"""The canonical candidate-surface producer and byte decoder (plan D7).

Shared single implementation: the public scanner and the maintainer-private
extraction pipeline both import this module (the private side imports it
from the repository), so extractor and scanner construct identical text
surfaces by construction. Digest bound in the signed attestation.

Decoder (ratified C3 pipeline): text byte-order marks longest-first
(UTF-32 BE/LE, UTF-8, UTF-16 BE/LE; strict; malformed input fails closed;
decoded forbidden controls fail closed); otherwise the frozen magic
signature table; otherwise strict UTF-8 with the decoded-control check;
otherwise raw C0/DEL/C1 rejection, then Latin-1.

Surface kinds:
  P  every path component relative to the scan/extraction root
  L  every decoded line
  C  every cell of a .csv file
  A  every string constant of a .py file's syntax tree
  R  printable-ASCII runs of a binary file -- extraction side only; on the
     scan side a binary file is a fail-closed VIOLATION instead.
"""

import ast
import csv
import io
import re
from collections.abc import Iterator
from pathlib import Path

_FORBIDDEN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
_PRINTABLE_RUN = re.compile(rb"[\x20-\x7e]{4,}")

_BOMS = [
    (b"\x00\x00\xfe\xff", "utf-32-be"),
    (b"\xff\xfe\x00\x00", "utf-32-le"),
    (b"\xef\xbb\xbf", "utf-8"),
    (b"\xfe\xff", "utf-16-be"),
    (b"\xff\xfe", "utf-16-le"),
]


def load_magic(path: Path) -> list[tuple[int, bytes]]:
    table = []
    for line in path.read_text().splitlines():
        if line and not line.startswith("#"):
            off, sig, _label = line.split(" ", 2)
            table.append((int(off), bytes.fromhex(sig)))
    return table


def decode_bytes(raw: bytes, magic_table) -> tuple[str, "str | None"]:
    """Return (kind, text); text only for kind == 'text'."""
    for bom, codec in _BOMS:
        if raw.startswith(bom):
            try:
                text = raw[len(bom):].decode(codec)
            except UnicodeDecodeError:
                return "malformed", None
            if _FORBIDDEN.search(text):
                return "binary-control", None
            return "text", text
    for off, sig in magic_table:
        if raw[off : off + len(sig)] == sig:
            return "binary-magic", None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        if _FORBIDDEN.search(raw.decode("latin-1")):
            return "binary-control", None
        return "text", raw.decode("latin-1")
    if _FORBIDDEN.search(text):
        return "binary-control", None
    return "text", text


def file_surfaces(
    path: Path, root: Path, magic_table, *, binary_as_runs: bool = False
) -> Iterator[tuple[str, str, str]]:
    """Yield (kind, locator, surface_text) for ``path``.

    With ``binary_as_runs`` (extraction side) a binary file contributes
    printable-run R surfaces; otherwise (scan side) it yields a single
    fail-closed ('VIOLATION', kind, '') marker.
    """
    rel = path.relative_to(root)
    for i, part in enumerate(rel.parts):
        yield "P", f"component:{i}", part

    raw = path.read_bytes()
    kind, text = decode_bytes(raw, magic_table)
    if kind != "text":
        if binary_as_runs:
            for j, run in enumerate(_PRINTABLE_RUN.findall(raw)):
                yield "R", f"run:{j}", run.decode("ascii")
        else:
            yield "VIOLATION", kind, ""
        return

    for lineno, line in enumerate(text.splitlines(), 1):
        if line.strip():
            yield "L", f"line:{lineno}", line

    if path.suffix.lower() == ".csv":
        for rowno, row in enumerate(csv.reader(io.StringIO(text)), 1):
            for colno, cell in enumerate(row, 1):
                if cell.strip():
                    yield "C", f"cell:{rowno}:{colno}", cell

    if path.suffix.lower() == ".py":
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and node.value.strip()
            ):
                yield "A", f"ast:{getattr(node, 'lineno', 0)}", node.value

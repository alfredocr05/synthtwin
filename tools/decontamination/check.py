#!/usr/bin/env python3
"""synthtwin decontamination scanner.

Verifies that no tracked file contains content matching the hashed
decontamination manifest (`manifest.txt`). The manifest holds only SHA-256
digests of normalized denied entries; the vocabulary itself never appears
in this repository. The plaintext inventory is maintainer-private and
reviewer-audited; the signed attestation (`attestation.json` + `.sig`)
binds this scanner, the manifest, and every private input together.

Matching contract (Phase 0 plan, D7, as ratified):
  tokenization -- NFKC-normalize the whole string; chunk on maximal
  Unicode alphanumerics (underscore excluded); split chunks at case
  transitions and letter/digit boundaries; casefold each subtoken.
  Candidates are all token n-grams up to the n_max recorded in the
  manifest header, over these surfaces: every path component, every
  decoded line, every cell of a .csv file, every string constant of a
  .py file's syntax tree.

  decoding -- text byte-order marks longest-first (UTF-32 BE/LE, UTF-8,
  UTF-16 BE/LE; strict, malformed input fails closed, decoded forbidden
  controls fail closed); otherwise the `magic.txt` signature table;
  otherwise strict UTF-8 (decoded forbidden controls fail closed);
  otherwise raw C0/DEL/C1 rejection, then Latin-1. A binary or malformed
  file is a fail-closed violation here -- data files are governed by the
  provenance guard, not exempted.

Output is value-silent: locations and digest prefixes only, never matched
text. Exit codes: 0 clean, 1 matches, 2 violations, 3 both.

Usage: python tools/decontamination/check.py [ROOT]   (default: repo root)
"""

import argparse
import ast
import csv
import hashlib
import io
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent

_CHUNK = re.compile(r"[^\W_]+", re.UNICODE)
_FORBIDDEN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
_BOMS = [
    (b"\x00\x00\xfe\xff", "utf-32-be"),
    (b"\xff\xfe\x00\x00", "utf-32-le"),
    (b"\xef\xbb\xbf", "utf-8"),
    (b"\xfe\xff", "utf-16-be"),
    (b"\xff\xfe", "utf-16-le"),
]


def _split_chunk(chunk):
    start = 0
    n = len(chunk)
    for i in range(1, n):
        p, c = chunk[i - 1], chunk[i]
        nxt = chunk[i + 1] if i + 1 < n else ""
        if (
            p.isdigit() != c.isdigit()
            or (p.islower() and c.isupper())
            or (p.isupper() and c.isupper() and nxt.islower())
        ):
            yield chunk[start:i]
            start = i
    yield chunk[start:]


def tokenize(text):
    normalized = unicodedata.normalize("NFKC", text)
    for chunk in _CHUNK.findall(normalized):
        for sub in _split_chunk(chunk):
            tok = sub.casefold()
            if tok:
                yield tok


def load_magic(path):
    table = []
    for line in path.read_text().splitlines():
        if line and not line.startswith("#"):
            off, sig, _label = line.split(" ", 2)
            table.append((int(off), bytes.fromhex(sig)))
    return table


def decode_bytes(raw, magic_table):
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


def file_surfaces(path, root, magic_table):
    rel = path.relative_to(root)
    for i, part in enumerate(rel.parts):
        yield "P", f"component:{i}", part
    raw = path.read_bytes()
    kind, text = decode_bytes(raw, magic_table)
    if kind != "text":
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


def load_manifest(path):
    hashes = set()
    n_max = 1
    for line in path.read_text().splitlines():
        if line.startswith("# n_max:"):
            n_max = int(line.split(":")[1])
        elif line and not line.startswith("#"):
            hashes.add(line)
    return hashes, n_max


def tracked_files(root):
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z"], cwd=root, capture_output=True, check=True
        ).stdout
        names = [n for n in out.decode().split("\0") if n]
        if names:
            return [root / n for n in names]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    skip = {".git", "__pycache__", ".venv", "venv", ".pytest_cache",
            ".mypy_cache", ".ruff_cache", "dist", "build", "wheelhouse"}
    return [
        p for p in sorted(root.rglob("*"))
        if p.is_file()
        and not (skip & set(p.parts))
        and not any(part.endswith(".egg-info") for part in p.parts)
    ]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("root", nargs="?", default=str(HERE.parent.parent))
    parser.add_argument(
        "--manifest", default=str(HERE / "manifest.txt"),
        help="hashed manifest (default: the committed one)",
    )
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    hashes, n_max = load_manifest(Path(args.manifest))
    magic = load_magic(HERE / "magic.txt")

    matches = violations = 0
    for f in tracked_files(root):
        for kind, locator, surf in file_surfaces(f, root, magic):
            if kind == "VIOLATION":
                print(
                    f"VIOLATION {f.relative_to(root)}: {locator} — this file "
                    "is not scannable text; if it is a legitimate fixture it "
                    "must go through the provenance allowlist, otherwise "
                    "remove it."
                )
                violations += 1
                continue
            toks = list(tokenize(surf))
            L = len(toks)
            for n in range(1, min(L, n_max) + 1):
                for i in range(L - n + 1):
                    h = hashlib.sha256(" ".join(toks[i : i + n]).encode()).hexdigest()
                    if h in hashes:
                        print(
                            f"MATCH {f.relative_to(root)} {kind} {locator} "
                            f"n={n} {h[:12]} — this content matches the "
                            "denied-vocabulary manifest; rewrite the text "
                            "(never edit the manifest)."
                        )
                        matches += 1

    if matches == 0 and violations == 0:
        print("decontamination: clean")
    code = (1 if matches else 0) | (2 if violations else 0)
    return code


if __name__ == "__main__":
    sys.exit(main())

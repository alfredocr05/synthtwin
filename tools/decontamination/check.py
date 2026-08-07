#!/usr/bin/env python3
"""synthtwin decontamination scanner.

Verifies that no tracked file contains content matching the hashed
decontamination manifest (`manifest.txt`). The manifest holds only SHA-256
digests of normalized denied entries; the vocabulary itself never appears
in this repository. The plaintext inventory is maintainer-private and
reviewer-audited; the signed attestation (`attestation.json` + `.sig`)
binds this scanner, the shared tokenizer/surface modules, the manifest,
and every private input together.

The tokenizer and surface/decoder implementations live in the sibling
modules `tokenizer.py` and `surfaces.py`, which are the SINGLE shared
implementation used by both this scanner and the maintainer-private
extraction pipeline (plan D7 Amendment A1: identical text-surface
candidate sets by construction).

Output is value-silent: locations and digest prefixes only, never matched
text. When a match occurs in a path component, the component itself is
redacted from the printed location. Exit codes: 0 clean, 1 matches,
2 violations, 3 both. A malformed manifest is itself reported as a
violation (exit 2) by the strict shared parser below.

Usage: python tools/decontamination/check.py [ROOT]   (default: repo root)
"""

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from surfaces import file_surfaces, load_magic
from tokenizer import tokenize

MANDATORY_HEADERS = (
    "entry_count",
    "n_max",
    "snapshot_tree_sha256",
    "wordlist_sha256",
    "seed_sha256",
    "grammar_sha256",
    "magic_sha256",
    "tokenizer_sha256",
)
_COUNT_HEADERS = ("entry_count", "n_max")
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_DECIMAL = re.compile(r"[0-9]+\Z")


class ManifestFormatError(ValueError):
    """The manifest file itself is malformed (never a content match)."""


def load_manifest(path):
    """Strict shared manifest parser (code-review round-2 item R2-B4).

    This is the SINGLE manifest parser: this scanner and
    verify_attestation.py both call it, so the two tools can never read
    different values from the same file. Returns ``(headers, body_lines)``
    where ``headers`` maps every mandatory header name to its string
    value and ``body_lines`` preserves the manifest's digest lines in
    order. Raises ManifestFormatError when a mandatory header is absent
    or appears more than once, when a count header is not a plain
    decimal number, when a digest header is not 64 lowercase hex
    characters, or when a body line is not exactly 64 lowercase hex
    characters.
    """
    headers = {}
    body = []
    for lineno, line in enumerate(path.read_text().splitlines(), 1):
        if line.startswith("#"):
            name, sep, value = line[1:].strip().partition(":")
            name = name.strip()
            if sep and name in MANDATORY_HEADERS:
                if name in headers:
                    raise ManifestFormatError(
                        f"line {lineno}: header '{name}' appears more than "
                        "once; each control header must appear exactly once. "
                        "Restore the manifest from version control."
                    )
                headers[name] = value.strip()
        elif line:
            if not _HEX64.fullmatch(line):
                raise ManifestFormatError(
                    f"line {lineno}: every body line must be exactly 64 "
                    "lowercase hex characters. Restore the manifest from "
                    "version control."
                )
            body.append(line)
    missing = [name for name in MANDATORY_HEADERS if name not in headers]
    if missing:
        raise ManifestFormatError(
            "missing mandatory header(s): " + ", ".join(missing)
            + ". Restore the manifest from version control."
        )
    for name in _COUNT_HEADERS:
        if not _DECIMAL.fullmatch(headers[name]):
            raise ManifestFormatError(
                f"header '{name}' must be a plain decimal number. Restore "
                "the manifest from version control."
            )
    for name in MANDATORY_HEADERS:
        if name.endswith("_sha256") and not _HEX64.fullmatch(headers[name]):
            raise ManifestFormatError(
                f"header '{name}' must be exactly 64 lowercase hex "
                "characters. Restore the manifest from version control."
            )
    return headers, body


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


def _match_hash(toks, hashes, n_max):
    found = []
    length = len(toks)
    for n in range(1, min(length, n_max) + 1):
        for i in range(length - n + 1):
            h = hashlib.sha256(" ".join(toks[i : i + n]).encode()).hexdigest()
            if h in hashes:
                found.append((n, h))
    return found


def _redacted_display(rel, matched_components):
    """Path for output with any matched component replaced by a digest tag,
    so a protected filename never reaches logs (value-silent output)."""
    parts = []
    for i, part in enumerate(rel.parts):
        if i in matched_components:
            tag = hashlib.sha256(part.encode()).hexdigest()[:12]
            parts.append(f"<redacted:{tag}>")
        else:
            parts.append(part)
    return "/".join(parts)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("root", nargs="?", default=str(HERE.parent.parent))
    parser.add_argument(
        "--manifest", default=str(HERE / "manifest.txt"),
        help="hashed manifest (default: the committed one)",
    )
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        headers, body_lines = load_manifest(Path(args.manifest))
    except ManifestFormatError as err:
        print(f"manifest format error: {err}")
        return 2
    hashes = set(body_lines)
    n_max = int(headers["n_max"])
    magic = load_magic(HERE / "magic.txt")

    matches = violations = 0
    for f in tracked_files(root):
        rel = f.relative_to(root)
        # First pass: identify matched path components so every printed
        # location can be redacted (value-silent output, review item F20).
        collected = list(file_surfaces(f, root, magic, binary_as_runs=False))
        matched_components = set()
        for kind, locator, surf in collected:
            if kind == "P" and _match_hash(list(tokenize(surf)), hashes, n_max):
                matched_components.add(int(locator.split(":")[1]))
        display = _redacted_display(rel, matched_components)

        for kind, locator, surf in collected:
            if kind == "VIOLATION":
                print(
                    f"VIOLATION {display}: {locator} - this file is not "
                    "scannable text; if it is a legitimate fixture it must "
                    "go through the provenance allowlist, otherwise remove "
                    "it."
                )
                violations += 1
                continue
            loc = "component:<redacted>" if (
                kind == "P" and int(locator.split(":")[1]) in matched_components
            ) else locator
            for n, h in _match_hash(list(tokenize(surf)), hashes, n_max):
                print(
                    f"MATCH {display} {kind} {loc} n={n} {h[:12]} - this "
                    "content matches the denied-vocabulary manifest; rewrite "
                    "the text (never edit the manifest)."
                )
                matches += 1

    if matches == 0 and violations == 0:
        print("decontamination: clean")
    return (1 if matches else 0) | (2 if violations else 0)


if __name__ == "__main__":
    sys.exit(main())

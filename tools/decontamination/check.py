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
2 violations, 3 both.

Usage: python tools/decontamination/check.py [ROOT]   (default: repo root)
"""

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from surfaces import file_surfaces, load_magic
from tokenizer import tokenize


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
    hashes, n_max = load_manifest(Path(args.manifest))
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
                    f"VIOLATION {display}: {locator} — this file is not "
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
                    f"MATCH {display} {kind} {loc} n={n} {h[:12]} — this "
                    "content matches the denied-vocabulary manifest; rewrite "
                    "the text (never edit the manifest)."
                )
                matches += 1

    if matches == 0 and violations == 0:
        print("decontamination: clean")
    return (1 if matches else 0) | (2 if violations else 0)


if __name__ == "__main__":
    sys.exit(main())

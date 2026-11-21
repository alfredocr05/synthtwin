#!/usr/bin/env python3
"""Fail when a file of the repository starts with the inside record's protected marker (plan P4-D495, lane IN-0).

An inside record describes a real table and stays on the computer that
table is on (`synthtwin.inside`). CI's sensitive-paths job runs this on
every event, pushes included: it reads the first bytes of every file
under the folder it is given (the checkout; the `.git` folder skipped),
prints the PATH of each file that starts with the marker (a UTF-8
byte-order mark before it allowed) and never a byte of its content, and
exits 1 where it found one, 0 where it found none.

    python3 tools/hooks/check_inside_records.py [FOLDER]

Standard library only, and it imports nothing of the package: the job
runs it without installing anything. `MARKER` must equal
`synthtwin.inside.MARKER`; `tests/test_inside_export.py` holds the two
equal.
"""

from __future__ import annotations

import os
import sys

MARKER = (
    "SYNTHTWIN PROTECTED INSIDE RECORD 1 -- describes a real table; it stays on this computer, never shared, "
    "synced, printed or committed"
)
BOM = b"\xef\xbb\xbf"


def starts_with_marker(path: str) -> bool:
    """Whether the file at `path` starts with the marker; only its first bytes are read."""
    wanted = MARKER.encode("utf-8")
    try:
        with open(path, "rb") as handle:
            head = handle.read(len(wanted) + len(BOM))
    except OSError:
        return False
    if head.startswith(BOM):
        head = head[len(BOM):]
    return head[: len(wanted)] == wanted


def records_under(root: str) -> "list[str]":
    """Every file under `root` that starts with the marker, as a path relative to `root`, sorted."""
    found: "list[str]" = []
    for folder, subfolders, names in os.walk(root):
        subfolders[:] = sorted(name for name in subfolders if name != ".git")
        for name in sorted(names):
            path = os.path.join(folder, name)
            if os.path.islink(path) or not os.path.isfile(path):
                continue
            if starts_with_marker(path):
                found += [os.path.relpath(path, root)]
    return sorted(found)


def main(argv: "list[str] | None" = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    root = arguments[0] if arguments else "."
    found = records_under(root)
    if not found:
        print(f"No file under {root} starts with the inside record's protected marker.")
        return 0
    for path in found:
        print(f"::error title=Inside record in the repository::{path} starts with the inside record's protected "
              "marker. An inside record describes a real table and never leaves the computer it was made on: "
              "remove the file from the repository and from its history.")
    print(f"{len(found)} file(s) start with the inside record's protected marker; the job fails.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Structural validator for the dev/build requirement files (plan D5).

Reads requirements-dev.in and requirements-dev.lock as plain text and
accepts only the line shapes a frozen, wheel-only closure needs:

- comment lines and blank lines;
- exactly one "--only-binary :all:" directive per file;
- requirement lines naming a pinned index release: in the lock an exact
  "name==version" pin with one or more "--hash=sha256:..." options and
  an optional environment marker; in the .in file a name with an
  ordinary version range.

Every other line is refused while it is still text: direct file
references, source or wheel archive paths, version-control references,
editable installs, bare local paths, URLs, and unknown directives.

This validator never executes anything. It does not invoke pip, does
not import any package code, and never opens a path named inside the
files. CI runs it before every pip command that consumes the lock, so
a lock line that could make pip fetch or build arbitrary code is
refused before pip exists in the picture at all.

Usage:
  python tools/supply_chain/validate_lock.py
      Validate the repository's requirements-dev.in and
      requirements-dev.lock.
  python tools/supply_chain/validate_lock.py --lock PATH [--lock PATH]
  python tools/supply_chain/validate_lock.py --input PATH [--input PATH]
      Validate specific files under the lock rules or the .in rules.

Exit codes: 0 every checked file is acceptable; 1 at least one line
was refused; 2 a named file could not be read.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ONLY_BINARY_LINE = "--only-binary :all:"

_NAME = r"[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?"
_PIN_RE = re.compile(rf"^{_NAME}\s*==\s*[0-9][A-Za-z0-9.!+]*$")
_RANGE_OP = r"(?:===|==|!=|<=|>=|~=|<|>)"
_RANGE_VERSION = r"[0-9][A-Za-z0-9.!+*]*"
_RANGE_RE = re.compile(
    rf"^{_NAME}\s*{_RANGE_OP}\s*{_RANGE_VERSION}"
    rf"(?:\s*,\s*{_RANGE_OP}\s*{_RANGE_VERSION})*$"
)
_HASH_RE = re.compile(r"^--hash=sha256:[0-9a-f]{64}$")
# Environment markers are plain comparisons joined by and/or. The '*'
# belongs to the version-wildcard form a resolver emits when a release
# applies to exactly one interpreter series
# (python_full_version == '3.11.*'); it appears inside a quoted version
# literal and cannot name a file, a path, an archive, or a URL -- those
# shapes are refused by _screen before this pattern is ever applied.
_MARKER_RE = re.compile(r"^[A-Za-z0-9_.'\" ()=<>!,*-]+$")
_ARCHIVE_MARKS = (".tar.gz", ".tgz", ".tar.bz2", ".tar.xz", ".tar", ".zip", ".whl")
_VCS_MARKS = ("git+", "hg+", "svn+", "bzr+")


def _logical_lines(text):
    """Yield (first physical line number, joined line) pairs.

    A trailing backslash continues a line, exactly as pip reads the
    requirement files.
    """
    pending = ""
    pending_start = 1
    for number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if not pending:
            pending_start = number
        if stripped.endswith("\\"):
            pending += stripped[:-1].strip() + " "
            continue
        yield pending_start, (pending + stripped).strip()
        pending = ""
    if pending:
        yield pending_start, pending.strip()


def _screen(line):
    """Return the refusal reason for a forbidden reference, or None.

    Purely lexical: the line is inspected as text and nothing it names
    is resolved, opened, or fetched.
    """
    if not line.isascii():
        return (
            "contains non-ASCII characters; the requirement files stay "
            "plain ASCII so every line means exactly what it shows"
        )
    if line == "-e" or line.startswith("-e ") or "--editable" in line:
        return (
            "asks for an editable install; editable installs point at "
            "local source and execute its build code, so they are refused"
        )
    for mark in _VCS_MARKS:
        if mark in line:
            return (
                f"names a version-control source ('{mark}...'); checkouts "
                "build from source and are refused"
            )
    if "file:" in line:
        return (
            "contains a 'file:' reference; a direct file reference makes "
            "pip fetch and possibly build local code, so it is refused"
        )
    if "://" in line:
        return (
            "contains a URL; requirements may name only pinned index "
            "releases, never a download location"
        )
    if "/" in line or "\\" in line:
        return (
            "contains a path separator, so it points at a local file or "
            "directory; local paths are refused"
        )
    for mark in _ARCHIVE_MARKS:
        if mark in line:
            return (
                f"references an archive file ('{mark}'); archives are "
                "fetched and possibly built by pip, so they are refused"
            )
    if "@" in line:
        return (
            "uses an '@' direct reference; requirements may name only "
            "pinned index releases"
        )
    return None


def _check_requirement(line, mode, where):
    """Check one requirement line's structure. Returns problem strings."""
    problems = []
    head_tokens = []
    option_tokens = []
    for token in line.split():
        if token.startswith("--") or option_tokens:
            option_tokens.append(token)
        else:
            head_tokens.append(token)
    for token in option_tokens:
        if not _HASH_RE.fullmatch(token):
            problems.append(
                where + f"carries the option '{token}', but after the "
                "requirement only '--hash=sha256:' plus 64 hex characters "
                "is accepted"
            )
    if mode == "lock" and not option_tokens:
        problems.append(
            where + "has no '--hash=sha256:...' option; every lock entry "
            "must pin its exact file hashes"
        )

    head = " ".join(head_tokens)
    req_part, sep, marker = head.partition(";")
    req_part = req_part.strip()
    marker = marker.strip()
    if sep and (not marker or ";" in marker or not _MARKER_RE.fullmatch(marker)):
        problems.append(
            where + "has an environment marker with unexpected characters; "
            "only plain comparisons like \"sys_platform == 'linux'\" "
            "joined by 'and'/'or' are accepted"
        )

    if not req_part:
        problems.append(where + "has no requirement before its options")
    elif mode == "lock":
        if not _PIN_RE.fullmatch(req_part):
            problems.append(
                where + "is not an exact 'name==version' pin; the lock may "
                "hold only exactly pinned index releases"
            )
    elif not _RANGE_RE.fullmatch(req_part):
        problems.append(
            where + "is not a package name with a version range such as "
            "'name>=1.0'; bare names and every other form are refused"
        )
    return problems


def check_text(text, mode, label):
    """Validate one requirement file's text. Returns problem strings.

    mode is 'lock' (exact pins, hashes required) or 'input' (version
    ranges, the shape of requirements-dev.in). The check is lexical and
    structural only: nothing is executed, resolved, or opened.
    """
    if mode not in ("lock", "input"):
        raise ValueError(f"unknown mode: {mode!r} (use 'lock' or 'input')")
    problems = []
    directive_count = 0
    for lineno, line in _logical_lines(text):
        if not line or line.startswith("#"):
            continue
        if line == ONLY_BINARY_LINE:
            directive_count += 1
            continue
        where = f"{label}:{lineno}: the line "
        refusal = _screen(line)
        if refusal is not None:
            problems.append(where + refusal)
            continue
        if line.startswith("-"):
            problems.append(
                where + "uses a directive that is not on the accepted "
                f"list; only '{ONLY_BINARY_LINE}' may appear"
            )
            continue
        problems.extend(_check_requirement(line, mode, where))
    if directive_count != 1:
        problems.append(
            f"{label}: expected exactly one '{ONLY_BINARY_LINE}' line but "
            f"found {directive_count}; the wheel-only rule must live in "
            "the file itself"
        )
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Check the requirement files' structure as plain text, before "
            "pip runs. Without arguments, checks the repository's "
            "requirements-dev.in and requirements-dev.lock."
        )
    )
    parser.add_argument(
        "--lock",
        action="append",
        default=[],
        metavar="PATH",
        help="check PATH under the lock rules (exact pins with hashes)",
    )
    parser.add_argument(
        "--input",
        action="append",
        default=[],
        dest="inputs",
        metavar="PATH",
        help="check PATH under the requirements-dev.in rules (version ranges)",
    )
    args = parser.parse_args(argv)

    targets = [(Path(p), "lock") for p in args.lock]
    targets += [(Path(p), "input") for p in args.inputs]
    if not targets:
        root = Path(__file__).resolve().parents[2]
        targets = [
            (root / "requirements-dev.in", "input"),
            (root / "requirements-dev.lock", "lock"),
        ]

    problems = []
    for path, mode in targets:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            print(f"Cannot read {path}.")
            print("This structural check needs the requirement file to exist.")
            print("Restore it from version control, or fix the path given on")
            print("the command line, then run this check again.")
            return 2
        except UnicodeDecodeError:
            problems.append(
                f"{path.name}: the file is not plain UTF-8 text; a binary "
                "file cannot be a requirement input"
            )
            continue
        problems.extend(check_text(text, mode, path.name))

    if problems:
        print("The requirement files failed the structural check:")
        for entry in problems:
            print(" -", entry)
        print("These files may hold only comments, blank lines, one")
        print(f"'{ONLY_BINARY_LINE}' line, and pinned index releases (in the")
        print("lock: exact 'name==version' pins with sha256 hashes and")
        print("optional environment markers). Rewrite or remove the refused")
        print("lines, rebuild the lock from requirements-dev.in with a")
        print("maintainer, and run this check again. Nothing was executed")
        print("or fetched: this check reads the files as text only.")
        return 1
    checked = ", ".join(f"{path.name} ({mode} rules)" for path, mode in targets)
    print(f"structural check passed: {checked}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

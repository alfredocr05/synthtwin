"""K-P0-05: the decontamination scan over the whole repository, with its non-vacuity floor.

`tests/test_decontamination.py` asserts only that the scan exits 0, and
a scan that walked no file exits 0 too: on a copy of this repository
under a folder named `build`, the scanner's non-git fallback skipped
every file and printed `clean`. So this counts the files the scan
reads, the text surfaces it reads in them and the matches it finds,
and the ledger holds all three: at least 400 files, at least 100,000
surfaces, and none matching. About four minutes.

COUNTED FROM THE READS THE SCAN COMPLETES, NOT FROM THE PATHS IT LISTS
(round-2 ledger item 4). `files_scanned` was `len(check.tracked_files(ROOT))`
-- the LISTING, taken before `check.main` ran and never compared with
what it read. Measured: with `check.file_surfaces` replaced by an empty
iterator, this driver reported "447 files scanned, 0 matches, exit 0"
over a run that opened no file at all, and K-P0-05 read PASS. Its
"lists and reads >= 400" rule was therefore measuring the listing
twice.

The scanner itself is not touched to fix this: `check.py` is inside the
digest the signed attestation binds (`verify_attestation.py`), so an
edit there would break a gate nobody here can re-sign. The count is
taken by INSTRUMENTING the surface reader the scan pulls its text
through -- one wrapper around `check.file_surfaces`, counting each file
whose surfaces the scan actually consumed and how many it consumed --
which is the same reads, counted where they happen. A run that raises
is not a measurement either: `counted_scan` catches nothing, so a scan
that dies comes out of this module before any KPI line is printed and
the driver exits non-zero, which the runner fails the entry for.

THE FILE COUNT ALONE IS NOT ENOUGH (the round-2 ledger repair pass,
finding 1). A reader that yields ONE trivial surface per file reports
447 files read and passes a floor of 400 while reading 1/1230 of the
text: measured on this tree, the honest scan reads 549,744 surfaces
against that attack's 447. So the surfaces are counted and bounded
too, at 100,000 -- an order of magnitude under the honest number and
two orders over the attack.

    .venv/bin/python tools/measurements/kpi_decontamination.py --kpi
"""

import contextlib
import importlib.util
import io
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402


def load_scanner(root):
    """The decontamination scanner, loaded as a module of its own."""
    sys.path.insert(0, str(root / "tools" / "decontamination"))
    spec = importlib.util.spec_from_file_location(
        "kpi_check", root / "tools" / "decontamination" / "check.py"
    )
    check = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(check)
    return check


def counted_scan(check, root, manifest=None):
    """Run the scan over ``root``, counting the reads it COMPLETES.

    Returns files_listed (what the scanner's own walk offers),
    files_scanned (files whose text surfaces the scan actually pulled),
    surfaces_scanned (how many surfaces it pulled), matches and exit.
    `files_scanned` is 0 on a scan that reads nothing, whatever the
    listing says and whatever the scan exits with, and
    `surfaces_scanned` is what separates a scan that read the tree from
    one that opened every file and read a token out of each.

    A SCAN THAT RAISES IS NOT A MEASUREMENT AND IS NOT REPORTED AS ONE.
    Nothing is caught here: the exception leaves this function -- the
    `finally` only puts the real reader back -- so no partial count is
    ever returned and the driver dies before it can print a KPI line.
    (The round-2 ledger repair pass, finding 5: a `completed` flag stood
    here that no path could set to False, guarding a branch of main()
    that could not run.)
    """
    reading = check.file_surfaces
    counted = {"files": 0, "surfaces": 0}

    def through(*arguments, **named):
        pulled = 0
        for surface in reading(*arguments, **named):
            pulled = pulled + 1
            counted["surfaces"] = counted["surfaces"] + 1
            yield surface
        if pulled:
            counted["files"] = counted["files"] + 1

    listed = check.tracked_files(root)
    argv = [str(root)] + ([] if manifest is None else ["--manifest", str(manifest)])
    printed = io.StringIO()
    check.file_surfaces = through
    try:
        with contextlib.redirect_stdout(printed), contextlib.redirect_stderr(printed):
            code = check.main(argv)
    finally:
        check.file_surfaces = reading
    lines = printed.getvalue().splitlines()
    matches = sum(1 for line in lines if line.startswith("MATCH"))
    violations = sum(1 for line in lines if line.startswith("VIOLATION"))
    return {
        "files_listed": len(listed),
        "files_scanned": counted["files"],
        "surfaces_scanned": counted["surfaces"],
        "matches": matches + violations,
        "exit": code,
    }


def main():
    kpi_rules.guard_this_tree()
    check = load_scanner(ROOT)
    found = counted_scan(check, ROOT)
    print(
        f"files listed {found['files_listed']}, files read {found['files_scanned']}, "
        f"surfaces read {found['surfaces_scanned']}, matches {found['matches']}, "
        f"exit {found['exit']}"
    )
    kpi_rules.emit(
        "K-P0-05",
        {
            "files_listed": found["files_listed"],
            "files_scanned": found["files_scanned"],
            "surfaces_scanned": found["surfaces_scanned"],
            "matches": found["matches"],
            "exit": found["exit"],
        },
    )


if __name__ == "__main__":
    main()

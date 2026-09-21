"""K-P0-10: what the suite itself costs -- its wall clock and its collected count.

WHY THE SUITE'S OWN COST IS A KPI. Every stage from here is gated by
CI, and CI is the whole suite on eleven matrix cells plus the floors
job. Measured on the reference machine in one process, the suite was
7,087 collected cases in 54 min 42 s of almost entirely serial CPU, and
a two-core runner paid an hour and a half to three hours for that on
every cell; the floors cell twice came near three hours. Nothing in the
repository measured it, so it had grown to that quietly, one landing at
a time. This is the number that stops it growing quietly again.

THE TWO HALVES, AND WHY BOTH. Seconds alone can always be bought by
running fewer tests, which is the one thing a speed landing must not be
able to do, so the count is measured in the same breath and the ledger
holds it at AT LEAST what it is: a suite that got faster by losing
cases fails here. Seconds are a MACHINE-decided number
(`kpi_rules.MACHINE_KINDS`) and are judged only on the quiet reference
machine; the collected count is the machine's business nowhere and is
judged everywhere.

WHAT IT MEASURES, AND WHAT IT DOES NOT. One `python -m pytest -q` from
the repository root, end to end, timed by the wall clock, in the
ordinary single process the ledger's other seconds were taken in -- not
sharded, not parallel. The CI split this landing added divides that
same work across jobs; it does not change this number, and that is why
this number is the honest one to hold: a later stage cannot make the
suite three hours again and hide it behind more runners.

    .venv/bin/python tools/measurements/kpi_suite_time.py --kpi

It takes as long as the suite does. There is no shortcut that is still
the measurement.
"""

import os
import pathlib
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

# The last line of `pytest -q` in both its shapes: a run that passed and
# a run that did not. The count is what this reads; the verdict is the
# exit code.
_TAIL = re.compile(r"(\d+) (?:passed|failed|error)")
_COLLECTED = re.compile(r"(\d+) tests? collected")


def _environment(root):
    """The environment the timed run gets: this tree's `src` on the path.

    THE MEASUREMENT MUST BE OF THIS TREE. A bare `pytest` subprocess
    imports synthtwin from whatever the interpreter already resolves --
    which, with an editable install in the virtual environment, is
    another checkout entirely. `kpi_rules.guard_this_tree` holds the
    driver itself to this tree; this holds the suite it starts to the
    same one.
    """
    environment = dict(os.environ)
    ahead = str(root / "src")
    carried = environment["PYTHONPATH"] if "PYTHONPATH" in environment else ""
    environment["PYTHONPATH"] = f"{ahead}{os.pathsep}{carried}" if carried else ahead
    return environment


def collected(root=ROOT):
    """How many cases pytest collects, from its own collector."""
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider"],
        cwd=root,
        capture_output=True,
        text=True,
        env=_environment(root),
    )
    found = _COLLECTED.findall(done.stdout)
    if not found or done.returncode != 0:
        raise SystemExit(
            "pytest could not collect the suite, so there is nothing to measure:\n"
            + done.stdout[-2000:]
            + done.stderr[-2000:]
        )
    return int(found[len(found) - 1])


def timed_run(root=ROOT):
    """The whole suite, once, timed. Returns seconds, cases reported, exit."""
    started = time.perf_counter()
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
        cwd=root,
        capture_output=True,
        text=True,
        env=_environment(root),
    )
    seconds = time.perf_counter() - started
    reported = 0
    for number in _TAIL.findall(done.stdout):
        reported = reported + int(number)
    return seconds, reported, done.returncode, done.stdout


def main():
    kpi_rules.guard_this_tree()
    found = collected()
    seconds, reported, code, output = timed_run()
    tail = output.strip().splitlines()
    print(tail[len(tail) - 1] if tail else "(pytest printed nothing)")
    print(
        f"collected {found} cases, ran in {seconds:.1f} s "
        f"({seconds / 60:.1f} min), exit {code}"
    )
    kpi_rules.emit(
        "K-P0-10",
        {
            "collected": found,
            "suite_seconds": round(seconds, 1),
            "cases_reported": reported,
            "exit": code,
        },
    )


if __name__ == "__main__":
    main()

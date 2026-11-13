"""K-P0-10 and K-P0-11: the suite's cost in five shards, read from a finished run of them (plan P4-D461).

TWO SUITE KPIS, ONE READING. K-P0-10 holds the suite's collected count
and, by its dated amendment of 2026-11-06 (LANE SPD2 RULINGS 2 (2)), the
five shards' summed seconds and the heaviest shard's seconds: the
one-process seconds it was written with, which `kpi_suite_time.py`
measured, are dropped, since the suite runs as `tools/ci/shards.py`'s
five shards, one process each and the five at once (CI's
`SHARD_COUNT`), and one process of today's suite would run for hours.
What every lane, integrator and CI cell waits on is the heaviest of the
five shards, and K-P0-11 holds it, registered at lane SPD2's rebase from
batch 4p's merged suite. With `--kpi` this script prints both lines: K-P0-10's
collected count (the manifest's cases) with the summed and heaviest
seconds, and K-P0-11's heaviest and summed seconds with the files and
cases run.

WHAT IT READS. One finished run of the five shards, each shard's files
from `tools/ci/shards.py --of 5 --shard N` run by one pytest process: the
folder holds `shard-N.files` (the shard's file list), `shard-N.log`
(pytest's output, whose last line is its summary) and `shard-N.exit`; and
THE COLLECTION MANIFEST of the measured revision (`--collected`):
`pytest --collect-only -q`'s output over the same tree, whose node ids say
which test files the revision collects and how many cases each holds.

WHAT IT REFUSES -- exit 1, no KPI line -- every way a folder fails to be
one finished run of the whole suite (Codex's review of lane SPD2, items 2
and 3):

- not EXACTLY the five shards: a shard's files, log or exit missing, or a
  file of any other shard beside them (`shard-6.log`);
- not an exact PARTITION of the manifest: an empty file list, a file in
  two shards, a collected file in no shard, or a shard file the manifest
  does not collect;
- not a finished EXECUTION: a log whose last line is no pytest summary of
  cases run with their seconds (a collection's `3220 tests collected in
  0.10s` is none, and neither is `no tests ran`); a summary naming a
  failed, erroring or deselected case, whatever the exit file says; an
  exit other than 0; or cases run that do not reconcile with the manifest
  (passed, skipped, xfailed and xpassed together must equal the cases the
  manifest collects in the shard's files).

It reports the heaviest shard's seconds, the five summed, each shard's,
and the files and cases run. Seconds are a MACHINE-decided number
(`kpi_rules.MACHINE_KINDS`): recorded everywhere, judged only on the quiet
reference machine.

    .venv/bin/python tools/measurements/kpi_suite_shards.py --kpi --suite <folder of a finished run> --collected <its revision's collect-only output>

Without `--suite` and `--collected` it measures nothing and exits 2: the
run it reads takes an hour or more and is made by the suite runner, never
by this script.
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

SHARDS = 5
# Every file the suite runner leaves for a shard: shard-N.files, shard-N.log and shard-N.exit.
_SHARD_FILE = re.compile(r"^shard-([0-9]+)\.")
# pytest's last line of a run, with or without its rule of '=' signs:
# "1 failed, 2510 passed, 2 xfailed, 4 warnings in 5956.20s (1:39:16)".
_SUMMARY = re.compile(r"^=*\s*(?P<counts>.+?) in (?P<seconds>[0-9]+(?:\.[0-9]+)?)s\b")
_COUNT = re.compile(r"^(?P<count>[0-9]+) (?P<outcome>[a-z]+)$")
_COLLECTED = re.compile(r"^([0-9]+) tests? collected\b")
# Cases that ran to an outcome the suite accepts; outcomes that say a case failed or did not run;
# and what is only noted beside them.
_RAN = ("passed", "skipped", "xfailed", "xpassed")
_REFUSED = ("failed", "error", "errors", "deselected", "rerun")
_NOTED = ("warning", "warnings")


def read_manifest(path: pathlib.Path) -> "tuple[dict[str, int], list[str]]":
    """The cases each collected test file holds, from `pytest --collect-only -q`'s output, and why it is no manifest."""
    if not path.is_file():
        return {}, [f"the collection manifest {path} does not exist"]
    counts: "dict[str, int]" = {}
    stated = -1
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if "::" in line:
            name = line.split("::", 1)[0]
            counts[name] = counts.get(name, 0) + 1
            continue
        found = _COLLECTED.match(line)
        if found:
            stated = int(found.group(1))
    if not counts:
        return counts, [f"the collection manifest {path} names no collected case"]
    if stated >= 0 and stated != sum(counts.values()):
        return counts, [f"the collection manifest says {stated} collected and names {sum(counts.values())}"]
    return counts, []


def _summary(line: str) -> "tuple[dict[str, int], float] | None":
    """pytest's summary of cases run, read: each outcome's count and the seconds; None where the line is none."""
    found = _SUMMARY.match(line.strip())
    if found is None:
        return None
    outcomes: "dict[str, int]" = {}
    for part in found.group("counts").split(", "):
        counted = _COUNT.match(part.strip())
        if counted is None or counted.group("outcome") not in _RAN + _REFUSED + _NOTED:
            return None
        outcomes[counted.group("outcome")] = int(counted.group("count"))
    if not any(outcome in outcomes for outcome in _RAN + _REFUSED):
        return None
    return outcomes, float(found.group("seconds"))


def read_run(folder: pathlib.Path, collected: "dict[str, int]") -> "tuple[dict[str, object], list[str]]":
    """The run's measures and every way it fails to be one finished run of the whole manifest in five shards, named."""
    problems: "list[str]" = []
    if not folder.is_dir():
        return {}, [f"{folder} is no folder of a run"]
    for entry in sorted(folder.iterdir()):
        found = _SHARD_FILE.match(entry.name)
        if found and not 1 <= int(found.group(1)) <= SHARDS:
            problems += [f"{entry.name} is no file of shards 1 to {SHARDS}"]
    seconds: "list[float]" = []
    seen: "dict[str, int]" = {}
    cases = 0
    for shard in range(1, SHARDS + 1):
        files = folder / f"shard-{shard}.files"
        log = folder / f"shard-{shard}.log"
        exit_file = folder / f"shard-{shard}.exit"
        if not (files.is_file() and log.is_file() and exit_file.is_file()):
            problems += [f"shard {shard}: its files, log or exit is missing"]
            continue
        names = files.read_text(encoding="utf-8").split()
        if not names:
            problems += [f"shard {shard}: its file list is empty"]
        expected = 0
        for name in names:
            if name in seen:
                problems += [f"{name} is in shard {seen[name]} and in shard {shard}"]
                continue
            seen[name] = shard
            if name not in collected:
                problems += [f"{name} (shard {shard}) is no file the manifest collects"]
            expected += collected.get(name, 0)
        code = exit_file.read_text(encoding="utf-8").strip()
        if code != "0":
            problems += [f"shard {shard} exited {code}"]
        lines = [line for line in log.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]
        read = _summary(lines[len(lines) - 1]) if lines else None
        if read is None:
            problems += [f"shard {shard}: its log ends without pytest's summary of the cases it ran and their seconds"]
            continue
        outcomes, spent = read
        for outcome in _REFUSED:
            if outcomes.get(outcome):
                problems += [f"shard {shard}: its summary says {outcomes[outcome]} {outcome}"]
        ran = sum(outcomes.get(outcome, 0) for outcome in _RAN)
        if ran != expected:
            problems += [f"shard {shard} ran {ran} cases where the manifest collects {expected} in its files"]
        cases += ran
        seconds += [spent]
    for name in sorted(collected):
        if name not in seen:
            problems += [f"{name} is collected and in no shard"]
    measures: "dict[str, object]" = {}
    if len(seconds) == SHARDS:
        measures = {
            "heaviest_shard_seconds": round(max(seconds), 2),
            "summed_shard_seconds": round(sum(seconds), 2),
            "test_files": len(seen),
            "cases": cases,
        }
        measures["detail"] = ", ".join(f"{one:.2f}" for one in seconds)
    return measures, problems


def main(arguments: "list[str]") -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--kpi", action="store_true", help="print the KPI line")
    parser.add_argument("--suite", help="the folder of one finished run of the five shards")
    parser.add_argument("--collected", help="pytest --collect-only -q's output over the measured revision")
    chosen = parser.parse_args(arguments)
    if not chosen.suite or not chosen.collected:
        print("K-P0-11 reads one finished run of the five shards and its revision's collection: name the run's "
              "folder with --suite and the collect-only output with --collected. Nothing was measured.")
        return 2
    collected, problems = read_manifest(pathlib.Path(chosen.collected))
    measures: "dict[str, object]" = {}
    if collected:
        measures, more = read_run(pathlib.Path(chosen.suite), collected)
        problems += more
    for problem in problems:
        print(f"refused: {problem}")
    if problems or not measures:
        return 1
    shards = measures.pop("detail")
    head = pathlib.Path(chosen.suite) / "head.txt"
    revision = head.read_text(encoding="utf-8").strip()[:12] if head.is_file() else "unnamed"
    detail = (f"heaviest of {SHARDS} shards {measures['heaviest_shard_seconds']} s, "
              f"{measures['summed_shard_seconds']} s summed over {measures['test_files']} test files and "
              f"{measures['cases']} cases (each shard, in order: {shards} s; revision {revision})")
    print(detail)
    if chosen.kpi:
        kpi_rules.emit("K-P0-10", {"collected": sum(collected.values()),
                                   "summed_shard_seconds": measures["summed_shard_seconds"],
                                   "heaviest_shard_seconds": measures["heaviest_shard_seconds"]}, detail)
        kpi_rules.emit("K-P0-11", measures, detail)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""K-RU-01, the headline: analysis code runs unchanged on the twin and reaches the real table's conclusions.

Runs the reliability battery (`tests/reliability_battery.py`): the seven
invented tables of `tests/reliability_tables.py` and its null table, each described and
twinned by the commands a person types (profile, the truthful answers,
generate), and every analysis file of `tests/reliability_scripts/` run on
the real table, its eight halves, the twin, a fresh sample and the
shuffled table, then judged by the battery's pass rule. Every table is
drawn from its seed at run time; nothing is committed.

* ``--kpi`` -- the 20,000-row tier: table seeds 1 to 3, twin seeds 0 to 2.
  Prints one KPI line for K-RU-01, every key suffixed `_20k`.
* ``--quick`` -- the same at one table seed and one twin seed: a first
  look, never a stamp.
* ``--night`` -- the 200,000-row tier: one table seed, twin seeds 0 and 1,
  each table in a child process of its own (``--one``), keys `_200k`
  (lane RU-b's tier; it waits while a whole suite runs, as the analyst
  battery's night does, through ``SYNTHTWIN_PAUSE_WHILE``).
* ``--one TABLE --seed S`` -- one table at one seed in this process, its
  run written as JSON to ``--json`` (what each night child runs).

F0, the zoo's analyst scripts over its kinds of export, is K-HZ-01's own
measurement and is read from that entry's stamp (its commit named in the
value) unless ``--zoo`` is given, which runs the zoo's 20,000-row leg here
(about four hours on the reference machine).

``--report PATH`` writes every table run, every script's verdict on every
side with the clause it failed, and the reasons counted script by script,
as JSON for the lane's report; where ``--report`` is not given and the
environment names a file in ``SYNTHTWIN_RELIABILITY_REPORT`` (a run that
`kpi_run.py --slow` starts, which passes no option of its own), the
report is written there. ``--out`` names the work folder (default: a
temporary one, removed after); each version of a table is deleted as soon
as its scripts have read it. Every run at 20,000 rows or more goes through
the machine's memory guard.

    .venv/bin/python tools/measurements/kpi_reliability_battery.py --kpi
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402
import reliability_battery as B  # noqa: E402
import reliability_tables as T  # noqa: E402

# THE GUARD, AMONG THE MODULE'S OWN STATEMENTS (LANE CHON RULINGS 7 (1)(c); batch 4u's checks): every run of the
# shipped `profile` this driver or a night's child makes, through `reliability_battery` or any module, has a data
# folder of the run's own and the floor off, and the code measured is this tree's.
kpi_rules.guard_this_tree()

THIS = pathlib.Path(__file__).resolve()


def busy() -> "list[str]":
    """The paths named in SYNTHTWIN_PAUSE_WHILE that exist as a file or a folder with anything in it."""
    held = []
    for name in os.environ.get("SYNTHTWIN_PAUSE_WHILE", "").split(os.pathsep):
        path = pathlib.Path(name) if name else None
        if path is not None and (path.is_file() or (path.is_dir() and any(path.iterdir()))):
            held += [name]
    return held


def f0_value(zoo: bool) -> "dict[str, object]":
    """F0: K-HZ-01's stamped value, or (``zoo``) the zoo's 20,000-row leg run here."""
    if not zoo:
        return B.f0_from_ledger(kpi_rules.load_ledger())
    import health_zoo

    with tempfile.TemporaryDirectory(prefix="synthtwin-reliability-zoo-") as folder:
        results = health_zoo.run_zoo(pathlib.Path(folder), health_zoo.KPI_ROWS)
    measured = health_zoo.zoo_measures(results)
    kinds = measured["kinds"]
    passing = sum(1 for verdict in kinds.values() if verdict["passed"])
    return {"F0_twin": round(passing / max(1, len(kinds)), 4), "F0_kinds": len(kinds), "F0_from": "the zoo run here"}


def report(runs: "list[B.TableRun]", value: "dict[str, object]", path: pathlib.Path, seconds: float) -> None:
    """Every verdict of the run, for the lane's report: per script, side and seed, with the clause failed."""
    verdicts = []
    for run in runs:
        for s in B.score(run):
            verdicts += [{
                "script": s.stem, "table": s.table, "family": s.family, "relation": s.relation, "seed": s.seed,
                "twin_seed": s.twin, "real_ok": s.real_ok, "real_error": s.real_error,
                "sides": {kind: {"runs": j.runs, "passed": j.passed, "why": j.why, "supported": j.supported,
                                 "same": j.same, "failing": j.failing, "null_share": j.null_share}
                          for kind, j in s.sides.items()},
            }]
    document = {
        "value": value, "seconds": round(seconds, 1),
        "products": [{"table": r.table, "seed": r.seed, **r.product} for r in runs],
        "script_seconds": {stem: round(sum(x.seconds for r in runs for x in [r.real.get(stem)] if x), 2)
                           for stem in B.SCRIPTS},
        "reasons": B.reasons(runs),
        "verdicts": verdicts,
    }
    path.write_text(json.dumps(document, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")


def emit(value: "dict[str, object]", suffix: str, seconds: float) -> None:
    """K-RU-01's KPI line, with the families and the controls named in its detail."""
    families = value.get("families" + suffix) or {}
    said = "; ".join(f"{family} {v['twin']} of {v['n']} (fresh {v['replicate']}, shuffled {v['shuffled']}, "
                     f"runs {v['runs']})" for family, v in families.items())  # type: ignore[index, union-attr]
    kpi_rules.emit("K-RU-01", value,
                   f"same_rel {value.get('same_rel' + suffix)}, runs {value.get('runs' + suffix)}; per family: {said}; "
                   f"void: {value.get('void_families' + suffix) or 'none'}; {round(seconds)} s")


def run_tier(tier: str, folder: pathlib.Path, zoo: bool, report_path: "pathlib.Path | None") -> None:
    """One tier in this process: every table and seed, then the KPI line."""
    started = time.perf_counter()
    settings = B.TIERS[tier]
    suffix = "_200k" if settings["rows"] >= 200000 else "_20k"
    runs = B.run_tables(T.TABLES, settings["rows"], settings["seeds"], settings["twins"], folder, log=sys.stdout)
    value = B.kpi_value(runs, suffix, f0_value(zoo))
    seconds = time.perf_counter() - started
    if report_path is not None:
        report(runs, value, report_path, seconds)
    emit(value, suffix, seconds)


def run_one(table: str, seed: int, rows: int, twins: "tuple[int, ...]", folder: pathlib.Path, out: pathlib.Path,
            companions: "pathlib.Path | None") -> None:
    """One table at one seed in this process, its run written to ``out`` (T1 also writes its sides for T5)."""
    keep: "dict[str, str]" = {}
    cohort = json.loads(companions.read_text(encoding="utf-8")) if companions and companions.exists() else None
    run = B.run_table(table, rows, seed, twins, folder / f"{table}-{seed}", companions=cohort,
                      keep=keep if table == "T1" else None, log=sys.stdout)
    out.write_text(json.dumps(B.run_to_dict(run)) + "\n", encoding="utf-8", newline="\n")
    if table == "T1":
        out.with_name(f"cohort-sides-{seed}.json").write_text(json.dumps(keep), encoding="utf-8", newline="\n")


def run_night(folder: pathlib.Path, zoo: bool, report_path: "pathlib.Path | None") -> None:
    """The 200,000-row tier: each table in a child process of its own, waiting while a whole suite runs."""
    started = time.perf_counter()
    settings = B.TIERS["night"]
    runs = []
    for seed in settings["seeds"]:
        for table in sorted(T.TABLES, key=lambda t: (t != "T1", t)):
            while busy():
                time.sleep(30)
            out = folder / f"{table}-{seed}.json"
            arguments = [sys.executable, str(THIS), "--one", table, "--seed", str(seed), "--rows",
                         str(settings["rows"]), "--out", str(folder), "--json", str(out)]
            if table == "T5":
                arguments += ["--companions", str(folder / f"cohort-sides-{seed}.json")]
            done = subprocess.run(arguments, check=False)
            if done.returncode != 0 or not out.exists():
                print(f"{table} seed {seed}: the child exited {done.returncode}", flush=True)
                sys.exit(1)
            runs += [B.run_from_dict(json.loads(out.read_text(encoding="utf-8")))]
    value = B.kpi_value(runs, "_200k", f0_value(zoo))
    seconds = time.perf_counter() - started
    if report_path is not None:
        report(runs, value, report_path, seconds)
    emit(value, "_200k", seconds)


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--kpi", action="store_true", help="the 20,000-row tier: 3 table seeds x 3 twin seeds")
    parser.add_argument("--quick", action="store_true", help="one table seed and one twin seed at 20,000 rows")
    parser.add_argument("--night", action="store_true", help="the 200,000-row tier, a child per table")
    parser.add_argument("--one", metavar="TABLE", help="one table in this process (a night's child)")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--rows", type=int, default=B.TIERS["night"]["rows"])
    parser.add_argument("--json", help="where --one writes its run")
    parser.add_argument("--companions", help="the cohort's sides a T5 child reads")
    parser.add_argument("--zoo", action="store_true", help="run the zoo's 20,000-row leg for F0")
    parser.add_argument("--report", help="where to write every verdict as JSON")
    parser.add_argument("--out", help="the work folder")
    args = parser.parse_args(argv)
    named = args.report or os.environ.get("SYNTHTWIN_RELIABILITY_REPORT", "")
    report_path = pathlib.Path(named) if named else None
    if args.one:
        run_one(args.one, args.seed, args.rows, B.TIERS["night"]["twins"], pathlib.Path(args.out),
                pathlib.Path(args.json), pathlib.Path(args.companions) if args.companions else None)
        return 0
    with tempfile.TemporaryDirectory(prefix="synthtwin-reliability-") as scratch:
        folder = pathlib.Path(args.out) if args.out else pathlib.Path(scratch)
        folder.mkdir(parents=True, exist_ok=True)
        if args.kpi:
            run_tier("kpi", folder / "kpi", args.zoo, report_path)
        if args.quick:
            run_tier("quick", folder / "quick", args.zoo, report_path)
        if args.night:
            (folder / "night").mkdir(parents=True, exist_ok=True)
            run_night(folder / "night", args.zoo, report_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())

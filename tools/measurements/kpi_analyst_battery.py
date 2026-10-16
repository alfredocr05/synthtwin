"""K-BC-01 to K-BC-13, the slow part: the analyst battery over all six seeded tables (plan P4-D398).

The suite runs the battery's FAST part (`tests/analyst_battery.py`,
ST1 and ST2 at 5,000 rows, one seed). This driver runs the rest, through
the same code, so the suite and the night cannot judge one table two
ways:

* ``--kpi`` -- the 20,000-row tier: all six tables (ST1 to ST6), table
  seeds 1 to 3, today's twin at twin seeds 0 to 4 beside the fresh
  replicate and the shuffled twin at the same five seeds, and the thin
  replicate (twin-seed stability's negative control). It prints one KPI
  line for each of K-BC-01 to K-BC-10 and K-BC-12, every key suffixed
  `_20k`. About an hour on the reference machine.
* ``--night`` -- the 200,000-row tier: each table once, seed 1, twin
  seed 0, in a child process of its own so that each table's seconds and
  peak memory are its own (the child's `ru_maxrss`, which counts the
  product's describe and generate as well as the battery). It prints
  K-BC-13's `_200k` keys: the slowest table's seconds, the largest peak,
  the tables run, and the KPIs whose controls do not hold at that size.
  About two hours; never beside a whole suite (the machine's rule).
* ``--one TABLE`` -- one table in this process (what ``--night`` runs in
  each child), its results written as JSON to ``--json``.

``--out`` names the folder the tables, descriptions and twins are
written to (default: a temporary folder, removed after). Nothing is
committed: every table is drawn from its seed at run time.

THE NIGHT WAITS ITS TURN. Where the environment names paths in
``SYNTHTWIN_PAUSE_WHILE`` (separated as PATH is), the night starts each
table only once every one of them is absent or an empty folder -- point
it at a machine's whole-suite lock and its queue, and no 200,000-row
table starts beside a whole suite.

    .venv/bin/python tools/measurements/kpi_analyst_battery.py --kpi
    .venv/bin/python tools/measurements/kpi_analyst_battery.py --night
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import resource
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import analyst_battery as B  # noqa: E402
import kpi_rules  # noqa: E402

THIS = pathlib.Path(__file__).resolve()


def peak_mb() -> float:
    """This process's peak resident memory in MB (macOS reports bytes, Linux kilobytes)."""
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(peak / 1e6 if sys.platform == "darwin" else peak / 1e3, 1)


def emit_values(values: "dict[str, dict[str, object]]") -> None:
    """One KPI line per entry, its `_detail` given as the line's detail."""
    for kpi in sorted(values):
        value = dict(values[kpi])
        detail = str(value.pop("_detail", ""))
        kpi_rules.emit(kpi, B.finite(value), detail)


def run_kpi(folder: pathlib.Path) -> None:
    """The 20,000-row tier, every table and seed in this process."""
    started = time.perf_counter()
    runs = []
    for table in B.TIERS["slow"]["tables"]:
        for seed in B.TIERS["slow"]["seeds"]:
            run = B.run_table(table, B.TIERS["slow"]["rows"], seed, B.TIERS["slow"]["twins"], "slow",
                              folder / f"{table}-{seed}", thin=True)
            print(f"{table} seed {seed}: {run.seconds:.0f} s ({run.product_seconds:.0f} s in the product)",
                  flush=True)
            runs += [run]
    values = B.kpi_values(runs, "_20k")
    values["K-BC-12"] = B.kpi_12(runs, "_20k")
    failing = B.controls_failing(values)
    values["K-BC-13"] = {
        "controls_failing_20k": len(failing),
        "seconds_per_table_seed_20k": round(max(r.seconds for r in runs), 1),
        "seconds_total_20k": round(time.perf_counter() - started, 1),
        "_detail": "controls failing at 20,000 rows: " + (", ".join(failing) or "none"),
    }
    emit_values(values)


def run_one(table: str, rows: int, folder: pathlib.Path, out: pathlib.Path) -> None:
    """One table of the night in this process; its runs, seconds and peak written to ``out``."""
    started = time.perf_counter()
    run = B.run_table(table, rows, 1, (0,), "night", folder / table)
    record = {"run": B.run_to_dict(run), "seconds": round(time.perf_counter() - started, 1),
              "peak_mb": peak_mb()}
    out.write_text(json.dumps(record), encoding="utf-8", newline="\n")


def busy() -> "list[str]":
    """The paths named in SYNTHTWIN_PAUSE_WHILE that exist as a file or a folder with anything in it."""
    held = []
    for name in os.environ.get("SYNTHTWIN_PAUSE_WHILE", "").split(os.pathsep):
        path = pathlib.Path(name) if name else None
        if path is not None and (path.is_file() or (path.is_dir() and any(path.iterdir()))):
            held += [name]
    return held


def run_night(folder: pathlib.Path) -> None:
    """The 200,000-row tier: each table in a child process of its own."""
    found = []
    for table in B.TIERS["night"]["tables"]:
        waited = 0
        while busy():
            if waited % 600 == 0:
                print(f"{table}: waiting while {', '.join(busy())} is held", flush=True)
            time.sleep(30)
            waited += 30
        out = folder / f"{table}.json"
        done = subprocess.run(
            [sys.executable, str(THIS), "--one", table, "--rows", str(B.TIERS["night"]["rows"]),
             "--out", str(folder), "--json", str(out)], check=False)
        if done.returncode != 0 or not out.exists():
            print(f"{table}: the child exited {done.returncode}", flush=True)
            sys.exit(1)
        record = json.loads(out.read_text(encoding="utf-8"))
        print(f"{table}: {record['seconds']} s, peak {record['peak_mb']} MB", flush=True)
        found += [record]
    runs = [B.run_from_dict(record["run"]) for record in found]
    values = B.kpi_values(runs, "_200k")
    failing = B.controls_failing(values)
    slowest = max(found, key=lambda r: r["seconds"])
    largest = max(found, key=lambda r: r["peak_mb"])
    gaps = values.get("K-BC-01", {})
    kpi_rules.emit("K-BC-13", {
        "seconds_per_table_200k": slowest["seconds"],
        "peak_mb_200k": largest["peak_mb"],
        "tables_200k": len(found),
        "controls_failing_200k": len(failing),
    }, "per table at 200,000 rows: " + "; ".join(
        f"{r['run']['table']} {r['seconds']} s {r['peak_mb']} MB" for r in found)
        + "; controls failing: " + (", ".join(failing) or "none")
        + f"; K-BC-01 at 200,000 rows: {B.finite(gaps.get('pooled_points_below_replicate_200k'))} points below the replicate")


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--kpi", action="store_true", help="the 20,000-row tier")
    parser.add_argument("--night", action="store_true", help="the 200,000-row tier, a child per table")
    parser.add_argument("--one", metavar="TABLE", help="one table in this process (a night's child)")
    parser.add_argument("--rows", type=int, default=B.TIERS["night"]["rows"])
    parser.add_argument("--json", help="where --one writes its record")
    parser.add_argument("--out", help="the folder for tables, descriptions and twins")
    args = parser.parse_args(argv)
    kpi_rules.guard_this_tree()
    if args.one:
        run_one(args.one, args.rows, pathlib.Path(args.out), pathlib.Path(args.json))
        return 0
    with tempfile.TemporaryDirectory(prefix="synthtwin-analyst-") as scratch:
        folder = pathlib.Path(args.out) if args.out else pathlib.Path(scratch)
        folder.mkdir(parents=True, exist_ok=True)
        if args.kpi:
            run_kpi(folder / "slow")
        if args.night:
            (folder / "night").mkdir(parents=True, exist_ok=True)
            run_night(folder / "night")
    return 0


if __name__ == "__main__":
    sys.exit(main())

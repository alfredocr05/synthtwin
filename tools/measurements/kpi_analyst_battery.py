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
  About two hours; never beside a whole suite (the machine's rule). It
  first checks ST4's chapter-B truth on a 200,000-row table (about 3 s and
  85 MB, the table generator and one fit, no product): the estimate within
  four standard errors of the estimand `analyst_tables` states, and those
  under 0.3; a miss exits 1 before any table runs. The suite checks the
  estimand against the generator's constants, and the generator against
  them row by row, at a few thousand rows.
* ``--one TABLE`` -- one table in this process (what ``--night`` runs in
  each child), its results written as JSON to ``--json``.

``--out`` names the folder the tables, descriptions and twins are
written to (default: a temporary folder, removed after). Nothing is
committed: every table is drawn from its seed at run time. Peak memory
is read from `resource`, which Windows lacks: there the peak is not
measured and every statistic still is.

A RUN KEPT FOR ITS KPIs. Where the environment names a folder in
``SYNTHTWIN_ANALYST_RUNS``, ``--kpi`` writes each table run there as JSON
beside a digest of the code its panels come from -- the product's
source, and every module under tests/ the battery loads to make them
(the kit, the tables, `kpi_shapes` and what it loads, the battery up to
its KPI functions) -- and on a later ``--kpi`` reads a run back instead
of running it again
only where that digest is unchanged: a KPI function changed after the
runs is re-read over the same panels, and any change to what makes a
panel runs the tables afresh.

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
import hashlib
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
import analyst_battery as B  # noqa: E402
import analyst_tables as T  # noqa: E402
import kpi_rules  # noqa: E402

THIS = pathlib.Path(__file__).resolve()


def peak_mb() -> "float | None":
    """This process's peak resident memory in MB (macOS reports bytes, Linux kilobytes); None without `resource`.

    `resource` is Unix's: imported here, not at the top, so that on
    Windows the driver still runs and only the peak goes unmeasured.
    """
    try:
        import resource
    except ImportError:
        return None
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(peak / 1e6 if sys.platform == "darwin" else peak / 1e3, 1)


def emit_values(values: "dict[str, dict[str, object]]") -> None:
    """One KPI line per entry, its `_detail` given as the line's detail."""
    for kpi in sorted(values):
        value = dict(values[kpi])
        detail = str(value.pop("_detail", ""))
        kpi_rules.emit(kpi, B.finite(value), detail)


KPI_MARK = "# -- the KPIs --"


# Modules under tests/ that never make a panel: the ledger's judge reads
# the KPI values only.
NOT_PANEL = ("kpi_rules",)


def panel_code_files() -> "list[pathlib.Path]":
    """Every file a table run's panels come from: src/, and each module under tests/ the battery loads.

    The battery reaches the product's description through `kpi_shapes`,
    which loads `fixtures` and `workbooks`. Loading it here loads that
    whole chain, and every module then loaded from tests/ is read: a
    digest of the kit, the tables and the battery alone let panels made
    by an old helper be read back as current (Codex's review).
    """
    import kpi_shapes  # noqa: F401  (the chain the battery's description reaches)

    tests = (ROOT / "tests").resolve()
    files = sorted((ROOT / "src").rglob("*.py"))
    for name, module in sorted(list(sys.modules.items())):
        where = getattr(module, "__file__", None)
        if where and name not in NOT_PANEL and pathlib.Path(where).resolve().parent == tests:
            files += [pathlib.Path(where).resolve()]
    return files


def panel_code_digest() -> str:
    """The sha256 of the code a table run's panels come from (`panel_code_files`), the battery to its KPIs."""
    digest = hashlib.sha256()
    for path in panel_code_files():
        text = path.read_bytes()
        if path.name == "analyst_battery.py":
            text = text.decode("utf-8").split(KPI_MARK)[0].encode("utf-8")
        digest.update(path.resolve().relative_to(ROOT.resolve()).as_posix().encode("utf-8") + b"\0" + text)
    return digest.hexdigest()


def run_kpi(folder: pathlib.Path) -> None:
    """The 20,000-row tier, every table and seed in this process (or read back where kept, see the module)."""
    started = time.perf_counter()
    kept = os.environ.get("SYNTHTWIN_ANALYST_RUNS")
    code = panel_code_digest()
    runs = []
    for table in B.TIERS["slow"]["tables"]:
        for seed in B.TIERS["slow"]["seeds"]:
            saved = pathlib.Path(kept) / f"{table}-{seed}.json" if kept else None
            if saved is not None and saved.exists():
                record = json.loads(saved.read_text(encoding="utf-8"))
                if record.get("code") == code:
                    runs += [B.run_from_dict(record["run"])]
                    print(f"{table} seed {seed}: read back from {saved}", flush=True)
                    continue
            run = B.run_table(table, B.TIERS["slow"]["rows"], seed, B.TIERS["slow"]["twins"], "slow",
                              folder / f"{table}-{seed}", thin=True)
            print(f"{table} seed {seed}: {run.seconds:.0f} s ({run.product_seconds:.0f} s in the product)",
                  flush=True)
            if saved is not None:
                saved.parent.mkdir(parents=True, exist_ok=True)
                saved.write_text(json.dumps({"code": code, "run": B.run_to_dict(run)}), encoding="utf-8",
                                 newline="\n")
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


def chapter_b_truth(rows: int = 200_000) -> bool:
    """ST4's chapter-B truth on a table of ``rows`` rows: within 4 standard errors of the estimand, and those under 0.3."""
    _key, stated = T.TRUTHS["ST4"]["outcome by chapter"]
    value, se = T.st4_chapter_b_fit(rows, 1)
    held = 4.0 * se < 0.3 and abs(value - stated) <= 4.0 * se
    print(f"ST4 chapter B at {rows:,} rows: {value:.3f} (se {se:.3f}) against the estimand {stated:.3f}: "
          + ("held" if held else "MISSED"), flush=True)
    return held


def run_night(folder: pathlib.Path) -> None:
    """The 200,000-row tier: the chapter-B truth first, then each table in a child process of its own."""
    if not chapter_b_truth():
        sys.exit(1)
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
    largest = max(found, key=lambda r: -1.0 if r["peak_mb"] is None else r["peak_mb"])
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

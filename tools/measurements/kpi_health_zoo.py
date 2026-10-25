"""K-HZ-01, K-HZ-02, K-HZ-03 and K-HZ-05: the health data zoo at 600 and 20,000 rows, in shards, timed (plans P4-D399, P4-D431).

Runs `tests/health_zoo.py`'s whole catalogue -- E0a's twenty-five
exports and lane E0c's widening to every kind of the zoo plan's section
6 (b), each profiled, answered with general facts about the data,
generated, validated and read by the analyst's own script on the real
table and on the twin -- shard by shard (`health_zoo.shards()`, at most
thirty kinds a shard, a table's kinds in one), twice, in this process:
at the suite's 600 rows, BELOW THE OWNER'S TABLE FLOOR, with the
command's internal switch off as the suite runs it; then at 20,000 rows,
the KPI size, with the SHIPPED floor on (plan P4-D425: `cli.main`'s
`small_tables_refused` passed True), each shard timed on its own. This
process's peak resident memory is read at the end. It prints

- K-HZ-01's slow keys: the kinds that pass under the pass rule of plan
  P4-D431 (they pass at 20,000 rows with the floor on, the questions
  general and the analyst's script holding on the real table there, AND
  their 600-row smoke runs every step to exit 0 or 3), the failing
  kinds named, and the 20,000-row prerequisites and owners;
- K-HZ-02's slow keys: the failures per (kind, check) at 20,000 rows,
  each with its owner lane, and the real values of person, place and
  record columns found published there (HIPAA first);
- K-HZ-03: the seconds of each shard at 600 rows (the suite's fixture
  runs the same shards) and at 20,000 rows, the peak memory in
  megabytes, and the table runs, a machine-free count beside them;
- K-HZ-05: the kinds the shipped floor refused at 20,000 rows, and the
  fewest people a several-rows-per-patient kind's table holds there.

Each table is written into a folder of its own under a temporary folder,
and each shard's folder is removed when the shard is done; nothing is
kept. Where openpyxl is absent the workbook exports are left out of both
runs and said so. The peak memory is read through `resource`, which
Windows lacks: there the key is left out and the line says it was not
measured. Every 20,000-row run of this driver goes through the lane's
memory guard (planning-notes lib-study/formats-probes/guard.sh).

    .venv/bin/python tools/measurements/kpi_health_zoo.py --kpi
"""

import pathlib
import shutil
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import health_zoo  # noqa: E402
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()

SMALL = health_zoo.SMOKE_ROWS
LARGE = health_zoo.KPI_ROWS


def _peak_megabytes() -> "float | None":
    """This process's peak resident memory: bytes on macOS, kilobytes on Linux; None without `resource`."""
    try:
        import resource
    except ImportError:
        return None
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    scale = 1 if sys.platform == "darwin" else 1024
    return round(peak * scale / 1_000_000, 1)


def _run_shards(folder: pathlib.Path, rows: int) -> "tuple[list[dict], list[float]]":
    """Every shard at one size, in order: the results, and each shard's seconds."""
    results: "list[dict]" = []
    seconds: "list[float]" = []
    for place, tables in enumerate(health_zoo.shards(), 1):
        home = folder / f"{rows}-shard-{place}"
        started = time.perf_counter()
        results += health_zoo.run_zoo(home, rows, tables=tables)
        seconds += [round(time.perf_counter() - started, 1)]
        shutil.rmtree(home, ignore_errors=True)
    return results, seconds


def _per_kind(kinds: "dict[str, dict]") -> "dict[str, str]":
    """Each failing kind's step, its failures and its owners, as K-HZ-02 prints them."""
    said: "dict[str, str]" = {}
    for kind, verdict in kinds.items():
        if verdict["passed"]:
            said[kind] = "passes"
            continue
        said[kind] = (
            f"{verdict['failing_step']}: {len(verdict['failures'])} failing; "
            f"{', '.join(verdict['owners']) or 'NO OWNER'}"
            + (f"; UNOWNED {verdict['unowned']}" if verdict["unowned"] else "")
            + (f"; NEEDING AN OWNER {verdict['needing_owner']}" if verdict["needing_owner"] else "")
        )
    return said


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="synthtwin-health-zoo-") as folder:
        small, small_seconds = _run_shards(pathlib.Path(folder), SMALL)
        large, large_seconds = _run_shards(pathlib.Path(folder), LARGE)
    measured_large = health_zoo.zoo_measures(large)
    smoke = health_zoo.smoke_ran(small)
    for kind, verdict in measured_large["kinds"].items():
        state = "passes" if verdict["passed"] else f"fails at {verdict['failing_step']}"
        print(f"20,000 rows: {kind} {state}; {len(verdict['failures'])} failing "
              f"{verdict['failures']}; smoke at 600 rows {'runs' if smoke.get(kind) else 'STOPS'}")
    kinds = list(measured_large["kinds"])
    passing = [kind for kind in kinds if measured_large["kinds"][kind]["passed"] and smoke.get(kind)]
    workbook = set(health_zoo.workbook_kinds())
    failing = ", ".join(kind for kind in kinds if kind not in passing) or "none"
    every_table = health_zoo.catalogue()
    left_out = [table.name for table in every_table if table not in health_zoo.runnable_tables(every_table)]
    # Where the workbook reader is absent the workbooks are not run, so the
    # keys over every export are left out rather than printed short; the
    # delimited exports' keys are measured everywhere.
    whole = not left_out
    large_first = measured_large["K-HZ-01"]
    large_second = measured_large["K-HZ-02"]
    first: "dict[str, object]" = {
        "kinds_passing_csv": sum(1 for kind in passing if kind not in workbook),
        "kinds_smoke_600_rows_running": sum(1 for kind in kinds if smoke.get(kind)),
        "questions_not_general_20000_rows": large_first["questions_not_general"],
        "analyst_errors_on_real_20000_rows": large_first["analyst_errors_on_real"],
        "failures_needing_owner_20000_rows": large_second["failures_needing_owner"],
        "failures_without_owner_20000_rows": large_second["failures_without_owner"],
        "kinds_failing_named": failing,
    }
    if whole:
        first["kinds_passing"] = len(passing)
        first["kinds_in_catalogue"] = len(kinds)
    kpi_rules.emit(
        "K-HZ-01",
        first,
        f"{len(passing)} of {len(kinds)} kinds pass at 20,000 rows with the floor on, their 600-row smoke "
        f"running; failing: {failing}"
        + (f"; not run here, no workbook reader: {left_out}" if left_out else ""),
    )
    second: "dict[str, object]" = {
        "kinds_failing_20000_rows_csv": large_second["kinds_failing_csv"],
        "failing_kinds_without_owner_20000_rows": large_second["failing_kinds_without_owner"],
        "failures_without_owner_20000_rows": large_second["failures_without_owner"],
        "failures_needing_owner_20000_rows": large_second["failures_needing_owner"],
        "real_values_published_20000_rows": large_second["real_values_published"],
        "real_values_published_20000_rows_named": large_second["real_values_published_named"],
        "per_kind_20000_rows": _per_kind(measured_large["kinds"]),
    }
    if whole:
        second["kinds_failing_20000_rows"] = large_second["kinds_failing"]
        second["failures_20000_rows"] = large_second["failures"]
        second["validate_misses_20000_rows"] = large_second["validate_misses"]
        second["analyst_failures_20000_rows"] = large_second["analyst_failures"]
    kpi_rules.emit("K-HZ-02", second, f"{large_second['failures']} failures at 20,000 rows over {len(kinds)} kinds")
    found: "dict[str, object]" = {
        "seconds_600_rows": round(sum(small_seconds), 1),
        "shards": len(large_seconds),
        "kinds_in_largest_shard": max(sum(len(table.kinds) for table in shard) for shard in health_zoo.shards()),
        "tables_run_csv": sum(1 for result in small + large if health_zoo.table_named(result["table"]).suffix != ".xlsx"),
    }
    for place, seconds in enumerate(small_seconds, 1):
        found[f"seconds_600_rows_shard_{place}"] = seconds
    for place, seconds in enumerate(large_seconds, 1):
        found[f"seconds_20000_rows_shard_{place}"] = seconds
    if whole:
        found["tables_run"] = len(small) + len(large)
    peak = _peak_megabytes()
    if peak is not None:
        found["peak_memory_mb"] = peak
    said = [f"600-row shards {small_seconds} s"]
    said += [] if peak is not None else ["peak memory not measured: this platform has no resource module"]
    said += [f"not run here, no workbook reader: {left_out}"] if left_out else []
    kpi_rules.emit("K-HZ-03", found, "; ".join(said))
    fifth = measured_large["K-HZ-05"]
    kpi_rules.emit(
        "K-HZ-05",
        dict(fifth),
        f"{fifth['kinds_refused_by_floor']} kinds refused at 20,000 rows; the fewest people a several-rows "
        f"kind holds there {fifth['fewest_people']}",
    )


if __name__ == "__main__":
    main()

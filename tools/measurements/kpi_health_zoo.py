"""K-HZ-01 and K-HZ-03: the health data zoo at 600 and 20,000 rows, timed (plan P4-D399).

Runs `tests/health_zoo.py`'s battery -- twenty-three exports holding
the thirty-six kinds of healthcare data, each profiled, answered with
general facts about the data, generated, validated and read by the
analyst's own script on the real table and on the twin -- twice, in
this process: at the suite's 600 rows, timed, and at 20,000 rows,
timed, with this process's peak resident memory read at the end. It
prints

- K-HZ-01's slow keys at 20,000 rows: the kinds that pass end to end,
  the questions that are not general and the analyst's faults on the
  real tables (the suite's test measures the 600-row keys), with the
  failing kinds named;
- K-HZ-03: the seconds of each run, the peak memory in megabytes, and
  the tables run, a machine-free count beside them.

Each table is written into a folder of its own under a temporary
folder that is removed at the end; nothing is kept. Where openpyxl is
absent the workbook export is left out of both runs and said so. The
peak memory is read through `resource`, which Windows lacks: there the
key is left out and the line says it was not measured.

    .venv/bin/python tools/measurements/kpi_health_zoo.py --kpi
"""

import pathlib
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import health_zoo  # noqa: E402
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()

SMALL = 600
LARGE = 20_000


def _peak_megabytes() -> "float | None":
    """This process's peak resident memory: bytes on macOS, kilobytes on Linux; None without `resource`."""
    try:
        import resource
    except ImportError:
        return None
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    scale = 1 if sys.platform == "darwin" else 1024
    return round(peak * scale / 1_000_000, 1)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="synthtwin-health-zoo-") as folder:
        started = time.perf_counter()
        small = health_zoo.run_zoo(pathlib.Path(folder) / "small", SMALL)
        small_seconds = round(time.perf_counter() - started, 1)
        started = time.perf_counter()
        large = health_zoo.run_zoo(pathlib.Path(folder) / "large", LARGE)
        large_seconds = round(time.perf_counter() - started, 1)
    measured_small = health_zoo.zoo_measures(small)
    measured_large = health_zoo.zoo_measures(large)
    for kind, verdict in measured_large["kinds"].items():
        state = "passes" if verdict["passed"] else f"fails at {verdict['failing_step']}"
        print(f"20,000 rows: {kind} {state}; {verdict['misses']} missed; "
              f"{len(verdict['analyst_failures'])} analyst failure(s)")
    large_first = measured_large["K-HZ-01"]
    passing = large_first["kinds_passing_end_to_end"]
    failing = ", ".join(large_first["failing"]) or "none"
    left_out = [table.name for table in health_zoo.TABLES if table not in health_zoo.runnable_tables()]
    kpi_rules.emit(
        "K-HZ-01",
        {
            "kinds_passing_20000_rows": passing,
            "questions_not_general_20000_rows": large_first["questions_not_general"],
            "analyst_errors_on_real_20000_rows": large_first["analyst_errors_on_real"],
            "kinds_failing_20000_rows_named": failing,
        },
        f"{passing} of {large_first['kinds']} kinds at 20,000 rows; failing: {failing}"
        + (f"; not run here, no workbook reader: {left_out}" if left_out else ""),
    )
    found: "dict[str, object]" = {
        "seconds_600_rows": small_seconds,
        "seconds_20000_rows": large_seconds,
        "tables_run": len(small) + len(large),
        "kinds_passing_600_rows": measured_small["K-HZ-01"]["kinds_passing_end_to_end"],
    }
    peak = _peak_megabytes()
    if peak is not None:
        found["peak_memory_mb"] = peak
    kpi_rules.emit(
        "K-HZ-03",
        found,
        "" if peak is not None else "peak memory not measured: this platform has no resource module",
    )


if __name__ == "__main__":
    main()

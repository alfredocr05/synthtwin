"""K-S4-09's generate part and K-S4-12: `synthtwin generate` of the big table, its memory and its seconds.

PLAN P4-D415 (lane SG of the December plan). The owner's big table is
2,000,000 rows by 50 columns, and the process building its twin must fit
under the 2.5 GB the watchdog lets one process hold. `synthtwin
generate` now holds each finished column as its cells' own bytes
(`twinstore`), places the rows a column at a time and writes the twin a
piece at a time, so what it holds grows with the twin's text and one
column's working set, not with the whole table as Python objects.

The two tables are lane B0's, as K-S4-09's describe part measures them
(`kpi_describe_groups.write`): the made-up 50-column health table of
K-S4-02 and K-S1-06's Gaussian columns at 50 columns. No value comes
from a real table. Each size is described first by `synthtwin profile`
in a process of its own, which this driver does not measure, and its
description is then generated at seed 0.

    kpi_generate_memory.py write {mixed|gaussian} ROWS PATH
    kpi_generate_memory.py describe TABLE OUT_DIR
    kpi_generate_memory.py run DESCRIPTION OUT_DIR [--trace]
    kpi_generate_memory.py workbook ROWS
    kpi_generate_memory.py --kpi [--night]

`run` generates one description with `synthtwin generate` in THIS
process and prints one line of JSON: the CPU seconds, the process's
peak resident memory (`ru_maxrss`) and, with --trace, the most bytes
`tracemalloc` saw held. `workbook` writes a workbook twin of ROWS rows
of fifty columns -- a held twin of lane XW's seeded wide workbook, its
records repeated in turn (`tests/workbook_stream_cases.stretched`'s
rule) -- by `sheetwriting.workbook_stream` and
`writing.write_workbook_file`, and prints its seconds and peak.

`--kpi` measures, each run in a process of its own, one at a time:

* K-S4-09's machine-free keys (generate's part): each table of 50,000
  rows by 50 generated once with `tracemalloc` on, the most bytes it saw
  held over the cells (`*_generate_traced_bytes_a_cell`: at 100,000,000
  cells, 17.7 bytes a cell and the 78 MB of imports are the watchdog's
  2,560 MiB with the resident peak taken as 1.4 times the traced one,
  K-S4-09's describe bound);
* K-S4-09's machine keys and K-S4-12, RECORDED: each table at 50,000
  and 100,000 rows (with --night 100,000, 200,000, 500,000 and
  1,000,000), the peak
  resident memory and CPU seconds of the generate run, and the
  projection to 2,000,000 rows as lane B0 makes it, a least-squares
  line through log(rows) and log(value) over the three largest sizes
  (over two by day, which says so), memory as its rise above what the
  process holds once synthtwin is imported; judged only on the quiet
  reference machine (`kpi_rules.MACHINE_KINDS`), and the 2,000,000-row
  projection of memory only from the night's sizes.

By day about ninety minutes (four descriptions, six generate runs);
--night about five hours: run it in a NIGHT window, one heavy process at
a time, the watchdog running (`wave6/SG/night-sg.sh` in the notes).
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import math
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import tracemalloc

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tools" / "measurements"))

import kpi_rules  # noqa: E402

COLUMNS = 50
BIG_ROWS = 2_000_000
TRACED_ROWS = 50_000
SIZES = (50_000, 100_000)
NIGHT_SIZES = (100_000, 200_000, 500_000, 1_000_000)
MEBIBYTE = 1024 * 1024


def write(kind: str, rows: int, path: pathlib.Path) -> None:
    """One of K-S4-09's two made-up tables, ``rows`` rows by 50 columns."""
    import kpi_describe_groups

    kpi_describe_groups.write(kind, rows, path)


def _resident_peak() -> int:
    """This process's peak resident memory in bytes, or -1 where it cannot be read."""
    try:
        import resource
    except ImportError:
        return -1
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # ru_maxrss is in bytes on macOS and in kilobytes on Linux.
    return peak if sys.platform == "darwin" else peak * 1024


def describe(table: str, out: pathlib.Path) -> "dict[str, object]":
    """`synthtwin profile` of ``table`` in this process; its exit code."""
    from synthtwin import cli

    said = io.StringIO()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(["profile", table, "--out-dir", str(out), "--replace"])
    return {"exit": code}


def run(description: str, out: pathlib.Path, trace: bool) -> "dict[str, object]":
    """`synthtwin generate` of ``description`` in this process; what it took. An empty one imports only."""
    from synthtwin import cli
    import synthtwin

    if not description:
        return {"exit": 0, "cpu_seconds": 0.0, "peak_rss_bytes": _resident_peak(), "synthtwin": synthtwin.__file__}
    if trace:
        tracemalloc.start()
    said = io.StringIO()
    started = time.process_time()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(
            ["generate", description, "--out-dir", str(out), "--seed", "0", "--replace"]
        )
    seconds = time.process_time() - started
    traced = -1
    if trace:
        traced = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
    return {
        "exit": code,
        "cpu_seconds": round(seconds, 1),
        "peak_rss_bytes": _resident_peak(),
        "traced_peak_bytes": traced,
        "synthtwin": synthtwin.__file__,
    }


def workbook(n_rows: int) -> "dict[str, object]":
    """A held workbook twin of ``n_rows`` rows of fifty columns written; its seconds and memory."""
    import workbook_stream_cases as cases
    from synthtwin import generation, sheetwriting, twinstore, writing

    with tempfile.TemporaryDirectory() as folder:
        base = pathlib.Path(folder)
        described = cases.describe_book(base / "wide", "wide", cases.wide_book(300))
        small = generation.generate_held(described, 0)
        held: "list[twinstore.HeldColumn]" = []
        for index in range(generation.twin_width(small)):
            column = generation.twin_column(small, index)
            held += [twinstore.held_column([column[row % small.n_rows] for row in range(n_rows)])]
        twin = generation.Twin(
            names=small.names,
            write_header=small.write_header,
            n_rows=n_rows,
            columns=(),
            rows=(),
            outcomes=(),
            deviations=(),
            approximations=(),
            remarks=(),
            words_drawn=0,
            seed=small.seed,
            held_columns=tuple(held),
        )
        before = _resident_peak()
        began = time.perf_counter()
        parts = sheetwriting.workbook_stream(described, twin)
        prepared = time.perf_counter()
        sheet = [size for name, size, _pieces in parts if name.startswith("xl/worksheets/")]
        writing.write_workbook_file(base / "twin.xlsx", parts)
        ended = time.perf_counter()
        return {
            "rows": n_rows,
            "columns": len(twin.names),
            "sheet_bytes": sheet[0],
            "file_bytes": (base / "twin.xlsx").stat().st_size,
            "seconds_parts": round(prepared - began, 2),
            "seconds_write": round(ended - prepared, 2),
            "peak_rss_mb_before_parts": round(before / MEBIBYTE, 1),
            "peak_rss_mb": round(_resident_peak() / MEBIBYTE, 1),
        }


# THE GUARD (the orchestrator's memory rule of 2026-10-20): a child above
# the watchdog's 2.5 GB is stopped and the measurement fails, where `ps`
# can read its resident memory; checked every half second.
GUARD_KB = 2_500_000


def _resident_kb(pid: int) -> int:
    """A child's resident memory in KB from `ps`, or -1 where it cannot be read."""
    try:
        done = subprocess.run(["ps", "-o", "rss=", "-p", f"{pid}"], capture_output=True, text=True)
    except OSError:
        return -1
    text = done.stdout.strip()
    return int(text) if text.isdigit() else -1


def _child(argv: "list[str]") -> "dict[str, object]":
    """One action of this driver in a process of its own, so its peak is its own; its JSON.

    Run under nice and under `GUARD_KB`: a child past it is stopped and
    the driver exits with the size it was stopped at.
    """
    with tempfile.TemporaryFile("w+") as said:
        child = subprocess.Popen(
            ["nice", "-n", "10", sys.executable, str(pathlib.Path(__file__).resolve())] + argv,
            stdout=said,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        while child.poll() is None:
            if _resident_kb(child.pid) > GUARD_KB:
                child.kill()
                child.wait()
                raise SystemExit(f"{argv[0]} of {argv[1]} passed {GUARD_KB} KB and was stopped")
            time.sleep(0.5)
        said.seek(0)
        lines = said.read().strip().splitlines()
    if child.returncode != 0 or not lines:
        raise SystemExit(f"{argv[0]} of {argv[1]} exited {child.returncode}")
    found = json.loads(lines[-1])
    if found.get("exit", 0) != 0:
        raise SystemExit(f"{argv[0]} of {argv[1]} exited {found['exit']}")
    return found


def _number(value: object) -> float:
    """A measured number, read back from a run's JSON."""
    return float(f"{value}")


def projected(sizes: "list[int]", values: "list[float]", base: float = 0.0) -> "tuple[float, float]":
    """Lane B0's projection: the growth a doubling, and the value at 2,000,000 rows, of ``values`` above ``base``."""
    xs = [math.log(size) for size in sizes]
    ys = [math.log(max(value - base, 1e-9)) for value in values]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / sum((x - mean_x) ** 2 for x in xs)
    at = mean_y + slope * (math.log(BIG_ROWS) - mean_x)
    return 2 ** slope, math.exp(at) + base


def _generated(work: pathlib.Path, kind: str, rows: int, trace: bool) -> "dict[str, object]":
    """One size of one table written, described and generated; the generate run's record."""
    table = work / f"{kind}-{rows}.csv"
    write(kind, rows, table)
    described = work / f"{kind}-{rows}"
    described.mkdir(exist_ok=True)
    _child(["describe", str(table), str(described)])
    table.unlink()
    description = described / f"{kind}-{rows}-profile.json"
    out = work / f"{kind}-{rows}-twin"
    out.mkdir(exist_ok=True)
    found = _child(["run", str(description), str(out)])
    traced: "dict[str, object]" = {}
    if trace:
        traced = _child(["run", str(description), str(out), "--trace"])
    for made in out.iterdir():
        made.unlink()
    return {"run": found, "traced": traced}


def measure(night: bool) -> "tuple[dict[str, object], dict[str, object]]":
    """K-S4-09's generate keys and K-S4-12's values."""
    sizes = list(NIGHT_SIZES if night else SIZES)
    memory: "dict[str, object]" = {"rows_traced": TRACED_ROWS, "generate_sizes": sizes}
    seconds: "dict[str, object]" = {"sizes": sizes}
    with tempfile.TemporaryDirectory() as folder:
        work = pathlib.Path(folder)
        imports_peak = _number(_child(["run", "-", str(work)])["peak_rss_bytes"])
        resident = imports_peak >= 0
        imports = imports_peak / MEBIBYTE
        if resident:
            memory["generate_imports_mb"] = round(imports, 1)
        else:
            memory["resident_memory"] = "unavailable on this platform: no peak recorded"
        for kind in ("mixed", "gaussian"):
            peaks: "list[float]" = []
            cpu: "list[float]" = []
            for rows in sizes:
                found = _generated(work, kind, rows, rows == TRACED_ROWS)
                run_record = found["run"]
                if not isinstance(run_record, dict):
                    raise SystemExit("a generate run printed no record")
                peaks += [_number(run_record["peak_rss_bytes"]) / MEBIBYTE]
                cpu += [_number(run_record["cpu_seconds"])]
                traced = found["traced"]
                if isinstance(traced, dict) and traced:
                    memory[f"{kind}_generate_traced_bytes_a_cell"] = round(
                        _number(traced["traced_peak_bytes"]) / (TRACED_ROWS * COLUMNS), 1
                    )
            if TRACED_ROWS not in sizes:
                traced = _generated(work, kind, TRACED_ROWS, True)["traced"]
                if isinstance(traced, dict) and traced:
                    memory[f"{kind}_generate_traced_bytes_a_cell"] = round(
                        _number(traced["traced_peak_bytes"]) / (TRACED_ROWS * COLUMNS), 1
                    )
            top = sizes[-3:]
            if resident:
                growth, at = projected(top, peaks[-3:], imports)
                memory[f"{kind}_generate_peak_mb"] = [round(peak, 1) for peak in peaks]
                memory[f"{kind}_generate_peak_growth_a_doubling"] = round(growth, 3)
                key = "peak_mb_2m" if night else "peak_mb_2m_from_two_sizes"
                memory[f"{kind}_generate_{key}"] = round(at, 1)
            growth, at = projected(top, cpu[-3:])
            seconds[f"{kind}_generate_cpu_seconds"] = cpu
            seconds[f"{kind}_generate_seconds_growth_a_doubling"] = round(growth, 3)
            seconds[f"{kind}_generate_seconds_2m_projected"] = round(at, 1)
    return memory, seconds


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", nargs="?", default="")
    parser.add_argument("rest", nargs="*")
    parser.add_argument("--kpi", action="store_true")
    parser.add_argument("--night", action="store_true")
    parser.add_argument("--trace", action="store_true")
    arguments = parser.parse_args()
    if arguments.action == "write":
        kind, rows, path = arguments.rest
        write(kind, int(rows), pathlib.Path(path))
        return 0
    if arguments.action == "describe":
        table, out = arguments.rest
        print(json.dumps(describe(table, pathlib.Path(out))))
        return 0
    if arguments.action == "run":
        description, out = arguments.rest
        print(json.dumps(run("" if description == "-" else description, pathlib.Path(out), arguments.trace)))
        return 0
    if arguments.action == "workbook":
        print(json.dumps(workbook(int(arguments.rest[0]))))
        return 0
    if not arguments.kpi:
        print(__doc__)
        return 0
    kpi_rules.guard_this_tree()
    # The night's sizes by flag or, under `kpi_run.py`, which passes no
    # flag of its own, by SG_KPI_NIGHT=1 (`wave6/SG/night-sg.sh`).
    night = arguments.night or os.environ.get("SG_KPI_NIGHT") == "1"
    memory, seconds = measure(night)
    detail = (
        "B0's two made-up tables, 50 columns, described then generated at seed 0, "
        + ("projected from the three largest sizes" if night else "the day's two sizes")
    )
    kpi_rules.emit("K-S4-09", memory, detail)
    kpi_rules.emit("K-S4-12", seconds, detail)
    return 0


if __name__ == "__main__":
    sys.exit(main())

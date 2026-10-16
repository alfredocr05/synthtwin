"""K-S4-09 and K-S4-11: `synthtwin profile` of the big table, one group of columns at a time.

PLAN P4-D400 (lane SR of the December plan). The owner's big table is
2,000,000 rows by 50 columns, and the process describing it must fit
under the 2.5 GB the watchdog lets one process hold. `synthtwin profile`
now reads a table too large for one group of columns
(`reading.GROUP_BYTES`, 512 MiB) one group at a time, so what it holds
grows with one group's columns and one column's description, not with
the whole table.

The two tables are lane B0's (planning-notes/work-2026-10/wave6/B0): the
made-up 50-column health table of K-S4-02 (`kpi_reader_memory`'s:
record numbers, codes, labels, numbers in their spellings, dates,
stamps, clocks and free texts, seed 20261002) and K-S1-06's Gaussian
columns at two places (`kpi_scale.write_numeric`, seed 20260913), at 50
columns. No value comes from a real table.

    kpi_describe_groups.py write {mixed|gaussian} ROWS PATH
    kpi_describe_groups.py run TABLE OUT_DIR [--group-bytes N] [--trace]
    kpi_describe_groups.py --kpi

`run` describes one table in THIS process with `synthtwin profile` and
prints one line of JSON: the CPU seconds, the process's peak resident
memory (`ru_maxrss`) and, with --trace, the most bytes `tracemalloc` saw
held. --group-bytes sets `reading.GROUP_BYTES`.

THE BIG TABLE'S GROUPS, AT EVERY SIZE MEASURED. A group holds as many
columns as `GROUP_BYTES` buys at the table's rows, so 2,000,000 rows are
read about three columns a group and 100,000 rows at the same budget in
one group of fifty. Every run below is read with the budget scaled by
the rows (`GROUP_BYTES` times rows over 2,000,000), so each size is read
in the groups 2,000,000 rows are read in, and what it holds grows with
the rows as the big table's does.

`--kpi` measures, each run in a process of its own, one at a time:

* K-S4-09's machine-free keys: each table of 200,000 rows by 50
  described once with `tracemalloc` on, the most bytes it saw held over
  the cells (`*_traced_bytes_a_cell`, judged everywhere: at 100,000,000
  cells, 25 bytes a cell is 2.5 GB);
* K-S4-09's machine keys and K-S4-11: each table at 100,000, 250,000 and
  500,000 rows, its peak resident memory and CPU seconds, and the
  projection to 2,000,000 rows as lane B0 makes it -- a least-squares
  line through log(rows) and log(value) over the three sizes, read at
  2,000,000; memory as its rise above what the process holds once
  synthtwin is imported, measured here and added back; never linear
  unless the growth measured is x2.00. Peaks and seconds are the
  machine's and are judged only on the quiet reference machine
  (`kpi_rules.MACHINE_KINDS`).

About three hours on the reference machine: run it in a measurement
window, one heavy process at a time.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import math
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
TRACED_ROWS = 200_000
SIZES = (100_000, 250_000, 500_000)
# `reading.GROUP_BYTES` as shipped; read here from the module, below.
MEBIBYTE = 1024 * 1024


def write(kind: str, rows: int, path: pathlib.Path) -> None:
    """Write one of the two made-up tables, ``rows`` rows by 50 columns."""
    if kind == "mixed":
        import kpi_reader_memory

        kpi_reader_memory.write_table(path, rows)
        return
    import kpi_scale

    kpi_scale.write_numeric(path, rows, COLUMNS)


def _resident_peak() -> int:
    """The process's peak resident memory so far, in bytes, or -1 where it cannot be read."""
    try:
        import resource
    except ImportError:
        return -1
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # ru_maxrss is in bytes on macOS and in kilobytes on Linux.
    return peak if sys.platform == "darwin" else peak * 1024


def run(table: str, out: pathlib.Path, group_bytes: int, trace: bool) -> "dict[str, object]":
    """Describe ``table`` with `synthtwin profile` in this process; what it took. An empty table imports only."""
    from synthtwin import cli, reading
    import synthtwin

    if not table:
        return {"exit": 0, "cpu_seconds": 0.0, "peak_rss_bytes": _resident_peak(), "synthtwin": synthtwin.__file__}
    if group_bytes > 0:
        reading.GROUP_BYTES = group_bytes
    if trace:
        tracemalloc.start()
    said = io.StringIO()
    started = time.process_time()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(["profile", table, "--out-dir", str(out), "--replace"])
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
        "group_bytes": reading.GROUP_BYTES,
        "synthtwin": synthtwin.__file__,
    }


def _child(table: str, out: pathlib.Path, group_bytes: int, trace: bool) -> "dict[str, object]":
    """`run` in a process of its own, so its peak is that run's alone."""
    out.mkdir(parents=True, exist_ok=True)
    argv = [sys.executable, str(pathlib.Path(__file__).resolve()), "run", table or "-", str(out),
            "--group-bytes", str(group_bytes)] + (["--trace"] if trace else [])
    done = subprocess.run(argv, capture_output=True, text=True, check=True)
    found = json.loads(done.stdout.strip().splitlines()[-1])
    if found["exit"] != 0:
        raise SystemExit(f"synthtwin profile of {table} exited {found['exit']}")
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


def measure() -> "tuple[dict[str, object], dict[str, object]]":
    """K-S4-09's and K-S4-11's values."""
    from synthtwin import reading

    budget = reading.GROUP_BYTES
    memory: "dict[str, object]" = {"rows_traced": TRACED_ROWS, "sizes": list(SIZES)}
    seconds: "dict[str, object]" = {"sizes": list(SIZES)}
    with tempfile.TemporaryDirectory() as folder:
        work = pathlib.Path(folder)
        imports = _number(_child("", work / "imports", 0, False)["peak_rss_bytes"]) / MEBIBYTE
        memory["imports_mb"] = round(imports, 1)
        for kind in ("mixed", "gaussian"):
            table = work / f"{kind}.csv"
            write(kind, TRACED_ROWS, table)
            traced = _child(str(table), work / f"{kind}-traced", budget * TRACED_ROWS // BIG_ROWS, True)
            memory[f"{kind}_traced_bytes_a_cell"] = round(
                _number(traced["traced_peak_bytes"]) / (TRACED_ROWS * COLUMNS), 1
            )
            peaks: "list[float]" = []
            cpu: "list[float]" = []
            for rows in SIZES:
                write(kind, rows, table)
                found = _child(str(table), work / f"{kind}-{rows}", budget * rows // BIG_ROWS, False)
                peaks += [_number(found["peak_rss_bytes"]) / MEBIBYTE]
                cpu += [_number(found["cpu_seconds"])]
            table.unlink()
            growth, at = projected(list(SIZES), peaks, imports)
            memory[f"{kind}_describe_peak_mb"] = [round(peak, 1) for peak in peaks]
            memory[f"{kind}_describe_peak_growth_a_doubling"] = round(growth, 3)
            memory[f"{kind}_describe_peak_mb_2m_projected"] = round(at, 1)
            growth, at = projected(list(SIZES), cpu)
            seconds[f"{kind}_describe_cpu_seconds"] = cpu
            seconds[f"{kind}_describe_seconds_growth_a_doubling"] = round(growth, 3)
            seconds[f"{kind}_describe_seconds_2m_projected"] = round(at, 1)
    return memory, seconds


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", nargs="?", default="")
    parser.add_argument("rest", nargs="*")
    parser.add_argument("--kpi", action="store_true")
    parser.add_argument("--group-bytes", type=int, default=0)
    parser.add_argument("--trace", action="store_true")
    arguments = parser.parse_args()
    if arguments.action == "write":
        kind, rows, path = arguments.rest
        write(kind, int(rows), pathlib.Path(path))
        return 0
    if arguments.action == "run":
        table, out = arguments.rest
        found = run("" if table == "-" else table, pathlib.Path(out), arguments.group_bytes, arguments.trace)
        print(json.dumps(found))
        return 0
    if not arguments.kpi:
        print(__doc__)
        return 0
    kpi_rules.guard_this_tree()
    memory, seconds = measure()
    detail = "B0's two made-up tables, 50 columns, read in the groups 2,000,000 rows are read in"
    kpi_rules.emit("K-S4-09", memory, detail)
    kpi_rules.emit("K-S4-11", seconds, detail)
    return 0


if __name__ == "__main__":
    sys.exit(main())

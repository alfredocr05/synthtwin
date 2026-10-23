"""K-S4-09 and K-S4-11: `synthtwin profile` of the big table, one group of columns at a time.

PLAN P4-D400 (lane SR of the December plan). The owner's big table is
2,000,000 rows by 50 columns, and the process describing it must fit
under the 2.5 GB the watchdog lets one process hold. `synthtwin profile`
now reads a table too large for one group of columns
(`reading.GROUP_BYTES`, 256 MiB) one group at a time, so what it holds
grows with one group's columns and one column's description, not with
the whole table.

The two tables are lane B0's (planning-notes/work-2026-10/wave6/B0): the
made-up 50-column health table of K-S4-02 (`kpi_reader_memory`'s:
record numbers, codes, labels, numbers in their spellings, dates,
stamps, clocks and free texts, seed 20261002) and K-S1-06's Gaussian
columns at two places (`kpi_scale.write_numeric`, seed 20260913), at 50
columns. No value comes from a real table.

    kpi_describe_groups.py write {mixed|gaussian} ROWS PATH
    kpi_describe_groups.py run TABLE OUT_DIR [--group-bytes N] [--walk-bytes N] [--trace]
    kpi_describe_groups.py --kpi

`run` describes one table in THIS process with `synthtwin profile` and
prints one line of JSON: the CPU seconds, the process's peak resident
memory (`ru_maxrss`) and, with --trace, the most bytes `tracemalloc` saw
held. --group-bytes and --walk-bytes set `reading.GROUP_BYTES` and
`reading.WALK_BYTES`.

THE BIG TABLE'S GROUPS, AT EVERY SIZE MEASURED. A group holds as many
columns as `GROUP_BYTES` buys at the table's rows, and a walk as many
groups as `WALK_BYTES` buys, so 2,000,000 rows are read one column a
group and 100,000 rows at the same budgets in one group of fifty. Every
run below is read with both budgets scaled by the rows (times rows over
2,000,000), so each size is read in the groups and walks 2,000,000 rows
are read in, and what it holds grows with the rows as the big table's
does.

`--kpi` measures, each run in a process of its own, one at a time:

* K-S4-09's machine-free keys: each table of 200,000 rows by 50
  described once with `tracemalloc` on, the most bytes it saw held over
  the cells (`*_traced_bytes_a_cell`, judged everywhere: at 100,000,000
  cells, 25 bytes a cell is 2.5 GB);
* K-S4-09's machine keys and K-S4-11: the mixed table at 100,000,
  250,000, 500,000 and 1,000,000 rows, the Gaussian at 100,000, 250,000
  and 500,000, their peak resident memory and CPU seconds, and the
  projection to 2,000,000 rows as lane B0 makes it -- a least-squares
  line through log(rows) and log(value) over the THREE LARGEST sizes,
  read at 2,000,000; memory as its rise above what the process holds
  once synthtwin is imported, measured here and added back; never
  linear unless the growth measured is x2.00. Beside it, the projection
  at the largest doubling's own rate (`*_top_doubling`), recorded. Peaks
  and seconds are the machine's and are judged only on the quiet
  reference machine (`kpi_rules.MACHINE_KINDS`).

SKEPTIC 1 OF LANE SR (items 2 and 6): the mixed table is measured at
1,000,000 rows too, so its projection rests on the three largest sizes
and not on the curvature the 100,000 point lends it; and each Gaussian
size is the LARGEST peak of three hash seeds (`HASH_SEEDS`), because the
allocator keeps what pandas' C reader freed on some seeds and not on
others (183 against 531 MB on one file at 250,000 rows), which made a
series that fell from 250,000 to 500,000 rows. THE TRIPWIRE SKEPTIC OF
LANE SR (item 2): the mixed table, the one K-S4-09 judges, is held to
the same rule -- three seeds, never PYTHONHASHSEED=0, which no person
runs -- so its projection is not low by the same allocator effect; its
leg takes about three times as long. CODEX'S REVIEW (item 6):
where resident memory cannot be read (no `resource`, as on Windows), the
memory keys are left out and the evidence says so; CPU seconds and the
traced bytes are kept.

About six hours on the reference machine: run it in a NIGHT window,
one heavy process at a time, the watchdog running.
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
SIZES = {"mixed": (100_000, 250_000, 500_000, 1_000_000), "gaussian": (100_000, 250_000, 500_000)}
HASH_SEEDS = {"mixed": ("1", "2", "3"), "gaussian": ("1", "2", "3")}
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
    """The process's peak resident memory so far, in bytes, or -1 where it cannot be read (`measure` then records none)."""
    try:
        import resource
    except ImportError:
        return -1
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # ru_maxrss is in bytes on macOS and in kilobytes on Linux.
    return peak if sys.platform == "darwin" else peak * 1024


def run(table: str, out: pathlib.Path, group_bytes: int, trace: bool, walk_bytes: int = 0) -> "dict[str, object]":
    """Describe ``table`` with `synthtwin profile` in this process; what it took. An empty table imports only."""
    from synthtwin import cli, reading
    import synthtwin

    if not table:
        return {"exit": 0, "cpu_seconds": 0.0, "peak_rss_bytes": _resident_peak(), "synthtwin": synthtwin.__file__}
    if group_bytes > 0:
        reading.GROUP_BYTES = group_bytes
    if walk_bytes > 0:
        reading.WALK_BYTES = walk_bytes
    if trace:
        tracemalloc.start()
    said = io.StringIO()
    started = time.process_time()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(["profile", table, "--out-dir", str(out), "--replace"], table_floor=False)
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
        "walk_bytes": reading.WALK_BYTES,
        "synthtwin": synthtwin.__file__,
    }


def _child(table: str, out: pathlib.Path, group_bytes: int, trace: bool, seed: str = "0") -> "dict[str, object]":
    """`run` in a process of its own, so its peak is that run's alone, under hash seed ``seed``."""
    import os

    out.mkdir(parents=True, exist_ok=True)
    from synthtwin import reading

    walk_bytes = reading.WALK_BYTES * group_bytes // reading.GROUP_BYTES if group_bytes > 0 else 0
    argv = [sys.executable, str(pathlib.Path(__file__).resolve()), "run", table or "-", str(out),
            "--group-bytes", str(group_bytes), "--walk-bytes", str(walk_bytes)] + (["--trace"] if trace else [])
    done = subprocess.run(argv, capture_output=True, text=True, check=True, env=dict(os.environ, PYTHONHASHSEED=seed))
    found = json.loads(done.stdout.strip().splitlines()[-1])
    if found["exit"] != 0:
        raise SystemExit(f"synthtwin profile of {table} exited {found['exit']}")
    return found


def _number(value: object) -> float:
    """A measured number, read back from a run's JSON."""
    return float(f"{value}")


def top_doubling(sizes: "list[int]", values: "list[float]", base: float = 0.0) -> float:
    """The value at 2,000,000 rows at the rate the two largest sizes grew by, above ``base``."""
    rate = math.log(max(values[-1] - base, 1e-9) / max(values[-2] - base, 1e-9)) / math.log(sizes[-1] / sizes[-2])
    return (values[-1] - base) * (BIG_ROWS / sizes[-1]) ** rate + base


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
    memory: "dict[str, object]" = {"rows_traced": TRACED_ROWS, "sizes": dict(SIZES), "hash_seeds": dict(HASH_SEEDS)}
    seconds: "dict[str, object]" = {"sizes": dict(SIZES)}
    with tempfile.TemporaryDirectory() as folder:
        work = pathlib.Path(folder)
        imports_peak = _number(_child("", work / "imports", 0, False)["peak_rss_bytes"])
        resident = imports_peak >= 0
        imports = imports_peak / MEBIBYTE
        if resident:
            memory["imports_mb"] = round(imports, 1)
        else:
            memory["resident_memory"] = "unavailable on this platform: no peak recorded"
        for kind in ("mixed", "gaussian"):
            table = work / f"{kind}.csv"
            write(kind, TRACED_ROWS, table)
            traced = _child(str(table), work / f"{kind}-traced", budget * TRACED_ROWS // BIG_ROWS, True)
            memory[f"{kind}_traced_bytes_a_cell"] = round(
                _number(traced["traced_peak_bytes"]) / (TRACED_ROWS * COLUMNS), 1
            )
            sizes = list(SIZES[kind])
            peaks: "list[float]" = []
            cpu: "list[float]" = []
            for rows in sizes:
                write(kind, rows, table)
                most = -1.0
                spent = 0.0
                for seed in HASH_SEEDS[kind]:
                    found = _child(str(table), work / f"{kind}-{rows}-{seed}", budget * rows // BIG_ROWS, False, seed)
                    most = max(most, _number(found["peak_rss_bytes"]) / MEBIBYTE)
                    spent = max(spent, _number(found["cpu_seconds"]))
                peaks += [most]
                cpu += [spent]
            table.unlink()
            top = sizes[-3:]
            if resident:
                growth, at = projected(top, peaks[-3:], imports)
                memory[f"{kind}_describe_peak_mb"] = [round(peak, 1) for peak in peaks]
                memory[f"{kind}_describe_peak_growth_a_doubling"] = round(growth, 3)
                memory[f"{kind}_describe_peak_mb_2m_projected"] = round(at, 1)
                memory[f"{kind}_describe_peak_mb_2m_top_doubling"] = round(top_doubling(sizes, peaks, imports), 1)
            growth, at = projected(top, cpu[-3:])
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
    parser.add_argument("--walk-bytes", type=int, default=0)
    parser.add_argument("--trace", action="store_true")
    arguments = parser.parse_args()
    if arguments.action == "write":
        kind, rows, path = arguments.rest
        write(kind, int(rows), pathlib.Path(path))
        return 0
    if arguments.action == "run":
        table, out = arguments.rest
        found = run("" if table == "-" else table, pathlib.Path(out), arguments.group_bytes, arguments.trace, arguments.walk_bytes)
        print(json.dumps(found))
        return 0
    if not arguments.kpi:
        print(__doc__)
        return 0
    kpi_rules.guard_this_tree()
    memory, seconds = measure()
    detail = "B0's two made-up tables, 50 columns, read in the groups 2,000,000 rows are read in, projected from the three largest sizes"
    kpi_rules.emit("K-S4-09", memory, detail)
    kpi_rules.emit("K-S4-11", seconds, detail)
    return 0


if __name__ == "__main__":
    sys.exit(main())

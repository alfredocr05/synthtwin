"""K-S4-09 and K-S4-11: `synthtwin profile` of a big table, one group of columns at a time.

PLAN P4-D400 (lane SR of the December plan). The owner's big table is
2,000,000 rows by 50 columns, and the process describing it must fit
under the 2.5 GB the watchdog lets one process hold. `synthtwin profile`
now reads a table too large for one group of columns
(`reading.GROUP_BYTES`) one group at a time, so what it holds grows with
one group's columns and one column's description, not the whole table.

The two tables are B0's (planning-notes/work-2026-10/wave6/B0): the
made-up 50-column health table of K-S4-02 (`kpi_reader_memory`'s,
record numbers, codes, labels, numbers in their spellings, dates,
stamps, clocks and free texts, seed 20261002) and K-S1-06's Gaussian
columns at two places (`kpi_scale.write_numeric`, seed 20260913), at
50 columns. No value comes from a real table.

    kpi_describe_groups.py write {mixed|gaussian} ROWS PATH
    kpi_describe_groups.py run TABLE OUT_DIR [--group-bytes N] [--trace]
    kpi_describe_groups.py --kpi [--rows N]

`run` describes one table in THIS process with `synthtwin profile` and
prints one line of JSON: the CPU seconds, the process's peak resident
memory (`ru_maxrss`, machine-decided) and, with --trace, the most bytes
`tracemalloc` saw held (machine-free). --group-bytes sets
`reading.GROUP_BYTES`, so a smaller table is read in the groups a larger
one would be: 2,000,000 rows at the default budget are read about three
columns a group, and 200,000 rows at a tenth of it are too.

`--kpi` is K-S4-09's machine-free part: each table of 200,000 rows by
50 (`--rows`) described twice in processes of their own -- read whole,
as before this lane, and in the groups 2,000,000 rows would be read in
-- with the bytes `tracemalloc` saw held divided by the cells. Its
memory peaks and seconds at 100,000, 250,000 and 500,000 rows, and the
projection to 2,000,000, are measured in a measurement window (one heavy
process at a time, the suite slot held) by `run`, and recorded in the
ledger's evidence: they are the machine's.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
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

# The rows of the machine-free measure, and of the owner's big table.
ROWS = 200_000
BIG_ROWS = 2_000_000
COLUMNS = 50


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


def run(table: pathlib.Path, out: pathlib.Path, group_bytes: int, trace: bool) -> "dict[str, object]":
    """Describe ``table`` with `synthtwin profile` in this process; what it took."""
    from synthtwin import cli, reading
    import synthtwin

    if group_bytes > 0:
        reading.GROUP_BYTES = group_bytes
    if trace:
        tracemalloc.start()
    said = io.StringIO()
    started = time.process_time()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(["profile", str(table), "--out-dir", str(out), "--replace"])
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


def _child(table: pathlib.Path, out: pathlib.Path, group_bytes: int, trace: bool) -> "dict[str, object]":
    """`run` in a process of its own, so its peak is that run's alone."""
    argv = [sys.executable, str(pathlib.Path(__file__).resolve()), "run", str(table), str(out),
            "--group-bytes", str(group_bytes)] + (["--trace"] if trace else [])
    done = subprocess.run(argv, capture_output=True, text=True, check=True)
    return json.loads(done.stdout.strip().splitlines()[-1])


def measure(rows: int) -> "dict[str, float | int]":
    """K-S4-09's machine-free keys: traced bytes a cell, read whole and in the big table's groups."""
    found: "dict[str, float | int]" = {"rows": rows}
    with tempfile.TemporaryDirectory() as folder:
        for kind in ("mixed", "gaussian"):
            table = pathlib.Path(folder) / f"{kind}.csv"
            write(kind, rows, table)
            cells = rows * COLUMNS
            # Read whole: a budget no table of this size reaches.
            whole = _child(table, pathlib.Path(folder) / f"{kind}-whole", 1 << 40, True)
            # Read in the groups the big table is read in: the budget scaled
            # by the rows, so a group holds as many columns as it would
            # there.
            scaled = 512 * 1024 * 1024 * rows // BIG_ROWS
            grouped = _child(table, pathlib.Path(folder) / f"{kind}-groups", scaled, True)
            if whole["exit"] != 0 or grouped["exit"] != 0:
                raise SystemExit(f"synthtwin profile of the {kind} table exited {whole['exit']} and {grouped['exit']}")
            whole_bytes = float(f"{whole['traced_peak_bytes']}")
            grouped_bytes = float(f"{grouped['traced_peak_bytes']}")
            found[f"{kind}_traced_bytes_a_cell_whole"] = round(whole_bytes / cells, 1)
            found[f"{kind}_traced_bytes_a_cell_in_groups"] = round(grouped_bytes / cells, 1)
            found[f"{kind}_in_groups_over_whole"] = round(grouped_bytes / whole_bytes, 3)
            table.unlink()
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", nargs="?", default="")
    parser.add_argument("rest", nargs="*")
    parser.add_argument("--kpi", action="store_true")
    parser.add_argument("--rows", type=int, default=ROWS)
    parser.add_argument("--group-bytes", type=int, default=0)
    parser.add_argument("--trace", action="store_true")
    arguments = parser.parse_args()
    if arguments.action == "write":
        kind, rows, path = arguments.rest
        write(kind, int(rows), pathlib.Path(path))
        return 0
    if arguments.action == "run":
        table, out = arguments.rest
        print(json.dumps(run(pathlib.Path(table), pathlib.Path(out), arguments.group_bytes, arguments.trace)))
        return 0
    if not arguments.kpi:
        print(__doc__)
        return 0
    kpi_rules.guard_this_tree()
    found = measure(arguments.rows)
    kpi_rules.emit("K-S4-09", found, f"{found['rows']:,} rows by 50 columns of B0's two made-up tables")
    return 0


if __name__ == "__main__":
    sys.exit(main())

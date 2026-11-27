"""K-S4-17: generating one padded code column, projected to two million rows (lane H1, plan P4-D402).

    .venv/bin/python tools/measurements/kpi_padded_generate.py --kpi [--rows 100000 250000 500000]

The postal-code column of the made-up mixed table
(`kpi_reader_memory.table_lines`, the column `post_code`: five-figure
codes, some written with leading zeros, so its description publishes
`pad_widths` and its twin goes through the padded exchange) is written
alone at each size, described once, and generated once at seed 0. The
seconds are the process CPU of `contract.load_profile` and
`generation.generate`, the phase lane B0's cost table times as
"generate". Printed: those seconds at each size, the growth a doubling
fitted through them (two to the slope of the least-squares line of log
seconds on log rows, B0's fit), and the seconds at 2,000,000 rows
projected from the largest size at that growth.

Every number here is the machine's as much as the code's: the projection
is judged only in a measurement window on the quiet reference machine
(one heavy process, the suite slot held, the load under the ledger's
bound), and recorded everywhere else. On 68dae22f, before lane H1, B0's
window measured 16.0, 84.4 and 269.3 s at 100,000, 250,000 and 500,000
rows, about 3,630 s at two million on its a-n-squared-plus-b-n fit.
Three sizes take about five minutes and under 500 MB.
"""

import argparse
import csv
import io
import math
import pathlib
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tools" / "measurements"))
import kpi_reader_memory  # noqa: E402
import kpi_rules  # noqa: E402
import kpi_shapes  # noqa: E402
from synthtwin import contract, generation  # noqa: E402

COLUMN = "post_code"
TARGET_ROWS = 2_000_000


def write_column(path, rows):
    """The mixed table's postal-code column alone, ``rows`` rows, as lane B0's tables.py writes it."""
    lines = kpi_reader_memory.table_lines(rows)
    header = next(lines).split(",")
    place = header.index(COLUMN)
    with path.open("w", encoding="utf-8", newline="") as sink:
        sink.write(COLUMN + "\n")
        for line in lines:
            cell = next(csv.reader(io.StringIO(line)))[place]
            sink.write((f'"{cell}"' if "," in cell else cell) + "\n")


def growth_per_doubling(seconds):
    """Two to the slope of the least-squares line through (log2 rows, log2 seconds)."""
    points = [(math.log2(rows), math.log2(taken)) for rows, taken in sorted(seconds.items())]
    mean_x = sum(x for x, _y in points) / len(points)
    mean_y = sum(y for _x, y in points) / len(points)
    slope = sum((x - mean_x) * (y - mean_y) for x, y in points) / sum((x - mean_x) ** 2 for x, _y in points)
    return 2.0 ** slope


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kpi", action="store_true")
    parser.add_argument("--rows", type=int, nargs="+", default=[100_000, 250_000, 500_000])
    args = parser.parse_args()
    kpi_rules.guard_this_tree()
    seconds = {}
    with tempfile.TemporaryDirectory() as folder:
        home = pathlib.Path(folder)
        for rows in sorted(args.rows):
            source = home / f"{COLUMN}-{rows}.csv"
            write_column(source, rows)
            code = kpi_shapes.quiet_cli(["profile", str(source), "--out-dir", str(home), "--replace"])
            assert code == 0, code
            started = time.process_time()
            loaded = contract.load_profile(str(home / f"{COLUMN}-{rows}-profile.json"))
            twin = generation.generate(loaded, 0)
            seconds[rows] = time.process_time() - started
            del twin, loaded
            print(f"{COLUMN} {rows} rows: generate {seconds[rows]:.1f} s of CPU", flush=True)
    growth = growth_per_doubling(seconds)
    largest = max(seconds)
    projected = seconds[largest] * growth ** math.log2(TARGET_ROWS / largest)
    print(f"growth x{growth:.2f} a doubling; {projected:.0f} s projected at {TARGET_ROWS} rows", flush=True)
    if args.kpi:
        value = {f"generate_seconds_{rows}_rows": round(taken, 1) for rows, taken in seconds.items()}
        value["generate_growth_per_doubling"] = round(growth, 3)
        value["projected_generate_seconds_2000000_rows"] = round(projected, 1)
        kpi_rules.emit("K-S4-17", value)


if __name__ == "__main__":
    main()

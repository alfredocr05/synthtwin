"""K-S1-05 and K-S1-06: describing and generating large tables end to end.

    .venv/bin/python tools/measurements/kpi_scale.py labels2 --kpi
    .venv/bin/python tools/measurements/kpi_scale.py numeric --kpi [--rows N --cols C --repeats R]

`labels2` (K-S1-05): two label columns, 50,000 and 200,000 rows, each
described three times, the sizes taken in turn; the median seconds
`profile` takes at 200,000 (judged on a quiet reference machine only)
and the ratio of the two medians, machine-free. A few minutes.

`numeric` (K-S1-06, OPEN until landing 4): N rows (default 100,000) of C
Gaussian columns (default 20) described and generated end to end, and
the same at N/4 rows, each size R times (default 3), the sizes taken in
turn so that a change in the machine's load falls on both. Printed: the
median seconds at N (judged on a quiet reference machine only), the
ratio of the medians at N and N/4 -- machine-free, the part that can fail
anywhere -- and the microseconds per cell. About an hour under load.
`--rows 2000000 --cols 50` is the landing-4 gate itself, MEASURED and
never projected; it runs for hours, so it is asked for by name, with
`--repeats 1` if one sample is all the time allows (the printed value
then says repeats 1).
"""

import argparse
import pathlib
import random
import statistics
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402
import kpi_shapes  # noqa: E402


def write_labels(path, rows):
    draw = random.Random(20260913)
    sites = ["north", "south", "east", "west", "central"]
    grades = ["low", "mid", "high"]
    with path.open("w", encoding="utf-8", newline="") as out:
        out.write("site,grade\n")
        for _ in range(rows):
            out.write(f"{draw.choice(sites)},{draw.choice(grades)}\n")


def write_numeric(path, rows, cols):
    draw = random.Random(20260913)
    with path.open("w", encoding="utf-8", newline="") as out:
        out.write(",".join(f"m{c:02d}" for c in range(cols)) + "\n")
        for _ in range(rows):
            out.write(",".join(f"{draw.gauss(50 + c, 5 + c % 7):.2f}" for c in range(cols)) + "\n")


def timed(argv):
    started = time.perf_counter()
    code = kpi_shapes.quiet_cli(argv)
    return code, time.perf_counter() - started


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("shape", choices=["labels2", "numeric"])
    parser.add_argument("--kpi", action="store_true")
    parser.add_argument("--rows", type=int, default=100_000)
    parser.add_argument("--cols", type=int, default=20)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    kpi_rules.guard_this_tree()
    with tempfile.TemporaryDirectory() as folder:
        home = pathlib.Path(folder)
        if args.shape == "labels2":
            samples = {50_000: [], 200_000: []}
            for rows in samples:
                write_labels(home / f"labels2-{rows}.csv", rows)
            for repeat in range(3):
                for rows in samples:
                    source = home / f"labels2-{rows}.csv"
                    code, taken = timed(["profile", str(source), "--out-dir", str(home),
                                         "--replace"])
                    assert code == 0, code
                    samples[rows] += [taken]
                    print(f"labels2 {rows} rows, repeat {repeat + 1}: profile {taken:.1f} s",
                          flush=True)
            seconds = {rows: statistics.median(taken) for rows, taken in samples.items()}
            kpi_rules.emit("K-S1-05", {
                "profile_seconds_200k": round(seconds[200_000], 1),
                "profile_ratio_4x_rows": round(seconds[200_000] / seconds[50_000], 2)})
            return
        sizes = (args.rows // 4, args.rows)
        totals = {rows: [] for rows in sizes}
        for rows in sizes:
            write_numeric(home / f"numeric-{rows}.csv", rows, args.cols)
        for repeat in range(args.repeats):
            for rows in sizes:
                here = home / f"out-{rows}"
                here.mkdir(exist_ok=True)
                source = home / f"numeric-{rows}.csv"
                code, profile_s = timed(["profile", str(source), "--out-dir", str(here),
                                         "--replace"])
                assert code == 0, code
                code, generate_s = timed(["generate", str(here / f"numeric-{rows}-profile.json"),
                                          "--out-dir", str(here), "--seed", "0", "--replace"])
                assert code == 0, code
                totals[rows] += [profile_s + generate_s]
                print(f"numeric {rows} x {args.cols}, repeat {repeat + 1}: describe "
                      f"{profile_s:.1f} s, generate {generate_s:.1f} s", flush=True)
        small, large = (statistics.median(totals[rows]) for rows in sizes)
        cells = args.rows * args.cols
        print(f"numeric {args.rows} x {args.cols}: median {large:.1f} s end to end, "
              f"{1e6 * large / cells:.1f} microseconds per cell; {sizes[0]} rows: median "
              f"{small:.1f} s; ratio {large / small:.2f} over {args.repeats} repeat(s)",
              flush=True)
        if (args.rows, args.cols) == (100_000, 20):
            key = "seconds_100k_x20"
        elif (args.rows, args.cols) == (2_000_000, 50):
            key = "seconds_2m_x50"
        else:
            key = f"seconds_{args.rows}_x{args.cols}"
        kpi_rules.emit("K-S1-06", {key: round(large, 1),
                                   "ratio_4x_rows": round(large / small, 2),
                                   "repeats": args.repeats,
                                   "microseconds_per_cell": round(1e6 * large / cells, 1)})


if __name__ == "__main__":
    main()

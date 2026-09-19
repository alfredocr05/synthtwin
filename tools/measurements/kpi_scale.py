"""K-S1-05 and K-S1-06: describing and generating large tables end to end.

    .venv/bin/python tools/measurements/kpi_scale.py labels2 --kpi
    .venv/bin/python tools/measurements/kpi_scale.py numeric --kpi [--rows N --cols C]

`labels2` (K-S1-05): two label columns, 50,000 and 200,000 rows; the
seconds `profile` takes at 200,000 (reference machine only) and the
50k-to-200k ratio, machine-free. About a minute.

`numeric` (K-S1-06, OPEN until landing 4): 100,000 rows of 20 Gaussian
columns described and generated end to end, the seconds printed and the
microseconds per cell beside them. About seven minutes. `--rows 2000000
--cols 50` is the landing-4 gate itself, MEASURED and never projected;
it runs for hours, so it is asked for by name and never run by default.
"""

import argparse
import pathlib
import random
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
    args = parser.parse_args()
    kpi_rules.guard_this_tree()
    with tempfile.TemporaryDirectory() as folder:
        home = pathlib.Path(folder)
        if args.shape == "labels2":
            seconds = {}
            for rows in (50_000, 200_000):
                source = home / f"labels2-{rows}.csv"
                write_labels(source, rows)
                code, seconds[rows] = timed(["profile", str(source), "--out-dir", str(home)])
                assert code == 0, code
                print(f"labels2 {rows} rows: profile {seconds[rows]:.1f} s", flush=True)
            kpi_rules.emit("K-S1-05", {
                "profile_seconds_200k": round(seconds[200_000], 1),
                "profile_ratio_4x_rows": round(seconds[200_000] / seconds[50_000], 2)})
            return
        source = home / "numeric.csv"
        write_numeric(source, args.rows, args.cols)
        code, profile_s = timed(["profile", str(source), "--out-dir", str(home)])
        assert code == 0, code
        code, generate_s = timed(["generate", str(home / "numeric-profile.json"),
                                  "--out-dir", str(home), "--seed", "0"])
        assert code == 0, code
        total = profile_s + generate_s
        cells = args.rows * args.cols
        print(f"numeric {args.rows} x {args.cols}: describe {profile_s:.1f} s, generate "
              f"{generate_s:.1f} s, {1e6 * total / cells:.1f} microseconds per cell", flush=True)
        if (args.rows, args.cols) == (100_000, 20):
            key = "seconds_100k_x20"
        elif (args.rows, args.cols) == (2_000_000, 50):
            key = "seconds_2m_x50"
        else:
            key = f"seconds_{args.rows}_x{args.cols}"
        kpi_rules.emit("K-S1-06", {key: round(total, 1),
                                   "microseconds_per_cell": round(1e6 * total / cells, 1)})


if __name__ == "__main__":
    main()

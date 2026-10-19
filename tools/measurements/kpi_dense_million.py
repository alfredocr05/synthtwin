"""K-S4-21: G2's dense tail at 1,000,000 rows, described, generated and validated (stage 4 lane G2T, plan P4-D405).

Whole numbers from 5 to 999999 beside five at `999999 + 1,560,000 + j`,
declared a measurement, at a floor of eleven: the shape of Codex's review
of lane G2, item 3 (`tests/test_stage4_million_rows.py`'s `_dense_tail`).
On 36ad3061 the twin missed the column's mean, skew and kurtosis because
G12.3's windows, drawn through the staircase, did not reach the published
values (lane S4c's measurement: the mean's window 500,051.9 to 500,061.4
around a published 500,012.3, the twin at 500,013.3). Printed: the
obligations `validate` MISSED among the moments and the tails' distances,
and the twin's four moments and its high tail's two distances off the
published ones, in parts per million of the published spread (the mean)
or of the published value (the rest). Machine-free counts and ratios.

Run it only in a measurement window: about ten minutes, near 1 GB at its
peak, one process at a time (`generate` 221 s and 851 MB, `validate`
181 s on lane S4c's head).
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()

ROWS = 1000000


def _run(arguments: "list[str]") -> int:
    return subprocess.run(
        [sys.executable, "-m", "synthtwin"] + arguments,
        env={"PYTHONPATH": str(ROOT / "src"), "PYTHONHASHSEED": "0", "PATH": "/usr/bin:/bin"},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode


def _moments(values: "list[float]") -> "tuple[float, float, float, float]":
    count = len(values)
    mean = math.fsum(values) / count
    squares = math.fsum([(value - mean) ** 2 for value in values])
    spread = math.sqrt(squares / (count - 1))
    population = math.sqrt(squares / count)
    skew = math.fsum([((value - mean) / population) ** 3 for value in values]) / count
    kurtosis = math.fsum([((value - mean) / population) ** 4 for value in values]) / count
    return mean, spread, skew, kurtosis


def measure(folder: pathlib.Path) -> "dict[str, float]":
    table = folder / "dense.csv"
    with table.open("w", encoding="utf-8", newline="\n") as sink:
        sink.write("value\n")
        for value in range(1000005 - ROWS, 1000000):
            sink.write(f"{value}\n")
        for step in range(5):
            sink.write(f"{999999 + (ROWS * 156) // 100 + step}\n")
    assert _run(["profile", str(table), "--measurement", "value", "--smallest-group", "11", "--out-dir", str(folder), "--replace"]) == 0
    described = folder / "dense-profile.json"
    assert _run(["generate", str(described), "--out-dir", str(folder), "--seed", "0", "--replace"]) == 0
    (folder / "v").mkdir()
    code = _run(["validate", str(described), "--twin", str(folder / "dense-twin.csv"), "--out-dir", str(folder / "v"), "--replace"])
    assert code in (0, 3), code
    report = next((folder / "v").glob("*.txt")).read_text(encoding="utf-8")
    named: "set[str]" = set()
    for line in report.splitlines():
        stripped = line.strip()
        if stripped.endswith(": MISSED") and stripped.startswith(("moments.", "tails.")):
            named.add(stripped)
    missed = len(named)
    column = json.loads(described.read_text(encoding="utf-8"))["columns"][0]
    values: "list[float]" = []
    with (folder / "dense-twin.csv").open(encoding="utf-8") as source:
        next(source)
        for line in source:
            values += [float(line)]
    mean, spread, skew, kurtosis = _moments(values)
    high = column["tails"]["high"]
    boundary = column["percentiles"]["p99"]
    kept = sorted(values)[len(values) - high["rows"]:]
    distances = [value - boundary for value in kept]
    tail_mean = math.fsum(distances) / len(distances)
    tail_root = math.sqrt(math.fsum([one * one for one in distances]) / len(distances))
    return {
        "moment_and_tail_misses_1m": missed,
        "validate_exit_1m": code,
        "mean_off_ppm_of_spread": round(abs(mean - column["mean"]) / column["std"] * 1e6, 1),
        "std_off_ppm": round(abs(spread / column["std"] - 1.0) * 1e6, 1),
        "skew_off_ppm": round(abs(skew / column["skew"] - 1.0) * 1e6, 1),
        "kurtosis_off_ppm": round(abs(kurtosis / column["kurtosis"] - 1.0) * 1e6, 1),
        "tail_mean_distance_off_ppm": round(abs(tail_mean / high["mean_distance"] - 1.0) * 1e6, 1),
        "tail_rms_distance_off_ppm": round(abs(tail_root / high["rms_distance"] - 1.0) * 1e6, 1),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kpi", action="store_true")
    arguments = parser.parse_args()
    with tempfile.TemporaryDirectory() as folder:
        found = measure(pathlib.Path(folder))
    if arguments.kpi:
        kpi_rules.emit("K-S4-21", found)
    else:
        print(json.dumps(found, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()

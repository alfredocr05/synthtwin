"""K-P3-03, K-P3-12 and K-S1-01: twenty plain numeric columns at 5,000 and 20,000 rows.

The stage-1 shape (`numeric20`, Random(20260913), each column Gaussian
at two decimals) described, generated and validated through the command
line, in this process, at both sizes. Printed per size: the seconds each
command took and the obligations the twin's quality report MISSED.

- K-P3-03 (GREEN since stage 3's numeric tail): MISSED obligations at
  each size, read from the validator's census, and the twin's spread
  against the published one, per cent either way, the widest and the
  narrowest of the twenty columns at each size (`taxonomy.spread_of` of
  the twin's cells over the description's `std`). Method G5.3's straight
  outer segment to the exact published extreme held that spread too
  wide -- 19 MISSED on the frozen copy, 10 on e53d5f4 and on caf3079,
  all `moments.std` -- and the tail rule of contract 6.7a withdraws the
  extreme, so nothing is missed at either size now. The entry's bound is
  the merged tree's own measurement on the widest and the target's floor
  on the narrowest; the ledger says why.
- K-P3-12: validate seconds at 20,000 (reference machine only) and the
  5k-to-20k ratio, which is machine-free.
- K-S1-01: generate seconds at 20,000 (reference machine only) and the
  5k-to-20k ratio.

Each ratio is the median of three runs at 20,000 rows over the median of
three at 5,000 (generate and validate each run three times at each
size, the same seed, so the MISSED count is the same every time); the
small size takes well over a second, so scheduler noise cannot move it
past its bound. About fifteen minutes on the reference machine under
load.

    .venv/bin/python tools/measurements/kpi_numeric_20k.py --kpi
"""

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
import csv  # noqa: E402

from synthtwin import contract, taxonomy, validation  # noqa: E402

kpi_rules.guard_this_tree()


def table(rows):
    draw = random.Random(20260913)
    head = [f"m{c:02d}" for c in range(20)]
    lines = [",".join(head)]
    for _ in range(rows):
        lines += [",".join(f"{draw.gauss(50 + c, 5 + c % 7):.2f}" for c in range(20))]
    return "\n".join(lines) + "\n"


def timed(argv):
    started = time.perf_counter()
    code = kpi_shapes.quiet_cli(argv)
    return code, time.perf_counter() - started


def spread_excess(description, twin):
    """Per column, the twin's spread over the published one, less one, in per cent."""
    loaded = contract.load_profile(str(description))
    with open(twin, encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    excess = []
    for index, column in enumerate(loaded.columns):
        published = getattr(column.facts, "std", None)
        spread = taxonomy.spread_of([float(row[index]) for row in rows[1:] if row[index]])
        if published and spread is not None:
            excess += [(spread / published - 1) * 100]
    return round(max(excess), 2), round(min(excess), 2)


def missed_in(description, twin):
    """The census's MISSED count, by the validator the command itself runs."""
    loaded = contract.load_profile(str(description))
    return validation.measure(loaded, str(twin)).census.missed


found = {}
with tempfile.TemporaryDirectory() as folder:
    home = pathlib.Path(folder)
    for rows in (5000, 20000):
        here = home / f"n{rows}"
        here.mkdir()
        source = here / "numeric20.csv"
        source.write_text(table(rows), encoding="utf-8")
        code, profile_s = timed(["profile", str(source), "--out-dir", str(here)])
        assert code == 0, code
        description = here / "numeric20-profile.json"
        generate_s, validate_s, exits = [], [], []
        missed = None
        for repeat in range(3):
            code, seconds = timed(["generate", str(description), "--out-dir", str(here),
                                   "--seed", "0", "--replace"])
            generate_s += [seconds]
            report = here / f"v{repeat}"
            report.mkdir()
            code, seconds = timed(["validate", str(description), "--twin",
                                   str(here / "numeric20-twin.csv"), "--out-dir", str(report)])
            validate_s += [seconds]
            exits += [code]
            missed = missed_in(description, here / "numeric20-twin.csv")
        widest, narrowest = spread_excess(description, here / "numeric20-twin.csv")
        found[rows] = dict(profile=profile_s, generate=statistics.median(generate_s),
                           validate=statistics.median(validate_s), missed=missed, exits=exits,
                           widest=widest, narrowest=narrowest)
        print(rows, {k: (round(v, 2) if isinstance(v, float) else v) for k, v in found[rows].items()},
              flush=True)

small, large = found[5000], found[20000]
kpi_rules.emit("K-P3-03", {
    "missed_5k": small["missed"], "missed_20k": large["missed"],
    "spread_widest_pct_5k": small["widest"], "spread_narrowest_pct_5k": small["narrowest"],
    "spread_widest_pct_20k": large["widest"], "spread_narrowest_pct_20k": large["narrowest"]})
kpi_rules.emit("K-P3-12", {
    "validate_seconds_20k": round(large["validate"], 1),
    "validate_ratio_4x_rows": round(large["validate"] / small["validate"], 2)})
kpi_rules.emit("K-S1-01", {
    "generate_seconds_20k": round(large["generate"], 1),
    "generate_ratio_4x_rows": round(large["generate"] / small["generate"], 2),
    "profile_seconds_20k": round(large["profile"], 1)})

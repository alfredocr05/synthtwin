"""K-S3-38: time of day comes back -- the hour census of a column of moments.

LANDING 3b.2-H (lane T2, plan P4-D371). A column of moments read on its
own clock publishes how many cells of its body fall on each hour of the
written clock, in groups the one merge rule chooses, and the twin meets
it (method G7.3g).

K-S3-38, over the gate's own battery (`tests/test_stage3b_hour.py`) -- its
1,000-row table of eleven columns (vitals on four-hourly rounds with
the count at midnight published, weekday appointments, admissions, arrivals, a
clinic, discharges, rule 4's witness and four spans of 1, 3, 7 and 14
days, the first three of which publish no census) and its 10,000-row
table (the 10-week clinic, a burst, every cell on the hour and a
half-hour grid) -- a lab panel of 2,000 results on 1 to 25 rows an
instant and 3,021 OR starts, ten rooms at 07:30 on 100 weekdays, at a
floor of eleven and seeds 0 to 4:

* `censuses`: the columns that publish a census;
* `missed`: checkable obligations MISSED on every twin and on every real
  table;
* `over_bound`, `over_cap`, `shape`: the gate's statistics clauses
  (`_statistics_failures`), the twin's hour TVD against the real
  column's;
* `weekday_changed`, `distinct_changed`: twins whose weekdays, or whose
  count of different values, differ from the same seed's with the hour
  pass withdrawn;
* `cases`: how many statistics were judged, one a twin a column.

    .venv/bin/python tools/measurements/kpi_hour_census.py --kpi
"""

import datetime
import pathlib
import random
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))
import kpi_rules  # noqa: E402
import kpi_shapes  # noqa: E402
import test_stage3b_hour as gate  # noqa: E402
from synthtwin import generation  # noqa: E402

kpi_rules.guard_this_tree()

SEEDS = (0, 1, 2, 3, 4)


def _tables() -> "list[tuple[str, dict[str, tuple[list[str], str]]]]":
    panel = gate._panel(random.Random(71004), 2000)
    return [
        ("thousand", gate._thousand()),
        ("ten-thousand", gate._ten_thousand()),
        ("panel", {"drawn_at": (panel, gate._ISO_S)}),
        ("or-starts", gate._or_starts()),
    ]


def _weekdays(cells: "list[str]", form: str) -> "list[int]":
    return sorted(datetime.datetime.strptime(cell, form).weekday() for cell in cells if cell)


def battery(home: pathlib.Path) -> "tuple[dict[str, int], list[str]]":
    totals = {
        "censuses": 0, "missed": 0, "over_bound": 0, "over_cap": 0, "shape": 0,
        "weekday_changed": 0, "distinct_changed": 0, "cases": 0,
    }
    notes: "list[str]" = []
    keep = generation._hour_settled
    for shape, columns in _tables():
        text = gate._table_text(columns)
        described = kpi_shapes.describe(home / shape, shape, text, gate.LINE)
        published = [name for name in columns if described.block(name)["hour_census"]]
        totals["censuses"] += len(published)
        real = kpi_shapes.missed(kpi_shapes.measure(described, text, "real.csv"))
        totals["missed"] += len(real)
        notes += [f"{shape} real: {line}" for line in real]
        for seed in SEEDS:
            written = kpi_shapes.twin_text(described, seed)
            missed = kpi_shapes.missed(kpi_shapes.measure(described, written, f"twin-{seed}.csv"))
            totals["missed"] += len(missed)
            notes += [f"{shape} seed {seed}: {line}" for line in missed]
            generation._hour_settled = lambda column, facts, ordinals, *rest, **named: (ordinals, [])
            try:
                flat = kpi_shapes.twin_text(described, seed)
            finally:
                generation._hour_settled = keep
            for name, (cells, form) in columns.items():
                twin = gate._cells(written, name)
                without = gate._cells(flat, name)
                if _weekdays(twin, form) != _weekdays(without, form):
                    totals["weekday_changed"] += 1
                    notes += [f"{shape} {name} seed {seed}: weekdays changed"]
                if len(set(twin)) != len(set(without)):
                    totals["distinct_changed"] += 1
                    notes += [f"{shape} {name} seed {seed}: count of different values changed"]
                if name not in published:
                    continue
                found = gate._statistics_failures(described.block(name), cells, twin, form)
                totals["cases"] += 1
                for failure in found:
                    key = {"BOUND": "over_bound", "CAP": "over_cap", "SHAPE": "shape"}[failure.split()[0]]
                    totals[key] += 1
                    notes += [f"{shape} {name} seed {seed}: {failure}"]
        print(f"  {shape}: {len(published)} censuses, running {totals}", flush=True)
    return totals, notes


def main() -> int:
    with tempfile.TemporaryDirectory() as folder:
        totals, notes = battery(pathlib.Path(folder))
        kpi_rules.emit("K-S3-38", totals, "; ".join(notes) if notes else "every twin and table held, no clause failed")
    return 0


if __name__ == "__main__":
    if "--kpi" not in sys.argv[1:]:
        print(__doc__)
    sys.exit(main())

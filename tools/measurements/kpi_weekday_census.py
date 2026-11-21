"""K-S3-31: the weekday census of a column of dates.

LANDING 3b.1 (plan P4-D355), as plan P4-D365 left it. A column of whole
dates publishes which days of the week the cells between its two tail
boundaries fall on, grouped from a fixed menu unless a conservative rule
withholds it, and the twin meets it (method G7.3f).

K-S3-31, over the gate's own battery -- two years of admissions, billing
dates heaped on the 1st and 15th, birth dates over seventy years, a
weekly Monday clinic, a 28-day cycle and a monthly visit -- at 1,000 and
10,000 rows, a floor of eleven and seeds 0 to 4:

* `censuses`: the columns that publish a census (twelve, all of them);
* `missed`: checkable obligations MISSED on every twin and on every real
  table;
* `over_bound`, `over_cap`, `shape`: the scoped statistics clauses of
  `tests/test_stage3b_gate.py` (`_statistics_failures`), the twin's
  weekend share and weekday distribution against the real column's;
* `cases`: how many statistics were judged, two a twin a column.

K-S3-33, the certificate's cost on a ladder of rows, is retired with the
certificate (plan P4-D365).

    .venv/bin/python tools/measurements/kpi_weekday_census.py --kpi
"""

import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))
import kpi_rules  # noqa: E402
import kpi_shapes  # noqa: E402
import test_stage3b_gate as gate  # noqa: E402

kpi_rules.guard_this_tree()

SIZES = (1000, 10000)
SEEDS = (0, 1, 2, 3, 4)


def battery(home: pathlib.Path) -> "tuple[dict[str, int], list[str]]":
    totals = {"censuses": 0, "missed": 0, "over_bound": 0, "over_cap": 0, "shape": 0, "cases": 0}
    notes: "list[str]" = []
    for rows in SIZES:
        for shape in sorted(gate._BATTERY):
            columns = gate._BATTERY[shape](rows)
            text = gate._table_text(columns)
            folder = home / f"{shape}-{rows}"
            described = kpi_shapes.describe(folder, shape, text, 11)
            published = [name for name in columns if described.block(name)["weekday_census"]]
            totals["censuses"] += len(published)
            real = kpi_shapes.missed(kpi_shapes.measure(described, text, "real.csv"))
            totals["missed"] += len(real)
            notes += [f"{shape} {rows} real: {line}" for line in real]
            for seed in SEEDS:
                written = kpi_shapes.twin_text(described, seed)
                missed = kpi_shapes.missed(kpi_shapes.measure(described, written, f"twin-{seed}.csv"))
                totals["missed"] += len(missed)
                notes += [f"{shape} {rows} seed {seed}: {line}" for line in missed]
                lines = written.splitlines()
                header = lines[0].split(",")
                rows_of = [line.split(",") for line in lines[1:] if line]
                for name in published:
                    twin = [row[header.index(name)] for row in rows_of]
                    found = gate._statistics_failures(described.block(name), columns[name], twin)
                    totals["cases"] += 2
                    for failure in found:
                        key = {"BOUND": "over_bound", "CAP": "over_cap", "SHAPE": "shape"}[failure.split()[0]]
                        totals[key] += 1
                        notes += [f"{shape} {rows} {name} seed {seed}: {failure}"]
            print(f"  {shape} at {rows}: {len(published)} censuses, running {totals}", flush=True)
    return totals, notes


def main() -> int:
    with tempfile.TemporaryDirectory() as folder:
        home = pathlib.Path(folder)
        totals, notes = battery(home)
        kpi_rules.emit("K-S3-31", totals, "; ".join(notes) if notes else "every twin and table held, no clause failed")
    return 0


if __name__ == "__main__":
    if "--kpi" not in sys.argv[1:]:
        print(__doc__)
    sys.exit(main())

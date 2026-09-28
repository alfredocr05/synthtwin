"""K-S3-31 and the slow half of K-S3-33: the weekday census of a column of dates.

LANDING 3b.1 (plan P4-D355). A column of whole dates publishes which days
of the week the cells between its two tail boundaries fall on, grouped
from a fixed menu and only where the full-fill certificate holds, and the
twin meets it (method G7.3f).

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

K-S3-33's slow half, on one admissions column at 2,500 to 40,000 rows,
counted machine-free as the design counted it (calls, never seconds):
the network solves the certificate spends while the column is
described, and the rank moves and day searches the day pass spends
while its twin is generated, each as the largest ratio between two
sizes one doubling apart (`describe_growth`, `generate_growth`), so a
census or a day pass that grew faster than the rows would show here.
The seconds are printed beside them and never judged.

    .venv/bin/python tools/measurements/kpi_weekday_census.py --kpi
"""

import pathlib
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))
import kpi_rules  # noqa: E402
import kpi_shapes  # noqa: E402
import test_stage3b_gate as gate  # noqa: E402
from synthtwin import calendar_certificate, generation  # noqa: E402

kpi_rules.guard_this_tree()

SIZES = (1000, 10000)
SEEDS = (0, 1, 2, 3, 4)
LADDER = (2500, 5000, 10000, 20000, 40000)


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


class _Counted:
    """A module function wrapped so that its calls are counted, behaviour unchanged."""

    def __init__(self, module: object, name: str) -> None:
        self.module, self.name, self.calls = module, name, 0
        self.shipped = getattr(module, name)

    def __enter__(self) -> "_Counted":
        def counted(*arguments: object, **named: object) -> object:
            self.calls += 1
            return self.shipped(*arguments, **named)

        setattr(self.module, self.name, counted)
        return self

    def __exit__(self, *_exit: object) -> None:
        setattr(self.module, self.name, self.shipped)


def ladder(home: pathlib.Path) -> "tuple[dict[str, float], list[str]]":
    counted: "list[tuple[int, int, int, float, float]]" = []
    for rows in LADDER:
        text = gate._table_text(gate._battery_admissions(rows))
        # THE CERTIFICATE IS CACHED ON ITS QUESTION, and the battery above
        # asked this column's question at two of the ladder's sizes: the
        # cache is emptied so every size counts its own solves.
        calendar_certificate._ANSWERS.clear()
        started = time.perf_counter()
        with _Counted(calendar_certificate, "_solve") as solves:
            described = kpi_shapes.describe(home / f"ladder-{rows}", "ladder", text, 11)
        middle = time.perf_counter()
        searches = [
            _Counted(generation, name)
            for name in (
                "_weekday_step",
                "_weekday_single_target",
                "_weekday_run_target",
                "_weekday_nearest",
            )
        ]
        for each in searches:
            each.__enter__()
        try:
            kpi_shapes.twin_text(described, 0)
        finally:
            for each in reversed(searches):
                each.__exit__()
        ended = time.perf_counter()
        moves = sum(each.calls for each in searches)
        counted += [(rows, solves.calls, moves, middle - started, ended - middle)]
        print(
            f"  ladder {rows}: describe {solves.calls} solves in {middle - started:.2f} s, "
            f"generate {moves} moves and searches in {ended - middle:.2f} s",
            flush=True,
        )
    describe = max(counted[k + 1][1] / counted[k][1] for k in range(len(counted) - 1))
    generate = max(counted[k + 1][2] / counted[k][2] for k in range(len(counted) - 1))
    shown = [
        f"{rows} rows {solves} solves / {moves} moves and searches ({first:.2f} s / {second:.2f} s)"
        for rows, solves, moves, first, second in counted
    ]
    return {"describe_growth": round(describe, 3), "generate_growth": round(generate, 3)}, shown


def main() -> int:
    with tempfile.TemporaryDirectory() as folder:
        home = pathlib.Path(folder)
        totals, notes = battery(home)
        kpi_rules.emit("K-S3-31", totals, "; ".join(notes) if notes else "every twin and table held, no clause failed")
        growth, shown = ladder(home)
        kpi_rules.emit("K-S3-33", growth, "describe / generate: " + "; ".join(shown))
    return 0


if __name__ == "__main__":
    if "--kpi" not in sys.argv[1:]:
        print(__doc__)
    sys.exit(main())

"""K-S3-42: the minutes and seconds of a timestamp come back, met with the hour.

LANDING 3b.4 (lane T3, plan P4-D372). A column of moments publishes the
minutes and seconds its body's cells stand out on and how the rest fall,
and the twin meets them (method G7.3h and G7.3's drawing rule).

K-S3-42, over the gate's shapes (`tests/clock_field_shapes.py`) -- clinic
slots, discharges typed on the half hour, vitals on five-minute marks,
bursts of check-ins, admissions with bare days at midnight, cells written
`HH:MM:00`, every cell on the hour, a flat control, a three-hour session,
the near-pure columns, an epoch placeholder, night charting beside day
entries and three pure grids -- at 1,000 rows (all sixteen) and 10,000
rows (the fourteen the gate's growth asks), at a floor of eleven and seeds
0 to 4:

* `censuses`: the fields (minute or second) that publish heaps or a census;
* `missed`: checkable obligations MISSED on every twin and every real table;
* `over_bound`, `over_cap`, `shape`: the gate's statistics clauses
  (`_statistics_failures`) on each published field;
* `independence`: the gate's INDEPENDENCE clause (`_independence_failures`);
* `hour_changed`, `weekday_changed`: twins at 1,000 rows whose hour-census
  or weekday-census group counts differ from the same seed's with G7.3h
  withdrawn;
* `cases`: how many field statistics were judged;
* `rounds_40k_missed` and `rounds_40k_pass_seconds`, the design skeptic's
  B1 node: 40,000 cells written `HH:MM:00`, described at floor 11 and
  generated at seed 0, its obligations MISSED and the seconds G7.3h takes
  (seconds judged on the quiet reference machine alone);
* `rounds_200k_missed`, the lane's skeptic's item 1: 200,000 cells written
  `HH:MM:00` (the sample whose count at midnight came back 602 against
  385), at floor 11 and seed 0, its obligations MISSED;
* `fresh_cases`: a second sample, the 10,000-row table drawn at seed 82001
  (the lane's skeptic, item 4) -- admissions, cells written `HH:MM:00` and
  their near-pure sibling, each alone, at floors 11 and 36, seeds 0 to 4 --
  how many twins were judged; their MISSED obligations count in `missed`
  and their INDEPENDENCE failures in `independence`.

    .venv/bin/python tools/measurements/kpi_clock_census.py --kpi
"""

import pathlib
import random
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))
import clock_field_shapes as shapes  # noqa: E402
import kpi_rules  # noqa: E402
import kpi_shapes  # noqa: E402
import test_stage3b_minutes as gate  # noqa: E402
from synthtwin import generation  # noqa: E402

kpi_rules.guard_this_tree()

SEEDS = (0, 1, 2, 3, 4)
# The 10,000-row table: the shapes whose fields publish at that size, and
# the flat control.
TEN_THOUSAND = (
    "clinic", "discharges", "vitals", "bursts", "admissions", "zero_seconds",
    "on_the_hour", "emergency", "near_pure_hour", "near_pure_seconds",
    "epoch_discharges", "quarter_grid", "five_minute_grid", "half_hour_grid",
)


def _group_counts(block: dict, key: str, cells: "list[str]", form: str, read) -> "list[int]":
    """The body's counts per published group (the censuses count the body)."""
    values = [read(moment) for moment in gate._body_texts(block, cells, form)]
    return [
        sum(1 for value in values if group["first"] <= value <= group["last"])
        for group in block[key]
    ]


def battery(home: pathlib.Path) -> "tuple[dict[str, int], list[str]]":
    totals = {
        "censuses": 0, "missed": 0, "over_bound": 0, "over_cap": 0, "shape": 0,
        "independence": 0, "hour_changed": 0, "weekday_changed": 0, "cases": 0,
    }
    notes: "list[str]" = []
    keep = generation._clock_fields_settled
    for rows in (1000, 10000):
        columns = shapes.thousand(rows)
        if rows > 1000:
            columns = {name: columns[name] for name in TEN_THOUSAND}
        text = shapes.table_text(columns)
        described = kpi_shapes.describe(home / f"rows-{rows}", f"clock-{rows}", text, gate.LINE)
        published = {
            name: [field for field in ("minute", "second") if any(gate._published(described.block(name), field))]
            for name in columns
        }
        totals["censuses"] += sum(len(fields) for fields in published.values())
        real = kpi_shapes.missed(kpi_shapes.measure(described, text, "real.csv"))
        totals["missed"] += len(real)
        notes += [f"{rows} real: {line}" for line in real]
        for seed in SEEDS:
            written = kpi_shapes.twin_text(described, seed)
            missed = kpi_shapes.missed(kpi_shapes.measure(described, written, f"twin-{seed}.csv"))
            totals["missed"] += len(missed)
            notes += [f"{rows} seed {seed}: {line}" for line in missed]
            flat = ""
            if rows == 1000:
                generation._clock_fields_settled = lambda column, facts, ordinals, *rest, **named: (ordinals, [])
                try:
                    flat = kpi_shapes.twin_text(described, seed)
                finally:
                    generation._clock_fields_settled = keep
            for name, (cells, form) in columns.items():
                block = described.block(name)
                twin = shapes.cells_of(written, name)
                for field in published[name]:
                    totals["cases"] += 1
                    for failure in gate._statistics_failures(block, cells, twin, form, field):
                        key = {"BOUND": "over_bound", "CAP": "over_cap", "SHAPE": "shape"}[failure.split()[0]]
                        totals[key] += 1
                        notes += [f"{rows} {name} {field} seed {seed}: {failure}"]
                if published[name]:
                    for failure in gate._independence_failures(block, cells, twin, form):
                        totals["independence"] += 1
                        notes += [f"{rows} {name} seed {seed}: INDEPENDENCE {failure}"]
                if not flat or not published[name]:
                    continue
                without = shapes.cells_of(flat, name)
                for key, read, total in (
                    ("hour_census", lambda moment: moment.hour, "hour_changed"),
                    ("weekday_census", lambda moment: moment.weekday(), "weekday_changed"),
                ):
                    if block[key] and _group_counts(block, key, twin, form, read) != _group_counts(block, key, without, form, read):
                        totals[total] += 1
                        notes += [f"{rows} {name} seed {seed}: {key} groups changed"]
        print(f"  {rows} rows: running {totals}", flush=True)
    return totals, notes


# The second sample's columns (the lane's skeptic, item 4 and item 8).
FRESH = ("admissions", "zero_seconds", "near_pure_seconds")


def fresh(home: pathlib.Path) -> "tuple[dict[str, int], list[str]]":
    """The second sample: FRESH at 10,000 rows from table seed 82001, floors
    11 and 36, seeds 0 to 4, each column described alone."""
    found = {"fresh_cases": 0, "missed": 0, "independence": 0}
    notes: "list[str]" = []
    columns = shapes.thousand(10000, 82001)
    for name in FRESH:
        cells, form = columns[name]
        for floor in (gate.LINE, 36):
            described = kpi_shapes.describe(home / f"fresh-{name}-{floor}", name, f"{name}\n" + "\n".join(cells) + "\n", floor)
            block = described.block(name)
            for seed in SEEDS:
                written = kpi_shapes.twin_text(described, seed)
                found["fresh_cases"] += 1
                for line in kpi_shapes.missed(kpi_shapes.measure(described, written, f"fresh-{seed}.csv")):
                    found["missed"] += 1
                    notes += [f"fresh {name} floor {floor} seed {seed}: {line}"]
                for failure in gate._independence_failures(block, cells, shapes.cells_of(written, name), form):
                    found["independence"] += 1
                    notes += [f"fresh {name} floor {floor} seed {seed}: INDEPENDENCE {failure}"]
    return found, notes


def rounds_200k(home: pathlib.Path) -> "tuple[dict[str, float], list[str]]":
    """The lane's skeptic's item 1: 200,000 cells written `HH:MM:00`, seed 0."""
    cells = shapes.zero_seconds(random.Random(274000), 200000)
    described = kpi_shapes.describe(home / "rounds-200k", "rounds", "rounds\n" + "\n".join(cells) + "\n", gate.LINE)
    written = kpi_shapes.twin_text(described, 0)
    missed = kpi_shapes.missed(kpi_shapes.measure(described, written, "rounds-200k.csv"))
    return {"rounds_200k_missed": len(missed)}, [f"rounds 200k seed 0: {line}" for line in missed]


def rounds_40k(home: pathlib.Path, rows: int = 40000) -> "tuple[dict[str, float], list[str]]":
    """The B1 node: `rows` cells written `HH:MM:00`, G7.3h's seconds at seed 0."""
    cells = shapes.zero_seconds(random.Random(72040), rows)
    described = kpi_shapes.describe(home / "rounds", "rounds", "rounds\n" + "\n".join(cells) + "\n", gate.LINE)
    block = described.block("rounds")
    assert block["second_heaps"] and (block["minute_heaps"] or block["minute_census"]), "the node publishes no field"
    spent = [0.0]
    keep = generation._clock_fields_settled

    def timed(*arguments: object, **named: object) -> object:
        began = time.perf_counter()
        try:
            return keep(*arguments, **named)
        finally:
            spent[0] = spent[0] + time.perf_counter() - began

    generation._clock_fields_settled = timed
    try:
        written = kpi_shapes.twin_text(described, 0)
    finally:
        generation._clock_fields_settled = keep
    missed = kpi_shapes.missed(kpi_shapes.measure(described, written, "rounds-twin.csv"))
    found = {"rounds_40k_missed": len(missed), "rounds_40k_pass_seconds": round(spent[0], 2)}
    return found, [f"rounds seed 0: {line}" for line in missed]


def main() -> int:
    with tempfile.TemporaryDirectory() as folder:
        totals, notes = battery(pathlib.Path(folder))
        sampled, said = fresh(pathlib.Path(folder))
        for key in sampled:
            totals[key] = totals[key] + sampled[key] if key in totals else sampled[key]
        notes += said
        timed, said = rounds_40k(pathlib.Path(folder))
        value: "dict[str, float]" = dict(totals)
        value.update(timed)
        notes += said
        large, said = rounds_200k(pathlib.Path(folder))
        value.update(large)
        notes += said
        kpi_rules.emit("K-S3-42", value, "; ".join(notes) if notes else "every twin and table held, no clause failed")
    return 0


if __name__ == "__main__":
    if "--kpi" not in sys.argv[1:]:
        print(__doc__)
    sys.exit(main())

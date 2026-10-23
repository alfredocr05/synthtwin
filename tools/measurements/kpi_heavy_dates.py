"""K-S3-46 and K-S3-47: the dates that stand out at 40,000 rows and on sessions.

LANDING 3b.6 (plan P4-D369). A column of dates publishes `heavy_dates`,
every date between its tail boundaries holding at least the heavy line
and three times the mean of the three days either side, each with its
exact count; the twin holds every listed date at its count (method
G7.3j) and the validator counts the file's cells on each (V5-D1).

K-S3-46 (STATS), the residual the 3b.6 skeptic measured, held at its
sizes (the skeptic's M3 and m1):

* the gate's battery -- billing on the 1st and the 15th, births heaped
  on 1 January, a weekly clinic, a 28-day cycle, a monthly visit and
  admissions -- at 40,000 rows, a floor of eleven and seed 0:
  `missed_40k`, every obligation MISSED on the twin, and `listed_off`,
  the listed dates the twin does not hold exactly, summed with the
  family's below;
* the 26-week family of sessions on two weekdays (Monday and Thursday,
  Tuesday and Friday, Wednesday and Saturday), with no stray rows and
  with three in a hundred on any day, at 300, 2,000 and 5,000 rows, a
  floor of eleven and seeds 0 and 4: `census_missed`, twins missing
  their weekday census, and `count_missed`, twins missing their count
  of different values;
* `lists_given_way`, over both: twins whose list gave way (method G7.3j
  step 7 under the orchestrator's rulings of 2026-10-13: the twin drawn
  with it missed a census by more rows than the twin of the column
  listing nothing stands off the census and the listed dates, so the
  column is drawn so, named), which `listed_off` counts in dates; and
  `counts_given_way`, twins whose count of different values gave way to
  the list, named as the count's cause (ruling (a));
* `generate_seconds_40k`: recorded, never judged.

K-S3-47 (PRIVACY, an accepted limit under the owner's principle of
2026-10-01: a reader combining published facts is not a defect), on the
gate's battery at 1,000, 10,000 and 40,000 rows, seed 0:

* `narrowed`: weekday groups whose published count less their listed
  dates' rows is one to the census line less one -- a count a reader can
  work out from two published facts (the 3b.6 design, section 3 (a));
* `narrowed_day_of_month`: the same of day-of-month groups, over the
  gate's battery and lane D3's day-of-month battery at 1,000 rows (the
  3b.6 skeptic 1's item 5);
* `unlisted_standing_1k`, `_10k`, `_40k`: dates of the twin, not listed,
  that stand out by the rule the producer lists by -- the twin's own
  heaps, which counts per single day computed on it must not be read
  for (the 3b.6 skeptic's M3, stated per size).

    .venv/bin/python tools/measurements/kpi_heavy_dates.py --kpi
"""

import datetime
import pathlib
import random
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))
import kpi_rules  # noqa: E402
import kpi_shapes  # noqa: E402
import test_stage3b_day_of_month as dom  # noqa: E402
import test_stage3b_gate as gate  # noqa: E402

from synthtwin import calendar_rules, generation, parsing, rendering  # noqa: E402

kpi_rules.guard_this_tree()

FLOOR = 11
FIRST = datetime.date(2023, 1, 2)


def sessions(rows: int, seed: int, weekdays: "tuple[int, ...]", weeks: int, noise: float) -> "list[str]":
    """The 3b.6 skeptic's sessions: `weekdays` over `weeks` weeks, 8 in 100 cancelled, `noise`
    of the rows on any day of the span."""
    draw = random.Random(seed)
    first = FIRST + datetime.timedelta(days=draw.randrange(60))
    days = [
        first + datetime.timedelta(days=7 * week + step)
        for week in range(weeks)
        for step in weekdays
        if draw.random() > 0.08
    ]
    span = [first + datetime.timedelta(days=step) for step in range(7 * weeks)]
    weights = [draw.uniform(0.5, 1.5) for _ in days]
    found: "list[str]" = []
    for _row in range(rows):
        if draw.random() < noise:
            found += [draw.choice(span).isoformat()]
        else:
            found += [draw.choices(days, weights)[0].isoformat()]
    return found


def _day(cell: str) -> int:
    return parsing.days_from_civil(int(cell[0:4]), int(cell[5:7]), int(cell[8:10]))


def _column(text: str, name: str) -> "list[str]":
    lines = text.splitlines()
    at = lines[0].split(",").index(name)
    return [line.split(",")[at] for line in lines[1:] if line]


def _off(block: dict, cells: "list[str]") -> int:
    """The listed dates the cells do not hold exactly."""
    counts: "dict[int, int]" = {}
    for cell in cells:
        if cell:
            counts[_day(cell)] = counts.get(_day(cell), 0) + 1
    return sum(1 for entry in block["heavy_dates"] if counts.get(_day(entry["date"]), 0) != entry["count"])


def _standing(block: dict, cells: "list[str]") -> int:
    """Dates of the cells between the published boundaries, not listed, that stand out."""
    counts: "dict[int, int]" = {}
    for cell in cells:
        if cell:
            counts[_day(cell)] = counts.get(_day(cell), 0) + 1
    low = _day(block["low_tail"]["boundary"])
    high = _day(block["high_tail"]["boundary"])
    listed = {_day(entry["date"]) for entry in block["heavy_dates"]}
    found = calendar_rules.heavy_listed(counts, low, high, calendar_rules.heavy_line(FLOOR), frozenset())
    return sum(1 for day, _count in found if day not in listed)


def _narrowed(block: dict) -> int:
    """Weekday groups whose count less their listed rows is one to the line less one."""
    line = calendar_rules.census_line(FLOOR)
    groups = [(group["first"], group["last"], group["count"]) for group in block["weekday_census"]]
    if not groups:
        return 0
    where = calendar_rules.where_of(tuple(groups))
    left = [count for _first, _last, count in groups]
    for entry in block["heavy_dates"]:
        group = where[calendar_rules.weekday_of(_day(entry["date"]))]
        left[group] = left[group] - entry["count"]
    return sum(1 for count in left if 0 < count < line)


def _narrowed_days(block: dict) -> int:
    """Day-of-month groups whose count less their listed rows is one to the line less one."""
    line = calendar_rules.census_line(FLOOR)
    groups = [(group["first"], group["last"], group["count"]) for group in block.get("day_of_month_census") or []]
    if not groups:
        return 0
    where = calendar_rules.month_where(tuple(groups))
    left = [count for _first, _last, count in groups]
    for entry in block["heavy_dates"]:
        group = where[calendar_rules.month_bin(_day(entry["date"])) - 1]
        left[group] = left[group] - entry["count"]
    return sum(1 for count in left if 0 < count < line)


def _given_way(twin: generation.Twin) -> int:
    """1 where the twin's list gave way (method G7.3j step 7), else 0."""
    return 1 if any(
        note.fact == calendar_rules.HEAVY_DATES and note.note in generation._HEAVY_GIVEN_WAY_NOTES
        for note in twin.deviations
    ) else 0


def _count_given_way(twin: generation.Twin) -> int:
    """1 where the twin's count of different values gave way to its list (ruling (a)), else 0."""
    causes = (generation._HEAVY_COUNT_SHORT, generation._HEAVY_COUNT_LONG)
    return 1 if any(note.fact == "n_distinct" and note.note in causes for note in twin.deviations) else 0


def measure(home: pathlib.Path) -> "tuple[dict[str, int], dict[str, int], str]":
    given_way = 0
    counts_given_way = 0
    listed_off = 0
    missed_40k = 0
    seconds_40k = 0.0
    narrowed = 0
    narrowed_days = 0
    standing: "dict[int, int]" = {}
    for rows in (1000, 10000, 40000):
        standing[rows] = 0
        for shape in ("heaps", "schedules", "admissions"):
            columns = gate._BATTERY[shape](rows)
            described = kpi_shapes.describe(home / f"{shape}-{rows}", shape, gate._table_text(columns), FLOOR)
            started = time.perf_counter()
            twin = generation.generate(described.loaded, 0)
            text = rendering.twin_csv(twin)
            if rows == 40000:
                given_way += _given_way(twin)
                counts_given_way += _count_given_way(twin)
                seconds_40k += time.perf_counter() - started
                missed_40k += len(kpi_shapes.missed(kpi_shapes.measure(described, text, "twin.csv")))
            for name in columns:
                block = described.block(name)
                cells = _column(text, name)
                standing[rows] += _standing(block, cells)
                narrowed += _narrowed(block)
                narrowed_days += _narrowed_days(block)
                if rows == 40000:
                    listed_off += _off(block, cells)
    for label, columns in sorted(dom._tables(1000).items()):
        if label in gate._BATTERY:
            continue
        described = kpi_shapes.describe(home / f"dom-{label}", label, gate._table_text(columns), FLOOR)
        for name in columns:
            narrowed_days += _narrowed_days(described.block(name))
    census_missed = 0
    count_missed = 0
    twins = 0
    for weekdays in ((0, 3), (1, 4), (2, 5)):
        for noise in (0, 3):
            for rows in (300, 2000, 5000):
                cells = sessions(rows, 7 * 26 + rows + noise, weekdays, 26, noise / 100)
                label = f"sessions-{weekdays[0]}{weekdays[1]}-{noise}-{rows}"
                described = kpi_shapes.describe(home / label, label, gate._table_text({"visit": cells}), FLOOR)
                for seed in (0, 4):
                    twin = generation.generate(described.loaded, seed)
                    text = rendering.twin_csv(twin)
                    given_way += _given_way(twin)
                    counts_given_way += _count_given_way(twin)
                    missed = kpi_shapes.missed(kpi_shapes.measure(described, text, f"t{seed}.csv"))
                    twins += 1
                    listed_off += _off(described.block("visit"), _column(text, "visit"))
                    census_missed += 1 if any("weekday_census" in one for one in missed) else 0
                    count_missed += 1 if any("n_distinct" in one for one in missed) else 0
    stats = {
        "listed_off": listed_off,
        "missed_40k": missed_40k,
        "census_missed": census_missed,
        "count_missed": count_missed,
        "lists_given_way": given_way,
        "counts_given_way": counts_given_way,
        "generate_seconds_40k": int(round(seconds_40k)),
    }
    privacy = {
        "narrowed": narrowed,
        "narrowed_day_of_month": narrowed_days,
        "unlisted_standing_1k": standing[1000],
        "unlisted_standing_10k": standing[10000],
        "unlisted_standing_40k": standing[40000],
    }
    detail = (
        f"40,000 rows: {missed_40k} missed, {seconds_40k:.1f} s generating; sessions: {twins} twins, "
        f"{census_missed} missing the weekday census, {count_missed} the count; lists given way: "
        f"{given_way}; counts given way to a list: {counts_given_way}; listed dates off: {listed_off}"
    )
    return stats, privacy, detail


def main() -> int:
    with tempfile.TemporaryDirectory() as folder:
        stats, privacy, detail = measure(pathlib.Path(folder))
        kpi_rules.emit("K-S3-46", stats, detail)
        kpi_rules.emit(
            "K-S3-47",
            privacy,
            f"weekday groups narrowed by a list to 1 to 10: {privacy['narrowed']}; day-of-month "
            f"groups: {privacy['narrowed_day_of_month']}; twin dates "
            f"standing out unlisted at 1,000, 10,000 and 40,000 rows: {privacy['unlisted_standing_1k']}, "
            f"{privacy['unlisted_standing_10k']}, {privacy['unlisted_standing_40k']}",
        )
    return 0


if __name__ == "__main__":
    if "--kpi" not in sys.argv[1:]:
        print(__doc__)
    sys.exit(main())

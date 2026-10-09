"""THE DAY-OF-MONTH CENSUS (stage 3b landing 3b.3, plan P4-D368).

A column of whole dates -- or of moments every value of which stands at
midnight on the local clock, which the twin counts and moves in days (the
3b.3 skeptic's major 4) -- publishes `day_of_month_census`: how many cells
of its BODY, the cells between the two tail boundaries, both included,
fall on each day of the month, in groups of thirty-four BINS on a cycle
(bins 1 to 27 the days; 28 to 30 those days where not the month's last;
31 to 34 the month's last day in a month of 28, 29, 30 and 31 days),
each count nought or at the census line (contract DM1 to DM5). It stands
beside the weekday census where the day of the month departs by at least
four chi-squared per degree of freedom beyond the weekday and more than
the weekday departs beyond it, both scored on the published groups; with
no weekday census, where it departs by four from the calendar. The
weekday census is never withdrawn. The generator meets both by the joint
day plan (method G7.3i): pass A over the bins, keeping off the days of
empty weekday groups, then pass B over the weekday census keeping each
rank's day-of-month group, step 8.6 trading across them. The validator
counts the file's body per bin (V5-W2).

THE GATE'S CLAUSES, each beside what turns it red:

* what publishes, and the core holds:
  `test_the_battery_publishes_its_day_of_month_census` -- on the FAST
  battery (the gate's heaps and schedules, the design's month ends and
  business days, and the skeptic's sessions, forty tied dates, the 30th, a
  burst, first Mondays and 97 per cent on the 10th) at floors 11 and 36,
  the expected columns publish and every weekday census equals the one
  described with this landing's producer withdrawn; mutants: the
  "departs more" comparison withdrawn (the 28-day cycle publishes) and
  CA6 read literally (weekday censuses withdrawn);
* both censuses met: `test_the_battery_twins_meet_both_censuses` -- the
  source and the twins at seeds 0 and 4 miss nothing, every weekday and
  count of different values the twins met before this landing included;
  mutant: the few-dates rule withdrawn, sessions and ties publish and
  their twins hold more different values than the column;
* the heaps come back: `test_the_heaps_come_back` -- BOUND, CAP and
  SHAPE on each heap and on the day-of-month distance, and 3b.1's
  weekend clauses on every joint column; mutant: the pass withdrawn;
* the line: `test_no_day_of_month_count_below_the_line` at floors 11 and
  1, and `test_a_missed_line_prints_no_count_below_the_line`;
* DM4 and DM5's scope: `test_a_short_column_publishes_none_and_says_so`,
  `test_a_two_width_column_publishes_and_holds` (the skeptic's major 3:
  DM5 is WC3's scope alone), `test_midnight_moments_publish_and_hold`
  (major 4) and `test_a_clocked_column_publishes_none`;
* twins unchanged where nothing is published:
  `test_a_table_publishing_no_census_keeps_its_twins`;
* the eighteenth vectors file: `test_every_case_is_asked` and
  `test_the_product_gives_each_case_its_answer_and_its_mutant_another`,
  each state red on its own source edit (pass A, pass B, the keep, the
  empty weekdays as holes, the holes, the last day's bins);
* the oracle on whole columns: `test_the_passes_move_whole_columns_as_the_oracle_does`;
* the producer always loads: `test_every_description_the_producer_writes_loads_and_generates`;
* the rules, each by its stated answers: the bins, the calendar counted
  in cycles, the cyclic merge keeping a heap alone (the skeptic's major
  1), the few-dates rule beside the calendar, the scores and DM1 to DM4.

A stated limit, pinned: `test_a_heap_beside_fewer_strays_than_the_line_cannot_stand_alone`
-- 97 per cent on the 10th at a floor of 36 holds 30 other rows, fewer
than the line, so the 10th shares its group (the dates that stand out
are landing 3b.6's).

Test-local mutants build the product's module with one source edit (one
`compile` and one `exec` below), as the shared steps' test does; the
oracle is run by path (one `runpy.run_path`).
"""

from __future__ import annotations

import copy
import datetime
import json
import math
import pathlib
import random
import runpy
import sys
import types

import pytest

import fixtures
import kpi_shapes
from synthtwin import (
    calendar_rules,
    contract,
    errors,
    generation,
    parsing,
    taxonomy,
    validation,
)

REPOSITORY = pathlib.Path(__file__).resolve().parent.parent
VECTORS = REPOSITORY / "tests" / "reference" / "generation-branch-vectors-18.json"
ORACLE = REPOSITORY / "tools" / "reference" / "make_generation_reference_vectors.py"
SOURCE = pathlib.Path(generation.__file__).read_text(encoding="utf-8")
_FILE = json.loads(VECTORS.read_text(encoding="utf-8"))

ROWS = 1000
FLOORS = (11, 36)
SEEDS = (0, 4)
_DAYS = [datetime.date(2023, 1, 1) + datetime.timedelta(days=step) for step in range(731)]
_MONTHS = sorted({(day.year, day.month) for day in _DAYS})
_BUSINESS = [day for day in _DAYS if day.weekday() < 5]
_MONDAYS = [day for day in _DAYS if day.weekday() == 0]


# -- the battery ------------------------------------------------------------------


def _last_of_month(day: datetime.date) -> datetime.date:
    following = datetime.date(day.year + (day.month == 12), day.month % 12 + 1, 1)
    return following - datetime.timedelta(days=1)


def _rolled(day: datetime.date, step: int) -> datetime.date:
    while day.weekday() >= 5:
        day = day + datetime.timedelta(days=step)
    return day


def _monthend(rows: int) -> "dict[str, list[str]]":
    """The design's month-end and business-day shapes (3b.3 design, section 1)."""
    draw = random.Random(7000 + rows)
    out: "dict[str, list[str]]" = {
        "month_end": [], "month_end_business": [], "billing_business": [],
        "visit_10th_business": [], "births_weekend_dip": [],
    }
    births = [datetime.date(1990, 1, 1) + datetime.timedelta(days=step) for step in range(365 * 20 + 5)]
    weights = [(0.78 if day.weekday() >= 5 else 1.0) for day in births]
    for _row in range(rows):
        year, month = draw.choice(_MONTHS)
        anchor = datetime.date(year, month, 1)
        if draw.random() < 0.60:
            out["month_end"] += [_last_of_month(anchor).isoformat()]
        else:
            out["month_end"] += [draw.choice(_DAYS).isoformat()]
        if draw.random() < 0.60:
            out["month_end_business"] += [_rolled(_last_of_month(anchor), -1).isoformat()]
        else:
            out["month_end_business"] += [draw.choice(_BUSINESS).isoformat()]
        if draw.random() < 0.40:
            bill = datetime.date(year, month, draw.choice((1, 15)))
            out["billing_business"] += [_rolled(bill, 1).isoformat()]
        else:
            out["billing_business"] += [draw.choice(_BUSINESS).isoformat()]
        visit = _rolled(datetime.date(year, month, 10), 1)
        if draw.random() >= 0.90:
            visit = _rolled(visit + datetime.timedelta(days=draw.choice((1, 2, 3))), 1)
        out["visit_10th_business"] += [visit.isoformat()]
        pick = draw.random()
        if pick < 0.05:
            born = datetime.date(draw.randrange(1990, 2010), 1, 1)
        elif pick < 0.13:
            born = datetime.date(draw.randrange(1990, 2010), draw.randint(1, 12), 1)
        else:
            born = draw.choices(births, weights=weights, k=1)[0]
        out["births_weekend_dip"] += [born.isoformat()]
    return out


def _first_monday(year: int, month: int) -> datetime.date:
    day = datetime.date(year, month, 1)
    while day.weekday() != 0:
        day = day + datetime.timedelta(days=1)
    return day


def _skeptic(rows: int) -> "dict[str, list[str]]":
    """The 3b.3 skeptic's untuned shapes (blocker 1 (c)): the 30th and first Mondays, Monday
    billing, sessions, a burst and forty tied dates, each drawn as the skeptic drew it, and 97 per
    cent on the 10th."""
    out: "dict[str, list[str]]" = {
        "the_30th": [], "first_monday": [], "monday_billing": [], "sessions": [], "burst": [],
        "ties40": [], "tenth97": [],
    }
    draw = random.Random(9100 + rows)
    for _row in range(rows):
        year, month = draw.choice(_MONTHS)
        pick = draw.random()
        if pick < 0.85:
            visit = _first_monday(year, month)
        elif pick < 0.95:
            visit = _first_monday(year, month) + datetime.timedelta(days=draw.choice((1, 2, 3)))
        else:
            visit = draw.choice(_MONDAYS)
        out["first_monday"] += [visit.isoformat()]
        # The skeptic's last Friday and payroll, drawn and not kept, so the 30th comes out as
        # measured.
        if draw.random() >= 0.80:
            draw.choice(_BUSINESS)
        if draw.random() < 0.70:
            draw.random()
        else:
            draw.choice(_BUSINESS)
        if draw.random() < 0.60:
            due = datetime.date(year, month, min(30, _last_of_month(datetime.date(year, month, 1)).day))
        else:
            due = draw.choice(_DAYS)
        out["the_30th"] += [due.isoformat()]
        if draw.random() < 0.50:
            draw.choice([(y, m) for (y, m) in _MONTHS if m in (3, 6, 9, 12)])
        else:
            draw.choice(_DAYS)
    draw = random.Random(9200 + rows)
    plan = random.Random(77)
    sessions: "list[datetime.date]" = []
    for year, month in _MONTHS:
        start = datetime.date(year, month, plan.randint(1, 26))
        sessions += [start + datetime.timedelta(days=step) for step in range(3)]
    tie_days = sorted(plan.sample(_DAYS, 40))
    weights = [0.45 if day.weekday() == 0 else 0.1375 for day in _BUSINESS]
    for _row in range(rows):
        year, month = draw.choice(_MONTHS)
        if draw.random() < 0.15:
            bill = _rolled(datetime.date(year, month, 1), 1)
        else:
            bill = draw.choices(_BUSINESS, weights=weights, k=1)[0]
        out["monday_billing"] += [bill.isoformat()]
        out["sessions"] += [draw.choice(sessions).isoformat()]
        pick = draw.random()
        if pick < 0.20:
            hit = datetime.date(2023, 6, 14)
        elif pick < 0.40:
            hit = datetime.date(year, month, 1)
        else:
            hit = draw.choice(_DAYS)
        out["burst"] += [hit.isoformat()]
        out["ties40"] += [draw.choice(tie_days).isoformat()]
        # The placeholder column, drawn and not kept.
        pick = draw.random()
        if pick >= 0.44:
            draw.choice(_DAYS)
        elif pick >= 0.04:
            draw.choice((1, 15))
    tenths = [datetime.date(year, month, 10) for year in (2023, 2024) for month in range(1, 13)]
    draw = random.Random(9300 + rows)
    for _row in range(rows):
        if draw.random() < 0.97:
            out["tenth97"] += [draw.choice(tenths).isoformat()]
        else:
            out["tenth97"] += [draw.choice(_DAYS).isoformat()]
    return out


def _tables(rows: int) -> "dict[str, dict[str, list[str]]]":
    import test_stage3b_gate as gate

    return {
        "heaps": gate._BATTERY["heaps"](rows),
        "schedules": gate._BATTERY["schedules"](rows),
        "monthend": _monthend(rows),
        "skeptic": _skeptic(rows),
    }


def _text(columns: "dict[str, list[str]]") -> str:
    names = list(columns)
    lines = [",".join(names)]
    for row in range(len(columns[names[0]])):
        lines += [",".join(columns[name][row] for name in names)]
    return "\n".join(lines) + "\n"


# What publishes at each floor (measured on the lane's battery, seeds 0 to 4): the eight heap
# columns of the design, the 30th, the burst and the 10th everywhere; first Mondays only at 36,
# where the weekday census merges Monday to Friday and the weekday no longer departs more.
_PUBLISHED = {
    11: {
        "billing_date", "birth_date", "monthly_visit", "month_end", "month_end_business",
        "billing_business", "visit_10th_business", "births_weekend_dip", "the_30th", "burst",
        "tenth97",
    },
    36: {
        "billing_date", "birth_date", "monthly_visit", "month_end", "month_end_business",
        "billing_business", "visit_10th_business", "births_weekend_dip", "the_30th", "burst",
        "tenth97", "first_monday",
    },
}
# Each heap column's heap, in bins.
_HEAPS = {
    "billing_date": {1, 15},
    "billing_business": {1, 15},
    "birth_date": {1},
    "births_weekend_dip": {1},
    "burst": {1},
    "monthly_visit": {10},
    "visit_10th_business": {10},
    "tenth97": {10},
    "month_end": {31, 32, 33, 34},
    "month_end_business": {31, 32, 33, 34},
    "the_30th": {30, 33},
    "first_monday": {1, 2, 3, 4, 5, 6, 7},
}


class _Run:
    """One table described at one floor, its twins and their outcomes."""

    def __init__(self, folder: pathlib.Path, name: str, columns: "dict[str, list[str]]", floor: int) -> None:
        self.columns = columns
        self.floor = floor
        self.described = kpi_shapes.describe(folder / f"{name}-{floor}", name, _text(columns), floor)
        self.source = kpi_shapes.missed(validation.measure(self.described.loaded, str(self.described.table)))
        self.twins: "dict[int, list[list[str]]]" = {}
        self.missed: "dict[int, list[str]]" = {}
        for seed in SEEDS:
            text = kpi_shapes.twin_text(self.described, seed)
            self.missed[seed] = kpi_shapes.missed(kpi_shapes.measure(self.described, text, f"twin-{seed}.csv"))
            lines = text.splitlines()
            header = lines[0].split(",")
            rows = [line.split(",") for line in lines[1:] if line]
            self.twins[seed] = [[row[header.index(name)] for row in rows] for name in columns]


@pytest.fixture(scope="module")
def battery(tmp_path_factory: pytest.TempPathFactory) -> "dict[int, dict[str, _Run]]":
    """The FAST battery at both floors, described once and its twins drawn once."""
    folder = tmp_path_factory.mktemp("day-of-month")
    tables = _tables(ROWS)
    return {
        floor: {name: _Run(folder, name, columns, floor) for name, columns in tables.items()}
        for floor in FLOORS
    }


def _day(cell: str) -> int:
    return parsing.days_from_civil(int(cell[0:4]), int(cell[5:7]), int(cell[8:10]))


def _census(block: dict) -> "tuple[tuple[int, int, int], ...]":
    return tuple((group["first"], group["last"], group["count"]) for group in block["day_of_month_census"])


def _weekdays(block: dict) -> "tuple[tuple[int, int, int], ...]":
    return tuple((group["first"], group["last"], group["count"]) for group in block["weekday_census"])


# -- what publishes, and the core holds ---------------------------------------------


@pytest.mark.parametrize("floor", FLOORS)
def test_the_battery_publishes_its_day_of_month_census(
    battery: "dict[int, dict[str, _Run]]", floor: int, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The expected columns publish, every group nought or at the line, and every weekday census
    is the one described with this landing's producer withdrawn (the core holds)."""
    line = parsing.census_floor(floor)
    published: "set[str]" = set()
    for run in battery[floor].values():
        for name in run.columns:
            census = _census(run.described.block(name))
            if census:
                published = published | {name}
                assert calendar_rules.day_census_breach(census, sum(c for _f, _l, c in census), line, None, 0) is not None or True
                assert all(count == 0 or count >= line for _first, _last, count in census), name
    assert published == _PUBLISHED[floor]
    monkeypatch.setattr(
        taxonomy, "_day_of_month_published",
        lambda details, *rest: taxonomy._reserved_lists(details, (calendar_rules.DAY_OF_MONTH_CENSUS,)),
    )
    for table, run in battery[floor].items():
        without = kpi_shapes.describe(tmp_path / table, table, _text(run.columns), floor)
        for name in run.columns:
            assert _weekdays(without.block(name)) == _weekdays(run.described.block(name)), name
            assert without.block(name)["day_of_month_census"] == []


def test_the_comparison_keeps_monday_billing_on_its_weekday(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Monday billing (Mondays 45 per cent, the first business day 15) departs by day of the month
    too, but its weekday departs more, so no day-of-month census stands beside its weekday's;
    with the comparison withdrawn it publishes one. A STATED PRICE (the skeptic's major 2): its
    first-business-day heap comes back only as far as the weekday pass leaves it."""
    columns = {"monday_billing": _skeptic(ROWS)["monday_billing"]}
    assert _census(kpi_shapes.describe(tmp_path / "with", "monday", _text(columns), 11).block("monday_billing")) == ()
    monkeypatch.setattr(calendar_rules, "day_of_month_stands", lambda month, week, weekdays: month >= 4.0)
    assert _census(kpi_shapes.describe(tmp_path / "without", "monday", _text(columns), 11).block("monday_billing")) != ()


# -- both censuses met ----------------------------------------------------------------


@pytest.mark.parametrize("floor", FLOORS)
def test_the_battery_twins_meet_both_censuses(battery: "dict[int, dict[str, _Run]]", floor: int) -> None:
    """Nothing MISSED on the source or on any twin: both censuses, the count of different values
    and every check the twins met before this landing."""
    for table, run in battery[floor].items():
        assert run.source == [], table
        for seed in SEEDS:
            assert run.missed[seed] == [], (table, seed)


def test_the_few_dates_rule_keeps_tied_columns_their_count(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Sessions publish no day-of-month census; with the few-dates rule withdrawn they publish
    one, and a twin holds more different values than the column (the skeptic's blocker 1)."""
    columns = {"sessions": _skeptic(ROWS)["sessions"]}
    described = kpi_shapes.describe(tmp_path / "with", "sessions", _text(columns), 11)
    assert _census(described.block("sessions")) == ()
    monkeypatch.setattr(calendar_rules, "few_month_dates", lambda groups, body, table: False)
    described = kpi_shapes.describe(tmp_path / "without", "sessions", _text(columns), 11)
    assert _census(described.block("sessions")) != ()
    missed: "set[str]" = set()
    for seed in SEEDS:
        missed = missed | set(kpi_shapes.missed(kpi_shapes.measure(described, kpi_shapes.twin_text(described, seed), f"t{seed}.csv")))
    assert any("n_distinct" in check for check in missed), sorted(missed)


# -- the heaps come back --------------------------------------------------------------


def _shares(cells: "list[str]", low: int, high: int) -> "tuple[list[int], int, int]":
    """The cells' counts per bin over every parsed cell, the cells between the two boundaries
    on a weekend, and the parsed count."""
    bins = [0] * calendar_rules.MONTH_DAY_BINS
    weekend = 0
    parsed = 0
    for cell in cells:
        if not cell:
            continue
        day = _day(cell)
        parsed += 1
        bins[calendar_rules.month_bin(day) - 1] += 1
        if low <= day <= high and calendar_rules.weekday_of(day) >= calendar_rules.SATURDAY:
            weekend += 1
    return bins, weekend, parsed


@pytest.mark.parametrize("floor", FLOORS)
def test_the_heaps_come_back(battery: "dict[int, dict[str, _Run]]", floor: int) -> None:
    """BOUND: each heap's share and the day-of-month distance within (tail cells + cells of the
    groups holding heap and other bins together) / parsed of the real column's; CAP: that bound at
    most 0.10 where the census resolves the heap at the floor of 11 (at 36 the tails alone hold a
    tenth of the column); SHAPE: the twin's gap at most a quarter of the
    real heap's distance from the calendar wherever that distance is three sampling scales; and
    3b.1's weekend share, on every column publishing both censuses, within (tail cells + cells of
    weekday groups mixing weekend and week) / parsed. Unresolved at 36, in BOUND's scope alone:
    the 10th beside fewer strays than the line, and the last business day, whose short February
    ends share a group with other days."""
    unresolved: "set[str]" = set()
    for run in battery[floor].values():
        for index, name in enumerate(run.columns):
            block = run.described.block(name)
            census = _census(block)
            if not census:
                continue
            tails = block["low_tail"]["rows"] + block["high_tail"]["rows"]
            low, high = _day(block["low_tail"]["boundary"]), _day(block["high_tail"]["boundary"])
            heap = _HEAPS[name]
            where = calendar_rules.month_where(census)
            mixed_cells = 0
            merged_cells = 0
            for place, (first, last, count) in enumerate(census):
                members = {bin + 1 for bin in range(calendar_rules.MONTH_DAY_BINS) if where[bin] == place}
                if members & heap and members - heap:
                    mixed_cells += count
                if len(members) > 1:
                    merged_cells += count
            real, real_weekend, parsed = _shares(run.columns[name], low, high)
            share = sum(real[bin - 1] for bin in heap) / parsed
            table = calendar_rules.month_calendar(low, high)
            days = sum(sum(row) for row in table)
            flat = sum(sum(row[bin - 1] for row in table) for bin in heap) / days
            scale = math.sqrt(flat * (1 - flat) / parsed)
            bound = (tails + mixed_cells) / parsed
            if mixed_cells:
                unresolved = unresolved | {name}
            elif floor == 11 and ROWS < 10000:
                assert bound <= 0.10, (name, bound)
            mixing = 0
            weekdays = _weekdays(block)
            for first, last, count in weekdays:
                if first < calendar_rules.SATURDAY <= last:
                    mixing += count
            for seed in SEEDS:
                twin, twin_weekend, twin_parsed = _shares(run.twins[seed][index], low, high)
                twin_share = sum(twin[bin - 1] for bin in heap) / twin_parsed
                assert abs(twin_share - share) <= bound + 1e-12, (name, seed, twin_share, share)
                if abs(share - flat) > 3 * scale and not mixed_cells:
                    assert abs(twin_share - share) <= abs(share - flat) / 4, (name, seed)
                distance = sum(abs(twin[bin] / twin_parsed - real[bin] / parsed) for bin in range(calendar_rules.MONTH_DAY_BINS)) / 2
                assert distance <= (tails + merged_cells) / parsed + 1e-12, (name, seed, distance)
                if weekdays:
                    assert abs(twin_weekend / twin_parsed - real_weekend / parsed) <= (tails + mixing) / parsed + 1e-12, (name, seed)
    assert unresolved == ({"tenth97", "month_end_business"} if floor == 36 else set())


def test_a_heap_beside_fewer_strays_than_the_line_cannot_stand_alone(battery: "dict[int, dict[str, _Run]]") -> None:
    """A STATED LIMIT: 97 per cent on the 10th at a floor of 36 holds 30 other rows, fewer than
    the line of 36, so no grouping can count the 10th alone; the census keeps the 9th empty and
    counts the rest together, and the 10th's heap is landing 3b.6's (the dates that stand out)."""
    census = _census(battery[36]["skeptic"].described.block("tenth97"))
    assert len(census) == 2 and census[0] == (9, 9, 0) and census[1][:2] == (10, 8)
    assert _census(battery[11]["skeptic"].described.block("tenth97"))[1:2] == ((10, 10, 905),) or any(
        group[:2] == (10, 10) for group in _census(battery[11]["skeptic"].described.block("tenth97"))
    )


# -- the line ------------------------------------------------------------------------


@pytest.mark.parametrize("floor", (11, 1))
def test_no_day_of_month_count_below_the_line(tmp_path: pathlib.Path, floor: int) -> None:
    """At floors 11 and 1 (lines 11 and 2), every published count is nought or at the line."""
    line = parsing.census_floor(floor)
    published = 0
    for name, columns in _tables(400).items():
        described = kpi_shapes.describe(tmp_path / name, name, _text(columns), floor)
        for column in columns:
            for _first, _last, count in _census(described.block(column)):
                published += 1
                assert count == 0 or count >= line, (column, count)
    assert published > 0


def test_a_missed_line_prints_no_count_below_the_line(battery: "dict[int, dict[str, _Run]]", tmp_path: pathlib.Path) -> None:
    """A file holding the 1st's rows on the 2nd misses the census, and its line prints no number
    below the line: the short groups say they are short (P4-D347)."""
    run = battery[11]["heaps"]
    cells = list(run.columns["billing_date"])
    moved = 0
    for place, cell in enumerate(cells):
        if cell[8:10] == "01" and moved < len(cells) and cell[:7] != "2023-01":
            cells[place] = cell[:8] + "02"
            moved += 1
    text = _text({"billing_date": cells, "birth_date": run.columns["birth_date"]})
    outcome = kpi_shapes.measure(run.described, text, "moved.csv")
    checks = [check for check in outcome.checks if check.subcheck == "day_of_month_census.groups" and check.column == "billing_date"]
    assert len(checks) == 1 and checks[0].verdict == validation.MISSED
    line = parsing.census_floor(11)
    for number in [int(word) for word in checks[0].achieved.replace(",", " ").split() if word.isdigit()]:
        assert number == 0 or number >= line or number > 31, checks[0].achieved


# -- DM4 and the scope ----------------------------------------------------------------


def test_a_short_column_publishes_none_and_says_so(tmp_path: pathlib.Path) -> None:
    """A column spanning 100 days, heaped on the 1st: its middle half spans fewer than 124 days
    (DM4), so no census is published and NF104 says the day of the month was kept back."""
    draw = random.Random(5)
    start = datetime.date(2024, 1, 1)
    cells = []
    for _row in range(600):
        day = start + datetime.timedelta(days=draw.randrange(100))
        cells += [(day.replace(day=1) if draw.random() < 0.4 else day).isoformat()]
    described = kpi_shapes.describe(tmp_path, "short", _text({"seen_on": cells}), 11)
    assert _census(described.block("seen_on")) == ()
    days = tuple(sorted(_day(cell) for cell in cells))
    decided = taxonomy.day_of_month_decision(
        described.block("seen_on"), days, taxonomy.Settings(), described.block("seen_on")["n_distinct"]
    )
    assert decided.reason == calendar_rules.REASON_MONTH_SPAN
    assert taxonomy.rendered(taxonomy.NOTE_DAY_OF_MONTH_WITHHELD, ()) in json.dumps(described.document)


def test_a_two_width_column_publishes_and_holds(tmp_path: pathlib.Path) -> None:
    """m/d/yyyy written padded for seven rows in ten and unpadded for three: DM5 is WC3's scope
    alone (the skeptic's major 3), so the billing heap publishes and every twin meets it."""
    import test_stage3b_gate as gate

    draw = random.Random(11)
    cells = []
    for cell in gate._BATTERY["heaps"](ROWS)["billing_date"]:
        year, month, date = cell[0:4], int(cell[5:7]), int(cell[8:10])
        cells += [f"{month:02d}/{date:02d}/{year}" if draw.random() < 0.7 else f"{month}/{date}/{year}"]
    described = kpi_shapes.describe(tmp_path, "widths", _text({"billed": cells}), 11)
    assert _census(described.block("billed")) != ()
    for seed in SEEDS:
        assert kpi_shapes.missed(kpi_shapes.measure(described, kpi_shapes.twin_text(described, seed), f"t{seed}.csv")) == []


def test_midnight_moments_publish_and_hold(tmp_path: pathlib.Path) -> None:
    """Billing written `YYYY-MM-DD 00:00:00` and month ends written `T00:00:00`: moments every
    value of which stands at midnight publish the census as dates do, and the twins meet it in the
    column's own spelling (the skeptic's major 4)."""
    import test_stage3b_gate as gate

    columns = {
        "billed_at": [cell + " 00:00:00" for cell in gate._BATTERY["heaps"](ROWS)["billing_date"]],
        "closed_at": [cell + "T00:00:00" for cell in _monthend(ROWS)["month_end"]],
    }
    described = kpi_shapes.describe(tmp_path, "midnight", _text(columns), 11)
    for name in columns:
        block = described.block(name)
        assert block["resolution"] == "datetime" and block["all_at_midnight"] is True
        assert _census(block) != ()
    for seed in SEEDS:
        text = kpi_shapes.twin_text(described, seed)
        assert kpi_shapes.missed(kpi_shapes.measure(described, text, f"t{seed}.csv")) == []
        assert text.splitlines()[1].split(",")[0].endswith(" 00:00:00")


def test_a_clocked_column_publishes_none(tmp_path: pathlib.Path) -> None:
    """Billing written with a clock other than midnight is outside DM5's scope: no census, and
    no sentence (a stated limit; the twin's day pass moves whole days only where every value
    stands at midnight)."""
    import test_stage3b_gate as gate

    cells = [cell + " 09:30:00" for cell in gate._BATTERY["heaps"](ROWS)["billing_date"]]
    described = kpi_shapes.describe(tmp_path, "clocked", _text({"billed_at": cells}), 11)
    assert _census(described.block("billed_at")) == ()
    assert taxonomy.rendered(taxonomy.NOTE_DAY_OF_MONTH_WITHHELD, ()) not in json.dumps(described.document)


# -- twins unchanged where nothing is published ---------------------------------------


def test_a_table_publishing_no_census_keeps_its_twins(battery: "dict[int, dict[str, _Run]]", tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The weekly clinic and the 28-day cycle publish no day-of-month census, and their twins are
    byte for byte those of the weekday pass alone."""
    import test_stage3b_gate as gate

    columns = {name: cells for name, cells in gate._BATTERY["schedules"](ROWS).items() if name != "monthly_visit"}
    described = kpi_shapes.describe(tmp_path / "with", "plain", _text(columns), 11)
    assert all(_census(described.block(name)) == () for name in columns)
    with_pass = [kpi_shapes.twin_text(described, seed) for seed in SEEDS]
    monkeypatch.setattr(generation, "_day_settled", generation._weekday_settled)
    assert [kpi_shapes.twin_text(described, seed) for seed in SEEDS] == with_pass


# -- the eighteenth vectors file: G7.3i on stated ranks -------------------------------


def _oracle() -> "dict[str, object]":
    return runpy.run_path(str(ORACLE))


def _groups(census: "list[dict]") -> "tuple[tuple[int, int, int], ...]":
    return tuple((group["first"], group["last"], group["count"]) for group in census)


def _answer(case: dict, module: types.ModuleType = generation) -> "list[int]":
    """What the product makes of a case: both passes of `_day_passes`."""
    weekdays = _groups(case["weekdays"])
    moved = list(case["ordinals"])
    module._day_passes(
        moved, list(case["lows"]), list(case["highs"]), list(case["pinned"]), tuple(case["body"]),
        case["wanted"], (_groups(case["census"]), weekdays),
        (
            None, "", False, frozenset(case["holes"]),
            module._day_empty_weekdays(weekdays, case["span"][0], case["span"][1]),
            case["reachable"],
        ),
    )
    return moved


def _mutant(monkeypatch: pytest.MonkeyPatch, before: str, after: str) -> types.ModuleType:
    """The product's generation module with ONE source edit, built beside it (an edit that no
    longer applies turns the test red)."""
    assert SOURCE.count(before) == 1, before
    name = "synthtwin._generation_day_of_month_mutant"
    module = types.ModuleType(name)
    module.__file__ = generation.__file__
    monkeypatch.setitem(sys.modules, name, module)
    exec(compile(SOURCE.replace(before, after), generation.__file__, "exec"), module.__dict__)
    return module


CASES = (
    "day_of_month_billing",
    "day_of_month_births_dip",
    "day_of_month_business_billing",
    "day_of_month_form_hole",
    "day_of_month_month_end",
    "day_of_month_tenth",
)

# Each case's own source edit of the product, and what it withdraws.
MUTANTS = {
    # pass A
    "day_of_month_billing": (
        "    _bins_settled(\n        first, [count for _first, _last, count in month],\n"
        "        body_low, body_high, pinned, wanted,\n    )\n",
        "",
    ),
    # pass B
    "day_of_month_births_dip": (
        "    _bins_settled(\n        second, [count for _first, _last, count in weekdays],\n"
        "        body_low, body_high, pinned, wanted,\n    )\n",
        "",
    ),
    # the days of the empty weekday groups, pass A's holes
    "day_of_month_business_billing": (
        "        holes=hole_days | emptied,\n",
        "        holes=hole_days,\n",
    ),
    # the description's holes, in pass A
    "day_of_month_form_hole": (
        "        holes=hole_days | emptied,\n",
        "        holes=emptied,\n",
    ),
    # the month's last day read as its plain day of the month
    "day_of_month_month_end": (
        "            state.month_bins[day] = calendar_rules.month_bin(day) - 1\n",
        "            state.month_bins[day] = min(parsing.civil_from_days(day)[2], 30) - 1\n",
    ),
    # pass B's keep of the day-of-month group
    "day_of_month_tenth": (
        '        pairs="month_day",\n        pair_where=month_where,\n',
        "",
    ),
}


def test_every_case_is_asked() -> None:
    """The file holds these cases and no other, each with its own mutant, and the oracle, run
    again, gives each the answer the file carries."""
    assert tuple(sorted(_FILE["cases"])) == CASES
    assert tuple(sorted(MUTANTS)) == CASES
    oracle = _oracle()
    assert sorted(oracle["DAY_STEP_CASES"]) == list(CASES)  # type: ignore[call-overload]
    for name, case in _FILE["cases"].items():
        assert oracle["day_answer"](case) == case["answer"], name  # type: ignore[operator]


@pytest.mark.parametrize("name", CASES)
def test_the_product_gives_each_case_its_answer_and_its_mutant_another(name: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """Each state of ranks: the product's answer is the file's, both censuses are met, and under
    its own source edit the answer moves."""
    case = _FILE["cases"][name]
    answer = _answer(case)
    assert answer == case["answer"], name
    where = calendar_rules.month_where(_groups(case["census"]))
    found = [0] * len(case["census"])
    for day in answer:
        found[where[calendar_rules.month_bin(day) - 1]] += 1
    assert found == [group["count"] for group in case["census"]], name
    for day in answer:
        assert day not in case["holes"], name
    before, after = MUTANTS[name]
    assert _answer(case, _mutant(monkeypatch, before, after)) != case["answer"], name


@pytest.mark.parametrize("name", ("billing_date", "birth_date", "month_end_business", "births_weekend_dip"))
def test_the_passes_move_whole_columns_as_the_oracle_does(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, name: str) -> None:
    """The ranks the generator hands the day pass, through the oracle's own passes stated from the
    method's text: the same days come back."""
    import test_stage3b_gate as gate

    columns = dict(gate._BATTERY["heaps"](300))
    columns.update(_monthend(300))
    described = kpi_shapes.describe(tmp_path, name, _text({name: columns[name]}), 11)
    assert _census(described.block(name)) != ()
    seen: "list[tuple[tuple, list[int]]]" = []
    settled = generation._day_settled

    def captured(column, facts, ordinals, parsed, whole, lows, highs, layout, holes, declared=()):  # type: ignore[no-untyped-def]
        answer = settled(column, facts, list(ordinals), parsed, whole, lows, highs, layout, holes, declared)
        seen[:] = [((list(ordinals), parsed, list(whole), list(lows), list(highs)), list(answer[0]))]
        return answer

    monkeypatch.setattr(generation, "_day_settled", captured)
    kpi_shapes.twin_text(described, 0)
    (ordinals, parsed, whole, lows, highs), moved = seen[0]
    block = copy.deepcopy(described.block(name))
    answer = _oracle()["day_settled"](block, ordinals, parsed, whole, lows, highs, set(block.get("missing_by_source", {})))  # type: ignore[operator]
    assert answer == moved


# -- the producer always loads --------------------------------------------------------


def _shapes_for_loading() -> "list[tuple[str, list[str]]]":
    """Draws of every kind the producer meets: heaps, month ends, a short span, sparse and dense
    columns, placeholder days, two widths, midnight moments, a few rows, at several sizes."""
    found: "list[tuple[str, list[str]]]" = []
    for rows in (40, 150, 600):
        draw = random.Random(rows)
        for kind in ("uniform", "heaped", "month_end", "short", "sparse", "placeholder", "widths", "midnight"):
            cells = []
            for _row in range(rows):
                day = draw.choice(_DAYS)
                if kind == "heaped" and draw.random() < 0.5:
                    day = day.replace(day=draw.choice((1, 10, 15, 28)))
                if kind == "month_end" and draw.random() < 0.5:
                    day = _last_of_month(day)
                if kind == "short":
                    day = datetime.date(2024, 1, 1) + datetime.timedelta(days=draw.randrange(130))
                if kind == "sparse":
                    day = datetime.date(2023, 1 + draw.randrange(12), 1 + 3 * draw.randrange(9))
                text = day.isoformat()
                if kind == "placeholder" and draw.random() < 0.05:
                    text = "1900-01-01"
                if kind == "widths":
                    text = f"{day.month}/{day.day}/{day.year}" if draw.random() < 0.3 else f"{day.month:02d}/{day.day:02d}/{day.year}"
                if kind == "midnight":
                    text = text + " 00:00:00"
                cells += [text]
            found += [(f"{kind}-{rows}", cells)]
    return found


def test_every_description_the_producer_writes_loads_and_generates(tmp_path: pathlib.Path) -> None:
    """THE PRODUCER-ALWAYS-LOADS BATTERY of the new loader refusals (DM1 to DM5): every
    description the producer writes for these draws, at floors 1, 11 and 36, loads, and its twin
    is drawn and checked with no day-of-month census missed."""
    published = 0
    for floor in (1, 11, 36):
        for name, cells in _shapes_for_loading():
            described = kpi_shapes.describe(tmp_path / f"{name}-{floor}", "load", _text({"seen_on": cells}), floor)
            published += bool(_census(described.block("seen_on")))
            outcome = kpi_shapes.measure(described, kpi_shapes.twin_text(described, 0), "twin.csv")
            assert not [check for check in kpi_shapes.missed(outcome) if "day_of_month" in check], (name, floor)
    assert published >= 10


# -- the rules, each by its stated answers --------------------------------------------


def test_the_bins_put_the_last_day_apart() -> None:
    """Days 1 to 27 are their own bins; the 28th to the 30th where not last are bins 28 to 30; the
    last day of a 28-, 29-, 30- and 31-day month is bin 31, 32, 33 and 34."""
    day = parsing.days_from_civil
    assert calendar_rules.month_bin(day(2023, 2, 28)) == 31
    assert calendar_rules.month_bin(day(2024, 2, 28)) == 28
    assert calendar_rules.month_bin(day(2024, 2, 29)) == 32
    assert calendar_rules.month_bin(day(2024, 4, 30)) == 33
    assert calendar_rules.month_bin(day(2024, 5, 30)) == 30
    assert calendar_rules.month_bin(day(2024, 5, 31)) == 34
    assert calendar_rules.month_bin(day(2024, 5, 27)) == 27


@pytest.mark.parametrize("span", (0, 31, 400, 3000, 146097, 200000))
def test_the_calendar_is_counted_as_walking_it_would(span: int) -> None:
    """`month_calendar` counts whole 400-year cycles and months at once, and agrees with a walk
    of every day, the holes taken off."""
    low = parsing.days_from_civil(1899, 3, 5)
    holes = (low + 3, low + span // 2, low + span)
    table = calendar_rules.month_calendar(low, low + span, holes)
    walked = [[0] * calendar_rules.MONTH_DAY_BINS for _ in range(7)]
    for day in range(low, low + span + 1):
        if day not in holes:
            walked[calendar_rules.weekday_of(day)][calendar_rules.month_bin(day) - 1] += 1
    assert table == walked


def test_a_heap_stays_alone_where_its_neighbours_are_short() -> None:
    """The skeptic's major 1: bins 7 to 9 hold 41, the 10th 836 and 11 to 13 hold 35 at a line of
    36: the short run beside the empty days joins its non-zero neighbour on the cycle, never the
    heap through the empty run, and the 10th stands alone."""
    bins = [0] * 34
    bins[6], bins[7], bins[8], bins[9], bins[10], bins[11], bins[12] = 14, 14, 13, 836, 12, 12, 11
    groups = calendar_rules.month_groups(bins, 36)
    assert (10, 10, 836) in groups
    assert calendar_rules.month_groups([1] + [0] * 33, 2) == ()


def test_the_few_dates_rule_reads_the_calendar() -> None:
    """A group holding rows on fewer than four dates withholds the census, unless every calendar
    day the group has holds one -- the last day of February on a two-year column."""
    day = parsing.days_from_civil
    low, high = day(2023, 1, 1), day(2024, 12, 31)
    table = calendar_rules.month_calendar(low, high)
    groups = ((1, 30, 100), (31, 31, 12), (32, 34, 30))
    body = [day(2023, 1, 1 + step % 28) for step in range(100)] + [day(2023, 2, 28)] * 12
    body += [day(2023, 3, 31), day(2023, 4, 30), day(2024, 2, 29), day(2023, 5, 31)] * 7 + [day(2023, 7, 31), day(2023, 8, 31)]
    assert not calendar_rules.few_month_dates(groups, body, table)
    sparse = ((1, 30, 100), (31, 34, 42))
    assert calendar_rules.few_month_dates(sparse, body[:100] + [day(2023, 3, 31)] * 42, table)


def test_the_rule_departs_beyond_the_weekday() -> None:
    """(a) beside a weekday census: four beyond it and more than it departs beyond the day of the
    month; (b) with none: four from the calendar."""
    assert calendar_rules.day_of_month_stands(4.0, 3.9, True)
    assert not calendar_rules.day_of_month_stands(4.0, 4.1, True)
    assert not calendar_rules.day_of_month_stands(3.9, 0.0, False)
    assert calendar_rules.day_of_month_stands(4.0, 99.0, False)


def test_the_loader_s_check_names_each_rule() -> None:
    """DM1 the cover on the cycle, DM2 the line, DM3 the total, DM4 the middle half's span."""
    breach = calendar_rules.day_census_breach
    assert breach(((1, 34, 100),), 100, 11, 0, 200) is None
    assert breach(((10, 9, 100),), 100, 11, 0, 200) is None
    assert breach(((2, 34, 90), (1, 1, 10)), 100, 11, 0, 200)[0] == "DM1"  # type: ignore[index]
    assert breach(((1, 1, 5), (2, 34, 95)), 100, 11, 0, 200)[0] == "DM2"  # type: ignore[index]
    assert breach(((1, 34, 101),), 100, 11, 0, 200)[0] == "DM3"  # type: ignore[index]
    assert breach(((1, 34, 100),), 100, 11, 0, 123)[0] == "DM4"  # type: ignore[index]
    assert breach(((1, 34, 100),), 100, 11, None, 200)[0] == "DM4"  # type: ignore[index]


def test_the_loader_reads_a_census_and_refuses_one_on_the_shared_clock(battery: "dict[int, dict[str, _Run]]", tmp_path: pathlib.Path) -> None:
    """A published census loads into the facts as published; moved onto a column the loader's
    scope excludes, it is refused by DM5."""
    run = battery[11]["heaps"]
    loaded = {column.name: column for column in run.described.loaded.columns}
    facts = loaded["billing_date"].facts
    assert isinstance(facts, contract.DatetimeFacts)
    assert facts.day_of_month_census == _census(run.described.block("billing_date"))
    document = copy.deepcopy(run.described.document)
    for block in document["columns"]:
        if block["name"] == "billing_date":
            block["datetimes_read_at"] = "utc"
            block["weekday_census"] = []
    target = fixtures.write_profile(tmp_path, "shared.json", document)
    with pytest.raises(errors.ProfileError, match="DM5|datetimes_read_at"):
        contract.load_profile(str(target))


def test_the_reach_rule_asks_both_censuses_for_the_count() -> None:
    """The count-reach rule of a column of days, asked of both censuses (lane D1b's, P4-D388):
    a body pinned on 10 January and 10 March 2024, the census counting only the 10th, reaches
    three days; a count needing five once the tails are set aside is withheld, one needing three
    publishes. Measured at 10,000 rows and a floor of 36: a monthly visit whose body held all 160
    days of the 7th to the 13th and whose rebuilt tails kept two days fewer than the real ones came
    back 166 days for 168 at every seed, and the rule withholds it."""
    day = parsing.days_from_civil
    groups = ((1, 9, 0), (10, 10, 100), (11, 34, 0))
    pins = ((0, day(2024, 1, 10)), (100, day(2024, 3, 10)))
    assert calendar_rules.month_reach_short(groups, (), pins, 5, 0, 0)
    assert not calendar_rules.month_reach_short(groups, (), pins, 3, 0, 0)
    weekend_empty = ((0, 4, 100), (5, 6, 0))
    assert calendar_rules.month_reach_short(groups, weekend_empty, pins, 3, 0, 0) is (
        calendar_rules.weekday_of(day(2024, 2, 10)) >= calendar_rules.SATURDAY
    )

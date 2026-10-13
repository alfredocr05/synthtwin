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

* the core holds (G7.3i step 3, the repair round):
  `test_the_core_holds_where_the_joint_plan_cannot`, `test_step_three_moves_a_column_as_the_oracle_does`,
  `test_quarter_ends_at_ten_thousand_rows_keep_their_count` and
  `test_a_group_of_three_dates_withholds_the_census`; and skeptic 1's clauses, each red on its own
  source edit: the reach rule at 10,000 rows, the hole rule, V5-W2's hole clause, the generator's
  deviation and its sentence, the NF102/NF103 choice and the publication guard's two kinds.

* the Codex review (one round), each item red on a3c1b33: item 1, the census as written --
  `test_the_spelling_repair_keeps_the_published_groups` (Codex's 1,200-row table, seeds 0, 2
  and 3), `test_a_census_the_finished_cells_miss_is_named_and_said` (the recount, red with it
  withdrawn), the eighteenth file's repair state and `test_each_clause_of_the_repair_moves_its_answer`;
  item 2, the empty weekdays as a rule -- `test_the_empty_weekdays_grow_with_the_span_not_its_square`
  and `test_the_day_pass_stores_no_empty_weekday_day`; item 3, rows and span apart --
  `test_the_month_bins_keep_no_calendar_span` and `test_the_calendar_prior_is_the_walked_one`;
  item 4, `test_nf104_says_a_possible_cost_or_a_conservative_rule`.

A stated limit, pinned: `test_a_heap_beside_fewer_strays_than_the_line_cannot_stand_alone`
-- 97 per cent on the 10th at a floor of 36 holds 30 other rows, fewer
than the line, so the 10th shares its group (the dates that stand out
are landing 3b.6's). Another, for lane D4: `test_quarter_ends_at_ten_thousand_rows_meet_every_check`,
a strict xfail.

Test-local mutants build the product's module with one source edit (one
`compile` and one `exec` below), as the shared steps' test does; the
oracle is run by path (one `runpy.run_path`).
"""

from __future__ import annotations

import copy
import dataclasses
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
    profile,
    reading,
    rendering,
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


def _skeptic(rows: int, quarter_ends: bool = False) -> "dict[str, list[str]]":
    """The 3b.3 skeptic's untuned shapes (blocker 1 (c)): the 30th and first Mondays, Monday
    billing, sessions, a burst and forty tied dates, each drawn as the skeptic drew it, and 97 per
    cent on the 10th. With `quarter_ends`, the quarter ends drawn beside the first two alone: half
    the rows on the last day of March, June, September and December, the rest any day."""
    closes: "list[str]" = []
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
            year, month = draw.choice([(y, m) for (y, m) in _MONTHS if m in (3, 6, 9, 12)])
            closes += [_last_of_month(datetime.date(year, month, 1)).isoformat()]
        else:
            closes += [draw.choice(_DAYS).isoformat()]
    if quarter_ends:
        return {"quarter_end": closes}
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
                # The loader's own check, on the block's own body and rungs.
                block = run.described.block(name)
                parsed = len([cell for cell in run.columns[name] if cell]) - block["n_unparsed"]
                body = parsed - block["low_tail"]["rows"] - block["high_tail"]["rows"]
                rungs = block["date_percentiles"]
                assert calendar_rules.day_census_breach(census, body, line, _day(rungs["p25"]), _day(rungs["p75"])) is None, name
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
    one, and the twins cannot keep both: before G7.3i step 3 a twin held more different values
    than the column (the skeptic's blocker 1); now the weekday pass's column keeps the count and
    the census published is missed."""
    columns = {"sessions": _skeptic(ROWS)["sessions"]}
    described = kpi_shapes.describe(tmp_path / "with", "sessions", _text(columns), 11)
    assert _census(described.block("sessions")) == ()
    monkeypatch.setattr(calendar_rules, "few_month_dates", lambda groups, body, table: False)
    described = kpi_shapes.describe(tmp_path / "without", "sessions", _text(columns), 11)
    assert _census(described.block("sessions")) != ()
    missed: "set[str]" = set()
    for seed in SEEDS:
        missed = missed | set(kpi_shapes.missed(kpi_shapes.measure(described, kpi_shapes.twin_text(described, seed), f"t{seed}.csv")))
    assert "sessions:day_of_month_census.groups" in missed, sorted(missed)
    assert not any("n_distinct" in check for check in missed), sorted(missed)


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


def _repaired(case: dict, module: types.ModuleType, monkeypatch: pytest.MonkeyPatch) -> "int | str | None":
    """What the product makes of a state of the spelling repair (`_day_repaired_cell`): each
    day's cell is the day's number, `hole` on the days whose cell wears an absent spelling (and
    `hole` comes back where a mutant takes one)."""
    monkeypatch.setattr(module, "_interior_cell", lambda facts, day, *rest: "hole" if day in case["spelled"] else str(day))
    monkeypatch.setattr(module, "_is_a_hole_spelling", lambda text, holes: text == "hole")
    weekdays = _groups(case["weekdays"])
    repair = module._DayRepair(
        month_where=calendar_rules.month_where(_groups(case["census"])),
        week_where=calendar_rules.where_of(weekdays) if weekdays else (),
        days=frozenset(case["holes"]),
        word="",
        widths=False,
        ordinals=list(case["ordinals"]),
    )
    cell = module._day_repaired_cell(
        repair, None, case["ordinals"][case["rank"]], tuple(case["window"]), ("", "", (), False, None)
    )
    if not cell:
        return None
    return int(cell) if cell.isdigit() else cell


def _answer(case: dict, module: types.ModuleType = generation, monkeypatch: "pytest.MonkeyPatch | None" = None) -> "object":
    """What the product makes of a case: both passes of `_day_passes`, or the day the spelling
    repair moves its rank to."""
    if case.get("repair"):
        assert monkeypatch is not None
        return _repaired(case, module, monkeypatch)
    weekdays = _groups(case["weekdays"])
    moved = list(case["ordinals"])
    module._day_passes(
        moved, list(case["lows"]), list(case["highs"]), list(case["pinned"]), tuple(case["body"]),
        case["wanted"], (_groups(case["census"]), weekdays),
        (None, "", False, frozenset(case["holes"]), frozenset(), case["reachable"]),
        (module._day_empty_weekday_numbers(weekdays), case["span"][0], case["span"][1]),
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
    "day_of_month_repair",
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
    # the days of the empty weekday groups, pass A's holes (read as a rule since the Codex
    # review's item 2)
    "day_of_month_business_billing": (
        "        empty_weekdays=empty[0],\n",
        "",
    ),
    # the description's holes, in pass A
    "day_of_month_form_hole": (
        "        holes=hole_days | emptied,\n",
        "        holes=emptied,\n",
    ),
    # the month's last day read as its plain day of the month
    "day_of_month_month_end": (
        "        state.month_bins[day] = calendar_rules.month_bin(day) - 1\n",
        "        state.month_bins[day] = min(parsing.civil_from_days(day)[2], 30) - 1\n",
    ),
    # the spelling repair's keep of the count of different days (the Codex review's item 1)
    "day_of_month_repair": (
        "            if free == alone:\n",
        "            if True:\n",
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
    answer = _answer(case, generation, monkeypatch)
    assert answer == case["answer"], name
    before, after = MUTANTS[name]
    if case.get("repair"):
        assert _answer(case, _mutant(monkeypatch, before, after), monkeypatch) != case["answer"], name
        return
    assert isinstance(answer, list)
    where = calendar_rules.month_where(_groups(case["census"]))
    found = [0] * len(case["census"])
    for day in answer:
        found[where[calendar_rules.month_bin(day) - 1]] += 1
    assert found == [group["count"] for group in case["census"]], name
    for day in answer:
        assert day not in case["holes"], name
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

    def captured(column, facts, ordinals, parsed, whole, lows, highs, layout, holes, declared=(), counted=()):  # type: ignore[no-untyped-def]
        # ``counted``: the days a column of counted dates holds no date on
        # (landing R4, met at batch 3's integration); none on these columns.
        answer = settled(column, facts, list(ordinals), parsed, whole, lows, highs, layout, holes, declared, counted)
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
    # Any other group of fewer than four dates withholds, even holding every one its calendar
    # gives: the 5th of May, June and July 2023 (the repair round's May alone).
    spring = calendar_rules.month_calendar(day(2023, 5, 1), day(2023, 7, 31))
    fifths = [day(2023, 5, 5), day(2023, 6, 5), day(2023, 7, 5)] * 10
    assert calendar_rules.few_month_dates(((1, 4, 0), (5, 5, 30), (6, 34, 0)), fifths, spring)


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
    scope excludes -- moments with a clock, or a tail withheld -- it is refused by DM5. The
    shared clock and the joint member are in scope since landing 3b.7 (plan P4-D378), each
    cell counted on the day it is written on (tests/test_stage3b_shared_clock.py)."""
    run = battery[11]["heaps"]
    loaded = {column.name: column for column in run.described.loaded.columns}
    column = loaded["billing_date"]
    facts = column.facts
    assert isinstance(facts, contract.DatetimeFacts)
    assert facts.day_of_month_census == _census(run.described.block("billing_date"))
    mapping = {"day_of_month_census": run.described.block("billing_date")["day_of_month_census"]}
    for scope in (
        {"resolution": "datetime", "all_at_midnight": False},
        {"low_tail": None},
    ):
        with pytest.raises(errors.ProfileError) as raised:
            contract._day_of_month_census(
                mapping, "here", 11, column.n_present, column.n_distinct, (), (),
                dataclasses.replace(facts, **scope),
            )
        assert contract.INVARIANTS["DM5"] in f"{raised.value}", scope


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


# -- the repair round of landing 3b.3 (skeptic 1's items) -----------------------------


def _decided(block: dict, days: "list[int]", floor: int) -> taxonomy.DayOfMonthDecision:
    """The producer's decision on one described block and its column's parsed days."""
    return taxonomy.day_of_month_decision(
        block, tuple(sorted(days)), taxonomy.Settings(small_cell_floor=floor), block["n_distinct"]
    )


def _mays(years: "range", rows: int, seed: int, weekend: "float | None" = None) -> "list[str]":
    """Days of May alone, written `3 May 2023`, two rows in five moved to the 1st or the 15th;
    with `weekend`, Saturdays and Sundays drawn at that weight. The month names publish every
    other month's day as a hole."""
    draw = random.Random(seed)
    mays = [datetime.date(year, 5, date) for year in years for date in range(1, 32)]
    weights = [(weekend if day.weekday() >= 5 else 1.0) for day in mays] if weekend is not None else []
    cells: "list[str]" = []
    for _row in range(rows):
        day = draw.choices(mays, weights=weights, k=1)[0] if weekend is not None else draw.choice(mays)
        if draw.random() < 0.4:
            day = day.replace(day=draw.choice((1, 15)))
        cells += [f"{day.day} May {day.year}"]
    return cells


def _may_day(cell: str) -> int:
    day = datetime.datetime.strptime(cell, "%d %B %Y").date()
    return parsing.days_from_civil(day.year, day.month, day.day)


@pytest.fixture(scope="module")
def quarter_ends(tmp_path_factory: pytest.TempPathFactory) -> "tuple[kpi_shapes.Described, list[str]]":
    """The skeptic's quarter ends at 10,000 rows and a floor of 11, described, and what its twin at
    seed 0 misses."""
    folder = tmp_path_factory.mktemp("quarter-ends")
    described = kpi_shapes.describe(folder, "quarters", _text(_skeptic(10000, quarter_ends=True)), 11)
    text = kpi_shapes.twin_text(described, 0)
    return described, kpi_shapes.missed(kpi_shapes.measure(described, text, "twin.csv"))


def test_quarter_ends_at_ten_thousand_rows_keep_their_count(quarter_ends: "tuple[kpi_shapes.Described, list[str]]") -> None:
    """Skeptic 1's major 1: at 10,000 rows, half the rows on eight quarter ends, the joint plan
    met both censuses at seed 0 and gave the count of different days way, 717 to 726 of 730 at
    three seeds of five, where the twin before this landing held it. G7.3i step 3 now takes the
    weekday pass's column there: the count and the weekday census hold, and only the day of the
    month, which the twin names given way, is missed. Red where step 3 is withdrawn."""
    described, missed = quarter_ends
    assert _census(described.block("quarter_end")) != ()
    assert missed == ["quarter_end:day_of_month_census.groups"]


@pytest.mark.xfail(strict=True, reason="P4-D368: lane D4 owns the joint fix")
def test_quarter_ends_at_ten_thousand_rows_meet_every_check(quarter_ends: "tuple[kpi_shapes.Described, list[str]]") -> None:
    """A STATED LIMIT, pinned for lane D4 (heavy dates, its joint fix): the quarter ends' twin at
    seed 0 meets every check, its day-of-month census among them."""
    _described, missed = quarter_ends
    assert missed == []


@pytest.fixture(scope="module")
def six_mays(tmp_path_factory: pytest.TempPathFactory) -> "tuple[kpi_shapes.Described, list[str]]":
    """Skeptic 2's column of one month a year at 10,000 rows: six Mays, weekends drawn at 0.4, a
    floor of 11, described, and what its twin at seed 0 misses."""
    folder = tmp_path_factory.mktemp("six-mays")
    described = kpi_shapes.describe(folder, "mays", _text({"visit": _mays(range(2019, 2025), 10000, 1606, 0.4)}), 11)
    text = kpi_shapes.twin_text(described, 0)
    return described, kpi_shapes.missed(kpi_shapes.measure(described, text, "twin.csv"))


def test_one_month_a_year_at_ten_thousand_rows_gives_only_the_day_of_month_way(six_mays: "tuple[kpi_shapes.Described, list[str]]") -> None:
    """Skeptic 2's item 2: six Mays at 10,000 rows publish the census, and G7.3i step 3 takes the
    weekday pass's column (13 of 24 such twins measured): the twin misses the day-of-month census
    alone, named given way, and nothing else."""
    described, missed = six_mays
    assert _census(described.block("visit")) != ()
    assert missed == ["visit:day_of_month_census.groups"]


@pytest.mark.xfail(strict=True, reason="P4-D368: lane D4 owns the joint fix")
def test_one_month_a_year_at_ten_thousand_rows_meets_every_check(six_mays: "tuple[kpi_shapes.Described, list[str]]") -> None:
    """A STATED LIMIT, pinned for lane D4 (heavy dates, its joint fix): the six Mays' twin at seed
    0 meets every check, its day-of-month census among them."""
    _described, missed = six_mays
    assert missed == []


def test_the_core_holds_where_the_joint_plan_cannot(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Found in the repair round: six Mays, weekends drawn at 0.4 and two rows in five on the 1st
    or the 15th, publish the census beside seven weekday groups, and each bin's six dates leave
    pass B too few to move between weekdays: every twin missed the weekday census, which the
    weekday pass alone met at every seed. G7.3i step 3 takes the weekday pass's column, so the
    weekday census and the count hold and the day of the month is named given way (the oracle,
    measured once on this column, moves it alike; its walk of the written width takes minutes,
    so `test_step_three_moves_a_column_as_the_oracle_does` asks it on billing). Red where step 3
    is withdrawn."""
    cells = _mays(range(2019, 2025), 1000, 1600, 0.4)
    described = kpi_shapes.describe(tmp_path, "mays", _text({"visit": cells}), 11)
    block = described.block("visit")
    assert _census(block) != () and _weekdays(block) != ()
    for seed in SEEDS:
        twin = generation.generate(described.loaded, seed)
        outcome = kpi_shapes.measure(described, rendering.twin_csv(twin), f"t{seed}.csv")
        assert kpi_shapes.missed(outcome) == ["visit:day_of_month_census.groups"], seed
        notes = [deviation.note for deviation in twin.deviations if deviation.fact == "day_of_month_census"]
        assert notes == [generation._DAY_OF_MONTH_GIVEN_WAY], seed
    mutant = _mutant(
        monkeypatch,
        "        if kept != joint and kept[0] <= joint[0] and kept[1] <= joint[1]:\n",
        "        if False:\n",
    )
    text = rendering.twin_csv(mutant.generate(described.loaded, 0))
    assert "visit:weekday_census.groups" in kpi_shapes.missed(kpi_shapes.measure(described, text, "mutant.csv"))


def test_step_three_moves_a_column_as_the_oracle_does(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """G7.3i step 3 in the oracle (A-P4-59): the gate's billing at 300 rows, with both joint plans
    stood still so the drawn ranks miss the weekday census, is moved by the product and by the
    oracle onto the weekday pass's days, the same days."""
    import test_stage3b_gate as gate

    cells = gate._BATTERY["heaps"](300)["billing_date"]
    described = kpi_shapes.describe(tmp_path, "billing", _text({"billing_date": cells}), 11)
    block = copy.deepcopy(described.block("billing_date"))
    assert _census(block) != () and _weekdays(block) != ()
    oracle = _oracle()
    monkeypatch.setitem(oracle["day_settled"].__globals__, "day_passes", lambda ordinals, *rest: list(ordinals))  # type: ignore[attr-defined]
    monkeypatch.setattr(generation, "_day_passes", lambda *args: (None, None))
    seen: "list[tuple[tuple, list[int], list]]" = []
    settled = generation._day_settled

    def captured(column, facts, ordinals, parsed, whole, lows, highs, layout, holes, declared=(), counted=()):  # type: ignore[no-untyped-def]
        # ``counted``: the days a column of counted dates holds no date on
        # (landing R4, met at batch 3's integration); none on these columns.
        answer = settled(column, facts, list(ordinals), parsed, whole, lows, highs, layout, holes, declared, counted)
        seen[:] = [((list(ordinals), parsed, list(whole), list(lows), list(highs)), list(answer[0]), answer[1])]
        return answer

    monkeypatch.setattr(generation, "_day_settled", captured)
    kpi_shapes.twin_text(described, 0)
    (ordinals, parsed, whole, lows, highs), moved, notes = seen[0]
    assert moved != ordinals
    assert [note.note for note in notes if note.fact == "day_of_month_census"] == [generation._DAY_OF_MONTH_GIVEN_WAY]
    holes = set(block.get("missing_by_source", {}))
    assert oracle["day_settled"](block, ordinals, parsed, whole, lows, highs, holes) == moved  # type: ignore[operator]
    assert oracle["weekday_settled"](block, ordinals, parsed, whole, lows, highs, holes) == moved  # type: ignore[operator]


@pytest.fixture(scope="module")
def step_three_days(tmp_path_factory: pytest.TempPathFactory) -> "dict[str, object]":
    """The gate's billing at 300 rows: `_day_settled`'s own arguments as the twin at seed 0 asks
    it, the oracle's, and stand-in days of each kind built from the weekday pass's days (which
    meet both the weekday census and the count): `lose` keeps the census and loses one day of the
    count (a body rank moved onto another's date seven days away), `shift` and `shift2` keep the
    count and miss the census (a rank alone on its date moved to an empty date of another weekday
    group, two different ranks)."""
    import test_stage3b_gate as gate

    folder = tmp_path_factory.mktemp("step-three")
    cells = gate._BATTERY["heaps"](300)["billing_date"]
    described = kpi_shapes.describe(folder, "billing", _text({"billing_date": cells}), 11)
    block = copy.deepcopy(described.block("billing_date"))
    seen: "list[tuple[tuple, dict]]" = []
    settled = generation._day_settled

    def captured(*args, **kwargs):  # type: ignore[no-untyped-def]
        seen[:] = [(tuple(list(one) if isinstance(one, list) else one for one in args), dict(kwargs))]
        return settled(*args, **kwargs)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_day_settled", captured)
        kpi_shapes.twin_text(described, 0)
    args, kwargs = seen[0]
    _column, facts, ordinals, parsed, _whole, _lows, _highs, layout = args[:8]
    good = list(generation._weekday_settled(*args, **kwargs)[0])
    body = range(layout.low.rows, parsed - 1 - layout.high.rows + 1)
    weekdays = facts.weekday_census
    where = calendar_rules.where_of(weekdays)

    def missed(days: "list[int]") -> "tuple[bool, bool]":
        found = [0 for _ in weekdays]
        for rank in body:
            found[where[calendar_rules.weekday_of(days[rank])]] += 1
        return found != [count for _first, _last, count in weekdays], len(set(days)) != len(set(ordinals))

    assert weekdays and missed(good) == (False, False)
    alone = [rank for rank in body if good.count(good[rank]) == 1]
    lose = next(
        good[:rank] + [good[other]] + good[rank + 1:]
        for rank in alone for other in body if abs(good[other] - good[rank]) == 7
    )
    shifts = [
        good[:rank] + [good[rank] + step] + good[rank + 1:]
        for rank in alone for step in (1, -1, 2, -2, 3, -3)
        if good[rank] + step not in good
        and where[calendar_rules.weekday_of(good[rank] + step)] != where[calendar_rules.weekday_of(good[rank])]
    ]
    shift, shift2 = shifts[0], next(days for days in shifts if days != shifts[0])
    assert missed(lose) == (False, True) and missed(shift) == missed(shift2) == (True, False)
    return {
        "args": args, "kwargs": kwargs, "block": block, "oracle": _oracle(),
        "good": good, "lose": lose, "shift": shift, "shift2": shift2,
    }


# Each case: the joint plan's days, the weekday pass's, whether the count is reachable, and which
# the column takes (skeptic 2's item 1, (a) to (e)).
STEP_THREE = {
    "a_the_joint_days_lose_only_the_count": ("lose", "good", True, "alone"),
    "b_both_miss_the_weekday_census": ("shift", "shift2", True, "joint"),
    "c_the_alone_days_lose_the_count": ("shift", "lose", True, "joint"),
    "d_the_alone_days_miss_the_weekday_census": ("lose", "shift", True, "joint"),
    "e_the_count_is_not_reachable": ("lose", "good", False, "joint"),
}


@pytest.mark.parametrize("name", sorted(STEP_THREE))
def test_step_three_chooses_as_the_oracle_does(name: str, step_three_days: "dict[str, object]", monkeypatch: pytest.MonkeyPatch) -> None:
    """Skeptic 2's item 1 (A-P4-59): step 3's choice, clause by clause, in the product and in the
    oracle. Both joint plans write stand-in days and both weekday passes return stand-in days;
    the column takes the weekday pass's days only where the joint days miss the weekday census
    or a reachable count, and the alone days miss neither where the joint days met it and meet
    one they missed. Each clause of the choice -- `kept != joint`, the weekday's `<=`, the
    count's `<=`, the trigger's `or`, the count asked only where reachable -- is red on its own
    edit in either."""
    joint_name, alone_name, reachable, expected = STEP_THREE[name]
    days = step_three_days
    joint, alone = list(days[joint_name]), list(days[alone_name])  # type: ignore[call-overload]
    wanted = alone if expected == "alone" else joint

    def joint_passes(moved, *rest):  # type: ignore[no-untyped-def]
        moved[:] = list(joint)
        return None, None

    monkeypatch.setattr(generation, "_day_passes", joint_passes)
    monkeypatch.setattr(generation, "_weekday_settled", lambda *args, **kwargs: (list(alone), []))
    monkeypatch.setattr(generation, "_day_found", lambda *args: True)
    monkeypatch.setattr(generation, "_day_body_full", lambda *args: False)
    monkeypatch.setattr(contract, "datetime_counts_reachable", lambda column: reachable)
    moved, notes = generation._day_settled(*days["args"], **days["kwargs"])  # type: ignore[arg-type]
    oracle = days["oracle"]
    scope = oracle["day_settled"].__globals__  # type: ignore[index]
    monkeypatch.setitem(scope, "day_passes", lambda *args: list(joint))
    monkeypatch.setitem(scope, "weekday_settled", lambda *args: list(alone))
    monkeypatch.setitem(scope, "date_counts_reachable", lambda column: reachable)
    _column, _facts, ordinals, parsed, whole, lows, highs = days["args"][:7]  # type: ignore[index]
    block = days["block"]
    holes = set(block.get("missing_by_source", {}))  # type: ignore[attr-defined]
    told = oracle["day_settled"](block, ordinals, parsed, whole, lows, highs, holes)  # type: ignore[index]
    assert moved == told == wanted
    given = [note.note for note in notes if note.fact == "day_of_month_census"]
    assert given == ([generation._DAY_OF_MONTH_GIVEN_WAY] if expected == "alone" else [])


def test_the_few_dates_rule_counts_only_a_month_s_last_day_by_its_calendar() -> None:
    """Skeptic 2's item 1, the few-dates rule's calendar clause: a group holding every date its
    calendar gives on fewer than four stands only where it counts a month's last day alone (bins
    31 to 34, never wrapping). The 30th of May three years running, the 30th's own group or one
    running on to the last day, and the 1st in a group wrapping from the last day, each still
    withholds."""
    day = parsing.days_from_civil

    def table(dates: "list[int]") -> "list[list[int]]":
        total = [[0] * calendar_rules.MONTH_DAY_BINS for _ in range(7)]
        for date in dates:
            for weekday, row in enumerate(calendar_rules.month_calendar(date, date)):
                total[weekday] = [one + two for one, two in zip(total[weekday], row)]
        return total

    thirtieths = [day(year, 5, 30) for year in (2022, 2023, 2024)]
    assert calendar_rules.few_month_dates(((1, 29, 0), (30, 30, 30), (31, 34, 0)), thirtieths * 10, table(thirtieths))
    assert calendar_rules.few_month_dates(((1, 29, 0), (30, 34, 30)), thirtieths * 10, table(thirtieths))
    firsts = [day(year, 5, 1) for year in (2022, 2023, 2024)]
    assert calendar_rules.few_month_dates(((2, 30, 0), (31, 1, 30)), firsts * 10, table(firsts))
    lasts = [day(year, 5, 31) for year in (2022, 2023, 2024)]
    assert not calendar_rules.few_month_dates(((1, 30, 0), (31, 34, 30)), lasts * 10, table(lasts))


def test_a_group_of_three_dates_withholds_the_census(tmp_path: pathlib.Path) -> None:
    """Three Mays heaped on the 1st and the 15th: every bin holds its three dates, every one its
    calendar gives, but only a month's last day may stand on fewer than four, so no census is
    published, NF104 says so and the twins miss nothing. With the calendar clause on every group
    the census published and every twin missed the weekday census."""
    cells = _mays(range(2022, 2025), 1000, 21)
    described = kpi_shapes.describe(tmp_path, "mays", _text({"visit": cells}), 11)
    block = described.block("visit")
    assert _census(block) == () and _weekdays(block) != ()
    assert _decided(block, [_may_day(cell) for cell in cells], 11).reason == calendar_rules.REASON_MONTH_FEW_DATES
    assert taxonomy.rendered(taxonomy.NOTE_DAY_OF_MONTH_WITHHELD, ()) in json.dumps(described.document)
    for seed in SEEDS:
        assert kpi_shapes.missed(kpi_shapes.measure(described, kpi_shapes.twin_text(described, seed), f"t{seed}.csv")) == []


def test_four_mays_at_a_floor_of_36_withhold_the_census(tmp_path: pathlib.Path) -> None:
    """Skeptic 2's item 3, the few-dates rule's stated price: four Mays at 1,000 rows and a floor
    of 36 heap on the 1st and the 15th, and the 1st's group holds three body dates, every one its
    calendar gives (the low tail takes the first year's 1st). Before the repair round the census
    published 12 groups and every twin met it; the rule now keeps it back (NF104), and the twin
    still misses nothing. Red where every group may stand on its calendar again."""
    cells = _mays(range(2021, 2025), 1000, 1604, 1.0)
    described = kpi_shapes.describe(tmp_path, "mays", _text({"visit": cells}), 36)
    block = described.block("visit")
    assert _census(block) == ()
    assert _decided(block, [_may_day(cell) for cell in cells], 36).reason == calendar_rules.REASON_MONTH_FEW_DATES
    assert kpi_shapes.missed(kpi_shapes.measure(described, kpi_shapes.twin_text(described, 0), "t0.csv")) == []


def test_the_reach_rule_withholds_the_monthly_visit_at_ten_thousand_rows(tmp_path: pathlib.Path) -> None:
    """Skeptic 1's item 2a, the rule as measured: at 10,000 rows and a floor of 36 the gate's
    monthly visit departs, and the count-reach rule keeps its census back with NF104. Red where
    the producer no longer asks the rule."""
    import test_stage3b_gate as gate

    cells = gate._BATTERY["schedules"](10000)["monthly_visit"]
    described = kpi_shapes.describe(tmp_path, "visit", _text({"monthly_visit": cells}), 36)
    block = described.block("monthly_visit")
    assert _census(block) == ()
    assert _decided(block, [_day(cell) for cell in cells if cell], 36).reason == calendar_rules.REASON_MONTH_REACH
    assert taxonomy.rendered(taxonomy.NOTE_DAY_OF_MONTH_WITHHELD, ()) in json.dumps(described.document)


def test_a_body_day_on_a_published_hole_withholds_the_census(battery: "dict[int, dict[str, _Run]]") -> None:
    """Item 2b: billing's own block decides its published census; with one of its body days named
    an absent spelling, that day is a published hole the body stands on, and the census is kept
    back. Red where the producer no longer asks the hole rule."""
    run = battery[11]["heaps"]
    cells = [cell for cell in run.columns["billing_date"] if cell]
    block = run.described.block("billing_date")
    days = [_day(cell) for cell in cells]
    assert _decided(block, days, 11).groups == _census(block) != ()
    middle = sorted(cells)[len(cells) // 2]
    decided = _decided(dict(block, missing_by_source={middle: 1}), days, 11)
    assert decided.groups == () and decided.reason == calendar_rules.REASON_MONTH_HOLE


def test_a_file_with_a_body_date_on_a_hole_misses_the_census(tmp_path: pathlib.Path) -> None:
    """Item 2c, V5-W2's hole clause: ten Mays written `3 May 2020` publish every other month's day
    as a hole. A file moving one body date from 3 May 2020 to 3 April 2020 keeps every
    day-of-month count -- the same bin -- and the census is MISSED, its line saying why. Red where
    the validator counts no hole."""
    cells = _mays(range(2015, 2025), 1000, 1070)
    described = kpi_shapes.describe(tmp_path, "mays", _text({"visit": cells}), 11)
    assert _census(described.block("visit")) != ()
    moved = list(cells)
    moved[moved.index("3 May 2020")] = "3 April 2020"
    outcome = kpi_shapes.measure(described, _text({"visit": moved}), "moved.csv")
    [check] = [check for check in outcome.checks if check.subcheck == "day_of_month_census.groups"]
    assert check.verdict == validation.MISSED and check.achieved == check.published, check
    assert any("days its description holds no value on" in line for line in check.note), check.note


def test_a_census_the_twin_misses_is_named_and_said(battery: "dict[int, dict[str, _Run]]", monkeypatch: pytest.MonkeyPatch) -> None:
    """Item 2e: with the generator told no census holds, the twin names the day-of-month census
    among its deviations, and the column's sentence on its spread says it is missed, never met.
    Red where either is withdrawn."""
    run = battery[11]["heaps"]
    monkeypatch.setattr(generation, "_day_found", lambda *args: False)
    twin = generation.generate(run.described.loaded, 0)
    notes = [d.note for d in twin.deviations if d.column == "billing_date" and d.fact == "day_of_month_census"]
    assert notes == [generation._DAY_OF_MONTH_MISSED]
    said = [r.note for r in twin.remarks if r.column == "billing_date" and r.subject == generation._SPREAD_SUBJECT]
    assert len(said) == 1 and generation._SPREAD_DAY_OF_MONTH_MISSED in said[0], said


def test_each_published_census_says_how_it_counts(battery: "dict[int, dict[str, _Run]]", tmp_path: pathlib.Path) -> None:
    """Item 2f: a published census says NF102 where every group holding rows is one bin and NF103
    where some hold neighbouring bins together: every census of the battery holds some days
    together, and ten Mays count each day. Red where the choice is withdrawn."""
    said: "set[str]" = set()
    mays = kpi_shapes.describe(tmp_path, "mays", _text({"visit": _mays(range(2015, 2025), 1000, 1070)}), 11)
    for floor in FLOORS:
        line = parsing.census_floor(floor)
        each = taxonomy.rendered(taxonomy.REMARK_DAY_OF_MONTH_EACH, (line,))
        together = taxonomy.rendered(taxonomy.REMARK_DAY_OF_MONTH_TOGETHER, (line,))
        described = [run.described for run in battery[floor].values()] + ([mays] if floor == 11 else [])
        for one in described:
            for name in [block["name"] for block in one.document["columns"] if block["role"] == "datetime"]:
                block = one.block(name)
                census = _census(block)
                if not census:
                    assert each not in block["remarks"] and together not in block["remarks"], name
                    continue
                merged = any(count > 0 and first != last for first, last, count in census)
                assert (together if merged else each) in block["remarks"], (name, floor)
                assert (each if merged else together) not in block["remarks"], (name, floor)
                said = said | {"NF103" if merged else "NF102"}
    assert said == {"NF102", "NF103"}


def test_the_publication_guard_refuses_a_bin_off_the_cycle_and_a_count_below_the_line(battery: "dict[int, dict[str, _Run]]") -> None:
    """Item 2g: the producer's own guard passes billing's description and refuses it with a group
    counting 5 at a floor of 11, or a group's bin at 35 or 0. Red where either kind accepts
    anything."""
    document = battery[11]["heaps"].described.document
    profile.check_publication(copy.deepcopy(document))
    for key, value in (("count", 5), ("last", 35), ("first", 0)):
        changed = copy.deepcopy(document)
        for block in changed["columns"]:
            if block["name"] == "billing_date":
                block["day_of_month_census"][0][key] = value
        with pytest.raises(errors.ProfileError):
            profile.check_publication(changed)


# -- the Codex review of landing 3b.3 -------------------------------------------------


def _codex_table() -> str:
    """Codex's item 1: 800 padded month-first dates on the 1st or the 15th over twenty years from
    2010 and 400 copies of `1/1/2020`, beside 1,180 ISO dates and 20 cells of the declared missing
    spelling `01/01/2020`."""
    draw = random.Random(6)
    start = datetime.date(2010, 1, 1)
    first: "list[str]" = []
    for _row in range(800):
        day = start + datetime.timedelta(days=draw.randrange(7300))
        day = day.replace(day=draw.choice([1, 15]))
        first += [f"{day.month:02d}/{day.day:02d}/{day.year}"]
    first += ["1/1/2020"] * 400
    second = [(datetime.date(2021, 1, 1) + datetime.timedelta(days=step % 900)).isoformat() for step in range(1180)]
    second += ["01/01/2020"] * 20
    return _text({"a": first, "b": second})


@pytest.fixture(scope="module")
def codex_missing(tmp_path_factory: pytest.TempPathFactory) -> kpi_shapes.Described:
    """Codex's item 1 table described at a floor of 11 with `01/01/2020` declared missing."""
    folder = tmp_path_factory.mktemp("codex-missing")
    table = fixtures.write(folder, "codex.csv", _codex_table())
    settings = taxonomy.Settings(small_cell_floor=11, declared_missing_values=("01/01/2020",))
    document = profile.build_document(reading.read_table(str(table), small_cell_floor=11), settings, [], [], [])
    written = fixtures.write_profile(folder, "codex-profile.json", document)
    return kpi_shapes.Described(folder, table, document, contract.load_profile(str(written)))


def _spread_of(twin: generation.Twin, name: str) -> generation.Remark:
    [said] = [remark for remark in twin.remarks if remark.column == name and remark.subject == generation._SPREAD_SUBJECT]
    return said


@pytest.mark.parametrize("seed", (0, 2, 3))
def test_the_spelling_repair_keeps_the_published_groups(codex_missing: kpi_shapes.Described, seed: int) -> None:
    """Codex's item 1 (High): the census [809, 0, 368, 0] is met by the day pass, and the spelling
    repair then moved a 1st of January written `01/01/2020` to the 31st of December, so seeds 0,
    2, 3, 5, 6, 8 and 9 came back [808, 0, 368, 1], V5-W2 MISSED, while generation named nothing
    and said the counts were met. The repair now takes the nearest day keeping the rank's
    published groups (`_day_repaired_cell`): V5-W2 holds and the sentence says met. Red on
    a3c1b33."""
    assert _census(codex_missing.block("a")) == ((1, 1, 809), (2, 14, 0), (15, 15, 368), (16, 34, 0))
    missed = kpi_shapes.missed(kpi_shapes.measure(codex_missing, kpi_shapes.twin_text(codex_missing, seed), f"t{seed}.csv"))
    assert "a:day_of_month_census.groups" not in missed, missed
    twin = generation.generate(codex_missing.loaded, seed)
    assert [d for d in twin.deviations if d.column == "a" and d.fact == "day_of_month_census"] == []
    assert generation._SPREAD_DAY_OF_MONTH_MET in _spread_of(twin, "a").held


def test_a_census_the_finished_cells_miss_is_named_and_said(codex_missing: kpi_shapes.Described, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 1, the recount: with the repair moving cells as it did before (no day keeping
    the groups), the finished cells miss the census at seed 0, and generation now names it
    (`_day_of_month_count_notes`) and the sentence says missed, as V5-W2 does. Red on a3c1b33,
    and red here with the recount withdrawn (nothing named, the sentence says met)."""
    monkeypatch.setattr(generation, "_day_repaired_cell", lambda *args: "")
    missed = kpi_shapes.missed(kpi_shapes.measure(codex_missing, kpi_shapes.twin_text(codex_missing, 0), "t0.csv"))
    assert "a:day_of_month_census.groups" in missed, missed
    twin = generation.generate(codex_missing.loaded, 0)
    notes = [d.note for d in twin.deviations if d.column == "a" and d.fact == "day_of_month_census"]
    assert notes == [generation._DAY_OF_MONTH_MISSED]
    said = _spread_of(twin, "a")
    assert generation._SPREAD_DAY_OF_MONTH_MISSED in said.note and generation._SPREAD_DAY_OF_MONTH_MET not in said.held
    monkeypatch.setattr(generation, "_day_of_month_count_notes", lambda *args: [])
    silent = generation.generate(codex_missing.loaded, 0)
    assert [d for d in silent.deviations if d.column == "a" and d.fact == "day_of_month_census"] == []
    assert generation._SPREAD_DAY_OF_MONTH_MET in _spread_of(silent, "a").held


@pytest.mark.parametrize(
    "before, after",
    (
        # the day-of-month group
        ("            if repair.month_where[calendar_rules.month_bin(other) - 1] != month:\n", "            if False:\n"),
        # the weekday group
        ("            if repair.week_where and repair.week_where[calendar_rules.weekday_of(other)] != week:\n", "            if False:\n"),
        # the holes
        ("            if other < low or other > high or other in repair.days:\n", "            if other < low or other > high:\n"),
        # the absent spellings
        ("            if _is_a_hole_spelling(tried, holes):\n                continue\n            free =", "            free ="),
    ),
)
def test_each_clause_of_the_repair_moves_its_answer(before: str, after: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """The repair's state in the eighteenth file under each other clause's source edit: the day
    of the month's group, the weekday's, the holes and the absent spellings each turn the answer."""
    case = _FILE["cases"]["day_of_month_repair"]
    assert _answer(case, generation, monkeypatch) == case["answer"]
    assert _answer(case, _mutant(monkeypatch, before, after), monkeypatch) != case["answer"]


def _wide(shape: str, rows: int, first: int, last: int) -> "list[str]":
    """Codex's items 2 and 3: ISO dates over years `first` to `last`, seven in ten on the 1st or
    the 15th; `business`, no weekend day."""
    draw = random.Random(3)
    cells: "list[str]" = []
    while len(cells) < rows:
        year, month = draw.randint(first, last), draw.randint(1, 12)
        length = calendar_rules.month_length(year, month)
        day = datetime.date(year, month, draw.choice((1, 15)) if draw.random() < 0.7 else draw.randint(1, length))
        if shape == "business" and day.weekday() >= 5:
            continue
        cells += [f"{day.year:04d}-{day.month:02d}-{day.day:02d}"]
    return cells


def _pass_a(described: kpi_shapes.Described, monkeypatch: pytest.MonkeyPatch) -> "tuple[generation._WeekdayPass, int, str]":
    """Pass A's state, the generator's traced peak in bytes and the twin's text, at seed 0."""
    import tracemalloc

    states: "list[generation._WeekdayPass]" = []
    passes = generation._day_passes

    def captured(*args, **kwargs):  # type: ignore[no-untyped-def]
        found = passes(*args, **kwargs)
        states[:] = [found[0]]
        return found

    monkeypatch.setattr(generation, "_day_passes", captured)
    tracemalloc.start()
    try:
        text = kpi_shapes.twin_text(described, 0)
        _now, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return states[0], peak, text


def test_the_empty_weekdays_grow_with_the_span_not_its_square() -> None:
    """Codex's item 2 (Medium), the calendar-span growth check: `found = found | {day}` copied
    every day collected before it, 0.26, 1.02 and 3.98 CPU seconds over 40,000, 80,000 and
    160,000 days on a3c1b33 (a span four times as long, fifteen times the work). Grown in place,
    four times the span is at most eight times the work. Red on a3c1b33."""
    import time

    weekdays = ((0, 4, 5), (5, 6, 0))

    def took(span: int) -> float:
        best = math.inf
        for _round in range(3):
            start = time.perf_counter()
            found = generation._day_empty_weekdays(weekdays, 0, span - 1)
            best = min(best, time.perf_counter() - start)
        assert len(found) == len([day for day in range(span) if (day + 3) % 7 >= 5])
        return best

    assert took(160000) < 8 * took(40000) + 0.01


def test_the_day_pass_stores_no_empty_weekday_day(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 2: a 1,000-row business-day column over years 0001 to 2000, seven in ten on
    the 1st or the 15th, publishes both censuses, its weekend empty, and its body asked 202,436
    weekend holes, each collected by copying the ones before (20.49 billion entries). The pass
    now reads the empty weekdays as a rule (`_WeekdayPass.empty_weekdays`) and never collects
    them: the twin meets both censuses with no hole stored and a traced peak under 16 MB. Red on
    a3c1b33, whose day pass asks `_day_empty_weekdays` over the whole span."""
    described = kpi_shapes.describe(tmp_path, "wide", _text({"visit": _wide("business", 1000, 1, 2000)}), 11)
    block = described.block("visit")
    assert _census(block) != () and _weekdays(block)[-1] == (5, 6, 0)

    def refused(*args: object) -> None:
        raise AssertionError("the day pass collected the empty weekdays' days")

    monkeypatch.setattr(generation, "_day_empty_weekdays", refused)
    state, peak, text = _pass_a(described, monkeypatch)
    assert state.holes == frozenset() and state.empty_weekdays == frozenset({5, 6})
    assert peak < 16_000_000, peak
    assert kpi_shapes.missed(kpi_shapes.measure(described, text, "t0.csv")) == []


def test_the_month_bins_keep_no_calendar_span(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 3 (Medium), rows and span measured apart: on a3c1b33 a 1,000-row column over
    years 0001 to 2000, seven in ten on the 1st or the 15th, every weekday group non-zero, kept
    713,670 days in `month_bins` (85.7 MB traced peak) against 35,678 for 1,000 rows over 1901 to
    2000: pass A's prior asked every day of every gap. The prior is now counted by the calendar
    past `_MONTH_DAY_WALKED` days and the memo holds at most `_MONTH_BINS_HELD`: the same rows
    over twenty times the span keep no more than twice the peak, and the twin is the same with
    the memo cut to 64 days. Red on a3c1b33."""
    peaks = {}
    kept = {}
    for first in (1901, 1):
        described = kpi_shapes.describe(tmp_path / str(first), "wide", _text({"visit": _wide("plain", 1000, first, 2000)}), 11)
        assert _census(described.block("visit")) != ()
        state, peaks[first], text = _pass_a(described, monkeypatch)
        kept[first] = len(state.month_bins)
    assert peaks[1] < 2 * peaks[1901] + 1_000_000, (peaks, kept)
    assert max(kept.values()) <= generation._MONTH_BINS_HELD, kept
    monkeypatch.setattr(generation, "_MONTH_BINS_HELD", 64)
    assert _pass_a(described, monkeypatch)[2] == text


def test_the_calendar_prior_is_the_walked_one() -> None:
    """Codex's items 2 and 3: the prior counted by the calendar, with the empty weekdays read as a
    rule, gives every gap the shares the walk over stated holes gives -- gaps of one day, gaps
    ending on a hole or on an empty weekday, gaps across leap years and centuries."""
    draw = random.Random(368)
    census = ((1, 1, 30), (2, 14, 0), (15, 15, 20), (16, 30, 11), (31, 34, 12))
    where = calendar_rules.month_where(census)
    low, high = parsing.days_from_civil(1890, 3, 1), parsing.days_from_civil(2110, 2, 27)
    holes = frozenset(draw.randrange(low, high) for _ in range(300))
    emptied = frozenset(day for day in range(low, high + 1) if (day + 3) % 7 in (5, 6))

    def state(stated: "frozenset[int]", empty: "frozenset[int]") -> generation._WeekdayPass:
        return generation._WeekdayPass(
            moved=[], held={}, where=where, facts=None, word="", widths=False, kinds={},  # type: ignore[arg-type]
            holes=stated, lows=[], highs=[], keep_units=False, bins="month_day", period=0,
            empty_weekdays=empty, empty_low=low, empty_high=high,
        )

    walked = state(holes | emptied, frozenset())
    counted = state(holes, frozenset({5, 6}))
    gaps = [(day, day) for day in (low, high, min(holes), min(emptied))]
    gaps += [(min(holes), min(holes) + 3000), (low - 40, low + 5), (low, high)]
    for _gap in range(12):
        first = draw.randrange(low - 100, high)
        gaps += [(first, min(high + 100, first + draw.choice((2, 30, 1500, 40000))))]
    for first, last in gaps:
        assert generation._weekday_prior(counted, first, last, len(census)) == generation._weekday_prior(
            walked, first, last, len(census)
        ), (first, last)


def test_nf104_says_a_possible_cost_or_a_conservative_rule(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 4 (Medium): four Mays 2021 to 2024, 1,000 rows, source seed 1604, two in five
    moved to the 1st or the 15th, a floor of 36: the few-dates rule withholds the census, and
    NF104 said counting the days WOULD cost the twin its count of different values or its
    weekday counts. With that rule alone set aside the census publishes 12 groups the twins meet
    with nothing missed, so the rule is a conservative exclusion, not an established loss, and
    NF104 now says so. Red on a3c1b33."""
    said = taxonomy.rendered(taxonomy.NOTE_DAY_OF_MONTH_WITHHELD, ())
    assert "would cost" not in said
    assert "could cost" in said and "conservative rule" in said and "too few different dates" in said
    cells = _mays(range(2021, 2025), 1000, 1604, 1.0)
    monkeypatch.setattr(calendar_rules, "few_month_dates", lambda *args: False)
    described = kpi_shapes.describe(tmp_path, "mays", _text({"visit": cells}), 36)
    assert len(_census(described.block("visit"))) == 12
    for seed in (0, 1):
        assert kpi_shapes.missed(kpi_shapes.measure(described, kpi_shapes.twin_text(described, seed), f"t{seed}.csv")) == []

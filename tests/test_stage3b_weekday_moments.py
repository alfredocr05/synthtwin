"""THE WEEKDAY CENSUS OF A COLUMN OF MOMENTS (stage 3b landing D2, plan P4-D367).

A column of dates and times read on the local clock publishes the
weekday census a column of whole dates does: its body -- the cells
between the two tail boundaries, both included, compared as INSTANTS --
counted on the weekday of each cell's day, in the groups of the menu
(contract WC1 to WC4, WC3 widened). Before this landing it published
`weekday_census: []`, and its twin drew every gap evenly: clinic visits
on weekdays alone came back 24 to 31 per cent on weekends. Two rules
more than a column of dates, one fewer: the middle half spans at least
four weeks (WC10, loader and producer), the body holds at least eight
different WRITTEN units a non-empty group on average where two or more
are non-empty (the few-units rule, producer-only, the 3b.2-W skeptic's
blocker 1), and WC6's half on written forms is not asked -- the count of
different values counts instants there. Every withholding but one
without tails is said in NF74's sentence. The generator moves a moment
by whole days, keeping its clock (G7.3f over a unit of 86,400 seconds);
where its clock stands outside its gap on the gap's end day, step 7c
lets it take another clock there, and where the kept clocks of few days
meet and leave the count of different values short, step 8.7 puts it
back at another clock on each moment's own day. The validator counts the
file's moments by instant (V5-W1).

The gate's clauses, each beside the mutant that turns it red:

* G-D1, what publishes: `test_moments_publish_their_census_where_the_rules_allow`
  -- clinic visits, emergency arrivals, admissions, Wednesday sessions,
  admissions at midnight and a business log publish; seven sessions,
  forty ties and payroll at a fixed clock, a clinic over three weeks
  and a column on the shared clock do not, the first four with NF74.
  Mutants: the few-dates and few-units rules withdrawn (the fixed
  clocks publish), the span rule withdrawn (three weeks publishes);
* G-D2, every published census met:
  `test_every_published_census_is_met_by_its_twins_and_its_source` --
  three twins each, nothing MISSED, the weekend share of the body as
  the real column's to within a hundredth, and the source table meets
  its own description. Mutant: the validator counting by day, where a
  boundary's day holds tail cells before its instant
  (`test_the_validator_counts_moments_by_instant`);
* G-D3, a clock changes only where step 7c, 8.4 at another clock, 8.5
  or 8.7 moved it (`test_a_clock_changes_only_on_ranks_steps_7c_8_4_8_5_or_8_7_moved`),
  the 3b.2-W skeptic's minor 2: the bound is the cells those steps
  moved, never a share of the body;
* G-D4, the mutants: the few-units rule keyed to `all_at_midnight`
  (`test_the_few_units_rule_is_asked_off_midnight_too`), step 7c
  withdrawn (`test_wednesday_sessions_need_step_7c`), step 8.7 withdrawn
  (`test_a_short_count_is_put_back_on_each_moments_own_day`: 2,400
  visits on seven Wednesdays, minutes from 07:00 to 19:59, miss their
  count of different values), and each clause of steps 7c and 8.7 on
  the seventeenth vectors file's states;
* the seventeenth file (`tests/reference/generation-branch-vectors-17.json`):
  `test_every_case_is_asked` and one test a case, each red on its own
  source edit of the product;
* the product against the oracle on whole columns:
  `test_the_pass_moves_whole_columns_as_the_oracle_does`;
* the loader: `test_the_loader_reads_a_census_of_moments_and_holds_it_to_wc10`;
* the report: `test_a_count_the_pass_leaves_off_is_counted_in_values`
  (the 3b.2-W skeptic's minor 1);
* the workbook: `test_a_workbook_storing_moments_two_ways_publishes_no_census`
  (WC6's storage half, kept on moments).
"""

from __future__ import annotations

import collections
import copy
import datetime
import json
import pathlib
import random
import runpy
import sys
import types

import pytest

import fixtures
import kpi_shapes
import workbooks
from synthtwin import (
    calendar_rules,
    contract,
    errors,
    generation,
    parsing,
    profile,
    reading,
    taxonomy,
    validation,
)

REPOSITORY = pathlib.Path(__file__).resolve().parent.parent
VECTORS = REPOSITORY / "tests" / "reference" / "generation-branch-vectors-17.json"
ORACLE = REPOSITORY / "tools" / "reference" / "make_generation_reference_vectors.py"
SOURCE = pathlib.Path(generation.__file__).read_text(encoding="utf-8")
DAY = 86400
FLOOR = 11
NOTE_NF74 = "and why is not said"

_FILE = json.loads(VECTORS.read_text(encoding="utf-8"))


# -- the battery, every cell built at runtime from a fixed seed -------------------

_YEAR = [datetime.date(2023, 1, 1) + datetime.timedelta(days=step) for step in range(365)]
_TWO_YEARS = [datetime.date(2023, 1, 1) + datetime.timedelta(days=step) for step in range(731)]


def _at(day: datetime.date, hours: int, minutes: int, seconds: int = 0) -> datetime.datetime:
    return datetime.datetime(day.year, day.month, day.day, hours, minutes, seconds)


def _weighted_days(draw: random.Random, span: "list[datetime.date]", weights: "tuple[float, ...]", rows: int) -> "list[datetime.date]":
    return draw.choices(span, weights=[weights[day.weekday()] for day in span], k=rows)


def _clinic(rows: int = 1000, seed: int = 671, span: "list[datetime.date] | None" = None) -> "list[str]":
    """Weekday appointments, 08:00 to 16:45, most on the quarter hour (`2023/03/17 09:30`)."""
    draw = random.Random(seed)
    found: "list[str]" = []
    for day in _weighted_days(draw, span or _YEAR, (1.0, 1.2, 1.0, 1.1, 0.9, 0.0, 0.0), rows):
        minute = draw.choice((0, 15, 30, 45)) if draw.random() < 0.8 else draw.randrange(60)
        found += [_at(day, draw.randrange(8, 17), minute).strftime("%Y/%m/%d %H:%M")]
    return found


def _emergency(rows: int = 1000, seed: int = 672) -> "list[str]":
    """Arrivals every day of a year, a mild Monday peak (`2023-03-17T14:05`)."""
    draw = random.Random(seed)
    found: "list[str]" = []
    for day in _weighted_days(draw, _YEAR, (1.12, 1.03, 1.0, 0.98, 0.98, 0.94, 0.95), rows):
        found += [_at(day, draw.randrange(24), draw.randrange(60)).strftime("%Y-%m-%dT%H:%M")]
    return found


def _laboratory(rows: int = 1000, seed: int = 679) -> "list[str]":
    """Draws every day of a year, fewer at weekends, month first with unpadded fields
    (`3/7/2023 6:42`), so a day's width kind is the pass's to keep."""
    draw = random.Random(seed)
    found: "list[str]" = []
    for day in _weighted_days(draw, _YEAR, (1.1, 1.05, 1.05, 1.05, 1.05, 0.7, 0.65), rows):
        moment = _at(day, draw.choice((6, 7, 7, 8, 9, 10, 13, 15)), draw.randrange(60))
        found += [f"{moment.month}/{moment.day}/{moment.year} {moment.hour:02d}:{moment.minute:02d}"]
    return found


def _admissions(rows: int = 1000, seed: int = 673, midnight: bool = False) -> "list[str]":
    """Admissions over two years, Monday heaviest, to the second -- or every one at midnight."""
    draw = random.Random(seed)
    found: "list[str]" = []
    for day in _weighted_days(draw, _TWO_YEARS, (1.45, 1.2, 1.15, 1.1, 1.1, 0.55, 0.5), rows):
        moment = _at(day, 0, 0) if midnight else _at(day, draw.randrange(24), draw.randrange(60), draw.randrange(60))
        found += [moment.strftime("%Y-%m-%d %H:%M:%S")]
    return found


def _sessions(rows: int = 1000, seed: int = 674) -> "list[str]":
    """Twelve Wednesday morning sessions a week apart, to the second."""
    draw = random.Random(seed)
    days = [datetime.date(2024, 1, 3) + datetime.timedelta(days=7 * step) for step in range(12)]
    return [
        _at(draw.choice(days), draw.randrange(8, 13), draw.randrange(60), draw.randrange(60)).strftime("%Y-%m-%d %H:%M:%S")
        for _row in range(rows)
    ]


def _business_log(rows: int = 1000, seed: int = 675, weekend: int = 15) -> "list[str]":
    """A weekday log with fifteen rows on weekend days."""
    draw = random.Random(seed)
    weekdays = [day for day in _YEAR if day.weekday() < 5]
    weekends = [day for day in _YEAR if day.weekday() >= 5]
    found = [
        _at(draw.choice(weekdays), draw.randrange(7, 19), draw.randrange(60), draw.randrange(60)).strftime("%Y-%m-%d %H:%M:%S")
        for _row in range(rows - weekend)
    ]
    found += [
        _at(draw.choice(weekends), draw.randrange(7, 19), draw.randrange(60), draw.randrange(60)).strftime("%Y-%m-%d %H:%M:%S")
        for _row in range(weekend)
    ]
    draw.shuffle(found)
    return found


def _seven_sessions(clock: str) -> "list[str]":
    """The gate's seven sessions, one date a weekday, every cell at one clock (the skeptic's B1)."""
    draw = random.Random(0)
    start = datetime.date(2024, 3, 4)
    days: "list[datetime.date]" = []
    for offset in (0, 1, 16, 17, 32, 33, 34):
        days += [start + datetime.timedelta(days=offset)] * (140 + draw.randrange(25))
    days += [start - datetime.timedelta(days=10)] * 12
    days += [start + datetime.timedelta(days=44)] * 12
    draw.shuffle(days)
    return [f"{day.isoformat()} {clock}" for day in days]


def _forty_ties(clock: str, rows: int = 1000) -> "list[str]":
    """Forty days of two years, every row on one of them, at one clock."""
    plan = random.Random(77)
    tie_days = sorted(plan.sample(_TWO_YEARS, 40))
    draw = random.Random(9200 + rows)
    return [f"{draw.choice(tie_days).isoformat()} {clock}" for _row in range(rows)]


def _payroll(clock: str, rows: int = 1000) -> "list[str]":
    """The 15th and the last day of 24 months, at one clock."""
    days: "list[datetime.date]" = []
    for month in range(24):
        year, place = 2023 + month // 12, month % 12 + 1
        days += [datetime.date(year, place, 15)]
        after = datetime.date(year + place // 12, place % 12 + 1, 1)
        days += [after - datetime.timedelta(days=1)]
    draw = random.Random(5150)
    return [f"{draw.choice(days).isoformat()} {clock}" for _row in range(rows)]


def _shared_clock(rows: int = 1000, seed: int = 676) -> "list[str]":
    """Arrivals written in two offsets, so read on the shared clock: no census stands (WC3)."""
    draw = random.Random(seed)
    found: "list[str]" = []
    for day in draw.choices(_YEAR, k=rows):
        offset = "+02:00" if draw.random() < 0.5 else "+01:00"
        found += [_at(day, draw.randrange(24), draw.randrange(60)).strftime("%Y-%m-%dT%H:%M:%S") + offset]
    return found


_THREE_WEEKS = [datetime.date(2023, 6, 5) + datetime.timedelta(days=step) for step in range(21)]


def _three_weeks() -> "list[str]":
    """Eight hundred clinic visits in three weeks of June and two hundred over the year: the
    middle half spans under four weeks while every group holds dates enough (WC10 alone)."""
    return _clinic(800, 677, _THREE_WEEKS) + _clinic(200, 678)

PUBLISHED = {
    "clinic": _clinic,
    "emergency": _emergency,
    "laboratory": _laboratory,
    "admissions": _admissions,
    "sessions": _sessions,
    "midnight": lambda: _admissions(midnight=True),
    "business": _business_log,
}
WITHHELD = {
    "seven_at_noon": lambda: _seven_sessions("12:00:00"),
    "forty_at_noon": lambda: _forty_ties("12:00:00"),
    "payroll_at_six": lambda: _payroll("18:00:00"),
    "three_weeks": _three_weeks,
}


def _block(name: str, cells: "list[str]", floor: int = FLOOR) -> "taxonomy.ColumnProfile":
    return taxonomy.profile_column(name, 1, cells, len(cells), taxonomy.Settings(small_cell_floor=floor))


def _text(name: str, cells: "list[str]") -> str:
    return name + "\n" + "\n".join(cells) + "\n"


def _described(folder: pathlib.Path, name: str, cells: "list[str]", floor: int = FLOOR) -> kpi_shapes.Described:
    return kpi_shapes.describe(folder / name, name, _text(name, cells), floor)


def _weekdays(block: "dict[str, object]", cells: "list[str]") -> "list[int]":
    """The body's weekday counts by instant, read under the column's own member."""
    low = parsing.instant_key(block["low_tail"]["boundary"], "")  # type: ignore[index]
    high = parsing.instant_key(block["high_tail"]["boundary"], "")  # type: ignore[index]
    found = [0] * 7
    for cell in cells:
        read = parsing.parse_datetime(cell, str(block["format"]))
        if read is None:
            continue
        instant = parsing.instant_key(read[0], "")
        if instant is not None and low <= instant <= high:
            found[(instant // DAY + 3) % 7] += 1
    return found


def _weekend(counts: "list[int]") -> float:
    return (counts[5] + counts[6]) / max(1, sum(counts))


# -- G-D1: what publishes ---------------------------------------------------------


@pytest.mark.parametrize("name", sorted(PUBLISHED))
def test_moments_publish_their_census_where_the_rules_allow(name: str) -> None:
    """Each shape of the battery publishes its census: one of the menu's groupings, every count
    nought or at least the census line, and the groups of its own body by instant."""
    cells = PUBLISHED[name]()
    described = _block(name, cells)
    census = described.details["weekday_census"]
    assert census, name
    groups = tuple((group["first"], group["last"], group["count"]) for group in census)
    assert calendar_rules.entry_of(groups) != calendar_rules.ENTRY_NONE
    line = parsing.census_floor(FLOOR)
    assert all(calendar_rules.calendar_floor_ok(count, line) for _first, _last, count in groups)
    found = calendar_rules.group_counts(groups, _weekdays(described.details, cells))
    assert found == [group["count"] for group in census], name


@pytest.mark.parametrize("name", sorted(WITHHELD))
def test_a_census_the_rules_keep_back_is_withheld_with_nf74(tmp_path: pathlib.Path, name: str) -> None:
    """Seven sessions, forty ties and payroll at one clock hold too few different days or
    written units a group; a clinic of three weeks has a middle half under four weeks (WC10).
    Each publishes `[]` and says so in NF74's one sentence."""
    document = _described(tmp_path, name, WITHHELD[name]()).document
    assert document["columns"][0]["weekday_census"] == []
    said = [entry["note"] for entry in document["publication_notes"]]
    assert any(NOTE_NF74 in sentence for sentence in said), said


def test_a_column_on_the_shared_clock_publishes_nothing_and_says_nothing() -> None:
    """Two offsets read on the shared clock: WC3 keeps the census to the local clock, and a
    census that cannot stand on the column is no withholding to speak of."""
    described = _block("arrived_at", _shared_clock())
    assert described.details["datetimes_read_at"] == "utc"
    assert described.details["weekday_census"] == []


def test_each_rule_withholds_its_own_shapes(monkeypatch: pytest.MonkeyPatch) -> None:
    """The mutants of G-D1: with the few-dates and few-units rules withdrawn the fixed clocks
    publish, and with the span rule withdrawn three weeks of clinic publishes."""
    monkeypatch.setattr(calendar_rules, "few_dates", lambda groups, body: False)
    monkeypatch.setattr(calendar_rules, "few_units", lambda groups, body, units: False)
    for name in ("seven_at_noon", "forty_at_noon", "payroll_at_six"):
        assert _block(name, WITHHELD[name]()).details["weekday_census"], name
    monkeypatch.undo()
    monkeypatch.setattr(calendar_rules, "span_short", lambda p25, p75: False)
    monkeypatch.setattr(calendar_rules, "moments_breach", lambda *arguments: None)
    assert _block("three_weeks", WITHHELD["three_weeks"]()).details["weekday_census"]


def test_the_rules_give_their_stated_answers_on_hand_made_bodies() -> None:
    """WC10 at 27 and 28 days and on a withheld rung; the few-units rule at a mean of eight
    written units a group and just under it, on one group alone, and on days at midnight."""
    assert calendar_rules.span_short(100, 127)
    assert not calendar_rules.span_short(100, 128)
    assert calendar_rules.span_short(None, 128) and calendar_rules.span_short(100, None)
    groups = ((0, 4, 16), (5, 6, 16))
    monday, saturday = 19781, 19786  # 2024-02-26 and 2024-03-02
    body = [monday + 7 * (step % 8) for step in range(16)] + [saturday + 7 * (step % 8) for step in range(16)]
    assert not calendar_rules.few_units(groups, body, body)
    shorter = [monday + 7 * (step % 7) for step in range(16)] + [saturday + 7 * (step % 8) for step in range(16)]
    assert calendar_rules.few_units(groups, shorter, shorter)
    clocked = [day * DAY + 3600 * (step % 2) for step, day in enumerate(shorter)]
    assert not calendar_rules.few_units(groups, shorter, clocked)
    assert not calendar_rules.few_units(((0, 4, 32), (5, 6, 0)), [monday] * 32, [monday] * 32)


# -- G-D2: every published census met --------------------------------------------


@pytest.mark.parametrize("name", sorted(PUBLISHED))
def test_every_published_census_is_met_by_its_twins_and_its_source(tmp_path: pathlib.Path, name: str) -> None:
    """Three twins of each published shape miss nothing, hold the body's weekend share to
    within a hundredth of the real one, and the source table meets its own description."""
    cells = PUBLISHED[name]()
    described = _described(tmp_path, name, cells)
    block = described.block(name)
    assert block["weekday_census"]
    real = _weekend(_weekdays(block, cells))
    for seed in (0, 1, 2):
        text = kpi_shapes.twin_text(described, seed)
        assert kpi_shapes.missed(kpi_shapes.measure(described, text, f"twin-{seed}.csv")) == [], (name, seed)
        twin = _weekdays(block, [line for line in text.split("\n")[1:] if line])
        assert abs(_weekend(twin) - real) <= 0.01, (name, seed, real, _weekend(twin))
    source = described.table.read_text(encoding="utf-8")
    assert kpi_shapes.missed(kpi_shapes.measure(described, source, "source.csv")) == []


def test_the_validator_counts_moments_by_instant(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """V5-W1 by instant: a cell on a boundary's day but beyond its instant is a tail cell, as
    the census counted it -- the clinic's high boundary's day holds five after it. Mutant:
    counted by day, the source misses its own census."""
    cells = _clinic()
    described = _described(tmp_path, "clinic", cells)
    block = described.block("clinic")
    low = parsing.instant_key(block["low_tail"]["boundary"], "")
    high = parsing.instant_key(block["high_tail"]["boundary"], "")
    beyond = 0
    for cell in cells:
        read = parsing.parse_datetime(cell, block["format"])
        instant = parsing.instant_key(read[0], "") if read is not None else None
        if instant is not None and (
            (instant // DAY == low // DAY and instant < low) or (instant // DAY == high // DAY and instant > high)
        ):
            beyond += 1
    assert beyond == 5, "a boundary's day holds tail cells beyond its instant"
    source = described.table.read_text(encoding="utf-8")
    assert kpi_shapes.missed(kpi_shapes.measure(described, source, "source.csv")) == []

    def by_day(facts, cells, holes, bins):
        low_day = parsing.days_from_civil(int(facts.low_tail.boundary[0:4]), int(facts.low_tail.boundary[5:7]), int(facts.low_tail.boundary[8:10]))
        high_day = parsing.days_from_civil(int(facts.high_tail.boundary[0:4]), int(facts.high_tail.boundary[5:7]), int(facts.high_tail.boundary[8:10]))
        for cell in cells:
            read = parsing.parse_datetime(cell, facts.parser_family)
            if read is not None:
                day = parsing.days_from_civil(int(read[0][0:4]), int(read[0][5:7]), int(read[0][8:10]))
                if low_day <= day <= high_day:
                    bins[calendar_rules.weekday_of(day)] += 1
        return 0

    monkeypatch.setattr(validation, "_moments_tallied", by_day)
    assert "clinic:weekday_census.groups" in kpi_shapes.missed(kpi_shapes.measure(described, source, "by-day.csv"))


# -- G-D3: a clock changes only where step 7c, 8.4, 8.5 or 8.7 moved it ----------


def _clocks_watched(monkeypatch: pytest.MonkeyPatch) -> "dict[str, int]":
    """How many clocks each step changed, as a multiset of times of day AS WRITTEN: step 9 sorts
    each run, so a rank's own clock may change where the column's clocks do not, and a run of
    one minute moved whole takes one place, the seconds under the minute never written."""
    changed: "dict[str, int]" = collections.defaultdict(int)
    for name in ("_bins_settled", "_weekday_escaped", "_weekday_units_merged", "_weekday_long_paired", "_weekday_day_spread"):
        original = getattr(generation, name)

        def watched(state, *arguments, _original=original, _name=name):
            before = collections.Counter(ordinal % DAY // state.step for ordinal in state.moved)
            answer = _original(state, *arguments)
            after = collections.Counter(ordinal % DAY // state.step for ordinal in state.moved)
            if state.day == DAY and state.unit == DAY:
                changed[_name] += sum((before - after).values())
            return answer

        monkeypatch.setattr(generation, name, watched)
    return changed


@pytest.mark.parametrize("name", ("sessions", "clinic", "nightly", "crowded"))
def test_a_clock_changes_only_on_ranks_steps_7c_8_4_8_5_or_8_7_moved(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, name: str) -> None:
    """The times of day the pass hands on are the drawn ones, but for the clocks steps 7c, 8.4
    at another clock, 8.5 and 8.7 gave the ranks they moved (the 3b.2-W skeptic, minor 2: on
    ties those steps alone rewrite 2.5 to 38.5 per cent of a body, so the bound is the cells
    they moved). Wednesday sessions reach step 7c, nightly batches at one clock step 8.4, and
    crowded Wednesdays step 8.7."""
    cells = {"nightly": _nightly, "crowded": _crowded_wednesdays}.get(name, PUBLISHED.get(name))()
    described = _described(tmp_path, name, cells)
    changed = _clocks_watched(monkeypatch)
    for seed in (0, 1):
        kpi_shapes.twin_text(described, seed)
    assert changed["_bins_settled"] <= (
        changed["_weekday_escaped"] + changed["_weekday_units_merged"] + changed["_weekday_long_paired"]
        + changed["_weekday_day_spread"]
    ), dict(changed)
    if name == "sessions":
        assert changed["_weekday_escaped"] > 0
    if name == "nightly":
        assert changed["_weekday_units_merged"] > 0
    if name == "crowded":
        assert changed["_weekday_day_spread"] > 0


def _nightly(rows: int = 1000, seed: int = 81001) -> "list[str]":
    """A nightly batch at 02:00 every weekday of two years."""
    draw = random.Random(seed)
    weekdays = [day for day in _TWO_YEARS if day.weekday() < 5]
    return [f"{draw.choice(weekdays).isoformat()} 02:00:00" for _row in range(rows)]


def _crowded_wednesdays(rows: int = 2400, seed: int = 81002) -> "list[str]":
    """Visits on seven Wednesdays a week apart, each at a minute from 07:00 to 19:59
    (`2024-03-06 07:46`): one non-empty group, so no few-dates or few-units rule asks it, and
    a body dense enough that the clocks the day pass keeps meet."""
    draw = random.Random(seed)
    days = [datetime.date(2024, 3, 6) + datetime.timedelta(days=7 * step) for step in range(7)]
    return [
        _at(draw.choice(days), draw.randrange(7, 20), draw.randrange(60)).strftime("%Y-%m-%d %H:%M")
        for _row in range(rows)
    ]


# -- G-D4: the mutants -----------------------------------------------------------


def _tenth_of_the_month(clock: str, months: int = 54, rows: int = 1000) -> "list[str]":
    """One date a month, the tenth, over `months` months, every row at one clock."""
    days = [datetime.date(2021 + (month // 12), month % 12 + 1, 10) for month in range(months)]
    draw = random.Random(5400 + months)
    return [f"{draw.choice(days).isoformat()} {clock}" for _row in range(rows)]


def test_the_few_units_rule_is_asked_off_midnight_too(monkeypatch: pytest.MonkeyPatch) -> None:
    """The tenth of the month over 56 months, every row at noon: its body's groups hold 7.71
    different days on average, which the few-dates rule lets through (seven and a half), and
    7.71 written units, under the few-units rule's eight, so the census is withheld -- and so
    is the same column at midnight, the rule asked in both spaces. Mutant: the rule keyed to
    `all_at_midnight`, the FEW DAYS the 3b.2-W skeptic's blocker 1 found: the noon column
    publishes. (Its twins then meet their counts on this column, 15 of 15 measured at noon and
    at 09:00 over 55 to 57 months: every noon witness of that blocker -- seven sessions, forty
    ties, payroll, the tenth over 24 to 54 months -- is withheld by the few-dates rule already,
    and this rule's own band, seven and a half to eight a group, is its stated price, P4-D367.)"""
    seen: "list[tuple[bool, bool]]" = []
    dates, units = calendar_rules.few_dates, calendar_rules.few_units

    def asked(groups, body, written):
        seen[:] = seen + [(dates(groups, body), units(groups, body, written))]
        return units(groups, body, written)

    monkeypatch.setattr(calendar_rules, "few_units", asked)
    assert _block("issued_at", _tenth_of_the_month("12:00:00", 56)).details["weekday_census"] == []
    assert seen == [(False, True)], seen
    assert _block("issued_at", _tenth_of_the_month("00:00:00", 56)).details["weekday_census"] == []

    def keyed_to_midnight(groups, body, written):
        return units(groups, body, written) if list(written) == list(body) else False

    monkeypatch.setattr(calendar_rules, "few_units", keyed_to_midnight)
    assert _block("issued_at", _tenth_of_the_month("12:00:00", 56)).details["weekday_census"]
    assert _block("issued_at", _tenth_of_the_month("00:00:00", 56)).details["weekday_census"] == []


def test_wednesday_sessions_need_step_7c(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Twelve Wednesday sessions: a rank drawn between two sessions at a clock neither
    Wednesday of its gap takes reaches the census only by step 7c. Mutant: the step withdrawn,
    and the twins miss the census."""
    described = _described(tmp_path, "session_at", _sessions())
    monkeypatch.setattr(generation, "_weekday_escaped", lambda *arguments: None)
    missed = set()
    for seed in (0, 1, 2):
        text = kpi_shapes.twin_text(described, seed)
        missed |= set(kpi_shapes.missed(kpi_shapes.measure(described, text, f"twin-{seed}.csv")))
    assert "session_at:weekday_census.groups" in missed, sorted(missed)


def test_a_short_count_is_put_back_on_each_moments_own_day(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Crowded Wednesdays publish their census, and three twins meet it and the count of
    different values: the pass moves each moment by whole days, so on seven Wednesdays the
    clocks it keeps meet, and step 8.7 puts the count back at another clock on each moment's
    own day, never on or off midnight. Mutant: the step withdrawn, and a twin holds fewer
    different values than the column (2,400 visits came back 1,882 to 1,887 minutes for 1,933
    at seeds 0 to 2 on the proof's battery)."""
    described = _described(tmp_path, "visit", _crowded_wednesdays())
    census = described.block("visit")["weekday_census"]
    assert [group["count"] > 0 for group in census].count(True) == 1, census
    for seed in (0, 1, 2):
        text = kpi_shapes.twin_text(described, seed)
        assert kpi_shapes.missed(kpi_shapes.measure(described, text, f"twin-{seed}.csv")) == [], seed
    monkeypatch.setattr(generation, "_weekday_day_spread", lambda *arguments: None)
    missed = set()
    for seed in (0, 1, 2):
        text = kpi_shapes.twin_text(described, seed)
        missed |= set(kpi_shapes.missed(kpi_shapes.measure(described, text, f"bare-{seed}.csv")))
    assert "visit:distinct.n_distinct" in missed, sorted(missed)


# -- the seventeenth vectors file: steps 7c and 8.7 on stated ranks -----------------


def _oracle() -> "dict[str, object]":
    return runpy.run_path(str(ORACLE))


def _case(name: str) -> dict:
    return _FILE["cases"][name]


def _state(case: dict, module: types.ModuleType = generation):
    state = module._WeekdayPass(
        moved=list(case["ordinals"]), held={}, where=list(case["where"]), facts=None,
        word="", widths=False, kinds={}, holes=frozenset(case["holes"]), lows=list(case["lows"]),
        highs=list(case["highs"]), keep_units=case["reachable"], unit=case["unit"],
        step=case["written_unit"], day=case["day"], bins=case["bin"], period=case["period"],
        keeps=case["keep"], pairs=case["pair"], pair_where=tuple(case["pair_where"]),
    )
    for ordinal in state.moved:
        module._weekday_tally(state.held, ordinal // state.step, 1)
        if state.unit != state.step:
            module._weekday_tally(state.units_held, ordinal // state.unit, 1)
    return state


def _answer(case: dict, module: types.ModuleType = generation) -> "list[int]":
    """What the product makes of a case: the whole pass, step 7c alone or step 8.7 alone."""
    state = _state(case, module)
    low, high, pinned = case["body"][0], case["body"][1], list(case["pinned"])
    if case["step"] == "settled":
        module._bins_settled(state, list(case["counts"]), low, high, pinned, case["wanted"])
        return state.moved
    if case["step"] == "day_spread":
        module._weekday_day_spread(state, low, high, pinned, case["wanted"])
        return state.moved
    ranks = [rank for rank in range(low, high + 1) if not pinned[rank]]
    have = [0] * len(case["want"])
    for rank in ranks:
        have[module._weekday_group(state, state.moved[rank])] += 1
    module._weekday_escaped(state, ranks, have, list(case["want"]))
    return state.moved


def _mutant(monkeypatch: pytest.MonkeyPatch, before: str, after: str) -> types.ModuleType:
    """The product's generation module with ONE source edit, built beside it (an edit that no
    longer applies turns the test red)."""
    assert SOURCE.count(before) == 1, before
    name = "synthtwin._generation_moments_mutant"
    module = types.ModuleType(name)
    module.__file__ = generation.__file__
    monkeypatch.setitem(sys.modules, name, module)
    exec(compile(SOURCE.replace(before, after), generation.__file__, "exec"), module.__dict__)
    return module


CASES = (
    "a_day_spread_keeps_inside_its_gap",
    "a_day_spread_leaves_a_hole_day_alone",
    "a_day_spread_puts_no_clock_on_midnight",
    "a_day_spread_takes_no_clock_off_midnight",
    "a_day_spread_takes_the_nearer_minute",
    "an_escape_keeps_off_a_hole",
    "an_escape_keeps_the_count",
    "an_escape_keeps_the_midnight",
    "an_escape_takes_the_nearer_end",
    "crowded_wednesdays_spread_on_their_day",
    "wednesdays_at_another_clock",
)

# Each case's own source edit of the product, and what it withdraws.
MUTANTS = {
    "wednesdays_at_another_clock": (
        "    if have != target and state.unit == state.day and state.unit != state.step:\n"
        "        _weekday_escaped(state, everything, have, target)\n",
        "",
    ),
    "an_escape_keeps_the_count": (
        "            if chosen is None or (keeps and chosen[0]):\n",
        "            if chosen is None:\n",
    ),
    "an_escape_keeps_the_midnight": (
        "            if place != start:\n                found += [place]\n",
        "            found += [place]\n",
    ),
    "an_escape_takes_the_nearer_end": (
        "        if chosen is not None and (best is None or chosen < best):\n",
        "        if chosen is not None and best is None:\n",
    ),
    "an_escape_keeps_off_a_hole": (
        "            or _weekday_hole(state, spot)\n            or _weekday_kind(state, spot) != kind\n        ):\n            continue\n        chosen",
        "            or _weekday_kind(state, spot) != kind\n        ):\n            continue\n        chosen",
    ),
    "crowded_wednesdays_spread_on_their_day": (
        "    if state.keep_units and state.unit == state.day and state.unit != state.step:\n"
        "        _weekday_day_spread(state, body_low, body_high, pinned, wanted)\n",
        "",
    ),
    "a_day_spread_takes_the_nearer_minute": (
        "        for place in (ordinal - away, ordinal + away):\n",
        "        for place in (ordinal + away, ordinal - away):\n",
    ),
    "a_day_spread_puts_no_clock_on_midnight": (
        "    first = max(state.lows[rank], start + 1)\n",
        "    first = max(state.lows[rank], start)\n",
    ),
    "a_day_spread_takes_no_clock_off_midnight": (
        "    if ordinal == start:\n        return []\n    first = max(state.lows[rank], start + 1)\n",
        "    first = max(state.lows[rank], start + 1)\n",
    ),
    "a_day_spread_keeps_inside_its_gap": (
        "    first = max(state.lows[rank], start + 1)\n",
        "    first = start + 1\n",
    ),
    "a_day_spread_leaves_a_hole_day_alone": (
        "            pinned[rank]\n            or _weekday_hole(state, ordinal)\n            or _weekday_there(state, ordinal) < 2\n",
        "            pinned[rank]\n            or _weekday_there(state, ordinal) < 2\n",
    ),
}


def test_every_case_is_asked() -> None:
    """The file holds these cases and no other, each with its own mutant, and the oracle, run
    again, gives each the answer the file carries."""
    assert tuple(sorted(_FILE["cases"])) == CASES
    assert tuple(sorted(MUTANTS)) == CASES
    oracle = _oracle()
    assert sorted(oracle["MOMENT_STEP_CASES"]) == list(CASES)  # type: ignore[call-overload]
    for name, case in _FILE["cases"].items():
        assert oracle["moment_answer"](case) == case["answer"], name  # type: ignore[operator]


@pytest.mark.parametrize("name", CASES)
def test_the_product_gives_each_case_its_answer_and_its_mutant_another(name: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """Each state of ranks: the product's answer is the file's, and under its own source edit
    the answer moves."""
    case = _case(name)
    assert _answer(case) == case["answer"], name
    before, after = MUTANTS[name]
    assert _answer(case, _mutant(monkeypatch, before, after)) != case["answer"], name


def test_wednesdays_reach_their_sessions_at_the_nearest_clock() -> None:
    """The whole pass on the sessions state: every rank on a Wednesday, the count of different
    minutes kept, and a clock changed only on the four ranks step 7c moved, each now within its
    gap's end at the minute nearest its own clock that no rank held."""
    case = _case("wednesdays_at_another_clock")
    moved = _answer(case)
    assert all((ordinal // DAY + 3) % 7 == 2 for ordinal in moved)
    assert len({ordinal // 60 for ordinal in moved}) == case["wanted"]
    before = collections.Counter(ordinal % DAY for ordinal in case["ordinals"])
    after = collections.Counter(ordinal % DAY for ordinal in moved)
    assert sum((before - after).values()) == 4
    for rank in range(len(moved)):
        assert case["lows"][rank] <= moved[rank] <= case["highs"][rank] or case["pinned"][rank]


def test_an_escape_keeps_the_count_of_different_values() -> None:
    case = _case("an_escape_keeps_the_count")
    assert len({o // 60 for o in case["answer"]}) == len({o // 60 for o in case["ordinals"]})


def test_an_escape_never_puts_a_clock_on_midnight_or_takes_one_off_it() -> None:
    case = _case("an_escape_keeps_the_midnight")
    for before, after in zip(case["ordinals"], case["answer"]):
        assert (before % DAY == 0) == (after % DAY == 0)
    assert case["answer"][1] == case["ordinals"][1], "a clock is never put on midnight"


def test_crowded_wednesdays_take_one_more_minute_on_their_own_day() -> None:
    """The whole pass on the crowded state: every rank on a Wednesday, the count of different
    minutes back at its own, and one clock changed, by one minute on the day it stood on."""
    case = _case("crowded_wednesdays_spread_on_their_day")
    moved = _answer(case)
    assert all((ordinal // DAY + 3) % 7 == 2 for ordinal in moved)
    assert len({ordinal // 60 for ordinal in moved}) == case["wanted"]
    before = collections.Counter(ordinal % DAY for ordinal in case["ordinals"])
    after = collections.Counter(ordinal % DAY for ordinal in moved)
    assert sum((before - after).values()) == 1
    assert sorted((after - before).elements()) == [9 * 3600 + 59 * 60]


def test_a_day_spread_moves_a_moment_only_on_its_own_day_and_off_midnight() -> None:
    """Step 8.7 alone, on every one of its states: each rank keeps its day, a rank at midnight
    stays there and none is put on it, every rank stays inside its gap, and the count rises by
    one a moved rank, never above what is asked."""
    for name in CASES:
        case = _case(name)
        if case["step"] != "day_spread":
            continue
        moved = 0
        for rank, (before, after) in enumerate(zip(case["ordinals"], case["answer"])):
            assert before // DAY == after // DAY, name
            assert (before % DAY == 0) == (after % DAY == 0), name
            assert case["lows"][rank] <= after <= case["highs"][rank], name
            moved += before != after
        count = len({ordinal // 60 for ordinal in case["answer"]})
        assert count == len({ordinal // 60 for ordinal in case["ordinals"]}) + moved <= case["wanted"], name


# -- the product against the oracle, on whole columns -----------------------------


@pytest.mark.parametrize("name", ("clinic", "sessions", "midnight", "emergency", "laboratory", "crowded"))
def test_the_pass_moves_whole_columns_as_the_oracle_does(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, name: str) -> None:
    """The ranks the generator hands the weekday pass, through the oracle's own pass, stated from
    the method's text: the same instants come back, through step 7c on the sessions and step 8.7
    on the crowded Wednesdays."""
    described = _described(tmp_path, name, PUBLISHED[name]() if name in PUBLISHED else _crowded_wednesdays())
    seen: "list[tuple[tuple, list[int]]]" = []
    settled = generation._weekday_settled

    def captured(column, facts, ordinals, parsed, whole, lows, highs, layout, holes, declared=()):
        answer = settled(column, facts, list(ordinals), parsed, whole, lows, highs, layout, holes, declared)
        seen[:] = [((list(ordinals), parsed, list(whole), list(lows), list(highs)), list(answer[0]))]
        return answer

    monkeypatch.setattr(generation, "_weekday_settled", captured)
    kpi_shapes.twin_text(described, 0)
    (ordinals, parsed, whole, lows, highs), moved = seen[0]
    oracle = _oracle()
    block = copy.deepcopy(described.block(name))
    answer = oracle["weekday_settled"](block, ordinals, parsed, whole, lows, highs, set(block.get("missing_by_source", {})))  # type: ignore[operator]
    assert answer == moved


# -- the loader -------------------------------------------------------------------


def test_the_loader_reads_a_census_of_moments_and_holds_it_to_wc10(tmp_path: pathlib.Path) -> None:
    """A clinic's census loads, and with its p75 pulled to 27 days after its p25 it is refused
    by WC10. (A census on the shared clock is refused by WC3, the loader battery's mutation on
    `logged_at`; a withheld p25 stands only where its rank lies in a tail, D11, and
    `calendar_rules.span_short` holds such a column short.)"""
    described = _described(tmp_path, "clinic", _clinic())
    document = described.document
    block = document["columns"][0]
    assert block["weekday_census"] and block["resolution"] == "datetime"

    def refused(edit, rule: str) -> None:
        changed = copy.deepcopy(document)
        edit(changed["columns"][0])
        path = fixtures.write_profile(tmp_path, f"edit-{rule}.json", changed)
        with pytest.raises(errors.ProfileError) as refusal:
            contract.load_profile(str(path))
        assert rule in str(refusal.value), str(refusal.value)

    def narrowed(column: dict) -> None:
        p25 = column["date_percentiles"]["p25"]
        day = datetime.date.fromisoformat(p25[0:10]) + datetime.timedelta(days=27)
        column["date_percentiles"]["p75"] = day.isoformat() + p25[10:]
        for rung in ("p50",):
            if column["date_percentiles"][rung] > column["date_percentiles"]["p75"]:
                column["date_percentiles"][rung] = column["date_percentiles"]["p75"]

    refused(narrowed, "WC10")


# -- the report ------------------------------------------------------------------


def test_a_count_the_pass_leaves_off_is_counted_in_values(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Where the census holds and the count of different values does not, the deviation counts
    VALUES on a column of moments, never days (the 3b.2-W skeptic, minor 1, found it counting
    days over instants). The pass is made to leave one moment on another's minute inside its
    own group, so the census holds and the count is one short."""
    described = _described(tmp_path, "session_at", _sessions())
    settled = generation._bins_settled

    def one_short(state, counts, body_low, body_high, pinned, wanted):
        settled(state, counts, body_low, body_high, pinned, wanted)
        ranks = [rank for rank in range(body_low, body_high + 1) if not pinned[rank]]
        for rank in ranks:
            other = next(
                (
                    place for place in ranks
                    if generation._weekday_group(state, state.moved[place]) == generation._weekday_group(state, state.moved[rank])
                    and state.moved[place] // state.step != state.moved[rank] // state.step
                    and generation._weekday_there(state, state.moved[rank]) == 1
                ),
                None,
            )
            if other is not None:
                generation._weekday_step(state, rank, state.moved[other])
                return

    said: "list[tuple[str, str]]" = []
    weekday_settled = generation._weekday_settled

    def heard(*arguments, **named):
        moved, notes = weekday_settled(*arguments, **named)
        said[:] = said + [(note.published, note.achieved) for note in notes if note.fact == "n_distinct"]
        return moved, notes

    monkeypatch.setattr(generation, "_bins_settled", one_short)
    monkeypatch.setattr(generation, "_weekday_settled", heard)
    generation.generate(described.loaded, 0)
    assert said and all(
        published.endswith("different values") and achieved.endswith("different values")
        for published, achieved in said
    ), said


# -- the workbook ----------------------------------------------------------------


def _moment_book(moments: "list[datetime.datetime]", text_every: int) -> bytes:
    """A workbook of one column of moments stored as dated numbers, and every
    `text_every`-th as ISO text."""
    body = [(1, [workbooks.cell("A1", "seen_at", "inlineStr")])]
    for place, moment in enumerate(moments):
        number = place + 2
        if text_every and place % text_every == 0:
            one = workbooks.cell(f"A{number}", moment.strftime("%Y-%m-%d %H:%M:%S"), "inlineStr")
        else:
            serial = (moment - datetime.datetime(1899, 12, 30)).total_seconds() / DAY
            one = workbooks.cell(f"A{number}", repr(serial), "", 2)
        body += [(number, [one])]
    return workbooks.package(
        [
            ("[Content_Types].xml", workbooks._content_types(1, False, False, False)),
            ("_rels/.rels", workbooks._root_rels()),
            ("xl/workbook.xml", workbooks._workbook([("Data", "")])),
            ("xl/_rels/workbook.xml.rels", workbooks._workbook_rels(1, False)),
            ("xl/styles.xml", workbooks._styles()),
            ("xl/worksheets/sheet1.xml", workbooks.sheet(body, dimension=f"A1:A{len(moments) + 1}")),
        ]
    )


def test_a_workbook_storing_moments_two_ways_publishes_no_census(tmp_path: pathlib.Path) -> None:
    """WC6's storage half is asked of moments too: the same moments stored as dated numbers
    publish a census its loader reads; with every sixth stored as text, none, and NF74 says so
    (the 3b.2-W design's workbook check: without it the producer published a census its own
    loader refused)."""
    draw = random.Random(3101)
    moments: "list[datetime.datetime]" = []
    for step in range(730):
        day = datetime.date(2022, 1, 3) + datetime.timedelta(days=step)
        times = draw.choice((0, 1, 2, 3)) if day.weekday() < 5 else draw.choice((0, 0, 0, 1))
        moments += [_at(day, draw.randrange(7, 20), draw.randrange(60), draw.randrange(60)) for _time in range(times)]
    draw.shuffle(moments)
    found = {}
    for name, every in (("moments", 0), ("mixed", 6)):
        path = tmp_path / f"{name}.xlsx"
        path.write_bytes(_moment_book(moments, every))
        document = profile.build_document(
            reading.read_table(str(path), small_cell_floor=FLOOR), taxonomy.Settings(small_cell_floor=FLOOR), [], [], []
        )
        written = fixtures.write_profile(tmp_path, f"{name}-profile.json", document)
        contract.load_profile(str(written))
        found[name] = document
    assert found["moments"]["columns"][0]["resolution"] == "datetime"
    assert found["moments"]["columns"][0]["weekday_census"], "dated numbers alone publish a census"
    assert found["mixed"]["columns"][0]["weekday_census"] == []
    said = [entry["note"] for entry in found["mixed"]["publication_notes"]]
    assert any(NOTE_NF74 in sentence for sentence in said), said

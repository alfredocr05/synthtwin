"""Gate file of lane STATS-A (batch 4zz): a day-scale gap of the dates zone lands on the weekday the real gaps land on.

A person's later date is the date before it plus a gap drawn from a quantile function of the real gaps (the
timeline's grid of its band, by the weekday of the date before), and a chained date is its reference plus a gap of
its chain's grid; the weekday such a date falls on is the earlier date's weekday plus the gap, modulo seven.

THE DEFECT (measured on the type battery's date table, `tests/types_zoo.py`'s typed_dates at 20,000 rows, 5,000
persons, dates over three years): a grid of 101 points holds a gap every few days where the gaps run to months, so the
weekday a drawn gap landed on was whatever those 101 gaps happened to land on -- each weekday cell's grid put the
landing shares up to 0.08 from the real ones (0.037 on average) -- and the twin's later dates drifted: on the
shipped route validate read Monday 3,061 to 3,069 for 2,910 published and Sunday 2,684 to 2,692 for 2,889 (its
window about 150), so five date types of the battery missed their weekday census.

WHAT IT HOLDS (each clause red on its mutant):

* On the battery's date table, the weekday counts the writer gives a person's later dates IN EXPECTATION (each gap
  drawn at many positions, the earlier dates the real ones) lie within 30 of the real counts of some 2,150 a weekday
  (measured 16; the writer before this lane 72): mutant, the writer reads no landing shares (`_landed` returns the
  grid's gap).
* After a weekend date of the battery's cases table, which has no cell of its own, the next date lands on a weekday
  in expectation as the real ones do (mutant: a grid of every weekday always read as days past whole weeks).
* A weekly schedule keeps whole weeks: every twin gap of a table whose every gap is whole weeks is whole weeks, so
  each person's dates stay on the person's weekday (mutants: every part's shares pulled into the pooled shares,
  `_concentration` read as no departure; a grid of every weekday of the date before always keeping the weekday its
  gaps land on rather than their days past whole weeks -- measured 156 gaps of 9,000 off whole weeks).
* A day-scale chain of long gaps lands its dates on the real weekdays in expectation (within 30 of the real counts of
  20,000; measured 9, the grid alone 196: Fridays 3,092 for the real 2,896), and no twin gap leaves the real gaps'
  span (mutant: the moved gap not held inside its part's span).
* A zone written before the landing shares (no `landings` key) is still read, and its writer draws the grid's own
  gaps as before (mutant: a missing key read as a damaged zone).
"""

from __future__ import annotations

import collections
import csv
import datetime
import io
import random
import typing

import pytest

import reliability_tables as T
import types_zoo
from synthtwin import inside_dates

ROWS = 20000
POSITIONS = 20000


def _days(zone: "dict[str, object]", name: str, cells: "list[str]") -> "list[int | None]":
    entry = zone["columns"][name]  # type: ignore[index]
    reading = inside_dates.Reading(entry["reading"]["kind"], entry["reading"]["member"])
    out: "list[int | None]" = []
    for cell in cells:
        found = inside_dates.moment_of(cell, reading) if cell.strip() else None
        out += [found[0] if found is not None else None]
    return out


def _landing_shares(grid: "list[int]", landings: "list[list[int]]", before: int) -> "list[float]":
    """The weekday the writer's gap lands on, over many positions of the grid (each its own spot inside its share)."""
    shares = [0.0] * 7
    jitter = random.Random(1)
    for j in range(POSITIONS):
        u = (j + jitter.random()) / POSITIONS
        shares[(before + max(0, inside_dates._landed(grid, landings, u, before))) % 7] += 1.0 / POSITIONS
    return shares


@pytest.fixture(scope="module")
def battery() -> "tuple[dict[str, list[str]], dict[str, object]]":
    table = types_zoo.table_named("typed_dates")
    header, rows = table.build(ROWS, types_zoo.seed_of(table))
    columns = {name: [row[k] for row in rows] for k, name in enumerate(header)}
    return columns, inside_dates.build_zone(columns, "person_key")


def test_a_person_s_later_dates_land_on_the_real_weekdays_in_expectation(battery) -> None:  # type: ignore[no-untyped-def]
    """Measured: within 16 of the real counts (the writer before this lane: 72)."""
    columns, zone = battery
    timeline = typing.cast("dict[str, object]", zone["timeline"])
    name = typing.cast(str, timeline["column"])
    assert timeline["scale"] == "day"
    column = inside_dates._prepared_column(name, zone["columns"][name])  # type: ignore[index]
    line = inside_dates._prepared_line(timeline, column)
    by: "dict[str, list[int]]" = collections.defaultdict(list)
    for person, day in zip(columns["person_key"], _days(zone, name, columns[name])):
        if day is not None:
            by[person] += [day]
    real = [0] * 7
    expected = [0.0] * 7
    cache: "dict[tuple[int, int, int], list[float]]" = {}
    for days in by.values():
        days.sort()
        for before, after in zip(days, days[1:]):
            real[inside_dates.weekday(after)] += 1
            weekday = inside_dates.weekday(before)
            grid, landings = inside_dates._band_gaps(line, len(days), f"{weekday}", weekday)
            key = (id(grid), id(landings), inside_dates.weekday(before))
            if key not in cache:
                cache[key] = _landing_shares(grid, landings, inside_dates.weekday(before))
            for weekday in range(7):
                expected[weekday] += cache[key][weekday]
    worst = max(abs(a - b) for a, b in zip(real, expected))
    assert worst <= 30, f"later dates' weekdays in expectation {[round(x) for x in expected]} for the real {real}"


def test_after_a_weekend_date_a_weekday_clinic_s_next_date_lands_on_a_weekday() -> None:
    """The reliability battery's cases table: cases on weekdays, a few on a weekend, too few for a cell of their own.

    After such a date the next is drawn from its band's grid of every weekday, which keeps the weekday its gaps land
    on here (`_past_weeks_fit`: they land on weekdays whatever the weekday before). Measured: 2 of 65 such gaps land
    on a weekend in expectation, as 3 real ones do; read as days past whole weeks, 25 did, and the twins' weekend
    share of `sched_start` rose (the battery's f08_case_starts reached the real table's conclusion on 5 runs of 9).
    """
    rows = list(csv.reader(io.StringIO(T.text("T4", ROWS, 1))))
    columns = {name: [row[k] for row in rows[1:]] for k, name in enumerate(rows[0])}
    skip = tuple(name for name, known in T.KNOWS["T4"].items() if known == "identifier" and name != T.PERSON["T4"])
    zone = inside_dates.build_zone(columns, T.PERSON["T4"], skip=skip)
    timeline = typing.cast("dict[str, object]", zone["timeline"])
    name = typing.cast(str, timeline["column"])
    line = inside_dates._prepared_line(timeline, inside_dates._prepared_column(name, zone["columns"][name]))  # type: ignore[index]
    by: "dict[str, list[int]]" = collections.defaultdict(list)
    for person, day in zip(columns[T.PERSON["T4"]], _days(zone, name, columns[name])):
        if day is not None:
            by[person] += [day]
    gaps = 0
    weekend = 0.0
    for days in by.values():
        days.sort()
        chosen = max([band for band in inside_dates.BANDS if len(days) >= band and band in line.bands], default=0)
        for before in days[:-1]:
            weekday = inside_dates.weekday(before)
            if not chosen or f"{weekday}" in line.bands[chosen].cells or weekday < 5:
                continue
            grid, landings = inside_dates._band_gaps(line, len(days), f"{weekday}", weekday)
            shares = _landing_shares(grid, landings, weekday)
            gaps += 1
            weekend += shares[5] + shares[6]
    assert gaps >= 20, gaps
    assert weekend <= 0.15 * gaps, f"{weekend:.1f} of {gaps} gaps after a weekend date land on a weekend"


def _weekly(persons: int, seed: int) -> "dict[str, list[str]]":
    """Each person seen on one weekday of their own, every one to 26 weeks, two to twelve times."""
    draw = random.Random(seed)
    who: "list[str]" = []
    seen: "list[str]" = []
    for person in range(persons):
        day = datetime.date(2022, 1, 3) + datetime.timedelta(days=draw.randrange(700))
        for _visit in range(draw.randint(2, 12)):
            who += [f"W{100000 + person}"]
            seen += [day.isoformat()]
            day = day + datetime.timedelta(weeks=draw.randint(1, 26))
    return {"person": who, "seen_on": seen}


def test_a_weekly_schedule_keeps_whole_weeks() -> None:
    columns = _weekly(1500, 4)
    rows = len(columns["seen_on"])
    zone = inside_dates.build_zone(columns, "person")
    twin = inside_dates.write_dates(zone, rows, people=columns["person"], given=columns, seed=2)
    by: "dict[str, list[int]]" = collections.defaultdict(list)
    for person, day in zip(columns["person"], _days(zone, "seen_on", twin["seen_on"])):
        assert day is not None
        by[person] += [day]
    off = sum(1 for days in by.values() for a, b in zip(sorted(days), sorted(days)[1:]) if (b - a) % 7)
    assert off == 0, f"{off} twin gaps of a weekly schedule are not whole weeks"


def _return_visits(rows: int, seed: int) -> "dict[str, list[str]]":
    """A visit over six years and a return visit up to 600 days later, on a weekday, Mondays the commonest."""
    draw = random.Random(seed)
    seen: "list[str]" = []
    back: "list[str]" = []
    for _row in range(rows):
        day = datetime.date(2018, 1, 1) + datetime.timedelta(days=draw.randrange(6 * 365))
        target = draw.choices(range(5), (30, 20, 20, 15, 15))[0]
        later = day + datetime.timedelta(days=draw.randint(1, 600))
        later = later + datetime.timedelta(days=(target - later.weekday()) % 7)
        seen += [day.isoformat()]
        back += [later.isoformat()]
    return {"seen_on": seen, "back_on": back}


def test_a_long_chained_gap_lands_on_the_real_weekdays() -> None:
    """Measured: within 9 of the real counts in expectation (the grid alone: 196); every twin gap in the real span."""
    columns = _return_visits(ROWS, 9)
    zone = inside_dates.build_zone(columns)
    entry = zone["columns"]["back_on"]  # type: ignore[index]
    assert entry["chain"]["reference"] == "seen_on" and entry["chain"]["scale"] == "day"
    chain = inside_dates._prepared_chain(entry["chain"])
    assert chain is not None
    before_days = _days(zone, "seen_on", columns["seen_on"])
    after_days = _days(zone, "back_on", columns["back_on"])
    real = [0] * 7
    expected = [0.0] * 7
    cache: "dict[int, list[float]]" = {}
    gaps: "list[int]" = []
    for before, after in zip(before_days, after_days):
        assert before is not None and after is not None
        gaps += [after - before]
        real[inside_dates.weekday(after)] += 1
        weekday = inside_dates.weekday(before)
        if weekday not in cache:
            key = f"{weekday}"
            cache[weekday] = _landing_shares(inside_dates._gaps_at(chain.gaps, key),
                                             inside_dates._landings_at(chain.gaps, key, weekday), weekday)
        for day in range(7):
            expected[day] += cache[weekday][day]
    worst = max(abs(a - b) for a, b in zip(real, expected))
    assert worst <= 30, f"return visits. weekdays in expectation {[round(x) for x in expected]} for the real {real}"
    twin = inside_dates.write_dates(zone, ROWS, seed=5)
    twin_gaps = [b - a for a, b in zip(_days(zone, "seen_on", twin["seen_on"]), _days(zone, "back_on", twin["back_on"]))
                 if a is not None and b is not None]
    assert twin_gaps and min(gaps) <= min(twin_gaps) and max(twin_gaps) <= max(gaps)


def test_a_zone_written_before_the_landing_shares_draws_the_grid_s_own_gaps() -> None:
    columns = _return_visits(4000, 3)
    zone = inside_dates.build_zone(columns)
    chain_entry = zone["columns"]["back_on"]["chain"]  # type: ignore[index]
    del chain_entry["landings"], chain_entry["cell_landings"], chain_entry["landings_by"]
    twin = inside_dates.write_dates(zone, 4000, seed=1)
    allowed = set(chain_entry["grid"])
    for key in chain_entry["cells"]:
        allowed |= set(chain_entry["cells"][key])
    twin_gaps = [b - a for a, b in zip(_days(zone, "seen_on", twin["seen_on"]), _days(zone, "back_on", twin["back_on"]))
                 if a is not None and b is not None]
    assert twin_gaps and set(twin_gaps) <= allowed

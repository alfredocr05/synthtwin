"""Gate file of lane IN-5 (batch 4zz): every twin date of the dates zone lies in its column's real months.

A date column's calendar in the dates zone holds the months the real column held dates in, from the first day of
its first month to the last day of its last (`inside_dates.outside_the_real_months` counts against it). A made-up day
of the month moves a date inside its month; nothing of the draw may move it out of them, because `synthtwin
validate` excuses a drawn column's day-level ladder and tails only where every twin date lies inside (the owner's
ruling of 2026-11-22, `cli._INSIDE_RANGE_GUARDED_FACTS`).

THE DEFECT (measured on batch 4z's line through the shipped commands, the writer's inputs replayed step by step):
the draw left almost every date inside, and the moves that hold the description's twin's months
(`inside_dates._held_months`, whole persons by whole weeks) took them out -- the Windows bundle's visits table 12
dates of 11 persons up to 44 days before the real first month, the battery's cases table 42 dates up to 212 days
outside, its accounts table 10 dates up to 1,308 days past the real last month (a person moved far to fill a short
month, its later dates carried past the end); and a person's first date placed by whole weeks a few days before the
first month (6 dates on the cases table, 1 on the accounts table). The description's twin itself held no date outside.

WHAT IT HOLDS (each clause red on its mutant):

* With the description's twin's months held (the shipped route's `months`; here the table's own cells in another row
  order stand for them), no twin date of the battery's visits, cases or accounts table lies outside its column's real
  months, every person's dates keep their order, and the months are still held (mutant: the persons' rooms not read
  by `_persons_months_held`).
* A row heading its own chain is never moved where a date chained to it would leave its column's months (mutant: the
  row's room not read by `_months_held`).
* A person's first date placed near the first month stays inside it (mutant: the placement's inside move dropped from
  `_timeline_moments`).
* The last pass (`_kept_inside`) brings a person moved outside back inside by whole weeks with every date chained to
  it, gaps and weekdays kept, and puts a person's dates spread wider than its months each at the nearest end (mutant:
  the last pass moves nothing).
"""

from __future__ import annotations

import csv
import io
import random
import typing

import pytest

import reliability_tables as T
from synthtwin import inside_dates, parsing

ROWS = 20000


def _columns(text: str) -> "dict[str, list[str]]":
    rows = list(csv.reader(io.StringIO(text)))
    header, body = rows[0], rows[1:]
    return {name: [row[i] for row in body] for i, name in enumerate(header)}


def _skip(table: str) -> "tuple[str, ...]":
    return tuple(name for name, known in T.KNOWS[table].items() if known == "identifier" and name != T.PERSON[table])


def _reading(zone: "dict[str, object]", name: str) -> inside_dates.Reading:
    entry = zone["columns"][name]  # type: ignore[index]
    return inside_dates.Reading(entry["reading"]["kind"], entry["reading"]["member"])


def _room(zone: "dict[str, object]", name: str) -> "tuple[int, int]":
    calendar = inside_dates._prepared_calendar(zone["columns"][name]["calendar"])  # type: ignore[index]
    return calendar.first_day, calendar.last_day


def _days(zone: "dict[str, object]", name: str, cells: "list[str]") -> "list[int | None]":
    reading = _reading(zone, name)
    out: "list[int | None]" = []
    for cell in cells:
        found = inside_dates.moment_of(cell, reading) if cell.strip() else None
        out += [found[0] if found is not None else None]
    return out


def _months(zone: "dict[str, object]", name: str, cells: "list[str]") -> "dict[tuple[int, int], int]":
    counted: "dict[tuple[int, int], int]" = {}
    for day in _days(zone, name, cells):
        if day is not None:
            year, month, _date = parsing.civil_from_days(day)
            counted[(year, month)] = counted.get((year, month), 0) + 1
    return counted


@pytest.fixture(scope="module", params=["T2", "T4", "T7"])
def held(request: pytest.FixtureRequest) -> "tuple[typing.Any, ...]":
    """A battery table, its zone, the stand-in for the description's twin's cells, the twin written holding them, and
    how many dates the last pass moved (`_kept_inside`'s count, read as the writer calls it)."""
    table = request.param
    columns = _columns(T.text(table, ROWS, 1))
    zone = inside_dates.build_zone(columns, T.PERSON[table], skip=_skip(table))
    order = list(range(ROWS))
    random.Random(7).shuffle(order)
    stand_in = {name: [columns[name][k] for k in order] for name in zone["order"]}  # type: ignore[union-attr]
    moved: "list[int]" = []
    kept_inside = inside_dates._kept_inside

    def counted(*arguments: typing.Any) -> int:
        found = kept_inside(*arguments)
        moved.append(found)
        return found

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inside_dates, "_kept_inside", counted)
        twin = inside_dates.write_dates(zone, ROWS, people=columns[T.PERSON[table]], given=columns, seed=3,
                                        months=stand_in)
    return table, columns, zone, stand_in, twin, moved


def test_no_twin_date_leaves_its_real_months_when_the_description_s_months_are_held(held) -> None:  # type: ignore[no-untyped-def]
    """Measured with the stand-in on batch 4z's writer: cases 55 dates up to 388 days outside, accounts 22 up to 1,889."""
    table, columns, zone, stand_in, twin, moved = held
    # The holding moves keep every date inside by themselves: the last pass has nothing left to bring in.
    assert moved == [0], f"{table}: the last pass moved {moved} dates the month holding left outside"
    for name in zone["order"]:
        first, last = _room(zone, name)
        days = [day for day in _days(zone, name, twin[name]) if day is not None]
        outside = [day for day in days if not first <= day <= last]
        assert not outside, f"{table} {name}: {len(outside)} twin dates outside the real months"
        # ...and the months the description's twin asks for are still held (no more than 2 per cent elsewhere).
        want, have = _months(zone, name, stand_in[name]), _months(zone, name, twin[name])
        elsewhere = sum(abs(want.get(key, 0) - have.get(key, 0)) for key in set(want) | set(have)) // 2
        assert elsewhere <= 0.02 * len(days), f"{table} {name}: {elsewhere} dates in another month"


def test_every_person_s_dates_keep_their_order(held) -> None:  # type: ignore[no-untyped-def]
    table, columns, zone, _stand_in, twin, _moved = held
    timeline = zone["timeline"]
    assert isinstance(timeline, dict), table
    name = timeline["column"]
    last: "dict[str, int]" = {}
    for person, day in zip(columns[T.PERSON[table]], _days(zone, name, twin[name])):
        if day is None:
            continue
        assert person not in last or day >= last[person], f"{table}: a person's dates out of order"
        last[person] = day


def test_a_row_is_never_moved_where_a_date_chained_to_it_would_leave_its_months() -> None:
    """`_months_held` reads the row's room: March asked for, a date chained to each row in a column whose real
    months end on 14 March, so every row lands in March by 14 March and none past it."""
    january = parsing.days_from_civil(2022, 1, 3)
    days = [january + (row % 21) for row in range(70)]
    seconds = [-1] * len(days)
    cache: "dict[int, tuple[int, int, int]]" = {}
    march = inside_dates._month_key(parsing.days_from_civil(2022, 3, 15), cache) * 2
    end = parsing.days_from_civil(2022, 3, 14)
    chained = ({"chained": (list(days), seconds)}, ["chained"], {"chained": (january - 400, end)})
    moves = inside_dates._months_held(days, seconds, [march] * len(days), cache, None, chained)
    landed = [day + move for day, move in zip(days, moves)]
    assert all(parsing.days_from_civil(2022, 3, 1) <= day <= end for day in landed)
    assert all(move % 7 == 0 for move in moves)
    # ...and with no room read the same rows land anywhere in March, some past its 14th (the mutant's twin).
    unbounded = inside_dates._months_held(days, seconds, [march] * len(days), cache, None, None)
    assert max(day + move for day, move in zip(days, unbounded)) > end


def test_a_person_s_first_date_placed_near_the_first_month_stays_inside_it() -> None:
    """The timeline's own placement (before any month is held): no date before the first month or after the last."""
    columns = _columns(T.text("T4", ROWS, 1))
    zone = inside_dates.build_zone(columns, T.PERSON["T4"], skip=_skip("T4"))
    timeline = zone["timeline"]
    assert isinstance(timeline, dict)
    name = timeline["column"]
    column = inside_dates._prepared_column(name, zone["columns"][name])  # type: ignore[index]
    line = inside_dates._prepared_line(timeline, column)
    outside = 0
    for seed in range(4):
        days, _seconds = inside_dates._timeline_moments(line, column, columns[T.PERSON["T4"]], ROWS, columns, {},
                                                        seed, {})
        outside += sum(1 for day in days if day != inside_dates._ABSENT
                       and not column.calendar.first_day <= day <= column.calendar.last_day)
    assert outside == 0


def test_the_last_pass_brings_a_person_and_its_chained_dates_inside_by_whole_weeks() -> None:
    columns = _columns(T.text("T4", 6000, 1))
    zone = inside_dates.build_zone(columns, T.PERSON["T4"], skip=_skip("T4"))
    people = columns[T.PERSON["T4"]]
    entries, order, moments = inside_dates._date_moments(zone, 6000, people, columns, None, None, 2)
    head = zone["timeline"]["column"]  # type: ignore[index]
    rows = [row for row in range(6000) if people[row] == people[0]]
    before = {name: [moments[name][0][row] for row in rows] for name in order}
    first, last = _room(zone, head)
    push = last - min(day for day in before[head] if day != inside_dates._ABSENT) + 30
    for name in order:
        for row in rows:
            if moments[name][0][row] != inside_dates._ABSENT:
                moments[name][0][row] += push
    groups: "dict[str, list[int]]" = {}
    for row, person in enumerate(people):
        groups.setdefault(person, []).append(row)
    moved = inside_dates._kept_inside(entries, order, head, moments, list(groups.values()))
    assert moved > 0
    shifts = set()
    for name in order:
        low, high = _room(zone, name)
        for row, was in zip(rows, before[name]):
            now = moments[name][0][row]
            if was == inside_dates._ABSENT:
                assert now == inside_dates._ABSENT
                continue
            assert low <= now <= high, name
            shifts.add(now - (was + push))
    # One move for the person's every date (every gap kept), of whole weeks from where it stood (every weekday kept).
    assert len(shifts) == 1 and shifts.pop() % 7 == 0


def test_a_person_s_dates_wider_than_their_months_are_each_put_at_the_nearest_end() -> None:
    columns = _columns(T.text("T2", 6000, 1))
    people = columns[T.PERSON["T2"]]
    zone = inside_dates.build_zone(columns, T.PERSON["T2"], skip=_skip("T2"))
    entries, order, moments = inside_dates._date_moments(zone, 6000, people, columns, None, None, 2)
    head = zone["timeline"]["column"]  # type: ignore[index]
    first, last = _room(zone, head)
    groups: "dict[str, list[int]]" = {}
    for row, person in enumerate(people):
        groups.setdefault(person, []).append(row)
    rows = [row for row in max(groups.values(), key=len) if moments[head][0][row] != inside_dates._ABSENT]
    moments[head][0][rows[0]] = first - 30
    moments[head][0][rows[-1]] = last + 30
    moved = inside_dates._kept_inside(entries, order, head, moments, list(groups.values()))
    assert moved >= 2
    assert (moments[head][0][rows[0]], moments[head][0][rows[-1]]) == (first, last)
    assert all(first <= moments[head][0][row] <= last for row in rows)

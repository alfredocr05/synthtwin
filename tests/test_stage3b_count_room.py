"""Landing 3b.D1b (plan P4-D388) and its Codex review: the weekday census withheld where the count of different values has no room for it, either way.

The few-dates rule of landing 3b.G (plan P4-D365) was measured at the
floor of 11 alone. Raised to 36, 59 twins of the date batteries published
a weekday census and came back holding MORE different values than their
column: a tail that publishes its two distances rather than its values is
rebuilt with up to the floor's number of different days, the count pass
leaves the body only what the tails leave of the count, and the census
then asks the body for a day of each of its groups inside every gap
between two pins. `calendar_rules.count_room_short` withholds the census
there (`REASON_COUNT_ROOM`), said in the one sentence every rule the
table's own numbers decide shares. Its two halves are what the
construction can do at most -- the tails' most (`tails_most`), the
census's need between the body's pins (`body_pins`) -- so it is
conservative, and its price is the censuses it withholds that a twin
would have met.

ITS CODEX REVIEW, THREE ITEMS. (1) The rule was asked above the floor of
11 alone, and a column it withholds at 12 with one cell moved published
its census at 11 and left a twin long, 27 different values for 24 at
seed 17: it is asked at every floor now. (2) A count is lost the other
way too: a rebuilt tail can hold FEWER days than the real one, and where
the census keeps the body off the days that would make them up the twin
comes back short, 11 for 12 at every seed of the review's fortnight.
`calendar_rules.count_reach_short` withholds the census there
(`REASON_COUNT_REACH`), reading the fewest and the most days the twin's
tails can hold as the generator rebuilds them (`tails_fewest`,
`tails_most_rebuilt`: method G7.3b written a second time and held to the
generator's own here) and the days the body's draw lands on: where the
draw falls short of the count the count pass only splits and the tails
reach their most, and where it merges the body keeps no more than its
draw. Read so, it withholds some censuses a twin meets -- on columns
holding a row on every day their census allows, two rows a business
day over two years and three clinic days a week among them -- and that
is its price; with the federal holidays closed, such logs keep 70 of
the 72 censuses measured.
(3) What is claimed is what was measured: on the review's columns,
the 26 batteries at seeds 0 to 4, 2,000 short spans, 25 weekday logs
and six business-day logs, no census these rules publish left a twin a
value long or short where
its census withheld kept the count, and the tails' own limit stands
beside them -- fifteen Mondays at the floor of 36 come back with 33
different values for 15 with or without their census.

Each test names the mutation that turns it red.
"""

from __future__ import annotations

import dataclasses
import datetime
import json
import math
import pathlib
import random

import pytest

import fixtures
import kpi_shapes
from synthtwin import calendar_rules, contract, generation, parsing, profile, reading, rendering, taxonomy, validation

# Monday 1 January 2024 as a day number counted from 1970-01-01.
_MONDAY = 19723
_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _weekly_schedule(shape: int) -> "list[str]":
    """Weekly sessions on one to three weekdays, drawn with `Random(77000 + shape)` (the review's seeded schedules)."""
    draw = random.Random(77000 + shape)
    first = datetime.date(2023, 1, 1) + datetime.timedelta(days=draw.randrange(300))
    weeks = draw.randint(15, 70)
    allowed = sorted(draw.sample(range(7), draw.randint(1, 3)))
    days = sorted({
        first + datetime.timedelta(days=7 * week + draw.choice(allowed))
        for week in range(weeks)
        if draw.random() < 0.9
    })
    rows = draw.randint(200, 1500)
    weights = [draw.choice([draw.uniform(0.2, 1), draw.paretovariate(1.3)]) for _ in days]
    return [draw.choices(days, weights)[0].isoformat() for _ in range(rows)]


def _weekly_clinic(shape: int) -> "list[str]":
    """500 visits over 39 weekly clinic days, some moved a day either way (the sparse schedules measured)."""
    draw = random.Random(1000 + shape)
    first = datetime.date(2024, 1, 1) + datetime.timedelta(days=draw.randrange(100))
    days = [first + datetime.timedelta(days=7 * week + draw.choice([0, 0, 0, 1, -1])) for week in range(39)]
    weights = [draw.uniform(0.2, 3.0) for _ in days]
    return [draw.choices(days, weights)[0].isoformat() for _ in range(500)]


def _monthly(day: int, start: int, months: int, seed: int) -> "list[str]":
    """One date a month, the `day`th, over `months` months from January of `start`; 1,000 rows (the gate's builder)."""
    draw = random.Random(seed)
    days = [datetime.date(start + step // 12, 1 + step % 12, day) for step in range(months)]
    return [draw.choice(days).isoformat() for _row in range(1000)]


def _hunt(seed: int) -> "list[str]":
    """A small column of 90 to 160 visits over two weeks to two hundred days (D0's hunt batteries, `Random(seed)`)."""
    draw = random.Random(seed)
    rows = draw.randint(90, 160)
    span = draw.choice([14, 21, 28, 42, 60, 90, 120, 200])
    first = datetime.date(2024, 1, 1) + datetime.timedelta(days=draw.randrange(60))
    days = [first + datetime.timedelta(days=step) for step in range(span)]
    kind = draw.randrange(5)
    if kind == 0:
        weights = [draw.uniform(0.5, 1.5) * (0.15 if day.weekday() >= 5 else 1) for day in days]
    elif kind == 1:
        keep = set(draw.sample(range(7), draw.randint(1, 3)))
        weights = [draw.uniform(0.5, 1.5) if day.weekday() in keep else 0.02 for day in days]
    elif kind == 2:
        weights = [draw.choice([0.1, 0.1, 0.1, 3, 8]) for _each in days]
    elif kind == 3:
        on = set(draw.sample(range(span), max(3, span // draw.randint(3, 9))))
        weights = [draw.uniform(0.5, 2) if step in on else 0.0 for step in range(span)]
    else:
        weights = [draw.uniform(0.2, 1.8) for _each in days]
    return [draw.choices(days, weights)[0].isoformat() for _ in range(rows)]


def _moved_hunt_690() -> "list[str]":
    """`_hunt(690)` with one `2024-07-02` cell written `2024-05-16` (the Codex review of P4-D388, item 1)."""
    cells = list(_hunt(690))
    cells[cells.index("2024-07-02")] = "2024-05-16"
    return cells


def _fortnight() -> "list[str]":
    """The Codex review's 14 days from Monday 29 January 2024, its first weekend empty: 156 rows over 12 dates (item 2)."""
    counts = (23, 3, 14, 8, 23, 0, 0, 4, 20, 30, 20, 8, 1, 2)
    first = datetime.date(2024, 1, 29)
    return [
        (first + datetime.timedelta(days=step)).isoformat()
        for step in range(len(counts))
        for _copy in range(counts[step])
    ]


def _business_year() -> "list[str]":
    """Every weekday of 2024's first 52 weeks once, then 740 more drawn by weight: 1,000 rows (D0's `attack2:mon_fri_52_1000`)."""
    draw = random.Random(7612)
    first = datetime.date(2024, 1, 1)
    days = [first + datetime.timedelta(days=step) for step in range(52 * 7)]
    days = [day for day in days if day.weekday() < 5]
    weights = [draw.uniform(0.5, 1.5) for _ in days]
    cells = [day.isoformat() for day in days]
    cells += [day.isoformat() for day in draw.choices(days, weights, k=1000 - len(days))]
    draw.shuffle(cells)
    return cells


def _one_row_a_business_day() -> "list[str]":
    """One row a business day from Monday 6 January 2020, 1,180 of them, and one more (the gate's `bizlog_x1_s1`)."""
    draw = random.Random(101)
    day = datetime.date(2020, 1, 6)
    days: "list[datetime.date]" = []
    while len(days) < 1180:
        if day.weekday() < 5:
            days += [day]
        day += datetime.timedelta(days=1)
    cells = [each.isoformat() for each in days]
    cells += [each.isoformat() for each in draw.sample(days[20:-20], 1)]
    draw.shuffle(cells)
    return cells


# The US federal holidays of 2022 and 2023 on the business day each was observed: 21 days.
_FEDERAL_HOLIDAYS = frozenset(
    datetime.date.fromisoformat(each)
    for each in (
        "2022-01-17 2022-02-21 2022-05-30 2022-06-20 2022-07-04 2022-09-05 2022-10-10 2022-11-11 2022-11-24"
        " 2022-12-26 2023-01-02 2023-01-16 2023-02-20 2023-05-29 2023-06-19 2023-07-04 2023-09-04 2023-10-09"
        " 2023-11-10 2023-11-23 2023-12-25"
    ).split()
)


def _two_rows_a_business_day(closed: "frozenset[datetime.date]" = frozenset()) -> "list[str]":
    """About two rows a business day for 104 weeks from Monday 3 January 2022, `Random(304)`: 1,063 rows over 520 days.

    A day in `closed` holds none of the rows it draws; every other day
    holds the rows it draws either way.
    """
    draw = random.Random(304)
    first = datetime.date(2022, 1, 3)
    cells: "list[str]" = []
    for step in range(104 * 7):
        day = first + datetime.timedelta(days=step)
        if day.weekday() >= 5:
            continue
        rows = max(1, int(round(draw.gauss(2, 2 / 3))))
        if day not in closed:
            cells += [day.isoformat()] * rows
    draw.shuffle(cells)
    return cells


def _three_clinic_days_a_week() -> "list[str]":
    """About one and a half rows every Monday, Wednesday and Friday for 52 weeks from 3 January 2022, `Random(9202)`.

    242 rows over 156 days, every clinic day holding at least one.
    """
    draw = random.Random(9202)
    first = datetime.date(2022, 1, 3)
    cells: "list[str]" = []
    for step in range(52 * 7):
        day = first + datetime.timedelta(days=step)
        if day.weekday() in (0, 2, 4):
            cells += [day.isoformat()] * max(1, int(round(draw.gauss(1.5, 0.5))))
    draw.shuffle(cells)
    return cells


def _mondays() -> "list[str]":
    """Fifteen consecutive Mondays from 1 January 2024, ten rows each (the Codex review of P4-D388, item 3)."""
    first = datetime.date(2024, 1, 1)
    return [(first + datetime.timedelta(days=7 * week)).isoformat() for week in range(15) for _copy in range(10)]


def _day(cell: str) -> int:
    """An ISO date as a day number counted from 1970-01-01."""
    return parsing.days_from_civil(int(cell[0:4]), int(cell[5:7]), int(cell[8:10]))


def _described(tmp_path: pathlib.Path, name: str, cells: "list[str]", floor: int) -> kpi_shapes.Described:
    return kpi_shapes.describe(tmp_path / name, name, "visit\n" + "".join(f"{cell}\n" for cell in cells), floor)


def _described_declaring(
    tmp_path: pathlib.Path, name: str, cells: "list[str]", floor: int, declared: "tuple[str, ...]"
) -> kpi_shapes.Described:
    """As `_described`, with `declared` named as missing values (`--missing-value`)."""
    folder = tmp_path / name
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(folder, f"{name}.csv", "visit\n" + "".join(f"{cell}\n" for cell in cells))
    settings = taxonomy.Settings(small_cell_floor=floor, declared_missing_values=declared)
    document = profile.build_document(reading.read_table(str(table), small_cell_floor=floor), settings, [])
    written = fixtures.write_profile(folder, f"{name}-profile.json", document)
    return kpi_shapes.Described(folder, table, document, contract.load_profile(str(written)))


def _decided(block: dict, cells: "list[str]", floor: int) -> taxonomy.WeekdayDecision:
    """The producer's decision for this block, asked again."""
    return taxonomy.weekday_decision(
        block,
        tuple(sorted(_day(cell) for cell in cells)),
        block["n_distinct"],
        taxonomy.Settings(small_cell_floor=floor),
        texts=len(set(cells)),
    )


def _seven(counts: "tuple[int, ...]") -> "tuple[tuple[int, int, int], ...]":
    return tuple((weekday, weekday, counts[weekday]) for weekday in range(7))


def _restored(
    tmp_path: pathlib.Path, name: str, described: kpi_shapes.Described, cells: "list[str]", floor: int
) -> contract.Profile:
    """The description with the census the menu offers written back into it, loaded."""
    block = described.block("visit")
    body = sorted(_day(cell) for cell in cells)[block["low_tail"]["rows"] : len(cells) - block["high_tail"]["rows"]]
    groups, _entry = calendar_rules.menu_groups(calendar_rules.body_bins(body), parsing.census_floor(floor))
    document = dict(described.document)
    document["columns"] = [
        dict(block, weekday_census=[{"first": first, "last": last, "count": count} for first, last, count in groups])
    ]
    return contract.load_profile(str(fixtures.write_profile(tmp_path, f"{name}-restored.json", document)))


def _twins_off(
    tmp_path: pathlib.Path, name: str, profile: contract.Profile, seeds: "tuple[int, ...]", wanted: int, longer: bool
) -> None:
    """Every twin of `profile` at `seeds` holds more (or fewer) different values than `wanted`, both counts MISSED."""
    for seed in seeds:
        twin = generation.generate(profile, seed)
        held = len(set(twin.columns[0]))
        assert (held > wanted) if longer else (held < wanted), (name, seed, held, wanted)
        written = fixtures.write(tmp_path, f"{name}-off-{seed}.csv", rendering.twin_csv(twin))
        missed = kpi_shapes.missed(validation.measure(profile, str(written)))
        assert "visit:distinct.n_distinct" in missed and "visit:distinct.n_distinct_folded" in missed, (name, seed, missed)


def _twins_meet(
    tmp_path: pathlib.Path, name: str, profile: contract.Profile, seeds: "tuple[int, ...]"
) -> None:
    """Every twin of `profile` at `seeds` misses no check."""
    for seed in seeds:
        written = fixtures.write(tmp_path, f"{name}-met-{seed}.csv", rendering.twin_csv(generation.generate(profile, seed)))
        assert kpi_shapes.missed(validation.measure(profile, str(written))) == [], (name, seed)


def _restored_twins_long(
    tmp_path: pathlib.Path, name: str, described: kpi_shapes.Described, cells: "list[str]", floor: int
) -> None:
    """The census the menu offers, written back into the description: every twin of seeds 0 to 2 long, both counts MISSED."""
    _twins_off(
        tmp_path, name, _restored(tmp_path, name, described, cells, floor), (0, 1, 2),
        described.block("visit")["n_distinct"], True,
    )


def _stabbed(near: "tuple[int, ...] | list[int]", far: "tuple[int, ...] | list[int]") -> int:
    """The fewest distances leaving one inside every rank's span, read off the generator's own spans."""
    spans = sorted((far[index], near[index]) for index in range(len(near)))
    taken = 0
    last = -1
    for furthest, nearest in spans:
        if taken == 0 or nearest > last:
            taken = taken + 1
            last = furthest
    return taken


def _matched(near: "tuple[int, ...] | list[int]", far: "tuple[int, ...] | list[int]") -> int:
    """The most different distances the ranks can take, one inside each span: every distance in turn, from the
    nearest, given to the open span that closes first (an independent count of the generator's own spans)."""
    open_spans = [(far[index], near[index]) for index in range(len(near))]
    given = 0
    for point in range(min(near), max(far) + 1):
        waiting = [span for span in open_spans if span[1] <= point <= span[0]]
        if waiting:
            chosen = min(waiting)
            open_spans = [span for span in open_spans if span is not chosen]
            given = given + 1
    return given


def _layout_counted(described: kpi_shapes.Described, floor: int, most: bool) -> int:
    """The fewest (or the most) different days the generator's own layout lets the column's two tails hold."""
    column = described.loaded.columns[0]
    assert isinstance(column.facts, contract.DatetimeFacts)
    parsed = column.n_present - column.facts.n_unparsed
    layout = generation._date_layout(column, column.facts, parsed, floor)
    apart = column.n_distinct - column.facts.n_unparsed >= parsed
    found = 0
    for plan in (layout.low, layout.high):
        assert plan is not None
        if plan.shape is None:
            found = found + len(set(plan.spots))
        elif apart:
            found = found + len(set(plan.near))
        elif most:
            found = found + _matched(plan.near, plan.far)
        else:
            found = found + _stabbed(plan.near, plan.far)
    return found


def _layout_fewest(described: kpi_shapes.Described, floor: int) -> int:
    """The fewest different days the generator's own layout lets the column's two tails hold."""
    return _layout_counted(described, floor, False)


def _layout_most(described: kpi_shapes.Described, floor: int) -> int:
    """The most different days the generator's own layout lets the column's two tails hold."""
    return _layout_counted(described, floor, True)


def test_the_count_room_rule_needs_every_pin_day_and_each_gap_s_other_groups() -> None:
    """`calendar_rules.count_room_short` on hand-made pins, Monday 1 January 2024 first (plan P4-D388).

    Two Monday pins a fortnight apart with 29 ranks between them, every
    weekday its own group holding rows: the census needs both pin days
    and one day of each of the six other weekdays -- 8. With 12 days in
    the tails, a column of 19 days leaves the body 7, less than the
    need, and is withheld; 20 leaves it the need and is published. Two
    ranks between the pins need at most two days besides them, and one
    rank one. A gap whose two pins stand on one day is no gap. Only
    groups that hold rows are counted, and the gap's own end groups are
    not (a pin day stands for them), the first pin's and the last pin's
    alike. A gap from a Monday to the Wednesday of the next week needs a
    Tuesday, a Thursday, a Friday, a Saturday and a Sunday, 7 with its
    pin days. Under groups of Monday to Friday, Saturday and Sunday, a
    gap from a Monday to the next week's Saturday needs only its two pin
    days and a Sunday, 3 in all: Tuesday to Friday stand in the first
    pin's group, and the Saturday between the pins in the last pin's. A
    gap three days wide holds only the weekdays strictly inside it, a
    merged group is one group, and a day two pins stand on is counted
    once. Where the census needs no day past the pin days the rule is
    silent whatever the room. Red when the pin days are not counted or
    are counted twice, a gap's end groups, either of them, or an empty
    group are counted, the ranks between the pins do not cap a gap, a
    gap of one rank is passed over, a one-day gap counts, a gap is
    scanned a day deep, the rule withholds at the need too, leaves the
    tails out of the room, or speaks where the census needs nothing past
    the pins.
    """
    every = _seven((40, 40, 40, 40, 40, 40, 40))
    fortnight = ((10, _MONDAY), (40, _MONDAY + 14))
    assert calendar_rules.count_room_short(every, fortnight, 19, 12)
    assert not calendar_rules.count_room_short(every, fortnight, 20, 12)
    two_ranks = ((10, _MONDAY), (13, _MONDAY + 14))
    assert calendar_rules.count_room_short(every, two_ranks, 3, 0)
    assert not calendar_rules.count_room_short(every, two_ranks, 4, 0)
    one_rank = ((10, _MONDAY), (12, _MONDAY + 14))
    assert calendar_rules.count_room_short(every, one_rank, 2, 0)
    assert not calendar_rules.count_room_short(every, one_rank, 3, 0)
    heaped = ((10, _MONDAY), (20, _MONDAY))
    assert not calendar_rules.count_room_short(every, heaped, 0, 0)
    thursdays = _seven((40, 0, 0, 40, 0, 0, 0))
    assert calendar_rules.count_room_short(thursdays, fortnight, 2, 0)
    assert not calendar_rules.count_room_short(thursdays, fortnight, 3, 0)
    wednesday = ((10, _MONDAY), (30, _MONDAY + 9))
    assert calendar_rules.count_room_short(every, wednesday, 6, 0)
    assert not calendar_rules.count_room_short(every, wednesday, 7, 0)
    shared = ((0, _MONDAY), (10, _MONDAY + 7), (20, _MONDAY + 14))
    assert calendar_rules.count_room_short(every, shared, 14, 0)
    assert not calendar_rules.count_room_short(every, shared, 15, 0)
    twice = ((0, _MONDAY), (5, _MONDAY), (20, _MONDAY + 14))
    assert calendar_rules.count_room_short(every, twice, 7, 0)
    assert not calendar_rules.count_room_short(every, twice, 8, 0)
    narrow = ((0, _MONDAY), (10, _MONDAY + 2))
    assert calendar_rules.count_room_short(every, narrow, 2, 0)
    assert not calendar_rules.count_room_short(every, narrow, 3, 0)
    merged = ((0, 4, 200), (5, 6, 80))
    assert calendar_rules.count_room_short(merged, fortnight, 2, 0)
    assert not calendar_rules.count_room_short(merged, fortnight, 3, 0)
    three = ((0, 4, 200), (5, 5, 40), (6, 6, 40))
    to_saturday = ((10, _MONDAY), (30, _MONDAY + 12))
    assert calendar_rules.count_room_short(three, to_saturday, 2, 0)
    assert not calendar_rules.count_room_short(three, to_saturday, 3, 0)
    mondays = _seven((40, 0, 0, 0, 0, 0, 0))
    assert not calendar_rules.count_room_short(mondays, fortnight, 0, 30)


def test_the_pins_are_the_boundaries_and_the_rungs_strictly_between_them() -> None:
    """`calendar_rules.body_pins`: the ranks the generator lays and no pass moves (method G7.3).

    A hundred days, ten in each tail: the boundaries at ranks 10 and 89,
    and of the eleven rungs only p25, p50 and p75 strictly between them,
    read off rank `99 * percent // 100` (p90 reads rank 89, the high
    boundary's own, and is not laid twice, nor p05 on a low boundary at
    rank 4); a percent named twice is one pin, each pin carries the day
    at its rank, and a body of one rank is one pin. Red when a rung is
    read a rank on, a rung on a boundary's rank is laid again, or the
    high boundary is left out.
    """
    every = tuple(range(1000, 1100))
    ladder = [0, 1, 5, 10, 25, 50, 75, 90, 95, 99, 100]
    assert calendar_rules.body_pins(every, 10, 10, ladder) == (
        (10, 1010), (24, 1024), (49, 1049), (74, 1074), (89, 1089),
    )
    assert calendar_rules.body_pins(every, 10, 10, [50, 50]) == ((10, 1010), (49, 1049), (89, 1089))
    assert calendar_rules.body_pins(every, 10, 10, []) == ((10, 1010), (89, 1089))
    assert calendar_rules.body_pins(every, 4, 10, [5]) == ((4, 1004), (89, 1089))
    heaped = tuple(sorted([2000] * 60 + [2003] * 40))
    assert calendar_rules.body_pins(heaped, 5, 5, [50]) == ((5, 2000), (49, 2000), (94, 2003))
    assert calendar_rules.body_pins(every, 49, 50, ladder) == ((49, 1049),)


def test_the_tails_most_is_their_listed_values_or_up_to_the_floor_and_their_spread() -> None:
    """`calendar_rules.tails_most`: the most different days the twin's two tails can hold (method G7.3b).

    Ten days a tail, one cell each, either side of a body of ten: each
    tail spreads over distances 1 to 10, so it can hold all ten days at
    any floor from 10 up, and at the floor of 4 only four; a tail that
    lists its values holds at most as many days as it lists, whatever its
    rows and the floor. Twenty cells a day out but one two days out hold
    a sum of squares of 23, which two different distances fill (1 + 4 and
    eighteen ones): two days and the two beside allowed (`SPREAD_SLACK`),
    four, at the floor of 20, and the high tail the same. A floor below
    one is read as one, the twin's tie group then taking every rank. Red
    when a distance tail counts its rows past the floor or a rank under
    it, a listed tail counts the floor, the spread is not asked or asked
    with another allowance beside it, or the floor is read as given.
    """
    spread = tuple(range(100, 110)) + tuple(range(120, 130)) + tuple(range(140, 150))
    assert calendar_rules.tails_most(spread, 10, 10, (None, None), 36) == 20
    assert calendar_rules.tails_most(spread, 10, 10, (None, None), 10) == 20
    assert calendar_rules.tails_most(spread, 10, 10, (None, None), 4) == 8
    assert calendar_rules.tails_most(spread, 10, 10, (3, None), 36) == 13
    assert calendar_rules.tails_most(spread, 10, 10, (2, 5), 36) == 7
    near = (98,) + (99,) * 19 + tuple(range(100, 130)) + (130,) * 19 + (132,)
    assert calendar_rules.tails_most(near, 20, 20, (None, None), 20) == 8
    assert calendar_rules.tails_most(near, 20, 20, (None, None), 0) == 2


@pytest.mark.parametrize("shape,low,high", [(0, 59, 40), (92, 57, 36)])
def test_a_raised_floor_withholds_a_schedule_whose_twin_would_go_long(
    tmp_path: pathlib.Path, shape: int, low: int, high: int
) -> None:
    """The review's weekly schedules at the floor of 36: withheld, and restored they come back long.

    `_weekly_schedule(0)` (270 rows, 35 different days) and
    `_weekly_schedule(92)` (538 rows, 46) publish their census at the
    floor of 11, met by their twins at seeds 0 to 2. At 36 their tails
    hold 59 and 40, and 57 and 36, rows over a handful of days, publish
    their two distances and are rebuilt with up to 36 different days
    each, so the count pass leaves the body at most 35 - 72 and 46 - 72
    days where the census needs 5 and 13: withheld, `count_room`, in the
    sentence every rule the table's own numbers decide shares. Restored,
    the census the menu offers sends their twins at seeds 0 to 2 back
    with more different values than the column holds, both counts
    MISSED (37 for 35, 53 for 46 at 493f6f8). Red when the rule is not
    asked, counts the real tails' days rather than the most the twin's
    can hold, or loses a gap.
    """
    cells = _weekly_schedule(shape)
    eleven = _described(tmp_path, f"eleven{shape}", cells, 11)
    assert eleven.block("visit")["weekday_census"], shape
    for seed in (0, 1, 2):
        twin = kpi_shapes.twin_text(eleven, seed)
        assert kpi_shapes.missed(kpi_shapes.measure(eleven, twin, f"eleven-{seed}.csv")) == [], (shape, seed)
    described = _described(tmp_path, f"raised{shape}", cells, 36)
    block = described.block("visit")
    assert (block["low_tail"]["rows"], block["high_tail"]["rows"]) == (low, high)
    assert block["low_tail"]["values"] is None and block["high_tail"]["values"] is None
    assert block["weekday_census"] == [], block["weekday_census"]
    decided = _decided(block, cells, 36)
    assert decided.reason == calendar_rules.REASON_COUNT_ROOM, decided.reason
    said = [entry["note"] for entry in described.document["publication_notes"] if entry["column"] == "visit"]
    assert any("and why is not said" in sentence for sentence in said), said
    _restored_twins_long(tmp_path, f"schedule{shape}", described, cells, 36)


def test_one_date_a_month_at_the_floor_of_50_is_withheld_and_restored_comes_back_long(tmp_path: pathlib.Path) -> None:
    """One date a month over 60 months (`_monthly(1, 2017, 60, 9740)`): published to the floor of 36, withheld at 50.

    Every weekday its own group, so a census asks the body for nearly a
    day of every group in every gap. Up to the floor of 36 both tails
    list their values and the body keeps room: the census is published
    and its twins at seeds 0 to 2 miss nothing. At 50 the low tail's 61
    rows publish their two distances, rebuilt with up to 50 different
    days: withheld, `count_room`, and restored its twins at seeds 0 to 2
    hold 75 to 77 different values for 60. Red when the rule is not asked
    or a listed tail is read as distances.
    """
    cells = _monthly(1, 2017, 60, 9740)
    for floor in (11, 36):
        described = _described(tmp_path, f"monthly{floor}", cells, floor)
        block = described.block("visit")
        assert block["low_tail"]["values"] is not None and block["high_tail"]["values"] is not None, floor
        assert len(block["weekday_census"]) == 7, (floor, block["weekday_census"])
        for seed in (0, 1, 2):
            twin = kpi_shapes.twin_text(described, seed)
            assert kpi_shapes.missed(kpi_shapes.measure(described, twin, f"monthly{floor}-{seed}.csv")) == [], (floor, seed)
    described = _described(tmp_path, "monthly50", cells, 50)
    block = described.block("visit")
    assert block["low_tail"]["values"] is None and block["low_tail"]["rows"] == 61, block["low_tail"]
    assert block["weekday_census"] == [], block["weekday_census"]
    assert _decided(block, cells, 50).reason == calendar_rules.REASON_COUNT_ROOM
    _restored_twins_long(tmp_path, "monthly50", described, cells, 50)


def test_the_producer_hands_both_rules_the_block_s_pins_and_tails(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """What `taxonomy.weekday_decision` hands the two count rules, at every floor (P4-D388 and its review, items 1 and 2).

    `_weekly_schedule(0)` with one cell written `unknown`, which no date
    member reads: the column still holds 35 different days, and its
    published count of different values is 36. At the floor of 36 both
    tails publish their distances, so their most is the floor each, 36
    and 36 though they hold 59 and 40 rows; the pins are the two
    boundaries, at ranks 59 and 229, and the rungs published between
    them, p25, p50 and p75 at ranks 67, 134 and 201. At the floor of 20
    its low tail lists two values and its high tail's 23 rows give 20,
    and the pins are the boundaries at 21 and 246 with p10 to p95
    between; at 11 its low tail lists one value and its high tail's 14
    rows give 11, the boundaries at 14 and 255 with p05 to p95 between.
    At every floor the pins are the body pins the generator lays from the
    description (`generation._date_layout`), rank for rank and day for
    day, so a pin the generator gains or loses there -- landing 3b.D4
    pins each listed date in `_heavy_layout` (plan P4-D369) -- parts
    them. Both rules are handed the column's 35 different days, never the
    published 36. The reach rule, asked where the room rule publishes, is
    handed the same pins and the fewest and most days the generator's own
    layout lets the twin's tails hold, 8 and 12 at 11 and 13 and 22 at
    20, from the member's own edges, the column's values not all
    different, and no hole. `_weekly_schedule(49)` at the floor of 20
    holds tails that differ: its low tail's 49 rows publish their
    distances and its high tail's 34 list two values, so the room rule's
    most is 20 and 2, 22, where the two tails' rows handed the other way
    round give 18, and the reach rule's fewest and most are 10 and 10,
    where handed the other way round they give 13 and 13. Red when the
    rungs are not handed over, the column's rows or its published count
    stand for its days, the settings floor is not read, a listed tail is
    handed over as one publishing its distances, the two tails' rows are
    handed over the other way round, the rules' pins part from the
    generator's body pins, the tails' fewest or most part from the
    generator's layout, or either rule is not asked at the floor of 11.
    """
    seen: "list[tuple[object, ...]]" = []
    reached: "list[tuple[object, ...]]" = []
    fewest: "list[tuple[object, ...]]" = []
    widest: "list[tuple[object, ...]]" = []
    asked = calendar_rules.count_room_short
    asked_reach = calendar_rules.count_reach_short
    asked_fewest = calendar_rules.tails_fewest
    asked_widest = calendar_rules.tails_most_rebuilt

    def recorded(groups: object, pins: "tuple[tuple[int, int], ...]", days: int, tails: int) -> bool:
        nonlocal seen
        seen += [(pins, days, tails)]
        return asked(groups, pins, days, tails)  # type: ignore[arg-type]

    def recorded_reach(
        groups: object,
        pins: "tuple[tuple[int, int], ...]",
        days: int,
        least: int,
        most: int,
        holes: "frozenset[int]" = frozenset(),
    ) -> bool:
        nonlocal reached
        reached += [(pins, days, least, most, holes)]
        return asked_reach(groups, pins, days, least, most, holes)  # type: ignore[arg-type]

    def recorded_fewest(*args: object) -> int:
        nonlocal fewest
        fewest += [args]
        return asked_fewest(*args)  # type: ignore[arg-type]

    def recorded_widest(*args: object) -> int:
        nonlocal widest
        widest += [args]
        return asked_widest(*args)  # type: ignore[arg-type]

    monkeypatch.setattr(calendar_rules, "count_room_short", recorded)
    monkeypatch.setattr(calendar_rules, "count_reach_short", recorded_reach)
    monkeypatch.setattr(calendar_rules, "tails_fewest", recorded_fewest)
    monkeypatch.setattr(calendar_rules, "tails_most_rebuilt", recorded_widest)
    cells = _weekly_schedule(0)
    ordered = sorted(_day(cell) for cell in cells)
    for floor, tails, ranks, least, most in (
        (36, 72, [59, 67, 134, 201, 229], None, None),
        (20, 22, [21, 26, 67, 134, 201, 242, 246], 13, 22),
        (11, 12, [14, 26, 67, 134, 201, 242, 255], 8, 12),
    ):
        seen.clear()
        reached.clear()
        fewest.clear()
        widest.clear()
        described = _described(tmp_path, f"floor{floor}", cells + ["unknown"], floor)
        block = described.block("visit")
        assert (block["n_distinct"], block["n_unparsed"]) == (36, 1), (floor, block["n_distinct"])
        assert len(seen) == 1, seen
        pins, days, counted = seen[0]
        assert (days, counted) == (35, tails), (floor, days, counted)
        low = block["low_tail"]["rows"]
        high = len(cells) - 1 - block["high_tail"]["rows"]
        expected = [low]
        rungs = block["date_percentiles"]
        for label, num, den in taxonomy.LADDER:
            rank = min(len(cells) - 1, ((len(cells) - 1) * num) // den)
            if rungs[label] is not None and expected[len(expected) - 1] < rank < high:
                expected += [rank]
        expected += [high]
        assert [rank for rank, _day_number in pins] == expected == ranks, (floor, pins, expected)
        assert [day for _rank, day in pins] == [ordered[rank] for rank in expected], floor
        column = described.loaded.columns[0]
        assert isinstance(column.facts, contract.DatetimeFacts)
        layout = generation._date_layout(column, column.facts, column.n_present - column.facts.n_unparsed, floor)
        assert list(pins) == [(rank, layout.body[rank]) for rank in sorted(layout.body)], (floor, layout.body)
        if least is None:
            assert reached == [] and block["weekday_census"] == [], (floor, reached)
            continue
        assert block["weekday_census"], floor
        assert len(reached) == 1 and len(fewest) == 1 and len(widest) == 1, (reached, fewest, widest)
        assert reached[0] == (pins, 35, least, most, frozenset()), (floor, reached[0])
        assert (least, most) == (_layout_fewest(described, floor), _layout_most(described, floor)), floor
        handed = fewest[0]
        assert widest[0] == handed, (floor, widest[0], handed)
        assert block["format"] == "iso-date", block["format"]
        edges = taxonomy.tail_edges(block["format"], parsing.TAIL_UNIT_DAY, "local", {})
        assert handed[4:] == (floor, edges, False, frozenset()), (floor, handed[4:])
    seen.clear()
    reached.clear()
    differing = _weekly_schedule(49)
    described = _described(tmp_path, "differing", differing, 20)
    block = described.block("visit")
    ordered_differing = tuple(sorted(_day(cell) for cell in differing))
    low, high = block["low_tail"]["rows"], block["high_tail"]["rows"]
    listed = (None, len(block["high_tail"]["values"]))
    assert block["low_tail"]["values"] is None and (low, high, listed[1]) == (49, 34, 2), (low, high, listed)
    assert block["weekday_census"], block["weekday_census"]
    assert len(seen) == 1 and len(reached) == 1, (seen, reached)
    assert seen[0][2] == calendar_rules.tails_most(ordered_differing, low, high, listed, 20) == 22, seen[0]
    assert calendar_rules.tails_most(ordered_differing, high, low, listed, 20) == 18
    assert reached[0][2:4] == (10, 10) == (_layout_fewest(described, 20), _layout_most(described, 20)), reached[0]
    sides = (
        (None, float(block["low_tail"]["mean_distance"]), float(block["low_tail"]["rms_distance"])),
        (2, None if block["high_tail"]["mean_distance"] is None else float(block["high_tail"]["mean_distance"]), None),
    )
    edges = taxonomy.tail_edges(block["format"], parsing.TAIL_UNIT_DAY, "local", {})
    assert calendar_rules.tails_fewest(ordered_differing, high, low, sides, 20, edges, False) == 13
    assert calendar_rules.tails_most_rebuilt(ordered_differing, high, low, sides, 20, edges, False) == 13


def test_at_the_floor_of_11_the_rule_is_asked_and_withholds_a_census_its_twins_met(tmp_path: pathlib.Path) -> None:
    """The rule's scope since its Codex review (item 1): asked at every floor, and its price at 11.

    `_hunt(1084)`, 95 visits over 24 days (D0's hunt batteries), at the
    floor of 11: both tails publish their distances, 17 and 13 rows, so
    their most is 11 and 11 and leaves the body 2 of its 24 days where
    the census the menu offers, Monday to Friday against the weekend,
    needs 6: withheld, `count_room`. Asked above the floor of 11 alone,
    as P4-D388 first did, the rule published it, and its twins at seeds 0
    to 4 met it with every check -- the rule's price, one of the 15
    censuses of the 26 batteries asking it at 11 withholds, every twin of
    which met them there. Red when the rule is not asked at the floor of 11.
    """
    cells = _hunt(1084)
    described = _described(tmp_path, "hunt1084", cells, 11)
    block = described.block("visit")
    assert block["weekday_census"] == [], block["weekday_census"]
    assert _decided(block, cells, 11).reason == calendar_rules.REASON_COUNT_ROOM
    ordered = tuple(sorted(_day(cell) for cell in cells))
    rungs = block["date_percentiles"]
    percents = [(100 * num) // den for label, num, den in taxonomy.LADDER if rungs[label] is not None]
    assert block["low_tail"]["values"] is None and block["high_tail"]["values"] is None
    pins = calendar_rules.body_pins(ordered, block["low_tail"]["rows"], block["high_tail"]["rows"], percents)
    most = calendar_rules.tails_most(ordered, block["low_tail"]["rows"], block["high_tail"]["rows"], (None, None), 11)
    assert (block["low_tail"]["rows"], block["high_tail"]["rows"], most, len(set(ordered))) == (17, 13, 22, 24)
    body = list(ordered[17 : len(ordered) - 13])
    groups = calendar_rules.menu_groups(calendar_rules.body_bins(body), parsing.census_floor(11))[0]
    assert groups == ((0, 4, 29), (5, 6, 36)), groups
    assert calendar_rules.count_room_short(groups, pins, len(set(ordered)), most)
    _twins_meet(tmp_path, "hunt1084", _restored(tmp_path, "hunt1084", described, cells, 11), (0, 1, 2, 3, 4))


def test_at_the_floor_of_11_a_census_whose_twin_at_seed_17_went_long_is_withheld(tmp_path: pathlib.Path) -> None:
    """The Codex review of P4-D388, item 1: the floor-11 exemption admitted a census that broke the count.

    `_hunt(690)` with one `2024-07-02` cell written `2024-05-16`: 131 rows
    over 24 dates. At the floor of 11 both its tails publish their
    distances, 16 and 11 rows, and 4a4b901 published the census the menu
    offers, Monday to Friday 73 against the weekend 31, without asking the
    count-room rule, which answers that the body is left too little room:
    its twins at seeds 2, 3 and 17 came back with 25, 27 and 27 different
    values for 24, both counts MISSED, and with 24 where the census was
    emptied. Withheld now, `count_room`: its twins at those seeds meet
    every check, and restored they come back long again. Red when the
    count-room rule is not asked at the floor of 11.
    """
    cells = _moved_hunt_690()
    assert (len(cells), len(set(cells))) == (131, 24)
    described = _described(tmp_path, "moved690", cells, 11)
    block = described.block("visit")
    assert (block["low_tail"]["rows"], block["high_tail"]["rows"]) == (16, 11)
    assert block["low_tail"]["values"] is None and block["high_tail"]["values"] is None
    assert block["weekday_census"] == [], block["weekday_census"]
    assert _decided(block, cells, 11).reason == calendar_rules.REASON_COUNT_ROOM
    _twins_meet(tmp_path, "moved690", described.loaded, (2, 3, 17))
    restored = _restored(tmp_path, "moved690", described, cells, 11)
    column = restored.columns[0]
    assert isinstance(column.facts, contract.DatetimeFacts)
    assert column.facts.weekday_census == ((0, 4, 73), (5, 6, 31)), column.facts.weekday_census
    _twins_off(tmp_path, "moved690", restored, (2, 3, 17), 24, True)


def test_the_count_reach_rule_reads_what_the_census_lets_the_body_reach() -> None:
    """`calendar_rules.count_reach_short` on hand-made pins, Monday 1 January 2024 first (the review's item 2).

    Monday to Friday holding rows and the weekend empty, two pins a
    Monday and the next week's Wednesday apart with 29 ranks between them:
    the census lets the body reach both pin days and the six weekdays
    strictly between them, 8, where without it the body would reach the
    weekend's two days too, 10. So many ranks over so few days draw every
    one of them, so the count pass may merge and the tails are read at
    their fewest: a column of 12 days whose tails hold 4 days at fewest
    needs 8 of the body and is published, a need equal to the reach;
    whose tails hold 3 at fewest, it needs 9 and is withheld, though they
    could hold 4. Where every group holds rows the census narrows nothing
    and withholds nothing, whatever the need. A gap of two ranks reaches
    two days past its pins with the census or without it. A pin day
    counted twice is one day. A hole inside the gap -- the Thursday -- is
    reached by neither, so 4 days of tails withhold; a hole on the
    Saturday narrows only what the body would reach without the census,
    so they publish. Monday to Friday holding 5 rows reaches 5 different
    days at most, so tails of 6 days withhold and of 7 publish. Where a
    gap's ranks bind before a group's count does -- one rank between a
    Monday and a Friday, three between that Friday and the next Tuesday
    -- the body reaches the three pin days, one of Tuesday to Thursday
    and the Monday, 5: a need of 6 withholds and of 5 publishes; with
    that Monday a hole a need of 5 withholds; and the first Monday pinned
    twice still reaches 5. Red when the pin days, the weekend or a hole
    are counted in the reach, the ranks between two pins do not cap a
    gap, a group's count does not cap its days, the rule withholds at a
    need equal to the reach, withholds where the census narrows nothing,
    or reads the tails' most where the count pass may merge.
    """
    weekdays = ((0, 4, 200), (5, 6, 0))
    wednesday = ((10, _MONDAY), (40, _MONDAY + 9))
    assert not calendar_rules.count_reach_short(weekdays, wednesday, 12, 4, 4)
    assert calendar_rules.count_reach_short(weekdays, wednesday, 12, 3, 3)
    assert calendar_rules.count_reach_short(weekdays, wednesday, 12, 3, 4)
    every = _seven((40, 40, 40, 40, 40, 40, 40))
    assert not calendar_rules.count_reach_short(every, wednesday, 30, 0, 0)
    two_ranks = ((10, _MONDAY), (13, _MONDAY + 9))
    assert not calendar_rules.count_reach_short(weekdays, two_ranks, 12, 0, 0)
    twice = ((0, _MONDAY), (5, _MONDAY), (40, _MONDAY + 9))
    assert not calendar_rules.count_reach_short(weekdays, twice, 12, 4, 4)
    assert calendar_rules.count_reach_short(weekdays, twice, 12, 3, 3)
    assert calendar_rules.count_reach_short(weekdays, wednesday, 12, 4, 4, frozenset({_MONDAY + 3}))
    assert not calendar_rules.count_reach_short(weekdays, wednesday, 12, 4, 4, frozenset({_MONDAY + 5}))
    few = ((0, 4, 5), (5, 6, 0))
    assert calendar_rules.count_reach_short(few, wednesday, 12, 6, 6)
    assert not calendar_rules.count_reach_short(few, wednesday, 12, 7, 7)
    tight = ((0, _MONDAY), (2, _MONDAY + 4), (6, _MONDAY + 8))
    assert calendar_rules.count_reach_short(weekdays, tight, 6, 0, 0)
    assert not calendar_rules.count_reach_short(weekdays, tight, 5, 0, 0)
    assert calendar_rules.count_reach_short(weekdays, tight, 5, 0, 0, frozenset({_MONDAY + 7}))
    tight_twice = ((0, _MONDAY), (1, _MONDAY), (3, _MONDAY + 4), (7, _MONDAY + 8))
    assert calendar_rules.count_reach_short(weekdays, tight_twice, 6, 0, 0)


def test_the_count_reach_rule_reads_the_tails_and_the_body_s_draw_as_the_count_pass_leaves_them() -> None:
    """The need is what the tails at their most leave the body, and where its draw passes that, its draw, no more than the tails' fewest leave.

    Two Mondays 700 days apart, Monday to Friday holding rows and the
    weekend empty: the census lets the body reach the two pin days and
    the 499 weekdays strictly between them where 500 ranks stand, 501.
    Those 500 ranks drawn independently over the 699 days between land on
    357.3 of them in expectation, 359.3 with the pin days: a column of 513
    days whose tails hold 6 days at fewest and 12 at most is far past that
    draw, so the count pass only splits and spreads the tails to their 12,
    the body needs 501 and the census is published; 514 withholds it, the
    need one past the reach. The same pins with 2,000 ranks between them
    draw 661.1 days, more than the count leaves the body, so the pass
    merges and may take every merge from the tails, down to their 6: 513
    withholds, and 507 publishes, its need of 501 equal to the reach. Two
    Mondays four weeks apart, 30 ranks between them: the census reaches
    21 of the 27 days between, 19 weekdays and the pin days, and the
    ranks draw 20.3 of them with the pin days. A column of 34 days whose
    tails hold 10 at fewest and 14 at most asks the body for 20 with the
    tails at their most; the pass merges, but the body keeps no more than
    the 20.3 days it drew, within the reach, and the census is published
    where the tails' fewest alone would ask 24; 36 days withholds it, 22
    past the 21. With 60 ranks between the two Mondays the draw is 26.2,
    so the merge may leave the body all 24 the tails' fewest leave: 34
    withholds. Red when the rule reads the tails' fewest whatever the
    draw, their most whatever the draw, the merge without the body's
    draw, or the gaps' days by walking them rather than counting them.
    """
    weekdays = ((0, 4, 200000), (5, 6, 0))
    sparse = ((10, _MONDAY), (511, _MONDAY + 700))
    dense = ((10, _MONDAY), (2011, _MONDAY + 700))
    assert sum(calendar_rules._weekday_days(_MONDAY + 1, _MONDAY + 699)[0:5]) == 499
    drawn = 699 * (1.0 - calendar_rules._power_of(1.0 - 1.0 / 699, 500))
    assert 357.3 < drawn < 357.4, drawn
    assert not calendar_rules.count_reach_short(weekdays, sparse, 513, 6, 12)
    assert calendar_rules.count_reach_short(weekdays, sparse, 514, 6, 12)
    assert calendar_rules.count_reach_short(weekdays, dense, 513, 6, 12)
    assert not calendar_rules.count_reach_short(weekdays, dense, 507, 6, 12)
    thirty = ((10, _MONDAY), (41, _MONDAY + 28))
    sixty = ((10, _MONDAY), (71, _MONDAY + 28))
    assert sum(calendar_rules._weekday_days(_MONDAY + 1, _MONDAY + 27)[0:5]) == 19
    drawn = 27 * (1.0 - calendar_rules._power_of(1.0 - 1.0 / 27, 30))
    assert 18.29 < drawn < 18.30, drawn
    assert not calendar_rules.count_reach_short(weekdays, thirty, 34, 10, 14)
    assert calendar_rules.count_reach_short(weekdays, thirty, 36, 10, 14)
    assert calendar_rules.count_reach_short(weekdays, sixty, 34, 10, 14)
    for first, last in ((_MONDAY - 3, _MONDAY + 30), (_MONDAY + 5, _MONDAY + 5), (_MONDAY + 9, _MONDAY + 8)):
        counted = calendar_rules._weekday_days(first, last)
        walked = [0 for _weekday in range(7)]
        for day in range(first, last + 1):
            walked[calendar_rules.weekday_of(day)] += 1
        assert counted == walked, (first, last, counted, walked)


def test_the_rebuilt_tail_is_the_generator_s_own() -> None:
    """`calendar_rules.rebuilt_tail` and `rebuilt_distances` are method G7.3b as the generator takes it.

    The producer may not import the generator, so the steps from a
    tail's published rows, distances and floor to every rank's nearest
    and furthest whole distance are written a second time in
    `calendar_rules`; here they are held equal to `generation._tail_shape`
    and `generation._tail_distance_bounds` over 600 tails drawn with
    `Random(388)` -- rows 1 to 1,000, mean distances 1 to 400, the square
    of the root-mean-square 1 to 40 times the mean's, floors 0 to 60,
    edges 1 to a million, values all different or not -- end, group and
    first grouped rank, and every rank's two distances; its rounding is
    the generator's at exact halves too; and G7.3b step 7's step inward
    off a hole is the generator's `_off_the_holes`. When the copy was
    written a grid of 607,200 such tails parted nowhere. Red when any
    operation of the copy departs from the generator's.
    """
    for value in (0.5, 1.5, 2.5, 3.5, 1048576.5, 4503599627370495.5, 2.4999999999999996, 0.49999999999999994, 7.0):
        assert calendar_rules._half_up(value) == generation._half_up(value), value
    assert (calendar_rules._half_up(2.5), calendar_rules._half_up(0.5), calendar_rules._half_up(2.4999999999999996)) == (3, 1, 2)
    draw = random.Random(388)
    for _case in range(600):
        rows = draw.choice([draw.randint(1, 40), draw.randint(41, 1000)])
        mean = draw.choice([1.0, 1.0 + draw.random(), draw.uniform(1.0, 20.0), draw.uniform(20.0, 400.0)])
        ratio = draw.choice([1.0, 1.0 + draw.random() / 1000.0, draw.uniform(1.0, 3.0), draw.uniform(3.0, 40.0)])
        root = mean * math.sqrt(ratio)
        floor = draw.choice([0, 1, 2, draw.randint(3, 60)])
        edge = draw.choice([1, draw.randint(2, 30), draw.randint(31, 10**6)])
        apart = draw.random() < 0.2
        shape = generation._tail_shape(rows, mean, root, floor, edge, apart, True)
        mixture, stretch, end, group, grouped = calendar_rules.rebuilt_tail(rows, mean, root, floor, edge, apart)
        case = (rows, mean, root, floor, edge, apart)
        assert (end, group, grouped, stretch) == (shape.end, shape.group, shape.grouped, shape.stretch), case
        assert mixture == (shape.scale, shape.power, shape.weight), case
        rebuilt = (mixture, stretch, end, group, grouped)
        near, far = generation._tail_distance_bounds(shape)
        assert calendar_rules.rebuilt_distances(rows, rebuilt, edge, apart, 0) == near, case
        assert calendar_rules.rebuilt_distances(rows, rebuilt, edge, apart, 2**64 - 1) == far, case
        boundary = 20000
        holes = frozenset(boundary + end - step for step in range(4) if draw.random() < 0.6)
        for low_side in (True, False):
            mirrored = frozenset(2 * boundary - day for day in holes) if low_side else holes
            assert calendar_rules._off_the_holes(end, boundary, low_side, mirrored) == generation._off_the_holes(
                end, boundary, low_side, {day: True for day in mirrored}
            ), case


@pytest.mark.parametrize(
    "name,floor",
    [
        ("fortnight", 21), ("schedule0", 11), ("schedule0", 20), ("hunt846", 11), ("hunt2291", 11),
        ("business_year", 20), ("days_once", 11), ("business_days", 11),
    ],
)
def test_the_tails_fewest_and_most_are_read_off_the_generator_s_own_layout(
    tmp_path: pathlib.Path, name: str, floor: int
) -> None:
    """`calendar_rules.tails_fewest` and `tails_most_rebuilt` on described columns are the generator's layout.

    The fewest and the most different days the twin's two tails can hold,
    as the producer counts them from the description, against the same
    counts read off `generation._date_layout`: a listed tail's values, a
    tail of all different values its ranks -- 200 days written once each
    -- and otherwise the fewest distances that leave one inside every
    rank's span between its nearest and furthest, and the most that can
    stand one inside each span, each its own, counted here by giving every
    distance in turn to the open span that closes first. One row a
    business day holds tails of 6 days at fewest and 11 at most a side.
    Red when either of the producer's counts parts from the generator's
    layout.
    """
    cells = {
        "fortnight": _fortnight,
        "schedule0": lambda: _weekly_schedule(0),
        "hunt846": lambda: _hunt(846),
        "hunt2291": lambda: _hunt(2291),
        "business_year": _business_year,
        "days_once": lambda: [
            (datetime.date(2024, 1, 1) + datetime.timedelta(days=step)).isoformat() for step in range(200)
        ],
        "business_days": _one_row_a_business_day,
    }[name]()
    described = _described(tmp_path, name, cells, floor)
    block = described.block("visit")
    ordered = tuple(sorted(_day(cell) for cell in cells))
    sides = []
    for key in ("low_tail", "high_tail"):
        tail = block[key]
        listed = len(tail["values"]) if tail["values"] is not None else None
        mean = None if tail["mean_distance"] is None else float(tail["mean_distance"])
        root = None if tail["rms_distance"] is None else float(tail["rms_distance"])
        sides += [(listed, mean, root)]
    handed = (
        ordered,
        block["low_tail"]["rows"],
        block["high_tail"]["rows"],
        (sides[0], sides[1]),
        floor,
        taxonomy.tail_edges(block["format"], parsing.TAIL_UNIT_DAY, "local", {}),
        block["n_distinct"] - block["n_unparsed"] >= len(ordered),
    )
    counted = (calendar_rules.tails_fewest(*handed), calendar_rules.tails_most_rebuilt(*handed))
    assert counted == (_layout_fewest(described, floor), _layout_most(described, floor)), (name, floor, counted)
    if name == "business_days":
        assert counted == (12, 22), counted


def test_the_tails_fewest_steps_a_rebuilt_end_off_a_hole_as_the_generator_does() -> None:
    """G7.3b step 7 inside `calendar_rules.tails_fewest`: an absent day at a rebuilt tail's end.

    A high tail of 13 rows -- eight a day past its boundary and one each at
    2, 4, 6, 8 and 10 days -- beside a low tail listing one value, at the
    floor of 11: the twin rebuilds the high tail with its end 9 days out,
    and its ranks' spans hold 5 different days at fewest, 6 with the low
    tail's. A published absent spelling naming the end's day steps the end
    inward as the generator steps it (`generation._off_the_holes`), the
    ranks inside it raise it back where they stand further out, and the
    spans then hold 4 at fewest: the generator's own spans, its shape
    stepped and replaced as `_date_tail_plan` replaces it, are the same
    rank for rank, and they can hold 8 different days at most, 9 with the
    low tail's. A tail of 7 rows -- 1, 1, 2, 2, 3, 5 and 8 days out --
    rebuilt with its end at 7, absent days at 7 and 6 stepping it to 5,
    is raised back to where the rank inside it stands, as the generator
    raises it, rank for rank. Red when the count skips the step, or the
    copy does not raise a stepped end to the ranks inside it.
    """
    distances = [1, 1, 1, 1, 1, 1, 1, 1, 2, 4, 6, 8, 10]
    ordered = tuple([4999, 4999] + list(range(5000, 5100)) + sorted(5099 + distance for distance in distances))
    at = ordered[len(ordered) - 1 - len(distances)]
    mean = sum(distances) / len(distances)
    root = math.sqrt(sum(distance * distance for distance in distances) / len(distances))
    published = ((1, 1.0, None), (None, mean, root))
    edges = (0, 1000000)
    edge = edges[1] - at
    mixture, stretch, end, group, grouped = calendar_rules.rebuilt_tail(13, mean, root, 11, edge, False)
    assert (end, grouped) == (9, 10), (end, grouped)
    holes = frozenset({at + end})
    shape = generation._tail_shape(13, mean, root, 11, edge, False, True)
    stepped = generation._off_the_holes(shape.end, at, False, {day: True for day in holes})
    kept = generation._off_the_holes(shape.group, at, False, {day: True for day in holes})
    moved = dataclasses.replace(shape, end=max(stepped, kept), group=kept)
    near, far = generation._tail_distance_bounds(moved)
    copied = (mixture, stretch, max(calendar_rules._off_the_holes(end, at, False, holes), kept), kept, grouped)
    assert calendar_rules.rebuilt_distances(13, copied, edge, False, 0) == near
    assert calendar_rules.rebuilt_distances(13, copied, edge, False, 2**64 - 1) == far
    assert calendar_rules.tails_fewest(ordered, 2, 13, published, 11, edges, False) == 6
    assert calendar_rules.tails_fewest(ordered, 2, 13, published, 11, edges, False, holes) == 1 + _stabbed(near, far) == 5
    assert calendar_rules.tails_most_rebuilt(ordered, 2, 13, published, 11, edges, False, holes) == 1 + _matched(near, far) == 9
    shorter = [1, 1, 2, 2, 3, 5, 8]
    mean = sum(shorter) / len(shorter)
    root = math.sqrt(sum(distance * distance for distance in shorter) / len(shorter))
    mixture, stretch, end, group, grouped = calendar_rules.rebuilt_tail(7, mean, root, 11, edge, False)
    assert (end, grouped) == (7, 7), (end, grouped)
    holes = frozenset({at + 7, at + 6})
    assert calendar_rules._off_the_holes(end, at, False, holes) == 5
    shape = generation._tail_shape(7, mean, root, 11, edge, False, True)
    moved = dataclasses.replace(shape, end=generation._off_the_holes(shape.end, at, False, {day: True for day in holes}))
    near, far = generation._tail_distance_bounds(moved)
    assert far[0] > 5, far
    copied = (mixture, stretch, 5, group, grouped)
    assert calendar_rules.rebuilt_distances(7, copied, edge, False, 0) == near
    assert calendar_rules.rebuilt_distances(7, copied, edge, False, 2**64 - 1) == far


def test_a_census_that_keeps_the_body_from_a_day_its_rebuilt_tail_lost_is_withheld(tmp_path: pathlib.Path) -> None:
    """The Codex review of P4-D388, item 2: a count lost the other way, a rebuilt tail short of a day.

    `_fortnight()`, 14 days from Monday 29 January 2024 holding 23, 3, 14,
    8, 23, 0, 0, 4, 20, 30, 20, 8, 1 and 2 rows: 156 rows over 12 dates.
    At the floor of 21 the low tail lists its one Monday, and the high
    tail's 31 rows -- 20, 8, 1 and 2 at one to four days past the
    boundary -- publish their two distances, which the generator rebuilds
    on one to three days whatever its draws: three at the most. The body
    holds every weekday between the boundaries, the census the menu offers
    is Monday to Friday 102 against the weekend 0, and 4a4b901 published
    it: the count pass made up the tail's lost day on the empty weekend,
    the day pass moved it off, and the twins at seeds 0, 7 and 31 held 11
    different values for 12, both counts MISSED, where the census emptied
    held 12. The twin's tails hold 4 days at fewest and at most, its body
    draws every one of its 9 days, so the body needs 8, and the census
    lets it reach 7 of the 9 it reaches without: withheld,
    `count_reach`, in the sentence every rule the table's own numbers
    decide shares. Its twins at those seeds meet every check; restored,
    they come back short again. Red when the rule is not asked, reads the
    real tails' days in place of the rebuilt tails' fewest, or counts the
    empty weekend in the body's reach.
    """
    cells = _fortnight()
    assert (len(cells), len(set(cells))) == (156, 12)
    described = _described(tmp_path, "fortnight", cells, 21)
    block = described.block("visit")
    assert block["low_tail"]["values"] == ["2024-01-29"] and block["low_tail"]["rows"] == 23, block["low_tail"]
    assert block["high_tail"]["values"] is None and block["high_tail"]["rows"] == 31, block["high_tail"]
    assert block["weekday_census"] == [], block["weekday_census"]
    decided = _decided(block, cells, 21)
    assert decided.reason == calendar_rules.REASON_COUNT_REACH, decided.reason
    said = [entry["note"] for entry in described.document["publication_notes"] if entry["column"] == "visit"]
    assert any("and why is not said" in sentence for sentence in said), said
    assert _layout_fewest(described, 21) == 4
    _twins_meet(tmp_path, "fortnight", described.loaded, (0, 7, 31))
    restored = _restored(tmp_path, "fortnight", described, cells, 21)
    column = restored.columns[0]
    assert isinstance(column.facts, contract.DatetimeFacts)
    assert column.facts.weekday_census == ((0, 4, 102), (5, 6, 0)), column.facts.weekday_census
    _twins_off(tmp_path, "fortnight", restored, (0, 7, 31), 12, False)


def test_a_declared_day_inside_the_body_s_span_is_no_day_the_body_reaches(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The holes the producer hands the reach rule (the review's item 2): a declared day no rank is moved onto.

    `_fortnight()` with its Thursday's eight dates gone and 25 cells
    written `2024-02-01` declared missing (`--missing-value`): at the floor
    of 21 the column publishes that spelling among its absent ones, so the
    Thursday between its boundaries is a published hole the twin's day
    pass moves no rank onto. Its body holds every other weekday between
    the boundaries, 6, its high tail is rebuilt on three days at most, and
    the census the menu offers, Monday to Friday 94 against the weekend 0,
    lets the body reach those 6 of the 7 days the count asks of it:
    withheld, `count_reach`. The producer hands the tails' count the same
    day, which G7.3b steps a tail's end and group off. Its twins at seeds
    0, 7 and 31 meet every check; restored, they miss both distinct
    counts. Red when the producer hands the rule no holes, which counts
    the Thursday in the body's reach and publishes, or hands the tails'
    count none of the column's absent days.
    """
    handed: "list[tuple[object, ...]]" = []
    asked_fewest = calendar_rules.tails_fewest

    def recorded_fewest(*args: object) -> int:
        nonlocal handed
        handed += [args]
        return asked_fewest(*args)  # type: ignore[arg-type]

    monkeypatch.setattr(calendar_rules, "tails_fewest", recorded_fewest)
    declared = ("2024-02-01",)
    cells = [cell for cell in _fortnight() if cell != "2024-02-01"] + ["2024-02-01" for _copy in range(25)]
    described = _described_declaring(tmp_path, "declared", cells, 21, declared)
    assert len(handed) == 1 and handed[0][7] == frozenset({_day("2024-02-01")}), handed
    block = described.block("visit")
    assert block["missing_by_source"] == {"2024-02-01": 25}, block["missing_by_source"]
    assert block["weekday_census"] == [], block["weekday_census"]
    present = [cell for cell in cells if cell != "2024-02-01"]
    decided = taxonomy.weekday_decision(
        block,
        tuple(sorted(_day(cell) for cell in present)),
        block["n_distinct"],
        taxonomy.Settings(small_cell_floor=21, declared_missing_values=declared),
        texts=len(set(present)),
    )
    assert decided.reason == calendar_rules.REASON_COUNT_REACH, decided.reason
    _twins_meet(tmp_path, "declared", described.loaded, (0, 7, 31))
    restored = _restored(tmp_path, "declared", described, present, 21)
    column = restored.columns[0]
    assert isinstance(column.facts, contract.DatetimeFacts)
    assert column.facts.weekday_census == ((0, 4, 94), (5, 6, 0)), column.facts.weekday_census
    for seed in (0, 7, 31):
        written = fixtures.write(tmp_path, f"declared-off-{seed}.csv", rendering.twin_csv(generation.generate(restored, seed)))
        missed = kpi_shapes.missed(validation.measure(restored, str(written)))
        assert "visit:distinct.n_distinct" in missed and "visit:distinct.n_distinct_folded" in missed, (seed, missed)


def test_one_row_a_business_day_keeps_its_census_its_count_pass_spreading_the_tails(tmp_path: pathlib.Path) -> None:
    """The count-reach rule's price kept off a column twins meet: a sparse body, its count pass only splitting.

    `_one_row_a_business_day()`, 1,181 rows over 1,180 business days and
    the weekend empty (the gate's `bizlog_x1_s1`). At the floor of 11 its
    tails' 11 rows a side publish their distances, and the twin rebuilds
    each on 6 days at fewest and 11 at most; its census, one group a
    weekday and the weekend 0, lets the body reach every one of the 1,158
    business days between the boundaries, which a need read at the
    fewest, 1,168, would pass. But the body's 1,159 ranks drawn over its
    1,610 days land on about 830 of them, far short of the count, so the
    count pass only splits: it spreads the tails' ranks onto their own
    spans' free days, and the tails hold their most, 22, which leaves the
    body exactly the 1,158 the census lets it reach. Published at the
    floors of 11, 20, 36 and 50, where the tails' fewest and most are 12
    and 22, 22 and 40, 38 and 72, and 52 and 100, and its twins at seeds
    0 and 1 at the floors of 11 and 50 meet every check, holding 11 days
    in each tail at 11. The rule as first repaired read the fewest
    whatever the draw and withheld all four. Red when the rule reads the
    tails' fewest where the count pass only splits.
    """
    cells = _one_row_a_business_day()
    assert (len(cells), len(set(cells))) == (1181, 1180)
    for floor, least, most in ((11, 12, 22), (20, 22, 40), (36, 38, 72), (50, 52, 100)):
        described = _described(tmp_path, f"business{floor}", cells, floor)
        block = described.block("visit")
        assert block["low_tail"]["values"] is None and block["high_tail"]["values"] is None, floor
        assert (_layout_fewest(described, floor), _layout_most(described, floor)) == (least, most), floor
        assert _decided(block, cells, floor).reason == "", floor
        groups = tuple((group["first"], group["last"], group["count"]) for group in block["weekday_census"])
        assert groups[len(groups) - 1] == (5, 6, 0), groups
        if floor not in (11, 50):
            continue
        for seed in (0, 1):
            twin = generation.generate(described.loaded, seed)
            held = sorted(_day(cell) for cell in twin.columns[0])
            assert len(set(held)) == 1180, (floor, seed)
            if floor == 11:
                assert (len(set(held[:11])), len(set(held[len(held) - 11 :]))) == (11, 11), seed
            written = fixtures.write(tmp_path, f"business{floor}-{seed}.csv", rendering.twin_csv(twin))
            assert kpi_shapes.missed(validation.measure(described.loaded, str(written))) == [], (floor, seed)


def test_two_rows_a_business_day_are_withheld_though_their_twins_meet_their_census(tmp_path: pathlib.Path) -> None:
    """The count-reach rule's price (the review's item 2): a census its twins meet, withheld where the count pass merges.

    `_two_rows_a_business_day()`, 1,063 rows over 520 business days and
    the weekend empty. At the floor of 11 its tails publish their
    distances, and the twin rebuilds them on 10 days at fewest and 16 at
    most. Its body's ranks draw more days than the count leaves the body,
    so the count pass merges, and the rule reads every merge it may make
    as taken from the tails, down to their fewest: the body then needs
    more days than the census, each weekday its own group and the
    weekend 0, lets it reach -- every business day holds a row, so it
    reaches the body's own days and no more -- and the census is
    withheld, `count_reach`, at the floors of 11, 20, 36 and 50 alike.
    Restored at 11, its twins at seeds 0 to 2 hold all 520 days and miss
    no check. That is the rule's price, and it falls on columns holding a
    row on every day their census allows, where the count pass merges
    (the next test holds both sides of that); the same reading withholds
    `_hunt(2291)` and the short logs. Red when the merge stops being read
    at the tails' fewest -- a change that must be measured again on the
    columns this file holds short.
    """
    cells = _two_rows_a_business_day()
    assert (len(cells), len(set(cells))) == (1063, 520)
    for floor in (11, 20, 36, 50):
        described = _described(tmp_path, f"two{floor}", cells, floor)
        block = described.block("visit")
        assert block["weekday_census"] == [], (floor, block["weekday_census"])
        assert _decided(block, cells, floor).reason == calendar_rules.REASON_COUNT_REACH, floor
        if floor != 11:
            continue
        assert block["low_tail"]["values"] is None and block["high_tail"]["values"] is None
        assert (_layout_fewest(described, 11), _layout_most(described, 11)) == (10, 16)
        restored = _restored(tmp_path, "two11", described, cells, 11)
        column = restored.columns[0]
        assert isinstance(column.facts, contract.DatetimeFacts)
        assert column.facts.weekday_census[len(column.facts.weekday_census) - 1] == (5, 6, 0)
        _twins_meet(tmp_path, "two11", restored, (0, 1, 2))


def test_the_reach_rule_s_price_falls_where_every_day_the_census_allows_holds_a_row(tmp_path: pathlib.Path) -> None:
    """The columns the count-reach rule's price falls on (the verification of P4-D388's Codex review).

    The price was recorded on logs of one and a half to two rows a
    business day. Measured again, it falls on columns holding a row on
    EVERY day their census allows, where the count pass merges: the body
    can then reach its own days and no more, and a need read at the
    tails' fewest passes them. Close a few of those days and the census
    is published: `_two_rows_a_business_day()` with the 21 federal
    holidays of 2022 and 2023 closed, every other day as it was, 1,017
    rows over 499 days, keeps its census at the floors of 11, 20, 36 and
    50, each weekday its own group and the weekend 0 -- a closed day
    inside the body is a day the census allows that no row holds, and
    the body reaches it -- and its twins at seeds 0 to 2 meet it at 11.
    And the price is no business-day log's alone: three clinic days a
    week, `_three_clinic_days_a_week()`, 242 rows over 156 days, its
    census Monday, Wednesday and Friday each its own group and Tuesday,
    Thursday and the weekend 0, is withheld at 11, 20 and 36,
    `count_reach`, though its twins at seeds 0 to 2 meet it restored at
    11; at 50 the census joins Monday to Friday against the weekend,
    allowing the empty Tuesdays and Thursdays, and is published. Red when
    the rule withholds a column with an allowed day left empty, or
    publishes a full clinic week: either moves the price that P4-D388,
    K-S3-59 and the changelog record.
    """
    closed = _two_rows_a_business_day(_FEDERAL_HOLIDAYS)
    assert (len(closed), len(set(closed))) == (1017, 499)
    assert len(_FEDERAL_HOLIDAYS) == 21 and not _FEDERAL_HOLIDAYS & {datetime.date.fromisoformat(cell) for cell in closed}
    for floor in (11, 20, 36, 50):
        described = _described(tmp_path, f"closed{floor}", closed, floor)
        block = described.block("visit")
        assert _decided(block, closed, floor).reason == "", floor
        groups = tuple((group["first"], group["last"], group["count"]) for group in block["weekday_census"])
        assert [(first, last) for first, last, _count in groups] == [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 6)], groups
        assert groups[len(groups) - 1] == (5, 6, 0), groups
        if floor == 11:
            _twins_meet(tmp_path, "closed11", described.loaded, (0, 1, 2))
    clinic = _three_clinic_days_a_week()
    assert (len(clinic), len(set(clinic))) == (242, 156)
    assert {datetime.date.fromisoformat(cell).weekday() for cell in clinic} == {0, 2, 4}
    for floor in (11, 20, 36):
        described = _described(tmp_path, f"clinic{floor}", clinic, floor)
        block = described.block("visit")
        assert block["weekday_census"] == [], (floor, block["weekday_census"])
        assert _decided(block, clinic, floor).reason == calendar_rules.REASON_COUNT_REACH, floor
        if floor != 11:
            continue
        restored = _restored(tmp_path, "clinic11", described, clinic, 11)
        column = restored.columns[0]
        assert isinstance(column.facts, contract.DatetimeFacts)
        assert column.facts.weekday_census == ((0, 0, 73), (1, 1, 0), (2, 2, 72), (3, 3, 0), (4, 4, 75), (5, 6, 0))
        _twins_meet(tmp_path, "clinic11", restored, (0, 1, 2))
    described = _described(tmp_path, "clinic50", clinic, 50)
    block = described.block("visit")
    assert _decided(block, clinic, 50).reason == ""
    groups = tuple((group["first"], group["last"], group["count"]) for group in block["weekday_census"])
    assert groups == ((0, 4, 142), (5, 6, 0)), groups


@pytest.mark.parametrize(
    "name,floor,days",
    [("hunt846", 11, 11), ("hunt846", 20, 11), ("hunt2291", 11, 17), ("business_year", 11, 260), ("business_year", 20, 260)],
)
def test_the_batteries_columns_their_census_left_short_are_withheld(
    tmp_path: pathlib.Path, name: str, floor: int, days: int
) -> None:
    """The columns of the 26 batteries whose census left their twins a value short at 4a4b901 (the review's item 2).

    `_hunt(846)` at the floors of 11 and 20, `_hunt(2291)` at 11, and a
    year of business days at 11 and 20 (D0's `attack2:mon_fri_52_1000`):
    each published its census, every weekday between its boundaries held a
    date, and a tail its twin rebuilds on fewer days than the real one
    left the body nowhere to make them up, so every twin at seeds 0 to 4
    held one value fewer than the column, where the census withheld kept
    the count. Withheld now, `count_reach`: their twins at seeds 0 to 2
    meet every check, and restored they come back short. Red when the
    rule is not asked or lets any of them through.
    """
    cells = {"hunt846": lambda: _hunt(846), "hunt2291": lambda: _hunt(2291), "business_year": _business_year}[name]()
    assert len(set(cells)) == days
    described = _described(tmp_path, f"{name}{floor}", cells, floor)
    block = described.block("visit")
    assert block["weekday_census"] == [], (name, floor, block["weekday_census"])
    assert _decided(block, cells, floor).reason == calendar_rules.REASON_COUNT_REACH, (name, floor)
    _twins_meet(tmp_path, f"{name}{floor}", described.loaded, (0, 1, 2))
    _twins_off(
        tmp_path, f"{name}{floor}", _restored(tmp_path, f"{name}{floor}", described, cells, floor), (0, 1, 2), days, False
    )


def test_at_the_floor_of_12_the_rule_is_asked_and_withholds_a_census_whose_twins_would_go_long(
    tmp_path: pathlib.Path,
) -> None:
    """The rule at the floor of 12 (plan P4-D388): a census 493f6f8 published there left its twins long.

    `_hunt(690)`, 131 visits over 24 days (D0's hunt batteries), at the
    floor of 12: both tails publish their distances, 16 and 12 rows, so
    their most is 12 and 12 and leaves the body none of its 24 days,
    where the census the menu offers, Monday to Friday against the
    weekend, needs 9. Withheld, `count_room`; restored, its twins at
    seeds 0 to 2 hold more different values than the column, both counts
    MISSED, as 493f6f8's twins did at seeds 0 to 4 (25 to 27 for 24).
    Red when the rule is not asked at the floor of 12.
    """
    cells = _hunt(690)
    described = _described(tmp_path, "hunt690", cells, 12)
    block = described.block("visit")
    assert block["weekday_census"] == [], block["weekday_census"]
    assert _decided(block, cells, 12).reason == calendar_rules.REASON_COUNT_ROOM
    _restored_twins_long(tmp_path, "hunt690", described, cells, 12)


def test_at_the_floor_of_20_a_census_whose_room_equals_its_need_is_published_and_met(tmp_path: pathlib.Path) -> None:
    """A room equal to the need publishes the census (plan P4-D388, its review's item 1).

    `_hunt(169)`, 122 visits over 27 days (D0's hunt batteries), at the
    floor of 20: both tails publish their distances, 23 and 24 rows, so
    their most is 10 and 11 by their spread and leaves the body 6 of its
    27 days, exactly what its census, Monday to Friday against the
    weekend, needs; a day fewer would withhold it. Published, and its
    twins at seeds 0 to 4 meet every check, their tails holding 11 days.
    Every census of the 26 batteries standing at its need was met so, 19
    at the floor of 20 and one at 50. Red when the rule withholds at the
    need too.
    """
    cells = _hunt(169)
    described = _described(tmp_path, "hunt169", cells, 20)
    block = described.block("visit")
    groups = tuple((group["first"], group["last"], group["count"]) for group in block["weekday_census"])
    assert groups == ((0, 4, 43), (5, 6, 32)), groups
    assert _decided(block, cells, 20).reason == ""
    ordered = tuple(sorted(_day(cell) for cell in cells))
    rungs = block["date_percentiles"]
    percents = [(100 * num) // den for label, num, den in taxonomy.LADDER if rungs[label] is not None]
    assert block["low_tail"]["values"] is None and block["high_tail"]["values"] is None
    low, high = block["low_tail"]["rows"], block["high_tail"]["rows"]
    pins = calendar_rules.body_pins(ordered, low, high, percents)
    most = calendar_rules.tails_most(ordered, low, high, (None, None), 20)
    assert (low, high, most, len(set(ordered))) == (23, 24, 21, 27)
    assert not calendar_rules.count_room_short(groups, pins, 27, most)
    assert calendar_rules.count_room_short(groups, pins, 26, most)
    for seed in (0, 1, 2, 3, 4):
        twin = kpi_shapes.twin_text(described, seed)
        assert kpi_shapes.missed(kpi_shapes.measure(described, twin, f"hunt169-{seed}.csv")) == [], seed


# The mini battery: (builder, shape) -> the decision at the floors 11, 20, 36 and 50, "" where published.
_ROOM = calendar_rules.REASON_COUNT_ROOM
_BATTERY = {
    ("schedule", 0): ("", "", _ROOM, ""),
    ("schedule", 1): ("", "", _ROOM, _ROOM),
    ("schedule", 92): ("", "", _ROOM, _ROOM),
    ("clinic", 45): ("", "", _ROOM, _ROOM),
    ("schedule", 5): ("", "", _ROOM, _ROOM),
    ("schedule", 6): ("", "", "", _ROOM),
    ("schedule", 4): ("", "", "", ""),
    ("schedule", 17): ("", "", "", ""),
    ("clinic", 61): ("", "", "", ""),
}


@pytest.mark.parametrize("builder,shape", sorted(_BATTERY))
def test_nine_schedules_take_their_measured_decisions_and_their_published_censuses_are_met(
    tmp_path: pathlib.Path, builder: str, shape: int
) -> None:
    """Nine schedules at the floors of 11, 20, 36 and 50: each decision, and every census published met at seeds 0 and 1.

    Weekly schedules and clinics of the review's batteries. At 493f6f8
    the census of `schedule` 0 at the floor of 36, and of `schedule` 1
    and 92 and `clinic` 45 at 36 and 50, left their twins long: each is
    withheld now. `schedule` 5 at 36 and 50 and `schedule` 6 at 50 are
    withheld too though 493f6f8's twins met them -- the rule's price,
    their rebuilt tails counted at the most the floor allows where they
    held fewer days. `schedule` 4 and 17 and `clinic` 61, their tails
    listing their values, publish at every floor, and `schedule` 0 again
    at 50, where its census is Monday to Friday against the weekend and
    needs no day past the pin days. Every twin of a census published here,
    at seeds 0 and 1, misses no check; that is what these nine measure,
    not a promise about every column. Red when the rule stops withholding
    a long schedule, withholds a census whose tails list their values, or
    speaks where the census needs no day past the pins.
    """
    cells = _weekly_schedule(shape) if builder == "schedule" else _weekly_clinic(shape)
    for floor, reason in zip((11, 20, 36, 50), _BATTERY[(builder, shape)]):
        described = _described(tmp_path, f"{builder}{shape}-{floor}", cells, floor)
        block = described.block("visit")
        decided = _decided(block, cells, floor)
        assert decided.reason == reason, (builder, shape, floor, decided.reason)
        assert bool(block["weekday_census"]) == (reason == ""), (builder, shape, floor)
        if reason:
            continue
        for seed in (0, 1):
            twin = kpi_shapes.twin_text(described, seed)
            assert kpi_shapes.missed(kpi_shapes.measure(described, twin, f"twin-{floor}-{seed}.csv")) == [], (
                builder, shape, floor, seed,
            )


def test_fifteen_mondays_at_the_floor_of_36_come_back_long_with_or_without_their_census(tmp_path: pathlib.Path) -> None:
    """The stated limit beside the rules (the Codex review of P4-D388, item 3): tails rebuilt long whatever the census.

    Fifteen consecutive Mondays from 1 January 2024, ten rows each, at the
    floor of 36: both tails publish their two distances over 40 rows, and
    the twin rebuilds them on at least 30 different days whatever its
    draws (`tails_fewest`), twice the column's 15. Its census, Monday 70
    against Tuesday to Sunday 0, needs no day past the pins and asks the
    body for nothing its tails take away, so neither count rule withholds
    it, and its twins at seeds 0 to 2 hold 33 different values for 15 --
    and 33 with the census emptied. The census is not the cause, and the
    count rules do not claim this column: the twin's report names the
    deviation and the validator reads both distinct counts as WITHIN-BOUND,
    the window the tails' construction allows, as P4-D388 records. Red when
    the limit changes and nothing records it.
    """
    cells = _mondays()
    described = _described(tmp_path, "mondays", cells, 36)
    block = described.block("visit")
    assert (block["low_tail"]["rows"], block["high_tail"]["rows"]) == (40, 40)
    assert block["low_tail"]["values"] is None and block["high_tail"]["values"] is None
    groups = tuple((group["first"], group["last"], group["count"]) for group in block["weekday_census"])
    assert groups == ((0, 0, 70), (1, 6, 0)), groups
    assert _layout_fewest(described, 36) == 30
    document = dict(described.document)
    document["columns"] = [dict(block, weekday_census=[])]
    emptied = contract.load_profile(str(fixtures.write_profile(tmp_path, "mondays-emptied.json", document)))
    for name, loaded in (("published", described.loaded), ("emptied", emptied)):
        for seed in (0, 1, 2):
            twin = generation.generate(loaded, seed)
            assert len(set(twin.columns[0])) == 33, (name, seed)
            written = fixtures.write(tmp_path, f"mondays-{name}-{seed}.csv", rendering.twin_csv(twin))
            verdicts = {
                check.subcheck: check.verdict
                for check in validation.measure(loaded, str(written)).checks
                if check.column == "visit" and check.subcheck in ("distinct.n_distinct", "distinct.n_distinct_folded")
            }
            assert verdicts == {
                "distinct.n_distinct": validation.WITHIN_BOUND,
                "distinct.n_distinct_folded": validation.WITHIN_BOUND,
            }, (name, seed, verdicts)


def test_k_s3_59_claims_what_was_measured_and_states_the_limit_beside_it() -> None:
    """K-S3-59 and the landing's changelog entry say what was measured, never that every census keeps its count (item 3).

    The ledger entry's name said that every census published keeps its
    twins' count, which fifteen Mondays at the floor of 36 disprove, the
    census not their cause. Its name now claims what its nodes and the
    batteries measured, its evidence and the changelog name the limit,
    and neither says the rules repair it. And the verification of the
    review found the count-reach rule's price recorded on the wrong
    columns, logs of one and a half to two rows a business day: P4-D388,
    the entry's evidence and the changelog now name the columns it falls
    on, those holding a row on every day their census allows, as
    `test_the_reach_rule_s_price_falls_where_every_day_the_census_allows_holds_a_row`
    holds. Red when the name claims every published census again, the
    limit goes unnamed, or the price is put back on rows a business day.
    """
    ledger = json.loads((_ROOT / "tests" / "kpi" / "ledger.json").read_text(encoding="utf-8"))
    entry = [item for item in ledger["entries"] if item["id"] == "K-S3-59"][0]
    assert "every one published keeps" not in entry["name"], entry["name"]
    assert "measured" in entry["name"] and "fifteen Mondays" in entry["name"], entry["name"]
    assert "fifteen Mondays" in entry["evidence"], entry["evidence"]
    changelog = (_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    start = changelog.index("**Landing 3b.D1b**")
    section = changelog[start : changelog.index("\n### ", start)]
    assert "fifteen Mondays" in section, section
    assert "no longer leaves a twin with too many different days" not in changelog
    plan = (_ROOT / "docs" / "plans" / "phase-4-columns.md").read_text(encoding="utf-8")
    begin = plan.index("## Decision P4-D388")
    end = plan.find("\n## ", begin)
    decision = plan[begin:] if end < 0 else plan[begin:end]
    for name, text in (("P4-D388", decision), ("K-S3-59", entry["evidence"]), ("the changelog", section)):
        flat = " ".join(text.split())
        assert "every day their census allows" in flat, name
        assert "one and a half to two rows a business day" not in flat, name

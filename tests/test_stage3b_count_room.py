"""Landing 3b.D1b (plan P4-D388): above the floor of 11 no published weekday census leaves a twin holding too many values.

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
would have met. It is asked above the floor of 11, the floor the
few-dates rule was measured at (`COUNT_ROOM_ABOVE_FLOOR`): there no
published census was measured to leave a twin long, and the rule asked
there withheld only censuses whose twins met them.

Each test names the mutation that turns it red.
"""

from __future__ import annotations

import datetime
import pathlib
import random

import pytest

import fixtures
import kpi_shapes
from synthtwin import calendar_rules, contract, generation, parsing, rendering, taxonomy, validation

# Monday 1 January 2024 as a day number counted from 1970-01-01.
_MONDAY = 19723


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


def _day(cell: str) -> int:
    """An ISO date as a day number counted from 1970-01-01."""
    return parsing.days_from_civil(int(cell[0:4]), int(cell[5:7]), int(cell[8:10]))


def _described(tmp_path: pathlib.Path, name: str, cells: "list[str]", floor: int) -> kpi_shapes.Described:
    return kpi_shapes.describe(tmp_path / name, name, "visit\n" + "".join(f"{cell}\n" for cell in cells), floor)


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


def _restored_twins_long(
    tmp_path: pathlib.Path, name: str, described: kpi_shapes.Described, cells: "list[str]", floor: int
) -> None:
    """The census the menu offers, written back into the description: every twin of seeds 0 to 2 long, both counts MISSED."""
    block = described.block("visit")
    body = sorted(_day(cell) for cell in cells)[block["low_tail"]["rows"] : len(cells) - block["high_tail"]["rows"]]
    groups, _entry = calendar_rules.menu_groups(calendar_rules.body_bins(body), parsing.census_floor(floor))
    document = dict(described.document)
    document["columns"] = [
        dict(block, weekday_census=[{"first": first, "last": last, "count": count} for first, last, count in groups])
    ]
    restored = contract.load_profile(str(fixtures.write_profile(tmp_path, f"{name}-restored.json", document)))
    for seed in (0, 1, 2):
        twin = generation.generate(restored, seed)
        assert len(set(twin.columns[0])) > block["n_distinct"], (name, seed)
        written = fixtures.write(tmp_path, f"{name}-restored-{seed}.csv", rendering.twin_csv(twin))
        missed = kpi_shapes.missed(validation.measure(restored, str(written)))
        assert "visit:distinct.n_distinct" in missed and "visit:distinct.n_distinct_folded" in missed, (name, seed, missed)


def test_the_count_room_rule_needs_every_pin_day_and_each_gap_s_other_groups() -> None:
    """`calendar_rules.count_room_short` on hand-made pins, Monday 1 January 2024 first (plan P4-D388).

    Two Monday pins a fortnight apart with 29 ranks between them, every
    weekday its own group holding rows: the census needs both pin days
    and one day of each of the six other weekdays -- 8. With 12 days in
    the tails, a column of 20 days leaves the body 8, the need, and is
    withheld (at the need the day pass must find the fewest days the
    census allows, which it does not always); 21 is published. Two
    ranks between the pins need at most two days besides them. A gap
    whose two pins stand on one day is no gap. Only groups that hold
    rows are counted, the gap's own end groups are not (a pin day stands
    for them), a gap three days wide holds only the weekdays strictly
    inside it, a merged group is one group, and a day two pins stand on
    is counted once. Where the census needs no day past the pin days the
    rule is silent whatever the room. Red when the pin days are not
    counted or are counted twice, a gap's end groups or an empty group
    are counted, the ranks between the pins do not cap a gap, a one-day
    gap counts, a gap is scanned a day deep, the rule withholds below
    the need only, leaves the tails out of the room, or speaks where the
    census needs nothing past the pins.
    """
    every = _seven((40, 40, 40, 40, 40, 40, 40))
    fortnight = ((10, _MONDAY), (40, _MONDAY + 14))
    assert calendar_rules.count_room_short(every, fortnight, 20, 12)
    assert not calendar_rules.count_room_short(every, fortnight, 21, 12)
    two_ranks = ((10, _MONDAY), (13, _MONDAY + 14))
    assert calendar_rules.count_room_short(every, two_ranks, 4, 0)
    assert not calendar_rules.count_room_short(every, two_ranks, 5, 0)
    heaped = ((10, _MONDAY), (20, _MONDAY))
    assert not calendar_rules.count_room_short(every, heaped, 0, 0)
    thursdays = _seven((40, 0, 0, 40, 0, 0, 0))
    assert calendar_rules.count_room_short(thursdays, fortnight, 3, 0)
    assert not calendar_rules.count_room_short(thursdays, fortnight, 4, 0)
    shared = ((0, _MONDAY), (10, _MONDAY + 7), (20, _MONDAY + 14))
    assert calendar_rules.count_room_short(every, shared, 15, 0)
    assert not calendar_rules.count_room_short(every, shared, 16, 0)
    twice = ((0, _MONDAY), (5, _MONDAY), (20, _MONDAY + 14))
    assert calendar_rules.count_room_short(every, twice, 8, 0)
    assert not calendar_rules.count_room_short(every, twice, 9, 0)
    narrow = ((0, _MONDAY), (10, _MONDAY + 2))
    assert calendar_rules.count_room_short(every, narrow, 3, 0)
    assert not calendar_rules.count_room_short(every, narrow, 4, 0)
    merged = ((0, 4, 200), (5, 6, 80))
    assert calendar_rules.count_room_short(merged, fortnight, 3, 0)
    assert not calendar_rules.count_room_short(merged, fortnight, 4, 0)
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


def test_the_producer_hands_the_rule_the_block_s_pins_and_tails(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """What `taxonomy.weekday_decision` hands the rule, and only above the floor of 11 (plan P4-D388).

    `_weekly_schedule(0)` at the floor of 36: both tails publish their
    distances, so their most is the floor each, 36 and 36 though they
    hold 59 and 40 rows; the pins are the two boundaries, at ranks 59
    and 229, and the rungs published between them, p25, p50 and p75 at
    ranks 67, 134 and 201. At the floor of 20 its low tail lists two
    values and its high tail's 23 rows give 20, and the pins are the
    boundaries at 21 and 246 with p10 to p95 between. The column's
    different days are its own 35. At the floor of 11 the rule is not
    asked at all (`calendar_rules.COUNT_ROOM_ABOVE_FLOOR`). Red when the
    rungs are not handed over, the column's rows stand for its days, the
    settings floor is not read, a listed tail is handed over as one
    publishing its distances, or the rule is asked at the floor of 11.
    """
    seen: "list[tuple[object, ...]]" = []
    asked = calendar_rules.count_room_short

    def recorded(groups: object, pins: "tuple[tuple[int, int], ...]", days: int, tails: int) -> bool:
        seen.append((pins, days, tails))
        return asked(groups, pins, days, tails)  # type: ignore[arg-type]

    monkeypatch.setattr(calendar_rules, "count_room_short", recorded)
    cells = _weekly_schedule(0)
    ordered = sorted(_day(cell) for cell in cells)
    for floor, tails, ranks in ((36, 72, [59, 67, 134, 201, 229]), (20, 22, [21, 26, 67, 134, 201, 242, 246])):
        seen.clear()
        block = _described(tmp_path, f"floor{floor}", cells, floor).block("visit")
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
    seen.clear()
    assert _described(tmp_path, "floor11", cells, 11).block("visit")["weekday_census"]
    assert seen == [], seen


def test_at_the_floor_of_11_the_rule_is_not_asked_and_a_small_column_keeps_its_census(tmp_path: pathlib.Path) -> None:
    """The rule's scope (plan P4-D388): asked above the floor of 11, the floor the few-dates rule was measured at.

    `_hunt(215)`, 95 visits over 30 days (D0's hunt batteries), at the
    floor of 11 publishes Monday to Friday against the weekend and its
    twins meet it at seeds 0 to 4. Asked here the rule would withhold it:
    both tails publish their distances, 15 and 11 rows, so their most is
    11 and 11 and leaves the body 8 of its 30 days, where its twins' tails
    held 13 or 14 and left 16 or 17; the census needs 8. At the floor of
    11 the 26 batteries measured hold 46 such censuses, every twin of
    which met them, and no published census whose twin went long. Red
    when the rule is asked at the floor of 11 or below.
    """
    cells = _hunt(215)
    described = _described(tmp_path, "hunt215", cells, 11)
    block = described.block("visit")
    groups = tuple((group["first"], group["last"], group["count"]) for group in block["weekday_census"])
    assert groups == ((0, 4, 56), (5, 6, 13)), groups
    assert _decided(block, cells, 11).reason == ""
    for seed in (0, 1, 2, 3, 4):
        twin = kpi_shapes.twin_text(described, seed)
        assert kpi_shapes.missed(kpi_shapes.measure(described, twin, f"hunt215-{seed}.csv")) == [], seed
    ordered = tuple(sorted(_day(cell) for cell in cells))
    rungs = block["date_percentiles"]
    percents = [(100 * num) // den for label, num, den in taxonomy.LADDER if rungs[label] is not None]
    pins = calendar_rules.body_pins(ordered, block["low_tail"]["rows"], block["high_tail"]["rows"], percents)
    most = calendar_rules.tails_most(ordered, block["low_tail"]["rows"], block["high_tail"]["rows"], (None, None), 11)
    assert (block["low_tail"]["rows"], block["high_tail"]["rows"], most) == (15, 11, 22)
    assert calendar_rules.count_room_short(groups, pins, len(set(ordered)), most)


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
def test_no_published_census_costs_its_twins_their_count_at_any_floor(
    tmp_path: pathlib.Path, builder: str, shape: int
) -> None:
    """Nine schedules at the floors of 11, 20, 36 and 50: each decision, and every published census met (plan P4-D388).

    Weekly schedules and clinics of the review's batteries. At 493f6f8
    the census of `schedule` 0 at the floor of 36, and of `schedule` 1
    and 92 and `clinic` 45 at 36 and 50, left their twins long: each is
    withheld now. `schedule` 5 at 36 and 50 and `schedule` 6 at 50 are
    withheld too though 493f6f8's twins met them -- the rule's price,
    their rebuilt tails counted at the most the floor allows where they
    held fewer days. `schedule` 4 and 17 and `clinic` 61, their tails
    listing their values, publish at every floor, and `schedule` 0 again
    at 50, where its census is Monday to Friday against the weekend and
    needs no day past the pin days. Every twin of a published census, at
    seeds 0 and 1, misses no check. Red when the rule stops withholding
    a long schedule, withholds a census whose tails list their values,
    or speaks where the census needs no day past the pins.
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

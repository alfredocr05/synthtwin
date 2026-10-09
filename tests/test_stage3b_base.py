"""THE BASE OF STAGE 3B (plan P4-D364): the reserved keys, the shared rules, the anchors.

What this file holds, clause by clause, and what turns each red:

* every block of dates, moments and clock times carries the keys stage 3b
  reserves, EMPTY -- red where a key leaves `DATETIME_KEYS` or
  `CLOCK_KEYS`, or a producer stub writes anything into it;
* the producer's own guard refuses a reserved key holding anything, by
  its place -- red where `profile`'s registry gives one of them an
  `_EACH` row; the loader's refusal is in `tests/test_contract_loader.py`'s
  battery, one R16 mutation per key;
* the stubs and seams hand back what they are handed -- red where one
  moves a rank, adds a check or changes a unit;
* the rules every census shares: the floor (`calendar_floor_ok`), the
  merge (`merged_groups`), the stand-out rule (`standing_out`) and the
  checker (`census_breach`), each on a case worked by hand here;
* the twin report's spread remark and the validator's census lines read
  exactly as they did before they were taken apart;
* one anchor per landing, in order, in every block landings append to --
  red where an anchor is lost or two are swapped.

HOW A LANDING EDITS THIS FILE (plan P4-D364). The reserved keys, the
guard's cases and the stubs are listed lane by lane, one entry to a line
under the lane's own `# -- 3b.X (P4-Dnnn)` line. A landing that fills a
key or a stub deletes its own entries, keeps its lane's line, and edits
no other line here, so two landings built side by side never touch one
line.

Every table is built here, seeded and neutral (plan D13).
"""

from __future__ import annotations

import copy
import datetime
import pathlib
import random
import re

import pytest

import kpi_shapes
from synthtwin import (
    calendar_clock,
    calendar_rules,
    contract,
    errors,
    generation,
    profile,
    taxonomy,
    validation,
)

REPO = pathlib.Path(__file__).resolve().parent.parent

# THE KEYS STAGE 3B RESERVES, lane by lane: the role whose blocks carry
# each, and the one value it holds until its landing fills it.
_RESERVED: "dict[tuple[str, str], object]" = {
    # -- 3b.D3 (P4-D368)
    ("datetime", "day_of_month_census"): [],
    # -- 3b.D4 (P4-D369)
    ("datetime", "heavy_dates"): [],
    # -- 3b.T2 (P4-D371)
    # -- 3b.T3 (P4-D372)
    ("datetime", "minute_census"): [],
    ("datetime", "second_census"): [],
    ("datetime", "minute_heaps"): [],
    ("datetime", "second_heaps"): [],
    # -- 3b.C1 (P4-D373)
    # -- 3b.C2 (P4-D374)
    ("time_of_day", "minute_census"): [],
    # -- 3b.R4 (P4-D384), reserved by the second cut (P4-D386)
    ("datetime", "count_form"): None,
}

# THE DECLARATIONS THE SECOND CUT RESERVES (plan P4-D386), lane by lane:
# each a key of the settings block, and the one value it holds until its
# landing fills it.
_RESERVED_SETTINGS: "dict[str, object]" = {
    # -- 3b.R2a (P4-D383)
    # Filled by its landing (question Q5): no longer reserved.
    # -- 3b.R2b (P4-D383)
    # No key of its own: the clock half reads layouts under 3b.T1's key.
    # -- 3b.R2c (P4-D383)
    "forced_date_columns": [],
    # -- 3b.R4 (P4-D384)
    "forced_date_counts": [],
}

# THE GUARD'S CASES, lane by lane: a column of `_three_kinds`, one of its
# lane's keys, and a value the key may not hold until its landing.
_GUARDED = (
    # -- 3b.D3 (P4-D368)
    ("seen_on", "day_of_month_census", [{"first": 1, "last": 31, "count": 300}]),
    # -- 3b.D4 (P4-D369)
    ("seen_on", "heavy_dates", [{"date": "2023-02-01", "count": 30}]),
    # -- 3b.T2 (P4-D371)
    # -- 3b.T3 (P4-D372)
    ("seen_at", "minute_census", [{"first": 0, "last": 59, "count": 300}]),
    ("seen_at", "minute_heaps", [{"value": 0, "count": 30}]),
    ("seen_at", "second_census", [{"first": 0, "last": 59, "count": 300}]),
    ("seen_at", "second_heaps", [{"value": 0, "count": 30}]),
    # -- 3b.C1 (P4-D373)
    # -- 3b.C2 (P4-D374)
    # No case of its own: a clock block's `minute_census` is published
    # under the path of 3b.T3's key, so the rows 3b.T3 adds admit it here
    # too, and until 3b.C2 fills it the loader's R16 case refuses it.
    # -- 3b.R4 (P4-D384), reserved by the second cut (P4-D386)
    ("seen_on", "count_form", {"places": 0, "trimmed": False, "contacts": None}),
)

# ...AND THE SETTINGS BLOCK'S, lane by lane: a reserved declaration and a
# value it may not hold until its landing.
_GUARDED_SETTINGS = (
    # -- 3b.R2a (P4-D383)
    # Filled by its landing (question Q5): its rows admit a declared window.
    # -- 3b.R2c (P4-D383)
    ("forced_date_columns", ["seen_on"]),
    # -- 3b.R4 (P4-D384)
    ("forced_date_counts", [["seen_on", "excel-1900"]]),
)

# THE STUBS AND SEAMS, lane by lane: how each is called (its kind, read by
# `test_the_stubs_and_seams_hand_back_what_they_are_handed`) and the stub.
_STUBS = (
    # -- 3b.D3 (P4-D368)
    ("spread", generation._day_of_month_spread),
    ("check", validation._day_of_month_checks),
    # -- 3b.D4 (P4-D369)
    ("layout", generation._heavy_layout),
    ("holes", generation._heavy_holes),
    ("pass", generation._heavy_sorted),
    ("spread", generation._heavy_spread),
    ("check", validation._heavy_checks),
    # -- 3b.T2 (P4-D371)
    # -- 3b.T3 (P4-D372)
    ("unit", generation._draw_unit),
    ("on the unit", generation._on_draw_unit),
    ("pass", generation._clock_fields_settled),
    ("spread", generation._clock_fields_spread),
    ("check", validation._clock_field_checks),
    # -- 3b.C1 (P4-D373)
    # -- 3b.C2 (P4-D374)
    ("clock layout", generation._clock_minutes_laid),
    ("clock check", validation._clock_minute_checks),
)

_FACTS = {"datetime": contract.DatetimeFacts, "time_of_day": contract.ClockFacts}
_KEYS = {"datetime": contract.DATETIME_KEYS, "time_of_day": contract.CLOCK_KEYS}


def _three_kinds(folder: pathlib.Path, floor: int = 11) -> kpi_shapes.Described:
    """Dates, moments and clock times, 400 rows, seeded."""
    draw = random.Random(364)
    rows = []
    for _row in range(400):
        day = datetime.date(2023, 1, 1) + datetime.timedelta(days=draw.randrange(300))
        clock = f"{draw.randrange(6, 22):02d}:{draw.randrange(60):02d}"
        rows += [[day.isoformat(), f"{day.isoformat()} {clock}:00", clock]]
    text = kpi_shapes.delimited_text(["seen_on", "seen_at", "slot"], rows)
    return kpi_shapes.describe(folder, f"three-{floor}", text, floor)


@pytest.fixture(scope="module")
def three_kinds(tmp_path_factory: pytest.TempPathFactory) -> kpi_shapes.Described:
    """`_three_kinds` at floor 11, described once for the tests that read it."""
    return _three_kinds(tmp_path_factory.mktemp("three"))


@pytest.mark.parametrize("floor", (1, 11))
def test_every_date_and_clock_block_carries_the_reserved_keys_empty(
    tmp_path: pathlib.Path, floor: int
) -> None:
    described = _three_kinds(tmp_path, floor)
    roles = {block["name"]: block["role"] for block in described.document["columns"]}
    assert roles == {"seen_on": "datetime", "seen_at": "datetime", "slot": "time_of_day"}
    for block in described.document["columns"]:
        for (role, key), empty in _RESERVED.items():
            if block["role"] == role:
                assert block[key] == empty, (block["name"], key)
    for column in described.loaded.columns:
        for (role, key), empty in _RESERVED.items():
            if isinstance(column.facts, _FACTS[role]):
                assert getattr(column.facts, key) == (None if empty is None else ()), (column.name, key)
    for role, key in _RESERVED:
        assert key in _KEYS[role], (role, key)
    # ...and the settings block carries the second cut's three, empty, and
    # reads them back empty.
    for key, empty in _RESERVED_SETTINGS.items():
        assert described.document["settings"][key] == empty, key
        assert getattr(described.loaded.settings, key) == (), key
        assert key in contract.SETTINGS_KEYS, key


@pytest.mark.parametrize(
    "column,key,value", _GUARDED, ids=[f"{column}-{key}" for column, key, _value in _GUARDED]
)
def test_the_producer_guard_refuses_a_reserved_key_holding_anything(
    three_kinds: kpi_shapes.Described, column: str, key: str, value: object
) -> None:
    document = copy.deepcopy(three_kinds.document)
    for block in document["columns"]:
        if block["name"] == column:
            block[key] = value
    # ...refused BY THE KEY'S OWN PLACE, so a refusal for any other reason
    # leaves this red -- and so does a row that admits the key's entries
    # and refuses only one field of this value.
    place = f"'columns[].{key}[]'" if isinstance(value, list) else f"'columns[].{key}'"
    with pytest.raises(errors.ProfileError, match=re.escape(place)):
        profile.check_publication(document)


@pytest.mark.parametrize(
    "key,value", _GUARDED_SETTINGS, ids=[key for key, _value in _GUARDED_SETTINGS]
)
def test_the_producer_guard_refuses_a_reserved_declaration_holding_anything(
    three_kinds: kpi_shapes.Described, key: str, value: object
) -> None:
    """Plan P4-D386: the settings block's reserved keys, refused by their place."""
    document = copy.deepcopy(three_kinds.document)
    document["settings"][key] = value
    with pytest.raises(errors.ProfileError, match=re.escape(f"'settings.{key}[]'")):
        profile.check_publication(document)


def test_the_stubs_and_seams_hand_back_what_they_are_handed(
    three_kinds: kpi_shapes.Described,
) -> None:
    dates, moments, clocks = (column for column in three_kinds.loaded.columns)
    assert isinstance(dates.facts, contract.DatetimeFacts)
    assert isinstance(moments.facts, contract.DatetimeFacts)
    assert isinstance(clocks.facts, contract.ClockFacts)
    facts = moments.facts
    parsed = moments.n_present - facts.n_unparsed
    layout = generation._date_layout(moments, facts, parsed, 11)
    ordinals = list(range(parsed))
    handed = (moments, facts, ordinals, parsed, [False] * parsed, [0] * parsed, [parsed] * parsed, layout, ())
    clock_layout = generation._clock_knots_laid(clocks, clocks.facts, 11)
    spread = generation._SPREAD_NOTHING_MET
    for kind, stub in _STUBS:
        if kind == "unit":
            assert stub(facts) == 1 and layout.draw_unit == 1, stub
        elif kind == "on the unit":
            assert stub(17, 1, 0, 99) == 17, stub
        elif kind == "layout":
            assert stub(moments, facts, layout) is layout, stub
        elif kind == "holes":
            assert stub(facts) == frozenset(), stub
        elif kind == "pass":
            assert stub(*handed) == (ordinals, []), stub
        elif kind == "spread":
            assert stub(facts, spread) is spread, stub
        elif kind == "check":
            assert stub(moments, facts, {}, 11, []) == [], stub
        elif kind == "clock layout":
            assert stub(clocks, clocks.facts, 11, clock_layout) is clock_layout, stub
        else:
            assert kind == "clock check", kind
            assert stub(clocks, clocks.facts, {}, [], 11) == [], stub


def test_the_shared_floor_rule() -> None:
    assert calendar_rules.calendar_floor_ok(0, 11)
    assert calendar_rules.calendar_floor_ok(11, 11)
    assert not calendar_rules.calendar_floor_ok(1, 11)
    assert not calendar_rules.calendar_floor_ok(10, 11)
    assert not calendar_rules.calendar_floor_ok(-1, 11)


def test_the_shared_merge_rule() -> None:
    merged = calendar_rules.merged_groups
    # Each short group joins its smaller non-zero neighbour, the nought
    # bins between them coming too.
    assert merged([12, 5, 0, 0, 40, 6, 0], [], 11) == ((0, 1, 17), (2, 3, 0), (4, 5, 46), (6, 6, 0))
    # The sure cells make a group short: 40 less 35 leaves 5, so it joins
    # the smaller of its two neighbours, the nought bin between them too.
    assert merged([12, 0, 40, 30], [0, 0, 35, 0], 11) == ((0, 2, 52), (3, 3, 30))
    # One non-zero group beside nought groups stands; one group over
    # every bin is no census.
    assert merged([0, 0, 30, 0, 0], [], 11) == ((0, 1, 0), (2, 2, 30), (3, 4, 0))
    assert merged([3, 0, 20, 0, 5], [], 11) == ()
    # On a cycle the last bin neighbours the first, and the one group
    # running past the last bin is listed last.
    assert merged([3, 0, 0, 30, 20, 0, 20, 0, 0, 5], [], 11, True) == (
        (1, 2, 0), (3, 3, 30), (4, 4, 20), (5, 5, 0), (6, 0, 28)
    )
    assert merged([0, 0, 30, 0, 0], [], 11, True) == ((2, 2, 30), (3, 1, 0))
    # The short group of least count joins first, the earlier on a tie:
    # the first 8 joins its neighbour past the last bin and the merge
    # stops at two groups, where the later 8 first would leave one group
    # over every bin, which is no census.
    assert merged([8, 0, 8], [], 11, True) == ((1, 1, 0), (2, 0, 16))
    # ...the least, not the largest: 5 joins 8 and the nought bin stands.
    assert merged([0, 8, 5], [], 11, True) == ((0, 0, 0), (1, 2, 13))
    # A short group with no non-zero neighbour leaves no census, never a
    # published group of 5.
    assert merged([5, 0, 0], [], 11) == ()
    # On a cycle the nought runs at both ends are one group, holding the
    # sure cells of both: 5 sure on either end bin make it short, so it
    # joins its neighbour -- of two 20s the one listed first, at bin 1.
    assert merged([0, 20, 20, 0], [0, 0, 0, 5], 11, True) == ((2, 2, 20), (3, 1, 20))
    assert merged([0, 20, 20, 0], [5, 0, 0, 0], 11, True) == ((2, 2, 20), (3, 1, 20))


def test_the_shared_merge_rule_breaks_a_tie_in_census_order() -> None:
    # Between two neighbours of one count, a short group joins the one
    # listed earlier in the census, never the one it reaches backwards
    # past the last bin (Codex's review of 3b.K): minute 1 joins minute
    # 2, then minute 3 joins them, and the empty run stands.
    merged = calendar_rules.merged_groups
    assert merged([0, 5, 5, 5] + [0] * 56, [], 11, True) == ((1, 3, 15), (4, 0, 0))
    assert merged([5, 11, 11], [], 11, True) == ((0, 1, 16), (2, 2, 11))
    assert merged([5, 11, 11], [], 11) == ((0, 1, 16), (2, 2, 11))
    # ...the group running past the last bin is listed last, so of 20 at
    # bin 3 and 20 at bin 6 it joins the one at bin 3.
    assert merged([3, 0, 0, 20, 20, 0, 20, 0, 0, 5], [], 11, True) == (
        (4, 4, 20), (5, 5, 0), (6, 6, 20), (7, 8, 0), (9, 3, 28)
    )
    # Where both neighbours are one group it joins it through the bins
    # before it, as before: the first 8 of [8, 0, 8] past the last bin.
    assert merged([8, 0, 8], [], 11, True) == ((1, 1, 0), (2, 0, 16))


def test_the_shared_stand_out_rule() -> None:
    # A date stands out at the line and three times the mean of the three
    # days either side; a day past either end holds nought.
    found = calendar_rules.standing_out(
        [0, 1, 0, 30, 1, 0, 0, 2, 15, 2], 11, 3, calendar_rules.CENTRE_MEAN
    )
    assert found == ((3, 30), (8, 15))
    assert calendar_rules.standing_out([11, 4, 4, 4], 11, 3, calendar_rules.CENTRE_MEAN) == ((0, 11),)
    assert calendar_rules.standing_out([12, 4, 4, 4], 12, 1, calendar_rules.CENTRE_MEAN) == ((0, 12),)
    assert calendar_rules.standing_out([10, 4, 4, 4], 11, 3, calendar_rules.CENTRE_MEAN) == ()
    # A clock value against the median of the five each side, which a
    # neighbouring heap does not lift.
    grid = [5] * 5 + [40] + [5] * 5
    assert calendar_rules.standing_out(grid, 11, 5, calendar_rules.CENTRE_MEDIAN) == ((5, 40),)
    heaps = [5, 60, 5, 5, 5, 40, 5, 5, 5, 60, 5]
    assert (5, 40) in calendar_rules.standing_out(heaps, 11, 5, calendar_rules.CENTRE_MEDIAN)
    assert (5, 40) not in calendar_rules.standing_out(heaps, 11, 5, calendar_rules.CENTRE_MEAN)
    # The median of an even count of neighbours is the mean of its middle
    # two, the lower of them included; the count stands at three times it
    # exactly, and not at twice or four times.
    median, mean = calendar_rules.CENTRE_MEDIAN, calendar_rules.CENTRE_MEAN
    stand = calendar_rules.standing_out
    assert stand([11, 6], 11, 1, median) == ((0, 11),)
    assert stand([30, 40], 11, 1, median) == ()
    assert stand([5, 12], 11, 1, median) == ((1, 12),)
    assert stand([18, 12], 11, 1, median) == ((0, 18),)
    # ...and the mean at three times exactly, over every one of the reach.
    assert stand([15, 30], 11, 3, mean) == ((0, 15), (1, 30))
    assert stand([15, 18], 11, 1, mean) == ()
    # ON A CYCLE the neighbours wrap: minute :00 at 16 among minutes of 10
    # stands on a line, where the minutes before it are none, and not on
    # the hour, where they are :55 to :59; and so does :59.
    assert stand([16] + [10] * 59, 11, 5, median) == ((0, 16),)
    assert stand([16] + [10] * 59, 11, 5, median, True) == ()
    assert stand([10] * 59 + [16], 11, 5, median) == ((59, 16),)
    assert stand([10] * 59 + [16], 11, 5, median, True) == ()
    # ...and the units read past either end are the ones round the cycle:
    # :55 to :59 before :00, never :01 to :05 again nor :00 itself.
    assert stand([16] + [0] * 54 + [20] * 5, 11, 5, median, True) == ()
    assert stand([16] + [0] * 59, 11, 5, median, True) == ((0, 16),)


def test_the_shared_census_checker() -> None:
    breach = calendar_rules.census_breach
    assert breach((), 24, 11, 0) is None
    assert breach(((0, 9, 40), (10, 23, 60)), 24, 11, 100) is None
    assert breach(((0, 9, 40), (11, 23, 60)), 24, 11, 100)[0] == "CA1"
    assert breach(((0, 9, 40), (10, 22, 60)), 24, 11, 100)[0] == "CA1"
    assert breach(((0, 9, 40), (10, 23, 5), ), 24, 11, 45)[0] == "CA2"
    assert breach(((0, 9, 40), (10, 23, 60)), 24, 11, 99)[0] == "CA3"
    sure = tuple([0] * 9 + [35] + [0] * 14)
    assert breach(((0, 9, 40), (10, 23, 60)), 24, 11, 100, sure)[0] == "CA5"
    assert breach(((0, 9, 40), (10, 23, 60)), 24, 11, 100, rules=("H1", "H2", "H3", "H5"), sure=sure)[0] == "H5"
    # On a cycle one group may run past the last bin, listed last; the
    # same grouping turned about is refused.
    assert breach(((1, 2, 0), (3, 5, 60), (6, 0, 28)), 10, 11, 88, cyclic=True) is None
    assert breach(((6, 0, 28), (1, 2, 0), (3, 5, 60)), 10, 11, 88, cyclic=True)[0] == "CA1"
    assert breach(((1, 2, 0), (3, 5, 60), (6, 0, 28)), 10, 11, 88)[0] == "CA1"
    # A census of the days of a month counts from 1.
    assert breach(((1, 15, 30), (16, 31, 40)), 31, 11, 70, low=1, unit="day") is None
    # The sure cells are read round a cycle, and from the first bin's own
    # number: 20 sure cells on bin 0 leave 8 of the group from bin 6 past
    # the last bin, and 25 on day 1 leave 5 of days 1 to 15.
    assert breach(((1, 2, 0), (3, 5, 60), (6, 0, 28)), 10, 11, 88, (20,) + (0,) * 9, True)[0] == "CA5"
    assert breach(((1, 15, 30), (16, 31, 40)), 31, 11, 70, (25,) + (0,) * 30, low=1, unit="day")[0] == "CA5"
    # A group ending before the first bin is refused by where it ends:
    # read as covering bins 6 to 9 it would pass the cover, so the total
    # of 99 would be the first rule it breaks.
    assert breach(((0, 5, 40), (6, -1, 60)), 10, 11, 99, cyclic=True)[0] == "CA1"


def test_the_spread_remark_reads_as_it_did() -> None:
    held, note = generation._spread_written(generation._SPREAD_NOTHING_MET)
    assert held == (
        "the published ladder is met rung for rung, and between the rungs "
        "the days are drawn independently"
    )
    assert note == (
        "Four things a real column of dates often has are not reproduced, "
        "because the description publishes nothing that carries them: which "
        "days of the week the values fall on, the time of day, days that "
        "hold far more values than their neighbours, and a column whose "
        "values sit on a few scheduled dates. Counts per weekday, per hour "
        "or per single day computed on this twin are not the real column's."
    )

    class Weekend:
        weekday_census = ((0, 0, 11), (1, 1, 11), (2, 2, 11), (3, 3, 11), (4, 4, 11), (5, 6, 11))

    held, note = generation._spread_written(
        generation._weekday_spread(Weekend(), generation._SPREAD_NOTHING_MET)  # type: ignore[arg-type]
    )
    assert held == (
        "the published ladder is met rung for rung, the published counts per "
        "day of the week are met over the values between the two tail "
        "boundaries, and between the rungs the days are otherwise drawn "
        "independently"
    )
    assert note == (
        "Three things a real column of dates often has are not reproduced, "
        "because the description publishes nothing that carries them: the "
        "time of day, days that hold far more values than their neighbours, "
        "and a column whose values sit on a few scheduled dates. Counts per "
        "hour or per single day computed on this twin are not the real "
        "column's. Saturday and Sunday are counted together here, so the "
        "twin's split between them can differ from the real one."
    )

    class Weekdays:
        weekday_census = ((0, 4, 55), (5, 6, 11))

    held, note = generation._spread_written(
        generation._weekday_spread(Weekdays(), generation._SPREAD_NOTHING_MET)  # type: ignore[arg-type]
    )
    assert note.endswith(
        "column's. Monday to Friday are counted together here, and Saturday "
        "and Sunday together, so the twin's split among the days of each can "
        "differ from the real one."
    )


def test_the_census_lines_print_as_the_weekday_check_did() -> None:
    groups = [("Monday", 40), ("Tuesday", 30)]
    assert validation._census_lines(groups, [40, 30], 11) == (
        "Monday 40, Tuesday 30", "Monday 40, Tuesday 30", []
    )
    # A count at the line is printed as it is: the line is not short.
    assert validation._census_lines([("Monday", 11), ("Tuesday", 30)], [11, 30], 11) == (
        "Monday 11, Tuesday 30", "Monday 11, Tuesday 30", []
    )
    asked, shown, lines = validation._census_lines(groups, [65, 5], 11)
    assert (asked, shown) == ("Monday 40, Tuesday 30", "Monday kept back, Tuesday fewer than 11")
    assert lines and lines[0].startswith("A group this file holds fewer than 11")
    asked, shown, lines = validation._census_lines([("Monday", 12)], [5], 11)
    assert shown == "Monday kept back"
    assert lines[0].startswith("Some group this file holds fewer than 11")


# THE APPEND BLOCKS, each with its nineteen anchors in the plan's order
# (plan P4-D364): the file, and the text the block's anchors follow. The
# first fifteen are numbered P4-D365 on; the second cut (plan P4-D386)
# adds the three halves of the layout reader, P4-D383, and the numbers
# that are dates, P4-D384, after them.
_LANES = (
    "3b-D1", "3b-D0", "3b-D2", "3b-D3", "3b-D4", "3b-T1", "3b-T2", "3b-T3",
    "3b-C1", "3b-C2", "3b-G1", "3b-G3", "3b-G2", "3b-7", "3b-J",
    "3b-R2a", "3b-R2b", "3b-R2c", "3b-R4",
)
_NUMBERS = tuple(365 + place for place in range(15)) + (383, 383, 383, 384)
_BLOCKS = (
    ("src/synthtwin/calendar_rules.py", 1),
    ("src/synthtwin/calendar_clock.py", 1),
    ("src/synthtwin/contract.py", 1),
    ("src/synthtwin/taxonomy.py", 4),
    ("src/synthtwin/profile.py", 3),
    ("tests/dispositions.py", 3),
    ("tests/test_p3v1f2_entry_table.py", 2),
    ("tests/test_contract_loader.py", 1),
    ("tests/test_version_reach.py", 1),
    ("tests/test_generation_reference.py", 1),
    ("tests/test_stage3b_gate.py", 1),
    ("docs/spec/profile-contract-v6.md", 7),
)


@pytest.mark.parametrize("path,blocks", _BLOCKS, ids=[path for path, _blocks in _BLOCKS])
def test_every_append_block_carries_one_anchor_per_landing(path: str, blocks: int) -> None:
    text = (REPO / path).read_text(encoding="utf-8")
    numbers = _NUMBERS
    assert len(numbers) == len(_LANES)
    for lane, number in zip(_LANES, numbers):
        assert text.count(f"anchor {lane} (P4-D{number})") == blocks, (path, lane)
    # ...and in order, block by block.
    at = -1
    for _block in range(blocks):
        for lane, number in zip(_LANES, numbers):
            found = text.index(f"anchor {lane} (P4-D{number})", at + 1)
            assert found > at, (path, lane)
            at = found


def test_the_new_module_is_shipped_and_names_the_clock_keys() -> None:
    workflow = (REPO / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "wheel required synthtwin/calendar_clock.py" in workflow
    assert "sdist required ROOT/src/synthtwin/calendar_clock.py" in workflow
    assert set(calendar_clock.DATETIME_CLOCK_LISTS) <= set(contract.DATETIME_KEYS)
    assert set(calendar_clock.CLOCK_LISTS) | {calendar_clock.CLOCK_STEP} <= set(contract.CLOCK_KEYS)
    assert {calendar_rules.DAY_OF_MONTH_CENSUS, calendar_rules.HEAVY_DATES} <= set(contract.DATETIME_KEYS)
    assert taxonomy._reserved_lists({"a": 1}, ("b",)) == ({"a": 1, "b": []}, [], [])

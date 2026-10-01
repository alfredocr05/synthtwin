"""THE BASE OF STAGE 3B (plan P4-D364): the reserved keys, the shared rules, the anchors.

What this file holds, clause by clause, and what turns each red:

* every block of dates, moments and clock times carries the eleven keys
  stage 3b reserves, EMPTY -- red where a key leaves `DATETIME_KEYS` or
  `CLOCK_KEYS`, or a producer stub writes anything into it;
* the producer's own guard refuses a reserved key holding anything -- red
  where `profile`'s registry gives one of them an `_EACH` row; the
  loader's refusal is in `tests/test_contract_loader.py`'s battery, one
  R16 mutation per key;
* the stubs and seams hand back what they are handed -- red where one
  moves a rank, adds a check or changes a unit;
* the rules every census shares: the floor (`calendar_floor_ok`), the
  merge (`merged_groups`), the stand-out rule (`standing_out`) and the
  checker (`census_breach`), each on a case worked by hand here;
* the twin report's spread remark and the validator's census lines read
  exactly as they did before they were taken apart;
* one anchor per landing, in order, in every block landings append to --
  red where an anchor is lost or two are swapped.

Every table is built here, seeded and neutral (plan D13).
"""

from __future__ import annotations

import datetime
import pathlib
import random

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

_DATE_KEYS = (
    "hour_census",
    "minute_census",
    "second_census",
    "minute_heaps",
    "second_heaps",
    "day_of_month_census",
    "heavy_dates",
)
_CLOCK_KEYS = ("clock_census", "clock_heaps", "clock_step", "clock_codes")


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


@pytest.mark.parametrize("floor", (1, 11))
def test_every_date_and_clock_block_carries_the_reserved_keys_empty(
    tmp_path: pathlib.Path, floor: int
) -> None:
    described = _three_kinds(tmp_path, floor)
    roles = {}
    for block in described.document["columns"]:
        roles[block["name"]] = block["role"]
        if block["role"] == "datetime":
            assert {key: block[key] for key in _DATE_KEYS} == {key: [] for key in _DATE_KEYS}
        if block["role"] == "time_of_day":
            assert [block[key] for key in _CLOCK_KEYS] == [[], [], None, []]
    assert roles == {"seen_on": "datetime", "seen_at": "datetime", "slot": "time_of_day"}
    for column in described.loaded.columns:
        facts = column.facts
        if isinstance(facts, contract.DatetimeFacts):
            assert all(getattr(facts, key) == () for key in _DATE_KEYS)
        if isinstance(facts, contract.ClockFacts):
            assert (facts.clock_census, facts.clock_heaps, facts.clock_step, facts.clock_codes) == (
                (), (), None, ()
            )
    assert set(_DATE_KEYS) <= set(contract.DATETIME_KEYS)
    assert set(_CLOCK_KEYS) <= set(contract.CLOCK_KEYS)


@pytest.mark.parametrize(
    "column,key,value",
    [
        ("seen_on", "heavy_dates", [{"date": "2023-02-01", "count": 30}]),
        ("seen_at", "hour_census", [{"first": 0, "last": 23, "count": 300}]),
        ("slot", "clock_step", 60),
        ("slot", "clock_census", [{"first": 0, "last": 143, "count": 300}]),
    ],
)
def test_the_producer_guard_refuses_a_reserved_key_holding_anything(
    tmp_path: pathlib.Path, column: str, key: str, value: object
) -> None:
    described = _three_kinds(tmp_path)
    document = described.document
    for block in document["columns"]:
        if block["name"] == column:
            block[key] = value
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


def test_the_stubs_and_seams_hand_back_what_they_are_handed(tmp_path: pathlib.Path) -> None:
    described = _three_kinds(tmp_path)
    dates, moments, clocks = (column for column in described.loaded.columns)
    assert isinstance(dates.facts, contract.DatetimeFacts)
    assert isinstance(moments.facts, contract.DatetimeFacts)
    assert isinstance(clocks.facts, contract.ClockFacts)
    facts = moments.facts
    parsed = moments.n_present - facts.n_unparsed
    layout = generation._date_layout(moments, facts, parsed, 11)
    assert layout.draw_unit == 1 and generation._draw_unit(facts) == 1
    assert generation._heavy_layout(moments, facts, layout) is layout
    assert generation._heavy_holes(facts) == frozenset()
    assert generation._on_draw_unit(17, 1, 0, 99) == 17
    ordinals = list(range(parsed))
    lows = [0] * parsed
    highs = [parsed] * parsed
    for settled in (
        generation._hour_settled,
        generation._clock_fields_settled,
        generation._heavy_sorted,
    ):
        assert settled(moments, facts, ordinals, parsed, [False] * parsed, lows, highs, layout, ()) == (
            ordinals,
            [],
        )
    clock_layout = generation._clock_knots_laid(clocks, clocks.facts, 11)
    assert generation._clock_census_laid(clocks, clocks.facts, 11, clock_layout) is clock_layout
    assert generation._clock_minutes_laid(clocks, clocks.facts, 11, clock_layout) is clock_layout
    spread = generation._SPREAD_NOTHING_MET
    for clause in (
        generation._hour_spread,
        generation._clock_fields_spread,
        generation._day_of_month_spread,
        generation._heavy_spread,
    ):
        assert clause(facts, spread) is spread
    for check in (
        validation._hour_checks,
        validation._clock_field_checks,
        validation._day_of_month_checks,
        validation._heavy_checks,
    ):
        assert check(moments, facts, {}, 11, []) == []
    assert validation._clock_census_checks(clocks, clocks.facts, {}, [], 11) == []


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
    assert merged([3, 0, 0, 20, 20, 0, 20, 0, 0, 5], [], 11, True) == (
        (1, 2, 0), (3, 3, 20), (4, 4, 20), (5, 5, 0), (6, 0, 28)
    )
    assert merged([0, 0, 30, 0, 0], [], 11, True) == ((2, 2, 30), (3, 1, 0))


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


def test_the_census_lines_print_as_the_weekday_check_did() -> None:
    groups = [("Monday", 40), ("Tuesday", 30)]
    assert validation._census_lines(groups, [40, 30], 11) == (
        "Monday 40, Tuesday 30", "Monday 40, Tuesday 30", []
    )
    asked, shown, lines = validation._census_lines(groups, [65, 5], 11)
    assert (asked, shown) == ("Monday 40, Tuesday 30", "Monday kept back, Tuesday fewer than 11")
    assert lines and lines[0].startswith("A group this file holds fewer than 11")
    asked, shown, lines = validation._census_lines([("Monday", 12)], [5], 11)
    assert shown == "Monday kept back"
    assert lines[0].startswith("Some group this file holds fewer than 11")


# THE APPEND BLOCKS, each with its fifteen anchors in the plan's order
# (plan P4-D364): the file, and the text the block's anchors follow.
_LANES = (
    "3b-D1", "3b-D0", "3b-D2", "3b-D3", "3b-D4", "3b-T1", "3b-T2", "3b-T3",
    "3b-C1", "3b-C2", "3b-G1", "3b-G3", "3b-G2", "3b-7", "3b-J",
)
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
    numbers = [365 + place for place in range(len(_LANES))]
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

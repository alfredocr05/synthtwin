"""A lone pool is asked of every value a reader can count, and of every open census's spellings (plan P4-D356).

THE DEFECTS (the critic's report on the review round of follow-up B, item
B2, and its second skeptic). Each is reproduced red at 410841a:

1. the rule asked of the mode and of each tail taken whole, so a value
   the finer rungs count -- 1234 on twenty of a hundred rows between p68
   at 479.88 and p88 at 1277.92 -- or one the rungs and a listed tail
   count -- -50 on nineteen rows -- pinned a pool of 32 marks, or of 30
   notations, to two counts of ten, and the strict loader took all three
   descriptions;
2. the open censuses passed no room, so ten `1.5` and ten `2.25` beside
   eighty whole numbers of two spellings published a pool of 20 widths:
   two widths of ten;
3. a band of marks whose comma warning said "fewer than 11" was silent;
4. withdrawing the room clause left every producer test green, and no
   test held the loader's day-clock half (D12).

Every column here is built by seeded neutral code at test time.
"""

import itertools
import random

import pytest

from synthtwin import contract, parsing
from tests.test_mixture_reader_bounds import (
    ITEM_TWO,
    LINE,
    _block,
    _document,
    _refusal,
)


def _rungs_column() -> "list[str]":
    """The critic's column: 1234 on twenty rows over two marks, shuffled with `Random(1)`."""
    cells = [str(10 + k) for k in range(12)] + ["50"] * 30
    cells += [str(100 + k) for k in range(26)]
    cells += ["1,234"] * 10 + ["1 234"] * 10
    value = 1600
    for mark in ("'", " ", " ", " "):
        for _ in range(3):
            cells += [f"{value // 1000}{mark}{value % 1000:03d}"]
            value += 1
    random.Random(1).shuffle(cells)
    return cells


_OTHER_MARKS = ("'", " ", " ", " ", ",")

# The second skeptic's two shapes: 1234 on twenty body rows over two marks
# beside twelve high values of one spelling each; and -50 on nineteen rows
# over two notations, ten `-50.00` and nine `(50.00)`, the last row of a
# listed low tail and the eighteen rows above it.
BODY_MARKS = (
    [str(value) for value in [5] * 30 + [7] * 20 + [9] * 18]
    + ["1 234"] * 10 + ["1’234"] * 10
    + ["%d%s%03d" % (3 + k // 3, _OTHER_MARKS[k % 5], 100 + k) for k in range(12)]
)
TAIL_NOTATIONS = (
    ["−100.00"] * 6 + ["90.00-"] * 5 + ["-50.00"] * 10 + ["(50.00)"] * 9
    + ["5.00"] * 40 + ["7.00"] * 30
)
# The second skeptic's open census: two decimal spellings beside two whole
# ones, and beside twenty whole values of four rows each.
FRACTIONS = ["1.5"] * 10 + ["2.25"] * 10 + ["7"] * 40 + ["8"] * 40
FRACTIONS_WIDE = ["1.5"] * 10 + ["2.25"] * 10 + [str(k) for k in range(3, 23) for _ in range(4)]
PADS = ["007"] * 10 + ["0007"] * 10 + ["123"] * 80
# Eleven offsets of ten rows, each one moment written alike.
OFFSETS = [
    "2020-01-%02dT00:00:00+%02d:00" % (1 + k, k) for k in range(11) for _ in range(10)
]
# Twenty moments of one clock over two marks beside eighty rows of one day:
# three spellings, so the clocks' two marks are all the column leaves.
CLOCKS = ["2023-06-01T10:00:00"] * 10 + ["2023-06-01 10:00:00"] * 10 + ["2023-06-02"] * 80


# ------------------------------------------- 1. every value a reader counts


def test_a_value_the_rungs_count_bounds_a_pool_of_marks() -> None:
    """The critic's column: 1234 on rows 68 to 87, two spellings, so two marks of ten.

    Derived from the block: p68 479.88, p69 to p87 1234 and p88 1277.92
    place 1234 on exactly twenty rows; 53 spellings over 52 values leave
    it two; the field widths put every four-figure cell in the pool of 32.
    So the pool may not stand, and it is counted under the comma, the
    commonest mark the comma warning lets every grouped cell wear. At
    410841a it published `{"(withheld)": 32}`.
    Mutation: `taxonomy._value_groups` answering only the mode's value
    turns it red.
    """
    block = _block(_rungs_column())
    assert block["thousands_marks"] == {",": 32}
    assert block["group_separator"] == ","


def test_a_body_value_beside_a_high_tail_bounds_a_pool_of_marks() -> None:
    """The second skeptic's body-marks shape: 1234 on twenty rows, two marks of ten."""
    block = _block(BODY_MARKS)
    assert block["n_distinct_folded"] == 17 and block["n_distinct_values"] == 16
    assert block["thousands_marks"] == {",": 32}


def test_a_value_a_listed_tail_and_the_rungs_count_bounds_a_pool_of_notations() -> None:
    """-50 on nineteen rows: the tail's last row and eighteen above it, two notations.

    Six spellings over five values leave -50 two, so its nineteen rows sit
    on two notations of ten and nine. At 410841a the tail was asked whole
    -- thirty rows on four spellings, as many as the room -- and set aside,
    and `{"(withheld)": 30}` was published.
    """
    block = _block(TAIL_NOTATIONS)
    assert block["negative_notations"] == {"minus": 30}


@pytest.mark.parametrize(
    "cells,key,pool,rule,thing",
    (
        (_rungs_column(), "thousands_marks", 32, "TM1", "grouped numbers"),
        (BODY_MARKS, "thousands_marks", 32, "TM1", "grouped numbers"),
        (TAIL_NOTATIONS, "negative_notations", 30, "NS2", "negative numbers"),
    ),
    ids=("rungs", "body-marks", "tail-notations"),
)
def test_the_loader_refuses_a_pool_a_counted_value_pins(cells, key, pool, rule, thing, tmp_path) -> None:
    """Each description as 410841a wrote it, pooled by hand: refused.

    The loader places a value on the rows the rungs and a listed tail give
    it (`contract._located_runs`) and bounds the rows a pool of marks
    leaves out by the rows the rungs put under a thousand.
    Mutation: `contract._located_runs` answering nothing turns all three red.
    """
    document = _document(cells)
    column = document["columns"][0]
    column[key] = {"(withheld)": pool}
    if key == "thousands_marks":
        column["group_separator"] = ""
    said = _refusal(document, tmp_path)
    assert rule in said and f"all {pool} {thing} are held back" in said


def test_a_listed_tail_s_distances_count_each_of_its_values() -> None:
    """Three values, twelve rows, two distances: six, five and one, as the second skeptic read them.

    Ten `-50` sit at the low tail's boundary beside six `-100` and five
    `-90`: the mean distance 500/12 and the root-mean-square one of
    23000/12 leave one count each. A pair no whole counts meet settles
    nothing. Mutation: `contract._tail_rows` answering None turns it red.
    """
    mean = 500 / 12
    root = (23000 / 12) ** 0.5
    side = contract.TailSide(12, 12, mean, root, (-100.0, -90.0, -50.0))
    assert contract._tail_rows(side, -50.0, True) == [6, 5, 1]
    two = contract.TailSide(12, 12, 0.625, (5.625 / 12) ** 0.5, (1.5, 2.25))
    assert contract._tail_rows(two, 2.25, True) == [10, 2]
    loose = contract.TailSide(12, 12, mean + 0.3, root, (-100.0, -90.0, -50.0))
    assert contract._tail_rows(loose, -50.0, True) is None


# ---------------------------------------------- two values share a convention


def _full(rows: int, names: int) -> "tuple[int, ...]":
    return (rows,) * names


@pytest.mark.parametrize(
    "population,capacities,room,groups,holds",
    (
        # Twenty values of two rows and one spelling each: kept apart they
        # could not sit on seven marks, and a pool no reader pins was
        # refused; sharing, 8 8 8 8 8 or 10 10 10 10 hold them.
        (40, [40] * 7, 7, ((2, 1, _full(2, 7)),) * 20, True),
        # 22 rows of one value on three forms and 3 of another on one:
        # kept apart the three sat alone and a three stood in every reading;
        # beside the first value's seven they need not.
        (25, [25] * 6, 4, ((22, 3, _full(22, 6)), (3, 1, _full(3, 6))), True),
        # Two values of ten on one spelling each cannot share a notation.
        (20, [20] * 4, 4, ((10, 1, _full(10, 4)), (10, 1, _full(10, 4))), False),
        # A value of one row that cannot wear a trailing minus is no free
        # cell: at a floor of three four negatives with no point sit on
        # three notations of two at most, 2 2 or 2 1 1, a two in each;
        # free, one would take the trailing minus a pointed cell allows.
        (4, [4, 4, 4, 1], 4, ((3, 3, (3, 3, 3, 0)), (1, 1, (1, 1, 1, 0))), False),
    ),
    ids=("twenty-pairs", "forms-beside", "two-tens", "one-row-no-point"),
)
def test_values_share_a_convention_in_a_reading(population, capacities, room, groups, holds) -> None:
    """Each row worked by hand from the rule, two values free to share a convention.

    Mutations: `_placements` giving a loaded convention nothing more turns
    the first two red; a value of one row always set aside, the last.
    """
    floor = 3 if population == 4 else LINE
    assert parsing.mixture_pool_holds(population, floor, capacities, room, groups) is holds


def test_a_walk_that_stops_short_is_banded_by_the_producer_and_admitted_by_the_loader() -> None:
    """Twenty values of ten rows on two spellings at a floor of 31: the walk stops short.

    Where `parsing.POOL_SEARCH_STEPS` runs out, the answer is the
    caller's: the producer, asking with False, counts the census under
    one convention, and the loader, asking with True, refuses nothing it
    has not shown. Fifteen values of four rows on two spellings at eleven
    settle, and stand, whichever is asked.
    Mutation: `_pool_readings` answering False where it stops short turns
    the loader's half red.
    """
    heavy = ((10, 2, _full(10, 7)),) * 20
    assert parsing.mixture_pool_holds(200, 31, [200] * 7, 7, heavy, False) is False
    assert parsing.mixture_pool_holds(200, 31, [200] * 7, 7, heavy, True) is True
    light = ((4, 2, _full(4, 7)),) * 15
    assert parsing.mixture_pool_holds(60, LINE, [60] * 7, 7, light, False) is True


def _packable(totals: "tuple[int, ...]", groups: "list[tuple[int, int, tuple[int, ...]]]") -> bool:
    """Whether the groups fit these convention totals, each over no more conventions than its spellings."""
    if not groups:
        return True
    rows, spellings, reach = groups[0]
    names = len(totals)
    for amounts in itertools.product(*[range(min(totals[place], reach[place], rows) + 1) for place in range(names)]):
        if sum(amounts) != rows or sum(1 for amount in amounts if amount) > spellings:
            continue
        left = tuple(totals[place] - amounts[place] for place in range(names))
        if _packable(left, groups[1:]):
            return True
    return False


def _stated(population: int, floor: int, capacities: "list[int]", room: int, groups: "list[tuple[int, int, tuple[int, ...]]]") -> bool:
    """`mixture_pool_holds` as its docstring states it, every reading listed."""
    line = parsing.census_floor(floor)
    if population < line:
        return True
    held = [min(line - 1, max(0, capacity)) for capacity in capacities]
    seen = min(room, len(held))
    readings = [
        totals
        for totals in itertools.product(*[range(most + 1) for most in held])
        if sum(totals) == population
        and sum(1 for total in totals if total) <= seen
        and _packable(totals, [(rows, min(spellings, seen), reach) for rows, spellings, reach in groups])
    ]
    for place in range(len(held)):
        if held[place] >= 1 and not any(totals[place] == 0 for totals in readings):
            return False
    for count in range(1, line):
        if not any(all(total != count for total in totals) for totals in readings):
            return False
    return True


def test_the_pool_rule_is_its_statement_on_small_blocks() -> None:
    """Six hundred seeded small blocks: the walk answers what listing every reading answers.

    Values may share a convention, one of one row or partial reach is
    kept, and the walk never stops short on blocks this small.
    """
    draw = random.Random("the pool rule, stated")
    for _ in range(600):
        floor = draw.choice((2, 3, 4, 5, 6))
        line = parsing.census_floor(floor)
        names = draw.choice((2, 3, 4))
        capacities = [draw.randint(0, 3 * line) if draw.random() < 0.3 else 99 for _ in range(names)]
        most = sum(min(line - 1, capacity) for capacity in capacities) + 1
        population = draw.randint(line, max(line, min(most, 3 * line)))
        room = draw.randint(1, names + 1)
        groups: "list[tuple[int, int, tuple[int, ...]]]" = []
        left = population
        for _ in range(draw.randint(0, 3)):
            if left < 1:
                break
            rows = draw.randint(1, min(left, 2 * line))
            left -= rows
            reach = tuple(rows if draw.random() < 0.8 else draw.randint(0, rows) for _ in range(names))
            groups += [(rows, draw.randint(1, names), reach)]
        stated = _stated(population, floor, capacities, room, groups)
        walked = parsing.mixture_pool_holds(population, floor, capacities, room, tuple(groups))
        assert walked is stated, (population, floor, capacities, room, groups)


# ----------------------------------------------- 2. the open censuses' room


@pytest.mark.parametrize(
    "cells,key,census",
    (
        (FRACTIONS, "fraction_widths", {"2": 20}),
        (FRACTIONS_WIDE, "fraction_widths", {"2": 20}),
        (PADS, "pad_widths", {"3": 20}),
        (OFFSETS, "utc_offsets", {"+00:00": 110}),
    ),
    ids=("fractions", "fractions-wide", "pads", "offsets"),
)
def test_an_open_census_its_spellings_pin_is_counted_at_one_name(cells, key, census) -> None:
    """Two decimal spellings, two padded ones, eleven moments: no pool.

    Ten `1.5` and ten `2.25` beside `mode_count` 40 and four spellings:
    the whole numbers hold two, the decimals two widths of ten. Counted
    at the commonest width every decimal can be written at, `2` -- `1.5`
    is written `1.50`, and no figure of a value is cut. Two padded widths
    over two spellings are counted at `3`; eleven offsets of one spelling
    each at the first in sorted order. At 410841a all four pooled.
    Mutation: `taxonomy._width_band` answering `{}` turns the first three
    red; `_offset_counts` asking no room, the fourth.
    """
    assert _block(cells)[key] == census


@pytest.mark.parametrize(
    "cells,key,pool,rule",
    (
        (FRACTIONS, "fraction_widths", 20, "P6"),
        (PADS, "pad_widths", 20, "P6b"),
        (OFFSETS, "utc_offsets", 110, "D3"),
    ),
    ids=("fractions", "pads", "offsets"),
)
def test_the_loader_refuses_an_open_pool_its_spellings_pin(cells, key, pool, rule, tmp_path) -> None:
    """The same censuses pooled by hand: refused.

    The room is the column's spellings less those the cells outside the
    pool certainly hold (`contract._spellings_outside`): eighty whole
    numbers under a mode of forty hold two.
    Mutation: `_spellings_outside` answering nought turns the first red.
    """
    document = _document(cells)
    column = document["columns"][0]
    column[key] = {"(withheld)": pool}
    if key == "pad_widths":
        column["field_widths"] = {"3": 100}
    said = _refusal(document, tmp_path)
    assert rule in said and f"all {pool}" in said


# A sibling, the band of forms: the table with every counted cell written
# in the band's one form. Four `7`, three `+8` and three `0.25` or `9e0` at
# a floor of five hold three spellings, so three forms of 4, 3 and 3.
BAND_WEARS = ["7"] * 4 + ["+8"] * 3 + ["0.25"] * 3 + [""] * 90
BAND_PLAIN = ["7"] * 4 + ["+8"] * 3 + ["9e0"] * 3 + [""] * 90


def test_a_band_of_forms_takes_a_form_every_value_can_wear() -> None:
    """`0.25` cannot be written plain, so the band is the decimals, and their widths follow.

    At 410841a the band was the form the cells wrote most, `{"plain": 10}`,
    beside a value no plain cell holds: a table nobody reading `0.25` off
    the block believes, so the band told it had spoken.
    Mutation: `taxonomy._wearable_band` answering "" turns it red.
    """
    block = _block(BAND_WEARS, 5)
    assert block["numeric_styles"] == {"decimal": 10}
    assert block["fraction_widths"] == {"2": 10}


def test_a_band_of_forms_counts_its_widths_as_every_cell_written_in_it() -> None:
    """A plain band over `7`, `+8` and `9e0`: every cell one figure wide, `{"1": 10}`.

    At 410841a the four plain cells' width stood under the line and the six
    it took in were counted at no width, so the fields pooled beside
    `{"plain": 10}` -- where the table writing all ten plain names one width.
    Mutation: `taxonomy._width_censuses` never reading a band turns it red.
    """
    block = _block(BAND_PLAIN, 5)
    assert block["numeric_styles"] == {"plain": 10}
    assert block["field_widths"] == {"1": 10}


# ------------------------------------ 3. a band under the comma, the warning


def test_a_band_under_the_comma_keeps_the_warning_and_drops_its_number() -> None:
    """Ten `1,234` and ten `1 234`: counted under the comma, the warning says "some".

    The orchestrator's decision (i), P4-D347 applied: the warning's
    "fewer than 11" told a reader a comma census of twenty had spoken as a
    band. Wherever the census is the comma alone over no more cells than
    seven marks hold under the line, the warning keeps its sentence and
    says `said_some_but_not_all` in place of its count -- and a table of
    three spellings writing all twenty with a comma, one of them `+1,234`,
    says the same, character for character.
    Mutation: `taxonomy._comma_count_unsaid` answering False turns it red
    (the census goes silent again).
    """
    band = _block(ITEM_TWO)
    literal = _block(["1,234"] * 19 + ["+1,234"] + ["12"] * 80)
    assert band["thousands_marks"] == literal["thousands_marks"] == {",": 20}
    said = [remark for remark in band["remarks"] if "written with a comma" in remark]
    assert said and said == [remark for remark in literal["remarks"] if "written with a comma" in remark]
    assert said[0].startswith("some but not all of this column's values")


def test_a_band_that_would_write_the_warning_takes_another_mark() -> None:
    """Ten `1 234` and ten `1'234`: under the comma the warning would appear, so a space.

    No cell writes a comma, so the table writing all twenty with one would
    carry a warning this one does not; the band takes the commonest mark
    that keeps the warning as it is, the space before the apostrophe.
    """
    block = _block(["1 234"] * 10 + ["1'234"] * 10 + ["12"] * 80)
    assert block["thousands_marks"] == {" ": 20}
    assert not any("written with a comma" in remark for remark in block["remarks"])


# ------------------------------------------- 4. the room alone, and D12


def test_a_pool_its_room_alone_pins_is_counted_at_one_name() -> None:
    """Eleven offsets of ten rows, one spelling each: the room is all that pins it.

    The offsets are asked with no value group, so only their eleven
    spellings bound the pool: eleven offsets under eleven holding 110
    are ten each.
    Mutation: `parsing.mixture_pool_holds` reading the vocabulary's size
    for the room turns it red (and the day-clock marks' test beside it).
    """
    assert _block(OFFSETS)["utc_offsets"] == {"+00:00": 110}


def test_the_loader_refuses_a_pool_of_day_clock_marks_the_column_bounds(tmp_path) -> None:
    """Three spellings in the column, two of them the clocks': D12 refuses a hand pool of twenty.

    Measured by the second skeptic: beside a hundred dates of their own
    spellings the loader's room is the column's and bounds nothing, so a
    hand pool loads and the producer, reading the clocks' two spellings,
    is stricter than any reader there. Where the column writes one day
    beside them, the loader bounds it too.
    Mutation: the D12 branch withdrawn from `contract._closed_pools_bounded`
    turns it red.
    """
    document = _document(CLOCKS)
    column = document["columns"][0]
    assert column["datetime_separators"] == {"space": 20}
    column["datetime_separators"] = {"(withheld)": 20}
    said = _refusal(document, tmp_path)
    assert "D12" in said and "all 20" in said

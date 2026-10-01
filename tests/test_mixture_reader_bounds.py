"""The two mixture censuses bound what a reader of the WHOLE block can take (plan P4-D356).

THE DEFECT (the review of follow-up B). Plan P4-D352 let a census of marks
or notations that holds every convention under the line pool where the
vocabulary's size allowed it, and counted a larger pool under its commonest
convention (the band). Both read the vocabulary alone, and the rest of the
block bounds more than the vocabulary does:

1. ten `12.00-` beside nine each of `-12`, `(12)` and `-12` written with
   the minus sign, seventy-three `12` and one `12.50`, at a floor of
   eleven, published `{"trailing_minus": 37}` beside a forms map leaving
   too few cells with a point for 37 trailing minuses, so a reader knew
   the band had spoken, that no notation reached eleven, and so that the
   commonest held exactly ten;
2. ten `1,234`, ten `1 234` and eighty `12` published `{"(withheld)":
   20}` beside three different spellings, so the pool held two marks at
   most, both at exactly ten, and the comma warning named one of them;
3. a hand-written census naming five marks at sixteen beside a pool of
   twenty loaded, and its twin, writing all twenty with one mark, held;
4. seven `1,234.00` and seven `1 234.00` beside eighty-six bare, and
   five, five and four over three marks, came back with eight spellings
   where the source shows three or four suffice.

AND THE SECOND REVIEW OF THAT REPAIR:

5. a value whose rows the block publishes bounds the pool too: ten
   `-12.00` and ten `(12.00)` beside 55 cells of one spelling each
   published a pool of 30 beside `mode -12`, `mode_count 20`, 57
   spellings and 56 values, so -12 had two spellings at most and its
   twenty rows sat on two notations of ten; and ten `1 234` and ten
   `1'234` did the same to two marks;
6. the older closed censuses were still bounded by their vocabulary:
   ten `007`, ten `+7` and ten `7e0` published a pool of forms of 30
   beside three spellings, three forms of ten;
7. the first repair refused a pool that says only HOW MANY conventions
   were written -- never which, never a count -- and counted the
   review's own seven and seven under one mark for it.

Every column here is built by seeded neutral code at test time.
"""

import collections
import pathlib
import random

import pytest

from synthtwin import (
    contract,
    dialect,
    errors,
    parsing,
    profile,
    reading,
    taxonomy,
    validation,
)
from tests import fixtures
from tests.test_stage2_round_trip import _round_trip

LINE = 11
MARKS = parsing.GROUP_MARKS
SEEDS = ("0", "1", "2", "3", "4")


def _document(cells: "list[str]", floor: int = LINE) -> "dict[str, object]":
    """The producer's description of one measured column, loaded back once."""
    table = reading.Table(
        ["value"], [cells], len(cells), dialect.ENCODING_UTF8, False,
        reading.HEADER_FROM_FILE, reading._TAKEN_BY_CONVENTION, True,
    )
    document = profile.build_document(
        table, taxonomy.Settings(small_cell_floor=floor), [],
        forced_measurements=["value"],
    )
    contract._validated(document)
    return document


def _block(cells: "list[str]", floor: int = LINE) -> "dict[str, object]":
    column = _document(cells, floor)["columns"]
    assert isinstance(column, list)
    block = column[0]
    assert isinstance(block, dict)
    return block


def _refusal(document: "dict[str, object]", folder: pathlib.Path) -> str:
    """What the strict loader says of a description written in its exact form."""
    path = fixtures.write_profile(folder, "hand-profile.json", document)
    try:
        contract.load_profile(str(path))
    except errors.ProfileError as refused:
        return str(refused)
    return "accepted"


# ---------------------------------------------------------------- the shapes

ITEM_ONE = (
    ["12.00-"] * 10 + ["-12"] * 9 + ["(12)"] * 9 + ["\u221212"] * 9
    + ["12"] * 73 + ["12.50"]
)
ITEM_TWO = ["1,234"] * 10 + ["1 234"] * 10 + ["12"] * 80

# THE SECOND REVIEW'S SHAPES. -12 on twenty rows over two spellings, ten
# negatives of one spelling each, and 45 positives; 1234 on twenty rows over
# two marks, twenty other grouped values of one spelling each on the four
# other space-like marks, and forty three-figure numbers -- forty, so that
# the width census names its two widths at one count and has taken nothing
# in, and a reader knows every four-figure cell is grouped.
MODE_NOTATIONS = (
    ["-12.00"] * 10 + ["(12.00)"] * 10
    + ["\u2212%d.00" % k for k in range(1, 6)] + ["%d.00-" % k for k in range(6, 11)]
    + ["%d.00" % k for k in range(100, 145)]
)
_SPACES = ("'", "\u00a0", "\u202f", "\u2009")
MODE_MARKS = (
    ["1 234"] * 10 + ["1\u2019234"] * 10
    + ["2%s%03d" % (_SPACES[k % 4], k) for k in range(20)]
    + [str(100 + k) for k in range(40)]
)
FORMS = ["007"] * 10 + ["+7"] * 10 + ["7e0"] * 10
FORMS_APART = ["007"] * 4 + ["+8"] * 3 + ["9e0"] * 3
# A TAIL THAT LISTS ONE VALUE, at a floor of five: -9 on the seven lowest
# rows over two spellings, five other negatives, and 110 positives.
TAIL_NOTATIONS = (
    ["(9.00)"] * 4 + ["-9.00"] * 3
    + ["\u22121.00", "\u22122.00", "\u22123.00", "4.00-", "5.00-"]
    + ["7.00"] * 20 + ["%d.00" % (10 + k % 10) for k in range(90)]
)


def _seven_marks_of_ten() -> "list[str]":
    """Seventy whole numbers, ten per mark, each a lone group; a hundred small."""
    draw = random.Random("seven marks of ten, lone groups")
    cells: "list[str]" = []
    for mark in MARKS:
        cells += [
            f"{draw.randint(10, 99)}{mark}{draw.randint(0, 999):03d}"
            for _ in range(10)
        ]
    cells += [str(draw.randint(1, 999)) for _ in range(100)]
    return cells


def _band_beside_whole() -> "list[str]":
    """Ten `x.yy-` beside nine each of `(x)`, `-x` and `-x` with the minus sign."""
    draw = random.Random(601)
    out = [f"{draw.randint(1, 999)}.{draw.randint(0, 99):02d}-" for _ in range(10)]
    out += [f"({draw.randint(1, 999)})" for _ in range(9)]
    out += [f"-{draw.randint(1, 999)}" for _ in range(9)]
    out += [f"\u2212{draw.randint(1, 999)}" for _ in range(9)]
    out += [
        f"{draw.randint(1, 999)}" if draw.random() < 0.5
        else f"{draw.randint(1, 999)}.{draw.randint(0, 99):02d}"
        for _ in range(130)
    ]
    draw.shuffle(out)
    return out


# ------------------------------------------------------- item 1, the band


def test_a_band_takes_no_notation_some_negative_cannot_wear() -> None:
    """The review's column: 37 negatives, a point on ten of them.

    Derived from the rule: no notation reaches eleven and 37 is more than
    three notations hold below it, so the census is counted under one
    notation. The commonest is the trailing minus (10), which only a
    figure with a point can wear, and 27 negatives carry none; of the
    three others, nine each, the first in the contract's order is the
    hyphen-minus. So `{"minus": 37}` and `negative_form` `minus`.
    At 2af1f03 it published `{"trailing_minus": 37}` beside the forms map
    `plain 100, decimal 11`, which no table writing 37 negatives with a
    point stands beside, and so fixed the trailing minuses at ten.
    Mutation: `_reader_bounds` answering every notation wearable turns
    it red.
    """
    block = _block(ITEM_ONE)
    assert block["numeric_styles"] == {"plain": 100, "decimal": 11}
    assert block["negative_notations"] == {"minus": 37}
    assert block["negative_form"] == "minus"


def test_a_band_counted_under_the_hyphen_minus_is_written_so(tmp_path) -> None:
    """The same band on a column of amounts, through the three commands.

    The shape the trailing-minus gate carried as `band-beside-whole` until
    this review: every negative the twin writes wears the hyphen-minus in
    front, the twin's own description counts all 37 there, and both files
    validate.
    """
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path, _band_beside_whole(), (), seed="0"
    )
    assert first["negative_notations"] == {"minus": 37}
    assert second["negative_notations"] == {"minus": 37}
    assert first["negative_form"] == second["negative_form"] == "minus"
    assert twin_exit == 0 and real_exit == 0
    assert sum(1 for cell in written if cell.endswith("-")) == 0


def test_a_band_keeps_a_trailing_minus_where_every_negative_has_a_point() -> None:
    """The control: ten `12.50-` beside nine each of the others, all pointed."""
    cells = (
        ["12.50-"] * 10 + ["-12.25"] * 9 + ["(12.75)"] * 9
        + ["\u221212.05"] * 9 + ["12"] * 73
    )
    assert _block(cells)["negative_notations"] == {"trailing_minus": 37}


def test_a_band_under_the_comma_drops_the_warning_s_number() -> None:
    """Seven marks of ten whole lone groups each, beside the comma warning.

    At 2af1f03 the band published `{",": 70}` while the comma warning said
    fewer than eleven cells wrote a comma that reads either way: seventy
    commas would have said seventy, so a reader knew the band had spoken
    and each mark held exactly ten. The census went silent at 178bde2; at
    the final fix of follow-up B the warning keeps its sentence and drops
    its number instead (P4-D347, the orchestrator's decision (i)), as the
    table writing all seventy with a comma does, and the band stands.
    Mutation: `taxonomy._comma_count_unsaid` answering False turns it red.
    """
    block = _block(_seven_marks_of_ten())
    assert block["thousands_marks"] == {",": 70}
    assert block["group_separator"] == ","
    said = [remark for remark in block["remarks"] if "written with a comma" in remark]
    assert len(said) == 1 and said[0].startswith("some but not all of")


# -------------------------------------------------- item 2, the lone pool


def test_a_pool_its_spellings_fix_is_not_published() -> None:
    """The review's column: twenty grouped cells of one value, two marks.

    Derived from the rule: the pooled cells hold two spellings, so a
    reader sees at most two marks, and twenty is more than one mark holds
    below eleven -- the pool may not stand. Counted under the comma, whose
    warning then says "some but not all" for its count; under the space
    the warning would go. At 2af1f03 it published `{"(withheld)": 20}`.
    Mutation: `taxonomy._value_groups` answering nothing and
    `parsing.mixture_pool_holds` reading the room as the vocabulary's
    size together turn it red.
    """
    block = _block(ITEM_TWO)
    assert block["n_distinct"] == 3
    assert block["thousands_marks"] == {",": 20}
    assert block["group_separator"] == ","


def test_a_pool_of_notations_its_spellings_fix_is_counted_under_one() -> None:
    """Ten `(12)` and ten `-12`: two spellings, so two notations at most.

    At 2af1f03 `{"(withheld)": 20}` beside three different spellings fixed
    both notations at ten. Twenty is more than one notation holds below
    eleven, so it is counted under one: brackets and the hyphen-minus
    both hold ten, and the first in the contract's order is `minus`.
    """
    block = _block(["(12)"] * 10 + ["-12"] * 10 + ["5"] * 100)
    assert block["negative_notations"] == {"minus": 20}
    assert block["negative_form"] == "minus"


def test_a_trailing_minus_on_few_points_bounds_the_pool_too() -> None:
    """Three `12.50-` beside twenty-two whole negatives, a pool of 25.

    Three notations of ten and a trailing minus of three hold 23 with the
    hyphen-minus absent, so a pool of 25 said the hyphen-minus was
    written. At 2af1f03 it published `{"(withheld)": 25}`; counted under
    the commonest notation every negative can wear it is `{"minus": 25}`.
    """
    draw = random.Random("few points")
    cells = (
        ["12.50-"] * 3 + ["-12"] * 9 + ["(12)"] * 9 + ["\u221212"] * 4
        + [str(draw.randint(1, 999)) for _ in range(100)]
    )
    assert _block(cells)["negative_notations"] == {"minus": 25}


def test_the_spelling_room_is_the_vocabulary_rule_on_a_full_vocabulary() -> None:
    """With every capacity at the line, a full room and no group it is the vocabulary's rule, and never looser.

    The rule `census_pools` asked of the vocabulary alone until the second
    review of follow-up B: a population under the line pools, and one of
    ``n`` names pools while ``n - 1`` of them hold it under the line.
    Where the line is more than the vocabulary -- four and up for the day
    and clock marks, seven and up for the forms, eight and up for the
    marks, so at the default floor of eleven for every census -- the two
    agree cell for cell; under it the rule that no count stands in every
    reading refuses more.
    """
    for floor in (2, 3, 5, 8, 11, 31):
        line = max(2, floor)
        for names in (3, 4, 6, 7):
            for population in range(0, 8 * line):
                vocabulary = population < line or population <= (names - 1) * (line - 1)
                pooled = parsing.census_pools(population, floor, names)
                assert pooled == parsing.mixture_pool_holds(
                    population, floor, [population] * names, 99
                )
                if line > names:
                    assert pooled == vocabulary
                else:
                    assert vocabulary or not pooled


def _one(rows: int, spellings: int, names: int, pointed: int = -1) -> "tuple[tuple[int, int, tuple[int, ...]], ...]":
    """One value the block counts: its rows, its spellings, and what each convention holds of it."""
    reach = (rows,) * names
    if pointed >= 0:
        reach = (rows,) * (names - 1) + (pointed,)
    return ((rows, spellings, reach),)


@pytest.mark.parametrize(
    "population,floor,capacities,room,groups,holds",
    (
        (20, 11, [20] * 7, 2, (), False),  # two marks at most: ten each
        (10, 11, [10] * 7, 2, (), True),  # under the line: always a pool
        (20, 11, [20] * 7, 3, (), True),  # three: 10 10, 10 9 1, 8 6 6 ...
        (30, 11, [30] * 4, 4, (), True),  # three notations of ten, or four
        (31, 11, [31] * 4, 4, (), False),  # past three notations of ten
        (25, 11, [25, 25, 25, 3], 4, (), False),  # 10 + 10 + 3 without a minus
        (23, 11, [23, 23, 23, 3], 4, (), True),  # exactly that
        (5, 2, [5] * 7, 5, (), False),  # at a line of two every pool is ones
        (12, 11, [12] * 7, 1, (), False),  # one spelling: one mark at twelve
        (3, 3, [3] * 4, 3, (), False),  # two and one, or three ones: a one in each
        (4, 3, [4] * 4, 4, (), True),  # two twos, a two and two ones, four ones
        (19, 11, [19] * 7, 3, (), True),  # three marks: 10 9, 10 8 1 ... no count in all
        (29, 11, [29] * 4, 3, (), False),  # three notations: ten, ten and nine in each
        # HOW MANY, NEVER WHICH AND NEVER A COUNT (finding 3): two marks
        # of fourteen, four to ten each, and any five of the seven absent.
        (14, 11, [14] * 7, 2, (), True),
        (18, 11, [18] * 7, 2, (), True),  # 10 8, 9 9: no count in both
        (19, 11, [19] * 7, 2, (), False),  # 10 9 only
        (27, 11, [27] * 7, 3, (), True),  # 10 10 7, 9 9 9
        (28, 11, [28] * 7, 3, (), False),  # 10 10 8, 10 9 9: a ten in each
        # A VALUE THE BLOCK COUNTS (finding 1): its rows on no more
        # conventions than its spellings.
        (30, 11, [30] * 4, 12, _one(20, 2, 4), False),  # -12's twenty: ten and ten
        (40, 11, [40] * 7, 22, _one(20, 2, 7), False),  # 1234's twenty: ten and ten
        (40, 11, [40] * 7, 22, _one(18, 2, 7), True),  # eighteen: 10 8 or 9 9
        (30, 11, [30] * 4, 12, _one(10, 1, 4), False),  # ten on one notation: that one at ten
        (30, 11, [30] * 4, 12, _one(9, 1, 4), True),  # nine: the notation at nine or ten
        (25, 11, [25] * 4, 6, _one(12, 2, 4, 0), True),  # twelve on two, no trailing
        # two values of ten, one spelling each: two notations at ten
        (20, 11, [20] * 4, 4, _one(10, 1, 4) + _one(10, 1, 4), False),
    ),
)
def test_the_pool_rule_on_hand_worked_rows(population, floor, capacities, room, groups, holds) -> None:
    """Each row worked from the rule: any convention may be absent and no count stands in every reading."""
    assert parsing.mixture_pool_holds(population, floor, capacities, room, groups) is holds


# ---------------------------------------------------------------- the loader


def test_the_loader_refuses_a_pool_its_spellings_fix(tmp_path) -> None:
    """Item 2's description as 2af1f03 wrote it: refused under TM1.

    The column publishes three different spellings, so its twenty grouped
    cells show two marks at most, and one mark holds ten below eleven.
    """
    document = _document(ITEM_TWO)
    column = document["columns"][0]
    column["thousands_marks"] = {"(withheld)": 20}
    column["group_separator"] = ""
    said = _refusal(document, tmp_path)
    assert "TM1" in said and "20 grouped numbers are held back beside 3" in said


def test_the_loader_refuses_a_pool_of_notations_its_spellings_fix(tmp_path) -> None:
    """Ten `(12)` and ten `-12` beside a hundred `5`, pooled by hand: NS2."""
    document = _document(["(12)"] * 10 + ["-12"] * 10 + ["5"] * 100)
    column = document["columns"][0]
    column["negative_notations"] = {"(withheld)": 20}
    said = _refusal(document, tmp_path)
    assert "NS2" in said and "20 negative numbers are held back beside 3" in said


def _grouped_hundred() -> "dict[str, object]":
    return _document([f"{1234.25 + step:,.2f}" for step in range(100)])


def test_the_loader_refuses_a_pool_beside_named_marks(tmp_path) -> None:
    """Item 3: five marks named at sixteen beside a pool of twenty.

    No producer writes it -- a mark under the line is counted into the
    commonest named one -- and it fixed the two unnamed marks at ten each.
    At 2af1f03 the strict loader took it. Mutation: the
    `_pool_stands_alone` call withdrawn from TM1 turns it red.
    """
    document = _grouped_hundred()
    column = document["columns"][0]
    column["group_separator"] = ""
    column["thousands_marks"] = {
        ",": 16, " ": 16, "'": 16, "\u2019": 16, "\u00a0": 16, "(withheld)": 20,
    }
    said = _refusal(document, tmp_path)
    assert "TM1" in said and "held back beside a named count" in said


def test_the_loader_refuses_a_pool_beside_a_named_notation(tmp_path) -> None:
    """The same on the notations: brackets named at twenty beside a pool of eleven."""
    cells = ["(12)"] * 20 + ["-13"] * 6 + ["\u221214"] * 5 + ["5"] * 100
    document = _document(cells)
    column = document["columns"][0]
    assert column["negative_notations"] == {"brackets": 31}
    column["negative_notations"] = {"brackets": 20, "(withheld)": 11}
    said = _refusal(document, tmp_path)
    assert "NS2" in said and "held back beside a named count" in said


def test_a_pool_beside_named_marks_is_an_obligation_too() -> None:
    """Item 3's twin, checked as the checker would if such a census reached it.

    The census says twenty cells wore marks it does not name, each on
    fewer than eleven. A file naming one of those marks at twenty has not
    written the pool; at 2af1f03 only the five named counts were compared
    and it held. One pooling fifteen beside the same five has not written
    it either. A file pooling the same twenty, beside the same five, holds.
    Mutation: the pooled count's comparison withdrawn turns the first two
    red.
    """
    census = {",": 16, " ": 16, "'": 16, "\u2019": 16, "\u00a0": 16, "(withheld)": 20}
    named = {",": 16, " ": 16, "'": 16, "\u2019": 16, "\u00a0": 16}
    one_mark = dict(named, **{"\u202f": 20})
    fewer = dict(named, **{"(withheld)": 15})
    pooled = dict(named, **{"(withheld)": 20})
    order = parsing.PUBLISHED_GROUP_MARKS
    verdicts = [
        validation._mixture_check("value", "thousands_marks", census, file, order, 100, LINE, 100).verdict
        for file in (one_mark, fewer, pooled)
    ]
    assert verdicts == [validation.MISSED, validation.MISSED, validation.HELD]


# ------------------------------------------------- item 4, the marks spent


def _three_marks_one_value() -> "list[str]":
    return (
        ["1,234.00"] * 5 + ["1 234.00"] * 5 + ["1'234.00"] * 4 + ["1234.00"] * 86
    )


@pytest.mark.parametrize("seed", SEEDS)
def test_a_lone_pool_is_spent_over_no_more_marks_than_the_spellings_allow(seed, tmp_path) -> None:
    """Five, five and four grouped cells of one value over three marks.

    Derived from the rule: the census pools fourteen beside four different
    spellings. Seven marks over one value write eight spellings, six seven,
    five six, four five and three four, so three marks are spent -- and
    three is also the fewest whose rooms, two of ten, hold fourteen, so the
    twin's own description pools it again. At 2af1f03 the twin wrote eight
    spellings at five seeds of five and both distinctness checks passed as
    authorized deviations. Mutation: `_pool_mark_count` answering seven
    turns every seed red.
    """
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path, _three_marks_one_value(), (), seed=seed
    )
    assert first["thousands_marks"] == {"(withheld)": 14}
    assert first["n_distinct"] == 4
    assert len(set(written)) == 4
    assert second["thousands_marks"] == {"(withheld)": 14}
    assert second["n_distinct"] == 4
    assert twin_exit == 0 and real_exit == 0


@pytest.mark.parametrize("seed", SEEDS)
def test_the_review_s_two_marks_pool_again_over_two_marks(seed, tmp_path) -> None:
    """Seven `1,234.00` and seven `1 234.00`: a pool of fourteen, spent over two marks.

    The review's own column for item 4. Two spellings let a reader see
    two marks at most, four to ten each, any five of the seven absent: it
    is told how many marks were written and never which or a count, so the
    pool stands (the second review, finding 3). Two marks is the fewest
    whose room lets fourteen stand, and over two the column holds the
    three published spellings, so G6.1 spends it over two and the twin
    holds three and pools fourteen again. The first repair counted it
    under the comma. Mutations: the room-less-one clause restored in
    `parsing.mixture_pool_holds`, or `_pool_mark_count`'s fewest read as
    the room less one, each turns it red.
    """
    cells = ["1,234.00"] * 7 + ["1 234.00"] * 7 + ["1234.00"] * 86
    first, second, written, twin_exit, real_exit = _round_trip(tmp_path, cells, (), seed=seed)
    assert first["thousands_marks"] == {"(withheld)": 14}
    assert first["n_distinct"] == 3
    assert len(set(written)) == 3
    assert second["thousands_marks"] == {"(withheld)": 14}
    assert twin_exit == 0 and real_exit == 0


# ------------------------------------ the second review: what else bounds a pool


def test_a_value_the_block_counts_bounds_a_pool_of_notations() -> None:
    """-12 on twenty rows over two spellings: counted under one notation.

    Derived from the rule (finding 1): the block publishes `mode -12`,
    `mode_count 20`, 57 spellings and 56 values, so -12 has two spellings
    at most, and its twenty rows sit on two notations under eleven -- ten
    each, in every reading. So the pool may not stand, and the thirty are
    counted under the commonest notation every negative can wear: the
    hyphen-minus and the brackets hold ten each, and the hyphen-minus is
    first. At 178bde2 it published `{"(withheld)": 30}`.
    Mutation: `taxonomy._published_groups` answering no group turns it red.
    """
    block = _block(MODE_NOTATIONS)
    assert (block["mode"], block["mode_count"]) == (-12.0, 20)
    assert (block["n_distinct_folded"], block["n_distinct_values"]) == (57, 56)
    assert block["negative_notations"] == {"minus": 30}
    assert block["negative_form"] == "minus"


def test_the_loader_refuses_a_pool_of_notations_the_mode_pins(tmp_path) -> None:
    """The same column's census written as 178bde2 wrote it: refused under NS2.

    The loader reads the mode's spellings as the column's less one per
    other value, 57 - 55 = 2, and its twenty rows as all in the pool, since
    every negative is. Mutation: `contract._mixture_pools_bounded` asking no
    group turns it red.
    """
    document = _document(MODE_NOTATIONS)
    document["columns"][0]["negative_notations"] = {"(withheld)": 30}
    said = _refusal(document, tmp_path)
    assert "NS2" in said and "30 negative numbers are held back beside 57" in said


def test_a_tail_that_lists_one_value_bounds_a_pool_of_notations() -> None:
    """At a floor of five the low tail lists -9 on its seven rows, two spellings.

    Derived from the rule: the tail publishes its rows and its one value,
    and the block 18 spellings of 17 values, so -9 has two spellings at
    most and its seven rows sit on two notations under five -- one of them
    at four in every reading. So the twelve negatives are counted under
    the commonest notation, the brackets at four. At 178bde2 they pooled.
    Mutation: `taxonomy._published_groups` reading no tail turns it red.
    """
    block = _block(TAIL_NOTATIONS, 5)
    assert block["tails"]["low"]["values"] == [-9.0]
    assert block["tails"]["low"]["rows"] == 7
    assert block["negative_notations"] == {"brackets": 12}


def test_the_loader_refuses_a_pool_of_notations_a_listed_tail_pins(tmp_path) -> None:
    """The same census pooled by hand: refused under NS2, the tail read as a group.

    Mutation: `contract._published_groups` reading no tail turns it red.
    """
    document = _document(TAIL_NOTATIONS, 5)
    column = document["columns"][0]
    column["negative_notations"] = {"(withheld)": 12}
    column["negative_form"] = "brackets"
    said = _refusal(document, tmp_path)
    assert "NS2" in said and "12 negative numbers are held back beside 18" in said


def test_a_value_the_block_counts_bounds_a_pool_of_marks() -> None:
    """1234 on twenty rows over two marks: counted under one mark.

    The same on the marks: 1234's twenty grouped rows sit on two marks of
    ten. The space and U+2019 hold ten each and the space is first among
    the marks a grouped cell can wear without moving the comma warning;
    no cell here reads a comma either way, so the space stands.
    """
    block = _block(MODE_MARKS)
    assert (block["mode"], block["mode_count"]) == (1234.0, 20)
    assert block["field_widths"] == {"3": 40, "4": 40}
    assert block["thousands_marks"] == {" ": 40}
    assert block["group_separator"] == " "


def test_the_loader_refuses_a_pool_of_marks_the_mode_pins(tmp_path) -> None:
    """Refused under TM1: the width census shows no four-figure cell left ungrouped.

    Forty cells three figures wide, never grouped and never 1234, and the
    forty others four wide beside a pool of forty: 1234's twenty rows are
    all in the pool, on no more marks than its two spellings.
    """
    document = _document(MODE_MARKS)
    column = document["columns"][0]
    column["thousands_marks"] = {"(withheld)": 40}
    column["group_separator"] = ""
    said = _refusal(document, tmp_path)
    assert "TM1" in said and "40 grouped numbers are held back beside 62" in said


@pytest.mark.parametrize(
    "cells,floor,census",
    (
        (FORMS, LINE, {"exponent_lower": 30}),
        (FORMS_APART, 5, {"leading_zero": 10}),
    ),
    ids=("one-value", "three-values-at-five"),
)
def test_a_pool_of_forms_its_spellings_fix_is_counted_under_one(cells, floor, census) -> None:
    """Ten `007`, ten `+7` and ten `7e0`: three spellings, so three forms of ten.

    Finding 2: the forms map pooled thirty beside three spellings at
    178bde2, and at most three forms under eleven each fix each at ten. So
    it is counted under the commonest form the cells wrote, the first in
    sorted order on the tie (`parsing.absorbed_census`). Over one value the
    mode, thirty rows on three spellings, pins it as well. At a floor of
    five four `007`, three `+8` and three `9e0` publish no mode and, ten
    numbers being too few for a tail, no tail, so only the room pins them:
    three forms under five holding ten read 4 4 2 or 4 3 3, a four in each.
    Mutation: `taxonomy._forms_bounds` answering the vocabulary's size as
    the room turns the second red.
    """
    block = _block(cells + [""] * 90, floor)
    assert block["n_distinct"] == 3
    assert block["numeric_styles"] == census


def test_the_loader_refuses_a_pool_of_forms_its_spellings_fix(tmp_path) -> None:
    """The same forms map pooled by hand: refused under P6."""
    document = _document(FORMS + [""] * 90)
    document["columns"][0]["numeric_styles"] = {"(withheld)": 30}
    said = _refusal(document, tmp_path)
    assert "P6" in said and "30 numbers' forms are held back beside 3" in said


def test_a_pool_of_day_clock_marks_its_spellings_fix_is_counted_under_one() -> None:
    """Twenty moments of one clock over two marks, beside a hundred dates.

    The clocks hold two spellings, so two marks at most, ten each: counted
    under the commonest mark the cells wrote, `space` before `upper_t` on
    the tie. At 178bde2 it published `{"(withheld)": 20}`.
    Mutation: `taxonomy._separator_counts` asking no room turns it red.
    """
    days = [f"2023-{1 + k // 28:02d}-{1 + k % 28:02d}" for k in range(100)]
    clocks = ["2023-06-01T10:00:00"] * 10 + ["2023-06-01 10:00:00"] * 10
    block = _block(days + clocks)
    assert block["datetime_separators"] == {"space": 20}


def test_three_day_clock_spellings_pool_twenty() -> None:
    """The control: seven, seven and six over three marks -- 10 10, 7 7 6 -- pool."""
    days = [f"2023-{1 + k // 28:02d}-{1 + k % 28:02d}" for k in range(100)]
    clocks = (
        ["2023-06-01T10:00:00"] * 7 + ["2023-06-01 10:00:00"] * 7
        + ["2023-06-01t10:00:00"] * 6
    )
    assert _block(days + clocks)["datetime_separators"] == {"(withheld)": 20}


# ----------------------------------------------------------------- the battery
#
# A READER OF THE WHOLE BLOCK, written here and not taken from the producer.
# Where a census is a lone pool, every world the block admits is enumerated:
# counts under the line, a trailing minus on no more cells than carry a
# point, no more conventions than the pooled cells' different spellings,
# and the comma written wherever the comma warning counts a cell. The pool
# may leave no count forced -- none a convention must take, none every
# world holds -- and no convention forced to be written. Where a census
# names ONE convention over cells that each held fewer than the line (a
# band), the table with every such cell written in that convention is
# described again, and it must publish the same block but for its count
# of different spellings and the remark that reads it -- which a table
# can make up with a spelling in a form the forms census counts into its
# commonest, `+1 234` or `012` -- otherwise a reader tells the band from
# a table that wrote one convention.

BATTERY = 240


def _hyphen_first(text: str) -> str:
    """A negative cell with its notation read back to the hyphen-minus in front."""
    body = text.strip()
    if body[:1] == "(" and body[-1:] == ")":
        return "-" + body[1:-1]
    if body[:1] == "\u2212":
        return "-" + body[1:]
    if body[-1:] == "-":
        return "-" + body[:-1]
    return body


def _grouped(value: int, mark: str) -> str:
    text = f"{value:,}"
    return text.replace(",", mark)


def _battery_shapes() -> "list[tuple[str, list[str], int, list[str], list[str]]]":
    """(kind, cells, floor, the counted cells, their conventions), seeded."""
    draw = random.Random("mixture reader battery")
    shapes: "list[tuple[str, list[str], int, list[str], list[str]]]" = []
    for _index in range(BATTERY):
        floor = draw.choice((3, 5, 11, 11, 11, 31))
        line = max(2, floor)
        values = [draw.randint(1000, 99999) for _ in range(draw.choice((1, 1, 2, 3, 40)))]
        counted: "list[str]" = []
        worn: "list[str]" = []
        if draw.random() < 0.5:
            kind = "marks"
            pointed = draw.random() < 0.5
            for mark in draw.sample(MARKS, draw.randint(1, 7)):
                for _cell in range(draw.randint(1, line + 2)):
                    text = _grouped(draw.choice(values), mark)
                    counted += [text + (".50" if pointed else "")]
                    worn += [mark]
        else:
            kind = "notations"
            share = draw.choice((0.0, 0.3, 1.0))
            small = [draw.randint(1, 99) for _ in range(len(values))]
            for form in draw.sample(parsing.NEGATIVE_FORMS, draw.randint(1, 4)):
                for _cell in range(draw.randint(1, line + 2)):
                    value = draw.choice(small)
                    point = form == parsing.NEGATIVE_TRAILING or draw.random() < share
                    text = f"-{value}.25" if point else f"-{value}"
                    counted += [parsing.with_negative_notation(text, form)]
                    worn += [form]
        rest = [str(draw.randint(1, 999)) for _ in range(120)]
        cells = counted + rest
        draw.shuffle(cells)
        shapes += [(kind, cells, floor, counted, worn)]
    return shapes


MODE_BATTERY = 60


def _mode_shapes() -> "list[tuple[str, list[str], int, list[str], list[str]]]":
    """(kind, cells, floor, the counted cells, their conventions), seeded, a heavy value first.

    The second review's shape, drawn: one value on the line to twice one
    less than it of rows, split over two conventions each under the line,
    other values one spelling and one row each on the conventions left,
    none of them reaching the line, and 120 small positives, so the value
    is the published mode.
    """
    draw = random.Random("mixture reader battery, a heavy value")
    shapes: "list[tuple[str, list[str], int, list[str], list[str]]]" = []
    for _index in range(MODE_BATTERY):
        floor = draw.choice((5, 11, 11, 11))
        line = max(2, floor)
        rows = draw.randint(line, 2 * (line - 1))
        first = draw.randint(rows - (line - 1), line - 1)
        kind = draw.choice(("marks", "notations"))
        names = list(MARKS) if kind == "marks" else list(parsing.NEGATIVE_FORMS)
        worn_by = draw.sample(names, len(names))
        held = {name: 0 for name in names}
        counted: "list[str]" = []
        worn: "list[str]" = []
        for place, share in ((0, first), (1, rows - first)):
            name = worn_by[place]
            held[name] = share
            text = _grouped(1234, name) if kind == "marks" else parsing.with_negative_notation("-12.00", name)
            counted += [text] * share
            worn += [name] * share
        for step in range(draw.randint(0, 3 * (line - 1))):
            open_names = [name for name in worn_by[2:] if held[name] < line - 1]
            if not open_names:
                break
            name = draw.choice(open_names)
            held[name] += 1
            text = (
                _grouped(2000 + 37 * step, name) if kind == "marks"
                else parsing.with_negative_notation(f"-{20 + step}.00", name)
            )
            counted += [text]
            worn += [name]
        rest = [str(draw.randint(100, 999)) for _ in range(120)]
        cells = counted + rest
        draw.shuffle(cells)
        shapes += [(kind, cells, floor, counted, worn)]
    return shapes


def _counted_of(cells: "list[str]", kind: str) -> "tuple[list[str], list[str]]":
    """The cells a census counts, and the convention each wears, read with the parser's own rules."""
    counted: "list[str]" = []
    worn: "list[str]" = []
    for text in cells:
        if kind == "marks":
            mark = parsing.thousands_mark(text)
            if mark:
                counted += [text]
                worn += [mark]
        elif parsing.number_core(text)[:1] == "-":
            counted += [text]
            worn += [parsing.negative_notation(text)]
    return counted, worn


def _partitions(total: int, parts: int, most: int) -> "list[tuple[int, ...]]":
    """Every way to write ``total`` as ``parts`` counts of 1 to ``most``, descending."""
    if parts == 0:
        return [()] if total == 0 else []
    found: "list[tuple[int, ...]]" = []
    for part in range(min(most, total), 0, -1):
        if part * parts < total:
            break
        found += [(part,) + rest for rest in _partitions(total - part, parts - 1, part)]
    return found


def _mode_fits(world: "tuple[int, ...]", mode: "tuple[int, int, int]") -> bool:
    """Whether the mode's counted rows sit on no more conventions of ``world`` than its spellings.

    ``mode`` is (its counted rows, its spellings among them, what the last
    convention holds of it -- a trailing minus only its cells with a
    point); the last place of a notations world is the trailing minus.
    """
    rows, spellings, last = mode
    if rows < 2:
        return True
    held = [min(count, last) if place == 3 and len(world) == 4 else count
            for place, count in enumerate(world)]
    return sum(sorted(held, reverse=True)[:spellings]) >= rows


def _lone_pool_leak(
    kind: str, pool: int, floor: int, counted: "list[str]", comma: bool, mode: "tuple[int, int, int]"
) -> str:
    """Why the worlds a lone pool admits pin a count, or ""."""
    line = max(2, floor)
    names = 7 if kind == "marks" else 4
    room = min(names, len({parsing.folded(text) for text in counted}))
    if kind == "notations":
        points = sum(1 for text in counted if "." in text)
        worlds = []
        for minus in range(line):
            for brackets in range(line):
                for sign in range(line):
                    trailing = pool - minus - brackets - sign
                    if not 0 <= trailing <= min(line - 1, points):
                        continue
                    world = (minus, brackets, sign, trailing)
                    if sum(1 for count in world if count) <= room and _mode_fits(world, mode):
                        worlds += [world]
        for place in range(4):
            seen = {world[place] for world in worlds}
            if 0 not in seen:
                return f"{parsing.NEGATIVE_FORMS[place]} is always written: {sorted(seen)}"
        shared = None
        for world in worlds:
            held = {count for count in world if count}
            shared = held if shared is None else shared & held
        return f"every world holds a count of {sorted(shared)}" if shared else ""
    partitions = []
    for parts in range(1, room + 1):
        partitions += [
            world for world in _partitions(pool, parts, line - 1) if _mode_fits(world, mode)
        ]
    shared = None
    for partition in partitions:
        shared = set(partition) if shared is None else shared & set(partition)
    if shared:
        return f"every world holds a count of {sorted(shared)}"
    if all(len(partition) >= names for partition in partitions):
        return "every mark is written in every world"
    if comma:
        seen = set()
        for partition in partitions:
            seen |= set(partition)
        if len(seen) < 2:
            return f"the comma the warning names holds {sorted(seen)}"
    return ""


def _band_leak(block, cells, floor, counted, worn, kind, name) -> str:
    """Where the table writing every counted cell in the band's convention publishes otherwise."""
    rewritten = []
    lookup = {}
    for text, convention in zip(counted, worn):
        if kind == "marks":
            lookup[text] = parsing.with_thousands_mark(text, name)
        else:
            lookup[text] = parsing.with_negative_notation(_hyphen_first(text), name)
    for text in cells:
        rewritten += [lookup.get(text, text)]
    other = _block(rewritten, floor)
    for key in sorted(set(block) | set(other)):
        if key in ("n_distinct", "n_distinct_folded"):
            continue
        mine, theirs = block.get(key), other.get(key)
        if key == "remarks":
            mine = [said for said in mine if not said.startswith(EVERY_DIFFERENT)]
            theirs = [said for said in theirs if not said.startswith(EVERY_DIFFERENT)]
        if mine != theirs:
            return f"{key}: {mine!r} against {theirs!r}"
    return ""


# The remark that reads the count of different spellings against the rows,
# in both its forms: "every value ..." and, where some cells share a
# value, "nearly every value ..." (NF32 and NF85, plan P4-D357 A). Both
# are said only where that count reaches the uniqueness line.
EVERY_DIFFERENT = (
    "every value in this column is different",
    "nearly every value in this column is different",
)


def _mode_of_counted(block: "dict[str, object]", counted: "list[str]") -> "tuple[int, int, int]":
    """The published mode's counted rows, their spellings and their pointed rows, or nothing."""
    mode = block["mode"]
    if not isinstance(mode, float):
        return (0, 0, 0)
    mine = [text for text in counted if float(parsing.number_core(text)) == mode]
    pointed = sum(1 for text in mine if "." in text)
    return (len(mine), len({parsing.folded(text) for text in mine}), pointed)


# THE BATTERY'S OWN HAND-DERIVED COVERAGE: columns whose census the rule
# gives by hand, so the reader is shown a pool and a band whatever the
# seeded ones do. Fourteen grouped cells of one value over two marks pool
# (finding 3); ten `(12)` and ten `-13` are two spellings of twenty
# negatives, ten each, and are counted under the hyphen-minus; and the
# second review's -12, twenty rows on two spellings, is counted there too.
COVERED = (
    ("marks", ["1,234.00"] * 7 + ["1 234.00"] * 7 + ["1234.00"] * 86, 11, "pool"),
    ("notations", ["(12)"] * 10 + ["-13"] * 10 + [str(k) for k in range(100, 200)], 11, "band"),
    ("notations", MODE_NOTATIONS, 11, "band"),
)


def test_no_mixture_census_lets_a_reader_of_the_whole_block_pin_a_count() -> None:
    """300 seeded columns and the hand-derived ones, each census read by the reader above.

    The reader enumerates the worlds the whole block admits, the published
    mode's rows on no more conventions than its own spellings among them.
    At 2af1f03 it pins counts on the review's shapes and their siblings in
    the battery, and at 178bde2 on the mode (the second review, finding
    1); it finds none now. Mutations, each run: `mixture_pool_holds`
    reading the room as the vocabulary's size, `_reader_bounds` answering
    every convention wearable, and `_published_groups` answering no group,
    each turn it red.
    """
    leaks: "list[str]" = []
    seen: "list[str]" = []
    shapes = [
        (kind, cells, floor, "")
        for kind, cells, floor, _counted, _worn in _battery_shapes() + _mode_shapes()
    ]
    shapes += [(kind, cells, floor, want) for kind, cells, floor, want in COVERED]
    for index, (kind, cells, floor, want) in enumerate(shapes):
        counted, worn = _counted_of(cells, kind)
        block = _block(cells, floor)
        census = block["thousands_marks" if kind == "marks" else "negative_notations"]
        line = max(2, floor)
        tally = collections.Counter(worn)
        read = ""
        if counted and census == {"(withheld)": len(counted)}:
            read = "pool"
            comma = kind == "marks" and any(
                "read either way" in remark or "either way" in remark
                for remark in block["remarks"]
            )
            mode = _mode_of_counted(block, counted)
            said = _lone_pool_leak(kind, len(counted), floor, counted, comma, mode)
            if said:
                leaks += [f"{index} {kind} pool {len(counted)} at {floor}: {said}"]
        elif counted and len(census) == 1 and max(tally.values()) < line:
            name = next(iter(census))
            if census[name] == len(counted) and name != "(unavailable)":
                read = "band"
                said = _band_leak(block, cells, floor, counted, worn, kind, name)
                if said:
                    leaks += [f"{index} {kind} band {name!r} at {floor}: {said}"]
        if want:
            seen += [f"{want} read as {read or 'neither'}"]
    assert leaks == []
    assert seen == [f"{want} read as {want}" for _kind, _cells, _floor, want in COVERED]

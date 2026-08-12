"""Review item P2-C3-F1: the grid carries the published counts, and no
ceiling stops the walk that answers them.

Round 3 found two independent defects behind one item, and this file
holds the repair to both. Every description here is built by the REAL
producer from a seeded neutral table (plan D13: no data-format file is
ever committed), so what is exercised is the path from table to twin.

1. THE GRID DID NOT REPRESENT THE SOURCE MARGINS. A column of numbers
   too large or too small to hold publishes three families of counts
   over the same cells -- what the notation classifies as (`n_numeric`,
   `n_not_numeric`, `n_out_of_range`, `n_contradictory`), whether the
   value is a whole number (`n_whole`, `n_fraction`,
   `n_whole_unknown`), and what sign it settles (`n_negative`,
   `n_positive`, `n_sign_unknown`) -- and publishes NO cross-tabulation
   of them. The earlier revision split `n_out_of_range` between whole
   numbers and fractions with a `min(...)` of its own and packed the
   six classes that split produced. On a genuine six-row source that
   split has no answer while another split of the very same published
   counts has one, so the twin lost six exact counts.

2. THE WORK CEILING WAS REACHED BY A PRODUCER DESCRIPTION. The walk
   stopped after 200,000 trips and handed the answer to the greedy
   packing, on the recorded belief that no producer description could
   reach that. A 2,710-row column of numbers too large to hold, with 38
   anonymous groups, class counts 592, 879 and 1,239 and sign counts
   1,578, 540 and 592, needs far more than 200,000 states of the walk
   the earlier revision ran. The ceiling is withdrawn; nothing counts
   trips now.
"""

import itertools
import pathlib
import random

import pytest

import fixtures
from synthtwin import (
    contract,
    generation,
    profile,
    reading,
    rendering,
    taxonomy,
)

EXACT_COUNTS = (
    "n_numeric",
    "n_not_numeric",
    "n_out_of_range",
    "n_contradictory",
    "n_whole",
    "n_fraction",
    "n_whole_unknown",
    "n_positive",
    "n_negative",
    "n_sign_unknown",
)

# The published counts the review's own case carries, so a reader can
# see that this file exercises that case and not a neighbour of it.
REVIEW_CLASSES = (592, 879, 1239, 0)
REVIEW_WHOLES = (1303, 815, 592)
REVIEW_SIGNS = (1578, 540, 592)

# One value four hundred figures wide is far outside the range this
# format holds, at both ends.
_HUGE = "9" * 320
_TINY_TAIL = "0" * 400


def _described(folder: pathlib.Path, values: "list[str]") -> contract.Profile:
    """Write a one-column table, describe it, load the description."""
    path = fixtures.write(
        folder, "table.csv", fixtures.single_column_table("value", values)
    )
    table = reading.read_table(str(path))
    document = profile.build_document(table, taxonomy.Settings(), [])
    target = fixtures.write_profile(folder, "table-profile.json", document)
    return contract.load_profile(str(target))


def _missed(twin: generation.Twin) -> "list[tuple[str, str, str]]":
    """Every exact cell count the twin failed to meet, as it names them."""
    return [
        (note.fact, note.published, note.achieved)
        for note in twin.deviations
        if note.fact in EXACT_COUNTS
    ]


def _facts(loaded: contract.Profile) -> contract.UnrepresentableFacts:
    """The wide-column facts of the one column, checked to be those."""
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.UnrepresentableFacts)
    return facts


def _without_the_fallback(call: "object") -> "object":
    """Run ``call`` with the greedy fallback made to fail loudly.

    A recount that happens to match after one family was packed after
    another proves nothing about the joint walk, so the fallback is not
    allowed to answer: `_allocation` is the only way into it for a wide
    column, and reaching it at all is the failure.
    """
    packed = generation._allocation

    def refused(*given):  # type: ignore[no-untyped-def]
        raise AssertionError(
            "the wide column fell back to packing one published family "
            "after another, so the joint walk did not answer it"
        )

    generation._allocation = refused  # type: ignore[assignment]
    try:
        return call()  # type: ignore[operator]
    finally:
        generation._allocation = packed  # type: ignore[assignment]


def _states(call: "object") -> "tuple[object, int]":
    """Run ``call`` and count the states the packing walk entered.

    `_cell_room` is asked once for every state the walk enters -- which
    cell is being filled, which sizes are unplaced, what every count of
    every margin still owes -- so counting its calls counts exactly the
    quantity the withdrawn ceiling claimed to bound.
    """
    room = generation._cell_room
    seen = [0]

    def counting(*given):  # type: ignore[no-untyped-def]
        seen[0] = seen[0] + 1
        return room(*given)

    generation._cell_room = counting  # type: ignore[assignment]
    try:
        answer = call()  # type: ignore[operator]
    finally:
        generation._cell_room = room  # type: ignore[assignment]
    return answer, seen[0]


# -- 1. the six-row source whose split had no answer -------------------


def _six_row_values() -> "list[str]":
    """The review's six-row source, as its four raw groups.

    Two cells written inside accounting parentheses with a sign inside
    them and one more of the same shape; two whole numbers the format
    holds; and one fraction far below the smallest value it holds. That
    publishes two numeric, one out-of-range and three contradictory
    cells; two whole, one fraction and three settling neither; and three
    negative cells against three settling no sign.
    """
    return [
        "(-5)", "(-5)", "-5", "-5", "(-6)", "-0." + _TINY_TAIL + "7",
    ]


def test_the_six_row_source_publishes_what_the_review_reported(
    tmp_path: pathlib.Path,
) -> None:
    """The vacuity floor: this really is the case the review built."""
    loaded = _described(tmp_path, _six_row_values())
    block = loaded.columns[0]
    facts = _facts(loaded)
    assert block.role == "numeric_unrepresentable"
    assert (block.n_numeric, block.n_out_of_range) == (2, 1)
    assert (block.n_contradictory, block.n_not_numeric) == (3, 0)
    assert (facts.n_whole, facts.n_fraction, facts.n_whole_unknown) == (
        2, 1, 3
    )
    assert (facts.n_negative, facts.n_positive, facts.n_sign_unknown) == (
        3, 0, 3
    )
    assert generation._groups_of(facts.n_distinct_by_occurrences) == (
        1, 1, 2, 2
    )


def test_the_six_row_source_meets_every_published_count(
    tmp_path: pathlib.Path,
) -> None:
    """Defect 1, end to end: six exact counts came out wrong before.

    The earlier revision wrote one numeric cell against two, four
    contradictory against three, no fraction against one, four settling
    neither whole status against three, two negative cells against three
    and four settling no sign against three -- and named all six. The
    counts are EXACT-OBSERVABLE and the real column's own values are a
    packing that meets them.

    The EXACT walk has to be the one that meets them: an implementation
    whose grid still asks a question the description never answered, and
    which then reaches the counts by packing one family after another,
    has the defect this item names even where the arithmetic comes out.
    """
    loaded = _described(tmp_path, _six_row_values())
    twin = _without_the_fallback(lambda: generation.generate(loaded, 0))
    assert _missed(twin) == []


def test_the_split_the_old_rule_invented_is_the_one_with_no_answer() -> None:
    """Defect 1, at the place the loss happened.

    `n_out_of_range` is published; how it divides between whole numbers
    and fractions is NOT. Sending the one out-of-range cell to "whole"
    -- which is what `min(n_out_of_range, n_whole)` did -- asks for
    class counts 3, 1, 0, 1, 1 and 0 from groups of 1, 1, 2 and 2, and
    no packing of whole groups meets those beside the sign counts.
    Sending it to "fraction" asks for 3, 0, 1, 2, 0 and 0, which has an
    answer. Both splits agree with every published count, so an
    implementation that picks one of them has invented the choice.
    """
    groups = (1, 1, 2, 2)
    signs = [3, 0, 3]
    permitted = [generation._spread_pairs(6, 3) for _each in groups]

    invented = generation._allotted_pairs(
        groups, [3, 1, 0, 1, 1, 0], signs, permitted
    )
    assert invented is None

    other = generation._allotted_pairs(
        groups, [3, 0, 1, 2, 0, 0], signs, permitted
    )
    assert other is not None


def test_the_grid_answers_from_the_published_counts_alone(
    tmp_path: pathlib.Path,
) -> None:
    """Defect 1, at the walk: all three published families are met.

    Recounted by hand from the walk's own answer, so a walk that
    returned an assignment nobody can recount fails here too, and with
    the greedy fallback made to fail, so only the joint walk can answer.
    """
    loaded = _described(tmp_path, _six_row_values())
    block = loaded.columns[0]
    facts = _facts(loaded)
    groups = generation._groups_of(facts.n_distinct_by_occurrences)

    kinds, negatives = _without_the_fallback(
        lambda: generation._unrepresentable_families(block, facts, groups)
    )

    notations = [0, 0, 0, 0]
    wholes = [0, 0, 0]
    signs = [0, 0, 0]
    for place in range(len(groups)):
        notations[generation._WIDE_CLASS_OF[kinds[place]]] += groups[place]
        wholes[generation._WIDE_WHOLE_OF[kinds[place]]] += groups[place]
        if generation._wide_settles(
            generation._WIDE_CLASS_OF[kinds[place]]
        ):
            signs[0 if negatives[place] else 1] += groups[place]
        else:
            signs[2] += groups[place]
    assert notations == [
        block.n_contradictory, block.n_out_of_range,
        block.n_numeric, block.n_not_numeric,
    ]
    assert wholes == [facts.n_whole, facts.n_fraction, facts.n_whole_unknown]
    assert signs == [
        facts.n_negative, facts.n_positive, facts.n_sign_unknown
    ]


def test_a_count_no_packing_can_reach_is_named_and_rendered(
    tmp_path: pathlib.Path,
) -> None:
    """And where the three families have no joint answer, it is SAID.

    A description asking for one whole number out of groups covering
    three, two and two rows cannot be met by whole groups at all. The
    twin then holds a different count, and the run names it under the
    contract's own key with the achieved value beside the published one,
    in the report a person reads. Silence there is the defect this file
    exists to stop.
    """
    values = ["1e999", "1e999", "1e999", "2e999", "2e999", "3e999", "3e999"]
    path = fixtures.write(
        tmp_path, "table.csv", fixtures.single_column_table("huge", values)
    )
    table = reading.read_table(str(path))
    document = profile.build_document(table, taxonomy.Settings(), [])
    for block in document["columns"]:
        if block["name"] == "huge":
            block["n_whole"] = 1
            block["n_fraction"] = 6
    target = fixtures.write_profile(tmp_path, "table-profile.json", document)
    loaded = contract.load_profile(str(target))

    twin = generation.generate(loaded, 0)
    named = {note.fact: note for note in twin.deviations}
    assert "n_whole" in named
    assert named["n_whole"].published == "1"
    assert named["n_whole"].note in rendering.report(loaded, twin)


# -- the floor under both: the three-margin walk is COMPLETE -----------


_WIDTH = 3
_KINDS = 6
_CELLS = _KINDS * _WIDTH


def _wide_totals(
    groups: "list[int]", placed: "list[int]"
) -> "tuple[list[int], list[int], list[int]]":
    """The three published families, recounted from an assignment."""
    notations = [0, 0, 0, 0]
    wholes = [0, 0, 0]
    signs = [0, 0, 0]
    for place in range(len(groups)):
        kind = placed[place] // _WIDTH
        notations[generation._WIDE_CLASS_OF[kind]] += groups[place]
        wholes[generation._WIDE_WHOLE_OF[kind]] += groups[place]
        signs[placed[place] - kind * _WIDTH] += groups[place]
    return notations, wholes, signs


def _wide_margins(
    notations: "list[int]", wholes: "list[int]", signs: "list[int]"
) -> "list[tuple[list[int], list[int]]]":
    """The grid a wide column packs over: three published families."""
    return [
        (
            notations,
            [generation._WIDE_CLASS_OF[cell // _WIDTH] for cell in range(_CELLS)],
        ),
        (
            wholes,
            [generation._WIDE_WHOLE_OF[cell // _WIDTH] for cell in range(_CELLS)],
        ),
        (
            signs,
            [cell - (cell // _WIDTH) * _WIDTH for cell in range(_CELLS)],
        ),
    ]


def test_the_three_margin_walk_agrees_with_exhaustion() -> None:
    """A completeness floor checked against EXHAUSTION, not a second walk.

    Six hundred small instances over the wide column's own cells and
    permissions: half built by drawing an assignment and publishing what
    it counts, so an answer is known to exist, and half with the three
    families drawn independently, so most have none. For every one of
    them the walk must answer exactly when some assignment of whole
    groups to permitted cells meets all three families, tried here one
    by one by hand. A walk checked against another walk of the same rule
    would prove nothing; checked against exhaustion it proves what it
    says.
    """
    permitted = [
        cell
        for cell in range(_CELLS)
        if (generation._spread_pairs(_KINDS, _WIDTH) >> cell) & 1
    ]
    rng = random.Random(20260812)
    answered = 0
    refused = 0
    for trial in range(600):
        groups = [rng.randint(1, 3) for _each in range(rng.randint(2, 4))]
        total = 0
        for size in groups:
            total = total + size
        if trial % 2 == 0:
            drawn = [
                permitted[rng.randrange(len(permitted))] for _each in groups
            ]
            notations, wholes, signs = _wide_totals(groups, drawn)
        else:
            asked = []
            for parts in (4, 3, 3):
                cuts = sorted(
                    rng.randint(0, total) for _each in range(parts - 1)
                )
                edges = [0] + cuts + [total]
                asked = asked + [[
                    edges[step + 1] - edges[step] for step in range(parts)
                ]]
            notations, wholes, signs = asked[0], asked[1], asked[2]

        walked = generation._allotted_over(
            groups,
            _wide_margins(notations, wholes, signs),
            [generation._spread_pairs(_KINDS, _WIDTH) for _each in groups],
        )
        by_hand = False
        for assignment in itertools.product(permitted, repeat=len(groups)):
            if _wide_totals(groups, list(assignment)) == (
                notations, wholes, signs
            ):
                by_hand = True
                break
        assert (walked is not None) == by_hand, (
            f"{groups} against {notations}, {wholes} and {signs}: the "
            f"walk said {walked is not None} where exhaustion says "
            f"{by_hand}"
        )
        if walked is None:
            refused = refused + 1
        else:
            answered = answered + 1
            assert _wide_totals(groups, walked) == (
                notations, wholes, signs
            )
    assert answered > 100, "too few of these instances had an answer at all"
    assert refused > 100, "no instance was refused, so refusal is untested"


# -- 2. the producer description that reached the work ceiling ---------


_CEILING_PLAN = (
    ("contradictory", 172), ("contradictory", 239), ("contradictory", 100),
    ("contradictory", 81), ("huge_negative", 700), ("huge_positive", 89),
    ("huge_positive", 24), ("huge_positive", 66), ("whole_negative", 62),
    ("whole_negative", 9), ("whole_negative", 72), ("whole_negative", 99),
    ("whole_negative", 38), ("whole_negative", 20), ("whole_positive", 4),
    ("whole_positive", 10), ("whole_positive", 17), ("whole_positive", 93),
    ("fraction_negative", 129), ("fraction_negative", 23),
    ("fraction_negative", 24), ("fraction_negative", 93),
    ("fraction_negative", 309), ("fraction_positive", 13),
    ("fraction_positive", 5), ("fraction_positive", 18),
    ("fraction_positive", 10), ("fraction_positive", 25),
    ("fraction_positive", 31), ("fraction_positive", 4),
    ("fraction_positive", 13), ("fraction_positive", 6),
    ("fraction_positive", 9), ("fraction_positive", 20),
    ("fraction_positive", 37), ("fraction_positive", 10),
    ("fraction_positive", 31), ("fraction_positive", 5),
)


def _wide_spelling(shape: str, index: int) -> str:
    """One distinct spelling of one shape, at the canonical width."""
    tail = f"{index:03d}"
    if shape == "contradictory":
        return f"(-{tail})"
    if shape == "huge_negative":
        return "-" + _HUGE[:len(_HUGE) - 3] + tail
    if shape == "huge_positive":
        return _HUGE[:len(_HUGE) - 3] + tail
    if shape == "whole_negative":
        return f"-1{tail}"
    if shape == "whole_positive":
        return f"1{tail}"
    if shape == "fraction_negative":
        return f"-2{tail}.5"
    return f"2{tail}.5"


def _ceiling_values() -> "list[str]":
    """The 2,710-row source, 38 groups, the review's own published counts."""
    values: list[str] = []
    for index in range(len(_CEILING_PLAN)):
        shape, size = _CEILING_PLAN[index]
        values = values + [_wide_spelling(shape, index)] * size
    return values


@pytest.fixture(scope="module")
def ceiling_case(
    tmp_path_factory: pytest.TempPathFactory,
) -> contract.Profile:
    """The producer description whose walk the ceiling used to stop."""
    folder = tmp_path_factory.mktemp("c3f1-ceiling")
    return _described(folder, _ceiling_values())


def test_the_ceiling_case_carries_the_counts_the_review_reported(
    ceiling_case: contract.Profile,
) -> None:
    """The vacuity floor again: 2,710 rows, 38 groups, those counts."""
    block = ceiling_case.columns[0]
    facts = _facts(ceiling_case)
    assert ceiling_case.n_rows == 2710
    assert block.role == "numeric_unrepresentable"
    assert (
        block.n_contradictory, block.n_out_of_range,
        block.n_numeric, block.n_not_numeric,
    ) == REVIEW_CLASSES
    assert (
        facts.n_whole, facts.n_fraction, facts.n_whole_unknown
    ) == REVIEW_WHOLES
    assert (
        facts.n_negative, facts.n_positive, facts.n_sign_unknown
    ) == REVIEW_SIGNS
    assert len(generation._groups_of(facts.n_distinct_by_occurrences)) == 38


def test_no_ceiling_stops_the_packing_walk_on_that_description(
    ceiling_case: contract.Profile,
) -> None:
    """Defect 2, MEASURED: the walk runs past the withdrawn ceiling.

    The earlier revision packed this description over a grid of six
    invented classes against the three sign counts and stopped after
    200,000 trips. That same grid, over these groups, enters more than
    200,000 states before it answers -- and it does answer. So a ceiling
    anywhere near the withdrawn one is not a bound on cost, it is a
    published count traded away, and reinstating one of any size at or
    below the number measured here fails this test.
    """
    facts = _facts(ceiling_case)
    groups = generation._groups_of(facts.n_distinct_by_occurrences)
    invented = [592, 879, 0, 424, 815, 0]
    signs = [facts.n_negative, facts.n_positive, facts.n_sign_unknown]
    permitted = [generation._spread_pairs(6, 3) for _each in groups]

    answer, entered = _states(
        lambda: generation._allotted_pairs(
            groups, invented, signs, permitted
        )
    )
    assert answer is not None, (
        "the walk found no answer at all on the description the review "
        "built, which is a different defect from the one measured here"
    )
    assert entered > 200000, (
        f"this description entered only {entered} states, so it no "
        "longer demonstrates that a producer description reaches the "
        "withdrawn ceiling"
    )


def test_the_ceiling_case_is_answered_by_the_joint_walk(
    ceiling_case: contract.Profile,
) -> None:
    """Defect 2, end to end, and by the JOINT route rather than by luck.

    The recount happening to match after the greedy fallback would prove
    nothing, so the fallback is made to fail: `_allocation` is the only
    way into it for this role, and it must not be reached at all. The
    run must also name no exact count as missed.
    """
    twin = _without_the_fallback(
        lambda: generation.generate(ceiling_case, 0)
    )
    assert _missed(twin) == []

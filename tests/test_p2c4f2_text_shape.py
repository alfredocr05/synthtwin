"""Review item P2-C4-F2: the shape of a column of free text is part of
the allocation, not an input to it.

WHAT WENT WRONG, IN ONE SENTENCE. Method G9.5 gave the two published
length ends and the two published word ends to the description's FIRST
TWO groups, walked every other length toward the published average, and
only then asked the grid of classes and alphabets for a packing inside
that shape -- so a shape the profile never published could make an exact
count unreachable that another shape reaches.

The review's own source is the witness, and it comes from the real
producer: twelve cells, one holding two words in three characters, five
holding one character the code alphabet has, six holding two characters
it does not. The description publishes `n_code_alphabet = 5`, and the
source's own twelve cells are an exact assignment of it. Pinning the
longest length and the largest word count onto the group of five bars
that group from the code alphabet -- a cell counted in that alphabet
holds one word, and a space is not one of its characters -- and no other
group covers five cells. Every seed wrote one code-alphabet cell against
the five published, and the report named the miss.

WHY THE REPAIR IS THE SHAPE AND NOT THE COUNT. Round 3 fixed the same
defect class for other roles by walking one grid over every published
family together. This is that repair carried to the one decision that
was still made in advance: which group carries each end, and what length
every other group takes. Both readings are offered in a fixed order and
the FIRST that packs every published count exactly is taken, so a
description the earlier rule already answered is answered identically,
byte for byte, and the reference vectors are unmoved.

THE SECOND HALF, and it is a different mechanism with the same cost. A
number written in the code alphabet used to need three characters,
because the only shape stated for it was an exponent. `-3` is two
characters, reads as a number, and holds a character the figures do not,
and a real table holds values like it: a source of one one-character
number, five two-letter words and six copies of `-3` publishes twelve
code-alphabet cells of which six read as numbers, its own values are the
assignment, and the twin could not write one. The family now begins at
two characters.

WHAT IS PROVED HERE. Not that one case passes -- this item was twice
declared closed on witnesses. The claim the method makes is general:
*a description a real table produced always has a packing, because that
table's own values are one*. So the battery below puts several thousand
free-text columns through the REAL producer and requires that not one of
them loses a single exact count, with the fallback packing forbidden
throughout. Two mutants restore the two rules this repair replaced and
must fail.
"""

import itertools
import pathlib

import pytest

import fixtures
from synthtwin import (
    canonical,
    contract,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    taxonomy,
)

# Every fact of a column of free text that the ratified matrix makes
# EXACT-OBSERVABLE (`docs/plans/phase-2-generator.md`, P2-D6). A twin
# that names any of these in its deviation ledger has missed an exact
# fact, whichever mechanism did it.
EXACT = (
    "n_present",
    "n_missing",
    "n_numeric",
    "n_not_numeric",
    "n_out_of_range",
    "n_contradictory",
    "n_all_digits",
    "n_code_alphabet",
    "length.min",
    "length.max",
    "words.min",
    "words.max",
    "n_distinct",
    "n_distinct_folded",
    "n_distinct_by_occurrences",
)

# The review's own source, value for value.
REVIEW_SOURCE = ["a b"] + ["x"] * 5 + ["!!"] * 6

# The same defect reached through the family table instead of the shape:
# a two-character number that the code alphabet holds.
SHORT_NUMBER_SOURCE = ["7"] + ["ab"] * 5 + ["-3"] * 6


def _described(
    folder: pathlib.Path, values: "list[str]"
) -> contract.Profile:
    """Write a one-column table, describe it with the REAL producer, load it.

    No hand-built document appears in this file. What is exercised is
    the path a person walks: table, `synthtwin profile`, `synthtwin
    generate`.
    """
    path = fixtures.write(
        folder, "table.csv", fixtures.single_column_table("value", values)
    )
    table = reading.read_table(str(path))
    document = profile.build_document(table, taxonomy.Settings(), [])
    target = folder / "table-profile.json"
    target.write_text(
        canonical.serialize(document), encoding="utf-8", newline="\n"
    )
    return contract.load_profile(str(target))


def _text_facts(loaded: contract.Profile) -> contract.TextFacts:
    """The one column's free-text facts, checked to be those."""
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.TextFacts), (
        "this source did not reach the free-text role, so it proves "
        "nothing about G9.5"
    )
    return facts


def _missed(twin: generation.Twin) -> "list[tuple[str, str, str]]":
    """Every exact fact the twin named as missed, as the report names it."""
    return [
        (note.fact, note.published, note.achieved)
        for note in twin.deviations
        if note.fact in EXACT
    ]


def _counted(twin: generation.Twin) -> "dict[str, int]":
    """The alphabet and class counts, RECOUNTED from the written cells.

    Nothing here trusts what the generator says it did. A cell counted
    in the code alphabet is one written from letters, figures, hyphens
    and underscores alone; a cell counted in the figures is one written
    from figures alone.
    """
    cells = [row[0] for row in twin.rows if row[0] != ""]
    code = 0
    digits = 0
    numbers = 0
    for cell in cells:
        if all(
            character.isalnum() or character in "-_" for character in cell
        ):
            code = code + 1
        if cell.isdigit():
            digits = digits + 1
        if parsing.classify_number(cell) == parsing.NUMBER:
            numbers = numbers + 1
    return {
        "n_present": len(cells),
        "n_code_alphabet": code,
        "n_all_digits": digits,
        "n_numeric": numbers,
        "length.min": min(len(cell) for cell in cells),
        "length.max": max(len(cell) for cell in cells),
        "words.min": min(parsing.token_count(cell) for cell in cells),
        "words.max": max(parsing.token_count(cell) for cell in cells),
    }


class _NoFallback:
    """The greedy fallback packing, made to fail loudly while in force.

    A recount that happens to match after one published family was
    packed after another proves nothing about the joint allocation, so
    the fallback is not allowed to answer: reaching it at all is the
    failure this guard reports.
    """

    def __enter__(self) -> None:
        self.packed = generation._allocation

        def refused(*given: object) -> object:
            raise AssertionError(
                "this column fell back to packing one published family "
                "after another, so no shape of the grid answered it"
            )

        generation._allocation = refused  # type: ignore[assignment]

    def __exit__(self, *given: object) -> None:
        generation._allocation = self.packed  # type: ignore[assignment]


def test_the_reviews_own_source_holds_every_published_count(
    tmp_path: pathlib.Path,
) -> None:
    """The producer's own twelve-cell source, end to end, on 64 seeds.

    The published facts first, so the case is visible rather than
    asserted: three groups covering 1, 5 and 6 cells, lengths 1 to 3,
    word counts 1 to 2, and five cells the code alphabet holds.
    """
    loaded = _described(tmp_path, REVIEW_SOURCE)
    block = loaded.columns[0]
    facts = _text_facts(loaded)
    assert facts.n_distinct_by_occurrences == {"1": 1, "5": 1, "6": 1}
    assert (facts.length.minimum, facts.length.maximum) == (1, 3)
    assert (facts.words.minimum, facts.words.maximum) == (1, 2)
    assert facts.n_code_alphabet == 5
    assert block.n_present == 12

    for seed in range(64):
        with _NoFallback():
            twin = generation.generate(loaded, seed)
        counted = _counted(twin)
        assert counted["n_code_alphabet"] == 5, (
            f"seed {seed} wrote {counted['n_code_alphabet']} code-alphabet "
            "cells against the five the description publishes"
        )
        assert counted["n_all_digits"] == facts.n_all_digits
        assert counted["length.min"] == 1
        assert counted["length.max"] == 3
        assert counted["words.min"] == 1
        assert counted["words.max"] == 2
        assert _missed(twin) == []


def test_the_ends_moved_off_the_first_two_groups_to_do_it(
    tmp_path: pathlib.Path,
) -> None:
    """And the repair is the one the review named, not a lucky neighbour.

    The allocation gave the published ends to a different pair of groups
    than the description's first two, and that is the whole of the
    change: the group covering five cells now carries NEITHER end, so
    its word count is free to come down to one and it can answer for the
    five code-alphabet cells. The group covering six carries the longest
    length and the largest word count instead.
    """
    loaded = _described(tmp_path, REVIEW_SOURCE)
    plan = generation.plan_generation(loaded)
    carriers = plan.columns[0].carriers
    assert carriers != (0, 1)
    groups = generation._groups_of(
        _text_facts(loaded).n_distinct_by_occurrences
    )
    assert groups == (1, 5, 6)
    assert 5 not in (groups[carriers[0]], groups[carriers[1]])
    twin = generation.generate(loaded, 0)
    five = [
        cell for cell in (row[0] for row in twin.rows) if cell == "A"
    ]
    assert len(five) == 5


def test_restoring_the_pre_assignment_loses_the_count(
    tmp_path: pathlib.Path,
) -> None:
    """THE MUTANT. Pin the ends to the first two groups and the count goes.

    This is revision 5's rule exactly: one shape, chosen before the
    grid. It must fail -- and the failure must be the review's own
    number, one code-alphabet cell against five -- or this file is
    testing something the repair did not do.

    The miss is also NAMED: the ledger carries `n_code_alphabet` with
    both values and the rendered report prints them, which is what the
    generator owes for any published fact it cannot hold.
    """
    loaded = _described(tmp_path, REVIEW_SOURCE)
    choices = generation._shape_choices

    def only_the_first_pair(total: int) -> "list[tuple[int, int]]":
        return choices(total)[:1]

    generation._shape_choices = only_the_first_pair  # type: ignore[assignment]
    try:
        twin = generation.generate(loaded, 0)
    finally:
        generation._shape_choices = choices  # type: ignore[assignment]

    assert _counted(twin)["n_code_alphabet"] == 1
    named = [
        (note.published, note.achieved)
        for note in twin.deviations
        if note.fact == "n_code_alphabet"
    ]
    assert named == [("5", "1")]
    printed = rendering.report(loaded, twin)
    assert "n_code_alphabet" in printed


def test_a_two_character_number_the_code_alphabet_holds(
    tmp_path: pathlib.Path,
) -> None:
    """The second mechanism: `-3` is a number, and two characters is enough.

    The published counts are the point: twelve cells the code alphabet
    holds, of which one is written in figures alone and six read as
    numbers, at a longest published length of two. A construction whose
    numeric code-alphabet family began at three characters could not
    write those six, and every seed reported the miss.
    """
    loaded = _described(tmp_path, SHORT_NUMBER_SOURCE)
    block = loaded.columns[0]
    facts = _text_facts(loaded)
    assert facts.n_code_alphabet == 12
    assert facts.n_all_digits == 1
    assert facts.length.maximum == 2
    assert block.n_numeric == 7

    for seed in (0, 1, 63):
        with _NoFallback():
            twin = generation.generate(loaded, seed)
        counted = _counted(twin)
        assert counted["n_code_alphabet"] == 12
        assert counted["n_all_digits"] == 1
        assert counted["n_numeric"] == 7
        assert _missed(twin) == []


def test_restoring_the_three_character_code_number_loses_the_count(
    tmp_path: pathlib.Path,
) -> None:
    """THE SECOND MUTANT. Take the two-character shape away and it goes.

    The exponent form needs three characters. With it as the only
    numeric shape the code alphabet has, this description's own values
    stop being writable and the counts are missed and named.
    """
    loaded = _described(tmp_path, SHORT_NUMBER_SOURCE)
    room = generation._family_room
    spelling = generation._number_at

    def only_from_three(kind: str, band: str, length: int, words: int) -> int:
        if (
            kind == generation._CLASS_NUMBER
            and band == generation._BAND_CODE
            and length < 3
        ):
            return 0
        return room(kind, band, length, words)

    def no_short_form(band: str, length: int, index: int) -> "str | None":
        if band == generation._BAND_CODE and length < 3:
            return None
        return spelling(band, length, index)

    generation._family_room = only_from_three  # type: ignore[assignment]
    generation._number_at = no_short_form  # type: ignore[assignment]
    try:
        twin = generation.generate(loaded, 0)
    finally:
        generation._family_room = room  # type: ignore[assignment]
        generation._number_at = spelling  # type: ignore[assignment]

    missed = {note[0] for note in _missed(twin)}
    assert "n_all_digits" in missed or "n_code_alphabet" in missed


def test_a_first_pair_answer_leaves_the_shape_where_it_was(
    tmp_path: pathlib.Path,
) -> None:
    """The search costs nothing where the earlier rule already answered.

    The shapes are offered in a fixed order whose first member is the
    description's own first two groups, so a column the pre-assignment
    already packed keeps its ends, its lengths and its bytes. That is
    what leaves the frozen reference vectors unmoved.
    """
    loaded = _described(tmp_path, ["7", "7", "42", "ab", "x!"])
    plan = generation.plan_generation(loaded)
    assert plan.columns[0].carriers == (0, 1)
    assert generation._shape_choices(4)[0] == (0, 1)
    assert generation._shape_choices(1) == [(0, 0)]
    assert len(generation._shape_choices(4)) == 12


def test_any_published_length_is_open_to_a_group_carrying_no_end() -> None:
    """The wider reading, and the one claim it rests on.

    A group carrying neither end is held to no length by the
    description, so the pairs it may stand in are the pairs SOME
    permitted length allows. The union is taken over the whole published
    range rather than reasoned about; this checks the taking of it
    against the same union computed here, so a family whose room stops
    growing with the length cannot quietly narrow the reading.
    """
    for shortest in range(1, 6):
        for longest in range(shortest, 9):
            for words in (1, 2):
                room: dict[tuple[int, int], int] = {}
                reached = generation._pair_reach(
                    shortest, longest, words, room
                )
                by_hand = 0
                for length in range(shortest, longest + 1):
                    by_hand = by_hand | generation._pair_permits(
                        length, words, False
                    )
                assert reached == by_hand
                assert reached & generation._pair_permits(
                    shortest, words, False
                ) == generation._pair_permits(shortest, words, False)


# The values the battery draws from. Every shape a one-column table of
# short text can take that this construction has a family for: figures,
# a decimal, a two-word cell, code-alphabet words, cells outside that
# alphabet, a one-character cell, and a two-character number.
POOL = (
    "7",
    "42",
    "913",
    "5.5",
    "ab",
    "q_z",
    "x!",
    "no!!",
    "a b",
    "one two",
    "x",
    "!!",
    "z9",
    "-3",
)

# Three repetition patterns over three values, each covering twelve
# cells or six, and each order of them, so which group is first varies.
PATTERNS = ((1, 5, 6), (2, 2, 8), (1, 2, 3))
ORDERS = ((0, 1, 2), (1, 2, 0), (2, 0, 1))


def test_no_producer_free_text_column_loses_an_exact_count(
    tmp_path: pathlib.Path,
) -> None:
    """THE GENERAL CLAIM, checked rather than asserted.

    G9.5 says a description a real table produced always has a packing,
    because that table's own values are one. That claim was made in
    round 1, repeated in round 3, and disproved in round 4 by a
    twelve-cell source. So it is checked here over every three-value
    free-text column this pool and these repetition patterns build --
    several thousand of them, each described by the REAL producer and
    generated with the fallback packing forbidden.

    A column that misses one exact fact fails this test whichever
    mechanism missed it: the shape, the grid or the family table. The
    assertion is on the recounted cells and on the deviation ledger
    together, so neither a silent miss nor a named one passes.
    """
    reached = 0
    for step, trio in enumerate(itertools.combinations(POOL, 3)):
        for pattern in PATTERNS:
            for order in ORDERS:
                values: list[str] = []
                for place in range(3):
                    values = values + [trio[place]] * pattern[order[place]]
                folder = tmp_path / f"case-{step}-{pattern[0]}-{order[0]}"
                if not folder.exists():
                    folder.mkdir()
                loaded = _described(folder, values)
                if not isinstance(
                    loaded.columns[0].facts, contract.TextFacts
                ):
                    continue
                reached = reached + 1
                facts = _text_facts(loaded)
                with _NoFallback():
                    twin = generation.generate(loaded, 0)
                counted = _counted(twin)
                assert _missed(twin) == [], (
                    f"{values}: the twin named an exact fact as missed"
                )
                assert counted["n_code_alphabet"] == facts.n_code_alphabet, (
                    f"{values}: code-alphabet cells"
                )
                assert counted["n_all_digits"] == facts.n_all_digits, (
                    f"{values}: all-figure cells"
                )
                assert counted["n_numeric"] == loaded.columns[0].n_numeric, (
                    f"{values}: cells reading as numbers"
                )
                assert counted["length.min"] == facts.length.minimum
                assert counted["length.max"] == facts.length.maximum
                assert counted["words.min"] == facts.words.minimum
                assert counted["words.max"] == facts.words.maximum
    assert reached > 900, (
        "this battery reached too few columns of free text to say anything "
        f"general: {reached}"
    )


def test_the_battery_would_have_caught_the_reported_defect(
    tmp_path: pathlib.Path,
) -> None:
    """And the battery is not vacuous: the old rule fails it.

    A battery that passes under the rule the review rejected proves
    nothing. This runs a slice of it with the pre-assignment restored
    and requires columns to lose exact counts, so the assertions above
    are known to be able to fail.
    """
    choices = generation._shape_choices

    def only_the_first_pair(total: int) -> "list[tuple[int, int]]":
        return choices(total)[:1]

    lost = 0
    reached = 0
    generation._shape_choices = only_the_first_pair  # type: ignore[assignment]
    try:
        for step, trio in enumerate(itertools.combinations(POOL, 3)):
            values: list[str] = []
            for place in range(3):
                values = values + [trio[place]] * (1, 5, 6)[place]
            folder = tmp_path / f"case-{step}"
            folder.mkdir()
            loaded = _described(folder, values)
            if not isinstance(loaded.columns[0].facts, contract.TextFacts):
                continue
            reached = reached + 1
            if _missed(generation.generate(loaded, 0)):
                lost = lost + 1
    finally:
        generation._shape_choices = choices  # type: ignore[assignment]
    assert lost > 20, (
        "the pre-assignment lost a count on too few of this slice, so the "
        f"battery above is not evidence of anything: {lost} of {reached}"
    )


def test_the_end_carriers_are_what_the_bounds_are_measured_against(
    tmp_path: pathlib.Path,
) -> None:
    """The approximated bounds follow the pins the allocation chose.

    `length.mean`, `length.p50` and `words.mean` are APPROXIMATED, and
    their bounds are statements about the walk that filled the groups
    AROUND the two carrying the ends (G12.6). Measuring them against an
    assumed pair where the run used another is a bound that describes a
    construction nobody ran, so the plan records the pair and the
    measurement reads it.
    """
    loaded = _described(tmp_path, REVIEW_SOURCE)
    plan = generation.plan_generation(loaded)
    carriers = plan.columns[0].carriers
    facts = _text_facts(loaded)
    groups = generation._groups_of(facts.n_distinct_by_occurrences)
    assert generation._pinned_totals(groups, 1, 3, carriers) != (
        generation._pinned_totals(groups, 1, 3, (0, 1))
    )
    twin = generation.generate(loaded, 0)
    measured = {found.fact: found for found in twin.approximations}
    assert "length.mean" in measured
    assert measured["length.mean"].inside
    assert measured["length.p50"].inside


def test_two_groups_of_the_same_size_are_the_same_question(
    tmp_path: pathlib.Path,
) -> None:
    """The one skip the search makes, checked rather than asserted.

    The shapes are offered in a fixed order and a pair whose two group
    SIZES an earlier pair already offered is skipped, which is what
    keeps the walk bounded by the number of different sizes instead of
    the number of groups. That skip is only free if two pairs with the
    same two sizes pose the same packing question -- so this builds
    every pair's shape by hand over a battery of producer columns and
    requires the multiset of (size, permitted cells) to be the same
    within each pair of sizes. A group's identity is not among the facts
    the grid reads, and this is what says so.
    """
    checked = 0
    for step, trio in enumerate(itertools.combinations(POOL[:9], 3)):
        values: list[str] = []
        for place in range(3):
            values = values + [trio[place]] * (2, 2, 8)[place]
        folder = tmp_path / f"case-{step}"
        folder.mkdir()
        loaded = _described(folder, values)
        if not isinstance(loaded.columns[0].facts, contract.TextFacts):
            continue
        facts = _text_facts(loaded)
        groups = generation._groups_of(facts.n_distinct_by_occurrences)
        for reach in (False, True):
            posed: dict[tuple[int, int], object] = {}
            for carriers in generation._shape_choices(len(groups)):
                room: dict[tuple[int, int], int] = {}
                lengths, counts, _notes = generation._text_shape(
                    loaded.columns[0], facts, groups, carriers
                )
                permits = generation._text_permits(
                    facts, lengths, counts, carriers, reach, room
                )
                question = tuple(sorted(
                    (groups[place], permits[place])
                    for place in range(len(groups))
                ))
                sizes = (groups[carriers[0]], groups[carriers[1]])
                if sizes in posed:
                    assert posed[sizes] == question, (
                        f"{values}: two pairs of the sizes {sizes} pose "
                        "different packing questions, so skipping the "
                        "second one can lose an assignment"
                    )
                    checked = checked + 1
                    continue
                posed[sizes] = question
    assert checked > 50, (
        f"too few pairs shared a size pair to say anything: {checked}"
    )


def test_an_unreached_end_is_named_when_one_happens(
    tmp_path: pathlib.Path,
) -> None:
    """The recount of the four ends can fail, so it means something.

    A check that cannot fail is a defect. This hands the recount cells
    that hold neither published end and requires it to name both, with
    the published value beside the achieved one.
    """
    loaded = _described(tmp_path, REVIEW_SOURCE)
    column = loaded.columns[0]
    named = {
        note.fact: (note.published, note.achieved)
        for note in generation._extreme_notes(column, ["ab", "ab", "ab"])
    }
    assert named["length.min"] == ("1", "2")
    assert named["length.max"] == ("3", "2")
    assert named["words.max"] == ("2", "1")
    assert "words.min" not in named
    twin = generation.generate(loaded, 0)
    cells = [row[0] for row in twin.rows]
    assert generation._extreme_notes(column, cells) == []


@pytest.mark.parametrize("seed", (0, 1, 2, 3, 63))
def test_the_same_description_and_seed_give_the_same_cells(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """The search is a function of the description and of nothing else.

    Two runs of the same description and seed write the same cells: the
    shapes are offered in an order fixed by the description, the first
    that packs is taken, and no random word is drawn to settle it.
    """
    loaded = _described(tmp_path, REVIEW_SOURCE)
    first = generation.generate(loaded, seed)
    second = generation.generate(loaded, seed)
    assert first.rows == second.rows

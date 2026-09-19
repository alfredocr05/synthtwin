"""Plan P4-D298: an absorbed count is owed as the producer publishes it.

WHAT WENT WRONG. Plan P4-D277 put the two alphabet counts of the two
roles that publish no value -- free text and a declared record number --
and the four class counts of a record number through the disclosure
rule: where a side is below the census line the smaller is counted into
the larger, and the block publishes nought or every present cell. The
generator went on packing those numbers as if they were measured counts
of the table, and they are not: eleven figures beside one `ab` publish
`n_all_digits 12` beside `n_numeric 11`, which no assignment of whole
groups meets. Measured at e53d5f4, with the fallback packing forbidden:
158 of the 3,186 producer columns of review item P2-C4-F2's battery fell
to it, six of the 200 record-number columns of P2-C5-F2's missed a class
count, an alphabet count or the whole-number fact on every seed, and the
refusal `generation-whole-numbers-need-room` stopped a column whose own
values are its witness.

THE READING. `synthtwin validate` holds a twin to its description by
describing the twin again, so a published absorbed count is met wherever
the twin's own description publishes the same number -- and the table
itself meets it in exactly that sense and no other. So the generator
packs the PUBLISHED counts first, and only where they have no packing,
or where the cells built from them miss a count as published, every
other reading the producer would have published the same way, in the
stated order (`parsing.counts_absorbed_to`, `parsing.parts_absorbed_to`).

Every table here is built by seeded neutral code at runtime (plan D13),
and each repair is proved twice: from the reproduction, end to end with
both files validated at exit 0, and by withdrawing the rule in place.
"""

import pathlib

import pytest

import fixtures
from synthtwin import (
    contract,
    generation,
    parsing,
    profile,
    reading,
    taxonomy,
)
from tests.test_final_review_labels import _round_trip

# The free-text reproduction: eleven figures and one word.
FIGURES_AND_A_WORD = ["7"] * 5 + ["42"] * 6 + ["ab"]

# The record-number reproductions. The first is `case-16` of the
# P2-C5-F2 battery value for value; the second is its `case-21` with the
# one `7E999` written `7e999`, because the capital exponent makes a
# layout of its own that the twin misses whichever reading it takes (the
# published reading misses it too), and this file holds the reading and
# not that layout.
TEXT_AMONG_NUMBERS = ["-463"] * 15 + ["-4"] * 8 + ["bLMQsN", "5e999"]
CODE_AMONG_CONTRADICTIONS = ["(-6)"] * 10 + ["7e999"] * 4 + ["8xEa"]
ONE_FIGURE_AMONG_SIGNS = ["7"] + ["-3"] * 20


def _described(
    folder: pathlib.Path,
    values: "list[str]",
    declared: "list[str] | None" = None,
) -> contract.Profile:
    """A one-column table described by the REAL producer, and loaded."""
    folder.mkdir(parents=True, exist_ok=True)
    path = fixtures.write(
        folder, "table.csv", fixtures.single_column_table("value", values)
    )
    table = reading.read_table(str(path))
    document = profile.build_document(
        table, taxonomy.Settings(), declared if declared else []
    )
    target = fixtures.write_profile(folder, "table-profile.json", document)
    return contract.load_profile(str(target))


def _forbid_the_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reaching the family-after-family packing at all fails the test."""

    def refused(*given: object) -> object:
        raise AssertionError(
            "the column fell back to packing one published family after "
            "another, so no reading of its counts was packed"
        )

    monkeypatch.setattr(generation, "_allocation", refused)


# ------------------------------------------ the readings, from the rule


@pytest.mark.parametrize("floor", (1, 3, 11))
def test_every_count_the_rule_publishes_alike_is_a_reading(floor: int) -> None:
    """`counts_absorbed_to` is the preimage of `absorbed_total`, exhausted.

    Written from the rule's statement rather than from the function: for
    every population up to 40 and every count it could publish, the
    counts that publish it are found by asking `absorbed_total` of every
    count from nought to the population, and the reading must be exactly
    that set, the published count first where it is in it, the rest in
    ascending distance from it.
    """
    for population in range(41):
        for published in range(population + 1):
            want = [
                count
                for count in range(population + 1)
                if parsing.absorbed_total(count, population, floor)
                == published
            ]
            got = parsing.counts_absorbed_to(published, population, floor)
            assert sorted(got) == want, (population, published)
            if published in want:
                assert got[0] == published
            distances = [abs(count - published) for count in got]
            assert distances == sorted(distances)


@pytest.mark.parametrize("floor", (1, 3))
def test_every_partition_x2_publishes_alike_is_a_reading(floor: int) -> None:
    """`parts_absorbed_to` is the preimage of `absorbed_parts`, exhausted.

    Every four-part partition of every total up to fourteen is put
    through the X2 rule, which gives each published partition the set of
    measured ones that publish it; the reading must be exactly that set,
    the published partition first, then by cells moved.
    """
    preimage: "dict[tuple[int, ...], list[list[int]]]" = {}
    for total in range(15):
        for numbers in range(total + 1):
            for large in range(total - numbers + 1):
                for contradictory in range(total - numbers - large + 1):
                    measured = [
                        numbers,
                        large,
                        contradictory,
                        total - numbers - large - contradictory,
                    ]
                    key = tuple(parsing.absorbed_parts(measured, floor))
                    preimage[key] = preimage.get(key, []) + [measured]
    for key, measured in preimage.items():
        got = parsing.parts_absorbed_to(list(key), floor)
        assert sorted(got) == sorted(measured), key
        assert got[0] == list(key), key
        moved = [
            sum(abs(one[place] - key[place]) for place in range(4))
            for one in got
        ]
        assert moved == sorted(moved), key


# --------------------------------------------------------- free text


def test_eleven_figures_and_a_word_pack_as_published(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The free-text reproduction, with the fallback packing forbidden.

    The description is derived, not read off: the one `ab` outside the
    figures is below the line `census_floor(1) = 2` and eleven is at
    least half of twelve (`2 * 11 >= 12`), so `absorbed_total(11, 12, 1)`
    publishes twelve figures-only cells; all twelve cells are in the code
    alphabet and twelve is published as measured; eleven read as numbers,
    and free text publishes that count as measured. Twelve cells in
    figures alone are twelve numbers, so the published pair has no
    packing; the first reading after it (`_alphabet_readings` order, one
    cell moved) is the table's own eleven, the twin holds eleven cells in
    figures alone, and describing it again publishes twelve.
    """
    loaded = _described(tmp_path, FIGURES_AND_A_WORD)
    block = loaded.columns[0]
    facts = block.facts
    assert isinstance(facts, contract.TextFacts)
    assert (facts.n_all_digits, facts.n_code_alphabet) == (12, 12)
    assert (block.n_numeric, block.n_not_numeric) == (11, 1)
    _forbid_the_fallback(monkeypatch)
    for seed in (0, 1, 63):
        twin = generation.generate(loaded, seed)
        cells = [cell for cell in twin.columns[0] if cell != ""]
        figures = len([cell for cell in cells if parsing.is_digit_text(cell)])
        coded = len([cell for cell in cells if parsing.is_code_text(cell)])
        assert (figures, coded) == (11, 12)
        assert parsing.absorbed_total(figures, len(cells), 1) == 12
        assert [note.fact for note in twin.deviations] == []


def test_eleven_figures_and_a_word_round_trip(tmp_path: pathlib.Path) -> None:
    """Describe, build, describe the twin again, validate BOTH at exit 0."""
    result = _round_trip(tmp_path, {"value": FIGURES_AND_A_WORD})
    assert result["generated"] == 0
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)
    assert "n_all_digits" not in result["report"]
    assert "n_code_alphabet" not in result["report"]


def test_withdrawing_the_readings_puts_the_fallback_back(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """THE MUTANT: pack the published counts and nothing else.

    With `_text_readings` cut to its first reading -- the rule before
    this repair -- the reproduction reaches the fallback packing again,
    which is the failure the battery of P2-C4-F2 forbids.
    """
    readings = generation._text_readings
    monkeypatch.setattr(
        generation,
        "_text_readings",
        lambda column, facts, floor: readings(column, facts, floor)[:1],
    )
    loaded = _described(tmp_path, FIGURES_AND_A_WORD)
    _forbid_the_fallback(monkeypatch)
    with pytest.raises(AssertionError, match="fell back"):
        generation.generate(loaded, 0)


def test_the_table_itself_is_not_named_by_the_recount(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The alphabet recount reads the cells as the producer does.

    Handed the TABLE's own twelve cells, `_alphabet_notes` names nothing,
    because the table publishes these very counts. THE MUTANT: with the
    absorption withdrawn from the recount -- the rule before this repair
    -- it names `n_all_digits` on the table itself, twelve published
    against eleven, which is what the twin's report filed on every twin
    that held the table's own shape.
    """
    loaded = _described(tmp_path, FIGURES_AND_A_WORD)
    column = loaded.columns[0]
    assert generation._alphabet_notes(column, FIGURES_AND_A_WORD, 1) == []
    monkeypatch.setattr(
        parsing, "absorbed_total", lambda count, population, floor: count
    )
    named = [
        (note.fact, note.published, note.achieved)
        for note in generation._alphabet_notes(
            column, FIGURES_AND_A_WORD, 1
        )
    ]
    assert named == [("n_all_digits", "12", "11")]


# ---------------------------------------------------- record numbers


def test_a_text_cell_counted_as_a_number_keeps_the_whole_number_fact(
    tmp_path: pathlib.Path,
) -> None:
    """`case-16`: the published reading wrote twenty-five whole numbers.

    One `bLMQsN` and one `5e999` are each below the line and are counted
    into the numbers (X2), so the block publishes `n_numeric 25` and
    nothing else -- and `all_whole_numbers: false`, which only a cell
    those counts do not show can make true of the table. The twin now
    holds a cell that is not a whole number, its own description
    publishes the same four counts, and both files validate.
    """
    result = _round_trip(
        tmp_path, {"code": TEXT_AMONG_NUMBERS}, ("--identifier", "code")
    )
    block = [
        one for one in result["document"]["columns"] if one["name"] == "code"
    ][0]
    assert (
        block["n_numeric"],
        block["n_out_of_range"],
        block["n_contradictory"],
        block["n_not_numeric"],
    ) == (25, 0, 0, 0)
    assert block["all_whole_numbers"] is False
    assert result["generated"] == 0
    cells = [cell for cell in result["twin"]["code"] if cell != ""]
    whole = [
        cell
        for cell in cells
        if parsing.numeric_whole(parsing.trimmed(cell)) == parsing.WHOLE_YES
    ]
    assert len(whole) < len(cells)
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)
    assert "all_whole_numbers" not in result["report"]


def test_a_code_cell_counted_as_a_contradiction_is_written_in_the_code(
    tmp_path: pathlib.Path,
) -> None:
    """`case-21`: no contradictory numeral is written in the code alphabet.

    The one `8xEa` reads as text, a part of one below the line, so X2
    counts it into the ten contradictory cells and the block publishes
    eleven; it is also one of the five code-alphabet cells (with the four
    `7e999`), and five of fifteen is published as measured. So five
    code-alphabet cells stand beside four numerals out of range, and the
    fifth is among the contradictions, which no family writes in the code
    alphabet. The reading that keeps it as text is found.
    """
    result = _round_trip(
        tmp_path,
        {"code": CODE_AMONG_CONTRADICTIONS},
        ("--identifier", "code"),
    )
    block = [
        one for one in result["document"]["columns"] if one["name"] == "code"
    ][0]
    assert (block["n_out_of_range"], block["n_contradictory"]) == (4, 11)
    assert block["n_code_alphabet"] == 5
    cells = [cell for cell in result["twin"]["code"] if cell != ""]
    coded = len(
        [cell for cell in cells if parsing.is_code_text(parsing.trimmed(cell))]
    )
    assert coded == 5
    # The text cell is counted among the contradictions exactly as the
    # table's own `8xEa` was, so the report names neither class.
    texts = [
        cell for cell in cells
        if parsing.classify_number(cell) == parsing.NOT_A_NUMBER
    ]
    assert len(texts) == 1
    assert "n_contradictory" not in result["report"]
    assert "n_not_numeric" not in result["report"]
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_a_one_figure_record_number_counted_away_is_not_refused(
    tmp_path: pathlib.Path,
) -> None:
    """The refusal asks every count the producer publishes alike.

    `7` beside twenty `-3`: every value a whole number, the shortest one
    character long, and the one cell in figures alone below the line, so
    `n_all_digits` is published as nought. At e53d5f4 this was refused
    as a pair that contradicts itself; the table is its own witness that
    it does not, and the twin writes one figure-only cell again.
    """
    result = _round_trip(
        tmp_path,
        {"code": ONE_FIGURE_AMONG_SIGNS},
        ("--identifier", "code"),
    )
    block = [
        one for one in result["document"]["columns"] if one["name"] == "code"
    ][0]
    assert block["n_all_digits"] == 0
    assert block["all_whole_numbers"] is True
    assert block["min_length"] == 1
    assert result["generated"] == 0
    cells = [cell for cell in result["twin"]["code"] if cell != ""]
    assert len([cell for cell in cells if parsing.is_digit_text(cell)]) == 1
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_withdrawing_the_record_number_readings_loses_the_counts(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """THE MUTANT: no reading but the published one.

    `_identifier_readings` answering nothing is the rule before this
    repair, and the two reproductions miss exactly what they missed.
    """
    monkeypatch.setattr(
        generation, "_identifier_readings", lambda *given: []
    )
    whole = _described(tmp_path / "whole", TEXT_AMONG_NUMBERS, ["value"])
    named = [note.fact for note in generation.generate(whole, 0).deviations]
    assert "all_whole_numbers" in named
    coded = _described(
        tmp_path / "coded", CODE_AMONG_CONTRADICTIONS, ["value"]
    )
    named = [note.fact for note in generation.generate(coded, 0).deviations]
    assert "n_code_alphabet" in named

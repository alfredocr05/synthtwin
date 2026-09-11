"""The number a column held most often, and how many cells held it.

Plan decision P4-D4.11, contract invariant Q18. The owner's fifth
numeric ask of 2026-08-26: "the mode, for columns where one value
dominates".

THE GAP IT MEASURES, measured before the fact was built. Five
three-hundred-row columns were described and generated, and the twin's
count of the column's most frequent value compared with the real one:
where a value genuinely dominates the twin was seventeen to twenty-eight
per cent short of it. That is the fidelity the owner named, and until
this fact existed nothing published said the number.

WHAT IS PINNED HERE:

- the mode is the commonest NUMBER, by the canonical triple, so two
  spellings of one number are one value;
- the tie rule is the SMALLEST of the tied, written down rather than
  left to whatever a mapping iterates in;
- a mode held by one cell is withheld, because every value ties there
  and the tie rule would otherwise publish the column's smallest number
  under a name saying it dominates;
- the small-cell floor withholds the PAIR and not the count alone;
- invariant Q18 refuses a value without a count, a count without a
  value, a count below two, and a count above the column's numbers;
- and the quality report LISTS both halves rather than holding a file
  to them, which is what REPORT-ONLY means here.

WHY IT IS REPORT-ONLY, stated because the first draft got it wrong.
Both halves are readable off a file, so they look checkable, and they
were written as CHECKS. A check is an OBLIGATION: the generator carves
no stratum for the mode, so a twin cannot meet the count, and
sixty-three tests went red -- "a twin of its own description misses
nothing" among them, which is the product's headline claim. This is
the fourth fact in the phase to walk into that trap and the rule that
came out of the first three holds: a fact whose exactness needs a
change to how cells are ALLOTTED is REPORT-ONLY until that change
lands. P4-D4.11 carries the design of the stratum that would make it
exact, on the model of the zero stratum whose published count the twin
already meets to the cell.
"""

import pathlib
import random
import tempfile

import fixtures
import pytest
from synthtwin import (
    contract,
    errors,
    generation,
    profile,
    reading,
    taxonomy,
    validation,
)


def _described(
    values: "list[str]", settings: "taxonomy.Settings | None" = None
) -> "tuple[dict, contract.Profile, pathlib.Path]":
    """One single-column table, described and read back."""
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "thing.csv", fixtures.single_column_table("thing", values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), settings or taxonomy.Settings(), []
    )
    written = fixtures.write_profile(folder, "thing.json", document)
    return document, contract.load_profile(f"{written}"), folder


# -- what the profiler publishes --------------------------------------


def test_the_mode_is_the_commonest_number_and_its_count() -> None:
    """A dose column with one common value names it and says how often."""
    values = ["10"] * 40 + ["20"] * 12 + ["25"] * 8 + ["30"] * 5
    document, _loaded, _folder = _described(values)
    column = document["columns"][0]
    assert column["mode"] == 10.0
    assert column["mode_count"] == 40


def test_two_spellings_of_one_number_are_one_value() -> None:
    """Identity is the canonical triple, not the text.

    `07` and `7` are two spellings and one number. A mode counted by
    spelling would find neither of them commonest here; counted by the
    number, seven is held by thirty cells.
    """
    values = ["07"] * 15 + ["7"] * 15 + ["8"] * 14 + ["9"] * 6
    document, _loaded, _folder = _described(values)
    column = document["columns"][0]
    assert column["mode"] == 7.0
    assert column["mode_count"] == 30, (
        "the two spellings of seven must count as one number, or the "
        "commonest number here is eight"
    )


def test_two_numbers_that_round_together_are_still_two() -> None:
    """Identity is the EXACT number and not the rounded one.

    `1e16` and `10000000000000001` are different numbers that land on
    one binary64 value. Counted by the rounded value they would be one
    group of twenty-four and the commonest thing in the column; counted
    by the canonical triple they are two groups of twelve, and the
    commonest number is the thirteen thirteens beside them.

    This is the mutation the sibling test above cannot catch: `07` and
    `7` share a float as well as a number, so grouping by either answers
    the same there.
    """
    values = (
        ["1e16"] * 12 + ["10000000000000001"] * 12 + ["13"] * 13 + ["14"] * 4
    )
    document, _loaded, _folder = _described(values)
    column = document["columns"][0]
    assert column["mode"] == 13.0, (
        "two numbers that merely round together were counted as one, "
        f"so the mode came out as {column['mode']}"
    )
    assert column["mode_count"] == 13


def test_the_tie_goes_to_the_smallest() -> None:
    """Where several numbers share the largest count, the smallest wins."""
    values = ["5", "5", "3", "3", "9", "9"] + [str(v) for v in range(10, 30)]
    document, _loaded, _folder = _described(values)
    column = document["columns"][0]
    assert column["mode"] == 3.0, (
        "three, five and nine are each held twice, and the rule is the "
        "smallest of them"
    )
    assert column["mode_count"] == 2


def test_a_mode_held_by_one_cell_is_withheld() -> None:
    """All-different values have no mode worth the name.

    Every value ties at one, so the tie rule would publish the column's
    smallest number under a name that says it dominates.
    """
    values = [f"{value}.5" for value in range(200)]
    document, _loaded, _folder = _described(values)
    column = document["columns"][0]
    assert column["mode"] is None
    assert column["mode_count"] == 0


def test_the_floor_withholds_the_pair_and_not_the_count_alone() -> None:
    """Below the floor BOTH keys go, because one of them is the fact.

    A value published without its count still says "this was the
    commonest number", which is the same disclosure in fewer words.
    """
    values = ["4"] * 6 + [str(value) for value in range(20, 220)]
    document, _loaded, _folder = _described(
        values, taxonomy.Settings(small_cell_floor=11)
    )
    column = document["columns"][0]
    assert column["mode"] is None, "six cells is under a floor of eleven"
    assert column["mode_count"] == 0

    document, _loaded, _folder = _described(
        values, taxonomy.Settings(small_cell_floor=1)
    )
    assert document["columns"][0]["mode"] == 4.0, (
        "the same column at a floor of one publishes the pair, so this "
        "fixture reaches the floor rule and not some other refusal"
    )
    assert document["columns"][0]["mode_count"] == 6


# -- invariant Q18, each half with its red case -----------------------


def _forged(edit) -> "tuple[dict, pathlib.Path]":
    """One conforming numeric document with one thing changed."""
    import copy

    values = ["10"] * 40 + ["20"] * 12 + ["25"] * 8 + ["30"] * 5
    document, _loaded, _folder = _described(values)
    forged = copy.deepcopy(document)
    edit(forged["columns"][0])
    folder = pathlib.Path(tempfile.mkdtemp())
    return forged, fixtures.write_profile(folder, "forged.json", forged)


@pytest.mark.parametrize(
    "why, edit",
    [
        ("a value with no count", lambda c: c.__setitem__("mode_count", 0)),
        ("a count with no value", lambda c: c.__setitem__("mode", None)),
        ("a count of one", lambda c: c.__setitem__("mode_count", 1)),
        (
            "a count above the column's numbers",
            lambda c: c.__setitem__("mode_count", c["n_numeric"] + 1),
        ),
    ],
)
def test_q18_refuses_a_document_that_breaks_it(why: str, edit) -> None:
    """Each half of Q18, against a document that breaks exactly it."""
    _forged_document, path = _forged(edit)
    with pytest.raises(errors.ProfileError) as refusal:
        contract.load_profile(f"{path}")
    assert "Q18" in str(refusal.value), why


def test_the_conforming_document_this_red_case_edits_still_loads() -> None:
    """The vacuity check: the fixture must load before it is broken."""
    _document, path = _forged(lambda column: None)
    loaded = contract.load_profile(f"{path}")
    assert loaded.columns[0].facts.mode == 10.0
    assert loaded.columns[0].facts.mode_count == 40


# -- the validator checks it, which the histogram cannot --------------


def test_the_quality_report_lists_the_pair_rather_than_checking_it() -> None:
    """REPORT-ONLY means LISTED, and listed means never silent.

    A published fact that appears in no check and no listing is one a
    reader cannot tell was never measured. So the pair is named in the
    report with the sentence saying no file is held to it, exactly as
    the histogram beside it is.
    """
    values = ["10"] * 40 + ["20"] * 12 + ["25"] * 8 + ["30"] * 5
    document, loaded, folder = _described(values)
    assert document["columns"][0]["mode_count"] == 40

    table = fixtures.write(
        folder, "again.csv", fixtures.single_column_table("thing", values)
    )
    outcome = validation.measure(loaded, f"{table}")
    listed = {
        listing.fact
        for listing in outcome.listings
        if "mode" in listing.fact
    }
    assert listed == {"numeric.mode", "numeric.mode_count"}
    checked = [check.fact for check in outcome.checks if "mode" in check.fact]
    assert not checked, (
        "the pair is REPORT-ONLY until the generator carves its "
        f"stratum, and these are being checked: {checked}"
    )


def test_a_column_with_no_dominant_value_gets_no_listing() -> None:
    """The listing follows the fact: no pair published, nothing listed.

    A listing on a column that published no mode would tell a reader
    something was withheld from them when nothing was.
    """
    values = [f"{value}.5" for value in range(200)]
    document, loaded, folder = _described(values)
    assert document["columns"][0]["mode"] is None

    table = fixtures.write(
        folder, "again.csv", fixtures.single_column_table("thing", values)
    )
    outcome = validation.measure(loaded, f"{table}")
    assert not [
        listing for listing in outcome.listings if "mode" in listing.fact
    ]


# -- what the twin does with it today ---------------------------------


def test_the_twin_holds_the_value_and_lands_near_the_count() -> None:
    """The state this fact is registered APPROXIMATED for.

    The generator does not carve a stratum for the mode yet, so the
    twin reproduces the dominant VALUE and lands near its count rather
    than on it. This test records what "near" is today, so that the
    stratum of P4-D4.11 has something to improve on and cannot land
    silently.
    """
    generator = random.Random(11)
    values = [
        str(generator.choice([10] * 6 + [20, 25, 30, 40]))
        for _each in range(300)
    ]
    document, loaded, _folder = _described(values)
    published = document["columns"][0]["mode_count"]
    assert published >= 150, "this fixture must have a dominant value"

    twin = generation.generate(loaded, 3)
    cells = [cell for cell in twin.columns[0] if cell]
    held = len([cell for cell in cells if float(cell) == 10.0])
    assert held > 0, "the twin lost the dominant value altogether"
    assert abs(held - published) <= published // 10, (
        f"the twin holds {held} of a published {published}; this test "
        "records how near the generator gets WITHOUT a mode stratum, so "
        "a change that moves it far away is a change to look at"
    )

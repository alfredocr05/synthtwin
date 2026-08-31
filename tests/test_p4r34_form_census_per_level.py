"""The form census misses when a level's held-back spellings are placed.

Residual R-P4-34, MEASURED here rather than repaired. Plan
`docs/plans/phase-4-columns.md` carries the entry and the price.

WHAT IS WRONG. `shape_forms` is published PER COLUMN (plan P4-D18,
contract 7.9). A published level whose spellings the floor held back
gets stand-in spellings from method G8.2 -- the case flips first, then
trailing spaces -- and only the case flips keep the label's written
form. Which held-back group takes a form-keeping spelling is therefore
decided by a rule reading the description, and THE DESCRIPTION DOES NOT
SAY WHICH HELD-BACK SPELLING WORE WHICH FORM. Two source columns whose
level entries are byte-identical can publish different censuses, so no
rule can be right about both.

THE FIVE TESTS BELOW ARE WITNESSES, not guards. Each fails when the
defect is repaired, which is when the witness should go, and each pins
the exact published and achieved counts so the defect cannot WORSEN
behind a passing test -- the lesson round 4 of the R-P4-62 landing
taught, where two witnesses kept only the SET of missed names and a
defect three times as large would have passed them.

THE RESIDUAL UNDERSTATED ITSELF UNTIL THIS WAS MEASURED. It said the
census "can fall one group short". It also OVERSHOOTS, by the same
mechanism running the other way: the label's own spelling is offered to
the LARGEST held-back group (G8.1), so where the source's form-bearing
held-back spelling was a SMALLER group the twin writes more cells in
that form than any source cell wore. The entry and the two contract
passages that said only the first half now say both.

THE FLOOR IS DECLARED, and it has to be. At the shipped default of one
(plan amendment A-P4-37) nothing is held back at all, so a level has no
held-back spelling to stand in for and this defect cannot occur.
Eleven is the floor these columns are described at, exactly as
`tests/test_p3v1f2_entry_table.py` declares its own and says why.
"""

import pathlib
import random
import tempfile

import fixtures
from synthtwin import (
    contract,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

# The floor every column below is described at. See the module
# docstring: at the shipped default of one nothing is held back and
# there is no defect to witness.
SMALL_CELL_FLOOR = 11

SEED = 7

# The level this file is about. One letter, so the case-flip supply of
# G8.2 is a single spelling -- which is the supply the residual names.
LOWER = "e11.9"
UPPER = "E11.9"
# A third spelling of the same folded label, carrying no form at all: a
# space is not one of the thirteen marks, so `shape_form` answers "" for
# it (contract 7.9, C6-31a).
SPACED = "E11.9  "
FORM = "@%%.%"


def _column(
    named_spelling: str, form_rows: int, plain_rows: int
) -> "tuple[dict, contract.Profile, pathlib.Path]":
    """One source column, described at the declared floor.

    ``named_spelling`` is the spelling enough rows wrote to be published.
    ``form_rows`` rows wrote the OTHER case, which has the same form and
    is held back; ``plain_rows`` rows wrote it with trailing spaces,
    which has no form and is held back too. The four ordinary levels
    beside it give the column a census large enough to publish.
    """
    other = UPPER if named_spelling == LOWER else LOWER
    values: "list[str]" = []
    for code, rows in (
        ("A10.1", 40), ("B20.2", 40), ("C30.3", 40), ("D40.4", 61)
    ):
        values = values + [code for _row in range(rows)]
    values = values + [named_spelling for _row in range(20)]
    values = values + [other for _row in range(form_rows)]
    values = values + [SPACED for _row in range(plain_rows)]
    folder = pathlib.Path(tempfile.mkdtemp())
    rows_out = [[value, "x"] for value in values]
    table = fixtures.write(
        folder, "codes.csv", fixtures.rows_to_csv(["code", "other"], rows_out)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(small_cell_floor=SMALL_CELL_FLOOR),
        [],
    )
    written = fixtures.write_profile(folder, "codes.json", document)
    return document, contract.load_profile(f"{written}"), folder


def _entry(document: dict) -> "dict[str, object]":
    """The published level entry this file is about."""
    for level in document["columns"][0]["levels"]:
        if level["label"] == LOWER:
            return level
    raise AssertionError("the column did not publish the level")


def _census_verdicts(
    described: contract.Profile, twin: generation.Twin, folder: pathlib.Path
) -> "list[validation.Check]":
    """What `synthtwin validate` says about the census of this column."""
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    return [
        check for check in outcome.checks
        if check.fact == "label.shape_forms" and check.column == "code"
    ]


def test_one_level_entry_two_censuses_so_no_rule_can_be_right_about_both(
) -> None:
    """THE MEASUREMENT THE RESIDUAL RESTS ON, and it is the whole case.

    Two source columns differing only in WHICH held-back spelling of one
    level wore the form. Their published level entries are identical key
    for key, so every rule reading the description reaches the same
    answer for both -- and the twins are identical cell for cell, which
    is asserted rather than argued. Their column censuses differ, so one
    of the two verdicts is wrong whatever the rule is.
    """
    large, large_described, large_folder = _column(LOWER, 5, 3)
    small, small_described, small_folder = _column(LOWER, 3, 5)

    assert _entry(large) == _entry(small)
    assert _entry(large)["variants_withheld"] == {"3": 1, "5": 1}

    large_twin = generation.generate(large_described, SEED)
    small_twin = generation.generate(small_described, SEED)
    assert list(large_twin.columns[0]) == list(small_twin.columns[0])

    # ...and the two columns published DIFFERENT censuses, which is the
    # fact the identical entries above cannot carry.
    assert large["columns"][0]["shape_forms"] == {FORM: 206}
    assert small["columns"][0]["shape_forms"] == {FORM: 204}

    # So exactly one of them is met, and the other misses.
    held = _census_verdicts(small_described, small_twin, small_folder)
    missed = _census_verdicts(large_described, large_twin, large_folder)
    assert [check.verdict for check in held] == ["HELD"]
    assert [check.verdict for check in missed] == ["MISSED"]


def test_the_census_falls_short_when_the_larger_group_wore_the_form(
) -> None:
    """THE DIRECTION THE RESIDUAL NAMES, pinned at its exact counts.

    The label's own spelling goes to the largest held-back group and is
    already published, so that group falls through to a trailing space
    and loses the form; the smaller group takes the one case flip. The
    census is short by the difference between the two group sizes.
    """
    document, described, folder = _column(LOWER, 5, 3)
    twin = generation.generate(described, SEED)
    checks = _census_verdicts(described, twin, folder)
    assert len(checks) == 1
    assert checks[0].subcheck == f"forms.published.{FORM}"
    assert checks[0].verdict == "MISSED"
    assert checks[0].published == "206"
    assert checks[0].achieved == "204"


def test_the_census_overshoots_when_the_smaller_group_wore_the_form(
) -> None:
    """THE DIRECTION THE RESIDUAL DOES NOT NAME, and it is as common.

    With the OTHER case published, the label's own spelling is free and
    is offered to the LARGEST held-back group -- so the twin writes five
    cells in the form where three of the source's wore it. The census is
    overshot, and the report calls that a miss exactly as it calls the
    shortfall one.
    """
    document, described, folder = _column(UPPER, 3, 5)
    twin = generation.generate(described, SEED)
    checks = _census_verdicts(described, twin, folder)
    assert len(checks) == 1
    assert checks[0].subcheck == f"forms.published.{FORM}"
    assert checks[0].verdict == "MISSED"
    assert checks[0].published == "204"
    assert checks[0].achieved == "206"


def test_the_twins_own_report_names_the_census_in_both_directions() -> None:
    """The contract's own claim beside this residual, measured.

    Section 9 says the shortfall "is named by the report". It is, and so
    is the overshoot: the deviation carries the published count and the
    achieved one, and its sentence says "a different number" rather than
    "fewer", so it is true of both directions.
    """
    for published_spelling, form_rows, plain_rows, said, got in (
        (LOWER, 5, 3, "206", "204"),
        (UPPER, 3, 5, "204", "206"),
    ):
        _document, described, _folder = _column(
            published_spelling, form_rows, plain_rows
        )
        twin = generation.generate(described, SEED)
        named = [
            one for one in twin.deviations
            if one.column == "code" and one.fact == "shape_forms"
        ]
        assert len(named) == 1, (published_spelling, named)
        assert said in named[0].published
        assert named[0].achieved == got


def test_every_form_bearing_spelling_of_a_level_wears_its_labels_form(
) -> None:
    """WHY A PER-LEVEL CENSUS WOULD BE ONE NUMBER AND NOT A MAP.

    A spelling belongs to a level when trimming and case folding it
    gives the label. A spelling that HAS a form holds only letters,
    digits and marks -- no space, so trimming changes nothing -- and
    case folding an ASCII letter leaves a letter, so the form is
    untouched. Every form-bearing spelling of a level therefore wears
    exactly `shape_form(label)`, and a level's census can name at most
    that one form.

    It is asserted here because it is the fact anybody building the
    closure rests on, and nothing else in the suite says it.
    """
    for label in ("e11.9", "4548-4", "0002-8215-01", "120/80", "a-1"):
        wanted = parsing.shape_form(label)
        assert wanted, label
        for spelling in (
            label.upper(), label.lower(), label.swapcase(), label
        ):
            assert parsing.folded(spelling) == label, spelling
            assert parsing.shape_form(spelling) == wanted, spelling
        # ...and a spelling of the same level carrying a space has NO
        # form, so it is counted nowhere rather than under another key.
        for spaced in (f"{label} ", f" {label}", f"{label}  "):
            assert parsing.folded(spaced) == label, spaced
            assert parsing.shape_form(spaced) == "", spaced

    # ...and the same property over built spellings rather than chosen
    # ones, because a hand-picked list proves only what was picked. The
    # alphabet reaches past ASCII on purpose: `ß` folds to two
    # characters and `İ` to two, and a rule reading a cell's LENGTH
    # would break on them. Neither has a form, so neither can.
    marks = [mark for mark in parsing.SHAPE_MARKS]
    alphabet = (
        ["a", "b", "c", "X", "Y", "Z", "0", "1", "9"]
        + marks
        + [" ", "ß", "İ", "é", "%", "@"]
    )
    rng = random.Random(11)
    seen = 0
    for _each in range(20000):
        built = ""
        for _place in range(rng.randint(1, 8)):
            built = f"{built}{rng.choice(alphabet)}"
        form = parsing.shape_form(built)
        if not form:
            continue
        seen = seen + 1
        assert parsing.shape_form(parsing.folded(built)) == form, built
    # ...and the walk really did reach form-bearing spellings, so the
    # loop above is not vacuously green.
    assert seen > 1000, seen

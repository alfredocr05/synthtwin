"""The per-level form census, and the defect it closes.

Residual R-P4-34, REPAIRED here. The owner ruled the fact in on
2026-08-31 (plan amendment A-P4-47) after the landing that measured the
defect recommended against it on disclosure grounds; the ruling and its
ground are in the amendment and are not re-opened here.

WHAT WAS WRONG. `shape_forms` is published PER COLUMN (plan P4-D18,
contract 7.9). A published level whose spellings the floor held back
gets stand-in spellings from method G8.2 -- the case flips first, then
trailing spaces -- and only the case flips keep the label's written
form. Which held-back group took a form-keeping spelling was therefore
decided by a rule reading the description, and THE DESCRIPTION DID NOT
SAY WHICH HELD-BACK SPELLING WORE WHICH FORM. Two source columns whose
level entries were byte-identical published different censuses, so no
rule could be right about both.

WHAT CLOSES IT. Every published level now carries `shape_form_cells`:
how many of its rows wrote it in the label's own written form (7.4.8).
It is ONE NUMBER and not a census, because every form-bearing spelling
of a level wears exactly `shape_form(label)` -- the property the last
test here pins. Given it, method G8.1a picks the sub-multiset of the
held-back group sizes that adds up to the level's outstanding form
debt, and G8.2a asks each group for a spelling wearing the form it was
allotted. The closure is EXACT: the same pair that could not be told
apart now publishes 25 and 23, and each twin meets its own census.

THE MEASURED VALUES ARE KEPT. The two columns and the four counts --
206, 204 and the two verdicts that used to disagree -- are the ones the
residual measured, so this file reads as a repair of exactly what was
reported and not as a fresh case built to pass.

WHAT IS NOT CLOSED, and it is stated here rather than left to be
found. There is NO SUM INVARIANT between a level's number and the
column's census (residual R-P4-80): the column census pools below the
floor, refuses a form the column has no room for, and counts the cells
of levels the floor held back, so it is a fact of its own beside these
and not their sum. And the form-keeping supply is finite -- a label of
one letter has one case flip -- so a description asking for more
form-bearing cells than the supply can spell is met as far as it goes
and NAMED where it is not.

THE FLOOR IS DECLARED, and it has to be. At the shipped default of one
(plan amendment A-P4-37) nothing is held back at all, so a level has no
held-back spelling to stand in for and this defect could not occur.
Eleven is the floor these columns are described at, exactly as
`tests/test_p3v1f2_entry_table.py` declares its own and says why.

AND SINCE RULING 6 REACHED A LABEL'S SPELLINGS, NO PRODUCER WRITES THE
SHAPE THIS FILE WAS BUILT ON (plan P4-D275). Every spelling below the
floor is counted into its level's commonest, so both source columns
below now publish `variants {"e11.9": 28}`, no held-back spelling and
`shape_form_cells 28` -- the fact that told them apart was a fact about
two groups below the line, and the ruling withholds it. The first test
is therefore a witness of the ruling, and the column census beside the
level counts the same respelled cells (plan P4-D275.1, the defect the
merge of the extra round's fixes exposed: the census went on counting
the raw cells, 206, beside a level saying 28, and the twin missed it).

THE GENERATOR'S WALK IS STILL REACHABLE, and the tests that guard it are
re-armed rather than dropped. Invariant W5 refuses a held-back key of 1
and nothing else, so a description carrying groups of three and five
below a floor of eleven still loads, and G8.1a and G8.2a still decide
what its twin writes. `_as_the_residual_measured` builds exactly the
description the residual measured -- the source's own document, with the
one level entry, `n_distinct` and the census restored by hand from the
rule statement -- and those tests run the walk on it. Their census is
counted off the twin's own cells: `synthtwin validate` describes the
file it checks under ruling 6 too, so it counts a twin's held-back
stand-ins into the level's commonest spelling and cannot see which group
wore the form (measured: MISSED 206 -> 209 on that twin, from the
ruling and not from the walk).
"""

import copy
import json
import pathlib
import random
import tempfile

import fixtures
from synthtwin import (
    contract,
    errors,
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
# there is no defect to repair.
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
# The same form with every letter lower case (contract C6-31d).
LOWER_FORM = "&%%.%"
# The cells of the four ordinary levels, every one in FORM: 40 + 40 + 40
# + 61.
ORDINARY_CELLS = 181


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


def _as_the_residual_measured(
    named_spelling: str, form_rows: int, plain_rows: int
) -> "tuple[dict, contract.Profile, pathlib.Path]":
    """The description the residual measured, which no producer writes now.

    The source column's own document with the three keys ruling 6 moved
    put back by hand, each from the rule statement and not from any
    earlier output: the level names its twenty-row spelling and holds
    back two spellings of ``form_rows`` and ``plain_rows`` rows; its
    form count is the named twenty plus the held-back rows that wore the
    form; the column holds the five named spellings and the two held
    back; and the census counts the ordinary cells, the named twenty and
    the held-back rows in the form. The two held-back spellings with a
    trailing space wear no form and are counted nowhere.
    """
    document, _described, folder = _column(named_spelling, form_rows, plain_rows)
    edited = copy.deepcopy(document)
    column = edited["columns"][0]
    for level in column["levels"]:
        if level["label"] == LOWER:
            level["variants"] = {named_spelling: 20}
            level["variants_withheld"] = {f"{form_rows}": 1, f"{plain_rows}": 1}
            level["shape_form_cells"] = 20 + form_rows
    column["n_distinct"] = 5 + 2
    column["shape_forms"] = {FORM: ORDINARY_CELLS + 20 + form_rows}
    return edited, _reloaded(edited, folder, "measured.json"), folder


def _twin_census(twin: generation.Twin) -> "dict[str, int]":
    """The twin's own form census, counted off its cells with the reader
    the fact is measured with. Cells with no form are counted nowhere."""
    counted: "dict[str, int]" = {}
    for cell in twin.columns[0]:
        form = parsing.shape_form(cell)
        if form:
            counted[form] = (counted[form] if form in counted else 0) + 1
    return counted


def _form_deviations(twin: generation.Twin) -> "list[generation.Deviation]":
    """What the twin's own report says about this column's forms."""
    return [
        one for one in twin.deviations
        if one.column == "code"
        and one.fact in ("shape_forms", "levels -> shape_form_cells")
    ]


def _entry(document: dict) -> "dict[str, object]":
    """The published level entry this file is about."""
    for level in document["columns"][0]["levels"]:
        if level["label"] == LOWER:
            return level
    raise AssertionError("the column did not publish the level")


def _reloaded(
    document: dict, folder: pathlib.Path, name: str
) -> contract.Profile:
    """One hand-edited description, taken back through the real loader."""
    written = fixtures.write_profile(folder, name, document)
    return contract.load_profile(f"{written}")


def _verdicts(
    described: contract.Profile,
    twin: generation.Twin,
    folder: pathlib.Path,
    fact: str,
) -> "list[validation.Check]":
    """What `synthtwin validate` says about one fact of this column."""
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    return [
        check for check in outcome.checks
        if check.fact == fact and check.column == "code"
    ]


def _census_verdicts(
    described: contract.Profile, twin: generation.Twin, folder: pathlib.Path
) -> "list[validation.Check]":
    """What `synthtwin validate` says about the census of this column."""
    return _verdicts(described, twin, folder, "label.shape_forms")


def test_the_two_columns_are_told_apart_and_each_twin_meets_its_census(
) -> None:
    """THE MEASUREMENT THE RESIDUAL RESTS ON, AND WHAT RULING 6 MADE OF IT.

    Two source columns differing only in WHICH held-back spelling of one
    level wore the form. Before amendment A-P4-47 their level entries
    were identical and one of the two verdicts was wrong whatever rule
    the generator used; A-P4-47 told them apart by `shape_form_cells`,
    25 and 23.

    THE OWNER'S RULING 6 OF 2026-09-17, AS P4-D275 ASKS IT OF A LABEL'S
    SPELLINGS, TAKES THAT DIFFERENCE AWAY, AND THIS IS NOW ITS WITNESS.
    The fact that told the columns apart was which of two groups BELOW
    THE FLOOR -- five rows and three -- wore the form, and the ruling
    counts every spelling below the floor into the level's commonest.
    Both levels are written `e11.9` in all 20 + 5 + 3 = 28 rows, which
    wears the form, so both publish `variants {"e11.9": 28}`, nothing held
    back and 28 rows in the form. The census counts those same cells
    (P4-D275.1): 28 lower-case cells clear the line of eleven, the 181
    ordinary cells clear it too, the lower-case key's room of 26,000
    clears `n_distinct` 5 plus the floor, and `n_distinct` 5 equals
    `n_distinct_folded` 5, so C6-31d names both keys. The two documents
    are the same document, so the twins are the same twin, and each
    meets its census.
    """
    large, large_described, large_folder = _column(LOWER, 5, 3)
    small, small_described, small_folder = _column(LOWER, 3, 5)

    assert large == small
    assert _entry(large)["variants"] == {LOWER: 20 + 5 + 3}
    assert _entry(large)["variants_withheld"] == {}
    assert _entry(large)["shape_form_cells"] == 20 + 5 + 3
    assert large["columns"][0]["n_distinct"] == 5
    assert large["columns"][0]["shape_forms"] == {
        LOWER_FORM: 28, FORM: ORDINARY_CELLS
    }

    large_twin = generation.generate(large_described, SEED)
    small_twin = generation.generate(small_described, SEED)
    assert list(large_twin.columns[0]) == list(small_twin.columns[0])

    held = _census_verdicts(small_described, small_twin, small_folder)
    also = _census_verdicts(large_described, large_twin, large_folder)
    wanted = [
        (f"forms.published.{LOWER_FORM}", "HELD", "28", "28"),
        (f"forms.published.{FORM}", "HELD", "181", "181"),
    ]
    for checks in (held, also):
        assert [
            (check.subcheck, check.verdict, check.published, check.achieved)
            for check in checks
        ] == wanted


def test_the_table_and_its_twin_both_meet_the_census_the_levels_speak_of(
) -> None:
    """THE DEFECT THE MERGE EXPOSED (plan P4-D275.1), from its reproduction.

    P4-D275 respelled the level entry and left the column census counting
    the raw cells: at the residual's own counts the level said 28 rows of
    `E11.9` in the form and the census said 204, the twin wrote the 28
    and held 209, and `synthtwin validate` MISSED the twin while the
    table passed. Repairing the producer alone turns it the other way --
    the table's own raw recount then finds 204 against a published 209 --
    so the checker's recount respells the file's cells by the same rule.

    Both halves are pinned: the census is 181 ordinary cells plus the 28
    of the level, all capitals, so one key of 209; the twin's own report
    names nothing; and the table and the twin both meet it.
    """
    document, described, folder = _column(UPPER, 3, 5)
    assert document["columns"][0]["shape_forms"] == {FORM: ORDINARY_CELLS + 28}
    assert _entry(document)["shape_form_cells"] == 28
    twin = generation.generate(described, SEED)
    assert _form_deviations(twin) == []
    assert _twin_census(twin) == {FORM: ORDINARY_CELLS + 28}
    on_twin = _census_verdicts(described, twin, folder)
    table = validation.measure(described, f"{folder / 'codes.csv'}")
    on_table = [
        check for check in table.checks
        if check.fact == "label.shape_forms" and check.column == "code"
    ]
    for checks in (on_twin, on_table):
        assert [
            (check.subcheck, check.verdict, check.published, check.achieved)
            for check in checks
        ] == [(f"forms.published.{FORM}", "HELD", "209", "209")]


def test_the_census_is_met_where_the_larger_group_wore_the_form() -> None:
    """THE DIRECTION THE RESIDUAL NAMED, at its own counts.

    It read `MISSED 206 -> 204`: the label's own spelling went to the
    largest held-back group and was already published, so that group
    fell through to a trailing space and lost the form, while the
    smaller group took the one case flip. The level publishes 25 of
    its 28 rows in the form, the walk gives the five-row group the
    form-keeping spelling because five is the debt, and the census is
    met exactly.

    RE-ARMED ON THE DESCRIPTION THE RESIDUAL MEASURED (see the module
    docstring): the source itself now publishes 28 under ruling 6, so
    the walk is reached through `_as_the_residual_measured`, and the
    census is counted off the twin's cells.
    """
    document, _described, _folder = _column(LOWER, 5, 3)
    assert _entry(document)["shape_form_cells"] == 20 + 5 + 3
    measured, described, _folder = _as_the_residual_measured(LOWER, 5, 3)
    assert _entry(measured)["shape_form_cells"] == 25
    twin = generation.generate(described, SEED)
    cells = list(twin.columns[0])
    assert _twin_census(twin) == {FORM: 206}
    assert cells.count(UPPER) == 5
    assert _form_deviations(twin) == []


def test_the_census_is_met_where_the_smaller_group_wore_the_form() -> None:
    """THE DIRECTION THE RESIDUAL DID NOT NAME, at its own counts.

    It read `MISSED 204 -> 206`: with the other case published the
    label's own spelling was free and was offered to the LARGEST
    held-back group, so the twin wrote five cells in the form where
    three of the source's wore it. The level publishes 23 now, the debt
    is three, and the spelling goes to the three-row group instead --
    which is the half of the repair a rule reading only group sizes
    cannot reach.

    RE-ARMED ON THE DESCRIPTION THE RESIDUAL MEASURED, for the reason
    the larger group's test gives.
    """
    document, _described, _folder = _column(UPPER, 3, 5)
    assert _entry(document)["shape_form_cells"] == 20 + 3 + 5
    measured, described, _folder = _as_the_residual_measured(UPPER, 3, 5)
    assert _entry(measured)["shape_form_cells"] == 23
    twin = generation.generate(described, SEED)
    cells = list(twin.columns[0])
    assert _twin_census(twin) == {FORM: 204}
    assert cells.count(LOWER) == 3
    assert _form_deviations(twin) == []


def test_the_twins_own_report_names_neither_direction_any_more() -> None:
    """The deviation the repair removes, on both columns.

    Before A-P4-47 the twin's own report carried a `shape_forms`
    deviation on each of these two columns -- 206 against 204 on one and
    204 against 206 on the other. Both are gone, and the per-level fact
    beside them raises none either, which is the check that says the
    repair did not simply move the miss onto the new key.
    """
    for published_spelling, form_rows, plain_rows in (
        (LOWER, 5, 3),
        (UPPER, 3, 5),
    ):
        _document, described, _folder = _column(
            published_spelling, form_rows, plain_rows
        )
        twin = generation.generate(described, SEED)
        named = [
            one for one in twin.deviations
            if one.column == "code"
            and one.fact in ("shape_forms", "levels -> shape_form_cells")
        ]
        assert named == [], (published_spelling, named)


def test_every_level_of_the_column_meets_its_own_form_count() -> None:
    """The new fact is CHECKED per level, not only in the column's total.

    A census met in total while two levels are wrong in opposite
    directions is exactly the failure the column-wide number could not
    see, so the verdict is asked level by level and every one of the
    five is named.

    `e11.9` counts 28 and not 25 since ruling 6 reached a label's
    spellings (plan P4-D275): its five `E11.9` rows and three rows with
    trailing spaces are below the floor of eleven, so they are counted
    into its commonest spelling, `e11.9` -- 20 + 5 + 3 rows, every one
    wearing the form.
    """
    document, described, folder = _column(LOWER, 5, 3)
    twin = generation.generate(described, SEED)
    checks = _verdicts(described, twin, folder, "label.shape_form_cells")
    seen = {check.subcheck: (check.verdict, check.published, check.achieved)
            for check in checks}
    assert seen == {
        "levels.d40.4.shape_form_cells": ("HELD", "61", "61"),
        "levels.a10.1.shape_form_cells": ("HELD", "40", "40"),
        "levels.b20.2.shape_form_cells": ("HELD", "40", "40"),
        "levels.c30.3.shape_form_cells": ("HELD", "40", "40"),
        "levels.e11.9.shape_form_cells": ("HELD", "28", "28"),
    }
    for level in document["columns"][0]["levels"]:
        assert "shape_form_cells" in level, level["label"]


def test_the_labels_own_spelling_is_not_spent_where_no_group_keeps_the_form(
) -> None:
    """The overshoot repair, pinned at the branch that makes it.

    `_spare_variant_group` used to hand the label's own spelling to the
    largest held-back group whatever the level owed. Where the level
    owes NO form-bearing cell beyond its published spellings, spending
    it there writes one more cell in the form than any source cell
    wore, which is the overshoot half of R-P4-34. The spelling is not
    spent at all now, so the label's own text appears in no twin cell.

    RE-ARMED ON THE DESCRIPTION THE RESIDUAL MEASURED: the source now
    publishes no held-back spelling at all (ruling 6, plan P4-D275), so
    there would be no group to overshoot on.
    """
    document, _described, folder = _as_the_residual_measured(UPPER, 3, 5)
    edited = copy.deepcopy(document)
    for level in edited["columns"][0]["levels"]:
        if level["label"] == LOWER:
            # Every one of this level's form-bearing cells is a
            # published spelling: nothing is owed to a held-back group.
            level["shape_form_cells"] = 20
    # The column census moves with it, or SF3 and the recount would be
    # arguing about a change this case is not making.
    edited["columns"][0]["shape_forms"] = {FORM: 201}
    twin = generation.generate(_reloaded(edited, folder, "edited.json"), SEED)
    cells = list(twin.columns[0])
    assert LOWER not in cells
    assert cells.count(UPPER) == 20
    for cell in cells:
        if parsing.folded(cell) == LOWER:
            assert parsing.shape_form(cell) == "" or cell == UPPER, cell


def test_the_walk_reaches_a_debt_the_largest_first_rule_cannot(
) -> None:
    """G8.1a's second pass, on the smallest case that needs it.

    Taking the largest group that fits, over and over, is right on
    nearly every level and wrong on some: a debt of 6 against groups of
    4, 3 and 3 takes the 4 and cannot spend the 2 it has left, while 3
    and 3 pay it exactly. The reachability walk decides it, and this is
    the case that separates the two.
    """
    entry = contract.LevelEntry(
        label="a-1",
        count=10,
        variants={},
        variants_withheld={"3": 2, "4": 1},
        shape_form_cells=6,
    )
    keeping = generation._form_keeping_groups(entry, 0)
    assert keeping == {"3": 2}
    total = 0
    for key in keeping:
        total = total + int(key) * keeping[key]
    assert total == 6

    # ...and the plain walk on its own really does fall short here, so
    # the case is not vacuously proving the second pass exists.
    assert generation._debt_reached(entry, ["4", "3"], 6) == {"3": 2}
    assert generation._debt_reached(entry, ["4", "3"], 5) is None


def test_a_debt_the_spelling_supply_cannot_reach_is_named() -> None:
    """The honest limit, in the twin's own report.

    `e11.9` has ONE letter, so it has ONE case flip, and here that flip
    is the only form-keeping spelling left -- the label's own is already
    published as a variant. A description asking BOTH held-back groups
    to keep the form is asking for a spelling that does not exist. No
    producer writes such a description -- a source cannot have three
    form-bearing spellings of a one-letter label -- and W8 cannot see
    it, because the count is inside its two bounds. The twin covers
    what it can and the report NAMES the rest, which is what this
    package does with every bounded search.

    THE ACHIEVED NUMBER IS PINNED AND NOT ONLY THE MISS, so the
    shortfall cannot WORSEN behind a passing test. The one flip goes to
    the group the walk reaches first -- ascending key order, so the
    three-row one -- and the twin holds 23 of the 28 asked for.

    RE-ARMED ON THE DESCRIPTION THE RESIDUAL MEASURED: the source now
    publishes all 28 rows under its one named spelling (ruling 6, plan
    P4-D275), which owes the walk nothing.
    """
    document, _described, folder = _as_the_residual_measured(LOWER, 5, 3)
    edited = copy.deepcopy(document)
    for level in edited["columns"][0]["levels"]:
        if level["label"] == LOWER:
            level["shape_form_cells"] = 28
    edited["columns"][0]["shape_forms"] = {FORM: 209}
    twin = generation.generate(_reloaded(edited, folder, "asked.json"), SEED)
    named = [
        one for one in twin.deviations
        if one.column == "code" and one.fact == "levels -> shape_form_cells"
    ]
    assert len(named) == 1, named
    assert named[0].published == (
        "28 row(s) of one published label written in that label's own shape"
    )
    assert named[0].achieved == "23"


def test_the_loader_refuses_a_level_count_below_its_own_named_spellings(
) -> None:
    """W8's lower bound, and it is a fact of the entry alone.

    The named spellings that wear the form are already on the page at
    their counts, so a number below them describes a level whose own
    published spellings contradict it.
    """
    document, _described, folder = _column(LOWER, 5, 3)
    edited = copy.deepcopy(document)
    for level in edited["columns"][0]["levels"]:
        if level["label"] == LOWER:
            level["shape_form_cells"] = 19
    try:
        _reloaded(edited, folder, "low.json")
    except errors.ProfileError as refused:
        assert "W8" in f"{refused}", f"{refused}"
        return
    raise AssertionError("the loader accepted a count below its own spellings")


def test_the_loader_refuses_a_level_count_above_what_could_wear_the_form(
) -> None:
    """W8's upper bound. Only the held-back rows can join the named ones.

    A cell of a named spelling that has no form cannot acquire one, so
    the ceiling is the named form-bearing rows plus every row the floor
    held back -- and NOT the level's own count, which would admit a
    number the twin can never write.
    """
    document, _described, folder = _column(LOWER, 5, 3)
    edited = copy.deepcopy(document)
    for level in edited["columns"][0]["levels"]:
        if level["label"] == LOWER:
            level["shape_form_cells"] = 29
    try:
        _reloaded(edited, folder, "high.json")
    except errors.ProfileError as refused:
        assert "W8" in f"{refused}", f"{refused}"
        return
    raise AssertionError("the loader accepted a count above the level's cells")


def test_the_loader_refuses_a_form_count_on_a_label_with_no_form() -> None:
    """W8's third clause, on a label of letters alone.

    `north` has no written form -- letters are one kind, and a form
    carries two -- so no spelling of it can have one. A description
    saying otherwise describes a column no table can hold, and this is
    the clause that says so rather than leaving the generator to write
    cells nothing can wear.
    """
    folder = pathlib.Path(tempfile.mkdtemp())
    values = (
        ["north" for _row in range(20)]
        + ["NORTH" for _row in range(5)]
        + ["south" for _row in range(20)]
    )
    table = fixtures.write(
        folder,
        "regions.csv",
        fixtures.rows_to_csv(
            ["code", "other"], [[value, "x"] for value in values]
        ),
    )
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(small_cell_floor=SMALL_CELL_FLOOR),
        [],
    )
    for level in document["columns"][0]["levels"]:
        assert level["shape_form_cells"] == 0, level["label"]
    edited = copy.deepcopy(document)
    edited["columns"][0]["levels"][0]["shape_form_cells"] = 1
    try:
        _reloaded(edited, folder, "formless.json")
    except errors.ProfileError as refused:
        assert "W8" in f"{refused}", f"{refused}"
        return
    raise AssertionError("the loader accepted a form count on a formless label")


def test_the_key_is_written_by_every_label_role() -> None:
    """All four label roles publish it, because all four hold levels back.

    `shape_forms` beside it stands on all four for exactly this reason
    (contract 6.3), and a key carried by three of them would be a key a
    consumer has to learn which roles have.
    """
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "roles.csv", fixtures.every_role_table()
    )
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(small_cell_floor=SMALL_CELL_FLOOR),
        [],
    )
    seen: "dict[str, int]" = {}
    for column in document["columns"]:
        if "levels" not in column:
            continue
        seen[column["role"]] = 1
        for level in column["levels"]:
            assert "shape_form_cells" in level, (column["name"], level["label"])
            assert isinstance(level["shape_form_cells"], int)
    for role in ("constant", "binary", "categorical", "long_tail_labels"):
        assert role in seen, (role, sorted(seen))


def test_the_key_survives_the_canonical_round_trip() -> None:
    """It is written, read back and written again unchanged.

    A key the producer emits and the canonical serializer drops is a key
    the loader would refuse on the second pass, which is the shape
    section 10.4 exists to catch.
    """
    document, _described, folder = _column(LOWER, 5, 3)
    written = fixtures.write_profile(folder, "round.json", document)
    again = json.loads(pathlib.Path(f"{written}").read_text(encoding="utf-8"))
    for first, second in zip(
        document["columns"][0]["levels"], again["columns"][0]["levels"]
    ):
        assert first["shape_form_cells"] == second["shape_form_cells"]


def test_every_form_bearing_spelling_of_a_level_wears_its_labels_form(
) -> None:
    """WHY THE PER-LEVEL CENSUS IS ONE NUMBER AND NOT A MAP.

    A spelling belongs to a level when trimming and case folding it
    gives the label. A spelling that HAS a form holds only letters,
    digits and marks -- no space, so trimming changes nothing -- and
    case folding an ASCII letter leaves a letter, so the form is
    untouched. Every form-bearing spelling of a level therefore wears
    exactly `shape_form(label)`, and a level's census can name at most
    that one form.

    It is asserted here because it is the fact the whole closure rests
    on, and nothing else in the suite says it.
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


def test_the_producer_counts_the_same_cells_the_level_holds() -> None:
    """The producer's own rule, measured against a built column.

    `taxonomy.shape_form_cells` is handed one level's spellings and
    counts the rows whose spelling has a form. This walks a column of
    known shape and checks the published number against a count taken
    the other way -- off the source rows themselves -- so the key is
    pinned to the cells and not to the function that writes it.

    The rows are counted as the description speaks of them, which since
    ruling 6 reached a label's spellings (plan P4-D275) is with every
    spelling below the floor counted into the level's commonest.
    """
    document, _described, _folder = _column(LOWER, 5, 3)
    wrote = {
        "a10.1": 40, "b20.2": 40, "c30.3": 40, "d40.4": 61,
        # 20 rows of `e11.9` wear the form; the 5 of `E11.9` and the 3
        # spelled with trailing spaces are below the floor of eleven, so
        # they are counted into `e11.9` and wear it too.
        "e11.9": 20 + 5 + 3,
    }
    published = {
        level["label"]: level["shape_form_cells"]
        for level in document["columns"][0]["levels"]
    }
    assert published == wrote
    # ...and the function itself still counts whatever spellings it is
    # handed: over the raw ones, the three spaced rows wear no form.
    assert taxonomy.shape_form_cells(
        {LOWER: 20, UPPER: 5, SPACED: 3}
    ) == 25
    assert taxonomy.shape_form_cells({"north": 13, "NORTH": 2}) == 0

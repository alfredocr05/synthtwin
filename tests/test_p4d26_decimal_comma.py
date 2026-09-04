"""`--decimal-comma`: the fourth declaration, end to end (plan P4-D26).

THE DEFECT IT CLOSES, measured before it existed. A person whose file
writes decimals with a comma -- most of Europe -- could not get a
correct description out of this tool, and got one of two WRONG ones
with no way to tell which:

- `1,5` reads as no number at all, so a column of quantities is
  described as free text and every number in it is lost;
- `1,234` reads as one thousand two hundred and thirty-four, so the
  description is confidently and silently off by a factor of a
  thousand.

Residual R-P4-31 named the answer and named the reason it had not been
built: the reading is per COLUMN and not per table, because a comma
inside an address or a note is not a decimal point. So this takes
column names, exactly as the three declarations beside it do.

THE FOUR HALVES, and the last three are the ones a first attempt
forgets. The profiler must READ the named columns with a comma; the
description must RECORD the declaration; the twin must WRITE those
columns back with a comma, or a person gets cells their own tools read
as thousands separators -- the very defect this prevents, one step
later; and the validator must RE-DESCRIBE a checked file under the
declaration, or a twin whose every cell is exactly right is reported
as missing its own facts. Each half has tests here and each was
watched to fail without its code.
"""

import pathlib
import random
import tempfile

import fixtures
import pytest
from synthtwin import (
    contract,
    errors,
    rendering,
    generation,
    parsing,
    profile,
    reading,
    taxonomy,
    validation,
)


def _described(
    values: "list[str]",
    commas: "list[str] | None" = None,
    name: str = "weight",
) -> "tuple[dict, contract.Profile, pathlib.Path, pathlib.Path]":
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "t.csv", fixtures.single_column_table(name, values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(),
        [],
        [],
        [],
        commas or [],
    )
    written = fixtures.write_profile(folder, "t.json", document)
    return document, contract.load_profile(f"{written}"), folder, table


def _quantities(rows: int = 200) -> "list[str]":
    """A column of quantities written the European way."""
    generator = random.Random(1)
    return [
        f"{generator.randint(1, 300)},{generator.randint(0, 99):02d}"
        for _each in range(rows)
    ]


# -- the swap itself ---------------------------------------------------


@pytest.mark.parametrize(
    "written, means",
    [
        ("1,5", 1.5),
        ("1,234", 1.234),
        ("1.234,56", 1234.56),
        ("-0,75", -0.75),
        ("1.000.000,5", 1000000.5),
        ("12", 12.0),
    ],
)
def test_the_reading_drops_the_points_and_swaps_the_commas(
    written: str, means: float
) -> None:
    """The point is a THOUSANDS separator here and is dropped, not kept.

    `1.234,56` is one thousand two hundred and thirty-four and
    fifty-six hundredths. A reading that only swapped the comma would
    make it `1.234.56`, which is not a number at all.
    """
    swapped = parsing.written_with_a_decimal_comma(written)
    assert parsing.parse_number(swapped) == means


# -- half one: the profiler reads it ----------------------------------


def test_an_undeclared_column_of_commas_is_read_as_it_always_was() -> None:
    """NO HEURISTIC DECIDES THIS. A column nobody named keeps today's
    reading, whatever its commas look like -- which is the whole of
    what P4-D26 forbids guessing about.
    """
    document, _loaded, _folder, _table = _described(_quantities())
    assert document["columns"][0]["role"] == "free_text", (
        "an undeclared column must not start reading as numbers merely "
        "because this feature exists"
    )


def test_a_declared_column_is_read_as_quantities() -> None:
    document, _loaded, _folder, _table = _described(
        _quantities(), ["weight"]
    )
    column = document["columns"][0]
    assert column["role"] == "continuous"
    assert column["percentiles"]["min"] == 2.89
    assert column["percentiles"]["max"] == 300.23


def test_the_declaration_reaches_only_the_columns_it_names() -> None:
    """A comma inside a note is not a decimal point.

    This is the reason R-P4-31 gave for the declaration being per
    column, so it is pinned rather than trusted: a second column full
    of commas, not named, must be untouched.
    """
    folder = pathlib.Path(tempfile.mkdtemp())
    weights = _quantities(60)
    # An ADDRESS, which is the example R-P4-31 itself gives for a comma
    # that is not a decimal point.
    towns = ("Ames", "Cedar Falls", "Dubuque", "Iowa City", "Waterloo")
    notes = [
        f"{100 + row} Main Street, {towns[row % 5]}, Iowa"
        for row in range(60)
    ]
    table = fixtures.write(
        folder,
        "t.csv",
        fixtures.rows_to_csv(
            ["weight", "note"],
            [[weights[row], notes[row]] for row in range(60)],
        ),
    )
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(),
        [],
        [],
        [],
        ["weight"],
    )
    assert document["columns"][0]["role"] == "continuous"
    assert document["columns"][1]["role"] == "free_text", (
        "the note column was rewritten by a declaration that never "
        "named it"
    )


def test_the_style_census_is_taken_on_the_number_not_the_characters(
) -> None:
    """THE DEFECT A FIRST BUILD OF THIS SHIPPED WITH.

    The reading was swapped and the CENSUSES were not, so `1,5` carried
    no point, counted as the `plain` form, and the column published
    `plain` for every cell beside `integer_valued: false`. The twin
    then wrote `222` for a column running from 2.89 to 300.23 -- the
    fraction gone altogether, which is a worse failure than the comma
    confusion this feature exists to prevent.

    Goes red if any numeric-spelling census reads `cell.text` instead
    of `cell.numeric_text`.
    """
    document, _loaded, _folder, _table = _described(
        _quantities(), ["weight"]
    )
    column = document["columns"][0]
    assert column["numeric_styles"] == {"decimal": 200}, (
        "the census counted the file's characters rather than how the "
        f"number is written: {column['numeric_styles']}"
    )
    assert column["integer_valued"] is False


# -- half two: the description records it ------------------------------


def test_the_declaration_is_recorded_in_the_description() -> None:
    """Two readers downstream need it and neither can work it out."""
    document, loaded, _folder, _table = _described(
        _quantities(), ["weight"]
    )
    assert document["settings"]["forced_decimal_commas"] == ["weight"]
    assert loaded.settings.forced_decimal_commas == ("weight",)


def test_an_undeclared_run_records_an_empty_declaration() -> None:
    document, loaded, _folder, _table = _described(_quantities())
    assert document["settings"]["forced_decimal_commas"] == []
    assert loaded.settings.forced_decimal_commas == ()


# -- half three: the twin writes it back -------------------------------


def test_the_twin_writes_the_column_back_with_commas() -> None:
    """THE HALF THE DECISION SAYS IS EASY TO FORGET.

    A column declared this way and reproduced with points hands a
    person cells their own tools read as thousands separators.

    Goes red if `_spelled_with_a_decimal_comma` is removed from the
    generation loop.
    """
    _document, loaded, _folder, _table = _described(
        _quantities(), ["weight"]
    )
    twin = generation.generate(loaded, 5)
    cells = [cell for cell in twin.columns[0] if cell]
    assert len(cells) == 200
    assert all("," in cell for cell in cells), (
        "a declared column came back spelled with points"
    )
    assert not any("." in cell for cell in cells), (
        "a twin cell carries both marks, so a reader cannot tell which "
        "is the decimal point"
    )
    # And the VALUES are the published ones, read back the same way.
    numbers = [
        parsing.parse_number(parsing.written_with_a_decimal_comma(cell))
        for cell in cells
    ]
    assert min(numbers) == 2.89
    assert max(numbers) == 300.23


def test_an_undeclared_twin_is_not_touched() -> None:
    """The vacuity guard on the swap: it must reach declared columns
    only, or every numeric twin in the product changes shape.
    """
    values = [f"{row}.5" for row in range(1, 61)]
    _document, loaded, _folder, _table = _described(values)
    twin = generation.generate(loaded, 5)
    cells = [cell for cell in twin.columns[0] if cell]
    assert any("." in cell for cell in cells)
    assert not any("," in cell for cell in cells)


# -- half four: the validator re-describes under it --------------------


def test_the_twin_of_a_declared_column_misses_nothing() -> None:
    """The product's headline claim, on this feature.

    Two paths inside the validator measure a file -- one re-describes
    it with the profiler's producer, the other recounts cells in
    helpers of its own -- and BOTH must be given the declaration.
    Giving it to only the first left `221,39` reading as a number to
    one and as free text to the other, and a twin whose every cell was
    exactly right came back with its style census MISSED.

    Goes red if `_cells_read_as_declared` or `_declared_commas_here` is
    removed.
    """
    _document, loaded, folder, _table = _described(
        _quantities(), ["weight"]
    )
    twin = generation.generate(loaded, 5)
    written = fixtures.write(
        folder,
        "twin.csv",
        fixtures.single_column_table("weight", list(twin.columns[0])),
    )
    outcome = validation.measure(loaded, f"{written}")
    missed = [
        check.fact for check in outcome.checks if check.verdict == "MISSED"
    ]
    assert not missed, f"the twin was told it missed: {missed}"


def test_the_real_file_meets_its_own_description() -> None:
    """The strongest form: the file that was described, checked.

    Nothing about it differs from what was published, because it IS
    what was published.
    """
    _document, loaded, _folder, table = _described(
        _quantities(), ["weight"]
    )
    outcome = validation.measure(loaded, f"{table}")
    missed = [
        check.fact for check in outcome.checks if check.verdict == "MISSED"
    ]
    assert not missed, f"the source file was told it missed: {missed}"


def test_a_file_that_really_differs_is_still_caught() -> None:
    """The vacuity guard on the whole feature.

    Reading a checked file under the declaration could have been
    widened into reading every file as sound. A file whose numbers are
    genuinely other numbers must still come back MISSED.
    """
    _document, loaded, folder, _table = _described(
        _quantities(), ["weight"]
    )
    other = fixtures.write(
        folder,
        "other.csv",
        fixtures.single_column_table(
            "weight", [f"{row},50" for row in range(400, 600)]
        ),
    )
    outcome = validation.measure(loaded, f"{other}")
    assert [
        check for check in outcome.checks if check.verdict == "MISSED"
    ], "a file of entirely different numbers was accepted"


# -- adversarial review round P4-G3-R2 --------------------------------


def test_the_twin_is_measured_in_the_spelling_it_was_described_in(
) -> None:
    """THE REPORT WENT BLIND WHEN THE SWAP CAME TOO EARLY (F1).

    The twin is written with commas and MEASURED with points, because
    the description was made with points. Swapping before the measuring
    made every recount in the generation loop read `221,39` with the
    ordinary parser and find no number in it: the report said the twin
    held 0 numeric cells against a published 200, 200 not-numeric
    against a published 0, and named 2 approximated facts where the
    same column undeclared names 15. Every one of those was false.

    Goes red if `_spelled_with_a_decimal_comma` moves back above the
    note and approximation chain.
    """
    _document, loaded, _folder, _table = _described(
        _quantities(), ["weight"]
    )
    twin = generation.generate(loaded, 5)
    assert not twin.deviations, (
        "the twin's own report says it gave something up, and it gave "
        f"up nothing: {[(d.fact, d.achieved) for d in twin.deviations]}"
    )
    assert len(twin.approximations) == 15, (
        f"{len(twin.approximations)} approximated facts were named; a "
        "column of the same numbers written with points names 15, and "
        "the declaration must not change what the report can see"
    )
    cells = [cell for cell in twin.columns[0] if cell]
    assert all("," in cell for cell in cells), (
        "the cells that leave must still carry the comma"
    )


def test_the_same_numbers_report_the_same_way_either_spelling() -> None:
    """The sharpest form of F1: one set of numbers, two spellings.

    A column of `1,5` declared and a column of `1.5` undeclared are the
    same quantities described the same way, so their twins must give up
    the same things. Any difference is the declaration leaking into a
    measurement.
    """
    with_commas = _quantities()
    with_points = [cell.replace(",", ".") for cell in with_commas]
    _one, declared, _f1, _t1 = _described(with_commas, ["weight"])
    _two, plain, _f2, _t2 = _described(with_points)
    first = generation.generate(declared, 5)
    second = generation.generate(plain, 5)
    assert len(first.approximations) == len(second.approximations)
    assert len(first.deviations) == len(second.deviations)


def test_a_declared_word_for_no_value_is_still_a_hole() -> None:
    """A HOLE IS DECIDED ON THE FILE'S OWN TEXT (F5).

    `--missing-value 7,5` names a word this description reads as "no
    value". Translating it first turns it into `7.5`, which every
    census downstream counts as a number the column never held -- and
    the SOURCE FILE came back missing its own style obligation, with
    200 numbers recounted in a column published as holding 180.

    Goes red if `_cells_read_as_declared` stops asking which cells are
    holes before it translates.
    """
    # A WORD, because that is what the refusal of R-P4-54 leaves
    # available beside `--decimal-comma`: a "no value" marker whose
    # meaning does not depend on which grammar reads it. The point of
    # this test is unchanged -- a hole is decided on the file's own
    # text, before the numbers are translated.
    generator = random.Random(4)
    values = [
        f"{generator.randint(1, 300)},{generator.randint(0, 99):02d}"
        for _each in range(180)
    ] + ["absent"] * 20
    generator.shuffle(values)
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "t.csv", fixtures.single_column_table("weight", values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(declared_missing_values=("absent",)),
        [],
        [],
        [],
        ["weight"],
    )
    assert document["columns"][0]["n_present"] == 180
    assert document["columns"][0]["n_missing"] == 20
    written = fixtures.write_profile(folder, "t.json", document)
    loaded = contract.load_profile(f"{written}")
    missed = [
        check.fact
        for check in validation.measure(loaded, f"{table}").checks
        if check.verdict == "MISSED"
    ]
    assert not missed, (
        f"the file that was described was told it missed: {missed}"
    )


def test_saying_the_same_declaration_twice_is_not_an_error() -> None:
    """THE TOOL WROTE A DESCRIPTION IT COULD NOT READ (F7).

    `--decimal-comma weight --decimal-comma weight` -- a repeated line,
    a pasted command -- put the name in the settings array twice. The
    contract requires those names to be distinct, so the loader then
    REFUSED the file, telling the person to make the description again
    by running the same command, which reproduces the same file.

    This predates the fourth declaration and reached all four, so all
    four are checked here.
    """
    for spot, key in (
        (2, "forced_identifiers"),
        (3, "forced_codes"),
        (4, "forced_measurements"),
        (5, "forced_decimal_commas"),
    ):
        folder = pathlib.Path(tempfile.mkdtemp())
        table = fixtures.write(
            folder,
            "t.csv",
            fixtures.single_column_table("weight", _quantities(60)),
        )
        declarations: "list[list[str]]" = [[], [], [], []]
        declarations[spot - 2] = ["weight", "weight"]
        document = profile.build_document(
            reading.read_table(f"{table}"),
            taxonomy.Settings(),
            declarations[0],
            declarations[1],
            declarations[2],
            declarations[3],
        )
        assert document["settings"][key] == ["weight"], (
            f"{key} carries the name twice, and the loader refuses that"
        )
        # And the loader really does read back what was just written.
        contract.load_profile(
            f"{fixtures.write_profile(folder, 't.json', document)}"
        )


def test_a_declaration_that_cannot_be_honoured_is_said_out_loud() -> None:
    """R-P4-52 FAILS LOUDLY (F4).

    Which columns the declaration reaches depends on the ROLE the
    values take, which is not known until the table has been read. So
    a declaration that lands on a role it cannot help is named on the
    screen rather than quietly not applied -- principle 5 forbids a
    silent miscast, and a declaration accepted and then ignored is one.
    """
    said = errors.the_comma_declaration_did_not_reach("price", "free_text")
    assert "price" in said
    assert "free_text" in said
    assert "NOT read" in said
    assert "decimal point" in said


def test_the_role_names_and_the_type_test_agree_column_by_column() -> None:
    """The two questions are different, and the narrower implies the
    wider.

    `DECIMAL_COMMA_HONOURED_ROLES` says where the declaration changed
    the DESCRIPTION; `a_decimal_comma_reaches` says where the generator
    must SPELL the numbers itself. They are not the same set -- a
    `constant` column of `1,5` is read with the comma and publishes
    ones and a halves, while its twin writes the published spelling
    straight out and has nothing to swap (review item P4-G3-R5-F2).

    What must hold is that the narrower is inside the wider: a column
    whose numbers the generator spells is a column whose description
    was made with the declaration. A first version asserted a literal
    tuple and pinned nothing (P4-G3-R3-F4): removing
    `UnrepresentableFacts` from the predicate left it green while
    generation silently stopped applying the declaration.

    Goes red if either side is changed without the other.
    """
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "every.csv", fixtures.every_role_table()
    )
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(small_cell_floor=11),
        ["record_code"],
    )
    loaded = contract.load_profile(
        f"{fixtures.write_profile(folder, 'every.json', document)}"
    )
    seen: "set[str]" = set()
    for column in loaded.columns:
        seen.add(column.role)
        honoured = column.role in contract.DECIMAL_COMMA_HONOURED_ROLES
        spelled = contract.a_decimal_comma_reaches(column)
        assert not spelled or honoured, (
            f"the column '{column.name}' is role {column.role}: the "
            "generator would spell its numbers with a comma while the "
            "command line would tell the person the declaration was "
            "not honoured there"
        )
    assert len(seen) >= 8, (
        f"only {len(seen)} roles were walked, so this test no longer "
        "covers enough of the map to catch a drift"
    )


def test_the_unrepresentable_role_is_one_the_declaration_reaches() -> None:
    """Named on its own because it was the one silently left out.

    Its cells are numbers too large or too small for this format to
    hold -- but numbers, spelled by the same rules -- so a declared
    column landing there would otherwise be read with the comma and
    written back with a point.
    """
    assert (
        "numeric_unrepresentable" in contract.DECIMAL_COMMA_HONOURED_ROLES
    )
    values = [f"1,{row}e-400" for row in range(100, 260)]
    document, loaded, _folder, _table = _described(values, ["weight"])
    assert document["columns"][0]["role"] == "numeric_unrepresentable", (
        "this fixture no longer reaches the role it was built for"
    )
    assert contract.a_decimal_comma_reaches(loaded.columns[0])


# -- adversarial review round P4-G3-R4 --------------------------------


def _colliding_rows() -> "list[str]":
    """The column both witnesses below stand on.

    A HUNDRED AND EIGHTY READINGS BETWEEN 7.0 AND 7.9, twenty of them
    written `7.5`, and A TAIL OF TWENTY REACHING 11.8. The readings and
    the hole spelling are what the collision is made of; the tail is
    what keeps it reachable, and it was added on 2026-09-04 when
    residual R-P4-138 landed.

    WHY THE TAIL IS THERE, measured. Declaring `7.5` a hole takes every
    cell reading 7.5 out of the statistics, so the values they leave
    behind have a real gap at 7.5 -- and since R-P4-138 the description
    publishes the two values that gap lies between. On the narrow
    column the gap covered whole BINS, `empty_bins` named them, and
    method G6.7 moved every stratum out: the twin came back holding
    exactly the published forty-two and there was no collision left to
    report. That is the value stage working, and it is measured in
    `tests/test_p4d32_empty_bins.py`; what it took away was the
    WITNESS. The tail widens the column's reach so that one bin is
    wider than the gap, 7.5 falls in a bin that holds plenty, no
    stretch is named around it, and the collision these two tests exist
    for happens again: the twin holds fifty-eight against a published
    forty-two.
    """
    generator = random.Random(5)
    values = [f"7.{generator.randint(0, 9)}" for _each in range(180)]
    values = values + ["7.5"] * 20
    values = values + [f"{8 + one * 0.2:.1f}" for one in range(20)]
    generator.shuffle(values)
    return values


def test_the_swap_cannot_quietly_turn_a_value_into_a_hole() -> None:
    """A NUMERIC HOLE SPELLING AND A GENERATED VALUE CAN COLLIDE (F1).

    A column whose published "no value" word is `7,5` and whose values
    run from 7.0 to 7.9 generates present cells spelled `7.5`. Without
    the declaration those are two different spellings and nothing
    collides; the swap makes them one. Measured, the twin held
    FIFTY-EIGHT cells spelled `7.5` against a published forty-two --
    sixteen values became holes -- and the twin's own report,
    recounting the
    cells from BEFORE the swap, called it all correct while `synthtwin
    validate` reported eight missed obligations.

    The collision is REPORTED and not steered around, which is the
    position R-P2-13 already takes for a value that lands on a
    stand-in. What must never happen again is the SILENCE.

    Goes red if the recount moves back onto the pre-swap cells, or if
    `_recount_notes` stops naming presence.
    """
    # ON AN UNDECLARED COLUMN, because the collision is a general
    # phenomenon and the decimal-comma form of it is now unreachable:
    # R-P4-54 refuses a declared value whose number depends on the
    # grammar, and `7,5` is one. `7.5` beside ordinary decimals is the
    # same defect in a shape the tool still accepts.
    values = _colliding_rows()
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "t.csv", fixtures.single_column_table("weight", values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(declared_missing_values=("7.5",)),
        [],
    )
    published = document["columns"][0]
    assert published["missing_by_source"] == {"7.5": 42}, (
        "this fixture must publish a numeric hole spelling, or it "
        "witnesses nothing"
    )
    loaded = contract.load_profile(
        f"{fixtures.write_profile(folder, 't.json', document)}"
    )
    twin = generation.generate(loaded, 25)
    held = len([cell for cell in twin.columns[0] if cell == "7.5"])
    assert held > published["missing_by_source"]["7.5"], (
        "this fixture no longer produces the collision it was built "
        f"for: the twin holds {held} and the description publishes "
        f"{published['missing_by_source']['7.5']}"
    )
    named = {note.fact for note in twin.deviations}
    assert "n_present" in named and "n_missing" in named, (
        "the twin turned values into holes and its own report says "
        f"nothing about presence: {sorted(named)}"
    )


def test_the_twin_report_and_the_quality_report_agree_on_presence() -> None:
    """The two pages of one run, on the collision above.

    `synthtwin validate` reported this from the start; the twin's own
    report did not. Both must now.
    """
    values = _colliding_rows()
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "t.csv", fixtures.single_column_table("weight", values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(declared_missing_values=("7.5",)),
        [],
    )
    loaded = contract.load_profile(
        f"{fixtures.write_profile(folder, 't.json', document)}"
    )
    twin = generation.generate(loaded, 25)
    written = fixtures.write(
        folder, "twin.csv", rendering.twin_csv(twin)
    )
    outcome = validation.measure(loaded, f"{written}")
    said = {note.fact for note in twin.deviations}
    caught = {
        check.fact.split(".")[-1]
        for check in outcome.checks
        if check.verdict == "MISSED"
    }
    for fact in ("n_present", "n_missing"):
        assert fact in said and fact in caught, (
            f"{fact}: the twin's report says {fact in said} and the "
            f"quality report says {fact in caught}"
        )


def test_a_column_with_no_collision_reports_no_presence_trouble() -> None:
    """The vacuity guard: the new notes must stay silent otherwise.

    Presence is exact by construction on every ordinary column, so a
    note here on a column that held everything would be a false alarm
    printed on every run.
    """
    _document, loaded, _folder, _table = _described(
        _quantities(), ["weight"]
    )
    twin = generation.generate(loaded, 5)
    assert not [
        note
        for note in twin.deviations
        if note.fact in ("n_present", "n_missing")
    ]


def test_a_description_naming_one_column_two_ways_is_refused() -> None:
    """Invariant S8a, which nothing enforced (F3 of round 3).

    The contract forbade the overlap and the loader accepted it, so a
    hand-written description could name a column both a code and a
    decimal-comma column; the generator then quietly did not apply the
    comma, because a code column carries no numeric facts.

    It carries its OWN invariant code and not S8's (F6 of round 4):
    S8 says a declared name is not a column of this table, and this
    says the name IS one and has been given two readings.
    """
    _document, _loaded, folder, table = _described(
        _quantities(60), ["weight"]
    )
    import copy

    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(),
        [],
        [],
        [],
        ["weight"],
    )
    # BOTH OVERLAPS ARE REFUSED, and they are refused by different
    # rules, which is worth stating rather than papering over. The
    # `--identifier` pair is caught EARLIER by a more specific check --
    # a silenced column and a described one disagree about the column's
    # own quality state, and that check names the column. Only the
    # `--code` pair reaches S8a, because a code column is described
    # like any other. What matters is that neither is accepted.
    for other in ("forced_codes", "forced_identifiers"):
        forged = copy.deepcopy(document)
        forged["settings"][other] = ["weight"]
        written = fixtures.write_profile(folder, f"{other}.json", forged)
        with pytest.raises(errors.ProfileError) as refused:
            contract.load_profile(f"{written}")
        if other == "forced_codes":
            assert "comma" in f"{refused.value}", (
                "the code overlap must be refused by S8a, which names "
                "the comma declaration as one of the two readings"
            )

    # And the conforming document loads, so the red cases above are
    # about the overlap and not about some other refusal.
    assert contract.load_profile(
        f"{fixtures.write_profile(folder, 'ok.json', document)}"
    ).settings.forced_decimal_commas == ("weight",)


# -- adversarial review round P4-G3-R5 --------------------------------


def test_a_declaration_is_read_the_column_s_own_way_beneath_the_refusal(
) -> None:
    """BOTH HALVES OF A COMPARISON GET THE SAME GRAMMAR.

    The matching rule is `exact_number_when_it_reads_as_one_else_
    spelling`, so a declaration that reads as a number is matched BY
    NUMBER and never by spelling. Reading the CELLS with the comma and
    the DECLARATION without it made `1,234` one and
    two-hundred-and-thirty-four thousandths on one side and one
    thousand two hundred and thirty-four on the other, so every cell
    the person had called "no value" was counted as a measurement.

    THIS COMBINATION IS NOW REFUSED at `build_document` (R-P4-54), and
    that refusal is tested above. It is driven HERE at
    `taxonomy.profile_column`, which is public, sits beneath the
    refusal, and must be right on its own terms -- if the refusal were
    ever relaxed this is what would have to hold. Goes red if
    `_declarations` stops taking the column's reading.
    """
    generator = random.Random(2)
    values = [
        f"{generator.randint(1, 9)},{generator.randint(100, 999)}"
        for _each in range(180)
    ] + ["1,234"] * 20
    generator.shuffle(values)
    described = taxonomy.profile_column(
        "amount",
        1,
        values,
        len(values),
        taxonomy.Settings(declared_missing_values=("1,234",)),
        False,
        False,
        False,
        True,
    )
    assert described.n_missing >= 20, (
        "cells the person named as 'no value' were counted as "
        f"measurements: n_missing came out {described.n_missing}"
    )


def test_a_kept_value_survives_the_judgement_beneath_the_refusal(
) -> None:
    """The same, for `--keep-value`, and for the same reason.

    `--keep-value -999,0` on a declared column read the cells as the
    stand-in and the KEPT declaration under the ordinary grammar, where
    it is no number at all -- so the outlier pass carried off cells the
    person had explicitly said to keep.

    Refused at `build_document` now; driven here, beneath it.
    """
    generator = random.Random(3)
    values = [
        f"{generator.randint(10, 90)},{generator.randint(0, 9)}"
        for _each in range(160)
    ] + ["-999,0"] * 40
    generator.shuffle(values)
    described = taxonomy.profile_column(
        "amount",
        1,
        values,
        len(values),
        taxonomy.Settings(kept_values=("-999,0",)),
        False,
        False,
        False,
        True,
    )
    assert described.n_present == 200, (
        "cells the person said to KEEP were carried off as stand-ins: "
        f"n_present came out {described.n_present}"
    )
    assert "kept_as_a_number" in [
        verdict["verdict"] for verdict in described.sentinel_verdicts
    ]


def test_a_declaration_is_honoured_on_a_constant_column() -> None:
    """THE PROFILER READS BEFORE IT CHOOSES A ROLE (F2).

    Sixty cells all spelled `1,5`, declared, are sixty copies of one
    and a half -- and take the `constant` role, which is chosen BEFORE
    the numeric roles. The twin writes the published spelling `1,5`
    straight out, which is exactly right and which `synthtwin validate`
    confirmed; and the twin's OWN report read those cells with the
    ordinary parser, found no number in any of them, and said it held
    0 numeric cells against a published 60.

    Goes red if the note chain stops reading `_read_as_described`.
    """
    document, loaded, folder, _table = _described(["1,5"] * 60, ["x"], "x")
    column = document["columns"][0]
    assert column["role"] == "constant"
    assert column["n_numeric"] == 60, (
        "the profiler must read a declared column with the comma "
        "whatever role it takes"
    )
    twin = generation.generate(loaded, 3)
    assert set(twin.columns[0]) == {"1,5"}
    assert not twin.deviations, (
        "the twin's cells are exactly what the description asks for "
        f"and its own report says otherwise: "
        f"{[(d.fact, d.published, d.achieved) for d in twin.deviations]}"
    )
    written = fixtures.write(
        folder, "twin.csv", rendering.twin_csv(twin)
    )
    assert not [
        check
        for check in validation.measure(loaded, f"{written}").checks
        if check.verdict == "MISSED"
    ]


def test_the_warning_does_not_fire_where_the_reading_was_used() -> None:
    """The complement of the honoured set is what gets the warning.

    A `constant` or `binary` column of comma-written numbers HAS its
    declaration honoured, so telling its owner the numbers were "NOT
    read" with the comma is a false statement about a description whose
    profiler read exactly that way.
    """
    for role in ("binary", "constant"):
        assert role in contract.DECIMAL_COMMA_HONOURED_ROLES, (
            f"{role} is chosen before the numeric roles and the "
            "profiler reads it with the declaration, so a person must "
            "not be told otherwise"
        )
    for role in ("free_text", "categorical", "joined_numbers"):
        assert role not in contract.DECIMAL_COMMA_HONOURED_ROLES


# -- adversarial review round P4-G3-R6 --------------------------------


def test_two_declarations_that_are_one_number_are_refused() -> None:
    """A CONTRADICTION UNDER EITHER GRAMMAR IS A CONTRADICTION (F2).

    `--keep-value 1,234 --missing-value 1,2340` names one number twice
    on a declared column and two different numbers everywhere else.
    Tested under the ordinary grammar alone the pair looks innocent,
    the command is accepted, and the missing declaration then quietly
    defeats the keep declaration on the very column the person
    declared.
    """
    assert not taxonomy.contradictory_declarations(
        ("1,234",), ("1,2340",)
    ), "this pair must look innocent under the ordinary grammar alone"
    clashes = taxonomy.contradictory_declarations(
        ("1,234",), ("1,2340",), True
    )
    assert clashes, (
        "the pair is one number on a declared column and was accepted"
    )
    assert "same number" in clashes[0]

    # And an honest pair is still not refused.
    assert not taxonomy.contradictory_declarations(("NA",), ("unknown",), True)


def test_a_hole_is_not_read_as_a_number_by_the_report() -> None:
    """THE DESCRIBED-DOMAIN VIEW MUST LEAVE HOLES ALONE (F3).

    Translating a hole spelled `-9,99` gives `-999`, which reads as a
    number -- so the twin's own report counted 200 numeric cells
    against a published 180 and printed eleven false deviations after
    it, including moments and rungs computed over twenty values the
    column does not have. The twin's CELLS were right the whole time.

    Goes red if `_read_as_described` stops asking which cells are
    holes.
    """
    # A JUDGED hole spelled with a comma, which is legal beside the
    # declaration and is the shape that remains after R-P4-54's
    # refusal: the tool decided these forty outliers mean "no value",
    # and their spelling is one number under this column's reading.
    generator = random.Random(3)
    values = [
        f"{generator.randint(10, 90)},{generator.randint(0, 9)}"
        for _each in range(160)
    ] + ["-999,0"] * 40
    generator.shuffle(values)
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "t.csv", fixtures.single_column_table("amount", values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(),
        [],
        [],
        [],
        ["amount"],
    )
    assert document["columns"][0]["missing_by_source"] == {"-999,0": 40}
    assert document["columns"][0]["n_present"] == 160
    loaded = contract.load_profile(
        f"{fixtures.write_profile(folder, 't.json', document)}"
    )
    twin = generation.generate(loaded, 3)
    said = {note.fact for note in twin.deviations}
    assert "n_numeric" not in said, (
        "the report read this column's holes as numbers: "
        f"{[(n.fact, n.published, n.achieved) for n in twin.deviations]}"
    )
    assert not {"mean", "std"} & said


def test_one_judged_hole_does_not_silence_another_hole_s_collision(
) -> None:
    """THE GUARD IS PER SPELLING, NOT PER COLUMN (F4).

    A column-wide flag let one judged `-999` silence a genuine
    collision on an unconditional `7,5` in the same column: the quality
    report named it and the twin's own report did not.

    Goes red if `_unconditional_hole_excess` is replaced by a
    column-wide test again.
    """
    # ON AN UNDECLARED COLUMN, because the decimal-comma form of this
    # is unreachable after R-P4-54: an unconditional hole beside a
    # declared column can no longer be a spelling whose number depends
    # on the grammar, so it can no longer collide with a generated
    # NUMBER. The defect is not about the comma at all -- it is one
    # judged hole silencing another hole's collision -- and this is it
    # in a shape the tool accepts.
    generator = random.Random(5)
    values = [f"7.{generator.randint(0, 9)}" for _each in range(160)]
    values = values + ["7.5"] * 20 + ["-9999"] * 20
    generator.shuffle(values)
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "t.csv", fixtures.single_column_table("weight", values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(declared_missing_values=("7.5",)),
        [],
    )
    holes = document["columns"][0]["missing_by_source"]
    assert "7.5" in holes and "-9999" in holes, (
        "this fixture must publish one judged hole and one declared "
        f"one, or it witnesses nothing: {holes}"
    )
    loaded = contract.load_profile(
        f"{fixtures.write_profile(folder, 't.json', document)}"
    )
    twin = generation.generate(loaded, 5)
    written = fixtures.write(
        folder, "twin.csv", rendering.twin_csv(twin)
    )
    outcome = validation.measure(loaded, f"{written}")
    said = {note.fact for note in twin.deviations}
    caught = {
        check.fact.split(".")[-1]
        for check in outcome.checks
        if check.verdict == "MISSED"
    }
    assert ("n_present" in said) == ("n_present" in caught), (
        f"the twin's report says {'n_present' in said} and the quality "
        f"report says {'n_present' in caught}"
    )


def test_a_judged_sentinel_alone_still_raises_no_presence_note() -> None:
    """The other side of the same guard, kept from round 5.

    A stand-in the judgement made absent may not be judged absent again
    on the twin's own distribution, so the recount cannot speak for the
    re-description and the note stays silent.
    """
    generator = random.Random(5)
    values = [
        str(generator.randint(20, 90)) for _each in range(180)
    ] + ["-999"] * 20
    generator.shuffle(values)
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "t.csv", fixtures.single_column_table("v", values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(), []
    )
    loaded = contract.load_profile(
        f"{fixtures.write_profile(folder, 't.json', document)}"
    )
    twin = generation.generate(loaded, 5)
    said = {note.fact for note in twin.deviations}
    assert "n_present" not in said and "n_missing" not in said


# -- adversarial review round P4-G3-R7 --------------------------------


@pytest.mark.parametrize("option", ["kept", "missing"])
def test_a_grammar_dependent_declared_value_is_refused(option: str) -> None:
    """R-P4-54, CLOSED BY REFUSING THE PAIR (F1).

    `--keep-value` and `--missing-value` name VALUES and reach every
    column; `--decimal-comma` names COLUMNS. A spelling whose number
    depends on which grammar reads it means one thing on a declared
    column and another everywhere else, and `settings` has one place to
    record it.

    I CARRIED THIS AS A RESIDUAL ON THE ARGUMENT THAT THE CONSEQUENCE
    WAS CONSERVATIVE, AND THE ARGUMENT WAS WRONG. Declare `1,234` and
    `1234` as missing: the ordinary grammar folds them into one and the
    comma grammar keeps them apart, so the table-wide recovery looks
    complete, the column stays checkable, and the SOURCE FILE is told
    it missed presence, role and its numbers against a description
    correct about all three.
    """
    said = errors.a_declared_value_reads_two_ways(
        "1,234", f"--{option}-value"
    )
    assert "1,234" in said
    assert f"--{option}-value" in said
    assert "--decimal-comma" in said
    assert "Nothing was written" in said

    # AND THE REFUSAL ITSELF, not just its sentence (review item
    # P4-G3-R8-F3). The first version of this test called only the
    # message formatter, so deleting the check left it green while
    # `--decimal-comma amount --missing-value 1,234` was accepted
    # again -- the same non-red control shape earlier rounds rejected.
    # It is driven at the PRODUCER, which is where the refusal now
    # lives and which every path goes through.
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "t.csv", fixtures.single_column_table("amount", _quantities(60))
    )
    read = reading.read_table(f"{table}")
    settings = (
        taxonomy.Settings(kept_values=("1,234",))
        if option == "kept"
        else taxonomy.Settings(declared_missing_values=("1,234",))
    )
    with pytest.raises(ValueError) as refused:
        profile.build_document(read, settings, [], [], [], ["amount"])
    assert "decimal-comma" in f"{refused.value}"

    # The same declaration WITHOUT a declared column is accepted, so
    # this refuses the pair and not the value.
    profile.build_document(read, settings, [])

    # And an honest word is accepted beside a declared column.
    honest = (
        taxonomy.Settings(kept_values=("NA",))
        if option == "kept"
        else taxonomy.Settings(declared_missing_values=("NA",))
    )
    profile.build_document(read, honest, [], [], [], ["amount"])


def test_which_declared_values_the_refusal_reaches() -> None:
    """It must reach the ambiguous ones and no others.

    A refusal that swept up `NA` would take away the commonest true
    thing a person says, and one that missed `1,234` would not be a
    refusal at all.
    """
    for safe in ("NA", "unknown", "-999", "n/a", "", "0"):
        assert not parsing.reads_as_two_numbers(safe), safe
    for ambiguous in ("1,234", "-9.99", "-999,0", "7,5", "1.234,56"):
        assert parsing.reads_as_two_numbers(ambiguous), ambiguous


def test_a_judged_hole_of_a_declared_column_is_written_blank() -> None:
    """THE CONTRACT'S WRITE RULE, under the column's own grammar (F3).

    Forty outlier cells spelled `-999,0` on a declared column are read
    as minus nine hundred and ninety-nine and publish a verdict naming
    that number. Asked with the ORDINARY parser, `-999,0` is no number
    at all, so the spelling matched no candidate and `_absent_cells`
    reproduced `-999,0` where the rule asks for empty cells -- which
    makes a later stand-in judgement contingent on the twin's own
    distribution, the very thing the rule exists to prevent.

    Goes red if `_is_the_same_candidate` stops taking the reading.
    """
    generator = random.Random(3)
    values = [
        f"{generator.randint(10, 90)},{generator.randint(0, 9)}"
        for _each in range(160)
    ] + ["-999,0"] * 40
    generator.shuffle(values)
    document, loaded, _folder, _table = _described(
        values, ["amount"], "amount"
    )
    column = document["columns"][0]
    assert column["missing_by_source"] == {"-999,0": 40}, (
        "this fixture must publish a judged hole spelled with a comma"
    )
    twin = generation.generate(loaded, 3)
    cells = list(twin.columns[0])
    assert not [cell for cell in cells if cell == "-999,0"], (
        "a judged hole was reproduced by its spelling; the rule is that "
        "it is written empty, because the judgement may not re-fire"
    )
    assert len([cell for cell in cells if not cell]) == 40


def test_one_identity_decides_whether_a_cell_wears_a_hole() -> None:
    """THREE PLACES WERE ASKING THIS THREE WAYS (F2).

    A column publishing the hole `7,50` whose generated value 7.5 is
    written `7,5` has the two recognised as one number by a
    re-description and as two different texts by an exact guard. The
    rule is the profiler's own: the same NUMBER where the spelling
    reads as one under this column's grammar, the same folded spelling
    otherwise.
    """
    # The same number, spelled two ways, under the column's grammar.
    assert generation._wears_this_hole("7,5", "7,50", True)
    assert generation._wears_this_hole("7,50", "7,5", True)
    # And NOT the same number under the ordinary one, where neither
    # spelling reads as a number and the texts differ.
    assert not generation._wears_this_hole("7,5", "7,50", False)
    # Exact text always counts, either way.
    assert generation._wears_this_hole("7,5", "7,5", False)
    # A word is compared as a word.
    assert generation._wears_this_hole(" na ", "NA", False)
    # And two different numbers are two different numbers.
    assert not generation._wears_this_hole("7,6", "7,5", True)


def test_the_recount_uses_the_same_hole_identity_as_everything_else(
) -> None:
    """THE THIRD CALLER WAS STILL ASKING THE OLD QUESTION (F1 of round 8).

    A comment beside `_wears_this_hole` claimed three callers shared one
    rule and only two of them did. `_recounted` still read numbers
    under the ordinary grammar -- so on a declared column publishing
    the hole `-999`, a present cell written `-999,0` was counted
    PRESENT here and ABSENT by a re-description. The collision was
    detected, the recount was unchanged, and the presence lines --
    which need BOTH -- stayed silent while the quality report named the
    loss.

    `--missing-value -999` is a SAFE declaration: its number does not
    depend on the grammar, so R-P4-54's refusal leaves it available,
    and this is the shape that remains.

    Goes red if `_recounted` stops taking the column's reading.
    """
    # THE TWO SPELLINGS MUST DIFFER while the numbers agree, or the
    # test cannot tell the two identities apart: a cell whose TEXT
    # equals the published hole is matched by either rule. So the
    # column publishes the hole `-999` and the twin writes `-999,0`,
    # and the source is kept clear of that spelling.
    generator = random.Random(2)
    values: "list[str]" = []
    while len(values) < 180:
        whole = generator.randint(0, 9)
        part = generator.randint(0, 9)
        if (whole, part) == (9, 0):
            continue
        values = values + [f"-99{whole},{part}"]
    values = values + ["-999"] * 20
    generator.shuffle(values)
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "t.csv", fixtures.single_column_table("amount", values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(declared_missing_values=("-999",)),
        [],
        [],
        [],
        ["amount"],
    )
    holes = document["columns"][0]["missing_by_source"]
    assert holes == {"-999": 20}, (
        "the column must publish the hole as `-999`, so that the "
        f"twin's `-999,0` differs from it in TEXT: {holes}"
    )
    loaded = contract.load_profile(
        f"{fixtures.write_profile(folder, 't.json', document)}"
    )
    # The seed is chosen so the twin actually writes the colliding
    # spelling; the assertion below refuses the fixture if it stops.
    twin = generation.generate(loaded, 5)
    assert [cell for cell in twin.columns[0] if cell == "-999,0"], (
        "this fixture no longer produces the collision it was built "
        "for, so any agreement below is between two silences"
    )
    written = fixtures.write(
        folder, "twin.csv", rendering.twin_csv(twin)
    )
    outcome = validation.measure(loaded, f"{written}")
    said = {note.fact for note in twin.deviations}
    caught = {
        check.fact.split(".")[-1]
        for check in outcome.checks
        if check.verdict == "MISSED"
    }
    assert "n_present" in caught, "the quality report must see the loss"
    assert "n_present" in said, (
        "the quality report names the lost presence and the twin's own "
        "report does not, which is the two pages of one run "
        "disagreeing about what happened"
    )

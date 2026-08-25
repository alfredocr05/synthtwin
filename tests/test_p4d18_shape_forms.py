"""A held-back value gets a stand-in that looks like one.

Plan decision P4-D18, contract clauses C6-D18.

WHAT WAS WRONG. A column whose rare values the disclosure floor holds
back publishes NOTHING about them, so the twin wrote `group-1`,
`group-2`, `group-3` in their place. On a column of clinical codes that
stand-in is wrong every way a stand-in can be: the wrong length,
lower-case where the codes are not, and on a hyphenated scheme it
carries a hyphen OF ITS OWN -- so it passes a "looks segmented" check,
crashes a split into fixed parts, and, the word being exactly five
characters, makes a width check on the leading segment answer plausibly
and wrongly.

WHAT IS PINNED HERE:

- the census says what a cell looked like and nothing about what it
  held -- every figure becomes `9` and every letter `A`;
- a column of prose publishes NOTHING, because the floor plus a length
  limit does that work with no rule deciding which columns are codes;
- the twin's stand-ins wear the published forms, so a code column's
  twin is code-shaped throughout;
- the published levels pay their own forms first, so the counts close;
- and a stand-in still has the four properties `group-N` had for free:
  it is not a word meaning "no value", reads as neither number nor
  date, carries no comma or quote, and does not open a formula.
"""

import pathlib
import random
import re
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


def _described(
    values: "list[str]", name: str = "code"
) -> "tuple[dict, contract.Profile, pathlib.Path]":
    folder = pathlib.Path(tempfile.mkdtemp())
    rows = [[value, "x"] for value in values]
    table = fixtures.write(
        folder, "thing.csv", fixtures.rows_to_csv([name, "other"], rows)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(), []
    )
    written = fixtures.write_profile(folder, "thing.json", document)
    return document, contract.load_profile(f"{written}"), folder


def _long_tail(common: "list[str]", rare: "list[str]") -> "list[str]":
    """A column shaped like a real one: a few common codes, a long tail."""
    values: list[str] = []
    for code, count in zip(common, (62, 45, 34, 28, 22)):
        values = values + [code] * count
    for place, code in enumerate(rare):
        values = values + [code] * (1 if place % 2 else 2)
    random.Random(3).shuffle(values)
    return values


# -- the form itself --------------------------------------------------


def test_a_form_says_the_shape_and_nothing_else() -> None:
    """Every figure becomes `9`, every letter `A`, the marks stand."""
    for text, form in (
        ("E11.9", "A99.9"),
        ("S72.001A", "A99.999A"),
        ("4548-4", "9999-9"),
        ("0002-8215-01", "9999-9999-99"),
        ("120/80", "999/99"),
        ("00100", "99999"),
    ):
        assert parsing.shape_form(text) == form, text
    # ...and a cell too long to be a code has no form at all.
    assert parsing.shape_form("a note about a patient seen today") == ""


def test_a_column_of_prose_publishes_no_forms() -> None:
    """THE SAFETY PROPERTY, and it is the floor doing the work.

    Every cell of a note column has its own form, so no form is shared
    by enough cells to be named, and the census comes out empty. No
    rule decides which columns are codes; the floor decides, as it
    decides everything else.
    """
    words = "patient reports mild chest pain on exertion denies fever".split()
    rng = random.Random(8)
    notes = [
        " ".join(rng.choice(words) for _each in range(rng.randint(6, 14)))
        for _row in range(240)
    ]
    document, _loaded, _folder = _described(notes, "note")
    assert document["columns"][0]["shape_forms"] == {}


def test_a_code_column_publishes_the_forms_it_wore() -> None:
    document, _loaded, _folder = _described(
        _long_tail(
            ["E11.9", "I10", "Z00.00", "J45.909", "M54.5"],
            [f"Q{number:02d}.{number % 3}" for number in range(70, 96)],
        ),
        "dx",
    )
    forms = document["columns"][0]["shape_forms"]
    assert forms, forms
    for form in forms:
        if form == "(withheld)":
            continue
        for character in form:
            if character.isdigit():
                assert character == "9", form
            if character.isalpha():
                assert character == "A", form


# -- the twin --------------------------------------------------------


def test_the_twin_of_a_code_column_is_code_shaped_throughout() -> None:
    """THE CASE THE DECISION IS FOR.

    Before this landing 60 of these 251 cells were `group-14` and the
    like; now every one of them is shaped like a diagnosis code.
    """
    _document, described, folder = _described(
        _long_tail(
            ["E11.9", "I10", "Z00.00", "J45.909", "M54.5"],
            [f"Q{number:02d}.{number % 3}" for number in range(70, 96)],
        ),
        "dx",
    )
    twin = generation.generate(described, 7)
    cells = [cell for cell in twin.columns[0] if cell]
    assert cells
    for cell in cells:
        assert not cell.startswith("group-"), cell
        assert re.fullmatch(r"[A-Z][0-9]{2}(\.[0-9]+)?", cell), cell
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    assert outcome.census.missed == 0


def test_a_hyphenated_code_still_splits_into_its_parts() -> None:
    """THE CRASH THIS CLOSES.

    `group-14` carries a hyphen of its own, so a laboratory code column
    whose twin held it split into two parts and passed for a code,
    while a three-part drug code split into two and crashed the frame
    that expected three.
    """
    for common, rare, parts in (
        (
            ["2160-0", "718-7", "2345-7", "2951-2", "2823-3"],
            [f"{4000 + number}-{number % 10}" for number in range(40)],
            2,
        ),
        (
            [
                "0002-8215-01", "00093-0058-01", "50580-506-02",
                "00378-0208-01", "00069-2587-68",
            ],
            [
                f"{number:05d}-{number % 9999:04d}-{number % 99:02d}"
                for number in range(40)
            ],
            3,
        ),
    ):
        _document, described, _folder = _described(
            _long_tail(common, rare)
        )
        twin = generation.generate(described, 7)
        cells = [cell for cell in twin.columns[0] if cell]
        found = {len(cell.split("-")) for cell in cells}
        assert found == {parts}, (found, parts)


def test_the_published_levels_pay_their_forms_first() -> None:
    """Or every count in the census is missed by double-writing.

    A twin writes the published spellings byte for byte, so those cells
    already wear their forms. A stand-in walk that started from the
    whole census would write each form twice over and miss every count
    it was built to meet.
    """
    _document, described, folder = _described(
        _long_tail(
            ["E11.9", "I10", "Z00.00", "J45.909", "M54.5"],
            [f"Q{number:02d}.{number % 3}" for number in range(70, 96)],
        ),
        "dx",
    )
    twin = generation.generate(described, 7)
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    missed = [
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    ]
    assert [name for name in missed if name.startswith("forms.")] == []


def test_a_stand_in_keeps_the_four_properties_it_had_for_free() -> None:
    """`group-N` had them by construction; a code-shaped one does not.

    A spelling built to look like a code could be a word meaning "no
    value", could read as a number or a date, could carry a comma that
    breaks the row, or could open with a character a spreadsheet reads
    as a formula. Each is asked of every stand-in before it is used.
    """
    assert not generation._is_a_usable_stand_in("NA")
    assert not generation._is_a_usable_stand_in("1234")
    assert not generation._is_a_usable_stand_in("2024-03-17")
    assert not generation._is_a_usable_stand_in("a,b")
    assert not generation._is_a_usable_stand_in("=SUM(A1)")
    assert generation._is_a_usable_stand_in("A00.0")


def test_a_label_role_that_publishes_no_census_is_unchanged() -> None:
    """The three sibling roles keep the neutral spelling.

    A column at or under the categorical ceiling publishes its levels,
    so its twin holds them and has no stand-in to shape.
    """
    values = ["north"] * 60 + ["south"] * 60 + ["east"] * 60 + ["west"] * 60
    document, _loaded, _folder = _described(values, "region")
    assert document["columns"][0]["role"] == "categorical"
    assert "shape_forms" not in document["columns"][0]


# -- what the census found in the walk that was already there ---------


def _forms_of(cells: "list[str]") -> "dict[str, int]":
    counted: dict[str, int] = {}
    for cell in cells:
        form = parsing.shape_form(cell)
        counted[form] = counted.get(form, 0) + 1
    return counted


def _level_with_held_back_spellings() -> "list[str]":
    """A code column one of whose labels was written three ways.

    `E11.9` clears the floor; `e11.9` (three rows) and `E11.9 ` (two)
    do not, so they are held back as a multiplicity map and the twin
    makes up two spellings in their place. All five rows of the first
    two wear the form `A99.9`; the two trailing-space rows wear
    `A99.9 `, which no cell shares, so the floor pools them.
    """
    values: list[str] = []
    for code, count in zip(
        ["E11.9", "I10.0", "Z00.00", "J45.90", "M54.50"], (62, 45, 34, 28, 22)
    ):
        values = values + [code] * count
    values = values + ["e11.9"] * 3 + ["E11.9 "] * 2
    for place, number in enumerate(range(70, 96)):
        values = values + [f"Q{number:02d}.{number % 3}"] * (
            1 if place % 2 else 2
        )
    random.Random(5).shuffle(values)
    return values


def test_a_made_up_variant_keeps_the_form_where_one_spelling_is_left() -> None:
    """THE DEFECT THE CENSUS FOUND IN A WALK OLDER THAN IT.

    A held-back spelling of a published label is made up by flipping
    case and then, when the flips run out, by appending spaces -- and a
    trailing space is A DIFFERENT WRITTEN FORM. With one letter in
    `E11.9` there is exactly one flip and it is already published, so
    both made-up spellings were `e11.9 ` and `e11.9  `, and three cells
    the census counted at `A99.9` were written at a form the source
    never had.

    The label's OWN spelling is the one further spelling that folds
    onto the label and keeps its form. The binary counter calls it
    order zero and started at one, so the walk never offered it. It is
    offered now, wherever nothing else of the level needs it.
    """
    _document, described, folder = _described(
        _level_with_held_back_spellings(), "dx"
    )
    twin = generation.generate(described, 7)
    cells = [cell for cell in twin.columns[0] if cell]
    assert "e11.9" in cells
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    missed = [
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    ]
    assert missed == []


def test_the_form_keeping_spelling_goes_to_the_largest_held_back_group() -> None:
    """It is scarce, so it is spent where it pays the most cells.

    Two spellings were held back here, one covering three rows and one
    covering two, and only ONE further spelling keeps the form. Giving
    it to the two-row group leaves three cells in a form the column
    never had and the census one short; giving it to the three-row
    group leaves two, which is exactly what the source pooled.
    """
    document, described, _folder = _described(
        _level_with_held_back_spellings(), "dx"
    )
    published = document["columns"][0]["shape_forms"]
    twin = generation.generate(described, 7)
    counted = _forms_of([cell for cell in twin.columns[0] if cell])
    assert counted["A99.9"] == published["A99.9"]
    assert counted["A99.9 "] == published["(withheld)"]


def test_a_multiplicity_key_past_nine_is_read_as_a_number() -> None:
    """`10` comes after `2`, and the code sorted the key TEXT.

    Method G8.1 step 2 says ascending numeric order. Sorting the
    strings puts `10` first, which two implementations reading one
    document would disagree about as soon as a spelling covers ten
    rows.
    """
    assert generation._withheld_keys({"10": 1, "2": 1, "9": 3}) == [
        "2", "9", "10",
    ]


def test_a_stand_in_that_collides_still_owes_its_form() -> None:
    """The walk used to advance past the form, not just the spelling.

    A stand-in's spelling is stepped until it clears everything already
    written. The step also chose WHICH form to write, so a collision
    threw one away and the census went unpaid. The form a stand-in owes
    is now a debt over the column's cells and a collision moves only
    the spelling.

    Here the first spellings the stepper reaches are exactly what the
    column already published, so every early candidate collides.
    """
    values: list[str] = []
    for code, count in zip(
        ["A00.0", "B01.1", "C02.2", "D03.3", "E04.4"], (62, 45, 34, 28, 22)
    ):
        values = values + [code] * count
    for place, number in enumerate(range(70, 96)):
        values = values + [f"Q{number:02d}.{number % 3}"] * (
            1 if place % 2 else 2
        )
    random.Random(3).shuffle(values)
    document, described, folder = _described(values, "dx")
    twin = generation.generate(described, 7)
    counted = _forms_of([cell for cell in twin.columns[0] if cell])
    assert counted == document["columns"][0]["shape_forms"]
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    assert validation.measure(described, f"{written}").census.missed == 0


def test_a_stand_in_pays_the_form_owing_the_most_cells() -> None:
    """Two forms, one supply of stand-ins, and a fixed size each.

    A stand-in covers its level's size and nothing else, so the walk
    chooses only WHERE to pay. It pays the largest debt first, which
    leaves the smallest remainder when the sizes do not divide the
    debts evenly.
    """
    owing = {"A99.9": 3, "9999-9": 40, "A99.99": 40}
    assert generation._neediest_form(owing) == "9999-9"
    assert generation._neediest_form({"A99.9": 0}) == ""
    assert generation._neediest_form({}) == ""


# -- the free-text half, which is where a code column usually lands ---


def _all_different(values: "list[str]", name: str = "code"):
    """A column of 240 different codes, which no earlier rule claims."""
    random.Random(4).shuffle(values)
    return _described(values, name)


def test_an_all_different_code_column_is_free_text_and_says_its_shape() -> None:
    """WHERE A REAL CODE COLUMN USUALLY LANDS.

    A laboratory-code column holds hundreds of different codes and
    repeats few of them, so no level clears the floor, no earlier rule
    claims it, and it falls to the fallback role. That role publishes
    nothing of its values -- and the census is the one thing it now
    says, because a form carries no figure and no letter of any cell.
    """
    document, _described_profile, _folder = _all_different(
        [f"{1000 + number * 13}-{number % 10}" for number in range(240)],
        "lab_code",
    )
    block = document["columns"][0]
    assert block["role"] == "free_text"
    assert block["shape_forms"] == {"9999-9": 240}


def test_the_twin_of_a_free_text_code_column_wears_the_form() -> None:
    """The half that was missing when the description already had it.

    The census shipped on this role and the invention walk ignored it,
    so a column of `4548-4` got a twin of `F----6`: the right length,
    five hyphens where the source had one, and a split into six parts
    where the source split into two.
    """
    _document, described, folder = _all_different(
        [f"{1000 + number * 13}-{number % 10}" for number in range(240)],
        "lab_code",
    )
    twin = generation.generate(described, 7)
    cells = [cell for cell in twin.columns[0] if cell]
    assert len(cells) == 240
    for cell in cells:
        assert re.fullmatch(r"[0-9]{4}-[0-9]", cell), cell
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    missed = [
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    ]
    assert missed == []


def test_a_form_is_walked_so_that_every_position_of_it_varies() -> None:
    """AND THE PLAIN COUNTER CHANGED A TWIN'S ROLE.

    Two hundred and forty values taken in counting order out of a form
    holding a hundred thousand leave every position but the lowest at
    zero, so every cell of the twin ended `-0` -- and a column whose
    cells all end in the same two characters is not free text to the
    describer, it is a column of numbers wearing an affix. The twin
    reprofiled as `affixed_number` where the source was `free_text`.

    A stride sharing no factor with the form's own supply is a
    one-to-one map onto it, so no two steps below that supply collide
    and consecutive steps land far apart.
    """
    spellings = [generation._filled_form("9999-9", step) for step in range(240)]
    assert len(set(spellings)) == 240
    form = "9999-9"
    for place in range(len(form)):
        seen = {spelling[place] for spelling in spellings}
        if form[place] == "9":
            assert len(seen) > 1, place
        else:
            assert seen == {form[place]}, place
    assert generation._form_room("9999-9") == 100000
    assert generation._form_room("A99.9") == 26000
    assert generation._form_room("--") == 1


def test_a_form_is_offered_only_where_the_length_and_the_words_agree() -> None:
    """A form fixes a length, which is what makes it assignable at all.

    Every cell that wore a form was exactly as long as the form, so
    giving a form to a value the packing put at that length costs the
    published length statistics nothing. A space survives into a form
    unchanged, so the word count has to agree too.
    """
    assert generation._form_words("9999-9") == 1
    assert generation._form_words("AAA AAAAA") == 2


def test_a_column_of_prose_is_written_exactly_as_it_was_before() -> None:
    """THE REGRESSION GUARD FOR EVERY FREE-TEXT COLUMN THERE IS.

    A prose column publishes an empty census, so no value of it is
    offered a form and the invention walk is what it was. The twin is
    still made-up language honouring the published length and word
    statistics.
    """
    words = "patient reports mild chest pain on exertion denies fever".split()
    rng = random.Random(8)
    notes = [
        " ".join(rng.choice(words) for _each in range(rng.randint(6, 14)))
        for _row in range(240)
    ]
    document, described, folder = _described(notes, "note")
    assert document["columns"][0]["shape_forms"] == {}
    twin = generation.generate(described, 7)
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    assert outcome.census.missed == 0


def test_every_named_code_system_survives_both_shapes() -> None:
    """THE SWEEP THE OWNER ASKED FOR, held as one executable case.

    Each of these is a real clinical coding scheme, written twice: as a
    column of all-different codes, which falls to `free_text`, and as a
    long tail, which is the label role. What is asserted is what a
    person developing against the twin would check first -- that the
    twin's cells are shaped like codes of that scheme, and that a split
    on the hyphen gives the number of parts the scheme has.
    """
    schemes = (
        ("icd10", [f"{chr(65 + n % 26)}{n % 99:02d}.{n % 9}"
                   for n in range(240)], r"[A-Z][0-9]{2}\.[0-9]", 1),
        ("hcpcs", [f"{chr(65 + n % 26)}{1000 + n % 9000:04d}"
                   for n in range(240)], r"[A-Z][0-9]{4}", 1),
        ("loinc", [f"{1000 + n * 13}-{n % 10}"
                   for n in range(240)], r"[0-9]{4}-[0-9]", 2),
        ("ndc", [f"{n % 99999:05d}-{n % 9999:04d}-{n % 99:02d}"
                 for n in range(240)], r"[0-9]{5}-[0-9]{4}-[0-9]{2}", 3),
    )
    for name, values, pattern, parts in schemes:
        random.Random(4).shuffle(values)
        for column in (values, _long_tail(values[:5], values[5:31])):
            _document, described, _folder = _described(list(column), name)
            twin = generation.generate(described, 7)
            cells = [cell for cell in twin.columns[0] if cell]
            assert cells, name
            for cell in cells:
                assert re.fullmatch(pattern, cell), (name, cell)
            assert {len(cell.split("-")) for cell in cells} == {parts}, name


def test_the_report_says_which_stand_ins_wore_a_published_form() -> None:
    """A column can hold both kinds, so the count is given.

    Where the forms a column's held-back cells wore were themselves too
    rare to name, the census owes the stand-ins nothing and they are
    the neutral spelling exactly as before. Where it owes them
    something they are written in it. One column can have both, so the
    sentence names how many rather than leaving a reader to guess which
    happened.
    """
    _document, described, _folder = _described(
        _long_tail(
            ["E11.9", "I10", "Z00.00", "J45.909", "M54.5"],
            [f"Q{number:02d}.{number % 3}" for number in range(70, 96)],
        ),
        "dx",
    )
    twin = generation.generate(described, 7)
    said = [
        note.achieved
        for note in twin.deviations
        if note.fact == "suppressed_levels"
    ]
    assert said, twin.deviations
    assert "written in a form this column published" in said[0], said

    # ...and a column that publishes no census keeps the older sentence,
    # which claims the spelling is NEUTRAL and may go on claiming it.
    words = "patient reports mild chest pain on exertion denies fever".split()
    rng = random.Random(8)
    values = [
        " ".join(rng.choice(words) for _each in range(rng.randint(6, 14)))
        for _row in range(220)
    ]
    values = values + ["seen in clinic today"] * 20
    _document, described, _folder = _described(values, "note")
    twin = generation.generate(described, 7)
    said = [
        note.achieved
        for note in twin.deviations
        if note.fact == "suppressed_levels"
    ]
    for sentence in said:
        assert "neutral labels made up in their place" in sentence, sentence

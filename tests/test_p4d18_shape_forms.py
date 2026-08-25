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
import time

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
        ("E11.9", "@%%.%"),
        ("S72.001A", "@%%.%%%@"),
        ("4548-4", "%%%%-%"),
        ("0002-8215-01", "%%%%-%%%%-%%"),
        ("120/80", "%%%/%%"),
        ("A-1", "@-%"),
    ):
        assert parsing.shape_form(text) == form, text
    # ...and a cell of ONE kind of symbol has no form, because
    # `length` and the two alphabet counts already say everything such
    # a key could say.
    for uniform in ("00100", "@@@@@", "north", "A", "999999"):
        assert parsing.shape_form(uniform) == "", uniform
    # ...and a cell too long to be a code has no form at all.
    assert parsing.shape_form("a note about a patient seen today") == ""


def test_a_column_of_prose_publishes_no_forms() -> None:
    """THE SAFETY PROPERTY, and the SPACE is what does the work.

    The first version of this test used notes over twenty-four
    characters, where the length limit hides the question -- so it
    would have passed with the rule that actually protects prose
    removed. These notes are SHORT, well inside the limit, and the
    column still publishes nothing, because a cell holding a space has
    no form (review round 1, test weakening 1).
    """
    words = ("pain", "fever", "cough", "rash", "ache")
    rng = random.Random(8)
    notes = [
        " ".join(rng.choice(words) for _each in range(rng.randint(2, 3)))
        for _row in range(240)
    ]
    assert max(len(note) for note in notes) < parsing.SHAPE_FORM_LIMIT
    document, _loaded, _folder = _described(notes, "note")
    assert document["columns"][0]["shape_forms"] == {}


def test_a_short_sentence_template_publishes_nothing_either() -> None:
    """THE LEAK THE CLOSED MARK LIST CLOSES.

    Two hundred and forty different short sentences written to ONE
    template all share a form, so the floor names it -- and that form
    said every word's length, where the space fell, where the comma
    fell and what the sentence ended with. It is a fact about a
    sentence, which is what this census is not for.

    THE SPACE IS ISOLATED HERE, and it was not (review round 2, test
    weakening 21). The first version of this used `xxxxx, yyyy!`, which
    carries BOTH a space and a `!` -- and `!` is not one of the
    thirteen marks -- so removing either exclusion on its own left the
    cell formless and the test green. These sentences carry nothing
    but letters, a comma and the space, so the space is the only thing
    standing between them and a published form.
    """
    rng = random.Random(3)
    letters = "abcdefghijklmnopqrstuvwxyz"
    sentences = []
    while len(sentences) < 240:
        one = "".join(rng.choice(letters) for _each in range(5))
        two = "".join(rng.choice(letters) for _each in range(4))
        sentence = f"{one}, {two}"
        if sentence not in sentences:
            sentences = sentences + [sentence]
    assert max(len(one) for one in sentences) < parsing.SHAPE_FORM_LIMIT
    document, _loaded, _folder = _described(sentences, "note")
    assert document["columns"][0]["shape_forms"] == {}


def test_a_form_carries_no_letter_of_any_alphabet_and_no_odd_mark() -> None:
    """THE LEAK ROUND 1 FOUND, AND WHAT ROUND 2 DID TO THE REPAIR.

    Replacing the ASCII ranges alone left every other letter standing,
    so a column of Japanese clinical text published a key holding the
    words themselves. Round 1 answered by replacing letters and digits
    over the whole of Unicode; round 2 showed that answer asks the
    INTERPRETER what a letter is, and five supported interpreters give
    five answers.

    So the ranges are fixed and everything outside them makes the cell
    FORMLESS. The leak stays closed -- nothing outside ASCII can stand
    in a key, because no cell holding it has a form at all -- and the
    census now says the same thing on every Python this package runs
    on. What it costs is the census on a column of non-ASCII codes,
    which the band check was going to refuse to write anyway.
    """
    # A CELL OUTSIDE THE ASCII RANGES HAS NO FORM, and the ranges are
    # fixed here rather than asked of the interpreter (review round 2
    # finding 14). `str.isalpha` and `str.isdigit` answer out of the
    # Unicode database the running Python carries, and this package
    # supports five of them: measured, the same table produced a
    # different census, profile and twin on 3.10 and 3.13, and a twin
    # built on one and validated on the other was reported as MISSING
    # two exact counts it held.
    assert parsing.shape_form("患者-1") == ""
    assert parsing.shape_form("Ω12") == ""
    assert parsing.shape_form("١٢٣-A") == ""
    assert parsing.shape_form("𞓐-1") == ""
    # ...and a character outside the thirteen leaves the cell formless,
    # whatever it is.
    for odd in ("a b", "x!y", "a~b", "p&q", "🙂-1", "a\tb", "a'b", 'a"b'):
        assert parsing.shape_form(odd) == "", odd
    # The thirteen themselves survive, and nothing else does.
    assert parsing.shape_form("9-9.9/9_9:9#9*9(9)9[9]9+9,9") == ""  # too long
    assert parsing.shape_form("1#*()[]+,") == "%#*()[]+,"


def test_no_cell_that_has_a_form_can_be_spelled_like_one() -> None:
    """THE PROPERTY THE PLACEHOLDERS BUY, and it needs no data.

    A form carries at least one placeholder, because a form needs two
    of the three kinds and two of the three ARE the placeholders. A
    cell that has a form carries only letters, digits and marks, and
    neither placeholder is any of those. So a cell spelled like a form
    has no form, and no form is ever a spelling a counted cell wore.

    THIS IS WHAT WAS NOT TRUE. Under `9` and `A` every form was its own
    form: of the 1230 forms of length one to three over that alphabet,
    1230 were. `A99` is a real diagnosis code, so a column holding
    three patients coded `A99` had that code held back by the floor and
    published straight back as a census key.
    """
    for placeholder in (parsing.SHAPE_DIGIT, parsing.SHAPE_LETTER):
        assert not placeholder.isdigit(), placeholder
        assert not placeholder.isalpha(), placeholder
        assert placeholder not in parsing.SHAPE_MARKS, placeholder
    assert parsing.SHAPE_DIGIT != parsing.SHAPE_LETTER

    # By enumeration, over the whole key alphabet: no form of length
    # one to three is a spelling any counted cell could wear.
    alphabet = (
        parsing.SHAPE_DIGIT + parsing.SHAPE_LETTER + parsing.SHAPE_MARKS
    )
    seen = 0
    for one in alphabet:
        for two in alphabet:
            for three in alphabet:
                for name in (one, one + two, one + two + three):
                    if not parsing.is_a_written_form(name):
                        continue
                    seen = seen + 1
                    assert parsing.shape_form(name) == "", name
    assert seen > 1000, seen


def test_a_prose_column_whose_forms_are_each_its_own_is_pooled() -> None:
    """AND THE CONTRACT SAID OTHERWISE, WHICH WAS WRONG.

    The claim was that a column of prose publishes `{}` because every
    cell's form is its own. That is not what happens to a form nobody
    else shares: the floor POOLS it, and the census reads
    `{"(withheld)": n}`. It is the space, not the floor, that makes a
    prose column publish nothing -- and this pins the distinction, on a
    column of short different codes where the pooling really does
    happen.
    """
    values = [f"{number:03d}-{number % 7}" for number in range(240)]
    document, _loaded, _folder = _described(values, "code")
    forms = document["columns"][0]["shape_forms"]
    assert forms == {"%%%-%": 240}, forms
    # ...and where the forms really do differ, the pool is what holds
    # them, not an empty census.
    mixed = [
        f"{chr(65 + number % 26)}{number:0{2 + number % 20}d}"
        for number in range(240)
    ]
    document, _loaded, _folder = _described(mixed, "code")
    forms = document["columns"][0]["shape_forms"]
    assert "(withheld)" in forms, forms
    assert forms["(withheld)"] > 0


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


def test_a_categorical_column_with_a_rare_tail_gets_shaped_stand_ins() -> None:
    """THE CASE THAT WAS LEFT OUT, AND IT IS THE COMMON ONE.

    The census first stood on `long_tail_labels` alone, reasoning that
    the other three label roles publish their levels so their twins
    hold them and have no stand-in to shape. Running the tool on a
    patient table is what showed that wrong: a diagnosis column of five
    common codes and twenty-six rare ones has thirty-one different
    values, which is UNDER the categorical ceiling for four hundred
    rows -- so it takes `categorical`, and the floor holds back all
    twenty-six. Its twin held `group-1` through `group-24`.

    Whether a label role suppresses levels is a fact about the FLOOR,
    not about the role, so the census stands on all four.
    """
    values = []
    for code, count in zip(
        ["E11.9", "I10.0", "Z00.00", "J45.90", "M54.50"], (98, 76, 62, 48, 40)
    ):
        values = values + [code] * count
    for number in range(70, 96):
        values = values + [f"Q{number:02d}.{number % 3}"] * 2
    random.Random(4).shuffle(values)
    document, described, folder = _described(values, "dx")
    block = document["columns"][0]
    assert block["role"] == "categorical"
    assert block["shape_forms"], block
    assert block["suppressed_levels"] > 0

    twin = generation.generate(described, 7)
    cells = [cell for cell in twin.columns[0] if cell]
    for cell in cells:
        assert not cell.startswith("group-"), cell
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    missed = [
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    ]
    assert [name for name in missed if name.startswith("forms.")] == []


def test_a_column_of_plain_words_publishes_no_census_at_all() -> None:
    """Because a form of one kind of symbol is not a form.

    Four region names would say `AAAAA` and `AAAA`, and `length`
    already publishes the four and the five exactly while
    `n_code_alphabet` already says which alphabet they came from. A key
    saying only that adds a published fact carrying no information, and
    the census is not published where it would say nothing.
    """
    values = ["north"] * 60 + ["south"] * 60 + ["east"] * 60 + ["west"] * 60
    document, _loaded, _folder = _described(values, "region")
    block = document["columns"][0]
    assert block["role"] == "categorical"
    assert block["shape_forms"] == {}
    assert block["suppressed_levels"] == 0


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
    """It is scarce, so it is spent where it covers the most cells.

    Two spellings were held back here, one covering three rows and one
    covering two, and only ONE further spelling keeps the form. A
    trailing space makes a cell FORMLESS, so a spelling reached that
    way settles nothing at all: giving the form-keeping spelling to the
    two-row group leaves the census three cells short, and giving it to
    the three-row group leaves it two short -- which is exactly what
    the source itself left, its own two trailing-space cells being
    counted nowhere.
    """
    document, described, _folder = _described(
        _level_with_held_back_spellings(), "dx"
    )
    published = document["columns"][0]["shape_forms"]
    twin = generation.generate(described, 7)
    counted = _forms_of([cell for cell in twin.columns[0] if cell])
    assert counted["@%%.%"] == published["@%%.%"]
    assert "(withheld)" not in published, published
    # The two cells the source wrote with a trailing space have no form
    # and are in no count; the twin's stand for them has none either.
    assert counted[""] == 2, counted


def test_a_multiplicity_key_is_read_as_a_number_and_it_changes_nothing() -> None:
    """AND SAYING SO IS THE POINT OF THIS TEST.

    Method G8.1 step 2 says ascending numeric order; the code sorted
    the key STRINGS, which in general puts `10` before `2`. On a
    CONFORMING document the two orders agree, because section 5.3 pads
    a multiplicity key with leading zeros to a uniform width and
    section 3.1 gives that agreement as the reason for the padding. So
    this changes no twin's bytes, and the earlier version of this test
    claimed a live defect by handing the helper keys of unequal width
    that no document can carry (review round 1, test weakening 8).

    What it pins is that the code now says what the method says, and
    that the padded case -- the only one a loader admits -- is
    unaffected.
    """
    # The unequal-width keys no conforming document holds: the helper
    # reads them as numbers, which is what the method asks for.
    assert generation._withheld_keys({"10": 1, "2": 1, "9": 3}) == [
        "2", "9", "10",
    ]
    # ...and the padded keys every conforming document DOES hold sort
    # the same way under either reading, which is why nothing moved.
    padded = {"02": 1, "09": 3, "10": 1}
    assert generation._withheld_keys(padded) == sorted(padded)


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


def test_a_stand_in_settles_the_form_owing_the_most_cells() -> None:
    """Two forms, one supply of stand-ins, and a fixed size each.

    A stand-in covers its level's size and nothing else, so the walk
    chooses only WHERE to settle. It settles the largest debt first,
    which leaves the smallest remainder when the sizes do not divide
    the debts evenly.
    """
    owing = {"@%%.%": 3, "%%%%-%": 40, "@%%.%%": 40}
    assert generation._neediest_form(owing) == "%%%%-%"
    assert generation._neediest_form({"@%%.%": 0}) == ""
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
    assert block["shape_forms"] == {"%%%%-%": 240}


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
    spellings = [generation._filled_form("%%%%-%", step) for step in range(240)]
    assert len(set(spellings)) == 240
    form = "%%%%-%"
    for place in range(len(form)):
        seen = {spelling[place] for spelling in spellings}
        if form[place] == parsing.SHAPE_DIGIT:
            assert len(seen) > 1, place
        else:
            assert seen == {form[place]}, place
    assert generation._form_room("%%%%-%") == 100000
    assert generation._form_room("@%%.%") == 26000
    assert generation._form_room("--") == 1


def test_a_form_is_offered_only_where_the_length_and_the_words_agree() -> None:
    """AND THE PREDICATES ARE ASKED OF `_wanted_form`, NOT OF A HELPER.

    The first version of this test called `_form_words` and nothing
    else, so removing either predicate from the offer itself left it
    green (review round 1, test weakening 3).

    A form fixes a length, so a group carrying a published length END
    may take only a form of exactly its length; every other group may
    take any form whose length lies between the two published ends,
    since those are approximated and an exact count outranks them.
    """
    owing = {"%%%%-%": 40, "@%%-%": 25, "@%-%": 60}
    rich = [999, 999]
    # A length-carrying group takes only its OWN length: at six it can
    # have neither the five-character form nor the four-character one,
    # however much either owes.
    assert generation._wanted_form(owing, 6, 1, True, 4, 9, rich) == "%%%%-%"
    assert generation._wanted_form(owing, 5, 1, True, 4, 9, rich) == "@%%-%"
    # ...and a carrier at a length no form has is offered none.
    assert generation._wanted_form(owing, 7, 1, True, 4, 9, rich) == ""
    # A group carrying NEITHER end may take any admitted length, and
    # takes the form owing the most cells whatever its length.
    assert generation._wanted_form(owing, 6, 1, False, 4, 9, rich) == "@%-%"
    # ...but not a length the published ends exclude: raising the floor
    # to five puts the four-character form out of reach.
    assert generation._wanted_form(owing, 6, 1, False, 5, 9, rich) == "%%%%-%"
    # The word count has to agree either way, because a space survives
    # into a form unchanged.
    assert generation._wanted_form(owing, 6, 2, False, 4, 9, rich) == ""
    # ...AND THE AVERAGE'S OWN BUDGET IS ASKED LAST (review round 2
    # finding 9). With no room left to move, a non-carrier may take
    # only a form of exactly the length the packing gave it.
    broke = [0, 0]
    assert generation._wanted_form(owing, 6, 1, False, 4, 9, broke) == "%%%%-%"
    assert generation._wanted_form(owing, 7, 1, False, 4, 9, broke) == ""
    assert generation._form_words("%%%%-%") == 1
    assert generation._form_words("AAA AAAAA") == 2


def test_a_column_of_prose_is_written_exactly_as_it_was_before() -> None:
    """THE REGRESSION GUARD FOR EVERY FREE-TEXT COLUMN THERE IS.

    A prose column publishes an empty census, so no value of it is
    offered a form and the invention walk is what it was.

    IT COMPARES THE BYTES, and it did not: measuring only that the
    published facts were met let any other invented prose pass, which
    is most of what this test is for (review round 2, test weakening
    22). The twin is built twice -- once here and once with the form
    offer stubbed out entirely -- and the two must be the same file.
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

    # ...and BYTE FOR BYTE what the walk writes with the form offer
    # taken out altogether.
    offer = generation._wanted_form
    generation._wanted_form = (
        lambda owing, length, words, carrier, shortest, longest, budget: ""
    )
    try:
        without = generation.generate(described, 7)
    finally:
        generation._wanted_form = offer
    assert rendering.twin_csv(without) == rendering.twin_csv(twin)


def test_every_named_code_system_survives_both_shapes() -> None:
    """THE SWEEP THE OWNER ASKED FOR, held as one executable case.

    Each of these is a real clinical coding scheme, written twice: as a
    column of all-different codes, which falls to `free_text`, and as a
    long tail, which is the label role. What is asserted is what a
    person developing against the twin would check first -- that the
    twin's cells are shaped like codes of that scheme, and that a split
    on the hyphen gives the number of parts the scheme has.
    """
    # ALL TEN, because the plan and the changelog say ten and this
    # said four (review round 2, test weakening 23). A scheme whose
    # column lands on a numeric role has no census to test -- its
    # shape is `numeric_styles`' and `pad_widths`' business -- so it
    # is named here with the role it takes, and the assertion is the
    # one that matters either way: the twin's cells are shaped like
    # that scheme and split into the parts it has.
    schemes = (
        ("scheme01", [f"{250 + n % 99:03d}.{n % 9}"
                  for n in range(240)], r"[0-9]{3}\.[0-9]", 1),
        ("scheme02", [f"{chr(65 + n % 26)}{n % 99:02d}.{n % 9}"
                   for n in range(240)], r"[A-Z][0-9]{2}\.[0-9]", 1),
        ("scheme03", [f"{10000 + n * 37:05d}"
                 for n in range(240)], r"[0-9]{5}", 1),
        ("scheme04", [f"{chr(65 + n % 26)}{1000 + n % 9000:04d}"
                   for n in range(240)], r"[A-Z][0-9]{4}", 1),
        ("scheme05", [f"D{1000 + n * 7:04d}"
                 for n in range(240)], r"D[0-9]{4}", 1),
        ("scheme06", [f"{1000 + n * 13}-{n % 10}"
                   for n in range(240)], r"[0-9]{4}-[0-9]", 2),
        ("scheme07", [f"{100000 + n * 97}"
                    for n in range(240)], r"[0-9]{6}", 1),
        ("scheme08", [f"{100000000 + n * 7919}"
                    for n in range(240)], r"[0-9]{9}", 1),
        ("scheme09", [f"{n % 200:03d}"
                 for n in range(240)], r"[0-9]{3}", 1),
        ("scheme10", [f"{n % 99999:05d}-{n % 9999:04d}-{n % 99:02d}"
                 for n in range(240)], r"[0-9]{5}-[0-9]{4}-[0-9]{2}", 3),
    )
    # THE ONE CASE THAT DOES NOT HOLD, NAMED RATHER THAN SKIPPED
    # (residual R-P4-35). The ninth column, running `000` to `199`,
    # is a column of NUMBERS, so the padding census governs it -- and
    # that census counts only the cells written with a leading zero.
    # The hundred-odd cells written `100` to `199` carry none, so
    # their WIDTH is published nowhere and the twin may write one two
    # figures wide. It is a gap in `pad_widths`, not in the form
    # census, and closing it is that census's landing.
    short_of_it = {("scheme09", "long tail")}
    for name, values, pattern, parts in schemes:
        random.Random(4).shuffle(values)
        for shape, column in (
            ("all different", values),
            ("long tail", _long_tail(values[:5], values[5:31])),
        ):
            _document, described, _folder = _described(list(column), name)
            twin = generation.generate(described, 7)
            cells = [cell for cell in twin.columns[0] if cell]
            assert cells, name
            shaped = [
                cell for cell in cells if re.fullmatch(pattern, cell)
            ]
            if (name, shape) in short_of_it:
                # It is still MOSTLY right, and a regression past this
                # would turn the test red rather than pass quietly.
                assert len(shaped) >= len(cells) - 8, (name, shape)
                continue
            assert len(shaped) == len(cells), (
                name, shape, sorted(set(cells) - set(shaped))[:4]
            )
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


# -- what round 1 showed the walk could not survive -------------------


def test_a_form_no_spelling_of_which_is_usable_ends_the_walk() -> None:
    """IT USED TO RUN FOREVER, on a document the loader had accepted.

    A column of `-A` through `-Z` publishes the form `-A`, and EVERY
    spelling of that form opens with the character a spreadsheet reads
    as the start of a formula -- so every candidate was refused and the
    stand-in walk cycled through the same twenty-six candidates without
    end. The walk is bounded by the form's own supply and then gives
    the form up: a neutral spelling in place of a shaped one costs the
    census a count and says so, where a hang costs the person the run
    and says nothing.
    """
    values = ["steady"] * 20 + [f"-{chr(65 + n)}" for n in range(26)]
    values = values + [f"{n:025d}" for n in range(194)]
    _document, described, _folder = _described(values, "code")
    twin = generation.generate(described, 7)
    cells = [cell for cell in twin.columns[0] if cell]
    assert cells
    for cell in cells:
        assert cell[0] not in "=+-@", cell


def test_a_free_text_form_is_held_to_the_same_four_properties() -> None:
    """THE HALF THE LABEL WALK HAD AND THE INVENTION WALK DID NOT.

    Every candidate the alphabet walk builds comes from an alphabet
    with the four hazardous characters taken out, so the class and
    collision checks were the whole of what a candidate owed. A form is
    built from the CELL, so it can open with one of them -- and a
    column of `-000-A` published `-999-A`, whose every spelling opens
    with the character a spreadsheet reads as the start of a formula.
    The twin wrote none of them.
    """
    values = [f"-{number:03d}-{chr(65 + number % 26)}" for number in range(240)]
    random.Random(1).shuffle(values)
    document, described, _folder = _described(values, "code")
    assert document["columns"][0]["role"] == "free_text"
    assert document["columns"][0]["shape_forms"] == {"-%%%-@": 240}
    twin = generation.generate(described, 7)
    cells = [cell for cell in twin.columns[0] if cell]
    assert cells
    for cell in cells:
        assert cell[0] not in "=+-@", cell


def test_the_four_properties_are_each_asked_and_not_three_of_them() -> None:
    """Each of the four, including the ones the first test left out."""
    for refused in ("NA", "n/a", "1234", "2024-03-17", "a,b", 'a"b',
                    "=SUM(A1)", "+1", "-x", "@here"):
        assert not generation._is_a_usable_stand_in(refused), refused
    for allowed in ("A00.0", "X12", "%%%%-%"):
        assert generation._is_a_usable_stand_in(allowed), allowed


def test_a_walked_form_varies_every_fillable_position_it_has() -> None:
    """LETTERS TOO, WHICH THE FIRST VERSION OF THIS TEST DID NOT ASK.

    It walked `9999-9`, which has no letter, so a walk that left every
    letter position constant would have passed it (review round 1, test
    weakening 5).
    """
    for form in ("%%%%-%", "@%%.%", "@@%%@@", "@%@%@%"):
        spellings = [generation._filled_form(form, step) for step in range(240)]
        assert len(set(spellings)) == 240, form
        for place in range(len(form)):
            seen = {spelling[place] for spelling in spellings}
            if form[place] in (parsing.SHAPE_DIGIT, parsing.SHAPE_LETTER):
                assert len(seen) > 1, (form, place)
            else:
                assert seen == {form[place]}, (form, place)


def test_the_twin_says_so_when_it_cannot_reach_a_published_form() -> None:
    """THE TWIN'S OWN REPORT OWED THIS AND DID NOT PAY IT.

    Every other exact census this generator writes is recounted off the
    finished cells and named where it was missed. The form census was
    checked only by `synthtwin validate` -- run later, and by somebody
    who might not run it -- so a twin that could not reach a form said
    nothing about it in the file written beside it.

    The column here publishes a form every spelling of which opens with
    the character a spreadsheet reads as the start of a formula, so the
    walk refuses every one and gives the form up. The count is missed,
    and now it is SAID.
    """
    values = ["steady"] * 20 + [f"-{chr(65 + n)}" for n in range(26)]
    values = values + [f"{n:025d}" for n in range(194)]
    _document, described, _folder = _described(values, "code")
    twin = generation.generate(described, 7)
    said = [note for note in twin.deviations if note.fact == "shape_forms"]
    assert said, [note.fact for note in twin.deviations]
    assert "-@" in said[0].published, said[0].published
    assert "splits a value on a mark" in said[0].note


def test_a_twin_that_reaches_every_form_says_nothing_about_them() -> None:
    """The note is a deviation and not a running commentary."""
    values = [f"{1000 + number * 13}-{number % 10}" for number in range(240)]
    random.Random(4).shuffle(values)
    _document, described, _folder = _described(values, "lab_code")
    twin = generation.generate(described, 7)
    assert [
        note for note in twin.deviations if note.fact == "shape_forms"
    ] == []


def test_the_arrangement_of_forms_is_searched_and_not_only_greedy() -> None:
    """LARGEST DEBT FIRST IS NOT ENOUGH, and the case is ordinary.

    Two forms owing 76 and 164 cells, and twenty-five stand-ins
    covering five levels of eight rows and twenty of ten. The source's
    own arrangement is exact -- two eights and six tens make 76, three
    eights and fourteen tens make 164 -- so an exact one demonstrably
    exists. Paying the largest debt first hands every eight to the
    larger form and reaches neither count.
    """
    sizes = tuple(sorted([8] * 5 + [10] * 20))
    owing = {"@@-%%": 76, "@@_%%": 164}
    taken = generation._shared_out(sizes, dict(owing), {}, {}, ())
    settled: dict[str, int] = {}
    for place in range(len(sizes)):
        form = taken[place]
        settled[form] = settled.get(form, 0) + sizes[place]
    assert settled == owing, settled


def test_where_no_exact_arrangement_exists_the_walk_still_answers() -> None:
    """It settles the largest debt first, which is what it always did.

    Three levels of seven rows cannot settle debts of ten and five
    exactly under any arrangement, so the search finds none and the
    one-pass rule stands -- and the twin's own report names whatever
    that leaves unsettled.
    """
    taken = generation._shared_out((7, 7, 7), {"@-%": 10, "@_%": 5}, {}, {}, ())
    assert taken == ["@-%", "@_%", "@-%"]
    assert generation._shared_out((5,), {}, {}, {}, ()) == [""]


def test_a_file_holding_TOO_MANY_of_a_form_misses_it_too() -> None:
    """THE UPPER HALF OF THE ENVELOPE, WHICH NOTHING EXERCISED.

    Every red case the entry table registers REDUCES a form's count, so
    removing the validator's `measured <= published + pool` bound left
    the whole suite green (review round 1, test weakening 4). The
    envelope is two-sided for a reason: a file writing MORE cells in a
    published form than the census admits is describing a different
    column just as surely as one writing fewer, and a person checking a
    width or a split against it is misled the same way.

    Here the pooled remainder is zero, so the published count is the
    whole envelope, and one extra cell in that form is outside it.
    """
    # Two hundred and thirty cells of one form, and ten that have none
    # at all, because they hold a space -- so the census names 230 and
    # pools nothing.
    values = [f"{1000 + number * 13}-{number % 10}" for number in range(230)]
    values = values + [f"note {number}" for number in range(10)]
    random.Random(4).shuffle(values)
    document, described, folder = _described(values, "lab_code")
    published = document["columns"][0]["shape_forms"]
    assert published == {"%%%%-%": 230}, published

    # A file whose two hundred and forty cells are ALL of that form is
    # ten above the whole envelope.
    rows = [[f"{2000 + number}-{number % 10}", "x"] for number in range(240)]
    written = fixtures.write(
        folder, "too-many.csv", fixtures.rows_to_csv(["lab_code", "other"], rows)
    )
    outcome = validation.measure(described, f"{written}")
    verdicts = {
        check.subcheck: check.verdict
        for check in outcome.checks
        if check.subcheck.startswith("forms.")
    }
    assert verdicts.get("forms.published.%%%%-%") == validation.MISSED, verdicts


# -- what the verification of the round-2 repairs found in them -------


def test_a_form_no_spelling_of_which_serves_costs_the_run_nothing() -> None:
    """IT COST SIX SECONDS ON A SMALL COLUMN.

    The stand-in walk restarted its place in a form's supply on every
    call, so a form every spelling of which is refused -- `-@%%`, each
    one opening with the character a spreadsheet reads as a formula --
    was re-walked whole for each of three hundred held-back levels.
    Measured at 6.0 seconds against 0.025 with the place carried, and
    at four thousand stand-ins the old walk took twelve (review round
    2 finding 13).
    """
    values = ["steady"] * 11
    values = values + [f"-{chr(65 + n % 26)}{n // 26:02d}" for n in range(300)]
    _document, described, _folder = _described(values, "code")
    began = time.monotonic()
    twin = generation.generate(described, 7)
    assert time.monotonic() - began < 2.0
    cells = [cell for cell in twin.columns[0] if cell]
    assert cells


def test_a_shaped_stand_in_does_not_advance_the_neutral_number() -> None:
    """AND THE METHOD SAYS WHEN THAT NUMBER MAY ADVANCE.

    G8.3: the invented labels are `group-1`, `group-2`, … in order,
    each candidate skipped and the number advanced WHEN IT COLLIDES.
    The walk advanced it once per shaped probe too, so a column whose
    forms were reached without a single collision still held
    `group-20101` (review round 2, the second defect its verification
    of finding 13 found).
    """
    values = []
    for code, count in zip(
        ["E11.9", "I10.0", "Z00.00", "J45.90", "M54.50"], (62, 45, 34, 28, 22)
    ):
        values = values + [code] * count
    values = values + [f"Q{number:02d}.{number % 3}" for number in range(200)]
    values = values + [
        f"{chr(65 + n)}{chr(65 + n)}-{n:02d}" for n in range(9)
    ]
    _document, described, _folder = _described(values, "dx")
    twin = generation.generate(described, 7)
    neutral = sorted(
        cell for cell in set(twin.columns[0]) if cell.startswith("group-")
    )
    assert neutral, "this column is meant to reach the neutral spelling"
    assert "group-1" in neutral, neutral[:4]
    for cell in neutral:
        assert int(cell[len("group-"):]) <= len(neutral), cell


def test_a_form_pass_that_gave_up_under_the_letter_ask_is_put_back() -> None:
    """THE RESIDUAL THE FIRST REPAIR OF FINDING 3 LEFT.

    Giving each form its own place in its supply closed finding 3. But
    the first version of that repair never put the place back, so the
    LETTER ASK -- which walks a whole family looking for a spelling
    with a case in it, and is meant to be undone when it fails --
    walked a form's entire supply and left it spent for every value
    after it.

    Measured on one column: 100 of 240 cells reached a published shape
    under that rule, 200 of 240 under this one. Putting it back
    unconditionally reaches 200 too and costs 240,000 fillings against
    1,000 on a column whose every spelling is refused, so the rule is
    the family cursor's own: put back under the ask, left where it
    stopped without it.
    """
    values = list(dict.fromkeys(
        [f"{a}-{b}" for a in "0123456789abcdefghij" for b in "0123456789"]
    ))[:200]
    values = values + [f"X{n:02d}" for n in range(20)]
    values = values + [f"x{n:02d}" for n in range(20)]
    document, described, _folder = _described(values, "code")
    published = document["columns"][0]["shape_forms"]
    twin = generation.generate(described, 7)
    counted = _forms_of([cell for cell in twin.columns[0] if cell])
    met = 0
    for form in published:
        if form == "(withheld)":
            continue
        met = met + min(counted.get(form, 0), published[form])
    assert met >= 190, (met, counted, published)


def test_constant_and_binary_carry_the_census_and_meet_it() -> None:
    """THE TWO LABEL ROLES NOTHING EXERCISED (review round 2, weakening 19).

    The census moved to all four label roles and only `categorical` and
    `long_tail_labels` had a test or an entry-table fixture. A change
    that emitted `{}` for `constant` and `binary`, or skipped their
    form validation, stayed green while the matrix looked covered.
    """
    # BINARY, with one of its two labels below the floor.
    values = ["E11.9"] * 60 + ["I10.0"] * 5
    document, described, folder = _described(values, "dx")
    block = document["columns"][0]
    assert block["role"] == "binary"
    assert block["shape_forms"] == {"@%%.%": 65}, block["shape_forms"]
    assert block["suppressed_levels"] == 1
    twin = generation.generate(described, 7)
    cells = [cell for cell in twin.columns[0] if cell]
    for cell in cells:
        assert re.fullmatch(r"[A-Z][0-9]{2}\.[0-9]", cell), cell
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    assert [
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    ] == []

    # CONSTANT, whose one label the floor holds back: the census is the
    # only thing that says what its twin should look like.
    document, described, folder = _described(["E11.9"] * 5, "dx")
    block = document["columns"][0]
    assert block["role"] == "constant"
    assert block["levels"] == []
    assert block["shape_forms"] == {"(withheld)": 5}, block["shape_forms"]

    # ...and a constant column whose one label CLEARS the floor names
    # the form, and its twin holds the label itself.
    document, described, folder = _described(["E11.9"] * 60, "dx")
    block = document["columns"][0]
    assert block["role"] == "constant"
    assert block["shape_forms"] == {"@%%.%": 60}, block["shape_forms"]
    twin = generation.generate(described, 7)
    assert {cell for cell in twin.columns[0] if cell} == {"E11.9"}


def test_the_form_supply_bound_is_the_form_s_and_not_the_global_one() -> None:
    """AND THE TWO INTEGRATION TESTS COULD NOT TELL THEM APART.

    Both bounded walks cap at `min(the form's own supply, 4096)`.
    Every case exercising them had a supply of 26 or 26,000, so
    removing the form's own half and keeping the global 4096 left both
    green (review round 2, test weakening 18). This asks the bound
    directly, on a form whose supply is far below the global cap and
    whose every spelling is refused.
    """
    # `-@%` opens with the character a spreadsheet reads as a formula,
    # so no spelling of it is ever usable; its supply is 26 x 10.
    assert generation._form_room("-@%") == 260
    for step in range(5):
        assert not generation._is_a_usable_stand_in(
            generation._filled_form("-@%", step)
        )
    values = ["steady"] * 11
    values = values + [f"-{chr(65 + n % 26)}{n % 10}" for n in range(60)]
    _document, described, _folder = _described(values, "code")
    began = time.monotonic()
    twin = generation.generate(described, 7)
    took = time.monotonic() - began
    # Under the form's own supply the whole column costs one walk of
    # 260; under the global cap alone it would cost sixty walks of
    # 4096, and under the pre-repair rule sixty walks of 260 each.
    assert took < 1.0, took
    assert [cell for cell in twin.columns[0] if cell]


def test_every_candidate_is_asked_for_its_band_not_only_a_shaped_one() -> None:
    """AND THE `BY CONSTRUCTION` CLAIM IS CHECKED, NOT ARGUED.

    The band check exists because a form's spelling is built from the
    cell's shape and filled from ASCII, so it can leave the band the
    packing assigned -- a column of Greek-letter codes published
    `n_code_alphabet: 0` and its twin recounted 240.

    It is asked of EVERY candidate. Gating it on `form` changes nothing
    observable, because every spelling the alphabet walk builds is in
    its band already -- and that is the claim this enumerates, over
    every class, band, length and word count the packing can assign. A
    check that runs on everything cannot be weakened to run on nothing
    without turning this red.
    """
    checked = 0
    for place, kind in enumerate(generation._CLASSES):
        for slot, band in enumerate(generation._BANDS):
            for length in range(1, 8):
                permitted = generation._pair_permits(length, 1, False)
                if not permitted & (1 << (place * len(generation._BANDS) + slot)):
                    continue
                checked = checked + 1
                for index in range(80):
                    built = generation._family_at(kind, band, length, 1, index)
                    if built is None:
                        continue
                    assert generation._reads_in_band(built, band), (
                        kind, band, length, built
                    )
    assert checked >= 50, checked


def test_a_column_whose_holes_look_like_values_is_not_accused() -> None:
    """THIRTEEN FABRICATED DEVIATIONS ON A CONFORMING TWIN.

    A twin reproduces the spellings its source's absent cells wore
    (contract 7.7), so a numeric column whose holes were written `-999`
    has twenty twin cells that LOOK like numbers and are not values.
    Nine recounts of the generator asked "is this cell not blank"
    where they meant "is this cell present", and counted every one of
    them: the report said the twin's mean was -40.4 against a
    published 39.5, its standard deviation 277 against 11.6, and its
    first percentile -999.

    `synthtwin validate` was right about that file the whole time and
    said so -- it excludes the holes correctly. Only the report written
    beside the twin accused it, which is worse than saying nothing,
    because a person reading eleven deviations abandons a twin that
    was fine (review round 2 finding 11, widened by its verification).

    What may still be named is a REAL shortfall, and this asserts that
    too: the twin holds fewer distinct values than the description
    publishes, and that one is true.
    """
    values = [str(20 + number % 40) for number in range(240)]
    values = values + ["-999"] * 20
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "thing.csv",
        fixtures.rows_to_csv(["v", "o"], [[value, "x"] for value in values]),
    )
    settings = taxonomy.Settings(declared_missing_values=("-999",))
    document = profile.build_document(
        reading.read_table(f"{table}"), settings, []
    )
    written = fixtures.write_profile(folder, "thing.json", document)
    described = contract.load_profile(f"{written}")
    twin = generation.generate(described, 7)

    named = {note.fact for note in twin.deviations}
    for fabricated in (
        "mean", "std", "skew", "numeric_styles", "n_numeric",
        "percentiles.p01", "percentiles.p05", "percentiles.p10",
        "percentiles.p25",
    ):
        assert fabricated not in named, (fabricated, sorted(named))

    # ...and the shortfall that IS real is still named.
    assert "n_distinct" in named, sorted(named)
    twin_file = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{twin_file}")
    assert [
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    ] == []


def test_a_census_key_is_never_withheld_on_account_of_another_cell() -> None:
    """THE RULE THAT LOOKS LIKE PRIVACY AND IS THE OPPOSITE OF IT.

    Two reads asked for it: do not name a form spelled the same as a
    present cell, so that a column holding `E11.9` beside the literal
    text `@%%.%` does not publish `@%%.%` as a key. It was built twice
    and reverted twice, and this is the test that keeps it out.

    It makes suppression DATA-DEPENDENT, and a reader runs the
    dependency backwards: `e11.9` is published covering eleven rows,
    its form is `@%%.%`, eleven clears the floor, so SF1 REQUIRES that
    key -- and it is absent. Only the collision rule removes it.
    Therefore a cell is spelled exactly `@%%.%`. A floor-suppressed
    value, recovered exactly, from published facts alone.

    What it would prevent discloses nothing: that key is what ANY
    letter-figure-figure-point-figure column publishes.

    So the two documents below must be THE SAME. If they ever differ,
    the rule is back and the channel with it.
    """
    with_it, _loaded, _folder = _described(
        ["E11.9"] * 11 + ["@%%.%"] * 3, "dx"
    )
    without, _loaded, _folder = _described(
        ["E11.9"] * 11 + ["z" * 28] * 3, "dx"
    )
    assert with_it["columns"][0]["shape_forms"] == {"@%%.%": 11}
    assert (
        with_it["columns"][0]["shape_forms"]
        == without["columns"][0]["shape_forms"]
    ), "the census must not depend on what else the column holds"


def test_the_debts_are_settled_by_arithmetic_before_any_search() -> None:
    """A SEARCH NEEDS A BOUND, AND THE BOUND MISSED A REAL ANSWER.

    Twelve held-back levels whose debts of 31 and 74 are met exactly by
    `14+17` and `6+13+13+14+14+14` -- an arrangement the SOURCE itself
    exhibits -- were reached only at node 67,208, past the twenty
    thousand the walk allows, so it settled for 41 and 83 (round 3
    finding 7).

    Which sizes make one debt is a question with an answer: reachable
    sums over the sizes. Both this case and round 1's are settled
    exactly now, without entering the search at all.
    """
    for sizes, owing in (
        ((6, 9, 10, 11, 13, 13, 14, 14, 14, 14, 14, 17),
         {"@-%": 31, "@_%": 74}),
        (tuple(sorted([8] * 5 + [10] * 20)),
         {"@%-%%": 76, "@%_%%": 164}),
    ):
        taken = generation._shared_out(sizes, dict(owing), {}, {}, ())
        settled: dict[str, int] = {}
        for place in range(len(sizes)):
            settled[taken[place]] = settled.get(taken[place], 0) + sizes[place]
        for form in owing:
            assert settled.get(form) == owing[form], (form, settled, owing)


def test_the_supply_knows_what_the_column_has_already_written() -> None:
    """IT COUNTED SPELLINGS THE WALK WOULD REFUSE (round 3 finding 5).

    A form's supply is how many stand-ins it can still dress, not how
    many spellings it has. `_form_room` answers the second: for a form
    whose twenty-six spellings are twenty-five taken and one free, it
    says twenty-six, and an arrangement built on that hands the form
    places it cannot fill.

    It stops at what the caller asked for, too, which is what makes it
    affordable on a wide table -- fifty calls cost five milliseconds
    where the whole-supply scan cost nearly two seconds.
    """
    used = {generation._filled_form("@_", step): 1 for step in range(25)}
    assert generation._form_room("@_") == 26
    assert generation._usable_room("@_", 10, used, {}, ()) == 1
    # ...and a form no spelling of which is usable supplies nothing.
    assert generation._usable_room("-@%%", 10, {}, {}, ()) == 0
    # ...and it stops at what was asked for.
    assert generation._usable_room("@%%.%", 12, {}, {}, ()) == 12

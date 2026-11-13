"""Record numbers beside labels, names joined to record numbers, and names with no layout (plan P4-D469, lane CZ-A2).

Batch 4q's checks measured three readings that published real identifiers
while nothing was declared or answered, each at the owner's table floor
(20,000 rows, 1,000 people of 20 rows): a record number with a sign before
its label (`#MR1000013`, one a row), read as an affixed number, its twin
19,999 of 20,000 real cells; a family name, a given name and a record
number joined by commas (`Cedar,Abc,1000013`), read as an affixed number,
1,000 names published as prefixes and 18,000 twin cells real -- one record
number a person read as labels, 1,000 published whole, with a space after
each comma too; and a held name column with no layout, whose generate took
75 to 80 CPU seconds where the same column with a layout takes 5.5.

THE SWEEP IS GENERATED (LANE I4r RULINGS 1 (4)): thousands of spellings
drawn from a seed by `labelled_records` -- signs, marks, spaces, check
letters, widths, cases; joiners, the number first or last, two to four
parts of a name, initials, suffixes, apostrophes, accents -- each read by
the product's own reader, beside cells no reader may take. ONE case runs
the command at 20,000 rows (one case a writer; THE SUITE'S TIME rule):
the rest of the 20,000-row measurement is K-HZ-22's driver
(`tools/measurements/kpi_identifier_readings.py`, under kpi_run --slow).

LANE CZ-A2'S REPAIR 1 closes the classes at their cause (its skeptic's
items 1 to 5): a record number of five figures or more beside words in an
affixed cell, whatever follows it (`asking._a_whole_number_beside_words`),
one a row and one a person; labels after spaces and a mark, or in a pair
of brackets; every empty part of a joined name set aside; a declared
column of two layouts kept off the other layout's runs; and the walk's
memo of unread searches and its band heads pinned to what they must hold.
"""

from __future__ import annotations

import bisect
import contextlib
import csv
import dataclasses
import io
import json
import pathlib
import random
import unicodedata

import pytest

from synthtwin import asking, cli, generation, parsing, taxonomy

import labelled_records as records
import unanswered_identifier_shapes as held_shapes

SWEEP = 5_000


def test_every_drawn_spelling_of_a_record_number_beside_its_label_is_read_with_its_figures_whole() -> None:
    """5,000 drawn spellings: a sign before the label, a mark or a space after it, a check letter, 5 to 12 figures.

    Each is read by lane HX5's arm (`asking._a_whole_number_after_letters`)
    with its figures whole. MUTANT: `_LABEL_SIGNS` empty (the base's
    reader, which took no sign before a label): every signed spelling is
    unread.
    """
    unread = [
        (cell, figures) for cell, figures in records.label_spellings(SWEEP)
        if (asking._a_whole_number_after_letters(cell) or ("", "", ""))[1] != figures
    ]
    assert unread == []


def test_no_unit_currency_percent_or_bare_figures_is_read_as_a_label() -> None:
    """A unit glued after figures, a currency or percent sign, a decimal: no label (HX5's line, kept)."""
    assert [cell for cell in records.NOT_LABELS if asking._a_whole_number_after_letters(cell) is not None] == []


@pytest.mark.parametrize("item", ["sign_label", "sign_space_label", "label_point", "check_letter",
                                  "number_sign_alone", "sign_on_a_few"])
def test_a_column_of_labelled_record_numbers_one_a_row_is_reached_by_the_each_on_one_row_rule(item: str) -> None:
    """The column at the table floor, read as an affixed number: lane HX5's rule reaches it (its question holds it).

    MUTANT: `_LABEL_SIGNS` empty: `sign_label`, `sign_space_label`,
    `number_sign_alone` and `sign_on_a_few` (one cell in twenty signed)
    reach no arm.
    """
    assert asking._whole_numbers_each_on_one_row(records.cells_of(item), taxonomy.ROLE_AFFIXED)


def test_every_drawn_name_joined_to_a_record_number_is_held_whatever_its_share() -> None:
    """5,000 drawn cells of a name and a record number joined by one mark are each a name beside a record number.

    And a column holding one such cell among others is held by the forms'
    rule (`taxonomy.identifier_form_hold`). MUTANT:
    `_a_name_joined_to_a_number` returning False: every drawn cell is
    unread.
    """
    drawn = records.joined_names(SWEEP)
    unread = [cell for cell in drawn if taxonomy._forms_of_a_cell(cell)[0] != taxonomy.HELD_NAMES_WITH_NUMBERS]
    assert unread == []
    assert taxonomy.identifier_form_hold("label", ["plain text"] * 50 + [drawn[0]], frozenset()) == (
        taxonomy.HELD_NAMES_WITH_NUMBERS
    )


def test_cells_that_are_no_name_joined_to_a_record_number_are_not_held() -> None:
    """A code of four figures beside two words, one name and a number, a word with a figure, two numbers: none.

    Five figures beside a name are read since lane CZ-A2's repair 1 (LANE CZ-A2 RULINGS 4 (1)).
    """
    held = [cell for cell in records.not_joined_names(2_000)
            if taxonomy._forms_of_a_cell(cell)[0] == taxonomy.HELD_NAMES_WITH_NUMBERS]
    assert held == []


def test_every_drawn_record_number_beside_words_is_read_whole_or_held_by_its_form() -> None:
    """5,000 drawn record numbers of five figures or more beside words no label reader names (lane CZ-A2's repair 1).

    A name's parts and the number joined by a mark that parts fields (an
    empty part among them or after them, a flag after the number, small
    letters, the number first), a label after spaces and a mark or in
    brackets, a word after the number: each is either held by the forms'
    rule (`taxonomy.a_form_of_the_forms_rule`: a name joined to a record
    number keeps the Safe Harbor question), or read by
    `asking._a_whole_number_beside_words` with its figures whole AND a
    code of route two's register (`asking._a_register_of_codes`). On the
    base a391424c, one a row, these published 3,000 or 126 values and wrote
    18,000 or 19,999 real twin cells. One cell of several record numbers
    (`R100000;R100001`) is none, and a cell in square brackets is left to
    lane HX4's list question (`tests/test_privacy_unanswered_identifiers.py`'s
    lists in brackets). MUTANT: `_read_beside_words` returning None, or the
    register's beside-words branch off: red here.
    """
    unread = []
    for cell, figures in records.beside_words_spellings(SWEEP):
        if taxonomy.a_form_of_the_forms_rule(cell):
            continue
        found = asking._a_whole_number_beside_words(cell)
        # ...a record number in square brackets is lane HX4's list of one record number a cell, which its list
        # question holds (`[MR #1000013]` one a person: 0 values shown, 0 real cells at the lane's test size).
        listed = cell[:1] == "[" and cell[-1:] == "]"
        if found is None or found[1] != figures or asking._a_register_of_codes([cell]) == listed:
            unread += [(cell, figures, found)]
    assert unread == []


def test_no_unit_currency_date_or_few_figures_beside_a_label_is_read_beside_words() -> None:
    """A unit or a currency after the figures, a label before few figures, a decimal, a date, a telephone: none.

    HX5's line kept: true measurements are not asked (`12345 mg`,
    `12345 EUR`, `Weight 72.5 kg`, `Age 45`, `12345/min`); and a record
    number with one word after it (`185380;pending`) stays lane HX4's list
    question's (`tests/test_zoo_units_order.py`). A record number and a
    flag of one or two letters after it is read (`1000013,F`), one a row.
    MUTANT: the text after the number read whatever it holds: red here.
    """
    assert [cell for cell in records.NOT_BESIDE_WORDS if asking._a_whole_number_beside_words(cell) is not None] == []
    assert asking._a_whole_number_beside_words("1000013,F") == ("", "1000013", ",F")
    flagged = [f"{1_000_001 + row},{'FM'[row % 2]}" for row in range(records.ROWS)]
    assert asking._whole_numbers_each_on_one_row(flagged, taxonomy.ROLE_AFFIXED)


@pytest.mark.parametrize("item", ["label_spaced_mark", "label_spaced_dash", "label_in_brackets", "joined_empty_part",
                                  "joined_number_first_empty_after", "joined_underscore", "joined_five_figures",
                                  "joined_flag_after", "joined_small_letters"])
def test_a_record_number_beside_words_one_a_row_is_held_by_its_form_or_reached_by_the_each_on_one_row_rule(
    item: str,
) -> None:
    """Skeptic 1's spellings of items 1 and 2 (lane CZ-A2's repair 1), 20,000 cells, read as an affixed number.

    Each column is held by the forms' rule (a name joined to its record
    number, every empty part set aside: `joined_empty_part`,
    `joined_number_first_empty_after`) or reached by lane HX5's rule, whose
    open question holds it. On the base each published 126 or 3,000 values
    and wrote 19,999 or 18,000 real twin cells. MUTANT: `_read_beside_words`
    returning None: `joined_underscore`, `joined_five_figures`,
    `joined_flag_after` and `joined_small_letters` are reached by neither.
    """
    cells = records.cells_of(item)
    assert taxonomy.identifier_form_hold(records.COLUMN, cells, frozenset()) or (
        asking._whole_numbers_each_on_one_row(cells, taxonomy.ROLE_AFFIXED)
    )


@pytest.mark.parametrize("item", ["sign_label_one_a_person", "label_point_one_a_person", "label_slash_one_a_person",
                                  "label_hash_one_a_person", "number_sign_one_a_person",
                                  "label_spaced_mark_one_a_person", "label_in_brackets_one_a_person"])
def test_one_labelled_record_number_a_person_is_a_register_of_codes(item: str) -> None:
    """One record number a person beside its label, 1,000 people of 20 rows: route two's register of codes.

    The rule (lane CZ-A2, 2ecde461) that took `#MR`, `MR.`, `MR/`, `MR#`
    and `#` one a person from 20,000 real twin cells and 1,000 values shown
    to 0, and its repair's `MR #` and `(MR...)`: each column is a register
    of codes, so the person question is put and holds it. MUTANT (skeptic
    1, item 3): the register's labelled branch off -- `number_sign_one_a_person`
    is read by no other branch: red; both branches off: every item red.
    """
    assert asking._a_register_of_codes(records.cells_of(item))


def test_route_two_puts_its_question_on_labelled_record_numbers_one_a_person_and_not_on_codes_one_a_row() -> None:
    """Route two of the person rule on the five spellings one a person, and on a labelled five-figure code one a row.

    `#MR`, `MR.`, `MR/`, `MR#` and `#` before one record number a person
    (1,000 people of 20 rows): the person question is put (route two's
    register; LANE CZ-A2 RULINGS 4 (4)). A label and five figures each on
    one row, `Stage 2`, `Grade 3` and `Age 45` one a person: not by route
    two (each value on one row; few figures). MUTANT: the register's
    labelled branch off: `MR.` and `#` red (the others are read beside
    words too).
    """
    settings = taxonomy.Settings()
    rows = records.ROWS
    for item in ("sign_label_one_a_person", "label_point_one_a_person", "label_slash_one_a_person",
                 "label_hash_one_a_person", "number_sign_one_a_person"):
        assert asking._names_people_past_route_four(records.cells_of(item), taxonomy.ROLE_CATEGORICAL, rows,
                                                    settings), item
    one_a_row = [f"QD {10_000 + row}" for row in range(rows)]
    assert not asking._names_people_past_route_four(one_a_row, taxonomy.ROLE_CATEGORICAL, rows, settings)
    for word, figures in (("Stage", 4), ("Grade", 5), ("Age", 90)):
        cells = [f"{word} {1 + person % figures}" for person in range(1_000) for _row in range(records.ROWS_A_PERSON)]
        assert not asking._names_people_past_route_four(cells, taxonomy.ROLE_CATEGORICAL, rows, settings), word


def test_one_record_number_a_person_beside_words_is_a_register_and_few_figures_beside_a_label_are_not() -> None:
    """A name in small letters beside its record number, the number last or first, one a person: a register; `Stage 2` is not.

    Read by the register's beside-words branch alone: no label reader and
    not the forms' rule take them (their names are no capitalised words).
    The underscore, a flag after the number and five figures, one a person,
    are the forms' rule's since LANE CZ-A2 RULINGS 4 (1), held whatever their
    share. `Stage 2`, `Grade 3` and `Age 45` one a person hold few figures:
    no register (skeptic 1, item 3). MUTANT: the register's beside-words
    branch off: red here.
    """
    people = range(1_000)
    for make in (lambda person: f"cedar,{records.given_of(person).lower()},{1_000_000 + person}",
                 lambda person: f"{1_000_000 + person},cedar,{records.given_of(person).lower()}"):
        cells = [make(person) for person in people for _row in range(records.ROWS_A_PERSON)]
        assert not taxonomy.identifier_form_hold(records.COLUMN, cells, frozenset()), cells[0]
        assert asking._a_register_of_codes(cells), cells[0]
    for make in (lambda person: f"Cedar_{records.given_of(person)}_{1_000_000 + person}",
                 lambda person: f"Cedar,{records.given_of(person)},{1_000_000 + person},F",
                 lambda person: f"Cedar,{records.given_of(person)},{60_000 + person}"):
        cells = [make(person) for person in people for _row in range(records.ROWS_A_PERSON)]
        assert taxonomy.identifier_form_hold(records.COLUMN, cells, frozenset()) == taxonomy.HELD_NAMES_WITH_NUMBERS
    for word, figures in (("Stage", 4), ("Grade", 5), ("Age", 90)):
        cells = [f"{word} {1 + person % figures}" for person in people for _row in range(records.ROWS_A_PERSON)]
        assert not asking._a_register_of_codes(cells), cells[0]


def test_a_name_joined_to_a_record_number_keeps_the_forms_rule_and_its_safe_harbor_question() -> None:
    """The beside-words reading leaves a cell the forms' rule reads to that rule (lane CZ-A2's repair 1).

    `Cedar,Abc,1000013` one a row and one a person is held by the forms'
    rule (`taxonomy.identifier_form_hold`) and put the Safe Harbor question,
    as on the lane's build head; lane HX5's arm and route two's register do
    not read it, so their question does not come first. A blood-unit number
    with its check character one a person, held by its share, keeps its
    question too (the repair's price run measured the forms' `unit_ref` and
    `blood_unit` put the person question first without it). MUTANT: the arm or
    the register reading such a cell beside words
    (`taxonomy.a_form_of_the_forms_rule` not asked): red here.
    """
    one_a_row = records.cells_of("joined_by_commas")
    one_a_person = records.cells_of("joined_one_a_person")
    assert taxonomy.identifier_form_hold(records.COLUMN, one_a_row, frozenset()) == taxonomy.HELD_NAMES_WITH_NUMBERS
    assert asking._each_on_one_row_arm(one_a_row, False, records.COLUMN, True)[0] == ""
    assert not asking._a_register_of_codes(one_a_person)
    # ...and a blood-unit number, a form the rule holds by its share, one a person (the forms' `unit_ref`):
    # the register leaves it to that rule's question.
    units = [f"Q4012 {22 + person % 5} {100000 + person} {'X*0'[person % 3]}" for person in range(1_000)
             for _row in range(records.ROWS_A_PERSON)]
    assert taxonomy.identifier_form_hold(records.COLUMN, units, frozenset()) == taxonomy.HELD_UNIT_NUMBERS
    assert not asking._a_register_of_codes(units)


def test_a_one_word_label_s_run_left_free_by_its_exclusion_is_kept_off_the_real(tmp_path: pathlib.Path) -> None:
    """`MR` and five figures one a row, unanswered, 4,000 rows (a test size): no twin cell holds a real run whole.

    The layout's own exclusion writes the label out and leaves the run
    free, so the call site reads `taxonomy._a_run_left_free` and keeps the
    run off the real by its opening (lane CZ-A2, item 3; 4,447 such twin
    cells at 20,000 rows on the base). MUTANT (skeptic 1, item 4's
    call-site mutants): the reopening read for layouts of two words only
    (`_layout_words(layout) >= 2`): red here.
    """
    cells = [f"MR{10_000 + row}" for row in range(4_000)]
    table = tmp_path / "t.csv"
    with open(table, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["record_label"])
        writer.writerows([[cell] for cell in cells])
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace"], small_tables_refused=False) == 0
        assert cli.main(["generate", f"{tmp_path / 't-profile.json'}", "--out-dir", f"{tmp_path}", "--seed", "0",
                         "--replace"], small_tables_refused=False) == 0
    with open(tmp_path / "t-twin.csv", encoding="utf-8", newline="") as handle:
        twin = [row[0] for row in list(csv.reader(handle))[1:]]
    real = set(cells)
    assert sum(1 for cell in twin if cell in real) == 0
    assert records.complete_runs(cells, twin) == 0


def test_a_joined_name_is_read_up_to_its_longest_and_no_longer() -> None:
    """A name joined to its record number is read at 160 characters and not at 161 (`taxonomy._JOINED_NAME_LONGEST`).

    So a note of free text is never walked whole. MUTANT (skeptic 1, item
    6 (c)): the bound removed: the 161-character cell is read: red here.
    """
    def joined(length: int) -> str:
        return f"Cedar,A{'b' * (length - len('Cedar,,1000013') - 1)},1000013"

    assert taxonomy._JOINED_NAME_LONGEST == 160
    assert len(joined(160)) == 160 and taxonomy._a_name_joined_to_a_number(joined(160))
    assert len(joined(161)) == 161 and not taxonomy._a_name_joined_to_a_number(joined(161))


def test_an_exclusion_opening_another_layout_s_real_runs_is_written_off_them(tmp_path: pathlib.Path) -> None:
    """A declared column of `#MR` and seven figures beside `#9` and six (a quarter of its rows), 4,000 rows (a test size).

    `taxonomy._an_opening_held` reads that the `#MR` layout's own exclusion
    (`#@@9%%%%%%`) opens its run as the other layout's real runs open, so
    the run is kept off them by an opening no real run of its width holds:
    no twin cell holds a real `#9...` run, none is real. Measured on the
    lane's build head at this size: 6 twin cells holding a complete real
    run. The 20,000-row reading is K-HZ-22's driver's (`two_layouts_declared`).
    MUTANT (skeptic 1, item 4): `_an_opening_held` returning False: red here.
    """
    assert taxonomy._an_opening_held(["#@@9%%%%%%"], [(3, 7)], {7: {"9": 1000, "1": 3000}}, [])
    assert not taxonomy._an_opening_held(["#@@8%%%%%%"], [(3, 7)], {7: {"9": 1000, "1": 3000}}, [])
    assert not taxonomy._an_opening_held(["Z@%%%%%%%"], [(2, 7)], {7: {"9": 1000}}, [])
    cells = [f"#{9_000_000 + row}" if row % 4 == 0 else f"#MR{1_000_001 + row}" for row in range(4_000)]
    table = tmp_path / "t.csv"
    with open(table, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["record_label"])
        writer.writerows([[cell] for cell in cells])
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace", "--identifier",
                         "record_label"], small_tables_refused=False) == 0
        assert cli.main(["generate", f"{tmp_path / 't-profile.json'}", "--out-dir", f"{tmp_path}", "--seed", "0",
                         "--replace"], small_tables_refused=False) == 0
    block = json.loads((tmp_path / "t-profile.json").read_text(encoding="utf-8"))["columns"][0]
    assert block["layout_prefixes"].get("#@@%%%%%%%") == "#MR"
    assert not block["layout_exclusions"]["#@@%%%%%%%"].startswith("#@@9")
    with open(tmp_path / "t-twin.csv", encoding="utf-8", newline="") as handle:
        twin = [row[0] for row in list(csv.reader(handle))[1:]]
    real = set(cells)
    assert sum(1 for cell in twin if cell in real) == 0
    assert records.complete_runs(cells, twin) == 0


def test_a_one_word_code_reaches_its_run_and_a_number_in_exponent_form_does_not() -> None:
    """5,000 drawn one-word codes: a label or capitals beside a run of five figures or more reach the run.

    Each drawn spelling's layout (`parsing.layout_form`) names its run in
    `taxonomy.inner_runs`, so the exclusion keeps it off the real by its
    opening; a number a spreadsheet displays in exponent form
    (`5.07906E+11`, `1.71457E+09`, `1E+11`) is one key, as is a run of
    figures alone. MUTANT: `inner_runs` reading one-word layouts as before
    (no run): every drawn code is unread; `_a_label_beside_figures` taking
    the exponent's letter for a label: the exponent forms read runs.
    """
    from synthtwin import parsing

    unread = []
    for cell, figures in records.label_spellings(SWEEP):
        layout = parsing.layout_form(cell.replace(" ", ""), parsing.LAYOUT_PLAIN)
        if len(figures) >= 5 and any(mark in "@&" for mark in layout) and not taxonomy.inner_runs(layout):
            unread += [cell]
    assert unread == []
    for cell in ("S24-012345", "24S-100000", "ZQ-90-698113", "S-24-012345", "MR1000013A", "BLK00012345X"):
        assert taxonomy.inner_runs(parsing.layout_form(cell, parsing.LAYOUT_PLAIN)), cell
    for cell in ("5.07906E+11", "1.71457E+09", "1E+11", "6.02e23", "1000013", "00012345"):
        assert taxonomy.inner_runs(parsing.layout_form(cell, parsing.LAYOUT_PLAIN)) == [], cell


def test_a_one_word_exclusion_written_inside_its_run_stands_and_one_left_free_is_opened() -> None:
    """The narrowest rule: a one-word layout's run is opened only where its own exclusion leaves the run free.

    `ZM1004715` beside a real `MR1004715`: the label written out, the run
    free (`Z@%%%%%%%`); an accession's year written, its sequence free
    (`9%@-%%%%%%`). A declared record number's exclusion after its
    published prefix (`@@9%%%%%%`) and a block inside a run (`&&9%9%9`)
    write inside the run and stand byte for byte. MUTANT: `_a_run_left_free`
    returning True (the broader rule R4): the landing's `REC` and seven
    figures beside `E` and six is written as the spill
    (`tests/test_landing_2b18_identifier_layout.py`), and the rsID shapes'
    exclusions write neighbouring figures (`tests/test_identifier_room.py`).
    """
    assert taxonomy._a_run_left_free(["Z@%%%%%%%"], "@@%%%%%%%", [(2, 7)])
    assert taxonomy._a_run_left_free(["9%@-%%%%%%"], "%%@-%%%%%%", [(4, 6)])
    assert taxonomy._a_run_left_free(["@@9%%%%%%", "Z@%%%%%%%"], "@@%%%%%%%", [(2, 7)])
    assert not taxonomy._a_run_left_free(["@@9%%%%%%"], "@@%%%%%%%", [(2, 7)])
    assert not taxonomy._a_run_left_free(["&&9%9%9"], "&&%%%%%", [(2, 5)])


class _Forgetful(dict):  # type: ignore[type-arg]
    """A memo that keeps nothing: the walk as it ran before lane CZ-A2."""

    def __setitem__(self, key: object, value: object) -> None:
        return None


def _generate_names(folder: pathlib.Path, rows: int, forget: bool, monkeypatch: pytest.MonkeyPatch) -> "tuple[bytes, int]":
    """A held name column with no layout through the library at ``rows``: the twin's bytes and the fillings read."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "t.csv"
    with open(table, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["label"])
        writer.writerows([[f"O'Cedar, {records.given_of(row * 1000 // rows)} [MR{1000000 + row}]"]
                          for row in range(rows)])
    reads = [0]
    worn = generation._wears_template

    def counted(*arguments: object, **options: object) -> bool:
        reads[0] += 1
        return worn(*arguments, **options)  # type: ignore[arg-type]

    room = generation._off_the_real_room

    def without_memo(*arguments: object, **options: object) -> object:
        return dataclasses.replace(room(*arguments, **options), unread=_Forgetful())  # type: ignore[arg-type]

    with monkeypatch.context() as patched:
        patched.setattr(generation, "_wears_template", counted)
        if forget:
            patched.setattr(generation, "_off_the_real_room", without_memo)
        with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            assert cli.main(["profile", f"{table}", "--out-dir", f"{folder}", "--replace"],
                            small_tables_refused=False) == 0
            assert cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir", f"{folder}", "--seed", "0",
                             "--replace"], small_tables_refused=False) == 0
    return (folder / "t-twin.csv").read_bytes(), reads[0]


def test_a_value_no_layout_describes_is_searched_once_a_class_and_the_twin_keeps_its_bytes(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A held name column with no layout (an apostrophe in the family name), 3,000 rows (a test size): the same bytes.

    With the search remembered as unread (`generation._next_off_the_real`)
    the walk reads at most two searches' fillings; without it, 45,056 at
    3,000 rows (each member of a merged identity searched the spill's
    4,096 fillings again). The twin's bytes are the same either way. The
    seconds at 20,000 and 200,000 rows are decision P4-D469's item (7),
    measured by the lane's build through the command on five tables and
    re-run by its statistics check (K-HZ-22's driver times its fixed
    20,000-row identifier items, not this column alone; Codex's item 7).
    """
    remembered, reads = _generate_names(tmp_path / "on", 3_000, False, monkeypatch)
    forgotten, reads_before = _generate_names(tmp_path / "off", 3_000, True, monkeypatch)
    assert remembered == forgotten
    assert reads <= 2 * generation._OFF_THE_REAL_TRIES < reads_before


# The twelve band heads, written out (lane CZ-A2's repair 1, its skeptic's
# item 5 (b)): the digits band opens a whole number longer than one figure
# with no nought; the code band opens with a letter or an underscore; the
# wide band with a mark; none with a space or a character a spreadsheet
# reads as the start of a formula.
_DIGITS_HEAD = "0123456789"
_CODE_HEAD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz"
_WIDE_HEAD = "!\"#$%&'()*,./:;<>?[\\]^`{|}~"
_BAND_HEADS_WRITTEN = {
    (band, whole, longer): head
    for band, head in (("digits", _DIGITS_HEAD), ("code", _CODE_HEAD), ("wide", _WIDE_HEAD))
    for whole in (False, True)
    for longer in (False, True)
}
_BAND_HEADS_WRITTEN[("digits", True, True)] = "123456789"


def test_the_walk_s_band_heads_written_once_are_the_sets_each_draw_read() -> None:
    """`generation._band_head` reads its twelve sets off `_BAND_HEADS`, each the set written out above.

    The same sets, so the same bytes (the case above holds a twin's bytes
    whole); a band no table names is still read off its alphabet. MUTANT:
    a set of `_BAND_HEADS` with one character fewer, or `_band_head_written`
    keeping the nought before a whole number longer than one figure (the
    nought rule flipped): red here, since each set is compared with its
    letters written out, not with the function that writes it.
    """
    assert generation._BAND_DIGITS == "digits" and generation._BAND_CODE == "code" and generation._BAND_WIDE == "wide"
    for band in (generation._BAND_DIGITS, generation._BAND_CODE, generation._BAND_WIDE):
        for whole in (False, True):
            for length in (1, 2, 7):
                written = _BAND_HEADS_WRITTEN[(band, whole, length > 1)]
                assert "".join(generation._band_head(band, whole, length)) == written, (band, whole, length)
                assert "".join(generation._band_head_written(band, whole, length > 1)) == written, (band, whole)
    assert len(generation._BAND_HEADS) == 12
    assert generation._band_head("unnamed", True, 2) == generation._band_head_written("unnamed", True, True)


def _a_bare_room() -> "generation._OffTheReal":
    """A room of the walk over no description: no template, no hole, every merged key kept off the real."""
    return generation._OffTheReal(
        facts=None, holes=(), convention=parsing.LAYOUT_PLAIN, whole="", whole_places=False,  # type: ignore[arg-type]
        templates={}, lowered={}, stands={}, spill="", bound=1, written={}, folds={}, merged={}, numbers={},
        steps={}, missed={}, widened={}, lengths={"letters": {}, "figures": {}}, sharing={}, nought_led={},
        spends={}, unread={},
    )


def test_a_search_whose_filling_read_as_its_class_is_never_remembered_as_unread() -> None:
    """A strict search refused only by an identity a member may share runs again once it shares.

    Every filling of the template `%%` reads as the value's class (figures,
    whole) and is refused by `generation._identity_taken` alone, every
    merged key taken: the search finds nothing, and since a filling was
    classed it is NOT recorded in `room.unread` (its end is no property of
    its class). Once the member shares those keys (`room.sharing`), the
    same search from the same step finds a filling. A search no filling of
    which reads as its value's class (a value of letters) is recorded and
    gives its step back. MUTANT (lane CZ-A2's skeptic 1, item 5 (a)): the
    search recorded as unread whether or not a filling was classed -- the
    second search returns nothing: red here.
    """
    template = "%%"
    keys = {parsing.merged_key(generation._filled_layout(template, step)) for step in range(parsing.layout_room(template))}
    room = _a_bare_room()
    room.merged.update({key: True for key in keys})
    parts = [("", "12", "", "12")]
    assert generation._next_off_the_real(room, template, parts, True) is None
    assert room.unread == {}
    room.sharing.update({"k|" + key: True for key in keys})
    found = generation._next_off_the_real(room, template, parts, True)
    assert found is not None and found["12"] != "12"
    letters = _a_bare_room()
    assert generation._next_off_the_real(letters, template, [("", "ab", "", "ab")], True) is None
    assert len(letters.unread) == 1


# -- lane CZ-A2's repair 2 (its verify's items 1 to 6 and Codex's items 1 to 5) --------------------------------------

# Each generated column is read at a test size by the readers alone, the
# person rule's ceiling read at the table floor's 20,000 rows (THE SUITE'S
# TIME rule: the 20,000-row readings are K-HZ-22's driver's items).
SWEEP_ROWS = 600


def test_every_space_and_dash_beside_the_lane_s_spellings_is_read_as_its_plain_mark() -> None:
    """756 generated columns: 42 spaces and dashes in nine places of a label or a joined name, one a row and one a person.

    Each is held by the forms' rule, reached by lane HX5's arm or asked by
    route two (`labelled_records.held_by_a_reader`): every reader of the
    lane reads the product's one definition of a space and a dash
    (`taxonomy.with_plain_marks`). On repair 1's head 44 were held by none
    -- a minus sign (U+2212) before the number of a label, a signed label
    or a joined name, and the zero-width characters and the dashes after a
    number written first -- each published at 20,000 rows (1,000 values and
    20,000 real twin cells one a person; 18,000 real twin cells and 1,998
    complete runs one a row, the verify's runs). The dash set is the marks
    of `taxonomy._SSN_MARKS` that are no space, held equal here. MUTANT:
    `with_plain_marks` returning its text: red here (44).
    """
    unheld = [label for label, cells, one_a_person in records.spaced_columns(SWEEP_ROWS)
              if not records.held_by_a_reader(cells, one_a_person)]
    assert unheld == []
    assert set(taxonomy._SCREEN_DASHES) == {
        mark for mark in taxonomy._SSN_MARKS if not taxonomy._a_space_of_the_screen(mark)
    }
    assert taxonomy.with_plain_marks("MR\u22121000013") == "MR-1000013"
    assert taxonomy.with_plain_marks("1000013\u200b,Cedar\tAbc") == "1000013,Cedar\tAbc"


def test_the_plain_reading_is_the_product_s_one_definition_of_a_space_and_a_dash_over_every_code_point() -> None:
    """THE GENERATED AGREEMENT CASE OF BATCH 4s'S MERGE OF LANE CZ-A2 (step 7; LANE CZ-A2 RULINGS 10 (4) and 11 (3)).

    Over all 1,114,112 code points the plain reading (`taxonomy.with_plain_marks`) writes `-` for
    exactly the dashes of the word screen's one definition (`taxonomy._SCREEN_DASHES`) and the soft
    hyphen, sets aside exactly the spaces that print nothing (`taxonomy._prints_nothing`) but the soft
    hyphen, writes ` ` for exactly the other spaces of the definition (`taxonomy._a_space_of_the_screen`)
    but the tab, and keeps the tab and every other character as written; an ASCII cell is read so by
    the short road too. The soft hyphen is read both ways (`taxonomy.plain_readings`), and a cell either
    reading holds is held: `MR100` and a soft hyphen before ` 0013`, and `MR` and a soft hyphen before
    `100 0013`, one a person, are two groups of figures only with it set aside, held by no reader on the
    merge's first commit. The lane's three lists before the merge, written out here, lie inside, and the
    dashes are the marks of `taxonomy._SSN_MARKS` that are no space. The two-groups reading takes ONE
    space of the definition: each space a display draws between `MR100` and `0013` is read in two
    groups, and with each space that prints nothing the cell is the labelled record number `MR1000013`.
    MUTANTS (batch 4s's merge, step 7): the lane's lists before the merge; the soft hyphen read only as a
    dash; the horizontal bar out of the dashes; the information separators read as written; the spaces
    that print nothing written ` `: each red here.
    """
    soft = "\u00ad"
    dashes = frozenset(taxonomy._SCREEN_DASHES)
    every = [chr(code) for code in range(0x110000)]
    spaces = [character for character in every if taxonomy._a_space_of_the_screen(character)]
    silent = frozenset(character for character in spaces if taxonomy._prints_nothing(character))

    def plain(character: str) -> str:
        if character in dashes or character == soft:
            return "-"
        if character in silent:
            return ""
        if character != "\t" and taxonomy._a_space_of_the_screen(character):
            return " "
        return character

    assert taxonomy.with_plain_marks("".join(every)) == "".join(plain(character) for character in every)
    for character in every[:128]:
        assert taxonomy.with_plain_marks("A" + character + "B") == "A" + plain(character) + "B", hex(ord(character))
    old_spaces = (
        "\t\n\r\x0b\x0c\x85\u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005"
        "\u2006\u2007\u2008\u2009\u200a\u200b\u200c\u200d\u200e\u200f\u2028"
        "\u2029\u202f\u205f\u2060\u3000\ufeff"
    )
    old_no_width = "\u200b\u200c\u200d\u200e\u200f\u2060\ufeff"
    old_dashes = "-\u2013\u2014\u2010\u2011\u2012\u2212\ufe63\uff0d\u2015\ufe58\u00ad"
    assert set(old_no_width) <= silent
    assert all(mark in spaces and mark not in silent for mark in old_spaces if mark not in old_no_width)
    assert set(old_dashes) == dashes | {soft}
    assert dashes == {mark for mark in taxonomy._SSN_MARKS if not taxonomy._a_space_of_the_screen(mark)}
    assert (len(spaces), len(silent), len(dashes)) == (2474, 2445, 11)
    assert taxonomy.plain_readings("MR100" + soft + " 0013") == ("MR100- 0013", "MR100 0013")
    assert taxonomy.plain_readings("MR100 0013") == ("MR100 0013",)
    for character in spaces:
        if character == soft:
            continue
        cell = "MR100" + character + "0013"
        if character in silent:
            assert asking._record_number_groups(cell) is None, hex(ord(character))
            assert asking._a_whole_number_after_letters(cell) == ("MR", "1000013", ""), hex(ord(character))
        else:
            assert asking._record_number_groups(cell) == ("MR", "100", "0013"), hex(ord(character))
    for spelled in ("MR{0}" + soft + " {1}", "MR" + soft + "{0} {1}"):
        cells: "list[str]" = []
        for row in range(SWEEP_ROWS):
            figures = str(100_000 + row // records.ROWS_A_PERSON)
            cells += [spelled.format(figures[:3], figures[3:])]
        assert records.held_by_a_reader(cells, True), ascii(cells[0])


def test_a_dash_or_a_zero_width_space_beside_a_joined_number_is_set_aside_by_both_readers() -> None:
    """A dash before the number or after a number written first, read by the forms' rule and the beside-words reader.

    The forms' rule sets every space and dash aside at either end of a
    joined name's part (`taxonomy._a_part_trimmed`), so a capitalised name
    keeps the Safe Harbor question; the beside-words reader sets them
    aside at the head of the text after a number written first
    (`asking._a_name_or_a_flag_after`), so a name in small letters, which
    the forms' rule does not read, is a record number beside words. MUTANTS:
    either set kept to the space alone: red here.
    """
    for cell in ("Cedar,Abc,\u22121000013", "1000013\u2013,Cedar,Abc", "1000013\u200b,Cedar,Abc",
                 "Cedar,Abc,1000013\u2014"):
        assert taxonomy._forms_of_a_cell(cell)[0] == taxonomy.HELD_NAMES_WITH_NUMBERS, cell
    for cell in ("1000013\u2013,cedar,abc", "1000013\u2212,cedar,abc", "1000013\ufe58^cedar^abc"):
        found = asking._a_whole_number_beside_words(cell)
        assert found is not None and found[1] == "1000013", cell


def test_every_spelling_the_lane_holds_is_held_with_a_space_or_a_dash_wherever_its_plain_spelling_is() -> None:
    """2,100 generated columns: 25 spellings of the class, each space, dash or joint written with each of 42 marks, both layouts.

    Each column is held by a reader wherever its plain spelling is (each
    dash written `-`, each mark of no width set aside, each other space
    written ` `, the tab kept: `labelled_records.plain_mark`, written out
    in the test, not read from the product): the readers of a label, a
    joined name and a record number beside words, AND the forms' rule's
    name beside a bracketed record number (`taxonomy._a_name_beside_a_number`
    and its caller's look for the bracket), which on repair 2's first code
    read a zero-width space after the comma, a zero-width space or a dash
    before the bracket and a zero-width space after it as no reader did:
    `Cedar,\u200bAbc (1000013)` was held by none where `Cedar,Abc (1000013)`
    is held. MUTANTS: `with_plain_marks` returning its text, and the
    bracketed reader reading the cell as written: red here.
    """
    plain_held: "dict[int, bool]" = {}
    escapes: "list[str]" = []
    for label, cells, plain, one_a_person in records.plain_mark_columns(SWEEP_ROWS):
        if id(plain) not in plain_held:
            plain_held[id(plain)] = bool(records.held_by_a_reader(plain, one_a_person))
        if plain_held[id(plain)] and not records.held_by_a_reader(cells, one_a_person):
            escapes += [label]
    assert escapes == []
    for cell in ("Cedar,\u200bAbc (1000013)", "Cedar, Abc\u200b(1000013)", "Cedar, Abc\u2013(1000013)",
                 "Cedar, Abc (1000013)\u200b", "Cedar,\u2060Abc #1000013"):
        assert taxonomy._forms_of_a_cell(cell)[0] == taxonomy.HELD_NAMES_WITH_NUMBERS, ascii(cell)


def test_a_name_beside_a_bracketed_number_and_a_number_sign_hold_each_mark_in_each_place() -> None:
    """1,596 generated columns: nineteen places of the bracketed form, a number sign alone and labels, each of 42 marks, both layouts.

    Each column is held (LANE CZ-A2 RULINGS 5 (3): any of the marks in any
    position), as the verify's set holds the joined names: the bracketed
    reader sets the spaces and dashes aside at either end of the cell, of
    each part of the name and of the record number (`taxonomy._a_part_trimmed`
    in `_a_name_beside_a_number` and `_a_name_before`), and the label reader
    reads a number sign, a dash and the figures with the dash as a mark and
    sets aside the spaces and dashes after a label's figures
    (`asking._a_labelled_number`). Measured at 20,000 rows before:
    `Cedar,-Abc (1000000)` one a row 3,000 values shown, 18,000 real twin
    cells and 1,998 complete runs, one a person 1,000 and 20,000; `#-1000000`
    one a person 1,000 values and 20,000 real twin cells, one a row 19,999
    real twin cells; at the unit level `#1000013 ` and `MR.1000013 ` (a space
    after the figures) were held by no reader. MUTANTS: the name's parts or
    the bracket's number read with their dashes, the look for the bracket
    without them set aside, the number sign's dash read as a minus sign, or
    the marks after the figures kept: red here. The follow-up of lane CZ-A2
    (LANE CZ-A2 RULINGS 9 (2)) adds the places of a labelled record number
    the set lacked: between the label and the figures, at the head and at
    both ends (`MR` + a mark + seven figures, a mark + `MR` + seven figures,
    the mark on both sides), each held on 8b28950b and here; the mark
    inside the figures is a set of its own (below).
    """
    unheld = [label for label, cells, one_a_person in records.every_mark_columns(SWEEP_ROWS)
              if not records.held_by_a_reader(cells, one_a_person)]
    assert unheld == []
    assert asking._a_whole_number_after_letters("#\u22121000013") == ("#-", "1000013", "")
    assert asking._a_whole_number_after_letters("#1000013 ") == ("#", "1000013", "")
    assert asking._a_whole_number_after_letters("MR.1000013\u2013") == ("MR.", "1000013", "")
    for cell in ("Cedar,-Abc (1000013)", "Cedar\u2013, Abc (1000013)", "Cedar, Abc (\u22121000013)",
                 "Cedar, Abc (1000013)-", "Cedar, Abc #-1000013"):
        assert taxonomy._forms_of_a_cell(cell)[0] == taxonomy.HELD_NAMES_WITH_NUMBERS, ascii(cell)


def test_a_mark_inside_a_labelled_record_number_s_figures_is_read_as_its_plain_spelling() -> None:
    """504 generated columns: each of 42 marks after each of the first six figures of `MR` and seven, both layouts.

    LANE CZ-A2 RULINGS 9 (2) (its verify 2's C1): `MR100` + a soft hyphen +
    `0000`, one a person at 1,000 people of 20 rows, was read as labels and
    published 1,000 values and 20,000 real twin cells at 20,000 rows on
    8b28950b: route two's register read the code alphabet on the cell as
    written. It reads it on the cell read plain (`taxonomy.with_plain_marks`),
    so each column is held wherever its plain spelling is (each dash written
    `-`, each mark of no width set aside, each other space ` `, the tab
    kept): on 8b28950b 22 were held by no reader, the eleven dashes after
    the third or the fourth figure one a person. A dash after the third or
    the fourth figure one a row leaves groups of fewer than five figures
    that no reader reads in their plain spelling either (22 columns; the
    command reads such a column as free text, which publishes nothing). A
    space after the second, third or fourth figure, both layouts, was so
    too on 8b28950b and 7894ddbd (142 columns, one a person the record
    numbers published) and is read in two groups since lane CZ-A2's
    follow-up 4 (`asking._record_number_groups`; the generated set below).
    MUTANT: the register's code-text test reading the cell as written: red
    here.
    """
    escapes: "list[str]" = []
    plain_held: "dict[int, bool]" = {}
    for label, cells, plain, one_a_person in records.inside_the_figures_columns(SWEEP_ROWS):
        if id(plain) not in plain_held:
            plain_held[id(plain)] = bool(records.held_by_a_reader(plain, one_a_person))
        if plain_held[id(plain)] and not records.held_by_a_reader(cells, one_a_person):
            escapes += [label]
    assert escapes == []
    soft = records.cells_of("label_soft_hyphen_inside_one_a_person", SWEEP_ROWS)
    assert soft[0] == "MR100\u00ad0000" and asking._a_register_of_codes(soft)


def test_a_labelled_record_number_in_two_groups_of_figures_is_held_with_every_space_of_the_definition() -> None:
    """896 generated columns: a label of one or two letters, six or seven figures in two groups, each of 32 spaces, both layouts.

    LANE CZ-A2 RULINGS 10 (2): `MR100 0013` and `MR1000 013`, the groups
    parted by a plain, a no-break or a thin space or a tab, one a person at
    1,000 people of 20 rows, were read as labels and published 1,000 values
    and wrote 20,000 real twin cells at 20,000 rows on 7894ddbd, as on the
    public head; and one a row `MR100 000` (six figures in groups of three)
    was read as an affixed number and wrote 19,999 real twin cells. Route
    two's register key and lane HX5's arm read the two groups as one record
    number where the shape says one (`asking._record_number_groups`: letters,
    each group two figures or more, six or more in all, one space of the one
    definition), so each column is held by a reader: every split of six and
    seven figures that leaves both groups two figures or more, after the
    plain space and each space of `labelled_records.SPACES_AND_DASHES`. On
    7894ddbd 596 of the 896 were held by none, 298 of each layout. And the
    label as the label reader reads it: a sign before it, the spaces and
    dashes at either end set aside, letters of any script (Greek, Cyrillic,
    Han): each such column held, both layouts. MUTANTS: the register's
    two-groups branch off (one a person red), the arm's off (one a row red),
    the ends kept, the letters ASCII alone, the sign refused (each red).
    """
    unheld = [label for label, cells, one_a_person in records.two_group_columns(SWEEP_ROWS)
              if not records.held_by_a_reader(cells, one_a_person)]
    assert unheld == []
    assert asking._record_number_groups("MR100\u20090013") == ("MR", "100", "0013")
    assert asking._record_number_groups("m10\t0013") == ("M", "10", "0013")
    for opening, closing in (("#MR", ""), ("* MR", ""), ("MR", " "), (" MR", ""), ("MR", "\u2013"),
                             ("\u039c\u03a1", ""), ("\u041c\u0420", ""), ("\u60a3\u8005", "")):
        for one_a_person in (False, True):
            cells = [f"{opening}{str(100_000 + unit)[:3]} {str(100_000 + unit)[3:]}{closing}"
                     for unit in (row // records.ROWS_A_PERSON if one_a_person else row for row in range(SWEEP_ROWS))]
            assert records.held_by_a_reader(cells, one_a_person), ascii(cells[0])
    assert asking._record_number_groups("* MR100 0013 ") == ("* MR", "100", "0013")


def test_no_period_version_or_group_of_one_figure_is_read_as_a_record_number_in_two_groups() -> None:
    """The near-miss controls: fiscal quarters, fiscal years, versions, weeks, months and thousands repeating; a group of one figure.

    Each repeating control is put no question by route two, as on 7894ddbd
    (its description unchanged at 20,000 rows, P4-D469): a quarter
    (`Q3 2024`) holds a group of one figure, a short version (`v10 12`) and
    a short fiscal year (`FY23 24`) four figures in all, figures parted by
    a space between thousands (`100 000`) no label, and a column every
    two-group cell of which is a year beside two figures or a second year
    is a column of periods (`asking._periods_in_two_groups`: `W23 2024`,
    `FY2023 24`, `FY2023 2024`, `v2023 10`, `M12 2024`). No cell of a group
    of one figure (`MR1 000013`, `MR100001 3`, one a person) is read in two
    groups, nor two spaces between the groups, a sign with no letters, or a
    currency sign. MUTANTS: the periods not read, the least figures of a
    group lowered to one, the least in all to four, and no label asked: red
    here.
    """
    for name, levels in records.NEAR_MISS_CONTROLS.items():
        cells = [levels[row % len(levels)] for row in range(SWEEP_ROWS)]
        assert not records.held_by_a_reader(cells, True), name
    for where, cells in records.ONE_FIGURE_GROUPS.items():
        assert [cell for cell in cells if asking._record_number_groups(cell) is not None] == [], where
    for cell in ("MR10 001", "MR100 0013A", "MR100  0013", "MR100 00 13", "MR 100 0013", "#100 0013",
                 "€12 345678", "ABCDEFGHIJKLM10 0013", "MR100-0013"):
        assert asking._record_number_groups(cell) is None, ascii(cell)


def test_a_label_of_a_script_with_no_capital_beside_a_record_number_is_read() -> None:
    """Two Han characters, an Arabic, a Hebrew and a Devanagari word before seven figures, one a row and one a person.

    Each column is held, as on repair 1's head, though the offline audit
    admits no table of letters (`asking._a_letter_of_any_script`: a capital
    and a small form, or a letter of a script with no capital read by its
    range); a currency or degree sign before five figures stays unread.
    AND (lane CZ-A2's follow-up, LANE CZ-A2 RULINGS 9 (2)) two letters of
    Ethiopic, Khmer, Lao, Tibetan, Myanmar, Mongolian and the Canadian
    syllabics, each held by no reader on 8b28950b, either layout (the
    Ethiopic label one a person: 1,000 values shown and 20,000 real twin
    cells at 20,000 rows; one a row: 126 runs shown and 19,999 real twin
    cells). MUTANTS: the scripts with no capital not read (`_UNCASED_LETTERS`
    empty), or the ranges back to repair 2's twelve: red here.
    """
    for label in ("\u60a3\u8005", "\u0631\u0642\u0645", "\u05de\u05e1", "\u0930\u094b\u0917\u0940",
                  "\u1200\u1208", "\u1780\u1781", "\u0e81\u0e82", "\u0f40\u0f41", "\u1000\u1001",
                  "\u1820\u1821", "\u1401\u1403"):
        one_a_row = [f"{label}{1_000_000 + row}" for row in range(SWEEP_ROWS)]
        one_a_person = [f"{label}{1_000_000 + row // records.ROWS_A_PERSON}" for row in range(SWEEP_ROWS)]
        assert records.held_by_a_reader(one_a_row, False), label
        assert records.held_by_a_reader(one_a_person, True), label
    for cell in ("\u20ac12345", "\u20ac 12345", "\u00a312345", "\u00b0 12345"):
        assert asking._a_whole_number_beside_words(cell) is None, cell


def test_every_letter_of_no_case_lies_in_a_range_of_the_scripts_with_no_capital() -> None:
    """Every letter of no case of the running Python's Unicode lies in a range of `asking._UNCASED_LETTERS`.

    The expectation is read from `unicodedata` here, never from the ranges
    (LANE CZ-A2 RULINGS 9 (2)): every character of the categories Lo and Lm
    whose small and capital forms are one. On repair 2's head, twelve
    ranges, 87,240 of the 127,667 letters of no case of Unicode 14.0 lay
    outside them, in 447 runs -- Syriac, Thaana, N'Ko, Ethiopic, Tifinagh,
    Vai, Bamum, Lao, Tibetan, Myanmar, Khmer, Mongolian, the Canadian
    syllabics, Yi, Bopomofo, the modifier letters and every ideograph past
    U+FFFF among them -- and an Ethiopic label before seven figures, one a
    person at 1,000 people of 20 rows, published 1,000 values and wrote
    20,000 real twin cells at 20,000 rows. The ranges stand sorted and apart
    (the reader stops at the first range above a character), the reader
    reads the first and the last character of each range as a letter, and
    the character after each range as none unless it has a case. MUTANTS:
    the ranges back to repair 2's twelve, or any range dropped: red here,
    naming the letters left out.
    """
    ranges = [(ord(lowest), ord(highest)) for lowest, highest in asking._UNCASED_LETTERS]
    assert all(lowest <= highest for lowest, highest in ranges)
    assert all(ranges[place][1] + 1 < ranges[place + 1][0] for place in range(len(ranges) - 1))
    starts = [lowest for lowest, _highest in ranges]
    outside: "list[int]" = []
    for code in range(0x110000):
        if 0xD800 <= code <= 0xDFFF:
            continue
        character = chr(code)
        if unicodedata.category(character) not in ("Lo", "Lm") or character.lower() != character.upper():
            continue
        place = bisect.bisect_right(starts, code) - 1
        if place < 0 or code > ranges[place][1]:
            outside += [code]
    runs: "list[list[int]]" = []
    for code in outside:
        if runs and code == runs[-1][1] + 1:
            runs[-1][1] = code
        else:
            runs += [[code, code]]
    assert runs == [], (unicodedata.unidata_version, len(outside), [
        f"U+{low:04X} to U+{high:04X} {unicodedata.name(chr(low), '')}" for low, high in runs[:40]])
    for lowest, highest in asking._UNCASED_LETTERS:
        assert asking._a_letter_of_any_script(lowest) and asking._a_letter_of_any_script(highest), ascii(lowest)
        after = chr(ord(highest) + 1)
        if after.lower() == after.upper():
            assert not asking._a_letter_of_any_script(after), ascii(after)


def test_every_pair_of_identifier_families_in_one_column_is_held_or_asked() -> None:
    """924 generated columns: every pair of twelve identifier families at seven shares, one a row and one a person.

    The lane's labelled and joined families and every form of the forms'
    rule (social security and beneficiary numbers, tokens, accessions,
    blood-unit numbers, fifteen and sixteen figures), each pair at 5 to 95
    per cent of the column: each is held by the forms' rule, reached by
    lane HX5's arm or asked by route two. On repair 1's head 64 were held by
    none, every one beside a blood-unit or a fifteen-figure family: a cell
    the forms' rule read was left to it although the rule did not hold the
    column (Codex's item 1: `#MR` beside blood-unit numbers, half each,
    published 1,000 record numbers and wrote 20,000 real twin cells).
    MUTANT: `asking._forms_hold_the_column` read as true (the cell left to
    the rule whatever the column): red here.
    """
    unheld = [label for label, cells, one_a_person in records.mixed_columns(SWEEP_ROWS)
              if not records.held_by_a_reader(cells, one_a_person)]
    assert unheld == []


def test_a_word_or_a_placeholder_beside_the_lane_s_holds_never_defeats_them() -> None:
    """1,836 generated columns: seventeen forms of the lane's holds beside 27 set-aside spellings, two shares, both layouts.

    A word, a minus sign and one to three figures, a lone `0` or nines
    alone (`asking._set_aside_beside_keys`, the product's own definition),
    on one person's twenty rows or on one person in twenty: each column is
    held by the forms' rule, reached by lane HX5's arm or asked by route
    two (route two's register reads a labelled record number or one beside
    words as a key beside words: `asking._beside_keys_counted`). On repair
    1's head 540 were held by none (one person's `UNKNOWN` beside `#MR`
    one a person: 999 record numbers published and 20,000 real twin cells
    at 20,000 rows). MUTANT: the register's keys off in
    `_beside_keys_counted`: red here.
    """
    unheld = [label for label, cells, one_a_person in records.set_aside_columns(SWEEP_ROWS)
              if not records.held_by_a_reader(cells, one_a_person)]
    assert unheld == []


def test_a_figure_an_exclusion_writes_inside_its_run_is_read_against_the_real_runs_at_every_place() -> None:
    """Every place of a seven-figure run and every figure, with and without a second layout holding it there.

    `taxonomy._an_opening_held` over a spelling that writes one figure at
    one place inside the run (`#@@%9%%%%%` at the second place, Codex's
    item 2): held where a real run of the merged width holds that figure at
    that place (a second layout's `#` and seven figures), not held where
    none does; and the opening written from the run's first place is read
    as before. On repair 1's head every place but the first read as not
    held: Codex's construction wrote 93 to 101 twin cells holding a
    complete real record number at 20,000 rows. MUTANT: the figures past
    the run's opening not read: red here.
    """
    draw = random.Random(records.SEED + 11)
    misses = []
    for place in range(7):
        for figure in "0123456789":
            if place == 0 and figure == "0":
                continue
            def run(holding: bool) -> str:
                while True:
                    figures = f"{draw.randrange(1_000_000, 10_000_000)}"
                    if (figures[place] == figure) == holding:
                        return figures
            own = [f"#MR{run(False)}" for _row in range(200)]
            other = [f"#{run(True)}" for _row in range(50)]
            spelling = "#@@" + "%" * place + figure + "%" * (6 - place)
            for present, expected in ((own, False), (own + other, True)):
                held = taxonomy._run_firsts(present, {7: True})
                if taxonomy._an_opening_held([spelling], [(3, 7)], held, present) != expected:
                    misses += [(place, figure, expected)]
    assert misses == []


def test_codex_s_interior_figure_writes_no_complete_real_run_at_a_test_size(tmp_path: pathlib.Path) -> None:
    """Codex's declared column, 4,000 rows (a test size): `#` and seven figures from 1,900,000 beside `#MR` and seven.

    The `#MR` layout's exclusion wrote `#@@%9%%%%%` on repair 1's head, the
    `9` inside the run where every real `#19...` run holds it, and 3 twin
    cells held a complete real run at this size (93 to 101 at 20,000 rows,
    K-HZ-22's `interior_figure_declared`); and the `#` layout's `#9%%%%%%`
    opened its run with the `9` the `#MR` numbers from 9,000,000 open with
    (8 twin cells at 20,000 rows on the repair's first code). Here every
    layout's exclusion opens each run of five figures or more with figures
    no real run of its width opens with, and no twin cell holds a complete
    real run. MUTANTS: the figures past the run's opening not read, or a
    figure layout's run not kept off in a column of several layouts: red
    here.
    """
    cells = [f"#{1_900_000 + row}" if row % 4 == 0 else f"#MR{(1 + row % 9) * 1_000_000 + row // 9}"
             for row in range(4_000)]
    table = tmp_path / "t.csv"
    with open(table, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["record_label"])
        writer.writerows([[cell] for cell in cells])
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace", "--identifier",
                         "record_label"], small_tables_refused=False) == 0
        assert cli.main(["generate", f"{tmp_path / 't-profile.json'}", "--out-dir", f"{tmp_path}", "--seed", "0",
                         "--replace"], small_tables_refused=False) == 0
    with open(tmp_path / "t-twin.csv", encoding="utf-8", newline="") as handle:
        twin = [row[0] for row in list(csv.reader(handle))[1:]]
    real = set(cells)
    assert sum(1 for cell in twin if cell in real) == 0
    assert records.complete_runs(cells, twin) == 0
    exclusions = json.loads((tmp_path / "t-profile.json").read_text(encoding="utf-8"))["columns"][0][
        "layout_exclusions"]
    real_runs = {run.lstrip("0") for cell in cells for run in records.DIGIT_RUN.findall(cell)}
    opened = []
    for layout, spelling in exclusions.items():
        for place, figures in taxonomy._figure_runs_of_a_layout(layout):
            opening = ""
            while place + len(opening) < len(spelling) and spelling[place + len(opening)].isdigit():
                opening += spelling[place + len(opening)]
            if any(len(run) == figures and run.startswith(opening) for run in real_runs):
                opened += [(layout, spelling)]
    assert opened == [], opened


def test_the_memo_of_unread_searches_holds_the_literal_template() -> None:
    """Two list templates spending one room (`09%%%,09%%%` and `009%%%,009%%%`), a member sharing (Codex's item 3).

    The first's strict search, every filling of its budget written before,
    is remembered as unread; the second's, from the same step, finds a
    filling of its own. On repair 1's head the memo's key held the shared
    step counter alone, so the second was answered by the first's memo and
    its value fell to the spill (Codex's 45,078 rows: the last 11 written
    `87994779760632` with the memo and `009231,009274` without it). MUTANT:
    the template out of the key: red here.
    """
    shorter, longer = "09%%%,09%%%", "009%%%,009%%%"
    room = _a_bare_room()
    room.spends.update({shorter: "shared", longer: "shared"})
    room.sharing.update({"k|elsewhere": True})
    for step in range(1, generation._OFF_THE_REAL_TRIES + 2):
        room.written[generation._filled_layout(shorter, step)] = True
    parts = [("", "000923,019274", "", "000923,019274")]
    assert generation._next_off_the_real(room, shorter, parts, True) is None
    assert len(room.unread) == 1
    found = generation._next_off_the_real(room, longer, parts, True)
    assert found is not None and found["000923,019274"][:3] == "009"


@pytest.mark.parametrize("depth", [1_000, 10_000, 100_000])
def test_a_cell_of_nested_brackets_is_read_once_whatever_its_depth(depth: int) -> None:
    """`'(' * depth + 'MR12345' + ')' * depth` (Codex's item 4): read, never a RecursionError.

    The label reader reads one enclosing pair, once (a pair inside it is no
    label); route two's register reads the cell beside words, and route
    two reads a column of 20,000 such cells (the person question's own
    call). On repair 1's head each raised RecursionError past a depth of
    about 990, and the command's person question with them (the case below
    runs the command; a 20,000-row table holding such a column was profiled,
    generated and validated at exit 0 by the repair's run of this file).
    MUTANT: the pair read by recursion: red here.
    """
    cell = "(" * depth + "MR12345" + ")" * depth
    assert asking._a_whole_number_after_letters(cell) is None
    assert asking._a_register_of_codes([cell] * 20) in (True, False)
    assert asking._names_people_past_route_four([cell] * records.ROWS, taxonomy.ROLE_CATEGORICAL, records.ROWS,
                                                taxonomy.Settings()) in (True, False)


def test_a_column_of_nested_brackets_is_profiled_through_the_person_question(tmp_path: pathlib.Path) -> None:
    """600 rows (a test size) of a thousand nested brackets around `MR12345`, through the command: exit 0 (Codex's item 4).

    On repair 1's head the profile's person question (`asking.person_questions`)
    raised RecursionError on this column at any size. MUTANT: the pair read
    by recursion: red here.
    """
    nested = "(" * 1_000 + "MR12345" + ")" * 1_000
    table = tmp_path / "t.csv"
    with open(table, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["label_text"])
        writer.writerows([[nested]] * 600)
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace"],
                        small_tables_refused=False) == 0


def test_the_names_beside_numbers_question_states_the_properties_of_each_form_it_holds() -> None:
    """The Safe Harbor question of a name beside a record number names every form the rule holds (Codex's item 5).

    `1000013,Cedar,Aaa`, `Cedar,Aaa,60000` and `Cedar;Aaa;60000` were told
    of a family name, a comma and a given name beside six figures in
    brackets or after a number sign: false for them. The words name the
    bracketed form and the joined one -- its joiners, the number first or
    last, five figures, a label and a flag -- and no value.
    """
    said = asking._identifier_form_seen(asking.BECAUSE_SAFE_HARBOR_NAMES_WITH_NUMBERS)
    for words in ("in brackets or after a number sign", "six figures or more", "a comma, a semicolon, a bar, a tab, "
                  "a caret or an underscore", "written first or last", "five figures or more", "a flag of one or two "
                  "letters"):
        assert words in said, words
    for cell in ("1000013,Cedar,Aaa", "Cedar,Aaa,60000", "Cedar;Aaa;60000", "Cedar, Aaa [1000013]"):
        assert taxonomy._forms_of_a_cell(cell)[0] == taxonomy.HELD_NAMES_WITH_NUMBERS, cell
        assert cell not in said


def test_three_and_four_figure_labelled_values_one_a_person_are_read_beside_no_words() -> None:
    """`Bed 1001` upward and `Room 123` upward, one a person: no record number beside words, no register.

    The beside-words reader's five-figure line (`_PREFIXED_FIGURES_AT_LEAST`,
    read by `asking._read_beside_words`) holds: a bed or a room is no
    record number (the verify's finding 6). MUTANT MV7 (the line lowered to
    three figures): red here.
    """
    people = range(1_000)
    for make in (lambda person: f"Bed {1001 + person}", lambda person: f"Room {123 + person % 800}"):
        drawn = [make(person) for person in people]
        assert [cell for cell in drawn if asking._a_whole_number_beside_words(cell) is not None] == []
        cells = [cell for cell in drawn for _row in range(records.ROWS_A_PERSON)]
        assert not asking._a_register_of_codes(cells), cells[0]


def test_a_device_identifier_keeps_its_own_hold_and_is_no_register_beside_words() -> None:
    """HIBCC device identifiers one a person, 20 devices of 30 rows: no code of route two's register.

    The beside-words reading read `+H724PRD1230/$$3270101LOT123X` as a
    record number beside words and route two's person question took the
    place of the device hold's Safe Harbor question (the suite's
    `udi_hibcc` case on repair 1's head). A cell holding a device
    identifier is left to that hold, which takes the column from one such
    cell. MUTANT: `taxonomy.a_device_identifier` not asked: red here.
    """
    devices = [f"+H724PRD{lot}0/$$3{270101 + lot}LOT{lot}X" for lot in range(100, 120)]
    cells = [devices[row % 20] for row in range(600)]
    assert taxonomy.a_device_identifier(devices[0])
    assert not asking._a_register_of_codes(cells)
    assert not asking._a_register_key(devices[0], cells, {})


def test_the_three_classes_at_the_table_floor_publish_nothing_and_write_no_real_value(tmp_path: pathlib.Path) -> None:
    """ONE table at 20,000 rows, 1,000 people of 20 rows, a column of each class, nothing declared or answered.

    Through the command with nobody at the keyboard (profile, generate at
    seed 0, validate): each column is held as an identifier and put a
    question offering `identifier` or the Safe Harbor question; no real
    value of it is in the description, its summary, the questions file,
    the screen or the twin's reports; no twin cell is a real one or holds
    a complete real run of five figures or more inside a wider cell. On
    the base a391424c the signed label wrote 19,999 real cells and showed
    126 values, the commas 18,000 real cells and 1,998 complete runs, and
    one record number a person beside a name with spaced commas 20,000
    real cells and 1,000 values shown. AND (lane CZ-A2's follow-up, LANE
    CZ-A2 RULINGS 9 (2)) a soft hyphen inside a label's figures, one a
    person (`MR100` + U+00AD + `0013`): on 8b28950b read as labels, 1,000
    values in the description and 20,000 real twin cells; and two Ethiopic
    letters before seven figures, one a row (an affixed number there, 126
    runs shown and 19,999 real twin cells) and one a person (labels, 1,000
    values shown and 20,000 real twin cells). AND (lane CZ-A2's follow-up 4,
    LANE CZ-A2 RULINGS 10 (2)) a record number in two groups of figures, one
    a person, after a plain space (`MR100 0013`), a no-break space after the
    fourth figure (`MR1000 013`) or a tab: on 7894ddbd read as labels, 1,000
    values shown and 20,000 real twin cells each; six figures in groups of
    three one a row (`MR100 000`): an affixed number there, 19,999 real twin
    cells. Beside them weeks of the year (`W23 2024`), a column of periods,
    keep their reading: labels, no question offering `identifier`.
    """
    import health_zoo as zoo

    columns = {
        "record_label": records.ITEMS["sign_label"][1],
        "patient_label": records.ITEMS["joined_by_commas"][1],
        "chart_label": records.ITEMS["joined_spaced_one_a_person"][1],
        "visit_label": records.ITEMS["label_soft_hyphen_inside_one_a_person"][1],
        "ward_label": records.ITEMS["ethiopic_label"][1],
        "bed_label": records.ITEMS["ethiopic_label_one_a_person"][1],
        "folder_label": records.ITEMS["label_two_groups_one_a_person"][1],
        "card_label": records.ITEMS["label_two_groups_no_break_space_one_a_person"][1],
        "file_label": records.ITEMS["label_two_groups_tab_one_a_person"][1],
        "slip_label": records.ITEMS["label_two_groups_six_figures"][1],
    }
    periods = {"week_label": records.FALSE_ALARMS["weeks_of_the_year"]}
    rows = records.ROWS
    table = tmp_path / "t.csv"
    cells = {name: [make(row, row // records.ROWS_A_PERSON) for row in range(rows)]  # type: ignore[operator]
             for name, make in {**columns, **periods}.items()}
    with open(table, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(list(columns) + list(periods))
        writer.writerows([[cells[name][row] for name in list(columns) + list(periods)] for row in range(rows)])
    screen = io.StringIO()
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        assert cli.main(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace"]) == 0
        assert cli.main(["generate", f"{tmp_path / 't-profile.json'}", "--out-dir", f"{tmp_path}", "--seed", "0",
                         "--replace"]) == 0
        assert cli.main(["validate", f"{tmp_path / 't-profile.json'}", "--twin", f"{tmp_path / 't-twin.csv'}",
                         "--out-dir", f"{tmp_path}", "--replace"]) == 0
    texts = [screen.getvalue()] + [
        (tmp_path / name).read_text(encoding="utf-8")
        for name in ("t-profile.json", "t-profile.txt", "t-questions.json", "t-twin-report.txt", "t-twin-quality.txt")
        if (tmp_path / name).is_file()
    ]
    roles = {block["name"]: block["role"]
             for block in json.loads((tmp_path / "t-profile.json").read_text(encoding="utf-8"))["columns"]}
    asked: "dict[str, list[list[str]]]" = {}
    for entry in zoo._entries(json.loads((tmp_path / "t-questions.json").read_text(encoding="utf-8"))):
        asked.setdefault(f"{entry.get('column', '')}", []).append(sorted(zoo._offered(entry)))
    with open(tmp_path / "t-twin.csv", encoding="utf-8", newline="") as handle:
        written = list(csv.reader(handle))
    for place, name in enumerate(columns):
        real = sorted(set(cells[name]))
        real_set = set(real)
        twin = [row[place] for row in written[1:]]
        counted = held_shapes.count_real(real, texts, twin, linear=True)
        assert roles[name] == taxonomy.ROLE_IDENTIFIER, name
        assert any("identifier" in one or one == ["no", "yes"] for one in asked.get(name, [])), name
        assert counted["description_values"] == 0, name
        assert sum(1 for cell in twin if cell in real_set) == 0, name
        assert records.complete_runs(real, twin) == 0, name
    for name in periods:
        assert roles[name] == taxonomy.ROLE_CATEGORICAL, name
        assert not any("identifier" in one for one in asked.get(name, [])), name

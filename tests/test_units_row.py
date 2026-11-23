"""A row under the column names that names each column's unit (lane ZOO-Y, plan P4-D517).

Instrument and laboratory exports write one row under the names with
each column's unit: `,mg/dL,mmHg,kg` over columns of numbers. MEASURED
(lane ZOO-X's data-type zoo, 20,000 rows, the floor on): the row was
read as a record, its three words left out of three columns' statistics
and written by the twin as stand-ins (`text-1`) in other rows, so a
script that skips the second row of the file read three columns of the
twin as text.

Such a row (`dialect._units_row_shape`) holds a unit in every column of
numbers that is not blank in it, nothing in any other column, and no
figure on its own. The shape is ASKED ABOUT, and the row stays a record
until the person answers `units-row`: then it is taken out of the table
and published as written, like the column names, and the twin writes it
back under them. Until batch 4z's fix round it was taken unasked, and the
outside review of the batch (item 1) took a patient's record `A123,` --
an identifier over a column of numeric keys, the rest blank -- for a
units row and wrote it back whole under the twin's names. Every table
here is invented, written by this file.
"""

from __future__ import annotations

import pathlib
import random

import fixtures
from synthtwin import asking, reading


def _table(folder: pathlib.Path, first: str, name: str = "units.csv") -> pathlib.Path:
    draw = random.Random(3)
    lines = ["person_key,glucose,systolic,weight", first]
    for row in range(300):
        lines += [f"P{row:05d},{draw.randint(60, 200)},{draw.randint(90, 180)},{draw.gauss(78, 14):.1f}"]
    return fixtures.write(folder, name, "\n".join(lines) + "\n")


def test_a_units_row_answered_is_taken_out_and_the_columns_read_as_numbers(tmp_path: pathlib.Path) -> None:
    """Answered `units-row` (one row declared and confirmed): the row is taken and the three columns read as numbers."""
    read = reading.read_table(
        str(_table(tmp_path, ",mg/dL,mmHg,kg")), reading.FIRST_ROW_NAMES, metadata_rows=asking.METADATA_ROWS_UNITS,
        metadata_rows_confirmed=True)
    assert read.survey is not None and read.survey.units_shape
    assert read.survey.form.header_rows == (("", "mg/dL", "mmHg", "kg"),)
    assert read.n_rows == 300
    for place in (1, 2, 3):
        assert all(cell.replace(".", "", 1).isdigit() for cell in reading.column_values(read, place)), place


def test_a_units_row_unanswered_stays_a_record(tmp_path: pathlib.Path) -> None:
    """Unanswered, or answered `data`: the shape is seen, and the row stays one of the table's records."""
    for confirmed in (False, True):
        read = reading.read_table(
            str(_table(tmp_path, ",mg/dL,mmHg,kg", f"u{confirmed}.csv")), reading.FIRST_ROW_NAMES, metadata_rows=0,
            metadata_rows_confirmed=confirmed)
        assert read.survey is not None and read.survey.units_shape
        assert read.survey.form.header_rows == () and read.n_rows == 301, confirmed


def test_a_record_holding_an_identifier_is_never_taken_unasked(tmp_path: pathlib.Path) -> None:
    """The outside review's item 1: `A123,` over a column of numeric keys reads as the shape, and stays a record."""
    draw = random.Random(5)
    lines = ["patient_id,lab_value", "A123,"] + [f"{100000 + row},{draw.gauss(5, 1):.2f}" for row in range(300)]
    path = fixtures.write(tmp_path, "keys.csv", "\n".join(lines) + "\n")
    read = reading.read_table(str(path), reading.FIRST_ROW_NAMES)
    assert read.survey is not None and read.survey.units_shape, "premise: the record has the shape"
    assert read.survey.form.header_rows == () and read.n_rows == 301
    assert "A123" in reading.column_values(read, 0)


def test_a_record_is_never_read_as_a_units_row(tmp_path: pathlib.Path) -> None:
    """A figure in it, a key in it, a missing word in it, or a unit over a column of words: it stays a record."""
    for first in ("P99999,mg/dL,mmHg,kg", ",120,mmHg,kg", ",NA,NA,NA", ",mg/dL,,", ",,,"):
        read = reading.read_table(str(_table(tmp_path, first, f"t{len(first)}.csv")), reading.FIRST_ROW_NAMES)
        assert read.survey is not None and read.survey.units_shape == (first == ",mg/dL,,"), first
        assert read.survey.form.header_rows == (), first
    words = ["name,weight", "text,kg"] + [f"n{row},{row}" for row in range(300)]
    path = fixtures.write(tmp_path, "words.csv", "\n".join(words) + "\n")
    read = reading.read_table(str(path), reading.FIRST_ROW_NAMES)
    assert read.survey is not None and not read.survey.units_shape and read.n_rows == 301


def test_the_questions_file_asks_about_the_units_row_with_the_record_standing() -> None:
    asked = asking.file_questions(False, units_shape=True)
    assert len(asked) == 1
    question = asked[0]
    assert question.taken == asking.ANSWER_DATA
    assert [choice.answer for choice in question.choices] == [asking.ANSWER_UNITS_ROW, asking.ANSWER_DATA]
    assert asking.file_questions(False) == []

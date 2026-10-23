"""The answers file may not change the reading and name a column at once.

THE TWO ANSWER-PATH ITEMS OF STAGE 3'S REVIEW (floor items 1 and 2). Both are about the same seam: a questions file carries answers about
how the FILE is read -- which row holds the column names, which
character separates the columns -- beside answers that name COLUMNS, and
the two kinds were applied without either noticing the other.

FINDING 1. An answer that changes the reading gives the file's column
names to different columns, and a declaration applied by NAME afterwards
lands on the wrong one. Reproduced on a header of `column_2,column_1`:
answering `names` for the first row and `identifier` for `column_1` --
the FIRST field under the reading in force -- put the declaration on the
SECOND field, and the run counted 350 people and published twelve real
subject codes with their visit counts. The pair is refused now.

FINDING 2. The other answer about the first row, `first-record`, was
dropped as "the reading that already stands", which it is only while
nothing else moves. Answered beside a delimiter correction it is the one
answer holding the first row IN the table, and the corrected reading took
that row as the column names: 360 records described instead of 361, with
`12,HEADER` and `LABEL` published as two column names. Both answers are
applied now, and the pair agrees with the equivalent options cell for
cell.

EVERY EXPECTATION HERE IS DERIVED FROM THE OPTIONS, not from a run. What
the answers do is what `--first-row` and `--delimiter` do, so the control
in each test is the same table read with those options typed, and the
answered run is compared against it.
"""

import json
import pathlib

import pytest

from synthtwin import asking, errors
from synthtwin.cli import main

import fixtures


# How many records each table below holds under the reading in force. Over
# `parsing.POPULATION_FLOOR` so nothing is refused for its size, and the
# number itself is arbitrary: no expectation is computed from it.
_RECORDS = 360
# How many of the second field's records repeat the header's own value in
# the finding-1 table. Under the default smallest group, so the repeat is
# what makes the first row unreadable and not a published level.
_REPEATS = 11
# How many subjects the first field of the finding-1 table holds. Under
# `parsing.POPULATION_FLOOR`, so a run that counts this table in people
# refuses it -- which is what the right declaration does and what the
# wrong one did not.
_SUBJECTS = 12


def _table_with_swapped_names(folder: pathlib.Path) -> pathlib.Path:
    """The finding-1 file: a header whose names are `column_2,column_1`.

    The first field holds twelve repeating subject codes. The second
    field's first `_REPEATS` records hold the header's own second value,
    which is what makes the first row indistinguishable from a record --
    "the value in that row appears again further down the same column" --
    so the automatic reading names the columns `column_1`, `column_2` and
    keeps every row.

    THE POINT OF THE SHAPE: `column_1` is a column name under BOTH
    readings, and a different column under each. A repair that mapped
    names across the change by parsing the digit out of a placeholder
    would read this file wrong in exactly the same way.
    """
    lines = ["column_2,column_1"]
    for place in range(_RECORDS):
        second = "column_1" if place < _REPEATS else f"S{place:05d}"
        lines += [f"P{place % _SUBJECTS + 1:05d},{second}"]
    return fixtures.write(folder, "clinic.csv", "\n".join(lines) + "\n")


def _table_that_splits_two_ways(folder: pathlib.Path) -> pathlib.Path:
    """The finding-2 file: a first record that reads two ways.

    `12,HEADER|LABEL` over records of `i,code{i}|other{i}`. Under the
    comma the first row is a record -- its first value is a number lying
    among the numbers below it -- and under the vertical bar nothing in
    the values marks it, so the corrected reading takes it as the names
    unless the person's `first-record` answer is applied.
    """
    lines = ["12,HEADER|LABEL"]
    for place in range(_RECORDS):
        lines += [f"{place},code{place}|other{place}"]
    return fixtures.write(folder, "clinic.csv", "\n".join(lines) + "\n")


def _delimiter_answer(character: str) -> str:
    """The word that answers the delimiter question for that character.

    Read off `asking.ANSWER_DELIMITERS` rather than written out, so a
    renamed answer turns this file red where the rename happened.
    """
    for word in asking.ANSWER_DELIMITERS:
        if asking.ANSWER_DELIMITERS[word] == character:
            return word
    raise AssertionError(f"no answer offers {character!r}")


def _questions(folder: pathlib.Path) -> "dict[str, object]":
    return json.loads(
        (folder / "clinic-questions.json").read_text(encoding="utf-8")
    )


def _described(folder: pathlib.Path) -> "dict[str, object]":
    document = json.loads(
        (folder / "clinic-profile.json").read_text(encoding="utf-8")
    )
    assert isinstance(document, dict)
    return document


def _names(folder: pathlib.Path) -> "list[str]":
    blocks = _described(folder)["columns"]
    assert isinstance(blocks, list)
    return [f"{block['name']}" for block in blocks]


def _answered(
    folder: pathlib.Path,
    written: "dict[str, object]",
    about_file: "dict[str, str]",
    columns: "dict[str, str]",
) -> pathlib.Path:
    """The questions file with those answers written into it.

    `about_file` is keyed by the question's subject, as `asking` names it,
    and `columns` by column name; both are written exactly where a person
    would write them.
    """
    folder.mkdir(parents=True, exist_ok=True)
    sections = written["about_your_file"]
    assert isinstance(sections, list)
    for entry in sections:
        if entry["column"] in about_file:
            entry["your_answer"] = about_file[entry["column"]]
    asked = written["asked"]
    checklist = written["checklist"]
    assert isinstance(asked, list)
    assert isinstance(checklist, dict)
    listed = checklist["columns"]
    assert isinstance(listed, list)
    for entry in asked + listed:
        if entry["column"] in columns:
            entry["your_answer"] = columns[entry["column"]]
    # Written through `fixtures.write`, which fixes the line endings: a
    # file this suite composes has to be the same bytes on every
    # platform (`tests/test_description_line_endings.py`).
    return fixtures.write(
        folder, "answers.json", json.dumps(written, indent=1)
    )


def _run(folder: pathlib.Path, table: pathlib.Path, *options: str) -> int:
    folder.mkdir(parents=True, exist_ok=True)
    return main(
        ["profile", f"{table}", "--out-dir", f"{folder}", "--replace"]
        + list(options)
    )


# -- finding 1: the pair that cannot be acted on -----------------------


def test_the_first_reading_asks_about_the_first_row_and_keeps_every_record(
    tmp_path: pathlib.Path,
) -> None:
    """The premise of the two tests below, asserted rather than assumed.

    If this file were read with its header row as the names, there would
    be no question to answer and no reading to change, and the tests
    below would be about nothing.
    """
    folder = tmp_path / "first"
    table = _table_with_swapped_names(tmp_path)
    assert _run(folder, table) == 0
    assert _names(folder) == ["column_1", "column_2"]
    assert _described(folder)["n_rows"] == _RECORDS + 1
    subjects = [
        entry["column"] for entry in _questions(folder)["about_your_file"]
    ]
    assert asking.FIRST_ROW_SUBJECT in subjects


def test_a_header_correction_beside_an_identifier_answer_is_refused(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """THE REVIEWER'S OWN REPRODUCTION (floor item 1).

    `names` for the first row and `identifier` for `column_1`, in one
    file. Under the reading in force `column_1` is the first field, the
    one holding the subject codes; under the corrected reading it is the
    second. The run applied the declaration to the second field, reached
    every writer, counted 350 people and published the twelve subject
    codes with counts of thirty.

    Nothing is written, and the message says which question it was and
    which column was named, so the person can do it in two runs.
    """
    folder = tmp_path / "first"
    table = _table_with_swapped_names(tmp_path)
    assert _run(folder, table) == 0
    answers = _answered(
        tmp_path,
        _questions(folder),
        {asking.FIRST_ROW_SUBJECT: asking.ANSWER_FIRST_ROW_NAMES},
        {"column_1": asking.ANSWER_IDENTIFIER},
    )
    second = tmp_path / "second"
    assert _run(second, table, "--answers", f"{answers}") == 2
    assert sorted(one.name for one in second.iterdir()) == []
    said = capsys.readouterr()
    screen = said.err + said.out
    assert asking.FIRST_ROW_SUBJECT in screen
    assert "column_1" in screen
    assert "Nothing was written." in screen


def test_the_refusal_is_about_the_pair_and_not_about_either_answer(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Each answer alone is acted on, which is what makes it a PAIR rule.

    The header correction on its own renames the columns as the file
    names them and drops that row from the table. The identifier answer
    on its own reaches the column the person was looking at -- the first
    field, holding twelve repeating subject codes -- and the run then
    counts the table in PEOPLE and refuses it, which is the outcome the
    review said the right declaration gives. Neither answer is refused
    for being the answer it is, and a repair that refused the header
    correction outright would pass the test above and fail this one.

    THIRTEEN, NOT TWELVE, AND THE THIRTEENTH IS DERIVED. Under the
    reading in force the file's first row is a RECORD, so its own value
    in that field is a thirteenth person: twelve subjects plus one.
    """
    folder = tmp_path / "first"
    table = _table_with_swapped_names(tmp_path)
    assert _run(folder, table) == 0
    written = _questions(folder)
    header_only = _answered(
        tmp_path / "header",
        json.loads(json.dumps(written)),
        {asking.FIRST_ROW_SUBJECT: asking.ANSWER_FIRST_ROW_NAMES},
        {},
    )
    renamed = tmp_path / "renamed"
    assert _run(renamed, table, "--answers", f"{header_only}") == 0
    assert _names(renamed) == ["column_2", "column_1"]
    assert _described(renamed)["n_rows"] == _RECORDS

    column_only = _answered(
        tmp_path / "column",
        json.loads(json.dumps(written)),
        {},
        {"column_1": asking.ANSWER_IDENTIFIER},
    )
    capsys.readouterr()
    declared = tmp_path / "declared"
    assert _run(declared, table, "--answers", f"{column_only}") == 1
    said = capsys.readouterr()
    screen = said.err + said.out
    assert f"{_SUBJECTS + 1} people" in screen
    assert "'column_1'" in screen
    assert sorted(one.name for one in declared.iterdir()) == []


def test_a_delimiter_correction_beside_a_column_answer_is_refused_too(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The other answer that moves a column name (floor item 1).

    Which character separates the columns decides how many columns there
    are and where each one begins, so a name in the file can mean a
    different column, a wider one, or none at all. The review named the
    header correction; this is the same defect one question along, and a
    repair that closed only the one named would pass every test above.
    """
    folder = tmp_path / "first"
    table = _table_that_splits_two_ways(tmp_path)
    assert _run(folder, table) == 0
    answers = _answered(
        tmp_path,
        _questions(folder),
        {asking.DELIMITER_SUBJECT: _delimiter_answer("|")},
        {"column_1": asking.ANSWER_IDENTIFIER},
    )
    second = tmp_path / "second"
    assert _run(second, table, "--answers", f"{answers}") == 2
    assert sorted(one.name for one in second.iterdir()) == []
    said = capsys.readouterr()
    assert asking.DELIMITER_SUBJECT in said.err + said.out


def test_an_answer_that_agrees_with_the_option_typed_changes_nothing(
    tmp_path: pathlib.Path,
) -> None:
    """A reading already in force is not a change, and is not refused.

    `--delimiter ','` typed and `comma` answered is the same reading
    twice, so the column names do not move and a column answer beside it
    is acted on. Without this the rule would cost a person a run for
    confirming what they had already said.
    """
    folder = tmp_path / "first"
    table = _table_that_splits_two_ways(tmp_path)
    assert _run(folder, table, "--delimiter", ",") == 0
    answers = _answered(
        tmp_path,
        _questions(folder),
        {asking.DELIMITER_SUBJECT: _delimiter_answer(",")},
        {"column_1": asking.ANSWER_IDENTIFIER},
    )
    second = tmp_path / "second"
    assert _run(second, table, "--delimiter", ",", "--answers", f"{answers}") == 0
    settings = _described(second)["settings"]
    assert isinstance(settings, dict)
    assert settings["forced_identifiers"] == ["column_1"]


def test_the_message_names_the_question_the_column_and_the_two_runs(
    tmp_path: pathlib.Path,
) -> None:
    """What the refusal owes its reader, asked of the message itself."""
    said = errors.answers_change_the_reading_and_name_columns(
        "answers.json", [asking.FIRST_ROW_SUBJECT], ["dose"]
    )
    assert asking.FIRST_ROW_SUBJECT in said
    assert "'dose'" in said
    assert "two runs" in said
    assert said.rstrip().endswith("Nothing was written.")


# -- finding 2: the answer that was dropped ----------------------------


def test_a_first_record_answer_beside_a_delimiter_answer_is_applied(
    tmp_path: pathlib.Path,
) -> None:
    """THE REVIEWER'S OWN REPRODUCTION (floor item 2).

    `first-record` and `vertical-bar` in one file. Only the delimiter was
    applied: the corrected reading took `12,HEADER` and `LABEL` as two
    column names and described 360 records instead of 361.

    THE EXPECTATION IS THE CONTROL'S, not a run's. `--first-row data
    --delimiter '|'` is what those two answers mean, so the answered run
    is compared against it: the same column names, the same row count and
    the same cells.
    """
    folder = tmp_path / "first"
    table = _table_that_splits_two_ways(tmp_path)
    assert _run(folder, table) == 0
    assert _described(folder)["n_rows"] == _RECORDS + 1
    answers = _answered(
        tmp_path,
        _questions(folder),
        {
            asking.FIRST_ROW_SUBJECT: asking.ANSWER_FIRST_ROW_DATA,
            asking.DELIMITER_SUBJECT: _delimiter_answer("|"),
        },
        {},
    )
    answered = tmp_path / "answered"
    assert _run(answered, table, "--answers", f"{answers}") == 0
    typed = tmp_path / "typed"
    assert _run(typed, table, "--first-row", "data", "--delimiter", "|") == 0
    assert _names(answered) == _names(typed)
    assert _described(answered)["n_rows"] == _described(typed)["n_rows"]
    assert _names(answered) == ["column_1", "column_2"]
    assert _described(answered)["n_rows"] == _RECORDS + 1


def test_a_first_record_answer_overrides_the_option_typed(
    tmp_path: pathlib.Path,
) -> None:
    """The file is the newer statement, in both directions.

    `--first-row names` typed and `first-record` answered: the answer
    wins, exactly as `names` answered wins over a typed `data`. An answer
    applied in one direction only would leave a person who changed their
    mind back towards the standing reading unheard.
    """
    folder = tmp_path / "first"
    table = _table_that_splits_two_ways(tmp_path)
    assert _run(folder, table) == 0
    answers = _answered(
        tmp_path,
        _questions(folder),
        {asking.FIRST_ROW_SUBJECT: asking.ANSWER_FIRST_ROW_DATA},
        {},
    )
    answered = tmp_path / "answered"
    assert _run(
        answered, table, "--first-row", "names", "--answers", f"{answers}"
    ) == 0
    assert _names(answered) == ["column_1", "column_2"]
    assert _described(answered)["n_rows"] == _RECORDS + 1

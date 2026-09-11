"""The questions file is filled in and handed back with `--answers`.

AMENDMENT A-P4-58 built the file; A-P4-60 makes it answerable. Together
they are how the owner's standing principle -- "it's better to ask the
user than make wrong guesses" -- is kept for somebody who is not at a
keyboard, which is most runs.

**AND THIS FILE IS ALSO THE RECORD OF A RULING THAT WAS WITHDRAWN.**
A-P4-59 clause 3 ruled that an unanswered column of figures should be
read as CODES rather than as numbers. It was built, narrowed to the
padded signal alone on a measurement, and then run against the suite,
which returned three results that settle it:

* the owner had already settled it the other way. Review item P1-R6-F7
  deleted a rule routing on width AND ON THE LEADING ZERO, and
  `tests/test_p1r6f7_one_policy.py` names `00501` and `000000`..`000049`
  among the columns that must land where the ordinary rules put them;
* the harm was already prevented, and better. Plan decision P4-D14
  publishes the FIELD WIDTH of a padded column, so the twin of `00100`
  is written `00100` -- which is what a length check or a join on the
  code needs. The argument for routing was that the twin loses the
  padding; it has not since P4-D14, and `tests/test_p4d14_pad_widths.py`
  is the record of that;
* and routing costs the distribution. A genuine padded measurement
  would have lost its average, its spread and its ends.

So the tests below hold the two halves that DID ship: a padded column
is asked about and reads as a measurement until somebody says
otherwise, and the answer can now be given in a file.
"""

import json
import pathlib
import random
import tempfile

import fixtures
from synthtwin import asking, cli, contract, profile, reading, taxonomy


def _table(
    folder: pathlib.Path, columns: "dict[str, list[str]]"
) -> pathlib.Path:
    names = sorted(columns)
    rows: list[list[str]] = []
    deep = len(columns[names[0]])
    for place in range(deep):
        rows += [[columns[name][place] for name in names]]
    return fixtures.write(
        folder, "clinic.csv", fixtures.rows_to_csv(names, rows)
    )


def _columns() -> "dict[str, list[str]]":
    """Three columns of digits, none of them separable from the others."""
    draw = random.Random(11)
    return {
        # padded: a procedure code register written five wide
        "padded_code": [
            f"{draw.choice([80053, 9921, 2988, 453, 2061]):05d}"
            for _index in range(120)
        ],
        # fixed width and not padded: a real reading, 100 to 999
        "reading": [f"{draw.randint(100, 999)}" for _index in range(120)],
        # fixed width and not padded: a year
        "born": [f"{draw.randint(1930, 1999)}" for _index in range(120)],
    }


def _role_of(document: "dict[str, object]", name: str) -> str:
    for block in document["columns"]:
        if block["name"] == name:
            return f"{block['role']}"
    raise AssertionError(f"no column named {name}")


def _described(
    codes: "list[str] | None" = None,
    identifiers: "list[str] | None" = None,
    measurements: "list[str] | None" = None,
) -> "tuple[dict, object, taxonomy.Settings]":
    folder = pathlib.Path(tempfile.mkdtemp())
    table = _table(folder, _columns())
    read = reading.read_table(f"{table}")
    settings = taxonomy.Settings()
    document = profile.build_document(
        read,
        settings,
        [] if identifiers is None else identifiers,
        [] if codes is None else codes,
        [] if measurements is None else measurements,
    )
    return document, read, settings


# ---------------------------------------------------------------------
# 1. nothing is routed, and the file says the reading that is taken
# ---------------------------------------------------------------------


def test_no_column_of_figures_is_routed_by_its_shape() -> None:
    """A-P4-59 clause 3, withdrawn: all three stay measurements.

    One is padded, two are fixed width. Under the withdrawn rule the
    padded one became labels; under the rule as first written all three
    did, taking a genuine reading and a column of years with it.
    """
    document, _read, _settings = _described()
    for name in ("padded_code", "reading", "born"):
        assert _role_of(document, name) in asking.NUMERIC_ROLES, (
            f"'{name}' is read by the ordinary rules, which is review "
            f"item P1-R6-F7's settled policy"
        )


def test_the_questions_file_states_the_reading_the_run_takes() -> None:
    """The one promise this file may never break.

    Every column here is asked about -- one for its padding, two for
    their width -- and every one of them says `measurement`, because
    that is what the run does with it.
    """
    document, read, settings = _described()
    asked = asking.questions_for(document, read.columns, settings, [])
    named = sorted(question.name for question in asked)
    assert named == ["born", "padded_code", "reading"]
    for question in asked:
        assert question.taken == asking.ANSWER_MEASUREMENT, (
            f"'{question.name}' is described as a measurement, so the "
            f"file may not name any other reading for it"
        )
    for question in asked:
        assert asking.ANSWER_CODE in [
            choice.answer for choice in question.choices
        ], "and `code` is offered, which is how the person corrects it"


def test_a_declared_measurement_is_not_asked_about_again() -> None:
    """A declaration is an answer, and asking again unsays it."""
    document, read, settings = _described(measurements=["padded_code"])
    asked = asking.questions_for(
        document, read.columns, settings, ["padded_code"]
    )
    assert "padded_code" not in [question.name for question in asked]


# ---------------------------------------------------------------------
# 2. the hand-back
# ---------------------------------------------------------------------


def _run(folder: pathlib.Path, *options: str) -> int:
    table = _table(folder, _columns())
    return cli.main(["profile", f"{table}", "--replace", *options])


def _answered(
    questions: pathlib.Path, name: str, answer: str
) -> pathlib.Path:
    document = json.loads(questions.read_text(encoding="utf-8"))
    for entry in document["asked"]:
        if entry["column"] == name:
            entry["your_answer"] = answer
    for entry in document["checklist"]["columns"]:
        if entry["column"] == name:
            entry["your_answer"] = answer
    questions.write_text(
        json.dumps(document, indent=2), encoding="utf-8", newline="\n"
    )
    return questions


def test_a_questions_file_is_written_on_every_run(
    tmp_path: pathlib.Path, capsys
) -> None:
    """Unconditionally, which is why the handling rule needs no hedge."""
    assert _run(tmp_path) == 0
    capsys.readouterr()
    written = sorted(path.name for path in tmp_path.iterdir())
    assert "clinic-questions.json" in written
    document = json.loads(
        (tmp_path / "clinic-questions.json").read_text(encoding="utf-8")
    )
    said = json.dumps(document)
    for column in _columns().values():
        for value in column[:20]:
            assert f'"{value}"' not in said, (
                "the file travels and a cell of the table may not"
            )


def test_an_answer_in_the_file_becomes_the_declaration(
    tmp_path: pathlib.Path, capsys
) -> None:
    """The whole round trip: run, answer the file, run again."""
    assert _run(tmp_path) == 0
    capsys.readouterr()
    questions = tmp_path / "clinic-questions.json"
    _answered(questions, "padded_code", asking.ANSWER_CODE)
    assert _run(tmp_path, "--answers", f"{questions}") == 0
    capsys.readouterr()
    document = json.loads(
        (tmp_path / "clinic-profile.json").read_text(encoding="utf-8")
    )
    assert _role_of(document, "padded_code") not in asking.NUMERIC_ROLES, (
        "the person answered `code`, so no average is published over it"
    )
    assert document["settings"]["forced_codes"] == ["padded_code"], (
        "and the answer is recorded as the declaration it stands for, "
        "so the description says who decided"
    )
    assert _role_of(document, "reading") in asking.NUMERIC_ROLES, (
        "a column they did not answer about is untouched"
    )


def test_each_answer_reaches_its_own_declaration(
    tmp_path: pathlib.Path, capsys
) -> None:
    assert _run(tmp_path) == 0
    capsys.readouterr()
    questions = tmp_path / "clinic-questions.json"
    _answered(questions, "padded_code", asking.ANSWER_IDENTIFIER)
    _answered(questions, "reading", asking.ANSWER_MEASUREMENT)
    assert _run(tmp_path, "--answers", f"{questions}") == 0
    capsys.readouterr()
    settings = json.loads(
        (tmp_path / "clinic-profile.json").read_text(encoding="utf-8")
    )["settings"]
    assert settings["forced_identifiers"] == ["padded_code"]
    assert settings["forced_measurements"] == ["reading"]


def test_an_answer_that_was_not_offered_is_refused(
    tmp_path: pathlib.Path, capsys
) -> None:
    """Refused, never ignored: the person has said something.

    Dropping a word nobody could read would describe the table the old
    way while the file on disk said otherwise -- so they would have
    corrected their description and been told nothing.
    """
    assert _run(tmp_path) == 0
    capsys.readouterr()
    description = tmp_path / "clinic-profile.json"
    before = description.read_bytes()
    questions = tmp_path / "clinic-questions.json"
    _answered(questions, "padded_code", "codes")
    assert _run(tmp_path, "--answers", f"{questions}") == 2
    said = capsys.readouterr().err
    assert "padded_code" in said, "the message names the column"
    assert "codes" in said, "and the word they wrote"
    assert "measurement" in said, "and what they could write instead"
    assert description.read_bytes() == before, (
        "and nothing was written: the answers are read before the "
        "table is opened, so a refusal costs the person one edit and "
        "not a run over their real data"
    )


def test_a_file_that_is_not_a_questions_file_is_refused(
    tmp_path: pathlib.Path, capsys
) -> None:
    assert _run(tmp_path) == 0
    capsys.readouterr()
    other = tmp_path / "clinic-profile.json"
    assert _run(tmp_path, "--answers", f"{other}") == 2
    said = capsys.readouterr().err
    assert "not a synthtwin questions file" in said
    assert "-questions.json" in said, (
        "and it says what the right file is called"
    )


def test_a_blank_answer_changes_nothing(
    tmp_path: pathlib.Path, capsys
) -> None:
    """The commonest case by far, and it must cost nothing."""
    assert _run(tmp_path) == 0
    capsys.readouterr()
    questions = tmp_path / "clinic-questions.json"
    read = asking.answers_in(
        contract.load_answers(f"{questions}"), f"{questions}"
    )
    assert read.codes == ()
    assert read.identifiers == ()
    assert read.measurements == ()


def test_the_answer_replaces_a_declaration_typed_earlier(
    tmp_path: pathlib.Path, capsys
) -> None:
    """The file is the newer statement, and the pair it could make is
    the pair the command line refuses."""
    assert _run(tmp_path) == 0
    capsys.readouterr()
    questions = tmp_path / "clinic-questions.json"
    _answered(questions, "padded_code", asking.ANSWER_MEASUREMENT)
    assert (
        _run(tmp_path, "--code", "padded_code", "--answers", f"{questions}")
        == 0
    )
    capsys.readouterr()
    settings = json.loads(
        (tmp_path / "clinic-profile.json").read_text(encoding="utf-8")
    )["settings"]
    assert settings["forced_codes"] == []
    assert settings["forced_measurements"] == ["padded_code"]


def test_the_run_says_the_answered_file_is_written_again(
    tmp_path: pathlib.Path, capsys
) -> None:
    """A person who spent ten minutes filling it in is told first."""
    assert _run(tmp_path) == 0
    capsys.readouterr()
    questions = tmp_path / "clinic-questions.json"
    _answered(questions, "padded_code", asking.ANSWER_CODE)
    assert _run(tmp_path, "--answers", f"{questions}") == 0
    said = capsys.readouterr().out
    assert "written again" in said
    assert said.index("written again") < said.index("Written:"), (
        "before the write, not after it"
    )
    fresh = json.loads(questions.read_text(encoding="utf-8"))
    assert "padded_code" not in [
        entry["column"] for entry in fresh["asked"]
    ], "and the successor no longer asks what was answered"

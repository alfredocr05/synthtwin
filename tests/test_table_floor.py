"""P4-D425: the owner's table floor -- no twin of a small table.

THE GATE OF LANE POP. The owner, 2026-10-22: "we don't make twins of
small tables". `synthtwin profile` refuses, writing nothing, a table with
fewer than `parsing.TABLE_ROW_FLOOR` rows that hold a value, and a table
in which a declared or answered person column repeats but fewer than
`parsing.TABLE_PEOPLE_FLOOR` people appear. An OPEN person question never
refuses a table by itself. The floor is the command's: `cli.main`'s
internal `table_floor` keyword switches it off for the suite's helpers
and the measurement drivers, and no command line reaches it.

EVERY RUN HERE PASSES `table_floor=True` EXPLICITLY, because the suite's
conftest makes False the default for in-process runs; the one run that
does not pass it is the fresh interpreter, which is the installed command.
"""

import ast
import inspect
import json
import os
import pathlib
import subprocess
import sys

import pytest

from synthtwin import asking, cli, errors, parsing

ROWS = parsing.TABLE_ROW_FLOOR
PEOPLE = parsing.TABLE_PEOPLE_FLOOR


def _write(folder: pathlib.Path, lines: "list[str]") -> pathlib.Path:
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "clinic.csv"
    body = "\n".join(lines) + "\n"
    table.write_text(body, encoding="utf-8", newline="\n")
    return table


def _rows_table(folder: pathlib.Path, rows: int, blank_rows: int = 0) -> pathlib.Path:
    """``rows`` rows that hold a value, then ``blank_rows`` that hold none."""
    lines = ["age,site"]
    lines += [f"{20 + index % 60},{'north' if index % 3 else 'south'}" for index in range(rows)]
    lines += ["," for _blank in range(blank_rows)]
    return _write(folder, lines)


def _people_table(folder: pathlib.Path, people: int, rows: int = ROWS) -> pathlib.Path:
    """``rows`` rows over ``people`` people, every person on several rows."""
    lines = ["patient,age"]
    lines += [f"P{index % people:05d},{20 + index % 60}" for index in range(rows)]
    return _write(folder, lines)


def _profile(table: pathlib.Path, *extra: str) -> int:
    return cli.main(["profile", f"{table}", *extra], table_floor=True)


def _written(folder: pathlib.Path) -> "list[str]":
    return sorted(entry.name for entry in folder.iterdir())


@pytest.fixture(autouse=True)
def _nobody_at_the_keyboard(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "_there_is_somebody_to_ask", lambda: False)


# -- rows --------------------------------------------------------------------


def test_a_table_one_row_under_the_floor_is_refused_and_nothing_is_written(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    table = _rows_table(tmp_path, ROWS - 1)
    assert _profile(table) == 1
    said = capsys.readouterr().err
    assert f"{ROWS - 1:,} rows that hold a value" in said
    assert _written(tmp_path) == ["clinic.csv"]


def test_a_table_at_the_floor_is_described(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    table = _rows_table(tmp_path, ROWS)
    assert _profile(table) == 0
    capsys.readouterr()
    assert "clinic-profile.json" in _written(tmp_path)


def test_rows_that_hold_nothing_do_not_reach_the_floor(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """20,000 lines, one of them blank in every cell: 19,999 rows, refused."""
    table = _rows_table(tmp_path, ROWS - 1, blank_rows=1)
    assert _profile(table) == 1
    said = capsys.readouterr().err
    assert f"{ROWS - 1:,} rows that hold a value" in said
    assert _written(tmp_path) == ["clinic.csv"]


# -- people ------------------------------------------------------------------


def test_a_person_column_with_too_few_people_is_refused(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """999 people over 20,000 rows: the rows clear the floor, the people do not."""
    table = _people_table(tmp_path, PEOPLE - 1)
    assert _profile(table, "--identifier", "patient") == 1
    said = capsys.readouterr().err
    assert f"{PEOPLE - 1:,} people, counted by 'patient'" in said
    assert f"{ROWS:,} rows that hold a value" in said
    assert _written(tmp_path) == ["clinic.csv"]


def test_a_person_column_with_enough_people_is_described(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    table = _people_table(tmp_path, PEOPLE)
    assert _profile(table, "--identifier", "patient") == 0
    capsys.readouterr()
    document = json.loads((tmp_path / "clinic-profile.json").read_text(encoding="utf-8"))
    assert document["settings"]["person_columns"] == ["patient"]


def test_the_people_floor_needs_the_rows_too(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """1,000 people on 19,999 rows: enough people, too few rows."""
    table = _people_table(tmp_path, PEOPLE, rows=ROWS - 1)
    assert _profile(table, "--identifier", "patient") == 1
    capsys.readouterr()
    assert _written(tmp_path) == ["clinic.csv"]


# -- the open person question ------------------------------------------------


def _candidate_table(folder: pathlib.Path) -> pathlib.Path:
    """20,000 rows, a `subject_id` of 500 subjects nobody has declared."""
    lines = ["subject_id,score"]
    lines += [f"S{index % 500:04d},{index % 97}" for index in range(ROWS)]
    return _write(folder, lines)


def test_an_open_person_question_does_not_refuse_the_table(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Offered the person question and unanswered: counted in rows, described.

    And the screen says the people floor applies once the column is
    answered as one that names people.
    """
    table = _candidate_table(tmp_path)
    assert _profile(table) == 0
    screen = capsys.readouterr()
    said = screen.out + screen.err
    assert "counted in ROWS" in said and "subject_id" in said
    assert "--identifier subject_id" in said
    assert f"at least {PEOPLE:,} people" in said
    assert "An unanswered question does not refuse the table." in said
    written = json.loads((tmp_path / "clinic-questions.json").read_text(encoding="utf-8"))
    assert "subject_id" in [entry["column"] for entry in written["asked"]]


def test_at_the_keyboard_an_unanswered_question_does_not_refuse_either(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Somebody at the keyboard who answers nothing: described, and told."""
    monkeypatch.setattr(cli, "_there_is_somebody_to_ask", lambda: True)
    answers = iter([""] * 9)
    monkeypatch.setattr(cli, "_read_one_answer", lambda standing: next(answers))
    table = _candidate_table(tmp_path)
    assert _profile(table) == 0
    said = capsys.readouterr().err
    assert "counted in ROWS" in said
    assert f"at least {PEOPLE:,} people" in said


def test_the_same_column_answered_as_a_person_column_is_refused(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Answered at the keyboard: 500 people, and the second census refuses."""
    monkeypatch.setattr(cli, "_there_is_somebody_to_ask", lambda: True)
    answers = iter([asking.ANSWER_IDENTIFIER] + [""] * 8)
    monkeypatch.setattr(cli, "_read_one_answer", lambda standing: next(answers))
    table = _candidate_table(tmp_path)
    assert _profile(table) == 1
    said = capsys.readouterr().err
    assert "500 people, counted by 'subject_id'" in said
    assert _written(tmp_path) == ["clinic.csv"]


# -- the message -------------------------------------------------------------


def test_the_message_says_the_sizes_the_counts_why_and_what_to_do() -> None:
    said = errors.the_table_is_below_the_floor(20000, 999, "patient")
    for fact in (
        "20,000 rows that hold a value",
        "1,000 people",
        "This table holds 20,000 rows that hold a value and 999 people, counted by 'patient'",
        f"at least {parsing.DEFAULT_SMALL_CELL_FLOOR} people",
        "would not stand on the real table",
        "points to one person",
        "the whole extract rather than a sample",
        "combine sites or years",
        "Nothing was written.",
    ):
        assert fact in said, fact
    rows_only = errors.the_table_is_below_the_floor(812, 0, "")
    assert "This table holds 812 rows that hold a value." in rows_only
    assert "counted by" not in rows_only
    assert "\n" not in said


# -- the switch --------------------------------------------------------------


def test_the_notice_line_is_never_above_the_floor() -> None:
    """No table the floor accepts gets P4-D341's small-population notice."""
    assert parsing.POPULATION_FLOOR <= parsing.POPULATION_NOTICE_LINE
    assert parsing.POPULATION_NOTICE_LINE <= parsing.TABLE_PEOPLE_FLOOR
    assert parsing.TABLE_PEOPLE_FLOOR <= parsing.TABLE_ROW_FLOOR


def test_the_switch_changes_no_byte_at_the_floor(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    on = _people_table(tmp_path / "on", PEOPLE)
    off = _people_table(tmp_path / "off", PEOPLE)
    assert cli.main(["profile", f"{on}", "--identifier", "patient"], table_floor=True) == 0
    assert cli.main(["profile", f"{off}", "--identifier", "patient"], table_floor=False) == 0
    capsys.readouterr()
    names = _written(tmp_path / "on")
    assert names == _written(tmp_path / "off")
    assert len(names) > 1
    for name in names:
        assert (tmp_path / "on" / name).read_bytes() == (tmp_path / "off" / name).read_bytes(), name


def test_the_internal_parameter_is_keyword_only_and_on_by_default() -> None:
    """Read from the source: the suite's conftest moves the live default."""
    parameter = inspect.signature(cli.main).parameters["table_floor"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    function = ast.parse(inspect.getsource(cli.main).lstrip()).body[0]
    assert isinstance(function, ast.FunctionDef)
    names = [argument.arg for argument in function.args.kwonlyargs]
    assert names == ["table_floor"]
    default = function.args.kw_defaults[0]
    assert isinstance(default, ast.Constant) and default.value is True


def test_no_command_line_reaches_the_internal_parameter() -> None:
    """main hands its own keyword on untouched, and the parser has no such option."""
    tree = ast.parse(inspect.getsource(cli.main).lstrip())
    function = tree.body[0]
    assert isinstance(function, ast.FunctionDef)
    for node in ast.walk(function):
        for target in getattr(node, "targets", []) + [getattr(node, "target", None)]:
            assert not (isinstance(target, ast.Name) and target.id == "table_floor"), (
                "main assigns table_floor: something other than its caller sets it"
            )
    handed = [
        keyword.value
        for node in ast.walk(function)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_run_profile"
        for keyword in node.keywords
        if keyword.arg == "table_floor"
    ]
    assert len(handed) == 1
    assert isinstance(handed[0], ast.Name) and handed[0].id == "table_floor"
    parser_source = inspect.getsource(cli._parse_arguments)
    assert "table_floor" not in parser_source
    assert "table-floor" not in parser_source
    run_source = inspect.getsource(cli._run_profile)
    assert "environ" not in run_source and "getenv" not in run_source


def test_an_option_naming_the_floor_is_not_recognised(tmp_path: pathlib.Path) -> None:
    table = _rows_table(tmp_path, 50)
    for spelling in ("--table-floor", "--no-table-floor", "--small-tables", "--table_floor"):
        with pytest.raises(SystemExit) as stopped:
            cli.main(["profile", f"{table}", spelling], table_floor=True)
        assert stopped.value.code == 2, spelling


def test_the_installed_command_has_the_floor_on(tmp_path: pathlib.Path) -> None:
    """A fresh interpreter, no keyword, the environment named after the switch set."""
    table = _rows_table(tmp_path / "fresh", ROWS - 1)
    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join(sys.path)
    for name in ("SYNTHTWIN_TABLE_FLOOR", "TABLE_FLOOR", "SYNTHTWIN_SMALL_TABLES"):
        environment[name] = "0"
    done = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; from synthtwin.cli import main; sys.exit(main(sys.argv[1:]))",
            "profile",
            f"{table}",
        ],
        capture_output=True,
        text=True,
        env=environment,
        timeout=300,
        check=False,
    )
    assert done.returncode == 1, done.stderr
    assert "below its floor" in done.stderr
    assert _written(tmp_path / "fresh") == ["clinic.csv"]


# -- the census --------------------------------------------------------------


@pytest.mark.parametrize("declared", [[], ["p"]])
def test_the_rows_holding_a_value_are_counted_alike_whole_and_in_groups(
    declared: "list[str]", tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The floor's row count, read whole and a column group at a time (lane SR).

    420 lines, 60 of them holding nothing in any cell, 18 naming nobody:
    360 rows hold a value however the table is read, with a person
    column declared or not.
    """
    from synthtwin import profile, reading, taxonomy

    table = tmp_path / "people.csv"
    lines = ["p,x"]
    for row in range(420):
        if row % 7 == 0:
            lines += [","]
            continue
        lines += [f"{'' if row % 23 == 0 else f'P{row // 3:04d}'},{row % 5}"]
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    settings = taxonomy.Settings()
    whole = profile.population_and_rows_census_of(
        reading.read_table(str(table)), settings, declared, [], [], [], ()
    )
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    grouped = profile.population_and_rows_census_of(
        reading.read_table(str(table), in_groups=True), settings, declared, [], [], [], ()
    )
    assert whole[2] == grouped[2] == 360
    assert whole[:2] == grouped[:2]
    if declared:
        assert whole[0] == ("p",) and whole[1] < 360
    else:
        assert whole[1] == 360

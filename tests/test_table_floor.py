"""P4-D425: the owner's table floor -- no twin of a small table.

THE GATE OF LANE POP. The owner, 2026-10-22: "we don't make twins of
small tables". `synthtwin profile` refuses, writing nothing, a table with
fewer than `parsing.TABLE_ROW_FLOOR` rows that hold a value, and a table
in which a declared or answered person column repeats but fewer than
`parsing.TABLE_PEOPLE_FLOOR` people appear. An OPEN person question never
refuses a table by itself. The floor is the command's: `cli.main`'s
internal `small_tables_refused` keyword switches it off for the suite's helpers
and the measurement drivers, and no command line reaches it.

EVERY RUN HERE PASSES `small_tables_refused=True` EXPLICITLY, because the suite's
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

import environment_audit
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
    lines = ["patient,reading"]
    lines += [f"P{index % people:05d},{20 + index % 60}" for index in range(rows)]
    return _write(folder, lines)


def _profile(table: pathlib.Path, *extra: str) -> int:
    return cli.main(["profile", f"{table}", *extra], small_tables_refused=True)


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


def test_the_second_census_counts_merged_people_and_names_the_run_s_group(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Answered at the keyboard, 600 subjects each written two ways: 600 people, group 20.

    The census after the answer counts people with one person's
    spellings merged (as the first does), and its message names the
    run's smallest group (POP verify item 3).
    """
    monkeypatch.setattr(cli, "_there_is_somebody_to_ask", lambda: True)
    answers = iter([asking.ANSWER_IDENTIFIER] + [""] * 20)
    monkeypatch.setattr(cli, "_read_one_answer", lambda standing: next(answers))
    lines = ["subject_id,score"]
    for index in range(ROWS):
        subject = index % 600
        spelled = f"S{subject:04d}" if (index // 600) % 2 == 0 else f"S-{subject:04d}"
        lines += [f"{spelled},{index % 97}"]
    table = _write(tmp_path, lines)
    assert _profile(table, "--smallest-group", "20") == 1
    said = capsys.readouterr().err
    assert "600 people, counted by 'subject_id'" in said
    assert "at least the smallest group, 20 (" in said
    assert _written(tmp_path) == ["clinic.csv"]


# -- the message -------------------------------------------------------------


def test_the_message_says_the_sizes_the_counts_why_and_what_to_do() -> None:
    """The facts, and a why that claims no more than holds (skeptic 1, item 5; Codex item 1).

    Just under the floor a column of a few common levels publishes
    every level, so the message may not say MOST groups are withheld;
    the smallest group is the run's (it is configurable) and is counted
    in rows where no column names the person.
    """
    said = errors.the_table_is_below_the_floor(20000, 999, "patient", 11)
    for fact in (
        "a policy for every table synthtwin twins",
        "20,000 rows that hold a value",
        "1,000 people",
        "This table holds 20,000 rows that hold a value and 999 people, counted by 'patient'",
        "apart from case, spaces, punctuation and leading zeros, are one person",
        "at least the smallest group, 11 (11, or more if you raised it with --smallest-group)",
        "counted in people where a column names the person and in rows where none does",
        "the more of its counts",
        "stands less well on the real table",
        "can point to one person",
        "the whole extract rather than a sample",
        "combine sites or years",
        "Nothing was written.",
    ):
        assert fact in said, fact
    # The owner, 2026-10-23: the floor of 11 is a minimum; no message
    # suggests lowering it (lane POP's addendum, ruling (3)).
    for claim in (
        "most of its groups",
        "every count a description publishes",
        "would not stand",
        "unless",
        "set another",
        "lower",
    ):
        assert claim not in said, claim
    raised = errors.the_table_is_below_the_floor(20000, 999, "patient", 20)
    assert "at least the smallest group, 20 (" in raised
    rows_only = errors.the_table_is_below_the_floor(812, 0, "", 11)
    assert "This table holds 812 rows that hold a value." in rows_only
    assert "counted by" not in rows_only
    assert "\n" not in said


def test_the_refusal_names_the_run_s_smallest_group(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    table = _rows_table(tmp_path, ROWS - 1)
    assert _profile(table, "--smallest-group", "20") == 1
    assert "at least the smallest group, 20 (" in capsys.readouterr().err


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
    assert cli.main(["profile", f"{on}", "--identifier", "patient"], small_tables_refused=True) == 0
    assert cli.main(["profile", f"{off}", "--identifier", "patient"], small_tables_refused=False) == 0
    capsys.readouterr()
    names = _written(tmp_path / "on")
    assert names == _written(tmp_path / "off")
    assert len(names) > 1
    for name in names:
        assert (tmp_path / "on" / name).read_bytes() == (tmp_path / "off" / name).read_bytes(), name


def test_the_internal_parameter_is_keyword_only_and_on_by_default() -> None:
    """Read from the source: the suite's conftest moves the live default."""
    parameter = inspect.signature(cli.main).parameters["small_tables_refused"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    function = ast.parse(inspect.getsource(cli.main).lstrip()).body[0]
    assert isinstance(function, ast.FunctionDef)
    names = [argument.arg for argument in function.args.kwonlyargs]
    # Lane MIN's `internal_smallest_group` beside it (plan P4-D426,
    # batch 4i's integration): both keyword only, each off by default.
    assert names == ["small_tables_refused", "internal_smallest_group"]
    defaults = function.args.kw_defaults
    assert isinstance(defaults[0], ast.Constant) and defaults[0].value is True
    assert isinstance(defaults[1], ast.Constant) and defaults[1].value is None


def test_no_command_line_reaches_the_internal_parameter() -> None:
    """main hands its own keyword on untouched, and the parser has no such option."""
    tree = ast.parse(inspect.getsource(cli.main).lstrip())
    function = tree.body[0]
    assert isinstance(function, ast.FunctionDef)
    for node in ast.walk(function):
        for target in getattr(node, "targets", []) + [getattr(node, "target", None)]:
            assert not (isinstance(target, ast.Name) and target.id == "small_tables_refused"), (
                "main assigns small_tables_refused: something other than its caller sets it"
            )
    handed = [
        keyword.value
        for node in ast.walk(function)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_run_profile"
        for keyword in node.keywords
        if keyword.arg == "small_tables_refused"
    ]
    assert len(handed) == 1
    assert isinstance(handed[0], ast.Name) and handed[0].id == "small_tables_refused"
    parser_source = inspect.getsource(cli._parse_arguments)
    assert "small_tables_refused" not in parser_source
    assert "table-floor" not in parser_source
    run_source = inspect.getsource(cli._run_profile)
    assert "environ" not in run_source and "getenv" not in run_source


def test_an_option_naming_the_floor_is_not_recognised(tmp_path: pathlib.Path) -> None:
    table = _rows_table(tmp_path, 50)
    for spelling in ("--table-floor", "--no-table-floor", "--small-tables", "--small_tables_refused"):
        with pytest.raises(SystemExit) as stopped:
            cli.main(["profile", f"{table}", spelling], small_tables_refused=True)
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
    assert whole[3] == grouped[3] == 360
    assert whole[:3] == grouped[:3]
    if declared:
        assert whole[0] == ("p",) and whole[1] < 360
        assert whole[2] == whole[1]
    else:
        assert whole[1] == whole[2] == 360


# -- one person written several ways (skeptic 1, item 2) ----------------------

_TWO_WAYS = {
    "dash": (lambda person: f"P{person:05d}", lambda person: f"P-{person:05d}"),
    "zeros": (lambda person: f"{person + 1:06d}", lambda person: f"{person + 1}"),
    "space": (lambda person: f"P {person:05d}", lambda person: f"P{person:05d}"),
}


def _spelled_table(folder: pathlib.Path, people: int, way: str) -> pathlib.Path:
    """20,000 rows over ``people`` people, each person written two ways."""
    first, second = _TWO_WAYS[way]
    lines = ["patient,reading"]
    for index in range(ROWS):
        person = index % people
        spelling = first if (index // people) % 2 == 0 else second
        lines += [f"{spelling(person)},{20 + index % 60}"]
    return _write(folder, lines)


@pytest.mark.parametrize("way", sorted(_TWO_WAYS))
def test_one_person_written_two_ways_is_one_person_to_the_floor(
    way: str, tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """600 people, each written two ways: 600 to the floor, as the description counts them.

    `taxonomy.people_in` folds case and space only and counts 1,200;
    `profile.subject_keys`, which the description publishes by, merges
    each pair, and so does the floor (`parsing.subject_key`).
    """
    table = _spelled_table(tmp_path, 600, way)
    assert _profile(table, "--identifier", "patient") == 1
    said = capsys.readouterr().err
    assert "600 people, counted by 'patient'" in said
    assert _written(tmp_path) == ["clinic.csv"]


def test_a_thousand_people_written_two_ways_are_described(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    table = _spelled_table(tmp_path, PEOPLE, "dash")
    assert _profile(table, "--identifier", "patient") == 0
    capsys.readouterr()
    assert "clinic-profile.json" in _written(tmp_path)


def test_the_merged_count_is_alike_whole_and_in_groups(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """And P4-D341's population stays `people_in`'s: only the floor reads the merged count."""
    from synthtwin import profile, reading, taxonomy

    table = tmp_path / "spelled.csv"
    lines = ["p,x"]
    for row in range(400):
        person = row % 40
        lines += [f"{f'R{person:03d}' if (row // 40) % 2 else f'r-{person}'},{row % 5}"]
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    settings = taxonomy.Settings()
    whole = profile.population_and_rows_census_of(
        reading.read_table(str(table)), settings, ["p"], [], [], [], ()
    )
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    grouped = profile.population_and_rows_census_of(
        reading.read_table(str(table), in_groups=True), settings, ["p"], [], [], [], ()
    )
    assert whole[:4] == grouped[:4]
    assert whole[1] == 80 and whole[2] == 40 and whole[3] == 400


# -- the conftest's default survives a test's own undo (skeptic 1, item 1 (b)) --


def test_a_test_that_undoes_its_monkeypatch_still_describes_a_small_table(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """46 tests call `monkeypatch.undo()` part way; the refusal stays off for them (150 rows: above P4-D341's 100)."""
    monkeypatch.undo()
    monkeypatch.setattr(cli, "_there_is_somebody_to_ask", lambda: False)
    table = _rows_table(tmp_path, 150)
    assert cli.main(["profile", f"{table}"]) == 0
    capsys.readouterr()
    assert "clinic-profile.json" in _written(tmp_path)


# -- what the person reads before any run (skeptic 1, item 3 (a); Codex item 2) --


def test_the_status_screen_and_the_package_say_the_new_floor() -> None:
    import synthtwin

    for text in (cli._STATUS, f"{synthtwin.__doc__}"):
        flat = " ".join(text.split())
        assert "smallest table" not in flat
        assert "20,000 rows that hold a value" in flat
        assert "1,000 people" in flat


# -- nothing reaches the refusal but the keyword (skeptic 1, item 4) -----------


# THE ONE ENVIRONMENT READ THE PACKAGE MAKES (batch 4i's integration;
# narrowed by batch 4j's records on Codex's review of batch 4i): lane
# CHa's `installation.data_folder` finds the platform's data folder
# (contract 4.6b.4) from LOCALAPPDATA or XDG_DATA_HOME, behind the
# chain's switch. Only its one audited read is set aside, and only while
# the function keeps the audited structure (`environment_audit`), so a
# third key, a computed key or the environment used for anything but the
# folder fails here.


def _environment_readers(name: str, source: str) -> "list[str]":
    """Every read of the environment in one module of the package, and every way `data_folder` leaves its audited structure."""
    tree = ast.parse(source)
    aside, found = environment_audit.data_folder_set_aside(name, tree)
    for node in ast.walk(tree):
        if id(node) in aside:
            continue
        if isinstance(node, ast.Attribute) and node.attr in ("environ", "getenv", "environb", "getenvb"):
            found += [f"{name}:{node.lineno}"]
        if isinstance(node, ast.Name) and node.id in ("environ", "getenv"):
            found += [f"{name}:{node.lineno}"]
        if isinstance(node, ast.alias) and node.name in ("environ", "getenv"):
            found += [f"{name}"]
    return found


def test_no_module_of_the_package_reads_the_environment() -> None:
    """S6: an environment variable that switched the refusal off would be a bypass."""
    package = pathlib.Path(cli.__file__).parent
    found: "list[str]" = []
    for path in sorted(package.glob("*.py")):
        found += _environment_readers(path.name, path.read_text(encoding="utf-8"))
    assert found == []


@pytest.mark.parametrize("case", sorted(environment_audit.MUTANTS))
def test_the_data_folder_s_exemption_takes_no_other_environment_read(case: str) -> None:
    """Codex's review of batch 4i: a third key, a computed key, the environment used past the folder: each fails the check."""
    path = pathlib.Path(cli.__file__).parent / "installation.py"
    source = path.read_text(encoding="utf-8")
    assert _environment_readers("installation.py", source) == []
    assert _environment_readers("installation.py", environment_audit.mutated(source, case)) != []


def _every_option() -> "list[str]":
    """The option strings of the parser `cli._parse_arguments` builds, read off it."""
    import argparse

    seen: "list[str]" = []
    original = argparse.ArgumentParser.parse_known_args

    def caught(self: argparse.ArgumentParser, *arguments: object, **keywords: object) -> object:
        for action in self._actions:
            seen.extend(action.option_strings)
        raise SystemExit(0)

    argparse.ArgumentParser.parse_known_args = caught  # type: ignore[assignment,method-assign]
    try:
        with pytest.raises(SystemExit):
            cli._parse_arguments(["profile", "x.csv"], None)
    finally:
        argparse.ArgumentParser.parse_known_args = original  # type: ignore[method-assign]
    return sorted(seen)


# A valid value for each option on the 19,999-row `age,site` table; each
# run reaches the refusal (measured: all 21 exit 1 with the floor's
# message). Help and the version stop before any table is read, and are
# asked only to write nothing.
_VALUES: "dict[str, list[str]]" = {
    "--answers": ["@answers"],
    "--century": ["age=1900"],
    "--code": ["site"],
    "--date-column": ["age"],
    "--date-count": ["age", "excel-1900"],
    "--day-first": [],
    "--decimal-comma": ["age"],
    "--delimiter": [","],
    "--first-row": ["names"],
    "--identifier": ["age"],
    "--keep-value": ["north"],
    "--measurement": ["age"],
    "--metadata-rows": ["0"],
    "--missing-value": ["-999"],
    "--out-dir": ["@out"],
    "--replace": [],
    "--seed": ["7"],
    "--sheet": ["Sheet1"],
    "--smallest-group": ["20"],
    "--twelve-hour": ["age"],
    "--twin": ["@twin"],
}
_STOPS_FIRST = ("-h", "--help", "--version")


def test_no_option_of_the_command_lets_a_small_table_through(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """S7: every option the parser has, with a valid value, on 19,999 rows: never described.

    The list is read off the parser itself, so an option added later is
    asked too (the test fails until it is given a value here).
    """
    options = _every_option()
    assert sorted(set(options) - set(_STOPS_FIRST)) == sorted(_VALUES)
    table = _rows_table(tmp_path / "t", ROWS - 1)
    # A real questions file, from a small table described with the
    # refusal off, so --answers is read rather than refused.
    asked = _write(tmp_path / "q", ["subject_id,score"] + [f"S{index % 50:04d},{index % 97}" for index in range(150)])
    assert cli.main(["profile", f"{asked}"], small_tables_refused=False) == 0
    answers = tmp_path / "q" / "clinic-questions.json"
    places = {"@answers": f"{answers}", "@out": f"{tmp_path / 'out'}", "@twin": f"{tmp_path / 'twin.csv'}"}
    for option in options:
        given = [places.get(value, value) for value in _VALUES.get(option, [])]
        try:
            code = _profile(table, option, *given)
        except SystemExit as stopped:
            code = stopped.code if isinstance(stopped.code, int) else 2
        said = capsys.readouterr()
        if option in _STOPS_FIRST:
            assert _written(tmp_path / "t") == ["clinic.csv"], option
            continue
        assert code == 1, option
        assert "below its floor" in said.err, option
        assert _written(tmp_path / "t") == ["clinic.csv"], option
        assert not (tmp_path / "out").exists(), option
    for value in ("11", "50"):
        assert _profile(table, "--smallest-group", value) == 1
        assert "below its floor" in capsys.readouterr().err

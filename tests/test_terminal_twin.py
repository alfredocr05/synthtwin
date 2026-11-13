"""Lane TT's gate: one command for the whole journey (plan P4-D460).

The owner, 2026-10-15: "we can run the app in the terminal, however the
instructions and the way to make the application to run needs to be
easy anyway!". This file holds what lane TT built to that:

* `synthtwin twin TABLE` runs profile, the questions on screen, generate
  and validate in one run and one folder; nothing is written before the
  questions are answered (a run stopped at the first question leaves no
  file and no folder); the answers stay in the folder's questions file,
  and a second run there asks nothing and writes the same six files;
  its six files and its screen are the three commands' own, run apart
  with the same words (HIPAA first: the twin shows nothing the three
  commands do not, and no record number, ZIP code or birth date of the
  table reaches its screen or its saved answers);
* ONE OVERWRITE RULE: profile, generate, validate and twin each refuse a
  file already at one of their names, in one template's words, unless
  `--replace` says so (and profile's answers round, `--answers`, as it
  always has);
* one help page of at most 60 lines for each command, plus the examples
  page, reached through the one parser;
* the measures of `K-S8-01`, `K-S8-03` and `K-S8-05`.

THE TABLES ARE AT THE TABLE FLOOR (plan P4-D425; LANE I4m RULINGS 18):
20,000 rows, through the shipped command (`small_tables_refused` on).
Every run at that size is made once a process (`journey`) and read by
every case here and by the ledger's tests (`tests/test_kpi_ledger.py`).
The held table's runs (`held`, `entered`) are read by the gate's second
file, `tests/test_terminal_twin_held.py`, and the three commands run apart
beside them (`apart`) by `K-S8-03`'s driver alone (`apart_measures`): the
orchestrator's LANE TT RULINGS 2 (7)(b) and LANE I4m RULINGS 21 (9)
judge a gate file by its CPU seconds, at most 180. The cases on the
library's small-table path (`_library`) are test devices for what no
table size changes: a command line's meaning.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import random
import re
import shutil
import time
import typing

import pytest

import stage5_battery as battery
from synthtwin import cli, errors, parsing, results

ROWS = battery.TABLE_ROWS
_RECORD = re.compile(r"REC[0-9]{6}")
_FIVE = re.compile(r"(?<![0-9])[0-9]{5}(?![0-9])")
_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


_FOLIO = re.compile(r"(?<![0-9.])[0-9]{8}(?![0-9])")
_PATIENT = re.compile(r"PT[0-9]{5}")
_STAMP = re.compile(r"(?<![0-9.])[0-9]{10}(?![0-9])")
_ZIP = re.compile(r"(?<![0-9.])[0-9]{5}(?![0-9.])")


def held_table(n_rows: int) -> str:
    """Step 0's columns with a ZIP code and a birth date beside them, and every kind of question the prompt puts (invented, seeded).

    The record number is `REC` and six figures, one a row; the ZIP code is
    five figures from 40001 to 48999, odd, so no count on a screen can be
    one; the birth date is a full date from 1921 to 1990, so some show an
    age over 89; the weight runs to 104, which the Safe Harbor question
    top-codes. Beside them, one column for each kind of question the
    prompt puts (lane TT's repair, the orchestrator's LANE TT RULINGS 2
    (1)): `folio`, eight figures (the fixed-width question, offering
    `identifier`); `patient`, `PT` and five figures, 1,600 of them on
    about twelve rows each (the person question); `stamp`, ten figures
    from 1,600,000,000 (a count of seconds, the date-counting question);
    `stature`, a number and `cm` (the unit question: codes against
    measurements); `clock`, a time of day from 1:00 to 12:45 (the
    12-hour question). The record number's question is the one of numbers
    each on one row, and the ZIP code's the date-counting one. Built from
    `random.Random` and its `random()` stream alone.
    """
    stream = random.Random(4600)
    rows = ["record_no,zip,born,weight,ward,folio,patient,stamp,stature,clock"]
    for index in range(n_rows):
        zip_five = 40001 + 2 * int(stream.random() * 4400)
        year = 1921 + int(stream.random() * 70)
        month = 1 + int(stream.random() * 12)
        day = 1 + int(stream.random() * 28)
        weight = 50.0 + 18.0 * (stream.random() + stream.random() + stream.random())
        ward = battery.WARDS[int(stream.random() * len(battery.WARDS))]
        folio = 70000000 + int(stream.random() * 9000000)
        patient = 10000 + int(stream.random() * 1600)
        stamp = 1600000000 + int(stream.random() * 100000000)
        stature = 150 + int(stream.random() * 50)
        hour = 1 + int(stream.random() * 12)
        minute = 15 * int(stream.random() * 4)
        rows += [
            f"REC{200000 + index},{zip_five},{year}-{month:02d}-{day:02d},"
            f"{weight:.1f},{ward},{folio},PT{patient},{stamp},{stature} cm,"
            f"{hour}:{minute:02d}"
        ]
    return "\n".join(rows) + "\n"


def _run(
    argv: "typing.Sequence[str]",
    folder: pathlib.Path,
    ask: "list[str | None] | None" = None,
) -> "tuple[results.Result, list[tuple[str, str]]]":
    """One command line through `cli.run` in ``folder``, as the shipped command runs it."""
    here = os.getcwd()
    os.chdir(folder)
    try:
        screen: "list[tuple[str, str]]" = []
        result = cli.run(list(argv), screen=screen, ask=ask, small_tables_refused=True)
    finally:
        os.chdir(here)
    return result, screen


def _digests(folder: pathlib.Path) -> "dict[str, str]":
    """Each file of ``folder`` by name, by SHA-256."""
    return {
        one.name: hashlib.sha256(one.read_bytes()).hexdigest()
        for one in sorted(folder.iterdir())
        if one.is_file()
    }


def _everything_under(folder: pathlib.Path) -> "list[str]":
    """Every file and folder under ``folder``, by its path from there."""
    return sorted(f"{one.relative_to(folder)}" for one in folder.rglob("*"))


def _text(screen: "list[tuple[str, str]]") -> str:
    return "".join(text for _stream, text in screen)


def _teaching(screen: "list[tuple[str, str]]") -> "list[tuple[str, str]]":
    """A command's screen less its next-command teaching lines, which a twin's step does not show."""
    return [
        (stream, text)
        for stream, text in screen
        if not text.startswith("\nNext, build the twin from this description:")
        and not text.startswith("\nNext, measure the twin against the description:")
    ]


_JOURNEY: "dict[str, typing.Any]" = {}
_HELD: "dict[str, typing.Any]" = {}
_APART: "dict[str, typing.Any]" = {}
_ENTERED: "dict[str, typing.Any]" = {}


def journey(root: pathlib.Path) -> "dict[str, typing.Any]":
    """The runs on Step 0's table this file and the ledger read, made once a process under ``root``.

    On Step 0's table (the stage-5 battery's, 20,000 rows): A, a twin
    whose reader ends input at the first question; B, the same from that
    folder with the record number answered `identifier` (key 3) at the
    one question put; C, B again without `--replace`; D, B again with
    `--replace` and a reader of no lines, which would end the run at any
    question put, its three steps profile, generate and validate each
    writing over its own files with `--replace`. Then, in the same folder,
    profile, generate and validate each again without `--replace`. The
    held table's runs are `held`, `entered` and `apart`, each made only
    where a case reads it.
    """
    if _JOURNEY:
        return _JOURNEY
    home = root / "journey"
    home.mkdir(parents=True)
    home = home.resolve()
    (home / "t.csv").write_text(battery.step0_table(ROWS), encoding="utf-8", newline="\n")
    found: "dict[str, typing.Any]" = {"home": home}
    found["A"] = _run(["twin", "t.csv"], home, ask=[])
    found["after_A"] = _everything_under(home)
    started = time.perf_counter()
    found["B"] = _run(["twin", "t.csv"], home, ask=["3"])
    found["B_seconds"] = time.perf_counter() - started
    folder = home / "t-synthtwin"
    found["folder"] = folder
    found["after_B"] = _digests(folder)
    found["C"] = _run(["twin", "t.csv"], home, ask=[])
    found["after_C"] = _digests(folder)
    found["D"] = _run(["twin", "t.csv", "--replace"], home, ask=[])
    found["after_D"] = _digests(folder)
    description = f"{folder / 't-profile.json'}"
    each = (
        ("profile", ["profile", "t.csv", f"--out-dir={folder}"]),
        ("generate", ["generate", description, f"--out-dir={folder}"]),
        ("validate", ["validate", description, f"--out-dir={folder}"]),
    )
    for command, argv in each:
        before = _digests(folder)
        found[f"{command}_refused"] = _run(argv, home, ask=[])
        found[f"{command}_unchanged"] = _digests(folder) == before
    # ...and the same table at the keyboard with Enter pressed at its one
    # question (lane TT's repair, the orchestrator's LANE TT RULINGS 2
    # (2)): B_enter, then D_enter, its folder again with `--replace` and a
    # reader of no lines.
    pressed = root / "pressed"
    pressed.mkdir()
    pressed = pressed.resolve()
    (pressed / "t.csv").write_text(battery.step0_table(ROWS), encoding="utf-8", newline="\n")
    found["B_enter"] = _run(["twin", "t.csv"], pressed, ask=[""] * 8)
    found["after_B_enter"] = _digests(pressed / "t-synthtwin")
    found["D_enter"] = _run(["twin", "t.csv", "--replace"], pressed, ask=[])
    found["after_D_enter"] = _digests(pressed / "t-synthtwin")
    _JOURNEY.update(found)
    return _JOURNEY


def held(root: pathlib.Path) -> "dict[str, typing.Any]":
    """E: a twin of the held table with nobody at the keyboard, made once a process under ``root``, timed."""
    if _HELD:
        return _HELD
    home = root / "held"
    home.mkdir(parents=True)
    home = home.resolve()
    (home / "h.csv").write_text(held_table(ROWS), encoding="utf-8", newline="\n")
    found: "dict[str, typing.Any]" = {"held_home": home}
    started = time.perf_counter()
    found["E"] = _run(["twin", "h.csv"], home)
    found["E_seconds"] = time.perf_counter() - started
    found["E_files"] = _digests(home / "h-synthtwin")
    found["E_description"] = (home / "h-synthtwin" / "h-profile.json").read_text(encoding="utf-8")
    found["E_questions"] = (home / "h-synthtwin" / "h-questions.json").read_text(encoding="utf-8")
    found["E_twin"] = (home / "h-synthtwin" / "h-twin.csv").read_text(encoding="utf-8")
    found["E_real"] = (home / "h.csv").read_text(encoding="utf-8")
    _HELD.update(found)
    return _HELD


def entered(root: pathlib.Path) -> "dict[str, typing.Any]":
    """The held table at the keyboard, Enter pressed at every question, then the same folder again (lane TT's repair).

    In E's folder, over E's files once they are counted: E_enter, a twin
    whose person presses Enter at every question the prompt puts, writing
    into the folder E wrote, so every path any file names is E's.
    """
    if _ENTERED:
        return _ENTERED
    home = held(root)["held_home"]
    target = home / "h-synthtwin"
    shutil.rmtree(target)
    found: "dict[str, typing.Any]" = {}
    found["E_enter"] = _run(["twin", "h.csv"], home, ask=[""] * 40)
    found["E_enter_files"] = _digests(target)
    found["E_enter_description"] = (target / "h-profile.json").read_text(encoding="utf-8")
    found["E_enter_twin"] = (target / "h-twin.csv").read_text(encoding="utf-8")
    _ENTERED.update(found)
    return _ENTERED


def entered_again(root: pathlib.Path) -> "dict[str, typing.Any]":
    """E_again: E_enter's folder again with `--replace` and a reader of no lines, which would end the run at any question put."""
    found = entered(root)
    if "E_again" not in found:
        home = held(root)["held_home"]
        found["E_again"] = _run(["twin", "h.csv", "--replace"], home, ask=[])
        found["E_again_files"] = _digests(home / "h-synthtwin")
    return found


def apart(root: pathlib.Path) -> "dict[str, typing.Any]":
    """The three commands run apart on the held table with the twin's words, into E's folder, timed."""
    if _APART:
        return _APART
    home = held(root)["held_home"]
    target = home / "h-synthtwin"
    shutil.rmtree(target)
    target.mkdir()
    made = f"{target / 'h-profile.json'}"
    found: "dict[str, typing.Any]" = {}
    started = time.perf_counter()
    found["E_apart"] = [
        _run(["profile", "h.csv", f"--out-dir={target}"], home),
        _run(["generate", made, f"--out-dir={target}", "--seed=0"], home),
        _run(["validate", made, f"--out-dir={target}"], home),
    ]
    found["E_apart_seconds"] = time.perf_counter() - started
    found["E_apart_files"] = _digests(target)
    found["E_apart_questions"] = (target / "h-questions.json").read_text(encoding="utf-8")
    _APART.update(found)
    return _APART


@pytest.fixture(scope="module")
def ran(tmp_path_factory: pytest.TempPathFactory) -> "dict[str, typing.Any]":
    return journey(tmp_path_factory.mktemp("twin"))




# -- the measures (K-S8-01, K-S8-03, K-S8-05) ----------------------------


def journey_measures(root: pathlib.Path) -> "dict[str, int]":
    """`K-S8-01`: from a folder holding only a battery table to a validated twin.

    * `install_commands`: the one install command of README's install
      block (lane TI's scripts), counted as lane TI counts it;
    * `run_commands`: the command lines the journey typed: B alone, one
      `synthtwin twin t.csv` in a folder that held only the table, whose
      validate step reached its end with no obligation missed and wrote
      the quality report;
    * `hand_edited_files`: the files the journey wrote or edited by hand
      before and between its commands (none: the questions were answered
      on screen).
    """
    import test_terminal_install as terminal

    found = journey(root)
    made, _screen = found["B"]
    validated = [step for step in made.steps if step.command == results.VALIDATE]
    reached = int(
        len(validated) == 1
        and validated[0].verdict == results.NO_MISS
        and any(one.kind == results.FILE_QUALITY_REPORT for one in made.files)
    )
    return {
        "install_commands": terminal.journey_measures()["install_commands"],
        "run_commands": 1 if reached else 0,
        "hand_edited_files": 0 if found["after_A"] == ["t.csv"] else 1,
    }


def rule_measures(root: pathlib.Path) -> "dict[str, int]":
    """`K-S8-03`: nothing written before the answers; a second run asks nothing; one overwrite rule.

    * `files_written_before_the_answers`: the files and folders a twin
      stopped at its first question left beside the table (A);
    * `questions_put_on_a_second_run`: the questions D's profile step put
      at a prompt, D's reader holding no line (so a question put would
      have stopped it), plus 1 where D did not finish or wrote six files
      other than B's; and the same of D_enter after B_enter, the first
      run answered with Enter at its question (lane TT's repair, the
      orchestrator's LANE TT RULINGS 2 (2): answers typed by number, and
      Enter, are reused byte for byte; the held table's own case is
      `tests/test_terminal_twin_held.py`'s);
    * `commands_under_one_overwrite_rule`: of profile, generate, validate
      and twin, those that refused a name already taken -- exit 1, step
      `outputs`, the folder unchanged, the words the one template writes
      -- and wrote over it with `--replace`.
    """
    found = journey(root)
    stopped, _screen = found["A"]
    after = [name for name in found["after_A"] if name != "t.csv"]
    put = 0
    for again, first, later in (
        (found["D"][0], found["after_B"], found["after_D"]),
        (found["D_enter"][0], found["after_B_enter"], found["after_D_enter"]),
    ):
        put = put + (dict(again.steps[0].tally).get("questions-put", 1) if again.steps else 1)
        if again.verdict not in (results.NO_MISS, results.MISSED) or later != first:
            put = put + 1
    again, _again_screen = found["D"]
    kept = 0
    template = (
        ("profile", errors.DESCRIBING_AGAIN),
        ("generate", errors.BUILDING_AGAIN),
        ("validate", errors.CHECKING_AGAIN),
    )
    for place, (command, usual) in enumerate(template):
        refused, _shown = found[f"{command}_refused"]
        # ...and written over with --replace: D's step of that command,
        # which ran with it over the files B left.
        replaced = again.steps[place] if place < len(again.steps) else None
        if (
            _refused_by_the_rule(refused, found[f"{command}_unchanged"], usual)
            and replaced is not None
            and replaced.command == command
            and replaced.verdict in (results.NO_MISS, results.MISSED)
        ):
            kept = kept + 1
    twice, _twice_screen = found["C"]
    if _refused_by_the_rule(twice, found["after_C"] == found["after_B"], errors.MAKING_AGAIN) and again.verdict in (
        results.NO_MISS,
        results.MISSED,
    ):
        kept = kept + 1
    return {
        "files_written_before_the_answers": len(after) + (0 if stopped.verdict == results.REFUSED else 1),
        "questions_put_on_a_second_run": put,
        "commands_under_one_overwrite_rule": kept,
    }


def apart_measures(root: pathlib.Path) -> "dict[str, int]":
    """`K-S8-03`'s fourth key, measured by its driver alone: the twin's files and screen against the three commands run apart.

    Moved out of the gate by the orchestrator's LANE TT RULINGS 2 (7)(b),
    the gate files judged by CPU seconds. E, the held table's twin with
    nobody at the keyboard, against profile, generate and validate run
    apart with the twin's words into E's folder: its five other files
    byte for byte, its questions file the profile command's own but for
    the one sentence binding its answers to the table read
    (`cli._bound_reading`), its screen theirs less two teaching lines
    (validate's exit line naming the twin's status, 3 where generate
    missed), and its own lines -- the folder, where the answers stay, the
    next command -- naming no record number, five figures or date.
    HIPAA FIRST: so the twin shows nothing the three commands do not.

    * `twin_other_than_the_three_commands_apart`: of those four, the ones
      that do not hold;
    * `questions_put_on_a_second_run`: the held table's own Enter-first
      second run, E_again after E_enter, counted as `rule_measures` counts
      D's (the orchestrator's LANE TT RULINGS 2 (2): skeptic 1's table,
      where a second run once counted the ZIP code as the person column),
      the driver adding it to the gate's count of D and D_enter.
    """
    pressed = entered_again(root)
    again = pressed["E_again"][0]
    put = dict(again.steps[0].tally).get("questions-put", 1) if again.steps else 1
    if again.verdict not in (results.NO_MISS, results.MISSED) or pressed["E_again_files"] != pressed["E_enter_files"]:
        put = put + 1
    found = held(root)
    apart_found = apart(root)
    other = 0
    alike = [name for name in found["E_files"] if name != "h-questions.json"]
    if len(alike) != 5 or {name: found["E_files"][name] for name in alike} != {
        name: apart_found["E_apart_files"].get(name) for name in alike
    }:
        other = other + 1
    own = json.loads(found["E_questions"])
    apart_own = json.loads(apart_found["E_apart_questions"])
    bound = [one for one in own["about_your_table"] if one not in apart_own["about_your_table"]]
    own["about_your_table"] = apart_own["about_your_table"]
    if len(bound) != 1 or not bound[0].startswith(cli._BINDING_HEAD) or own != apart_own:
        other = other + 1
    made, screen = found["E"]
    steps = apart_found["E_apart"]
    expected = _teaching(steps[0][1]) + _teaching(steps[1][1]) + steps[2][1]
    if len(made.steps) > 1 and made.steps[1].verdict == results.MISSED:
        expected = [
            (stream, text.replace("Automation saw exit code 0", "Automation saw exit code 3"))
            for stream, text in expected
        ]
    if list(screen[: len(expected)]) != expected:
        other = other + 1
    said = _text(screen[len(expected) :])
    if not said.startswith("\nThe twin's six files are in:\n") or (
        _RECORD.findall(said) + _FIVE.findall(said) + _DATE.findall(said)
    ):
        other = other + 1
    return {"twin_other_than_the_three_commands_apart": other, "questions_put_on_a_second_run": put}


def _refused_by_the_rule(result: results.Result, unchanged: bool, usual: str) -> bool:
    """Whether ``result`` is the one overwrite rule's refusal: exit 1, step outputs, its words, nothing changed."""
    return (
        unchanged
        and results.exit_code(result) == 1
        and result.refusal is not None
        and result.refusal.step == results.STEP_OUTPUTS
        and result.refusal.words.startswith(
            "synthtwin stopped because something is already at"
        )
        and f"the usual reason is {usual} -- add --replace" in result.refusal.words
    )


def help_measures() -> "dict[str, int]":
    """`K-S8-05`: the lines of each command's help page, and the examples page.

    * `longest_command_page_lines`: the most lines any of profile,
      generate, validate, doctor and twin's page holds, as
      `synthtwin COMMAND --help` shows it;
    * `command_pages`: the command words whose page is their own, at most
      60 lines of at most 79 characters, and the same page as `synthtwin
      help COMMAND`;
    * `examples_page_lines`: the lines `synthtwin help examples` shows.
    """
    longest = 0
    own = 0
    for command in ("profile", "generate", "validate", "doctor", "twin"):
        shown = _page(command, "--help")
        longest = max(longest, len(shown.splitlines()))
        if (
            shown == cli.command_page(command)
            and shown == _page("help", command)
            and len(shown.splitlines()) <= 60
            and max(len(line) for line in shown.splitlines()) <= 79
        ):
            own = own + 1
    return {
        "longest_command_page_lines": longest,
        "command_pages": own,
        "examples_page_lines": len(_page("help", "examples").splitlines()),
    }


def _page(first: str, second: str) -> str:
    """What `synthtwin FIRST SECOND` shows on standard output."""
    screen: "list[tuple[str, str]]" = []
    result = cli.run([first, second], screen=screen)
    assert result.command == results.HELP and result.verdict == results.NO_MISS
    assert all(stream == "out" for stream, _text in screen)
    return _text(screen)


# -- the KPIs' pinned cases -------------------------------------------------


def test_k_s8_01_one_install_and_one_run_command_reach_a_validated_twin(
    ran: "dict[str, typing.Any]",
) -> None:
    """`K-S8-01` at its target: 1 install command, 1 run command, 0 files edited by hand."""
    assert journey_measures(ran["home"].parent) == {
        "install_commands": 1,
        "run_commands": 1,
        "hand_edited_files": 0,
    }


def test_k_s8_03_nothing_before_the_answers_a_second_run_asks_nothing_one_rule(
    ran: "dict[str, typing.Any]",
) -> None:
    """`K-S8-03` all true: no file before the answers, no question on a second run, four commands under one rule."""
    assert rule_measures(ran["home"].parent) == {
        "files_written_before_the_answers": 0,
        "questions_put_on_a_second_run": 0,
        "commands_under_one_overwrite_rule": 4,
    }


# -- the twin command ----------------------------------------------------


def test_nothing_is_written_before_the_questions_are_answered(ran: "dict[str, typing.Any]") -> None:
    """A twin stopped at its first question leaves the table's folder as it found it: no file, no folder."""
    stopped, screen = ran["A"]
    assert ran["after_A"] == ["t.csv"]
    assert stopped.verdict == results.REFUSED and results.exit_code(stopped) == 1
    assert stopped.refusal is not None and stopped.refusal.step == results.STEP_QUESTIONS
    assert [step.command for step in stopped.steps] == [results.PROFILE]
    assert stopped.files == ()
    # The question was on the screen before the run stopped; its next
    # command runs it again, to answer it.
    assert "COLUMN(S) CAN BE READ MORE THAN ONE WAY" in _text(screen)
    assert stopped.next_command == results.NextCommand(
        ("synthtwin", "twin", "t.csv"), results.PURPOSE_TWIN
    )


def test_the_questions_come_before_any_file_on_the_screen(ran: "dict[str, typing.Any]") -> None:
    """The one question is put, and answered, before the screen announces a file."""
    made, screen = ran["B"]
    text = _text(screen)
    asked = text.index("COLUMN(S) CAN BE READ MORE THAN ONE WAY")
    announced = text.index("These three files will be written")
    assert asked < announced
    assert dict(made.steps[0].tally)["questions-put"] == 1


def test_one_run_writes_the_six_files_into_one_folder(ran: "dict[str, typing.Any]") -> None:
    """B: profile, generate and validate in one run and one folder, each step's result its command's own."""
    made, _screen = ran["B"]
    folder = ran["folder"]
    assert [step.command for step in made.steps] == [results.PROFILE, results.GENERATE, results.VALIDATE]
    assert [one.kind for one in made.files] == [
        results.FILE_DESCRIPTION,
        results.FILE_SUMMARY,
        results.FILE_QUESTIONS,
        results.FILE_TWIN,
        results.FILE_TWIN_REPORT,
        results.FILE_QUALITY_REPORT,
    ]
    assert {pathlib.Path(one.path).parent for one in made.files} == {folder.resolve()}
    assert sorted(ran["after_B"]) == sorted(pathlib.Path(one.path).name for one in made.files)
    # The table's own folder holds the table and the twin's folder, and
    # no file of the run is beside the table.
    assert sorted(os.listdir(ran["home"])) == ["t-synthtwin", "t.csv"]


def test_the_verdict_and_the_exit_status_are_the_most_severe_step_s(ran: "dict[str, typing.Any]") -> None:
    """At the table floor the weight's commonest value is given up, so generate missed: the twin exits 3."""
    made, _screen = ran["B"]
    verdicts = [step.verdict for step in made.steps]
    assert verdicts == [results.NO_MISS, results.MISSED, results.NO_MISS]
    assert made.verdict == results.MISSED and results.exit_code(made) == 3
    assert made.misses == made.steps[1].misses and made.misses
    assert made.tally == made.steps[1].tally
    assert made.refusal is None
    assert made.warnings == made.steps[0].warnings + made.steps[1].warnings + made.steps[2].warnings
    assert made.questions == made.steps[0].questions


def test_a_question_still_open_after_the_screen_is_taught_its_command(ran: "dict[str, typing.Any]") -> None:
    """B: the record number answered on screen, the weight's Safe Harbor question is still open, so its command is taught.

    Lane TT's repair 2 (the orchestrator's LANE TT RULINGS 3 (1)): the
    answers line and its command (`answer-questions`) are taught wherever
    a question is still open, whoever was at the keyboard; on cd7b7851 a
    run with somebody at the keyboard taught none, so a person who
    pressed Enter was never told how to answer what Enter left open. The
    one question open here is answered in the questions file alone, so
    the line sends the person to that file, then to the command.
    """
    made, screen = ran["B"]
    folder = pathlib.Path(made.files[0].path).parent
    still_open = [
        one.column
        for one in made.questions
        if one.section in (results.SECTION_ABOUT_FILE, results.SECTION_ASKED)
    ]
    assert still_open == ["weight"]
    assert made.next_command == results.NextCommand(
        (
            "synthtwin", "twin", "t.csv", "--out-dir", f"{folder}",
            "--answers", f"{folder / 't-questions.json'}", "--replace",
        ),
        results.PURPOSE_ANSWER_QUESTIONS,
    )
    shown = _text(screen)
    assert "\n1 question(s) are still open, so each of their columns kept the reading" in shown
    assert "They are answered in" in shown and "Nobody was at the keyboard" not in shown


def test_a_second_run_asks_nothing_and_writes_the_same_six_files(ran: "dict[str, typing.Any]") -> None:
    """D: the folder's questions file is handed back, nobody is asked, and the six files come back byte for byte."""
    again, screen = ran["D"]
    assert again.verdict == results.MISSED
    assert dict(again.steps[0].tally)["questions-put"] == 0
    assert "COLUMN(S) CAN BE READ MORE THAN ONE WAY" not in _text(screen)
    assert ran["after_D"] == ran["after_B"]
    assert len(ran["after_D"]) == 6


def test_a_second_run_without_replace_is_refused_by_the_one_rule(ran: "dict[str, typing.Any]") -> None:
    """C: the six names are taken, so the run stops before it reads the table, asking and writing nothing."""
    twice, screen = ran["C"]
    assert _refused_by_the_rule(twice, ran["after_C"] == ran["after_B"], errors.MAKING_AGAIN)
    assert twice.steps == ()
    assert twice.refusal is not None and "This run writes six files" in twice.refusal.words
    assert "COLUMN(S)" not in _text(screen)


def test_each_command_keeps_the_one_overwrite_rule(ran: "dict[str, typing.Any]") -> None:
    """Profile, generate and validate refuse a taken name in the one template's words, and replace it with --replace."""
    for command, usual in (
        ("profile", errors.DESCRIBING_AGAIN),
        ("generate", errors.BUILDING_AGAIN),
        ("validate", errors.CHECKING_AGAIN),
    ):
        refused, _screen = ran[f"{command}_refused"]
        assert _refused_by_the_rule(refused, ran[f"{command}_unchanged"], usual), command
    assert rule_measures(ran["home"].parent)["commands_under_one_overwrite_rule"] == 4


def test_generate_and_validate_keep_their_words() -> None:
    """The one template writes generate's and validate's refusals as they always read (the battery's R3 and R4)."""
    assert errors.outputs_already_there("a", "b", ["a"]) == (
        "synthtwin stopped because something is already at one of the names it "
        "would write. This run writes two files, a and b, and this one is "
        "already there: a. Nothing was written and nothing was changed. If that "
        "file can be replaced -- the usual reason is building the twin again "
        "with a different seed -- add --replace to the command. If not, move or "
        "rename what is there, or give --out-dir a different folder to write "
        "into, then run the command again."
    )
    assert errors.quality_target_already_there("q") == (
        "synthtwin stopped because something is already at the name it would "
        "write. This run writes one file, q, and it is already there. Nothing "
        "was written and nothing was changed. If that file can be replaced -- "
        "the usual reason is checking the same twin again -- add --replace to "
        "the command. If not, move or rename what is there, or give --out-dir a "
        "different folder to write into, then run the command again."
    )


def test_profile_s_answers_round_and_replace_keep_working(tmp_path: pathlib.Path) -> None:
    """`profile --replace` writes over, as it always did; so does the answers round (the battery's G7), without it.

    The library's small-table path (a test device: the shipped command
    refuses this table, plan P4-D425), for the rule's bytes alone.
    """
    (tmp_path / "t.csv").write_text(battery.step0_table(600), encoding="utf-8", newline="\n")

    def profiled(*argv: str) -> results.Result:
        here = os.getcwd()
        os.chdir(tmp_path)
        try:
            return cli.run(list(argv), small_tables_refused=False)
        finally:
            os.chdir(here)

    assert profiled("profile", "t.csv").verdict == results.NO_MISS
    before = _digests(tmp_path)
    refused = profiled("profile", "t.csv")
    assert _refused_by_the_rule(refused, _digests(tmp_path) == before, errors.DESCRIBING_AGAIN)
    assert "This run writes three files" in (refused.refusal.words if refused.refusal else "")
    assert profiled("profile", "t.csv", "--replace").verdict == results.NO_MISS
    assert profiled("profile", "t.csv", "--answers", "t-questions.json").verdict == results.NO_MISS


def test_a_questions_file_name_on_the_table_keeps_its_caution(tmp_path: pathlib.Path) -> None:
    """A link at the questions file's name, pointing at the table, is no file of the run (the battery's L1)."""
    if os.name == "nt":
        pytest.skip("Windows refuses a link at the path gate before anything is written")
    (tmp_path / "t.csv").write_text(battery.step0_table(600), encoding="utf-8", newline="\n")
    os.symlink("t.csv", tmp_path / "t-questions.json")
    written, taken = cli._profile_outputs_taken(f"{tmp_path / 't.csv'}", None)
    assert len(written) == 2 and taken == []


# -- the twin never harms the person's files nor reaches off the machine --


def test_no_name_of_the_twin_s_folder_may_lead_onto_the_table(tmp_path: pathlib.Path) -> None:
    """Codex's item 1 (LANE TT RULINGS 1 item 1): a link at any of the six names, pointing at the table, is refused before any step.

    With `data-synthtwin/data-twin.csv` a link to `../data.csv`, `twin
    data.csv --replace` let generate write the twin over the real table on
    c4925cd8: each step guards only the file it was handed. Now each of
    the six names is asked before any step runs, the table is untouched
    and nothing is read or written; the description's and the summary's
    refusal is the profile step's own words.
    """
    if os.name == "nt":
        pytest.skip("Windows refuses a link at the path gate before anything is written")
    (tmp_path / "data.csv").write_text(battery.step0_table(ROWS), encoding="utf-8", newline="\n")
    table = (tmp_path / "data.csv").read_bytes()
    folder = tmp_path / "data-synthtwin"
    folder.mkdir()
    own = errors.output_would_replace_the_table(f"{(tmp_path / 'data.csv').resolve()}")
    for name in (
        "data-twin.csv",
        "data-twin-report.txt",
        "data-twin-quality.txt",
        "data-questions.json",
        "data-profile.json",
        "data-profile.txt",
    ):
        os.symlink("../data.csv", folder / name)
        refused, screen = _run(["twin", "data.csv", "--replace"], tmp_path)
        assert refused.verdict == results.REFUSED and results.exit_code(refused) == 1, name
        assert refused.refusal is not None and refused.refusal.step == results.STEP_OUTPUTS, name
        assert "would have replaced your own table" in refused.refusal.words, name
        if name.startswith("data-profile."):
            assert refused.refusal.words == own, name
        assert refused.steps == () and "COLUMN(S)" not in _text(screen), name
        assert (tmp_path / "data.csv").read_bytes() == table, name
        assert sorted(os.listdir(folder)) == [name], name
        os.unlink(folder / name)


def test_the_table_s_path_passes_the_locality_gate_before_anything_touches_it(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Codex's item 2 (LANE TT RULINGS 1 item 2): a network path is refused by its words before any call of the filesystem involves it.

    `twin \\\\server\\share\\data.csv --out-dir FOLDER` reached the alias
    check on c4925cd8, which resolved the raw path before its UNC check
    ran. No network share exists here, so the path is a string and every
    call that asks the filesystem about a path is recorded.
    """
    called: "list[str]" = []

    def recorded(real: "typing.Callable[..., typing.Any]") -> "typing.Callable[..., typing.Any]":
        def call(self_or_path: object, *rest: object, **named: object) -> object:
            called.append(f"{self_or_path}")
            return real(self_or_path, *rest, **named)

        return call

    for name in ("resolve", "stat", "lstat", "exists", "is_dir", "is_file", "is_symlink"):
        monkeypatch.setattr(pathlib.Path, name, recorded(getattr(pathlib.Path, name)))
    monkeypatch.setattr(os, "lstat", recorded(os.lstat))
    monkeypatch.setattr(os, "stat", recorded(os.stat))
    shared = "\\\\server\\share\\data.csv"
    refused, _screen = _run(["twin", shared, "--out-dir", f"{tmp_path}"], tmp_path, ask=[])
    assert refused.verdict == results.REFUSED and results.exit_code(refused) == 1
    assert refused.refusal is not None and refused.refusal.step == results.STEP_INPUT
    assert "network" in refused.refusal.words
    assert not [one for one in called if "server" in one]
    assert sorted(os.listdir(tmp_path)) == []


def test_the_twin_takes_the_table_s_floor_and_its_unusable_lines(tmp_path: pathlib.Path) -> None:
    """A table under the floor is refused before any question; a bad seed or no table before anything is read."""
    (tmp_path / "tiny.csv").write_text(battery.step0_table(battery.TINY_ROWS), encoding="utf-8", newline="\n")
    tiny, screen = _run(["twin", "tiny.csv"], tmp_path, ask=[])
    assert tiny.verdict == results.REFUSED and tiny.refusal is not None
    assert tiny.refusal.step == results.STEP_CONTENT
    assert "COLUMN(S)" not in _text(screen)
    assert sorted(os.listdir(tmp_path)) == ["tiny.csv"]
    seed, _seed_screen = _run(["twin", "tiny.csv", "--seed", "-1"], tmp_path)
    assert seed.verdict == results.UNUSABLE and results.exit_code(seed) == 2
    none, _none_screen = _run(["twin"], tmp_path)
    assert none.verdict == results.UNUSABLE and none.command == results.TWIN
    nowhere, _nowhere_screen = _run(["twin", "tiny.csv", "--out-dir", "nowhere"], tmp_path)
    assert nowhere.verdict == results.REFUSED and nowhere.refusal is not None
    assert nowhere.refusal.step == results.STEP_OUTPUTS
    assert sorted(os.listdir(tmp_path)) == ["tiny.csv"]


# -- the commands the twin teaches mean what the first run meant -----------


def _library(
    argv: "typing.Sequence[str]",
    folder: pathlib.Path,
    ask: "list[str | None] | None" = None,
) -> "tuple[results.Result, list[tuple[str, str]]]":
    """One command line through `cli.run` in ``folder`` on the library's small-table path.

    A test device (plan P4-D425; LANE I4m RULINGS 18 (4)): the shipped
    command refuses a table this small, so what these cases pin is the
    command line's meaning, which no table size changes.
    """
    here = os.getcwd()
    os.chdir(folder)
    try:
        screen: "list[tuple[str, str]]" = []
        result = cli.run(list(argv), screen=screen, ask=ask, small_tables_refused=False)
    finally:
        os.chdir(here)
    return result, screen


def _two_sheet_book(n_rows: int, notes_first: bool = True) -> bytes:
    """A workbook of two visible sheets, a page of notes first and the table on the second (Codex's item 5; invented, seeded).

    `record_no` is `REC` and six figures, one a row, so its question stays
    open with nobody at the keyboard; `arm` is `red`, `blue` or `VOID`;
    `weight` is a number. Read without `--sheet`, the notes are read (a
    sheet beside it holding a second table is refused by the reader
    whichever sheet is named, so the first one holds one note). Without
    ``notes_first``, the table's sheet alone.
    """
    import workbooks

    def body(seed: int) -> "list[tuple[int, list[str]]]":
        stream = random.Random(seed)
        rows = [
            (
                1,
                [
                    workbooks.cell("A1", "record_no", "inlineStr"),
                    workbooks.cell("B1", "arm", "inlineStr"),
                    workbooks.cell("C1", "weight", "inlineStr"),
                ],
            )
        ]
        for place in range(n_rows):
            number = place + 2
            arm = ("red", "blue", "VOID")[int(stream.random() * 3)]
            rows += [
                (
                    number,
                    [
                        workbooks.cell(f"A{number}", f"REC{100000 * seed + place}", "inlineStr"),
                        workbooks.cell(f"B{number}", arm, "inlineStr"),
                        workbooks.cell(f"C{number}", f"{50 + 40 * stream.random():.1f}"),
                    ],
                )
            ]
        return rows

    last = f"C{n_rows + 1}"
    table = workbooks.sheet(body(2), dimension=f"A1:{last}")
    if not notes_first:
        return workbooks.package(
            [
                ("[Content_Types].xml", workbooks._content_types(1, False, False, False)),
                ("_rels/.rels", workbooks._root_rels()),
                ("xl/workbook.xml", workbooks._workbook([("Study", "")])),
                ("xl/_rels/workbook.xml.rels", workbooks._workbook_rels(1, False)),
                ("xl/styles.xml", workbooks._styles()),
                ("xl/worksheets/sheet1.xml", table),
            ]
        )
    return workbooks.package(
        [
            ("[Content_Types].xml", workbooks._content_types(2, False, False, False)),
            ("_rels/.rels", workbooks._root_rels()),
            ("xl/workbook.xml", workbooks._workbook([("Notes", ""), ("Study", "")])),
            ("xl/_rels/workbook.xml.rels", workbooks._workbook_rels(2, False)),
            ("xl/styles.xml", workbooks._styles()),
            (
                "xl/worksheets/sheet1.xml",
                workbooks.sheet([(1, [workbooks.cell("A1", "notes", "inlineStr")])], dimension="A1:A1"),
            ),
            ("xl/worksheets/sheet2.xml", table),
        ]
    )


_WHOLE_LINE = [
    "twin", "w.xlsx", "--sheet", "Study", "--missing-value", "VOID",
    "--smallest-group", "12", "--seed", "3",
]


def test_the_answers_command_means_what_the_first_run_meant(tmp_path: pathlib.Path) -> None:
    """Codex's item 5 (LANE TT RULINGS 1 item 5): the taught answers command, run, writes the first run's six files byte for byte.

    A workbook run with `--sheet Study`, `--missing-value VOID`, a floor
    of 12 and seed 3, nobody at the keyboard: on c4925cd8 the taught
    command dropped all four, read the first sheet and replaced the
    Study outputs. Now it carries the whole command line, and running it
    (nobody at the keyboard again) gives back the same six files.
    """
    (tmp_path / "w.xlsx").write_bytes(_two_sheet_book(600))
    first, _screen = _library(_WHOLE_LINE, tmp_path)
    folder = tmp_path / "w-synthtwin"
    assert first.verdict in (results.NO_MISS, results.MISSED), first.refusal
    made = _digests(folder)
    assert len(made) == 6
    assert first.next_command is not None
    assert first.next_command.purpose == results.PURPOSE_ANSWER_QUESTIONS
    words = list(first.next_command.words)
    assert words[:3] == ["synthtwin", "twin", "w.xlsx"]
    for pair in (["--sheet", "Study"], ["--missing-value", "VOID"], ["--smallest-group", "12"], ["--seed", "3"]):
        assert any(words[place : place + 2] == pair for place in range(len(words) - 1)), pair
    again, _again_screen = _library(words[1:], tmp_path)
    assert again.verdict == first.verdict
    assert _digests(folder) == made


def test_the_answers_command_stopped_at_a_question_teaches_itself(tmp_path: pathlib.Path) -> None:
    """Skeptic 1's item 3 (LANE TT RULINGS 2 (3)): stopped at its first question, the answers command teaches itself, word for word.

    On c4925cd8 it taught `synthtwin twin TABLE --out-dir FOLDER`, which
    the overwrite rule refused, and with `--replace` added asked nothing;
    the first run's options were gone too. A bare `synthtwin twin t.csv`
    still teaches `synthtwin twin t.csv` (journey A, the battery's T6).
    """
    (tmp_path / "w.xlsx").write_bytes(_two_sheet_book(600))
    first, _screen = _library(_WHOLE_LINE, tmp_path)
    assert first.next_command is not None
    words = tuple(first.next_command.words)
    made = _digests(tmp_path / "w-synthtwin")
    stopped, screen = _library(list(words[1:]), tmp_path, ask=[])
    assert stopped.verdict == results.REFUSED and stopped.refusal is not None
    assert stopped.refusal.step == results.STEP_QUESTIONS
    assert stopped.next_command == results.NextCommand(words, results.PURPOSE_TWIN)
    assert _digests(tmp_path / "w-synthtwin") == made
    shown = _text(screen)
    assert "--sheet Study" in shown and "--answers" in shown and "--replace" in shown


# -- the help pages --------------------------------------------------------


def test_each_command_has_one_page_of_at_most_60_lines() -> None:
    """`K-S8-05`: five pages, each its command's own, at most 60 lines; and the examples page."""
    measured = help_measures()
    assert measured["command_pages"] == 5
    assert measured["longest_command_page_lines"] <= 60
    assert measured["examples_page_lines"] > 0


def test_each_page_names_the_options_its_command_reads_and_the_parser_takes() -> None:
    """Every option a page names is one the parser reads (`_LONG_OPTIONS`), and every option its command reads is on it."""
    for command, options in cli._READ_BY.items():
        page = cli.command_page(command)
        named = set(re.findall(r"--[a-z][a-z-]*", page))
        assert named <= set(cli._LONG_OPTIONS), (command, named - set(cli._LONG_OPTIONS))
        for option in options:
            assert option in named, (command, option)
        # ...and the command line it names parses with every one of them.
        for option in options:
            metavar, _said = cli._SHORT_HELP[option]
            words = [command, "x.csv", option]
            if option == "--date-count":
                words += ["a", "excel-1900"]
            elif option == "--first-row":
                words += ["names"]
            elif option == "--smallest-group":
                words += ["11"]
            elif metavar:
                words += ["v"]
            assert cli._parse_arguments(words, None).command == command, words


def test_the_disclosure_of_a_declared_value_is_printed_whole_where_it_is_read() -> None:
    """--keep-value and --missing-value carry their whole help on profile's and twin's pages (amendment A-P3-31)."""
    for command in ("profile", "twin"):
        flat = " ".join(cli.command_page(command).split())
        assert " ".join(cli._MISSING_VALUE_HELP.split()) in flat
        assert " ".join(cli._KEEP_VALUE_HELP.split()) in flat


def test_the_whole_tool_page_is_the_one_the_base_printed() -> None:
    """`synthtwin --help` and `--help COMMAND` keep the whole-tool page; the new words are not added to it (G10.2)."""
    screen: "list[tuple[str, str]]" = []
    cli.run(["--help"], screen=screen)
    page = _text(screen)
    assert "{profile,generate,validate,doctor}" in page
    assert "doctor,twin" not in page and "synthtwin help" not in page
    other: "list[tuple[str, str]]" = []
    cli.run(["--help", "profile"], screen=other)
    assert _text(other) == page


def test_every_example_parses_and_help_refuses_a_page_it_lacks(tmp_path: pathlib.Path) -> None:
    """Each line of the examples page and the index is a command line the parser reads; an unknown topic exits 2."""
    for page in (cli._EXAMPLES_PAGE, cli._HELP_INDEX):
        for line in page.splitlines():
            words = line.split()
            if line.startswith("  synthtwin ") and "--help" not in words:
                options = cli._parse_arguments(words[1:], None)
                assert options.command in ("profile", "generate", "validate", "doctor", "twin", "help"), line
    refused = cli.run(["help", "nothing-here"], screen=[])
    assert refused.verdict == results.UNUSABLE and results.exit_code(refused) == 2
    assert parsing.visible_lines("x") == "x"


# -- the answers a folder keeps are handed back only as they were given ---


def _coded_table(n_rows: int, seed: int) -> str:
    """A record number, an arm written `red`, `blue` or `VOID`, and a weight (invented, seeded; Codex's items 3 and 4).

    The record number is `REC` and six figures, one a row, so its question
    is the one the prompt puts; tables of other seeds are other tables of
    the same column names.
    """
    stream = random.Random(seed)
    rows = ["record_no,arm,weight"]
    for index in range(n_rows):
        draw = stream.random()
        arm = "VOID" if draw < 0.2 else ("red" if draw < 0.6 else "blue")
        rows += [f"REC{100000 * seed + index},{arm},{50 + 40 * stream.random():.1f}"]
    return "\n".join(rows) + "\n"


def test_a_folder_s_answers_are_not_handed_back_under_other_reading_options(tmp_path: pathlib.Path) -> None:
    """Codex's item 3 (LANE TT RULINGS 1 item 3): a second run that gives a reading option otherwise is refused, naming it.

    First `--first-row names --code arm --missing-value VOID`, then `twin
    data.csv --replace`: on c4925cd8 the folder's questions file was
    handed back without the declaration it does not carry, and `arm` was
    read with `VOID` as a value. Now the file binds its answers to the
    options it does not carry (the floor and how many times
    `--missing-value` and `--keep-value` were given), and a run giving one
    otherwise stops before reading, naming it; the same options again
    are handed the answers, ask nothing and write the same six files.
    """
    (tmp_path / "data.csv").write_text(_coded_table(600, 3), encoding="utf-8", newline="\n")
    typed = ["twin", "data.csv", "--first-row", "names", "--code", "arm", "--missing-value", "VOID"]
    first, _screen = _library(typed, tmp_path)
    folder = tmp_path / "data-synthtwin"
    assert first.verdict in (results.NO_MISS, results.MISSED), first.refusal
    made = _digests(folder)
    for again, option in (
        (["twin", "data.csv", "--replace"], "--missing-value"),
        (typed + ["--replace", "--smallest-group", "12"], "--smallest-group"),
        (typed + ["--replace", "--keep-value", "NA"], "--keep-value"),
    ):
        refused, screen = _library(again, tmp_path)
        assert refused.verdict == results.REFUSED and results.exit_code(refused) == 1, option
        assert refused.refusal is not None and refused.refusal.step == results.STEP_INPUT, option
        assert f"read with {option}" in refused.refusal.words, option
        assert refused.steps == () and "COLUMN(S)" not in _text(screen), option
        assert _digests(folder) == made, option
    same, _same_screen = _library(typed + ["--replace"], tmp_path)
    assert same.verdict == first.verdict
    assert dict(same.steps[0].tally)["questions-put"] == 0
    assert _digests(folder) == made


def test_a_folder_s_answers_are_handed_back_only_to_the_file_they_were_given_about(tmp_path: pathlib.Path) -> None:
    """Codex's item 4 (LANE TT RULINGS 1 item 4): answers kept about one table are never handed to another of the same name.

    `twin cohortA/data.csv --out-dir reports`, the record number answered
    `identifier` at the prompt; then `twin cohortB/data.csv --out-dir
    reports --replace`, the same column names over other rows: on
    c4925cd8 A's answer decided B's reading. Now the questions file binds
    its answers to the file's size and fingerprint, read in the profile
    step's own one reading, and B is refused before anything is written;
    A again is handed them, asked nothing, its six files the same. A
    questions file that binds its answers to no file (`profile` wrote it)
    is not handed back by itself.
    """
    for cohort, seed in (("cohortA", 4), ("cohortB", 5)):
        (tmp_path / cohort).mkdir()
        (tmp_path / cohort / "data.csv").write_text(_coded_table(600, seed), encoding="utf-8", newline="\n")
    (tmp_path / "reports").mkdir()
    first, _screen = _library(["twin", "cohortA/data.csv", "--out-dir", "reports"], tmp_path, ask=["3"])
    assert first.verdict in (results.NO_MISS, results.MISSED), first.refusal
    made = _digests(tmp_path / "reports")
    other, screen = _library(["twin", "cohortB/data.csv", "--out-dir", "reports", "--replace"], tmp_path, ask=[])
    assert other.verdict == results.REFUSED and results.exit_code(other) == 1
    assert other.refusal is not None and other.refusal.step == results.STEP_INPUT
    assert "were given about another file" in other.refusal.words and "--replace" in other.refusal.words
    assert [step.command for step in other.steps] == [results.PROFILE]
    assert other.files == () and "COLUMN(S)" not in _text(screen)
    assert _digests(tmp_path / "reports") == made
    again, _again_screen = _library(["twin", "cohortA/data.csv", "--out-dir", "reports", "--replace"], tmp_path, ask=[])
    assert again.verdict == first.verdict
    assert dict(again.steps[0].tally)["questions-put"] == 0
    assert _digests(tmp_path / "reports") == made
    (tmp_path / "apart").mkdir()
    profiled, _profiled_screen = _library(["profile", "cohortA/data.csv", "--out-dir", "apart"], tmp_path)
    assert profiled.verdict in (results.NO_MISS, results.MISSED)
    unbound, _unbound_screen = _library(["twin", "cohortA/data.csv", "--out-dir", "apart", "--replace"], tmp_path)
    assert unbound.verdict == results.REFUSED and unbound.refusal is not None
    assert "does not say which file" in unbound.refusal.words and unbound.steps == ()


# -- the preflight refuses before the table is read, and the ending counts --


def test_a_workbook_named_as_text_is_named_by_its_content_before_anything_is_read(tmp_path: pathlib.Path) -> None:
    """Codex's item 6 (LANE TT RULINGS 1 item 6): the preflight names a workbook's twin by the reader's own test of its bytes.

    A workbook named `data.csv`, with only `data-twin.xlsx` already in its
    folder: on c4925cd8 the preflight looked for `data-twin.csv`, then the
    profile step read the table and wrote three files before generate
    found the workbook twin's name taken. Now the one overwrite rule
    refuses before anything is read or written.
    """
    (tmp_path / "data.csv").write_bytes(_two_sheet_book(600, notes_first=False))
    folder = tmp_path / "data-synthtwin"
    folder.mkdir()
    (folder / "data-twin.xlsx").write_bytes(b"an earlier twin")
    refused, screen = _library(["twin", "data.csv"], tmp_path, ask=[])
    assert refused.verdict == results.REFUSED and refused.refusal is not None
    assert refused.refusal.step == results.STEP_OUTPUTS
    assert "data-twin.xlsx" in refused.refusal.words and refused.steps == ()
    assert "COLUMN(S)" not in _text(screen)
    assert sorted(os.listdir(folder)) == ["data-twin.xlsx"]


def test_a_folder_at_a_profile_name_is_refused_before_the_table_is_read(tmp_path: pathlib.Path) -> None:
    """Codex's item 7 (LANE TT RULINGS 1 item 7): a folder standing at `data-profile.json` keeps profile's early refusal.

    On c4925cd8 the name check turned the folder's refusal into "nothing
    taken", so `profile data.csv` read the table and put its question
    first. Now it refuses at once, in the words it always used; and a
    twin refuses a folder at any of its six names before any step.
    """
    (tmp_path / "data.csv").write_text(_coded_table(600, 6), encoding="utf-8", newline="\n")
    (tmp_path / "data-profile.json").mkdir()
    refused, screen = _library(["profile", "data.csv"], tmp_path, ask=[])
    assert refused.verdict == results.REFUSED and refused.refusal is not None
    assert refused.refusal.step == results.STEP_OUTPUTS
    assert "COLUMN(S)" not in _text(screen)
    assert sorted(os.listdir(tmp_path)) == ["data-profile.json", "data.csv"]
    folder = tmp_path / "data-synthtwin"
    folder.mkdir()
    (folder / "data-twin-quality.txt").mkdir()
    twin, twin_screen = _library(["twin", "data.csv", "--replace"], tmp_path, ask=[])
    assert twin.verdict == results.REFUSED and twin.refusal is not None
    assert twin.refusal.step == results.STEP_OUTPUTS and twin.steps == ()
    assert "COLUMN(S)" not in _text(twin_screen)


def test_a_twin_folder_that_cannot_be_made_is_refused_in_words(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 8 (LANE TT RULINGS 1 item 8): a default folder that cannot be made names a writable --out-dir, never a stack trace.

    On c4925cd8 a table in a folder that takes no new folder was profiled,
    and `mkdir` raised. Where the folder's own mode says so, the run
    refuses before the table is read; where it cannot be foreseen, the
    refusal comes when the folder is made, before any file is written.
    """
    if os.name != "nt":
        locked = tmp_path / "locked"
        locked.mkdir()
        (locked / "t.csv").write_text(battery.step0_table(ROWS), encoding="utf-8", newline="\n")
        locked.chmod(0o555)
        try:
            refused, screen = _run(["twin", "t.csv"], locked)
        finally:
            locked.chmod(0o755)
        assert refused.verdict == results.REFUSED and refused.refusal is not None
        assert refused.refusal.step == results.STEP_OUTPUTS and refused.steps == ()
        assert "Give --out-dir a folder you can save files in" in refused.refusal.words
        assert refused.refusal.words == errors.twin_folder_not_made(f"{locked.resolve() / 't-synthtwin'}")
        assert sorted(os.listdir(locked)) == ["t.csv"]
    (tmp_path / "t.csv").write_text(battery.step0_table(600), encoding="utf-8", newline="\n")
    real_mkdir = pathlib.Path.mkdir

    def refused_mkdir(self: pathlib.Path, *rest: object, **named: object) -> None:
        if self.name == "t-synthtwin":
            raise PermissionError("not allowed here")
        real_mkdir(self, *rest, **named)  # type: ignore[arg-type]

    monkeypatch.setattr(pathlib.Path, "mkdir", refused_mkdir)
    stopped, _screen = _library(["twin", "t.csv"], tmp_path)
    assert stopped.verdict == results.REFUSED and results.exit_code(stopped) == 1
    assert stopped.refusal is not None and stopped.refusal.step == results.STEP_OUTPUTS
    assert "Give --out-dir a folder you can save files in" in stopped.refusal.words
    assert "t-synthtwin" not in os.listdir(tmp_path) and stopped.files == ()


def test_the_ending_counts_the_files_the_steps_wrote(tmp_path: pathlib.Path) -> None:
    """Codex's item 10 (LANE TT RULINGS 1 item 10): the ending's count of files is the steps' own record.

    A questions file name that leads onto the description is no file of
    the profile step (a caution, the battery's L1 in the description's
    case), so the twin writes five files, and its last lines said six on
    c4925cd8.
    """
    if os.name == "nt":
        pytest.skip("Windows refuses a link at the path gate before anything is written")
    (tmp_path / "t.csv").write_text(_coded_table(600, 7), encoding="utf-8", newline="\n")
    first, _screen = _library(["twin", "t.csv"], tmp_path)
    assert first.verdict in (results.NO_MISS, results.MISSED)
    folder = tmp_path / "t-synthtwin"
    shutil.copy(folder / "t-questions.json", tmp_path / "kept.json")
    os.unlink(folder / "t-questions.json")
    os.symlink("t-profile.json", folder / "t-questions.json")
    five, screen = _library(["twin", "t.csv", "--replace", "--answers", "kept.json"], tmp_path)
    assert five.verdict in (results.NO_MISS, results.MISSED), five.refusal
    assert len(five.files) == 5
    assert "\nThe twin's five files are in:\n" in _text(screen)


def test_an_unknown_command_word_is_refused_in_the_base_s_words() -> None:
    """Skeptic 1's item 4 (LANE TT RULINGS 2 (4)): `bogus`, `profil` and `Profile` are refused byte for byte as the base refused them (G1).

    The base's argument was named `command` and listed four words; the
    metavar the lane added renamed it in this message and listed the two
    new words. The reference parser below is the base's argument, so the
    words are argparse's own on every version.
    """
    import argparse

    reference = argparse.ArgumentParser(prog="synthtwin", exit_on_error=False, add_help=False)
    reference.add_argument(
        "command", nargs="?", default=None, choices=["profile", "generate", "validate", "doctor"]
    )
    for argv in (["bogus"], ["profil", "x.csv"], ["Profile", "x.csv"]):
        screen: "list[tuple[str, str]]" = []
        refused = cli.run(argv, screen=screen)
        assert refused.verdict == results.UNUSABLE and results.exit_code(refused) == 2, argv
        try:
            reference.parse_args(argv[:1])
        except argparse.ArgumentError as error:
            expected = f"synthtwin: error: {error}"
        else:
            raise AssertionError(argv)
        text = _text(screen)
        assert text.splitlines()[-1] == expected, argv
        assert "[{profile,generate,validate,doctor}] [path]" in text, argv
    assert cli._parse_arguments(["twin", "t.csv"], None).command == "twin"
    assert cli._parse_arguments(["help", "twin"], None).command == "help"

"""Lane TT's gate, its held table: what a twin with nobody at the keyboard, and one whose person presses Enter at every question, publish (plan P4-D460).

The second file of the gate (`tests/test_terminal_twin.py` holds the
journey on Step 0's table, the measures, the help pages and the cases on
the library's small-table path): the orchestrator's LANE TT RULINGS 2
(7)(b) and LANE I4m RULINGS 21 (9) judge a gate file by its CPU seconds,
at most 180 a file. Here, on the held table at the table floor of 20,000
rows (`test_terminal_twin.held_table`: a column for each kind of question
the prompt puts, beside a ZIP code, a birth date and a top-coded weight),
through the shipped command: E, a twin with nobody at the keyboard;
E_enter, the same with Enter pressed at every question. HIPAA FIRST:
Enter never releases more than nobody does (the orchestrator's LANE TT
RULINGS 2 (1)). Measured by `tools/measurements/kpi_terminal.py` under
`kpi_run.py --slow` alone, as `K-S8-03`'s keys (`test_terminal_twin.
apart_measures`): the twin's files and screen against the three commands
run apart, and E_enter's folder again with `--replace` and nobody asked,
which must ask nothing and write the same six files (LANE TT RULINGS 2
(2); the gate's own case of it is Step 0's table, in the journey).
"""

from __future__ import annotations

import json
import pathlib
import re
import typing

import pytest

import test_terminal_twin as twin
from synthtwin import cli, results
from test_terminal_twin import (
    _DATE,
    _FIVE,
    _FOLIO,
    _PATIENT,
    _RECORD,
    _STAMP,
    _ZIP,
    _text,
)


@pytest.fixture(scope="module")
def held_ran(tmp_path_factory: pytest.TempPathFactory) -> "dict[str, typing.Any]":
    return twin.held(tmp_path_factory.mktemp("held"))


@pytest.fixture(scope="module")
def entered_ran(held_ran: "dict[str, typing.Any]") -> "dict[str, typing.Any]":
    return twin.entered(held_ran["held_home"].parent)


# -- nobody at the keyboard --------------------------------------------------


def test_no_record_number_zip_or_birth_date_reaches_the_screen_or_the_saved_answers(
    held_ran: "dict[str, typing.Any]",
) -> None:
    """HIPAA FIRST, at 20,000 rows, nobody at the keyboard: the held columns show nothing real.

    The record numbers (held while their question is open), the ZIP
    codes (held while the Safe Harbor question is open) and the birth
    dates (held whole) of the held table appear nowhere on the twin's
    screen and nowhere in its questions file, where the answers stay;
    and no published fact or twin cell of the weight, which that
    question top-codes, passes 90.
    """
    twin, screen = held_ran["E"]
    real = held_ran["E_real"].splitlines()[1:]
    records = {line.split(",")[0] for line in real}
    zips = {line.split(",")[1] for line in real}
    born = {line.split(",")[2] for line in real}
    assert [one.kind for one in twin.files].count(results.FILE_QUESTIONS) == 1
    for text in (_text(screen), held_ran["E_questions"]):
        assert not records & set(_RECORD.findall(text))
        assert not zips & set(_FIVE.findall(text))
        assert not born & set(_DATE.findall(text))
    weights = [line.split(",")[3] for line in held_ran["E_twin"].splitlines()[1:]]
    assert all(float(one) <= 90 for one in weights if one)


# -- Enter at every question: never more than nobody (LANE TT RULINGS 2 (1)) --


def _real_of(held_ran: "dict[str, typing.Any]", place: int) -> "set[str]":
    """The held table's real values of the column at ``place``, as written."""
    return {line.split(",")[place] for line in held_ran["E_real"].splitlines()[1:]}


def _twin_column(text: str, place: int) -> "list[str]":
    """One column of a twin's text, its cells as written."""
    return [line.split(",")[place] for line in text.splitlines()[1:]]


def _enter_texts(entered_ran: "dict[str, typing.Any]") -> "list[str]":
    """What a person who pressed Enter at every question saw and was given: the screen and the description."""
    _result, screen = entered_ran["E_enter"]
    return [_text(screen), entered_ran["E_enter_description"]]


def test_enter_at_every_question_writes_what_nobody_s_run_writes(
    held_ran: "dict[str, typing.Any]", entered_ran: "dict[str, typing.Any]"
) -> None:
    """The six files of a twin whose person pressed Enter at every question are nobody's six, byte for byte.

    Lane TT's repair (the orchestrator's LANE TT RULINGS 2 (1)): Enter
    leaves each question open, so the key a person presses when unsure
    never releases more than a run with nobody at the keyboard does -- for
    every kind of question the prompt puts here: record numbers of two
    kinds, the person question, ZIP codes and counts of seconds under the
    date-counting question, the unit question and the 12-hour question.
    Measured on lane TT's head c4925cd8, Enter released the record
    number, `folio` and `patient` (19,998 of 20,000 real record numbers in
    a twin of the skeptic's table). Red on the mutant Enter = keep.
    """
    pressed, _screen = entered_ran["E_enter"]
    assert [step.command for step in pressed.steps] == [results.PROFILE, results.GENERATE, results.VALIDATE]
    assert dict(pressed.steps[0].tally)["questions-put"] >= 6
    assert entered_ran["E_enter_files"] == held_ran["E_files"]


def test_enter_keeps_the_record_numbers_held(entered_ran: "dict[str, typing.Any]", held_ran: "dict[str, typing.Any]") -> None:
    """Record numbers of two kinds (one a row; eight figures, fixed width): 0 real in the twin, the description and the screen."""
    records, folio = _real_of(held_ran, 0), _real_of(held_ran, 5)
    for text in _enter_texts(entered_ran):
        assert not records & set(_RECORD.findall(text))
        assert not folio & set(_FOLIO.findall(text))
    assert not records & set(_twin_column(entered_ran["E_enter_twin"], 0))
    assert not folio & set(_twin_column(entered_ran["E_enter_twin"], 5))


def test_enter_keeps_the_person_question_s_column_held(
    entered_ran: "dict[str, typing.Any]", held_ran: "dict[str, typing.Any]"
) -> None:
    """The person question's column (`PT` and five figures, about twelve rows each): 0 real in the twin, the description and the screen."""
    patients = _real_of(held_ran, 6)
    figures = {one[2:] for one in patients}
    for text in _enter_texts(entered_ran):
        assert not patients & set(_PATIENT.findall(text))
        assert not figures & set(_ZIP.findall(text))
    assert not patients & set(_twin_column(entered_ran["E_enter_twin"], 6))


def test_enter_keeps_the_zip_codes_held(entered_ran: "dict[str, typing.Any]", held_ran: "dict[str, typing.Any]") -> None:
    """ZIP codes, put the date-counting question at the prompt: 0 real in the twin, the description and the screen.

    No answer the prompt can take releases them (only the Safe Harbor
    question's `no`, which is put in the questions file, or
    `--identifier`, which holds them); red on the mutant that skips the
    Safe Harbor holds once a person answered at the keyboard.
    """
    zips = _real_of(held_ran, 1)
    for text in _enter_texts(entered_ran):
        assert not zips & set(_ZIP.findall(text))
    assert not zips & set(_twin_column(entered_ran["E_enter_twin"], 1))


def test_enter_keeps_the_dates_held(entered_ran: "dict[str, typing.Any]", held_ran: "dict[str, typing.Any]") -> None:
    """Dates: counts of seconds put the date-counting question, and full birth dates: 0 real in the twin, the description and the screen."""
    born, stamps = _real_of(held_ran, 2), _real_of(held_ran, 7)
    for text in _enter_texts(entered_ran):
        assert not born & set(_DATE.findall(text))
        assert not stamps & set(_STAMP.findall(text))
    assert not born & set(_twin_column(entered_ran["E_enter_twin"], 2))
    assert not stamps & set(_twin_column(entered_ran["E_enter_twin"], 7))


def test_enter_keeps_the_top_code(entered_ran: "dict[str, typing.Any]") -> None:
    """Ages: the weight, which runs to 104 and which the Safe Harbor question top-codes, writes no twin cell above 90."""
    weights = _twin_column(entered_ran["E_enter_twin"], 3)
    assert weights and all(float(one) <= 90 for one in weights if one)


def test_enter_keeps_the_reading_of_codes_against_measurements(
    entered_ran: "dict[str, typing.Any]", held_ran: "dict[str, typing.Any]"
) -> None:
    """The unit question and the 12-hour question, which hold nothing: Enter keeps the reading nobody's run keeps, column by column."""
    pressed = {one["name"]: one for one in json.loads(entered_ran["E_enter_description"])["columns"]}
    nobody = {one["name"]: one for one in json.loads(held_ran["E_description"])["columns"]}
    for name in ("stature", "clock", "ward", "weight"):
        assert pressed[name] == nobody[name], name
    result, _screen = entered_ran["E_enter"]
    put = {one.column for one in result.steps[0].questions if one.put}
    assert {"stature", "clock"} <= put


def test_the_prompt_puts_no_safe_harbor_question(entered_ran: "dict[str, typing.Any]") -> None:
    """The Safe Harbor questions are answered in the questions file alone: the prompt puts none, so Enter answers none.

    Every question the prompt put is one of the column questions; each
    Safe Harbor question the file asks (the birth date and the weight's
    top-code among them) was put at no prompt.
    """
    from synthtwin import asking

    result, screen = entered_ran["E_enter"]
    records = result.steps[0].questions
    harbor = [
        one
        for one in records
        if one.reason in asking.SAFE_HARBOR_REASONS + asking.SH2_SAFE_HARBOR_REASONS
    ]
    assert {one.column for one in harbor} >= {"born", "weight"}
    assert not [one for one in harbor if one.put]
    shown = re.findall(r"\n  Column [0-9]+ of [0-9]+: '", _text(screen))
    assert dict(result.steps[0].tally)["questions-put"] == len(shown)


def test_nobody_at_the_keyboard_is_taught_the_command_that_asks(held_ran: "dict[str, typing.Any]") -> None:
    """E: the questions left open are named, and the next command puts them on screen (`answer-questions`)."""
    twin, _screen = held_ran["E"]
    folder = pathlib.Path(twin.files[0].path).parent
    assert twin.next_command is not None
    assert twin.next_command.purpose == results.PURPOSE_ANSWER_QUESTIONS
    assert twin.next_command.words == (
        "synthtwin",
        "twin",
        "h.csv",
        "--out-dir",
        f"{folder}",
        "--answers",
        f"{folder / 'h-questions.json'}",
        "--replace",
    )
    # ...and that command parses, as the person would type it.
    assert cli._parse_arguments(list(twin.next_command.words[1:]), None).command == "twin"


def test_enter_is_taught_the_command_nobody_s_run_is_taught(
    held_ran: "dict[str, typing.Any]", entered_ran: "dict[str, typing.Any]"
) -> None:
    """E_enter: a person who pressed Enter at every question is taught E's answers command, in E's words.

    Lane TT's repair 2 (the orchestrator's LANE TT RULINGS 3 (1), from the
    verify of repair 1, its finding 1): Enter leaves each question open,
    and on cd7b7851 such a run taught nothing (the verify's own table of
    20,000 rows: the next command none, 6 questions open), while the same
    table with nobody at the keyboard taught `answer-questions`. Here the
    next command is E's, word for word, and so is the line that teaches
    it, but for its opening: the questions are still open, rather than
    unanswered for want of anybody. Red on the mutant that teaches it
    only where nobody was at the keyboard.
    """
    twin, screen = held_ran["E"]
    pressed, pressed_screen = entered_ran["E_enter"]
    assert pressed.next_command is not None
    assert pressed.next_command.purpose == results.PURPOSE_ANSWER_QUESTIONS
    assert pressed.next_command == twin.next_command
    still_open = [
        one
        for one in pressed.questions
        if one.section in (results.SECTION_ABOUT_FILE, results.SECTION_ASKED)
    ]
    nobody = f"\nNobody was at the keyboard to answer {len(still_open)} question(s), "
    somebody = f"\n{len(still_open)} question(s) are still open, "
    shown = _text(screen)
    pressed_shown = _text(pressed_screen)
    assert nobody not in pressed_shown
    assert pressed_shown[pressed_shown.index(somebody) + len(somebody) :] == shown[
        shown.index(nobody) + len(nobody) :
    ]


def test_the_answers_line_counts_only_the_questions_the_screen_puts(
    held_ran: "dict[str, typing.Any]", entered_ran: "dict[str, typing.Any]"
) -> None:
    """Codex's item 9, skeptic 1's item 5 (LANE TT RULINGS 2 (5)): the answers line counts the questions the prompt puts, and names the rest.

    On c4925cd8 the line said 6 questions would be answered on screen
    where the command put 3: the Safe Harbor questions and those about
    the file are answered in the questions file alone. Here the count on
    screen is the count the prompt put when somebody pressed Enter at
    every question (E_enter), and the rest are named as the file's.
    """
    twin, screen = held_ran["E"]
    pressed, _pressed_screen = entered_ran["E_enter"]
    put = dict(pressed.steps[0].tally)["questions-put"]
    asked = [
        one
        for one in twin.steps[0].questions
        if one.section in (results.SECTION_ABOUT_FILE, results.SECTION_ASKED)
    ]
    shown = _text(screen)
    assert f"Nobody was at the keyboard to answer {len(asked)} question(s)" in shown
    assert f"{put} of them can be answered on screen" in shown
    assert 0 < put < len(asked)
    assert f"The other {len(asked) - put} are answered in" in shown

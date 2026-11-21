"""P4-D479 items 4, 5, 7, 15 and 16: every question at the keyboard, and the keyboard is the file (lane EZ-a).

THE USABILITY WALKTHROUGH'S ITEMS 4, 5, 7, 15 AND 16. The Safe Harbor
question, the checklist and the questions about the file were put only in
the questions file, answered by hand-editing a nested JSON file; a curly
quotation mark a text editor put there was reported as a broken
DESCRIPTION, with the advice to make it again; nothing was printed for
the first minutes of a long run; the line that repeats a run left the
Safe Harbor answers out; and 'Yes' was refused for 'yes'. Now:

- where somebody is at the keyboard, every entry the written questions
  file holds open and no prompt put is put after the files are written,
  and the table is described again exactly as `--answers` describes it
  (`cli._profile_rounds`); ending input there keeps the files;
- a plain-text answers file of lines `column = answer` is read as the
  questions file it is matched against (`contract.load_answers`);
- the answers file's refusals are its own;
- at a terminal a first line comes before the table is read, and the
  stages after it (`synthtwin.progress`); a piped run prints nothing new;
- the repeat line names the questions file where an answer no option
  repeats stands, and repeating it describes the table byte for byte;
- an answer is taken whatever its capitals;
- the person question answered `keep` is not put again.

ONE CASE AT 20,000 ROWS AND 1,000 PEOPLE; every other case reads a table
of 2,000 rows through the library's small-table setting. Every table is
invented here, with generic names.
"""

from __future__ import annotations

import json
import pathlib
import random
import re
import shutil

import pytest

import keyboard_answers_measures as measures
from synthtwin import asking, cli, contract, errors, parsing, progress, results

clinic_table = measures.clinic_table


def _run(
    argv: "list[str]", ask: "list[str | None] | None" = None, refused: bool = False
) -> "tuple[results.Result, str, str]":
    screen: "list[tuple[str, str]]" = []
    result = cli.run(argv, screen=screen, ask=ask, small_tables_refused=refused)
    out = "".join(text for stream, text in screen if stream == "out")
    err = "".join(text for stream, text in screen if stream == "err")
    return result, out, err


def _copied(table: pathlib.Path, folder: pathlib.Path) -> pathlib.Path:
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(table, folder / table.name)
    return folder / table.name


def _answer_file(questions: pathlib.Path, answers: "dict[str, str]") -> None:
    """Write each answer beside 'your_answer' of the open entry about its column, as a person editing the file does."""
    document = json.loads(questions.read_text(encoding="utf-8"))
    for _section, entry in contract.open_questions(document):
        if entry["column"] in answers:
            offered = [choice["answer"] for choice in entry["answers_you_can_give"]]
            if answers[entry["column"]].strip().casefold() in [one.casefold() for one in offered]:
                entry["your_answer"] = answers[entry["column"]]
    questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")


# The answers a person who knows these columns gives: the patient number
# names the people, the pressure is two measurements, the service code is
# a code, the age is ages in years, the heart rate is no age at all.
_ANSWERS = {
    "subject_id": "identifier",
    "blood_pressure": "joined",
    "service_code": "code",
    "age": "Years",
    "heart_rate": "No",
}


def test_the_keyboard_is_the_file_at_the_table_floor(tmp_path: pathlib.Path) -> None:
    """20,000 rows over 1,000 patients: every question answered at the keyboard, and the same description as the file gives.

    The Safe Harbor questions are put at the keyboard after the files are
    written, answered there, and leave the questions file; the description
    the keyboard gives is the one the questions file answered by hand
    gives, byte for byte; no real patient number or pressure is on the
    screen or in the questions file.
    """
    table, real = clinic_table(tmp_path / "table", 20000, 1000)
    keyed = _copied(table, tmp_path / "keyed")
    # The person at the keyboard types the key the screen shows beside each
    # answer, in the first round and after the files alike, and the real
    # reader reads it (`measures.Typist`).
    # The answered round publishes between columns where the first did not (the patient layer at the floor, lane
    # W5-PL), so the record of earlier descriptions asks for --replace-description, inside one run as in a later
    # one: typed up front on both routes.
    result, out, typist = measures.typed_run(
        ["profile", f"{keyed}", "--replace-description"], {key: _ANSWERS[key].lower() for key in _ANSWERS}, ""
    )
    err = ""
    assert result.verdict == results.NO_MISS, result.refusal
    assert (typist.refused, typist.mismatched) == (0, 0)
    assert "MORE QUESTION(S), FROM THE QUESTIONS FILE" in out
    asked = json.loads((keyed.parent / "clinic-questions.json").read_text(encoding="utf-8"))["asked"]
    assert [entry["column"] for entry in asked if entry["column"] in ("age", "heart_rate")] == []
    shown = out + err + (keyed.parent / "clinic-questions.json").read_text(encoding="utf-8")
    assert [value for value in sorted(real) if value in shown] == []
    filed = _copied(table, tmp_path / "filed")
    # ...and the file route's runs, judged against the keyboard route's description of this same table (the same
    # name, the same installation), type it as well.
    first, _out, _err = _run(["profile", f"{filed}", "--replace-description"])
    assert first.verdict == results.NO_MISS, first.refusal
    _answer_file(filed.parent / "clinic-questions.json", _ANSWERS)
    again, _out, _err = _run(["profile", f"{filed}", "--answers", f"{filed.parent / 'clinic-questions.json'}",
                              "--replace-description"])
    assert again.verdict == results.NO_MISS, again.refusal
    assert (keyed.parent / "clinic-profile.json").read_bytes() == (filed.parent / "clinic-profile.json").read_bytes()


@pytest.fixture
def small(tmp_path: pathlib.Path) -> "tuple[pathlib.Path, set[str]]":
    return clinic_table(tmp_path / "table", 1000, 100)


def test_the_entries_are_shown_in_their_own_words_and_no_cell(
    tmp_path: pathlib.Path, small: "tuple[pathlib.Path, set[str]]"
) -> None:
    """The second round prints each entry's words, a key for every answer it offers, and no value of the table."""
    table, real = small
    result, out, _err = _run(["profile", f"{table}"], ask=[""] * 40)
    assert result.verdict == results.NO_MISS
    # The person question's own words end with a full stop, and the line that
    # says what synthtwin saw ends with one, in both rounds (LANE EZ RULINGS
    # 4 (7), skeptic 1's item 6).
    assert "not the patient.\n" in out and "..\n" not in out
    later = out[out.index("MORE QUESTION(S)"):]
    assert "[no] none of these" in later
    assert "[years] yes: the values are ages counted in years" in later
    assert "Press Enter to leave it open: the Safe Harbor top-code stays" in later
    # The keys that stop and end, named as LANE EZ RULINGS 2 (1) words them.
    assert "To stop, press Ctrl+C; to end your answers, press Ctrl+D (on Windows: Ctrl+Z, then Enter)" in later
    assert [value for value in sorted(real) if value in later] == []


def test_the_keyboard_helper_leaves_every_later_question_open(
    tmp_path: pathlib.Path, small: "tuple[pathlib.Path, set[str]]", monkeypatch: pytest.MonkeyPatch
) -> None:
    """`tests/keyboard.py`'s empty answer leaves every question of the later round open: no second description, the files as one round writes them."""
    import keyboard

    table, _real = small
    keyboard.every_reading_kept(monkeypatch)
    one = _copied(table, tmp_path / "one")
    monkeypatch.setattr(cli, "_ANSWER_ROUNDS_AT_MOST", 1)
    assert cli.main(["profile", f"{one}"], small_tables_refused=False) == 0
    monkeypatch.setattr(cli, "_ANSWER_ROUNDS_AT_MOST", 6)
    two = _copied(table, tmp_path / "two")
    assert cli.main(["profile", f"{two}"], small_tables_refused=False) == 0
    for name in ("clinic-profile.json", "clinic-profile.txt", "clinic-questions.json"):
        assert (one.parent / name).read_bytes() == (two.parent / name).read_bytes(), name


def test_a_question_put_in_the_first_round_is_not_put_again(
    tmp_path: pathlib.Path, small: "tuple[pathlib.Path, set[str]]"
) -> None:
    """Enter at the first round's questions leaves them open, and the later round puts only the entries no prompt put."""
    table, _real = small
    result, out, _err = _run(["profile", f"{table}"], ask=[""] * 40)
    assert result.verdict == results.NO_MISS
    later = out[out.index("MORE QUESTION(S)"):]
    first = out[: out.index("MORE QUESTION(S)")]
    assert "'subject_id'" in first
    assert re.search(r"Question \d+ \(1 of \d+ in this round\)", later) and "'subject_id'" not in later
    put = [(one.subject, one.put) for one in result.questions]
    assert ("age", True) in put and ("subject_id", True) in put


def test_ending_input_in_a_later_round_keeps_the_files(
    tmp_path: pathlib.Path, small: "tuple[pathlib.Path, set[str]]"
) -> None:
    """Ctrl-D, or the end of a library run's lines, in the later round keeps the files; in the first round it still writes nothing."""
    table, _real = small
    kept = _copied(table, tmp_path / "kept")
    declared = ["--identifier", "subject_id", "--code", "service_code", "--measurement", "blood_pressure"]
    result, out, _err = _run(["profile", f"{kept}", *declared], ask=["no"])
    assert result.verdict == results.NO_MISS
    assert "You ended the questions here. The files written above stand as they are." in out
    assert "still open in" in out
    assert (kept.parent / "clinic-profile.json").is_file()
    stopped = _copied(table, tmp_path / "stopped")
    first, _out, err = _run(["profile", f"{stopped}"], ask=[])
    assert first.verdict == results.REFUSED
    assert "nothing was written" in err
    assert not (stopped.parent / "clinic-profile.json").exists()


@pytest.mark.parametrize("typed", ["\x04", "\x1a"], ids=["ctrl-d", "ctrl-z"])
@pytest.mark.parametrize("loop", ["first round", "subject question", "later round"])
def test_ctrl_d_or_ctrl_z_typed_in_a_windows_console_ends_the_answers(typed: str, loop: str) -> None:
    """A line made only of U+0004 or U+001A ends the answers as the end of input does (LANE EZ RULINGS 2 (2)).

    In a Windows console Ctrl+D and Ctrl+Z, typed and handed over with
    Enter, arrive as those characters: each keyboard loop takes them as the
    end of input, and never asks the person to type one of the answers.
    """
    record = results.Asked(
        results.SECTION_ASKED, 1, "heart_rate", "number", "safe-harbor", "a count", "no",
        (results.Offer("no", "none of these", "every value"),), False, "heart_rate",
    )
    session = cli._Session([], [typed, "no", "1"])
    cli._OPEN.sessions += [session]
    try:
        if loop == "first round":
            got: object = cli._read_one_answer(cli._LEFT_OPEN)
        elif loop == "subject question":
            got = cli._subject_question(("patient_number", "clinician_number"))
        else:
            got = cli._put_the_entries([record])
    finally:
        del cli._OPEN.sessions[len(cli._OPEN.sessions) - 1]
    assert got == (([], True) if loop == "later round" else None)
    assert session.answered == 1
    assert "Please type one" not in "".join(text for _stream, text in session.screen)  # type: ignore[union-attr]


def test_a_plain_text_answers_file_is_the_questions_file(
    tmp_path: pathlib.Path, small: "tuple[pathlib.Path, set[str]]"
) -> None:
    """Lines `column = answer`, notes, blank lines, an answer's capitals and quotation marks describe the table as the questions file does."""
    table, _real = small
    filed = _copied(table, tmp_path / "filed")
    _run(["profile", f"{filed}"])
    _answer_file(filed.parent / "clinic-questions.json", {key: _ANSWERS[key] for key in _ANSWERS if key not in ("blood_pressure", "heart_rate")})
    _run(["profile", f"{filed}", "--answers", f"{filed.parent / 'clinic-questions.json'}"])
    written = _copied(table, tmp_path / "written")
    _run(["profile", f"{written}"])
    answers = written.parent / "answers.txt"
    answers.write_text(
        "# what each column is\n\nsubject_id = IDENTIFIER\n"
        "'service_code' = “code”\n  age = Years\n",
        encoding="utf-8",
        newline="\n",
    )
    result, _out, _err = _run(["profile", f"{written}", "--answers", f"{answers}"])
    assert result.verdict == results.NO_MISS, result.refusal
    assert (written.parent / "clinic-profile.json").read_bytes() == (filed.parent / "clinic-profile.json").read_bytes()
    answers.write_text("weigth = no\n", encoding="utf-8", newline="\n")
    refused, _out, err = _run(["profile", f"{written}", "--answers", f"{answers}"])
    assert refused.verdict == results.REFUSED
    assert "Line 1 of your answers file" in err and "'weigth'" in err
    # ...and a column is named exactly: other capitals are refused, naming
    # what the file writes (lane EZ-a's second repair, Codex's item 3).
    answers.write_text("Age = years\n", encoding="utf-8", newline="\n")
    capitals, _out, err = _run(["profile", f"{written}", "--answers", f"{answers}"])
    assert capitals.verdict == results.REFUSED
    assert "'Age'" in err and "'age'" in err and "capitals" in err


def _line_said(questions: pathlib.Path, answers: pathlib.Path, line: str) -> "dict[str, object] | str":
    """One text line read against the questions file: the document filled, or the refusal's words."""
    answers.write_text(line + "\n", encoding="utf-8", newline="\n")
    try:
        return contract.load_answers(f"{answers}", f"{questions}")
    except errors.ProfileError as refused:
        return f"{refused}"


def _answers_of(document: "dict[str, object]") -> "list[tuple[str, str]]":
    """Each answerable entry's (section, your_answer), in the file's order."""
    return [(section, f"{entry.get('your_answer') or ''}") for section, entry in contract.answer_entries(document)]


def test_a_line_two_questions_take_is_refused_and_numbers_are_not_read(tmp_path: pathlib.Path) -> None:
    """A text line naming a column two open questions take its answer for is refused; a number before a column is never read.

    Lane EZ-a's second repair (the orchestrator's LANE EZ RULINGS 7, Codex's
    items 2 and 3, the lane's choice stated in P4-D479): THE NUMBERED FORM
    IS WITHDRAWN. The refusal names both questions by the numbers the screen
    prints and sends the person to the keyboard or the questions file; `2
    visit_code = code` is refused, never read as question 2; a number alone
    answers only a question about the file, and a number past the open
    questions is refused saying an earlier answer is kept already.
    """
    questions = tmp_path / "t-questions.json"
    entry = {"column": "visit_code", "what_synthtwin_saw": "a shape", "read_as_now": "keep", "your_answer": "",
             "answers_you_can_give": [{"answer": "keep", "means": "m", "then_the_description_publishes": "p"},
                                      {"answer": "code", "means": "m", "then_the_description_publishes": "p"}]}
    other = dict(entry, column="ward")
    document = {"asked": [dict(entry), dict(entry), other], "checklist": {"columns": []}}
    questions.write_text(json.dumps(document), encoding="utf-8", newline="\n")
    answers = tmp_path / "a.txt"
    twice = _line_said(questions, answers, "visit_code = code")
    assert twice == errors.answers_line_asks_twice(f"{answers}", 1, "visit_code", ["question 1", "question 2"])
    assert "keyboard" in f"{twice}" and "your_answer" in f"{twice}"
    numbered = _line_said(questions, answers, "2 visit_code = CODE")
    assert numbered == errors.answers_line_numbered(f"{answers}", 1, 2, "visit_code")
    assert _line_said(questions, answers, "2 = CODE") == errors.answers_line_number_alone(f"{answers}", 1, 2, "visit_code")
    assert _line_said(questions, answers, "9 = code") == errors.answers_line_number_not_there(f"{answers}", 1, 9)
    filled = _line_said(questions, answers, "ward = Code")
    assert isinstance(filled, dict) and _answers_of(filled) == [("asked", ""), ("asked", ""), ("asked", "code")]


# THE FAMILIES OF QUESTIONS ONE COLUMN CAN HOLD, each as its kept entry and
# its open question offer them (`asking._FAMILY_WORDS`); the dates question
# shares the age or ZIP question's words and is told apart by what it saw.
_FAMILIES = (
    "kind", "grammar", "clock", "date-codes", "dates", "safe-harbor", "safe-harbor-dates", "unit", "counted",
)


def _kept(column: str, family: str, answer: str) -> "dict[str, object]":
    saw = asking.SAFE_HARBOR_DATES_KEPT_SAW if family == "safe-harbor-dates" else ""
    return asking._kept_entry(column, answer, family, saw)


def _opened(column: str, family: str) -> "dict[str, object]":
    words = asking._FAMILY_WORDS[family]
    saw = f"values that, {asking.SAFE_HARBOR_DATES_SEEN}." if family == "safe-harbor-dates" else f"a {family} shape."
    return {
        "column": column, "what_synthtwin_saw": saw, "read_as_now": words[0], "your_answer": "",
        "answers_you_can_give": [{"answer": one, "means": f"{one}", "then_the_description_publishes": "p"} for one in words],
    }


def test_a_text_answer_never_answers_a_question_opened_since(tmp_path: pathlib.Path) -> None:
    """Every pair of question families that can follow one another about one column, in text and numbered form.

    Codex's item 2 of lane EZ-a (the orchestrator's LANE EZ RULINGS 7): `v
    = no` answered the age or ZIP question; the next questions file keeps
    that answer and opens the question about values that read as dates; the
    same text file handed back answered the new question `no` too, lifting
    the date hold unasked. Generated over every kept family and answer and
    every family opened after it, with a second column beside: the line
    saying again the kept answer fills no open question (the new one stays
    open); the line `N v = answer` for the new question's number is refused;
    a line both questions take another answer for is refused; and no line
    ever fills an entry about the other column.
    """
    questions = tmp_path / "t-questions.json"
    answers = tmp_path / "a.txt"
    # The words the text route tells the dates question by are the asking
    # module's own, mirrored in `contract` (which reaches no reader).
    assert contract._SAFE_HARBOR_DATES_SEEN == asking.SAFE_HARBOR_DATES_SEEN
    checked = 0
    for first in _FAMILIES:
        for kept_answer in asking._FAMILY_WORDS[first]:
            for later in _FAMILIES:
                document = {
                    "asked": [_opened("w", later), _opened("v", later)], "checklist": {"columns": []},
                    asking.ANSWERED_BEFORE: [_kept("v", first, kept_answer)],
                }
                questions.write_text(json.dumps(document), encoding="utf-8", newline="\n")
                before = _answers_of(json.loads(json.dumps(document)))
                said = _line_said(questions, answers, f"v = {kept_answer.upper()}")
                assert isinstance(said, dict), (first, kept_answer, later, said)
                assert _answers_of(said)[:2] == before[:2], (first, kept_answer, later)
                assert isinstance(_line_said(questions, answers, f"2 v = {kept_answer}"), str)
                for word in asking._FAMILY_WORDS[later]:
                    other = _line_said(questions, answers, f"v = {word}")
                    if isinstance(other, str):
                        continue
                    assert _answers_of(other)[0] == before[0], (first, kept_answer, later, word)
                    if word != kept_answer and word in asking._FAMILY_WORDS[first]:
                        # Both take it: refused, unless the open question and
                        # the kept answer are one question (same words, same seen).
                        assert first == later, (first, kept_answer, later, word)
                    checked += 1
    # ...and the pair the verify 2 of lane EZ-a measured (its MINOR 1 (b);
    # the orchestrator's LANE EZ RULINGS 9 (2)): a Safe Harbor question about
    # ZIP-shaped values offers `no` and `yes` alone, the very words of a kept
    # answer to the question about values that read as dates, so only the
    # dates words tell the two apart; the other word, said beside the kept
    # answer, is refused, never read as lifting the ZIP hold unasked.
    zip_question = {
        "column": "v", "what_synthtwin_saw": "five-figure numbers that read as ZIP codes.", "read_as_now": "yes",
        "your_answer": "",
        "answers_you_can_give": [
            {"answer": one, "means": one, "then_the_description_publishes": "p"} for one in ("no", "yes")
        ],
    }
    for kept_answer, other in (("yes", "no"), ("no", "yes")):
        document = {
            "asked": [dict(zip_question)], "checklist": {"columns": []},
            asking.ANSWERED_BEFORE: [_kept("v", "safe-harbor-dates", kept_answer)],
        }
        questions.write_text(json.dumps(document), encoding="utf-8", newline="\n")
        assert isinstance(_line_said(questions, answers, f"v = {other}"), str), (kept_answer, other)
        checked += 1
    assert checked > 100


_CASED = (
    ("ID", "id"), ("Id", "iD"), ("straße", "STRASSE"), ("İd", "id"), ("ΟΔΟΣ", "οδος"), ("οδοσ", "οδος"),
    ("Visit Code", "visit code"), ("dx", "DX"),
)


def test_column_names_are_exact_in_a_text_file(tmp_path: pathlib.Path) -> None:
    """`ID` and `id` are two columns: a line names one exactly, or is refused, never matched by its capitals.

    Codex's item 3 of lane EZ-a: with question 1 about the held patient key
    `ID` and question 2 about the code column `id`, `1 id = code` was taken
    for `ID`. Generated over case variants and the Unicode case folds (the
    sharp s, the dotted capital I, the final sigma), each pair of columns
    in either order with a question each: the exact name fills its own
    entry alone; any other spelling, the capitals changed or the name
    folded, is refused naming what the file writes; a number before either
    name is refused.
    """
    questions = tmp_path / "t-questions.json"
    answers = tmp_path / "a.txt"
    for one, two in _CASED:
        for first, second in ((one, two), (two, one)):
            document = {"asked": [_opened(first, "kind"), _opened(second, "kind")], "checklist": {"columns": []}}
            questions.write_text(json.dumps(document), encoding="utf-8", newline="\n")
            for place, name in ((0, first), (1, second)):
                filled = _line_said(questions, answers, f"{name} = code")
                assert isinstance(filled, dict), (first, second, name, filled)
                assert [answer for _section, answer in _answers_of(filled)] == [
                    "code" if at == place else "" for at in range(2)
                ]
                assert isinstance(_line_said(questions, answers, f"{place + 1} {name} = code"), str)
            for spelling in {first.upper(), first.lower(), first.casefold(), first.swapcase(), second.title()}:
                if spelling in (first, second):
                    continue
                refused = _line_said(questions, answers, f"{spelling} = code")
                assert isinstance(refused, str), (first, second, spelling)


def test_one_question_one_line_in_a_text_file(tmp_path: pathlib.Path) -> None:
    """A duplicated column is refused in every position, whether its question is open or an answer the file keeps.

    Codex's item 7 of lane EZ-a: once `id` stood under `answered_before`,
    `id = identifier` then `id = code` was taken, the last line winning, and
    the hold went. Generated: three columns, one open, one kept, one both;
    every column written twice with every pair of answers, the two lines in
    every position among the others: refused naming both lines.
    """
    questions = tmp_path / "t-questions.json"
    answers = tmp_path / "a.txt"
    document = {
        "asked": [_opened("ward", "kind"), _opened("pulse", "kind")], "checklist": {"columns": []},
        asking.ANSWERED_BEFORE: [_kept("id", "kind", "identifier"), _kept("pulse", "kind", "measurement")],
    }
    questions.write_text(json.dumps(document), encoding="utf-8", newline="\n")
    words = asking._FAMILY_WORDS["kind"]
    refused = 0
    for column in ("ward", "id", "pulse"):
        for one in words:
            for two in words:
                others = [f"{name} = keep" for name in ("ward", "id", "pulse") if name != column]
                for first_at in range(len(others) + 1):
                    for second_at in range(first_at + 1, len(others) + 2):
                        lines = list(others)
                        lines.insert(first_at, f"{column} = {one}")
                        lines.insert(second_at, f"{column} = {two}")
                        answers.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
                        with pytest.raises(errors.ProfileError) as said:
                            contract.load_answers(f"{answers}", f"{questions}")
                        assert f"line {first_at + 1} answers already" in f"{said.value}" or (
                            "already" in f"{said.value}" and f"Line {second_at + 1}" in f"{said.value}"
                        ), lines
                        refused += 1
    assert refused > 200


def _generated_entry(column: str, offered: "tuple[str, ...]", answered: str, now: str) -> "dict[str, object]":
    return {
        "column": column, "what_synthtwin_saw": "a shape.", "read_as_now": now or offered[0], "your_answer": answered,
        "answers_you_can_give": [
            {"answer": one, "means": f"{one}, as meant", "then_the_description_publishes": "p"} for one in offered
        ],
    }


def test_every_text_line_binds_to_its_own_question_or_is_refused(tmp_path: pathlib.Path) -> None:
    """600 generated questions files: the number the round prints is the file's, and a text line fills its own question or is refused.

    Skeptic 1's item 1 of lane EZ-a (a BLOCKER, LANE EZ RULINGS 4 (2)) and
    Codex's items 2 and 3 (RULINGS 7): the round printed its own count, and
    a text line written from it landed on the patient number's question.
    Generated: questions about the file, asked ones and checklist entries,
    some answered, some open, some put again under the reading an answer
    gave, and kept answers; the round puts a random set of the open ones.
    The numbers printed are the file's (`contract.question_number`), the
    closing line's labels. For each entry the round prints: `column =
    answer`, the column named exactly, fills exactly that entry wherever no
    other question about the column takes the answer and the file keeps no
    such answer, and is refused where another open one takes it; written
    with other capitals it is refused (the verify's v9); `N column =
    answer` is refused; a question about the file is answered by its number
    alone; and no line ever fills an entry about another column.
    """
    draw = random.Random(479)
    questions = tmp_path / "t-questions.json"
    answers = tmp_path / "a.txt"
    columns = ("age", "weight", "dx_code", "ward", "lab_value", "visit_code", "pulse")
    words = ("keep", "code", "identifier", "measurement", "no", "yes")
    checked = refused = 0
    for _case in range(600):
        sections: "dict[str, list[dict[str, object]]]" = {"about_your_file": [], "asked": [], "checklist": []}
        for section in sections:
            for _one in range(draw.randint(0, 4)):
                column = "the order of the day and the month in your dates" if section == "about_your_file" else draw.choice(columns)
                offered = tuple(draw.sample(("month-first", "day-first", "data"), 2)) if section == "about_your_file" else tuple(
                    draw.sample(words, draw.randint(2, 4))
                )
                state = draw.random()
                sections[section] += [_generated_entry(
                    column, offered, draw.choice(offered) if state < 0.3 else "",
                    draw.choice(offered) if 0.3 <= state < 0.5 else "",
                )]
        kept = [
            _generated_entry(column, tuple(draw.sample(words, 3)), "", "")
            for column in draw.sample(columns, draw.randint(0, 2))
        ]
        for entry in kept:
            entry["your_answer"] = entry["read_as_now"]
        document = {"about_your_file": sections["about_your_file"], "asked": sections["asked"],
                    "checklist": {"columns": sections["checklist"]}, asking.ANSWERED_BEFORE: kept}
        text = json.dumps(document)
        questions.write_text(text, encoding="utf-8", newline="\n")
        records: "list[results.Asked]" = []
        for section in sections:
            for order in range(1, len(sections[section]) + 1):
                entry = sections[section][order - 1]
                if entry["your_answer"] or draw.random() < 0.4:
                    continue
                records += [results.Asked(
                    section, order, "" if section == "about_your_file" else f"{entry['column']}", "role", "reason",
                    "a shape.", f"{entry['read_as_now']}",
                    tuple(results.Offer(f"{one['answer']}", f"{one['means']}", "p")
                          for one in entry["answers_you_can_give"]),  # type: ignore[attr-defined]
                    False, f"{entry['column']}",
                )]
        if not records:
            continue
        screen: "list[tuple[str, str]]" = []
        session = cli._Session(screen, [""] * len(records))
        session.files = [results.FileWritten(results.FILE_QUESTIONS, f"{questions}")]
        cli._OPEN.sessions += [session]
        try:
            cli._put_the_entries(records)
        finally:
            del cli._OPEN.sessions[len(cli._OPEN.sessions) - 1]
        printed = [
            (int(found.group("number")), found.group("column") or found.group("about"))
            for found in measures.ON_SCREEN.finditer("".join(text for _stream, text in screen))
        ]
        assert [about for _number, about in printed] == [record.subject for record in records]
        original = json.loads(text)
        standing = contract.open_questions(original)
        entries = contract.answer_entries(original)
        before = _answers_of(original)
        for place in range(len(records)):
            number, about = printed[place]
            record = records[place]
            assert f"{standing[number - 1][1]['column']}" == about
            answer = draw.choice([offer.answer for offer in record.offers])
            if not record.column:
                filled = _line_said(questions, answers, f"{number} = {answer}")
                assert isinstance(filled, dict), filled
                changed = [at for at in range(len(before)) if _answers_of(filled)[at] != before[at]]
                assert [entries[at][1] is standing[number - 1][1] for at in changed] == [True]
                checked += 1
                continue
            takers = [
                at for at, (section, entry) in enumerate(entries)
                if entry["column"] == about and answer in [one["answer"] for one in entry["answers_you_can_give"]]
                and (section == asking.ANSWERED_BEFORE or not f"{entry.get('your_answer') or ''}")
            ]
            holding = [at for at in takers if entries[at][0] == asking.ANSWERED_BEFORE and entries[at][1]["your_answer"] == answer]
            filled = _line_said(questions, answers, f"{about} = {answer.upper()}")
            if isinstance(filled, dict):
                changed = [at for at in range(len(before)) if _answers_of(filled)[at] != before[at]]
                # Never an entry about another column, never one that does not take the answer.
                assert all(at in takers for at in changed) and len(changed) <= 1, (about, answer, changed)
                assert not holding or changed == [], (about, answer, changed)
                if not holding and len(takers) == 1:
                    assert changed == takers, (about, answer, changed)
                checked += 1
            else:
                assert not holding and len(takers) != 1, (about, answer, filled)
                refused += 1
            for wrong in (f"{number} {about} = {answer}", f"{about.upper()} = {answer}", f"{number} = {answer}"):
                assert isinstance(_line_said(questions, answers, wrong), str), wrong
                refused += 1
    assert checked > 600 and refused > 800


def test_the_laboratory_table_answers_by_the_column_on_the_screen(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Skeptic 1's own shape: the patient number left open at the first prompt, the round opening with the checklist.

    Enter at every question; the round prints the diagnosis code's question
    with the number the file gives it, which is not 1 (a label); `dx =
    code` written from the screen answers the diagnosis code, the patient
    number stays held and no real patient number reaches any file or the
    screen; the line written with the number before the column, and the
    number alone, are refused (lane EZ-a's second repair: no number is read
    back for a column's question). 'what synthtwin saw' ends with one full
    stop, in both rounds (LANE EZ RULINGS 4 (7)), and the closing line says
    'it' for one question still open (the verify's MINOR 6). The two table
    floors lowered for this file's small table alone.
    """
    monkeypatch.setattr(parsing, "TABLE_ROW_FLOOR", 400)
    monkeypatch.setattr(parsing, "TABLE_PEOPLE_FLOOR", 40)
    table, real = measures.labs_table(tmp_path / "labs", 2000, 100)
    result, screen, _typist = measures.typed_run(["profile", f"{table}"], {}, person="")
    assert result.verdict == results.NO_MISS, result.refusal
    later = screen[screen.index("MORE QUESTION(S)"):]
    printed = {
        found.group("column"): int(found.group("number"))
        for found in measures.ON_SCREEN.finditer(later) if found.group("number")
    }
    assert "dx" in printed and printed["dx"] > 1 and "patient_no" not in printed
    assert "..\n" not in screen and "what synthtwin saw:" in screen
    answers = table.parent / "answers.txt"
    for wrong in (f"{printed['dx']} dx = code", f"{printed['dx']} = code", "1 dx = code"):
        answers.write_text(wrong + "\n", encoding="utf-8", newline="\n")
        refused, _out, err = _run(["profile", f"{table}", "--answers", f"{answers}"], refused=True)
        assert refused.verdict == results.REFUSED, wrong
    answers.write_text("dx = code\n", encoding="utf-8", newline="\n")
    again, out, err = _run(["profile", f"{table}", "--answers", f"{answers}"], refused=True)
    assert again.verdict == results.NO_MISS, again.refusal
    settings = json.loads((table.parent / "labs-profile.json").read_text(encoding="utf-8"))["settings"]
    assert settings["forced_codes"] == ["dx"] and "patient_no" in settings["forced_identifiers"]
    written = out + err + "".join(
        (table.parent / name).read_text(encoding="utf-8")
        for name in ("labs-profile.json", "labs-profile.txt", "labs-questions.json")
    )
    assert set(re.findall(r"[0-9]+", written)) & real == set()
    one = cli._how_to_answer_said(None, 1)
    assert one.startswith(" To answer it,") and cli._how_to_answer_said(None, 2).startswith(" To answer them,")


def test_a_question_answered_at_the_first_prompt_is_not_said_open(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Sodium answered at the first prompt is not counted open, and the command the closing line teaches runs.

    Lane EZ-a's repair (skeptic 1's item 3; LANE EZ RULINGS 4 (4)): the
    file puts an answered question again under the reading its answer gave
    (plan P4-D401), and the closing line counted it 'still open' and told
    the person to run the same command again, which the one overwrite rule
    refuses once the files exist. Here the patient number is left open with
    Enter and sodium answered `measurement`: one question is said open, the
    patient number, which 'stays' held; the line names a command with
    `--answers` and the questions file, and that command, run, is not
    refused. The two table floors lowered for this file's small table.
    """
    monkeypatch.setattr(parsing, "TABLE_ROW_FLOOR", 400)
    monkeypatch.setattr(parsing, "TABLE_PEOPLE_FLOOR", 40)
    table, _real = measures.stays_table(tmp_path / "stays", 2000, 100)
    plan: "dict[str, object]" = {"patient_no": "", "sodium": ("measurement",), "pulse": ("measurement", "no"),
                                 "dx": ("code",)}
    result, screen, typist = measures.typed_run(["profile", f"{table}"], plan, person="")
    assert result.verdict == results.NO_MISS, result.refusal
    assert typist.kept_undeclared == ["sodium"]
    closing = screen[screen.rindex("still open"):]
    assert "\n1 question is still open in" in screen
    assert re.search(r"\(question \d+, patient_no\)", closing) and "sodium" not in closing
    assert "patient_no stays held as record numbers" in closing
    taught = re.search(r"run this at the keyboard:\n  ([^\n]+)\n", closing)
    assert taught is not None and "--answers" in taught.group(1)
    # ...and the repeat line the round's description printed names the
    # questions file, which carries sodium's answer no option repeats, so
    # running it describes the table byte for byte (measured before the
    # repair: it held sodium, and the description differed).
    words = screen[screen.rindex("TO REPEAT THIS RUN WITHOUT THE QUESTIONS, add:"):].split("\n")[1]
    assert "--answers" in words
    described = (table.parent / "stays-profile.json").read_bytes()
    repeated, _out, err = _run(["profile", f"{table}"] + measures.shell_words(words), refused=True)
    assert repeated.verdict == results.NO_MISS, err
    assert (table.parent / "stays-profile.json").read_bytes() == described
    again, _out, err = _run(measures.shell_words(taught.group(1))[1:], ask=[""] * 40, refused=True)
    assert again.verdict == results.NO_MISS, err


def test_the_answers_file_has_messages_of_its_own(tmp_path: pathlib.Path) -> None:
    """A curly quotation mark is said first, with the line and character; the description's own message is unchanged."""
    broken = tmp_path / "t-questions.json"
    broken.write_text('{\n  “asked”: []\n}\n', encoding="utf-8", newline="\n")
    with pytest.raises(errors.ProfileError) as answers:
        contract.load_answers(f"{broken}")
    said = f"{answers.value}"
    assert said.startswith(f"Your answers file at {broken} holds curly quotation marks")
    assert "line 2, character 3" in said and "run the same command again" in said
    assert "description" not in said and "make" not in said
    with pytest.raises(errors.ProfileError) as missing:
        contract.load_answers(f"{tmp_path / 'none.json'}")
    assert "your answers" in f"{missing.value}" and "description" not in f"{missing.value}"
    with pytest.raises(errors.ProfileError) as described:
        contract.load_profile(f"{broken}")
    assert f"{described.value}" == errors.profile_not_json(f"{broken}", 2, 3)


def test_answers_are_taken_whatever_their_capitals(
    tmp_path: pathlib.Path, small: "tuple[pathlib.Path, set[str]]"
) -> None:
    """'Yes', ' NO ' and 'Years' are the offered answers 'yes', 'no' and 'years'."""
    table, _real = small
    lower = _copied(table, tmp_path / "lower")
    _run(["profile", f"{lower}"])
    _answer_file(lower.parent / "clinic-questions.json", {"age": "years", "heart_rate": "no"})
    _run(["profile", f"{lower}", "--answers", f"{lower.parent / 'clinic-questions.json'}"])
    upper = _copied(table, tmp_path / "upper")
    _run(["profile", f"{upper}"])
    questions = upper.parent / "clinic-questions.json"
    document = json.loads(questions.read_text(encoding="utf-8"))
    for entry in document["asked"]:
        if entry["column"] == "age":
            entry["your_answer"] = "Years"
        if entry["column"] == "heart_rate":
            entry["your_answer"] = " NO "
    questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
    result, _out, _err = _run(["profile", f"{upper}", "--answers", f"{questions}"])
    assert result.verdict == results.NO_MISS, result.refusal
    assert (upper.parent / "clinic-profile.json").read_bytes() == (lower.parent / "clinic-profile.json").read_bytes()


def test_the_repeat_line_repeats_every_answer(
    tmp_path: pathlib.Path, small: "tuple[pathlib.Path, set[str]]", monkeypatch: pytest.MonkeyPatch
) -> None:
    """Safe Harbor answers no option repeats: the repeat line names the questions file, and repeating it describes the table byte for byte."""
    table, _real = small
    # The floors are lowered part way below, where the shipped command would draw the patient layer its first
    # description did not (lane W5-PL): the layer is left out, so every description here is the same table's.
    monkeypatch.setattr(cli, "_PATIENT_LAYER_SHIPPED", False)
    _run(["profile", f"{table}"])
    questions = table.parent / "clinic-questions.json"
    _answer_file(questions, {"subject_id": "identifier", "service_code": "code", "blood_pressure": "keep",
                             "age": "years", "heart_rate": "no"})
    result, out, _err = _run(["profile", f"{table}", "--answers", f"{questions}"])
    assert result.verdict == results.NO_MISS, result.refusal
    words = out[out.index("TO REPEAT THIS RUN WITHOUT THE QUESTIONS, add:"):].split("\n")[1]
    assert "--answers" in words
    described = (table.parent / "clinic-profile.json").read_bytes()
    again, _out, _err = _run(["profile", f"{table}"] + measures.shell_words(words))
    assert again.verdict == results.NO_MISS, again.refusal
    assert (table.parent / "clinic-profile.json").read_bytes() == described
    # K-HZ-31'S REPEAT STEP (Codex's item 8 of lane EZ-a): the line owed and
    # missing, or a command it makes that does not finish -- here without
    # `--answers`, refused by the overwrite rule while the description stays
    # -- is counted; comparing bytes after it proved nothing. The measure
    # runs at the table floors, lowered here for this small table.
    monkeypatch.setattr(parsing, "TABLE_ROW_FLOOR", 400)
    monkeypatch.setattr(parsing, "TABLE_PEOPLE_FLOOR", 40)
    stands, repeated = measures._repeated(table, out, True)
    assert stands and repeated == (table.parent / "clinic-profile.json").read_text(encoding="utf-8")
    without = out.replace(words, words.split(" --answers")[0])
    assert measures._repeated(table, without, True) == (False, "")
    assert measures._repeated(table, "no repeat line here", True) == (False, "")
    assert measures._repeated(table, "no repeat line here", False) == (True, "")


def test_a_first_line_and_progress_at_a_terminal_only(
    tmp_path: pathlib.Path, small: "tuple[pathlib.Path, set[str]]",
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """At a terminal the first line comes before anything is read and the stages follow on the error stream; piped, nothing new.

    And nobody at the keyboard is put no round after the files: a piped
    run and a library run without a reader show no later round's banner
    and read no line (lane EZ-a's repair; skeptic 1's item 5, whose mutant
    putting the round wherever no chain is switched on survived).
    """
    table, _real = small
    read: "list[str]" = []
    real_asked = cli._asked

    def asked(prompt: str) -> "str | None":
        read.append(prompt)
        return real_asked(prompt)

    monkeypatch.setattr(cli, "_asked", asked)
    assert cli.main(["profile", f"{table}", "--replace"], small_tables_refused=False) == 0
    piped = capsys.readouterr()
    assert "do not close this window" not in piped.out and "  ... " not in piped.err
    assert "MORE QUESTION(S)" not in piped.out and "You ended the questions here" not in piped.out
    nobody: "list[tuple[str, str]]" = []
    cli.run(["profile", f"{table}", "--replace"], screen=nobody, small_tables_refused=False)
    assert "MORE QUESTION(S)" not in "".join(text for _stream, text in nobody)
    assert read == []
    monkeypatch.setattr(cli.os, "isatty", lambda handle: True)
    monkeypatch.setattr(cli, "_there_is_somebody_to_ask", lambda: False)
    assert cli.main(["profile", f"{table}", "--replace"], small_tables_refused=False) == 0
    shown = capsys.readouterr()
    assert shown.out.startswith("Reading clinic.csv: on a large table this takes a long time; do not close this window.")
    assert "  ... counting the people in the table" in shown.err
    assert "  ... describing column 1 of 13" in shown.err
    assert not progress.is_on()
    screen: "list[tuple[str, str]]" = []
    cli.run(["profile", f"{table}", "--replace"], screen=screen, small_tables_refused=False)
    assert "do not close this window" not in "".join(text for _stream, text in screen)


def test_the_person_question_answered_keep_is_not_put_again(
    tmp_path: pathlib.Path, small: "tuple[pathlib.Path, set[str]]"
) -> None:
    """A keep answer to the person question stands under 'answered_before' and is not asked again; the description is the one keep gives."""
    table, _real = small
    _run(["profile", f"{table}"])
    questions = table.parent / "clinic-questions.json"
    _answer_file(questions, {"subject_id": "keep"})
    _run(["profile", f"{table}", "--answers", f"{questions}"])
    document = json.loads(questions.read_text(encoding="utf-8"))
    assert [entry["column"] for entry in document["asked"] if entry["column"] == "subject_id"] == []
    assert [entry["column"] for entry in document["answered_before"] if entry["column"] == "subject_id"] == ["subject_id"]
    # ...The round that reads the answer puts the heart rate the record-number question (a held column of small whole
    # numbers beside a person kept) and the next round lists it in the checklist again, so the description of the
    # round after the answer is the one the answer keeps (batch 4v: lane RX-1's narrowing of the age cap moved the
    # question this table's heart rate was put before; CARRIED, owner lane RX-2: one round of questions for it).
    _run(["profile", f"{table}", "--answers", f"{questions}"])
    first = (table.parent / "clinic-profile.json").read_bytes()
    _run(["profile", f"{table}", "--answers", f"{questions}"])
    assert (table.parent / "clinic-profile.json").read_bytes() == first


def _numbered_visits(folder: pathlib.Path) -> "tuple[pathlib.Path, set[str]]":
    """Codex's item 1 table of lane EZ-a, at the library's small size: seven-figure patient numbers twenty rows each, a pulse of 60 to 79, a ward."""
    draw = random.Random(3)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "visits.csv"
    ids = [f"{4000000 + place * 37}" for place in range(100)]
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write("patient_no,pulse,ward\n")
        for row in range(2000):
            handle.write(f"{ids[row % 100]},{draw.randint(60, 79)},{draw.choice(['north', 'south'])}\n")
    return path, set(ids)


def test_a_later_round_keeps_the_newest_answer_over_the_command_line(tmp_path: pathlib.Path) -> None:
    """A typed declaration a keyboard answer replaced never comes back in a later round, its repeat line or the command taught.

    Codex's item 1 of lane EZ-a (LANE EZ RULINGS 7): `--decimal-comma
    patient_no` typed, `identifier` answered at the first prompt, then
    `measurement` at the pulse's checklist question after the files: the
    later round handed the typed comma back as newer than the kept
    `identifier` (`asking.typed_over_kept`), read the patient numbers as
    counts and published them. Now the patient number stays held in every
    round, no real patient number reaches a file or the screen, the repeat
    line says to take the typed option out, and running that line describes
    the table byte for byte. Every other role a command line declares, set
    against every keyboard answer, is the generated case below.
    """
    typed = "--decimal-comma"
    table, ids = _numbered_visits(tmp_path / "comma")
    result, out, typist = measures.typed_run(
        ["profile", f"{table}", typed, "patient_no"], {"patient_no": ("identifier",), "pulse": ("measurement",)},
        person="", refused=False,
    )
    err = ""
    assert result.verdict == results.NO_MISS, result.refusal
    assert "MORE QUESTION(S)" in out and (typist.refused, typist.mismatched) == (0, 0)
    settings = json.loads((table.parent / "visits-profile.json").read_text(encoding="utf-8"))["settings"]
    assert settings["forced_identifiers"] == ["patient_no"]
    assert "patient_no" not in settings["forced_decimal_commas"] + settings["forced_measurements"]
    written = out + err + "".join(
        (table.parent / name).read_text(encoding="utf-8")
        for name in ("visits-profile.json", "visits-profile.txt", "visits-questions.json")
    )
    assert [one for one in sorted(ids) if one in written] == []
    last = out[out.rindex("TO REPEAT THIS RUN WITHOUT THE QUESTIONS, add:"):]
    assert "take these out of the command you typed" in last and f"{typed} patient_no" in last
    words = last.split("\n")[1]
    described = (table.parent / "visits-profile.json").read_bytes()
    again, _out, _err = _run(["profile", f"{table}"] + measures.shell_words(words))
    assert again.verdict == results.NO_MISS and (table.parent / "visits-profile.json").read_bytes() == described


_ROLE_WORDS = ("identifier", "code", "measurement", "decimal_comma", "twelve-hour", "excel-1900", "dates")
# The pairs one column cannot hold at once, as the product refuses or ignores them typed together.
_NEVER_TOGETHER = (
    {"identifier", "code"}, {"identifier", "measurement"}, {"code", "measurement"},
    {"decimal_comma", "identifier"}, {"decimal_comma", "code"}, {"twelve-hour", "code"},
    {"excel-1900", "code"}, {"excel-1900", "identifier"}, {"excel-1900", "measurement"}, {"excel-1900", "twelve-hour"},
)


def _given_of(answers: "asking.Answers", columns: "tuple[str, ...]") -> "asking.Given":
    """What a run acts on, as its questions file keeps it, from what `asking.answers_in` read (the declarations alone)."""
    return asking.Given(
        columns=columns, codes=tuple(answers.codes), identifiers=tuple(answers.identifiers),
        measurements=tuple(answers.measurements), decimal_commas=tuple(answers.decimal_commas),
        twelve_hours=tuple(answers.twelve_hours), date_counts=tuple(answers.date_counts),
        date_columns=tuple(answers.date_columns),
    )


def _declared(answers: "asking.Answers", column: str) -> "set[str]":
    found: "set[str]" = set()
    for word, names in (
        ("identifier", answers.identifiers), ("code", answers.codes), ("measurement", answers.measurements),
        ("decimal_comma", answers.decimal_commas), ("twelve-hour", answers.twelve_hours),
        ("dates", answers.date_columns),
    ):
        if column in names:
            found.add(word)
    found |= {system for name, system in answers.date_counts if name == column}
    return found


def test_every_typed_declaration_loses_to_a_newer_answer_over_three_rounds() -> None:
    """Every role a command line declares against every keyboard answer for the same column, over three rounds (Codex's item 1).

    Round one keeps the keyboard's answer under `answered_before` beside the
    typed declarations it did not replace, as a run writes its questions
    file; each later round hands the command line back less what an answer
    of the file replaces (`asking.typed_answered_over`), and reads the file
    as `_run_profile_body` reads it (`typed_over_kept`, then `answers_in`).
    In every round the keyboard's answer stands, and no pair the product
    refuses typed together is ever read.
    """
    checked = 0
    for typed_word in _ROLE_WORDS:
        for keyboard_word in _ROLE_WORDS:
            if typed_word == keyboard_word:
                continue
            together = {typed_word, keyboard_word} not in _NEVER_TOGETHER
            kept = _given_of(asking.answers_in(
                {"asked": [], "checklist": {"columns": []},
                 asking.ANSWERED_BEFORE: asking.answered_before(_given_from_words("c", [keyboard_word] + ([typed_word] if together else [])))},
                "q.json",
            ), ("c",))
            given = kept
            for _round in range(3):
                document = {"asked": [], "checklist": {"columns": []}, asking.ANSWERED_BEFORE: asking.answered_before(given)}
                typed = (("c", typed_word),)
                replaced = asking.typed_answered_over(document, typed)
                left = tuple(one for one in typed if one not in replaced)
                answers = asking.answers_in(asking.typed_over_kept(document, left), "q.json")
                declared = _declared(answers, "c") | {word for _name, word in left}
                assert keyboard_word in declared, (typed_word, keyboard_word, _round, declared)
                assert not [pair for pair in _NEVER_TOGETHER if pair <= declared], (typed_word, keyboard_word, declared)
                assert (typed_word in declared) == together, (typed_word, keyboard_word, declared)
                given = _given_of(answers, ("c",))
                checked += 1
    assert checked == len(_ROLE_WORDS) * (len(_ROLE_WORDS) - 1) * 3


def _given_from_words(column: str, words: "list[str]") -> "asking.Given":
    """A `Given` declaring ``words`` about one column, as a run that acted on them keeps them."""
    return asking.Given(
        columns=(column,),
        codes=(column,) if "code" in words else (), identifiers=(column,) if "identifier" in words else (),
        measurements=(column,) if "measurement" in words else (),
        decimal_commas=(column,) if "decimal_comma" in words else (),
        twelve_hours=(column,) if "twelve-hour" in words else (),
        date_counts=((column, "excel-1900"),) if "excel-1900" in words else (),
        date_columns=(column,) if "dates" in words else (),
    )


@pytest.mark.parametrize("redirected", ["2>run.log", ">out.log"])
def test_the_counters_follow_the_stream_they_are_written_to(monkeypatch: pytest.MonkeyPatch, redirected: str) -> None:
    """The first line asks the output stream, the counters the error stream they are written to (Codex's item 10 of lane EZ-a).

    `synthtwin profile table.csv 2>run.log`: the output stream stayed a
    terminal, so the counters went on and the log filled with lines written
    over in place. Now with the error stream redirected no counter is
    switched on, and with the output stream redirected the counters still
    show on the terminal and the first line is not written into the file.
    The run's whole terminal path is `test_a_first_line_and_progress_at_a_terminal_only`.
    """
    terminal = 1 if redirected == "2>run.log" else 2
    monkeypatch.setattr(cli.os, "isatty", lambda handle: handle == terminal)
    session = cli._Session(cli.TERMINAL, None)
    cli._OPEN.sessions += [session]
    try:
        first = cli._progress_at_a_terminal()
        cli._counting_switched_on("describing")
        counting = progress.is_on()
        progress.switch_off()
    finally:
        del cli._OPEN.sessions[len(cli._OPEN.sessions) - 1]
    assert (first, counting) == ((True, False) if redirected == "2>run.log" else (False, True))


def test_a_keep_typed_at_the_person_question_is_not_put_again(
    tmp_path: pathlib.Path, small: "tuple[pathlib.Path, set[str]]"
) -> None:
    """`keep` typed at the first prompt's person question is carried, and the command taught does not put it again (the verify's MINOR 3).

    Lane EZ-a's second repair (LANE EZ RULINGS 8 (5)): written in the
    questions file, `keep` was carried under `answered_before`; typed at
    the keyboard it was put again at every run. The description is the one
    `keep` gives in every round.
    """
    table, _real = small
    result, out, _typist = measures.typed_run(
        ["profile", f"{table}"], {"subject_id": ("means:not a person",)}, person="", refused=False
    )
    assert result.verdict == results.NO_MISS, result.refusal
    assert "'subject_id'" in out[: out.index("MORE QUESTION(S)")]
    questions = table.parent / "clinic-questions.json"
    kept = json.loads(questions.read_text(encoding="utf-8"))[asking.ANSWERED_BEFORE]
    assert [entry["your_answer"] for entry in kept if entry["column"] == "subject_id"] == ["keep"]
    first = (table.parent / "clinic-profile.json").read_bytes()
    again, again_out, _err = _run(["profile", f"{table}", "--answers", f"{questions}"], ask=[""] * 40)
    assert again.verdict == results.NO_MISS, again.refusal
    assert "'subject_id'" not in again_out
    assert (table.parent / "clinic-profile.json").read_bytes() == first


def test_a_later_round_whose_write_stops_is_not_said_to_stand(
    tmp_path: pathlib.Path, small: "tuple[pathlib.Path, set[str]]", monkeypatch: pytest.MonkeyPatch
) -> None:
    """A later round whose description write stopped part-way is not told 'the files ... stand as they were' (the verify's v8 of lane EZ-a).

    The write transaction's own account of what is on disk stands (commit
    0b818185): the later round's write raising with that account here
    stands in for a disk that filled up between the two files.
    """
    from synthtwin import profile

    table, _real = small
    real_write = profile.write_both_files
    calls = [0]
    said = "The description was written and its summary was not: the disk is full."

    def stopping(*args: object, **kwargs: object) -> object:
        calls[0] += 1
        if calls[0] == 2:
            state = kwargs["state"]
            state.sentence = said  # type: ignore[attr-defined]
            raise errors.ProfileError(said)
        return real_write(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(profile, "write_both_files", stopping)
    result, screen, _typist = measures.typed_run(
        ["profile", f"{table}"], {"age": ("years",), "heart_rate": ("no",)}, person="", refused=False
    )
    assert calls[0] == 2, screen[-1500:]
    assert said in screen and "stand as they were" not in screen


def test_the_twin_counts_no_question_whose_answer_stands(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The twin command at the keyboard leaves a first-prompt answer out of the questions it says are still open (the verify's v6).

    Hospital stays: sodium answered `measurement` at the first prompt, the
    patient number and the rest left open with Enter: the twin's last lines
    count the questions still open, and sodium is not among them.
    """
    monkeypatch.setattr(parsing, "TABLE_ROW_FLOOR", 400)
    monkeypatch.setattr(parsing, "TABLE_PEOPLE_FLOOR", 40)
    table, _real = measures.stays_table(tmp_path / "stays", 2000, 100)
    screen: "list[tuple[str, str]]" = []
    typist = measures.Typist(screen, {"patient_no": "", "sodium": ("measurement",)}, "")
    typist.questions = table.parent / f"stays{cli._TWIN_FOLDER_MARK}" / "stays-questions.json"
    real_question = cli._the_question

    def watched(question: object, place: int, total: int, held: bool = False) -> str:
        typist.question = question
        return real_question(question, place, total, held)  # type: ignore[arg-type]

    monkeypatch.setattr(cli, "_asked", typist)
    monkeypatch.setattr(cli, "_the_question", watched)
    result = cli.run(["twin", f"{table}"], screen=screen, ask=[], small_tables_refused=True)
    shown = "".join(text for _stream, text in screen)
    assert typist.kept_undeclared == ["sodium"], shown[-1500:]
    counted = re.search(r"(\d+) question\(s\) are still open", shown)
    assert counted is not None, shown[-1500:]
    first = result.steps[0].questions
    assert [one for one in first if one.offers and one.subject == "sodium"]
    assert int(counted.group(1)) == len([
        one for one in first
        if one.offers and one.section in (results.SECTION_ABOUT_FILE, results.SECTION_ASKED) and one.subject != "sodium"
    ])


def test_the_twin_teaches_no_typed_option_a_newer_answer_replaced(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The twin's answers command leaves off a typed declaration a keyboard answer replaced (Codex's item 1 of lane EZ-a, the taught command).

    `synthtwin twin visits.csv --decimal-comma patient_no`, `identifier`
    answered at the first prompt, every other question left open: the
    command the twin teaches hands its questions file back, and a typed
    option handed back with it is later than the file's kept answer, so
    the comma came back over `identifier` and published the patient
    numbers. The twin's description holds the patient number, and the
    line it teaches no longer types the comma. An age column's Safe Harbor
    question, left open, makes the twin teach the command.
    """
    draw = random.Random(9)
    (tmp_path / "twin").mkdir()
    table = tmp_path / "twin" / "visits.csv"
    ids = [f"{4000000 + place * 37}" for place in range(100)]
    with open(table, "w", encoding="utf-8", newline="") as handle:
        handle.write("patient_no,pulse,age\n")
        for row in range(2000):
            handle.write(f"{ids[row % 100]},{draw.randint(60, 79)},{20 + row % 90}\n")
    screen: "list[tuple[str, str]]" = []
    typist = measures.Typist(screen, {"patient_no": ("identifier",)}, "")
    typist.questions = table.parent / f"visits{cli._TWIN_FOLDER_MARK}" / "visits-questions.json"
    real_question = cli._the_question

    def watched(question: object, place: int, total: int, held: bool = False) -> str:
        typist.question = question
        return real_question(question, place, total, held)  # type: ignore[arg-type]

    monkeypatch.setattr(cli, "_asked", typist)
    monkeypatch.setattr(cli, "_the_question", watched)
    result = cli.run(["twin", f"{table}", "--decimal-comma", "patient_no"], screen=screen, ask=[], small_tables_refused=False)
    shown = "".join(text for _stream, text in screen)
    assert result.verdict in (results.NO_MISS, results.MISSED), shown[-1500:]
    folder = table.parent / f"visits{cli._TWIN_FOLDER_MARK}"
    settings = json.loads((folder / "visits-profile.json").read_text(encoding="utf-8"))["settings"]
    assert "patient_no" in settings["forced_identifiers"] and "patient_no" not in settings["forced_decimal_commas"]
    taught = re.search(r"run this at a terminal\n  ([^\n]+)\n", shown)
    assert taught is not None, shown[-1500:]
    assert "--answers" in taught.group(1) and "--decimal-comma" not in taught.group(1)
    written = (folder / "visits-profile.json").read_text(encoding="utf-8") + (folder / "visits-questions.json").read_text(encoding="utf-8")
    assert [one for one in sorted(ids) if one in written] == []


def test_profile_teaches_no_typed_option_a_newer_answer_replaced(tmp_path: pathlib.Path) -> None:
    """Profile's closing command leaves off a typed declaration a keyboard answer replaced, and run, keeps the patient number held.

    The verify 2's MINOR 1 (a) of lane EZ-a (the orchestrator's LANE EZ
    RULINGS 9 (2)): the command profile's closing lines teach
    (`cli._profile_again`) was pinned by no case, and on repair 1's head
    that path published 10 real patient numbers at 20,000 rows (Codex's
    item 1 of the lane). Codex's comma table with an age column whose Safe
    Harbor question is left open: `--decimal-comma patient_no` typed and
    `identifier` answered at the first prompt; the command taught holds
    `--answers` and no `--decimal-comma`, and run, the patient number stays
    an identifier, no real patient number in a file or on the screen.
    """
    draw = random.Random(9)
    folder = tmp_path / "taught"
    folder.mkdir()
    table = folder / "visits.csv"
    ids = [f"{4000000 + place * 37}" for place in range(100)]
    with open(table, "w", encoding="utf-8", newline="") as handle:
        handle.write("patient_no,pulse,age\n")
        for row in range(2000):
            handle.write(f"{ids[row % 100]},{draw.randint(60, 79)},{20 + row % 90}\n")
    result, shown, typist = measures.typed_run(
        ["profile", f"{table}", "--decimal-comma", "patient_no"], {"patient_no": ("identifier",)},
        person="", refused=False,
    )
    assert result.verdict == results.NO_MISS, result.refusal
    assert (typist.refused, typist.mismatched) == (0, 0)
    taught = re.search(r"run this at the keyboard:\n  ([^\n]+)\n", shown)
    assert taught is not None, shown[-1500:]
    assert "--answers" in taught.group(1) and "--decimal-comma" not in taught.group(1)
    again, out, err = _run(measures.shell_words(taught.group(1))[1:], ask=[""] * 40)
    assert again.verdict == results.NO_MISS, err
    settings = json.loads((folder / "visits-profile.json").read_text(encoding="utf-8"))["settings"]
    assert "patient_no" in settings["forced_identifiers"]
    assert "patient_no" not in settings["forced_decimal_commas"] + settings["forced_measurements"]
    written = shown + out + err + "".join(
        (folder / name).read_text(encoding="utf-8")
        for name in ("visits-profile.json", "visits-profile.txt", "visits-questions.json")
    )
    assert [one for one in sorted(ids) if one in written] == []

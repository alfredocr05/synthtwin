"""Lane Q-FLOW, step 1: the keyboard's broken default path and three plain defects of its rounds.

DEFECT 1 (the question review's section 8, a broken default path). A
first-time person who answered every question at the keyboard got no twin:
the round after the files -- the first of the run to publish between
columns once the subject or person question was answered -- differed from
the description the run's own first round had recorded seconds before, and
the record of earlier descriptions refused it in words that ask for
--replace-description (measured on the review's invented cohort and
operating-room tables at 20,000 rows). Under the owner's ruling of
2026-11-18 the description never leaves the protected computer; a later
round of one run is now judged against the ledger as the run found it
(`cli._ledger_as_the_run_found_it`), so it is never refused for differing
from the run's own earlier round, and a description an earlier RUN wrote is
judged exactly as before (plan P4-D512's typed remedy on answered rounds
stays what a command of its own needs).

DEFECT 2. A column answered at a prompt came back in a later round as a
checklist question (`crp`: Safe Harbor `no`, then measurement, code or
record number). The Safe Harbor answer settles it; a Safe Harbor entry is
never left out, and a column put another question first is still asked
(`cli._column_put_already`).

DEFECTS 8 AND 9. The subject question's keys were its whole phrases, and
the column name its own words invite ("write the name of the column that
identifies the person") was refused at the keyboard. Its answers are now
numbered, and a column of the table typed is taken, as the questions file
takes it.

Every table is invented here, at the table floor of 20,000 rows, with
generic names. Each case is red on its mutant, named in its docstring.
"""

from __future__ import annotations

import json
import pathlib
import random

from synthtwin import asking, cli, installation, results

ROWS = 20_000


def _run(argv: "list[str]", ask: "list[str | None] | None" = None) -> "tuple[results.Result, str]":
    """One command in this process, every line it printed joined; ``ask`` the lines typed, None nobody."""
    screen: "list[tuple[str, str]]" = []
    result = cli.run(argv, screen=screen, ask=ask)
    return result, "".join(text for _stream, text in screen)


def _two_columns(folder: pathlib.Path, seed: int) -> pathlib.Path:
    """A group of two labels by turns and a yes-or-no treatment that depends on it: its one question is the subject question."""
    folder.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    table = folder / "cohort.csv"
    lines = ["group,treated"]
    for row in range(ROWS):
        group = "A" if row % 2 == 0 else "B"
        lines += [f"{group},{1 if rng.random() < (0.7 if group == 'A' else 0.3) else 0}"]
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return table


def _lab(folder: pathlib.Path, seed: int) -> pathlib.Path:
    """The two columns above beside a laboratory value of 0 to 240 that the age rule reads (some above 89): a Safe Harbor question, then a checklist one."""
    folder.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    table = folder / "lab.csv"
    lines = ["group,treated,crp"]
    for row in range(ROWS):
        group = "A" if row % 2 == 0 else "B"
        treated = 1 if rng.random() < (0.7 if group == "A" else 0.3) else 0
        crp = min(240.0, rng.expovariate(1 / 12.0))
        lines += [f"{group},{treated},{crp:.1f}"]
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return table


def _document(path: pathlib.Path) -> "dict[str, object]":
    found = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(found, dict)
    return found


def _publishes_between(description: pathlib.Path) -> bool:
    relationships = _document(description)["relationships"]
    assert isinstance(relationships, dict)
    return relationships["statistical"] is not None


def _subject_answer(questions: pathlib.Path) -> str:
    chained = _document(questions)[asking.BETWEEN_COLUMNS]
    assert isinstance(chained, dict)
    entry = chained[asking.ROWS_PER_PERSON]
    assert isinstance(entry, dict)
    return f"{entry['your_answer']}"


# -- DEFECT 1 ------------------------------------------------------------------


def test_a_first_run_answered_at_the_keyboard_is_not_refused_by_its_own_description(tmp_path: pathlib.Path) -> None:
    """The subject question answered in the round after the files: the run finishes and publishes between columns.

    MUTANT: `_ledger_as_the_run_found_it` returning the ledger as it stands
    (the run's own first entry in it) -- the round is refused again.
    """
    table = _two_columns(tmp_path / "t", 7)
    questions = table.parent / "cohort-questions.json"
    result, said = _run(["profile", f"{table}"], ask=["1", None])
    assert "(1 of 1 in this round): rows_per_person" in said, said[-2000:]
    assert installation.words_changed("cohort") not in said, said[-2000:]
    assert result.verdict == results.NO_MISS, said[-2000:]
    assert _subject_answer(questions) == asking.ANSWER_ONE_ROW_EACH
    assert _publishes_between(table.parent / "cohort-profile.json")


def test_a_first_twin_answered_at_the_keyboard_is_built(tmp_path: pathlib.Path) -> None:
    """The same through `synthtwin twin`, the command the person runs: the twin and its two reports are written (Enter at the one round's last screen, lane Q-FLOW's step 2)."""
    table = _two_columns(tmp_path / "w", 9)
    result, said = _run(["twin", f"{table}"], ask=["1", "", None])
    folder = table.parent / "cohort-synthtwin"
    assert installation.words_changed("cohort") not in said, said[-2000:]
    assert result.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    assert (folder / "cohort-twin.csv").is_file()
    assert _publishes_between(folder / "cohort-profile.json")


def test_a_description_an_earlier_run_wrote_is_still_judged_as_before(tmp_path: pathlib.Path) -> None:
    """Nobody at the keyboard first, then a keyboard run whose answered round differs from that earlier run's description: refused, answer kept.

    The strict reading for a description of an earlier RUN stands (plan
    P4-D512, Codex's review of batch 4u, item 7), and its remedy works.
    MUTANT: `_ledger_as_the_run_found_it` leaving out the table's entry
    even where one stood before the run -- the round is not refused.
    """
    table = _two_columns(tmp_path / "e", 5)
    questions = table.parent / "cohort-questions.json"
    first, said = _run(["profile", f"{table}"])
    assert first.verdict == results.NO_MISS, said[-1500:]
    second, said = _run(["profile", f"{table}", "--replace"], ask=["1", None])
    assert second.verdict == results.REFUSED, said[-2000:]
    assert "run again with --replace-description" in said
    assert _subject_answer(questions) == asking.ANSWER_ONE_ROW_EACH
    assert not _publishes_between(table.parent / "cohort-profile.json")
    third, said = _run(["profile", f"{table}", "--answers", f"{questions}", "--replace-description"])
    assert third.verdict == results.NO_MISS, said[-1500:]
    assert _publishes_between(table.parent / "cohort-profile.json")


# -- DEFECT 2 ------------------------------------------------------------------


def test_a_column_answered_at_a_prompt_is_not_put_again_in_a_later_round(tmp_path: pathlib.Path) -> None:
    """`crp` answered `no` at its Safe Harbor question is not put again as a checklist question; its reading stays a measurement.

    MUTANT: `_column_put_already` answering False -- 'crp' is put twice.
    """
    table = _lab(tmp_path / "l", 3)
    result, said = _run(["profile", f"{table}"], ask=["no", "1", None])
    assert result.verdict == results.NO_MISS, said[-2000:]
    assert said.count("): 'crp'") == 1, said[-3000:]
    described = _document(table.parent / "lab-profile.json")
    columns = described["columns"]
    assert isinstance(columns, list)
    crp = [one for one in columns if isinstance(one, dict) and one.get("name") == "crp"][0]
    assert crp["role"] in ("continuous", "discrete"), crp["role"]


def test_a_safe_harbor_entry_is_never_left_out_for_an_earlier_answer(tmp_path: pathlib.Path) -> None:
    """The rule leaves out only a checklist entry after a Safe Harbor question: every Safe Harbor entry is kept, and so is a checklist entry after any other question."""
    session = cli._Session(None, None)
    cli._OPEN.sessions += [session]
    try:
        session.put = [("crp", "continuous", asking.BECAUSE_SAFE_HARBOR_AGES)]
        for reason in asking.SAFE_HARBOR_REASONS + asking.SH2_SAFE_HARBOR_REASONS:
            record = results.Asked("asked", 1, "crp", "continuous", reason, "", "", (), False, "crp")
            assert not cli._column_put_already(record), reason
        checklist = results.Asked(results.SECTION_CHECKLIST, 1, "crp", "continuous", "listed", "", "", (), False, "crp")
        assert cli._column_put_already(checklist)
        other = results.Asked(results.SECTION_CHECKLIST, 2, "sbp", "continuous", "listed", "", "", (), False, "sbp")
        assert not cli._column_put_already(other)
        # ...and a column put another question first (the person question's
        # `not a person`) is still asked whether it holds record numbers.
        session.put += [("staff_no", "continuous", asking.BECAUSE_REPEATS_AND_MANY)]
        staff = results.Asked(results.SECTION_CHECKLIST, 3, "staff_no", "continuous", "listed", "", "", (), False, "staff_no")
        assert not cli._column_put_already(staff)
    finally:
        del cli._OPEN.sessions[len(cli._OPEN.sessions) - 1]


# -- DEFECTS 8 AND 9 -------------------------------------------------------------


def _subject_record() -> results.Asked:
    """The subject question as the round after the files puts it (`cli._subject_entry_now`'s record)."""
    offers = tuple(
        results.Offer(answer, means, publishes)
        for answer, means, publishes in asking.ROWS_PER_PERSON_ANSWERS
        if answer in (asking.ANSWER_ONE_ROW_EACH, asking.ANSWER_NO_PERSON_COLUMN)
    )
    return results.Asked(
        asking.BETWEEN_COLUMNS, 1, "", "", asking.ROWS_PER_PERSON,
        f"{asking.ROWS_PER_PERSON_SEEN} {asking.ROWS_PER_PERSON_QUESTION}",
        asking.ROWS_PER_PERSON_STANDING, offers, False, asking.ROWS_PER_PERSON,
    )


def _put_with(typed: "list[str | None]", columns: "tuple[str, ...]") -> "tuple[list[tuple[results.Asked, str]], str]":
    """The subject question put once at a stand-in keyboard, the table's columns on the session; what was read and the screen."""
    screen: "list[tuple[str, str]]" = []
    session = cli._Session(screen, typed)
    session.subject_columns = columns
    cli._OPEN.sessions += [session]
    try:
        given, ended = cli._put_the_entries([_subject_record()])
    finally:
        del cli._OPEN.sessions[len(cli._OPEN.sessions) - 1]
    assert not ended
    return given, "".join(text for _stream, text in screen)


def test_the_subject_question_takes_a_column_name_typed_and_numbers_its_answers() -> None:
    """[1] and [2] are its keys, each phrase is still taken, and a column of the table typed (any capitals) is the answer; another word is Enter.

    MUTANT: the column names left out of the answers the entry takes at
    the keyboard -- `subject_ref` is read as Enter and the question stays open.
    """
    columns = ("subject_ref", "group", "treated")
    given, said = _put_with(["Subject_Ref"], columns)
    assert [answer for _record, answer in given] == ["subject_ref"], said
    assert "[1] every row describes a different person" in said
    assert "[2] one person may have several rows" in said
    assert "Or type the name of the column that identifies the person" in said
    given, _said = _put_with(["1"], columns)
    assert [answer for _record, answer in given] == [asking.ANSWER_ONE_ROW_EACH]
    given, _said = _put_with(["2"], columns)
    assert [answer for _record, answer in given] == [asking.ANSWER_NO_PERSON_COLUMN]
    given, _said = _put_with([asking.ANSWER_ONE_ROW_EACH], columns)
    assert [answer for _record, answer in given] == [asking.ANSWER_ONE_ROW_EACH]
    given, _said = _put_with([""], columns)
    assert [answer for _record, answer in given] == [cli._LEFT_OPEN]
    given, said = _put_with(["visit_no", ""], columns)
    assert [answer for _record, answer in given] == [cli._LEFT_OPEN]
    assert "Please type one of the answers offered" in said

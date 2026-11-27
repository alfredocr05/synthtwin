"""The keyboard's rounds after the outside review of batch 4u, items 6 and 7: the subject question put, and answers a refused round keeps.

ITEM 6. The subject question -- may one person stand on more than one row
of the table (plan P4-D449)? -- is written under the chain's one entry of
the questions file, `between_columns`, and no record of the profile's
result stands for it. On a table whose only question it is (20,000 rows
of two ordinary yes-or-no columns), the rounds at the keyboard had nothing
to put, the run ended with no relationship between columns published, and
a plain-text answers file had no line for it: a person could turn the
relationships on only by editing the nested file by hand. Now the round
after the files puts it, once a run, in a round of its own after the
file's other entries (so ending input there loses no answer given to
them), offering its two answers that name no column; and a text line
`rows_per_person = <answer>` answers it.

ITEM 7. A later round's description that the record of earlier
descriptions refuses -- the table described before, and this description
a different one where either publishes something between columns -- had
its answers taken out of the questions file again, and the command the
run taught to answer again lacked --replace-description, which the
refusal's own words ask for. Now the description and its summary stand
as they were, the answers given since stay in the questions file, and the
command shown types the person's own options, `--name` and
`--private-folder` where typed, and --replace-description: run, it
describes the table with those answers. Since lane Q-FLOW's step 1 a later
round is judged against the ledger as the run found it, so the refusal
these cases read is of a description an EARLIER RUN wrote; a run's own
first round no longer refuses its later ones.

Every table is invented here, at the table floor of 20,000 rows, with
generic names; each case is red on the merged line's head before the fix
(3d534e76) and on its mutant.
"""

from __future__ import annotations

import json
import pathlib
import random

import pytest

import keyboard_answers_measures as measures
from synthtwin import asking, cli, contract, errors, results

ROWS = 20_000


def _run(argv: "list[str]", ask: "list[str | None] | None" = None) -> "tuple[results.Result, str]":
    """One command in this process, every line it printed joined; `ask` the lines typed, None nobody."""
    screen: "list[tuple[str, str]]" = []
    result = cli.run(argv, screen=screen, ask=ask)
    return result, "".join(text for _stream, text in screen)


def _two_columns(folder: pathlib.Path, seed: int) -> pathlib.Path:
    """The review's table: a group of two labels by turns and a yes-or-no treatment that depends on it."""
    folder.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    table = folder / "cohort.csv"
    lines = ["group,treated"]
    for row in range(ROWS):
        group = "A" if row % 2 == 0 else "B"
        lines += [f"{group},{1 if rng.random() < (0.7 if group == 'A' else 0.3) else 0}"]
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return table


def _drawn_labels(folder: pathlib.Path, seed: int) -> pathlib.Path:
    """Two to four label columns of two to six levels each, the later ones drawn partly from the first: no key, no number."""
    folder.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    columns = rng.randint(2, 4)
    levels = [rng.randint(2, 6) for _column in range(columns)]
    names = ["colour", "grade", "region", "season"][:columns]
    words = (
        ("red", "green", "blue", "amber", "grey", "violet"),
        ("low", "middle", "high", "very high", "none", "some"),
        ("north", "south", "east", "west", "centre", "coast"),
        ("spring", "summer", "autumn", "winter", "wet", "dry"),
    )
    lines = [",".join(names)]
    for _row in range(ROWS):
        first = rng.randrange(levels[0])
        cells = [words[0][first]]
        for place in range(1, columns):
            drawn = first % levels[place] if rng.random() < 0.6 else rng.randrange(levels[place])
            cells += [words[place][drawn]]
        lines += [",".join(cells)]
    table = folder / "drawn.csv"
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return table


def _visits(folder: pathlib.Path, seed: int, dated: int = 1, codes: int = 900) -> pathlib.Path:
    """The review's item 7 table: a person number on every row, a code of ``codes`` values, two yes-or-no columns, and costs that read as dates."""
    folder.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    names = ["pid", "amount", "flag_a", "flag_b"] + [f"cost_{place}" if place else "cost" for place in range(dated)]
    spans = [rng.randint(300, 700) for _place in range(dated)]
    lines = [",".join(names)]
    for row in range(ROWS):
        flag_a = 1 if rng.random() < 0.4 else 0
        flag_b = 1 if rng.random() < (0.6 if flag_a else 0.3) else 0
        cells = [f"P{row + 1:06d}", f"{rng.randint(100, 99 + codes)}", f"{flag_a}", f"{flag_b}"]
        cells += [f"{45000 + (row % span) / 10:.1f}" for span in spans]
        lines += [",".join(cells)]
    table = folder / "visits.csv"
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return table


def _document(path: pathlib.Path) -> "dict[str, object]":
    found = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(found, dict)
    return found


def _subject_answer(questions: pathlib.Path) -> str:
    """The subject question's answer as the questions file holds it ('' unanswered)."""
    chained = _document(questions)[asking.BETWEEN_COLUMNS]
    assert isinstance(chained, dict)
    entry = chained[asking.ROWS_PER_PERSON]
    assert isinstance(entry, dict)
    return f"{entry['your_answer']}"


def _publishes_between(description: pathlib.Path) -> bool:
    relationships = _document(description)["relationships"]
    assert isinstance(relationships, dict)
    return relationships["statistical"] is not None


def _answer_of(questions: pathlib.Path, column: str) -> "tuple[str, str]":
    """A column's answer in the questions file: (section, answer), the open question first, then the kept answers."""
    document = _document(questions)
    for section in ("asked", "answered_before"):
        entries = document[section] if section in document else []
        assert isinstance(entries, list)
        for entry in entries:
            if isinstance(entry, dict) and entry.get("column") == column and f"{entry.get('your_answer') or ''}":
                return section, f"{entry['your_answer']}"
    return "", ""


_KEPT_LEAD = "run this to describe the table with them:\n  "


def _taught(said: str) -> "list[str]":
    """The command a refused later round teaches, as words after `synthtwin`."""
    assert _KEPT_LEAD in said, said[-1500:]
    line = said[said.index(_KEPT_LEAD) + len(_KEPT_LEAD):].split("\n")[0]
    words = measures.shell_words(line)
    assert words[:2] == ["synthtwin", "profile"], line
    return words[1:]


# -- ITEM 6: the subject question --------------------------------------------


def test_the_subject_question_alone_is_put_at_the_keyboard_and_the_taught_run_applies_it(
    tmp_path: pathlib.Path,
) -> None:
    """The review's table: the only question is put, its answer stays in the file, and the run taught publishes between columns."""
    table = _two_columns(tmp_path / "t", 7)
    questions = table.parent / "cohort-questions.json"
    result, said = _run(["profile", f"{table}"], ask=[asking.ANSWER_ONE_ROW_EACH, None])
    assert "(1 of 1 in this round): rows_per_person" in said, said[-2000:]
    assert said.count("): rows_per_person") == 1
    assert _subject_answer(questions) == asking.ANSWER_ONE_ROW_EACH
    # The round's description is the first to publish between columns. The
    # record no longer refuses it for differing from the description this
    # same run wrote a round before (lane Q-FLOW, step 1: the run is judged
    # against the ledger as it found it), so the run ends publishing them.
    assert result.verdict == results.NO_MISS, said[-2000:]
    assert _publishes_between(table.parent / "cohort-profile.json")
    assert _subject_answer(questions) == asking.ANSWER_ONE_ROW_EACH


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_drawn_tables_whose_one_question_is_the_subject_question(tmp_path: pathlib.Path, seed: int) -> None:
    """Two to four drawn label columns: the subject question is put once, either answer is kept, and each answer does what it offers."""
    table = _drawn_labels(tmp_path / f"d{seed}", seed)
    questions = table.parent / "drawn-questions.json"
    described = table.parent / "drawn-profile.json"
    answer = random.Random(seed * 31).choice([asking.ANSWER_ONE_ROW_EACH, asking.ANSWER_NO_PERSON_COLUMN])
    result, said = _run(["profile", f"{table}"], ask=[answer, None])
    assert said.count("): rows_per_person") == 1, said[-2000:]
    assert _subject_answer(questions) == answer
    if answer == asking.ANSWER_NO_PERSON_COLUMN:
        # Nothing is published between columns either way: the record
        # takes the round, and the run ends with the answer standing.
        assert result.verdict == results.NO_MISS, said[-1500:]
        assert not _publishes_between(described)
        return
    # ...and the round that publishes between columns is not refused for
    # differing from the run's own first round (lane Q-FLOW, step 1).
    assert result.verdict == results.NO_MISS, said[-1500:]
    assert _publishes_between(described)


def test_an_entry_left_open_does_not_keep_the_subject_question_from_its_round(tmp_path: pathlib.Path) -> None:
    """A cost column whose values read as dates beside the review's two columns: its question left open with Enter, the subject question follows in a round of its own."""
    folder = tmp_path / "e"
    folder.mkdir(parents=True)
    rng = random.Random(13)
    lines = ["group,treated,cost"]
    for row in range(ROWS):
        group = "A" if row % 2 == 0 else "B"
        treated = 1 if rng.random() < (0.7 if group == "A" else 0.3) else 0
        lines += [f"{group},{treated},{45000 + (row % 500) / 10:.1f}"]
    table = folder / "cohort.csv"
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    questions = folder / "cohort-questions.json"
    result, said = _run(["profile", f"{table}"], ask=["", asking.ANSWER_ONE_ROW_EACH, None])
    assert "'cost'" in said and "(1 of 1 in this round): rows_per_person" in said, said[-2500:]
    assert said.index("'cost'") < said.index("(1 of 1 in this round): rows_per_person")
    assert _subject_answer(questions) == asking.ANSWER_ONE_ROW_EACH
    assert _answer_of(questions, "cost") == ("", "")
    assert result.verdict == results.NO_MISS, said[-2500:]
    assert _publishes_between(folder / "cohort-profile.json")


def test_a_text_answers_file_answers_the_subject_question(tmp_path: pathlib.Path) -> None:
    """`rows_per_person = One Row Each` in a text file answers it, whatever its capitals; a second line about it is refused."""
    table = _two_columns(tmp_path / "x", 5)
    questions = table.parent / "cohort-questions.json"
    first, said = _run(["profile", f"{table}"])
    assert first.verdict == results.NO_MISS, said[-1500:]
    assert _subject_answer(questions) == ""
    text = tmp_path / "answers.txt"
    text.write_text("# the subject question\nrows_per_person = One Row Each\n", encoding="utf-8", newline="\n")
    second, said = _run(["profile", f"{table}", "--answers", f"{text}", "--replace-description"])
    assert second.verdict == results.NO_MISS, said[-1500:]
    assert _subject_answer(questions) == asking.ANSWER_ONE_ROW_EACH
    assert _publishes_between(table.parent / "cohort-profile.json")
    twice = tmp_path / "twice.txt"
    twice.write_text(
        f"rows_per_person = {asking.ANSWER_ONE_ROW_EACH}\nrows_per_person = {asking.ANSWER_NO_PERSON_COLUMN}\n",
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_answers(f"{twice}", f"{questions}")
    assert "rows_per_person" in f"{refused.value}" and "line 1" in f"{refused.value}"


def test_the_contract_mirrors_the_subject_question_words() -> None:
    """The contract reads the subject question by the asking module's own words, mirrored (it imports nothing that reaches the reader)."""
    assert contract._BETWEEN_COLUMNS == asking.BETWEEN_COLUMNS
    assert contract._ROWS_PER_PERSON == asking.ROWS_PER_PERSON
    assert contract._ROWS_PER_PERSON_WORDS == (asking.ANSWER_ONE_ROW_EACH, asking.ANSWER_NO_PERSON_COLUMN)
    offered = [answer for answer, _means, _publishes in asking.ROWS_PER_PERSON_ANSWERS]
    assert [one for one in offered if one in contract._ROWS_PER_PERSON_WORDS] == list(contract._ROWS_PER_PERSON_WORDS)


# -- ITEM 7: the answers a refused later round keeps ----------------------------


def test_a_refused_later_round_keeps_its_answers_and_teaches_the_run_that_applies_them(tmp_path: pathlib.Path) -> None:
    """The review's table: `no` to the cost's dates is kept after the record's refusal, and the command shown applies it."""
    table = _visits(tmp_path / "v", 11)
    questions = table.parent / "visits-questions.json"
    # The table was described before, by a run of its own with nobody at the
    # keyboard: a later round of this run that differs from THAT description
    # is refused as before (lane Q-FLOW, step 1, keeps the strict reading for
    # an earlier run's description).
    earlier, said = _run(["profile", f"{table}", "--person", "pid", "--code", "amount"])
    assert earlier.verdict == results.NO_MISS, said[-1500:]
    result, said = _run(["profile", f"{table}", "--person", "pid", "--code", "amount", "--replace"], ask=["", "no", None])
    assert result.verdict == results.REFUSED
    assert "run again with --replace-description" in said
    assert _answer_of(questions, "cost") == ("asked", "no")
    words = _taught(said)
    assert words.count("--replace-description") == 1
    assert "--answers" in words and "--person" in words and "--code" in words
    again, said_again = _run(words)
    assert again.verdict == results.NO_MISS, said_again[-1500:]
    assert _answer_of(questions, "cost") == ("answered_before", "no")


@pytest.mark.parametrize("seed", [3, 4])
def test_drawn_tables_keep_every_answer_and_the_typed_name_after_the_refusal(tmp_path: pathlib.Path, seed: int) -> None:
    """One or two columns of costs read as dates, each answered `no`, a typed `--name` on one seed: kept, taught and applied."""
    rng = random.Random(seed)
    dated = rng.randint(1, 2)
    table = _visits(tmp_path / f"g{seed}", seed, dated, codes=100)
    questions = table.parent / "visits-questions.json"
    named = ["--name", f"visits_{seed}"] if seed % 2 == 0 else []
    costs = [f"cost_{place}" if place else "cost" for place in range(dated)]
    # ...described before by a run of its own (lane Q-FLOW, step 1).
    earlier, said = _run(["profile", f"{table}", "--person", "pid", "--code", "amount"] + named)
    assert earlier.verdict == results.NO_MISS, said[-1500:]
    result, said = _run(
        ["profile", f"{table}", "--person", "pid", "--code", "amount", "--replace"] + named,
        ask=["no"] * dated + [None],
    )
    assert result.verdict == results.REFUSED, said[-1500:]
    for column in costs:
        assert _answer_of(questions, column) == ("asked", "no"), column
    words = _taught(said)
    assert words[-1] == "--replace-description"
    if named:
        assert words[words.index("--name") + 1] == named[1]
    again, said_again = _run(words)
    assert again.verdict == results.NO_MISS, said_again[-1500:]
    for column in costs:
        assert _answer_of(questions, column) == ("answered_before", "no"), column


@pytest.mark.parametrize("windows", [True, False])
def test_a_taught_line_splits_back_into_its_words_as_its_shell_reads_it(windows: bool) -> None:
    """The splitter these cases read a taught line with gives back every word the product quoted, for PowerShell and for POSIX.

    GitHub's Windows runs of push 24 split such a line with `shlex`'s POSIX
    reading, which took a bare path's backslashes as escapes, so four cases
    of tests/test_keyboard_answers.py ran a command on another file. MUTANT:
    the POSIX reading on Windows (the PowerShell case is red).
    """
    words = [
        "C:\\Users\\runneradmin\\AppData\\Local\\Temp\\pytest-0\\stays-questions.json",
        "C:\\Users\\x y\\it's\\visits.csv",
        "--answers",
        "plain_word",
        "Visit & time",
        "--missing-value=-1.5",
    ]
    line = " ".join(cli._quoted_for_the_shell(word, windows=windows) for word in words)
    assert measures.shell_words(line, windows=windows) == words

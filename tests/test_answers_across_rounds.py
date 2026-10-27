"""The questions file keeps every answer across rounds (lane AQ, plan P4-D408).

THE FINDING (lane E0a, plan P4-D399, measured on 68dae22f). A person who
answers the questions file in two rounds lost the first round's answers:
the file the first `--answers` run wrote carried only the questions still
open, so a column answered in round one was unanswered after round two.
`us_vitals`' patient column, answered as the person in round one, read
as an affixed number after round two; `diagnoses_procedures` lost its
encounter key and a SNOMED code answer. Lane HX's P4-D401 (fa89ed59)
kept the answers to questions offering `identifier`; every other answer
-- a 12-hour clock, a column of dates, codes standing for a missing date,
a century, the order of day and month, the delimiter, the row of the
names, and every declaration typed on the command line -- was still
lost, and the refusal of a file answer beside column answers asked for
two runs whose second lost the first's answer.

THE RULE. The file every run writes carries, under `answered_before`,
every answer that run acted on, written from the declarations and not
from the questions each answered; an answer stands until a later one --
in the file, in that section, or typed -- replaces it; and a run that
would drop one refuses in plain words. So the same answers given in one
round or in several write the same description, summary, questions file
and twin, byte for byte. These tests prove it on E0a's two cases at 600
rows, on a table raising nine kinds of question over three rounds, on a
later answer changing an earlier one, on the refusal's two runs, and
with each of the three mutants the rule exists against.
"""

from __future__ import annotations

import contextlib
import dataclasses
import io
import json
import pathlib
import random
import re
from typing import Callable

import pytest

import fixtures
import health_zoo as zoo
from synthtwin import asking, cli, date_counts, results

ROWS = 600
SEED = 20261016

# The command-line option each answer is typed as, where one exists.
_TYPED_FLAGS = {
    asking.ANSWER_CODE: "--code",
    asking.ANSWER_IDENTIFIER: "--identifier",
    asking.ANSWER_MEASUREMENT: "--measurement",
    asking.ANSWER_JOINED: "--measurement",
    asking.ANSWER_DECIMAL_COMMA: "--decimal-comma",
    asking.ANSWER_TWELVE_HOUR: "--twelve-hour",
    asking.ANSWER_DATES: "--date-column",
}


def run(arguments: "list[str]") -> int:
    """One synthtwin command in this process, its screen swallowed."""
    with contextlib.redirect_stdout(io.StringIO()) as said:
        with contextlib.redirect_stderr(said):
            return cli.main(arguments)


def typed_form(column: str, answer: str) -> "list[str] | None":
    """The options that type `answer` for `column`, or None where none does."""
    if answer in _TYPED_FLAGS:
        return [_TYPED_FLAGS[answer], column]
    if answer in asking.CENTURY_ANSWERS:
        return ["--century", f"{column}={asking.CENTURY_ANSWERS[answer]}"]
    if answer in zoo_members():
        return ["--date-count", column, answer]
    if column == asking.DAY_FIRST_SUBJECT and answer == asking.ANSWER_DAY_FIRST:
        return ["--day-first"]
    if column == asking.DELIMITER_SUBJECT and answer in asking.ANSWER_DELIMITERS:
        return ["--delimiter", asking.ANSWER_DELIMITERS[answer]]
    if column == asking.FIRST_ROW_SUBJECT:
        if answer == asking.ANSWER_FIRST_ROW_NAMES:
            return ["--first-row", "names"]
        if answer == asking.ANSWER_FIRST_ROW_DATA:
            return ["--first-row", "data"]
    return None


def zoo_members() -> "tuple[str, ...]":
    from synthtwin import date_counts

    return date_counts.MEMBERS


def entries(document: "dict[str, object]") -> "list[dict[str, object]]":
    """The entries a person answers: the file's, the asked and the checklist."""
    found: "list[dict[str, object]]" = []
    for key in ("about_your_file", "asked"):
        section = document.get(key) or []
        assert isinstance(section, list)
        found += [entry for entry in section if isinstance(entry, dict)]
    checklist = document.get("checklist") or {}
    assert isinstance(checklist, dict)
    found += [entry for entry in checklist.get("columns") or [] if isinstance(entry, dict)]
    return found


def offered(entry: "dict[str, object]") -> "tuple[str, ...]":
    choices = entry["answers_you_can_give"]
    assert isinstance(choices, list)
    return tuple(f"{choice['answer']}" for choice in choices)


# The section's key, written out so this module measures the tree before
# plan P4-D408 as well (the lane's reproduction runs it there).
ANSWERED_BEFORE = "answered_before"
# The families of question an answer belongs to, as plan P4-D408 groups
# them: `keep` belongs to the question that offered it. How a column's
# numbers are written is a family of its own beside what the column
# holds (the third round; Codex's review of lane AQ, item 1), so the
# legal pair `measurement` and `decimal_comma` stands as two answers.
_FAMILIES = (
    ("kind", (asking.ANSWER_CODE, asking.ANSWER_IDENTIFIER, asking.ANSWER_MEASUREMENT, asking.ANSWER_JOINED)),
    ("grammar", (asking.ANSWER_DECIMAL_COMMA,)),
    ("clock", (asking.ANSWER_TWELVE_HOUR,)),
    ("date-codes", (asking.ANSWER_NO_DATE, asking.ANSWER_REAL_VALUE)),
    ("century", (asking.ANSWER_CENTURY_POSIX,) + tuple(asking.CENTURY_ANSWERS)),
    ("dates", (asking.ANSWER_DATES,)),
    ("first-row", (asking.ANSWER_FIRST_ROW_NAMES, asking.ANSWER_FIRST_ROW_DATA)),
    ("metadata", (asking.ANSWER_DATA, asking.ANSWER_METADATA_ROWS)),
    ("delimiter", tuple(asking.ANSWER_DELIMITERS)),
    ("day-order", (asking.ANSWER_DAY_FIRST, asking.ANSWER_MONTH_FIRST)),
)


def family(answer: str, choices: "tuple[str, ...]") -> str:
    """The family of question an answer answers, as plan P4-D408 groups them."""
    if answer == asking.ANSWER_KEEP:
        if asking.ANSWER_IDENTIFIER in choices:
            return "kind"
        if asking.ANSWER_DATES in choices:
            return "dates"
        return ""
    for name, words in _FAMILIES:
        if answer in words:
            return name
    return "counted" if answer in zoo_members() else ""


def give(
    document: "dict[str, object]", wanted: "list[tuple[str, str]]"
) -> "list[tuple[str, str, str]]":
    """Write each wanted answer beside the first entry about its column offering it.

    Returns `(column, answer, family)` for each written.
    """
    written: "list[tuple[str, str, str]]" = []
    left = list(wanted)
    for entry in entries(document):
        name = f"{entry['column']}"
        for one in left:
            if one[0] == name and one[1] in offered(entry):
                entry["your_answer"] = one[1]
                written += [(name, one[1], family(one[1], offered(entry)))]
                left = [other for other in left if other != one]
                break
    return written


@dataclasses.dataclass
class Table:
    """A table on disk, and the stem its files are written under."""

    source: pathlib.Path
    stem: str

    @property
    def folder(self) -> pathlib.Path:
        return self.source.parent

    def path(self, ending: str) -> pathlib.Path:
        return self.folder / f"{self.stem}-{ending}"


def profile(table: Table, *options: str) -> int:
    return run(["profile", f"{table.source}", "--replace"] + list(options))


def questions(table: Table) -> "dict[str, object]":
    document = json.loads(table.path("questions.json").read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    return document


def hand_back(table: Table, document: "dict[str, object]") -> pathlib.Path:
    """The answered file, written where the person keeps it: over the questions file."""
    return fixtures.write(table.folder, f"{table.stem}-questions.json", json.dumps(document, indent=1))


def written(table: Table) -> "tuple[dict[str, bytes], int]":
    """The description, the summary, the questions file and the twin at seed 0, as bytes, and generation's exit.

    The twin is the file generation wrote, and only that: where none was
    written it is left out of the mapping, so no exit code ever stands in
    for a twin (Codex's review of lane AQ, item 5: two refusals compared
    as `exit 2` against `exit 2` counted as one twin written alike).
    """
    found = {
        "description": table.path("profile.json").read_bytes(),
        "summary": table.path("profile.txt").read_bytes(),
        "questions": table.path("questions.json").read_bytes(),
    }
    twin = table.folder / f"{table.stem}-twin{table.source.suffix}"
    if twin.exists():
        twin.unlink()
    code = run(["generate", f"{table.path('profile.json')}", "--replace", "--seed", "0"])
    if twin.is_file():
        found["twin"] = twin.read_bytes()
    return found, code


def outputs(table: Table) -> "dict[str, bytes]":
    """`written`'s four files, the twin required: generation exits 0 and writes it."""
    found, code = written(table)
    assert code == 0 and "twin" in found, code
    return found


@dataclasses.dataclass
class Judged:
    """One table's two routes set side by side (K-S3-66)."""

    differing: int
    refused_on_both: bool
    failed: bool


def judged(several: "tuple[dict[str, bytes], int]", once: "tuple[dict[str, bytes], int]") -> Judged:
    """The files the rounds and the one round wrote, compared; a refusal is never a twin.

    A route whose generation exits 0 and writes no twin failed. Where
    both routes refuse, the refusal is counted apart, the other three
    files are compared, and refusals of different codes differ. Where one
    route alone writes a twin, the twin differs. Only two twins written
    are compared byte for byte.
    """
    (first, first_code), (second, second_code) = several, once
    if (first_code == 0 and "twin" not in first) or (second_code == 0 and "twin" not in second):
        return Judged(0, False, True)
    names = ("description", "summary", "questions")
    differing = sum(1 for name in names if first[name] != second[name])
    if "twin" in first and "twin" in second:
        return Judged(differing + (first["twin"] != second["twin"]), False, False)
    if "twin" not in first and "twin" not in second:
        return Judged(differing + (first_code != second_code), True, False)
    return Judged(differing + 1, False, False)


def clear(table: Table) -> None:
    """Every file a run left beside the table, so the next starts from the table alone."""
    for one in table.folder.iterdir():
        if one != table.source:
            one.unlink()


def kept(table: Table) -> "dict[tuple[str, str], bool]":
    """`(column, answer)` for each answer the last file written keeps."""
    found: "dict[tuple[str, str], bool]" = {}
    for entry in questions(table).get(ANSWERED_BEFORE) or []:
        assert isinstance(entry, dict)
        found[(f"{entry['column']}", f"{entry['your_answer']}")] = True
    return found


def said(answer: str) -> str:
    """An answer as the section keeps it: `joined` is the measurement it declares."""
    return asking.ANSWER_MEASUREMENT if answer == asking.ANSWER_JOINED else answer


@dataclasses.dataclass
class Rounds:
    """What answering in rounds did: the exit codes, the answers and what was lost."""

    exits: "list[int]"
    given: "list[list[tuple[str, str, str]]]"
    standing: "dict[tuple[str, str], str]"
    lost: "list[tuple[int, str, str]]"


Answerer = Callable[["dict[str, object]", int], "list[tuple[str, str]]"]


def in_rounds(table: Table, answerer: Answerer, typed: "list[list[str]] | None" = None) -> Rounds:
    """Profile, then answer the file each run writes until nothing new is answered.

    `answerer(document, round)` names the answers to write in that round;
    `typed[round - 1]`, where given, is typed on that round's command
    line. After every round each answer given before, unless a later one
    replaced it, must be kept in the file that round wrote.
    """
    found = Rounds([profile(table)], [], {}, [])
    number = 0
    while True:
        number += 1
        document = questions(table)
        wanted = answerer(document, number)
        flags = typed[number - 1] if typed and number <= len(typed) else []
        given = give(document, wanted)
        fresh = [one for one in given if found.standing.get((one[0], one[2])) != one[1]]
        if not fresh and not flags:
            break
        found.given += [given]
        before = dict(found.standing)
        for name, answer, kind in given:
            found.standing[(name, kind)] = answer
        hand_back(table, document)
        found.exits += [profile(table, "--answers", f"{table.path('questions.json')}", *flags)]
        if found.exits[-1] != 0:
            break
        held = kept(table)
        for (name, kind), answer in before.items():
            if found.standing.get((name, kind)) == answer and (name, said(answer)) not in held:
                found.lost += [(number, name, answer)]
        if number >= 4:
            break
    return found


def in_one_round(table: Table, answers: "dict[tuple[str, str], str]") -> "int | None":
    """Every answer at once: in the first file where it is asked, typed where not.

    A column one of whose answers must be typed has each of its answers
    typed where it can be: an answer in the file to a question deciding
    several families -- the point between thousands decides what the
    column holds and how its numbers are written -- replaces a typed
    declaration of either, as the file is the newer statement (plan
    P4-D408, third round). None where an answer is neither asked in the
    first file nor typeable.
    """
    assert profile(table) == 0
    document = questions(table)
    wanted = [(name, answer) for (name, _kind), answer in answers.items()]
    probe = json.loads(json.dumps(document))
    placed = {(name, answer) for name, answer, _kind in give(probe, wanted)}
    typed_columns = {name for name, answer in wanted if (name, answer) not in placed}
    in_file = [
        (name, answer) for name, answer in wanted if name not in typed_columns or typed_form(name, answer) is None
    ]
    given = give(document, in_file)
    written = {(name, answer) for name, answer, _kind in given}
    flags: "list[str]" = []
    for name, answer in wanted:
        if (name, answer) in written:
            continue
        form = typed_form(name, answer)
        if form is None:
            return None
        flags += form
    hand_back(table, document)
    return profile(table, "--answers", f"{table.path('questions.json')}", *flags)


def compare(
    table: Table, answerer: Answerer, typed: "list[list[str]] | None" = None
) -> "tuple[Rounds, dict[str, bool]]":
    """Answer in rounds, then the same answers in one round; which files differ."""
    rounds = in_rounds(table, answerer, typed)
    assert rounds.exits and all(code == 0 for code in rounds.exits), rounds.exits
    several = outputs(table)
    clear(table)
    code = in_one_round(table, rounds.standing)
    assert code == 0, code
    once = outputs(table)
    return rounds, {name: several[name] != once[name] for name in several}


# -- E0a's two cases ----------------------------------------------------


def zoo_table(folder: pathlib.Path, name: str, rows: int = ROWS) -> "tuple[Table, Answerer]":
    """One catalogue table on disk, and the zoo's own general answerer for it."""
    kind = zoo.table_named(name)
    source = zoo.write_table(kind, folder, rows, SEED)

    def answerer(document: "dict[str, object]", _round: int) -> "list[tuple[str, str]]":
        asked, _general = zoo.answer_generally(kind, document)
        found = [(f"{one['column']}", f"{one['given']}") for one in asked if one["given"]]
        for entry in entries(document):
            entry["your_answer"] = ""
        return found

    return Table(source, kind.name), answerer


def test_us_vitals_person_answered_over_two_rounds_is_one_rounds_twin(tmp_path: pathlib.Path) -> None:
    """E0a's first case: patient_id answered in round one, weight in round two."""
    table, answerer = zoo_table(tmp_path, "us_vitals")
    rounds, differs = compare(table, answerer)
    assert len(rounds.given) == 2
    # Round one also answers `keep` for weight: since lane HX (plan
    # P4-D401) a blank to a question offering `identifier` holds the
    # column, so the zoo's person answers `keep` where it knows the column
    # as something else (batch 4d's integration, 2026-10-20).
    assert [(one[0], one[1]) for one in rounds.given[0]] == [
        ("patient_id", asking.ANSWER_IDENTIFIER),
        ("weight", "keep"),
    ]
    assert [(one[0], one[1]) for one in rounds.given[1]] == [("weight", asking.ANSWER_MEASUREMENT)]
    assert rounds.lost == []
    assert differs == {"description": False, "summary": False, "questions": False, "twin": False}
    described = json.loads(table.path("profile.json").read_text(encoding="utf-8"))
    roles = {f"{block['name']}": f"{block['role']}" for block in described["columns"]}
    assert roles["patient_id"] == "identifier"


def test_diagnoses_keep_the_encounter_key_and_the_snomed_code(tmp_path: pathlib.Path) -> None:
    """E0a's second case: enc_id and the SNOMED code column survive round two."""
    table, answerer = zoo_table(tmp_path, "diagnoses_procedures")
    rounds, differs = compare(table, answerer)
    assert len(rounds.given) == 2
    assert rounds.lost == []
    assert rounds.standing[("enc_id", "kind")] == asking.ANSWER_IDENTIFIER
    assert rounds.standing[("snomed_id", "kind")] == asking.ANSWER_CODE
    assert not any(differs.values()), differs
    held = kept(table)
    assert ("enc_id", asking.ANSWER_IDENTIFIER) in held
    assert ("snomed_id", asking.ANSWER_CODE) in held


# -- nine kinds of question over three rounds ------------------------------

_MIXED = "pid,clock,visit,seen,born,amount,bp,reg,mostly"
_MIXED_ANSWERS = (
    (asking.DAY_FIRST_SUBJECT, asking.ANSWER_DAY_FIRST),
    ("clock", asking.ANSWER_TWELVE_HOUR),
    ("amount", asking.ANSWER_DECIMAL_COMMA),
    ("bp", asking.ANSWER_CODE),
    ("reg", asking.ANSWER_CODE),
    ("pid", asking.ANSWER_IDENTIFIER),
    ("mostly", asking.ANSWER_DATES),
    ("seen", asking.ANSWER_NO_DATE),
    ("born", asking.ANSWER_CENTURY_1930),
)


def mixed_table(folder: pathlib.Path) -> Table:
    """One table whose columns raise nine different questions, seeded.

    A person column, a clock whose hours all lie in 1 to 12, dates whose
    day and month read either way, dates beside a few `UNK`, two-figure
    years, a point between thousands, pressures, a register of codes and
    a column mostly of dates.
    """
    draw = random.Random(7)
    lines = [_MIXED]
    for place in range(ROWS):
        lines += [",".join([
            f"P{draw.randrange(1, 150):05d}",
            f"{draw.randrange(1, 13)}:{draw.randrange(0, 60):02d}",
            f"{draw.randrange(1, 13):02d}/{draw.randrange(1, 13):02d}/20{draw.randrange(10, 24)}",
            "UNK" if place % 40 == 0 else f"2023-{draw.randrange(1, 13):02d}-{draw.randrange(1, 29):02d}",
            f"{draw.randrange(1, 13):02d}/{draw.randrange(1, 29):02d}/{draw.randrange(30, 99)}",
            f"{draw.randrange(1, 99)}.{draw.randrange(0, 1000):03d}",
            f"{draw.randrange(90, 180)}/{draw.randrange(50, 110)}",
            f"{draw.choice([1101, 2202, 3303, 4404, 5505, 6606, 7707, 8808, 9909, 1212, 1313, 1414])}",
            f"2022-{draw.randrange(1, 13):02d}-{draw.randrange(1, 29):02d}" if place % 3 else f"X{draw.randrange(100, 999)}",
        ])]
    folder.mkdir(parents=True, exist_ok=True)
    return Table(fixtures.write(folder, "mixed.csv", "\n".join(lines) + "\n"), "mixed")


def by_round(plan: "list[list[tuple[str, str]]]") -> Answerer:
    """An answerer that gives the plan's answers for each round, and nothing after."""

    def answerer(_document: "dict[str, object]", number: int) -> "list[tuple[str, str]]":
        return list(plan[number - 1]) if number <= len(plan) else []

    return answerer


def test_the_first_file_asks_all_nine(tmp_path: pathlib.Path) -> None:
    """The table's first file offers every answer the cases below give."""
    table = mixed_table(tmp_path)
    assert profile(table) == 0
    document = questions(table)
    for name, answer in _MIXED_ANSWERS:
        assert any(f"{entry['column']}" == name and answer in offered(entry) for entry in entries(document)), name


@pytest.mark.parametrize("cut", [(3, 6), (1, 8), (5, 7)])
def test_three_rounds_write_one_rounds_bytes(tmp_path: pathlib.Path, cut: "tuple[int, int]") -> None:
    """The nine answers given over three rounds, cut at two places, are one round's."""
    table = mixed_table(tmp_path)
    plan = [list(_MIXED_ANSWERS[: cut[0]]), list(_MIXED_ANSWERS[cut[0] : cut[1]]), list(_MIXED_ANSWERS[cut[1] :])]
    rounds, differs = compare(table, by_round(plan))
    assert len(rounds.given) == 3
    assert rounds.lost == []
    assert len(rounds.standing) == len(_MIXED_ANSWERS)
    assert not any(differs.values()), differs


def test_answers_typed_in_round_one_are_kept_by_the_file(tmp_path: pathlib.Path) -> None:
    """Typed in round one, the file alone in round two: nothing typed is lost."""
    table = mixed_table(tmp_path)
    assert profile(table, "--identifier", "pid", "--twelve-hour", "clock", "--day-first") == 0
    held = kept(table)
    assert ("pid", asking.ANSWER_IDENTIFIER) in held
    assert ("clock", asking.ANSWER_TWELVE_HOUR) in held
    assert (asking.DAY_FIRST_SUBJECT, asking.ANSWER_DAY_FIRST) in held
    typed_once = outputs(table)
    document = questions(table)
    hand_back(table, document)
    assert profile(table, "--answers", f"{table.path('questions.json')}") == 0
    assert outputs(table) == typed_once
    held = kept(table)
    assert ("pid", asking.ANSWER_IDENTIFIER) in held
    assert ("clock", asking.ANSWER_TWELVE_HOUR) in held
    assert (asking.DAY_FIRST_SUBJECT, asking.ANSWER_DAY_FIRST) in held


def test_codes_in_dates_read_either_way_answered_after_the_order(tmp_path: pathlib.Path) -> None:
    """The order of day and month in round one, the codes in round two: one round's bytes.

    The question about the codes counts the cells the reading of its
    round reads, and that reading moves with the order; the kept answer
    is kept by the codes' own words, which every round finds alike. Found
    by replaying tests/test_stage3b_date_questions.py's answered runs in
    two rounds: the questions file differed until it was.
    """
    draw = random.Random(11)
    lines = ["seen_at,other"]
    for place in range(ROWS):
        lines += [",".join([
            "UNK" if place % 40 == 0 else f"{draw.randrange(1, 13):02d}/{draw.randrange(1, 13):02d}/20{draw.randrange(10, 24)}",
            "UNK" if place % 40 == 7 else f"2023-{draw.randrange(1, 13):02d}-{draw.randrange(1, 29):02d}",
        ])]
    tmp_path.mkdir(parents=True, exist_ok=True)
    table = Table(fixtures.write(tmp_path, "real.csv", "\n".join(lines) + "\n"), "real")
    plan = [
        [(asking.DAY_FIRST_SUBJECT, asking.ANSWER_DAY_FIRST)],
        [("seen_at", asking.ANSWER_NO_DATE), ("other", asking.ANSWER_NO_DATE)],
    ]
    rounds, differs = compare(table, by_round(plan))
    assert len(rounds.given) == 2 and len(rounds.standing) == 3
    assert rounds.lost == []
    assert not any(differs.values()), differs


# -- a later answer changes an earlier one -------------------------------


def test_a_later_round_changes_an_earlier_answer(tmp_path: pathlib.Path) -> None:
    """Changed in the kept section, and typed: the later answer wins, as if given once.

    `--measurement amount` typed over a kept `decimal_comma` says what
    the column holds and nothing about how its numbers are written, so
    both stand (the third round; Codex's review of lane AQ, item 1);
    `--code clock` typed over a kept `twelve-hour` replaces it, since a
    12-hour clock reaches nothing on a column of codes.
    """
    table = mixed_table(tmp_path)
    assert profile(table) == 0
    first = questions(table)
    give(
        first,
        [
            ("reg", asking.ANSWER_CODE), ("amount", asking.ANSWER_DECIMAL_COMMA), ("pid", asking.ANSWER_IDENTIFIER),
            ("clock", asking.ANSWER_TWELVE_HOUR),
        ],
    )
    hand_back(table, first)
    assert profile(table, "--answers", f"{table.path('questions.json')}") == 0
    second = questions(table)
    for entry in second[ANSWERED_BEFORE]:
        if entry["column"] == "reg":
            entry["your_answer"] = asking.ANSWER_MEASUREMENT
    hand_back(table, second)
    assert profile(table, "--answers", f"{table.path('questions.json')}", "--measurement", "amount", "--code", "clock") == 0
    held = kept(table)
    assert ("reg", asking.ANSWER_MEASUREMENT) in held and ("reg", asking.ANSWER_CODE) not in held
    assert ("amount", asking.ANSWER_MEASUREMENT) in held
    assert ("amount", asking.ANSWER_DECIMAL_COMMA) in held
    assert ("clock", asking.ANSWER_CODE) in held and ("clock", asking.ANSWER_TWELVE_HOUR) not in held
    several = outputs(table)
    clear(table)
    code = in_one_round(
        table,
        {
            ("reg", "kind"): asking.ANSWER_MEASUREMENT,
            ("amount", "kind"): asking.ANSWER_MEASUREMENT,
            ("amount", "grammar"): asking.ANSWER_DECIMAL_COMMA,
            ("pid", "kind"): asking.ANSWER_IDENTIFIER,
            ("clock", "kind"): asking.ANSWER_CODE,
        },
    )
    assert code == 0
    assert outputs(table) == several


def test_a_later_answer_to_the_question_asked_again_wins(tmp_path: pathlib.Path) -> None:
    """Answered again where the next file asks again: the later answer wins, as if given once.

    `keep` for the person column, then `identifier`; a point between
    thousands for `amount`, then `code`, where the file the first
    answering run wrote puts each question again. (`measurement` there
    says what the column holds, and the comma stands beside it: the third
    round.)
    """
    table = mixed_table(tmp_path)
    assert profile(table) == 0
    first = questions(table)
    give(first, [("pid", asking.ANSWER_KEEP), ("amount", asking.ANSWER_DECIMAL_COMMA)])
    hand_back(table, first)
    assert profile(table, "--answers", f"{table.path('questions.json')}") == 0
    assert ("pid", asking.ANSWER_KEEP) in kept(table)
    assert ("amount", asking.ANSWER_DECIMAL_COMMA) in kept(table)
    second = questions(table)
    assert give(second, [("pid", asking.ANSWER_IDENTIFIER), ("amount", asking.ANSWER_CODE)]) == [
        ("pid", asking.ANSWER_IDENTIFIER, "kind"), ("amount", asking.ANSWER_CODE, "kind"),
    ]
    hand_back(table, second)
    assert profile(table, "--answers", f"{table.path('questions.json')}") == 0
    held = kept(table)
    assert ("pid", asking.ANSWER_IDENTIFIER) in held and ("pid", asking.ANSWER_KEEP) not in held
    assert ("amount", asking.ANSWER_CODE) in held and ("amount", asking.ANSWER_DECIMAL_COMMA) not in held
    several = outputs(table)
    clear(table)
    assert in_one_round(table, {("pid", "kind"): asking.ANSWER_IDENTIFIER, ("amount", "kind"): asking.ANSWER_CODE}) == 0
    assert outputs(table) == several


# -- the refusal that asks for two runs ------------------------------------

_RECORDS = 360
_SUBJECTS = 12
_REPEATS = 11


def swapped_names(folder: pathlib.Path) -> Table:
    """A header `column_2,column_1` the first reading cannot tell from a record.

    The shape of tests/test_stage3_answer_paths.py: `column_1` names a
    column under both readings, and a different one under each.
    """
    lines = ["column_2,column_1"]
    for place in range(_RECORDS):
        second = "column_1" if place < _REPEATS else f"S{place:05d}"
        lines += [f"P{place % _SUBJECTS + 1:05d},{second}"]
    folder.mkdir(parents=True, exist_ok=True)
    return Table(fixtures.write(folder, "clinic.csv", "\n".join(lines) + "\n"), "clinic")


def test_the_refusals_two_runs_keep_the_first_runs_answer(tmp_path: pathlib.Path) -> None:
    """The refusal's own procedure: the reading answer first, the column in the next file.

    One file answering `names` for the first row and `identifier` for a
    column is refused, as before, and asks for two runs. Before plan
    P4-D408 the second run read the table the old way again, so
    `column_1` -- the second field under `names`, the name the file the
    first run wrote gives it -- was the FIRST field, the twelve subject
    codes, under the reading the second run took. Now the second run
    keeps the first's answer and ends where the two answers typed at once
    end, byte for byte.
    """
    table = swapped_names(tmp_path)
    assert profile(table) == 0
    both = questions(table)
    give(both, [(asking.FIRST_ROW_SUBJECT, asking.ANSWER_FIRST_ROW_NAMES), ("column_1", asking.ANSWER_IDENTIFIER)])
    hand_back(table, both)
    assert profile(table, "--answers", f"{table.path('questions.json')}") == 2, "one file holding both is refused, as before"
    assert profile(table) == 0
    first = questions(table)
    give(first, [(asking.FIRST_ROW_SUBJECT, asking.ANSWER_FIRST_ROW_NAMES)])
    hand_back(table, first)
    assert profile(table, "--answers", f"{table.path('questions.json')}") == 0
    second = questions(table)
    assert give(second, [("column_1", asking.ANSWER_IDENTIFIER)]) == [("column_1", asking.ANSWER_IDENTIFIER, "kind")]
    hand_back(table, second)
    assert profile(table, "--answers", f"{table.path('questions.json')}") == 0
    several = outputs(table)
    clear(table)
    assert profile(table, "--first-row", "names", "--identifier", "column_1") == 0
    assert outputs(table) == several


def test_a_carried_column_beside_a_new_reading_answer_is_refused(tmp_path: pathlib.Path) -> None:
    """An earlier answer names a column under the reading in force; a new reading moves it: refused."""
    table = swapped_names(tmp_path)
    assert profile(table, "--code", "column_2") == 0
    assert ("column_2", asking.ANSWER_CODE) in kept(table)
    document = questions(table)
    give(document, [(asking.FIRST_ROW_SUBJECT, asking.ANSWER_FIRST_ROW_NAMES)])
    hand_back(table, document)
    before = {one.name: one.read_bytes() for one in table.folder.iterdir()}
    assert profile(table, "--answers", f"{table.path('questions.json')}") == 2
    assert {one.name: one.read_bytes() for one in table.folder.iterdir()} == before


# -- an earlier answer that cannot be kept is refused ----------------------


def test_an_earlier_answer_this_table_cannot_hold_is_refused(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A kept `keep` for a column the table does not have: refused, nothing written."""
    table = mixed_table(tmp_path)
    assert profile(table) == 0
    document = questions(table)
    document[ANSWERED_BEFORE] = [asking._kept_entry("gone", asking.ANSWER_KEEP, "kind", "")]
    hand_back(table, document)
    before = {one.name: one.read_bytes() for one in table.folder.iterdir()}
    assert cli.main(["profile", f"{table.source}", "--replace", "--answers", f"{table.path('questions.json')}"]) == 2
    assert {one.name: one.read_bytes() for one in table.folder.iterdir()} == before
    screen = capsys.readouterr()
    words = screen.err + screen.out
    assert "'gone'" in words and "Nothing was written." in words


def test_the_section_is_absent_where_nothing_was_answered(tmp_path: pathlib.Path) -> None:
    """A run given no answer writes its questions file as before."""
    table = mixed_table(tmp_path)
    assert profile(table) == 0
    document = questions(table)
    assert asking.ANSWERED_BEFORE not in document and asking.ANSWERED_BEFORE_SAYS not in document


# -- the reading the file was written under (skeptic 1, item 1) -----------

_SUBJECTS_200 = 200
_ROWS_200 = 2400


def two_hundred_subjects(folder: pathlib.Path) -> Table:
    """Skeptic 1's table: a header `column_2,column_1` over 2,400 records of 200 subjects.

    The first field holds the subject codes, twelve rows each; the second
    holds 150 visit labels, and `column_1` in its first sixteen rows, so
    the header reads as a record and both readings name the columns
    `column_1` and `column_2` -- each a different field under each.
    """
    lines = ["column_2,column_1"]
    for place in range(_ROWS_200):
        second = "column_1" if place < 16 else f"V{place % 150 + 1:04d}"
        lines += [f"P{place % _SUBJECTS_200 + 1:05d},{second}"]
    folder.mkdir(parents=True, exist_ok=True)
    return Table(fixtures.write(folder, "clinic.csv", "\n".join(lines) + "\n"), "clinic")


def subject_codes_published(table: Table) -> int:
    """How many of the 200 real subject codes the description, summary or twin print."""
    files = outputs(table)
    found = 0
    for number in range(1, _SUBJECTS_200 + 1):
        code = f"P{number:05d}"
        if any(code.encode() in files[name] or code.lower().encode() in files[name] for name in files):
            found += 1
    return found


def answered_in_two_rounds(table: Table) -> None:
    """Round one answers `names`; round two `identifier` for the subjects, `keep` for the labels."""
    assert profile(table) == 0
    first = questions(table)
    give(first, [(asking.FIRST_ROW_SUBJECT, asking.ANSWER_FIRST_ROW_NAMES)])
    hand_back(table, first)
    assert profile(table, "--answers", f"{table.path('questions.json')}") == 0
    second = questions(table)
    assert give(second, [("column_2", asking.ANSWER_IDENTIFIER), ("column_1", asking.ANSWER_KEEP)]) == [
        ("column_2", asking.ANSWER_IDENTIFIER, "kind"), ("column_1", asking.ANSWER_KEEP, "kind"),
    ]
    hand_back(table, second)
    assert profile(table, "--answers", f"{table.path('questions.json')}") == 0
    assert subject_codes_published(table) == 0


def refused_with_nothing_written(table: Table, document: "dict[str, object]", *typed: str) -> str:
    """Hand `document` back with `typed`: exit 2, every file as it was; the screen's words."""
    hand_back(table, document)
    before = {one.name: one.read_bytes() for one in table.folder.iterdir()}
    with contextlib.redirect_stdout(io.StringIO()) as screen:
        with contextlib.redirect_stderr(screen):
            code = cli.main(["profile", f"{table.source}", "--replace", "--answers", f"{table.path('questions.json')}", *typed])
    assert code == 2, code
    assert {one.name: one.read_bytes() for one in table.folder.iterdir()} == before
    return screen.getvalue()


_OTHER_READING = "this run would read it another way"
_OTHER_NAMES = "this run reads your table under other names"


def kept_entry_of(document: "dict[str, object]", column: str) -> "dict[str, object]":
    section = document[ANSWERED_BEFORE]
    assert isinstance(section, list)
    for entry in section:
        if entry["column"] == column:
            return entry
    raise AssertionError(column)


@pytest.mark.parametrize("route", ["edited", "typed", "deleted"])
def test_the_kept_reading_changed_beside_kept_columns_is_refused(tmp_path: pathlib.Path, route: str) -> None:
    """Round three reads the table another way than round two's file: refused, no subject code printed.

    Measured on 9acf61d7: the kept `names` edited to `first-record`, or
    `--first-row data` typed, put `identifier` on the visit labels and
    `keep` on the subject column, and published 200 of 200 real subject
    codes; with the kept entry deleted, the same.
    """
    table = two_hundred_subjects(tmp_path)
    answered_in_two_rounds(table)
    document = questions(table)
    typed: "list[str]" = []
    if route == "edited":
        kept_entry_of(document, asking.FIRST_ROW_SUBJECT)["your_answer"] = asking.ANSWER_FIRST_ROW_DATA
    elif route == "typed":
        typed = ["--first-row", "data"]
    else:
        section = document[ANSWERED_BEFORE]
        assert isinstance(section, list)
        document[ANSWERED_BEFORE] = [entry for entry in section if entry["column"] != asking.FIRST_ROW_SUBJECT]
    words = refused_with_nothing_written(table, document, *typed)
    assert (_OTHER_NAMES if route == "deleted" else _OTHER_READING) in " ".join(words.split())
    assert subject_codes_published(table) == 0


@pytest.mark.parametrize("route", ["typed-code", "fresh-keep"])
def test_the_kept_names_deleted_beside_one_named_column_is_refused(tmp_path: pathlib.Path, route: str) -> None:
    """The kept `names` deleted beside ONE column answer of either source: refused, no subject code printed.

    The names check runs where a kept column answer (`typed-code`: round
    two types `--code column_1` for the visit labels) or a `keep` to a
    question offering `identifier` (`fresh-keep`: round two's file
    answers `column_1 keep` and deletes the kept `names`) names a column.
    Measured on 8901146b (lane AQ's verify, L1 and L2): with the one
    source the case carries left out of the check, the run read the
    subject codes as `column_1`, categorical, and published 200 of 200.
    """
    table = two_hundred_subjects(tmp_path)
    assert profile(table) == 0
    first = questions(table)
    give(first, [(asking.FIRST_ROW_SUBJECT, asking.ANSWER_FIRST_ROW_NAMES)])
    hand_back(table, first)
    assert profile(table, "--answers", f"{table.path('questions.json')}") == 0
    document = questions(table)
    if route == "typed-code":
        hand_back(table, document)
        assert profile(table, "--answers", f"{table.path('questions.json')}", "--code", "column_1") == 0
        assert ("column_1", "code") in kept(table)
        assert subject_codes_published(table) == 0
        document = questions(table)
    else:
        assert give(document, [("column_1", asking.ANSWER_KEEP)]) == [("column_1", asking.ANSWER_KEEP, "kind")]
    section = document[ANSWERED_BEFORE]
    assert isinstance(section, list)
    document[ANSWERED_BEFORE] = [entry for entry in section if entry["column"] != asking.FIRST_ROW_SUBJECT]
    words = refused_with_nothing_written(table, document)
    assert _OTHER_NAMES in " ".join(words.split())
    assert subject_codes_published(table) == 0


@pytest.mark.parametrize("route", ["edited", "typed"])
def test_the_kept_delimiter_changed_beside_a_kept_column_is_refused(tmp_path: pathlib.Path, route: str) -> None:
    """A kept delimiter edited or typed over, beside a kept column answer: refused by the reading's words."""
    table = mixed_table(tmp_path)
    assert profile(table, "--delimiter", ",", "--code", "reg") == 0
    assert (asking.DELIMITER_SUBJECT, "comma") in kept(table)
    document = questions(table)
    typed: "list[str]" = []
    if route == "edited":
        kept_entry_of(document, asking.DELIMITER_SUBJECT)["your_answer"] = "semicolon"
    else:
        typed = ["--delimiter", ";"]
    words = refused_with_nothing_written(table, document, *typed)
    assert _OTHER_READING in " ".join(words.split())


def test_the_kept_reading_unchanged_or_typed_alike_is_acted_on(tmp_path: pathlib.Path) -> None:
    """The kept `names` handed back as it stands, or typed alike: the run goes on, no code printed.

    The same for a kept delimiter typed alike: `--delimiter ,` beside the
    kept `comma` is read as the file's writer read the table.
    """
    table = two_hundred_subjects(tmp_path)
    answered_in_two_rounds(table)
    once = outputs(table)
    hand_back(table, questions(table))
    assert profile(table, "--answers", f"{table.path('questions.json')}") == 0
    assert outputs(table) == once
    assert profile(table, "--answers", f"{table.path('questions.json')}", "--first-row", "names") == 0
    assert outputs(table) == once
    comma = mixed_table(tmp_path / "comma")
    assert profile(comma, "--delimiter", ",", "--code", "reg") == 0
    assert (asking.DELIMITER_SUBJECT, "comma") in kept(comma)
    hand_back(comma, questions(comma))
    assert profile(comma, "--answers", f"{comma.path('questions.json')}") == 0
    handed = outputs(comma)
    hand_back(comma, questions(comma))
    assert profile(comma, "--answers", f"{comma.path('questions.json')}", "--delimiter", ",") == 0
    assert outputs(comma) == handed


# -- every typed form replaces a kept answer (skeptic 1, item 2) -----------


def counts_table(folder: pathlib.Path) -> Table:
    """Whole numbers that read as days from 1899 as well as counts, beside a label."""
    draw = random.Random(5)
    lines = ["n,label"]
    for _place in range(ROWS):
        lines += [f"{draw.randrange(40000, 45000)},L{draw.randrange(1, 9)}"]
    folder.mkdir(parents=True, exist_ok=True)
    return Table(fixtures.write(folder, "counts.csv", "\n".join(lines) + "\n"), "counts")


# (form, table, round one typed, round one answered in the file, round
# two typed, the kept answer that must win, the one it replaces)
_TYPED_CASES: "list[tuple[str, Callable[[pathlib.Path], Table], list[str], list[tuple[str, str]], list[str], tuple[str, str], tuple[str, str]]]" = [
    ("--code", mixed_table, ["--measurement", "reg"], [], ["--code", "reg"], ("reg", asking.ANSWER_CODE), ("reg", asking.ANSWER_MEASUREMENT)),
    ("--identifier", mixed_table, [], [("amount", asking.ANSWER_DECIMAL_COMMA)], ["--identifier", "amount"], ("amount", asking.ANSWER_IDENTIFIER), ("amount", asking.ANSWER_DECIMAL_COMMA)),
    ("--measurement", mixed_table, ["--code", "reg"], [], ["--measurement", "reg"], ("reg", asking.ANSWER_MEASUREMENT), ("reg", asking.ANSWER_CODE)),
    # A comma beside a kept `measurement` is the legal pair, kept beside it
    # (the third round); a comma replaces a kept `code`, which it cannot
    # stand beside.
    ("--decimal-comma", mixed_table, ["--code", "amount"], [], ["--decimal-comma", "amount"], ("amount", asking.ANSWER_DECIMAL_COMMA), ("amount", asking.ANSWER_CODE)),
    ("--twelve-hour", mixed_table, ["--code", "clock"], [], ["--twelve-hour", "clock"], ("clock", asking.ANSWER_TWELVE_HOUR), ("clock", asking.ANSWER_CODE)),
    ("--date-column", mixed_table, [], [("mostly", asking.ANSWER_KEEP)], ["--date-column", "mostly"], ("mostly", asking.ANSWER_DATES), ("mostly", asking.ANSWER_KEEP)),
    ("--date-count", counts_table, ["--measurement", "n"], [], ["--date-count", "n", date_counts.EXCEL_1900], ("n", date_counts.EXCEL_1900), ("n", asking.ANSWER_MEASUREMENT)),
    ("--century", mixed_table, ["--century", "born=1930"], [], ["--century", "born=1900"], ("born", asking.ANSWER_CENTURY_1900), ("born", asking.ANSWER_CENTURY_1930)),
    ("--day-first", mixed_table, [], [(asking.DAY_FIRST_SUBJECT, asking.ANSWER_MONTH_FIRST)], ["--day-first"], (asking.DAY_FIRST_SUBJECT, asking.ANSWER_DAY_FIRST), (asking.DAY_FIRST_SUBJECT, asking.ANSWER_MONTH_FIRST)),
    ("--delimiter", mixed_table, ["--delimiter", ";"], [], ["--delimiter", ","], (asking.DELIMITER_SUBJECT, "comma"), (asking.DELIMITER_SUBJECT, "semicolon")),
    ("--first-row", mixed_table, ["--first-row", "data"], [], ["--first-row", "names"], (asking.FIRST_ROW_SUBJECT, asking.ANSWER_FIRST_ROW_NAMES), (asking.FIRST_ROW_SUBJECT, asking.ANSWER_FIRST_ROW_DATA)),
]
# The answer word each form is set against kept answers by.
_FORM_WORDS = {
    "--code": asking.ANSWER_CODE,
    "--identifier": asking.ANSWER_IDENTIFIER,
    "--measurement": asking.ANSWER_MEASUREMENT,
    "--decimal-comma": asking.ANSWER_DECIMAL_COMMA,
    "--twelve-hour": asking.ANSWER_TWELVE_HOUR,
    "--date-column": asking.ANSWER_DATES,
    "--date-count": date_counts.EXCEL_1900,
    "--century": asking.ANSWER_CENTURY_1900,
    "--day-first": asking.ANSWER_DAY_FIRST,
    "--delimiter": "comma",
    "--first-row": asking.ANSWER_FIRST_ROW_NAMES,
}


def typed_case(folder: pathlib.Path, form: str) -> None:
    """One typed form replacing a kept answer: acted on, kept, and one round's bytes."""
    _form, make, typed_first, answered_first, typed_then, wins, loses = [case for case in _TYPED_CASES if case[0] == form][0]
    table = make(folder)
    assert profile(table, *typed_first) == 0
    if answered_first:
        document = questions(table)
        assert len(give(document, answered_first)) == len(answered_first)
        hand_back(table, document)
        assert profile(table, "--answers", f"{table.path('questions.json')}") == 0
    assert loses in kept(table)
    hand_back(table, questions(table))
    assert profile(table, "--answers", f"{table.path('questions.json')}", *typed_then) == 0
    held = kept(table)
    assert wins in held and loses not in held, sorted(held)
    several = outputs(table)
    if form == "--identifier":
        description = json.loads(several["description"])
        column = [one for one in description["columns"] if one["name"] == "amount"][0]
        assert column["role"] == "identifier"
        source = table.source.read_text(encoding="utf-8").splitlines()[1:]
        place = _MIXED.split(",").index("amount")
        values = {line.split(",")[place] for line in source}
        published = json.dumps(column)
        assert not [value for value in values if f'"{value}"' in published]
    hand_back(table, questions(table))
    assert profile(table, "--answers", f"{table.path('questions.json')}") == 0
    assert wins in kept(table)
    assert outputs(table) == several
    clear(table)
    assert profile(table, *typed_then) == 0
    assert outputs(table) == several


@pytest.mark.parametrize("form", [case[0] for case in _TYPED_CASES])
def test_every_typed_form_replaces_a_kept_answer(tmp_path: pathlib.Path, form: str) -> None:
    """Each option `_typed_answers` maps, typed over a kept answer about its column: the typed one wins."""
    typed_case(tmp_path, form)


@pytest.mark.parametrize("form", [case[0] for case in _TYPED_CASES])
def test_mutant_a_typed_form_not_set_against_kept_answers_is_seen(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, form: str) -> None:
    """The form left out of `_typed_answers`: the kept answer stands, or the run refuses."""
    real = cli._typed_answers
    word = _FORM_WORDS[form]

    def typed_answers(*arguments: object) -> "tuple[tuple[str, str], ...]":
        return tuple(one for one in real(*arguments) if one[1] != word)  # type: ignore[arg-type]

    monkeypatch.setattr(cli, "_typed_answers", typed_answers)
    with pytest.raises(AssertionError):
        typed_case(tmp_path, form)


# -- a blank kept entry keeps its answer (skeptic 1, item 3) ---------------


def test_a_blank_kept_entry_keeps_its_answer(tmp_path: pathlib.Path) -> None:
    """A kept `identifier` and a kept `code` with `your_answer` cleared: the unedited file's bytes."""
    table = mixed_table(tmp_path)
    assert profile(table) == 0
    first = questions(table)
    give(first, [("pid", asking.ANSWER_IDENTIFIER), ("reg", asking.ANSWER_CODE)])
    hand_back(table, first)
    assert profile(table, "--answers", f"{table.path('questions.json')}") == 0
    handed = questions(table)
    hand_back(table, handed)
    assert profile(table, "--answers", f"{table.path('questions.json')}") == 0
    unedited = outputs(table)
    for column in ("pid", "reg"):
        kept_entry_of(handed, column)["your_answer"] = ""
    hand_back(table, handed)
    assert profile(table, "--answers", f"{table.path('questions.json')}") == 0
    assert outputs(table) == unedited


def test_mutant_a_blank_kept_entry_read_as_unanswered_is_seen(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A cleared kept line read as no answer: the person column is held again, the code kept blank."""
    real = asking._entry_answer

    def entry_answer(entry: object, place: str, carried: bool = False) -> "tuple[str, str, tuple[str, ...]] | None":
        return real(entry, place, False)

    monkeypatch.setattr(asking, "_entry_answer", entry_answer)
    with pytest.raises(AssertionError):
        test_a_blank_kept_entry_keeps_its_answer(tmp_path)


# -- the contradicted answer (skeptic 1, item 4) ---------------------------


def test_answers_not_kept_names_what_the_section_drops() -> None:
    """A carried answer the section lacks is named; a carried `keep` beside a declaration is not."""
    section = asking.answered_before(asking.Given(columns=("a", "b"), codes=("b",)))
    carried = (("a", asking.ANSWER_CODE, "kind"), ("b", asking.ANSWER_KEEP, "kind"), ("b", asking.ANSWER_CODE, "kind"))
    assert asking.answers_not_kept(carried, section) == ["a"]
    assert asking.answers_not_kept((("a", asking.ANSWER_TWELVE_HOUR, "clock"),), section) == ["a"]
    assert asking.answers_not_kept((("b", asking.ANSWER_CODE, "kind"),), section) == []


def test_mutant_answers_not_kept_naming_nothing_is_seen(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(asking, "answers_not_kept", lambda carried, section: [])
    with pytest.raises(AssertionError):
        test_answers_not_kept_names_what_the_section_drops()


# -- `keep` alone does not make two questions one (skeptic 1, item 6) ------


def test_a_fresh_keep_to_another_question_leaves_a_kept_code(tmp_path: pathlib.Path) -> None:
    """`mostly` kept as `code`; the question of dates answered `keep` beside it: both stand.

    The question of dates is the round-zero file's own entry, handed back
    in the `asked` section of the file the next run wrote; it offers only
    `keep` and `dates`, so it is not the question `code` answered.
    """
    table = mixed_table(tmp_path)
    assert profile(table) == 0
    dated = [entry for entry in entries(questions(table)) if entry["column"] == "mostly"]
    assert len(dated) == 1 and offered(dated[0]) == (asking.ANSWER_KEEP, asking.ANSWER_DATES)
    assert profile(table, "--code", "mostly") == 0
    document = questions(table)
    dated[0]["your_answer"] = asking.ANSWER_KEEP
    asked = document["asked"]
    assert isinstance(asked, list)
    asked += [dated[0]]
    hand_back(table, document)
    assert profile(table, "--answers", f"{table.path('questions.json')}") == 0
    held = kept(table)
    assert ("mostly", asking.ANSWER_CODE) in held and ("mostly", asking.ANSWER_KEEP) in held


def test_mutant_keep_making_two_questions_one_is_seen(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`keep` offered counted as deciding what the column holds: the question of dates replaces the kept code."""
    real = asking._decided_by

    def decided_by(answer: str, offered: "tuple[str, ...]") -> "tuple[str, ...]":
        found = real(answer, offered)
        return found + ("kind",) if asking.ANSWER_KEEP in offered else found

    monkeypatch.setattr(asking, "_decided_by", decided_by)
    with pytest.raises(AssertionError):
        test_a_fresh_keep_to_another_question_leaves_a_kept_code(tmp_path)


# -- codes in dates answered against the table's order (skeptic 1, item 5) -


def test_codes_in_dates_answered_against_the_table_order(tmp_path: pathlib.Path) -> None:
    """The first column's codes in round one, the second's in round two: one round's bytes.

    The second run acts on the fresh answer before the kept one, against
    the table's order, and the files are one round's all the same. Two
    columns sharing a spelling cannot be answered in different rounds:
    the first answer declares the spelling in every column, so the next
    file no longer asks it (measured with `UNK` twice, and `UNK` beside
    `unk`, answered `missing` and `real-value`).
    """
    draw = random.Random(11)
    lines = ["seen_at,other"]
    for place in range(ROWS):
        lines += [",".join([
            "UNK" if place % 40 == 0 else f"2023-{draw.randrange(1, 13):02d}-{draw.randrange(1, 29):02d}",
            "TBD" if place % 40 == 7 else f"2024-{draw.randrange(1, 13):02d}-{draw.randrange(1, 29):02d}",
        ])]
    tmp_path.mkdir(parents=True, exist_ok=True)
    table = Table(fixtures.write(tmp_path, "real.csv", "\n".join(lines) + "\n"), "real")
    plan = [[("seen_at", asking.ANSWER_NO_DATE)], [("other", asking.ANSWER_NO_DATE)]]
    rounds, differs = compare(table, by_round(plan))
    assert len(rounds.given) == 2 and rounds.lost == []
    assert not any(differs.values()), differs


# -- the reading's mutants (skeptic 1, item 1) ------------------------------


@pytest.mark.parametrize("route", ["edited", "typed"])
def test_mutant_the_kept_reading_not_checked_is_seen(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, route: str) -> None:
    monkeypatch.setattr(cli, "_kept_reading_changed", lambda written, first_row, delimiter, kept, automatic=False: [])
    with pytest.raises(AssertionError):
        test_the_kept_reading_changed_beside_kept_columns_is_refused(tmp_path, route)


def test_mutant_the_names_not_checked_is_seen(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(asking, "columns_answered_under", lambda document: None)
    with pytest.raises(AssertionError):
        test_the_kept_reading_changed_beside_kept_columns_is_refused(tmp_path, "deleted")


# -- the mutants, each red ------------------------------------------------


def test_mutant_the_writer_dropping_earlier_answers_is_seen(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The section written with this run's file answers alone: round two loses round one's."""
    written_now: "dict[str, list[tuple[str, str]]]" = {"pairs": []}
    real_answers_in = asking.answers_in

    def answers_in(document: object, shown: str) -> asking.Answers:
        found = real_answers_in(document, shown)
        assert isinstance(document, dict)
        written_now["pairs"] = [
            (f"{entry['column']}", f"{entry['your_answer']}") for entry in entries(document) if entry.get("your_answer")
        ]
        return dataclasses.replace(found, carried=())

    real_answered_before = asking.answered_before

    def answered_before(given: asking.Given) -> "list[dict[str, object]]":
        return [entry for entry in real_answered_before(given) if (f"{entry['column']}", f"{entry['your_answer']}") in written_now["pairs"]]

    monkeypatch.setattr(asking, "answers_in", answers_in)
    monkeypatch.setattr(asking, "answered_before", answered_before)
    table, answerer = zoo_table(tmp_path, "us_vitals")
    rounds = in_rounds(table, answerer)
    assert rounds.lost, "the mutant must lose patient_id"


def test_mutant_the_later_answer_losing_to_the_earlier_is_seen(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """No later answer replaces a kept one: the typed measurement does not win."""
    monkeypatch.setattr(asking, "_answered_again", lambda name, answer, family, later: False)
    with pytest.raises(AssertionError):
        test_a_later_round_changes_an_earlier_answer(tmp_path / "typed")
    with pytest.raises(AssertionError):
        test_a_later_answer_to_the_question_asked_again_wins(tmp_path / "asked")


def test_mutant_the_refusal_path_losing_answers_is_seen(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The answer about the file's reading not kept: the refusal's second run reads the old way."""
    real_answered_before = asking.answered_before
    subjects = (asking.FIRST_ROW_SUBJECT, asking.DELIMITER_SUBJECT)

    def answered_before(given: asking.Given) -> "list[dict[str, object]]":
        return [entry for entry in real_answered_before(given) if entry["column"] not in subjects]

    monkeypatch.setattr(asking, "answered_before", answered_before)
    with pytest.raises(AssertionError):
        test_the_refusals_two_runs_keep_the_first_runs_answer(tmp_path)


def test_mutant_the_refusal_not_made_is_seen(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """No check of the earlier answers: the unknown column is dropped in silence."""
    monkeypatch.setattr(cli, "_earlier_answers_dropped", lambda carried, columns, given: [])
    with pytest.raises(AssertionError):
        test_an_earlier_answer_this_table_cannot_hold_is_refused(tmp_path, capsys)


# -- the third round: Codex's review of lane AQ (codex-w3/verdict-AQ.md) ------


def dose_table(folder: pathlib.Path) -> Table:
    """Codex's item 1: 200 cells `1.200` to `1.399`, a point between thousands."""
    folder.mkdir(parents=True, exist_ok=True)
    lines = ["dose"] + [f"1.{place:03d}" for place in range(200, 400)]
    return Table(fixtures.write(folder, "dose.csv", "\n".join(lines) + "\n"), "dose")


def described_column(table: Table, name: str) -> "dict[str, object]":
    described = json.loads(table.path("profile.json").read_text(encoding="utf-8"))
    found = [one for one in described["columns"] if one["name"] == name]
    assert len(found) == 1, name
    column = found[0]
    assert isinstance(column, dict)
    return column


_PAIR = (("dose", asking.ANSWER_MEASUREMENT), ("dose", asking.ANSWER_DECIMAL_COMMA))


def test_a_measurement_and_its_comma_are_both_kept(tmp_path: pathlib.Path) -> None:
    """`--measurement dose --decimal-comma dose`, at once or a round apart either way: both kept, the mean 1299.5.

    Codex's review of lane AQ, item 1 (high), on 8901146b: the section
    kept `measurement` alone in the one slot it gave a column, and the
    file handed back unchanged read the 200 cells with the point as the
    decimal point, mean 1.2995. Each route ends where the two typed at
    once end, byte for byte, and a third round handed back unchanged
    keeps it there.
    """
    for route, first, then in (
        ("handed-back", ["--measurement", "dose", "--decimal-comma", "dose"], []),
        ("comma-later", ["--measurement", "dose"], ["--decimal-comma", "dose"]),
        ("measurement-later", ["--decimal-comma", "dose"], ["--measurement", "dose"]),
    ):
        table = dose_table(tmp_path / route)
        assert profile(table, *first) == 0
        hand_back(table, questions(table))
        assert profile(table, "--answers", f"{table.path('questions.json')}", *then) == 0
        held = kept(table)
        assert all(pair in held for pair in _PAIR), (route, sorted(held))
        assert described_column(table, "dose")["mean"] == 1299.5, route
        hand_back(table, questions(table))
        assert profile(table, "--answers", f"{table.path('questions.json')}") == 0
        assert described_column(table, "dose")["mean"] == 1299.5, route
        several = outputs(table)
        clear(table)
        assert profile(table, "--measurement", "dose", "--decimal-comma", "dose") == 0
        assert described_column(table, "dose")["mean"] == 1299.5
        assert outputs(table) == several, route


def test_mutant_the_comma_in_the_slot_of_what_the_column_holds_is_seen(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The section keeping one answer a column, as 8901146b did: the comma is lost and the mean is 1.2995."""
    real = asking.answered_before

    def answered_before(given: asking.Given) -> "list[dict[str, object]]":
        alone = tuple(name for name in given.decimal_commas if name not in given.measurements)
        return real(dataclasses.replace(given, decimal_commas=alone))

    monkeypatch.setattr(asking, "answered_before", answered_before)
    with pytest.raises(AssertionError):
        test_a_measurement_and_its_comma_are_both_kept(tmp_path)


def visits_table(folder: pathlib.Path, grouped: bool = False) -> Table:
    """Codex's item 2: 600 visit dates written as Excel day counts, `random.Random(5).randrange(40000, 45000)`.

    `grouped` writes each count with a point between the thousands,
    `42.345` (lane AQ's close verify, finding 1).
    """
    draw = random.Random(5)
    folder.mkdir(parents=True, exist_ok=True)
    counts = [draw.randrange(40000, 45000) for _ in range(ROWS)]
    lines = ["visit"] + [f"{one // 1000}.{one % 1000:03d}" if grouped else f"{one}" for one in counts]
    return Table(fixtures.write(folder, "visits.csv", "\n".join(lines) + "\n"), "visits")


def day_counts_printed(files: "dict[str, bytes]") -> int:
    """How many different day counts 40000 to 44999 the description or the summary publish as a number.

    A column of visit dates attached to persons is described as dates;
    read as a number column instead, its mean, percentiles and tails are
    day counts -- dates of persons published as plain numbers, outside
    the rule that counts dates in subjects (98 in the description and 4
    in the summary on bbdf0f88, `wave6/AQ/r3-repro-bbdf0f88.log`). The
    twin is not counted: it writes its generated dates as the source
    spelled them, day counts, whichever reading stands.
    """
    found: "dict[bytes, bool]" = {}
    for name in ("description", "summary"):
        for one in re.findall(rb"(?<![0-9])4[0-4][0-9]{3}(?![0-9])", files[name]):
            found[one] = True
    return len(found)


def test_a_comma_beside_counted_dates_keeps_the_dates(tmp_path: pathlib.Path) -> None:
    """`--decimal-comma visit` beside a kept `excel-1900`, typed over it or handed back: the dates stand.

    Codex's review of lane AQ, item 2 (high), on 8901146b: typed over the
    kept date count, the comma took the whole family of what a column
    holds with it and deleted the dates, so the 600 visit dates were
    described as a count column -- their day counts published as plain
    numbers; and the two typed at once, handed back unchanged, had the
    kept comma delete the dates where the answers are merged
    (`cli._run_profile`) and the run refused. The privacy face: the date
    reading is kept and no day count is published, in the description or
    the summary.

    The third route answers the comma in the file (lane AQ's close
    verify, finding 1): the 600 counts written with a point between the
    thousands, `42.345`, the first file's question about `visit` answered
    `decimal_comma` -- an answer deciding what the column holds as well
    as how its numbers are written -- with `--date-count visit
    excel-1900` typed. The typed count is kept after the round and after
    one hand-back unchanged, and the files equal one round's; deleting
    the counted dates of every column the file's answers speak for
    (`spoken_for` in place of `held_by_answer`) drops it, as bbdf0f88
    did. Kept, that count is declined with a notice -- the cells do not
    read as such dates -- so this route judges the answers and the
    files, not the reading: the day counts it then publishes as numbers
    are lane HX2's item.
    """
    for route in ("typed-over", "handed-back", "comma-answered"):
        dated = route != "comma-answered"
        table = visits_table(tmp_path / route, grouped=not dated)
        if route == "typed-over":
            assert profile(table, "--date-count", "visit", date_counts.EXCEL_1900) == 0
            hand_back(table, questions(table))
            assert profile(table, "--answers", f"{table.path('questions.json')}", "--decimal-comma", "visit") == 0
        elif route == "handed-back":
            assert profile(table, "--date-count", "visit", date_counts.EXCEL_1900, "--decimal-comma", "visit") == 0
            hand_back(table, questions(table))
            assert profile(table, "--answers", f"{table.path('questions.json')}") == 0
        else:
            assert profile(table) == 0
            document = questions(table)
            assert give(document, [("visit", asking.ANSWER_DECIMAL_COMMA)]), route
            hand_back(table, document)
            assert profile(table, "--answers", f"{table.path('questions.json')}", "--date-count", "visit", date_counts.EXCEL_1900) == 0
            assert ("visit", date_counts.EXCEL_1900) in kept(table), (route, sorted(kept(table)))
            hand_back(table, questions(table))
            assert profile(table, "--answers", f"{table.path('questions.json')}") == 0
        held = kept(table)
        assert ("visit", date_counts.EXCEL_1900) in held and ("visit", asking.ANSWER_DECIMAL_COMMA) in held, (route, sorted(held))
        if dated:
            assert described_column(table, "visit")["role"] == "datetime", route
        several = outputs(table)
        if dated:
            assert day_counts_printed(several) == 0, route
        clear(table)
        assert profile(table, "--date-count", "visit", date_counts.EXCEL_1900, "--decimal-comma", "visit") == 0
        assert outputs(table) == several, route


def test_mutant_a_typed_comma_deciding_the_date_count_is_seen(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A typed comma deciding what the column holds and its date count, as on 8901146b: the dates are lost."""
    real = asking._decided_by

    def decided_by(answer: str, offered: "tuple[str, ...]") -> "tuple[str, ...]":
        found = real(answer, offered)
        return found + ("kind", "counted") if answer == asking.ANSWER_DECIMAL_COMMA else found

    monkeypatch.setattr(asking, "_decided_by", decided_by)
    with pytest.raises(AssertionError):
        test_a_comma_beside_counted_dates_keeps_the_dates(tmp_path)


def events_table(folder: pathlib.Path) -> Table:
    """Codex's item 3: two-figure years, `01/02/40` on 30 rows beside 570 others."""
    draw = random.Random(3)
    folder.mkdir(parents=True, exist_ok=True)
    lines = ["event_date"] + ["01/02/40"] * 30 + [
        f"{draw.randrange(1, 13):02d}/{draw.randrange(1, 29):02d}/{draw.randrange(30, 70):02d}" for _ in range(ROWS - 30)
    ]
    return Table(fixtures.write(folder, "events.csv", "\n".join(lines) + "\n"), "events")


def heavy_dates(table: Table) -> "list[object]":
    """The dates `event_date` publishes as heavy, each with its count."""
    found = described_column(table, "event_date")["heavy_dates"]
    assert isinstance(found, list)
    return found


def numbers_table(folder: pathlib.Path) -> Table:
    """300 records of two numbers and no names: read alone, the first row is a record."""
    draw = random.Random(4)
    folder.mkdir(parents=True, exist_ok=True)
    lines = [f"{draw.randrange(100, 999)},{draw.randrange(10, 99)}" for _ in range(300)]
    return Table(fixtures.write(folder, "plain.csv", "\n".join(lines) + "\n"), "plain")


def test_a_typed_default_replaces_a_kept_answer(tmp_path: pathlib.Path) -> None:
    """`--century event_date=1969` and `--first-row auto` typed over kept answers: each replaces its answer.

    Codex's review of lane AQ, item 3 (high), on 8901146b: the parser
    dropped the standing window before the typed answers were set
    against the kept ones, so a kept 1930 window survived and `01/02/40`
    read 1940 where the person asked for 2040; a kept `names` survived
    `--first-row auto` alike. The standing window typed is now kept as
    the answer naming it (`1969-2068`); a window nobody typed is not
    stored. `auto` typed is kept as nothing, and the names it reads are
    set against the file's list: the same names are acted on, others
    refused with nothing written.
    """
    events = events_table(tmp_path / "century")
    assert profile(events, "--century", "event_date=1930") == 0
    assert ("event_date", asking.ANSWER_CENTURY_1930) in kept(events)
    assert {"count": 30, "date": "1940-01-02"} in heavy_dates(events)
    hand_back(events, questions(events))
    assert profile(events, "--answers", f"{events.path('questions.json')}", "--century", "event_date=1969") == 0
    held = kept(events)
    assert ("event_date", asking.ANSWER_CENTURY_POSIX) in held and ("event_date", asking.ANSWER_CENTURY_1930) not in held
    assert json.loads(events.path("profile.json").read_text(encoding="utf-8"))["settings"]["century_windows"] == []
    assert {"count": 30, "date": "2040-01-02"} in heavy_dates(events)
    several = outputs(events)
    hand_back(events, questions(events))
    assert profile(events, "--answers", f"{events.path('questions.json')}") == 0
    assert outputs(events) == several
    clear(events)
    assert profile(events, "--century", "event_date=1969") == 0
    assert outputs(events) == several
    clear(events)
    assert profile(events) == 0
    assert asking.ANSWERED_BEFORE not in questions(events), "a window nobody typed is not stored"

    plain = numbers_table(tmp_path / "first-row")
    assert profile(plain, "--first-row", "names") == 0
    assert (asking.FIRST_ROW_SUBJECT, asking.ANSWER_FIRST_ROW_NAMES) in kept(plain)
    hand_back(plain, questions(plain))
    assert profile(plain, "--answers", f"{plain.path('questions.json')}", "--first-row", "auto") == 0
    described = json.loads(plain.path("profile.json").read_text(encoding="utf-8"))
    assert [one["name"] for one in described["columns"]] == ["column_1", "column_2"] and described["n_rows"] == 300
    assert not [pair for pair in kept(plain) if pair[0] == asking.FIRST_ROW_SUBJECT]
    several = outputs(plain)
    clear(plain)
    assert profile(plain, "--first-row", "auto") == 0
    assert outputs(plain) == several

    named = mixed_table(tmp_path / "same-names")
    assert profile(named, "--first-row", "names", "--code", "reg") == 0
    hand_back(named, questions(named))
    assert profile(named, "--answers", f"{named.path('questions.json')}", "--first-row", "auto") == 0
    assert ("reg", asking.ANSWER_CODE) in kept(named)
    assert not [pair for pair in kept(named) if pair[0] == asking.FIRST_ROW_SUBJECT]
    several = outputs(named)
    clear(named)
    assert profile(named, "--first-row", "auto", "--code", "reg") == 0
    assert outputs(named) == several

    moved = numbers_table(tmp_path / "other-names")
    assert profile(moved, "--first-row", "names") == 0
    first = [one["name"] for one in json.loads(moved.path("profile.json").read_text(encoding="utf-8"))["columns"]]
    assert profile(moved, "--first-row", "names", "--code", first[0]) == 0
    words = refused_with_nothing_written(moved, questions(moved), "--first-row", "auto")
    assert f"'{first[0]}'" in words


def keys_table(folder: pathlib.Path, name: str) -> Table:
    """Codex's item 4: a column of record numbers named exactly like a file question's subject."""
    draw = random.Random(6)
    folder.mkdir(parents=True, exist_ok=True)
    lines = [f"{name},value"] + [f"K{100000 + place},{draw.randrange(50, 150)}" for place in range(ROWS)]
    return Table(fixtures.write(folder, "keys.csv", "\n".join(lines) + "\n"), "keys")


def test_a_column_named_like_a_file_question_is_not_a_reading(tmp_path: pathlib.Path) -> None:
    """A column named `which row your column names are in` or `the character between your columns`, kept `identifier`: acted on.

    Codex's review of lane AQ, item 4 (medium), on 8901146b: the kept
    entry was read as an answer about how the file is read by its
    subject text alone, with no reading it could name, and the unchanged
    hand-back was refused. A file question is now told by its family as
    well: what the entry offers.
    """
    for subject in (asking.FIRST_ROW_SUBJECT, asking.DELIMITER_SUBJECT):
        table = keys_table(tmp_path / subject.split()[1], subject)
        assert profile(table, "--identifier", subject) == 0
        assert (subject, asking.ANSWER_IDENTIFIER) in kept(table)
        assert asking.kept_reading(questions(table)) == ()
        once = outputs(table)
        hand_back(table, questions(table))
        assert profile(table, "--answers", f"{table.path('questions.json')}") == 0, subject
        assert outputs(table) == once, subject


def test_judged_never_reads_a_refusal_as_a_twin() -> None:
    """K-S3-66's comparison of one table's two routes (Codex's review of lane AQ, item 5)."""
    files = {"description": b"d", "summary": b"s", "questions": b"q"}
    assert judged((dict(files), 2), (dict(files), 2)) == Judged(0, True, False)
    assert judged((dict(files), 2), (dict(files), 3)) == Judged(1, True, False)
    assert judged((dict(files, twin=b"t"), 0), (dict(files), 2)) == Judged(1, False, False)
    assert judged((dict(files), 0), (dict(files, twin=b"t"), 0)) == Judged(0, False, True)
    assert judged((dict(files, twin=b"t"), 0), (dict(files, twin=b"t"), 0)) == Judged(0, False, False)
    assert judged((dict(files, twin=b"t"), 0), (dict(files, twin=b"u"), 0)) == Judged(1, False, False)


def test_k_s3_66_counts_a_refusal_on_both_routes_apart(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Generation refused on both routes of a zoo table: counted apart, never as two twins written alike.

    Codex's review of lane AQ, item 5 (medium): both routes compared by
    their exit codes, `exit 2` against `exit 2`, counted no difference
    and no failure, so a regression stopping every twin from being
    written left K-S3-66 green.
    """
    real = run

    def refusing(arguments: "list[str]") -> int:
        return 2 if arguments[0] == "generate" else real(arguments)

    monkeypatch.setitem(globals(), "run", refusing)
    found = {name: 0 for name in _MEASURED}
    table, answerer = zoo_table(tmp_path, "us_vitals")
    measure_table(table, answerer, found)
    assert found["twins_refused_on_both_routes"] == 1
    assert found["answers"] == 2 and found["byte_differences"] == 0 and found["failed_runs"] == 0


def test_mutant_judged_reading_refusals_as_twins_is_seen(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The comparison of 8901146b: an exit code stands in for the twin, and two refusals compare alike."""

    def as_before(several: "tuple[dict[str, bytes], int]", once: "tuple[dict[str, bytes], int]") -> Judged:
        first = dict(several[0], twin=several[0]["twin"] if "twin" in several[0] else f"exit {several[1]}".encode())
        second = dict(once[0], twin=once[0]["twin"] if "twin" in once[0] else f"exit {once[1]}".encode())
        return Judged(sum(1 for name in first if first[name] != second[name]), False, False)

    monkeypatch.setitem(globals(), "judged", as_before)
    with pytest.raises(AssertionError):
        test_judged_never_reads_a_refusal_as_a_twin()
    with pytest.raises(AssertionError):
        test_k_s3_66_counts_a_refusal_on_both_routes_apart(tmp_path, monkeypatch)


# -- lane HX3 (plan P4-D420): route four's person question offers `code` --------
#
# Route four of the person rule (plan P4-D401) asks a key of figures
# repeating on its patients' rows the person question, and the checklist,
# the one question that offered such a column `code`, lists it only once a
# person column is declared, a round later. Measured on the health data
# zoo at batch 4d's integration (P4-D399): the diagnoses export's SNOMED
# ids, answered `keep` in the one round a person answers, wrote codes the
# real never writes and lost values 11 or more real rows hold. So the
# question route four puts offers `code` in round one, and that answer is
# the checklist's: the same description, summary and twin, byte for byte.

_ROUTE_FOUR_COLUMN = "snomed_id"
_ROUTE_FOUR_PERSON = ("enc_id", asking.ANSWER_IDENTIFIER)


def diagnoses_table(folder: pathlib.Path) -> Table:
    kind = zoo.table_named("diagnoses_procedures")
    return Table(zoo.write_table(kind, folder, ROWS, SEED), kind.name)


def entry_about(entries_of: "list[object]", column: str) -> "list[dict[str, object]]":
    return [entry for entry in entries_of if isinstance(entry, dict) and entry["column"] == column]


def code_choice(entry: "dict[str, object]") -> "dict[str, object]":
    choices = entry["answers_you_can_give"]
    assert isinstance(choices, list)
    return [choice for choice in choices if choice["answer"] == asking.ANSWER_CODE][0]


def answer_and_run(table: Table, wanted: "list[tuple[str, str]]") -> None:
    document = questions(table)
    assert [(one[0], one[1]) for one in give(document, wanted)] == wanted, "an answer not offered where it is given"
    hand_back(table, document)
    assert profile(table, "--answers", f"{table.path('questions.json')}") == 0


def route_four_case(folder: pathlib.Path) -> None:
    """`code` answered to route four's question in round one, against the checklist's `code` in round two."""
    once = diagnoses_table(folder / "once")
    put: "dict[str, list[asking.Question]]" = {"questions": []}
    asks = asking.person_questions

    def recorded(*arguments: object, **named: object) -> "list[asking.Question]":
        found = asks(*arguments, **named)  # type: ignore[arg-type]
        put["questions"] += found
        return found

    with pytest.MonkeyPatch.context() as patched:
        patched.setattr(asking, "person_questions", recorded)
        assert profile(once) == 0
    # `code` is never what standing still gives (skeptic 1 of lane HX3, item
    # 2): Enter at the keyboard, or a blank in the file, on a patient key
    # route four reaches would otherwise declare it a code and publish it.
    standing = [one.taken for one in put["questions"] if one.name == _ROUTE_FOUR_COLUMN]
    assert standing != [] and set(standing) == {asking.ANSWER_KEEP}, f"the standing answer is not keep: {standing}"
    first = questions(once)
    asked = entry_about(list(first["asked"]), _ROUTE_FOUR_COLUMN)  # type: ignore[arg-type]
    assert len(asked) == 1 and asked[0]["read_as_now"] == asking.ANSWER_IDENTIFIER, "route four did not put the question"
    assert asked[0]["your_answer"] == "", f"the file answers for the person: {asked[0]['your_answer']!r}"
    assert offered(asked[0]) == (asking.ANSWER_KEEP, asking.ANSWER_CODE, asking.ANSWER_IDENTIFIER), (
        f"code not offered in round one: {offered(asked[0])}"
    )
    said_in_round_one = code_choice(asked[0])
    answer_and_run(once, [_ROUTE_FOUR_PERSON, (_ROUTE_FOUR_COLUMN, asking.ANSWER_CODE)])
    in_one = outputs(once)
    described = json.loads(in_one["description"])
    settings = described["settings"]
    block = [one for one in described["columns"] if one["name"] == _ROUTE_FOUR_COLUMN][0]
    assert block["role"] != "identifier" and _ROUTE_FOUR_COLUMN in settings["forced_codes"], (
        f"code answered, the column still held: {block['role']}, {settings['forced_codes']}"
    )
    assert _ROUTE_FOUR_COLUMN not in settings["forced_identifiers"], "code answered, the column still held"
    held = kept(once)
    assert (_ROUTE_FOUR_COLUMN, asking.ANSWER_CODE) in held and _ROUTE_FOUR_PERSON in held, (
        f"answered_before lost: {sorted(held)}"
    )

    rounds = diagnoses_table(folder / "rounds")
    assert profile(rounds) == 0
    answer_and_run(rounds, [_ROUTE_FOUR_PERSON, (_ROUTE_FOUR_COLUMN, asking.ANSWER_KEEP)])
    second = questions(rounds)
    assert entry_about(list(second["asked"]), _ROUTE_FOUR_COLUMN) == []  # type: ignore[arg-type]
    checklist = second["checklist"]
    assert isinstance(checklist, dict)
    listed = entry_about(list(checklist["columns"]), _ROUTE_FOUR_COLUMN)
    assert len(listed) == 1, "the checklist does not list the column in round two"
    assert code_choice(listed[0])["then_the_description_publishes"] == said_in_round_one["then_the_description_publishes"]
    answer_and_run(rounds, [(_ROUTE_FOUR_COLUMN, asking.ANSWER_CODE)])
    in_two = outputs(rounds)
    differing = [name for name in ("description", "summary", "twin", "questions") if in_one[name] != in_two[name]]
    assert differing == [], f"code in round one is not the checklist's code in round two: {differing}"


def test_route_four_offers_code_in_round_one_and_it_is_the_checklists_code(tmp_path: pathlib.Path) -> None:
    """Lane HX3's gate case (plan P4-D420)."""
    route_four_case(tmp_path)


def test_mutant_route_four_not_offering_code_is_seen(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The person question offers `keep` and `identifier` alone, as before plan P4-D420."""
    real = asking._person_choices
    monkeypatch.setattr(asking, "_person_choices", lambda role, floor, offers_code=False: real(role, floor, False))
    with pytest.raises(AssertionError, match="code not offered in round one"):
        route_four_case(tmp_path)


def test_mutant_code_answered_and_still_held_is_seen(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A `code` answered to the person question read as no answer: the column stays held."""
    real = asking._entry_answer

    def entry_answer(entry: object, place: str, carried: bool = False) -> "tuple[str, str, tuple[str, ...]] | None":
        read = real(entry, place, carried)
        if read is not None and read[1] == asking.ANSWER_CODE and asking.ANSWER_KEEP in read[2]:
            return None
        return read

    monkeypatch.setattr(asking, "_entry_answer", entry_answer)
    with pytest.raises(AssertionError, match="the column still held"):
        route_four_case(tmp_path)


def test_mutant_route_four_answers_not_kept_is_seen(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The file the answering run writes carries no `answered_before` (plan P4-D408)."""
    monkeypatch.setattr(asking, "answered_before", lambda given: [])
    with pytest.raises(AssertionError, match="answered_before lost"):
        route_four_case(tmp_path)


asking_person_questions = asking.person_questions


def code_standing(*arguments: object, **named: object) -> "list[asking.Question]":
    """The mutant: route four's question stands on `code`, so a blank or Enter declares a code."""
    found = asking_person_questions(*arguments, **named)  # type: ignore[arg-type]
    return [
        dataclasses.replace(one, taken=asking.ANSWER_CODE)
        if asking.ANSWER_CODE in [choice.answer for choice in one.choices]
        else one
        for one in found
    ]


def test_mutant_code_standing_is_seen(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Route four's question standing on `code` (skeptic 1 of lane HX3, item 2)."""
    monkeypatch.setattr(asking, "person_questions", code_standing)
    with pytest.raises(AssertionError, match="the standing answer is not keep"):
        route_four_case(tmp_path)


def test_mutant_the_file_prefilling_code_is_seen(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The questions file writes `code` beside route four's question as if the person had said it."""
    real = asking._record_entry

    # The file is rendered from its records since lane S5b (plan P4-D441).
    def prefilled(record: results.Asked) -> "dict[str, object]":
        entry = real(record)
        if asking.ANSWER_CODE in [offer.answer for offer in record.offers]:
            entry["your_answer"] = asking.ANSWER_CODE
        return entry

    monkeypatch.setattr(asking, "_record_entry", prefilled)
    with pytest.raises(AssertionError, match="the file answers for the person"):
        route_four_case(tmp_path)


def test_route_fours_other_answers_move_no_byte(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Unanswered (held) and `keep`: the description, summary and twin of the question without `code`."""
    found: "dict[str, dict[str, dict[str, bytes]]]" = {}
    real = asking._person_choices
    for offers in ("with_code", "without_code"):
        with monkeypatch.context() as patched:
            if offers == "without_code":
                patched.setattr(asking, "_person_choices", lambda role, floor, offers_code=False: real(role, floor, False))
            unanswered = diagnoses_table(tmp_path / offers / "unanswered")
            assert profile(unanswered) == 0
            kept_table = diagnoses_table(tmp_path / offers / "keep")
            assert profile(kept_table) == 0
            answer_and_run(kept_table, [_ROUTE_FOUR_PERSON, (_ROUTE_FOUR_COLUMN, asking.ANSWER_KEEP)])
            found[offers] = {"unanswered": outputs(unanswered), "keep": outputs(kept_table)}
    held = json.loads(found["with_code"]["unanswered"]["description"])
    assert [one["role"] for one in held["columns"] if one["name"] == _ROUTE_FOUR_COLUMN] == ["identifier"]
    for route in ("unanswered", "keep"):
        for name in ("description", "summary", "twin"):
            assert found["with_code"][route][name] == found["without_code"][route][name], (route, name)
    # Only the open question's list of answers differs; once answered, the file too is the same.
    assert found["with_code"]["unanswered"]["questions"] != found["without_code"]["unanswered"]["questions"]
    assert found["with_code"]["keep"]["questions"] == found["without_code"]["keep"]["questions"]


# -- K-S3-66: over the zoo and the cases above ------------------------------


_MEASURED = (
    "tables",
    "tables_answered_over_rounds",
    "answers",
    "answers_lost",
    "byte_differences",
    "not_in_one_round",
    "failed_runs",
    "twins_refused_on_both_routes",
    "cases",
)


def measure_table(table: Table, answerer: Answerer, found: "dict[str, int]") -> None:
    """One zoo table answered in rounds and in one round, counted into `found` (K-S3-66).

    A twin is compared only where both routes wrote one; a table whose
    generation refuses on both routes is counted under
    `twins_refused_on_both_routes` and its other three files compared, so
    a regression keeping both twins from being written cannot read as
    identical bytes (Codex's review of lane AQ, item 5).
    """
    found["tables"] += 1
    rounds = in_rounds(table, answerer)
    if not rounds.exits or any(code != 0 for code in rounds.exits):
        found["failed_runs"] += 1
        return
    if len(rounds.given) >= 2:
        found["tables_answered_over_rounds"] += 1
    several = written(table)
    clear(table)
    code = in_one_round(table, rounds.standing)
    if code is None:
        found["not_in_one_round"] += 1
        return
    if code != 0:
        found["failed_runs"] += 1
        return
    verdict = judged(several, written(table))
    if verdict.failed:
        found["failed_runs"] += 1
        return
    found["answers"] += len(rounds.standing)
    found["answers_lost"] += len(rounds.lost)
    found["byte_differences"] += verdict.differing
    found["twins_refused_on_both_routes"] += 1 if verdict.refused_on_both else 0


def measure(folder: pathlib.Path) -> "dict[str, int]":
    """K-S3-66's values: answers lost between rounds, and one-round-versus-rounds byte differences.

    Over every table of E0a's zoo (tests/health_zoo.py) at 600 rows,
    answered by the zoo's own general answerer until a round answers
    nothing new, and over this file's answered cases: the nine-question
    table cut three ways over three rounds, its later answers changing
    earlier ones, its declarations typed in round one, the refusal's two
    runs, and the third round's four (a measurement beside its comma, a
    comma beside counted dates, a typed default and a column named like a
    file question). A table whose answers cannot be given in one round,
    or whose answering run fails, is counted apart and never as a pass;
    so is a table whose twin both routes refuse to write.
    """
    found = {name: 0 for name in _MEASURED}

    def counted(rounds: Rounds, differs: "dict[str, bool]") -> None:
        found["answers"] += len(rounds.standing)
        found["answers_lost"] += len(rounds.lost)
        found["byte_differences"] += sum(1 for one in differs.values() if one)

    for kind in zoo.TABLES:
        table, answerer = zoo_table(folder / kind.name, kind.name)
        measure_table(table, answerer, found)
    for cut in ((3, 6), (1, 8), (5, 7)):
        found["cases"] += 1
        table = mixed_table(folder / f"mixed-{cut[0]}-{cut[1]}")
        plan = [list(_MIXED_ANSWERS[: cut[0]]), list(_MIXED_ANSWERS[cut[0] : cut[1]]), list(_MIXED_ANSWERS[cut[1] :])]
        try:
            rounds, differs = compare(table, by_round(plan))
        except AssertionError:
            found["failed_runs"] += 1
            continue
        counted(rounds, differs)
    for case in (
        test_codes_in_dates_read_either_way_answered_after_the_order,
        test_answers_typed_in_round_one_are_kept_by_the_file,
        test_a_later_round_changes_an_earlier_answer,
        test_a_later_answer_to_the_question_asked_again_wins,
        test_the_refusals_two_runs_keep_the_first_runs_answer,
        test_a_measurement_and_its_comma_are_both_kept,
        test_a_comma_beside_counted_dates_keeps_the_dates,
        test_a_typed_default_replaces_a_kept_answer,
        test_a_column_named_like_a_file_question_is_not_a_reading,
    ):
        found["cases"] += 1
        try:
            case(folder / case.__name__)
        except AssertionError:
            found["byte_differences"] += 1
    return found

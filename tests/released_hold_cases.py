"""Three columns a rule of batch 4o released that the heads before it held (the orchestrator's LANE I4m RULINGS 21).

Codex's own cases of its review of batch 4o, at the owner's table floor -- 20,000
rows, and 1,000 people where a person has several rows -- run through the shipped
command, nobody at the keyboard, each question of the column answered as the case
says, round by round. The shapes are invented: record numbers in a column whose
name says age; given names of two letters beside a declared person column; a code
column whose rare value is a person's key. And a fourth, the independent verify's
shape B6 of the fix round (LANE I4m RULINGS 27 (1)): first initials that are all
yes-no letters, beside a flag of one yes-no pair. Nothing here reads a real table.
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import pathlib

from synthtwin import cli, parsing

ROWS = 20_000
PEOPLE = 1_000
ROWS_A_PERSON = 20
# Codex's case 1: record numbers `00001` to `02000`, each on ten rows.
AGE_KEY = "age_key"
# Codex's case 2: person 0 `Ed`, the others by their place modulo four.
NAMES = ("Al", "Bo", "Jo", "Li")
RARE_NAME = "Ed"
# Codex's case 3: person 0's key `8888`, the others' `100001` up; the code
# column holds `8888` on person 0's rows and `201` to `204` and `A` on the others'.
KEY_OF_PERSON_0 = "8888"
CODES = ("201", "202", "203", "204", "A")
# The verify's shape B6: persons 0 and 1 `F`, the others `Y`, `N` or `T` by
# their place modulo three.
INITIALS = ("Y", "N", "T")
RARE_INITIAL = "F"


def record_numbers_named_as_ages() -> "tuple[list[str], list[list[str]], str, list[str]]":
    """Case 1: one column `age_key`, `00001` to `02000` each on ten rows, no person column."""
    rows = [[f"{number:05d}"] for number in range(1, 2001) for _row in range(10)]
    return [AGE_KEY], rows, AGE_KEY, []


def record_numbers_named_as_ages_beside_people() -> "tuple[list[str], list[list[str]], str, list[str]]":
    """Case 1 beside a declared person column: each person's own record number `1` to `1000` in `age_key`."""
    rows = [
        [f"{100000 + who}", f"{who + 1}"] for who in range(PEOPLE) for _row in range(ROWS_A_PERSON)
    ]
    return ["patient_key", AGE_KEY], rows, AGE_KEY, ["--identifier", "patient_key"]


def record_numbers_within_the_age_reach() -> "tuple[list[str], list[list[str]], str, list[str]]":
    """The sibling sweep's case beside case 1: `age_key` holding `001` to `125`, each on 160 rows, no person column.

    Its cells read in years reach the ages, so lane SH's top-code reaches the
    column its open question holds (LANE I4m RULINGS 21 (6)).
    """
    rows = [[f"{number:03d}"] for number in range(1, 126) for _row in range(160)]
    return [AGE_KEY], rows, AGE_KEY, []


def given_names() -> "tuple[list[str], list[list[str]], str, list[str]]":
    """Case 2: 1,000 declared people on 20 rows each; `kind` holds a two-letter given name a person."""
    rows = [
        [f"{100000 + who}", RARE_NAME if who == 0 else NAMES[who % len(NAMES)]]
        for who in range(PEOPLE)
        for _row in range(ROWS_A_PERSON)
    ]
    return ["patient_key", "kind"], rows, "kind", ["--identifier", "patient_key"]


def a_code_that_is_a_key() -> "tuple[list[str], list[list[str]], str, list[str]]":
    """Case 3: person 0's key `8888` is also person 0's rare value of `kind`."""
    rows: "list[list[str]]" = []
    for who in range(PEOPLE):
        for row in range(ROWS_A_PERSON):
            key = KEY_OF_PERSON_0 if who == 0 else f"{100000 + who}"
            code = KEY_OF_PERSON_0 if who == 0 else CODES[(who * ROWS_A_PERSON + row) % len(CODES)]
            rows += [[key, code]]
    return ["patient_key", "kind"], rows, "kind", ["--identifier", "patient_key"]


def yes_no_letters_as_initials() -> "tuple[list[str], list[list[str]], str, list[str]]":
    """Shape B6: 1,000 declared people on 20 rows each; `first_initial` holds `Y`, `N` or `T` a person, `F` two."""
    rows = [
        [f"{300000 + who}", RARE_INITIAL if who < 2 else INITIALS[who % len(INITIALS)]]
        for who in range(PEOPLE)
        for _row in range(ROWS_A_PERSON)
    ]
    return ["patient_key", "first_initial"], rows, "first_initial", ["--identifier", "patient_key"]


def a_yes_no_flag_with_a_rare_third_level() -> "tuple[list[str], list[list[str]], str, list[str]]":
    """1,000 declared people on 20 rows each; `flag` holds `U` for persons 0 to 4, the others `Y` or `N` by place."""
    rows = [
        [f"{300000 + who}", "U" if who < 5 else ("Y", "N")[who % 2]]
        for who in range(PEOPLE)
        for _row in range(ROWS_A_PERSON)
    ]
    return ["patient_key", "flag"], rows, "flag", ["--identifier", "patient_key"]


@contextlib.contextmanager
def _nobody_at_the_keyboard():  # type: ignore[no-untyped-def]
    asked = cli._there_is_somebody_to_ask
    cli._there_is_somebody_to_ask = lambda: False
    try:
        yield
    finally:
        cli._there_is_somebody_to_ask = asked


def _asked_of(questions: pathlib.Path, column: str) -> "list[dict[str, object]]":
    if not questions.is_file():
        return []
    document = json.loads(questions.read_text(encoding="utf-8"))
    return [entry for entry in document.get("asked", []) if entry.get("column") == column]


def run(
    folder: pathlib.Path,
    case: "tuple[list[str], list[list[str]], str, list[str]]",
    answers: "tuple[str, ...]" = (),
    seed: int = 0,
    typed: "tuple[str, ...]" = (),
) -> "dict[str, object]":
    """Profile, answer the column's questions one round an answer, generate; what each step wrote.

    ``answers``: each round's answer, given to every question put to the
    column and still unanswered. ``typed``: more of the command line.
    Returns the exits, the questions put to the column in each round (each
    with what it offered), the description's text and the column's block,
    the real cells and the twin's.
    """
    header, rows, column, declared = case
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / "t.csv"
    with open(source, "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    questions = folder / "t-questions.json"
    exits: "list[int]" = []
    put: "list[list[list[str]]]" = []
    screen = io.StringIO()
    with _nobody_at_the_keyboard(), contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        exits += [cli.main(["profile", f"{source}", "--out-dir", f"{folder}", "--replace"] + declared + list(typed))]
        for answer in answers:
            entries = _asked_of(questions, column)
            put += [[[f"{one['answer']}" for one in entry.get("answers_you_can_give", [])] for entry in entries]]  # type: ignore[union-attr]
            document = json.loads(questions.read_text(encoding="utf-8"))
            for entry in document["asked"]:
                if entry.get("column") == column and not f"{entry.get('your_answer') or ''}":
                    entry["your_answer"] = answer
            given = folder / "answers.json"
            given.write_text(json.dumps(document), encoding="utf-8", newline="\n")
            exits += [cli.main(["profile", f"{source}", "--out-dir", f"{folder}", "--replace", "--answers", f"{given}"]
                               + declared + list(typed))]
        put += [[[f"{one['answer']}" for one in entry.get("answers_you_can_give", [])]  # type: ignore[union-attr]
                 for entry in _asked_of(questions, column) if not f"{entry.get('your_answer') or ''}"]]
        twin_folder = folder / "twin"
        twin_folder.mkdir(exist_ok=True)
        exits += [cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir", f"{twin_folder}",
                            "--seed", f"{seed}", "--replace"])]
    text = (folder / "t-profile.json").read_text(encoding="utf-8")
    block = [one for one in json.loads(text)["columns"] if one["name"] == column][0]
    with open(twin_folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
        table = list(csv.reader(handle))
    place = table[0].index(column)
    return {
        "exits": exits,
        "put": put,
        "text": text,
        "block": block,
        "real": [row[header.index(column)] for row in rows],
        "twin": [row[place] for row in table[1:]],
        "twin_rows": table[1:],
        "twin_header": table[0],
    }


def equal_cells(real: "list[str]", twin: "list[str]") -> int:
    """Twin cells, present, spelled exactly as a present real cell: a set of the real, each twin cell read once."""
    present = {cell for cell in real if cell.strip()}
    return sum(1 for cell in twin if cell.strip() and cell in present)


def merged_cells(real: "list[str]", twin: "list[str]") -> int:
    """Twin cells, present, whose merged key (`parsing.merged_key`) is a present real cell's: `00018` and `18` are one."""
    keys = {parsing.merged_key(cell) for cell in real if cell.strip()}
    keys.discard("")
    return sum(1 for cell in twin if cell.strip() and parsing.merged_key(cell) in keys)

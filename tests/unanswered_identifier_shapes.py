"""Long tables carrying a Safe Harbor identifier on each patient's rows (plan P4-D401).

Shared by `tests/test_privacy_unanswered_identifiers.py` (600 rows) and
`tools/measurements/kpi_unanswered_identifiers.py` (600 and 20,000 rows,
ledger K-S3-64), so the gate and the ledger measure the same tables the
same way.

EACH TABLE is several rows per patient: 44 patients, their rows drawn with
weights 1 to 25, and one column holding the patient's identifier of one
kind beside a test name and a value. Nothing is answered, so `synthtwin
profile` runs as a script does -- told so explicitly, whatever terminal
the measurement is started from -- asks its questions in the questions
file, and goes on.

THE SHAPES (`HELD`), each put a question offering `identifier` and so
held back until it is answered: record, health plan, account and
beneficiary numbers in every layout the first reviews of lane HX
measured (letters and figures, six to fourteen figures, dashed, padded,
grouped with commas or spaces), telephone numbers in six layouts,
social security numbers, e-mail addresses, a numeric patient key beside
missing cells, five-figure ZIP codes, device identifiers, a study
subject code of five figures, and a register of record numbers with one
short number among them. `BESIDE`: three tables of 150 patients whose
record number is DECLARED a person column, carrying an e-mail address, a
beneficiary identifier or a telephone number beside it. `STATED`: a
patient's name, a street address and a full birth date, which no
question flags -- a stated limit owned by lane HX2 (plan P4-D401).

WHAT IS COUNTED (`count_real`, a pure function the gate also tests on
cases made for it). In the description, its summary, the questions file and
the screen: each real value written whole anywhere -- or its figures
written as a number, without separators or leading zeros -- and each
FRAGMENT of one: a run of five or more letters and figures out of a real
value, or the text every real value opens with. In the twin's column:
cells holding a real value, or its figures, anywhere inside them, and the
fragments found inside its cells.
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import pathlib
import random
import re

from synthtwin import cli

PATIENTS = 44
PATIENTS_BESIDE = 150
SEED = 20261016

_FIRST = ("James", "Maria", "Robert", "Linda", "Michael", "Patricia", "David",
          "Jennifer", "William", "Elizabeth", "Joseph", "Susan", "Thomas",
          "Jessica", "Charles", "Sarah", "Daniel", "Karen")
_LAST = ("Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
         "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
         "Wilson", "Anderson", "Taylor", "Moore")
_STREETS = ("Maple St", "Oak Ave", "Pine Rd", "Cedar Ln", "Elm St",
            "Washington Blvd", "Lake Dr")
_BENEFICIARY_LETTERS = "ACDEFGHJKMNPQRTUVWXY"


def _beneficiary(draw: random.Random) -> str:
    written = ""
    for place in "9AX9AX9AA99":
        if place == "9":
            written += f"{draw.randint(1 if not written else 0, 9)}"
        elif place == "A" or draw.random() < 0.5:
            written += _BENEFICIARY_LETTERS[draw.randrange(len(_BENEFICIARY_LETTERS))]
        else:
            written += f"{draw.randint(0, 9)}"
    return written


def _patient(kind: str, place: int, draw: random.Random) -> str:
    first = _FIRST[draw.randrange(len(_FIRST))]
    last = _LAST[draw.randrange(len(_LAST))]
    area = f"{draw.randint(201, 989)}"
    exchange = f"{draw.randint(200, 999)}"
    line = f"{draw.randint(0, 9999):04d}"
    grouped = f"{123456789 + 1013 * place:,}"
    shapes = {
        "record": f"REC{10000000 + 7 * place:08d}",
        "plan": f"XKH{draw.randint(100000000, 999999999)}",
        "email": f"{first.lower()}.{last.lower()}{draw.randint(1, 99)}@mailhost.org",
        "email_upper": f"{first.upper()}.{last.upper()}{draw.randint(1, 99)}@MAILHOST.ORG",
        "account": f"{draw.randint(1000000000, 9999999999)}",
        "phone": f"{area}-{exchange}-{line}",
        "phone_space": f"{area} {exchange} {line}",
        "phone_plus": f"+1-{area}-{exchange}-{line}",
        "phone_dot": f"{area}.{exchange}.{line}",
        "phone_paren": f"({area}) {exchange}-{line}",
        "phone10": f"{area}{exchange}{line}",
        "ssn": f"{draw.randint(100, 899):03d}-{draw.randint(10, 99):02d}-{draw.randint(1000, 9999):04d}",
        "ssn9": f"{draw.randint(100, 899):03d}{draw.randint(10, 99):02d}{draw.randint(1000, 9999):04d}",
        "subject": f"P{place + 1:05d}",
        "beneficiary": _beneficiary(draw),
        "rec6": f"REC{draw.randint(100000, 999999)}",
        "letter6": f"E{draw.randint(100000, 999999)}",
        "account_dash": f"AC-{draw.randint(1000, 9999)}-{draw.randint(1000, 9999)}",
        "dash9": f"{draw.randint(100, 999)}-{draw.randint(100, 999)}-{draw.randint(100, 999)}",
        "plain6": f"{draw.randint(100000, 999999)}",
        "plain7": f"{draw.randint(1000000, 9999999)}",
        "npi": f"1{draw.randint(0, 999999999):09d}",
        "padded": f"{1000000 + place:09d}",
        "grouped": grouped,
        "spaced": grouped.replace(",", " "),
        "durable": f"{100000 + place}",
        "zip": f"0{2100 + 7 * place:04d}",
        "udi": f"0088483803{5600 + 13 * place:04d}",
        "mixed": f"REC{10000000 + 7 * place:08d}",
        "name": f"{first} {last}",
        "address": f"{draw.randint(10, 9899)} {_STREETS[draw.randrange(len(_STREETS))]}",
        "dob": f"{draw.randint(1930, 2005)}-{draw.randint(1, 12):02d}-{draw.randint(1, 28):02d}",
    }
    if kind.endswith("_beside"):
        return shapes[kind[: -len("_beside")]]
    return shapes[kind]


HELD = ("record", "plan", "email", "email_upper", "account", "phone",
        "phone_space", "phone_plus", "phone_dot", "phone_paren", "phone10",
        "ssn", "ssn9", "subject", "beneficiary", "rec6", "letter6",
        "account_dash", "dash9", "plain6", "plain7", "npi", "padded",
        "grouped", "spaced", "durable", "zip", "udi", "mixed")
BESIDE = ("email_beside", "beneficiary_beside", "phone_beside")
STATED = ("name", "address", "dob")

# The one short number among a register of record numbers (`mixed`).
SHORT_AMONG_LONG = "P00017"
# The key a numeric patient key writes for an unknown patient (`durable`).
UNKNOWN_KEY = "-1"


def _cell(value: str) -> str:
    """A CSV cell, quoted where it holds the delimiter."""
    return f'"{value}"' if "," in value else value


def write_table(folder: pathlib.Path, kind: str, rows: int) -> "tuple[pathlib.Path, list[str]]":
    """The table, written as a CSV file; its path and its different identifiers."""
    draw = random.Random(SEED + len(kind))
    beside = kind.endswith("_beside")
    patients = PATIENTS_BESIDE if beside else PATIENTS
    people: "list[str]" = []
    for place in range(patients):
        one = _patient(kind, place, draw)
        while one in people:
            one = _patient(kind, place, draw)
        people += [one]
    weights = [1.0 + (place % 9) * 3 for place in range(patients)]
    lines = [f"patient,{kind},test,value" if beside else f"{kind},test,value"]
    seen: "dict[str, bool]" = {}
    for row in range(rows):
        place = draw.choices(range(patients), weights)[0]
        who = people[place]
        if kind == "mixed" and row == 0:
            who = SHORT_AMONG_LONG
        if kind == "durable" and draw.random() < 0.02:
            who = UNKNOWN_KEY
        else:
            seen[who] = True
        test = ("Sodium", "Potassium", "Glucose")[draw.randrange(3)]
        value = f"{draw.uniform(3, 150):.1f}"
        if beside:
            lines += [f"REC{20000000 + 7 * place:08d},{_cell(who)},{test},{value}"]
        else:
            lines += [f"{_cell(who)},{test},{value}"]
    path = folder / f"{kind}_long.csv"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return path, sorted(seen)


def _runs(value: str) -> "list[str]":
    """Each run of five or more letters and figures in a value."""
    found: "list[str]" = []
    run = ""
    for character in value + " ":
        if character.isascii() and character.isalnum():
            run = run + character
            continue
        if len(run) >= 5:
            found += [run]
        run = ""
    return found


def _opening(values: "list[str]") -> str:
    """The letters every value opens with, two or more of them, or nothing."""
    shared = ""
    first = values[0]
    for place, character in enumerate(first):
        if not character.isalpha() or any(
            len(one) <= place or one[place] != character for one in values
        ):
            break
        shared = shared + character
    return shared if len(shared) >= 2 else ""


_SEPARATORS = " ,.-()+"


def _as_number(value: str) -> str:
    """A value of figures and separators written as a number, or nothing.

    `02100` is printed `2100`, `123,456,789` is printed `123456789`: the
    figures alone without leading zeros, of a value of five figures or
    more.
    """
    figures = ""
    for character in value:
        if "0" <= character <= "9":
            figures += character
        elif character not in _SEPARATORS:
            return ""
    if len(figures) < 5:
        return ""
    return figures.lstrip("0")


def _found_in(needle: str, text: str) -> bool:
    """Whether a value's text, or its figures as a number, stands anywhere in a text."""
    if needle in text:
        return True
    number = _as_number(needle)
    if not number:
        return False
    return re.search(f"(?<![0-9]){number}(?![0-9])", text) is not None


def _opening_in(opening: str, text: str) -> bool:
    """Whether the shared opening stands in a text with no letter against it.

    `REC` in `REC10000007` or in a published prefix `"REC"`, never inside
    a word of the page such as `RECORD` or `HELD BACK`.
    """
    return re.search(f"(?<![A-Za-z]){re.escape(opening)}(?![A-Za-z])", text) is not None


def count_real(
    real: "list[str]", texts: "list[str]", cells: "list[str]"
) -> "dict[str, int]":
    """What of the real values the published texts and the twin's cells carry.

    ``texts``: the description, its summary, the questions file and the
    screen; ``cells``: the twin's column. Every comparison is by
    substring, so a value wrapped in other characters is still found.
    """
    fragments: "dict[str, bool]" = {}
    for value in real:
        for run_of in _runs(value):
            fragments[run_of] = True
    opening = _opening(real) if real else ""
    whole = [value for value in real if any(_found_in(value, text) for text in texts)]
    in_texts = [one for one in fragments if any(_found_in(one, text) for text in texts)]
    if opening and any(_opening_in(opening, text) for text in texts):
        in_texts += [opening]
    twin_cells = 0
    twin_fragments: "dict[str, bool]" = {}
    seen_cells: "dict[str, bool]" = {}
    for cell in cells:
        if any(_found_in(value, cell) for value in real):
            twin_cells += 1
        if cell in seen_cells:
            continue
        seen_cells[cell] = True
        for one in fragments:
            if _found_in(one, cell):
                twin_fragments[one] = True
        if opening and _opening_in(opening, cell):
            twin_fragments[opening] = True
    return {
        "description_values": len(whole),
        "description_fragments": len(in_texts),
        "twin_cells": twin_cells,
        "twin_fragments": len(twin_fragments),
    }


@contextlib.contextmanager
def nobody_at_the_keyboard():
    """A scripted run, whatever terminal the measurement was started from.

    Redirecting Python's output leaves the process's own handles on the
    terminal, so `cli._there_is_somebody_to_ask` would still see a
    person and wait for one (Codex's review of lane HX, item 5); the
    measurement says who is there instead.
    """
    asked = cli._there_is_somebody_to_ask
    cli._there_is_somebody_to_ask = lambda: False
    try:
        yield
    finally:
        cli._there_is_somebody_to_ask = asked


def _csv_column(path: pathlib.Path, place: int) -> "list[str]":
    with open(path, encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    return [row[place] for row in rows[1:]]


def run(folder: pathlib.Path, kind: str, rows: int) -> "dict[str, object]":
    """Profile the table unanswered, generate seed 0, and count what is real."""
    table, real = write_table(folder, kind, rows)
    beside = kind.endswith("_beside")
    declared = ["--identifier", "patient"] if beside else []
    screen = io.StringIO()
    with nobody_at_the_keyboard():
        with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
            profiled = cli.main(["profile", f"{table}", "--out-dir", f"{folder}",
                                 "--replace"] + declared)
        described = folder / f"{kind}_long-profile.json"
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            generated = cli.main(["generate", f"{described}", "--out-dir", f"{folder}",
                                  "--seed", "0", "--replace"])
    texts = {
        name: (folder / name).read_text(encoding="utf-8")
        for name in (f"{kind}_long-profile.json", f"{kind}_long-profile.txt",
                     f"{kind}_long-questions.json")
    }
    document = json.loads(texts[f"{kind}_long-profile.json"])
    block = [one for one in document["columns"] if one["name"] == kind][0]
    questions = json.loads(texts[f"{kind}_long-questions.json"])
    asked = [entry for entry in questions["asked"] if entry["column"] == kind]
    cells = _csv_column(folder / f"{kind}_long-twin.csv", 1 if beside else 0)
    counted = count_real(real, list(texts.values()) + [screen.getvalue()], cells)
    seen: "dict[str, object]" = {
        "profile_exit": profiled,
        "generate_exit": generated,
        "different": len(real),
        "role": block["role"],
        "evidence": block["detection_evidence"],
        "forced_identifiers": document["settings"]["forced_identifiers"],
        "person_columns": document["settings"]["person_columns"],
        "asked": [[c["answer"] for c in entry["answers_you_can_give"]] for entry in asked],
        "read_as_now": [entry["read_as_now"] for entry in asked],
        "screen": screen.getvalue(),
        "twin_sample": sorted(set(cells))[:3],
    }
    seen.update(counted)
    return seen

"""Long tables carrying a Safe Harbor identifier on each patient's rows (plan P4-D401).

Shared by `tests/test_privacy_unanswered_identifiers.py` (600 rows) and
`tools/measurements/kpi_unanswered_identifiers.py` (600 and 20,000 rows,
ledger K-S3-64), so the gate and the ledger measure the same tables the
same way.

EACH TABLE is several rows per patient: 44 patients, their rows drawn with
weights 1 to 25, and one column holding the patient's identifier of one
kind beside a test name and a value. Nothing is declared and nothing is
answered, so `synthtwin profile` runs as a script does, asks its questions
in the questions file, and goes on.

THE SHAPES. Six are held back until their question is answered -- the
person question (a record number, a health plan number, an e-mail
address), the fixed-width question (an account number of ten figures)
and the two-numbers question on a column written as telephone or social
security numbers. Four are STATED LIMITS no general rule reaches without
hiding columns that identify nobody (lane CODES-2's allowlist owns them;
wave6/ZOO/PLAN.md section 2.3): a patient's name, a street address and a
full birth date, which no question flags, and a study subject code of
five figures (`P00017`), which the person question reaches but which is
written as the code registers it also reaches are (`I10`, `HCC102`).

WHAT IS COUNTED, for one table. In the description, its summary and the
questions file: each real value written whole anywhere, and in the
column's own block each FRAGMENT of one -- a run of five or more letters
and figures out of a real value, or the text every real value opens with.
In the twin's column: cells holding a real value, and the fragments of
real values found inside its cells, the shared opening included.
"""

from __future__ import annotations

import contextlib
import io
import json
import pathlib
import random

from synthtwin import cli

PATIENTS = 44
SEED = 20261016

_FIRST = ("James", "Maria", "Robert", "Linda", "Michael", "Patricia", "David",
          "Jennifer", "William", "Elizabeth", "Joseph", "Susan", "Thomas",
          "Jessica", "Charles", "Sarah", "Daniel", "Karen")
_LAST = ("Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
         "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
         "Wilson", "Anderson", "Taylor", "Moore")
_STREETS = ("Maple St", "Oak Ave", "Pine Rd", "Cedar Ln", "Elm St",
            "Washington Blvd", "Lake Dr")


def _patient(kind: str, place: int, draw: random.Random) -> str:
    first = _FIRST[draw.randrange(len(_FIRST))]
    last = _LAST[draw.randrange(len(_LAST))]
    if kind == "mrn":
        return f"MRN{10000000 + 7 * place:08d}"
    if kind == "plan":
        return f"XKH{draw.randint(100000000, 999999999)}"
    if kind == "email":
        return f"{first.lower()}.{last.lower()}{draw.randint(1, 99)}@mailhost.org"
    if kind == "account":
        return f"{draw.randint(1000000000, 9999999999)}"
    if kind == "phone":
        return (f"{draw.randint(201, 989)}-{draw.randint(200, 999)}-"
                f"{draw.randint(0, 9999):04d}")
    if kind == "ssn":
        return (f"{draw.randint(100, 899):03d}-{draw.randint(10, 99):02d}-"
                f"{draw.randint(1000, 9999):04d}")
    if kind == "subject":
        return f"P{place + 1:05d}"
    if kind == "name":
        return f"{first} {last}"
    if kind == "address":
        return f"{draw.randint(10, 9899)} {_STREETS[draw.randrange(len(_STREETS))]}"
    return f"{draw.randint(1930, 2005)}-{draw.randint(1, 12):02d}-{draw.randint(1, 28):02d}"


HELD = ("mrn", "plan", "email", "account", "phone", "ssn")
STATED = ("name", "address", "dob", "subject")


def write_table(folder: pathlib.Path, kind: str, rows: int) -> "tuple[pathlib.Path, list[str]]":
    """The table, written as a CSV file; its path and its different identifiers."""
    draw = random.Random(SEED + len(kind))
    people = []
    for place in range(PATIENTS):
        one = _patient(kind, place, draw)
        while one in people:
            one = _patient(kind, place, draw)
        people += [one]
    weights = [1.0 + (place % 9) * 3 for place in range(PATIENTS)]
    lines = [f"{kind},test,value"]
    seen: "dict[str, bool]" = {}
    for _row in range(rows):
        who = draw.choices(people, weights)[0]
        seen[who] = True
        test = ("Sodium", "Potassium", "Glucose")[draw.randrange(3)]
        lines += [f"{who},{test},{draw.uniform(3, 150):.1f}"]
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


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        yield


def run(folder: pathlib.Path, kind: str, rows: int) -> "dict[str, object]":
    """Profile the table unanswered, generate seed 0, and count what is real."""
    table, real = write_table(folder, kind, rows)
    screen = io.StringIO()
    with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        profiled = cli.main(["profile", f"{table}", "--out-dir", f"{folder}", "--replace"])
    described = folder / f"{kind}_long-profile.json"
    with _quiet():
        generated = cli.main(["generate", f"{described}", "--out-dir", f"{folder}",
                              "--seed", "0", "--replace"])
    texts = {
        name: (folder / name).read_text(encoding="utf-8")
        for name in (f"{kind}_long-profile.json", f"{kind}_long-profile.txt",
                     f"{kind}_long-questions.json")
    }
    document = json.loads(texts[f"{kind}_long-profile.json"])
    block = [one for one in document["columns"] if one["name"] == kind][0]
    block_text = json.dumps(block, sort_keys=True)
    questions = json.loads(texts[f"{kind}_long-questions.json"])
    asked = [entry for entry in questions["asked"] if entry["column"] == kind]
    opening = _opening(real)
    fragments: "dict[str, bool]" = {}
    for value in real:
        for run_of in _runs(value):
            fragments[run_of] = True
    whole = [value for value in real if any(value in text for text in texts.values())]
    in_block = [one for one in fragments if one in block_text]
    if opening and opening in block_text:
        in_block += [opening]
    cells = [line.split(",")[0] for line in
             (folder / f"{kind}_long-twin.csv").read_text(encoding="utf-8").splitlines()[1:]]
    known = set(real)
    twin_cells = sum(1 for cell in cells if cell in known)
    twin_fragments: "dict[str, bool]" = {}
    for cell in set(cells):
        for run_of in _runs(cell):
            if run_of in fragments:
                twin_fragments[run_of] = True
        if opening and cell.startswith(opening):
            twin_fragments[opening] = True
    return {
        "profile_exit": profiled,
        "generate_exit": generated,
        "different": len(real),
        "role": block["role"],
        "evidence": block["detection_evidence"],
        "forced_identifiers": document["settings"]["forced_identifiers"],
        "person_columns": document["settings"]["person_columns"],
        "asked": [[c["answer"] for c in entry["answers_you_can_give"]] for entry in asked],
        "read_as_now": [entry["read_as_now"] for entry in asked],
        "description_values": len(whole),
        "description_fragments": len(in_block),
        "twin_cells": twin_cells,
        "twin_fragments": len(twin_fragments),
        "screen": screen.getvalue(),
    }


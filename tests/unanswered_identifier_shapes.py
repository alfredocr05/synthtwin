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
short number among them; and, after the second repair's reviews, numeric
patient keys route four of the person rule reaches (drawn from one to
three million, across a power of ten, beside `0`, nines, `-99`, `-1` on
40 % of rows or `UNKNOWN`, exported as `100001.0`, of varying width, or
grouped by points) and registers route three reaches (an extension after
a telephone number, a spaced social security number, an internet or web
address, sixteen figures in four groups, an e-mail address after a name
or beside one `not given`). `BESIDE`: three tables of 150 patients whose
record number is DECLARED a person column, carrying an e-mail address, a
beneficiary identifier or a telephone number beside it. `COUNTED` (lane
HX2, plan P4-D406): a health plan or account number beside a declared
person column, and a patient's name, a street address or a full birth
date beside a patient key whose person question is open -- held by the
count in people. `STATED`: a name, a street address and a full birth date
on a long table with no subject column, which no question flags and no
count in people reaches (plan P4-D406 item (a)).

WHAT IS COUNTED (`count_real`, a pure function the gate also tests on
cases made for it). In the description, its summary, the questions file and
the screen: each real value written whole anywhere -- or its figures
written as a number, without separators or leading zeros -- and each
FRAGMENT of one: a run of five or more letters and figures out of a real
value, or the text every real value opens with -- and a value's longest
run of five figures or more written as a number. A value of figures
alone counts only with no figure or point against it, so a decimal of
another column is not one. In the twin's column:
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

import persons_counted

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


def _patient_more(kind: str, place: int, draw: random.Random) -> str:
    """The shapes the verify and the tripwire of lane HX's repair measured.

    Drawn apart from `_patient`, so every shape there keeps its table.
    """
    area = f"{draw.randint(201, 989)}"
    exchange = f"{draw.randint(200, 999)}"
    line = f"{draw.randint(0, 9999):04d}"
    if kind == "randkey":
        return f"{draw.randint(1, 3000000)}"
    if kind == "mixw":
        return f"{9900 + 13 * place}"
    if kind in ("zerokey", "nines"):
        return f"{100000 + 211 * place}"
    if kind in ("key_m99", "key_m1_40", "key_word"):
        return f"{100000 + place}"
    if kind == "key_point0":
        return f"{100000 + place}.0"
    if kind == "varkey":
        return f"{draw.randint(1000, 99999999)}"
    if kind == "dotted9":
        return f"{123456789 + 1013 * place:,}".replace(",", ".")
    if kind == "phone_ext":
        return f"{area}-{exchange}-{line} x{draw.randint(10, 99)}"
    if kind == "ssn_space":
        return (f"{draw.randint(100, 899):03d} {draw.randint(10, 99):02d} "
                f"{draw.randint(1000, 9999):04d}")
    if kind == "ip":
        return f"10.{draw.randint(0, 255)}.{draw.randint(0, 255)}.{draw.randint(1, 254)}"
    if kind == "url":
        return f"https://portal.example.org/p/{draw.randint(10000, 99999)}"
    if kind == "card16":
        return " ".join(f"{draw.randint(1000, 9999)}" for _group in range(4))
    if kind == "email_angle":
        return f"Pat {place} <pat{place}.x{draw.randint(1, 99)}@mailhost.org>"
    if kind == "email_one_bad":
        return f"user{place}.x{draw.randint(1, 99)}@mailhost.org"
    if kind == "record2":
        return f"ACC{30000000 + 11 * place:08d}"
    return f"XKH{draw.randint(100000000, 999999999)}"


def _patient(kind: str, place: int, draw: random.Random) -> str:
    base = _base(kind)
    if base in MORE:
        return _patient_more(base, place, draw)
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
    return shapes[_base(kind)]


# The shapes `_patient_more` writes (lane HX's second repair).
MORE = ("randkey", "mixw", "zerokey", "nines", "key_m99", "key_m1_40",
        "key_word", "key_point0", "varkey", "dotted9", "phone_ext",
        "ssn_space", "ip", "url", "card16", "email_angle", "email_one_bad",
        "record2", "plan2")

HELD = ("record", "plan", "email", "email_upper", "account", "phone",
        "phone_space", "phone_plus", "phone_dot", "phone_paren", "phone10",
        "ssn", "ssn9", "subject", "beneficiary", "rec6", "letter6",
        "account_dash", "dash9", "plain6", "plain7", "npi", "padded",
        "grouped", "spaced", "durable", "zip", "udi", "mixed",
        "randkey", "mixw", "zerokey", "nines", "key_m99", "key_m1_40",
        "key_word", "key_point0", "varkey", "dotted9", "phone_ext",
        "ssn_space", "ip", "url", "card16", "email_angle", "email_one_bad")
BESIDE = ("email_beside", "beneficiary_beside", "phone_beside")
# COUNTED IN PEOPLE (lane HX2, plan P4-D406): values no question flags,
# on a long table with a subject column -- a health plan or account
# number beside a DECLARED person column, and a name, a street address or
# a full birth date beside a patient key whose person question is OPEN
# (`_open`: 44 patients, nothing declared; `_ten`: ten patients, fewer than
# the floor's number of keys, lane HX2's first repair). Every value is held
# by one patient, so none is published and the twin writes none.
#
# ...and beside a patient key ANOTHER identity question holds (`_keyzero`,
# lane HX2's skeptic, round 2, item 1): 150 patients keyed by a number of
# seven figures padded with zeros (`0001013`), which the codes-or-
# measurements question is put to and not the person question -- a full
# birth date beside it, and a name beside it written without its zeros on
# about half the rows.
#
# ...and VISIT DATES beside that key with nothing attached to it (`visit_
# keyzero`, lane HX2's combined verify, item 1): five visit dates a patient,
# on lab rows only, so no column names the key's people and only the literal
# rule -- every held key that repeats is a subject -- counts the dates in
# them.
COUNTED = ("plan2_beside", "record2_beside", "name_open", "address_open",
           "dob_open", "name_ten", "dob_ten", "dob_keyzero", "name_keyzero",
           "visit_keyzero")
# The visit dates each patient of a `visit_` table holds.
VISITS_A_PATIENT = 5
# The patients of a `_ten` table.
PATIENTS_TEN = 10
# The STATED shapes: a name, a street address and a full birth date on a
# long table with NO subject column -- the value is the only thing that
# says who the rows are, nothing is declared and no person question is
# put -- so there are no people to count in (plan P4-D406, item (a)).
STATED = ("name", "address", "dob")

# THE HELD SHAPES WHOSE TWIN FAILS ITS OWN VALIDATION, each a stated limit
# of the generator for a DECLARED record number too (plan P4-D401):
# `-1` for nobody (CODES-1 part C), a telephone layout opening `+`, and a
# key written `100001.0` whose twin writes a figure after the point.
VALIDATION_LIMITS = ("durable", "key_m1_40", "phone_plus", "key_point0")

# What each key shape writes for an unknown patient, and on what share
# of its rows (`write_table`).
PLACEHOLDERS = {"durable": ("-1", 0.02), "zerokey": ("0", 0.03),
                "nines": ("999999999", 0.03), "key_m99": ("-99", 0.02),
                "key_m1_40": ("-1", 0.40), "key_word": ("UNKNOWN", 0.02)}

# The one short number among a register of record numbers (`mixed`).
SHORT_AMONG_LONG = "P00017"
# The key a numeric patient key writes for an unknown patient (`durable`).
UNKNOWN_KEY = "-1"


def _base(kind: str) -> str:
    """The shape a kind writes: `plan2_beside`, `name_open` and `name_ten` write `plan2` and `name`."""
    for ending in ("_beside", "_open", "_ten", "_keyzero"):
        if kind.endswith(ending):
            return kind[: -len(ending)]
    return kind


def _beside(kind: str) -> bool:
    """Whether the table carries a patient key beside the shape's column."""
    return (kind.endswith("_beside") or kind.endswith("_open") or kind.endswith("_ten")
            or kind.endswith("_keyzero"))


def _cell(value: str) -> str:
    """A CSV cell, quoted where it holds the delimiter."""
    return f'"{value}"' if "," in value else value


def write_table(folder: pathlib.Path, kind: str, rows: int) -> "tuple[pathlib.Path, list[str]]":
    """The table, written as a CSV file; its path and its different identifiers."""
    draw = random.Random(SEED + len(kind))
    beside = _beside(kind)
    patients = (PATIENTS_BESIDE if kind.endswith("_beside") or kind.endswith("_keyzero")
                else PATIENTS)
    if kind.endswith("_ten"):
        patients = PATIENTS_TEN
    people: "list[str]" = []
    visits: "list[list[str]]" = []
    for place in range(patients):
        if _base(kind) == "visit":
            visits += [[f"{draw.randint(2023, 2024)}-{draw.randint(1, 12):02d}-"
                        f"{draw.randint(1, 28):02d}" for _visit in range(VISITS_A_PATIENT)]]
            people += [f"{place}"]
            continue
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
        if visits:
            who = visits[place][draw.randrange(VISITS_A_PATIENT)]
        if kind == "mixed" and row == 0:
            who = SHORT_AMONG_LONG
        if kind == "email_one_bad" and row == 0:
            who = "not given"
        elif kind in PLACEHOLDERS and draw.random() < PLACEHOLDERS[kind][1]:
            who = PLACEHOLDERS[kind][0]
        else:
            seen[who] = True
        test = ("Sodium", "Potassium", "Glucose")[draw.randrange(3)]
        value = f"{draw.uniform(3, 150):.1f}"
        key = f"REC{20000000 + 7 * place:08d}"
        if kind.endswith("_keyzero"):
            key = f"{1000 + 13 * place:07d}"
            if kind == "name_keyzero" and draw.random() < 0.5:
                key = key.lstrip("0")
        if beside:
            lines += [f"{key},{_cell(who)},{test},{value}"]
        else:
            lines += [f"{_cell(who)},{test},{value}"]
    path = folder / f"{kind}_long.csv"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    if kind == "key_point0":
        # `100001.0` is the key `100001`, and found as that.
        return path, sorted(value[: -len(".0")] for value in seen)
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


def _longest_figures(value: str) -> str:
    """A value's longest run of figures, leading zeros off, where five figures or more."""
    longest = ""
    run = ""
    for character in value + " ":
        if "0" <= character <= "9":
            run = run + character
            continue
        if len(run.lstrip("0")) > len(longest):
            longest = run.lstrip("0")
        run = ""
    return longest if len(longest) >= 5 else ""


def _found_in(needle: str, text: str) -> bool:
    """Whether a value's text, or its figures as a number, stands anywhere in a text.

    AND THE FIGURES OF A VALUE WRITTEN BESIDE LETTERS (lane HX's
    tripwire, item 5): `ACC30000484` read as an affixed number is printed
    `"mode": 30000484.0`, so its longest run of five figures or more is
    looked for as a whole number too -- with no figure or point before
    it, so a decimal of another column does not count.
    """
    if needle.isascii() and needle.isdigit():
        # A value of figures alone stands with no figure or point against
        # it: `9991` inside a decimal of another column, `82.34100000000001`,
        # is no key published.
        if re.search(f"(?<![0-9.]){needle}(?![0-9])", text) is not None:
            return True
    elif needle in text:
        return True
    number = _as_number(needle)
    if number:
        return re.search(f"(?<![0-9.]){number}(?![0-9])", text) is not None
    figures = _longest_figures(needle)
    if not figures:
        return False
    return re.search(f"(?<![0-9.]){figures}(?![0-9])", text) is not None


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


def _csv_column(path: pathlib.Path, place: int, delimiter: str = ",") -> "list[str]":
    with open(path, encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle, delimiter=delimiter))
    return [row[place] for row in rows[1:]]


def run(folder: pathlib.Path, kind: str, rows: int) -> "dict[str, object]":
    """Profile the table unanswered, generate seed 0, and count what is real."""
    table, real = write_table(folder, kind, rows)
    beside = _beside(kind)
    declared = ["--identifier", "patient"] if kind.endswith("_beside") else []
    screen = io.StringIO()
    with nobody_at_the_keyboard():
        with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
            profiled = cli.main(["profile", f"{table}", "--out-dir", f"{folder}",
                                 "--replace"] + declared)
        described = folder / f"{kind}_long-profile.json"
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            generated = cli.main(["generate", f"{described}", "--out-dir", f"{folder}",
                                  "--seed", "0", "--replace"])
            # ...and the twin is judged against its own description (lane
            # HX's tripwire, item 4: a held census the twin cannot meet).
            validated = cli.main(["validate", f"{described}", "--twin",
                                  f"{folder / (kind + '_long-twin.csv')}",
                                  "--out-dir", f"{folder}", "--replace"])
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
    written = cells
    # A COLUMN OF DATES DESCRIBED AT A GRAIN OR HELD WITH VALID DATES (plan
    # P4-D417): its published points are the STARTS of buckets the floor's
    # number of people hold, and its twin's cells are draws inside them or
    # inside the method's fixed span, never values of the table (method
    # G7.13). A real date that is itself a bucket's start stands in the
    # description as that bucket, and a twin's date equal to a real one by
    # chance is no value written as itself: both are counted apart.
    grain = block.get("time_grain")
    drawn = 0
    starts: "list[str]" = []
    if isinstance(grain, dict):
        named = persons_counted.bucket_names(grain)
        at_the_grain = persons_counted.at_the_grain(real, block)
        starts = [
            value for value, start in zip(real, at_the_grain)
            if (value == start and grain["rung"] != "held") or value in named
        ]
        counted_cells = count_real(real, [], cells)
        drawn = counted_cells["twin_cells"]
        cells = []
    counted = count_real(
        [value for value in real if value not in starts],
        list(texts.values()) + [screen.getvalue()],
        cells,
    )
    seen: "dict[str, object]" = {
        "profile_exit": profiled,
        "generate_exit": generated,
        "validate_exit": validated,
        "different": len(real),
        "role": block["role"],
        "evidence": block["detection_evidence"],
        "forced_identifiers": document["settings"]["forced_identifiers"],
        "person_columns": document["settings"]["person_columns"],
        "asked": [[c["answer"] for c in entry["answers_you_can_give"]] for entry in asked],
        "read_as_now": [entry["read_as_now"] for entry in asked],
        "screen": screen.getvalue(),
        "twin_sample": sorted(set(written))[:3],
        "twin_cells_drawn": drawn,
        "bucket_starts_published": len(starts),
    }
    seen.update(counted)
    return seen


# THE SAFE HARBOR NUMBER SHAPES (lane SH, plan P4-D427), each a column of
# ZIP codes or ages beside a row key `pid` (unique but in `age_person`),
# nobody answering.
#
# ZIP CODES (`ZIPS`), counted by `count_real` as every held shape is:
# - ZR-b's verify 2, item 1 (`zip5word*`): 70 ZIP codes drawn with weights
#   1/(k+1)^1.1, with a leading zero (`02100`...) or without (`52240`...),
#   beside `UNKNOWN` once or `HOMELESS` three times. Measured on b85200be
#   at 600 rows: read as a count, 38 or 39 real ZIPs printed; 44 at 20,000.
# - the orchestrator's LANE SH addenda 1 (1) and (3), 3 (1), 4 and 5, and
#   skeptic 1 of lane SH, items 4 and 8, each measured LIVE at 20,000 rows
#   on b85200be or 28e5d2f5: every role (`zip_binary`, `zip_constant`,
#   `zip4_binary`, `zip4_constant`), ZIPs that lost their leading zero
#   beside five-figure ones (`zip_mixed`), placeholders of any share
#   (`zip_pad_minus99`, `zip_mixed_minus99`, `zip4_minus9999`,
#   `zip4_999999`), the unknown-ZIP code 99999 (`zip4_99999`,
#   `zip4_99999x11`), words of any share in a label role
#   (`zip_pad_unknown`, `zip_pad_unknown35`, `zip_mixed_unknown`,
#   `zip4_99999_unknown`), ZIP+4 cells (`zip_plus4`), and Codex's
#   plus-signed ZIPs (`zip_plus_sign`).
# - the orchestrator's LANE SH ADDENDUM 6 (the hold follows the offer):
#   60 ten-figure account numbers repeating, beside a nine-figure one on
#   every 150th row (`acct_date_count`), put the date-count question
#   alone -- two widths, so no fixed-width question -- which held nothing
#   before (lane HX held that question only beside the width question);
#   no ZIP and no age, so only that question's hold reaches it.
#
# AGES (`AGES`; 45 CFR 164.514(b)(2)(i)(C)), counted by `run_safe_harbor`
# against the same table with every age from 90 to 125 written 90:
# - ages 18 to 89 with 3 % drawn from 90 to 103 (the orchestrator's probe
#   of 2026-10-23), plain, beside `999` once or twenty times, or beside
#   `-9` on 2 % of rows (`ages`, `ages999`, `ages999x20`, `ages-9`);
# - the addenda 1 (1) and (2), 2 (1) and (2) and 3 (2): every role
#   (`age_binary`, `age_constant`), an outlier (`age_outlier`,
#   `age_126`), placeholders of any share (`age_999share`,
#   `age_minus1share`, `age_888`, `age_gauss_minus1`), ages in a label
#   role (`age_years`, `age_unk`, `age_words800`, `age_years_words`);
# - skeptic 1 of lane SH, items 9 and 12: ages beside an open person
#   question, each value above 89 held by at least eleven people at
#   20,000 rows (`age_person`), and a plus sign on every fiftieth age
#   (`age_plus`); and its item 5, one cell `07` (`age_padded07`): P4-D401's
#   padded question holds the column, its held block read from the
#   top-coded cells, and no Safe Harbor question is put beside it.
#
# THE SECOND REPAIR OF LANE SH (the combined verify on 9ccb6bc7,
# wave6/SH-verify.md), each measured live there at 20,000 rows:
# - item 2: every cell a ZIP+4 with a varied +4 (`zipplus4_all`) was put
#   the two-numbers question AND the Safe Harbor question;
# - item 3: ages written with a decimal comma (`94,8`) in a `;` file, no
#   comma declared (`agescomma`), read as labels and printed `96,5`;
# - item 4: nine-figure ZIP+4 cells with no hyphen beside three `UNKNOWN`
#   (`zip9_unk`, padded `zip9pad_unk`) read as a count and printed rungs
#   opening with real ZIPs; their published nine-figure numbers are
#   counted by the ZIP they open with (`_zip_heads`);
# - item 7: ages beside four placeholders, `777`, `888`, `555` and `999`
#   on 6 % of the rows each (`ages4ph`), are reached only while the
#   all-nines `999` is set aside;
# - items 1 and 6, the column's other question answered
#   (`SAFE_HARBOR_ANSWERED`): NAACCR's Age at Diagnosis, three figures
#   padded, `999` unknown on 2 % (`naaccr`), answered `measurement` or
#   `code`; and ZIPs answered `code`, `measurement` or `keep` to the
#   date-count question (`zip5word52_unknown`), the person question
#   (`zip52_unknown40`, `UNKNOWN` on 40 % of rows) or the two-numbers
#   question (`zipplus4_30`, `zipplus4_1234`): the Safe Harbor question
#   is put and the column held until `no`.
ZIP_WORDS = ("zip5word_unknown", "zip5word_homeless", "zip5word52_unknown",
             "zip5word52_homeless")
ZIPS = ZIP_WORDS + (
    "zip_binary", "zip_constant", "zip_mixed", "zip_pad_minus99",
    "zip_mixed_minus99", "zip4_99999", "zip4_99999x11", "zip_plus4",
    "zip_plus_sign", "zip4_binary", "zip4_constant", "zip_pad_unknown",
    "zip_pad_unknown35", "zip_mixed_unknown", "zip4_99999_unknown",
    "zip4_minus9999", "zip4_999999", "acct_date_count", "zipplus4_all",
    "zip9_unk", "zip9pad_unk", "zipplus4_30",
)
# The shapes counted only once their column's other question is answered.
ZIPS_ANSWERED_ONLY = ("zip52_unknown40", "zipplus4_1234")
ZIP_KINDS = ZIPS + ZIPS_ANSWERED_ONLY
# ZIP+4 cells written as nine figures, counted by the ZIP they open with.
ZIP_NINE = ("zip9_unk", "zip9pad_unk")
AGES = (
    "ages", "ages999", "ages999x20", "ages-9", "age_binary", "age_constant",
    "age_outlier", "age_126", "age_999share", "age_minus1share", "age_888",
    "age_gauss_minus1", "age_years", "age_unk", "age_words800",
    "age_years_words", "age_person", "age_plus", "age_padded07", "ages4ph",
    "agescomma", "naaccr",
)
SAFE_HARBOR_NUMBERS = ZIPS + AGES
# Each shape whose column's other question is answered, with the answer:
# in the questions file where a question offers it -- the person question
# keeps its place beside the Safe Harbor question -- and typed where the
# Safe Harbor question is put first in place of the other (`--code`,
# `--measurement`).
SAFE_HARBOR_ANSWERED = (
    ("naaccr", "measurement"), ("naaccr", "code"),
    ("zip5word52_unknown", "code"), ("zip5word52_unknown", "measurement"),
    ("zip52_unknown40", "keep"), ("zip52_unknown40", "code"),
    ("zipplus4_30", "code"), ("zipplus4_1234", "code"),
)
# The answers an option types.
_TYPED = {"code": "--code", "measurement": "--measurement"}
# The tables written with `;` between their cells.
_SEMICOLON = ("agescomma",)
AGE_TOP_CODE = 90
AGE_CEILING = 125
# Validation limits of the held block (plan P4-D427, stated): at 20,000
# rows a column of ZIP-shaped numbers beside ONE word is published with
# `all_whole_numbers` false beside every cell counted in figures (the
# census line absorbs the one), and the held generator writes whole
# numbers only, so the twin misses that one fact (exit 3); owner CODES-1
# part C, as `VALIDATION_LIMITS` are.
SAFE_HARBOR_HELD_LIMITS_AT_20000 = ("zip5word_unknown", "zip5word52_unknown", "ages4ph")
# ...and at 600 rows ZIP codes beside twenty ZIP+4 cells are held by
# P4-D401's person question, whose held twin writes the ZIP+4 layout and
# too few cells of the five-figure one (`forms.published.%%%%%`): the
# same exit 3 on b85200be, before this lane (wave6/SH/r1/base-zip4.log);
# owner CODES-1 part C, as above.
SAFE_HARBOR_HELD_LIMITS_AT_600 = ("zip_plus4", "ages4ph", "agescomma")
# ...and ages beside four placeholders, each on 6 % of the rows
# (`ages4ph`): the twin misses the published `p90`, which lies among the
# placeholders, top-coded or not -- the same exit 3 answered `no` and on
# b85200be (wave6/SH-verify.md, "for the orchestrator"); a generation
# limit outside lane SH, named there. And at 600 rows, ages written with
# an undeclared decimal comma read as labels (`agescomma`): the twin
# misses `n_numeric`, `n_not_numeric` and the form `%%,%` -- the same
# three on the table written with every age above 89 as `90,0`, which
# no top-code touches (wave6/SH/r2), a label generation limit outside
# lane SH.

def _an_age(draw: random.Random) -> int:
    """18 to 89, or 90 to 103 for 3 % of draws."""
    return draw.choice(range(90, 104)) if draw.random() < 0.03 else draw.randint(18, 89)


def _word(place: int) -> str:
    """A word of letters alone, different for each place: `wab`, `wac`..."""
    letters = ""
    left = place
    for _ in range(3):
        letters = chr(ord("a") + left % 26) + letters
        left = left // 26
    return "w" + letters


def _shares(rows: int, *parts: float) -> "list[int]":
    """Rows split by shares, the last part taking what is left."""
    counts = [int(rows * part) for part in parts[:-1]]
    return counts + [rows - sum(counts)]


def _zip_cells(kind: str, rows: int, draw: random.Random) -> "tuple[list[str], list[str]]":
    """A ZIP shape's cells, and the real ZIP codes among them."""
    padded = [f"0{2100 + 7 * k:04d}" for k in range(40)]
    four = [f"{2100 + 7 * k}" for k in range(40)]
    mixed = ["2100", "2107", "52240", "52247"]
    cells: "list[str]" = []
    if kind in ("zip5word_unknown", "zip5word_homeless", "zip5word52_unknown",
                "zip5word52_homeless", "zip_plus4"):
        word, times = {"zip5word_unknown": ("UNKNOWN", 1), "zip5word_homeless": ("HOMELESS", 3),
                       "zip5word52_unknown": ("UNKNOWN", 1),
                       "zip5word52_homeless": ("HOMELESS", 3),
                       "zip_plus4": ("UNKNOWN", 1)}[kind]
        lead = kind in ("zip5word_unknown", "zip5word_homeless")
        zips = [f"0{2100 + 7 * k:04d}" if lead else f"{52240 + 7 * k}" for k in range(70)]
        weights = [1.0 / (k + 1) ** 1.1 for k in range(70)]
        for row in range(rows):
            cells += [word if row < times else draw.choices(zips, weights)[0]]
        if kind == "zip_plus4":
            for row in range(1, 21):
                cells[row] = f"{zips[row % 7]}-{1000 + row}"
        real = sorted({cell for cell in cells if cell != word})
        return cells, real
    zips52 = [f"{52240 + 7 * k}" for k in range(40)]
    if kind in ("zipplus4_all", "zipplus4_30", "zipplus4_1234", "zip52_unknown40"):
        for _row in range(rows):
            zip_code = draw.choice(zips52)
            if kind == "zipplus4_all" or (kind == "zipplus4_30" and draw.random() < 0.3):
                cells += [f"{zip_code}-{draw.randint(1000, 9999)}"]
            elif kind == "zipplus4_1234":
                cells += [f"{zip_code}-1234"]
            else:
                cells += [zip_code]
        if kind == "zip52_unknown40":
            cells[: rows * 2 // 5] = ["UNKNOWN"] * (rows * 2 // 5)
            draw.shuffle(cells)
        return cells, sorted(set(zips52) & {cell[:5] for cell in cells})
    if kind in ZIP_NINE:
        heads = padded if kind == "zip9pad_unk" else zips52
        cells = [f"{draw.choice(heads)}{draw.randint(1000, 9999)}" for _ in range(rows - 3)]
        cells += ["UNKNOWN"] * 3
        draw.shuffle(cells)
        return cells, sorted(set(heads) & {cell[:5] for cell in cells})
    if kind == "acct_date_count":
        accounts = [f"{1400000000 + draw.randrange(10 ** 8)}" for _ in range(60)]
        cells = [f"{123400000 + row}" if row % 150 == 0 else accounts[row % 60]
                 for row in range(rows)]
    elif kind == "zip_plus_sign":
        cells = ["UNKNOWN" if row < 3 else f"+{52200 + row % 80}" for row in range(rows)]
    elif kind == "zip_binary":
        cells = ["02100" if row % 2 else "02107" for row in range(rows)]
    elif kind == "zip_constant":
        cells = ["02100"] * rows
    elif kind == "zip4_binary":
        cells = ["2100" if row % 2 else "2107" for row in range(rows)]
    elif kind == "zip4_constant":
        cells = ["2100"] * rows
    elif kind == "zip_mixed":
        cells = [mixed[row % 4] for row in range(rows)]
    else:
        base, word, share = {
            "zip_pad_minus99": (padded, "-99", 0.35),
            "zip_mixed_minus99": (mixed, "-99", 0.35),
            "zip4_99999": (four, "99999", 0.05),
            "zip4_99999x11": (four, "99999", 11 / rows),
            "zip_pad_unknown": (padded, "UNKNOWN", 0.05),
            "zip_pad_unknown35": (padded, "UNKNOWN", 0.35),
            "zip_mixed_unknown": (mixed, "UNKNOWN", 0.05),
            "zip4_99999_unknown": (four, "99999", 0.05),
            "zip4_minus9999": (four, "-9999", 0.05),
            "zip4_999999": (four, "999999", 0.05),
        }[kind]
        zips_rows, word_rows = _shares(rows, 1 - share, share)
        if kind == "zip4_99999_unknown":
            zips_rows, word_rows, other_rows = _shares(rows, 0.9, 0.05, 0.05)
            cells = ([base[row % len(base)] for row in range(zips_rows)]
                     + [word] * word_rows + ["UNKNOWN"] * other_rows)
        else:
            cells = [base[row % len(base)] for row in range(zips_rows)] + [word] * word_rows
        draw.shuffle(cells)
    placeholders = ("UNKNOWN", "HOMELESS", "-99", "-9999", "999999", "99999")
    real = sorted({cell for cell in cells if cell not in placeholders})
    if kind == "zip4_99999x11" or kind == "zip4_99999":
        real = sorted({cell for cell in cells if cell != "99999"})
    return cells, real


def _age_cells(kind: str, rows: int, draw: random.Random) -> "list[str | tuple[int, str]]":
    """An age shape's cells: a text kept as written, or an age and its form."""
    cells: "list[str | tuple[int, str]]" = []
    if kind in ("ages", "ages999", "ages999x20", "ages-9"):
        placeholder, times, share = {"ages": ("", 0, 0.0), "ages999": ("999", 1, 0.0),
                                     "ages999x20": ("999", 20, 0.0),
                                     "ages-9": ("-9", 0, 0.02)}[kind]
        for row in range(rows):
            age = _an_age(draw)
            if row < times or (share and draw.random() < share):
                cells += [placeholder]
            else:
                cells += [(age, "{}")]
        return cells
    if kind == "naaccr":
        # NAACCR's Age at Diagnosis: three figures, `999` unknown.
        return ["999" if draw.random() < 0.02
                else (min(105, max(0, round(draw.gauss(64, 14)))), "{:03d}")
                for _ in range(rows)]
    if kind == "agescomma":
        return [(_an_age(draw), "{}," + f"{draw.randint(0, 9)}") for _ in range(rows)]
    if kind == "ages4ph":
        share = rows * 6 // 100
        cells = [(_an_age(draw), "{}") for _ in range(rows - 4 * share)]
        for placeholder in ("777", "888", "555", "999"):
            cells += [placeholder] * share
        draw.shuffle(cells)
        return cells
    if kind == "age_plus":
        return [(_an_age(draw), "+{}" if row % 50 == 0 else "{}") for row in range(rows)]
    if kind == "age_padded07":
        return ["07"] + [(_an_age(draw), "{}") for _ in range(rows - 1)]
    if kind == "age_person":
        for row in range(rows):
            if row % 2 == 0:
                age = _an_age(draw)
            cells += [(age, "{}")]
        return cells
    if kind == "age_binary":
        return [(60, "{}") if row % 2 else (95, "{}") for row in range(rows)]
    if kind == "age_constant":
        return [(95, "{}")] * rows
    if kind == "age_outlier":
        half = rows // 2
        cells = [(60, "{}")] * half + [(95, "{}")] * (rows - half - 1) + ["130"]
    elif kind == "age_126":
        cells = [(_an_age(draw), "{}") for _ in range(rows - 1)] + ["126"]
    elif kind in ("age_999share", "age_minus1share", "age_888", "age_unk"):
        word = {"age_999share": "999", "age_minus1share": "-1", "age_888": "888",
                "age_unk": "UNK"}[kind]
        low, high, rest = _shares(rows, 0.325, 0.325, 0.35)
        cells = [(60, "{}")] * low + [(95, "{}")] * high + [word] * rest
    elif kind == "age_gauss_minus1":
        ages, rest = _shares(rows, 0.6, 0.4)
        cells = [(min(104, max(18, round(draw.gauss(70, 14)))), "{}") for _ in range(ages)]
        cells += ["-1"] * rest
    elif kind == "age_years":
        cells = [(draw.randint(18, 104), "{} years") for _ in range(rows)]
    elif kind == "age_words800":
        low, high, rest = _shares(rows, 0.3, 0.3, 0.4)
        cells = [(60, "{}")] * low + [(95, "{}")] * high
        cells += [_word(place // 10) for place in range(rest)]
    elif kind == "age_years_words":
        ages, rest = _shares(rows, 0.65, 0.35)
        cells = [(draw.randint(18, 104), "{} years") for _ in range(ages)]
        cells += [_word(place // 10) for place in range(rest)]
    draw.shuffle(cells)
    return cells


def _written_age(cell: "str | tuple[int, str]", top_coded: bool) -> str:
    """One age cell as the table writes it, or as the top-code reads it."""
    if isinstance(cell, str):
        return cell
    age, form = cell
    if top_coded and AGE_TOP_CODE <= age <= AGE_CEILING:
        age = AGE_TOP_CODE
        if "," in form:
            # A decimal comma's fraction is written as zeros: `90,0`.
            form = form.split(",")[0] + ",0"
    return form.format(age)


def _decoy(value: str) -> str:
    """A ZIP written as another: each figure but a leading `0` moved by five, the form kept."""
    moved = ""
    for place, character in enumerate(value):
        if "0" <= character <= "9" and not (place == 0 and character == "0"):
            moved += f"{(int(character) + 5) % 10}"
        else:
            moved += character
    return moved


def write_safe_harbor_table(
    folder: pathlib.Path, kind: str, rows: int, top_coded: bool = False, decoy: bool = False
) -> "tuple[pathlib.Path, list[str]]":
    """A Safe Harbor number table as a CSV file; its path and the real values to look for.

    For ZIPs, the different ZIP codes written; for ages, the different
    ages above 90, to 125, written (an age of 90 is the top-code itself).
    With ``top_coded``, every age from 90 to 125 is written 90 in its own
    form -- the table the top-code reads. With ``decoy``, every ZIP is
    written as another of the same form (`_decoy`), placeholders kept.
    """
    draw = random.Random(SEED + len(kind))
    if kind in ZIP_KINDS:
        written, real = _zip_cells(kind, rows, draw)
        if decoy:
            named = set(real)
            written = [_decoy(cell) if cell in named else cell for cell in written]
    else:
        cells = _age_cells(kind, rows, draw)
        written = [_written_age(cell, top_coded) for cell in cells]
        real = sorted({f"{cell[0]}" for cell in cells
                       if not isinstance(cell, str) and AGE_TOP_CODE < cell[0] <= AGE_CEILING})
    keys = [f"P{row // 2:06d}" if kind == "age_person" else f"P{row:06d}"
            for row in range(rows)]
    between = ";" if kind in _SEMICOLON else ","
    lines = [f"pid{between}{kind}"] + [f"{key}{between}{cell}" for key, cell in zip(keys, written)]
    path = folder / f"{kind}_long.csv"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return path, real


# A fact a quality report names as missed.
_MISSED = re.compile(r"^\s+(\S+) \[[^\]]+\]: MISSED", re.M)


def _number_tokens(value: str, text: str) -> int:
    """How often a whole number stands in a text as itself, `103` or `103.0`."""
    return len(re.findall(f"(?<![0-9.]){value}(?:\\.0+)?(?![0-9.])", text))


def _answers_given(folder: pathlib.Path, table: pathlib.Path, kind: str, answer: str) -> "list[str]":
    """Profile unanswered, then write `answer` to the question on the column offering it.

    Where no question offers it -- the Safe Harbor question put first in
    place of the other -- the answer is typed instead.
    """
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["profile", f"{table}", "--out-dir", f"{folder}", "--replace"]) == 0
    written = json.loads((folder / f"{kind}_long-questions.json").read_text(encoding="utf-8"))
    given = 0
    for entry in written["asked"]:
        offered = [choice["answer"] for choice in entry["answers_you_can_give"]]
        if entry["column"] == kind and answer in offered:
            entry["your_answer"] = answer
            given += 1
    if not given:
        return [_TYPED[answer], kind]
    assert given == 1, written["asked"]
    answers = folder / "answers.json"
    answers.write_text(json.dumps(written), encoding="utf-8", newline="\n")
    return ["--answers", f"{answers}"]


def _profiled(
    folder: pathlib.Path, table: pathlib.Path, kind: str, answer: str = ""
) -> "dict[str, object]":
    """Profile, generate (seed 0) and validate the twin and the table itself, scripted.

    With ``answer``, the column's one question is first answered so, and
    the table profiled again with that file.
    """
    screen = io.StringIO()
    with nobody_at_the_keyboard():
        given = _answers_given(folder, table, kind, answer) if answer else []
        with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
            profiled = cli.main(["profile", f"{table}", "--out-dir", f"{folder}", "--replace"]
                                + given)
        described = folder / f"{kind}_long-profile.json"
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            generated = cli.main(["generate", f"{described}", "--out-dir", f"{folder}",
                                  "--seed", "0", "--replace"])
            validated = cli.main(["validate", f"{described}", "--twin",
                                  f"{folder / (kind + '_long-twin.csv')}",
                                  "--out-dir", f"{folder}", "--replace"])
            checked = folder / "real"
            checked.mkdir(exist_ok=True)
            validated_real = cli.main(["validate", f"{described}", "--twin", f"{table}",
                                       "--out-dir", f"{checked}", "--replace"])
    texts = {
        name: (folder / name).read_text(encoding="utf-8")
        for name in (f"{kind}_long-profile.json", f"{kind}_long-profile.txt",
                     f"{kind}_long-questions.json", f"{kind}_long-twin-report.txt",
                     f"{kind}_long-twin-quality.txt")
    }
    texts["real-quality"] = (checked / f"{kind}_long-quality.txt").read_text(encoding="utf-8")
    texts["screen"] = screen.getvalue().replace(f"{folder}", "<folder>")
    for name in texts:
        texts[name] = texts[name].replace(f"{folder}", "<folder>")
    return {"profile_exit": profiled, "generate_exit": generated,
            "validate_exit": validated, "validate_real_exit": validated_real,
            "texts": texts,
            "twin": _csv_column(folder / f"{kind}_long-twin.csv", 1,
                                ";" if kind in _SEMICOLON else ",")}


def _twin_ages_over(twin: "list[str]") -> int:
    """How many twin cells hold a number above 90, to 125, a unit word after it or not."""
    over = 0
    for cell in twin:
        found = re.fullmatch(r"\s*\+?([0-9]+(?:[.,][0-9]+)?)(?:\s*[A-Za-z]+)?\s*", f"{cell}")
        if found is not None and AGE_TOP_CODE < float(found.group(1).replace(",", ".")) <= AGE_CEILING:
            over += 1
    return over


def _zip_heads(heads: "list[str]", texts: "list[str]", cells: "list[str]") -> "dict[str, int]":
    """The published nine-figure numbers, and twin cells, that open with a real ZIP.

    A number is read with its leading zeros put back to nine figures
    (`21001234` is `021001234`), so a padded ZIP's head is found too.
    """
    named = set(heads)
    published = 0
    for text in texts:
        for number in re.findall(r"(?<![0-9.])([0-9]{8,9})(?:\.0+)?(?![0-9])", text):
            if number.rjust(9, "0")[:5] in named:
                published += 1
    twin = 0
    for cell in cells:
        figures = cell.strip()
        if figures.isdigit() and len(figures) in (8, 9) and figures.rjust(9, "0")[:5] in named:
            twin += 1
    return {"description_values": published, "twin_cells": twin}


def _count_zips(
    kind: str, real: "list[str]", texts: "list[str]", cells: "list[str]"
) -> "dict[str, int]":
    """`count_real`, and for nine-figure ZIP+4 cells the numbers opening with a real ZIP."""
    counted = count_real(real, texts, cells)
    if kind in ZIP_NINE:
        heads = _zip_heads(real, texts, cells)
        counted["description_values"] += heads["description_values"]
        counted["twin_cells"] += heads["twin_cells"]
    return counted


def run_safe_harbor(
    folder: pathlib.Path, kind: str, rows: int, answer: str = ""
) -> "dict[str, object]":
    """One Safe Harbor number shape profiled unanswered, generated and validated.

    With ``answer``, the column's other question is answered so first
    (`SAFE_HARBOR_ANSWERED`), the control table's too. ZIPs are counted as every held shape is (`count_real`). Ages are
    counted against the same table with every age from 90 to 125 written
    90, profiled in a folder of its own: an age above 90 counts as
    published where it stands in an output of the table more often than
    in the same output of that table (so a `100` of the page's own words
    is no age), the outputs that differ are counted as fragments, and
    twin cells above 90 as real cells.
    """
    table, real = write_safe_harbor_table(folder, kind, rows)
    seen = _profiled(folder, table, kind, answer)
    texts = seen["texts"]
    assert isinstance(texts, dict)
    document = json.loads(texts[f"{kind}_long-profile.json"])
    block = [one for one in document["columns"] if one["name"] == kind][0]
    questions = json.loads(texts[f"{kind}_long-questions.json"])
    asked = [entry for entry in questions["asked"] if entry["column"] == kind]
    twin = seen["twin"]
    assert isinstance(twin, list)
    found: "dict[str, object]" = {
        "profile_exit": seen["profile_exit"], "generate_exit": seen["generate_exit"],
        "validate_exit": seen["validate_exit"],
        "validate_real_exit": seen["validate_real_exit"],
        "different": len(real), "role": block["role"],
        "top_coded": block["top_coded"] if "top_coded" in block else None,
        "asked": [[c["answer"] for c in entry["answers_you_can_give"]] for entry in asked],
        "read_as_now": [entry["read_as_now"] for entry in asked],
        "screen": texts["screen"],
        "summary": texts[f"{kind}_long-profile.txt"],
        "real_quality": texts["real-quality"],
    }
    if kind in ZIP_KINDS:
        published = [texts[name] for name in texts if name != "real-quality"]
        cells = [f"{cell}" for cell in twin]
        counted = _count_zips(kind, real, published, cells)
        found.update(counted)
        if counted["twin_cells"]:
            # A MADE-UP VALUE EQUAL TO A REAL ONE BY CHANCE. A held column's
            # twin writes made-up record numbers spread over its layout's
            # whole range, drawn from the description alone; where one lands
            # on a real ZIP (Codex's `+52200` to `+52279` fill 80 of the
            # thousand numbers where one made-up value falls), the same
            # table with every ZIP written as another twins the same value:
            # such a value is counted apart, as a date bucket's start is.
            decoy_folder = folder / "decoy"
            decoy_folder.mkdir()
            decoy_table, _same = write_safe_harbor_table(decoy_folder, kind, rows, decoy=True)
            decoy_twin = set(f"{cell}" for cell in _profiled(decoy_folder, decoy_table, kind, answer)["twin"])  # type: ignore[arg-type]
            again = _count_zips(kind, real, [], [cell for cell in cells if cell not in decoy_twin])
            found["twin_cells_by_chance"] = counted["twin_cells"] - again["twin_cells"]
            found["twin_cells"] = again["twin_cells"]
            found["twin_fragments"] = again["twin_fragments"]
        return found
    control_folder = folder / "top-coded"
    control_folder.mkdir()
    control_table, _none = write_safe_harbor_table(control_folder, kind, rows, top_coded=True)
    control = _profiled(control_folder, control_table, kind, answer)
    control_texts = control["texts"]
    assert isinstance(control_texts, dict)
    leaked = [value for value in real
              if any(_number_tokens(value, texts[name]) > _number_tokens(value, control_texts[name])
                     for name in texts)]
    differing = [name for name in texts if texts[name] != control_texts[name]]
    quality = f"{kind}_long-twin-quality.txt"
    found.update({"twin_misses": sorted(set(_MISSED.findall(texts[quality]))),
                  "control_twin_misses": sorted(set(_MISSED.findall(control_texts[quality])))})
    found.update({"description_values": len(leaked), "description_fragments": len(differing),
                  "twin_cells": _twin_ages_over([f"{cell}" for cell in twin]),
                  "twin_fragments": 0, "differing": differing})
    return found

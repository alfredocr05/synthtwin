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
import time

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
# REGISTER LISTS (lane HX4, plan P4-D424): one to three record numbers a
# cell, separated by `;`, drawn from `LIST_KEYS` of them, on each of the
# 44 patients' rows -- six figures, six figures padded to seven, and `R`
# and six figures (the three forms lane ZR-a's second repair measured), and
# the six-figure form beside a DECLARED person column of 150 patients (lane
# HX2). The real values are the record numbers, not the cells.
#
# ...and the shapes lane HX4's repair 1 closed, each of which published
# record numbers on 6c566d3c: lists whose mark is drawn from `;`, `,` and
# `|` cell by cell (`reglistmix6`, `reglistmixR`: 40 of 40 at 20,000 rows,
# skeptic 1's item 1); ONE list cell among single record numbers
# (`reglistonce6`, `reglistonceR`: 40 of 40, item 2); a `;` closing each
# list cell (`reglisttrail6`: 1 of 40 at 600 rows, item 3); and
# comma-grouped keys separated by spaces (`reglistgrouped`, nine figures;
# Codex's item 1 measured `123,001` on 12 rows).
#
# ...and the shapes lane HX4's repair 2 closed, each of which published 40
# of 40 record numbers at 600 and 20,000 rows on 5cd84df6, every twin cell
# a real one (item 1 of its verify): ONE record number a cell closed by
# `;` (`reglistone6`), in square brackets with `R` (`reglistoneR`) and in
# quotes (`reglistquoted6`); and a record number and a word in every
# cell, `185380;pending` (`reglistword6`, item 2: 33 of 40 at 600 rows).
LISTED = ("reglist6", "reglist7", "reglistR", "reglist6_beside",
          "reglistmix6", "reglistmixR", "reglistonce6", "reglistonceR",
          "reglisttrail6", "reglistgrouped", "reglistone6", "reglistoneR",
          "reglistquoted6", "reglistword6")
# The register lists of one record number a cell (lane HX4's repair 2).
LISTED_ONE = ("reglistone6", "reglistoneR", "reglistquoted6", "reglistword6")
LIST_KEYS = 40
# ONE VALUE A ROW, OR IN SEQUENCE (lane HX5, plan P4-D436): a reference
# column of whole numbers, alone or after letters, standing on fewer than
# two rows a value, which no route of the person rule reaches (each asks
# from two rows a value) and the width question reaches only at one width
# of plain figures. Lane E0c's strict twin scan measured the first on
# ccebc947: `RPT` and six figures counting up, one a row, read as an
# affixed number and asked nothing -- its percentile ladder published, the
# twin writing the sequence again (598 of 600 real references, 19,998 of
# 20,000). `refseq` is that shape; `refrand` its references drawn at random;
# `refacc` `ACC` and six figures on about four rows in three (letters and
# five figures or more); `seqcross` plain figures counting up across a
# power of ten (99,701 up), so no width question is put; `seqdup` that run
# with its first number on the last row too (a run in sequence, not all
# different); `randall` plain figures of six and seven, drawn at random,
# one a row; and `seqm1` the plain run beside `-1` on about one row in
# fifty. Lane HX5's repair 1 (skeptic 1, items 2 to 4) adds the shapes that
# escaped its first head: `refspecimen`, eight letters before the figures;
# `refyear`, a pathology accession with its year (`S24-50001` up);
# `refsuffix`, a mark and a letter after the figures (`300001-A` up);
# `seqnines`, the plain run beside `-9999` on about one row in fifty; and
# `seqdecimal` and `refstray`, the plain run and `refseq` with one stray
# cell (`99708.5`, `RPT300008A`).
# Every value is its own patient-free record, so the real values are
# every cell's but the placeholders'.
ONE_A_ROW = ("refseq", "refrand", "refacc", "seqcross", "seqdup", "randall", "seqm1",
             "refspecimen", "refyear", "refsuffix", "seqnines", "seqdecimal", "refstray")
# What `seqm1` writes for a row with no reference, and on what share
# (`seqnines` writes `-9999` on the same share).
ONE_A_ROW_PLACEHOLDER = ("-1", 0.02)
ONE_A_ROW_NINES = "-9999"
# The STATED shapes: a name, a street address and a full birth date on a
# long table with NO subject column -- the value is the only thing that
# says who the rows are, nothing is declared and no person question is
# put -- so there are no people to count in (plan P4-D406, item (a)).
STATED = ("name", "address", "dob")

# THE HELD SHAPES WHOSE TWIN FAILS ITS OWN VALIDATION, each a stated limit
# of the generator for a DECLARED record number too (plan P4-D401):
# `-1` for nobody (CODES-1 part C), a telephone layout opening `+`, and a
# key written `100001.0` whose twin writes a figure after the point.
#
# ...and `reglistonce6` (lane HX4's repair 1): 599 cells of one six-figure
# key beside ONE list cell publish `all_whole_numbers` false beside a
# figures count absorbed to every cell (plan P4-D298), and the twin's
# search writes whole numbers alone, naming the fact in the twin's report;
# the same generator limit as `-1`'s, CODES-1 part C's (plan P4-D424).
# And `reglistgrouped`, read at 600 rows as free text, which publishes no
# value and is held by nothing: its twin misses `free_text.shape_forms` at
# exit 3 on the tree before lane HX4 too (measured on 4682d6ad), the forms
# lane FM's limit STATE names.
VALIDATION_LIMITS = ("durable", "key_m1_40", "phone_plus", "key_point0", "reglistonce6",
                     "reglistgrouped", "seqm1")

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


def _list_key(kind: str, draw: random.Random) -> str:
    """One record number of a register list (`LISTED`)."""
    base = _base(kind)
    if base == "reglist7":
        # Six figures padded to seven. Lane ZR-a's probe padded one to
        # 99,999 to seven figures, a room of 100,000 spellings where a
        # made-up record number meets a real one by chance (plan P4-D424).
        return f"0{draw.randint(100000, 999999)}"
    if base in ("reglistR", "reglistmixR", "reglistonceR", "reglistoneR"):
        return f"R{draw.randint(100000, 999999)}"
    if base == "reglistgrouped":
        # Nine figures grouped by commas: Codex measured six (`123,001`),
        # whose room of 900,000 spellings lets a made-up key equal a real
        # one by chance (7 twin cells at 20,000 rows, plan P4-D424); the
        # gate holds Codex's own six-figure cells apart.
        return f"{draw.randint(100000000, 999999999):,}"
    return f"{draw.randint(100000, 999999)}"


def _list_cell(kind: str, keys: "list[str]", row: int, draw: random.Random) -> "list[str]":
    """One row's record numbers of a register list, and the cell they are written in.

    Returned as the record numbers followed by the cell.
    """
    base = _base(kind)
    many = draw.randint(1, 3)
    if base in ("reglistonce6", "reglistonceR"):
        many = 2 if row == 0 else 1
    if base in LISTED_ONE:
        many = 1
    listed = draw.sample(keys, many)
    mark = ";"
    if base in ("reglistmix6", "reglistmixR"):
        mark = (";", ",", "|")[draw.randrange(3)]
    elif base == "reglistgrouped":
        mark = " "
    cell = mark.join(listed)
    if base == "reglisttrail6" and many > 1:
        cell = cell + mark
    if base == "reglistone6":
        cell = cell + mark
    elif base == "reglistoneR":
        cell = f"[{cell}]"
    elif base == "reglistquoted6":
        cell = f"'{cell}'"
    elif base == "reglistword6":
        cell = cell + mark + "pending"
    return listed + [cell]


def _cell(value: str) -> str:
    """A CSV cell, quoted where it holds the delimiter."""
    return f'"{value}"' if "," in value else value


def _one_a_row(kind: str, rows: int, draw: random.Random) -> "list[str]":
    """The column of a `ONE_A_ROW` table, a cell a row (lane HX5, plan P4-D436)."""
    if kind == "refseq":
        return [f"RPT{300001 + row}" for row in range(rows)]
    if kind == "refrand":
        return [f"RPT{value}" for value in draw.sample(range(100000, 1000000), rows)]
    if kind == "seqdup":
        cells = [f"{99701 + row}" for row in range(rows)]
        cells[rows - 1] = cells[0]
        return cells
    if kind == "refacc":
        people = draw.sample(range(100000, 1000000), (rows * 3) // 4)
        return [f"ACC{people[draw.randrange(len(people))]}" for _row in range(rows)]
    if kind == "seqcross":
        return [f"{99701 + row}" for row in range(rows)]
    if kind == "randall":
        return [f"{value}" for value in draw.sample(range(100000, 10000000), rows)]
    if kind == "refspecimen":
        return [f"SPECIMEN{300001 + row}" for row in range(rows)]
    if kind == "refyear":
        # From 50001, so no count the description publishes about the
        # held column at 20,000 rows (its rows, 20000; its lines, 20001)
        # equals one by coincidence, as from 10001 two do.
        return [f"S24-{50001 + row}" for row in range(rows)]
    if kind == "refsuffix":
        return [f"{300001 + row}-A" for row in range(rows)]
    if kind == "seqdecimal":
        cells = [f"{99701 + row}" for row in range(rows)]
        cells[7] = "99708.5"
        return cells
    if kind == "refstray":
        cells = [f"RPT{300001 + row}" for row in range(rows)]
        cells[7] = "RPT300008A"
        return cells
    unknown, share = ONE_A_ROW_PLACEHOLDER
    if kind == "seqnines":
        unknown = ONE_A_ROW_NINES
    return [unknown if draw.random() < share else f"{99701 + row}" for row in range(rows)]


def write_table(folder: pathlib.Path, kind: str, rows: int) -> "tuple[pathlib.Path, list[str]]":
    """The table, written as a CSV file; its path and its different identifiers."""
    draw = random.Random(SEED + len(kind))
    if kind in ONE_A_ROW:
        column = _one_a_row(kind, rows, draw)
        lines = [f"{kind},test,value"]
        for cell in column:
            test = ("Sodium", "Potassium", "Glucose")[draw.randrange(3)]
            lines += [f"{cell},{test},{draw.uniform(3, 150):.1f}"]
        path = folder / f"{kind}_long.csv"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        return path, sorted({cell for cell in column
                             if cell not in (ONE_A_ROW_PLACEHOLDER[0], ONE_A_ROW_NINES)})
    beside = _beside(kind)
    patients = (PATIENTS_BESIDE if kind.endswith("_beside") or kind.endswith("_keyzero")
                else PATIENTS)
    if kind.endswith("_ten"):
        patients = PATIENTS_TEN
    people: "list[str]" = []
    visits: "list[list[str]]" = []
    keys: "list[str]" = []
    if _base(kind) in LISTED:
        while len(keys) < LIST_KEYS:
            one = _list_key(kind, draw)
            if one not in keys:
                keys += [one]
    for place in range(patients):
        if _base(kind) == "visit":
            visits += [[f"{draw.randint(2023, 2024)}-{draw.randint(1, 12):02d}-"
                        f"{draw.randint(1, 28):02d}" for _visit in range(VISITS_A_PATIENT)]]
            people += [f"{place}"]
            continue
        if keys:
            # A register list's cells are drawn row by row, below.
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
        if keys:
            listed = _list_cell(kind, keys, row, draw)
            who = listed[-1]
            for one in listed[:-1]:
                seen[one] = True
        if kind == "mixed" and row == 0:
            who = SHORT_AMONG_LONG
        if kind == "email_one_bad" and row == 0:
            who = "not given"
        elif kind in PLACEHOLDERS and draw.random() < PLACEHOLDERS[kind][1]:
            who = PLACEHOLDERS[kind][0]
        elif not keys:
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


# THE PAIRWISE SEARCH IS QUADRATIC (lane HX5, plan P4-D436): a column of a
# value a row holds as many real values as rows, and every real value was
# searched for in every twin cell -- 20,000 by 20,000 regular expressions,
# about three and a half hours a table, and 26 of a 600-row run's 28
# seconds. At 20,000 cells or real values, or past this many pairs, the
# same counts are read by a counter LINEAR IN THE DATA (`_count_real_
# linear`, the orchestrator's rule of 2026-10-26): the real values and
# their fragments in two lookups, and each text and each different twin
# cell scanned once, through its own runs of figures and its own pieces
# of the lengths the lookups hold. The gate holds it equal to the
# pairwise search on every shape of this file.
_PAIRWISE_AT_MOST = 50_000
_LINEAR_FROM_ROWS = 20000


def _figure_runs(text: str) -> "set[str]":
    """The runs of figures a figures-only needle can stand as in `_found_in`.

    `(?<![0-9.])N(?![0-9])` with N figures alone holds exactly where N is a
    whole run of figures with no point before it.
    """
    found: "set[str]" = set()
    run = ""
    before = ""
    for character in text + " ":
        if "0" <= character <= "9":
            run = run + character
            continue
        if run and before != ".":
            found.add(run)
        run = ""
        before = character
    return found


def _keys_of(needle: str) -> "tuple[bool, set[str]]":
    """Whether `_found_in` searches the needle as text, and the figure runs it stands as."""
    keys: "set[str]" = set()
    as_text = not (needle.isascii() and needle.isdigit())
    if not as_text:
        keys.add(needle)
    number = _as_number(needle)
    if number:
        keys.add(number)
    else:
        figures = _longest_figures(needle)
        if figures:
            keys.add(figures)
    return as_text, keys


def _count_real_linear(
    real: "list[str]", texts: "list[str]", cells: "list[str]"
) -> "dict[str, int]":
    """`count_real`'s counts, each text and each different twin cell read once."""
    fragments: "dict[str, bool]" = {}
    for value in real:
        for run_of in _runs(value):
            fragments[run_of] = True
    opening = _opening(real) if real else ""
    # Each needle -- a real value ("real") or a fragment ("fragment") --
    # under the text `_found_in` looks for and under the runs of figures
    # it stands as.
    by_text: "dict[str, list[tuple[str, str]]]" = {}
    by_key: "dict[str, list[tuple[str, str]]]" = {}
    for group, needles in (("real", real), ("fragment", list(fragments))):
        for needle in needles:
            as_text, keys = _keys_of(needle)
            if as_text:
                listed = by_text.setdefault(needle, [])
                listed += [(group, needle)]
            for key in keys:
                listed = by_key.setdefault(key, [])
                listed += [(group, needle)]
    sizes = sorted({len(needle) for needle in by_text})

    def needles_in(text: str) -> "set[tuple[str, str]]":
        hits: "set[tuple[str, str]]" = set()
        for key in _figure_runs(text):
            hits.update(by_key.get(key, ()))
        for size in sizes:
            for start in range(len(text) - size + 1):
                found = by_text.get(text[start:start + size])
                if found:
                    hits.update(found)
        return hits

    published: "set[tuple[str, str]]" = set()
    for text in texts:
        published |= needles_in(text)
    whole = len([1 for group, _needle in published if group == "real"])
    in_texts = len([1 for group, _needle in published if group == "fragment"])
    if opening and any(_opening_in(opening, text) for text in texts):
        in_texts += 1
    twin_cells = 0
    twin_fragments: "dict[str, bool]" = {}
    holds_real: "dict[str, bool]" = {}
    for cell in cells:
        if cell not in holds_real:
            hits = needles_in(cell)
            holds_real[cell] = any(group == "real" for group, _needle in hits)
            for group, needle in hits:
                if group == "fragment":
                    twin_fragments[needle] = True
            if opening and _opening_in(opening, cell):
                twin_fragments[opening] = True
        if holds_real[cell]:
            twin_cells += 1
    return {
        "description_values": whole,
        "description_fragments": in_texts,
        "twin_cells": twin_cells,
        "twin_fragments": len(twin_fragments),
    }


def count_real(
    real: "list[str]", texts: "list[str]", cells: "list[str]", linear: "bool | None" = None
) -> "dict[str, int]":
    """What of the real values the published texts and the twin's cells carry.

    ``texts``: the description, its summary, the questions file and the
    screen; ``cells``: the twin's column. Every comparison is by
    substring, so a value wrapped in other characters is still found.
    ``linear`` reads the same counts by the counter linear in the data
    (`_count_real_linear`): by default at 20,000 cells or real values or
    more, or where the pairs pass `_PAIRWISE_AT_MOST`.
    """
    if linear is None:
        linear = (
            max(len(real), len(cells)) >= _LINEAR_FROM_ROWS
            or len(real) * max(len(cells), len(texts)) > _PAIRWISE_AT_MOST
        )
    if linear:
        return _count_real_linear(real, texts, cells)
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
    beside = _beside(kind)
    declared = ["--identifier", "patient"] if kind.endswith("_beside") else []
    screen = io.StringIO()
    # THE PRODUCT'S OWN TIME, apart from the counting (the orchestrator's
    # rule of 2026-10-26, point 5): profile, generate and validate, then
    # the count of what is real.
    started = time.perf_counter()
    with nobody_at_the_keyboard():
        with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
            profiled = cli.main(["profile", f"{table}", "--out-dir", f"{folder}",
                                 "--replace"] + declared, small_tables_refused=False)
        described = folder / f"{kind}_long-profile.json"
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            generated = cli.main(["generate", f"{described}", "--out-dir", f"{folder}",
                                  "--seed", "0", "--replace"])
            # ...and the twin is judged against its own description (lane
            # HX's tripwire, item 4: a held census the twin cannot meet).
            validated = cli.main(["validate", f"{described}", "--twin",
                                  f"{folder / (kind + '_long-twin.csv')}",
                                  "--out-dir", f"{folder}", "--replace"])
    product_seconds = time.perf_counter() - started
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
    real_written = set(real)
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
        # ...and the twin cells EQUAL to a real value as written (lane HX5,
        # plan P4-D436), beside `twin_cells`' search for its figures inside.
        "twin_cells_equal": len([cell for cell in written if cell in real_written]),
    }
    seen.update(counted)
    seen["product_seconds"] = round(product_seconds, 1)
    seen["counting_seconds"] = round(time.perf_counter() - started - product_seconds, 1)
    return seen

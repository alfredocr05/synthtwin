"""Invented long tables for the patient layer's generator (lane GRb, plan P4-D465).

Every table here is invented: its parameters are round values chosen for
this module, the table's own, and none is read from or attributed to any
source. Each maker returns ``(header, rows)`` with every cell written as
text, the rows of one patient consecutive and in visit order, and the
person column first.

- `encounter_like`: rows a patient heavy-tailed (most patients a few
  visits, a few patients hundreds), a group, a gender, a birth year, a visit
  date, a visit number, a reading with a patient level and a drift over
  visits, and a unit.
- `lab_like`: a narrow reading written to one decimal, an arm-by-visit
  trend, and dropout that depends on the previous reading.
- `flowsheet_like`: a minority of patients holding hundreds to over a
  thousand rows each, beside many patients of a few rows.
- `st2_complete`: the visit table of `patient_enumeration.st2_rows` with
  every subject followed for all eight visits.
- `st2_long`: the same reading model with rows a subject heavy-tailed
  (median about 20, at most 120).
- `wide_like`: fifty columns (G4's width): five patient-fixed columns, a
  visit date, a visit number, 22 readings, ten codes, seven flags and four
  counts, about ten rows a patient.

The makers use the standard library only and a seeded `random.Random`,
so a table is a fixed function of its arguments.
"""
from __future__ import annotations

import math
import random

ENCOUNTER_HEADER = ["pid", "group", "gender", "birth_year", "visit_date", "visit_no", "reading", "unit"]
LAB_HEADER = ["pid", "arm", "gender", "birth_year", "draw_date", "visit_no", "result", "unit"]
FLOWSHEET_HEADER = ["pid", "group", "birth_year", "taken_on", "reading", "unit"]
ST2_HEADER = ["sid", "arm", "age", "visit", "reading"]


def _day(start: int) -> str:
    """Day number ``start`` (0 is 2020-01-01) as an ISO date, on a calendar of 28-day months and 336-day years."""
    year = 2020 + start // 336
    month = 1 + (start // 28) % 12
    return f"{year}-{month:02d}-{1 + start % 28:02d}"


def _heavy(draw: random.Random, median: float, spread: float, most: int) -> int:
    """A heavy-tailed whole number of rows, at least 1 and at most ``most``."""
    return max(1, min(most, int(round(math.exp(draw.gauss(math.log(median), spread))))))


def encounter_like(rows_wanted: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """About ``rows_wanted`` rows: rows a patient lognormal around 3 with a long tail to 400."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    patient = 0
    while len(rows) < rows_wanted:
        count = _heavy(draw, 3.0, 1.3, 400)
        count = min(count, rows_wanted - len(rows))
        group = draw.choice(["a", "b", "c"])
        gender = "F" if draw.random() < 0.5 else "M"
        born = 1930 + draw.randint(0, 75)
        level = draw.gauss(0.0, 10.0)
        start = draw.randint(0, 300)
        day = start
        for visit in range(count):
            day = day + 1 + draw.randint(0, 20)
            value = 120.0 + level + 0.2 * (2020 - born - 50) / 10 + 0.3 * visit + draw.gauss(0.0, 8.0)
            unit = "mmHg" if draw.random() < 0.9 else "kPa"
            rows += [[f"P{patient:07d}", group, gender, f"{born}", _day(day), f"{visit + 1}", f"{value:.0f}", unit]]
        patient = patient + 1
    return list(ENCOUNTER_HEADER), rows


def _logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def lab_like(rows_wanted: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """About ``rows_wanted`` rows: up to 12 draws a patient, a one-decimal result, an arm-by-visit trend, dropout on the previous result."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    patient = 0
    while len(rows) < rows_wanted:
        arm = 1 if draw.random() < 0.5 else 0
        gender = "F" if draw.random() < 0.5 else "M"
        born = 1940 + draw.randint(0, 60)
        level = draw.gauss(0.0, 0.6)
        day = draw.randint(0, 200)
        previous: "float | None" = None
        for visit in range(12):
            if len(rows) >= rows_wanted:
                break
            if previous is not None and draw.random() < _logistic(-2.0 + 1.5 * (previous - 6.0)):
                break
            day = day + 28 + draw.randint(-3, 3)
            value = 6.0 + level + 0.03 * visit - 0.1 * arm * visit + draw.gauss(0.0, 0.4)
            value = round(value, 1)
            rows += [[f"L{patient:06d}", f"{arm}", gender, f"{born}", _day(day), f"{visit + 1}", f"{value:.1f}", "mmol/L"]]
            previous = value
        patient = patient + 1
    return list(LAB_HEADER), rows


def flowsheet_like(rows_wanted: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """About ``rows_wanted`` rows: one patient in ten holds 200 to 1,500 rows, the others 1 to 20."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    patient = 0
    while len(rows) < rows_wanted:
        if draw.random() < 0.1:
            count = draw.randint(200, 1500)
        else:
            count = draw.randint(1, 20)
        count = min(count, rows_wanted - len(rows))
        group = draw.choice(["ward", "unit", "clinic"])
        born = 1935 + draw.randint(0, 70)
        level = draw.gauss(0.0, 8.0)
        day = draw.randint(0, 100)
        for at in range(count):
            if at and draw.random() < 0.05:
                day = day + 1
            value = 80.0 + level + draw.gauss(0.0, 6.0)
            rows += [[f"F{patient:06d}", group, f"{born}", _day(day), f"{value:.0f}", "/min"]]
        patient = patient + 1
    return list(FLOWSHEET_HEADER), rows


def _st2_patient(draw: random.Random, subject: int, visits: int, dropout: bool, scale: float = 1.0) -> "list[list[str]]":
    """One subject of the visit table: arm, age, a patient level, a trend by arm (times ``scale``), dropout on the previous value."""
    arm = 1 if draw.random() < 0.5 else 0
    age = int(min(90, max(25, draw.gauss(55, 12))))
    base = draw.gauss(0, 0.8)
    previous: "float | None" = None
    out: "list[list[str]]" = []
    for visit in range(visits):
        if dropout and previous is not None and draw.random() < _logistic(-3.0 + 0.6 * (previous - 7.5)):
            break
        value = round(7.5 + base + 0.01 * (age - 55) + scale * (0.02 * visit - 0.15 * arm * visit) + draw.gauss(0, 0.5), 1)
        out += [[f"S{subject:05d}", f"{arm}", f"{age}", f"{visit}", f"{value}"]]
        previous = value
    return out


def st2_complete(subjects: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """The visit table with every subject followed for all eight visits (no dropout)."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for subject in range(subjects):
        rows += _st2_patient(draw, subject, 8, False)
    return list(ST2_HEADER), rows


WIDE_READINGS = 22
WIDE_CODES = 10
WIDE_FLAGS = 7
WIDE_COUNTS = 4
WIDE_HEADER = (
    ["pid", "arm", "gender", "birth_year", "site", "visit_date", "visit_no"]
    + [f"r{at + 1:02d}" for at in range(WIDE_READINGS)]
    + [f"c{at + 1:02d}" for at in range(WIDE_CODES)]
    + [f"f{at + 1:02d}" for at in range(WIDE_FLAGS)]
    + [f"n{at + 1:02d}" for at in range(WIDE_COUNTS)]
)


def wide_like(rows_wanted: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """About ``rows_wanted`` rows of fifty columns (G4's width, lane GRb's repair 1): 1 to 19 visits a patient.

    Each reading carries a patient level and a drift over visits; each code
    takes one of five letters with falling chances; each flag is Y on about
    one row in four; each count a small whole number.
    """
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    patient = 0
    letters = ["A", "B", "C", "D", "E"]
    while len(rows) < rows_wanted:
        count = min(draw.randint(1, 19), rows_wanted - len(rows))
        arm = f"{1 if draw.random() < 0.5 else 0}"
        gender = "F" if draw.random() < 0.5 else "M"
        born = f"{1935 + draw.randint(0, 70)}"
        site = draw.choice(["north", "south", "east", "west"])
        levels = [draw.gauss(0.0, 1.0) for _at in range(WIDE_READINGS)]
        day = draw.randint(0, 300)
        for visit in range(count):
            day = day + 7 + draw.randint(0, 30)
            row = [f"W{patient:07d}", arm, gender, born, site, _day(day), f"{visit + 1}"]
            for at in range(WIDE_READINGS):
                row += [f"{10.0 * (at + 1) + 3.0 * levels[at] + 0.05 * visit + draw.gauss(0.0, 2.0):.1f}"]
            for _at in range(WIDE_CODES):
                pick = draw.random()
                row += [letters[0 if pick < 0.4 else 1 if pick < 0.65 else 2 if pick < 0.82 else 3 if pick < 0.94 else 4]]
            for _at in range(WIDE_FLAGS):
                row += ["Y" if draw.random() < 0.25 else "N"]
            for _at in range(WIDE_COUNTS):
                row += [f"{draw.randint(0, 20)}"]
            rows += [row]
        patient = patient + 1
    return list(WIDE_HEADER), rows


def st2_long(subjects: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """The visit table with rows a subject lognormal (median about 20, at most 120), no dropout, the trend a fifth as steep.

    1,000 subjects make about 27,000 rows, the owner's floor of 1,000
    people with rows to spare.
    """
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for subject in range(subjects):
        rows += _st2_patient(draw, subject, _heavy(draw, 20.0, 0.8, 120), False, 0.2)
    return list(ST2_HEADER), rows

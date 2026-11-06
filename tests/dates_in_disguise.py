"""Dates in disguise: Safe Harbor dates no column name and no cell shape marks as a date (lane CZ-H, plan P4-D446).

A health table can hold the date elements of a person -- a birth, an
admission, a discharge, a service time -- as numbers, as codes or as
words in a shared answer column, where neither the column's name nor its
cells' shape says "date". A twin that reads them as numbers, codes or
words can publish a real date: a percentile of day counts, a level of a
shared answer column, a tail value. Safe Harbor (45 CFR
164.514(b)(2)(i)(C)) removes every element of such a date but the year.

FIVE INVENTED FORMS, each a table of the health data zoo
(`health_zoo.Table`, run by `health_zoo.run_table`), generic column
names, every value drawn from the table's own seed:

1. `day_numbers` -- typed day numbers: a day count from the MUMPS $H
   epoch (day 0 is 1840-12-31, a public convention) in a wide table of
   ordinary columns, written four ways: a float with a two-figure contact
   index after the point (`66123.01`; the first contact of a day written
   whole), an integer, two fixed decimals and text; the float column
   sits in a three-part key (record, day number, line) that is unique.
2. `answers_long` -- key-value answers: one answer column under a
   question key, where a few questions answer with five-figure day
   counts (birth, admission, discharge) and a few with ten-figure epoch
   seconds (service times), beside yes/no answers written 1/0, free text,
   category words and small numbers; the admission days are few and each
   is shared by many people; one question answers with a lab value of
   five figures that lies in the day band and is no date (`LAB_QUESTION`).
3. `flow_values` -- values typed by the key: a value column under many
   keys, a few of which hold date text and a few clock text (no date: a
   time of day alone names none, and its cells are counted apart), among
   numbers, choice words and pressure pairs, and one key's five-figure lab
   values lie in the day band (`FLOW_LAB_KEY`).
4. `results_dated` -- dates as results: one result key whose value is a
   full date, `MM-DD-YYYY` or `YYYY-MM-DD`, among numeric and word results.
5. `paired_clocks` -- two clocks on every row, recorded and entered, the
   lag from a minute below nought to years.

`DISGUISED` names, per table, where its dates sit: whole columns with
their decoders, or the keys of a key-value column whose values are
dates. `real_dates` reads them off the real table; `count_shown` and
`count_twin` are the LINEAR COUNTER (the orchestrator's suite-time rule
of 2026-10-26, (3)): the real dates go into a set once, each published
text and each twin cell is read once through its own tokens, EVERY token
decoded by every spelling's rule (`TOKENS`, whatever form the column's
dates were written in) and looked up in the set. `CASES` are the attacks
the reviews made on the forms: a stray beside the counts, spellings the
reader once missed, a column of numbers alone, contacts past the usual,
each a table the driver runs at 20,000 rows and the gate at 600.
"""

from __future__ import annotations

import csv
import dataclasses
import datetime
import io
import json
import pathlib
import random
import re
from typing import Callable

import health_zoo
from health_zoo import Check, Table, _bad, _csv_reader, _pattern, _repeats, _t

# -- the calendars a disguised date is counted in ----------------------------

# The MUMPS $H convention: day 0 is 31 December 1840 (a public convention).
MUMPS_EPOCH = datetime.date(1840, 12, 31)
UNIX_EPOCH = datetime.datetime(1970, 1, 1)
FIRST_DAY = datetime.date(2019, 1, 1)
LAST_DAY = datetime.date(2023, 12, 31)
FIRST_BIRTH = datetime.date(1931, 1, 1)
LAST_BIRTH = datetime.date(2012, 12, 31)


def day_count(day: datetime.date) -> int:
    """A date as its day count from the MUMPS epoch."""
    return (day - MUMPS_EPOCH).days


def _draw_day(draw: random.Random, first: datetime.date, last: datetime.date) -> datetime.date:
    return first + datetime.timedelta(days=draw.randrange((last - first).days + 1))


def _people(n: int) -> int:
    """The people a table's rows are about: 100 at the smoke's 600 rows, a tenth of the rows from 1,000 rows."""
    return max(100, n // 10)


def _key(person: int) -> str:
    return f"R{1_000_000 + 37 * person:07d}"


def _person_of(row: int, n: int) -> int:
    """The person a row is about: consecutive runs of rows, every person met."""
    return row * _people(n) // n


def _blocks(n: int) -> "list[tuple[int, int, int]]":
    """Each person's first row and row count, in order."""
    found: "list[tuple[int, int, int]]" = []
    start = 0
    for person in range(_people(n)):
        end = (person + 1) * n // _people(n)
        found += [(person, start, end - start)]
        start = end
    return found


def quoted_csv(header: "list[str]", rows: "list[list[str]]", quoted: "frozenset[str]") -> bytes:
    """A delimited table whose text columns `quoted` are written in quotes, as a text export writes them."""
    places = {place for place, name in enumerate(header) if name in quoted}
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(header)
    text = buffer.getvalue()
    lines: "list[str]" = [text]
    for row in rows:
        cells: "list[str]" = []
        for place, cell in enumerate(row):
            if place in places and cell:
                cells += ['"' + cell.replace('"', '""') + '"']
            else:
                single = io.StringIO()
                csv.writer(single, lineterminator="", quoting=csv.QUOTE_MINIMAL).writerow([cell])
                cells += [single.getvalue()]
        lines += [",".join(cells) + "\n"]
    return "".join(lines).encode("utf-8")


# -- form 1: typed day numbers -------------------------------------------------

DEPARTMENTS = (("Medicine", 30.0), ("Surgery", 22.0), ("Cardiology", 14.0), ("Oncology", 12.0), ("Pediatrics", 12.0),
               ("Neurology", 10.0))
STATUS_WORDS = (("Final", 70.0), ("Preliminary", 15.0), ("Corrected", 10.0), ("Cancelled", 5.0))
NOTE_WORDS = ("stable", "improving", "reviewed", "follow up", "no change", "seen", "plan discussed", "gone home")


def _contact(draw: random.Random) -> int:
    """A contact's index on its day: the first on many rows, rarely past nine."""
    roll = draw.random()
    if roll < 0.55:
        return 0
    if roll < 0.77:
        return 1
    if roll < 0.87:
        return 2
    return draw.randint(3, 12)


DAY_NUMBER_COLUMNS = (
    "record_id", "visit_day_number", "line_no", "birth_day", "admit_day_fixed", "discharge_day_text",
    "body_mass", "heart_rate", "lab_value", "dose_mg", "item_count", "charge_cents", "order_number",
    "unit_code", "status_word", "flag_yn", "pain_score", "room_number", "department", "note_words",
)


def float_day(count: int, contact: int) -> str:
    """A day count with its contact index as a float column writes it: whole at nought, '66123.1' at ten."""
    return f"{count}" if contact == 0 else repr(float(f"{count}.{contact:02d}"))


def fixed_day(count: int, contact: int) -> str:
    """A day count with its contact index to two fixed decimals."""
    return f"{count}.{contact:02d}"


def day_numbers(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Form 1: a wide table whose day numbers are written as a float, an integer, two decimals and text."""
    draw = random.Random(seed)
    header = list(DAY_NUMBER_COLUMNS)
    rows: "list[list[str]]" = []
    order = 4_100_000
    for person, _first, count in _blocks(n):
        birth = day_count(_draw_day(draw, FIRST_BIRTH, LAST_BIRTH))
        weight = min(180.0, max(35.0, draw.gauss(78.0, 16.0)))
        used: "dict[int, int]" = {}
        left = count
        while left > 0:
            admit = _draw_day(draw, FIRST_DAY, LAST_DAY - datetime.timedelta(days=30))
            stay = min(left, draw.randint(2, 14))
            length = draw.choice((0, 0, 1, 2, 3, 4, 5, 7, 10, 14))
            admit_contact = draw.choices((0, 1, 2), weights=(80, 15, 5))[0]
            discharge = admit + datetime.timedelta(days=length)
            open_stay = draw.random() < 0.03
            written = 0
            while written < stay:
                day = day_count(admit + datetime.timedelta(days=draw.randint(0, length)))
                contact = max(_contact(draw), used.get(day, 0))
                used[day] = contact + 1
                lines = min(stay - written, draw.choice((1, 1, 1, 2, 2, 3)))
                for line in range(1, lines + 1):
                    order += draw.randint(1, 40)
                    rows += [[
                        _key(person), float_day(day, contact), f"{line}", f"{birth}",
                        fixed_day(day_count(admit), admit_contact),
                        "" if open_stay else fixed_day(day_count(discharge), draw.choice((0, 0, 0, 1))),
                        f"{weight:.1f}", f"{min(180, max(40, round(draw.gauss(80, 14))))}",
                        f"{draw.lognormvariate(0.0, 0.5):.2f}", f"{draw.choice((5, 10, 20, 25, 40, 50, 100, 250, 500, 1000))}",
                        f"{min(12, int(draw.expovariate(0.5)))}", f"{int(10_000 * 9.9999 ** draw.random())}",
                        f"{order}", f"U{draw.randint(1, 40):02d}", health_zoo._pick(draw, STATUS_WORDS),
                        draw.choice(("1", "0", "0")), f"{min(10, int(draw.expovariate(0.35)))}",
                        f"{draw.randint(1, 12)}{draw.randint(1, 40):02d}", health_zoo._pick(draw, DEPARTMENTS),
                        draw.choice(NOTE_WORDS),
                    ]]
                written += lines
            left -= stay
    return header, rows


def day_numbers_flat(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Form 1 on one row a record: the same columns, each row its own encounter, no person column repeating."""
    header, rows = day_numbers(n, seed)
    header = ["encounter_id"] + header[1:]
    for place, row in enumerate(rows):
        row[0] = f"E{20_000_000 + 13 * place:08d}"
    return header, rows


def _key_repeats(frames: "dict[str, object]") -> int:
    """Rows whose three-part key (record, day number, line) another row holds."""
    raw = frames["raw"]
    keys = list(zip(raw["record_id"], raw["visit_day_number"], raw["line_no"]))  # type: ignore[index]
    return len(keys) - len(set(keys))


def _repeat_a_key(header: "list[str]", rows: "list[list[str]]") -> None:
    """A spoil: the second row takes the first row's three-part key."""
    for name in ("record_id", "visit_day_number", "line_no"):
        rows[1][header.index(name)] = rows[0][header.index(name)]


def _days_outside(series: object, first: datetime.date, last: datetime.date) -> int:
    """Day numbers whose day falls outside the real span of years."""
    low, high = day_count(datetime.date(first.year, 1, 1)), day_count(datetime.date(last.year, 12, 31))
    bad = 0
    for cell in series.dropna().astype(str):  # type: ignore[attr-defined]
        match = re.fullmatch(r"(\d+)(?:\.\d+)?", cell.strip())
        bad += 0 if match and low <= int(match.group(1)) <= high else 1
    return bad


# -- form 2: key-value answers ---------------------------------------------------

YES_NO = tuple(f"Q1{place:03d}" for place in range(1, 13))
FREE_TEXT = tuple(f"Q2{place:03d}" for place in range(1, 9))
CATEGORIES = tuple(f"Q3{place:03d}" for place in range(1, 7))
SMALL_NUMBERS = tuple(f"Q4{place:03d}" for place in range(1, 5))
SERVICE_TIMES = ("Q5001", "Q5002")
# The three questions answered with a day count: birth, admission, discharge.
DAY_QUESTIONS = ("Q6001", "Q6002", "Q6003")
CATEGORY_WORDS = ("none", "mild", "moderate", "severe", "home", "facility", "declined", "other")
TEXT_WORDS = ("patient", "reports", "pain", "after", "walking", "denies", "fever", "family", "at", "bedside",
              "tolerating", "diet", "slept", "well", "requests", "call", "back", "education", "given", "understands")
# The shares of the answer column's kinds: day counts, epoch seconds, 1/0,
# free text and category words; small numbers take the rest.
ANSWER_DAYS = 0.007
ANSWER_SECONDS = 0.04
ANSWER_YES_NO = 0.37
ANSWER_TEXT = 0.3
ANSWER_WORDS = 0.19
# A question answered with a lab value of five figures: inside the day
# band and no date, on about 1 row in 100, the per-column question's price.
LAB_QUESTION = "Q8001"
# The admission days the many answers share (each by many people).
SHARED_ADMISSIONS = (datetime.date(2021, 3, 8), datetime.date(2022, 6, 14), datetime.date(2023, 1, 23))


def answers_long(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Form 2: one answer column under a question key, some answers day counts or epoch seconds."""
    draw = random.Random(seed)
    header = ["record_id", "answer_seq", "question_code", "answer_value"]
    births = [day_count(_draw_day(draw, FIRST_BIRTH, LAST_BIRTH)) for _ in range(_people(n))]
    rows: "list[list[str]]" = []
    for row in range(n):
        person = _person_of(row, n)
        roll = draw.random()
        if roll < ANSWER_DAYS:
            question = draw.choice(DAY_QUESTIONS)
            admit = day_count(draw.choice(SHARED_ADMISSIONS))
            answer = {"Q6001": births[person], "Q6002": admit, "Q6003": admit + draw.randint(0, 14)}[question]
            value = f"{answer}"
        elif roll < ANSWER_DAYS + ANSWER_SECONDS:
            question = draw.choice(SERVICE_TIMES)
            moment = datetime.datetime.combine(_draw_day(draw, FIRST_DAY, LAST_DAY), datetime.time()) + datetime.timedelta(
                minutes=draw.randrange(24 * 60))
            value = f"{int((moment - UNIX_EPOCH).total_seconds())}"
        elif roll < ANSWER_DAYS + ANSWER_SECONDS + ANSWER_YES_NO:
            question = draw.choice(YES_NO)
            value = draw.choice(("1", "1", "0"))
        elif roll < ANSWER_DAYS + ANSWER_SECONDS + ANSWER_YES_NO + ANSWER_TEXT:
            question = draw.choice(FREE_TEXT)
            value = " ".join(draw.choice(TEXT_WORDS) for _ in range(draw.randint(3, 9)))
        elif roll < ANSWER_DAYS + ANSWER_SECONDS + ANSWER_YES_NO + ANSWER_TEXT + ANSWER_WORDS:
            question = draw.choice(CATEGORIES)
            value = draw.choice(CATEGORY_WORDS)
        else:
            question = draw.choice(SMALL_NUMBERS)
            value = f"{draw.randint(0, 20)}" if question != "Q4004" else f"{draw.gauss(37.0, 0.6):.1f}"
        rows += [[_key(person), f"{row + 1}", question, value]]
    labs = random.Random(seed + 1)
    for row_cells in rows:
        if row_cells[2] in SMALL_NUMBERS and labs.random() < 0.15:
            row_cells[2] = LAB_QUESTION
            row_cells[3] = f"{labs.randint(12_000, 70_000)}"
    return header, rows


# -- form 3: values typed by the key ---------------------------------------------

FLOW_KEYS = tuple(f"F{10_000 + place}" for place in range(1, 651))
# A few keys hold date text, and a few clock text.
FLOW_DATE_KEYS = ("F10213", "F10487", "F10530")
FLOW_CLOCK_KEYS = ("F10301", "F10552")
# One key's five-figure lab values, in the day band and no date.
FLOW_LAB_KEY = "F10123"
FLOW_PAIR_KEYS = tuple(FLOW_KEYS[place] for place in range(5, 650, 30))
FLOW_CHOICE_KEYS = tuple(FLOW_KEYS[place] for place in range(3, 650, 8))
FLOW_CHOICES = ("Yes", "No", "Assisted", "Independent", "Refused", "Clear", "Diminished", "Absent")
# The share of rows each typed group holds.
FLOW_DATE_SHARE = 0.012
FLOW_CLOCK_SHARE = 0.008


def _flow_kind(key: str) -> str:
    if key in FLOW_DATE_KEYS:
        return "date"
    if key in FLOW_CLOCK_KEYS:
        return "clock"
    if key in FLOW_PAIR_KEYS:
        return "pair"
    if key in FLOW_CHOICE_KEYS:
        return "choice"
    return "number"


def _pairs_without_their_slash(frames: "dict[str, object]") -> int:
    """Cells written as a pressure pair with any other mark than its slash."""
    return int(_t("result_value")(frames).astype(str).str.fullmatch(r"\d{2,3}-\d{2,3}").sum())  # type: ignore[attr-defined]


def flow_values(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Form 3: a value column whose values are typed by the key: numbers, words, pressures, dates, clocks."""
    draw = random.Random(seed)
    header = ["record_id", "flow_key", "result_value"]
    ordinary = [key for key in FLOW_KEYS if _flow_kind(key) not in ("date", "clock") and key != FLOW_LAB_KEY]
    weights = [1.0 / (place + 1) ** 1.05 for place in range(len(ordinary))]
    scales = {key: (draw.uniform(1, 200), draw.choice((0, 0, 1, 2))) for key in ordinary}
    rows: "list[list[str]]" = []
    for row in range(n):
        person = _person_of(row, n)
        roll = draw.random()
        if roll < FLOW_DATE_SHARE:
            key = draw.choice(FLOW_DATE_KEYS)
            day = _draw_day(draw, datetime.date(2015, 1, 1), LAST_DAY)
            value = f"{day.month:02d}/{day.day:02d}/{day.year}"
        elif roll < FLOW_DATE_SHARE + FLOW_CLOCK_SHARE:
            key = draw.choice(FLOW_CLOCK_KEYS)
            value = f"{draw.randrange(24):02d}:{draw.randrange(60):02d}"
        else:
            key = draw.choices(ordinary, weights=weights)[0]
            kind = _flow_kind(key)
            if kind == "pair":
                upper = draw.randint(90, 180)
                value = f"{upper}/{draw.randint(50, min(110, upper - 20))}"
            elif kind == "choice":
                value = draw.choice(FLOW_CHOICES)
            else:
                middle, places = scales[key]
                value = f"{max(0.0, draw.gauss(middle, middle / 5)):.{places}f}"
        rows += [[_key(person), key, value]]
    labs = random.Random(seed + 1)
    for row_cells in rows:
        if row_cells[1] in ordinary and labs.random() < 0.01:
            row_cells[1] = FLOW_LAB_KEY
            row_cells[2] = f"{labs.randint(12_000, 70_000)}"
    return header, rows


# -- form 4: dates as results ----------------------------------------------------

RESULT_KEYS = tuple(f"L{place:03d}" for place in range(101, 125))
RESULT_DATE_KEY = "L117"
RESULT_WORD_KEYS = ("L103", "L108", "L111", "L120", "L124")
RESULT_WORDS = ("Positive", "Negative", "Detected", "Not detected", "See note", "Indeterminate")
RESULT_DATE_SHARE = 0.025
# The share of the date results written month first; the rest year first.
RESULT_MONTH_FIRST = 0.6


def results_dated(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Form 4: one result key whose result is a full date, month first or year first, among numbers and words."""
    draw = random.Random(seed)
    header = ["record_id", "result_key", "result_value"]
    numeric = [key for key in RESULT_KEYS if key != RESULT_DATE_KEY and key not in RESULT_WORD_KEYS]
    scales = {key: (draw.uniform(0.5, 300), draw.choice((0, 1, 1, 2))) for key in numeric}
    rows: "list[list[str]]" = []
    for row in range(n):
        person = _person_of(row, n)
        roll = draw.random()
        if roll < RESULT_DATE_SHARE:
            key = RESULT_DATE_KEY
            day = _draw_day(draw, datetime.date(2018, 1, 1), LAST_DAY)
            value = (f"{day.month:02d}-{day.day:02d}-{day.year}" if draw.random() < RESULT_MONTH_FIRST
                     else f"{day.year}-{day.month:02d}-{day.day:02d}")
        elif roll < RESULT_DATE_SHARE + 0.2:
            key = draw.choice(RESULT_WORD_KEYS)
            value = draw.choice(RESULT_WORDS)
        else:
            key = draw.choice(numeric)
            middle, places = scales[key]
            value = f"{max(0.0, draw.gauss(middle, middle / 4)):.{places}f}"
        rows += [[_key(person), key, value]]
    return header, rows


# -- form 5: paired clocks -------------------------------------------------------

CLOCK_ITEMS = tuple(f"V{place:02d}" for place in range(1, 41))
STAMP = "%Y-%m-%d %H:%M:%S"


def _lag_minutes(draw: random.Random) -> int:
    """The minutes from recorded to entered: nought often, a few minutes typically, a minute early to years."""
    roll = draw.random()
    if roll < 0.29:
        return 0
    if roll < 0.32:
        return -1
    if roll < 0.84:
        return 1 + int(draw.expovariate(1 / 4))
    if roll < 0.96:
        return 60 + int(draw.expovariate(1 / 300))
    if roll < 0.99:
        return 24 * 60 * draw.randint(1, 20)
    return 24 * 60 * draw.randint(200, 1100)


def paired_clocks(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Form 5: recorded and entered clocks on every row, entered a lag after recorded."""
    draw = random.Random(seed)
    header = ["record_id", "item_key", "item_value", "recorded_at", "entered_at"]
    rows: "list[list[str]]" = []
    for person, _first, count in _blocks(n):
        moment = datetime.datetime.combine(_draw_day(draw, FIRST_DAY, LAST_DAY), datetime.time(draw.randrange(24)))
        for _row in range(count):
            moment += datetime.timedelta(minutes=draw.choice((0, 0, 15, 30, 60, 240, 720)))
            entered = moment + datetime.timedelta(minutes=_lag_minutes(draw))
            rows += [[
                _key(person), draw.choice(CLOCK_ITEMS), f"{max(0.0, draw.gauss(70, 20)):.0f}",
                moment.strftime(STAMP), entered.strftime(STAMP),
            ]]
    return header, rows


def _lags_negative_past_a_minute(frames: "dict[str, object]") -> int:
    """Rows entered more than a minute before they were recorded."""
    import pandas

    raw = frames["raw"]
    recorded = pandas.to_datetime(raw["recorded_at"], format=STAMP, errors="coerce")  # type: ignore[index]
    entered = pandas.to_datetime(raw["entered_at"], format=STAMP, errors="coerce")  # type: ignore[index]
    return int(((entered - recorded).dt.total_seconds() < -60).sum())


def _lag_shares(frames: "dict[str, object]") -> "tuple[float, float]":
    """The share of rows entered at the minute they were recorded, and within ten minutes."""
    import pandas

    raw = frames["raw"]
    recorded = pandas.to_datetime(raw["recorded_at"], format=STAMP, errors="coerce")  # type: ignore[index]
    entered = pandas.to_datetime(raw["entered_at"], format=STAMP, errors="coerce")  # type: ignore[index]
    lag = (entered - recorded).dt.total_seconds()
    rows = max(1, len(lag))
    return float((lag == 0).sum()) / rows, float(((lag >= 0) & (lag <= 600)).sum()) / rows


# -- the tables ------------------------------------------------------------------

KIND_DAY_NUMBERS = "typed_day_numbers"
KIND_ANSWERS = "key_value_answers"
KIND_FLOW = "values_typed_by_key"
KIND_RESULTS = "dates_as_results"
KIND_CLOCKS = "paired_clocks"
KINDS = (KIND_DAY_NUMBERS, KIND_ANSWERS, KIND_FLOW, KIND_RESULTS, KIND_CLOCKS)
DAY_COLUMNS = ("visit_day_number", "birth_day", "admit_day_fixed", "discharge_day_text")

TABLES: "tuple[Table, ...]" = (
    Table(
        "day_numbers", ".csv", day_numbers,
        lambda header, rows: quoted_csv(header, rows, frozenset({"discharge_day_text"})),
        {KIND_DAY_NUMBERS: DAY_NUMBER_COLUMNS},
        {
            "record_id": "identifier", "visit_day_number": "days-since-1840", "birth_day": "days-since-1840",
            "admit_day_fixed": "days-since-1840", "discharge_day_text": "days-since-1840",
            "order_number": "identifier", "charge_cents": "measurement",
        },
        _csv_reader(),
        (
            *_repeats(KIND_DAY_NUMBERS, "record_id"),
            _bad(KIND_DAY_NUMBERS, "the three-part key (record, day number, line) is unique", "visit_day_number",
                 _key_repeats, _repeat_a_key),
            _pattern(KIND_DAY_NUMBERS, "a day number with its contact index after the point", "visit_day_number",
                     r"\d{5}(\.\d{1,2})?"),
            _pattern(KIND_DAY_NUMBERS, "two fixed decimals keep the contact's two figures", "admit_day_fixed", r"\d{5}\.\d\d"),
            _pattern(KIND_DAY_NUMBERS, "day numbers as text keep two decimals", "discharge_day_text", r"\d{5}\.\d\d"),
            _pattern(KIND_DAY_NUMBERS, "integer day numbers", "birth_day", r"\d{5}"),
            _bad(KIND_DAY_NUMBERS, "visit days fall in the real span of years", "visit_day_number",
                 lambda f: _days_outside(_t("visit_day_number")(f), FIRST_DAY, LAST_DAY),
                 health_zoo.spoil_cell("visit_day_number", "12345.01")),
            _bad(KIND_DAY_NUMBERS, "birth days fall in the real span of years", "birth_day",
                 lambda f: _days_outside(_t("birth_day")(f), FIRST_BIRTH, LAST_BIRTH),
                 health_zoo.spoil_cell("birth_day", "99999")),
        ),
        person="record_id",
    ),
    Table(
        "day_numbers_flat", ".csv", day_numbers_flat,
        lambda header, rows: quoted_csv(header, rows, frozenset({"discharge_day_text"})),
        {KIND_DAY_NUMBERS: ("encounter_id", *DAY_NUMBER_COLUMNS[1:])},
        {
            "encounter_id": "identifier", "visit_day_number": "days-since-1840", "birth_day": "days-since-1840",
            "admit_day_fixed": "days-since-1840", "discharge_day_text": "days-since-1840",
            "order_number": "identifier", "charge_cents": "measurement",
        },
        _csv_reader(),
        (
            _pattern(KIND_DAY_NUMBERS, "a day number with its contact index after the point", "visit_day_number",
                     r"\d{5}(\.\d{1,2})?"),
            _pattern(KIND_DAY_NUMBERS, "two fixed decimals keep the contact's two figures", "admit_day_fixed", r"\d{5}\.\d\d"),
            _bad(KIND_DAY_NUMBERS, "visit days fall in the real span of years", "visit_day_number",
                 lambda f: _days_outside(_t("visit_day_number")(f), FIRST_DAY, LAST_DAY),
                 health_zoo.spoil_cell("visit_day_number", "12345.01")),
            _bad(KIND_DAY_NUMBERS, "birth days fall in the real span of years", "birth_day",
                 lambda f: _days_outside(_t("birth_day")(f), FIRST_BIRTH, LAST_BIRTH),
                 health_zoo.spoil_cell("birth_day", "99999")),
        ),
    ),
    Table(
        "answers_long", ".csv", answers_long, lambda header, rows: health_zoo.csv_bytes(header, rows),
        {KIND_ANSWERS: ("record_id", "answer_seq", "question_code", "answer_value")},
        {"record_id": "identifier", "answer_seq": "identifier", "question_code": "code", "answer_value": "yes"},
        _csv_reader(),
        (
            *_repeats(KIND_ANSWERS, "record_id"),
            _pattern(KIND_ANSWERS, "question codes", "question_code", r"Q\d{4}"),
            Check(KIND_ANSWERS, "yes/no answers written 1/0 hold their share", "share",
                  lambda f: health_zoo._share_has(_t("answer_value")(f), r"[01]"), "answer_value",
                  health_zoo.spoil_every("answer_value", lambda value: "yes" if value in ("0", "1") else value)),
        ),
        person="record_id",
    ),
    Table(
        "flow_values", ".csv", flow_values, lambda header, rows: health_zoo.csv_bytes(header, rows),
        {KIND_FLOW: ("record_id", "flow_key", "result_value")},
        {"record_id": "identifier", "flow_key": "code", "result_value": "yes"},
        _csv_reader(),
        (
            *_repeats(KIND_FLOW, "record_id"),
            _pattern(KIND_FLOW, "flow keys", "flow_key", r"F\d{5}"),
            _bad(KIND_FLOW, "pressure pairs keep their slash", "result_value", _pairs_without_their_slash,
                 health_zoo.spoil_every("result_value", lambda value: value.replace("/", "-"))),
        ),
        person="record_id",
    ),
    Table(
        "results_dated", ".csv", results_dated, lambda header, rows: health_zoo.csv_bytes(header, rows),
        {KIND_RESULTS: ("record_id", "result_key", "result_value")},
        {"record_id": "identifier", "result_key": "code", "result_value": "yes"},
        _csv_reader(),
        (
            *_repeats(KIND_RESULTS, "record_id"),
            _pattern(KIND_RESULTS, "result keys", "result_key", r"L\d{3}"),
        ),
        person="record_id",
    ),
    Table(
        "paired_clocks", ".csv", paired_clocks, lambda header, rows: health_zoo.csv_bytes(header, rows),
        {KIND_CLOCKS: ("record_id", "item_key", "item_value", "recorded_at", "entered_at")},
        {"record_id": "identifier", "item_key": "code"},
        _csv_reader(),
        (
            *_repeats(KIND_CLOCKS, "record_id"),
            health_zoo._dated(KIND_CLOCKS, "recorded clocks parse", "recorded_at", STAMP),
            health_zoo._dated(KIND_CLOCKS, "entered clocks parse", "entered_at", STAMP),
            _bad(KIND_CLOCKS, "no row entered more than a minute before it was recorded", "entered_at",
                 _lags_negative_past_a_minute, health_zoo.spoil_cell("entered_at", "2019-01-01 00:00:00")),
            Check(KIND_CLOCKS, "lags of nought and of ten minutes or less hold their shares", "share",
                  _lag_shares, "entered_at",
                  health_zoo.spoil_every("entered_at", lambda value: value[:11] + "00:00:00")),
        ),
        person="record_id",
    ),
)
SEEDS = {table.name: 20261030 + place for place, table in enumerate(TABLES)}
# THE FIVE FORMS AS KINDS OF THE CATALOGUE (`health_zoo_wide`): a kind is served
# by one table, so the same columns on one row a record are K-HZ-16's alone.
CATALOGUE_TABLES = tuple(table for table in TABLES if table.name != "day_numbers_flat")


def table_named(name: str) -> Table:
    """The table of that name."""
    for table in TABLES:
        if table.name == name:
            return table
    raise KeyError(name)


# -- where each table's dates sit, and how each is decoded ------------------------


def _mumps(text: str) -> "int | None":
    match = re.fullmatch(r"\s*[+]?(\d{5}|\d{2},\d{3})(?:\.\d+)?(?:,\d{1,5})?\s*", text)
    return MUMPS_EPOCH.toordinal() + int(match.group(1).replace(",", "")) if match else None


def _mumps_in_the_span(text: str) -> "int | None":
    """A day count read as `_mumps` reads it, only where its day lies in the zoo's span of visits: a column whose other numbers are five figures too."""
    day = _mumps(text)
    return day if day is not None and FIRST_DAY.toordinal() <= day <= LAST_DAY.toordinal() else None


def _unix_seconds(text: str) -> "int | None":
    match = re.fullmatch(r"\s*(\d{9,10})(?:\.\d+)?\s*", text)
    if not match:
        return None
    return (UNIX_EPOCH + datetime.timedelta(seconds=int(match.group(1)))).date().toordinal()


def _civil(year: str, month: str, day: str) -> "int | None":
    try:
        return datetime.date(int(year), int(month), int(day)).toordinal()
    except ValueError:
        return None


def _century(year: str) -> str:
    """A two-figure year as a person's: the zoo's dates of this century."""
    return f"20{year}"


def _mdy(text: str) -> "int | None":
    match = re.fullmatch(r"\s*(\d{2})[/-](\d{2})[/-](\d{4})(?:\s[\d:]+)?\s*", text)
    return _civil(match.group(3), match.group(1), match.group(2)) if match else None


def _mdy_short(text: str) -> "int | None":
    match = re.fullmatch(r"\s*(\d{2})[/-](\d{2})[/-](\d{2})\s*", text)
    return _civil(_century(match.group(3)), match.group(1), match.group(2)) if match else None


def _ymd(text: str) -> "int | None":
    match = re.fullmatch(r"\s*(\d{4})[-.](\d{2})[-.](\d{2})(?:[ T][\d:.]+)?\s*", text)
    return _civil(match.group(1), match.group(2), match.group(3)) if match else None


def _stamp(text: str) -> "int | None":
    match = re.fullmatch(r"\s*(\d{4})(\d{2})(\d{2})(?:\d{4}|\d{6})?\s*", text)
    return _civil(match.group(1), match.group(2), match.group(3)) if match else None


def _ordinal(text: str) -> "int | None":
    match = re.fullmatch(r"\s*(\d{4})-(\d{3})\s*", text)
    if not match or not 1 <= int(match.group(2)) <= 366:
        return None
    return datetime.date(int(match.group(1)), 1, 1).toordinal() + int(match.group(2)) - 1


_MONTHS = {
    word: place + 1
    for place, word in enumerate(("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"))
}


def _month_named(text: str) -> "int | None":
    match = re.fullmatch(r"\s*(\d{2})-?([A-Za-z]{3})-?(\d{4})\s*", text)
    if not match or match.group(2).upper() not in _MONTHS:
        return None
    return _civil(match.group(3), f"{_MONTHS[match.group(2).upper()]}", match.group(1))


def _clock(text: str) -> "int | None":
    """A clock text names no day: its own text is what is looked up (`CLOCK`)."""
    return None


def _month_of(word: str) -> "int | None":
    """A month's name, short or whole, in any case: its number."""
    for place, name in enumerate(_MONTH_NAMES):
        if word.lower() in (name[:3], name) or (len(word) >= 3 and name.startswith(word.lower()) and word.lower() != "ma"):
            return place + 1
    return None


_MONTH_NAMES = ("january", "february", "march", "april", "may", "june", "july", "august", "september",
                "october", "november", "december")
_WEEKDAY = r"(?:(?:mon|tue|tues|wed|thu|thur|thurs|fri|sat|sun)(?:day|sday|nesday|rsday|urday)?\.?,?\s+)?"


def _iso_lead(text: str) -> "int | None":
    """An ISO date at the head of a cell, whatever follows it: a zone word, an offset, a bare clock."""
    match = re.fullmatch(r"\s*(\d{4})-(\d{2})-(\d{2})(?:[ TZ+-].*)?", text)
    return _civil(match.group(1), match.group(2), match.group(3)) if match else None


def _iso_basic(text: str) -> "int | None":
    """`YYYYMMDDTHHMM[SS]`, or eight figures and a clock after a space."""
    match = re.fullmatch(r"\s*(\d{4})(\d{2})(\d{2})(?:T\d{4}(?:\d{2})?| \d{4}(?:\d{2})?)\s*", text)
    return _civil(match.group(1), match.group(2), match.group(3)) if match else None


def _month_first_named(text: str) -> "int | None":
    """`Mar 08 2021`, `March 8th, 2021`, `Mon Mar 08 2021`, `Monday, March 8, 2021`."""
    match = re.fullmatch(_WEEKDAY + r"([A-Za-z]{3,9})\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\s*", text.strip(), re.IGNORECASE)
    if not match or _month_of(match.group(1)) is None:
        return None
    return _civil(match.group(3), f"{_month_of(match.group(1))}", match.group(2))


def _day_first_named(text: str) -> "int | None":
    """`8th March 2021`, `8 Mar 2021`, `Mon 8 March 2021`."""
    match = re.fullmatch(_WEEKDAY + r"(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]{3,9})\.?,?\s+(\d{4})\s*", text.strip(), re.IGNORECASE)
    if not match or _month_of(match.group(2)) is None:
        return None
    return _civil(match.group(3), f"{_month_of(match.group(2))}", match.group(1))


DECODERS: "dict[str, Callable[[str], int | None]]" = {
    "mumps": _mumps, "unix-seconds": _unix_seconds, "mdy": _mdy, "mdy-short": _mdy_short, "ymd": _ymd,
    "stamp": _stamp, "ordinal": _ordinal, "month-named": _month_named, "clock": _clock,
    # The spellings the verify of the first repair read (its items 1 and 5):
    # a date at the head of a cell, the basic ISO stamp, a month's name first
    # or a weekday's before it, so this counter counts what it stamps.
    "iso-lead": _iso_lead, "iso-basic": _iso_basic, "month-first-named": _month_first_named,
    "day-first-named": _day_first_named, "mumps-in-the-span": _mumps_in_the_span,
}
CLOCK = re.compile(r"\s*([01]\d|2[0-3]):[0-5]\d\s*")


@dataclasses.dataclass(frozen=True)
class Disguised:
    """Where a table's dates sit: a whole column, or the keys of a key-value column, with their decoders."""

    column: str
    decoders: "tuple[str, ...]"
    key_column: str = ""
    keys: "tuple[str, ...]" = ()
    # A clock or stamp column read as dates by its shape: the product's own
    # date rules govern it, so a date it shows counts only where one to ten
    # people hold it (K-HZ-07's rule, plan P4-D433).
    shaped: bool = False


DISGUISED: "dict[str, tuple[Disguised, ...]]" = {
    "day_numbers": tuple(Disguised(column, ("mumps",)) for column in DAY_COLUMNS),
    "day_numbers_flat": tuple(Disguised(column, ("mumps",)) for column in DAY_COLUMNS),
    "answers_long": (
        Disguised("answer_value", ("mumps",), "question_code", DAY_QUESTIONS),
        Disguised("answer_value", ("unix-seconds",), "question_code", SERVICE_TIMES),
    ),
    "flow_values": (
        Disguised("result_value", ("mdy",), "flow_key", FLOW_DATE_KEYS),
        Disguised("result_value", ("clock",), "flow_key", FLOW_CLOCK_KEYS),
    ),
    "results_dated": (Disguised("result_value", ("mdy", "ymd"), "result_key", (RESULT_DATE_KEY,)),),
    "paired_clocks": (
        Disguised("recorded_at", ("ymd",), shaped=True),
        Disguised("entered_at", ("ymd",), shaped=True),
    ),
}
FLOOR = 11


@dataclasses.dataclass
class RealDates:
    """One column's real dates: each day with the people holding it, the cells as written, the clock texts."""

    days: "dict[int, set[str]]"
    texts: "set[str]"
    clocks: "set[str]"
    decoders: "tuple[str, ...]"
    shaped: bool


def real_dates(
    table: Table, header: "list[str]", rows: "list[list[str]]",
    disguised: "tuple[Disguised, ...] | None" = None,
) -> "dict[str, RealDates]":
    """Per column of `DISGUISED` (or those named), the real dates its cells or its date keys' cells hold. One pass over the rows."""
    found: "dict[str, RealDates]" = {}
    person = header.index(table.person) if table.person else -1
    for where in DISGUISED[table.name] if disguised is None else disguised:
        place = header.index(where.column)
        key_place = header.index(where.key_column) if where.key_column else -1
        keys = set(where.keys)
        entry = found.setdefault(where.column, RealDates({}, set(), set(), (), where.shaped))
        entry.decoders = entry.decoders + tuple(name for name in where.decoders if name not in entry.decoders)
        for row in rows:
            cell = row[place]
            if not cell.strip() or (key_place >= 0 and row[key_place] not in keys):
                continue
            who = row[person] if person >= 0 else f"row-{id(row)}"
            if "clock" in where.decoders and CLOCK.fullmatch(cell):
                entry.clocks |= {cell.strip()}
                entry.texts |= {cell.strip()}
                continue
            for name in where.decoders:
                day = DECODERS[name](cell)
                if day is not None:
                    holders = entry.days.setdefault(day, set())
                    holders |= {who}
                    entry.texts |= {cell.strip()}
                    break
    return found


# The tokens a published text or a twin cell is read through: each shape
# a disguised date is written in, decoded by the rule of its form.
TOKENS: "tuple[tuple[str, re.Pattern[str]], ...]" = (
    ("mumps", re.compile(r"(?<![\d.,])[+]?(?:\d{5}|\d{2},\d{3})(?:\.\d+)?(?:,\d{1,5})?(?![\d,])")),
    ("unix-seconds", re.compile(r"(?<![\d.])\d{9,10}(?:\.\d+)?(?![\d])")),
    ("mdy", re.compile(r"(?<!\d)\d{2}[/-]\d{2}[/-]\d{4}(?!\d)")),
    ("mdy-short", re.compile(r"(?<![\d-])\d{2}[/-]\d{2}[/-]\d{2}(?![\d-])")),
    ("ymd", re.compile(r"(?<!\d)\d{4}[-.]\d{2}[-.]\d{2}(?!\d)")),
    ("stamp", re.compile(r"(?<!\d)\d{8}(?:\d{4}|\d{6})?(?!\d)")),
    ("ordinal", re.compile(r"(?<!\d)\d{4}-\d{3}(?!\d)")),
    ("month-named", re.compile(r"(?<!\d)\d{2}-?[A-Za-z]{3}-?\d{4}(?!\d)")),
    ("clock", re.compile(r"(?<![\d:])(?:[01]\d|2[0-3]):[0-5]\d(?![\d])")),
    ("iso-basic", re.compile(r"(?<!\d)\d{8}(?:T\d{4}(?:\d{2})?| \d{4}(?:\d{2})?)(?!\d)")),
    ("month-first-named", re.compile(
        r"(?<![A-Za-z])" + _WEEKDAY + r"[A-Za-z]{3,9}\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}(?!\d)", re.IGNORECASE)),
    ("day-first-named", re.compile(
        r"(?<![\dA-Za-z])" + _WEEKDAY + r"\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]{3,9}\.?,?\s+\d{4}(?!\d)", re.IGNORECASE)),
)
# The token that is a bare number: read in another column's rung by chance,
# so a hit outside the column's own entries is counted apart.
BARE_FORMS = ("mumps", "unix-seconds", "stamp")
_ISO = re.compile(r"(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)")


def _hits(text: str, real: RealDates) -> "tuple[set[int], set[str], set[int]]":
    """The real days and clock texts one text shows, and the days among them in a form the column does not write."""
    days: "set[int]" = set()
    clocks: "set[str]" = set()
    other: "set[int]" = set()
    for name, pattern in TOKENS:
        for match in pattern.finditer(text):
            token = match.group(0)
            if name == "clock":
                if "clock" in real.decoders:
                    clocks |= {token} & real.clocks
                continue
            day = DECODERS[name](token)
            if day is not None and day in real.days:
                if name in real.decoders:
                    days |= {day}
                else:
                    other |= {day}
    return days, clocks, other


def _finer_than_the_year(text: str) -> "set[str]":
    """The dates written in ISO text in one text that are not the first of a year."""
    found: "set[str]" = set()
    for match in _ISO.finditer(text):
        if (match.group(2), match.group(3)) != ("01", "01"):
            found |= {match.group(0)}
    return found


def _entries_naming(value: object, column: str) -> "list[str]":
    """The JSON of every dict in a document that names `column` as its column (a question, a note)."""
    found: "list[str]" = []
    if isinstance(value, dict):
        if f"{value.get('column', '')}" == column or f"{value.get('name', '')}" == column:
            found += [json.dumps(value)]
        else:
            for inner in value.values():
                found += _entries_naming(inner, column)
    elif isinstance(value, list):
        for inner in value:
            found += _entries_naming(inner, column)
    return found


def _people_in_month(real: RealDates, iso: str) -> int:
    """How many people hold a real day in that token's month (the grain a month or quarter start prints at most)."""
    year, month = int(iso[:4]), int(iso[5:7])
    people: "set[str]" = set()
    for day, holders in real.days.items():
        date = datetime.date.fromordinal(day)
        if date.year == year and date.month == month:
            people |= holders
    return len(people)


def count_shown(
    real: "dict[str, RealDates]", folder: pathlib.Path, screen: str, skip: "tuple[pathlib.Path, ...]",
) -> "dict[str, dict[str, object]]":
    """Per column, the real dates and clock texts shown in every file the run wrote (but `skip`) and on screen.

    A JSON file is read entry by entry: each dict that names the column
    (its description block, a question, a publication note) is read for
    that column. Any other file, and the screen, line by line: a line
    that names the column is read for it. EVERY text is then read whole,
    so a real day shown under another column's name is seen too. Each
    token is decoded by every spelling's rule (`TOKENS`), so:

    * `days` and `clocks`: the real days and clock texts in the column's
      own entries, in the forms the column writes;
    * `other_forms`: real days in its own entries in another form (a date
      published as ISO text where its cells count days);
    * `finer`: its own entries' ISO dates that are not a year's first day,
      real or not, with `finer_fewest`, the fewest people holding the
      month one of them names: what an answer that reads the column as
      dates publishes (`time_grain`'s span ends);
    * `elsewhere` and `elsewhere_bare`: real days outside the column's own
      entries, written as a date, and as a bare number (another column's
      rung may read so by chance);
    * `few`: days held by one to ten people among `days`: for a column
      read as dates by its shape, only those are a defect (K-HZ-07's rule).
    """
    shown: "dict[str, dict[str, set]]" = {
        column: {"days": set(), "clocks": set(), "other": set(), "finer": set(), "where": set(),
                 "elsewhere": set(), "elsewhere_bare": set()}
        for column in real
    }
    texts: "list[tuple[str, str]]" = [("screen", screen)]
    for path in sorted(folder.iterdir()):
        if path in skip or not path.is_file():
            continue
        texts += [(path.name, path.read_text(encoding="utf-8", errors="replace"))]
    for name, text in texts:
        document: object = None
        if name.endswith(".json"):
            try:
                document = json.loads(text)
            except ValueError:
                document = None
        for column, dates in real.items():
            if document is not None:
                pieces = _entries_naming(document, column)
            else:
                pieces = [line for line in text.split("\n") if column in line]
            for piece in pieces:
                days, clocks, other = _hits(piece, dates)
                if days or clocks or other:
                    shown[column]["where"] |= {name}
                shown[column]["days"] |= days
                shown[column]["clocks"] |= clocks
                shown[column]["other"] |= other
                shown[column]["finer"] |= _finer_than_the_year(piece)
        for column, dates in real.items():
            mine = shown[column]["days"] | shown[column]["other"]
            for form, pattern in TOKENS:
                if form == "clock":
                    continue
                for match in pattern.finditer(text):
                    day = DECODERS[form](match.group(0))
                    if day is not None and day in dates.days and day not in mine:
                        shown[column]["elsewhere_bare" if form in BARE_FORMS else "elsewhere"] |= {day}
    return {
        column: {
            "days": len(found["days"]),
            "few": sum(1 for day in found["days"] if len(real[column].days[day]) < FLOOR),
            "clocks": len(found["clocks"]),
            "other_forms": len(found["other"]),
            "finer": len(found["finer"]),
            "finer_fewest": min((_people_in_month(real[column], iso) for iso in found["finer"]), default=0),
            "elsewhere": len(found["elsewhere"] - found["days"] - found["other"]),
            "elsewhere_bare": len(found["elsewhere_bare"] - found["days"] - found["other"]),
            "where": sorted(found["where"]),
            "examples": [datetime.date.fromordinal(day).isoformat() for day in sorted(found["days"] | found["other"])[:3]],
        }
        for column, found in shown.items()
    }


def count_twin(real: "dict[str, RealDates]", twin_header: "list[str]", twin_rows: "list[list[str]]") -> "dict[str, dict[str, int]]":
    """Per column, the twin cells that carry a real date: as written, or decoded by every spelling's rule.

    Every cell of the column is read once (a key-value twin may write a
    date beside any key), each distinct cell decoded once; `days` counts
    the distinct real days met, `cells` the cells meeting one, `written`
    the cells equal to a real cell as written, `clock_cells` the cells
    equal to a real clock text.
    """
    found: "dict[str, dict[str, int]]" = {}
    for column, dates in real.items():
        if column not in twin_header:
            continue
        place = twin_header.index(column)
        days: "set[int]" = set()
        decoded: "dict[str, int | None]" = {}
        cells = written = clock_cells = 0
        for row in twin_rows:
            cell = row[place].strip()
            if not cell:
                continue
            if cell in dates.texts:
                written += 1
            if cell in dates.clocks:
                clock_cells += 1
                continue
            if cell not in decoded:
                reads: "int | None" = None
                for name in DECODERS:
                    reads = DECODERS[name](cell)
                    if reads is not None:
                        break
                decoded[cell] = reads
            day = decoded[cell]
            if day is not None and day in dates.days:
                days |= {day}
                cells += 1
        found[column] = {"days": len(days), "cells": cells, "written": written, "clock_cells": clock_cells}
    return found


def read_csv(path: pathlib.Path) -> "tuple[list[str], list[list[str]]]":
    """A delimited file's header and rows as text."""
    with path.open(encoding="utf-8", newline="") as handle:
        every = list(csv.reader(handle))
    return every[0], every[1:]


def date_questions(questions: pathlib.Path, column: str) -> "list[list[str]]":
    """The answers each question about `column` offers, the Safe Harbor dates question's marked `dates?`."""
    document = json.loads(questions.read_text(encoding="utf-8"))
    found: "list[list[str]]" = []
    for entry in health_zoo._entries(document):
        if f"{entry.get('column', '')}" != column:
            continue
        offered = list(health_zoo._offered(entry))
        saw = f"{entry.get('what_synthtwin_saw', '')}"
        if sorted(offered) == ["no", "yes"] and any(words in saw for words in SAFE_HARBOR_DATES_SAW):
            offered += [DATES_ASKED]
        found += [offered]
    return found


DATE_ANSWER = re.compile(r"dates|excel-19(00|04)|(days|seconds|milliseconds|microseconds|nanoseconds)-since-\d{4}")
# The Safe Harbor question about dates in disguise (plan P4-D446) says so
# in what synthtwin saw, and so does the one that holds a column of
# five-figure numbers whole, day counts among them (plan P4-D427); the mark
# this module gives such an entry.
SAFE_HARBOR_DATES_SEEN = "beside its other values, read as dates"
SAFE_HARBOR_DATES_SAW = (SAFE_HARBOR_DATES_SEEN, "as ZIP codes are written")
DATES_ASKED = "dates?"


def asks_the_date(offered: "list[list[str]]") -> bool:
    """Whether a question about a column offers a date reading, or is the Safe Harbor question about its dates."""
    return any(DATE_ANSWER.fullmatch(answer) or answer == DATES_ASKED for answers in offered for answer in answers)


# -- one form, end to end --------------------------------------------------------


def _command(arguments: "list[str]", small_tables_refused: bool) -> "tuple[int, str]":
    """One synthtwin command in this process: its exit code and everything it printed."""
    import contextlib

    from synthtwin import cli

    sink = io.StringIO()
    try:
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            code = cli.main(arguments, small_tables_refused=small_tables_refused)
    except SystemExit as stop:
        code = int(stop.code) if isinstance(stop.code, int) else 2
    return int(code or 0), sink.getvalue()


def run_form(
    table: Table, folder: pathlib.Path, n: int, answered: bool, seed: "int | None" = None,
    disguised: "tuple[Disguised, ...] | None" = None, twin_seeds: "tuple[int, ...]" = (),
    dates_answer: str = "", extra: "tuple[str, ...]" = (),
) -> "dict[str, object]":
    """profile (answered as the zoo answers, or not at all), generate and validate one form; what it showed.

    Returns the steps' exit codes, each disguised column's role and the
    answers its questions offer (and the answer given), the real dates
    shown in every file and on screen (`count_shown`), the twin's cells
    carrying one (`count_twin`), the checks validate missed, and the
    twin's analyst failures. `disguised` says where a case's dates sit
    (`CASES`), and `twin_seeds` the further twins to count, each against
    the real table and against an unrelated draw of it (`chance_cells`).
    At the owner's table floor (20,000 rows) the shipped command runs with
    its floor on; below it, the library's switch is off (plan P4-D425).
    `dates_answer`, where given, answers the Safe Harbor question about
    values that read as dates in place of the zoo's answer of the column
    (the column's age or ZIP question keeps the zoo's): a person answering
    `no` about ages and `yes` about dates. `extra` is handed to every
    profile run (`--missing-value ...`). A STAGE THAT FAILS IS NAMED
    (Codex's review of the first repair, item 3): `failed` lists each
    stage whose exit was not 0, or that never ran, so nothing reads a
    stage that did not finish as 0.
    """
    folder.mkdir(parents=True, exist_ok=True)
    the_seed = SEEDS.get(table.name, 0) if seed is None else seed
    header, rows = table.build(n, the_seed)
    source = folder / f"{table.name}{table.suffix}"
    source.write_bytes(table.write(header, rows))
    real = real_dates(table, header, rows, disguised)
    wider_than = {column: max(len(row[header.index(column)]) for row in rows) for column in real}
    del rows
    refused = n >= health_zoo.KPI_ROWS
    profile = folder / f"{table.name}-profile.json"
    questions = folder / f"{table.name}-questions.json"
    screen = ""
    result: "dict[str, object]" = {"table": table.name, "rows": n, "answered": answered, "steps": {}}
    steps: "dict[str, int]" = result["steps"]  # type: ignore[assignment]
    code, said = _command(["profile", f"{source}", "--replace", *extra], refused)
    steps["profile"] = code
    screen += said
    offered = {column: date_questions(questions, column) for column in real} if questions.is_file() else {}
    given: "dict[str, list[str]]" = {}
    if answered and code == 0:
        put: "set[tuple[object, ...]]" = set()
        for _round in range(health_zoo.ANSWER_ROUNDS_AT_MOST):
            document = json.loads(questions.read_text(encoding="utf-8"))
            entries = health_zoo._entries(document)
            new = [entry for entry in entries if _put_key(entry) not in put
                   and not f"{entry.get('your_answer') or ''}"]
            if _round and not new:
                break
            for column in real:
                offered[column] = offered.get(column, []) + date_questions(questions, column)
            asked, _general = health_zoo.answer_generally(table, document)
            if dates_answer:
                for entry in entries:
                    if (f"{entry.get('column', '')}" in real and sorted(health_zoo._offered(entry)) == ["no", "yes"]
                            and SAFE_HARBOR_DATES_SEEN in f"{entry.get('what_synthtwin_saw', '')}"):
                        entry["your_answer"] = dates_answer
                        asked += [{"column": entry["column"], "given": dates_answer}]
            for question in asked:
                if question["column"] in real:
                    given[question["column"]] = given.get(question["column"], []) + [question["given"]]
            put |= {_put_key(entry) for entry in entries}
            questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
            code, said = _command(["profile", f"{source}", "--replace", "--answers", f"{questions}", *extra], refused)
            steps["answers"] = code
            screen += said
            if code != 0:
                break
    if code == 0:
        code, said = _command(["generate", f"{profile}", "--replace", "--seed", "0"], refused)
        steps["generate"] = code
        screen += said
    twin = folder / f"{table.name}-twin{table.suffix}"
    if code == 0 and twin.is_file():
        code, said = _command(["validate", f"{profile}", "--replace"], refused)
        steps["validate"] = code
        screen += said
        twin_header, twin_rows = read_csv(twin)
        result["twin"] = count_twin(real, twin_header, twin_rows)
        result["wider_cells"] = {
            column: sum(1 for row in twin_rows if len(row[twin_header.index(column)]) > wider_than[column])
            for column in real if column in twin_header
        }
        quality = folder / f"{table.name}-twin-quality.txt"
        # Each miss once: the quality file says each in two sections.
        result["missed"] = sorted({
            line.strip() for line in (quality.read_text(encoding="utf-8").splitlines() if quality.is_file() else [])
            if line.rstrip().endswith("MISSED")
        })
        made = health_zoo.analyse(table, twin)
        real_found = health_zoo.analyse(table, source)
        result["analyst"] = [list(failure) for failure in health_zoo.analyst_failures(table, real_found, made)]
        del twin_rows
        if twin_seeds:
            result["chance"] = chance_cells(table, real, profile, twin, n, the_seed, refused, twin_seeds, disguised)
    try:
        described = json.loads(profile.read_text(encoding="utf-8"))
        roles = {f"{block['name']}": f"{block['role']}" for block in described["columns"]}
        blocks = {f"{block['name']}": block for block in described["columns"]}
    except (OSError, ValueError, KeyError, TypeError):
        roles = {}
        blocks = {}
    result["roles"] = {column: roles.get(column, "") for column in real}
    held_remark = _dated_values_held_remark()
    result["held"] = {column: held_remark in json.dumps(blocks.get(column, {})) for column in real}
    result["failed"] = _failed_stages(
        steps, answered and steps.get("profile") == 0, (folder / f"{table.name}-twin-quality.txt").is_file(),
    )
    if any(where.shaped for where in (DISGUISED[table.name] if disguised is None else disguised)) and profile.is_file():
        import dates_held

        held = dates_held.dates_held_few(source, folder)
        result["dates_held"] = {"few": int(held["few"]), "printed": len(held["printed"])}  # type: ignore[arg-type, call-overload]
    result["offered"] = offered
    result["given"] = given
    result["asked"] = {column: asks_the_date(found) for column, found in offered.items()}
    result["shown"] = count_shown(real, folder, screen, (source, twin))
    return result


def _put_key(entry: "dict") -> "tuple[object, ...]":
    """What makes a question the same in a later round: the zoo's key, and whether it is the question about values that read as dates.

    That question offers what the column's age or ZIP question offers, `no`
    and `yes`, and follows it in the next round (the orchestrator's LANE
    CZ-H RULINGS 6 (1), item 3), so the zoo's key alone would take it for
    the question already answered and stop.
    """
    return health_zoo._question_key(entry) + (SAFE_HARBOR_DATES_SEEN in f"{entry.get('what_synthtwin_saw', '')}",)


def _dated_values_held_remark() -> str:
    """The words a description says of a column whose values that read as dates are held (NF135)."""
    from synthtwin import taxonomy

    return taxonomy.rendered(taxonomy.REMARK_DATED_VALUES_HELD, ())


# Validate's exit where it ran to its end and named the checks the twin
# missed (each miss is recorded and owned, plan P4-D446).
VALIDATE_MISSED = 3


def _failed_stages(steps: "dict[str, int]", answered: bool, quality_written: bool) -> "list[str]":
    """Each stage of a run that did not finish: profile, the answers, generate (exit 0), validate (0, or 3 with its report)."""
    failed = [stage for stage in ["profile"] + (["answers"] if answered else []) + ["generate"] if steps.get(stage, -1) != 0]
    if steps.get("validate", -1) not in (0, VALIDATE_MISSED) or not quality_written:
        failed += ["validate"]
    return failed


def chance_cells(
    table: Table, real: "dict[str, RealDates]", profile: pathlib.Path, twin: pathlib.Path, n: int, seed: int,
    refused: bool, twin_seeds: "tuple[int, ...]", disguised: "tuple[Disguised, ...] | None",
) -> "dict[str, dict[str, int]]":
    """A real day in a twin is never recorded as chance without a measurement of the chance (the orchestrator's rulings).

    Each twin seed's cells on a real day of the table described, against
    the same cells read against an UNRELATED table: the same maker, the
    same size, another seed, whose real days the twin can know nothing of.
    Equal counts say the made-up values' room holds real days at the rate
    any made-up value meets them. One pass over each twin.
    """
    header, rows = table.build(n, seed + 7919)
    unrelated = real_dates(table, header, rows, disguised)
    del rows
    found: "dict[str, dict[str, int]]" = {}
    for other in twin_seeds:
        # NEVER THE TWIN BEFORE (Codex's review of the first repair, item 3):
        # a seed whose generation fails leaves no file to read, and is named.
        twin.unlink(missing_ok=True)
        code, _said = _command(["generate", f"{profile}", "--replace", "--seed", f"{other}"], refused)
        if code != 0 or not twin.is_file():
            found[f"{other}"] = {"exit": code if code != 0 else -1}
            continue
        twin_header, twin_rows = read_csv(twin)
        here = count_twin(real, twin_header, twin_rows)
        there = count_twin(unrelated, twin_header, twin_rows)
        del twin_rows
        found[f"{other}"] = {
            "exit": code,
            "real": sum(entry["cells"] for entry in here.values()),
            "unrelated": sum(entry["cells"] for entry in there.values()),
            "written": sum(entry["written"] for entry in here.values()),
        }
    return found


# -- the cases: what the reviews measured against the forms --------------------


@dataclasses.dataclass(frozen=True)
class Case:
    """An attack on a form: a table built from it, and where that table's dates sit.

    `answered` says whether the zoo answers it (every round); `dates_answer`
    answers the question about values that read as dates in place of the
    zoo's answer of the column (`run_form`); `extra` goes to every profile.
    """

    name: str
    table: Table
    disguised: "tuple[Disguised, ...]"
    answered: bool = True
    dates_answer: str = ""
    extra: "tuple[str, ...]" = ()


def _answers_changed(change: "Callable[[list[list[str]], random.Random, int], None]") -> Table:
    """The answer column's table with its rows changed by `change`, drawn from a seed of its own."""
    def build(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
        header, rows = answers_long(n, seed)
        change(rows, random.Random(seed + 2), n)
        return header, rows

    return dataclasses.replace(table_named("answers_long"), build=build)


def _one_stray(value: str) -> "Callable[[list[list[str]], random.Random, int], None]":
    """One answer an ordinary table may hold, under a question of its own: a ZIP, a lab value, a telephone number."""
    def change(rows: "list[list[str]]", draw: random.Random, n: int) -> None:
        place = next(place for place, row in enumerate(rows) if row[2] in YES_NO)
        rows[place][2] = "Q7001"
        rows[place][3] = value

    return change


SPELLED_KEY = "Q7002"


def _spelled(spell: "Callable[[datetime.date], str]") -> "Callable[[list[list[str]], random.Random, int], None]":
    """A key answered with the shared admission days in one spelling, on about 1 row in 40."""
    def change(rows: "list[list[str]]", draw: random.Random, n: int) -> None:
        for row in rows:
            if draw.random() < 1 / 40 and row[2] in YES_NO + FREE_TEXT + CATEGORIES:
                row[2] = SPELLED_KEY
                row[3] = spell(draw.choice(SHARED_ADMISSIONS))

    return change


def _numbers_alone(rows: "list[list[str]]", draw: random.Random, n: int) -> None:
    """The answer column with its words replaced by small numbers: no label to reach."""
    for row in rows:
        if not re.fullmatch(r"\d+(\.\d+)?", row[3]):
            row[3] = f"{draw.randint(0, 20)}"


def _mostly_days(rows: "list[list[str]]", draw: random.Random, n: int) -> None:
    """Three answers in five a shared admission day as a count: past any share a column's own reading reads."""
    for row in rows:
        if draw.random() < 0.6:
            row[2] = "Q6002"
            row[3] = f"{day_count(draw.choice(SHARED_ADMISSIONS))}"


def _numbers_few_words(rows: "list[list[str]]", draw: random.Random, n: int) -> None:
    """The answer column with its words replaced by numbers, about 3 in 100 of them a word: read as numbers beside labels or held."""
    for row in rows:
        if not re.fullmatch(r"\d+(\.\d+)?", row[3]):
            row[3] = f"{draw.gauss(100, 15):.1f}" if draw.random() < 0.97 else "Negative"


def _lab_past_the_band(rows: "list[list[str]]", draw: random.Random, n: int) -> None:
    """A key of five-figure values from 12,000 to 99,000 on about 1 row in 100, some past the band."""
    for row in rows:
        if row[2] in FREE_TEXT and draw.random() < 0.03:
            row[2] = "Q7003"
            row[3] = f"{draw.randint(12_000, 99_000)}"


ANSWER_DATES = (
    Disguised("answer_value", ("mumps",), "question_code", DAY_QUESTIONS),
    Disguised("answer_value", ("unix-seconds",), "question_code", SERVICE_TIMES),
)


def _spelling_dates(*decoders: str) -> "tuple[Disguised, ...]":
    return ANSWER_DATES + (Disguised("answer_value", decoders, "question_code", (SPELLED_KEY,)),)


def contact_days(n: int, seed: int, top: int = 12, past: int = 0, share: float = 0.0, third: bool = False) -> "tuple[list[str], list[list[str]]]":
    """Form 1's float day number alone, on one row a record, its contacts drawn from 1 to `top`.

    Three rows in five write a contact; of those, `share` past 20 up to
    `past`. `third` writes every one with a third figure after the point,
    a nought (`66123.010`).
    """
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for row in range(n):
        day = day_count(_draw_day(draw, FIRST_DAY, LAST_DAY))
        written = f"{day}"
        contact = draw.randint(1, top)
        if past and draw.random() < share:
            contact = draw.randint(21, past)
        if third:
            written = f"{day}.{contact if draw.random() < 0.6 else 0:02d}0"
        elif draw.random() < 0.6:
            written = repr(float(f"{day}.{contact:02d}"))
        rows += [[f"E{20_000_000 + 13 * row:08d}", written, draw.choice(("Final", "Corrected"))]]
    return ["encounter_id", "visit_day_number", "status_word"], rows


def _contact_table(**options: "object") -> Table:
    return Table(
        "contact_days", ".csv", lambda n, seed: contact_days(n, seed, **options),  # type: ignore[arg-type]
        lambda header, rows: health_zoo.csv_bytes(header, rows),
        {KIND_DAY_NUMBERS: ("encounter_id", "visit_day_number", "status_word")},
        # The key answered, the date question left blank and the Safe Harbor
        # one answered `yes`: what its days publish while nobody says what
        # they are. Answered as dates, they fall under the date rules.
        {"encounter_id": "identifier", "visit_day_number": "yes"},
        _csv_reader(),
        (),
    )


def _shared_results(spell: "Callable[[datetime.date], str]") -> Table:
    """Form 4 with thirty dates its date key shares among its people, in one spelling."""
    def build(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
        header, rows = results_dated(n, seed)
        draw = random.Random(seed + 2)
        days = [FIRST_DAY + datetime.timedelta(days=61 * place) for place in range(30)]
        for row in rows:
            if row[1] == RESULT_DATE_KEY:
                row[2] = spell(draw.choice(days))
        return header, rows

    return dataclasses.replace(table_named("results_dated"), build=build)


# -- the second repair's attacks (the verify of the first repair and Codex's review) --

MANY_KEYS = tuple(f"K{7_100 + place}" for place in range(210))
MANY_DATE_KEYS = (MANY_KEYS[23], MANY_KEYS[97], MANY_KEYS[160])


def many_keys(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """An answer column under 210 keys: day counts under three keys on about 1 row in 90, half on the shared admission days.

    Beside them, answers 1/0, one-decimal numbers about 76 (some past 89,
    which put the column in the age top-code's reach) and words: a column
    whose one Safe Harbor question is about ages.
    """
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for row in range(n):
        person = _person_of(row, n)
        key = draw.choice(MANY_KEYS)
        roll = draw.random()
        if roll < 0.011:
            key = draw.choice(MANY_DATE_KEYS)
            day = draw.choice(SHARED_ADMISSIONS) if draw.random() < 0.5 else _draw_day(draw, FIRST_DAY, LAST_DAY)
            value = f"{day_count(day)}"
        elif roll < 0.43:
            value = draw.choice(("1", "0", "1"))
        elif roll < 0.76:
            value = f"{draw.gauss(76, 17):.1f}"
        else:
            value = draw.choice(("none", "mild", "moderate", "severe", "declined", "other"))
        rows += [[_key(person), f"{row + 1}", key, value]]
    return ["record_id", "answer_seq", "question_code", "answer_value"], rows


def five_figure_values(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A value column of five-figure numbers from 80,000 up on most rows -- no ZIP, read in the ZIP reach -- with day counts on about 1 in 40."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for row in range(n):
        person = _person_of(row, n)
        roll = draw.random()
        if roll < 0.025:
            day = draw.choice(SHARED_ADMISSIONS) if draw.random() < 0.5 else _draw_day(draw, FIRST_DAY, LAST_DAY)
            value = f"{day_count(day)}"
        elif roll < 0.9:
            value = f"{draw.randint(80_000, 99_998)}"
        else:
            value = draw.choice(("pending", "not done"))
        rows += [[_key(person), f"{row + 1}", value]]
    return ["record_id", "line_number", "result_value"], rows


AGE_BESIDE_DAYS = SHARED_ADMISSIONS[1]


def ages_beside_days(n: int, seed: int, in_days: bool = False) -> "tuple[list[str], list[list[str]]]":
    """Ages of 40 to 100, cycling, on 24 rows in 25, and one admission day as a count on the 25th (Codex's review, item 1).

    `in_days` writes each age as days, 14,600 to 36,500, the admission
    day past the days an age of 125 years holds.
    """
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for row in range(n):
        age = 40 + row % 61
        value = f"{day_count(AGE_BESIDE_DAYS)}" if row % 25 == 24 else (f"{age * 365}" if in_days else f"{age}")
        rows += [[f"A{300_000 + 3 * row}", value, draw.choice(("Final", "Corrected"))]]
    return ["record_id", "age_value", "status_word"], rows


def readings_with_a_marker(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Readings of 150 to 219, cycling, and on 1 row in 25 the nine-figure missing marker `999999999` (Codex's review, item 2)."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for row in range(n):
        value = MISSING_MARKER if row % 25 == 24 else f"{150 + row % 70}"
        rows += [[f"M{500_000 + 7 * row}", value, draw.choice(("Final", "Corrected"))]]
    return ["record_id", "reading_value", "status_word"], rows


MISSING_MARKER = "999999999"


def charges(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Charges in cents, log-normal about 6,800 (the verify's case for item 4): a third of them lie in the day band."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for row in range(n):
        value = 2.718281828459045 ** draw.gauss(8.83, 1.08)
        rows += [[f"C{4_000_000 + 13 * row}", f"{value:.2f}", draw.choice(("Final", "Corrected", "Pending"))]]
    return ["record_id", "charge_amount", "status_word"], rows


SHARED_FORTY = tuple(datetime.date(2019, 2, 3) + datetime.timedelta(days=41 * place) for place in range(40))


def _results_mostly(mixed: bool, numbers: bool) -> "Callable[[int, int], tuple[list[str], list[list[str]]]]":
    """Form 4 with its date key on about 57 rows in 100 (the verify's item 2): month first, or month first and year first mixed.

    Two in five of the dates on forty shared days, the rest on any day of
    2019 to 2023; `numbers` keeps the form's numeric results, else words.
    """
    def build(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
        header, rows = results_dated(n, seed)
        draw = random.Random(seed + 11)
        for row in rows:
            if draw.random() < 0.57:
                row[1] = RESULT_DATE_KEY
                day = draw.choice(SHARED_FORTY) if draw.random() < 0.4 else _draw_day(draw, FIRST_DAY, LAST_DAY)
                row[2] = day.strftime("%Y-%m-%d") if mixed and draw.random() < 0.4 else day.strftime("%m-%d-%Y")
            elif not numbers and re.fullmatch(r"[-\d.]+", row[2]):
                row[2] = draw.choice(("Positive", "Negative", "Detected", "See note", "Low", "High"))
        return header, rows

    return build


def _named_table(name: str, build: "Callable[[int, int], tuple[list[str], list[list[str]]]]", columns: "tuple[str, ...]",
                 knows: "dict[str, str]", person: str = "record_id") -> Table:
    """A case's own table: the answer column's frame, its own maker, columns and answers, no checks of its own."""
    return dataclasses.replace(
        table_named("answers_long"), name=name, build=build, kinds={KIND_ANSWERS: columns}, knows=knows,
        checks=(), person=person,
    )


MANY_KEY_DATES = (Disguised("answer_value", ("mumps",), "question_code", MANY_DATE_KEYS),)
FIVE_FIGURE_DATES = (Disguised("result_value", ("mumps-in-the-span",)),)
AGE_VALUE_DATES = (Disguised("age_value", ("mumps-in-the-span",)),)
RESULTS_MOSTLY = (Disguised("result_value", ("mdy", "ymd"), "result_key", (RESULT_DATE_KEY,)),)
CONTACT_DATES = (Disguised("visit_day_number", ("mumps",)),)
RESULT_DATES = DISGUISED["results_dated"]
CASES: "tuple[Case, ...]" = (
    Case("stray_zip", _answers_changed(_one_stray("90210")), ANSWER_DATES),
    Case("stray_decimal", _answers_changed(_one_stray("12345.678")), ANSWER_DATES),
    Case("stray_negative", _answers_changed(_one_stray("-12345")), ANSWER_DATES),
    Case("stray_stamp", _answers_changed(_one_stray("44264.625")), ANSWER_DATES),
    Case("stray_telephone", _answers_changed(_one_stray("3195551212")), ANSWER_DATES),
    Case("lab_past_the_band", _answers_changed(_lab_past_the_band), ANSWER_DATES),
    Case("numbers_alone", _answers_changed(_numbers_alone), ANSWER_DATES),
    Case("numbers_few_words", _answers_changed(_numbers_few_words), ANSWER_DATES),
    Case("mostly_days", _answers_changed(_mostly_days), ANSWER_DATES),
    Case("year_short_dashed", _answers_changed(_spelled(lambda day: day.strftime("%m-%d-%y"))), _spelling_dates("mdy-short")),
    Case("year_first_dots", _answers_changed(_spelled(lambda day: day.strftime("%Y.%m.%d"))), _spelling_dates("ymd")),
    Case("dashed_with_clock", _answers_changed(_spelled(lambda day: day.strftime("%m-%d-%Y 00:00"))), _spelling_dates("mdy")),
    Case("stamp_14", _answers_changed(_spelled(lambda day: day.strftime("%Y%m%d000000"))), _spelling_dates("stamp")),
    Case("stamp_12", _answers_changed(_spelled(lambda day: day.strftime("%Y%m%d0000"))), _spelling_dates("stamp")),
    Case("year_and_day", _answers_changed(_spelled(lambda day: day.strftime("%Y-%j"))), _spelling_dates("ordinal")),
    Case("month_named", _answers_changed(_spelled(lambda day: day.strftime("%d%b%Y").upper())), _spelling_dates("month-named")),
    Case("grouped_count", _answers_changed(_spelled(lambda day: f"{day_count(day):,}")), _spelling_dates("mumps")),
    Case("count_and_seconds", _answers_changed(_spelled(lambda day: f"{day_count(day)},0")), _spelling_dates("mumps")),
    Case("signed_count", _answers_changed(_spelled(lambda day: f"+{day_count(day)}")), _spelling_dates("mumps")),
    Case("third_decimal_count", _answers_changed(_spelled(lambda day: f"{day_count(day)}.010")), _spelling_dates("mumps")),
    Case("contacts_to_30", _contact_table(top=30), CONTACT_DATES),
    Case("contacts_to_40", _contact_table(top=40), CONTACT_DATES),
    Case("contacts_past_20_on_15", _contact_table(past=60, share=0.15), CONTACT_DATES),
    Case("contacts_past_20_on_30", _contact_table(past=60, share=0.30), CONTACT_DATES),
    Case("contacts_third_figure", _contact_table(third=True), CONTACT_DATES),
    Case("results_shared_dashed", _shared_results(lambda day: day.strftime("%m-%d-%Y")), RESULT_DATES),
    Case("results_shared_short", _shared_results(lambda day: day.strftime("%m-%d-%y")),
         (Disguised("result_value", ("mdy-short",), "result_key", (RESULT_DATE_KEY,)),)),
    Case("results_shared_month_named", _shared_results(lambda day: day.strftime("%d%b%Y").upper()),
         (Disguised("result_value", ("month-named",), "result_key", (RESULT_DATE_KEY,)),)),
    # THE SECOND REPAIR: spellings the rule did not read (the verify's item 1)...
    Case("iso_zone", _answers_changed(_spelled(lambda day: day.strftime("%Y-%m-%d 00:00 EST"))), _spelling_dates("iso-lead")),
    Case("iso_bare_clock", _answers_changed(_spelled(lambda day: day.strftime("%Y-%m-%d 0000"))), _spelling_dates("iso-lead")),
    Case("weekday_named", _answers_changed(_spelled(lambda day: day.strftime("%a %b %d %Y"))), _spelling_dates("month-first-named")),
    Case("iso_basic_t", _answers_changed(_spelled(lambda day: day.strftime("%Y%m%dT000000"))), _spelling_dates("iso-basic")),
    # ...dates as text on most of a column (its item 2)...
    Case("results_mostly_mixed", dataclasses.replace(table_named("results_dated"), name="results_mostly",
                                                      build=_results_mostly(True, True), checks=()), RESULTS_MOSTLY),
    Case("results_mostly_mixed_words", dataclasses.replace(table_named("results_dated"), name="results_mostly",
                                                            build=_results_mostly(True, False), checks=()), RESULTS_MOSTLY),
    Case("results_mostly_month_first", dataclasses.replace(table_named("results_dated"), name="results_mostly",
                                                            build=_results_mostly(False, True), checks=()), RESULTS_MOSTLY),
    Case("results_mostly_month_first_words", dataclasses.replace(table_named("results_dated"), name="results_mostly",
                                                                  build=_results_mostly(False, False), checks=()), RESULTS_MOSTLY),
    # ...`no` to the age or ZIP question, `yes` to the dates question (its item 3)...
    Case("many_keys_no_to_ages", _named_table("many_keys", many_keys, ("record_id", "answer_seq", "question_code", "answer_value"),
                                              {"record_id": "identifier", "answer_seq": "identifier", "question_code": "code",
                                               "answer_value": "no"}), MANY_KEY_DATES, dates_answer="yes"),
    Case("five_figures_no_to_zips", _named_table("five_figures", five_figure_values, ("record_id", "line_number", "result_value"),
                                                 {"record_id": "identifier", "line_number": "identifier", "result_value": "no"}),
         FIVE_FIGURE_DATES, dates_answer="yes"),
    # ...and ages beside an admission day as a count (Codex's item 1): unanswered,
    # and `no` to the age question with `yes` to the dates question.
    Case("ages_beside_days", _named_table("ages_days", ages_beside_days, ("record_id", "age_value", "status_word"),
                                          {"record_id": "identifier"}, person=""), AGE_VALUE_DATES, answered=False),
    Case("ages_beside_days_no_to_ages", _named_table("ages_days", ages_beside_days, ("record_id", "age_value", "status_word"),
                                                     {"record_id": "identifier", "age_value": "no"}, person=""),
         AGE_VALUE_DATES, dates_answer="yes"),
    Case("ages_in_days_beside_days", _named_table("ages_in_days", lambda n, seed: ages_beside_days(n, seed, True),
                                                  ("record_id", "age_value", "status_word"), {"record_id": "identifier"},
                                                  person=""), AGE_VALUE_DATES, answered=False),
)
SEEDS["contact_days"] = 20261040
SEEDS["many_keys"] = 20261041
SEEDS["five_figures"] = 20261042
SEEDS["ages_days"] = 20261043
SEEDS["ages_in_days"] = 20261043
SEEDS["results_mostly"] = 20261044


MARKER_TABLE = _named_table("readings", readings_with_a_marker, ("record_id", "reading_value", "status_word"),
                            {"record_id": "identifier", "reading_value": "measurement"}, person="")
CHARGES_TABLE = _named_table("charges", charges, ("record_id", "charge_amount", "status_word"), {"record_id": "identifier"},
                             person="")
SEEDS["readings"] = 20261045
SEEDS["charges"] = 20261046


def column_run(
    table: Table, folder: pathlib.Path, n: int, column: str, extra: "tuple[str, ...]" = (), answered: bool = False,
    dates_answer: "str | None" = None,
) -> "dict[str, object]":
    """profile (unanswered, or answered as the zoo answers), generate and validate one table; one column's block, its real and twin cells.

    The cases of a column holding no date in disguise: a declared missing
    marker beside readings (`MARKER_TABLE`, Codex's review of the first
    repair, item 2) and charges a third of which lie in the day band
    (`CHARGES_TABLE`, the verify's item 4). `failed` names each stage that
    did not finish, as `run_form`'s does. `dates_answer`, where given,
    answers the question about values that read as dates in place of the
    zoo (empty: left open), as `run_form`'s does.
    """
    folder.mkdir(parents=True, exist_ok=True)
    header, rows = table.build(n, SEEDS[table.name])
    source = folder / f"{table.name}{table.suffix}"
    source.write_bytes(table.write(header, rows))
    place = header.index(column)
    real = [row[place] for row in rows]
    del rows
    refused = n >= health_zoo.KPI_ROWS
    steps: "dict[str, int]" = {}
    steps["profile"], _said = _command(["profile", f"{source}", "--replace", *extra], refused)
    questions = folder / f"{table.name}-questions.json"
    put: "set[tuple[object, ...]]" = set()
    for _round in range(health_zoo.ANSWER_ROUNDS_AT_MOST if answered and steps["profile"] == 0 else 0):
        if not questions.is_file():
            break
        document = json.loads(questions.read_text(encoding="utf-8"))
        entries = health_zoo._entries(document)
        if _round and not [entry for entry in entries if _put_key(entry) not in put and not f"{entry.get('your_answer') or ''}"]:
            break
        health_zoo.answer_generally(table, document)
        for entry in entries:
            if dates_answer is not None and SAFE_HARBOR_DATES_SEEN in f"{entry.get('what_synthtwin_saw', '')}":
                entry["your_answer"] = dates_answer
        put |= {_put_key(entry) for entry in entries}
        questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
        steps["answers"], _said = _command(["profile", f"{source}", "--replace", "--answers", f"{questions}", *extra], refused)
        if steps["answers"] != 0:
            break
    profile = folder / f"{table.name}-profile.json"
    twin = folder / f"{table.name}-twin{table.suffix}"
    quality = folder / f"{table.name}-twin-quality.txt"
    found: "dict[str, object]" = {"steps": steps, "real": real}
    if steps["profile"] == 0 and steps.get("answers", 0) == 0:
        steps["generate"], _said = _command(["generate", f"{profile}", "--replace", "--seed", "0"], refused)
    if steps.get("generate") == 0 and twin.is_file():
        steps["validate"], _said = _command(["validate", f"{profile}", "--replace"], refused)
        twin_header, twin_rows = read_csv(twin)
        found["twin"] = [row[twin_header.index(column)] for row in twin_rows]
        found["missed"] = sorted({
            line.strip() for line in (quality.read_text(encoding="utf-8").splitlines() if quality.is_file() else [])
            if line.rstrip().endswith("MISSED")
        })
    if profile.is_file():
        described = json.loads(profile.read_text(encoding="utf-8"))
        found["block"] = next((block for block in described["columns"] if block["name"] == column), {})
    found["failed"] = _failed_stages(steps, answered and "answers" in steps, quality.is_file())
    return found


# The cases before the second repair's: those after it record whether their
# disguised columns are held by the value rule (`case_values`).
FIRST_REPAIR_CASES = next(place for place, case in enumerate(CASES) if case.name == "iso_zone")


def run_counts(result: "dict[str, object]", own_forms_alone: bool) -> "tuple[int, int, int]":
    """A run's real dates shown (with those written as dates anywhere), twin cells carrying one, columns not asked."""
    shown = twin = not_asked = 0
    found = result["shown"]
    made = result.get("twin", {})
    for column, entry in found.items():  # type: ignore[attr-defined]
        shown += int(entry["days"])
        if not own_forms_alone:
            shown += int(entry["other_forms"]) + int(entry["elsewhere"])
        if made:
            twin += int(made[column]["cells"])  # type: ignore[index]
        not_asked += 0 if result["asked"].get(column) else 1  # type: ignore[attr-defined]
    return shown, twin, not_asked


def case_values(name: str, result: "dict[str, object]", second_repair: bool) -> "dict[str, object]":
    """One attack's K-HZ-16 keys from its run, or none where a stage failed: a key not measured is never read as 0.

    Codex's review of the first repair, item 3: a run whose generation
    failed read as 0 twin cells and 0 misses.
    """
    if result.get("failed"):
        return {}
    shown, twin, not_asked = run_counts(result, name.startswith("contacts_"))
    found: "dict[str, object]" = {
        f"case_{name}_shown": shown,
        f"case_{name}_twin": twin,
        f"case_{name}_misses": len(result.get("missed", [])),  # type: ignore[arg-type]
    }
    if result.get("answered"):
        found[f"case_{name}_not_asked"] = not_asked
    if second_repair:
        found[f"case_{name}_not_held"] = sum(1 for held in result["held"].values() if not held)  # type: ignore[attr-defined]
    return found


def case_named(name: str) -> Case:
    """The case of that name."""
    for case in CASES:
        if case.name == name:
            return case
    raise KeyError(name)


# -- the price: what the two rules reach over the zoo ----------------------------


def _in_the_contact_band(table: Table, rows: int) -> bool:
    """Whether a column of the table could meet the contact rule: its cells, as numbers, have a median in the band.

    The contact rule changes question Q3 only for a column of counts
    whose figures after the point are contacts, read as days since 1840
    inside the band from 1990 (`date_counts.band`); a table with no
    column whose numbers' median lies there is described once.
    """
    from synthtwin import date_counts

    low, high = date_counts.band(date_counts.DAYS_SINCE_1840, date_counts.NARROW_FROM)
    header, body = table.build(rows, health_zoo.seed_of(table))
    for place in range(len(header)):
        numbers: "list[float]" = []
        for row in body:
            try:
                numbers += [float(row[place])]
            except ValueError:
                continue
        if numbers and low <= sorted(numbers)[len(numbers) // 2] < high:
            return True
    return False


def values_held_not_dates(table: Table, rows: int) -> "tuple[int, int]":
    """Of a key-value form's cells that `date_counts.dated_values_blanked` holds, all of them and those under no date's key.

    The second number is the price of the per-column question: a value
    that reads as a date, held though its key holds none. (0, 0) for a
    table with no key column. One pass over the rows.
    """
    from synthtwin import date_counts

    header, body = table.build(rows, SEEDS[table.name])
    held = not_dates = 0
    keyed: "dict[str, set[str]]" = {}
    key_place: "dict[str, int]" = {}
    for where in DISGUISED[table.name]:
        # A clock key holds no date (LANE CZ-H RULINGS 3 (2)).
        if where.key_column and "clock" not in where.decoders:
            keyed.setdefault(where.column, set()).update(where.keys)
            key_place[where.column] = header.index(where.key_column)
    for column, keys in keyed.items():
        place = header.index(column)
        cells = [row[place] for row in body]
        blanked = date_counts.dated_values_blanked(cells)
        if blanked is None:
            continue
        for row, cell, kept in zip(body, cells, blanked):
            if cell.strip() and not kept:
                held += 1
                not_dates += 0 if row[key_place[column]] in keys else 1
    return held, not_dates


def _held_cells(table: Table, rows: int, column: str) -> int:
    """How many of a column's cells read as dates in disguise, as the rule holds them."""
    from synthtwin import date_counts

    header, body = table.build(rows, health_zoo.seed_of(table))
    place = header.index(column)
    cells = [row[place] for row in body]
    blanked = date_counts.dated_values_blanked(cells)
    if blanked is None:
        return 0
    return sum(1 for cell, kept in zip(cells, blanked) if cell.strip() and not kept)


def zoo_price(folder: pathlib.Path, rows: int) -> "dict[str, object]":
    """The WHOLE catalogue but the forms, workbooks too, described at `rows`, unanswered and answered: what the two rules reach, by name.

    `dated`: columns holding values that read as dates, put the Safe
    Harbor question while no question holds them whole, with the cells
    held; `dated_answered`: those still held once the zoo has answered as
    it does (a column it answers `no` frees itself); `q3_new`: columns put
    question Q3 only because of the contact rule (described again with
    `date_counts.contacts_shaped` answering False), and `q3_lost` the
    reverse, which must be none. Each named ``table.column``. The tables
    are written under `folder` and removed.
    """
    import contextlib
    import shutil

    from synthtwin import cli, date_counts, profile

    real_describe = profile.build_document
    real_shaped = date_counts.contacts_shaped
    captured: "list[list[str]]" = []

    def described(*arguments: object, **options: object) -> "dict[str, object]":
        named = options.get("dated_values")
        document = real_describe(*arguments, **options)  # type: ignore[arg-type]
        if isinstance(named, list):
            captured[len(captured):] = [[f"{name}" for name in named]]
        return document

    def command(arguments: "list[str]") -> int:
        sink = io.StringIO()
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            return int(cli.main(arguments, small_tables_refused=rows >= health_zoo.KPI_ROWS) or 0)

    def q3_columns(table: Table, where: pathlib.Path) -> "set[str]":
        path = where / f"{table.name}-questions.json"
        if not path.is_file():
            return set()
        document = json.loads(path.read_text(encoding="utf-8"))
        return {
            f"{entry.get('column', '')}" for entry in health_zoo._entries(document)
            if any(answer in date_counts.TABLE for answer in health_zoo._offered(entry))
        }

    found: "dict[str, object]" = {"dated": [], "dated_answered": [], "dated_cells": {}, "q3_new": [], "q3_lost": []}
    forms_here = {table.name for table in TABLES}
    profile.build_document = described  # type: ignore[assignment]
    try:
        for table in health_zoo.runnable_tables(health_zoo.catalogue()):
            if table.name in forms_here:
                continue
            where = folder / "with"
            where.mkdir(parents=True, exist_ok=True)
            source = health_zoo.write_table(table, where, rows, health_zoo.seed_of(table))
            del captured[:]
            code = command(["profile", f"{source}", "--replace"])
            names = sorted({name for named in captured for name in named})
            with_rule = q3_columns(table, where) if code == 0 else set()
            answers = where / f"{table.name}-questions.json"
            put: "set[tuple[object, ...]]" = set()
            for _round in range(health_zoo.ANSWER_ROUNDS_AT_MOST):
                if code != 0 or not answers.is_file():
                    break
                document = json.loads(answers.read_text(encoding="utf-8"))
                entries = health_zoo._entries(document)
                if _round and not [
                    entry for entry in entries
                    if _put_key(entry) not in put and not f"{entry.get('your_answer') or ''}"
                ]:
                    break
                health_zoo.answer_generally(table, document)
                put |= {_put_key(entry) for entry in entries}
                answers.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
                del captured[:]
                code = command(["profile", f"{source}", "--replace", "--answers", f"{answers}"])
                names = sorted(set(names) | {name for named in captured for name in named})
            still = sorted({name for named in captured[-1:] for name in named})
            found["dated"] += [f"{table.name}.{name}" for name in names]  # type: ignore[operator]
            found["dated_answered"] += [f"{table.name}.{name}" for name in still]  # type: ignore[operator]
            for name in names:
                found["dated_cells"][f"{table.name}.{name}"] = _held_cells(table, rows, name)  # type: ignore[index]
            without_rule = with_rule
            if _in_the_contact_band(table, rows):
                date_counts.contacts_shaped = lambda with_contact, small: False  # type: ignore[assignment]
                try:
                    shutil.rmtree(folder / "without", ignore_errors=True)
                    (folder / "without").mkdir(parents=True)
                    again = health_zoo.write_table(table, folder / "without", rows, health_zoo.seed_of(table))
                    command(["profile", f"{again}", "--replace"])
                    without_rule = q3_columns(table, folder / "without")
                finally:
                    date_counts.contacts_shaped = real_shaped  # type: ignore[assignment]
            found["q3_new"] += [f"{table.name}.{name}" for name in sorted(with_rule - without_rule)]  # type: ignore[operator]
            found["q3_lost"] += [f"{table.name}.{name}" for name in sorted(without_rule - with_rule)]  # type: ignore[operator]
            shutil.rmtree(folder / "with", ignore_errors=True)
            shutil.rmtree(folder / "without", ignore_errors=True)
    finally:
        profile.build_document = real_describe  # type: ignore[assignment]
    return found


def battery_price(folder: pathlib.Path) -> "dict[str, list[str]]":
    """The chance battery, the counted shapes and the stage-3 battery described as the command describes: the columns the value rule names.

    Ten draws of each ordinary and stated generator side by side at 1,000
    rows, each counted shape, each stage-3 shape. Before the rule the
    answer is none, by construction: no describe named a column.
    """
    import counted_dates
    import stage3_battery

    from synthtwin import profile, reading, taxonomy

    folder.mkdir(parents=True, exist_ok=True)
    reached: "list[str]" = []
    columns = 0

    def describe(name: str, header: "list[str]", body: "list[list[str]]") -> None:
        nonlocal columns, reached
        path = folder / f"{name}.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(header)
            writer.writerows(body)
        named: "list[str]" = []
        profile.build_document(
            reading.read_table(f"{path}"), taxonomy.Settings(), [], top_code=True, safe_harbor_no=[], dated_values=named,
        )
        columns += len(header)
        reached += named
        path.unlink()

    for source, maker in ((counted_dates.ORDINARY, counted_dates.ordinary), (counted_dates.STATED, counted_dates.stated)):
        for name in sorted(source):
            draws = [maker(name, 1000, number) for number in range(10)]
            describe(name, [f"{name}_{number}" for number in range(10)], [list(row) for row in zip(*draws)])
    for shape in counted_dates.SHAPES:
        cells, _truth = counted_dates.cells(shape, 1000, 0)
        describe(f"shape_{shape.name}", [shape.name], [[cell] for cell in cells])
    for name, build in sorted(stage3_battery.SHAPES.items()):
        built = build(random.Random(stage3_battery.BATTERY_SEED))
        cells = built[0] if isinstance(built, tuple) else built
        if isinstance(cells, list) and cells and all(isinstance(cell, str) for cell in cells):
            describe(f"stage3_{name}", [name], [[cell] for cell in cells])
    return {"reached": reached, "columns": [f"{columns}"]}

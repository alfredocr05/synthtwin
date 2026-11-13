"""Lane SH3's shapes (plan P4-D454): ages in other units and parts of an address, beside their false alarms.

Shared by the gate (`tests/test_safe_harbor_ages_and_address_parts.py`)
and K-HZ-20's driver (`tools/measurements/kpi_ages_and_address_parts.py`),
so the two measure the same columns with the same counters. Each table
is built by the standard library's own seeded generator from values
chosen here; no value comes from any real table. A health table can hold
each of these forms: an age counted in months, weeks or days, with its
unit in the column's name or in each cell; an age with decimals; an age
at death or at an event filled on a few rows; a house number, an
apartment, unit or suite number, a district or a county code, several
address blocks on one row. Standard library only: the driver loads
this before synthtwin.

THE MARK: 90 years in each unit, the smallest whole number of the unit
that may be an age of 90 or more -- 90 years, 1,080 months, 4,695 weeks
(a person 4,695 weeks old has lived 32,865 to 32,871 days) and 32,871
days (90 times 365 and the fewest leap days, 21, that 90 years hold).
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import pathlib
import random
import re
import typing

YEARS = "y"
MONTHS = "m"
WEEKS = "w"
DAYS = "d"
MARK = {YEARS: 90, MONTHS: 1080, WEEKS: 4695, DAYS: 32871}
# The unit words a cell may carry, read whole and in small letters.
UNIT_WORDS = {
    "y": YEARS, "yr": YEARS, "yrs": YEARS, "year": YEARS, "years": YEARS,
    "m": MONTHS, "mo": MONTHS, "mos": MONTHS, "month": MONTHS, "months": MONTHS,
    "w": WEEKS, "wk": WEEKS, "wks": WEEKS, "week": WEEKS, "weeks": WEEKS,
    "d": DAYS, "day": DAYS, "days": DAYS, "dy": DAYS, "dys": DAYS,
    "mth": MONTHS, "mths": MONTHS,
    # ...and an age's own affixes (lane SH3's repair): `100 y/o`, `9 m/o`,
    # `1 y.o.`, `yo`, a unit word before `old` (`92-year-old`).
    "y/o": YEARS, "yo": YEARS, "y.o": YEARS, "m/o": MONTHS, "w/o": WEEKS, "d/o": DAYS,
}
_CELL = re.compile(r"\s*\+?(-?\d+(?:\.\d+)?)[\s-]{0,2}([A-Za-z]*(?:/[A-Za-z]|\.[oO])?)\.?(?:[\s-][oO][lL][dD])?\s*$")

AGE = "age"
ADDRESS = "address"
PLAIN = "plain"
# ...a column of record numbers its values alone may read as ages, and a
# column naming the patient a row is about (lane SH3's repair).
RECORD = "record"
PERSON = "person"


class Column(typing.NamedTuple):
    """One column of a form: its name, what it is, its unit, its cells' maker and its truthful answers."""

    name: str
    kind: str
    unit: str
    make: "typing.Callable[[random.Random], str]"
    answers: "tuple[str, ...]"


def _age(unit: str, top: int, share_over: float, places: int = 0) -> "typing.Callable[[random.Random], str]":
    mark = MARK[unit]

    def make(draw: random.Random) -> str:
        if draw.random() < share_over:
            value = draw.uniform(mark, top) if places else draw.randint(mark, top)
        else:
            value = draw.uniform(0, mark - 1) if places else draw.randint(0, mark - 1)
        return f"{value:.{places}f}" if places else f"{value}"

    return make


def _few_old(unit: str, top: int, old: int) -> "typing.Callable[[random.Random], str]":
    """Ages of a unit, the first ``old`` cells drawn past the mark and every other one below it: a top category of 1 to 10 people."""
    mark = MARK[unit]

    def make(draw: random.Random) -> str:
        # ...counted on the generator itself, a new one for each table built.
        drawn = getattr(draw, "drawn_so_far", 0) + 1
        setattr(draw, "drawn_so_far", drawn)
        return f"{draw.randint(mark, top) if drawn <= old else draw.randint(0, mark - 1)}"

    return make


def _sparse(share: float, inner: "typing.Callable[[random.Random], str]") -> "typing.Callable[[random.Random], str]":
    return lambda draw: inner(draw) if draw.random() < share else ""


def _decimal_years(draw: random.Random) -> str:
    pick = draw.random()
    if pick < 0.03:
        return "89.99"
    if pick < 0.06:
        return "90.0"
    if pick < 0.12:
        return f"{draw.uniform(90, 104):.2f}"
    return f"{draw.uniform(0, 89.9):.2f}"


# An age written with its unit in each cell: infants in days, weeks and
# months, everyone else in years, a few past the mark in every unit.
def _unit_in_cell(draw: random.Random) -> str:
    pick = draw.random()
    if pick < 0.08:
        return f"{draw.randint(0, 27)} d"
    if pick < 0.14:
        return f"{draw.randint(1, 52)} wk"
    if pick < 0.24:
        return f"{draw.randint(1, 35)} months"
    if pick < 0.26:
        return f"{draw.randint(1080, 1240)} months"
    if pick < 0.28:
        return f"{draw.randint(32871, 37000)} days"
    if pick < 0.36:
        return f"{draw.randint(90, 104)} years"
    return f"{draw.randint(3, 89)} years"


def _affixed(affix: str, unit: str, top: int, share_over: float) -> "typing.Callable[[random.Random], str]":
    """Ages of a unit written with an age's own affix (`95 y/o`, `92-year-old`, `14 m/o`), a share past the mark."""
    bare = _age(unit, top, share_over)
    return lambda draw: bare(draw) + affix


def _ages_in_text(draw: random.Random) -> str:
    """Ages written as text in several units and affixes, a tenth past 89 years."""
    pick = draw.random()
    if pick < 0.10:
        return f"{draw.randint(90, 104)} y/o"
    if pick < 0.20:
        return f"{draw.randint(1, 23)} m/o"
    if pick < 0.30:
        return f"{draw.randint(1, 11)} months old"
    if pick < 0.40:
        return f"{draw.randint(18, 89)}-year-old"
    return f"{draw.randint(2, 89)} y/o"


def _years_beside(share: float, low: int, high: int) -> "typing.Callable[[random.Random], str]":
    """Ages in years 18 to 105, a tenth past 89, beside a share of bare numbers from ``low`` to ``high`` (strays, or infants' ages in days)."""
    years = _age(YEARS, 105, 0.10)
    return lambda draw: f"{draw.randint(low, high)}" if draw.random() < share else f"{max(18, int(years(draw)))}"


def _with_nines(share: float, inner: "typing.Callable[[random.Random], str]") -> "typing.Callable[[random.Random], str]":
    """``inner``'s cells beside `999` on a share of the rows, a value of the column (83 years in months), no placeholder."""
    return lambda draw: "999" if draw.random() < share else inner(draw)


def _cycling(values: "tuple[str, ...]") -> "typing.Callable[[random.Random], str]":
    """``values`` in turn, row after row (counted on the generator itself)."""

    def make(draw: random.Random) -> str:
        drawn = getattr(draw, "drawn_so_far", 0)
        setattr(draw, "drawn_so_far", drawn + 1)
        return values[drawn % len(values)]

    return make


# A LONG TABLE: ten rows a patient, each patient's age the same on all ten,
# and four patients past 89 (40 rows): a top category of 4 people.
LONG_ROWS = 10
LONG_OLD = {7: 92, 500: 95, 1200: 98, 1900: 101}


def _long_patient(draw: random.Random) -> str:
    drawn = getattr(draw, "drawn_so_far", 0)
    setattr(draw, "drawn_so_far", drawn + 1)
    return f"P{drawn // LONG_ROWS:05d}"


def _long_age(draw: random.Random) -> str:
    drawn = getattr(draw, "drawn_so_far", 0)
    setattr(draw, "drawn_so_far", drawn + 1)
    patient = drawn // LONG_ROWS
    if patient in LONG_OLD:
        return f"{LONG_OLD[patient]}"
    return f"{random.Random(f'long/{patient}').randint(18, 89)}"


def _pick(values: "tuple[str, ...]") -> "typing.Callable[[random.Random], str]":
    return lambda draw: draw.choice(values)


def _between(low: int, high: int, pad: int = 0) -> "typing.Callable[[random.Random], str]":
    return lambda draw: f"{draw.randint(low, high):0{pad}d}" if pad else f"{draw.randint(low, high)}"


def _apartment(draw: random.Random) -> str:
    return f"{draw.randint(1, 30)}{draw.choice('ABCDEF')}" if draw.random() < 0.5 else f"{draw.randint(101, 2412)}"


def _suite(draw: random.Random) -> str:
    return f"Suite {draw.randint(1, 9) * 100 + draw.randint(0, 40)}" if draw.random() < 0.6 else f"{draw.randint(100, 940)}"


def _often_blank(share: float, inner: "typing.Callable[[random.Random], str]") -> "typing.Callable[[random.Random], str]":
    return lambda draw: inner(draw) if draw.random() < share else ""


# The answers a truthful person gives, in the order a question offers
# them: an age holding one of 90 years or more is `yes` to the Safe Harbor
# question and a `measurement`; its unit where asked; a part of an
# address is `yes` and a `code`; a false alarm is `no`.
AGE_ANSWERS = ("yes", "measurement", "keep")
ADDRESS_ANSWERS = ("yes", "code", "keep")
COUNT_ANSWERS = ("no", "measurement", "keep")
CODE_ANSWERS = ("no", "code", "keep")
# ...a record number: `yes` to the Safe Harbor question (it may name a
# person), `identifier` where asked (beside 100 different numbers the
# table then holds 100 people, and at 20,000 rows the command refuses it
# under the owner's table floor, writing nothing: the description and the
# twin of the round before stand); a patient column names its patient.
RECORD_ANSWERS = ("yes", "identifier", "keep")
PERSON_ANSWERS = ("identifier", "keep")

FORMS: "dict[str, tuple[Column, ...]]" = {
    # Ages with their unit in the column's name, bare figures in the cells.
    "ages_named": (
        Column("age_in_years", AGE, YEARS, _age(YEARS, 110, 0.08), AGE_ANSWERS),
        Column("age_in_months", AGE, MONTHS, _age(MONTHS, 1300, 0.10), ("months",) + AGE_ANSWERS),
        Column("age_in_weeks", AGE, WEEKS, _age(WEEKS, 5600, 0.10), ("weeks",) + AGE_ANSWERS),
        Column("age_in_days", AGE, DAYS, _age(DAYS, 40000, 0.10), ("days",) + AGE_ANSWERS),
        Column("age (days)", AGE, DAYS, _age(DAYS, 38000, 0.06), ("days",) + AGE_ANSWERS),
        Column("AgeMonths", AGE, MONTHS, _age(MONTHS, 1250, 0.05), ("months",) + AGE_ANSWERS),
        # ...and ages in days all younger than 90, five figures as a ZIP has.
        Column("age_days_young", AGE, DAYS, _between(0, 20000), ("days",) + AGE_ANSWERS),
        # ...and ages in months beside `999` on a twentieth of the rows: 83
        # years, a value, never a placeholder (lane SH3's repair).
        Column("age_mos_nines", AGE, MONTHS, _with_nines(0.05, _age(MONTHS, 1300, 0.10)), AGE_ANSWERS),
        # Ages named with `old` after their unit.
        Column("months_old", AGE, MONTHS, _age(MONTHS, 1300, 0.10), AGE_ANSWERS),
        Column("days_old", AGE, DAYS, _age(DAYS, 40000, 0.10), AGE_ANSWERS),
        Column("years_old", AGE, YEARS, _age(YEARS, 110, 0.08), AGE_ANSWERS),
    ),
    # The gate's one case at the table floor: months, weeks and days by name,
    # and a top category of 1 to 10 rows in years and in days, pooled.
    "units_at_the_floor": (
        Column("age_in_months", AGE, MONTHS, _age(MONTHS, 1300, 0.10), ("months",) + AGE_ANSWERS),
        Column("age_in_weeks", AGE, WEEKS, _age(WEEKS, 5600, 0.10), ("weeks",) + AGE_ANSWERS),
        Column("age_in_days", AGE, DAYS, _age(DAYS, 40000, 0.10), ("days",) + AGE_ANSWERS),
        Column("age_years_few", AGE, YEARS, _few_old(YEARS, 104, 6), AGE_ANSWERS),
        Column("age_days_few", AGE, DAYS, _few_old(DAYS, 36000, 8), AGE_ANSWERS),
    ),
    # A long table, ten rows a patient: a top category of 4 PEOPLE (40 rows)
    # pooled, counted in people (lane SH3's repair; K-HZ-20 at 20,000 rows).
    "ages_long_table": (
        Column("person_key", PERSON, "", _long_patient, PERSON_ANSWERS),
        Column("age", AGE, YEARS, _long_age, AGE_ANSWERS),
    ),
    # Ages with their unit written in each cell.
    "ages_in_cells": (
        Column("age_written", AGE, "", _unit_in_cell, AGE_ANSWERS),
        Column("age_letter", AGE, "", lambda draw: f"{draw.randint(0, 104)}y" if draw.random() < 0.7 else f"{draw.randint(1, 1300)}m", AGE_ANSWERS),
        # Ages written with an age's own affix, the label route included.
        Column("age", AGE, YEARS, _affixed(" y/o", YEARS, 104, 0.10), AGE_ANSWERS),
        Column("pt_age", AGE, YEARS, _affixed("-year-old", YEARS, 104, 0.10), AGE_ANSWERS),
        Column("child_age", AGE, MONTHS, _affixed(" m/o", MONTHS, 1250, 0.10), AGE_ANSWERS),
        Column("age_txt", AGE, YEARS, _ages_in_text, AGE_ANSWERS),
    ),
    # Decimal ages, an age at death on a few rows, ages at an event.
    "ages_decimal_and_events": (
        Column("age_decimal", AGE, YEARS, _decimal_years, AGE_ANSWERS),
        Column("age_at_death", AGE, YEARS, _sparse(0.04, _age(YEARS, 106, 0.4)), AGE_ANSWERS),
        Column("age_at_diagnosis_days", AGE, DAYS, _sparse(0.3, _age(DAYS, 36500, 0.08)), ("days",) + AGE_ANSWERS),
        Column("death_age_days", AGE, DAYS, _sparse(0.05, _age(DAYS, 39000, 0.3)), ("days",) + AGE_ANSWERS),
    ),
    # A top category of 1 to 10 people: pooled, never named.
    "ages_few_old": (
        Column("age_years_few", AGE, YEARS, _few_old(YEARS, 104, 6), AGE_ANSWERS),
        Column("age_days_few", AGE, DAYS, _few_old(DAYS, 36000, 8), ("days",) + AGE_ANSWERS),
    ),
    # Ages with no unit anywhere: the name says age, the values say not years.
    "ages_bare": (
        Column("age", AGE, MONTHS, _age(MONTHS, 1300, 0.10), ("months",) + AGE_ANSWERS),
        Column("person_age", AGE, DAYS, _age(DAYS, 40000, 0.10), ("days",) + AGE_ANSWERS),
        # ...and infants' ages in days, under 1,300: read in years until the
        # unit is answered (lane SH3's repair).
        Column("infant_age", AGE, DAYS, _between(0, 1300), ("days",) + AGE_ANSWERS),
        # Ages in years beside strays past 125, or infants' ages written as bare
        # days: read in years until the unit is answered.
        Column("age_at_visit", AGE, YEARS, _years_beside(0.07, 126, 2000), AGE_ANSWERS),
        Column("age_mixed_bare", AGE, YEARS, _years_beside(0.15, 126, 365), AGE_ANSWERS),
    ),
    # Parts of an address smaller than a state, two blocks on one row.
    "address_parts": (
        Column("house_no", ADDRESS, "", _between(1, 9999), ADDRESS_ANSWERS),
        Column("street_no", ADDRESS, "", _between(1, 2500), ADDRESS_ANSWERS),
        Column("apt", ADDRESS, "", _often_blank(0.4, _apartment), ADDRESS_ANSWERS),
        Column("unit_number", ADDRESS, "", _often_blank(0.3, _between(1, 1800)), ADDRESS_ANSWERS),
        Column("suite", ADDRESS, "", _often_blank(0.2, _suite), ADDRESS_ANSWERS),
        Column("district_code", ADDRESS, "", _between(1, 48), ADDRESS_ANSWERS),
        Column("county_code", ADDRESS, "", _between(1, 199, 3), ADDRESS_ANSWERS),
        Column("home_house_no", ADDRESS, "", _between(1, 8800), ADDRESS_ANSWERS),
        Column("home_apt", ADDRESS, "", _often_blank(0.3, _apartment), ADDRESS_ANSWERS),
        Column("mail_house_number", ADDRESS, "", _often_blank(0.6, _between(1, 12000)), ADDRESS_ANSWERS),
        Column("mail_apt", ADDRESS, "", _often_blank(0.2, _apartment), ADDRESS_ANSWERS),
        # ...and the names of parts the first list missed (lane SH3's repair), a
        # unit number written as a clock is, and two parts in one name.
        Column("hse_no", ADDRESS, "", _between(1, 9999), ADDRESS_ANSWERS),
        Column("bldg_no", ADDRESS, "", _between(1, 9999), ADDRESS_ANSWERS),
        Column("building_num", ADDRESS, "", _between(1, 9999), ADDRESS_ANSWERS),
        Column("po_box", ADDRESS, "", _between(1, 9999), ADDRESS_ANSWERS),
        Column("flat_no", ADDRESS, "", _between(1, 400), ADDRESS_ANSWERS),
        Column("apt_suite", ADDRESS, "", _often_blank(0.4, _apartment), ADDRESS_ANSWERS),
        Column("unit_no", ADDRESS, "", _cycling(("13:01", "13:02", "13:03", "13:04")), ADDRESS_ANSWERS),
        # ...and a street number run together, a post office box with its
        # letters apart (lane SH3's second repair).
        Column("streetno", ADDRESS, "", _between(1, 9999), ADDRESS_ANSWERS),
        Column("p_o_box", ADDRESS, "", _between(1, 9999), ADDRESS_ANSWERS),
        Column("box_number", ADDRESS, "", _between(1, 9999), ADDRESS_ANSWERS),
    ),
    # Columns named like ages or houses that are neither: the false alarms.
    "named_alike": (
        Column("age_group", PLAIN, "", _between(1, 9), CODE_ANSWERS),
        Column("ages_seen", PLAIN, "", _between(0, 300), COUNT_ANSWERS),
        Column("household_size", PLAIN, "", _between(1, 12), COUNT_ANSWERS),
        Column("gestational_age_weeks", PLAIN, "", _between(22, 42), COUNT_ANSWERS),
        Column("stay_days", PLAIN, "", _between(0, 400), COUNT_ANSWERS),
        Column("months_on_therapy", PLAIN, "", _between(0, 240), COUNT_ANSWERS),
        Column("unit", PLAIN, "", _pick(("Ward A", "Ward B", "4 West", "5 East", "3 North", "Step-down", "Day unit")), CODE_ANSWERS),
        Column("insulin_units", PLAIN, "", _between(0, 60), COUNT_ANSWERS),
        Column("unit_cost", PLAIN, "", lambda draw: f"{draw.uniform(0.5, 900):.2f}", COUNT_ANSWERS),
    ),
    # Record numbers 1 to 100 its values alone may read as ages, in a table of
    # their own (answered `identifier` they would name the people every other
    # column is counted in): `yes` holds them whole, as before lane SH3 (the
    # orchestrator's LANE SH3 RULINGS 1 (1)). Its name says nothing (batch
    # 4o's merge): lane HB's key names read `patient_number` as a key (plan
    # P4-D442) and put its identifier question first, so the values alone
    # would no longer be what reads it.
    "record_numbers_like_ages": (
        Column("register_entry", RECORD, "", _cycling(tuple(f"{number}" for number in range(1, 101))), RECORD_ANSWERS),
    ),
}


def build(form: str, n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """One form's header and ``n`` rows from ``seed``: each column drawn from its own generator."""
    columns = FORMS[form]
    draws = [random.Random(f"{form}/{column.name}/{seed}") for column in columns]
    rows = [[column.make(draws[place]) for place, column in enumerate(columns)] for _row in range(n)]
    return [column.name for column in columns], rows


def write(folder: pathlib.Path, form: str, n: int, seed: int) -> pathlib.Path:
    """The form written as `t.csv` in ``folder``."""
    header, rows = build(form, n, seed)
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "t.csv"
    with open(table, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    return table


def quiet(main: "typing.Callable[..., int]", arguments: "list[str]", **switches: object) -> int:
    """One synthtwin command, its output kept off the screen."""
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return main(arguments, **switches)


def _entries(document: "dict") -> "list[dict]":
    found: "list[dict]" = []
    for key in ("about_your_file", "asked"):
        found += [one for one in (document.get(key) or []) if isinstance(one, dict) and "answers_you_can_give" in one]
    checklist = document.get("checklist") or {}
    found += [one for one in (checklist.get("columns") or []) if isinstance(one, dict) and "answers_you_can_give" in one]
    return found


def questions_put(folder: pathlib.Path, saw: bool = False) -> "dict[str, list[str]]":
    """Each column's open questions in the questions file, as the answers each offers (and the opening of what each saw, where ``saw``)."""
    path = folder / "t-questions.json"
    put: "dict[str, list[str]]" = {}
    if not path.is_file():
        return put
    for entry in _entries(json.loads(path.read_text(encoding="utf-8"))):
        offered = "/".join(f"{choice.get('answer')}" for choice in entry["answers_you_can_give"])
        if saw:
            offered += " (" + f"{entry.get('what_synthtwin_saw', '')}"[:60] + ")"
        put.setdefault(f"{entry.get('column', '')}", []).append(offered)
    return put


def profile(main: "typing.Callable[..., int]", table: pathlib.Path, answered: bool, floor_on: bool, form: str = "") -> "list[str]":
    """`profile` on the table, then, where ``answered``, every round answered truthfully; the answers given.

    The answers are those of ``form``'s columns, where it is named (two
    forms may hold columns of one name, `age` in years and in months).
    """
    columns = {column.name: column for one in FORMS.values() for column in one}
    if form:
        columns = {column.name: column for column in FORMS[form]}
    switches = {"small_tables_refused": floor_on}
    code = quiet(main, ["profile", f"{table}", "--replace"], **switches)
    assert code in (0, 3), code
    given: "list[str]" = []
    questions = table.parent / "t-questions.json"
    for round_number in range(5):
        if not answered or not questions.is_file():
            return given
        document = json.loads(questions.read_text(encoding="utf-8"))
        changed = False
        for entry in _entries(document):
            if f"{entry.get('your_answer', '')}":
                continue
            offered = [f"{choice.get('answer')}" for choice in entry["answers_you_can_give"]]
            column = columns.get(f"{entry.get('column', '')}")
            if column is None:
                continue
            pick = next((answer for answer in column.answers if answer in offered), "")
            if pick:
                entry["your_answer"] = pick
                changed = True
                given += [f"{round_number}:{column.name}={pick}"]
        if not changed:
            return given
        questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
        code = quiet(main, ["profile", f"{table}", "--replace", "--answers", f"{questions}"], **switches)
        # ...exit 1 where an answer leaves the table under the owner's table
        # floor (100 people): refused, writing nothing; the round before stands.
        assert code in (0, 3) or (code == 1 and floor_on), code
        if code == 1:
            given += [f"{round_number}:(refused)=floor"]
            return given
    return given


def generate(main: "typing.Callable[..., int]", folder: pathlib.Path) -> "dict[str, list[str]]":
    """`generate` at seed 0; the twin's columns by name."""
    assert quiet(main, ["generate", f"{folder / 't-profile.json'}", "--replace", "--seed", "0"]) == 0
    twin = next(path for path in sorted(folder.iterdir()) if path.suffix == ".csv" and path.name != "t.csv")
    with open(twin, encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    return {name: [row[place] for row in rows[1:]] for place, name in enumerate(rows[0])}


def in_its_unit(cell: str, unit: str) -> "tuple[float, str] | None":
    """A cell read as a number and the unit it is in: its own unit word, else the column's (years where neither)."""
    found = _CELL.match(cell)
    if found is None:
        return None
    word = found.group(2).lower().rstrip(".")
    if word and word not in UNIT_WORDS:
        return None
    return float(found.group(1)), UNIT_WORDS[word] if word else (unit or YEARS)


def over_the_mark(value: float, unit: str, top_category: bool) -> bool:
    """Whether a value is an age of 90 years or more in its unit; the top category itself (the mark) is allowed where ``top_category``."""
    mark = MARK[unit]
    return value > mark if top_category else value >= mark


# The facts whose numbers count cells, rows or widths, never values: read
# on the whole path of the fact (lane SH2's verify 2's walk), so a width
# census's keys and a share of rows are no ages.
_COUNTISH = re.compile(
    r"count|styles|\.n_|^n_|rows|missing|occurrences|people|_cells|distinct|width|length|places|figures"
    r"|percent(?!ile)|top_coded|kurtosis|skew|std|variance|digits|share|floor|holders|plain|signs|layout_forms|position"
    r"|shape_forms|suppressed|distance|evidence|remarks|notes|ceiling|top_category"
)


def _published(node: object, path: str = "", unit: str = "") -> "typing.Iterator[tuple[str, object, str]]":
    """Every value of a block and every key of its maps, with its path and the unit word of the affix it stands under, but those of `_COUNTISH` paths."""
    if _COUNTISH.search(path):
        return
    if isinstance(node, dict):
        suffix = f"{node.get('suffix', '')}".strip().lower().rstrip(".")
        here = UNIT_WORDS.get(suffix, unit)
        for inner, value in node.items():
            yield f"{path}.{inner}#key", inner, here
            # ...a map of spellings to their counts (`variants`): its keys
            # are values, its numbers counts.
            if not path.endswith("variants"):
                yield from _published(value, f"{path}.{inner}", here)
    elif isinstance(node, list):
        for place, value in enumerate(node):
            yield from _published(value, f"{path}[{place}]", unit)
    elif isinstance(node, bool) or node is None:
        return
    elif isinstance(node, (int, float, str)):
        yield path, node, unit


def blocks(folder: pathlib.Path) -> "dict[str, dict]":
    """The description's column blocks by name."""
    document = json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))
    return {block.get("name"): block for block in document.get("columns", [])}


def ages_published(block: "dict", column: Column) -> int:
    """Distinct values of 90 years or more a column's block publishes (a linear counter over its facts)."""
    top = "top_coded" in block
    seen: "set[tuple[float, str]]" = set()
    for _key, value, unit in _published(block):
        read = in_its_unit(f"{value}", unit or column.unit)
        if read is not None and over_the_mark(read[0], read[1], top):
            seen.add(read)
    return len(seen)


def top_named(block: "dict", column: Column) -> bool:
    """Whether a block names a value at or past the mark, the top category itself included."""
    for _key, value, unit in _published(block):
        read = in_its_unit(f"{value}", unit or column.unit)
        if read is not None and over_the_mark(read[0], read[1], False):
            return True
    return False


def held_as_written(one: "dict[str, object]") -> bool:
    """An age column an open question offering `identifier` holds, read as its cells are written (LANE I4m RULINGS 21 (1)).

    Its role a record number's, no top-code, and that question among those
    put to it: its name says nothing while the question is open, so where its
    cells reach no ages its twin writes made-up values in lane ID-ROOM's room,
    past the mark where its cells lie there, and a cell of it is an age written
    only where it is a real value of the column (`twin_real`).
    """
    return one["role"] == "identifier" and one["top_coded"] is None and any(
        "identifier" in f"{offered}".split(" (")[0].split("/") for offered in one["open"]  # type: ignore[attr-defined]
    )


def ages_written(cells: "list[str]", column: Column, top: bool) -> int:
    """Twin cells holding an age of 90 years or more (a linear counter)."""
    return sum(1 for cell in cells if (read := in_its_unit(cell, column.unit)) is not None and over_the_mark(read[0], read[1], top))


def parts_published(block: "dict", real: "set[str]") -> int:
    """Distinct real values of an address part a column's block publishes, as written or as a number (a linear counter)."""
    numbers = {float(value) for value in real if re.fullmatch(r"\d+", value)}
    seen: "set[str]" = set()
    for _key, value, _unit in _published(block):
        text = f"{value}".strip()
        if text in real:
            seen.add(text)
        elif isinstance(value, (int, float)) and float(value) in numbers:
            seen.add(f"{float(value):g}")
        else:
            for token in re.findall(r"\d+[A-Za-z]?", text):
                if token in real and len(token) >= 2:
                    seen.add(token)
    return len(seen)


def measure(main: "typing.Callable[..., int]", folder: pathlib.Path, form: str, n: int, seed: int, answered: bool) -> "dict[str, dict[str, object]]":
    """One form through the command at ``n`` rows: per column its role, questions put, answers, and the counters."""
    from synthtwin import parsing

    table = write(folder, form, n, seed)
    header, rows = build(form, n, seed)
    given = profile(main, table, answered, n >= 20000, form)
    put = questions_put(folder, True)
    found = blocks(folder)
    twin = generate(main, folder)
    # ...and `validate`, the real table against its description: 0, or 3
    # with the misses its report names.
    validated = quiet(main, ["validate", f"{folder / 't-profile.json'}", "--replace"])
    misses = sorted({found.group(1) for path in folder.iterdir() if path.name.endswith("quality.txt")
                     for found in re.finditer(r"^\s+(\S+ \[[^\]]+\]): MISSED", path.read_text(encoding="utf-8"), re.M)})
    measured: "dict[str, dict[str, object]]" = {"(table)": {"validate_exit": validated, "misses": misses}}
    for place, column in enumerate(FORMS[form]):
        block = found.get(column.name, {})
        top = "top_coded" in block
        one: "dict[str, object]" = {
            "role": block.get("role"), "top_coded": block.get("top_coded"),
            "open": put.get(column.name, []),
            "answers": [one for one in given if one.split(":", 1)[1].split("=")[0] == column.name],
        }
        if column.kind == AGE:
            one["published_over"] = ages_published(block, column)
            one["twin_over"] = ages_written(twin.get(column.name, []), column, top)
            # ...and its twin cells that are a real value of it, merged as a
            # person's key is (`parsing.merged_key`): a held column's made-up
            # values in lane ID-ROOM's room are none (a linear counter).
            merged_real = {parsing.merged_key(row[place]) for row in rows if row[place].strip()}
            one["twin_real"] = sum(
                1 for cell in twin.get(column.name, []) if cell.strip() and parsing.merged_key(cell) in merged_real
            )
            # ...and a top category 1 to 10 real cells hold, named anywhere
            # in the block or written in the twin (it is to be pooled).
            old = sum(1 for row in rows if (read := in_its_unit(row[place], column.unit)) is not None
                      and over_the_mark(read[0], read[1], False))
            one["real_over"] = old
            # ...and its cells read absent, against the real blank cells.
            one["n_missing"] = block.get("n_missing")
            one["real_missing"] = sum(1 for row in rows if not row[place].strip())
            # ...counted in people where the form names its patients (a
            # long table, ten rows a patient: lane SH3's repair).
            people = [spot for spot, other in enumerate(FORMS[form]) if other.kind == PERSON]
            if people:
                old = len({row[people[0]] for row in rows if (read := in_its_unit(row[place], column.unit)) is not None
                           and over_the_mark(read[0], read[1], False)})
            one["few_top_named"] = int(0 < old < 11 and (
                top_named(block, column) or ages_written(twin.get(column.name, []), column, False) > 0))
        else:
            real = {row[place].strip() for row in rows if row[place].strip()}
            one["published_real"] = parts_published(block, real)
            one["twin_real"] = sum(1 for cell in twin.get(column.name, []) if cell.strip() in real)
        measured[column.name] = one
    return measured

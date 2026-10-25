"""P4-D433 (lane PS2): the tables and the count of dates held by the floor, shared by the gate and the KPI driver.

THE COUNT (`K-HZ-07`). Every real date a description publishes -- a
percentile, a rung, a tail boundary, a census entry, a mode, a span's end,
a written form -- is counted in PEOPLE where a person column is declared or
answered and repeats (`persons_counted.count`, the independent count lane
HX2's gate and K-S3-65 read), else in ROWS by the calendar part it names
(one row a person: a row is a person; no person column: a row is the one
holder the table names): a published day, month or quarter that one to ten
rows fall on is counted (`_in_rows`), and so is a pooled or held record's
span end or bucket one to ten rows hold. Beside it, lane E0c's leak scan
read as a search of the description's text (`printed`): a real date one to
ten people (else rows, by its day) hold, printed anywhere as written or as
its canonical day. Written apart from `profile._counted_in_subjects` and
`profile._dates_few_in_rows`.

THE SWEEP (the lane's spec): birth dates over seventy years, death dates,
sparse event dates and dense admission dates that must stay at the day, on
a table of one row a person, of several rows a person, and of no person
column; and lane E0c's two live exposures, the zoo's `patients.csv`
(`dob_iso`, one row a person, `patient_id` answered `identifier`) and
`phi_registry.csv` (`birth_date`, no question flags it), the second rebuilt
here as lane E0c's build writes it (`tests/health_zoo_wide.py` is not on
this lane's base). Every table runs the zoo's own path: profile, the
general answers, profile --answers (`answered`).
"""

from __future__ import annotations

import contextlib
import datetime
import decimal
import hashlib
import io
import json
import pathlib
import random
import re

from synthtwin import cli, parsing

import health_zoo
import persons_counted

FLOOR = 11


def _day(draw: random.Random, first: datetime.date, last: datetime.date) -> datetime.date:
    return first + datetime.timedelta(days=draw.randrange((last - first).days + 1))


def one_row_a_person(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A patient a row: a birth date over seventy years, a dense admission day, a sparse death date."""
    draw = random.Random(seed)
    lines: "list[list[str]]" = []
    for index in range(rows):
        born = _day(draw, datetime.date(1930, 1, 1), datetime.date(1999, 12, 31))
        admitted = _day(draw, datetime.date(2023, 1, 1), datetime.date(2023, 12, 31))
        died = _day(draw, datetime.date(2015, 1, 1), datetime.date(2024, 12, 31)) if draw.random() < 0.03 else None
        lines += [[
            f"P{1000000 + index:07d}", born.isoformat(), admitted.isoformat(),
            died.isoformat() if died else "", f"{draw.uniform(40, 140):.1f}",
        ]]
    return ["patient_id", "birth_date", "admit_date", "death_date", "weight"], lines


def one_row_a_person_unanswered(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A patient a row under a padded key nobody answered: its open question makes the key a candidate subject."""
    draw = random.Random(seed)
    lines: "list[list[str]]" = []
    for index in range(rows):
        born = _day(draw, datetime.date(1930, 1, 1), datetime.date(1999, 12, 31))
        lines += [[f"{1000000 + index:09d}", born.isoformat(), f"{draw.uniform(40, 140):.1f}"]]
    return ["patient_key", "birth_date", "weight"], lines


def several_rows_a_person(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Four visits a patient: the birth and death date repeated on each, a dense visit day."""
    draw = random.Random(seed)
    lines: "list[list[str]]" = []
    people = max(rows // 4, 1)
    born = [_day(draw, datetime.date(1930, 1, 1), datetime.date(1999, 12, 31)) for _person in range(people)]
    died = [
        _day(draw, datetime.date(2015, 1, 1), datetime.date(2024, 12, 31)) if draw.random() < 0.03 else None
        for _person in range(people)
    ]
    for index in range(rows):
        person = index % people
        seen = _day(draw, datetime.date(2023, 1, 1), datetime.date(2023, 12, 31))
        death = died[person]
        lines += [[
            f"P{1000000 + person:07d}", born[person].isoformat(), seen.isoformat(),
            death.isoformat() if death else "", f"{draw.uniform(40, 140):.1f}",
        ]]
    return ["patient_id", "birth_date", "visit_date", "death_date", "weight"], lines


def no_person_column(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """An event log naming nobody: a birth date, a dense admission day, an event over thirty years on few rows."""
    draw = random.Random(seed)
    lines: "list[list[str]]" = []
    for _index in range(rows):
        born = _day(draw, datetime.date(1930, 1, 1), datetime.date(1999, 12, 31))
        admitted = _day(draw, datetime.date(2023, 1, 1), datetime.date(2023, 12, 31))
        event = _day(draw, datetime.date(1990, 1, 1), datetime.date(2019, 12, 31)) if draw.random() < 0.02 else None
        lines += [[
            born.isoformat(), admitted.isoformat(), event.isoformat() if event else "",
            draw.choice(("A", "B", "C")),
        ]]
    return ["birth_date", "admit_date", "event_date", "ward"], lines


def dense_only(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """No person column, every date column dense: an admission day over a year and a stamp to the minute."""
    draw = random.Random(seed)
    lines: "list[list[str]]" = []
    for _index in range(rows):
        admitted = _day(draw, datetime.date(2023, 1, 1), datetime.date(2023, 12, 31))
        stamp = datetime.datetime.combine(
            _day(draw, datetime.date(2023, 1, 1), datetime.date(2023, 12, 31)),
            datetime.time(draw.randrange(24), draw.randrange(60)),
        )
        lines += [[admitted.isoformat(), stamp.strftime("%Y-%m-%d %H:%M"), draw.choice(("A", "B", "C"))]]
    return ["admit_date", "arrived_at", "ward"], lines


# -- repair round 1 (lane PS2's skeptic 1 and Codex's review): the shapes
# each item names, at the table floor and above.


def even_days(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """No person column: admission days over 1,095 days, each on 18 or 19 rows at 20,000 (skeptic 1, item 4).

    Every day holds the owner's floor of 11, so the column keeps its day
    and its bytes; under `--smallest-group 20` no day does.
    """
    draw = random.Random(seed)
    first = datetime.date(2021, 1, 1)
    lines = [[(first + datetime.timedelta(days=index % 1095)).isoformat(), draw.choice(("A", "B", "C"))]
             for index in range(rows)]
    draw.shuffle(lines)
    return ["admit_date", "ward"], lines


EXCEL_START = datetime.date(1899, 12, 30)


def excel_births(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A patient a row, the birth date written as an Excel 1900 day count, declared (skeptic 1, item 5)."""
    draw = random.Random(seed)
    lines: "list[list[str]]" = []
    for index in range(rows):
        born = _day(draw, datetime.date(1930, 1, 1), datetime.date(1999, 12, 31))
        lines += [[f"P{1000000 + index:07d}", f"{(born - EXCEL_START).days}", f"{draw.uniform(40, 140):.1f}"]]
    return ["patient_id", "birth_day", "weight"], lines


def utc_offsets(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """No person column: one stamp every two days at local midnight, at +13:00 and +14:00 in turn (Codex, item 1).

    The column is published on the shared clock, where each stamp's day
    is the day before its local one and holds one row.
    """
    draw = random.Random(seed)
    first = datetime.date(1900, 1, 1)
    lines = [[f"{(first + datetime.timedelta(days=2 * index)).isoformat()}T00:00:00{('+13:00', '+14:00')[index % 2]}",
              draw.choice(("A", "B", "C"))] for index in range(rows)]
    return ["arrived_at", "ward"], lines


def utc_shifted(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """No person column: for each day, 19 stamps at the next local midnight at +14:00 and one at 10:00 UTC (Codex, item 1).

    On the shared clock all twenty fall on the same day, so every published
    day holds 20 rows and the column keeps its day.
    """
    draw = random.Random(seed)
    first = datetime.date(2001, 1, 1)
    lines: "list[list[str]]" = []
    for index in range(rows):
        day = first + datetime.timedelta(days=index // 20)
        if index % 20 == 19:
            cell = f"{day.isoformat()}T10:00:00Z"
        else:
            cell = f"{(day + datetime.timedelta(days=1)).isoformat()}T00:00:00+14:00"
        lines += [[cell, draw.choice(("A", "B", "C"))]]
    return ["arrived_at", "ward"], lines


def unix_afternoons(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """No person column: Unix seconds at 13:00 every second day, declared (Codex, item 2): each day one row."""
    draw = random.Random(seed)
    lines = [[f"{946684800 + index * 172800 + 13 * 3600}", draw.choice(("A", "B", "C"))] for index in range(rows)]
    return ["stamp", "ward"], lines


def unix_millis_before_midnight(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """No person column: Unix milliseconds a millisecond before midnight every second day, declared (Codex, item 2)."""
    draw = random.Random(seed)
    lines = [[f"{946684800000 + index * 172800000 + 86399999}", draw.choice(("A", "B", "C"))]
             for index in range(rows)]
    return ["stamp", "ward"], lines


def month_first_days(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """No person column: consecutive days from 1950 written MM/DD/YYYY, read under `--day-first` (Codex, item 4).

    Days above twelve settle the column month-first; at the month every
    bucket is `MM/01/YYYY`, which reads either way.
    """
    draw = random.Random(seed)
    first = datetime.date(1950, 1, 1)
    lines = [[(first + datetime.timedelta(days=index)).strftime("%m/%d/%Y"), draw.choice(("A", "B"))]
             for index in range(rows)]
    return ["seen_on", "group"], lines


# Lane E0c's `phi_registry` (tests/health_zoo_wide.py on lane E0c's head
# a974b1d9), the same builder: every value invented.
FIRST_NAMES = (
    "Maria", "James", "Aisha", "Wei", "Olga", "Carlos", "Fatima", "John", "Priya", "Liam", "Sofia", "Kwame", "Hannah",
    "Mateo", "Yuki", "Omar", "Elena", "Noah", "Amara", "Lucas", "Mei", "Diego", "Zara", "Ethan", "Ines", "Tariq",
    "Grace", "Ivan", "Leila", "Samuel", "Nadia", "Jonah", "Rosa", "Arjun", "Clara", "Kofi", "Anya", "Felix", "Lina",
    "Hugo",
)
LAST_NAMES = (
    "Gonzalez", "Smith", "Okafor", "Zhang", "Ivanova", "Mendes", "Haddad", "Murphy", "Raman", "Walsh", "Rossi",
    "Mensah", "Becker", "Silva", "Tanaka", "Farouk", "Petrova", "Clarke", "Diallo", "Moreau", "Chen", "Ortiz", "Khan",
    "Novak", "Duarte", "Aziz", "Bennett", "Kowalski", "Rahimi", "Adeyemi", "Sato", "Lindqvist", "Vargas", "Iyer",
    "Hoffmann", "Boateng", "Sokolova", "Weber", "Nasser", "Laurent",
)
STREETS = ("Elm", "Maple", "Oak", "Cedar", "Pine", "Willow", "Harbor", "Lake", "Hill", "River", "Mill", "Park")
SUFFIXES = ("St", "Ave", "Rd", "Blvd", "Ln")
PHI_ZIPS = tuple(f"{52240 + 7 * place}" for place in range(59))
PHI_COLUMNS = ("med_rec_no", "patient_name", "street_address", "phone", "email", "ssn", "zip5", "birth_date")


def phi_registry(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Lane E0c's registry export: every direct identifier of HIPAA's Safe Harbor list a hospital file carries."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for index in range(n):
        first, last = draw.choice(FIRST_NAMES), draw.choice(LAST_NAMES)
        born = health_zoo._day(draw, datetime.date(1930, 1, 1), datetime.date(2005, 12, 31))
        rows += [[
            f"MR{4000000 + index}",
            f"{first} {last}",
            f"{draw.randint(1, 9999)} {draw.choice(STREETS)} {draw.choice(SUFFIXES)}",
            f"({draw.randint(201, 989)}) 555-{draw.randint(0, 9999):04d}",
            f"{first.lower()}.{last.lower()}{draw.randint(1, 999)}@example.org",
            f"9{draw.randint(0, 99):02d}-{draw.randint(10, 99)}-{draw.randint(0, 9999):04d}",
            draw.choice(PHI_ZIPS),
            born.isoformat(),
        ]]
    return list(PHI_COLUMNS), rows


def _table(name: str, build: object, columns: "tuple[str, ...]", knows: "dict[str, str]") -> health_zoo.Table:
    return health_zoo.Table(
        name, ".csv", build,  # type: ignore[arg-type]
        lambda header, rows: health_zoo.csv_bytes(header, rows),
        {name: columns}, knows, health_zoo._csv_reader(), (),
    )


def _zoo_table(name: str) -> health_zoo.Table:
    return [table for table in health_zoo.TABLES if table.name == name][0]


# The sweep: each shape's table; DENSE names the columns whose day grain
# the floor holds (their bytes pinned by the gate).
SWEEP: "dict[str, health_zoo.Table]" = {
    "one_row": _table("one_row", one_row_a_person,
                      ("patient_id", "birth_date", "admit_date", "death_date", "weight"),
                      {"patient_id": "identifier", "weight": "measurement"}),
    "one_row_open": _table("one_row_open", one_row_a_person_unanswered,
                           ("patient_key", "birth_date", "weight"), {"weight": "measurement"}),
    "several_rows": _table("several_rows", several_rows_a_person,
                           ("patient_id", "birth_date", "visit_date", "death_date", "weight"),
                           {"patient_id": "identifier", "weight": "measurement"}),
    "no_person": _table("no_person", no_person_column, ("birth_date", "admit_date", "event_date", "ward"), {}),
    "dense_only": _table("dense_only", dense_only, ("admit_date", "arrived_at", "ward"), {}),
    "demographics": _zoo_table("patients"),
    # The person question answered for the record number only, `keep` for
    # every other column it is put to, as lane E0c's zoo answers it (its
    # build: two repeating identifiers made 5 and 66 "people"): so no
    # subject column repeats and the birth dates are counted in rows.
    "phi_registry": _table("phi_registry", phi_registry, PHI_COLUMNS, {
        "med_rec_no": "identifier", "patient_name": "keep", "street_address": "keep",
        "phone": "keep", "email": "keep", "ssn": "keep", "zip5": "code",
    }),
}
SWEEP.update({
    "even_days": _table("even_days", even_days, ("admit_date", "ward"), {}),
    "even_days_20": _table("even_days", even_days, ("admit_date", "ward"), {}),
    "excel_births": _table("excel_births", excel_births, ("patient_id", "birth_day", "weight"),
                           {"patient_id": "identifier", "weight": "measurement"}),
    "utc_offsets": _table("utc_offsets", utc_offsets, ("arrived_at", "ward"), {}),
    "utc_shifted": _table("utc_shifted", utc_shifted, ("arrived_at", "ward"), {}),
    "unix_afternoons": _table("unix_afternoons", unix_afternoons, ("stamp", "ward"), {}),
    "unix_millis": _table("unix_millis", unix_millis_before_midnight, ("stamp", "ward"), {}),
    "month_first": _table("month_first", month_first_days, ("seen_on", "group"), {}),
})
# The options each shape is profiled under, and the floor it is counted at:
# the owner's floor of 11, or the user's raised floor (skeptic 1, item 4).
OPTIONS: "dict[str, tuple[tuple[str, ...], int]]" = {
    "even_days_20": (("--smallest-group", "20"), 20),
    "excel_births": (("--date-count", "birth_day", "excel-1900"), 11),
    "unix_afternoons": (("--date-count", "stamp", "seconds-since-1970"), 11),
    "unix_millis": (("--date-count", "stamp", "milliseconds-since-1970"), 11),
    "month_first": (("--day-first",), 11),
}


def options_of(shape: str) -> "tuple[tuple[str, ...], int]":
    """The command's options a sweep shape is profiled under and the floor it is counted at."""
    return OPTIONS.get(shape, ((), FLOOR))


DENSE: "dict[str, tuple[str, ...]]" = {
    "one_row": ("admit_date",),
    "several_rows": ("visit_date",),
    "no_person": ("admit_date",),
    "dense_only": ("admit_date", "arrived_at"),
    "even_days": ("admit_date",),
    "utc_shifted": ("arrived_at",),
}
# The sha256 of each dense column's block (json.dumps, sorted keys) on the
# base, ccebc947, through the same path (wave6/PS2/probe2.py, base-*.log;
# repair round 1's two, wave6/PS2/repair1/base-20k.log and base-200k.log). The gate pins
# the 20,000-row ones; K-HZ-07's slow leg the 200,000-row ones (the
# orchestrator's ruling 2 on the build, 2026-10-25).
DENSE_DIGESTS: "dict[tuple[str, str, int], str]" = {
    ("one_row", "admit_date", 20000): "62edde5415265efa1fd62ff5d917d8a865e227b7d4396bdfc953bf7c648870f9",
    ("several_rows", "visit_date", 20000): "0066f4fe052f739dd6f3cd41ce98779f0acfc131c8f3e2193af26424b55c4e69",
    ("no_person", "admit_date", 20000): "670a7f2848427d5b25534e42737c2334993a539fd8a65fc7528a4403c83cd7c0",
    ("dense_only", "admit_date", 20000): "681b7844e6f374a54a1c04834d5a7708aae16dc50b1b07657f09f328972ed3f6",
    ("dense_only", "arrived_at", 20000): "24c21436cb1faea7e381e8780c43ba40b4f3c433738cfa0c1dac22fee34309e0",
    ("one_row", "admit_date", 200000): "48d5904c9a33e578a333cc74a46854471644a4cbed6b372f9279f72bc57904e8",
    ("several_rows", "visit_date", 200000): "fa40ccc42396d76e301fbe8c453f9c2c0100feff6c73f351732b8a33bc194890",
    ("no_person", "admit_date", 200000): "080f3843acf7aa062f30d5b9d0420625b7f185b0bbf7edbd63012d011982a1ba",
    ("dense_only", "admit_date", 200000): "79beae64e891d3f447c613416434bd029641ae7db761327a878d35dd64c95d9c",
    ("dense_only", "arrived_at", 200000): "c831fbebcc60caaa306fb685ca867bbc8f6c1ba9ed7a7df3d1a6fc4ddeb26e0a",
    ("even_days", "admit_date", 20000): "ad30f5dd06e697fe29987e5a4153e7a33b6068eea04bd7ade12e6763148fd28d",
    ("utc_shifted", "arrived_at", 20000): "d33f637afd4f81963cf423eba79221ef6a6b92524e61be736d1e4bfc6769ac3d",
    ("even_days", "admit_date", 200000): "f00f96ff6821c47d1477681995105d3b8d5f4917b2ee251dd35732b95ad7c5d4",
    ("utc_shifted", "arrived_at", 200000): "e841666d138bcd09662f1f7c61343162e71b11b81d07fc66f02308c5b16cb2e8",
}


def dense_digest(folder: pathlib.Path, shape: str, column: str) -> str:
    """The sha256 of one dense column's block, as `DENSE_DIGESTS` pins it."""
    block = block_of(folder, SWEEP[shape].name, column)
    return hashlib.sha256(json.dumps(block, sort_keys=True).encode("utf-8")).hexdigest()


# Each date column's own layouts as its source writes it: the twin's cells
# are read in these and no other (skeptic 1, item 8). `strptime` layouts,
# or `count:<system>` for a declared count.
LAYOUTS: "dict[tuple[str, str], tuple[str, ...]]" = {
    ("one_row", "birth_date"): ("%Y-%m-%d",), ("one_row", "admit_date"): ("%Y-%m-%d",),
    ("one_row", "death_date"): ("%Y-%m-%d",),
    ("one_row_open", "birth_date"): ("%Y-%m-%d",),
    ("several_rows", "birth_date"): ("%Y-%m-%d",), ("several_rows", "visit_date"): ("%Y-%m-%d",),
    ("several_rows", "death_date"): ("%Y-%m-%d",),
    ("no_person", "birth_date"): ("%Y-%m-%d",), ("no_person", "admit_date"): ("%Y-%m-%d",),
    ("no_person", "event_date"): ("%Y-%m-%d",),
    ("dense_only", "admit_date"): ("%Y-%m-%d",), ("dense_only", "arrived_at"): ("%Y-%m-%d %H:%M",),
    ("demographics", "dob_iso"): ("%Y-%m-%d",), ("demographics", "dob_us"): ("%m/%d/%Y",),
    ("demographics", "dob_text"): ("%d-%b-%Y",),
    ("phi_registry", "birth_date"): ("%Y-%m-%d",),
    ("even_days", "admit_date"): ("%Y-%m-%d",), ("even_days_20", "admit_date"): ("%Y-%m-%d",),
    ("excel_births", "birth_day"): ("count:excel-1900",),
    ("utc_offsets", "arrived_at"): ("%Y-%m-%dT%H:%M:%S%z",),
    ("utc_shifted", "arrived_at"): ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ"),
    ("unix_afternoons", "stamp"): ("count:seconds-since-1970",),
    ("unix_millis", "stamp"): ("count:milliseconds-since-1970",),
    ("month_first", "seen_on"): ("%m/%d/%Y",),
}


def in_its_layouts(cell: str, layouts: "tuple[str, ...]") -> bool:
    """Whether a cell reads in one of its column's own source layouts."""
    for layout in layouts:
        if layout.startswith("count:"):
            if counted_moment(cell, layout[6:]) is not None and cell.strip() == cell and "." not in cell:
                return True
            continue
        try:
            datetime.datetime.strptime(cell, layout)
        except ValueError:
            continue
        return True
    return False


SEED = 20261016


def _quietly(arguments: "list[str]", refused: bool) -> int:
    screen = io.StringIO()
    with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        code = cli.main(arguments, small_tables_refused=refused)
    assert code in (0, 3), screen.getvalue()[-2000:]
    return code


def answered(table: health_zoo.Table, folder: pathlib.Path, rows: int,
             options: "tuple[str, ...]" = ()) -> pathlib.Path:
    """The zoo's path for one table: written from its seed, profiled, its questions answered generally, profiled again.

    The table floor stays on at 20,000 rows and above (the command's own
    rule); below it only the internal switch reaches the table. ``options``
    are the command's own (`options_of`), given to every profile. Returns
    the table's path; its description and questions sit beside it.
    """
    from unanswered_identifier_shapes import nobody_at_the_keyboard

    source = health_zoo.write_table(table, folder, rows, SEED)
    refused = rows >= 20000
    asked = folder / f"{table.name}-questions.json"
    with nobody_at_the_keyboard():
        _quietly(["profile", f"{source}", "--out-dir", f"{folder}", "--replace", *options], refused)
        # An answer may put the next question (a column answered `keep` to
        # the person question is then asked what it holds): the person
        # answers each round the file asks something they know, three at most.
        for _round in range(ROUNDS):
            if not asked.exists():
                break
            document = json.loads(asked.read_text(encoding="utf-8"))
            answers, _general = health_zoo.answer_generally(table, document)
            if not [answer for answer in answers if answer["given"]]:
                break
            asked.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
            _quietly(["profile", f"{source}", "--out-dir", f"{folder}", "--replace", "--answers", f"{asked}",
                      *options], refused)
    return source


ROUNDS = 3


def block_of(folder: pathlib.Path, table: str, column: str) -> "dict[str, object]":
    """One column's block of a table's description in ``folder``."""
    described = json.loads((folder / f"{table}-profile.json").read_text(encoding="utf-8"))
    return [block for block in described["columns"] if block["name"] == column][0]


def dates_held_few(table: pathlib.Path, folder: pathlib.Path, floor: int = FLOOR) -> "dict[str, object]":
    """K-HZ-07 over one table: the real dates one to ten people (else rows) hold that its description publishes.

    Each column the description reads as dates (or holds with a
    `time_grain` record) is counted alone, beside the person columns that
    repeat and hold the floor's number of people
    (`persons_counted.subject_columns`), or, with none, in rows
    (`_in_rows`). Returns the count, the named dates and groups, the date
    columns, the unit and the printed real dates (`printed`). ``floor`` is
    the owner's 11 or the user's raised floor; in people the count reads
    11 (`persons_counted`), which no raised floor of this sweep reaches.
    """
    stem = table.name[: -len(table.suffix)]
    text = (folder / f"{stem}-profile.json").read_text(encoding="utf-8")
    described = json.loads(text)
    asked = folder / f"{stem}-questions.json"
    questions = json.loads(asked.read_text(encoding="utf-8")) if asked.exists() else None
    names, columns = persons_counted.table_columns(table, *persons_counted._written(described))
    # A question answered in an earlier round is asked again only to show
    # the reading it keeps (`answered_before`): not an open question.
    settled = {
        entry["column"] for entry in (questions or {}).get("answered_before", [])
        if entry.get("your_answer") and entry.get("column") not in described["settings"]["person_columns"]
    }
    people = [
        name for name in persons_counted.subject_columns(described, questions)
        if name in names and name not in settled
        and persons_counted.repeats(columns[names.index(name)])
        and persons_counted.counts_people([persons_counted.subject_of(cell) for cell in columns[names.index(name)]])
    ]
    if not people:
        found = _in_rows(described, names, columns, floor)
        found["printed"] = printed(text, found["dated"], names, columns, [], described, floor)  # type: ignore[arg-type]
        return found
    held_columns = [columns[names.index(name)] for name in people]
    # The person column's own census of rows a person is lane MG's, not a
    # date: the count reads the description with no declared person column.
    settings = dict(described["settings"])
    settings["person_columns"] = []
    plain = dict(described)
    plain["settings"] = settings
    few = 0
    named: "list[str]" = []
    dated: "list[str]" = []
    for block in described["columns"]:
        if block["name"] not in names or block["name"] in people or not (
            block.get("role") == "datetime" or isinstance(block.get("time_grain"), dict)
        ):
            continue
        dated += [block["name"]]
        found = persons_counted.count(
            [block["name"]] + people,
            [columns[names.index(block["name"])]] + held_columns,
            plain,
            people,
        )
        few += int(found["few"])  # type: ignore[call-overload]
        named += list(found["named"])  # type: ignore[call-overload]
    shown = printed(text, dated, names, columns, held_columns, described)
    return {"few": few, "named": named, "dated": dated, "counted_in": "people", "printed": shown}


_PART = re.compile(r"^([0-9]{4})-(?:q([1-4])|([0-9]{2})(?:-([0-9]{2}))?)")


def parts_of(text: str) -> "list[str]":
    """The calendar parts a canonical date text names, finest first (day, month, quarter), by pattern."""
    found = _PART.match(parsing.folded(text))
    if not found:
        return []
    year, quarter, month, day = found.groups()
    if quarter:
        return [f"{year}-q{quarter}"]
    if not 1 <= int(month) <= 12:
        return []
    named = [f"{year}-{month}", f"{year}-q{(int(month) - 1) // 3 + 1}"]
    return ([f"{year}-{month}-{day}"] if day else []) + named


def _offset_of(text: str) -> "datetime.timedelta | None":
    """A written UTC offset (`Z`, `+14:00`, `-0500`, `+14`) as a time span, read apart from `parsing`."""
    found = re.fullmatch(r"([+-])([0-9]{2}):?([0-9]{2})?", text.strip())
    if text.strip() in ("Z", "z"):
        return datetime.timedelta(0)
    if not found:
        return None
    span = datetime.timedelta(hours=int(found.group(2)), minutes=int(found.group(3) or 0))
    return span if found.group(1) == "+" else -span


def _days_of_text(canonical: str, offset: str, at_utc: bool) -> "list[str]":
    """The day a read cell names on the clock its block publishes: its UTC day where `datetimes_read_at` is `utc`."""
    if not at_utc or not offset:
        return [canonical]
    shift = _offset_of(offset)
    try:
        moment = datetime.datetime.fromisoformat(canonical[:19])
    except ValueError:
        return [canonical]
    if shift is None:
        return [canonical]
    return [(moment - shift).isoformat(sep=" ")]


_SECONDS_SINCE = {"seconds-since-1970": (datetime.datetime(1970, 1, 1), 1),
                  "milliseconds-since-1970": (datetime.datetime(1970, 1, 1), 1000),
                  "seconds-since-1960": (datetime.datetime(1960, 1, 1), 1),
                  "milliseconds-since-1960": (datetime.datetime(1960, 1, 1), 1000)}


def counted_moment(cell: str, member: str) -> "datetime.datetime | None":
    """The instant a declared count names, read exactly by `decimal` and `datetime`, apart from `date_counts`.

    Excel's 1900 days (its leap day skipped), the days since 1970, 1960 or
    1904, and the seconds or milliseconds since 1970 or 1960; None for any
    other system or text.
    """
    try:
        count = decimal.Decimal(cell.strip())
    except decimal.InvalidOperation:
        return None
    if not count.is_finite():
        return None
    whole = int(count.to_integral_value(rounding=decimal.ROUND_FLOOR))
    rest = count - whole
    if member == "excel-1900":
        if whole < 1 or whole == 60:
            return None
        start = datetime.datetime(1899, 12, 30) if whole > 60 else datetime.datetime(1899, 12, 31)
        return start + datetime.timedelta(days=whole, microseconds=int(rest * 86400000000))
    if member in persons_counted._EPOCHS:
        start = datetime.datetime.combine(persons_counted._EPOCHS[member], datetime.time())
        return start + datetime.timedelta(days=whole, microseconds=int(rest * 86400000000))
    if member in _SECONDS_SINCE:
        start, per = _SECONDS_SINCE[member]
        micro = int(count * 1000000 / per)
        return start + datetime.timedelta(microseconds=micro)
    return None


def _counted_texts(cell: str, member: str) -> "list[str]":
    """A count's day four ways, each its own tally: its true calendar day, and the day of its instant rounded to
    the second, the minute and the day (the precisions a description publishes a count at)."""
    moment = counted_moment(cell, member)
    if moment is None:
        day = persons_counted._counted_day(cell, member)
        return [day] if day else []
    texts = [moment.date().isoformat()]
    for unit in (datetime.timedelta(seconds=1), datetime.timedelta(minutes=1), datetime.timedelta(days=1)):
        since = moment - datetime.datetime(1, 1, 1)
        steps = (since + unit / 2) // unit
        texts += [(datetime.datetime(1, 1, 1) + steps * unit).date().isoformat()]
    return texts


def _stamp_of(cell: str, member: str) -> str:
    """A declared count of seconds or milliseconds as the ISO stamp it names to the second, floored; else the cell."""
    moment = counted_moment(cell, member) if parsing.folded(cell) else None
    return cell if moment is None else moment.strftime("%Y-%m-%d %H:%M:%S")


def _at_the_grain(raw: "list[str]", block: "dict[str, object]", member: str) -> "list[str]":
    """`persons_counted.at_the_grain`, and for a count of seconds or milliseconds, which it does not read, the
    same: each instant (`counted_moment`) floored to its bucket at the last span's rung, inside the span."""
    grain = block.get("time_grain")
    if member not in _SECONDS_SINCE or not isinstance(grain, dict) or grain.get("rung") == "held" \
            or not grain.get("spans"):
        return persons_counted.at_the_grain(raw, block, member)
    rung, first_text, last_text = grain["spans"][-1]
    first = datetime.datetime.fromisoformat(f"{first_text}")
    last = datetime.datetime.fromisoformat(f"{last_text}")
    found: "list[str]" = []
    for cell in raw:
        moment = counted_moment(cell, member) if parsing.folded(cell) else None
        if moment is None:
            found += [cell]
            continue
        start = min(max(persons_counted._grain_floor(moment, rung), first), last)
        found += [persons_counted._grain_text(start, grain, block)]
    return found


def _in_rows(described: "dict[str, object]", names: "list[str]", columns: "list[list[str]]",
             floor: int = FLOOR) -> "dict[str, object]":
    """The count where no person column repeats: each published date's day, month or quarter against the rows on it.

    Each column read as dates: its cells at the grain its block publishes
    (`persons_counted.at_the_grain`), else read by its format; every text
    the block publishes that names a date (`persons_counted.leaves`) is
    counted as the part it names, against the rows whose date falls in
    it; and a pooled or held record's spans and buckets
    (`persons_counted.spans_few`, `grain_groups`) with each row its own
    holder.
    """
    settings = described["settings"]
    members = {pair[0]: pair[1] for pair in settings.get("forced_date_counts", [])} \
        if isinstance(settings, dict) else {}
    few = 0
    named: "list[str]" = []
    dated: "list[str]" = []
    for block in described["columns"]:  # type: ignore[union-attr]
        name = block["name"]
        grain = block.get("time_grain")
        if name not in names or not (block.get("role") == "datetime" or isinstance(grain, dict)):
            continue
        dated += [name]
        raw = columns[names.index(name)]
        rows = [f"{place}" for place in range(len(raw))]
        member = members.get(name, "")
        values = _at_the_grain(raw, block, member)
        shown = f"{block.get('format', '')}"
        at_utc = block.get("datetimes_read_at") == "utc"
        # One tally a way of reading a cell's day (`_counted_texts`): a part
        # one to ten rows fall on in any of them is few.
        on: "dict[tuple[int, str], int]" = {}
        for cell, at in zip(raw, values):
            if not parsing.folded(cell) or parsing.folded(cell) in persons_counted._NOBODY:
                continue
            read_as: "list[str]" = [at] if at != cell else []
            if not read_as and member:
                read_as = _counted_texts(cell, member)
            elif not read_as and shown:
                read = parsing.parse_datetime(cell, shown)
                read_as = _days_of_text(read[0], read[1], at_utc) if read is not None else []
            for tally, text in enumerate(read_as):
                for part in parts_of(text):
                    on[(tally, part)] = on.get((tally, part), 0) + 1
        texts, _numbers = persons_counted.leaves(block)
        for text in sorted(texts):
            mine = parts_of(text)
            if mine and [key for key, rows_on in on.items() if key[1] == mine[0] and 0 < rows_on < floor]:
                few += 1
                named += [f"{name}={text}"]
        if isinstance(grain, dict):
            # A count of seconds or milliseconds is read by the spans and the
            # buckets as the stamp it names, which those helpers read.
            view_raw, view_block, view_member = raw, block, member
            if member in _SECONDS_SINCE:
                view_raw = [_stamp_of(cell, member) for cell in raw]
                view_block = dict(block)
                view_block["time_grain"] = dict(grain, kind="stamp", reading="iso-datetime")
                view_member = ""
            groups = persons_counted.spans_few(view_raw, rows, view_block, view_member)
            groups += persons_counted.grain_groups(view_raw, values, rows, view_block, view_member)
            few += len(groups)
            named += [f"{name}:{group}" for group in groups]
    return {"few": few, "named": named, "dated": dated, "counted_in": "rows"}


def printed(text: str, dated: "list[str]", names: "list[str]", columns: "list[list[str]]",
            people: "list[list[str]]", described: "dict[str, object]", floor: int = FLOOR) -> "list[str]":
    """The real dates one to ten people (else rows: by their day) hold whose text the description prints anywhere.

    Lane E0c's leak scan, read as a search of the column's own block: each
    cell of a date column, as written and as its canonical form (in rows
    its day), held by one to ten people under some person column, or, with
    none, whose day one to ten rows fall on. A bucket start a pooled or
    held record names at a month, a quarter or a year (`1962-01-01` for
    1962) names that bucket, not a day, and is not searched for.
    """
    blocks = {block["name"]: block for block in described["columns"]}  # type: ignore[union-attr]
    settings = described["settings"]
    members = {pair[0]: pair[1] for pair in settings.get("forced_date_counts", [])} \
        if isinstance(settings, dict) else {}
    found: "set[str]" = set()
    rows = [[f"{row}" for row in range(len(columns[0]))]] if columns else []
    for name in dated:
        raw = columns[names.index(name)]
        canonical: "dict[str, str]" = {}
        keys: "list[str]" = []
        for cell in raw:
            folded = parsing.folded(cell)
            if not folded or folded in persons_counted._NOBODY:
                keys += [""]
                continue
            if cell not in canonical:
                canonical[cell] = ""
                # A declared count: its true calendar day (`counted_moment`).
                moment = counted_moment(cell, members[name]) if name in members else None
                if moment is not None:
                    canonical[cell] = moment.date().isoformat()
                for shown in (() if moment is not None else _READINGS):
                    read = parsing.parse_datetime(cell, shown)
                    if read is not None:
                        # in people the value as the block writes it; in rows its day,
                        # on the clock the block publishes
                        utc = blocks[name].get("datetimes_read_at") == "utc" if name in blocks else False
                        canonical[cell] = read[0] if people else _days_of_text(read[0], read[1], utc)[0][:10]
                        break
            keys += [cell if people else (canonical[cell] or cell)]
        grain = blocks[name].get("time_grain") if name in blocks else None
        starts: "set[str]" = set()
        if isinstance(grain, dict):
            # A bucket start at a rung coarser than the cells' own names its
            # bucket (`2023-03-05 14:00:00` the hour, `1962-01-01` the year).
            finest = _RUNG_ORDER.index(f"{grain.get('finest', 'day')}")
            if [rung for rung, _first, _last in grain.get("spans", []) if _RUNG_ORDER.index(rung) < finest]:
                starts = persons_counted.bucket_names(grain)
            if f"{grain.get('rung')}" in _RUNG_ORDER and _RUNG_ORDER.index(f"{grain.get('rung')}") < finest:
                starts |= set(_at_the_grain(raw, blocks[name], members.get(name, "")))
            if f"{grain.get('rung')}" in _ABOVE_THE_DAY:
                starts |= {start[:10] for start in starts}
            # ...written at the cells' own precision: `1995-01` for 1995 in a
            # column of months.
            if grain.get("finest") == "month":
                starts |= {start[:7] for start in starts}
            # ...and on the shared clock a bucket start's instant at UTC may
            # fall on the day before or after its local day.
            if blocks[name].get("datetimes_read_at") == "utc":
                for start in list(starts):
                    if len(start) >= 10 and parts_of(start[:10]):
                        day = datetime.date.fromisoformat(start[:10])
                        starts |= {(day + datetime.timedelta(days=step)).isoformat() for step in (-1, 1)}
        own = json.dumps(blocks[name], indent=2) if name in blocks else text
        written: "dict[str, set[str]]" = {}
        for cell, key in zip(raw, keys):
            if key:
                written.setdefault(key, set()).update({cell, canonical.get(cell, "")} - {""})
        for column in people or rows:
            holders: "dict[str, set[str]]" = {}
            for key, holder in zip(keys, column):
                if key:
                    holders.setdefault(key, set()).add(persons_counted.subject_of(holder) if people else holder)
            for key, who in holders.items():
                if len(who) >= (FLOOR if people else floor):
                    continue
                for form in written[key] - starts:
                    # A declared count's own figures are searched as text
                    # only: as a bare number it is one of the block's counts.
                    if name in members and form not in canonical.values():
                        if f'"{form}"' in own:
                            found.add(f"{name}={form}")
                    elif f'"{form}' in own or f" {form}" in own:
                        found.add(f"{name}={form}")
    return sorted(found)


_ABOVE_THE_DAY = ("year", "quarter", "month")
_RUNG_ORDER = ("year", "quarter", "month", "day", "four hours", "hour", "minute", "second")
_READINGS = ("iso-datetime", "iso-date", "month-first-date", "textual-day-first-date")

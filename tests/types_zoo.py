"""The data-type zoo: every way a health table writes a value, one column a way (lane ZOO-X).

The owner, 2026-11-21: "I am worried about the different data types we
will find. I want to dramatically increase this. The application needs
to be bullet proof for all types of health data."

The health data zoo (`tests/health_zoo.py`, `tests/health_zoo_wide.py`)
counts KINDS OF EXPORT: a lab export, a claims file, a flowsheet. This
module counts WAYS OF WRITING A VALUE inside any of them: a number with
its thousands grouped, a dollar amount in brackets, `<0.5`, `Inf`, a
code with its opening zeros, a cell in Chinese or Hebrew, an emoji, a
line break or a JSON fragment inside a cell, a date with its month in
French, an instant in UTC, epoch milliseconds, a duration `1d 3h`, a
flag written `Positive`, a pain score, a list `a|b`, `key=value` pairs,
a waveform `[0.1, 0.2]`, a variant `c.35G>A`, a URL, an IP or MAC
address, a UUID, a key past 2**53, a file whose column names repeat or
whose last row is a total -- and, since lane ZOO-Y, the shapes a
hospital's bedside and procedure exports write: a rate with its unit
(`5 mL/hr`), a value and its unit in two columns, abnormal flags
`H`, `L`, `A`, `*`, a reference range in two columns, a pulse with its
artifacts (`0`, `300`, `???`), procedure events with their clock, a
signed sedation scale, risk score totals, comments holding a pressure,
and a flowsheet whose measure is named in a column of its own. Each
type is one column (`TYPES`), the
columns are grouped into tables of the shapes a hospital warehouse
writes (several rows a person, 20,000 rows and at least 1,000 people at
the owner's table floor), and every table is run by the zoo's own
engine (`health_zoo.run_table`): profile, the questions answered with
general facts about the data, generate, validate, and the analyst's
pandas script on the real table and on the twin.

TO THAT, THIS MODULE ADDS THE CHECKS THE TWIN MUST PASS TO LEAVE THE
PROTECTED COMPUTER (`run_type_table`):

* the five twin-versus-real checks (`synthtwin.twin_checks`: exact row
  copies, nearest-record distances, copied patients, identifiers and
  dates, rare combinations), run as the command runs them;
* the owner's rule for dates (2026-11-18): a twin date keeps the real
  column's weekday and time of day, and its day of the month is made up
  (`date_rule`: the weekday shares and the hour shares of the twin
  against the real, and the share of twin dates that fall on a real
  row's own day no higher than a fresh draw's);
* code written on the real table runs unchanged on the twin: each
  type's own analyst steps (`Table.checks`) parse the column the way an
  analyst would (pd.to_numeric after stripping a unit, pd.to_datetime
  with the column's format, a flag mapped to True and False, a list
  split on its mark), beside the zoo's generic checks of every column
  (dtype, missing count and spellings, levels, shapes and forms).

A type passes when its table's steps exit 0 or 3, every question is
general, validate misses nothing on its columns, the analyst's checks
hold on the real table and on the twin, the five checks pass, no twin
cell of an identifier column equals a real one, no age past 89 is
written, and its date columns keep the rule (`type_verdicts`).

THIS MODULE MEASURES. What fails is fixed in the product with a test of
its own; nothing here is loosened to make a type pass. The vocabulary
is made up for the battery from the public coding systems' own shapes;
no value comes from any real table, every address is under
example.org, every IP address in a block reserved for documentation
and every telephone number in the 555 exchange.
"""

from __future__ import annotations

import base64
import dataclasses
import datetime
import hashlib
import json
import math
import pathlib
import random
import re
import uuid
from typing import Callable

import health_zoo as zoo
from health_zoo import Check, Table, _bad, _csv_reader, _listed, _pattern, _present, _t, csv_bytes

# -- the sizes and seeds ----------------------------------------------------

# The owner's table floor (plan P4-D425): 20,000 rows that hold a value,
# and 1,000 people where one person has several rows.
FLOOR_ROWS = 20_000
# The suite's smoke size, below the floor (the command's internal switch).
SMOKE_ROWS = 600
SEED = 20261121

# A column is built from one draw of the row's random source and the row's
# own facts (`Row`): its person, its index and a moment the row is about.
Maker = Callable[[random.Random, "Row"], str]


@dataclasses.dataclass(frozen=True)
class Row:
    """What one row of a type table is about: a person, its place and a moment."""

    index: int
    person: str
    moment: datetime.datetime


@dataclasses.dataclass(frozen=True)
class Column:
    """One column of a type table: its name, the type it proves and how a cell is written."""

    name: str
    type_name: str
    make: Maker
    # What the person who holds the table knows about the column, as the
    # zoo's answers use it (`Table.knows`): '' for nothing said.
    known: str = ""


def _person_of(index: int, people: int, draw: random.Random) -> str:
    return f"P{4000000 + draw.randrange(people):07d}"


def _moment(draw: random.Random) -> datetime.datetime:
    day = datetime.date(2021, 1, 1) + datetime.timedelta(days=draw.randint(0, 3 * 365))
    # Clinic hours weigh more than the night, as a hospital's stamps do.
    hour = draw.choices(range(24), [1, 1, 1, 1, 1, 2, 4, 8, 10, 10, 9, 8, 7, 8, 9, 9, 8, 6, 5, 4, 3, 2, 2, 1])[0]
    return datetime.datetime.combine(day, datetime.time(hour, draw.randint(0, 59), draw.randint(0, 59)))


def build_rows(columns: "tuple[Column, ...]", n: int, seed: int, person: bool = True) -> "tuple[list[str], list[list[str]]]":
    """A table of these columns, `n` rows from `seed`: a person key first where `person`, four rows a person."""
    draw = random.Random(seed)
    people = max(n // 4, 1)
    header = (["person_key"] if person else []) + [column.name for column in columns]
    rows: "list[list[str]]" = []
    for index in range(n):
        who = _person_of(index, people, draw) if person else f"S{5000000 + index:07d}"
        row = Row(index, who, _moment(draw))
        rows += [([who] if person else []) + [column.make(draw, row) for column in columns]]
    return header, rows


def _weighted(pool: "tuple[tuple[str, float], ...]") -> Maker:
    values = [value for value, _weight in pool]
    weights = [weight for _value, weight in pool]
    return lambda draw, _row: draw.choices(values, weights)[0]


def _sometimes(share: float, written: Maker, otherwise: Maker) -> Maker:
    return lambda draw, row: written(draw, row) if draw.random() < share else otherwise(draw, row)


def _blank(_draw: random.Random, _row: Row) -> str:
    return ""


def _gauss(mean: float, spread: float, places: int, low: float = -math.inf, high: float = math.inf) -> Maker:
    return lambda draw, _row: f"{min(max(draw.gauss(mean, spread), low), high):.{places}f}"


# -- 1. NUMBERS AS A HEALTH TABLE WRITES THEM --------------------------------


def _scientific(draw: random.Random, _row: Row) -> str:
    return f"{math.exp(draw.gauss(8.0, 2.0)):.2E}"


def _grouped(draw: random.Random, _row: Row) -> str:
    return f"{math.exp(draw.gauss(7.5, 1.4)):,.2f}"


def _dollars(draw: random.Random, _row: Row) -> str:
    amount = math.exp(draw.gauss(6.0, 1.3))
    return f"(${amount:,.2f})" if draw.random() < 0.06 else f"${amount:,.2f}"


DOSE_UNITS = (("mg", 60.0), ("g", 8.0), ("mL", 15.0), ("units", 12.0), ("mcg", 5.0))
DOSE_AMOUNTS = {"mg": (5, 10, 20, 25, 40, 50, 100, 250, 500, 1000), "g": (1, 2), "mL": (5, 10, 15, 20),
                "units": (4, 6, 8, 10, 20), "mcg": (25, 50, 100)}


def _dose(draw: random.Random, _row: Row) -> str:
    unit = draw.choices([unit for unit, _w in DOSE_UNITS], [w for _u, w in DOSE_UNITS])[0]
    amount = draw.choice(DOSE_AMOUNTS[unit])
    return f"{amount} {unit}" if draw.random() < 0.9 else f"{amount / 2:g} {unit}"


REFERENCE_RANGES = (
    ("3.5-5.1", 20.0), ("135-145", 20.0), ("0.6-1.2", 15.0), ("70-99", 15.0), ("4.0-11.0", 15.0),
    ("150-400", 10.0), ("<200", 5.0),
)


def _censored(draw: random.Random, _row: Row) -> str:
    value = math.exp(draw.gauss(2.0, 1.2))
    if value < 0.5:
        return "<0.5"
    if value > 100:
        return ">100"
    return f"{value:.1f}"


def _percent(draw: random.Random, _row: Row) -> str:
    value = min(max(draw.gauss(45, 15), 0), 100)
    return f"{value:.1f}%" if draw.random() < 0.5 else f"{round(value)}%"


FRACTIONS = (("1/2", 30.0), ("1/4", 20.0), ("3/4", 15.0), ("1/3", 15.0), ("2/3", 10.0), ("1/8", 10.0))


def _signed(draw: random.Random, _row: Row) -> str:
    value = round(draw.gauss(0, 4))
    return f"+{value}" if value > 0 else f"{value}"


def _near_zero(draw: random.Random, _row: Row) -> str:
    value = round(draw.gauss(0, 0.4), 1)
    return "-0.0" if value == 0 and draw.random() < 0.5 else f"{value:.1f}"


def _with_infinities(draw: random.Random, _row: Row) -> str:
    roll = draw.random()
    if roll < 0.02:
        return "Inf"
    if roll < 0.03:
        return "-Inf"
    if roll < 0.05:
        return "NaN"
    return f"{math.exp(draw.gauss(0.0, 0.6)):.3f}"


UNIT_CODES = tuple((f"{code:03d}", 100.0 / (rank + 1)) for rank, code in enumerate((7, 12, 3, 105, 41, 9, 88, 230, 15, 64, 5, 1)))


def _with_placeholders(draw: random.Random, _row: Row) -> str:
    roll = draw.random()
    if roll < 0.03:
        return "-1"
    if roll < 0.05:
        return "999"
    if roll < 0.06:
        return "9999"
    return f"{draw.randint(40, 180)}"


MISSING_WORDS = ("NULL", "N/A", ".", "unknown", "--", "NA")


def _with_missing_words(draw: random.Random, _row: Row) -> str:
    if draw.random() < 0.07:
        return draw.choice(MISSING_WORDS)
    return f"{draw.gauss(98.6, 0.9):.1f}"


NUMBER_COLUMNS = (
    Column("count_whole", "whole_numbers", lambda draw, _row: f"{min(int(draw.expovariate(0.2)), 60)}", "measurement"),
    Column("result_decimal", "decimal_numbers", _gauss(5.2, 1.3, 2, 0.1)),
    Column("assay_exponent", "scientific_notation", _scientific, "measurement"),
    Column("charge_grouped", "thousands_separators", _grouped, "measurement"),
    Column("charge_dollars", "currency_amounts", _dollars, "measurement"),
    Column("dose_with_unit", "units_in_values", _dose, "measurement"),
    Column("reference_range", "ranges_in_cells", _weighted(REFERENCE_RANGES)),
    Column("censored_result", "censored_values", _censored, "measurement"),
    Column("percent_written", "percentages", _percent, "measurement"),
    Column("fraction_written", "fractions", _weighted(FRACTIONS), "keep"),
    Column("signed_change", "signed_numbers", _signed, "measurement"),
    Column("near_zero_change", "negative_zero", _near_zero, "measurement"),
    Column("ratio_value", "infinity_and_nan_spellings", _with_infinities, "measurement"),
    Column("unit_code", "leading_zero_codes", _weighted(UNIT_CODES), "code"),
    Column("pulse_coded", "sentinel_numbers", _with_placeholders, "measurement"),
    Column("temp_with_words", "sentinel_words", _with_missing_words, "measurement"),
)

# -- 2. TEXT AS A HEALTH TABLE WRITES IT -------------------------------------

LANGUAGES_WRITTEN = (
    ("English", 40.0), ("Español", 15.0), ("Français", 5.0), ("Tiếng Việt", 5.0), ("中文", 6.0), ("日本語", 3.0),
    ("한국어", 3.0), ("العربية", 6.0), ("עברית", 3.0), ("Русский", 4.0), ("हिन्दी", 4.0), ("Português", 6.0),
)
EMOJI_COMMENTS = (
    ("ok 👍", 30.0), ("pain 😣", 20.0), ("better 🙂", 20.0), ("no change", 20.0), ("😴 tired", 10.0),
)
MOJIBAKE = (("CafÃ© unit", 25.0), ("NiÃ±os ward", 25.0), ("Café unit", 25.0), ("Niños ward", 25.0))
CONTROL_MARKED = (("K1\x1fone", 40.0), ("K2\x1ftwo", 35.0), ("K3\x7fthree", 25.0))
QUOTED = (
    ('said "fine"', 30.0), ('"stable", per nurse', 25.0), ("a, b and c", 25.0), ("it's 'ok'", 20.0),
)
TWO_LINES = (
    ("Seen today.\nNo change.", 40.0), ("Called back.\r\nLeft message.", 30.0), ("Line one\nLine two\nLine three", 30.0),
)
MARKUP = (("<b>POS</b>", 30.0), ("<i>neg</i>", 30.0), ("<p>see note</p>", 20.0), ("&lt;5 &amp; stable", 20.0))


def _json_cell(draw: random.Random, _row: Row) -> str:
    return json.dumps({"sys": draw.randint(95, 170), "dia": draw.randint(55, 100), "pos": draw.choice(["sit", "lie"])})


def _xml_cell(draw: random.Random, _row: Row) -> str:
    return f'<obs code="P1" unit="/min">{draw.randint(48, 130)}</obs>'


def _hl7_segment(draw: random.Random, _row: Row) -> str:
    return f"OBX|1|NM|8867-4^Heart rate^LN||{draw.randint(48, 130)}|/min|60-100|{draw.choice(['N', 'N', 'N', 'H', 'L'])}"


def _fhir_fragment(draw: random.Random, _row: Row) -> str:
    return json.dumps({
        "resourceType": "Observation",
        "valueQuantity": {"value": round(draw.gauss(37.0, 0.5), 1), "unit": "Cel"},
    }, separators=(",", ":"))


def _base64_payload(draw: random.Random, _row: Row) -> str:
    return base64.b64encode(bytes(draw.getrandbits(8) for _ in range(24))).decode("ascii")


SENTENCES = (
    "The patient was seen in clinic today.", "Vital signs were within normal limits.",
    "No acute distress was noted.", "Plan reviewed with the family.", "Return in two weeks.",
)


def _long_text(draw: random.Random, _row: Row) -> str:
    return " ".join(draw.choice(SENTENCES) for _ in range(draw.randint(25, 60)))


TEXT_COLUMNS = (
    Column("language_written", "unicode_scripts", _weighted(LANGUAGES_WRITTEN)),
    Column("comment_emoji", "emoji", _weighted(EMOJI_COMMENTS)),
    Column("unit_name_mojibake", "mojibake", _weighted(MOJIBAKE)),
    Column("control_marked", "control_characters", _weighted(CONTROL_MARKED)),
    Column("quoted_words", "quotes_and_delimiters", _weighted(QUOTED)),
    Column("two_line_text", "line_breaks_in_cells", _weighted(TWO_LINES)),
    Column("markup_cell", "html_fragments", _weighted(MARKUP)),
    Column("json_cell", "json_fragments", _json_cell),
    Column("xml_cell", "xml_fragments", _xml_cell),
    Column("hl7_segment", "hl7_segments_in_cells", _hl7_segment),
    Column("fhir_fragment", "fhir_fragments", _fhir_fragment),
    Column("payload_b64", "base64", _base64_payload),
    Column("long_text", "very_long_strings", _long_text),
)

# -- 3. DATES AND TIMES AS A HEALTH TABLE WRITES THEM ------------------------

MONTHS_EN = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
             "November", "December")
MONTHS_FR = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
             "novembre", "décembre")
MONTHS_DE = ("Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober",
             "November", "Dezember")
MONTHS_ES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
             "noviembre", "diciembre")
EPOCH = datetime.datetime(1970, 1, 1)
EXCEL_DAY_NOUGHT = datetime.datetime(1899, 12, 30)


def _twelve_hour(moment: datetime.datetime) -> str:
    hour = moment.hour % 12 or 12
    return f"{moment.month}/{moment.day}/{moment.year} {hour}:{moment.minute:02d} {'AM' if moment.hour < 12 else 'PM'}"


def _offset_stamp(draw: random.Random, row: Row) -> str:
    offset = draw.choice((-5, -5, -6, 1, 0))
    local = row.moment + datetime.timedelta(hours=offset)
    sign = "+" if offset >= 0 else "-"
    return f"{local:%Y-%m-%dT%H:%M:%S}{sign}{abs(offset):02d}:00"


def _duration_clock(draw: random.Random, _row: Row) -> str:
    seconds = int(draw.expovariate(1 / 5400))
    return f"{seconds // 3600:02d}:{seconds // 60 % 60:02d}:{seconds % 60:02d}"


def _duration_words(draw: random.Random, _row: Row) -> str:
    minutes = int(draw.expovariate(1 / 900)) + 5
    days, rest = divmod(minutes, 1440)
    hours, minutes = divmod(rest, 60)
    parts = ([f"{days}d"] if days else []) + ([f"{hours}h"] if hours else []) + ([f"{minutes}m"] if minutes else [])
    return " ".join(parts) or "0m"


def _impossible(draw: random.Random, row: Row) -> str:
    roll = draw.random()
    if roll < 0.01:
        return "2023-02-30"
    if roll < 0.02:
        return "0000-00-00"
    return f"{row.moment:%Y-%m-%d}"


DATE_COLUMNS = (
    Column("iso_day", "iso_dates", lambda _draw, row: f"{row.moment:%Y-%m-%d}"),
    Column("utc_moment", "iso_instants_in_utc", lambda _draw, row: f"{row.moment:%Y-%m-%dT%H:%M:%S}Z"),
    Column("offset_moment", "iso_instants_with_offsets", _offset_stamp),
    Column("us_moment_ampm", "twelve_hour_stamps", lambda _draw, row: _twelve_hour(row.moment), "twelve-hour"),
    Column("day_mon_year", "day_month_name_year", lambda _draw, row: f"{row.moment:%d}-{zoo.MONTHS[row.moment.month - 1]}-{row.moment.year}"),
    Column("long_month_date", "long_month_names", lambda _draw, row: f"{MONTHS_EN[row.moment.month - 1]} {row.moment.day}, {row.moment.year}"),
    Column("french_date", "month_names_french", lambda _draw, row: f"{row.moment.day} {MONTHS_FR[row.moment.month - 1]} {row.moment.year}", "keep"),
    Column("german_date", "month_names_german", lambda _draw, row: f"{row.moment.day}. {MONTHS_DE[row.moment.month - 1]} {row.moment.year}"),
    Column("spanish_date", "month_names_spanish", lambda _draw, row: f"{row.moment.day} de {MONTHS_ES[row.moment.month - 1]} de {row.moment.year}", "keep"),
    Column("compact_day", "compact_yyyymmdd", lambda _draw, row: f"{row.moment:%Y%m%d}"),
    Column("epoch_seconds", "epoch_seconds", lambda _draw, row: f"{int((row.moment - EPOCH).total_seconds())}", "seconds-since-1970"),
    Column("epoch_millis", "epoch_milliseconds", lambda draw, row: f"{int((row.moment - EPOCH).total_seconds()) * 1000 + draw.randint(0, 999)}", "milliseconds-since-1970"),
    Column("excel_serial_day", "excel_serial_numbers", lambda _draw, row: f"{(row.moment - EXCEL_DAY_NOUGHT).total_seconds() / 86400:.4f}", "excel-1900"),
    Column("duration_clock", "durations_hh_mm_ss", _duration_clock),
    Column("duration_words", "durations_in_words", _duration_words, "keep"),
    Column("clock_only", "time_only", lambda _draw, row: f"{row.moment:%H:%M}"),
    Column("day_with_impossible", "impossible_dates", _impossible, "missing"),
    Column("year_month", "partial_dates_year_month", lambda _draw, row: f"{row.moment:%Y-%m}"),
)
# The date columns the owner's date rule reads, each with the format that
# reads it whole and whether it writes a time of day (`date_rule`).
DATED: "dict[str, tuple[str, bool]]" = {
    "iso_day": ("%Y-%m-%d", False),
    "utc_moment": ("%Y-%m-%dT%H:%M:%SZ", True),
    "us_moment_ampm": ("%m/%d/%Y %I:%M %p", True),
    "day_mon_year": ("%d-%b-%Y", False),
    "long_month_date": ("%B %d, %Y", False),
    "compact_day": ("%Y%m%d", False),
}

# -- 4. CODES AS A HEALTH TABLE WRITES THEM ----------------------------------

ICD9 = zoo._zipf(("250.00", "401.9", "414.01", "428.0", "496", "584.9", "599.0", "780.79", "V58.69", "E849.0",
                  "272.4", "530.81", "311", "427.31", "486", "305.1", "V45.81", "285.9", "244.9", "786.50"))
RXNORM = zoo._zipf(("197361", "310965", "314076", "617312", "1049630", "198211", "308136", "866924", "861007",
                    "1361048", "897122", "245314", "312961", "849574", "1719286"))
PROCEDURES = zoo._zipf(("99213", "99214", "99203", "93000", "36415", "80053", "71046", "85025", "99285", "J1100",
                        "G0008", "A0427", "97110", "29881", "43239"))
DRG = zoo._zipf(("470", "871", "291", "392", "690", "194", "603", "065", "683", "177", "189", "378"))
REVENUE = zoo._zipf(("0450", "0300", "0250", "0636", "0320", "0730", "0270", "0120", "0360", "0710"))
PLACE_OF_SERVICE = zoo._zipf(("11", "21", "22", "23", "02", "12", "31", "81", "19", "20"))
OIDS = zoo._zipf(("2.16.840.1.113883.6.1", "2.16.840.1.113883.6.96", "2.16.840.1.113883.6.88", "2.16.840.1.113883.6.90",
                  "2.16.840.1.113883.12.292"))
HIERARCHY = zoo._zipf(("A.01", "A.01.02", "A.02", "B.10.01", "B.10.02", "C.03", "C.03.01.04", "D.11"))


def _ean13(figures: str) -> str:
    total = sum(int(figure) * (3 if place % 2 else 1) for place, figure in enumerate(figures))
    return figures + f"{(10 - total % 10) % 10}"


PRODUCT_BARCODES = zoo._zipf(tuple(_ean13(f"0{301234560 + step * 731:09d}00") for step in range(14)))


def _url(draw: random.Random, row: Row) -> str:
    return f"https://records.example.org/chart/{row.person}/{draw.randint(100000, 999999)}"


def _ip(draw: random.Random, _row: Row) -> str:
    return f"192.0.2.{draw.randint(1, 254)}" if draw.random() < 0.5 else f"198.51.100.{draw.randint(1, 254)}"


def _mac(draw: random.Random, _row: Row) -> str:
    return ":".join(f"{draw.randint(0, 255):02X}" for _ in range(6))


def _email(draw: random.Random, row: Row) -> str:
    return f"pt{row.person[1:]}.{draw.randint(1, 99)}@example.org"


CODE_COLUMNS = (
    Column("icd9_code", "icd9_codes", _weighted(ICD9), "code"),
    Column("rxnorm_code", "rxnorm_codes", _weighted(RXNORM), "code"),
    Column("procedure_code", "procedure_codes", _weighted(PROCEDURES), "code"),
    Column("drg_code", "drg_codes", _weighted(DRG), "code"),
    Column("revenue_code", "revenue_codes_leading_zero", _weighted(REVENUE), "code"),
    Column("place_code", "two_figure_codes", _weighted(PLACE_OF_SERVICE), "code"),
    Column("system_oid", "dotted_object_identifiers", _weighted(OIDS), "code"),
    Column("hierarchy_code", "dotted_hierarchical_codes", _weighted(HIERARCHY), "code"),
    Column("product_barcode", "barcodes_with_check_figure", _weighted(PRODUCT_BARCODES), "code"),
    Column("chart_url", "urls", _url, "identifier"),
    Column("device_ip", "ip_addresses", _ip, "identifier"),
    Column("device_mac", "mac_addresses", _mac, "identifier"),
    Column("contact_email", "email_addresses", _email, "identifier"),
)

# -- 5. IDENTIFIERS AS A HEALTH TABLE WRITES THEM ----------------------------


def _luhn(figures: str) -> str:
    total = 0
    for place, figure in enumerate(reversed(figures)):
        value = int(figure) * (2 if place % 2 == 0 else 1)
        total += value - 9 if value > 9 else value
    return figures + f"{(10 - total % 10) % 10}"


ID_COLUMNS = (
    Column("visit_key", "encounter_keys", lambda _draw, row: f"V{700000000 + row.index:09d}", "identifier"),
    Column("visit_line", "composite_keys", lambda draw, row: f"{row.person}-{draw.randint(1, 12):02d}", "identifier"),
    Column("order_uuid", "uuids", lambda draw, _row: f"{uuid.UUID(int=draw.getrandbits(128), version=4)}", "identifier"),
    Column("hashed_key", "hashed_keys", lambda _draw, row: hashlib.sha256(f"k{row.index}".encode()).hexdigest(), "identifier"),
    Column("luhn_key", "check_figure_keys", lambda _draw, row: _luhn(f"{300000000 + row.index * 7:09d}"), "identifier"),
    Column("specimen_number", "keys_past_two_to_the_53", lambda _draw, row: f"{9007199254740993 + row.index * 977}", "identifier"),
)

# -- 6. FLAGS, SCALES AND CATEGORIES -----------------------------------------


def _flag(yes: str, no: str, share: float = 0.3) -> Maker:
    return lambda draw, _row: yes if draw.random() < share else no


MIXED_CASE = (("yes", 15.0), ("Yes", 20.0), ("YES", 10.0), ("no", 20.0), ("No", 25.0), ("NO", 10.0))
GCS = tuple((f"{score}", 60.0 if score == 15 else 4.0 + score) for score in range(3, 16))
PHYSICAL_STATUS = (("1", 15.0), ("2", 40.0), ("3", 30.0), ("4", 10.0), ("3E", 3.0), ("5", 2.0))
NYHA = (("I", 30.0), ("II", 35.0), ("III", 25.0), ("IV", 10.0))
LIKERT = (("Never", 8.0), ("Rarely", 15.0), ("Sometimes", 22.0), ("Often", 35.0), ("Always", 20.0))
APGAR = tuple((f"{score}", (1.0, 1.0, 1.0, 1.0, 2.0, 3.0, 5.0, 10.0, 25.0, 40.0, 11.0)[score]) for score in range(11))
MALLAMPATI = (("Class 1", 35.0), ("Class 2", 40.0), ("Class 3", 20.0), ("Class 4", 5.0))
RARE_LEVELS = tuple((f"Clinic {name}", weight) for name, weight in zip(
    ("North", "South", "East", "West", "Central", "Harbor", "Valley", "Ridge", "Lake", "Park", "Hill", "Bay",
     "Grove", "Mill", "Field", "Brook", "Stone", "Forest", "Meadow", "Spring", "Summit", "Shore", "Glen", "Pine",
     "Cedar", "Maple", "Oak", "Elm", "Ash", "Birch"),
    tuple(2000.0 / (rank + 1) ** 1.6 for rank in range(30)),
))

FLAG_COLUMNS = (
    Column("flag_yn", "flags_y_n", _flag("Y", "N")),
    Column("flag_01", "flags_0_1", _flag("1", "0")),
    Column("flag_true_false", "flags_true_false", _flag("True", "False")),
    Column("flag_yes_no", "flags_yes_no", _flag("Yes", "No")),
    Column("flag_tf", "flags_t_f", _flag("T", "F")),
    Column("flag_pos_neg", "flags_positive_negative", _flag("Positive", "Negative", 0.12)),
    Column("flag_present", "flags_present_absent", _flag("Present", "Absent", 0.2)),
    Column("flag_one_blank", "flags_one_or_blank", _flag("1", "", 0.15)),
    Column("flag_x_blank", "flags_x_or_blank", _flag("X", "", 0.25)),
    Column("flag_mixed_case", "flags_mixed_case", _weighted(MIXED_CASE)),
    Column("pain_score", "ordinal_pain_0_10", _weighted(tuple((f"{s}", 30.0 if s == 0 else 12.0 - s) for s in range(11)))),
    Column("gcs_total", "ordinal_gcs", _weighted(GCS)),
    Column("physical_status_class", "ordinal_physical_status", _weighted(PHYSICAL_STATUS)),
    Column("nyha_class", "ordinal_nyha_roman", _weighted(NYHA)),
    Column("likert_answer", "ordinal_likert_words", _weighted(LIKERT)),
    Column("apgar_five", "ordinal_apgar", _weighted(APGAR)),
    Column("mallampati", "ordinal_mallampati", _weighted(MALLAMPATI)),
    Column("clinic_name", "categories_with_rare_levels", _weighted(RARE_LEVELS)),
)

# -- 7. CELLS WITH A STRUCTURE INSIDE ---------------------------------------

ALLERGENS = (("Penicillin", 30.0), ("Sulfa", 15.0), ("Latex", 10.0), ("Peanut", 10.0), ("Codeine", 10.0),
             ("Shellfish", 10.0), ("Iodine", 8.0), ("Aspirin", 7.0))
SIDES = (("Left", 35.0), ("Right", 35.0), ("Bilateral", 15.0), ("L", 6.0), ("R", 6.0), ("N/A", 3.0))
SITES = (("Left knee", 20.0), ("Right knee", 20.0), ("Left hip", 15.0), ("Right hip", 15.0), ("Left shoulder", 10.0),
         ("Right shoulder", 10.0), ("Lumbar spine", 10.0))
HGVS_C = zoo._zipf(("c.35G>A", "c.34G>T", "c.38G>A", "c.1799T>A", "c.2573T>G", "c.2369C>T", "c.3140A>G", "c.1633G>A",
                    "c.181C>A", "c.215C>G", "c.5266dupC", "c.68_69delAG"))
HGVS_P = zoo._zipf(("p.Gly12Asp", "p.Gly12Cys", "p.Gly13Asp", "p.Val600Glu", "p.Leu858Arg", "p.Thr790Met",
                    "p.His1047Arg", "p.Glu545Lys", "p.Gln61His", "p.Pro72Arg"))
RESULT_WORDS = (("see comment", 3.0), ("POS", 2.0), ("NEG", 2.0), ("QNS", 1.0))


def _allergy_list(draw: random.Random, _row: Row) -> str:
    if draw.random() < 0.4:
        return "NKDA"
    picks = draw.sample([name for name, _w in ALLERGENS], draw.randint(1, 3))
    return "|".join(picks)


def _pairs(draw: random.Random, _row: Row) -> str:
    return f"sys={draw.randint(95, 170)};dia={draw.randint(55, 100)};hr={draw.randint(48, 130)}"


def _wave(draw: random.Random, _row: Row) -> str:
    base = draw.gauss(0.0, 0.05)
    return "[" + ", ".join(f"{base + 0.8 * math.sin(step / 2) + draw.gauss(0, 0.02):.3f}" for step in range(8)) + "]"


def _mixed_result(draw: random.Random, _row: Row) -> str:
    roll = draw.random()
    if roll < 0.08:
        return draw.choices([word for word, _w in RESULT_WORDS], [w for _x, w in RESULT_WORDS])[0]
    return f"{math.exp(draw.gauss(1.0, 0.5)):.2f}"


def _sparse(draw: random.Random, _row: Row) -> str:
    return draw.choice(("reviewed", "pending", "declined")) if draw.random() < 0.03 else ""


STRUCTURE_COLUMNS = (
    Column("allergy_list", "lists_pipe_separated", _allergy_list),
    Column("vital_pairs", "key_value_cells", _pairs),
    Column("waveform", "arrays_in_cells", _wave),
    Column("laterality", "laterality", _weighted(SIDES)),
    Column("body_site", "body_sites", _weighted(SITES)),
    Column("variant_cdna", "hgvs_cdna", _weighted(HGVS_C), "code"),
    Column("variant_protein", "hgvs_protein", _weighted(HGVS_P), "code"),
    Column("result_mixed", "numbers_beside_words", _mixed_result),
    Column("sparse_status", "sparse_columns", _sparse),
)


# -- 8. A STUDY TABLE: TIME TO EVENT, WIDE REPEATS, MONEY, PLACES --------------


def _study_rows(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """One row a person: enrolment, days to an event or to censoring, a wide block of repeats, amounts, places."""
    draw = random.Random(seed)
    header = [
        "subject_key", "enrolled_on", "days_to_event", "event_flag", "event_kind",
        *(f"pulse_{visit}" for visit in range(1, 7)),
        "billed_amount", "allowed_amount", "paid_amount", "home_latitude", "home_longitude", "county_fips",
    ]
    rows: "list[list[str]]" = []
    for index in range(n):
        enrolled = datetime.date(2019, 1, 1) + datetime.timedelta(days=draw.randint(0, 900))
        event_day = int(draw.expovariate(1 / 700)) + 1
        censor_day = draw.randint(30, 1500)
        event = event_day <= censor_day
        base = draw.gauss(76, 10)
        pulses = [
            f"{round(base + draw.gauss(0, 5))}" if draw.random() > 0.08 * visit else "" for visit in range(6)
        ]
        billed = math.exp(draw.gauss(7.0, 1.0))
        allowed = billed * draw.uniform(0.3, 0.8)
        paid = allowed * draw.uniform(0.6, 1.0)
        rows += [[
            f"S{5000000 + index:07d}", f"{enrolled:%Y-%m-%d}", f"{min(event_day, censor_day)}", "1" if event else "0",
            draw.choice(("death", "relapse")) if event else draw.choice(("censored", "censored", "lost")),
            *pulses, f"{billed:.2f}", f"{allowed:.2f}", f"{paid:.2f}",
            f"{35.1 + draw.gauss(0, 0.4):.5f}", f"{-106.6 + draw.gauss(0, 0.5):.5f}",
            draw.choice(("35001", "35013", "35043", "35049", "35061", "35028", "35045", "35055")),
        ]]
    return header, rows


STUDY_KINDS = {
    "survival_time_and_event": ("subject_key", "enrolled_on", "days_to_event", "event_flag", "event_kind"),
    "wide_repeated_columns": tuple(f"pulse_{visit}" for visit in range(1, 7)),
    "claims_amounts": ("billed_amount", "allowed_amount", "paid_amount"),
    "coordinates": ("home_latitude", "home_longitude"),
    "county_fips_codes": ("county_fips",),
}

# -- 9. FILES WHOSE HEADER OR LAST ROWS ARE ODD -------------------------------

LONG_NAME = "a_measurement_name_written_out_in_full_" * 6 + "end"


def _odd_header_rows(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Column names that repeat, a blank name, names that are years, a very long name."""
    draw = random.Random(seed)
    people = max(n // 4, 1)
    header = ["person_key", "value", "value", "", "2019", "2020", LONG_NAME]
    rows = [[
        _person_of(index, people, draw), f"{draw.gauss(5, 1):.1f}", f"{draw.gauss(50, 9):.0f}",
        draw.choice(("a", "b", "c")), f"{draw.randint(0, 40)}", f"{draw.randint(0, 40)}", f"{draw.gauss(1, 0.2):.2f}",
    ] for index in range(n)]
    return header, rows


def _with_total_row(header: "list[str]", rows: "list[list[str]]") -> bytes:
    """The table as some reports export it: a last row of totals and a line saying when it ran."""
    total = sum(float(row[2]) for row in rows if re.fullmatch(r"\d+(\.\d+)?", row[2]))
    tail = [["Total", "", f"{total:.2f}", ""]]
    return csv_bytes(header, rows + tail) + b"\nReport generated 2024-01-31 by the information office\n"


def _total_rows(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    draw = random.Random(seed)
    people = max(n // 4, 1)
    header = ["person_key", "service", "charge", "posted_on"]
    rows = [[
        _person_of(index, people, draw), draw.choice(("Lab", "Imaging", "Pharmacy", "Room")),
        f"{math.exp(draw.gauss(5, 1)):.2f}", f"{_moment(draw):%Y-%m-%d}",
    ] for index in range(n)]
    return header, rows


def _units_row(header: "list[str]", rows: "list[list[str]]") -> bytes:
    """A second header row of units under the names, as instrument exports write it."""
    return csv_bytes(header, [["", "mg/dL", "mmHg", "kg"]] + rows)


def _unit_rows(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    draw = random.Random(seed)
    people = max(n // 4, 1)
    header = ["person_key", "glucose", "systolic", "weight"]
    rows = [[
        _person_of(index, people, draw), f"{draw.gauss(105, 25):.0f}", f"{draw.gauss(125, 15):.0f}",
        f"{draw.gauss(78, 14):.1f}",
    ] for index in range(n)]
    return header, rows


# -- the tables ---------------------------------------------------------------


def _column_table(name: str, columns: "tuple[Column, ...]", checks: "tuple[Check, ...]") -> Table:
    kinds: "dict[str, tuple[str, ...]]" = {"several_rows_a_person": ("person_key",)}
    for column in columns:
        kinds[column.type_name] = kinds.get(column.type_name, ()) + (column.name,)
    knows = {"person_key": "identifier", **{column.name: column.known for column in columns if column.known}}
    return Table(
        name, ".csv", lambda n, seed: build_rows(columns, n, seed),
        lambda header, rows: csv_bytes(header, rows), kinds, knows, _csv_reader(), checks, person="person_key",
    )


def _numbers_bad(column: str, strip: str = "", words: "tuple[str, ...]" = ()) -> "Callable[[dict[str, object]], object]":
    """Cells that do not read as a number once `strip` is taken out, the words named set aside."""

    def run(frames: "dict[str, object]") -> int:
        import pandas

        cells = _t(column)(frames).dropna().astype(str)  # type: ignore[attr-defined]
        cells = cells[~cells.isin(list(words))]
        if strip:
            cells = cells.str.replace(strip, "", regex=True)
        return int(pandas.to_numeric(cells, errors="coerce").isna().sum())

    return run


def _numbers_range(column: str, strip: str = "", words: "tuple[str, ...]" = ()) -> "Callable[[dict[str, object]], object]":
    def run(frames: "dict[str, object]") -> object:
        import pandas

        cells = _t(column)(frames).dropna().astype(str)  # type: ignore[attr-defined]
        cells = cells[~cells.isin(list(words))]
        if strip:
            cells = cells.str.replace(strip, "", regex=True)
        numbers = [float(value) for value in pandas.to_numeric(cells, errors="coerce").dropna() if math.isfinite(value)]
        return zoo._spread(numbers)

    return run


def _ranged(kind: str, column: str, strip: str = "", words: "tuple[str, ...]" = ()) -> Check:
    return Check(kind, f"the numbers of {column} keep their range", "range", _numbers_range(column, strip, words),
                 column, zoo.spoil_every(column, lambda text: _scaled_text(text)))


def _scaled_text(text: str) -> str:
    """A spoil: every number of a cell written ten times larger."""
    return re.sub(r"\d+(\.\d+)?", lambda match: f"{float(match.group()) * 10:g}", text)


def _parses(kind: str, column: str, strip: str = "", words: "tuple[str, ...]" = ()) -> Check:
    return _bad(kind, f"{column} reads as numbers", column, _numbers_bad(column, strip, words))


def _dates_bad(column: str, form: str, **options: object) -> "Callable[[dict[str, object]], object]":
    return lambda frames: zoo._bad_dates(_t(column)(frames), form, **options)


def _shares_of(column: str) -> "Callable[[dict[str, object]], object]":
    """The shares of the column's most common values, for a column of few values."""

    def run(frames: "dict[str, object]") -> object:
        cells = _t(column)(frames).fillna("").astype(str)  # type: ignore[attr-defined]
        counts = cells.value_counts(normalize=True)
        return tuple(round(float(share), 3) for share in counts.sort_index().values[:12])

    return run


def _shares(kind: str, column: str) -> Check:
    return Check(kind, f"the shares of {column}'s values", "share", _shares_of(column), column,
                 zoo.spoil_every(column, lambda _text: "zz"))


def _flag_bad(column: str, mapping: "dict[str, bool]") -> "Callable[[dict[str, object]], object]":
    def run(frames: "dict[str, object]") -> int:
        cells = _t(column)(frames).fillna("").astype(str)  # type: ignore[attr-defined]
        return int((~cells.isin(sorted(mapping))).sum())

    return run


def _flag_checks(kind: str, column: str, yes: str, no: str) -> "tuple[Check, ...]":
    mapping = {yes: True, no: False}
    return (
        _bad(kind, f"{column} maps to True and False", column, _flag_bad(column, mapping)),
        _shares(kind, column),
    )


def _list_items_bad(column: str, mark: str, allowed: "set[str]") -> "Callable[[dict[str, object]], object]":
    def run(frames: "dict[str, object]") -> int:
        cells = _t(column)(frames).dropna().astype(str)  # type: ignore[attr-defined]
        return int(sum(1 for cell in cells for item in cell.split(mark) if item not in allowed))

    return run


def _pairs_bad(frames: "dict[str, object]") -> int:
    cells = _t("vital_pairs")(frames).dropna().astype(str)  # type: ignore[attr-defined]
    bad = 0
    for cell in cells:
        found = dict(part.split("=", 1) for part in cell.split(";") if "=" in part)
        bad += 0 if set(found) == {"sys", "dia", "hr"} and all(value.isdigit() for value in found.values()) else 1
    return bad


def _wave_bad(frames: "dict[str, object]") -> int:
    cells = _t("waveform")(frames).dropna().astype(str)  # type: ignore[attr-defined]
    bad = 0
    for cell in cells:
        try:
            values = json.loads(cell)
        except ValueError:
            bad += 1
            continue
        bad += 0 if isinstance(values, list) and len(values) == 8 and all(isinstance(v, float) for v in values) else 1
    return bad


def _json_bad(column: str, keys: "set[str]") -> "Callable[[dict[str, object]], object]":
    def run(frames: "dict[str, object]") -> int:
        bad = 0
        for cell in _t(column)(frames).dropna().astype(str):  # type: ignore[attr-defined]
            try:
                document = json.loads(cell)
            except ValueError:
                bad += 1
                continue
            bad += 0 if isinstance(document, dict) and set(document) == keys else 1
        return bad

    return run


def _rare(
    kind: str, name: str, column: str, pattern: str,
    spoil: "Callable[[list[str], list[list[str]]], None]", crowded: str,
) -> "tuple[Check, Check]":
    """A shape the real holds on a few rows, as two checks: present at all (red on `spoil`), and on its share of the
    rows (red on the shape written on every third cell: a shape on a twentieth of the rows taken away moves its share
    by less than the tolerance)."""
    present, share = _present(kind, name, column, pattern, spoil)

    def crowd(header: "list[str]", rows: "list[list[str]]") -> None:
        place = header.index(column)
        for index in range(0, len(rows), 3):
            rows[index][place] = crowded

    return present, Check(share.kind, share.name, share.mode, share.run, share.column, crowd)


NUMBER_CHECKS = (
    _parses("whole_numbers", "count_whole"),
    _ranged("whole_numbers", "count_whole"),
    _parses("decimal_numbers", "result_decimal"),
    _ranged("decimal_numbers", "result_decimal"),
    _pattern("scientific_notation", "exponents written 1.23E+04", "assay_exponent", r"\d\.\d{2}E[+-]\d{2}"),
    _parses("scientific_notation", "assay_exponent"),
    _pattern("thousands_separators", "amounts grouped by thousands", "charge_grouped", r"\d{1,3}(,\d{3})*\.\d{2}"),
    _ranged("thousands_separators", "charge_grouped", ","),
    _pattern("currency_amounts", "dollar amounts, brackets for negatives", "charge_dollars", r"\(?\$\d{1,3}(,\d{3})*\.\d{2}\)?"),
    *_rare("currency_amounts", "some amounts are negative", "charge_dollars", r"^\(", zoo.spoil_every("charge_dollars", lambda text: text.strip("()")), "($45.00)"),
    _pattern("units_in_values", "an amount and its unit", "dose_with_unit", r"\d+(\.\d+)? (mg|g|mL|units|mcg)"),
    _parses("units_in_values", "dose_with_unit", r" (mg|g|mL|units|mcg)$"),
    _listed("ranges_in_cells", "reference ranges", "reference_range", {value for value, _w in REFERENCE_RANGES}),
    _parses("censored_values", "censored_result", "", ("<0.5", ">100")),
    *_rare("censored_values", "some results are under the limit", "censored_result", r"^<", zoo.spoil_every("censored_result", lambda text: text.lstrip("<")), "<0.5"),
    *_rare("censored_values", "some results are over the limit", "censored_result", r"^>", zoo.spoil_every("censored_result", lambda text: text.lstrip(">")), ">100"),
    _pattern("percentages", "percentages", "percent_written", r"\d+(\.\d)?%"),
    _ranged("percentages", "percent_written", "%"),
    _listed("fractions", "fractions", "fraction_written", {value for value, _w in FRACTIONS}),
    _pattern("signed_numbers", "a plus before the gains", "signed_change", r"[+-]?\d+"),
    *_present("signed_numbers", "some changes carry a plus", "signed_change", r"^\+", zoo.spoil_every("signed_change", lambda text: text.lstrip("+"))),
    _parses("negative_zero", "near_zero_change"),
    *_rare("negative_zero", "some cells write -0.0", "near_zero_change", r"^-0\.0$", zoo.spoil_every("near_zero_change", lambda text: "0.0" if text == "-0.0" else text), "-0.0"),
    _parses("infinity_and_nan_spellings", "ratio_value"),
    *_rare("infinity_and_nan_spellings", "some ratios are infinite", "ratio_value", r"^-?Inf$", zoo.spoil_every("ratio_value", lambda text: "1.000" if "Inf" in text else text), "Inf"),
    _listed("leading_zero_codes", "opening zeros kept on the codes", "unit_code", {value for value, _w in UNIT_CODES}),
    _parses("sentinel_numbers", "pulse_coded"),
    *_rare("sentinel_numbers", "the placeholder 999 is written", "pulse_coded", r"^999$", zoo.spoil_every("pulse_coded", lambda text: "120" if text == "999" else text), "999"),
    _parses("sentinel_words", "temp_with_words", "", MISSING_WORDS),
    *_rare("sentinel_words", "a word written for a missing value", "temp_with_words", r"^(?:unknown|--|\.)$", zoo.spoil_every("temp_with_words", lambda text: "98.6" if text in ("unknown", "--", ".") else text), "unknown"),
)
TEXT_CHECKS = (
    _listed("unicode_scripts", "languages written in their own scripts", "language_written", {value for value, _w in LANGUAGES_WRITTEN}),
    _shares("unicode_scripts", "language_written"),
    _listed("emoji", "comments keep their emoji", "comment_emoji", {value for value, _w in EMOJI_COMMENTS}),
    _listed("mojibake", "names written as the source wrote them", "unit_name_mojibake", {value for value, _w in MOJIBAKE}),
    _listed("control_characters", "a control character inside the value", "control_marked", {value for value, _w in CONTROL_MARKED}),
    _listed("quotes_and_delimiters", "quotes and commas inside cells", "quoted_words", {value for value, _w in QUOTED}),
    _listed("line_breaks_in_cells", "line breaks inside cells", "two_line_text", {value for value, _w in TWO_LINES}),
    _listed("html_fragments", "markup inside cells", "markup_cell", {value for value, _w in MARKUP}),
    _bad("json_fragments", "each cell parses as JSON with its keys", "json_cell", _json_bad("json_cell", {"sys", "dia", "pos"})),
    _pattern("xml_fragments", "each cell is one element", "xml_cell", r'<obs code="P1" unit="/min">\d+</obs>'),
    _pattern("hl7_segments_in_cells", "each cell is an OBX segment", "hl7_segment", r"OBX\|1\|NM\|8867-4\^Heart rate\^LN\|\|\d+\|/min\|60-100\|[NHL]"),
    _bad("fhir_fragments", "each cell parses as a resource", "fhir_fragment", _json_bad("fhir_fragment", {"resourceType", "valueQuantity"})),
    _pattern("base64", "base64 of 24 bytes", "payload_b64", r"[A-Za-z0-9+/]{32}"),
    Check("very_long_strings", "long cells keep their lengths", "ratios", lambda f: zoo._length_percentiles(_t("long_text")(f)), "long_text",
          zoo.spoil_every("long_text", lambda text: text[:200])),
)
DATE_CHECKS = (
    _bad("iso_dates", "iso_day parses as %Y-%m-%d", "iso_day", _dates_bad("iso_day", "%Y-%m-%d")),
    _bad("iso_instants_in_utc", "utc_moment parses with its Z", "utc_moment", _dates_bad("utc_moment", "%Y-%m-%dT%H:%M:%SZ")),
    _bad("iso_instants_with_offsets", "offset_moment parses with its offset", "offset_moment", _dates_bad("offset_moment", "%Y-%m-%dT%H:%M:%S%z", utc=True)),
    _bad("twelve_hour_stamps", "us_moment_ampm parses with AM and PM", "us_moment_ampm", _dates_bad("us_moment_ampm", "%m/%d/%Y %I:%M %p")),
    _bad("day_month_name_year", "day_mon_year parses as %d-%b-%Y", "day_mon_year", _dates_bad("day_mon_year", "%d-%b-%Y")),
    _bad("long_month_names", "long_month_date parses as %B %d, %Y", "long_month_date", _dates_bad("long_month_date", "%B %d, %Y")),
    _pattern("month_names_french", "a French month name", "french_date", r"\d{1,2} (" + "|".join(MONTHS_FR) + r") \d{4}"),
    _pattern("month_names_german", "a German month name", "german_date", r"\d{1,2}\. (" + "|".join(MONTHS_DE) + r") \d{4}"),
    _pattern("month_names_spanish", "a Spanish month name", "spanish_date", r"\d{1,2} de (" + "|".join(MONTHS_ES) + r") de \d{4}"),
    _bad("compact_yyyymmdd", "compact_day parses as %Y%m%d", "compact_day", _dates_bad("compact_day", "%Y%m%d")),
    _pattern("epoch_seconds", "ten figures of seconds", "epoch_seconds", r"1[5-7]\d{8}"),
    _pattern("epoch_milliseconds", "thirteen figures of milliseconds", "epoch_millis", r"1[5-7]\d{11}"),
    _pattern("excel_serial_numbers", "a day count with its fraction", "excel_serial_day", r"4[4-6]\d{3}\.\d{4}"),
    _pattern("durations_hh_mm_ss", "durations as HH:MM:SS", "duration_clock", r"\d{2,3}:[0-5]\d:[0-5]\d"),
    _pattern("durations_in_words", "durations as 1d 3h 15m", "duration_words", r"(\d+d)?( ?\d+h)?( ?\d+m)?"),
    _bad("time_only", "clock_only parses as %H:%M", "clock_only", _dates_bad("clock_only", "%H:%M")),
    _pattern("impossible_dates", "the column writes its dates as %Y-%m-%d", "day_with_impossible", r"\d{4}-\d{2}-\d{2}"),
    *_rare("impossible_dates", "the impossible day is kept", "day_with_impossible", r"^(?:2023-02-30|0000-00-00)$", zoo.spoil_every("day_with_impossible", lambda text: "2023-02-28" if text in ("2023-02-30", "0000-00-00") else text), "0000-00-00"),
    _bad("partial_dates_year_month", "year_month parses as %Y-%m", "year_month", _dates_bad("year_month", "%Y-%m")),
)
CODE_CHECKS = (
    _listed("icd9_codes", "ICD-9 codes from the list", "icd9_code", zoo._levels(ICD9)),
    _listed("rxnorm_codes", "RxNorm codes from the list", "rxnorm_code", zoo._levels(RXNORM)),
    _listed("procedure_codes", "procedure codes from the list", "procedure_code", zoo._levels(PROCEDURES)),
    _listed("drg_codes", "DRG codes keep three figures", "drg_code", zoo._levels(DRG)),
    _listed("revenue_codes_leading_zero", "revenue codes keep their opening zero", "revenue_code", zoo._levels(REVENUE)),
    _listed("two_figure_codes", "two-figure codes keep their zero", "place_code", zoo._levels(PLACE_OF_SERVICE)),
    _listed("dotted_object_identifiers", "object identifiers from the list", "system_oid", zoo._levels(OIDS)),
    _listed("dotted_hierarchical_codes", "dotted codes from the list", "hierarchy_code", zoo._levels(HIERARCHY)),
    _listed("barcodes_with_check_figure", "barcodes from the list", "product_barcode", zoo._levels(PRODUCT_BARCODES)),
    _pattern("urls", "addresses of a chart", "chart_url", r"https://records\.example\.org/chart/P\d{7}/\d{6}"),
    _pattern("ip_addresses", "IPv4 addresses", "device_ip", r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"),
    _pattern("mac_addresses", "MAC addresses", "device_mac", r"([0-9A-F]{2}:){5}[0-9A-F]{2}"),
    _pattern("email_addresses", "e-mail addresses", "contact_email", r"[a-z0-9.]+@example\.org"),
)
ID_CHECKS = (
    _pattern("encounter_keys", "visit keys of a letter and nine figures", "visit_key", r"V\d{9}"),
    _pattern("composite_keys", "a person key and a line number", "visit_line", r"P\d{7}-\d{2}"),
    _pattern("uuids", "UUIDs", "order_uuid", r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"),
    _pattern("hashed_keys", "sha-256 digests", "hashed_key", r"[0-9a-f]{64}"),
    _bad("check_figure_keys", "keys pass their Luhn check", "luhn_key",
         lambda f: int(sum(1 for cell in _t("luhn_key")(f).dropna().astype(str) if _luhn(cell[:-1]) != cell))),  # type: ignore[attr-defined]
    _pattern("keys_past_two_to_the_53", "sixteen figures or more", "specimen_number", r"\d{16,19}"),
)
FLAG_CHECKS = (
    *_flag_checks("flags_y_n", "flag_yn", "Y", "N"),
    *_flag_checks("flags_0_1", "flag_01", "1", "0"),
    *_flag_checks("flags_true_false", "flag_true_false", "True", "False"),
    *_flag_checks("flags_yes_no", "flag_yes_no", "Yes", "No"),
    *_flag_checks("flags_t_f", "flag_tf", "T", "F"),
    *_flag_checks("flags_positive_negative", "flag_pos_neg", "Positive", "Negative"),
    *_flag_checks("flags_present_absent", "flag_present", "Present", "Absent"),
    *_flag_checks("flags_one_or_blank", "flag_one_blank", "1", ""),
    *_flag_checks("flags_x_or_blank", "flag_x_blank", "X", ""),
    _listed("flags_mixed_case", "yes and no in three cases", "flag_mixed_case", {value for value, _w in MIXED_CASE}),
    _shares("flags_mixed_case", "flag_mixed_case"),
    _listed("ordinal_pain_0_10", "pain scores 0 to 10", "pain_score", {f"{s}" for s in range(11)}),
    _shares("ordinal_pain_0_10", "pain_score"),
    _listed("ordinal_gcs", "coma scores 3 to 15", "gcs_total", {f"{s}" for s in range(3, 16)}),
    _listed("ordinal_physical_status", "physical status classes with an emergency mark", "physical_status_class", {value for value, _w in PHYSICAL_STATUS}),
    _listed("ordinal_nyha_roman", "classes in Roman figures", "nyha_class", {value for value, _w in NYHA}),
    _listed("ordinal_likert_words", "how often, in five words", "likert_answer", {value for value, _w in LIKERT}),
    _listed("ordinal_apgar", "scores 0 to 10", "apgar_five", {f"{s}" for s in range(11)}),
    _listed("ordinal_mallampati", "classes 1 to 4", "mallampati", {value for value, _w in MALLAMPATI}),
)
STRUCTURE_CHECKS = (
    _bad("lists_pipe_separated", "list items split on |", "allergy_list",
         _list_items_bad("allergy_list", "|", {name for name, _w in ALLERGENS} | {"NKDA"})),
    *_present("lists_pipe_separated", "some cells hold several items", "allergy_list", r"\|", zoo.spoil_every("allergy_list", lambda text: text.split("|")[0])),
    _bad("key_value_cells", "key=value pairs sys, dia and hr", "vital_pairs", _pairs_bad),
    _bad("arrays_in_cells", "each waveform parses as eight numbers", "waveform", _wave_bad),
    _listed("laterality", "sides", "laterality", {value for value, _w in SIDES}),
    _listed("body_sites", "sites", "body_site", {value for value, _w in SITES}),
    _listed("hgvs_cdna", "cDNA variants", "variant_cdna", zoo._levels(HGVS_C)),
    _listed("hgvs_protein", "protein variants", "variant_protein", zoo._levels(HGVS_P)),
    _parses("numbers_beside_words", "result_mixed", "", tuple(word for word, _w in RESULT_WORDS)),
    *_rare("numbers_beside_words", "some results are words", "result_mixed", r"^(?:see comment|POS|NEG|QNS)$", zoo.spoil_every("result_mixed", lambda text: "1.00" if not text[:1].isdigit() else text), "POS"),
    Check("sparse_columns", "the column is nearly all blank", "share", lambda f: round(float(_t("sparse_status")(f).isna().mean()), 2), "sparse_status",  # type: ignore[attr-defined]
          zoo.spoil_every("sparse_status", lambda _text: "reviewed")),
)
STUDY_CHECKS = (
    _bad("survival_time_and_event", "enrolled_on parses", "enrolled_on", _dates_bad("enrolled_on", "%Y-%m-%d")),
    _parses("survival_time_and_event", "days_to_event"),
    _ranged("survival_time_and_event", "days_to_event"),
    _listed("survival_time_and_event", "event flags 0 and 1", "event_flag", {"0", "1"}),
    _shares("survival_time_and_event", "event_flag"),
    _listed("survival_time_and_event", "event kinds", "event_kind", {"death", "relapse", "censored", "lost"}),
    *(_parses("wide_repeated_columns", f"pulse_{visit}") for visit in range(1, 7)),
    Check("wide_repeated_columns", "later visits are blank more often", "share",
          lambda f: tuple(round(float(_t(f"pulse_{v}")(f).isna().mean()), 2) for v in range(1, 7)), "pulse_6",  # type: ignore[attr-defined]
          zoo.spoil_every("pulse_6", lambda _text: "80")),
    *(_ranged("claims_amounts", name) for name in ("billed_amount", "allowed_amount", "paid_amount")),
)


def _odd_header_reader(path: pathlib.Path) -> "dict[str, object]":
    """pandas reads a repeated name as value and value.1, a blank one as Unnamed: 3."""
    return _csv_reader()(path)


def _total_reader(path: pathlib.Path) -> "dict[str, object]":
    """The analyst skips the totals row and the footer line, as such a report is read."""
    return _csv_reader(skipfooter=3, engine="python")(path)


def _units_row_reader(path: pathlib.Path) -> "dict[str, object]":
    return _csv_reader(skiprows=[1])(path)


# -- 10. A WORKBOOK WITH A SPREADSHEET'S FURNITURE ------------------------------

BOOK_HEADER = ["person_key", "visit_day", "pressure", "", "pressure_ratio", "share_formatted", "amount_formatted", "site"]
BOOK_SITES = ("North", "South", "East", "West", "Central")
# The style a cell wears (`workbooks.FORMAT_CODES`): a date, a percent and a
# currency format, the stored value a plain number.
STYLE_DATE = 1
STYLE_PERCENT = 5
STYLE_CURRENCY = 6


def _book_rows(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """The data sheet's rows as a reader of the stored values sees them: an Excel day, two pressures, a ratio, a share, an amount."""
    draw = random.Random(seed)
    people = max(n // 4, 1)
    rows: "list[list[str]]" = []
    for index in range(n):
        moment = _moment(draw)
        upper = round(draw.gauss(125, 16))
        lower = round(draw.gauss(78, 10))
        rows += [[
            _person_of(index, people, draw), f"{(moment.date() - EXCEL_DAY_NOUGHT.date()).days}",
            f"{upper}", f"{lower}", f"{upper / lower:.6f}", f"{min(max(draw.gauss(0.45, 0.15), 0), 1):.4f}",
            f"{math.exp(draw.gauss(6.0, 1.2)):.2f}", draw.choice(BOOK_SITES),
        ]]
    return BOOK_HEADER, rows


def _letter(place: int) -> str:
    return "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[place]


def _book_bytes(header: "list[str]", rows: "list[list[str]]") -> bytes:
    """A workbook as a clinic's spreadsheet is saved: a hidden notes sheet first, the data, a summary sheet after it.

    The data sheet's header merges `pressure` over two columns (the
    second name blank), its dates are Excel days in a date style, its
    ratio is a formula with its cached value, and its share and amount
    are numbers in a percent and a currency style.
    """
    import workbooks

    head = [workbooks.cell(f"{_letter(place)}1", name, "inlineStr") if name else workbooks.cell(f"{_letter(place)}1")
            for place, name in enumerate(header)]
    body: "list[tuple[int, list[str]]]" = [(1, head)]
    for place, row in enumerate(rows):
        number = place + 2
        cells = [
            workbooks.cell(f"A{number}", row[0], "inlineStr"),
            workbooks.cell(f"B{number}", row[1], "", STYLE_DATE),
            workbooks.cell(f"C{number}", row[2]),
            workbooks.cell(f"D{number}", row[3]),
            workbooks.cell(f"E{number}", row[4], "", 0, f"C{number}/D{number}"),
            workbooks.cell(f"F{number}", row[5], "", STYLE_PERCENT),
            workbooks.cell(f"G{number}", row[6], "", STYLE_CURRENCY),
            workbooks.cell(f"H{number}", row[7], "inlineStr"),
        ]
        body += [(number, cells)]
    data = workbooks.sheet(body, dimension=f"A1:H{len(rows) + 1}", merged=["C1:D1"])
    notes = workbooks.sheet([(1, [workbooks.cell("A1", "made-up notes", "inlineStr")])], dimension="A1:A1")
    summary = workbooks.sheet([(1, [workbooks.cell("A1", "rows", "inlineStr"), workbooks.cell("B1", f"{len(rows)}")])],
                              dimension="A1:B1")
    return workbooks.package([
        ("[Content_Types].xml", workbooks._content_types(3, False, False, False)),
        ("_rels/.rels", workbooks._root_rels()),
        ("xl/workbook.xml", workbooks._workbook([("Notes", "hidden"), ("Data", ""), ("Summary", "")])),
        ("xl/_rels/workbook.xml.rels", workbooks._workbook_rels(3, False)),
        ("xl/styles.xml", workbooks._styles()),
        ("xl/worksheets/sheet1.xml", notes),
        ("xl/worksheets/sheet2.xml", data),
        ("xl/worksheets/sheet3.xml", summary),
    ])


def _book_reader(path: pathlib.Path) -> "dict[str, object]":
    """The analyst reads the workbook's first visible sheet by its name, as a person who opened it would."""
    import crosscheck

    # The suite's cross-check reader is asked for through tests/crosscheck.py alone (tests/test_dependencies.py).
    book = crosscheck.reader().load_workbook(path, read_only=True)  # type: ignore[attr-defined]
    try:
        shown = [sheet.title for sheet in book.worksheets if sheet.sheet_state == "visible"][0]
    finally:
        book.close()
    inferred = crosscheck.read_excel_present(path, sheet_name=shown)
    as_text = crosscheck.read_excel_present(path, sheet_name=shown, dtype=str)
    raw = crosscheck.read_excel_present(path, sheet_name=shown, dtype=str, keep_default_na=False)
    return {"inferred": inferred, "text": as_text, "raw": raw}


def _ratio_bad(frames: "dict[str, object]") -> int:
    import pandas

    frame = frames["inferred"]
    upper = pandas.to_numeric(frame["pressure"], errors="coerce")  # type: ignore[index]
    ratio = pandas.to_numeric(frame["pressure_ratio"], errors="coerce")  # type: ignore[index]
    return int((ratio.isna() | upper.isna()).sum())


def _second_name_given(header: "list[str]", rows: "list[list[str]]") -> None:
    """A spoil: the merged header's blank second name written out."""
    header[3] = "pressure_lower"


def _days_bad(frames: "dict[str, object]") -> int:
    import pandas

    cells = frames["inferred"]["visit_day"]  # type: ignore[index]
    return int(pandas.to_datetime(cells, errors="coerce").isna().sum()) + (0 if "datetime" in str(cells.dtype) else 1)


BOOK_CHECKS = (
    Check("workbook_merged_header_cells", "the merged header reads as pressure and a blank name", "same",
          lambda f: list(f["inferred"].columns)[2:4], "pressure", _second_name_given),  # type: ignore[attr-defined]
    _bad("workbook_formula_cells", "each ratio reads as a number", "pressure_ratio", _ratio_bad,
         zoo.spoil_cell("pressure_ratio", "")),
    _bad("workbook_date_cells", "visit_day reads as dates", "visit_day", _days_bad, zoo.spoil_cell("visit_day", "")),
    _ranged("workbook_number_formats", "share_formatted"),
    _ranged("workbook_number_formats", "amount_formatted"),
    _listed("workbook_hidden_and_extra_sheets", "sites", "site", set(BOOK_SITES)),
)
BOOK_TABLE = Table(
    "workbook_furniture", ".xlsx", _book_rows, _book_bytes,
    {
        "several_rows_a_person": ("person_key",),
        "workbook_date_cells": ("visit_day",),
        "workbook_merged_header_cells": ("pressure", ""),
        "workbook_formula_cells": ("pressure_ratio",),
        "workbook_number_formats": ("share_formatted", "amount_formatted"),
        "workbook_hidden_and_extra_sheets": ("site",),
    },
    {"person_key": "identifier"}, _book_reader, BOOK_CHECKS, person="person_key",
)


# -- 11. A BEDSIDE TABLE: RATES, FLAGS, SCORES, ARTIFACTS, EVENTS (lane ZOO-Y) ---

INFUSION_UNITS = (("mL/hr", 50.0), ("mcg/kg/min", 20.0), ("units/hr", 15.0), ("mg/hr", 15.0))
INFUSION_AMOUNTS = {"mL/hr": (5, 10, 20, 25, 50, 75, 100, 125, 150), "mcg/kg/min": (0.5, 1, 2, 3, 5, 10),
                    "units/hr": (1, 2, 4, 6, 8, 10), "mg/hr": (1, 2, 5, 10)}
LAB_FLAGS = (("", 70.0), ("H", 12.0), ("L", 9.0), ("A", 4.0), ("*", 2.0), ("HH", 2.0), ("LL", 1.0))
RASS = tuple((f"{score:+d}" if score else "0", weight) for score, weight in
             ((-5, 3.0), (-4, 5.0), (-3, 8.0), (-2, 12.0), (-1, 15.0), (0, 40.0), (1, 9.0), (2, 5.0), (3, 2.0),
              (4, 1.0)))
CASE_EVENTS = (("Room in", 15.0), ("Induction", 15.0), ("Incision", 15.0), ("Closure", 15.0), ("Room out", 15.0),
               ("Handover", 10.0), ("Block placed", 8.0), ("Lines placed", 7.0))
COMMENTS = (("pt refused", 30.0), ("see note", 30.0), ("NPO since midnight", 20.0), ("family at bedside", 20.0))


def _infusion(draw: random.Random, _row: Row) -> str:
    unit = draw.choices([unit for unit, _w in INFUSION_UNITS], [w for _u, w in INFUSION_UNITS])[0]
    return f"{draw.choice(INFUSION_AMOUNTS[unit]):g} {unit}"


def _pulse_artifacts(draw: random.Random, _row: Row) -> str:
    roll = draw.random()
    if roll < 0.01:
        return "0"
    if roll < 0.015:
        return "300"
    if roll < 0.03:
        return "???"
    return f"{round(draw.gauss(82, 14))}"


def _event_clock(draw: random.Random, row: Row) -> str:
    return f"{row.moment:%H:%M}"


def _templated_comment(draw: random.Random, _row: Row) -> str:
    if draw.random() < 0.5:
        return f"BP {draw.randint(95, 170)}/{draw.randint(55, 100)} {draw.choice(('L', 'R'))} arm"
    return draw.choices([text for text, _w in COMMENTS], [w for _t, w in COMMENTS])[0]


BEDSIDE_COLUMNS = (
    Column("infusion_rate", "rates_with_units", _infusion, "measurement"),
    Column("rate_value", "value_and_unit_columns", lambda draw, _row: f"{draw.choice((0.5, 1, 2, 5, 10, 20)):g}", "measurement"),
    Column("rate_unit", "value_and_unit_columns", _weighted(INFUSION_UNITS)),
    Column("lab_flag", "abnormal_flags", _weighted(LAB_FLAGS)),
    Column("ref_low", "reference_range_columns", _weighted((("3.5", 40.0), ("135", 30.0), ("0.6", 30.0))), "measurement"),
    Column("ref_high", "reference_range_columns", _weighted((("5.1", 40.0), ("145", 30.0), ("1.2", 30.0))), "measurement"),
    Column("pulse_artifacts", "vital_signs_with_artifacts", _pulse_artifacts, "measurement"),
    Column("case_event", "case_event_stamps", _weighted(CASE_EVENTS)),
    Column("case_event_at", "case_event_stamps", _event_clock),
    Column("sedation_score", "signed_sedation_scale", _weighted(RASS)),
    Column("skin_risk_total", "risk_score_totals", _weighted(tuple((f"{score}", 1.0 + (score - 6) % 7) for score in range(6, 24)))),
    Column("fall_risk_total", "risk_score_totals", _weighted(tuple((f"{score}", 10.0 - score / 25) for score in range(0, 130, 5))), "measurement"),
    Column("short_comment", "comments_with_numbers", _templated_comment),
)

BEDSIDE_CHECKS = (
    _parses("rates_with_units", "infusion_rate", r" (mL/hr|mcg/kg/min|units/hr|mg/hr)$"),
    _pattern("rates_with_units", "a rate and its unit", "infusion_rate", r"\d+(\.\d+)? (mL/hr|mcg/kg/min|units/hr|mg/hr)"),
    _parses("value_and_unit_columns", "rate_value"),
    _listed("value_and_unit_columns", "units from the list", "rate_unit", {unit for unit, _w in INFUSION_UNITS}),
    _listed("abnormal_flags", "flags H, L, A, *, HH, LL or blank", "lab_flag", {flag for flag, _w in LAB_FLAGS if flag}),
    _shares("abnormal_flags", "lab_flag"),
    _parses("reference_range_columns", "ref_low"),
    _parses("reference_range_columns", "ref_high"),
    _parses("vital_signs_with_artifacts", "pulse_artifacts", "", ("???",)),
    _ranged("vital_signs_with_artifacts", "pulse_artifacts", "", ("???",)),
    *_rare("vital_signs_with_artifacts", "an unreadable reading is kept", "pulse_artifacts", r"^\?\?\?$",
           zoo.spoil_every("pulse_artifacts", lambda text: "80" if text == "???" else text), "???"),
    _listed("case_event_stamps", "events from the list", "case_event", {name for name, _w in CASE_EVENTS}),
    _bad("case_event_stamps", "event clocks parse as %H:%M", "case_event_at", _dates_bad("case_event_at", "%H:%M")),
    _listed("signed_sedation_scale", "scores -5 to +4 with their sign", "sedation_score", {score for score, _w in RASS}),
    _shares("signed_sedation_scale", "sedation_score"),
    _listed("risk_score_totals", "totals 6 to 23", "skin_risk_total", {f"{score}" for score in range(6, 24)}),
    _listed("risk_score_totals", "totals 0 to 125 by fives", "fall_risk_total", {f"{score}" for score in range(0, 130, 5)}),
    _pattern("comments_with_numbers", "a pressure and its arm, or a word of the list", "short_comment",
             r"BP \d{2,3}/\d{2,3} (L|R) arm|pt refused|see note|NPO since midnight|family at bedside"),
)


# -- 12. A FLOWSHEET: ONE ROW A READING, ITS MEASURE NAMED IN A COLUMN (lane ZOO-Y)

FLOW_MEASURES = (("Pulse", 30.0), ("SpO2", 25.0), ("Temp", 20.0), ("Pain", 15.0), ("Rhythm", 10.0))
RHYTHMS = (("Sinus", 70.0), ("AFib", 15.0), ("Paced", 10.0), ("Other", 5.0))


def _flowsheet_rows(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A long table: a person, a stamp, which measure, its value (a number or a word), its unit."""
    draw = random.Random(seed)
    people = max(n // 4, 1)
    header = ["person_key", "recorded_at", "measure", "reading", "reading_unit"]
    rows: "list[list[str]]" = []
    for index in range(n):
        who = _person_of(index, people, draw)
        moment = _moment(draw)
        measure = draw.choices([name for name, _w in FLOW_MEASURES], [w for _n, w in FLOW_MEASURES])[0]
        if measure == "Pulse":
            value, unit = f"{round(draw.gauss(82, 14))}", "/min"
        elif measure == "SpO2":
            value, unit = f"{min(100, round(draw.gauss(96, 2)))}", "%"
        elif measure == "Temp":
            value, unit = f"{draw.gauss(37.0, 0.5):.1f}", "Cel"
        elif measure == "Pain":
            value, unit = f"{draw.choices(range(11), [30, 8, 8, 9, 9, 8, 7, 6, 6, 5, 4])[0]}", ""
        else:
            value, unit = draw.choices([name for name, _w in RHYTHMS], [w for _n, w in RHYTHMS])[0], ""
        rows += [[who, f"{moment:%Y-%m-%d %H:%M}", measure, value, unit]]
    return header, rows


def _pulse_readings_bad(frames: "dict[str, object]") -> int:
    """Readings of the measure Pulse that are no number of beats a minute (a cross-column reading of a long table)."""
    import pandas

    text = frames["text"]
    pulses = text[text["measure"] == "Pulse"]["reading"].dropna()  # type: ignore[index]
    numbers = pandas.to_numeric(pulses, errors="coerce")
    return int(numbers.isna().sum() + ((numbers < 0) | (numbers > 300)).sum())


def _rhythm_readings_bad(frames: "dict[str, object]") -> int:
    text = frames["text"]
    rhythms = text[text["measure"] == "Rhythm"]["reading"].dropna()  # type: ignore[index]
    return int((~rhythms.isin([name for name, _w in RHYTHMS])).sum())


FLOWSHEET_CHECKS = (
    _listed("flowsheet_long_table", "measures from the list", "measure", {name for name, _w in FLOW_MEASURES}),
    _bad("flowsheet_long_table", "recorded_at parses", "recorded_at", _dates_bad("recorded_at", "%Y-%m-%d %H:%M")),
    _bad("flowsheet_long_table", "a pulse reading is a number of beats", "reading", _pulse_readings_bad,
         zoo.spoil_every("reading", lambda text: "x" if text.isdigit() else text)),
    _bad("flowsheet_long_table", "a rhythm reading is a word of the list", "reading", _rhythm_readings_bad,
         zoo.spoil_every("reading", lambda text: "Junctional" if text.isalpha() else text)),
    _listed("flowsheet_long_table", "units of the measures", "reading_unit", {"/min", "%", "Cel"}),
)


NUMBER_TABLE = _column_table("typed_numbers", NUMBER_COLUMNS, NUMBER_CHECKS)
TEXT_TABLE = _column_table("typed_text", TEXT_COLUMNS, TEXT_CHECKS)
DATE_TABLE = _column_table("typed_dates", DATE_COLUMNS, DATE_CHECKS)
CODE_TABLE = _column_table("typed_codes", CODE_COLUMNS, CODE_CHECKS)
ID_TABLE = _column_table("typed_keys", ID_COLUMNS, ID_CHECKS)
FLAG_TABLE = _column_table("typed_flags", FLAG_COLUMNS, FLAG_CHECKS)
STRUCTURE_TABLE = _column_table("typed_structures", STRUCTURE_COLUMNS, STRUCTURE_CHECKS)
STUDY_TABLE = Table(
    "typed_study", ".csv", _study_rows, lambda header, rows: csv_bytes(header, rows), dict(STUDY_KINDS),
    {"subject_key": "identifier", "county_fips": "code", "home_latitude": "yes", "home_longitude": "yes"}, _csv_reader(), STUDY_CHECKS,
)
HEADER_TABLE = Table(
    "odd_header", ".csv", _odd_header_rows, lambda header, rows: csv_bytes(header, rows),
    {"several_rows_a_person": ("person_key",), "repeated_blank_numeric_long_names": ("value", "", "2019", "2020", LONG_NAME)},
    {"person_key": "identifier"}, _odd_header_reader,
    (Check("repeated_blank_numeric_long_names", "the column names read back", "same",
           lambda f: list(f["inferred"].columns), "value", zoo.spoil_extra_column),),  # type: ignore[attr-defined]
    person="person_key",
)
TOTAL_TABLE = Table(
    "total_row", ".csv", _total_rows, _with_total_row,
    {"several_rows_a_person": ("person_key",), "totals_and_footer_rows": ("service", "charge", "posted_on")},
    {"person_key": "identifier"}, _total_reader,
    (_parses("totals_and_footer_rows", "charge"),
     _bad("totals_and_footer_rows", "posted_on parses", "posted_on", _dates_bad("posted_on", "%Y-%m-%d"))),
    person="person_key",
)
UNITS_TABLE = Table(
    "units_row", ".csv", _unit_rows, _units_row,
    {"several_rows_a_person": ("person_key",), "units_row_under_the_names": ("glucose", "systolic", "weight")},
    {"person_key": "identifier"}, _units_row_reader,
    tuple(_parses("units_row_under_the_names", name) for name in ("glucose", "systolic", "weight")),
    # The person knows the row under the names names the units (lane ZOO-Y).
    facts=("names", "month-first", "units-row"),
    person="person_key",
)

BEDSIDE_TABLE = _column_table("typed_bedside", BEDSIDE_COLUMNS, BEDSIDE_CHECKS)
FLOWSHEET_TABLE = Table(
    "typed_flowsheet", ".csv", _flowsheet_rows, lambda header, rows: csv_bytes(header, rows),
    {"several_rows_a_person": ("person_key",), "flowsheet_long_table": ("recorded_at", "measure", "reading", "reading_unit")},
    {"person_key": "identifier"}, _csv_reader(), FLOWSHEET_CHECKS, person="person_key",
)

TABLES: "tuple[Table, ...]" = (
    NUMBER_TABLE, TEXT_TABLE, DATE_TABLE, CODE_TABLE, ID_TABLE, FLAG_TABLE, STRUCTURE_TABLE, STUDY_TABLE,
    HEADER_TABLE, TOTAL_TABLE, UNITS_TABLE, BOOK_TABLE, BEDSIDE_TABLE, FLOWSHEET_TABLE,
)
# Every type the battery proves, in the order the report lists them.
TYPES: "tuple[str, ...]" = tuple(
    kind for table in TABLES for kind in table.kinds if kind != "several_rows_a_person"
)
# The date columns each table holds for the owner's date rule.
TABLE_DATES: "dict[str, dict[str, tuple[str, bool]]]" = {
    "typed_dates": DATED,
    "typed_study": {"enrolled_on": ("%Y-%m-%d", False)},
    "typed_flowsheet": {"recorded_at": ("%Y-%m-%d %H:%M", True)},
}


def table_named(name: str) -> Table:
    for table in TABLES:
        if table.name == name:
            return table
    raise KeyError(name)


def seed_of(table: Table) -> int:
    return SEED + [known.name for known in TABLES].index(table.name)


# -- the checks the twin passes before it leaves -------------------------------

# The owner's date rule's tolerance: a weekday's, or an hour's, share in the
# twin within this of the real's.
SHARE_SLACK = 0.02


def _shares_by(values: "list[int]", levels: int) -> "list[float]":
    total = max(len(values), 1)
    return [sum(1 for value in values if value == level) / total for level in range(levels)]


def date_rule(real: pathlib.Path, twin: pathlib.Path, dated: "dict[str, tuple[str, bool]]", read: "Callable[[pathlib.Path], dict[str, object]]") -> "dict[str, dict[str, object]]":
    """The owner's rule for dates (2026-11-18), column by column: weekday and hour kept, the day made up.

    For each column: the largest gap between the twin's and the real's
    share of a weekday (and of an hour, where the column writes a clock),
    and the share of twin cells written on a day some real row of the
    column holds against the share a fresh draw of the same calendar
    would hold (`same_day_share`, `same_day_fresh`): copies of real days
    would push the first far past the second.
    """
    import pandas

    real_frames = read(real)
    twin_frames = read(twin)
    found: "dict[str, dict[str, object]]" = {}
    for column, (form, clock) in dated.items():
        real_dates = pandas.to_datetime(real_frames["text"][column].dropna(), format=form, errors="coerce").dropna()  # type: ignore[index]
        twin_dates = pandas.to_datetime(twin_frames["text"][column].dropna(), format=form, errors="coerce").dropna()  # type: ignore[index]
        if not len(real_dates) or not len(twin_dates):
            found[column] = {"read": False}
            continue
        weekday_gap = max(abs(a - b) for a, b in zip(
            _shares_by(list(real_dates.dt.weekday), 7), _shares_by(list(twin_dates.dt.weekday), 7)))
        entry: "dict[str, object]" = {"read": True, "weekday_gap": round(weekday_gap, 4)}
        if clock:
            entry["hour_gap"] = round(max(abs(a - b) for a, b in zip(
                _shares_by(list(real_dates.dt.hour), 24), _shares_by(list(twin_dates.dt.hour), 24))), 4)
        real_days = set(real_dates.dt.normalize())
        span = pandas.date_range(real_dates.min().normalize(), real_dates.max().normalize(), freq="D")
        entry["same_day_share"] = round(float(twin_dates.dt.normalize().isin(real_days).mean()), 4)
        entry["same_day_fresh"] = round(len(real_days) / max(len(span), 1), 4)
        entry["passes"] = weekday_gap <= SHARE_SLACK and entry.get("hour_gap", 0.0) <= SHARE_SLACK  # type: ignore[operator]
        found[column] = entry
    return found


def five_checks(
    table: Table, real: pathlib.Path, twin: pathlib.Path, floor: bool, answered: bool = True,
) -> "dict[str, object]":
    """The five twin-versus-real checks, as `python -m synthtwin.twin_checks` runs them.

    ``answered``: with the person's answers about every column, as the
    command takes them (`--identifier` for the columns that are
    identifiers, `--not-identifier` for every other column of the
    table); without, the identifiers alone, as a first run types them,
    so the checks' own reading of the other columns is measured too.
    """
    from synthtwin import twin_checks

    every = [column for columns in table.kinds.values() for column in columns]
    identifiers = tuple(sorted(column for column, answer in table.knows.items() if answer == "identifier"))
    others = tuple(sorted(column for column in every if column and column not in identifiers)) if answered else ()
    try:
        outcome = twin_checks.run_checks(
            f"{real}", f"{twin}", person=table.person, identifiers=identifiers, not_identifiers=others,
            small_tables_refused=floor,
        )
    except Exception as failure:  # noqa: BLE001 -- a traceback is a result to record
        return {"error": f"{type(failure).__name__}: {failure}"[:300]}
    return {
        "passed": outcome.passed,
        "checks": {check.code: {"measured": check.measured, "passed": check.passed, "lines": list(check.lines)}
                   for check in outcome.checks},
    }


def run_type_table(
    table: Table, folder: pathlib.Path, n: int, floor: bool, private_beside: "pathlib.Path | None" = None,
) -> "dict[str, object]":
    """The zoo's engine on one type table, then the five checks and the owner's date rule on its twin.

    THE SHIPPED ROUTE WRITES THE INSIDE RECORD, AND THE TWIN IS DRAWN FROM
    IT (plan P4-D496). Its guard refuses a private folder inside the
    system's temporary folders without a word (a test's installation), so
    without ``private_beside`` the zoo's own engine makes its data folder
    there and the twin is the description's alone. With ``private_beside``
    -- a folder outside the temporary ones -- the engine makes it there
    instead (`health_zoo.run_table`'s own argument, lane ZOO-Y), the record
    is written as on a person's computer, and `inside_record` says whether
    it was.
    """
    result = zoo.run_table(table, folder, n, seed_of(table), small_tables_refused=floor, private_beside=private_beside)
    source = folder / f"{table.name}{table.suffix}"
    twin = folder / f"{table.name}-twin{table.suffix}"
    if not twin.is_file():
        twin = folder / f"{table.name}-twin.csv"
    if result.get("steps", {}).get("generate", {}).get("exit") in (0, 3) and twin.is_file():  # type: ignore[union-attr]
        result["five_checks"] = five_checks(table, source, twin, floor)
        result["five_checks_unanswered"] = five_checks(table, source, twin, floor, answered=False)
        dated = TABLE_DATES.get(table.name, {})
        if dated:
            try:
                result["date_rule"] = date_rule(source, twin, dated, table.read)
            except Exception as failure:  # noqa: BLE001 -- what the analyst would have seen
                result["date_rule"] = {"error": f"{type(failure).__name__}: {failure}"[:300]}
    report = folder / f"{table.name}-twin-quality.txt"
    if report.is_file():
        result["report_misses"], result["chain_misses"] = report_misses(report)
    return result


# The quality report's sections a column's facts stand in, and the one
# that judges the chain's family tables between columns (`report_misses`).
FACTS_SECTION = "FACT BY FACT"
NOT_CHECKED_SECTION = "WHAT COULD NOT BE CHECKED, AND WHY"
CHAIN_SECTION = "BETWEEN COLUMNS"


def report_misses(path: pathlib.Path) -> "tuple[list[list[str]], int]":
    """The quality report's own MISSED verdicts: (column, fact) within columns, and how many between columns.

    Read from the report `synthtwin validate` wrote, so a fact the report
    judges an authorized deviation (a date the inside record's dates zone
    made up) is not counted as missed, where the engine's first measure,
    before the record's authority is read, named it so.
    """
    within: "list[list[str]]" = []
    between = 0
    section = ""
    column = ""
    for line in path.read_text(encoding="utf-8").split("\n"):
        stripped = line.strip()
        if stripped in (FACTS_SECTION, NOT_CHECKED_SECTION) or stripped.startswith(CHAIN_SECTION):
            section = stripped
            continue
        if section == FACTS_SECTION and line.startswith("'") and line.rstrip().endswith("'"):
            column = line.strip()[1:-1]
        elif section == FACTS_SECTION and line.startswith("  ") and line.rstrip().endswith(": MISSED"):
            missed = [column, line.strip().split(" ", 1)[0]]
            within += [] if missed in within else [missed]
        elif section.startswith(CHAIN_SECTION) and line.rstrip().endswith(": MISSED"):
            between += 1
    return within, between


def _twin_leaks(result: "dict[str, object]") -> "list[str]":
    """The leak entries whose twin counts are above nought (a real identifier or an age past 89 in the twin)."""
    found = []
    for key, entry in (result.get("leaks") or {}).items():  # type: ignore[union-attr]
        if int(entry.get("twin", 0) or 0) or int(entry.get("twin_cells", 0) or 0):
            found += [f"{key}: {entry.get('twin', 0)} in the twin ({entry.get('twin_cells', 0)} cells)"]
    return found


def type_verdicts(table: Table, result: "dict[str, object]") -> "dict[str, list[str]]":
    """Each type of the table with what failed it ([] where it passes)."""
    failed: "dict[str, list[str]]" = {kind: [] for kind in table.kinds if kind != "several_rows_a_person"}
    steps = result.get("steps") or {}
    for step in ("profile", "answers", "generate", "validate"):
        entry = steps.get(step)  # type: ignore[union-attr]
        if entry is None and step != "answers":
            for kind in failed:
                failed[kind] += [f"{step}: not run"]
        elif entry is not None and entry.get("exit") not in (0, 3):
            for kind in failed:
                failed[kind] += [f"{step}: exit {entry.get('exit')} {entry.get('error', '')}"]
    if not result.get("general", True):
        for kind in failed:
            failed[kind] += ["a question is not general"]
    misses = result["report_misses"] if "report_misses" in result else result.get("misses")
    for column, fact in misses or []:  # type: ignore[union-attr]
        kind = _kind_or_file(table, column)
        if kind in failed:
            failed[kind] += [f"validate misses {column}: {fact}"]
    for name in result.get("analyst_real_errors") or []:  # type: ignore[union-attr]
        for kind in failed:
            failed[kind] += [f"the script fails on the real table: {name}"]
    for kind, name, why in result.get("analyst") or []:  # type: ignore[union-attr]
        if kind in failed:
            failed[kind] += [f"analyst {name}: {why}"[:300]]
    checks = result.get("five_checks") or {}
    if checks and not checks.get("passed"):  # type: ignore[union-attr]
        said = checks.get("error") or [code for code, entry in (checks.get("checks") or {}).items() if not entry["passed"]]  # type: ignore[union-attr]
        for kind in failed:
            failed[kind] += [f"the five checks fail: {said}"]
    for leak in _twin_leaks(result):
        column = leak.split(":", 1)[0].split(" ", 1)[0]
        kind = _kind_or_file(table, column)
        for target in ([kind] if kind in failed else list(failed)):
            failed[target] += [f"twin leak {leak}"]
    for column, entry in (result.get("date_rule") or {}).items():  # type: ignore[union-attr]
        kind = _kind_or_file(table, column)
        if isinstance(entry, dict) and entry.get("read") and not entry.get("passes"):
            failed.setdefault(kind, []).append(f"date rule {column}: {entry}")
        elif isinstance(entry, dict) and entry.get("read") is False:
            failed.setdefault(kind, []).append(f"date rule {column}: the twin's dates do not read")
    return failed


def _kind_or_file(table: Table, column: str) -> str:
    for kind, columns in table.kinds.items():
        if column in columns:
            return kind
    return next(iter(table.kinds))

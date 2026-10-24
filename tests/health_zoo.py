"""The health data zoo: every kind of healthcare data, built at run time (plan P4-D399).

The owner, 2026-10-16: "we should be able to ingest all, and when i say
all, i really mean all type of data that can come in a healthcare
database and reconstruct the twin. We can make question to the user
about the data, general question, but we shouldn't assume that the user
will know details of the analysis."

This module is the CATALOGUE that turns "all" into something counted.
Each kind of healthcare data -- demographics, encounters, diagnosis and
procedure codes, labs, medication orders, vitals, flowsheet rows, REDCap
exports, claims, notes, surveys, wearable series, genomic fields,
imaging metadata, and the file-level shapes the exports arrive in -- is
a seeded generator here, grouped into the tables a hospital system
actually exports. Nothing is committed as data: every table is written
at run time into a folder the caller names, from a seed, and the same
seed and size give the same bytes on every machine.

For every table, `run_table` runs today's product end to end the way a
person would: `profile`; the questions file answered with GENERAL facts
about the data (which column is a record number, which holds codes,
that a blood pressure is two numbers in one cell) and nothing about the
analysis; `profile --answers`; `generate`; `validate`. Then the
table's ANALYST SCRIPT -- written against the column names only, the
way an analyst reads an export with pandas -- runs on the real table and
on the twin, and the two results are compared: the same dtypes, no
unparseable cell where the real has none, no code outside its system's
pattern where the real has none.

`zoo_measures` turns that into the three KPIs of the lane: K-HZ-01, the
kinds that pass end to end with the analyst code running unchanged;
K-HZ-02, each kind's misses and the step that failed, with the lane
that owns it (`OWNERS`); K-HZ-03, the battery's own time and memory
(its driver, `tools/measurements/kpi_health_zoo.py`).

THIS MODULE MEASURES; IT FIXES NOTHING. A kind that fails is recorded
with its owner, never repaired here, and every check reads one column
on its own: what the twin carries between two columns is the stage-6
program's (plan TRACKED T1), and the one check here that needs it -- a
flowsheet's value read by its row name -- is named as such.

The vocabulary is made up for the battery: the codes are drawn from the
public coding systems' own shapes, and no value comes from any real
table.
"""

from __future__ import annotations

import contextlib
import csv
import dataclasses
import datetime
import io
import json
import pathlib
import random
import re
import time
from typing import Callable

import workbooks

# -- the catalogue's kinds ----------------------------------------------

# Every kind of healthcare data the battery proves, in the order the
# report lists them. A kind is a set of columns of one table; the
# file-level kinds are shapes of a whole file, and they carry the
# description's file-level obligations as well as their own columns.
KINDS = (
    "demographics",
    "utf8_accents",
    "encounters",
    "byte_order_mark",
    "crlf_line_endings",
    "diagnoses",
    "procedures",
    "labs",
    "mixed_results",
    "medication_orders",
    "vitals",
    "semicolon_decimal_comma",
    "flowsheet_long",
    "redcap",
    "claims",
    "latin1",
    "clinical_notes",
    "surveys_pro",
    "excel_workbook",
    "wearables",
    "genomics",
    "genomic_ids",
    "imaging",
    "dicom_metadata",
    "perioperative",
    "clock_times",
    "excel_serial_dates",
    "multi_value_cells",
    "tumor_registry",
    "partial_dates",
    "us_unit_vitals",
    "sql_server_export",
    "microbiology",
    "immunizations_providers",
    "risk_and_comorbidity_codes",
    "empty_and_constant_columns",
    "title_rows_above_header",
    "day_first_dates",
    "two_digit_years",
    "true_false_columns",
)
FILE_KINDS = (
    "utf8_accents",
    "byte_order_mark",
    "crlf_line_endings",
    "semicolon_decimal_comma",
    "latin1",
    "excel_workbook",
    "excel_serial_dates",
    "title_rows_above_header",
)

# The answers a questions file may offer that are about WHAT THE DATA
# IS -- a column's nature, a file's layout, how a date is written -- and
# never about an analysis. A question offering any other answer is
# recorded as not general.
GENERAL_ANSWERS = frozenset(
    {
        "measurement", "code", "identifier", "joined", "keep",
        "decimal_comma", "twelve-hour", "data", "metadata-rows",
        "comma", "semicolon", "tab", "vertical-bar", "names",
        "first-record", "month-first", "day-first", "missing",
        "real-value", "1969-2068", "1930-2029", "1940-2039",
        "1900-1999", "dates",
        # The Safe Harbor question (plan P4-D427): whether a value of the
        # column could name a person, a place, a birth date or a number
        # given to one person -- what the data is.
        "no", "yes",
    }
)
# The count systems a column of dates written as numbers may be read in
# (`date_counts`): which one an export used is a fact about the export.
DATE_COUNT_ANSWER = re.compile(
    r"excel-19(00|04)|(days|seconds|milliseconds|microseconds|nanoseconds)-since-\d{4}"
)
# Words that would mean a question asks about the analysis, not the data.
ANALYSIS_WORDS = re.compile(
    r"\b(regression|model|predict\w*|outcome|exposure|hypothes\w*|"
    r"analysis you|your analysis)\b",
    re.IGNORECASE,
)


# -- writing a table ------------------------------------------------------


def csv_bytes(
    header: "list[str]",
    rows: "list[list[str]]",
    delimiter: str = ",",
    newline: str = "\n",
    encoding: str = "utf-8",
    mark: bool = False,
) -> bytes:
    """A delimited table as an exporter writes it, quoting only where needed."""
    buffer = io.StringIO()
    writer = csv.writer(
        buffer, delimiter=delimiter, lineterminator=newline, quoting=csv.QUOTE_MINIMAL
    )
    writer.writerow(header)
    writer.writerows(rows)
    text = buffer.getvalue()
    if mark:
        text = "﻿" + text
    return text.encode(encoding)


def _pick(draw: random.Random, pool: "tuple[tuple[str, float], ...]") -> str:
    """One value of a weighted pool."""
    values = [value for value, _weight in pool]
    weights = [weight for _value, weight in pool]
    return draw.choices(values, weights)[0]


def _day(draw: random.Random, first: datetime.date, last: datetime.date) -> datetime.date:
    return first + datetime.timedelta(days=draw.randint(0, (last - first).days))


# US Eastern time: daylight saving from 02:00 on the second Sunday of
# March to 02:00 on the first Sunday of November.
def _nth_sunday(year: int, month: int, nth: int) -> datetime.date:
    first = datetime.date(year, month, 1)
    return first + datetime.timedelta(days=(6 - first.weekday()) % 7 + 7 * (nth - 1))


def eastern_offsets(moment: datetime.datetime) -> "tuple[str, ...]":
    """Every offset a local US Eastern wall-clock moment may wear, as written.

    None in the hour the clocks skip (02:00 to 02:59 on the second Sunday
    of March never happens), both in the hour they repeat (01:00 to 01:59
    on the first Sunday of November happens once at -04:00 and again at
    -05:00), and the one in force everywhere else.
    """
    hour = datetime.timedelta(hours=1)
    start = datetime.datetime.combine(_nth_sunday(moment.year, 3, 2), datetime.time(2))
    end = datetime.datetime.combine(_nth_sunday(moment.year, 11, 1), datetime.time(2))
    if start <= moment < start + hour:
        return ()
    if end - hour <= moment < end:
        return ("-04:00", "-05:00")
    return ("-04:00",) if start <= moment < end else ("-05:00",)


def eastern_offset(moment: datetime.datetime) -> str:
    """The offset the fixture writes: the first a moment may wear (never a skipped one)."""
    offsets = eastern_offsets(moment)
    assert offsets, f"{moment} is in the hour the clocks skip"
    return offsets[0]


CHANGE_DAYS = (
    datetime.date(2023, 3, 12), datetime.date(2023, 11, 5),
    datetime.date(2024, 3, 10), datetime.date(2024, 11, 3),
)
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


# -- the tables ------------------------------------------------------------

GENDER_CODES = (("M", 48.0), ("F", 50.0), ("U", 1.5), ("X", 0.5))
GENDER_WORDS = (("Male", 48.0), ("Female", 50.0), ("Unknown", 2.0))
ANCESTRIES = (
    ("White", 60.0), ("Black or African American", 18.0), ("Asian", 8.0),
    ("Other", 6.0), ("Unknown", 5.0), ("American Indian or Alaska Native", 2.0),
    ("Native Hawaiian or Other Pacific Islander", 0.6), ("Declined", 0.4),
)
ETHNICITIES = (("Not Hispanic", 80.0), ("Hispanic", 15.0), ("Unknown", 5.0))
ZIPS = (
    ("02139", 14.0), ("02115", 12.0), ("01803", 9.0), ("06510", 8.0), ("07030", 8.0),
    ("08540", 7.0), ("10027", 10.0), ("19104", 9.0), ("33101", 6.0), ("60611", 7.0),
    ("94110", 6.0), ("00501", 0.5),
)
LANGUAGES = (
    ("English", 55.0), ("Español", 15.0), ("Português", 8.0), ("Français", 7.0),
    ("Tiếng Việt", 6.0), ("中文", 5.0), ("Kreyòl ayisyen", 4.0),
)
CITIES = (
    ("Boston", 50.0), ("Bogotá", 12.0), ("São Paulo", 10.0), ("Montréal", 10.0),
    ("Zürich", 6.0), ("San Juan", 8.0), ("Hà Nội", 4.0),
)


def patients(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Demographics: one row per patient, birth dates three ways, '90+' ages."""
    draw = random.Random(seed)
    header = [
        "patient_id", "dob_iso", "dob_us", "dob_text", "age", "gender_code", "gender_word",
        "ancestry", "ethnicity", "zip5", "zip4", "preferred_language", "birth_city",
    ]
    rows: "list[list[str]]" = []
    for index in range(n):
        born = _day(draw, datetime.date(1925, 1, 1), datetime.date(2005, 12, 31))
        years = 2024 - born.year - (1 if (born.month, born.day) > (1, 1) else 0)
        zip5 = _pick(draw, ZIPS)
        rows += [[
            f"PT{1000000 + index:07d}",
            born.isoformat(),
            f"{born.month:02d}/{born.day:02d}/{born.year}",
            f"{born.day:02d}-{MONTHS[born.month - 1]}-{born.year}",
            "90+" if years >= 90 else f"{years}",
            _pick(draw, GENDER_CODES),
            _pick(draw, GENDER_WORDS),
            _pick(draw, ANCESTRIES),
            _pick(draw, ETHNICITIES),
            zip5,
            f"{_pick(draw, ZIPS)}-{draw.randint(1, 9999):04d}",
            _pick(draw, LANGUAGES),
            _pick(draw, CITIES),
        ]]
    return header, rows


DEPARTMENTS = (
    ("Cardiology", 15.0), ("Emergency", 25.0), ("Oncology", 10.0), ("Orthopedics", 10.0),
    ("Pediatrics", 10.0), ("Neurology", 8.0), ("Medicine", 17.0), ("MEDICINE", 5.0),
)
VISIT_TYPES = (("Inpatient", 30.0), ("Outpatient", 40.0), ("Emergency", 25.0), ("Observation", 5.0))


def _stamp(moment: datetime.datetime) -> str:
    return moment.strftime("%Y-%m-%d %H:%M:%S") + eastern_offset(moment)


def encounters(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Encounters: several per patient, stamps with offsets across daylight saving."""
    draw = random.Random(seed)
    people = max(n // 3, 1)
    header = ["enc_id", "patient_id", "admit_ts", "discharge_ts", "stay_days", "department", "visit_type"]
    rows: "list[list[str]]" = []
    for index in range(n):
        if draw.random() < 0.25:
            day = draw.choice(CHANGE_DAYS)
        else:
            day = _day(draw, datetime.date(2023, 1, 1), datetime.date(2024, 12, 31))
        admit = datetime.datetime.combine(day, datetime.time(draw.randint(0, 23), draw.randint(0, 59)))
        if admit.date() in CHANGE_DAYS and admit.month == 3 and admit.hour == 2:
            admit = admit.replace(hour=3)
        stay = draw.choice((0, 0, 1, 1, 2, 3, 4, 5, 7, 10, 14))
        discharge = admit + datetime.timedelta(days=stay, hours=draw.randint(1, 20))
        if discharge.month == 3 and discharge.date() in CHANGE_DAYS and discharge.hour == 2:
            discharge = discharge.replace(hour=3)
        rows += [[
            f"E{100000000 + index}",
            f"PT{1000000 + draw.randrange(people):07d}",
            _stamp(admit),
            _stamp(discharge),
            f"{(discharge.date() - admit.date()).days}",
            _pick(draw, DEPARTMENTS),
            _pick(draw, VISIT_TYPES),
        ]]
    return header, rows


def _zipf(values: "tuple[str, ...]") -> "tuple[tuple[str, float], ...]":
    return tuple((value, 1.0 / (rank + 1)) for rank, value in enumerate(values))


ICD10 = _zipf((
    "E11.9", "I10", "E78.5", "J44.9", "I25.10", "N18.3", "F32.9", "J45.909", "K21.9",
    "M54.5", "E66.9", "I48.91", "Z79.4", "R07.9", "J18.9", "N39.0", "I50.9", "E03.9",
    "G47.33", "F41.1", "Z00.00", "S72.001A", "O80", "C50.911", "A41.9", "U07.1",
))
ICD9 = _zipf((
    "250.00", "401.9", "272.4", "496", "414.01", "585.3", "311", "493.90", "530.81",
    "724.2", "V58.67", "786.50", "486", "599.0", "428.0", "E849.0",
))
SNOMED = _zipf((
    "44054006", "38341003", "55822004", "13645005", "53741008", "709044004", "35489007",
    "195967001", "235595009", "49436004", "73211009", "84114007", "40930008",
    "427089005", "10811121000119102", "16114001000119100",
))
POA = (("Y", 80.0), ("N", 10.0), ("U", 5.0), ("W", 3.0), ("1", 2.0))
PROC = _zipf(("99213", "99214", "99232", "93000", "71046", "80053", "85025", "36415", "99285", "0001U"))
PROC_MODIFIED = _zipf(("99213-25", "97140-59", "99214", "20610-RT", "93010-26", "73030-LT", "97110-GP"))
HCPCS = _zipf(("J1100", "G0439", "A0428", "J3490", "E0114", "Q4081", "G0008", "J1885"))
PCS = _zipf(("0DTJ4ZZ", "02703DZ", "0SR9019", "10E0XZZ", "3E0336Z", "0W9930Z", "B2111ZZ", "5A1955Z"))


def diagnoses_procedures(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Coded rows: ICD-10-CM with and without the dot, ICD-9, SNOMED CT, level I procedure codes, HCPCS, ICD-10-PCS."""
    draw = random.Random(seed)
    header = [
        "enc_id", "dx_seq", "icd10_dotted", "icd10_plain", "icd9", "snomed_id", "poa",
        "proc_code", "proc_code_mod", "hcpcs", "icd10pcs",
    ]
    rows: "list[list[str]]" = []
    for _index in range(n):
        rows += [[
            f"E{100000000 + draw.randrange(max(n // 2, 1))}",
            f"{draw.choice((1, 1, 1, 2, 2, 3, 4, 5))}",
            _pick(draw, ICD10),
            _pick(draw, ICD10).replace(".", ""),
            _pick(draw, ICD9),
            _pick(draw, SNOMED),
            _pick(draw, POA),
            _pick(draw, PROC),
            _pick(draw, PROC_MODIFIED),
            _pick(draw, HCPCS),
            _pick(draw, PCS),
        ]]
    return header, rows


LOINC = _zipf((
    "2345-7", "2160-0", "718-7", "4548-4", "2951-2", "2823-3", "6690-2", "777-3",
    "1742-6", "2093-3", "13457-7", "94500-6", "17861-6", "101284-8",
))
UNITS = (("mmol/L", 40.0), ("mg/dL", 35.0), ("g/dL", 10.0), ("%", 10.0), ("10*3/uL", 5.0))
RANGES = (("3.5-5.0", 25.0), ("70-99", 25.0), ("0.6-1.2", 20.0), ("12.0-16.0", 15.0), ("4.0-5.6", 15.0))
FLAGS = (("", 60.0), ("N", 10.0), ("H", 12.0), ("L", 10.0), ("HH", 4.0), ("LL", 4.0))


def labs(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Labs: LOINC, values with units, POS/NEG, '<5' and '>1000', ranges and H/L flags.

    `result_value` is the one result field an EHR's result table carries
    for every kind of test: a number, a censored number or a word, in one
    column ('5.2', '<5', 'NEGATIVE').
    """
    draw = random.Random(seed)
    header = [
        "patient_id", "collected_at", "loinc", "result", "qualitative", "viral_load",
        "ref_range", "abnormal_flag", "result_value",
    ]
    rows: "list[list[str]]" = []
    for _index in range(n):
        moment = datetime.datetime.combine(
            _day(draw, datetime.date(2023, 1, 1), datetime.date(2024, 12, 31)),
            datetime.time(draw.randint(0, 23), draw.randint(0, 59)),
        )
        level = draw.random()
        if level < 0.15:
            load = "<5"
        elif level < 0.2:
            load = ">1000"
        else:
            load = f"{draw.randint(5, 1000)}"
        rows += [[
            f"PT{1000000 + draw.randrange(max(n // 3, 1)):07d}",
            moment.strftime("%Y-%m-%d %H:%M"),
            _pick(draw, LOINC),
            f"{draw.gauss(5.5, 1.4):.1f} {_pick(draw, UNITS)}",
            _pick(draw, (("POS", 20.0), ("NEG", 78.0), ("INDETERMINATE", 2.0))),
            load,
            _pick(draw, RANGES),
            _pick(draw, FLAGS),
            _mixed_result(draw),
        ]]
    return header, rows


def _mixed_result(draw: random.Random) -> str:
    level = draw.random()
    if level < 0.6:
        return f"{draw.gauss(5.5, 1.4):.1f}"
    if level < 0.72:
        return "<5"
    if level < 0.78:
        return ">1000"
    return _pick(draw, (("NEGATIVE", 70.0), ("POSITIVE", 25.0), ("SEE NOTE", 5.0)))


NDC = _zipf((
    "00071-0155-23", "00093-7146-56", "00378-0208-01", "00591-0405-01", "00904-6278-61",
    "50090-1234-00", "68180-0513-09", "00006-0749-54",
))
RXNORM = _zipf(("197361", "310965", "314076", "860975", "1049621", "197884", "617312", "308136", "866924"))
DOSE_STRINGS = _zipf(("500 mg", "1-2 tabs", "10 units", "0.5 mg", "2 puffs", "1 tab", "250 mg", "40 mg"))
ROUTES = (("PO", 60.0), ("IV", 20.0), ("SC", 8.0), ("IM", 4.0), ("INH", 5.0), ("TOP", 2.5), ("PR", 0.5))
FREQUENCIES = _zipf(("BID", "QD", "TID", "q6h", "PRN", "QHS", "q8h", "q4h PRN"))


def prescriptions(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Medication orders: NDC 5-4-2 and 11 digits, RxNorm, dose strings, routes, BID and q6h."""
    draw = random.Random(seed)
    header = ["order_id", "patient_id", "ndc_542", "ndc_11", "rxnorm", "dose", "route", "frequency"]
    rows: "list[list[str]]" = []
    for index in range(n):
        rows += [[
            f"ORD{50000000 + index}",
            f"PT{1000000 + draw.randrange(max(n // 3, 1)):07d}",
            _pick(draw, NDC),
            _pick(draw, NDC).replace("-", ""),
            _pick(draw, RXNORM),
            _pick(draw, DOSE_STRINGS),
            _pick(draw, ROUTES),
            _pick(draw, FREQUENCIES),
        ]]
    return header, rows


def _comma(value: float, places: int) -> str:
    return f"{value:.{places}f}".replace(".", ",")


def vitals(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Vitals as a European monitor exports them: semicolons, decimal commas, units."""
    draw = random.Random(seed)
    header = ["patient_id", "taken_at", "bp", "temp", "spo2", "pulse", "stature", "weight", "mass_index"]
    rows: "list[list[str]]" = []
    for _index in range(n):
        stature = draw.randint(150, 195)
        weight = draw.gauss(78, 14)
        moment = datetime.datetime.combine(
            _day(draw, datetime.date(2024, 1, 1), datetime.date(2024, 12, 31)),
            datetime.time(draw.randint(6, 22), draw.choice((0, 15, 30, 45))),
        )
        rows += [[
            f"PT{1000000 + draw.randrange(max(n // 3, 1)):07d}",
            moment.strftime("%Y-%m-%d %H:%M"),
            f"{draw.randint(95, 165)}/{draw.randint(55, 100)}",
            f"{_comma(draw.gauss(36.9, 0.5), 1)} °C",
            f"{min(100, max(85, round(draw.gauss(97, 2))))}%",
            f"{draw.randint(50, 120)}",
            f"{stature} cm",
            f"{_comma(weight, 1)} kg",
            _comma(draw.gauss(25.5, 4.0), 1),
        ]]
    return header, rows


def flowsheet(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Flowsheet rows in long format: one measure a row, named by its row."""
    draw = random.Random(seed)
    header = ["patient_id", "recorded_at", "flo_row", "flo_value"]
    rows: "list[list[str]]" = []
    for _index in range(n):
        name = draw.choice(("Pulse", "Resp", "SpO2", "Temp", "BP", "Pain Score"))
        if name == "Pulse":
            value = f"{draw.randint(50, 120)}"
        elif name == "Resp":
            value = f"{draw.randint(10, 26)}"
        elif name == "SpO2":
            value = f"{draw.randint(88, 100)}"
        elif name == "Temp":
            value = f"{draw.gauss(98.4, 0.9):.1f}"
        elif name == "BP":
            value = f"{draw.randint(95, 165)}/{draw.randint(55, 100)}"
        else:
            value = f"{draw.randint(0, 10)}"
        moment = datetime.datetime.combine(
            _day(draw, datetime.date(2024, 1, 1), datetime.date(2024, 6, 30)),
            datetime.time(draw.randint(0, 23), draw.choice((0, 15, 30, 45))),
        )
        rows += [[
            f"PT{1000000 + draw.randrange(max(n // 3, 1)):07d}",
            moment.strftime("%Y-%m-%dT%H:%M:%S"),
            name,
            value,
        ]]
    return header, rows


def redcap(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A REDCap export: events and arms, checkboxes, branching blanks, repeats, DAGs."""
    draw = random.Random(seed)
    header = [
        "record_id", "redcap_event_name", "redcap_repeat_instrument", "redcap_repeat_instance",
        "redcap_data_access_group", "consent_date", "gender", "smoke___1", "smoke___2",
        "smoke___3", "cigs_per_day", "phq_1", "phq_2", "phq_3", "phq_total", "mass_index_calc",
        "baseline_complete", "ae_term",
    ]
    rows: "list[list[str]]" = []
    record = 0
    while len(rows) < n:
        record += 1
        arm = draw.choice((1, 1, 2))
        group = draw.choice(("site_a", "site_a", "site_b", "site_c"))
        events = ["baseline_arm_1", "month_6_arm_1"] if arm == 1 else ["baseline_arm_2"]
        for event in events:
            smoker = draw.random() < 0.3
            items = [draw.randint(0, 3) for _place in range(3)]
            rows += [[
                f"{record}", event, "", "", group,
                _day(draw, datetime.date(2023, 1, 1), datetime.date(2024, 6, 30)).isoformat()
                if event.startswith("baseline") else "",
                draw.choice(("1", "2")) if event.startswith("baseline") else "",
                "1" if smoker else "0",
                "1" if not smoker and draw.random() < 0.2 else "0",
                "1" if not smoker and draw.random() < 0.5 else "0",
                f"{draw.randint(1, 30)}" if smoker else "",
                f"{items[0]}", f"{items[1]}", f"{items[2]}", f"{sum(items)}",
                f"{draw.gauss(26.0, 4.0):.1f}",
                draw.choice(("0", "1", "2", "2", "2")),
                "",
            ]]
        for instance in range(1, draw.choice((0, 0, 0, 1, 2, 3)) + 1):
            rows += [[
                f"{record}", events[0], "adverse_events", f"{instance}", group,
                "", "", "", "", "", "", "", "", "", "", "", "",
                draw.choice(("Headache", "Nausea", "Fatigue", "Dizziness", "Rash")),
            ]]
    return header, rows[:n]


PAYERS = (("MCR", 30.0), ("MCAID", 20.0), ("BCBS", 18.0), ("AETNA", 10.0), ("UHC", 12.0), ("CIGNA", 6.0), ("SELF", 4.0))
DRGS = _zipf(("470", "291", "871", "392", "190", "065", "064", "189", "292", "872"))
REVENUE = _zipf(("0450", "0250", "0300", "0320", "0360", "0636", "0730", "0120"))
FACILITIES = (
    ("General Hospital", 40.0), ("Clínica Santa María", 20.0), ("Hôpital Saint-Jean", 15.0),
    ("Centro Médico Norte", 15.0), ("Klinik Müller", 10.0),
)


def _dollars(value: float) -> str:
    return f"${value:,.2f}"


def claims(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Claim lines in Latin-1: dollar amounts, adjustments in parentheses, DRG, revenue codes."""
    draw = random.Random(seed)
    header = [
        "claim_id", "patient_id", "service_date", "billed", "adjustment", "payer_code", "drg",
        "revenue_code", "facility",
    ]
    rows: "list[list[str]]" = []
    for index in range(n):
        day = _day(draw, datetime.date(2023, 1, 1), datetime.date(2024, 12, 31))
        level = draw.random()
        if level < 0.3:
            adjustment = f"({_dollars(draw.uniform(5, 900))})"
        elif level < 0.8:
            adjustment = "$0.00"
        else:
            adjustment = _dollars(draw.uniform(5, 300))
        rows += [[
            f"CLM{200000000 + index}",
            f"PT{1000000 + draw.randrange(max(n // 3, 1)):07d}",
            f"{day.month:02d}/{day.day:02d}/{day.year}",
            _dollars(draw.lognormvariate(7.0, 1.2)),
            adjustment,
            _pick(draw, PAYERS),
            _pick(draw, DRGS),
            _pick(draw, REVENUE),
            _pick(draw, FACILITIES),
        ]]
    return header, rows


COMPLAINTS = _zipf((
    "chest pain, shortness of breath", "fever, cough", "abdominal pain", "fall, hip pain",
    "headache", "nausea, vomiting, diarrhea", "back pain", "dizziness",
))
NOTE_TYPES = (("Progress Note", 50.0), ("Discharge Summary", 20.0), ("H&P", 20.0), ("Nursing Note", 10.0))
SENTENCES = (
    "Patient [NAME] seen on [DATE] for follow-up.",
    'Reports "feeling better" since last visit.',
    "Denies fever, chills, or night sweats.",
    "Vitals stable; BP 128/76, HR 72.",
    "Plan: continue metformin 500 mg BID, recheck A1c in 3 months.",
    "ID [ID] reviewed with ***.",
    "Lungs clear to auscultation bilaterally.",
    "Follow up with PCP in 2 weeks, sooner if symptoms worsen.",
)


def notes(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Clinical notes: short and long free text, commas, quotes and line breaks in quoted cells."""
    draw = random.Random(seed)
    header = ["note_id", "enc_id", "note_type", "chief_complaint", "note_text"]
    rows: "list[list[str]]" = []
    for index in range(n):
        lines = [
            " ".join(draw.choice(SENTENCES) for _word in range(draw.randint(1, 3)))
            for _line in range(draw.randint(1, 5))
        ]
        rows += [[
            f"N{70000000 + index}",
            f"E{100000000 + draw.randrange(max(n // 2, 1))}",
            _pick(draw, NOTE_TYPES),
            _pick(draw, COMPLAINTS),
            "\n".join(lines),
        ]]
    return header, rows


LIKERT = (
    ("Strongly disagree", 10.0), ("Disagree", 20.0), ("Neutral", 30.0), ("Agree", 28.0),
    ("Strongly agree", 12.0),
)
ASKED = (("Yes", 45.0), ("No", 35.0), ("NA", 12.0), ("Not asked", 8.0))
EXCEL_EPOCH = datetime.date(1899, 12, 30)


def surveys(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A patient-reported outcome survey: Likert words and numbers, totals, -99 and 999 codes."""
    draw = random.Random(seed)
    header = ["respondent_id", "survey_date", "q1_word", "q2_score", "q3_score", "scale_total", "q4_status"]
    rows: "list[list[str]]" = []
    for index in range(n):
        day = _day(draw, datetime.date(2023, 1, 1), datetime.date(2024, 12, 31))
        first = draw.randint(1, 5)
        second = draw.randint(1, 5)
        rows += [[
            f"R{10000 + index}",
            f"{(day - EXCEL_EPOCH).days}",
            _pick(draw, LIKERT),
            f"{first}" if draw.random() > 0.08 else "-99",
            f"{second}" if draw.random() > 0.05 else "-99",
            f"{first + second}" if draw.random() > 0.06 else "999",
            _pick(draw, ASKED),
        ]]
    return header, rows


def survey_book(header: "list[str]", rows: "list[list[str]]") -> bytes:
    """The survey as an Excel workbook: typed number cells, a date style, text inline.

    A cell of a typed column that is not a number is written as text,
    the way a person typing over a cell leaves it.
    """
    numeric = {"q2_score", "q3_score", "scale_total"}
    body: "list[tuple[int, list[str]]]" = [
        (1, [workbooks.cell(f"{_letter(place)}1", header[place], "inlineStr")
             for place in range(len(header))])
    ]
    for index in range(len(rows)):
        number = index + 2
        cells: "list[str]" = []
        for place in range(len(header)):
            name = header[place]
            value = rows[index][place]
            where = f"{_letter(place)}{number}"
            typed = re.fullmatch(r"-?\d+(\.\d+)?", value) is not None
            if name == "survey_date" and typed:
                cells += [workbooks.cell(where, value, "", 1)]
            elif name in numeric and typed:
                cells += [workbooks.cell(where, value)]
            else:
                cells += [workbooks.cell(where, value, "inlineStr")]
        body += [(number, cells)]
    last = f"{_letter(len(header) - 1)}{len(rows) + 1}"
    return workbooks.package(
        [
            ("[Content_Types].xml", workbooks._content_types(1, False, False, False)),
            ("_rels/.rels", workbooks._root_rels()),
            ("xl/workbook.xml", workbooks._workbook([("Survey", "")])),
            ("xl/_rels/workbook.xml.rels", workbooks._workbook_rels(1, False)),
            ("xl/styles.xml", workbooks._styles()),
            ("xl/worksheets/sheet1.xml", workbooks.sheet(body, dimension=f"A1:{last}")),
        ]
    )


def _letter(place: int) -> str:
    return "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[place]


def wearables(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A wearable's series: second-resolution stamps, step counts with many zeros."""
    draw = random.Random(seed)
    header = ["device_id", "ts", "steps", "heart_rate", "activity"]
    rows: "list[list[str]]" = []
    start = datetime.datetime(2024, 5, 1, 8, 0, 0)
    for index in range(n):
        moment = start + datetime.timedelta(seconds=index * 7 + draw.randint(0, 6))
        moving = draw.random() > 0.4
        rows += [[
            f"DEV-{draw.randint(1, max(n // 4, 2)):04d}",
            moment.strftime("%Y-%m-%dT%H:%M:%S"),
            f"{draw.randint(1, 40) if moving else 0}",
            f"{draw.randint(52, 160)}",
            _pick(draw, (("sedentary", 40.0), ("light", 30.0), ("moderate", 20.0), ("vigorous", 10.0))),
        ]]
    return header, rows


GENES = _zipf(("BRCA1", "BRCA2", "TP53", "CFTR", "EGFR", "KRAS", "BRAF", "MLH1", "HLA-B", "APOE"))
HGVS_C = _zipf((
    "c.123A>G", "c.5266dupC", "c.1521_1523delCTT", "c.68_69delAG", "c.35delG",
    "c.1A>G", "c.2T>C", "c.3920T>G", "c.-21C>T", "c.1799T>A",
))
HGVS_P = _zipf(("p.Arg117His", "p.Phe508del", "p.Gly12Asp", "p.Val600Glu", "p.Leu858Arg", "p.Gln1756fs", "p.="))
OMIM = ("113705", "600185", "191170", "602421", "131550", "190070", "164757", "120436", "142830", "107741")
HGNC = ("HGNC:1100", "HGNC:1101", "HGNC:11998", "HGNC:1884", "HGNC:3236", "HGNC:6407", "HGNC:1097", "HGNC:7127", "HGNC:4932", "HGNC:613")
CLINVAR = _zipf(("VCV000017661", "VCV000007105", "VCV000012374", "VCV000013961", "VCV000009322", "VCV000376716"))
GA4GH = _zipf((
    "ga4gh:VA.0VbYIUSKNp3vL9xHjCCQOLwVg6DZaaEA", "ga4gh:VA.ttAbM9lSj2RYQiBV5k3QrVbW1F49ShHs",
    "ga4gh:VA.4m5sDOR7q4zN5u6WqYBSfR9Fp1_sBe9d", "ga4gh:VA.f-OFRoYi0b9kXxxQ5cv4N1lEcPQ79tVq",
))
CLASSES = (
    ("Pathogenic", 15.0), ("Likely pathogenic", 10.0), ("Uncertain significance", 45.0),
    ("Likely benign", 15.0), ("Benign", 15.0),
)


def genomics(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Variant calls: HGVS strings, gene symbols, allele frequencies."""
    draw = random.Random(seed)
    header = [
        "sample_id", "gene", "hgvs_c", "hgvs_p", "allele_freq", "zygosity", "classification",
        "omim", "hgnc_id", "clinvar_id", "ga4gh_id",
    ]
    rows: "list[list[str]]" = []
    for index in range(n):
        gene = draw.randrange(len(GENES))
        rows += [[
            f"S{300000 + index}",
            _pick(draw, GENES),
            _pick(draw, HGVS_C),
            _pick(draw, HGVS_P),
            f"{min(0.5, draw.expovariate(40.0)):.4f}",
            _pick(draw, (("heterozygous", 70.0), ("homozygous", 28.0), ("hemizygous", 2.0))),
            _pick(draw, CLASSES),
            OMIM[gene],
            HGNC[gene],
            _pick(draw, CLINVAR),
            _pick(draw, GA4GH),
        ]]
    return header, rows


MODALITIES = (
    ("CT", 25.0), ("MR", 15.0), ("CR", 20.0), ("DX", 15.0), ("US", 12.0), ("NM", 4.0),
    ("PT", 3.0), ("MG", 5.0), ("XA", 1.0),
)
BODY_PARTS = (("CHEST", 35.0), ("HEAD", 20.0), ("ABDOMEN", 18.0), ("KNEE", 9.0), ("SPINE", 10.0), ("PELVIS", 8.0))


def imaging(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Imaging metadata as a PACS exports it: accession, modality, and DICOM's DA, TM and UID."""
    draw = random.Random(seed)
    header = [
        "accession", "patient_id", "modality", "study_date", "study_time", "study_uid",
        "body_part", "series_count",
    ]
    rows: "list[list[str]]" = []
    for index in range(n):
        day = _day(draw, datetime.date(2023, 1, 1), datetime.date(2024, 12, 31))
        rows += [[
            f"ACC{40000000 + index}",
            f"PT{1000000 + draw.randrange(max(n // 3, 1)):07d}",
            _pick(draw, MODALITIES),
            day.strftime("%Y%m%d"),
            f"{draw.randint(7, 19):02d}{draw.randint(0, 59):02d}{draw.randint(0, 59):02d}"
            f".{draw.randint(0, 999999):06d}",
            f"1.2.840.113619.2.55.3.{draw.randint(100000000, 999999999)}.{draw.randint(100, 999)}"
            f".{1600000000 + index}",
            _pick(draw, BODY_PARTS),
            f"{draw.randint(1, 12)}",
        ]]
    return header, rows


PHYSICAL_STATUS = (("I", 10.0), ("II", 40.0), ("III", 35.0), ("IV", 10.0), ("III E", 4.0), ("V", 1.0))


def perioperative(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """An operating-room log kept in a spreadsheet and saved as CSV.

    Times of day three ways ('07:42', '07:55:10', '08:30 PM'), a case
    length as hours and minutes, the physical-status class in roman
    figures with its emergency mark ('III E'),
    and the case date as the spreadsheet's serial number.
    """
    draw = random.Random(seed)
    header = [
        "surgery_id", "patient_id", "case_date_serial", "in_room", "anes_start", "incision_time",
        "case_duration", "phys_status", "or_room",
    ]
    rows: "list[list[str]]" = []
    for index in range(n):
        day = _day(draw, datetime.date(2023, 1, 1), datetime.date(2024, 12, 31))
        start = datetime.datetime.combine(day, datetime.time(draw.randint(6, 19), draw.randint(0, 59), draw.randint(0, 59)))
        cut = start + datetime.timedelta(minutes=draw.randint(10, 50))
        minutes = draw.randint(20, 400)
        rows += [[
            f"SRG{500000 + index}",
            f"PT{1000000 + draw.randrange(max(n // 3, 1)):07d}",
            f"{(day - EXCEL_EPOCH).days}",
            start.strftime("%H:%M"),
            (start + datetime.timedelta(minutes=draw.randint(5, 15))).strftime("%H:%M:%S"),
            cut.strftime("%I:%M %p"),
            f"{minutes // 60:02d}:{minutes % 60:02d}",
            _pick(draw, PHYSICAL_STATUS),
            f"OR {draw.randint(1, 14)}",
        ]]
    return header, rows


PROBLEMS = ("E11.9", "I10", "N18.3", "E78.5", "J44.9", "F32.9", "I25.10", "K21.9", "M54.5", "Z79.4")
ALLERGENS = ("Penicillin", "Sulfa", "Latex", "Peanut", "Codeine")


def problem_list(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Several codes or words in one cell: a problem list by ';', allergies by '|'."""
    draw = random.Random(seed)
    header = ["enc_id", "dx_list", "allergies"]
    rows: "list[list[str]]" = []
    for index in range(n):
        rows += [[
            f"E{100000000 + index}",
            ";".join(draw.sample(PROBLEMS, draw.randint(1, 4))),
            "|".join(draw.sample(ALLERGENS, draw.randint(0, 2))) or "NKDA",
        ]]
    return header, rows


MORPHOLOGY = _zipf(("8500/3", "8140/3", "8070/3", "8520/3", "9680/3", "8010/2"))
TOPOGRAPHY = _zipf(("C50.9", "C18.7", "C34.1", "C61.9", "C83.3", "C44.3"))
STAGES = (("I", 25.0), ("IIA", 15.0), ("IIB", 12.0), ("IIIA", 12.0), ("IIIB", 10.0), ("IV", 26.0))


def tumor_registry(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A tumor registry: dates known to the year or month, ICD-O-3, TNM."""
    draw = random.Random(seed)
    header = ["tumor_id", "dx_date", "first_treatment_month", "morphology", "topography", "tnm", "stage"]
    rows: "list[list[str]]" = []
    for index in range(n):
        year, month, day = draw.randint(1995, 2023), draw.randint(1, 12), draw.randint(1, 28)
        known = draw.random()
        if known < 0.2:
            when = f"{year}"
        elif known < 0.45:
            when = f"{month:02d}/{year}"
        else:
            when = f"{year}-{month:02d}-{day:02d}"
        treated = datetime.date(year, month, 1) + datetime.timedelta(days=draw.randint(10, 120))
        rows += [[
            f"T{80000 + index}",
            when,
            f"{treated.year}-{treated.month:02d}",
            _pick(draw, MORPHOLOGY),
            _pick(draw, TOPOGRAPHY),
            f"T{draw.randint(1, 4)}N{draw.randint(0, 3)}M{draw.choice((0, 0, 0, 1))}",
            _pick(draw, STAGES),
        ]]
    return header, rows


def us_vitals(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Vitals in US units: 5'10\", '172 lb', '98.4 F', several rows a patient."""
    draw = random.Random(seed)
    header = ["patient_id", "stature", "weight", "temp_f"]
    rows: "list[list[str]]" = []
    for _index in range(n):
        inches = draw.randint(58, 76)
        rows += [[
            f"PT{1000000 + draw.randrange(max(n // 3, 1)):07d}",
            f"{inches // 12}'{inches % 12}\"",
            f"{draw.randint(100, 260)} lb",
            f"{draw.gauss(98.4, 0.8):.1f} F",
        ]]
    return header, rows


def sql_server(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A SQL Server export: milliseconds on its stamps, the literal NULL, zero-padded record numbers."""
    draw = random.Random(seed)
    header = ["record_no", "created_dttm", "death_date", "is_active", "middle_initial"]
    rows: "list[list[str]]" = []
    for _index in range(n):
        moment = datetime.datetime(2023, 1, 1) + datetime.timedelta(
            seconds=draw.randint(0, 60_000_000), milliseconds=draw.randint(0, 999)
        )
        died = datetime.date(2023, 1, 1) + datetime.timedelta(days=draw.randint(0, 700))
        rows += [[
            f"{draw.randint(1, 999999):09d}",
            moment.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            died.isoformat() if draw.random() < 0.12 else "NULL",
            draw.choice(("0", "1")),
            "NULL" if draw.random() < 0.3 else draw.choice(("A", "B", "C")),
        ]]
    return header, rows


ORGANISMS = (("E. coli", 40.0), ("S. aureus", 25.0), ("K. pneumoniae", 20.0), ("P. aeruginosa", 15.0))
ANTIBIOTICS = (("Ampicillin", 25.0), ("Ceftriaxone", 25.0), ("Vancomycin", 25.0), ("Ciprofloxacin", 25.0))
MICS = _zipf(("<=0.5", "1", "2", "<=0.25", "4", ">=32", "8", ">=64", "16"))


def microbiology(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Susceptibility results: MIC values with '<=' and '>=', S/I/R."""
    draw = random.Random(seed)
    header = ["isolate_id", "organism", "antibiotic", "mic", "interp"]
    rows: "list[list[str]]" = []
    for index in range(n):
        rows += [[
            f"M{60000 + index}",
            _pick(draw, ORGANISMS),
            _pick(draw, ANTIBIOTICS),
            _pick(draw, MICS),
            _pick(draw, (("S", 60.0), ("I", 10.0), ("R", 30.0))),
        ]]
    return header, rows


CVX = _zipf(("08", "03", "140", "208", "115", "21", "10", "133", "62", "212"))
MVX = _zipf(("PFR", "MOD", "MSD", "SKB", "PMC", "JSN", "NOV"))


def _npi(draw: random.Random) -> str:
    """A ten-figure NPI whose last figure is its Luhn check over the prefix 80840."""
    body = "1" + "".join(f"{draw.randint(0, 9)}" for _place in range(8))
    return body + f"{_luhn_check('80840' + body)}"


def _luhn_check(figures: str) -> int:
    total = 0
    for place, figure in enumerate(reversed(figures)):
        value = int(figure)
        if place % 2 == 0:
            value *= 2
            value = value - 9 if value > 9 else value
        total += value
    return (10 - total % 10) % 10


def immunizations(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Immunizations and their providers: CVX with its leading zero, MVX, NPI, UDI."""
    draw = random.Random(seed)
    header = ["patient_id", "cvx", "mvx", "npi", "udi", "dose_number"]
    providers = [_npi(draw) for _place in range(40)]
    devices = [
        f"(01){draw.randrange(10**13, 10**14)}(17){draw.randrange(250101, 271231)}(10)LOT{draw.randrange(100, 999)}"
        for _place in range(20)
    ]
    rows: "list[list[str]]" = []
    for _index in range(n):
        rows += [[
            f"PT{1000000 + draw.randrange(max(n // 3, 1)):07d}",
            _pick(draw, CVX),
            _pick(draw, MVX),
            draw.choice(providers),
            draw.choice(devices),
            f"{draw.randint(1, 3)}",
        ]]
    return header, rows


ELIXHAUSER = _zipf(("HTN", "DM", "CHF", "CHRNLUNG", "RENLFAIL", "HYPOTHY", "VALV", "LIVER", "PERIVASC", "PULMCIRC"))
CDPS = _zipf(("CAR-L", "PSY-M", "PUL-L", "CNS-M", "GI-L", "SKC-L", "CAR-H", "PSY-VH"))


def risk_adjustment(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A payer's risk file: CMS-HCC, APC, CDPS, Charlson and Elixhauser, clinical classes."""
    draw = random.Random(seed)
    header = ["member_id", "cms_hcc", "apc", "cdps", "charlson", "elixhauser", "clinical_class"]
    rows: "list[list[str]]" = []
    for index in range(n):
        rows += [[
            f"MBR{7000000 + index}",
            f"HCC{_pick(draw, _zipf(('19', '85', '18', '111', '108', '96', '22', '59', '40', '2')))}",
            _pick(draw, _zipf(("5012", "5521", "5072", "5302", "5734", "5822", "5113"))),
            _pick(draw, CDPS),
            f"{min(12, int(draw.expovariate(0.6)))}",
            _pick(draw, ELIXHAUSER),
            f"{_pick(draw, _zipf(('98', '49', '108', '127', '205', '106', '59', '651', '101', '53')))}",
        ]]
    return header, rows


def edge_columns(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """An export with a column nobody filled and a column that never changes."""
    draw = random.Random(seed)
    header = ["patient_id", "middle_name", "facility", "age_years"]
    rows: "list[list[str]]" = []
    for index in range(n):
        rows += [[f"PT{1000000 + index:07d}", "", "MAIN", f"{draw.randint(18, 89)}"]]
    return header, rows


TITLE_LINES = "Ward Activity Report\nExported 16/10/2026 by the information office\n"
WARDS = (("Ward 1", 30.0), ("Ward 2", 25.0), ("Ward 3", 15.0), ("HDU", 10.0), ("Maternity", 20.0))


def titled_report(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A report saved as CSV with two title lines above the column names, every column text.

    No column holds bare numbers, so nothing in the values tells the
    names' row from a record: the product asks which row the names are
    in, and the person says.
    """
    draw = random.Random(seed)
    header = ["report_ref", "ward", "admitted", "went_home"]
    rows: "list[list[str]]" = []
    for index in range(n):
        admitted = _day(draw, datetime.date(2024, 1, 1), datetime.date(2024, 12, 31))
        rows += [[
            f"RPT{300000 + index}",
            _pick(draw, WARDS),
            admitted.isoformat(),
            (admitted + datetime.timedelta(days=draw.choice((0, 1, 1, 2, 2, 3, 4, 5, 7, 9, 12)))).isoformat(),
        ]]
    return header, rows


def registry_extract(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A registry's extract as a European office writes it.

    Dates day first ('29/06/2022', '03.08.2022'), years in two figures
    ('06-NOV-22', and birth dates '02/03/62' whose century the person
    knows), and true/false columns in either case.
    """
    draw = random.Random(seed)
    header = ["case_ref", "referral_date", "seen_date", "op_date", "dob_short", "on_waiting_list", "consented"]
    rows: "list[list[str]]" = []
    for index in range(n):
        referred = datetime.date(2019, 1, 1) + datetime.timedelta(days=draw.randint(0, 2000))
        seen = referred + datetime.timedelta(days=draw.randint(3, 90))
        operated = seen + datetime.timedelta(days=draw.randint(1, 120))
        born = datetime.date(1930, 1, 1) + datetime.timedelta(days=draw.randint(0, 25000))
        rows += [[
            f"CR-{100000 + index:06d}",
            referred.strftime("%d/%m/%Y"),
            seen.strftime("%d.%m.%Y"),
            f"{operated.day:02d}-{MONTHS[operated.month - 1].upper()}-{operated.year % 100:02d}",
            f"{born.day:02d}/{born.month:02d}/{born.year % 100:02d}",
            draw.choice(("TRUE", "FALSE", "FALSE")),
            draw.choice(("true", "true", "false")),
        ]]
    return header, rows


# -- the analyst scripts ---------------------------------------------------
#
# Each table's script is what an analyst writes against the column
# names: read the export with pandas, parse dates in the source's own
# format, match codes with their system's pattern, split '120/80', read
# units and censored values. Each check returns either a COUNT OF BAD
# CELLS ("bad": where the real table has none, the twin may have none),
# a value both files must share ("same"), or whether a shape is there at
# all ("present": where the real table has it, the twin must), or a
# SHARE of the rows, or several ("share": each of the twin's within
# SHARE_TOLERANCE of the real's), the least, middle and greatest number
# a column holds past its unit or mark ("range": the twin's middle
# within RANGE_TOLERANCE of the real's, its ends inside the real's
# range widened by RANGE_TOLERANCE of its width), or percentiles of a
# length ("ratios": each of the twin's within LENGTH_TOLERANCE of the
# real's, as a ratio). Every "present" check has a "share" sibling, so a
# shape kept on a handful of cells is not the shape kept.
#
# Beside the table's own checks, `analyse` runs the same GENERIC checks
# on every column and every file (`generic_mode`): the dtype pandas
# infers; the missing cells ("bad"); the spellings of missing a cell
# wears, counted ("spellings": none the real table never wrote, every
# one 11 or more real cells write, each at its share); the cells written
# as the product's stand-in 'group-N' ("bad"); for a column answered
# `code`, the cells holding a value the real never writes ("codes"); the
# shapes of its text, digits read as 9 and letters as a ("shapes": none
# the real table never wrote, and every shape 11 or more real cells
# hold); the forms of its text character by character, each figure a 9,
# each capital an A and each small letter an a ("forms": none the real
# never wrote on 11 or more twin cells, and every form 11 or more real
# cells hold), which sees a date or a clock written unpadded or in
# another case; for a column of few values, read as text whatever dtype
# pandas infers, the values themselves ("levels": every value 11 or more
# real cells hold); the rows read; and, for a delimited file, its
# byte-order mark, its line endings and whether it decodes as UTF-8
# ("same").

SHARE_TOLERANCE = 0.1
# The range check's slack: the middle within 10 % of the real's (1 % of
# the real's width where its middle is nought), the ends within 10 % of
# the real's width beyond its own.
RANGE_TOLERANCE = 0.1
# A length percentile of the twin within 25 % of the real's.
LENGTH_TOLERANCE = 0.25
# The stand-in the product writes for a level too few rows hold.
STAND_IN = r"group-\d+"
# Columns answered `code` whose values the twin must NOT copy where few
# rows hold them: a ZIP code past its first three figures is one of
# HIPAA's Safe Harbor identifiers (the owner's principle of 2026-10-01:
# HIPAA exposure is the threat), so a ZIP+4 the real never writes is the
# rule there, not a gap. The `codes` check leaves them out; their levels,
# shapes and forms are checked like any column's.
NOT_A_VOCABULARY = frozenset({"zip5", "zip4"})
# The columns naming a place smaller than a state: a five-figure ZIP code
# (45 CFR 164.514(b)(2)(i)(B)); the four-figure ZIP+4 add-on alone is not.
PLACES = frozenset({"zip5"})
# A text column is read for its shapes when the real table writes it in
# at most this many shapes; free text, whose sentences recombine, is not.
SHAPED_AT_MOST = 30
# The floor every count printed on its own keeps (the owner's rulings):
# a shape held by this many real cells or more is one the twin must write.
FLOOR = 11
# What pandas reads as missing by default, so the spellings of missing a
# file carries can be read with `keep_default_na=False` and compared.
MISSING_SPELLINGS = frozenset({
    "", "#N/A", "#N/A N/A", "#NA", "-1.#IND", "-1.#QNAN", "-NaN", "-nan", "1.#IND",
    "1.#QNAN", "<NA>", "N/A", "NA", "NULL", "NaN", "None", "n/a", "nan", "null",
})
BYTE_ORDER_MARK = b"\xef\xbb\xbf"
# The dtypes pandas gives a column of text: `object` before pandas 3,
# `str` from it (CI's `minimums` cell runs the declared floor).
TEXT_DTYPES = ("object", "str", "string")
JUNK = "?§?"

@dataclasses.dataclass(frozen=True)
class Check:
    """One step of an analyst script: the kind it serves, its name and its mode.

    `column` is the column it reads, and `spoil` the change to a real
    table that must make it fail (`tests/test_health_zoo.py` runs every
    one): by default, the column's first cell written as JUNK.
    """

    kind: str
    name: str
    mode: str
    run: "Callable[[dict[str, object]], object]"
    column: str = ""
    spoil: "Callable[[list[str], list[list[str]]], None] | None" = None


def spoil_cell(column: str, value: str = JUNK, row: int = 0) -> "Callable[[list[str], list[list[str]]], None]":
    """A spoil: one cell of a column written as `value`."""

    def change(header: "list[str]", rows: "list[list[str]]") -> None:
        rows[row][header.index(column)] = value

    return change


def spoil_every(column: str, how: "Callable[[str], str]") -> "Callable[[list[str], list[list[str]]], None]":
    """A spoil: every cell of a column rewritten."""

    def change(header: "list[str]", rows: "list[list[str]]") -> None:
        place = header.index(column)
        for row in rows:
            row[place] = how(row[place])

    return change


def spoil_of(check: Check) -> "Callable[[list[str], list[list[str]]], None]":
    """The change to a real table that must make this check fail."""
    if check.spoil is not None:
        return check.spoil
    assert check.column, f"{check.name}: a check with no column must say how it is spoiled"
    return spoil_cell(check.column)


def signature(text: str) -> str:
    """A cell's shape: every run of digits read as 9, every run of letters as a."""
    return re.sub(r"\d+", "9", re.sub(r"[^\W\d_]+", "a", text))


def form(text: str) -> str:
    """A cell's form, character by character: each figure a 9, each capital an A, each other letter an a."""
    lettered = re.sub(r"[^\W\d_]", lambda letter: "A" if letter.group().isupper() else "a", text)
    return re.sub(r"\d", "9", lettered)


def _bad_pattern(series: object, pattern: str) -> int:
    values = series.dropna().astype(str)  # type: ignore[attr-defined]
    return int((~values.str.fullmatch(pattern)).sum())


def _bad_set(series: object, allowed: "set[str]") -> int:
    values = series.dropna().astype(str)  # type: ignore[attr-defined]
    return int((~values.isin(sorted(allowed))).sum())


def _bad_dates(series: object, form: str, **options: object) -> int:
    import pandas

    present = series.dropna().astype(str)  # type: ignore[attr-defined]
    parsed = pandas.to_datetime(present, format=form, errors="coerce", **options)
    return int(parsed.isna().sum())


def _bad_numbers(series: object) -> int:
    import pandas

    present = series.dropna()  # type: ignore[attr-defined]
    return int(pandas.to_numeric(present, errors="coerce").isna().sum())


def _strip(series: object, pattern: str) -> object:
    return series.dropna().astype(str).str.replace(pattern, "", regex=True)  # type: ignore[attr-defined]


def _wrong_offsets(series: object) -> int:
    wrong = 0
    for text in series.dropna().astype(str):  # type: ignore[attr-defined]
        try:
            local = datetime.datetime.strptime(text[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
        wrong += 0 if text[19:] in eastern_offsets(local) else 1
    return wrong


def _money(series: object) -> object:
    import pandas

    text = series.dropna().astype(str)  # type: ignore[attr-defined]
    negative = text.str.startswith("(")
    figures = pandas.to_numeric(text.str.replace(r"[$,()]", "", regex=True), errors="coerce")
    return figures.where(~negative, -figures)


def _flowsheet_numbers_bad(frame: object) -> int:
    import pandas

    rows = frame[frame["flo_row"] != "BP"]  # type: ignore[index]
    return int(pandas.to_numeric(rows["flo_value"], errors="coerce").isna().sum())


def _flowsheet_pressures_bad(frame: object) -> int:
    rows = frame[frame["flo_row"] == "BP"]  # type: ignore[index]
    return _bad_pattern(rows["flo_value"], r"\d+/\d+")


def _pressure_parts_bad(series: object) -> int:
    import pandas

    parts = series.dropna().astype(str).str.split("/", expand=True)  # type: ignore[attr-defined]
    if parts.shape[1] != 2:
        return int(len(parts))
    numbers = parts.apply(pandas.to_numeric, errors="coerce")
    return int(numbers.isna().any(axis=1).sum())


def _repeat_patients_missing(series: object) -> int:
    counts = series.dropna().value_counts()  # type: ignore[attr-defined]
    return 0 if int((counts > 1).sum()) else 1


def _repeat_shares(series: object) -> "tuple[float, float]":
    """The share of patients holding two rows or more, and three or more."""
    counts = series.dropna().value_counts()  # type: ignore[attr-defined]
    if not len(counts):
        return (0.0, 0.0)
    return (round(float((counts >= 2).mean()), 3), round(float((counts >= 3).mean()), 3))


def _share_has(series: object, pattern: str) -> float:
    """The share of the column's rows whose cell carries the pattern (a missing cell does not)."""
    cells = series.fillna("").astype(str)  # type: ignore[attr-defined]
    return round(float(cells.str.contains(pattern, regex=True).mean()), 3) if len(cells) else 0.0


def _spread(numbers: "list[float]") -> "tuple[float, float, float] | None":
    """The least, the middle and the greatest of the numbers read; None where none read."""
    if not numbers:
        return None
    ordered = sorted(numbers)
    middle = len(ordered) // 2
    median = ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2
    return (round(ordered[0], 6), round(median, 6), round(ordered[-1], 6))


def _range_of(series: object, pattern: str) -> "tuple[float, float, float] | None":
    """The spread of the number group `n` holds in the cells the pattern reads whole, a comma read as the point."""
    numbers: "list[float]" = []
    for text in series.dropna().astype(str):  # type: ignore[attr-defined]
        match = re.fullmatch(pattern, text)
        if match:
            numbers += [float(match.group("n").replace(",", "."))]
    return _spread(numbers)


def _money_range(series: object) -> "tuple[float, float, float] | None":
    return _spread([float(value) for value in _money(series).dropna()])  # type: ignore[attr-defined]


STATURE_FEET = r"(?P<f>\d)'(?P<i>\d{1,2})\""


def _inches(text: str) -> int:
    match = re.fullmatch(STATURE_FEET, text)
    assert match, text
    return 12 * int(match.group("f")) + int(match.group("i"))


def _feet(inches: int) -> str:
    return f"{inches // 12}'{inches % 12}\""


def _feet_range(series: object) -> "tuple[float, float, float] | None":
    """A stature written in feet and inches, read as inches."""
    inches: "list[float]" = []
    for text in series.dropna().astype(str):  # type: ignore[attr-defined]
        match = re.fullmatch(STATURE_FEET, text)
        if match:
            inches += [float(12 * int(match.group("f")) + int(match.group("i")))]
    return _spread(inches)


def _length_percentiles(series: object) -> "tuple[float, float, float] | None":
    """The 10th, 50th and 90th percentiles of the cells' lengths, in characters."""
    lengths = sorted(len(text) for text in series.dropna().astype(str))  # type: ignore[attr-defined]
    if not lengths:
        return None
    return tuple(float(lengths[min(len(lengths) - 1, int(share * len(lengths)))]) for share in (0.1, 0.5, 0.9))  # type: ignore[return-value]


def _serial_dates_bad(series: object) -> int:
    import pandas

    numbers = pandas.to_numeric(series.dropna(), errors="coerce")  # type: ignore[attr-defined]
    days = pandas.to_datetime(numbers, unit="D", origin="1899-12-30", errors="coerce")
    return int((days.isna() | (days.dt.year < 2000) | (days.dt.year > 2030)).sum())


def _mojibake(frame: object) -> int:
    bad = 0
    for name in frame.columns:  # type: ignore[attr-defined]
        values = frame[name].dropna().astype(str)  # type: ignore[index]
        bad += int(values.str.contains("Ã|Â|�", regex=True).sum())
    return bad


def _stray_returns(frame: object) -> int:
    bad = 0
    for name in frame.columns:  # type: ignore[attr-defined]
        values = frame[name].dropna().astype(str)  # type: ignore[index]
        bad += int(values.str.contains("\r", regex=False).sum())
    return bad


def _range_bounds_bad(series: object) -> int:
    """Reference ranges that do not split into exactly two numbers."""
    bad = 0
    for text in series.dropna().astype(str):  # type: ignore[attr-defined]
        parts = text.split("-")
        try:
            numbers = [float(part) for part in parts]
        except ValueError:
            numbers = []
        bad += 0 if len(parts) == 2 and len(numbers) == 2 else 1
    return bad


def _npi_bad(series: object) -> int:
    """NPIs whose last figure is not their Luhn check over the prefix 80840."""
    bad = 0
    for text in series.dropna().astype(str):  # type: ignore[attr-defined]
        whole = re.fullmatch(r"\d{10}", text) is not None
        bad += 0 if whole and _luhn_check("80840" + text[:9]) == int(text[9]) else 1
    return bad


def _births_outside(series: object) -> int:
    """Two-figure birth years read in the 1900s, as the person said they lie: outside 1930 to 1999 is bad."""
    import pandas

    days = pandas.to_datetime(series.dropna().astype(str), format="%d/%m/%y", errors="coerce")  # type: ignore[attr-defined]
    years = days.dt.year.where(days.dt.year < 2000, days.dt.year - 100)
    return int(((years < 1930) | (years > 1999)).sum())


def _list_items(series: object, mark: str) -> object:
    return series.dropna().astype(str).str.split(mark, regex=False).explode()  # type: ignore[attr-defined]


def _has(series: object, pattern: str) -> bool:
    return bool(series.dropna().astype(str).str.contains(pattern, regex=True).any())  # type: ignore[attr-defined]


def _share_on_the_minute(series: object) -> float:
    import pandas

    stamps = pandas.to_datetime(series.dropna(), format="%Y-%m-%dT%H:%M:%S", errors="coerce")  # type: ignore[attr-defined]
    return round(float((stamps.dt.second == 0).mean()), 3) if len(stamps) else 0.0


def spoil_scaled(column: str, pattern: str, factor: float) -> "Callable[[list[str], list[list[str]]], None]":
    """A spoil: every number the pattern's group `n` reads multiplied, written in its own places and point."""

    def how(value: str) -> str:
        match = re.fullmatch(pattern, value)
        if not match:
            return value
        number = match.group("n")
        comma = "," in number
        places = len(number.replace(",", ".").split(".")[1]) if "." in number.replace(",", ".") else 0
        scaled = f"{float(number.replace(',', '.')) * factor:.{places}f}"
        return value[: match.start("n")] + (scaled.replace(".", ",") if comma else scaled) + value[match.end("n"):]

    return spoil_every(column, how)


def spoil_money(column: str, factor: float) -> "Callable[[list[str], list[list[str]]], None]":
    """A spoil: every dollar amount multiplied, written as the source writes it."""

    def how(value: str) -> str:
        negative = value.startswith("(")
        figures = float(value.strip("()").lstrip("$").replace(",", "")) * factor
        return f"({_dollars(figures)})" if negative else _dollars(figures)

    return spoil_every(column, how)


def spoil_unique(column: str) -> "Callable[[list[str], list[list[str]]], None]":
    """A spoil: every row its own patient, so nobody repeats."""

    def change(header: "list[str]", rows: "list[list[str]]") -> None:
        place = header.index(column)
        for index in range(len(rows)):
            rows[index][place] = f"PT{2000000 + index:07d}"

    return change


def spoil_first_where(column: str, test: "Callable[[list[str], list[str]], bool]", value: str) -> "Callable[[list[str], list[list[str]]], None]":
    """A spoil: the first row that passes `test` gets `value` in the column."""

    def change(header: "list[str]", rows: "list[list[str]]") -> None:
        for row in rows:
            if test(header, row):
                row[header.index(column)] = value
                return
        raise AssertionError(f"no row to spoil in {column}")

    return change


def spoil_extra_column(header: "list[str]", rows: "list[list[str]]") -> None:
    header += ["extra"]
    for row in rows:
        row += [""]


def spoil_first_name(header: "list[str]", rows: "list[list[str]]") -> None:
    header[0] = "encounter_id"


def spoil_half_on_the_minute(header: "list[str]", rows: "list[list[str]]") -> None:
    place = header.index("ts")
    for index in range(0, len(rows), 2):
        rows[index][place] = rows[index][place][:17] + "00"


def spoil_npi_check(header: "list[str]", rows: "list[list[str]]") -> None:
    place = header.index("npi")
    text = rows[0][place]
    rows[0][place] = text[:9] + f"{(int(text[9]) + 1) % 10}"


PROC_PATTERN = r"\d{4}[0-9A-Z]"


@dataclasses.dataclass(frozen=True)
class Table:
    """One export of the catalogue: how it is built, what it holds, how it is read."""

    name: str
    suffix: str
    build: "Callable[[int, int], tuple[list[str], list[list[str]]]]"
    write: "Callable[[list[str], list[list[str]]], bytes]"
    kinds: "dict[str, tuple[str, ...]]"
    knows: "dict[str, str]"
    read: "Callable[[pathlib.Path], dict[str, object]]"
    checks: "tuple[Check, ...]"
    # What the person knows about the whole file, for the questions about
    # it: where the column names are and how the dates order day and month.
    facts: "tuple[str, ...]" = ("names", "month-first")


def _csv_reader(**options: object) -> "Callable[[pathlib.Path], dict[str, object]]":
    """The analyst's reads: the dtypes pandas infers, codes kept as text, the raw cells and bytes."""

    def read(path: pathlib.Path) -> "dict[str, object]":
        import pandas

        inferred = pandas.read_csv(path, **options)
        as_text = pandas.read_csv(path, dtype=str, keep_default_na=True, **options)
        raw = pandas.read_csv(path, dtype=str, keep_default_na=False, **options)
        return {"inferred": inferred, "text": as_text, "raw": raw, "bytes": path.read_bytes()}

    return read


def _excel_reader(path: pathlib.Path) -> "dict[str, object]":
    """The workbook's reads, through the suite's cross-check reader (`tests/crosscheck.py`).

    pandas opens an `.xlsx` through openpyxl, which is not a dependency
    and is absent from CI's `minimums` cell; `run_zoo` leaves the
    workbook out there, and a caller that reads one asks first.
    """
    import crosscheck

    inferred = crosscheck.read_excel_present(path)
    as_text = crosscheck.read_excel_present(path, dtype=str)
    raw = crosscheck.read_excel_present(path, dtype=str, keep_default_na=False)
    return {"inferred": inferred, "text": as_text, "raw": raw}


def _t(column: str) -> "Callable[[dict[str, object]], object]":
    return lambda frames: frames["text"][column]  # type: ignore[index]


def _i(column: str) -> "Callable[[dict[str, object]], object]":
    return lambda frames: frames["inferred"][column]  # type: ignore[index]


def _r(column: str) -> "Callable[[dict[str, object]], object]":
    return lambda frames: frames["raw"][column]  # type: ignore[index]


def _bad(
    kind: str,
    name: str,
    column: str,
    how: "Callable[[dict[str, object]], object]",
    spoil: "Callable[[list[str], list[list[str]]], None] | None" = None,
) -> Check:
    return Check(kind, name, "bad", how, column, spoil)


def _pattern(kind: str, name: str, column: str, pattern: str) -> Check:
    return _bad(kind, name, column, lambda f: _bad_pattern(_t(column)(f), pattern))


def _listed(kind: str, name: str, column: str, allowed: "set[str]") -> Check:
    return _bad(kind, name, column, lambda f: _bad_set(_t(column)(f), allowed))


def _dated(kind: str, name: str, column: str, form: str, **options: object) -> Check:
    return _bad(kind, name, column, lambda f: _bad_dates(_t(column)(f), form, **options))


def _present(
    kind: str, name: str, column: str, pattern: str,
    spoil: "Callable[[list[str], list[list[str]]], None]",
) -> "tuple[Check, Check]":
    """A shape the real holds, as two checks: present at all, and on its share of the rows."""
    return (
        Check(kind, name, "present", lambda f: _has(_t(column)(f), pattern), column, spoil),
        Check(kind, f"{name}, as a share", "share", lambda f: _share_has(_t(column)(f), pattern), column, spoil),
    )


def _repeats(kind: str, column: str = "patient_id") -> "tuple[Check, Check]":
    """Several rows a patient, as two checks: some patient repeats, and the shares that hold two and three rows."""
    return (
        _bad(
            kind, "some patient has several rows", column,
            lambda f: _repeat_patients_missing(_t(column)(f)), spoil_unique(column),
        ),
        Check(
            kind, "patients with two rows or more, and three or more, as shares", "share",
            lambda f: _repeat_shares(_t(column)(f)), column, spoil_at_most_two(column),
        ),
    )


def _ranged(
    kind: str, column: str, pattern: str, factor: float = 10.0, reader: "Callable[[object], object] | None" = None,
) -> Check:
    """The numbers a column holds past its unit or mark: the least, the middle and the greatest."""
    if reader is None:
        return Check(
            kind, f"the numbers of {column} keep their range", "range",
            lambda f: _range_of(_t(column)(f), pattern), column, spoil_scaled(column, pattern, factor),
        )
    read = reader
    return Check(
        kind, f"the numbers of {column} keep their range", "range",
        lambda f: read(_t(column)(f)), column, spoil_money(column, factor),
    )


def spoil_at_most_two(column: str) -> "Callable[[list[str], list[list[str]]], None]":
    """A spoil: every patient holds two rows at most."""

    def change(header: "list[str]", rows: "list[list[str]]") -> None:
        place = header.index(column)
        for index in range(len(rows)):
            rows[index][place] = f"PT{2000000 + index // 2:07d}"

    return change


def _levels(pool: "tuple[tuple[str, float], ...]") -> "set[str]":
    return {value for value, _weight in pool}


def _is_bp(header: "list[str]", row: "list[str]") -> bool:
    return row[header.index("flo_row")] == "BP"


def _not_bp(header: "list[str]", row: "list[str]") -> bool:
    return row[header.index("flo_row")] != "BP"


ICD10_PATTERN = r"[A-Z][0-9][0-9A-Z](\.[0-9A-Z]{1,4})?"

TABLES: "tuple[Table, ...]" = (
    Table(
        "patients", ".csv", patients,
        lambda header, rows: csv_bytes(header, rows),
        {
            "demographics": (
                "patient_id", "dob_iso", "dob_us", "dob_text", "age", "gender_code", "gender_word",
                "ancestry", "ethnicity", "zip5", "zip4",
            ),
            "utf8_accents": ("preferred_language", "birth_city"),
        },
        {"patient_id": "identifier", "zip5": "code", "zip4": "code", "dob_us": "month-first", "age": "measurement"},
        _csv_reader(),
        (
            _pattern("demographics", "record numbers match PT#######", "patient_id", r"PT\d{7}"),
            _dated("demographics", "dob_iso parses as %Y-%m-%d", "dob_iso", "%Y-%m-%d"),
            _dated("demographics", "dob_us parses as %m/%d/%Y", "dob_us", "%m/%d/%Y"),
            _dated("demographics", "dob_text parses as %d-%b-%Y", "dob_text", "%d-%b-%Y"),
            _pattern("demographics", "age is a whole number or 90+", "age", r"\d{1,2}|90\+"),
            _listed("demographics", "gender codes are M/F/U/X", "gender_code", {"M", "F", "U", "X"}),
            _listed("demographics", "gender words are Male/Female/Unknown", "gender_word", {"Male", "Female", "Unknown"}),
            _listed("demographics", "ancestry is a listed category", "ancestry", _levels(ANCESTRIES)),
            _listed("demographics", "ethnicity is a listed category", "ethnicity", _levels(ETHNICITIES)),
            _pattern("demographics", "zip5 is five figures", "zip5", r"\d{5}"),
            _pattern("demographics", "zip4 is ZIP+4", "zip4", r"\d{5}-\d{4}"),
            _listed("utf8_accents", "languages are listed ones", "preferred_language", _levels(LANGUAGES)),
            _listed("utf8_accents", "cities are listed ones", "birth_city", _levels(CITIES)),
            _bad("utf8_accents", "no cell reads as mojibake", "birth_city", lambda f: _mojibake(f["text"]),
                 spoil_cell("birth_city", "SÃ£o Paulo")),
        ),
    ),
    Table(
        "encounters", ".csv", encounters,
        lambda header, rows: csv_bytes(header, rows, newline="\r\n", mark=True),
        {
            "encounters": ("enc_id", "patient_id", "admit_ts", "discharge_ts", "stay_days", "department", "visit_type"),
            "byte_order_mark": (),
            "crlf_line_endings": (),
        },
        {"enc_id": "identifier", "patient_id": "identifier", "stay_days": "measurement"},
        _csv_reader(),
        (
            Check("byte_order_mark", "the first column is named enc_id", "same",
                  lambda f: list(f["inferred"].columns)[0], "", spoil_first_name),  # type: ignore[attr-defined]
            _bad("crlf_line_endings", "no cell carries a stray carriage return", "department",
                 lambda f: _stray_returns(f["text"]), spoil_cell("department", "Card\riology")),
            _pattern("encounters", "encounter ids match E#########", "enc_id", r"E\d{9}"),
            _pattern("encounters", "patients match PT#######", "patient_id", r"PT\d{7}"),
            *_repeats("encounters"),
            _dated("encounters", "admit_ts parses with its offset", "admit_ts", "%Y-%m-%d %H:%M:%S%z", utc=True),
            _dated("encounters", "discharge_ts parses with its offset", "discharge_ts", "%Y-%m-%d %H:%M:%S%z", utc=True),
            _bad("encounters", "admit_ts wears an offset in force on its date", "admit_ts",
                 lambda f: _wrong_offsets(_t("admit_ts")(f)), spoil_cell("admit_ts", "2024-07-01 10:00:00-05:00")),
            _bad("encounters", "discharge_ts wears an offset in force on its date", "discharge_ts",
                 lambda f: _wrong_offsets(_t("discharge_ts")(f)), spoil_cell("discharge_ts", "2024-01-15 10:00:00-04:00")),
            _bad("encounters", "length of stay is not negative", "stay_days",
                 lambda f: int((_i("stay_days")(f) < 0).sum()), spoil_cell("stay_days", "-1")),  # type: ignore[operator]
            _bad("encounters", "departments are listed ones, in either case", "department",
                 lambda f: _bad_set(_t("department")(f).str.title(), {"Cardiology", "Emergency", "Oncology", "Orthopedics", "Pediatrics", "Neurology", "Medicine"})),  # type: ignore[attr-defined]
            _listed("encounters", "visit types are listed ones", "visit_type", _levels(VISIT_TYPES)),
        ),
    ),
    Table(
        "diagnoses_procedures", ".csv", diagnoses_procedures,
        lambda header, rows: csv_bytes(header, rows),
        {
            "diagnoses": ("enc_id", "dx_seq", "icd10_dotted", "icd10_plain", "icd9", "snomed_id", "poa"),
            "procedures": ("proc_code", "proc_code_mod", "hcpcs", "icd10pcs"),
        },
        {
            "enc_id": "identifier", "icd10_dotted": "code", "icd10_plain": "code", "icd9": "code",
            "snomed_id": "code", "poa": "code", "proc_code": "code", "proc_code_mod": "code",
            "hcpcs": "code", "icd10pcs": "code",
        },
        _csv_reader(),
        (
            _pattern("diagnoses", "ICD-10-CM with the dot", "icd10_dotted", ICD10_PATTERN),
            _pattern("diagnoses", "ICD-10-CM without the dot", "icd10_plain", r"[A-Z][0-9][0-9A-Z][0-9A-Z]{0,4}"),
            _pattern("diagnoses", "ICD-9-CM", "icd9", r"V\d{2}(\.\d{1,2})?|E\d{3}(\.\d)?|\d{3}(\.\d{1,2})?"),
            _pattern("diagnoses", "SNOMED CT ids are 6 to 18 figures", "snomed_id", r"[1-9]\d{5,17}"),
            _listed("diagnoses", "present-on-admission flags", "poa", {"Y", "N", "U", "W", "1"}),
            _pattern("procedures", "level I procedure codes", "proc_code", PROC_PATTERN),
            _pattern("procedures", "procedure codes with a modifier", "proc_code_mod", PROC_PATTERN + r"(-[0-9A-Z]{2})?"),
            _pattern("procedures", "HCPCS level II", "hcpcs", r"[A-V]\d{4}"),
            _pattern("procedures", "ICD-10-PCS", "icd10pcs", r"[0-9A-HJ-NP-Z]{7}"),
        ),
    ),
    Table(
        "labs", ".csv", labs,
        lambda header, rows: csv_bytes(header, rows),
        {
            "labs": ("patient_id", "collected_at", "loinc", "result", "qualitative", "viral_load", "ref_range", "abnormal_flag"),
            "mixed_results": ("result_value",),
        },
        {
            "patient_id": "identifier", "loinc": "code", "result": "measurement", "viral_load": "measurement",
            "ref_range": "joined", "result_value": "measurement",
        },
        _csv_reader(),
        (
            *_repeats("labs"),
            _dated("labs", "collected_at parses as %Y-%m-%d %H:%M", "collected_at", "%Y-%m-%d %H:%M"),
            _pattern("labs", "LOINC codes", "loinc", r"\d{1,7}-\d"),
            _pattern("labs", "a value and its unit", "result", r"-?\d+(\.\d+)? (mmol/L|mg/dL|g/dL|%|10\*3/uL)"),
            _bad("labs", "the value read as a number", "result",
                 lambda f: _bad_numbers(_t("result")(f).str.split(" ").str[0])),  # type: ignore[attr-defined]
            _listed("labs", "POS/NEG results", "qualitative", {"POS", "NEG", "INDETERMINATE"}),
            _bad("labs", "censored values read past < and >", "viral_load",
                 lambda f: _bad_numbers(_strip(_t("viral_load")(f), r"^[<>]"))),
            _bad("labs", "reference ranges split into exactly two numbers", "ref_range",
                 lambda f: _range_bounds_bad(_t("ref_range")(f))),
            _listed("labs", "abnormal flags", "abnormal_flag", {"N", "H", "L", "HH", "LL"}),
            _ranged("labs", "result", r"(?P<n>-?\d+(\.\d+)?) \S+"),
            _ranged("labs", "viral_load", r"[<>]?(?P<n>\d+)", 1000.0),
            _ranged("mixed_results", "result_value", r"[<>]?(?P<n>\d+(\.\d+)?)"),
            _pattern("mixed_results", "a result is a number, a censored number or a word", "result_value",
                     r"[<>]?\d+(\.\d+)?|NEGATIVE|POSITIVE|SEE NOTE"),
            _bad("mixed_results", "the numbers read past < and >", "result_value",
                 lambda f: _bad_numbers(_strip(_t("result_value")(f)[~_t("result_value")(f).str.fullmatch(r"[A-Z ]+")], r"^[<>]"))),  # type: ignore[attr-defined]
            *_present("mixed_results", "some result is censored", "result_value", r"^[<>]",
                     spoil_every("result_value", lambda v: v.lstrip("<>"))),
            *_present("mixed_results", "some result is a word", "result_value", r"^[A-Z ]+$",
                     spoil_every("result_value", lambda v: "1.0" if v.replace(" ", "").isalpha() else v)),
        ),
    ),
    Table(
        "prescriptions", ".csv", prescriptions,
        lambda header, rows: csv_bytes(header, rows),
        {"medication_orders": ("order_id", "patient_id", "ndc_542", "ndc_11", "rxnorm", "dose", "route", "frequency")},
        {"order_id": "identifier", "patient_id": "identifier", "ndc_542": "code", "ndc_11": "code", "rxnorm": "code"},
        _csv_reader(),
        (
            _pattern("medication_orders", "NDC 5-4-2", "ndc_542", r"\d{5}-\d{4}-\d{2}"),
            _pattern("medication_orders", "NDC 11 figures", "ndc_11", r"\d{11}"),
            _pattern("medication_orders", "RxNorm ids", "rxnorm", r"\d{3,8}"),
            _pattern("medication_orders", "dose strings read", "dose", r"\d+(\.\d+)?(-\d+)? (mg|tabs?|units|puffs)"),
            _listed("medication_orders", "routes", "route", _levels(ROUTES)),
            _pattern("medication_orders", "frequencies", "frequency", r"(BID|TID|QID|QD|QHS|PRN|q\d+h)( PRN)?"),
        ),
    ),
    Table(
        "vitals", ".csv", vitals,
        lambda header, rows: csv_bytes(header, rows, delimiter=";"),
        {
            "vitals": ("patient_id", "taken_at", "bp", "temp", "spo2", "pulse", "stature", "weight"),
            "semicolon_decimal_comma": ("mass_index",),
        },
        {"patient_id": "identifier", "bp": "joined", "pulse": "measurement", "mass_index": "decimal_comma"},
        _csv_reader(sep=";", decimal=","),
        (
            Check("semicolon_decimal_comma", "the file splits into nine columns", "same",
                  lambda f: int(f["inferred"].shape[1]), "", spoil_extra_column),  # type: ignore[attr-defined]
            _bad("semicolon_decimal_comma", "the mass index reads as a number", "mass_index",
                 lambda f: _bad_numbers(_i("mass_index")(f))),
            *_repeats("vitals"),
            _dated("vitals", "taken_at parses", "taken_at", "%Y-%m-%d %H:%M"),
            _bad("vitals", "'120/80' splits into two numbers", "bp", lambda f: _pressure_parts_bad(_t("bp")(f))),
            _bad("vitals", "temperature with its unit", "temp",
                 lambda f: _bad_numbers(_strip(_t("temp")(f), " °C$").str.replace(",", "."))),  # type: ignore[attr-defined]
            _pattern("vitals", "oxygen saturation with %", "spo2", r"\d{2,3}%"),
            _pattern("vitals", "stature in cm", "stature", r"\d{2,3} cm"),
            _pattern("vitals", "weight in kg with a decimal comma", "weight", r"\d{2,3},\d kg"),
            _ranged("vitals", "stature", r"(?P<n>\d+) cm", 0.5),
            _ranged("vitals", "weight", r"(?P<n>\d+,\d) kg"),
            _ranged("vitals", "temp", r"(?P<n>\d+,\d) °C"),
            _ranged("vitals", "spo2", r"(?P<n>\d+)%", 0.5),
            _ranged("semicolon_decimal_comma", "mass_index", r"(?P<n>-?\d+(,\d+)?)"),
        ),
    ),
    Table(
        "flowsheet", ".csv", flowsheet,
        lambda header, rows: csv_bytes(header, rows),
        {"flowsheet_long": ("patient_id", "recorded_at", "flo_row", "flo_value")},
        {"patient_id": "identifier"},
        _csv_reader(),
        (
            *_repeats("flowsheet_long"),
            _dated("flowsheet_long", "recorded_at parses", "recorded_at", "%Y-%m-%dT%H:%M:%S"),
            _listed("flowsheet_long", "row names are listed ones", "flo_row", {"Pulse", "Resp", "SpO2", "Temp", "BP", "Pain Score"}),
            _bad("flowsheet_long", "BP rows hold '120/80' (read by row name)", "flo_value",
                 lambda f: _flowsheet_pressures_bad(f["text"]), spoil_first_where("flo_value", _is_bp, JUNK)),
            _bad("flowsheet_long", "other rows hold numbers (read by row name)", "flo_value",
                 lambda f: _flowsheet_numbers_bad(f["text"]), spoil_first_where("flo_value", _not_bp, JUNK)),
        ),
    ),
    Table(
        "redcap", ".csv", redcap,
        lambda header, rows: csv_bytes(header, rows),
        {"redcap": (
            "record_id", "redcap_event_name", "redcap_repeat_instrument", "redcap_repeat_instance",
            "redcap_data_access_group", "consent_date", "gender", "smoke___1", "smoke___2", "smoke___3",
            "cigs_per_day", "phq_1", "phq_2", "phq_3", "phq_total", "mass_index_calc", "baseline_complete",
            "ae_term",
        )},
        {"record_id": "identifier", "gender": "code"},
        _csv_reader(),
        (
            _pattern("redcap", "event names wear their arm", "redcap_event_name", r"[a-z0-9_]+_arm_\d+"),
            _listed("redcap", "repeat instruments are named ones", "redcap_repeat_instrument", {"adverse_events"}),
            _pattern("redcap", "repeat instances are whole numbers", "redcap_repeat_instance", r"\d+"),
            _listed("redcap", "data access groups", "redcap_data_access_group", {"site_a", "site_b", "site_c"}),
            _dated("redcap", "consent_date parses", "consent_date", "%Y-%m-%d"),
            _listed("redcap", "gender coded 1/2", "gender", {"1", "2"}),
            _bad("redcap", "checkboxes hold 0 or 1", "smoke___1",
                 lambda f: sum(_bad_set(_t(f"smoke___{k}")(f), {"0", "1"}) for k in (1, 2, 3))),
            _bad("redcap", "PHQ items 0 to 3", "phq_1",
                 lambda f: sum(_bad_set(_t(f"phq_{k}")(f), {"0", "1", "2", "3"}) for k in (1, 2, 3))),
            _pattern("redcap", "the calculated total is a whole number", "phq_total", r"\d+"),
            _listed("redcap", "form status 0/1/2", "baseline_complete", {"0", "1", "2"}),
        ),
    ),
    Table(
        "claims", ".csv", claims,
        lambda header, rows: csv_bytes(header, rows, encoding="latin-1"),
        {
            "claims": ("claim_id", "patient_id", "service_date", "billed", "adjustment", "payer_code", "drg", "revenue_code"),
            "latin1": ("facility",),
        },
        {
            "claim_id": "identifier", "patient_id": "identifier", "payer_code": "code", "drg": "code",
            "revenue_code": "code", "billed": "measurement", "adjustment": "measurement",
        },
        _csv_reader(encoding="latin-1"),
        (
            _listed("latin1", "facilities are listed ones", "facility", _levels(FACILITIES)),
            _bad("latin1", "no cell reads as mojibake", "facility", lambda f: _mojibake(f["text"]),
                 spoil_cell("facility", "ClÃnica Santa MarÃa")),
            _pattern("claims", "claim ids", "claim_id", r"CLM\d{9}"),
            *_repeats("claims"),
            _dated("claims", "service_date parses as %m/%d/%Y", "service_date", "%m/%d/%Y"),
            _bad("claims", "billed reads past $ and commas", "billed",
                 lambda f: int(_money(_t("billed")(f)).isna().sum())),  # type: ignore[attr-defined]
            _bad("claims", "adjustments read, parentheses negative", "adjustment",
                 lambda f: int(_money(_t("adjustment")(f)).isna().sum())),  # type: ignore[attr-defined]
            _listed("claims", "payer codes", "payer_code", _levels(PAYERS)),
            _ranged("claims", "billed", "", 10.0, _money_range),
            _ranged("claims", "adjustment", "", 10.0, _money_range),
            _pattern("claims", "DRG three figures", "drg", r"\d{3}"),
            _pattern("claims", "revenue codes keep the leading zero", "revenue_code", r"0\d{3}"),
        ),
    ),
    Table(
        "notes", ".csv", notes,
        lambda header, rows: csv_bytes(header, rows),
        {"clinical_notes": ("note_id", "enc_id", "note_type", "chief_complaint", "note_text")},
        {"note_id": "identifier", "enc_id": "identifier"},
        _csv_reader(),
        (
            _listed("clinical_notes", "note types", "note_type", _levels(NOTE_TYPES)),
            _bad("clinical_notes", "no empty note", "note_text",
                 lambda f: int(_t("note_text")(f).isna().sum()), spoil_cell("note_text", "")),  # type: ignore[attr-defined]
            *_present("clinical_notes", "some note runs over several lines", "note_text", "\n",
                     spoil_every("note_text", lambda v: v.replace("\n", " "))),
            *_present("clinical_notes", "some note keeps a de-identification token", "note_text", r"\[NAME\]|\[DATE\]|\*\*\*",
                     spoil_every("note_text", lambda v: re.sub(r"\[NAME\]|\[DATE\]|\[ID\]|\*\*\*", "x", v))),
            *_present("clinical_notes", "some complaint lists several, by commas", "chief_complaint", ",",
                     spoil_every("chief_complaint", lambda v: v.replace(",", ""))),
            *_present("clinical_notes", "some note quotes a phrase", "note_text", '"',
                      spoil_every("note_text", lambda v: v.replace('"', ""))),
            Check("clinical_notes", "note lengths at the 10th, 50th and 90th percentiles", "ratios",
                  lambda f: _length_percentiles(_t("note_text")(f)), "note_text",
                  spoil_every("note_text", lambda v: v.split("\n")[0][:20])),
        ),
    ),
    Table(
        "surveys", ".xlsx", surveys,
        survey_book,
        {
            "surveys_pro": ("respondent_id", "q1_word", "q2_score", "q3_score", "scale_total", "q4_status"),
            "excel_workbook": ("survey_date",),
        },
        {"respondent_id": "identifier", "q2_score": "measurement", "q3_score": "measurement", "scale_total": "measurement"},
        _excel_reader,
        (
            Check("excel_workbook", "survey_date reads as dates", "same",
                  lambda f: str(_i("survey_date")(f).dtype), "survey_date"),  # type: ignore[attr-defined]
            _listed("surveys_pro", "Likert words", "q1_word", _levels(LIKERT)),
            _bad("surveys_pro", "scores 1 to 5 or -99", "q2_score",
                 lambda f: sum(_bad_set(_i(c)(f).astype("Int64").astype(str), {"1", "2", "3", "4", "5", "-99"}) for c in ("q2_score", "q3_score")),  # type: ignore[attr-defined]
                 spoil_cell("q2_score", "7")),
            _bad("surveys_pro", "totals 2 to 10 or 999", "scale_total",
                 lambda f: _bad_set(_i("scale_total")(f).astype("Int64").astype(str), {f"{k}" for k in range(2, 11)} | {"999"}),  # type: ignore[attr-defined]
                 spoil_cell("scale_total", "11")),
            _bad("surveys_pro", "status words with NA and Not asked", "q4_status",
                 lambda f: _bad_set(_t("q4_status")(f).fillna("NA"), {"Yes", "No", "NA", "Not asked"})),  # type: ignore[attr-defined]
        ),
    ),
    Table(
        "wearables", ".csv", wearables,
        lambda header, rows: csv_bytes(header, rows),
        {"wearables": ("device_id", "ts", "steps", "heart_rate", "activity")},
        {"device_id": "identifier", "steps": "measurement", "heart_rate": "measurement"},
        _csv_reader(),
        (
            _dated("wearables", "ts parses to the second", "ts", "%Y-%m-%dT%H:%M:%S"),
            Check("wearables", "stamps on the whole minute, as a share", "share",
                  lambda f: _share_on_the_minute(_t("ts")(f)), "ts", spoil_half_on_the_minute),
            _bad("wearables", "steps are not negative", "steps",
                 lambda f: int((_i("steps")(f) < 0).sum()), spoil_cell("steps", "-1")),  # type: ignore[operator]
            _listed("wearables", "activity levels", "activity", {"sedentary", "light", "moderate", "vigorous"}),
        ),
    ),
    Table(
        "genomics", ".csv", genomics,
        lambda header, rows: csv_bytes(header, rows),
        {
            "genomics": ("sample_id", "gene", "hgvs_c", "hgvs_p", "allele_freq", "zygosity", "classification"),
            "genomic_ids": ("omim", "hgnc_id", "clinvar_id", "ga4gh_id"),
        },
        {
            "sample_id": "identifier", "gene": "code", "hgvs_c": "code", "hgvs_p": "code", "allele_freq": "measurement",
            "omim": "code", "hgnc_id": "code", "clinvar_id": "code", "ga4gh_id": "code",
        },
        _csv_reader(),
        (
            _pattern("genomics", "gene symbols", "gene", r"[A-Z][A-Z0-9]*(-[A-Z0-9]+)?"),
            _pattern("genomics", "HGVS c. strings", "hgvs_c", r"c\.-?\d+(_\d+)?([ACGT]>[ACGT]|del[ACGT]*|dup[ACGT]*|ins[ACGT]+)"),
            _pattern("genomics", "HGVS p. strings", "hgvs_p", r"p\.([A-Z][a-z]{2}\d+([A-Z][a-z]{2}|del|fs)|=)"),
            _bad("genomics", "allele frequencies between 0 and 1", "allele_freq",
                 lambda f: int(((_i("allele_freq")(f) < 0) | (_i("allele_freq")(f) > 1)).sum()),  # type: ignore[operator]
                 spoil_cell("allele_freq", "1.5")),
            _listed("genomics", "clinical significance", "classification", _levels(CLASSES)),
            _pattern("genomic_ids", "OMIM numbers", "omim", r"[1-6]\d{5}"),
            _pattern("genomic_ids", "HGNC ids", "hgnc_id", r"HGNC:\d{1,5}"),
            _pattern("genomic_ids", "ClinVar variation ids", "clinvar_id", r"VCV\d{9}"),
            _pattern("genomic_ids", "GA4GH VRS ids", "ga4gh_id", r"ga4gh:VA\.[A-Za-z0-9_-]{32}"),
        ),
    ),
    Table(
        "imaging", ".csv", imaging,
        lambda header, rows: csv_bytes(header, rows),
        {
            "imaging": ("accession", "patient_id", "modality", "body_part", "series_count"),
            "dicom_metadata": ("study_date", "study_time", "study_uid"),
        },
        {"accession": "identifier", "patient_id": "identifier", "modality": "code", "study_uid": "identifier"},
        _csv_reader(),
        (
            _pattern("imaging", "accession numbers", "accession", r"ACC\d{8}"),
            _listed("imaging", "DICOM modality codes", "modality", _levels(MODALITIES)),
            _listed("imaging", "body parts", "body_part", _levels(BODY_PARTS)),
            _pattern("imaging", "series counts are whole numbers", "series_count", r"\d+"),
            _dated("dicom_metadata", "DA dates parse as %Y%m%d", "study_date", "%Y%m%d"),
            _dated("dicom_metadata", "TM times parse as %H%M%S.%f", "study_time", "%H%M%S.%f"),
            _pattern("dicom_metadata", "UIDs are dotted figures", "study_uid", r"[0-9]+(\.[0-9]+)+"),
        ),
    ),
    Table(
        "perioperative", ".csv", perioperative,
        lambda header, rows: csv_bytes(header, rows),
        {
            "perioperative": ("surgery_id", "patient_id", "case_duration", "phys_status", "or_room"),
            "clock_times": ("in_room", "anes_start", "incision_time"),
            "excel_serial_dates": ("case_date_serial",),
        },
        {"surgery_id": "identifier", "patient_id": "identifier", "case_date_serial": "excel-1900", "incision_time": "twelve-hour"},
        _csv_reader(),
        (
            _bad("excel_serial_dates", "serial dates read from 1899-12-30", "case_date_serial",
                 lambda f: _serial_dates_bad(_t("case_date_serial")(f))),
            _dated("clock_times", "in_room parses as %H:%M", "in_room", "%H:%M"),
            _dated("clock_times", "anes_start parses as %H:%M:%S", "anes_start", "%H:%M:%S"),
            _dated("clock_times", "incision_time parses as %I:%M %p", "incision_time", "%I:%M %p"),
            _pattern("perioperative", "surgery ids", "surgery_id", r"SRG\d{6}"),
            _pattern("perioperative", "durations as HH:MM", "case_duration", r"\d{2}:[0-5]\d"),
            _pattern("perioperative", "physical status with its emergency mark", "phys_status", r"(I|II|III|IV|V|VI)( E)?"),
            _pattern("perioperative", "rooms", "or_room", r"OR \d{1,2}"),
        ),
    ),
    Table(
        "problem_list", ".csv", problem_list,
        lambda header, rows: csv_bytes(header, rows),
        {"multi_value_cells": ("enc_id", "dx_list", "allergies")},
        {"enc_id": "identifier", "dx_list": "code"},
        _csv_reader(),
        (
            _bad("multi_value_cells", "every listed code is ICD-10-CM", "dx_list",
                 lambda f: _bad_pattern(_list_items(_t("dx_list")(f), ";"), ICD10_PATTERN)),
            *_present("multi_value_cells", "some cell lists several codes", "dx_list", ";",
                     spoil_every("dx_list", lambda v: v.split(";")[0])),
            _bad("multi_value_cells", "allergies are listed words", "allergies",
                 lambda f: _bad_set(_list_items(_t("allergies")(f), "|"), set(ALLERGENS) | {"NKDA"})),
            *_present("multi_value_cells", "some cell lists several allergies", "allergies", r"\|",
                     spoil_every("allergies", lambda v: v.split("|")[0])),
        ),
    ),
    Table(
        "tumor_registry", ".csv", tumor_registry,
        lambda header, rows: csv_bytes(header, rows),
        {
            "tumor_registry": ("tumor_id", "morphology", "topography", "tnm", "stage"),
            "partial_dates": ("dx_date", "first_treatment_month"),
        },
        {"tumor_id": "identifier", "morphology": "code", "topography": "code", "tnm": "code", "stage": "code"},
        _csv_reader(),
        (
            _pattern("partial_dates", "dates to the year, the month or the day", "dx_date", r"\d{4}|\d\d/\d{4}|\d{4}-\d\d-\d\d"),
            *_present("partial_dates", "some date is known to the year only", "dx_date", r"^\d{4}$",
                     spoil_every("dx_date", lambda v: f"{v}-07-01" if len(v) == 4 else v)),
            *_present("partial_dates", "some date is known to the month only", "dx_date", r"^\d\d/\d{4}$",
                     spoil_every("dx_date", lambda v: f"{v[3:]}-{v[:2]}-15" if "/" in v else v)),
            _dated("partial_dates", "first_treatment_month parses as %Y-%m", "first_treatment_month", "%Y-%m"),
            _pattern("tumor_registry", "ICD-O-3 morphology", "morphology", r"\d{4}/[0-9]"),
            _pattern("tumor_registry", "ICD-O-3 topography", "topography", r"C\d\d\.\d"),
            _pattern("tumor_registry", "TNM", "tnm", r"T[0-4]N[0-3]M[01]"),
            _listed("tumor_registry", "stage", "stage", _levels(STAGES)),
        ),
    ),
    Table(
        "us_vitals", ".csv", us_vitals,
        lambda header, rows: csv_bytes(header, rows),
        {"us_unit_vitals": ("patient_id", "stature", "weight", "temp_f")},
        {"patient_id": "identifier", "weight": "measurement", "temp_f": "measurement"},
        _csv_reader(),
        (
            *_repeats("us_unit_vitals"),
            _pattern("us_unit_vitals", "stature in feet and inches", "stature", r"\d'\d{1,2}\""),
            _pattern("us_unit_vitals", "weight in lb", "weight", r"\d{2,3} lb"),
            _pattern("us_unit_vitals", "temperature in F", "temp_f", r"\d{2,3}\.\d F"),
            Check("us_unit_vitals", "the numbers of stature keep their range", "range",
                  lambda f: _feet_range(_t("stature")(f)), "stature",
                  spoil_every("stature", lambda v: _feet(_inches(v) // 2))),
            _ranged("us_unit_vitals", "weight", r"(?P<n>\d+) lb", 0.1),
            _ranged("us_unit_vitals", "temp_f", r"(?P<n>\d+\.\d) F", 2.0),
        ),
    ),
    Table(
        "sql_server", ".csv", sql_server,
        lambda header, rows: csv_bytes(header, rows),
        {"sql_server_export": ("record_no", "created_dttm", "death_date", "is_active", "middle_initial")},
        {"record_no": "identifier"},
        _csv_reader(),
        (
            _pattern("sql_server_export", "record numbers nine figures with their leading zeros", "record_no", r"\d{9}"),
            _dated("sql_server_export", "created_dttm with milliseconds", "created_dttm", "%Y-%m-%d %H:%M:%S.%f"),
            _bad("sql_server_export", "death_date ISO or the literal NULL", "death_date",
                 lambda f: _bad_pattern(_r("death_date")(f), r"\d{4}-\d\d-\d\d|NULL")),
            _bad("sql_server_export", "middle_initial A/B/C or the literal NULL", "middle_initial",
                 lambda f: _bad_pattern(_r("middle_initial")(f), r"[ABC]|NULL")),
            _listed("sql_server_export", "is_active 0/1", "is_active", {"0", "1"}),
        ),
    ),
    Table(
        "microbiology", ".csv", microbiology,
        lambda header, rows: csv_bytes(header, rows),
        {"microbiology": ("isolate_id", "organism", "antibiotic", "mic", "interp")},
        {"isolate_id": "identifier", "mic": "measurement"},
        _csv_reader(),
        (
            _bad("microbiology", "MIC read past <= and >=", "mic", lambda f: _bad_numbers(_strip(_t("mic")(f), r"^(<=|>=)"))),
            _pattern("microbiology", "MIC comparators", "mic", r"(<=|>=)?\d+(\.\d+)?"),
            _listed("microbiology", "S/I/R", "interp", {"S", "I", "R"}),
            _ranged("microbiology", "mic", r"(<=|>=)?(?P<n>\d+(\.\d+)?)"),
            _listed("microbiology", "organisms", "organism", _levels(ORGANISMS)),
            _listed("microbiology", "antibiotics", "antibiotic", _levels(ANTIBIOTICS)),
        ),
    ),
    Table(
        "immunizations", ".csv", immunizations,
        lambda header, rows: csv_bytes(header, rows),
        {"immunizations_providers": ("patient_id", "cvx", "mvx", "npi", "udi", "dose_number")},
        {"patient_id": "identifier", "cvx": "code", "mvx": "code", "npi": "code", "udi": "code"},
        _csv_reader(),
        (
            _pattern("immunizations_providers", "CVX two or three figures", "cvx", r"\d{2,3}"),
            *_present("immunizations_providers", "some CVX keeps its leading zero", "cvx", r"^0",
                     spoil_every("cvx", lambda v: v.lstrip("0") or "0")),
            _pattern("immunizations_providers", "MVX three letters", "mvx", r"[A-Z]{3}"),
            _bad("immunizations_providers", "NPIs pass their Luhn check", "npi", lambda f: _npi_bad(_t("npi")(f)),
                 spoil_npi_check),
            _pattern("immunizations_providers", "UDI with its application identifiers", "udi",
                     r"\(01\)\d{14}\(17\)\d{6}\(10\)[A-Z0-9]+"),
        ),
    ),
    Table(
        "risk_adjustment", ".csv", risk_adjustment,
        lambda header, rows: csv_bytes(header, rows),
        {"risk_and_comorbidity_codes": ("member_id", "cms_hcc", "apc", "cdps", "charlson", "elixhauser", "clinical_class")},
        {
            "member_id": "identifier", "cms_hcc": "code", "apc": "code", "cdps": "code", "elixhauser": "code",
            "clinical_class": "code", "charlson": "measurement",
        },
        _csv_reader(),
        (
            _pattern("risk_and_comorbidity_codes", "CMS-HCC categories", "cms_hcc", r"HCC\d{1,3}"),
            _pattern("risk_and_comorbidity_codes", "APC four figures", "apc", r"\d{4}"),
            _pattern("risk_and_comorbidity_codes", "CDPS category and level", "cdps", r"[A-Z]{2,3}-(L|M|H|VH)"),
            _listed("risk_and_comorbidity_codes", "Charlson index 0 to 12", "charlson", {f"{k}" for k in range(13)}),
            _listed("risk_and_comorbidity_codes", "Elixhauser groups", "elixhauser", _levels(ELIXHAUSER)),
            _pattern("risk_and_comorbidity_codes", "clinical classes", "clinical_class", r"\d{1,3}"),
        ),
    ),
    Table(
        "edge_columns", ".csv", edge_columns,
        lambda header, rows: csv_bytes(header, rows),
        {"empty_and_constant_columns": ("patient_id", "middle_name", "facility", "age_years")},
        {"patient_id": "identifier", "age_years": "measurement"},
        _csv_reader(),
        (
            Check("empty_and_constant_columns", "middle_name is blank throughout", "same",
                  lambda f: int(_t("middle_name")(f).notna().sum()), "middle_name"),  # type: ignore[attr-defined]
            Check("empty_and_constant_columns", "facility never changes", "same",
                  lambda f: sorted(set(_t("facility")(f).dropna())), "facility"),  # type: ignore[attr-defined]
        ),
    ),
    Table(
        "titled_report", ".csv", titled_report,
        lambda header, rows: TITLE_LINES.encode("utf-8") + csv_bytes(header, rows),
        {"title_rows_above_header": ("report_ref", "ward", "admitted", "went_home")},
        {"report_ref": "identifier"},
        _csv_reader(skiprows=2),
        (
            Check("title_rows_above_header", "under its two title lines the header names report_ref first", "same",
                  lambda f: list(f["inferred"].columns)[0], "", spoil_first_name),  # type: ignore[attr-defined]
            _pattern("title_rows_above_header", "report references", "report_ref", r"RPT\d{6}"),
            _listed("title_rows_above_header", "wards", "ward", _levels(WARDS)),
            _dated("title_rows_above_header", "admitted parses as %Y-%m-%d", "admitted", "%Y-%m-%d"),
            _dated("title_rows_above_header", "went_home parses as %Y-%m-%d", "went_home", "%Y-%m-%d"),
        ),
    ),
    Table(
        "registry_extract", ".csv", registry_extract,
        lambda header, rows: csv_bytes(header, rows),
        {
            "day_first_dates": ("case_ref", "referral_date", "seen_date"),
            "two_digit_years": ("op_date", "dob_short"),
            "true_false_columns": ("on_waiting_list", "consented"),
        },
        {"case_ref": "identifier", "op_date": "1969-2068", "dob_short": "1900-1999"},
        _csv_reader(),
        (
            _pattern("day_first_dates", "case references", "case_ref", r"CR-\d{6}"),
            _dated("day_first_dates", "referral_date parses as %d/%m/%Y", "referral_date", "%d/%m/%Y"),
            _dated("day_first_dates", "seen_date parses as %d.%m.%Y", "seen_date", "%d.%m.%Y"),
            _dated("two_digit_years", "op_date parses as %d-%b-%y", "op_date", "%d-%b-%y"),
            _dated("two_digit_years", "dob_short parses as %d/%m/%y", "dob_short", "%d/%m/%y"),
            Check("two_digit_years", "birth years read into the 1900s fall from 1930 to 1999", "bad",
                  lambda f: _births_outside(_t("dob_short")(f)), "dob_short", spoil_cell("dob_short", "01/01/05")),
            _listed("true_false_columns", "on_waiting_list TRUE or FALSE", "on_waiting_list", {"TRUE", "FALSE"}),
            _listed("true_false_columns", "consented true or false", "consented", {"true", "false"}),
        ),
        facts=("names", "day-first"),
    ),
)


def table_named(name: str) -> Table:
    """The catalogue table of that name."""
    for table in TABLES:
        if table.name == name:
            return table
    raise KeyError(name)


def kind_of(table: Table, column: str) -> str:
    """The kind a column of a table serves."""
    for kind, columns in table.kinds.items():
        if column in columns:
            return kind
    raise KeyError(f"{table.name}.{column}")


def write_table(table: Table, folder: pathlib.Path, n: int, seed: int) -> pathlib.Path:
    """Build one table from its seed and write it; the same seed and size give the same bytes."""
    header, rows = table.build(n, seed)
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f"{table.name}{table.suffix}"
    target.write_bytes(table.write(header, rows))
    return target


# -- the analyst, run on both files ----------------------------------------


def _file_kind(table: Table, *preferred: str) -> str:
    """The kind a file-level fact of a table serves: a named file kind, or the table's first."""
    for kind in preferred:
        if kind in table.kinds:
            return kind
    return next(iter(table.kinds))


def generic_mode(table: Table, name: str) -> "tuple[str, str] | None":
    """(kind, mode) of a generic check's name, or None for a table's own check."""
    columns = (
        ("dtype ", "same"), ("missing spellings ", "spellings"), ("missing ", "bad"), ("shapes ", "shapes"),
        ("forms ", "forms"), ("levels ", "levels"), ("stand-ins ", "bad"), ("codes ", "codes"),
    )
    for prefix, mode in columns:
        if name.startswith(prefix):
            return kind_of(table, name[len(prefix):]), mode
    if name == "rows read":
        return _file_kind(table), "same"
    if name == "file: byte-order mark":
        return _file_kind(table, "byte_order_mark"), "same"
    if name == "file: line endings":
        return _file_kind(table, "crlf_line_endings"), "same"
    if name == "file: decodes as UTF-8":
        return _file_kind(table, "latin1", "utf8_accents"), "same"
    return None


def _line_endings(data: bytes) -> str:
    feeds = data.count(b"\n")
    returns = data.count(b"\r\n")
    if not feeds:
        return "none"
    return "CRLF" if returns == feeds else "LF" if returns == 0 else "mixed"


def _decodes(data: bytes) -> bool:
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def _shapes(series: object) -> "dict[str, int] | None":
    """Each shape the column's text takes, with its count; None for free text."""
    counts: "dict[str, int]" = {}
    for text in series.dropna().astype(str):  # type: ignore[attr-defined]
        shape = signature(text)
        counts[shape] = counts.get(shape, 0) + 1
        if len(counts) > SHAPED_AT_MOST:
            return None
    return counts


def _forms(series: object) -> "dict[str, int] | None":
    """Each form the column's text takes character by character, with its count; None past SHAPED_AT_MOST."""
    counts: "dict[str, int]" = {}
    for text in series.dropna().astype(str):  # type: ignore[attr-defined]
        shape = form(text)
        counts[shape] = counts.get(shape, 0) + 1
        if len(counts) > SHAPED_AT_MOST:
            return None
    return counts


def _levels_of(series: object) -> "dict[str, int] | None":
    """Each value a column of few values writes, with its count; None for a column of many."""
    counts: "dict[str, int]" = {}
    for text in series.dropna().astype(str):  # type: ignore[attr-defined]
        counts[text] = counts.get(text, 0) + 1
        if len(counts) > SHAPED_AT_MOST:
            return None
    return counts


def _census(cells: "object") -> "dict[str, int]":
    """Each value, with the number of cells that hold it."""
    counts: "dict[str, int]" = {}
    for text in cells:  # type: ignore[attr-defined]
        counts[text] = counts.get(text, 0) + 1
    return counts


def _generic(frames: "dict[str, object]", codes: "tuple[str, ...]" = ()) -> "dict[str, object]":
    """The checks every column and every file takes, by name; `codes` names the columns answered `code`."""
    inferred = frames["inferred"]
    text = frames["text"]
    raw = frames["raw"]
    found: "dict[str, object]" = {"rows read": int(len(inferred))}  # type: ignore[arg-type]
    for column in inferred.columns:  # type: ignore[attr-defined]
        found[f"dtype {column}"] = str(inferred[column].dtype)  # type: ignore[index]
        found[f"missing {column}"] = int(text[column].isna().sum())  # type: ignore[index]
        cells = raw[column].astype(str)  # type: ignore[index]
        found[f"missing spellings {column}"] = _census(cells[cells.isin(sorted(MISSING_SPELLINGS))])
        present = text[column].dropna().astype(str)  # type: ignore[index]
        found[f"levels {column}"] = _levels_of(present)
        found[f"stand-ins {column}"] = int(present.str.fullmatch(STAND_IN).sum())
        if column in codes:
            found[f"codes {column}"] = _census(present)
        if str(inferred[column].dtype) in TEXT_DTYPES:  # type: ignore[index]
            found[f"shapes {column}"] = _shapes(text[column])  # type: ignore[index]
            found[f"forms {column}"] = _forms(text[column])  # type: ignore[index]
    data = frames.get("bytes")
    if isinstance(data, bytes):
        found["file: byte-order mark"] = data.startswith(BYTE_ORDER_MARK)
        found["file: line endings"] = _line_endings(data)
        found["file: decodes as UTF-8"] = _decodes(data)
    return found


def analyse(table: Table, path: pathlib.Path) -> "dict[str, tuple[str, object]]":
    """Run a table's analyst script on one file: per check, ('ok', value) or ('error', why).

    The read is one step of its own; when it fails, every check fails
    with it. The generic checks (`generic_mode`) run on every column and
    file beside the table's own.
    """
    out: "dict[str, tuple[str, object]]" = {}
    try:
        frames = table.read(path)
    except Exception as failure:  # noqa: BLE001 -- what the analyst would have seen
        out["read"] = ("error", f"{type(failure).__name__}: {failure}"[:200])
        return out
    out["read"] = ("ok", True)
    codes = tuple(
        column for column, answer in table.knows.items() if answer == "code" and column not in NOT_A_VOCABULARY
    )
    for name, value in _generic(frames, codes).items():
        out[name] = ("ok", value)
    for check in table.checks:
        try:
            out[check.name] = ("ok", check.run(frames))
        except Exception as failure:  # noqa: BLE001 -- what the analyst would have seen
            out[check.name] = ("error", f"{type(failure).__name__}: {failure}"[:200])
    return out


def _mode_of(table: Table, name: str) -> "tuple[str, str]":
    generic = generic_mode(table, name)
    if generic is not None:
        return generic
    for check in table.checks:
        if check.name == name:
            return check.kind, check.mode
    raise KeyError(f"{table.name}: no check named {name!r}")


def real_faults(table: Table, real: "dict[str, tuple[str, object]]") -> "list[str]":
    """The analyst's checks that do not hold on the REAL table: the script's faults, never the twin's.

    A check that raises, a bad count above nought, or a shape the real
    table lacks would disable its own comparison, so each is named here.
    """
    if real.get("read", ("error", ""))[0] != "ok":
        return ["read"]
    faults: "list[str]" = []
    for name in sorted(real):
        if name == "read":
            continue
        status, value = real[name]
        _kind, mode = _mode_of(table, name)
        if status != "ok":
            faults += [name]
        elif mode == "bad" and not name.startswith("missing ") and value != 0:
            faults += [name]
        elif mode == "present" and not value:
            faults += [name]
        elif mode in ("range", "ratios") and value is None:
            faults += [name]
    return faults


def _shape_failure(wanted: object, value: object) -> str:
    if wanted is None:
        return ""
    if value is None:
        return f"the twin writes more than {SHAPED_AT_MOST} shapes"
    real_shapes = dict(wanted)  # type: ignore[call-overload]
    twin_shapes = dict(value)  # type: ignore[call-overload]
    invented = sorted(set(twin_shapes) - set(real_shapes))
    lost = sorted(shape for shape, count in real_shapes.items() if count >= FLOOR and shape not in twin_shapes)
    said = []
    if invented:
        said += [f"shapes the real never wrote {invented[:4]}"]
    if lost:
        said += [f"shapes {FLOOR}+ real cells hold, absent {lost[:4]}"]
    return "; ".join(said)


def _form_failure(wanted: object, value: object) -> str:
    """Forms the real never wrote on FLOOR or more twin cells in all, and forms FLOOR or more real cells hold, lost.

    A lone value past the real's widest -- '$9.99' below the real's least
    amount -- is a new form on a cell or two; a spelling the twin chose
    (a date unpadded, a month in capitals) is a new form on many.
    """
    if wanted is None:
        return ""
    if value is None:
        return f"the twin writes more than {SHAPED_AT_MOST} forms"
    real_forms = dict(wanted)  # type: ignore[call-overload]
    twin_forms = dict(value)  # type: ignore[call-overload]
    invented = sorted(set(twin_forms) - set(real_forms))
    lost = sorted(shape for shape, count in real_forms.items() if count >= FLOOR and shape not in twin_forms)
    said = []
    if sum(twin_forms[shape] for shape in invented) >= FLOOR:
        said += [f"forms the real never wrote {invented[:4]}"]
    if lost:
        said += [f"forms {FLOOR}+ real cells hold, absent {lost[:4]}"]
    return "; ".join(said)


def _spelling_failure(wanted: object, value: object, real_rows: int, twin_rows: int) -> str:
    """Spellings of missing the real never writes, ones FLOOR or more real cells write lost, or shares moved."""
    real = dict(wanted)  # type: ignore[call-overload]
    twin = dict(value)  # type: ignore[call-overload]
    said = []
    invented = sorted(set(twin) - set(real))
    if invented:
        said += [f"the twin writes missing as {invented}, the real never does"]
    lost = sorted(spelling for spelling, count in real.items() if count >= FLOOR and spelling not in twin)
    if lost:
        said += [f"spellings {FLOOR}+ real cells write, absent {lost}"]
    moved = sorted(
        spelling for spelling in set(real) & set(twin)
        if abs(twin[spelling] / max(twin_rows, 1) - real[spelling] / max(real_rows, 1)) > SHARE_TOLERANCE
    )
    if moved:
        said += [f"shares moved by more than {SHARE_TOLERANCE}: {moved}"]
    return "; ".join(said)


def _share_failure(wanted: object, value: object) -> bool:
    """A share, or each of several, more than SHARE_TOLERANCE from the real's."""
    real = wanted if isinstance(wanted, (tuple, list)) else (wanted,)
    twin = value if isinstance(value, (tuple, list)) else (value,)
    return len(real) != len(twin) or any(
        abs(float(mine) - float(theirs)) > SHARE_TOLERANCE for mine, theirs in zip(twin, real)
    )


def _range_failure(wanted: object, value: object) -> str:
    """The twin's middle more than RANGE_TOLERANCE from the real's, or an end outside the real's range widened."""
    if wanted is None:
        return ""
    if value is None:
        return "the twin holds no number in the column's form"
    low, middle, high = wanted  # type: ignore[misc]
    twin_low, twin_middle, twin_high = value  # type: ignore[misc]
    width = high - low
    slack = RANGE_TOLERANCE * width
    said = []
    if abs(twin_middle - middle) > max(RANGE_TOLERANCE * abs(middle), 0.01 * width):
        said += [f"middle {twin_middle} against the real's {middle}"]
    if twin_low < low - slack or twin_high > high + slack:
        said += [f"range {twin_low} to {twin_high} against the real's {low} to {high}"]
    return "; ".join(said)


def _ratio_failure(wanted: object, value: object) -> str:
    """A percentile of the twin more than LENGTH_TOLERANCE from the real's, as a ratio."""
    if wanted is None:
        return ""
    if value is None:
        return "the twin holds no cell"
    off = [
        f"{mine} against {theirs}" for mine, theirs in zip(value, wanted)  # type: ignore[call-overload]
        if abs(float(mine) / max(float(theirs), 1.0) - 1.0) > LENGTH_TOLERANCE
    ]
    return f"percentiles off by more than {LENGTH_TOLERANCE:.0%}: {off}" if off else ""


def _unseen_codes(wanted: object, value: object) -> int:
    """The twin's cells holding a value the real never writes."""
    real = dict(wanted)  # type: ignore[call-overload]
    return sum(count for code, count in dict(value).items() if code not in real)  # type: ignore[call-overload]


def _lost_levels(wanted: object, value: object) -> "list[str]":
    """The values the real column writes in FLOOR cells or more that the twin never writes."""
    if wanted is None:
        return []
    if value is None:
        return [f"(the twin writes more than {SHAPED_AT_MOST} values)"]
    twin = dict(value)  # type: ignore[call-overload]
    return sorted(level for level, count in dict(wanted).items() if count >= FLOOR and level not in twin)  # type: ignore[call-overload]


def analyst_failures(
    table: Table, real: "dict[str, tuple[str, object]]", twin: "dict[str, tuple[str, object]]"
) -> "list[tuple[str, str, str]]":
    """Per failing check of the twin: (kind, check, what went wrong)."""
    failures: "list[tuple[str, str, str]]" = []
    if twin.get("read", ("error", ""))[0] != "ok":
        for kind in sorted(table.kinds):
            failures += [(kind, "read", f"the twin does not read: {twin['read'][1]}")]
        return failures
    real_rows = int(real.get("rows read", ("ok", 0))[1])  # type: ignore[call-overload]
    twin_rows = int(twin.get("rows read", ("ok", 0))[1])  # type: ignore[call-overload]
    for name in sorted(real):
        if name == "read" or real[name][0] != "ok":
            continue
        kind, mode = _mode_of(table, name)
        status, value = twin.get(name, ("error", "no such column in the twin"))
        if status != "ok":
            failures += [(kind, name, f"raised on the twin: {value}")]
            continue
        wanted = real[name][1]
        if mode == "same" and value != wanted:
            failures += [(kind, name, f"real {wanted!r}, twin {value!r}")]
        elif mode == "bad" and wanted == 0 and value != 0:
            failures += [(kind, name, f"{value} bad cell(s) on the twin, none on the real")]
        elif mode == "present" and wanted and not value:
            failures += [(kind, name, "the real has it and the twin does not")]
        elif mode == "spellings" and _spelling_failure(wanted, value, real_rows, twin_rows):
            failures += [(kind, name, _spelling_failure(wanted, value, real_rows, twin_rows))]
        elif mode == "share" and _share_failure(wanted, value):
            failures += [(kind, name, f"real {wanted!r}, twin {value!r}")]
        elif mode == "shapes" and _shape_failure(wanted, value):
            failures += [(kind, name, _shape_failure(wanted, value))]
        elif mode == "forms" and _form_failure(wanted, value):
            failures += [(kind, name, _form_failure(wanted, value))]
        elif mode == "range" and _range_failure(wanted, value):
            failures += [(kind, name, _range_failure(wanted, value))]
        elif mode == "ratios" and _ratio_failure(wanted, value):
            failures += [(kind, name, _ratio_failure(wanted, value))]
        elif mode == "codes" and _unseen_codes(wanted, value):
            failures += [(kind, name, f"{_unseen_codes(wanted, value)} cell(s) hold a code the real never writes")]
        elif mode == "levels" and _lost_levels(wanted, value):
            failures += [(kind, name, f"values {FLOOR}+ real cells hold, absent {_lost_levels(wanted, value)[:4]}")]
    return failures


# -- the person's answers ---------------------------------------------------


def _entries(document: "dict") -> "list[dict]":
    """Every entry of a questions file that takes an answer."""
    found: "list[dict]" = []
    for key in ("about_your_file", "asked"):
        for entry in document.get(key) or []:
            if isinstance(entry, dict) and "answers_you_can_give" in entry:
                found += [entry]
    for entry in (document.get("checklist") or {}).get("columns") or []:
        if isinstance(entry, dict) and "answers_you_can_give" in entry:
            found += [entry]
    return found


def _offered(entry: "dict") -> "list[str]":
    return [f"{choice.get('answer')}" for choice in entry["answers_you_can_give"]]


# Keys whose strings are names or answers rather than prose a person reads.
NOT_PROSE = frozenset({"column", "answer", "your_answer", "table", "subject"})


def prose(value: object) -> "list[str]":
    """Every sentence a questions file shows the person, under any key but a name or an answer."""
    found: "list[str]" = []
    if isinstance(value, str):
        found += [value]
    elif isinstance(value, dict):
        for key, inner in value.items():
            if key not in NOT_PROSE:
                found += prose(inner)
    elif isinstance(value, list):
        for inner in value:
            found += prose(inner)
    return found


def answer_generally(table: Table, document: "dict") -> "tuple[list[dict], bool]":
    """Fill a questions file the way the person who holds the table would.

    The answers are GENERAL facts about the data: which column is a
    record number, which holds codes, how a date orders its day and
    month, that a pressure is two numbers in one cell, which character
    divides the columns. Nothing about the analysis. An answer the file
    does not offer is left blank, which keeps the reading synthtwin took
    -- save where the question offers `identifier`: since lane HX (plan
    P4-D401) such a question left blank holds the column as record
    numbers until it is answered, so the person who knows the column is
    something else answers `keep`, which keeps the reading as the blank
    did before (batch 4d's integration, 2026-10-20). Since lane HX3
    (plan P4-D420) the person question route four puts offers `code`
    too, so a column the person knows as a code -- the diagnoses
    export's SNOMED ids -- is answered `code` there, in the one round.
    Returns what was asked -- column (or subject), the answers offered
    and the answer given -- and whether every question was general.

    A question is general when every answer it offers is about the data
    AND none of the prose that asks it -- the entry's own sentences
    (`what_synthtwin_saw`, `read_as_now`, `then_the_description_publishes`,
    each answer's `means`), the checklist's `question` and `why` for a
    checklist column, and the file's own framing (`what_this_is`,
    `how_to_answer`, ...) -- asks about an analysis.
    """
    asked: "list[dict]" = []
    general = True
    file_facts = {"data", "semicolon" if table.name == "vitals" else "comma"} | set(table.facts)
    every_column = {column for names in table.kinds.values() for column in names}
    checklist = document.get("checklist") or {}
    framing = " ".join(prose({key: value for key, value in document.items() if key not in ("about_your_file", "asked", "checklist")}))
    checklist_words = " ".join(prose({key: value for key, value in checklist.items() if key != "columns"}))
    listed = [id(entry) for entry in checklist.get("columns") or []]
    for entry in _entries(document):
        offered = _offered(entry)
        column = f"{entry.get('column', '')}"
        if column in every_column:
            known = table.knows.get(column, "")
        else:
            # A question about the whole file names its subject where a
            # column's name would stand ("which row your column names are
            # in"): the person answers it with what they know of the file.
            known = next((answer for answer in offered if answer in file_facts), "")
        given = known if known in offered else ""
        if not given and known and "identifier" in offered and "keep" in offered:
            given = "keep"
        # ...and the Safe Harbor question (plan P4-D427; lane ZR-b's ZS.7):
        # a column the person knows as anything but a record number names
        # nobody, so `no`; one they know as a record number, `yes`; and a
        # five-figure ZIP code names a place smaller than a state, so `yes`
        # (the second repair of lane SH, item 6).
        if not given and known and offered == ["no", "yes"]:
            given = "yes" if known == "identifier" or column in PLACES else "no"
        entry["your_answer"] = given
        words = " ".join(prose(entry) + [framing] + ([checklist_words] if id(entry) in listed else []))
        this_general = all(
            answer in GENERAL_ANSWERS or DATE_COUNT_ANSWER.fullmatch(answer) for answer in offered
        ) and not ANALYSIS_WORDS.search(words)
        general = general and this_general
        asked += [{
            "column": column or f"{entry.get('subject', entry.get('about', 'the file'))}",
            "offered": offered,
            "given": given,
            "general": this_general,
        }]
    return asked, general


# -- one table, end to end ---------------------------------------------------


def _quietly(arguments: "list[str]") -> "tuple[int, str]":
    """Run one synthtwin command in this process; its exit code, or the error it raised."""
    from synthtwin import cli

    sink = io.StringIO()
    try:
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            code = cli.main(arguments)
    except Exception as failure:  # noqa: BLE001 -- a traceback is a result to record
        return -1, f"{type(failure).__name__}: {failure}"[:300]
    except SystemExit as stop:
        return int(stop.code or 0) if isinstance(stop.code, int) else 2, "exited"
    if code in (0, 3):
        return int(code), ""
    said = [line for line in sink.getvalue().split("\n") if line.strip()]
    return int(code), (said[-1] if said else "")[:300]


def run_table(table: Table, folder: pathlib.Path, n: int, seed: int) -> "dict":
    """profile, the general answers, profile --answers, generate, validate, the analyst.

    Every step is recorded, and a step that fails stops the ones that
    need its output. Nothing is retried and nothing is repaired.
    """
    from synthtwin import validation

    folder.mkdir(parents=True, exist_ok=True)
    source = write_table(table, folder, n, seed)
    stem = table.name
    profile_path = folder / f"{stem}-profile.json"
    questions_path = folder / f"{stem}-questions.json"
    result: "dict" = {"table": table.name, "rows": n, "steps": {}, "misses": [], "analyst": []}
    steps = result["steps"]
    started = time.perf_counter()

    code, error = _quietly(["profile", f"{source}", "--replace"])
    steps["profile"] = {"exit": code, "error": error}
    if code != 0:
        result["seconds"] = time.perf_counter() - started
        return result
    document = json.loads(questions_path.read_text(encoding="utf-8"))
    asked, general = answer_generally(table, document)
    result["asked"] = asked
    result["general"] = general
    questions_path.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
    code, error = _quietly(["profile", f"{source}", "--replace", "--answers", f"{questions_path}"])
    steps["answers"] = {"exit": code, "error": error}
    if code != 0:
        result["seconds"] = time.perf_counter() - started
        return result
    # ...AND THE SAFE HARBOR QUESTION AN ANSWER OPENS (plan P4-D427, the
    # second repair of lane SH, item 6): a column of ZIP-shaped numbers
    # answered `code` or `keep` is put that question in the run reading
    # the answer, and the person answers it as they did the first.
    follow = json.loads(questions_path.read_text(encoding="utf-8"))
    if any(_offered(entry) == ["no", "yes"] and not entry.get("your_answer")
           for entry in follow.get("asked") or []):
        more, more_general = answer_generally(table, follow)
        result["asked"] = asked + [one for one in more if one["offered"] == ["no", "yes"]]
        result["general"] = general and more_general
        questions_path.write_text(json.dumps(follow, indent=2), encoding="utf-8", newline="\n")
        code, error = _quietly(["profile", f"{source}", "--replace", "--answers", f"{questions_path}"])
        steps["answers"] = {"exit": code, "error": error}
        if code != 0:
            result["seconds"] = time.perf_counter() - started
            return result

    code, error = _quietly(["generate", f"{profile_path}", "--replace", "--seed", "0"])
    steps["generate"] = {"exit": code, "error": error}
    twin = folder / f"{stem}-twin{table.suffix}"
    if code != 0 or not twin.is_file():
        result["seconds"] = time.perf_counter() - started
        return result

    seen: "list[object]" = []
    measure = validation.measure

    def keep(description: object, path: str, sheet: str = "") -> object:
        outcome = measure(description, path, sheet)  # type: ignore[arg-type]
        seen.extend([outcome])
        return outcome

    validation.measure = keep  # type: ignore[assignment]
    try:
        code, error = _quietly(["validate", f"{profile_path}", "--replace"])
    finally:
        validation.measure = measure  # type: ignore[assignment]
    steps["validate"] = {"exit": code, "error": error}
    if seen:
        for check in seen[0].checks:  # type: ignore[attr-defined]
            if check.verdict == validation.MISSED:
                result["misses"] += [[check.column, check.subcheck or check.fact]]

    try:
        described = json.loads(profile_path.read_text(encoding="utf-8"))
        result["roles"] = {f"{column['name']}": f"{column['role']}" for column in described["columns"]}
    except (OSError, ValueError, KeyError, TypeError):
        result["roles"] = {}
    real = analyse(table, source)
    made = analyse(table, twin)
    result["analyst_real_errors"] = real_faults(table, real)
    result["analyst"] = [list(failure) for failure in analyst_failures(table, real, made)]
    result["seconds"] = time.perf_counter() - started
    return result


# -- per kind, and the three KPIs --------------------------------------------

# WHO OWNS EACH FAILURE, by the lanes of the December plan (plan-dec
# PLAN-DEC.md section 3.1) and of its zoo-fix track (wave6 ZOO/PLAN.md
# sections 1 to 3: UN-1a, UN-1b, CODES-1, CODES-2, CODES-3, GG, TR, SS,
# LISTS, UN-2, NOTES, KV, and the widened DST, LM1 and GR), or 'needs
# owner' where no lane covers it yet and the orchestrator names a new
# one. Filled from the baseline runs of plan P4-D399. Each line is
# (owner, the gap, the failures it covers): the failures are named as
# `failure_items` names them -- a step ('profile', 'answers',
# 'generate', 'validate'), 'questions', 'miss <column>', 'real <check>',
# or an analyst check's own name -- and the line covers the ones its
# pattern matches whole. A failure no line matches is UNOWNED, and
# K-HZ-02 counts it: a kind that already has an owner does not lend it
# to a new failure. A failure only 'needs owner' covers is counted apart
# (`failures_needing_owner`): it has a gap stated, not a lane.
NEEDS_OWNER = "needs owner"
ZOO_LANES = (
    "UN-1a", "UN-1b", "CODES-1", "CODES-2", "CODES-3", "GG", "TR", "SS", "LISTS", "UN-2", "NOTES", "KV", "GR",
)


def covers(*names: str, columns: "tuple[str, ...]" = ()) -> str:
    """The pattern an OWNERS line covers: these failures whole, and the generic checks of these columns."""
    whole = [re.escape(name) for name in names]
    if columns:
        whole += [
            r"(shapes|forms|levels|missing|missing spellings|dtype|stand-ins|codes) ("
            + "|".join(re.escape(c) for c in columns) + ")"
        ]
    return "|".join(whole)


WITHHELD = (
    "a level fewer than 11 rows hold is written as 'group-N', or as a made-up code "
    "outside its system's pattern, so the analyst's code list or pattern meets it"
)
UNITS_AS_LABELS = (
    "a number beside a unit ('172 cm', '36,9 °C', '98%', '98.4 F', '5.4 mmol/L' over several "
    "units) is read as labels and its rarer values written as 'group-N'; the questions file "
    "offers no 'measurement' answer for it"
)
MADE_UP_CODES = (
    "a code's levels are made up character by character in its shape ('T2N1M0' as 'D5X1Q5', "
    "an NPI that fails its Luhn check), so a grammar or a check figure the real codes obey "
    "rejects them"
)
# HELD IN PEOPLE (lane HX2, plan P4-D406; batch 4e's integration, the
# integrator's, unreviewed). Beside a person column, a measurement column
# holding a value one to ten people hold is held whole (the orchestrator's
# ruling of 2026-10-19 15:42, item 1), and the person column's census of
# rows a person is counted in people, its groups of one to ten pooled:
# the zoo measured both on the merge, owned by the lanes P4-D406 names
# (pooling values in subject units, lane PS; the census in subject bands,
# lane MG). Its dates and times are pooled in people since lane PS (plan
# P4-D417): every check that parses them holds at 600 and 20,000 rows.
POOLED_FEW_HOURS = (
    "a stamp pooled in people at the hour over a short span (lane PS, plan P4-D417): its twin "
    "is built from a description of a few evenly filled hours with no census of the hour, so the "
    "generator's count of different values and its count at midnight miss (method G7.9 on "
    "stamps): 32 of 39 hours and 1,208 rows at midnight against 515 at 20,000 rows; the twin's "
    "stamps parse; lane PS's follow-up"
)
HELD_VALUES = (
    "a measurement column beside a person column holding a value one to ten people hold is held "
    "whole (the orchestrator's ruling of 2026-10-19 15:42, item 1): its twin writes made-up values "
    "in the column's layouts; pooling values in subject units is lane PS's (plan P4-D406)"
)
CENSUS_IN_PEOPLE = (
    "the person column's census of rows a person is counted in people, its groups of one to ten "
    "pooled, so the shares of patients with two and three rows move on the twin; a census in "
    "subject bands is lane MG's (plan P4-D406)"
)
OWNERS: "dict[str, tuple[tuple[str, str, str], ...]]" = {
    "demographics": (
        ("CODES-2", WITHHELD, covers(
            "ancestry is a listed category", "ethnicity is a listed category",
            "gender codes are M/F/U/X", "gender words are Male/Female/Unknown",
            columns=("ancestry", "ethnicity", "gender_code", "gender_word"))),
    ),
    "diagnoses": (
        ("CODES-1", "a code column held whole in people (plan P4-D406) gets a twin that misses its "
                    "published forms: the identifier generator's limit, lane CODES-1 part C "
                    "(P4-D406's stated limit 4)", covers("miss icd10_dotted")),
        ("CODES-1", "a held-back code is written outside its pattern or as a number-class stand-in "
                    "('486' as '99.9'), and a SNOMED id answered 'code' in round one (lane HX3, plan "
                    "P4-D420) keeps the values 11 or more rows hold but writes codes the real never "
                    "writes (2 codes on 14 twin cells at 600 rows, batch 4f's merge)", covers(
            "ICD-10-CM with the dot", "ICD-10-CM without the dot", "ICD-9-CM",
            "SNOMED CT ids are 6 to 18 figures", "present-on-admission flags",
            columns=("icd10_dotted", "icd10_plain", "icd9", "snomed_id", "poa"))),
        ("CODES-2", WITHHELD, covers(
            "ICD-10-CM with the dot", "ICD-10-CM without the dot", "ICD-9-CM",
            columns=("icd10_dotted", "icd10_plain", "icd9", "snomed_id", "poa"))),
    ),
    "medication_orders": (
        ("CODES-2", WITHHELD, covers("routes", "frequencies", "dose strings read", columns=("route", "frequency", "dose"))),
    ),
    "imaging": (
        ("CODES-2", WITHHELD, covers("DICOM modality codes", "body parts", columns=("modality", "body_part"))),
    ),
    "genomics": (
        ("CODES-2", WITHHELD, covers("clinical significance", columns=("zygosity", "classification"))),
    ),
    "perioperative": (
        ("CODES-2", WITHHELD, covers("physical status with its emergency mark", columns=("phys_status",))),
    ),
    "encounters": (
        ("MG", CENSUS_IN_PEOPLE, covers("patients with two rows or more, and three or more, as shares")),
        ("DST", "the twin writes an offset not in force on its date (US Eastern)", covers(
            "admit_ts wears an offset in force on its date", "discharge_ts wears an offset in force on its date")),
    ),
    "labs": (
        ("PS", HELD_VALUES, covers(
            "censored values read past < and >", "the numbers of viral_load keep their range",
            columns=("viral_load",))),
        ("CODES-1", "a measurement column held whole in people (plan P4-D406) gets a twin that misses "
                    "its published forms at 20,000 rows: the identifier generator's limit, lane CODES-1 "
                    "part C (P4-D406's stated limit 4)", covers("miss viral_load")),
        ("MG", CENSUS_IN_PEOPLE, covers("patients with two rows or more, and three or more, as shares")),
        ("UN-1a", UNITS_AS_LABELS, covers(
            "a value and its unit", "the value read as a number", "the numbers of result keep their range",
            columns=("result",))),
        ("UN-1b", "the digit and decimals guards refuse units with figures ('10*3/uL')", covers(
            "a value and its unit", "the value read as a number", "the numbers of result keep their range",
            columns=("result",))),
        ("CODES-2", WITHHELD, covers("POS/NEG results", "abnormal flags", columns=("qualitative", "abnormal_flag"))),
        ("CODES-1", "a held-back LOINC code is written as a code in its form the real never writes "
                    "('00000-0')", covers("LOINC codes", columns=("loinc",))),
        ("LM1", "a joined range '12.0-16.0' comes back as '12.0-16' and '70-99' as '70.0-99.0': "
                "validate misses its styles and counts", covers("miss ref_range", columns=("ref_range",))),
    ),
    "mixed_results": (
        ("CODES-2", WITHHELD, covers(
            "a result is a number, a censored number or a word", "the numbers read past < and >",
            columns=("result_value",))),
        ("CODES-1", "a held-back result's shape is filled from the whole alphabet", covers(
            "a result is a number, a censored number or a word", columns=("result_value",))),
        # RE-OWNED AT BATCH 4E'S RECORDS (2026-10-21; push critic 11's MINOR 3), read
        # on d90d16b4 at 20,000 rows, the driver's seed for labs (20261019): validate
        # measures the twin's held-back pool exactly as generate wrote it (26 labels,
        # 95 cells), so the miss is generation's, not validate's (lane SV's work is
        # validate's scale): the 95 held-back numbers land at a mean of 6.124 against
        # the published 6.325 (window 6.125 to 6.525), kept to one figure before the
        # point beside the published 2.0 to 9.0, since the real's 10.0 to 11.2 are a
        # form under the floor. A placement held by a width: lane G2T2's.
        ("G2T2", "one result column holding numbers, censored numbers and words: at 20,000 rows "
                 "the twin's held-back numbers, kept to the one-figure width, miss their published "
                 "mean, which validate reports", covers("miss result_value")),
    ),
    "vitals": (
        ("UN-1a", UNITS_AS_LABELS, covers(
            "oxygen saturation with %", "stature in cm", "temperature with its unit",
            "the numbers of stature keep their range", "the numbers of temp keep their range",
            "the numbers of spo2 keep their range", columns=("spo2", "stature", "temp"))),
        ("UN-1b", "a decimal-comma number beside a unit ('72,5 kg') is written as made-up "
                  "characters", covers(
            "weight in kg with a decimal comma", "the numbers of weight keep their range", columns=("weight",))),
    ),
    "semicolon_decimal_comma": (
        ("UN-1b", "a decimal-comma number ('25,5') is read as labels made up character by character: the "
                  "twin's values are invented ('48,1' in the middle, '0,0' to '99,9')", covers(
            "the numbers of mass_index keep their range", columns=("mass_index",))),
    ),
    "us_unit_vitals": (
        ("UN-1a", UNITS_AS_LABELS, covers(
            "temperature in F", "weight in lb", "the numbers of temp_f keep their range",
            "the numbers of weight keep their range", columns=("temp_f", "weight"))),
        ("UN-2", "a stature in feet and inches (5'10\") is a template of two numbers", covers(
            "stature in feet and inches", "the numbers of stature keep their range", columns=("stature",))),
    ),
    "flowsheet_long": (
        ("KV", "a long table's value is read by its row name; the twin carries no relation "
               "between the two columns (the between-columns program, TRACKED T1 and T2)", covers(
            "BP rows hold '120/80' (read by row name)", "other rows hold numbers (read by row name)",
            columns=("flo_value",))),
    ),
    "clinical_notes": (
        ("NOTES", "free text publishes no line, marker or length facts: at 600 rows the twin's notes "
                  "hold no line break and no de-identification token, few quotes and lengths near "
                  "one value; at 20,000 the column turns long tail and most notes are 'group-N'", covers(
            "some note runs over several lines", "some note keeps a de-identification token",
            "some note runs over several lines, as a share", "some note keeps a de-identification token, as a share",
            "some note quotes a phrase", "some note quotes a phrase, as a share",
            "note lengths at the 10th, 50th and 90th percentiles", columns=("note_text",))),
    ),
    "surveys_pro": (
        ("GG", "a 1-to-5 score beside a missing code (-99) is a few-valued number with one wide gap: "
               "the twin writes values inside the gap and loses a level", covers(
            "scores 1 to 5 or -99", columns=("q2_score", "q3_score"))),
        ("UN-2", "no question asks whether -99 means missing", covers("scores 1 to 5 or -99")),
    ),
    "dicom_metadata": (
        ("TR", "DICOM's TM time of day ('074512.123456') is read as a decimal number: the twin "
               "loses its leading zero and writes minutes and seconds past 59, and at 20,000 rows "
               "validate misses its spread", covers("TM times parse as %H%M%S.%f", "miss study_time")),
        ("CODES-3", "a DICOM UID of dotted figures is written as made-up characters",
         covers("UIDs are dotted figures", columns=("study_uid",))),
    ),
    "multi_value_cells": (
        ("LISTS", "a cell listing several codes or words ('E11.9;I10', 'Penicillin|Sulfa') is read "
                  "as one label: its rarer combinations are written as 'group-N' and the lists of "
                  "three and four are lost", covers(
            "every listed code is ICD-10-CM", "allergies are listed words", "some cell lists several codes",
            "some cell lists several allergies", "some cell lists several codes, as a share",
            "some cell lists several allergies, as a share", columns=("dx_list", "allergies"))),
    ),
    "tumor_registry": (
        ("CODES-1", MADE_UP_CODES, covers("TNM", "ICD-O-3 morphology", "ICD-O-3 topography", columns=("tnm",))),
    ),
    "partial_dates": (
        ("TR", "a date known to the month ('03/2019') or the year beside full dates is written as a "
               "made-up figure string", covers("dates to the year, the month or the day")),
    ),
    "immunizations_providers": (
        ("CODES-1", MADE_UP_CODES, covers("NPIs pass their Luhn check", columns=("npi",))),
    ),
    "wearables": (
        ("PS", POOLED_FEW_HOURS, covers("miss ts")),
    ),
}


def failure_items(table: Table, result: "dict", kind: str) -> "list[str]":
    """Every way a kind failed in one table's run, named for OWNERS."""
    columns = table.kinds[kind]
    file_kinds = [name for name in table.kinds if name in FILE_KINDS]
    items: "list[str]" = []
    steps = result["steps"]
    for step in ("profile", "answers", "generate", "validate"):
        if step not in steps or steps[step]["exit"] not in (0, 3):
            items += [step]
            break
    every_column = {column for names in table.kinds.values() for column in names}
    for entry in result.get("asked", []):
        if not entry["general"] and (entry["column"] in columns or entry["column"] not in every_column):
            items += ["questions"]
            break
    for miss in result["misses"]:
        if miss[0] in columns or (not miss[0] and (kind in file_kinds or not file_kinds)):
            items += [f"miss {miss[0] or 'the file'}"]
    for name in result.get("analyst_real_errors", []):
        if name == "read" or _mode_of(table, name)[0] == kind:
            items += [f"real {name}"]
    items += [failure[1] for failure in result["analyst"] if failure[0] == kind]
    return sorted(set(items))


def owner_lines(kind: str, item: str) -> "list[tuple[str, str]]":
    """The OWNERS lines that cover one failure of a kind: (owner, gap)."""
    return [
        (owner, gap) for owner, gap, covers in OWNERS.get(kind, ())
        if re.fullmatch(covers, item)
    ]


def _step_of(items: "list[str]") -> str:
    for step in ("profile", "answers", "generate", "validate"):
        if step in items:
            return step
    if "questions" in items:
        return "questions"
    if any(item.startswith("miss ") for item in items):
        return "validate"
    if any(item.startswith("real ") for item in items):
        return "analyst on the real table"
    return "analyst" if items else ""


def per_kind(results: "list[dict]") -> "dict[str, dict]":
    """Each kind's verdict: passed, the failing step, its misses, analyst failures and owners.

    A kind passes only when every step ran (exit 0 or 3), every
    question its table asked was general, validate missed nothing on
    its columns, the analyst's script held on the real table, and every
    analyst check held on the twin.
    """
    kinds: "dict[str, dict]" = {}
    for result in results:
        table = table_named(result["table"])
        file_kinds = [kind for kind in table.kinds if kind in FILE_KINDS]
        for kind, columns in table.kinds.items():
            items = failure_items(table, result, kind)
            misses = [
                miss for miss in result["misses"]
                if miss[0] in columns
                or (not miss[0] and (kind in file_kinds or not file_kinds))
            ]
            analyst = [failure for failure in result["analyst"] if failure[0] == kind]
            owned = {item: owner_lines(kind, item) for item in items}
            kinds[kind] = {
                "table": table.name,
                "passed": not items,
                "failing_step": _step_of(items),
                "failures": items,
                "misses": len(misses),
                "missed": sorted({f"{miss[0]}: {miss[1]}" for miss in misses}),
                "analyst_failures": [f"{failure[1]} -- {failure[2]}" for failure in analyst],
                "unowned": sorted(item for item, lines in owned.items() if not lines),
            "needing_owner": sorted(
                item for item, lines in owned.items() if lines and {owner for owner, _gap in lines} == {NEEDS_OWNER}
            ),
                "owners": sorted({owner for lines in owned.values() for owner, _gap in lines}),
                "gaps": sorted({f"{owner}: {gap}" for lines in owned.values() for owner, gap in lines}),
            }
    return {kind: kinds[kind] for kind in KINDS if kind in kinds}


def runnable_tables() -> "tuple[Table, ...]":
    """The catalogue's tables this machine can read: a workbook needs the cross-check reader.

    pandas opens an `.xlsx` through openpyxl, which CI's `minimums` cell
    does not install (`tests/crosscheck.py`); there the workbook export
    is left out, and its kinds are named as not measured.
    """
    import crosscheck

    if crosscheck.present():
        return TABLES
    return tuple(table for table in TABLES if table.suffix != ".xlsx")


def workbook_kinds() -> "tuple[str, ...]":
    """The kinds the workbook exports serve, measured only where the cross-check reader is."""
    return tuple(kind for table in TABLES if table.suffix == ".xlsx" for kind in table.kinds)


def run_zoo(folder: pathlib.Path, n: int, seed: int = 20261016) -> "list[dict]":
    """Every catalogue table this machine can read, end to end, each in a folder of its own."""
    results: "list[dict]" = []
    runnable = runnable_tables()
    for place in range(len(TABLES)):
        table = TABLES[place]
        if table in runnable:
            results += [run_table(table, folder / table.name, n, seed + place)]
    return results


def zoo_measures(results: "list[dict]") -> "dict[str, dict]":
    """K-HZ-01 and K-HZ-02 from one run of the battery.

    The `_csv` keys count the kinds of the delimited exports alone, so a
    machine without the workbook reader still measures and judges them.
    """
    kinds = per_kind(results)
    workbook = set(workbook_kinds())
    passing = [kind for kind, verdict in kinds.items() if verdict["passed"]]
    failing = [kind for kind, verdict in kinds.items() if not verdict["passed"]]
    questions = [entry for result in results for entry in result.get("asked", [])]
    roles = {role for result in results for role in result.get("roles", {}).values()}
    first = {
        "kinds": len(kinds),
        "kinds_passing_end_to_end": len(passing),
        "kinds_passing_csv": sum(1 for kind in passing if kind not in workbook),
        "kinds_csv": sum(1 for kind in kinds if kind not in workbook),
        "tables": len(results),
        "tables_profiled": sum(1 for r in results if r["steps"].get("answers", {}).get("exit") == 0),
        "tables_generated": sum(1 for r in results if r["steps"].get("generate", {}).get("exit") == 0),
        "questions_asked": len(questions),
        "questions_not_general": sum(1 for entry in questions if not entry["general"]),
        "analyst_errors_on_real": sum(len(r.get("analyst_real_errors", [])) for r in results),
        "roles_reached": len(roles),
        "roles": sorted(roles),
        "failing": [kind for kind in KINDS if kind in failing],
    }
    second: "dict[str, object]" = {
        "kinds_failing": len(failing),
        "kinds_failing_csv": sum(1 for kind in failing if kind not in workbook),
        "failing_kinds_without_owner": sum(1 for kind in failing if kinds[kind]["unowned"]),
        "failures_without_owner": sum(len(kinds[kind]["unowned"]) for kind in failing),
        "failures_needing_owner": sum(len(kinds[kind]["needing_owner"]) for kind in failing),
        "validate_misses": sum(len(r["misses"]) for r in results),
        "analyst_failures": sum(len(r["analyst"]) for r in results),
    }
    for kind, verdict in kinds.items():
        second[f"misses_{kind}"] = verdict["misses"]
        second[f"analyst_failures_{kind}"] = len(verdict["analyst_failures"])
    return {"K-HZ-01": first, "K-HZ-02": second, "kinds": kinds}

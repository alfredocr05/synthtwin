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
    "imaging",
    "excel_serial_dates",
)
FILE_KINDS = (
    "utf8_accents",
    "byte_order_mark",
    "crlf_line_endings",
    "semicolon_decimal_comma",
    "latin1",
    "excel_workbook",
    "excel_serial_dates",
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


def eastern_offset(moment: datetime.datetime) -> str:
    """The offset in force at a local US Eastern wall-clock moment, as written."""
    start = datetime.datetime.combine(_nth_sunday(moment.year, 3, 2), datetime.time(2))
    end = datetime.datetime.combine(_nth_sunday(moment.year, 11, 1), datetime.time(2))
    return "-04:00" if start <= moment < end else "-05:00"


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
    "1742-6", "2093-3", "13457-7", "94500-6", "17861-6",
))
UNITS = (("mmol/L", 40.0), ("mg/dL", 35.0), ("g/dL", 10.0), ("%", 10.0), ("10*3/uL", 5.0))
RANGES = (("3.5-5.0", 25.0), ("70-99", 25.0), ("0.6-1.2", 20.0), ("12.0-16.0", 15.0), ("4.0-5.6", 15.0))
FLAGS = (("", 60.0), ("N", 10.0), ("H", 12.0), ("L", 10.0), ("HH", 4.0), ("LL", 4.0))


def labs(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Labs: LOINC, values with units, POS/NEG, '<5' and '>1000', ranges and H/L flags."""
    draw = random.Random(seed)
    header = [
        "patient_id", "collected_at", "loinc", "result", "qualitative", "viral_load",
        "ref_range", "abnormal_flag",
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
        ]]
    return header, rows


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
    """The survey as an Excel workbook: typed number cells, a date style, text inline."""
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
            if name == "survey_date":
                cells += [workbooks.cell(where, value, "", 1)]
            elif name in numeric:
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
CLASSES = (
    ("Pathogenic", 15.0), ("Likely pathogenic", 10.0), ("Uncertain significance", 45.0),
    ("Likely benign", 15.0), ("Benign", 15.0),
)


def genomics(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Variant calls: HGVS strings, gene symbols, allele frequencies."""
    draw = random.Random(seed)
    header = ["sample_id", "gene", "hgvs_c", "hgvs_p", "allele_freq", "zygosity", "classification"]
    rows: "list[list[str]]" = []
    for index in range(n):
        rows += [[
            f"S{300000 + index}",
            _pick(draw, GENES),
            _pick(draw, HGVS_C),
            _pick(draw, HGVS_P),
            f"{min(0.5, draw.expovariate(40.0)):.4f}",
            _pick(draw, (("heterozygous", 70.0), ("homozygous", 28.0), ("hemizygous", 2.0))),
            _pick(draw, CLASSES),
        ]]
    return header, rows


MODALITIES = (
    ("CT", 25.0), ("MR", 15.0), ("CR", 20.0), ("DX", 15.0), ("US", 12.0), ("NM", 4.0),
    ("PT", 3.0), ("MG", 5.0), ("XA", 1.0),
)
BODY_PARTS = (("CHEST", 35.0), ("HEAD", 20.0), ("ABDOMEN", 18.0), ("KNEE", 9.0), ("SPINE", 10.0), ("PELVIS", 8.0))


def imaging(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Imaging metadata: accession numbers, DICOM modality codes, Excel serial study dates."""
    draw = random.Random(seed)
    header = ["accession", "patient_id", "modality", "study_date_serial", "body_part", "series_count"]
    rows: "list[list[str]]" = []
    for index in range(n):
        day = _day(draw, datetime.date(2023, 1, 1), datetime.date(2024, 12, 31))
        rows += [[
            f"ACC{40000000 + index}",
            f"PT{1000000 + draw.randrange(max(n // 3, 1)):07d}",
            _pick(draw, MODALITIES),
            f"{(day - EXCEL_EPOCH).days}",
            _pick(draw, BODY_PARTS),
            f"{draw.randint(1, 12)}",
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
# all ("present": where the real table has it, the twin must).


@dataclasses.dataclass(frozen=True)
class Check:
    """One step of an analyst script: the kind it serves, its name and its mode."""

    kind: str
    name: str
    mode: str
    run: "Callable[[object], object]"


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
        wrong += 0 if eastern_offset(local) == text[19:] else 1
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


def _csv_reader(**options: object) -> "Callable[[pathlib.Path], dict[str, object]]":
    """The analyst's two reads: the dtypes pandas infers, and codes kept as text."""

    def read(path: pathlib.Path) -> "dict[str, object]":
        import pandas

        inferred = pandas.read_csv(path, **options)
        as_text = pandas.read_csv(path, dtype=str, keep_default_na=True, **options)
        return {"inferred": inferred, "text": as_text}

    return read


def _excel_reader(path: pathlib.Path) -> "dict[str, object]":
    import pandas

    inferred = pandas.read_excel(path)
    as_text = pandas.read_excel(path, dtype=str)
    return {"inferred": inferred, "text": as_text}


def _t(column: str) -> "Callable[[dict[str, object]], object]":
    return lambda frames: frames["text"][column]  # type: ignore[index]


def _i(column: str) -> "Callable[[dict[str, object]], object]":
    return lambda frames: frames["inferred"][column]  # type: ignore[index]


def _bad(kind: str, name: str, how: "Callable[[dict[str, object]], object]") -> Check:
    return Check(kind, name, "bad", how)


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
            _bad("demographics", "record numbers match PT#######", lambda f: _bad_pattern(_t("patient_id")(f), r"PT\d{7}")),
            _bad("demographics", "dob_iso parses as %Y-%m-%d", lambda f: _bad_dates(_t("dob_iso")(f), "%Y-%m-%d")),
            _bad("demographics", "dob_us parses as %m/%d/%Y", lambda f: _bad_dates(_t("dob_us")(f), "%m/%d/%Y")),
            _bad("demographics", "dob_text parses as %d-%b-%Y", lambda f: _bad_dates(_t("dob_text")(f), "%d-%b-%Y")),
            _bad("demographics", "age is a whole number or 90+", lambda f: _bad_pattern(_t("age")(f), r"\d{1,2}|90\+")),
            _bad("demographics", "gender codes are M/F/U/X", lambda f: _bad_set(_t("gender_code")(f), {"M", "F", "U", "X"})),
            _bad("demographics", "gender words are Male/Female/Unknown", lambda f: _bad_set(_t("gender_word")(f), {"Male", "Female", "Unknown"})),
            _bad("demographics", "ancestry is a listed category", lambda f: _bad_set(_t("ancestry")(f), {v for v, _w in ANCESTRIES})),
            _bad("demographics", "ethnicity is a listed category", lambda f: _bad_set(_t("ethnicity")(f), {v for v, _w in ETHNICITIES})),
            _bad("demographics", "zip5 is five figures", lambda f: _bad_pattern(_t("zip5")(f), r"\d{5}")),
            _bad("demographics", "zip4 is ZIP+4", lambda f: _bad_pattern(_t("zip4")(f), r"\d{5}-\d{4}")),
            _bad("utf8_accents", "languages are listed ones", lambda f: _bad_set(_t("preferred_language")(f), {v for v, _w in LANGUAGES})),
            _bad("utf8_accents", "cities are listed ones", lambda f: _bad_set(_t("birth_city")(f), {v for v, _w in CITIES})),
            _bad("utf8_accents", "no cell reads as mojibake", lambda f: _mojibake(f["text"])),
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
            Check("byte_order_mark", "the first column is named enc_id", "same", lambda f: list(f["inferred"].columns)[0]),  # type: ignore[attr-defined]
            _bad("crlf_line_endings", "no cell carries a stray carriage return", lambda f: _stray_returns(f["text"])),
            _bad("encounters", "encounter ids match E#########", lambda f: _bad_pattern(_t("enc_id")(f), r"E\d{9}")),
            _bad("encounters", "patients match PT#######", lambda f: _bad_pattern(_t("patient_id")(f), r"PT\d{7}")),
            _bad("encounters", "some patient has several encounters", lambda f: _repeat_patients_missing(_t("patient_id")(f))),
            _bad("encounters", "admit_ts parses with its offset", lambda f: _bad_dates(_t("admit_ts")(f), "%Y-%m-%d %H:%M:%S%z", utc=True)),
            _bad("encounters", "discharge_ts parses with its offset", lambda f: _bad_dates(_t("discharge_ts")(f), "%Y-%m-%d %H:%M:%S%z", utc=True)),
            _bad("encounters", "admit_ts wears the offset in force on its date", lambda f: _wrong_offsets(_t("admit_ts")(f))),
            _bad("encounters", "discharge_ts wears the offset in force on its date", lambda f: _wrong_offsets(_t("discharge_ts")(f))),
            _bad("encounters", "length of stay is not negative", lambda f: int((_i("stay_days")(f) < 0).sum())),  # type: ignore[operator]
            _bad("encounters", "departments are listed ones, in either case", lambda f: _bad_set(_t("department")(f).str.title(), {"Cardiology", "Emergency", "Oncology", "Orthopedics", "Pediatrics", "Neurology", "Medicine"})),  # type: ignore[attr-defined]
            _bad("encounters", "visit types are listed ones", lambda f: _bad_set(_t("visit_type")(f), {v for v, _w in VISIT_TYPES})),
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
            _bad("diagnoses", "ICD-10-CM with the dot", lambda f: _bad_pattern(_t("icd10_dotted")(f), r"[A-Z][0-9][0-9A-Z](\.[0-9A-Z]{1,4})?")),
            _bad("diagnoses", "ICD-10-CM without the dot", lambda f: _bad_pattern(_t("icd10_plain")(f), r"[A-Z][0-9][0-9A-Z][0-9A-Z]{0,4}")),
            _bad("diagnoses", "ICD-9-CM", lambda f: _bad_pattern(_t("icd9")(f), r"V\d{2}(\.\d{1,2})?|E\d{3}(\.\d)?|\d{3}(\.\d{1,2})?")),
            _bad("diagnoses", "SNOMED CT ids are 6 to 18 figures", lambda f: _bad_pattern(_t("snomed_id")(f), r"[1-9]\d{5,17}")),
            _bad("diagnoses", "present-on-admission flags", lambda f: _bad_set(_t("poa")(f), {"Y", "N", "U", "W", "1"})),
            _bad("procedures", "level I procedure codes", lambda f: _bad_pattern(_t("proc_code")(f), PROC_PATTERN)),
            _bad("procedures", "procedure codes with a modifier", lambda f: _bad_pattern(_t("proc_code_mod")(f), PROC_PATTERN + r"(-[0-9A-Z]{2})?")),
            _bad("procedures", "HCPCS level II", lambda f: _bad_pattern(_t("hcpcs")(f), r"[A-V]\d{4}")),
            _bad("procedures", "ICD-10-PCS", lambda f: _bad_pattern(_t("icd10pcs")(f), r"[0-9A-HJ-NP-Z]{7}")),
        ),
    ),
    Table(
        "labs", ".csv", labs,
        lambda header, rows: csv_bytes(header, rows),
        {"labs": ("patient_id", "collected_at", "loinc", "result", "qualitative", "viral_load", "ref_range", "abnormal_flag")},
        {"patient_id": "identifier", "loinc": "code", "result": "measurement", "viral_load": "measurement", "ref_range": "joined"},
        _csv_reader(),
        (
            _bad("labs", "collected_at parses as %Y-%m-%d %H:%M", lambda f: _bad_dates(_t("collected_at")(f), "%Y-%m-%d %H:%M")),
            _bad("labs", "LOINC codes", lambda f: _bad_pattern(_t("loinc")(f), r"\d{1,5}-\d")),
            _bad("labs", "a value and its unit", lambda f: _bad_pattern(_t("result")(f), r"-?\d+(\.\d+)? (mmol/L|mg/dL|g/dL|%|10\*3/uL)")),
            _bad("labs", "the value read as a number", lambda f: _bad_numbers(_t("result")(f).str.split(" ").str[0])),  # type: ignore[attr-defined]
            _bad("labs", "POS/NEG results", lambda f: _bad_set(_t("qualitative")(f), {"POS", "NEG", "INDETERMINATE"})),
            _bad("labs", "censored values read past < and >", lambda f: _bad_numbers(_strip(_t("viral_load")(f), r"^[<>]"))),
            _bad("labs", "reference ranges split into two numbers", lambda f: _bad_numbers(_t("ref_range")(f).str.split("-", expand=True).stack())),  # type: ignore[attr-defined]
            _bad("labs", "abnormal flags", lambda f: _bad_set(_t("abnormal_flag")(f), {"N", "H", "L", "HH", "LL"})),
        ),
    ),
    Table(
        "prescriptions", ".csv", prescriptions,
        lambda header, rows: csv_bytes(header, rows),
        {"medication_orders": ("order_id", "patient_id", "ndc_542", "ndc_11", "rxnorm", "dose", "route", "frequency")},
        {"order_id": "identifier", "patient_id": "identifier", "ndc_542": "code", "ndc_11": "code", "rxnorm": "code"},
        _csv_reader(),
        (
            _bad("medication_orders", "NDC 5-4-2", lambda f: _bad_pattern(_t("ndc_542")(f), r"\d{5}-\d{4}-\d{2}")),
            _bad("medication_orders", "NDC 11 figures", lambda f: _bad_pattern(_t("ndc_11")(f), r"\d{11}")),
            _bad("medication_orders", "RxNorm ids", lambda f: _bad_pattern(_t("rxnorm")(f), r"\d{3,8}")),
            _bad("medication_orders", "dose strings read", lambda f: _bad_pattern(_t("dose")(f), r"\d+(\.\d+)?(-\d+)? (mg|tabs?|units|puffs)")),
            _bad("medication_orders", "routes", lambda f: _bad_set(_t("route")(f), {v for v, _w in ROUTES})),
            _bad("medication_orders", "frequencies", lambda f: _bad_pattern(_t("frequency")(f), r"(BID|TID|QID|QD|QHS|PRN|q\d+h)( PRN)?")),
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
            Check("semicolon_decimal_comma", "the file splits into nine columns", "same", lambda f: int(f["inferred"].shape[1])),  # type: ignore[attr-defined]
            _bad("semicolon_decimal_comma", "the mass index reads as a number", lambda f: _bad_numbers(_i("mass_index")(f))),
            _bad("vitals", "taken_at parses", lambda f: _bad_dates(_t("taken_at")(f), "%Y-%m-%d %H:%M")),
            _bad("vitals", "'120/80' splits into two numbers", lambda f: _pressure_parts_bad(_t("bp")(f))),
            _bad("vitals", "temperature with its unit", lambda f: _bad_numbers(_strip(_t("temp")(f), " °C$").str.replace(",", "."))),  # type: ignore[attr-defined]
            _bad("vitals", "oxygen saturation with %", lambda f: _bad_pattern(_t("spo2")(f), r"\d{2,3}%")),
            _bad("vitals", "stature in cm", lambda f: _bad_pattern(_t("stature")(f), r"\d{2,3} cm")),
            _bad("vitals", "weight in kg with a decimal comma", lambda f: _bad_pattern(_t("weight")(f), r"\d{2,3},\d kg")),
        ),
    ),
    Table(
        "flowsheet", ".csv", flowsheet,
        lambda header, rows: csv_bytes(header, rows),
        {"flowsheet_long": ("patient_id", "recorded_at", "flo_row", "flo_value")},
        {"patient_id": "identifier"},
        _csv_reader(),
        (
            _bad("flowsheet_long", "recorded_at parses", lambda f: _bad_dates(_t("recorded_at")(f), "%Y-%m-%dT%H:%M:%S")),
            _bad("flowsheet_long", "row names are listed ones", lambda f: _bad_set(_t("flo_row")(f), {"Pulse", "Resp", "SpO2", "Temp", "BP", "Pain Score"})),
            _bad("flowsheet_long", "BP rows hold '120/80' (read by row name)", lambda f: _flowsheet_pressures_bad(f["text"])),
            _bad("flowsheet_long", "other rows hold numbers (read by row name)", lambda f: _flowsheet_numbers_bad(f["text"])),
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
            _bad("redcap", "event names wear their arm", lambda f: _bad_pattern(_t("redcap_event_name")(f), r"[a-z0-9_]+_arm_\d+")),
            _bad("redcap", "repeat instruments are named ones", lambda f: _bad_set(_t("redcap_repeat_instrument")(f), {"adverse_events"})),
            _bad("redcap", "repeat instances are whole numbers", lambda f: _bad_pattern(_t("redcap_repeat_instance")(f), r"\d+")),
            _bad("redcap", "data access groups", lambda f: _bad_set(_t("redcap_data_access_group")(f), {"site_a", "site_b", "site_c"})),
            _bad("redcap", "consent_date parses", lambda f: _bad_dates(_t("consent_date")(f), "%Y-%m-%d")),
            _bad("redcap", "gender coded 1/2", lambda f: _bad_set(_t("gender")(f), {"1", "2"})),
            _bad("redcap", "checkboxes hold 0 or 1", lambda f: sum(_bad_set(_t(f"smoke___{k}")(f), {"0", "1"}) for k in (1, 2, 3))),
            _bad("redcap", "PHQ items 0 to 3", lambda f: sum(_bad_set(_t(f"phq_{k}")(f), {"0", "1", "2", "3"}) for k in (1, 2, 3))),
            _bad("redcap", "the calculated total is a whole number", lambda f: _bad_pattern(_t("phq_total")(f), r"\d+")),
            _bad("redcap", "form status 0/1/2", lambda f: _bad_set(_t("baseline_complete")(f), {"0", "1", "2"})),
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
            _bad("latin1", "facilities are listed ones", lambda f: _bad_set(_t("facility")(f), {v for v, _w in FACILITIES})),
            _bad("latin1", "no cell reads as mojibake", lambda f: _mojibake(f["text"])),
            _bad("claims", "claim ids", lambda f: _bad_pattern(_t("claim_id")(f), r"CLM\d{9}")),
            _bad("claims", "service_date parses as %m/%d/%Y", lambda f: _bad_dates(_t("service_date")(f), "%m/%d/%Y")),
            _bad("claims", "billed reads past $ and commas", lambda f: int(_money(_t("billed")(f)).isna().sum())),  # type: ignore[attr-defined]
            _bad("claims", "adjustments read, parentheses negative", lambda f: int(_money(_t("adjustment")(f)).isna().sum())),  # type: ignore[attr-defined]
            _bad("claims", "payer codes", lambda f: _bad_set(_t("payer_code")(f), {v for v, _w in PAYERS})),
            _bad("claims", "DRG three figures", lambda f: _bad_pattern(_t("drg")(f), r"\d{3}")),
            _bad("claims", "revenue codes keep the leading zero", lambda f: _bad_pattern(_t("revenue_code")(f), r"0\d{3}")),
        ),
    ),
    Table(
        "notes", ".csv", notes,
        lambda header, rows: csv_bytes(header, rows),
        {"clinical_notes": ("note_id", "enc_id", "note_type", "chief_complaint", "note_text")},
        {"note_id": "identifier", "enc_id": "identifier"},
        _csv_reader(),
        (
            Check("clinical_notes", "rows read", "same", lambda f: int(len(f["inferred"]))),  # type: ignore[arg-type]
            _bad("clinical_notes", "note types", lambda f: _bad_set(_t("note_type")(f), {v for v, _w in NOTE_TYPES})),
            _bad("clinical_notes", "no empty note", lambda f: int(_t("note_text")(f).isna().sum())),  # type: ignore[attr-defined]
            Check("clinical_notes", "some note runs over several lines", "present", lambda f: bool(_t("note_text")(f).str.contains("\n").any())),  # type: ignore[attr-defined]
            Check("clinical_notes", "some note keeps a de-identification token", "present", lambda f: bool(_t("note_text")(f).str.contains(r"\[NAME\]|\[DATE\]|\*\*\*").any())),  # type: ignore[attr-defined]
            Check("clinical_notes", "some complaint lists several, by commas", "present", lambda f: bool(_t("chief_complaint")(f).str.contains(",").any())),  # type: ignore[attr-defined]
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
            Check("excel_workbook", "survey_date reads as dates", "same", lambda f: str(_i("survey_date")(f).dtype)),  # type: ignore[attr-defined]
            _bad("surveys_pro", "Likert words", lambda f: _bad_set(_t("q1_word")(f), {v for v, _w in LIKERT})),
            _bad("surveys_pro", "scores 1 to 5 or -99", lambda f: sum(_bad_set(_i(c)(f).astype("Int64").astype(str), {"1", "2", "3", "4", "5", "-99"}) for c in ("q2_score", "q3_score"))),  # type: ignore[attr-defined]
            _bad("surveys_pro", "totals 2 to 10 or 999", lambda f: _bad_set(_i("scale_total")(f).astype("Int64").astype(str), {f"{k}" for k in range(2, 11)} | {"999"})),  # type: ignore[attr-defined]
            _bad("surveys_pro", "status words with NA and Not asked", lambda f: _bad_set(_t("q4_status")(f).fillna("NA"), {"Yes", "No", "NA", "Not asked"})),  # type: ignore[attr-defined]
        ),
    ),
    Table(
        "wearables", ".csv", wearables,
        lambda header, rows: csv_bytes(header, rows),
        {"wearables": ("device_id", "ts", "steps", "heart_rate", "activity")},
        {"device_id": "identifier", "steps": "measurement", "heart_rate": "measurement"},
        _csv_reader(),
        (
            _bad("wearables", "ts parses to the second", lambda f: _bad_dates(_t("ts")(f), "%Y-%m-%dT%H:%M:%S")),
            Check("wearables", "stamps keep their seconds", "present", lambda f: bool((__import__("pandas").to_datetime(_t("ts")(f), format="%Y-%m-%dT%H:%M:%S", errors="coerce").dt.second > 0).any())),
            _bad("wearables", "steps are not negative", lambda f: int((_i("steps")(f) < 0).sum())),  # type: ignore[operator]
            _bad("wearables", "activity levels", lambda f: _bad_set(_t("activity")(f), {"sedentary", "light", "moderate", "vigorous"})),
        ),
    ),
    Table(
        "genomics", ".csv", genomics,
        lambda header, rows: csv_bytes(header, rows),
        {"genomics": ("sample_id", "gene", "hgvs_c", "hgvs_p", "allele_freq", "zygosity", "classification")},
        {"sample_id": "identifier", "gene": "code", "hgvs_c": "code", "hgvs_p": "code", "allele_freq": "measurement"},
        _csv_reader(),
        (
            _bad("genomics", "gene symbols", lambda f: _bad_pattern(_t("gene")(f), r"[A-Z][A-Z0-9]*(-[A-Z0-9]+)?")),
            _bad("genomics", "HGVS c. strings", lambda f: _bad_pattern(_t("hgvs_c")(f), r"c\.-?\d+(_\d+)?([ACGT]>[ACGT]|del[ACGT]*|dup[ACGT]*|ins[ACGT]+)")),
            _bad("genomics", "HGVS p. strings", lambda f: _bad_pattern(_t("hgvs_p")(f), r"p\.([A-Z][a-z]{2}\d+([A-Z][a-z]{2}|del|fs)|=)")),
            _bad("genomics", "allele frequencies between 0 and 1", lambda f: int(((_i("allele_freq")(f) < 0) | (_i("allele_freq")(f) > 1)).sum())),  # type: ignore[operator]
            _bad("genomics", "clinical significance", lambda f: _bad_set(_t("classification")(f), {v for v, _w in CLASSES})),
        ),
    ),
    Table(
        "imaging", ".csv", imaging,
        lambda header, rows: csv_bytes(header, rows),
        {
            "imaging": ("accession", "patient_id", "modality", "body_part", "series_count"),
            "excel_serial_dates": ("study_date_serial",),
        },
        {"accession": "identifier", "patient_id": "identifier", "modality": "code", "study_date_serial": "excel-1900"},
        _csv_reader(),
        (
            _bad("excel_serial_dates", "serial dates read from 1899-12-30", lambda f: _serial_dates_bad(_t("study_date_serial")(f))),
            _bad("imaging", "accession numbers", lambda f: _bad_pattern(_t("accession")(f), r"ACC\d{8}")),
            _bad("imaging", "DICOM modality codes", lambda f: _bad_set(_t("modality")(f), {v for v, _w in MODALITIES})),
            _bad("imaging", "body parts", lambda f: _bad_set(_t("body_part")(f), {v for v, _w in BODY_PARTS})),
            _bad("imaging", "series counts are whole numbers", lambda f: _bad_pattern(_t("series_count")(f), r"\d+")),
        ),
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


def analyse(table: Table, path: pathlib.Path) -> "dict[str, tuple[str, object]]":
    """Run a table's analyst script on one file: per check, ('ok', value) or ('error', why).

    The read is one step of its own; when it fails, every check fails
    with it. The dtypes pandas infers are one 'same' check per column.
    """
    out: "dict[str, tuple[str, object]]" = {}
    try:
        frames = table.read(path)
    except Exception as failure:  # noqa: BLE001 -- what the analyst would have seen
        out["read"] = ("error", f"{type(failure).__name__}: {failure}"[:200])
        return out
    out["read"] = ("ok", True)
    inferred = frames["inferred"]
    for column in inferred.columns:  # type: ignore[attr-defined]
        out[f"dtype {column}"] = ("ok", str(inferred[column].dtype))  # type: ignore[index]
    for check in table.checks:
        try:
            out[check.name] = ("ok", check.run(frames))
        except Exception as failure:  # noqa: BLE001 -- what the analyst would have seen
            out[check.name] = ("error", f"{type(failure).__name__}: {failure}"[:200])
    return out


def analyst_failures(
    table: Table, real: "dict[str, tuple[str, object]]", twin: "dict[str, tuple[str, object]]"
) -> "list[tuple[str, str, str]]":
    """Per failing check of the twin: (kind, check, what went wrong)."""
    modes = {check.name: (check.kind, check.mode) for check in table.checks}
    every_kind = sorted(table.kinds)
    failures: "list[tuple[str, str, str]]" = []
    if twin.get("read", ("error", ""))[0] != "ok":
        for kind in every_kind:
            failures += [(kind, "read", f"the twin does not read: {twin['read'][1]}")]
        return failures
    for name in sorted(real):
        if name == "read":
            continue
        if name.startswith("dtype "):
            column = name[len("dtype "):]
            kind, mode = kind_of(table, column), "same"
        else:
            kind, mode = modes[name]
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


def answer_generally(table: Table, document: "dict") -> "tuple[list[dict], bool]":
    """Fill a questions file the way the person who holds the table would.

    The answers are GENERAL facts about the data: which column is a
    record number, which holds codes, how a date orders its day and
    month, that a pressure is two numbers in one cell, which character
    divides the columns. Nothing about the analysis. An answer the file
    does not offer is left blank, which keeps the reading synthtwin took.
    Returns what was asked -- column (or subject), the answers offered
    and the answer given -- and whether every question was general.
    """
    asked: "list[dict]" = []
    general = True
    file_facts = {"names", "comma", "semicolon" if table.name == "vitals" else "comma", "data"}
    for entry in _entries(document):
        offered = _offered(entry)
        column = f"{entry.get('column', '')}"
        if column:
            known = table.knows.get(column, "")
        else:
            known = next((answer for answer in offered if answer in file_facts), "")
        given = known if known in offered else ""
        entry["your_answer"] = given
        words = " ".join(
            [f"{entry.get('what_synthtwin_saw', '')}"]
            + [f"{choice.get('means', '')}" for choice in entry["answers_you_can_give"]]
        )
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

    real = analyse(table, source)
    made = analyse(table, twin)
    result["analyst_real_errors"] = sorted(
        name for name, (status, _value) in real.items() if status != "ok"
    )
    result["analyst"] = [list(failure) for failure in analyst_failures(table, real, made)]
    result["seconds"] = time.perf_counter() - started
    return result


# -- per kind, and the three KPIs --------------------------------------------

# WHO OWNS EACH KIND THAT FAILS TODAY, by the December plan's lanes
# (plan-dec PLAN-DEC.md section 3.1) or 'needs owner' where no lane
# covers it yet and the orchestrator names a new one. Filled from the
# baseline run of plan P4-D399; a kind that starts failing with no line
# here turns tests/test_health_zoo.py red, so no failure goes unowned.
NEEDS_OWNER = "needs owner"
WITHHELD = (
    NEEDS_OWNER,
    "a level fewer than 11 rows hold is written as 'group-N', or as a made-up code "
    "outside its system's pattern, so the analyst's code list or pattern meets it",
)
UNITS_AS_LABELS = (
    NEEDS_OWNER,
    "a number beside a unit ('172 cm', '36,9 °C', '5.4 mmol/L' over several units) is "
    "read as labels, its rarer values written as 'group-N'; the questions file offers "
    "no 'measurement' answer for it",
)
OWNERS: "dict[str, tuple[tuple[str, str], ...]]" = {
    "demographics": (WITHHELD,),
    "diagnoses": (WITHHELD,),
    "medication_orders": (WITHHELD,),
    "imaging": (WITHHELD,),
    "encounters": (
        ("DST", "the twin writes the offset not in force on its date (US Eastern)"),
    ),
    "labs": (
        UNITS_AS_LABELS,
        ("LM1", "a joined range '12.0-16.0' comes back as '12.0-16' and '70-99' as "
                "'70.0-99.0': validate misses its styles and counts"),
    ),
    "vitals": (
        UNITS_AS_LABELS,
        (NEEDS_OWNER, "a decimal-comma number beside a unit ('72,5 kg') is written as "
                      "made-up characters"),
    ),
    "flowsheet_long": (
        (NEEDS_OWNER, "a long table's value is read by its row name; the twin carries no "
                      "relation between the two columns (the between-columns program, "
                      "TRACKED T1 and T2)"),
    ),
    "clinical_notes": (
        (NEEDS_OWNER, "at small sizes the twin's notes hold no line break and no "
                      "de-identification token where the real notes do"),
    ),
    "surveys_pro": (
        (NEEDS_OWNER, "a missing code (-99) below a 1-to-5 score is read as part of the "
                      "range: the twin writes values between them, and no question asks "
                      "whether -99 means missing"),
    ),
}


def per_kind(results: "list[dict]") -> "dict[str, dict]":
    """Each kind's verdict: passed, the failing step, its misses and analyst failures."""
    kinds: "dict[str, dict]" = {}
    for result in results:
        table = table_named(result["table"])
        steps = result["steps"]
        failed_step = ""
        for step in ("profile", "answers", "generate", "validate"):
            if step not in steps:
                failed_step = failed_step or step
            elif steps[step]["exit"] not in (0, 3):
                failed_step = failed_step or step
        file_kinds = [kind for kind in table.kinds if kind in FILE_KINDS]
        for kind, columns in table.kinds.items():
            misses = [
                miss for miss in result["misses"]
                if miss[0] in columns
                or (not miss[0] and (kind in file_kinds or not file_kinds))
            ]
            analyst = [failure for failure in result["analyst"] if failure[0] == kind]
            step = failed_step
            if not step and misses:
                step = "validate"
            if not step and analyst:
                step = "analyst"
            kinds[kind] = {
                "table": table.name,
                "passed": not step,
                "failing_step": step,
                "misses": len(misses),
                "missed": sorted({f"{miss[0]}: {miss[1]}" for miss in misses}),
                "analyst_failures": [f"{failure[1]} -- {failure[2]}" for failure in analyst],
                "owners": sorted({owner for owner, _gap in OWNERS.get(kind, ())}) if step else [],
                "gaps": [f"{owner}: {gap}" for owner, gap in OWNERS.get(kind, ())] if step else [],
            }
    return {kind: kinds[kind] for kind in KINDS if kind in kinds}


def run_zoo(folder: pathlib.Path, n: int, seed: int = 20261016) -> "list[dict]":
    """Every catalogue table end to end, each in a folder of its own."""
    results: "list[dict]" = []
    for place in range(len(TABLES)):
        table = TABLES[place]
        results += [run_table(table, folder / table.name, n, seed + place)]
    return results


def zoo_measures(results: "list[dict]") -> "dict[str, dict]":
    """K-HZ-01 and K-HZ-02 from one run of the battery."""
    kinds = per_kind(results)
    passing = [kind for kind, verdict in kinds.items() if verdict["passed"]]
    failing = [kind for kind, verdict in kinds.items() if not verdict["passed"]]
    questions = [entry for result in results for entry in result.get("asked", [])]
    first = {
        "kinds": len(kinds),
        "kinds_passing_end_to_end": len(passing),
        "tables": len(results),
        "tables_profiled": sum(1 for r in results if r["steps"].get("answers", {}).get("exit") == 0),
        "tables_generated": sum(1 for r in results if r["steps"].get("generate", {}).get("exit") == 0),
        "questions_asked": len(questions),
        "questions_not_general": sum(1 for entry in questions if not entry["general"]),
        "analyst_errors_on_real": sum(len(r.get("analyst_real_errors", [])) for r in results),
    }
    second: "dict[str, object]" = {
        "kinds_failing": len(failing),
        "failing_kinds_without_owner": sum(1 for kind in failing if not kinds[kind]["owners"]),
        "validate_misses": sum(len(r["misses"]) for r in results),
        "analyst_failures": sum(len(r["analyst"]) for r in results),
    }
    for kind, verdict in kinds.items():
        second[f"misses_{kind}"] = verdict["misses"]
        second[f"analyst_failures_{kind}"] = len(verdict["analyst_failures"])
    return {"K-HZ-01": first, "K-HZ-02": second, "kinds": kinds}

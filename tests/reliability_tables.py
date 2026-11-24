"""Seven invented tables with seeded relationships, and a null table, for the reliability battery (K-RU-01).

Each table is drawn at run time from a seed and never committed (plan
D13; CLAUDE.md, "Test fixtures are built by seeded neutral scripts at
runtime"). Every name is an ordinary clinical word and every value is
drawn here, by the standard library's `random` alone, so a table is the
same bytes on every platform. The forms are the ones a health table can
hold -- a value written "<0.5", a decimal with no leading zero, a fixed
sentinel in a numeric copy of a text result, a unit that follows the
row's key, two clocks a fixed offset apart -- chosen by the builder; no
value, name or proportion comes from anywhere but this file.

THE SEVEN TABLES (`FILES` names the file each is written to; an analyst's
script reads its table by that name and nothing else):

* T1 `cohort.csv`, one row a patient: an age written at most 90, an
  integer physical-status class, yes/no comorbidity letters, a procedure
  group with a long tail of rare codes, a creatinine written "<0.5" below
  its detection limit, a weight missing more often with age, a
  multinomial anaesthetic technique, a complication with a curved age
  effect and a diabetes x smoking interaction, an overdispersed count, a
  length of stay, admission dates with a weekday pattern and a step in
  their monthly volume, and death with censored follow-up.
* T2 `visits.csv`, several rows a patient (a heavy-tailed count): an arm,
  a systolic pressure with a random intercept, a random slope over the
  visits, an arm x visit effect and serially correlated residuals, a
  blood loss that is zero on most rows and heavy-tailed otherwise, and two
  yes/no outcomes.
* T3 `charting.csv`, a long keyed table: the item key decides the kind of
  value (whole numbers, a pressure pair, a temperature in Celsius or
  Fahrenheit, a score, a choice list, `;`-joined multiple picks) and its
  unit; device rows are entered at once and charted at any minute, manual
  rows are heaped on five-minute marks and entered later.
* T4 `cases.csv`, paired clocks: scheduled start, in room, incision,
  close and out of room as minute stamps, the in-room time also in
  universal time a fixed six hours later, durations and delays that are
  computed from them (a delay can be zero or negative).
* T5 `orders.csv`, medication orders JOINABLE TO T1 at the same seed:
  patient keys taken from the cohort, no row for most patients and very
  many for a few, a drug with a long tail, a dose text whose unit follows
  the drug, ordered and given times, and an action word.
* T6 `labs.csv`, a long laboratory table: collected and received times
  (no lag on the bedside keys most of the time), a text result mixing
  numbers, "<" forms, words and decimals without a leading zero, a
  numeric copy holding the fixed sentinel 9999999 exactly where the text
  is not a number, a unit by key (two units and a case variant on some
  keys), a range text and a mostly empty integer flag.
* T9 `methods.csv` (the extended battery's alone, lane STATS-B), one row a
  patient: an age, a body-mass index and diabetes; a treatment given more
  often to the older, heavier and diabetic; an arterial and a cuff systolic
  pressure of one patient (the cuff reading higher by a bias, a proportional
  part and the body-mass index); two readers' grades of one finding; a
  risk score; an outcome in time whose hazard the treatment lowers less in
  the older (an interaction), censored; and admissions over an observed
  time of its own length.
* T7 `accounts.csv`, identifiers of other people: a guarantor shared by
  several accounts, a subscriber who is the patient exactly where the
  relationship is `Self`, the staff member who registered the account,
  beside a plan, a balance in money with zeros and negatives, and the day
  the account was opened.

And the battery's CONTROL TABLE, which is no shape of the queries:

* T8 `attributes.csv`, one row a patient: ten columns of every kind
  (labels, a yes/no letter, a count, a measurement, money, a date) each
  drawn from a stream of its own, so no two of them are related: the
  null table, on which a twin must not call more pairs related than
  chance does.

`header_rows(table, n, seed)` yields a table's header and rows;
`text(table, n, seed)` is its CSV text; `write(path, table, n, seed)`
streams it to disk. `TRUTHS[table]` states what each table's generator
sets, `KNOWS[table]` what the person who holds the table knows of each
column (the truthful answers, `tests/reliability_battery.py`), and
`PERSON[table]` the column that names the patient where one patient has
several rows ("" where every row is a patient of its own).
"""

from __future__ import annotations

import datetime
import math
import pathlib
import random
from typing import Iterator

TABLES = ("T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8")
# THE EXTENDED BATTERY'S OWN TABLE (lane STATS-B): read only by the further analysis families of
# `reliability_battery.EXTENDED_SCRIPTS`, never by K-RU-01's.
EXTENDED_TABLES = ("T9",)
ALL_TABLES = TABLES + EXTENDED_TABLES
FILES = {
    "T1": "cohort.csv",
    "T2": "visits.csv",
    "T3": "charting.csv",
    "T4": "cases.csv",
    "T5": "orders.csv",
    "T6": "labs.csv",
    "T7": "accounts.csv",
    "T8": "attributes.csv",
    "T9": "methods.csv",
}
NAMES = {
    "T1": "cohort, one row a patient",
    "T2": "visits, several rows a patient",
    "T3": "charting, a long table keyed by item",
    "T4": "cases, paired clocks and durations",
    "T5": "medication orders, joinable to the cohort",
    "T6": "laboratory results with a sentinel",
    "T7": "accounts with identifiers of other people",
    "T8": "the null table: ten unrelated columns (a control)",
    "T9": "methods, a cohort with two measuring methods, two readers, a treatment and an outcome in time",
}
PERSON = {"T1": "", "T2": "patient_id", "T3": "patient_id", "T4": "patient_id",
          "T5": "patient_id", "T6": "patient_id", "T7": "patient_id", "T8": "", "T9": ""}
SENTINEL = 9999999
UTC_OFFSET_MINUTES = 360
STUDY_START = datetime.date(2019, 1, 1)
STUDY_DAYS = 1826
STEP_DAY = datetime.date(2021, 7, 1)

T1_COLUMNS = ["patient_id", "admit_date", "age", "gender", "weight", "diabetes", "hypertension", "smoker", "risk_class",
              "proc_group", "creat", "technique", "complication", "n_medicines", "stay_days", "died", "fu_days"]
T2_COLUMNS = ["patient_id", "arm", "age", "visit", "visit_date", "sbp", "blood_loss_ml", "vasopressor",
              "hospitalized"]
T3_COLUMNS = ["patient_id", "item", "value", "unit", "charted_at", "entered_at", "device"]
T4_COLUMNS = ["case_no", "patient_id", "service", "risk_class", "emergency", "sched_start", "in_room", "incision",
              "close", "out_room", "in_room_utc", "recovery_min", "critical_care"]
T5_COLUMNS = ["order_id", "patient_id", "drug", "dose", "route", "ordered_at", "given_at", "action"]
T6_COLUMNS = ["patient_id", "test", "collected_at", "received_at", "result", "result_num", "unit", "ref_range",
              "abnormal"]
T7_COLUMNS = ["account_id", "patient_id", "guarantor_id", "subscriber_id", "relationship", "staff_id",
              "plan_type", "balance", "opened"]
NULL_COLUMNS = ("plan_type", "region", "paperless", "contact_pref", "language", "balance", "visits_yr",
                "risk_score", "copay", "opened")
T8_COLUMNS = ["patient_id", *NULL_COLUMNS]
T9_COLUMNS = ["patient_id", "age", "gender", "body_mass_index", "diabetes", "treated", "arterial_sbp", "cuff_sbp", "grade_first",
              "grade_second", "score", "outcome", "outcome_days", "admissions", "exposure_days"]
COLUMNS = {"T1": T1_COLUMNS, "T2": T2_COLUMNS, "T3": T3_COLUMNS, "T4": T4_COLUMNS, "T5": T5_COLUMNS,
           "T6": T6_COLUMNS, "T7": T7_COLUMNS, "T8": T8_COLUMNS, "T9": T9_COLUMNS}

# What the person who holds each table knows of its columns: the reading a
# question offers that is true of the column. 'identifier' for a record
# number, 'measurement' for a number that is a quantity, 'code' for a code
# whose figures are a label, 'keep' for anything else a question offers
# 'identifier' about. Columns not named here are answered by the rule in
# `tests/reliability_battery.py` (an age's Safe Harbor question `yes`,
# any other Safe Harbor question `no`).
KNOWS = {
    "T1": {"patient_id": "identifier", "age": "measurement", "weight": "measurement", "risk_class": "code",
           "n_medicines": "measurement", "stay_days": "measurement", "fu_days": "measurement",
           "proc_group": "code", "died": "code", "creat": "measurement"},
    "T2": {"patient_id": "identifier", "age": "measurement", "visit": "measurement", "sbp": "measurement",
           "blood_loss_ml": "measurement"},
    "T3": {"patient_id": "identifier", "value": "measurement"},
    "T4": {"case_no": "identifier", "patient_id": "identifier", "risk_class": "code", "recovery_min": "measurement"},
    "T5": {"order_id": "identifier", "patient_id": "identifier"},
    "T6": {"patient_id": "identifier", "result_num": "measurement", "abnormal": "code",
           "result": "measurement"},
    "T7": {"account_id": "identifier", "patient_id": "identifier", "guarantor_id": "identifier",
           "subscriber_id": "identifier", "staff_id": "identifier", "balance": "measurement"},
    "T8": {"patient_id": "identifier", "visits_yr": "measurement", "risk_score": "measurement",
           "balance": "measurement", "copay": "measurement"},
    "T9": {"patient_id": "identifier", "age": "measurement", "body_mass_index": "measurement", "arterial_sbp": "measurement",
           "cuff_sbp": "measurement", "score": "measurement", "outcome_days": "measurement",
           "admissions": "measurement", "exposure_days": "measurement"},
}
# The age columns, whose Safe Harbor question the person answers `yes`
# (ages past 89 are pooled at 90 by Safe Harbor's own rule).
AGES = {"T1": ("age",), "T2": ("age",), "T3": (), "T4": (), "T5": (), "T6": (), "T7": (), "T8": (), "T9": ("age",)}


def _logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _poisson(r: random.Random, lam: float) -> int:
    """A Poisson draw: inversion below 40, a rounded normal above (a test table's counts, not a method)."""
    if lam <= 0.0:
        return 0
    if lam >= 40.0:
        return max(0, int(round(r.gauss(lam, math.sqrt(lam)))))
    u = r.random()
    k, p = 0, math.exp(-lam)
    cumulative = p
    while u > cumulative and k < 1000:
        k += 1
        p *= lam / k
        cumulative += p
    return k


def _negbin(r: random.Random, mean: float, shape: float) -> int:
    """A negative binomial draw as a gamma-mixed Poisson: mean ``mean``, variance mean + mean^2 / shape."""
    return _poisson(r, r.gammavariate(shape, mean / shape))


def _ids(r: random.Random, count: int, prefix: str, figures: int) -> "list[str]":
    """``count`` distinct record numbers: a prefix and ``figures`` figures, drawn without replacement."""
    low = 10 ** (figures - 1)
    return [f"{prefix}{k}" for k in r.sample(range(low, 10 * low), count)]


def _stamp(moment: datetime.datetime) -> str:
    return moment.strftime("%Y-%m-%d %H:%M")


# -- T1: the cohort ----------------------------------------------------------

PROC_GROUPS = [f"PG{k:02d}" for k in range(1, 81)]
PROC_WEIGHTS = [1.0 / k ** 1.5 for k in range(1, 81)]
PROC_STAY = {"PG01": 0.0, "PG02": 0.25, "PG03": -0.2, "PG04": 0.4, "PG05": 0.1, "PG06": -0.1, "PG07": 0.3,
            "PG08": 0.15}
WEEKDAY_VOLUME = (1.1, 1.05, 1.0, 1.0, 0.95, 0.45, 0.35)
T1_TRUTH = {
    "complication": {"intercept": -2.4, "age": 0.02, "age_squared": 0.0005, "risk_class": 0.45, "diabetes": 0.45,
                     "smoker": 0.6, "diabetes_x_smoker": 0.5, "creat_high": 0.5},
    "log_stay": {"intercept": 1.0, "age": 0.006, "risk_class": 0.15, "complication": 0.45, "diabetes": 0.12,
                "weight": 0.007, "sd": 0.5},
    "log_hazard_death": {"age": 0.04, "risk_class": 0.35, "complication": 0.7, "diabetes": 0.3, "weibull_shape": 1.2,
                         "baseline_scale_days": 4335.0},
    "n_medicines_log_rate": {"intercept": 0.9, "age": 0.012, "diabetes": 0.35, "hypertension": 0.25, "gamma_shape": 2.0},
    "weight_missing": {"intercept": -2.2, "age": 0.04},
    "class_latent": {"age": 0.04, "diabetes": 0.9, "hypertension": 0.6, "weight": 0.017, "cuts": [-1.2, 1.0, 3.0, 5.2]},
    "technique": {"RA": {"intercept": -1.0, "class3": 0.4, "age": 0.015},
                  "SED": {"intercept": -2.0, "class3": 0.6, "age": 0.02}},
    "monthly_volume": {"growth_per_month": 0.008, "step_at": STEP_DAY.isoformat(), "step": 0.25,
                       "weekday": list(WEEKDAY_VOLUME)},
}


def _admit_day(r: random.Random) -> datetime.date:
    """An admission day: a monthly growth, a step on STEP_DAY and a weekday pattern, by rejection."""
    volume = T1_TRUTH["monthly_volume"]
    top = (1.0 + volume["growth_per_month"] * 60) * (1.0 + volume["step"]) * max(WEEKDAY_VOLUME)
    while True:
        day = STUDY_START + datetime.timedelta(days=r.randrange(STUDY_DAYS))
        months = (day.year - STUDY_START.year) * 12 + day.month - 1
        weight = ((1.0 + volume["growth_per_month"] * months) * (1.0 + volume["step"] if day >= STEP_DAY else 1.0)
                  * WEEKDAY_VOLUME[day.weekday()])
        if r.random() * top < weight:
            return day


def _cohort_rows(n: int, seed: int) -> "Iterator[list[str]]":
    """T1's rows; each patient's draws come from one stream, so a row depends on the seed and its place alone."""
    r = random.Random(f"T1-{seed}")
    ids = _ids(random.Random(f"T1-ids-{seed}"), n, "P", 7)
    for i in range(n):
        age_true = min(99.0, max(18.0, r.gauss(57.0, 17.0)))
        age = int(age_true)
        female = r.random() < 0.52
        weight_true = min(180.0, max(40.0, r.gauss(84.0 + 0.09 * (age - 57) - 2.4 * female, 15.0)))
        diabetes = r.random() < _logistic(-1.9 + 0.03 * (age - 57) + 0.03 * (weight_true - 84.0))
        hypertension = r.random() < _logistic(-0.6 + 0.05 * (age - 57) + 0.5 * diabetes)
        smoker = r.random() < min(0.4, max(0.03, 0.18 - 0.002 * (age - 57)))
        latent = (0.04 * (age - 57) + 0.9 * diabetes + 0.6 * hypertension + 0.017 * (weight_true - 84.0)
                  + math.log(1.0 / max(1e-12, r.random()) - 1.0))
        risk_class = 1 + sum(1 for cut in T1_TRUTH["class_latent"]["cuts"] if latent > cut)
        proc = r.choices(PROC_GROUPS, PROC_WEIGHTS)[0]
        creat_true = math.exp(r.gauss(-0.05 + 0.006 * (age - 57) + 0.15 * diabetes + 0.12 * (not female), 0.3))
        creat = "<0.5" if creat_true < 0.5 else f"{creat_true:.2f}"
        weight_missing = r.random() < _logistic(-2.2 + 0.04 * (age - 57))
        class3 = risk_class >= 3
        ra = math.exp(-1.0 + 0.4 * class3 + 0.015 * (age - 57))
        sed = math.exp(-2.0 + 0.6 * class3 + 0.02 * (age - 57))
        pick = r.random() * (1.0 + ra + sed)
        technique = "GA" if pick < 1.0 else ("RA" if pick < 1.0 + ra else "SED")
        c = T1_TRUTH["complication"]
        risk = (c["intercept"] + c["age"] * (age - 57) + c["age_squared"] * (age - 57) ** 2 + c["risk_class"] * (risk_class - 2)
                + c["diabetes"] * diabetes + c["smoker"] * smoker + c["diabetes_x_smoker"] * diabetes * smoker
                + c["creat_high"] * (creat_true > 1.3))
        complication = r.random() < _logistic(risk)
        m = T1_TRUTH["n_medicines_log_rate"]
        n_medicines = _negbin(r, math.exp(m["intercept"] + m["age"] * (age - 57) + m["diabetes"] * diabetes
                                     + m["hypertension"] * hypertension), m["gamma_shape"])
        s = T1_TRUTH["log_stay"]
        stay = math.exp(r.gauss(s["intercept"] + s["age"] * (age - 57) + s["risk_class"] * (risk_class - 2)
                               + s["complication"] * complication + s["diabetes"] * diabetes
                               + s["weight"] * (weight_true - 84.0) + PROC_STAY.get(proc, 0.05), s["sd"]))
        h = T1_TRUTH["log_hazard_death"]
        eta = (h["age"] * (age - 57) + h["risk_class"] * (risk_class - 2) + h["complication"] * complication
               + h["diabetes"] * diabetes)
        death = h["baseline_scale_days"] * (-math.log(max(1e-12, r.random())) / math.exp(eta)) ** (
            1.0 / h["weibull_shape"])
        censor = r.uniform(30.0, 1825.0)
        died = death <= censor
        fu = max(1, int(min(death, censor)))
        yield [
            ids[i], _admit_day(r).isoformat(), str(min(age, 90)), "F" if female else "M",
            "" if weight_missing else f"{weight_true:.1f}", "Y" if diabetes else "N", "Y" if hypertension else "N",
            "Y" if smoker else "N", str(risk_class), proc, creat, technique, "Y" if complication else "N",
            str(n_medicines), f"{max(0.1, stay):.1f}", "1" if died else "0", str(fu),
        ]


# -- T2: visits, several rows a patient ----------------------------------------

T2_TRUTH = {
    "sbp": {"intercept": 138.0, "visit": -0.4, "arm_b_x_visit": -0.8, "age": 0.15, "intercept_sd": 12.0,
            "slope_sd": 0.6, "residual_sd": 8.0, "ar1": 0.5},
    "rows_per_patient": {"mean_extra": 7.0, "gamma_shape": 1.0, "at_most": 60},
    "blood_loss": {"zero_share_a": 0.55, "zero_share_b": 0.65, "log_mean_a": 5.3, "log_mean_b": 5.0,
                   "log_sd": 1.0},
    "hospitalized": {"intercept": -2.2, "sbp": 0.035, "arm_a": 0.5, "patient_sd": 0.9},
}


def _visit_rows(n: int, seed: int) -> "Iterator[list[str]]":
    r = random.Random(f"T2-{seed}")
    id_stream = random.Random(f"T2-ids-{seed}")
    seen: "set[str]" = set()
    written = 0
    t = T2_TRUTH
    while written < n:
        pid = f"P{id_stream.randrange(1_000_000, 10_000_000)}"
        if pid in seen:
            continue
        seen.add(pid)
        visits = min(t["rows_per_patient"]["at_most"],
                     1 + _negbin(r, t["rows_per_patient"]["mean_extra"], t["rows_per_patient"]["gamma_shape"]))
        visits = min(visits, n - written)
        arm_b = r.random() < 0.5
        age = int(min(90.0, max(18.0, r.gauss(60.0, 12.0))))
        b0 = r.gauss(0.0, t["sbp"]["intercept_sd"])
        b1 = r.gauss(0.0, t["sbp"]["slope_sd"])
        u = r.gauss(0.0, t["hospitalized"]["patient_sd"])
        start = datetime.date(2021, 1, 1) + datetime.timedelta(days=r.randrange(911))
        day = start
        residual = r.gauss(0.0, t["sbp"]["residual_sd"])
        for k in range(1, visits + 1):
            if k > 1:
                day = day + datetime.timedelta(days=28 + r.randint(-3, 3))
                residual = t["sbp"]["ar1"] * residual + r.gauss(0.0, t["sbp"]["residual_sd"] * math.sqrt(0.75))
            sbp = (t["sbp"]["intercept"] + b0 + (t["sbp"]["visit"] + t["sbp"]["arm_b_x_visit"] * arm_b + b1) * (k - 1)
                   + t["sbp"]["age"] * (age - 60) + residual)
            loss_zero = r.random() < (t["blood_loss"]["zero_share_b"] if arm_b else t["blood_loss"]["zero_share_a"])
            loss = 0 if loss_zero else int(math.exp(r.gauss(
                t["blood_loss"]["log_mean_b"] if arm_b else t["blood_loss"]["log_mean_a"], t["blood_loss"]["log_sd"])))
            vaso = r.random() < _logistic(-3.2 + 0.002 * loss - 0.04 * (sbp - 138.0))
            hosp = r.random() < _logistic(t["hospitalized"]["intercept"] + t["hospitalized"]["sbp"] * (sbp - 138.0)
                                          + t["hospitalized"]["arm_a"] * (not arm_b) + u)
            yield [pid, "B" if arm_b else "A", str(age), str(k), day.isoformat(), str(int(round(sbp))), str(loss),
                   "Y" if vaso else "N", "Y" if hosp else "N"]
            written += 1


# -- T3: charting, keyed by item ---------------------------------------------------

ITEMS = ("HR", "RR", "SPO2", "TEMP", "BP", "PAIN", "LOC", "O2DEV")
ITEM_WEIGHTS = (0.22, 0.12, 0.18, 0.12, 0.18, 0.08, 0.05, 0.05)
DEVICE_ITEMS = ("HR", "SPO2")
LOC_WORDS = ("Alert", "Verbal", "Pain", "Unresponsive")
LOC_WEIGHTS = (0.82, 0.12, 0.04, 0.02)
O2_WORDS = ("Room air", "Nasal cannula", "Mask", "High flow")
T3_TRUTH = {
    "hr": {"mean": 82.0, "patient_sd": 10.0, "per_hour": -0.08, "sd": 8.0},
    "bp": {"systolic_mean": 125.0, "patient_sd": 15.0, "sd": 10.0, "diastolic_slope": 0.55,
           "diastolic_intercept": 10.0, "diastolic_sd": 6.0},
    "temp_celsius": {"mean": 37.0, "sd": 0.45, "fahrenheit_share": 0.3},
    "lag_minutes": {"device": 0.0, "manual_mean": 12.0},
    "manual_on_five_minutes": 0.8,
}


def _charting_rows(n: int, seed: int) -> "Iterator[list[str]]":
    r = random.Random(f"T3-{seed}")
    id_stream = random.Random(f"T3-ids-{seed}")
    seen: "set[str]" = set()
    written = 0
    t = T3_TRUTH
    while written < n:
        pid = f"P{id_stream.randrange(1_000_000, 10_000_000)}"
        if pid in seen:
            continue
        seen.add(pid)
        count = min(n - written, min(300, 1 + _negbin(r, 14.0, 0.8)))
        start = datetime.datetime(2022, 1, 1) + datetime.timedelta(minutes=r.randrange(700 * 24 * 60))
        hours = r.uniform(12.0, 96.0)
        hr_mean = r.gauss(t["hr"]["mean"], t["hr"]["patient_sd"])
        sbp_mean = r.gauss(t["bp"]["systolic_mean"], t["bp"]["patient_sd"])
        spo2_base = r.gauss(96.0, 1.5)
        fahrenheit = r.random() < t["temp_celsius"]["fahrenheit_share"]
        offsets = sorted(r.uniform(0.0, hours) for _ in range(count))
        for offset in offsets:
            item = r.choices(ITEMS, ITEM_WEIGHTS)[0]
            device = item in DEVICE_ITEMS or (item == "BP" and r.random() < 0.5)
            moment = start + datetime.timedelta(minutes=int(offset * 60))
            if not device and r.random() < t["manual_on_five_minutes"]:
                moment = moment - datetime.timedelta(minutes=moment.minute % 5)
            lag = 0 if device else int(r.expovariate(1.0 / t["lag_minutes"]["manual_mean"]))
            if item == "HR":
                value, unit = str(int(round(hr_mean + t["hr"]["per_hour"] * offset + r.gauss(0.0, t["hr"]["sd"])))), "bpm"
            elif item == "RR":
                value, unit = str(max(6, int(round(r.gauss(17.0, 3.0))))), "/min"
            elif item == "SPO2":
                value, unit = str(min(100, int(round(spo2_base + r.gauss(0.0, 1.5))))), "%"
            elif item == "TEMP":
                celsius = r.gauss(t["temp_celsius"]["mean"], t["temp_celsius"]["sd"])
                value = f"{celsius * 9.0 / 5.0 + 32.0:.1f}" if fahrenheit else f"{celsius:.1f}"
                unit = ("F" if r.random() < 0.8 else "degF") if fahrenheit else "C"
            elif item == "BP":
                systolic = int(round(sbp_mean + r.gauss(0.0, t["bp"]["sd"])))
                diastolic = int(round(t["bp"]["diastolic_intercept"] + t["bp"]["diastolic_slope"] * systolic
                                      + r.gauss(0.0, t["bp"]["diastolic_sd"])))
                value, unit = f"{systolic}/{diastolic}", "mmHg"
            elif item == "PAIN":
                value, unit = str(min(10, _poisson(r, 2.5))), "score"
            elif item == "LOC":
                value, unit = r.choices(LOC_WORDS, LOC_WEIGHTS)[0], ""
            else:
                picks = sorted(r.sample(range(1, 4), 1 if r.random() < 0.8 else 2))
                value = "Room air" if r.random() < 0.55 else ";".join(O2_WORDS[k] for k in picks)
                unit = ""
            yield [pid, item, value, unit, _stamp(moment), _stamp(moment + datetime.timedelta(minutes=lag)),
                   "Y" if device else "N"]
            written += 1


# -- T4: cases, paired clocks --------------------------------------------------------

SERVICES = ("GEN", "ORTHO", "URO", "GYN", "CARD", "SPINE", "ENT", "VASC", "PLAST")
SERVICE_WEIGHTS = (0.25, 0.22, 0.1, 0.1, 0.08, 0.07, 0.08, 0.06, 0.04)
SERVICE_LOG_MINUTES = {"GEN": 4.3, "ORTHO": 4.5, "URO": 4.0, "GYN": 4.2, "CARD": 5.2, "SPINE": 5.0,
                       "ENT": 4.1, "VASC": 4.9, "PLAST": 4.4}
T4_TRUTH = {
    "log_duration": {"risk_class": 0.1, "emergency": 0.25, "sd": 0.45, "by_service": SERVICE_LOG_MINUTES},
    "critical_care": {"intercept": -4.0, "duration_hours": 0.36, "risk_class": 0.6, "emergency": 0.8},
    "utc_offset_minutes": UTC_OFFSET_MINUTES,
    "order": "sched_start, in_room <= incision <= close <= out_room",
}


def _case_rows(n: int, seed: int) -> "Iterator[list[str]]":
    r = random.Random(f"T4-{seed}")
    patients = _ids(random.Random(f"T4-ids-{seed}"), max(1, int(n * 0.6)), "P", 7)
    cases = _ids(random.Random(f"T4-cases-{seed}"), n, "C", 8)
    t = T4_TRUTH
    for i in range(n):
        service = r.choices(SERVICES, SERVICE_WEIGHTS)[0]
        emergency = r.random() < 0.12
        risk_class = min(5, max(1, int(round(r.gauss(2.3 + 0.6 * emergency, 0.8)))))
        day = datetime.date(2022, 1, 1) + datetime.timedelta(days=r.randrange(730))
        if not emergency:
            while day.weekday() >= 5:
                day = day + datetime.timedelta(days=1)
        slot = r.randrange(0, 36) if emergency else r.choices(range(0, 36), [6.0] + [1.0] * 35)[0]
        sched = datetime.datetime(day.year, day.month, day.day, 7, 30) + datetime.timedelta(minutes=15 * slot)
        delay = 0 if r.random() < 0.18 else int(round(r.gauss(9.0, 14.0)))
        in_room = sched + datetime.timedelta(minutes=delay)
        incision = in_room + datetime.timedelta(minutes=max(5, int(round(r.gauss(25.0, 8.0)))))
        minutes = math.exp(r.gauss(t["log_duration"]["by_service"][service] + t["log_duration"]["risk_class"] * (risk_class - 2)
                                   + t["log_duration"]["emergency"] * emergency, t["log_duration"]["sd"]))
        close = incision + datetime.timedelta(minutes=max(5, int(round(minutes))))
        out_room = close + datetime.timedelta(minutes=r.randint(5, 20))
        utc = in_room + datetime.timedelta(minutes=UTC_OFFSET_MINUTES)
        recovery = int(math.exp(r.gauss(4.2 + 0.08 * (risk_class - 2) + 0.15 * (minutes > 180), 0.4)))
        c = t["critical_care"]
        critical_care = r.random() < _logistic(c["intercept"] + c["duration_hours"] * minutes / 60.0 + c["risk_class"] * (risk_class - 2)
                                     + c["emergency"] * emergency)
        yield [cases[i], r.choice(patients), service, str(risk_class), "Y" if emergency else "N", _stamp(sched),
               _stamp(in_room), _stamp(incision), _stamp(close), _stamp(out_room), utc.strftime("%Y-%m-%dT%H:%MZ"),
               str(recovery), "Y" if critical_care else "N"]


# -- T5: medication orders, joinable to T1 ---------------------------------------------

# Each drug: its unit, its route, the amounts it is ordered in, its class.
DRUG_TABLE = {
    "cefazolin": ("g", "IV", ("1", "2"), "antibiotic"),
    "ondansetron": ("mg", "IV", ("4",), "antiemetic"),
    "acetaminophen": ("mg", "PO", ("650", "1000"), "analgesic"),
    "heparin": ("units", "SC", ("5000",), "anticoagulant"),
    "fentanyl": ("mcg", "IV", ("25", "50", "100"), "opioid"),
    "oxycodone": ("mg", "PO", ("5", "10"), "opioid"),
    "pantoprazole": ("mg", "IV", ("40",), "other"),
    "metoprolol": ("mg", "PO", ("25", "50"), "cardiac"),
    "insulin lispro": ("units", "SC", ("2", "4", "6", "8"), "insulin"),
    "enoxaparin": ("mg", "SC", ("40",), "anticoagulant"),
    "hydromorphone": ("mg", "IV", ("0.2", "0.5", "1"), "opioid"),
    "morphine": ("mg", "IV", ("2", "4"), "opioid"),
    "furosemide": ("mg", "IV", ("20", "40"), "cardiac"),
    "prednisone": ("mg", "IV", ("4", "8"), "other"),
    "vancomycin": ("mg", "IV", ("1000", "1250"), "antibiotic"),
    "ketorolac": ("mg", "IV", ("15", "30"), "analgesic"),
    "magnesium sulfate": ("g", "IV", ("2",), "electrolyte"),
    "potassium chloride": ("mEq", "PO", ("20", "40"), "electrolyte"),
    "lorazepam": ("mg", "IV", ("0.5", "1"), "other"),
    "docusate": ("mg", "PO", ("100",), "other"),
    "senna": ("mg", "PO", ("8.6", "17.2"), "other"),
    "famotidine": ("mg", "PO", ("20",), "other"),
    "amlodipine": ("mg", "PO", ("5", "10"), "cardiac"),
    "labetalol": ("mg", "IV", ("10", "20"), "cardiac"),
    "cefepime": ("g", "IV", ("2",), "antibiotic"),
    "metronidazole": ("mg", "IV", ("500",), "antibiotic"),
    "atorvastatin": ("mg", "PO", ("40", "80"), "cardiac"),
    "gabapentin": ("mg", "PO", ("300",), "analgesic"),
    "melatonin": ("mg", "PO", ("3",), "other"),
    "naloxone": ("mg", "IV", ("0.4",), "other"),
}
DRUG_NAMES = tuple(DRUG_TABLE)
DRUG_WEIGHTS = tuple(1.0 / (k + 1) ** 1.1 for k in range(len(DRUG_NAMES)))
ACTIONS = ("Given", "Held", "Refused", "Missed")
T5_TRUTH = {
    "orders_any": {"intercept": -1.4, "age": 0.03, "diabetes": 0.6},
    "orders_count": {"log_mean": 1.6, "diabetes": 0.4, "age": 0.01, "gamma_shape": 0.5},
    "action_given": {"opioid": 0.72, "other": 0.88},
    "given_lag_minutes": {"IV": 20.0, "PO": 45.0, "SC": 35.0},
    "unit_by_drug": "each drug is written in one unit",
}


def _order_rows(n: int, seed: int) -> "Iterator[list[str]]":
    """T5's rows for the cohort T1 draws at the same size and seed: its patients, ages and diabetes letters."""
    r = random.Random(f"T5-{seed}")
    t = T5_TRUTH
    order_ids = _ids(random.Random(f"T5-orders-{seed}"), 3 * n + 1000, "O", 9)
    used = 0
    for row in _cohort_rows(n, seed):
        pid, admit, age, diabetes = row[0], row[1], int(row[2]), row[5] == "Y"
        anything = r.random() < _logistic(t["orders_any"]["intercept"] + t["orders_any"]["age"] * (age - 57)
                                          + t["orders_any"]["diabetes"] * diabetes)
        if not anything:
            continue
        count = 1 + _negbin(r, math.exp(t["orders_count"]["log_mean"] + t["orders_count"]["diabetes"] * diabetes
                                        + t["orders_count"]["age"] * (age - 57)), t["orders_count"]["gamma_shape"])
        count = min(count, 3 * n + 1000 - used)
        start = datetime.datetime.fromisoformat(admit) + datetime.timedelta(minutes=r.randrange(8 * 60, 20 * 60))
        for _k in range(count):
            drug = r.choices(DRUG_NAMES, DRUG_WEIGHTS)[0]
            unit, route, amounts, kind = DRUG_TABLE[drug]
            ordered = start + datetime.timedelta(minutes=r.randrange(0, 5 * 24 * 60))
            given_share = t["action_given"]["opioid"] if kind == "opioid" else t["action_given"]["other"]
            action = "Given" if r.random() < given_share else r.choices(ACTIONS[1:], (0.5, 0.3, 0.2))[0]
            lag = int(r.expovariate(1.0 / t["given_lag_minutes"][route]))
            given = _stamp(ordered + datetime.timedelta(minutes=lag)) if action == "Given" else ""
            yield [order_ids[used], pid, drug, f"{r.choice(amounts)} {unit}", route, _stamp(ordered), given, action]
            used += 1


# -- T6: laboratory results with a sentinel ------------------------------------------------

# Each test: (unit, range text, its share of rows).
TESTS = {
    "GLU": ("mg/dL", "70-99", 0.2), "K": ("mmol/L", "3.5-5.1", 0.15), "SOD": ("mmol/L", "135-145", 0.12),
    "CREAT": ("mg/dL", "0.6-1.2", 0.14), "HGB": ("g/dL", "12.0-16.0", 0.12), "TROP": ("ng/mL", "<0.04", 0.06),
    "UPROT": ("", "NEG", 0.05), "LACT": ("mmol/L", "0.5-2.0", 0.05), "INR": ("", "0.8-1.2", 0.04),
    "CRP": ("mg/L", "<5.0", 0.04),
}
RARE_TESTS = tuple(f"X{k:02d}" for k in range(1, 21))
BEDSIDE_TESTS = ("GLU", "LACT")
PROTEIN_WORDS = ("NEG", "TRACE", "1+", "2+", "3+")
T6_TRUTH = {
    "glucose": {"mean": 112.0, "patient_sd": 18.0, "sd": 14.0, "per_day": 1.5, "mmol_share": 0.05},
    "potassium": {"mean": 4.1, "patient_sd": 0.25, "sd": 0.3, "upper_case_unit_share": 0.1},
    "sentinel": SENTINEL,
    "bedside_zero_lag_share": 0.4,
    "lag_minutes_mean": 25.0,
}


def _number_text(value: float, places: int, leading_dot: bool) -> str:
    written = f"{value:.{places}f}"
    if leading_dot and written.startswith("0."):
        return written[1:]
    return written


def _is_number(text: str) -> bool:
    try:
        float(text)
    except ValueError:
        return False
    return True


def _lab_rows(n: int, seed: int) -> "Iterator[list[str]]":
    r = random.Random(f"T6-{seed}")
    id_stream = random.Random(f"T6-ids-{seed}")
    seen: "set[str]" = set()
    names = tuple(TESTS) + ("RARE",)
    weights = tuple(spec[2] for spec in TESTS.values()) + (0.03,)
    written = 0
    t = T6_TRUTH
    while written < n:
        pid = f"P{id_stream.randrange(1_000_000, 10_000_000)}"
        if pid in seen:
            continue
        seen.add(pid)
        count = min(n - written, min(200, 1 + _negbin(r, 9.0, 0.9)))
        start = datetime.datetime(2022, 3, 1) + datetime.timedelta(minutes=r.randrange(600 * 24 * 60))
        glucose_mean = r.gauss(t["glucose"]["mean"], t["glucose"]["patient_sd"])
        potassium_mean = r.gauss(t["potassium"]["mean"], t["potassium"]["patient_sd"])
        creat_mean = math.exp(r.gauss(-0.05, 0.3))
        hgb_mean = r.gauss(12.5, 1.4)
        offsets = sorted(r.uniform(0.0, 10.0 * 24 * 60) for _ in range(count))
        for offset in offsets:
            test = r.choices(names, weights)[0]
            if test == "RARE":
                test = r.choices(RARE_TESTS, [1.0 / (k + 1) for k in range(len(RARE_TESTS))])[0]
            collected = start + datetime.timedelta(minutes=int(offset))
            day = offset / (24 * 60)
            bedside_now = test in BEDSIDE_TESTS and r.random() < t["bedside_zero_lag_share"]
            lag = 0 if bedside_now else 1 + int(r.expovariate(1.0 / t["lag_minutes_mean"]))
            unit, ref, _share = TESTS.get(test, ("U/L", "", 0.0))
            if test == "GLU":
                glucose = glucose_mean + t["glucose"]["per_day"] * day + r.gauss(0.0, t["glucose"]["sd"])
                if r.random() < t["glucose"]["mmol_share"]:
                    result, unit, ref = f"{glucose / 18.0:.1f}", "mmol/L", "3.9-5.5"
                else:
                    result = ">500" if glucose > 500 else str(int(round(glucose)))
            elif test == "K":
                result = f"{potassium_mean + r.gauss(0.0, t['potassium']['sd']):.1f}"
                if r.random() < t["potassium"]["upper_case_unit_share"]:
                    unit = "MMOL/L"
            elif test == "SOD":
                result = str(int(round(r.gauss(139.0, 3.0))))
            elif test == "CREAT":
                result = _number_text(creat_mean * math.exp(r.gauss(0.0, 0.1)), 2, r.random() < 0.5)
            elif test == "HGB":
                result = f"{hgb_mean + r.gauss(0.0, 0.6):.1f}"
            elif test == "TROP":
                value = math.exp(r.gauss(-4.6, 1.2))
                result = "<0.01" if value < 0.01 else _number_text(value, 3, True)
            elif test == "UPROT":
                result = r.choices(PROTEIN_WORDS, (0.7, 0.12, 0.1, 0.05, 0.03))[0]
            elif test == "LACT":
                result = "see comment" if r.random() < 0.02 else f"{math.exp(r.gauss(0.2, 0.4)):.1f}"
            elif test == "INR":
                result = f"{math.exp(r.gauss(0.05, 0.12)):.1f}"
            elif test == "CRP":
                value = math.exp(r.gauss(1.5, 1.2))
                result = "<0.5" if value < 0.5 else f"{value:.1f}"
            else:
                result = f"{math.exp(r.gauss(3.0 + RARE_TESTS.index(test) * 0.1, 0.5)):.0f}"
            numeric = _is_number(result)
            result_num = result if numeric else str(SENTINEL)
            abnormal = ""
            if numeric and "-" in ref:
                low, high = (float(part) for part in ref.split("-"))
                if not low <= float(result) <= high:
                    abnormal = "1"
            yield [pid, test, _stamp(collected), _stamp(collected + datetime.timedelta(minutes=lag)), result,
                   result_num, unit, ref, abnormal]
            written += 1


# -- T7: accounts, identifiers of other people; T8: the null table ---------------------------

RELATIONSHIPS = ("Self", "Spouse", "Child", "Other")
RELATIONSHIP_WEIGHTS = (0.6, 0.2, 0.15, 0.05)
PLAN_TYPES = ("HMO", "PPO", "EPO", "POS", "Medicaid", "Medicare", "Self-pay")
REGIONS = ("North", "South", "East", "West", "Central", "Coast", "Valley", "Mountain")
CONTACTS = ("Mail", "Phone", "Portal", "Email")
LANGUAGE_WORDS = ("English", "Spanish", "Other")
COPAYS = ("0.00", "10.00", "20.00", "35.00", "50.00")
T7_TRUTH = {
    "rule": "subscriber_id equals patient_id exactly where relationship is Self",
    "self_share": 0.6,
}
T8_TRUTH = {"null_columns": list(NULL_COLUMNS), "rule": "no two of the ten columns are related"}


def _null_cells(s: "dict[str, random.Random]") -> "dict[str, str]":
    """One row of the ten unrelated columns, each from its own stream."""
    balance_draw = s["balance"].random()
    if balance_draw < 0.15:
        balance = "0.00"
    elif balance_draw < 0.2:
        balance = f"-{s['balance'].uniform(1.0, 300.0):.2f}"
    else:
        balance = f"{math.exp(s['balance'].gauss(5.0, 1.2)):.2f}"
    opened = datetime.date(2015, 1, 1) + datetime.timedelta(days=s["opened"].randrange(3287))
    return {
        "plan_type": s["plan_type"].choices(PLAN_TYPES, (0.25, 0.2, 0.05, 0.05, 0.15, 0.25, 0.05))[0],
        "region": s["region"].choice(REGIONS),
        "paperless": "Y" if s["paperless"].random() < 0.4 else "N",
        "contact_pref": s["contact_pref"].choices(CONTACTS, (0.2, 0.3, 0.35, 0.15))[0],
        "language": s["language"].choices(LANGUAGE_WORDS, (0.8, 0.15, 0.05))[0],
        "balance": balance,
        "visits_yr": str(_negbin(s["visits_yr"], 3.0, 1.5)),
        "risk_score": f"{min(100.0, max(0.0, s['risk_score'].gauss(50.0, 15.0))):.1f}",
        "copay": s["copay"].choices(COPAYS, (0.2, 0.3, 0.25, 0.15, 0.1))[0],
        "opened": opened.isoformat(),
    }


def _attribute_rows(n: int, seed: int) -> "Iterator[list[str]]":
    """T8's rows, one a patient; each of the ten columns has a stream of its own, so no two of them can be related."""
    streams = {name: random.Random(f"T8-{name}-{seed}") for name in NULL_COLUMNS}
    patients = _ids(random.Random(f"T8-patients-{seed}"), n, "P", 7)
    for i in range(n):
        cells = _null_cells(streams)
        yield [patients[i], *(cells[name] for name in NULL_COLUMNS)]


def _account_rows(n: int, seed: int) -> "Iterator[list[str]]":
    """T7's rows: accounts naming their patient, a guarantor, a subscriber and a staff member."""
    streams = {name: random.Random(f"T7-{name}-{seed}") for name in NULL_COLUMNS}
    r = random.Random(f"T7-{seed}")
    patients = _ids(random.Random(f"T7-patients-{seed}"), max(1, int(n * 0.75)), "P", 7)
    others = _ids(random.Random(f"T7-others-{seed}"), max(1, n // 2), "Q", 7)
    guarantors = _ids(random.Random(f"T7-guarantors-{seed}"), max(1, n // 3), "G", 7)
    staff = _ids(random.Random(f"T7-staff-{seed}"), 40, "E", 5)
    staff_weights = [1.0 / (k + 1) for k in range(40)]
    accounts = _ids(random.Random(f"T7-accounts-{seed}"), n, "A", 9)
    for i in range(n):
        pid = r.choice(patients)
        relation = r.choices(RELATIONSHIPS, RELATIONSHIP_WEIGHTS)[0]
        subscriber = pid if relation == "Self" else r.choice(others)
        guarantor = guarantors[min(len(guarantors) - 1, int(r.paretovariate(1.2)) - 1)] if r.random() < 0.3 \
            else r.choice(guarantors)
        cells = _null_cells(streams)
        yield [accounts[i], pid, guarantor, subscriber, relation, r.choices(staff, staff_weights)[0],
               cells["plan_type"], cells["balance"], cells["opened"]]


# -- T9: two measuring methods, two readers, a treatment and an outcome in time (lane STATS-B) ----------------------

GRADES = ("none", "mild", "moderate", "severe")
T9_TRUTH = {
    "treated": {"intercept": -0.3, "age": 0.03, "mass_index": 0.08, "diabetes": 0.6},
    "arterial_sbp": {"mean": 128.0, "age": 0.4, "diabetes": 5.0, "sd": 16.0},
    "cuff_minus_arterial": {"bias": 3.0, "proportional": 0.06, "mass_index": 0.25, "sd": 6.0},
    "grades": {"age": 0.02, "diabetes": 0.4, "reader_sd": 0.45, "reader_2_shift": 0.15, "cuts": [-0.5, 0.5, 1.4]},
    "score": {"base": 4.0, "age": 0.05, "diabetes": 1.2, "mass_index": 0.08, "sd": 1.6},
    "log_hazard": {"treated": -0.6, "age": 0.03, "diabetes": 0.5, "score": 0.15, "treated_x_age": 0.025,
                   "weibull_shape": 1.1, "scale_days": 2600.0, "censor_days": [90, 1095]},
    "admissions_log_rate_a_year": {"intercept": -0.4, "age": 0.02, "diabetes": 0.5, "treated": -0.3,
                                   "gamma_shape": 1.5, "exposure_days": [30, 730]},
}


def _method_rows(n: int, seed: int) -> "Iterator[list[str]]":
    """T9's rows, one a patient: each patient's draws from one stream, so a row depends on the seed and its place alone."""
    r = random.Random(f"T9-{seed}")
    ids = _ids(random.Random(f"T9-ids-{seed}"), n, "P", 7)
    t = T9_TRUTH
    for i in range(n):
        age = int(min(90.0, max(18.0, r.gauss(62.0, 14.0))))
        female = r.random() < 0.5
        mass = min(55.0, max(16.0, r.gauss(28.0 + 0.03 * (age - 62), 5.0)))
        diabetes = r.random() < _logistic(-2.0 + 0.04 * (age - 62) + 0.1 * (mass - 28.0))
        p = t["treated"]
        treated = r.random() < _logistic(p["intercept"] + p["age"] * (age - 62) + p["mass_index"] * (mass - 28.0)
                                         + p["diabetes"] * diabetes)
        a = t["arterial_sbp"]
        arterial = int(round(r.gauss(a["mean"] + a["age"] * (age - 62) + a["diabetes"] * diabetes, a["sd"])))
        c = t["cuff_minus_arterial"]
        cuff = int(round(arterial + c["bias"] + c["proportional"] * (arterial - 128) + c["mass_index"] * (mass - 28.0)
                         + r.gauss(0.0, c["sd"])))
        g = t["grades"]
        latent = r.gauss(0.0, 1.0) + g["age"] * (age - 62) + g["diabetes"] * diabetes
        first = sum(1 for cut in g["cuts"] if latent + r.gauss(0.0, g["reader_sd"]) > cut)
        second = sum(1 for cut in g["cuts"] if latent + g["reader_2_shift"] + r.gauss(0.0, g["reader_sd"]) > cut)
        sc = t["score"]
        score = int(round(min(10.0, max(0.0, sc["base"] + sc["age"] * (age - 62) + sc["diabetes"] * diabetes
                                        + sc["mass_index"] * (mass - 28.0) + r.gauss(0.0, sc["sd"])))))
        h = t["log_hazard"]
        eta = (h["treated"] * treated + h["age"] * (age - 62) + h["diabetes"] * diabetes + h["score"] * (score - 4)
               + h["treated_x_age"] * treated * (age - 62))
        event = h["scale_days"] * (-math.log(max(1e-12, r.random())) / math.exp(eta)) ** (1.0 / h["weibull_shape"])
        censor = r.uniform(*h["censor_days"])
        happened = event <= censor
        m = t["admissions_log_rate_a_year"]
        exposure = r.randint(*m["exposure_days"])
        rate = math.exp(m["intercept"] + m["age"] * (age - 62) + m["diabetes"] * diabetes + m["treated"] * treated)
        admissions = _negbin(r, rate * exposure / 365.0, m["gamma_shape"])
        yield [ids[i], str(age), "F" if female else "M", f"{mass:.1f}", "Y" if diabetes else "N",
               "Y" if treated else "N", str(arterial), str(cuff), GRADES[first], GRADES[second], str(score),
               "Y" if happened else "N", str(max(1, int(min(event, censor)))), str(admissions), str(exposure)]


_ROWS = {"T1": _cohort_rows, "T2": _visit_rows, "T3": _charting_rows, "T4": _case_rows, "T5": _order_rows,
         "T6": _lab_rows, "T7": _account_rows, "T8": _attribute_rows, "T9": _method_rows}
TRUTHS = {"T1": T1_TRUTH, "T2": T2_TRUTH, "T3": T3_TRUTH, "T4": T4_TRUTH, "T5": T5_TRUTH, "T6": T6_TRUTH,
          "T7": T7_TRUTH, "T8": T8_TRUTH, "T9": T9_TRUTH}


def header_rows(table: str, n: int, seed: int) -> "tuple[list[str], Iterator[list[str]]]":
    """A table's header and its rows at size ``n`` (T5: the orders of T1's ``n`` patients) and ``seed``.

    Deterministic: the same table, size and seed give the same rows on
    every platform (the standard library's Mersenne Twister, seeded with a
    text). Raises KeyError for a table not in `TABLES`.
    """
    return list(COLUMNS[table]), _ROWS[table](n, seed)


def _line(cells: "list[str]") -> str:
    return ",".join(f'"{cell}"' if ("," in cell or '"' in cell) else cell for cell in cells) + "\n"


def text(table: str, n: int, seed: int) -> str:
    """The table's CSV text: a header line and one line a row, comma-separated, `\\n` line ends."""
    header, rows = header_rows(table, n, seed)
    return _line(header) + "".join(_line(row) for row in rows)


def write(path: "str | pathlib.Path", table: str, n: int, seed: int) -> int:
    """Stream the table to ``path`` (one row in memory at a time); the data rows written."""
    header, rows = header_rows(table, n, seed)
    count = 0
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(_line(header))
        for row in rows:
            handle.write(_line(row))
            count += 1
    return count

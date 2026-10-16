"""Six seeded tables with known statistical truths, for the analyst battery (plan P4-D398).

Each table is built at run time from a seed and never committed (plan
D13; CLAUDE.md, "Test fixtures are built by seeded neutral scripts at
runtime"). Each is invented: the column names are ordinary clinical
words and every value is drawn here. The formats are clean on purpose --
E0's tables test formats; these test statistics, so a failure here is a
statistical one.

* ST1, a patient cohort (17 columns, one row per patient): a J-shaped
  blood pressure in age, a death risk hinged at 60, thresholds (diabetes
  at glucose 126, ventilation at lactate 4), a ventilation x age-over-75
  interaction, a diabetes x current-smoker interaction of opposite sign
  (a relation of three columns), a rare readmission driven by ward x
  diabetes, glucose and CRP missing depending on other columns, a cost
  with 30 % zeros, an overdispersed count of procedures and Weibull
  survival with known hazard ratios. Its draws follow the S2 design
  probe's cohort, column for column.
* ST2, several rows per subject: a random intercept (ICC 0.64 / 0.89),
  an arm x visit slope of -0.15 and dropout that depends on the previous
  value.
* ST3, a registry with dates: a stage effect that fades after the first
  year (a non-proportional hazard), censoring that depends on the centre,
  a competing event that depends on age, and every end date after its
  entry date.
* ST4, claims: 500 diagnosis-like codes under 20 chapters, chapter
  effects on visits and on a 0.5 % outcome, code effects on purpose only
  on codes too rare to publish, a pure three-way parity effect (flat
  pair margins) and a dose that is weight times the dose rate.
* ST5, the null table: fifteen of ST1's columns, each drawn from its own
  ST1 stream, so no two are associated.
* ST6, curves that turn: ST1 with a creatinine column, a U-shaped glucose
  and a J-shaped creatinine on the death risk.

`write(path, name, rows, seed)` streams a table to disk (memory: one
row); `TRUTHS[name]` is its truth file -- each seeded truth, the
estimate of the battery's targeted panel that measures it, and the value
the generator's own code sets.
"""

from __future__ import annotations

import datetime
import math
import pathlib
import random
from typing import Iterator

TABLES = ("ST1", "ST2", "ST3", "ST4", "ST5", "ST6")

ST1_COLUMNS = [
    "age", "urban", "language", "ward", "smoker", "glucose", "sbp", "lactate", "diabetes",
    "ventilated", "crp", "procedures", "cost", "died", "fu_days", "event", "readmit",
]
LANGUAGES = ["en", "es", "zh", "vi", "ht", "so"]
LANGUAGE_WEIGHTS = [0.62, 0.18, 0.09, 0.095, 0.01, 0.005]
WARDS = ["w%02d" % k for k in range(12)]
WARD_EFFECT = [0.0, 0.1, -0.1, 0.3, -0.2, 0.5, 0.0, 0.2, -0.3, 0.4, 0.1, 0.8]
ST5_COLUMNS = [
    "age", "urban", "language", "ward", "smoker", "glucose", "sbp", "lactate", "diabetes",
    "ventilated", "crp", "procedures", "cost", "died", "readmit",
]
ST2_COLUMNS = ["sid", "arm", "age", "visit", "marker"]
ST3_COLUMNS = ["centre", "stage", "age", "urban", "entry_date", "event_date", "censor_date", "status"]
ST4_COLUMNS = [
    "code", "payer", "visits", "amount", "weight", "dose_rate", "dose",
    "cond_a", "cond_b", "cond_c", "readmit", "outcome",
]
ST6_COLUMNS = ST1_COLUMNS + ["creatinine"]
CHAPTERS = "ABCDEFGHIJKLMNOPQRST"
PAYERS = ["public", "private", "self", "other"]
STUDY_START = datetime.date(2015, 1, 1)
STUDY_END = datetime.date(2021, 12, 31)


def _logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _poisson(r: random.Random, lam: float) -> int:
    """A Poisson draw by multiplying uniforms (Knuth); lam is small here."""
    limit, k, product = math.exp(-lam), 0, 1.0
    while True:
        product *= r.random()
        if product < limit:
            return k
        k += 1


def _number(value: "float | None", places: int) -> str:
    return "" if value is None else f"{value:.{places}f}"


# -- ST1 and ST6: one row per patient --------------------------------------


def _patient(r: random.Random, curves: bool) -> "list[str]":
    """One patient of ST1 (``curves`` False) or ST6 (True)."""
    age = int(min(98, max(18, r.gauss(58, 17))))
    urban = r.random() < 0.48
    language = r.choices(LANGUAGES, LANGUAGE_WEIGHTS)[0]
    ward_index = r.randrange(12)
    draw = r.random()
    smoker = "current" if draw < 0.2 else ("former" if draw < 0.45 else "never")
    glucose_true = int(round(r.gauss(105 + 0.4 * (age - 58), 22)))
    diabetes = 1 if r.random() < (0.38 if glucose_true >= 126 else 0.09) else 0
    sbp = int(round(112 + 0.012 * (age - 40) ** 2 / 2 + (4 if urban else 0)
                    + 0.1 * (glucose_true - 105) + r.gauss(0, 12)))
    lactate = round(math.exp(r.gauss(0.5, 0.55)), 1)
    vent = 1 if r.random() < _logistic(-2.0 + 0.02 * (age - 60) + 1.2 * (lactate > 4)) else 0
    crp: "float | None" = round(math.exp(r.gauss(1.5 + 0.8 * vent, 0.9)), 1)
    mu = math.exp(0.9 + 0.6 * vent + 0.01 * (age - 60) + 0.3 * diabetes)
    lam = mu * r.gammavariate(2.0, 0.5)
    procedures = _poisson(r, lam) + 1
    cost = 0.0 if r.random() < 0.3 else round(math.exp(r.gauss(7 + 0.15 * procedures, 0.8)), 2)
    parity = 1 if ((smoker == "current") != (diabetes == 1)) else 0
    eta = (-3.6 + 0.07 * max(0, age - 60) + 0.9 * vent + 0.8 * (lactate > 4)
           + 0.4 * urban - 0.8 * vent * (age > 75) + 0.9 * parity - 0.45)
    creatinine = 0.0
    if curves:
        creatinine = round(math.exp(r.gauss(0.005 * (age - 60), 0.35)), 2)
        eta += 0.0012 * (glucose_true - 100.0) ** 2 - 0.55
        eta += 2.0 * (1.0 - creatinine) ** 2 if creatinine < 1.0 else 1.2 * (creatinine - 1.0)
    died = 1 if r.random() < _logistic(eta) else 0
    linear = 0.03 * (age - 60) + 0.7 * vent + 0.4 * diabetes + 0.25 * urban
    t = 900.0 * (-math.log(r.random()) / math.exp(linear)) ** (1 / 1.3)
    c = 365.0 if r.random() < 0.8 else r.uniform(10, 365)
    follow_up = int(min(t, c)) + 1
    event = 1 if t <= c else 0
    readmit = 1 if r.random() < _logistic(-4.6 + 0.12 * ward_index * diabetes
                                          + WARD_EFFECT[ward_index]) else 0
    glucose: "int | None" = glucose_true
    if r.random() < (0.25 if age > 80 else 0.05):
        glucose = None
    if r.random() < (0.45 if vent == 0 else 0.08):
        crp = None
    row = [
        str(age), "yes" if urban else "no", language, WARDS[ward_index], smoker,
        "" if glucose is None else str(glucose), str(sbp), _number(lactate, 1), str(diabetes),
        str(vent), _number(crp, 1), str(procedures), _number(cost, 2), str(died),
        str(follow_up), str(event), str(readmit),
    ]
    if curves:
        row += [_number(creatinine, 2)]
    return row


def st1(rows: int, seed: int) -> "Iterator[list[str]]":
    """ST1's rows (cells as text)."""
    r = random.Random(seed)
    for _ in range(rows):
        yield _patient(r, False)


def st6(rows: int, seed: int) -> "Iterator[list[str]]":
    """ST6's rows: ST1's draws with creatinine and the two turning curves."""
    r = random.Random(seed)
    for _ in range(rows):
        yield _patient(r, True)


def st5(rows: int, seed: int) -> "Iterator[list[str]]":
    """ST5's rows: each of fifteen ST1 columns from a stream of its own, so none is associated."""
    streams = [random.Random(seed * 1000 + k) for k in range(len(ST5_COLUMNS))]
    places = [ST1_COLUMNS.index(name) for name in ST5_COLUMNS]
    for _ in range(rows):
        yield [_patient(stream, False)[at] for stream, at in zip(streams, places)]


# -- ST2: several rows per subject ---------------------------------------


def subjects_for(rows: int) -> int:
    """How many ST2 subjects give about ``rows`` rows (6.6 visits each, measured)."""
    return max(50, rows * 3 // 20)


def st2(rows: int, seed: int) -> "Iterator[list[str]]":
    """ST2's rows: up to eight visits per subject, dropout depending on the previous value."""
    r = random.Random(seed)
    for s in range(subjects_for(rows)):
        arm = 1 if r.random() < 0.5 else 0
        age = int(min(90, max(25, r.gauss(55, 12))))
        b = r.gauss(0, 0.8)
        previous = None
        for v in range(8):
            if previous is not None and r.random() < _logistic(-3.0 + 0.6 * (previous - 7.5)):
                break
            y = round(7.5 + b + 0.01 * (age - 55) + 0.02 * v - 0.15 * arm * v + r.gauss(0, 0.5), 1)
            yield ["S%05d" % s, str(arm), str(age), str(v), f"{y:.1f}"]
            previous = y


# -- ST3: a registry with dates ------------------------------------------


def st3(rows: int, seed: int) -> "Iterator[list[str]]":
    """ST3's rows: entry, the end by event, competing event or censoring, and the status."""
    r = random.Random(seed)
    span = (STUDY_END - STUDY_START).days
    for _ in range(rows):
        centre = 1 + r.randrange(20)
        draw = r.random()
        stage = 1 if draw < 0.3 else 2 if draw < 0.6 else 3 if draw < 0.85 else 4
        age = int(min(95, max(30, r.gauss(65, 12))))
        urban = r.random() < 0.5
        entry = STUDY_START + datetime.timedelta(days=r.randrange(1826))
        early = 0.00045 * math.exp(0.45 * (stage - 1) + 0.02 * (age - 65))
        late = 0.00045 * math.exp(0.10 * (stage - 1) + 0.02 * (age - 65))
        e = -math.log(r.random())
        t1 = e / early if e < early * 365.0 else 365.0 + (e - early * 365.0) / late
        t2 = -math.log(r.random()) / (0.00012 * math.exp(0.06 * (age - 65)))
        loss = 0.0012 if centre <= 4 else 0.00008
        c = min(float(span - (entry - STUDY_START).days), -math.log(r.random()) / loss)
        end = min(t1, t2, c)
        days = max(1, int(end))
        status = "event" if end == t1 else "competing" if end == t2 else "censored"
        when = (entry + datetime.timedelta(days=days)).isoformat()
        yield [
            "C%02d" % centre, str(stage), str(age), "yes" if urban else "no", entry.isoformat(),
            when if status != "censored" else "", when if status == "censored" else "", status,
        ]


# -- ST4: claims ----------------------------------------------------------


CHAPTER_WEIGHT = [1.0 / (k + 1) ** 0.8 for k in range(20)]
CHAPTER_VISITS = [0.0, 0.3, -0.2, 0.5, 0.1, -0.3, 0.4, 0.0, 0.2, -0.1,
                  0.3, 0.0, -0.2, 0.1, 0.0, 0.2, -0.1, 0.0, 0.1, 0.0]
CHAPTER_OUTCOME = [0.0, 1.0, 0.0, 1.4, 0.0, 0.0, 0.8, 0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
CODE_WEIGHT = [1.0 / (k + 1) ** 1.1 for k in range(25)]


def code_name(chapter: int, k: int) -> str:
    """The k-th code of a chapter, written like a diagnosis code: E12.3."""
    return f"{CHAPTERS[chapter]}{10 + k // 5:02d}.{k % 5}"


def st4(rows: int, seed: int) -> "Iterator[list[str]]":
    """ST4's rows: one member each, a primary code, payer, visits, amount, dosing, three flags."""
    r = random.Random(seed)
    for _ in range(rows):
        chapter = r.choices(range(20), CHAPTER_WEIGHT)[0]
        k = r.choices(range(25), CODE_WEIGHT)[0]
        payer = r.choices(PAYERS, [0.45, 0.4, 0.1, 0.05])[0]
        weight = round(max(35.0, r.gauss(80, 15)), 1)
        rate = round(max(1.0, r.gauss(5.0, 1.0)), 1)
        dose = round(weight * rate, 1)
        visits = _poisson(r, math.exp(0.8 + CHAPTER_VISITS[chapter] + 0.2 * (payer == "private")))
        amount = 0.0 if r.random() < 0.1 else round(math.exp(r.gauss(6 + 0.3 * math.log1p(visits), 1.0)), 2)
        flags = [1 if r.random() < 0.5 else 0 for _ in range(3)]
        parity = flags[0] ^ flags[1] ^ flags[2]
        readmit = 1 if r.random() < _logistic(-1.4 + 0.4 * (2 * parity - 1)) else 0
        rare_code = 2.5 if k >= 20 and chapter % 2 == 0 else 0.0
        outcome = 1 if r.random() < _logistic(-5.6 + CHAPTER_OUTCOME[chapter] + rare_code
                                              + 0.02 * (weight - 80.0)) else 0
        yield [
            code_name(chapter, k), payer, str(visits), f"{amount:.2f}", f"{weight:.1f}",
            f"{rate:.1f}", f"{dose:.1f}", str(flags[0]), str(flags[1]), str(flags[2]),
            str(readmit), str(outcome),
        ]


BUILDERS = {"ST1": st1, "ST2": st2, "ST3": st3, "ST4": st4, "ST5": st5, "ST6": st6}
HEADERS = {
    "ST1": ST1_COLUMNS, "ST2": ST2_COLUMNS, "ST3": ST3_COLUMNS,
    "ST4": ST4_COLUMNS, "ST5": ST5_COLUMNS, "ST6": ST6_COLUMNS,
}


def lines(name: str, rows: int, seed: int) -> "Iterator[str]":
    """The table's CSV lines, header first, each ended by a line feed.

    No cell holds a comma, a quote or a line break, so every cell is
    written bare.
    """
    yield ",".join(HEADERS[name]) + "\n"
    for row in BUILDERS[name](rows, seed):
        yield ",".join(row) + "\n"


def write(path: pathlib.Path, name: str, rows: int, seed: int) -> int:
    """Stream the table to ``path`` (line feeds, UTF-8); return the data rows written."""
    written = -1
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        for line in lines(name, rows, seed):
            handle.write(line)
            written += 1
    return written


def text(name: str, rows: int, seed: int) -> str:
    """The whole table as one string, for tables small enough to hold."""
    return "".join(lines(name, rows, seed))


# -- the truth files --------------------------------------------------------
#
# Each seeded truth: the estimate of the targeted panel that measures it,
# and the value the generator's own code sets (None where the truth is a
# shape or a share the panel reads, not one coefficient).

_ST1_TRUTHS = {
    "sbp J-shape in age": ("ST1/curve:sbp_age_90", 0.006 * (50**2 - 20**2)),
    "death hinged at 60": ("ST1/curve:died_age_80", 0.07 * 20),
    "diabetes jumps at glucose 126": ("ST1/logistic:diabetes_glucose126",
                                      math.log(0.38 / 0.62) - math.log(0.09 / 0.91)),
    "ventilation jumps at lactate 4": ("ST1/logistic:vent_lact4", 1.2),
    "ventilation x age over 75 on death": ("ST1/logistic_ix:vent_old75", -0.8),
    "diabetes x current smoker on death": ("ST1/logistic_ix:diab_cur", -1.8),
    "readmission by ward x diabetes": ("ST1/logistic:readmit_diab_highward", None),
    "glucose missing over 80": ("ST1/miss:glucose_old80", math.log(0.25 / 0.75) - math.log(0.05 / 0.95)),
    "CRP missing off the ventilator": ("ST1/miss:crp_vent", math.log(0.08 / 0.92) - math.log(0.45 / 0.55)),
    "cost by procedures among the costed": ("ST1/ols:logcost_procedures", 0.15),
    "procedures overdispersed": ("ST1/poisson:procedures_dispersion", None),
    "hazard per 10 years of age": ("ST1/cox:age10", 0.3),
    "hazard of ventilation": ("ST1/cox:vent", 0.7),
    "hazard of diabetes": ("ST1/cox:diab", 0.4),
    "hazard of urban living": ("ST1/cox:urban", 0.25),
}
_ST2_TRUTHS = {
    "random intercept ICC": ("ST2/mixed:icc", 0.64 / 0.89),
    "arm x visit slope": ("ST2/mixed:arm_visit", -0.15),
    "dropout on the previous value": ("ST2/logistic:dropout_previous", 0.6),
}
_ST3_TRUTHS = {
    "stage effect fades after a year": ("ST3/cox:stage_early_minus_late", 0.35),
    "censoring depends on the centre": ("ST3/logistic:censored_low_centres", None),
    "competing event by age": ("ST3/cox_competing:age10", 0.6),
    "hazard per 10 years of age": ("ST3/cox:age10", 0.2),
    "no urban effect": ("ST3/cox:urban", 0.0),
}
_ST4_TRUTHS = {
    "three-way parity on readmission": ("ST4/logistic:readmit_abc", 8 * 0.4),
    "no pair effect of the parity": ("ST4/logistic_pairs:readmit_ab", 0.0),
    "dose from weight and rate": ("ST4/ols:dose_weight", None),
    "visits by chapter D": ("ST4/poisson:visits_chD", 0.5),
    "private payer visits": ("ST4/poisson:visits_private", 0.2),
    "outcome by chapter": ("ST4/logistic:outcome_chB", 1.0),
}
_ST5_TRUTHS = {
    "no association anywhere": ("ST5/null:significant_share", 0.05),
}
_ST6_TRUTHS = {
    "U-shaped glucose on death": ("ST6/curve:died_glucose_70", 0.0012 * (70 - 100.0) ** 2),
    "J-shaped creatinine on death": ("ST6/curve:died_creat_3", 1.2 * 2.0),
}
TRUTHS = {
    "ST1": _ST1_TRUTHS, "ST2": _ST2_TRUTHS, "ST3": _ST3_TRUTHS,
    "ST4": _ST4_TRUTHS, "ST5": _ST5_TRUTHS, "ST6": _ST6_TRUTHS,
}
# The truths that are a relation of three columns or more (K-S7-01's
# three-way clause, folded into K-BC-02).
THREE_WAY = ("diabetes x current smoker on death", "ventilation x age over 75 on death",
             "three-way parity on readmission")

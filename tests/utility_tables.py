"""Six invented tables with KNOWN generating structure, for lane MU's model-utility battery (plan P4-D485).

Each table is drawn at run time from a seed and never committed (plan
D13), streamed one row at a time as `analyst_tables.write` streams E0b's
tables. The column names are ordinary clinical words and every value is
drawn here: none comes from any real table. The formats are clean on
purpose -- E0's tables test formats, these test statistics -- so a miss
measured on them is a statistical one.

* ST7, clinic visits: about one person per 8.6 rows (2,310 to 2,355
  people at 20,000 rows on table seeds 1 to 3; 4 to 30 visits planned a
  person, irregular gamma gaps between visit dates, no visit after year
  6), 12 clinics whose effects are fixed constants (SD 3,
  drawn once: every table seed shares them, so a real table and its
  replicates are draws of one population), the arm, age and gender fixed
  within a person; a systolic pressure with a patient intercept (SD 8)
  and slope (SD 0.5 a year, correlation -0.3), arm B x years -1.0, a bend
  of -0.3 x years squared in arm B and an AR(1) residual (0.4 from visit
  to visit, SD 5); a repeated yes-or-no outcome with a patient intercept
  (SD 1.0); dropout on the previous value. The analysis computes the
  years from the dates.
* ST8, a treatment registry on start-stop rows: about one person per 2.5
  rows, a Weibull baseline of shape 1.3, a treatment that starts during
  follow-up (log hazard ratio -0.51), stage, age and an eGFR band updated
  at 0 to 3 laboratory updates, a competing event by age, censoring by
  centre, the event on the last interval only. Four structure rules hold
  on every row (start below stop, a person's intervals contiguous from 0,
  at most one event a person and on the last interval, treated never
  returning to 0).
* ST9, a cohort of 15 columns: a quadratic age term, a creatinine hinge, a
  lactate threshold, diabetes x smoker, a treatment confounded by age,
  diabetes, gender and pressure, three latent laboratory classes, a CRP
  missing at random. Its FLATTENED replicate (``flat=True``) halves the
  quadratic terms and the hinge.
* ST10, admissions counted over a time at risk: negative binomial (alpha
  0.5) with the days at risk as exposure, structural zeros by gender,
  eight wards.
* ST11, three laboratory values missing at random, the third missing
  wherever the second is (a monotone block): about 30 % of rows incomplete.
* ST12, a 40-level procedure group with Zipf frequencies, a 4-level
  ordinal severity, a 3-level discharge and a stay in days.

Each table has a TRUTHS entry: each generating value, the battery's
estimate key that targets it (`tests/model_utility.py`) and the value the
generator's code sets. Where an estimand is marginal, its value is the
generator's own large-sample value, labelled as such: COMPUTED by this
module's own code from the generator's constants (as
`analyst_tables.st4_outcome_estimand` is). An estimate of a misspecified
model has no truth here. ``flat=True`` exists for ST7 and ST9 only (the
curvature control); it halves every curve term the battery reads as a
curve.

Each table also has a KNOWS entry: what the person who holds the table
knows of each column (a measurement, a code, the identifier of the
person), the general facts the twin's routes answer the questions file
with (`tests/twin_routes.py`, the zoo's rule).

Ages are drawn in 18 to 89 years, so no value of an age column is a Safe
Harbor element. The people counts reach the owner's floor at both sizes
the battery reads (20,000 and 200,000 rows; LANE I4m RULINGS 18).
"""

from __future__ import annotations

import datetime
import math
import pathlib
import random
from typing import Iterator

TABLES = ("ST7", "ST8", "ST9", "ST10", "ST11", "ST12")
# The column naming the person, where one person stands on several rows.
PERSON = {"ST7": "subject", "ST8": "subject"}
# The tables drawn with ``flat=True`` as the flattened replicate.
FLATTENED = ("ST7", "ST9")
# Each table's stream is decorrelated from the others' at the same seed.
_STREAM = {"ST7": 7, "ST8": 8, "ST9": 9, "ST10": 10, "ST11": 11, "ST12": 12}

ST7_COLUMNS = ["subject", "clinic", "arm", "age", "gender", "visit", "visit_date", "sbp", "controlled"]
ST8_COLUMNS = ["subject", "centre", "stage", "age", "gender", "enrolled_on", "start_day", "stop_day",
               "treated", "egfr_band", "status"]
ST9_COLUMNS = ["age", "gender", "body_mass", "smoker", "sbp", "diabetes", "lactate", "creatinine", "lab1",
               "lab2", "lab3", "centre", "treatment", "crp", "died"]
ST10_COLUMNS = ["age", "gender", "ward", "diabetes", "days_at_risk", "admissions"]
ST11_COLUMNS = ["age", "gender", "outcome", "lab_a", "lab_b", "lab_c"]
ST12_COLUMNS = ["age", "gender", "procedure_group", "severity", "discharge", "stay_days"]
HEADERS = {"ST7": ST7_COLUMNS, "ST8": ST8_COLUMNS, "ST9": ST9_COLUMNS, "ST10": ST10_COLUMNS,
           "ST11": ST11_COLUMNS, "ST12": ST12_COLUMNS}
# What the person who holds each table knows of its columns (the zoo's `knows`): the
# reading a route answers a column's question with where the questions file offers it
# (`twin_routes.truthful`). A date column is asked nothing here and knows nothing.
KNOWS = {
    "ST7": {"subject": "identifier", "clinic": "code", "arm": "code", "age": "measurement", "gender": "code",
            "visit": "measurement", "sbp": "measurement", "controlled": "code"},
    "ST8": {"subject": "identifier", "centre": "code", "stage": "code", "age": "measurement", "gender": "code",
            "start_day": "measurement", "stop_day": "measurement", "treated": "code", "egfr_band": "code",
            "status": "code"},
    "ST9": {"age": "measurement", "gender": "code", "body_mass": "measurement", "smoker": "code",
            "sbp": "measurement", "diabetes": "code", "lactate": "measurement", "creatinine": "measurement",
            "lab1": "measurement", "lab2": "measurement", "lab3": "measurement", "centre": "code",
            "treatment": "code", "crp": "measurement", "died": "code"},
    "ST10": {"age": "measurement", "gender": "code", "ward": "code", "diabetes": "code",
             "days_at_risk": "measurement", "admissions": "measurement"},
    "ST11": {"age": "measurement", "gender": "code", "outcome": "code", "lab_a": "measurement",
             "lab_b": "measurement", "lab_c": "measurement"},
    "ST12": {"age": "measurement", "gender": "code", "procedure_group": "code", "severity": "code",
             "discharge": "code", "stay_days": "measurement"},
}

# -- shared draws -------------------------------------------------------------


def _logistic(x: float) -> float:
    if x < -700.0:
        return 0.0
    return 1.0 / (1.0 + math.exp(-x))


def _poisson(r: random.Random, lam: float) -> int:
    """A Poisson draw: Knuth's product of uniforms, over pieces of at most 30 (a sum of Poissons is one)."""
    total = 0
    while lam > 0.0:
        piece = min(lam, 30.0)
        lam -= piece
        limit, k, product = math.exp(-piece), 0, 1.0
        while True:
            product *= r.random()
            if product < limit:
                break
            k += 1
        total += k
    return total


def _negbin(r: random.Random, mean: float, alpha: float) -> int:
    """A negative binomial draw of the given mean and dispersion alpha (variance mean + alpha mean^2)."""
    return _poisson(r, r.gammavariate(1.0 / alpha, alpha * mean))


def _age(r: random.Random, centre: float, spread: float, low: int = 18, high: int = 89) -> int:
    return int(min(high, max(low, round(r.gauss(centre, spread)))))


def _one(value: float) -> str:
    return f"{value:.1f}"


def _two(value: float) -> str:
    return f"{value:.2f}"


# -- ST7: clinic visits ---------------------------------------------------------

ST7_START = datetime.date(2015, 1, 1)
ST7_CLINICS = 12
# The twelve clinics' effects on the pressure, drawn ONCE from a fixed stream
# (random.Random(70012), gauss with SD 3, rounded to 0.01) and written here as
# constants, as ST10's wards are: every table seed shares them, so a real table
# and its replicates are draws of one population (the statistics check's item 2;
# a table seed of its own drew its own clinic effects before).
ST7_CLINIC_EFFECT = [1.46, 2.08, -3.59, -0.73, -0.22, 3.54, 0.12, 2.1, 5.86, -2.92, 0.61, -1.41]
# A person's visits stop after this many years from the first (the bend of -0.3 a
# year squared in arm B stays in a plausible range of pressures; with no stop the
# follow-up ran to 18.6 years and arm B's pressure fell below 60 mmHg).
ST7_YEARS_MAX = 6.0
ST7_INTERCEPT = 120.0
ST7_AGE = 0.3          # per year of age at entry, around 60
ST7_MALE = 2.0
ST7_YEARS = 0.5        # arm A's slope a year
ST7_ARM_B_YEARS = -1.0
ST7_BEND = -0.3        # arm B x years squared
ST7_SD_INTERCEPT = 8.0
ST7_SD_SLOPE = 0.5
ST7_CORR = -0.3
ST7_SD_CLINIC = 3.0
ST7_AR = 0.4
ST7_SD_RESIDUAL = 5.0
ST7_CTL = (-1.0, 0.5, 0.2)   # controlled: intercept, arm B, per year
ST7_SD_CTL = 1.0
ST7_DROP = (-4.0, 0.05)      # dropout after a visit: intercept, per mmHg over 140


def st7(rows: int, seed: int, flat: bool = False) -> "Iterator[list[str]]":
    """ST7's rows: persons drawn until ``rows`` rows are written (the last person whole)."""
    r = random.Random(1_000_003 * seed + _STREAM["ST7"])
    bend = ST7_BEND / 2.0 if flat else ST7_BEND
    written = person = 0
    while written < rows:
        person += 1
        clinic = r.randrange(ST7_CLINICS)
        arm_b = r.random() < 0.5
        age = _age(r, 60.0, 10.0, 30, 85)
        male = r.random() < 0.5
        z1, z2 = r.gauss(0.0, 1.0), r.gauss(0.0, 1.0)
        b0 = ST7_SD_INTERCEPT * z1
        b1 = ST7_SD_SLOPE * (ST7_CORR * z1 + math.sqrt(1.0 - ST7_CORR ** 2) * z2)
        u = r.gauss(0.0, ST7_SD_CTL)
        planned = min(30, 4 + _poisson(r, r.gammavariate(2.0, 3.0)))
        entry = ST7_START + datetime.timedelta(days=r.randrange(6 * 365))
        gap = 0.0
        residual = None
        for visit in range(1, planned + 1):
            if visit > 1:
                gap += r.gammavariate(2.0, 0.25)
                if gap > ST7_YEARS_MAX:
                    break
            day = entry + datetime.timedelta(days=int(round(gap * 365.25)))
            years = (day - entry).days / 365.25
            shock = r.gauss(0.0, ST7_SD_RESIDUAL)
            residual = shock if residual is None else ST7_AR * residual + math.sqrt(1.0 - ST7_AR ** 2) * shock
            mean = (ST7_INTERCEPT + ST7_AGE * (age - 60) + ST7_MALE * male + ST7_CLINIC_EFFECT[clinic] + b0
                    + (ST7_YEARS + b1 + ST7_ARM_B_YEARS * arm_b) * years + bend * arm_b * years * years)
            sbp = round(mean + residual, 1)
            controlled = r.random() < _logistic(ST7_CTL[0] + ST7_CTL[1] * arm_b + u + ST7_CTL[2] * years)
            yield ["P%06d" % person, "C%02d" % (clinic + 1), "B" if arm_b else "A", str(age),
                   "male" if male else "female", str(visit), day.isoformat(), _one(sbp), str(int(controlled))]
            written += 1
            if r.random() < _logistic(ST7_DROP[0] + ST7_DROP[1] * (sbp - 140.0)):
                break


def st7_controlled_estimand(rows: int = 400_000, seed: int = 99, nodes: int = 60) -> "dict[str, float]":
    """ST7's repeated yes-or-no outcome: the population-averaged log odds a binomial GEE reaches (`ST7/gee_bin`).

    COMPUTED by the generator's own code, as `analyst_tables.st4_outcome_estimand`
    is (the population maximum-likelihood coefficients of the model an
    analysis fits, found as the zero of its expected score): the visits of
    ``rows`` rows drawn by `st7` itself at a seed the battery never reads
    give the design a table holds (each person's visit dates, dropout
    included; the years from the person's first visit, the arm, the age
    and the gender); at each visit the outcome's marginal mean is the
    generator's own curve, logistic(-1.0 + 0.5 arm B + u + 0.2 years),
    averaged over the person's intercept u ~ N(0, `ST7_SD_CTL`^2) by
    Gauss-Hermite quadrature of ``nodes`` points (no outcome is drawn); the
    estimand is the zero of the expected score of the marginal logistic
    model the GEE fits (intercept, years, arm B, age a year over 60, male),
    by Newton's method. The person's intercept is independent of the
    pressure that drives the dropout, so the dropout leaves the outcome's
    marginal mean as it is. The GEE's exchangeable working correlation
    weighs the visits otherwise than this score's independence, and the
    marginal curve is not exactly logistic; the difference this makes
    (lane MU's repair 2, a 200,000-row draw fitted by the GEE itself) is
    stated in plan P4-D485. Its error from the draw of the design at
    400,000 rows is under 0.001.
    """
    import array

    import numpy as np

    first: "dict[str, datetime.date]" = {}
    columns = [array.array("d") for _ in range(5)]
    for row in st7(rows, seed):
        day = datetime.date.fromisoformat(row[6])
        start = first.setdefault(row[0], day)
        for column, value in zip(columns, (1.0, (day - start).days / 365.25, float(row[2] == "B"),
                                           float(int(row[3]) - 60), float(row[4] == "male"))):
            column.append(value)
    x = np.column_stack([np.frombuffer(column, dtype=float) for column in columns])
    points, weights = np.polynomial.hermite.hermgauss(nodes)
    eta = ST7_CTL[0] + ST7_CTL[1] * x[:, 2] + ST7_CTL[2] * x[:, 1]
    mean = np.zeros(len(eta))
    for point, weight in zip(points, weights):
        mean += weight / math.sqrt(math.pi) / (1.0 + np.exp(-(eta + math.sqrt(2.0) * ST7_SD_CTL * point)))
    beta = np.zeros(x.shape[1])
    for _ in range(50):
        p = 1.0 / (1.0 + np.exp(-(x @ beta)))
        step = np.linalg.solve(x.T @ (x * (p * (1.0 - p))[:, None]), x.T @ (mean - p))
        beta = beta + step
        if float(np.max(np.abs(step))) < 1e-12:
            break
    return {name: float(b) for name, b in zip(("intercept", "years", "arm", "age", "male"), beta)}


# -- ST8: a treatment registry on start-stop rows -------------------------------

ST8_START = datetime.date(2012, 1, 1)
ST8_SHAPE = 1.3
ST8_RATE = 0.04                 # the Weibull baseline: H0(t) = rate * t^shape, t in years
ST8_TREATED = -0.51
ST8_STAGE = {"I": 0.0, "II": 0.4, "III": 0.8}
ST8_AGE10 = 0.3                 # per decade over 60
ST8_LOW_EGFR = 0.5
ST8_COMPETING = (0.03, 0.5)     # rate a year at 60, per decade over 60
ST8_CENTRE_SCALE = [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
ST8_TREAT_SHARE = 0.6
ST8_TREAT_WITHIN = 3.0          # years: the start day uniform over 0 to this
DAY = 365.25


def _st8_low(r: random.Random, age: int) -> bool:
    return r.random() < _logistic(-1.2 + 0.04 * (age - 66))


def _st8_person(r: random.Random) -> "dict[str, object]":
    """One person of ST8: baseline, the treatment and laboratory path, and the end of follow-up with its status."""
    centre = r.randrange(8)
    u = r.random()
    stage = "I" if u < 0.4 else "II" if u < 0.75 else "III"
    age = _age(r, 66.0, 10.0, 40, 89)
    male = r.random() < 0.5
    enrolled = ST8_START + datetime.timedelta(days=r.randrange(7 * 365))
    start = r.uniform(0.0, ST8_TREAT_WITHIN) if r.random() < ST8_TREAT_SHARE else None
    updates = sorted(r.uniform(0.2, 6.0) for _ in range(r.randrange(4)))
    bands = [_st8_low(r, age)] + [_st8_low(r, age) for _ in updates]
    censor = r.uniform(1.0, 8.0) * ST8_CENTRE_SCALE[centre]
    competing = r.expovariate(ST8_COMPETING[0] * math.exp(ST8_COMPETING[1] * (age - 60) / 10.0))
    need = r.expovariate(1.0)
    fixed = ST8_STAGE[stage] + ST8_AGE10 * (age - 60) / 10.0
    # The event time by inversion over the pieces where the treatment and the band hold.
    cuts = sorted(set([0.0] + ([start] if start is not None else []) + updates))
    event = math.inf
    used = 0.0
    for i, a in enumerate(cuts):
        b = cuts[i + 1] if i + 1 < len(cuts) else math.inf
        treated = start is not None and a >= start
        low = bands[sum(1 for t in updates if t <= a)]
        rate = ST8_RATE * math.exp(fixed + ST8_TREATED * treated + ST8_LOW_EGFR * low)
        piece = rate * (b ** ST8_SHAPE - a ** ST8_SHAPE) if b != math.inf else math.inf
        if used + piece >= need:
            event = (a ** ST8_SHAPE + (need - used) / rate) ** (1.0 / ST8_SHAPE)
            break
        used += piece
    end = min(event, competing, censor)
    status = 1 if end == event else 2 if end == competing else 0
    return {"centre": centre, "stage": stage, "age": age, "male": male, "enrolled": enrolled, "start": start,
            "updates": updates, "bands": bands, "end": end, "status": status, "event": event,
            "competing": competing}


def st8(rows: int, seed: int, flat: bool = False) -> "Iterator[list[str]]":
    """ST8's rows: a person's follow-up split where treatment starts and at each laboratory update."""
    r = random.Random(1_000_003 * seed + _STREAM["ST8"])
    written = person = 0
    while written < rows:
        person += 1
        p = _st8_person(r)
        end_day = max(1, int(round(float(p["end"]) * DAY)))  # type: ignore[arg-type]
        start = p["start"]
        start_day = None if start is None else int(round(float(start) * DAY))  # type: ignore[arg-type]
        update_days = [int(round(t * DAY)) for t in p["updates"]]  # type: ignore[attr-defined]
        cuts = sorted({d for d in update_days + ([start_day] if start_day is not None else []) if 0 < d < end_day})
        edges = [0] + cuts + [end_day]
        for i in range(len(edges) - 1):
            a, b = edges[i], edges[i + 1]
            treated = start_day is not None and a >= start_day
            low = p["bands"][sum(1 for d in update_days if d <= a)]  # type: ignore[index]
            last = i == len(edges) - 2
            yield ["S%06d" % person, "K%d" % (int(p["centre"]) + 1), str(p["stage"]), str(p["age"]),  # type: ignore[call-overload]
                   "male" if p["male"] else "female", p["enrolled"].isoformat(), str(a), str(b),  # type: ignore[attr-defined]
                   str(int(treated)), "low" if low else "normal", str(p["status"]) if last else "0"]
            written += 1


def st8_incidence_estimand(persons: int = 400_000, seed: int = 99) -> "dict[str, float]":
    """The cumulative incidence of the event and of the competing event at 1, 3 and 5 years, uncensored.

    COMPUTED by the generator's own code: ``persons`` persons drawn as
    `st8` draws them, each followed to the earlier of its event and its
    competing event (censoring removed), counted at each time. Its Monte
    Carlo error at 400,000 persons is under 0.001.
    """
    r = random.Random(seed)
    counts = {f"{cause}_{t}": 0 for cause in (1, 2) for t in (1, 3, 5)}
    for _ in range(persons):
        p = _st8_person(r)
        first = min(float(p["event"]), float(p["competing"]))  # type: ignore[arg-type]
        cause = 1 if first == p["event"] else 2
        for t in (1, 3, 5):
            if first <= t:
                counts[f"{cause}_{t}"] += 1
    return {k: v / persons for k, v in counts.items()}


# -- ST9: a cohort with a curve, a hinge, a threshold, an interaction and a treatment

ST9_DIED = {"intercept": -3.0, "age": 0.5, "age_sq": 0.15, "sbp10": 0.2, "diabetes": 0.5, "smoker": 0.4,
            "diabetes_smoker": 0.6, "lactate_over2": 0.8, "creat_hinge": 0.9, "treatment": -0.4,
            "female": -0.3, "lab1": 0.2}
ST9_TREAT = {"intercept": -0.5, "age": 0.4, "diabetes": 0.5, "female": -0.3, "sbp10": 0.2}
ST9_SBP = {"intercept": 120.0, "age": 5.0, "age_sq": 1.0, "body_mass": 0.8, "smoker": 5.0, "sd": 12.0}
ST9_CLASS_SHARE = (0.5, 0.3, 0.2)
ST9_CLASS_MEANS = ((0.0, 0.0, 0.0), (1.5, 2.0, -1.0), (3.0, -1.0, 2.0))
ST9_HINGE = 1.3
ST9_CRP_MISSING = (-2.2, 0.3, 0.5)  # intercept, per decade over 60, diabetes


def _st9_row(r: random.Random, flat: bool) -> "dict[str, float]":
    age = _age(r, 60.0, 12.0)
    a = (age - 60) / 10.0
    female = r.random() < 0.5
    body_mass = round(min(60.0, max(15.0, r.gauss(28.0 - 0.8 * female, 5.0))), 1)
    smoker = r.random() < _logistic(-1.0 - 0.2 * a)
    sq = ST9_SBP["age_sq"] / 2.0 if flat else ST9_SBP["age_sq"]
    sbp = round(ST9_SBP["intercept"] + ST9_SBP["age"] * a + sq * a * a + ST9_SBP["body_mass"] * (body_mass - 28.0)
                + ST9_SBP["smoker"] * smoker + r.gauss(0.0, ST9_SBP["sd"]))
    diabetes = r.random() < _logistic(-2.0 + 0.4 * a + 0.12 * (body_mass - 28.0))
    lactate = round(math.exp(r.gauss(0.35 + 0.1 * diabetes, 0.4)), 1)
    creatinine = round(math.exp(r.gauss(0.0 + 0.1 * diabetes, 0.3)), 2)
    u = r.random()
    k = 0 if u < ST9_CLASS_SHARE[0] else 1 if u < ST9_CLASS_SHARE[0] + ST9_CLASS_SHARE[1] else 2
    labs = [round(ST9_CLASS_MEANS[k][j] + r.gauss(0.0, 1.0), 1) for j in range(3)]
    centre = r.randrange(10)
    s10 = (sbp - 130.0) / 10.0
    treated = r.random() < _logistic(ST9_TREAT["intercept"] + ST9_TREAT["age"] * a + ST9_TREAT["diabetes"] * diabetes
                                     + ST9_TREAT["female"] * female + ST9_TREAT["sbp10"] * s10)
    crp = round(math.exp(r.gauss(1.0 + 0.4 * diabetes + 0.05 * a, 0.8)), 1)
    crp_missing = r.random() < _logistic(ST9_CRP_MISSING[0] + ST9_CRP_MISSING[1] * a + ST9_CRP_MISSING[2] * diabetes)
    noise = r.random()
    eta = _st9_eta(a, s10, diabetes, smoker, lactate, creatinine, female, labs[0], flat)
    died_if_untreated = noise < _logistic(eta)
    died_if_treated = noise < _logistic(eta + ST9_DIED["treatment"])
    return {"age": age, "female": female, "body_mass": body_mass, "smoker": smoker, "sbp": sbp, "diabetes": diabetes,
            "lactate": lactate, "creatinine": creatinine, "labs": labs, "class": k, "centre": centre,
            "treatment": treated, "crp": None if crp_missing else crp,
            "died": died_if_treated if treated else died_if_untreated, "eta": eta}  # type: ignore[dict-item]


def _st9_eta(a: float, s10: float, diabetes: bool, smoker: bool, lactate: float, creatinine: float,
             female: bool, lab1: float, flat: bool) -> float:
    """The death log odds without the treatment's term."""
    sq = ST9_DIED["age_sq"] / 2.0 if flat else ST9_DIED["age_sq"]
    hinge = ST9_DIED["creat_hinge"] / 2.0 if flat else ST9_DIED["creat_hinge"]
    return (ST9_DIED["intercept"] + ST9_DIED["age"] * a + sq * a * a + ST9_DIED["sbp10"] * s10
            + ST9_DIED["diabetes"] * diabetes + ST9_DIED["smoker"] * smoker
            + ST9_DIED["diabetes_smoker"] * diabetes * smoker + ST9_DIED["lactate_over2"] * (lactate > 2.0)
            + hinge * max(0.0, creatinine - ST9_HINGE) + ST9_DIED["treatment"] * 0.0
            + ST9_DIED["female"] * female + ST9_DIED["lab1"] * lab1)


def st9(rows: int, seed: int, flat: bool = False) -> "Iterator[list[str]]":
    """ST9's rows, one a patient."""
    r = random.Random(1_000_003 * seed + _STREAM["ST9"])
    for _ in range(rows):
        p = _st9_row(r, flat)
        labs = p["labs"]
        yield [str(p["age"]), "female" if p["female"] else "male", _one(p["body_mass"]),
               "yes" if p["smoker"] else "no", str(int(p["sbp"])), str(int(p["diabetes"])), _one(p["lactate"]),
               _two(p["creatinine"]), _one(labs[0]), _one(labs[1]), _one(labs[2]),  # type: ignore[index]
               "H%02d" % (int(p["centre"]) + 1), str(int(p["treatment"])),
               "" if p["crp"] is None else _one(p["crp"]), str(int(p["died"]))]


def st9_ate_estimand(persons: int = 1_000_000, seed: int = 99) -> float:
    """The average effect of treatment on the risk of death, both potential outcomes, over the population.

    COMPUTED by the generator's own code: the mean over ``persons`` draws
    of expit(eta + treatment) - expit(eta), each person's own death log
    odds without the treatment (Monte Carlo error under 0.0002 at a
    million persons).
    """
    r = random.Random(seed)
    total = 0.0
    for _ in range(persons):
        eta = float(_st9_row(r, False)["eta"])
        total += _logistic(eta + ST9_DIED["treatment"]) - _logistic(eta)
    return total / persons


def st9_att_estimand(persons: int = 1_000_000, seed: int = 99) -> float:
    """The average effect of treatment on the risk of death among the TREATED: what matching treated to untreated reads.

    COMPUTED by the generator's own code, as `st9_ate_estimand`, over the
    draws the generator treats (Monte Carlo error under 0.0003).
    """
    r = random.Random(seed)
    total = 0.0
    treated = 0
    for _ in range(persons):
        row = _st9_row(r, False)
        if row["treatment"]:
            eta = float(row["eta"])
            total += _logistic(eta + ST9_DIED["treatment"]) - _logistic(eta)
            treated += 1
    return total / treated


# -- ST10: admissions over a time at risk ----------------------------------------

ST10_COUNT = {"intercept": -3.0, "age": 0.1, "diabetes": 0.3}
ST10_WARD = [0.0, 0.2, -0.1, 0.3, -0.2, 0.1, 0.4, -0.3]
ST10_ALPHA = 0.5
ST10_ZERO = {"intercept": -1.1, "female": 0.3}


def st10(rows: int, seed: int, flat: bool = False) -> "Iterator[list[str]]":
    """ST10's rows: a negative binomial over the days at risk, with structural zeros."""
    r = random.Random(1_000_003 * seed + _STREAM["ST10"])
    for _ in range(rows):
        age = _age(r, 55.0, 15.0)
        a = (age - 60) / 10.0
        female = r.random() < 0.5
        ward = r.randrange(8)
        diabetes = r.random() < 0.25
        days = r.randint(30, 365)
        structural = r.random() < _logistic(ST10_ZERO["intercept"] + ST10_ZERO["female"] * female)
        mean = math.exp(ST10_COUNT["intercept"] + ST10_COUNT["age"] * a + ST10_COUNT["diabetes"] * diabetes
                        + ST10_WARD[ward]) * days
        count = _negbin(r, mean, ST10_ALPHA)
        yield [str(age), "female" if female else "male", "W%d" % (ward + 1), str(int(diabetes)), str(days),
               "0" if structural else str(count)]


# -- ST11: missing values at random, a monotone block ------------------------------

ST11_OUTCOME = {"intercept": -1.0, "lab_a": 0.4, "lab_c": 0.3, "age": 0.2}
ST11_MISS_A = {"intercept": -2.2, "age": 0.4, "outcome": 0.5}
ST11_MISS_B = {"intercept": -2.0, "female": 0.4, "lab_a": 0.3}
ST11_MISS_C = {"intercept": -3.0, "age": 0.3}


def st11(rows: int, seed: int, flat: bool = False) -> "Iterator[list[str]]":
    """ST11's rows: lab_b follows lab_a, lab_c follows lab_b and age; each missing at random given what is seen."""
    r = random.Random(1_000_003 * seed + _STREAM["ST11"])
    for _ in range(rows):
        age = _age(r, 60.0, 12.0)
        a = (age - 60) / 10.0
        female = r.random() < 0.5
        lab_a = r.gauss(0.2 * a, 1.0)
        lab_b = 0.6 * lab_a + r.gauss(0.0, 0.8)
        lab_c = 0.5 * lab_b + 0.3 * a + r.gauss(0.0, 0.7)
        outcome = r.random() < _logistic(ST11_OUTCOME["intercept"] + ST11_OUTCOME["lab_a"] * lab_a
                                         + ST11_OUTCOME["lab_c"] * lab_c + ST11_OUTCOME["age"] * a)
        miss_a = r.random() < _logistic(ST11_MISS_A["intercept"] + ST11_MISS_A["age"] * a
                                        + ST11_MISS_A["outcome"] * outcome)
        # Whether lab_b is missing reads lab_a where lab_a is seen; where it is not, gender alone.
        seen_a = 0.0 if miss_a else lab_a
        miss_b = r.random() < _logistic(ST11_MISS_B["intercept"] + ST11_MISS_B["female"] * female
                                        + ST11_MISS_B["lab_a"] * seen_a)
        miss_c = miss_b or r.random() < _logistic(ST11_MISS_C["intercept"] + ST11_MISS_C["age"] * a)
        yield [str(age), "female" if female else "male", str(int(outcome)), "" if miss_a else _two(lab_a),
               "" if miss_b else _two(lab_b), "" if miss_c else _two(lab_c)]


# -- ST12: rare levels; ordinal and nominal outcomes --------------------------------

ST12_GROUPS = 40
# Zipf frequencies of exponent 2 (the lane's brief said 1.1, whose rarest of
# 40 levels holds about 94 rows at 20,000 rows, so no level would fall under
# the floor): at 20,000 rows and table seed 1 six levels hold fewer than 11
# rows (the smallest 6; the floor pools them) and nine more hold 11 to 21
# (seeds 2 and 3: seven and eight under 11, seven more of 11 to 21 each); at
# 200,000 rows every level holds about 77 rows or more.
ST12_ZIPF = 2.0
ST12_WEIGHTS = [1.0 / (k + 1) ** ST12_ZIPF for k in range(ST12_GROUPS)]
# Each group's effect on the severity's latent scale; the commonest group's is 0.
ST12_GROUP_EFFECT = [0.0] + [round(0.9 * math.sin(1.7 * k), 3) for k in range(1, ST12_GROUPS)]
ST12_SEVERITY = {"age": 0.4, "female": -0.3}
ST12_CUTS = (-1.0, 0.5, 2.0)
SEVERITY_LEVELS = ("mild", "moderate", "severe", "critical")
DISCHARGE_LEVELS = ("home", "rehabilitation", "other")
# The log odds of each discharge against home: intercept, per decade over 60, female, severe or worse.
ST12_DISCHARGE = {"rehabilitation": (-1.2, 0.3, 0.0, 0.8), "other": (-2.0, 0.2, 0.4, 0.5)}
ST12_STAY = (1.0, 0.4, 0.5)   # log mean intercept, per severity step, alpha


def st12(rows: int, seed: int, flat: bool = False) -> "Iterator[list[str]]":
    """ST12's rows: the latent severity, the discharge by severity, the stay by severity."""
    r = random.Random(1_000_003 * seed + _STREAM["ST12"])
    total = sum(ST12_WEIGHTS)
    cumulative = []
    running = 0.0
    for w in ST12_WEIGHTS:
        running += w / total
        cumulative += [running]
    for _ in range(rows):
        age = _age(r, 60.0, 14.0)
        a = (age - 60) / 10.0
        female = r.random() < 0.5
        u = r.random()
        group = next((k for k, c in enumerate(cumulative) if u < c), ST12_GROUPS - 1)
        v = min(max(r.random(), 1e-12), 1.0 - 1e-12)
        latent = (ST12_SEVERITY["age"] * a + ST12_SEVERITY["female"] * female + ST12_GROUP_EFFECT[group]
                  + math.log(v / (1.0 - v)))
        severity = sum(1 for c in ST12_CUTS if latent > c)
        severe = severity >= 2
        etas = {name: c[0] + c[1] * a + c[2] * female + c[3] * severe for name, c in ST12_DISCHARGE.items()}
        denominator = 1.0 + sum(math.exp(e) for e in etas.values())
        w = r.random()
        p_rehab = math.exp(etas["rehabilitation"]) / denominator
        p_other = math.exp(etas["other"]) / denominator
        discharge = "rehabilitation" if w < p_rehab else "other" if w < p_rehab + p_other else "home"
        stay = 1 + _negbin(r, math.exp(ST12_STAY[0] + ST12_STAY[1] * severity), ST12_STAY[2])
        yield [str(age), "female" if female else "male", "G%02d" % (group + 1), SEVERITY_LEVELS[severity],
               discharge, str(stay)]


# -- writing ---------------------------------------------------------------------------

BUILDERS = {"ST7": st7, "ST8": st8, "ST9": st9, "ST10": st10, "ST11": st11, "ST12": st12}


def lines(name: str, rows: int, seed: int, flat: bool = False) -> "Iterator[str]":
    """The table's CSV lines, header first, each ended by a line feed (no cell holds a comma or a quote)."""
    yield ",".join(HEADERS[name]) + "\n"
    for row in BUILDERS[name](rows, seed, flat):
        yield ",".join(row) + "\n"


def write(path: pathlib.Path, name: str, rows: int, seed: int, flat: bool = False) -> int:
    """Stream the table to ``path`` (line feeds, UTF-8); return the data rows written."""
    written = -1
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        for line in lines(name, rows, seed, flat):
            handle.write(line)
            written += 1
    return written


def text(name: str, rows: int, seed: int, flat: bool = False) -> str:
    """The whole table as one string, for tables small enough to hold."""
    return "".join(lines(name, rows, seed, flat))




# -- the truth files --------------------------------------------------------------------
#
# Each truth: (the estimate key of `tests/model_utility.py` that targets it,
# the value, and how the value is known). GENERATING: a constant the
# generator sets, which a correctly specified model reaches. COMPUTED: the
# generator's own large-sample value of a marginal estimand, computed by
# this module's own code (`COMPUTED_BY` names the function; the value is
# what that function returns at its default size, its Monte Carlo error
# stated there). An estimate of a misspecified model (a random-slope
# model without the serial term, a GEE of the pressure under dropout on
# the previous value, an AFT on the per-person table) has no truth here:
# the battery reads it against the real table's own value, as every
# estimate. The binomial GEE of the repeated yes-or-no outcome holds a
# COMPUTED truth (`st7_controlled_estimand`): that outcome's person
# intercept is independent of the pressure the dropout follows. Its arm
# and year terms are held by that GEE within four standard errors (LANE
# MU RULINGS 7 (3), the combined verify's item 4: the variational truths
# alone held the arm by 0.512 against an effect of 0.5, so a generator
# that dropped it passed); the variational truths stay as approximate
# checks.

GENERATING = "generating"
COMPUTED = "computed"

_ST7_TRUTHS = {
    "years in arm A": ("ST7/lmm:years", ST7_YEARS, GENERATING),
    "arm B x years": ("ST7/lmm:arm_years", ST7_ARM_B_YEARS, GENERATING),
    "the bend in arm B": ("ST7/lmm:arm_years_sq", ST7_BEND, GENERATING),
    "arm B at entry": ("ST7/lmm:arm", 0.0, GENERATING),
    "age per year": ("ST7/lmm:age", ST7_AGE, GENERATING),
    "male": ("ST7/lmm:male", ST7_MALE, GENERATING),
    "controlled per year (variational)": ("ST7/vb:years", ST7_CTL[2], GENERATING),
    "controlled, arm B (variational)": ("ST7/vb:arm", ST7_CTL[1], GENERATING),
    "controlled per year (population-averaged)": ("ST7/gee_bin:years", 0.16591, COMPUTED),
    "controlled, arm B (population-averaged)": ("ST7/gee_bin:arm", 0.41509, COMPUTED),
}
_ST8_TRUTHS = {
    "treated, from its start": ("ST8/cox_tv:treated", ST8_TREATED, GENERATING),
    "stage II": ("ST8/cox_tv:stage2", ST8_STAGE["II"], GENERATING),
    "stage III": ("ST8/cox_tv:stage3", ST8_STAGE["III"], GENERATING),
    "age per decade": ("ST8/cox_tv:age10", ST8_AGE10, GENERATING),
    "low eGFR band": ("ST8/cox_tv:egfr_low", ST8_LOW_EGFR, GENERATING),
    "the competing event per decade": ("ST8/cox_comp:age10", ST8_COMPETING[1], GENERATING),
    "the competing event, treated": ("ST8/cox_comp:treated", 0.0, GENERATING),
    "incidence of the event at 1 year": ("ST8/aj:event_1", 0.07612, COMPUTED),
    "incidence of the event at 3 years": ("ST8/aj:event_3", 0.23699, COMPUTED),
    "incidence of the event at 5 years": ("ST8/aj:event_5", 0.36158, COMPUTED),
    "incidence of the competing event at 1 year": ("ST8/aj:competing_1", 0.04277, COMPUTED),
    "incidence of the competing event at 3 years": ("ST8/aj:competing_3", 0.10913, COMPUTED),
    "incidence of the competing event at 5 years": ("ST8/aj:competing_5", 0.15535, COMPUTED),
}
_ST9_TRUTHS = {
    "age on death": ("ST9/quad:age", ST9_DIED["age"], GENERATING),
    "quadratic age on death": ("ST9/quad:age_sq", ST9_DIED["age_sq"], GENERATING),
    "pressure on death": ("ST9/quad:sbp10", ST9_DIED["sbp10"], GENERATING),
    "diabetes x smoker on death": ("ST9/quad:diabetes_smoker", ST9_DIED["diabetes_smoker"], GENERATING),
    "lactate over 2 on death": ("ST9/quad:lactate_over2", ST9_DIED["lactate_over2"], GENERATING),
    "creatinine hinge on death": ("ST9/quad:creat_hinge", ST9_DIED["creat_hinge"], GENERATING),
    "treatment on death": ("ST9/quad:treatment", ST9_DIED["treatment"], GENERATING),
    "female on death": ("ST9/quad:female", ST9_DIED["female"], GENERATING),
    "lab1 on death": ("ST9/quad:lab1", ST9_DIED["lab1"], GENERATING),
    "quadratic age on pressure": ("ST9/sbp:age_sq", ST9_SBP["age_sq"], GENERATING),
    "treatment by age": ("ST9/prop:age", ST9_TREAT["age"], GENERATING),
    "treatment by diabetes": ("ST9/prop:diabetes", ST9_TREAT["diabetes"], GENERATING),
    "treatment by female": ("ST9/prop:female", ST9_TREAT["female"], GENERATING),
    "treatment by pressure": ("ST9/prop:sbp10", ST9_TREAT["sbp10"], GENERATING),
    "the average effect on the risk": ("ST9/ate:weighting", -0.02947, COMPUTED),
}
_ST10_TRUTHS = {
    "admissions per decade": ("ST10/zinb:age", ST10_COUNT["age"], GENERATING),
    "admissions by diabetes": ("ST10/zinb:diabetes", ST10_COUNT["diabetes"], GENERATING),
    "overdispersion": ("ST10/zinb:alpha", ST10_ALPHA, GENERATING),
    "structural zeros, female": ("ST10/zinb:zero_female", ST10_ZERO["female"], GENERATING),
    "structural zeros, intercept": ("ST10/zinb:zero_intercept", ST10_ZERO["intercept"], GENERATING),
}
_ST11_TRUTHS = {
    "outcome by lab_a": ("ST11/mice:lab_a", ST11_OUTCOME["lab_a"], GENERATING),
    "outcome by lab_c": ("ST11/mice:lab_c", ST11_OUTCOME["lab_c"], GENERATING),
    "outcome per decade": ("ST11/mice:age", ST11_OUTCOME["age"], GENERATING),
    "lab_a missing per decade": ("ST11/miss_a:age", ST11_MISS_A["age"], GENERATING),
    "lab_a missing by outcome": ("ST11/miss_a:outcome", ST11_MISS_A["outcome"], GENERATING),
    "lab_b missing, female": ("ST11/miss_b:female", ST11_MISS_B["female"], GENERATING),
    "lab_b missing by lab_a": ("ST11/miss_b:lab_a", ST11_MISS_B["lab_a"], GENERATING),
}
_ST12_TRUTHS = {
    "severity per decade": ("ST12/ord:age", ST12_SEVERITY["age"], GENERATING),
    "severity, female": ("ST12/ord:female", ST12_SEVERITY["female"], GENERATING),
    "rehabilitation per decade": ("ST12/mnl:rehabilitation_age", ST12_DISCHARGE["rehabilitation"][1], GENERATING),
    "rehabilitation, severe": ("ST12/mnl:rehabilitation_severe", ST12_DISCHARGE["rehabilitation"][3], GENERATING),
    "other discharge, female": ("ST12/mnl:other_female", ST12_DISCHARGE["other"][2], GENERATING),
    "other discharge, severe": ("ST12/mnl:other_severe", ST12_DISCHARGE["other"][3], GENERATING),
}
TRUTHS = {"ST7": _ST7_TRUTHS, "ST8": _ST8_TRUTHS, "ST9": _ST9_TRUTHS, "ST10": _ST10_TRUTHS,
          "ST11": _ST11_TRUTHS, "ST12": _ST12_TRUTHS}
# The sampling SD of an APPROXIMATE estimate (the variational check, which carries no standard error: a posterior SD
# is no sampling SE), and the rows it was measured at: the SD of its value over 24 independent ST7 draws at 20,000 rows
# (table seeds 2001 to 2024, never a seed the battery reads, the persons chosen by the battery's own share rule, about
# 283 a draw; lane MU's repair 1: arm 0.511 on average against the generating 0.5, SD 0.128; a year 0.205 against 0.2,
# SD 0.041). A truth case holds the estimate within four of them at every size: the check reads about 300 persons at
# 200,000 rows as at 20,000 (its share is fixed on each real table), so its spread does not shrink with the rows.
ACROSS_DRAW_SD = {"ST7/vb:arm": (0.128, 20000), "ST7/vb:years": (0.041, 20000)}
# The function that computes each COMPUTED truth (at its default size), by key prefix.
COMPUTED_BY = {"ST7/gee_bin:": "st7_controlled_estimand", "ST8/aj:": "st8_incidence_estimand",
               "ST9/ate:": "st9_ate_estimand"}

"""Invented start-stop tables for the counting process (lane GRb2-b, plan P4-D491 part b; contract 4.6c.14).

Every table here is invented: its parameters are round values chosen for
this module, the table's own, and none is read from or attributed to any
source. `start_stop` returns ``(header, rows)`` with every cell written as
text, the rows of one patient consecutive and in interval order, the
person column first:

- a patient's follow-up from day 0 to its end, cut where its treatment
  starts and at each of 0 to 3 laboratory updates (uniform over 0.2 to 6
  years), one row an interval: `start_day` below `stop_day`, the intervals
  contiguous from 0, `on_treatment` switching once from 0 to 1 and
  staying, `outcome` 0 on every row but the last;
- the end drawn by inversion of a Weibull hazard (shape 1.25, 0.04 a
  year) with the treatment (log hazard ratio -0.5 from its start), the
  grade (II +0.4, III +0.8), the age (+0.3 a decade over 60) and the
  current laboratory band (low +0.5), a competing end (0.03 a year at 60,
  +0.5 a decade) and censoring uniform over 1 to 8 years times its site's
  factor: outcome 1, 2 or 0.

The variants keep every rule but the one they name: ``gap=True`` starts
one patient's second interval a day after its first stops (the interval
rule then holds on every patient but one); ``returning=True`` turns one
patient's treatment off again (the switch rule then holds on every
patient but one); ``dated=True`` writes the start and the stop as dates
(which this version's rule does not read).

The maker uses the standard library only and a seeded `random.Random`,
so a table is a fixed function of its arguments.
"""
from __future__ import annotations

import datetime
import math
import random

HEADER = ["pid", "site", "grade", "age", "gender", "entered_on", "start_day", "stop_day", "on_treatment", "lab_band", "outcome"]
SHAPE = 1.25
RATE = 0.04
TREATED = -0.5
GRADE = {"I": 0.0, "II": 0.4, "III": 0.8}
AGE_DECADE = 0.3
LOW_LAB = 0.5
COMPETING = (0.03, 0.5)
SITE_FACTOR = (0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3)
TREATED_SHARE = 0.6
TREATED_WITHIN = 3.0
DAY = 365.25
FIRST = datetime.date(2014, 1, 1)


def _logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _treatment(grade: str, age: int) -> "tuple[float, float]":
    """BY INDICATION (``confounded=True``): the share ever treated and the window its start is uniform over, by grade and age.

    At age 66 the shares are 0.35, 0.60 and 0.85 for grades I, II and
    III, the odds times exp(-0.04) a year over 66; the start falls within
    3, 2 and 1 years. Invented values, chosen so a time-to-start model
    reads a strong grade term and the crude treated term lies far from
    the adjusted one.
    """
    base = {"I": 0.35, "II": 0.60, "III": 0.85}[grade]
    odds = base / (1.0 - base) * math.exp(-0.04 * (age - 66))
    return odds / (1.0 + odds), {"I": 3.0, "II": 2.0, "III": 1.0}[grade]


def _patient(draw: random.Random, confounded: bool = False) -> "dict[str, object]":
    site = draw.randrange(len(SITE_FACTOR))
    u = draw.random()
    grade = "I" if u < 0.4 else "II" if u < 0.75 else "III"
    age = int(min(89, max(40, round(draw.gauss(66.0, 10.0)))))
    male = draw.random() < 0.5
    entered = FIRST + datetime.timedelta(days=draw.randrange(7 * 365))
    share, within = _treatment(grade, age) if confounded else (TREATED_SHARE, TREATED_WITHIN)
    start = draw.uniform(0.0, within) if draw.random() < share else None
    updates = sorted(draw.uniform(0.2, 6.0) for _ in range(draw.randrange(4)))
    lows = [draw.random() < _logistic(-1.2 + 0.04 * (age - 66)) for _ in range(len(updates) + 1)]
    censor = draw.uniform(1.0, 8.0) * SITE_FACTOR[site]
    competing = draw.expovariate(COMPETING[0] * math.exp(COMPETING[1] * (age - 60) / 10.0))
    need = draw.expovariate(1.0)
    fixed = GRADE[grade] + AGE_DECADE * (age - 60) / 10.0
    cuts = sorted(set([0.0] + ([start] if start is not None else []) + updates))
    event = math.inf
    used = 0.0
    for at, low in enumerate(cuts):
        high = cuts[at + 1] if at + 1 < len(cuts) else math.inf
        treated = start is not None and low >= start
        band = lows[sum(1 for one in updates if one <= low)]
        rate = RATE * math.exp(fixed + TREATED * treated + LOW_LAB * band)
        piece = rate * (high ** SHAPE - low ** SHAPE) if high != math.inf else math.inf
        if used + piece >= need:
            event = (low ** SHAPE + (need - used) / rate) ** (1.0 / SHAPE)
            break
        used += piece
    end = min(event, competing, censor)
    outcome = 1 if end == event else 2 if end == competing else 0
    return {"site": site, "grade": grade, "age": age, "male": male, "entered": entered, "start": start,
            "updates": updates, "lows": lows, "end": end, "outcome": outcome}


END_WORDS = {"0": "censored", "1": "event", "2": "competing"}
BARE = ["pid", "start_day", "stop_day", "on_treatment", "lab_band", "outcome"]


def _split(mine: "list[list[str]]", pieces: int, draw: random.Random) -> "list[list[str]]":
    """Each interval of one patient cut into up to ``pieces`` contiguous pieces at drawn inner days; the end value on the last piece only."""
    out: "list[list[str]]" = []
    for at, line in enumerate(mine):
        low, high = int(line[6]), int(line[7])
        inner = sorted(draw.sample(range(low + 1, high), min(pieces - 1, high - low - 1))) if high - low > 1 else []
        bounds = [low] + inner + [high]
        for piece in range(len(bounds) - 1):
            cut = list(line)
            cut[6], cut[7] = str(bounds[piece]), str(bounds[piece + 1])
            if not (at == len(mine) - 1 and piece == len(bounds) - 2):
                cut[10] = "0"
            out += [cut]
    return out


def bare(header: "list[str]", rows: "list[list[str]]") -> "tuple[list[str], list[list[str]]]":
    """The table with its patient-level columns left out: the person, the intervals, the treatment, the laboratory band, the end."""
    keep = [header.index(name) for name in BARE]
    return [header[at] for at in keep], [[row[at] for at in keep] for row in rows]


def start_stop(
    rows_wanted: int, seed: int, gap: bool = False, returning: bool = False, dated: bool = False,
    pieces: int = 1, words: bool = False, confounded: bool = False,
) -> "tuple[list[str], list[list[str]]]":
    """The invented start-stop table: patients drawn until ``rows_wanted`` rows are written (the last patient whole).

    ``pieces=k`` cuts each interval into up to k contiguous pieces (a
    person-period file: the end value on the last piece only, so the end
    column holds a value other than its none on few rows); ``words=True``
    writes the end values as words (censored, event, competing);
    ``confounded=True`` gives the treatment by indication (see
    `_treatment`). The defaults write the table of the first version byte
    for byte.
    """
    draw = random.Random(7_000_003 * seed + 17)
    cutting = random.Random(31 * seed + pieces)
    rows: "list[list[str]]" = []
    patient = 0
    broken_gap = broken_return = False
    while len(rows) < rows_wanted:
        patient += 1
        one = _patient(draw, confounded)
        end_day = max(1, int(round(float(one["end"]) * DAY)))  # type: ignore[arg-type]
        start = one["start"]
        start_day = None if start is None else int(round(float(start) * DAY))  # type: ignore[arg-type]
        update_days = [int(round(t * DAY)) for t in one["updates"]]  # type: ignore[attr-defined]
        cuts = sorted({d for d in update_days + ([start_day] if start_day is not None else []) if 0 < d < end_day})
        edges = [0] + cuts + [end_day]
        mine: "list[list[str]]" = []
        for at in range(len(edges) - 1):
            low, high = edges[at], edges[at + 1]
            treated = start_day is not None and low >= start_day
            band = one["lows"][sum(1 for d in update_days if d <= low)]  # type: ignore[index]
            last = at == len(edges) - 2
            entered = one["entered"]
            assert isinstance(entered, datetime.date)
            mine += [["P%06d" % patient, "S%d" % (int(one["site"]) + 1), str(one["grade"]), str(one["age"]),  # type: ignore[call-overload]
                      "male" if one["male"] else "female", entered.isoformat(), str(low), str(high),
                      str(int(treated)), "low" if band else "normal", str(one["outcome"]) if last else "0"]]
        if gap and not broken_gap and len(mine) >= 2 and int(mine[1][7]) > int(mine[1][6]) + 1:
            mine[1][6] = str(int(mine[1][6]) + 1)
            broken_gap = True
        if returning and not broken_return and len(mine) >= 3 and mine[1][8] == "1":
            mine[2][8] = "0"
            broken_return = True
        if pieces > 1:
            mine = _split(mine, pieces, cutting)
        if words:
            for line in mine:
                line[10] = END_WORDS[line[10]]
        if dated:
            for line in mine:
                entered = datetime.date.fromisoformat(line[5])
                line[6] = (entered + datetime.timedelta(days=int(line[6]))).isoformat()
                line[7] = (entered + datetime.timedelta(days=int(line[7]))).isoformat()
        rows += mine
    return list(HEADER), rows


def constant_census(patients: int, rows_each: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """An invented person-period file of a CONSTANT CENSUS: ``patients`` patients of exactly ``rows_each`` contiguous rows each.

    Each patient's follow-up (400 to 4,000 days) is cut at ``rows_each - 1``
    drawn inner days; the treatment switches once from 0 to 1 at one of its
    rows for half of the patients; the end, 0 on every row but the last, is
    1 (about a quarter, more in grade III), 2 (about a sixth) or 0 there.
    Invented values, chosen so every patient holds the same number of rows
    (repair 2, LANE GRb2 RULINGS 11 (3)).
    """
    draw = random.Random(9_173 * seed + 5)
    rows: "list[list[str]]" = []
    for patient in range(patients):
        follow = draw.randint(400, 4000)
        bounds = [0] + sorted(draw.sample(range(1, follow), rows_each - 1)) + [follow]
        grade = draw.choice(["I", "II", "III"])
        turn = draw.randint(1, rows_each - 1) if draw.random() < 0.5 else None
        u = draw.random()
        outcome = "1" if u < 0.22 + 0.12 * (grade == "III") else "2" if u < 0.38 else "0"
        entered = (FIRST + datetime.timedelta(days=draw.randrange(2400))).isoformat()
        fixed = ["S%d" % draw.randint(1, 7), grade, str(draw.randint(41, 88)), draw.choice(["male", "female"]), entered]
        for at in range(rows_each):
            rows += [["C%05d" % patient] + fixed + [str(bounds[at]), str(bounds[at + 1]), "1" if turn is not None and at >= turn else "0",
                                                    draw.choice(["low", "normal", "normal"]), outcome if at == rows_each - 1 else "0"]]
    return list(HEADER), rows


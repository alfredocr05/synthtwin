"""An invented wide table of 302 columns, written from a seed at run time (lane W5-302).

A health table exported at full width holds a few hundred columns of
every kind side by side: a person's key and a record number, dates and
clock times, yes/no letters, codes, measurements (several of them a
series over a person's visits), counts, columns that are empty on most
rows, short notes and keys of other kinds. This module writes such a
table from one seeded stream of the standard library's `random`, so it
is the same bytes on every platform, and is never committed (plan D13;
CLAUDE.md, "Test fixtures are built by seeded neutral scripts at
runtime"). The column names are `col_001` to `col_302`; what each column
IS lives in `FAMILIES`, and the relations written into the table, which
a twin's relations zone must carry, live in `RELATIONS`. Nothing here
comes from a real table: every value, level, share and slope is chosen in
this file.

THE FAMILIES (`FAMILIES`, in the table's order):

* `person` (col_001): a person's key, one to twelve rows a person, about
  four on average;
* `record` (col_002): a record number of every row;
* `start`, `stop` (col_003, col_004): a visit's start and stop, a date
  and a minute clock, the stop a duration after the start that the first
  code's level sets;
* `day` (col_005): a calendar date a few days after the start;
* `clock` (col_006): a clock time alone, on five-minute marks;
* `years` (col_007): a whole number of years, the same on a person's
  rows (18 to 95, so a Safe Harbor question is put);
* `flag` (col_008 to col_027): yes/no letters, the first four the same
  on a person's rows;
* `code` (col_028 to col_087): codes of 3 to 25 levels, the commoner
  levels far commoner;
* `series` (col_088 to col_107): measurements with a person's own level
  and a trend over the person's visits;
* `chain` (col_108 to col_167): measurements each moved by the one
  before it, a letter and a code, with a few empty cells;
* `count` (col_168 to col_187): whole numbers whose mean a letter moves;
* `skewed` (col_188 to col_207): positive measurements of two decimals
  with a long right tail and a detection limit written `<0.10`;
* `sparse` (col_208 to col_267): empty on 85 to 99 rows in a hundred,
  half numbers and half codes, some present only beside a letter;
* `note` (col_268 to col_287): short free-text notes from templates;
* `key` (col_288 to col_297): keys of other kinds (a second key of the
  person, an order number, a hexadecimal token, a key shared by one to
  three consecutive rows, a sample number with a year);
* `far` (col_298 to col_302): columns moved by columns far before them
  in the table, so the relations search must look the whole width back.

`KNOWS` is what the person who holds the table knows of each column (the
reading a question offers that is true of it), as the reliability
battery's `reliability_tables.KNOWS` is for its tables.
"""

from __future__ import annotations

import math
import random
from typing import Iterator

COLUMNS = 302
NAMES = tuple(f"col_{k:03d}" for k in range(1, COLUMNS + 1))


def _span(first: int, last: int) -> "tuple[str, ...]":
    return tuple(f"col_{k:03d}" for k in range(first, last + 1))


FAMILIES: "dict[str, tuple[str, ...]]" = {
    "person": _span(1, 1),
    "record": _span(2, 2),
    "start": _span(3, 3),
    "stop": _span(4, 4),
    "day": _span(5, 5),
    "clock": _span(6, 6),
    "years": _span(7, 7),
    "flag": _span(8, 27),
    "code": _span(28, 87),
    "series": _span(88, 107),
    "chain": _span(108, 167),
    "count": _span(168, 187),
    "skewed": _span(188, 207),
    "sparse": _span(208, 267),
    "note": _span(268, 287),
    "key": _span(288, 297),
    "far": _span(298, 302),
}
FAMILY_OF = {name: family for family, names in FAMILIES.items() for name in names}
PERSON = "col_001"

# The relations written into the table, response -> the earlier columns that move it (each a parent a relations
# fit of the response must find): a code moved by a letter, a code moved by a code, a measurement by the one before
# it, a count by a letter, a sparse column's presence by a letter, and the far columns by columns 100 to 270
# places before them.
RELATIONS: "dict[str, tuple[str, ...]]" = {
    "col_013": ("col_009",),
    "col_028": ("col_012",),
    "col_029": ("col_028",),
    "col_109": ("col_108",),
    "col_130": ("col_129",),
    "col_150": ("col_149",),
    "col_168": ("col_016",),
    "col_208": ("col_014",),
    "col_298": ("col_120", "col_030"),
    "col_299": ("col_150",),
    "col_300": ("col_130", "col_015"),
    "col_301": ("col_007",),
    "col_302": ("col_029",),
}

KNOWS: "dict[str, str]" = {PERSON: "identifier", "col_002": "identifier", "col_007": "measurement"}
for _name in FAMILIES["key"]:
    KNOWS[_name] = "identifier"
for _family in ("series", "chain", "count", "skewed", "far"):
    for _name in FAMILIES[_family]:
        KNOWS.setdefault(_name, "measurement")
for _name in FAMILIES["code"]:
    KNOWS[_name] = "code"
KNOWS["col_299"] = "code"
KNOWS["col_302"] = "code"
AGES = ("col_007",)


def holder_answer(column: str, choices: "list[str]", people: bool) -> str:
    """The answer the table's holder gives a column's question, or '' where none offered fits.

    The reliability battery's rule (`reliability_battery.truthful`) over
    `KNOWS`: the years' Safe Harbor question `yes`; the known reading
    where offered, `keep` where a known column is offered `identifier`
    and `keep` but not its reading; the person question (``people``)
    `identifier` for the person's key alone and `keep` for any other key;
    `keep` for a column nothing is known of where it is offered (a note,
    a clock: read as they are); any other yes-or-no question `no` (no
    column here is a Safe Harbor element but the years and the keys).
    """
    known = KNOWS.get(column, "")
    if column in AGES and "yes" in choices:
        return "yes"
    given = known if known in choices else ""
    if not given and known and "identifier" in choices and "keep" in choices:
        given = "keep"
    if given == "identifier" and people and column != PERSON:
        given = "keep" if "keep" in choices else ""
    if not given and not known and "keep" in choices:
        given = "keep"
    if not given and "yes" in choices and "no" in choices:
        given = "no"
    return given

_FIRST_DAY = 19_000  # days after 1970-01-01: a day in 2022
_DAYS = 1_400


def _date_text(day: int) -> str:
    """The calendar date ``day`` days after 1970-01-01, written YYYY-MM-DD (the civil-from-days rule)."""
    z = day + 719_468
    era = z // 146_097
    doe = z - era * 146_097
    yoe = (doe - doe // 1_460 + doe // 36_524 - doe // 146_096) // 365
    doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
    mp = (5 * doy + 2) // 153
    d = doy - (153 * mp + 2) // 5 + 1
    m = mp + 3 if mp < 10 else mp - 9
    y = yoe + era * 400 + (1 if m <= 2 else 0)
    return f"{y:04d}-{m:02d}-{d:02d}"


def _stamp(day: int, minute: int) -> str:
    day += minute // 1_440
    minute %= 1_440
    return f"{_date_text(day)} {minute // 60:02d}:{minute % 60:02d}"


def _weights(levels: int, steep: float) -> "list[float]":
    return [1.0 / (k + 1) ** steep for k in range(levels)]


def _pick(draw: random.Random, cumulative: "list[float]") -> int:
    u = draw.random() * cumulative[-1]
    low, high = 0, len(cumulative) - 1
    while low < high:
        middle = (low + high) // 2
        if cumulative[middle] < u:
            low = middle + 1
        else:
            high = middle
    return low


def _cumulative(weights: "list[float]") -> "list[float]":
    out: "list[float]" = []
    total = 0.0
    for w in weights:
        total += w
        out += [total]
    return out


def _poisson(draw: random.Random, lam: float) -> int:
    limit, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= draw.random()
        if p <= limit:
            return k
        k += 1


def _logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


class _Plan:
    """The fixed shape of every column, drawn once from the seed before any row."""

    def __init__(self, draw: random.Random) -> None:
        self.code_levels = [3 + draw.randrange(23) for _k in FAMILIES["code"]]
        self.code_letters = [chr(ord("A") + draw.randrange(20)) for _k in FAMILIES["code"]]
        self.code_cumulative = [_cumulative(_weights(levels, 1.1)) for levels in self.code_levels]
        self.flag_share = [0.1 + 0.4 * draw.random() for _k in FAMILIES["flag"]]
        self.series_level = [40.0 + 80.0 * draw.random() for _k in FAMILIES["series"]]
        self.series_trend = [draw.uniform(-1.5, 1.5) for _k in FAMILIES["series"]]
        self.chain_places = [1 + (k % 2) for k in range(len(FAMILIES["chain"]))]
        self.count_mean = [0.5 + 6.0 * draw.random() for _k in FAMILIES["count"]]
        self.skewed_scale = [0.2 + 3.0 * draw.random() for _k in FAMILIES["skewed"]]
        self.sparse_share = [0.01 + 0.14 * draw.random() for _k in FAMILIES["sparse"]]
        self.sparse_levels = [2 + draw.randrange(9) for _k in FAMILIES["sparse"]]


_NOTES = ("review in {n} days", "no change", "stable", "improving", "seen by team {l}", "see note {n}",
          "repeat test", "call back in {n} weeks", "", "")


def rows(n: int, seed: int) -> "list[list[str]]":
    """The table's ``n`` rows, the header aside, from ``seed``."""
    return list(_rows(n, seed))


def _rows(n: int, seed: int) -> "Iterator[list[str]]":
    draw = random.Random(f"wide-table-{seed}")
    plan = _Plan(draw)
    person, left, visit, day = 0, 0, 0, 0
    fixed_flags: "list[bool]" = []
    years = 0
    person_level: "list[float]" = []
    person_key2 = ""
    shared_key, shared_left = "", 0
    for row in range(n):
        if left == 0:
            person += 1
            left = 1 + min(11, int(draw.expovariate(1.0 / 3.0)))
            visit = 0
            day = _FIRST_DAY + draw.randrange(_DAYS)
            fixed_flags = [draw.random() < plan.flag_share[k] for k in range(4)]
            years = int(draw.gauss(52.0, 16.0)) if draw.random() < 0.97 else 80 + draw.randrange(16)
            years = max(18, min(95, years))
            person_level = [draw.gauss(0.0, 6.0) for _k in FAMILIES["series"]]
            person_key2 = f"E{30_000_000 + 11 * person}"
        else:
            visit += 1
            day += 3 + int(draw.expovariate(1.0 / 30.0))
        left -= 1
        cells: "list[str]" = []
        # person, record, start, stop, day, clock, years
        flags = list(fixed_flags)
        for k in range(4, len(FAMILIES["flag"])):
            share = plan.flag_share[k]
            if k == 5:  # col_013 moved by col_009 (the second of the person's letters)
                share = 0.65 if flags[1] else 0.15
            flags += [draw.random() < share]
        codes: "list[int]" = []
        for k in range(len(FAMILIES["code"])):
            if k == 0:  # col_028 moved by col_012
                shift = 1.2 if flags[4] else 0.0
                level = 0 if draw.random() < _logistic(-0.6 + shift) else 1 + _pick(draw, plan.code_cumulative[k][:-1])
            elif k == 1:  # col_029 moved by col_028
                level = codes[0] % plan.code_levels[1] if draw.random() < 0.55 else _pick(draw, plan.code_cumulative[k])
            else:
                level = _pick(draw, plan.code_cumulative[k])
            codes += [min(level, plan.code_levels[k] - 1)]
        start = 450 if draw.random() < 0.12 else 480 + 15 * draw.randrange(40)
        length = 30 + 25 * (codes[2] % 5) + int(draw.expovariate(1.0 / 20.0))
        cells += [f"P{1_000_000 + 7 * person}", f"R{50_000_000 + 13 * row}", _stamp(day, start),
                  _stamp(day, start + length), _date_text(day + draw.randrange(4)),
                  f"{(6 + draw.randrange(14)):02d}:{5 * draw.randrange(12):02d}", str(years)]
        cells += ["Y" if f else "N" for f in flags]
        cells += [f"{plan.code_letters[k]}{10 + code}" for k, code in enumerate(codes)]
        for k in range(len(FAMILIES["series"])):
            value = plan.series_level[k] + person_level[k] + plan.series_trend[k] * visit + draw.gauss(0.0, 4.0)
            cells += ["" if draw.random() < 0.01 else f"{value:.1f}"]
        chain: "list[float]" = []
        for k in range(len(FAMILIES["chain"])):
            before = chain[k - 1] - 50.0 if k else 0.0
            value = (50.0 + 0.6 * before + 4.0 * flags[k % 20] + 3.0 * (codes[k % 60] == 0)
                     + (0.015 * before * before if k % 7 == 3 else 0.0) + draw.gauss(0.0, 6.0))
            chain += [value]
            cells += ["" if draw.random() < 0.02 else f"{value:.{plan.chain_places[k]}f}"]
        for k in range(len(FAMILIES["count"])):
            lam = plan.count_mean[k] * (2.2 if k == 0 and flags[8] else 1.0)  # col_168 moved by col_016
            cells += [str(_poisson(draw, lam))]
        for k in range(len(FAMILIES["skewed"])):
            value = plan.skewed_scale[k] * math.exp(draw.gauss(0.0, 0.8))
            cells += ["<0.10" if value < 0.10 else f"{value:.2f}"]
        for k in range(len(FAMILIES["sparse"])):
            share = plan.sparse_share[k]
            if k == 0:  # col_208 present mostly beside col_014 = Y
                share = 0.30 if flags[6] else 0.02
            if draw.random() >= share:
                cells += [""]
            elif k % 2 == 0:
                cells += [f"{draw.gauss(20.0 + k, 5.0):.1f}"]
            else:
                cells += [f"S{k:02d}-{draw.randrange(plan.sparse_levels[k])}"]
        for k in range(len(FAMILIES["note"])):
            template = _NOTES[(k + draw.randrange(len(_NOTES))) % len(_NOTES)]
            cells += [template.format(n=1 + draw.randrange(30), l=chr(ord("A") + draw.randrange(6)))]
        if shared_left == 0:
            shared_left = 1 + draw.randrange(3)
            shared_key = f"V{70_000_000 + 17 * row}"
        shared_left -= 1
        token = draw.getrandbits(48)
        keys = [person_key2, f"ORD{9_000_000 + 3 * row}", f"{token:012x}", shared_key,
                f"AC-{2022 + (day - _FIRST_DAY) // 365}-{600_000 + row:06d}",
                f"M{40_000_000 + 19 * person}", f"K{row:07d}", f"Q{80_000_000 + 23 * row}",
                f"T{60_000_000 + 29 * person}", f"N{10_000_000 + 31 * row}"]
        cells += keys
        # far: col_298 by col_120 and col_030; col_299 by col_150; col_300 by col_130 x col_015; col_301 by
        # col_007 (curved); col_302 by col_029.
        x120, x130, x150 = chain[12] - 50.0, chain[22] - 50.0, chain[42] - 50.0
        cells += [f"{10.0 + 0.5 * x120 + 6.0 * (codes[2] == 0) + draw.gauss(0.0, 3.0):.1f}"]
        cells += ["H" if draw.random() < _logistic(-0.2 + 0.12 * x150) else "L"]
        cells += [f"{20.0 + (0.6 if flags[7] else -0.2) * x130 + draw.gauss(0.0, 3.0):.1f}"]
        cells += [f"{30.0 + 0.004 * (years - 55) ** 2 + draw.gauss(0.0, 1.5):.1f}"]
        cells += [f"Z{(codes[1] * 3) % 7}" if draw.random() < 0.7 else f"Z{draw.randrange(7)}"]
        yield cells


def write(path: object, n: int, seed: int = 1) -> int:
    """Writes the table of ``n`` rows from ``seed`` to ``path`` (UTF-8, comma, LF); the bytes written."""
    import csv

    written = 0
    with open(str(path), "w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out, lineterminator="\n")
        writer.writerow(NAMES)
        for cells in _rows(n, seed):
            writer.writerow(cells)
        written = out.tell()
    return written

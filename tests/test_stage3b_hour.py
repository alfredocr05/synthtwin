"""THE HOUR'S GATE (stage 3b landing 3b.2-H, lane T2, plan P4-D371): time of day comes back.

Before this landing a column of moments published nothing about the
hour of the day, and the twin drew each rank's clock evenly over the day:
lab draws heaped from 06:00 to 08:00 came back at 8 per cent where 43 per
cent of the real draws stood, discharges between 10:00 and 14:00 at 17
per cent against 63, hour TVD 0.18 to 0.65. A column of moments now
publishes `hour_census` -- how many cells of its body fall on each hour
of the written clock, in groups the one merge rule chooses
(`calendar_clock.hour_groups`) -- the loader holds it to HC1 to HC6, the
generator meets it (method G7.3g) and the validator recounts it (V5-H1).

The clauses, each red on its own mutant (named beside it):

* `test_the_hour_battery_publishes_its_census` -- every column of the
  battery in scope publishes; its groups equal the merge recomputed here
  from the cells; the loader's own check finds nothing at floors 11 and
  1; the 1-, 3- and 7-day spans are withheld with the span sentence and
  the 14-day span publishes (mutant: the span rule withdrawn);
* `test_the_hour_battery_twins_meet_their_census` -- at seeds 0 and 4
  nothing is MISSED, V5-H1 is HELD on every published column, a
  published count at midnight is exact, and the hour statistics hold:
  BOUND, the twin's hour TVD within (tail rows a listed tail does not
  fix + cells of groups of several hours) / parsed; CAP, that TVD at
  most 0.10 below 10,000 rows and 0.02 from them at floor 11; SHAPE,
  the twin's gap at most a quarter of the real column's distance from
  flat wherever that distance is three sampling scales; and every twin's
  weekdays and count of different values are the ones the same seed
  writes with the pass withdrawn;
* the ten-thousand-row table -- the 10-week clinic, a burst, every cell
  on the hour, a half-hour grid -- and the lab panel, where whole units
  cannot meet the census: met, nothing missed, the count kept (mutants:
  G7.3g's own steps withdrawn; PUT BACK withdrawn);
* OR starts, ten rooms at 07:30 on weekdays alone, whose ranks before
  the rung on the last day of their gap have no place but in a full hour:
  met through RELIEF (mutant: RELIEF withdrawn, the census missed);
* rule 4 and its amendment: the cells at midnight a description counts
  are the body's, but for those of a tail listing only midnight values (the 1970
  clinic: mutant, every midnight charged to the body, so the night
  hours merge with the morning's) and the loader holds a published
  group to them (mutant: a producer without rule 4, refused HC5); and
  where those tails hold every midnight, no tie group stands at one
  (the 1970 clinic at a floor of 36: mutant, the group at a midnight
  and `midnight.count` missed);
* the sixteenth vectors file: the product gives every frozen state the
  oracle's answer, and each case is red on its own mutant
  (`STEP_MUTANTS`) -- three of them on a field of minutes whose parent
  is the hour, so the one clock pass is held field-generic (G7.3g, the
  3b.4 skeptic's M4), and, since the landing's Codex review, two of
  ranks written at a sixtieth second: one pinned there, counted in the
  hour it is written in, and the ranks between two pins of one such
  second, written as it (its other items:
  `tests/test_stage3b_hour_review.py`);
* the dial's half day (plan P4-D370's carve-out): a stamp declared a
  12-hour clock with no marker writes no time it cannot read back, its
  census published or withheld (mutants: G7.3b step 10 withdrawn; the
  half day's own census withdrawn);
* the loader's six rules, one refused description each, and
  `test_validating_never_produces_an_hour_census`;
* the leftover round (the lane's second skeptic): a dense column drawn
  past its count keeps the ties the pass makes, within 1 per cent of its
  published count (mutant: the short count put back whatever that count
  is), and a 300-row 12-hour lunch clinic keeps its count at midnight
  (mutants: four edits of the half day's rule in the move onto a
  midnight, each its own test).

Every table is built here, seeded and neutral (plan D13).
"""

from __future__ import annotations

import copy
import dataclasses
import datetime
import importlib.util
import io
import json
import pathlib
import random
import sys
import types

import pytest

import crosscheck
import fixtures
import kpi_shapes
from synthtwin import (
    calendar_clock,
    calendar_rules,
    contract,
    errors,
    generation,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

REPOSITORY = pathlib.Path(__file__).resolve().parent.parent
VECTORS = REPOSITORY / "tests" / "reference" / "generation-branch-vectors-16.json"
ORACLE = REPOSITORY / "tools" / "reference" / "make_generation_reference_vectors.py"
SOURCE = pathlib.Path(generation.__file__).read_text(encoding="utf-8")

DAY = 86400
LINE = 11

# -- the battery -----------------------------------------------------------

_YEAR = [datetime.date(2023, 1, 1) + datetime.timedelta(days=step) for step in range(365)]
_TWO_YEARS = [datetime.date(2023, 1, 1) + datetime.timedelta(days=step) for step in range(731)]
_WEEKDAYS = [day for day in _YEAR if day.weekday() < 5]
_TEN_WEEKS = [datetime.date(2024, 3, 4) + datetime.timedelta(days=step) for step in range(70)]
_ED = (2.6, 2.2, 1.9, 1.6, 1.4, 1.4, 1.7, 2.5, 3.8, 5.0, 5.9, 6.2,
       6.1, 5.9, 5.7, 5.6, 5.6, 5.6, 5.5, 5.3, 4.9, 4.4, 3.8, 3.2)
_LAB = (1.0, 0.8, 0.8, 1.0, 1.5, 3.0, 22.0, 20.0, 6.0, 5.0, 4.5, 4.0,
        3.5, 3.5, 3.5, 3.0, 3.0, 2.5, 2.0, 2.0, 1.8, 1.5, 1.2, 1.0)
_DISCHARGE = (0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.5, 1.5, 3.0, 12.0, 14.0,
              13.0, 10.0, 6.0, 4.5, 3.5, 2.5, 2.0, 1.5, 1.2, 0.8, 0.5, 0.3)
_ADMITTED = (1.2, 1.0, 0.8, 0.7, 0.6, 0.6, 0.9, 3.0, 5.5, 5.0, 4.0, 3.2,
             2.6, 2.5, 2.6, 2.7, 2.6, 2.4, 2.2, 2.0, 1.8, 1.6, 1.5, 1.3)
_ROUNDS = tuple(9.0 if hour % 4 == 0 else (3.0 if hour % 4 == 1 else 1.0) for hour in range(24))
_CLINIC_HOURS = (8, 9, 10, 11, 12, 13, 14, 15, 16)
_CLINIC = (1.0, 1.2, 1.2, 1.1, 0.4, 1.0, 1.1, 1.0, 0.7)
# Rule 4's witness: arrivals almost never at night's first hour.
_QUIET_MIDNIGHT = (0.05,) + _ED[1:]

_ISO_S = "%Y-%m-%d %H:%M:%S"
_ISO_M = "%Y-%m-%d %H:%M"
_ISO_T = "%Y-%m-%dT%H:%M"
_US = "%m/%d/%Y %H:%M"
_SLASHED = "%Y/%m/%d %H:%M"
_DAY_FIRST = "%d/%m/%Y %H:%M:%S"


def _at(day: datetime.date, hour: int, minute: int, second: int = 0) -> datetime.datetime:
    return datetime.datetime(day.year, day.month, day.day, hour, minute, second)


def _hourly(draw: random.Random, days: "list[datetime.date]", weights: "tuple[float, ...]", rows: int) -> "list[datetime.datetime]":
    return [
        _at(draw.choice(days), draw.choices(range(24), weights=weights)[0], draw.randrange(60), draw.randrange(60))
        for _row in range(rows)
    ]


def _clinic(draw: random.Random, days: "list[datetime.date]", rows: int) -> "list[datetime.datetime]":
    """Weekday slots 08:00 to 16:59, seven in ten on :00 or :30."""
    found: "list[datetime.datetime]" = []
    for _row in range(rows):
        pick = draw.random()
        minute = draw.choice((0, 30)) if pick < 0.70 else (draw.choice((15, 45)) if pick < 0.95 else draw.randrange(60))
        found += [_at(draw.choice(days), draw.choices(_CLINIC_HOURS, weights=_CLINIC)[0], minute)]
    return found


def _vitals(draw: random.Random, rows: int) -> "list[str]":
    """Rounds every four hours, and 3.2 per cent charted at exactly midnight."""
    found: "list[str]" = []
    for _row in range(rows):
        day = draw.choice(_TWO_YEARS)
        if draw.random() < 0.032:
            found += [_at(day, 0, 0).strftime(_ISO_S)]
            continue
        moment = _at(day, draw.choices(range(24), weights=_ROUNDS)[0], draw.randrange(60), 1 + draw.randrange(59))
        found += [moment.strftime(_ISO_S)]
    return found


def _midtail(draw: random.Random, rows: int) -> "list[str]":
    """Rule 4's witness: 30 imports at 00:00:00, eleven on the first day -- the low tail --
    and four other cells of hour 0, so hour 0 holds its 19 body cells at midnight and few more."""
    cells = [moment.strftime(_ISO_S) for moment in _hourly(draw, _YEAR[10:], _QUIET_MIDNIGHT, rows - 34)]
    cells += [_at(draw.choice(_YEAR[20:]), 0, 30).strftime(_ISO_S) for _step in range(4)]
    cells += [_at(_YEAR[0], 0, 0).strftime(_ISO_S)] * 11
    cells += [_at(draw.choice(_YEAR[20:]), 0, 0).strftime(_ISO_S) for _step in range(19)]
    draw.shuffle(cells)
    return cells


def _span(draw: random.Random, days: int, rows: int) -> "list[str]":
    first = datetime.date(2023, 3, 6)
    window = [first + datetime.timedelta(days=step) for step in range(days)]
    return [moment.strftime(_ISO_S) for moment in _hourly(draw, window, _ED, rows)]


def _thousand() -> "dict[str, tuple[list[str], str]]":
    """The 1,000-row table: the design's seven columns and its four spans."""
    draw = random.Random(71001)
    return {
        "vitals": (_vitals(draw, 1000), _ISO_S),
        "appointments": ([moment.strftime(_ISO_T) for moment in _clinic(draw, [d for d in _TWO_YEARS if d.weekday() < 5], 1000)], _ISO_T),
        "admitted": ([moment.strftime(_US) for moment in _hourly(draw, _TWO_YEARS, _ADMITTED, 1000)], _US),
        "arrivals": ([moment.strftime(_ISO_T) for moment in _hourly(draw, _YEAR, _ED, 1000)], _ISO_T),
        "clinic": ([moment.strftime(_SLASHED) for moment in _clinic(draw, _WEEKDAYS, 1000)], _SLASHED),
        "discharges": ([moment.strftime(_DAY_FIRST) for moment in _hourly(draw, _YEAR, _DISCHARGE, 1000)], _DAY_FIRST),
        "midtail": (_midtail(draw, 1000), _ISO_S),
        "span_1d": (_span(draw, 1, 1000), _ISO_S),
        "span_3d": (_span(draw, 3, 1000), _ISO_S),
        "span_7d": (_span(draw, 7, 1000), _ISO_S),
        "span_14d": (_span(draw, 14, 1000), _ISO_S),
    }


_WITHHELD_SPANS = ("span_1d", "span_3d", "span_7d")


def _panel(draw: random.Random, rows: int) -> "list[str]":
    """Lab results in panels: one draw instant holds 1 to 25 result rows."""
    sizes = (1, 2, 3, 4, 5, 6, 8, 10, 14, 20, 25)
    weights = (30, 10, 8, 8, 6, 6, 8, 6, 8, 6, 4)
    found: "list[str]" = []
    seen: "set[datetime.datetime]" = set()
    while len(found) < rows:
        moment = _at(draw.choice(_TWO_YEARS), draw.choices(range(24), weights=_LAB)[0], draw.randrange(60), draw.randrange(60))
        if moment in seen or moment.time() == datetime.time(0, 0):
            continue
        seen.add(moment)
        found += [moment.strftime(_ISO_S)] * min(draw.choices(sizes, weights=weights)[0], rows - len(found))
    draw.shuffle(found)
    return found


def _ten_thousand() -> "dict[str, tuple[list[str], str]]":
    """The 10,000-row table PLAN.md's row adds: the 10-week clinic, a burst,
    every cell on the hour and a half-hour grid."""
    draw = random.Random(71002)
    burst: "list[str]" = []
    for _row in range(10000):
        if draw.random() < 0.06:
            burst += [_at(_TWO_YEARS[160], 14 + draw.randrange(4), draw.randrange(60), draw.randrange(60)).strftime(_ISO_S)]
        else:
            burst += [moment.strftime(_ISO_S) for moment in _hourly(draw, _TWO_YEARS, _ED, 1)]
    return {
        "ten_week_clinic": ([moment.strftime(_SLASHED) for moment in _clinic(draw, [d for d in _TEN_WEEKS if d.weekday() < 5], 10000)], _SLASHED),
        "burst": (burst, _ISO_S),
        "on_the_hour": ([_at(draw.choice(_TWO_YEARS), draw.choices(range(24), weights=_ED)[0], 0).strftime(_ISO_M) for _row in range(10000)], _ISO_M),
        "half_hour_grid": ([_at(draw.choice(_YEAR), draw.choices(range(24), weights=_LAB)[0], draw.choice((0, 30))).strftime(_ISO_M) for _row in range(10000)], _ISO_M),
    }


def _the_1970_clinic(tied: bool = False) -> "tuple[list[str], str]":
    """A clinic whose system wrote one in twenty unknown visits as the Unix epoch.

    `tied` books two visits on one slot where the high tail of a floor of
    36 ends -- the 36th latest visit moved onto the 37th's slot -- so that
    tail runs one row past the floor and holds a tie group (G7.3b step 7).
    """
    draw = random.Random(71003)
    cells = [moment.strftime(_ISO_M) for moment in _clinic(draw, _WEEKDAYS, 1000)]
    for place in range(len(cells)):
        if draw.random() < 0.05:
            cells[place] = "1970-01-01 00:00"
    if tied:
        latest = sorted(range(len(cells)), key=lambda place: cells[place], reverse=True)
        cells[latest[35]] = cells[latest[36]]
    return cells, _ISO_M


def _or_starts() -> "dict[str, tuple[list[str], str]]":
    """Operating-room starts: ten rooms at 07:30 on each of 100 weekdays, and one
    to three cases a room from 09:00 on five-minute slots (the design skeptic's B2)."""
    draw = random.Random(71005)
    found: "list[str]" = []
    for day in [day for day in _TWO_YEARS if day.weekday() < 5][:100]:
        for _room in range(10):
            found += [_at(day, 7, 30).strftime(_US)]
            for _case in range(draw.randint(1, 3)):
                minutes = 9 * 60 + 5 * draw.randrange(96)
                found += [_at(day, minutes // 60, minutes % 60).strftime(_US)]
    return {"or_start": (found, _US)}


def _table_text(columns: "dict[str, tuple[list[str], str]]") -> str:
    names = list(columns)
    rows = len(columns[names[0]][0])
    lines = [",".join(names)]
    for row in range(rows):
        lines += [",".join(columns[name][0][row] for name in names)]
    return "\n".join(lines) + "\n"


def _cells(text: str, name: str) -> "list[str]":
    lines = text.splitlines()
    place = lines[0].split(",").index(name)
    return [line.split(",")[place] for line in lines[1:] if line]


# -- the statistics ----------------------------------------------------------


def _hours(cells: "list[str]", form: str) -> "list[int]":
    """How many cells fall on each hour of the written clock, the 12-hour
    face read as `%I` reads it."""
    counts = [0] * 24
    for cell in cells:
        try:
            moment = datetime.datetime.strptime(cell, form)
        except ValueError:
            continue
        counts[moment.hour] += 1
    return counts


def _tvd(first: "list[int]", second: "list[int]") -> float:
    one, two = sum(first), sum(second)
    return 0.5 * sum(abs(a / one - b / two) for a, b in zip(first, second))


def _statistics_failures(block: dict, real: "list[str]", twin: "list[str]", form: str) -> "list[str]":
    """BOUND, CAP and SHAPE on the hour TVD, for one twin.

    BOUND holds everywhere: the twin's hour TVD lies within (the rows of a
    tail that lists no values -- a listed tail stands on its values -- plus
    the cells of every group counting several hours) / parsed. CAP, at a
    floor of eleven and 1,000 rows or more: the twin's hour TVD itself at
    most 0.10 below 10,000 rows and 0.02 from them -- on the twin, not on
    the bound, which a column whose night hours hold a few rows each
    widens with its merged groups (the 1,000-row vitals' bound is 0.106,
    its twins' TVD 0.03). SHAPE: the twin's gap at most a quarter of the
    real column's distance from flat wherever that distance is three
    times its sampling scale.
    """
    parsed = block["n_present"] - block["n_unparsed"]
    tails = sum(
        block[side]["rows"]
        for side in ("low_tail", "high_tail")
        if block[side] is not None and block[side]["values"] is None
    )
    merged = sum(group["count"] for group in block["hour_census"] if group["last"] > group["first"])
    real_hours, twin_hours = _hours(real, form), _hours(twin, form)
    gap = _tvd(real_hours, twin_hours)
    bound = (tails + merged) / parsed
    found: "list[str]" = []
    if gap > bound + 1e-12:
        found += [f"BOUND {gap:.4f} > {bound:.4f}"]
    if parsed >= 1000:
        cap = 0.02 if parsed >= 10000 else 0.10
        if gap > cap:
            found += [f"CAP {gap:.4f} > {cap}"]
    total = sum(real_hours)
    share = [count / total for count in real_hours]
    flat = 0.5 * sum(abs(value - 1 / 24) for value in share)
    scale = 0.5 * sum((value * (1 - value) / total) ** 0.5 for value in share)
    if flat > 3 * scale and gap > 0.25 * flat:
        found += [f"SHAPE {gap:.4f} > a quarter of {flat:.4f}"]
    return found


# -- the merge, recomputed from the cells -----------------------------------


def _seconds(cell: str, form: str) -> int:
    moment = datetime.datetime.strptime(cell, form)
    return (moment.date() - datetime.date(1970, 1, 1)).days * DAY + moment.hour * 3600 + moment.minute * 60 + moment.second


def _merge(bins: "list[int]", sure: "list[int]", line: int) -> "list[tuple[int, int, int]]":
    """The one merge rule, restated here: every hour alone and each run of
    empty hours one group; while a group's count, or its count less its
    sure cells, is one to line - 1 (or below nought), the shortest joins its
    smaller non-zero neighbour (the earlier on a tie), never across
    midnight. One group over every hour, or a short group with no
    neighbour, publishes nothing."""
    groups: "list[list[int]]" = []
    hour = 0
    while hour < 24:
        if bins[hour]:
            groups += [[hour, hour, bins[hour], sure[hour]]]
            hour += 1
            continue
        end = hour
        held = sure[hour]
        while end + 1 < 24 and bins[end + 1] == 0:
            end += 1
            held += sure[end]
        groups += [[hour, end, 0, held]]
        hour = end + 1

    def short(group: "list[int]") -> bool:
        left = group[2] - group[3]
        return (0 < group[2] < line) or left < 0 or (0 < left < line)

    while True:
        shorts = [index for index in range(len(groups)) if short(groups[index])]
        if not shorts:
            break
        pick = min(shorts, key=lambda index: (groups[index][2], index))
        before = next((index for index in range(pick - 1, -1, -1) if groups[index][2]), None)
        after = next((index for index in range(pick + 1, len(groups)) if groups[index][2]), None)
        if before is None and after is None:
            return []
        if after is None or (before is not None and groups[before][2] <= groups[after][2]):
            start, stop = before, pick
        else:
            start, stop = pick, after
        joined = [groups[start][0], groups[stop][1], sum(g[2] for g in groups[start:stop + 1]), sum(g[3] for g in groups[start:stop + 1])]
        groups = groups[:start] + [joined] + groups[stop + 1:]
    if len(groups) == 1:
        return []
    return [(first, last, count) for first, last, count, _sure in groups]


def _expected_groups(block: dict, cells: "list[str]", form: str, line: int) -> "list[tuple[int, int, int]]":
    """The census the cells give, recomputed: the body's hours, and the sure
    cells -- both boundaries and every rung in their hours, and the cells at
    midnight the description counts less those of a tail listing only
    midnight values."""
    instants = sorted(_seconds(cell, form) for cell in cells if cell)
    parsed = len(instants)
    low, high = block["low_tail"]["rows"], block["high_tail"]["rows"]
    body = instants[low: parsed - high]
    bins = [0] * 24
    for instant in body:
        bins[(instant // 3600) % 24] += 1
    published = [(low, instants[low]), (parsed - 1 - high, instants[parsed - 1 - high])]
    for percent, key in ((1, "p01"), (5, "p05"), (10, "p10"), (25, "p25"), (50, "p50"), (75, "p75"), (90, "p90"), (95, "p95"), (99, "p99")):
        if block["date_percentiles"][key] is not None:
            rank = min(parsed - 1, ((parsed - 1) * percent) // 100)
            published += [(rank, instants[rank])]
    known: "dict[int, int]" = dict(published)
    ordered = sorted(published)
    for (first, here), (last, there) in zip(ordered, ordered[1:]):
        if here == there:
            for rank in range(first, last + 1):
                known[rank] = here
    sure = [0] * 24
    zero = 0
    for instant in known.values():
        if instant % DAY == 0:
            zero += 1
        else:
            sure[(instant // 3600) % 24] += 1
    counted = block["n_at_midnight"]
    if counted is not None:
        for side in ("low_tail", "high_tail"):
            values = block[side]["values"]
            if values and all(value.endswith("00:00:00") for value in values):
                counted -= block[side]["rows"]
        zero = max(zero, max(counted, 0))
    sure[0] += zero
    return _merge(bins, sure, line)


def _groups(block: dict) -> "list[tuple[int, int, int]]":
    return [(group["first"], group["last"], group["count"]) for group in block["hour_census"]]


# -- the battery's clauses -----------------------------------------------------


@pytest.fixture(scope="module")
def thousand(tmp_path_factory: pytest.TempPathFactory) -> "tuple[kpi_shapes.Described, dict[str, tuple[list[str], str]], str]":
    columns = _thousand()
    text = _table_text(columns)
    described = kpi_shapes.describe(tmp_path_factory.mktemp("hours"), "hours", text, LINE)
    return described, columns, text


def test_the_hour_battery_publishes_its_census(thousand) -> None:
    """Every column in scope publishes, its groups the merge recomputed from its cells.

    The census's groups equal `_merge` over the body's hours and the sure
    cells recomputed here; the loader's own check
    (`calendar_clock.hour_breach`) finds nothing at the census line and at
    a floor of one; the 1-, 3- and 7-day spans -- their middle half
    shorter than four days -- are withheld with the span sentence and
    publish no census, and the 14-day span publishes. The real table meets
    its own description.
    """
    described, columns, text = thousand
    assert kpi_shapes.missed(kpi_shapes.measure(described, text, "real.csv")) == []
    for name, (cells, form) in columns.items():
        block = described.block(name)
        if name in _WITHHELD_SPANS:
            assert block["hour_census"] == [], name
            said = [
                note for note in described.document["publication_notes"]
                if note["column"] == name and "fewer than four days" in note["note"]
            ]
            assert len(said) == 1, name
            continue
        groups = _groups(block)
        assert groups, name
        assert groups == _expected_groups(block, cells, form, LINE), name
        body = block["n_present"] - block["n_unparsed"] - block["low_tail"]["rows"] - block["high_tail"]["rows"]
        assert calendar_clock.hour_breach(tuple(groups), body, LINE, [0] * 24) is None, name
        assert calendar_clock.hour_breach(tuple(groups), body, 2, [0] * 24) is None, name
        assert all(calendar_rules.calendar_floor_ok(count, LINE) for _f, _l, count in groups), name


def test_red_when_the_span_rule_is_withdrawn(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """HC4's mutant: with no span rule a three-day column publishes the hours of three dates."""
    monkeypatch.setattr(calendar_clock, "span_long_enough", lambda _low, _high: True)
    cells = _span(random.Random(5), 3, 1000)
    described_block = _described_alone(tmp_path, cells, LINE, loads=False)
    assert described_block["hour_census"] != []


def _described_alone(folder: pathlib.Path, cells: "list[str]", floor: int, loads: bool = True, twelve: bool = False) -> dict:
    """One column described the way `synthtwin profile` describes it; its block."""
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(folder, "real.csv", "seen_at\n" + "\n".join(cells) + "\n")
    settings = taxonomy.Settings(
        small_cell_floor=floor, forced_twelve_hour_clocks=("seen_at",) if twelve else ()
    )
    document = profile.build_document(reading.read_table(str(table), small_cell_floor=floor), settings, [], [], [])
    if loads:
        contract.load_profile(str(fixtures.write_profile(folder, "real-profile.json", document)))
    return next(block for block in document["columns"] if block["name"] == "seen_at")


@pytest.mark.parametrize("seed", [0, 4])
def test_the_hour_battery_twins_meet_their_census(thousand, seed: int, monkeypatch: pytest.MonkeyPatch) -> None:
    """Nothing missed, V5-H1 held, the count at midnight exact, BOUND, CAP and SHAPE; weekdays and counts kept.

    Every twin validates with nothing MISSED, V5-H1 HELD on every
    published column and a published `n_at_midnight` held exactly; its
    hour statistics lie inside BOUND, CAP and SHAPE
    (`_statistics_failures`); and its weekdays and count of different
    values are the ones the same seed writes with the pass withdrawn --
    the pass moves no rank to another weekday where no weekday census
    stands, and puts back every value it splits.
    """
    described, columns, text = thousand
    written = kpi_shapes.twin_text(described, seed)
    outcome = kpi_shapes.measure(described, written, f"twin-{seed}.csv")
    assert kpi_shapes.missed(outcome) == [], seed
    held = [check for check in outcome.checks if check.fact == "datetime.hour_census"]
    published = [name for name in columns if described.block(name)["hour_census"]]
    assert len(held) == len(published) and all(check.verdict == validation.HELD for check in held)
    monkeypatch.setattr(generation, "_hour_settled", lambda column, facts, ordinals, *rest, **named: (ordinals, []))
    flat = kpi_shapes.twin_text(described, seed)
    monkeypatch.undo()
    for name, (cells, form) in columns.items():
        twin = _cells(written, name)
        if name in published:
            assert _statistics_failures(described.block(name), cells, twin, form) == [], (name, seed)
        without = _cells(flat, name)
        assert len(set(twin)) == len(set(without)), (name, seed)
        days = sorted(datetime.datetime.strptime(cell, form).weekday() for cell in twin if cell)
        assert days == sorted(datetime.datetime.strptime(cell, form).weekday() for cell in without if cell), (name, seed)


def test_a_flat_twin_misses_the_hour_census(thousand, monkeypatch: pytest.MonkeyPatch) -> None:
    """The pass withdrawn, every hour census is MISSED, and no count below the line is printed."""
    described, columns, _text = thousand
    monkeypatch.setattr(generation, "_hour_settled", lambda column, facts, ordinals, *rest, **named: (ordinals, []))
    written = kpi_shapes.twin_text(described, 0)
    outcome = kpi_shapes.measure(described, written, "flat.csv")
    checks = [check for check in outcome.checks if check.fact == "datetime.hour_census"]
    assert checks and all(check.verdict == validation.MISSED for check in checks)
    for check in checks:
        for shown in check.achieved.split(", "):
            last = shown.split(" ")[-1]
            if last.isdigit():
                assert int(last) == 0 or int(last) >= LINE, check.achieved


def test_validating_never_produces_an_hour_census(thousand, monkeypatch: pytest.MonkeyPatch) -> None:
    """The validator counts the file's body against the PUBLISHED groups and asks no producer."""
    described, _columns, _text = thousand
    written = kpi_shapes.twin_text(described, 0)

    def refused(*_arguments: object, **_named: object) -> None:
        raise AssertionError("a validate run produced an hour census")

    monkeypatch.setattr(taxonomy, "hour_decision", refused)
    outcome = kpi_shapes.measure(described, written, "twin.csv")
    held = [check for check in outcome.checks if check.fact == "datetime.hour_census"]
    assert held and all(check.verdict == validation.HELD for check in held)


# -- the ten-thousand-row table and the panel --------------------------------


@pytest.fixture(scope="module")
def ten_thousand(tmp_path_factory: pytest.TempPathFactory) -> "tuple[kpi_shapes.Described, dict[str, tuple[list[str], str]], str]":
    columns = _ten_thousand()
    text = _table_text(columns)
    described = kpi_shapes.describe(tmp_path_factory.mktemp("tenk"), "tenk", text, LINE)
    return described, columns, text


def test_whole_units_the_census_cannot_hold_are_split_and_put_back(ten_thousand) -> None:
    """The 10-week clinic, a burst, every cell on the hour and a half-hour grid, at 10,000 rows.

    Tied units -- seven in ten clinic visits on :00 or :30, every cell on
    the hour -- leave no group room for a whole unit, and the shared
    steps alone leave the census unmet; G7.3g's own steps meet it and put
    the count of different values back. Seed 0, nothing missed, every
    statistic inside its bound.
    """
    described, columns, _text = ten_thousand
    written = kpi_shapes.twin_text(described, 0)
    outcome = kpi_shapes.measure(described, written, "twin-0.csv")
    assert kpi_shapes.missed(outcome) == []
    for name, (cells, form) in columns.items():
        assert described.block(name)["hour_census"], name
        assert _statistics_failures(described.block(name), cells, _cells(written, name), form) == [], name


def _spread_of(twin: "generation.Twin", name: str) -> "generation.Remark":
    """The twin's one sentence on how a column's dates are spread across the calendar."""
    return next(
        remark for remark in twin.remarks
        if remark.column == name and "published ladder is met" in remark.held
    )


def test_red_without_the_hour_steps(ten_thousand, monkeypatch: pytest.MonkeyPatch) -> None:
    """Mutant: G7.3g's own steps withdrawn -- the shared steps alone miss the 10-week clinic.

    And the twin SAYS so (the lane's skeptic, finding 3 (g)): one deviation names
    `hour_census` on that column, and its sentence on how the dates are spread says the counts
    per hour are not met, never that they are.
    """
    described, _columns, _text = ten_thousand
    monkeypatch.setattr(generation, "_clock_left_their_groups", lambda *_arguments: None)
    twin = generation.generate(described.loaded, 0)
    written = rendering.twin_csv(twin)
    missed = kpi_shapes.missed(kpi_shapes.measure(described, written, "twin.csv"))
    assert "ten_week_clinic:hour_census.groups" in missed, missed
    named = [entry for entry in twin.deviations if entry.column == "ten_week_clinic"]
    assert [entry.fact for entry in named] == [calendar_clock.HOUR_CENSUS], named
    spread = _spread_of(twin, "ten_week_clinic")
    assert generation._SPREAD_HOUR_MISSED in spread.note
    assert generation._SPREAD_HOUR_MET not in spread.held


def test_a_census_counting_hours_together_says_so(thousand) -> None:
    """Where a published group counts several hours, the twin's sentence says its split among
    them is its own; where every group is one hour, it says nothing of the kind, and every
    published census is said to be met (the lane's skeptic, finding 3 (g))."""
    described, columns, _text = thousand
    twin = generation.generate(described.loaded, 0)
    together = 0
    for name in columns:
        census = described.block(name)["hour_census"]
        if not census:
            continue
        spread = _spread_of(twin, name)
        assert generation._SPREAD_HOUR_MET in spread.held, name
        merged = any(group["first"] != group["last"] and group["count"] > 0 for group in census)
        assert (generation._SPREAD_HOURS_TOGETHER in spread.note) == merged, name
        together += merged
    assert together >= 1


@pytest.fixture(scope="module")
def panel(tmp_path_factory: pytest.TempPathFactory) -> "tuple[kpi_shapes.Described, list[str]]":
    cells = _panel(random.Random(71004), 2000)
    described = kpi_shapes.describe(tmp_path_factory.mktemp("panel"), "panel", "drawn_at\n" + "\n".join(cells) + "\n", LINE)
    return described, cells


def test_a_lab_panel_keeps_its_census_and_its_count(panel) -> None:
    """2,000 results on 1 to 25 rows an instant: met, and the count of different values kept."""
    described, cells = panel
    for seed in (0, 4):
        written = kpi_shapes.twin_text(described, seed)
        assert kpi_shapes.missed(kpi_shapes.measure(described, written, f"twin-{seed}.csv")) == [], seed
        assert _statistics_failures(described.block("drawn_at"), cells, _cells(written, "drawn_at"), _ISO_S) == []


def test_red_without_put_back(panel, monkeypatch: pytest.MonkeyPatch) -> None:
    """Mutant: PUT BACK withdrawn -- the panel's split units leave the count long."""
    described, _cells_of = panel
    monkeypatch.setattr(generation, "_clock_count_put_back", lambda *_arguments: None)
    written = kpi_shapes.twin_text(described, 0)
    missed = kpi_shapes.missed(kpi_shapes.measure(described, written, "twin.csv"))
    assert "drawn_at:distinct.n_distinct" in missed, missed


def test_or_starts_meet_their_census_through_relief(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """OR starts: ten rooms at 07:30 on 100 weekdays alone (the design skeptic's B2).

    A rank before the 07:30 rung on the last day of its gap has hours 0
    to 6, counted empty, and hour 7, full, on its own day, and no other
    day of its weekday inside the gap, so SAMEDAY and the escape leave it
    where it is; RELIEF moves a unit of hour 7 to a later hour of its own
    day and the rank into hour 7 (G7.3g step 3). Seeds 0 and 1 at a floor
    of 11, nothing missed. Mutant: RELIEF withdrawn, the census missed.
    """
    columns = _or_starts()
    cells, form = columns["or_start"]
    described = kpi_shapes.describe(tmp_path, "or", _table_text(columns), LINE)
    assert described.block("or_start")["hour_census"], "the OR starts publish no census"
    for seed in (0, 1):
        written = kpi_shapes.twin_text(described, seed)
        assert kpi_shapes.missed(kpi_shapes.measure(described, written, f"twin-{seed}.csv")) == [], seed
        assert _statistics_failures(described.block("or_start"), cells, _cells(written, "or_start"), form) == [], seed
    monkeypatch.setattr(generation, "_clock_relieved", lambda *_arguments: None)
    written = kpi_shapes.twin_text(described, 0)
    missed = kpi_shapes.missed(kpi_shapes.measure(described, written, "mutant.csv"))
    assert "or_start:hour_census.groups" in missed, missed


# -- rule 4 and its amendment ---------------------------------------------------


def test_rule_4_holds_the_midnight_group(thousand, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The body's cells at midnight are sure cells of hour 0; a producer without rule 4 is refused HC5.

    The witness's hour 0 holds its 19 body cells at midnight and a few other
    cells: with rule 4 the remainder is short, so hour 0 joins hour 1;
    a description written without it publishes hour 0 alone, and the
    loader, which asks rule 4, refuses it by HC5.
    """
    described, columns, _text = thousand
    groups = _groups(described.block("midtail"))
    assert groups[0][0] == 0 and groups[0][1] >= 1, groups
    monkeypatch.setattr(calendar_clock, "midnight_sure", lambda counted, tails: None)
    cells, _form = columns["midtail"]
    block = _described_alone(tmp_path, cells, LINE, loads=False)
    assert _groups(block)[0][:2] == (0, 0), _groups(block)
    monkeypatch.undo()
    document = copy.deepcopy(described.document)
    for entry in document["columns"]:
        if entry["name"] == "midtail":
            entry["hour_census"] = block["hour_census"]
    assert "HC5" in _refusal(tmp_path, document)


def test_a_sentinel_tail_is_not_charged_to_the_body(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The 1970 clinic: its cells at midnight are its low tail's, so hours 0 to 7 stay a group of nought.

    The design skeptic's M1: 1970-01-01 is not read as missing, the low
    tail IS the sentinel, and charging its rows to the body's hour 0 put
    clinic visits at night. Mutant: every midnight charged to the body.
    """
    cells, form = _the_1970_clinic()
    block = _described_alone(tmp_path / "kept", cells, LINE)
    assert block["low_tail"]["values"] == ["1970-01-01 00:00:00"], block["low_tail"]
    assert _groups(block)[0] == (0, 7, 0), _groups(block)
    monkeypatch.setattr(calendar_clock, "midnight_sure", lambda counted, tails: counted)
    charged = _described_alone(tmp_path / "charged", cells, LINE, loads=False)
    assert _groups(charged)[0][2] > 0, _groups(charged)


def test_no_tie_group_stands_at_a_midnight_the_listed_tails_hold(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The 1970 clinic at a floor of 36: its twins write exactly the published count at midnight.

    The epoch tail holds every midnight the description counts, so the
    high tail's tie group stands at none (G7.3b step 7, landing 3b.2-H):
    before, it stood at the nearest midnight and the twin wrote two more
    than published, `midnight.count` MISSED at every seed. Mutant: the
    group put at a midnight whatever the listed tails hold.
    """
    cells, _form = _the_1970_clinic(tied=True)
    described = kpi_shapes.describe(tmp_path, "clinic", "seen_at\n" + "\n".join(cells) + "\n", 36)
    block = described.block("seen_at")
    assert block["n_at_midnight"] == block["low_tail"]["rows"]
    # The high tail holds a tie group: one row past the floor.
    assert block["high_tail"]["rows"] == 37 and block["high_tail"]["values"] is None
    for seed in (0, 1, 2):
        written = kpi_shapes.twin_text(described, seed)
        assert kpi_shapes.missed(kpi_shapes.measure(described, written, f"twin-{seed}.csv")) == [], seed
    monkeypatch.setattr(generation, "_midnight_past_the_listed", lambda facts: True)
    written = kpi_shapes.twin_text(described, 0)
    assert "seen_at:midnight.count" in kpi_shapes.missed(kpi_shapes.measure(described, written, "mutant.csv"))
    monkeypatch.undo()
    # ...and the CHECKER draws each tail's strata from the construction the generator runs:
    # the high tail's tie group stands at its own distance in both (the lane's skeptic,
    # finding 3 (d)). With the amendment withdrawn from the validator alone, its window put
    # the group at the nearest midnight, 558 minutes in where the generator stands it at 474.
    column = next(column for column in described.loaded.columns if column.name == "seen_at")
    facts = column.facts
    assert isinstance(facts, contract.DatetimeFacts)
    layout = generation._date_layout(column, facts, column.n_present - facts.n_unparsed, 36)
    assert layout.high is not None
    assert validation._date_tail_windows(column, facts, 36, "")["high"] == (list(layout.high.near), list(layout.high.far))


def _refusal(folder: pathlib.Path, document: dict) -> str:
    """What the loader says when it refuses this document."""
    path = fixtures.write_profile(folder, "refused-profile.json", document)
    with pytest.raises(errors.ProfileError) as raised:
        contract.load_profile(str(path))
    return f"{raised.value}"


# -- the loader's six rules -------------------------------------------------------


def _edited(described: kpi_shapes.Described, name: str, **changes: object) -> dict:
    document = copy.deepcopy(described.document)
    for entry in document["columns"]:
        if entry["name"] == name:
            entry.update(changes)
    return document


def test_hc1_the_groups_cover_the_hours_in_order(thousand, tmp_path: pathlib.Path) -> None:
    described, _columns, _text = thousand
    groups = described.block("arrivals")["hour_census"]
    wrapped = [dict(groups[0], first=1)] + groups[1:-1] + [dict(groups[-1], last=0)]
    assert "HC1" in _refusal(tmp_path, _edited(described, "arrivals", hour_census=wrapped))


def test_hc2_every_count_is_nought_or_at_the_line(thousand, tmp_path: pathlib.Path) -> None:
    described, _columns, _text = thousand
    groups = copy.deepcopy(described.block("arrivals")["hour_census"])
    groups[0]["count"] -= groups[0]["count"] - 5
    groups[1]["count"] += described.block("arrivals")["hour_census"][0]["count"] - 5
    assert "HC2" in _refusal(tmp_path, _edited(described, "arrivals", hour_census=groups))


def test_hc3_the_scope_and_the_total(thousand, tmp_path: pathlib.Path) -> None:
    """A total off the body is refused; and a census on a column read on the shared clock,
    or one wholly at midnight, is refused by the reader before any count is asked."""
    described, _columns, _text = thousand
    groups = copy.deepcopy(described.block("arrivals")["hour_census"])
    groups[0]["count"] += LINE
    assert "HC3" in _refusal(tmp_path, _edited(described, "arrivals", hour_census=groups))
    column = next(column for column in described.loaded.columns if column.name == "arrivals")
    facts = column.facts
    assert isinstance(facts, contract.DatetimeFacts)
    mapping = {"hour_census": described.block("arrivals")["hour_census"]}
    for scope in ({"datetimes_read_at": "utc"}, {"all_at_midnight": True}, {"low_tail": None}):
        with pytest.raises(errors.ProfileError) as raised:
            contract._hour_census(
                mapping, "here", LINE, column.n_present, column.n_distinct, (), (),
                dataclasses.replace(facts, **scope),
            )
        assert contract.INVARIANTS["HC3"] in f"{raised.value}", scope


def test_hc4_the_middle_half_spans_four_days(thousand, tmp_path: pathlib.Path) -> None:
    described, _columns, _text = thousand
    span = described.block("span_3d")
    body = span["n_present"] - span["low_tail"]["rows"] - span["high_tail"]["rows"]
    census = [{"first": 0, "last": 11, "count": 0}, {"first": 12, "last": 23, "count": body}]
    said = _refusal(tmp_path, _edited(described, "span_3d", hour_census=census))
    assert contract.INVARIANTS["HC4"] in said, said


def test_hc5_a_group_holds_its_sure_cells(thousand, tmp_path: pathlib.Path) -> None:
    """A group the rest of the description places more cells in than it counts is refused."""
    described, _columns, _text = thousand
    block = described.block("vitals")
    groups = copy.deepcopy(block["hour_census"])
    assert groups[0]["first"] == 0 and block["n_at_midnight"] is not None
    shift = groups[0]["count"] - LINE
    groups[0]["count"] -= shift
    groups[1]["count"] += shift
    assert "HC5" in _refusal(tmp_path, _edited(described, "vitals", hour_census=groups))


def test_hc6_one_storage_per_workbook_column() -> None:
    """HC6 reads the published cell classes: two value classes holding cells refuse a census."""
    assert calendar_rules.published_one_way({"date": 300, "text": 0}) is True
    assert calendar_rules.published_one_way({"date": 300, "text": 12}) is False
    assert "HC6" in contract.INVARIANTS


# -- the producer's scope and its sentences (the lane's skeptic, finding 3 (a) and (b)) ---

_HOURS_SAID = "hours of the day this column's values fall on"


def _hour_sentences(document: dict, name: str) -> "list[str]":
    """Every sentence of a description that speaks of one column's hours of the day."""
    return [
        entry["note"] for entry in document["publication_notes"]
        if entry["column"] == name and _HOURS_SAID in entry["note"]
    ]


def test_a_column_wholly_at_midnight_publishes_no_census_and_says_nothing(tmp_path: pathlib.Path) -> None:
    """HC3's scope in the producer: moments every one written at 00:00:00 count no hour.

    Two years of moments, each at midnight: the column is read wholly at midnight, publishes
    `[]`, says nothing of its hours of the day, and its description loads. Mutant: the producer
    asking such a column, which publishes a census its own loader refuses (HC3).
    """
    draw = random.Random(40005)
    cells = [f"{draw.choice(_TWO_YEARS).isoformat()} 00:00:00" for _row in range(1000)]
    described = kpi_shapes.describe(tmp_path, "at_midnight", "seen_at\n" + "\n".join(cells) + "\n", LINE)
    block = described.block("seen_at")
    assert block["all_at_midnight"] is True
    assert block["hour_census"] == []
    assert _hour_sentences(described.document, "seen_at") == []


def test_a_census_withheld_says_why(tmp_path: pathlib.Path) -> None:
    """NF89 and NF92 said, each in its own sentence, and no census published.

    A hundred moments over two years at a floor of 50: two tails need at least 101 values,
    fifty beyond each boundary, so neither is published and nothing lies between them to
    count (NF89). Two hundred and fifty at a floor of 60: the hundred-odd values between the
    tails cannot be grouped short of the whole day with every count nought or at least 60,
    and the one merge rule leaves them one group over the whole day, which NF92 says.
    Mutants: either census withheld without its sentence.
    """
    draw = random.Random(40006)
    cells = [
        _at(draw.choice(_TWO_YEARS), draw.choices(range(24), weights=_ED)[0], draw.randrange(60)).strftime(_ISO_M)
        for _row in range(250)
    ]
    for rows, floor, said in ((100, 50, "the column has no tails"), (250, 60, "leaves one group over the whole day")):
        text = "seen_at\n" + "\n".join(cells[:rows]) + "\n"
        described = kpi_shapes.describe(tmp_path / f"floor-{floor}", "few", text, floor)
        assert described.block("seen_at")["hour_census"] == [], floor
        sentences = _hour_sentences(described.document, "seen_at")
        assert len(sentences) == 1 and said in sentences[0], (floor, sentences)


def _book_of_moments(rows: int, seed: int, typed: int) -> bytes:
    """One sheet, one column `seen_at` of moments stored as moments, but every `typed`-th cell
    typed in as text, written as the stored ones are shown."""
    openpyxl = crosscheck.fixture_writer()
    book = openpyxl.Workbook()
    sheet = book.active
    sheet.title = "Data"
    sheet.cell(row=1, column=1, value="seen_at")
    draw = random.Random(seed)
    for row in range(rows):
        moment = _at(draw.choice(_YEAR), draw.choices(range(24), weights=_ED)[0], draw.randrange(60))
        if typed and row % typed == 0:
            sheet.cell(row=row + 2, column=1, value=moment.strftime(_ISO_M + ":00"))
        else:
            cell = sheet.cell(row=row + 2, column=1, value=moment)
            cell.number_format = "yyyy-mm-dd hh:mm:ss"
    held = io.BytesIO()
    book.save(held)
    return held.getvalue()


def test_a_workbook_storing_its_moments_two_ways_publishes_no_census(tmp_path: pathlib.Path) -> None:
    """HC6 in the producer (NF91): the workbook reads such a column back differently cell by cell.

    A thousand moments stored as moments, every twentieth typed in as text: no census, and the
    sentence says the workbook stores its values in more than one way; stored one way, the
    same moments publish theirs. Mutant: the producer not asking how the column is stored.
    """
    descriptions = {}
    for typed in (0, 20):
        table = tmp_path / f"typed-{typed}.xlsx"
        table.write_bytes(_book_of_moments(1000, 40007, typed))
        document = profile.build_document(
            reading.read_table(str(table), small_cell_floor=LINE), taxonomy.Settings(small_cell_floor=LINE), [], [], []
        )
        descriptions[typed] = document
    one_way = next(block for block in descriptions[0]["columns"] if block["name"] == "seen_at")
    two_ways = next(block for block in descriptions[20]["columns"] if block["name"] == "seen_at")
    assert one_way["hour_census"], "stored one way, the moments publish their census"
    assert two_ways["hour_census"] == []
    sentences = _hour_sentences(descriptions[20], "seen_at")
    assert len(sentences) == 1 and "stores its values in more than one way" in sentences[0], sentences


# -- the sixteenth vectors file -----------------------------------------------------

_FILE = json.loads(VECTORS.read_text(encoding="utf-8"))


def _case(name: str) -> dict:
    return _FILE["cases"][name]


def _state(case: dict, module=generation):
    # A state's FIELD: the hour unless the case names another, its bins
    # `where`. The bin rule `bins` is read only by the shared steps, which
    # only the whole-pass case runs, and that case is of hours.
    state = module._WeekdayPass(
        moved=list(case["ordinals"]), held={}, where=tuple(case["where"]), facts=None,
        word="", widths=False, kinds={}, holes=frozenset(case["holes"]), lows=list(case["lows"]),
        highs=list(case["highs"]), keep_units=case["reachable"], unit=case.get("field_unit", 3600),
        step=case["written_unit"], day=DAY, bins="hour", period=len(case["where"]), keeps="day",
    )
    for ordinal in state.moved:
        module._weekday_tally(state.held, ordinal // state.step, 1)
        if state.unit != state.step:
            module._weekday_tally(state.units_held, ordinal // state.unit, 1)
    return state


def _answer(case: dict, module=generation) -> list:
    """What the product's step makes of a case, in the file's own form."""
    if case["step"] == "ties":
        # The ranks between two body pins of one sixtieth second: a layout
        # holding those pins alone, each its own text.
        pins = {rank: ordinal for rank, ordinal, _text in case["pins"]}
        texts = {rank: text for rank, _ordinal, text in case["pins"]}
        layout = module._DateLayout(
            parsed=max(pins) + 1, pins=pins, body=pins, lows=(), highs=(), low=None, high=None, texts=texts
        )
        tied = module._sixtieth_ties(layout)
        return [[rank, tied[rank][0], tied[rank][1]] for rank in sorted(tied)]
    if case["step"] == "half_day":
        return module.calendar_clock.half_day_distances(
            list(case["found"]), case["anchor"], case["unit"], case["low_side"], case["apart"], case["edge"]
        )
    state = _state(case, module)
    first, last = case["body"]
    pinned = list(case["pinned"])
    standing = tuple(case["standing"])
    anyday = case.get("anyday", False)
    kin = tuple(case.get("kin", ()))
    step = case["step"]
    if step == "pass":
        counts = list(case["counts"])
        if "sixtieths" in case:
            # The census as written: ranks the twin writes at a sixtieth second.
            counts = module._clock_counts_as_written(state, counts, list(case["sixtieths"]))
        module._clock_pass(
            state, counts, first, last, pinned, case["wanted"], standing, case["half_day"],
            anyday, kin,
        )
    elif step == "left":
        have = module._clock_found(state, len(case["counts"]), first, last)
        module._clock_left_their_groups(
            state, list(case["counts"]), have, first, last, pinned, standing, anyday, kin
        )
    elif step == "relief":
        have = module._clock_found(state, len(case["counts"]), first, last)
        module._clock_relieved(state, list(case["counts"]), have, first, last, pinned)
    elif step == "put_back":
        module._clock_count_put_back(state, first, last, pinned, case["wanted"], standing, anyday, kin)
    elif step == "midnight":
        module._clock_off_midnight(state, list(case["before"]), first, last, pinned)
    elif step == "tails":
        module._hour_tails_on_the_half_day(state, first, last, state.step)
    return state.moved


def _oracle():
    spec = importlib.util.spec_from_file_location("make_generation_reference_vectors_t2", ORACLE)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def _mutant(monkeypatch: pytest.MonkeyPatch, before: str, after: str):
    """The product's generation module with ONE source edit, built beside it (a step's
    mutant, applied exactly once: an edit that no longer applies turns the test red)."""
    assert SOURCE.count(before) == 1, before
    name = "synthtwin._generation_hour_mutant"
    module = types.ModuleType(name)
    module.__file__ = generation.__file__
    monkeypatch.setitem(sys.modules, name, module)
    exec(compile(SOURCE.replace(before, after), generation.__file__, "exec"), module.__dict__)
    return module


def _validation_mutant(monkeypatch: pytest.MonkeyPatch, before: str, after: str):
    """The product's validation module with ONE source edit, built beside it."""
    source = pathlib.Path(validation.__file__).read_text(encoding="utf-8")
    assert source.count(before) == 1, before
    name = "synthtwin._validation_hour_mutant"
    module = types.ModuleType(name)
    module.__file__ = validation.__file__
    monkeypatch.setitem(sys.modules, name, module)
    exec(compile(source.replace(before, after), validation.__file__, "exec"), module.__dict__)
    return module


class _Distances:
    """`calendar_clock` with ONE edit to step 10, for the distance cases' mutants."""

    def __init__(self, before: str, after: str) -> None:
        source = pathlib.Path(calendar_clock.__file__).read_text(encoding="utf-8")
        assert source.count(before) == 1, before
        name = "synthtwin._calendar_clock_mutant"
        module = types.ModuleType(name)
        module.__file__ = calendar_clock.__file__
        # Registered while it is built, as the generation and validation
        # mutants above are: since landing 3b.5 the module declares
        # dataclasses, which read their own module as they are made.
        sys.modules[name] = module
        try:
            exec(compile(source.replace(before, after), calendar_clock.__file__, "exec"), module.__dict__)
        finally:
            del sys.modules[name]
        self.calendar_clock = module


# Each case's mutant: the one edit that withdraws or bends the step the
# case freezes, and the case it turns red.
STEP_MUTANTS = {
    "SAMEDAY withdrawn": (
        "hour_same_day_clock",
        "                    target = _clock_target_on(\n                        state, here // span, here,",
        "                    target = None and _clock_target_on(\n                        state, here // span, here,",
    ),
    "the escape keeps no day standing": (
        "hour_escape_weekday",
        "                if (standing[calendar_rules.weekday_of(other)] == own) != kept:\n                    continue\n                if _weekday_width_kind(state, other * state.day) != width:\n                    continue\n                target = _clock_target_on(",
        "                if False:\n                    continue\n                if _weekday_width_kind(state, other * state.day) != width:\n                    continue\n                target = _clock_target_on(",
    ),
    "the escape takes no day of another weekday": (
        "hour_escape_any_day",
        "    for kept in [True, False] if anyday else [True]:\n        for away in range(1, max(day - first, last - day) + 1):\n            for other in (day - away, day + away):\n                if other < first or other > last or other in state.holes:\n                    continue\n                if (standing[calendar_rules.weekday_of(other)] == own) != kept:",
        "    for kept in [True]:\n        for away in range(1, max(day - first, last - day) + 1):\n            for other in (day - away, day + away):\n                if other < first or other > last or other in state.holes:\n                    continue\n                if (standing[calendar_rules.weekday_of(other)] == own) != kept:",
    ),
    "PUT BACK takes no day of another weekday": (
        "hour_put_back_any_day",
        "    for kept in [True, False] if anyday else [True]:\n        for away in range(1, max(day - first, last - day) + 1):\n            for other in (day - away, day + away):\n                if other < first or other > last or other in state.holes:\n                    continue\n                if (standing[calendar_rules.weekday_of(other)] == mine) != kept:",
        "    for kept in [True]:\n        for away in range(1, max(day - first, last - day) + 1):\n            for other in (day - away, day + away):\n                if other < first or other > last or other in state.holes:\n                    continue\n                if (standing[calendar_rules.weekday_of(other)] == mine) != kept:",
    ),
    "no SPLIT": (
        "hour_split",
        "for members in [unit] + ([[rank] for rank in unit] if size > 1 else []):\n                    if have[group] <= counts[group]:\n                        break\n                    here",
        "for members in [unit]:\n                    if have[group] <= counts[group]:\n                        break\n                    here",
    ),
    "RELIEF asks no full group": (
        "hour_relief",
        "        if _clock_target_on(state, parent, here, low, high, size, alone, counts) is None:\n            continue",
        "        if True:\n            continue",
    ),
    "RELIEF takes a unit of any size": (
        "hour_relief",
        "            if index in spent[middle] or len(relief) != size or first in relief:",
        "            if index in spent[middle] or len(relief) < size or first in relief:",
    ),
    "PUT BACK withdrawn": (
        "hour_put_back",
        "    count = _weekday_count(state)\n    if count > wanted:\n        by_parent",
        "    count = wanted\n    if count > wanted:\n        by_parent",
    ),
    "PUT BACK merges only on its own parent": (
        "hour_put_back",
        "    target = nearest_on(day * per_day + seat)\n    if target is not None:\n        return target\n    if kin:",
        "    target = nearest_on(day * per_day + seat)\n    if target is not None or True:\n        return target\n    if kin:",
    ),
    "the short count is not put back": (
        "hour_put_back_short",
        "    if count < wanted:\n        # A BIN WITH NO FREE WRITTEN UNIT IS ASKED ONCE",
        "    if count < wanted and False:\n        # A BIN WITH NO FREE WRITTEN UNIT IS ASKED ONCE",
    ),
    "units leave in rank order": (
        "hour_proportional",
        "        credit = credit + leaving\n        if credit >= len(units):",
        "        credit = credit + len(units)\n        if credit >= len(units):",
    ),
    "a written midnight is left": (
        "hour_off_midnight",
        "        target = _clock_nearest_free(state, start, low, high, len(members))\n        if target is None:\n            continue\n        for rank in members:",
        "        target = None\n        if target is None:\n            continue\n        for rank in members:",
    ),
    "the half day's tail ranks are left": (
        "hour_half_day_tails",
        "        if calendar_clock.morning(place, step):\n            continue\n        low, high",
        "        if True:\n            continue\n        low, high",
    ),
    "the whole pass without its own steps": (
        "hour_whole_pass",
        "    if found != counts:\n        _clock_left_their_groups(\n            state, counts, found, body_low, body_high, pinned, standing, False, kin\n        )\n    if found != counts:\n        _clock_relieved(",
        "    if found != counts and False:\n        _clock_left_their_groups(\n            state, counts, found, body_low, body_high, pinned, standing, False, kin\n        )\n    if found != counts and False:\n        _clock_relieved(",
    ),
    # THE STEP DETAILS no other state turned red (the lane's skeptic, finding 3 (h)).
    "PUT BACK merges onto a written midnight": (
        "hour_put_back_off_midnight",
        "            if _written_at_midnight(target, 0, state.step):\n                continue\n            found = (abs(target - ordinal), target)",
        "            found = (abs(target - ordinal), target)",
    ),
    "PUT BACK's short count moves any rank": (
        "hour_put_back_short_shared",
        "            if pinned[rank] or _weekday_there(state, ordinal) < 2:\n                continue\n            start = ordinal - ordinal % state.unit",
        "            if pinned[rank]:\n                continue\n            start = ordinal - ordinal % state.unit",
    ),
    "the half day's tail ranks leave their strata": (
        "hour_half_day_tails_stratum",
        "        for target in (before, after):\n            if low <= target <= high:\n                found += [(abs(target - place), target)]",
        "        for target in (before, after):\n            if True:\n                found += [(abs(target - place), target)]",
    ),
    "RELIEF never gives a unit back": (
        "hour_relief_given_back",
        "            if target is None:\n                for rank in relief:\n                    _weekday_step(state, rank, start)\n                have[middle] = have[middle] + size\n                have[into] = have[into] - size\n                continue",
        "            if target is None:\n                continue",
    ),
    "a free place may stand on a hole": (
        "hour_off_a_hole",
        "        low <= target <= high\n        and not _weekday_hole(state, target)\n        and not _weekday_holds(state, target)",
        "        low <= target <= high\n        and not _weekday_holds(state, target)",
    ),
    # STEP 3'S LATER ROUND (the lane's second skeptic, finding 2): a whole unit's
    # leaving gives its group room, which a unit asked earlier takes in the next round.
    "step 3 makes one round": (
        "hour_rounds",
        "_CLOCK_ROUNDS = 4",
        "_CLOCK_ROUNDS = 1",
    ),
    # A RANK WRITTEN AT A SIXTIETH SECOND (Codex's review of the landing, item 1):
    # counted in its written hour, not in its ordinal's.
    "a sixtieth second counted in its ordinal's hour": (
        "hour_sixtieth_second",
        "        if counted != written:\n            asked[counted] = asked[counted] + 1",
        "        if False:\n            asked[counted] = asked[counted] + 1",
    ),
    "a rank between two pins of one sixtieth second keeps its ordinal": (
        "hour_sixtieth_ties",
        "        if text != layout.texts[last] or text[17:19] != \"60\":\n            continue",
        "        if True:\n            continue",
    ),
    "two pins of any one value tie the ranks between": (
        "hour_sixtieth_ties",
        "        if text != layout.texts[last] or text[17:19] != \"60\":\n            continue",
        "        if text != layout.texts[last]:\n            continue",
    ),
    # THE ONE CLOCK PASS, field-generic (the 3b.4 skeptic's M4): its own
    # tier of the escape and of PUT BACK where the parent is shorter than a
    # day, frozen on a field of minutes whose parent is the hour.
    "the escape asks no parent of its own day": (
        "clock_minute_kin_escape",
        "    if kin:\n        for away in range(1, per_day):\n            for other in (seat - away, seat + away):\n                if other < 0 or other >= per_day or kin[other] != kin[seat]:\n                    continue\n                target = _clock_target_on(",
        "    if False:\n        for away in range(1, per_day):\n            for other in (seat - away, seat + away):\n                if other < 0 or other >= per_day or kin[other] != kin[seat]:\n                    continue\n                target = _clock_target_on(",
    ),
    "the escape leaves its kin group": (
        "clock_minute_kin_kept",
        "                if other < 0 or other >= per_day or kin[other] != kin[seat]:\n                    continue\n                target = _clock_target_on(",
        "                if other < 0 or other >= per_day:\n                    continue\n                target = _clock_target_on(",
    ),
    "PUT BACK asks no parent of its own day": (
        "clock_minute_put_back_kin",
        "    if kin:\n        for away in range(1, per_day):\n            for other in (seat - away, seat + away):\n                if other < 0 or other >= per_day or kin[other] != kin[seat]:\n                    continue\n                target = nearest_on(",
        "    if False:\n        for away in range(1, per_day):\n            for other in (seat - away, seat + away):\n                if other < 0 or other >= per_day or kin[other] != kin[seat]:\n                    continue\n                target = nearest_on(",
    ),
}

# ...and step 10's, edits of `calendar_clock`.
DISTANCE_MUTANTS = {
    "a tie goes outward": (
        "half_day_high",
        "        if distance - inward <= out - distance:\n            return inward",
        "        if distance - inward < out - distance:\n            return inward",
    ),
    "the nearest is always the outer": (
        "half_day_low",
        "        if inward < 1:\n            return out\n        if distance",
        "        if True:\n            return out\n        if distance",
    ),
    "the first pass is not made again": (
        "half_day_apart",
        "            if placed[index] <= placed[index + 1]:\n                placed[index] = further(placed[index + 1] + 1)",
        "            if False:\n                placed[index] = further(placed[index + 1] + 1)",
    ),
}

CASES = [
    "clock_minute_kin_escape", "clock_minute_kin_kept", "clock_minute_put_back_kin",
    "half_day_apart", "half_day_high", "half_day_low", "hour_escape_any_day", "hour_escape_weekday",
    "hour_half_day_tails", "hour_half_day_tails_stratum", "hour_off_a_hole", "hour_off_midnight",
    "hour_proportional", "hour_put_back", "hour_put_back_any_day", "hour_put_back_off_midnight",
    "hour_put_back_short", "hour_put_back_short_shared", "hour_relief", "hour_relief_given_back",
    "hour_rounds", "hour_same_day_clock", "hour_sixtieth_second", "hour_sixtieth_ties", "hour_split",
    "hour_whole_pass",
]


def test_every_case_is_asked_and_the_oracle_agrees() -> None:
    """The file holds these cases and no other, each frozen by a mutant here, and the
    oracle, run again, gives each the answer the file carries."""
    assert sorted(_FILE["cases"]) == sorted(CASES)
    named = {case for case, _before, _after in STEP_MUTANTS.values()}
    named = named | {case for case, _before, _after in DISTANCE_MUTANTS.values()}
    assert named == set(CASES)
    oracle = _oracle()
    assert sorted(oracle.HOUR_STEP_CASES) == sorted(_FILE["cases"])
    for name, case in _FILE["cases"].items():
        assert oracle.hour_step_answer(case) == case["answer"], name


@pytest.mark.parametrize("name", CASES)
def test_the_product_gives_every_case_its_answer(name: str) -> None:
    case = _case(name)
    assert _answer(case) == case["answer"], name


@pytest.mark.parametrize("mutant", sorted(STEP_MUTANTS))
def test_each_step_case_is_red_on_its_mutant(mutant: str, monkeypatch: pytest.MonkeyPatch) -> None:
    name, before, after = STEP_MUTANTS[mutant]
    case = _case(name)
    assert _answer(case, _mutant(monkeypatch, before, after)) != case["answer"], mutant


@pytest.mark.parametrize("mutant", sorted(DISTANCE_MUTANTS))
def test_each_distance_case_is_red_on_its_mutant(mutant: str) -> None:
    name, before, after = DISTANCE_MUTANTS[mutant]
    case = _case(name)
    assert _answer(case, _Distances(before, after)) != case["answer"], mutant


# -- the dial's half day (plan P4-D370's carve-out) -----------------------------------


def _twelve_hour_stamps(rows: int, seed: int, days: "list[datetime.date]") -> "list[str]":
    """`m/d/yyyy h:mm` on a 12-hour face with no marker, emergency-shaped hours."""
    draw = random.Random(seed)
    found: "list[str]" = []
    for _row in range(rows):
        moment = _at(draw.choice(days), draw.choices(range(24), weights=_ED)[0], draw.randrange(60))
        found += [f"{moment.month}/{moment.day}/{moment.year} {moment.hour % 12 or 12}:{moment.minute:02d}"]
    return found


def _twelve_hour_run(folder: pathlib.Path, cells: "list[str]", seeds: "tuple[int, ...]", generate=None) -> "list[list[str]]":
    """Describe a declared 12-hour stamp, then what each seed's twin misses."""
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(folder, "real.csv", "seen_at\n" + "\n".join(cells) + "\n")
    settings = taxonomy.Settings(small_cell_floor=LINE, forced_twelve_hour_clocks=("seen_at",))
    document = profile.build_document(reading.read_table(str(table), small_cell_floor=LINE), settings, [], [], [])
    loaded = contract.load_profile(str(fixtures.write_profile(folder, "real-profile.json", document)))
    described = kpi_shapes.Described(folder, table, document, loaded)
    found: "list[list[str]]" = []
    for seed in seeds:
        twin = rendering.twin_csv((generate or generation.generate)(loaded, seed))
        found += [kpi_shapes.missed(kpi_shapes.measure(described, twin, f"twin-{seed}.csv"))]
    return found


def test_a_declared_twelve_hour_stamp_writes_what_it_reads_back(tmp_path: pathlib.Path) -> None:
    """A year of stamps declared a 12-hour clock: census published, hours 12 to 23 nought, nothing missed."""
    cells = _twelve_hour_stamps(1000, 40001, _YEAR)
    block = _described_alone(tmp_path / "year", cells, LINE, twelve=True)
    assert _groups(block)[-1] == (12, 23, 0), _groups(block)
    assert _twelve_hour_run(tmp_path / "run", cells, (0, 1, 2)) == [[], [], []]


def test_a_twelve_hour_stamp_with_its_census_withheld_keeps_the_half_day(tmp_path: pathlib.Path) -> None:
    """Three days of stamps: the span withholds the census, and the half day's own census holds the body."""
    days = [datetime.date(2023, 3, 6) + datetime.timedelta(days=step) for step in range(3)]
    cells = _twelve_hour_stamps(1000, 40002, days)
    block = _described_alone(tmp_path / "span", cells, LINE, twelve=True)
    assert block["hour_census"] == []
    assert _twelve_hour_run(tmp_path / "run", cells, (0, 1)) == [[], []]


def test_red_without_the_half_day_tails(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Mutant: G7.3b step 10 withdrawn -- tail ranks past noon read twelve hours earlier."""
    cells = _twelve_hour_stamps(1000, 40001, _YEAR)
    mutant = _mutant(
        monkeypatch,
        "    if _on_the_half_day(facts) and half == 0:\n        # STEP 10 ON THE GROUP TOO",
        "    if False:\n        # STEP 10 ON THE GROUP TOO",
    )
    found = _twelve_hour_run(tmp_path, cells, (0, 1, 2), mutant.generate)
    assert any(any("tails." in check for check in missed) for missed in found), found


def test_red_without_the_half_days_own_census(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Mutant: no pass where the census is withheld -- afternoon draws read twelve hours earlier."""
    days = [datetime.date(2023, 3, 6) + datetime.timedelta(days=step) for step in range(3)]
    cells = _twelve_hour_stamps(1000, 40002, days)
    mutant = _mutant(
        monkeypatch,
        "        (not census and not half_day)\n        or parsed < 3",
        "        not census\n        or parsed < 3",
    )
    found = _twelve_hour_run(tmp_path, cells, (0, 1), mutant.generate)
    assert any(missed for missed in found), found


def test_v5_h1_reads_no_stamp_on_another_face(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """V5-H1's own reader counts no stamp written on another face (the lane's skeptic, finding 3 (c)).

    A year of stamps declared a 12-hour clock, and beside them three written on the 24-hour
    face, `23:59`, `13:05` and `17:30`: the census's recount reads every stamp the producer
    read and none of the three, which the producer counts unread (contract NF108). Every
    recount a validate run makes is handed cells `_cells_on_the_written_clock` has already
    cleared of such stamps, so no table turns this test of V5-H1's own red; its reader,
    asked alone, does. Mutant: V5-H1 reading a stamp on another face.
    """
    cells = _twelve_hour_stamps(1000, 40001, _YEAR)
    table = fixtures.write(tmp_path, "real.csv", "seen_at\n" + "\n".join(cells) + "\n")
    settings = taxonomy.Settings(small_cell_floor=LINE, forced_twelve_hour_clocks=("seen_at",))
    document = profile.build_document(reading.read_table(str(table), small_cell_floor=LINE), settings, [], [], [])
    loaded = contract.load_profile(str(fixtures.write_profile(tmp_path, "real-profile.json", document)))
    column = next(column for column in loaded.columns if column.name == "seen_at")
    facts = column.facts
    assert isinstance(facts, contract.DatetimeFacts) and facts.hour_census
    off = ["3/18/2023 23:59", "6/2/2023 13:05", "9/9/2023 17:30"]
    read = validation._hour_instants_of(facts, cells)
    assert len(read) == len(cells)
    assert validation._hour_instants_of(facts, cells + off) == read
    mutant = _validation_mutant(
        monkeypatch,
        "        if facts.parser_family in contract.CLOCK_FORM_MEMBERS and _stamp_off_its_face(cell, face):\n"
        "            continue\n        canonical = parsing.stamp_canonical(read[0], style)",
        "        canonical = parsing.stamp_canonical(read[0], style)",
    )
    assert len(mutant._hour_instants_of(facts, cells + off)) == len(read) + len(off)


def test_a_tie_group_gives_way_on_the_half_day_alone(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """G7.3b step 9 offers a 12-hour stamp's tie group no unit off the half day (finding 3 (h)).

    A year of stamps whose high tail ends in two visits booked on one slot, 11:58 the day
    before the last, so it runs a row past the floor and holds a tie group, which the twin
    stands at 11:59. With every unit beside the group held but the one past it at 12:00 and the
    count one short, step 9 takes the next free unit on the half day, 11:57; a unit at 12:00
    would be written on the dial at 00:00. Mutant: step 9 offering units off the half day.
    """
    cells = _twelve_hour_stamps(1000, 40001, _YEAR[:-3])
    last, before_last = _YEAR[-1], _YEAR[-2]
    for slot in range(10):
        moment = _at(last, 1 + slot, 5 * slot)
        cells += [f"{moment.month}/{moment.day}/{moment.year} {moment.hour % 12 or 12}:{moment.minute:02d}"]
    cells += [f"{before_last.month}/{before_last.day}/{before_last.year} 11:58"] * 2
    table = fixtures.write(tmp_path, "real.csv", "seen_at\n" + "\n".join(cells) + "\n")
    settings = taxonomy.Settings(small_cell_floor=LINE, forced_twelve_hour_clocks=("seen_at",))
    document = profile.build_document(reading.read_table(str(table), small_cell_floor=LINE), settings, [], [], [])
    loaded = contract.load_profile(str(fixtures.write_profile(tmp_path, "real-profile.json", document)))
    asked: "list[tuple[tuple[object, ...], dict[str, object]]]" = []
    gives_way = generation._group_gives_way

    def recorded(*arguments: object, **named: object) -> None:
        nonlocal asked
        asked += [(arguments, named)]
        gives_way(*arguments, **named)

    monkeypatch.setattr(generation, "_group_gives_way", recorded)
    generation.generate(loaded, 0)
    monkeypatch.undo()
    (arguments, named), = asked
    column, facts, layout, moved, day, step, unit, _wanted, widths, word = arguments[:10]
    plan = layout.high
    assert plan is not None and plan.shape is not None and plan.shape.grouped < plan.rows
    group = plan.shape.group
    near = 1
    while calendar_clock.morning(generation._tail_place(plan, group + near), unit):
        near = near + 1
    held = [generation._tail_place(plan, group - away) for away in range(1, near + 1)]
    held += [generation._tail_place(plan, group + away) for away in range(1, near)]
    stood = list(moved)
    for place in range(len(held)):
        stood[plan.rows + 5 + place] = held[place]
    found = {}
    for name, module in (
        ("product", generation),
        ("mutant", _mutant(
            monkeypatch,
            "                if shape.half_day is not None and not calendar_clock.morning(\n"
            "                    spot, shape.half_day[1]\n                ):\n                    continue",
            "                if False:\n                    continue",
        )),
    ):
        ranks = list(stood)
        count = len({value // unit for value in ranks})
        module._group_gives_way(column, facts, layout, ranks, day, step, unit, count + 1, widths, word, *arguments[10:], **named)
        found[name] = [ranks[rank] for rank in range(len(ranks)) if ranks[rank] != stood[rank]]
    assert len(found["product"]) == 1 and calendar_clock.morning(found["product"][0], unit), found
    assert len(found["mutant"]) == 1 and not calendar_clock.morning(found["mutant"][0], unit), found


def _twelve_hour_clinic(rows: int, seed: int) -> "list[str]":
    """A weekday clinic written `m/d/yyyy h:mm` on a 12-hour face with no marker, on the
    quarter hours: its morning slots read as written, its afternoon ones twelve hours earlier,
    and its noon slots read 12:00, midnight on the dial."""
    draw = random.Random(seed)
    found: "list[str]" = []
    for _row in range(rows):
        moment = _at(
            draw.choice(_WEEKDAYS), draw.choices(_CLINIC_HOURS, weights=_CLINIC)[0], draw.choice((0, 15, 30, 45))
        )
        found += [f"{moment.month}/{moment.day}/{moment.year} {moment.hour % 12 or 12}:{moment.minute:02d}"]
    return found


def test_a_twelve_hour_clinic_keeps_its_count_at_midnight(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The count at midnight of a 12-hour clinic is the body's to hold (the lane's skeptic, finding 2).

    Its noon slots read 12:00, midnight on the dial, and the description publishes them as
    its count at midnight. The move onto a midnight (G7.5) spread that count over the tail
    ranks too, G7.3g step 5 took a tail rank chosen there back onto the half day, and every
    twin at a floor of 11 wrote one cell fewer at midnight than published. Seeds 0 to 4,
    nothing missed. Mutant: the move onto a midnight choosing tail ranks again.
    """
    cells = _twelve_hour_clinic(2000, 40003)
    block = _described_alone(tmp_path / "clinic", cells, LINE, twelve=True)
    assert block["n_at_midnight"] is not None and block["n_at_midnight"] >= LINE, block["n_at_midnight"]
    assert _twelve_hour_run(tmp_path / "run", cells, (0, 1, 2, 3, 4)) == [[], [], [], [], []]
    mutant = _mutant(
        monkeypatch,
        "        elif first <= rank <= last:\n            free += [rank]",
        "        else:\n            free += [rank]",
    )
    found = _twelve_hour_run(tmp_path / "mutant", cells, (0, 1), mutant.generate)
    assert any("seen_at:midnight.count" in missed for missed in found), found


def _twelve_hour_lunch(rows: int, seed: int) -> "list[str]":
    """A weekday lunch clinic, 10:00 to 14:59, written `m/d/yyyy h:mm` on a 12-hour face with
    no marker, three slots in four on the hour or the half hour: its noon slots read 12:00,
    midnight on the dial, and are far more of its cells than its tails hold."""
    draw = random.Random(seed)
    found: "list[str]" = []
    for _row in range(rows):
        minute = draw.choice((0, 30)) if draw.random() < 0.75 else draw.choice((15, 45))
        day = draw.choice(_WEEKDAYS)
        hour = draw.choices((10, 11, 12, 13, 14), weights=(0.6, 1.2, 2.0, 1.4, 0.5))[0]
        found += [f"{day.month}/{day.day}/{day.year} {hour % 12 or 12}:{minute:02d}"]
    return found


_HALF_DAY_BODY = "        first, last = layout.low.rows, parsed - 1 - layout.high.rows\n"
# The move onto a midnight offers the body alone on the dial's half day: four edits of
# that rule (the lane's second skeptic, finding 3), of which the 2,000-row clinic above
# turns only the first red.
_HALF_DAY_BODY_MUTANTS = {
    "every tail offered": ("        elif first <= rank <= last:\n            free += [rank]", "        else:\n            free += [rank]"),
    "the high tail offered": (_HALF_DAY_BODY, "        first, last = layout.low.rows, parsed - 1\n"),
    "the low tail offered": (_HALF_DAY_BODY, "        first, last = 0, parsed - 1 - layout.high.rows\n"),
    "a rank more each side": (_HALF_DAY_BODY, "        first, last = layout.low.rows - 1, parsed - layout.high.rows\n"),
}


def test_a_twelve_hour_lunch_clinic_keeps_its_count_at_midnight(tmp_path: pathlib.Path) -> None:
    """The body alone holds a 12-hour stamp's count at midnight (the lane's second skeptic, finding 3).

    Three hundred visits of a weekday lunch clinic at a floor of 11: 35 cells at midnight
    published beside two tails of eleven rows each. Seeds 0 to 4, nothing missed. Each
    mutant of the rule (`test_a_twelve_hour_lunch_clinic_is_red_on_each_mutant`) misses
    `midnight.count` at every seed.
    """
    cells = _twelve_hour_lunch(300, 40043)
    block = _described_alone(tmp_path / "lunch", cells, LINE, twelve=True)
    assert block["n_at_midnight"] == 35 and block["low_tail"]["rows"] == block["high_tail"]["rows"] == LINE, block
    assert _twelve_hour_run(tmp_path / "run", cells, (0, 1, 2, 3, 4)) == [[], [], [], [], []]


@pytest.mark.parametrize("name", sorted(_HALF_DAY_BODY_MUTANTS))
def test_a_twelve_hour_lunch_clinic_is_red_on_each_mutant(
    name: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each edit of the half day's rule in the move onto a midnight misses the lunch clinic's
    count at midnight at seeds 0 and 1."""
    before, after = _HALF_DAY_BODY_MUTANTS[name]
    found = _twelve_hour_run(tmp_path, _twelve_hour_lunch(300, 40043), (0, 1), _mutant(monkeypatch, before, after).generate)
    assert all("seen_at:midnight.count" in missed for missed in found), (name, found)


def _two_marks(rows: int, seed: int) -> "list[str]":
    """Discharges, every one a different moment, four in five written with a `T` between day
    and clock and the rest with a space: one instant has two spellings, so the count of
    different values is one the construction does not reach."""
    draw = random.Random(seed)
    found: "list[str]" = []
    seen: "set[datetime.datetime]" = set()
    while len(found) < rows:
        moment = _at(draw.choice(_YEAR), draw.choices(range(24), weights=_DISCHARGE)[0], draw.randrange(60), draw.randrange(60))
        if moment in seen:
            continue
        seen = seen | {moment}
        found += [moment.strftime("%Y-%m-%dT%H:%M:%S") if draw.random() < 0.8 else moment.strftime(_ISO_S)]
    return found


def test_a_tie_the_pass_makes_is_split_where_the_count_is_out_of_reach(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """PUT BACK's short count, where the column's count is not reachable (the lane's skeptic, finding 4).

    Two thousand different discharges written with two marks: G7.3f's moves at the unit of an
    hour made one tie at seed 2 and nothing put it back, the count of different values falling
    from what the construction drew to 1,999. Now, at seeds 0 to 2, every twin holds as many
    different instants as the same seed with the pass withdrawn, nothing missed. Mutant: PUT
    BACK asked only where the count is reachable.
    """
    cells = _two_marks(2000, 40021)
    described = kpi_shapes.describe(tmp_path, "marks", "seen_at\n" + "\n".join(cells) + "\n", LINE)
    block = described.block("seen_at")
    assert block["hour_census"] and len(block["datetime_separators"]) == 2, block["datetime_separators"]
    column = next(column for column in described.loaded.columns if column.name == "seen_at")
    assert not contract.datetime_counts_reachable(column)

    def instants(written: str) -> int:
        return len({cell.replace("T", " ") for cell in _cells(written, "seen_at") if cell})

    monkeypatch.setattr(generation, "_hour_settled", lambda column, facts, ordinals, *rest, **named: (ordinals, []))
    flat = [instants(kpi_shapes.twin_text(described, seed)) for seed in (0, 1, 2)]
    monkeypatch.undo()
    for seed in (0, 1, 2):
        written = kpi_shapes.twin_text(described, seed)
        assert kpi_shapes.missed(kpi_shapes.measure(described, written, f"twin-{seed}.csv")) == [], seed
        assert instants(written) == flat[seed], seed
    mutant = _mutant(
        monkeypatch,
        "    if (state.keep_units and count != wanted) or short:",
        "    if state.keep_units and count != wanted:",
    )
    lost = instants(rendering.twin_csv(mutant.generate(described.loaded, 2)))
    assert lost < flat[2], (lost, flat[2])


_TWELVE_DAYS = [datetime.date(2023, 1, 2) + datetime.timedelta(days=step) for step in range(12)]


def _lab_minutes_two_marks(rows: int, seed: int) -> "list[str]":
    """Lab draws to the minute over twelve days, four in five written with a `T` between day
    and clock and the rest with a space: so dense that many draws share a minute, as in the
    real column, and one instant has two spellings, so the count of different values is one
    the construction does not reach."""
    draw = random.Random(seed)
    found: "list[str]" = []
    for _row in range(rows):
        moment = _at(draw.choice(_TWELVE_DAYS), draw.choices(range(24), weights=_LAB)[0], draw.randrange(60))
        found += [moment.strftime(_ISO_T if draw.random() < 0.8 else _ISO_M)]
    return found


def test_a_dense_column_drawn_past_its_count_keeps_the_ties_the_pass_makes(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """PUT BACK's short count is put back, where the column's count is out of reach, only
    where the count drawn is not above the published one (the lane's second skeptic, finding 1).

    Twenty thousand lab draws to the minute over twelve days, written with two marks: the
    construction draws more different minutes than the column publishes different values, and
    the ties the hour pass makes bring the twin near the published count, as the real column's
    own ties do. Putting the count drawn back split them, and every twin came back 18 to 19 per
    cent long. At floors 11 and 36, seeds 0 to 4, the twin's count of different values is
    within 1 per cent of the published one (on seven columns of this shape 70 twins came within
    -0.94 and +1.15 per cent). Mutant: the short count put back whatever the published count.
    """
    cells = _lab_minutes_two_marks(20000, 40033)
    text = "seen_at\n" + "\n".join(cells) + "\n"
    for floor in (LINE, 36):
        described = kpi_shapes.describe(tmp_path / f"floor-{floor}", "labs", text, floor)
        block = described.block("seen_at")
        column = next(column for column in described.loaded.columns if column.name == "seen_at")
        assert block["hour_census"] and not contract.datetime_counts_reachable(column)
        published = block["n_distinct"]
        for seed in (0, 1, 2, 3, 4):
            written = len({cell for cell in _cells(kpi_shapes.twin_text(described, seed), "seen_at") if cell})
            assert 100 * abs(written - published) <= published, (floor, seed, written, published)
    mutant = _mutant(
        monkeypatch,
        "    short = count < wanted and (published is None or wanted <= published)\n",
        "    short = count < wanted\n",
    )
    written = len({cell for cell in _cells(rendering.twin_csv(mutant.generate(described.loaded, 0)), "seen_at") if cell})
    assert 100 * (written - published) > published, (written, published)


# -- the rules, worked by hand ---------------------------------------------------------


def test_the_sure_cells_and_rule_4_by_hand() -> None:
    """Both boundaries and every rung in their written hours, ranks between two rungs of
    one value too, and rule 4's cells at midnight in place of the published ones at
    00:00:00. A sixtieth second stands in the hour it is written in, and a rank between it
    and the next day's midnight, the same instant written another way, is sure of neither
    (Codex's review of the landing, item 1)."""
    published = [
        (5, "2022-01-08 09:00:00"), (40, "2022-01-08 09:00:00"), (90, "2022-01-08 23:00:00"),
        (60, "2022-01-09 00:00:00"),
    ]
    sure = calendar_clock.hour_sure(published, None)
    assert sure[9] == 36 and sure[23] == 1 and sure[0] == 1
    assert calendar_clock.hour_sure(published, 30)[0] == 30
    leap = [(10, "2022-01-08 23:59:60"), (20, "2022-01-09 00:00:00")]
    assert calendar_clock.hour_sure(leap, None) == [1] + [0] * 22 + [1]
    assert calendar_clock.written_hour("2022-01-08 23:59:60") == 23
    assert calendar_clock.midnight_sure(51, [(51, ("1970-01-01 00:00:00",)), (11, None)]) == 0
    assert calendar_clock.midnight_sure(51, [(51, ("1970-01-01 00:00:00", "2023-01-02 08:00:00")), (11, None)]) == 51
    assert calendar_clock.midnight_sure(None, []) is None


def test_the_merge_never_runs_past_midnight() -> None:
    """Hour 23 and hour 0 are no neighbours: a short hour 23 joins hour 22."""
    bins = [40] + [0] * 21 + [30, 3]
    groups = calendar_clock.hour_groups(bins, [0] * 24, LINE)
    assert groups[-1] == (22, 23, 33) and groups[0] == (0, 0, 40)
    assert calendar_clock.hour_breach(groups, 73, LINE, [0] * 24) is None
    one = calendar_clock.hour_groups([0] * 6 + [500] + [0] * 17, [0] * 24, LINE)
    assert one == ((0, 5, 0), (6, 6, 500), (7, 23, 0))


def test_the_half_day_by_hand() -> None:
    """A place on the dial's half day, and the nearest either side of one that is not."""
    noon = 19000 * DAY + 43200
    assert not calendar_clock.morning(noon, 60) and calendar_clock.morning(noon - 60, 60)
    assert not calendar_clock.morning(19000 * DAY, 60) and calendar_clock.morning(19000 * DAY + 60, 60)
    assert calendar_clock.morning_at_or_before(noon + 600, 60) == noon - 60
    assert calendar_clock.morning_at_or_after(noon + 600, 60) == 19001 * DAY + 60

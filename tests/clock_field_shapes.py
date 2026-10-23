"""The shapes of the minute and second gate (stage 3b landing 3b.4, plan P4-D372).

Columns of moments whose minutes or seconds heap -- clinic slots on the
half and quarter hour, discharges typed on the half hour, vitals with a
five-minute digit preference, bursts of check-ins on one minute,
admissions with bare days at midnight, cells written `HH:MM:00`, cells
on the hour -- beside a flat control, a three-hour span, the design
skeptic's near-pure columns (M2), an epoch placeholder (m1), night
charting on the hour beside day entries at any minute (M3) and three
pure grids. Every table is built here, seeded and neutral (plan D13);
`tests/test_stage3b_minutes.py` and `tools/measurements/kpi_clock_census.py`
read the same shapes.
"""

from __future__ import annotations

import datetime
import random

ISO_S = "%Y-%m-%d %H:%M:%S"
ISO_M = "%Y-%m-%d %H:%M"
US = "%m/%d/%Y %H:%M"

_YEAR = [datetime.date(2023, 1, 1) + datetime.timedelta(days=step) for step in range(365)]
_TWO_YEARS = [datetime.date(2023, 1, 1) + datetime.timedelta(days=step) for step in range(731)]
_WEEKDAYS = [day for day in _TWO_YEARS if day.weekday() < 5]
_ED = (2.6, 2.2, 1.9, 1.6, 1.4, 1.4, 1.7, 2.5, 3.8, 5.0, 5.9, 6.2,
       6.1, 5.9, 5.8, 5.6, 5.5, 5.4, 5.3, 5.1, 4.8, 4.3, 3.7, 3.1)
_DISCHARGE = (0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.5, 1.5, 3.0, 12.0, 14.0,
              13.0, 11.0, 9.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.2, 0.6, 0.3)
_ADMITTED = (1.2, 1.0, 0.8, 0.7, 0.6, 0.6, 0.9, 3.0, 5.5, 5.0, 4.0, 3.2,
             3.0, 3.4, 3.8, 4.0, 4.2, 4.3, 4.0, 3.6, 3.0, 2.4, 1.9, 1.5)
_ROUNDS = tuple(9.0 if hour % 4 == 0 else (3.0 if hour % 4 == 1 else 1.0) for hour in range(24))
_PASSES = tuple(
    12.0 if hour in (8, 12, 17, 21) else (2.0 if 6 <= hour <= 22 else 0.4) for hour in range(24)
)
_CLINIC_HOURS = (8, 9, 10, 11, 12, 13, 14, 15, 16)


def _at(day: datetime.date, hour: int, minute: int, second: int = 0) -> datetime.datetime:
    return datetime.datetime(day.year, day.month, day.day, hour, minute, second)


def _hour(draw: random.Random, weights: "tuple[float, ...]") -> int:
    return draw.choices(range(24), weights=weights)[0]


def clinic(draw: random.Random, rows: int, days: int = 0) -> "list[str]":
    """Weekday slots 08:00 to 16:59: seven in ten on :00 or :30, a quarter
    on :15 or :45, the rest walk-ins at any minute; written to the minute;
    over the first `days` weekdays where that is not nought."""
    found: "list[str]" = []
    weekdays = _WEEKDAYS[:days] if days else _WEEKDAYS
    for _row in range(rows):
        pick = draw.random()
        minute = draw.choice((0, 30)) if pick < 0.70 else (draw.choice((15, 45)) if pick < 0.95 else draw.randrange(60))
        found += [_at(draw.choice(weekdays), draw.choice(_CLINIC_HOURS), minute).strftime(ISO_M)]
    return found


def discharges(draw: random.Random, rows: int, epoch_share: float = 0.0) -> "list[str]":
    """Late-morning discharges, 35 in 100 typed on :00 or :30, the rest at
    any minute; `epoch_share` of them written as the epoch placeholder."""
    found: "list[str]" = []
    for _row in range(rows):
        if draw.random() < epoch_share:
            found += ["1970-01-01 00:00"]
            continue
        minute = draw.choice((0, 30)) if draw.random() < 0.35 else draw.randrange(60)
        found += [_at(draw.choice(_YEAR), _hour(draw, _DISCHARGE), minute).strftime(ISO_M)]
    return found


def vitals(draw: random.Random, rows: int) -> "list[str]":
    """Rounds every four hours, three in four charted on a five-minute mark,
    to the second."""
    found: "list[str]" = []
    for _row in range(rows):
        minute = 5 * draw.randrange(12) if draw.random() < 0.76 else draw.randrange(60)
        found += [_at(draw.choice(_TWO_YEARS), _hour(draw, _ROUNDS), minute, draw.randrange(60)).strftime(ISO_S)]
    return found


def bursts(draw: random.Random, rows: int) -> "list[str]":
    """Check-ins in bursts of one to six on one minute, two in three of
    the bursts on :00 or :30; written to the minute, US style."""
    found: "list[str]" = []
    while len(found) < rows:
        minute = draw.choice((0, 30)) if draw.random() < 0.67 else draw.randrange(60)
        moment = _at(draw.choice(_TWO_YEARS), _hour(draw, _ED), minute)
        found += [moment.strftime(US)] * min(draw.randint(1, 6), rows - len(found))
    draw.shuffle(found)
    return found


def admissions(draw: random.Random, rows: int) -> "list[str]":
    """Three in ten written as a bare day at 00:00, the rest at any minute."""
    found: "list[str]" = []
    for _row in range(rows):
        day = draw.choice(_TWO_YEARS)
        if draw.random() < 0.30:
            found += [_at(day, 0, 0).strftime(ISO_M)]
            continue
        found += [_at(day, _hour(draw, _ADMITTED), draw.randrange(60)).strftime(ISO_M)]
    return found


def zero_seconds(draw: random.Random, rows: int, strays: int = 0) -> "list[str]":
    """Rounds written `HH:MM:00`, seven in ten on :00 or :30;
    `strays` of them carry a second other than 00."""
    found: "list[str]" = []
    for row in range(rows):
        minute = draw.choice((0, 30)) if draw.random() < 0.71 else draw.randrange(60)
        second = 1 + draw.randrange(59) if row < strays else 0
        found += [_at(draw.choice(_YEAR), _hour(draw, _PASSES), minute, second).strftime(ISO_S)]
    draw.shuffle(found)
    return found


def on_the_hour(draw: random.Random, rows: int, strays: int = 0) -> "list[str]":
    """Every cell on the hour, written to the minute; `strays` at another minute."""
    found: "list[str]" = []
    for row in range(rows):
        minute = 1 + draw.randrange(59) if row < strays else 0
        found += [_at(draw.choice(_TWO_YEARS), _hour(draw, _ED), minute).strftime(ISO_M)]
    draw.shuffle(found)
    return found


def emergency(draw: random.Random, rows: int) -> "list[str]":
    """The flat control: arrivals at any minute and second."""
    return [
        _at(draw.choice(_YEAR), _hour(draw, _ED), draw.randrange(60), draw.randrange(60)).strftime(ISO_S)
        for _row in range(rows)
    ]


def three_hours(draw: random.Random, rows: int) -> "list[str]":
    """A three-hour session of one day, slotted on the quarter hour and
    written to the second: its middle half spans fewer than four hours (MC4)."""
    day = datetime.date(2023, 5, 9)
    found: "list[str]" = []
    for _row in range(rows):
        minute = 15 * draw.randrange(4) if draw.random() < 0.8 else draw.randrange(60)
        found += [_at(day, 9 + draw.randrange(3), minute, draw.randrange(60)).strftime(ISO_S)]
    return found


def night_and_day(draw: random.Random, rows: int) -> "list[str]":
    """Night charting on the hour from 19:00 to 06:59, day entries at any
    minute: how the minutes fall changes with the hour (M3)."""
    found: "list[str]" = []
    for _row in range(rows):
        hour = draw.randrange(24)
        minute = 0 if (hour >= 19 or hour < 7) else draw.randrange(60)
        found += [_at(draw.choice(_YEAR), hour, minute).strftime(ISO_M)]
    return found


def days_and_a_few_times(draw: random.Random, rows: int, timed: int) -> "list[str]":
    """Days at midnight over four years, `timed` of them at 09:30: a day
    column a few timed cells made a column of moments (P4-D382's line)."""
    found: "list[str]" = []
    for row in range(rows):
        day = datetime.date(2021, 1, 1) + datetime.timedelta(days=draw.randrange(1460))
        found += [_at(day, 9, 30).strftime(ISO_M) if row < timed else _at(day, 0, 0).strftime(ISO_M)]
    draw.shuffle(found)
    return found


def grid(draw: random.Random, rows: int, step: int) -> "list[str]":
    """A pure grid: every cell on a multiple of `step` minutes."""
    return [
        _at(draw.choice(_WEEKDAYS), draw.choice(_CLINIC_HOURS), step * draw.randrange(60 // step)).strftime(ISO_M)
        for _row in range(rows)
    ]


def thousand(rows: int = 1000, seed: int = 72001) -> "dict[str, tuple[list[str], str]]":
    """The gate's table: every shape at `rows` rows."""
    draw = random.Random(seed)
    return {
        "clinic": (clinic(draw, rows), ISO_M),
        "discharges": (discharges(draw, rows), ISO_M),
        "vitals": (vitals(draw, rows), ISO_S),
        "bursts": (bursts(draw, rows), US),
        "admissions": (admissions(draw, rows), ISO_M),
        "zero_seconds": (zero_seconds(draw, rows), ISO_S),
        "on_the_hour": (on_the_hour(draw, rows), ISO_M),
        "emergency": (emergency(draw, rows), ISO_S),
        "three_hours": (three_hours(draw, rows), ISO_S),
        "near_pure_hour": (on_the_hour(draw, rows, 3), ISO_M),
        "near_pure_seconds": (zero_seconds(draw, rows, 3), ISO_S),
        "epoch_discharges": (discharges(draw, rows, 0.25), ISO_M),
        "night_and_day": (night_and_day(draw, rows), ISO_M),
        "quarter_grid": (grid(draw, rows, 15), ISO_M),
        "five_minute_grid": (grid(draw, rows, 5), ISO_M),
        "half_hour_grid": (grid(draw, rows, 30), ISO_M),
    }


# What each shape is expected to publish: both lists empty and why, or a field.
FLAT = ("emergency",)
SHORT_SPAN = ("three_hours",)
WITH_THE_HOUR = ("night_and_day",)
SECONDS_PUBLISHED = ("zero_seconds", "near_pure_seconds")


def two_shifts(draw: random.Random, rows: int) -> "list[str]":
    """Clinic hours 8 to 16 on weekdays: mornings seven in ten on :00 or :30,
    afternoons four in ten -- minutes depending on the hour, where one count
    over every hour is still closer to each than a flat field (the lane's
    skeptic, item 7)."""
    found: "list[str]" = []
    for _row in range(rows):
        hour = draw.choice(range(8, 17))
        share = 0.70 if hour < 12 else 0.40
        minute = draw.choice((0, 30)) if draw.random() < share else draw.randrange(60)
        found += [_at(draw.choice(_WEEKDAYS), hour, minute).strftime(ISO_M)]
    return found


def second_few(draw: random.Random, rows: int) -> "list[str]":
    """Seventy moments of the day hours on seconds 0 to 9, each written five
    times over: a second census of the rest standing on a few values (the
    lane's skeptic, item 6)."""
    moments: "list[str]" = []
    for _moment in range(70):
        moments += [
            _at(draw.choice(_YEAR), draw.choice(range(6, 22)), draw.randrange(60), draw.randrange(10)).strftime(ISO_S)
        ]
    found: "list[str]" = []
    while len(found) < rows:
        found += [draw.choice(moments)] * 5
    found = found[:rows]
    draw.shuffle(found)
    return found


def fuzzed(seed: int, number: int) -> "tuple[list[str], int, str]":
    """One random column of moments of the lane's first skeptic (its `fuzz.py`,
    `column`): random minute heaps, seconds pinned to 0 in a share, bare days
    at midnight, an epoch placeholder, sixtieth seconds and bursts, spans of
    a day to five years, 60 to 3,000 rows, written to the minute, the second
    or the millisecond; with the floor it is described under and its
    precision. The same `seed` and `number` draw the same column."""
    draw = random.Random(seed * 100000 + number)
    rows = draw.choice((60, 120, 300, 700, 1500, 3000))
    span = draw.choice((1, 3, 30, 365, 1826))
    start = datetime.datetime(2022, 1, 1)
    precision = draw.choice(("minute", "second", "second", "subsecond"))
    heaps: "list[tuple[int, float]]" = []
    for _heap in range(draw.randrange(0, 5)):
        heaps += [(draw.randrange(60), draw.random())]
    heap_share = draw.choice((0.0, 0.3, 0.7, 0.95, 1.0)) if heaps else 0.0
    second_zero = draw.choice((0.0, 0.5, 0.9, 1.0))
    midnight = draw.choice((0.0, 0.0, 0.05, 0.3))
    epoch = draw.choice((0.0, 0.0, 0.1))
    leap = draw.choice((0.0, 0.0, 0.02))
    burst = draw.choice((1, 1, 3, 6))
    hours = [draw.random() ** 2 for _hour in range(24)]
    found: "list[str]" = []
    while len(found) < rows:
        if draw.random() < epoch:
            moment = datetime.datetime(1970, 1, 1)
        else:
            day = start + datetime.timedelta(days=draw.randrange(span))
            if draw.random() < midnight:
                moment = day
            else:
                hour = draw.choices(range(24), weights=hours)[0]
                if heaps and draw.random() < heap_share:
                    minute = draw.choices([value for value, _weight in heaps], weights=[weight for _value, weight in heaps])[0]
                else:
                    minute = draw.randrange(60)
                second = 0 if draw.random() < second_zero else draw.randrange(60)
                moment = day.replace(hour=hour, minute=minute, second=second, microsecond=1000 * draw.randrange(1000))
        if precision == "minute":
            text = moment.strftime("%Y-%m-%d %H:%M")
        elif precision == "second":
            text = moment.strftime("%Y-%m-%d %H:%M:%S")
            if draw.random() < leap and text[-2:] == "59":
                text = text[:-2] + "60"
        else:
            text = moment.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        found += [text] * min(draw.randint(1, burst), rows - len(found))
    draw.shuffle(found)
    floor = draw.choice((1, 5, 11, 11, 20, 36, 50))
    return found, floor, precision


def table_text(columns: "dict[str, tuple[list[str], str]]") -> str:
    """The columns as one comma-separated table."""
    names = list(columns)
    rows = len(columns[names[0]][0])
    lines = [",".join(names)]
    for row in range(rows):
        lines += [",".join(columns[name][0][row] for name in names)]
    return "\n".join(lines) + "\n"


def cells_of(text: str, name: str) -> "list[str]":
    """One column's cells out of a table's text."""
    lines = text.splitlines()
    place = lines[0].split(",").index(name)
    return [line.split(",")[place] for line in lines[1:] if line]

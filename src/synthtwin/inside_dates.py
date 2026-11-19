"""The dates zone of the inside record and the writer of a twin's dates (lane IN-5).

THE OWNER'S RULING (2026-11-18): a twin's dates keep the real weekday and
the real time of day, and their day of the month is made up, built so that
analyses by weekday, hour, season, month and year, the time between two
dates, the time to an event and the gaps between a patient's visits behave
as on the real table. Safe Harbor binds the twin: no twin date is any real
person's date; a made-up day that lands on a real calendar day by chance is
the class the owner accepted.

WHAT THE ZONE HOLDS (`build_zone`; the record's `zones["dates"]`). A model,
never data: no row, no person's dates, no list of real days. For each date
column:

* its reading (a member of the product's date vocabulary,
  `parsing.DATE_FORMATS`, or a counting system of `date_counts.MEMBERS`
  the person declared) and its spellings (the written forms, as shares);
* its CALENDAR: for each year, the shares of the 84 cells of month by
  weekday. Years, months, seasons and the weekday within each month are
  carried; the day of the month is not;
* its CLOCK where it writes one: hour by weekday, minute by hour and the
  second, as shares; by the levels of one label column (two to ten levels)
  where that column moves the clock (hand-typed rows on five-minute marks,
  device rows at any minute);
* its CHAIN where an earlier date column of the same row stands nearest
  to it (the smallest spread of the difference): the gap to that column as
  a quantile function of `GAP_GRID` points, by the levels of one label
  column where the gap is minutes or hours (a lag by route, a duration by
  service), by the reference's weekday where it is days (a stay ending on
  a weekday the real stays end on), and the joint presence of the two;
* with a person column and several rows a person, the TIMELINE: the
  census of each person's first date and the gaps between a person's
  consecutive dates.

Every table of shares is written per million (`PER`), so the zone's size
follows its columns, levels, years and grid points, never its rows.

WHAT THE WRITER KEEPS (`write_dates`, the hook the generate step calls).
A date with no reference (a person's first date, a column standing alone)
takes its year and month from the calendar, its weekday from that month's
weekday shares and its day of the month MADE UP: each day of the month
weighs its weekday's share divided by the number of such weekdays in the
month, so the weekday shares come back exactly and the day falls on any of
the month's days of that weekday. The time of day comes from the clock.
A chained date is its reference plus a gap drawn from the chain's quantile
function (days for a day-scale chain, the date's own clock then drawn from
its census; seconds for a minute-scale one, minutes heaped on five-minute
marks where the census heaps them). Where every real gap is at least
nought, so is every twin gap: no later column precedes its reference and
a person's dates come in order. A person whose last date would pass the
real calendar's last month is moved earlier by whole weeks, which keeps
every weekday and every gap.

WHAT IT DOES NOT KEEP (stated): the day of the month (paydays, the first
of the month, a holiday's own day); a gap's relation to columns other than
its one label column (the generate step's, through `ranks`); the serial
pace of one person's gaps (the trajectories', through `ranks`); a date
column the product reads at a month or a quarter (no day to make up: the
marginals zone carries it).

THE HOOK. `write_dates(zone, rows, people=..., given=..., ranks=...,
present=..., seed=...)` returns each date column's twin cells. `people`
names each twin row's person; `given` holds the twin's cells of the label
columns the zone conditions on; `ranks` holds, for a column, one number in
(0, 1) a row that the generate step chose to tie the date to its other
columns (the position of the calendar for a first date, of the gap for a
chained one); `present` the rows that hold a date. Each is optional.

INSTANTS, TO THE NANOSECOND. A moment is fitted, ordered and drawn as an
instant: a stamp written with an offset (`09:00+02:00`) is read as the
instant it names (`07:00Z`), so the gaps, the chains and the orderings are
the real intervals whatever offsets the cells wear, and each twin cell is
written back in its own spelling's offset (the instant moved by it). The
time of day is counted in nanoseconds (`TICKS` a second), so a fraction of a
second is carried through the gaps and written from the moment itself (a
tenth of a second between two stamps stays a tenth); a first date of a
column that writes fractions draws its own. `moment_of`, the public reader,
gives the instant to the whole second.

No randomness is imported: the draws are SplitMix64 streams of the seed
and the column's name (as lane IN-1's checks draw), so the same zone and
seed write the same bytes. Nothing here prints, logs or raises a value of
the zone.
"""

import dataclasses
import math
import typing

from synthtwin import date_counts, parsing

ZONE = "dates"
# Version 2: moments are instants in nanoseconds (version 1 held wall clocks in whole seconds; a writer reading one
# would draw gaps a billion times too short, so it refuses it and the twin keeps the description's dates).
VERSION = 2
GAP_GRID = 1001
CELL_GRID = 201
PER = 1_000_000
SPELLING_CAP = 64
CONTACT_CAP = 1000
YEAR_CAP = 1000
PARENT_LEVELS = 10
PARENT_LEAST_ROWS = 30
PARENT_MOVE = 0.02
CHAIN_LEAST_SHARE = 0.5
SAMPLE = 4000
READ_PERCENT = 95
DAY = 86400
# A moment's time of day in nanoseconds, as `date_counts` settles a count: `TICKS` a second, `DAY_TICKS` a day.
TICKS = date_counts.SECOND // date_counts.NANOSECOND
DAY_TICKS = DAY * TICKS
WEEK = 7
HEAP_LINE = 0.3
REDRAWS = 8
MIXED_TRIES = 200
MIXED_LEAST = 3
MIXED_SHARE = 0.005
MIXED_SET_ASIDE = ("compact-date", "two-digit-month-first-date", "two-digit-day-first-date",
                   "dotted-two-digit-month-first-date", "dotted-two-digit-day-first-date")
CELL_SHARE = 0.01
TIGHTER = 0.9
BANDS = (2, 3, 4, 5, 7, 10, 20, 50)
FIRST_BANDS = (1, 2, 3, 4, 5, 7, 10, 20, 50)
FIRST_LEAST_PEOPLE = 100
BAND_GRID = 101

# The members of the product's date vocabulary the zone reads, in the
# product's own order (a cell two members read is read by the first).
TEXT_MEMBERS = (
    "iso-datetime",
    "iso-date",
    "slashed-iso-datetime",
    "slashed-iso-date",
    "compact-date",
    "month-first-datetime",
    "day-first-datetime",
    "month-first-date",
    "day-first-date",
    "textual-day-first-date",
    "textual-month-first-date",
    "dotted-month-first-date",
    "dotted-day-first-date",
    "two-digit-month-first-date",
    "two-digit-day-first-date",
    "dotted-two-digit-month-first-date",
    "dotted-two-digit-day-first-date",
    "iso-mixed",
)
CLOCK_MEMBERS = ("iso-datetime", "slashed-iso-datetime", "month-first-datetime", "day-first-datetime", "iso-mixed")
_ISO_MEMBERS = ("iso-date", "iso-datetime", "iso-mixed")
_ABSENT = -(1 << 62)
_MASK = (1 << 64) - 1
_GOLDEN = 0x9E3779B97F4A7C15
_DIGITS = "0123456789"
_PI = 3.141592653589793


class DatesError(ValueError):
    """A refusal of the dates zone, in plain words naming columns and reasons, never a value."""


# -- words, read under the offline audit's exact type checks --------------------------------------


def _text(cell: object) -> str:
    if not isinstance(cell, str):
        raise TypeError("synthtwin reads a table's cells and names as text only.")
    return cell


def _bare(cell: object) -> str:
    if not isinstance(cell, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    return cell.strip()


def _figures(text: object) -> bool:
    if not isinstance(text, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    if not text:
        return False
    for character in text:
        if character not in _DIGITS:
            return False
    return True


def _starts(text: object, head: object) -> bool:
    if not isinstance(text, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    if not isinstance(head, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    return text[: len(head)] == head


# -- the draws: SplitMix64, no random source imported ---------------------------------------------


def _mixed(value: int) -> int:
    z = (value + _GOLDEN) & _MASK
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK
    return z ^ (z >> 31)


def _stream(seed: int, name: object, purpose: object) -> "list[int]":
    """A stream's state: the seed, the column's name and the draw's purpose, mixed character by character."""
    state = _mixed(seed & _MASK)
    for character in _text(name):
        state = _mixed(state ^ ord(character))
    state = _mixed(state ^ 0x5F)
    for character in _text(purpose):
        state = _mixed(state ^ ord(character))
    return [state]


def _uniform(state: "list[int]") -> float:
    """The stream's next number in (0, 1)."""
    state[0] = (state[0] + _GOLDEN) & _MASK
    z = state[0]
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK
    z = z ^ (z >> 31)
    return ((z >> 11) + 0.5) / 9007199254740992.0


# -- the calendar ----------------------------------------------------------------------------------


def weekday(day: int) -> int:
    """Monday 0 to Sunday 6 of a day counted from 1 January 1970 (a Thursday)."""
    return (day + 3) % WEEK


def _days_in(year: int, month: int) -> int:
    if month == 2:
        leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
        return 29 if leap else 28
    return 30 if month in (4, 6, 9, 11) else 31


def _civil(day: int, cache: "dict[int, tuple[int, int, int]]") -> "tuple[int, int, int]":
    if day in cache:
        return cache[day]
    found = parsing.civil_from_days(day)
    cache[day] = found
    return found


# -- reading a column ---------------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Reading:
    """How a column writes its dates: `kind` is "text" (a member of the date vocabulary) or "count"."""

    kind: str
    member: str


def _iso_fast(cell: object) -> "tuple[int, int, int] | None":
    """A cell written YYYY-MM-DD, with HH:MM[:SS[.f]] after a space or a T and Z or an offset: its day, its time of day in
    ticks as written (-1 where it writes no clock) and the offset it writes, in seconds east of UTC (0 where none)."""
    text = _text(cell)
    if len(text) < 10 or text[4] != "-" or text[7] != "-":
        return None
    if not _figures(text[0:4] + text[5:7] + text[8:10]):
        return None
    year, month, date = int(text[0:4]), int(text[5:7]), int(text[8:10])
    if not parsing.valid_date(year, month, date):
        return None
    day = parsing.days_from_civil(year, month, date)
    rest = text[10:]
    if not rest:
        return day, -1, 0
    if rest[0] != " " and rest[0] != "T":
        return None
    clock = rest[1:]
    if len(clock) < 5 or clock[2] != ":" or not _figures(clock[0:2] + clock[3:5]):
        return None
    hour, minute, second, fraction = int(clock[0:2]), int(clock[3:5]), 0, 0
    tail = clock[5:]
    if len(tail) >= 3 and tail[0] == ":" and _figures(tail[1:3]):
        second = int(tail[1:3])
        tail = tail[3:]
        if len(tail) >= 2 and tail[0] == "." and _figures(tail[1:2]):
            index = 1
            while index < len(tail) and tail[index] in _DIGITS:
                index += 1
            fraction = _ticks_of(tail[1:index])
            tail = tail[index:]
    if tail and not _offset_text(tail):
        return None
    if hour > 23 or minute > 59 or second > 59:
        return None
    return day, (hour * 3600 + minute * 60 + second) * TICKS + fraction, _offset_seconds(tail) if tail else 0


def _ticks_of(figures: object) -> int:
    """The ticks the figures after a second's point name (`250` is a quarter of a second); past nine figures, none."""
    written = _text(figures)
    value = 0
    for index in range(9):
        value = value * 10 + (ord(written[index]) - ord("0") if index < len(written) else 0)
    return value


def _offset_seconds(offset: object) -> int:
    """An offset's seconds east of UTC: `Z` nought, `+02:00`, `+0200` and `+02` two hours, `-05:30` five and a half
    hours west; nought for any other text, and for an offset past the fourteen hours no zone reaches."""
    tail = _text(offset)
    if not _offset_text(tail) or tail == "Z" or tail == "z":
        return 0
    body = tail[1:]
    hours = int(body[0:2])
    minutes = int(body[3:5]) if len(body) == 5 else (int(body[2:4]) if len(body) == 4 else 0)
    if hours > 14 or minutes > 59:
        return 0
    seconds = hours * 3600 + minutes * 60
    return -seconds if tail[0] == "-" else seconds


def _fraction_ticks(text: object, offset: object) -> int:
    """The ticks of the fraction of a second a stamp writes after its seconds (`:SS.fff`, before its offset), else 0."""
    body = _text(text)
    if "." not in body:
        return 0
    written = _text(offset)
    if written and body[len(body) - len(written):] == written:
        body = body[: len(body) - len(written)]
    point = -1
    for index in range(len(body)):
        if body[index] == ".":
            point = index
    if point < 3 or body[point - 3] != ":" or not _figures(body[point - 2: point]):
        return 0
    if not _figures(body[point + 1:]):
        return 0
    return _ticks_of(body[point + 1:])


def _offset_text(text: object) -> bool:
    """Z, or a sign and HH, HHMM or HH:MM."""
    tail = _text(text)
    if tail == "Z" or tail == "z":
        return True
    if not tail or (tail[0] != "+" and tail[0] != "-"):
        return False
    body = tail[1:]
    if len(body) == 5 and body[2] == ":":
        return _figures(body[0:2] + body[3:5])
    return (len(body) == 2 or len(body) == 4) and _figures(body)


def _from_canonical(canonical: object) -> "tuple[int, int] | None":
    text = _text(canonical)
    if len(text) < 10 or text[4] != "-" or text[7] != "-" or not _figures(text[0:4] + text[5:7] + text[8:10]):
        return None
    day = parsing.days_from_civil(int(text[0:4]), int(text[5:7]), int(text[8:10]))
    if len(text) == 10:
        return day, -1
    if len(text) >= 19 and _figures(text[11:13] + text[14:16] + text[17:19]):
        return day, int(text[11:13]) * 3600 + int(text[14:16]) * 60 + int(text[17:19])
    return None


def _wall_of(cell: object, reading: Reading) -> "tuple[int, int, int] | None":
    """A cell's day as written, its time of day in ticks as written (-1 where it writes no clock) and the offset it
    writes in seconds east of UTC (0 where none), or None."""
    text = _bare(cell)
    if not text:
        return None
    if reading.kind == "count":
        counted = _counted_moment(text, reading.member)
        return None if counted is None else (counted[0], counted[1], 0)
    if reading.member in _ISO_MEMBERS:
        fast = _iso_fast(text)
        if fast is not None:
            if reading.member == "iso-date" and fast[1] >= 0:
                return None
            if reading.member == "iso-datetime" and fast[1] < 0:
                return None
            return fast
    found = parsing.parse_datetime(text, reading.member)
    if found is None:
        return None
    canonical = _from_canonical(found[0])
    if canonical is None:
        return None
    if canonical[1] < 0:
        return canonical[0], -1, 0
    return canonical[0], canonical[1] * TICKS + _fraction_ticks(text, found[1]), _offset_seconds(found[1])


def _moment(cell: object, reading: Reading) -> "tuple[int, int] | None":
    """A cell's instant: its day (from 1 January 1970) and time of day in ticks, its offset taken off (-1: no clock)."""
    wall = _wall_of(cell, reading)
    if wall is None:
        return None
    day, tick, offset = wall
    if tick < 0 or offset == 0:
        return day, tick
    instant = day * DAY_TICKS + tick - offset * TICKS
    return instant // DAY_TICKS, instant % DAY_TICKS


def moment_of(cell: object, reading: Reading) -> "tuple[int, int] | None":
    """A cell's instant: its day (from 1 January 1970) and second of the day (-1 where it writes no clock), or None.

    A stamp written with an offset is read as the instant it names (`09:00+02:00` is `07:00` of the same day); the
    fraction of a second is cut off here (the zone itself carries it, `_moment`).
    """
    found = _moment(cell, reading)
    if found is None:
        return None
    return found[0], (found[1] // TICKS if found[1] >= 0 else -1)


def _counted_moment(text: str, member: str) -> "tuple[int, int] | None":
    """A counted cell's day and time of day in ticks (-1 where its member counts whole days), settled to the nanosecond."""
    written = date_counts.counted(member, text)
    if written is None:
        return None
    numerator, denominator = date_counts.exact_value(written)
    moment = date_counts.moment_of(member, numerator, denominator, date_counts.NANOSECOND)
    if moment is None:
        return None
    day = moment // DAY_TICKS
    found = date_counts.TABLE[member]
    clock = found.unit < date_counts.DAY or (bool(written.fraction) and not found.contacts)
    return day, (moment - day * DAY_TICKS) if clock else -1


def _spread_sample(cells: "list[str]", most: int) -> "list[str]":
    """Up to `most` present cells, spread over the column."""
    present = [cell for cell in cells if _bare(cell)]
    if len(present) <= most:
        return present
    step = len(present) / most
    return [present[int(k * step)] for k in range(most)]


def reading_of(cells: "list[str]", declared: str = "") -> "Reading | None":
    """The column's reading: the declared one (a member or a counting system), else the first member reading 95 per cent."""
    if declared:
        if declared in date_counts.MEMBERS:
            return Reading("count", declared)
        if declared in TEXT_MEMBERS:
            return Reading("text", declared)
        raise DatesError("A date column's declared reading names no member of synthtwin's date vocabulary.")
    sample = _spread_sample(cells, SAMPLE)
    if not sample:
        return None
    for member in TEXT_MEMBERS:
        reading = Reading("text", member)
        missed = 0
        room = len(sample) - (len(sample) * READ_PERCENT + 99) // 100
        for cell in sample:
            if moment_of(cell, reading) is None:
                missed += 1
                if missed > room:
                    break
        if missed <= room:
            return reading
    return None


# -- spellings ------------------------------------------------------------------------------------------


def _clock_parts(text: object, offset: object) -> "tuple[str, str, int, str] | None":
    """The text after a date's half: its mark, its clock form, the figures of its fraction and its offset."""
    rest = _text(text)
    written_offset = _text(offset)
    mark = ""
    while rest and (rest[0] == " " or rest[0] == "T" or rest[0] == "t") and len(mark) < 2:
        mark = mark + rest[0]
        rest = rest[1:]
    if written_offset and rest[len(rest) - len(written_offset):] == written_offset:
        rest = rest[: len(rest) - len(written_offset)]
    figures = 0
    point = -1
    for index in range(len(rest)):
        if rest[index] == ".":
            point = index
    if point >= 0 and _figures(rest[point + 1:]):
        figures = len(rest) - point - 1
        rest = rest[:point]
    form = parsing.clock_form(rest)
    if form is None:
        return None
    return mark, form, figures, written_offset


def _offset_of(cell: object, member: str) -> str:
    text = _text(cell)
    found = parsing.parse_datetime(text, member)
    if found is None:
        return ""
    return _text(found[1])


def spelling_of(cell: object, reading: Reading) -> "list[object] | None":
    """How a text cell is written: [width, month name style, mark, clock form, fraction figures, offset]."""
    text = _bare(cell)
    found = _wall_of(text, reading)
    if found is None:
        return None
    # The day and clock AS WRITTEN (an offset's instant may fall on another day): the spelling is read off them.
    day, second, _offset = found
    year, month, date = parsing.civil_from_days(day)
    width = parsing.date_field_style(text, reading.member)
    style = parsing.month_name_style(text, reading.member)
    width_text = width if width is not None else parsing.DEFAULT_FIELD_WIDTH
    style_text = style if style is not None else parsing.DEFAULT_NAME_STYLE
    half = parsing.written_date(year, month, date, reading.member, width_text, style_text)
    if not _starts(text, half):
        return None
    rest = text[len(half):]
    # A width no field of this cell shows (every field of two figures) is kept as '' and written, in the twin, as
    # the width the column's other cells show (`_widths`).
    shown = width if width is not None else ""
    if second < 0:
        return [shown, style_text, "", "", 0, ""] if not rest else None
    parts = _clock_parts(rest, _offset_of(text, reading.member))
    if parts is None:
        return None
    mark, form, figures, offset = parts
    return [shown, style_text, mark, form, figures, offset]


def _count_spelling(sample: "list[str]", member: str) -> "dict[str, object]":
    """A counted column's form: the places, trimming, significance and mark its counts are written with."""
    written: "list[date_counts.Written]" = []
    contacts: "dict[str, int]" = {}
    for cell in sample:
        found = date_counts.counted(member, _bare(cell))
        if found is not None:
            written += [found]
            if date_counts.TABLE[member].contacts:
                word = date_counts.contact_word(found)
                contacts[word] = (contacts[word] if word in contacts else 0) + 1
    form = date_counts.form_of(written, date_counts.POINT, contacts if date_counts.TABLE[member].contacts else None)
    entry: "dict[str, object]" = {"places": form.places, "trimmed": form.trimmed, "significant": form.significant,
                                  "exponent": form.exponent, "mark": form.mark}
    if date_counts.TABLE[member].contacts:
        entry["contacts"] = _shares_of(_capped(contacts, CONTACT_CAP))
    return entry


def _capped(counts: "dict[str, int]", most: int) -> "dict[str, int]":
    ranked = sorted((-counts[key], key) for key in counts)
    kept: "dict[str, int]" = {}
    for negative, key in ranked[:most]:
        kept[key] = -negative
    return kept


# -- shares -----------------------------------------------------------------------------------------------


def _per_million(counts: "list[int]") -> "list[int]":
    """Counts as shares per million that sum to exactly `PER` (largest remainders), all nought where the counts are."""
    total = sum(counts)
    if total <= 0:
        return [0 for _ in counts]
    floors = [count * PER // total for count in counts]
    left = PER - sum(floors)
    ranked = sorted((-(count * PER - floors[k] * total), k) for k, count in enumerate(counts))
    for _remainder, k in ranked[:left]:
        floors[k] += 1
    return floors


def _shares_of(counts: "dict[str, int]") -> "list[list[object]]":
    keys = sorted(counts)
    shares = _per_million([counts[key] for key in keys])
    return [[key, share] for key, share in zip(keys, shares)]


def _calendar(days: "list[int]", cache: "dict[int, tuple[int, int, int]]") -> "dict[str, object]":
    """The calendar of a list of days: each year's 84 shares of month by weekday, per million over all of them."""
    by_year: "dict[int, list[int]]" = {}
    for day in days:
        year, month, _date = _civil(day, cache)
        if year not in by_year:
            by_year[year] = [0] * 84
        by_year[year][(month - 1) * WEEK + weekday(day)] += 1
    years = sorted(by_year)
    if len(years) > YEAR_CAP:
        middle = years[len(years) // 2]
        kept = [year for year in years if abs(year - middle) <= YEAR_CAP // 2][:YEAR_CAP]
        years = kept
    flat: "list[int]" = []
    for year in years:
        flat += by_year[year]
    shares = _per_million(flat)
    return {"years": years, "cells": [shares[84 * k: 84 * (k + 1)] for k in range(len(years))]}


def _clock(days: "list[int]", ticks: "list[int]") -> "dict[str, object]":
    """Hour by weekday, minute by hour and the second, as shares, and the share of minutes on five-minute marks."""
    hours = [0] * (WEEK * 24)
    minutes = [0] * (24 * 60)
    at_second = [0] * 60
    marks = 0
    for day, tick in zip(days, ticks):
        if tick < 0:
            continue
        second = tick // TICKS
        hour = second // 3600
        minute = (second // 60) % 60
        hours[weekday(day) * 24 + hour] += 1
        minutes[hour * 60 + minute] += 1
        at_second[second % 60] += 1
        marks += 1 if minute % 5 == 0 else 0
    clocked = sum(at_second)
    hour_shares = _per_million(hours)
    minute_shares = _per_million(minutes)
    return {"hour": [hour_shares[24 * k: 24 * (k + 1)] for k in range(WEEK)],
            "minute": [minute_shares[60 * k: 60 * (k + 1)] for k in range(24)],
            "second": _per_million(at_second), "marks": (marks * PER // clocked) if clocked else 0,
            "clocked": clocked}


# -- quantile functions -------------------------------------------------------------------------------


def _grid(values: "list[int]", points: int) -> "list[int]":
    """The quantile function on `points` points, each an observed value (the lower order statistic)."""
    ordered = sorted(values)
    last = len(ordered) - 1
    return [ordered[(k * last) // (points - 1)] for k in range(points)]


def _below(ordered: "list[int]", value: int) -> int:
    """How many of the ordered values are at most `value` (a binary search; no library is needed)."""
    low, high = 0, len(ordered)
    while low < high:
        middle = (low + high) // 2
        if ordered[middle] <= value:
            low = middle + 1
        else:
            high = middle
    return low


def _moved_by(values: "list[int]", levels: "list[str]") -> float:
    """The weighted Kolmogorov distance between each level's values and all of them (levels under the least rows aside)."""
    ordered = sorted(values)
    if len(ordered) < 2 * PARENT_LEAST_ROWS:
        return 0.0
    probes = _grid(ordered, 101)
    by_level: "dict[str, list[int]]" = {}
    for value, level in zip(values, levels):
        if level not in by_level:
            by_level[level] = []
        by_level[level] += [value]
    if len(by_level) < 2:
        return 0.0
    moved = 0.0
    noise = 0.0
    for level in by_level:
        mine = sorted(by_level[level])
        if len(mine) < PARENT_LEAST_ROWS:
            continue
        distance = 0.0
        for probe in probes:
            distance = max(distance, abs(_below(mine, probe) / len(mine) - _below(ordered, probe) / len(ordered)))
        weight = len(mine) / len(ordered)
        moved += distance * weight
        # The Kolmogorov distance a level of this many rows shows by chance alone (its mean, 0.87 over the root).
        noise += weight * 0.87 * math.sqrt(max(0.0, 1.0 - weight) / len(mine))
    return moved - 2.0 * noise


def _parent_of(values: "list[int]", rows: "list[int]", labels: "dict[str, list[str]]") -> str:
    """The label column (two to ten levels) that moves the values most, '' where none moves them by `PARENT_MOVE`."""
    best, chosen = PARENT_MOVE, ""
    for name in sorted(labels):
        cells = labels[name]
        moved = _moved_by(values, [_bare(cells[row]) for row in rows])
        if moved > best:
            best, chosen = moved, name
    return chosen


def _clock_key(tick: int) -> int:
    """The hour and whether the minute stands on a five-minute mark, as one number of 48."""
    second = tick // TICKS
    return (second // 3600) * 2 + (1 if (second // 60) % 5 == 0 else 0)


def _moved_cells(keys: "list[int]", levels: "list[str]", cells: int) -> float:
    """The weighted distance in total variation between each level's census of keys and all of them."""
    whole = [0] * cells
    by_level: "dict[str, list[int]]" = {}
    for key, level in zip(keys, levels):
        whole[key] += 1
        if level not in by_level:
            by_level[level] = [0] * cells
        by_level[level][key] += 1
    total = len(keys)
    if total < 2 * PARENT_LEAST_ROWS or len(by_level) < 2:
        return 0.0
    moved = 0.0
    noise = 0.0
    for level in by_level:
        mine = by_level[level]
        rows = sum(mine)
        if rows < PARENT_LEAST_ROWS:
            continue
        distance = 0.0
        chance = 0.0
        for k in range(cells):
            distance += abs(mine[k] / rows - whole[k] / total)
            share = whole[k] / total
            # The mean absolute departure of a share drawn by chance alone: the root of 2 p (1 - p) over pi n.
            chance += math.sqrt(2.0 * share * (1.0 - share) / (_PI * rows))
        moved += 0.5 * distance * rows / total
        noise += 0.5 * chance * rows / total
    return moved - 2.0 * noise


def _clock_parent(keys: "list[int]", rows: "list[int]", labels: "dict[str, list[str]]") -> str:
    best, chosen = PARENT_MOVE, ""
    for name in sorted(labels):
        cells = labels[name]
        moved = _moved_cells(keys, [_bare(cells[row]) for row in rows], 48)
        if moved > best:
            best, chosen = moved, name
    return chosen


def _label_columns(columns: "dict[str, list[str]]", skip: "set[str]") -> "dict[str, list[str]]":
    """The columns of two to ten different words: the ones a date's clock or gap may depend on."""
    found: "dict[str, list[str]]" = {}
    for name in columns:
        if name in skip:
            continue
        seen: "set[str]" = set()
        for cell in columns[name]:
            word = _bare(cell)
            if word and word not in seen:
                seen = seen | {word}
                if len(seen) > PARENT_LEVELS:
                    break
        if 2 <= len(seen) <= PARENT_LEVELS:
            found[name] = columns[name]
    return found


def _iqr(values: "list[int]") -> int:
    ordered = sorted(values)
    if not ordered:
        return 0
    last = len(ordered) - 1
    return ordered[(3 * last) // 4] - ordered[last // 4]


def _instant(day: int, tick: int) -> int:
    """A moment as one number of ticks from 1 January 1970 (a date with no clock at its midnight)."""
    return day * DAY_TICKS + (tick if tick >= 0 else 0)


def first_band_of(dates: int) -> int:
    """The band of a person's number of dates the timeline keeps the persons' first dates by (one date is a band)."""
    found = FIRST_BANDS[0]
    for band in FIRST_BANDS:
        if dates >= band:
            found = band
    return found


def time_block(day: int, tick: int) -> str:
    """Weekday or weekend, and the four-hour block of the day: the twelve blocks a minute-scale gap is kept by."""
    return f"{'e' if weekday(day) >= 5 else 'd'}{(tick if tick >= 0 else 0) // (4 * 3600 * TICKS)}"


def band_of(dates: int) -> int:
    """The band of a person's number of dates the timeline keeps its gaps by (a person of many dates has short gaps)."""
    found = BANDS[0]
    for band in BANDS:
        if dates >= band:
            found = band
    return found


def _presence(both: int, reference_only: int, own_only: int, neither: int) -> "list[int]":
    return _per_million([both, reference_only, own_only, neither])


def _levels_grid(values: "list[int]", levels: "list[str]", points: int) -> "dict[str, list[int]]":
    by_level: "dict[str, list[int]]" = {}
    for value, level in zip(values, levels):
        if level not in by_level:
            by_level[level] = []
        by_level[level] += [value]
    out: "dict[str, list[int]]" = {}
    for level in sorted(by_level):
        if _kept(len(by_level[level]), len(values), PARENT_LEAST_ROWS):
            out[level] = _grid(by_level[level], points)
    return out


def _kept(rows: int, total: int, least: int) -> bool:
    """Whether a cell of `rows` of `total` keeps its own census: the least rows, and a share no larger table moves.

    A cell is kept by its count AND by its share (`CELL_SHARE`), so a table twice as long keeps the same cells
    (the zone's size follows its cells, never its rows).
    """
    return rows >= least and rows >= CELL_SHARE * total


def _chain(name: str, earlier: "list[str]", days_of: "dict[str, list[int]]", seconds_of: "dict[str, list[int]]",
           labels: "dict[str, list[str]]") -> "dict[str, object] | None":
    """The chain of a date column to its nearest earlier date column of the row, None where it stands alone."""
    days = days_of[name]
    seconds = seconds_of[name]
    present = [row for row in range(len(days)) if days[row] != _ABSENT]
    if not present or not earlier:
        return None
    step = max(1, len(present) // 20000)
    probe = present[::step]
    own = _iqr([_instant(days[row], seconds[row]) for row in probe])
    best, reference = -1, ""
    # The nearest earlier column first: another one takes its place only where its gap is clearly tighter
    # (`TIGHTER`), so a column of a row's steps chains to the step before it, not to one its gap merely ties.
    for other in reversed(earlier):
        other_days = days_of[other]
        other_seconds = seconds_of[other]
        both = [row for row in probe if other_days[row] != _ABSENT]
        if len(both) < CHAIN_LEAST_SHARE * len(probe):
            continue
        spread = _iqr([_instant(days[row], seconds[row]) - _instant(other_days[row], other_seconds[row])
                       for row in both])
        if best < 0 or spread < TIGHTER * best:
            best, reference = spread, other
    if not reference or best > own // 2:
        return None
    reference_days = days_of[reference]
    reference_seconds = seconds_of[reference]
    rows = [row for row in present if reference_days[row] != _ABSENT]
    clocked = all(seconds[row] >= 0 and reference_seconds[row] >= 0 for row in rows)
    gaps = [_instant(days[row], seconds[row]) - _instant(reference_days[row], reference_seconds[row]) for row in rows]
    middle = sorted(abs(gap) for gap in gaps)[len(gaps) // 2] if gaps else 0
    entry: "dict[str, object]" = {"reference": reference, "ordered": bool(gaps) and min(gaps) >= 0}
    both_count = len(rows)
    reference_only = sum(1 for row in range(len(days)) if days[row] == _ABSENT and reference_days[row] != _ABSENT)
    own_only = len(present) - both_count
    neither = len(days) - both_count - reference_only - own_only
    entry["presence"] = _presence(both_count, reference_only, own_only, neither)
    if clocked and middle < DAY_TICKS:
        parent = _parent_of(gaps, rows, labels)
        entry["scale"] = "minute"
        entry["grid"] = _grid(gaps, GAP_GRID)
        entry["by"] = parent
        entry["cells"] = _levels_grid(gaps, [_bare(labels[parent][row]) for row in rows], CELL_GRID) if parent else {}
        return entry
    day_gaps = [days[row] - reference_days[row] for row in rows]
    entry["scale"] = "day"
    entry["ordered"] = bool(day_gaps) and min(day_gaps) >= 0 and bool(entry["ordered"])
    entry["day_ordered"] = bool(day_gaps) and min(day_gaps) >= 0
    entry["grid"] = _grid(day_gaps, GAP_GRID)
    entry["by"] = "weekday"
    entry["cells"] = _levels_grid(day_gaps, [f"{weekday(reference_days[row])}" for row in rows], CELL_GRID)
    return entry


def _clock_entry(days: "list[int]", seconds: "list[int]", rows: "list[int]",
                 labels: "dict[str, list[str]]") -> "dict[str, object]":
    """A clock census with, where one label column moves it, a census for each of its levels."""
    clocked = [row for row in rows if seconds[row] >= 0]
    entry = _clock([days[row] for row in clocked], [seconds[row] for row in clocked])
    parent = _clock_parent([_clock_key(seconds[row]) for row in clocked], clocked, labels) if clocked else ""
    entry["by"] = parent
    levels: "dict[str, object]" = {}
    if parent:
        by_level: "dict[str, list[int]]" = {}
        for row in clocked:
            level = _bare(labels[parent][row])
            if level not in by_level:
                by_level[level] = []
            by_level[level] += [row]
        for level in sorted(by_level):
            if _kept(len(by_level[level]), len(clocked), PARENT_LEAST_ROWS):
                levels[level] = _clock([days[row] for row in by_level[level]],
                                       [seconds[row] for row in by_level[level]])
    entry["levels"] = levels
    return entry


def _spellings(cells: "list[str]", reading: Reading) -> "dict[str, object]":
    sample = _spread_sample(cells, SAMPLE)
    if reading.kind == "count":
        return {"count": _count_spelling(sample, reading.member)}
    counts: "dict[str, int]" = {}
    keys: "dict[str, list[object]]" = {}
    for cell in sample:
        found = spelling_of(cell, reading)
        if found is None:
            continue
        key = f"{found}"
        counts[key] = (counts[key] if key in counts else 0) + 1
        keys[key] = found
    kept = _capped(counts, SPELLING_CAP)
    shares = _per_million([kept[key] for key in sorted(kept)])
    return {"text": [[*keys[key], share] for key, share in zip(sorted(kept), shares)]}


def _timeline(person: str, column: str, columns: "dict[str, list[str]]", days: "list[int]", seconds: "list[int]",
              labels: "dict[str, list[str]]", cache: "dict[int, tuple[int, int, int]]") -> "dict[str, object] | None":
    """Each person's first date and the gaps between a person's consecutive dates of the timeline column."""
    keys = columns[person]
    by_person: "dict[str, list[tuple[int, int, int]]]" = {}
    for row in range(len(days)):
        if days[row] == _ABSENT:
            continue
        key = _bare(keys[row])
        if not key:
            continue
        if key not in by_person:
            by_person[key] = []
        by_person[key] += [(_instant(days[row], seconds[row]), row, days[row])]
    if not by_person or len(days) < 1.5 * len(by_person):
        return None
    first_rows: "list[int]" = []
    first_bands: "list[int]" = []
    gaps: "list[int]" = []
    day_gaps: "list[int]" = []
    previous_weekdays: "list[str]" = []
    previous_blocks: "list[str]" = []
    bands: "list[int]" = []
    clocked = True
    for key in by_person:
        ordered = sorted(by_person[key])
        first_rows += [ordered[0][1]]
        first_bands += [first_band_of(len(ordered))]
        band = band_of(len(ordered))
        for k in range(1, len(ordered)):
            gaps += [ordered[k][0] - ordered[k - 1][0]]
            day_gaps += [ordered[k][2] - ordered[k - 1][2]]
            previous_weekdays += [f"{weekday(ordered[k - 1][2])}"]
            previous_blocks += [time_block(ordered[k - 1][2], seconds[ordered[k - 1][1]])]
            bands += [band]
        for _moment, row, _day in ordered:
            clocked = clocked and seconds[row] >= 0
    if not gaps:
        return None
    by_band: "dict[str, object]" = {}
    for band in FIRST_BANDS:
        mine_rows = [first_rows[k] for k in range(len(first_rows)) if first_bands[k] == band]
        if _kept(len(mine_rows), 2 * len(first_rows), FIRST_LEAST_PEOPLE) and len(mine_rows) >= 0.04 * len(first_rows):
            by_band[f"{band}"] = _calendar([days[row] for row in mine_rows], cache)
    whole = _calendar([days[row] for row in first_rows], cache)
    entry: "dict[str, object]" = {"person": person, "column": column, "calendar": whole, "calendars": by_band,
                                  "clock": _clock_entry(days, seconds, first_rows, labels) if clocked else None,
                                  "places": _places(by_person, by_band, whole, days)}
    middle = sorted(gaps)[len(gaps) // 2]
    minute = clocked and middle < DAY_TICKS
    values = gaps if minute else day_gaps
    keys = previous_blocks if minute else previous_weekdays
    entry["scale"] = "minute" if minute else "day"
    entry["grid"] = _grid(values, GAP_GRID)
    banded: "dict[str, object]" = {}
    for band in BANDS:
        rows_of = [k for k in range(len(values)) if bands[k] == band]
        if not _kept(len(rows_of), 2 * len(values), PARENT_LEAST_ROWS) or len(rows_of) < 0.02 * len(values):
            continue
        mine = [values[k] for k in rows_of]
        cells = _levels_grid(mine, [keys[k] for k in rows_of], BAND_GRID)
        banded[f"{band}"] = {"grid": _grid(mine, CELL_GRID), "cells": cells}
    entry["bands"] = banded
    return entry


def _places(by_person: "dict[str, list[tuple[int, int, int]]]", by_band: "dict[str, object]",
            whole: "dict[str, object]", days: "list[int]") -> "dict[str, object]":
    """Where each person of two dates or more starts inside the room its span leaves, by band, per million.

    A person's dates must end by the calendar's last month, so a person of a long span starts early: the place
    is the person's first date's position in its band's first-date calendar between the calendar's start (0)
    and the latest first date its span allows (1). The writer places a twin person at the same relative place.
    """
    present = [day for day in days if day != _ABSENT]
    year, month, _date = parsing.civil_from_days(max(present))
    last_day = parsing.days_from_civil(year, month, _days_in(year, month))
    prepared: "dict[str, _Calendar]" = {}
    for band in by_band:
        prepared[band] = _prepared_calendar(by_band[band])
    overall = _prepared_calendar(whole)
    found: "dict[str, list[int]]" = {}
    everyone: "list[int]" = []
    for key in by_person:
        ordered = sorted(by_person[key])
        if len(ordered) < 2:
            continue
        band = f"{first_band_of(len(ordered))}"
        calendar = prepared[band] if band in prepared else overall
        first, span = ordered[0][2], ordered[len(ordered) - 1][2] - ordered[0][2]
        latest = last_day - span
        if latest <= calendar.first_day:
            continue
        low = _position_of(calendar, calendar.first_day)
        high = _position_of(calendar, latest)
        place = (_position_of(calendar, first) - low) / (high - low) if high > low else 0.5
        value = int(min(1.0, max(0.0, place)) * PER)
        if band not in found:
            found[band] = []
        found[band] += [value]
        everyone += [value]
    out: "dict[str, object]" = {"grid": _grid(everyone, BAND_GRID) if everyone else []}
    for band in sorted(found):
        if _kept(len(found[band]), len(everyone), PARENT_LEAST_ROWS) and len(found[band]) >= 0.02 * len(everyone):
            out[band] = _grid(found[band], BAND_GRID)
    return out


def _always_before(first_days: "list[int]", first_seconds: "list[int]", second_days: "list[int]",
                   second_seconds: "list[int]") -> bool:
    """Whether every row holding both dates holds the first at or before the second (and at least the floor's rows do)."""
    both = 0
    for row in range(len(first_days)):
        if first_days[row] == _ABSENT or second_days[row] == _ABSENT:
            continue
        clocked = first_seconds[row] >= 0 and second_seconds[row] >= 0
        if clocked:
            if _instant(first_days[row], first_seconds[row]) > _instant(second_days[row], second_seconds[row]):
                return False
        elif first_days[row] > second_days[row]:
            return False
        both += 1
    return both >= PARENT_LEAST_ROWS


def _mixed_reading(cells: "list[str]") -> "Reading | None":
    """The member that reads the most of a column's cells as dates where some cells do but not the column.

    Only a cell of four figures or more can be a date, and a member that reads none of its first `MIXED_TRIES`
    such cells is passed by, so a column of numbers or words costs little. The members whose cells are figures
    alone or two-figure years (`MIXED_SET_ASIDE`) are not read here: among other values, a number of eight
    figures is an amount or a code far more often than a day. At least `MIXED_LEAST` cells, and a share of the
    present ones of `MIXED_SHARE`, must read.
    """
    present = [cell for cell in cells if _bare(cell)]
    sample = [cell for cell in _spread_sample(present, SAMPLE) if _figure_count(cell) >= 4]
    if not sample:
        return None
    best, chosen = 0, ""
    for member in TEXT_MEMBERS:
        if member in MIXED_SET_ASIDE:
            continue
        reading = Reading("text", member)
        found = 0
        for tried, cell in enumerate(sample):
            if tried >= MIXED_TRIES and found == 0:
                break
            found += 1 if moment_of(cell, reading) is not None else 0
        if found > best:
            best, chosen = found, member
    share = best / max(1, min(len(present), SAMPLE))
    if best < MIXED_LEAST or share < MIXED_SHARE:
        return None
    return Reading("text", chosen)


def _figure_count(cell: object) -> int:
    text = _text(cell)
    return sum(1 for character in text if character in _DIGITS)


def _mixed_columns(columns: "dict[str, list[str]]", skip: "set[str]",
                   cache: "dict[int, tuple[int, int, int]]") -> "dict[str, object]":
    """Columns that hold some dates among other values: each one's census of those dates, so the twin makes them up.

    A label or text column whose values are mostly not dates may still hold dates (a result written as a date, an
    answer that is a day): its category table would hand the twin those real days as levels. The census here lets
    `rewrite_mixed` write each such cell of the twin as a made-up date in the column's own spelling, the weekday
    and clock kept, so no real day finer than the year leaves through it.
    """
    out: "dict[str, object]" = {}
    for name in columns:
        if name in skip:
            continue
        cells = [_text(cell) for cell in columns[name]]
        reading = _mixed_reading(cells)
        if reading is None:
            continue
        days: "list[int]" = []
        seconds: "list[int]" = []
        for cell in cells:
            found = _moment(cell, reading) if _bare(cell) else None
            if found is not None:
                days += [found[0]]
                seconds += [found[1]]
        rows = list(range(len(days)))
        out[name] = {"reading": {"kind": reading.kind, "member": reading.member}, "dates": len(days),
                     "calendar": _calendar(days, cache),
                     "clock": _clock_entry(days, seconds, rows, {}) if any(second >= 0 for second in seconds) else None,
                     "spellings": _spellings(_dated_cells(cells, reading), reading),
                     "presence": [PER, 0]}
    return out


def _dated_cells(cells: "list[str]", reading: Reading) -> "list[str]":
    return [cell for cell in cells if _bare(cell) and moment_of(cell, reading) is not None]


def build_zone(columns: "dict[str, list[str]]", person: str = "", readings: "dict[str, str] | None" = None,
               skip: "tuple[str, ...]" = (), declared_only: bool = False) -> "dict[str, object]":
    """The dates zone of a table's inside record: a census a date column, its chain, and the timeline.

    `columns` maps each column's name to its cells as read; `person` names
    the column that names the person (the person's answer); `readings`
    the reading the product or the person gave a column (a member of
    `TEXT_MEMBERS` or of `date_counts.MEMBERS`: a column of counts is a date
    column only where it is declared); `skip` the columns never read as
    dates (record numbers). A column reads as dates where one member reads
    95 per cent of its present cells. `declared_only`: the columns
    `readings` names are the table's date columns and no other is (the
    profile step's established reading, `--day-first` and the person's
    answers in it: a column the description reads otherwise is never read
    again here, and one it reads day first is never read month first).
    """
    names = [name for name in columns]
    rows = len(columns[names[0]]) if names else 0
    declared = readings if readings is not None else {}
    cache: "dict[int, tuple[int, int, int]]" = {}
    read: "dict[str, Reading]" = {}
    days_of: "dict[str, list[int]]" = {}
    seconds_of: "dict[str, list[int]]" = {}
    for name in names:
        if name == person or name in skip or (declared_only and name not in declared):
            continue
        cells = [_text(cell) for cell in columns[name]]
        reading = reading_of(cells, declared[name] if name in declared else "")
        if reading is None:
            continue
        days: "list[int]" = []
        seconds: "list[int]" = []
        for cell in cells:
            found = _moment(cell, reading)
            if found is None:
                days += [_ABSENT]
                seconds += [-1]
            else:
                days += [found[0]]
                seconds += [found[1]]
        if all(day == _ABSENT for day in days):
            continue
        read[name] = reading
        days_of[name] = days
        seconds_of[name] = seconds
    labels = _label_columns(columns, {person, *skip, *read})
    entries: "dict[str, object]" = {}
    order = [name for name in names if name in read]
    for k, name in enumerate(order):
        days = days_of[name]
        seconds = seconds_of[name]
        present = [row for row in range(rows) if days[row] != _ABSENT]
        chain = _chain(name, order[:k], days_of, seconds_of, labels)
        # A minute-scale chain writes its clock from its reference and its gap: its own clock is
        # read only where the reference is missing, so it keeps no census by a label column.
        minute_chain = chain is not None and chain["scale"] == "minute"
        entry: "dict[str, object]" = {"reading": {"kind": read[name].kind, "member": read[name].member},
                                      "rows": rows, "present": len(present),
                                      "presence": _per_million([len(present), rows - len(present)]),
                                      "calendar": _calendar([days[row] for row in present], cache),
                                      "clock": _clock_entry(days, seconds, present, {} if minute_chain else labels)
                                      if any(seconds[row] >= 0 for row in present) else None,
                                      "spellings": _spellings(columns[name], read[name]),
                                      "chain": chain}
        entries[name] = entry
    orders: "list[list[str]]" = []
    for k, later in enumerate(order):
        for earlier in order[:k]:
            for first, second in ((earlier, later), (later, earlier)):
                if _always_before(days_of[first], seconds_of[first], days_of[second], seconds_of[second]):
                    orders += [[first, second]]
    timeline: "dict[str, object] | None" = None
    if person and person in columns and order:
        anchors = [name for name in order if typing.cast("dict[str, object]", entries[name])["chain"] is None]
        if anchors:
            timeline = _timeline(person, anchors[0], columns, days_of[anchors[0]], seconds_of[anchors[0]], labels,
                                 cache)
    return {"version": VERSION, "rows": rows, "person": person, "order": order, "columns": entries,
            "orders": orders, "timeline": timeline,
            "mixed": _mixed_columns(columns, {person, *skip, *read}, cache)}


def add_zone(record: "dict[str, object]", columns: "dict[str, list[str]]", person: str = "",
             readings: "dict[str, str] | None" = None, skip: "tuple[str, ...]" = ()) -> "dict[str, object]":
    """The inside record with its dates zone set (`inside.build_record`'s record; its other zones untouched)."""
    zones = record["zones"] if "zones" in record else None
    if not isinstance(zones, dict):
        raise DatesError("An inside record holds an object under 'zones'; this one does not.")
    zones[ZONE] = build_zone(columns, person, readings, skip)
    return record


# -- reading the zone back --------------------------------------------------------------------------------


def _versioned(zone: "dict[str, object]") -> None:
    """Refuse a zone of another version (`VERSION`): the writer would read its moments at another scale."""
    if "version" not in zone or zone["version"] != VERSION:
        raise DatesError("The dates zone is of another version; describe the table again.")


def _object(value: object) -> "dict[str, object]":
    if not isinstance(value, dict):
        raise DatesError("The dates zone is damaged: an object is missing where the zone keeps one.")
    return typing.cast("dict[str, object]", value)


def _numbers(value: object) -> "list[int]":
    if not isinstance(value, list):
        raise DatesError("The dates zone is damaged: a list is missing where the zone keeps one.")
    out: "list[int]" = []
    for item in value:
        if not isinstance(item, int) or isinstance(item, bool):
            raise DatesError("The dates zone is damaged: a whole number is missing where the zone keeps one.")
        out += [item]
    return out


def _rows(value: object) -> "list[list[int]]":
    if not isinstance(value, list):
        raise DatesError("The dates zone is damaged: a list is missing where the zone keeps one.")
    return [_numbers(item) for item in value]


def _word(value: object) -> str:
    if not isinstance(value, str):
        raise DatesError("The dates zone is damaged: a word is missing where the zone keeps one.")
    return value


def _cumulative(shares: "list[int]") -> "list[int]":
    out: "list[int]" = []
    total = 0
    for share in shares:
        total += share
        out += [total]
    return out


def _pick(cumulative: "list[int]", u: float) -> int:
    """The first index whose cumulative share passes `u` of the whole (a binary search)."""
    target = u * cumulative[len(cumulative) - 1]
    low, high = 0, len(cumulative) - 1
    while low < high:
        middle = (low + high) // 2
        if cumulative[middle] > target:
            high = middle
        else:
            low = middle + 1
    return low


@dataclasses.dataclass(frozen=True)
class _Calendar:
    months: "list[tuple[int, int]]"
    weekdays: "list[list[int]]"
    cumulative: "list[int]"
    first_day: int
    last_day: int


def _prepared_calendar(entry: object) -> _Calendar:
    found = _object(entry)
    years = _numbers(found["years"])
    cells = _rows(found["cells"])
    months: "list[tuple[int, int]]" = []
    weekdays: "list[list[int]]" = []
    shares: "list[int]" = []
    for year, row in zip(years, cells):
        for month in range(1, 13):
            week = row[(month - 1) * WEEK: month * WEEK]
            if sum(week) > 0:
                months += [(year, month)]
                weekdays += [week]
                shares += [sum(week)]
    if not months:
        raise DatesError("The dates zone is damaged: a calendar holds no month.")
    first_year, first_month = months[0]
    last_year, last_month = months[len(months) - 1]
    return _Calendar(months, weekdays, _cumulative(shares), parsing.days_from_civil(first_year, first_month, 1),
                     parsing.days_from_civil(last_year, last_month, _days_in(last_year, last_month)))


def _month_days(year: int, month: int, week: "list[int]",
                cache: "dict[tuple[int, ...], list[float]]") -> "list[float]":
    """The cumulative weights of a month's days: its weekday's share over the number of such weekdays in the month.

    Kept in `cache` by the month AND its weekday shares: two columns (or a column and its persons' first dates) share
    a month but not its weekdays, and weights kept by the month alone wrote one column's Fridays as the Mondays of
    the column written before it.
    """
    key = (year, month, *week)
    if key in cache:
        return cache[key]
    first = parsing.days_from_civil(year, month, 1)
    length = _days_in(year, month)
    many = [0] * WEEK
    for date in range(length):
        many[weekday(first + date)] += 1
    out: "list[float]" = []
    total = 0.0
    for date in range(length):
        found = weekday(first + date)
        total += week[found] / many[found]
        out += [total]
    cache[key] = out
    return out


def made_up_day(calendar: _Calendar, u: float, cache: "dict[tuple[int, ...], list[float]]") -> int:
    """The day a position `u` in (0, 1) of the calendar names: its month by the calendar, its day made up.

    The month is the one whose cumulative share passes `u`; the rest of
    `u` inside that month's share picks a day among the month's days, each
    weighing its weekday's share over the number of such weekdays in the
    month. So the weekday shares of each month come back exactly, a larger
    `u` never names an earlier day, and which of the month's Mondays a
    Monday falls on is made up.
    """
    target = u * calendar.cumulative[len(calendar.cumulative) - 1]
    index = _pick(calendar.cumulative, u)
    before = calendar.cumulative[index - 1] if index > 0 else 0
    share = calendar.cumulative[index] - before
    inside = min(max((target - before) / share, 0.0), 1.0) if share > 0 else 0.5
    year, month = calendar.months[index]
    weights = _month_days(year, month, calendar.weekdays[index], cache)
    goal = inside * weights[len(weights) - 1]
    last = 0
    for date in range(len(weights)):
        width = weights[date] - (weights[date - 1] if date > 0 else 0.0)
        if width <= 0.0:
            continue
        last = date
        if weights[date] >= goal:
            break
    return parsing.days_from_civil(year, month, 1) + last


@dataclasses.dataclass(frozen=True)
class _Clock:
    hours: "list[list[int]]"
    minutes: "list[list[int]]"
    seconds: "list[int]"
    marks: float


def _prepared_clock(entry: object) -> _Clock:
    found = _object(entry)
    hours = [_cumulative(row) for row in _rows(found["hour"])]
    minutes = [_cumulative(row) for row in _rows(found["minute"])]
    marks = found["marks"]
    if not isinstance(marks, int):
        raise DatesError("The dates zone is damaged: a clock's share of marks is missing.")
    return _Clock(hours, minutes, _cumulative(_numbers(found["second"])), marks / PER)


def _clocks(entry: object) -> "tuple[_Clock | None, str, dict[str, _Clock]]":
    if entry is None:
        return None, "", {}
    found = _object(entry)
    levels: "dict[str, _Clock]" = {}
    held = _object(found["levels"])
    for level in held:
        levels[level] = _prepared_clock(held[level])
    return _prepared_clock(found), _word(found["by"]), levels


def _second_of(clock: _Clock, day: int, state: "list[int]", fraction: bool = False) -> int:
    """A time of day in ticks drawn from the clock: the hour by the day's weekday, the minute by the hour, the second,
    and, for a column that writes fractions of a second (`fraction`), a fraction of its own."""
    week = clock.hours[weekday(day)]
    if week[len(week) - 1] <= 0:
        merged = [0] * 24
        for row in clock.hours:
            for hour in range(24):
                merged[hour] += row[hour] - (row[hour - 1] if hour > 0 else 0)
        week = _cumulative(merged)
    hour = _pick(week, _uniform(state))
    within = clock.minutes[hour]
    minute = _pick(within, _uniform(state)) if within[len(within) - 1] > 0 else 0
    second = _pick(clock.seconds, _uniform(state)) if clock.seconds[len(clock.seconds) - 1] > 0 else 0
    tick = (hour * 3600 + minute * 60 + second) * TICKS
    return tick + int(_uniform(state) * TICKS) if fraction else tick


def _quantile(grid: "list[int]", u: float) -> int:
    """The quantile function at `u`: its nearest point, an observed gap (never a value between two, so a gap of whole
    weeks stays whole weeks and a gap on five-minute marks stays on them)."""
    return grid[min(len(grid) - 1, max(0, int(u * (len(grid) - 1) + 0.5)))]


def _level(given: "dict[str, list[str]]", name: str, row: int) -> str:
    if not name or name not in given:
        return ""
    cells = given[name]
    return _bare(cells[row]) if row < len(cells) else ""


def _cell_positions(scores: "dict[str, list[float]]", name: str, rows: "list[int]", keys: "list[str]",
                    state: "list[int]") -> "dict[int, float]":
    """The generate step's scores of a column's rows as positions in (0, 1), ranked within each cell.

    A cell is the rows the zone draws alike (one level of the label a gap is kept by, one weekday of the
    reference, one band of a person's number of dates): a score says only where its row stands among them, so
    a gap is drawn from its own cell's quantile function at its row's place in that cell. A row with no score
    (none given, or not a number) draws its own.
    """
    if name not in scores:
        return {}
    found = scores[name]
    by_key: "dict[str, list[tuple[float, int]]]" = {}
    for row, key in zip(rows, keys):
        if row >= len(found):
            continue
        value = found[row]
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value != value:
            continue
        if key not in by_key:
            by_key[key] = []
        by_key[key] += [(float(value), row)]
    out: "dict[int, float]" = {}
    for key in by_key:
        ordered = sorted(by_key[key])
        for place, (_value, row) in enumerate(ordered):
            out[row] = _order_statistic(place + 1, len(ordered), state)
    return out


def _order_statistic(rank: int, count: int, state: "list[int]") -> float:
    """A position drawn as the `rank`-th of `count` independent positions in (0, 1) falls (near its Beta law).

    A rank alone would place a cell's rows on an even ladder of positions, which copies the real table's own
    sampling noise into the twin (a twin closer to the table than a fresh sample is, as the nearest-record check
    reads it). The `rank`-th of `count` uniform draws has mean rank / (count + 1) and variance m (1 - m) /
    (count + 2): the position is drawn about that mean with that spread (a sum of twelve draws less six stands
    for the normal), so the order of the scores is kept but for neighbours, and the twin's positions spread as
    an independent sample's would.
    """
    mean = rank / (count + 1)
    spread = math.sqrt(mean * (1.0 - mean) / (count + 2))
    normal = -6.0
    for _ in range(12):
        normal += _uniform(state)
    return min(max(mean + spread * normal, 0.5 / (count + 1)), 1.0 - 0.5 / (count + 1))


def _position(positions: "dict[int, float]", row: int, state: "list[int]") -> float:
    """The row's position from the generate step's scores where it gave one, else a draw of the stream."""
    if row in positions:
        return positions[row]
    return _uniform(state)


@dataclasses.dataclass(frozen=True)
class _Column:
    name: str
    calendar: _Calendar
    clock: "_Clock | None"
    clock_by: str
    clock_levels: "dict[str, _Clock]"
    presence: float
    minute_only: bool
    fractions: bool


def _writes_fractions(entry: "dict[str, object]") -> bool:
    """Whether a column's cells carry a fraction of a second: a spelling with figures after its seconds' point, or a
    counting system finer than the second."""
    reading = _object(entry["reading"])
    spellings = _object(entry["spellings"])
    if reading["kind"] == "count":
        member = _word(reading["member"])
        return member in date_counts.TABLE and date_counts.TABLE[member].unit < date_counts.SECOND
    keys = spellings["text"] if "text" in spellings else []
    if not isinstance(keys, list):
        raise DatesError("The dates zone is damaged: a column's spellings are no list.")
    for key in keys:
        if isinstance(key, list) and len(key) > 4 and isinstance(key[4], int) and key[4] > 0:
            return True
    return False


def _prepared_column(name: str, entry: "dict[str, object]") -> _Column:
    clock, by, levels = _clocks(entry["clock"])
    presence = _numbers(entry["presence"])
    fractions = _writes_fractions(entry)
    minute_only = not fractions
    if clock is not None:
        minute_only = minute_only and clock.seconds[0] >= clock.seconds[len(clock.seconds) - 1]
    return _Column(name, _prepared_calendar(entry["calendar"]), clock, by, levels, presence[0] / PER, minute_only,
                   fractions)


def _clock_for(column: _Column, given: "dict[str, list[str]]", row: int) -> "_Clock | None":
    level = _level(given, column.clock_by, row)
    if level and level in column.clock_levels:
        return column.clock_levels[level]
    return column.clock


def _heaped(moment: int, level: "_Clock | None", whole: "_Clock | None", state: "list[int]") -> int:
    """A person's next moment with its minute on a five-minute mark as often as the census heaps that level's rows.

    Only where the column heaps its minutes at all (over `HEAP_LINE` of them on a mark): a hand-typed row is put on
    the nearest mark as often as hand-typed rows are, and a row the census writes at any minute is moved off a mark.
    """
    if level is None or whole is None or whole.marks <= HEAP_LINE:
        return moment
    minute = moment // (60 * TICKS)
    if _uniform(state) < level.marks:
        return ((minute + 2) // 5) * 5 * 60 * TICKS
    return ((minute + 1) if minute % 5 == 0 else minute) * 60 * TICKS


def _anchored(column: _Column, u: float, row: int, given: "dict[str, list[str]]", state: "list[int]",
              cache: "dict[tuple[int, ...], list[float]]") -> "tuple[int, int]":
    day = made_up_day(column.calendar, u, cache)
    clock = _clock_for(column, given, row)
    return day, (_second_of(clock, day, state, column.fractions) if clock is not None else -1)


@dataclasses.dataclass(frozen=True)
class _Gaps:
    """A quantile function of gaps and its cells (by a label column's level, or by a weekday)."""

    grid: "list[int]"
    cells: "dict[str, list[int]]"


def _prepared_gaps(grid: object, cells: object) -> _Gaps:
    held = _object(cells)
    out: "dict[str, list[int]]" = {}
    for key in held:
        out[key] = _numbers(held[key])
    return _Gaps(_numbers(grid), out)


def _gaps_at(gaps: _Gaps, key: str) -> "list[int]":
    if key and key in gaps.cells:
        return gaps.cells[key]
    return gaps.grid


@dataclasses.dataclass(frozen=True)
class _Chain:
    reference: str
    minute: bool
    ordered: bool
    day_ordered: bool
    by: str
    gaps: _Gaps
    with_reference: float
    without_reference: float


def _prepared_chain(entry: object) -> "_Chain | None":
    if entry is None:
        return None
    found = _object(entry)
    presence = _numbers(found["presence"])
    minute = found["scale"] == "minute"
    day_ordered = "day_ordered" in found and found["day_ordered"] is True
    return _Chain(_word(found["reference"]), minute, found["ordered"] is True, day_ordered,
                  _word(found["by"]) if minute else "", _prepared_gaps(found["grid"], found["cells"]),
                  presence[0] / max(1, presence[0] + presence[1]), presence[2] / max(1, presence[2] + presence[3]))


def _after(reference: "tuple[int, int]", chain: _Chain, column: _Column, level: str, u: float, row: int,
           given: "dict[str, list[str]]", state: "list[int]") -> "tuple[int, int]":
    """A date after its reference by a gap of the chain, ordered where every real gap is at least nought."""
    reference_day, reference_second = reference
    if chain.minute:
        start = _instant(reference_day, reference_second)
        moment = start + _quantile(_gaps_at(chain.gaps, level), u)
        if column.minute_only:
            moment = (moment // (60 * TICKS)) * (60 * TICKS)
        if chain.ordered and moment < start:
            moment = start
        day = moment // DAY_TICKS
        return day, moment - day * DAY_TICKS
    day = reference_day + _quantile(_gaps_at(chain.gaps, f"{weekday(reference_day)}"), u)
    clock = _clock_for(column, given, row)
    if clock is None:
        return day, -1
    second = _second_of(clock, day, state, column.fractions)
    if day == reference_day and reference_second >= 0 and chain.day_ordered:
        tries = 0
        while second < reference_second and tries < REDRAWS:
            second = _second_of(clock, day, state, column.fractions)
            tries += 1
        second = max(second, reference_second)
    return day, second


def _is_present(column: _Column, present: "dict[str, list[bool]]", row: int, state: "list[int]") -> bool:
    if column.name in present:
        found = present[column.name]
        if row < len(found):
            return found[row] is True
    return _uniform(state) < column.presence


@dataclasses.dataclass(frozen=True)
class _Line:
    column: str
    minute: bool
    first: _Column
    firsts: "dict[int, _Calendar]"
    overall: "list[int]"
    bands: "dict[int, _Gaps]"
    places: "dict[str, list[int]]"


def _prepared_line(timeline: "dict[str, object]", column: _Column) -> _Line:
    first = dataclasses.replace(column, calendar=_prepared_calendar(timeline["calendar"]))
    first_clock, first_by, first_levels = _clocks(timeline["clock"])
    if first_clock is not None:
        first = dataclasses.replace(first, clock=first_clock, clock_by=first_by, clock_levels=first_levels)
    held = _object(timeline["bands"])
    bands: "dict[int, _Gaps]" = {}
    for band in BANDS:
        if f"{band}" in held:
            found = _object(held[f"{band}"])
            bands[band] = _prepared_gaps(found["grid"], found["cells"])
    calendars = _object(timeline["calendars"])
    firsts: "dict[int, _Calendar]" = {}
    for band in FIRST_BANDS:
        if f"{band}" in calendars:
            firsts[band] = _prepared_calendar(calendars[f"{band}"])
    held_places = _object(timeline["places"])
    places: "dict[str, list[int]]" = {}
    for key in held_places:
        places[key] = _numbers(held_places[key])
    return _Line(column.name, timeline["scale"] == "minute", first, firsts, _numbers(timeline["grid"]), bands, places)


def _first_calendar(line: _Line, dates: int) -> _Calendar:
    """The calendar of the first dates of the persons of the band of `dates` dates, else of every person."""
    band = first_band_of(dates)
    if band in line.firsts:
        return line.firsts[band]
    return line.first.calendar


def _band_gaps(line: _Line, dates: int, weekday_key: str) -> "list[int]":
    """The gaps of the band of a person's number of dates (by the weekday of the date before, on a day scale)."""
    chosen = 0
    for band in BANDS:
        if dates >= band and band in line.bands:
            chosen = band
    if not chosen:
        return line.overall
    return _gaps_at(line.bands[chosen], weekday_key)


def _position_of(calendar: _Calendar, day: int) -> float:
    """Where a day stands in the calendar, as the position in (0, 1) `made_up_day` reads (its month's share in part)."""
    year, month, date = parsing.civil_from_days(day)
    total = calendar.cumulative[len(calendar.cumulative) - 1]
    before = 0
    for index in range(len(calendar.months)):
        if calendar.months[index] < (year, month):
            before = calendar.cumulative[index]
            continue
        if calendar.months[index] == (year, month):
            share = calendar.cumulative[index] - before
            return (before + share * date / _days_in(year, month)) / total
        break
    return before / total


def _person_dates(line: _Line, column: _Column, members: "list[int]", start: "tuple[int, int]", shrink: float,
                  given: "dict[str, list[str]]", positions: "dict[int, float]",
                  state: "list[int]") -> "list[tuple[int, int]]":
    """One person's dates: the first, then a gap of the person's band each (positions shrunk where they overrun)."""
    moments = [start]
    for row in members[1:]:
        u = _position(positions, row, state) * shrink
        last_day, last_second = moments[len(moments) - 1]
        if line.minute:
            begin = _instant(last_day, last_second)
            moment = begin + _quantile(_band_gaps(line, len(members), time_block(last_day, last_second)), u)
            if column.minute_only:
                moment = _heaped((moment // (60 * TICKS)) * (60 * TICKS), _clock_for(column, given, row),
                                 column.clock, state)
            moment = max(moment, begin)
            day = moment // DAY_TICKS
            moments += [(day, moment - day * DAY_TICKS)]
            continue
        day = last_day + max(0, _quantile(_band_gaps(line, len(members), f"{weekday(last_day)}"), u))
        clock = _clock_for(column, given, row)
        second = _second_of(clock, day, state, column.fractions) if clock is not None else -1
        if clock is not None and day == last_day:
            tries = 0
            while second < last_second and tries < REDRAWS:
                second = _second_of(clock, day, state, column.fractions)
                tries += 1
            second = max(second, last_second)
        moments += [(day, second)]
    return moments


def _placed(line: _Line, calendar: _Calendar, last_day: int, dates: int, first_day: int, end: int, u: float,
            cache: "dict[tuple[int, ...], list[float]]") -> int:
    """The whole weeks a person's dates move by to start at the relative place a real person of its band starts."""
    band = f"{first_band_of(dates)}"
    grid = line.places[band] if band in line.places else (line.places["grid"] if "grid" in line.places else [])
    latest = last_day - (end - first_day)
    if dates < 2 or not grid or latest <= calendar.first_day:
        return 0
    low = _position_of(calendar, calendar.first_day)
    high = _position_of(calendar, latest)
    place = _quantile(grid, u) / PER
    target = min(made_up_day(calendar, low + place * (high - low), cache), latest)
    shift = WEEK * ((first_day - target + WEEK // 2) // WEEK)
    while end - shift > last_day:
        shift += WEEK
    while first_day - shift < calendar.first_day and end - shift + WEEK <= last_day:
        shift -= WEEK
    return shift


def _timeline_moments(line: _Line, column: _Column, people: "list[str]", rows: int, given: "dict[str, list[str]]",
                      scores: "dict[str, list[float]]", seed: int,
                      cache: "dict[tuple[int, ...], list[float]]") -> "tuple[list[int], list[int]]":
    """Each twin person's dates of the timeline column: a first date, then the person's gaps, kept in the calendar.

    A person whose dates would pass the calendar's last month is moved earlier by whole weeks (every weekday,
    clock and gap kept) to a first date drawn again from the first dates' calendar up to the latest first date
    that fits, so the persons of long spans start early as the real ones do and none piles up at the end.
    """
    state = _stream(seed, column.name, "timeline")
    groups: "dict[str, list[int]]" = {}
    for row in range(rows):
        key = _bare(people[row]) if row < len(people) else ""
        if key not in groups:
            groups[key] = []
        groups[key] += [row]
    days = [_ABSENT] * rows
    seconds = [-1] * rows
    span = column.calendar.last_day - column.calendar.first_day
    firsts: "list[int]" = []
    first_keys: "list[str]" = []
    later: "list[int]" = []
    later_keys: "list[str]" = []
    for key in groups:
        members = groups[key]
        firsts += [members[0]]
        first_keys += [f"{first_band_of(len(members))}"]
        later += members[1:]
        later_keys += [f"{band_of(len(members))}"] * (len(members) - 1)
    positions = _cell_positions(scores, column.name, firsts, first_keys, state)
    gaps_at = _cell_positions(scores, column.name, later, later_keys, state)
    for row in gaps_at:
        positions[row] = gaps_at[row]
    for key in groups:
        members = groups[key]
        opening = dataclasses.replace(line.first, calendar=_first_calendar(line, len(members)))
        start = _anchored(opening, _position(positions, members[0], state), members[0], given, state, cache)
        shrink = 1.0
        moments = _person_dates(line, column, members, start, shrink, given, positions, state)
        tries = 0
        while moments[len(moments) - 1][0] - moments[0][0] > span and tries < REDRAWS:
            shrink = shrink * 0.7
            moments = _person_dates(line, column, members, start, shrink, given, positions, state)
            tries += 1
        first_day = moments[0][0]
        end = moments[len(moments) - 1][0]
        shift = _placed(line, opening.calendar, column.calendar.last_day, len(members), first_day, end,
                        _position(positions, members[0], state), cache)
        if end - shift > column.calendar.last_day:
            latest = column.calendar.last_day - (end - first_day)
            if latest >= opening.calendar.first_day:
                wanted = made_up_day(opening.calendar, _uniform(state) * _position_of(opening.calendar, latest), cache)
                wanted = min(wanted, latest)
                shift = WEEK * ((first_day - wanted + WEEK - 1) // WEEK)
            else:
                shift = max(0, WEEK * ((first_day - column.calendar.first_day) // WEEK))
        for row, (day, second) in zip(members, moments):
            days[row] = day - shift
            seconds[row] = second
    return days, seconds


def _widths(keys: "list[list[object]]") -> str:
    """The width the column's cells show most (by share), the product's default where none shows one."""
    best, chosen = -1, parsing.DEFAULT_FIELD_WIDTH
    for key in keys:
        width, share = key[0], key[6]
        if isinstance(width, str) and width and isinstance(share, int) and share > best:
            best, chosen = share, width
    return chosen


def _spelled_text(day: int, tick: int, member: str, key: "list[object]", fallback: str) -> str:
    """A moment (an instant) written in one of the column's spellings: moved into the spelling's offset, its clock at
    the spelling's step and its fraction of a second the moment's own, to the spelling's figures (cut, never rounded,
    so two moments in order are written in order)."""
    width, style, mark, form, figures, offset = key[0], key[1], key[2], key[3], key[4], key[5]
    written_offset = _word(offset)
    shift = _offset_seconds(written_offset) if tick >= 0 else 0
    if shift:
        moved = day * DAY_TICKS + tick + shift * TICKS
        day, tick = moved // DAY_TICKS, moved % DAY_TICKS
    year, month, date = parsing.civil_from_days(day)
    half = parsing.written_date(year, month, date, member, _word(width) or fallback, _word(style))
    clock_form = _word(form)
    if not clock_form or tick < 0:
        return half
    step = parsing.clock_step(clock_form)
    clock = parsing.clock_spelling((tick // TICKS) // step, clock_form)
    if isinstance(figures, int) and figures > 0:
        nine = f"{tick % TICKS:09d}"
        clock = f"{clock}.{nine[:figures]}{'0' * max(0, figures - 9)}"
    return f"{half}{_word(mark)}{clock}{written_offset}"


def _spelled_count(day: int, second: int, member: str, form: "dict[str, object]", state: "list[int]") -> str:
    places, trimmed, significant, exponent, mark = (form["places"], form["trimmed"], form["significant"],
                                                     form["exponent"], form["mark"])
    contacts: "dict[str, int] | None" = None
    contact = date_counts.NO_CONTACT
    if "contacts" in form:
        shares = form["contacts"]
        if isinstance(shares, list) and shares:
            words = [_word(item[0]) for item in shares if isinstance(item, list)]
            weights = _cumulative([item[1] for item in shares if isinstance(item, list) and isinstance(item[1], int)])
            contacts = {word: 1 for word in words}
            contact = words[_pick(weights, _uniform(state))] if weights and weights[len(weights) - 1] > 0 else contact
    built = date_counts.CountForm(int(typing.cast("int", places)), trimmed is True,
                                  significant if isinstance(significant, int) else None, exponent is True,
                                  _word(mark), contacts)
    written = date_counts.written_for(member, _instant(day, second), date_counts.NANOSECOND, built, contact)
    return written if written is not None else ""


def _ordered(zone: "dict[str, object]", moments: "dict[str, tuple[list[int], list[int]]]") -> None:
    """Every ordering the real table never breaks (an earlier column at or before a later one) held in the twin."""
    pairs = zone["orders"] if "orders" in zone else []
    if not isinstance(pairs, list):
        raise DatesError("The dates zone is damaged: its orderings are no list.")
    for pair in pairs:
        if not isinstance(pair, list) or len(pair) != 2:
            raise DatesError("The dates zone is damaged: an ordering is no pair of columns.")
        first, second = _word(pair[0]), _word(pair[1])
        if first not in moments or second not in moments:
            continue
        first_days, first_seconds = moments[first]
        second_days, second_seconds = moments[second]
        for row in range(len(first_days)):
            if first_days[row] == _ABSENT or second_days[row] == _ABSENT:
                continue
            if second_days[row] < first_days[row]:
                second_days[row] = first_days[row]
                if second_seconds[row] >= 0:
                    second_seconds[row] = max(second_seconds[row], first_seconds[row])
            elif second_days[row] == first_days[row] and 0 <= second_seconds[row] < first_seconds[row]:
                second_seconds[row] = first_seconds[row]


def write_dates(zone: "dict[str, object]", rows: int, people: "list[str] | None" = None,
                given: "dict[str, list[str]] | None" = None, scores: "dict[str, list[float]] | None" = None,
                present: "dict[str, list[bool]] | None" = None, seed: int = 0) -> "dict[str, list[str]]":
    """The twin's cells of every date column of the zone (the hook the generate step calls).

    `rows` is the twin's number of rows; `people` its person column's cells
    (each person's rows in the order they are written); `given` the twin's
    cells of the label columns the zone's clocks and gaps depend on;
    `scores` one number a row and date column that ties the date to the
    twin's other columns (a latent score of the generate step: only its
    order within the rows the zone draws alike is read; `_cell_positions`);
    `present` the rows of a column that hold a date. Every ordering the
    real table never breaks between two date columns of a row holds in the
    twin (`orders`). Same zone and seed, same cells.
    """
    found = _object(zone)
    _versioned(found)
    entries = _object(found["columns"])
    order = [_word(name) for name in typing.cast("list[object]", found["order"])]
    timeline = found["timeline"]
    held = given if given is not None else {}
    tied = scores if scores is not None else {}
    holds = present if present is not None else {}
    cache: "dict[tuple[int, ...], list[float]]" = {}
    moments: "dict[str, tuple[list[int], list[int]]]" = {}
    columns: "dict[str, _Column]" = {}
    for name in order:
        columns[name] = _prepared_column(name, _object(entries[name]))
    if isinstance(timeline, dict) and people is not None:
        name = _word(typing.cast("dict[str, object]", timeline)["column"])
        line = _prepared_line(typing.cast("dict[str, object]", timeline), columns[name])
        days, seconds = _timeline_moments(line, columns[name], people, rows, held, tied, seed, cache)
        state = _stream(seed, name, "present")
        for row in range(rows):
            if not _is_present(columns[name], holds, row, state):
                days[row] = _ABSENT
        moments[name] = (days, seconds)
    for name in order:
        if name in moments:
            continue
        column = columns[name]
        link = _prepared_chain(_object(entries[name])["chain"])
        state = _stream(seed, name, "dates")
        days = [_ABSENT] * rows
        seconds = [-1] * rows
        dated: "list[int]" = []
        keys: "list[str]" = []
        if link is not None:
            reference_days, reference_seconds = moments[link.reference]
            for row in range(rows):
                there = reference_days[row] != _ABSENT
                if name in holds and row < len(holds[name]):
                    mine = holds[name][row] is True
                else:
                    mine = _uniform(state) < (link.with_reference if there else link.without_reference)
                if not mine:
                    continue
                dated += [row]
                if not there:
                    keys += ["(alone)"]
                elif link.minute:
                    keys += [_level(held, link.by, row)]
                else:
                    keys += [f"{weekday(reference_days[row])}"]
            positions = _cell_positions(tied, name, dated, keys, state)
            for row, key in zip(dated, keys):
                u = _position(positions, row, state)
                if key == "(alone)":
                    day, second = _anchored(column, u, row, held, state, cache)
                else:
                    day, second = _after((reference_days[row], reference_seconds[row]), link, column,
                                         _level(held, link.by, row), u, row, held, state)
                days[row] = day
                seconds[row] = second
        else:
            for row in range(rows):
                if _is_present(column, holds, row, state):
                    dated += [row]
            positions = _cell_positions(tied, name, dated, [""] * len(dated), state)
            for row in dated:
                day, second = _anchored(column, _position(positions, row, state), row, held, state, cache)
                days[row] = day
                seconds[row] = second
        moments[name] = (days, seconds)
    _ordered(found, moments)
    out: "dict[str, list[str]]" = {}
    for name in order:
        entry = _object(entries[name])
        reading = _object(entry["reading"])
        member = _word(reading["member"])
        spellings = _object(entry["spellings"])
        state = _stream(seed, name, "spelling")
        days, seconds = moments[name]
        cells: "list[str]" = []
        if reading["kind"] == "count":
            form = _object(spellings["count"])
            for row in range(rows):
                cells += ["" if days[row] == _ABSENT else _spelled_count(days[row], seconds[row], member, form, state)]
        else:
            spelled = typing.cast("list[list[object]]", spellings["text"])
            weights = _cumulative([int(typing.cast("int", item[6])) for item in spelled])
            fallback = _widths(spelled)
            for row in range(rows):
                if days[row] == _ABSENT or not spelled:
                    cells += [""]
                    continue
                chosen = spelled[_pick(weights, _uniform(state))] if weights[len(weights) - 1] > 0 else spelled[0]
                cells += [_spelled_text(days[row], seconds[row], member, chosen, fallback)]
        out[name] = cells
    return out


def rewrite_mixed(zone: "dict[str, object]", name: str, cells: "list[str]", seed: int = 0) -> "list[str]":
    """A twin column's cells with every cell that reads as a date written again as a made-up date.

    For a column the zone's `mixed` part names (dates among other values): the generate step writes the
    column from its other zones, then hands its cells here; each one that reads as a date under the column's
    member is replaced by a made-up date (the calendar's month and weekday, the clock, a made-up day of the
    month) in one of the column's own spellings. Every other cell is kept as it is.
    """
    found = _object(zone)
    _versioned(found)
    mixed = _object(found["mixed"]) if "mixed" in found else {}
    if name not in mixed:
        return list(cells)
    entry = _object(mixed[name])
    reading_entry = _object(entry["reading"])
    reading = Reading(_word(reading_entry["kind"]), _word(reading_entry["member"]))
    column = _prepared_column(name, entry)
    spellings = _object(entry["spellings"])
    spelled = typing.cast("list[list[object]]", spellings["text"])
    weights = _cumulative([int(typing.cast("int", item[6])) for item in spelled])
    fallback = _widths(spelled)
    state = _stream(seed, name, "mixed")
    cache: "dict[tuple[int, ...], list[float]]" = {}
    out: "list[str]" = []
    for row in range(len(cells)):
        cell = _text(cells[row])
        if not _bare(cell) or moment_of(cell, reading) is None or not spelled or weights[len(weights) - 1] <= 0:
            out += [cell]
            continue
        day, second = _anchored(column, _uniform(state), row, {}, state, cache)
        chosen = spelled[_pick(weights, _uniform(state))]
        out += [_spelled_text(day, second, reading.member, chosen, fallback)]
    return out

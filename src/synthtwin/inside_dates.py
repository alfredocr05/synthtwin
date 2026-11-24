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

EVERY TWIN DATE LIES IN ITS COLUMN'S REAL MONTHS (lane IN-5, batch 4zz):
the first day of the calendar's first month to the last day of its last.
A person's placement, and every whole-week move that holds the
description's twin's months (`_held_months`), stays inside the room the
person's dates -- and the dates chained to them -- leave in their own
columns' months; a last pass (`_kept_inside`) moves anything still outside
in with its person or its row's chain, by whole weeks where they fit.

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

from synthtwin import chain_walk, date_counts, offset_rules, parsing, twinstore

ZONE = "dates"
# Version 2: moments are instants in nanoseconds (version 1 held wall clocks in whole seconds; a writer reading one
# would draw gaps a billion times too short, so it refuses it and the twin keeps the description's dates).
# Version 3: every census a twin's day or minute is drawn from is pulled toward its pooled shape as far as the
# real departures from that shape allow (`_concentration`), and where a person starts inside its room is kept as
# shares of `PLACE_BINS` bins: a version 2 zone held the persons' first dates by band in cells of month by
# weekday of a few real persons each and their places on a grid of real persons' own places, and its twins sat on
# real persons' times (lane IN-5b), so the writer refuses it and the twin keeps the description's dates.
VERSION = 3
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
# The counting system a held column's counts are read in (`_mixed_reading`'s ``held``), by their whole figures:
# days (Excel's count from 1899-12-30), seconds and milliseconds from 1970.
HELD_COUNT_MEMBERS = {date_counts.DAY_FIGURES: date_counts.EXCEL_1900, 10: date_counts.SECONDS_SINCE_1970,
                      13: date_counts.MILLISECONDS_SINCE_1970}
MIXED_SET_ASIDE = ("compact-date", "two-digit-month-first-date", "two-digit-day-first-date",
                   "dotted-two-digit-month-first-date", "dotted-two-digit-day-first-date")
CELL_SHARE = 0.01
TIGHTER = 0.9
BANDS = (2, 3, 4, 5, 7, 10, 20, 50)
FIRST_BANDS = (1, 2, 3, 4, 5, 7, 10, 20, 50)
BAND_GRID = 101
# Where a person starts inside the room its span leaves: shares of this many equal bins, a place drawn evenly
# inside its bin (a tenth of the room: wide against any person's span of dates, so no real person's place is kept).
PLACE_BINS = 10
# THE WEEKDAY A DAY-SCALE GAP LANDS ON (lane STATS-A, batch 4zz). A quantile function of gaps on 101 or 201 points
# holds a gap every few days where the gaps run to months, so the weekday a drawn gap lands on was whatever those few
# points' gaps happened to fall on: measured on the type battery's date table (20,000 rows, 5,000 persons, gaps up to
# three years), each weekday cell's grid put the gaps' weekday shares up to 0.08 from the real ones (0.037 on average),
# and the twin's later dates drifted to 2,400 Mondays and 2,043 Sundays for the real 2,227 and 2,190 (validate's window
# about 150). So each grid keeps, for each of `LANDING_BINS` equal parts of its positions whose gaps span a week or
# more, where its real gaps land (`_landings`): a cell of one weekday of the date before keeps the weekday they land
# on; a grid of every weekday (a band's, the timeline's, a chain's, read where a weekday keeps no cell of its own)
# keeps each gap's days past whole weeks (a weekly schedule) or the weekday they land on (a clinic open on weekdays),
# whichever the real gaps follow more closely (`_past_weeks_fit`).
# The writer moves the grid's gap by at most three days inside that part's span to land on a weekday drawn from them
# (`_landed`). A part narrower than a week (gaps of nought, whole weeks, a few days) keeps the grid's own gap, so
# same-day repeats and weekly schedules stand.
LANDING_BINS = 10
# What a grid of every weekday keeps (`_past_weeks_fit`): its gaps' days past whole weeks, or the weekday they land
# on; a zone written before the choice keeps days past whole weeks.
LANDINGS_PAST_WEEKS = "past_weeks"
LANDINGS_WEEKDAY = "weekday"

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


def stream_of(seed: int, name: object, purpose: object) -> "list[int]":
    """A SplitMix64 stream of the seed, a column's name and a purpose, for another writer of the inside record (lane
    ZOO-Y's real range, `generation._inside_ranged`): the same draws as this zone's own, no random source imported."""
    return _stream(seed, name, purpose)


def uniform_of(state: "list[int]") -> float:
    """The next number in (0, 1) of a stream `stream_of` made."""
    return _uniform(state)


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
    return _spelling_shown(cell, reading)[0]


def _hour_shown(rest: str, offset: str) -> str:
    """The hour width the clock after a date's half shows: `h`, `hh`, or "" where its hour, ten or past, shows none."""
    body = _text(rest)
    while body and (body[0] == " " or body[0] == "T" or body[0] == "t"):
        body = body[1:]
    if offset and body[len(body) - len(offset):] == offset:
        body = body[: len(body) - len(offset)]
    for index in range(len(body)):
        if body[index] == "." and _figures(body[index + 1:]):
            body = body[:index]
            break
    parts = parsing.clock_parts(body)
    return parsing.clock_shown_width(parts) if parts is not None else ""


# A spelling's clock form opens with its hour width (`parsing.CLOCK_HOUR_WIDTHS`), and a month name style is
# `case-length-rest`, its length `full`, `abbreviated` or `either` (`parsing.NAME_LENGTH_EITHER`).
_HOUR_WIDTHS = ("hh", "h")
_NAME_LENGTHS = ("full", "abbreviated")


def _style_pieces(style: str) -> "list[str]":
    """A month name style's case, length and the rest (`case-length-rest`), split at its first two hyphens by hand."""
    pieces: "list[str]" = []
    start = 0
    for index in range(len(style)):
        if style[index] == "-" and len(pieces) < 2:
            pieces += [style[start:index]]
            start = index + 1
    return pieces + [style[start:]]


def _with_hour_width(form: str, width: str) -> str:
    """A clock form's hour width set to `width` (a form of figures, which has one width, as it is)."""
    if parsing.CLOCK_FIGURES in form:
        return form
    for written in _HOUR_WIDTHS:
        if form[: len(written)] == written and form[len(written): len(written) + 1] == "-":
            return width + form[len(written):]
    return form


def _resolved_keys(pairs: "list[tuple[list[object] | None, str]]") -> "list[list[object] | None]":
    """Each spelling with what its own cell does not show taken from the column's other cells (lane ZOO-X).

    A CELL SHOWS NO HOUR WIDTH WHERE ITS HOUR IS TEN OR PAST (`11:17 AM`,
    `14:22`: `h` and `hh` write it alike), and no length of a month's name
    where the month is May; `spelling_of` keys such a cell at `hh` and at
    the `either` length, and the twin then wrote every moment dealt that
    key at two figures of hour (`04:02 PM` in a column that writes `4:02
    PM`, on 13,847 of 20,000 cells) and every month at its abbreviation
    (`Jun 1, 2022` in a column that writes `June`). Each such key takes the
    width, or the length, the column's cells that show one show most (two
    figures of hour, and the full name, on a tie); a column none of whose
    cells shows one keeps its keys as they are. ``pairs`` is each cell's key
    (`spelling_of`) and the hour width its clock shows (`_hour_shown`; "-"
    where it writes no clock). Raises nothing. No I/O.
    """
    widths = {width: 0 for width in _HOUR_WIDTHS}
    lengths: "dict[str, dict[str, int]]" = {}
    # Each style split once, and each (key, width shown) resolved once: a column of millions of cells holds a few
    # spellings, and the cells that share one share its resolved key (one list, not one a cell).
    styles: "dict[str, list[str]]" = {}
    for key, shown in pairs:
        if key is None:
            continue
        if shown in widths and _word(key[3]):
            widths[shown] += 1
        style = _word(key[1])
        if style not in styles:
            styles[style] = _style_pieces(style)
        pieces = styles[style]
        if len(pieces) == 3 and pieces[1] in _NAME_LENGTHS:
            family = f"{pieces[0]}-{pieces[2]}"
            if family not in lengths:
                lengths[family] = {length: 0 for length in _NAME_LENGTHS}
            lengths[family][pieces[1]] += 1
    width = "h" if widths["h"] > widths["hh"] else "hh"
    made: "dict[tuple[object, ...], list[object]]" = {}
    out: "list[list[object] | None]" = []
    for key, shown in pairs:
        if key is None:
            out += [None]
            continue
        held = (*key, shown)
        if held in made:
            out += [made[held]]
            continue
        resolved = list(key)
        if shown == "" and _word(key[3]) and widths["h"] + widths["hh"]:
            resolved[3] = _with_hour_width(_word(key[3]), width)
        pieces = styles[_word(key[1])]
        if len(pieces) == 3 and pieces[1] == parsing.NAME_LENGTH_EITHER:
            family = f"{pieces[0]}-{pieces[2]}"
            counted = lengths[family] if family in lengths else None
            if counted is not None and counted["full"] + counted["abbreviated"]:
                length = "abbreviated" if counted["abbreviated"] > counted["full"] else "full"
                resolved[1] = f"{pieces[0]}-{length}-{pieces[2]}"
        made[held] = resolved
        out += [resolved]
    return out


def _spelling_shown(cell: object, reading: Reading) -> "tuple[list[object] | None, str]":
    """`spelling_of`'s key and the hour width its clock shows (`_hour_shown`; "-" where the cell writes no clock)."""
    text = _bare(cell)
    found = _wall_of(text, reading)
    if found is None:
        return None, "-"
    # The day and clock AS WRITTEN (an offset's instant may fall on another day): the spelling is read off them.
    day, second, _offset = found
    year, month, date = parsing.civil_from_days(day)
    width = parsing.date_field_style(text, reading.member)
    style = parsing.month_name_style(text, reading.member)
    width_text = width if width is not None else parsing.DEFAULT_FIELD_WIDTH
    style_text = style if style is not None else parsing.DEFAULT_NAME_STYLE
    half = parsing.written_date(year, month, date, reading.member, width_text, style_text)
    if not _starts(text, half):
        return None, "-"
    rest = text[len(half):]
    # A width no field of this cell shows (every field of two figures) is kept as '' and written, in the twin, as
    # the width the column's other cells show (`_widths`).
    shown = width if width is not None else ""
    if second < 0:
        return ([shown, style_text, "", "", 0, ""] if not rest else None), "-"
    written_offset = _offset_of(text, reading.member)
    parts = _clock_parts(rest, written_offset)
    if parts is None:
        return None, "-"
    mark, form, figures, offset = parts
    return [shown, style_text, mark, form, figures, offset], _hour_shown(rest, written_offset)


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


def _per_million_of(weights: "list[float]") -> "list[int]":
    """Weights as shares per million that sum to exactly `PER` (largest remainders), all nought where they are."""
    total = math.fsum(weights)
    if total <= 0.0:
        return [0 for _ in weights]
    exact = [weight * PER / total for weight in weights]
    floors = [int(value) for value in exact]
    left = PER - sum(floors)
    ranked = sorted((floors[k] - exact[k], k) for k in range(len(exact)))
    for _remainder, k in ranked[:left]:
        floors[k] += 1
    return floors


# -- smoothing a census toward its pooled shape -----------------------------------------------------
#
# A census of fine cells (a month's seven weekdays, an hour's sixty minutes) read from a table of a few thousand
# persons holds, besides the table's real shape, the weekdays and the minutes ITS persons happened to come at. A
# twin drawn from it lands on the real persons' own days and minutes more often than a fresh sample of the same
# people would (lane IN-1's nearest-record and rare-date checks read exactly that). So each group of cells (a
# month, an hour) is read as its own shares spread about a pooled shape (the whole calendar's weekdays, the
# whole clock's minutes) with a Dirichlet concentration, estimated by the method of moments from how far the
# groups really depart from the pooled shape; each group's shares are its counts pulled toward that shape by the
# concentration. A real departure (no scheduled case before the 07:30 first slot, a clinic held on Mondays only)
# is kept almost whole; a departure no larger than chance makes is pulled into the pooled shape.


def _concentration(groups: "list[list[int]]", priors: "list[list[float]]") -> float:
    """How far groups of counts spread about their pooled shares beyond chance, as a Dirichlet concentration.

    A group of `n` counts drawn with shares that themselves spread about the prior shares with concentration
    `alpha` gives Pearson's statistic an expectation of (cells - 1)(n + alpha) / (1 + alpha); summed over the
    groups and solved for `alpha`. Returns -1.0 where the groups spread no more than draws of the prior shares
    themselves would (no departure beyond chance: the prior alone is the estimate), 0.0 where they spread as far
    as can be (each group keeps its own counts).
    """
    statistic = 0.0
    freedom = 0.0
    weighted = 0.0
    for counts, prior in zip(groups, priors):
        total = sum(counts)
        if total <= 0:
            continue
        cells = 0
        for count, share in zip(counts, prior):
            if share <= 0.0:
                continue
            cells += 1
            expected = total * share
            statistic += (count - expected) * (count - expected) / expected
        if cells > 1:
            freedom += cells - 1
            weighted += (cells - 1) * total
    if freedom <= 0.0 or statistic <= freedom:
        return -1.0
    if statistic >= weighted:
        return 0.0
    return (weighted - statistic) / (statistic - freedom)


def _pulled(counts: "list[int]", prior: "list[float]", alpha: float, weight: "float | None" = None) -> "list[float]":
    """A group's shares: its counts pulled toward the prior shares by the concentration (-1.0: the prior itself).

    `weight`, where given, is the size the pull is read at (a group's persons where its counts are rows), so a
    group of many rows of few persons is pulled as its persons warrant; its own shares are then its counts'.
    """
    total = sum(counts)
    if total <= 0:
        return [share for share in prior]
    size = float(total) if weight is None else weight
    if alpha < 0.0:
        return [share for share in prior]
    own = size / (size + alpha) if size + alpha > 0.0 else 1.0
    return [own * count / total + (1.0 - own) * share for count, share in zip(counts, prior)]


def _pooled(groups: "list[list[int]]", cells: int) -> "list[float]":
    """The shares of all groups' counts together (nought everywhere where there is none)."""
    sums = [0] * cells
    for counts in groups:
        for k in range(cells):
            sums[k] += counts[k]
    total = sum(sums)
    return [count / total if total else 0.0 for count in sums]


def _calendar(days: "list[int]", cache: "dict[int, tuple[int, int, int]]",
              units: "list[int] | None" = None) -> "dict[str, object]":
    """The calendar of a list of days: each year's 84 shares of month by weekday, per million over all of them.

    Each month keeps its own share of the days (a trend, a season, a step). Its weekdays are its own shares
    pulled toward the whole calendar's weekday shares as far as the months' real departures from them allow
    (`_concentration`, read on the days a person holds, one person's rows of one day counted once: `units` names
    each day's person, every day its own where none is given): a month of few persons writes the calendar's
    weekdays, never the weekdays its few real persons came on.
    """
    by_year: "dict[int, list[int]]" = {}
    held: "dict[int, list[int]]" = {}
    met: "dict[tuple[int, int], int]" = {}
    for k in range(len(days)):
        day = days[k]
        year, month, _date = _civil(day, cache)
        if year not in by_year:
            by_year[year] = [0] * 84
            held[year] = [0] * 84
        cell = (month - 1) * WEEK + weekday(day)
        by_year[year][cell] += 1
        unit = (units[k], day) if units is not None else (k, day)
        if unit not in met:
            met[unit] = 1
            held[year][cell] += 1
    met = {}
    years = sorted(by_year)
    if len(years) > YEAR_CAP:
        middle = years[len(years) // 2]
        kept = [year for year in years if abs(year - middle) <= YEAR_CAP // 2][:YEAR_CAP]
        years = kept
    months_rows: "list[list[int]]" = []
    months_held: "list[list[int]]" = []
    for year in years:
        for month in range(12):
            months_rows += [by_year[year][month * WEEK: (month + 1) * WEEK]]
            months_held += [held[year][month * WEEK: (month + 1) * WEEK]]
    week_rows = _pooled(months_rows, WEEK)
    week_held = _pooled(months_held, WEEK)
    alpha = _concentration(months_held, [week_held for _ in months_held])
    flat: "list[float]" = []
    for k in range(len(months_rows)):
        size = sum(months_rows[k])
        pulled = _pulled(months_rows[k], week_rows, alpha, float(sum(months_held[k])))
        flat += [size * share for share in pulled]
    shares = _per_million_of(flat)
    return {"years": years, "cells": [shares[84 * k: 84 * (k + 1)] for k in range(len(years))]}


def _clock(days: "list[int]", ticks: "list[int]") -> "dict[str, object]":
    """Hour by weekday, minute by hour and the second, as shares, and the share of minutes on five-minute marks.

    Each weekday's hours are pulled toward the hours of its kind of day (a weekday or the weekend), and those
    toward all the hours; each hour's minutes toward the minutes of every hour (`_concentration`): a minute a
    real hour keeps apart (the 07:30 first slot) stays its own, a minute only the table's few persons happened
    to come at is drawn as the clock's minutes are. Every weekday and hour keeps its own share of the stamps.
    """
    hours = [[0] * 24 for _ in range(WEEK)]
    minutes = [[0] * 60 for _ in range(24)]
    at_second = [0] * 60
    marks = 0
    for day, tick in zip(days, ticks):
        if tick < 0:
            continue
        second = tick // TICKS
        hour = second // 3600
        minute = (second // 60) % 60
        hours[weekday(day)][hour] += 1
        minutes[hour][minute] += 1
        at_second[second % 60] += 1
        marks += 1 if minute % 5 == 0 else 0
    clocked = sum(at_second)
    kinds = [_sum_rows(hours[0:5]), _sum_rows(hours[5:7])]
    every = _pooled(kinds, 24)
    kind_alpha = _concentration(kinds, [every, every])
    kind_shares = [_pulled(kinds[0], every, kind_alpha), _pulled(kinds[1], every, kind_alpha)]
    priors = [kind_shares[0 if day < 5 else 1] for day in range(WEEK)]
    day_alpha = _concentration(hours, priors)
    hour_weights: "list[float]" = []
    for day in range(WEEK):
        size = sum(hours[day])
        hour_weights += [size * share for share in _pulled(hours[day], priors[day], day_alpha)]
    within = _pooled(minutes, 60)
    minute_alpha = _concentration(minutes, [within for _ in minutes])
    minute_weights: "list[float]" = []
    for hour in range(24):
        size = sum(minutes[hour])
        minute_weights += [size * share for share in _pulled(minutes[hour], within, minute_alpha)]
    hour_shares = _per_million_of(hour_weights)
    minute_shares = _per_million_of(minute_weights)
    return {"hour": [hour_shares[24 * k: 24 * (k + 1)] for k in range(WEEK)],
            "minute": [minute_shares[60 * k: 60 * (k + 1)] for k in range(24)],
            "second": _per_million(at_second), "marks": (marks * PER // clocked) if clocked else 0,
            "clocked": clocked}


def _sum_rows(rows: "list[list[int]]") -> "list[int]":
    """The cell-by-cell sums of rows of counts of one length."""
    sums = [0] * (len(rows[0]) if rows else 0)
    for row in rows:
        for k in range(len(sums)):
            sums[k] += row[k]
    return sums


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


def _wide(grid: "list[int]", part: int) -> bool:
    """Whether a part of a gap grid's positions (one of `LANDING_BINS`) spans a week or more of gaps."""
    step = (len(grid) - 1) // LANDING_BINS
    return grid[(part + 1) * step] - grid[part * step] >= WEEK


def _landings(sets: "list[tuple[list[int], list[int], list[int]]]", past_weeks: bool = False) -> "list[list[list[int]]]":
    """For each (gaps in days, the weekday of each gap's earlier date, the gaps' grid): where its gaps land.

    The gaps are ranked as the grid ranks them (equal gaps in the table's order, so no weekday is favoured where equal
    gaps straddle two parts), and each of the grid's `LANDING_BINS` parts of positions that spans a week or more of
    gaps (`_wide`) counts the weekday its gaps land on (the earlier date's weekday plus the gap, modulo seven), or,
    with `past_weeks` (a grid of every weekday of the date before), each gap's days past whole weeks. Every
    such part's counts, of every set, are pulled toward their pooled shares as far as the parts' real departures from
    them allow (`_concentration`), as every census of the zone is: a weekly schedule (every gap whole weeks) or a
    weekday rule (no one back on a Sunday) is kept, a part's departure no larger than chance is drawn as the pooled
    shares. Returns per million shares a part, all nought for a part narrower than a week or a grid it cannot read.
    """
    groups: "list[list[int]]" = []
    where: "list[tuple[int, int]]" = []
    out = [[[0] * WEEK for _part in range(LANDING_BINS)] for _set in sets]
    for index, (values, befores, grid) in enumerate(sets):
        last = len(values) - 1
        if last < 1 or len(grid) < 2 or (len(grid) - 1) % LANDING_BINS:
            continue
        wide = [_wide(grid, part) for part in range(LANDING_BINS)]
        if not any(wide):
            continue
        ordered = sorted(values)
        rank: "dict[int, int]" = {}
        counts = [[0] * WEEK for _part in range(LANDING_BINS)]
        for value, before in zip(values, befores):
            if value not in rank:
                rank[value] = _below(ordered, value - 1)
            place = rank[value]
            rank[value] = place + 1
            part = min(LANDING_BINS - 1, (place * LANDING_BINS) // last)
            if wide[part]:
                counts[part][(value if past_weeks else before + value) % WEEK] += 1
        del ordered, rank
        for part in range(LANDING_BINS):
            if wide[part] and sum(counts[part]) > 0:
                groups += [counts[part]]
                where += [(index, part)]
    if not groups:
        return out
    prior = _pooled(groups, WEEK)
    alpha = _concentration(groups, [prior for _group in groups])
    for counts_of, (index, part) in zip(groups, where):
        out[index][part] = _per_million_of(_pulled(counts_of, prior, alpha))
    return out


def _spread_about_pooled(groups: "list[list[int]]") -> float:
    """Pearson's statistic of groups of counts about their pooled shares (0.0 where they hold none)."""
    pooled = _pooled(groups, WEEK)
    statistic = 0.0
    for counts in groups:
        total = sum(counts)
        for count, share in zip(counts, pooled):
            if share > 0.0:
                expected = total * share
                statistic += (count - expected) * (count - expected) / expected
    return statistic


def _past_weeks_fit(values: "list[int]", befores: "list[int]") -> bool:
    """Whether a grid of every weekday of the date before keeps its gaps' days past whole weeks (True) or the weekday
    they land on (False), as the real gaps show (lane STATS-A).

    The grid is read where the date before falls on a weekday with no cell of its own, so it must say what such a
    date's next date does. A weekly schedule moves its next date with the date before (every gap whole weeks: the
    days past whole weeks the same whatever the weekday before), and a clinic open on weekdays does not (the next date
    lands on a weekday whatever the weekday before: measured on the reliability battery's cases table, the days past
    whole weeks pooled over weekday dates put 25 of 65 such gaps on a weekend where the real table put 3). So the gaps
    are counted by the weekday before, once by the weekday they land on and once by their days past whole weeks, and
    the reading whose groups spread less about their pooled shares (`_spread_about_pooled`, over the weekdays before
    holding the least rows) is kept; days past whole weeks where they tie or fewer than two such weekdays are read.
    A fixed function of the two. Raises nothing. No I/O.
    """
    landing: "dict[int, list[int]]" = {}
    past: "dict[int, list[int]]" = {}
    for value, before in zip(values, befores):
        if before not in landing:
            landing[before] = [0] * WEEK
            past[before] = [0] * WEEK
        landing[before][(before + value) % WEEK] += 1
        past[before][value % WEEK] += 1
    kept = [before for before in sorted(landing) if sum(landing[before]) >= PARENT_LEAST_ROWS]
    if len(kept) < 2:
        return True
    return _spread_about_pooled([past[before] for before in kept]) <= _spread_about_pooled(
        [landing[before] for before in kept])


def _cell_landings(values: "list[int]", levels: "list[str]", befores: "list[int]",
                   cells: "dict[str, list[int]]") -> "dict[str, list[list[int]]]":
    """The weekday the gaps of each kept cell land on (`_landings`, the cells pooled together)."""
    gaps_of: "dict[str, list[int]]" = {}
    befores_of: "dict[str, list[int]]" = {}
    for value, level, before in zip(values, levels, befores):
        if level not in cells:
            continue
        if level not in gaps_of:
            gaps_of[level] = []
            befores_of[level] = []
        gaps_of[level] += [value]
        befores_of[level] += [before]
    names = [level for level in sorted(cells) if level in gaps_of]
    found = _landings([(gaps_of[level], befores_of[level], cells[level]) for level in names])
    return {level: shares for level, shares in zip(names, found)}


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
    befores = [weekday(reference_days[row]) for row in rows]
    words = [f"{day}" for day in range(WEEK)]
    levels = [words[before] for before in befores]
    cells = _levels_grid(day_gaps, levels, CELL_GRID)
    entry["cells"] = cells
    # Where each grid's gaps land (`_landings`): a stay of months still ends on the weekdays real stays end on. The grid
    # of every reference weekday keeps its gaps' days past whole weeks; each weekday's cell the weekday they land on.
    past_weeks = _past_weeks_fit(day_gaps, befores)
    entry["landings"] = _landings([(day_gaps, befores, typing.cast("list[int]", entry["grid"]))], past_weeks)[0]
    entry["landings_by"] = LANDINGS_PAST_WEEKS if past_weeks else LANDINGS_WEEKDAY
    entry["cell_landings"] = _cell_landings(day_gaps, levels, befores, cells)
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
    # Each key with what its own cell does not show taken from the column's other cells (`_resolved_keys`).
    for found in _resolved_keys([_spelling_shown(cell, reading) for cell in sample]):
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
    first_bands: "dict[int, list[int]]" = {}
    gaps: "list[int]" = []
    day_gaps: "list[int]" = []
    previous_weekdays: "list[str]" = []
    previous_blocks: "list[str]" = []
    bands: "list[int]" = []
    # A gap's weekday and four-hour block, seven and twelve texts, each held once (lane IN-8): a pointer a gap.
    held_keys: "dict[str, str]" = {}
    clocked = True
    for key in by_person:
        ordered = sorted(by_person[key])
        first_rows += [ordered[0][1]]
        opening_band = first_band_of(len(ordered))
        if opening_band not in first_bands:
            first_bands[opening_band] = []
        first_bands[opening_band] += [ordered[0][2]]
        band = band_of(len(ordered))
        for k in range(1, len(ordered)):
            gaps += [ordered[k][0] - ordered[k - 1][0]]
            day_gaps += [ordered[k][2] - ordered[k - 1][2]]
            weekday_key = f"{weekday(ordered[k - 1][2])}"
            four_hours = time_block(ordered[k - 1][2], seconds[ordered[k - 1][1]])
            if weekday_key not in held_keys:
                held_keys[weekday_key] = weekday_key
            if four_hours not in held_keys:
                held_keys[four_hours] = four_hours
            previous_weekdays += [held_keys[weekday_key]]
            previous_blocks += [held_keys[four_hours]]
            bands += [band]
        for _moment, row, _day in ordered:
            clocked = clocked and seconds[row] >= 0
    if not gaps:
        return None
    # The persons' first dates (each person once), pulled as every calendar is, and each band's own calendar
    # of first dates where its months or weekdays depart from every person's beyond chance (`_band_calendars`):
    # a person of one date starts anywhere in the calendar while a person of many starts early; a person's first
    # order falls on another weekday where it is its only one. Where a person of a band starts inside its room is
    # kept by its place (`_places`), at a tenth of the room.
    whole = _calendar([days[row] for row in first_rows], cache)
    by_band = _band_calendars(first_bands, whole, len(first_rows), cache)
    entry: "dict[str, object]" = {"person": person, "column": column, "calendar": whole, "calendars": by_band,
                                  "clock": _clock_entry(days, seconds, first_rows, labels) if clocked else None,
                                  "places": _places(by_person, by_band, whole, days)}
    middle = sorted(gaps)[len(gaps) // 2]
    minute = clocked and middle < DAY_TICKS
    values = gaps if minute else day_gaps
    keys = previous_blocks if minute else previous_weekdays
    entry["scale"] = "minute" if minute else "day"
    entry["grid"] = _grid(values, GAP_GRID)
    # On a day scale, where each grid's gaps land (`_landings`): a weekday's cell keeps the weekday they land on (the
    # earlier date's weekday is its key), a grid of every weekday its gaps' days past whole weeks.
    befores = [] if minute else [int(key) for key in keys]
    if not minute:
        past_weeks = _past_weeks_fit(values, befores)
        entry["landings"] = _landings([(values, befores, typing.cast("list[int]", entry["grid"]))], past_weeks)[0]
        entry["landings_by"] = LANDINGS_PAST_WEEKS if past_weeks else LANDINGS_WEEKDAY
    banded: "dict[str, object]" = {}
    for band in BANDS:
        rows_of = [k for k in range(len(values)) if bands[k] == band]
        if not _kept(len(rows_of), 2 * len(values), PARENT_LEAST_ROWS) or len(rows_of) < 0.02 * len(values):
            continue
        mine = [values[k] for k in rows_of]
        levels = [keys[k] for k in rows_of]
        cells = _levels_grid(mine, levels, BAND_GRID)
        held_band: "dict[str, object]" = {"grid": _grid(mine, CELL_GRID), "cells": cells}
        if not minute:
            mine_before = [befores[k] for k in rows_of]
            band_past = _past_weeks_fit(mine, mine_before)
            held_band["landings"] = _landings([(mine, mine_before, typing.cast("list[int]", held_band["grid"]))],
                                              band_past)[0]
            held_band["landings_by"] = LANDINGS_PAST_WEEKS if band_past else LANDINGS_WEEKDAY
            held_band["cell_landings"] = _cell_landings(mine, levels, mine_before, cells)
        banded[f"{band}"] = held_band
    entry["bands"] = banded
    return entry


def _band_calendars(days_by_band: "dict[int, list[int]]", whole: "dict[str, object]", persons: int,
                    cache: "dict[int, tuple[int, int, int]]") -> "dict[str, object]":
    """Each band's calendar of first dates: every person's calendar with the band's own month and weekday shares.

    A band of a fiftieth of the persons or more (and the least rows) keeps a calendar. Its month shares are its
    persons' months pulled toward every person's months, and its weekday shares likewise, each by the band's own
    departure from every person's beyond chance (`_concentration` on the band alone): a band that starts as
    every person does writes every person's calendar, never the months and weekdays its few real persons came
    on; a band that starts late or on other weekdays keeps it. Within a month, the weekdays are every person's
    (every person's calendar's own) tilted by the band's weekday shares over every person's.
    """
    pooled = _prepared_calendar(whole)
    years = _numbers(_object(whole)["years"])
    index: "dict[tuple[int, int], int]" = {}
    for k in range(len(pooled.months)):
        index[pooled.months[k]] = k
    month_totals = [float(sum(week)) for week in pooled.weekdays]
    total = math.fsum(month_totals)
    month_prior = [share / total for share in month_totals]
    week_sums = [0.0] * WEEK
    for week in pooled.weekdays:
        for day in range(WEEK):
            week_sums[day] += week[day]
    week_prior = [share / total for share in week_sums]
    out: "dict[str, object]" = {}
    for band in sorted(days_by_band):
        days = days_by_band[band]
        if not _kept(len(days), persons, PARENT_LEAST_ROWS) or len(days) < 0.02 * persons:
            continue
        month_counts = [0] * len(pooled.months)
        week_counts = [0] * WEEK
        for day in days:
            year, month, _date = _civil(day, cache)
            if (year, month) in index:
                month_counts[index[(year, month)]] += 1
            week_counts[weekday(day)] += 1
        months = _pulled(month_counts, month_prior, _concentration([month_counts], [month_prior]))
        band_week = _pulled(week_counts, week_prior, _concentration([week_counts], [week_prior]))
        tilt = [band_week[day] / week_prior[day] if week_prior[day] > 0.0 else 0.0 for day in range(WEEK)]
        cells: "dict[int, list[float]]" = {}
        for year in years:
            cells[year] = [0.0] * 84
        for k in range(len(pooled.months)):
            year, month = pooled.months[k]
            if year not in cells:
                continue
            tilted = [pooled.weekdays[k][day] * tilt[day] for day in range(WEEK)]
            size = math.fsum(tilted)
            for day in range(WEEK):
                cells[year][(month - 1) * WEEK + day] = months[k] * tilted[day] / size if size > 0.0 else 0.0
        flat: "list[float]" = []
        for year in years:
            flat += cells[year]
        shares = _per_million_of(flat)
        out[f"{band}"] = {"years": years, "cells": [shares[84 * k: 84 * (k + 1)] for k in range(len(years))]}
    return out


def _places(by_person: "dict[str, list[tuple[int, int, int]]]", by_band: "dict[str, object]",
            whole: "dict[str, object]", days: "list[int]") -> "dict[str, object]":
    """Where the persons of two dates or more start inside the room their span leaves: shares of `PLACE_BINS` bins.

    A person's dates must end by the calendar's last month, so a person of a long span starts early: the place
    is the person's first date's position in its band's first-date calendar (every person's where its band keeps
    none) between the calendar's start (0) and the latest first date its span allows (1). Kept as shares of
    equal bins of the room, by band of the persons' numbers of dates ("all": every such person): the writer
    places a twin person evenly inside a bin drawn by its share, never at a real person's own place.
    """
    present = [day for day in days if day != _ABSENT]
    year, month, _date = parsing.civil_from_days(max(present))
    last_day = parsing.days_from_civil(year, month, _days_in(year, month))
    prepared: "dict[str, _Calendar]" = {}
    for band in by_band:
        prepared[band] = _prepared_calendar(by_band[band])
    overall = _prepared_calendar(whole)
    found: "dict[str, list[int]]" = {}
    everyone = [0] * PLACE_BINS
    persons = 0
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
        cell = min(PLACE_BINS - 1, max(0, int(place * PLACE_BINS)))
        if band not in found:
            found[band] = [0] * PLACE_BINS
        found[band][cell] += 1
        everyone[cell] += 1
        persons += 1
    out: "dict[str, object]" = {"all": _per_million(everyone)}
    for band in sorted(found):
        held = sum(found[band])
        if _kept(held, persons, PARENT_LEAST_ROWS) and held >= 0.02 * persons:
            out[band] = _per_million(found[band])
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


def _mixed_reading(cells: "list[str]", held: bool = False) -> "Reading | None":
    """The member that reads the most of a column's cells as dates where some cells do but not the column.

    Only a cell of four figures or more can be a date, and a member that reads none of its first `MIXED_TRIES`
    such cells is passed by, so a column of numbers or words costs little. The members whose cells are figures
    alone or two-figure years (`MIXED_SET_ASIDE`) are not read here: among other values, a number of eight
    figures is an amount or a code far more often than a day. At least `MIXED_LEAST` cells, and a share of the
    present ones of `MIXED_SHARE`, must read.

    ``held``: the description holds the column's dates in disguise (its block's remark,
    `taxonomy.REMARK_DATED_VALUES_HELD`, lane ZOO-Y): the product has already read those cells as dates, so every
    member is read, and a count read whole (`date_counts.counted_figures`) by the counting system its figures name
    (`HELD_COUNT_MEMBERS`): days from 1899-12-30, seconds or milliseconds from 1970. A count's epoch shifts its
    weekday by a fixed number of days, so the twin's made-up counts, written back under the same member, keep the
    real weekdays and times of day whatever epoch wrote them.
    """
    present = [cell for cell in cells if _bare(cell)]
    if held:
        counted: "dict[int, int]" = {}
        for cell in _spread_sample(present, SAMPLE):
            figures = date_counts.counted_figures(_bare(cell))
            if figures in HELD_COUNT_MEMBERS:
                counted[figures] = (counted[figures] if figures in counted else 0) + 1
        if counted:
            most = sorted((-counted[figures], figures) for figures in counted)[0]
            if -most[0] >= MIXED_LEAST:
                return Reading("count", HELD_COUNT_MEMBERS[most[1]])
    sample = [cell for cell in _spread_sample(present, SAMPLE) if _figure_count(cell) >= 4]
    if not sample:
        return None
    best, chosen = 0, ""
    for member in TEXT_MEMBERS:
        if member in MIXED_SET_ASIDE and not held:
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
                   cache: "dict[int, tuple[int, int, int]]", held: bool = False) -> "dict[str, object]":
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
        reading = _mixed_reading(cells, held)
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
        if held:
            out[name]["held"] = True  # type: ignore[index]
    return out


def _dated_cells(cells: "list[str]", reading: Reading) -> "list[str]":
    return [cell for cell in cells if _bare(cell) and moment_of(cell, reading) is not None]


@dataclasses.dataclass
class Census:
    """What the zone keeps of a table read a column at a time (`take_column`), before `zone_of` builds the zone.

    THE MEMORY (lane IN-8, plan P4-D502): a column is read once and let go.
    Kept: each date column's days and seconds, every number held once a
    value (`_shared`: a list of a row's pointers, eight bytes a row, the
    values a few thousand objects); each label column of two to ten words,
    its cells held once a word the same way; the person column's keys once
    a key; and each column's spellings and dates among other values as
    their small entries. Never a column of numbers or of free text, so the
    zone of a table of 2,000,000 rows holds about 16 bytes a row a date
    column and 8 a label column, not the table.
    """

    person: str
    declared: "dict[str, str]"
    skip: "tuple[str, ...]"
    declared_only: bool = False
    rows: int = -1
    names: "list[str]" = dataclasses.field(default_factory=list)
    read: "dict[str, Reading]" = dataclasses.field(default_factory=dict)
    days_of: "dict[str, list[int]]" = dataclasses.field(default_factory=dict)
    seconds_of: "dict[str, list[int]]" = dataclasses.field(default_factory=dict)
    spelled: "dict[str, dict[str, object]]" = dataclasses.field(default_factory=dict)
    labels: "dict[str, list[str]]" = dataclasses.field(default_factory=dict)
    mixed: "dict[str, object]" = dataclasses.field(default_factory=dict)
    keys: "list[str] | None" = None
    cache: "dict[int, tuple[int, int, int]]" = dataclasses.field(default_factory=dict)
    # The columns whose dates in disguise the description holds (lane ZOO-Y): read for them among other values with
    # every member (`_mixed_reading`'s ``held``), so the twin makes them up where the description's twin is blank.
    held: "tuple[str, ...]" = ()


def census(person: str = "", readings: "dict[str, str] | None" = None, skip: "tuple[str, ...]" = (),
           declared_only: bool = False, held: "tuple[str, ...]" = ()) -> Census:
    """An empty census: `build_zone`'s arguments but the columns, which `take_column` hands in one at a time.

    ``held`` names the columns whose dates in disguise the description holds (`Census.held`)."""
    return Census(person, dict(readings) if readings is not None else {}, tuple(skip), declared_only,
                  held=tuple(held))


def _shared_texts(cells: "list[str]") -> "list[str]":
    """The cells, each value held by one text object (a list of pointers, eight bytes a row)."""
    held: "dict[str, str]" = {}
    out: "list[str]" = []
    for cell in cells:
        text = _text(cell)
        if text not in held:
            held[text] = text
        out += [held[text]]
    return out


def _shared_numbers(values: "list[int]") -> "list[int]":
    """The whole numbers, each value held by one object (a list of pointers, eight bytes a row)."""
    held: "dict[int, int]" = {}
    out: "list[int]" = []
    for value in values:
        if value not in held:
            held[value] = value
        out += [held[value]]
    return out


def _is_label(cells: "list[str]") -> bool:
    """Whether a column holds two to ten different words: a column a date's clock or gap may depend on."""
    seen: "set[str]" = set()
    for cell in cells:
        word = _bare(cell)
        if word and word not in seen:
            seen = seen | {word}
            if len(seen) > PARENT_LEVELS:
                break
    return 2 <= len(seen) <= PARENT_LEVELS


def take_column(gathered: Census, name: str, cells: "list[str]") -> None:
    """Read one column into the census, in the table's order; nothing of it is kept but what the zone reads.

    The same reading as `build_zone`'s of the whole table: a date column
    (one member reads 95 per cent of its present cells, or the person's
    declared member; with `declared_only`, a column the readings name and
    no other) keeps its days, its times of day in ticks and its spellings;
    any other column but the person's and the skipped is a label of two to
    ten words or not, and holds dates among other values or not.
    """
    if gathered.rows < 0:
        gathered.rows = len(cells)
    gathered.names += [name]
    if name == gathered.person:
        gathered.keys = _shared_texts(cells)
        return
    if name in gathered.skip:
        return
    texts = [_text(cell) for cell in cells]
    reading: "Reading | None" = None
    if not gathered.declared_only or name in gathered.declared:
        reading = reading_of(texts, gathered.declared[name] if name in gathered.declared else "")
    if reading is not None:
        days: "list[int]" = []
        seconds: "list[int]" = []
        for cell in texts:
            found = _moment(cell, reading)
            if found is None:
                days += [_ABSENT]
                seconds += [-1]
            else:
                days += [found[0]]
                seconds += [found[1]]
        if not all(day == _ABSENT for day in days):
            gathered.read[name] = reading
            gathered.days_of[name] = _shared_numbers(days)
            gathered.seconds_of[name] = _shared_numbers(seconds)
            gathered.spelled[name] = _spellings(texts, reading)
            return
    if _is_label(cells):
        gathered.labels[name] = _shared_texts(cells)
    found_mixed = _mixed_columns({name: texts}, set(), gathered.cache, name in gathered.held)
    if name in found_mixed:
        gathered.mixed[name] = found_mixed[name]


def build_zone(columns: "dict[str, list[str]]", person: str = "", readings: "dict[str, str] | None" = None,
               skip: "tuple[str, ...]" = (), declared_only: bool = False,
               held: "tuple[str, ...]" = ()) -> "dict[str, object]":
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
    The columns are taken one at a time (`take_column`), as the profile
    hook takes them from a table read in groups, so the zone is the same
    whichever way it is built. ``held`` names the columns whose dates in
    disguise the description holds (`Census.held`, `fill_held`).
    """
    gathered = census(person, readings, skip, declared_only, held)
    for name in columns:
        take_column(gathered, name, columns[name])
    return zone_of(gathered)


def zone_of(gathered: Census) -> "dict[str, object]":
    """The dates zone of a census every column of the table was taken into (`take_column`)."""
    names = gathered.names
    rows = max(0, gathered.rows)
    person = gathered.person
    cache = gathered.cache
    read = gathered.read
    days_of = gathered.days_of
    seconds_of = gathered.seconds_of
    labels = gathered.labels
    columns: "dict[str, list[str]]" = {person: gathered.keys} if gathered.keys is not None else {}
    # Each row's person (a number a person), so a calendar reads a person's rows of one day as one day held.
    owners: "list[int] | None" = None
    if person and gathered.keys is not None:
        codes: "dict[str, int]" = {}
        owners = []
        for cell in gathered.keys:
            key = _bare(cell)
            if key not in codes:
                codes[key] = len(codes)
            owners += [codes[key]]
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
                                      "calendar": _calendar([days[row] for row in present], cache,
                                                            [owners[row] for row in present] if owners else None),
                                      "clock": _clock_entry(days, seconds, present, {} if minute_chain else labels)
                                      if any(seconds[row] >= 0 for row in present) else None,
                                      "spellings": gathered.spelled[name],
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
            "orders": orders, "timeline": timeline, "mixed": gathered.mixed}


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


def _spread_positions(rows: "list[int]", state: "list[int]") -> "dict[int, float]":
    """Positions in (0, 1) for rows drawn alike: one in each of as many equal parts of (0, 1) as there are rows, the
    parts dealt to the rows in an order the stream shuffles, each position drawn evenly inside its part.

    Each row's month then comes back in its calendar share to within a row, so a twin's monthly counts carry the
    table's own spread about a trend and not a second spread drawn on top of it (a month drawn row by row from
    shares that already hold the table's counts left a twin's monthly admissions noisier than the table's: a step's
    standard error a third too wide). Which day and minute of the month a row takes stays drawn.
    """
    count = len(rows)
    order = list(range(count))
    for k in range(count - 1, 0, -1):
        other = min(k, int(_uniform(state) * (k + 1)))
        order[k], order[other] = order[other], order[k]
    out: "dict[int, float]" = {}
    for k in range(count):
        out[rows[k]] = (order[k] + _uniform(state)) / count
    return out


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
    if minute % 5 == 0:
        # Off the mark by one or two minutes, earlier or later, each as likely: no minute between two marks
        # takes what the mark gives up (always one later made the minute after a mark twice as common).
        minute += (1, 2, -1, -2)[min(3, int(_uniform(state) * 4))]
    return minute * 60 * TICKS


def _anchored(column: _Column, u: float, row: int, given: "dict[str, list[str]]", state: "list[int]",
              cache: "dict[tuple[int, ...], list[float]]") -> "tuple[int, int]":
    day = made_up_day(column.calendar, u, cache)
    clock = _clock_for(column, given, row)
    return day, (_second_of(clock, day, state, column.fractions) if clock is not None else -1)


@dataclasses.dataclass(frozen=True)
class _Gaps:
    """A quantile function of gaps and its cells (by a label column's level, or by a weekday), and on a day scale
    where each one's gaps land (`_landings`, as cumulative shares a part of the weekday landed on; for the grid of
    every weekday one such list for each weekday of the date before; empty where the zone keeps none)."""

    grid: "list[int]"
    cells: "dict[str, list[int]]"
    landings: "list[list[list[int]]]"
    cell_landings: "dict[str, list[list[int]]]"


def _landing_parts(value: object) -> "list[list[int]]":
    parts = _rows(value)
    if len(parts) != LANDING_BINS or [part for part in parts if len(part) != WEEK]:
        raise DatesError("The dates zone is damaged: the weekdays a grid's gaps land on are not seven a part.")
    return parts


def _prepared_landings(value: object) -> "list[list[int]]":
    """A weekday cell's landing shares as cumulative shares a part (`_landings`); a zone written before them keeps none."""
    if value is None:
        return []
    return [_cumulative(part) for part in _landing_parts(value)]


def _prepared_every_weekday(value: object, landings_by: object) -> "list[list[list[int]]]":
    """A grid of every weekday's shares, for each weekday of the date before, as cumulative shares a part of the
    weekday landed on: its days past whole weeks turned (`_prepared_past_weeks`), or the weekday they land on, the
    same whatever the weekday before (`_past_weeks_fit` chose; none given: days past whole weeks)."""
    if landings_by is None or landings_by == LANDINGS_PAST_WEEKS:
        return _prepared_past_weeks(value)
    if landings_by != LANDINGS_WEEKDAY:
        raise DatesError("The dates zone is damaged: a grid's landings are of no reading the writer knows.")
    if value is None:
        return []
    shares = _prepared_landings(value)
    return [shares for _before in range(WEEK)]


def _prepared_past_weeks(value: object) -> "list[list[list[int]]]":
    """A grid of every weekday's shares of days past whole weeks, as the cumulative shares of the weekday landed on
    for each weekday of the date before (that weekday plus the days); none for a zone written before them."""
    if value is None:
        return []
    parts = _landing_parts(value)
    return [[_cumulative([part[(day - before) % WEEK] for day in range(WEEK)]) for part in parts]
            for before in range(WEEK)]


def _prepared_gaps(grid: object, cells: object, landings: object = None, cell_landings: object = None,
                   landings_by: object = None) -> _Gaps:
    held = _object(cells)
    out: "dict[str, list[int]]" = {}
    for key in held:
        out[key] = _numbers(held[key])
    by_cell: "dict[str, list[list[int]]]" = {}
    if cell_landings is not None:
        found = _object(cell_landings)
        for key in found:
            by_cell[key] = _prepared_landings(found[key])
    return _Gaps(_numbers(grid), out, _prepared_every_weekday(landings, landings_by), by_cell)


def _gaps_at(gaps: _Gaps, key: str) -> "list[int]":
    if key and key in gaps.cells:
        return gaps.cells[key]
    return gaps.grid


def _landings_at(gaps: _Gaps, key: str, before: int) -> "list[list[int]]":
    """The landing shares of the grid `_gaps_at` gives for `key`, for a date before on weekday `before` (empty where
    the zone keeps none for it)."""
    if key and key in gaps.cells:
        return gaps.cell_landings[key] if key in gaps.cell_landings else []
    return gaps.landings[before] if gaps.landings else []


def _landed(grid: "list[int]", landings: "list[list[int]]", u: float, before: int) -> int:
    """A day-scale gap at position `u` of its grid, landing on a weekday of its part's real gaps (`_landings`).

    The grid's nearest point is the gap (`_quantile`). Where the grid keeps landing shares and the part of positions
    `u` falls in spans a week or more, the gap moves by at most three days, inside that part's span, to land on a
    weekday drawn from the part's shares: the draw reads where `u` falls between the grid's two neighbouring points
    (no draw of the stream is spent, so every other date of the twin stays as it was). A part narrower than a week, or
    a grid with no shares, keeps the grid's gap. `before` is the weekday of the date the gap is added to.
    """
    points = len(grid)
    index = min(points - 1, max(0, int(u * (points - 1) + 0.5)))
    gap = grid[index]
    if len(landings) != LANDING_BINS or points < 2 or (points - 1) % LANDING_BINS:
        return gap
    part = min(LANDING_BINS - 1, max(0, int(u * LANDING_BINS)))
    shares = landings[part]
    step = (points - 1) // LANDING_BINS
    low, high = grid[part * step], grid[(part + 1) * step]
    if high - low < WEEK or shares[WEEK - 1] <= 0:
        return gap
    # Where `u` falls inside the piece of its grid point's reach that lies in its part, read as a position in (0, 1):
    # a point on the line between two parts (or at an end) reaches into each only in part, and each piece draws the
    # whole of its part's shares (measured: reading the whole reach left a cell's weekday counts up to 8 of 270 off).
    low_reach = max((index - 0.5) / (points - 1), part / LANDING_BINS, 0.0)
    high_reach = min((index + 0.5) / (points - 1), (part + 1) / LANDING_BINS, 1.0)
    inside = (u - low_reach) / (high_reach - low_reach) if high_reach > low_reach else 0.5
    landing = _pick(shares, min(max(inside, 0.0), 1.0))
    move = (landing - before - gap) % WEEK
    if move > WEEK // 2:
        move -= WEEK
    found = gap + move
    if found < low:
        found += WEEK
    elif found > high:
        found -= WEEK
    return found


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
    landings = found["landings"] if "landings" in found and not minute else None
    cell_landings = found["cell_landings"] if "cell_landings" in found and not minute else None
    landings_by = found["landings_by"] if "landings_by" in found and not minute else None
    return _Chain(_word(found["reference"]), minute, found["ordered"] is True, day_ordered,
                  _word(found["by"]) if minute else "",
                  _prepared_gaps(found["grid"], found["cells"], landings, cell_landings, landings_by),
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
    key = f"{weekday(reference_day)}"
    before = weekday(reference_day)
    day = reference_day + _landed(_gaps_at(chain.gaps, key), _landings_at(chain.gaps, key, before), u, before)
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
    landings: "list[list[list[int]]]"


def _prepared_line(timeline: "dict[str, object]", column: _Column) -> _Line:
    first = dataclasses.replace(column, calendar=_prepared_calendar(timeline["calendar"]))
    first_clock, first_by, first_levels = _clocks(timeline["clock"])
    if first_clock is not None:
        first = dataclasses.replace(first, clock=first_clock, clock_by=first_by, clock_levels=first_levels)
    minute = timeline["scale"] == "minute"
    held = _object(timeline["bands"])
    bands: "dict[int, _Gaps]" = {}
    for band in BANDS:
        if f"{band}" in held:
            found = _object(held[f"{band}"])
            landings = found["landings"] if "landings" in found and not minute else None
            cell_landings = found["cell_landings"] if "cell_landings" in found and not minute else None
            landings_by = found["landings_by"] if "landings_by" in found and not minute else None
            bands[band] = _prepared_gaps(found["grid"], found["cells"], landings, cell_landings, landings_by)
    calendars = _object(timeline["calendars"])
    firsts: "dict[int, _Calendar]" = {}
    for band in FIRST_BANDS:
        if f"{band}" in calendars:
            firsts[band] = _prepared_calendar(calendars[f"{band}"])
    held_places = _object(timeline["places"])
    places: "dict[str, list[int]]" = {}
    for key in held_places:
        shares = _numbers(held_places[key])
        if len(shares) != PLACE_BINS:
            raise DatesError("The dates zone is damaged: a share of the persons' places is missing.")
        places[key] = shares
    overall_by = timeline["landings_by"] if "landings_by" in timeline and not minute else None
    overall = (_prepared_every_weekday(timeline["landings"], overall_by) if "landings" in timeline and not minute
               else [])
    return _Line(column.name, minute, first, firsts, _numbers(timeline["grid"]), bands, places, overall)


def _first_calendar(line: _Line, dates: int) -> _Calendar:
    """The calendar of the first dates of the persons of the band of `dates` dates, else of every person."""
    band = first_band_of(dates)
    if band in line.firsts:
        return line.firsts[band]
    return line.first.calendar


def _band_gaps(line: _Line, dates: int, weekday_key: str, before: int = -1) -> "tuple[list[int], list[list[int]]]":
    """The gaps of the band of a person's number of dates (by the weekday of the date before, on a day scale), with
    where they land for a date before on weekday `before` (`_landings`; empty where the zone keeps none, or on a
    minute scale, `before` below nought)."""
    chosen = 0
    for band in BANDS:
        if dates >= band and band in line.bands:
            chosen = band
    if not chosen:
        return line.overall, (line.landings[before] if line.landings and before >= 0 else [])
    gaps = line.bands[chosen]
    return _gaps_at(gaps, weekday_key), (_landings_at(gaps, weekday_key, before) if before >= 0 else [])


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
            moment = begin + _quantile(_band_gaps(line, len(members), time_block(last_day, last_second))[0], u)
            if column.minute_only:
                moment = _heaped((moment // (60 * TICKS)) * (60 * TICKS), _clock_for(column, given, row),
                                 column.clock, state)
            moment = max(moment, begin)
            day = moment // DAY_TICKS
            moments += [(day, moment - day * DAY_TICKS)]
            continue
        grid, landings = _band_gaps(line, len(members), f"{weekday(last_day)}", weekday(last_day))
        day = last_day + max(0, _landed(grid, landings, u, weekday(last_day)))
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
            state: "list[int]", cache: "dict[tuple[int, ...], list[float]]") -> int:
    """The whole weeks a person's dates move by to start at a place inside its room drawn from its band's shares.

    The bin by its share (`u`), the place evenly inside the bin: a tenth of the room is far wider than any
    person's dates, so a twin person starts where the persons of its band start, never where one of them did.
    """
    band = f"{first_band_of(dates)}"
    shares = line.places[band] if band in line.places else (line.places["all"] if "all" in line.places else [])
    latest = last_day - (end - first_day)
    if dates < 2 or not shares or sum(shares) <= 0 or latest <= calendar.first_day:
        return 0
    low = _position_of(calendar, calendar.first_day)
    high = _position_of(calendar, latest)
    place = (_pick(_cumulative(shares), u) + _uniform(state)) / len(shares)
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
                        _position(positions, members[0], state), state, cache)
        if end - shift > column.calendar.last_day:
            latest = column.calendar.last_day - (end - first_day)
            if latest >= opening.calendar.first_day:
                wanted = made_up_day(opening.calendar, _uniform(state) * _position_of(opening.calendar, latest), cache)
                wanted = min(wanted, latest)
                shift = WEEK * ((first_day - wanted + WEEK - 1) // WEEK)
            else:
                shift = max(0, WEEK * ((first_day - column.calendar.first_day) // WEEK))
        # ...and every date of the person inside the column's real months: the whole weeks above round a first date
        # placed near the first month a few days before it (batch 4z: 6 dates on the cases table, 1 on the accounts
        # table), so the move nearest them that keeps the person inside is taken (`_move_within`).
        inside_move = _move_within(column.calendar.first_day - first_day, column.calendar.last_day - end, -shift)
        if inside_move is not None:
            shift = -inside_move
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


# THE WIDTH A MADE-UP DATE IS WRITTEN WITH (the Windows bundle workflow's trial). A spelling's width word is read
# off one cell (`spelling_of`), and it says only what that cell's fields could show: a field of ten or more shows no
# width, so `7/29/2021` is counted `first-field-unpadded`, and `10/10/2020` under no word at all. Dealt to a made-up
# date whose day is below ten, the field the word never decided took `parsing.pair_widths`' padded default, so a
# column every real cell of which writes `m/d/yyyy` was written `7/03/2021` on 1,460 twin cells of 20,000, a
# convention neither the table nor the description's twin holds, and validate missed the column's width census (its
# one published word and the unnamed remainder). `_width_written` writes each made-up date with a word the
# column's own cells showing the same fields are written with (`_width_pools`).
WIDTH_BOTH = "both"
WIDTH_FIRST = "first"
WIDTH_SECOND = "second"


def _width_kind(word: object) -> str:
    """Which fields a width word decides: `WIDTH_BOTH` for a joint word, `WIDTH_FIRST` or `WIDTH_SECOND` for a
    one-field word, '' for anything else (a cell that showed no width)."""
    if word in parsing.FIELD_WIDTH_STYLES_BOTH:
        return WIDTH_BOTH
    if word in parsing.FIELD_WIDTH_STYLES_FIRST:
        return WIDTH_FIRST
    if word in parsing.FIELD_WIDTH_STYLES_SECOND:
        return WIDTH_SECOND
    return ""


def _width_pools(keys: "list[list[object]]", weighted: bool) -> "dict[str, dict[str, int]]":
    """The width words a column's cells are written with, by the fields each shows: for `WIDTH_BOTH` the joint words
    of the cells whose two fields show a width, for `WIDTH_FIRST` and `WIDTH_SECOND` the one-field words of the cells
    where only that field does, each with its weight (the key's share where `weighted`, one a key otherwise: the
    description's twin's keys, one a cell). A key whose width is no word of the census is passed over.

    Raises DatesError where a key's width is not text (a damaged zone, as `_word`); no I/O.
    """
    pools: "dict[str, dict[str, int]]" = {WIDTH_BOTH: {}, WIDTH_FIRST: {}, WIDTH_SECOND: {}}
    for key in keys:
        if not isinstance(key, list) or len(key) < 1:
            continue
        word = _word(key[0])
        kind = _width_kind(word)
        if not kind:
            continue
        weight = 1
        if weighted:
            weight = key[6] if len(key) > 6 and isinstance(key[6], int) and not isinstance(key[6], bool) else 0
        pool = pools[kind]
        pool[word] = (pool[word] if word in pool else 0) + weight
    return pools


def _width_agrees(candidate: str, kind: str, decided: str, padded: "tuple[bool, bool]") -> bool:
    """Whether a candidate word of the pool `kind` pads each field the dealt word decided (`decided`, its kind) and
    the made-up date shows as that word pads it."""
    first, second = parsing.pair_widths(candidate)
    if kind == WIDTH_FIRST:
        return decided not in (WIDTH_BOTH, WIDTH_FIRST) or (candidate == parsing.WIDTH_FIRST_FIELD_PADDED) == padded[0]
    if kind == WIDTH_SECOND:
        return decided not in (WIDTH_BOTH, WIDTH_SECOND) or (candidate == parsing.WIDTH_SECOND_FIELD_PADDED) == padded[1]
    if decided in (WIDTH_BOTH, WIDTH_FIRST) and first != padded[0]:
        return False
    return not (decided in (WIDTH_BOTH, WIDTH_SECOND) and second != padded[1])


def _width_written(word: str, fallback: str, month: int, date: int, member: str,
                   pools: "dict[str, dict[str, int]] | None", state: "list[int] | None" = None) -> str:
    """The width word a made-up date of `member` is written with, `word` being the dealt spelling's ('' where its
    cell showed none) and `fallback` the column's (`_widths`).

    `word` (else `fallback`) where every field this date shows is a field `word` decided and comes out as the
    column's cells showing the same fields write it, or where no such cell is known (`pools`, `_width_pools`).
    Otherwise -- a shown field `word` never decided, which `parsing.pair_widths` would write padded, or a decided one
    no such cell writes -- one of the words of those cells that pad every field `word` decided as `word` does (all of
    them where none does), drawn from `state` in proportion to their weights, so a column written both ways keeps
    its share of each on the cells showing the same fields; with no `state`, the heaviest (ties to the first in
    sorted order). A one-field word chosen is given as the joint word that pads its field so (the other field is ten
    or more there and shows nothing). Only the members with two numeric fields of either width are resolved.

    Raises nothing; no I/O; deterministic (a function of its arguments and the stream's state, which it advances
    only where it draws among two words or more).
    """
    given = word or fallback
    if pools is None or member not in parsing.VARIABLE_WIDTH_MEMBERS:
        return given
    values = (month, date) if member in parsing.MONTH_FIRST_MEMBERS else (date, month)
    shows = (values[0] < 10, values[1] < 10)
    if not shows[0] and not shows[1]:
        return given
    padded = parsing.pair_widths(given)
    decided = _width_kind(word)
    covered = decided == WIDTH_BOTH
    if shows[0] and shows[1]:
        kind, written = WIDTH_BOTH, parsing.joint_width(padded[0], padded[1])
    elif shows[0]:
        kind, written = WIDTH_FIRST, parsing.field_width_word(1, padded[0])
        covered = covered or decided == WIDTH_FIRST
    else:
        kind, written = WIDTH_SECOND, parsing.field_width_word(2, padded[1])
        covered = covered or decided == WIDTH_SECOND
    pool = pools[kind] if kind in pools else {}
    if not pool or (covered and written in pool):
        return given
    candidates: "list[str]" = []
    for agreeing in (True, False):
        for candidate in sorted(pool):
            if pool[candidate] > 0 and (not agreeing or _width_agrees(candidate, kind, decided, padded)):
                candidates += [candidate]
        if candidates:
            break
    if not candidates:
        return given
    chosen = candidates[0]
    if len(candidates) > 1 and state is not None:
        chosen = candidates[_pick(_cumulative([pool[candidate] for candidate in candidates]), _uniform(state))]
    elif len(candidates) > 1:
        for candidate in candidates:
            if pool[candidate] > pool[chosen]:
                chosen = candidate
    return chosen if kind == WIDTH_BOTH else parsing.width_of_field_word(chosen)


def _spelled_text(day: int, tick: int, member: str, key: "list[object]", fallback: str,
                  pools: "dict[str, dict[str, int]] | None" = None, state: "list[int] | None" = None) -> str:
    """A moment (an instant) written in one of the column's spellings: moved into the spelling's offset, its clock at
    the spelling's step and its fraction of a second the moment's own, to the spelling's figures (cut, never rounded,
    so two moments in order are written in order); its fields at the width `_width_written` gives where `pools` (the
    column's widths, `_width_pools`) is given, its draws from `state` (the column's own width stream)."""
    width, style, mark, form, figures, offset = key[0], key[1], key[2], key[3], key[4], key[5]
    written_offset = _word(offset)
    shift = _offset_seconds(written_offset) if tick >= 0 else 0
    if shift:
        moved = day * DAY_TICKS + tick + shift * TICKS
        day, tick = moved // DAY_TICKS, moved % DAY_TICKS
    year, month, date = parsing.civil_from_days(day)
    width = _width_written(_word(width), fallback, month, date, member, pools, state)
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


_WEEK = 7
_WEEKS_AT_MOST = 600
_DAYS_NEAR = 62
_FAR = 1 << 40


# EVERY TWIN DATE IN ITS COLUMN'S REAL MONTHS (lane IN-5, batch 4zz): a date column's calendar holds the months the
# real column held dates in, from its first month's first day to its last month's last day, and no twin date lies
# outside them. Measured on batch 4z's line, the moves that hold the description's twin's months moved whole persons
# by weeks with no regard to the calendar's ends: the Windows bundle's visits table 12 visit dates of 11 persons up to
# 44 days before the real first month, the battery's cases table 42 dates up to 212 days outside, its accounts table
# 10 dates up to 1,308 days past the real last month (persons moved far to fill a short month, their later dates
# carried past the end); and a person's first date placed by whole weeks a few days before the first month (6 dates
# on the cases table, 1 on the accounts table). Each move now stays inside the room its dates leave
# (`_room_of`, `_move_within`), and a last pass (`_kept_inside`) brings any date still outside in with its person or
# its row's chain, so every gap and order within them stands.


def _rooms(entries: "dict[str, object]", names: "list[str]") -> "dict[str, tuple[int, int]]":
    """Each column's real months as its first and last day (its calendar's first month's first day, its last month's
    last day): the days a twin date of that column may take."""
    out: "dict[str, tuple[int, int]]" = {}
    for name in names:
        calendar = _prepared_calendar(_object(entries[name])["calendar"])
        out[name] = (calendar.first_day, calendar.last_day)
    return out


def _room_of(moments: "dict[str, tuple[list[int], list[int]]]", names: "list[str]",
             rooms: "dict[str, tuple[int, int]]", rows: "list[int]") -> "tuple[int, int]":
    """The moves, in days (the least and the most), that keep every date of `rows` in each of the columns `names`
    inside its column's real months (`rooms`); (-_FAR, _FAR) where the rows hold no date. The least above the most
    where no single move does (dates spread wider than their months)."""
    low, high = -_FAR, _FAR
    for name in names:
        if name not in moments or name not in rooms:
            continue
        first, last = rooms[name]
        own = moments[name][0]
        for row in rows:
            day = own[row]
            if day == _ABSENT:
                continue
            if first - day > low:
                low = first - day
            if last - day < high:
                high = last - day
    return low, high


def _move_within(low: int, high: int, wanted: int = 0) -> "int | None":
    """The move nearest `wanted` between `low` and `high` (days): `wanted` itself, else whole weeks from it (every
    weekday and clock kept), else, where no whole week fits, the nearest day that does (the weekday given up for
    those dates alone). None where no move fits at all."""
    if low > high:
        return None
    if low <= wanted <= high:
        return wanted
    if wanted < low:
        weeks = wanted + _WEEK * ((low - wanted + _WEEK - 1) // _WEEK)
        return weeks if weeks <= high else low
    weeks = wanted - _WEEK * ((wanted - high + _WEEK - 1) // _WEEK)
    return weeks if weeks >= low else high


def _chains_of(entries: "dict[str, object]", order: "list[str]") -> "tuple[list[str], dict[str, list[str]]]":
    """The columns heading their own chain, in the zone's order, and each column's chained columns."""
    children: "dict[str, list[str]]" = {}
    heads: "list[str]" = []
    for name in order:
        link = _prepared_chain(_object(entries[name])["chain"])
        if link is None:
            heads += [name]
        elif link.reference in children:
            children[link.reference] += [name]
        else:
            children[link.reference] = [name]
    return heads, children


def _kept_inside(entries: "dict[str, object]", order: "list[str]", timeline_column: str,
                 moments: "dict[str, tuple[list[int], list[int]]]", groups: "list[list[int]] | None") -> int:
    """Every twin date brought inside its column's real months, the dates that move together moved together.

    The dates that move together are a person's dates of the timeline
    column and of every column chained to it (`groups`), else one row's
    dates of a column heading its own chain and of the columns chained to
    it. Where any of them lies outside its column's months, all of them
    move by the whole weeks nearest nought that bring every one inside
    (the nearest days where no whole week fits: `_move_within`), so each
    gap, order and clock among them stands. Dates spread wider than their
    months (no move fits) are each put at their own column's nearest end.
    Returns how many dates were moved or put so; a fixed function of its
    inputs; no I/O.
    """
    rooms = _rooms(entries, order)
    heads, children = _chains_of(entries, order)
    changed = 0
    for name in heads:
        if name not in moments:
            continue
        names = [name] + _descendants(name, children)
        # Only the rows holding a date outside are read row by row: a column whose different days all lie inside
        # its months (the set of them, held once a value) is passed whole.
        outside: "set[int]" = set()
        for each in names:
            if each not in moments:
                continue
            first, last = rooms[each]
            own_days = moments[each][0]
            different = set(own_days) - {_ABSENT}
            if not different or (min(different) >= first and max(different) <= last):
                continue
            outside |= {row for row in range(len(own_days))
                        if own_days[row] != _ABSENT and not first <= own_days[row] <= last}
            del different
        if not outside:
            continue
        units = ([group for group in groups if [row for row in group if row in outside]]
                 if name == timeline_column and groups is not None else [[row] for row in sorted(outside)])
        for unit in units:
            low, high = _room_of(moments, names, rooms, unit)
            if low <= 0 <= high:
                continue
            move = _move_within(low, high)
            for each in names:
                if each not in moments:
                    continue
                first, last = rooms[each]
                own_days = moments[each][0]
                for row in unit:
                    day = own_days[row]
                    if day == _ABSENT:
                        continue
                    placed = day + move if move is not None else min(max(day, first), last)
                    if placed != day:
                        own_days[row] = placed
                        changed += 1
    return changed


def _month_key(day: int, cache: "dict[int, tuple[int, int, int]]") -> int:
    year, month, _date = _civil(day, cache)
    return year * 12 + month - 1


def _rule_of(given: "list[str]", member: str) -> "offset_rules.Rule | None":
    """The daylight-saving rule the description's twin's stamps of a column follow (`offset_rules.rule_of`), or None."""
    pairs: "list[tuple[str, str]]" = []
    for cell in given:
        if not _bare(cell):
            continue
        found = parsing.parse_datetime(_bare(cell), member)
        if found is not None:
            pairs += [(found[0], found[1])]
    if not pairs:
        return None
    return offset_rules.parsed_rule(offset_rules.rule_of(pairs))


def _summer(day: int, tick: int, rule: "offset_rules.Rule | None") -> int:
    """1 where the rule puts its summer offset in force at the instant (`day`, `tick` from 1970 UTC), else 0."""
    if rule is None:
        return 0
    instant = day * DAY + (tick // TICKS if tick >= 0 else 0)
    return 1 if offset_rules.offset_at(rule, instant) != rule.standard else 0


def _bin(day: int, tick: int, rule: "offset_rules.Rule | None", cache: "dict[int, tuple[int, int, int]]") -> int:
    """A date's month, and, where the column follows an offset rule, the part of the month it falls in: before the
    rule's change in that month or after it (two bins a month, in the order of the calendar)."""
    if rule is None:
        return _month_key(day, cache) * 2
    _year, _month, date = _civil(day, cache)
    phase = 1 if _summer(day, tick, rule) != _summer(day - (date - 1), 0, rule) else 0
    return _month_key(day, cache) * 2 + phase


def _months_held(days: "list[int]", seconds: "list[int]", targets: "list[int]",
                 cache: "dict[int, tuple[int, int, int]]", rule: "offset_rules.Rule | None" = None,
                 chained: "tuple[dict[str, tuple[list[int], list[int]]], list[str], dict[str, tuple[int, int]]] | None"
                 = None) -> "list[int]":
    """Each row's move, in whole weeks, that gives a column's dates exactly the months of `targets` (one month a date
    of the description's twin), the earliest date the earliest month; nought where a date stays or is absent.

    A move of whole weeks keeps each date's weekday and clock and changes
    only its day of the month (made up in any case) and, where its month
    differs from the month its rank asks for, its month: the date lands on
    one of that month's days of its weekday, chosen by a fixed hash of the
    row, as the dates zone makes up a day (so no date piles at a month's
    first or last week); where no whole week reaches its bin (a part of a
    month before or after an offset rule's change, fewer than seven days),
    the nearest day in it, its clock kept. `chained`, where given (the
    moments, the column and the columns chained to it, and their real
    months), bounds a row's moves to those that keep each of its dates
    inside its own column's real months (`_room_of`): a move outside them
    is never taken (the row then keeps its date where no landing fits).
    """
    moves = [0 for _row in range(len(days))]
    ordered = sorted((days[row], seconds[row], row) for row in range(len(days)) if days[row] != _ABSENT)
    count = len(ordered)
    wanted = sorted(targets)
    if not count or not wanted:
        return moves
    for rank in range(count):
        day, second, row = ordered[rank]
        goal = wanted[min(len(wanted) - 1, (rank * len(wanted)) // count)]
        own = _bin(day, second, rule, cache)
        if own == goal:
            continue
        step = _WEEK if goal > own else -_WEEK
        moved = day
        landing: "list[int]" = []
        for _week in range(_WEEKS_AT_MOST):
            moved += step
            here = _bin(moved, second, rule, cache)
            if here == goal:
                landing += [moved - day]
            elif landing or (here // 2 > goal // 2 if step > 0 else here // 2 < goal // 2):
                break
        low, high = _room_of(chained[0], chained[1], chained[2], [row]) if chained is not None else (-_FAR, _FAR)
        landing = [move for move in landing if low <= move <= high]
        if landing:
            moves[row] = landing[_mixed((row << 4) + len(landing)) % len(landing)]
            continue
        # A part of a month no whole week reaches (the days before an offset rule's change in a month, fewer than
        # seven): the nearest day that is in it, its clock kept and its weekday given up.
        for distance in range(1, _DAYS_NEAR + 1):
            ahead = distance * (1 if step > 0 else -1)
            if low <= ahead <= high and _bin(day + ahead, second, rule, cache) == goal:
                moves[row] = ahead
                break
            if low <= -ahead <= high and _bin(day - ahead, second, rule, cache) == goal:
                moves[row] = -ahead
                break
    return moves


_PERSON_WEEKS = (1, 2, 3, 4, 6, 9, 13, 20, 26)
_PERSON_PASSES = 6


def _gap_after(surplus: "dict[int, int]", leaving: "list[int]", arriving: "list[int]") -> int:
    """How much the summed distance from the target months changes when dates leave and arrive at these months."""
    change: "dict[int, int]" = {}
    for month in leaving:
        change[month] = (change[month] if month in change else 0) - 1
    for month in arriving:
        change[month] = (change[month] if month in change else 0) + 1
    total = 0
    for month in change:
        before = surplus[month] if month in surplus else 0
        total += abs(before + change[month]) - abs(before)
    return total


def _persons_months_held(days: "list[int]", groups: "list[list[int]]", targets: "list[int]",
                         cache: "dict[int, tuple[int, int, int]]", seconds: "list[int] | None" = None,
                         rule: "offset_rules.Rule | None" = None,
                         rooms: "list[tuple[int, int]] | None" = None) -> "list[int]":
    """Each row's move, in whole weeks and the same for every row of a person, that brings a person timeline's months
    to `targets` (one month a date of the description's twin): passes in which each person takes the move among
    `_PERSON_WEEKS` (weeks, earlier or later) that most closes the distance, then persons of one date moved from a
    month that holds too many to one that holds too few. Every weekday, clock and gap within a person stands.

    `rooms`, where given, names each person's moves (the least and the most, in days) that keep every one of its
    dates, of the timeline and of each column chained to it, inside its column's real months: a person starting
    outside them is first moved inside (`_move_within`), and no later move leaves them (lane IN-5, batch 4zz).
    """
    moves = [0 for _row in range(len(days))]
    allowed = rooms if rooms is not None and len(rooms) == len(groups) else [(-_FAR, _FAR)] * len(groups)
    shift = [0 for _group in groups]
    for at in range(len(groups)):
        inside_move = _move_within(allowed[at][0], allowed[at][1])
        if inside_move is not None:
            shift[at] = inside_move
    surplus: "dict[int, int]" = {}
    for month in targets:
        surplus[month] = (surplus[month] if month in surplus else 0) - 1
    dated: "list[list[int]]" = []
    for at, rows in enumerate(groups):
        mine = [row for row in rows if days[row] != _ABSENT]
        dated += [mine]
        for row in mine:
            month = _bin(days[row] + shift[at], _tick_of(seconds, row), rule, cache)
            surplus[month] = (surplus[month] if month in surplus else 0) + 1
    for _pass in range(_PERSON_PASSES):
        improved = False
        for at in range(len(groups)):
            mine = dated[at]
            if not mine:
                continue
            low, high = allowed[at]
            now = [_bin(days[row] + shift[at], _tick_of(seconds, row), rule, cache) for row in mine]
            best, chosen = 0, 0
            tried: "set[int]" = set()
            for weeks in _PERSON_WEEKS:
                for sign in (1, -1):
                    step = sign * weeks * _WEEK
                    if not low <= shift[at] + step <= high:
                        # ...a move past the room's end tried as the furthest whole weeks that stay inside it.
                        step = (((high - shift[at]) // _WEEK) if sign > 0 else -((shift[at] - low) // _WEEK)) * _WEEK
                    if step * sign <= 0 or step in tried:
                        continue
                    tried = tried | {step}
                    then = [_bin(days[row] + shift[at] + step, _tick_of(seconds, row), rule, cache) for row in mine]
                    change = _gap_after(surplus, now, then)
                    if change < best:
                        best, chosen = change, step
            if chosen:
                for month in now:
                    surplus[month] -= 1
                for row in mine:
                    month = _bin(days[row] + shift[at] + chosen, _tick_of(seconds, row), rule, cache)
                    surplus[month] = (surplus[month] if month in surplus else 0) + 1
                shift[at] += chosen
                improved = True
        if not improved:
            break
    # A person holding a date in a month of too many may move far: its first date into a month of too few, where
    # that closes the distance (the months short at the calendar's ends are reached so).
    for _pass in range(_PERSON_PASSES):
        short = sorted(month for month in surplus if surplus[month] < 0)
        if not short:
            break
        improved = False
        for at in range(len(groups)):
            mine = dated[at]
            if not mine:
                continue
            now = [_bin(days[row] + shift[at], _tick_of(seconds, row), rule, cache) for row in mine]
            if not [month for month in now if surplus[month] > 0]:
                continue
            first = days[mine[0]] + shift[at]
            low, high = allowed[at]
            best, chosen = 0, 0
            for goal in short:
                if surplus[goal] >= 0:
                    continue
                step = _week_into(first, goal, cache, _tick_of(seconds, mine[0]), rule)
                # ...never so far that a later date of the person passes its real months (batch 4z: 1,308 days).
                if not step or not low <= shift[at] + step <= high:
                    continue
                then = [_bin(days[row] + shift[at] + step, _tick_of(seconds, row), rule, cache) for row in mine]
                change = _gap_after(surplus, now, then)
                if change < best:
                    best, chosen = change, step
            if chosen:
                for month in now:
                    surplus[month] -= 1
                for row in mine:
                    month = _bin(days[row] + shift[at] + chosen, _tick_of(seconds, row), rule, cache)
                    surplus[month] = (surplus[month] if month in surplus else 0) + 1
                shift[at] += chosen
                improved = True
        if not improved:
            break
    for at in range(len(groups)):
        mine = dated[at]
        if len(mine) != 1:
            continue
        month = _bin(days[mine[0]] + shift[at], _tick_of(seconds, mine[0]), rule, cache)
        if surplus[month] <= 0:
            continue
        goal = -1
        for each in surplus:
            if surplus[each] < 0 and (goal < 0 or abs(each - month) < abs(goal - month)):
                goal = each
        if goal < 0:
            break
        step = _WEEK if goal > month else -_WEEK
        moved = shift[at]
        low, high = allowed[at]
        for _week in range(_WEEKS_AT_MOST):
            moved += step
            if not low <= moved <= high:
                break
            if _bin(days[mine[0]] + moved, _tick_of(seconds, mine[0]), rule, cache) == goal:
                surplus[month] -= 1
                surplus[goal] += 1
                shift[at] = moved
                break
    for at in range(len(groups)):
        for row in groups[at]:
            moves[row] = shift[at]
    return moves


def _week_into(day: int, goal: int, cache: "dict[int, tuple[int, int, int]]", tick: int = -1,
               rule: "offset_rules.Rule | None" = None) -> int:
    """The nearest move in whole weeks that brings `day` into the bin `goal` (its month, and its rule's season where
    one stands: `_bin`), 0 where it is there or none is."""
    own = _bin(day, tick, rule, cache)
    if own == goal:
        return 0
    step = _WEEK if goal > own else -_WEEK
    moved = 0
    for _week in range(_WEEKS_AT_MOST):
        moved += step
        if _bin(day + moved, tick, rule, cache) == goal:
            return moved
    return 0


def _tick_of(seconds: "list[int] | None", row: int) -> int:
    """A row's clock (its ticks), or -1 where none is read."""
    return seconds[row] if seconds is not None else -1


def _descendants(name: str, children: "dict[str, list[str]]") -> "list[str]":
    """The columns chained to `name`, and to them, in turn."""
    out: "list[str]" = []
    for child in children[name] if name in children else []:
        out += [child] + _descendants(child, children)
    return out


def _held_months(entries: "dict[str, object]", order: "list[str]", timeline_column: str,
                 moments: "dict[str, tuple[list[int], list[int]]]", months: "dict[str, list[str]]",
                 cache: "dict[int, tuple[int, int, int]]", groups: "list[list[int]] | None" = None) -> None:
    """Every date column that heads its own chain moved by whole weeks so its months hold the months of the
    description's twin's cells (`months`): row by row, exactly (`_months_held`); a person's timeline (`groups`, each
    person's rows) person by person (`_persons_months_held`). Each column chained to it moves with it, row by row,
    so every gap stands (lane IN-2b). No move takes a date of the column, or of a column chained to it, outside
    its own column's real months (`_room_of`; lane IN-5, batch 4zz)."""
    heads, children = _chains_of(entries, order)
    rooms = _rooms(entries, order)
    for name in heads:
        if name not in months or name not in moments or (name == timeline_column and groups is None):
            continue
        entry = _object(entries[name])
        reading_entry = _object(entry["reading"])
        reading = Reading(_word(reading_entry["kind"]), _word(reading_entry["member"]))
        rule = _rule_of(months[name], reading.member) if reading.kind == "text" else None
        bins: "list[int]" = []
        for cell in months[name]:
            if _bare(cell):
                found = _moment(cell, reading)
                if found is not None:
                    bins += [_bin(found[0], found[1], rule, cache)]
        days, seconds = moments[name]
        names = [name] + _descendants(name, children)
        if name == timeline_column and groups is not None:
            allowed = [_room_of(moments, names, rooms, group) for group in groups]
            moves = _persons_months_held(days, groups, bins, cache, seconds, rule, allowed)
            del allowed
            _moved(moments, names, moves)
            continue
        # ...row by row: its months exactly, and, where it follows an offset rule, the dates in each season of it.
        moves = _months_held(days, seconds, bins, cache, rule, (moments, names, rooms))
        _moved(moments, names, moves)


def _moved(moments: "dict[str, tuple[list[int], list[int]]]", names: "list[str]", moves: "list[int]") -> None:
    """Each named column's dates moved row by row (a row's absent date stays absent)."""
    for each in names:
        if each not in moments:
            continue
        own_days = moments[each][0]
        for row in range(len(own_days)):
            if moves[row] and own_days[row] != _ABSENT:
                own_days[row] += moves[row]


def write_dates(zone: "dict[str, object]", rows: int, people: "list[str] | None" = None,
                given: "dict[str, list[str]] | None" = None, scores: "dict[str, list[float]] | None" = None,
                present: "dict[str, list[bool]] | None" = None, seed: int = 0,
                months: "dict[str, list[str]] | None" = None) -> "dict[str, list[str]]":
    """The twin's cells of every date column of the zone (the hook the generate step calls).

    `rows` is the twin's number of rows; `people` its person column's cells
    (each person's rows in the order they are written); `given` the twin's
    cells of the label columns the zone's clocks and gaps depend on;
    `scores` one number a row and date column that ties the date to the
    twin's other columns (a latent score of the generate step: only its
    order within the rows the zone draws alike is read; `_cell_positions`);
    `present` the rows of a column that hold a date; `months` the
    description's twin's cells of a column, whose months a column heading
    its own chain then holds exactly (`_held_months`: whole weeks, so the
    weekday and the clock stand, and the columns chained to it move with
    it). Every ordering the real table never breaks between two date
    columns of a row holds in the twin (`orders`). Same zone and seed, same
    cells.
    """
    entries, order, moments = _date_moments(zone, rows, people, given, scores, present, seed, months)
    out: "dict[str, list[str]]" = {}
    for name in order:
        out[name] = _spelled_column(entries, name, moments[name], rows, seed,
                                    months[name] if months is not None and name in months else None)
    return out


def write_dates_held(zone: "dict[str, object]", rows: int, people: "list[str] | None" = None,
                     given: "dict[str, list[str]] | None" = None, scores: "dict[str, list[float]] | None" = None,
                     present: "dict[str, list[bool]] | None" = None, seed: int = 0,
                     months: "dict[str, list[str]] | None" = None) -> "dict[str, twinstore.HeldColumn]":
    """`write_dates`' cells, each column held compactly as soon as it is spelled (lane IN-8, plan P4-D502).

    The same cells (`twinstore.column_cells` gives them back): what is held
    beside the columns' days and seconds is one column's text at a time,
    never every date column's at once. `months` as `write_dates` reads it.
    """
    entries, order, moments = _date_moments(zone, rows, people, given, scores, present, seed, months)
    out: "dict[str, twinstore.HeldColumn]" = {}
    for name in order:
        out[name] = twinstore.held_column(_spelled_column(entries, name, moments[name], rows, seed,
                                                          months[name] if months is not None and name in months
                                                          else None))
    return out


def _date_moments(zone: "dict[str, object]", rows: int, people: "list[str] | None",
                  given: "dict[str, list[str]] | None", scores: "dict[str, list[float]] | None",
                  present: "dict[str, list[bool]] | None", seed: int,
                  months: "dict[str, list[str]] | None" = None,
                  ) -> "tuple[dict[str, object], list[str], dict[str, tuple[list[int], list[int]]]]":
    """Every date column's days and seconds a row, the orderings held: `write_dates`' moments before they are spelled.

    Each column's days and seconds are held once a value (`_shared_numbers`:
    a list of pointers, eight bytes a row) as soon as the column is made.
    """
    found = _object(zone)
    _versioned(found)
    entries = _object(found["columns"])
    order = [_word(name) for name in typing.cast("list[object]", found["order"])]
    timeline = found["timeline"]
    held = given if given is not None else {}
    tied = scores if scores is not None else {}
    holds: "dict[str, list[bool]]" = {}
    if present is not None:
        for name in present:
            holds[name] = present[name]
    # Where the description's twin's cells of a column are given (`months`), the column holds a date on exactly the
    # rows those cells hold one, read as the zone reads the column (lane IN-2b): a blank or another word there is
    # written back as that twin writes it, so its missing-value spellings stand too.
    readings: "dict[str, Reading]" = {}
    for name in order:
        reading_entry = _object(_object(entries[name])["reading"])
        readings[name] = Reading(_word(reading_entry["kind"]), _word(reading_entry["member"]))
        if months is not None and name in months and len(months[name]) == rows:
            holds[name] = [bool(_bare(cell)) and moment_of(cell, readings[name]) is not None for cell in months[name]]
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
        moments[name] = (_shared_numbers(days), _shared_numbers(seconds))
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
            if not positions:
                positions = _spread_positions(dated, state)
            for row in dated:
                day, second = _anchored(column, _position(positions, row, state), row, held, state, cache)
                days[row] = day
                seconds[row] = second
        moments[name] = (_shared_numbers(days), _shared_numbers(seconds))
        del days, seconds, dated, keys
    line_column = ""
    groups: "list[list[int]] | None" = None
    if isinstance(timeline, dict) and people is not None:
        line_column = _word(typing.cast("dict[str, object]", timeline)["column"])
        members: "dict[str, list[int]]" = {}
        for row in range(rows):
            key = _bare(people[row]) if row < len(people) else ""
            if key in members:
                members[key] += [row]
            else:
                members[key] = [row]
        groups = [members[key] for key in members]
        del members
    if months is not None:
        cache_days: "dict[int, tuple[int, int, int]]" = {}
        _held_months(entries, order, line_column, moments, months, cache_days, groups)
    _ordered(found, moments)
    # Every date in its column's real months (lane IN-5, batch 4zz): what the draw or an ordering still leaves
    # outside moves in with its person or its row's chain, and the orderings are held again over what moved.
    if _kept_inside(entries, order, line_column, moments, groups):
        _ordered(found, moments)
    return entries, order, moments


def _spelled_column(entries: "dict[str, object]", name: str, moment: "tuple[list[int], list[int]]", rows: int,
                    seed: int, given: "list[str] | None" = None) -> "list[str]":
    """One date column's twin cells, spelled from its days and seconds by the zone's census of spellings.

    `given`, the description's twin's cells of the column (lane IN-2b): its
    dates' spellings are dealt by the rank of the instants (`_keys_dealt`),
    and a row that holds no date writes that twin's cell back (its blanks
    and missing-value spellings).
    """
    entry = _object(entries[name])
    reading = _object(entry["reading"])
    member = _word(reading["member"])
    spellings = _object(entry["spellings"])
    state = _stream(seed, name, "spelling")
    days, seconds = moment
    twin_cells = given if given is not None and len(given) == rows else None
    cells: "list[str]" = []
    if reading["kind"] == "count":
        form = _object(spellings["count"])
        for row in range(rows):
            cells += ["" if days[row] == _ABSENT else _spelled_count(days[row], seconds[row], member, form, state)]
    else:
        spelled = typing.cast("list[list[object]]", spellings["text"])
        weights = _cumulative([int(typing.cast("int", item[6])) for item in spelled])
        fallback = _widths(spelled)
        given_keys = (_keys_dealt(days, seconds, twin_cells, Reading(_word(reading["kind"]), member))
                      if twin_cells is not None else {})
        # Each made-up date's fields at the widths the description's twin writes the same fields with, or, where no
        # twin cells are given, the zone's own census of spellings (`_width_written`), drawn from a stream of their own.
        pools = _width_pools([given_keys[row] for row in given_keys], False) if given_keys else _width_pools(spelled, True)
        widths = _stream(seed, name, "widths")
        for row in range(rows):
            if days[row] == _ABSENT or not spelled:
                cells += [""]
                continue
            if row in given_keys:
                chosen = given_keys[row]
            else:
                chosen = spelled[_pick(weights, _uniform(state))] if weights[len(weights) - 1] > 0 else spelled[0]
            cells += [_spelled_text(days[row], seconds[row], member, chosen, fallback, pools, widths)]
    if twin_cells is not None:
        cells = [twin_cells[row] if cells[row] == "" and days[row] == _ABSENT else cells[row] for row in range(rows)]
    return cells


def _keys_dealt(days: "list[int]", seconds: "list[int]", given: "list[str]",
                reading: Reading) -> "dict[int, list[object]]":
    """Each dated row's spelling (`spelling_of`): the spellings of the description's twin's dates (`given`), dealt by
    the rank of the instants, the earliest spelling to the earliest date, so every written form that twin holds
    (offsets, marks, clock forms, fractions of a second, month-name styles) stands in count, and a spelling that
    follows the calendar (an offset of the season) stays near its season. A spelling that cannot be read is left to
    the zone's own draw."""
    found: "list[tuple[int, int, int, list[object] | None]]" = []
    shown: "list[tuple[list[object] | None, str]]" = []
    for row in range(len(given)):
        cell = given[row]
        if not _bare(cell):
            continue
        moment = _moment(cell, reading)
        if moment is None:
            continue
        shown += [_spelling_shown(cell, reading)]
        found += [(moment[0], moment[1], row, None)]
    # Each key with what its own cell does not show taken from the column's other cells (`_resolved_keys`): a key
    # dealt to another moment writes that moment's hour and month as the column writes them.
    resolved = _resolved_keys(shown)
    del shown
    found = [(day, second, row, resolved[at]) for at, (day, second, row, _none) in enumerate(found)]
    del resolved
    ranked = sorted((day, second, row) for day, second, row, _key in found)
    keys_of: "dict[int, list[object] | None]" = {}
    for _day, _second, row, key in found:
        keys_of[row] = key
    dated = sorted((days[row], seconds[row], row) for row in range(len(days)) if days[row] != _ABSENT)
    out: "dict[int, list[object]]" = {}
    if len(dated) != len(ranked):
        return out
    for at in range(len(dated)):
        key = keys_of[ranked[at][2]]
        if key is not None:
            out[dated[at][2]] = key
    rule = _rule_of(given, reading.member) if reading.kind == "text" else None
    if rule is not None:
        _offsets_in_force(out, days, seconds, rule)
    return out


def _offsets_in_force(keys: "dict[int, list[object]]", days: "list[int]", seconds: "list[int]",
                      rule: "offset_rules.Rule") -> None:
    """Each dealt spelling's offset made the one the column's rule puts in force on its date: two rows each holding
    the other's season's offset exchange spellings (the counts stand), and a row left holding the wrong one takes the
    one in force, written as the column writes it."""
    written: "dict[int, str]" = {}
    for row in keys:
        offset = _word(keys[row][5])
        found = offset_rules.offset_seconds(offset) if offset else None
        if found is not None:
            written[found] = offset
    summer_rows: "list[int]" = []
    winter_rows: "list[int]" = []
    for row in sorted(keys):
        offset = _word(keys[row][5])
        found = offset_rules.offset_seconds(offset) if offset else None
        if found is None:
            continue
        wanted = rule.standard + 3600 * _summer(days[row], seconds[row], rule)
        if found == wanted:
            continue
        if wanted == rule.standard:
            winter_rows += [row]
        else:
            summer_rows += [row]
    pairs = min(len(summer_rows), len(winter_rows))
    for at in range(pairs):
        first, second = summer_rows[at], winter_rows[at]
        keys[first], keys[second] = keys[second], keys[first]
    for row in summer_rows[pairs:] + winter_rows[pairs:]:
        wanted = rule.standard + 3600 * _summer(days[row], seconds[row], rule)
        key = keys[row]
        offset = written[wanted] if wanted in written else offset_rules.offset_text(wanted)
        keys[row] = [key[0], key[1], key[2], key[3], key[4], offset]


def outside_the_real_months(zone: "dict[str, object]", name: str, cells: "list[str]") -> "int | None":
    """How many of a made-up date column's twin cells read as dates outside the months the real column held dates in.

    THE OWNER'S RULING OF 2026-11-22 ON A DRAWN TWIN'S DATES (batch 4z's fix
    round): validate may excuse what the made-up day of the month moves --
    the day-level ladder, tails and counts -- but not a date outside the
    real column's span. The record's calendar holds the real column's
    months (`_prepared_calendar`: its first month's first day to its last
    month's last day); a twin cell that reads as a date under the column's
    own reading (`moment_of`) on a day outside them is counted. None where
    the zone holds no such column. Guarantees: a fixed function of the
    three; raises `DatesError` for a damaged zone; no I/O.
    """
    found = _object(zone)
    _versioned(found)
    entries = _object(found["columns"]) if "columns" in found else {}
    if name not in entries:
        return None
    entry = _object(entries[name])
    reading_entry = _object(entry["reading"])
    reading = Reading(_word(reading_entry["kind"]), _word(reading_entry["member"]))
    calendar = _prepared_calendar(entry["calendar"])
    outside = 0
    for cell in cells:
        text = _text(cell)
        if not _bare(text):
            continue
        moment = moment_of(text, reading)
        if moment is not None and not calendar.first_day <= moment[0] <= calendar.last_day:
            outside = outside + 1
    return outside


def held_columns(zone: "dict[str, object]") -> "tuple[str, ...]":
    """The columns the zone's `mixed` part holds for dates the description held (`fill_held`), in name order."""
    found = _object(zone)
    mixed = _object(found["mixed"]) if "mixed" in found else {}
    found_held: "list[str]" = []
    for name in mixed:
        entry = _object(mixed[name])
        if "held" in entry and entry["held"] is True:
            found_held += [_word(name)]
    return tuple(sorted(found_held))


def fill_held(zone: "dict[str, object]", name: str, cells: "list[str]", seed: int = 0) -> "list[str] | None":
    """A held column's twin cells with made-up dates written on the rows its real dates stood on (lane ZOO-Y).

    THE OWNER'S RULING OF 2026-11-18 REACHES A COLUMN THE DESCRIPTION
    BLANKS. Where the description holds a column's dates in disguise (the
    Safe Harbor question about them open or answered `yes`, plan P4-D446),
    its twin writes those cells blank, and the dates zone wrote a date only
    where that twin holds one: a column of Excel days answered `yes` came
    back 20,000 blank, a column of ISO dates beside two impossible
    placeholders left unanswered 98 per cent blank. The zone's `mixed` part
    counts such a column's dates (``dates``) and keeps their calendar, clock
    and spellings, so here as many of the twin's blank cells as the real
    column held dates -- chosen evenly at random among them, all of them
    where there are fewer -- each take a made-up date: the calendar's year,
    month and weekday, the clock, the day of the month made up, in one of the
    column's own spellings (a count in its own places). Every other cell
    (its placeholders, its other values) is kept as it is. No real day finer
    than the year is written: the day of the month is made up, as for every
    date the zone writes. AND NO YEAR AT OR BEFORE THE YEAR CUT (batch 4z's
    fix round; the outside review's item 3): a date the calendar draws in a
    year that would show an age of 90 or more in this release's reference
    year (`taxonomy.year_cutoff` of `taxonomy.SAFE_HARBOR_REFERENCE_YEAR`,
    1937) is not written, and its cell stays blank as the description
    wrote it -- measured before this on a column of birth dates beside a
    placeholder, five of them in 1930: six twin dates in 1930. Every other
    cell is the same as before, the draws taken in the same order.

    Returns None where the zone holds no such column. Determinism: a fixed
    function of the zone, the cells and the seed. Raises `DatesError` for a
    damaged zone; no I/O.
    """
    found = _object(zone)
    _versioned(found)
    mixed = _object(found["mixed"]) if "mixed" in found else {}
    if name not in mixed:
        return None
    entry = _object(mixed[name])
    if "held" not in entry or entry["held"] is not True:
        return None
    reading_entry = _object(entry["reading"])
    reading = Reading(_word(reading_entry["kind"]), _word(reading_entry["member"]))
    wanted = entry["dates"] if "dates" in entry else 0
    if isinstance(wanted, bool) or not isinstance(wanted, int) or wanted < 1:
        return None
    blank = [row for row in range(len(cells)) if not _bare(_text(cells[row]))]
    if not blank:
        return None
    state = _stream(seed, name, "held")
    chosen_rows: "list[int]" = []
    need = min(wanted, len(blank))
    for at in range(len(blank)):
        # Selection sampling: each blank row is taken with the chance the rows still wanted leave it.
        if (len(blank) - at) * _uniform(state) < need - len(chosen_rows):
            chosen_rows += [blank[at]]
    column = _prepared_column(name, entry)
    spellings = _object(entry["spellings"])
    cache: "dict[tuple[int, ...], list[float]]" = {}
    out = [_text(cell) for cell in cells]
    from synthtwin import taxonomy

    cut = taxonomy.year_cutoff(taxonomy.SAFE_HARBOR_REFERENCE_YEAR)
    civil: "dict[int, tuple[int, int, int]]" = {}
    if reading.kind == "count":
        form = _object(spellings["count"])
        for row in chosen_rows:
            day, second = _anchored(column, _uniform(state), row, {}, state, cache)
            written = _spelled_count(day, second, reading.member, form, state)
            if _civil(day, civil)[0] > cut:
                out[row] = written
        return out
    spelled = typing.cast("list[list[object]]", spellings["text"])
    weights = _cumulative([int(typing.cast("int", item[6])) for item in spelled])
    if not spelled or weights[len(weights) - 1] <= 0:
        return None
    fallback = _widths(spelled)
    pools = _width_pools(spelled, True)
    widths = _stream(seed, name, "held widths")
    for row in chosen_rows:
        day, second = _anchored(column, _uniform(state), row, {}, state, cache)
        key = spelled[_pick(weights, _uniform(state))]
        written = _spelled_text(day, second, reading.member, key, fallback, pools, widths)
        if _civil(day, civil)[0] > cut:
            out[row] = written
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
    pools = _width_pools(spelled, True)
    widths = _stream(seed, name, "mixed widths")
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
        out += [_spelled_text(day, second, reading.member, chosen, fallback, pools, widths)]
    return out


# -- THE TIES (lane STATS-B): a chained gap placed by the other columns of its row ---------------------------------
#
# WHAT IT CARRIES. A chain keeps its gap's quantile function by the levels of one label column (a duration by
# service), and nothing else of the row: on the battery's cases table an operation's minutes followed the service
# alone, so a regression of the duration on the case's class and urgency, a recovery time's rank correlation with
# the duration and a logistic of a critical-care stay on the hours all read nothing (0 of 9 runs each). The TIE of a
# chain is a linear fit, on the protected computer, of the gap's NORMAL SCORE WITHIN ITS CELL (the rows the zone
# draws alike: one level of its label, or one weekday of its reference) on the other modelled columns of the row --
# a number's normal score on its quantile points and whether it is a number, a label's levels -- each term entering
# only where its z reaches `TIE_GATE_Z` (the two-sided 0.001 level, as the relations zone screens its blocks), at most
# `TIE_TERMS_MOST` of them, fitted on at most `TIE_ROWS` rows spread over the table. It is a model, never data: its
# terms, coefficients and residual spread, a number's `TIE_GRID` quantile points (the relations zone's own), a
# label's level spellings (the relations zone's own).
#
# HOW THE TWIN READS IT (`tied_again`, the last step of the generate step, after every other zone): each tied
# chain's gaps on the twin are DEALT AGAIN within each cell, the cell's own gaps (the twin's, so each cell's
# quantile function stands exactly) to its rows in the order of a score, the fit's prediction from the twin's own
# cells of the row plus a residual of the fit's spread; the column is its reference plus its gap; a column chained
# to a moved one moves with it (its own gap kept); a row where an ordering the real table never breaks would break
# keeps every date it had. Nothing else of the twin moves.

TIE_ROWS = 8000
TIE_GATE_Z = 3.290527
TIE_TERMS_MOST = 12
TIE_LEVELS_MOST = 30
TIE_LEAST_ROWS = 400
TIE_LEAST_CELLS = 40
TIE_GRID = 201
TIE_CANDIDATES_MOST = 48
_TIE_SCORE = "score"
_TIE_PRESENT = "present"
_TIE_LEVEL = "level"


@dataclasses.dataclass
class TieSource:
    """One column a chain's tie may read: its name, its kind ("number" or "label"), its cells on `tie_rows`' rows, a
    number's quantile points (the relations zone's grid) and a label's levels, commonest first (the relations zone's)."""

    name: str
    kind: str
    cells: "list[str]"
    grid: "list[float]"
    levels: "list[str]"
    # Its place in the table's order: a chain's dependents are the columns after its own.
    place: int = -1


def tie_rows(rows: int) -> "list[int]":
    """The rows a chain's tie is fitted on: every row up to `TIE_ROWS`, else `TIE_ROWS` rows spread evenly."""
    if rows <= TIE_ROWS:
        return list(range(rows))
    return [(k * rows) // TIE_ROWS for k in range(TIE_ROWS)]


def tie_grid(grid: "list[float]") -> "list[float]":
    """`TIE_GRID` points of a quantile function of more points (its ends kept)."""
    if len(grid) <= TIE_GRID:
        return [float(value) for value in grid]
    last = len(grid) - 1
    return [float(grid[(k * last) // (TIE_GRID - 1)]) for k in range(TIE_GRID)]


def _plain_value(cell: object) -> "float | None":
    """A cell's number where the whole cell is one plain finite number, else None."""
    bare = _bare(cell)
    if not bare:
        return None
    try:
        value = float(bare)
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def _grid_share(grid: "list[float]", value: float) -> float:
    """Where `value` stands on a quantile function's points, as a share in (0, 1): the middle of the points equal to
    it, else read between the two points around it; a value past an end at that end, held half a point inside."""
    count = len(grid)
    low, high = 0, count
    while low < high:
        middle = (low + high) // 2
        if grid[middle] < value:
            low = middle + 1
        else:
            high = middle
    first = low
    low, high = first, count
    while low < high:
        middle = (low + high) // 2
        if grid[middle] <= value:
            low = middle + 1
        else:
            high = middle
    after = low
    last = count - 1
    if after > first:
        place = (first + after - 1) / 2.0
    elif first == 0:
        place = 0.0
    elif first >= count:
        place = float(last)
    else:
        below, above = grid[first - 1], grid[first]
        place = (first - 1) + ((value - below) / (above - below) if above > below else 0.5)
    share = place / last if last > 0 else 0.5
    edge = 0.5 / count
    return min(max(share, edge), 1.0 - edge)


def _tie_value(term: "list[object]", cell: object) -> float:
    """One term of a tie at one cell: a label level's indicator, a number's presence, or a number's normal score."""
    kind = _word(term[1])
    if kind == _TIE_LEVEL:
        return 1.0 if _bare(cell) == _word(term[2]) else 0.0
    value = _plain_value(cell)
    if kind == _TIE_PRESENT:
        return 1.0 if value is not None else 0.0
    if value is None:
        return 0.0
    grid = [float(typing.cast(float, point)) for point in typing.cast("list[object]", term[2])]
    return chain_walk.normal_score(_grid_share(grid, value))


def _cell_scores(values: "list[int]", keys: "list[str]") -> "list[float]":
    """Each value's normal score among the values of its own key (mid-ranks for ties)."""
    by_key: "dict[str, list[tuple[int, int]]]" = {}
    for at in range(len(values)):
        key = keys[at]
        if key not in by_key:
            by_key[key] = []
        by_key[key] += [(values[at], at)]
    out = [0.0 for _value in values]
    for key in by_key:
        ordered = sorted(by_key[key])
        count = len(ordered)
        start = 0
        while start < count:
            end = start
            while end + 1 < count and ordered[end + 1][0] == ordered[start][0]:
                end += 1
            score = chain_walk.normal_score((start + end + 1) / (2.0 * count))
            for at in range(start, end + 1):
                out[ordered[at][1]] = score
            start = end + 1
    return out


def _cholesky_solved(matrix: "list[list[float]]", right: "list[float]") -> "tuple[list[float], list[list[float]]] | None":
    """The solution of `matrix x = right` and the inverse of `matrix` by Cholesky, or None where it is not positive."""
    size = len(matrix)
    lower = [[0.0 for _j in range(size)] for _i in range(size)]
    for i in range(size):
        for j in range(i + 1):
            total = matrix[i][j]
            for k in range(j):
                total -= lower[i][k] * lower[j][k]
            if i == j:
                if total <= 1e-9 * max(1.0, matrix[i][i]):
                    return None
                lower[i][i] = math.sqrt(total)
            else:
                lower[i][j] = total / lower[j][j]
    inverse = [[0.0 for _j in range(size)] for _i in range(size)]
    for column in range(size):
        unit = [1.0 if row == column else 0.0 for row in range(size)]
        forward = [0.0 for _k in range(size)]
        for i in range(size):
            total = unit[i]
            for k in range(i):
                total -= lower[i][k] * forward[k]
            forward[i] = total / lower[i][i]
        back = [0.0 for _k in range(size)]
        for i in range(size - 1, -1, -1):
            total = forward[i]
            for k in range(i + 1, size):
                total -= lower[k][i] * back[k]
            back[i] = total / lower[i][i]
        for row in range(size):
            inverse[row][column] = back[row]
    solution = [math.fsum([inverse[i][k] * right[k] for k in range(size)]) for i in range(size)]
    return solution, inverse


def _tie_fit(gram: "list[list[float]]", cross: "list[float]", total: float, rows: int,
             chosen: "list[int]") -> "tuple[list[float], list[float], float] | None":
    """Least squares on the Gram matrix's terms `chosen` (the intercept first): coefficients, their z and the residual spread."""
    matrix = [[gram[i][j] for j in chosen] for i in chosen]
    right = [cross[i] for i in chosen]
    solved = _cholesky_solved(matrix, right)
    if solved is None or rows <= len(chosen) + 1:
        return None
    beta, inverse = solved
    explained = math.fsum([beta[k] * right[k] for k in range(len(chosen))])
    variance = max(total - explained, 0.0) / (rows - len(chosen))
    zs = []
    for k in range(len(chosen)):
        spread = math.sqrt(max(variance * inverse[k][k], 0.0))
        zs += [beta[k] / spread if spread > 0.0 else 0.0]
    return beta, zs, math.sqrt(variance)


def _candidate_terms(sources: "list[TieSource]", picked: "list[int]", skip: "set[str]") -> "list[list[object]]":
    """The terms a tie may read: each number's score (and its presence where both states hold enough rows), each label
    level but the commonest that holds enough of the picked rows and not all of them."""
    terms: "list[list[object]]" = []
    for source in sources:
        if source.name in skip:
            continue
        cells = [source.cells[at] for at in picked]
        if source.kind == "number":
            if len(source.grid) < 3:
                continue
            present = sum(1 for cell in cells if _plain_value(cell) is not None)
            if present >= TIE_LEAST_CELLS:
                terms += [[source.name, _TIE_SCORE, list(source.grid)]]
            if TIE_LEAST_CELLS <= present <= len(cells) - TIE_LEAST_CELLS:
                terms += [[source.name, _TIE_PRESENT]]
        else:
            counts: "dict[str, int]" = {}
            for cell in cells:
                bare = _bare(cell)
                counts[bare] = (counts[bare] if bare in counts else 0) + 1
            for level in source.levels[1:TIE_LEVELS_MOST]:
                held = counts[_bare(level)] if _bare(level) in counts else 0
                if TIE_LEAST_CELLS <= held <= len(cells) - TIE_LEAST_CELLS:
                    terms += [[source.name, _TIE_LEVEL, _bare(level)]]
    return terms


def _chain_gap(days: "list[int]", ticks: "list[int]", reference_days: "list[int]", reference_ticks: "list[int]",
               row: int) -> "int | None":
    """A row's gap from its reference: in ticks where both cells write a clock, else in days; None where either is absent."""
    if days[row] == _ABSENT or reference_days[row] == _ABSENT:
        return None
    if ticks[row] >= 0 and reference_ticks[row] >= 0:
        return _instant(days[row], ticks[row]) - _instant(reference_days[row], reference_ticks[row])
    return days[row] - reference_days[row]


_GAP_VALUE = "gap value"
_GAP_SCORE = "gap score"
_LOGISTIC_ROUNDS = 25


def _selected(values: "list[list[float]]", response: "list[float]", forced: "list[int]") -> "list[int] | None":
    """The terms a forward selection keeps (the intercept, row 0 of `values`, always): each step the candidate of the
    largest |z| while it reaches `TIE_GATE_Z`, at most `TIE_TERMS_MOST`; None where the intercept alone cannot be fitted.
    `forced` are the candidates at least one of which must enter for the selection to stand (else None)."""
    size = len(values)
    gram = [[0.0 for _j in range(size)] for _i in range(size)]
    for i in range(size):
        for j in range(i + 1):
            gram[i][j] = gram[j][i] = math.fsum([a * b for a, b in zip(values[i], values[j])])
    cross = [math.fsum([a * b for a, b in zip(values[i], response)]) for i in range(size)]
    total = math.fsum([value * value for value in response])
    rows = len(response)
    chosen = [0]
    if _tie_fit(gram, cross, total, rows, chosen) is None:
        return None
    while len(chosen) <= TIE_TERMS_MOST:
        best: "tuple[float, int] | None" = None
        for candidate in range(1, size):
            if candidate in chosen:
                continue
            trial = _tie_fit(gram, cross, total, rows, chosen + [candidate])
            if trial is None:
                continue
            strength = abs(trial[1][len(chosen)])
            if strength >= TIE_GATE_Z and (best is None or strength > best[0]):
                best = (strength, candidate)
        if best is None:
            break
        chosen += [best[1]]
    if forced and not [at for at in chosen if at in forced]:
        return None
    return chosen


def _logistic_fit(columns: "list[list[float]]", outcome: "list[float]") -> "list[float] | None":
    """Logistic regression by iteratively reweighted least squares (row 0 of `columns` the intercept); None where it
    does not settle in `_LOGISTIC_ROUNDS` rounds or a step cannot be solved."""
    size = len(columns)
    rows = len(outcome)
    share = math.fsum(outcome) / rows
    if share <= 0.0 or share >= 1.0:
        return None
    beta = [0.0 for _k in range(size)]
    beta[0] = chain_walk.natural_log(share / (1.0 - share))
    for _round in range(_LOGISTIC_ROUNDS):
        eta = [math.fsum([beta[k] * columns[k][row] for k in range(size)]) for row in range(rows)]
        weights: "list[float]" = []
        working: "list[float]" = []
        for row in range(rows):
            bounded = min(max(eta[row], -30.0), 30.0)
            chance = 1.0 / (1.0 + chain_walk.exponential(-bounded))
            weight = max(chance * (1.0 - chance), 1e-9)
            weights += [weight]
            working += [eta[row] + (outcome[row] - chance) / weight]
        matrix = [[math.fsum([columns[i][row] * columns[j][row] * weights[row] for row in range(rows)])
                   for j in range(size)] for i in range(size)]
        right = [math.fsum([columns[i][row] * weights[row] * working[row] for row in range(rows)]) for i in range(size)]
        solved = _cholesky_solved(matrix, right)
        if solved is None:
            return None
        change = max(abs(solved[0][k] - beta[k]) for k in range(size))
        beta = solved[0]
        if change < 1e-8:
            return beta
    return beta


def _gap_terms(gaps: "list[int]", keys: "list[str]", mean: float, spread: float) -> "tuple[list[float], list[float]]":
    """A chain's two gap terms a dependent reads: the gap standardized by the real table's mean and spread, and its
    normal score within its cell (among the rows it is read on)."""
    values = [(gap - mean) / spread for gap in gaps]
    return values, _cell_scores(gaps, keys)


def _dependent_response(source: TieSource, cells: "list[str]") -> "tuple[list[int], list[float]] | None":
    """A dependent's rows and response on them: a two-level label's rows holding either level (1.0 its second level),
    a number's rows holding a number (its normal score on its quantile points); None for any other column."""
    rows: "list[int]" = []
    response: "list[float]" = []
    if source.kind == "number":
        if len(source.grid) < 3:
            return None
        for at in range(len(cells)):
            value = _plain_value(cells[at])
            if value is not None:
                rows += [at]
                response += [chain_walk.normal_score(_grid_share(source.grid, value))]
        return rows, response
    if len(source.levels) != 2:
        return None
    first, second = _bare(source.levels[0]), _bare(source.levels[1])
    for at in range(len(cells)):
        bare = _bare(cells[at])
        if bare == first or bare == second:
            rows += [at]
            response += [1.0 if bare == second else 0.0]
    return rows, response


def _dependents_of(sources: "list[TieSource]", picked: "list[int]", gaps: "list[int]", keys: "list[str]",
                   skip: "set[str]", after: int, by: str) -> "list[dict[str, object]]":
    """Each modelled column the chain's gap places (lane STATS-B): a number or a two-level label of the row standing
    after the chained column (`after`, its place) whose fit on the row's other columns and the gap's two terms
    (`_gap_terms`) keeps a gap term; its terms and coefficients. The label the gap is kept by (`by`) is read, never
    dealt."""
    if len(gaps) < TIE_LEAST_ROWS:
        return []
    mean = math.fsum([float(gap) for gap in gaps]) / len(gaps)
    spread = math.sqrt(math.fsum([(gap - mean) * (gap - mean) for gap in gaps]) / len(gaps))
    if spread <= 0.0:
        return []
    gap_values, gap_scores = _gap_terms(gaps, keys, mean, spread)
    out: "list[dict[str, object]]" = []
    for source in sources:
        if source.name in skip or source.name == by or source.place <= after:
            continue
        found = _dependent_response(source, [source.cells[at] for at in picked])
        if found is None or len(found[0]) < TIE_LEAST_ROWS:
            continue
        rows, response = found
        if source.kind != "number" and (sum(1 for value in response if value > 0.5) < TIE_LEAST_CELLS
                                        or sum(1 for value in response if value < 0.5) < TIE_LEAST_CELLS):
            continue
        offered = _candidate_terms([other for other in sources if other.name != source.name],
                                   [picked[at] for at in rows], skip)[:TIE_CANDIDATES_MOST]
        value_term: "list[object]" = ["", _GAP_VALUE, mean, spread]
        score_term: "list[object]" = ["", _GAP_SCORE]
        terms: "list[list[object]]" = [value_term, score_term] + offered
        values = [[1.0 for _at in rows], [gap_values[at] for at in rows], [gap_scores[at] for at in rows]]
        for term in offered:
            column = [other for other in sources if other.name == _word(term[0])][0]
            values += [[_tie_value(term, column.cells[picked[at]]) for at in rows]]
        chosen = _selected(values, response, [1, 2])
        if chosen is None:
            continue
        kept_terms = [terms[at - 1] for at in chosen[1:]]
        columns = [values[at] for at in chosen]
        if source.kind == "number":
            size = len(columns)
            gram = [[math.fsum([a * b for a, b in zip(columns[i], columns[j])]) for j in range(size)]
                    for i in range(size)]
            cross = [math.fsum([a * b for a, b in zip(columns[i], response)]) for i in range(size)]
            total = math.fsum([value * value for value in response])
            fitted = _tie_fit(gram, cross, total, len(response), list(range(size)))
            if fitted is None:
                continue
            out += [{"column": source.name, "kind": "number", "terms": kept_terms, "coefficients": fitted[0],
                     "residual": fitted[2], "grid": list(source.grid)}]
        else:
            beta = _logistic_fit(columns, response)
            if beta is None:
                continue
            out += [{"column": source.name, "kind": "label", "terms": kept_terms, "coefficients": beta,
                     "yes": _bare(source.levels[1]), "no": _bare(source.levels[0])}]
    return out


def tie_chains(zone: "dict[str, object]", gathered: Census, rows_used: "list[int]", sources: "list[TieSource]") -> int:
    """Each chain of `zone` gains its tie (`chain["tie"]`) where the other columns of its row place its gap; the ties made.

    `gathered` is the census the zone was built from (each date column's days and ticks a row), `rows_used` the rows
    the sources' cells stand on (`tie_rows`), `sources` the modelled columns' cells there. Deterministic: a fixed
    function of its inputs. A chain whose gap no term of its row places keeps no tie. Raises what the census's lists
    raise on a mismatch (the caller then writes the zone without ties).
    """
    entries = _object(zone["columns"])
    ties: "dict[str, dict[str, object]]" = {}
    for name in [_word(each) for each in typing.cast("list[object]", zone["order"])]:
        entry = _object(entries[name])
        chain = entry["chain"]
        if not isinstance(chain, dict):
            continue
        reference = _word(chain["reference"])
        if name not in gathered.days_of or reference not in gathered.days_of:
            continue
        days, ticks = gathered.days_of[name], gathered.seconds_of[name]
        reference_days, reference_ticks = gathered.days_of[reference], gathered.seconds_of[reference]
        minute = chain["scale"] == "minute"
        by = _word(chain["by"]) if minute and isinstance(chain["by"], str) else ""
        own_place = -1
        for at_name in range(len(gathered.names)):
            if gathered.names[at_name] == name and own_place < 0:
                own_place = at_name
        picked: "list[int]" = []
        gaps: "list[int]" = []
        keys: "list[str]" = []
        for at in range(len(rows_used)):
            row = rows_used[at]
            gap = _chain_gap(days, ticks, reference_days, reference_ticks, row)
            if gap is None:
                continue
            picked += [at]
            gaps += [gap]
            if minute:
                keys += [_bare(gathered.labels[by][row]) if by and by in gathered.labels else ""]
            else:
                keys += [f"{weekday(reference_days[row])}"]
        if len(picked) < TIE_LEAST_ROWS or len(set(gaps)) < 3:
            continue
        response = _cell_scores(gaps, keys)
        offered = _candidate_terms(sources, picked, {name, reference, by})
        if not offered:
            continue
        # The candidates a wide table offers past `TIE_CANDIDATES_MOST` are screened first: the terms whose own
        # correlation with the gap's score is the largest stay (ties by the table's order).
        mean_response = math.fsum(response) / len(response)
        screened: "list[tuple[float, int, list[object], list[float]]]" = []
        for at_term in range(len(offered)):
            term = offered[at_term]
            column = [source for source in sources if source.name == _word(term[0])][0]
            column_values = [_tie_value(term, column.cells[at]) for at in picked]
            mean_value = math.fsum(column_values) / len(column_values)
            spread = math.fsum([(value - mean_value) * (value - mean_value) for value in column_values])
            if spread <= 0.0:
                continue
            joint = math.fsum([(value - mean_value) * (other - mean_response)
                               for value, other in zip(column_values, response)])
            screened += [(-abs(joint) / math.sqrt(spread), at_term, term, column_values)]
        strongest = sorted([(item[0], item[1]) for item in screened])[:TIE_CANDIDATES_MOST]
        kept_at = sorted([at_term for _strength, at_term in strongest])
        by_at: "dict[int, tuple[list[object], list[float]]]" = {}
        for item in screened:
            by_at[item[1]] = (item[2], item[3])
        terms = [by_at[at_term][0] for at_term in kept_at]
        if not terms:
            continue
        values = [[1.0 for _at in picked]] + [by_at[at_term][1] for at_term in kept_at]
        size = len(values)
        gram = [[0.0 for _j in range(size)] for _i in range(size)]
        for i in range(size):
            for j in range(i + 1):
                gram[i][j] = gram[j][i] = math.fsum([a * b for a, b in zip(values[i], values[j])])
        cross = [math.fsum([a * b for a, b in zip(values[i], response)]) for i in range(size)]
        total = math.fsum([value * value for value in response])
        chosen = [0]
        best_fit = _tie_fit(gram, cross, total, len(picked), chosen)
        while best_fit is not None and len(chosen) <= TIE_TERMS_MOST:
            best: "tuple[float, int] | None" = None
            for candidate in range(1, size):
                if candidate in chosen:
                    continue
                trial = _tie_fit(gram, cross, total, len(picked), chosen + [candidate])
                if trial is None:
                    continue
                strength = abs(trial[1][len(chosen)])
                if strength >= TIE_GATE_Z and (best is None or strength > best[0]):
                    best = (strength, candidate)
            if best is None:
                break
            chosen += [best[1]]
            best_fit = _tie_fit(gram, cross, total, len(picked), chosen)
        if best_fit is None or len(chosen) < 2:
            continue
        beta, _zs, residual = best_fit
        ties[name] = {"terms": [terms[at - 1] for at in chosen[1:]], "coefficients": [beta[0]] + beta[1:],
                      "residual": residual,
                      "dependents": _dependents_of(sources, picked, gaps, keys, {name, reference}, own_place, by)}
    # ...each set once every chain is fitted, so a fit that stops leaves the zone without any.
    for name in ties:
        typing.cast("dict[str, object]", _object(entries[name])["chain"])["tie"] = ties[name]
    return len(ties)


def tie_columns(zone: "dict[str, object]") -> "list[str]":
    """Every column a tie of the zone reads, once each, in order (a twin's cells of them are what `tied_again` reads)."""
    out: "list[str]" = []
    found = _object(zone)
    entries = _object(found["columns"])
    for name in [_word(each) for each in typing.cast("list[object]", found["order"])]:
        chain = _object(entries[name])["chain"]
        if not isinstance(chain, dict) or "tie" not in chain:
            continue
        tie = _object(chain["tie"])
        for term in typing.cast("list[list[object]]", tie["terms"]):
            if _word(term[0]) not in out:
                out += [_word(term[0])]
        for dependent in typing.cast("list[object]", tie["dependents"] if "dependents" in tie else []):
            found = _object(dependent)
            for word in [_word(found["column"])] + [_word(term[0]) for term in typing.cast("list[list[object]]", found["terms"])]:
                if word and word not in out:
                    out += [word]
        by = chain["by"] if "by" in chain else ""
        if isinstance(by, str) and by and by != "weekday" and by not in out:
            out += [by]
    return out


def tie_dates(zone: "dict[str, object]") -> "list[str]":
    """The date columns `tied_again` reads, in the zone's order: each tied chain's column and its reference, and every
    column chained, at any depth, to one of them with its reference (a twin's other date columns are never read, so a
    table of millions of rows holds only these while the ties are dealt)."""
    found = _object(zone)
    entries = _object(found["columns"])
    order = [_word(each) for each in typing.cast("list[object]", found["order"])]
    moving: "set[str]" = set()
    needed: "list[str]" = []
    for name in order:
        chain = _object(entries[name])["chain"]
        if not isinstance(chain, dict):
            continue
        reference = _word(chain["reference"])
        if "tie" in chain or reference in moving:
            moving = moving | {name}
            for each in (reference, name):
                if each not in needed:
                    needed += [each]
    # ...and every column an ordering of the real table ties to a moving one, so the orderings are read whole.
    for pair in typing.cast("list[list[object]]", found["orders"]) if "orders" in found else []:
        if isinstance(pair, list) and len(pair) == 2:
            first, second = _word(pair[0]), _word(pair[1])
            if first in moving and second not in needed:
                needed += [second]
            if second in moving and first not in needed:
                needed += [first]
    return [name for name in order if name in needed]


def tied(zone: object) -> bool:
    """Whether a dates zone holds a tie (`tie_chains`)."""
    if not isinstance(zone, dict) or "columns" not in zone or "order" not in zone:
        return False
    return bool([name for name in typing.cast("list[object]", zone["order"])
                 if isinstance(name, str) and isinstance(_object(zone["columns"])[name], dict)
                 and isinstance(_object(_object(zone["columns"])[name])["chain"], dict)
                 and "tie" in _object(_object(_object(zone["columns"])[name])["chain"])])


def _dealt_by(latent: "dict[int, float]", cells: "list[str]") -> "list[str]":
    """The cells of `latent`'s rows dealt again among them: the smallest cell (a number's value, a label's text in
    order) to the row of the smallest latent score, and so on; every other row keeps its cell."""
    rows = sorted(latent)
    ranked: "list[tuple[float, str]]" = []
    for row in rows:
        value = _plain_value(cells[row])
        ranked += [(value if value is not None else 0.0, cells[row])]
    ranked = sorted(ranked)
    takers = [row for _score, row in sorted((latent[row], row) for row in rows)]
    out = list(cells)
    for at in range(len(takers)):
        out[takers[at]] = ranked[at][1]
    return out


def _dependents_dealt(dependents: "list[object]", gaps: "dict[int, int]", keys: "dict[int, str]",
                      cells: "dict[str, list[str]]", exclude: "typing.Collection[str]", seed: int, name: str,
                      out: "dict[str, list[str]]") -> None:
    """Each dependent of a tied chain (`_dependents_of`) dealt again by its fit on the twin's row, the twin's own gap
    among its terms: a number's cells among its rows holding a number by the fit plus a residual, a two-level label's
    two levels among its rows holding either by the fit plus a logistic draw. Each dealt column is written into
    `out` and `cells` (a later dependent reads it)."""
    rows_with = sorted(gaps)
    for dependent in dependents:
        entry = _object(dependent)
        column = _word(entry["column"])
        terms = typing.cast("list[list[object]]", entry["terms"])
        if column in exclude or column not in cells or not all(
                (not _word(term[0])) or _word(term[0]) in cells for term in terms):
            continue
        coefficients = [float(typing.cast(float, value)) for value in typing.cast("list[object]", entry["coefficients"])]
        if len(coefficients) != len(terms) + 1:
            continue
        own = cells[column]
        number = _word(entry["kind"]) == "number"
        eligible = [row for row in rows_with
                    if (_plain_value(own[row]) is not None if number
                        else _bare(own[row]) in (_word(entry["yes"]), _word(entry["no"])))]
        if len(eligible) < 2:
            continue
        scores = _cell_scores([gaps[row] for row in eligible], [keys[row] for row in eligible])
        score_of: "dict[int, float]" = {}
        for at in range(len(eligible)):
            score_of[eligible[at]] = scores[at]
        state = _stream(seed, name + "\x00" + column, "dependent")
        latent: "dict[int, float]" = {}
        for row in eligible:
            total = coefficients[0]
            for at in range(len(terms)):
                term = terms[at]
                kind = _word(term[1])
                if kind == _GAP_VALUE:
                    value = (gaps[row] - float(typing.cast(float, term[2]))) / float(typing.cast(float, term[3]))
                elif kind == _GAP_SCORE:
                    value = score_of[row]
                else:
                    value = _tie_value(term, cells[_word(term[0])][row])
                total += coefficients[at + 1] * value
            if number:
                noise = -6.0
                for _k in range(12):
                    noise += _uniform(state)
                total += float(typing.cast(float, entry["residual"])) * noise
            else:
                u = _uniform(state)
                total += chain_walk.natural_log(u / (1.0 - u))
            latent[row] = total
        if number:
            written = _dealt_by(latent, own)
        else:
            yes = _word(entry["yes"])
            takers = [row for _score, row in sorted((-latent[row], row) for row in eligible)]
            ones = [row for row in eligible if _bare(own[row]) == yes]
            others = [row for row in eligible if _bare(own[row]) != yes]
            written = list(own)
            for at in range(len(takers)):
                source = ones[at] if at < len(ones) else others[at - len(ones)]
                written[takers[at]] = own[source]
        cells[column] = written
        out[column] = written


def tied_again(zone: "dict[str, object]", cells: "dict[str, list[str]]", rows: int, seed: int,
               exclude: "typing.Collection[str]" = ()) -> "dict[str, list[str]]":
    """The twin's date columns a tie moves, written again: each tied chain's gaps dealt within its cells by the tie's
    score of the row (lane STATS-B), each column chained to a moved one moved with it; only the columns that move.

    `cells` holds the twin's cells of every date column of the zone and of every column a tie reads
    (`tie_columns`); a column missing from it is left as it stands, and so is every chain whose reference or own
    column is missing. `exclude` names the columns another zone writes by its own rule: such a chained column is
    not tied again (it moves only with a moved reference) and such a column is never dealt as a dependent. Each cell's gap is one of its cell's own gaps on the twin, so every cell's quantile function
    stands; a moved date is spelled by `_spelled_column` with the column's own cells as given (their spellings dealt
    by the rank of the instants). A row where an ordering of `orders` would break keeps all its dates. Same zone,
    cells and seed, same cells. Raises DatesError on a damaged zone.
    """
    found = _object(zone)
    _versioned(found)
    entries = _object(found["columns"])
    order = [_word(each) for each in typing.cast("list[object]", found["order"])]
    readings: "dict[str, Reading]" = {}
    original: "dict[str, tuple[list[int], list[int]]]" = {}
    for name in order:
        if name not in cells or len(cells[name]) != rows:
            continue
        reading_entry = _object(_object(entries[name])["reading"])
        readings[name] = Reading(_word(reading_entry["kind"]), _word(reading_entry["member"]))
        days = [_ABSENT] * rows
        ticks = [-1] * rows
        for row in range(rows):
            moment = _moment(cells[name][row], readings[name]) if _bare(cells[name][row]) else None
            if moment is not None:
                days[row], ticks[row] = moment
        original[name] = (days, ticks)
    current: "dict[str, tuple[list[int], list[int]]]" = {}
    for name in order:
        if name not in original:
            continue
        chain = _object(entries[name])["chain"]
        if not isinstance(chain, dict):
            continue
        reference = _word(chain["reference"])
        if reference not in original:
            continue
        # A column another zone writes by its own rule (a keyed table's later clock, moved to its key level's gap)
        # is never tied again here; it moves only with a moved reference.
        tie = _object(chain["tie"]) if "tie" in chain and name not in exclude else None
        moved_reference = reference in current
        if tie is None and not moved_reference:
            continue
        days, ticks = original[name]
        reference_days, reference_ticks = original[reference]
        now_days, now_ticks = current[reference] if moved_reference else original[reference]
        gaps: "dict[int, int]" = {}
        for row in range(rows):
            gap = _chain_gap(days, ticks, reference_days, reference_ticks, row)
            if gap is not None:
                gaps[row] = gap
        if tie is not None:
            minute = chain["scale"] == "minute"
            by = _word(chain["by"]) if minute and isinstance(chain["by"], str) else ""
            terms = typing.cast("list[list[object]]", tie["terms"])
            coefficients = [float(typing.cast(float, value)) for value in typing.cast("list[object]", tie["coefficients"])]
            residual = float(typing.cast(float, tie["residual"]))
            if all(_word(term[0]) in cells for term in terms) and len(coefficients) == len(terms) + 1:
                state = _stream(seed, name, "tie")
                by_key: "dict[str, list[tuple[float, int]]]" = {}
                for row in sorted(gaps):
                    score = coefficients[0]
                    for at in range(len(terms)):
                        score += coefficients[at + 1] * _tie_value(terms[at], cells[_word(terms[at][0])][row])
                    noise = -6.0
                    for _k in range(12):
                        noise += _uniform(state)
                    score += residual * noise
                    if minute:
                        key = _level(cells, by, row) if by else ""
                    else:
                        key = f"{weekday(reference_days[row])}"
                    if key not in by_key:
                        by_key[key] = []
                    by_key[key] += [(score, row)]
                dealt: "dict[int, int]" = {}
                for key in sorted(by_key):
                    placed = sorted(by_key[key])
                    values = sorted(gaps[row] for _score, row in placed)
                    for at in range(len(placed)):
                        dealt[placed[at][1]] = values[at]
                gaps = dealt
        new_days = list(days)
        new_ticks = list(ticks)
        for row in gaps:
            if now_days[row] == _ABSENT:
                continue
            if ticks[row] >= 0 and reference_ticks[row] >= 0 and now_ticks[row] >= 0:
                instant = _instant(now_days[row], now_ticks[row]) + gaps[row]
                new_days[row] = instant // DAY_TICKS
                new_ticks[row] = instant - new_days[row] * DAY_TICKS
            else:
                new_days[row] = now_days[row] + gaps[row]
        current[name] = (new_days, new_ticks)
    if not current:
        return {}
    pairs = [(_word(pair[0]), _word(pair[1])) for pair in typing.cast("list[list[object]]", found["orders"])
             if isinstance(pair, list) and len(pair) == 2] if "orders" in found else []
    # ...and each moved column's real months (batch 4zz's fix round, the outside review's item 8: the deal rebuilt a
    # date from a gap dealt to another row, and a January start's end crossed into February, after lane IN-5's pass
    # kept every date inside): a row whose moved date would leave them keeps all its dates, as a broken order does.
    rooms: "dict[str, tuple[int, int]]" = {}
    for name in current:
        calendar = _prepared_calendar(_object(entries[name])["calendar"])
        rooms[name] = (calendar.first_day, calendar.last_day)
    for row in range(rows):
        if not any(current[name][0][row] != original[name][0][row] or current[name][1][row] != original[name][1][row]
                   for name in current):
            continue
        broken = any(
            current[name][0][row] != _ABSENT
            and current[name][0][row] != original[name][0][row]
            and not rooms[name][0] <= current[name][0][row] <= rooms[name][1]
            for name in current
        )
        for first, second in pairs:
            if broken:
                break
            if first not in original or second not in original:
                continue
            a = current[first] if first in current else original[first]
            b = current[second] if second in current else original[second]
            if a[0][row] == _ABSENT or b[0][row] == _ABSENT:
                continue
            if _instant(a[0][row], a[1][row]) > _instant(b[0][row], b[1][row]):
                broken = True
                break
        if broken:
            for name in current:
                current[name][0][row] = original[name][0][row]
                current[name][1][row] = original[name][1][row]
    out: "dict[str, list[str]]" = {}
    for name in order:
        if name not in current:
            continue
        if current[name] == original[name]:
            continue
        out[name] = _spelled_column(entries, name, current[name], rows, seed, cells[name])
    # THE GAP'S DEPENDENTS (lane STATS-B): each column after a tied chain that the gap places, dealt again on the
    # twin's own gaps as they now stand -- but never one each person holds one value of on the twin (batch 4zz's fix
    # round, the outside review's item 9: a person's group, fixed on every row of the person, was dealt row by row
    # and took both values within all 1,000 persons), read off the zone's person column where `cells` holds it.
    person = _word(found["person"]) if "person" in found and isinstance(found["person"], str) else ""
    held_by_person: "set[str]" = set()
    if person and person in cells and len(cells[person]) == rows:
        for name in order:
            chain = _object(entries[name])["chain"] if name in original else None
            if not isinstance(chain, dict) or "tie" not in chain:
                continue
            for dependent in typing.cast("list[object]", _object(chain["tie"])["dependents"]
                                         if "dependents" in _object(chain["tie"]) else []):
                column = _word(_object(dependent)["column"])
                if column in cells and column not in held_by_person and _one_a_person(cells[column], cells[person]):
                    held_by_person = held_by_person | {column}
    excluded = set(exclude) | held_by_person
    for name in order:
        chain = _object(entries[name])["chain"] if name in original else None
        if not isinstance(chain, dict) or "tie" not in chain or name not in current or name in exclude:
            continue
        dependents = typing.cast("list[object]", _object(chain["tie"])["dependents"]
                                 if "dependents" in _object(chain["tie"]) else [])
        reference = _word(chain["reference"])
        if not dependents or reference not in original:
            continue
        own_days, own_ticks = current[name]
        reference_days, reference_ticks = current[reference] if reference in current else original[reference]
        minute = chain["scale"] == "minute"
        by = _word(chain["by"]) if minute and isinstance(chain["by"], str) else ""
        gaps_now: "dict[int, int]" = {}
        keys_now: "dict[int, str]" = {}
        for row in range(rows):
            gap = _chain_gap(own_days, own_ticks, reference_days, reference_ticks, row)
            if gap is None:
                continue
            gaps_now[row] = gap
            if minute:
                keys_now[row] = _level(cells, by, row) if by else ""
            else:
                keys_now[row] = f"{weekday(original[reference][0][row])}"
        _dependents_dealt(dependents, gaps_now, keys_now, cells, excluded, seed, name, out)
    return out


def _one_a_person(values: "list[str]", persons: "list[str]") -> bool:
    """Whether every person (a blank person none) holds one value on all its rows, and some person holds two rows."""
    seen: "dict[str, str]" = {}
    repeated = False
    for row in range(min(len(values), len(persons))):
        who = persons[row]
        if not _bare(who):
            continue
        if who in seen:
            if seen[who] != values[row]:
                return False
            repeated = True
        else:
            seen[who] = values[row]
    return repeated

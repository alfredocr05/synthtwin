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

from synthtwin import date_counts, offset_rules, parsing, twinstore

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


def census(person: str = "", readings: "dict[str, str] | None" = None, skip: "tuple[str, ...]" = (),
           declared_only: bool = False) -> Census:
    """An empty census: `build_zone`'s arguments but the columns, which `take_column` hands in one at a time."""
    return Census(person, dict(readings) if readings is not None else {}, tuple(skip), declared_only)


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
    found_mixed = _mixed_columns({name: texts}, set(), gathered.cache)
    if name in found_mixed:
        gathered.mixed[name] = found_mixed[name]


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
    The columns are taken one at a time (`take_column`), as the profile
    hook takes them from a table read in groups, so the zone is the same
    whichever way it is built.
    """
    gathered = census(person, readings, skip, declared_only)
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
        shares = _numbers(held_places[key])
        if len(shares) != PLACE_BINS:
            raise DatesError("The dates zone is damaged: a share of the persons' places is missing.")
        places[key] = shares
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
                 cache: "dict[int, tuple[int, int, int]]", rule: "offset_rules.Rule | None" = None) -> "list[int]":
    """Each row's move, in whole weeks, that gives a column's dates exactly the months of `targets` (one month a date
    of the description's twin), the earliest date the earliest month; nought where a date stays or is absent.

    A move of whole weeks keeps each date's weekday and clock and changes
    only its day of the month (made up in any case) and, where its month
    differs from the month its rank asks for, its month: the date lands on
    one of that month's days of its weekday, chosen by a fixed hash of the
    row, as the dates zone makes up a day (so no date piles at a month's
    first or last week); where no whole week reaches its bin (a part of a
    month before or after an offset rule's change, fewer than seven days),
    the nearest day in it, its clock kept.
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
        if landing:
            moves[row] = landing[_mixed((row << 4) + len(landing)) % len(landing)]
            continue
        # A part of a month no whole week reaches (the days before an offset rule's change in a month, fewer than
        # seven): the nearest day that is in it, its clock kept and its weekday given up.
        for distance in range(1, _DAYS_NEAR + 1):
            if _bin(day + distance * (1 if step > 0 else -1), second, rule, cache) == goal:
                moves[row] = distance * (1 if step > 0 else -1)
                break
            if _bin(day - distance * (1 if step > 0 else -1), second, rule, cache) == goal:
                moves[row] = -distance * (1 if step > 0 else -1)
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
                         rule: "offset_rules.Rule | None" = None) -> "list[int]":
    """Each row's move, in whole weeks and the same for every row of a person, that brings a person timeline's months
    to `targets` (one month a date of the description's twin): passes in which each person takes the move among
    `_PERSON_WEEKS` (weeks, earlier or later) that most closes the distance, then persons of one date moved from a
    month that holds too many to one that holds too few. Every weekday, clock and gap within a person stands."""
    moves = [0 for _row in range(len(days))]
    surplus: "dict[int, int]" = {}
    for month in targets:
        surplus[month] = (surplus[month] if month in surplus else 0) - 1
    dated: "list[list[int]]" = []
    for rows in groups:
        mine = [row for row in rows if days[row] != _ABSENT]
        dated += [mine]
        for row in mine:
            month = _bin(days[row], _tick_of(seconds, row), rule, cache)
            surplus[month] = (surplus[month] if month in surplus else 0) + 1
    shift = [0 for _group in groups]
    for _pass in range(_PERSON_PASSES):
        improved = False
        for at in range(len(groups)):
            mine = dated[at]
            if not mine:
                continue
            now = [_bin(days[row] + shift[at], _tick_of(seconds, row), rule, cache) for row in mine]
            best, chosen = 0, 0
            for weeks in _PERSON_WEEKS:
                for sign in (1, -1):
                    step = sign * weeks * _WEEK
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
            best, chosen = 0, 0
            for goal in short:
                if surplus[goal] >= 0:
                    continue
                step = _week_into(first, goal, cache, _tick_of(seconds, mine[0]), rule)
                if not step:
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
        for _week in range(_WEEKS_AT_MOST):
            moved += step
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
    so every gap stands (lane IN-2b)."""
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
        if name == timeline_column and groups is not None:
            moves = _persons_months_held(days, groups, bins, cache, seconds, rule)
            _moved(moments, [name] + _descendants(name, children), moves)
            continue
        # ...row by row: its months exactly, and, where it follows an offset rule, the dates in each season of it.
        moves = _months_held(days, seconds, bins, cache, rule)
        _moved(moments, [name] + _descendants(name, children), moves)


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
    if months is not None:
        cache_days: "dict[int, tuple[int, int, int]]" = {}
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
        _held_months(entries, order, line_column, moments, months, cache_days, groups)
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
    for row in range(len(given)):
        cell = given[row]
        if not _bare(cell):
            continue
        moment = _moment(cell, reading)
        if moment is None:
            continue
        found += [(moment[0], moment[1], row, spelling_of(cell, reading))]
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

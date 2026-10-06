"""Numbers that are dates: the twelve counting systems (landing R4, plan P4-D384).

A spreadsheet, a statistics package and a database each keep a date as a
NUMBER -- days from an epoch, seconds, milliseconds -- and an export
writes that number. Read undeclared, such a column is a column of counts
or of measurements: its twin keeps every number's spelling and its span,
and loses the calendar -- the weekday, the clock grid, the hours.

This module holds the closed table of the twelve counting systems
(`MEMBERS`), how a cell written as a count is read EXACTLY as the moment
it names, how a moment is written back as the same count in the
column's own spelling (`count_form`), and the rule that says where a
column of numbers is worth asking about (question Q3, "number or
date?"). Every rule here is whole-number arithmetic: no float stands on
either side of a reading, so a count past 2**53 -- nanoseconds since
1970 -- is read from its figures and written back from them.

Nothing here reads a table or decides a reading on its own: a column is
read as counted dates only where the person said so (`--date-count`, or
an answer to Q3, recorded as `settings.forced_date_counts`). No I/O of
any kind.
"""

import dataclasses

from synthtwin import parsing

# ---------------------------------------------------------------- units

# How many nanoseconds each unit a member counts in holds. Whole numbers:
# every instant this module handles is a whole number of nanoseconds.
NANOSECOND = 1
MICROSECOND = 1000
MILLISECOND = 1000 * MICROSECOND
SECOND = 1000 * MILLISECOND
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR

# THE UNITS A READING MAY BE SETTLED TO, finest first (the design's unit
# U): a column's figures carry a step -- its member's unit over ten to
# the figures it writes after the point -- and its moments are settled to
# the finest of these that is at least that step, so no figure is read
# finer than it was written: Excel's `%.15g` writes ten figures after
# the point, a step of 8.64 microseconds, and is settled to the
# millisecond, which takes away what binary64 added. AND NEVER COARSER
# THAN A MINUTE where the step is under a day: a column writing one
# figure after the point steps by 2.4 hours, and the design's own rule
# settled `45386.5`, a noon, to midnight, where a minute keeps every
# step the figures can tell apart.
SETTLED_UNITS = (NANOSECOND, MICROSECOND, MILLISECOND, SECOND, MINUTE, DAY)

# THE UNITS A MOMENT IS WRITTEN AT, coarsest first: a whole date, a clock
# to the minute (an hour is written as one), to the second, and to three,
# six or nine figures of a second. These are exactly the precisions the
# datetime role publishes, so a reading written at one of them is read
# back by that role at the same precision.
WRITTEN_UNITS = (DAY, MINUTE, SECOND, MILLISECOND, MICROSECOND, NANOSECOND)

# The figures after the second each sub-second unit writes.
_SUBSECOND_FIGURES = {MILLISECOND: 3, MICROSECOND: 6, NANOSECOND: 9}

# ---------------------------------------------------------- the members

# THE TWELVE WORDS, in the table's own order. Each is the setting a
# description records, the answer a person writes in the questions file
# and the second word of `--date-count COLUMN MEMBER`.
EXCEL_1900 = "excel-1900"
EXCEL_1904 = "excel-1904"
DAYS_SINCE_1960 = "days-since-1960"
SECONDS_SINCE_1960 = "seconds-since-1960"
MILLISECONDS_SINCE_1960 = "milliseconds-since-1960"
DAYS_SINCE_1970 = "days-since-1970"
SECONDS_SINCE_1970 = "seconds-since-1970"
MILLISECONDS_SINCE_1970 = "milliseconds-since-1970"
MICROSECONDS_SINCE_1970 = "microseconds-since-1970"
NANOSECONDS_SINCE_1970 = "nanoseconds-since-1970"
DAYS_SINCE_1840 = "days-since-1840"
SECONDS_SINCE_1582 = "seconds-since-1582"

MEMBERS = (
    EXCEL_1900,
    EXCEL_1904,
    DAYS_SINCE_1960,
    SECONDS_SINCE_1960,
    MILLISECONDS_SINCE_1960,
    DAYS_SINCE_1970,
    SECONDS_SINCE_1970,
    MILLISECONDS_SINCE_1970,
    MICROSECONDS_SINCE_1970,
    NANOSECONDS_SINCE_1970,
    DAYS_SINCE_1840,
    SECONDS_SINCE_1582,
)


@dataclasses.dataclass(frozen=True)
class Member:
    """One counting system: what it counts, from when, and who writes it.

    `epoch` is the day its count of nought names, as days from 1 January
    1970 (`parsing.days_from_civil`); `unit` how many nanoseconds one of
    its counts holds. `signed` says a count below nought is read, as the
    day before the epoch and so on, which every member does but the two
    spreadsheet systems, whose first day is their first count. `contacts`
    says the figures after the point are a CONTACT NUMBER and never a
    time of day (`days-since-1840`, as `*_DATE_REAL` columns write it).
    `means` is the clause a question says the member in, and `unit_word`
    the plural of what it counts.
    """

    word: str
    unit: int
    epoch: int
    signed: bool
    contacts: bool
    unit_word: str
    means: str


def _day(year: int, month: int, day: int) -> int:
    """`parsing.days_from_civil`, named once for this table."""
    return parsing.days_from_civil(year, month, day)


# EXCEL'S 1900 SYSTEM AND ITS LEAP DAY. Serial 1 is 1 January 1900, and
# the system counts a 29 February 1900 that never was as serial 60, so
# serials 1 to 59 count from 31 December 1899, serial 60 names no day,
# and from serial 61 (1 March 1900) the count runs from 30 December 1899.
# `dialect.sheet_serial_moment` reads a typed workbook cell by the same
# rule through its own float path (the R4 design review, item 9: sharing
# the exact path would move 94 of 333,333 computed times by a
# millisecond), and `tests/test_stage3b_counted.py` holds the two to
# one answer on every whole serial.
_EXCEL_EARLY_EPOCH = _day(1899, 12, 31)
_EXCEL_LEAP_SERIAL = 60
_EXCEL_FIRST_MARCH = _day(1900, 3, 1)

TABLE: "dict[str, Member]" = {
    EXCEL_1900: Member(
        EXCEL_1900, DAY, _day(1899, 12, 30), False, False, "days",
        "days from 30 December 1899, as Excel, Sheets and LibreOffice "
        "keep dates, with the figures after the point the time of day",
    ),
    EXCEL_1904: Member(
        EXCEL_1904, DAY, _day(1904, 1, 1), False, False, "days",
        "days from 1 January 1904, as Excel for Mac kept dates in older "
        "workbooks, with the figures after the point the time of day",
    ),
    DAYS_SINCE_1960: Member(
        DAYS_SINCE_1960, DAY, _day(1960, 1, 1), True, False, "days",
        "days from 1 January 1960, as SAS and Stata keep dates",
    ),
    SECONDS_SINCE_1960: Member(
        SECONDS_SINCE_1960, SECOND, _day(1960, 1, 1), True, False, "seconds",
        "seconds from the start of 1 January 1960, as SAS keeps moments",
    ),
    MILLISECONDS_SINCE_1960: Member(
        MILLISECONDS_SINCE_1960, MILLISECOND, _day(1960, 1, 1), True, False,
        "milliseconds",
        "milliseconds from the start of 1 January 1960, as Stata keeps "
        "moments",
    ),
    DAYS_SINCE_1970: Member(
        DAYS_SINCE_1970, DAY, _day(1970, 1, 1), True, False, "days",
        "days from 1 January 1970, as R keeps dates",
    ),
    SECONDS_SINCE_1970: Member(
        SECONDS_SINCE_1970, SECOND, _day(1970, 1, 1), True, False, "seconds",
        "seconds from the start of 1 January 1970, as Unix and Python keep "
        "moments",
    ),
    MILLISECONDS_SINCE_1970: Member(
        MILLISECONDS_SINCE_1970, MILLISECOND, _day(1970, 1, 1), True, False,
        "milliseconds",
        "milliseconds from the start of 1 January 1970, as JavaScript and "
        "Java keep moments",
    ),
    MICROSECONDS_SINCE_1970: Member(
        MICROSECONDS_SINCE_1970, MICROSECOND, _day(1970, 1, 1), True, False,
        "microseconds",
        "microseconds from the start of 1 January 1970, as Arrow and "
        "Parquet keep moments",
    ),
    NANOSECONDS_SINCE_1970: Member(
        NANOSECONDS_SINCE_1970, NANOSECOND, _day(1970, 1, 1), True, False,
        "nanoseconds",
        "nanoseconds from the start of 1 January 1970, as pandas keeps "
        "moments",
    ),
    DAYS_SINCE_1840: Member(
        DAYS_SINCE_1840, DAY, _day(1840, 12, 31), True, True, "days",
        "days from 31 December 1840, as Epic and MUMPS keep dates, with "
        "the figures after the point a contact number rather than a time",
    ),
    SECONDS_SINCE_1582: Member(
        SECONDS_SINCE_1582, SECOND, _day(1582, 10, 14), True, False,
        "seconds",
        "seconds from the start of 14 October 1582, as SPSS keeps dates",
    ),
}

# The first and the last moment any member is read to: the four-figure
# years an ISO date writes. A count naming a moment outside them is a
# number that names no date this description can write.
_FIRST_DAY = _day(1, 1, 1)
_LAST_DAY = _day(9999, 12, 31)

# THE WORD A CENSUS OF CONTACT NUMBERS GIVES A CELL WRITING NONE.
NO_CONTACT = "(none)"

# ------------------------------------------------------------- grammar

# The decimal marks a column of counts may write, the point first.
POINT = "."
COMMA = ","
MARKS = (POINT, COMMA)


def _figures(text: str) -> bool:
    """Whether ``text`` is one or more ASCII figures and nothing else."""
    if not isinstance(text, str):
        raise TypeError("internal check: a count's figures were not text")
    return bool(text) and text.isascii() and text.isdigit()


def _place_of(text: str, mark: str) -> int:
    """Where ``mark`` first stands in ``text``, or -1."""
    if not isinstance(text, str):
        raise TypeError("internal check: a cell was not text")
    if not isinstance(mark, str):
        raise TypeError("internal check: a mark was not text")
    return text.find(mark)


@dataclasses.dataclass(frozen=True)
class Written:
    """One cell read as a count, figure for figure.

    `negative` is the leading minus; `whole` the figures before the mark,
    `fraction` those after it (empty where the cell writes no mark), and
    `exponent` the power of ten an exponent form multiplies by (nought
    where the cell writes none). `exponent_form` says the cell wrote one.
    """

    negative: bool
    whole: str
    fraction: str
    exponent: int
    exponent_form: bool


def written_count(text: str, mark: str = POINT) -> "Written | None":
    """A cell read as a count, or None where it is written any other way.

    THE GRAMMAR, and nothing wider: an optional minus, then whole figures
    -- `0` alone or a first figure other than `0`, so a padded `007` is a
    code's spelling and not a count's -- then optionally ``mark`` and one
    or more figures, then, on the point only, optionally an exponent:
    `e` or `E`, an optional sign and figures, the form R and Python write
    a count in where it is shorter (the R4 design review, item 6). A
    leading plus, a grouped number, a space anywhere and any other
    character are not counts.

    Guarantees: accepts a cell's text and the column's decimal mark;
    returns its parts or None. Determinism: a function of the two.
    Raises TypeError where the text is not text. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a cell was not text")
    if not isinstance(mark, str):
        raise TypeError("internal check: a decimal mark was not text")
    if not text:
        return None
    negative = text[:1] == "-"
    start = 1 if negative else 0
    exponent = 0
    exponent_form = False
    stop = len(text)
    if mark == POINT:
        cut = _place_of(text, "e")
        if cut < 0:
            cut = _place_of(text, "E")
        if cut >= 0:
            sign = 1
            after = cut + 1
            if text[after : after + 1] in ("+", "-"):
                if text[after : after + 1] == "-":
                    sign = -1
                after = after + 1
            power = text[after:]
            if not _figures(power) or len(power) > 4:
                return None
            exponent = sign * int(power)
            exponent_form = True
            stop = cut
    split = _place_of(text, mark)
    whole = text[start:stop]
    fraction = ""
    if 0 <= split < stop:
        whole = text[start:split]
        fraction = text[split + 1 : stop]
        if not _figures(fraction):
            return None
    if not _figures(whole):
        return None
    if len(whole) > 1 and whole[:1] == "0":
        return None
    if exponent_form and (len(whole) != 1 or whole == "0" and fraction):
        # A MANTISSA WRITES ONE FIGURE BEFORE THE POINT, as every exporter
        # writing an exponent does; anything else is not this form.
        return None
    return Written(negative, whole, fraction, exponent, exponent_form)


def exact_value(written: Written) -> "tuple[int, int]":
    """The number a written count denotes, as a whole numerator over a power of ten.

    Exact: the figures are read as one whole number and the point and
    the exponent only move the power of ten beneath it. Guarantees: a
    function of the parts; the denominator is a positive power of ten.
    Raises nothing. No I/O.
    """
    numerator = int(written.whole + written.fraction)
    shift = len(written.fraction) - written.exponent
    denominator = 1
    if shift >= 0:
        denominator = 10**shift
    else:
        numerator = numerator * 10 ** (-shift)
    if written.negative:
        numerator = -numerator
    return numerator, denominator


def figures_after_the_mark(written: Written) -> int:
    """How many figures after the point the number a cell writes carries.

    The figures written after the mark, less the exponent: `1.6e+12` is a
    whole number and carries none. Guarantees: a function of the parts;
    never below nought. Raises nothing. No I/O.
    """
    return max(0, len(written.fraction) - written.exponent)


def significant_figures(written: Written) -> int:
    """How many significant figures a cell writes: its figures, less the leading zeros."""
    figures = written.whole + written.fraction
    while len(figures) > 1 and figures[:1] == "0":
        figures = figures[1:]
    return len(figures)


def integer_figures(written: Written) -> int:
    """How many figures the whole part of a cell's number has: `45386.5` five, `1.6e+12` thirteen."""
    if written.exponent_form:
        return max(1, len(written.whole) + written.exponent)
    return len(written.whole)


@dataclasses.dataclass(frozen=True)
class Tally:
    """What a column's counts show of how they are written, cell by cell, held as five numbers.

    `places` the most figures after the mark a cell's number carries and
    `least` the fewest; `significant` the most significant figures a cell
    writes; `whole` the most figures a cell's whole part has; `exponent`
    whether a cell writes an exponent form. Taken in one walk and nothing
    kept per cell, so a million counts cost five numbers.
    """

    places: int = 0
    least: int = -1
    significant: int = 0
    whole: int = 0
    exponent: bool = False


def tallied(tally: Tally, written: Written) -> Tally:
    """One more cell's figures, taken into a tally."""
    figures = figures_after_the_mark(written)
    return Tally(
        max(tally.places, figures),
        figures if tally.least < 0 else min(tally.least, figures),
        max(tally.significant, significant_figures(written)),
        max(tally.whole, integer_figures(written)),
        tally.exponent or written.exponent_form,
    )


# ------------------------------------------------------------- reading


def _rounded(numerator: int, denominator: int) -> int:
    """``numerator / denominator`` rounded to the nearest whole number, halves to even."""
    quotient, rest = divmod(numerator, denominator)
    doubled = 2 * rest
    if doubled > denominator or (doubled == denominator and quotient % 2 == 1):
        quotient = quotient + 1
    return quotient


def moment_of(
    member: str, numerator: int, denominator: int, settled: int
) -> "int | None":
    """The moment a count names, in whole ``settled`` units from 1970, or None.

    THE COUNT IS READ EXACTLY AND SETTLED ONCE: the number is carried as
    a whole numerator over its power of ten, multiplied out in
    nanoseconds and rounded, halves to even, to the nearest ``settled``
    unit -- one of `SETTLED_UNITS`. A spreadsheet serial reads its whole
    days by Excel's own leap rule and the rest of the day as a time; a
    member with contacts reads the figures before the point alone, as a
    day.

    None where the count names no date: a spreadsheet serial below one
    or on day 60 of the 1900 system, a negative count of a member that
    reads none, and a moment before 0001-01-01 or after 9999-12-31.

    Guarantees: accepts a member word, the exact count and a settled
    unit; returns a whole number of those units from the start of 1
    January 1970, or None. Determinism: whole-number arithmetic only.
    Raises KeyError for a word outside `MEMBERS`. No I/O of any kind.
    """
    found = TABLE[member]
    if denominator <= 0:
        return None
    if numerator < 0 and not found.signed:
        return None
    if found.contacts:
        # THE FIGURES AFTER THE POINT ARE A CONTACT NUMBER, so the day is
        # the count's whole part as written, toward nought.
        whole = abs(numerator) // denominator
        if numerator < 0:
            whole = -whole
        day = found.epoch + whole
        if day < _FIRST_DAY or day > _LAST_DAY:
            return None
        return day * (DAY // settled)
    if member == EXCEL_1900:
        whole = numerator // denominator
        if whole < 1 or whole == _EXCEL_LEAP_SERIAL:
            return None
        start = found.epoch
        if whole < _EXCEL_LEAP_SERIAL:
            start = _EXCEL_EARLY_EPOCH
        day = start + whole
        rest = numerator - whole * denominator
        moment = day * (DAY // settled) + _rounded(rest * DAY, denominator * settled)
    else:
        moment = found.epoch * (DAY // settled) + _rounded(
            numerator * found.unit, denominator * settled
        )
    first = _FIRST_DAY * (DAY // settled)
    last = (_LAST_DAY + 1) * (DAY // settled)
    if moment < first or moment >= last:
        return None
    return moment


def contact_word(written: Written) -> str:
    """The contact number a `days-since-1840` cell writes, as written, or `(none)`."""
    if written.fraction:
        return written.fraction
    return NO_CONTACT


def settled_unit(member: str, places: int) -> int:
    """The unit a column's moments are settled to (the design's unit U).

    The finest of `SETTLED_UNITS` that is at least the step the figures
    carry: the member's unit over ten to the ``places`` figures its cells
    write after the point. Whole counts settle to the member's own unit;
    Excel's `%.15g`, ten figures after the point, to the millisecond;
    six figures to the second; four to the minute. A member with
    contacts settles to the day, since its figures after the point are
    no time.

    Guarantees: a function of the two. Raises KeyError for a word outside
    `MEMBERS`. No I/O of any kind.
    """
    found = TABLE[member]
    if found.contacts:
        return DAY
    scale = 10 ** max(0, places)
    if scale > 1 and found.unit >= DAY and DAY > MINUTE * scale:
        # A step past a minute and under a day: settled to the minute.
        return MINUTE
    for unit in SETTLED_UNITS:
        if unit * scale >= found.unit:
            return unit
    return DAY


def written_unit(moments: "list[int]", settled: int) -> int:
    """The coarsest unit every settled moment stands on, of `WRITTEN_UNITS`.

    Asked of the moments in ``settled`` units: a whole date where every
    one is a midnight, a minute where every one is a whole minute, and so
    on down to the settled unit itself.

    Guarantees: a function of the two; returns one of `WRITTEN_UNITS`
    no finer than ``settled``. Raises nothing. No I/O of any kind.
    """
    candidates: "list[int]" = []
    for unit in WRITTEN_UNITS:
        if unit >= settled:
            candidates += [unit]
    for unit in candidates:
        if unit <= settled:
            return unit
        step = unit // settled
        held = True
        for moment in moments:
            if moment % step:
                held = False
                break
        if held:
            return unit
    return candidates[len(candidates) - 1]


def iso_text(moment: int, settled: int, unit: int) -> str:
    """A moment in ``settled`` units, written as ISO text at ``unit``.

    `YYYY-MM-DD` for a whole date, `YYYY-MM-DD HH:MM` for the minute,
    `YYYY-MM-DD HH:MM:SS` for the second, and three, six or nine figures
    of a second after that. Each is a spelling `iso-date` or
    `iso-datetime` reads at exactly that precision, which is what lets
    the datetime role describe a column of counts as dates.

    The moment is first settled to ``unit``, rounding halves to even,
    where ``unit`` is the coarser: that is the validator reading a file
    at the precision its description published.

    Guarantees: accepts a moment, its unit and the unit to write;
    returns the text. Determinism: whole-number arithmetic. Raises
    nothing for a moment inside 0001-01-01 to 9999-12-31. No I/O.
    """
    nanos = moment * settled
    if unit > settled:
        nanos = _rounded(nanos, unit) * unit
    day = nanos // DAY
    year, month, date = parsing.civil_from_days(day)
    written = f"{year:04d}-{month:02d}-{date:02d}"
    if unit >= DAY:
        return written
    rest = nanos - day * DAY
    hours = rest // HOUR
    minutes = (rest // MINUTE) % 60
    written = f"{written} {hours:02d}:{minutes:02d}"
    if unit >= MINUTE:
        return written
    seconds = (rest // SECOND) % 60
    written = f"{written}:{seconds:02d}"
    if unit >= SECOND:
        return written
    figures = _SUBSECOND_FIGURES[unit]
    part = (rest % SECOND) // unit
    return f"{written}.{part:0{figures}d}"


def moment_of_iso(text: str, unit: int) -> "int | None":
    """An ISO text a twin writes, read as a whole number of ``unit`` from 1970.

    The inverse of `iso_text` over the spellings `iso-date` and
    `iso-datetime` read: a date, or a date, one space or `T`, and a clock
    to the minute or the second with up to nine figures of a second. The
    moment is settled to ``unit``, halves to even. None for any other
    text.

    Guarantees: a function of the two. Raises TypeError where the text is
    not text. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a cell was not text")
    if len(text) < 10 or text[4:5] != "-" or text[7:8] != "-":
        return None
    year_text = text[0:4]
    month_text = text[5:7]
    date_text = text[8:10]
    if not (_figures(year_text) and _figures(month_text) and _figures(date_text)):
        return None
    year = int(year_text)
    month = int(month_text)
    date = int(date_text)
    if not parsing.valid_date(year, month, date):
        return None
    nanos = _day(year, month, date) * DAY
    clock = text[10:]
    if clock:
        if clock[:1] not in (" ", "T") or len(clock) < 6 or clock[3:4] != ":":
            return None
        hours_text = clock[1:3]
        minutes_text = clock[4:6]
        if not (_figures(hours_text) and _figures(minutes_text)):
            return None
        nanos = nanos + int(hours_text) * HOUR + int(minutes_text) * MINUTE
        rest = clock[6:]
        if rest:
            if rest[:1] != ":" or not _figures(rest[1:3]):
                return None
            nanos = nanos + int(rest[1:3]) * SECOND
            part = rest[3:]
            if part:
                digits = part[1:]
                if part[:1] != "." or not _figures(digits) or len(digits) > 9:
                    return None
                nanos = nanos + int(digits) * 10 ** (9 - len(digits))
    return _rounded(nanos, unit)


# ------------------------------------------------------------- writing


@dataclasses.dataclass(frozen=True)
class CountForm:
    """How a column of counted dates writes its numbers (`count_form`).

    * `places` -- the most figures after the mark any cell writes, 0 to
      17;
    * `trimmed` -- whether cells drop the zeros at the end of their
      figures after the mark, and the mark with them, as `%g`, `repr`
      and R do, rather than always writing `places` of them as `%.6f`
      and pandas' `45000.0` do;
    * `significant` -- 15 or 17 where each cell is written to that many
      significant figures and trimmed (`%.15g`, `repr`), so a column
      crossing serial 10,000 writes one figure fewer after the point on
      the far side (the R4 design review, item 7); `None` otherwise;
    * `exponent` -- whether a cell is written in exponent form where that
      is shorter, as R writes a whole number of milliseconds;
    * `mark` -- the decimal mark, a point or a comma;
    * `contacts` -- `days-since-1840` alone: how many cells write each
      contact number, floored, or `None` where no cell writes one.
    """

    places: int
    trimmed: bool
    significant: "int | None"
    exponent: bool
    mark: str
    contacts: "dict[str, int] | None"


def _pow10_exponent(numerator: int, denominator: int) -> int:
    """The power of ten of a positive rational's leading figure: 10**e <= x < 10**(e+1)."""
    exponent = len(str(numerator)) - len(str(denominator))
    if exponent >= 0:
        if numerator < denominator * 10**exponent:
            exponent = exponent - 1
    elif numerator * 10 ** (-exponent) < denominator:
        exponent = exponent - 1
    return exponent


def _fixed_figures(numerator: int, denominator: int, places: int) -> "tuple[bool, str, str]":
    """A rational rounded to ``places`` figures after the point: (negative, whole, fraction)."""
    negative = numerator < 0
    scaled = _rounded(abs(numerator) * 10**places, denominator)
    if scaled == 0:
        negative = False
    if places:
        figures = f"{scaled:0{places + 1}d}"
        return negative, figures[: len(figures) - places], figures[len(figures) - places :]
    return negative, f"{scaled}", ""


def _significant_figures(
    numerator: int, denominator: int, figures: int
) -> "tuple[bool, str, int]":
    """A rational rounded to ``figures`` significant figures: (negative, digits, exponent).

    The value is `0.digits` read with its point after the first figure,
    times ten to the exponent, its digits trimmed of trailing zeros.
    """
    negative = numerator < 0
    magnitude = abs(numerator)
    if magnitude == 0:
        return False, "0", 0
    exponent = _pow10_exponent(magnitude, denominator)
    shift = figures - 1 - exponent
    if shift >= 0:
        digits = _rounded(magnitude * 10**shift, denominator)
    else:
        digits = _rounded(magnitude, denominator * 10 ** (-shift))
    if digits >= 10**figures:
        exponent = exponent + 1
        digits = digits // 10
    while digits >= 10 and digits % 10 == 0:
        digits = digits // 10
    return negative, f"{digits}", exponent


def _spelled_number(
    negative: bool, whole: str, fraction: str, mark: str
) -> str:
    """A number from its parts, the mark between them only where a fraction stands."""
    sign = "-" if negative else ""
    if fraction:
        return f"{sign}{whole}{mark}{fraction}"
    return f"{sign}{whole}"


def _trimmed_fraction(fraction: str) -> str:
    """The figures after the mark with the zeros at their end taken off."""
    if not isinstance(fraction, str):
        raise TypeError("internal check: figures were not text")
    return fraction.rstrip("0")


def spelled_count(numerator: int, denominator: int, form: CountForm) -> str:
    """A count written the way the column writes its counts (`count_form`).

    THE INVERSE OF THE READING, by the form the column published:

    * fixed -- rounded, halves to even, to `places` figures after the
      mark, every one written;
    * trimmed -- the same, with the zeros at the end and then a bare mark
      taken off;
    * significant -- rounded to `significant` figures and trimmed, the
      number written in full (Excel's `%.15g` and `repr` write no
      exponent below 10**15);
    * exponent -- R's own rule: fifteen significant figures, written in
      exponent form where that is SHORTER than written in full, and in
      full where the two are as long.

    A COUNT THAT IS NOT WHOLE IS WRITTEN AS AN EXPORTER WRITES IT: the
    binary64 nearest it, formatted to the form's places or significant
    figures -- `%.6f`, `%.15g`, `repr`, R's fifteen figures -- which is
    the text a spreadsheet, Python or R writes for that moment. Rounding
    the exact count instead differs from those writers in the last figure
    where the exact count stands within a binary64 step of a rounding
    boundary, which a source written by any of them does on about one
    cell in seventy (measured on `%.15g` serials at whole seconds over
    1920 to 2025). A whole count is written from its figures, so a count
    past 2**53 keeps every one.

    Guarantees: accepts the exact count and the form; returns its text.
    Determinism: correctly rounded binary64 arithmetic and formatting,
    the same on every platform. Raises nothing. No I/O.
    """
    if numerator % denominator:
        return _spelled_inexact(numerator, denominator, form)
    return _spelled_exact(numerator, denominator, form)


def _spelled_exact(numerator: int, denominator: int, form: CountForm) -> str:
    """A count written from its exact value, rounded halves to even: a whole count's own path."""
    if form.significant is not None or form.exponent:
        figures = form.significant if form.significant is not None else 15
        negative, digits, exponent = _significant_figures(
            numerator, denominator, figures
        )
        if digits == "0":
            return "0"
        if exponent >= len(digits) - 1:
            full = _spelled_number(
                negative, digits + "0" * (exponent - len(digits) + 1), "", form.mark
            )
        elif exponent >= 0:
            full = _spelled_number(
                negative, digits[: exponent + 1], digits[exponent + 1 :], form.mark
            )
        else:
            full = _spelled_number(
                negative, "0", "0" * (-exponent - 1) + digits, form.mark
            )
        if not form.exponent:
            return full
        sign = "-" if negative else ""
        mantissa = digits[:1]
        if len(digits) > 1:
            mantissa = f"{mantissa}{form.mark}{digits[1:]}"
        direction = "+" if exponent >= 0 else "-"
        scientific = f"{sign}{mantissa}e{direction}{abs(exponent):02d}"
        if len(scientific) < len(full):
            return scientific
        return full
    negative, whole, fraction = _fixed_figures(numerator, denominator, form.places)
    if form.trimmed:
        fraction = _trimmed_fraction(fraction)
    return _spelled_number(negative, whole, fraction, form.mark)


def _spelled_inexact(numerator: int, denominator: int, form: CountForm) -> str:
    """A count that is not whole, as the binary64 nearest it is written by the form."""
    value = numerator / denominator
    if form.significant is not None or form.exponent:
        figures = form.significant if form.significant is not None else 15
        if figures == 17 and not form.exponent:
            # `repr`: the fewest figures that read back as this binary64.
            text = repr(value)
            if "e" not in text and "E" not in text:
                return _with_mark(text, form.mark)
        scientific = f"{value:.{figures - 1}e}"
        cut = _place_of(scientific, "e")
        mantissa = scientific[:cut]
        exponent = int(scientific[cut + 1 :])
        negative = mantissa[:1] == "-"
        digits = ""
        for letter in mantissa:
            if "0" <= letter <= "9":
                digits = digits + letter
        while len(digits) > 1 and digits[len(digits) - 1 :] == "0":
            digits = digits[: len(digits) - 1]
        sign = "-" if negative else ""
        if exponent >= len(digits) - 1:
            full = f"{sign}{digits}{'0' * (exponent - len(digits) + 1)}"
        elif exponent >= 0:
            full = f"{sign}{digits[: exponent + 1]}{form.mark}{digits[exponent + 1 :]}"
        else:
            full = f"{sign}0{form.mark}{'0' * (-exponent - 1)}{digits}"
        if not form.exponent:
            return full
        shown = digits[:1]
        if len(digits) > 1:
            shown = f"{shown}{form.mark}{digits[1:]}"
        direction = "+" if exponent >= 0 else "-"
        short = f"{sign}{shown}e{direction}{abs(exponent):02d}"
        return short if len(short) < len(full) else full
    text = f"{value:.{form.places}f}"
    if form.trimmed and form.places:
        text = _trimmed_number(text)
    return _with_mark(text, form.mark)


def _trimmed_number(text: str) -> str:
    """A fixed spelling with the zeros after its point, and then a bare point, taken off."""
    if not isinstance(text, str):
        raise TypeError("internal check: a number was not text")
    if _place_of(text, ".") < 0:
        return text
    return text.rstrip("0").rstrip(".")


def _with_mark(text: str, mark: str) -> str:
    """A spelling written with a point, written with the column's own mark."""
    if not isinstance(text, str):
        raise TypeError("internal check: a number was not text")
    if not isinstance(mark, str):
        raise TypeError("internal check: a mark was not text")
    if mark == POINT:
        return text
    return text.replace(POINT, mark)


def count_of(member: str, moment: int, unit: int) -> "tuple[int, int] | None":
    """The exact count a member writes for a moment, as a numerator and denominator.

    The inverse of `moment_of`: ``moment`` whole ``unit`` from the start
    of 1 January 1970. A spreadsheet serial counts its whole days by
    Excel's own leap rule. None where the member writes no count for the
    moment -- a spreadsheet date before its first day. A member with
    contacts counts the day alone.

    Guarantees: a function of the three. Raises KeyError for a word
    outside `MEMBERS`. No I/O of any kind.
    """
    found = TABLE[member]
    nanos = moment * unit
    if found.contacts:
        return nanos // DAY - found.epoch, 1
    if member == EXCEL_1900:
        day = nanos // DAY
        rest = nanos - day * DAY
        if day < _EXCEL_EARLY_EPOCH + 1:
            return None
        whole = day - found.epoch
        if day < _EXCEL_FIRST_MARCH:
            whole = day - _EXCEL_EARLY_EPOCH
        return whole * DAY + rest, DAY
    offset = nanos - found.epoch * DAY
    if offset < 0 and not found.signed:
        return None
    return offset, found.unit


def written_for(
    member: str, moment: int, unit: int, form: CountForm, contact: str = NO_CONTACT
) -> "str | None":
    """The cell a twin writes for a moment: the member's count, spelled by the form.

    A member with contacts writes its day count, then the mark and the
    contact number as the census spells it, or no mark where the word is
    `(none)`. None where the member writes no count for the moment.

    Guarantees: a function of its arguments. Raises KeyError for a word
    outside `MEMBERS`. No I/O of any kind.
    """
    found = count_of(member, moment, unit)
    if found is None:
        return None
    numerator, denominator = found
    if TABLE[member].contacts:
        text = f"{numerator}"
        if contact != NO_CONTACT:
            text = f"{text}{form.mark}{contact}"
        return text
    return spelled_count(numerator, denominator, form)


# ------------------------------------------------- the column's form


def form_from(
    tally: Tally, mark: str, contacts: "dict[str, int] | None"
) -> CountForm:
    """The `count_form` a column's written counts publish, from their tally.

    `places` is the most figures after the mark any cell's number
    carries. A column is FIXED where every cell writes exactly that many
    (and at least one), and TRIMMED otherwise. A trimmed column whose
    cells reach fifteen significant figures -- sixteen or seventeen --
    is written to fifteen (seventeen): `%.15g` and `repr` write by
    significance, not by places, so a column crossing a power of ten
    writes one figure fewer after the point beyond it (the R4 design
    review, item 7). A column holding an exponent form is written by R's
    own rule, at fifteen significant figures. A `days-since-1840` column
    publishes its census of contact numbers, and its places are the
    longest contact number's.

    Guarantees: a function of the three. Raises nothing. No I/O.
    """
    if contacts is not None:
        places = 0
        for word in contacts:
            if word != NO_CONTACT:
                places = max(places, len(word))
        return CountForm(places, False, None, False, mark, contacts)
    places = min(tally.places, 17)
    if tally.exponent:
        return CountForm(places, True, 15, True, mark, None)
    fixed = tally.places > 0 and tally.least == tally.places
    significant: "int | None" = None
    if not fixed and tally.places > 0 and 15 <= tally.significant <= 17:
        significant = 15 if tally.significant == 15 else 17
    return CountForm(places, not fixed and tally.places > 0, significant, False, mark, None)


def form_of(
    cells: "list[Written]", mark: str, contacts: "dict[str, int] | None"
) -> CountForm:
    """`form_from` over every counted cell of a column, read."""
    tally = Tally()
    for written in cells:
        tally = tallied(tally, written)
    return form_from(tally, mark, contacts)


def reading_unit(member: str, form: CountForm, tally: Tally) -> int:
    """The unit a column's counts are settled to, from how they are written (the design's unit U).

    `settled_unit` at the figures after the point the LEAST precise cell
    can write: a form by places writes `places` of them everywhere, and a
    form by significant figures writes fewer where the whole part is
    longer -- `%.15g` writes ten after the point on a serial of five
    figures and eleven on one of four, so a column crossing serial 10,000
    is settled at ten, to the millisecond, and its four-figure cells' last
    figure is not read as a microsecond nobody wrote.

    Guarantees: a function of the three. Raises KeyError for a word
    outside `MEMBERS`. No I/O of any kind.
    """
    places = form.places
    if form.significant is not None:
        places = max(0, form.significant - tally.whole)
    return settled_unit(member, places)


def form_holds(form: CountForm, written: Written) -> bool:
    """Whether a cell is one the published form can write (validation, CD).

    A fixed form writes exactly `places` figures after the mark; a
    trimmed one at most `places`, none of them a trailing zero; a
    significant one at most `significant` significant figures, trimmed;
    an exponent form fifteen significant figures, either written in full
    or in exponent form. A member with contacts writes its day count and
    a contact word the census names.
    """
    if form.contacts is not None:
        if written.exponent_form:
            return False
        word = contact_word(written)
        return word in form.contacts
    if written.exponent_form and not form.exponent:
        return False
    if form.exponent:
        return significant_figures(written) <= 15 and written.fraction[-1:] != "0"
    if form.significant is not None:
        return (
            significant_figures(written) <= form.significant
            and written.fraction[-1:] != "0"
        )
    if form.trimmed:
        return len(written.fraction) <= form.places and written.fraction[-1:] != "0"
    return len(written.fraction) == form.places


# ------------------------------------------------- what is set aside

# THE NUMBERS A COUNT WRITES WHERE NO DATE WAS GIVEN (the R4 design
# review, item 1): nought and minus one, which a database writes for "not
# set", each member's own count for 1 January 1900 and 31 December 9999,
# the placeholder days the date role already knows
# (`parsing.CALENDAR_PLACEHOLDERS`), and the spreadsheet's 0, 1 and 60 --
# the serial an empty date formula shows, its first day, and the 29
# February 1900 it counts and no calendar has. They are SET ASIDE before
# a column is asked about, so one stray cell does not silence the
# question, and under a declaration each is read as no date and written
# back as written.


def set_aside_named(member: str) -> "tuple[tuple[int, str], ...]":
    """The whole counts a member's column sets aside, each with its word.

    Nought (`0`) and minus one (`-1`), which a database writes for "not
    set"; the member's count for each placeholder day (`1900-01-01`,
    `9999-12-31`) -- by its own rule and by the plain arithmetic an
    exporter writes it with from the member's epoch, which differ only
    before March 1900 on Excel's 1900 system (serial 1 by Excel's rule,
    2 from 30 December 1899) and before 1904 on its 1904 system, where
    the count is below nought; and Excel's day 60 (`60`), the 29
    February 1900 the 1900 system counts. The words are this package's
    own: a question may name them, and no cell stands behind one.

    Guarantees: a function of the word, in rising order of the counts.
    Raises KeyError for a word outside `MEMBERS`. No I/O of any kind.
    """
    found = TABLE[member]
    named: "dict[int, str]" = {0: "0", -1: "-1"}
    for year, month, date in ((1900, 1, 1), (9999, 12, 31)):
        word = f"{year:04d}-{month:02d}-{date:02d}"
        day = _day(year, month, date)
        counted = count_of(member, day, DAY)
        if counted is not None:
            numerator, denominator = counted
            if numerator % denominator == 0:
                named[numerator // denominator] = word
        plain = (day - found.epoch) * DAY
        if plain % found.unit == 0:
            named[plain // found.unit] = word
    if member == EXCEL_1900:
        named[_EXCEL_LEAP_SERIAL] = "60"
    return tuple((number, named[number]) for number in sorted(named))


def set_aside(member: str) -> "tuple[int, ...]":
    """The whole counts a member's column sets aside, in rising order (`set_aside_named`)."""
    return tuple(number for number, _word in set_aside_named(member))


def declared_aside(member: str) -> "tuple[int, ...]":
    """The set-aside counts a DECLARED column reads as no value: its placeholder days alone.

    Under a declaration a count that names no date -- Excel's 0 and 60, a
    count below a spreadsheet's first day, one past 9999-12-31 -- is no
    value whatever it is, and so is the member's count for 1 January 1900
    or 31 December 9999, by its own rule or by plain epoch arithmetic. But
    nought and minus one NAME DATES in every member that reads them -- 1
    January 1960 and 1970 and the days before -- and a column of births
    holds those days as births: they are read as the dates they name, and
    a person who means "not set" by them says so with `--missing-value`.
    Asked about, the column sets them aside as well (`set_aside`), so one
    stray placeholder silences no question.

    Guarantees: a function of the word, in rising order. Raises KeyError
    for a word outside `MEMBERS`. No I/O of any kind.
    """
    placeholders = (_word_of_day(1900, 1, 1), _word_of_day(9999, 12, 31))
    return tuple(
        number for number, word in set_aside_named(member) if word in placeholders
    )


def _word_of_day(year: int, month: int, date: int) -> str:
    """A day's ISO word, as `set_aside_named` names it."""
    return f"{year:04d}-{month:02d}-{date:02d}"


def is_set_aside(member: str, written: Written, kept: "tuple[int, ...]" = ()) -> bool:
    """Whether a cell holds one of the member's set-aside numbers.

    Exactly: `0.0` is nought and `60.5` is not sixty. A member with
    contacts asks the figures before the point alone, the day they name.
    A number the person named with `--keep-value` (``kept``) is never set
    aside.
    """
    numerator, denominator = exact_value(written)
    if TABLE[member].contacts:
        whole = abs(numerator) // denominator
        numerator = -whole if numerator < 0 else whole
        denominator = 1
    if numerator % denominator:
        return False
    number = numerator // denominator
    if number in kept:
        return False
    return number in set_aside(member)


# -------------------------------------------- question Q3, the bands

# THE NARROW BAND (rule A): a column whose counts all name a moment from
# 1 January 1990 up to, and not including, 1 January 2051. Starting in
# 1990 keeps every ordinary column of the measured battery out of it --
# 6 of 2,304 measurement draws fell in a band from 1990, each already
# asked as a fixed-width column, and none from 2000 -- where a band from
# 1970 held 1,917 of 1,920.
NARROW_FROM = 1990
WIDE_FROM = 1900
BAND_UNTIL = 2051

# How much of a column may stand outside the question's rules: the rest
# beside the set-aside numbers must be at least nine tenths of the
# present cells and at least eleven, and at most one cell in a thousand
# -- one at least -- may lie outside the band (the R4 design review,
# item 1). Text cells may stand to the date role's own line.
REST_SHARE_NUM = 9
REST_SHARE_DEN = 10
REST_LEAST = 11
STRAY_PER = 1000

RULE_BAND = "inside-a-band"
RULE_MIDNIGHT = "at-midnight"
RULE_FIXED_WIDTH = "fixed-width-days"
RULES = (RULE_BAND, RULE_MIDNIGHT, RULE_FIXED_WIDTH)


def band(member: str, first_year: int) -> "tuple[float, float]":
    """The counts a member writes from 1 January ``first_year`` to before 1 January 2051.

    As two numbers to compare a column's own numbers with: the count of
    the band's first moment and of its end. Guarantees: a function of the
    two. Raises KeyError for a word outside `MEMBERS`. No I/O.
    """
    found = TABLE[member]
    edges: "list[float]" = []
    for year in (first_year, BAND_UNTIL):
        day = _day(year, 1, 1)
        if member == EXCEL_1900 and day < _EXCEL_FIRST_MARCH:
            edges += [float(day - _EXCEL_EARLY_EPOCH)]
            continue
        edges += [(day - found.epoch) * (DAY // found.unit) * 1.0]
    return edges[0], edges[1]


def _in_band(ordered: "list[float]", low: float, high: float) -> int:
    """How many values of a rising list lie in [low, high)."""
    return _first_at_least(ordered, high) - _first_at_least(ordered, low)


def _first_at_least(ordered: "list[float]", value: float) -> int:
    """The first place of a rising list holding a value at least ``value``."""
    low = 0
    high = len(ordered)
    while low < high:
        middle = (low + high) // 2
        if ordered[middle] < value:
            low = middle + 1
        else:
            high = middle
    return low


def _count_of_value(ordered: "list[float]", value: float) -> int:
    """How many values of a rising list equal ``value``."""
    return _first_past(ordered, value) - _first_at_least(ordered, value)


def _first_past(ordered: "list[float]", value: float) -> int:
    """The first place of a rising list holding a value above ``value``."""
    low = 0
    high = len(ordered)
    while low < high:
        middle = (low + high) // 2
        if ordered[middle] <= value:
            low = middle + 1
        else:
            high = middle
    return low


@dataclasses.dataclass(frozen=True)
class Asked:
    """Why a column of numbers is worth asking whether it holds dates (Q3).

    `rule` is one of `RULES`; `members` the members offered, in the
    table's order, each of the same unit as a member the rule fired on
    and each reading the column inside 1900 to 2050; `set_aside` which
    of the set-aside numbers the column holds -- words of this package's
    own (`0`, `-1`, `1900-01-01`, `9999-12-31`, `60`), never a cell.
    """

    rule: str
    members: "tuple[str, ...]"
    set_aside: "tuple[str, ...]"


def _rest_is_enough(rest: int, present: int) -> bool:
    """The rest beside the set-aside numbers is nine tenths of the present cells, and eleven."""
    return rest >= REST_LEAST and rest * REST_SHARE_DEN >= present * REST_SHARE_NUM


def _strays_allowed(present: int) -> int:
    """How many of the rest may lie outside the band: one in a thousand, one at least."""
    return max(1, present // STRAY_PER)


def fixed_width(present: "list[str]") -> int:
    """The one width every cell is written in, as figures alone, or 0.

    Today's fixed-width question, as `asking.why_worth_asking` asks it: no
    cell padded with a leading zero, every cell ASCII figures and nothing
    else, all one width. Guarantees: a function of the cells. Raises
    nothing. No I/O.
    """
    width = 0
    for text in present:
        if not _figures(text) or (len(text) > 1 and text[:1] == "0"):
            return 0
        if width and len(text) != width:
            return 0
        width = len(text)
    return width


def _may_be_asked(
    numbers: "list[float]", median: "float | None", whole: bool
) -> "list[tuple[str, str]]":
    """The members a column's own published median and residues leave open.

    THE CHEAP HALF, asked before anything is sorted, so an ordinary column
    pays a lookup: a column that satisfies rule A has nine tenths of its
    numbers inside the member's narrow band, so its median is inside it;
    rule B reads whole numbers only, every one beside the set-aside ones
    at midnight UTC, which the walk refuses at the first that is not; and
    rule C reads a column already asked as fixed-width figures of at least
    five, whose median then stands at ten thousand or more.
    """
    open_to: "list[tuple[str, str]]" = []
    if median is None:
        return [(member, RULE_BAND) for member in MEMBERS]
    for member in MEMBERS:
        low, high = band(member, NARROW_FROM)
        if low <= median < high:
            open_to += [(member, RULE_BAND)]
    if whole:
        for member in MEMBERS:
            found = TABLE[member]
            if found.unit >= DAY:
                continue
            per_day = float(DAY // found.unit)
            aside: "dict[float, int]" = {}
            for number in set_aside(member):
                aside[float(number)] = 1
            held = True
            for value in numbers:
                if value in aside:
                    continue
                if value % per_day:
                    held = False
                    break
            if held:
                open_to += [(member, RULE_MIDNIGHT)]
    if median >= 10000:
        for member in MEMBERS:
            if TABLE[member].unit < DAY:
                continue
            low, high = band(member, WIDE_FROM)
            if low <= median < high:
                open_to += [(member, RULE_FIXED_WIDTH)]
    return open_to


def asked_of(
    present: "list[str]",
    numbers: "list[float]",
    needed: int,
    median: "float | None" = None,
    whole: bool = False,
    mark: str = POINT,
) -> "Asked | None":
    """Whether a column of numbers is worth asking about as dates (question Q3).

    THREE RULES, each over the column's present cells with each member's
    set-aside numbers taken out first (`set_aside`), the rest at least
    nine tenths of the present cells and at least eleven:

    * A -- every one of the rest is a count written by the grammar
      (`written_count`), at most one in a thousand of them (one at
      least) lies outside the member's band from 1990, and the whole
      figures of those inside it are all written with one number of
      figures: a column of record numbers spread over two widths is not
      asked about, where a column of moments in one decade is (the R4
      design review, item 5);
    * B -- whole counts of a member finer than the day, every one of the
      rest at midnight UTC, at least eleven different, inside the band
      from 1900, one in a thousand at most outside it: a date kept as an
      instant (narrowed to midnight UTC, item 3 of that review: a date
      kept at LOCAL midnight comes back as instants and is a stated
      limit);
    * C -- the column is asked already as a column of figures all one
      width, at least five (`fixed_width`), and a member counting days
      reads every value inside 1900 to 2050: the question offers dates
      as answers beside its own, and asks nothing new.

    TEXT CELLS STAND TO THE DATE ROLE'S LINE: ``needed`` cells of the
    present ones must be counts. ``numbers`` are the column's own numbers
    as the numeric role read them, which the bands are asked of; the
    grammar asks the text. ``median`` is the block's own published median
    and ``whole`` whether every number is whole, which let an ordinary
    column be answered before anything is sorted (`_may_be_asked`).
    ``mark`` is the column's decimal mark: a column declared
    `--decimal-comma` writes its counts `45386,5`, and the grammar reads
    them with the comma (the R4 design review, item 8).

    THE ANSWERS (item 2 of that review): every member counting in the
    unit of a member a rule fired on and reading the column inside 1900
    to 2050, so a column of SAS days from 1985 is offered the 1960
    member it is written in beside the 1970 one.

    Guarantees: accepts the present cells as text, their numbers, the
    cells the date role's line needs, the median and whether every number
    is whole; returns `Asked` or None. Determinism: a function of the
    five. Raises nothing. No I/O of any kind.
    """
    total = len(present)
    if total < REST_LEAST or len(numbers) < needed:
        return None
    open_to = _may_be_asked(numbers, median, whole)
    if not open_to:
        return None
    ordered = sorted(numbers)
    held: "list[tuple[str, str]]" = []
    for member, rule in open_to:
        if rule != RULE_BAND:
            continue
        rest = len(ordered) - _aside_in(ordered, member)
        if not _rest_is_enough(rest, total):
            continue
        low, high = band(member, NARROW_FROM)
        inside = _in_band(ordered, low, high) - _aside_inside(ordered, member, low, high)
        if rest - inside <= _strays_allowed(total):
            held += [(member, RULE_BAND)]
    if not held:
        for member, rule in open_to:
            if rule != RULE_MIDNIGHT:
                continue
            rest = len(ordered) - _aside_in(ordered, member)
            if not _rest_is_enough(rest, total):
                continue
            low, high = band(member, WIDE_FROM)
            inside = _in_band(ordered, low, high) - _aside_inside(
                ordered, member, low, high
            )
            if rest - inside <= _strays_allowed(total):
                held += [(member, RULE_MIDNIGHT)]
    if not held:
        for member, rule in open_to:
            if rule != RULE_FIXED_WIDTH:
                continue
            rest = len(ordered) - _aside_in(ordered, member)
            if not _rest_is_enough(rest, total):
                continue
            low, high = band(member, WIDE_FROM)
            inside = _in_band(ordered, low, high) - _aside_inside(
                ordered, member, low, high
            )
            if rest - inside <= _strays_allowed(total):
                held += [(member, RULE_FIXED_WIDTH)]
    if not held:
        return None
    # THE TEXT, ONCE, and only for a column the numbers placed in a band.
    rule = held[0][1]
    kept: "list[str]" = []
    for member, fired in held:
        if _text_holds(present, member, fired, needed, mark):
            kept += [member]
    if not kept:
        return None
    offered = _offered(ordered, kept, total)
    return Asked(rule, offered, _set_aside_words(ordered, kept))


def _aside_in(ordered: "list[float]", member: str) -> int:
    """How many of the numbers are one of the member's set-aside numbers."""
    found = 0
    for number in set_aside(member):
        found = found + _count_of_value(ordered, float(number))
    return found


def _aside_inside(
    ordered: "list[float]", member: str, low: float, high: float
) -> int:
    """How many set-aside numbers lie inside [low, high)."""
    found = 0
    for number in set_aside(member):
        if low <= number < high:
            found = found + _count_of_value(ordered, float(number))
    return found


def _text_holds(
    present: "list[str]", member: str, rule: str, needed: int, mark: str = POINT
) -> bool:
    """The written half of a rule: the grammar, the width, and midnight.

    At least ``needed`` present cells are counts by the grammar (text
    cells stand to the date role's line). For rule A, the whole figures of
    the counts inside the narrow band all have one width; for rule C, every
    count beside the set-aside numbers is whole, and those inside the wide
    band all have one width of at least five figures. NO CELL OF ANOTHER
    WIDTH IS LET STAND, where a stray outside the band is: measured on the
    chance battery, letting one in a thousand stand asked two measurement
    columns that are no fixed width -- the kind of question nothing asked
    before -- and costs one keying slip that lands inside the band at
    another width (`xl_birth` a century early, one seed of three). For
    rule B, every count beside the set-aside numbers is whole and stands
    at midnight UTC, with at least eleven different values.
    """
    found = TABLE[member]
    counted = 0
    widths: "dict[int, int]" = {}
    different: "dict[int, int]" = {}
    low, high = band(member, WIDE_FROM if rule == RULE_FIXED_WIDTH else NARROW_FROM)
    per_day = DAY // found.unit if found.unit < DAY else 1
    aside: "dict[int, int]" = {}
    for number in set_aside(member):
        aside[number] = 1
    for text in present:
        written = written_count(text, mark)
        if written is None:
            continue
        counted = counted + 1
        numerator, denominator = exact_value(written)
        if found.contacts:
            day_part = abs(numerator) // denominator
            if (-day_part if numerator < 0 else day_part) in aside:
                continue
        elif numerator % denominator == 0 and numerator // denominator in aside:
            continue
        if rule == RULE_MIDNIGHT:
            if denominator != 1 or numerator % per_day:
                return False
            if len(different) < REST_LEAST:
                different[numerator] = 1
            continue
        if rule == RULE_FIXED_WIDTH and (written.fraction or written.exponent_form):
            return False
        whole = abs(numerator) // denominator
        if low <= numerator / denominator < high:
            width = len(f"{whole}")
            widths[width] = (widths[width] if width in widths else 0) + 1
    if counted < needed:
        return False
    if rule == RULE_MIDNIGHT:
        return len(different) >= REST_LEAST
    if len(widths) > 1:
        return False
    for width in widths:
        if rule == RULE_FIXED_WIDTH and width < 5:
            return False
    return True


def _offered(
    ordered: "list[float]", hits: "list[str]", total: int
) -> "tuple[str, ...]":
    """Every member counting in a hit's unit that reads the column inside 1900 to 2050."""
    units = {TABLE[member].unit: 1 for member in hits}
    offered: "list[str]" = []
    for member in MEMBERS:
        if member in hits:
            offered += [member]
            continue
        found = TABLE[member]
        if found.unit not in units:
            continue
        rest = len(ordered) - _aside_in(ordered, member)
        if not _rest_is_enough(rest, total):
            continue
        low, high = band(member, WIDE_FROM)
        inside = _in_band(ordered, low, high) - _aside_inside(ordered, member, low, high)
        if rest - inside <= _strays_allowed(total):
            offered += [member]
    return tuple(offered)


# The set-aside numbers a question may name, as words of this package's
# own, in the order a sentence names them.
_ASIDE_WORDS = ("0", "-1", "1900-01-01", "9999-12-31", "60")


def _set_aside_words(ordered: "list[float]", members: "list[str]") -> "tuple[str, ...]":
    """Which of the set-aside numbers the column holds, as this package's own words."""
    seen: "dict[str, int]" = {}
    for member in members:
        for number, word in set_aside_named(member):
            if _count_of_value(ordered, float(number)):
                seen[word] = 1
    return tuple(word for word in _ASIDE_WORDS if word in seen)


def years_of(member: str, value: float) -> "int | None":
    """The year a published edge names read under a member, or None.

    Read as the published binary64 value says it, to the day: the year a
    question or a remark prints beside the member. None where the member
    writes no date there.
    """
    if value != value or value - value != 0:
        return None
    whole = int(value)
    if whole > value:
        whole = whole - 1
    moment = moment_of(member, whole, 1, NANOSECOND)
    if moment is None:
        return None
    return parsing.civil_from_days(moment // DAY)[0]


# ------------------------------------------------- the words of Q3


def listed(words: "tuple[str, ...]") -> str:
    """Words said as one list: `a`, `a or b`, `a, b or c`."""
    said = ""
    for place in range(len(words)):
        if place == 0:
            said = words[place]
        elif place == len(words) - 1:
            said = f"{said} or {words[place]}"
        else:
            said = f"{said}, {words[place]}"
    return said


# WHERE A COLUMN HOLDS NOT ONE OF A SET-ASIDE NUMBER'S KIND: the word NF113
# writes in that number's place.
ASIDE_NONE = "(none set aside)"


def aside_slots(words: "tuple[str, ...]") -> "tuple[str, ...]":
    """NF113's five set-aside places: each number's word where the column holds it, or `ASIDE_NONE`."""
    slots: "tuple[str, ...]" = ()
    for word in _ASIDE_WORDS:
        slots = slots + ((word if word in words else ASIDE_NONE),)
    return slots


# How a sentence names each set-aside number: a placeholder day by the
# count a system writes for it, since no cell holds the day's own text.
_ASIDE_SAID = {
    "0": "0",
    "-1": "-1",
    "1900-01-01": "the count for 1 January 1900",
    "9999-12-31": "the count for 31 December 9999",
    "60": "60",
}


def aside_listed(slots: "tuple[str, ...]") -> str:
    """The set-aside numbers NF113's places name, said as a list, or ""."""
    named: "tuple[str, ...]" = ()
    for word in slots:
        if word in _ASIDE_WORDS:
            named = named + (_ASIDE_SAID[word],)
    return listed(named)


# The words a sentence of question Q3 may carry: the members, the rules,
# the set-aside numbers and the word for none of them, all this package's
# own (contract 4.5.1).
NOTE_WORDS = MEMBERS + RULES + _ASIDE_WORDS + (ASIDE_NONE,)


def rule_said(rule: str) -> str:
    """What NF113 says a rule saw, opening its sentence.

    "NEARLY EVERY", NEVER "EVERY": each rule lets text cells stand to the
    date role's own line, the set-aside numbers stand beside the rest and
    one cell in a thousand stray outside the band, so a sentence saying
    "every" would be false on a column it fires on.
    """
    if rule == RULE_MIDNIGHT:
        return (
            "nearly every value in this column is a whole number standing at "
            "the very start of a day counted in seconds or a finer unit from "
            "a fixed moment, which is how a date from 1900 to 2050 is kept as "
            "an instant at midnight UTC."
        )
    if rule == RULE_FIXED_WIDTH:
        return (
            "nearly every value in this column is written in figures alone, "
            "all one width, and lies where a system counting days from a "
            "fixed day writes a date from 1900 to 2050."
        )
    return (
        "nearly every value in this column is a number, and nearly every one "
        "lies where a system counting days, seconds or a finer unit from a "
        "fixed day writes a date from 1990 to 2050."
    )


def aside_said(slots: "tuple[str, ...]") -> str:
    """What NF113 says of the set-aside numbers a column holds, or nothing."""
    named = aside_listed(slots)
    if not named:
        return ""
    return (
        f" Some cells hold {named}: numbers such a system writes where no "
        f"date was given, or that name no real day. Read as dates, a cell "
        f"naming no date -- a "
        f"spreadsheet's 0, 60 or a number below nought -- or the "
        f"system's own count for 1 January 1900 or 31 December 9999 is "
        f"counted as no value and written back as it is; 0 and -1 name "
        f"a day of 1960 or 1970 in the other systems, and are read as "
        f"that day unless you name them with --missing-value."
    )

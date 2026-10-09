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
date?"). A count is READ EXACTLY, by whole-number arithmetic, so a count
past 2**53 -- nanoseconds since 1970 -- is read from its figures and a
whole one is written back from them; a count that is not whole is
written as the exporter writes it, through the binary64 nearest it
(`spelled_count`).

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
# millisecond, which takes away what binary64 added. A unit at least the
# step is what lets the twin's own cells read back as the moments it
# drew: a column settled finer than its step -- the minute the first
# build kept for one or two figures of a day -- has its twin's moments
# rounded onto the column's coarser grid as they are written, and the
# twin missed its own description (the review of landing R4, item 2).
# WHERE THE UNIT LOSES A FIGURE THE COLUMN WROTE -- the step falls
# between two units, as four figures of a day or one figure of a second
# do, or is coarser than any unit the figures stand on -- the column is
# not read as counted dates at all (`held_by_its_moment`).
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

    THE GRAMMAR OF CONTRACT 6.6.2, and nothing wider: an optional minus,
    then whole figures -- `0` alone or a first figure other than `0`, so
    a padded `007` is a code's spelling and not a count's -- then
    optionally ``mark`` and one or more figures, then, on the point only,
    optionally an exponent: `e` or `E`, an optional sign and figures, the
    form R and Python write a count in where it is shorter (the R4 design
    review, item 6). The whole figures before an exponent are as many as
    the cell writes -- `17e+8` and `1704067200e+0` are counts, which the
    first build refused for writing more than one (the Codex review of
    landing R4, item 8). A leading plus, a grouped number, a space
    anywhere and any other character are not counts. An exponent of more
    than `EXPONENT_FIGURES` figures, its leading zeros aside, is held at
    ten to that many: it names no date either way (`exact_value`).

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
            if not _figures(power):
                return None
            exponent = sign * _bounded_power(power)
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
    return Written(negative, whole, fraction, exponent, exponent_form)


# THE MOST FIGURES AN EXPONENT IS READ TO, its leading zeros aside: ten to
# the millionth is past every date and below every unit, so a longer one
# is held there -- its number names no date either way -- and no cell
# builds a number of its own length (the Codex review of landing R4,
# item 7).
EXPONENT_FIGURES = 6


def _without_leading_noughts(text: str) -> str:
    """Figures with the noughts at their front taken off."""
    if not isinstance(text, str):
        raise TypeError("internal check: figures were not text")
    return text.lstrip("0")


def _noughts_alone(text: str) -> bool:
    """Whether figures are all noughts, or none."""
    if not isinstance(text, str):
        raise TypeError("internal check: figures were not text")
    return not text.strip("0")


def _bounded_power(power: str) -> int:
    """An exponent's figures as a whole number, held at ten to `EXPONENT_FIGURES` where longer."""
    if not isinstance(power, str):
        raise TypeError("internal check: an exponent was not text")
    figures = power.lstrip("0")
    if len(figures) > EXPONENT_FIGURES:
        return int(10**EXPONENT_FIGURES)
    return int(figures) if figures else 0


# THE READINGS A COLUMN OF COUNTS IS DESCRIBED IN once read as dates: each
# count is written as ISO text (`iso_text`), so a cell the source itself
# writes as an ISO date is one the date role reads beside them and one the
# twin, writing every date as a count, would turn into a number.
ISO_READINGS = ("iso-date", "iso-datetime", "iso-mixed")


def written_as_a_date(text: str) -> bool:
    """Whether a cell is a date written as ISO text, which counts read as dates would be read beside.

    THE REPRESENTATION IS PART OF THE DATA (the Codex review of landing
    R4, item 1; the owner's rule of 2026-09-15, every value as the source
    wrote it): a declared column of Excel serials beside cells written
    `2023-06-01` was described as counted dates with no cell unread, its
    twin wrote numbers alone, and code converting every cell with `int()`
    ran on the twin and broke on the real table -- and Epic days carrying
    `.01` beside such cells published a census of contact numbers its
    loader refused (CD4). Such a column is not read as counted dates
    (NF115 says so, and what to do), and question Q3 does not ask about
    it. Guarantees: a function of the text. Raises TypeError where it is
    not text. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a cell was not text")
    for reading in ISO_READINGS:
        if parsing.parse_datetime(text, reading) is not None:
            return True
    return False


# THE MOST FIGURES A CONTACT NUMBER WRITES after the point of an Epic day
# (`days-since-1840`): the census of contact numbers names words of one to
# nine figures (contract 6.6.2), and the description's own publication
# rules take no longer word.
CONTACT_FIGURES = 9


def counted(member: str, text: str, mark: str = POINT) -> "Written | None":
    """A cell read as a count OF ``member``, or None where it is none.

    `written_count`, and on a member whose figures after the point are a
    contact number (`days-since-1840`) also no exponent form and at most
    `CONTACT_FIGURES` figures after the point: an Epic `*_DATE_REAL`
    exported with seventeen significant figures writes `65053.010000000002`,
    which is a day and a binary64's tail, not a day and a contact number,
    and such a cell stands to the date role's own line as text (the review
    of landing R4, item 3). Every reading of a column under a declaration
    and question Q3's walk ask this, so the producer, the generator and
    the checker read the same cells as counts.

    Guarantees: a function of the three. Raises KeyError for a word
    outside `MEMBERS` and TypeError where the text is not text. No I/O.
    """
    written = written_count(text, mark)
    if written is None or not TABLE[member].contacts:
        return written
    if written.exponent_form or len(written.fraction) > CONTACT_FIGURES:
        return None
    return written


# HOW FAR A COUNT IS READ (the Codex review of landing R4, item 7): a number
# of more than `VALUE_FIGURES` whole figures is past the last date of every
# system -- the longest, nanoseconds to 9999, writes twenty-one -- and one
# below ten to minus that many is nearer its epoch than any unit reads; and
# of the figures a cell writes, the first `VALUE_FIGURES` are kept and the
# rest stand as one figure that is nought only where they all are. So no
# cell builds a number of its own length -- `1e+9999` built a 4,456-byte
# integer, kept for every cell, and `45042.` with 4,301 zeros raised
# Python's limit on integer text -- and every reading decides as the exact
# number would: no moment, an epoch, or the same side of each rounding
# boundary.
VALUE_FIGURES = 30


def exact_value(written: Written) -> "tuple[int, int]":
    """The number a written count denotes, as a whole numerator over a power of ten.

    Exact: the figures are read as one whole number and the point and
    the exponent only move the power of ten beneath it. THE REDUNDANT
    FIGURES GO FIRST -- the zeros at the end of the figures after the
    point and those at the front -- and the magnitude is asked before any
    number is built (`VALUE_FIGURES`): a number past every date is held at
    ten to that many, one nearer nought than any unit reads at ten to
    minus one more, and figures past that many stand as one, nought only
    where every one of them is, so each reading decides as the exact
    number would.

    Guarantees: a function of the parts; the denominator is a positive
    power of ten; neither number is longer than about two hundred bits.
    Raises nothing. No I/O.
    """
    fraction = _trimmed_fraction(written.fraction)
    if not written.exponent_form and len(written.whole) + len(fraction) <= VALUE_FIGURES:
        # THE COMMON CELL, short and with no exponent: already in lowest
        # terms over ten once its trailing zeros are gone.
        numerator = int(written.whole + fraction)
        return (-numerator if written.negative else numerator), 10 ** len(fraction)
    digits = _without_leading_noughts(written.whole + fraction)
    if not digits:
        return 0, 1
    shift = len(fraction) - written.exponent
    order = len(digits) - shift
    sign = -1 if written.negative else 1
    if order > VALUE_FIGURES:
        return sign * 10**VALUE_FIGURES, 1
    if order < -VALUE_FIGURES:
        return sign, 10 ** (VALUE_FIGURES + 1)
    if len(digits) > VALUE_FIGURES + 1:
        rest = digits[VALUE_FIGURES:]
        shift = shift - (len(rest) - 1)
        digits = digits[:VALUE_FIGURES] + ("0" if _noughts_alone(rest) else "1")
    while shift > 0 and digits[len(digits) - 1 :] == "0":
        # IN LOWEST TERMS OVER TEN: `31553280000e-2` is the whole 315532800.
        digits = digits[: len(digits) - 1]
        shift = shift - 1
    numerator = int(digits)
    denominator = 1
    if shift >= 0:
        denominator = 10**shift
    else:
        numerator = numerator * 10 ** (-shift)
    return sign * numerator, denominator


def figures_after_the_mark(written: Written) -> int:
    """How many figures after the point the number a cell writes carries.

    The figures written after the mark, less the exponent: `1.6e+12` is a
    whole number and carries none. Guarantees: a function of the parts;
    never below nought. Raises nothing. No I/O.
    """
    return max(0, len(written.fraction) - written.exponent)


def significant_figures(written: Written) -> int:
    """How many significant figures a cell writes: its figures, less the leading zeros.

    AND, WHERE IT WRITES NO FIGURE AFTER THE MARK, LESS THE ZEROS AT THE
    END OF ITS WHOLE FIGURES, which place the point and say nothing of
    how finely the number was written: `1704067200000010000` is
    1.70406720000001e+18 written in full, fifteen figures, as R's rule
    writes it where that is the shorter (the Codex review of landing R4,
    item 3). One rule for the profiler's tally, the writer and the
    checker (`form_holds`).
    """
    figures = _without_leading_noughts(written.whole + written.fraction)
    if not written.fraction:
        figures = _trimmed_fraction(figures)
    return max(1, len(figures))


def integer_figures(written: Written) -> int:
    """How many figures the whole part of a cell's number has: `45386.5` five, `1.6e+12` and `16e+11` thirteen."""
    if written.exponent_form:
        digits = _without_leading_noughts(written.whole + written.fraction)
        if not digits:
            return 1
        return max(1, len(digits) - len(written.fraction) + written.exponent)
    return len(written.whole)


@dataclasses.dataclass(frozen=True)
class Tally:
    """What a column's counts show of how they are written, cell by cell, held as six numbers.

    `places` the most figures after the mark a cell's number carries and
    `least` the fewest; `significant` the most significant figures a cell
    writes; `whole` the most figures a cell's whole part has; `exponent`
    whether a cell writes an exponent form; `cells` how many counts it
    took in. Taken in one walk and nothing kept per cell, so a million
    counts cost six numbers -- or six per number of figures after the
    mark the counts write, where a column is tallied by places
    (`tallied_by_places`).
    """

    places: int = 0
    least: int = -1
    significant: int = 0
    whole: int = 0
    exponent: bool = False
    cells: int = 0


def tallied(tally: Tally, written: Written) -> Tally:
    """One more cell's figures, taken into a tally."""
    figures = figures_after_the_mark(written)
    return Tally(
        max(tally.places, figures),
        figures if tally.least < 0 else min(tally.least, figures),
        max(tally.significant, significant_figures(written)),
        max(tally.whole, integer_figures(written)),
        tally.exponent or written.exponent_form,
        tally.cells + 1,
    )


def tallied_by_places(tallies: "dict[int, Tally]", written: Written) -> None:
    """One more cell's figures, taken into the tally of the counts writing as many figures after the mark.

    ``tallies`` maps figures after the mark to the tally of the counts
    writing that many, and is updated in place: a column's counts cost
    six numbers per number of figures they write, at most eighteen.
    """
    figures = figures_after_the_mark(written)
    tallies[figures] = tallied(tallies[figures] if figures in tallies else Tally(), written)


def merged(one: Tally, other: Tally) -> Tally:
    """Two tallies taken as one."""
    if one.cells == 0:
        return other
    if other.cells == 0:
        return one
    return Tally(
        max(one.places, other.places),
        min(one.least, other.least),
        max(one.significant, other.significant),
        max(one.whole, other.whole),
        one.exponent or other.exponent,
        one.cells + other.cells,
    )


def every_count(tallies: "dict[int, Tally]") -> Tally:
    """The tally of EVERY count of a column, strays included: its tallies by places taken as one.

    The first reading a column is settled by (`usual_tally`): its form,
    unit and figures check from all its counts.

    Guarantees: accepts the tallies by figures after the mark
    (`tallied_by_places`); returns their merged tally. Raises nothing. No
    I/O.
    """
    every = Tally()
    for figures in sorted(tallies):
        every = merged(every, tallies[figures])
    return every


def usual_tally(tallies: "dict[int, Tally]") -> "tuple[Tally, int]":
    """The tally of a column's USUAL counts, and the most figures after the mark they write (or -1).

    A COUNT WRITTEN WITH MORE FIGURES THAN THE REST IS A STRAY (the second
    review of landing R4, item 5): one cell exported to seven or ten
    figures among a thousand written `%.6f` made the column's form one of
    seven figures, the six-figure cells were held to a seven-figure
    tolerance they cannot meet, and question Q3 asked nothing and the
    declaration was refused. So where EVERY count's reading
    (`every_count`) holds no unit, the column's form, its unit and the
    check are taken from the counts written with its usual figures, and
    the counts writing the most figures are set beside them as strays, the
    longest first, while they number at most one in a hundred of the
    counts -- one at least (`STRAY_PER`) -- and the usual ones at least
    nine tenths (`REST_SHARE_NUM`). Each stray is held to its own last
    figure (`settled_reading`), and is not written back as itself: the
    twin writes its moment in the column's usual form.

    EVERY COUNT IS TRIED FIRST (the verification of that repair): where the
    few longer counts are the ones carrying the time of day -- date-times
    mostly at six-hour steps or at midnight, written trimmed (`45123.25`,
    `45123`), the rest at other hours or minutes in full -- the usual
    counts' two figures, or none, settle at the day, the strays name times
    a day cannot hold, and setting them aside refused eight such columns
    that the reading by every count reads at the minute. So a column is
    read as all its counts are written, and its longest counts are strays
    only where that reading holds no unit (`taxonomy._counts_read_as_dates`,
    `figures_kept`).

    Guarantees: accepts the tallies by figures after the mark
    (`tallied_by_places`); returns the merged tally of the usual counts
    and the most figures after the mark a usual count writes, -1 where no
    count is a stray. Raises nothing. No I/O.
    """
    ordered = sorted(tallies)
    total = 0
    for figures in ordered:
        total = total + tallies[figures].cells
    allowed = _strays_allowed(total)
    strays = 0
    keep = len(ordered)
    while keep > 1:
        here = tallies[ordered[keep - 1]].cells
        if strays + here > allowed:
            break
        if (total - strays - here) * REST_SHARE_DEN < total * REST_SHARE_NUM:
            break
        strays = strays + here
        keep = keep - 1
    usual = Tally()
    for figures in ordered[:keep]:
        usual = merged(usual, tallies[figures])
    if keep == len(ordered):
        return usual, -1
    return usual, ordered[keep - 1]


def held_to(plain: "CountForm", usual: int, denominator: int) -> "CountForm":
    """The form one count is held to: its column's, or -- a stray (`usual_tally`) -- its own last figure."""
    if usual < 0 or denominator <= 10**usual:
        return plain
    return CountForm(len(f"{denominator}") - 1, False, None, False, plain.mark, None)


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
    six figures to the second; four to the minute; one to three figures
    of a day, whose step is coarser than a minute, to the day -- so such
    a column keeps its figures only where every count is a whole day, and
    is otherwise not read as counted dates (`held_by_its_moment`). A
    member with contacts settles to the day, since its figures after the
    point are no time.

    Guarantees: a function of the two. Raises KeyError for a word outside
    `MEMBERS`. No I/O of any kind.
    """
    found = TABLE[member]
    if found.contacts:
        return DAY
    scale = 10 ** max(0, places)
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

    * `places` -- the most figures after the mark any count of the
      reading that held writes, 0 to 17: every count's, or -- where that
      reading holds no unit -- the USUAL counts', a stray written with
      more being held to its own last figure and not counted here
      (`every_count`, `usual_tally`);
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
      exponent below 10**15), and a whole count at seventeen written as
      `repr` writes a whole double, `45123.0`;
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


# `repr` WRITES A WHOLE DOUBLE WITH ITS POINT AND A NOUGHT, `45123.0`, up to
# ten to the sixteenth, where it turns to an exponent.
_REPR_WHOLE_BELOW = 10**16


def _spelled_exact(numerator: int, denominator: int, form: CountForm) -> str:
    """A count written from its exact value, rounded halves to even: a whole count's own path."""
    if (
        form.significant == 17
        and not form.exponent
        and numerator % denominator == 0
        and abs(numerator // denominator) < _REPR_WHOLE_BELOW
    ):
        # A WHOLE COUNT IN `repr`'S SEVENTEEN FIGURES -- a date-time at
        # midnight that pandas writes -- keeps `repr`'s `.0`.
        return f"{numerator // denominator}{form.mark}0"
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

    `places` is the most figures after the mark any tallied cell's number
    carries -- every count of the column, or its usual counts where the
    profiler set strays aside, every count's reading holding no unit
    (`every_count`, `usual_tally`). A column is FIXED where every cell writes exactly that many
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


# THE FIGURES A BINARY64 HOLDS FAITHFULLY: any decimal of fifteen
# significant figures reads back as itself through one. `repr` writes
# seventeen where it must, and its last two are the double's own tail.
FAITHFUL_FIGURES = 15


def writer_keeps(member: str, top: int) -> int:
    """The finest settled unit a count below ``top``, written through binary64, reads back at.

    THE WRITER WRITES A COUNT THAT IS NOT WHOLE THROUGH THE BINARY64
    NEAREST IT (`spelled_count`), which stands within half a binary64 step
    of the exact count: below two to the ``bits`` that is two to the
    ``bits - 54`` of the member's unit. A moment drawn at a unit reads
    back as itself only where that is under half the unit, and one bit is
    kept spare for a twin's tail beyond the column's largest count -- so
    the unit is the finest of `SETTLED_UNITS` above two to the
    ``bits - 52`` of the member's unit (the Codex review of landing R4,
    item 2: Excel serials written to fourteen figures were settled to the
    nanosecond, and 999 of 1,000 moments the writer was handed read back
    as another one, 149 ns early). Excel serials of this century keep the
    millisecond, Unix seconds the microsecond, and SPSS seconds -- past
    two to the thirty-third -- the millisecond.

    Guarantees: accepts a member and a bound above every count's
    magnitude; returns one of `SETTLED_UNITS`. Raises KeyError for a word
    outside `MEMBERS`. No I/O of any kind.
    """
    found = TABLE[member]
    bits = 0
    rest = max(1, top)
    while rest:
        rest = rest // 2
        bits = bits + 1
    for unit in SETTLED_UNITS:
        if unit * 2**52 > found.unit * 2**bits:
            return unit
    return DAY


def count_top(counts: "list[tuple[int, int]]") -> int:
    """One more than the largest whole part of any count's magnitude: the bound `writer_keeps` asks."""
    top = 0
    for numerator, denominator in counts:
        top = max(top, abs(numerator) // denominator + 1)
    return top


def reading_units(member: str, form: CountForm, tally: Tally, top: int = 0) -> "tuple[int, ...]":
    """The units a column's counts may be settled to, coarsest first.

    One, `reading_unit`, for every form but `repr`'s seventeen significant
    figures, whose last two figures are the double's tail and not the
    exporter's step: such a column is tried first at the unit fifteen
    figures carry (`FAITHFUL_FIGURES`) and then at each finer one down to
    `reading_unit`'s, and is settled at the first that holds every figure
    (`held_by_its_moment`) -- a pandas column of Excel serials at whole
    seconds at the second, where the double's tail moved some cells by a
    microsecond, and Unix seconds Python wrote to the microsecond at the
    microsecond.

    NO UNIT FINER THAN THE WRITER KEEPS (`writer_keeps`, the Codex review
    of landing R4, item 2): where some count is not whole, ``top`` -- one
    more than the largest count's whole part (`count_top`) -- bounds what
    binary64 holds, and each unit finer than the one it keeps is taken to
    that one, so a column whose figures are finer than any moment the
    twin could write back is read at the finest it can, and held there or
    not read at all.

    Guarantees: a function of the four, each a member of `SETTLED_UNITS`,
    coarsest first. Raises KeyError for a word outside `MEMBERS`. No I/O.
    """
    finest = reading_unit(member, form, tally)
    units: "list[int]" = [finest]
    if form.significant == 17:
        coarsest = settled_unit(member, max(0, FAITHFUL_FIGURES - tally.whole))
        units = []
        for unit in WRITTEN_UNITS:
            # `WRITTEN_UNITS` are `SETTLED_UNITS`, coarsest first.
            if finest <= unit <= coarsest:
                units += [unit]
    if top <= 0 or tally.places == 0 or TABLE[member].contacts:
        return tuple(units)
    kept = writer_keeps(member, top)
    taken: "list[int]" = []
    for unit in units:
        held = max(unit, kept)
        if held not in taken:
            taken += [held]
    return tuple(taken)


# HOW FAR AN EXPORTER'S OWN ARITHMETIC MAY MOVE A COUNT, in binary64 steps
# of the count: a spreadsheet adds a day and a time of day, and pandas
# divides two large integers, each rounding once or twice, so the figures
# an exporter wrote may stand a few such steps from the exact count of
# the moment it meant.
EXPORTER_STEPS = 4


def _last_figure(form: CountForm, numerator: int, denominator: int) -> "tuple[int, int]":
    """The value of one unit in the last figure a form rounds a count to, as a fraction."""
    if form.significant is not None or form.exponent:
        figures = form.significant if form.significant is not None else 15
        if numerator == 0:
            return 1, 10**figures
        shift = _pow10_exponent(abs(numerator), denominator) - figures + 1
        if shift >= 0:
            return 10**shift, 1
        return 1, 10 ** (-shift)
    return 1, 10**form.places


def held_by_its_moment(
    member: str, form: CountForm, numerator: int, denominator: int, moment: int, unit: int
) -> bool:
    """Whether a count is its column's own writing of the moment it was read as.

    THE FIGURES A COLUMN WROTE ARE KEPT (the review of landing R4, item
    2): the moment a count is settled to -- ``moment``, in whole ``unit``
    -- is the one its exporter meant only where the count stands within
    half of the form's last figure of that moment's exact count, and a
    few binary64 steps more (`EXPORTER_STEPS`), which is what rounding to
    the form's figures and the exporter's own arithmetic leave. A column
    of Unix seconds written with tenths, settled to the second, has
    counts half a second from their moments; four figures of a day of
    moments off the whole minute, settled to the minute, have counts
    thirty seconds from theirs; neither is held, and such a column is not
    read as counted dates. A member with contacts holds the day alone,
    its figures after the point being no time.

    Guarantees: accepts the member, the column's form, the exact count
    and the moment it was settled to; returns whether it holds.
    Determinism: whole-number arithmetic. Raises KeyError for a word
    outside `MEMBERS`. No I/O of any kind.
    """
    found = count_of(member, moment, unit)
    if found is None:
        return False
    top, bottom = found
    if TABLE[member].contacts:
        whole = abs(numerator) // denominator
        return (-whole if numerator < 0 else whole) * bottom == top
    step_top, step_bottom = _last_figure(form, numerator, denominator)
    gap = abs(numerator * bottom - top * denominator)
    # |count - exact| <= step / 2 + EXPORTER_STEPS * |exact| / 2**52, every
    # side multiplied out by 2 * step_bottom * denominator * bottom * 2**52.
    room = (
        step_top * denominator * bottom * 2**52
        + 2 * EXPORTER_STEPS * abs(top) * step_bottom * denominator
    )
    return gap * 2 * step_bottom * 2**52 <= room


def settled_reading(
    member: str,
    plain: CountForm,
    tally: Tally,
    counts: "list[tuple[int, int]]",
    published: int = 0,
    usual: int = -1,
) -> "tuple[int, int, list[int | None]] | None":
    """How a declared column's counts are read: the settled unit, the written unit, each count's moment.

    THE ONE DECISION THE PROFILER AND QUESTION Q3 SHARE (the review of
    landing R4, item 2). ``counts`` are the column's exact counts beside
    its set-aside numbers, in the order the cells stand; ``plain`` and
    ``tally`` say how the counts of the reading asked are written -- every
    count, or the USUAL ones -- and ``usual`` the most figures after the
    mark a usual count writes, -1 where every count is read alike
    (`every_count`, `usual_tally`): a stray written with more figures is
    held to its own last figure (`held_to`; the second review of landing
    R4, item 5). The profiler asks every count's reading first and the
    usual counts' only where that one holds no unit, as Q3 does
    (`figures_kept`). Each unit the figures may carry
    is tried, coarsest first (`reading_units`; the checker passes the
    unit the description published, ``published``, and that alone): every
    count is read as the moment it names in that unit, None where it names
    none or a moment of a placeholder day (`placeholder_day_named`), and
    the moments are written at the coarsest unit every one of them stands
    on (`written_unit`). The first unit at which every count is its
    column's own writing of its moment (`held_by_its_moment`) is the
    reading -- at once for the published unit, for whole counts and for a
    member with contacts, whose figures after the point are no time. A
    count is asked of at the unit it was settled to: the written unit
    names the same instant, and `count_of` reads it from the same
    nanoseconds.

    None where no unit holds every figure: Unix seconds written with
    tenths, four figures of a day of moments off the whole minute, and one
    to three figures of a day that are not whole days are no counted dates
    a twin could be drawn at.

    Guarantees: accepts the member, the column's plain form, its tally,
    its counts and a published unit or nought; returns the settled unit,
    the written unit and one moment or None per count, or None.
    Determinism: whole-number arithmetic. Raises KeyError for a word
    outside `MEMBERS`. No I/O of any kind.
    """
    found = TABLE[member]
    candidates: "tuple[int, ...]" = (published,)
    if not published:
        candidates = reading_units(member, plain, tally, count_top(counts))
    for settled in candidates:
        moments: "list[int | None]" = []
        standing: "list[int]" = []
        for numerator, denominator in counts:
            moment = _settled_moment(member, numerator, denominator, settled)
            moments += [moment]
            if moment is not None:
                standing += [moment]
        unit = published if published else written_unit(standing, settled)
        if published or found.contacts or (tally.places == 0 and usual < 0):
            return settled, unit, moments
        if _every_figure_held(member, plain, counts, moments, settled, usual):
            return settled, unit, moments
    return None


def _settled_moment(member: str, numerator: int, denominator: int, settled: int) -> "int | None":
    """A count's moment in whole ``settled`` units: None where it names none, or a moment of a placeholder day."""
    moment = moment_of(member, numerator, denominator, settled)
    if moment is not None and placeholder_day_named(moment, settled):
        return None
    return moment


def names_a_date(member: str, numerator: int, denominator: int) -> bool:
    """Whether an exact count is read as a date at all: it names a moment, and no moment of a placeholder day.

    THE ABSENCE DECISION, asked before a count tells how its column is
    written (the verification of the Codex review of landing R4, item
    4): Excel's 0 and 60, minus one in a spreadsheet, a count past
    9999-12-31 and a moment of 1 January 1900 or 31 December 9999 are
    read as no value and written back as written, so none of them takes
    part in the tally the form is drawn from -- a lone `0` beside six-place
    serials made the tally a trimmed form its own six-place counts then
    missed, and the column was declined. Asked at the nanosecond, the
    finest unit, before any unit is settled; the profiler's reading
    (`taxonomy`) and question Q3's (`figures_kept`) share it.

    Guarantees: a function of the three. Raises KeyError for a word
    outside `MEMBERS`. No I/O of any kind.
    """
    return _settled_moment(member, numerator, denominator, NANOSECOND) is not None


def _every_figure_held(
    member: str,
    plain: CountForm,
    counts: "list[tuple[int, int]]",
    moments: "list[int | None]",
    settled: int,
    usual: int = -1,
) -> bool:
    """Whether every count that names a moment is its column's own writing of it, a stray by its own last figure."""
    for place in range(len(counts)):
        moment = moments[place]
        if moment is None:
            continue
        numerator, denominator = counts[place]
        form = held_to(plain, usual, denominator)
        if not held_by_its_moment(member, form, numerator, denominator, moment, settled):
            return False
    return True


def figures_kept(
    members: "tuple[str, ...]", present: "list[str]", mark: str = POINT
) -> "tuple[str, ...]":
    """The members a declaration of which would keep every figure a column's counts write (question Q3).

    THE PROFILER'S OWN DECISION, asked before the question is put
    (`settled_reading`): for each member, the present cells read as its
    counts (`counted`), its set-aside numbers taken out (`declared_aside`)
    and those read as no value (`names_a_date`), tallied by the figures each writes after the mark, settled to each
    unit the figures may carry (`reading_units`) and asked whether every
    count names its moment as its column wrote it (`held_by_its_moment`),
    exactly as a declaration reads them -- by EVERY count's form first
    and, where some counts are strays, by the usual counts' form with
    each stray held to its own last figure (`every_count`, `usual_tally`,
    `held_to`). A member is kept where EITHER reading holds, as the
    profiler reads the column by whichever does. A system
    no unit of which holds every figure -- Unix seconds written with
    tenths, four figures of a day of moments off the minute -- is not
    offered, since the answer would be refused (NF115): the first build of
    the review of landing R4 asked such a column and then refused every
    system it offered, as item 3 of that review found for Epic days with a
    binary64's tail. A member with contacts holds the day alone, and whole
    counts hold at every unit.

    WALKS OF THE CELLS SHARED BY THE MEMBERS, NOTHING KEPT PER CELL: a
    cell is a count of every member without contacts alike, so each is
    read once a walk -- the first tallies each member's counts, the next
    asks each member at one unit, and stops where none is left standing.
    A member is kept where ANY unit holds (the profiler settles at the
    coarsest that does; the question asks only whether one does), so its
    units are tried finest first -- `repr`'s seventeen figures hold at the
    finest at once -- and a member whose unit fails is walked again at the
    next. Keeping every count instead cost 170 MB at a million rows.

    The caller asks this only of a column some count of which is not whole:
    a whole count is its own writing of its moment at every unit, and a
    count past 2**53 whose fraction binary64 cannot hold stands well
    inside the exporter's steps (`EXPORTER_STEPS`).

    Guarantees: accepts the members, the present cells and the mark;
    returns those members whose reading holds, in their order.
    Determinism: whole-number arithmetic over the text. Raises KeyError
    for a word outside `MEMBERS`. No I/O of any kind.
    """
    walked: "list[str]" = []
    asides: "dict[str, dict[int, int]]" = {}
    tallies: "dict[str, dict[int, Tally]]" = {}
    tops: "dict[str, int]" = {}
    for member in members:
        if TABLE[member].contacts:
            continue
        walked += [member]
        aside: "dict[int, int]" = {}
        for number in declared_aside(member):
            aside[number] = 1
        asides[member] = aside
        tallies[member] = {}
        tops[member] = 0
    if walked:
        for text in present:
            written = written_count(text, mark)
            if written is None:
                continue
            numerator, denominator = exact_value(written)
            for member in walked:
                # ONLY A COUNT READ AS A DATE TELLS HOW THE COLUMN IS WRITTEN
                # (`names_a_date`), as the profiler's own reading tallies.
                if not stands_aside(
                    numerator, denominator, False, asides[member]
                ) and names_a_date(member, numerator, denominator):
                    tallied_by_places(tallies[member], written)
                    tops[member] = max(tops[member], abs(numerator) // denominator + 1)
    held: "dict[str, int]" = {}
    # ONE READING PER KEY, a member and which of its readings: 0 by every
    # count's form, 1 by the usual counts' with each stray held to its own
    # last figure (`every_count`, `usual_tally`, `held_to`).
    plains: "dict[tuple[str, int], CountForm]" = {}
    usuals: "dict[tuple[str, int], int]" = {}
    units: "dict[tuple[str, int], tuple[int, ...]]" = {}
    tried: "dict[tuple[str, int], int]" = {}
    pending: "list[tuple[str, int]]" = []
    for member in walked:
        every = every_count(tallies[member])
        if every.places == 0 and not every.exponent:
            # No count at all, or every count whole and written bare: every
            # figure is held, and the form of none but whole figures holds
            # every cell.
            held[member] = 1
            continue
        tally, usual = usual_tally(tallies[member])
        readings: "list[tuple[Tally, int]]" = [(every, -1)]
        if usual >= 0:
            readings += [(tally, usual)]
        for which in range(len(readings)):
            counted_here, longest_usual = readings[which]
            key = (member, which)
            plains[key] = form_from(counted_here, mark, None)
            usuals[key] = longest_usual
            units[key] = reading_units(member, plains[key], counted_here, tops[member])
            # The finest first: `reading_units` gives them coarsest first.
            tried[key] = len(units[key]) - 1
            pending += [key]
    while pending:
        standing: "dict[tuple[str, int], int]" = {}
        # THE CHECKER'S RULE TOO (`in_its_form`): the counts each reading
        # reads as dates, and those written finer than its form.
        dated: "dict[tuple[str, int], int]" = {}
        finer: "dict[tuple[str, int], int]" = {}
        for key in pending:
            standing[key] = 1
            dated[key] = 0
            finer[key] = 0
        for text in present:
            if not standing:
                break
            written = written_count(text, mark)
            if written is None:
                continue
            numerator, denominator = exact_value(written)
            for key in pending:
                member = key[0]
                if key not in standing or stands_aside(
                    numerator, denominator, False, asides[member]
                ):
                    continue
                settled = units[key][tried[key]]
                moment = _settled_moment(member, numerator, denominator, settled)
                if moment is None:
                    continue
                if not held_by_its_moment(
                    member,
                    held_to(plains[key], usuals[key], denominator),
                    numerator,
                    denominator,
                    moment,
                    settled,
                ):
                    del standing[key]
                    continue
                dated[key] = dated[key] + 1
                if form_holds(member, plains[key], written):
                    continue
                if not written_finer(plains[key], written):
                    del standing[key]
                    continue
                finer[key] = finer[key] + 1
        for key in pending:
            if key in standing and strays_stand(finer[key], dated[key]):
                held[key[0]] = 1
        still: "list[tuple[str, int]]" = []
        for key in pending:
            # A member one reading holds is kept, and its other is not walked.
            if key[0] in held:
                continue
            if tried[key] > 0:
                tried[key] = tried[key] - 1
                still += [key]
        pending = still
    kept: "list[str]" = []
    for member in members:
        if member not in tallies or member in held:
            kept += [member]
    return tuple(kept)


def form_holds(member: str, form: CountForm, written: Written) -> bool:
    """Whether a cell is one the published form can write (validation, CD).

    A fixed form writes exactly `places` figures after the mark; a
    trimmed one at most `places`, none of them a trailing zero; a
    significant one at most `significant` significant figures, trimmed --
    and at seventeen, `repr`'s `45123.0` for a whole count;
    an exponent form fifteen significant figures, either written in full
    or in exponent form. A MEMBER WITH CONTACTS (``member``, the system
    the column is declared in) writes its day count and no contact
    number, or one of at most `places` figures, WHETHER OR NOT A CENSUS
    IS PUBLISHED: a contact number fewer cells than the disclosure line
    wrote is counted into the commonest, and where none reaches the line
    no census is published at all (the second review of landing R4, item
    1), so a source holding five `.03` cells beside a census of `(none)`,
    `01` and `02`, or eight `.01` cells and no census, is still in its
    own form -- `places` is the longest any cell writes. The census
    itself, where published, is held exactly beside this check. An empty
    ``member`` reads a census published as the contact rule.

    Guarantees: a function of the three. Raises KeyError for a word
    outside `MEMBERS` other than the empty one. No I/O of any kind.
    """
    contacts = TABLE[member].contacts if member else form.contacts is not None
    if contacts:
        if written.exponent_form:
            return False
        return len(written.fraction) <= form.places
    if written.exponent_form and not form.exponent:
        return False
    if form.exponent:
        return significant_figures(written) <= 15 and written.fraction[-1:] != "0"
    if form.significant is not None:
        return significant_figures(written) <= form.significant and (
            written.fraction[-1:] != "0"
            or (form.significant == 17 and written.fraction == "0" and not written.exponent_form)
        )
    if form.trimmed:
        return len(written.fraction) <= form.places and written.fraction[-1:] != "0"
    return len(written.fraction) == form.places


def written_finer(form: CountForm, written: Written) -> bool:
    """Whether a cell writes more figures than the published form does: a stray (`usual_tally`).

    More figures after the mark than a form by places writes, or more
    significant figures than a form by significance; a column with
    contacts has none. The checker lets as many such cells stand as the
    profiler set beside the usual counts -- one in a hundred, one at
    least, the rest nine tenths -- and misses any cell the form cannot
    write for another reason (the second review of landing R4, item 5).

    Guarantees: a function of the two. Raises nothing. No I/O.
    """
    if form.contacts is not None or written.exponent_form:
        return False
    if form.significant is not None or form.exponent:
        figures = form.significant if form.significant is not None else 15
        return significant_figures(written) > figures
    return figures_after_the_mark(written) > form.places


def in_its_form(member: str, form: CountForm, cells: "list[str]") -> bool:
    """Whether every cell written as a count is one the form can write, the strays few enough (V5-CF).

    THE CHECKER'S OWN RULE, asked by the profiler before it publishes a
    form (the Codex review of landing R4, item 3): each count of the
    member (`counted`, in the form's mark) is held by `form_holds`, or is
    written with more figures than the form (`written_finer`) and stands
    as a stray while they number no more than `strays_stand` lets; any
    other is a spelling the form cannot write. A column writing whole
    counts both bare and with `.0`, or Python's `%e` with its zeros, has
    no form its own checker holds every cell of, and is not read as
    counted dates -- where the first build published a form its source
    then missed. ``cells`` are the cells the description reads as dates;
    a cell that is no count of the member is not asked.

    Guarantees: a function of the three. Raises KeyError for a word
    outside `MEMBERS`. No I/O of any kind.
    """
    counts = 0
    strays = 0
    for text in cells:
        written = counted(member, text, form.mark)
        if written is None:
            continue
        counts = counts + 1
        if form_holds(member, form, written):
            continue
        if not written_finer(form, written):
            return False
        strays = strays + 1
    return strays_stand(strays, counts)


def strays_stand(strays: int, counts: int) -> bool:
    """Whether a column's cells written finer than its form are few enough to stand as strays.

    At most one in a hundred of its counts, one at least, and the rest at
    least nine tenths -- the profiler's own rule (`usual_tally`).
    """
    return strays <= _strays_allowed(counts) and (counts - strays) * REST_SHARE_DEN >= counts * REST_SHARE_NUM


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


def stands_aside(
    numerator: int, denominator: int, contacts: bool, aside: "dict[int, int]"
) -> bool:
    """Whether an exact count is one of the set-aside numbers in ``aside``.

    Exactly: `0.0` is nought and `60.5` is not sixty. A member with
    contacts asks the figures before the point alone, the day they name.
    The one test the profiler's reading, the generator's and the
    checker's share (`declared_aside` gives the numbers, once per column).

    Guarantees: a function of the four. Raises nothing. No I/O.
    """
    if contacts:
        whole = abs(numerator) // denominator
        return (-whole if numerator < 0 else whole) in aside
    if numerator % denominator:
        return False
    return numerator // denominator in aside


def _word_of_day(year: int, month: int, date: int) -> str:
    """A day's ISO word, as `set_aside_named` names it."""
    return f"{year:04d}-{month:02d}-{date:02d}"


# THE PLACEHOLDER DAYS, as whole days from 1970: a declared column's count
# naming one of them -- whole or not, `2958465` or `2958465.5` -- is read as
# no value unless the person kept it (`placeholder_day_named`).
PLACEHOLDER_DAYS = (_day(1900, 1, 1), _day(9999, 12, 31))


def placeholder_day_named(moment: int, unit: int) -> str:
    """The placeholder day a moment falls on, as its ISO word, or "".

    1 January 1900 and 31 December 9999 (`parsing.CALENDAR_PLACEHOLDERS`),
    at any time of day: under a declaration, every count naming one of
    them is set aside before the date role reads the column, so no cell
    of a counted column reaches the date role's own judgement of
    placeholder days -- which would record it under the ISO text it was
    read as, and the twin would write that text into a column of numbers
    (the review of landing R4, item 5, mutant M12).

    Guarantees: a function of the two. Raises nothing. No I/O.
    """
    day = (moment * unit) // DAY
    for placeholder in PLACEHOLDER_DAYS:
        if day == placeholder:
            year, month, date = parsing.civil_from_days(day)
            return _word_of_day(year, month, date)
    return ""


def hole_days(member: str, moments: bool = False) -> "tuple[int, ...]":
    """The whole days a column counted in ``member`` holds no date on, from 1970 (method G7.10).

    THE DAYS A TWIN DATE WOULD READ BACK AS NO VALUE (the second review of
    landing R4, item 2): both placeholder days, since every count naming
    either at any time of day is set aside (`placeholder_day_named`), and
    -- on a column of DATES -- the day each of the member's other
    set-aside numbers (`declared_aside`) names by its own rule, which adds
    a day only on Excel's 1900 system, whose serial 2, the count pandas
    writes for 1 January 1900, Excel reads as 2 January. On a column of
    MOMENTS (``moments``) that serial names one instant, midnight of 2
    January, and every other moment of that day is a count such as
    `2.519...` and a date (the verification of that repair, its item 2
    (d)): the day is no hole there, and the instant is kept off by the
    reach of the column's low tail (`tail_reach`), which no other rank of
    a column whose dates start on that day can pass.

    Guarantees: a function of the two, the days rising. Raises KeyError
    for a word outside `MEMBERS`. No I/O of any kind.
    """
    days: "dict[int, int]" = {}
    for day in PLACEHOLDER_DAYS:
        days[day] = 1
    if not moments:
        for number in declared_aside(member):
            moment = moment_of(member, number, 1, DAY)
            if moment is not None:
                days[moment] = 1
    return tuple(sorted(days))


def hole_words(member: str, moments: bool = False) -> "tuple[str, ...]":
    """The days a column counted in ``member`` holds no date on, as ISO words (method G7.10).

    `hole_days`, written as the words the producer, the generator and the
    validator each hold as the column's absent spellings
    (`calendar_rules.public_holes`), so the twin's ranks keep off them. A
    real date on one of them in the source is no value, and the twin
    draws none: a twin of Excel birth dates from 1900 drew serial 1 on 3
    seeds of 3, and one of SAS days from 1890 day -21914 on 1 of 3, each
    read back as no value, so each missed its own count of present cells
    (the second review of landing R4, item 2).

    Guarantees: a function of the two, the days rising. Raises KeyError
    for a word outside `MEMBERS`. No I/O of any kind.
    """
    words: "list[str]" = []
    for day in hole_days(member, moments):
        year, month, date = parsing.civil_from_days(day)
        words += [_word_of_day(year, month, date)]
    return tuple(words)


def blocked_spans(member: str, written: int) -> "tuple[tuple[int, int], ...]":
    """The stretches of time no twin cell of a column counted in ``member`` may stand on (method G7.10).

    Each a first and a last second counted from the start of 1 January
    1970, both included, for a column written at ``written`` (a unit of
    `WRITTEN_UNITS`, `DAY` for a column of dates): every second of either
    placeholder day; the instant each other set-aside count names -- Excel
    1900's serial 2, midnight of 2 January 1900 -- with the whole of its
    day on a column of dates and, on a column of moments, the seconds the
    written unit writes as that instant (a minute's sixty, which the
    clock writes as `00:00`); and, on the two spreadsheet systems, which
    read no count below their first day, every second before it, from the
    calendar's first day. A cell on one reads back as no value or is no
    count at all: a twin of Excel date-times from 1900 wrote
    `1899-12-31 06:20`, a moment before serial 1, as ISO text, and drew
    1 January 1900 (the verification of the second review's item 2).

    Guarantees: a function of the two, rising by first second. Raises
    KeyError for a word outside `MEMBERS`. No I/O of any kind.
    """
    spans: "dict[int, int]" = {}
    for day in PLACEHOLDER_DAYS:
        spans[day * 86400] = day * 86400 + 86399
    for number in declared_aside(member):
        moment = moment_of(member, number, 1, SECOND)
        if moment is None or moment // 86400 in PLACEHOLDER_DAYS:
            continue
        if written >= DAY:
            day = moment // 86400
            spans[day * 86400] = day * 86400 + 86399
        else:
            spans[moment] = moment + max(1, written // SECOND) - 1
    if not TABLE[member].signed:
        first = moment_of(member, 1 if member == EXCEL_1900 else 0, 1, DAY)
        if first is not None and first > _FIRST_DAY:
            spans[_FIRST_DAY * 86400] = first * 86400 - 1
    return tuple((start, spans[start]) for start in sorted(spans))


def blocked_units(
    member: str, written: int, tail_seconds: int
) -> "tuple[tuple[int, int], ...]":
    """`blocked_spans` in tail units, joined where they touch or overlap (method G7.10).

    Each a first and a last tail unit, both included, counted from 1970
    as `taxonomy.tail_ordinal` counts them; ``tail_seconds`` is how many
    seconds one tail unit holds -- 86,400 for a day, 60 for a minute, one
    for a second. Stretches that touch are one: Excel 1900's days before
    its first count, 1 January 1900 and the instant serial 2 names are
    one stretch from the calendar's first day.

    Guarantees: a function of the three, rising and apart. Raises KeyError
    for a word outside `MEMBERS`. No I/O of any kind.
    """
    joined: "list[tuple[int, int]]" = []
    for first, last in blocked_spans(member, written):
        start = first // tail_seconds
        stop = last // tail_seconds
        if joined and start <= joined[len(joined) - 1][1] + 1:
            before = joined[len(joined) - 1]
            joined[len(joined) - 1] = (before[0], max(before[1], stop))
            continue
        joined += [(start, stop)]
    return tuple(joined)


def tail_reach(
    member: str, written: int, tail_seconds: int, at: int, low_side: bool, edge: int
) -> int:
    """How far one tail of a column counted in ``member`` may reach from its boundary, in tail units (G7.10).

    THE TAIL STOPS SHORT OF THE FIRST WALL BEYOND ITS BOUNDARY: a stretch
    the column's counts cannot hold (`blocked_units`) that runs on to the
    furthest unit the member's own spelling writes, ``edge`` from the
    boundary ``at``, or to the calendar's first or last day, so that no
    count stands beyond it -- every moment
    before a spreadsheet system's first count, with 1 January 1900 and
    Excel's serial 2 beside it, and 31 December 9999 (the verification of
    the second review of landing R4, item 2). A tail's outermost rank is
    drawn from its two published distances and can stand beyond every
    value the source holds: a low tail of Excel date-times from 1900 put
    its end at `1899-12-31 06:20`, before Excel's first day and written as
    ISO text, and a rank's stratum ran across 1 January 1900, so the twin
    drew that day and read it back as no value on 6 seeds of 6. The
    source's own values beyond a boundary stand on this side of a wall,
    so no tail loses one. Where no unit is left between the boundary and
    the wall the reach is the member's own.

    AN ISLAND DOES NOT CUT THE REACH (`tail_islands`): 1 January 1900, in
    a system that writes the days either side of it, has values of the
    source beyond it as often as not, and a reach cut there drew such a
    tail this side of the day -- SAS days from December 1899 lost every
    one of their eight values before the day, and a dense tail of SAS
    seconds was piled onto its last second, missing its own count of
    different values (the repair of that verification, found on the way).
    A tail reaches past an island, and no rank of it stays on one.

    Guarantees: accepts the member, the written unit, the tail unit in
    seconds, the boundary's tail unit, the side and the member's reach;
    returns a whole number of at least one and at most ``edge`` where
    ``edge`` is at least one. Determinism: whole-number arithmetic.
    Raises KeyError for a word outside `MEMBERS`. No I/O of any kind.
    """
    furthest = at - edge if low_side else at + edge
    first = (_FIRST_DAY * 86400) // tail_seconds
    last = (_LAST_DAY * 86400 + 86399) // tail_seconds
    nearest: "int | None" = None
    for start, stop in blocked_units(member, written, tail_seconds):
        if low_side and stop < at and (start <= furthest or start <= first):
            if nearest is None or stop > nearest:
                nearest = stop
        if not low_side and start > at and (stop >= furthest or stop >= last):
            if nearest is None or start < nearest:
                nearest = start
    if nearest is None:
        return edge
    reach = at - nearest - 1 if low_side else nearest - at - 1
    if reach < 1:
        return edge
    return min(edge, reach)


def tail_islands(
    member: str, written: int, tail_seconds: int, at: int, low_side: bool, reach: int
) -> "tuple[tuple[int, int], ...]":
    """The stretches inside one tail's reach its counts cannot hold, as distances (method G7.10).

    Each a nearest and a furthest distance from the boundary ``at``, in
    tail units, both included and the nearest first: every stretch of
    `blocked_units` beyond the boundary that starts within ``reach``
    (`tail_reach`), its far end kept within it. On a column counted in a
    system that writes the days either side of it, 1 January 1900 is such
    an ISLAND: the tail reaches past it, its end and its group step off
    it, a rank whose stratum lies wholly on it is given room either side
    (`stratum_off_the_islands`), and every rank left on its day moves off
    it (`generation._kept_off_placeholder_days`).

    Guarantees: a function of the six, rising and apart, each pair inside
    one to ``reach``. Raises KeyError for a word outside `MEMBERS`. No I/O
    of any kind.
    """
    found: "list[tuple[int, int]]" = []
    for start, stop in blocked_units(member, written, tail_seconds):
        if low_side and stop < at:
            nearest, furthest = at - stop, at - start
        elif not low_side and start > at:
            nearest, furthest = start - at, stop - at
        else:
            continue
        if nearest > reach:
            continue
        found += [(nearest, min(furthest, reach))]
    return tuple(sorted(found))


def on_an_island(distance: int, islands: "tuple[tuple[int, int], ...]") -> bool:
    """True where one whole distance of a tail stands on one of ``islands`` (`tail_islands`).

    Guarantees: a function of the two. Raises nothing. No I/O.
    """
    for nearest, furthest in islands:
        if nearest <= distance <= furthest:
            return True
    return False


def off_the_islands(distance: int, islands: "tuple[tuple[int, int], ...]", reach: int) -> int:
    """One whole distance of a tail, stepped off every island it stands on (method G7.10).

    INWARD to the unit just inside the island where that is a distance of
    one or more -- as a tail's end and group step off a unit an absent
    spelling names -- and otherwise OUTWARD to the unit just beyond it
    where that is within ``reach``; it stays where neither is. ``islands``
    are `tail_islands`.

    Guarantees: a function of the three. Raises nothing. No I/O.
    """
    for nearest, furthest in islands:
        if nearest <= distance <= furthest:
            if nearest - 1 >= 1:
                return nearest - 1
            if furthest + 1 <= reach:
                return furthest + 1
            return distance
    return distance


def stratum_off_the_islands(
    near: "list[int]",
    far: "list[int]",
    islands: "tuple[tuple[int, int], ...]",
    reach: int,
) -> "tuple[list[int], list[int]]":
    """Each rank's stratum, given room off any island it lies wholly on (method G7.10).

    ``near`` and ``far`` are each rank's nearest and furthest distance,
    outermost first, each no smaller than the one inside it. A rank whose
    stratum lies wholly on an island has nowhere to stand off it, so the
    stratum of every such rank -- ``m`` of them on that island -- runs
    from ``m`` units inside the island to ``m`` units beyond it, within
    one and ``reach``; the strata are then kept no smaller than the ones
    inside them, the nearest widened inward and the furthest outward, so
    each still holds the one it had. The generator moves such a rank off
    the island inside that room, and the validator draws its windows from
    the same strata.

    Guarantees: accepts two lists of one length and the islands; returns
    two new lists of that length, each stratum holding the one given.
    Determinism: a function of the four. Raises nothing. No I/O.
    """
    nearest = [value for value in near]
    furthest = [value for value in far]
    for first, last in islands:
        inside: "list[int]" = []
        for index in range(len(nearest)):
            if first <= nearest[index] and furthest[index] <= last:
                inside += [index]
        for index in inside:
            nearest[index] = max(1, first - len(inside))
            furthest[index] = min(reach, last + len(inside))
    for index in range(1, len(nearest)):
        nearest[index] = min(nearest[index], nearest[index - 1])
    for index in range(len(furthest) - 2, -1, -1):
        furthest[index] = max(furthest[index], furthest[index + 1])
    return (nearest, furthest)


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
# present cells and at least eleven, and at most one cell in a hundred
# -- one at least -- may lie outside the band (the R4 design review,
# item 1). One in a thousand let two keying slips in a thousand cells
# silence the question again on 2 to 3 of 13 shapes; one in a hundred
# asks 12 or 13 of them under five, and raises no new question on the
# chance battery (the review of landing R4, item 6). Text cells may
# stand to the date role's own line.
REST_SHARE_NUM = 9
REST_SHARE_DEN = 10
REST_LEAST = 11
STRAY_PER = 100

# RULE A ON COUNTS OF DAYS THAT ARE NOT WHOLE (the review of landing R4,
# item 7): a spreadsheet's date-times write four figures after the point
# or more -- a minute is 0.000694 of a day -- or fifteen significant
# figures and more, where a salary in cents or a dose to one decimal in
# Excel's five-figure band writes one or two. Epic's figures after the
# point are contact numbers, and its days are mostly the first contact of
# their day, written whole: at least half of a column asked as Epic days
# writes no contact number, where cents of a room rate write one nearly
# everywhere.
DAY_TIME_PLACES = 4
DAY_TIME_SIGNIFICANT = 15

# RULE B ON A COLUMN NEAR ITS EPOCH (the same item): a length of stay
# kept as whole days of seconds names days of January and February 1970,
# so a column more than half of whose rest lies within a year of its
# system's first day is a column of durations, and is not asked. AND ON A
# UNIT A THOUSAND TIMES TOO COARSE: whole days of milliseconds, read as
# seconds, stand at midnight every thousand days -- 1972, 1975, ... 2049
# -- which no column of dates does, so a column whose every day count is
# a multiple of a thousand is not asked either.
EPOCH_YEAR_DAYS = 365
UNIT_STEP_DAYS = 1000

# RULE C's WIDTH: the fewest figures a column of fixed-width figures
# writes for rule C to read it as days -- serial 10,000 is 1927.
FIXED_WIDTH_LEAST = 5

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
    table's order, each of the same unit as a member the rule fired on,
    each reading the column inside 1900 to 2050 and each keeping its
    figures (`figures_kept`); `set_aside` which
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
    """How many of the rest may lie outside the band: one in a hundred, one at least."""
    return max(1, present // STRAY_PER)


def fixed_width(present: "list[str]") -> int:
    """The one width every cell is written in, as figures alone, or 0.

    Today's fixed-width question, as `asking.why_worth_asking` asks it: no
    cell padded with a leading zero, every cell ASCII figures and nothing
    else, all one width. Rule C asks it of the cells beside the set-aside
    numbers (`_text_holds`). Guarantees: a function of the cells. Raises
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
    costs one lookup: a column that satisfies rule A has nine tenths of its
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
    *,
    floor: int,
) -> "Asked | None":
    """Whether a column of numbers is worth asking about as dates (question Q3).

    THREE RULES, each over the column's present cells with each member's
    set-aside numbers taken out first (`set_aside`), the rest at least
    nine tenths of the present cells and at least eleven:

    * A -- every one of the rest is a count written by the grammar
      (`counted`), at most one in a hundred of them (one at least) lies
      outside the member's band from 1990, and the whole figures of those
      inside it are all written with one number of figures: a column of
      record numbers spread over two widths is not asked about, where a
      column of moments in one decade is (the R4 design review, item 5).
      Counts of days that are not whole write four figures after the
      point or fifteen significant ones, as a spreadsheet's date-times
      do, and at least half of a column of Epic days writes no contact
      number (the review of landing R4, item 7);
    * B -- whole counts of a member finer than the day, every one of the
      rest at midnight UTC, at least eleven different, inside the band
      from 1900, one in a hundred at most outside it, more than half of
      them a year or more from the member's first day, and not every one
      a whole thousand days from it: a date kept as an instant (narrowed
      to midnight UTC, item 3 of that review: a date kept at LOCAL
      midnight comes back as instants and is a stated limit), and not a
      length of stay kept as whole days of seconds, or of milliseconds
      read as seconds;
    * C -- every count beside the set-aside numbers is written in figures
      alone, all one width of at least five (`fixed_width`), so the
      column is one the fixed-width question asks already, set-aside
      numbers aside, and a member counting days reads it inside 1900 to
      2050, one in a hundred at most outside: the question offers dates
      as answers beside its own. A column whose "none" is `-1` beside
      five-figure codes is asked newly, a stated limit (plan P4-D384).

    TEXT CELLS STAND TO THE DATE ROLE'S LINE: ``needed`` cells of the
    present ones must be counts. ``numbers`` are the column's own numbers
    as the numeric role read them, which the bands are asked of; the
    grammar asks the text. ``median`` is the block's own published median
    and ``whole`` whether every number is whole, which let an ordinary
    column be answered before anything is sorted (`_may_be_asked`).
    ``mark`` is the column's decimal mark: a column declared
    `--decimal-comma` writes its counts `45386,5`, and the grammar reads
    them with the comma (the R4 design review, item 8). ``floor`` is the
    settings' disclosure floor: a set-aside number is NAMED only where
    `parsing.census_floor` cells or more hold it, since a count of one
    names an individual -- one `0` among births in Unix seconds is a
    birth on 1 January 1970 (the review of landing R4, item 4).

    THE ANSWERS (item 2 of that review): every member counting in the
    unit of a member a rule fired on and reading the column inside 1900
    to 2050, so a column of SAS days from 1985 is offered the 1960
    member it is written in beside the 1970 one -- and, on a column some
    count of which is not whole, only a member whose declaration would
    keep every figure (`figures_kept`): Unix seconds written with tenths
    are asked nothing, where the first build of the review of landing R4
    offered systems whose every answer was then refused.

    Guarantees: accepts the present cells as text, their numbers, the
    cells the date role's line needs, the median, whether every number
    is whole, the mark and the floor; returns `Asked` or None.
    Determinism: a function of the seven. Raises nothing. No I/O of any
    kind.
    """
    total = len(present)
    if total < REST_LEAST or len(numbers) < needed:
        return None
    open_to = _may_be_asked(numbers, median, whole)
    if not open_to:
        return None
    ordered = sorted(numbers)
    # THE RULES IN THEIR ORDER, EACH TAKEN TO ITS END -- its numbers, its
    # text and the systems it would offer -- before the next is tried (the
    # Codex review of landing R4, item 6): the band's numbers held Unix
    # counts at midnight crossing from nine figures to ten, its text then failed
    # on the two widths, and the midnight rule, which those values meet,
    # was never asked.
    for rule in RULES:
        held = _numbers_hold(ordered, open_to, rule, total)
        kept: "list[str]" = []
        # THE TEXT HALF'S OWN WALK ALSO SAYS whether every cell is whole
        # figures written bare and whether any cell is a date written as
        # text (`_text_walk`), so the two checks the Codex review of landing
        # R4 added (items 1 and 3) cost no walk of their own.
        bare = True
        dated = False
        for member in held:
            holds, member_bare, member_dated = _text_walk(present, member, rule, needed, mark)
            if holds:
                kept += [member]
                bare = bare and member_bare
                dated = dated or member_dated
        if not kept:
            continue
        if dated:
            # COUNTS BESIDE DATES WRITTEN AS TEXT are not read as counted
            # dates (`written_as_a_date`), so no answer would be taken.
            return None
        offered = _offered(ordered, kept, total, present, needed, mark)
        if not bare:
            # A SYSTEM WHOSE ANSWER WOULD BE REFUSED IS NOT OFFERED (the
            # review of landing R4, item 2): its declaration keeps no unit of
            # the figures, or -- whole or not -- no form its checker holds
            # every count of (the Codex review of landing R4, item 3). Whole
            # figures written bare, with no mark and no exponent, keep every
            # figure in the one form they are written in, and are not walked.
            offered = figures_kept(offered, present, mark)
        if offered:
            return Asked(rule, offered, _set_aside_words(ordered, kept, floor))
    return None


def _numbers_hold(
    ordered: "list[float]",
    open_to: "list[tuple[str, str]]",
    rule: str,
    total: int,
) -> "list[str]":
    """The members whose numbers one rule holds, before any text is read (`asked_of`)."""
    held: "list[str]" = []
    for member, fired in open_to:
        if fired != rule:
            continue
        rest = len(ordered) - _aside_in(ordered, member)
        if not _rest_is_enough(rest, total):
            continue
        low, high = band(member, NARROW_FROM if rule == RULE_BAND else WIDE_FROM)
        inside = _in_band(ordered, low, high) - _aside_inside(ordered, member, low, high)
        if rest - inside > _strays_allowed(total):
            continue
        if rule == RULE_MIDNIGHT:
            # A LENGTH OF TIME IS NO DATE: more than half the rest must lie a
            # year or more from the member's first day.
            year = float(EPOCH_YEAR_DAYS * (DAY // TABLE[member].unit))
            near = _in_band(ordered, -year, year) - _aside_inside(
                ordered, member, -year, year
            )
            if 2 * near >= rest:
                continue
        held += [member]
    return held


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
    """The written half of a rule: the grammar, the width, and midnight (`_text_walk`'s first answer)."""
    return _text_walk(present, member, rule, needed, mark)[0]


def _text_walk(
    present: "list[str]", member: str, rule: str, needed: int, mark: str = POINT
) -> "tuple[bool, bool, bool]":
    """The written half of a rule: the grammar, the width, and midnight.

    Returns whether it holds, and -- over the cells walked, which are all
    of them wherever it holds -- whether every cell is whole figures
    written bare, with no mark and no exponent, and whether some cell
    that is no count is a date written as ISO text (`written_as_a_date`;
    the Codex review of landing R4, items 1 and 3).

    At least ``needed`` present cells are counts of the member
    (`counted`; text cells stand to the date role's line). For rule A, the
    whole figures of the counts inside the narrow band all have one width;
    counts of days that are not whole write `DAY_TIME_PLACES` figures after
    the point or `DAY_TIME_SIGNIFICANT` significant ones; and a member
    with contacts has at least half its counts write no contact number.
    NO CELL INSIDE THE BAND OF ANOTHER WIDTH IS LET STAND, where a stray
    outside the band is: measured on the chance battery, letting one cell
    of another width in a thousand stand asked two measurement columns
    that are no fixed width -- the kind of question nothing asked before
    -- and costs one keying slip that lands inside the band at another
    width (`xl_birth` a century early, one seed of three). A stray of
    another width OUTSIDE the band is let stand, so that a century slip
    -- Excel's 2016 keyed as 1916, four figures -- silences no question;
    the price is that ten- and thirteen-figure identifiers with half a
    percent one figure shorter are asked (a stated limit, plan P4-D384).
    For rule C, EVERY count beside the set-aside numbers, strays outside
    the band among them, is written in figures alone, all one width of at
    least `FIXED_WIDTH_LEAST` (`fixed_width`): set-aside numbers aside,
    the column is one the fixed-width question asks already. The
    one-in-a-hundred stray allowance had let six- or seven-figure record
    numbers stand beside five-figure ones, and such columns were newly
    asked on 37 and 31 of 40 draws (the second review of landing R4, item
    4); the battery's only rule-C shape, Excel birth dates, keeps five
    figures under a slip a century late. For rule B, every count beside
    the set-aside numbers is whole and stands at midnight UTC, with at
    least eleven different values, and not every one a whole thousand
    days from the member's first day (`UNIT_STEP_DAYS`).
    """
    found = TABLE[member]
    tally = 0
    rest = 0
    not_whole = 0
    with_contact = 0
    most_places = 0
    most_significant = 0
    widths: "dict[int, int]" = {}
    different: "dict[int, int]" = {}
    standing: "list[str]" = []
    off_the_step = False
    # Rule A's band: the widths it holds to one are those inside it.
    low, high = band(member, NARROW_FROM)
    per_day = DAY // found.unit if found.unit < DAY else 1
    aside: "dict[int, int]" = {}
    for number in set_aside(member):
        aside[number] = 1
    bare = True
    dated = False
    for text in present:
        written = counted(member, text, mark)
        if written is None:
            bare = False
            if not dated and written_as_a_date(text):
                dated = True
            continue
        if written.fraction or written.exponent_form:
            bare = False
        tally = tally + 1
        numerator, denominator = exact_value(written)
        if found.contacts:
            day_part = abs(numerator) // denominator
            if (-day_part if numerator < 0 else day_part) in aside:
                continue
        elif numerator % denominator == 0 and numerator // denominator in aside:
            continue
        rest = rest + 1
        if rule == RULE_MIDNIGHT:
            # WHOLE AND AT MIDNIGHT ONCE THE FRACTION IS REDUCED: a count
            # written `315532800.0` is the midnight `315532800` is (the Codex
            # review of landing R4, item 5).
            if numerator % (denominator * per_day):
                return False, bare, dated
            value = numerator // denominator
            if len(different) < REST_LEAST:
                different[value] = 1
            if (value // per_day) % UNIT_STEP_DAYS:
                off_the_step = True
            continue
        if rule == RULE_FIXED_WIDTH:
            # FIGURES ALONE, OR THE WALK ENDS: a cell that is not is no
            # column of one width (`fixed_width`), so a column of cents the
            # band rule refused costs rule C one cell rather than a walk (the
            # Codex review of landing R4, item 6, tries rule C after the
            # band's text fails).
            if not _figures(text):
                return False, bare, dated
            standing += [text]
            continue
        if numerator % denominator:
            not_whole = not_whole + 1
            if found.contacts:
                with_contact = with_contact + 1
            most_places = max(most_places, figures_after_the_mark(written))
            most_significant = max(most_significant, significant_figures(written))
        whole = abs(numerator) // denominator
        if low <= numerator / denominator < high:
            width = len(f"{whole}")
            widths[width] = (widths[width] if width in widths else 0) + 1
    if tally < needed:
        return False, bare, dated
    if rule == RULE_MIDNIGHT:
        return len(different) >= REST_LEAST and off_the_step, bare, dated
    if rule == RULE_FIXED_WIDTH:
        return fixed_width(standing) >= FIXED_WIDTH_LEAST, bare, dated
    if len(widths) > 1:
        return False, bare, dated
    if rule == RULE_BAND and found.contacts and 2 * with_contact > rest:
        return False, bare, dated
    if (
        rule == RULE_BAND
        and not found.contacts
        and found.unit >= DAY
        and not_whole
        and most_places < DAY_TIME_PLACES
        and most_significant < DAY_TIME_SIGNIFICANT
    ):
        return False, bare, dated
    return True, bare, dated


def _contacts_fit(present: "list[str]", member: str, needed: int, mark: str) -> bool:
    """Whether a column is counts of a member with contacts: enough of them, mostly with none."""
    tally = 0
    with_contact = 0
    for text in present:
        written = counted(member, text, mark)
        if written is None:
            continue
        tally = tally + 1
        numerator, denominator = exact_value(written)
        if numerator % denominator:
            with_contact = with_contact + 1
    return tally >= needed and 2 * with_contact <= tally


def _offered(
    ordered: "list[float]",
    hits: "list[str]",
    total: int,
    present: "list[str]",
    needed: int,
    mark: str = POINT,
) -> "tuple[str, ...]":
    """Every member counting in a hit's unit that reads the column inside 1900 to 2050.

    A member with contacts (`days-since-1840`) is offered beside a hit only
    where the cells are its counts and at least half write no contact
    number, as rule A asks of it: an Excel column of date-times writes a
    time after the point, which that member would read as contact numbers.
    """
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
        if rest - inside > _strays_allowed(total):
            continue
        if found.contacts and not _contacts_fit(present, member, needed, mark):
            continue
        offered += [member]
    return tuple(offered)


# The set-aside numbers a question may name, as words of this package's
# own, in the order a sentence names them.
_ASIDE_WORDS = ("0", "-1", "1900-01-01", "9999-12-31", "60")


def _set_aside_words(
    ordered: "list[float]", members: "list[str]", floor: int
) -> "tuple[str, ...]":
    """Which of the set-aside numbers the column holds, as this package's own words.

    A NUMBER IS NAMED ONLY WHERE THE CENSUS LINE OF CELLS HOLDS IT
    (`parsing.census_floor`, plan P4-D65.1): fewer, and the word would say
    that a value one row holds -- a birth on 1 January 1970 in Unix
    seconds -- is in the table; it is still set aside, and the place
    reads `ASIDE_NONE`.
    """
    line = parsing.census_floor(floor)
    seen: "dict[str, int]" = {}
    for member in members:
        for number, word in set_aside_named(member):
            if _count_of_value(ordered, float(number)) >= line:
                seen[word] = 1
    return tuple(word for word in _ASIDE_WORDS if word in seen)


def heap_counts(
    words: "tuple[str, ...]", members: "tuple[str, ...]"
) -> "frozenset[float]":
    """Every count a heap of placeholders may stand on, for NF114's walk (landing R4).

    THE COUNT, IN EVERY SYSTEM OFFERED (``members``), OF EACH SET-ASIDE
    WORD THE QUESTION NAMES (``words``, NF113's): a column holds a named
    word under some count of one of the systems that wrote it, and which
    one is not published, so each is a place a heap may stand -- and one
    system's placeholder read as another system's date is no date of the
    column (the second review of landing R4, item 3: Excel's 31 December
    9999 read as Epic days was "1957 to 9941"). Both NF114's producer and
    the guard beside the loader ask it of the same published words.

    Guarantees: a function of the two. Raises KeyError for a word outside
    `MEMBERS`. No I/O of any kind.
    """
    found: "dict[float, int]" = {}
    for member in members:
        for number, word in set_aside_named(member):
            if word in words:
                found[float(number)] = 1
    return frozenset(found)


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
    slots: "list[str]" = []
    for word in _ASIDE_WORDS:
        slots += [word if word in words else ASIDE_NONE]
    return tuple(slots)


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
    named: "list[str]" = []
    for word in slots:
        if word in _ASIDE_WORDS:
            named += [_ASIDE_SAID[word]]
    return listed(tuple(named))


# The words a sentence of question Q3 may carry: the members, the rules,
# the set-aside numbers and the word for none of them, all this package's
# own (contract 4.5.1).
NOTE_WORDS = MEMBERS + RULES + _ASIDE_WORDS + (ASIDE_NONE,)


def rule_said(rule: str) -> str:
    """What NF113 says a rule saw, opening its sentence.

    "NEARLY EVERY", NEVER "EVERY": each rule lets text cells stand to the
    date role's own line, the set-aside numbers stand beside the rest and
    one cell in a hundred stray outside the band, so a sentence saying
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

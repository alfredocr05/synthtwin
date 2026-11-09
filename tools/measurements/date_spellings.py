"""The spellings of a day this module writes, built combinatorially in six families, and the held-date room's sweep over them (plan P4-D457).

Batch 4q's fix round 3. Three rounds closed the held-date room against
hand lists of spellings (Codex's review of batch 4q, item 2: `Jan 01,
2028`; the verifies of fix rounds 1 and 2: `Jan 01, 28`, `28-01-01`, then
the compact stamps `202801010915` and a clock written first, `09:15
01/01/28`), and each hand list left a neighbour open. This module writes
the spellings instead of listing them: the date part in every order of
year, month and day; a year of one, two, three and four figures, the two
with an apostrophe too; a month in figures (padded and not), in three
letters, with a point, and in full, in upper, lower and title case; a day
in figures (padded and not) and with an ordinal's letters; the fields
parted by nothing, a hyphen, a slash, a point, a space or a comma; and,
around it, a clock (none; after it with a space, glued with nothing,
glued with a `T`; with seconds, a fraction after a point, AM or PM, a
zone; run on in the figures of a compact date; before it), a weekday
word, brackets or a label.

Batch 4q's fix round 4 (the verify of fix round 3) adds the families of
the product's own date vocabulary the verify found open, each written in
full rather than sampled: EVERY ZONE WORD AND OFFSET of the layout
grammar (`Z`, `z`, `UTC`, `GMT`, `+HH:MM`, `+HHMM`, `+HH`, either sign)
and the room's other clock zones, and every meridiem, glued to a clock
run on in a compact date's figures (`20280101091530Z`, `202801010915AM`)
and after or glued to a clock; SAS's DATETIME and DATEAMPM at every
width from 7 to 40 (`01JAN28:09:15:30`, `01JAN28:09:15:30 AM`); a day
written as a count in every counting system the product names
(`date_counts.MEMBERS`: Excel's `46757`, Unix seconds, ...); a day of
the year (`%Y%j`, `%y%j`, `%y-%j`, `%Y-%j`); and a clock glued to the
date with an hour of one figure (`01/05/289:15`).

THE SWEEP (`open_spellings`) asks, of each spelling of a day whose year
-- read every way its figures can be (`years_named`: a year of four
figures names itself; one of one to three figures, its last figures in
both centuries) -- is one the room may take (from
`taxonomy.MADE_UP_FIRST_YEAR`), whether the readings the room holds for
a real cell (`taxonomy.cell_date_years`, with the cross rule: a
two-figure year holds 19yy and 20yy) hold that year. A spelling whose
year is held is CLOSED; one whose year is not is OPEN, and the room may
take a year a real cell names. The unit gate
(tests/test_held_dates_spellings.py) reads the sweep; `main` prints its
counts by class.

Nothing here reads a table or writes a file. Run from the repository:

    PYTHONPATH=src python tools/measurements/date_spellings.py [--every N]
"""

from __future__ import annotations

import dataclasses
import datetime
import sys

MONTH_NAMES = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)
WEEKDAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

# The days spelled: years whose last two figures are 28 or more (so a
# two-figure spelling names a year of the room too), a day of 12 or less
# and one past it (read month first and day first, or one way only), a
# two-figure year of 31 or less (a day's number too) and one past it, a
# leap day, and four-figure years far into the room's stepped shares.
DAYS = (
    (2028, 1, 5), (2031, 12, 25), (2045, 3, 13), (2099, 11, 30),
    (2060, 2, 29), (2137, 7, 4), (3050, 10, 1), (9998, 8, 12),
)
ORDERS = ("YMD", "YDM", "MDY", "MYD", "DMY", "DYM")
YEAR_FORMS = ("four", "three", "two", "two_apostrophe", "one")
MONTH_FORMS = (
    "figures", "figures_unpadded", "word", "word_upper", "word_lower", "word_point",
    "name", "name_upper", "name_lower",
)
DAY_FORMS = ("figures", "figures_unpadded", "ordinal")
# The marks parting the three fields: the first between the first and the
# second field, the second between the second and the third.
SEPARATORS = (
    ("none", "", ""), ("hyphen", "-", "-"), ("slash", "/", "/"), ("point", ".", "."),
    ("space", " ", " "), ("comma", ", ", ", "), ("space_comma", " ", ", "), ("comma_space", ", ", " "),
)
CLOCKS = (
    "none", "after", "after_seconds", "after_fraction", "after_meridiem", "after_meridiem_points",
    "after_zone_word", "after_offset", "after_run_on", "glued", "glued_t", "glued_t_zone",
    "run_on", "run_on_seconds", "run_on_t", "run_on_t_zone", "run_on_fraction",
    "before", "before_seconds", "before_meridiem", "before_glued",
)
# FIX ROUND 4, a clock glued to the date with an hour of one figure (the verify of fix round 3, CARRY 4: no
# generated clock glued an unpadded hour, so a reading that never took a glued clock's hour as its last figure
# alone left the unit gate green). Kept apart from `CLOCKS` so that round 3's layers are written as before.
GLUED_UNPADDED_CLOCKS = ("glued_unpadded", "glued_unpadded_seconds")
# The clocks written run on in a compact date's figures: only beside a
# date part of figures alone with no mark between its fields.
_RUN_ON = ("run_on", "run_on_seconds", "run_on_t", "run_on_t_zone", "run_on_fraction")
DECORATIONS = ("none", "weekday", "weekday_full", "weekday_after", "brackets", "parentheses", "label")

# FIX ROUND 4, THE ZONES AND THE MERIDIEMS (the verify of fix round 3, blocker 1). Every zone word and offset
# the product's layout grammar names (`parsing._LAYOUT_ZULU_FIELDS` and `_LAYOUT_SIGNED_FIELDS`, either sign),
# the other zone words of the room's clock reader, and every meridiem in its cases and points.
ZONE_WORDS = (
    "Z", "z", "UTC", "GMT", "utc", "gmt",
    "EST", "EDT", "CST", "CDT", "MST", "MDT", "PST", "PDT", "CET", "CEST", "BST",
)
ZONE_OFFSETS = ("+05:00", "-06:00", "+0500", "-0600", "+05", "-06")
MERIDIEMS = ("AM", "PM", "am", "pm", "A.M.", "P.M.", "a.m.", "p.m.")
# Each zone's placement: run on in a compact date's figures (with minutes, seconds, a fraction, or after a `T`),
# and after a clock written with its colons, spaced or glued; each meridiem's likewise.
ZONE_PLACES = {
    "zone_run_on": "0915{}", "zone_run_on_seconds": "091530{}", "zone_run_on_fraction": "091530.000{}",
    "zone_t_run_on": "T091530{}", "zone_after": " 09:15:30{}", "zone_glued": "09:15:30{}",
    "zone_t_glued": "T09:15:30{}",
}
MERIDIEM_PLACES = {
    "meridiem_run_on": "0915{}", "meridiem_run_on_seconds": "091530{}", "meridiem_after": " 9:15 {}",
    "meridiem_glued": "9:15{}",
}
# The placements run on in the figures: only beside a date part of figures alone with no mark between its fields.
_RUN_ON_PLACES = ("zone_run_on", "zone_run_on_seconds", "zone_run_on_fraction", "zone_t_run_on", "meridiem_run_on",
                  "meridiem_run_on_seconds")


def _zone_clocks() -> "list[str]":
    """Every zone and meridiem clock's name: its placement, a colon, the word or offset."""
    found: "list[str]" = []
    for place in ZONE_PLACES:
        for word in ZONE_WORDS + ZONE_OFFSETS:
            found += [f"{place}:{word}"]
    for place in MERIDIEM_PLACES:
        for word in MERIDIEMS:
            found += [f"{place}:{word}"]
    return found


ZONE_CLOCKS = tuple(_zone_clocks())

# FIX ROUND 4, SAS'S DATETIME AND DATEAMPM (the verify of fix round 3, blocker 2): `DATETIMEw.d` and
# `DATEAMPMw.d` at a width w from 7 to 40 and d figures of a second write the longest of their forms the width
# holds, right-aligned: the date `ddMONyy` (or `ddMONyyyy`); then `:hh`, `:hh:mm`, or `:hh:mm:ss` and d figures of a
# second; DATEAMPM a 12-hour clock and its meridiem. Every such form is written (`sas_texts`), so every width's.
SAS_WIDTHS = tuple(range(7, 41))
SAS_DECIMALS = (0, 1, 2, 3, 6)
# Two moments a day: a morning clock with a fraction of a second, and an evening one past 12 (the meridiem's other
# half): hour, minute, second, microsecond.
SAS_TIMES = ((9, 15, 30, 123456), (21, 45, 5, 0))

# FIX ROUND 4, DATES WRITTEN AS COUNTS (the verify of fix round 3, blocker 3): the twelve counting systems the
# product names (`date_counts.MEMBERS`, the words of `--date-count`), each written here by its own epoch and unit,
# never by the product's reader: (the word, the unit in seconds or 0 for days, the epoch).
COUNT_SYSTEMS = (
    ("excel-1900", 0, datetime.date(1899, 12, 30)),
    ("excel-1904", 0, datetime.date(1904, 1, 1)),
    ("days-since-1960", 0, datetime.date(1960, 1, 1)),
    ("seconds-since-1960", 1, datetime.date(1960, 1, 1)),
    ("milliseconds-since-1960", 1_000, datetime.date(1960, 1, 1)),
    ("days-since-1970", 0, datetime.date(1970, 1, 1)),
    ("seconds-since-1970", 1, datetime.date(1970, 1, 1)),
    ("milliseconds-since-1970", 1_000, datetime.date(1970, 1, 1)),
    ("microseconds-since-1970", 1_000_000, datetime.date(1970, 1, 1)),
    ("nanoseconds-since-1970", 1_000_000_000, datetime.date(1970, 1, 1)),
    ("days-since-1840", 0, datetime.date(1840, 12, 31)),
    ("seconds-since-1582", 1, datetime.date(1582, 10, 14)),
)
# The clock a count's moment is written at (09:15:30), in seconds of the day.
_COUNT_SECONDS = 9 * 3600 + 15 * 60 + 30

# FIX ROUND 4, A DAY OF THE YEAR (the verify of fix round 3, blocker 4): the year then the day's three figures,
# compact or with a hyphen, the year in four figures or two.
DAY_OF_YEAR_FORMS = (("%Y%j", "four"), ("%y%j", "two"), ("%y-%j", "two"), ("%Y-%j", "four"))


@dataclasses.dataclass(frozen=True)
class Spelling:
    """One cell's text, the day it spells, the width its year is written in, and its class."""

    text: str
    day: "tuple[int, int, int]"
    year_width: int
    order: str
    year_form: str
    month_form: str
    day_form: str
    separator: str
    clock: str
    decoration: str
    # fix round 4: "date" for the date part's product, else the family ("sas", "count", "day_of_year")
    kind: str = "date"

    def family(self) -> str:
        """The class the counts are kept by: the order, the year's width, the month's kind, the separator, the
        clock and the decoration; for fix round 4's families, the family, the year's width and the form."""
        if self.kind != "date":
            return f"{self.kind} y{self.year_width} {self.clock} {self.decoration}"
        month = "figures" if self.month_form.startswith("figures") else "word"
        return (
            f"{self.order} y{self.year_width}{'a' if self.year_form == 'two_apostrophe' else ''} "
            f"m-{month} sep-{self.separator} clock-{self.clock} {self.decoration}"
        )


def _year_text(year: int, form: str) -> str:
    if form == "four":
        return f"{year:04d}"
    if form == "three":
        return f"0{year % 100:02d}"
    if form == "two":
        return f"{year % 100:02d}"
    if form == "two_apostrophe":
        return f"'{year % 100:02d}"
    return f"{year % 10}"


def _month_text(month: int, form: str) -> str:
    name = MONTH_NAMES[month - 1]
    texts = {
        "figures": f"{month:02d}", "figures_unpadded": f"{month}", "word": name[0:3],
        "word_upper": name[0:3].upper(), "word_lower": name[0:3].lower(), "word_point": name[0:3] + ".",
        "name": name, "name_upper": name.upper(), "name_lower": name.lower(),
    }
    return texts[form]


def _day_text(day: int, form: str) -> str:
    if form == "figures":
        return f"{day:02d}"
    if form == "figures_unpadded":
        return f"{day}"
    ending = "th" if 10 <= day % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"{day}{ending}"


def _readable(order: str, year_form: str, month_form: str, day_form: str, separator: str) -> bool:
    """Whether a person may write the date part so: fields with no mark between them are padded figures or
    words, never an unpadded field, an ordinal or a year of one figure run into another field."""
    if separator != "none":
        return True
    return month_form != "figures_unpadded" and day_form == "figures" and year_form in ("four", "three", "two")


def date_part(day: "tuple[int, int, int]", order: str, year_form: str, month_form: str, day_form: str,
              separator: str) -> str:
    """The day written in ``order`` with its fields in the forms named and parted by ``separator``."""
    year, month, date = day
    fields = {"Y": _year_text(year, year_form), "M": _month_text(month, month_form), "D": _day_text(date, day_form)}
    first, second = "", ""
    for name, one, two in SEPARATORS:
        if name == separator:
            first, second = one, two
    return fields[order[0]] + first + fields[order[1]] + second + fields[order[2]]


def with_clock(text: str, clock: str) -> str:
    """``text`` with the clock 09:15 (30 seconds, a fraction, a meridiem, a zone) written as ``clock`` says; a zone or
    meridiem clock (`ZONE_CLOCKS`) is its placement and its word, `zone_run_on:Z`."""
    if ":" in clock:
        place, word = clock.split(":", 1)
        form = ZONE_PLACES[place] if place in ZONE_PLACES else MERIDIEM_PLACES[place]
        return text + form.format(word)
    written = {
        "none": text, "after": text + " 09:15", "after_seconds": text + " 09:15:30",
        "after_fraction": text + " 09:15:30.123456", "after_meridiem": text + " 9:15 AM",
        "after_meridiem_points": text + " 9:15 p.m.", "after_zone_word": text + " 09:15 UTC",
        "after_offset": text + " 09:15:30+05:00", "after_run_on": text + " 0915", "glued": text + "09:15",
        "glued_t": text + "T09:15", "glued_t_zone": text + "T09:15:30Z", "run_on": text + "0915",
        "run_on_seconds": text + "091530", "run_on_t": text + "T091530", "run_on_t_zone": text + "T091530Z",
        "run_on_fraction": text + "091530.000000", "before": "09:15 " + text,
        "before_seconds": "09:15:30 " + text, "before_meridiem": "9:15 AM " + text, "before_glued": "09:15" + text,
        "glued_unpadded": text + "9:15", "glued_unpadded_seconds": text + "9:15:30",
    }
    return written[clock]


def run_on(clock: str) -> bool:
    """Whether ``clock`` is written run on in a compact date's figures (only beside a date part of figures alone
    with no mark between its fields)."""
    return clock in _RUN_ON or clock.split(":", 1)[0] in _RUN_ON_PLACES


def sas_texts(moment: datetime.datetime, ampm: bool) -> "list[str]":
    """Every text SAS's DATETIMEw.d (or, with ``ampm``, DATEAMPMw.d) may write ``moment`` in, at any width w of
    `SAS_WIDTHS` and d of `SAS_DECIMALS`: each width writes the longest of these forms it holds, right-aligned, so
    every form is written here, bare and right-aligned in the widest field. The forms: the date `ddMONyy` and
    `ddMONyyyy`; then `:hh`, `:hh:mm`, or `:hh:mm:ss` with d figures of a second; the year in two figures or
    four; DATEAMPM's hour on the 12-hour dial, padded or not, and its meridiem. Each text once, in order."""
    hours = [f"{moment.hour:02d}"]
    if ampm:
        dial = moment.hour % 12 or 12
        hours = [f"{dial:02d}", f"{dial}"]
    half = (" AM" if moment.hour < 12 else " PM") if ampm else ""
    month = moment.strftime("%b").upper()
    forms: "list[str]" = []
    for year in (f"{moment.year % 100:02d}", f"{moment.year:04d}"):
        day = f"{moment.day:02d}{month}{year}"
        forms += [day]
        for hour in hours:
            forms += [f"{day}:{hour}{half}", f"{day}:{hour}:{moment.minute:02d}{half}"]
            for decimals in SAS_DECIMALS:
                fraction = ("." + f"{moment.microsecond:06d}"[0:decimals]) if decimals else ""
                forms += [f"{day}:{hour}:{moment.minute:02d}:{moment.second:02d}{fraction}{half}"]
    widest = SAS_WIDTHS[len(SAS_WIDTHS) - 1]
    found: "list[str]" = []
    for form in forms:
        for text in (form, " " * (widest - len(form)) + form):
            if text not in found:
                found += [text]
    return found


def count_texts(day: "tuple[int, int, int]", system: "tuple[str, int, datetime.date]") -> "list[str]":
    """The day written as a count of ``system`` (a word of `COUNT_SYSTEMS`) at 09:15:30: the whole count, and for a
    system counting days the count with the time of day after a point and after a comma."""
    _word, unit, epoch = system
    days = (datetime.date(*day) - epoch).days
    if unit == 0:
        fraction = f"{_COUNT_SECONDS * 1_000_000 // 86_400:06d}"
        return [f"{days}", f"{days}.{fraction}", f"{days},{fraction}"]
    return [f"{(days * 86_400 + _COUNT_SECONDS) * unit}"]


def day_of_year_text(day: "tuple[int, int, int]", form: str) -> str:
    """The day written as its year and its day of the year in ``form`` (`DAY_OF_YEAR_FORMS`)."""
    return datetime.date(*day).strftime(form)


def with_decoration(text: str, decoration: str) -> str:
    """``text`` beside a weekday word, inside brackets or after a label, as ``decoration`` says."""
    written = {
        "none": text, "weekday": "Sat " + text, "weekday_full": "Saturday, " + text,
        "weekday_after": text + " (Sat)", "brackets": "[" + text + "]", "parentheses": "(" + text + ")",
        "label": "DOB: " + text,
    }
    return written[decoration]


def _width(year_form: str) -> int:
    return {"four": 4, "three": 3, "two": 2, "two_apostrophe": 2, "one": 1}[year_form]


def _cores() -> "list[tuple[str, str, str, str, str]]":
    """Every date part's form: order, year, month, day and separator, as a person may write them."""
    found: "list[tuple[str, str, str, str, str]]" = []
    for order in ORDERS:
        for year_form in YEAR_FORMS:
            for month_form in MONTH_FORMS:
                for day_form in DAY_FORMS:
                    for separator, _one, _two in SEPARATORS:
                        if _readable(order, year_form, month_form, day_form, separator):
                            found += [(order, year_form, month_form, day_form, separator)]
    return found


def spellings(every: int = 1) -> "list[Spelling]":
    """The generated spellings, in a fixed order (``every``: each that many-th of them, for a quick sweep).

    Four layers, each a full product but for the day, which turns over
    `DAYS` from one spelling to the next: every date part's form, bare,
    at every day; every date part's form with each clock; every date
    part's form with each decoration; and the date parts of figures and
    of three-letter words, padded, with a year of four or two figures,
    with each clock AND each decoration. Fix round 4 adds five more,
    after those four, which are written as before: the glued clock with
    an hour of one figure (`GLUED_UNPADDED_CLOCKS`) beside every date
    part, each decoration too beside the fourth layer's; each zone and
    meridiem clock (`ZONE_CLOCKS`) run on in every compact date part, and
    after or glued to a clock beside the fourth layer's date parts, each
    decoration too where run on; SAS's DATETIME and DATEAMPM at every day,
    both moments and every decoration; every counting system's counts at
    every day; and each day-of-the-year form at every day and decoration.
    """
    found: "list[Spelling]" = []
    cores = _cores()
    turn = 0

    def add(core: "tuple[str, str, str, str, str]", day: "tuple[int, int, int]", clock: str,
            decoration: str) -> None:
        nonlocal found
        order, year_form, month_form, day_form, separator = core
        if run_on(clock) and (separator != "none" or not month_form.startswith("figures")):
            return
        text = with_decoration(with_clock(date_part(day, order, year_form, month_form, day_form, separator), clock),
                               decoration)
        found += [Spelling(text, day, _width(year_form), order, year_form, month_form, day_form, separator,
                           clock, decoration)]

    def fourth(core: "tuple[str, str, str, str, str]") -> bool:
        return core[1] in ("four", "two") and core[2] in ("figures", "word") and core[3] == "figures"

    for core in cores:
        for day in DAYS:
            add(core, day, "none", "none")
    for core in cores:
        for clock in CLOCKS[1:]:
            turn += 1
            add(core, DAYS[turn % len(DAYS)], clock, "none")
    for core in cores:
        for decoration in DECORATIONS[1:]:
            turn += 1
            add(core, DAYS[turn % len(DAYS)], "none", decoration)
    for core in cores:
        if fourth(core):
            for clock in CLOCKS[1:]:
                for decoration in DECORATIONS[1:]:
                    turn += 1
                    add(core, DAYS[turn % len(DAYS)], clock, decoration)
    # fix round 4: the glued clock with an hour of one figure, as `CLOCKS` are written (each core; the fourth
    # layer's cores with each decoration)
    for core in cores:
        for clock in GLUED_UNPADDED_CLOCKS:
            turn += 1
            add(core, DAYS[turn % len(DAYS)], clock, "none")
            if fourth(core):
                for decoration in DECORATIONS[1:]:
                    turn += 1
                    add(core, DAYS[turn % len(DAYS)], clock, decoration)
    # ...the zones and meridiems
    for core in cores:
        for clock in ZONE_CLOCKS:
            if run_on(clock) or fourth(core):
                turn += 1
                add(core, DAYS[turn % len(DAYS)], clock, "none")
            if run_on(clock) and fourth(core):
                for decoration in DECORATIONS[1:]:
                    turn += 1
                    add(core, DAYS[turn % len(DAYS)], clock, decoration)
    # ...SAS's DATETIME and DATEAMPM (each form bare with every decoration, and right-aligned), the counts and the
    # day of the year
    for day in DAYS:
        for hour, minute, second, micro in SAS_TIMES:
            moment = datetime.datetime(day[0], day[1], day[2], hour, minute, second, micro)
            for ampm in (False, True):
                name = "sas_dateampm" if ampm else "sas_datetime"
                for text in sas_texts(moment, ampm):
                    bare = text.strip()
                    width = 4 if bare[5:9] == f"{day[0]:04d}" else 2
                    shape = "".join("9" if "0" <= one <= "9" else "A" if one.isalpha() else one for one in bare)
                    for decoration in DECORATIONS if text == bare else ("none",):
                        found += [Spelling(with_decoration(text, decoration), day, width, "DMY",
                                           "four" if width == 4 else "two", "word_upper", "figures", "none",
                                           f"{name}:{shape}", decoration, "sas")]
        for system in COUNT_SYSTEMS:
            for text in count_texts(day, system):
                found += [Spelling(text, day, 4, "count", "four", "count", "count", "none", system[0], "none",
                                   "count")]
        for form, year_form in DAY_OF_YEAR_FORMS:
            for decoration in DECORATIONS:
                found += [Spelling(with_decoration(day_of_year_text(day, form), decoration), day, _width(year_form),
                                   "YD", year_form, "day_of_year", "figures", "-" if "-" in form else "none", form,
                                   decoration, "day_of_year")]
    if every > 1:
        return [found[place] for place in range(0, len(found), every)]
    return found


def years_named(spelling: Spelling) -> "tuple[int, ...]":
    """The years a spelling's year names: four figures name themselves; one to three figures name their last
    figures (one, or two) in both centuries -- `Mar 05, 45` names 1945 and 2045."""
    year = spelling.day[0]
    if spelling.year_width == 4:
        return (year,)
    last = year % 10 if spelling.year_width == 1 else year % 100
    return (1900 + last, 2000 + last)


def held_by(cell_years: "tuple[list[int], list[int]]") -> "set[int]":
    """The four-figure years a cell's readings hold, a two-figure year held as 19yy and 20yy (the cross rule)."""
    four, two = cell_years
    held = set(four)
    for year in two:
        held.add(1900 + year)
        held.add(2000 + year)
    return held


def open_spellings(spelled: "list[Spelling]", reader: object, first_year: int) -> "list[tuple[Spelling, list[int]]]":
    """Each spelling naming a year from ``first_year`` that ``reader`` (a cell's text -> its held four- and
    two-figure years, `taxonomy.cell_date_years`) does not hold, with those years."""
    found: "list[tuple[Spelling, list[int]]]" = []
    for spelling in spelled:
        named = [year for year in years_named(spelling) if year >= first_year]
        if not named:
            continue
        held = held_by(reader(spelling.text))  # type: ignore[operator]
        missed = [year for year in named if year not in held]
        if missed:
            found += [(spelling, missed)]
    return found


def family_of(spelling: Spelling) -> str:
    """The family a spelling is counted under: round 3's date parts and clocks (`date_part`), and fix round 4's
    glued clock with an hour of one figure, zones and meridiems, SAS, counts and a day of the year."""
    if spelling.kind != "date":
        return spelling.kind
    if ":" in spelling.clock:
        return "zone_or_meridiem"
    if spelling.clock in GLUED_UNPADDED_CLOCKS:
        return "glued_unpadded_hour"
    return "date_part"


def main(arguments: "list[str]") -> int:
    from synthtwin import taxonomy

    every = int(arguments[arguments.index("--every") + 1]) if "--every" in arguments else 1
    spelled = spellings(every)
    naming = [one for one in spelled if any(year >= taxonomy.MADE_UP_FIRST_YEAR for year in years_named(one))]
    found = open_spellings(spelled, taxonomy.cell_date_years, taxonomy.MADE_UP_FIRST_YEAR)
    by_family: "dict[str, list[str]]" = {}
    for spelling, _missed in found:
        texts = by_family.get(spelling.family(), [])
        texts += [spelling.text]
        by_family[spelling.family()] = texts
    print(f"spellings {len(spelled)}; naming a year of the room {len(naming)}; open {len(found)}; "
          f"open classes {len(by_family)}")
    # ...and by family: the date part's product and fix round 4's zones and meridiems, SAS, counts, day of the year
    kinds: "dict[str, list[int]]" = {}
    for one in spelled:
        counted = kinds.get(family_of(one), [0, 0, 0])
        counted[0] += 1
        counted[1] += 1 if any(year >= taxonomy.MADE_UP_FIRST_YEAR for year in years_named(one)) else 0
        kinds[family_of(one)] = counted
    for spelling, _missed in found:
        kinds[family_of(spelling)][2] += 1
    for kind in sorted(kinds):
        print(f"  family {kind}: spellings {kinds[kind][0]}; naming a year of the room {kinds[kind][1]}; "
              f"open {kinds[kind][2]}")
    for family in sorted(by_family):
        print(f"  {family}: {len(by_family[family])} open, e.g. {by_family[family][0:3]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

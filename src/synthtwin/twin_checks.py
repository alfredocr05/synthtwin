"""The five twin-versus-real checks a twin passes before it leaves the protected computer.

WHERE THIS RUNS. Inside the protected computer, where the real table and
its twin both exist: `python -m synthtwin.twin_checks REAL TWIN`. Both
files are read through the product's own reader (`reading.read_table`,
in groups of columns), so a twin is read the way its source was. The
checks compare the two tables and print COUNTS, RATES and a verdict:
never a cell of either table, never a row's place in a file and never a
person's key. Counts under 11 may be printed: the report is read inside
the protected computer and carries no value (the owner's ruling of
2026-11-18, question 3).

THE FIVE CHECKS.

- C1, exact row copy: twin rows equal to a real row on every column but
  the identifiers (a twin's identifiers are made up, and C4 reads them)
  once every cell is written in one normal spelling (a number at its own
  places, a date as year, month, day and clock, a label trimmed and
  folded, every spelling of "no value" one code).
- C2, nearest-record distance: for up to `QUERY_ROWS` twin rows, the
  distance to the nearest row of one real half (numbers and dates in
  standard units, a label a mismatch of one, a missing value against a
  present one a mismatch of one), against up to `QUERY_ROWS` real rows'
  distances to the nearest row of the other half. At the fresh
  distances' 0.1st, 1st and 5th percentiles, the share of the twin's
  distances at or under each may pass the fresh share by no more than
  chance allows (`_closer_share`); the percentiles themselves are
  printed beside it.
- C3, patient copy: twin patients of five rows or more whose readings,
  or whose dates, are a real patient's (each patient's rows taken as a
  set, so a copy in another order, or with its rows written twice,
  still counts).
- C4, identifiers and dates: a twin cell of an identifier column equal
  to a real one of that column, read as one key (`parsing.merged_key`),
  a short list of persons' names among them (`a_listed_detail`); an
  age past 90 in a column named as an age; a text cell holding a
  person's details (the product's readers of names, telephone numbers,
  record numbers and addresses) equal to a real cell, or holding one of
  its names or numbers in other words (`elements`); and rare real dates
  (held by 1 to 10 people) written into the twin more often than a
  fresh draw writes them (a made-up day landing on a real calendar day
  by chance is the fresh draw's too), a date read at its calendar day
  wherever the real cell has no clock.
- C5, rare combination: twin rows that hold a combination of the
  quasi-identifier columns (every label column, every column of numbers
  of few levels, the whole year of an age, the first three characters
  of a place) that only one real row holds.

THE YARDSTICK IS A FRESH HALF, NEVER A CONSTANT. Chance makes copies:
two people share a common combination, a round number, a calendar day.
So C1, C3, C5 and the dates of C4 compare the twin with the real table
split in two halves by person (`seed`): each half plays a fresh draw
against the other. The twin's matches against each half are counted
beside each half's matches against the other, rate for rate, so a
reference of the same size stands behind both numbers; a copied row
lies in one half and is counted there. The allowance over the fresh
rate is 1 per 10,000 rows plus three standard errors of the two rates;
C1 drops the 1 per 10,000 where a column of numbers is written with
more than two decimals, as a table of measurements is, where chance
makes no exact copy. C2's yardstick is the real table itself: each real
row's nearest other real row. C4's identifiers, ages and details allow
none.

THE SEAM FOR THE INSIDE RECORD. Which column is the person, which are
identifiers, dates, ages and places is a `Plan`. `run_checks` reads one
from the real table with the product's readers of names and cells; a
caller that already holds the decisions (a record of the description)
hands it a plan made by `plan_from_roles` instead, and nothing else
changes.

THE QUARANTINE (`release`). A twin that fails is moved into a
quarantine folder the person names, never into the folder it would
have been released to, with its check report beside it; a twin that
passes is moved into the release folder. Up to `REDRAWS_MOST` redraws
are asked of a caller's `Redraw`, each new twin checked again. The
command line offers the quarantine; a redraw of only the failing rows
or patients needs the generator and is not built here.

ZONE AND REACH. A module of zone D: it reads the person's files only
through `reading`, writes only its report and moves only the twin it
was given, imports no random source (the halves and the rows it reads
come from a fixed integer mix of the seed, `_mix`), and every number it
prints is a count, a quotient of counts or a distance computed in an
order written out.
"""

import argparse
import dataclasses
import math
import pathlib
import sys

from synthtwin import asking, errors, parsing, reading, taxonomy
from synthtwin.paths import PathValidationError, validate_local_path

# The kinds a column is read as.
KIND_IDENTIFIER = "identifier"
KIND_DATE = "date"
KIND_NUMBER = "number"
KIND_LABEL = "label"
KIND_TEXT = "text"
KINDS = (KIND_IDENTIFIER, KIND_DATE, KIND_NUMBER, KIND_LABEL, KIND_TEXT)
# Two more roles a caller may give: a column of numbers named as an age,
# and an identifier column holding a place; and the person's answer that
# a column is no identifier.
ROLE_AGE = "age"
ROLE_PLACE = "place"
ROLE_NOT_IDENTIFIER = "not identifier"
ROLES = KINDS + (ROLE_AGE, ROLE_PLACE, ROLE_NOT_IDENTIFIER)

# A column of at most this many different present values is a label
# column: compared in C2 as equal or not, and part of C5's combination.
LABEL_LEVELS_MOST = 100
# The share, in thousandths, of the cells read that must read as dates,
# or as numbers, for a column to be read so.
READING_SHARE = 900
# The present cells read to decide a kind, spread evenly over the rows.
KIND_SAMPLE = 2000
# A text column whose different values cover this share of its present
# cells, in thousandths, is read as keys.
KEY_LIKE_SHARE = 900
# The share, in thousandths, of the different present cells read that
# must hold a person's details for a text column to be read as an
# identifier, and how many different cells are read.
DETAILS_SHARE = 500
DETAILS_SAMPLE = 400
# C3 reads patients of at least this many rows.
PATIENT_ROWS_LEAST = 5
# C4: an age above this, in a column named as an age, is past the top
# code (the product writes an age past 89 as 90).
AGE_TOP = 90
# C4: a real date held by at most this many people is a rare one.
RARE_HOLDERS_MOST = 10
# C2: the twin rows, and the real rows, whose nearest record is sought.
QUERY_ROWS = 20000
# C2: the rows read on each side of a row's place in one sorted probe,
# and the probes, each a sorted order of the real rows.
PROBE_WINDOW = 10
PROBES = 5
# C2: the percentiles of the fresh half's distances, in thousandths, at
# which the twin's distances are read.
DISTANCE_POINTS = (1, 10, 50)
# The allowance over a fresh half's rate: one row in this many.
MARGIN_ROWS = 10000
# Standard errors of the two rates added to the allowance.
NOISE_ERRORS = 3
# A column of numbers written with more than this many decimals, in at
# least half of its numbers, is one where chance makes no exact copy.
CHANCE_DECIMALS = 2
# C4's elements of a text cell (`elements`): the most words of a run of
# capitalised words read as one element, the marks set aside around a
# word, the marks that may part the figures of one number and how many of
# them may stand together.
ELEMENT_WORDS_MOST = 4
_WORD_MARKS = ".,;:!?()[]{}<>\"'`*|/\\"
_FIGURE_MARKS = " -./()+"
_FIGURE_GAP_MOST = 2
# C2: an exponent of two past which a twin's value is read as off the
# real column's scale altogether (`_encoded`).
_SCALED_MOST = 1000
# The most redraws `release` asks for.
REDRAWS_MOST = 3
# The seed of the halves when none is given.
DEFAULT_SEED = 1

# C2's encoding: a value in standard units times `_SCALE`, around the
# middle of an unsigned 16-bit range; its top is "no value".
_SCALE = 2048
_MIDDLE = 32768
_TOP = 65534
_NO_VALUE = 65535
# C2's label codes in one byte: an unseen label of the twin, no value.
_UNSEEN_LABEL = 254
_NO_LABEL = 255
# C2's probe keys: a block of labels above a place on a projection.
_BLOCK_MASK = (1 << 31) - 1
_PLACE_BITS = 24
_PLACE_MIDDLE = 1 << 23
_PLACE_TOP = (1 << 24) - 1
_WEIGHT_TOP = 1024
_PLACE_SHIFT = 13
_MASK = (1 << 64) - 1
_NOT_TEXT = "a cell must be text"
# One code for every spelling of "no value".
_MISSING = "\x00no value"
_SECONDS_A_DAY = 86400
# A memo's largest size: a column of many different values is read cell
# by cell rather than held twice.
_MEMO_MOST = 200000
# THE REPORT'S NAME, the twin's own stem, `-checks` and a text ending,
# joined where it is written: the report is no file of the three
# commands' run (profile, generate, validate), whose files the claim
# inventory counts from the constants that name them, as the private
# report's name is joined in `cli`.
_CHECKS_WORD = "checks"


def report_name(twin_name: str) -> str:
    """The name of the checks' report beside a twin of this name: its stem, `-checks`, a text ending.

    Guarantees: a fixed function of the name. Raises TypeError for a
    name that is not text. No I/O.
    """
    if not isinstance(twin_name, str):
        raise TypeError(_NOT_TEXT)
    return pathlib.Path(twin_name).stem + "-" + _CHECKS_WORD + "." + "txt"

# C2: a query no candidate was measured against yet.
_NONE_FOUND = -1.0
# C2: added to the seed for the half each twin person reads.
_TWIN_SALT = 0x5DEECE66D


def _digest(text: str) -> int:
    """A fixed whole number for a text: the same text gives the same number in every run.

    Python's own hash of a text changes from one run to the next, so the
    text's UTF-8 bytes are hashed as a tuple of small whole numbers,
    whose hash is fixed. Two different texts give two different numbers
    except by a chance of about one in 2 ** 64 a pair.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    return hash(tuple(bytes(text, "utf-8")))


_MISSING_DIGEST = _digest(_MISSING)


def _mix(value: int) -> int:
    """The 64-bit SplitMix64 finaliser of a whole number: a fixed, well-spread function, no random source."""
    mixed = (value + 0x9E3779B97F4A7C15) & _MASK
    mixed = ((mixed ^ (mixed >> 30)) * 0xBF58476D1CE4E5B9) & _MASK
    mixed = ((mixed ^ (mixed >> 27)) * 0x94D049BB133111EB) & _MASK
    return mixed ^ (mixed >> 31)


def _half_of(seed: int, unit: int) -> int:
    """Which half, 0 or 1, the person or row numbered `unit` falls in under `seed`."""
    return _mix(((seed * 0x100000001B3) & _MASK) ^ unit) >> 63


def _day_number(year: int, month: int, day: int) -> int:
    """Days from 1970-01-01 to a date of the proleptic Gregorian calendar."""
    shifted = year - 1 if month <= 2 else year
    era = shifted // 400
    year_of_era = shifted - era * 400
    month_place = (month + 9) % 12
    day_of_year = (153 * month_place + 2) // 5 + day - 1
    day_of_era = year_of_era * 365 + year_of_era // 4 - year_of_era // 100 + day_of_year
    return era * 146097 + day_of_era - 719468


def _all_figures(text: str) -> bool:
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if not text:
        return False
    for character in text:
        if not "0" <= character <= "9":
            return False
    return True


def _pieces(text: str, mark: str) -> "list[str]":
    """The text cut at every `mark`."""
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(mark, str):
        raise TypeError(_NOT_TEXT)
    return text.split(mark)


def _clock_seconds(text: str) -> "int | None":
    """Seconds past midnight of a clock `9:15`, `09:15:30`, `09:15:30.250`, `9:15 PM` or `09:15Z`, or None."""
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    body = parsing.folded(text)
    meridiem = ""
    if body[-2:] in ("am", "pm"):
        meridiem = body[-2:]
        body = parsing.trimmed(body[:-2])
    elif body[-1:] == "z":
        body = body[:-1]
    parts = _pieces(body, ":")
    if len(parts) < 2 or len(parts) > 3:
        return None
    if len(parts) == 3:
        parts = [parts[0], parts[1], _pieces(parts[2], ".")[0]]
    for part in parts:
        if not _all_figures(part) or len(part) > 2:
            return None
    hour = int(parts[0])
    minute = int(parts[1])
    second = int(parts[2]) if len(parts) == 3 else 0
    if meridiem:
        if not 1 <= hour <= 12:
            return None
        hour = hour % 12 + (12 if meridiem == "pm" else 0)
    if hour > 23 or minute > 59 or second > 59:
        return None
    return hour * 3600 + minute * 60 + second


@dataclasses.dataclass(frozen=True)
class DateRead:
    """A date cell read: its normal spelling, its day (from 1970-01-01) and its second of the day, -1 with no clock."""

    spelling: str
    day: int
    second: int


def read_date(text: str) -> "DateRead | None":
    """A date, or a date with its clock, read into one normal spelling; None for any other cell.

    Dates are the forms `parsing.date_parts` reads (`2031-03-14`,
    `2031/03/14`, `03/14/2031`, `03-14-2031`), a clock after a space or
    a `T` or none (`_clock_seconds`). MIDNIGHT IS THE DAY ITSELF (the
    batch 4w Codex review, item 5): a clock of `00:00` or `00:00:00`
    reads as no clock, so `2031-03-14 00:00:00` and `2031-03-14` are one
    date (a twin repeating real days with midnight added was read as
    holding none of them). Guarantees: a fixed function of the text.
    Raises TypeError for a cell that is not text. No I/O.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    body = parsing.trimmed(text)
    clock = ""
    for place in range(len(body)):
        if body[place] == " " or (body[place] == "T" and place == 10):
            clock = parsing.trimmed(body[place + 1:])
            body = body[:place]
            break
    parts = parsing.date_parts(body)
    if parts is None:
        return None
    year = parts[1]
    month = parts[2]
    day = parts[3]
    second = -1
    if clock:
        found = _clock_seconds(clock)
        if found is None:
            return None
        second = found if found > 0 else -1
    spelling = f"{year:04d}-{month:02d}-{day:02d}"
    if second >= 0:
        spelling = spelling + f" {second}"
    return DateRead(spelling, _day_number(year, month, day), second)


@dataclasses.dataclass(frozen=True)
class NumberRead:
    """A number cell read: its normal spelling, its value and the decimals it was written with."""

    spelling: str
    value: float
    decimals: int


def read_number(text: str) -> "NumberRead | None":
    """A number in figures, read into one normal spelling at its own places; None for any other cell.

    The cell's core (`parsing.number_core`: brackets, minus signs and
    group marks read) must be a sign or none, figures, a point and
    figures or none, and an exponent or none. The normal spelling drops
    a plus sign, the zeros that open the whole part and the zeros that
    close the fraction, so `007.50` and `7.5` are one number. AN
    EXPONENT IS WRITTEN OUT (the batch 4w Codex review, item 18): its
    figures with the point moved by it (`_point_moved`), so `1e3`,
    `1.0E+03` and `1000` are one spelling, `1000`, and `1.999e-6` is
    `0.000001999`, its decimals the written-out fraction's.
    Guarantees: a fixed function of the text. Raises TypeError for a
    cell that is not text. No I/O.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    core = parsing.number_core(text)
    sign = ""
    if core[:1] in ("+", "-"):
        sign = core[:1]
        core = core[1:]
    mantissa = core
    exponent = ""
    for mark in ("e", "E"):
        pieces = _pieces(mantissa, mark)
        if len(pieces) == 2:
            mantissa = pieces[0]
            exponent = pieces[1]
        elif len(pieces) > 2:
            return None
    if exponent:
        figures = exponent[1:] if exponent[:1] in ("+", "-") else exponent
        if not _all_figures(figures):
            return None
    pieces = _pieces(mantissa, ".")
    if len(pieces) > 2:
        return None
    whole = pieces[0]
    fraction = pieces[1] if len(pieces) == 2 else ""
    if not whole and not fraction:
        return None
    if (whole and not _all_figures(whole)) or (fraction and not _all_figures(fraction)):
        return None
    written = (whole or "0") + "." + (fraction or "0") + ("e" + exponent if exponent else "")
    value = float(written)
    if not math.isfinite(value):
        return None
    if sign == "-":
        value = -value
    kept_whole = whole
    kept_fraction = fraction
    if exponent:
        kept_whole, kept_fraction = _point_moved(whole, fraction, exponent, value)
    decimals = len(kept_fraction)
    kept_whole = _without_opening_zeros(kept_whole)
    kept_fraction = _without_closing_zeros(kept_fraction)
    spelling = (kept_whole or "0") + ("." + kept_fraction if kept_fraction else "")
    if sign == "-" and spelling != "0":
        spelling = "-" + spelling
    return NumberRead(spelling, value, decimals)


def _point_moved(whole: str, fraction: str, exponent: str, value: float) -> "tuple[str, str]":
    """A number written with an exponent written out without one: its whole part's figures and its fraction's, the point moved by the exponent (`1.5`, `e3`: `1500` and none; `2`, `e-3`: `0` and `002`).

    A value that reads as zero is `0` and no fraction, whatever its
    exponent (so `0e999999` builds no long text). Any other finite value
    moves the point at most about 330 places past its figures, so the
    text built is short. Raises TypeError for a part that is not text.
    No I/O.
    """
    if not isinstance(whole, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(fraction, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(exponent, str):
        raise TypeError(_NOT_TEXT)
    if value == 0.0:
        return "0", ""
    figures = whole + fraction
    point = len(whole) + int(exponent)
    if point <= 0:
        return "0", "0" * (-point) + figures
    if point >= len(figures):
        return figures + "0" * (point - len(figures)), ""
    return figures[:point], figures[point:]


def _without_opening_zeros(figures: str) -> str:
    """Figures without the zeros that open them, one figure kept at the least (`007` is `7`, `000` is `0`)."""
    if not isinstance(figures, str):
        raise TypeError(_NOT_TEXT)
    start = 0
    while start < len(figures) - 1 and figures[start] == "0":
        start += 1
    return figures[start:]


def _without_closing_zeros(figures: str) -> str:
    """Figures without the zeros that close them (`500` is `5`, `000` is none)."""
    if not isinstance(figures, str):
        raise TypeError(_NOT_TEXT)
    end = len(figures)
    while end > 0 and figures[end - 1] == "0":
        end -= 1
    return figures[:end]


def a_persons_detail(text: str) -> bool:
    """Whether a cell holds a person's details by the product's readers.

    A person's name written whole (`taxonomy.a_persons_name`), identifier
    words inside it (`taxonomy.identifier_words_form`: a telephone
    number, a record number, a date beside words, an address), a social
    security number, a network address, a device's identifier or a
    serial number. Guarantees: a fixed function of the text. Raises
    TypeError for a cell that is not text. No I/O.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    return bool(
        taxonomy.a_persons_name(text)
        or taxonomy.identifier_words_form(text)
        or taxonomy.social_security_form(text)
        or taxonomy.a_network_address(text)
        or taxonomy.a_device_identifier(text)
        or taxonomy.a_serial_number(text)
    )


def a_listed_detail(text: str) -> bool:
    """Whether a value of a short category list holds a person's details (the batch 4w Codex review, item 3).

    A column of at most `LABEL_LEVELS_MOST` different values was read as
    labels before its values were looked at, so three persons' names
    cycled over 20,000 rows under a neutral heading went out unchanged
    with C4 not measured. Its values are read by the readers
    `a_persons_detail` reads a text cell with, two of them narrowed to a
    list's own words: the identifier words read without a month and a
    day (`taxonomy.identifier_words_form` with its dates set aside: a
    list of days is the dates' to read), and a name written whole
    (`taxonomy.a_persons_name`) only where none of its words is a role, a
    service, a source or a flag of the product's closed lists
    (`taxonomy.an_ordinary_family_name`): `Talvo Brisk` is a name;
    `Intensive Care`, `Day Unit`, `Not Recorded` and `Never Smoker` are
    labels. A STATED FALSE ALARM: two capitalised words that none of
    those lists holds (`Left Arm`, `Blue Cross`) read as a name too; the
    person's answer that the column is no identifier
    (`--not-identifier`) sets it aside. Guarantees: a fixed function of
    the text. Raises TypeError for a value that is not text. No I/O.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    return bool(
        taxonomy.identifier_words_form(text, False)
        or taxonomy.social_security_form(text)
        or taxonomy.a_network_address(text)
        or taxonomy.a_device_identifier(text)
        or taxonomy.a_serial_number(text)
        or (taxonomy.a_persons_name(text) and taxonomy.an_ordinary_family_name(text))
    )


def _small_word(word: str) -> str:
    """A word in small letters, the marks around it set aside (`_WORD_MARKS`)."""
    if not isinstance(word, str):
        raise TypeError(_NOT_TEXT)
    return word.strip(_WORD_MARKS).lower()


def _capital_word(word: str) -> str:
    """A word written with a capital first, in small letters, the marks around it set aside; '' for a word of one character or one that opens with no capital."""
    if not isinstance(word, str):
        raise TypeError(_NOT_TEXT)
    bare = word.strip(_WORD_MARKS)
    first = bare[:1]
    if len(bare) < 2 or first == first.lower():
        return ""
    return bare.lower()


def _stretches(run: "list[str]") -> "set[str]":
    """Every stretch of one to `ELEMENT_WORDS_MOST` words one after another inside a run, a space between them."""
    found: "set[str]" = set()
    for start in range(len(run)):
        stretch = ""
        for end in range(start, min(start + ELEMENT_WORDS_MOST, len(run))):
            stretch = run[end] if end == start else stretch + " " + run[end]
            found |= {stretch}
    return found


def _given_first(run: "list[str]") -> str:
    """A run written family name first, a comma after it (`brisk`, `talvo`), its given names put first (`talvo brisk`), at most `ELEMENT_WORDS_MOST` words."""
    out = ""
    for word in run[1:ELEMENT_WORDS_MOST]:
        out = word if not out else out + " " + word
    return out + " " + run[0]


def _names_from(run: "list[str]", first: int) -> "set[str]":
    """The names a run holds from its word `first` on: every stretch of two to `ELEMENT_WORDS_MOST` words opening there (`talvo brisk`, `talvo brisk monday`)."""
    found: "set[str]" = set()
    stretch = ""
    for end in range(first, min(first + ELEMENT_WORDS_MOST, len(run))):
        stretch = run[end] if end == first else stretch + " " + run[end]
        if end > first:
            found |= {stretch}
    return found


def _figure_runs(text: str) -> "list[str]":
    """The numbers of `taxonomy.IDENTIFIER_WORD_FIGURES` figures or more a text holds, each its figures alone: figures parted by at most `_FIGURE_GAP_MOST` marks of `_FIGURE_MARKS` are one number (`(319) 555-0142` is `3195550142`)."""
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    runs: "list[str]" = []
    current = ""
    gap = 0
    for character in text + "x":
        if "0" <= character <= "9":
            current = current + character
            gap = 0
        elif current and gap < _FIGURE_GAP_MOST and character in _FIGURE_MARKS:
            gap += 1
        else:
            if len(current) >= taxonomy.IDENTIFIER_WORD_FIGURES:
                runs += [current]
            current = ""
            gap = 0
    return runs


def elements(text: str, held: bool) -> "frozenset[str]":
    """THE IDENTIFIER ELEMENTS OF A TEXT CELL, read apart from the words around them (the batch 4w Codex review, item 4).

    C4 compared whole cells, so a real relative's name kept inside a
    remark worded another way was read as no copy. A capitalised word is
    one of two characters or more, once the marks around it are set
    aside, whose first is a capital; a run is a stretch of them one after
    another; every element is in small letters, a space between words.
    ``held`` (a real cell holding a person's details, `a_persons_detail`):
    the names of a run that follows a word naming a relative or a title,
    or opens with one (`taxonomy.RELATIVE_WORDS`, `taxonomy.NAME_TITLES`:
    `son Talvo Brisk` and `Son Talvo Brisk` give `talvo brisk`); of a run
    whose first word is closed by a comma (`Brisk, Talvo` gives `brisk
    talvo`, and `talvo brisk` too, `_given_first`); of the cell's runs
    where the whole cell is a person's name (`taxonomy.a_persons_name`)
    -- each name two to `ELEMENT_WORDS_MOST` words opening the run
    (`_names_from`); and every number of `taxonomy.IDENTIFIER_WORD_FIGURES`
    figures or more (`_figure_runs`). Not ``held`` (a cell looked up: the
    twin's): every stretch of one to `ELEMENT_WORDS_MOST` words inside a
    run (`_stretches`), a run whose first word is closed by a comma also
    given names first, and the same numbers. So the held elements are the
    names and numbers the readers
    found, never a capitalised phrase beside them (`Blood Bank`), and a
    cell looked up meets them wherever its own words put them. A STATED
    LIMIT: a person named by one word alone (`wife Mara`, `Dr. Okafor`)
    is no element (one capitalised word the twin writes anywhere would
    meet it by chance); such a remark is compared whole, as before.
    Numbers are written `#` and their figures. Guarantees: a fixed
    function of the two. Raises TypeError for a text that is not text.
    No I/O.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    found: "set[str]" = set()
    words = text.split()
    whole_name = held and taxonomy.a_persons_name(text)
    at = 0
    while at < len(words):
        if not _capital_word(words[at]):
            at += 1
            continue
        start = at
        run: "list[str]" = []
        while at < len(words) and _capital_word(words[at]):
            run += [_capital_word(words[at])]
            at += 1
        comma = len(run) > 1 and words[start][-1:] == ","
        if comma:
            found |= {_given_first(run)}
        if not held:
            found |= _stretches(run)
            continue
        before = _small_word(words[start - 1]) if start > 0 else ""
        opened = before in taxonomy.RELATIVE_WORDS or before in taxonomy.NAME_TITLES or whole_name or comma
        first = 0
        while first < len(run) - 1 and (run[first] in taxonomy.RELATIVE_WORDS or run[first] in taxonomy.NAME_TITLES):
            first += 1
            opened = True
        if opened:
            found |= _names_from(run, first)
    for figures in _figure_runs(text):
        found |= {"#" + figures}
    return frozenset(found)


def named_as_an_identifier(name: str) -> bool:
    """Whether a column's name says it holds an identifier element, by the product's readers of column names.

    A key or a person (`asking.named_as_a_key`, `asking.names_a_person`),
    persons' names, a line of an address, a place smaller than a state,
    a coordinate, or a device's numbers. Guarantees: a fixed function of
    the name. Raises TypeError for a name that is not text. No I/O.
    """
    if not isinstance(name, str):
        raise TypeError(_NOT_TEXT)
    return bool(
        asking.named_as_a_key(name)
        or asking.names_a_person(name)
        or taxonomy.named_as_persons_names(name)
        or taxonomy.named_as_an_address_part(name)
        or taxonomy.named_as_a_place(name)
        or taxonomy.named_as_a_coordinate(name)
        or taxonomy.named_as_device_numbers(name)
    )


@dataclasses.dataclass(frozen=True)
class ColumnPlan:
    """How the checks read one column.

    ``kind`` is one of `KINDS`, or empty where the column is to be read
    from its cells. ``age`` marks a column of numbers named as an age;
    ``place`` an identifier column holding a place (C5 reads its first
    three characters); ``not_identifier`` a column the person answered
    is no identifier, which no reader of names or cells makes one;
    ``days`` a date column whose real cells hold no clock (midnight
    read as none): every cell of either table is then read at its
    calendar day, so a clock the twin adds hides no real day (the batch
    4w Codex review, item 5).
    """

    name: str
    kind: str = ""
    age: bool = False
    place: bool = False
    not_identifier: bool = False
    days: bool = False


@dataclasses.dataclass(frozen=True)
class Plan:
    """The checks' reading of a table: one `ColumnPlan` a column, the person column's place (-1 for none), and where the reading came from."""

    columns: "tuple[ColumnPlan, ...]"
    person: int
    source: str


def plan_from_roles(names: "list[str]", roles: "dict[str, str]", person: str = "") -> Plan:
    """A plan from decisions a caller already holds: THE SEAM for a record of the description.

    ``roles`` maps a column's name to one of `ROLES`; a column it does
    not name is read from its cells as `run_checks` reads it.
    ``person`` names the person column, or is empty for a table whose
    rows are its people (no person column is then looked for).
    Guarantees: a fixed function of the three. Raises ValueError, in
    words, for a role that is not one of `ROLES` or a person column the
    names do not hold. No I/O.
    """
    for name in sorted(roles):
        if roles[name] not in ROLES:
            raise ValueError(
                "A role given for a column is not one of: identifier, date, number, label, text, age, place, "
                "not identifier."
            )
    place = -1
    if person:
        for at in range(len(names)):
            if names[at] == person:
                place = at
        if place < 0:
            raise ValueError("The person column named is not a column of the table.")
    columns: "list[ColumnPlan]" = []
    for at in range(len(names)):
        name = names[at]
        role = roles[name] if name in roles else ""
        if at == place:
            role = KIND_IDENTIFIER
        if role == ROLE_AGE:
            columns += [ColumnPlan(name, KIND_NUMBER, age=True)]
        elif role == ROLE_PLACE:
            columns += [ColumnPlan(name, KIND_IDENTIFIER, place=True)]
        elif role == ROLE_NOT_IDENTIFIER:
            columns += [ColumnPlan(name, not_identifier=True)]
        else:
            columns += [ColumnPlan(name, role)]
    return Plan(tuple(columns), place, "given")


@dataclasses.dataclass(frozen=True)
class Check:
    """One check's result: its code, its title, whether it was measured and passed, and its lines (counts and rates only)."""

    code: str
    title: str
    measured: bool
    passed: bool
    lines: "tuple[str, ...]"


@dataclasses.dataclass(frozen=True)
class Outcome:
    """The five checks of one twin against one real table, and what they were measured on."""

    checks: "tuple[Check, ...]"
    real_rows: int
    twin_rows: int
    real_people: int
    twin_people: int
    person_column: str
    kinds: "tuple[str, ...]"
    seed: int

    @property
    def passed(self) -> bool:
        """True when every check passed (a check not measured passes)."""
        return all(check.passed for check in self.checks)


def _kind_of(column: ColumnPlan, cells: "list[str]") -> ColumnPlan:
    """A column's kind, read from its name and its present cells where the plan does not give it.

    In this order: an identifier by its name (unless answered no
    identifier); dates, then numbers, on `READING_SHARE` of the present
    cells read (`KIND_SAMPLE` of them, spread evenly; a column of
    numbers named as an age is an age); labels of at most
    `LABEL_LEVELS_MOST` different values, save an identifier where
    `DETAILS_SHARE` of them hold a person's details (`a_listed_detail`;
    unless answered no identifier); an identifier where
    `DETAILS_SHARE` of the different present cells read hold a person's
    details, or where the different values cover `KEY_LIKE_SHARE` of the
    present cells (both unless answered no identifier); text otherwise.
    """
    name = column.name
    if column.kind:
        return column
    free = not column.not_identifier
    place = taxonomy.named_as_a_place(name)
    if free and named_as_an_identifier(name):
        return dataclasses.replace(column, kind=KIND_IDENTIFIER, place=place)
    present = [cell for cell in cells if not parsing.is_missing_text(cell)]
    if not present:
        return dataclasses.replace(column, kind=KIND_LABEL)
    read = [present[at] for at in _spread_places(len(present), KIND_SAMPLE)]
    dates = 0
    numbers = 0
    for cell in read:
        if read_date(cell) is not None:
            dates += 1
        elif read_number(cell) is not None:
            numbers += 1
    if dates * 1000 >= READING_SHARE * len(read):
        return dataclasses.replace(column, kind=KIND_DATE)
    if numbers * 1000 >= READING_SHARE * len(read):
        age = taxonomy.named_as_an_age(name) and not taxonomy.named_as_a_measurement(name)
        return dataclasses.replace(column, kind=KIND_NUMBER, age=age)
    different: "dict[str, int]" = {}
    for cell in present:
        if cell not in different:
            different[cell] = len(different)
            if len(different) > DETAILS_SAMPLE:
                break
    if len(different) <= LABEL_LEVELS_MOST:
        # ...A SHORT LIST OF PERSONS' DETAILS IS NO LABEL (the batch 4w
        # Codex review, item 3): its different values are read before the
        # list is accepted, and where `DETAILS_SHARE` of them hold a
        # person's details (`a_listed_detail`) the column is an identifier,
        # which C4 reads (unless answered no identifier).
        if free:
            listed = sorted(different)
            details = sum(1 for cell in listed if a_listed_detail(cell))
            if details * 1000 >= DETAILS_SHARE * len(listed):
                return dataclasses.replace(column, kind=KIND_IDENTIFIER, place=place)
        return dataclasses.replace(column, kind=KIND_LABEL)
    if free:
        shown = sorted(different)[:DETAILS_SAMPLE]
        details = sum(1 for cell in shown if a_persons_detail(cell))
        if details * 1000 >= DETAILS_SHARE * len(shown):
            return dataclasses.replace(column, kind=KIND_IDENTIFIER, place=place)
        if len(set(present)) * 1000 >= KEY_LIKE_SHARE * len(present):
            return dataclasses.replace(column, kind=KIND_IDENTIFIER, place=place)
    return dataclasses.replace(column, kind=KIND_TEXT)


def reads_as_an_identifier(name: str, cells: "list[str]") -> bool:
    """Whether C4 reads a column of this name and these cells as an identifier column (`_kind_of`, the one reading).

    Lane IN-4c (plan P4-D514): a long table's key block -- one
    measurement's cells -- is released by its own question's answer only
    where the checks would NOT read it as an identifier column: its name
    names no identifier element, its different values cover less than
    `KEY_LIKE_SHARE` of its present cells, and fewer than `DETAILS_SHARE`
    of them hold a person's details. Guarantees: a fixed function of the
    two. Raises TypeError for a name or a cell that is not text. No I/O.
    """
    if not isinstance(name, str):
        raise TypeError(_NOT_TEXT)
    for cell in cells:
        if not isinstance(cell, str):
            raise TypeError(_NOT_TEXT)
    return _kind_of(ColumnPlan(name), cells).kind == KIND_IDENTIFIER


def _spread_places(count: int, wanted: int) -> "list[int]":
    """Up to `wanted` places spread evenly over `count` (every place when there are fewer)."""
    if count <= wanted:
        return list(range(count))
    return [at * count // wanted for at in range(wanted)]


def _chosen_rows(rows: int, wanted: int, seed: int, salt: int) -> "list[int]":
    """About `wanted` rows chosen by a fixed mix of the seed (every row when there are fewer)."""
    if rows <= wanted:
        return list(range(rows))
    cut = (wanted << 32) // rows
    base = (seed * 0x9E3779B1 + salt) & _MASK
    return [row for row in range(rows) if _mix(base ^ (row << 8)) >> 32 < cut]


@dataclasses.dataclass
class _Cells:
    """One column as a walk read it: each row's digest and value, its normal spellings where asked, and a date column's calendar days and clocked cells."""

    digests: "list[int]"
    values: "list[float | None]"
    spellings: "list[str]"
    numbers: int
    many_decimals: int
    # A date column's: each row's calendar day as a digest (the digest of
    # its day written alone, `_MISSING_DIGEST` for none; empty for any
    # other column), and how many of its cells hold a clock (midnight
    # read as none).
    days: "list[int]"
    clocked: int


def _cell_read(column: ColumnPlan, cell: str) -> "tuple[int, float | None, str, int, int]":
    """One cell's digest in its normal spelling, its value (a number, or a date in seconds), its normal spelling, its decimals (a date's: 1 where it holds a clock) and a date's calendar day as a digest."""
    if parsing.is_missing_text(cell):
        return _MISSING_DIGEST, None, _MISSING, 0, _MISSING_DIGEST
    if column.kind == KIND_NUMBER:
        number = read_number(cell)
        if number is not None:
            return _digest("n" + number.spelling), number.value, number.spelling, number.decimals, _MISSING_DIGEST
    elif column.kind == KIND_DATE:
        date = read_date(cell)
        if date is not None:
            # ...the day written alone, its first ten characters
            # (`read_date`'s spelling opens with it): a column read at its
            # calendar day (``days``) reads every cell so.
            day = date.spelling[:10]
            day_digest = _digest("d" + day)
            if column.days or date.second < 0:
                return day_digest, float(date.day * _SECONDS_A_DAY), day, 0, day_digest
            seconds = float(date.day * _SECONDS_A_DAY + date.second)
            return _digest("d" + date.spelling), seconds, date.spelling, 1, day_digest
    elif column.kind == KIND_IDENTIFIER:
        key = parsing.merged_key(cell)
        return _digest("k" + key), None, key, 0, _MISSING_DIGEST
    folded = parsing.folded(cell)
    return _digest("t" + folded), None, folded, 0, _MISSING_DIGEST


def _read_cells(column: ColumnPlan, cells: "list[str]", keep_spellings: bool) -> _Cells:
    """Every cell of a column read once, a memo for repeated cells: digests, values and, where asked, normal spellings; a date column's calendar days and clocked cells too."""
    memo: "dict[str, tuple[int, float | None, str, int, int]]" = {}
    digests: "list[int]" = []
    values: "list[float | None]" = []
    spellings: "list[str]" = []
    days: "list[int]" = []
    numbers = 0
    many = 0
    clocked = 0
    for cell in cells:
        if cell in memo:
            found = memo[cell]
        else:
            found = _cell_read(column, cell)
            if len(memo) < _MEMO_MOST:
                memo[cell] = found
        digests += [found[0]]
        values += [found[1]]
        if keep_spellings:
            spellings += [found[2]]
        if column.kind == KIND_NUMBER and found[1] is not None:
            numbers += 1
            if found[3] > CHANCE_DECIMALS:
                many += 1
        if column.kind == KIND_DATE:
            days += [found[4]]
            clocked += found[3]
    return _Cells(digests, values, spellings, numbers, many, days, clocked)


def _standard_units(values: "list[float | None]") -> "tuple[int, float, float]":
    """The present values' mean and spread (sample standard deviation; 1 where it is 0), each in units of 2 ** exponent, with that exponent, by `math.fsum`.

    SCALED MOMENTS (the batch 4w Codex review, item 17): every value is
    first divided by the power of two at or above the largest size
    present (`math.frexp`, `math.ldexp`), so the sum, the mean and the
    squared deviations stay within 2 and 4 times the count: repeated
    finite `1e308` values no longer overflow the sum, and values about
    plus or minus `1e200` no longer overflow the squares into an
    infinite spread that put every value on one code. A division by a
    power of two is exact, so on every column that did not overflow the
    codes are the ones the unscaled moments gave. A column whose spread
    is 0, or of one value, has a spread of 1 in its own units, as
    before (2 ** -exponent in the scale's).
    """
    present = [value for value in values if value is not None]
    if not present:
        return 0, 0.0, 1.0
    largest = max(abs(value) for value in present)
    exponent = math.frexp(largest)[1] if largest > 0.0 else 0
    scaled = [math.ldexp(value, -exponent) for value in present]
    mean = math.fsum(scaled) / len(scaled)
    unit = math.ldexp(1.0, -exponent) if exponent > -_SCALED_MOST else math.ldexp(1.0, _SCALED_MOST)
    if len(scaled) < 2:
        return exponent, mean, unit
    squares = math.fsum((value - mean) * (value - mean) for value in scaled)
    spread = math.sqrt(squares / (len(scaled) - 1))
    return exponent, mean, spread if spread > 0.0 else unit


def _encoded(value: "float | None", units: "tuple[int, float, float]") -> int:
    """C2's code of one value: its standard units (`_standard_units`, read in the column's scale) times `_SCALE` around `_MIDDLE`, held to 0 and `_TOP`; `_NO_VALUE` for none.

    A value more than 2 ** `_SCALED_MOST` times the column's scale, or
    whose standard units overflow, is off the scale altogether: 0 or
    `_TOP` by its sign, never an overflow.
    """
    if value is None:
        return _NO_VALUE
    exponent, mean, spread = units
    if value != 0.0 and math.frexp(value)[1] - exponent > _SCALED_MOST:
        return _TOP if value > 0.0 else 0
    standard = (math.ldexp(value, -exponent) - mean) / spread * _SCALE
    if not math.isfinite(standard):
        return _TOP if standard > 0.0 else 0
    code = round(standard) + _MIDDLE
    return min(max(code, 0), _TOP)


def _fold_in(running: "list[int]", column: "list[int]") -> "list[int]":
    """Each row's running digest with one more column's digest folded in."""
    return [hash((before, digest)) for before, digest in zip(running, column)]


def _present_flags(flags: bytearray, digests: "list[int]") -> bytearray:
    """The flags with every row whose digest is a present value's set."""
    return bytearray(1 if flag or digest != _MISSING_DIGEST else 0 for flag, digest in zip(flags, digests))


@dataclasses.dataclass
class _Tally:
    """Counts a rate rule reads: the twin's matches against each half, and each half's against the other."""

    twin_in_first: int = 0
    twin_in_second: int = 0
    twin_in_both: int = 0
    twin_total: int = 0
    first_in_second: int = 0
    first_total: int = 0
    second_in_first: int = 0
    second_total: int = 0
    # How much wider the fresh halves' matches spread than independent
    # rows would, measured over the real table's people (`_design_effect`).
    design: float = 1.0


def _design_effect(matched: "dict[int, int]", rows: "dict[int, int]") -> float:
    """How much wider a share spreads over people than over independent rows: 1 at the least.

    ``matched`` and ``rows`` count, a person at a time, the fresh rows
    that matched and the fresh rows read. A person's rows are alike (one
    age, one ward, one level of a reading), so they match together, and
    a share's spread read as if every row were drawn alone is too
    narrow. The spread over people (the variance of a ratio of sums over
    clusters) over the spread over rows is the design effect; a rate's
    allowance is widened by it. Read on the real table's fresh halves
    alone, so a twin's own matches never widen its allowance.
    """
    total = 0
    hits = 0
    for unit in rows:
        total += rows[unit]
        hits += matched[unit] if unit in matched else 0
    if total == 0 or hits == 0 or hits == total:
        return 1.0
    share = hits / total
    spread = math.fsum(
        ((matched[unit] if unit in matched else 0) - share * rows[unit])
        * ((matched[unit] if unit in matched else 0) - share * rows[unit])
        for unit in rows
    )
    return max(1.0, spread / (share * (1.0 - share) * total))


def _count_in(counts: "dict[int, int]", unit: int, step: int) -> None:
    """Add a step to a person's count."""
    counts[unit] = counts[unit] + step if unit in counts else step


@dataclasses.dataclass
class _Side:
    """What one table's walk gathers, a list a row: digests for C1, C3 and C5, flags of present readings and dates, the person; and C2's encoded columns."""

    rows: int
    row_digest: "list[int]"
    reading_digest: "list[int]"
    reading_present: bytearray
    date_digest: "list[int]"
    date_present: bytearray
    combination: "list[int]"
    combined: int
    unit: "list[int]"
    held: bytearray
    numbers: "list[tuple[bytes, bytes]]"
    labels: "list[bytes]"


def _new_side(rows: int) -> _Side:
    """An empty walk of a table of `rows` rows: every row its own person until a person column numbers them."""
    return _Side(
        rows,
        [0] * rows,
        [0] * rows,
        bytearray(rows),
        [0] * rows,
        bytearray(rows),
        [0] * rows,
        0,
        list(range(rows)),
        bytearray(rows),
        [],
        [],
    )


@dataclasses.dataclass
class _Real:
    """What the real table's walk keeps for the twin's: the plan read, the halves, and the sets each check looks up."""

    plan: Plan
    halves: bytearray
    people: int
    columns_units: "dict[int, tuple[int, float, float]]"
    label_codes: "dict[int, dict[int, int]]"
    identifier_sets: "dict[int, set[int]]"
    detail_sets: "dict[int, set[int]]"
    date_rare: "dict[int, tuple[set[int], set[int]]]"
    date_fresh: "dict[int, _Tally]"
    chance_free: bool
    # A text column's identifier elements of its cells holding a
    # person's details, as digests (`elements`, held).
    element_sets: "dict[int, set[int]]"


@dataclasses.dataclass
class _Twin:
    """C4's counts and C2's chosen rows, gathered on the twin's walk."""

    people: int
    identifiers: "list[tuple[str, int]]"
    details: "list[tuple[str, int]]"
    ages: "list[tuple[str, int]]"
    dates: "list[tuple[str, _Tally]]"
    numbers: "list[list[int]]"
    labels: "list[list[int]]"
    # Each text column's twin cells holding an element a real cell
    # holding a person's details holds (`elements`).
    elements: "list[tuple[str, int]]"


def _number_people(side: _Side, cells: "list[str]") -> int:
    """Number each row's person in the order the table first holds them (keys read by `parsing.merged_key`); return how many."""
    codes: "dict[str, int]" = {}
    units: "list[int]" = []
    for cell in cells:
        key = _MISSING if parsing.is_missing_text(cell) else parsing.merged_key(cell)
        if key not in codes:
            codes[key] = len(codes)
        units += [codes[key]]
    side.unit = units
    return len(codes)


def _person_place(table: reading.Table, person: str, plan: "Plan | None") -> int:
    """The person column's place: the plan's; the one named; else the first column named as a key or a person whose keys repeat; -1 for none."""
    names = table.column_names
    if plan is not None:
        return plan.person
    if person:
        for at in range(len(names)):
            if names[at] == person:
                return at
        raise errors.ProfileError(
            "The person column named with --person is not a column of the real table. Give its name as the "
            "header row writes it."
        )
    for at in range(len(names)):
        name = names[at]
        if not (asking.named_as_a_key(name) or asking.names_a_person(name)):
            continue
        cells = reading.column_values(table, at)
        keys = [parsing.merged_key(cell) for cell in cells if not parsing.is_missing_text(cell)]
        if keys and len(set(keys)) < len(keys):
            return at
    return -1


def _rare_in_halves(cells: _Cells, units: "list[int]", halves: bytearray) -> "tuple[set[int], set[int]]":
    """The values each half holds for 1 to `RARE_HOLDERS_MOST` people (a person counted once a value)."""
    held: "list[set[tuple[int, int]]]" = [set(), set()]
    for row in range(len(cells.digests)):
        digest = cells.digests[row]
        if digest != _MISSING_DIGEST:
            held[halves[row]] |= {(units[row], digest)}
    rare: "list[set[int]]" = []
    for half in (0, 1):
        holders: "dict[int, int]" = {}
        for pair in held[half]:
            holders[pair[1]] = holders[pair[1]] + 1 if pair[1] in holders else 1
        rare += [set(digest for digest in holders if holders[digest] <= RARE_HOLDERS_MOST)]
    return rare[0], rare[1]


def _fresh_dates(
    cells: _Cells, units: "list[int]", halves: bytearray, rare: "tuple[set[int], set[int]]"
) -> _Tally:
    """Each half's present cells holding a value rare in the other half, each half's present cells, and the design effect over people.

    A cell meets a rare value by its own spelling or by its calendar day
    (`_Cells.days`): a clocked cell on a day that 1 to 10 people's cells
    written as the day alone hold meets that day (the batch 4w Codex
    review, item 5), as the twin's cells are read (`_walk_twin`).
    """
    tally = _Tally()
    matched: "dict[int, int]" = {}
    read: "dict[int, int]" = {}
    for row in range(len(cells.digests)):
        digest = cells.digests[row]
        if digest == _MISSING_DIGEST:
            continue
        other = rare[1 - halves[row]]
        hit = digest in other or cells.days[row] in other
        if halves[row] == 0:
            tally.first_total += 1
            tally.first_in_second += 1 if hit else 0
        else:
            tally.second_total += 1
            tally.second_in_first += 1 if hit else 0
        _count_in(read, units[row], 1)
        _count_in(matched, units[row], 1 if hit else 0)
    tally.design = _design_effect(matched, read)
    return tally


def _details_held(cells: "list[str]", read: _Cells) -> "set[int]":
    """The digests of the different text cells that hold a person's details."""
    seen: "set[int]" = set()
    held: "set[int]" = set()
    for row in range(len(cells)):
        digest = read.digests[row]
        if digest == _MISSING_DIGEST or digest in seen:
            continue
        seen |= {digest}
        if a_persons_detail(cells[row]):
            held |= {digest}
    return held


def _element_digests(cell: str, held: bool, memo: "dict[str, frozenset[int]]") -> "frozenset[int]":
    """A cell's identifier elements (`elements`) as digests, a memo for repeated cells."""
    if cell in memo:
        return memo[cell]
    found = frozenset(_digest("e" + element) for element in elements(cell, held))
    if len(memo) < _MEMO_MOST:
        memo[cell] = found
    return found


def _held_elements(cells: "list[str]", read: _Cells, details: "set[int]") -> "set[int]":
    """The identifier elements (`elements`, held) of a text column's real cells that hold a person's details (`_details_held`), as digests."""
    found: "set[int]" = set()
    memo: "dict[str, frozenset[int]]" = {}
    for row in range(len(cells)):
        if read.digests[row] in details:
            found |= _element_digests(cells[row], True, memo)
    return found


def _cells_meeting(cells: "list[str]", read: _Cells, held: "set[int]") -> int:
    """A text column's twin cells any of whose elements (`elements`, looked up) is one of ``held``; 0 without reading a cell where none is held."""
    if not held:
        return 0
    memo: "dict[str, frozenset[int]]" = {}
    met = 0
    for row in range(len(cells)):
        if read.digests[row] == _MISSING_DIGEST:
            continue
        if any(element in held for element in _element_digests(cells[row], False, memo)):
            met += 1
    return met


def _label_codes(digests: "list[int]") -> "dict[int, int]":
    """A label column's code for each different present digest, in the order the column first holds them."""
    codes: "dict[int, int]" = {}
    for digest in digests:
        if digest != _MISSING_DIGEST and digest not in codes:
            codes[digest] = min(len(codes), _UNSEEN_LABEL)
    return codes


def _label_code(codes: "dict[int, int]", digest: int) -> int:
    if digest == _MISSING_DIGEST:
        return _NO_LABEL
    return codes[digest] if digest in codes else _UNSEEN_LABEL


def _whole_years(value: float) -> int:
    """The whole number at or below a value: an age's whole years."""
    whole = int(value)
    return whole - 1 if whole > value else whole


def _combination_part(column: ColumnPlan, read: _Cells) -> "list[int] | None":
    """C5's part of a column: a label or a column of numbers of few levels as written, an age's whole year, a place's first three characters; None for no part."""
    if column.kind == KIND_LABEL:
        return read.digests
    if column.kind == KIND_NUMBER and column.age:
        return [_MISSING_DIGEST if value is None else _digest(f"a{_whole_years(value)}") for value in read.values]
    if column.kind == KIND_NUMBER and len(set(read.digests)) <= LABEL_LEVELS_MOST + 1:
        return read.digests
    if column.kind == KIND_IDENTIFIER and column.place:
        return [
            _MISSING_DIGEST if spelling == _MISSING else _digest("p" + spelling[:3])
            for spelling in read.spellings
        ]
    return None


def _take_common(side: _Side, column: ColumnPlan, read: _Cells) -> None:
    """The digests every walk folds in: the row's (C1, every column but the identifiers, which C4 reads), the readings' and the dates' (C3), the combination's (C5)."""
    if column.kind != KIND_IDENTIFIER:
        side.row_digest = _fold_in(side.row_digest, read.digests)
    side.held = _present_flags(side.held, read.digests)
    if column.kind == KIND_NUMBER:
        side.reading_digest = _fold_in(side.reading_digest, read.digests)
        side.reading_present = _present_flags(side.reading_present, read.digests)
    if column.kind == KIND_DATE:
        side.date_digest = _fold_in(side.date_digest, read.digests)
        side.date_present = _present_flags(side.date_present, read.digests)
    part = _combination_part(column, read)
    if part is not None:
        side.combination = _fold_in(side.combination, part)
        side.combined += 1


def _walk_real(table: reading.Table, plan: "Plan | None", person: str, seed: int) -> "tuple[_Side, _Real]":
    """The real table's walk, group by group: its plan (given or read), its halves and every set the checks look up."""
    names = table.column_names
    side = _new_side(table.n_rows)
    person_at = _person_place(table, person, plan)
    people = table.n_rows
    if person_at >= 0:
        people = _number_people(side, reading.column_values(table, person_at))
    halves = bytearray(_half_of(seed, unit) for unit in side.unit)
    real = _Real(
        Plan((), person_at, plan.source if plan is not None else "read"), halves, people, {}, {}, {}, {}, {}, {}, False,
        {},
    )
    columns: "list[ColumnPlan]" = []
    for start, end in reading.column_groups(table):
        for at in range(start, end):
            cells = reading.column_values(table, at)
            given = plan.columns[at] if plan is not None else ColumnPlan(names[at])
            if at == person_at:
                given = dataclasses.replace(given, kind=KIND_IDENTIFIER)
            column = _kind_of(given, cells)
            read = _read_cells(column, cells, column.kind == KIND_IDENTIFIER and column.place)
            if column.kind == KIND_DATE and read.clocked == 0:
                # ...a date column whose real cells hold no clock is read
                # at its calendar day in the twin too (`ColumnPlan.days`);
                # its real cells already are.
                column = dataclasses.replace(column, days=True)
            _take_common(side, column, read)
            if column.kind == KIND_NUMBER and read.numbers and read.many_decimals * 2 >= read.numbers:
                real.chance_free = True
            if column.kind in (KIND_NUMBER, KIND_DATE):
                units = _standard_units(read.values)
                real.columns_units[at] = units
                codes = [_encoded(value, units) for value in read.values]
                side.numbers += [(bytes(code & 255 for code in codes), bytes(code >> 8 for code in codes))]
            if column.kind == KIND_LABEL:
                label_codes = _label_codes(read.digests)
                real.label_codes[at] = label_codes
                side.labels += [bytes(_label_code(label_codes, digest) for digest in read.digests)]
            if column.kind == KIND_DATE:
                rare = _rare_in_halves(read, side.unit, halves)
                real.date_rare[at] = rare
                real.date_fresh[at] = _fresh_dates(read, side.unit, halves, rare)
            if column.kind == KIND_IDENTIFIER:
                real.identifier_sets[at] = set(digest for digest in read.digests if digest != _MISSING_DIGEST)
            if column.kind == KIND_TEXT:
                details = _details_held(cells, read)
                real.detail_sets[at] = details
                real.element_sets[at] = _held_elements(cells, read, details)
            columns += [column]
    real.plan = Plan(tuple(columns), person_at, real.plan.source)
    return side, real


def _walk_twin(table: reading.Table, real: _Real, chosen: "list[int]") -> "tuple[_Side, _Twin]":
    """The twin's walk, read by the real table's plan: its digests, C4's counts, and C2's codes of the chosen rows."""
    plan = real.plan
    side = _new_side(table.n_rows)
    people = table.n_rows
    if plan.person >= 0:
        people = _number_people(side, reading.column_values(table, plan.person))
    found = _Twin(people, [], [], [], [], [], [], [])
    for start, end in reading.column_groups(table):
        for at in range(start, end):
            column = plan.columns[at]
            cells = reading.column_values(table, at)
            read = _read_cells(column, cells, column.kind == KIND_IDENTIFIER and column.place)
            _take_common(side, column, read)
            if column.kind == KIND_NUMBER and column.age:
                over = sum(1 for value in read.values if value is not None and value > AGE_TOP)
                found.ages += [(column.name, over)]
            if column.kind == KIND_DATE:
                rare = real.date_rare[at]
                tally = dataclasses.replace(real.date_fresh[at])
                for row in range(len(read.digests)):
                    digest = read.digests[row]
                    if digest != _MISSING_DIGEST:
                        # ...its spelling or its calendar day (`_fresh_dates`).
                        day = read.days[row]
                        first = digest in rare[0] or day in rare[0]
                        second = digest in rare[1] or day in rare[1]
                        tally.twin_total += 1
                        tally.twin_in_first += 1 if first else 0
                        tally.twin_in_second += 1 if second else 0
                        tally.twin_in_both += 1 if first and second else 0
                found.dates += [(column.name, tally)]
            if column.kind == KIND_IDENTIFIER:
                held = real.identifier_sets[at]
                equal = sum(1 for digest in read.digests if digest != _MISSING_DIGEST and digest in held)
                found.identifiers += [(column.name, equal)]
            if column.kind == KIND_TEXT:
                held = real.detail_sets[at]
                equal = sum(1 for digest in read.digests if digest != _MISSING_DIGEST and digest in held)
                found.details += [(column.name, equal)]
                found.elements += [(column.name, _cells_meeting(cells, read, real.element_sets[at]))]
            if column.kind in (KIND_NUMBER, KIND_DATE):
                units = real.columns_units[at]
                found.numbers += [[_encoded(read.values[row], units) for row in chosen]]
            if column.kind == KIND_LABEL:
                label_codes = real.label_codes[at]
                found.labels += [[_label_code(label_codes, read.digests[row]) for row in chosen]]
    return side, found


def _allowed_rate(tally: _Tally, strict: bool) -> "tuple[float, float, float]":
    """The twin's rate, the fresh halves' rate and the rate allowed, each a quotient of the tally's counts.

    Each half against the other is a fresh draw against a reference of
    half the real table, and so is the twin against each half: the
    twin's rate is (its matches in the first half + its matches in the
    second) over its count, and the fresh rate the sum of the two
    halves' rates.

    A twin row is read against both halves, and a common value is
    likely in both, so the twin's two matches of a row move together:
    their covariance, read on the twin's rows matched in both halves, is
    added to the twin's spread (it is no copy: a copied row lies in one
    half). Every spread is widened by the fresh halves' design effect
    over the real table's people (`_design_effect`).

    STRICT (C1 where a column of numbers is written with more than two
    decimals, and C3): the allowance is the fresh rate and
    `NOISE_ERRORS` standard errors of the fresh halves' own rates, and
    nothing for the twin's: where no fresh half matches the other, no
    twin match is allowed. OTHERWISE (C1 of other tables, the dates of
    C4, C5): the fresh rate, one in `MARGIN_ROWS`, and `NOISE_ERRORS`
    standard errors of the difference as chance alone would spread it:
    the twin's rate and each half's read at the fresh halves' rates,
    each with half a match added (so a half that matched nothing by
    chance at a small size still carries a spread), as binomial shares.
    The twin's own matches never widen its allowance.
    """
    if tally.twin_total == 0 or tally.first_total == 0 or tally.second_total == 0:
        return 0.0, 0.0, 0.0
    first = tally.first_in_second / tally.first_total
    second = tally.second_in_first / tally.second_total
    fresh = first + second
    twin = (tally.twin_in_first + tally.twin_in_second) / tally.twin_total
    if strict:
        variance = first * (1.0 - first) / tally.first_total + second * (1.0 - second) / tally.second_total
        return twin, fresh, fresh + NOISE_ERRORS * math.sqrt(variance * tally.design)
    smooth_first = (tally.first_in_second + 0.5) / (tally.first_total + 1)
    smooth_second = (tally.second_in_first + 0.5) / (tally.second_total + 1)
    shares = smooth_first * (1.0 - smooth_first) + smooth_second * (1.0 - smooth_second)
    both = tally.twin_in_both / tally.twin_total
    together = both - (tally.twin_in_first / tally.twin_total) * (tally.twin_in_second / tally.twin_total)
    variance = (shares + 2.0 * max(together, 0.0)) / tally.twin_total
    variance = variance + smooth_first * (1.0 - smooth_first) / tally.first_total
    variance = variance + smooth_second * (1.0 - smooth_second) / tally.second_total
    return twin, fresh, fresh + 1.0 / MARGIN_ROWS + NOISE_ERRORS * math.sqrt(variance * tally.design)


def _ten_thousandths(rate: float) -> str:
    return f"{rate * MARGIN_ROWS:.2f}"


def _rate_check(what: str, tally: _Tally, strict: bool) -> "tuple[bool, tuple[str, ...]]":
    """Whether a tally passes its rate rule, and its two lines: the twin's count and rate, and the fresh rate beside the allowance."""
    twin, fresh, allowed = _allowed_rate(tally, strict)
    found = tally.twin_in_first + tally.twin_in_second
    lines = (
        f"{found} of {tally.twin_total} twin {what} match ({_ten_thousandths(twin)} per 10,000).",
        f"A fresh half of the real table against the other: {_ten_thousandths(fresh)} per 10,000; "
        f"allowed up to {_ten_thousandths(allowed)} per 10,000.",
    )
    return twin <= allowed, lines


def _halves_sets(digests: "list[int]", halves: bytearray, rows: "list[int]") -> "tuple[set[int], set[int]]":
    """The digests of the given rows of each half."""
    first: "set[int]" = set()
    second: "set[int]" = set()
    for row in rows:
        if halves[row] == 0:
            first |= {digests[row]}
        else:
            second |= {digests[row]}
    return first, second


def _check_rows(real_side: _Side, real: _Real, twin_side: _Side) -> Check:
    """C1: twin rows equal to a real row, against each half's rows equal to the other's."""
    if all(column.kind == KIND_IDENTIFIER for column in real.plan.columns):
        return Check("C1", "exact row copy", False, True, ("Every column is an identifier, which C4 reads.",))
    every = list(range(real_side.rows))
    first, second = _halves_sets(real_side.row_digest, real.halves, every)
    tally = _Tally()
    matched: "dict[int, int]" = {}
    read: "dict[int, int]" = {}
    for row in every:
        digest = real_side.row_digest[row]
        hit = digest in (second if real.halves[row] == 0 else first)
        if real.halves[row] == 0:
            tally.first_total += 1
            tally.first_in_second += 1 if hit else 0
        else:
            tally.second_total += 1
            tally.second_in_first += 1 if hit else 0
        _count_in(read, real_side.unit[row], 1)
        _count_in(matched, real_side.unit[row], 1 if hit else 0)
    tally.design = _design_effect(matched, read)
    either = 0
    for digest in twin_side.row_digest:
        tally.twin_total += 1
        inside_first = digest in first
        inside_second = digest in second
        tally.twin_in_first += 1 if inside_first else 0
        tally.twin_in_second += 1 if inside_second else 0
        tally.twin_in_both += 1 if inside_first and inside_second else 0
        either += 1 if inside_first or inside_second else 0
    passed, lines = _rate_check("rows' matches against each half", tally, real.chance_free)
    head = f"{either} of {twin_side.rows} twin rows equal a real row on every column but the identifiers."
    rule = (
        "A column of numbers is written with more than two decimals: no allowance beyond chance."
        if real.chance_free
        else "Allowance: 1 row in 10,000 and three standard errors over chance."
    )
    return Check("C1", "exact row copy", True, passed, tuple([head] + list(lines) + [rule]))


def _patients(side: _Side, digests: "list[int]", present: bytearray) -> "dict[int, int]":
    """Each person of at least `PATIENT_ROWS_LEAST` rows with a present value: the digest of their rows' digests taken as a set.

    A SET, its repeats read once (the batch 4w Codex review, item 6): a
    twin person holding a real person's whole history twice, or with
    some visits repeated, holds the same set as the real person; the
    sorted list read before kept the repeats, and C3 counted no copy.
    """
    rows_of: "dict[int, list[int]]" = {}
    shown: "set[int]" = set()
    for row in range(side.rows):
        unit = side.unit[row]
        if unit in rows_of:
            rows_of[unit] += [digests[row]]
        else:
            rows_of[unit] = [digests[row]]
        if present[row]:
            shown |= {unit}
    return {
        unit: hash(tuple(sorted(set(rows_of[unit]))))
        for unit in rows_of
        if len(rows_of[unit]) >= PATIENT_ROWS_LEAST and unit in shown
    }


def _patient_tally(real_side: _Side, real: _Real, twin_side: _Side, readings: bool) -> _Tally:
    """C3's counts on readings or on dates: twin patients equal to a patient of each half, and each half's against the other."""
    real_digests = real_side.reading_digest if readings else real_side.date_digest
    real_present = real_side.reading_present if readings else real_side.date_present
    twin_digests = twin_side.reading_digest if readings else twin_side.date_digest
    twin_present = twin_side.reading_present if readings else twin_side.date_present
    real_patients = _patients(real_side, real_digests, real_present)
    half_of_unit: "dict[int, int]" = {}
    for row in range(real_side.rows):
        half_of_unit[real_side.unit[row]] = real.halves[row]
    sets: "list[set[int]]" = [set(), set()]
    for unit in real_patients:
        sets[half_of_unit[unit]] |= {real_patients[unit]}
    tally = _Tally()
    for unit in real_patients:
        signature = real_patients[unit]
        if half_of_unit[unit] == 0:
            tally.first_total += 1
            tally.first_in_second += 1 if signature in sets[1] else 0
        else:
            tally.second_total += 1
            tally.second_in_first += 1 if signature in sets[0] else 0
    twin_patients = _patients(twin_side, twin_digests, twin_present)
    for unit in twin_patients:
        signature = twin_patients[unit]
        tally.twin_total += 1
        tally.twin_in_first += 1 if signature in sets[0] else 0
        tally.twin_in_second += 1 if signature in sets[1] else 0
    return tally


def _check_patients(real_side: _Side, real: _Real, twin_side: _Side) -> Check:
    """C3: twin patients holding a real patient's readings, or dates, against each half's patients against the other's."""
    if real.plan.person < 0:
        return Check("C3", "patient copy", False, True, ("No person column: the rows are the people, and C1 and C2 read them.",))
    lines: "list[str]" = []
    passed = True
    measured = False
    for readings, what in ((True, "readings"), (False, "dates")):
        tally = _patient_tally(real_side, real, twin_side, readings)
        if tally.first_total == 0 or tally.second_total == 0 or tally.twin_total == 0:
            lines += [f"On {what}: no patient of {PATIENT_ROWS_LEAST} rows or more holds any; not measured."]
            continue
        measured = True
        one, said = _rate_check(f"patients' {what} matches against each half", tally, True)
        passed = passed and one
        lines += [f"On {what}: {line}" for line in said]
    return Check("C3", "patient copy", measured, passed, tuple(lines))


def _check_identifiers(real: _Real, twin: _Twin) -> Check:
    """C4: identifier cells, text cells holding a person's details and ages past the top code (none allowed), and rare real dates (a rate rule each)."""
    lines: "list[str]" = []
    passed = True
    measured = False
    for name, equal in twin.identifiers:
        measured = True
        passed = passed and equal == 0
        lines += [f"Identifier column {name}: {equal} twin cells equal a real one."]
    for name, equal in twin.details:
        measured = True
        passed = passed and equal == 0
        lines += [f"Text column {name}: {equal} twin cells equal a real cell holding a person's details."]
    for name, met in twin.elements:
        # ...and the names and numbers of those real cells, in whatever
        # words the twin's cells put them (`elements`; none allowed).
        passed = passed and met == 0
        lines += [
            f"Text column {name}: {met} twin cells hold a name or a number of a real cell holding a person's details."
        ]
    for name, over in twin.ages:
        measured = True
        passed = passed and over == 0
        lines += [f"Age column {name}: {over} twin cells past {AGE_TOP}."]
    for name, tally in twin.dates:
        if tally.first_total == 0 or tally.second_total == 0 or tally.twin_total == 0:
            lines += [f"Date column {name}: no present date on one side; not measured."]
            continue
        measured = True
        one, said = _rate_check("cells' matches with a date 1 to 10 people hold", tally, False)
        passed = passed and one
        lines += [f"Date column {name}: {line}" for line in said]
    if not measured:
        lines += ["No identifier, age, text or date column was read."]
    return Check("C4", "identifiers and dates", measured, passed, tuple(lines))


def _check_combinations(real_side: _Side, real: _Real, twin_side: _Side) -> Check:
    """C5: twin rows holding a combination one real row holds, against each half's rows holding one the other half holds once."""
    if real_side.combined == 0:
        return Check("C5", "rare combination", False, True, ("No label, age, place or few-valued number column was read.",))
    counts: "list[dict[int, int]]" = [{}, {}]
    whole: "dict[int, int]" = {}
    for row in range(real_side.rows):
        digest = real_side.combination[row]
        held = counts[real.halves[row]]
        held[digest] = 2 if digest in held else 1
        whole[digest] = 2 if digest in whole else 1
    tally = _Tally()
    matched: "dict[int, int]" = {}
    read: "dict[int, int]" = {}
    for row in range(real_side.rows):
        digest = real_side.combination[row]
        other = counts[1 - real.halves[row]]
        hit = digest in other and other[digest] == 1
        if real.halves[row] == 0:
            tally.first_total += 1
            tally.first_in_second += 1 if hit else 0
        else:
            tally.second_total += 1
            tally.second_in_first += 1 if hit else 0
        _count_in(read, real_side.unit[row], 1)
        _count_in(matched, real_side.unit[row], 1 if hit else 0)
    tally.design = _design_effect(matched, read)
    unique = sum(1 for digest in whole if whole[digest] == 1)
    holding = 0
    for digest in twin_side.combination:
        tally.twin_total += 1
        unique_first = digest in counts[0] and counts[0][digest] == 1
        unique_second = digest in counts[1] and counts[1][digest] == 1
        tally.twin_in_first += 1 if unique_first else 0
        tally.twin_in_second += 1 if unique_second else 0
        tally.twin_in_both += 1 if unique_first and unique_second else 0
        holding += 1 if digest in whole and whole[digest] == 1 else 0
    passed, lines = _rate_check("rows' matches with a combination one row of a half holds", tally, False)
    head = (
        f"{unique} combinations of {real_side.combined} columns are held by one real row; "
        f"{holding} twin rows hold one of them."
    )
    return Check("C5", "rare combination", True, passed, tuple([head] + list(lines)))


def _row_codes(side: _Side, row: int) -> "tuple[list[int], list[int]]":
    """One real row's C2 codes: its numbers' and its labels'."""
    numbers = [low[row] | (high[row] << 8) for low, high in side.numbers]
    labels = [codes[row] for codes in side.labels]
    return numbers, labels


def _distance(numbers: "list[int]", labels: "list[int]", side: _Side, row: int) -> float:
    """The squared distance of a row's codes to a real row: standard units squared, one a mismatch."""
    total = 0
    mismatches = 0
    for at in range(len(numbers)):
        pair = side.numbers[at]
        value = pair[0][row] | (pair[1][row] << 8)
        mine = numbers[at]
        if value == _NO_VALUE or mine == _NO_VALUE:
            mismatches += 0 if value == mine else 1
        else:
            gap = value - mine
            total += gap * gap
    for at in range(len(labels)):
        mismatches += 0 if side.labels[at][row] == labels[at] else 1
    return total / (_SCALE * _SCALE) + mismatches


@dataclasses.dataclass(frozen=True)
class _Probe:
    """One probe: the label columns its block reads, and a weight a column of numbers (0 for one it does not read)."""

    labels: "tuple[int, ...]"
    weights: "tuple[int, ...]"


def _probes(seed: int, numbers: int, labels: int) -> "list[_Probe]":
    """`PROBES` probes: two read every label, one none, two half each; each reads about half the columns of numbers, by a fixed mix of the seed."""
    every = tuple(range(labels))
    readings = (every, every, (), every[0::2], every[1::2])
    made: "list[_Probe]" = []
    for probe in range(PROBES):
        weights: "list[int]" = []
        for at in range(numbers):
            mixed = _mix((seed << 20) ^ (probe << 12) ^ at)
            read = (mixed >> 63) == 1 or numbers <= 2
            weight = int((mixed >> 20) % (2 * _WEIGHT_TOP + 1)) - _WEIGHT_TOP
            weights += [weight if read and weight else (1 if read else 0)]
        made += [_Probe(readings[probe % len(readings)], tuple(weights))]
    return made


def _key(probe: _Probe, numbers: "list[int]", labels: "list[int]") -> int:
    """A row's place in a probe: its labels' block above its projection on the probe's weights."""
    block = hash(tuple(labels[at] for at in probe.labels)) & _BLOCK_MASK if probe.labels else 0
    total = 0
    for at in range(len(numbers)):
        weight = probe.weights[at]
        if weight and numbers[at] != _NO_VALUE:
            total += weight * (numbers[at] - _MIDDLE)
    place = min(max((total >> _PLACE_SHIFT) + _PLACE_MIDDLE, 0), _PLACE_TOP)
    return (block << _PLACE_BITS) + place


def _all_keys(probe: _Probe, side: _Side) -> "list[int]":
    """Every real row's key in a probe, a column at a time."""
    if probe.labels:
        columns = [side.labels[at] for at in probe.labels]
        blocks = [hash(codes) & _BLOCK_MASK for codes in zip(*columns)]
    else:
        blocks = [0] * side.rows
    totals = [0] * side.rows
    for at in range(len(side.numbers)):
        weight = probe.weights[at]
        if not weight:
            continue
        low, high = side.numbers[at]
        totals = [
            total if (lo | (hi << 8)) == _NO_VALUE else total + weight * ((lo | (hi << 8)) - _MIDDLE)
            for total, lo, hi in zip(totals, low, high)
        ]
    return [
        (block << _PLACE_BITS) + min(max((total >> _PLACE_SHIFT) + _PLACE_MIDDLE, 0), _PLACE_TOP)
        for block, total in zip(blocks, totals)
    ]


def _first_at_least(ordered: "list[int]", key: int) -> int:
    """The first place in an ascending list holding `key` or more (its length when none does)."""
    low = 0
    high = len(ordered)
    while low < high:
        middle = (low + high) // 2
        if ordered[middle] < key:
            low = middle + 1
        else:
            high = middle
    return low


@dataclasses.dataclass(frozen=True)
class _Query:
    """A row whose nearest record is sought: its codes, its own key place among the real rows (-1 for a twin row), and the half it is sought in."""

    numbers: "list[int]"
    labels: "list[int]"
    own: int
    half: int


def _nearest(side: _Side, probes: "list[_Probe]", halves: bytearray, queries: "list[_Query]") -> "list[float]":
    """Each query's squared distance to its nearest real row of the half it names, over every probe's window."""
    best = [_NONE_FOUND] * len(queries)
    for probe in probes:
        keys = _all_keys(probe, side)
        ordered: "list[list[int]]" = []
        order: "list[list[int]]" = []
        for half in (0, 1):
            pairs = sorted((keys[row], row) for row in range(side.rows) if halves[row] == half)
            ordered += [[pair[0] for pair in pairs]]
            order += [[pair[1] for pair in pairs]]
            del pairs
        for at in range(len(queries)):
            query = queries[at]
            key = keys[query.own] if query.own >= 0 else _key(probe, query.numbers, query.labels)
            place = _first_at_least(ordered[query.half], key)
            for row in order[query.half][max(place - PROBE_WINDOW, 0): place + PROBE_WINDOW]:
                gap = _distance(query.numbers, query.labels, side, row)
                if best[at] == _NONE_FOUND or gap < best[at]:
                    best[at] = gap
    return best


def _point(ordered: "list[float]", thousandths: int) -> float:
    """The value at a percentile, in thousandths, of an ascending list (the lower of two neighbours)."""
    return ordered[(len(ordered) - 1) * thousandths // 1000]


def _closer_share(
    twin_gaps: "list[float]", real_gaps: "list[float]", real_units: "list[int]", cut: float
) -> "tuple[bool, float, float, float]":
    """Whether the twin's distances fall at or under a fresh half's percentile no more often than chance allows.

    The share of the twin's distances at or under ``cut`` (a percentile
    of the fresh half's distances) against the fresh half's own share
    there: allowed one in `MARGIN_ROWS` and `NOISE_ERRORS` standard
    errors over it, the spread read at the fresh share with half a
    distance added, as binomial shares of both counts, widened by the
    design effect of the fresh distances over the real table's people
    (``real_units``, a person a fresh distance; `_design_effect`). Read at the
    percentile, a twin whose rows sit on real rows shows as a share far
    over the fresh one, while two percentiles estimated from a few
    thousand rows each, compared as values, differ by more than five
    per cent by chance alone.
    """
    twin_under = sum(1 for gap in twin_gaps if gap <= cut)
    real_under = sum(1 for gap in real_gaps if gap <= cut)
    matched: "dict[int, int]" = {}
    read: "dict[int, int]" = {}
    for at in range(len(real_gaps)):
        _count_in(read, real_units[at], 1)
        _count_in(matched, real_units[at], 1 if real_gaps[at] <= cut else 0)
    design = _design_effect(matched, read)
    twin_share = twin_under / len(twin_gaps)
    fresh_share = real_under / len(real_gaps)
    smooth = (real_under + 0.5) / (len(real_gaps) + 1)
    spread = smooth * (1.0 - smooth) * (1.0 / len(twin_gaps) + 1.0 / len(real_gaps)) * design
    allowed = fresh_share + 1.0 / MARGIN_ROWS + NOISE_ERRORS * math.sqrt(spread)
    return twin_share <= allowed, twin_share, fresh_share, allowed


def _check_distances(
    real_side: _Side, real: _Real, twin_side: _Side, twin: _Twin, chosen: "list[int]", seed: int
) -> Check:
    """C2: the twin rows' distances to their nearest row of one real half, against the real rows' distances to their nearest row of the other half.

    LIKE FOR LIKE: each real person's rows read the half the person is
    not in, and each twin person's rows read one half, chosen by a fixed
    mix of the seed and the twin person's number, so every distance on
    either side is one person's row against half the real table. A twin
    row read against both halves gave two distances that move together,
    and the twin's low percentiles sat under the fresh ones by chance
    alone (a clean twin failed the 5th percentile in 1 of 30 runs).
    """
    width = len(real_side.numbers) + len(real_side.labels)
    if width == 0 or not chosen or real_side.rows < 2:
        return Check("C2", "nearest-record distance", False, True, ("No column of numbers, dates or labels was read.",))
    sizes = (real_side.rows - sum(real.halves), sum(real.halves))
    if sizes[0] == 0 or sizes[1] == 0:
        return Check("C2", "nearest-record distance", False, True, ("One real half holds no row.",))
    probes = _probes(seed, len(real_side.numbers), len(real_side.labels))
    twin_queries: "list[_Query]" = []
    for at in range(len(chosen)):
        numbers = [codes[at] for codes in twin.numbers]
        labels = [codes[at] for codes in twin.labels]
        half = _half_of((seed + _TWIN_SALT) & _MASK, twin_side.unit[chosen[at]])
        twin_queries += [_Query(numbers, labels, -1, half)]
    real_queries: "list[_Query]" = []
    for row in _chosen_rows(real_side.rows, QUERY_ROWS, seed, 3):
        numbers, labels = _row_codes(real_side, row)
        real_queries += [_Query(numbers, labels, row, 1 - real.halves[row])]
    twin_best = _nearest(real_side, probes, real.halves, twin_queries)
    real_best = _nearest(real_side, probes, real.halves, real_queries)
    twin_gaps = sorted(math.sqrt(gap / width) for gap in twin_best if gap != _NONE_FOUND)
    real_found = [at for at in range(len(real_best)) if real_best[at] != _NONE_FOUND]
    real_gaps = [math.sqrt(real_best[at] / width) for at in real_found]
    real_units = [real_side.unit[real_queries[at].own] for at in real_found]
    if not twin_gaps or not real_gaps:
        return Check("C2", "nearest-record distance", False, True, ("No nearest record was found.",))
    passed = True
    lines: "list[str]" = [
        f"{len(chosen)} twin rows against one real half each, and {len(real_gaps)} real rows against the other half, "
        f"over {width} columns.",
    ]
    ordered = sorted(real_gaps)
    for point in DISTANCE_POINTS:
        theirs = _point(ordered, point)
        mine = _point(twin_gaps, point)
        holds, twin_share, fresh_share, allowed = _closer_share(twin_gaps, real_gaps, real_units, theirs)
        passed = passed and holds
        lines += [
            f"Percentile {point / 10:g}: a fresh half's distance {theirs:.4f}, the twin's {mine:.4f}; "
            f"{_ten_thousandths(twin_share)} per 10,000 of the twin's distances are at or under the fresh one, "
            f"against {_ten_thousandths(fresh_share)} of the fresh half's; allowed up to {_ten_thousandths(allowed)}.",
        ]
    return Check("C2", "nearest-record distance", True, passed, tuple(lines))


def _read(raw_path: str, first_row: str) -> reading.Table:
    """A table read through the product's reader, in groups, refusals naming positions and never a value."""
    return reading.read_table(
        raw_path,
        first_row=first_row,
        refusals=reading.REFUSALS_NAME_POSITIONS,
        small_cell_floor=parsing.DEFAULT_SMALL_CELL_FLOOR,
        in_groups=True,
    )


def run_checks(
    real_path: str,
    twin_path: str,
    *,
    person: str = "",
    identifiers: "tuple[str, ...]" = (),
    not_identifiers: "tuple[str, ...]" = (),
    seed: int = DEFAULT_SEED,
    plan: "Plan | None" = None,
    first_row: str = reading.FIRST_ROW_NAMES,
    small_tables_refused: bool = True,
) -> Outcome:
    """The five checks of a twin against its real table.

    ``person`` names the person column (else the first column named as a
    key or a person whose keys repeat is read as one); ``identifiers``
    and ``not_identifiers`` are the person's answers about columns;
    ``plan``, where given, is a reading a caller already holds
    (`plan_from_roles`), and the three before it are then not read.
    ``seed`` fixes the halves and the rows C2 reads. ``first_row`` is
    how the real table's first row is read (`reading.FIRST_ROW_NAMES`
    or `reading.FIRST_ROW_DATA`); the twin's is always its names.

    - ``small_tables_refused``, keyword only and INTERNAL: True, the
      default and the only value the command runs with, refuses a real
      table under `parsing.TABLE_ROW_FLOOR` rows that hold a value or,
      where its person column repeats, under `parsing.TABLE_PEOPLE_FLOOR`
      people, as `synthtwin profile` does. False is for the gate files'
      small invented tables alone.

    Guarantees: the same two files, options and seed give the same
    outcome, every line a count, a rate or a distance and never a cell,
    a row's place or a person's key. Raises errors.ProfileError, in
    words, for a file the reader refuses, a twin whose columns are not
    the real table's, a person column the real table does not hold, or
    a table under the floor; PathValidationError for a path that is not
    a local file. Reads the two files; writes nothing.
    """
    names: "dict[str, str]" = {}
    for name in identifiers:
        names[name] = KIND_IDENTIFIER
    for name in not_identifiers:
        names[name] = ROLE_NOT_IDENTIFIER
    real_table = _read(real_path, first_row)
    if plan is None and names:
        plan = plan_from_roles(real_table.column_names, names, person)
        plan = Plan(plan.columns, plan.person if person else -2, "answered")
    if plan is not None and plan.person == -2:
        found = _person_place(real_table, "", None)
        plan = Plan(plan.columns, found, plan.source)
        if found >= 0:
            columns = list(plan.columns)
            columns[found] = dataclasses.replace(columns[found], kind=KIND_IDENTIFIER)
            plan = Plan(tuple(columns), found, plan.source)
    if plan is not None and len(plan.columns) != len(real_table.column_names):
        raise errors.ProfileError("The plan given does not name every column of the real table, one for one.")
    if small_tables_refused and real_table.n_rows < parsing.TABLE_ROW_FLOOR:
        raise _under_the_floor()
    real_side, real = _walk_real(real_table, plan, person, seed)
    # The real table's held columns go before the twin is read: what the
    # checks keep of it is its digests and codes (`_Side`, `_Real`).
    real_names = real_table.column_names
    del real_table
    held_rows = sum(real_side.held)
    if small_tables_refused and held_rows < parsing.TABLE_ROW_FLOOR:
        raise _under_the_floor()
    repeats = real.plan.person >= 0 and real.people < real_side.rows
    if small_tables_refused and repeats and real.people < parsing.TABLE_PEOPLE_FLOOR:
        raise _under_the_floor()
    twin_table = _read(twin_path, reading.FIRST_ROW_NAMES)
    if twin_table.column_names != real_names:
        raise errors.ProfileError(
            f"The twin's columns are not the real table's: the twin has {len(twin_table.column_names)} columns, the "
            f"real table {len(real_names)}, and their names must be the same, in the same order. Check "
            "that the twin was made from this table's description."
        )
    chosen = _chosen_rows(twin_table.n_rows, QUERY_ROWS, seed, 2)
    twin_side, twin = _walk_twin(twin_table, real, chosen)
    del twin_table
    checks = (
        _check_rows(real_side, real, twin_side),
        _check_distances(real_side, real, twin_side, twin, chosen, seed),
        _check_patients(real_side, real, twin_side),
        _check_identifiers(real, twin),
        _check_combinations(real_side, real, twin_side),
    )
    person_column = real_names[real.plan.person] if real.plan.person >= 0 else ""
    kinds = tuple(column.kind for column in real.plan.columns)
    return Outcome(
        checks, real_side.rows, twin_side.rows, real.people, twin.people, person_column, kinds, seed
    )


def _under_the_floor() -> errors.ProfileError:
    return errors.ProfileError(
        f"The real table is under the table floor: synthtwin makes and checks twins of tables of at least "
        f"{parsing.TABLE_ROW_FLOOR:,} rows that hold a value and, where one person has several rows, at least "
        f"{parsing.TABLE_PEOPLE_FLOOR:,} people. Nothing was checked."
    )


def report_lines(outcome: Outcome) -> "tuple[str, ...]":
    """The checks' block for a twin's report: counts, rates, distances and verdicts, never a value.

    Guarantees: a fixed function of the outcome. Counts under 11 are
    printed (the report stays inside the protected computer). No I/O.
    """
    person = f" (person column: {outcome.person_column})" if outcome.person_column else " (no person column)"
    kinds = ""
    for wanted in KINDS:
        counted = sum(1 for kind in outcome.kinds if kind == wanted)
        kinds = kinds + (", " if kinds else "") + f"{counted} {wanted}"
    lines: "list[str]" = [
        "The twin checked against the real table, inside the protected computer.",
        f"Real table: {outcome.real_rows} rows, {outcome.real_people} people{person}. "
        f"Twin: {outcome.twin_rows} rows, {outcome.twin_people} people.",
        f"Columns read as: {kinds}.",
        f"The fresh halves: the real table split in two by person under seed {outcome.seed}.",
    ]
    for check in outcome.checks:
        verdict = "PASS" if check.passed else "FAIL"
        if not check.measured:
            verdict = "NOT MEASURED"
        lines += [f"{check.code} {check.title}: {verdict}"]
        lines += ["  " + line for line in check.lines]
    failed = ""
    for check in outcome.checks:
        if not check.passed:
            failed = failed + (", " if failed else "") + check.code
    if failed:
        lines += [f"VERDICT: FAIL ({failed}). The twin is not released."]
    else:
        lines += ["VERDICT: PASS. Every check passed; the twin may be released."]
    return tuple(lines)


def report_text(outcome: Outcome) -> str:
    """The checks' report as text, a line each, ending with a line break."""
    return "\n".join(report_lines(outcome)) + "\n"


@dataclasses.dataclass(frozen=True)
class Released:
    """What one `release` did: the released twin's path ('' for none), the quarantined twin's path ('' for none), whether a redraw may follow, and the checks' outcome."""

    released: str
    quarantined: str
    redraw_allowed: bool
    outcome: Outcome


def quarantine_name(twin_name: str, attempt: int) -> str:
    """The name a failing twin takes in the quarantine folder: its own, marked with the attempt.

    Guarantees: a fixed function of the two; a name with no folder in
    it. Raises TypeError for a name that is not text. No I/O.
    """
    if not isinstance(twin_name, str):
        raise TypeError(_NOT_TEXT)
    stem = pathlib.Path(twin_name).stem
    suffix = pathlib.Path(twin_name).suffix
    return stem + f"-attempt-{attempt}" + suffix


def _write_report(folder: str, twin_name: str, outcome: Outcome) -> str:
    """The checks' report written beside a moved twin; its path."""
    report = pathlib.Path(folder, report_name(twin_name))
    report.write_text(report_text(outcome), encoding="utf-8", newline="\n")
    return str(report)


def _one_file(first: pathlib.Path, second: pathlib.Path) -> bool:
    """Whether two validated paths name one file: the same resolved path, or, both standing, one file by the file system's identity (a link, or another spelling a case-blind volume reads as the same)."""
    here = pathlib.Path(f"{first}")
    there = pathlib.Path(f"{second}")
    if f"{here}" == f"{there}":
        return True
    return here.exists() and there.exists() and here.samefile(there)


def _refuse_an_input(target: pathlib.Path, real_path: str, twin_path: str) -> None:
    """Refuse a report place that is the real table or the twin, or a link to either: the report never writes over what it read (the batch 4w Codex review, item 9)."""
    for given, what in ((real_path, "the real table"), (twin_path, "the twin")):
        if _one_file(target, validate_local_path(given, purpose="input")):
            raise ValueError(
                f"The checks' report would be written over {what} ({target}): name another file for the report."
            )


def report_place(real_path: str, twin_path: str, report: str = "") -> pathlib.Path:
    """Where `main` writes the checks' report, validated before anything is read (the batch 4w Codex review, item 9).

    ``report``, or else beside the twin under `report_name`. The place
    passes the locality gate first (`validate_local_path`: a web,
    network or Windows device form is refused before any file system
    call), then is refused where it is the real table or the twin, or a
    link to either (`_refuse_an_input`). Raises PathValidationError for a
    place or an input the gate refuses, ValueError for a place that is an
    input. Reads only whether the paths stand.
    """
    twin = pathlib.Path(twin_path)
    wanted = report if report else str(pathlib.Path(str(twin.parent), report_name(twin.name)))
    target = validate_local_path(wanted, purpose="report")
    _refuse_an_input(target, real_path, twin_path)
    return target


def _move(source: str, target: str) -> None:
    """Move a file to a new name, refusing to move over a file already there."""
    if pathlib.Path(target).exists():
        raise ValueError(
            f"A file is already at {target}: nothing is moved over another file. Move it away, then run again."
        )
    pathlib.Path(source).replace(target)


def release(
    real_path: str,
    twin_path: str,
    release_folder: str,
    quarantine_folder: str,
    *,
    attempt: int = 0,
    person: str = "",
    identifiers: "tuple[str, ...]" = (),
    not_identifiers: "tuple[str, ...]" = (),
    seed: int = DEFAULT_SEED,
    plan: "Plan | None" = None,
    first_row: str = reading.FIRST_ROW_NAMES,
    small_tables_refused: bool = True,
) -> Released:
    """Check a twin, then move it: into the release folder when every check passes, into the quarantine folder when one fails.

    THE QUARANTINE AND THE REDRAWS. A twin that fails is moved into
    ``quarantine_folder`` under `quarantine_name` (its name marked with
    ``attempt``), its check report beside it, and never into
    ``release_folder``. ``redraw_allowed`` says whether the caller may
    draw a new twin and call again with the next attempt: while
    ``attempt`` is under `REDRAWS_MOST`, so a run makes at most
    `REDRAWS_MOST` redraws before it stops. A twin that passes is moved
    into ``release_folder`` under its own name, its report beside it.
    The two folders are made, readable by their owner alone, where they
    do not exist. The other arguments are `run_checks`'s.

    Guarantees: a twin that failed a check is never moved into the
    release folder, and nothing is moved before its checks finish. THE
    PLACES FIRST (the batch 4w Codex review, item 9): both folders pass
    the locality gate before any file system call is made on them, and
    neither report the run may write is the real table or the twin.
    Raises ValueError, in words, when the two folders are one, when
    ``attempt`` is past `REDRAWS_MOST` or under 0, when a report would be
    written over an input, or when a file is already at a name a move
    would take; errors.ProfileError and PathValidationError as
    `run_checks` does; OSError where a move or a write fails.
    """
    if attempt < 0 or attempt > REDRAWS_MOST:
        raise ValueError(f"A run makes at most {REDRAWS_MOST} redraws; attempt {attempt} is not one of them.")
    released = validate_local_path(release_folder, purpose="release folder")
    quarantined = validate_local_path(quarantine_folder, purpose="quarantine folder")
    if _one_file(released, quarantined):
        raise ValueError("The release folder and the quarantine folder are one folder. Name two different folders.")
    name = pathlib.Path(twin_path).name
    for folder, written in ((released, name), (quarantined, quarantine_name(name, attempt))):
        _refuse_an_input(pathlib.Path(f"{folder}", report_name(written)), real_path, twin_path)
    outcome = run_checks(
        real_path,
        twin_path,
        person=person,
        identifiers=identifiers,
        not_identifiers=not_identifiers,
        seed=seed,
        plan=plan,
        first_row=first_row,
        small_tables_refused=small_tables_refused,
    )
    if outcome.passed:
        pathlib.Path(release_folder).mkdir(mode=0o700, parents=True, exist_ok=True)
        target = str(pathlib.Path(release_folder, name))
        _move(twin_path, target)
        _write_report(release_folder, name, outcome)
        return Released(target, "", False, outcome)
    pathlib.Path(quarantine_folder).mkdir(mode=0o700, parents=True, exist_ok=True)
    held = quarantine_name(name, attempt)
    target = str(pathlib.Path(quarantine_folder, held))
    _move(twin_path, target)
    _write_report(quarantine_folder, held, outcome)
    return Released("", target, attempt < REDRAWS_MOST, outcome)


def main(argv: "list[str] | None" = None, *, small_tables_refused: bool = True) -> int:
    """Run the checks from the command line; return 0 when every check passed, 3 when one failed, 1 when a file could not be read or written, 2 for options that cannot be used.

    ``small_tables_refused``, keyword only and INTERNAL, is
    `run_checks`'s: True, the default and the only value a typed command
    runs with; no option or environment variable sets it.

    Guarantees: prints the report and writes it (beside the twin, or at
    ``--report``; beside the moved twin with ``--release-to`` and
    ``--quarantine``); never prints a value of either table; the
    report's place is validated before either table is read
    (`report_place`), and a place that the locality gate refuses or
    that is the real table or the twin is an option that cannot be used
    (2), nothing read or written.
    """
    parser = argparse.ArgumentParser(
        prog="python -m synthtwin.twin_checks",
        description=(
            "Check a twin against its real table, inside the protected computer, before the twin is shared: "
            "exact row copies, nearest-record distances, copied patients, identifiers and dates, and rare "
            "combinations. Prints counts, rates and a verdict, never a value of either table."
        ),
    )
    parser.add_argument("real", help="the real table's file (CSV or workbook)")
    parser.add_argument("twin", help="the twin's file")
    parser.add_argument("--person", default="", help="the real table's person column, by name")
    parser.add_argument(
        "--identifier", action="append", default=[], help="a column that is an identifier (may be given more than once)"
    )
    parser.add_argument(
        "--not-identifier",
        action="append",
        default=[],
        help="a column you answered is no identifier (may be given more than once)",
    )
    parser.add_argument("--seed", default=str(DEFAULT_SEED), help="the whole number that splits the real table in halves")
    parser.add_argument(
        "--first-row", default="names", choices=["names", "data"], help="how the real table's first row reads"
    )
    parser.add_argument("--report", default="", help="where to write the report (default: beside the twin)")
    parser.add_argument("--release-to", default="", help="move a twin that passes into this folder")
    parser.add_argument("--quarantine", default="", help="move a twin that fails into this folder")
    options = parser.parse_args(argv)
    seed_text = f"{options.seed}"
    if not _all_figures(seed_text):
        print("The seed must be a whole number in figures, such as 1.", file=sys.stderr)
        return 2
    if bool(options.release_to) != bool(options.quarantine):
        print("Give --release-to and --quarantine together, or neither.", file=sys.stderr)
        return 2
    first_row = reading.FIRST_ROW_NAMES if options.first_row == "names" else reading.FIRST_ROW_DATA
    seed = int(seed_text)
    identifiers = tuple(f"{name}" for name in options.identifier)
    not_identifiers = tuple(f"{name}" for name in options.not_identifier)
    try:
        if options.release_to:
            done = release(
                f"{options.real}",
                f"{options.twin}",
                f"{options.release_to}",
                f"{options.quarantine}",
                person=f"{options.person}",
                identifiers=identifiers,
                not_identifiers=not_identifiers,
                seed=seed,
                first_row=first_row,
                small_tables_refused=small_tables_refused,
            )
            print(report_text(done.outcome), end="")
            print(("Released: " + done.released) if done.released else ("Quarantined: " + done.quarantined))
            return 0 if done.outcome.passed else 3
        try:
            target = report_place(f"{options.real}", f"{options.twin}", f"{options.report}")
        except ValueError as refused:
            print(f"{refused}", file=sys.stderr)
            return 2
        outcome = run_checks(
            f"{options.real}",
            f"{options.twin}",
            person=f"{options.person}",
            identifiers=identifiers,
            not_identifiers=not_identifiers,
            seed=seed,
            first_row=first_row,
            small_tables_refused=small_tables_refused,
        )
        text = report_text(outcome)
        pathlib.Path(f"{target}").write_text(text, encoding="utf-8", newline="\n")
        print(text, end="")
        print(f"The report: {target}")
        return 0 if outcome.passed else 3
    except (errors.ProfileError, PathValidationError, ValueError, OSError) as failed:
        print(f"{failed}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

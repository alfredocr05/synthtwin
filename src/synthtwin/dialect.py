"""The file's written form: how a table's bytes are laid out (owner, 2026-09-15).

THE RULING THIS MODULE EXISTS FOR. "Twin should always write anything as
the original source, without changes." Code developed on the twin has to
run unchanged on the real table, and code that reads a file is written
against its bytes: the character between fields, how a row ends, whether
a byte-order mark comes first, which fields are quoted, whether the last
row ends with a line break, where blank lines stand, whether a title
line comes before the names. Until this module the twin was always a
comma-separated UTF-8 file with line-feed endings and minimal quoting,
whatever the table was, and a semicolon file was read as one column of
free text.

WHAT IS HERE, IN THREE HALVES THAT MUST AGREE.

1. `survey` reads a table's decoded text and says how it is written: the
   delimiter, the quoting and escaping, the line endings in file order,
   the lines that are not records (a separator hint, a preamble, blank
   lines), the metadata rows some survey exports put under the names,
   and per column how its cells are quoted, whether they are padded to a
   width and whether they are the row sequence. It also returns the
   table's records, so the reader that calls it has one reading, not two.
2. `twin_text` writes a twin's rows back in a published form.
3. `arranged` places a twin's rows where the form says they stand: the
   order the source was sorted in, the empty records, the row sequence.

The first halves are held to each other by the round trip: a twin written
by (2) and (3), surveyed by (1), gives back the form it was written from.
The suite checks that per shape.

THE LEXER IS THE STANDARD READER'S, WRITTEN OUT. The reader module reads
every table with the standard library's `csv` reader and compares the
result with pandas. That reader does not say whether a field was quoted
or what ended a record, and those are exactly the facts this module
publishes, so `_records` walks the text by the same state machine the
standard reader's C code runs -- start of record, start of field, inside
a quoted field, a quote inside a quoted field, an escaped character, the
end of a line -- and records the two facts on the way. The reader then
runs the standard reader over the same text and requires every record to
agree, so a divergence between the two is a refusal and never a silent
difference.

THE BOUNDARY (plan P2-D1). Nothing here opens a file, and nothing here
imports the reader, `csv` or pandas: the generator imports this module to
write and arrange a twin, and it may not reach anything that opens a
table. The text arrives already decoded; the bytes, where they matter,
arrive as bytes.

WHAT A FACT HERE DISCLOSES. Every fact describes the file's writer, not a
person: a delimiter, an ending, a quoting habit, a position in the file.
Two are text of the file -- the preamble lines and the metadata rows --
and they are treated differently on purpose. Metadata rows are one cell
per column saying what the column is, which is schema, and they are
published like names. A preamble line is free text that may name
anybody, so NO text of one is published at any smallest group: what
reaches a description is the run's SHAPE -- blank, or the punctuation a
comment began with -- and the twin writes a neutral stand-in of that
shape (`preamble_line`, plan P4-D80). The mark stops at a quote
character and at the delimiter, so the stand-in is still one record of
the file (plan P4-D83).

Imports here stay within the allowlist (plan D6.2): dataclasses, and this
package's own `errors` and `parsing`, neither of which reaches a file.
"""

import dataclasses

from synthtwin import errors, parsing

# -- the vocabularies --------------------------------------------------

# The field delimiters a table may be written with. A comma-space table
# (`"a", "b"`) is a comma table with `initial_space`.
DELIMITERS = (",", ";", "\t", "|")
DELIMITER_WORDS = {
    ",": "a comma",
    ";": "a semicolon",
    "\t": "a tab",
    "|": "a vertical bar",
}

# How a line ends. `crcrlf` is what Python's own csv writer produces on
# Windows in text mode, and a file of them is one terminator per record,
# not a record and a blank line.
ENDINGS = ("lf", "crlf", "cr", "crcrlf")
ENDING_TEXT = {"lf": "\n", "crlf": "\r\n", "cr": "\r", "crcrlf": "\r\r\n"}
ENDING_WORDS = {
    "lf": "line feed",
    "crlf": "carriage return and line feed",
    "cr": "carriage return",
    "crcrlf": "two carriage returns and a line feed",
}

# How a quote character is written inside a quoted field.
ESCAPE_DOUBLED = "doubled"
ESCAPE_BACKSLASH = "backslash"
ESCAPES = (ESCAPE_DOUBLED, ESCAPE_BACKSLASH)

# The classes a cell's quoting is recorded by. A writer quotes by what a
# value IS -- R quotes strings and leaves numbers and NA bare, Python's
# QUOTE_NONNUMERIC quotes whatever is not a number -- so one rule per
# column is not enough and one rule per cell would be a fact about a
# row. `absent` is a built-in spelling of no value other than the empty
# one (`NA`, `NULL`, ...); `empty` is the empty cell.
CELL_ABSENT = "absent"
CELL_EMPTY = "empty"
CELL_NUMBER = "number"
CELL_TEXT = "text"
CELL_CLASSES = (CELL_ABSENT, CELL_EMPTY, CELL_NUMBER, CELL_TEXT)
_CLASS_PLACE = {CELL_ABSENT: 0, CELL_EMPTY: 1, CELL_NUMBER: 2, CELL_TEXT: 3}

# When a cell of one class is quoted. `needed`: exactly when it has to
# be for a reader to read it back (it holds the delimiter, a quote
# character, a line break). `bare`: only when it could not be read back
# otherwise, so a quote character inside a value is left bare, as
# lenient writers leave it. `always`: every cell. `mixed`: the source
# quoted cells of this class in no way these three describe; the twin is
# written `needed` and the report says the quoting was not kept.
QUOTE_NEEDED = "needed"
QUOTE_BARE = "bare"
QUOTE_ALWAYS = "always"
QUOTE_MIXED = "mixed"
QUOTE_RULES = (QUOTE_NEEDED, QUOTE_BARE, QUOTE_ALWAYS, QUOTE_MIXED)
_CANONICAL_ORDER = (QUOTE_NEEDED, QUOTE_BARE, QUOTE_ALWAYS)

COLLATION_NUMBER = "number"
COLLATION_TEXT = "text"
# THE THIRD COLLATION, AND WHY A THIRD WAS NEEDED (review item CODEX-9).
# A column the person declared with `--decimal-comma` writes `0,5` and
# `10,0`. The ordinary number grammar reads neither as a number, so such
# a column fell through to the text collation, where `10,0` sorts before
# `9,9` -- and a table genuinely sorted by that column published NO row
# order, or published one the twin then wrote in the wrong order.
# Measured on 129 ascending amounts: `row_order` came back null.
#
# The declared grammar is a published fact of the order rather than a
# second argument threaded beside it, which is what keeps the generator
# and the validator honest: both read the collation out of the
# description and neither has to be told the declaration separately.
COLLATION_DECIMAL_COMMA = "decimal_comma"
COLLATIONS = (COLLATION_NUMBER, COLLATION_TEXT, COLLATION_DECIMAL_COMMA)
ASCENDING = "ascending"
DESCENDING = "descending"
DIRECTIONS = (ASCENDING, DESCENDING)
PAD_LEFT = "left"
PAD_RIGHT = "right"
PAD_SIDES = (PAD_LEFT, PAD_RIGHT)

# The encodings a table is read under, as the description names them.
# `utf-8-sig` is UTF-8 with or without a mark (`byte_order_mark` says
# which); the UTF-16 pair is read only behind its own mark.
ENCODING_UTF8 = "utf-8-sig"
ENCODING_LATIN1 = "latin-1"
ENCODING_CP1252 = "cp1252"
ENCODING_UTF16_LE = "utf-16-le"
ENCODING_UTF16_BE = "utf-16-be"
ENCODINGS = (
    ENCODING_UTF8,
    ENCODING_LATIN1,
    ENCODING_CP1252,
    ENCODING_UTF16_LE,
    ENCODING_UTF16_BE,
)
FALLBACK_ENCODINGS = (ENCODING_LATIN1, ENCODING_CP1252)
ENCODING_WORDS = {
    ENCODING_UTF8: "UTF-8",
    ENCODING_LATIN1: "Western European text (Latin-1)",
    ENCODING_CP1252: "Windows Western European text (Windows-1252)",
    ENCODING_UTF16_LE: "UTF-16, little-endian",
    ENCODING_UTF16_BE: "UTF-16, big-endian",
}

# The codec a twin is written with, per published encoding. The mark of
# a UTF-8 or UTF-16 file is put into the text by `twin_text` itself, so
# the codec here never adds one of its own.
WRITING_CODECS = {
    ENCODING_UTF8: "utf-8",
    ENCODING_LATIN1: "latin-1",
    ENCODING_CP1252: "cp1252",
    ENCODING_UTF16_LE: "utf-16-le",
    ENCODING_UTF16_BE: "utf-16-be",
}

# The codec the standard reader and pandas open a table with. A UTF-16
# table is opened with the codec that reads and consumes its mark.
READING_CODECS = {
    ENCODING_UTF8: "utf-8-sig",
    ENCODING_LATIN1: "latin-1",
    ENCODING_CP1252: "cp1252",
    ENCODING_UTF16_LE: "utf-16",
    ENCODING_UTF16_BE: "utf-16",
}

# Caps. None of them is a fact about a person; they bound the
# description's size. PAST THE FIRST TWO THE FILE IS STILL DESCRIBED,
# more coarsely, and never refused (repair of landing 2b.9: a file 53bb012
# twinned may not be refused by this landing). Line endings that change
# kind more often than this are published as how many lines end each way
# (`line_endings_spread`), and the twin spreads the rarer endings evenly;
# blank lines standing in more places than this are published as how
# many there are, where the first and last stand and what they hold
# (`blank_lines_spread`), and the twin spreads them evenly between those
# two places -- which is exact for a double-spaced file. A longer preamble
# than its cap is not a preamble: those lines are read as the table's.
# -- what a SPREADSHEET WORKBOOK's cells are, as closed sets ----------
#
# THESE LIVE HERE AND NOT IN `workbook` FOR ONE REASON: the loader reads
# them, and the loader is in the GENERATOR's import graph. `workbook`
# carries an XML parser, and the generator must reach no parser and no
# reader of the user's table at any instant (plan P2-D1, P4-D77). So the
# vocabulary a DESCRIPTION is checked against sits in this module, which
# holds no capability at all, and `workbook` imports it back for its own
# use. The names are prefixed because this module already has cell
# classes of its own, for delimited text, and they are a different set.

SHEET_CELL_ABSENT = "absent"
SHEET_CELL_BLANK = "blank"
SHEET_CELL_EMPTY = "empty"
SHEET_CELL_TEXT = "text"
SHEET_CELL_NUMBER = "number"
SHEET_CELL_BOOLEAN = "boolean"
SHEET_CELL_ERROR = "error"
# A CELL STORED AS AN ISO DATE (`t="d"`, plan P4-D168). The file keeps
# its date as text -- `2026-01-05T00:00:00` -- rather than as a number
# wearing a date format, and every reader hands it back as a date. It
# used to fall through to the number branch, publish `number`, and come
# back from the twin as TEXT: pandas read datetimes from the source and
# strings from the twin, and the twin missed `workbook.cell-classes`. It
# is its own class now, spelled as the text the file holds and written
# back the way the file wrote it.
SHEET_CELL_DATE = "date"
SHEET_CELL_CLASSES = (
    SHEET_CELL_ABSENT,
    SHEET_CELL_BLANK,
    SHEET_CELL_EMPTY,
    SHEET_CELL_TEXT,
    SHEET_CELL_NUMBER,
    SHEET_CELL_BOOLEAN,
    SHEET_CELL_ERROR,
    SHEET_CELL_DATE,
)

# The classes that HOLD a value, in the order the twin's writer hands a
# census out in: the ones whose cells a spelling can be told apart by
# first, text last (plan P4-D166).
SHEET_VALUE_CLASSES = (
    SHEET_CELL_ERROR,
    SHEET_CELL_BOOLEAN,
    SHEET_CELL_DATE,
    SHEET_CELL_NUMBER,
    SHEET_CELL_TEXT,
)

# The error cells a spreadsheet writes, by kind. It lives here rather
# than in `workbook` because the twin's WRITER asks it too -- an error
# class is handed only to a cell spelled as an error (plan P4-D166) --
# and the writer may not reach the module that parses a workbook.
SHEET_ERROR_KINDS = (
    "#DIV/0!",
    "#N/A",
    "#NAME?",
    "#NULL!",
    "#NUM!",
    "#REF!",
    "#VALUE!",
    "#GETTING_DATA",
    "#SPILL!",
    "#CALC!",
)

# How a boolean cell is spelled for the column machinery.
SHEET_BOOLEAN_TRUE = "TRUE"
SHEET_BOOLEAN_FALSE = "FALSE"

SHEET_FORMAT_PLAIN = "plain"
SHEET_FORMAT_DATE = "date"
SHEET_FORMAT_DATETIME = "datetime"
SHEET_FORMAT_TIME = "time"
SHEET_FORMAT_ELAPSED = "elapsed"
SHEET_FORMAT_TEXT = "text"
SHEET_FORMAT_KINDS = (
    SHEET_FORMAT_PLAIN,
    SHEET_FORMAT_DATE,
    SHEET_FORMAT_DATETIME,
    SHEET_FORMAT_TIME,
    SHEET_FORMAT_ELAPSED,
    SHEET_FORMAT_TEXT,
)

# THE LAST ROW AND THE LAST COLUMN A WORKSHEET HAS. Excel's own limits,
# stated here rather than in the reader, because the LOADER asks them
# too and the loader may not import a module that opens a table
# (plan P4-D288). `workbook.MAXIMUM_ROWS` and
# `workbook.MAXIMUM_COLUMNS` are these.
SHEET_MAXIMUM_ROWS = 1_048_576
SHEET_MAXIMUM_COLUMNS = 16_384

SHEET_DATE_SYSTEM_1900 = "1900"
SHEET_DATE_SYSTEM_1904 = "1904"
SHEET_DATE_SYSTEMS = (SHEET_DATE_SYSTEM_1900, SHEET_DATE_SYSTEM_1904)

SHEET_KEYS = (
    "autofilter",
    "columns",
    "date_system",
    "defined_names",
    "defined_table",
    "empty_rows_inside",
    "frozen_rows",
    "macro_project",
    "rows_above_header",
    "sheet_count",
    "sheet_extents",
    "sheet_hidden",
    "sheet_names",
    "sheet_position",
    "trailing_blank_columns",
    "trailing_blank_rows",
)

SHEET_COLUMN_KEYS = (
    "cell_classes",
    "format_code",
    "format_kinds",
    "formulas",
    "value_class",
)


# -- what a census of a workbook may publish (plan P4-D164) -----------
#
# THE DISCLOSURE RULE, WRITTEN ONCE. Every count the workbook block
# publishes -- a column's cell classes, its format kinds, its formulas,
# the records holding nothing -- counts CELLS OF THE TABLE, which is to
# say rows, and the owner's third clause says the description reveals
# nothing about any individual. The first writing held each count to the
# floor on its own, and a review measured two ways through it: a column
# of sixty numbers, thirty-nine texts and one boolean published the
# boolean's count of 1 at the default floor, and at a floor of five
# published `60, 39, null` with every other class `0` -- so 100 - 60 - 39
# rebuilt the count the floor had held back.
#
# So a census is published by these rules, and the producer and the
# loader both ask this module rather than each keeping a copy:
#
# * THE LINE is the floor or two, whichever is larger. No published count
#   is ever one, and no count's complement within the column is either.
# * A count is SMALL where it is neither nought nor the whole column and
#   it or its complement falls under the line. Where no count is small
#   the census is published exactly.
# * Where one is, every small count AND every nought is withheld
#   together, so that a withheld key never says "some, but few" -- a
#   reader cannot tell a withheld nought from a withheld handful.
# * THE POOL a reader can subtract -- the column's total less every
#   published count -- is never under the line, and holds at least two
#   keys. Where it would, the smallest published count joins it, the
#   earlier key on a tie, until it does or nothing is left published.
#   A census with nothing left published stands whatever the column's
#   total: what it leaves to subtract from is the row count alone, which
#   is published beside it (plan P4-D174).
#
# A SINGLE COUNT beside its total is the same rule with nowhere to pool:
# it is published where it is the whole, or where it and its complement
# both reach the line, and withheld otherwise -- a nought included, for
# the same reason.


def sheet_line(floor: int) -> int:
    """The smallest count a workbook census publishes: the floor, or two.

    `parsing.census_floor`, the line of the one disclosure rule, under
    the name the workbook censuses read it by (written once at the merge
    of the files review's repair, which had stated it a second time).

    Guarantees: a fixed function of the floor. Raises nothing.
    """
    return parsing.census_floor(floor)


def _small(count: int, total: int, line: int) -> bool:
    """Whether a count, or its complement, would name fewer than the line.

    `parsing.census_nameable` over the count and its total, asked of a
    count that is neither nought nor the whole: a nought and a whole are
    not small (a whole leaves nothing over, and a nought is settled by
    the census's own pooling rule above). ``line`` is already at least
    two, so asking the rule at that floor holds it to that line.
    """
    if count <= 0 or count >= total:
        return False
    return not parsing.census_nameable([count], [total], line)


def sheet_census(
    counts: "dict[str, int]",
    every: "tuple[str, ...]",
    total: int,
    floor: int,
) -> "dict[str, int | None]":
    """One census over a closed key space, as it may be published.

    Guarantees:

    - Inputs: a count per key (a key absent from ``counts`` counts
      nought), the closed key space in its fixed order, the cells the
      census partitions, and the settings floor.
    - Determinism: a fixed function of the arguments. Ties are broken
      by the order of ``every``.
    - Errors raised: none.
    - Boundary: the rules in the comment above, and nothing else; the
      loader holds a published census to them through
      `sheet_census_broken`.
    """
    line = sheet_line(floor)
    held: "dict[str, int]" = {}
    for key in every:
        held[key] = counts[key] if key in counts else 0
    small = False
    for key in every:
        if _small(held[key], total, line):
            small = True
    out: "dict[str, int | None]" = {}
    if not small:
        for key in every:
            out[key] = held[key]
        return out
    pooled: "dict[str, bool]" = {}
    for key in every:
        if held[key] == 0 or _small(held[key], total, line):
            pooled[key] = True
    while True:
        remainder = 0
        for key in pooled:
            remainder = remainder + held[key]
        if len(pooled) >= 2 and (remainder == 0 or remainder >= line):
            break
        smallest = ""
        for key in every:
            if key in pooled:
                continue
            if not smallest or held[key] < held[smallest]:
                smallest = key
        if not smallest:
            break
        pooled[smallest] = True
    for key in every:
        out[key] = None if key in pooled else held[key]
    return out


def sheet_count(count: int, total: int, floor: int) -> "int | None":
    """One count beside its total, as it may be published.

    Published where it is the whole, or where it and its complement both
    reach the line; withheld otherwise, a nought included, so that a
    withheld count never says "some, but few". Guarantees: a fixed
    function of the arguments; raises nothing.
    """
    if total > 0 and count == total:
        return count
    if count > 0 and parsing.census_nameable([count], [total], floor):
        return count
    return None


def sheet_census_broken(
    published: "dict[str, int | None]", total: int, floor: int
) -> str:
    """What a published census breaks of the rules above, or nothing.

    The loader's half of `sheet_census`: a description may be written by
    hand, so what is checked is the census as it stands, and every way
    it could name a row is refused by name. Returns an empty string for
    a census the rules allow.

    Guarantees: a fixed function of the arguments; raises nothing.
    """
    line = sheet_line(floor)
    withheld = 0
    counted = 0
    nought = False
    for key in sorted(published):
        found = published[key]
        if found is None:
            withheld = withheld + 1
            continue
        counted = counted + found
        if found == 0:
            nought = True
        if _small(found, total, line):
            return (
                f"a census publishes {found} of {total} cells, and the "
                f"line is {line}"
            )
    if counted > total:
        return f"a census counts {counted} cells of {total}"
    if not withheld:
        if counted != total:
            return f"a census counts {counted} cells of {total}"
        return ""
    if nought:
        return "a census publishes a nought beside a count it withholds"
    if withheld < 2:
        return "a census withholds one count, which the others rebuild"
    remainder = total - counted
    # A CENSUS HELD BACK WHOLE leaves the row count as the only thing to
    # subtract from, and the row count is published anyway: a table of
    # eight rows at a floor of eleven withholds every count, and that
    # names nobody. Refusing it refused the producer's own description
    # (plan P4-D174).
    if counted and 0 < remainder < line:
        return (
            f"the counts a census withholds come to {remainder}, and the "
            f"line is {line}"
        )
    return ""


def sheet_count_broken(count: "int | None", total: int, floor: int) -> str:
    """What a published single count breaks of the rules above, or nothing."""
    if count is None:
        return ""
    if sheet_count(count, total, floor) == count:
        return ""
    return (
        f"a count of {count} of {total} is published, and the line is "
        f"{sheet_line(floor)}"
    )


# -- which spellings a workbook cell of each class can be written with --
#
# ONE READING, TWO CALLERS (plan P4-D166). The twin's writer hands a
# class only to a cell spelled the way that class is written -- an error
# to `#N/A`, a boolean to `TRUE` -- and the reader refuses a column in
# which a cell of one class is spelled the way another class present in
# it is written, because there the writer cannot tell which values were
# which. Both ask here, so the two cannot disagree about a spelling.


def _figures_only(text: str) -> bool:
    """Whether every character is an ASCII digit, and there is one."""
    if not text:
        return False
    for character in text:
        place = ord(character)
        if place < 48 or place > 57:
            return False
    return True


def sheet_number_spelling(text: str) -> str:
    """The text as a workbook stores a number, or "" where it is not one.

    WHAT IS DELIBERATELY REFUSED HERE. A number a workbook stores is a
    plain spelling: an optional sign, figures, an optional point and
    figures, an optional exponent. A grouped number (`1,234`), a
    decimal comma (`0,5`), a bracketed negative, a percent sign or a
    currency mark is NOT one -- in a workbook those are a FORMAT worn by
    a plain number, never the stored value -- so a cell whose text is
    written that way is written as text and keeps its characters.
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a cell's text was not text")
    if not text:
        return ""
    body = text
    if body[:1] in ("-", "+"):
        body = body[1:]
    mantissa = body
    exponent = ""
    place = mantissa.find("e")
    if place < 0:
        place = mantissa.find("E")
    if place >= 0:
        exponent = mantissa[place + 1 :]
        mantissa = mantissa[:place]
        # AN EXPONENT MARK OWES FIGURES (plan P4-D173): `1e` is text, and
        # was written as a stored number no reader can read.
        if exponent[:1] in ("-", "+"):
            exponent = exponent[1:]
        if not _figures_only(exponent):
            return ""
    point = mantissa.find(".")
    if point >= 0:
        whole = mantissa[:point]
        fraction = mantissa[point + 1 :]
        if whole and not _figures_only(whole):
            return ""
        if fraction and not _figures_only(fraction):
            return ""
        if not whole and not fraction:
            return ""
        return text
    if not _figures_only(mantissa):
        return ""
    return text


def _figures_at(text: str, start: int, count: int) -> bool:
    """Whether `count` ASCII digits stand at `start`."""
    return _figures_only(text[start : start + count]) and len(
        text[start : start + count]
    ) == count


def sheet_iso_date(text: str) -> bool:
    """Whether the text is how a workbook stores a date as ISO text.

    `YYYY-MM-DD`, optionally followed by `T` and `hh:mm`, `hh:mm:ss` or
    `hh:mm:ss` with a fraction; or a clock of that shape alone. That is
    the shape a `t="d"` cell holds (plan P4-D168).
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a cell's text was not text")
    clock = text
    if _figures_at(text, 0, 4) and text[4:5] == "-":
        if not (
            _figures_at(text, 5, 2)
            and text[7:8] == "-"
            and _figures_at(text, 8, 2)
        ):
            return False
        if len(text) == 10:
            return True
        if text[10:11] != "T":
            return False
        clock = text[11:]
    if not (_figures_at(clock, 0, 2) and clock[2:3] == ":"):
        return False
    if not _figures_at(clock, 3, 2):
        return False
    if len(clock) == 5:
        return True
    if clock[5:6] != ":" or not _figures_at(clock, 6, 2):
        return False
    if len(clock) == 8:
        return True
    return clock[8:9] == "." and _figures_only(clock[9:])


def _clock_fields(text: str) -> "tuple[str, str, str, str]":
    """A date cell's clock split into its hours, minutes, seconds, rest.

    Asked only of text `sheet_iso_date` has already accepted, so the
    shape is known: an empty field is a clock the text does not carry.
    """
    clock = text
    if len(text) >= 10 and text[4:5] == "-":
        if len(text) == 10:
            return "", "", "", ""
        clock = text[11:]
    seconds = ""
    rest = ""
    if len(clock) > 5:
        seconds = clock[6:8]
        rest = clock[8:]
    return clock[0:2], clock[3:5], seconds, rest


def sheet_date_is_real(text: str) -> bool:
    """Whether the text names a day of the calendar and a time of the clock.

    THE NARROWING A TWIN NO READER COULD OPEN TAUGHT (plan P4-D291).
    `sheet_iso_date` reads the SHAPE alone, and a made-up cell of four
    figures, a hyphen, two figures, a hyphen and two figures wears that
    shape whatever the figures say: `2006-06-32` and `8204-84-03` both
    wear it. A workbook cell marked as holding a date (`t="d"`) carries
    those characters as the date itself, so a reader that parses the
    cell -- which is every reader but this one -- stops on the whole
    FILE rather than on the cell. Measured at a smallest group of
    eleven on 118 date cells: openpyxl raised `day is out of range for
    month` and could not open the twin at all.

    So the shape is asked first and then the calendar: the month is one
    of the twelve, the day is one the month has in that year
    (`parsing.valid_date`, the one statement of the calendar), the hour
    is at most 23 and the minutes and seconds at most 59. A fraction of
    a second is figures and has no range of its own.

    Guarantees: accepts text; returns a truth value; a fixed function of
    the text. Raises `TypeError` where what it was handed is not text.
    No I/O of any kind.
    """
    if not sheet_iso_date(text):
        return False
    if len(text) >= 10 and text[4:5] == "-":
        if not parsing.valid_date(
            int(text[0:4]), int(text[5:7]), int(text[8:10])
        ):
            return False
    hours, minutes, seconds, _rest = _clock_fields(text)
    if hours and int(hours) > 23:
        return False
    if minutes and int(minutes) > 59:
        return False
    if seconds and int(seconds) > 59:
        return False
    return True


def _month_length(year: int, month: int) -> int:
    """How many days that month of that year has, by the one calendar."""
    day = 31
    while day > 28 and not parsing.valid_date(year, month, day):
        day = day - 1
    return day


def _brought_to(figures: str, least: int, most: int) -> str:
    """One field moved to the nearest value its range allows, at its width."""
    found = int(figures)
    if found < least:
        found = least
    if found > most:
        found = most
    written = f"{found}"
    while len(written) < len(figures):
        written = "0" + written
    return written


def sheet_date_on_the_calendar(text: str) -> str:
    """The same date cell with every field brought onto the calendar.

    WHAT THE WRITER DOES INSTEAD OF WRITING A FILE NOBODY CAN OPEN
    (plan P4-D291). A column whose cells the source stored as dates is
    written as dates, and where the column's ROLE publishes no value of
    it -- free text, a long tail -- the cells handed here are made up
    from the column's published SHAPE and wear a date's shape without
    naming a date. Each field is moved to the nearest value the
    calendar allows, at the width it was written with: the year to at
    least `0001`, the month into the twelve, the day into the days that
    month has, the hour to at most 23 and the minutes and seconds to at
    most 59. The shape is what the description publishes about such a
    column, and the shape does not move, so what the twin holds of that
    column is what it held before -- written as a date a reader can
    read.

    A cell that is not a date's shape, and a cell that already names a
    day of the calendar, are returned exactly as they came: a column
    whose dates ARE published is generated from instants and never
    reaches the first branch below.

    Guarantees: accepts text; returns text of the same length; a fixed
    function of the text. Raises `TypeError` where what it was handed is
    not text. No I/O of any kind.
    """
    if sheet_date_is_real(text) or not sheet_iso_date(text):
        return text
    dated = ""
    clock = text
    if len(text) >= 10 and text[4:5] == "-":
        year = _brought_to(text[0:4], 1, 9999)
        month = _brought_to(text[5:7], 1, 12)
        day = _brought_to(text[8:10], 1, _month_length(int(year), int(month)))
        dated = f"{year}-{month}-{day}"
        if len(text) == 10:
            return dated
        clock = text[11:]
        dated = dated + "T"
    hours, minutes, seconds, rest = _clock_fields(text)
    written = f"{_brought_to(hours, 0, 23)}:{_brought_to(minutes, 0, 59)}"
    if seconds:
        written = written + f":{_brought_to(seconds, 0, 59)}" + rest
    if len(clock) != len(written):
        raise ValueError("internal check: a date cell changed its width")
    return dated + written


def sheet_class_fits(kind: str, text: str) -> bool:
    """Whether a cell holding this text can be written as this class.

    Text can hold anything, and so can a class holding nothing (its cell
    is written without its text). An error is one of the error kinds, a
    boolean is `TRUE` or `FALSE` as the reader spells one, a date is ISO
    text naming a day of the calendar (`sheet_date_is_real`, plan
    P4-D291), and a number is a plain number's spelling.
    """
    if kind == SHEET_CELL_ERROR:
        return text in SHEET_ERROR_KINDS
    if kind == SHEET_CELL_BOOLEAN:
        return text in (SHEET_BOOLEAN_TRUE, SHEET_BOOLEAN_FALSE)
    if kind == SHEET_CELL_DATE:
        return sheet_date_is_real(text)
    if kind == SHEET_CELL_NUMBER:
        return sheet_number_spelling(text) != ""
    return True


# -- what the twin is WRITTEN with (plan P4-D79) -----------------------
#
# Part 1 of this landing read a workbook and published the KIND of thing
# each cell's number format made of it, deliberately withholding the
# format CODE: a custom code is text out of somebody's file, and a
# census keyed by codes would publish that text as a key.
#
# A twin that is itself a workbook cannot be written from the kind
# alone. A date is a number wearing a format, so a column written with
# no format code comes back from every reader as a column of five-digit
# numbers rather than as dates, and the twin then fails the one thing it
# exists for: code developed on it does not run unchanged on the real
# table. So a code IS published now -- but only ever one of these, which
# are Excel's own published vocabulary and synthtwin's own, and never
# the person's. A custom code is published as the CANONICAL code of its
# kind, which is the stated limit of the landing: the twin wears the
# standard code for a date rather than the one somebody typed.

# Excel's built-in number formats, by the id the file stores. These are
# the codes of the OOXML standard itself, not text of anybody's table,
# which is what makes them publishable at all. The writer needs the id
# for each so it can write a built-in format rather than making up a
# custom one, and the reader needs the code for each id.
SHEET_BUILT_IN_FORMAT_IDS = {
    "General": 0,
    "0": 1,
    "0.00": 2,
    "#,##0": 3,
    "#,##0.00": 4,
    "0%": 9,
    "0.00%": 10,
    "0.00E+00": 11,
    "# ?/?": 12,
    "# ??/??": 13,
    "mm-dd-yy": 14,
    "d-mmm-yy": 15,
    "d-mmm": 16,
    "mmm-yy": 17,
    "h:mm AM/PM": 18,
    "h:mm:ss AM/PM": 19,
    "h:mm": 20,
    "h:mm:ss": 21,
    "m/d/yy h:mm": 22,
    "#,##0 ;(#,##0)": 37,
    "#,##0 ;[Red](#,##0)": 38,
    "#,##0.00;(#,##0.00)": 39,
    "#,##0.00;[Red](#,##0.00)": 40,
    "mm:ss": 45,
    "[h]:mm:ss": 46,
    "mmss.0": 47,
    "##0.0E+0": 48,
    "@": 49,
}

# The canonical code for each kind, used where the file's own code is
# not one of Excel's built-in ones. Each is an ordinary unambiguous
# spelling of its kind and none of them carries a currency symbol, a
# unit or a label, because those are the parts of a custom code that
# could be somebody's text.
SHEET_CANONICAL_FORMAT_CODES = {
    SHEET_FORMAT_PLAIN: "General",
    SHEET_FORMAT_DATE: "yyyy\\-mm\\-dd",
    SHEET_FORMAT_DATETIME: "yyyy\\-mm\\-dd\\ hh:mm:ss",
    SHEET_FORMAT_TIME: "h:mm:ss",
    SHEET_FORMAT_ELAPSED: "[h]:mm:ss",
    SHEET_FORMAT_TEXT: "@",
}


def _sheet_format_codes() -> "tuple[str, ...]":
    """Every code a description may publish, in a fixed order."""
    out: "list[str]" = []
    for code in sorted(SHEET_BUILT_IN_FORMAT_IDS):
        out += [code]
    for kind in SHEET_FORMAT_KINDS:
        code = SHEET_CANONICAL_FORMAT_CODES[kind]
        if code not in SHEET_BUILT_IN_FORMAT_IDS:
            out += [code]
    return tuple(out)


SHEET_FORMAT_CODES = _sheet_format_codes()

# WHICH KIND EACH PUBLISHABLE CODE IS. The reader works this out by
# reading the code (`workbook.format_kind`), which is the one rule; this
# map is that rule's answer for the closed list of codes a description
# may publish, written out so the LOADER can ask the question without
# reaching the reader. The loader must not import a module that opens or
# parses a table -- doing so broke the profile/generator boundary in
# part 1 of this landing -- and every entry here was measured against
# `workbook.format_kind` rather than typed from memory.
SHEET_FORMAT_CODE_KINDS = {
    "General": SHEET_FORMAT_PLAIN,
    "0": SHEET_FORMAT_PLAIN,
    "0.00": SHEET_FORMAT_PLAIN,
    "#,##0": SHEET_FORMAT_PLAIN,
    "#,##0.00": SHEET_FORMAT_PLAIN,
    "0%": SHEET_FORMAT_PLAIN,
    "0.00%": SHEET_FORMAT_PLAIN,
    "0.00E+00": SHEET_FORMAT_PLAIN,
    "# ?/?": SHEET_FORMAT_PLAIN,
    "# ??/??": SHEET_FORMAT_PLAIN,
    "mm-dd-yy": SHEET_FORMAT_DATE,
    "d-mmm-yy": SHEET_FORMAT_DATE,
    "d-mmm": SHEET_FORMAT_DATE,
    "mmm-yy": SHEET_FORMAT_DATE,
    "h:mm AM/PM": SHEET_FORMAT_TIME,
    "h:mm:ss AM/PM": SHEET_FORMAT_TIME,
    "h:mm": SHEET_FORMAT_TIME,
    "h:mm:ss": SHEET_FORMAT_TIME,
    "m/d/yy h:mm": SHEET_FORMAT_DATETIME,
    "#,##0 ;(#,##0)": SHEET_FORMAT_PLAIN,
    "#,##0 ;[Red](#,##0)": SHEET_FORMAT_PLAIN,
    "#,##0.00;(#,##0.00)": SHEET_FORMAT_PLAIN,
    "#,##0.00;[Red](#,##0.00)": SHEET_FORMAT_PLAIN,
    "mm:ss": SHEET_FORMAT_TIME,
    "[h]:mm:ss": SHEET_FORMAT_ELAPSED,
    "mmss.0": SHEET_FORMAT_TIME,
    "##0.0E+0": SHEET_FORMAT_PLAIN,
    "@": SHEET_FORMAT_TEXT,
    # The two canonical codes that are not built in, named rather than
    # spelled again: their own spelling carries escapes and one copy of
    # it is enough.
    SHEET_CANONICAL_FORMAT_CODES[SHEET_FORMAT_DATE]: SHEET_FORMAT_DATE,
    SHEET_CANONICAL_FORMAT_CODES[SHEET_FORMAT_DATETIME]: (
        SHEET_FORMAT_DATETIME
    ),
}



# A CODE WRITTEN AS THE SOURCE WROTE IT (plan P4-D189). Plan P4-D79
# published a custom code as the canonical code of its kind, on the
# ground that a custom code is text out of somebody's file -- and the
# twin then rewrote `00000` as `General` (a region code shown `00802`
# came back `802`) and `yyyy-mm-dd hh:mm` as the canonical spelling.
# That ground holds for a code carrying a quoted word, a currency or a
# locale; it does not hold for a code built only out of the number-format
# language's own tokens, which spells how a number is shown and nothing
# anybody typed about a person. Such a code is published and written as
# the source wrote it. Every other custom code still gives way to the
# canonical code of its kind.
SHEET_CODE_LENGTH = 64

# The characters a code may hold standing alone: the figure placeholders,
# the point, the comma, the percent, the fraction bar, the clock's colon,
# the brackets, dash, plus, dollar and space Excel shows as they are,
# the text placeholder and the section mark.
_CODE_BARE = "0#?.,%/:()-+$ @;"

# The date and clock letters, in either case.
_CODE_LETTERS = "ymdhsYMDHS"

# The colours a section may open with, folded, and the numbered form.
_CODE_COLOURS_FOLDED = (
    "black",
    "blue",
    "cyan",
    "green",
    "magenta",
    "red",
    "white",
    "yellow",
)


def _code_bracket_speaks(inside: str) -> bool:
    """Whether a bracket of a code holds a token of the language alone.

    An elapsed count (`h`, `mm`, `ss` repeated), a colour by name or
    `Color` and a number from one to fifty-six. A condition (`>=100`), a
    currency or a locale (`$USD-409`) is not: they hold figures and words
    a person chose.
    """
    if not inside:
        return False
    first = inside[0]
    if first in ("h", "H", "m", "M", "s", "S"):
        for character in inside:
            if character != first:
                return False
        return True
    folded = ""
    for character in inside:
        if "A" <= character <= "Z":
            folded = folded + chr(ord(character) + 32)
        else:
            folded = folded + character
    if folded in _CODE_COLOURS_FOLDED:
        return True
    if folded[:5] != "color" or not 1 <= len(folded) - 5 <= 2:
        return False
    figures = folded[5:]
    for character in figures:
        if not "0" <= character <= "9":
            return False
    if figures[0] == "0":
        return False
    number = 0
    for character in figures:
        number = number * 10 + (ord(character) - 48)
    return 1 <= number <= 56


def sheet_format_code_speakable(code: str) -> bool:
    """Whether a number format code holds the format language's tokens alone.

    Guarantees: a fixed function of the code; raises TypeError on a
    value that is not text. True where the code is at most
    `SHEET_CODE_LENGTH` characters, of at most four sections, and every
    character is one of these: a character of `_CODE_BARE`; a date or
    clock letter; `E` or `e` followed by a sign; `AM/PM`, `am/pm`, `A/P`
    or `a/p`; a backslash, underscore or asterisk followed by a character
    that is neither a letter nor a figure; a quoted run holding no letter
    and no figure; or a bracket `_code_bracket_speaks` accepts. A figure
    other than `0` is refused, and so is every other letter: such a
    character is a word or a number somebody wrote into the code.
    """
    if not isinstance(code, str):
        raise TypeError("internal check: a format code was not text")
    if not code or len(code) > SHEET_CODE_LENGTH:
        return False
    sections = 1
    index = 0
    size = len(code)
    while index < size:
        character = code[index]
        if character in ("\\", "_", "*"):
            if index + 1 >= size or _is_letter_or_digit(code[index + 1]):
                return False
            index = index + 2
            continue
        if character == '"':
            index = index + 1
            while index < size and code[index] != '"':
                if _is_letter_or_digit(code[index]):
                    return False
                index = index + 1
            if index >= size:
                return False
            index = index + 1
            continue
        if character == "[":
            inside = ""
            index = index + 1
            while index < size and code[index] != "]":
                inside = inside + code[index]
                index = index + 1
            if index >= size or not _code_bracket_speaks(inside):
                return False
            index = index + 1
            continue
        if code[index : index + 5] in ("AM/PM", "am/pm"):
            index = index + 5
            continue
        if code[index : index + 3] in ("A/P", "a/p"):
            index = index + 3
            continue
        if character in ("E", "e"):
            if index + 1 >= size or code[index + 1] not in ("+", "-"):
                return False
            index = index + 2
            continue
        if character in _CODE_LETTERS:
            index = index + 1
            continue
        if character in _CODE_BARE:
            if character == ";":
                sections = sections + 1
                if sections > 4:
                    return False
            index = index + 1
            continue
        return False
    return True


def sheet_format_code_publishable(code: str) -> bool:
    """Whether a description may publish this code (plans P4-D79, P4-D189).

    One of `SHEET_FORMAT_CODES` -- Excel's built-in vocabulary and the
    canonical code of each kind -- or a code of the format language's
    own tokens alone (`sheet_format_code_speakable`). The producer, the
    publication guard and the loader all ask this one question.
    """
    if not isinstance(code, str):
        raise TypeError("internal check: a format code was not text")
    return code in SHEET_FORMAT_CODES or sheet_format_code_speakable(code)


def _is_elapsed_token(inside: str) -> bool:
    """Whether a bracket's text is an elapsed count: `h`, `mm`, `ss`...

    One letter of hours, minutes or seconds, repeated, in either case.
    """
    if not inside:
        return False
    first = inside[0]
    if first not in ("h", "H", "m", "M", "s", "S"):
        return False
    for character in inside:
        if character != first:
            return False
    return True


def _format_body(code: str) -> "tuple[str, bool]":
    """One format code's first section, outside its quotes and brackets.

    THE ONE SCAN, read by `sheet_format_kind` for the kind and by
    `sheet_format_figures` for the figures after the second (plan
    P4-D259). A format may spell positives, negatives and zeros
    differently and only the first section is a positive number's; what
    a bracket holds is not a date token except an elapsed count; the
    character after `\\`, `_` and `*` is layout and skipped.

    Guarantees: accepts a format code; returns its readable characters
    and whether it names an elapsed count. Determinism: a fixed function
    of the code. Raises TypeError if handed anything that is not a string
    instance. No I/O of any kind.
    """
    if not isinstance(code, str):
        raise TypeError("internal check: a format code was not text")
    body = code.split(";")[0]
    plain = ""
    quoted = False
    skip = False
    bracket = ""
    in_bracket = False
    elapsed = False
    for character in body:
        if skip:
            skip = False
            continue
        if in_bracket:
            if character == "]":
                in_bracket = False
                if _is_elapsed_token(bracket):
                    elapsed = True
                continue
            bracket = bracket + character
            continue
        if character == "\\" or character == "_" or character == "*":
            skip = True
            continue
        if character == '"':
            quoted = not quoted
            continue
        if quoted:
            continue
        if character == "[":
            in_bracket = True
            bracket = ""
            continue
        plain = plain + character
    return (plain, elapsed)


def sheet_format_figures(code: str) -> int:
    """How many figures after the second a date format shows (P4-D259).

    THE PRECISION EVIDENCE A SERIAL DOES NOT CARRY (the extra review of
    c5d09d5, item 9). A workbook stores a moment as a day count and its
    fraction, so a moment standing at a whole second stores exactly what
    a moment with no subsecond figures stores; what tells them apart is
    the FORMAT, which is where the figures are written and what every
    reader shows a person. Measured: 240 serials formatted
    `yyyy-mm-dd hh:mm:ss.000` published `subsecond` and three figures,
    and their twin -- written back with the same format code, its
    thousandths nought -- was read as whole seconds, so it missed both
    obligations though its cells were right.

    Guarantees: accepts a format code; returns 0 to 3 -- the figures
    after the point following the seconds token, capped at the
    millisecond a workbook's own arithmetic keeps. Determinism: a fixed
    function of the code. Raises TypeError if handed anything that is
    not a string instance. No I/O of any kind.
    """
    if not isinstance(code, str):
        raise TypeError("internal check: a format code was not text")
    plain = _format_body(code)[0]
    place = 0
    found = -1
    for character in plain:
        if character == "s" or character == "S":
            found = place
        place = place + 1
    if found < 0:
        return 0
    rest = plain[found + 1 :]
    while rest[0:1] == "s" or rest[0:1] == "S":
        rest = rest[1:]
    if rest[0:1] != ".":
        return 0
    figures = 0
    for character in rest[1:]:
        if character != "0":
            break
        figures = figures + 1
        if figures == 3:
            break
    return figures


def sheet_format_kind(code: str) -> str:
    """Which kind of thing a number wearing this format code is.

    THE ONE RULE, IN THE MODULE EVERY SIDE MAY IMPORT (plan P4-D189). It
    was the reader's (`workbook.format_kind`), and the loader and the
    writer answered the same question from `SHEET_FORMAT_CODE_KINDS`, a
    closed map of its answers; a code published as the source wrote it
    is not in that map, so the rule itself moved here and the reader
    asks it.

    Guarantees: a fixed function of the code. The rule is the one every
    reader the study measured uses -- the format decides the type -- and
    it reads the code outside its quoted runs, so a currency symbol
    spelling `"d"` inside quotation marks never makes a column of money
    into a column of dates. Only the first section is read: a format may
    spell positives, negatives and zeros differently, and the first
    section is the one a positive number wears. What a bracket holds is
    not read as a date token (plan P4-D169) -- a colour, a currency and
    locale, a condition -- except an elapsed count, `[h]`, `[mm]`,
    `[ss]`; the character after `_` and after `*` is layout and skipped.
    """
    if not isinstance(code, str):
        raise TypeError("internal check: a format code was not text")
    if code == "General" or not code:
        return SHEET_FORMAT_PLAIN
    if code == "@":
        return SHEET_FORMAT_TEXT
    read = _format_body(code)
    plain = read[0]
    elapsed = read[1]
    day = "d" in plain or "D" in plain or "y" in plain or "Y" in plain
    # `m` is minutes next to an hour or a second, and months otherwise.
    month = "m" in plain or "M" in plain
    clock = "h" in plain or "H" in plain or "s" in plain or "S" in plain
    if elapsed:
        return SHEET_FORMAT_ELAPSED
    if day and clock:
        return SHEET_FORMAT_DATETIME
    if day or (month and not clock):
        return SHEET_FORMAT_DATE
    if clock:
        return SHEET_FORMAT_TIME
    return SHEET_FORMAT_PLAIN

# -- a date IN a workbook: a number wearing a format, read as a date ---
#
# WHY A DATE CELL IS READ AS ITS DATE (repair of the stage-2b
# integration). A workbook stores a date as the count of days since its
# epoch, with the time of day as the fraction, and a DATE FORMAT on the
# cell is what makes every reader hand it back as a date. The reader
# used to pass the count on as a number, and the column machinery then
# described a date column as a column of numbers: a `dd.mm.yyyy` column
# became role `count` with percentiles 44937 to 45579, a column of
# moments became `continuous`, and its twin -- drawn as continuous
# numbers -- lost moments at midnight: 1394 cells in the source,
# 1284 in the twin, where stage 2 promises a date stored at midnight
# stays at midnight. So a number cell whose format kind is `date` or
# `datetime` is read as the date it stands for, in one ISO spelling,
# and the twin writes that date back as the day count it came from,
# wearing a date format. A `time` or `elapsed` cell is a length of time
# and not a day, and stays a number.

SHEET_DAY_MILLISECONDS = 86_400_000
# The last day a workbook can show, 9999-12-31, as a 1900-system count.
SHEET_LAST_SERIAL = 2_958_465


def _days_from_civil(year: int, month: int, day: int) -> int:
    """Days from 1970-01-01 to one proleptic Gregorian date (exact)."""
    shifted = year - 1 if month <= 2 else year
    era = shifted // 400
    of_era = shifted - era * 400
    march = month - 3 if month > 2 else month + 9
    of_year = (153 * march + 2) // 5 + day - 1
    of_cycle = of_era * 365 + of_era // 4 - of_era // 100 + of_year
    return era * 146097 + of_cycle - 719468


def _civil_from_days(count: int) -> "tuple[int, int, int]":
    """The proleptic Gregorian date ``count`` days after 1970-01-01 (exact)."""
    shifted = count + 719468
    era = shifted // 146097
    of_era = shifted - era * 146097
    of_cycle = (
        of_era - of_era // 1460 + of_era // 36524 - of_era // 146096
    ) // 365
    year = of_cycle + era * 400
    of_year = of_era - (365 * of_cycle + of_cycle // 4 - of_cycle // 100)
    march = (5 * of_year + 2) // 153
    day = of_year - (153 * march + 2) // 5 + 1
    month = march + 3 if march < 10 else march - 9
    if month <= 2:
        year = year + 1
    return (year, month, day)


_EPOCH_1900 = _days_from_civil(1899, 12, 30)
_EPOCH_1900_EARLY = _days_from_civil(1899, 12, 31)
_EPOCH_1904 = _days_from_civil(1904, 1, 1)


def _plain_serial(text: str) -> bool:
    """Whether the text is a stored day count: figures, one optional point."""
    if not isinstance(text, str):
        raise TypeError("internal check: a cell's text was not text")
    point = text.find(".")
    if point < 0:
        return _figures_only(text)
    return _figures_only(text[:point]) and (
        point == len(text) - 1 or _figures_only(text[point + 1 :])
    )


def sheet_serial_moment(
    text: str, kind: str, epoch_1904: bool, figures: int = 0
) -> str:
    """A stored day count wearing a date format, read as the date it shows.

    ``figures`` is what the cell's FORMAT shows after the second
    (`sheet_format_figures`), and the fraction is written to that many
    places even where it is nought (plan P4-D259): a serial standing at
    a whole second under `hh:mm:ss.000` is a moment a person reads as
    `12:00:00.000`, and dropping the figures lost the only evidence of
    the column's precision the workbook holds.

    Guarantees: a fixed function of its four inputs. Where ``kind`` is
    `date` or `datetime` and the text is a day count a workbook can show
    as a date, the answer is `YYYY-MM-DD` for a `date` cell holding a
    whole day, and `YYYY-MM-DD HH:MM:SS` otherwise, with the fraction
    added to ``figures`` places, or to three where the time is not a
    whole second and the format shows none; the time is rounded to the
    millisecond, which is finer than any format a workbook can wear.
    Anything else comes back unchanged: another kind, a negative or
    exponent spelling, a count before the epoch's first day, the 1900
    system's day 60 (a 29 February 1900 that never was), and a count
    past 9999-12-31.
    """
    if not isinstance(text, str) or not isinstance(kind, str):
        raise TypeError("internal check: a cell's text or kind was not text")
    if kind not in (SHEET_FORMAT_DATE, SHEET_FORMAT_DATETIME):
        return text
    if not _plain_serial(text):
        return text
    value = float(text)
    first = 0.0 if epoch_1904 else 1.0
    if value < first or value > SHEET_LAST_SERIAL:
        return text
    moment = round(value * SHEET_DAY_MILLISECONDS)
    days = moment // SHEET_DAY_MILLISECONDS
    part = moment - days * SHEET_DAY_MILLISECONDS
    if epoch_1904:
        count = _EPOCH_1904 + days
    elif days == 60:
        return text
    elif days < 60:
        count = _EPOCH_1900_EARLY + days
    else:
        count = _EPOCH_1900 + days
    year, month, day = _civil_from_days(count)
    if year > 9999:
        return text
    written = f"{year:04d}-{month:02d}-{day:02d}"
    if kind == SHEET_FORMAT_DATE and part == 0:
        return written
    seconds = part // 1000
    written = (
        f"{written} {seconds // 3600:02d}:{(seconds // 60) % 60:02d}"
        f":{seconds % 60:02d}"
    )
    thousandths = f"{part % 1000:03d}"
    if figures > 0:
        written = f"{written}.{thousandths[0:figures]}"
    elif part % 1000:
        written = f"{written}.{thousandths}"
    return written


def sheet_moment_kind(text: str) -> str:
    """Which date format kind the reader's own spelling of a date is, or "".

    `date` for `YYYY-MM-DD`, `datetime` for `YYYY-MM-DD HH:MM:SS` with an
    optional fraction of one to three figures -- exactly the spellings
    `sheet_serial_moment` writes, and nothing else. One and two figures
    since plan P4-D259, which made the reader write as many figures as
    the cell's format shows.
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a cell's text was not text")
    if len(text) < 10 or text[4:5] != "-" or text[7:8] != "-":
        return ""
    if not (
        _figures_only(text[0:4])
        and _figures_only(text[5:7])
        and _figures_only(text[8:10])
    ):
        return ""
    if len(text) == 10:
        return SHEET_FORMAT_DATE
    if len(text) < 19 or len(text) > 23 or text[10:11] != " ":
        return ""
    if len(text) == 20:
        return ""
    if text[13:14] != ":" or text[16:17] != ":":
        return ""
    if not (
        _figures_only(text[11:13])
        and _figures_only(text[14:16])
        and _figures_only(text[17:19])
    ):
        return ""
    if len(text) > 19 and (
        text[19:20] != "." or not _figures_only(text[20:])
    ):
        return ""
    return SHEET_FORMAT_DATETIME


def sheet_moment_serial(text: str, epoch_1904: bool) -> str:
    """The day count a workbook stores for the reader's spelling of a date.

    Guarantees: the inverse of `sheet_serial_moment` on every text that
    function writes, so a twin cell written from it is read back as the
    same text. "" where the text is not one of those two spellings or
    names no day the workbook's date system can store. A whole day is
    spelled in figures; a moment as the shortest spelling of its double.
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a cell's text was not text")
    kind = sheet_moment_kind(text)
    if not kind:
        return ""
    year = int(text[0:4])
    month = int(text[5:7])
    day = int(text[8:10])
    if month < 1 or month > 12 or day < 1 or day > 31:
        return ""
    count = _days_from_civil(year, month, day)
    if _civil_from_days(count) != (year, month, day):
        return ""
    part = 0
    if kind == SHEET_FORMAT_DATETIME:
        hours = int(text[11:13])
        minutes = int(text[14:16])
        seconds = int(text[17:19])
        if hours > 23 or minutes > 59 or seconds > 59:
            return ""
        part = (hours * 3600 + minutes * 60 + seconds) * 1000
        if len(text) > 19:
            # ONE TO THREE FIGURES, padded to the thousandth a workbook
            # stores (plan P4-D259): `.5` is five hundred milliseconds.
            part = part + int(f"{text[20:]:0<3s}"[0:3])
    if epoch_1904:
        days = count - _EPOCH_1904
        if days < 0:
            return ""
    else:
        days = count - _EPOCH_1900
        if days <= 60:
            days = count - _EPOCH_1900_EARLY
            if days < 1 or days >= 60:
                return ""
    if days > SHEET_LAST_SERIAL:
        return ""
    if part == 0:
        return f"{days}"
    return repr(days + part / SHEET_DAY_MILLISECONDS)


# -- a sheet's NAME, and when it may be published ----------------------
#
# A sheet name is free text somebody typed, and the disclosure rule
# names it outright as a fact that can hold a person's name. It is also
# the one piece of a workbook's shape a reader meets first: code that
# says `read_excel(path, sheet_name="Data")` fails against a twin whose
# sheet is called something else, so withholding every name would break
# the first goal to protect the third.
#
# Both are held by publishing a name ONLY when it is one synthtwin can
# rebuild from its own vocabulary -- a generic name of the kind an
# exporter writes, optionally numbered -- and withholding every other,
# which the twin then writes under a neutral name. That is the same
# standard the publication guard already applies to every other
# published word: not "does this look like a person's name", which
# nothing can answer, but "is this one of the words we know".
SHEET_SAFE_NAMES = (
    "Codebook",
    "Data",
    "Export",
    "Info",
    "Notes",
    "Page",
    "Raw",
    "Report",
    "Results",
    "Sheet",
    "Summary",
    "Table",
    "Values",
    "Worksheet",
)

# The same names folded, written out as literals. The comparison below
# needs a folded form of each, and folding them in a loop would call a
# text method on a value the offline audit cannot trace to a literal.
SHEET_SAFE_NAMES_FOLDED = (
    "codebook",
    "data",
    "export",
    "info",
    "notes",
    "page",
    "raw",
    "report",
    "results",
    "sheet",
    "summary",
    "table",
    "values",
    "worksheet",
)

SHEET_NEUTRAL_NAME = "Sheet"

# WHAT A SHEET THAT IS NOT THE TABLE'S IS WRITTEN WITH (plan P4-D82).
#
# A workbook's other sheets used to be written EMPTY, and a reader then
# saw a different workbook: measured with pandas, a sheet holding one
# text cell reads back as one column and no rows on the real file and as
# nothing whatever on a twin whose sheet is bare -- (0, 1) against
# (0, 0). Writing the person's own text back is what the disclosure rule
# forbids, and writing cells that hold the EMPTY STRING changes nothing,
# because every reader folds an empty-string cell into a missing value
# and trims the frame away again (measured: still (0, 0)).
#
# So such a sheet is written with as many cells as it held, each holding
# one word of synthtwin's own -- the same answer the withheld preamble
# line takes. A reader then meets a sheet of the same shape, carrying no
# character of anybody's table.
SHEET_WITHHELD_CELL = "withheld"


# HOW MANY FIGURES A PUBLISHED SHEET NAME MAY END IN (plan P4-D171). The
# first writing allowed any number, stripped them for the test and then
# published the name whole, so a sheet called `Report123456789` -- a
# subject's own number -- reached a description at a floor of five and
# the loader passed it. Two figures, not beginning with a nought, is
# what the numbered sheets an application writes (`Sheet1` to `Sheet99`)
# need, and no identifier of a person fits in it.
SHEET_NAME_FIGURES = 2


def sheet_name_published(name: str) -> "str | None":
    """The sheet's name where it may be published, else nothing.

    A name may be published when it is one of `SHEET_SAFE_NAMES`,
    alone or followed by one or two figures that do not begin with a
    nought ("Data", "Sheet1", "Table12"); a longer run of figures is a
    number somebody typed and is withheld. The comparison ignores the
    case the person typed but the name is published AS TYPED, because a
    reader naming the sheet has to spell it the way the file does.
    """
    if not isinstance(name, str):
        raise TypeError("internal check: a sheet name was not text")
    if not name:
        return None
    figures = 0
    for index in range(len(name)):
        place = ord(name[len(name) - 1 - index])
        if 48 <= place <= 57:
            figures = figures + 1
            continue
        break
    if figures > SHEET_NAME_FIGURES:
        return None
    if figures and name[len(name) - figures] == "0":
        return None
    stem = name[: len(name) - figures]
    if stem.casefold() in SHEET_SAFE_NAMES_FOLDED:
        return name
    return None


def sheet_name_key(name: str) -> str:
    """The key two sheet names collide under: a spreadsheet ignores case.

    `Sheet1` and `sheet1` cannot stand in one workbook -- an application
    renames the second -- so every claim on a name is made under this
    key (plan P4-D171).
    """
    if not isinstance(name, str):
        raise TypeError("internal check: a sheet name was not text")
    return name.casefold()


def neutral_sheet_name(position: int) -> str:
    """The name a sheet is written under when its own is withheld."""
    return SHEET_NEUTRAL_NAME + f"{position}"


def twin_sheet_names(published: "tuple[str | None, ...]") -> "tuple[str, ...]":
    """The name the twin writes each sheet under, from the published list.

    ONE FUNCTION, TWO CALLERS, AND THAT IS THE WHOLE POINT (repair of
    landing 2b.10). The writer needs a name for every sheet, including
    the ones whose own name was withheld; the validator needs to know
    what name a conforming twin would carry there, or it reports a twin
    MISSED for writing exactly the neutral name the disclosure rule
    told it to write. Both ask here, so neither can drift from the
    other.

    A PUBLISHED NAME IS CLAIMED FIRST, which is the defect this rule was
    measured into. The first writing handed out neutral names in sheet
    order and appended an underscore on a collision, so a workbook
    whose first sheet was withheld and whose second was called `Sheet1`
    wrote `Sheet1` and `Sheet1_` -- renaming the sheet whose name the
    description PUBLISHES, and failing the published fact. Here the
    published names are taken before a single placeholder is allocated,
    and a placeholder walks up until it finds a number no published
    name has taken.

    AND A NAME IS TAKEN WHATEVER ITS CASE (plan P4-D171). The published
    names `[null, "sheet1"]` used to allocate `Sheet1` beside `sheet1`,
    which a spreadsheet cannot hold: openpyxl renamed the published sheet
    `sheet11`, and the validator, asking the same rule, missed nothing.
    Every claim is made under `sheet_name_key`.
    """
    taken: "dict[str, bool]" = {}
    for name in published:
        if name is not None:
            taken[sheet_name_key(name)] = True
    out: "list[str]" = []
    for index in range(len(published)):
        published_here = published[index]
        if published_here is not None:
            out += [published_here]
            continue
        number = index + 1
        neutral = neutral_sheet_name(number)
        while sheet_name_key(neutral) in taken:
            number = number + 1
            neutral = neutral_sheet_name(number)
        taken[sheet_name_key(neutral)] = True
        out += [neutral]
    return tuple(out)


MAXIMUM_ENDING_RUNS = 64
MAXIMUM_BLANK_PLACES = 64
MAXIMUM_PREAMBLE_LINES = 16

# The row sequence a column can be: 0, 1, 2, ... (pandas) or 1, 2, 3,
# ... (R, REDCap).
SEQUENCE_STARTS = (0, 1)

# The names a written row index carries, and the ONLY column that may be
# published as the row sequence (plan P4-D76, invariant FD12). A pandas
# frame written with its index leaves the first header cell blank and
# the reader names it `Unnamed: 0`; R's `write.csv` writes `""` and is
# named the same; a frame written, read and written again carries
# `Unnamed: 0` in the file itself. A column of its OWN name holding
# 1, 2, 3, ... -- a REDCap `record_id`, a register's serial -- is not one
# of these: it is the table's own data, and a sequence published of it
# is the generator's instruction to write those very values back.
INDEX_NAMES = ("Unnamed: 0", "rownames")

# What a withheld preamble line is written as, after the punctuation it
# began with (`# ` stays, so `comment="#"` still finds it). Two words, so
# the stand-in reads as a title line to the survey that reads the twin:
# a one-field line holding no space is a one-column table's name.
WITHHELD_LINE = "withheld line"

# WHAT A LINE BEFORE THE TABLE PUBLISHES, AND WHAT IT NEVER PUBLISHES
# (plan P4-D80; review item CODEX-3). Its TEXT is not published at any
# smallest group, this version's floor of one included. Such a line is
# free text somebody wrote above their table -- "Extract for unit 7",
# "# exported for Dr Vance" -- and the owner's ruling is that the
# description reveals nothing about any individual. The floor is no
# defence here and never was: a floor governs how many rows share a
# value, and one line of prose is not a group of rows at all, so at a
# floor of one the text went into the description and into the twin
# whole (measured: CODEX-3).
#
# What IS published is that such lines exist, how many there are, and
# what SHAPE each has: whether it is blank, whether it began with a
# comment mark, and what that mark was. Every one of those is a fact
# about the tool that wrote the file and about nobody who appears in
# it. The twin writes a neutral line of the same shape in its place, so
# a reader that skips a title line, and code that passes `comment="#"`,
# skip exactly as many lines in the twin as in the table.
PREAMBLE_BLANK = "blank"
PREAMBLE_COMMENT = "comment"
PREAMBLE_TEXT = "text"
PREAMBLE_KINDS = (PREAMBLE_BLANK, PREAMBLE_COMMENT, PREAMBLE_TEXT)

# The mark of a survey export's second metadata row (Qualtrics).
_IMPORT_MARK = '{"ImportId":'

_QUOTE = '"'
_BACKSLASH = "\\"
_MARK = "\ufeff"
_END_OF_FILE = "\x1a"
_SPACE = " "
_TAB = "\t"
_CR = "\r"
_LF = "\n"
_BYTE_ONE = b"\x01"
_BYTE_ZERO = b"\x00"
_SAMPLE_RECORDS = 400


# -- the published form ------------------------------------------------


@dataclasses.dataclass(frozen=True)
class EndingRun:
    """So many consecutive lines ending the same way, in file order."""

    ending: str
    lines: int


@dataclasses.dataclass(frozen=True)
class BlankPlace:
    """Blank lines standing after ``after`` data records.

    ``text`` is what each of them holds: nothing, or only spaces and tabs.
    """

    after: int
    lines: int
    text: str


def endings_disclosed(
    runs: "list[EndingRun]", floor: int, withheld_lines: int = 0
) -> "list[EndingRun]":
    """A file's line-ending runs, with no ending naming a group too small.

    THE DISCLOSURE RULE, ASKED OF A FILE'S OWN LINES (plan P4-D290, the
    repair of the extra review round of 2026-09-18). A run says how many
    consecutive lines ended one way, so the runs TOGETHER say exactly
    where each ending changed -- and where one ending was written by
    fewer lines than the line, those runs point at the records that
    carry it. **Measured** at a floor of eleven, on a header and 120
    records `R001,1` through `R120,120` with `record` declared an
    identifier: changing only record 57's ending to CRLF published
    `[{lf: 57}, {crlf: 1}, {lf: 63}]`, which is that record's exact
    position, and the description loaded.

    WHERE AN ENDING IS BELOW THE LINE THE WHOLE FILE IS PUBLISHED AS THE
    COMMONEST ONE, which is ruling 6 of 2026-09-17 applied to a file's
    own spelling: the description is the description of the file with its
    rare endings written the way most of its lines were, the twin writes
    that ending throughout, and describing the file again says the same
    thing, so the file passes its own description. Ties for the
    commonest go to the first ending in sorted order.

    AND A RUN BELOW THE LINE COUNTS THE SAME WAY, WHATEVER ITS ENDING'S
    TOTAL COMES TO (the repair pass of 2026-09-18). The first writing of
    this rule read each ENDING'S total over the whole file, so an ending
    with companions somewhere else never tripped it and its lone run
    stood. **Measured** at a floor of eleven, on the same header and 120
    records: giving lines 0 to 20 CRLF endings AND record 57 a CRLF
    ending, with every other line LF, published `[{crlf: 21}, {lf: 36},
    {crlf: 1}, {lf: 63}]` -- record 57's exact position again, from an
    ending whose total is 22. A run says how many CONSECUTIVE lines
    ended one way, so a published run shorter than the line points at
    the records that carry it whatever else the file holds; the runs are
    read here as well as the totals, and the file then collapses to one
    run of the commonest ending exactly as above.

    AND THE BLANK LINES THIS FILE DOES NOT PUBLISH LEAVE THE COUNT WITH
    THEM. `blank_places_disclosed` below withholds the places of a
    handful of blank lines, and invariant FD2 has the endings account for
    every line the file holds, the blank ones included -- so a
    description that dropped one blank line and kept its 122 endings
    beside 121 lines was refused by its own loader. Where any line is
    withheld the runs collapse to one for the same reason they collapse
    around a rare ending: their positions are what says where the
    withheld line stood.

    AT THE DEFAULT FLOOR NOTHING MOVES (the repair pass of 2026-09-18).
    A floor of one is a run in which the person has asked synthtwin for
    no protection at all, and at that same floor the column censuses
    beside this one publish a level covering ONE row -- so holding a
    file's own form to a stricter standard than the product holds its
    own column contents to, on the path where nothing was asked, took a
    file's lone blank line, its lone empty record and its trailing blank
    line out of the twin for nothing. **Measured** at the default floor,
    on a header and 120 records: a single blank line after record 57, a
    single bare-comma record and a single trailing blank line were all
    kept before this rule was written, all three were dropped after it,
    and the very same run published the level `("south", 1)` on a column
    of 239 `NORTH` and one `SOUTH`. So this rule is gated on a RAISED
    floor, exactly as `taxonomy._absorb_lone_spellings` is, and the
    floor's own value and unit stay the owner's deferred question.

    Guarantees: accepts the runs in file order, the settings floor and
    how many lines are withheld from the published form; returns those
    runs at a floor of one, and otherwise those runs where every
    ending's total AND every run's own length reach the line and no line
    is withheld, or a single run of the commonest ending over every line
    the description keeps. Determinism: a fixed function of the three.
    Raises nothing. No I/O of any kind.
    """
    if floor <= 1:
        return list(runs)
    line = parsing.census_floor(floor)
    totals: "dict[str, int]" = {}
    for run in runs:
        counted = totals[run.ending] if run.ending in totals else 0
        totals[run.ending] = counted + run.lines
    rare = False
    commonest = ""
    lines = 0
    for ending in sorted(totals):
        lines = lines + totals[ending]
        if totals[ending] < line:
            rare = True
        if not commonest or totals[ending] > totals[commonest]:
            commonest = ending
    # A RUN below the line is an exceptional position whatever its
    # ending's total over the file comes to (the repair pass of
    # 2026-09-18). See the paragraph above.
    for run in runs:
        if run.lines < line:
            rare = True
    if not commonest:
        return list(runs)
    if not rare and not withheld_lines:
        return list(runs)
    return [EndingRun(ending=commonest, lines=lines - withheld_lines)]


def blank_places_disclosed(
    places: "list[BlankPlace]", floor: int
) -> "list[BlankPlace]":
    """A file's blank-line places, where they are too many to name a record.

    THE DISCLOSURE RULE, ASKED OF A POSITION RATHER THAN OF A COUNT
    (plan P4-D290). A blank place says how many blank lines stood AFTER
    so many records, so a handful of them are a handful of record
    positions -- and a file with one is a file pointing at one record.
    **Measured** at a floor of eleven, on a header and 120 records with
    `record` declared an identifier: a single blank line after record 57
    published `{after: 57, lines: 1}`, and the description loaded. The
    coarse form beside it is no help, because `blank_lines_spread` names
    the first and the last place, which for one place is that place.

    So the places are published only where there are at least as many of
    them as the line, and a file with fewer is described as having none.
    The twin then writes none, and describing the file again reads it the
    same way, so the file passes its own description. What it costs is
    those blank lines in the twin, which is the price of not naming the
    records they stand beside.

    AT THE DEFAULT FLOOR NOTHING MOVES (the repair pass of 2026-09-18).
    A floor of one is a run in which the person has asked synthtwin for
    no protection at all, and at that same floor the column censuses
    beside this one publish a level covering ONE row -- so holding a
    file's own form to a stricter standard than the product holds its
    own column contents to, on the path where nothing was asked, took a
    file's lone blank line, its lone empty record and its trailing blank
    line out of the twin for nothing. **Measured** at the default floor,
    on a header and 120 records: a single blank line after record 57, a
    single bare-comma record and a single trailing blank line were all
    kept before this rule was written, all three were dropped after it,
    and the very same run published the level `("south", 1)` on a column
    of 239 `NORTH` and one `SOUTH`. So this rule is gated on a RAISED
    floor, exactly as `taxonomy._absorb_lone_spellings` is, and the
    floor's own value and unit stay the owner's deferred question.

    Guarantees: accepts the places in file order and the settings floor;
    returns those places at a floor of one or where they reach the line,
    and none at all otherwise. Determinism: a fixed function of the two.
    Raises nothing. No I/O of any kind.
    """
    if floor <= 1:
        return list(places)
    if len(places) >= parsing.census_floor(floor):
        return list(places)
    return []


def blank_lines_withheld(places: "list[BlankPlace]", floor: int) -> int:
    """How many blank lines `blank_places_disclosed` holds back (P4-D290).

    Asked of that rule itself, so the two can never part: nought where
    the places are published, and every one of their lines where they
    are not. `endings_disclosed` takes it off the line count it
    publishes, because invariant FD2 has the endings account for every
    line the description keeps.

    Guarantees: accepts the places in file order and the settings floor;
    returns nought or the lines those places hold. Determinism: a fixed
    function of the two. Raises nothing. No I/O of any kind.
    """
    if blank_places_disclosed(places, floor):
        return 0
    lines = 0
    for place in places:
        lines = lines + place.lines
    return lines


def row_count_disclosed(count: int, floor: int) -> int:
    """One count of a file's empty rows, as the disclosure rule allows.

    THE DISCLOSURE RULE, ASKED OF THE THREE EMPTY-ROW COUNTS (plan
    P4-D290). An empty row is a record of the table written with no
    value in any column, and its count is a count of records like any
    other. **Measured** at a floor of eleven, on a header and 120
    records with `record` declared an identifier: replacing record 57
    with a bare comma published `empty_rows.interior 1`, a count of one
    record, and the description loaded.

    A count below the line is published as NOUGHT -- the file described
    as though those rows held values, which is ruling 4 of 2026-09-17
    counting a group below a raised floor as absent. The twin writes no
    empty row there and the file described again says nought too, so the
    file passes its own description.

    AT THE DEFAULT FLOOR NOTHING MOVES (the repair pass of 2026-09-18).
    A floor of one is a run in which the person has asked synthtwin for
    no protection at all, and at that same floor the column censuses
    beside this one publish a level covering ONE row -- so holding a
    file's own form to a stricter standard than the product holds its
    own column contents to, on the path where nothing was asked, took a
    file's lone blank line, its lone empty record and its trailing blank
    line out of the twin for nothing. **Measured** at the default floor,
    on a header and 120 records: a single blank line after record 57, a
    single bare-comma record and a single trailing blank line were all
    kept before this rule was written, all three were dropped after it,
    and the very same run published the level `("south", 1)` on a column
    of 239 `NORTH` and one `SOUTH`. So this rule is gated on a RAISED
    floor, exactly as `taxonomy._absorb_lone_spellings` is, and the
    floor's own value and unit stay the owner's deferred question.

    Guarantees: accepts a count of empty rows and the settings floor;
    returns that count at a floor of one or where it reaches the line,
    and nought otherwise. Determinism: a fixed function of the two.
    Raises nothing. No I/O of any kind.
    """
    if floor <= 1:
        return count
    if count >= parsing.census_floor(floor):
        return count
    return 0


@dataclasses.dataclass(frozen=True)
class BlankSpread:
    """Blank lines in more places than `MAXIMUM_BLANK_PLACES`, counted.

    ``lines`` blank lines in all, the first standing after ``first`` data
    records and the last after ``last``; ``text`` is what the most of
    them hold (nothing, or only spaces and tabs), the earlier text on a
    tie. The twin writes them `spread_places` apart.
    """

    first: int
    last: int
    lines: int
    text: str


@dataclasses.dataclass(frozen=True)
class PreambleRun:
    """So many consecutive lines before the table, all of one shape.

    ``kind`` is one of `PREAMBLE_KINDS`. ``mark`` is the punctuation a
    comment line began with (`# `, `*** `), or the spaces and tabs a
    blank line held; it is empty for a line of text.

    NO TEXT OF THE LINE STANDS HERE. `mark` is the run of characters
    before the line's first letter or digit, so it cannot carry a word;
    the publication guard refuses a `mark` holding a letter or a digit
    outright (`profile._PREAMBLE_MARK`), which is what makes that a
    control rather than a habit of the producer.

    NOR A CHARACTER THE TWIN COULD NOT WRITE (plan P4-D83). The mark
    also stops at a quote character and at the table's delimiter, so
    the line the twin writes for the run is one record of the file and
    the twin stays readable; `mark_breaks_a_line` is that rule, and
    contract FD11 is where a description is held to it.

    RUNS AND NOT LINES, which is review item CODEX-11: seventeen leading
    blank lines are seventeen lines of ONE shape. Published a line
    apiece they broke the cap of sixteen and the loader refused the
    producer's own description; published as one run of seventeen they
    are inside it, and the file the baseline read is still described.
    """

    kind: str
    lines: int
    mark: str


@dataclasses.dataclass(frozen=True)
class WrittenName:
    """A header cell written differently from the column's name.

    A blank or repeated header cell cannot be a column's name, so the
    column is named by `named_columns` and the text the file holds is
    kept here, to be written back.
    """

    position: int
    text: str


@dataclasses.dataclass(frozen=True)
class ColumnForm:
    """How one column's cells are written.

    ``quoting`` holds one rule per `CELL_CLASSES`, in that order.
    ``pad_side`` is "" for a column whose cells are not padded.
    ``sequence_start`` is -1 for a column that is not the row sequence.
    """

    quoting: "tuple[str, ...]"
    pad_side: str
    pad_width: int
    sequence_start: int


@dataclasses.dataclass(frozen=True)
class RowOrder:
    """The column the file is sorted by, or column 0 for none."""

    column: int
    direction: str
    collation: str


@dataclasses.dataclass(frozen=True)
class Dialect:
    """Everything about a table's bytes that is not a cell's value."""

    delimiter: str
    initial_space: bool
    escape: str
    separator_line: bool
    byte_order_mark: bool
    line_endings: "tuple[EndingRun, ...]"
    final_line_ending: bool
    end_of_file_mark: bool
    preamble: "tuple[PreambleRun, ...]"
    preamble_withheld: bool
    header_quoting: str
    header_rows: "tuple[tuple[str, ...], ...]"
    header_rows_quoting: str
    written_names: "tuple[WrittenName, ...]"
    header_trailing_delimiter: bool
    rows_trailing_delimiter: bool
    short_rows: bool
    blank_lines: "tuple[BlankPlace, ...]"
    empty_rows_leading: int
    empty_rows_interior: int
    empty_rows_trailing: int
    columns: "tuple[ColumnForm, ...]"
    row_order: RowOrder
    # Past their caps, in place of `line_endings` and `blank_lines`
    # (both then empty): how many lines end each way, in `ENDINGS` order,
    # and the blank lines counted.
    line_endings_spread: "tuple[EndingRun, ...]" = ()
    blank_lines_spread: "BlankSpread | None" = None


NO_ORDER = RowOrder(column=0, direction=ASCENDING, collation=COLLATION_TEXT)


def plain_column() -> ColumnForm:
    """A column written the ordinary way: quoted when needed, unpadded."""
    return ColumnForm(
        quoting=(QUOTE_NEEDED, QUOTE_NEEDED, QUOTE_NEEDED, QUOTE_NEEDED),
        pad_side="",
        pad_width=0,
        sequence_start=-1,
    )


def lines_of(form: Dialect, n_rows: int, headed: bool) -> int:
    """How many lines a file of this form holds, records and others.

    The line endings of a form account for every one of them (loader
    invariant D2), and `twin_text` writes exactly this many.
    """
    total = (
        n_rows
        + preamble_lines_total(form.preamble)
        + len(form.header_rows)
    )
    if form.separator_line:
        total = total + 1
    if headed:
        total = total + 1
    for place in form.blank_lines:
        total = total + place.lines
    if form.blank_lines_spread is not None:
        total = total + form.blank_lines_spread.lines
    return total


def ordinary(n_columns: int, n_rows: int, headed: bool) -> Dialect:
    """The form of an ordinary file: comma, UTF-8, line feeds, minimal quoting.

    It is the form every twin was written in before this module, and a
    description of such a file publishes exactly this.
    """
    total = n_rows + (1 if headed else 0)
    runs: "tuple[EndingRun, ...]" = ()
    if total:
        runs = (EndingRun(ending="lf", lines=total),)
    return Dialect(
        delimiter=",",
        initial_space=False,
        escape=ESCAPE_DOUBLED,
        separator_line=False,
        byte_order_mark=False,
        line_endings=runs,
        final_line_ending=total > 0,
        end_of_file_mark=False,
        preamble=(),
        preamble_withheld=False,
        header_quoting=QUOTE_NEEDED,
        header_rows=(),
        header_rows_quoting=QUOTE_NEEDED,
        written_names=(),
        header_trailing_delimiter=False,
        rows_trailing_delimiter=False,
        short_rows=False,
        blank_lines=(),
        empty_rows_leading=0,
        empty_rows_interior=0,
        empty_rows_trailing=0,
        columns=tuple([plain_column() for _place in range(n_columns)]),
        row_order=NO_ORDER,
    )


def document_of(form: Dialect) -> "dict[str, object]":
    """The form as the description publishes it under `source.dialect`.

    Every key is always present, so the loader can require exactly this
    key set (contract 4.3); absent optional facts are `null`.
    """
    runs: list[object] = []
    for run in form.line_endings:
        runs += [{"ending": run.ending, "lines": run.lines}]
    blanks: list[object] = []
    for place in form.blank_lines:
        blanks += [
            {"after": place.after, "lines": place.lines, "text": place.text}
        ]
    names: list[object] = []
    for written in form.written_names:
        names += [{"position": written.position, "text": written.text}]
    rows: list[object] = []
    for row in form.header_rows:
        rows += [list(row)]
    columns: list[object] = []
    for column in form.columns:
        quoting: dict[str, object] = {}
        for index in range(len(CELL_CLASSES)):
            quoting[CELL_CLASSES[index]] = column.quoting[index]
        pad: object = None
        if column.pad_side:
            pad = {"side": column.pad_side, "width": column.pad_width}
        sequence: object = None
        if column.sequence_start >= 0:
            sequence = column.sequence_start
        columns += [
            {"pad": pad, "quoting": quoting, "sequence_start": sequence}
        ]
    order: object = None
    if form.row_order.column:
        order = {
            "collation": form.row_order.collation,
            "column": form.row_order.column,
            "direction": form.row_order.direction,
        }
    census: list[object] = []
    for run in form.line_endings_spread:
        census += [{"ending": run.ending, "lines": run.lines}]
    spread: object = None
    if form.blank_lines_spread is not None:
        spread = {
            "first": form.blank_lines_spread.first,
            "last": form.blank_lines_spread.last,
            "lines": form.blank_lines_spread.lines,
            "text": form.blank_lines_spread.text,
        }
    lines_before: list[object] = []
    for before in form.preamble:
        lines_before += [
            {"kind": before.kind, "lines": before.lines, "mark": before.mark}
        ]
    return {
        "blank_lines": blanks,
        "blank_lines_spread": spread,
        "byte_order_mark": form.byte_order_mark,
        "columns": columns,
        "delimiter": form.delimiter,
        "empty_rows": {
            "interior": form.empty_rows_interior,
            "leading": form.empty_rows_leading,
            "trailing": form.empty_rows_trailing,
        },
        "end_of_file_mark": form.end_of_file_mark,
        "escape": form.escape,
        "final_line_ending": form.final_line_ending,
        "header_quoting": form.header_quoting,
        "header_rows": rows,
        "header_rows_quoting": form.header_rows_quoting,
        "initial_space": form.initial_space,
        "line_endings": runs,
        "line_endings_spread": census,
        "preamble": lines_before,
        "preamble_withheld": form.preamble_withheld,
        "row_order": order,
        "separator_line": form.separator_line,
        "short_rows": form.short_rows,
        "trailing_delimiter": {
            "header": form.header_trailing_delimiter,
            "rows": form.rows_trailing_delimiter,
        },
        "written_names": names,
    }


DOCUMENT_KEYS = (
    "blank_lines",
    "blank_lines_spread",
    "byte_order_mark",
    "columns",
    "delimiter",
    "empty_rows",
    "end_of_file_mark",
    "escape",
    "final_line_ending",
    "header_quoting",
    "header_rows",
    "header_rows_quoting",
    "initial_space",
    "line_endings",
    "line_endings_spread",
    "preamble",
    "preamble_withheld",
    "row_order",
    "separator_line",
    "short_rows",
    "trailing_delimiter",
    "written_names",
)


# -- small text helpers the offline audit reads ------------------------


def _text(value: object) -> str:
    """``value`` proven to be text, which is what lets a method run on it."""
    if not isinstance(value, str):
        raise TypeError("internal check: a piece of a table was not text")
    return value


def _holds(text: str, part: str) -> bool:
    """True when ``part`` stands anywhere in ``text``."""
    return part in _text(text)


def _starts(text: str, part: str) -> bool:
    """True when ``text`` begins with ``part``."""
    found = _text(text)
    return found[: len(part)] == part


def _ends(text: str, part: str) -> bool:
    """True when ``text`` ends with ``part``."""
    found = _text(text)
    if len(found) < len(part):
        return False
    return found[len(found) - len(part) :] == part


def _holds_nothing(cell: str) -> bool:
    """True when a cell is empty or holds nothing but spaces and tabs.

    THE ONE READING OF A CELL OF NOTHING, on the survey's side and the
    twin's (the integration of landings 2b.6 to 2b.10, 2026-09-16). The
    survey reads a cell of spaces as holding nothing (plan P4-D84), and
    the twin's arrangement asked only whether a cell was EMPTY, which was
    the same question while the generator wrote such a cell empty.
    Landing 2b.8 made the twin write the spaces a writer put in an absent
    cell back as they were, so a record of ` , ` came back as spaces the
    arrangement could not see, its ninety records were scattered, and the
    twin missed `bytes.empty-rows` against its own description at exit 3.
    Both sides ask this now.
    """
    return cell == "" or _only_spaces_and_tabs(cell)


def _only_spaces_and_tabs(text: str) -> bool:
    """True when ``text`` holds something and nothing but spaces and tabs."""
    found = _text(text)
    if not found:
        return False
    for character in found:
        if character != _SPACE and character != _TAB:
            return False
    return True


def _is_sequence_number(text: str) -> bool:
    """A whole number written in plain decimal figures with no padding."""
    found = _text(text)
    if not found or not parsing.is_digit_text(found):
        return False
    return found == "0" or found[:1] != "0"


# -- which characters are which ----------------------------------------


def preamble_shape(line: str) -> "tuple[str, str]":
    """One line before the table as its kind and its mark, never its text.

    A line holding nothing, or nothing but spaces and tabs, is BLANK and
    its mark is the whitespace itself -- which discloses nothing and
    lets the twin write the line back exactly. A line beginning with
    anything that is not a letter or a digit is a COMMENT, and its mark
    is that opening punctuation, which is how a reader recognises such a
    line (`comment="#"`). Anything else is TEXT, and nothing whatever of
    it is published.

    THIS READS A LINE AND NOTHING ELSE. What the twin can WRITE is
    `writable_shape`, applied to the pair this returns; the two are
    apart so that a description can be held to each separately (plan
    P4-D83, contract FD11).
    """
    found = _text(line)
    if not found or _only_spaces_and_tabs(found):
        return (PREAMBLE_BLANK, found)
    kept = ""
    for character in found:
        if _is_letter_or_digit(character):
            break
        kept = kept + character
    if kept:
        return (PREAMBLE_COMMENT, kept)
    return (PREAMBLE_TEXT, "")


def mark_breaks_a_line(mark: str, delimiter: str) -> bool:
    """Whether a published mark would stop its stand-in being one record.

    A quote character opens a field nothing closes; the delimiter cuts
    the stand-in into fields (plan P4-D83). Either leaves a twin whose
    first line is not the line the description published, so neither
    may stand in a mark. The delimiter is not consulted where it is not
    known -- the producer's publication guard has no form in hand, and
    the loader, which does, passes it.
    """
    found = _text(mark)
    if _holds(found, _QUOTE):
        return True
    return bool(delimiter) and _holds(found, delimiter)


def writable_shape(
    kind: str, mark: str, delimiter: str
) -> "tuple[str, str]":
    """A line's shape narrowed to a mark the twin can write (plan P4-D83).

    The mark is written into the twin ahead of the stand-in, so a mark
    that cannot be written leaves a twin that is not a file. MEASURED,
    which is what this function exists for: a title line written
    `"Extract for unit 7"` gave the mark `"`, the twin's first line was
    written `"withheld line`, and that is a quoted field nothing
    closes -- the twin missed about 120 obligations of its own
    description and `synthtwin profile` refused to read the twin at
    all, where the very same bytes were twinned cleanly before lines
    before a table were withheld at all. A mark carrying the file's own
    delimiter breaks it the other way, cutting the stand-in into fields
    a reader takes for the table's header.

    So the mark ends before the first such character, and a line whose
    punctuation begins with one is a line of TEXT: its stand-in is the
    two neutral words, which every reader reads as one field. A blank
    line is untouched -- its mark is spaces and tabs, which hold
    neither character.
    """
    if kind == PREAMBLE_BLANK or not mark_breaks_a_line(mark, delimiter):
        return (kind, mark)
    kept = ""
    for character in _text(mark):
        if character == _QUOTE or (delimiter and character == delimiter):
            break
        kept = kept + character
    if kept:
        return (PREAMBLE_COMMENT, kept)
    return (PREAMBLE_TEXT, "")


def preamble_line(run: PreambleRun) -> str:
    """The neutral line a twin writes for one line of a run.

    It wears the run's own shape, so the survey that reads the twin back
    gives the very run that was published: a blank line stays blank and
    keeps its spaces, a comment keeps its mark, and a line of text
    becomes two words holding a space -- which is a title line to the
    survey and never a one-column table's name.

    AND IT IS ONE RECORD OF THE FILE, always (plan P4-D83). The mark a
    run carries holds no quote character and no delimiter, so nothing
    it can carry opens a field or cuts the line in two.
    """
    if run.kind == PREAMBLE_BLANK:
        return run.mark
    return run.mark + WITHHELD_LINE


def preamble_runs(
    lines: "list[str]", delimiter: str = ""
) -> "tuple[PreambleRun, ...]":
    """The lines before the table, run-length encoded by their shape.

    ``delimiter`` is the table's own, so that no mark carries it (plan
    P4-D83).
    """
    runs: list[PreambleRun] = []
    for line in lines:
        kind, mark = writable_shape(*preamble_shape(line), delimiter)
        last = len(runs) - 1
        if last >= 0 and runs[last].kind == kind and runs[last].mark == mark:
            runs[last] = PreambleRun(
                kind=kind, lines=runs[last].lines + 1, mark=mark
            )
            continue
        runs += [PreambleRun(kind=kind, lines=1, mark=mark)]
    return tuple(runs)


def preamble_lines_total(runs: "tuple[PreambleRun, ...]") -> int:
    """How many lines stand before the table in all."""
    total = 0
    for run in runs:
        total = total + run.lines
    return total


def preamble_lines_written(runs: "tuple[PreambleRun, ...]") -> int:
    """How many of those lines hold any character at all.

    The standard reader yields a record for a line of spaces and none
    for an empty one, so this is the count the reader agreement walks
    past.
    """
    total = 0
    for run in runs:
        if run.kind != PREAMBLE_BLANK or run.mark:
            total = total + run.lines
    return total


def preamble_lines_holding_text(runs: "tuple[PreambleRun, ...]") -> int:
    """How many of those lines held text, which is never published.

    Pandas counts a line of nothing but spaces as blank, so this is the
    count that reader is told to skip -- and it is also the count that
    decides `preamble_withheld`.
    """
    total = 0
    for run in runs:
        if run.kind != PREAMBLE_BLANK:
            total = total + run.lines
    return total


def holds_no_letter_or_digit(text: str) -> bool:
    """True when nothing in ``text`` is a letter or a digit.

    The publication guard asks this of a preamble mark. Punctuation and
    whitespace before a line's first letter belong to whatever wrote the
    file; a letter or a digit is a word of somebody's own text, and the
    description carries none (plan P4-D80).
    """
    found = _text(text)
    for character in found:
        if _is_letter_or_digit(character):
            return False
    return True


def _is_letter_or_digit(character: str) -> bool:
    """A letter or digit of any script: anything but punctuation and space."""
    if "a" <= character <= "z" or "A" <= character <= "Z":
        return True
    if "0" <= character <= "9":
        return True
    return ord(character) > 127


def cell_class(cell: str) -> str:
    """Which of `CELL_CLASSES` one cell belongs to."""
    found = _text(cell)
    if not found:
        return CELL_EMPTY
    if parsing.is_missing_text(found):
        return CELL_ABSENT
    if parsing.classify_number(found) != parsing.NOT_A_NUMBER:
        return CELL_NUMBER
    return CELL_TEXT


def needs_quoting(
    cell: str, delimiter: str, escape: str, initial_space: bool, alone: bool
) -> bool:
    """Whether a minimal writer quotes this cell.

    ``alone`` says the cell is the only one on its line, where an empty
    cell written bare would be a blank line and not a record.
    """
    found = _text(cell)
    if not found:
        return alone
    if (
        _holds(found, delimiter)
        or _holds(found, _QUOTE)
        or _holds(found, _CR)
        or _holds(found, _LF)
    ):
        return True
    if escape == ESCAPE_BACKSLASH and _holds(found, _BACKSLASH):
        return True
    return initial_space and found[:1] == _SPACE


def must_quote(
    cell: str, delimiter: str, escape: str, initial_space: bool, alone: bool
) -> bool:
    """Whether this cell cannot be read back at all unless it is quoted."""
    found = _text(cell)
    if not found:
        return alone
    if _holds(found, delimiter) or _holds(found, _CR) or _holds(found, _LF):
        return True
    if found[:1] == _QUOTE:
        return True
    if escape == ESCAPE_BACKSLASH and _holds(found, _BACKSLASH):
        return True
    return initial_space and found[:1] == _SPACE


# -- decoding ----------------------------------------------------------


def _holds_a_byte_between(data: bytes, low: int, high: int) -> bool:
    """True when some byte of ``data`` lies in ``low .. high``."""
    if not isinstance(data, bytes):
        raise TypeError("internal check: a file's bytes were not bytes")
    for value in range(low, high + 1):
        if bytes([value]) in data:
            return True
    return False


def decoded(data: bytes, shown: str) -> "tuple[str, str, bool]":
    """The file's text, the encoding that read it, and whether a mark led.

    Guarantees:

    - Inputs: the file's bytes, and the path as the person wrote it, for
      a refusal.
    - Order: a UTF-32 mark is refused; a UTF-16 mark is read as UTF-16
      when the bytes after it are UTF-16 holding a line break and no zero
      character; then UTF-8, with or without its mark; then, where a byte
      between 0x80 and 0x9F is present and every such byte is defined
      there, Windows-1252; then Latin-1, which reads any bytes. A file
      with no byte in 0x80-0x9F reads the same under Windows-1252 and
      Latin-1, and is named Latin-1.
    - Errors raised: ProfileError for a UTF-32 file. A file read under
      Latin-1 whose first bytes are a UTF-16 mark is refused by the
      reader, which owns that message.
    - Boundary: nothing is opened.

    WHY WRITING BACK MAKES THE GUESS SAFE. Latin-1 and Windows-1252 map
    each byte they define to one character and back, so a twin written
    in the encoding its table was read with carries the same bytes for
    every published label, whatever encoding the file really was: a
    MacRoman file read as Windows-1252 publishes letters that look wrong
    and writes back the bytes it read.
    """
    if not isinstance(data, bytes):
        raise TypeError("internal check: a file's bytes were not bytes")
    if data[:4] == b"\x00\x00\xfe\xff" or data[:4] == b"\xff\xfe\x00\x00":
        raise errors.ProfileError(errors.looks_like_utf16(shown))
    if data[:2] == b"\xff\xfe" or data[:2] == b"\xfe\xff":
        codec = ENCODING_UTF16_LE if data[:2] == b"\xff\xfe" else ENCODING_UTF16_BE
        try:
            wide = str(data[2:], codec)
        except UnicodeDecodeError:
            wide = ""
        if wide and "\x00" not in wide and (_CR in wide or _LF in wide):
            return (wide, codec, True)
    if data[:3] == b"\xef\xbb\xbf":
        try:
            return (str(data[3:], "utf-8"), ENCODING_UTF8, True)
        except UnicodeDecodeError:
            pass
    else:
        try:
            return (str(data, "utf-8"), ENCODING_UTF8, False)
        except UnicodeDecodeError:
            pass
    if _holds_a_byte_between(data, 0x80, 0x9F):
        try:
            return (str(data, "cp1252"), ENCODING_CP1252, False)
        except UnicodeDecodeError:
            pass
    return (str(data, "latin-1"), ENCODING_LATIN1, False)


def decoded_as(data: bytes, shown: str, encoding: str) -> "tuple[str, str, bool]":
    """The file's text read in a description's published encoding, where it can be.

    The validator's reading of a checked file (plan P4-D86, repair of
    landing 2b.9). A description published as Latin-1 or Windows-1252
    publishes every label as that encoding reads it, so a checked file is
    read the same way whenever its bytes decode there and carry no UTF-8
    or UTF-16 mark (contract FD3 gives such a description none). Reading
    it by detection instead would read a twin whose non-UTF-8 bytes all
    stood in cells written as stand-ins -- and which is therefore valid
    UTF-8 -- as UTF-8, and find every accented label changed. Every other
    case is `decoded`'s.

    A MARK-SHAPED PREFIX IS DATA HERE, NOT A MARK (review item CODEX-8).
    Contract FD3 gives a description published as Latin-1 or
    Windows-1252 no byte-order mark at all, so those three bytes at the
    start of such a file are three characters of its first cell -- which
    is exactly what they were in the table it describes. This used to
    hand the file to detection instead: a table whose bytes were UTF-8
    behind a mark with one stray Latin-1 byte was described as Latin-1,
    without a mark, its first column named `\u00ef\u00bb\u00bfrecord`; the twin
    dropped the stray byte, became valid UTF-8, and was then re-read AS
    UTF-8 with the prefix consumed as a mark -- so the twin failed its
    own description on twelve counts, names and label counts among them.
    """
    if not isinstance(data, bytes):
        raise TypeError("internal check: a file's bytes were not bytes")
    if encoding in FALLBACK_ENCODINGS:
        try:
            return (str(data, WRITING_CODECS[encoding]), encoding, False)
        except UnicodeDecodeError:
            pass
    return decoded(data, shown)


# -- the lexer ---------------------------------------------------------


def physical_lines(text: str) -> "list[str]":
    """The text's lines as a file opened with ``newline=""`` hands them over.

    A line ends after a line feed, after a carriage return with no line
    feed behind it, or after the pair, and keeps its ending; nothing is
    translated. This is the splitting the standard reader is fed by a
    file handle, and the walk below and the reader module's check both
    read these lines, so a record here is a record there.

    Cut on the line feeds first and then on the carriage returns inside
    each piece: two splits on a literal each, which the offline audit
    accepts and which keeps this linear in the text's size.
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a piece of a table was not text")
    lines: list[str] = []
    pieces = text.split("\n")
    for index in range(len(pieces)):
        lines += _cut_at_returns(pieces[index], index < len(pieces) - 1)
    return lines


def _cut_at_returns(piece: str, cut_at_a_feed: bool) -> "list[str]":
    """One line-feed piece cut again at every carriage return in it.

    ``cut_at_a_feed`` says the piece was followed by a line feed, so a
    carriage return at its very END is the first half of one `\\r\\n`
    terminator and not a line of its own.
    """
    if not isinstance(piece, str):
        raise TypeError("internal check: a piece of a table was not text")
    lines: list[str] = []
    parts = piece.split("\r")
    last = len(parts) - 1
    for at in range(last):
        body = parts[at] + _CR
        if at == last - 1 and cut_at_a_feed and not parts[last]:
            body = parts[at] + "\r\n"
        lines += [body]
    tail = parts[last]
    if cut_at_a_feed and not (last > 0 and not tail):
        return lines + [tail + _LF]
    if not cut_at_a_feed and tail:
        return lines + [tail]
    return lines


@dataclasses.dataclass
class _Cursor:
    """The lines a walk reads, and the next one it has not read."""

    lines: "list[str]"
    index: int
    delimiter: str
    escape: str
    initial_space: bool


@dataclasses.dataclass(frozen=True)
class Record:
    """One record as the standard reader yields it, with what it drops.

    ``fields`` are the values; ``quoted`` says which opened with a quote
    character; ``spaces`` counts the spaces skipped before each under
    `initial_space`; ``ending`` is the line ending that closed the record
    ("" at the end of the text); ``raw`` is the record's own text before
    that ending; ``malformed`` counts fields in which text followed a
    closing quote, or a quoted field the text ended inside; ``escapes``
    counts the quote characters written doubled, or the characters
    escaped, inside quoted fields.
    """

    fields: "list[str]"
    quoted: "list[bool]"
    spaces: "list[int]"
    ending: str
    raw: str
    malformed: int
    escapes: int = 0


def _body_of(line: str) -> "tuple[str, str]":
    """A line's text and its ending."""
    if not isinstance(line, str):
        raise TypeError("internal check: a piece of a table was not text")
    if line[len(line) - 2 :] == "\r\n":
        return (line[: len(line) - 2], "\r\n")
    if line[len(line) - 1 :] == _LF or line[len(line) - 1 :] == _CR:
        return (line[: len(line) - 1], line[len(line) - 1 :])
    return (line, "")


def _split_on(body: str, delimiter: str) -> "list[str]":
    """A line holding no quote or escape character, cut at its delimiter.

    One literal per branch, because the offline audit accepts a string
    method's argument only where it is a literal (plan D6.2).
    """
    if not isinstance(body, str):
        raise TypeError("internal check: a piece of a table was not text")
    if delimiter == ",":
        return body.split(",")
    if delimiter == ";":
        return body.split(";")
    if delimiter == "\t":
        return body.split("\t")
    if delimiter == "|":
        return body.split("|")
    raise ValueError("internal check: a delimiter the lexer does not know")


def _unspaced(value: str) -> "tuple[str, int]":
    """A field with the spaces it begins with taken off, and how many."""
    found = _text(value)
    count = 0
    while count < len(found) and found[count] == _SPACE:
        count = count + 1
    return (found[count:], count)


# The standard reader's states (`Modules/_csv.c`), for a record whose
# line holds a quote or an escape character.
_START_RECORD = 0
_START_FIELD = 1
_ESCAPED_CHAR = 2
_IN_FIELD = 3
_IN_QUOTED_FIELD = 4
_ESCAPE_IN_QUOTED_FIELD = 5
_QUOTE_IN_QUOTED_FIELD = 6
_EAT_CRNL = 7
_AFTER_ESCAPED_CRNL = 8


def _record_at(cursor: _Cursor) -> "Record | None":
    """The next record, or None where the text holds no more.

    A line holding no quote character, and no backslash under backslash
    escaping, is one record whose fields are its text cut at the
    delimiter -- which is what the standard reader's states make of such
    a line -- and is read by one split. Any other line is walked by those
    states a character at a time, across as many lines as a quoted field
    spans, with the end of each line handed to the machine as the reader
    hands it.
    """
    if cursor.index >= len(cursor.lines):
        return None
    line = cursor.lines[cursor.index]
    body, ending = _body_of(line)
    if not body:
        cursor.index = cursor.index + 1
        return Record([], [], [], ending, "", 0)
    backslash = cursor.escape == ESCAPE_BACKSLASH
    if not _holds(body, _QUOTE) and not (backslash and _holds(body, _BACKSLASH)):
        cursor.index = cursor.index + 1
        parts = _split_on(body, cursor.delimiter)
        if not cursor.initial_space:
            return Record(
                parts, [False for _part in parts], [0 for _part in parts],
                ending, body, 0,
            )
        fields: list[str] = []
        spaces: list[int] = []
        for part in parts:
            value, count = _unspaced(part)
            fields += [value]
            spaces += [count]
        return Record(
            fields, [False for _part in parts], spaces, ending, body, 0
        )
    return _record_by_characters(cursor)


def _record_by_characters(cursor: _Cursor) -> "Record | None":
    """One record walked by the standard reader's states, character by character."""
    delimiter = cursor.delimiter
    backslash = cursor.escape == ESCAPE_BACKSLASH
    spaced = cursor.initial_space
    fields: list[str] = []
    quoted: list[bool] = []
    spaces: list[int] = []
    value = ""
    opened = False
    skipped = 0
    closed = False
    malformed = 0
    escapes = 0
    state = _START_FIELD
    ending = ""
    raw = ""
    while cursor.index < len(cursor.lines):
        line = _text(cursor.lines[cursor.index])
        cursor.index = cursor.index + 1
        for place in range(len(line)):
            character = line[place]
            if state == _AFTER_ESCAPED_CRNL:
                state = _IN_FIELD
            if state == _START_FIELD:
                if character == _CR or character == _LF:
                    fields += [value]
                    quoted += [opened]
                    spaces += [skipped]
                    value, opened, skipped, closed = "", False, 0, False
                    state = _EAT_CRNL
                    ending = line[place:]
                elif character == _QUOTE:
                    state = _IN_QUOTED_FIELD
                    opened = True
                elif backslash and character == _BACKSLASH:
                    state = _ESCAPED_CHAR
                elif spaced and character == _SPACE:
                    skipped = skipped + 1
                elif character == delimiter:
                    fields += [value]
                    quoted += [opened]
                    spaces += [skipped]
                    value, opened, skipped, closed = "", False, 0, False
                else:
                    value = value + character
                    state = _IN_FIELD
            elif state == _ESCAPED_CHAR:
                value = value + character
                if character == _CR or character == _LF:
                    state = _AFTER_ESCAPED_CRNL
                else:
                    state = _IN_FIELD
            elif state == _IN_FIELD:
                if character == _CR or character == _LF:
                    fields += [value]
                    quoted += [opened]
                    spaces += [skipped]
                    value, opened, skipped, closed = "", False, 0, False
                    state = _EAT_CRNL
                    ending = line[place:]
                elif backslash and character == _BACKSLASH:
                    state = _ESCAPED_CHAR
                elif character == delimiter:
                    fields += [value]
                    quoted += [opened]
                    spaces += [skipped]
                    value, opened, skipped, closed = "", False, 0, False
                    state = _START_FIELD
                else:
                    if closed:
                        malformed = malformed + 1
                        closed = False
                    value = value + character
            elif state == _IN_QUOTED_FIELD:
                if backslash and character == _BACKSLASH:
                    state = _ESCAPE_IN_QUOTED_FIELD
                elif character == _QUOTE:
                    if backslash:
                        state = _IN_FIELD
                        closed = True
                    else:
                        state = _QUOTE_IN_QUOTED_FIELD
                else:
                    value = value + character
            elif state == _ESCAPE_IN_QUOTED_FIELD:
                value = value + character
                escapes = escapes + 1
                state = _IN_QUOTED_FIELD
            elif state == _QUOTE_IN_QUOTED_FIELD:
                if character == _QUOTE:
                    value = value + _QUOTE
                    escapes = escapes + 1
                    state = _IN_QUOTED_FIELD
                elif character == delimiter:
                    fields += [value]
                    quoted += [opened]
                    spaces += [skipped]
                    value, opened, skipped, closed = "", False, 0, False
                    state = _START_FIELD
                elif character == _CR or character == _LF:
                    fields += [value]
                    quoted += [opened]
                    spaces += [skipped]
                    value, opened, skipped, closed = "", False, 0, False
                    state = _EAT_CRNL
                    ending = line[place:]
                else:
                    malformed = malformed + 1
                    value = value + character
                    state = _IN_FIELD
        # The end of the line, as the reader hands it to its machine.
        if state == _START_FIELD or state == _IN_FIELD or state == _QUOTE_IN_QUOTED_FIELD:
            fields += [value]
            quoted += [opened]
            spaces += [skipped]
            value, opened, skipped, closed = "", False, 0, False
            state = _START_RECORD
        elif state == _ESCAPED_CHAR:
            value = value + _LF
            state = _IN_FIELD
        elif state == _ESCAPE_IN_QUOTED_FIELD:
            value = value + _LF
            state = _IN_QUOTED_FIELD
        elif state == _EAT_CRNL:
            state = _START_RECORD
        if state == _START_RECORD:
            raw = raw + line[: len(line) - len(ending)]
            return Record(fields, quoted, spaces, ending, raw, malformed, escapes)
        raw = raw + line
    if value or state == _IN_QUOTED_FIELD:
        fields += [value]
        quoted += [opened]
        spaces += [skipped]
        return Record(fields, quoted, spaces, "", raw, malformed + 1, escapes)
    if fields:
        return Record(fields, quoted, spaces, "", raw, malformed + 1, escapes)
    return None


def records(
    text: str,
    delimiter: str,
    escape: str,
    initial_space: bool,
    at: int = 0,
    limit: int = -1,
) -> "list[Record]":
    """Every record from ``at``, or the first ``limit`` of them.

    A blank line is a record with no fields, as the standard reader
    yields it. With a ``limit`` only the text's first megabyte is cut
    into lines, which is all detection needs; `survey` walks the whole
    text itself.
    """
    found = _text(text)
    span = found[at:] if limit < 0 else found[at : at + 1_048_576]
    cursor = _Cursor(physical_lines(span), 0, delimiter, escape, initial_space)
    taken: list[Record] = []
    while limit < 0 or len(taken) < limit:
        record = _record_at(cursor)
        if record is None:
            break
        taken += [record]
    return taken


def _ending_at(text: str, at: int, size: int) -> str:
    """The line ending that begins at ``at``: CR LF, CR, LF or nothing."""
    found = _text(text)
    if at >= size:
        return ""
    if found[at] == _LF:
        return _LF
    if found[at + 1 : at + 2] == _LF:
        return "\r\n"
    return _CR


# -- detecting the dialect ---------------------------------------------


def _separator_hint(text: str) -> "tuple[str, int]":
    """Excel's `sep=X` first line: the delimiter it names and where data starts."""
    found = _text(text)
    if found[:4] != "sep=" or len(found) < 5:
        return ("", 0)
    named = found[4]
    if named not in DELIMITERS:
        return ("", 0)
    ending = _ending_at(found, 5, len(found))
    if not ending and len(found) > 5:
        return ("", 0)
    return (named, 5 + len(ending))


def _leads_the_table(record: Record) -> bool:
    """Whether a record has the shape of a line before a table, not a row of it.

    A blank line; a line beginning with `#`; or a line of one field that
    reads as a title because it holds a space. A one-field line holding
    no space is the name of a one-column table as often as it is a
    title, and taking it for a title would put that table's first row
    in its place, so it is not one.
    """
    if not record.fields:
        return True
    raw = _text(record.raw)
    if _starts(raw, "#"):
        return True
    return len(record.fields) == 1 and lone_field_leads_a_table(raw)


def lone_field_leads_a_table(text: str) -> bool:
    """Whether ONE field standing alone above a table reads as furniture.

    THE ONE RULE FOR A LINE OF ONE FIELD AND A ROW OF ONE CELL (plan
    P4-D186). A field beginning with `#` is a comment and a field holding
    a space reads as a title; a field of one word holds neither and is
    the name of a table as often as it is a title, so it is not one. The
    delimited survey asks this of a one-field line (`_leads_the_table`)
    and the workbook reader of a one-cell row, so a title a text file
    steps over is stepped over in a workbook too, and a one-word row a
    text file reads as names is read as names there.
    """
    found = _text(text)
    return _starts(found, "#") or _holds(found, _SPACE)


def _width_share(sample: "list[Record]") -> "tuple[float, int]":
    """The share of records at their most common width, and that width.

    Blank lines and lines of nothing but spaces are not counted: they are
    not records of any width.
    """
    counted: dict[int, int] = {}
    total = 0
    for record in sample:
        width = len(record.fields)
        if not width:
            continue
        if width == 1 and _only_spaces_and_tabs(record.fields[0]):
            continue
        counted[width] = (counted[width] if width in counted else 0) + 1
        total = total + 1
    if not total:
        return (0.0, 0)
    best = 0
    best_count = 0
    for width in sorted(counted):
        if counted[width] >= best_count:
            best = width
            best_count = counted[width]
    return (best_count / total, best)


def delimiter_reading(text: str, at: int) -> "tuple[str, tuple[str, ...]]":
    """The delimiter a table is written with, from its first records.

    Each candidate reads the first records; the one under which the most
    records share one width of two or more fields wins, a wider table
    breaking a tie and the order of `DELIMITERS` breaking a tie of both.
    A table no candidate reads as two or more fields is one column, and
    its delimiter is the comma. The full walk in `survey` then holds
    every record to the width this chose, so a table that only looked
    delimited in its first records is refused as ragged, never read
    wrongly.

    EACH CANDIDATE IS READ AT ITS OWN BEST over the spacings and the
    escapings (`_best_reading`, review item CODEX-5): the settings
    decide what a delimiter reads as, so choosing the delimiter first
    and the settings afterwards read a two-column file as one column.

    A TIE OF BOTH IS DECIDED BY THE CELLS FIRST (repair of landing 2b.9).
    A European export whose names hold a comma (`Gewicht, kg`) and whose
    every number carries one decimal comma reads as three fields a
    record under the comma and under the semicolon alike, and the order
    of `DELIMITERS` took the comma -- `41943;91` and `0;166` as cells.
    So on a tie the candidate under whose reading more cells read as
    numbers, with a point or with a decimal comma, wins; the order of
    `DELIMITERS` decides only where that ties too.

    AND A TIE OF BOTH IS RECORDED, NOT ONLY BROKEN (review item CODEX-4,
    plan P4-D110). Counting the cells that read as numbers is a guess
    about the file, and a genuinely ambiguous one proves it: `id,pair|code`
    over rows such as `1,2|3` reads as two fields a record under the comma
    AND under the vertical bar, and the count took the bar where commit
    53bb012 had read the comma. Both readings are consistent, so no count
    of the cells can say which the person's file is. The second value
    returned is every candidate that reads the file AS CONSISTENTLY as
    the winner does -- the winner first, then the others in `DELIMITERS`
    order -- or empty where nothing does. The reading still stands,
    because a file the baseline twinned may not become refused; the
    competing reading is what the person is then ASKED about, and
    `--delimiter` is how they answer.

    A COMPETITOR IS NOT REQUIRED TO AGREE ABOUT THE WIDTH, and requiring
    it hid the worst case of all (plan P4-D282, the repair of review
    item 3 of the files review of 2026-09-18). Recording only the
    candidates that tied on the share AND the width meant that the
    WIDER reading, which this walk prefers on a tie of the share, could
    take the file from a narrower reading that is every bit as
    consistent and say nothing at all. MEASURED on the tree before this
    rule: a header `id,measure|low|high` over 120 rows of
    `{i},{100 + i % 4}|90|110` reads as two whole columns under the
    comma, at a share of 1.0, and as three whole columns under the
    vertical bar, at a share of 1.0. Commit 53bb012 read the comma; the
    width alone settled it for the bar, no question was asked, and the
    first field was then read as a QUANTITY -- the twin wrote rows such
    as `3,029|90|110`, so code using the source's own comma delimiter
    read the measurement `029` where the column holds 100 to 103. Both
    files validated with nothing missed, against a description of a
    table the person does not have. The share is what says a candidate
    reads the whole file; the width says only which of two readings is
    bigger, and it may break a tie but it may not hide one.
    """
    chosen = ","
    best_share = 0.0
    best_width = 0
    best_numbers = -1
    best_sample: "list[Record]" = []
    for candidate in DELIMITERS:
        found = _best_reading(text, candidate, at)
        if found is None:
            continue
        share, width, sample = found
        numbers = -1
        if share == best_share and width == best_width:
            numbers = _numbers_read(sample)
            if best_numbers < 0:
                best_numbers = _numbers_read(best_sample)
        if (
            share > best_share
            or (share == best_share and width > best_width)
            or (share == best_share and width == best_width and numbers > best_numbers)
        ):
            chosen = candidate
            best_share = share
            best_width = width
            best_numbers = numbers
            best_sample = sample
    tied: list[str] = []
    for candidate in DELIMITERS:
        if candidate == chosen:
            continue
        found = _best_reading(text, candidate, at)
        if found is None:
            continue
        if found[0] == best_share:
            tied += [candidate]
    if not tied:
        return chosen, ()
    return chosen, tuple([chosen] + tied)


def detected_delimiter(text: str, at: int) -> str:
    """The delimiter a table is written with, from its first records.

    The first half of `delimiter_reading`, which says how it is chosen.
    """
    chosen, _tied = delimiter_reading(text, at)
    return chosen


def _best_reading(
    text: str, candidate: str, at: int
) -> "tuple[float, int, list[Record]] | None":
    """The best the first records read under one candidate delimiter.

    EVERY SETTING IS SCORED WITH THE DELIMITER (review item CODEX-5).
    This walk read each candidate ONE way -- no space after the
    delimiter, doubled quotes -- and left the spacing and the escaping
    to be settled afterwards, from the delimiter it had already chosen.
    That is the wrong order wherever the settings decide what the
    delimiter reads as. MEASURED: a file written `"id"; "note"` with
    `"1"; "alpha; beta"` under it reads, under the semicolon with no
    space skipped, as a header of two fields and rows of three -- the
    space before the quote makes that quote an ordinary character, so
    the semicolon inside the note splits the field -- and this walk
    rejects that as ragged. Nothing else read as two fields at all, so
    the file was described as ONE column named `id; "note"`. Read with
    the space skipped it is the two columns it is.

    So each candidate is scored at its own best over the two spacings
    and the two escapings, and WHICH of them the file is written with
    is still settled by the walks that own that question
    (`detected_initial_space`, and `settle` for the escaping), over the
    whole file rather than its first records.

    THE TABLE'S FIRST RECORD HAS THE TABLE'S WIDTH. A one-column table
    of `100|30` cells reads as two fields a row under the vertical bar,
    and only its first record -- the column's name, one field -- says
    the bar is not its delimiter.
    """
    best: "tuple[float, int, list[Record]] | None" = None
    for spaced in (False, True):
        for escaping in ESCAPES:
            sample = records(
                text, candidate, escaping, spaced, at, _SAMPLE_RECORDS
            )
            share, width = _width_share(sample)
            if width < 2:
                continue
            opening = 0
            while opening < len(sample) and _leads_the_table(sample[opening]):
                opening = opening + 1
            if opening < len(sample) and len(sample[opening].fields) != width:
                continue
            if best is None or (share, width) > (best[0], best[1]):
                best = (share, width, sample)
    return best


def _numbers_read(sample: "list[Record]") -> int:
    """How many cells of these records read as numbers, with a point or a decimal comma."""
    found = 0
    for record in sample:
        for value in record.fields:
            cell = _text(value)
            if parsing.classify_number(cell) != parsing.NOT_A_NUMBER:
                found = found + 1
            elif _holds(cell, ",") and parsing.classify_number(
                parsing.written_with_a_decimal_comma(cell)
            ) != parsing.NOT_A_NUMBER:
                found = found + 1
    return found


def detected_initial_space(text: str, at: int, delimiter: str) -> bool:
    """Whether every field after the first begins with exactly one space.

    That is the comma-space writing (`"a", "b"`), read with the standard
    reader's `skipinitialspace`. A padded field, which begins with
    several, is not it.
    """
    sample = records(text, delimiter, ESCAPE_DOUBLED, False, at, _SAMPLE_RECORDS)
    seen = False
    for record in sample:
        if len(record.fields) < 2:
            continue
        for index in range(1, len(record.fields)):
            value = record.fields[index]
            if value[:1] != _SPACE or value[1:2] == _SPACE:
                return False
            seen = True
    return seen


# -- the survey --------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Survey:
    """A table's records and its written form, from one walk of its text.

    ``header`` is the header record as written, after any trailing
    delimiter is taken off, or empty when the first row is data.
    ``columns`` holds every data cell, column-major. ``quoting_holds``
    carries, per column and per cell class, every quoting rule the
    column's cells are consistent with, and ``classified`` says whether
    the classes were told apart (a column quoted all one way is not
    walked a second time); the validator reads both. ``short_vacuous``
    says no data row ends with an empty cell at all, so a published
    `short_rows` holds of this file whatever it measured.
    """

    form: Dialect
    header: "tuple[str, ...]"
    columns: "list[list[str]]"
    n_rows: int
    quoting_holds: "tuple[tuple[frozenset[str], ...], ...]"
    classified: "tuple[bool, ...]"
    header_holds: "frozenset[str]"
    header_rows_holds: "frozenset[str]"
    short_vacuous: bool
    malformed: int
    escapes: int
    initial_space_broken: bool
    # WHETHER THE FILE WEARS A KNOWN EXPORT'S METADATA SHAPE (plan
    # P4-D81): two records under the column names, each as wide as the
    # table, the second with every cell an ImportId object. It is
    # DETECTED and acted on NOWHERE -- the rows leave the table only
    # where the person declared them -- and it is here so that the
    # questions file can ask about a file that has it.
    metadata_shape: bool = False
    # EVERY DELIMITER THE FILE READS EQUALLY WELL UNDER, where more than
    # one does and nobody said which (review item CODEX-4, plan P4-D110):
    # the one it was read with first, then the others. Empty where one
    # candidate read best, where a separator line named it, and where
    # the person declared it. Acted on nowhere but the questions file.
    delimiter_tie: "tuple[str, ...]" = ()
    # Measured whatever the caps: every place blank lines stand, how many
    # lines end each way, and the blank lines counted. The reader checks
    # the first against the standard reader; the validator compares the
    # other two with a description that published them.
    every_blank_place: "tuple[BlankPlace, ...]" = ()
    ending_census: "tuple[EndingRun, ...]" = ()
    blank_census: "BlankSpread | None" = None


@dataclasses.dataclass
class _Walk:
    """What the walk accumulates while it reads, before the form is settled."""

    runs: "list[EndingRun]"
    pending: str
    lines: int


def _add_ending(walk: _Walk, ending: str, shown: str) -> None:
    """Record the ending of the line before this one, in file order."""
    if walk.lines == 0:
        walk.pending = ending
        walk.lines = 1
        return
    _flush_ending(walk, shown)
    walk.pending = ending
    walk.lines = walk.lines + 1


def _flush_ending(walk: _Walk, shown: str) -> None:
    """Count the pending line's ending into the runs."""
    if not walk.pending:
        return
    word = "lf"
    for name in ENDINGS:
        if ENDING_TEXT[name] == walk.pending:
            word = name
    last = len(walk.runs) - 1
    if last >= 0 and walk.runs[last].ending == word:
        walk.runs[last] = EndingRun(ending=word, lines=walk.runs[last].lines + 1)
    else:
        # No cap here: every run is kept, and `survey` publishes the
        # counts in their place where there are more than the cap.
        walk.runs += [EndingRun(ending=word, lines=1)]
    walk.pending = ""


def generated_column_name(position: int) -> str:
    """The name a column of a table with no header is given, from one.

    The reader names such columns this way (`reading`), and a
    declaration naming one has to be matched against the same name here.
    """
    return f"column_{position}"


def unnamed_column(index: int) -> str:
    """The name a blank header cell is given for its place, counted from 0."""
    return f"Unnamed: {index}"


def named_columns(header: "tuple[str, ...]") -> "tuple[str, ...]":
    """The name each column is given from the header as it is written.

    A header cell that is blank, or holds only spaces, is named
    `Unnamed: N` for its place counted from 0; a cell repeating an
    earlier name gets `.1`, `.2`, ... after it. A made-up name is never
    one another column already has or is written with, so it moves on to
    the next number instead. That is what pandas names the same columns
    in the common cases, so code written against the twin's names reads
    the real table's.

    WHAT THE SUFFIX SEARCH COSTS, and why it is written this way
    (review item CODEX-16; repair of landing 2b.10). A header repeating
    one name n times used to restart its search at `.1` every time, so
    naming n columns did work proportional to n squared: 1,000 repeated
    names took 0.035 s and 8,000 took 2.45 s on the machine this was
    measured on. The next free number per base name is REMEMBERED here
    instead, which is sound because a name once taken is never given
    up, so the search can only ever move forward. The names produced
    are identical -- the search resumes where it stopped rather than
    landing somewhere else -- and a workbook header, which may be
    16,384 columns wide, no longer reaches a quadratic path from a
    file.
    """
    written: dict[str, bool] = {}
    for cell in header:
        found = _text(cell)
        if parsing.trimmed(found):
            written[found] = True
    taken: dict[str, bool] = {}
    named: list[str] = []
    following: dict[str, int] = {}
    for index in range(len(header)):
        cell = _text(header[index])
        base = cell if parsing.trimmed(cell) else f"Unnamed: {index}"
        name = base
        own = parsing.trimmed(cell) and base == cell
        if name in taken or (not own and name in written):
            count = following[base] if base in following else 1
            name = f"{base}.{count}"
            while name in taken or name in written:
                count = count + 1
                name = f"{base}.{count}"
            following[base] = count + 1
        taken[name] = True
        named += [name]
    return tuple(named)


def _quoting_census(
    cells: "list[str]",
    flags: bytearray,
    delimiter: str,
    escape: str,
    initial_space: bool,
    alone: bool,
) -> "tuple[tuple[str, ...], tuple[frozenset[str], ...], bool]":
    """One column's quoting rule per cell class, what holds, and whether classified."""
    if not isinstance(flags, bytearray):
        raise TypeError("internal check: quoting flags were not bytes")
    total = len(cells)
    # Each flag is 0 or 1, so their sum is how many cells were quoted.
    quoted = sum(flags)
    every = frozenset(_CANONICAL_ORDER)
    if total and quoted == 0:
        inner = False
        for cell in cells:
            if _holds(cell, _QUOTE):
                inner = True
                break
        rule = QUOTE_BARE if inner else QUOTE_NEEDED
        held = frozenset([QUOTE_BARE]) if inner else frozenset(
            [QUOTE_NEEDED, QUOTE_BARE]
        )
        return (
            tuple([rule for _k in CELL_CLASSES]),
            tuple([held for _k in CELL_CLASSES]),
            False,
        )
    if total and quoted == total:
        needed = True
        bare = True
        for cell in cells:
            if needed and not needs_quoting(cell, delimiter, escape, initial_space, alone):
                needed = False
            if bare and not must_quote(cell, delimiter, escape, initial_space, alone):
                bare = False
            if not needed and not bare:
                break
        held_rules = [QUOTE_ALWAYS]
        if needed:
            held_rules += [QUOTE_NEEDED]
        if bare:
            held_rules += [QUOTE_BARE]
        rule = QUOTE_NEEDED if needed else QUOTE_ALWAYS
        held = frozenset(held_rules)
        return (
            tuple([rule for _k in CELL_CLASSES]),
            tuple([held for _k in CELL_CLASSES]),
            False,
        )
    counts = [0, 0, 0, 0]
    quoted_counts = [0, 0, 0, 0]
    needed_broken = [False, False, False, False]
    bare_broken = [False, False, False, False]
    for index in range(total):
        cell = cells[index]
        kind = _CLASS_PLACE[cell_class(cell)]
        was = flags[index] == 1
        counts[kind] = counts[kind] + 1
        if was:
            quoted_counts[kind] = quoted_counts[kind] + 1
        if was != needs_quoting(cell, delimiter, escape, initial_space, alone):
            needed_broken[kind] = True
        if was != must_quote(cell, delimiter, escape, initial_space, alone):
            bare_broken[kind] = True
    rules: list[str] = []
    holds: list[frozenset[str]] = []
    for kind in range(len(CELL_CLASSES)):
        if not counts[kind]:
            rules += [QUOTE_NEEDED]
            holds += [every]
            continue
        found: list[str] = []
        if not needed_broken[kind]:
            found += [QUOTE_NEEDED]
        if not bare_broken[kind]:
            found += [QUOTE_BARE]
        if quoted_counts[kind] == counts[kind]:
            found += [QUOTE_ALWAYS]
        rules += [found[0] if found else QUOTE_MIXED]
        holds += [frozenset(found)]
    return (tuple(rules), tuple(holds), True)


def _header_census(
    cells: "list[str]",
    flags: "list[bool]",
    delimiter: str,
    escape: str,
    initial_space: bool,
    names: bool = True,
) -> "tuple[str, frozenset[str]]":
    """A header record's quoting rule, and every rule its cells agree with.

    ``names`` says the cells are the column names, whose first cell
    beginning with the byte-order mark is always quoted (method G2
    exception 1) and so counts as needing quotes. The metadata rows under
    the names are held to a rule of their own.
    """
    if not cells:
        return (QUOTE_NEEDED, frozenset(_CANONICAL_ORDER))
    alone = len(cells) == 1
    needed = True
    bare = True
    every = True
    for index in range(len(cells)):
        cell = _text(cells[index])
        marked = names and index == 0 and cell[:1] == _MARK
        need = marked or needs_quoting(cell, delimiter, escape, initial_space, alone)
        must = marked or must_quote(cell, delimiter, escape, initial_space, alone)
        if flags[index] != need:
            needed = False
        if flags[index] != must:
            bare = False
        if not flags[index]:
            every = False
    found: list[str] = []
    if needed:
        found += [QUOTE_NEEDED]
    if bare:
        found += [QUOTE_BARE]
    if every:
        found += [QUOTE_ALWAYS]
    return (found[0] if found else QUOTE_MIXED, frozenset(found))


def _pad_of(cells: "list[str]") -> "tuple[str, int]":
    """The side and width a column's cells are padded to, or ("", 0).

    Padded means: every cell is exactly one width of two or more, some
    cell with something in it has spaces on one side, and no such cell
    has spaces on the other.
    """
    if len(cells) < 2:
        return ("", 0)
    width = len(cells[0])
    if width < 2:
        return ("", 0)
    left = False
    right = False
    for cell in cells:
        found = _text(cell)
        if len(found) != width:
            return ("", 0)
        if not parsing.trimmed(found):
            continue
        if found[:1] == _SPACE:
            left = True
        if found[width - 1 :] == _SPACE:
            right = True
    if left and not right:
        return (PAD_LEFT, width)
    if right and not left:
        return (PAD_RIGHT, width)
    return ("", 0)


def _sequence_of(cells: "list[str]") -> int:
    """The start of the row sequence a column holds, or -1."""
    if len(cells) < 2:
        return -1
    first = _text(cells[0])
    if not _is_sequence_number(first) or int(first) not in SEQUENCE_STARTS:
        return -1
    start = int(first)
    for index in range(len(cells)):
        found = _text(cells[index])
        if not _is_sequence_number(found) or int(found) != start + index:
            return -1
    return start


def _order_keys(cells: "list[str]", collation: str) -> "list[object] | None":
    """Every cell's sort key under ``collation``, or None where one has none."""
    keys: list[object] = []
    for cell in cells:
        found = _text(cell)
        if not found:
            return None
        if collation == COLLATION_DECIMAL_COMMA:
            # The cell as it would have been written the way this tool
            # reads by default, which is exactly what the declaration
            # says about it (`parsing.written_with_a_decimal_comma`).
            swapped = parsing.written_with_a_decimal_comma(found)
            if parsing.classify_number(swapped) != parsing.NUMBER:
                return None
            decimal = parsing.parse_number(swapped)
            if decimal is None:
                return None
            keys += [decimal]
        elif collation == COLLATION_NUMBER:
            if parsing.classify_number(found) != parsing.NUMBER:
                return None
            number = parsing.parse_number(found)
            if number is None:
                return None
            keys += [number]
        else:
            keys += [found]
    return keys


def _monotone(keys: "list[object]") -> str:
    """ASCENDING, DESCENDING or "" for a list of comparable keys.

    A list of one repeated key is neither: it says nothing about order.
    """
    rising = True
    falling = True
    changed = False
    for index in range(1, len(keys)):
        before = keys[index - 1]
        after = keys[index]
        if after != before:
            changed = True
        if _less(after, before):
            rising = False
        if _less(before, after):
            falling = False
        if not rising and not falling:
            return ""
    if not changed:
        return ""
    if rising:
        return ASCENDING
    return DESCENDING if falling else ""


def _less(first: object, second: object) -> bool:
    """``first < second`` for two keys of one collation."""
    if isinstance(first, str) and isinstance(second, str):
        return first < second
    if isinstance(first, float) and isinstance(second, float):
        return first < second
    return False


def _collations_for(declared: bool) -> "tuple[str, ...]":
    """The collations a column is read under, in the order they are tried.

    A column the person DECLARED to write its numbers with a comma is
    read under that grammar first and under text second; it is never
    read under the ordinary number grammar, which would call `1,5` text
    and `1,234` one thousand two hundred and thirty-four -- the two
    wrong readings `--decimal-comma` exists to prevent. Every other
    column is read as it always was.
    """
    if declared:
        return (COLLATION_DECIMAL_COMMA, COLLATION_TEXT)
    return (COLLATION_NUMBER, COLLATION_TEXT)


def row_order_of(
    columns: "list[list[str]]",
    sequences: "list[int]",
    n_rows: int,
    declared_commas: "list[bool] | None" = None,
) -> RowOrder:
    """The leftmost column the rows are sorted by, if any.

    A column counts when every cell holds something and the cells never
    step backwards, read as numbers where every cell is one and as text
    otherwise, and change at least once. A row-sequence column is passed
    over: it is written in place whatever order the rows take, so
    sorting by it would say nothing.
    """
    if n_rows < 3:
        return NO_ORDER
    for index in range(len(columns)):
        if sequences[index] >= 0:
            continue
        declared = bool(
            declared_commas is not None
            and index < len(declared_commas)
            and declared_commas[index]
        )
        for collation in _collations_for(declared):
            keys = _order_keys(columns[index], collation)
            if keys is None:
                continue
            direction = _monotone(keys)
            if direction:
                return RowOrder(
                    column=index + 1, direction=direction, collation=collation
                )
            break
    return NO_ORDER


def holds_order(cells: "list[str]", order: RowOrder) -> bool:
    """Whether ``cells`` never step against ``order`` under its collation.

    The validator's question about a checked file: every cell holds
    something, reads under the collation, and no cell comes before the
    one above it in the published direction. A column of one repeated
    value holds any order.
    """
    keys = _order_keys(cells, order.collation)
    if keys is None:
        return False
    for index in range(1, len(keys)):
        if order.direction == ASCENDING and _less(keys[index], keys[index - 1]):
            return False
        if order.direction == DESCENDING and _less(keys[index - 1], keys[index]):
            return False
    return True


def holds_order_in(columns: "list[list[str]]", order: RowOrder) -> bool:
    """`holds_order` over a table's records that hold something.

    A record holding nothing in any cell of a table of two or more
    columns has no key, and the survey reads the order without such
    records, so the validator asks its question the same way.
    """
    if order.column < 1 or order.column > len(columns):
        return False
    empty: list[int] = []
    if len(columns) >= 2:
        for row in range(len(columns[0])):
            nothing = True
            for column in columns:
                if row < len(column) and not _holds_nothing(column[row]):
                    nothing = False
                    break
            if nothing:
                empty += [row]
    kept = _without_rows([columns[order.column - 1]], empty)
    return holds_order(kept[0], order)


def _is_import_row(fields: "list[str]") -> bool:
    """A survey export's second metadata row: every cell an ImportId object."""
    if not fields:
        return False
    for value in fields:
        found = _text(value)
        if not _starts(found, _IMPORT_MARK) or not _ends(found, "}"):
            return False
    return True


@dataclasses.dataclass
class _Stream:
    """Records read ahead of the walk, with `\\r\\r\\n` already joined.

    A record ending in a lone carriage return followed straight away by
    a line that is only `\\r\\n` is one record ending in `\\r\\r\\n`: the
    standard reader yields the second half as an empty record, and a file
    of them would otherwise be a blank line after every row.
    """

    cursor: _Cursor
    ahead: "list[Record]"
    index: int


def _read_joined(stream: _Stream) -> "Record | None":
    """The next record from the text, its `\\r\\r\\n` joined."""
    cursor = stream.cursor
    record = _record_at(cursor)
    if record is None:
        return None
    if (
        record.ending == _CR
        and cursor.index < len(cursor.lines)
        and cursor.lines[cursor.index] == "\r\n"
    ):
        cursor.index = cursor.index + 1
        return dataclasses.replace(record, ending="\r\r\n")
    return record


def _peek(stream: _Stream, offset: int) -> "Record | None":
    """The record ``offset`` places ahead of the walk, without taking it."""
    while len(stream.ahead) - stream.index <= offset:
        found = _read_joined(stream)
        if found is None:
            return None
        stream.ahead += [found]
    return stream.ahead[stream.index + offset]


def _take(stream: _Stream) -> "Record | None":
    """The next record, taken."""
    if stream.index < len(stream.ahead):
        found = stream.ahead[stream.index]
        stream.index = stream.index + 1
        if stream.index == len(stream.ahead):
            stream.ahead = []
            stream.index = 0
        return found
    return _read_joined(stream)


def _raw_of(stream: _Stream, record: Record) -> str:
    """A record's own text, before its line ending."""
    return record.raw


def _preamble_count(stream: _Stream) -> int:
    """How many records lead the table without being part of it.

    Blank lines always lead. A title line or a comment line leads where
    a record of two or more fields follows within the preamble cap: a
    record of one field, or one beginning with `#` whose width is not
    that record's. Where no such record follows, only the blank lines
    lead, because a record of one field is then the table's own.
    """
    wide = -1
    for offset in range(MAXIMUM_PREAMBLE_LINES + 1):
        found = _peek(stream, offset)
        if found is None:
            break
        if not _leads_the_table(found):
            if len(found.fields) >= 2:
                wide = offset
            break
    blanks = 0
    while True:
        found = _peek(stream, blanks)
        if found is None or found.fields:
            break
        blanks = blanks + 1
    if wide < 0:
        return blanks
    target = _peek(stream, wide)
    width = 0 if target is None else len(target.fields)
    for offset in range(wide):
        found = _peek(stream, offset)
        if found is not None and len(found.fields) == width and _starts(
            _raw_of(stream, found), "#"
        ):
            wide = offset
            break
    for offset in range(wide):
        found = _peek(stream, offset)
        if found is None:
            return blanks
        raw = _raw_of(stream, found)
        if found.fields and (_holds(raw, _CR) or _holds(raw, _LF)):
            return blanks
    return wide


def survey(
    text: str,
    encoding: str,
    byte_order_mark: bool,
    first_row_is_data: bool,
    shown: str,
    initial_space: "bool | None" = None,
    escape: str = "",
    trailing_guess: bool = True,
    metadata_rows: int = 0,
    decimal_comma_columns: "tuple[str, ...]" = (),
    metadata_rows_confirmed: bool = False,
    declared_delimiter: str = "",
    small_cell_floor: int = 1,
) -> Survey:
    """Walk a table's decoded text once: its records and its written form.

    Guarantees:

    - Inputs: the text (without its byte-order mark), the encoding named
      for it and whether a mark led, whether the caller said the first
      row is data, and the path for refusals. The last three arguments
      are for `settle`, which walks again when the first walk shows a
      guess about the file was wrong.
    - Determinism: a fixed function of those.
    - Errors raised: ProfileError, or a shape refusal, for a file with
      no record at all, a file whose records do not all have one width
      that no rule here accounts for (`errors.ragged_rows`), a blank line
      inside a one-column table, and a form past one of this module's
      caps.
    - Boundary: nothing is opened.
    """
    body = _text(text)
    end_mark = _ends(body, _END_OF_FILE)
    if end_mark:
        body = body[: len(body) - 1]
    size = len(body)
    hinted, at = _separator_hint(body)
    # A DECLARED DELIMITER IS READ, AND NOT GUESSED (review item CODEX-4,
    # plan P4-D110). A separator line in the file names its delimiter
    # already, so a declaration that names another one contradicts the
    # file itself and is refused rather than ranked.
    if hinted and declared_delimiter and hinted != declared_delimiter:
        raise errors.ProfileError(
            errors.delimiter_declared_against_the_file(
                shown,
                DELIMITER_WORDS[declared_delimiter],
                DELIMITER_WORDS[hinted],
            )
        )
    tie: "tuple[str, ...]" = ()
    if hinted:
        delimiter = hinted
    elif declared_delimiter:
        delimiter = declared_delimiter
    else:
        delimiter, tie = delimiter_reading(body, at)
    if initial_space is None:
        spaced = detected_initial_space(body, at, delimiter)
    else:
        spaced = initial_space
    escaping = escape if escape else ESCAPE_DOUBLED
    cursor = _Cursor(physical_lines(body[at:]), 0, delimiter, escaping, spaced)
    stream = _Stream(cursor, [], 0)
    walk = _Walk([], "", 0)
    if hinted:
        _add_ending(walk, _ending_at(body, 5, size), shown)

    preamble: list[str] = []
    for _offset in range(_preamble_count(stream)):
        found = _take(stream)
        if found is None:
            break
        preamble += [_raw_of(stream, found) if found.fields else ""]
        _add_ending(walk, found.ending, shown)

    malformed = 0
    escapes = 0
    spaces_broken = False
    header: list[str] = []
    header_flags: list[bool] = []
    header_rows: list[tuple[str, ...]] = []
    header_row_flags: list[bool] = []
    metadata_shape = False
    if not first_row_is_data:
        found = _take(stream)
        if found is None:
            raise errors.shape_refusal(
                errors.file_is_empty(shown), errors.NO_DATA_TO_DESCRIBE
            )
        header = [_text(value) for value in found.fields]
        header_flags = [bool(flag) for flag in found.quoted]
        malformed = malformed + found.malformed
        escapes = escapes + found.escapes
        spaces_broken = spaces_broken or _spaces_broken(found, spaced)
        _add_ending(walk, found.ending, shown)
        first = _peek(stream, 0)
        second = _peek(stream, 1)
        # THE SHAPE IS DETECTED HERE AND ACTED ON NOWHERE (plan P4-D81,
        # review item CODEX-2). This condition used to TAKE the two
        # records it recognises out of the table and publish them as
        # the columns' descriptions. It is a guess about a file, and
        # the file it guesses wrong about is one whose first record
        # happens to be as wide as the header with an ImportId row
        # under it -- at which point a person's own record becomes
        # schema text, published whole and written into the twin, with
        # the table two rows short and every count computed without it.
        # A guess may not do that, so what happens now is that the
        # shape is remembered and the person is ASKED.
        metadata_shape = (
            len(header) >= 2
            and first is not None
            and second is not None
            and len(first.fields) == len(header)
            and len(second.fields) == len(header)
            and _is_import_row(second.fields)
        )
        # ...and the rows leave the table only where the person said
        # they describe the columns. Each has to be as wide as the
        # header, because a narrower record is a row of the table
        # however it was declared.
        #
        # AND ONLY WHERE THE FILE BEARS THE DECLARATION OUT, OR THE
        # PERSON HAS CONFIRMED IT (review of landing 2b.17, MAJOR).
        # `--metadata-rows 2` typed on an ordinary table took two
        # records out of it and published them verbatim as the columns'
        # description -- two people's rows, exempt from the smallest
        # group, written into the twin, and gone from every count --
        # while the screen said the shape was not there. A declaration
        # the file plainly does not bear out is now READ but not acted
        # on: the rows stay in the table, the safe reading the contract
        # already names for a declaration that found nothing, and the
        # person is asked in the questions file, where the answer says
        # what it costs before it is acted on. Answering there is the
        # confirmation this flag carries. It is the CODEX-2 ruling read
        # from the other side: that one stopped a resemblance from
        # taking rows out unasked, and this stops a typing slip from
        # doing the same.
        wanted_rows = metadata_rows
        if metadata_rows and not metadata_shape and not metadata_rows_confirmed:
            wanted_rows = 0
        taken = 0
        while taken < wanted_rows and len(header) >= 2:
            ahead = _peek(stream, 0)
            if ahead is None or len(ahead.fields) != len(header):
                break
            found = _take(stream)
            if found is None:
                break
            header_rows += [tuple(found.fields)]
            header_row_flags += [bool(flag) for flag in found.quoted]
            malformed = malformed + found.malformed
            escapes = escapes + found.escapes
            _add_ending(walk, found.ending, shown)
            taken = taken + 1

    header_trailing = False
    rows_trailing = False
    trailing_broken = False
    decided = False
    width = len(header)
    columns: list[list[str]] = [[] for _place in range(width)]
    flags: list[bytearray] = [bytearray() for _place in range(width)]
    n_rows = 0
    offenders: list[tuple[int, int]] = []
    ragged = 0
    short = 0
    short_inconsistent = False
    full_ending_empty = 0
    ends_empty = 0
    blanks: list[BlankPlace] = []
    empty_rows: list[int] = []
    while True:
        found = _take(stream)
        if found is None:
            break
        malformed = malformed + found.malformed
        escapes = escapes + found.escapes
        fields = found.fields
        if not fields:
            _add_ending(walk, found.ending, shown)
            _blank(blanks, n_rows, "", shown)
            continue
        # A WHITESPACE-ONLY LINE IS READ FROM THE RAW TEXT (review item
        # CODEX-15). Under the comma-space reading the leading spaces of
        # a field are skipped before this test ever sees them, so a line
        # holding three spaces arrived here as one EMPTY field, failed
        # this test, and was refused as a short record -- a file of
        # `a, b` rows with blank lines between them could not be read at
        # all. The record's own text is what it held before anything was
        # skipped, so the blank line is recognised, and the spelling
        # published for it is the one the file actually carries.
        if (
            len(fields) == 1
            and width >= 2
            and not found.quoted[0]
            and _only_spaces_and_tabs(found.raw)
        ):
            _add_ending(walk, found.ending, shown)
            _blank(blanks, n_rows, found.raw, shown)
            continue
        spaces_broken = spaces_broken or _spaces_broken(found, spaced)
        _add_ending(walk, found.ending, shown)
        if not decided:
            decided = True
            if first_row_is_data:
                width = len(fields)
            else:
                named = len(header)
                last_empty = fields[len(fields) - 1] == ""
                header_last_empty = named >= 2 and header[named - 1] == ""
                if (
                    trailing_guess
                    and header_last_empty
                    and len(fields) == named
                    and last_empty
                ):
                    header_trailing = True
                    rows_trailing = True
                    width = named - 1
                elif header_last_empty and len(fields) == named - 1:
                    header_trailing = True
                    width = named - 1
                elif len(fields) == named + 1 and last_empty:
                    rows_trailing = True
                    width = named
                else:
                    width = named
                if header_trailing:
                    header = header[: named - 1]
                    header_flags = header_flags[: named - 1]
            columns = [[] for _place in range(width)]
            flags = [bytearray() for _place in range(width)]
        count = len(fields)
        if rows_trailing:
            if count == width + 1 and fields[count - 1] == "":
                count = width
            else:
                if header_trailing:
                    trailing_broken = True
                ragged = ragged + 1
                if len(offenders) < 3:
                    offenders += [(n_rows + 1, len(fields))]
                n_rows = n_rows + 1
                continue
        if count > width:
            ragged = ragged + 1
            if len(offenders) < 3:
                offenders += [(n_rows + 1, count)]
            n_rows = n_rows + 1
            continue
        if count < width:
            short = short + 1
            if fields[count - 1] == "":
                short_inconsistent = True
            if len(offenders) < 3:
                offenders += [(n_rows + 1, count)]
        elif fields[count - 1] == "":
            full_ending_empty = full_ending_empty + 1
        every_empty = True
        for place in range(width):
            if place < count:
                value = fields[place]
                columns[place] += [value]
                flags[place] += _BYTE_ONE if found.quoted[place] else _BYTE_ZERO
                # A CELL OF NOTHING BUT SPACES HOLDS NOTHING (plan
                # P4-D84, review item CODEX-7). This asked only whether
                # the cell held any character at all, while the
                # profiler counts a cell of spaces and tabs ABSENT and
                # the generator writes such a cell empty. Measured: a
                # file of thirty records and ninety ` , ` records
                # published NO record holding nothing, its twin held
                # ninety all the same, and the twin then missed
                # `bytes.empty-rows` against its own description at
                # exit 3 while the real file held it -- an obligation
                # no twin of that file could meet. One reading of
                # nothing, on both sides.
                if value and not _only_spaces_and_tabs(value):
                    every_empty = False
            else:
                columns[place] += [""]
                flags[place] += _BYTE_ZERO
        if fields[count - 1] == "":
            ends_empty = ends_empty + 1
        if every_empty and width >= 2:
            empty_rows += [n_rows]
        n_rows = n_rows + 1
    _flush_ending(walk, shown)

    if first_row_is_data and not decided:
        raise errors.shape_refusal(
            errors.file_is_empty(shown), errors.NO_DATA_TO_DESCRIBE
        )
    short_rows = False
    if short:
        if short_inconsistent or full_ending_empty:
            ragged = ragged + short
        else:
            short_rows = True
            offenders = []
    if ragged:
        if trailing_broken and trailing_guess:
            return survey(
                text,
                encoding,
                byte_order_mark,
                first_row_is_data,
                shown,
                spaced,
                escaping,
                False,
                metadata_rows,
                decimal_comma_columns,
                metadata_rows_confirmed,
                declared_delimiter,
            )
        raise errors.ProfileError(
            errors.ragged_rows(
                shown, width, offenders, ragged, DELIMITER_WORDS[delimiter]
            )
        )
    if width == 1:
        for standing in blanks:
            if standing.after < n_rows:
                raise errors.ProfileError(
                    errors.blank_line_in_one_column(shown, standing.after + 1)
                )

    sequences = [_sequence_of(columns[place]) for place in range(width)]
    column_forms: list[ColumnForm] = []
    holds: list[tuple[frozenset[str], ...]] = []
    classified: list[bool] = []
    for place in range(width):
        rules, held, walked = _quoting_census(
            columns[place], flags[place], delimiter, escaping, spaced, width == 1
        )
        side, pad_width = _pad_of(columns[place])
        column_forms += [
            ColumnForm(
                quoting=rules,
                pad_side=side,
                pad_width=pad_width,
                sequence_start=sequences[place],
            )
        ]
        holds += [held]
        classified += [walked]
    header_rule, header_held = _header_census(
        list(header), list(header_flags), delimiter, escaping, spaced
    )
    metadata_cells: list[str] = []
    for row in header_rows:
        metadata_cells += list(row)
    metadata_rule, metadata_held = _header_census(
        metadata_cells, header_row_flags, delimiter, escaping, spaced, False
    )
    written: list[WrittenName] = []
    if header:
        names = named_columns(tuple(header))
        for place in range(len(header)):
            if names[place] != header[place]:
                written += [WrittenName(position=place + 1, text=header[place])]
    leading = 0
    while leading < len(empty_rows) and empty_rows[leading] == leading:
        leading = leading + 1
    trailing = 0
    while (
        trailing < len(empty_rows) - leading
        and empty_rows[len(empty_rows) - 1 - trailing] == n_rows - 1 - trailing
    ):
        trailing = trailing + 1
    # THE ORDER IS READ OVER THE RECORDS THAT HOLD SOMETHING (repair of
    # landing 2b.9). A sorted Excel table with formatted-empty records
    # below it is sorted; its empty records hold no key, and reading the
    # order over them lost it. The twin puts its empty records in their
    # places first and sorts the rest around them (`arranged`).
    # WHICH COLUMNS THE PERSON DECLARED TO WRITE A DECIMAL COMMA
    # (review item CODEX-9). The order is read off the cells AS
    # WRITTEN, so a declared column has to be read under its own
    # grammar here or it falls to the text collation, where `10,0`
    # sorts before `9,9` -- and a table genuinely sorted by it
    # published no order at all. The names are matched the way every
    # other declaration is matched: against the names the header gives,
    # after `named_columns` has settled the blank and repeated ones.
    #
    # AND AGAINST THE NAMES A HEADERLESS TABLE IS GIVEN (plan P4-D172). A
    # table read with `--first-row data` has no header, and its columns
    # are named `column_1`, `column_2`, ... -- which is how a person
    # names one in `--decimal-comma column_2`. The names were looked up
    # in the header alone, so the declaration was recorded and never
    # reached the order: 120 headerless rows sorted by a decimal-comma
    # amount published no order, and seed 4 wrote 59 descending pairs.
    declared_commas: "list[bool]" = []
    if decimal_comma_columns:
        headed_names: "tuple[str, ...]" = ()
        if header:
            headed_names = named_columns(tuple(header))
        for place in range(len(columns)):
            spelled_name = generated_column_name(place + 1)
            if header:
                spelled_name = ""
            if place < len(headed_names):
                spelled_name = headed_names[place]
            declared_commas += [
                bool(spelled_name) and spelled_name in decimal_comma_columns
            ]
    order = row_order_of(
        _without_rows(columns, empty_rows),
        sequences,
        n_rows - len(empty_rows),
        declared_commas if declared_commas else None,
    )
    # THE WRITTEN FORM OF A FILE IS HELD TO THE DISCLOSURE RULE TOO
    # (plan P4-D290). Every count and position below is a fact about
    # LINES, and a line of a delimited table is one of its records.
    #
    # WHAT IS GATED IS WHAT THE FORM PUBLISHES, AND NOT THE READING.
    # `blanks`, `walk.runs` and `empty_rows` stay exactly as the walk
    # found them, because the survey hands them to the checking pass
    # that holds this reading to the standard library reader's -- gating
    # `blanks` itself made that pass step over a line the reader kept,
    # and a spaced blank line then refused the file as read two ways.
    withheld_lines = blank_lines_withheld(blanks, small_cell_floor)
    told_runs = endings_disclosed(walk.runs, small_cell_floor, withheld_lines)
    told_blanks = blank_places_disclosed(blanks, small_cell_floor)
    leading_told = row_count_disclosed(leading, small_cell_floor)
    trailing_told = row_count_disclosed(trailing, small_cell_floor)
    interior_told = row_count_disclosed(
        len(empty_rows) - leading - trailing, small_cell_floor
    )
    census = census_of(told_runs)
    blank_census = blank_census_of(blanks)
    runs_published: "tuple[EndingRun, ...]" = tuple(told_runs)
    census_published: "tuple[EndingRun, ...]" = ()
    if len(told_runs) > MAXIMUM_ENDING_RUNS:
        runs_published = ()
        census_published = census
    places_published: "tuple[BlankPlace, ...]" = tuple(told_blanks)
    spread_published: "BlankSpread | None" = None
    if len(told_blanks) > MAXIMUM_BLANK_PLACES:
        places_published = ()
        spread_published = blank_census_of(told_blanks)
    # THE LINES BEFORE THE TABLE ARE PUBLISHED AS SHAPES (plan P4-D80).
    # Their text is not published here, and there is no floor at which
    # it is: nothing downstream can publish what this never puts in the
    # document.
    lines_before = preamble_runs(preamble, delimiter)
    form = Dialect(
        delimiter=delimiter,
        initial_space=spaced,
        escape=escaping,
        separator_line=bool(hinted),
        byte_order_mark=byte_order_mark,
        line_endings=runs_published,
        final_line_ending=_ended(body, size),
        end_of_file_mark=end_mark,
        preamble=lines_before,
        preamble_withheld=preamble_lines_holding_text(lines_before) > 0,
        header_quoting=header_rule,
        header_rows=tuple(header_rows),
        header_rows_quoting=metadata_rule,
        written_names=tuple(written),
        header_trailing_delimiter=header_trailing,
        rows_trailing_delimiter=rows_trailing,
        short_rows=short_rows,
        blank_lines=places_published,
        empty_rows_leading=leading_told,
        empty_rows_interior=interior_told,
        empty_rows_trailing=trailing_told,
        columns=tuple(column_forms),
        row_order=order,
        line_endings_spread=census_published,
        blank_lines_spread=spread_published,
    )
    return Survey(
        form=form,
        header=tuple(header),
        columns=columns,
        n_rows=n_rows,
        quoting_holds=tuple(holds),
        classified=tuple(classified),
        header_holds=header_held,
        header_rows_holds=metadata_held,
        short_vacuous=ends_empty == 0,
        malformed=malformed,
        escapes=escapes,
        initial_space_broken=spaces_broken,
        metadata_shape=metadata_shape,
        delimiter_tie=tie,
        every_blank_place=tuple(blanks),
        ending_census=census,
        blank_census=blank_census,
    )


def _without_rows(columns: "list[list[str]]", rows: "list[int]") -> "list[list[str]]":
    """The columns with the records at ``rows`` (ascending) taken out."""
    if not rows:
        return columns
    skip = [False for _row in range(len(columns[0]) if columns else 0)]
    for row in rows:
        skip[row] = True
    return [
        [column[row] for row in range(len(column)) if not skip[row]]
        for column in columns
    ]


def census_of(runs: "list[EndingRun] | tuple[EndingRun, ...]") -> "tuple[EndingRun, ...]":
    """How many lines end each way, in `ENDINGS` order, leaving out endings no line has."""
    counts = [0 for _name in ENDINGS]
    for run in runs:
        for index in range(len(ENDINGS)):
            if ENDINGS[index] == run.ending:
                counts[index] = counts[index] + run.lines
    return tuple(
        [
            EndingRun(ending=ENDINGS[index], lines=counts[index])
            for index in range(len(ENDINGS))
            if counts[index]
        ]
    )


def blank_census_of(
    places: "list[BlankPlace] | tuple[BlankPlace, ...]",
) -> "BlankSpread | None":
    """The blank lines counted: first place, last place, how many, what most hold."""
    if not places:
        return None
    total = 0
    held: dict[str, int] = {}
    order: list[str] = []
    for place in places:
        total = total + place.lines
        if place.text not in held:
            held[place.text] = 0
            order += [place.text]
        held[place.text] = held[place.text] + place.lines
    text = order[0]
    for found in order:
        if held[found] > held[text]:
            text = found
    return BlankSpread(
        first=places[0].after,
        last=places[len(places) - 1].after,
        lines=total,
        text=text,
    )


def spread_places(spread: BlankSpread) -> "tuple[BlankPlace, ...]":
    """Where a twin writes counted blank lines: evenly from the first place to the last.

    The k-th of n lines stands after ``first + k * (last - first) // (n - 1)``
    records, so a file with one blank line after each of its records --
    double spacing -- is written exactly as it was.
    """
    places: list[BlankPlace] = []
    span = spread.last - spread.first
    for index in range(spread.lines):
        after = spread.first
        if spread.lines > 1:
            after = spread.first + (index * span) // (spread.lines - 1)
        last = len(places) - 1
        if last >= 0 and places[last].after == after:
            places[last] = BlankPlace(after=after, lines=places[last].lines + 1, text=spread.text)
        else:
            places += [BlankPlace(after=after, lines=1, text=spread.text)]
    return tuple(places)


def spread_endings(census: "tuple[EndingRun, ...]") -> "list[str]":
    """Each line's ending, for counted line endings: the rarer spread evenly.

    The ending most lines have (the earlier in `ENDINGS` on a tie) ends
    every line that no rarer one takes. Each rarer ending, in `ENDINGS`
    order, takes its c lines at the middle of c equal stretches of the
    file, the next free line where that one is taken. Every ending is
    written on exactly as many lines as the census says.
    """
    total = 0
    most = 0
    for index in range(len(census)):
        total = total + census[index].lines
        if census[index].lines > census[most].lines:
            most = index
    if not census:
        return []
    endings = [census[most].ending for _line in range(total)]
    taken = [False for _line in range(total)]
    low = 0
    for index in range(len(census)):
        if index == most:
            continue
        count = census[index].lines
        cursor = 0
        for step in range(count):
            target = ((2 * step + 1) * total) // (2 * count)
            at = max(target, cursor)
            while at < total and taken[at]:
                at = at + 1
            if at >= total:
                while low < total and taken[low]:
                    low = low + 1
                at = low
            taken[at] = True
            endings[at] = census[index].ending
            cursor = at + 1
    return endings


def _spaces_broken(record: Record, spaced: bool) -> bool:
    """True when a comma-space reading skipped other than one space in a field."""
    if not spaced:
        return False
    for index in range(1, len(record.spaces)):
        if record.spaces[index] != 1:
            return True
    return False


def _ended(body: str, size: int) -> bool:
    """True when the text's last character ends a line."""
    found = _text(body)
    if not size:
        return False
    return found[size - 1] == _LF or found[size - 1] == _CR


def _blank(
    blanks: "list[BlankPlace]", after: int, text: str, shown: str
) -> None:
    """Count one blank line standing after ``after`` data records."""
    last = len(blanks) - 1
    if last >= 0 and blanks[last].after == after and blanks[last].text == text:
        blanks[last] = BlankPlace(after=after, lines=blanks[last].lines + 1, text=text)
        return
    # No cap here: every place is kept, and `survey` publishes them
    # counted where there are more than the cap.
    blanks += [BlankPlace(after=after, lines=1, text=text)]


def settle(
    text: str,
    encoding: str,
    byte_order_mark: bool,
    first_row_is_data: bool,
    shown: str,
    metadata_rows: int = 0,
    decimal_comma_columns: "tuple[str, ...]" = (),
    metadata_rows_confirmed: bool = False,
    declared_delimiter: str = "",
    small_cell_floor: int = 1,
) -> Survey:
    """The survey of a table, with every guess about its writing checked.

    Two guesses are made from the first records and held to the whole
    file here. A table guessed to be written comma-space whose fields do
    not all carry exactly one space is walked again without it, because
    reading it with the space skipped would have dropped spaces that are
    part of values. A table whose doubled-quote reading leaves text after
    a closing quote is walked again with backslash escapes, and that
    reading is kept only when it leaves none.
    """
    try:
        found = survey(
            text, encoding, byte_order_mark, first_row_is_data, shown,
            metadata_rows=metadata_rows,
            decimal_comma_columns=decimal_comma_columns,
            metadata_rows_confirmed=metadata_rows_confirmed,
            declared_delimiter=declared_delimiter,
            small_cell_floor=small_cell_floor,
        )
    except errors.ProfileError as refusal:
        # THE SUPPORTED ESCAPINGS ARE TRIED BEFORE A STRUCTURAL REFUSAL
        # IS PROPAGATED (review item CODEX-6). The doubled-quote reading
        # of a backslash-escaped file splits one field into several --
        # `"hello \"quoted, text\""` reads as three fields where the
        # header names two -- so the walk raised a ragged-rows refusal
        # and execution never reached the backslash retry below. The
        # file was readable all along, and removing the embedded comma
        # made the very same escaping work, which is what said the
        # refusal was about the reading and not about the file.
        try:
            other = survey(
                text, encoding, byte_order_mark, first_row_is_data, shown,
                None, ESCAPE_BACKSLASH, metadata_rows=metadata_rows,
                decimal_comma_columns=decimal_comma_columns,
                metadata_rows_confirmed=metadata_rows_confirmed,
                declared_delimiter=declared_delimiter,
                small_cell_floor=small_cell_floor,
            )
        except errors.ProfileError:
            raise refusal from None
        if other.malformed == 0:
            return other
        raise refusal from None
    if found.initial_space_broken:
        found = survey(
            text, encoding, byte_order_mark, first_row_is_data, shown, False,
            metadata_rows=metadata_rows,
            decimal_comma_columns=decimal_comma_columns,
            metadata_rows_confirmed=metadata_rows_confirmed,
            declared_delimiter=declared_delimiter,
            small_cell_floor=small_cell_floor,
        )
    if found.malformed and found.form.escape == ESCAPE_DOUBLED:
        try:
            other = survey(
                text,
                encoding,
                byte_order_mark,
                first_row_is_data,
                shown,
                found.form.initial_space,
                ESCAPE_BACKSLASH,
                metadata_rows=metadata_rows,
                decimal_comma_columns=decimal_comma_columns,
                metadata_rows_confirmed=metadata_rows_confirmed,
                declared_delimiter=declared_delimiter,
                small_cell_floor=small_cell_floor,
            )
        except errors.ProfileError:
            return found
        if other.malformed == 0:
            return other
    return found


# -- writing a twin ----------------------------------------------------


def written_field(
    cell: str,
    rule: str,
    form: Dialect,
    alone: bool,
    marked: bool = False,
) -> str:
    """One cell as the twin writes it, under one quoting rule of the form."""
    found = _text(cell)
    if rule == QUOTE_ALWAYS:
        quote = True
    elif rule == QUOTE_BARE:
        quote = marked or must_quote(
            found, form.delimiter, form.escape, form.initial_space, alone
        )
    else:
        quote = marked or needs_quoting(
            found, form.delimiter, form.escape, form.initial_space, alone
        )
    if not quote:
        return found
    body = ""
    for character in found:
        if form.escape == ESCAPE_BACKSLASH:
            if character == _QUOTE or character == _BACKSLASH:
                body = body + _BACKSLASH
        elif character == _QUOTE:
            body = body + _QUOTE
        body = body + character
    return f"{_QUOTE}{body}{_QUOTE}"


def _rule_for(column: ColumnForm, cell: str) -> str:
    """The quoting rule a column applies to one cell.

    A column whose four rules agree needs no class for the cell, which
    spares the numeric reading of every cell of an ordinary twin.
    """
    rules = column.quoting
    if rules[0] == rules[1] == rules[2] == rules[3]:
        return rules[0]
    return rules[_CLASS_PLACE[cell_class(cell)]]


def _padded(cell: str, column: ColumnForm) -> str:
    """A cell padded with spaces to its column's width, where it is shorter."""
    found = _text(cell)
    if not column.pad_side or len(found) >= column.pad_width:
        return found
    spaces = _SPACE * (column.pad_width - len(found))
    if column.pad_side == PAD_LEFT:
        return spaces + found
    return found + spaces


def _joined(parts: "list[str]", form: Dialect) -> str:
    """Fields put on one line with the form's delimiter."""
    separator = form.delimiter + (_SPACE if form.initial_space else "")
    line = ""
    for index in range(len(parts)):
        if index:
            line = line + separator
        line = line + parts[index]
    return line


def header_line(names: "tuple[str, ...]", form: Dialect) -> str:
    """The header record as the twin writes it, without its line ending."""
    shown = list(names)
    for written in form.written_names:
        if 1 <= written.position <= len(shown):
            shown[written.position - 1] = written.text
    alone = len(shown) == 1
    parts: list[str] = []
    for index in range(len(shown)):
        cell = _text(shown[index])
        marked = index == 0 and cell[:1] == _MARK
        parts += [written_field(cell, form.header_quoting, form, alone, marked)]
    line = _joined(parts, form)
    if form.header_trailing_delimiter:
        line = line + form.delimiter
    return line


def data_line(cells: "tuple[str, ...]", form: Dialect) -> str:
    """One data record as the twin writes it, without its line ending."""
    width = len(cells)
    kept = width
    if form.short_rows:
        while kept > 1 and cells[kept - 1] == "":
            kept = kept - 1
    alone = width == 1
    parts: list[str] = []
    for index in range(kept):
        column = form.columns[index] if index < len(form.columns) else plain_column()
        cell = _padded(cells[index], column)
        rule = _rule_for(column, cell)
        parts += [written_field(cell, rule, form, alone)]
    line = _joined(parts, form)
    if form.rows_trailing_delimiter:
        line = line + form.delimiter
    return line


def twin_text(
    names: "tuple[str, ...]",
    rows: "tuple[tuple[str, ...], ...]",
    write_header: bool,
    form: Dialect,
) -> str:
    """The whole twin in its source's written form, as text.

    Guarantees:

    - Inputs: the column names, the rows in their final order, whether
      a header is written, and the form.
    - Determinism: a fixed function of those, on every platform; the
      line endings are written into the text, so the caller writes it
      without translating any.
    - Errors raised: none.
    - Boundary: nothing is read and nothing is written.

    The lines are written in file order: the separator hint, the
    preamble, the header, the metadata rows, then the data records with
    the blank lines standing where the form places them. Each line takes
    the next ending from the form's runs; the last takes none where the
    source's last line had none. A byte-order mark leads where the form
    has one, and the end-of-file mark follows where it has one.
    """
    lines: list[str] = []
    if form.separator_line:
        lines += ["sep=" + form.delimiter]
    for before in form.preamble:
        for _line in range(before.lines):
            lines += [preamble_line(before)]
    if write_header:
        lines += [header_line(names, form)]
    for row in form.header_rows:
        alone = len(row) == 1
        parts = [
            written_field(cell, form.header_rows_quoting, form, alone)
            for cell in row
        ]
        lines += [_joined(parts, form)]
    blank_places = form.blank_lines
    if form.blank_lines_spread is not None:
        blank_places = spread_places(form.blank_lines_spread)
    blank_at = 0
    for index in range(len(rows)):
        while blank_at < len(blank_places) and blank_places[blank_at].after == index:
            place = blank_places[blank_at]
            for _line in range(place.lines):
                lines += [place.text]
            blank_at = blank_at + 1
        lines += [data_line(rows[index], form)]
    while blank_at < len(blank_places):
        place = blank_places[blank_at]
        for _line in range(place.lines):
            lines += [place.text]
        blank_at = blank_at + 1
    endings: list[str] = []
    for run in form.line_endings:
        for _line in range(run.lines):
            endings += [ENDING_TEXT[run.ending]]
    if form.line_endings_spread:
        endings = [ENDING_TEXT[word] for word in spread_endings(form.line_endings_spread)]
    text = _MARK if form.byte_order_mark else ""
    for index in range(len(lines)):
        text = text + lines[index]
        if index < len(endings):
            text = text + endings[index]
        elif index < len(lines) - 1 or form.final_line_ending:
            text = text + _LF
    if form.end_of_file_mark:
        text = text + _END_OF_FILE
    return text


# -- arranging a twin's rows -------------------------------------------


def sequence_cells(start: int, n_rows: int) -> "list[str]":
    """The row sequence as cells: start, start + 1, ... in row order."""
    return [f"{start + index}" for index in range(n_rows)]


def arranged(
    columns: "list[tuple[str, ...]]", form: Dialect, n_rows: int
) -> "list[tuple[str, ...]]":
    """A twin's columns with its rows placed where the form says they stand.

    Guarantees:

    - Inputs: the finished columns, the form, the number of rows.
    - What moves: WHOLE ROWS, when the form names a sorted column --
      every column is permuted together, so no column's cells and no
      pair of columns' joint cells change -- and single cells WITHIN one
      column, to put the published number of all-empty records in their
      places and to leave no other record empty. Moving cells within a
      column changes no fact of that column, and the twin carries no
      structure between columns for such a move to break (CLAUDE.md,
      what the twin carries today). A row-sequence column is written in
      place last, so it reads 0, 1, 2, ... or 1, 2, 3, ... whatever
      moved.
    - Determinism: no random draw; a fixed function of the inputs.
    - Errors raised: none.
    """
    width = len(columns)
    if not width or not n_rows:
        return columns
    grid = [list(column) for column in columns]
    order = form.row_order
    empties = form.empty_rows_leading + form.empty_rows_interior + form.empty_rows_trailing
    targets = [False for _row in range(n_rows)]
    if width >= 2 and (empties or not order.column):
        _place_empty_rows(grid, form, n_rows)
        targets = _empty_targets(form, n_rows)
    if order.column and order.column <= width:
        # The records holding nothing stay where they were placed, and
        # the others are sorted into the rows around them.
        free = [row for row in range(n_rows) if not targets[row]]
        key = grid[order.column - 1]
        placed = _permutation([key[row] for row in free], order, len(free))
        for place in range(width):
            column = grid[place]
            moved = list(column)
            for index in range(len(free)):
                moved[free[index]] = column[free[placed[index]]]
            grid[place] = moved
    for index in range(width):
        if index < len(form.columns) and form.columns[index].sequence_start >= 0:
            grid[index] = sequence_cells(form.columns[index].sequence_start, n_rows)
    return [tuple(column) for column in grid]


def _permutation(keys: "list[str]", order: RowOrder, n_rows: int) -> "list[int]":
    """The rows in the order the form's sort key puts them, ties kept in place.

    A cell with no number under the number collation goes last. The
    sort is stable: rows the key cannot tell apart keep the order the
    generator gave them.
    """
    if order.collation in (COLLATION_NUMBER, COLLATION_DECIMAL_COMMA):
        numbered: list[tuple[int, float, int]] = []
        for index in range(n_rows):
            cell_text = _text(keys[index])
            if order.collation == COLLATION_DECIMAL_COMMA:
                # THE TWIN SORTS THE WAY THE DESCRIPTION SAYS THE COLUMN
                # IS WRITTEN. The twin writes this column's numbers with
                # a comma, so sorting its own cells under the ordinary
                # grammar would put `10,0` before `9,9` and hand back a
                # column the description calls ascending and is not.
                cell_text = parsing.written_with_a_decimal_comma(cell_text)
            number = parsing.parse_number(cell_text)
            if number is None:
                numbered += [(1, 0.0, index)]
            elif order.direction == DESCENDING:
                numbered += [(0, -number, index)]
            else:
                numbered += [(0, number, index)]
        return [entry[2] for entry in sorted(numbered)]
    lettered: list[tuple[str, int]] = []
    for index in range(n_rows):
        cell = _text(keys[index])
        lettered += [(cell, index if order.direction == ASCENDING else -index)]
    placed = sorted(lettered)
    if order.direction == DESCENDING:
        placed = list(reversed(placed))
    return [abs(entry[1]) for entry in placed]


def _empty_targets(form: Dialect, n_rows: int) -> "list[bool]":
    """Which rows the form's all-empty records stand in."""
    targets = [False for _row in range(n_rows)]
    leading = min(form.empty_rows_leading, n_rows)
    for row in range(leading):
        targets[row] = True
    trailing = min(form.empty_rows_trailing, n_rows - leading)
    for row in range(n_rows - trailing, n_rows):
        targets[row] = True
    middle = n_rows - leading - trailing
    interior = min(form.empty_rows_interior, middle)
    for step in range(interior):
        row = leading + ((step + 1) * middle) // (interior + 1)
        while targets[row] and row < n_rows - trailing - 1:
            row = row + 1
        targets[row] = True
    return targets


def _place_empty_rows(grid: "list[list[str]]", form: Dialect, n_rows: int) -> None:
    """Swap cells within columns so exactly the target rows are all empty.

    First every target row is emptied: a cell holding something is
    exchanged for an empty cell of the same column from a row that is not
    a target. Then every other row left with nothing in it is given a
    cell: a cell holding something is exchanged into it from a row that
    keeps something else. Both walks are linear in the cells they touch.
    """
    width = len(grid)
    targets = _empty_targets(form, n_rows)
    for place in range(width):
        column = grid[place]
        donor = 0
        for row in range(n_rows):
            if not targets[row] or _holds_nothing(column[row]):
                continue
            while donor < n_rows and (
                targets[donor] or not _holds_nothing(column[donor])
            ):
                donor = donor + 1
            if donor >= n_rows:
                break
            column[row], column[donor] = column[donor], column[row]
            donor = donor + 1
    filled = [0 for _row in range(n_rows)]
    for place in range(width):
        column = grid[place]
        for row in range(n_rows):
            if not _holds_nothing(column[row]):
                filled[row] = filled[row] + 1
    giver = [0 for _place in range(width)]
    for row in range(n_rows):
        if targets[row] or filled[row]:
            continue
        for place in range(width):
            column = grid[place]
            source = giver[place]
            while source < n_rows and (
                targets[source]
                or _holds_nothing(column[source])
                or filled[source] < 2
            ):
                source = source + 1
            giver[place] = source
            if source >= n_rows:
                continue
            column[row], column[source] = column[source], column[row]
            filled[row] = filled[row] + 1
            filled[source] = filled[source] - 1
            break

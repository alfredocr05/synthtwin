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
anybody, so it is published only at a smallest group of one, where every
label is already published at its own count; above that it is withheld
and a stand-in of the same shape is written (`withheld_line`).

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
COLLATIONS = (COLLATION_NUMBER, COLLATION_TEXT)
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
    preamble: "tuple[str, ...]"
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
    total = n_rows + len(form.preamble) + len(form.header_rows)
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
        "preamble": list(form.preamble),
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


def withheld_line(text: str) -> str:
    """The stand-in written for a withheld preamble line.

    The punctuation and spaces it began with are kept -- `# ` and `*** `
    are how code skips such lines -- and everything from its first letter
    or digit is replaced. A blank line stays blank.
    """
    found = _text(text)
    if not found or _only_spaces_and_tabs(found):
        return found
    kept = ""
    for character in found:
        if _is_letter_or_digit(character):
            break
        kept = kept + character
    return kept + WITHHELD_LINE


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

    The validator's reading of a checked file (plan P4-D75, repair of
    landing 2b.9). A description published as Latin-1 or Windows-1252
    publishes every label as that encoding reads it, so a checked file is
    read the same way whenever its bytes decode there and carry no UTF-8
    or UTF-16 mark (contract FD3 gives such a description none). Reading
    it by detection instead would read a twin whose non-UTF-8 bytes all
    stood in cells written as stand-ins -- and which is therefore valid
    UTF-8 -- as UTF-8, and find every accented label changed. Every other
    case is `decoded`'s.
    """
    if not isinstance(data, bytes):
        raise TypeError("internal check: a file's bytes were not bytes")
    marked = data[:3] == b"\xef\xbb\xbf" or data[:2] == b"\xff\xfe" or data[:2] == b"\xfe\xff"
    if encoding in FALLBACK_ENCODINGS and not marked:
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
    return len(record.fields) == 1 and _holds(raw, _SPACE)


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


def detected_delimiter(text: str, at: int) -> str:
    """The delimiter a table is written with, from its first records.

    Each candidate reads the first records; the one under which the most
    records share one width of two or more fields wins, a wider table
    breaking a tie and the order of `DELIMITERS` breaking a tie of both.
    A table no candidate reads as two or more fields is one column, and
    its delimiter is the comma. The full walk in `survey` then holds
    every record to the width this chose, so a table that only looked
    delimited in its first records is refused as ragged, never read
    wrongly.

    A TIE OF BOTH IS DECIDED BY THE CELLS FIRST (repair of landing 2b.9).
    A European export whose names hold a comma (`Gewicht, kg`) and whose
    every number carries one decimal comma reads as three fields a
    record under the comma and under the semicolon alike, and the order
    of `DELIMITERS` took the comma -- `41943;91` and `0;166` as cells.
    So on a tie the candidate under whose reading more cells read as
    numbers, with a point or with a decimal comma, wins; the order of
    `DELIMITERS` decides only where that ties too.
    """
    chosen = ","
    best_share = 0.0
    best_width = 0
    best_numbers = -1
    for candidate in DELIMITERS:
        sample = records(text, candidate, ESCAPE_DOUBLED, False, at, _SAMPLE_RECORDS)
        share, width = _width_share(sample)
        if width < 2:
            continue
        # THE TABLE'S FIRST RECORD HAS THE TABLE'S WIDTH. A one-column
        # table of `100|30` cells reads as two fields a row under the
        # vertical bar, and only its first record -- the column's name,
        # one field -- says the bar is not its delimiter.
        opening = 0
        while opening < len(sample) and _leads_the_table(sample[opening]):
            opening = opening + 1
        if opening < len(sample) and len(sample[opening].fields) != width:
            continue
        numbers = -1
        if share == best_share and width == best_width:
            numbers = _numbers_read(sample)
            if best_numbers < 0:
                best_numbers = _numbers_read(
                    records(text, chosen, ESCAPE_DOUBLED, False, at, _SAMPLE_RECORDS)
                )
        if (
            share > best_share
            or (share == best_share and width > best_width)
            or (share == best_share and width == best_width and numbers > best_numbers)
        ):
            chosen = candidate
            best_share = share
            best_width = width
            best_numbers = numbers
    return chosen


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


def named_columns(header: "tuple[str, ...]") -> "tuple[str, ...]":
    """The name each column is given from the header as it is written.

    A header cell that is blank, or holds only spaces, is named
    `Unnamed: N` for its place counted from 0; a cell repeating an
    earlier name gets `.1`, `.2`, ... after it. A made-up name is never
    one another column already has or is written with, so it moves on to
    the next number instead. That is what pandas names the same columns
    in the common cases, so code written against the twin's names reads
    the real table's.
    """
    written: dict[str, bool] = {}
    for cell in header:
        found = _text(cell)
        if parsing.trimmed(found):
            written[found] = True
    taken: dict[str, bool] = {}
    named: list[str] = []
    for index in range(len(header)):
        cell = _text(header[index])
        base = cell if parsing.trimmed(cell) else f"Unnamed: {index}"
        name = base
        own = parsing.trimmed(cell) and base == cell
        if name in taken or (not own and name in written):
            count = 1
            name = f"{base}.{count}"
            while name in taken or name in written:
                count = count + 1
                name = f"{base}.{count}"
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
        if collation == COLLATION_NUMBER:
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


def row_order_of(
    columns: "list[list[str]]", sequences: "list[int]", n_rows: int
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
        for collation in COLLATIONS:
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
                if row < len(column) and column[row] != "":
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
    delimiter = hinted if hinted else detected_delimiter(body, at)
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
        if (
            len(header) >= 2
            and first is not None
            and second is not None
            and len(first.fields) == len(header)
            and len(second.fields) == len(header)
            and _is_import_row(second.fields)
        ):
            for _row in range(2):
                found = _take(stream)
                if found is None:
                    break
                header_rows += [tuple(found.fields)]
                header_row_flags += [bool(flag) for flag in found.quoted]
                malformed = malformed + found.malformed
                escapes = escapes + found.escapes
                _add_ending(walk, found.ending, shown)

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
        if (
            len(fields) == 1
            and width >= 2
            and not found.quoted[0]
            and _only_spaces_and_tabs(fields[0])
        ):
            _add_ending(walk, found.ending, shown)
            _blank(blanks, n_rows, fields[0], shown)
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
                if value:
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
    order = row_order_of(_without_rows(columns, empty_rows), sequences, n_rows - len(empty_rows))
    census = census_of(walk.runs)
    blank_census = blank_census_of(blanks)
    runs_published: "tuple[EndingRun, ...]" = tuple(walk.runs)
    census_published: "tuple[EndingRun, ...]" = ()
    if len(walk.runs) > MAXIMUM_ENDING_RUNS:
        runs_published = ()
        census_published = census
    places_published: "tuple[BlankPlace, ...]" = tuple(blanks)
    spread_published: "BlankSpread | None" = None
    if len(blanks) > MAXIMUM_BLANK_PLACES:
        places_published = ()
        spread_published = blank_census
    form = Dialect(
        delimiter=delimiter,
        initial_space=spaced,
        escape=escaping,
        separator_line=bool(hinted),
        byte_order_mark=byte_order_mark,
        line_endings=runs_published,
        final_line_ending=_ended(body, size),
        end_of_file_mark=end_mark,
        preamble=tuple(preamble),
        preamble_withheld=False,
        header_quoting=header_rule,
        header_rows=tuple(header_rows),
        header_rows_quoting=metadata_rule,
        written_names=tuple(written),
        header_trailing_delimiter=header_trailing,
        rows_trailing_delimiter=rows_trailing,
        short_rows=short_rows,
        blank_lines=places_published,
        empty_rows_leading=leading,
        empty_rows_interior=len(empty_rows) - leading - trailing,
        empty_rows_trailing=trailing,
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
    found = survey(text, encoding, byte_order_mark, first_row_is_data, shown)
    if found.initial_space_broken:
        found = survey(
            text, encoding, byte_order_mark, first_row_is_data, shown, False
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
    for line in form.preamble:
        lines += [line]
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
    if order.collation == COLLATION_NUMBER:
        numbered: list[tuple[int, float, int]] = []
        for index in range(n_rows):
            number = parsing.parse_number(_text(keys[index]))
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
            if not targets[row] or column[row] == "":
                continue
            while donor < n_rows and (targets[donor] or column[donor] != ""):
                donor = donor + 1
            if donor >= n_rows:
                break
            column[row], column[donor] = column[donor], column[row]
            donor = donor + 1
    filled = [0 for _row in range(n_rows)]
    for place in range(width):
        column = grid[place]
        for row in range(n_rows):
            if column[row] != "":
                filled[row] = filled[row] + 1
    giver = [0 for _place in range(width)]
    for row in range(n_rows):
        if targets[row] or filled[row]:
            continue
        for place in range(width):
            column = grid[place]
            source = giver[place]
            while source < n_rows and (
                targets[source] or column[source] == "" or filled[source] < 2
            ):
                source = source + 1
            giver[place] = source
            if source >= n_rows:
                continue
            column[row], column[source] = column[source], column[row]
            filled[row] = filled[row] + 1
            filled[source] = filled[source] - 1
            break

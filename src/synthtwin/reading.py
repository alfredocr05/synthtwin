"""Reading the user's table: the only code that opens real data (P1-D3).

The charter rule is that one module reads the real table and nothing
else ever does. This is that module. Everything downstream receives
already-read text and never sees where it came from.

THE TWO PASSES, AND WHAT THEY NOW PROVE
=======================================

The file is read TWICE, by two different readers, and the two results
must agree ABOUT EVERY VALUE -- not, as until review round 1, about the
number of rows and columns:

1. **The reading pass** (`csv` from the standard library) streams the
   file one row at a time and is AUTHORITATIVE. It establishes the
   encoding, the header, the value count of every row, the number of
   data rows, and every value. It never holds more than one row on top
   of the columns it is filling, so it adds nothing to the memory the
   answer itself needs.
2. **The checking pass** (`pandas.read_csv`) reads the same file
   independently and is compared, cell by cell, against what the first
   pass produced: the column names it found, the shape, and every
   single value. The first difference is a refusal naming the row and
   the column.

Round 1 of the review showed why the old counts-only comparison was
worth nothing. Three reproductions, all of which now refuse:

* a file rewritten between the passes with the same shape was accepted
  with the OLD header and the NEW values, because the header names were
  handed to the second reader instead of being read from it and
  compared. The second reader is no longer told the names; it is asked
  for them;
* a zero byte in data row 6 made pandas' C reader stop the value at the
  zero byte while the standard reader kept it whole. Equal counts, one
  truncated value. Zero bytes are now refused wherever they occur, not
  only in the first five rows;
* for the bytes ``c0,c1\\n\\r,B\\nz,w\\n`` the standard reader yields
  ``["", "B"]`` and pandas' C reader yields ``["B", ""]``. Values move
  BETWEEN columns with no zero byte anywhere and both counts equal, so
  two columns were profiled wrongly and nothing looked unusual. This is
  a pure parser disagreement: no arrangement that binds both readers to
  the same bytes can catch it, which is why the repair is the value
  comparison and not a byte-binding trick.

What the comparison costs was measured rather than guessed. Over 3,000
well-formed CSV files (both line endings, quoted commas, quoted line
breaks, quoted quotation marks, empty values) the two readers never once
disagreed, so the check is silent on ordinary files. Over 20,000
adversarial byte strings, the same 20,000 for both readers: the
arrangement this replaces accepted 417 of them and published values the
standard reader never saw in 6 of those; this one accepts 409 and
publishes a value the standard reader never saw in none. Every file it
now refuses and the old one accepted holds a stray carriage return, an
unclosed quotation mark, or a zero byte -- a file whose meaning is not
settled, which is where synthtwin must stop.

Why the standard reader is the authoritative one. It reports the value
count of every row exactly, which is the one thing pandas will not do
without a callback the offline policy forbids: pandas silently pads a
short row out to the header's width, so under a three-column header the
row ``4,5`` becomes ``4``, ``5`` and an empty third value that cannot be
told apart from a genuinely empty cell. Being authoritative as well as
structural also means padding can never reach the profile even if the
comparison were removed, and it costs less memory than the old
arrangement (measurements in `read_table`).

THE HEADER DECISION
===================

The first row is either the column names or the first record, and
guessing wrong is not a small error: it drops a whole person from every
statistic and publishes that person's values as schema text, outside
every suppression rule. Review round 1 read this headerless file with
column names ``P001`` and ``34`` and five rows instead of six.

The decision is now explicit, and it is made from the SHAPE of each
column's values rather than from the first row alone. For every column
the reader computes the signature of a value -- each ASCII digit becomes
``9``, each ASCII letter becomes ``A``, everything else stands for
itself, so ``P001`` becomes ``A999`` and ``2024-03-17`` becomes
``9999-99-99`` -- and asks two questions of the column's data values:

* **Does the first row's value CONTRADICT this column?** It does when
  every data value of the column shares one signature that contains a
  digit and the first row's value has a different signature, or when
  every data value reads as a number and the first row's value does
  not. A record cannot contradict its own column, so one contradiction
  anywhere settles it: the first row is the column names.
* **Does it FIT this column exactly?** It does when the column's data
  values all share one signature and the first row's value has that
  same signature. The fit is STRONG when the signature carries both a
  digit and something else (``A999``, ``AAAA-9``, ``9999-99-99``): that
  is what a code, an identifier or a date looks like, and a column name
  almost never has the shape of one. It is WEAK when the signature is
  all digits (``9999``), because plain numbers are everywhere and a
  column headed ``2019`` over four-digit values is an ordinary table.

The verdict:

* any contradiction -> the first row is the column names, accepted
  without a word;
* otherwise a strong fit anywhere, or a fit in every column ->
  synthtwin cannot tell, and REFUSES, naming the two ways to say which
  it is: ``--first-row names`` or ``--first-row data``. With
  ``--first-row data`` the columns are named ``column_1``, ``column_2``,
  ... and every record is kept, so nothing is lost either way;
* otherwise the first row is the column names.

The rule sketched at round 1 was tested against the same nine shapes and
is not this one: it refused ordinary pivoted year tables
(``region,2019,2020,2021``) and missed headerless files whose values are
all text. This one accepts the pivoted table (the year headers
contradict their one-digit and two-digit columns, and where they do not,
no column fits) and refuses ``P001,34`` and ``pa-001,site-1`` alike.

What it still cannot see is stated where the promise is, in
`read_table`: a headerless file whose columns have neither a shared
signature nor an all-numeric first row is accepted as headed.

ENCODINGS AND BYTE-ORDER MARKS
==============================

UTF-8 first (accepting a byte-order mark), then one documented fallback,
Latin-1. Latin-1 can decode any byte sequence, so a file that is really
UTF-16, UTF-32, or not text at all would come through as nonsense rather
than as an error.

Byte-order marks are matched as COMPLETE byte sequences. Latin-1 maps
each of the 256 bytes to the code point of the same number and back
again, so after a Latin-1 fallback the decoded characters ARE the file's
bytes, one for one, and comparing the first characters against
``\\xff\\xfe`` compares the first bytes. Review round 1 found a valid
Latin-1 header beginning with the single byte 0xFF -- an ordinary
``\\xff`` character -- refused as UTF-16 because a lone character was
being read as a mark; a mark is two or four bytes and is now required to
be all of them.

Reading a real byte prefix instead would be the obvious way to do this,
and it is not available: the offline policy accepts no method call on an
open file object (`handle.read(4)` is rejected by the scanner), and the
one accepted way to obtain bytes from a path, `Path.read_bytes`, reads
the whole file. The Latin-1 identity is exact, so nothing is lost.

IMPORTS
=======

Imports here stay within the allowlist (plan D6.2 with the Phase 1
additions in P1-D10): csv, pandas, pathlib, dataclasses, and this
package's own modules. `pandas.read_csv` is network-capable -- it would
open a URL if it were handed one -- and it is fenced, not trusted: the
only path that reaches it has passed `validate_local_path`, inside the
same function as the call, which rejects URL forms lexically before any
filesystem call (P1-D2.1, and SECURITY.md states it in the same terms).
"""

import csv
import dataclasses
import pathlib

import pandas

from synthtwin import errors, parsing
from synthtwin.paths import validate_local_path

# The per-value size the standard reader will accept while a table is
# being read. The default (about 130,000 characters) is too small for a
# free-text column of long notes; ten million characters is far beyond
# any real cell and still small enough that a file with an unclosed
# quotation mark is refused rather than read to its end. The previous
# value is restored afterwards, because this setting belongs to the
# whole program, not to us.
FIELD_SIZE_LIMIT = 10_000_000

_PRIMARY_ENCODING = "utf-8-sig"
_FALLBACK_ENCODING = "latin-1"

# How many wrong-length rows are named in a refusal message.
_MAX_REPORTED_OFFENDERS = 3

# What the caller may say about the first row. AUTOMATIC is the default
# and is the only one that can end in the ambiguity refusal.
FIRST_ROW_AUTOMATIC = "auto"
FIRST_ROW_NAMES = "names"
FIRST_ROW_DATA = "data"

# Where a Table's column names came from.
HEADER_FROM_FILE = "file"
HEADER_GENERATED = "generated"

# The complete byte-order marks, written as the Latin-1 characters that
# ARE those bytes (see the module docstring). The four-byte UTF-32 marks
# come first so that a UTF-32 file is never reported by its two-byte
# prefix. The big-endian UTF-32 mark begins with two zero bytes and is
# in practice caught by the zero-byte check before this one runs; it is
# listed so the set is the complete one rather than the reachable one.
_BYTE_ORDER_MARKS = (
    "\x00\x00\xfe\xff",
    "\xff\xfe\x00\x00",
    "\xfe\xff",
    "\xff\xfe",
)

# What one column's data values say about the first row's value in that
# column.
_CONTRADICTS = "contradicts"
_FITS_STRONGLY = "fits-strongly"
_FITS_WEAKLY = "fits-weakly"
_SAYS_NOTHING = "says-nothing"


@dataclasses.dataclass(frozen=True)
class Table:
    """One table read from disk, every value still exactly as written.

    ``column_names`` is the header row in source order; ``columns``
    holds one list of text values per column, in the same order;
    ``n_rows`` is the number of data rows; ``encoding`` names the
    encoding that succeeded; ``used_fallback_encoding`` records whether
    that was the fallback rather than UTF-8; and ``header_source`` is
    HEADER_FROM_FILE when the names were read from the file's first row
    or HEADER_GENERATED when the caller said the first row was data and
    the names were made up (``column_1``, ``column_2``, ...). Downstream
    code that shows column names to a person must say which of the two
    it is looking at.
    """

    column_names: list[str]
    columns: list[list[str]]
    n_rows: int
    encoding: str
    used_fallback_encoding: bool
    header_source: str


@dataclasses.dataclass(frozen=True)
class _Reading:
    """What the authoritative pass established about a file."""

    column_names: list[str]
    columns: list[list[str]]
    n_rows: int
    encoding: str
    used_fallback_encoding: bool
    header_source: str


def _has_zero_byte(text: str) -> bool:
    """True when ``text`` contains a zero byte (a NUL character)."""
    if not isinstance(text, str):
        raise TypeError("internal check: a cell value was not text")
    return "\x00" in text


def _starts_with_a_byte_order_mark(text: str) -> bool:
    """True when ``text`` begins with a COMPLETE byte-order mark.

    ``text`` is a Latin-1 decoding, so its characters are the file's
    bytes one for one (module docstring). A lone 0xFF or 0xFE byte is an
    ordinary Latin-1 character and is NOT a mark: refusing one was
    review item P1-R1-F18.
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a header name was not text")
    for mark in _BYTE_ORDER_MARKS:
        if text[: len(mark)] == mark:
            return True
    return False


def _signature(text: str) -> str:
    """The shape of one value: digits become 9, ASCII letters become A.

    Everything else stands for itself, so ``P001`` becomes ``A999``,
    ``site-1`` becomes ``AAAA-9`` and ``2024-03-17`` becomes
    ``9999-99-99``. Two values share a signature exactly when they have
    the same length and, at every position, a digit faces a digit, an
    ASCII letter faces an ASCII letter, and anything else faces the same
    character. Nothing here depends on a locale.
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a cell value was not text")
    out = ""
    for character in text:
        if "0" <= character <= "9":
            out = out + "9"
        elif ("a" <= character <= "z") or ("A" <= character <= "Z"):
            out = out + "A"
        else:
            out = out + character
    return out


def _matches_signature(text: str, signature: str) -> bool:
    """True when ``text`` has exactly the shape ``signature`` describes.

    The same relation `_signature` defines, decided without building a
    string: the length settles most values at once, and the first
    position that disagrees ends the comparison. On a table of 200,000
    rows that is the difference between a quarter of a second and a
    tenth of one.
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a cell value was not text")
    if not isinstance(signature, str):
        raise TypeError("internal check: a signature was not text")
    if len(text) != len(signature):
        return False
    for index in range(len(text)):
        character = text[index]
        marker = signature[index]
        if marker == "9":
            if not ("0" <= character <= "9"):
                return False
        elif marker == "A":
            if not (("a" <= character <= "z") or ("A" <= character <= "Z")):
                return False
        elif character != marker:
            return False
    return True


def _shared_signature(values: list[str]) -> "str | None":
    """The one signature every value in ``values`` has, or None.

    Returns None for an empty list and for any column whose values do
    not all have the same shape.
    """
    if not values:
        return None
    first = _signature(f"{values[0]}")
    for value in values:
        if not _matches_signature(f"{value}", first):
            return None
    return first


def _every_value_is_a_number(values: list[str]) -> bool:
    """True when every value reads as a number (or as one out of range)."""
    if not values:
        return False
    for value in values:
        if parsing.classify_number(f"{value}") == parsing.NOT_A_NUMBER:
            return False
    return True


def _class_signature(text: str) -> str:
    """The shape of one value with runs of one kind collapsed to one mark.

    ``P001`` and ``P12345`` both become ``A9``; ``7`` and ``12`` both
    become ``9``; ``region`` becomes ``A`` and ``r1`` becomes ``A9``.
    Only digits and ASCII letters collapse; every other character
    stands for itself and repeats of it are kept, so ``a--b`` becomes
    ``A--A``.
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a cell value was not text")
    out = ""
    previous = ""
    for character in text:
        if "0" <= character <= "9":
            marker = "9"
        elif ("a" <= character <= "z") or ("A" <= character <= "Z"):
            marker = "A"
        else:
            marker = character
            previous = ""
            out = out + marker
            continue
        if marker != previous:
            out = out + marker
        previous = marker
    return out


def _shared_class_signature(values: list[str]) -> "str | None":
    """The one class signature every value in ``values`` has, or None."""
    if not values:
        return None
    first = _class_signature(f"{values[0]}")
    for value in values:
        if _class_signature(f"{value}") != first:
            return None
    return first


def _shape_verdict(name: str, values: list[str]) -> str:
    """What one column's SHAPE says about the first row's value in it.

    A CONTRADICTION is decided on the class signature, which ignores how
    LONG a run of digits or letters is. Deciding it on the exact
    signature was wrong: an ordinary record can differ from its own
    column in length alone -- ``7`` above ``12``, ``13``, ``14`` -- and
    reading that as proof of a header dropped the record.
    """
    shared_class = _shared_class_signature(values)
    if (
        shared_class is not None
        and "9" in shared_class
        and _class_signature(f"{name}") != shared_class
    ):
        return _CONTRADICTS
    shared = _shared_signature(values)
    if shared is None:
        return _SAYS_NOTHING
    digits = "9" in shared
    if not _matches_signature(f"{name}", shared):
        return _SAYS_NOTHING
    if not digits:
        return _SAYS_NOTHING
    if shared == "9" * len(shared):
        return _FITS_WEAKLY
    return _FITS_STRONGLY


def _numeric_fit(name: str, values: list[str]) -> bool:
    """True when the first row's value is one of this column's own numbers.

    Every data value reads as a number, the first row's value reads as a
    number too, and that number is not something only a label could be:
    it either lies inside the range the column's own values cover or is
    written in the same shape as one of them. A column of years headed
    ``2019`` over the values 1, 2 and 3 is a label above its column; the
    value 140 above 99, 20, 7, 101 and 3 is a record among its own kind.

    The column is read once. That matters: this is the only question
    here that touches every value, and it is asked only of a column
    whose first-row value is itself a number, which is rare.
    """
    if parsing.classify_number(f"{name}") == parsing.NOT_A_NUMBER:
        return False
    if not values:
        return False
    wanted = _signature(f"{name}")
    mine = parsing.parse_number(f"{name}")
    matched = False
    lowest = None
    highest = None
    for value in values:
        text = f"{value}"
        if parsing.classify_number(text) == parsing.NOT_A_NUMBER:
            return False
        if not matched and _matches_signature(text, wanted):
            matched = True
        parsed = parsing.parse_number(text)
        if parsed is None:
            continue
        if lowest is None or parsed < lowest:
            lowest = parsed
        if highest is None or parsed > highest:
            highest = parsed
    if matched:
        return True
    if mine is None or lowest is None or highest is None:
        return False
    return lowest <= mine <= highest


def _numbers_contradict(name: str, values: list[str]) -> bool:
    """True when a column of numbers is headed by something that is not one.

    The cheap half of the test comes first on purpose: reading every
    value of a numeric column is the most expensive question this
    module asks, and it is worth asking only when the first row's value
    is not a number to begin with.
    """
    if parsing.classify_number(f"{name}") != parsing.NOT_A_NUMBER:
        return False
    return _every_value_is_a_number(values)


def _first_row_is_ambiguous(header: list[str], columns: list[list[str]]) -> bool:
    """True when the first row could equally be names or a record.

    The rule and the reasoning behind each clause are in the module
    docstring. One contradiction settles the question; otherwise a
    strong fit anywhere, or a fit in every column, means synthtwin must
    ask rather than choose.

    Both kinds of contradiction are tested before any fit is looked at,
    and the cheaper kind first: a shape is usually decided by the
    lengths of a column's values alone, while reading every value of a
    column as a number is the most expensive thing this module does. A
    table whose shapes already decide the question never runs the
    second test at all.
    """
    fits: list[str] = []
    for index in range(len(header)):
        verdict = _shape_verdict(header[index], columns[index])
        if verdict == _CONTRADICTS:
            return False
        fits = fits + [verdict]
    for index in range(len(header)):
        if _numbers_contradict(header[index], columns[index]):
            return False
    strengthened: list[str] = []
    for index in range(len(header)):
        verdict = fits[index]
        if verdict != _FITS_STRONGLY and _numeric_fit(
            header[index], columns[index]
        ):
            verdict = _FITS_STRONGLY
        strengthened = strengthened + [verdict]
    for verdict in strengthened:
        if verdict == _FITS_STRONGLY:
            return True
    for verdict in strengthened:
        if verdict == _SAYS_NOTHING:
            return False
    return True


def _generated_column_names(width: int) -> list[str]:
    """Names for a table whose first row the caller said was data."""
    return [f"column_{position}" for position in range(1, width + 1)]


def _read_streamed(
    table_path: pathlib.Path, encoding: str, shown: str, first_row: str
) -> "_Reading | None":
    """The authoritative pass: stream the file into columns.

    Returns None when the file cannot be decoded with ``encoding``, so
    the caller can try the fallback. Holds one row at a time on top of
    the columns it is filling: no list of all rows is ever built, which
    is what P1-D3 always claimed and what review item P1-R1-F15 found
    untrue.

    Blank lines are dropped, exactly as the checking pass drops them, so
    both passes count the same rows.
    """
    file_path = pathlib.Path(table_path)
    header: list[str] | None = None
    columns: list[list[str]] = []
    width = 0
    n_rows = 0
    offenders: list[tuple[int, int]] = []
    ragged = 0
    blank_pending = 0
    blank_inside = 0
    try:
        with file_path.open(
            mode="r", encoding=encoding, newline=""
        ) as handle:
            for row in csv.reader(handle):
                if not row:
                    # A blank line carries no values, so it is dropped,
                    # exactly as the checking pass drops it. In a table
                    # of ONE column that is not a safe thing to do: a
                    # blank line there is indistinguishable from a
                    # record whose only value is missing, and dropping
                    # it would delete a record and a missing value from
                    # the description without a word. Where that is
                    # what happened -- a blank line with data still to
                    # come -- the file is refused below instead.
                    blank_pending = blank_pending + 1
                    continue
                if blank_pending and header is not None and not blank_inside:
                    blank_inside = n_rows + 1
                blank_pending = 0
                if header is None:
                    header = [f"{cell}" for cell in row]
                    width = len(header)
                    columns = [[] for _position in range(width)]
                    # The byte-order-mark test belongs here, on the
                    # file's own first cell, and not later on the
                    # column names: with --first-row data those names
                    # are generated and the file's first cell has
                    # become a value. Only the Latin-1 reading is
                    # tested, because that is the reading whose
                    # characters ARE the file's bytes (module
                    # docstring).
                    marked = encoding == _FALLBACK_ENCODING and (
                        _starts_with_a_byte_order_mark(header[0])
                    )
                    if marked:
                        raise errors.ProfileError(
                            errors.looks_like_utf16(shown)
                        )
                    for position in range(width):
                        if _has_zero_byte(header[position]):
                            raise errors.ProfileError(
                                errors.looks_like_utf16(shown)
                            )
                        if first_row == FIRST_ROW_DATA:
                            # Growing a list with `+= [value]` rather
                            # than with .append: the offline policy
                            # accepts no method call on a container
                            # (plan D6.2), and `+=` on a list extends it
                            # in place, so this is a constant cost per
                            # value and not a copy of the column per row.
                            columns[position] += [header[position]]
                    if first_row == FIRST_ROW_DATA:
                        n_rows = 1
                    continue
                if len(row) != width:
                    # A wrong-length row is already a refusal; its values
                    # are not stored, because the columns they would go
                    # into are the ones whose width is in doubt. The scan
                    # continues so the message can say how many such rows
                    # there are.
                    ragged = ragged + 1
                    if len(offenders) < _MAX_REPORTED_OFFENDERS:
                        offenders = offenders + [(n_rows + 1, len(row))]
                    n_rows = n_rows + 1
                    continue
                for position in range(width):
                    value = f"{row[position]}"
                    # A zero byte anywhere in the text -- not only in the
                    # first five rows, as until review item P1-R1-F4 --
                    # means this is a UTF-16/UTF-32 file read as Latin-1
                    # or a file that is not text at all. The two readers
                    # demonstrably disagree about such a value: pandas'
                    # C reader stops the value at the zero byte and the
                    # standard reader keeps it whole.
                    if _has_zero_byte(value):
                        raise errors.ProfileError(errors.looks_like_utf16(shown))
                    columns[position] += [value]
                n_rows = n_rows + 1
    except UnicodeDecodeError:
        return None
    if header is None:
        raise errors.ProfileError(errors.file_is_empty(shown))
    if ragged:
        raise errors.ProfileError(
            errors.ragged_rows(shown, width, offenders, ragged)
        )
    if width == 1 and blank_inside:
        raise errors.ProfileError(
            errors.blank_line_in_one_column(shown, blank_inside)
        )
    if first_row == FIRST_ROW_DATA:
        names = _generated_column_names(width)
        source = HEADER_GENERATED
    else:
        names = header
        source = HEADER_FROM_FILE
    return _Reading(
        column_names=names,
        columns=columns,
        n_rows=n_rows,
        encoding=encoding,
        used_fallback_encoding=encoding == _FALLBACK_ENCODING,
        header_source=source,
    )


def _read_authoritatively(
    table_path: pathlib.Path, shown: str, first_row: str
) -> _Reading:
    """Run the authoritative pass; raise ProfileError with a plain message."""
    previous_limit = csv.field_size_limit()
    try:
        csv.field_size_limit(FIELD_SIZE_LIMIT)
        try:
            found = _read_streamed(
                table_path, _PRIMARY_ENCODING, shown, first_row
            )
            if found is None:
                found = _read_streamed(
                    table_path, _FALLBACK_ENCODING, shown, first_row
                )
            if found is None:
                raise errors.ProfileError(errors.not_utf8_or_latin1(shown))
        except csv.Error as error:
            detail = f"{error}"
            if "field larger than field limit" in detail:
                raise errors.ProfileError(
                    errors.field_too_long(shown, FIELD_SIZE_LIMIT)
                ) from error
            if "NUL" in detail:
                # Python 3.10's reader refuses a zero byte itself, and
                # later versions hand it through to the check inside the
                # streaming loop. Both paths end at the same message, so
                # the advice a reader gets does not depend on their
                # interpreter.
                raise errors.ProfileError(
                    errors.looks_like_utf16(shown)
                ) from error
            raise errors.ProfileError(
                errors.unreadable_as_csv(shown, detail)
            ) from error
        except MemoryError as error:
            raise errors.ProfileError(
                errors.out_of_memory(shown, _file_size(table_path))
            ) from error
    finally:
        csv.field_size_limit(previous_limit)

    if not found.n_rows:
        raise errors.ProfileError(errors.no_data_rows(shown))
    if found.header_source == HEADER_FROM_FILE:
        _check_header(found, shown, first_row)
    return found


def _check_header(found: _Reading, shown: str, first_row: str) -> None:
    """Refuse a first row that cannot be the column names (plan P1-D3).

    The order is deliberate: a first row that is entirely numbers, and a
    first row the shape rule cannot tell apart from a record, are
    questions about WHICH row the names are in, and they are asked
    before the questions about whether the names themselves are usable.
    """
    header = found.column_names
    if first_row == FIRST_ROW_AUTOMATIC:
        numbers = [
            name for name in header if not parsing.looks_like_a_column_name(name)
        ]
        if len(numbers) == len(header):
            raise errors.ProfileError(
                errors.header_looks_like_data(
                    shown, "every value in it reads as a number"
                )
            )
        if _first_row_is_ambiguous(header, found.columns):
            raise errors.ProfileError(
                errors.first_row_could_be_a_record(shown, len(header))
            )
    for position, name in enumerate(header, start=1):
        if not parsing.trimmed(name):
            raise errors.ProfileError(errors.empty_column_name(position))
    seen: dict[str, int] = {}
    for name in header:
        if name in seen:
            seen[name] = seen[name] + 1
        else:
            seen[name] = 1
    repeated = sorted(name for name in seen if seen[name] > 1)
    if repeated:
        raise errors.ProfileError(errors.duplicate_column_names(repeated))


def _file_size(table_path: pathlib.Path) -> int:
    """The file's size in bytes, or 0 when it cannot be read."""
    file_path = pathlib.Path(table_path)
    try:
        return int(file_path.stat().st_size)
    except OSError:
        return 0


def read_table(raw_path: str, first_row: str = FIRST_ROW_AUTOMATIC) -> Table:
    """Read a CSV table from a local path; return it as text.

    Guarantees:

    - Inputs: ``raw_path`` is the path the user typed. It is validated
      by `validate_local_path` (plan D6.1) before anything opens it, so
      a URL, a shared-network location, or a Windows device path is
      refused before any filesystem call happens. ``first_row`` is
      FIRST_ROW_AUTOMATIC (decide by the rule in this module's
      docstring), FIRST_ROW_NAMES (the first row holds the column
      names), or FIRST_ROW_DATA (the first row is a record; the columns
      are named ``column_1``, ``column_2``, ... and every record is
      kept).
    - Agreement: the returned values are the standard library reader's,
      and every one of them has been compared against a second,
      independent read by pandas, together with the column names and
      the shape. A single difference anywhere is a refusal. Equal row
      and column counts are NOT accepted as agreement (review item
      P1-R1-F4).
    - Header: the first row becomes the column names only when the rule
      in this module's docstring says so or the caller said so. A first
      row that could be a record is refused, never silently turned into
      schema (review item P1-R1-F5). WHAT THIS DOES NOT CATCH: a
      headerless file whose every column has values of differing shapes
      and whose first row is not entirely numeric -- free text over free
      text -- is still read as headed. The rule sees shape, and such a
      file has none to see.
    - Memory: NOT bounded, and this is the honest statement of it
      rather than the streaming claim P1-D3 used to make. The
      authoritative pass genuinely holds one row at a time, but what it
      is filling is the whole table as text, and while the checking
      pass runs the second reader's copy is held beside it. That
      moment is the peak. Measured as peak resident growth over the
      file's size, three shapes on one machine:

          200,000 rows x 4 columns, 9.2 MB    5.8x pass one, 13.0x peak
          1,000,000 rows x 4 columns, 46.4 MB 6.1x pass one, 11.2x peak
          200,000 rows x 20 columns, 18.7 MB 12.4x pass one, 19.3x peak

      The ratio is a property of the table, not a constant: it is
      driven by how many small values the file holds, because every one
      of them becomes a Python object. The arrangement this replaced
      peaked at 7.4x, 7.3x and 12.6x on the same three files while
      establishing nothing about the values; the authoritative pass on
      its own is now cheaper than that whole old read, and the
      difference between 7.4x and 13.0x is exactly what holding a
      second, independent reading costs. A table too large is refused
      with `errors.out_of_memory` from either pass, and every later
      allocation failure becomes one refusal at the command boundary;
      reading in pieces is future work, stated in the README.
    - Determinism: the same file bytes always produce the same Table.
      Nothing here consults a clock, an environment variable, or a
      random source; the encoding is chosen by two documented attempts,
      never guessed.
    - Errors raised: PathValidationError from the path rules, and
      ProfileError with a plain-language message for every refusal in
      the catalog (missing file, folder given instead of a file,
      unreadable encoding, empty file, no data rows, a first row that
      cannot be column names, a first row that could be a record,
      duplicate or empty column names, wrong-length rows, an over-long
      value, a zero byte anywhere in the text, the two readers
      disagreeing about a name or a value, and running out of memory).
    - Boundary: this is the only function in the package that opens the
      user's data. It reads; it never writes. The reader it hands the
      path to is network-capable and is fenced by the validated path
      (P1-D2.1).
    """
    if first_row not in (FIRST_ROW_AUTOMATIC, FIRST_ROW_NAMES, FIRST_ROW_DATA):
        # Not a refusal in the catalog: the command line offers exactly
        # these three words, so anything else is a caller's mistake and
        # not something a person typed. Reaching this is a bug report
        # against whoever called, and silently reading the first row as
        # names would lose a record on a misspelt option.
        raise ValueError(
            "synthtwin internal check: first_row must be 'auto', 'names' "
            "or 'data'."
        )
    validated = validate_local_path(raw_path, purpose="input")
    table_path = pathlib.Path(validated)
    shown = f"{table_path}"
    if not table_path.exists():
        raise errors.ProfileError(errors.file_missing(shown))
    if table_path.is_dir():
        raise errors.ProfileError(errors.path_is_a_folder(shown))
    try:
        found = _read_authoritatively(table_path, shown, first_row)
    except PermissionError as error:
        raise errors.ProfileError(
            errors.file_unreadable(shown, f"{error}")
        ) from error
    except OSError as error:
        raise errors.ProfileError(
            errors.file_unreadable(shown, f"{error}")
        ) from error

    try:
        _check_against_pandas(raw_path, found, shown)
    except MemoryError as error:
        # The checking pass holds the second reading beside the first,
        # which is the moment this reader uses the most memory. Running
        # out here is a size problem, not a bug, and it gets the
        # size-aware refusal rather than a traceback (review item
        # P1-R1-F15).
        raise errors.ProfileError(
            errors.out_of_memory(shown, _file_size(table_path))
        ) from error
    return Table(
        column_names=found.column_names,
        columns=found.columns,
        n_rows=found.n_rows,
        encoding=found.encoding,
        used_fallback_encoding=found.used_fallback_encoding,
        header_source=found.header_source,
    )


def _check_against_pandas(
    raw_path: str, found: _Reading, shown: str
) -> None:
    """Read the file again with pandas and compare EVERYTHING.

    The names are read back from the file rather than handed to the
    library. Handing them over is what made the old check blind: told
    what the columns were called, the second reader could not disagree
    about it, and a file rewritten between the passes was accepted with
    the old header and the new values (review item P1-R1-F4).

    The path is validated again here, immediately before the library
    call, rather than trusted from the caller. That is what makes the
    fence checkable: the offline scanner requires the argument handed to
    the reader to be traceable, inside this same function, to
    `validate_local_path` (plan P1-D2.1). Round 1 of the review showed
    why a path-shaped object is not enough on its own -- the library
    turns it back into text before deciding whether it is a URL, so a
    Path built from "https://host/f.csv" still reaches the network.
    """
    validated = validate_local_path(raw_path, purpose="input")
    file_path = pathlib.Path(validated)
    header_row = None if found.header_source == HEADER_GENERATED else 0
    try:
        frame = pandas.read_csv(
            file_path,
            encoding=found.encoding,
            encoding_errors="strict",
            header=header_row,
            index_col=False,
            dtype=str,
            keep_default_na=False,
            na_filter=False,
            skip_blank_lines=True,
            engine="c",
            sep=",",
            quotechar='"',
            doublequote=True,
            escapechar=None,
            skipinitialspace=False,
            comment=None,
        )
    except MemoryError as error:
        raise errors.ProfileError(
            errors.out_of_memory(shown, _file_size(file_path))
        ) from error
    except Exception as error:
        # Every failure of the checking pass becomes one plain-language
        # refusal. The catch is deliberately broad: the offline import
        # policy (plan D6.2) permits only pandas.read_csv from pandas,
        # so the library's own exception classes cannot be named here,
        # and nothing is swallowed -- the original is chained on.
        raise errors.ProfileError(
            errors.unreadable_as_csv(shown, f"{error}")
        ) from error

    found_rows = len(frame)
    keys = list(frame.columns)
    if found_rows != found.n_rows or len(keys) != len(found.column_names):
        raise errors.ProfileError(
            errors.readers_disagree(
                shown,
                f"{found.n_rows} rows of {len(found.column_names)} values",
                f"{found_rows} rows of {len(keys)} values",
            )
        )
    if found.header_source == HEADER_FROM_FILE:
        for index in range(len(keys)):
            second = f"{keys[index]}"
            if second != found.column_names[index]:
                raise errors.ProfileError(
                    errors.readers_disagree_about_a_name(
                        shown, index + 1, found.column_names[index], second
                    )
                )
    for index in range(len(keys)):
        mine = found.columns[index]
        # One column of the second reading is turned into text at a
        # time and dropped again: the whole second frame is already in
        # memory, and materializing all of it a second time would add a
        # third copy of the table for no gain.
        theirs = [f"{cell}" for cell in list(frame[keys[index]])]
        for position in range(found_rows):
            if theirs[position] != mine[position]:
                raise errors.ProfileError(
                    errors.readers_disagree_about_a_value(
                        shown, position + 1, found.column_names[index]
                    )
                )

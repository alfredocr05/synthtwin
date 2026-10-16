"""Reading the user's table: the only code that opens real data (P1-D3).

The charter rule is that one module reads the real table and nothing
else ever does. This is that module. Everything downstream receives
already-read text and never sees where it came from.

THE TWO PASSES, AND WHAT THEY NOW PROVE
=======================================

The file is read TWICE, by two different readers, and the two results
must agree ABOUT EVERY VALUE -- not, as until review round 1, about the
number of rows and columns:

1. **The reading pass** is AUTHORITATIVE, and since plan P4-D86 it is
   the survey of `dialect`: the file's bytes are decoded once, and the
   text is walked by the standard library `csv` reader's own states,
   which also records what that reader drops -- which fields were
   quoted, what ended each record, the lines that are not records -- so
   that the twin can be written the way the file was. The standard
   reader itself is then run over the same text, configured by the form
   the survey found, and every record must agree with the survey's. It
   establishes the encoding, the delimiter, the header, the value count
   of every row, the number of data rows, and every value.
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

Two attempts at this rule failed in opposite directions, and both were
trying to do the same impossible thing: prove that a first row IS a set
of column names. That proof does not exist. Nothing about the letters
in ``site`` makes it the name of a column rather than the name of a
place, so a rule built on such a proof either questions ordinary files
or swallows records, depending on how hard it strains. The question is
therefore turned around. The file is asked one thing only: does it show
that the first row is a RECORD?

Three outcomes, in this order.

1. **The caller said which it is.** ``--first-row names`` and
   ``--first-row data`` win over everything, in both directions, with
   no question asked. The rules below are not an oracle, and a person
   who knows their own file is never guessed at.

2. **The file shows the first row is a record -> stop and ask.** This
   is the one side of the question that can be shown positively, so it
   is the one side that is tested for. The first row is evidence of a
   record when, in ANY column, its value belongs to the population of
   values written below it. Five ways it can belong, any one of them
   enough on its own:

   * **A number among numbers.** Every value below reads as a number,
     the first row's value reads as a number too, and that number lies
     inside the range those values cover or within half that range's
     width of either end of it. This is the strongest signal there is:
     ``34`` above ``29``, ``41`` and ``38`` is one of them, and reading
     it as a column name publishes somebody's age as schema. Where the
     values below cover no range at all -- one data row, or one number
     repeated -- there is no spread to judge a distance by, and a whole
     number belongs only if it is that number or the one on either side
     of it.
   * **A date among dates.** Every value below is a date written in one
     format and the first row's value is a date written in that same
     format.
   * **A label the column repeats.** The first row's value appears
     again below it, more than once. A value a column repeats is one of
     that column's own labels, and the first row is holding one.
   * **A layout the column repeats** (plan P4-D241, amended by P4-D280).
     The first row's value wears the same silhouette -- its runs of
     letters and of figures collapsed, every mark standing for itself --
     as two values or more written below it, and that silhouette carries
     two marks and something that is not a word. ``CASE-ZEBRA-471``
     above ``CASE-ALPHA-0101`` is a record made of structured text.
   * **A measurement among numbers** (plan P4-D292, the merge-close of
     2026-09-18). The first row's value does not read as a number but
     carries a figure AS A VALUE -- past any leading space it opens on
     a figure or on one of the marks a reading is written with, and not
     on a letter of any alphabet or an underscore (plan P4-D310) -- and
     every value below it in
     that column reads as a number. ``<0.10`` above ``2.5``, ``3.5``,
     ``4.5`` is a reading under a limit of detection standing among the
     readings of its own column, and no column name is written that
     way. This is the exact shape `_names_evidence` already refuses to
     read as evidence of NAMES; until this rule it fell through to the
     convention instead of being read as the record it is.

   **The reading taken is the one that publishes nothing of that row**
   (the owner's ruling of 2026-09-17, item 8; plan P4-D232). Until then
   this stopped the run and asked on the screen. Now the file is read
   again with the first row as a RECORD: the columns are named
   ``column_1``, ``column_2`` and so on, every row is kept, that one
   included, and no text of it reaches the description, the summary, the
   twin, the twin's report or the quality report. The question is put in
   the questions file, naming the column by its POSITION and quoting
   nothing from the row, and ``--first-row names`` is the answer that
   takes the other reading. **A LINE THAT IS NOT A RECORD ABOVE THE ROW
   SETTLES IT THE SAME WAY**: a title or a comment over a headerless
   table and the same title over a headed one are the same bytes up to
   the row in question, so a row under furniture cannot be told from a
   record either, on delimited text and on a workbook sheet alike.

3. **The file shows the first row is NOT a record -> names, shown.**
   One thing a file can genuinely show: a column whose every value
   below is a number while the first row's value is not. That is a
   difference in kind, not in appearance, and it is the only such
   difference this module trusts. The row is read as names, and
   ``header_by_convention`` is False because nothing was assumed.

   This decides nothing the next outcome would not also decide -- the
   row is read as names either way. It exists so the summary can stay
   quiet on a file that shows its header and speak on a file that does
   not. Getting it wrong costs one sentence, never a record, which is
   why a rule too weak to decide the reading is strong enough here.

4. **No evidence either way, and no furniture above it -> the first row
   is taken as the column names, BY CONVENTION.** A CSV file normally begins with its column
   names, and
   following that convention is what makes this tool usable on ordinary
   files. Nothing is claimed about the file: taking is not proving.
   Nor is it silent. ``header_by_convention`` is set on the Table, and
   ``header_evidence`` says in plain words that the first row was read
   as the column names because nothing in the file contradicted it, and
   that ``--first-row data`` re-reads it as a record if that is wrong.
   Both belong beside ``header_source`` wherever the reading is
   published, so a person can see the assumption and take it back.

One first row is settled before any of that: one whose EVERY value
reads as a number. It goes the way outcome 2 goes, and for the same
reason -- a row of numbers is a record as surely as a row the columns
below claim -- so the columns are named ``column_1``, ``column_2`` and
so on, every record is kept, and the questions file asks.

The question is put to the person AFTER the checking pass below, never
before it. A file whose two readers disagree about a name or a value
has no single right reading to choose between, so that disagreement is
reported first. A blank or repeated name is no longer refused (plan
P4-D86): the column is named the way pandas names it, `Unnamed: N` or
with `.1`, `.2` after it (`dialect.named_columns`), the cell as the file
writes it is published so the twin writes it back, and pandas is asked
to read such a header as a row so its own renaming is not reported as a
disagreement.

WHERE THIS RULE IS WRONG, AND WHY IT IS DRAWN HERE
==================================================

Outcome 3 is the one that costs a record, and the cost is written down
here rather than left to be found. A headerless table whose every
column is worded text -- ``alpha note,red apple`` above two more rows
of the same kind, the file review round 6 named -- holds no value that
belongs to the column below it, so it is read as headed: two records
instead of three, and the third record's words standing as the column
names. That is what every CSV reader in the world does with such a
file, and it is what the previous two attempts to avoid could not do
without questioning ordinary tables instead. What changed is the
honesty of the record. The reading is published as a convention that
was followed, not as a verdict the file supported, and one word on the
command line takes it back with every record kept.

Outcome 2 costs the other way, and it is the cheaper cost because
nothing is published: a table that really is headed can be questioned.
A column named ``2024`` above a column of years, or a column named
``one`` above values ``one``, ``two``, ``one``, is a first row whose
value genuinely belongs to the column under it, and synthtwin asks
rather than choosing. Answering ``--first-row names`` costs one run.

Three shapes are the ones to keep in mind when this rule is next
touched. ``region,2019,2020,2021`` above ``r1,1,2,3`` is an ordinary
pivoted year table and must go through: 2019 is nowhere near the range
those columns cover. ``P001,34`` above ``P002,35`` must stop: 34 sits
one step from the only number under it. ``age,B10`` above ``31,B01``
... ``49,B19`` must go through: ``B10`` does appear below, but exactly
once, in a column of one-off codes, which is a coincidence and not
membership of anything.

ENCODINGS AND BYTE-ORDER MARKS
==============================

A UTF-32 mark is refused; UTF-16 is read behind its own mark; then
UTF-8, with or without its mark; then Windows-1252, where a byte between
0x80 and 0x9F is present and every such byte is defined there; then
Latin-1 (`dialect.decoded`). Latin-1 can decode any byte sequence, so a
file that is really UTF-16 without its mark, UTF-32, or not text at all
would come through as nonsense rather than as an error, which is what
the zero-byte and mark checks below stop. The twin is written back in
the encoding the table was read with (plan P4-D86), and Latin-1 and
Windows-1252 map each byte they define to one character and back, so a
guess between them costs no byte of any published label.

Byte-order marks are matched as COMPLETE byte sequences. Latin-1 maps
each of the 256 bytes to the code point of the same number and back
again, so after a Latin-1 fallback the decoded characters ARE the file's
bytes, one for one, and comparing the first characters against
``\\xff\\xfe`` compares the first bytes. Review round 1 found a valid
Latin-1 header beginning with the single byte 0xFF -- an ordinary
``\\xff`` character -- refused as UTF-16 because a lone character was
being read as a mark; a mark is two or four bytes and is now required to
be all of them.

The whole file is read with `Path.read_bytes`, the one accepted way to
obtain bytes from a path (the offline policy accepts no method call on an
open file object), and the mark is also tested on the bytes themselves.

IMPORTS
=======

Imports here stay within the allowlist (plan D6.2 with the Phase 1
additions in P1-D10): csv, pandas, pathlib, dataclasses, and this
package's own modules. `pandas.read_csv` is network-capable -- it would
open a URL if it were handed one -- and it is fenced, not trusted: the
only path that reaches it has passed `validate_local_path`, inside the
same function as the call, which rejects URL forms lexically before any
filesystem call (P1-D2.1, and SECURITY.md states it in the same terms).

`taxonomy` is among this package's own modules imported here, for one
reason: the header verdict this module settles is PUBLISHED in the
profile, and every sentence a profile publishes is built from the one
enumerated grammar `taxonomy.note` owns (plan P2-D2). A verdict written
as free text here would be the single string in the finished document
with no form behind it, and one exception is all a guard needs to stop
meaning anything. Nothing else travels the other way: `taxonomy` does
not import this module and cannot reach a file.
"""

import csv
import zipfile
import dataclasses
import pathlib
import typing

import pandas

from synthtwin import dialect, errors, parsing, taxonomy, workbook
from synthtwin.paths import validate_local_path

# The per-value size the standard reader will accept while a table is
# being read. The default (about 130,000 characters) is too small for a
# free-text column of long notes; ten million characters is far beyond
# any real cell and still small enough that a file with an unclosed
# quotation mark is refused rather than read to its end. The previous
# value is restored afterwards, because this setting belongs to the
# whole program, not to us.
FIELD_SIZE_LIMIT = 10_000_000
# Enough opening bytes to tell a package, a compound file and markup
# apart, and never enough to be a value of anybody's.
_OPENING_BYTES = 8

# The two encodings a table is read under, and the whole of what the
# profile's `source.encoding` may say. They are named here rather than
# left private because the publication guard checks that field against
# this enumeration (plan P2-D2): a value the reader never produces may
# not appear there.
PRIMARY_ENCODING = dialect.ENCODING_UTF8
FALLBACK_ENCODING = dialect.ENCODING_LATIN1
ENCODINGS = dialect.ENCODINGS

# How far outside the range of a column's own numbers the first row's
# number still counts as one of them, as a share of that range's width
# (`_numeric_fit`). Slack is needed at all because the smallest or
# largest number of a sorted table sits at the edge of its own column:
# 34 above 35, 36, 37, 38, 39 is a record and is one step outside the
# range those five cover.
#
# Half a width is where this is drawn, and both ends of the choice were
# measured against files rather than argued. Below about 0.4 the reader
# stops seeing 140 above 3, 7, 20, 99 and 101 -- a headerless table
# whose first record is its largest -- and publishes that record as
# schema. At a full width it starts asking about ``region,2019,2020``
# above sales counts in the 1,000-1,600 range, which is an ordinary
# pivoted year table nobody should be questioned about. Neither
# neighbouring value is safe, so this one is not a knob to turn without
# running both shapes again.
_NEARBY_SHARE_OF_THE_RANGE = 0.5

# How many wrong-length rows are named in a refusal message.
_MAX_REPORTED_OFFENDERS = 3

# The rows of the one piece the pandas check reads its whole frame as
# (`_check_against_pandas`, plan P4-D387): more than any file can hold,
# so the piece is every row the file has, parsed in the steps pandas
# parses a frame read at once and handed over at the line the check's
# other pieces are.
_EVERY_ROW = 1 << 62

# What the caller may say about the first row. AUTOMATIC is the default
# and is the only one that can end in the ambiguity refusal.
FIRST_ROW_AUTOMATIC = "auto"
FIRST_ROW_NAMES = "names"
FIRST_ROW_DATA = "data"

# Where a Table's column names came from.
HEADER_FROM_FILE = "file"
HEADER_GENERATED = "generated"

# WHAT A REFUSAL ABOUT THIS FILE MAY SAY (plan P3-D1, V9).
#
# `synthtwin profile` reads the table the person handed it and asked it
# to describe, so a refusal about that file may quote what the reader
# found: the name it read back, the column a disputed value sits in.
# Naming it is how the person finds the place.
#
# `synthtwin validate` is pointed at a file NOBODY promised was theirs.
# It may be a twin, it may be somebody else's table, it may be the wrong
# table entirely -- and a refusal travels as freely as a report does. So
# on that path every refusal names POSITIONS and never values, and the
# caller says which path it is on. The default is the profiler's, so
# every message the profiler produces is the same byte for byte as it
# was before this argument existed.
REFUSALS_MAY_QUOTE = "quote"
REFUSALS_NAME_POSITIONS = "positions"

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

# The evidence sentence for a first row the caller settled rather than
# the file. Both are published on the Table so a later reader of the
# profile can see how the column names were arrived at.
#
# All four verdicts below are `taxonomy.note` sentences rather than text
# written here, because they are published in the profile and every
# published sentence is built from one enumerated form (plan P2-D2). The
# words themselves are in `taxonomy.rendered`, beside every other
# sentence a profile can carry, so a reader meets the whole vocabulary
# in one place and the publication guard can rebuild each one.
_SAID_NAMES = taxonomy.note(taxonomy.HEADER_NAMES_BY_OPTION)
_SAID_DATA = taxonomy.note(taxonomy.HEADER_DATA_BY_OPTION)

# The sentence for outcome 3 of the module docstring: the first row was
# taken as the names because a CSV file is normally written that way and
# nothing in this one said otherwise. It claims no evidence, says so in
# as many words, and carries the way to take it back. A person who reads
# only this sentence has been told everything synthtwin assumed.
_TAKEN_BY_CONVENTION = taxonomy.note(taxonomy.HEADER_NAMES_BY_CONVENTION)
# WHERE THE ROW CANNOT BE TOLD FROM A RECORD (the owner's ruling of
# 2026-09-17, item 8; plan P4-D232).
_NOT_TOLD = taxonomy.note(taxonomy.HEADER_NAMES_NOT_TOLD)


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

    ``header_evidence`` is that same verdict in words: one sentence
    naming what in the file, or what on the command line, settled which
    row the names are in. It is written for a person to read and belongs
    beside ``header_source`` wherever that is published.

    ``first_row_seen`` is what the FILE showed, in words, where the
    first row could NOT be told from a record of the table (the owner's
    ruling of 2026-09-17, item 8; plan P4-D232); it is empty on every
    other outcome, ``--first-row data`` included -- a caller who SAID
    the row is a record was told nothing, they told synthtwin. Where it
    is filled the names are synthtwin's own placeholders, the row is
    kept as a record, and the questions file puts the question with
    these words as what was seen. They quote no cell of the file.

    ``header_by_convention`` is True exactly when the names came from
    the file's first row because nothing in the file contradicted the
    usual way of writing a CSV -- outcome 3 of this module's docstring
    -- and not because the caller said so and not because anything was
    proved. It is the machine-readable half of that one sentence, and
    it is False for both ``--first-row`` answers. A publisher that shows
    ``header_source`` must show this beside it: "the names came from the
    file" and "the names came from the file because we assumed they
    would" are not the same claim, and review item P1-R6-F6 is about
    exactly that difference.
    """

    column_names: list[str]
    columns: list[list[str]]
    n_rows: int
    encoding: str
    used_fallback_encoding: bool
    header_source: str
    # Every verdict this module produces is a `taxonomy.Note`, which IS
    # a string and is annotated as one here so that the empty default
    # below stays legal. What makes it a Note matters downstream: the
    # profile publishes this sentence, and the publication guard accepts
    # a published sentence only when it can rebuild it from an
    # enumerated form (plan P2-D2). `read_table` never leaves it empty.
    header_evidence: str = ""
    header_by_convention: bool = False
    first_row_seen: str = ""
    # How the file is written: its delimiter, quoting, line endings and
    # the lines that are not records (module `dialect`). The profile
    # publishes its form, and the validator holds a checked file to the
    # form a description publishes.
    survey: "dialect.Survey | None" = None
    # What a WORKBOOK said about itself, where the table came from one
    # (module `workbook`, plan P4-D77). Both are None for delimited
    # text, and the description then publishes no workbook block.
    book: "workbook.Reading | None" = None
    sheet: "workbook.Sheet | None" = None
    # WHERE A TABLE READ IN GROUPS OF COLUMNS IS HELD (lane SR, plan
    # P4-D400). Where it is given, ``columns`` is empty and every column
    # is asked of `column_values`, which holds one group at a time and
    # reads the file again for another; where it is None, ``columns``
    # holds every column and `column_values` hands one over.
    source: "ColumnSource | None" = None


@dataclasses.dataclass(frozen=True)
class _Reading:
    """What the authoritative pass established about a file."""

    column_names: list[str]
    columns: list[list[str]]
    n_rows: int
    encoding: str
    used_fallback_encoding: bool
    header_source: str
    header_evidence: str = ""
    header_by_convention: bool = False
    first_row_seen: str = ""
    survey: "dialect.Survey | None" = None
    book: "workbook.Reading | None" = None
    sheet: "workbook.Sheet | None" = None


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


def _numeric_fit(name: str, values: list[str]) -> bool:
    """True when the first row's value is one of this column's own numbers.

    The first of the three record rules in the module docstring, and the
    strongest of them. Every value below reads as a number, the first
    row's value reads as a number too, and that number lies inside the
    range those values cover or within _NEARBY_SHARE_OF_THE_RANGE of
    that range's width of either end of it. ``34`` above ``29``, ``41``
    and ``38`` is a person's age; read as a column name it becomes
    schema text, outside every suppression rule, and the person it came
    from disappears from every count.

    The slack on each side is what makes the rule work on the top and
    bottom of a sorted table: ``34`` above ``35`` ... ``39`` is the
    smallest number of its own column, not a label. It stays narrow
    enough to keep the rule off an ordinary pivoted year table --
    ``2019`` above values between 101 and 112 is nowhere near them.

    A column whose values cover NO range -- one data row, or one number
    written over and over -- offers no spread to judge a distance by. A
    whole number then belongs only if it is that number or the one on
    either side of it, which is what makes ``P001,34`` above ``P002,35``
    a question and leaves ``region,2019,...`` above fourteen rows of
    ``1234`` alone.

    Deleting this rule is what let review round 6's second repair
    publish ``alice``, ``canada`` and ``34`` as column names.

    The column is read once. That matters: this is the most expensive
    question this module asks, and it is asked only of a column whose
    first-row value is itself a number, which is rare.
    """
    if parsing.classify_number(f"{name}") == parsing.NOT_A_NUMBER:
        return False
    if not values:
        return False
    mine = parsing.parse_number(f"{name}")
    lowest = None
    highest = None
    every_value_is_whole = True
    for value in values:
        text = f"{value}"
        if parsing.classify_number(text) == parsing.NOT_A_NUMBER:
            return False
        parsed = parsing.parse_number(text)
        if parsed is None:
            # A well-formed number too large or too small to hold. It
            # is still a number, so the column is still numeric, but it
            # cannot take part in a comparison of magnitudes.
            continue
        if not parsing.is_whole_number(parsed):
            every_value_is_whole = False
        if lowest is None or parsed < lowest:
            lowest = parsed
        if highest is None or parsed > highest:
            highest = parsed
    if mine is None or lowest is None or highest is None:
        return False
    spread = highest - lowest
    if spread == 0.0:
        if not every_value_is_whole or not parsing.is_whole_number(mine):
            return mine == lowest
        return -1.0 <= mine - lowest <= 1.0
    margin = spread * _NEARBY_SHARE_OF_THE_RANGE
    return lowest - margin <= mine <= highest + margin


def _date_fit(name: str, values: list[str]) -> bool:
    """True when the first row's value is a date among this column's dates.

    The second record rule. Every value below reads as a date under one
    of the formats the profiler knows, and the first row's value reads
    as a date under that same format. A column name is not usually a
    date, and when it is -- a table pivoted by month -- the values under
    it are counts rather than dates, so the two halves do not both hold.

    The formats are tried in the profiler's own order, and the first one
    every value below fits is the one the first row's value is asked
    about. A single value below that does not fit that format ends the
    attempt, which keeps a column of dates with one word in it from
    counting.
    """
    if not values:
        return False
    for format_name in parsing.DATE_FORMATS:
        if parsing.parse_datetime(f"{name}", format_name) is None:
            continue
        every_value_fits = True
        for value in values:
            if parsing.parse_datetime(f"{value}", format_name) is None:
                every_value_fits = False
                break
        if every_value_fits:
            return True
    return False


def _repeats_a_value_below(name: str, values: list[str]) -> bool:
    """True when the first row's value is one this column repeats.

    The third record rule. A value that appears MORE THAN ONCE below the
    first row is one of the column's own labels -- a place, a category,
    a yes or a no -- and a first row holding one of them is holding a
    value of that column.

    "More than once" is what separates membership from coincidence, and
    it is not a detail. A column of one-off codes ``B01`` ... ``B19``
    under a column genuinely named ``B10`` matches once and means
    nothing: every value in such a column is unique, so any text at all
    might collide with one of them. A column that writes ``site-1``
    nine times is a column of places, and ``site-1`` above it is a
    tenth.
    """
    if not values:
        return False
    wanted = f"{name}"
    seen = 0
    for value in values:
        if f"{value}" == wanted:
            seen = seen + 1
            if seen > 1:
                return True
    return False


# A silhouette's two collapsed runs. Everything else in a value stands
# for itself, so `CASE-ZEBRA-471` and `CASE.ZEBRA.471` are different
# shapes and neither is the shape of `record_id`.
SILHOUETTE_LETTERS = "A"
SILHOUETTE_FIGURES = "9"
# Spelled out rather than asked of a method, because the audit accepts no
# method call on a value read out of the user's file, and because a
# silhouette is an ASCII question: a letter outside ASCII stands for
# itself, as every mark does.
_SILHOUETTE_ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
_SILHOUETTE_FIGURES = "0123456789"

# THE SPACES A VALUE MAY BE WRITTEN WITH BEFORE IT OPENS. A file written
# `record, q1, q2` hands this module the name ` q1`, and the space
# before the letter is the file's spacing and not part of what the value
# opens with (plan P4-D310). The spaces outside ASCII are here by plan
# P4-D313: a cell copied out of a web page or pasted through a
# spreadsheet opens on a NO-BREAK SPACE or a byte-order mark often
# enough that `\u00a0<0.10` -- a censored reading -- was read as a name and
# published as a column. Skipping one of these never turns a name into
# a reading on its own: it only lets the character BEHIND it answer.
# Spelled out rather than asked of a method for the same reason the
# alphabet above is.
_NAME_LEADING_SPACES = (
    " \t"
    + "\u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007"
    + "\u2008\u2009\u200a\u200b\u202f\u205f\u3000\ufeff"
)

# EVERY MARK A READING MAY OPEN WITH, and nothing else opens one (plans
# P4-D310, P4-D313). `_holds_a_figure_as_a_value` asks this rather than
# asking whether the opening is a LETTER, because the letters of the
# world are a Unicode table and the marks a measurement is written with
# are a short list. Every character absent from here -- which is every
# letter of every alphabet -- opens a NAME, so a mark MISSING from this
# enumeration hands a headerless table's first record back to the
# schema, which is ruling 8 of 2026-09-17 reversed. The four pieces are
# therefore stated separately and each is held by a test of its own:
#
# * every ASCII mark except the underscore a column name is written
#   with;
# * the comparison, sign, currency and unit marks outside ASCII a
#   reading opens with;
# * the FULL-WIDTH figures, which a CJK export writes its numbers with;
# * the FULL-WIDTH forms of those same ASCII marks, minus the
#   full-width underscore, which the same exports write `\uff1c0.10` with.
_ASCII_READING_MARKS = "!\"#$%&'()*+,-./:;<=>?@[\\]^`{|}~"
_READING_MARKS_OUTSIDE_ASCII = (
    "\u2264\u2265\u00b1\u2212\u2013\u2014\u2248\u20ac\u00a3\u00a5\u00a2"
    + "\u00d7\u00f7\u2032\u2033"
)
_FULL_WIDTH_FIGURES = (
    "\uff10\uff11\uff12\uff13\uff14\uff15\uff16\uff17\uff18\uff19"
)
_FULL_WIDTH_READING_MARKS = (
    "\uff01\uff02\uff03\uff04\uff05\uff06\uff07\uff08\uff09\uff0a"
    + "\uff0b\uff0c\uff0d\uff0e\uff0f\uff1a\uff1b\uff1c\uff1d\uff1e"
    + "\uff1f\uff20\uff3b\uff3c\uff3d\uff3e\uff40\uff5b\uff5c\uff5d"
    + "\uff5e"
)
_READING_OPENINGS = (
    _SILHOUETTE_FIGURES
    + _ASCII_READING_MARKS
    + _READING_MARKS_OUTSIDE_ASCII
    + _FULL_WIDTH_FIGURES
    + _FULL_WIDTH_READING_MARKS
)

# THE FIGURES A READING CARRIES, which is not the silhouette's question
# (plan P4-D313). A silhouette is an ASCII question by P4-D241 and stays
# one; but a value that has already OPENED a reading carries its figures
# in whatever alphabet its file writes them, so `\uff10\uff11\uff10` is a reading
# and not a word. Used by `_holds_a_figure_as_a_value` alone.
_READING_FIGURES = _SILHOUETTE_FIGURES + _FULL_WIDTH_FIGURES


def _silhouette(text: str) -> str:
    """One value's shape: runs of letters and of figures, marks as they stand.

    `CASE-ZEBRA-471` and `CASE-ALPHA-0101` are both `A-A-9`, and
    `record_id` over `R001` is `A_A` over `A9`. That is the difference
    the fourth record rule below reads (plan P4-D241).

    Guarantees: accepts text; returns its shape. Determinism: a fixed
    function of the text. Raises nothing. No I/O of any kind.
    """
    shape = ""
    last = ""
    for character in text:
        kind = character
        if character in _SILHOUETTE_ALPHABET:
            kind = SILHOUETTE_LETTERS
        elif character in _SILHOUETTE_FIGURES:
            kind = SILHOUETTE_FIGURES
        if kind == last and (
            kind == SILHOUETTE_LETTERS or kind == SILHOUETTE_FIGURES
        ):
            continue
        shape = shape + kind
        last = kind
    return shape


def _shape_is_structured(shape: str) -> bool:
    """Whether a silhouette says more than two column names share by accident.

    TWO MARKS AND SOMETHING THAT IS NOT A WORD. Both halves are measured
    rather than argued, and each was put there by a witness the first
    writing of this rule turned red.

    A run of letters beside a run of figures is what an ordinary header
    shares with its own column all the time: `visit1` over `a1`,
    `region,2019` over `r1`, `B10` over `B01` are all `A9` over `A9`,
    and every one of them is a headed table this package has read
    without a question since review item P1-R6-F6. So a silhouette of
    fewer than TWO marks says nothing here.

    Letters and spaces alone say nothing either: `Full Name` over `John
    Smith` is `A A` over `A A`, and `First Middle Last` over `John Paul
    Jones` is `A A A` -- two marks, and still two columns of words. A
    FIGURE, or a mark that is not a space, is what makes the shape a
    structure: `A-A-9` and `A A 9` carry one, and that is what a record
    number and an address wear and what a column name does not wear by
    accident.
    """
    marks = 0
    told = False
    for character in shape:
        if character == SILHOUETTE_LETTERS:
            continue
        if character == SILHOUETTE_FIGURES:
            told = True
            continue
        marks = marks + 1
        if character != " ":
            told = True
    return marks >= 2 and told


def _shares_the_shape_below(name: str, values: list[str]) -> bool:
    """True when the first row's value wears the structure of its column.

    THE FOURTH RECORD RULE (the owner's ruling of 2026-09-17, item 8;
    plan P4-D241, the repair of the final review of 2026-09-18). The
    three rules above read a NUMBER, a DATE and a repeat, and a record
    made of structured text is none of the three: 240 records of
    `CASE-ZEBRA-471,Northfield Clinic 3,<0.10` under a title published
    that first record as the three column names, wrote it verbatim as
    row two of the twin and of the twin workbook, described 239 rows
    where the file holds 240, and asked nothing -- because `<0.10` is
    not a number, so the column of numbers beside it read as evidence
    that the row is NAMES. The row's own first field is what tells it:
    every value below it in that column is `A-A-9` and so is it.

    A LAYOUT RECURRING BELOW IS THE EVIDENCE, AND IT DOES NOT HAVE TO BE
    THE COMMONEST ONE (plan P4-D280, the repair of review item 1 of the
    files review of 2026-09-18 and of the skeptic's finding 1 on that
    repair). The first row's silhouette must be structured
    (`_shape_is_structured` above) and must be worn by at least TWO of
    the non-empty values below it. A column of words under a name of
    words says nothing here, and neither does `record_id` over `R001`
    -- `A_A` is not `A9` -- which is what keeps this rule off the
    ordinary headed export.

    IT USED TO DEMAND EVERY VALUE BELOW, AND ONE CELL DEFEATED IT.
    Measured on the tree before this rule, at a floor of eleven: the 240
    records of `CASE-ZEBRA-471,Northfield Clinic 3,<0.10` under a title
    that this rule exists to catch were caught only while every
    identifier below wore `A-A-9`. Writing ONE of the 239 as
    `CASE_ALPHA_1120` -- a second system's layout, which the owner's
    seventh ruling says a file may hold -- or as `NA`, left the shape
    unanimous no longer, this rule silent, and the whole record
    published as the three column names with the table 239 rows long.

    AND COUNTING THE MINORITY WAS NOT ENOUGH EITHER: IT MOVED THE
    THRESHOLD RATHER THAN REMOVING IT. The first writing of this repair
    also asked that the first row's silhouette be the COMMONEST below
    it. MEASURED on the tree carrying that writing, same 239 records at
    a floor of eleven, varying only how many identifiers read `NA`: 119
    of them is caught -- 240 records, `column_1` to `column_3`, nothing
    of the record anywhere -- and 120 is not: 239 records, the whole
    record published as the three column names, nothing asked, and the
    twin's own header line the real record verbatim. A record number is
    not unspelled by the rows that wear another layout or hold no value
    at all, however many of them there are, so the count that matters
    is the count of rows wearing the FIRST ROW'S layout and nothing
    else: two of them say the first row is one of a population.

    WHAT THIS RULE STILL CANNOT SEE, measured and left for the owner. A
    first record whose layout NO row below repeats -- 239 identifiers
    written `CASE_ALPHA_1001` under the one record `CASE-ZEBRA-471` --
    wears a structured silhouette worn by nought below it, and this
    rule is silent: the same 239 records publish that record as the
    three column names. Reading any structured silhouette recurring
    below as the evidence would catch it and would also catch an
    ordinary headed export whose header is structured in another
    layout: MEASURED, `Street Address, Line 1` over 40 addresses such
    as `12 Oak St, Apt 3` is `A A, A 9` over `9 A A, A 9`, both
    structured, and the file loses its real column names to
    placeholders. That is a second rule with its own cost, not a widening
    of this one, and P4-D280 puts it to the owner.

    Guarantees: accepts the first row's value in one column and the
    values below it; returns a bool. Determinism: a fixed function of
    the two. Raises nothing. No I/O of any kind.
    """
    mine = _silhouette(f"{name}")
    if not _shape_is_structured(mine):
        return False
    worn: "dict[str, int]" = {}
    for value in values:
        text = f"{value}"
        if text == "":
            continue
        shape = _silhouette(text)
        worn[shape] = (worn[shape] if shape in worn else 0) + 1
    seen = worn[mine] if mine in worn else 0
    return seen >= 2


def _reads_as_a_reading(text: str) -> bool:
    """True when one value below the first row reads as a READING.

    The evidence population of `_measurement_among_numbers`, one value
    at a time (round 2 of the review, the disclosure pass, item 1). A
    number reads as a reading; so does a value written the way a
    measurement is written and not as a number -- `<0.10`, `2-4`,
    `5 mg` -- which is the same `_holds_a_figure_as_a_value` question
    that rule asks of the FIRST ROW, asked of the column instead. A
    column of readings holds both, and before this was asked one cell
    of the second kind was enough to defeat the rule and republish a
    real record as the file's column names.

    Spellings of NO VALUE never reach here: the caller drops them
    first, because a cell holding no value is evidence of nothing.

    Guarantees: accepts text; returns a bool. Determinism: a fixed
    function of the text. Raises nothing. No I/O of any kind.
    """
    if parsing.classify_number(text) != parsing.NOT_A_NUMBER:
        return True
    return _holds_a_figure_as_a_value(text)


# How many letters in a row make a WORD rather than a unit. Two is a
# unit -- `mg`, `kg`, `ml`, `cm` -- and a measurement is written with
# one; three is `total`, `count`, `time`, `week`, `dose`, and a column
# name is written with those. The line is stated once, here, and
# `_carries_a_word` is the only reader of it.
_A_WORD = 3


def _carries_a_word(text: str) -> bool:
    """Whether this value holds a run of `_A_WORD` letters or more.

    WHAT TELLS A COLUMN NAME FROM A MEASUREMENT ONCE THE FIGURE TEST
    HAS PASSED (round 2 of the review, the disclosure pass; the repair
    pass of this landing). `_holds_a_figure_as_a_value` asks only that
    the value carries a figure and does not OPEN on a letter, and an
    ordinary export's column name passes that test whenever it opens on
    a figure or a mark: `2024 total`, `1st reading`, `100m time`,
    `3-month change`, `>65 count`. The readings the measurement rule
    exists for do not carry a word: `<0.10`, `2-4` and `5 mg` are a
    mark, a range and a unit.

    The letters are read against this module's own alphabet rather than
    asked of a method, because this text came out of the user's file.

    Guarantees: accepts text; returns a bool. Determinism: a fixed
    function of the text. Raises nothing. No I/O of any kind.
    """
    run = 0
    for character in text:
        if character in _SILHOUETTE_ALPHABET:
            run = run + 1
            if run >= _A_WORD:
                return True
        else:
            run = 0
    return False


def _measurement_among_numbers(
    name: str, values: list[str], floor: int
) -> bool:
    """True when the first row's value is a MEASUREMENT of a numeric column.

    THE FIFTH RECORD RULE (the owner's ruling of 2026-09-17, item 8;
    plan P4-D292, the merge-close of 2026-09-18). It closes the hole the
    merge skeptic walked through: a headerless table with NO furniture
    above it, `R001,North Unit,<0.10` over 239 rows of `R###,East,#.5`,
    published that first record as the three column names, described 239
    rows where the file holds 240, asked no question at all, and wrote
    the record verbatim as the twin's header line -- in delimited text
    and in a workbook alike. The same table under a title line was read
    correctly, which is why the shape read as closed.

    IT IS THE COMPLEMENT OF `_names_evidence`, NOT A NEW JUDGEMENT.
    P4-D272 taught that function that a first-row value carrying a
    figure AS A VALUE -- `<0.10`, `2-4`, `5 mg`, which open on a figure
    or on one of the marks a reading is written with rather than on a
    letter of any alphabet or an underscore (plan P4-D310) -- is no
    evidence that the row is NAMES, because that is how a MEASUREMENT is
    written and a column name is not written that way. That left the
    shape with no evidence on either side, and outcome 4 takes a row
    with no evidence and no furniture as the names by convention. So
    exactly what that function refuses to read as names is read here as
    the record it is.

    WHY IT CANNOT SWALLOW THE PIVOTED YEAR TABLE. A value that reads as
    a NUMBER never reaches this rule: `_numeric_fit` is the rule for
    those, and it is the one that measures the distance, so `region,2019`
    over fourteen rows of `1234` is settled there and stays settled --
    2019 is a number, so this rule declines it before looking at the
    column at all. What is left is the value that is not a number and
    not a name either.

    Two values are required below, as in `_names_evidence`: one number
    under a first-row value says nothing about a population.

    WHAT ONE CELL USED TO COST, AND WHY THE POPULATION IS NOW FILTERED
    (round 2 of the review, the disclosure pass, item 1; this landing).
    The first writing of this rule demanded that EVERY value below read
    as a number, and a column of readings almost never does: the reader
    that this rule exists to protect writes `NA` where nobody was
    measured and `<0.10` where the instrument saw nothing. **Measured**
    at a floor of eleven on the rule's own table -- `R001,North
    Unit,<0.10` over 239 records `R###,East,#.5`, no furniture above it
    -- with the LAST record's reading changed and nothing else:

    * `240.5`, an ordinary number: `column_1` to `column_3`, 240
      records, the question asked. This is the shape the rule closed;
    * an EMPTY cell: the same, because the old population already
      dropped the empty spelling;
    * `NA`: the rule answered False and the file published `R001`,
      `North Unit` and `<0.10` as its three column names over 239
      records, asking nothing -- ruling 8 broken by one cell;
    * `#N/A`, a spreadsheet's own artifact: the same three names, 239
      records;
    * `<0.05`, a second censored reading of the very kind this rule is
      named for: the same three names, 239 records.

    So the evidence population is every value below that is not a
    spelling of NO VALUE, and each of those must read either as a
    number or as a reading written the way the first row's is -- the
    same `_holds_a_figure_as_a_value` question, asked of the column
    instead of the row. TWO of them must be actual numbers, which is
    what keeps the rule anchored to a column of numbers: a column of
    nothing but `<0.10` and `2-4` offers no numbers for the first row's
    value to stand among, and this rule declines it and leaves it to the
    furniture rule and to convention, as before.

    A FIRST-ROW VALUE CARRYING A WORD IS A COLUMN NAME (the repair pass
    of this landing, round 2's disclosure finding 2). Widening the
    population above cost something the first writing did not measure:
    one recognised missing spelling below the row used to defeat this
    rule, and that ACCIDENT was the only thing keeping it off an
    ordinary headed export whose header opens on a figure. **Measured**
    at floors one and eleven on a perfectly ordinary CSV -- the header
    `site,2024 total` over 320 records `North Unit,437` with `NA` every
    twenty-ninth row -- the tree before this guard published
    `column_1`/`column_2` over 321 records where 05e7d89 published
    `site`/`2024 total` over 320: the file's own column names thrown
    away and its header row generated as a 321st record. Of eleven
    realistic header names over that table, five flipped. That is two
    of the owner's mandatory goals broken at once -- code written on
    the twin no longer runs unchanged on the real table, and the row
    count is wrong by one -- so `_carries_a_word` is asked of the first
    row's own value before the column is looked at, and the seven
    header names measured below keep their file's reading:

    * kept as names: `2024 total`, `1st reading`, `100m time`,
      `3-month change`, `>65 count`, `5 mg dose`, `2-4 week`;
    * still read as a record: `<0.10`, `2-4`, `5 mg`, `250.5`.

    The cost is stated rather than hidden: a headerless file whose
    first record's reading carries a word -- `3 tablets` -- is not
    caught by this rule and falls to convention, as it did before round
    2's item 1. A column name carrying no word at all (`50%`) is not
    told from a reading either, which is the state 05e7d89 was already
    in for a file with no absent cell in that column.

    AND A MINORITY THAT READS AS NEITHER IS TOLERATED (the repair pass
    of this landing, round 2's disclosure finding 4). The first writing
    answered False at the first value below that was neither a
    recognised spelling of no value nor a reading, so ONE cell somebody
    typed as `missing` -- a word `parsing.is_missing_text` does not
    know, and no more does `unknown`, `N.A.` or `nil` -- put the whole
    of somebody's record back among the column names. **Measured** on
    the rule's own table with the last reading written `missing`:
    05e7d89 and the tree before this guard alike published `R001`,
    `North Unit` and `<0.10` as the three column names over 239
    records. So the values that read as neither are COUNTED, and the
    rule survives them while they are fewer than `parsing.census_floor`
    of the caller's floor -- the same shape `_shares_the_shape_below`
    uses, that two values below say the first row is one of a
    population, and the same line every other disclosure question in
    this package is asked at. A column most of whose values are words
    is still no column of numbers and still declines.

    Guarantees: accepts the first row's value in one column, the values
    below it and the person's smallest group size; returns a bool.
    Determinism: a fixed function of the three. Raises nothing. No I/O
    of any kind.
    """
    text = f"{name}"
    if parsing.classify_number(text) != parsing.NOT_A_NUMBER:
        return False
    if not _holds_a_figure_as_a_value(text):
        return False
    if _carries_a_word(text):
        return False
    # A cell holding NO VALUE is not evidence either way, so it is
    # dropped rather than counted against the rule, and the vocabulary
    # of "no value" is asked for through the one operation that owns it
    # (`parsing.is_missing_text`, plan P4-D6.2) instead of being read a
    # second time here. The empty spelling is a member of that
    # vocabulary, which is what the discarded `!= ""` test used to do on
    # its own.
    present = [
        f"{value}"
        for value in values
        if not parsing.is_missing_text(f"{value}")
    ]
    if len(present) < 2:
        return False
    figures = 0
    unread = 0
    for value in present:
        if not _reads_as_a_reading(value):
            unread = unread + 1
        elif parsing.classify_number(value) != parsing.NOT_A_NUMBER:
            figures = figures + 1
    if unread >= parsing.census_floor(floor):
        return False
    return figures >= 2


def _record_evidence(
    header: list[str], columns: list[list[str]], floor: int
) -> "str | None":
    """What shows the first row is a record, in words, or None.

    None means no column of the file shows it. That is NOT evidence for
    the names reading and is never described as any; the caller takes
    the first row as the names by convention and says so in those terms
    (outcome 3 of the module docstring, review item P1-R6-F6).

    The returned words are a clause, ready to be dropped into the
    questions file as what synthtwin SAW (the owner's ruling of
    2026-09-17, item 8; plan P4-D232; they were a refusal's words until
    then). The column is named by its POSITION and nothing is quoted
    from the file: in a file whose first row may be a record, the first
    row's text is somebody's data, and the values below it always are.

    The five rules are tried in the order a person would want to hear
    them, which is also cheapest first for the common case: only a
    numeric first-row value reaches the walk of a numeric column at all.
    Each rule stops at the first column that speaks. The fourth,
    `_shares_the_shape_below`, was added by plan P4-D241 and is the one
    that reads a record made of structured TEXT; it is asked fourth
    because it walks every column of the file. The fifth,
    `_measurement_among_numbers`, was added by plan P4-D292 and reads
    the measurement written the way no column name is written -- the
    exact shape `_names_evidence` refuses as evidence of names.

    ``floor`` is the person's smallest group size, and only the fifth
    rule reads it: it is the line under which that rule tolerates
    values it can read as neither a spelling of no value nor a reading
    (round 2's disclosure finding 4, closed in the repair pass of this
    landing). The four rules before it ask nothing of the floor and
    take none.
    """
    for rule in range(1, _RECORD_RULES + 1):
        for index in range(len(header)):
            if _record_rule_fits(rule, header[index], columns[index], floor):
                return _record_words(rule, index)
    return None


# The five rules `_record_evidence` tries, in its order.
_RECORD_RULES = 5


def _record_rule_fits(rule: int, name: str, values: "list[str]", floor: int) -> bool:
    """Whether `_record_evidence`'s rule ``rule`` (1 to 5) reads one column's first row as a record."""
    if rule == 1:
        return _numeric_fit(name, values)
    if rule == 2:
        return _date_fit(name, values)
    if rule == 3:
        return _repeats_a_value_below(name, values)
    if rule == 4:
        return _shares_the_shape_below(name, values)
    return _measurement_among_numbers(name, values, floor)


def _first_record_rule(name: str, values: "list[str]", floor: int) -> int:
    """The first of `_record_evidence`'s rules that reads one column's first row as a record, or 0.

    `_record_evidence` asks each rule of every column before the next
    rule, so the column it names is the leftmost of those whose first
    rule is the lowest any column answers; a reader that holds a group
    of columns at a time (lane SR, plan P4-D400) keeps this for each
    column and finds that one at the end (`_record_words`).
    """
    for rule in range(1, _RECORD_RULES + 1):
        if _record_rule_fits(rule, name, values, floor):
            return rule
    return 0


def _record_words(rule: int, index: int) -> str:
    """The words `_record_evidence` gives for rule ``rule`` met in the column at ``index``."""
    if rule == 1:
        return (
            f"in column {index + 1} the value in that row is a number "
            f"lying among the numbers written below it, which is what "
            f"a record in that column looks like"
        )
    if rule == 2:
        return (
            f"in column {index + 1} the value in that row is a date, "
            f"written the same way as every date below it, which is "
            f"what a record in that column looks like"
        )
    if rule == 3:
        return (
            f"in column {index + 1} the value in that row appears "
            f"again further down the same column, more than once, so "
            f"it is one of the values that column is made of"
        )
    if rule == 4:
        return (
            f"in column {index + 1} the value in that row is written "
            f"to the same pattern of letters, figures and marks as "
            f"values written below it in that column, which is what "
            f"a record in that column looks like"
        )
    return (
        f"in column {index + 1} the value in that row is not a "
        f"number but is written the way a measurement is written, "
        f"standing over a column whose values below it are "
        f"numbers, apart from readings written the same way, "
        f"cells holding no value, and fewer cells than the "
        f"smallest group that read as neither, which is what a "
        f"reading in that column looks like"
    )


def _generated_column_names(width: int) -> list[str]:
    """Names for a table whose first row the caller said was data."""
    return [f"column_{position}" for position in range(1, width + 1)]


def _as_text(value: object) -> str:
    """``value`` proven to be text, which is what lets a method run on it."""
    if not isinstance(value, str):
        raise TypeError("internal check: a file's text was not text")
    return value


def _agrees_with_the_standard_reader(
    lines: "typing.Iterator[str]",
    surveyed: dialect.Survey,
    headed: bool,
    shown: str,
    refusals: str,
    kept: "tuple[bool, ...] | None" = None,
) -> "tuple[int, int, int] | None":
    """Hold the survey's reading to the standard library reader's, value by value.

    The survey walks the text by the standard reader's own states so that
    it can see what that reader drops -- which fields were quoted, what
    ended each record. This runs the standard reader itself over the same
    text, configured by the form the survey found, and requires the same
    header, the same metadata rows and every data value in the same
    place. The lines the survey placed outside the table -- the
    separator hint, the preamble, blank lines -- are passed over where
    the form says they stand. A difference is a refusal: it would mean
    the survey read something the standard reader did not.

    ``lines`` are the text's lines without an end-of-file mark
    (`_body_lines`, or the file's own lines read a line at a time, lane
    SR, plan P4-D400). ``kept``, where given, names the columns the
    survey held (`dialect.survey`'s ``keep``): only their values are
    compared, nothing is refused, and the first difference is RETURNED
    as (stage, row, place) for the reader to weigh against the other
    groups' -- the header 0, a metadata row 1, a record 2 (place -1 for
    the record itself), the count of records 3 -- so the refusal made is
    the one this check makes reading every column at once.
    """
    width = len(surveyed.form.columns)
    expected_header: list[str] = []
    if headed:
        expected_header = list(surveyed.header)
        if surveyed.form.header_trailing_delimiter:
            expected_header += [""]
    header_pending = headed
    row = 0
    found: "tuple[int, int, int] | None" = None
    for kind, cells in _standard_records(lines, surveyed, headed):
        if kind == _RECORD_HEADER:
            header_pending = False
            if cells != expected_header:
                found = (0, 0, 0)
                break
            continue
        if kind >= _RECORD_METADATA:
            expected = list(surveyed.form.header_rows[kind - _RECORD_METADATA])
            if cells != expected:
                found = (1, kind - _RECORD_METADATA, 0)
                break
            continue
        if len(cells) != width or row >= surveyed.n_rows:
            found = (2, row, -1)
            break
        for place in range(width):
            if kept is not None and (place >= len(kept) or not kept[place]):
                continue
            if cells[place] != surveyed.columns[place][row]:
                found = (2, row, place)
                break
        if found is not None:
            break
        row = row + 1
    if found is None and (row != surveyed.n_rows or header_pending):
        found = (3, row, 0)
    if found is not None and kept is None:
        _refuse_the_disagreement(found, surveyed, shown, refusals)
    return found


# What `_standard_records` hands over with each record: the header, a
# data record, or a metadata row, numbered from `_RECORD_METADATA`.
_RECORD_HEADER = 0
_RECORD_DATA = 1
_RECORD_METADATA = 2


def _standard_records(
    lines: "typing.Iterator[str]", surveyed: dialect.Survey, headed: bool
) -> "typing.Iterator[tuple[int, list[str]]]":
    """The standard reader's records of a table, as the survey's form places them.

    The standard reader is configured by the form the survey found and
    run over ``lines``; the lines the survey placed outside the table --
    the separator hint, the preamble, blank lines -- are passed over
    where the form says they stand, a data record's closing delimiter is
    taken off and a short record is filled out with empty values, as the
    survey reads them. Each record is handed over with what it is: the
    header (`_RECORD_HEADER`), a metadata row (`_RECORD_METADATA` and on,
    in order) or a data record (`_RECORD_DATA`). Both the check of the
    survey's reading and the reading of a group of columns again
    (`column_values`) take their records from here (lane SR, plan
    P4-D400), so a record read again is the record the check held.
    """
    form = surveyed.form
    backslash = form.escape == dialect.ESCAPE_BACKSLASH
    rows = csv.reader(
        lines,
        delimiter=form.delimiter,
        doublequote=not backslash,
        escapechar="\\" if backslash else None,
        skipinitialspace=form.initial_space,
    )
    lead = 1 if form.separator_line else 0
    lead = lead + dialect.preamble_lines_written(form.preamble)
    header_pending = headed
    metadata_pending = len(form.header_rows)
    width = len(form.columns)
    # Every place, counted or not: past its cap the form publishes the
    # blank lines counted, and the file still holds each where it stands.
    places = [place for place in surveyed.every_blank_place if place.text]
    place_at = 0
    place_left = places[0].lines if places else 0
    row = 0
    for record in rows:
        cells = list(record)
        if not cells:
            continue
        if lead:
            lead = lead - 1
            continue
        if header_pending:
            header_pending = False
            yield _RECORD_HEADER, cells
            continue
        if metadata_pending:
            yield _RECORD_METADATA + len(form.header_rows) - metadata_pending, cells
            metadata_pending = metadata_pending - 1
            continue
        # WHAT THE STANDARD READER YIELDS FOR A LINE OF SPACES (review
        # item CODEX-15). The survey publishes that line's OWN spelling,
        # because that is what the twin has to write back. This reader
        # is configured with `skipinitialspace` wherever the file is
        # written comma-space, and that setting skips the leading
        # spaces of the FIRST field as well as the others -- so the very
        # same line reaches here as one EMPTY field. The two readings
        # agree about the line and present it differently, so the
        # comparison says which presentation it is asking for rather
        # than refusing the file for the difference.
        standing = ""
        if place_at < len(places):
            standing = places[place_at].text
            if form.initial_space:
                cut = 0
                while cut < len(standing) and standing[cut] == " ":
                    cut = cut + 1
                standing = standing[cut:]
        if (
            len(cells) == 1
            and width >= 2
            and place_at < len(places)
            and places[place_at].after == row
            and standing == cells[0]
        ):
            place_left = place_left - 1
            if not place_left:
                place_at = place_at + 1
                place_left = places[place_at].lines if place_at < len(places) else 0
            continue
        if (
            form.rows_trailing_delimiter
            and len(cells) == width + 1
            and cells[width] == ""
        ):
            cells = cells[:width]
        if form.short_rows and len(cells) < width:
            cells += ["" for _place in range(width - len(cells))]
        yield _RECORD_DATA, cells
        row = row + 1


def _refuse_the_disagreement(
    found: "tuple[int, int, int]",
    surveyed: dialect.Survey,
    shown: str,
    refusals: str,
) -> None:
    """Refuse the difference `_agrees_with_the_standard_reader` found, in its words."""
    stage, row, place = found
    width = len(surveyed.form.columns)
    if stage == 0:
        _disagree_about_a_name(shown, surveyed, refusals)
    if stage == 1:
        raise errors.ProfileError(
            errors.readers_disagree(
                shown, "a row of column descriptions", "a different row"
            )
        )
    if stage == 2 and place < 0:
        raise errors.ProfileError(
            errors.readers_disagree(
                shown,
                f"{surveyed.n_rows} rows of {width} values",
                "a row the standard reader read differently",
            )
        )
    if stage == 2:
        _disagree_about_a_value(shown, surveyed, row, place, refusals)
    raise errors.ProfileError(
        errors.readers_disagree(
            shown,
            f"{surveyed.n_rows} rows of {width} values",
            f"{row} rows",
        )
    )


def _body_lines(text: str, form: dialect.Dialect) -> "typing.Iterator[str]":
    """A whole text's lines, without the end-of-file mark the survey took off."""
    body = _as_text(text)
    if form.end_of_file_mark:
        body = body[: len(body) - 1]
    return dialect.lines_in_turn(body)


def _disagree_about_a_name(
    shown: str, surveyed: dialect.Survey, refusals: str
) -> None:
    """Refuse a header the standard reader read differently from the survey."""
    if refusals == REFUSALS_NAME_POSITIONS:
        raise errors.ProfileError(
            errors.checked_file_readers_disagree_about_a_name(shown, 1)
        )
    first = surveyed.header[0] if surveyed.header else ""
    raise errors.ProfileError(
        errors.readers_disagree_about_a_name(shown, 1, first, "")
    )


def _disagree_about_a_value(
    shown: str, surveyed: dialect.Survey, row: int, place: int, refusals: str
) -> None:
    """Refuse a value the standard reader read differently from the survey."""
    if refusals == REFUSALS_NAME_POSITIONS or not surveyed.header:
        raise errors.ProfileError(
            errors.checked_file_readers_disagree_about_a_value(
                shown, row + 1, place + 1
            )
        )
    names = dialect.named_columns(surveyed.header)
    raise errors.ProfileError(
        errors.readers_disagree_about_a_value(shown, row + 1, names[place])
    )


def _read_authoritatively(
    table_path: pathlib.Path,
    shown: str,
    first_row: str,
    refusals: str = REFUSALS_MAY_QUOTE,
    encoding: str = "",
    given: bytes = b"",
    metadata_rows: int = 0,
    decimal_comma_columns: "tuple[str, ...]" = (),
    metadata_rows_confirmed: bool = False,
    declared_delimiter: str = "",
    small_cell_floor: int = parsing.DEFAULT_SMALL_CELL_FLOOR,
) -> _Reading:
    """Survey the file, hold it to the standard reader; refuse in plain words.

    The bytes are read once and decoded once (`dialect.decoded`); the
    survey is the reading, and the standard reader is run over the same
    text as its check. Where the survey and the standard reader both
    stand, a zero byte, a byte-order mark read as text and a value past
    the reader's size limit are refused exactly as they were when the
    standard reader was the reading.
    """
    file_path = pathlib.Path(table_path)
    try:
        data = given if given else file_path.read_bytes()
    except MemoryError as error:
        raise errors.ProfileError(
            errors.out_of_memory(shown, _file_size(table_path))
        ) from error
    if encoding:
        text, encoding, marked = dialect.decoded_as(data, shown, encoding)
    else:
        text, encoding, marked = dialect.decoded(data, shown)
    # The bytes are not needed once they are text, and holding both while
    # the survey fills the table is one file's size of memory for nothing.
    data = b""
    if encoding in dialect.FALLBACK_ENCODINGS and _starts_with_a_byte_order_mark(
        text
    ):
        raise errors.ProfileError(errors.looks_like_utf16(shown))
    if _has_zero_byte(text):
        raise errors.ProfileError(errors.looks_like_utf16(shown))
    headed = first_row != FIRST_ROW_DATA
    previous_limit = csv.field_size_limit()
    try:
        csv.field_size_limit(FIELD_SIZE_LIMIT)
        try:
            surveyed = dialect.settle(
                text, encoding, marked, not headed, shown, metadata_rows,
                decimal_comma_columns, metadata_rows_confirmed,
                declared_delimiter, small_cell_floor,
            )
            _agrees_with_the_standard_reader(
                _body_lines(text, surveyed.form), surveyed, headed, shown,
                refusals,
            )
        except csv.Error as error:
            detail = f"{error}"
            if "field larger than field limit" in detail:
                raise errors.ProfileError(
                    errors.field_too_long(shown, FIELD_SIZE_LIMIT)
                ) from error
            if refusals == REFUSALS_NAME_POSITIONS:
                # The reader's own account of the trouble can carry a
                # piece of the file with it, and this file may not be
                # the person's own table (V9).
                raise errors.ProfileError(
                    errors.checked_file_unreadable_as_csv(shown)
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

    if not surveyed.n_rows:
        raise errors.shape_refusal(
            errors.no_data_rows(shown), errors.NO_DATA_TO_DESCRIBE
        )
    if headed:
        names = list(dialect.named_columns(surveyed.header))
        source = HEADER_FROM_FILE
        # The caller who said FIRST_ROW_NAMES has settled it already;
        # FIRST_ROW_AUTOMATIC is settled in `_settle_the_first_row`,
        # which replaces this sentence with what the file's own values
        # say, or stops and asks because they say nothing.
        evidence = _SAID_NAMES
    else:
        names = _generated_column_names(len(surveyed.columns))
        source = HEADER_GENERATED
        evidence = _SAID_DATA
    return _Reading(
        column_names=names,
        columns=surveyed.columns,
        n_rows=surveyed.n_rows,
        encoding=encoding,
        used_fallback_encoding=encoding in dialect.FALLBACK_ENCODINGS,
        header_source=source,
        header_evidence=evidence,
        survey=surveyed,
    )


def _settle_the_first_row(
    found: _Reading, shown: str, first_row: str, floor: int
) -> "tuple[str, bool, str]":
    """Settle WHICH row holds the column names, and say why (plan P1-D3).

    Returns the verdict in words, whether it was reached by convention,
    and -- where the row could NOT be told from a record -- what the
    file showed, in words, or the empty string where it could. The first
    two are published beside the names; the third is what the questions
    file says was SEEN.

    NOTHING IS REFUSED HERE ANY MORE (the owner's ruling of 2026-09-17,
    item 8; plan P4-D232). Two outcomes used to stop the run and ask on
    the screen -- a first row whose every value reads as a number, and a
    first row the values below show to be a record. Both now come back
    with the third answer, and the caller re-reads the file with the
    first row as a RECORD: the columns are named `column_1`, `column_2`
    and so on, every row is kept, no text of that row reaches the
    description, and the questions file puts the question. A person who
    knows the row holds the names says so with `--first-row names`.

    The outcomes are the module docstring's, in its order: a caller who
    said which it is settles it; otherwise a row that cannot be told
    from a record is not told from one; otherwise the first row is taken
    as the names, shown by a column or by convention.

    What this must never do is describe the third outcome as evidence.
    Absence of evidence for the record reading is not evidence for the
    names reading -- there is no such evidence to be had, which is why
    two attempts to find some failed in opposite directions (review
    item P1-R6-F6). It is an assumption, it is named as one, and the
    caller who disagrees has ``--first-row data``.

    It runs after the checking pass, not before it. The question it puts
    to a person is which reading of the first row is the right one, and
    a file whose two readers do not agree about a name or a value has no
    single right reading to choose between -- so that disagreement is
    reported first, and this question is asked only about a file both
    readers read the same way.

    ``floor`` is the person's smallest group size, handed down to
    `_record_evidence` for the one rule that reads it. Both callers
    have it: the delimited path as `read_table`'s ``small_cell_floor``
    and the workbook path as `_read_workbook_table`'s ``floor``, so the
    two formats settle the first row by one rule at one line.
    """
    header = found.column_names
    if first_row != FIRST_ROW_AUTOMATIC:
        return found.header_evidence, False, ""
    numbers = [
        name for name in header if not parsing.looks_like_a_column_name(name)
    ]
    if len(numbers) == len(header):
        return _NOT_TOLD, False, EVERY_VALUE_A_NUMBER
    spoken = _record_evidence(header, found.columns, floor)
    if spoken is not None:
        return _NOT_TOLD, False, spoken
    shown_by = _names_evidence(header, found.columns)
    if shown_by is not None:
        return shown_by, False, ""
    # ...AND A ROW UNDER FURNITURE THE FILE SHOWS NOTHING ABOUT CANNOT
    # BE TOLD EITHER (the owner's ruling of 2026-09-17, item 8; plan
    # P4-D232). A title over a headerless table and a title over a
    # headed one are the same bytes up to the row in question: the
    # survey steps over the title and hands this the row beneath it,
    # which is the column names as often as it is the first record.
    # Measured on the tree before this rule: `subject id` over
    # `CASE-ZEBRA-471,amber,Northfield` published that record as the
    # three column names, in the description, in the summary, in the
    # twin's header and in the quality report, and left the table one
    # row short. Nothing in the VALUES marks it, so no rule reading them
    # can catch it and the shape of the FILE is what answers.
    #
    # IT IS ASKED AFTER OUTCOME 3 AND NOT BEFORE IT, which is the whole
    # of what keeps it from reading an ordinary export wrong. A title
    # over a real header is the commonest shape a spreadsheet exports,
    # and where a column below that header holds numbers while the
    # header's own value does not, the file SHOWS the row is names --
    # measured: `Extract for unit 7` over `record_id,age,arm,site,
    # reading` and eighteen records read as a headerless table of
    # nineteen when this was asked first, the header row became a value
    # of every column, and the twin failed its own description at exit
    # 3 (`tests/test_file_dialect_round_trip.py`).
    if _stood_under_furniture(found):
        return _NOT_TOLD, False, UNDER_FURNITURE
    return _TAKEN_BY_CONVENTION, True, ""


# What the file showed, for the questions file to say. Each is words a
# person reads, and not one of them quotes a cell.
EVERY_VALUE_A_NUMBER = "every value in that row reads as a number"
UNDER_FURNITURE = (
    "that row stands under a line that is not a record of the table -- a "
    "title, or a comment -- so it is the column names as often as it is "
    "the first record, and nothing in the values can say which"
)


def _stood_under_furniture(found: _Reading) -> bool:
    """Whether a line that is not a record stood above the row taken as names.

    True for a delimited file whose survey stepped over a line of TEXT
    or a COMMENT before the table, and for a workbook sheet whose reader
    stepped over rows of one cell above it (plan P4-D186). Both are the
    same shape of file and are answered the same way, which is what the
    ruling asks for: on delimited text and on workbooks alike.

    A BLANK RUN IS NOT FURNITURE FOR THIS PURPOSE, and the difference is
    measured rather than argued: a file beginning with a spare newline
    is an ordinary file, its blank line says nothing about what the next
    line holds, and counting it here read `age` over four numbers as a
    headerless table of five records
    (`tests/test_reading_header_shape.py`). A line of text or a comment
    is a different thing: it is somebody's title, and a title stands
    over a headerless table as readily as over a headed one.

    Guarantees: accepts the reading; returns a bool. Determinism: a
    fixed function of the reading. Raises nothing. No I/O of any kind.
    """
    survey = found.survey
    if survey is not None:
        for run in survey.form.preamble:
            if run.kind != dialect.PREAMBLE_BLANK:
                return True
    sheet = found.sheet
    if sheet is None or sheet.rows_above < 1:
        return False
    # ...AND A SHEET THAT MARKS ITS HEADER HAS SAID WHICH ROW HOLDS THE
    # NAMES (plan P4-D174, P4-D232). Frozen panes ending at that row, or
    # an autofilter beginning at it, are things a person does to a
    # header and never to a record -- the file's own evidence, of the
    # same standing as a column of numbers under a name that is not one.
    # Measured without this clause: the autofilter of a marked sheet
    # names the header's row, the twin with no header wrote it elsewhere,
    # and `workbook.autofilter` MISSED on the twin.
    book = found.book
    return book is None or not workbook.marks_the_header(
        book, sheet.header_row
    )


def _names_evidence(
    header: list[str], columns: list[list[str]]
) -> "str | None":
    """Why the first row is DEMONSTRABLY names, or None if it is not.

    Guarantees:

    - Inputs: the first row, and the values below it by column.
    - Determinism: depends only on those values.
    - Errors raised: none.
    - Boundary: this decides NOTHING about how the file is read. The
      first row is taken as names either way; this only settles whether
      that was shown or assumed, so that the summary can stay quiet on
      a file that shows it and speak on a file that does not. A wrong
      answer here costs a sentence, never a record.

    The one thing a file can actually show: a column whose values are
    all of one kind -- all numbers, or all dates -- with a first-row
    value that is not of that kind. Nothing else counts. A value that
    merely looks different from its neighbours proves nothing, which is
    what defeated the two attempts that tried to use it (P1-R6-F6).

    AND "NOT A NUMBER" IS NOT THE SAME THING AS "NOT A MEASUREMENT"
    (the owner's ruling of 2026-09-17, item 8; plan P4-D272, the repair
    of the extra review round of 2026-09-18). A column of measurements
    holds values this package cannot parse as numbers all the time: a
    reading under the limit of detection is written `<0.10`, a range is
    written `2-4`, a value with its unit is written `5 mg`. Every one of
    them is a VALUE of that column, and taking one for a column name is
    how one person's first record became the file's schema. **Measured**
    at a floor of eleven, on a title line above a headerless table of
    240 records whose first is `R001,North Unit,<0.10` and whose rest
    are `R###,East,#.5`: both the delimited file and the workbook
    published `R001`, `North Unit` and `<0.10` as the three column
    names, described 239 records where the file holds 240, asked no
    question about the first row at all, and wrote that person's record
    as the twin's header line.

    So a first-row value that carries a figure AS A VALUE is no evidence
    here, and the cost of the rare case is a question rather than a
    record: the caller falls through to the furniture rule, which on a
    file with nothing above the row still takes it as the names by
    convention and on a file with a title asks the person.

    AND "CARRIES A FIGURE" ON ITS OWN WAS TOO WIDE (plan P4-D272, as
    amended by the repair pass of 2026-09-18). The first writing of this
    rule refused the evidence of ANY first-row value holding a figure,
    and a column name holds one often: `q1`, `week_2` and `glucose1` are
    column names by every reading. **Measured** at a floor of eleven,
    against the commit before this rule was written: `Patient
    questionnaire export 2021` over a real header `q1,q2,q3,q4` and 300
    rows of numbers was read correctly before and afterwards published
    `column_1` to `column_4` over 301 records -- the header row taken as
    a RECORD, which then gave every numeric column `n_numeric 300`
    beside `n_not_numeric 1`, a fresh count of one made by the very
    landing that was closing them. The same as a workbook, and the same
    for `subject,glucose1,week_2`. This rule returns on the FIRST column
    that shows evidence, so one such name was enough to lose the header.

    WHAT SEPARATES A MEASUREMENT FROM A NAME IS THE OPENING. `<0.10`,
    `2-4` and `5 mg` open on a mark or on a figure; `q1`, `week_2`,
    `glucose1` and `échelle1` open on a letter, and a name written with
    a leading underscore opens on one mark this rule reads the same way.
    So a figure counts here only in a value whose first character past
    any leading space is a figure or one of the marks a reading is
    written with -- which is every ASCII mark but the underscore, and
    the comparison, sign and currency marks outside it -- and never in
    one that opens on a letter of any alphabet (plan P4-D310).
    `record_id`, `age`, `arm`, `site` and `reading` over a title line
    are untouched as they always were.

    WHERE RULING 8'S SHAPE IS ACTUALLY HELD UP, AND IT WAS NOT HERE
    (plan P4-D292, the merge-close of 2026-09-18). Until that entry this
    docstring claimed that `<0.10` yielding no evidence here meant
    `R001,North Unit,<0.10` "still gets placeholder names and the
    question". **Measured** and false: refusing evidence of NAMES is not
    evidence of a RECORD, and under a title line it was the furniture
    rule -- not this one -- that asked. With no title line the same 240
    records published `R001`, `North Unit` and `<0.10` as the column
    names, described 239 rows where the file holds 240, asked nothing,
    and wrote that record as the twin's header line. The shape is now
    read as a record by `_measurement_among_numbers`, the fifth record
    rule, and by nothing else: `_shape_is_structured` deliberately
    excludes the `A9` that `R001` wears, so the fourth rule never
    reached it either.
    """
    for position, name in enumerate(header):
        if position >= len(columns):
            break
        if _names_shown(name, columns[position]):
            return taxonomy.note(
                taxonomy.HEADER_NAMES_SHOWN_BY_COLUMN, (position + 1,)
            )
    return None


def _names_shown(name: str, values: "list[str]") -> bool:
    """Whether one column shows its first row is a NAME, as `_names_evidence` asks each in turn."""
    # No method call on an untraced value: every element is forced to
    # text by an f-string first, and a blank cell is compared, not
    # trimmed. A whitespace-only cell therefore reads as "not a
    # number", so a column holding one yields no evidence and the
    # header is taken by convention -- the conservative side, and it
    # costs a sentence rather than a record.
    present = [f"{value}" for value in values if f"{value}" != ""]
    if len(present) < 2:
        return False
    if parsing.classify_number(f"{name}") != parsing.NOT_A_NUMBER:
        return False
    if _holds_a_figure_as_a_value(f"{name}"):
        return False
    every_value_is_a_number = True
    for value in present:
        if parsing.classify_number(f"{value}") == parsing.NOT_A_NUMBER:
            every_value_is_a_number = False
    return every_value_is_a_number


def _holds_a_figure_as_a_value(text: str) -> bool:
    """Whether one value carries a figure the way a VALUE does (P4-D272).

    A figure counts only in a value that OPENS THE WAY A READING OPENS,
    which is what separates a measurement from a name: `<0.10`, `2-4`
    and `5 mg` open on a mark or on a figure, while `q1`, `week_2` and
    `glucose1` open on a letter and `_2021` on the one mark a name is
    written with. The opening character is read, never asked of a
    method, because this value came out of the user's file.

    THE OPENING IS FOUND PAST THE SPACES A NAME MAY BE WRITTEN WITH, AND
    A LETTER OUTSIDE ASCII IS A LETTER (plan P4-D310, review item 3 of
    the files review of 2026-09-18). The first writing of this rule
    asked whether the opening stood in the ASCII alphabet, so every
    other character in the world opened a reading -- an accented letter
    and a leading space among them. **Measured** at a floor of eleven,
    on a header of two names over 120 records holding the numbers 1 to
    120 and three repeating groups: `échelle1,group` and ` q1,group`
    were each read as a RECORD by `_measurement_among_numbers`, so both
    files published `column_1` and `column_2`, described 121 records
    where the file holds 120, gave the numeric column a fresh
    `n_not_numeric 1`, counted the word `group` as one missing cell, and
    asked about the first row. Both were read correctly before the rule
    existed. The same as a workbook.

    SO THE OPENING IS ASKED THE OTHER WAY ROUND: the value opens a
    READING where its first character past any leading space it may be
    written with -- `_NAME_LEADING_SPACES`, the ASCII space and tab and
    the spaces outside ASCII a pasted cell opens with -- is a figure or
    one of `_READING_OPENINGS`, and it opens a NAME
    otherwise -- which is every letter of every alphabet, the ASCII ones
    and `é`, `ß` and `ω` alike, and the underscore a name is written
    with. Enumerating the marks rather than the letters is what keeps
    this readable without a Unicode table: the audit accepts no method
    call on a value read out of the user's file, and `str.isalpha`
    answers out of a table that moves between releases.

    WHAT A MARK MISSING FROM THE ENUMERATION COSTS -- MEASURED, AND
    CLOSED FOR THE SHAPES MEASURED (plan P4-D313, the repair pass of
    2026-09-19). A reading whose opening mark this enumeration does not
    hold is read as a NAME, so a headerless table whose first record
    opens that way is published as the schema and written verbatim as
    the twin's header line -- ruling 8 of 2026-09-17 reversed, by the
    door P4-D272 was written to shut. **Measured** on 240 headerless
    records whose only evidence is the fifth rule, `North Unit,<reading>`
    over 239 records of a site beside a plain number, at a floor of
    eleven, over nine spellings of that reading: at `05e7d89` all nine
    published `column_1` and `column_2` over 240 records and asked about
    the first row; with the enumeration as P4-D310 first wrote it FIVE
    of the nine instead published `North Unit` and the reading itself as
    the column names, described 239 records and asked nothing --
    `＜0.10`, ` <0.10`, `×10`, `０0.10` and `′5`. So the enumeration
    now holds the full-width figures and the full-width forms of the
    ASCII marks, `×`, `÷`, `′` and `″`, and the leading spaces hold the
    spaces outside ASCII a pasted cell opens with. All nine are read as
    readings again, and the accented and spaced headers of P4-D310 keep
    their own names.

    THE COST THAT REMAINS, STATED. The enumeration is still an
    enumeration: a reading opening on a mark absent from all four pieces
    is read as a name. A further mark is a one-character amendment held
    by the battery in
    `tests/test_extra_round_disclosure.py`, and the alternative -- every
    character outside ASCII opening a reading -- is the defect above,
    which costs an ordinary accented header its own names on every file
    that carries one.

    Guarantees: accepts text; returns whether it carries a figure as a
    value. Determinism: a fixed function of the text. Raises nothing. No
    I/O of any kind.
    """
    opening = ""
    for character in text:
        if character in _NAME_LEADING_SPACES:
            continue
        opening = character
        break
    if opening == "":
        return False
    if opening not in _READING_OPENINGS:
        return False
    for character in text:
        if character in _READING_FIGURES:
            return True
    return False


def _file_size(table_path: pathlib.Path) -> int:
    """The file's size in bytes, or 0 when it cannot be read."""
    file_path = pathlib.Path(table_path)
    try:
        return int(file_path.stat().st_size)
    except OSError:
        return 0


def opened_workbook(table_path: str, shown: str) -> "dict[str, bytes]":
    """Every member of a workbook package, expanded under the caps.

    THIS LIVES HERE AND NOT IN `workbook` BECAUSE IT OPENS A FILE. The
    vocabulary and the parsing of a workbook are reached by the loader,
    and the loader is in the GENERATOR's import graph; the generator
    never reads a table, and the rule is that the module which opens one
    is not in that graph at any instant (plan P2-D1). So the package is
    opened beside the only other code in this package that opens the
    user's table, and `workbook` works on the members this hands it.

    Guarantees:

    - Order: the package's own directory is read first, and every cap
      that can be checked from it -- the member count, the declared
      expanded total, and each member's declared expansion ratio -- is
      checked BEFORE a single member is expanded. That order is what
      makes these caps a defence rather than a report of what has
      already happened.
    - Errors raised: ProfileError for a package that is not one, for a
      member named outside the package, and for each cap by name.
    - Boundary: opens for reading only. No member is ever extracted to
      a path, so a member named `..` reaches no filesystem.
    """
    try:
        bundle = zipfile.ZipFile(table_path)
    except zipfile.BadZipFile as error:
        raise errors.ProfileError(errors.workbook_unreadable(shown)) from error
    except zipfile.LargeZipFile as error:
        raise errors.ProfileError(errors.workbook_unreadable(shown)) from error
    parts: "dict[str, bytes]" = {}
    try:
        listing = bundle.infolist()
        if len(listing) > workbook.MAXIMUM_MEMBERS:
            raise errors.ProfileError(
                errors.workbook_too_many_parts(shown, workbook.MAXIMUM_MEMBERS)
            )
        total = 0
        for item in listing:
            if workbook.names_a_place_outside(item.filename):
                raise errors.ProfileError(
                    errors.workbook_part_named_away(shown)
                )
            # A MEMBER NOBODY CAN EXPAND IS TURNED AWAY BEFORE ANYTHING
            # TRIES (plan P4-D289). An encrypted member and a member
            # packed by an unimplemented method both raise out of the
            # standard library's own reader, as a bare `RuntimeError`
            # and a bare `NotImplementedError`, and neither carries a
            # sentence a person can act on; the checks are asked of the
            # listing, which says both without expanding a byte.
            if workbook.is_packaged_unreadably(
                item.flag_bits, item.compress_type
            ):
                raise errors.ProfileError(
                    errors.workbook_is_packaged_unreadably(shown)
                )
            total = total + item.file_size
            if total > workbook.MAXIMUM_EXPANDED_BYTES:
                raise errors.ProfileError(
                    errors.workbook_expands_too_far(
                        shown, workbook.MAXIMUM_EXPANDED_BYTES
                    )
                )
            packed = item.compress_size
            if packed and item.file_size > packed * workbook.MAXIMUM_MEMBER_RATIO:
                raise errors.ProfileError(
                    errors.workbook_part_expands_too_far(
                        shown, workbook.MAXIMUM_MEMBER_RATIO
                    )
                )
        for item in listing:
            if workbook.names_a_folder(item.filename):
                continue
            try:
                parts[item.filename] = bundle.read(item)
            except zipfile.BadZipFile as error:
                raise errors.ProfileError(
                    errors.workbook_unreadable(shown)
                ) from error
    finally:
        bundle.close()
    return parts


def _read_workbook_table(
    table_path: str,
    shown: str,
    wanted: str,
    first_row: str = FIRST_ROW_AUTOMATIC,
    refusals: str = REFUSALS_MAY_QUOTE,
    published_header: int = 0,
    missing_under: "taxonomy.Settings | None" = None,
    floor: int = parsing.DEFAULT_SMALL_CELL_FLOOR,
) -> Table:
    """One sheet of a workbook, as a table of text (plan P4-D77).

    ``missing_under`` is `read_table`'s: the settings whose missing
    words are no present cell where a column's clocks are counted
    (`no_value_spellings`), the defaults where None.

    THE SECOND READER IS NOT RUN HERE, and that is a real difference
    from the delimited path rather than an oversight. A CSV file is read
    twice -- once by this module and once by pandas -- and a single
    disagreement anywhere is a refusal. A workbook has no second reader
    inside the offline guarantee: the package's pandas is reduced to
    `read_csv` alone, and admitting a workbook library would put a third
    runtime dependency inside that guarantee. So a workbook is read
    once, and what stands in for the second reading is the round-trip
    gate, which builds a workbook with a seeded script, describes it,
    and reads the description back with openpyxl and pandas as
    DEVELOPMENT oracles that `src` never imports.

    THE PERSON'S DECLARATIONS REACH A WORKBOOK TOO (plan P4-D165, P4-D170).
    `--first-row data` and the validator's request for positional
    refusals were both dropped on this branch: a person who said their
    first row was a record still had it published as names, and a
    checked workbook's refusal printed its sheets' names. Both are
    honoured here, and an undeclared first row is held to the same
    question a delimited file's is -- a header whose cells read as a
    record stops the run and asks.

    A COLUMN MIXING HOW ITS CELLS ARE STORED IS REFUSED on the profile
    path (`workbook.mixed_storage`, plan P4-D166), because its twin
    could not keep which values were stored which way. The validate path
    measures such a file instead of refusing it: what it checks is what
    a description publishes, and a checked file is not described.
    """
    positions = refusals == REFUSALS_NAME_POSITIONS
    parts = opened_workbook(table_path, shown)
    reading = workbook.read_parts(parts, shown, wanted, positions)
    # THE WORDS THIS RUN READS AS NO VALUE, asked once of the sheet's own
    # spellings and handed to every reading of it (the repair of review
    # item 3 of landing R3): clock times beside `NA` are clock times.
    no_value = no_value_spellings(
        reading,
        taxonomy.Settings() if missing_under is None else missing_under,
    )
    records = first_row == FIRST_ROW_DATA
    # WHICH ROW HOLDS THE NAMES, WHERE ROWS OF ONE CELL STAND ABOVE THEM
    # (plans P4-D174, P4-D186). A row of one cell above the header rule's
    # row is furniture where a text file's line would be -- a title
    # holding a space, a comment, a blank -- and the names otherwise; the
    # person's `--first-row names` says the first row holds them, and the
    # validator settles it by the description it checks against. The
    # row taken as names then meets the question below, as a text file's
    # header does.
    # WHERE THE DESCRIPTION'S RECORDS START BELOW FURNITURE (plan
    # P4-D232). A checked description whose names are synthtwin's own
    # still says how many rows stood above the table, and a reading that
    # took every row from the sheet's first would hold those rows as
    # records -- so the file the description was written from would miss
    # its own row count. Asked this way the two readings are one.
    from_header = records and positions and published_header > 1
    sheet = workbook.table_of(
        reading, shown, records and not from_header,
        names_on_top=first_row == FIRST_ROW_NAMES and not positions,
        published_header=published_header if positions else 0,
        records_from_the_header=from_header,
        no_value=no_value,
    )
    if not sheet.columns:
        if positions:
            raise errors.ProfileError(
                errors.checked_workbook_sheet_is_empty(
                    shown, _sheet_position(reading)
                )
            )
        raise errors.ProfileError(
            errors.workbook_sheet_is_empty(shown, reading.chosen)
        )
    if not sheet.n_rows:
        raise errors.shape_refusal(
            errors.no_data_rows(shown), errors.NO_DATA_TO_DESCRIBE
        )
    names = list(sheet.names)
    source = HEADER_FROM_FILE
    evidence = _TAKEN_BY_CONVENTION
    # WHICH ROW HOLDS THE NAMES IS AN ASSUMPTION HERE TOO, unless the
    # person said. The header is found by `workbook.table_of`'s rule,
    # which is what a person means by a header and what the probe
    # workbooks show, but nothing about a row of cells makes it names
    # rather than a record -- so it is published as the assumption it
    # is, exactly as the first row of a CSV file is.
    by_convention = True
    if records:
        names = _generated_column_names(len(sheet.columns))
        source = HEADER_GENERATED
        evidence = _SAID_DATA
        by_convention = False
    elif first_row == FIRST_ROW_NAMES:
        evidence = _SAID_NAMES
        by_convention = False
    found = _Reading(
        column_names=names,
        columns=sheet.columns,
        n_rows=sheet.n_rows,
        # A workbook's text is the markup's own, which is UTF-8 whatever
        # the file's bytes were packed as, so the encoding question a
        # delimited file asks does not arise and no fallback was taken.
        encoding=dialect.ENCODING_UTF8,
        used_fallback_encoding=False,
        header_source=source,
        header_evidence=evidence,
        header_by_convention=by_convention,
        survey=None,
        book=reading,
        sheet=sheet,
    )
    # THE QUESTION IS ASKED, AND THE PUBLISHED SENTENCE IS NOT MOVED. A
    # header whose cells read as a record stops the run here as it does
    # on a delimited file; one that does not keeps the sentence a
    # workbook has always published, so a description that described
    # the same book before this rule describes it the same way now.
    seen = ""
    if source == HEADER_FROM_FILE and not positions:
        spoken, by_convention, seen = _settle_the_first_row(
            found, shown, first_row, floor
        )
        if seen:
            # THE SHEET IS READ AGAIN AS A SHEET WITH NO NAMES IN IT
            # (the owner's ruling of 2026-09-17, item 8; plan P4-D232),
            # for the reason the delimited path gives: the row taken as
            # names is kept as the record it may be, the columns are
            # named `column_1`, `column_2` and so on, and no text of
            # that row reaches the description. `table_of` is asked for
            # the records reading, so the sheet's own facts -- which row
            # the table starts at, how many rows stand above it -- are
            # the facts of the reading that stands.
            sheet = workbook.table_of(
                reading, shown, records_from_the_header=True,
                no_value=no_value,
            )
            names = _generated_column_names(len(sheet.columns))
            found = dataclasses.replace(
                found,
                column_names=names,
                columns=sheet.columns,
                n_rows=sheet.n_rows,
                header_source=HEADER_GENERATED,
                sheet=sheet,
            )
            spoken = _NOT_TOLD
            by_convention = False
        found = dataclasses.replace(
            found,
            header_evidence=spoken,
            header_by_convention=by_convention,
            first_row_seen=seen,
        )
    # A REFUSAL THAT NAMES A COLUMN WAITS UNTIL THERE ARE NAMES TO USE
    # (plan P4-D286, the repair of review item 7 of the files review of
    # 2026-09-18). This refusal used to stand above the first-row
    # question, and it names the column it refuses -- so on a sheet
    # whose first row cannot be told from a record, it quoted a cell of
    # that record in a message printed on the screen, which is exactly
    # what the owner's eighth ruling forbids. MEASURED: a sheet holding
    # a text and 12 in row 1, a date-formatted 45000 and 11 in row 2 and
    # an ordinary 20 and 13 in row 3 refused with "The column '...' ..."
    # naming the row-1 text, although 12 standing among 11 and 13 is the
    # record evidence that ruling 8 answers with placeholder names.
    # Asked here, the names are the ones the reading settled on --
    # `column_1`, `column_2` and so on where the row could not be told
    # -- and the sheet asked is the one that stands.
    if not positions:
        settled = found.sheet
        if settled is not None:
            mixed = workbook.mixed_storage(settled)
            if mixed is not None:
                raise errors.ProfileError(
                    errors.workbook_column_mixes_storage(
                        shown, found.column_names[mixed[0]], mixed[1],
                        mixed[2],
                    )
                )
            # ...AND THE MIX ONE LEVEL DOWN (plan P4-D283): two number
            # format codes of one kind, each worn by the line. The
            # description carries one code per column, so the twin would
            # dress every cell in the commoner of them.
            dressed = workbook.mixed_number_formats(settled, floor)
            if dressed is not None:
                raise errors.ProfileError(
                    errors.workbook_column_mixes_number_formats(
                        shown, found.column_names[dressed[0]]
                    )
                )
    return Table(
        column_names=found.column_names,
        columns=found.columns,
        n_rows=found.n_rows,
        encoding=found.encoding,
        used_fallback_encoding=found.used_fallback_encoding,
        header_source=found.header_source,
        header_evidence=found.header_evidence,
        header_by_convention=found.header_by_convention,
        first_row_seen=found.first_row_seen,
        survey=None,
        book=reading,
        sheet=found.sheet,
    )


def no_value_spellings(
    reading: "workbook.Reading", settings: "taxonomy.Settings"
) -> "frozenset[str]":
    """The spellings beside a sheet's stored times that this run reads as no value.

    THE CLOCKS ARE COUNTED OVER THE PRESENT CELLS (the repair of review
    item 3 of landing R3). A column of clock times stored as numbers is
    read as clocks where every value cell beside them is one
    (`workbook.table_of`), and a word such as `NA` is no value to the
    rest of the reading: counted as a value, 31 `NA` cells beside 969
    whole-minute clocks left the column numbers, and its twin read back
    as 968 times and a date-time, 968 of them off the minute, with no
    miss reported. So the spellings `taxonomy.missing_cells` takes out
    under ``settings`` -- the vocabulary's words, and those named with
    `--missing-value` -- are handed to the reader, which asks the rule
    `split_missing` asks, by spelling, rather than a second one.

    Asked only of the value cells that are not numbers, in a sheet
    column holding a time-format number, each different spelling once:
    `taxonomy.missing_cells` costs 1.6 to 1.8 s of CPU over a million
    cells, and a sheet storing no time needs none of it.

    Guarantees: accepts a workbook reading and the run's settings;
    returns the spellings taken out. Determinism: a fixed function of the
    two. Raises nothing. No I/O of any kind.
    """
    kinds_of: "dict[str, str]" = {}
    timed: "dict[int, bool]" = {}
    for cell in reading.cells:
        if cell.kind != workbook.CELL_NUMBER:
            continue
        code = cell.number_format
        if code not in kinds_of:
            kinds_of[code] = workbook.format_kind(code)
        if kinds_of[code] == workbook.FORMAT_TIME:
            timed[cell.column] = True
    if not timed:
        return frozenset()
    asked: "dict[str, bool]" = {}
    for cell in reading.cells:
        if cell.column not in timed or cell.kind == workbook.CELL_NUMBER:
            continue
        if cell.kind not in dialect.SHEET_VALUE_CLASSES:
            continue
        asked[workbook.spelled(cell.kind, cell.text)] = True
    spellings = sorted(asked)
    marks = taxonomy.missing_cells(spellings, settings)
    taken: "list[str]" = []
    for place in range(len(spellings)):
        if marks[place]:
            taken += [spellings[place]]
    return frozenset(taken)


def _sheet_position(reading: "workbook.Reading") -> int:
    """Where the chosen sheet stands in workbook order, counting from one."""
    for index in range(len(reading.sheets)):
        if reading.sheets[index].name == reading.chosen:
            return index + 1
    return 0


def read_table(
    raw_path: str,
    first_row: str = FIRST_ROW_AUTOMATIC,
    refusals: str = REFUSALS_MAY_QUOTE,
    encoding: str = "",
    sheet: str = "",
    metadata_rows: int = 0,
    decimal_comma_columns: "tuple[str, ...]" = (),
    metadata_rows_confirmed: bool = False,
    declared_delimiter: str = "",
    published_header: int = 0,
    small_cell_floor: int = parsing.DEFAULT_SMALL_CELL_FLOOR,
    missing_under: "taxonomy.Settings | None" = None,
    in_groups: bool = False,
) -> Table:
    """Read a CSV table from a local path; return it as text.

    ``in_groups`` (lane SR, plan P4-D400; `synthtwin profile` passes it)
    reads delimited text a line at a time, never holding its bytes or its
    text whole, and a table too large for one group of columns
    (`GROUP_BYTES`) one group at a time: the Table then holds one group
    and every column is asked of `column_values`. The reading, every
    refusal and every value are the ones read without it.

    ``missing_under`` is the settings the run reads missing values under,
    and a workbook alone wants them (the repair of review item 3 of
    landing R3): a column of clock times stored as numbers is read as
    clocks where every PRESENT value cell beside them is one, and a word
    those settings read as no value -- `NA`, or one named with
    `--missing-value` -- is not present (`no_value_spellings`). Left
    out, the defaults are asked (`taxonomy.Settings()`); `synthtwin
    profile` passes the person's settings and the validator the ones
    the description records, so a checked twin is read the way its
    source was.

    ``small_cell_floor`` is the person's smallest group, and the reader
    wants it for two questions, one per path it can take. On a workbook
    (plan P4-D283): whether a column wears two number formats of one
    kind, each worn by enough cells to be a population of the column
    rather than the stray cell the owner's sixth ruling absorbs. On a
    delimited file (plan P4-D290): the written form carries counts and
    positions of its own lines, and those are held to the one disclosure
    rule like every other count synthtwin publishes. Left out, it is the
    default floor (`parsing.DEFAULT_SMALL_CELL_FLOOR`, 11 since plan
    P4-D316), and both questions are asked at it. At a floor of one the
    workbook question is asked at the smallest line a census ever uses,
    and the delimited file's line rules are NOT asked at all, because the
    repair pass of 2026-09-18 gated them on a floor above one (plan
    P4-D290, amendment b). A caller describing a table at any floor but
    the default passes that floor here, as `synthtwin profile` and the
    validator both do, or the form it reads is one no description at
    that floor publishes.

    ``published_header`` is the validator's alone: the row a workbook
    description puts its names on, which settles a checked workbook's
    header where the sheet leaves it unsettled (plan P4-D174).

    ``encoding``, where given, is a description's published encoding,
    and the bytes are read in it wherever they can be
    (`dialect.decoded_as`); the validator passes it, so a checked file
    is read the way the description's labels were. Otherwise the
    encoding is detected (`dialect.decoded`).

    Guarantees:

    - Inputs: ``raw_path`` is the path the user typed. It is validated
      by `validate_local_path` (plan D6.1) before anything opens it, so
      a URL, a shared-network location, or a Windows device path is
      refused before any filesystem call happens. ``first_row`` is
      FIRST_ROW_AUTOMATIC (decide by the rule in this module's
      docstring), FIRST_ROW_NAMES (the first row holds the column
      names), or FIRST_ROW_DATA (the first row is a record; the columns
      are named ``column_1``, ``column_2``, ... and every record is
      kept). ``refusals`` is REFUSALS_MAY_QUOTE (this is the person's
      own table, so a refusal may name what was read back) or
      REFUSALS_NAME_POSITIONS (this file was only pointed at, so every
      refusal names which column and which row and never a value -- the
      validate path, plan P3-D1 and V9).
    - Agreement: the returned values are the standard library reader's,
      and every one of them has been compared against a second,
      independent read by pandas, together with the column names and
      the shape. A single difference anywhere is a refusal. Equal row
      and column counts are NOT accepted as agreement (review item
      P1-R1-F4).
    - Header: three outcomes, in this order (the module docstring gives
      the reasoning and the rules). A caller who passed
      FIRST_ROW_NAMES or FIRST_ROW_DATA settles it, in both directions,
      with no question asked. Otherwise, if the file shows the first row
      is a RECORD -- in any column its value is a number lying among
      that column's numbers, a date among that column's dates, or a
      value the column repeats below it -- the read stops and asks,
      offering ``--first-row names`` and ``--first-row data``, and
      nothing is read or written (review items P1-R1-F5, P1-R6-F6).
      Otherwise the first row is taken as the column names BY
      CONVENTION, which is how a CSV file is normally written; that is
      an assumption and is published as one, as
      ``header_by_convention`` True and as one plain sentence in
      ``header_evidence`` that says the names were taken by convention
      and that ``--first-row data`` re-reads the row as a record. No
      claim of evidence for the names reading is ever made, because
      none can be: there is nothing about a value that makes it a name.
      Whichever way it is settled, the returned Table carries
      ``header_source``, ``header_evidence`` and
      ``header_by_convention``, and a publisher must show the second
      and third beside the first.
    - Memory: NOT bounded, and this is the honest statement of it
      rather than the streaming claim P1-D3 used to make. Since plan
      P4-D86 the authoritative pass holds the file's bytes, its text and
      its lines while it fills the whole table as text, and while the
      checking pass runs the second reader's copy is held beside it.
      That moment is the peak. The measurements below were taken before
      P4-D86 added the file's text to it. Measured as peak resident growth over the
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
      wrong-length rows no rule of the written form accounts for, a
      form past one of its caps, an over-long
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
    if refusals not in (REFUSALS_MAY_QUOTE, REFUSALS_NAME_POSITIONS):
        # Not a refusal in the catalog either: nobody types this word.
        # Defaulting a misspelt one to the quoting form would let a
        # refusal on the validate path print a string out of a file
        # nobody promised was the reader's, which is the whole point of
        # the argument.
        raise ValueError(
            "synthtwin internal check: refusals must be 'quote' or "
            "'positions'."
        )
    validated = validate_local_path(raw_path, purpose="input")
    table_path = pathlib.Path(validated)
    shown = f"{table_path}"
    if not table_path.exists():
        raise errors.ProfileError(errors.file_missing(shown))
    if table_path.is_dir():
        raise errors.ProfileError(errors.path_is_a_folder(shown))
    # WHICH KIND OF FILE THIS IS, DECIDED BY ITS OPENING BYTES AND NEVER
    # BY ITS NAME (plan P4-D77). The study measured why: many exports
    # named `.xls` hold HTML or 2003 markup, an encrypted workbook is a
    # compound file whatever it is called, and a `.xlsm` is an ordinary
    # package. A reader that trusted the ending would tell all three of
    # those people the wrong thing about their file.
    # THE FILE IS READ ONCE. The kind is decided from the same bytes the
    # delimited reading then uses, so a table is not opened twice to ask
    # what it is, and the bytes reach `Path.read_bytes` -- the one
    # accepted way to read a whole file in this package -- rather than a
    # handle this audit cannot trace. Read in groups (lane SR, plan
    # P4-D400), the kind is decided from the file's first bytes alone,
    # read as its lines are.
    if in_groups:
        try:
            opening = _opening_of(table_path)
        except PermissionError as error:
            raise errors.ProfileError(
                errors.file_unreadable(shown, f"{error}")
            ) from error
        except OSError as error:
            raise errors.ProfileError(
                errors.file_unreadable(shown, f"{error}")
            ) from error
        grouped_kind = workbook.kind_of(opening)
        workbook.refuse_by_kind(grouped_kind, shown)
        if grouped_kind != workbook.KIND_PACKAGE:
            try:
                return _read_in_groups(
                    raw_path, table_path, shown, first_row, refusals,
                    encoding, metadata_rows, decimal_comma_columns,
                    metadata_rows_confirmed, declared_delimiter,
                    small_cell_floor,
                )
            except PermissionError as error:
                raise errors.ProfileError(
                    errors.file_unreadable(shown, f"{error}")
                ) from error
            except OSError as error:
                raise errors.ProfileError(
                    errors.file_unreadable(shown, f"{error}")
                ) from error
    try:
        data = table_path.read_bytes()
    except MemoryError as error:
        raise errors.ProfileError(
            errors.out_of_memory(shown, _file_size(table_path))
        ) from error
    except PermissionError as error:
        raise errors.ProfileError(
            errors.file_unreadable(shown, f"{error}")
        ) from error
    except OSError as error:
        raise errors.ProfileError(
            errors.file_unreadable(shown, f"{error}")
        ) from error
    kind = workbook.kind_of(data[:_OPENING_BYTES])
    workbook.refuse_by_kind(kind, shown)
    if kind == workbook.KIND_PACKAGE:
        # A WORKBOOK HAS NO DELIMITER TO DECLARE (plan P4-D110). Its
        # cells are cells, so `--delimiter` given on one is a mistake
        # about the file, and it is refused rather than ignored: a
        # declaration a tool quietly ignores is worse than one it
        # refuses.
        if declared_delimiter:
            raise errors.ProfileError(
                errors.delimiter_declared_on_a_workbook(shown)
            )
        return _read_workbook_table(
            f"{table_path}", shown, sheet, first_row, refusals,
            published_header,
            missing_under=missing_under,
            floor=small_cell_floor,
        )
    try:
        found = _read_authoritatively(
            table_path, shown, first_row, refusals, encoding, data,
            metadata_rows, decimal_comma_columns, metadata_rows_confirmed,
            declared_delimiter, small_cell_floor,
        )
    except PermissionError as error:
        raise errors.ProfileError(
            errors.file_unreadable(shown, f"{error}")
        ) from error
    except OSError as error:
        raise errors.ProfileError(
            errors.file_unreadable(shown, f"{error}")
        ) from error

    try:
        _check_against_pandas(raw_path, found, shown, refusals)
    except MemoryError as error:
        # The checking pass holds the second reading beside the first,
        # which is the moment this reader uses the most memory. Running
        # out here is a size problem, not a bug, and it gets the
        # size-aware refusal rather than a traceback (review item
        # P1-R1-F15).
        raise errors.ProfileError(
            errors.out_of_memory(shown, _file_size(table_path))
        ) from error
    seen = ""
    if found.header_source == HEADER_FROM_FILE:
        spoken, by_convention, seen = _settle_the_first_row(
            found, shown, first_row, small_cell_floor
        )
        if seen:
            # THE FILE IS WALKED AGAIN, AS A FILE WITH NO NAMES IN IT
            # (the owner's ruling of 2026-09-17, item 8; plan P4-D232).
            # The first walk had to read the row as names to ask the
            # question at all -- the three record rules compare it with
            # the values below it -- and the answer is that it may be a
            # record, so the walk that stands is the one that keeps it
            # as one. Nothing is patched into the first reading: the
            # survey's own account of the file, its written names among
            # it, is built again under the answer, which is why
            # `source.dialect` then names no written name and no text of
            # that row survives anywhere. A second walk is what `settle`
            # already does where the first walk shows a guess was wrong.
            found = _read_authoritatively(
                table_path, shown, FIRST_ROW_DATA, refusals, encoding, data,
                metadata_rows, decimal_comma_columns,
                metadata_rows_confirmed, declared_delimiter,
                small_cell_floor,
            )
            _check_against_pandas(raw_path, found, shown, refusals)
            spoken = _NOT_TOLD
            by_convention = False
        found = dataclasses.replace(
            found,
            header_evidence=spoken,
            header_by_convention=by_convention,
            first_row_seen=seen,
        )
    return Table(
        column_names=found.column_names,
        columns=found.columns,
        n_rows=found.n_rows,
        encoding=found.encoding,
        used_fallback_encoding=found.used_fallback_encoding,
        header_source=found.header_source,
        header_evidence=found.header_evidence,
        header_by_convention=found.header_by_convention,
        first_row_seen=found.first_row_seen,
        survey=found.survey,
    )


# -- a large table, read in groups of columns (lane SR, plan P4-D400) --
#
# THE OWNER'S BIG TABLE MUST FIT THE MACHINE (the owner, 2026-10-16:
# 2,000,000 rows by 50 columns within twelve hours, under the 2.5 GB a
# process may hold). Holding a table as text costs a Python object a cell
# -- about 4.4 KB a row on the made-up health table of fifty columns,
# about 8.7 GB at two million rows -- so `synthtwin profile` reads such a
# table ONE GROUP OF COLUMNS AT A TIME: the file is read once to learn its
# encoding and its shape, once for each group to walk, check and hold
# that group's columns, and once more for each group a later step asks
# for again (`column_values`). No real value is ever written anywhere:
# the file itself is read again, its lines decoded as they are read, and
# its text is never held whole. Every reading of it is compared with the
# first -- its size, the moment it was last changed, how many lines and a
# digest of them -- and a file that changed in between is refused, so two
# versions of it are never mixed.

# How many bytes the cells of one group may take, at most, by the
# measured cost below. Tests lower it to read small tables in groups.
GROUP_BYTES = 512 * 1024 * 1024

# What one cell costs beside its characters, held as a column: its place
# in the column's list (8 bytes), its quoting flag in the survey (1) and,
# where its text is held on its own, a Python text object's header (56,
# rounded as the allocator rounds it). Measured on the made-up health
# table and the Gaussian table at 200,000 rows by 50 columns
# (`tools/measurements/kpi_describe_groups.py`).
_CELL_BYTES = 65

# How many groups one walk of the sweep holds at once. A walk holds its
# group's cells and no column's description, which at two million rows
# holds more than three groups' cells, so the sweep walks three groups at
# a time and the file is walked a third as often (`_sweep`).
_GROUPS_A_WALK = 3

# The text's first characters the survey's detection reads: a MiB past a
# separator line of at most seven characters, and some.
_HEAD_CHARACTERS = 1_048_576 + 64

# The opening bytes `workbook.kind_of` reads.
_OPENING_CHARACTERS = 8

# The digest of a reading of the file's lines: each line's hash folded in
# turn, modulo a prime. It is compared within one run only, so the hash
# need not be the same from one run to the next.
_DIGEST_STEP = 1_000_003
_DIGEST_MODULUS = (1 << 61) - 1

# The characters that make a Latin-1 reading a Windows-1252 one where
# that reading stands (`dialect.decoded`): bytes 0x80 to 0x9F.
_WINDOWS_ONLY = (
    "\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f"
    "\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f"
)


@dataclasses.dataclass
class _Pass:
    """What one reading of the file's lines saw: how many, their digest, and whether it reached the end."""

    digest: int = 0
    lines: int = 0
    done: bool = False


@dataclasses.dataclass(frozen=True)
class _Facts:
    """What the first reading of a file found, which every later reading must find again.

    ``codec`` reads the file's bytes as the encoding ``encoding`` names,
    from its first byte, so a byte-order mark comes through as its one
    character, which ``marked`` says to take off the first line.
    ``characters`` counts the text without that mark, ``size`` and
    ``last`` without an end-of-file mark too, which ``end_mark`` says the
    text ends with; ``head`` is the text's first characters
    (`dialect.Streamed`). ``zero``, ``breaks`` and ``high`` say whether
    the text holds a zero character, a line break, and (read as Latin-1)
    a byte between 0x80 and 0x9F. ``lines`` and ``digest`` are the
    reading's (`_Pass`), and ``file_bytes`` and ``changed_at`` the file's
    size and the moment it last changed.
    """

    codec: str
    encoding: str
    marked: bool
    characters: int
    size: int
    last: str
    end_mark: bool
    head: str
    zero: bool
    breaks: bool
    high: bool
    lines: int
    digest: int
    file_bytes: int
    changed_at: int


@dataclasses.dataclass
class ColumnSource:
    """Where `column_values` finds a table read in groups of columns.

    ``path`` is the validated path of the file, ``shown`` the path as the
    person wrote it, ``facts`` what its first reading found and
    ``survey`` the reading of every column, gathered from each group's
    walk; ``headed`` says the first record is the column names;
    ``groups`` are the groups, each from its first column to the one past
    its last; and ``held`` holds the columns of the one group starting at
    ``held_from`` -- the only cells of the table held at all.
    """

    path: str
    shown: str
    facts: _Facts
    survey: dialect.Survey
    headed: bool
    groups: "tuple[tuple[int, int], ...]"
    held_from: int
    held: "list[list[str]]"


def column_values(table: Table, place: int) -> "list[str]":
    """One column's values, in row order: THE way to ask a table for a column.

    THE GENERIC COLUMN ACCESS (lane SR, plan P4-D400). Where the table
    was read whole it hands over its column. Where it was read in groups
    (`Table.source`), the group holding the column is held -- the one
    already held, or, letting that one go first, the group read from
    the file again, with the standard reader as the survey's form
    configures it, whose every value the reading held equal to the
    survey's. Any column can be asked for any number of times, in any
    order; asking in column order reads each group once. What is held is
    one group's columns: a caller that keeps a column it was handed while
    asking for another group keeps that column alive beside it.

    Guarantees: returns the column's values exactly as `read_table`
    read them. Raises ProfileError where the file changed since it was
    first read (`errors.file_changed_while_read`) or can no longer be
    read; IndexError for a place past the last column. Reads the file
    only for a table read in groups.
    """
    source = table.source
    if source is None:
        return table.columns[place]
    if not source.held_from <= place < source.held_from + len(source.held):
        for start, end in source.groups:
            if start <= place < end:
                source.held = []
                source.held = _read_group(source, start, end)
                source.held_from = start
    return source.held[place - source.held_from]


def column_groups(table: Table) -> "tuple[tuple[int, int], ...]":
    """The groups `column_values` holds at a time, each from its first column to the one past its last.

    A table read whole is one group. A step that walks every column
    walks them group by group, in order, so each group is read once.
    """
    if table.source is None:
        return ((0, len(table.column_names)),)
    return table.source.groups


def _read_group(source: ColumnSource, start: int, end: int) -> "list[list[str]]":
    """The columns ``start`` to ``end`` of a table read in groups, read from its file again.

    The records are the standard reader's, as `_standard_records` places
    them -- the records the reading's check held equal to the survey's
    value by value -- and the file is the one first read, which is
    checked once it has been read (`_unchanged`). A text met again in a
    column is held once, as the survey holds it (lane S4d, plan P4-D390),
    up to `parsing.SPELLING_MEMO_TEXTS` texts a column.
    """
    table_path = pathlib.Path(source.path)
    run = _Pass()
    held: "list[list[str]]" = [[] for _place in range(start, end)]
    memos: "list[dict[str, str]]" = [{} for _place in range(start, end)]
    previous_limit = csv.field_size_limit()
    try:
        csv.field_size_limit(FIELD_SIZE_LIMIT)
        try:
            for kind, cells in _standard_records(
                _text_lines(table_path, source.facts, run),
                source.survey,
                source.headed,
            ):
                if kind != _RECORD_DATA:
                    continue
                for place in range(start, end):
                    value = cells[place]
                    memo = memos[place - start]
                    if value in memo:
                        value = memo[value]
                    elif len(memo) < parsing.SPELLING_MEMO_TEXTS:
                        memo[value] = value
                    held[place - start] += [value]
        except (OSError, UnicodeDecodeError) as error:
            raise errors.ProfileError(
                errors.file_changed_while_read(source.shown)
            ) from error
    finally:
        csv.field_size_limit(previous_limit)
    _unchanged(table_path, source.facts, run, source.shown)
    return held


def _stat_of(table_path: pathlib.Path) -> "tuple[int, int]":
    """The file's size in bytes and the moment it last changed, in nanoseconds."""
    file_path = pathlib.Path(table_path)
    seen = file_path.stat()
    return int(seen.st_size), int(seen.st_mtime_ns)


def _opened_lines(
    table_path: pathlib.Path, codec: str, run: _Pass
) -> "typing.Iterator[str]":
    """The file's lines as ``codec`` decodes them, one at a time, never the whole text.

    Read as a file opened with ``newline=""`` hands them over -- a line
    ends after a line feed, after a carriage return with no line feed
    behind it, or after the pair -- which is exactly how
    `dialect.physical_lines` cuts a decoded text, and decoded strictly,
    so a byte the codec does not read raises as decoding the whole file
    raises. ``run`` is given the count and the digest once the last line
    is read. The path is validated again here, immediately before it is
    opened.
    """
    validated = validate_local_path(f"{table_path}", purpose="input")
    file_path = pathlib.Path(validated)
    digest = 0
    count = 0
    with file_path.open("r", encoding=codec, errors="strict", newline="") as handle:
        for line in handle:
            digest = (digest * _DIGEST_STEP + hash(line)) % _DIGEST_MODULUS
            count = count + 1
            yield line
    run.digest = digest
    run.lines = count
    run.done = True


def _opening_of(table_path: pathlib.Path) -> bytes:
    """The file's first bytes, read as Latin-1, whose characters are its bytes one for one."""
    run = _Pass()
    found = ""
    for line in _opened_lines(table_path, "latin-1", run):
        found = found + line
        if len(found) >= _OPENING_CHARACTERS:
            break
    return bytes([ord(character) for character in found[:_OPENING_CHARACTERS]])


def _facts_under(
    table_path: pathlib.Path, shown: str, codec: str, encoding: str, marked: bool
) -> "_Facts | None":
    """The file read once under ``codec``: its `_Facts`, or None where the codec cannot read it."""
    run = _Pass()
    file_bytes, changed_at = _stat_of(table_path)
    text_head = ""
    characters = 0
    tail = ""
    zero = False
    high = False
    first = True
    try:
        for line in _opened_lines(table_path, codec, run):
            if first:
                first = False
                if marked:
                    line = line[1:]
            if len(text_head) < _HEAD_CHARACTERS:
                text_head = text_head + line
            characters = characters + len(line)
            if len(line) >= 2:
                tail = line[len(line) - 2 :]
            elif line:
                tail = tail[len(tail) - 1 :] + line
            if not zero and "\x00" in line:
                zero = True
            if encoding == dialect.ENCODING_LATIN1 and not high:
                for character in _WINDOWS_ONLY:
                    if character in line:
                        high = True
                        break
    except UnicodeDecodeError:
        return None
    if _stat_of(table_path) != (file_bytes, changed_at):
        raise errors.ProfileError(errors.file_changed_while_read(shown))
    end_mark = tail[len(tail) - 1 :] == "\x1a"
    size = characters - 1 if end_mark else characters
    last = tail[len(tail) - 2 : len(tail) - 1] if end_mark else tail[len(tail) - 1 :]
    if len(text_head) > size:
        text_head = text_head[:size]
    return _Facts(
        codec=codec,
        encoding=encoding,
        marked=marked,
        characters=characters,
        size=size,
        last=last,
        end_mark=end_mark,
        head=text_head,
        zero=zero,
        breaks=run.lines >= 2 or tail[len(tail) - 1 :] in ("\r", "\n"),
        high=high,
        lines=run.lines,
        digest=run.digest,
        file_bytes=file_bytes,
        changed_at=changed_at,
    )


def _file_facts(table_path: pathlib.Path, shown: str, encoding: str) -> _Facts:
    """The file's encoding, chosen as `dialect.decoded` and `dialect.decoded_as` choose it, and its `_Facts`.

    Each encoding those two try is tried here in their order, by reading
    the file a line at a time under it rather than decoding its whole
    bytes, so the one chosen is theirs: a description's published
    Latin-1 or Windows-1252 where the file reads in it (``encoding``,
    the validator's); a UTF-32 mark refused; UTF-16 behind its mark,
    where the text holds a line break and no zero character; UTF-8,
    behind its mark or not; Windows-1252 where a byte between 0x80 and
    0x9F stands and it reads them all; and Latin-1, which reads any
    bytes.
    """
    if encoding in dialect.FALLBACK_ENCODINGS:
        found = _facts_under(
            table_path, shown, dialect.WRITING_CODECS[encoding], encoding, False
        )
        if found is not None:
            return found
    opening = _opening_of(table_path)
    if opening[:4] == b"\x00\x00\xfe\xff" or opening[:4] == b"\xff\xfe\x00\x00":
        raise errors.ProfileError(errors.looks_like_utf16(shown))
    if opening[:2] == b"\xff\xfe" or opening[:2] == b"\xfe\xff":
        wide = (
            dialect.ENCODING_UTF16_LE
            if opening[:2] == b"\xff\xfe"
            else dialect.ENCODING_UTF16_BE
        )
        found = _facts_under(table_path, shown, wide, wide, True)
        if (
            found is not None
            and found.characters
            and not found.zero
            and found.breaks
        ):
            return found
    found = _facts_under(
        table_path,
        shown,
        "utf-8",
        dialect.ENCODING_UTF8,
        opening[:3] == b"\xef\xbb\xbf",
    )
    if found is not None:
        return found
    latin = _facts_under(
        table_path, shown, "latin-1", dialect.ENCODING_LATIN1, False
    )
    if latin is None:
        raise errors.ProfileError(errors.looks_like_utf16(shown))
    if latin.high:
        found = _facts_under(
            table_path, shown, "cp1252", dialect.ENCODING_CP1252, False
        )
        if found is not None:
            return found
    return latin


def _text_lines(
    table_path: pathlib.Path, facts: _Facts, run: _Pass
) -> "typing.Iterator[str]":
    """The text's lines as the survey reads them: past the byte-order mark, before the end-of-file mark.

    `dialect.physical_lines` of the decoded text the whole-file reading
    walks: the mark's character is taken off the first line, and the
    end-of-file mark off the last, a line it leaves empty not handed
    over at all.
    """
    first = True
    started = False
    pending = ""
    for line in _opened_lines(table_path, facts.codec, run):
        if first:
            first = False
            if facts.marked:
                line = line[1:]
            if not line:
                continue
        if started:
            yield pending
        pending = line
        started = True
    if started:
        if facts.end_mark:
            pending = pending[: len(pending) - 1]
        if pending:
            yield pending


def _streamed(
    table_path: pathlib.Path, facts: _Facts, run: _Pass
) -> dialect.Streamed:
    """The text as the survey walks it a line at a time (`dialect.Streamed`)."""
    return dialect.Streamed(
        head=facts.head,
        size=facts.size,
        last=facts.last,
        end_mark=facts.end_mark,
        lines=_text_lines(table_path, facts, run),
    )


def _unchanged(
    table_path: pathlib.Path, facts: _Facts, run: _Pass, shown: str
) -> None:
    """Refuse a reading that was not a reading of the file first read, to its end."""
    if (
        not run.done
        or run.lines != facts.lines
        or run.digest != facts.digest
        or _stat_of(table_path) != (facts.file_bytes, facts.changed_at)
    ):
        raise errors.ProfileError(errors.file_changed_while_read(shown))


def _whole_text(
    table_path: pathlib.Path, shown: str, facts: _Facts, encoding: str
) -> str:
    """The file's whole text, for a file the survey walks more than once (`dialect.WalkAgain`).

    Decoded exactly as before this lane, and held to the first reading:
    the same encoding, the same lines and the same digest.
    """
    file_path = pathlib.Path(table_path)
    try:
        data = file_path.read_bytes()
    except MemoryError as error:
        raise errors.ProfileError(
            errors.out_of_memory(shown, _file_size(table_path))
        ) from error
    if encoding:
        text, found, marked = dialect.decoded_as(data, shown, encoding)
    else:
        text, found, marked = dialect.decoded(data, shown)
    size = len(data)
    data = b""
    run = _Pass()
    digest = 0
    count = 0
    for line in dialect.lines_in_turn(text):
        if not count and marked:
            line = "﻿" + line
        digest = (digest * _DIGEST_STEP + hash(line)) % _DIGEST_MODULUS
        count = count + 1
    if marked and not count:
        digest = hash("﻿") % _DIGEST_MODULUS
        count = 1
    run.digest = digest
    run.lines = count
    run.done = True
    if found != facts.encoding or marked != facts.marked or size != facts.file_bytes:
        raise errors.ProfileError(errors.file_changed_while_read(shown))
    _unchanged(table_path, facts, run, shown)
    return text


def _walk_a_group(
    table_path: pathlib.Path,
    shown: str,
    first_row: str,
    refusals: str,
    encoding: str,
    facts: _Facts,
    keep: "tuple[bool, ...] | None",
    metadata_rows: int,
    decimal_comma_columns: "tuple[str, ...]",
    metadata_rows_confirmed: bool,
    declared_delimiter: str,
    small_cell_floor: int,
) -> "tuple[_Reading, tuple[int, int, int] | None]":
    """`_read_authoritatively` for the group of columns ``keep`` names, the text read a line at a time.

    The survey walks the file's lines as they are read (`_streamed`) and
    holds the group's columns; the standard reader then reads the lines
    again and is held to them. A file the survey would walk twice is
    walked from its whole text instead, as before (`_whole_text`). With
    ``keep`` None every column is held and every difference refused as
    `_read_authoritatively` refuses it; otherwise the check's first
    difference in the group is returned for the reader to weigh
    (`_agrees_with_the_standard_reader`).
    """
    headed = first_row != FIRST_ROW_DATA
    found: "tuple[int, int, int] | None" = None
    previous_limit = csv.field_size_limit()
    try:
        csv.field_size_limit(FIELD_SIZE_LIMIT)
        try:
            try:
                run = _Pass()
                surveyed = dialect.settle(
                    "", facts.encoding, facts.marked, not headed, shown,
                    metadata_rows, decimal_comma_columns,
                    metadata_rows_confirmed, declared_delimiter,
                    small_cell_floor, keep=keep,
                    streamed=_streamed(table_path, facts, run),
                )
                _unchanged(table_path, facts, run, shown)
                if keep is None or True in keep:
                    checked = _Pass()
                    found = _agrees_with_the_standard_reader(
                        _text_lines(table_path, facts, checked),
                        surveyed, headed, shown, refusals, keep,
                    )
                    if found is None:
                        _unchanged(table_path, facts, checked, shown)
            except dialect.WalkAgain:
                text = _whole_text(table_path, shown, facts, encoding)
                surveyed = dialect.settle(
                    text, facts.encoding, facts.marked, not headed, shown,
                    metadata_rows, decimal_comma_columns,
                    metadata_rows_confirmed, declared_delimiter,
                    small_cell_floor, keep=keep,
                )
                if keep is None or True in keep:
                    found = _agrees_with_the_standard_reader(
                        _body_lines(text, surveyed.form), surveyed, headed,
                        shown, refusals, keep,
                    )
                text = ""
        except csv.Error as error:
            detail = f"{error}"
            if "field larger than field limit" in detail:
                raise errors.ProfileError(
                    errors.field_too_long(shown, FIELD_SIZE_LIMIT)
                ) from error
            if refusals == REFUSALS_NAME_POSITIONS:
                raise errors.ProfileError(
                    errors.checked_file_unreadable_as_csv(shown)
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
    if headed:
        names = list(dialect.named_columns(surveyed.header))
        source = HEADER_FROM_FILE
        evidence = _SAID_NAMES
    else:
        names = _generated_column_names(len(surveyed.columns))
        source = HEADER_GENERATED
        evidence = _SAID_DATA
    return (
        _Reading(
            column_names=names,
            columns=surveyed.columns,
            n_rows=surveyed.n_rows,
            encoding=facts.encoding,
            used_fallback_encoding=facts.encoding in dialect.FALLBACK_ENCODINGS,
            header_source=source,
            header_evidence=evidence,
            survey=surveyed,
        ),
        found,
    )


@dataclasses.dataclass
class _Swept:
    """What a sweep of the file's groups found: the reading, the groups, the group held, and each column's evidence about the first row."""

    reading: _Reading
    groups: "tuple[tuple[int, int], ...]"
    held_from: int
    held: "list[list[str]]"
    record_rules: "list[int]"
    names_shown: "list[bool]"


def _sweep(
    raw_path: str,
    table_path: pathlib.Path,
    shown: str,
    first_row: str,
    refusals: str,
    encoding: str,
    facts: _Facts,
    metadata_rows: int,
    decimal_comma_columns: "tuple[str, ...]",
    metadata_rows_confirmed: bool,
    declared_delimiter: str,
    small_cell_floor: int,
) -> "_Swept | None":
    """Walk and check a large table one group of columns at a time, or None where it fits one group.

    A file that may not fit in one group (`GROUP_BYTES`, by the cost of a
    cell -- `_CELL_BYTES` beside its characters) is first walked holding
    no column, which settles its shape; the groups are then as many
    columns as fit, and each is walked, checked by the standard reader
    and by pandas, and held in turn, the last group first, so the first
    is the one held at the end. What each check would refuse is weighed
    once every group is read, so the refusal is the one reading every
    column at once makes: the standard reader's first difference, a file
    of no records, then pandas' first.
    """
    headed = first_row != FIRST_ROW_DATA
    if facts.characters * (_CELL_BYTES + 1) <= GROUP_BYTES:
        return None
    plan, _nothing = _walk_a_group(
        table_path, shown, first_row, refusals, encoding, facts, (),
        metadata_rows, decimal_comma_columns, metadata_rows_confirmed,
        declared_delimiter, small_cell_floor,
    )
    width = len(plan.column_names)
    rows = plan.n_rows
    if not rows or not width:
        return None
    cost = _CELL_BYTES + facts.size // (rows * width)
    per_group = max(1, GROUP_BYTES // (rows * cost))
    if per_group >= width:
        return None
    groups = tuple(
        (start, min(width, start + per_group))
        for start in range(0, width, per_group)
    )
    walks = tuple(
        (groups[at][0], groups[min(at + _GROUPS_A_WALK, len(groups)) - 1][1])
        for at in range(0, len(groups), _GROUPS_A_WALK)
    )
    forms: "list[dialect.ColumnForm]" = [dialect.plain_column() for _place in range(width)]
    holds: "list[tuple[frozenset[str], ...]]" = [() for _place in range(width)]
    classified: "list[bool]" = [False for _place in range(width)]
    best_order: "dialect.RowOrder | None" = None
    record_rules: "list[int]" = [0 for _place in range(width)]
    names_shown: "list[bool]" = [False for _place in range(width)]
    asked_of_the_first_row = headed and first_row == FIRST_ROW_AUTOMATIC
    disagreements: "list[tuple[int, int, int]]" = []
    refused: "list[tuple[tuple[int, int], errors.ProfileError]]" = []
    held: "list[list[str]]" = []
    held_from = 0
    last: "_Reading | None" = None
    for start, end in reversed(walks):
        keep = tuple(start <= place < end for place in range(width))
        # The group held before is let go before the next is read.
        held = []
        last = None
        reading, found = _walk_a_group(
            table_path, shown, first_row, refusals, encoding, facts, keep,
            metadata_rows, decimal_comma_columns, metadata_rows_confirmed,
            declared_delimiter, small_cell_floor,
        )
        surveyed = reading.survey
        if surveyed is None:
            raise ValueError("synthtwin internal check: a reading without its survey")
        if found is not None:
            disagreements += [found]
        if not disagreements and reading.n_rows:
            refusal = _check_against_pandas(
                raw_path, reading, shown, refusals, keep, surveyed.first_cells
            )
            if refusal is not None:
                refused += [refusal]
        for place in range(start, end):
            forms[place] = surveyed.form.columns[place]
            holds[place] = surveyed.quoting_holds[place]
            classified[place] = surveyed.classified[place]
            if asked_of_the_first_row:
                record_rules[place] = _first_record_rule(
                    reading.column_names[place],
                    reading.columns[place],
                    small_cell_floor,
                )
                names_shown[place] = _names_shown(
                    reading.column_names[place], reading.columns[place]
                )
        found_order = surveyed.form.row_order
        if found_order.column and (
            best_order is None or found_order.column < best_order.column
        ):
            best_order = found_order
        # The walk's first group is held, the first walk's at the end:
        # the description starts there.
        held = [
            reading.columns[place]
            for place in range(start, min(width, start + per_group))
        ]
        held_from = start
        last = reading
    if last is None or last.survey is None:
        raise ValueError("synthtwin internal check: a sweep of no group")
    if disagreements:
        first = disagreements[0]
        for one in disagreements:
            if one < first:
                first = one
        _refuse_the_disagreement(first, last.survey, shown, refusals)
    if not last.n_rows:
        raise errors.shape_refusal(
            errors.no_data_rows(shown), errors.NO_DATA_TO_DESCRIBE
        )
    if refused:
        earliest = refused[0]
        for weighed in refused:
            if weighed[0] < earliest[0]:
                earliest = weighed
        raise earliest[1]
    order = last.survey.form.row_order if best_order is None else best_order
    gathered = dataclasses.replace(
        last.survey,
        form=dataclasses.replace(
            last.survey.form, columns=tuple(forms), row_order=order
        ),
        columns=[],
        quoting_holds=tuple(holds),
        classified=tuple(classified),
        kept=tuple(True for _place in range(width)),
    )
    return _Swept(
        reading=dataclasses.replace(last, columns=[], survey=gathered),
        groups=groups,
        held_from=held_from,
        held=held,
        record_rules=record_rules,
        names_shown=names_shown,
    )


def _first_row_settled_from(
    found: _Reading,
    first_row: str,
    record_rules: "list[int]",
    names_shown: "list[bool]",
) -> "tuple[str, bool, str]":
    """`_settle_the_first_row`, answered from each column's evidence kept as its group was read."""
    header = found.column_names
    if first_row != FIRST_ROW_AUTOMATIC:
        return found.header_evidence, False, ""
    numbers = [
        name for name in header if not parsing.looks_like_a_column_name(name)
    ]
    if len(numbers) == len(header):
        return _NOT_TOLD, False, EVERY_VALUE_A_NUMBER
    best = 0
    at = -1
    for index in range(len(header)):
        rule = record_rules[index]
        if rule and (not best or rule < best):
            best = rule
            at = index
    if best:
        return _NOT_TOLD, False, _record_words(best, at)
    for index in range(len(header)):
        if names_shown[index]:
            return (
                taxonomy.note(
                    taxonomy.HEADER_NAMES_SHOWN_BY_COLUMN, (index + 1,)
                ),
                False,
                "",
            )
    if _stood_under_furniture(found):
        return _NOT_TOLD, False, UNDER_FURNITURE
    return _TAKEN_BY_CONVENTION, True, ""


def _read_in_groups(
    raw_path: str,
    table_path: pathlib.Path,
    shown: str,
    first_row: str,
    refusals: str,
    encoding: str,
    metadata_rows: int,
    decimal_comma_columns: "tuple[str, ...]",
    metadata_rows_confirmed: bool,
    declared_delimiter: str,
    small_cell_floor: int,
) -> Table:
    """`read_table` of delimited text, never holding the file's text whole, and a large table one group of columns at a time.

    A table that fits one group is read as before, its text a line at a
    time: walked, checked by the standard reader and by pandas, its first
    row settled, and every column held. A larger one is swept a group at
    a time (`_sweep`) and handed over holding its first group, the rest
    asked of `column_values`. The reading, the refusals and every value
    are the ones `read_table` makes holding the whole file.
    """
    facts = _file_facts(table_path, shown, encoding)
    if facts.encoding in dialect.FALLBACK_ENCODINGS and _starts_with_a_byte_order_mark(
        facts.head
    ):
        raise errors.ProfileError(errors.looks_like_utf16(shown))
    if facts.zero:
        raise errors.ProfileError(errors.looks_like_utf16(shown))
    swept = _sweep(
        raw_path, table_path, shown, first_row, refusals, encoding, facts,
        metadata_rows, decimal_comma_columns, metadata_rows_confirmed,
        declared_delimiter, small_cell_floor,
    )
    if swept is None:
        found, _nothing = _walk_a_group(
            table_path, shown, first_row, refusals, encoding, facts, None,
            metadata_rows, decimal_comma_columns, metadata_rows_confirmed,
            declared_delimiter, small_cell_floor,
        )
        if not found.n_rows:
            raise errors.shape_refusal(
                errors.no_data_rows(shown), errors.NO_DATA_TO_DESCRIBE
            )
        _check_against_pandas(raw_path, found, shown, refusals)
        seen = ""
        if found.header_source == HEADER_FROM_FILE:
            spoken, by_convention, seen = _settle_the_first_row(
                found, shown, first_row, small_cell_floor
            )
            if seen:
                # Walked again as a file with no names in it, as
                # `read_table` walks it (plan P4-D232).
                found, _nothing = _walk_a_group(
                    table_path, shown, FIRST_ROW_DATA, refusals, encoding,
                    facts, None, metadata_rows, decimal_comma_columns,
                    metadata_rows_confirmed, declared_delimiter,
                    small_cell_floor,
                )
                if not found.n_rows:
                    raise errors.shape_refusal(
                        errors.no_data_rows(shown), errors.NO_DATA_TO_DESCRIBE
                    )
                _check_against_pandas(raw_path, found, shown, refusals)
                spoken = _NOT_TOLD
                by_convention = False
            found = dataclasses.replace(
                found,
                header_evidence=spoken,
                header_by_convention=by_convention,
                first_row_seen=seen,
            )
        return Table(
            column_names=found.column_names,
            columns=found.columns,
            n_rows=found.n_rows,
            encoding=found.encoding,
            used_fallback_encoding=found.used_fallback_encoding,
            header_source=found.header_source,
            header_evidence=found.header_evidence,
            header_by_convention=found.header_by_convention,
            first_row_seen=found.first_row_seen,
            survey=found.survey,
        )
    reading = swept.reading
    if reading.header_source == HEADER_FROM_FILE:
        spoken, by_convention, seen = _first_row_settled_from(
            reading, first_row, swept.record_rules, swept.names_shown
        )
        if seen:
            swept.held = []
            again = _sweep(
                raw_path, table_path, shown, FIRST_ROW_DATA, refusals,
                encoding, facts, metadata_rows, decimal_comma_columns,
                metadata_rows_confirmed, declared_delimiter, small_cell_floor,
            )
            if again is None:
                raise ValueError(
                    "synthtwin internal check: a table read in groups fits one"
                )
            swept = again
            reading = swept.reading
            spoken = _NOT_TOLD
            by_convention = False
        reading = dataclasses.replace(
            reading,
            header_evidence=spoken,
            header_by_convention=by_convention,
            first_row_seen=seen,
        )
    surveyed = reading.survey
    if surveyed is None:
        raise ValueError("synthtwin internal check: a reading without its survey")
    held = swept.held
    swept.held = []
    return Table(
        column_names=reading.column_names,
        columns=[],
        n_rows=reading.n_rows,
        encoding=reading.encoding,
        used_fallback_encoding=reading.used_fallback_encoding,
        header_source=reading.header_source,
        header_evidence=reading.header_evidence,
        header_by_convention=reading.header_by_convention,
        first_row_seen=reading.first_row_seen,
        survey=surveyed,
        source=ColumnSource(
            path=f"{table_path}",
            shown=shown,
            # The text's head walked the survey; a group read again is
            # read by the standard reader, which needs none of it.
            facts=dataclasses.replace(facts, head=""),
            survey=surveyed,
            headed=reading.header_source == HEADER_FROM_FILE,
            groups=swept.groups,
            held_from=swept.held_from,
            held=held,
        ),
    )


def _pandas_may_rename(cell: str, cells: "list[str]") -> bool:
    """Whether pandas may name a column other than its header cell.

    Pandas renames a blank cell `Unnamed: N` and a repeated one with a
    number after it, and the numbering differs between its versions, so
    a cell that is blank, repeated, or already reads as such a made-up
    name is one whose name pandas may change. Every other cell must come
    back exactly; the survey and the standard reader have already read
    every cell as written.
    """
    if not isinstance(cell, str):
        raise TypeError("internal check: a header cell was not text")
    if not parsing.trimmed(cell) or cell[:9] == "Unnamed: ":
        return True
    seen = 0
    for other in cells:
        if other == cell:
            seen = seen + 1
        elif cell[: len(other) + 1] == f"{other}." and parsing.is_digit_text(
            cell[len(other) + 1 :]
        ):
            return True
    return seen > 1


def _check_against_pandas(
    raw_path: str,
    found: _Reading,
    shown: str,
    refusals: str = REFUSALS_MAY_QUOTE,
    kept: "tuple[bool, ...] | None" = None,
    first_cells: "tuple[str, ...] | None" = None,
) -> "tuple[tuple[int, int], errors.ProfileError] | None":
    """Read the file again with pandas and compare EVERYTHING.

    The names are read back from the file rather than handed to the
    library. Handing them over is what made the old check blind: told
    what the columns were called, the second reader could not disagree
    about it, and a file rewritten between the passes was accepted with
    the old header and the new values (review item P1-R1-F4).

    PANDAS IS CONFIGURED BY THE FORM THE SURVEY FOUND, and the form
    decides nothing pandas then fails to check. The delimiter, the
    escaping, the skipped initial space and the encoding are pandas' own
    options; the separator hint and the preamble are skipped as the
    records they are; an end-of-file mark is left unread by asking for
    no more rows than the survey read. Where the header's written cells
    are not the columns' names -- a blank or repeated name, a trailing
    delimiter, metadata rows under the names -- pandas would rename or
    add columns, so it reads the header as a row and that row is
    compared with the cells as written.

    The path is validated again here, immediately before the library
    call, rather than trusted from the caller. That is what makes the
    fence checkable: the offline scanner requires the argument handed to
    the reader to be traceable, inside this same function, to
    `validate_local_path` (plan P1-D2.1). Round 1 of the review showed
    why a path-shaped object is not enough on its own -- the library
    turns it back into text before deciding whether it is a URL, so a
    Path built from "https://host/f.csv" still reaches the network.

    A PIECE AT A TIME, AND THE WHOLE FRAME ONLY TO SAY WHAT DIFFERS
    (plan P4-D387). The second reading was held whole beside the first,
    a second copy of the table at the reader's peak. Pandas now hands it
    over a piece at a time, and each piece is compared and dropped before
    the next is read, so a file the two readers agree on is checked
    holding one piece. A piece is the rows pandas' own reader parses at a
    time (`_pandas_rows_a_piece`), so the pieces are parsed in the very
    steps the whole frame is: a damaged file the library misreads whole
    is misread in pieces too, rather than read right one way and wrong
    the other. Where anything differs, or the library fails, nothing is
    decided from the pieces: the file is read again as one frame and
    checked as before, so every refusal is the whole frame's, word for
    word, and only a file that is going to be refused is ever held twice.
    Both readings are made by one call and handed over at one line, the
    whole frame as one piece holding every row, so a warning pandas
    gives about the file is shown once, as it was when the file was
    read once, save for a file pandas reads in part and then cannot
    read at all: pandas may warn about the part it read (pandas 3, rows
    ending in a delimiter their header does not), where 110cb46,
    failing before it handed anything over, showed nothing; the refusal
    is the same, word for word.

    ONE GROUP OF COLUMNS AT A TIME (lane SR, plan P4-D400). ``kept``,
    where given, names the columns ``found`` holds: only theirs are
    compared, nothing is refused, and what this check would refuse is
    RETURNED with where it stands -- (0, 0) for a file pandas cannot
    read, (1, 0) for its shape, (2, column) for a name and (3, column)
    for a column's rows -- so the reader refuses the one this check
    finds first reading every column at once. ``first_cells`` is the
    first record's cells of every column (`dialect.Survey.first_cells`),
    which a headerless file with lines above it compares as names.
    """
    validated = validate_local_path(raw_path, purpose="input")
    file_path = pathlib.Path(validated)
    surveyed = found.survey
    if surveyed is None:
        raise ValueError("synthtwin internal check: a reading without its survey")
    form = surveyed.form
    headed = found.header_source == HEADER_FROM_FILE
    # The lines above the header, counted as pandas counts `header`: over
    # the lines that are not blank, a line of nothing but spaces being
    # blank to it too.
    lead = 1 if form.separator_line else 0
    lead = lead + dialect.preamble_lines_holding_text(form.preamble)
    # WHAT PANDAS TAKES AS NAMES. A headed file: its header row, found
    # past the lead. A headerless file with lines above it: its first
    # record, which pandas is asked to take as names only so that it
    # skips those lines -- that record's values are compared as names
    # below. A headerless file with nothing above it reads as before.
    header_row = lead if (headed or lead) else None
    offset = len(form.header_rows)
    first_as_names = not headed and bool(lead)
    wanted = None
    if form.end_of_file_mark:
        wanted = found.n_rows + offset - (1 if first_as_names else 0)
    backslash = form.escape == dialect.ESCAPE_BACKSLASH
    width = len(found.column_names)
    expected_rows = found.n_rows + offset - (1 if first_as_names else 0)
    named_cells: list[str] = []
    if headed:
        named_cells = list(surveyed.header)
    elif first_as_names and first_cells is not None:
        named_cells = list(first_cells)
    elif first_as_names:
        named_cells = [found.columns[place][0] for place in range(width)]
    # The columns pandas is to read: the header's trailing delimiter is a
    # column of its own to it, holding nothing.
    read_width = width + (1 if form.header_trailing_delimiter else 0)
    agrees = False
    keys: "list[object] | None" = None
    found_rows = 0
    # THE PIECES, AND THEN THE WHOLE FRAME WHERE THEY COULD NOT AGREE, ARE
    # BOTH READ BY THE ONE CALL BELOW AND HANDED OVER AT ITS ONE LINE
    # (plan P4-D387). Pandas warns about a file -- rows ending in a
    # delimiter that their header does not end in, say -- from the line of
    # this module that asked it to parse, and Python shows a warning once
    # for each line it comes from: read at two lines, a file refused after
    # its pieces showed the warning twice, where 110cb46, which read it
    # once, showed it once. The whole frame is therefore one piece holding
    # every row (`_EVERY_ROW`), which pandas parses in the very steps it
    # parses a frame read at once.
    for whole in (False, True):
        if not whole and wanted == 0:
            # Asked for no rows at all, pandas hands over no piece, where
            # the whole frame of no rows still names the columns it read:
            # that file is read as the one frame, which pandas hands over
            # itself.
            continue
        rows_a_piece: "int | None" = _pandas_rows_a_piece(read_width)
        if whole:
            rows_a_piece = None if wanted == 0 else _EVERY_ROW
        try:
            handed = pandas.read_csv(
                file_path,
                encoding=dialect.READING_CODECS[found.encoding],
                encoding_errors="strict",
                header=header_row,
                index_col=False,
                dtype=str,
                keep_default_na=False,
                na_filter=False,
                skip_blank_lines=True,
                engine="c",
                sep=form.delimiter,
                quotechar='"',
                doublequote=not backslash,
                escapechar="\\" if backslash else None,
                skipinitialspace=form.initial_space,
                comment=None,
                nrows=wanted,
                chunksize=rows_a_piece,
            )
        except MemoryError as error:
            raise errors.ProfileError(
                errors.out_of_memory(shown, _file_size(file_path))
            ) from error
        except Exception as error:
            if whole:
                refused = _unreadable_in_the_check(shown, refusals, error)
                if kept is not None:
                    return (0, 0), refused
                raise refused from error
            # Pandas could not begin, and the whole frame meets the same
            # failure and refuses in its words.
            continue
        if rows_a_piece is None:
            frame = handed
            break
        agrees = not whole
        while True:
            try:
                piece = next(handed, None)
            except MemoryError as error:
                raise errors.ProfileError(
                    errors.out_of_memory(shown, _file_size(file_path))
                ) from error
            except Exception as error:
                if whole:
                    refused = _unreadable_in_the_check(shown, refusals, error)
                    if kept is not None:
                        return (0, 0), refused
                    raise refused from error
                # Pandas closed the file before raising; the whole frame
                # says what failed.
                agrees = False
                break
            if piece is None:
                break
            if whole:
                # The one piece holding every row. Pandas is asked once
                # more, past it, and closes the file itself.
                frame = piece
                continue
            if not agrees:
                # Read to the end without comparing, so that pandas
                # closes the file itself: a reader dropped part way
                # leaves it open.
                continue
            if keys is None:
                # The columns pandas read are the ones the piece's size
                # was worked out for, or nothing more is compared; the
                # one a header's trailing delimiter adds is never asked.
                keys = list(piece.columns)
                names = [f"{key}" for key in keys]
                agrees = len(keys) == read_width
                agrees = agrees and _names_agree(named_cells, names)
            if agrees and keys is not None:
                # The record pandas took as names stands first in the
                # frame, as the survey read it, and is held to the names
                # it read above: a file with no names has no rows of
                # descriptions (the survey reads them under a header
                # alone), so that record is the survey's own first value
                # and nothing else, and the pieces start one place on.
                start = found_rows + (1 if first_as_names else 0)
                for index in range(width):
                    if kept is not None and not kept[index]:
                        continue
                    # One column of this piece is turned into text at a
                    # time and dropped again.
                    theirs = [f"{cell}" for cell in list(piece[keys[index]])]
                    if not _piece_agrees(found, form, index, start, theirs):
                        agrees = False
                        break
            found_rows = found_rows + len(piece)
        if not whole and agrees and keys is not None and found_rows == expected_rows:
            return None
    # THE WHOLE FRAME, checked as it always was, for a file the pieces
    # could not agree on: whatever it refuses is refused in its words,
    # and a file it accepts is accepted.
    found_rows = len(frame)
    keys = list(frame.columns)
    if form.header_trailing_delimiter and len(keys) == width + 1:
        # The delimiter ending the header line, which pandas names as a
        # column of its own holding nothing.
        keys = keys[:width]
    if found_rows != expected_rows or len(keys) != width:
        return _pandas_refusal(
            (1, 0),
            errors.ProfileError(
                errors.readers_disagree(
                    shown,
                    f"{found.n_rows} rows of {width} values",
                    f"{found_rows - offset} rows of {len(keys)} values",
                )
            ),
            kept,
        )
    for index in range(len(named_cells)):
        second = f"{keys[index]}"
        expected = named_cells[index]
        if second != expected and not _pandas_may_rename(expected, named_cells):
            if refusals == REFUSALS_NAME_POSITIONS:
                return _pandas_refusal(
                    (2, index),
                    errors.ProfileError(
                        errors.checked_file_readers_disagree_about_a_name(
                            shown, index + 1
                        )
                    ),
                    kept,
                )
            return _pandas_refusal(
                (2, index),
                errors.ProfileError(
                    errors.readers_disagree_about_a_name(
                        shown, index + 1, found.column_names[index], second
                    )
                ),
                kept,
            )
    for index in range(len(keys)):
        if kept is not None and not kept[index]:
            continue
        mine = found.columns[index]
        # One column of the second reading is turned into text at a
        # time and dropped again: the whole second frame is already in
        # memory, and materializing all of it a second time would add a
        # third copy of the table for no gain.
        theirs = [f"{cell}" for cell in list(frame[keys[index]])]
        if first_as_names:
            theirs = [mine[0]] + theirs
        if offset:
            above = [row[index] for row in form.header_rows]
            for place in range(offset):
                if theirs[place] != above[place]:
                    if refusals == REFUSALS_NAME_POSITIONS:
                        return _pandas_refusal(
                            (3, index),
                            errors.ProfileError(
                                errors.checked_file_readers_disagree_about_a_name(
                                    shown, index + 1
                                )
                            ),
                            kept,
                        )
                    return _pandas_refusal(
                        (3, index),
                        errors.ProfileError(
                            errors.readers_disagree_about_a_name(
                                shown, index + 1, above[place], theirs[place]
                            )
                        ),
                        kept,
                    )
        last = len(theirs) - 1
        if (
            form.end_of_file_mark
            and not form.final_line_ending
            and theirs[last][len(theirs[last]) - 1 :] == "\x1a"
        ):
            # The end-of-file mark glued to the last value, which pandas
            # reads as part of it; the survey took it off the text.
            theirs[last] = theirs[last][: len(theirs[last]) - 1]
        for position in range(found.n_rows):
            if theirs[position + offset] != mine[position]:
                if refusals == REFUSALS_NAME_POSITIONS:
                    # The column's NAME is a string out of this file,
                    # and this file may not be the person's own table,
                    # so the column is named by its position instead.
                    return _pandas_refusal(
                        (3, index),
                        errors.ProfileError(
                            errors.checked_file_readers_disagree_about_a_value(
                                shown, position + 1, index + 1
                            )
                        ),
                        kept,
                    )
                return _pandas_refusal(
                    (3, index),
                    errors.ProfileError(
                        errors.readers_disagree_about_a_value(
                            shown, position + 1, found.column_names[index]
                        )
                    ),
                    kept,
                )
    return None


def _pandas_refusal(
    where: "tuple[int, int]",
    refused: errors.ProfileError,
    kept: "tuple[bool, ...] | None",
) -> "tuple[tuple[int, int], errors.ProfileError]":
    """What `_check_against_pandas` refuses: raised reading every column, returned reading a group."""
    if kept is None:
        raise refused
    return where, refused


def _pandas_rows_a_piece(width: int) -> int:
    """The rows pandas' own reader parses at a time in a table ``width`` columns wide.

    THE CHECKING PASS READS ITS PIECES IN PANDAS' OWN STEPS (plan
    P4-D387). Pandas' C reader parses a file a fixed number of rows at a
    time, whether it is asked for one frame or for pieces: the power of
    two at least half of 1,048,576 divided by the width and below it,
    16,384 rows at fifty columns. A piece of exactly that many rows is
    parsed by the same steps the whole frame is, and pieces of another
    size were not, which on a damaged file -- lines ended by carriage
    returns alone, with quoted line breaks -- the library answered
    differently: the whole frame failed where the pieces read, or the
    other way round. That number is the library's and not this
    package's, so `tests/test_stage4_tier2a.py` finds it in the
    installed pandas, where a column's type splits.

    Guarantees: a power of two of at least 1, for any width. Determinism:
    a fixed function of the width. Raises nothing. No I/O.
    """
    target = 1_048_576 // max(1, width)
    rows = 1
    while rows * 2 < target:
        rows = rows * 2
    return rows


def _unreadable_in_the_check(
    shown: str, refusals: str, error: Exception
) -> errors.ProfileError:
    """The refusal of a file pandas could not read in the checking pass, in the words it always had.

    Every failure of the checking pass becomes one plain-language
    refusal. The catch that hands the failure here is deliberately
    broad: the offline import policy (plan D6.2) permits only
    pandas.read_csv from pandas, so the library's own exception classes
    cannot be named, and nothing is swallowed -- the caller chains the
    original on. Under ``REFUSALS_NAME_POSITIONS`` the library's words,
    which may quote the file, are left out.

    Guarantees: returns the refusal and raises nothing. Determinism: a
    fixed function of its arguments. No I/O.
    """
    if refusals == REFUSALS_NAME_POSITIONS:
        return errors.ProfileError(errors.checked_file_unreadable_as_csv(shown))
    return errors.ProfileError(errors.unreadable_as_csv(shown, f"{error}"))


def _names_agree(named_cells: "list[str]", names: "list[str]") -> bool:
    """Whether pandas named the columns as the survey read them, as the whole frame's check asks it.

    ``named_cells`` is what the survey read as names, and ``names`` the
    columns pandas named, as text. A name pandas may change on its own --
    a blank or repeated one (`_pandas_may_rename`) -- is not compared.
    """
    for index in range(len(named_cells)):
        expected = named_cells[index]
        if names[index] != expected and not _pandas_may_rename(
            expected, named_cells
        ):
            return False
    return True


def _piece_agrees(
    found: _Reading,
    form: dialect.Dialect,
    index: int,
    start: int,
    theirs: "list[str]",
) -> bool:
    """Whether one column of one piece of the checking pass reads as the survey read it.

    ``theirs`` stands at the places from ``start`` on, counted as the
    whole frame's column was checked: the rows of column descriptions
    under the names first, then the data. A row above the data is
    compared as pandas read it; the frame's last value, where an
    end-of-file mark is glued to it, without the mark, which the survey
    took off the text; and the values a run at a time, so a place past
    the survey's last value differs. Nothing is refused here: a piece
    that differs sends the check to the whole frame, which says what.
    """
    count = len(theirs)
    offset = len(form.header_rows)
    step = 0
    while step < count and start + step < offset:
        if theirs[step] != form.header_rows[start + step][index]:
            return False
        step = step + 1
    if step == count:
        return True
    position = start + step - offset
    last = found.n_rows + offset - 1
    if form.end_of_file_mark and not form.final_line_ending:
        if start + step <= last < start + count:
            value = theirs[last - start]
            if value[len(value) - 1 :] == "\x1a":
                # The end-of-file mark glued to the last value, which
                # pandas reads as part of it.
                theirs[last - start] = value[: len(value) - 1]
    mine = found.columns[index]
    return theirs[step:] == mine[position : position + count - step]

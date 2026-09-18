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
   values written below it. Three ways it can belong, any one of them
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

    THE COLUMN HAS TO SPEAK WITH ONE VOICE. Every value below must wear
    the SAME silhouette, that silhouette must be structured
    (`_shape_is_structured` above), and the first row's value must wear
    it too. A column of words under a name of words says nothing here,
    and neither does `record_id` over `R001` -- `A_A` is not `A9` --
    which is what keeps this rule off the ordinary headed export.

    Guarantees: accepts the first row's value in one column and the
    values below it; returns a bool. Determinism: a fixed function of
    the two. Raises nothing. No I/O of any kind.
    """
    mine = _silhouette(f"{name}")
    if not _shape_is_structured(mine):
        return False
    seen = 0
    for value in values:
        text = f"{value}"
        if text == "":
            continue
        seen = seen + 1
        if _silhouette(text) != mine:
            return False
    return seen >= 2


def _record_evidence(
    header: list[str], columns: list[list[str]]
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

    The four rules are tried in the order a person would want to hear
    them, which is also cheapest first for the common case: only a
    numeric first-row value reaches the walk of a numeric column at all.
    Each rule stops at the first column that speaks. The fourth,
    `_shares_the_shape_below`, was added by plan P4-D241 and is the one
    that reads a record made of structured TEXT; it is asked last
    because it is the only one that walks every column of the file.
    """
    for index in range(len(header)):
        if _numeric_fit(header[index], columns[index]):
            return (
                f"in column {index + 1} the value in that row is a number "
                f"lying among the numbers written below it, which is what "
                f"a record in that column looks like"
            )
    for index in range(len(header)):
        if _date_fit(header[index], columns[index]):
            return (
                f"in column {index + 1} the value in that row is a date, "
                f"written the same way as every date below it, which is "
                f"what a record in that column looks like"
            )
    for index in range(len(header)):
        if _repeats_a_value_below(header[index], columns[index]):
            return (
                f"in column {index + 1} the value in that row appears "
                f"again further down the same column, more than once, so "
                f"it is one of the values that column is made of"
            )
    for index in range(len(header)):
        if _shares_the_shape_below(header[index], columns[index]):
            return (
                f"in column {index + 1} the value in that row is written "
                f"to the same pattern of letters, figures and marks as "
                f"every value below it, which is what a record in that "
                f"column looks like"
            )
    return None


def _generated_column_names(width: int) -> list[str]:
    """Names for a table whose first row the caller said was data."""
    return [f"column_{position}" for position in range(1, width + 1)]


def _as_text(value: object) -> str:
    """``value`` proven to be text, which is what lets a method run on it."""
    if not isinstance(value, str):
        raise TypeError("internal check: a file's text was not text")
    return value


def _physical_lines(text: str) -> "list[str]":
    """The text's lines as a file opened with ``newline=""`` hands them over.

    Nothing is translated, and the lines are the survey's own
    (`dialect.physical_lines`), so the standard reader reads exactly the
    text the survey read -- including a text whose end-of-file mark has
    been taken off, which a file handle could not give it.
    """
    return dialect.physical_lines(text)


def _agrees_with_the_standard_reader(
    text: str,
    surveyed: dialect.Survey,
    headed: bool,
    shown: str,
    refusals: str,
) -> None:
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
    """
    form = surveyed.form
    body = _as_text(text)
    if form.end_of_file_mark:
        body = body[: len(body) - 1]
    backslash = form.escape == dialect.ESCAPE_BACKSLASH
    rows = csv.reader(
        _physical_lines(body),
        delimiter=form.delimiter,
        doublequote=not backslash,
        escapechar="\\" if backslash else None,
        skipinitialspace=form.initial_space,
    )
    lead = 1 if form.separator_line else 0
    lead = lead + dialect.preamble_lines_written(form.preamble)
    expected_header: list[str] = []
    if headed:
        expected_header = list(surveyed.header)
        if form.header_trailing_delimiter:
            expected_header += [""]
    header_pending = headed
    metadata_pending = len(form.header_rows)
    width = len(surveyed.columns)
    # Every place, counted or not: past its cap the form publishes the
    # blank lines counted, and the file still holds each where it stands.
    places = [place for place in surveyed.every_blank_place if place.text]
    place_at = 0
    place_left = places[0].lines if places else 0
    row = 0
    for record in rows:
        cells = [f"{cell}" for cell in record]
        if not cells:
            continue
        if lead:
            lead = lead - 1
            continue
        if header_pending:
            header_pending = False
            if cells != expected_header:
                _disagree_about_a_name(shown, surveyed, refusals)
            continue
        if metadata_pending:
            expected = list(form.header_rows[len(form.header_rows) - metadata_pending])
            metadata_pending = metadata_pending - 1
            if cells != expected:
                raise errors.ProfileError(
                    errors.readers_disagree(
                        shown, "a row of column descriptions", "a different row"
                    )
                )
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
            cells = cells + ["" for _place in range(width - len(cells))]
        if len(cells) != width or row >= surveyed.n_rows:
            raise errors.ProfileError(
                errors.readers_disagree(
                    shown,
                    f"{surveyed.n_rows} rows of {width} values",
                    "a row the standard reader read differently",
                )
            )
        for place in range(width):
            if cells[place] != surveyed.columns[place][row]:
                _disagree_about_a_value(shown, surveyed, row, place, refusals)
        row = row + 1
    if row != surveyed.n_rows or header_pending:
        raise errors.ProfileError(
            errors.readers_disagree(
                shown,
                f"{surveyed.n_rows} rows of {width} values",
                f"{row} rows",
            )
        )


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
                declared_delimiter,
            )
            _agrees_with_the_standard_reader(
                text, surveyed, headed, shown, refusals
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
    found: _Reading, shown: str, first_row: str
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
    """
    header = found.column_names
    if first_row != FIRST_ROW_AUTOMATIC:
        return found.header_evidence, False, ""
    numbers = [
        name for name in header if not parsing.looks_like_a_column_name(name)
    ]
    if len(numbers) == len(header):
        return _NOT_TOLD, False, EVERY_VALUE_A_NUMBER
    spoken = _record_evidence(header, found.columns)
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
    """
    for position, name in enumerate(header):
        if position >= len(columns):
            break
        # No method call on an untraced value: every element is forced to
        # text by an f-string first, and a blank cell is compared, not
        # trimmed. A whitespace-only cell therefore reads as "not a
        # number", so a column holding one yields no evidence and the
        # header is taken by convention -- the conservative side, and it
        # costs a sentence rather than a record.
        present = [
            f"{value}" for value in columns[position] if f"{value}" != ""
        ]
        if len(present) < 2:
            continue
        if parsing.classify_number(f"{name}") != parsing.NOT_A_NUMBER:
            continue
        every_value_is_a_number = True
        for value in present:
            if parsing.classify_number(f"{value}") == parsing.NOT_A_NUMBER:
                every_value_is_a_number = False
        if every_value_is_a_number:
            return taxonomy.note(
                taxonomy.HEADER_NAMES_SHOWN_BY_COLUMN, (position + 1,)
            )
    return None


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
) -> Table:
    """One sheet of a workbook, as a table of text (plan P4-D77).

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
    if not positions:
        mixed = workbook.mixed_storage(sheet)
        if mixed is not None:
            raise errors.ProfileError(
                errors.workbook_column_mixes_storage(
                    shown, names[mixed[0]], mixed[1]
                )
            )
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
            found, shown, first_row
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
                reading, shown, records_from_the_header=True
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
) -> Table:
    """Read a CSV table from a local path; return it as text.

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
    # accepted way to read a file in this package -- rather than a
    # handle this audit cannot trace.
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
        )
    try:
        found = _read_authoritatively(
            table_path, shown, first_row, refusals, encoding, data,
            metadata_rows, decimal_comma_columns, metadata_rows_confirmed,
            declared_delimiter,
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
            found, shown, first_row
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
) -> None:
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
    try:
        frame = pandas.read_csv(
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
        if refusals == REFUSALS_NAME_POSITIONS:
            raise errors.ProfileError(
                errors.checked_file_unreadable_as_csv(shown)
            ) from error
        raise errors.ProfileError(
            errors.unreadable_as_csv(shown, f"{error}")
        ) from error

    found_rows = len(frame)
    keys = list(frame.columns)
    width = len(found.column_names)
    if form.header_trailing_delimiter and len(keys) == width + 1:
        # The delimiter ending the header line, which pandas names as a
        # column of its own holding nothing.
        keys = keys[:width]
    expected_rows = found.n_rows + offset - (1 if first_as_names else 0)
    if found_rows != expected_rows or len(keys) != width:
        raise errors.ProfileError(
            errors.readers_disagree(
                shown,
                f"{found.n_rows} rows of {width} values",
                f"{found_rows - offset} rows of {len(keys)} values",
            )
        )
    named_cells: list[str] = []
    if headed:
        named_cells = list(surveyed.header)
    elif first_as_names:
        named_cells = [found.columns[place][0] for place in range(width)]
    for index in range(len(named_cells)):
        second = f"{keys[index]}"
        expected = named_cells[index]
        if second != expected and not _pandas_may_rename(expected, named_cells):
            if refusals == REFUSALS_NAME_POSITIONS:
                raise errors.ProfileError(
                    errors.checked_file_readers_disagree_about_a_name(
                        shown, index + 1
                    )
                )
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
        if first_as_names:
            theirs = [mine[0]] + theirs
        if offset:
            above = [row[index] for row in form.header_rows]
            for place in range(offset):
                if theirs[place] != above[place]:
                    if refusals == REFUSALS_NAME_POSITIONS:
                        raise errors.ProfileError(
                            errors.checked_file_readers_disagree_about_a_name(
                                shown, index + 1
                            )
                        )
                    raise errors.ProfileError(
                        errors.readers_disagree_about_a_name(
                            shown, index + 1, above[place], theirs[place]
                        )
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
                    raise errors.ProfileError(
                        errors.checked_file_readers_disagree_about_a_value(
                            shown, position + 1, index + 1
                        )
                    )
                raise errors.ProfileError(
                    errors.readers_disagree_about_a_value(
                        shown, position + 1, found.column_names[index]
                    )
                )

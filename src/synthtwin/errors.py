"""The refusal catalog (Phase 1 plan, P1-D7).

Every way synthtwin can refuse to profile a table has exactly one
message builder here, and every message follows the same shape: what
happened, then what to do next, in words a person who has never
programmed can act on. "Invalid input" is a bug report against us, not
an error message.

Positions in these messages are DATA-ROW numbers -- counted after the
header row and skipping blank lines -- never file line numbers. A
quoted value may contain line breaks, so a file line number can point
into the middle of a row and send the reader to the wrong place.

Every value that came out of the user's table -- a column name, a
spelling, a detail quoted from a library -- passes through
`parsing.visible` before it enters a message. A header can contain an
escape sequence, and a refusal is a human-facing sink like any other
(review item P1-R3-F9).

A HANDFUL OF THESE MESSAGES SERVE THREE COMMANDS, and the words they
use for the files differ between them. `ArtifactWords` below holds
exactly those words, the three sets are written out beside it, and the
builders that need one take it as an argument (plan P2-D10, extended to
the quality report by P3-D1).

Imports here stay within the allowlist (plan D6.2): `dataclasses`, for
that one record, and `parsing`, for `visible`.
"""

import dataclasses

from synthtwin import parsing


class ProfileError(Exception):
    """A refusal, carrying a message written for the person running the tool.

    Guarantees:

    - Inputs: constructed with one already-built message string from
      this module's builders.
    - Determinism: the message is fixed by its inputs; nothing here
      reads a clock, an environment variable, or a random source.
    - Errors raised: none. This type is raised, never raising itself.
    - Boundary: no path is read and no data value is ever placed in a
      message by these builders except a column name, which the user
      already knows, and counts.
    """


class TransactionRefusal(ProfileError):
    """A refusal the write transaction composed, cleanup already done.

    The transaction's own handler has exactly one question to ask about
    a failure on its way out: is this one MINE? A refusal built by the
    transaction has already cleared the working files away and already
    names every file on disk in its own message, so running the cleanup
    again and adding a second sentence would give the reader two
    different accounts of one folder. Anything else has had neither.

    Asking that question by testing for `ProfileError` was wrong, and
    the way it was wrong is the point: it treated a TYPE as proof of
    something a type cannot carry. `ProfileError` is the package's
    ordinary refusal and any code in the transaction's reach can raise
    one -- an unexpected one from inside a rename was passed straight
    out, with no cleanup and no sentence, leaving both working files on
    disk (review item P1-R8-F1). This class exists so the question has a
    truthful answer: it is constructed in exactly two places, both of
    which have run the cleanup and put the state of every name into the
    message before handing the object back.

    It is a subclass, so every caller that catches `ProfileError` --
    including the command -- catches it unchanged, and nothing about
    what the person reads depends on which of the two it is.
    """


# WHICH OF THE READER'S REFUSALS ABOUT A FILE'S OWN SHAPE THIS IS.
#
# Three words of this module's own vocabulary, so a caller can ask which
# refusal it caught without reading the sentence a person reads (review
# item P3-V4-F3). `synthtwin validate` reports on two of the reader's
# refusals rather than passing them on -- V9 makes a structural mismatch
# a MISSED verdict with a plain explanation -- and it used to decide
# which of them a file was going to get by walking the file itself,
# BEFORE the reader was called. A walk that has to be kept in step with
# the reader by hand is a walk that drifts: four ways were found in one
# review round where the two disagreed about which refusal a file gets,
# and on each of them two files the producer refuses identically got
# different reports. So the decision is taken from the refusal the
# reader ACTUALLY raised, and these are what it is taken on.
NO_DATA_TO_DESCRIBE = "no-data-to-describe"
HEADER_NAME_MISSING = "header-name-missing"
HEADER_NAME_REPEATED = "header-name-repeated"

_SHAPE_REFUSALS = (
    NO_DATA_TO_DESCRIBE,
    HEADER_NAME_MISSING,
    HEADER_NAME_REPEATED,
)


class ShapeRefusal(ProfileError):
    """A reader refusal about a file's SHAPE, carrying which one it is.

    The reader refuses a file with no rows to describe, and one whose
    first row leaves a name blank or uses a name twice. Both are
    refusals of the profiler and both are things `synthtwin validate`
    REPORTS on instead, so the caller that reports has to know which one
    it caught -- and knowing it from the message would mean matching on
    prose, which is a rule written twice again.

    ``position`` is the column number of a blank name and is zero for the
    other two. It is here because the profiler's own refusal for a blank
    name NAMES that number, so a report may state it (V5.1); the
    profiler's refusal for a REPEATED name quotes the name instead and
    names no position at all, so nothing carries one here.

    Guarantees:

    - Inputs: an already-built message from this module's builders, one
      of this module's three shape words, and a column number for the
      blank-name case.
    - Determinism: nothing here reads a clock, an environment variable,
      or a random source.
    - Errors raised: ValueError for a word that is not one of the three,
      because a caller reaching that has mistyped a constant and a
      refusal nobody can classify would be reported as the wrong kind of
      file.
    - Boundary: no value out of any file is placed in ``kind`` or
      ``position``; both are this module's own vocabulary and a count.

    It is a subclass, so every caller that catches `ProfileError` --
    including the command -- catches it unchanged, and nothing about
    what a person reads depends on which of the two it is.

    IT IS BUILT BY `shape_refusal` BELOW AND NOT BY A CONSTRUCTOR OF ITS
    OWN. Phase 0's offline audit accepts no double-underscore name and
    no `super` in this package's source (plan D6.2), so the two fields
    are class attributes with a stated default and the builder sets
    them. The default is what a caller who raised the class directly
    would see, and it names no refusal, which is why `shape_refusal` is
    the only thing that builds one.
    """

    kind = ""
    position = 0


def shape_refusal(
    message: str, kind: str, position: int = 0
) -> ShapeRefusal:
    """One shape refusal, with the word that says which one it is.

    Guarantees:

    - Inputs: an already-built message from this module's builders, one
      of this module's three shape words, and the column number of a
      blank name where there is one.
    - Determinism: a fixed function of the three.
    - Errors raised: ValueError for a word that is not one of the three.
      A refusal nobody can classify would be reported as the wrong kind
      of file, so it stops here rather than travelling.
    - Boundary: no value out of any file reaches ``kind`` or
      ``position``.
    """
    if kind not in _SHAPE_REFUSALS:
        raise ValueError(
            "synthtwin internal check: a shape refusal must name which "
            "of the reader's shape refusals it is."
        )
    refusal = ShapeRefusal(message)
    refusal.kind = kind
    refusal.position = position
    return refusal


_CHECK_AND_RETRY = "Fix that in the file and run the command again."


def _shown(value: str) -> str:
    """One table-derived value, safe to put on a screen."""
    return parsing.visible(f"{value}")


def _listed(items: list[str]) -> str:
    """Join items with commas for a message, without calling join().

    The offline policy accepts a text method only when every argument
    is a value it has resolved, and a list built at run time is not one
    (plan D6.2). Building the text by hand keeps the source inside the
    policy and costs nothing here.
    """
    text = ""
    for item in items:
        shown = _shown(f"{item}")
        if not text:
            text = shown
        else:
            text = f"{text}, {shown}"
    return text


def file_missing(path: str) -> str:
    """Message for a table path that names nothing on disk."""
    return (
        f"There is no file at {path}. Please check the spelling of the "
        f"path, and that the file is on this computer and not in a "
        f"folder you have not opened yet."
    )


def path_is_a_folder(path: str) -> str:
    """Message for a folder given where a table file was expected."""
    return (
        f"{path} is a folder, not a file. Please give the path of the "
        f"CSV file itself, for example the file ending in .csv inside "
        f"that folder."
    )


def file_unreadable(path: str, detail: str) -> str:
    """Message for a file that exists but could not be opened."""
    return (
        f"The file {path} could not be opened ({_shown(detail)}). Please check "
        f"that you have permission to read it and that no other "
        f"program is holding it open, then try again."
    )


def not_utf8_or_latin1(path: str) -> str:
    """Message for a file that is not text in either supported encoding."""
    return (
        f"The file {path} is not readable as text. synthtwin reads CSV "
        f"files saved as UTF-8 (the usual choice) and, as a fallback, "
        f"Western European text (Latin-1). If this file came from a "
        f"spreadsheet, open it and save it again choosing 'CSV UTF-8'."
    )


def looks_like_utf16(path: str) -> str:
    """Message for a UTF-16/UTF-32 file (or a binary file) given as CSV."""
    return (
        f"The file {path} looks like it was saved as UTF-16 or UTF-32 "
        f"text, or is not a text file at all: it contains "
        f"the zero bytes those formats use. synthtwin reads UTF-8 CSV "
        f"files. Open the file in your spreadsheet program and save it "
        f"again choosing 'CSV UTF-8'."
    )


def file_is_empty(path: str) -> str:
    """Message for a completely empty file."""
    return (
        f"The file {path} is empty: it has no column names and no "
        f"rows. Please give the path of the CSV file that holds your "
        f"table."
    )


def no_data_rows(path: str) -> str:
    """Message for a file with a header row and nothing else."""
    return (
        f"The file {path} has column names but no data rows, so there "
        f"is nothing to describe. Please give a file that contains the "
        f"rows as well."
    )


def header_looks_like_data(path: str, reason: str) -> str:
    """Message for a first row that does not look like column names."""
    return (
        f"The first row of {path} does not look like column names: "
        f"{_shown(reason)}. synthtwin needs the first row to be the names of "
        f"the columns. Add a first row with a name for every column, "
        f"then run the command again. If that row is the first record "
        f"and the table has no column names at all, run the command "
        f"again with --first-row data: synthtwin will name the columns "
        f"column_1, column_2, and so on and keep every record."
    )


def first_row_could_be_a_record(
    path: str, columns: int, found: str = ""
) -> str:
    """Message for a first row the file shows could be a record.

    ``found`` is what the reader actually found, in words, naming the
    column by its POSITION -- one of the clauses `reading` builds. Left
    out, the message states only the general shape of the trouble, which
    is what a caller with no detail to hand can honestly say.

    The wording says exactly what was found and nothing more. The
    version this replaces claimed that "none of them stands out as a
    name, and at least one has exactly the shape every other value in
    its column has". Neither half was what the reader had checked: the
    first is a claim no test can support, because nothing about a value
    makes it a name, and the second could be false of every column in
    the file while the refusal was raised for a different reason
    entirely (review item P1-R6-F6).

    The message deliberately quotes nothing from the row, and nothing
    from below it. If the row is a record, printing it would print
    somebody's data to the screen in order to ask a question about it,
    and in an unsettled file the "column name" IS that row.
    """
    stated = (
        _shown(found)
        if found
        else (
            "at least one value in that row belongs among the values of "
            "the column below it"
        )
    )
    return (
        f"synthtwin cannot tell whether the first row of {path} holds "
        f"the names of the {columns} columns or the first record of the "
        f"table, because {stated}. Guessing would either drop a whole "
        f"record from the description or publish a record as if it were "
        f"a set of column names, so synthtwin stops instead. Please run "
        f"the command again with --first-row names if that row holds the "
        f"column names, or with --first-row data if it is the first "
        f"record. With --first-row data the columns are named column_1, "
        f"column_2, and so on, and every record is kept."
    )


def readers_disagree_about_a_name(
    path: str, position: int, first: str, second: str
) -> str:
    """Message for the two reading passes finding different column names."""
    return (
        f"synthtwin read {path} twice and the two readings do not agree "
        f"about the name of column number {position}: the first reading "
        f"found '{_shown(first)}' and the second found "
        f"'{_shown(second)}'. There are two usual causes. Either "
        f"something else was writing to the file while synthtwin was "
        f"reading it -- make sure nothing else is using the file and "
        f"run the command again -- or the first row is written in a "
        f"way the two readers read differently, which a stray carriage "
        f"return, a zero byte, or a quotation mark that was never "
        f"closed will do. Open the file in your spreadsheet program, "
        f"save it again choosing 'CSV UTF-8', and run the command "
        f"again. synthtwin refuses to describe a table it could not "
        f"read the same way twice."
    )


def readers_disagree_about_a_value(path: str, row: int, column: str) -> str:
    """Message for the two reading passes finding different values.

    The two values themselves are never printed: one of them is a
    person's data, and a refusal is a human-facing sink like any other.
    The position is enough to find the place in the file.
    """
    return (
        f"synthtwin read {path} with two separate readers and they do "
        f"not agree about the value in row {row}, column "
        f"'{_shown(column)}'. Rows are counted after the first row, "
        f"leaving out blank lines. There are two usual causes. Either "
        f"something else was writing to the file while synthtwin was "
        f"reading it -- make sure nothing else is using the file and "
        f"run the command again -- or that part of the file is written "
        f"in a way the two readers read differently, which a stray "
        f"carriage return, a zero byte, or a quotation mark that was "
        f"never closed will do. Open the file in your spreadsheet "
        f"program, save it again choosing 'CSV UTF-8', and run the "
        f"command again. synthtwin refuses to describe a table it could "
        f"not read the same way twice."
    )


# THE SAME THREE REFUSALS, FOR A FILE NOBODY PROMISED WAS THEIRS
# (plan P3-D1, V9; review item P3-V1-F10).
#
# The three messages above quote what the reader found -- the name it
# read back, the column a value sits in -- and on the profiler's path
# that is right: the person handed synthtwin their own table and asked
# it to describe it, so naming what is in it tells them where to look.
#
# `synthtwin validate` is pointed at a file nobody promised was theirs.
# It may be a twin, somebody else's table, or the wrong table entirely,
# and a refusal travels as freely as a report does: it is printed, it is
# copied into a ticket, it is pasted into a message. So on that path
# every refusal names POSITIONS -- which column, which row -- and never
# a value. These are those forms. They are separate builders rather than
# a flag inside the ones above because a message a reader can act on is
# written, not assembled, and because the profiler's own wording then
# stays byte for byte what it was.


def checked_file_readers_disagree_about_a_name(
    path: str, position: int
) -> str:
    """Message for the two passes finding different names, by position."""
    return (
        f"synthtwin read {path} twice and the two readings do not agree "
        f"about the name of column number {position}. There are two "
        f"usual causes. Either something else was writing to the file "
        f"while synthtwin was reading it -- make sure nothing else is "
        f"using the file and run the command again -- or that name is "
        f"written in a way the two readers read differently, which a "
        f"stray carriage return, a zero byte, or a quotation mark that "
        f"was never closed will do. Open the file in your spreadsheet "
        f"program, save it again choosing 'CSV UTF-8', and run the "
        f"command again. synthtwin refuses to check a file it could not "
        f"read the same way twice, and it does not print what it found "
        f"in the file: this file may not be your own table."
    )


def checked_file_readers_disagree_about_a_value(
    path: str, row: int, position: int
) -> str:
    """Message for the two passes finding different values, by position."""
    return (
        f"synthtwin read {path} with two separate readers and they do "
        f"not agree about the value in row {row}, column number "
        f"{position}. Rows are counted after the first row, leaving out "
        f"blank lines. There are two usual causes. Either something else "
        f"was writing to the file while synthtwin was reading it -- make "
        f"sure nothing else is using the file and run the command again "
        f"-- or that part of the file is written in a way the two "
        f"readers read differently, which a stray carriage return, a "
        f"zero byte, or a quotation mark that was never closed will do. "
        f"Open the file in your spreadsheet program, save it again "
        f"choosing 'CSV UTF-8', and run the command again. synthtwin "
        f"refuses to check a file it could not read the same way twice, "
        f"and it does not print what it found in the file: this file may "
        f"not be your own table."
    )


def checked_file_unreadable_as_csv(path: str) -> str:
    """Message for a checked file the CSV reader could not make sense of.

    The profiler's form of this quotes the reader's own account of what
    went wrong, and that account can carry a piece of the file with it --
    a byte it stopped at, a fragment of a line. Here it is left out and
    the shape of the trouble is stated instead.
    """
    return (
        f"The file {path} could not be read as a CSV table. synthtwin "
        f"reads comma-separated files with one row per line and "
        f"quotation marks around any value that contains a comma. A "
        f"quotation mark that was never closed is the usual cause. Open "
        f"the file in your spreadsheet program, save it again choosing "
        f"'CSV UTF-8', and run the command again. synthtwin does not "
        f"print what it found in the file: this file may not be your "
        f"own table."
    )


def checked_file_repeats_a_column_name(path: str) -> str:
    """Message for a repeated name in a checked file, naming neither.

    The profiler's form of this QUOTES the repeated name, and on the
    checking path that name is a string out of a file nobody promised
    was the reader's (V9).

    AND IT NAMES NO POSITION EITHER (review item P3-V4-F3; plan
    amendment A-P3-10 clause 2). The version this replaces put the two
    column numbers in the name's place, on the reasoning that a number
    publishes strictly less than a string. That reasoning was wrong, and
    the way it was wrong is the point: `dup,a,dup` and `a,dup,dup` are
    two files `synthtwin profile` refuses with the SAME sentence, and
    the positions tell them apart. What the profiler's refusal
    publishes about such a file is that one of its names is used twice,
    so that is what this says.
    """
    return (
        f"The first row of {path} uses one column name twice. Every "
        f"column needs its own name, so that the description of one "
        f"column can never be confused with another's. Rename the "
        f"repeat and run the command again. synthtwin does not print "
        f"what it found in the file, or where: this file may not be "
        f"your own table."
    )


def duplicate_column_names(names: list[str]) -> str:
    """Message for repeated column names in the header row."""
    listed = _listed(names)
    return (
        f"The first row repeats the same column name more than once "
        f"({listed}). Every column needs its own name, so that the "
        f"description of one column can never be confused with "
        f"another's. Rename the repeats and run the command again."
    )


def empty_column_name(position: int) -> str:
    """Message for a header cell with no name in it."""
    return (
        f"Column number {position} has no name in the first row. Every "
        f"column needs a name. Add one and run the command again."
    )


def ragged_rows(
    path: str, expected: int, offenders: list[tuple[int, int]], total: int
) -> str:
    """Message for rows whose value count differs from the header's.

    ``offenders`` holds up to three (data-row number, value count)
    pairs; ``total`` is the full count of such rows.
    """
    described = [f"row {number} has {count}" for number, count in offenders]
    listed = _listed(described)
    tail = "" if total <= len(offenders) else f" ({total} rows in total)"
    return (
        f"The rows in {path} do not all have the same number of "
        f"values. The first row names {expected} columns, but {listed}"
        f"{tail}. Rows are counted after the first row, leaving out "
        f"blank lines. A row with too few or too many values usually "
        f"means a value contains a comma and needs quotation marks "
        f"around it. {_CHECK_AND_RETRY}"
    )


def blank_line_in_one_column(path: str, row: int) -> str:
    """Message for a blank line in a table that has only one column."""
    return (
        f"There is an empty line in {path} just before row {row}, and "
        f"the table has only one column. synthtwin cannot tell whether "
        f"that line is a record whose one value is missing or simply a "
        f"blank line left in the file. Reading it either way would "
        f"change how many records the description says the table has. "
        f"If it is a record with a missing value, write two quotation "
        f'marks ("") on that line; if it is a blank line, delete it. '
        f"Then run the command again."
    )


def field_too_long(path: str, limit: int) -> str:
    """Message for a single value longer than the reader's limit."""
    return (
        f"One value in {path} is longer than {limit} characters, which "
        f"is more text than synthtwin will read in a single value. "
        f"This usually means a quotation mark is missing somewhere, so "
        f"the reader kept going to the end of the file looking for the "
        f"closing one. {_CHECK_AND_RETRY}"
    )


def unreadable_as_csv(path: str, detail: str) -> str:
    """Message for a file the CSV reader could not make sense of."""
    return (
        f"The file {path} could not be read as a CSV table "
        f"({_shown(detail)}). "
        f"synthtwin reads comma-separated files with one row per line "
        f"and quotation marks around any value that contains a comma. "
        f"{_CHECK_AND_RETRY}"
    )


def readers_disagree(path: str, first: str, second: str) -> str:
    """Message for the two reading passes not agreeing (P1-D3)."""
    return (
        f"synthtwin read {path} twice and got two different answers: "
        f"{first}, then {second}. That usually means the file changed "
        f"while it was being read. Make sure nothing else is writing "
        f"to the file, then run the command again. synthtwin refuses "
        f"to describe a table it could not read the same way twice."
    )


def out_of_memory(path: str, size_bytes: int) -> str:
    """Message for a table too large for the memory available."""
    megabytes = size_bytes // (1024 * 1024)
    return (
        f"There was not enough memory to read {path} ({megabytes} MB "
        f"on disk, and a table takes several times its file size in "
        f"memory). Close other programs and try again, or use a "
        f"smaller extract of the table. Take rows spread through the "
        f"whole file, or a random sample of rows -- not the first rows, "
        f"which describe only one part of a table that is sorted. "
        f"Reading very large files in pieces is planned but not built "
        f"yet."
    )


def out_of_memory_while_describing(path: str) -> str:
    """Message for memory exhausted after the table was read."""
    return (
        f"There was not enough memory to finish describing {path}. "
        f"Close other programs and try again, or run synthtwin on a "
        f"smaller extract of the table. Take rows spread through the "
        f"whole file, or a random sample of rows -- not the first rows: "
        f"if the table is sorted by date, by place, or by how ill "
        f"people were, the first rows describe only one part of it and "
        f"the twin would be wrong in the same way. Describing very "
        f"large files in pieces is planned but not built yet."
    )


def publication_guard_stopped(where: str) -> str:
    """Message for a description carrying something it may not publish.

    `where` names the PLACE in the description -- `publication_notes[]
    .note`, `columns[].levels[].label` -- and never what stood there.
    The whole reason this run is stopping is that synthtwin could not
    account for that text, so showing it would publish to a screen what
    the guard is refusing to publish to a file (plan P2-D2).

    It says the fault is synthtwin's, because it is: no table can cause
    it, nothing about the file needs changing, and the only useful next
    step is to tell the people who can repair it.
    """
    return (
        f"synthtwin stopped before writing anything. While checking the "
        f"description it had just built, it found something at "
        f"'{where}' that its own publication rules do not account for, "
        f"and it will not write a description it cannot account for. "
        f"Nothing was written and your table was not changed. This is a "
        f"fault in synthtwin itself: no table causes it and there is "
        f"nothing to fix in your file. Please report it to the "
        f"synthtwin maintainers, with the quoted place above and the "
        f"command you ran -- and please do not include your data."
    )


# WHAT ONE COMMAND CALLS ITS OWN FILES (plan P2-D10).
#
# The write transaction serves every command that writes. `profile`
# reads a table and writes a profile beside a summary; `generate` reads
# that profile and writes a twin beside a report; `validate` reads the
# profile and one file and writes the quality report. The machinery is
# one piece of code and
# has to be -- two files or neither, every name looked at, every leftover
# named -- but the WORDS are not one set of words, and an inherited
# wording here is not a small blemish. A `generate` run that stopped
# would have told the person that their PROFILE could not be written,
# when the profile is the file they handed in and is the one file that
# run never writes to; and it would have sent them to check a table that
# is not part of that command at all. Somebody acting on either sentence
# looks at the wrong file, which is the whole cost of getting a message
# wrong.
#
# So the nouns are an argument. Each builder that needs them takes one
# `ArtifactWords` and defaults to the profiler's set, which is why every
# message the profiler produces is the same byte for byte as it was
# before this argument existed.
#
# The words live HERE, with every other message, rather than arriving
# from the module that composes the refusal: somebody who wants to know
# what a person reads reads this file and no other.


@dataclasses.dataclass(frozen=True)
class ArtifactWords:
    """What one command calls the files it writes and the file it was given.

    Guarantees:

    - Inputs: five pieces of text, each written out in one of the two
      sets below. Nothing here comes from a table, a profile, or
      anything else a run reads.
    - Determinism: a frozen record of constants, so the same set always
      composes the same message.
    - Errors raised: none.
    - Boundary: no value out of a user's file can reach one of these,
      because the only instances are the two module constants below and
      neither is built from anything a run read.

    The five, and exactly where each one lands:

    * ``produced`` -- what this command writes, as one noun: "The
      {produced} could not be written to ...", and "a file of the
      {produced}'s name is a link ...";
    * ``given`` -- what the person handed the command, as one noun:
      "... next to your {given}", and "... replaced your own {given} at
      ...";
    * ``new_file`` -- that same output named as a thing being written:
      "synthtwin stopped because writing {new_file} would have ...". It
      is a second field rather than a reuse of ``produced`` because the
      profiler's two sentences genuinely say two different words, and
      folding them together would have changed a message that no review
      asked to change;
    * ``loss`` -- one whole sentence saying what replacing ``given``
      would have cost. A sentence rather than a noun because what is
      lost differs in kind: a table is data nobody can rebuild, while a
      profile is the description a twin is built from;
    * ``mismatch`` -- one clause saying why this command's two files must
      never be left standing side by side from two different runs;
    * ``published`` -- the same output as the noun a sentence about what
      is on disk uses: "No new {published} was published", "... holds
      the new {published} this run produced", "... holds the
      {published} from before this run". It is a fourth spelling of the
      same file rather than a reuse of ``new_file`` because these
      sentences take no article, and folding them together would have
      moved a message no review asked to change;
    * ``working_holds`` -- one clause saying what a working file this
      command could not clear away is holding.

    THE LAST TWO ARRIVED WITH REVIEW ITEM P3-V4-F11, and the defect they
    close is the one this whole record exists for, found in the place it
    had not reached. A stopped `validate` run -- one that had installed
    a quality report and put the earlier one back -- told the person "No
    new description was published", about a command that writes no
    description and had just written a report. The words describing what
    is at each name were the same: a twin's own rollback said its twin
    file "holds the new description this run produced". Both sentences
    were composed here, from constants, with no way for the running
    command to say what it was actually writing.

    Four fields hold whole clauses or article-less nouns rather than one
    noun, and that is the deliberate choice. Substituting nouns into one
    fixed sentence would have forced every command to say the same thing
    about facts that are not the same, and a sentence that is
    grammatical and untrue is worse than three sentences.
    """

    produced: str
    given: str
    new_file: str
    loss: str
    mismatch: str
    published: str
    working_holds: str


# The profiler's set: the words every one of these messages used before
# they took an argument, unchanged to the byte.
PROFILE_WORDS = ArtifactWords(
    produced="profile",
    given="table",
    new_file="the description",
    loss="That would have destroyed the data you asked it to describe.",
    mismatch=(
        "a profile and a summary from two different runs do not describe "
        "the same table"
    ),
    published="description",
    working_holds="text taken from your table",
)

# The generator's set. `mismatch` says what actually goes wrong there:
# the report describes the twin beside it -- how well it matches, which
# columns were approximated, which warnings apply -- so a report from one
# run standing beside a twin from another describes a file that is not
# there.
TWIN_WORDS = ArtifactWords(
    produced="twin",
    given="profile",
    new_file="the twin",
    loss="That would have destroyed the description your twin is built from.",
    mismatch="a report from one run does not describe the twin from another",
    published="twin",
    # `generate` opens no table, so a working file of its own holds text
    # derived from the description it was handed and from nothing else.
    working_holds="text taken from the description your twin is built from",
)

# The validator's set (plan P3-D1). `validate` writes ONE file, so the
# transaction it uses is the one-target form and `mismatch` reads
# differently here from the two sets above: there is no second file this
# one has to match, and what a stale quality report contradicts is the
# FILE IT MEASURED. A report left standing from an earlier run states
# verdicts about bytes that are no longer at that name, which is the
# same failure -- a reader trusting a sentence about a file that is not
# there -- reached by a different route.
#
# `given` is the description rather than the measured file because that
# is the file the command is HANDED, exactly as `generate` is handed a
# description; the measured file is named by its own noun wherever a
# message needs to tell the two apart (`INPUT_MEASURED_FILE` below).
QUALITY_WORDS = ArtifactWords(
    produced="quality report",
    given="description",
    new_file="the quality report",
    loss=(
        "That would have destroyed the description the verdicts are "
        "measured against."
    ),
    mismatch=(
        "a quality report from one run does not describe the file "
        "another run measured"
    ),
    published="quality report",
    # A validate working file holds the report, which is counts and
    # measurements taken from the file that was checked -- and that file
    # may be the person's own table or may be a twin of it, which is why
    # this names what was measured rather than guessing which it was.
    working_holds=(
        "counts and measurements taken from the file synthtwin checked"
    ),
)

# The two files a `validate` run reads, as the nouns a refusal uses to
# say WHICH of them an output name would have landed on (plan P3-D1).
# One `ArtifactWords` carries one `given`, and this command is handed
# two files, so the second one is named here rather than by bending a
# record that exists to name one.
INPUT_DESCRIPTION = "description"
INPUT_MEASURED_FILE = "file you asked synthtwin to check"


COULD_NOT_CHECK = (
    "synthtwin could not read what is at that name to see whether it is "
    "safe to write there"
)

# What one name on disk can be holding when a run stops part way. The
# caller LOOKS at the disk and passes one of these codes for each name;
# the words a person reads live here, with every other message.
#
# The codes distinguish states that an earlier version ran together,
# because the difference is exactly what a researcher needs: an old
# profile still in place, a new one, and a name that is empty because
# its file was moved aside and could not be put back are three
# different situations, and only one of them is safe to ignore (review
# item P1-R6-F5).
ON_DISK_BEFORE = "before"
ON_DISK_RESTORED = "restored"
ON_DISK_ABSENT = "absent"
ON_DISK_TAKEN_AWAY = "taken-away"
ON_DISK_NEW = "new"
ON_DISK_SET_ASIDE = "set-aside"
ON_DISK_WORKING = "working"
ON_DISK_EMPTY_WORKING = "empty-working"
# A working name synthtwin created and then could not examine. It is
# separate from `empty-working` because synthtwin cannot say the name
# still holds the empty file it made, and separate from `unchecked`
# because synthtwin DID make it -- which is what the reader needs in
# order to know whose file it is (review item P1-R7-F1).
ON_DISK_UNCERTAIN_WORKING = "uncertain-working"
# A working name synthtwin had CLAIMED and was in the middle of creating
# when the run stopped. Creating a file is one step for the operating
# system and two moments for this program -- the file appears, and only
# then does the creating call hand back -- so a run stopped in between
# holds a name it may or may not have made anything at.
#
# It is separate from `empty-working` because synthtwin cannot say it
# made this one, and separate from `uncertain-working` because that one
# IS synthtwin's for certain and only its condition is in doubt. The
# difference decides what happens next: a name in this state is NAMED to
# the person and never removed, because removing it would risk deleting
# a file that was already there under that name (review item P1-R8-F1).
ON_DISK_CLAIMED_WORKING = "claimed-working"
ON_DISK_UNCHECKED = "unchecked"
# A name that HAS a file, at a moment when synthtwin was moving the two
# names into place and stopped for a reason it did not foresee -- memory
# exhausted, or a person pressing Ctrl-C. Which of the run's files
# ended up here is exactly what the code that did not finish would have
# known. It is separate from `unchecked` because the name WAS examined,
# and separate from `new`, `before` and `set-aside` because any of those
# would be a guess presented as a fact (review item P1-R7-F1).
ON_DISK_UNSETTLED = "unsettled"


def _on_disk_words(words: "ArtifactWords") -> "dict[str, str]":
    """What each on-disk code says, for the command that is running.

    Three of these name the file the RUNNING COMMAND writes and one
    says what a working file holds, so the table is built from that
    command's own nouns rather than written out once with the
    profiler's (review item P3-V4-F11).

    Guarantees:

    - Inputs: one `ArtifactWords`, whose fields are module constants of
      this file; nothing here comes from a table, a profile, or
      anything else a run reads.
    - Determinism: a fixed function of that record.
    - Errors raised: none.
    - Boundary: no value out of a user's file can reach one of these.
    """
    return {
        ON_DISK_BEFORE: "the file that was there before this run, unchanged",
        ON_DISK_RESTORED: "the file that was there before this run, put back",
        ON_DISK_ABSENT: (
            "nothing -- there is no file of that name, just as before "
            "this run"
        ),
        ON_DISK_TAKEN_AWAY: (
            "nothing -- the file that was there before this run was moved "
            "aside and could not be put back"
        ),
        # THESE THREE NAME THE FILE THIS COMMAND WRITES, and used to
        # name a description whichever command was running (review item
        # P3-V4-F11). The profiler's set fills them with exactly the
        # words that stood here before, so nothing a `profile` run
        # prints moved.
        ON_DISK_NEW: f"the new {words.published} this run produced",
        ON_DISK_SET_ASIDE: (
            f"the {words.published} from before this run, which synthtwin "
            f"moved here and could not move back"
        ),
        ON_DISK_WORKING: (
            f"a working file synthtwin could not clear away; it holds "
            f"{words.working_holds}"
        ),
        ON_DISK_EMPTY_WORKING: (
            "an empty working file synthtwin could not clear away; it holds "
            "nothing"
        ),
        ON_DISK_UNCERTAIN_WORKING: (
            "something synthtwin made for its own use, wrote nothing into, "
            "and could not clear away or examine afterwards"
        ),
        ON_DISK_CLAIMED_WORKING: (
            "something at a working name synthtwin had claimed and was still "
            "creating when the run stopped. synthtwin wrote nothing into it "
            "and did not remove it, because it cannot tell whether it made "
            "this file or whether the name was already taken by something "
            "else; please look at it before you delete it"
        ),
        ON_DISK_UNCHECKED: "not known: synthtwin could not check this name",
        ON_DISK_UNSETTLED: (
            "a file -- but synthtwin stopped while it was moving these "
            "names into place, so it cannot say which of this run's files "
            "ended up here; look at every name in this message before you "
            "use or delete any of them"
        ),
    }


_UNKNOWN_STATE = "not known: synthtwin could not say what is there"


def _stated(
    on_disk: "list[tuple[str, str]]", words: "ArtifactWords"
) -> str:
    """One clause per name: the path, then what is at it now.

    Each pair is a path and one of the ON_DISK_ codes above. A code
    this module does not recognize is reported as unknown rather than
    dropped: a message about what is on disk must never quietly leave a
    file out.

    ``words`` names the file the running command writes, because three
    of those codes are about that file and used to say "description"
    whichever command was running (review item P3-V4-F11).
    """
    table = _on_disk_words(words)
    text = ""
    for path, code in on_disk:
        said = _UNKNOWN_STATE
        if code in table:
            said = table[code]
        piece = f"{_shown(path)} holds {said}"
        if not text:
            text = piece
        else:
            text = f"{text}; {piece}"
    return text


def _anything_is_there(on_disk: "list[tuple[str, str]]") -> bool:
    """True when at least one of these names holds a file right now."""
    for _path, code in on_disk:
        if code == ON_DISK_ABSENT or code == ON_DISK_TAKEN_AWAY:
            continue
        return True
    return False


def nothing_was_written(
    stubborn: list[str],
    on_disk: "list[tuple[str, str]] | None" = None,
    words: ArtifactWords = PROFILE_WORDS,
) -> str:
    """Say what is on disk after a run that published no new output.

    ``words`` names the file THIS command writes (review item
    P3-V4-F11). It used to say "description" whichever command was
    running, so a stopped `validate` run that had put an earlier
    quality report back told the person no new description was
    published -- naming a file that command never writes, about a run
    that had just written a report. The default is the profiler's set,
    so every sentence a stopped `profile` run prints is the same byte
    for byte as it was before this argument existed.

    ``on_disk`` carries one (path, code) pair for every name the run
    could have changed -- the two output names first, then any working
    file left behind -- where each code is one of the ON_DISK_ constants
    above and the caller has LOOKED at the disk to arrive at it.

    ``stubborn`` names working files that would not go away, for a
    caller that has not looked; a caller that passes ``on_disk``
    describes those same files there, with what each one holds.

    The sentence never claims a clean failure it did not check. The
    earlier version said "both files are as they were before" whatever
    had happened, and said working files "hold no description of your
    table" even when one held a full profile (review item P1-R6-F5).
    """
    if on_disk:
        tail = "Check each one before you use it."
        if not _anything_is_there(on_disk):
            tail = "There is nothing left to clear up."
        return (
            f"No new {words.published} was published. This is what is at "
            f"each name now: {_stated(on_disk, words)}. {tail}"
        )
    if stubborn:
        listed = _listed(stubborn)
        return (
            f"No new {words.published} was published, and synthtwin could "
            f"not clear away its own working file(s): {listed}. Check "
            f"each one -- a working file can hold {words.working_holds} "
            f"-- and delete it when you have."
        )
    return (
        f"No new {words.published} was published. synthtwin did not check "
        f"the output name(s) afterwards, so please look at each one "
        f"before you use it."
    )


def rollback_failed(
    left: list[str],
    on_disk: "list[tuple[str, str]] | None" = None,
    words: ArtifactWords = PROFILE_WORDS,
) -> str:
    """Say what is on disk after a run that could not undo its own work.

    The first two parameters mean exactly what they mean in
    ``nothing_was_written``. This wording is for the case where the
    files on disk no longer match what was there before the run and
    synthtwin could not put them back -- so it names each one and says
    which run its contents came from.

    ``words`` names the files for the command that is running. Its
    ``mismatch`` clause closes the message -- the instruction has to say
    why the files must not be left as they are, and that reason is not
    the same for a profile beside a summary as it is for a twin beside a
    report -- and its ``published`` noun names what each name is holding
    (review item P3-V4-F11): a rollback of a `generate` run used to say
    that the twin's own name "holds the new description this run
    produced". Left out, the profiler's set is used, which is the
    wording this message has always had.
    """
    if on_disk:
        return (
            f"synthtwin could not put things back as they were. This is "
            f"what is at each name now: {_stated(on_disk, words)}. Check "
            f"each one before you use it, and finish by hand what "
            f"synthtwin could not: {words.mismatch}."
        )
    listed = _listed(left)
    return (
        f"synthtwin could not put things back as they were, so these "
        f"files are left: {listed}. Check each one before using it: it "
        f"may hold the {words.published} from this run or from an "
        f"earlier one."
    )


def working_name_unavailable(
    target: str, tried: list[str], attempts: int
) -> str:
    """Message for working names beside an output that are all taken."""
    listed = _listed(tried)
    return (
        f"synthtwin could not make itself a working file beside {target}. "
        f"It writes each file under a working name first and moves it "
        f"into place only once the whole file is on disk, and all "
        f"{attempts} working names it tried are already taken (the first "
        f"of them: {listed}). synthtwin never writes over a file it did "
        f"not create, so it stopped instead. Those files are usually "
        f"left over from a run that was interrupted: check what they "
        f"are, move or delete them, and run the command again."
    )


def output_folder_missing(
    path: str, words: ArtifactWords = PROFILE_WORDS
) -> str:
    """Message for an output folder that does not exist.

    ``words`` decides both nouns: what the command would have written
    there, and what the person's own file is called, since the advice
    for leaving the option out is "next to the file you gave me". Left
    out, the profiler's words are used, which is the wording this
    message has always had.
    """
    return (
        f"The folder {path} does not exist, so synthtwin cannot write "
        f"the {words.produced} there. Create the folder first, or leave "
        f"the option out to write the {words.produced} next to your "
        f"{words.given}."
    )


def output_not_writable(
    path: str, detail: str, words: ArtifactWords = PROFILE_WORDS
) -> str:
    """Message for an output location that could not be written.

    ``words`` decides which file this says could not be written. It
    matters more here than anywhere else in the catalog, because this is
    the message almost every stop inside the write transaction ends up
    composing: a `generate` run that told somebody their PROFILE could
    not be written would be naming the one file that run never writes
    to, and sending them to look at it. Left out, the profiler's word is
    used, which is the wording this message has always had.
    """
    return (
        f"The {words.produced} could not be written to {path} "
        f"({_shown(detail)}). "
        f"Please check that you have permission to write there and "
        f"that the file is not open in another program, then run the "
        f"command again."
    )


def output_is_a_folder(path: str) -> str:
    """Message for an output target that a folder already occupies."""
    return (
        f"synthtwin cannot write to {path}, because a folder of that "
        f"name is already there. Move or rename the folder, or use the "
        f"option for a different output folder, then run the command "
        f"again."
    )


def output_would_replace_the_table(
    path: str, words: ArtifactWords = PROFILE_WORDS
) -> str:
    """Message for an output target that IS the file the person gave.

    The name of this builder is the profiler's: there, the file being
    protected is the user's own table, and that is what the name says.
    Under ``words`` it protects whichever file the running command was
    handed -- the table for `profile`, the profile document for
    `generate` -- because the rule is the same one in both: nothing
    synthtwin writes may land on the file it was asked to read. The name
    was left alone so that every caller and every catalog entry written
    against it keeps working; the words a person reads are the ones that
    change.

    All four of ``words``'s remaining pieces land here: what would have
    been replaced, what writing it was, what that would have cost, and
    whose name the stray link is wearing.
    """
    return (
        f"synthtwin stopped because writing {words.new_file} would have "
        f"replaced your own {words.given} at {path}. {words.loss} This "
        f"usually means a file of the {words.produced}'s name is a link "
        f"pointing back at the {words.given}. Remove that link, or use "
        f"the option for a different output folder, then run the command "
        f"again. Nothing was written."
    )


def output_would_replace_an_input(
    path: str, source: str, words: ArtifactWords = PROFILE_WORDS
) -> str:
    """Message for an output name that leads back to one of two inputs.

    `output_would_replace_the_table` above protects the ONE file its
    command was handed. `validate` is handed two -- the description and
    the file it measures -- and a report written over either of them is
    the same accident with two different costs, so the refusal has to
    say which one it caught (plan P3-D1). ``source`` is one of the two
    nouns written out beside `QUALITY_WORDS`, never a value out of a
    file: on this path the measured file may not be the reader's own
    table, and a refusal travels as freely as a report does.

    ``words`` supplies what would have been written. The remaining
    fields of the record are not used here on purpose: `loss` and
    `given` speak about one handed-in file, and this message's whole
    job is that there are two.
    """
    return (
        f"synthtwin stopped because writing {words.new_file} would have "
        f"replaced the {source} at {path}. Both files a check reads have "
        f"to still be there when it finishes, so synthtwin wrote nothing. "
        f"This usually means a file of the {words.produced}'s name is a "
        f"link pointing back at one of them. Remove that link, or use "
        f"the option for a different output folder, then run the command "
        f"again. Nothing was written."
    )


def output_is_not_a_plain_file(path: str) -> str:
    """Message for an output target that is not an ordinary file."""
    return (
        f"synthtwin cannot write to {path}, because something that is "
        f"not an ordinary file is already there -- a pipe, a device, or "
        f"another special entry. Writing to it could send your "
        f"real-derived description somewhere you cannot see. Remove it, "
        f"or use the option for a different output folder, then run the "
        f"command again."
    )


def outputs_are_the_same_file(first: str, second: str) -> str:
    """Message for two output targets that are one file underneath."""
    return (
        f"synthtwin stopped because {first} and {second} are two names "
        f"for the same file. Writing both would leave you with only one "
        f"of them and no way to tell which. This usually means one name "
        f"is a link to the other. Remove that link, or use the option "
        f"for a different output folder, then run the command again. "
        f"Nothing was written."
    )


def unknown_column_named(purpose: str, name: str, known: list[str]) -> str:
    """Message for an option naming a column the table does not have."""
    shown = _listed(known[:10])
    more = "" if len(known) <= 10 else f", and {len(known) - 10} more"
    return (
        f"You asked synthtwin to treat a column called '{_shown(name)}' as "
        f"{purpose}, but this table has no column with that name. Its "
        f"columns are: {shown}{more}. Check the spelling and run the "
        f"command again. Nothing was written."
    )


def floor_not_positive(given: str) -> str:
    """Message for a small-cell floor that is not a positive whole number."""
    return (
        f"The smallest group size must be a whole number of 1 or more, "
        f"but {given} was given. Give a whole number, or leave the "
        f"option out altogether to use the default of 11: any value "
        f"shared by fewer than 11 rows is then left out of the profile, "
        f"so that a rare value cannot point back at anybody."
    )


# -- reading a description back: the strict loader's refusals ---------
#
# Nineteen ways reading a profile document can fail, one message each,
# catalogued as R1 to R19 in `docs/spec/profile-contract-v4.md` section
# 10.7, carried into version 5 unchanged except that R11 and R12 read
# against 5 (`docs/spec/profile-contract-v5.md` section 10), and carried
# out by `contract.py`. The word "description" is used
# throughout rather than "profile document", because it is what the
# person running the tool was told the file is.
#
# NO MESSAGE BELOW QUOTES A ROW COUNT, and the rule has no exceptions.
# Reading a description can run out of memory before a single field has
# been checked, so a message naming a row count could be naming a number
# nobody read. Where a row count is the thing that is wrong, the message
# says which row count and where it lives, and never what it says.

_MAKE_IT_AGAIN = (
    "Please make the description again by running 'synthtwin profile' "
    "on your table, and use the file it writes exactly as it writes it."
)

_A_DESCRIPTION_IS_WRITTEN = (
    "A description is always written by 'synthtwin profile'; it is not "
    "a file to edit by hand."
)


def profile_file_missing(path: str) -> str:
    """R1: the description path names nothing on disk."""
    return (
        f"There is no file at {path}. That is where synthtwin looked for "
        f"the description of your table. Please check the spelling of "
        f"the path, and that the file -- the one whose name ends in "
        f"-profile.json -- is on this computer and not in a folder you "
        f"have not opened yet."
    )


def profile_file_unreadable(path: str, detail: str) -> str:
    """R2: the description exists but could not be read."""
    return (
        f"The description at {path} could not be opened "
        f"({_shown(detail)}). Please check that you have permission to "
        f"read it, that the drive or folder it is on is still connected, "
        f"and that no other program is holding it open, then run the "
        f"command again."
    )


def profile_path_is_a_folder(path: str) -> str:
    """R3: a folder was given where the description was expected."""
    return (
        f"{path} is a folder, not a file. Please give the path of the "
        f"description itself: the file inside that folder whose name "
        f"ends in -profile.json."
    )


def profile_not_text(path: str) -> str:
    """R4: the bytes are not valid UTF-8."""
    return (
        f"The file at {path} is not readable as text, so it is not a "
        f"description synthtwin can use. {_A_DESCRIPTION_IS_WRITTEN} It "
        f"is saved as UTF-8 text and stays that way unless something "
        f"else has rewritten it. {_MAKE_IT_AGAIN}"
    )


def profile_not_json(path: str, line: int, character: int) -> str:
    """R5: the text is not the machine-readable form at all."""
    return (
        f"The description at {path} stopped making sense at line {line}, "
        f"character {character}, so synthtwin could not read it. A file "
        f"that has been edited by hand, or that was only partly copied "
        f"or downloaded, usually stops like this. {_MAKE_IT_AGAIN}"
    )


def profile_holds_unwritable_text(path: str) -> str:
    """R6: an escaped lone surrogate, which cannot be written as text."""
    return (
        f"The description at {path} holds a character that cannot be "
        f"written as text at all, so synthtwin cannot check that the "
        f"file is exactly as it was written. A description synthtwin "
        f"writes never contains one. {_MAKE_IT_AGAIN}"
    )


def profile_holds_a_number_that_is_not_one(path: str) -> str:
    """R7: a non-finite number the parser would otherwise accept."""
    return (
        f"The description at {path} holds something written as a number "
        f"that is not a number: an infinity, or the words for 'not a "
        f"number'. A description synthtwin writes never contains one, "
        f"and no program that reads this format may write one. "
        f"{_MAKE_IT_AGAIN}"
    )


def profile_nested_too_deeply(path: str, limit: int) -> str:
    """R8: blocks nested deeper than the loader's one depth bound."""
    return (
        f"The description at {path} has blocks nested inside one another "
        f"more than {limit} deep. A description synthtwin writes is six "
        f"deep whatever your table holds, so no table can make it "
        f"deeper, and this is not a file synthtwin wrote. "
        f"{_MAKE_IT_AGAIN}"
    )


def profile_number_too_long(path: str, limit: int) -> str:
    """R9: a single numeric token longer than the loader's bound."""
    return (
        f"The description at {path} holds a number written with more "
        f"than {limit} characters. A description synthtwin writes never "
        f"contains one anywhere near that long, so this is not a file "
        f"synthtwin wrote. {_MAKE_IT_AGAIN}"
    )


def profile_not_canonical(path: str) -> str:
    """R10: the file is not byte for byte the form synthtwin writes."""
    return (
        f"The description at {path} is not in the exact form synthtwin "
        f"writes: written out again, it does not come out the same. "
        f"Opening a description in an editor and saving it, saving it "
        f"from another program, merging two versions of it, or repeating "
        f"or reordering an entry will each do this. synthtwin will not "
        f"build a twin from a description it cannot prove is unchanged. "
        f"{_MAKE_IT_AGAIN}"
    )


def profile_version_is_older(found: int, reads: int) -> str:
    """R11: an older description, which is safely made again.

    THE WORDING IS FIXED BY THE CONTRACT, word for word (contract 5
    section 10.2, C5-26), with only the two version numbers filled in.
    It has to say three things and it says them in this order: which
    version each side is, WHY the older file cannot simply be read --
    because it does not record which of synthtwin's own words for "no
    value" the person named -- and what to do, which is to describe the
    table again UNDER THE SAME OPTIONS.

    IT NAMES FIVE OPTIONS AND NAMED TWO UNTIL 2026-08-17, AND THE TWO
    COULD DISCLOSE (review item P3-V9-F6; plan amendment A-P3-36). The
    retired wording named `--keep-value` and `--missing-value` only.
    Follow it to the letter -- which is what a person who does not
    program will do, because it is the whole of what they were told --
    after a first run that used `--smallest-group 20` on a table holding
    a declared marker in twelve cells, and the floor goes back to the
    default eleven. Twelve now clears it, so the NEW description names a
    spelling the old one pooled: the old file withheld a word of the
    person's own and the new one publishes it, with no warning anywhere.
    `--identifier` is the same shape and reaches further, because a
    column named there publishes no value of the table at all, and a
    re-run without it describes that column of record numbers like any
    other.

    AND ALL FIVE CHANGE WHAT IT PUBLISHES, WHERE THIS SAID TWO UNTIL
    2026-08-17 (review item P3-V10-F2; plan amendment A-P3-42 clause 1).
    The sentence named five options, priced two of them as
    disclosure-changing, and said of the other three only that they
    change how the table is READ. That was measured and it is false;
    each of the three was run through the real producer, twice, and the
    two descriptions compared:

    * `--first-row`. A file with no header row, whose first line holds a
      code. Described with `--first-row data` the column is called
      `column_1` and the code is one free-text value among many, which a
      free-text column publishes nowhere. Left out, the first line is
      taken for the column NAMES by convention and the code IS the
      column's name -- published in full, with no floor over it, because
      a column name is not a value of the table and no floor applies.
    * `--missing-value`. Sixty readings and five cells holding `-100`,
      named as "no value". Described that way the five are absent, five
      is under the floor and the number is published nowhere. Left out,
      `-100` is a reading: it is the smallest one, so the description
      publishes it as the column's minimum and as its first two
      percentiles.
    * `--keep-value`. Sixty readings and twelve cells holding a word,
      named as real data. Described that way the column reads as free
      text -- twelve of its values are not numbers -- and free text
      publishes no value at all. Left out, the word is one of
      synthtwin's own for "no value", the column reads as numbers, and
      the description publishes the whole distribution of the sixty
      readings AND the word, character for character, in
      `missing_by_source`.

    So the message names every option of `synthtwin profile` that
    changes what the description says about the table, says of every one
    of them that it changes what the description PUBLISHES, gives the
    consequence of leaving each out, and sends the person to the summary
    page before either new file travels. An option added to the profiler
    joins this sentence in the commit that adds it -- and it joins the
    priced list too, unless somebody can show it changes only the
    reading, which is what nobody could show for these three.

    WHY THE ADVICE IS SAFE TO GIVE, AND WHEN IT STOPS BEING SAFE.
    Somebody holding an old description of their own table is normally
    somebody who still holds the table, and today that is true of every
    description in existence: there is no release and no tag. After the
    first release this assumption is no longer safe for every reader,
    and this wording is re-examined rather than inherited.

    Nothing of the document is quoted here except the version it claims
    (C5-28), so the message cannot tell the person which options THEIR
    description was made with even though its settings block records
    them: the version is read before that block is validated at all.
    What is owed and paid is that they are told which options matter.
    """
    return (
        f"This description was written by an older version of synthtwin: "
        f"it says it is version {found}, and this synthtwin reads "
        f"version {reads}. A version {reads} description records which "
        f"of synthtwin's own words for \"no value\" you named on the "
        f"command line, and a version {found} description does not, so "
        f"this file cannot be read back exactly. Please make the "
        f"description again by running 'synthtwin profile' on your "
        f"table, giving it every option you gave the first time: "
        f"--keep-value, --missing-value, --identifier, --smallest-group "
        f"and --first-row. Every one of them changes what the "
        f"description PUBLISHES about your table, so any option you "
        f"leave out can put something into the new description that the "
        f"old one held back: without the --smallest-group you gave, a "
        f"value that fewer rows share can be named; without the "
        f"--identifier you gave, a column of record numbers is "
        f"described like any other column; without the --missing-value "
        f"you gave, a stand-in is read as a real reading, and the "
        f"stand-in itself can be published as the column's smallest "
        f"value; without the --keep-value you gave, a word you had "
        f"counted as an ordinary value becomes a gap, which can change "
        f"what kind of column synthtwin sees and publish both that word "
        f"and the column's own numbers; and without the --first-row you "
        f"gave, the first line of your file is read as the column names "
        f"and published as them. Read the summary page synthtwin writes "
        f"beside the new description before either file goes anywhere, "
        f"and use the description exactly as synthtwin writes it."
    )


def profile_version_is_newer(found: int, reads: int) -> str:
    """R12: a newer description, which is never made again here.

    A newer description means this synthtwin is behind. Telling somebody
    to re-run a profiler on a machine that may not hold the table -- or
    that may hold a different table -- is advice that cannot be followed
    and may be acted on anyway, so it is not given.
    """
    return (
        f"This description was written by a newer version of synthtwin: "
        f"it says it is version {found}, and this synthtwin reads "
        f"version {reads}. Please update synthtwin to a version that "
        f"reads version {found}, then run the command again. Do not make "
        f"the description again on this computer: the file you have is "
        f"the newer one, and this computer may not hold the table it "
        f"describes."
    )


def profile_unknown_key(key: str, where: str) -> str:
    """R13: an entry this version of synthtwin does not know."""
    return (
        f"The description has an entry called '{_shown(key)}' "
        f"{_shown(where)}, and this version of synthtwin does not know "
        f"it. That usually means the file was written by a newer "
        f"synthtwin, or that it was edited. Please update synthtwin if "
        f"the file came from a newer one. Otherwise: {_MAKE_IT_AGAIN}"
    )


def profile_missing_key(key: str, where: str, required_by: str) -> str:
    """R14: an entry that every block of this kind carries."""
    return (
        f"The description has no entry called '{_shown(key)}' "
        f"{_shown(where)}, and {_shown(required_by)} has one. "
        f"{_MAKE_IT_AGAIN}"
    )


def profile_wrong_type(
    key: str, where: str, found: str, required: str
) -> str:
    """R15: an entry holding a kind of value it may not hold.

    What was found is named as a KIND of value and never quoted: the
    thing that is wrong is the kind, and quoting a value nobody asked
    to see puts real-derived text on a screen for no reason.
    """
    return (
        f"The entry called '{_shown(key)}' {_shown(where)} holds "
        f"{_shown(found)}, and it has to hold {_shown(required)}. "
        f"{_MAKE_IT_AGAIN}"
    )


def profile_out_of_range(
    key: str, where: str, shown: str, permitted: str
) -> str:
    """R16: a value outside its range or its list of allowed values."""
    return (
        f"The entry called '{_shown(key)}' {_shown(where)} holds "
        f"{_shown(shown)}, and the only thing allowed there is "
        f"{_shown(permitted)}. {_MAKE_IT_AGAIN}"
    )


def profile_out_of_range_unquoted(
    key: str, where: str, permitted: str
) -> str:
    """R16 for a row count, whose value is deliberately not shown.

    The only difference from `profile_out_of_range` is that the value
    itself does not appear. No message on the loader's path quotes a row
    count, because reading a description can run out of memory before
    any field has been checked (contract 10.7).
    """
    return (
        f"The entry called '{_shown(key)}' {_shown(where)} holds "
        f"something that is not allowed there: it has to be "
        f"{_shown(permitted)}. {_MAKE_IT_AGAIN}"
    )


def profile_invariant_broken(
    rule: str, words: str, where: str, first: str, second: str
) -> str:
    """R17: a rule of the description that this file breaks.

    ``rule`` is the rule's short name in the description contract, which
    is there for anybody who wants to look it up; ``words`` is the rule
    itself in plain language, and the two clauses are the quantities
    that disagree and where each of them lives.
    """
    return (
        f"The description does not hold together {_shown(where)}: "
        f"{_shown(words)}. But {_shown(first)}, and {_shown(second)}. A "
        f"description synthtwin writes always keeps that rule (it is "
        f"called {_shown(rule)} in synthtwin's description contract), so "
        f"this file has been changed since it was written. "
        f"{_MAKE_IT_AGAIN}"
    )


def profile_relationships_carried(key: str) -> str:
    """R18: the reserved cross-column block carries something."""
    return (
        f"The description says something under '{_shown(key)}' about how "
        f"the columns move together, and this version of synthtwin does "
        f"not carry that: it reads a description in which all eight of "
        f"those entries are empty. A file that fills one of them was "
        f"written by a newer synthtwin. Please update synthtwin, then "
        f"run the command again."
    )


def profile_out_of_memory(path: str) -> str:
    """R19: the machine ran out of memory while reading the file.

    The message names no count of anything out of the file: this can
    happen before a single field has been read.
    """
    return (
        f"There was not enough memory to read the description at {path}. "
        f"This computer could not hold a file of that size, and reading "
        f"one takes several times its size in memory. Close other "
        f"programs and try again, use a computer with more memory, or "
        f"describe a table with fewer columns: a description grows with "
        f"the number of columns, not with the number of rows."
    )


# -- building the twin: what `generate` refuses -----------------------
#
# Three refusals belong to the command rather than to the loader or to
# the method: a seed nobody can use, and a pair of output names that are
# already taken. Each is written here with every other message a person
# reads, and each says the same three things: what happened, what
# synthtwin did NOT do, and what to type next.
#
# WHY THE SEED HAS TWO MESSAGES rather than one. "That is not a number
# synthtwin can use" and "that number is larger than synthtwin's largest
# seed" are two different mistakes with two different repairs, and a
# single message covering both would have to be vague about both. The
# library underneath accepts a wider set than synthtwin does and refuses
# a negative one in its own words, which name a bit width and a data
# type; neither message below lets that reach a person (plan P2-D8).


def quality_out_of_memory(path: str) -> str:
    """Message for a machine that ran out of memory checking a file.

    It names the DESCRIPTION, which is the file the person typed. A
    failure inside the measurement itself is composed where the file
    being read is known, and names that file instead; this one covers
    the rest of the run, where the honest answer is that synthtwin
    cannot say which of the two files it was holding at the time.
    """
    return (
        f"There was not enough memory to finish checking a file against "
        f"the description at {path}. Checking holds a whole description "
        f"of the measured file in memory at once, beside the description "
        f"it is being compared with, so it needs several times the space "
        f"the files themselves take. Please close other programs and run "
        f"the command again, or use a computer with more memory. Nothing "
        f"was written."
    )


def quality_target_already_there(target: str) -> str:
    """Message for a `validate` run whose one output name is taken.

    The generate refusal's reasoning, at one file (plan P3-D1, R-P2-12
    parity). synthtwin cannot tell an earlier quality report of its own
    from a file of the person's that happens to sit at that name, and
    reading it to find out would open a third file on a path that is
    allowed exactly two. So it refuses, names the file, and teaches
    `--replace`.

    It is one paragraph, like every other message here: a refusal is
    shown as a VALUE on its way to the screen, so a line feed inside one
    reaches the reader as text rather than as layout.
    """
    return (
        f"synthtwin stopped because something is already at the name it "
        f"would write. This run writes one file, {target}, and it is "
        f"already there. Nothing was written and nothing was changed. If "
        f"that file can be replaced -- the usual reason is checking the "
        f"same twin again -- add --replace to the command. If not, move "
        f"or rename what is there, or give --out-dir a different folder "
        f"to write into, then run the command again."
    )


# WHY THE FOUR REFUSALS OF METHOD G12 ARE NAMED HERE (amendment
# A-P3-23, review item P3-V7-F7). The message a person reads when no
# twin of their description can exist was built by a private helper of
# `validation.py`, so it stood outside the failure catalog: none of the
# catalog's rules about the shape of a sentence reached it, no test
# pinned it, and nothing drove it through the shipped command. Plan
# P3-D6 asks for exact-shape AND reachability tests on it by name.
#
# The names live beside the message rather than in `validation`, because
# `errors` may not import the module that raises its messages and one
# spelling of these four strings is what keeps the message and the
# decision in step. `validation.refusal_of` answers one of these or the
# empty text, and a test asserts it can answer nothing else.
REFUSAL_COUNTS_CONTRADICT = "generation-counts-contradict"
REFUSAL_WORDS_EXCEED_LENGTH = "generation-words-exceed-length"
REFUSAL_WHOLE_NUMBERS_NEED_ROOM = "generation-whole-numbers-need-room"
REFUSAL_DOMAIN_TOO_SMALL = "generation-domain-too-small"

# What is wrong with the description, in the person's own words, one
# clause per refusal. Each names the TWO published facts that cannot
# both hold, because that is what the reader has to go and change.
NO_TWIN_TROUBLE = {
    REFUSAL_COUNTS_CONTRADICT: (
        "one column says how many of its numbers are zero and how many "
        "are negative, and those two counts together are more numbers "
        "than the column has"
    ),
    REFUSAL_WORDS_EXCEED_LENGTH: (
        "one column of text says its values hold more words than their "
        "own published lengths have room for"
    ),
    REFUSAL_WHOLE_NUMBERS_NEED_ROOM: (
        "one column of record numbers says its codes are whole numbers "
        "and gives them a length that leaves no room to write one"
    ),
    REFUSAL_DOMAIN_TOO_SMALL: (
        "one column of text asks for more different values than there "
        "are ways to write a value of its own published lengths at all"
    ),
}


def no_twin_of_this_description_exists(named: str, shown: str) -> str:
    """Message for a description no file on earth can be the twin of.

    It mirrors the generation refusal -- the description is valid, and
    two published facts cannot both hold -- and adds the sentence this
    path needs: whatever the measured file is, it cannot be that
    description's twin. It names no value of the measured file, because
    on this path that file may not be the person's own table.

    Both instructions are load-bearing and are why this is not one
    sentence: the person holding the table describes it again, and the
    person who was handed the description has to ask whoever wrote it,
    because there is nothing they can do to the FILE that would help.
    """
    return (
        f"synthtwin stopped because the description asks for a table "
        f"that cannot exist: {NO_TWIN_TROUBLE[named]}. The description "
        f"itself is valid -- it was written by synthtwin and it loads -- "
        f"but no file can hold both of those facts at once, so whatever "
        f"is in {shown}, it cannot be this description's twin and there "
        f"is nothing to measure it against. Describe the table again to "
        f"get a description these two facts agree in, and if you no "
        f"longer hold the table, ask whoever wrote the description to "
        f"do so."
    )


def twin_out_of_memory(path: str) -> str:
    """Message for a machine that ran out of memory building the twin.

    It names no count out of the description, for the same reason the
    loader's memory message names none: the run can stop before a single
    field has been read, so a number in this sentence could be a number
    nobody read.
    """
    return (
        f"There was not enough memory to build the twin from the "
        f"description at {path}. A twin holds every value of every column "
        f"at once while it is being built, so it needs several times the "
        f"space the finished file takes. Please close other programs and "
        f"run the command again, or use a computer with more memory. "
        f"Nothing was written."
    )


def seed_not_in_figures(given: str, ceiling: str) -> str:
    """Message for a seed spelled in anything but plain ASCII figures.

    Covers every spelling outside the grammar: a sign, a separator such
    as an underscore, a space anywhere in it, a figure from another
    writing system, and nothing at all. One message covers them all
    because the repair is one repair -- write it in plain figures -- and
    naming which of the five it was would tell the reader nothing they
    cannot see.
    """
    return (
        f"The seed has to be written in plain figures, and "
        f"'{_shown(given)}' is not. Please give a whole number from 0 to "
        f"{ceiling} with nothing else in it -- no plus or minus sign, no "
        f"spaces, no commas, no underscores -- for example --seed 0 or "
        f"--seed 12345. Leading zeros are fine and change nothing: 007 is "
        f"the seed 7. Nothing was written."
    )


def seed_too_large(given: str, ceiling: str) -> str:
    """Message for a seed above the largest one synthtwin accepts."""
    return (
        f"The seed {_shown(given)} is larger than the largest seed "
        f"synthtwin uses. Please give a whole number from 0 to {ceiling} "
        f"-- any of them builds a twin that follows the description just "
        f"as closely, so 0, 1 or 12345 will do. Nothing was written."
    )


def outputs_already_there(
    first: str, second: str, taken: "list[str]"
) -> str:
    """Message for a run whose output names are already in use.

    Both names are printed whichever of them is taken, and the one that
    is in the way is named again: a person who ran the command twice
    needs to see the pair the run would write, and a person whose own
    file is sitting at one of those names needs to see WHICH file is
    about to be replaced.

    There is no way to prove that a file at one of these names is an
    earlier twin of this run rather than somebody's own work (plan
    P2-D10, review item P2-R4-F1), so no such proof is attempted and no
    file is replaced without the person saying so. The cost is one word
    on a re-run, and this message teaches it.

    It is one paragraph, like every other message in this catalog: the
    command shows a refusal as a VALUE on its way to the screen, which
    means a line feed inside one is shown as text rather than obeyed, so
    a message that laid its paths out in a column would reach the reader
    as one long line with the escapes in it.
    """
    listed = _listed(taken)
    one_only = len(taken) == 1
    is_are = "this one is" if one_only else "these are"
    it_them = "that file" if one_only else "those files"
    return (
        f"synthtwin stopped because something is already at one of the "
        f"names it would write. This run writes two files, {first} and "
        f"{second}, and {is_are} already there: {listed}. Nothing was "
        f"written and nothing was changed. If {it_them} can be replaced -- "
        f"the usual reason is building the twin again with a different "
        f"seed -- add --replace to the command. If not, move or rename "
        f"what is there, or give --out-dir a different folder to write "
        f"into, then run the command again."
    )

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

Imports here stay within the allowlist (plan D6.2): this module imports
only `parsing`, for that one function.
"""

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


def first_row_could_be_a_record(path: str, columns: int) -> str:
    """Message for a first row that could be names or could be data.

    The message deliberately quotes nothing from the row. If the row is
    a record, printing it would print somebody's data to the screen in
    order to ask a question about it.
    """
    return (
        f"synthtwin cannot tell whether the first row of {path} holds "
        f"the names of the {columns} columns or the first record of the "
        f"table. Each value in that row could be a value of its own "
        f"column: none of them stands out as a name, and at least one "
        f"has exactly the shape every other value in its column has. "
        f"Guessing would either drop a whole record from the "
        f"description or publish a record as if it were a set of column "
        f"names, so synthtwin stops instead. Please run the command "
        f"again with --first-row names if that row holds the column "
        f"names, or with --first-row data if it is the first record. "
        f"With --first-row data the columns are named column_1, "
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


def nothing_was_written(stubborn: list[str]) -> str:
    """Sentence confirming the folder is as it was before the run."""
    if not stubborn:
        return "Nothing was written: both files are as they were before."
    listed = _listed(stubborn)
    return (
        f"Nothing was written, but synthtwin could not clear up its own "
        f"working file(s) afterwards: {listed}. They hold no description "
        f"of your table and can be deleted."
    )


def rollback_failed(left: list[str]) -> str:
    """Sentence naming every file left behind when a rollback failed."""
    listed = _listed(left)
    return (
        f"synthtwin could not put things back as they were, so these "
        f"files are left: {listed}. Check each one before using it: the "
        f"description may be from this run or from an earlier one."
    )


def output_folder_missing(path: str) -> str:
    """Message for an output folder that does not exist."""
    return (
        f"The folder {path} does not exist, so synthtwin cannot write "
        f"the profile there. Create the folder first, or leave the "
        f"option out to write the profile next to your table."
    )


def output_not_writable(path: str, detail: str) -> str:
    """Message for an output location that could not be written."""
    return (
        f"The profile could not be written to {path} ({_shown(detail)}). "
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


def output_would_replace_the_table(path: str) -> str:
    """Message for an output target that IS the user's own table."""
    return (
        f"synthtwin stopped because writing the description would have "
        f"replaced your own table at {path}. That would have destroyed "
        f"the data you asked it to describe. This usually means a file "
        f"of the profile's name is a link pointing back at the table. "
        f"Remove that link, or use the option for a different output "
        f"folder, then run the command again. Nothing was written."
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

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

_ON_DISK_WORDS = {
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
    ON_DISK_NEW: "the new description this run produced",
    ON_DISK_SET_ASIDE: (
        "the description from before this run, which synthtwin moved "
        "here and could not move back"
    ),
    ON_DISK_WORKING: (
        "a working file synthtwin could not clear away; it holds text "
        "taken from your table"
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


def _stated(on_disk: "list[tuple[str, str]]") -> str:
    """One clause per name: the path, then what is at it now.

    Each pair is a path and one of the ON_DISK_ codes above. A code
    this module does not recognize is reported as unknown rather than
    dropped: a message about what is on disk must never quietly leave a
    file out.
    """
    text = ""
    for path, code in on_disk:
        words = _UNKNOWN_STATE
        if code in _ON_DISK_WORDS:
            words = _ON_DISK_WORDS[code]
        piece = f"{_shown(path)} holds {words}"
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
) -> str:
    """Say what is on disk after a run that published no new description.

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
            f"No new description was published. This is what is at each "
            f"name now: {_stated(on_disk)}. {tail}"
        )
    if stubborn:
        listed = _listed(stubborn)
        return (
            f"No new description was published, and synthtwin could not "
            f"clear away its own working file(s): {listed}. Check each "
            f"one -- a working file can hold text taken from your table "
            f"-- and delete it when you have."
        )
    return (
        "No new description was published. synthtwin did not check the "
        "two output names afterwards, so please look at each one before "
        "you use it."
    )


def rollback_failed(
    left: list[str],
    on_disk: "list[tuple[str, str]] | None" = None,
) -> str:
    """Say what is on disk after a run that could not undo its own work.

    The two parameters mean exactly what they mean in
    ``nothing_was_written``. This wording is for the case where the
    files on disk no longer match what was there before the run and
    synthtwin could not put them back -- so it names each one and says
    which run its contents came from.
    """
    if on_disk:
        return (
            f"synthtwin could not put things back as they were. This is "
            f"what is at each name now: {_stated(on_disk)}. Check each "
            f"one before you use it, and finish by hand what synthtwin "
            f"could not: a profile and a summary from two different runs "
            f"do not describe the same table."
        )
    listed = _listed(left)
    return (
        f"synthtwin could not put things back as they were, so these "
        f"files are left: {listed}. Check each one before using it: it "
        f"may hold the description from this run or from an earlier one."
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

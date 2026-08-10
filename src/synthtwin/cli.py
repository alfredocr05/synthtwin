"""The `synthtwin` command (plan P1-D3 and P1-D7).

Phase 1 gives the command one real job: `synthtwin profile <table>`
reads a local CSV file and writes two files beside it -- the profile,
which is what the twin will be built from, and a plain-language summary
of what was found and what left the table.

Zero-code use is the requirement (charter principle 2): the command
works with a path and nothing else. Everything else is an option with a
sensible default, and every message, including every refusal, is
written for a person who has never programmed.

THE DISPLAY BOUNDARY. A path or a value can carry an escape sequence,
and a terminal obeys one instead of printing it: a path containing the
bytes for ESC [ 2 J cleared the screen from a refusal message (review
item P1-R6-F11, carried from P1-R4-F4). Escaping at each sink as it was
noticed did not hold, twice, because the next sink was written without
it. So the escaping happens where the text is EMITTED, not where it is
composed:

* `_say` and `_warn` are the only two places in this module that print
  anything at all, and both put what they are given through
  `parsing.visible_lines` first. A sink added later that prints through
  either of them is covered without its author doing anything;
  `tests/test_p1r6f11_display_boundary.py` reads this file and turns
  red if a `print` appears anywhere else.
* `_shown` covers one VALUE -- a path, a name, or a whole message some
  other module built -- and shows the line feed as well, so a value
  cannot forge a line that reads as though synthtwin wrote it. Every
  path this module puts into a message goes through it.
* The command line itself is parsed with `parse_known_args`, so that
  words synthtwin does not understand are refused through `_warn` in
  its own words. argparse's remaining messages quote the value with
  Python's `repr`, which shows control characters as text of its own
  accord.

Imports here are restricted to the exact allowlist in the plan (D6.2,
with the Phase 1 additions in P1-D10); the offline-static scanner
enforces the list in CI.
"""

import argparse
import dataclasses
import importlib.metadata
import pathlib
import sys

from synthtwin import errors, parsing, profile, reading, summary, taxonomy
from synthtwin.paths import PathValidationError, validate_local_path
from synthtwin.reading import read_table

_REPO_URL = "https://github.com/alfredocr05/synthtwin"

_STATUS = """synthtwin {version}

Status: early. `synthtwin profile <your-table.csv>` reads a CSV table on
this computer and writes a description of it -- what each column holds,
how its values are spread, and what is missing. Building the synthetic
twin from that description is the next phase.

Everything runs on this computer. synthtwin never sends anything
anywhere, and it accepts only plain paths to local files.

Project home: {repo}
"""

_HELP_EPILOG = """examples:
  synthtwin profile data.csv
      describe data.csv and write data-profile.json and
      data-profile.txt beside it

  synthtwin profile data.csv --out-dir reports
      write the two files into the folder 'reports' instead

  synthtwin profile data.csv --keep-value NA
      treat NA as real data in every column, not as a missing value

  synthtwin profile data.csv --missing-value -1
      treat -1 as a missing value in every column, not as a number
"""


def _shown(value: object) -> str:
    """One value, safe to put into a message.

    Anything synthtwin did not write itself: a path the user typed, a
    name, or a whole message another module built. Every display
    control is shown as text, the line feed included -- a value is not
    layout, and a line feed inside one forges a line that reads as
    though synthtwin wrote it. Messages in the refusal catalog are one
    paragraph each, so nothing of synthtwin's own is lost.
    """
    return parsing.visible(f"{value}")


def _say(message: str) -> None:
    """Print one message to the screen, through the display boundary.

    One of the two places in this module that print. Whatever it is
    given goes through `parsing.visible_lines` first, so a value that
    reached here without being shown safely still cannot instruct the
    terminal. Line breaks are kept: they are synthtwin's own layout.
    """
    print(parsing.visible_lines(f"{message}"))


def _warn(message: str) -> None:
    """Print one refusal or caution to the error stream, likewise.

    The second and last place in this module that print. Same boundary,
    same reason; only the stream differs.
    """
    print(parsing.visible_lines(f"{message}"), file=sys.stderr)


def _refuse_the_command_line(reason: str) -> None:
    """Say why the command line could not be used, then stop with code 2.

    Used instead of argparse's own refusal so that the words reach the
    screen through `_warn` like every other message, and so that the
    reader is told what to do next rather than shown a usage line.
    """
    _warn(reason)
    _warn("Run  synthtwin --help  to see how the command is used.")
    sys.exit(2)


def _version() -> str:
    try:
        return importlib.metadata.version("synthtwin")
    except Exception:  # noqa: BLE001 -- the import allowlist (plan
        # D6.2) permits only importlib.metadata.version, so the
        # specific PackageNotFoundError name cannot be referenced.
        # Running from an uninstalled source tree: metadata is absent.
        return "0+unknown (package not installed; run `pip install -e .`)"


def _encoding_note(encoding: str, used_fallback: bool) -> str:
    """One sentence about how the file was read."""
    if used_fallback:
        return (
            "It was not readable as UTF-8, so it was read as Western "
            "European text (Latin-1); if any accented letter looks wrong "
            "in this summary, save the file as 'CSV UTF-8' and run the "
            "command again."
        )
    return f"It was read as UTF-8 text (encoding: {encoding})."


def _left_behind_note(left: "list[str]") -> str:
    """The caution for working files a finished run could not clear away.

    `profile.write_both_files` hands back every working file still on
    disk when everything else succeeded, so that the caller can say so.
    Throwing that list away -- as this module did until review item
    P1-R6-F5 -- told the reader the run had gone perfectly while a file
    synthtwin had made, holding text computed from the real table, sat
    in the output folder under a name nobody had been given.

    This is not a failure of the profile and is not reported as one: the
    two output files are written and correct, the exit code stays 0, and
    the one thing asked of the reader is to look at a named file and
    delete it.

    Every path is put through `_shown` before it reaches the sentence,
    like every other path this module prints.
    """
    listed = ""
    for path in left:
        listed = f"{listed}\n  {_shown(path)}"
    one_only = len(left) == 1
    which = "this one" if one_only else "these"
    them = "it" if one_only else "them"
    return (
        f"\nSomething to tidy up by hand. Both files above were written "
        f"and are complete -- nothing is wrong with your profile. "
        f"synthtwin makes itself a working file beside each output "
        f"while it writes, and removes it at the end; {which} could not "
        f"be removed:{listed}\n"
        f"A working file can hold a description computed from your real "
        f"table, so keep {them} under the same rules as the table "
        f"itself, and delete {them} once you have looked."
    )


@dataclasses.dataclass(frozen=True)
class _Options:
    """What the user asked for, read off the command line."""

    version: bool
    command: "str | None"
    table: "str | None"
    out_dir: "str | None"
    smallest_group: int
    identifiers: list[str]
    kept_values: list[str]
    missing_values: list[str]
    first_row: str


def _parse_arguments(argv: "list[str] | None") -> _Options:
    """Build the command line and read it; return the options.

    The command word is an ordinary argument rather than a subcommand.
    That keeps one help screen for the whole tool -- which is what a
    reader who has never used a command line needs -- and it keeps the
    parser object inside this one function, which is what the offline
    policy accepts (plan D6.2: a value an allowlisted API produced may
    be used where it was made).

    Anything the parser does not recognize is taken back here and
    refused through this module's display boundary, with exit code 2 as
    before. argparse's own report of unrecognized words copies them to
    the error stream exactly as typed, and a word can carry an escape
    sequence a terminal obeys (review item P1-R6-F11).
    """
    parser = argparse.ArgumentParser(
        prog="synthtwin",
        description=(
            "Create a synthetic twin of your tabular data: same shape, "
            "same statistics, no real records."
        ),
        epilog=_HELP_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version", action="store_true", help="print the version and exit"
    )
    parser.add_argument(
        "command",
        nargs="?",
        default=None,
        choices=["profile"],
        help="what to do: 'profile' describes a CSV table on this computer",
    )
    parser.add_argument(
        "table",
        nargs="?",
        default=None,
        help="the path of the CSV file to describe",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        metavar="FOLDER",
        help=(
            "folder to write the two files into (the default is the "
            "folder the table is in)"
        ),
    )
    parser.add_argument(
        "--smallest-group",
        type=int,
        default=taxonomy.Settings().small_cell_floor,
        metavar="ROWS",
        help=(
            "advanced: a value shared by fewer rows than this is left out "
            "of the profile, so that a rare value cannot identify anybody "
            "(default: %(default)s)"
        ),
    )
    parser.add_argument(
        "--identifier",
        action="append",
        default=None,
        metavar="COLUMN",
        help=(
            "name a column that holds record numbers or codes rather than "
            "measurements, so that none of its values are published. "
            "Naming it here is the ONLY way a column is given that "
            "treatment: synthtwin never decides it from the values, "
            "because a column of codes and a column of measurements can "
            "look identical. Any column you name is covered, whatever its "
            "values look like and whatever synthtwin would otherwise have "
            "made of it -- so name an ID column, never a measurement. May "
            "be given more than once"
        ),
    )
    parser.add_argument(
        "--keep-value",
        action="append",
        default=None,
        metavar="VALUE",
        help=(
            "a value that is real data in your table, even though "
            "synthtwin would otherwise read it as 'no value'. Use it when "
            "a code such as NA is a genuine answer -- a region really "
            "called NA, or -999 as a real reading. A value that reads as "
            "a number is matched as a NUMBER, so -999 also covers "
            "-999.00; anything else is matched as text, ignoring "
            "surrounding spaces and upper or lower case. The profile "
            "records how many values you named and the rule that "
            "matched them, never the values themselves -- but a value "
            "you name this way IS data from then on, so it can appear "
            "wherever its column publishes values, for instance as that "
            "column's smallest number. May be given more than once"
        ),
    )
    parser.add_argument(
        "--missing-value",
        action="append",
        default=None,
        metavar="VALUE",
        help=(
            "a value that means 'no value' in your table, even though "
            "synthtwin would otherwise treat it as data -- for example a "
            "column where 'unknown' or -1 was typed for a reading nobody "
            "took. It is matched the same way as --keep-value, and the "
            "rows holding it are counted as missing rather than "
            "described. The profile records how many values you named "
            "and the rule that matched them, never the values "
            "themselves -- but the column still lists the spellings it "
            "counted as missing, on the same rules as any other missing "
            "spelling. May be given more than once"
        ),
    )
    parser.add_argument(
        "--first-row",
        default=reading.FIRST_ROW_AUTOMATIC,
        choices=[
            reading.FIRST_ROW_AUTOMATIC,
            reading.FIRST_ROW_NAMES,
            reading.FIRST_ROW_DATA,
        ],
        help=(
            "what the first row of the file is: 'names' for the column "
            "names, 'data' if the table has no column names and the "
            "first row is already a record (the columns are then named "
            "column_1, column_2, and so on). Either of those settles the "
            "question, whatever the file's own values look like. The "
            "default reads the first row as the column names, which is "
            "what a CSV file normally holds; when nothing in the file "
            "settles it, the summary says the names were taken by that "
            "convention and how to take it back, and when the file does "
            "show the first row to be a record rather than names, "
            "synthtwin stops and asks instead of choosing"
        ),
    )
    # parse_known_args rather than parse_args: argparse's own report of
    # words it did not recognize copies them to the error stream exactly
    # as typed, so a word carrying an escape sequence would instruct the
    # terminal from inside argparse, where this module's display
    # boundary cannot reach it (review item P1-R6-F11). Taking the
    # leftovers back lets the refusal go through `_warn` like every
    # other message -- and say something a non-programmer can act on.
    args, not_understood = parser.parse_known_args(argv)
    if not_understood:
        listed = ""
        for word in not_understood:
            shown = _shown(word)
            listed = shown if not listed else f"{listed}, {shown}"
        _refuse_the_command_line(
            f"This part of what you typed was not understood: {listed}. "
            f"synthtwin describes one CSV file at a time, so the command "
            f"is  synthtwin profile my-table.csv  and nothing else. If "
            f"the path has a space in it, put quotation marks around the "
            f"whole path."
        )
    if args.command == "profile" and args.table is None:
        _refuse_the_command_line(
            "Please say which file to describe, for example: "
            "synthtwin profile my-table.csv"
        )
    named = args.identifier if args.identifier is not None else []
    kept = args.keep_value if args.keep_value is not None else []
    declared_missing = (
        args.missing_value if args.missing_value is not None else []
    )
    return _Options(
        version=bool(args.version),
        command=args.command,
        table=args.table,
        out_dir=args.out_dir,
        smallest_group=int(args.smallest_group),
        identifiers=list(named),
        kept_values=list(kept),
        missing_values=list(declared_missing),
        first_row=f"{args.first_row}",
    )


def _run_profile(
    table: str,
    out_dir: "str | None",
    smallest_group: int,
    forced_identifiers: list[str],
    kept_values: list[str],
    missing_values: list[str],
    first_row: str,
) -> int:
    """Do the work of `synthtwin profile`; return the exit code.

    The order of operations is a control, not a convenience, and review
    round 1 found it inverted. Nothing is written until every target has
    passed the locality gate and been shown to be writable, and the
    disclosure of what the profile carries is printed BEFORE the files
    exist -- which is what plan P1-D6 says and what a person moving
    real-derived material needs.

    A pair of declarations that contradict each other is refused here,
    before the table is opened: `--keep-value -999 --missing-value -999`
    asks for two opposite things about one value, and picking one of
    them would be synthtwin deciding something the person did not
    (review item P1-R6-F9).
    """
    if smallest_group < 1:
        _warn(errors.floor_not_positive(f"{smallest_group}"))
        return 2
    clashes = taxonomy.contradictory_declarations(
        tuple(kept_values), tuple(missing_values)
    )
    if clashes:
        _warn(
            f"These two options contradict each other: "
            f"{_shown(clashes[0])}. A value is either data or it is 'no "
            f"value'; it cannot be both, and synthtwin will not choose "
            f"for you. Decide which one you meant, remove the other, and "
            f"run the command again. Nothing was written."
        )
        return 2
    settings = taxonomy.Settings(
        small_cell_floor=smallest_group,
        kept_values=tuple(kept_values),
        declared_missing_values=tuple(missing_values),
    )
    read = read_table(table, first_row)

    # An option naming a column that is not there is refused here, with
    # nothing built and nothing written. Warning about it afterwards --
    # as this did until round 1 -- means the profile of a column the
    # user meant to suppress has already been written to disk.
    unknown = [
        name for name in forced_identifiers if name not in read.column_names
    ]
    if unknown:
        _warn(
            errors.unknown_column_named(
                "holding record numbers", unknown[0], read.column_names
            )
        )
        return 2

    document = profile.build_document(read, settings, forced_identifiers)
    # The summary crosses the boundary ONCE, here, and the same text is
    # what reaches the screen and what is written to disk. The two
    # cannot differ, and the file on disk carries the same guarantee the
    # screen does -- it is opened in an editor or a terminal by the same
    # person, so it is a human-facing sink like any other.
    text = parsing.visible_lines(
        summary.render(
            document, _encoding_note(read.encoding, read.used_fallback_encoding)
        )
    )
    profile_path, summary_path = profile.default_output_paths(
        pathlib.Path(table), out_dir
    )
    # The output must never be the table itself. On POSIX a link left at
    # the profile's name resolves to a permitted local path, so the
    # locality gate cannot catch this one: it is the user's own data
    # that would be destroyed, and for this audience that is the worst
    # outcome the tool has.
    source = validate_local_path(table, purpose="input")
    if (
        profile_path == source
        or summary_path == source
        or profile.is_the_same_file(profile_path, source)
        or profile.is_the_same_file(summary_path, source)
    ):
        _warn(errors.output_would_replace_the_table(_shown(source)))
        return 1

    shown_profile_path = _shown(profile_path)
    shown_summary_path = _shown(summary_path)
    _say(text)
    _say(
        f"These two files will be written:\n"
        f"  {shown_profile_path}\n  {shown_summary_path}"
    )
    _say(
        "\nBoth are computed from your real data. Keep them under the "
        "same rules your institution applies to the table itself, and "
        "read the section above before moving them anywhere."
    )
    if smallest_group < taxonomy.Settings().small_cell_floor:
        _warn(
            f"\nWarning: you lowered the smallest group size to "
            f"{smallest_group}. Values shared by very few rows can point "
            f"back at the people they came from; the default of "
            f"{taxonomy.Settings().small_cell_floor} exists for that "
            f"reason."
        )

    # The return value is the point of the call, not an afterthought:
    # it is every working file still sitting in the output folder after
    # an otherwise complete run. Discarding it left a real-derived file
    # in the user's folder while the screen said the run had finished
    # cleanly (review item P1-R6-F5).
    #
    # The DiskState is the other half of the same promise, for the
    # failures the transaction cannot describe in its own words. It
    # composes a message for every refusal it foresees; for anything
    # else -- memory exhausted mid-write, a person pressing Ctrl-C -- it
    # cleans up, writes what is at each name into this record, and lets
    # the failure continue as itself so that the handler in `main` still
    # recognizes it and still gives its own advice. Both halves are
    # needed: one says what they are holding, the other says why it
    # stopped (review item P1-R7-F1).
    state = profile.DiskState()
    try:
        left_behind = profile.write_both_files(
            profile_path,
            summary_path,
            profile.serialize(document),
            text,
            state=state,
        )
    except BaseException:
        if state.sentence:
            _warn(_shown(state.sentence))
        raise
    _say(f"\nWritten:\n  {shown_profile_path}\n  {shown_summary_path}")
    if left_behind:
        # A caution, not a refusal. The profile is good, so the exit
        # code stays 0; the reader is simply told what to delete.
        _warn(_left_behind_note(left_behind))
    return 0


def main(argv: "list[str] | None" = None) -> int:
    """Run the `synthtwin` command.

    Guarantees:

    - Inputs: `argv` is the list of command-line arguments to parse, or
      `None` to parse `sys.argv[1:]`. Recognized: `--version`, `--help`,
      and the `profile` subcommand with its options.
    - Return codes: 0 when the work finished; 1 when the table could not
      be read or the profile could not be written, with a
      plain-language explanation on the error stream; 2 when an option's
      value was not usable, which includes naming one value both with
      `--keep-value` and with `--missing-value`. `SystemExit` with code
      2 still ends the run for a word on the command line that synthtwin
      does not recognize, and with code 0 for `--help`. 0 always means
      both files were written: a working file that could not be cleared
      away afterwards is named on the error stream as a caution and does
      not change the code, because nothing about the profile is wrong.
    - Determinism: the same table and the same options produce the same
      two files, byte for byte, on the same platform (plan D12 and
      P1-D11).
    - Errors raised: none that reach the user as a traceback. Every
      refusal in the catalog and every path rejection is caught here and
      printed as a message that says what happened and what to do next.
      Pressing Ctrl-C is the exception, and deliberately: it is the
      person stopping their own command, so it ends the command the way
      every other command on their computer ends, rather than being
      dressed up as a refusal synthtwin decided on. What it does not do
      any more is leave a working file behind in silence -- the write
      transaction clears up and names what is on disk first, whatever
      stopped it.
    - Boundary: the only file this command reads is the table the user
      named, through the path validator; the only files it writes are
      the two it reports at the end, plus working files of synthtwin's
      own making beside them, which are removed before the command
      returns -- and named on the error stream in the rare case that one
      could not be. No network, subprocess, native, or dynamic-code
      operation is performed anywhere in the package.
    - Display: nothing reaches the screen, the error stream, or the
      summary file without passing the display boundary described at the
      top of this module. A path or a value carrying an escape sequence
      is shown as text, never obeyed by the terminal.
    """
    options = _parse_arguments(argv)

    if options.version:
        _say(_version())
        return 0

    if options.command != "profile" or options.table is None:
        _say(_STATUS.format(version=_version(), repo=_REPO_URL))
        return 0

    table_named = options.table
    try:
        return _run_profile(
            options.table,
            options.out_dir,
            options.smallest_group,
            options.identifiers,
            options.kept_values,
            options.missing_values,
            options.first_row,
        )
    except PathValidationError as error:
        # The message is treated as a VALUE, not as something synthtwin
        # composed: it carries the path the user typed, and the builders
        # that place it there do not show it safely (review item
        # P1-R6-F11). Every message in the catalog is one paragraph, so
        # showing the line feed too costs nothing and closes the last
        # way a path can forge a line of its own.
        _warn(_shown(error))
        return 1
    except errors.ProfileError as error:
        _warn(_shown(error))
        return 1
    except MemoryError:
        # Reading is not the only step that can exhaust memory: building
        # the description and rendering it allocate again. One refusal
        # covers them all rather than a traceback reaching the user.
        _warn(errors.out_of_memory_while_describing(_shown(table_named)))
        return 1


if __name__ == "__main__":
    sys.exit(main())

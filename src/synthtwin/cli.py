"""The `synthtwin` command (plan P1-D3 and P1-D7).

Phase 1 gives the command one real job: `synthtwin profile <table>`
reads a local CSV file and writes two files beside it -- the profile,
which is what the twin will be built from, and a plain-language summary
of what was found and what left the table.

Zero-code use is the requirement (charter principle 2): the command
works with a path and nothing else. Everything else is an option with a
sensible default, and every message, including every refusal, is
written for a person who has never programmed.

Imports here are restricted to the exact allowlist in the plan (D6.2,
with the Phase 1 additions in P1-D10); the offline-static scanner
enforces the list in CI.
"""

import argparse
import dataclasses
import importlib.metadata
import pathlib
import sys

from synthtwin import errors, profile, reading, summary, taxonomy
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
"""


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


@dataclasses.dataclass(frozen=True)
class _Options:
    """What the user asked for, read off the command line."""

    version: bool
    command: "str | None"
    table: "str | None"
    out_dir: "str | None"
    smallest_group: int
    identifiers: list[str]
    first_row: str


def _parse_arguments(argv: "list[str] | None") -> _Options:
    """Build the command line and read it; return the options.

    The command word is an ordinary argument rather than a subcommand.
    That keeps one help screen for the whole tool -- which is what a
    reader who has never used a command line needs -- and it keeps the
    parser object inside this one function, which is what the offline
    policy accepts (plan D6.2: a value an allowlisted API produced may
    be used where it was made).
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
            "advanced: name a column that holds record numbers rather "
            "than measurements, so that none of its values are "
            "published; may be given more than once"
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
            "column_1, column_2, and so on). The default works out "
            "which it is, and stops to ask when it cannot tell"
        ),
    )
    args = parser.parse_args(argv)
    if args.command == "profile" and args.table is None:
        parser.error(
            "please say which file to describe, for example: "
            "synthtwin profile my-table.csv"
        )
    named = args.identifier if args.identifier is not None else []
    return _Options(
        version=bool(args.version),
        command=args.command,
        table=args.table,
        out_dir=args.out_dir,
        smallest_group=int(args.smallest_group),
        identifiers=list(named),
        first_row=f"{args.first_row}",
    )


def _run_profile(
    table: str,
    out_dir: "str | None",
    smallest_group: int,
    forced_identifiers: list[str],
    first_row: str,
) -> int:
    """Do the work of `synthtwin profile`; return the exit code.

    The order of operations is a control, not a convenience, and review
    round 1 found it inverted. Nothing is written until every target has
    passed the locality gate and been shown to be writable, and the
    disclosure of what the profile carries is printed BEFORE the files
    exist -- which is what plan P1-D6 says and what a person moving
    real-derived material needs.
    """
    if smallest_group < 1:
        print(errors.floor_not_positive(f"{smallest_group}"), file=sys.stderr)
        return 2
    settings = taxonomy.Settings(small_cell_floor=smallest_group)
    read = read_table(table, first_row)

    # An option naming a column that is not there is refused here, with
    # nothing built and nothing written. Warning about it afterwards --
    # as this did until round 1 -- means the profile of a column the
    # user meant to suppress has already been written to disk.
    unknown = [
        name for name in forced_identifiers if name not in read.column_names
    ]
    if unknown:
        print(
            errors.unknown_column_named(
                "holding record numbers", unknown[0], read.column_names
            ),
            file=sys.stderr,
        )
        return 2

    document = profile.build_document(read, settings, forced_identifiers)
    text = summary.render(
        document, _encoding_note(read.encoding, read.used_fallback_encoding)
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
        print(
            errors.output_would_replace_the_table(f"{source}"),
            file=sys.stderr,
        )
        return 1

    print(text)
    print(f"These two files will be written:\n  {profile_path}\n  {summary_path}")
    print(
        "\nBoth are computed from your real data. Keep them under the "
        "same rules your institution applies to the table itself, and "
        "read the section above before moving them anywhere."
    )
    if smallest_group < taxonomy.Settings().small_cell_floor:
        print(
            f"\nWarning: you lowered the smallest group size to "
            f"{smallest_group}. Values shared by very few rows can point "
            f"back at the people they came from; the default of "
            f"{taxonomy.Settings().small_cell_floor} exists for that "
            f"reason.",
            file=sys.stderr,
        )

    profile.write_both_files(
        profile_path, summary_path, profile.serialize(document), text
    )
    print(f"\nWritten:\n  {profile_path}\n  {summary_path}")
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
      value was not usable. argparse still raises `SystemExit` with code
      2 for an unrecognized argument and 0 for `--help`.
    - Determinism: the same table and the same options produce the same
      two files, byte for byte, on the same platform (plan D12 and
      P1-D11).
    - Errors raised: none that reach the user as a traceback. Every
      refusal in the catalog and every path rejection is caught here and
      printed as a message that says what happened and what to do next.
    - Boundary: the only file this command reads is the table the user
      named, through the path validator; the only files it writes are
      the two it reports at the end. No network, subprocess, native, or
      dynamic-code operation is performed anywhere in the package.
    """
    options = _parse_arguments(argv)

    if options.version:
        print(_version())
        return 0

    if options.command != "profile" or options.table is None:
        print(_STATUS.format(version=_version(), repo=_REPO_URL))
        return 0

    table_named = options.table
    try:
        return _run_profile(
            options.table,
            options.out_dir,
            options.smallest_group,
            options.identifiers,
            options.first_row,
        )
    except PathValidationError as error:
        print(f"{error}", file=sys.stderr)
        return 1
    except errors.ProfileError as error:
        print(f"{error}", file=sys.stderr)
        return 1
    except MemoryError:
        # Reading is not the only step that can exhaust memory: building
        # the description and rendering it allocate again. One refusal
        # covers them all rather than a traceback reaching the user.
        print(errors.out_of_memory_while_describing(table_named), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""The `synthtwin` command (plan P1-D3, P1-D7, P2-D10 and P3-D1).

Three commands share one command line. `synthtwin profile <table>` reads
a local CSV file and writes two files beside it -- the profile, which is
what the twin is built from, and a plain-language summary of what was
found and what left the table. `synthtwin generate <profile>` reads that
profile and writes two more -- the twin table, and a report saying what
the twin carries, what it only approximates, and what it does not carry
at all. `synthtwin validate <profile>` reads that profile and one CSV
file, measures the file against it, and writes the quality report: which
obligations the file met, which it missed, and which no CSV could ever
evidence either way.

Zero-code use is the requirement (charter principle 2): each command
works with one path and nothing else. Everything else is an option with
a sensible default, and every message, including every refusal, is
written for a person who has never programmed.

WHY EACH COMMAND'S MODULES ARE IMPORTED INSIDE ITS OWN BRANCH (plan
P2-D1, extended by P3-D1). The generator never reads the real table, and
that promise is kept by the import graph rather than by anybody's care:
`reading` is the only module that opens a table, and a `generate` run has
to be free of it at EVERY instant, not merely after the dispatch. Python
runs a module's top-level imports before any branch of it exists, so
importing this module used to start the table reader -- and pandas
underneath it -- whatever the person had typed, which put module
initialization outside any boundary a check could draw. The profiler's
modules are therefore imported inside `_run_profile`, the generator's
inside `_run_generate`, the validator's inside `_run_validate`, and what
is left at the top of this file reaches none of them: `errors` and
`parsing` import nothing outside this package, and `paths` imports os,
pathlib, sys and typing.

THE VALIDATE BRANCH IS FENCED FROM BOTH SIDES, and only one side of that
fence is the reader's. It DOES import the reader, because measuring a
file means describing that file with the profiler's own producer, which
is the only way the recount is the same measurement the description was
made with. What it does NOT import is the generator: a check that called
the planner would inherit every planning defect of the thing it is
checking, which is the one thing a second opinion may not do, and the
generator is where this package's only random number generator lives, so
importing it would put THIS PACKAGE's random source in the reach of a
command whose bytes must be a fixed function of its two files. (Another
one is already in the process, and it is honest to say so here: the
reader needs pandas, pandas imports numpy, and numpy brings
`numpy.random` with it. What the validate path does with it is nothing
-- amendment A-P3-4.) That is also why the quality report is rendered by
`quality` rather than by `rendering`:
`rendering` imports the generator, so a validate run that reached it
would cross both of those lines at once.

One consequence of that rule looks like an oversight and is not. The
parser's own vocabulary -- the three choices for `--first-row`, the
default smallest group -- is written out below as constants instead of
being read off `reading` and `taxonomy`, because the parser is built
BEFORE any command word has been read: it may not start the reader, and
`taxonomy` belongs to the `profile` branch. The suite checks each
constant against the module that owns the value, so the two cannot
drift apart in silence.

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

from synthtwin import errors, parsing
from synthtwin.paths import PathValidationError, validate_local_path

_REPO_URL = "https://github.com/alfredocr05/synthtwin"

# THE PARSER'S OWN VOCABULARY, written out here for the reason the module
# docstring gives: the command line is built before any command word has
# been read, so it may not start the table reader (plan P2-D1) and may
# not reach into the `profile` branch's taxonomy. Each of these is the
# same value the module that owns it holds, and the suite compares them
# so a change in one place cannot pass unnoticed in the other.
_FIRST_ROW_AUTOMATIC = "auto"
_FIRST_ROW_NAMES = "names"
_FIRST_ROW_DATA = "data"
_SMALLEST_GROUP = 11

# THE HELP FOR `--missing-value`, HELD AS A CONSTANT BECAUSE IT IS A
# CONTROL (review item P3-V9-F1, plan amendment A-P3-31). This is the
# screen a person reads BEFORE deciding what to type after the option,
# and the thing they most need to know from it is that the word itself
# is written into the description. It leads with that, ahead of every
# rule about the settings block, because a researcher weighing whether
# to name a diagnosis code has to meet the exposure first and the
# bounds second. It stands out here rather than inside the parser so
# that `tests/test_p3v9f1_declared_words_disclosed.py` can put the
# pre-repair wording back and prove the assertion on it can fail.
_MISSING_VALUE_HELP = (
    "a value that means 'no value' in your table, even though "
    "synthtwin would otherwise treat it as data -- for example a "
    "column where 'unknown' or -1 was typed for a reading nobody "
    "took. It is matched the same way as --keep-value, and the "
    "rows holding it are counted as missing rather than "
    "described. READ THIS BEFORE YOU TYPE A WORD HERE: the word "
    "itself is written into the description, spelled exactly as "
    "your table spells it, in the block describing each column "
    f"where at least {_SMALLEST_GROUP} rows hold it and that "
    "column publishes any values at all -- so a diagnosis, a "
    "code or an identifier named here travels in the description "
    "and in the summary beside it. Below that many rows the "
    "cells are counted without the word being named, and a "
    "column that publishes no values at all -- record numbers, "
    "free text -- names no spelling either way. In the settings "
    "block the profile also records how many different values you "
    "named, the rule that matched them, and -- where what you "
    "named is one of synthtwin's own words for 'no value' -- which "
    "of those words it was; a word of your own is never written "
    "into the settings block, which is a rule about that block and "
    "not about the columns. May be given more than once"
)

# The three commands, as the words a person types.
_PROFILE = "profile"
_GENERATE = "generate"
_VALIDATE = "validate"

# THE SEED'S ACCEPTED SPELLING AND RANGE (plan P2-D8). synthtwin states
# its own range rather than passing whatever was typed to the library
# underneath: that library accepts a wider set, and refuses a negative
# number with a sentence about bit widths that no researcher should ever
# be shown. The accepted spelling is one or more of these ten figures and
# nothing else -- no sign, no separator, no space anywhere, no figure
# from another writing system -- and leading zeros are accepted and
# change nothing.
_FIGURES = "0123456789"
_SEED_CEILING = "18446744073709551615"

# The two files `generate` writes, as endings added to the description's
# own name once a trailing '-profile' has been taken off it (plan
# P2-D10). Neither can collide with the profiler's own pair: those end
# '-profile.json' and '-profile.txt'.
_PROFILE_MARK = "-profile"
_TWIN_SUFFIX = "-twin.csv"
_REPORT_SUFFIX = "-twin-report.txt"

# And the one file `validate` writes -- added to the name of the file it
# MEASURED, not to the name of the description (plan P3-D1, amendment
# A-P3-4). It collides with none of the other four by construction:
# those end '-profile.json', '-profile.txt', '-twin.csv' and
# '-twin-report.txt'.
#
# WHY THE MEASURED FILE AND NOT THE DESCRIPTION (review item P3-V2-G).
# One description makes one twin, so naming the twin after the
# description binds them; but one description can be measured against
# ANY NUMBER of files, and naming the report after the description broke
# exactly that binding. `validate clinic-profile.json --twin
# tampered.csv` wrote `clinic-twin-quality.txt` -- a report named after
# the twin, beside the twin, about a different file. Checking a second
# candidate was then refused for a name clash that had nothing to do
# with what was measured, or with `--replace` silently replaced the
# first file's report under the first file's name.
#
# The ordinary run's name does not move: the default measured file is
# `<stem>-twin.csv`, so the report is still `<stem>-twin-quality.txt`
# and the command a finished `generate` teaches still writes the file it
# always wrote.
_QUALITY_SUFFIX = "-quality.txt"

_STATUS = """synthtwin {version}

Status: early. `synthtwin profile <your-table.csv>` reads a CSV table on
this computer and writes a description of it -- what each column holds,
how its values are spread, and what is missing. Then `synthtwin generate
<your-table-profile.json>` builds the synthetic twin from that
description and a seed, and from nothing else, and writes it beside a
report saying what the twin carries and what it does not. Then
`synthtwin validate <your-table-profile.json>` measures that twin
against the description and writes the quality report: which of the
description's obligations the file met, which it missed, and which
nothing written in a CSV could evidence either way.

What the twin does NOT carry, before anything else here claims more.
This version builds every column on its own and carries no cross-column
structure at all: nothing that links two columns of your table is in the
twin -- not a taller person weighing more, not a later date costing
more, not a code that only ever appears beside one region, not two
columns left empty in the same rows. Every row is built on its own too,
and the description never says what one row of your table is, so a table
holding several rows per person yields a twin that behaves differently
from your table under anything that groups rows. Your analysis code
RUNS on the twin, which is what the twin is for; a number it computes
from two columns of the twin means nothing about your table.
Cross-column structure arrives in a later version of synthtwin.

What that does and does not promise about your rows. The generator is
never handed your table, does not open one, and samples or copies no row
of it. That says where the twin's values come from. It does not say that
no row of the twin can equal a row of yours: the description publishes
exact counts, and meeting them exactly can force a twin row to match a
real one. A table of eleven rows with one column, whose single label all
eleven rows share, publishes that label with the count eleven -- so the
twin writes it in all eleven of its rows. synthtwin offers no formal
privacy guarantee.

All five files -- the profile, the plain-language summary beside it, the
twin, the twin's report and the quality report -- are computed from your
real data, so your institution's rules for real-derived material apply
to all five, not to the profile alone.

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

  synthtwin generate data-profile.json
      build the twin from that description and write data-twin.csv and
      data-twin-report.txt beside it

  synthtwin generate data-profile.json --seed 7
      build a different twin from the same description

  synthtwin generate data-profile.json --replace
      build it again over the two files an earlier run left there

  synthtwin validate data-profile.json
      measure data-twin.csv against that description and write
      data-twin-quality.txt beside it

  synthtwin validate data-profile.json --twin somewhere/other.csv
      measure that file instead of the twin beside the description,
      and write other-quality.txt: the report is named after the file
      it is about, so checking a second file never overwrites the
      first one's report
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


def _left_behind_note(
    left: "list[str]", produced: str = "profile", one_output: bool = False
) -> str:
    """The caution for working files a finished run could not clear away.

    `writing.write_both_files` hands back every working file still on
    disk when everything else succeeded, so that the caller can say so.
    Throwing that list away -- as this module did until review item
    P1-R6-F5 -- told the reader the run had gone perfectly while a file
    synthtwin had made, holding text computed from the real table, sat
    in the output folder under a name nobody had been given.

    This is not a failure of the run and is not reported as one: the two
    output files are written and correct, the exit code stays 0, and the
    one thing asked of the reader is to look at a named file and delete
    it.

    ``produced`` is what the running command calls what it wrote -- the
    profile, the twin, or the quality report -- for the one sentence that
    names it. It defaults to the profiler's word, which is what keeps
    that command's caution the same text it has always been, and the
    other two commands pass their own: telling somebody that nothing is
    wrong with their profile after a run that never wrote one sends them
    to look at the wrong file (plan P2-D10).

    ``one_output`` says whether the run wrote one file or two, and it is
    a parameter rather than a guess because this sentence opens by
    telling the reader that what they came for is complete. "Both files
    above were written" is a false sentence in a `validate` run, which
    writes one, and a caution that opens with a false clause is a
    caution the reader stops trusting (plan P3-D1).

    Every path is put through `_shown` before it reaches the sentence,
    like every other path this module prints.
    """
    listed = ""
    for path in left:
        listed = f"{listed}\n  {_shown(path)}"
    one_only = len(left) == 1
    which = "this one" if one_only else "these"
    them = "it" if one_only else "them"
    written = "Both files above were written and are complete"
    if one_output:
        written = "The file above was written and is complete"
    return (
        f"\nSomething to tidy up by hand. {written} "
        f"-- nothing is wrong with your {produced}. "
        f"synthtwin makes itself a working file beside each output "
        f"while it writes, and removes it at the end; {which} could not "
        f"be removed:{listed}\n"
        f"A working file can hold text computed from your real data, so "
        f"keep {them} under the same rules as the table itself, and "
        f"delete {them} once you have looked."
    )


@dataclasses.dataclass(frozen=True)
class _Options:
    """What the user asked for, read off the command line.

    `given` is the one path the command word takes: the CSV table for
    `profile`, the description for `generate` and for `validate`. It is
    one field because it is one position on the command line, and
    calling it after any one command would make the others read as a
    mistake.

    `twin` is the second file `validate` reads, and it is a named option
    rather than a second position for the reason the whole command line
    is shaped that way: a person types one path, and every other file is
    worked out for them. Left out, the twin beside the description is
    what gets measured.

    `seed` is the text that was typed, not a number. Whether it is a
    number synthtwin can use is decided by `_seed_or_refusal` in words a
    person can act on, and letting the parser convert it would have let
    the library's own refusal reach the screen instead (plan P2-D8).
    """

    version: bool
    command: "str | None"
    given: "str | None"
    twin: "str | None"
    out_dir: "str | None"
    smallest_group: int
    identifiers: list[str]
    kept_values: list[str]
    missing_values: list[str]
    first_row: str
    day_first: bool
    seed: str
    replace: bool


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
            "and each column behaving like the same column of yours, "
            "worked out from a description of your table rather than "
            "from its rows. Every column is built on its own, so the "
            "twin carries no cross-column structure at all. Run "
            "synthtwin with no arguments for what that does and does "
            "not promise about your rows and about two columns "
            "together."
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
        choices=[_PROFILE, _GENERATE, _VALIDATE],
        help=(
            "what to do: 'profile' describes a CSV table on this "
            "computer, 'generate' builds the synthetic twin from a "
            "description 'profile' wrote, 'validate' measures a CSV "
            "file against that description and writes the quality "
            "report"
        ),
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help=(
            "the file to work on: the CSV table for 'profile', the "
            "description for 'generate' and for 'validate'"
        ),
    )
    parser.add_argument(
        "--twin",
        default=None,
        metavar="PATH",
        help=(
            "the CSV file for 'validate' to measure (the default is the "
            "twin beside the description, the file 'generate' wrote). "
            "synthtwin measures whatever file you name here: it has no "
            "way of telling a twin of its own from any other CSV, and "
            "the report says so. The report is named after this file "
            "and names it in its first lines, so checking a second file "
            "never writes over the first one's report. Used by "
            "'validate' only"
        ),
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        metavar="FOLDER",
        help=(
            "folder to write this command's own files into (the default "
            "is the folder the file you named is in)"
        ),
    )
    parser.add_argument(
        "--seed",
        default="0",
        metavar="NUMBER",
        help=(
            "which twin to build, as a whole number from 0 to "
            "18446744073709551615 written in figures (default: "
            "%(default)s). The same description, seed and version of "
            "synthtwin always give the same twin, byte for byte; a "
            "different seed gives a different twin that follows the "
            "description just as closely. Used by 'generate' only"
        ),
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help=(
            "let 'generate' write over the twin and the report an "
            "earlier run left at those names, and 'validate' over the "
            "quality report. Without it, a run that finds any of those "
            "names taken stops and changes nothing: synthtwin has no "
            "way of telling a file an earlier run of its own left there "
            "from a file of yours that happens to be there"
        ),
    )
    parser.add_argument(
        "--smallest-group",
        type=int,
        default=_SMALLEST_GROUP,
        metavar="ROWS",
        help=(
            "advanced: a value shared by fewer rows than this is left out "
            "of the profile, so that a rare value cannot identify anybody. "
            "A number below the default is accepted and the whole workflow "
            "then runs on it -- the profile names groups that small, prints "
            "how many rows each covers, and every file the run makes says on "
            "its face that it was built that way "
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
            "surrounding spaces and upper or lower case. In the settings "
            "block the profile records how many different values you "
            "named, the rule that matched them, and -- where what you "
            "named is one of synthtwin's own words for 'no value', such "
            "as NA or -999 -- which of "
            "those words it was; a word of your own is never written "
            "into the settings block, which is a rule about that block "
            "and not about the columns. And a value you name this way IS data "
            "from then on, so the word itself can appear wherever its "
            "column publishes values, for instance as that column's "
            "smallest number. May be given more than once"
        ),
    )
    parser.add_argument(
        "--missing-value",
        action="append",
        default=None,
        metavar="VALUE",
        help=_MISSING_VALUE_HELP,
    )
    parser.add_argument(
        "--day-first",
        action="store_true",
        help=(
            "say that dates written with slashes in this table are "
            "written day first, so 03/04/2024 is the 3rd of April. It "
            "is not a bare order swap: a column whose own values can "
            "only be read the other way round would then be read "
            "backwards and its evidence counted as unreadable. So both "
            "readings are counted for every such column, whichever "
            "parses more of that column's values is the one used, and "
            "this option decides only where the two parse exactly as "
            "many. Every column it touches says in its remarks which "
            "reading was used and why, and says so again where the "
            "column's own values point both ways at once"
        ),
    )
    parser.add_argument(
        "--first-row",
        default=_FIRST_ROW_AUTOMATIC,
        choices=[
            _FIRST_ROW_AUTOMATIC,
            _FIRST_ROW_NAMES,
            _FIRST_ROW_DATA,
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
            f"synthtwin works on one file at a time, so the command is "
            f"one of  synthtwin profile my-table.csv  ,  synthtwin "
            f"generate my-table-profile.json  and  synthtwin validate "
            f"my-table-profile.json  and nothing else. If the path has a "
            f"space in it, put quotation marks around the whole path."
        )
    if args.command == _PROFILE and args.path is None:
        _refuse_the_command_line(
            "Please say which file to describe, for example: "
            "synthtwin profile my-table.csv"
        )
    if args.command == _GENERATE and args.path is None:
        _refuse_the_command_line(
            "Please say which description to build the twin from, for "
            "example: synthtwin generate my-table-profile.json -- that "
            "is the file 'synthtwin profile' wrote."
        )
    if args.command == _VALIDATE and args.path is None:
        _refuse_the_command_line(
            "Please say which description to measure the file against, "
            "for example: synthtwin validate my-table-profile.json -- "
            "that is the file 'synthtwin profile' wrote. Add --twin and "
            "a path if the file to measure is not the twin beside it."
        )
    named = args.identifier if args.identifier is not None else []
    kept = args.keep_value if args.keep_value is not None else []
    declared_missing = (
        args.missing_value if args.missing_value is not None else []
    )
    return _Options(
        version=bool(args.version),
        command=args.command,
        given=args.path,
        twin=args.twin,
        out_dir=args.out_dir,
        smallest_group=int(args.smallest_group),
        identifiers=list(named),
        kept_values=list(kept),
        missing_values=list(declared_missing),
        first_row=f"{args.first_row}",
        day_first=bool(args.day_first),
        seed=f"{args.seed}",
        replace=bool(args.replace),
    )


# The loud rule the lowered-floor warning is wrapped in. It is not the
# `=` rule the reports use, on purpose: this is the one thing on the
# screen a person must not skim past, so it does not look like a section
# heading of the summary they have just read.
_ALARM = "!" * 66

# One extra line after the "Written:" confirmation on a lowered-floor
# run, so that the warning cannot be lost off the top of a terminal. It
# is a pointer rather than a second copy of the warning: repeating the
# whole block would teach people to scroll past both.
_LOWERED_FLOOR_REMINDER = (
    "These two files were written under a lowered smallest group size, "
    "and they name groups that small. The warning above says what that "
    "can reveal about a person. Read it before either file goes anywhere."
)


def _declared_words_notice(
    named: "list[tuple[str, str, int]]",
) -> str:
    """What the description kept of the words the person typed.

    Shown when a word of the person's OWN, named with `--missing-value`,
    reached the description -- which contract 5 section 3.2 way 4 makes
    the ordinary outcome rather than the corner case, and which nothing
    on any screen said until review item P3-V9-F1.

    IT IS IN THE LOWERED FLOOR'S REGISTER AND ITS PLACE, on purpose.
    Both are the same kind of fact: something a person did on the
    command line put real text into files they are about to be handed,
    and they have to weigh it BEFORE either file exists rather than
    discover it in a document a non-programmer does not open. So it is
    banded, it names the words and the columns, and it is printed
    before the write.

    IT IS CONDITIONAL, for the reason the lowered-floor block gives.
    Printing "no word of yours was kept" on every ordinary run is how a
    reader is trained to skip the paragraph that matters. The summary
    page states the RULE on every run where anything was declared and
    names the words on the run where there are any; this screen speaks
    only when there are.

    NOTHING NEW LEAVES THE MACHINE. Every word here is already printed
    on the summary this run has just shown, and already stored in the
    description beside it.

    IT COUNTS WORDS AND LISTS SPELLINGS, AND THOSE ARE TWO NUMBERS
    (review item P3-V10-F9; plan amendment A-P3-42 clause 5). The list
    it is handed has one entry per spelling per column, and it used to
    pluralise the whole notice off the LENGTH of that list -- so one
    `--missing-value XX` over a table holding eleven `XX` cells and
    eleven `" xx "` cells opened with "Words you typed after
    --missing-value are written into the description" and closed by
    telling the person to run again "without naming them". They named
    one word. Nothing was withheld and no spelling was wrong; the
    attribution was, and a person acting on it looks for a second option
    they never gave. The words are counted by
    `summary.words_behind`, which groups the spellings at the producer's
    own declaration identity, and every clause of this notice is now
    written from whichever of the two numbers it is actually about.

    Guarantees:

    - Inputs: the spellings the description names, each with its column
      and how many cells wore it, from `summary.words_of_your_own`.
    - Determinism: a fixed function of that list.
    - Errors raised: none.
    - Boundary: every spelling crosses the display boundary through
      `_shown` before it reaches the screen, exactly as the summary's
      own text does.
    """
    from synthtwin import summary

    listed = ""
    for spelling, column, count in named:
        listed = (
            f"{listed}\n  {_shown(spelling)} -- in the column "
            f"{_shown(column)}, {count} cell(s)"
        )
    one_spelling = len(named) == 1
    words = summary.words_behind(named)
    one_word = words == 1
    both = "" if len(named) == words else (
        f"\n\nWHY THERE ARE MORE LINES THAN WORDS. Your table wrote "
        f"{'the word you named' if one_word else 'some of the words you named'}"
        f" more than one way, and the description records each way "
        f"separately, because it has to say how each cell was spelled. "
        f"You typed {'one word' if one_word else f'{words} words'}; the "
        f"rest of what you see above is your table's own spelling."
    )
    return (
        f"\n{_ALARM}\n"
        f"READ THIS BEFORE EITHER OF THESE FILES GOES ANYWHERE.\n"
        f"{'A word' if one_word else f'{words} words'} you typed after "
        f"--missing-value {'is' if one_word else 'are'} written into the "
        f"description.\n"
        f"{_ALARM}\n"
        f"\n"
        f"WHAT IS IN THE FILES. The description names "
        f"{'this spelling' if one_spelling else 'these spellings'} "
        f"exactly as your table wrote "
        f"{'it' if one_spelling else 'them'}, and the plain-language "
        f"summary beside it prints "
        f"{'it' if one_spelling else 'them'} too:{listed}{both}\n"
        f"\n"
        f"WHY IT IS THERE. A description has to say how each cell was "
        f"read, or synthtwin cannot check your own table against it "
        f"later without reporting failures that are not real. Naming a "
        f"word as 'no value' does not withhold it: it moves those cells "
        f"out of the column's values and records the word that moved "
        f"them.\n"
        f"\n"
        f"WHAT TO DO. If "
        f"{'that spelling' if one_spelling else 'any of those spellings'}"
        f" is something you would not put in an email -- a diagnosis, a "
        f"code, anything that names a person -- then neither file may "
        f"leave your machine as it stands. Delete what this run writes "
        f"and describe the table again without naming "
        f"{'that word' if one_word else 'those words'}, or with the "
        f"cells already blank."
    )


def _lowered_floor_warning(given: int) -> str:
    """The warning shown when `--smallest-group` is under the default.

    Guarantees:

    - Inputs: the number the person typed, already known to be below
      `taxonomy.Settings().small_cell_floor` and at least 1.
    - Determinism: a fixed function of that number.
    - Errors raised: none.
    - Boundary: no value of the table reaches it. It names a count and
      nothing else.

    WHY IT IS THIS LONG (owner ruling 2026-08-14, plan amendment
    A-P3-11). The owner ruled that a floor below the default is let
    through everywhere, KNOWING what it costs, and ruled that the cost
    be made visible rather than softened. What it replaces said "values
    shared by very few rows can point back at the people they came
    from", which is true and tells a person nothing they can act on: it
    never says that the description prints the count itself, never says
    that one row may be one person, and never says the counts travel
    into the twin and all three reports. A warning a person cannot act
    on is the same defect as no warning.

    THE DEFAULT IS NAMED FROM THIS MODULE'S OWN MIRROR. `_SMALLEST_GROUP`
    is the value `taxonomy.Settings` holds, kept here because the command
    line is built before any command word is read (plan P2-D1), and the
    suite compares the two so they cannot drift.
    """
    # At a floor of one a published group can be a single row, which is
    # the whole of the disclosure said in one sentence -- so it is said,
    # rather than left inside "as few as 1 rows". It also replaces the
    # count sentence rather than standing beside it: "a group of 1 is 1
    # people" is not English, and a warning a person stumbles over is a
    # warning they stop reading.
    people = f"a group of {given} is {given} people. "
    if given < 2:
        people = (
            "a group of 1 is one person on their own, and the "
            "description says out loud that exactly one person in your "
            "table has that value. "
        )
    return (
        f"\n{_ALARM}\n"
        f"READ THIS BEFORE ANY OF THESE FILES GOES ANYWHERE.\n"
        f"You lowered the smallest group size to {given}. "
        f"It is normally {_SMALLEST_GROUP}.\n"
        f"{_ALARM}\n"
        f"\n"
        f"WHAT YOU CHANGED. synthtwin normally leaves a value out of "
        f"the description unless at least {_SMALLEST_GROUP} rows share "
        f"it. You told it {given}, so this description names values "
        f"that as few as {given} row(s) share, and prints how many rows "
        f"that is.\n"
        f"\n"
        f"WHAT A SMALL COUNT CAN REVEAL ABOUT A PERSON. If one row of "
        f"your table is one person, {people}"
        f"Somebody who already knows one true thing about someone in "
        f"your table -- that they are in it at all -- can find the "
        f"small group that person must be in and read off everything "
        f"else the description says about that group. Nothing has to be "
        f"broken into or decoded for that to happen: the count is the "
        f"disclosure, and the usual {_SMALLEST_GROUP} is the number "
        f"that keeps a published group too big to point at one person.\n"
        f"\n"
        f"WHERE THOSE COUNTS GO NEXT. Not into the description alone. "
        f"The twin is built to hold the published counts exactly, and "
        f"the plain-language summary beside the description, the twin's "
        f"report and the quality report all quote them back. All five "
        f"files of a full run carry them, and each of the four written "
        f"pages says on its own face that it was made this way.\n"
        f"\n"
        f"IF YOU DID NOT MEAN THIS, run the command again without "
        f"--smallest-group, or with a larger number, and delete what "
        f"this run writes."
    )


def _run_profile(
    table: str,
    out_dir: "str | None",
    smallest_group: int,
    forced_identifiers: list[str],
    kept_values: list[str],
    missing_values: list[str],
    first_row: str,
    day_first: bool,
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

    THE FOUR MODULES THIS COMMAND NEEDS ARE IMPORTED HERE, inside the
    branch, and the module docstring says why: `reading` is the module
    that opens the user's table and `profile` reaches it, so importing
    either at the top of this file would start the reader in a `generate`
    run that must never touch it (plan P2-D1). This is the only place in
    the package where the reader is reached from the command line.
    """
    from synthtwin import profile, reading, summary, taxonomy

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
        day_first=day_first,
    )
    read = reading.read_table(table, first_row)

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
    # BOTH WARNINGS GO HERE, before the write, for the one reason (plan
    # P1-D6): a person weighs what a file carries before it exists, not
    # after they have been told where it is. The declared-word notice is
    # printed first and the floor alarm last, because the floor alarm
    # has a reminder line of its own after the "Written:" confirmation
    # and reading the two in that order leaves the pointer beside the
    # block it points at.
    kept_of_yours = summary.words_of_your_own(document)
    if kept_of_yours:
        _warn(_declared_words_notice(kept_of_yours))
    if smallest_group < taxonomy.Settings().small_cell_floor:
        _warn(_lowered_floor_warning(smallest_group))

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
        elif state.both_files_written:
            # The other end of the same promise. Both renames finished
            # and then the run stopped -- a person pressing Ctrl-C in
            # that last instant -- so there is no failure of the write to
            # report and nothing to put back. Saying nothing would leave
            # them believing nothing was written while two complete
            # real-derived files sat in their folder, and would keep the
            # earlier profile's working name to ourselves (review item
            # P1-R8-F1). The transaction leaves no sentence in this case
            # precisely so that these words, the ones a finished run
            # uses, are what they read.
            _say(
                f"\nWritten:\n  {shown_profile_path}\n  {shown_summary_path}"
            )
            if state.left_behind:
                _warn(_left_behind_note([state.left_behind]))
        raise
    if left_behind:
        # A caution, not a refusal. The profile is good, so the exit
        # code stays 0; the reader is simply told what to delete.
        #
        # This goes out BEFORE the "Written:" confirmation on purpose.
        # Both are ordinary prints and a stop can land between them; if
        # only one of the two reaches the person, it must be the one
        # naming a file that may hold text taken from their table, not
        # the one confirming what already went well.
        _warn(_left_behind_note(left_behind))
    _say(f"\nWritten:\n  {shown_profile_path}\n  {shown_summary_path}")
    if smallest_group < taxonomy.Settings().small_cell_floor:
        _warn(f"\n{_LOWERED_FLOOR_REMINDER}")
    return 0


# -- building the twin (plan P2-D10) ----------------------------------


def _without_leading_zeros(figures: str) -> str:
    """``figures`` with its leading zeros dropped, keeping one figure.

    '007' is the seed 7 and '000' is the seed 0, so the last figure is
    never dropped. Nothing here converts anything to a number: the point
    of doing it as text is that the length of what is left is what says
    whether the number is too large to read at all.
    """
    start = 0
    while start < len(figures) - 1 and figures[start] == "0":
        start = start + 1
    return figures[start:]


def _seed_or_refusal(given: str) -> "tuple[int | None, str]":
    """The seed the person typed, or the sentence saying why it cannot be.

    Guarantees:

    - Inputs: the text typed after `--seed`, exactly as it arrived. It
      is text and not a number on purpose: converting it in the parser
      would have let the library's own refusal reach the screen, and
      that refusal names a bit width and a data type (plan P2-D8).
    - Determinism: a fixed function of that text.
    - Errors raised: none. A seed nobody can use comes back as a pair
      whose first item is nothing and whose second is the message for
      the person, so the caller decides what the exit code is.
    - Boundary: nothing is read and nothing is written.

    The accepted spelling is one or more ASCII figures and nothing else:
    no sign, no separator, no space anywhere in it, and no figure from
    another writing system -- a figure that is not one of these ten
    reads as a number to the library underneath and would silently mean
    something the person did not type. Leading zeros are accepted and
    change nothing. The accepted range is 0 to 18446744073709551615.

    The LENGTH is checked before the text is turned into a number, and
    that order is the point: Python refuses to read a number written in
    very many figures at all, and its refusal is a traceback rather than
    a sentence. Comparing two texts of the same length figure by figure
    is the same comparison as comparing the two numbers, so nothing is
    lost by settling it as text.
    """
    if not given:
        return (None, errors.seed_not_in_figures(given, _SEED_CEILING))
    for character in given:
        if character not in _FIGURES:
            return (None, errors.seed_not_in_figures(given, _SEED_CEILING))
    trimmed = _without_leading_zeros(given)
    if len(trimmed) > len(_SEED_CEILING):
        return (None, errors.seed_too_large(given, _SEED_CEILING))
    if len(trimmed) == len(_SEED_CEILING) and trimmed > _SEED_CEILING:
        return (None, errors.seed_too_large(given, _SEED_CEILING))
    return (int(trimmed), "")


def _twin_stem(name: str) -> str:
    """The description's file name with a trailing '-profile' taken off.

    'clinic-profile.json' names the twin 'clinic-twin.csv', which is the
    name a person expects beside their 'clinic.csv'. A description
    renamed to something that does not end that way keeps its whole name
    and the twin is written beside it under it, which is still two names
    nobody else owns.
    """
    if not isinstance(name, str):
        raise TypeError("internal check: a file name was not text")
    lowered = name.casefold()
    if lowered.endswith("-profile"):
        return name[: len(name) - len(_PROFILE_MARK)]
    return name


def _twin_paths(
    description: pathlib.Path, out_dir: "str | None"
) -> "tuple[pathlib.Path, pathlib.Path]":
    """Where the twin and its report go (plan P2-D10).

    Guarantees:

    - Inputs: the path of the description this run was given, and the
      folder the person asked for, or nothing for the folder the
      description is in.
    - Determinism: the same two paths for the same two inputs.
    - Errors raised: ProfileError, with a plain-language message, when a
      named folder does not exist; PathValidationError when the folder or
      either output name is not a plain local path.
    - Boundary: nothing is opened, created or written here.

    Every exact target goes through the locality gate, not only the
    folder: a link left at the twin's name would otherwise send the file
    wherever it points (review item P1-R1-F2, carried into this command).
    The two names cannot collide with the profiler's pair, which end
    '-profile.json' and '-profile.txt'.
    """
    source = pathlib.Path(description)
    stem = _twin_stem(f"{source.stem}")
    if out_dir is None:
        folder = pathlib.Path(source.parent)
    else:
        validated = validate_local_path(out_dir, purpose="output folder")
        folder = pathlib.Path(validated)
        if not folder.is_dir():
            raise errors.ProfileError(
                errors.output_folder_missing(f"{folder}", errors.TWIN_WORDS)
            )
    twin_target = validate_local_path(
        f"{folder / (stem + _TWIN_SUFFIX)}", purpose="output file"
    )
    report_target = validate_local_path(
        f"{folder / (stem + _REPORT_SUFFIX)}", purpose="output file"
    )
    return (pathlib.Path(twin_target), pathlib.Path(report_target))


def _already_there(target: pathlib.Path) -> bool:
    """True when something already occupies ``target``.

    A link is something, whether or not it leads anywhere: a run that
    called a dangling link "nothing" would write through it to wherever
    it points. Both questions answer False rather than raising when the
    filesystem will not say, and the write transaction refuses a name it
    could not examine, so a name this cannot settle is not written to on
    the strength of this answer alone.
    """
    place = pathlib.Path(target)
    if place.is_symlink():
        return True
    return place.exists()


def _run_generate(
    description: str,
    out_dir: "str | None",
    seed_given: str,
    replace: bool,
) -> int:
    """Do the work of `synthtwin generate`; return the exit code.

    The order of operations is a control here as much as in the profile
    command, and it is exactly this: the seed is settled before the
    description is opened; the description is loaded, which is what makes
    a missing or unreadable one say so rather than being reported as a
    name clash; every refusal that can be decided from the NAMES alone --
    a folder in the way, an output that leads back to the description, an
    output name already taken -- is made next, before the twin exists;
    and the twin is then built entirely in memory, so a description whose
    published facts cannot all hold is refused with nothing on disk
    either. A refused run leaves the folder exactly as it found it, at
    every one of those points.

    THE MODULES ARE IMPORTED HERE, inside the branch (plan P2-D1). None
    of the four reaches the table reader or pandas, and importing them
    here rather than at the top of the file is what makes that provable
    of the whole run rather than of the part after the dispatch: this
    function is the only place in the package where generation is
    reached from the command line, and the reader is not in scope in it.

    A PRE-EXISTING OUTPUT IS REFUSED, and there is no way to prove
    otherwise (plan P2-D10, review item P2-R4-F1). synthtwin cannot tell
    an earlier twin of its own from a file of the person's that happens
    to sit at that name -- reading either one to find out would break the
    rule that this command opens the description and nothing else -- so
    it refuses, names both files, and teaches `--replace`.
    """
    from synthtwin import contract, generation, rendering, writing

    seed, refusal = _seed_or_refusal(seed_given)
    if seed is None:
        _warn(refusal)
        return 2
    loaded = contract.load_profile(description)
    twin_path, report_path = _twin_paths(pathlib.Path(description), out_dir)
    writing.refuse_if_folder(twin_path, errors.TWIN_WORDS)
    writing.refuse_if_folder(report_path, errors.TWIN_WORDS)

    # The output must never be the description itself. On POSIX a link
    # left at the twin's name resolves to a permitted local path, so the
    # locality gate cannot catch this one -- and what would be destroyed
    # is the file the twin is built from.
    source = validate_local_path(description, purpose="input")
    if (
        twin_path == source
        or report_path == source
        or writing.is_the_same_file(twin_path, source)
        or writing.is_the_same_file(report_path, source)
    ):
        _warn(
            errors.output_would_replace_the_table(
                _shown(source), errors.TWIN_WORDS
            )
        )
        return 1

    shown_twin_path = _shown(twin_path)
    shown_report_path = _shown(report_path)
    if not replace:
        taken: list[str] = []
        for target in (twin_path, report_path):
            if _already_there(target):
                taken = taken + [_shown(target)]
        if taken:
            _warn(
                errors.outputs_already_there(
                    shown_twin_path, shown_report_path, taken
                )
            )
            return 1

    twin = generation.generate(loaded, seed)
    # The twin's bytes are NOT put through the display boundary. That
    # boundary is for text a person reads, and a cell that reached it
    # would arrive in the twin as the escape rather than as the value --
    # so a column name beginning with the byte-order mark, or a label
    # holding a control character, would come back from the twin as
    # something the description never published. The report is a
    # human-facing sink like the profiler's summary and crosses the
    # boundary once, here, so the file on disk and the screen carry the
    # same text and cannot differ.
    twin_text = rendering.twin_csv(twin)
    report_text = parsing.visible_lines(rendering.report(loaded, twin))

    _say(report_text)
    # ONE LINE ON THE SCREEN NAMING WHAT THE TWIN INVENTED (plan P4-D2
    # item 2). It is a warning rather than an ordinary line because a
    # person who reads one thing before opening the twin should read
    # this one; the exit code does not move for it, because a decline is
    # not a failure and a run that warned still succeeded.
    _warn(rendering.made_up_warning(loaded))
    _say(
        f"These two files will be written:\n"
        f"  {shown_twin_path}\n  {shown_report_path}"
    )
    _say(
        "\nBoth carry facts computed from your real data -- the counts, "
        "ranges and labels the description publishes are in the twin's "
        "own values. Keep them under the same rules your institution "
        "applies to the table itself, and read the report above before "
        "moving them anywhere."
    )

    # The same two halves as the profile command's write, for the same
    # two reasons: the returned list names every working file a finished
    # run could not clear away, and the DiskState carries the sentence
    # for a failure the transaction could not describe in its own words
    # (review items P1-R6-F5 and P1-R7-F1). The words are the
    # generator's, so a stop names the twin and the description rather
    # than a profile and a table this run never had (plan P2-D10).
    state = writing.DiskState()
    try:
        left_behind = writing.write_both_files(
            twin_path,
            report_path,
            twin_text,
            report_text,
            table_path=pathlib.Path(source),
            state=state,
            words=errors.TWIN_WORDS,
        )
    except BaseException:
        if state.sentence:
            _warn(_shown(state.sentence))
        elif state.both_files_written:
            _say(f"\nWritten:\n  {shown_twin_path}\n  {shown_report_path}")
            if state.left_behind:
                _warn(_left_behind_note([state.left_behind], "twin"))
        raise
    if left_behind:
        # A caution, not a refusal, and printed BEFORE the confirmation
        # for the same reason as in the profile command: if only one of
        # the two lines reaches the person, it must be the one naming a
        # file that may hold real-derived text.
        _warn(_left_behind_note(left_behind, "twin"))
    _say(f"\nWritten:\n  {shown_twin_path}\n  {shown_report_path}")
    _say(_teaching_validate(description, twin_path))
    return 0


def _teaching_validate(
    description: str, twin_path: pathlib.Path
) -> str:
    """The sentence that ends a finished `generate` run (plan P3-D6).

    The teaching chain: `profile` ends by teaching `generate`, `generate`
    ends by teaching `validate`, and `validate` ends by saying what its
    verdict means. Somebody who has never used a command line has to be
    able to get from the first command to the last without reading
    anything but what the previous one printed.

    The line names `--twin` even where the twin sits exactly where
    validate would look for it. Working out when the option can be left
    out means reasoning about `--out-dir`, and a taught command line that
    is right only sometimes is worse than a longer one that is always
    right.

    Both paths pass through `_shown`, like every other path this module
    prints.
    """
    return (
        f"\nNext, measure the twin against the description:\n"
        f"  synthtwin validate {_shown(description)} "
        f"--twin {_shown(twin_path)}\n"
        f"That writes a quality report saying which of the description's "
        f"obligations the twin holds, which it misses, and which nothing "
        f"written in a CSV can evidence either way."
    )


# -- checking a written file against the description (plan P3-D1) ------


def _quality_path(
    description: pathlib.Path, measured: str, out_dir: "str | None"
) -> pathlib.Path:
    """Where the quality report goes (plan P3-D1, amendment A-P3-4).

    Guarantees:

    - Inputs: the path of the description this run was given, the path of
      the file this run measures, and the folder the person asked for, or
      nothing for the folder the description is in.
    - Determinism: the same path for the same three inputs.
    - Errors raised: ProfileError, with a plain-language message, when a
      named folder does not exist; PathValidationError when the folder or
      the output name is not a plain local path.
    - Boundary: nothing is opened, created or written here.

    THE NAME COMES FROM THE MEASURED FILE AND THE FOLDER FROM THE
    DESCRIPTION, and both halves are deliberate. The name, because the
    report is about the measured file and two measured files must not
    collide on one report name -- the whole of review item P3-V2-G. The
    folder, because `--out-dir` is where this command writes and the
    description's folder is where the person is working; the measured
    file may sit somewhere they cannot write at all, and a command that
    put its output there would fail for a reason they did not choose.

    Two files with the SAME name in two folders still collide, and that
    is a real collision rather than a spurious one: the refusal names
    the file, and `--out-dir` separates them.

    The exact target goes through the locality gate, not only the folder,
    for the reason `_twin_paths` gives: a link left at the report's name
    would otherwise send the file wherever it points. The name cannot
    collide with any of the four artifacts that already exist, which end
    '-profile.json', '-profile.txt', '-twin.csv' and '-twin-report.txt'.
    """
    source = pathlib.Path(description)
    stem = f"{pathlib.Path(measured).stem}"
    if out_dir is None:
        folder = pathlib.Path(source.parent)
    else:
        validated = validate_local_path(out_dir, purpose="output folder")
        folder = pathlib.Path(validated)
        if not folder.is_dir():
            raise errors.ProfileError(
                errors.output_folder_missing(
                    f"{folder}", errors.QUALITY_WORDS
                )
            )
    target = validate_local_path(
        f"{folder / (stem + _QUALITY_SUFFIX)}", purpose="output file"
    )
    return pathlib.Path(target)


def _measured_path(description: str, twin_given: "str | None") -> str:
    """Which file this run measures: the one named, or the twin beside it.

    The default is derived from the DESCRIPTION's own folder rather than
    from `--out-dir`, because `--out-dir` says where this command writes
    and says nothing about where an earlier `generate` run put its twin.
    A person whose twin is somewhere else names it with `--twin`, which
    is the line the finished `generate` run taught them.
    """
    if twin_given is not None:
        return twin_given
    twin_path, _report_path = _twin_paths(pathlib.Path(description), None)
    return f"{twin_path}"


def _verdict_lines(missed: int, code: int) -> str:
    """What the verdict means, what it does not, and what code was seen.

    Plan P3-D6's third teaching sentence. It says the same things the
    report's own summary says, because the person who reads the screen
    and the person who reads the file are the same person, and two
    accounts of one verdict is one account too many.
    """
    if missed == 0:
        headline = (
            "No checkable obligation was missed. That is the whole of "
            "what this says."
        )
    else:
        headline = (
            f"{missed} checkable obligation(s) were missed. The quality "
            f"report names every one of them, with what the description "
            f"asks for beside what the file was found to hold."
        )
    return (
        f"\nWhat this means. {headline} It is not a verdict that the "
        f"file is fit for any analysis; it validates nothing this "
        f"description does not publish; and it cannot tell a synthetic "
        f"file from a real one, because nothing in a CSV proves where "
        f"its rows came from.\n"
        f"Automation saw exit code {code}: 0 means nothing was missed, 3 "
        f"means something was, 1 means the check could not run at all, "
        f"and 2 means the command line could not be used."
    )


def _run_validate(
    description: str,
    twin_given: "str | None",
    out_dir: "str | None",
    replace: bool,
) -> int:
    """Do the work of `synthtwin validate`; return the exit code.

    The order of operations is a control here as much as in the other
    two commands, and it is exactly this: the description is loaded
    first, so a missing or unreadable one says so rather than being
    reported as a name clash; every refusal that can be decided from the
    NAMES alone -- a folder in the way, an output leading back to either
    input, an output name already taken -- is made next, before a byte of
    the measured file is read; and the measurement then happens entirely
    in memory, so a description no file can be the twin of is refused
    with nothing on disk either. A refused run leaves the folder exactly
    as it found it, at every one of those points.

    THE MODULES ARE IMPORTED HERE, inside the branch (plan P2-D1, P3-D1).
    This branch DOES reach the table reader, through `validation`, and it
    must: measuring a file means describing that file with the profiler's
    own producer. What it must not reach is the generator, so `rendering`
    -- which imports it -- is not among these four, and the quality
    report is rendered by `quality` instead. This is the only place in
    the package where validation is reached from the command line.

    THE EXIT CODE IS THE PRODUCT AS MUCH AS THE REPORT IS (V6.5). 0 when
    the check ran and nothing was missed, 3 when it ran and something
    was, 1 when it could not run at all, 2 when the command line could
    not be used. Automation tells a file that failed its check from a
    file that was never evaluated without reading a word of prose.

    A PRE-EXISTING OUTPUT IS REFUSED, on the generate command's own
    reasoning (R-P2-12 parity): synthtwin cannot tell a quality report an
    earlier run of its own wrote from a file of the person's that happens
    to sit at that name, so it refuses, names the file, and teaches
    `--replace`.
    """
    from synthtwin import contract, quality, validation, writing

    loaded = contract.load_profile(description)
    measured = _measured_path(description, twin_given)
    quality_path = _quality_path(pathlib.Path(description), measured, out_dir)
    writing.refuse_if_folder(quality_path, errors.QUALITY_WORDS)

    # The output must never be either file this run reads. A link left
    # at the report's name resolves to a permitted local path, so the
    # locality gate cannot catch this one -- and what would be destroyed
    # is either the description the verdicts are measured against or the
    # file being measured, which may be somebody's own table.
    source = validate_local_path(description, purpose="input")
    measured_source = validate_local_path(measured, purpose="input")
    guarded = [
        (pathlib.Path(source), errors.INPUT_DESCRIPTION),
        (pathlib.Path(measured_source), errors.INPUT_MEASURED_FILE),
    ]
    for place, noun in guarded:
        if quality_path == place or writing.is_the_same_file(
            quality_path, place
        ):
            _warn(
                errors.output_would_replace_an_input(
                    _shown(place), noun, errors.QUALITY_WORDS
                )
            )
            return 1

    shown_quality_path = _shown(quality_path)
    if not replace and _already_there(quality_path):
        _warn(errors.quality_target_already_there(shown_quality_path))
        return 1

    outcome = validation.measure(loaded, measured)
    # The report is a human-facing sink like the profiler's summary and
    # the twin's report, so it crosses the display boundary once, here,
    # and the same text is what reaches the screen and what is written to
    # disk. The two cannot differ.
    report_text = parsing.visible_lines(
        quality.quality_report(loaded, outcome)
    )
    code = 3 if outcome.census.missed else 0

    _say(report_text)
    _say(f"This file will be written:\n  {shown_quality_path}")
    # THE OTHERS ARE ALL NAMED, not the two nearest to hand (plan
    # amendment A-P3-8 clause 2). This sentence exists to say that a
    # verdict travels under the same rules as the thing it measured, and
    # a list that stops partway through reads as a list of the ones that
    # matter.
    _say(
        "\nIt carries counts and measurements taken from the file it "
        "checked, so it is real-derived material like the description, "
        "the plain-language summary beside it, the twin and the twin's "
        "report. Keep it under the same rules your institution "
        "applies to the table itself, and read the report above before "
        "moving it anywhere."
    )

    # The same two halves as the other two commands' writes, for the same
    # two reasons: the returned list names every working file a finished
    # run could not clear away, and the DiskState carries the sentence
    # for a failure the transaction could not describe in its own words
    # (review items P1-R6-F5 and P1-R7-F1). The words are the
    # validator's, so a stop names the quality report and the description
    # rather than a profile and a table this run never had.
    state = writing.DiskState()
    try:
        left_behind = writing.write_one_file(
            quality_path,
            report_text,
            sources=guarded,
            state=state,
            words=errors.QUALITY_WORDS,
        )
    except BaseException:
        if state.sentence:
            _warn(_shown(state.sentence))
        elif state.target_written:
            _say(f"\nWritten:\n  {shown_quality_path}")
            if state.left_behind:
                _warn(
                    _left_behind_note(
                        [state.left_behind], "quality report", True
                    )
                )
        raise
    if left_behind:
        # A caution, not a refusal, and printed BEFORE the confirmation
        # for the reason the other two commands give: if only one of the
        # two lines reaches the person, it must be the one naming a file
        # that may hold real-derived text.
        _warn(_left_behind_note(left_behind, "quality report", True))
    _say(f"\nWritten:\n  {shown_quality_path}")
    _say(_verdict_lines(outcome.census.missed, code))
    return code


def main(argv: "list[str] | None" = None) -> int:
    """Run the `synthtwin` command.

    Guarantees:

    - Inputs: `argv` is the list of command-line arguments to parse, or
      `None` to parse `sys.argv[1:]`. Recognized: `--version`, `--help`,
      the `profile` command word with its options, the `generate`
      command word with `--seed`, `--out-dir` and `--replace`, and the
      `validate` command word with `--twin`, `--out-dir` and
      `--replace`.
    - Return codes: 0 when the work finished; 1 when a file given could
      not be read or an output file could not be written, with a
      plain-language explanation on the error stream; 2 when an option's
      value was not usable, which includes naming one value both with
      `--keep-value` and with `--missing-value`, and a seed that is not a
      whole number in figures inside the stated range. `SystemExit` with
      code 2 still ends the run for a word on the command line that
      synthtwin does not recognize, and with code 0 for `--help`. For
      `profile` and `generate`, 0 always means both files were written: a
      working file that could not be cleared away afterwards is named on
      the error stream as a caution and does not change the code, because
      nothing about the output is wrong.

      `validate` splits the finished run in two, and the split is the
      machine channel this phase ships (V6.5): 0 when the check ran to
      completion and no obligation was MISSED, and 3 when it ran to
      completion and at least one was. Both mean the quality report was
      written. Automation therefore tells a file that failed its check
      from a file that was never evaluated -- which is what 1 means on
      this command -- without reading a word of prose.
    - Determinism: the same table and the same options produce the same
      two files, byte for byte, on the same platform (plan D12 and
      P1-D11); so do the same description, the same seed and the same
      version of synthtwin (plan P2-D8); and so does the quality report,
      whose bytes are a fixed function of the description's bytes, the
      measured file's name and bytes, and the version (V10). A validate
      run consumes no randomness: it draws from no random source, and no
      module of this package it reaches imports one. It does not follow
      that none is in the process. The reader needs pandas and pandas
      imports numpy, so `numpy.random` is loaded by any run that reads a
      file; this used to be written as "reaches no random source at all",
      which was false (amendment A-P3-4).
    - Errors raised: none that reach the user as a traceback. Every
      refusal in the catalog and every path rejection is caught here and
      printed as a message that says what happened and what to do next.
      Pressing Ctrl-C is the exception, and deliberately: it is the
      person stopping their own command, so it ends the command the way
      every other command on their computer ends, rather than being
      dressed up as a refusal synthtwin decided on. The write
      transaction clears up and names what is on disk first, whatever
      stopped it, and if it stopped AFTER both files were written it
      says so in the words a finished run uses.

      Three bounds, stated rather than rounded off, because a claim
      that a file is never left in silence would be false:
      (1) a SECOND stop arriving while the first is being described
      costs that message (stated in `profile.write_both_files`);
      (2) once the transaction has returned normally, the two lines
      that report the run are ordinary prints outside any handler, so
      a stop between them can cost one of them -- the leftover caution
      is printed first for that reason;
      (3) a stopped MACHINE is not covered at all, because nothing runs
      afterwards to write anything.
    - Boundary: the only file `profile` reads is the table the user
      named; the only file `generate` reads is the description the user
      named; `validate` reads exactly two, the description and the file
      it measures, and never the generation report -- everything it needs
      to know about what the description authorizes is recomputed from
      the description alone. Every one of those paths goes through the
      path validator. The only files any of the three writes are the ones
      it reports at the end, plus working files of synthtwin's own making
      beside them, which are removed before the command returns -- and
      named on the error stream in the rare case that one could not be. A
      `generate` run never opens a table and never reaches the module
      that can: the reader is not imported at all unless the person typed
      `profile` or `validate` (plan P2-D1, P3-D1). A `validate` run never
      reaches the generator, so this package's own random number
      generator is out of its reach and its verdicts cannot inherit the
      planner's defects; and it never writes, moves, truncates or
      re-encodes either of the two files it read. No network,
      subprocess, native, or dynamic-code operation is performed
      anywhere in the package.
    - Display: nothing reaches the screen, the error stream, the summary
      file or the report file without passing the display boundary
      described at the top of this module. A path or a value carrying an
      escape sequence is shown as text, never obeyed by the terminal.
      The twin's own cells are the one thing that does NOT pass it, and
      must not: they are read by a program, and an escaped cell would be
      a value the description never published.
    """
    options = _parse_arguments(argv)

    if options.version:
        _say(_version())
        return 0

    named = options.given
    if named is None or options.command is None:
        _say(_STATUS.format(version=_version(), repo=_REPO_URL))
        return 0

    generating = options.command == _GENERATE
    validating = options.command == _VALIDATE
    try:
        if generating:
            return _run_generate(
                named, options.out_dir, options.seed, options.replace
            )
        if validating:
            return _run_validate(
                named, options.twin, options.out_dir, options.replace
            )
        return _run_profile(
            named,
            options.out_dir,
            options.smallest_group,
            options.identifiers,
            options.kept_values,
            options.missing_values,
            options.first_row,
            options.day_first,
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
        # the description and rendering it allocate again, and so does
        # building a twin, which holds every cell of every column at once.
        # One refusal per command covers them all rather than a traceback
        # reaching the user, and the three say different things because
        # the three runs are holding different files.
        #
        # The validate wording names the DESCRIPTION, because that is the
        # file the person typed and this handler cannot know how far the
        # run got. A failure inside the measurement itself is composed by
        # `validation.measure`, which does know, and names the file it
        # was reading.
        if generating:
            _warn(errors.twin_out_of_memory(_shown(named)))
        elif validating:
            _warn(errors.quality_out_of_memory(_shown(named)))
        else:
            _warn(errors.out_of_memory_while_describing(_shown(named)))
        return 1


if __name__ == "__main__":
    sys.exit(main())

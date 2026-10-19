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
evidence either way. One more word, `synthtwin doctor`, is no step of a
run: it checks this computer before the first one -- Python, numpy and
pandas, the output folder, the memory against a named table's size --
and reads no table (plan P4-D397).

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
default smallest group -- is held below as constants instead of being
read off `reading` and `taxonomy`, because the parser is built BEFORE
any command word has been read: it may not start the reader, and
`taxonomy` belongs to the `profile` branch. The default smallest group
is read from `parsing`, where it is written once for every module; the
suite checks each constant against the module that owns the value, so
the two cannot drift apart in silence.

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
import os
import pathlib
import sys

from synthtwin import asking, dialect, errors, parsing
# -- 3b.R4 (P4-D384): the twelve systems that write dates as counts, a
# module of the package's own that imports `parsing` alone.
from synthtwin import date_counts
from synthtwin.paths import PathValidationError, validate_local_path

_REPO_URL = "https://github.com/alfredocr05/synthtwin"

# THE PARSER'S OWN VOCABULARY, written out here for the reason the module
# docstring gives: the command line is built before any command word has
# been read, so it may not start the table reader (plan P2-D1) and may
# not reach into the `profile` branch's taxonomy. Each of these is the
# same value the module that owns it holds, and the suite compares them
# so a change in one place cannot pass unnoticed in the other. The
# smallest group is not written out: it is read from
# `parsing.DEFAULT_SMALL_CELL_FLOOR`, the one place its default is
# written (plan P4-D316), which this module imports already.
_FIRST_ROW_AUTOMATIC = "auto"
_FIRST_ROW_NAMES = "names"
_FIRST_ROW_DATA = "data"
_SMALLEST_GROUP = parsing.DEFAULT_SMALL_CELL_FLOOR

# THE LINE UNDER WHICH A NAMED GROUP CAN POINT AT ONE PERSON, mirrored
# here from `_NOTICE_LINE` for the reason
# `_SMALLEST_GROUP` is mirrored: the command line is built before any
# command word is read (plan P2-D1), and the suite compares the two so
# they cannot drift. It is the same number as the default again since
# 2026-09-22 (plan P4-D316), but it is a different fact: the default is
# what a run writes when nobody asks, and this is a fact about people
# that does not move when the default does.
_NOTICE_LINE = 11

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
    "where enough rows hold it -- by default at least "
    f"{_SMALLEST_GROUP} -- and that "
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

# The three commands of a run, as the words a person types.
_PROFILE = "profile"
_GENERATE = "generate"
_VALIDATE = "validate"
# ...and the check of this computer before a first run (plan P4-D397).
# It reads no table and makes nothing a run is built from, so it is not
# a step of the run: the install scripts end by running it, and a person
# runs it again with their table's path to weigh its size against this
# computer's memory before `profile` reads it.
_DOCTOR = "doctor"

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
# THE TWIN OF A WORKBOOK IS A WORKBOOK (plan P4-D79), so it is named
# like one. A person whose table arrived as `clinic.xlsx` gets
# `clinic-twin.xlsx`, which opens in the program their table came from.
_WORKBOOK_TWIN_SUFFIX = "-twin.xlsx"
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
from your table under anything that groups rows. Analysis code you
develop on the twin is meant to run unchanged on your table, and nothing
here guarantees that it will: a step that depends on more than the
description publishes, such as a cut into quartiles, can succeed on the
twin and fail on your table. A number it computes from two columns of
the twin means nothing about your table.
Cross-column structure arrives in a later version of synthtwin.

What that does and does not promise about your rows. The generator is
never handed your table, does not open one, and samples or copies no row
of it. That says where the twin's values come from. It does not say that
no row of the twin can equal a row of yours: the description publishes
exact counts, and meeting them exactly can force a twin row to match a
real one. A table of 100 rows with one column, whose single label all
100 rows share, publishes that label with the count 100 -- so the twin
writes it in all 100 of its rows. 100 rows is the smallest table
synthtwin describes: under that, `synthtwin profile` refuses and writes
nothing. synthtwin offers no formal privacy guarantee.

All six files -- the profile, the plain-language summary beside it, the
questions file, the twin, the twin's report and the quality report --
are computed from your real data, so your institution's rules for
real-derived material apply to all six, not to the profile alone.

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

  synthtwin doctor data.csv
      check this computer before a first run, and weigh the size of
      data.csv against its memory without opening the file
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


# THE CHARACTERS A SHELL READS AS THEMSELVES, outside any quotes (the
# Codex review of lane R1, item 1). A value of the table or a column's
# name is put into a line the person is told to type again, and a shell
# reads `$(...)`, a backtick, `;` or a space in it as syntax: measured on
# the tree before this, a code written `$(printf marker)` was printed
# bare after `--missing-value`, and `NOT RECORDED` became two words, so
# the repeat exited 2. A value made only of these characters is printed
# as it is; any other is quoted whole. POSIX shells first; PowerShell,
# the shell a Windows terminal opens, reads `,` and `@` as its own syntax
# and `\` and `:` as text, so its set differs by those. And `~` is no
# plain character to a POSIX shell anywhere in a word: bash reads a `~`
# after the `=` of a word shaped like `a=~`, or after a `:` there, as
# the home folder, and prints `a=/home/...` (measured with bash 3.2;
# zsh leaves it alone), so such a code would be declared as another.
_POSIX_PLAIN = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    "_@%+=:,./-"
)
_POWERSHELL_PLAIN = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    "_%+=:./\\~-"
)
# The four characters PowerShell reads as a single quote: the ASCII one
# and the three typographic ones. Inside single quotes each is written
# twice, which is how that shell writes one of them.
_POWERSHELL_QUOTES = "'‘’‚‛"


def _on_windows() -> bool:
    """Whether the lines to type are quoted for PowerShell rather than POSIX."""
    return sys.platform == "win32"


def _quoted_for_the_shell(value: object, windows: "bool | None" = None) -> str:
    """One word, written so the shell the person types it into reads it back.

    A word of only plain characters is printed as it stands, so `seen_at`
    stays `seen_at`. Any other is quoted whole: on POSIX in single quotes,
    a single quote inside written `'"'"'`; on Windows (``windows`` true,
    or the platform where it is None) in PowerShell's single quotes, each
    quote character inside written twice and a double quote written as
    the program reads it back (below). Both shells read everything
    between single quotes as text, so nothing in the value is run.

    Guarantees: accepts any value, read as text; returns one word for the
    shell. Determinism: a function of the value and the platform. Raises
    nothing. No I/O.
    """
    text = f"{value}"
    powershell = windows or (windows is None and _on_windows())
    plain = _POWERSHELL_PLAIN if powershell else _POSIX_PLAIN
    # ...and some of them not first: zsh reads a word starting with `=`
    # as the path of a command, and PowerShell a leading `~` as a home
    # folder, so such a word is quoted too. Inside a word `~` is text to
    # PowerShell, which a Windows short path (`RUNNER~1`) needs. And a
    # word starting with `-` is quoted for PowerShell: Windows PowerShell
    # hands a program a bare word such as `--missing-value=-1.5` as two,
    # split before the point, so `_typed_option`'s joined word is always
    # quoted there.
    leading = ("=", "~", "-") if powershell else ("=",)
    if (
        text
        and text[:1] not in leading
        and all(character in plain for character in text)
    ):
        return text
    # Built a character at a time, for the offline audit's reason
    # (`_joined`): no method of the value is called.
    #
    # AND ON POWERSHELL A DOUBLE QUOTE IS WRITTEN AS THE PROGRAM READS IT
    # BACK. Windows PowerShell 5.1, the one every Windows machine
    # carries, puts a value holding `"` into the command line it hands a
    # program with that quote bare, and the program reads it as a quote
    # of its own: `say "no" twice` arrived as `say no twice`, and `UNK"`
    # opened a run that took the option typed after it into the value.
    # So each `"` is written `\"` with the backslashes before it doubled,
    # and the backslashes ending a value that holds white space, which
    # that shell wraps in double quotes, are doubled too -- the C
    # runtime's own rule for reading a command line. PowerShell 7.3 or
    # later hands such a value over whole and keeps those backslashes, so
    # there the declaration misses its value and the question is put
    # again; on neither is an option taken into a value or anything run.
    #
    # WHITE SPACE IS EVERY CHARACTER .NET COUNTS AS WHITE SPACE, not the
    # space and the tab alone (the verification of the repairs of the
    # Codex review of lane R1, its open item 2). 5.1 wraps a value
    # holding any character `Char.IsWhiteSpace` names -- the no-break
    # space, the ideographic space and the other space separators, which
    # the display boundary leaves as they are -- so `a`, a no-break
    # space, `b` and `\` was printed with its one backslash, and in a
    # model of 5.1's native command binder (no Windows PowerShell was at
    # hand to run it) the program was handed one word, `a`, the space,
    # `b`, a `"` and ` --code dose`: the option typed after the value
    # was taken into it. `parsing.trimmed`
    # empties a character exactly where Python reads it as white space,
    # which takes in every character .NET counts. A character the
    # display boundary shows escaped -- the tab, the line breaks, and the
    # four separators below the space that Python counts too -- is no
    # white space on the printed line, so a value whose only white space
    # is one of those is not wrapped and its ending backslashes reach the
    # program doubled: the declaration misses its value, as it already
    # did for a value holding a character shown escaped, and nothing is
    # taken into a value.
    inside = ""
    slashes = ""
    spaced = False
    for character in text:
        if not parsing.trimmed(character):
            spaced = True
        if powershell and character == "\\":
            slashes = slashes + character
            continue
        if powershell and character == '"':
            inside = inside + slashes + slashes + '\\"'
            slashes = ""
            continue
        inside = inside + slashes
        slashes = ""
        if powershell and character in _POWERSHELL_QUOTES:
            inside = inside + character + character
        elif not powershell and character == "'":
            inside = inside + "'\"'\"'"
        else:
            inside = inside + character
    inside = inside + slashes + (slashes if spaced else "")
    return f"'{inside}'"


def _typed_option(
    option: str, value: object, windows: "bool | None" = None
) -> str:
    """An option and its value, as the person types them again.

    The value is quoted for the shell (`_quoted_for_the_shell`), and one
    that starts with a minus sign is joined to its option with `=` and
    the two written as one word, quoted on PowerShell always: argparse
    reads a word starting with `-` as an option of its own, so
    `--missing-value -UNK` is refused where `--missing-value=-UNK` is
    read. Then the whole is shown through the display boundary, like
    every value this module prints.

    Guarantees: accepts an option and a value; returns the text to type.
    Determinism: a function of the two and the platform. Raises nothing.
    """
    text = f"{value}"
    if text[:1] == "-":
        return _shown(_quoted_for_the_shell(f"{option}={text}", windows))
    return f"{option} {_shown(_quoted_for_the_shell(text, windows))}"


def _typed_path(path: object, windows: "bool | None" = None) -> str:
    """A path the person types as an argument of its own, quoted for the shell.

    A path starting with `-` is read by argparse as an option, so it is
    written `./-...`, which names the same file. Shown through the
    display boundary.
    """
    text = f"{path}"
    if text[:1] == "-":
        text = f"./{text}"
    return _shown(_quoted_for_the_shell(text, windows))


def _shell_named(windows: "bool | None" = None) -> str:
    """Which shell the lines to type are quoted for, in words."""
    if windows or (windows is None and _on_windows()):
        return "quoted for PowerShell"
    return "quoted for a POSIX shell such as bash or zsh"


def _quoting_said(line: str, windows: "bool | None" = None) -> str:
    """Which shell a line to type is quoted for, said where it quotes a value.

    The line that repeats a run always says it (`_how_to_repeat`). The
    other lines a person is told to type -- the options a notice offers,
    the `synthtwin validate` line -- say it once a value on them is
    quoted, which is when the shell matters: PowerShell's quotes are not
    the Windows command prompt's, which runs a `&` inside them, so the
    person is told which shell the line was written for (the Codex
    review of lane R1, item 1). A quoted value is the only way a `'`
    reaches such a line, since no plain character is one.
    """
    if "'" not in line:
        return ""
    return f"\n  (each value {_shell_named(windows)})"


def _say(message: str, end: str = "\n") -> None:
    """Print one message to the screen, through the display boundary.

    One of the two places in this module that print. Whatever it is
    given goes through `parsing.visible_lines` first, so a value that
    reached here without being shown safely still cannot instruct the
    terminal. Line breaks are kept: they are synthtwin's own layout.
    ``end`` is what follows the message, a line feed unless the caller
    is printing one message in pieces (`_say_pieces`).
    """
    print(parsing.visible_lines(f"{message}"), end=end)


def _say_pieces(pieces: "list[str]") -> None:
    """Print one message handed over in pieces, as `_say` prints it whole.

    Each piece goes through `_say` with nothing after it -- and so
    through `parsing.visible_lines`, which reads one character at a
    time -- and the line feed `_say` ends a message with comes once,
    after the last piece: the screen receives the bytes
    `_say` gives the pieces added together (stage 4 lane S4c, plan
    P4-D390), and the whole message is never made at once.
    """
    for piece in pieces:
        _say(piece, "")
    _say("")


def _described_columns(
    document: "dict[str, object]",
) -> "list[dict[str, object]]":
    """The column blocks of a freshly built description.

    `build_document` returns a plain mapping of published keys, so its
    `columns` entry is typed as loosely as every other value in it, and
    walking it directly is a walk over something the type check cannot
    name. This narrows it once, where the narrowing can be read, rather
    than at each of the two places that walk it.

    Guarantees: accepts a document this package built; returns its
    column blocks, or an empty list where the entry is not a list of
    mappings -- which no document this package writes can be, and is
    handled rather than assumed. Determinism: a function of the
    mapping. Raises nothing. No I/O of any kind.
    """
    if "columns" not in document:
        return []
    given = document["columns"]
    if not isinstance(given, list):
        return []
    found: "list[dict[str, object]]" = []
    for entry in given:
        if isinstance(entry, dict):
            found += [entry]
    return found


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
            f"It was not readable as UTF-8, so it was read as "
            f"{dialect.ENCODING_WORDS[encoding]}; if any accented letter "
            f"looks wrong in this summary, save the file as 'CSV UTF-8' "
            f"and run the command again."
        )
    if encoding in (dialect.ENCODING_UTF16_LE, dialect.ENCODING_UTF16_BE):
        return (
            f"It was read as {dialect.ENCODING_WORDS[encoding]} text "
            f"(encoding: {encoding})."
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
    floor_chosen: bool
    identifiers: list[str]
    codes: list[str]
    measurements: list[str]
    decimal_commas: list[str]
    answers: "str | None"
    kept_values: list[str]
    missing_values: list[str]
    first_row: str
    day_first: bool
    # How many rows under the column names describe those columns, as
    # the person typed it, or empty (plan P4-D81). Text rather than a
    # number for the reason `seed` is text: whether it is a number this
    # tool can use is decided in words a person can act on.
    metadata_rows: str
    # Which character separates the columns, as the person typed it, or
    # empty (plan P4-D110). Text for the reason `metadata_rows` is.
    delimiter: str
    # Which sheet of a workbook holds the table, or empty to settle it
    # by the first visible one (plan P4-D77).
    sheet: str
    seed: str
    replace: bool
    # The `--date-count COLUMN SYSTEM` pairs as typed (landing R4, plan
    # P4-D384), each a column's name and the word of the system its dates
    # are counted in, read by `_run_profile`.
    date_counts: "list[list[str]]" = dataclasses.field(default_factory=list)
    # The columns named with `--twelve-hour` (landing T1, plan P4-D370).
    twelve_hours: "list[str]" = dataclasses.field(default_factory=list)
    # The `--century COLUMN=YEAR` options as typed (landing R2a, plan
    # P4-D383), read in words a person can act on by `_run_profile`.
    centuries: "list[str]" = dataclasses.field(default_factory=list)
    # -- 3b.R2c (P4-D383): the columns named with `--date-column` (Q6).
    date_columns: "list[str]" = dataclasses.field(default_factory=list)


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
        choices=[_PROFILE, _GENERATE, _VALIDATE, _DOCTOR],
        help=(
            "what to do: 'profile' describes a CSV table on this "
            "computer, 'generate' builds the synthetic twin from a "
            "description 'profile' wrote, 'validate' measures a CSV "
            "file against that description and writes the quality "
            "report, and 'doctor' checks this computer before a first "
            "run -- Python, numpy and pandas, the output folder and the "
            "memory -- and weighs a table's size against that memory "
            "when you name one, without opening it"
        ),
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help=(
            "the file to work on: the CSV table for 'profile', the "
            "description for 'generate' and for 'validate', and for "
            "'doctor' a table to weigh (optional; doctor reads its size "
            "alone and never opens it)"
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
        # NONE RATHER THAN THE NUMBER, so that typing the default is
        # distinguishable from not typing it (plan A-P4-37). The screen
        # alarm below is for somebody who CHOSE a floor that names small
        # groups; the written pages state what the description carries
        # either way, and they are the files that travel.
        default=None,
        metavar="ROWS",
        help=(
            "advanced: a value shared by fewer rows than this is left out "
            "of the profile and counted into a pooled remainder instead of "
            f"being named. THE DEFAULT IS {_SMALLEST_GROUP}: no group named "
            "anywhere in the profile covers fewer than "
            f"{_SMALLEST_GROUP} rows, so a value that fewer rows share is "
            "not named and does not reach the twin by name. A smaller "
            "number is let through -- --smallest-group 1 names every value "
            "your table holds, together with how many rows shared it -- "
            "and then the screen and every file the run makes say on their "
            "face that the profile names groups small enough to point at "
            "one person "
            f"(default: {_SMALLEST_GROUP})"
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
        "--code",
        action="append",
        default=None,
        metavar="COLUMN",
        help=(
            "name a column that holds a CODING SYSTEM rather than "
            "measurements -- vaccine codes, procedure codes, revenue "
            "codes, provider numbers, risk-group codes. Its values are "
            "still published, because which codes are common is the point "
            "of the column; what changes is that synthtwin stops reading "
            "them as numbers. It keeps each code exactly as written, "
            "leading zeros and all, and publishes how many rows carried "
            "each code that at least the smallest group of rows share "
            "(11 by default; rarer codes are counted together and not "
            "named) -- instead of an average, a spread and points along "
            "a range, which for a code are meaningless, and whose "
            "published boundaries are real codes besides. "
            "Use this for a column written in digits. A column whose "
            "every value carries a letter or a dash usually reads as "
            "codes already, but one whose values are mostly bare "
            "figures does not, however a few of them are spelled. Name "
            "here only if it is codes -- use --identifier for a record "
            "number nothing should publish, and neither one for a "
            "measurement. May be given more than once"
        ),
    )
    parser.add_argument(
        "--decimal-comma",
        action="append",
        default=None,
        metavar="COLUMN",
        help=(
            "name a column whose numbers are written with a COMMA where "
            "the decimal point goes, as they are in much of Europe: "
            "'1,5' for one and a half, '1.234,56' for one thousand two "
            "hundred and thirty-four and fifty-six hundredths. Without "
            "this, synthtwin reads such a column by its own default and "
            "gets it wrong in one of two ways -- '1,5' is not a number "
            "at all and the column is described as text, or '1,234' "
            "reads as one thousand two hundred and thirty-four. The "
            "twin also WRITES that column's numbers with a comma, so "
            "your own tools read the twin as they read your table. "
            "synthtwin never guesses this: a comma inside an address or "
            "a note is not a decimal point, so it changes the reading "
            "only for the columns you name. It reaches a column read as "
            "PLAIN NUMBERS, and a column whose numbers each wear one "
            "shared unit or currency mark, such as '795,64 EUR' or "
            "'37,5 %%': there the number inside the mark is read and "
            "written your way and the mark itself is copied exactly. "
            "It does NOT reach a cell holding two numbers with a "
            "separator between them, because there synthtwin cannot "
            "tell which mark is the decimal point; where that happens "
            "it says so and reads the column as it otherwise would. "
            "May be given more than once"
        ),
    )
    parser.add_argument(
        "--measurement",
        action="append",
        default=None,
        metavar="COLUMN",
        help=(
            "name a column that holds MEASUREMENTS written as two or "
            "more whole numbers in one cell -- a blood pressure such as "
            "120/80, a score written 12-5. synthtwin reads each number "
            "separately and publishes a range and an average for each "
            "one, so the twin's cells hold believable readings instead "
            "of digits in the right shape. Use it only where the "
            "numbers are QUANTITIES: a lab code such as 1923-1 and a "
            "drug code such as 00052-0052-52 are written exactly the "
            "same way and are codes, so name those with --code instead. "
            "A column of plain single numbers needs nothing: it is "
            "already read as numbers. IT ALSO SETTLES A SECOND SHAPE. "
            "A column whose number sits inside an electronic address, "
            "such as user12345@example.org, is described by a later "
            "rule instead, because the average of a column of real "
            "addresses means nothing as a quantity. Naming such a "
            "column here says the number inside is a quantity after "
            "all, and it is described as one. May be given more than "
            "once"
        ),
    )
    parser.add_argument(
        "--century",
        action="append",
        default=None,
        metavar="COLUMN=YEAR",
        help=(
            "name a column of dates whose years are written with TWO "
            "FIGURES, and the first year of the century they lie in: 1930 "
            "(years 1930 to 2029), 1940 (1940 to 2039) or 1900 (1900 to "
            "1999), as in --century birth_date=1930. Two figures do not say "
            "which century they are in, so synthtwin asks; without this it "
            "reads them as 1969 to 2068, and a birth date of 1925 written "
            "25 is then read as 2025. May be given more than once"
        ),
    )
    # -- 3b.R2c (P4-D383)
    parser.add_argument(
        "--date-column",
        action="append",
        default=None,
        metavar="COLUMN",
        help=(
            "name a column that holds DATES although some of its values are "
            "written another way, or written as a year and its day of the "
            "year (2023076): it is read as dates where half its values or "
            "more read as one, the rest left unread and written in the twin "
            "as made-up text. Without this such a column is read as text or "
            "numbers, and synthtwin asks. May be given more than once"
        ),
    )
    parser.add_argument(
        "--twelve-hour",
        action="append",
        default=None,
        metavar="COLUMN",
        help=(
            "name a column of times of day written on a 12-HOUR CLOCK "
            "WITHOUT AM OR PM, such as 8:34 and 12:15. A 24-hour clock "
            "whose hours all lie between 1 and 12 is written the same "
            "way, so synthtwin cannot tell the two apart and asks; "
            "without this it reads such a column as a 24-hour clock. "
            "Named here, 12 is read as the hour after midnight and the "
            "twin writes hours 1 to 12 only, as your table does. May be "
            "given more than once"
        ),
    )
    # -- 3b.R4 (P4-D384): numbers that are dates.
    parser.add_argument(
        "--date-count",
        action="append",
        nargs=2,
        default=None,
        metavar=("COLUMN", "SYSTEM"),
        help=(
            "name a column whose DATES ARE WRITTEN AS NUMBERS, and the "
            "system that counts them: excel-1900 (Excel serial days), "
            "excel-1904, days-since-1960 (SAS and Stata dates), "
            "seconds-since-1960 (SAS date-times), milliseconds-since-1960 "
            "(Stata), days-since-1970 (R), seconds-since-1970 (Unix), "
            "milliseconds-since-1970 (JavaScript), microseconds-since-1970, "
            "nanoseconds-since-1970, days-since-1840 (Epic, with a contact "
            "number after the point) or seconds-since-1582 (SPSS), as in "
            "--date-count visit_day excel-1900. A number does not say that "
            "it counts days, so synthtwin asks; named here, each cell is "
            "read as the date it counts, the column is described as dates, "
            "and the twin writes each date back as the same count. May be "
            "given more than once"
        ),
    )
    parser.add_argument(
        "--metadata-rows",
        default=None,
        metavar="N",
        help=(
            "say that the first N rows UNDER your column names describe "
            "those columns rather than holding a record. Some survey "
            "tools write two such rows -- the question wording, then a "
            "row of ImportId markers -- and a reader that takes them "
            "for data gets two rows of machine text mixed in with "
            "people's answers. Takes 0 or 2. Without it, every row "
            "under your column names is read as a record of your "
            "table: synthtwin recognises that shape and will SAY so, "
            "in the questions file and on the screen, but it never "
            "acts on it by itself, because a file it recognised "
            "wrongly would have two real records removed from every "
            "count and their values published as column descriptions"
        ),
    )
    parser.add_argument(
        "--delimiter",
        default=None,
        metavar="CHARACTER",
        help=(
            "say which character separates the columns of your file: "
            "',' ';' '|' or the word tab. synthtwin works this out by "
            "itself, and it asks rather than guesses where a file reads "
            "equally well two ways -- 'id,pair|code' over rows such as "
            "'1,2|3' is two columns under the comma and two different "
            "columns under the vertical bar, and nothing in the cells "
            "can say which is yours. Only for delimited text; a "
            "workbook has no such character"
        ),
    )
    parser.add_argument(
        "--answers",
        default=None,
        metavar="FILE",
        help=(
            "the questions file from an earlier run, with your answers "
            "written in. Every 'synthtwin profile' run writes one "
            "beside the description, named for your table and ending "
            "'-questions.json'. It lists the columns synthtwin could "
            "read more than one way, says what it saw in each and what "
            "it read each as, and offers the answers you can give. "
            "Open it, write an answer beside 'your_answer' for the "
            "columns you want to correct, save it, and name it here: "
            "your answers become the declarations, exactly as if you "
            "had typed --code, --identifier or --measurement for each "
            "of them. Columns you leave blank keep the reading "
            "synthtwin made. It is the same set of answers the "
            "questions on screen ask for, so it is the way to answer "
            "them when nobody is at the keyboard"
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
            "surrounding spaces and upper or lower case -- with one "
            "exception, NaT, which synthtwin matches exactly as written "
            "because ignoring its capitals would make it a person's "
            "name. In the settings "
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
            "say that dates in this table are written day first, so "
            "03/04/2024 is the 3rd of April. It reaches every shape "
            "whose day and month are both numbers -- written with "
            "slashes, written with dots, and written with a "
            "two-figure year -- because each of them leaves the same "
            "question open. It "
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
        "--sheet",
        default="",
        metavar="NAME",
        help=(
            "which sheet of a spreadsheet workbook holds your table, by "
            "its name. Without this, synthtwin reads the first sheet "
            "that is not hidden and says on screen which one it chose. "
            "That is not what a spreadsheet's own readers do -- they "
            "take the first sheet whatever its state, which on a "
            "workbook whose first sheet is a hidden notes page means "
            "they read the notes -- so if your table is on a different "
            "sheet, name it here. The name has to match the tab exactly, "
            "and if it has a space in it put quotation marks around it. "
            "This option does nothing for a delimited text file, which "
            "has only one table in it"
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
    code_named = args.code if args.code is not None else []
    measured_named = args.measurement if args.measurement is not None else []
    comma_named = (
        args.decimal_comma if args.decimal_comma is not None else []
    )
    # -- 3b.R4 (P4-D384)
    counted_named = args.date_count if args.date_count is not None else []
    twelve_named = args.twelve_hour if args.twelve_hour is not None else []
    century_named = args.century if args.century is not None else []
    date_named = args.date_column if args.date_column is not None else []
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
        smallest_group=(
            _SMALLEST_GROUP
            if args.smallest_group is None
            else int(args.smallest_group)
        ),
        floor_chosen=args.smallest_group is not None,
        identifiers=list(named),
        codes=list(code_named),
        measurements=list(measured_named),
        decimal_commas=list(comma_named),
        answers=args.answers,
        kept_values=list(kept),
        missing_values=list(declared_missing),
        first_row=f"{args.first_row}",
        day_first=bool(args.day_first),
        metadata_rows=(
            "" if args.metadata_rows is None else f"{args.metadata_rows}"
        ),
        delimiter=("" if args.delimiter is None else f"{args.delimiter}"),
        sheet=f"{args.sheet}",
        seed=f"{args.seed}",
        replace=bool(args.replace),
        date_counts=[list(pair) for pair in counted_named],
        twelve_hours=list(twelve_named),
        centuries=list(century_named),
        date_columns=list(date_named),
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
    answered: "tuple[str, ...]" = (),
) -> str:
    """What the description kept of the words the person typed.

    OR ANSWERED (review of lane R1, item 1): a code found again from an
    answer of `missing` in the questions file is a `--missing-value` the
    person never typed, and a notice calling it "words you typed" sends
    them looking for an option they did not give. ``answered`` holds
    those spellings; a word is counted as answered where its
    declaration identity is one of theirs, and the opening line says
    which way each word arrived.

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
    from_answers: "list[tuple[str, object]]" = []
    answered_as = [asking.declared_identity(one) for one in answered]
    for spelling, _column, _count in named:
        identity = asking.declared_identity(spelling)
        if identity in answered_as and identity not in from_answers:
            from_answers += [identity]
    typed_how = "You typed"
    if not from_answers:
        arrived = "you typed after --missing-value"
    elif len(from_answers) >= words:
        arrived = "your answers in the questions file declared missing"
        typed_how = "You named"
    else:
        arrived = (
            "you typed after --missing-value or your answers in the "
            "questions file declared missing"
        )
        typed_how = "You named"
    both = "" if len(named) == words else (
        f"\n\nWHY THERE ARE MORE LINES THAN WORDS. Your table wrote "
        f"{'the word you named' if one_word else 'some of the words you named'}"
        f" more than one way, and the description records each way "
        f"separately, because it has to say how each cell was spelled. "
        f"{typed_how} {'one word' if one_word else f'{words} words'}; the "
        f"rest of what you see above is your table's own spelling."
    )
    undo = (
        ""
        if not from_answers
        else ", or with your answer about the column they were found in "
        "changed back to 'keep'"
    )
    return (
        f"\n{_ALARM}\n"
        f"READ THIS BEFORE EITHER OF THESE FILES GOES ANYWHERE.\n"
        f"{'A word' if one_word else f'{words} words'} {arrived} "
        f"{'is' if one_word else 'are'} written into the "
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
        f"{'that word' if one_word else 'those words'}{undo}, or with "
        f"the cells already blank."
    )


_ANSWER_KEYS = {
    "1": asking.ANSWER_MEASUREMENT,
    "2": asking.ANSWER_CODE,
    "3": asking.ANSWER_IDENTIFIER,
    "4": asking.ANSWER_JOINED,
    "5": asking.ANSWER_DECIMAL_COMMA,
    # THE 12-HOUR ANSWER HAS ITS OWN KEY (landing T1, repair item 1).
    # Without one, the first column `asking._clock_question` offered it
    # on stopped an interactive run with a KeyError where the base read
    # the same column and asked nothing.
    "6": asking.ANSWER_TWELVE_HOUR,
    # -- 3b.R4 (P4-D384): QUESTION Q3'S TWELVE SYSTEMS, from 7 in the
    # table's own order, so a question offering any of them can be answered
    # at the keyboard as in the questions file.
    "7": date_counts.EXCEL_1900,
    "8": date_counts.EXCEL_1904,
    "9": date_counts.DAYS_SINCE_1960,
    "10": date_counts.SECONDS_SINCE_1960,
    "11": date_counts.MILLISECONDS_SINCE_1960,
    "12": date_counts.DAYS_SINCE_1970,
    "13": date_counts.SECONDS_SINCE_1970,
    "14": date_counts.MILLISECONDS_SINCE_1970,
    "15": date_counts.MICROSECONDS_SINCE_1970,
    "16": date_counts.NANOSECONDS_SINCE_1970,
    "17": date_counts.DAYS_SINCE_1840,
    "18": date_counts.SECONDS_SINCE_1582,
    "m": asking.ANSWER_MEASUREMENT,
    "c": asking.ANSWER_CODE,
    "i": asking.ANSWER_IDENTIFIER,
    "j": asking.ANSWER_JOINED,
    "d": asking.ANSWER_DECIMAL_COMMA,
    "t": asking.ANSWER_TWELVE_HOUR,
}

_WHY_SHOWN = {
    asking.BECAUSE_PADDED: (
        "some values carry a leading zero, and a measurement is not "
        "padded"
    ),
    asking.BECAUSE_FIXED_WIDTH: (
        "every value is the same number of digits, which a measurement "
        "rarely is"
    ),
    asking.BECAUSE_JOINED: (
        "every value is two or more numbers joined by one mark, "
        "which is how a blood pressure is written and also how a "
        "laboratory code is"
    ),
    asking.BECAUSE_GROUPED_FIXED_WIDTH: (
        "every value is the same number of figures, grouped in threes, "
        "which is how an identifier is written for reading"
    ),
    asking.BECAUSE_POINT_THOUSANDS: (
        "every value with a point has three figures after it, and every "
        "other value is below a thousand, which is also how a point "
        "between thousands is written"
    ),
    # WHY THE PERSON QUESTION IS BEING PUT (plan P4-D340). Its reason is
    # not that the column might be a code: it is that the column might
    # name the people the rows are about, which is a different question
    # with a different consequence, so it says so in its own words.
    asking.BECAUSE_REPEATS_AND_MANY: (
        "its values repeat, and there are either more of them than a "
        "set of categories could hold or every one of them is written "
        "as a code of letters and figures standing on two rows or "
        "more, which is how a column naming the people the rows are "
        "about is written, and no column at all was named with "
        "--identifier"
    ),
}


def _there_is_somebody_to_ask() -> bool:
    """True where a person is at the keyboard to answer.

    Guarantees:

    - Determinism: not deterministic -- it reads the environment the
      command was started in, which is the one thing here that is not
      a function of the arguments. Nothing it decides reaches the
      profile: a question that is not asked becomes a printed
      assumption, and the description is identical either way.
    - Errors raised: none. A handle that cannot answer `isatty` is
      taken as nobody there, which is the safe reading.

    BOTH HANDLES ARE TESTED, not just the input. A run whose output is
    piped to a file is a scripted run even when its input is a
    terminal, and stopping it to ask a question would hang a pipeline
    with the question sitting unread in the file.
    """
    try:
        return bool(os.isatty(0)) and bool(os.isatty(1))
    except (OSError, ValueError):
        return False


def _joined(parts: "list[str]", separator: str) -> str:
    """Join text the long way round, for the offline audit's reason.

    `str.join` runs the formatting protocol of whatever it is handed,
    so the audit accepts only literals and values it watched being
    built. Every part here is gated as text and added one at a time.
    """
    out = ""
    for part in parts:
        if not isinstance(part, str):
            raise TypeError("a part must be text")
        out = out + (separator if out else "") + part
    return out


_KEY_OF = {
    asking.ANSWER_MEASUREMENT: "1",
    asking.ANSWER_CODE: "2",
    asking.ANSWER_IDENTIFIER: "3",
    asking.ANSWER_JOINED: "4",
    asking.ANSWER_DECIMAL_COMMA: "5",
    asking.ANSWER_TWELVE_HOUR: "6",
    # -- 3b.R4 (P4-D384)
    date_counts.EXCEL_1900: "7",
    date_counts.EXCEL_1904: "8",
    date_counts.DAYS_SINCE_1960: "9",
    date_counts.SECONDS_SINCE_1960: "10",
    date_counts.MILLISECONDS_SINCE_1960: "11",
    date_counts.DAYS_SINCE_1970: "12",
    date_counts.SECONDS_SINCE_1970: "13",
    date_counts.MILLISECONDS_SINCE_1970: "14",
    date_counts.MICROSECONDS_SINCE_1970: "15",
    date_counts.NANOSECONDS_SINCE_1970: "16",
    date_counts.DAYS_SINCE_1840: "17",
    date_counts.SECONDS_SINCE_1582: "18",
    # THE STANDING READING SHARES KEY 1 WITH `measurement`, and the two
    # never appear on one question: a column of figures offers
    # `measurement` as the reading it already has, and a joined-looking
    # column offers `keep`, which is the reading IT already has. Both
    # mean "make no declaration", and `_put_the_questions` gives
    # neither a branch, so they are one behaviour under two words --
    # the words differing because what a person is keeping differs.
    asking.ANSWER_KEEP: "1",
}


def _the_question(question: asking.Question, place: int, total: int) -> str:
    """One column's question, as the person sees it.

    IT RENDERS THE QUESTION'S OWN DATA AND WRITES NONE OF ITS OWN
    (amendment A-P4-58). The choices, what each publishes, and the
    reading that stands if nobody answers are `asking.Question`'s, so
    the questions file and this screen ask ONE question rather than two
    that drift; Phase 7 renders the same object again.

    AND IT SHOWS NO VALUE OF THE TABLE (owner ruling 2026-09-10). It
    printed four real cells until then, on the argument that the
    question is unanswerable without them. It is answerable: the shape
    says what synthtwin saw -- "every value is written in figures
    alone, all five characters wide" -- and says it in words that may
    travel where a cell may not. Showing values here while the file
    withholds them would make one question into two.
    """
    lines = ""
    for choice in question.choices:
        key = _KEY_OF[choice.answer]
        lines = lines + (
            f"\n      [{key}] {choice.means}\n"
            f"          then the description publishes {choice.publishes}"
        )
    return (
        f"\n  Column {place} of {total}: '{_shown(question.name)}'\n"
        f"    what synthtwin saw: {question.shape}.\n"
        f"    What does this column hold?{lines}\n"
        f"    Press Enter to keep the reading synthtwin made, "
        f"which is the first one above."
    )


def _metadata_rows_unseen_notice(rows: int) -> str:
    """What is said when such rows are declared on a file not wearing the shape.

    The declaration exists for a survey export whose rows under the
    column names describe those columns. Given on any other file it
    USED to take those rows out of the table and publish them as
    schema -- text held to no smallest group, written into the twin as
    it stands. Measured on an ordinary table of 120 records:
    `--metadata-rows 2` published two people's records verbatim at a
    floor of eleven, dropped them from every count, and nothing but
    this notice questioned it.

    THAT IS NO LONGER WHAT HAPPENS (review of landing 2b.17, MAJOR).
    A notice is not a safeguard: it is read after the description has
    been written, by a person who has already made the mistake, and
    the disclosure it describes has happened by the time they read it.
    So the rows now STAY in the table -- the safe reading the contract
    already names for a declaration that found nothing -- and this
    notice says so and says how to confirm the declaration in the
    questions file if the person means it. The reading still obeys the
    person; what it no longer does is obey a declaration the file
    contradicts without asking them first.
    """
    return (
        f"{'=' * 66}\n"
        f"YOUR FILE DOES NOT WEAR THE SHAPE --metadata-rows IS FOR\n"
        f"{'=' * 66}\n"
        f"You said the {rows} row(s) under your column names describe "
        f"those columns. What synthtwin looked for and did not see is "
        f"the shape such a file usually has: rows as wide as your "
        f"table whose second holds a marker in every cell. So those "
        f"{rows} rows have STAYED in your table: they are counted "
        f"among your rows, described as data like every other record, "
        f"and nothing they hold is published anywhere in your "
        f"description. If they really do describe your columns, say so "
        f"in the questions file this run writes -- answer "
        f"'metadata-rows' under 'about_your_file', then describe the "
        f"table again with --answers -- and they will be taken out of "
        f"the table and published as written. You are asked rather "
        f"than taken at your word here because on a file this "
        f"declaration is wrong about, those rows are somebody's "
        f"records, and publishing one of those cannot be undone."
    )


# How `--delimiter` may be typed (plan P4-D110). A tab is hard to type
# on most command lines, so the word stands for it beside the character.
_DELIMITER_SPELLINGS = {
    ",": ",",
    ";": ";",
    "|": "|",
    "\t": "\t",
    "tab": "\t",
}


def _answers_that_change_the_reading(
    written: asking.Answers, first_row: str, declared_delimiter: str
) -> "list[str]":
    """Which answers of a questions file change HOW THE FILE IS READ.

    The subjects, in the questions file's own words, of the answers that
    give the same column name to a different column (review of stage 3,
    floor item 1). Two of the three file questions do that:

    * WHICH ROW HOLDS THE COLUMN NAMES. Under one reading the names come
      out of the file's first row; under the other they are generated,
      `column_1`, `column_2` and so on. Every name moves, and `column_1`
      exists under both readings.
    * WHICH CHARACTER SEPARATES THE COLUMNS. It decides how many columns
      there are and where each one begins, so a name may move, may be
      the name of a wider column, or may not be a name at all.

    The third, how many rows under the names describe the columns, takes
    ROWS out of the table and leaves every column where it was, so it is
    not here.

    AN ANSWER THAT AGREES WITH WHAT WAS TYPED CHANGES NOTHING and is not
    reported: `--first-row names` answered `names`, or `--delimiter ';'`
    answered `semicolon`, is the reading already in force. A delimiter
    answered where none was typed IS a change, because the reading in
    force was the one the cells favoured and nothing here can know which
    that was -- the answers are read before the table is opened, which
    is what makes them usable at all.

    Guarantees: accepts the answers read back from the file, the
    `--first-row` option as typed and the delimiter as typed (empty
    where none was); returns the subjects in the order the questions
    file writes them. A fixed function of the three. Raises nothing,
    opens no file, and carries no value of the table -- the subjects are
    this module's own question headings.
    """
    changed: "list[str]" = []
    if written.first_row == asking.ANSWER_FIRST_ROW_NAMES:
        if first_row != _FIRST_ROW_NAMES:
            changed += [asking.FIRST_ROW_SUBJECT]
    elif written.first_row == asking.ANSWER_FIRST_ROW_DATA:
        if first_row == _FIRST_ROW_NAMES:
            changed += [asking.FIRST_ROW_SUBJECT]
    if written.delimiter and written.delimiter != declared_delimiter:
        changed += [asking.DELIMITER_SUBJECT]
    return changed


def _delimiter_tie_notice(tied: "tuple[str, ...]") -> str:
    """What is said about a file that reads equally well two ways.

    It names the delimiters, never a cell: which character separates the
    columns is a fact about the file, and the reading taken is the one
    the file would have had anyway (review item CODEX-4).

    AND THE REASON IT GIVES IS THE REASON THE WALK USED (the repair of
    the skeptic's finding 2 on P4-D282). This sentence said synthtwin
    had taken "the reading under which more of the values read as
    numbers", and that was true while a competitor had to agree about
    the WIDTH to be reported at all -- `dialect.delimiter_reading` asks
    the count of numbers only where the share AND the width tie. P4-D282
    widened the competitor to any reading of the winner's own share, so
    the sentence began to be printed about files the width alone
    settled. MEASURED on the tree carrying P4-D282: a header
    `id,note|tagA|tagB` over 120 rows `{i},alpha{i}|x{i}|y{i}` reads at
    a share of 1.0 under both, two columns and 120 values read as
    numbers under the comma, three columns and NOUGHT under the vertical
    bar; the bar wins on the width, and the person was told it won
    because more of the values read as numbers -- false by 120 to 0, in
    the one sentence that tells them whether to override the reading.
    The order is now stated as the walk has it: the wider reading, and
    the count of numbers only between readings of one width.

    AND A READING WHOSE FIRST ROW IS AS WIDE AS ITS ROWS COMES FIRST
    (Codex's review of landing R5, item 1). `dialect.delimiter_reading`
    takes such a reading before one that lines the first row up only by
    reading a delimiter at the end of a line as closing it, and records
    the lined-up reading as the competitor; the sentence says so, because
    on `id,notes,measure;type;unit;` over rows `i,x;y;z,6` the two
    readings give three columns each and the comma was not taken for
    its numbers.
    """
    others = ""
    for one in tied[1:]:
        others = (
            dialect.DELIMITER_WORDS[one]
            if not others
            else f"{others} or with {dialect.DELIMITER_WORDS[one]}"
        )
    return (
        f"{'=' * 66}\n"
        f"YOUR FILE READS EQUALLY WELL WITH MORE THAN ONE DELIMITER\n"
        f"{'=' * 66}\n"
        f"Every record of your file splits cleanly, into one steady "
        f"number of columns, whether it is read with "
        f"{dialect.DELIMITER_WORDS[tied[0]]} or with "
        f"{others} -- and the two readings need not give your table the "
        f"same number of columns at all. Nothing in the values can say "
        f"which your file uses. synthtwin has read it with "
        f"{dialect.DELIMITER_WORDS[tied[0]]}: a reading under which "
        f"the first row has as many fields as the rows below it most "
        f"often have is taken before one that lines them up only by "
        f"reading a delimiter at the end of a line as closing it; then "
        f"the reading that gives your table the most columns; where two "
        f"readings give it the same number of columns, the one under "
        f"which more of the values read as numbers is taken. If that is "
        f"not how your "
        f"file is written, describe the table again with --delimiter, "
        f"or answer the question under 'about_your_file' in the "
        f"questions file this run writes: your column names, and every "
        f"column's values, depend on it."
    )


def _metadata_rows_notice() -> str:
    """What is said about a file wearing a survey export's shape.

    It names what was SEEN, what was done about it (nothing), and the
    one option that changes it. The shape is not evidence: a table
    whose first record happens to be as wide as its header with a row
    of markers under it wears it too, and acting on the resemblance is
    how a person's own record became schema text (review item
    CODEX-2).
    """
    return (
        f"{'=' * 66}\n"
        f"THE TWO ROWS UNDER YOUR COLUMN NAMES MAY DESCRIBE THE COLUMNS\n"
        f"{'=' * 66}\n"
        f"They are each as wide as your table and every cell of the "
        f"second is an ImportId marker, which is the shape some survey "
        f"tools write to describe their columns. synthtwin has read "
        f"them as RECORDS of your table, because that is what a row "
        f"under the column names is unless you say otherwise, and "
        f"because a file this shape was recognised wrongly in would "
        f"have two real records taken out of every count and their "
        f"values published as column descriptions. If those two rows "
        f"do describe your columns, describe the table again with "
        f"--metadata-rows 2, or answer the question under "
        f"'about_your_file' in the questions file this run writes."
    )


def _checklist_notice(listed: "list[asking.Question]") -> str:
    """Every column read as a number, under ONE question.

    THE COLUMNS NOTHING ELSE REACHES (owner ruling 2026-09-10, decision
    D14). The questions beside this are the ones whose VALUES raised
    one. A register of drug concept identifiers six and seven figures
    wide raises nothing and can raise nothing -- it is written exactly
    as a column of ages is, and the rule that tried to tell them apart
    was deleted for guessing in review item P1-R6-F7. What reaches such
    a column is a person reading a list of their own columns, and
    nothing else ever will.

    ONE QUESTION AND NOT ONE PER COLUMN, which keeps it from being a
    burden (amendment A-P4-56 point 1): twelve columns under one
    question is a minute's reading, and twelve separate questions is a
    form nobody finishes.

    IT IS SHOWN ONCE PER RUN AND ON ITS OWN (review round 1, item 1).
    It hung off the scripted notice, which fires only where a column's
    values raised a question AND only where nobody is at the keyboard,
    so three of the four ways a person runs this command never saw it
    -- and a table whose only finding was this list showed nothing at
    all.
    """
    rows = ""
    for question in listed:
        rows = rows + f"\n  '{_shown(question.name)}' -- {question.shape}"
    return (
        f"{asking.CHECKLIST_HEADING}{rows}\n\n"
        f"Nothing in these columns' values can tell a coding system "
        f"from a measurement -- a code register and a column of counts "
        f"are written identically -- so they raised no question of "
        f"their own. Only you know which is which. Name any that hold "
        f"codes with --code, and any that hold record numbers with "
        f"--identifier. Nothing is wrong with this profile if they are "
        f"already read the way you meant."
    )


def _date_codes_notice(questions: "list[asking.Question]") -> str:
    """What is said about columns of dates or times beside a few codes (plan P4-D381).

    THE SHAPE, NOT THE VALUES, for the reason every question here gives
    (owner ruling 2026-09-10): the questions file may not name a code,
    so neither may the screen, or one question would be asked two ways.
    What it names is the column, what synthtwin saw in it, and the two
    ways to say the codes stand for a missing date or time -- the answer
    in the file, which finds them again, or `--missing-value` naming
    each, for a person who knows them.
    """
    rows = ""
    for question in questions:
        rows = rows + f"\n  '{_shown(question.name)}' -- {question.shape}"
    return (
        f"{'=' * 66}\n"
        f"THESE COLUMNS READ AS DATES OR TIMES BUT FOR A FEW REPEATED "
        f"SPELLINGS\n"
        f"{'=' * 66}{rows}\n\n"
        f"Those spellings keep each column above from being read as dates "
        f"or times, so it is described the way it reads with them in it, "
        f"and many of its twin's cells will not read as dates or times. If "
        f"they stand for a date or time nobody wrote down -- unknown, not "
        f"recorded or not applicable -- answer 'missing' for the column "
        f"under 'asked' in the questions file this run writes, and "
        f"describe the table again with --answers: the column is then "
        f"read as dates or times, and the spellings are counted as "
        f"missing and written back in the twin as your table writes them. "
        f"Naming each spelling with --missing-value does the same, in "
        f"every column of your table. Nothing is wrong with this profile "
        f"if they really are values of their own."
    )


def _century_notice(questions: "list[asking.Question]") -> str:
    """What is said about columns of dates whose years are two figures (landing R2a).

    Question Q5's own words, put in the questions file and said here, as
    the date questions of plan P4-D381 are: each column, what synthtwin saw
    and the two ways to place its years in another century.
    """
    rows = ""
    for question in questions:
        rows = rows + f"\n  '{_shown(question.name)}'"
    return (
        f"{'=' * 66}\n"
        f"THESE COLUMNS WRITE THEIR YEARS WITH TWO FIGURES\n"
        f"{'=' * 66}{rows}\n\n"
        f"Two figures do not say which century a year is in, so synthtwin "
        f"has read them as 1969 to 2068: 24 is 2024 and 75 is 1975. If a "
        f"column's years lie elsewhere -- birth dates before 1969 are the "
        f"commonest case -- answer '1930-2029', '1940-2039' or '1900-1999' "
        f"for it under 'asked' in the questions file this run writes and "
        f"describe the table again with --answers, or describe it again "
        f"with --century, as in --century birth_date=1930."
    )


def _date_column_notice(questions: "list[asking.Question]") -> str:
    """What is said about columns mostly of dates (landing R2c, question Q6).

    Question Q6's own words, put in the questions file and said here, as
    Q5's are: each column, and the two ways to have it read as dates.
    """
    rows = ""
    for question in questions:
        rows = rows + f"\n  '{_shown(question.name)}'"
    return (
        f"{'=' * 66}\n"
        f"THESE COLUMNS MAY HOLD DATES\n"
        f"{'=' * 66}{rows}\n\n"
        f"Half of these values or more read as dates, but not enough for "
        f"synthtwin to read the column as dates on its own, or they are "
        f"written as a year and a day of the year, which a record number "
        f"is too. If a column holds dates, answer 'dates' for it under "
        f"'asked' in the questions file this run writes and describe the "
        f"table again with --answers, or describe it again with "
        f"--date-column, as in --date-column visit_date. Its other values "
        f"are then left unread, and the twin writes them as made-up text."
    )


def _day_or_month_notice(found: "tuple[asking.DayOrMonth, ...]") -> str:
    """What is said where no value of a column of dates says which comes first (plan P4-D381).

    It is the questions file's own sentence, rendered from the question
    `asking.file_questions` puts, so the screen and the file ask one
    question in one set of words.
    """
    asked = asking.file_questions(False, day_or_month=found)
    seen = asked[0].shape if asked else ""
    return (
        f"{'=' * 66}\n"
        f"THE ORDER OF THE DAY AND THE MONTH CANNOT BE TOLD FROM SOME DATES\n"
        f"{'=' * 66}\n"
        f"What synthtwin saw: {_shown(seen)}.\n\n"
        f"synthtwin has read them month first, so 03/04/2024 is the 4th "
        f"of March. If your file writes the day first, describe the table "
        f"again with --day-first, or answer 'day-first' under "
        f"'about_your_file' in the questions file this run writes: every "
        f"such column is then read day first, and its twin writes its "
        f"dates the same way."
    )


def _offers(question: asking.Question, answer: str) -> bool:
    """Whether one question offers one answer among its choices."""
    for choice in question.choices:
        if choice.answer == answer:
            return True
    return False


def _clock_notice(clocks: "list[asking.Question]", listing: str) -> str:
    """The scripted run's block for columns read as times of day (the T1 review's item 8).

    Each column is offered what its own question offers: `--twelve-hour`
    where every hour lies in 1 to 12 with no AM or PM, `--measurement`
    where an hour in one figure makes the cell two numbers joined by a
    colon, and `--code` where few times each shared by many rows may be
    labels written as times (landing 3b.5, plan P4-D373), never for the
    colon question's codes written in parts (the T1 review's item 8).
    Guarantees: a function of the questions and their listing; raises
    nothing; opens nothing.
    """
    twelve = [one for one in clocks if _offers(one, asking.ANSWER_TWELVE_HOUR)]
    joined = [one for one in clocks if _offers(one, asking.ANSWER_JOINED)]
    codes = [one for one in clocks if asking.offers_labels_written_as_times(one)]
    said = (
        f"THESE COLUMNS WERE READ AS TIMES OF DAY, AND MIGHT BE READ "
        f"ANOTHER WAY.{listing}\n\n"
        f"Each column above is described as times of day on a 24-hour "
        f"clock -- alone, or after a date -- with points along the day and "
        f"the two tails beyond them, and its twin writes its times the way "
        f"your table does."
    )
    if twelve:
        flags = _joined(
            [f"--twelve-hour {_shown(one.name)}" for one in twelve], " "
        )
        said = said + (
            f" Where every hour lies from 1 to 12 and no cell writes AM or "
            f"PM, a 12-hour clock writes the same cells, and 12:15 is then "
            f"a quarter past midnight rather than past noon; only you know "
            f"which clock wrote them.\n\n"
            f"If any of them is a 12-hour clock, run the command again "
            f"naming it:\n  {flags}"
        )
    if joined:
        flags = _joined(
            [f"--measurement {_shown(one.name)}" for one in joined], " "
        )
        said = said + (
            f"\n\nA time whose hour is written in one figure is also two "
            f"numbers joined by a colon, which is how a duration in minutes "
            f"and seconds is written. If any of them holds such numbers, "
            f"run the command again naming it:\n  {flags}"
        )
    if codes:
        flags = _joined([_typed_option("--code", one.name) for one in codes], " ")
        said = said + (
            f"\n\nA few times each shared by many rows can also be labels "
            f"written as times, each naming a group rather than a moment -- "
            f"a shift called by when it starts. If any of them holds such "
            f"labels, run the command again naming it:\n  "
            f"{flags}{_quoting_said(flags)}"
        )
    return said


def _assumptions_notice(questions: "list[asking.Question]") -> str:
    """What is printed where there is nobody to ask.

    The person chose the tool; they did not choose to be guessed at.
    This says what was assumed and the exact words that correct it, so
    a scripted run is one rerun away from right rather than silently
    wrong.
    """
    # THE SENTENCE IS PER REASON, BECAUSE ONE SENTENCE WAS FALSE OF
    # HALF THE COLUMNS IT REACHED (landing L16). This said every column
    # above "is being described with an average, a smallest and a
    # largest", and the joined reason fires on columns that reached a
    # LABEL role -- a hyphenated laboratory code publishing no numeric
    # statistic at all was told its codes were being averaged. A false
    # sentence on the honesty surface is the defect principle 6 names,
    # and it reached the screen because nothing tests this text.
    numeric: list[asking.Question] = []
    joined: list[asking.Question] = []
    # A JOINED-LOOKING COLUMN ALREADY READ AS JOINED NUMBERS (plan
    # P4-D40) is not being described as text, and telling it so would
    # be the false sentence the comment above records once already.
    paired: list[asking.Question] = []
    pointed: list[asking.Question] = []
    # ...AND THE ONE QUESTION THAT IS NOT ABOUT A READING AT ALL (plan
    # P4-D340). It asks who the rows are about, and falling through to
    # the numeric block told a person their subject number was being
    # averaged and offered them `--code`, which is the wrong answer to
    # a question nobody had asked them.
    people: list[asking.Question] = []
    # ...AND A COLUMN READ AS TIMES OF DAY (the T1 review's item 8). Its
    # question is the 12-hour one, or the colon one a clock in one figure
    # keeps, and falling through put the first under "read as
    # measurements" with `--code`, and the second under "described as
    # text", though both are read as times of day. Its block offers what
    # its own question offers.
    clocks: list[asking.Question] = []
    # -- 3b.R4 (P4-D384): ...AND A COLUMN OF NUMBERS LYING WHERE A COUNTING
    # SYSTEM WRITES DATES (question Q3), which is told what it would gain
    # as dates and the option that reads it so.
    dated: list[asking.Question] = []
    for question in questions:
        if asking.asks_about_a_clock(question):
            clocks += [question]
        elif question.reason == asking.BECAUSE_DATE_COUNTS:
            dated += [question]
        elif question.reason == asking.BECAUSE_JOINED:
            if asking.reads_each_number(question.role):
                paired += [question]
            else:
                joined += [question]
        elif question.reason == asking.BECAUSE_POINT_THOUSANDS:
            pointed += [question]
        elif question.reason == asking.BECAUSE_REPEATS_AND_MANY:
            people += [question]
        else:
            numeric += [question]

    def _listing(group: "list[asking.Question]", say_what: bool) -> str:
        shown = ""
        for question in group:
            # THE SHAPE, NOT THE VALUES (owner ruling 2026-09-10).
            # This listed four real cells beside every column
            # name; the questions file may not, and one question
            # asked two ways is two questions.
            line = (
                f"\n  '{_shown(question.name)}' -- "
                f"{question.shape}"
            )
            if say_what:
                # WHAT THAT COLUMN ACTUALLY PUBLISHES, per column
                # (review round 1 of landing L16, item 2). One sentence
                # covered the whole group and said its values "are kept
                # as they are written"; a column of three hundred
                # different readings reaches free text, which publishes
                # no value of it at all, and the notice said the
                # opposite of the profile sitting beside it.
                if asking.reads_each_number(question.role):
                    line = line + (
                        "\n      (each number in its cells is described "
                        "on its own, and no whole cell is published)"
                    )
                elif not asking.publishes_its_values(question.role):
                    line = line + (
                        "\n      (no value of this column is published)"
                    )
                else:
                    line = line + (
                        "\n      (its values are published as they are "
                        "written, under the smallest-group size in force)"
                    )
            shown = shown + line
        return shown

    blocks: list[str] = []
    if clocks:
        blocks += [_clock_notice(clocks, _listing(clocks, False))]
    if dated:
        flags = _joined(
            [f"{_typed_option('--date-count', one.name)} SYSTEM" for one in dated],
            " ",
        )
        blocks += [
            f"THESE COLUMNS WERE READ AS NUMBERS, AND MIGHT BE DATES WRITTEN "
            f"AS COUNTS.{_listing(dated, False)}\n\n"
            f"Each column above lies where a system that counts days, "
            f"seconds or a finer unit from a fixed day writes dates, and was "
            f"read as numbers: its twin keeps how the numbers spread, but "
            f"not the day of the week or the time of day each date falls "
            f"on. Only you know whether they are dates.\n\n"
            f"If any of them holds dates, run the command again naming it "
            f"and the system it is counted in -- one of those named beside "
            f"it above:\n  {flags}{_quoting_said(flags)}"
        ]
    if numeric:
        flags = _joined(
            [_typed_option("--code", one.name) for one in numeric], " "
        )
        blocks += [
            f"THESE COLUMNS WERE READ AS MEASUREMENTS, AND MIGHT BE CODES."
            f"{_listing(numeric, False)}\n\n"
            f"synthtwin cannot tell a coding system from a measurement: "
            f"they are written identically, and only you know which this "
            f"is. Each column above is being described with an average, a "
            f"spread and points along its range -- which for a code are "
            f"meaningless, and whose published boundaries are real codes "
            f"besides -- and its twin will lose any "
            f"leading zeros.\n\n"
            f"If any of them holds codes, run the command again naming "
            f"them:\n  {flags}{_quoting_said(flags)}"
        ]
    if joined:
        flags = _joined(
            [_typed_option("--measurement", one.name) for one in joined], " "
        )
        blocks += [
            f"THESE COLUMNS HOLD TWO NUMBERS IN ONE CELL, AND MIGHT BE "
            f"READINGS.{_listing(joined, True)}\n\n"
            f"Each column above is being described as text rather than as "
            f"numbers, so NO number inside those cells is described: no "
            f"average, no smallest, no largest, and the twin's cells are "
            f"built from what is published beside each column above. A "
            f"blood pressure of `120/80` is two readings and a laboratory "
            f"code is not, and only you know which this is.\n\n"
            f"If any of them holds readings, run the command again naming "
            f"them:\n  {flags}{_quoting_said(flags)}"
        ]
    if paired:
        flags = _joined(
            [_typed_option("--code", one.name) for one in paired], " "
        )
        blocks += [
            f"THESE COLUMNS HOLD TWO NUMBERS IN ONE CELL, AND WERE READ AS "
            f"READINGS.{_listing(paired, True)}\n\n"
            f"Each number inside those cells is described on its own, with "
            f"its own average, spread and points along its range -- and "
            f"its own two ends only where a group of rows shares them -- "
            f"and the twin's cells "
            f"are built from those. A blood pressure of `120/80` is two "
            f"readings and a register written as two numbers is not, and "
            f"only you know which this is.\n\n"
            f"If any of them holds codes, run the command again naming "
            f"them:\n  {flags}{_quoting_said(flags)}"
        ]
    if pointed:
        flags = _joined(
            [_typed_option("--decimal-comma", one.name) for one in pointed], " "
        )
        blocks += [
            f"THESE COLUMNS WERE READ WITH A DECIMAL POINT, AND MIGHT BE "
            f"WRITTEN WITH A POINT BETWEEN THOUSANDS.{_listing(pointed, False)}"
            f"\n\n"
            f"Each column above is being described with its point as a "
            f"decimal point. If the point is a mark between thousands, "
            f"every average, spread and published point of it is a "
            f"thousand times too small, and only you know which it is.\n\n"
            f"If any of them writes a point between thousands, run the "
            f"command again naming them:\n  {flags}{_quoting_said(flags)}"
        ]
    if people:
        flags = _joined(
            [_typed_option("--identifier", one.name) for one in people], " "
        )
        blocks += [
            f"THESE COLUMNS MIGHT NAME THE PEOPLE YOUR ROWS ARE ABOUT."
            f"{_listing(people, False)}\n\n"
            f"No column that names PEOPLE has been declared, so this "
            f"table's population was counted in ROWS. If one row is one "
            f"visit rather than one person, that count is larger than "
            f"the number of people in the table, and synthtwin cannot "
            f"tell which it is: a column whose values repeat can be a "
            f"subject number or a ward.\n\n"
            f"If any of them names people, run the command again naming "
            f"them:\n  {flags}{_quoting_said(flags)}"
        ]
    # `_joined` rather than `str.join`, for the offline audit's reason:
    # the formatting protocol of whatever is handed to `join` runs, so
    # the audit accepts only literals and values it watched being built.
    return (
        _joined(blocks, "\n\n")
        + "\nNothing is wrong with this profile if they really are "
        + "what synthtwin read them as."
    )


def _cleaned(line: str) -> str:
    """One typed line, trimmed and lowered.

    The type gate is the offline audit's: what `input` returns is not
    traceable to an allowlisted API, so it is checked as text here
    before any method of it is called.
    """
    if not isinstance(line, str):
        raise TypeError("a typed line must be text")
    return line.strip().lower()


def _read_one_answer(standing: str = asking.ANSWER_MEASUREMENT) -> "str | None":
    """One typed answer, or None where the person ended the run.

    Enter alone keeps the reading synthtwin already made, so a person
    who does not know can press through and lose nothing they had.
    Anything unrecognized is asked again rather than assumed: this is
    the one place a wrong guess would be recorded in the profile as a
    fact the person had stated.
    """
    while True:
        try:
            line = input("    > ")
        except (EOFError, KeyboardInterrupt):
            return None
        typed = _cleaned(line)
        if not typed:
            # ...and what it keeps is THIS question's standing reading,
            # not a fixed one (review round 1 of landing L17a, item 3).
            # A joined-looking column's standing reading is the text or
            # label reading it already has; returning `measurement`
            # there named a reading Enter does not give.
            return standing
        if typed in _ANSWER_KEYS:
            return _ANSWER_KEYS[typed]
        _say(
            "    Please type one of the numbers offered, or press Enter "
            "to keep the reading synthtwin made."
        )


def _style_held_back(column: "dict[str, object]") -> bool:
    """Whether a slashed stamp's one written-clock word was pooled (the T1 review's item 9).

    Its census of marks is `(withheld)` alone, so the description names
    no written clock -- which is not the same as a declaration that
    reached nothing: where the clocks write no marker
    (`_clocks_on_the_declared_face`), `--twelve-hour` was honoured in
    reading them, and only the word saying so is too rare to print.
    """
    if "format" not in column or f"{column['format']}" not in parsing.SLASHED_STAMPS:
        return False
    census = column["datetime_separators"] if "datetime_separators" in column else None
    if not isinstance(census, dict) or not census:
        return False
    for word in census:
        if f"{word}" != "(withheld)":
            return False
    return True


def _clocks_on_the_declared_face(cells: "list[str]") -> bool:
    """Whether a declared column's clocks are read on the 12-hour face with no marker.

    THE PRODUCER'S OWN RULE (`parsing.clock_style_of_cells`): the face
    most of the clocks write, a column declared a 12-hour clock reading
    its unmarked ones on that face. Asked of a declared slashed stamp
    whose written-clock word was pooled (`_style_held_back`), whose
    description cannot say it: ten stamps written `1:00 PM` beside
    ninety `NA` were told `--twelve-hour` was used and to keep it, where
    a marked clock is one the declaration does not change -- the other
    half of the T1 review's item 9.

    Guarantees: accepts the column's cells as written; returns whether
    some clock half reads and most of them write no marker. Determinism:
    a function of the cells. Raises nothing. No I/O.
    """
    read: "list[tuple[int, int, int, bool, int, str, bool]]" = []
    for cell in cells:
        parts = parsing.clock_parts(parsing.stamp_halves(cell)[1])
        if parts is not None:
            read += [parts]
    if not read:
        return False
    style = parsing.clock_style_of_cells(read, True)
    return parsing.clock_face(style) == parsing.CLOCK_TWELVE_HOUR


def _read_on_twelve_hours(column: "dict[str, object]") -> bool:
    """Whether a described column was read on the declared 12-hour face."""
    style = ""
    # -- 3b.R2b (P4-D383): a layout says its own clock in its format.
    if "format" in column and parsing.is_layout_name(f"{column['format']}"):
        found = parsing.layout_clock_style(f"{column['format']}")
        return found is not None and parsing.clock_face(found) == parsing.CLOCK_TWELVE_HOUR
    if column["role"] == "time_of_day":
        form = f"{column['clock_form']}"
        if form in parsing.CLOCK_FORMS:
            style = parsing.clock_style_of(form)
    elif "datetime_separators" in column:
        census = column["datetime_separators"]
        if isinstance(census, dict):
            for word in census:
                found = parsing.stamp_style(f"{word}")
                if found is not None:
                    style = found
    return bool(style) and parsing.clock_face(style) == parsing.CLOCK_TWELVE_HOUR


def _offered_here(answer: str, question: asking.Question) -> bool:
    """Whether one typed answer is one this question offers.

    Guarantees: a fixed function of the two; raises nothing; opens
    nothing. The reading Enter keeps (`question.taken`) is always taken,
    and so is anything that is no column answer at all, which no key
    reaches. `measurement` stands for `keep` where the question offers
    `keep`, because the two share key 1 (see `_KEY_OF`).
    """
    if answer == question.taken:
        return True
    reached = False
    for key in _ANSWER_KEYS:
        if _ANSWER_KEYS[key] == answer:
            reached = True
    if not reached:
        return True
    offered = [choice.answer for choice in question.choices]
    if answer in offered:
        return True
    return answer == asking.ANSWER_MEASUREMENT and asking.ANSWER_KEEP in offered


def _century_given(typed: str) -> "tuple[str, int] | None":
    """One `--century COLUMN=YEAR` read, or None where it is not that (landing R2a).

    Split at the LAST equals sign, since a column's name may hold one; the
    year is one of the three a description may declare or the 1969 that
    stands where nothing is declared.
    """
    if not isinstance(typed, str):
        raise TypeError("a typed option reached the reader as something else")
    cut = len(typed) - 1
    while cut >= 0 and typed[cut] != "=":
        cut = cut - 1
    if cut < 1:
        return None
    name = typed[0:cut]
    year = typed[cut + 1 :]
    if not parsing.is_digit_text(year):
        return None
    first_year = int(year)
    if (
        first_year not in parsing.CENTURY_WINDOW_YEARS
        and first_year != parsing.CENTURY_DEFAULT_FIRST_YEAR
    ):
        return None
    return name, first_year


def _put_the_questions(
    questions: "list[asking.Question]",
) -> "tuple[list[str], list[str], list[str], list[str], list[str], list[tuple[str, str]]] | None":
    """Put every question; return the columns named as codes and as IDs.

    None where the person ended the run at a prompt: Ctrl-C and Ctrl-D
    mean stop, and stopping must not write a profile built on half an
    interview.
    """
    total = len(questions)
    _say(
        f"\n{'=' * 66}\n"
        f"{total} COLUMN(S) CAN BE READ MORE THAN ONE WAY\n"
        f"{'=' * 66}\n"
        f"synthtwin cannot tell a coding system from a measurement -- "
        f"they are written identically, and only you know which these "
        f"are. Press Enter to keep the reading it made. Your answers "
        f"are recorded in the profile, and the exact "
        f"options to repeat this run without typing are printed at the "
        f"end."
    )
    codes: list[str] = []
    identifiers: list[str] = []
    measurements: list[str] = []
    commas: list[str] = []
    twelve: list[str] = []
    # -- 3b.R4 (P4-D384): the columns answered with a counting system.
    counted: "list[tuple[str, str]]" = []
    place = 0
    for question in questions:
        place = place + 1
        _say(_the_question(question, place, total))
        answer = _read_one_answer(question.taken)
        # ONLY AN ANSWER THIS QUESTION OFFERS IS TAKEN (landing T1, its
        # second skeptic's item 2). `_read_one_answer` knows every key,
        # so `6` typed at a column of codes recorded a 12-hour clock on
        # it, and `5` a decimal comma, with no warning: the check that
        # warns on an unreached declaration runs before the questions.
        # A key of an answer the question did not offer is asked again,
        # as the questions file refuses an answer its entry did not
        # offer (`answers_answer_is_not_offered`).
        while answer is not None and not _offered_here(answer, question):
            _say(
                "    Please type one of the numbers offered, or press Enter "
                "to keep the reading synthtwin made."
            )
            answer = _read_one_answer(question.taken)
        if answer is None:
            return None
        if answer == asking.ANSWER_CODE:
            codes += [question.name]
        elif answer == asking.ANSWER_IDENTIFIER:
            identifiers += [question.name]
        elif answer == asking.ANSWER_JOINED:
            measurements += [question.name]
        elif answer == asking.ANSWER_DECIMAL_COMMA:
            commas += [question.name]
        elif answer == asking.ANSWER_TWELVE_HOUR:
            twelve += [question.name]
        elif answer in date_counts.MEMBERS:
            counted += [(question.name, answer)]
    return codes, identifiers, measurements, commas, twelve, counted


def _how_to_repeat(
    forced_codes: "list[str]",
    forced_identifiers: "list[str]",
    forced_measurements: "list[str]",
    forced_decimal_commas: "tuple[str, ...]" = (),
    twelve_hours: "tuple[str, ...]" = (),
    date_counted: "tuple[tuple[str, str], ...]" = (),
    answered_missing: "tuple[str, ...]" = (),
    answered_kept: "tuple[str, ...]" = (),
    answered_day_first: bool = False,
    taken_out: "tuple[str, ...]" = (),
    centuries: "tuple[tuple[str, int], ...]" = (),
    date_columns: "tuple[str, ...]" = (),
) -> str:
    """The options that repeat this run without asking anything.

    ``taken_out`` are options the person typed that an answer replaced,
    each already written as it is typed (`_typed_option`): they are said
    as options to take out of the command, since an answer is the newer
    statement and the typed option left in would contradict it (the Codex
    review of lane R1, item 7: `--keep-value UNK` typed and `missing`
    answered were told to add `--missing-value UNK`, and the pair exits 2).

    The answers about dates (plan P4-D381) are repeated as the options
    they stood for: `--day-first`, and `--missing-value` or
    `--keep-value` naming each code the run found in the answered
    columns. The codes are the person's declarations now, published
    where the description publishes any declared word, so naming them
    here says nothing the summary above did not. `answered_day_first`
    is True only where the run reads day first BECAUSE of an answer
    (landing T1): a typed `--day-first` is already on the line the
    person typed. `twelve_hours` names the columns read as 12-hour
    clocks, typed or answered (landing T1).
    """
    parts: list[str] = []
    # -- 3b.R4 (P4-D384): the columns whose dates are written as counts,
    # typed or answered, each with its system.
    for name, member in sorted(date_counted):
        parts += [f"{_typed_option('--date-count', name)} {member}"]
    if answered_day_first:
        parts += ["--day-first"]
    for name in sorted(twelve_hours):
        parts += [_typed_option("--twelve-hour", name)]
    # The centuries of two-figure years (landing R2a), typed or answered.
    for name, first_year in sorted(centuries):
        parts += [_typed_option("--century", f"{name}={first_year}")]
    # The columns said to hold dates (landing R2c), typed or answered.
    for name in sorted(date_columns):
        parts += [_typed_option("--date-column", name)]
    for spelling in answered_missing:
        parts += [_typed_option("--missing-value", spelling)]
    for spelling in answered_kept:
        parts += [_typed_option("--keep-value", spelling)]
    for name in sorted(forced_decimal_commas):
        parts += [_typed_option("--decimal-comma", name)]
    for name in sorted(forced_codes):
        parts += [_typed_option("--code", name)]
    for name in sorted(forced_identifiers):
        parts += [_typed_option("--identifier", name)]
    for name in sorted(forced_measurements):
        parts += [_typed_option("--measurement", name)]
    flags = _joined(parts, " ")
    out = ""
    if taken_out:
        out = (
            f"and take these out of the command you typed, because your "
            f"answers replaced them:\n  {_joined(list(taken_out), ' ')}\n"
        )
    return (
        f"\nTO REPEAT THIS RUN WITHOUT THE QUESTIONS, add:\n  "
        f"{flags}\n"
        f"{out}"
        f"Those answers are also recorded inside the profile itself. "
        f"Each value is {_shell_named()}."
    )


def _counted_settings(
    counted: "dict[str, str]",
) -> "tuple[tuple[str, str], ...]":
    """The columns whose dates are written as counts, as the settings hold them (landing R4).

    `(column, system)` in the columns' rising order: the one shape the
    settings block records, the questions file's answers and the typed
    options agree in.
    """
    return tuple((name, counted[name]) for name in sorted(counted))


def _lowered_floor_warning(given: int) -> str:
    """The warning shown when `--smallest-group` is under the notice line.

    Guarantees:

    - Inputs: the number the person typed, already known to be below
      `_NOTICE_LINE` (the default, 11) and at least 1.
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
    suite compares the two so they cannot drift. `_NOTICE_LINE` mirrors
    `contract.SMALL_GROUP_NOTICE_LINE` the same way.

    IT NAMES THE UNIT OF EACH FLOOR, AND IT COUNTS SIX FILES (review of
    2026-09-23, items 6 and 10). Two sentences were false. It said the
    notice line keeps a published group too big to point at one
    person, and the disclosure floor counts ROWS (plan P4-D348):
    measured on 100 declared people of twelve visits each, a value one
    person holds publishes the count 12 at the default floor. And it
    counted the files a full run leaves one short, and it counted the
    pages that stamp themselves one too many: the pages that say it in
    words are the summary, the twin's report and the quality report,
    beside the description, which records the floor as a setting.

    WHEN THIS IS SHOWN CHANGED ON 2026-08-25 (plan A-P4-37). It used to
    be shown whenever the floor was under the default, which was the
    same thing as somebody having typed `--smallest-group`. The default
    was 1 from then until 2026-09-22, so that test would never have
    fired. It is shown when the person TYPED a floor under
    `_NOTICE_LINE` -- a choice they made and should see priced. The
    default is 11 again since 2026-09-22 (plan P4-D316), the same number
    as `_NOTICE_LINE`, so a run that names no floor is never alarmed,
    and a run that types one below it always is.
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
        f"You set the smallest group size to {given}, which names "
        f"groups small enough to point at one person.\n"
        f"{_ALARM}\n"
        f"\n"
        f"WHAT YOU CHANGED. synthtwin normally leaves a value out of "
        f"the description unless at least {_NOTICE_LINE} rows share "
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
        f"disclosure, and {_NOTICE_LINE} is the number "
        f"that keeps a published group bigger than that.\n"
        f"\n"
        f"AND THE NUMBER COUNTS ROWS, NOT PEOPLE. Whatever you set it "
        f"to, a group has to cover that many ROWS. Where your table "
        f"holds several rows per person, twelve visits of one patient "
        f"are twelve rows, so a value only that patient has is "
        f"published with the count twelve even at the usual "
        f"{_NOTICE_LINE}. The one number counted in people is the SIZE "
        f"of the table, which is what decides whether synthtwin will "
        f"describe it at all.\n"
        f"\n"
        f"WHERE THOSE COUNTS GO NEXT. Not into the description alone. "
        f"The twin is built to hold the published counts exactly, and "
        f"the plain-language summary beside the description, the twin's "
        f"report and the quality report all quote them back. All six "
        f"files of a full run carry them, and the summary, the twin's "
        f"report and the quality report each say on their own face that "
        f"this description names groups this small, while the "
        f"description itself records the floor it was made at.\n"
        f"\n"
        f"IF YOU DID NOT MEAN THIS, run the command again without "
        f"--smallest-group, or with a larger number, and delete what "
        f"this run writes."
    )


# -- the population floor (plan P4-D341) ------------------------------
#
# IT LIVES IN THIS COMMAND AND NOWHERE ELSE. `profile.build_document`
# describes a table of any size, the loader reads a description of one,
# and `synthtwin validate` checks a file of one -- so a library caller
# keeps describing five rows, the validator keeps re-describing whatever
# it was pointed at, and a description written before this landing still
# loads. What the floor governs is the one act this command performs:
# turning somebody's real table into files that leave the machine.


def _population_of(
    column_names: "list[str]",
    columns: "list[list[str]]",
    settings: object,
    declared: "list[str]",
    codes: "list[str] | None" = None,
    measurements: "list[str] | None" = None,
    decimal_commas: "list[str] | None" = None,
    stored_as: "tuple[str, ...]" = (),
) -> "tuple[tuple[str, ...], int, str, tuple[object, ...]]":
    """The person columns, the population and the word it is counted in.

    Returns (person columns, how many, the unit word, the readings the
    census took). The readings are handed to `profile.build_document`
    right after, so a column the census read under the finished reading
    is not read again there (`taxonomy.population_census`). The unit is
    `people` where some declared identifier REPEATS and `rows` where
    none does, which is what `taxonomy.repeating_identifiers` decides
    and says why at length.

    THE ROWS COUNTED ARE THE ROWS THAT HOLD A VALUE (repair of landing
    3.2), which is `taxonomy.people_in`'s rule and not this function's:
    a row every cell of which the run reads as "no value" is counted
    nowhere, so twenty records padded to a hundred lines are a
    population of twenty and are refused -- whether the padding is
    blank, a listed spelling, a declared number or a stand-in this run
    judged for itself.

    AND WHAT A CELL HOLDS IS THE FINISHED READING'S ANSWER (review of
    stage 3, floor item 3). All four declarations are carried down,
    not the identifiers alone: each of them changes which cells of a
    column survive the passes that judge "no value", and the census has
    to read each column the way the run reads it. Measured before this:
    a column of twenty numbers followed by eighty `-999` cells passed
    the hundred-row floor as a hundred rows, under
    `--missing-value=-999`, under `-999.0`, and under the stand-in rule
    with nothing declared at all -- and the description that came out of
    the same run recorded twenty present cells.

    Guarantees: accepts the table's column names, its columns as text
    in the same order, the settings in force and the columns declared
    with `--identifier`, `--code`, `--measurement` and
    `--decimal-comma`, and how a workbook stores each column
    (`profile.stored_as_of`, plan P4-D382), which the description is
    handed too; returns the four. A fixed function of them.
    Raises TypeError where the settings are not settings, which is an
    internal invariant. Opens no file and prints nothing.
    """
    from synthtwin import taxonomy

    if not isinstance(settings, taxonomy.Settings):
        raise TypeError("internal check: the settings are not settings")
    declarations = taxonomy.Declarations(
        identifiers=tuple(declared),
        codes=tuple(codes if codes is not None else []),
        measurements=tuple(
            measurements if measurements is not None else []
        ),
        decimal_commas=tuple(
            decimal_commas if decimal_commas is not None else []
        ),
    )
    people, counted, readings = taxonomy.population_census(
        column_names, columns, declared, settings, declarations, stored_as
    )
    unit = taxonomy.NOTE_UNIT_ROWS
    if people:
        unit = taxonomy.NOTE_UNIT_PEOPLE
    return people, counted, unit, readings


def _table_sentences(document: "dict[str, object]") -> "list[str]":
    """The description's notes about the WHOLE TABLE, in its own order.

    Read back out of the document rather than kept in a variable beside
    it (plan P4-D341): the questions file then carries exactly what the
    description carries, and a rebuild that changed the note cannot
    leave the two disagreeing.
    """
    notes = document["publication_notes"]
    said: "list[str]" = []
    if not isinstance(notes, list):
        return said
    for entry in notes:
        if not isinstance(entry, dict):
            continue
        if entry["column"] != "":
            continue
        said += [f"{entry['note']}"]
    return said


def _counted_in_rows_notice(names: "list[str]") -> str:
    """What the screen says when nobody has said who the rows are about.

    Printed beside the person question (plan P4-D340), and only where
    the population is still counted in ROWS. The question asks whether
    a column names people; this says what the run did in the meantime,
    which is the half a person cannot see: the population was counted
    in ROWS, and a table of several rows per subject therefore passed a
    floor its subjects might not have.

    AND IT SAYS "NO COLUMN THAT NAMES PEOPLE", not "nothing was named
    with --identifier" (review of stage 3, floor item 4). The question
    is now put wherever the count is still in rows, and a unique-per-row
    `visit_id` declared is a column named with `--identifier` that
    leaves the count exactly there -- so the older sentence would have
    told a person who had just typed the option that they had not.

    Guarantees: accepts the columns asked about; returns one paragraph.
    A fixed function of the names, which are the table's own column
    names and are published in the description like every other.
    Raises nothing, opens no file.
    """
    return (
        f"\nHOW THIS RUN COUNTED YOUR TABLE\n"
        f"No column that names PEOPLE has been declared, so this "
        f"table's population was counted in ROWS. If one row of your "
        f"table is one visit rather than one person, that count is "
        f"larger than the number of people in it.\n"
        f"\nThe questions file asks about "
        f"{_joined(names, ' and ')}, whose values repeat and are "
        f"either many or written as codes -- the shape a column that "
        f"names people wears. Answer it there, or run the command "
        f"again with --identifier and the column's name, and the "
        f"population will be counted in people."
    )


def _withheld_notice(names: "tuple[str, ...]") -> str:
    """What the screen says of the columns held back until answered.

    Plan P4-D401. Each was asked a question `identifier` answers, and
    nobody has answered, so this run describes it as record numbers and
    publishes none of its values.
    The sentence names the way back, which is answering.

    Guarantees: accepts the columns held back; returns one paragraph. A
    fixed function of the names, which are the table's own column names
    and are published in the description like every other. Raises
    nothing, opens no file.
    """
    return (
        f"\nCOLUMNS HELD BACK UNTIL YOU ANSWER\n"
        f"Nobody has answered the question about "
        f"{_joined(list(names), ' and ')}, and `identifier` -- record "
        f"numbers -- is among its answers, so this description treats "
        f"them as record numbers and publishes none of their values, and "
        f"the twin writes made-up record numbers there. Answer the "
        f"questions file, and run the command again with --answers: any "
        f"answer gives the column the description that answer names."
    )


def _counted_in_people_notice(names: "tuple[str, ...]", floor: int) -> str:
    """What the screen says of the columns whose values were counted in people.

    Plan P4-D406. On a table of several rows a person, a value fewer
    than the smallest group size of PEOPLE hold is not published however
    many rows hold it; its cells are counted with the blanks, and the
    twin writes blanks there.

    Guarantees: accepts the columns and the floor; returns one
    paragraph. A fixed function of the names, which are the table's own
    column names and are published in the description like every other.
    Raises nothing, opens no file.
    """
    return (
        f"\nVALUES HELD BY FEWER THAN {floor} PEOPLE\n"
        f"This table has several rows a person, so each value of "
        f"{_joined(list(names), ' and ')} was counted in people as well "
        f"as rows: a value fewer than {floor} people hold is not "
        f"published however many rows hold it. Its cells are counted "
        f"with the blanks, and the twin writes blanks there."
    )


def _small_population_notice(spoken: str, person_columns: str) -> str:
    """The notice a table between the floor and the line gets, on the screen.

    ONE NOTICE, AND IT CANNOT BE SILENCED (plan P4-D341). There is no
    option that turns it off, it is not conditional on anybody being at
    the keyboard, and the sentence in it is the same sentence the
    description carries: the screen and the five pages a full run
    leaves cannot say two different things about how large the table
    was, because all of them render the one note.

    Guarantees: accepts the note's rendered sentence and the person
    columns named, if any; returns one paragraph. A fixed function of
    the two. Raises nothing, opens no file, and carries no value of the
    table -- the names in it are ones the person typed after
    `--identifier`.
    """
    by = ""
    if person_columns:
        by = (
            f" The people were counted by {person_columns}: rows "
            f"sharing a value there are one person, and rows holding no "
            f"value there count as one person between them."
        )
    return (
        f"\nABOUT THE SIZE OF THIS TABLE\n"
        f"{spoken}.{by}\n"
        f"\nThis notice is on the screen and on every page this run "
        f"writes. The description carries it as a note of its own, and "
        f"the plain-language summary, the questions file, the twin's "
        f"report and the quality report all read it back from there. "
        f"Nothing turns it off. The twin's own table carries no trace "
        f"of it, so code you write against the twin runs exactly as it "
        f"ran before."
    )


def _handed_once(box: "list[tuple[object, ...]]") -> "tuple[object, ...]":
    """Take the one thing a box holds out of it, leaving the box empty.

    WHY A BOX (lane S4d, plan P4-D390): `_run_profile` keeps the
    population census's readings in a local name while it describes the
    table, and a reading held there outlives the column it was read for:
    on a table of a million rows each one is a column's worth of records.
    The command puts the readings in a box made for the call, empties
    the name, and hands them over through this function, so the
    description's own frame is the only holder.

    Guarantees: returns what the box held; the box is empty afterwards.
    Raises IndexError on an empty box. No I/O of any kind.
    """
    taken = box[0]
    del box[0]
    return taken


def _run_profile(
    table: str,
    out_dir: "str | None",
    smallest_group: int,
    floor_chosen: bool,
    forced_identifiers: list[str],
    forced_codes: list[str],
    forced_measurements: list[str],
    forced_decimal_commas: list[str],
    answers_path: "str | None",
    kept_values: list[str],
    missing_values: list[str],
    first_row: str,
    day_first: bool,
    sheet: str = "",
    metadata_rows_given: str = "",
    delimiter_given: str = "",
    date_counts_given: "list[list[str]] | None" = None,
    forced_twelve_hours: "list[str] | None" = None,
    centuries_given: "list[str] | None" = None,
    date_columns_given: "list[str] | None" = None,
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
    from synthtwin import (
        canonical,
        contract,
        profile,
        reading,
        summary,
        taxonomy,
        writing,
    )
    # WHAT THE PERSON TYPED, kept as typed, so the line that repeats the
    # run can say which of these an answer replaced (`_how_to_repeat`).
    typed_codes = list(forced_codes)
    typed_identifiers = list(forced_identifiers)
    typed_measurements = list(forced_measurements)
    typed_commas = list(forced_decimal_commas)
    typed_kept = list(kept_values)
    typed_missing = list(missing_values)

    if smallest_group < 1:
        _warn(errors.floor_not_positive(f"{smallest_group}"))
        return 2
    # -- 3b.R4 (P4-D384): THE COLUMNS WHOSE DATES ARE WRITTEN AS COUNTS
    # (`--date-count COLUMN SYSTEM`, question Q3). Each system is one of
    # the twelve, refused before the table is opened where it is not, and
    # one column named with two systems is refused as two readings of it.
    counted: "dict[str, str]" = {}
    for typed_pair in date_counts_given or []:
        if len(typed_pair) != 2:
            continue
        counted_name = f"{typed_pair[0]}"
        counted_member = f"{typed_pair[1]}"
        if counted_member not in date_counts.MEMBERS:
            _warn(errors.date_count_system_not_supported(_shown(counted_member)))
            return 2
        if counted_name in counted and counted[counted_name] != counted_member:
            _warn(errors.column_declared_twice(counted_name))
            return 2
        counted[counted_name] = counted_member
    typed_counted = dict(counted)
    # THE SEVENTH DECLARATION (landing T1, plan P4-D370): the columns
    # named 12-hour clocks written without AM or PM.
    twelve_hours = sorted(
        {one: 1 for one in (forced_twelve_hours or [])}
    )
    # -- 3b.R2c (P4-D383): THE COLUMNS SAID TO HOLD DATES (question Q6).
    date_columns = sorted({one: 1 for one in (date_columns_given or [])})
    # THE CENTURIES OF TWO-FIGURE YEARS (landing R2a, question Q5): each
    # `--century COLUMN=YEAR`, refused before the table is opened where it
    # is not that, and the window that stands where nothing was said
    # (1969) taken as no declaration at all.
    centuries: "dict[str, int]" = {}
    for typed_century in centuries_given or []:
        found_century = _century_given(typed_century)
        if found_century is None:
            _warn(errors.century_not_supported(_shown(typed_century)))
            return 2
        if found_century[1] in parsing.CENTURY_WINDOW_YEARS:
            centuries[found_century[0]] = found_century[1]
        elif found_century[0] in centuries:
            del centuries[found_century[0]]

    # HOW MANY ROWS UNDER THE NAMES DESCRIBE THE COLUMNS (plan P4-D81).
    # Refused here, before the table is opened, like every other
    # declaration that cannot be acted on.
    metadata_rows = 0
    # WHETHER THE PERSON CONFIRMED IT AFTER BEING TOLD WHAT IT COSTS
    # (review of landing 2b.17, MAJOR). A declaration typed on the
    # command line is read, and where the file does not bear it out the
    # rows STAY in the table and the question is put in the questions
    # file. An answer in that file is the confirmation: it is given
    # after reading what each answer publishes, so it cannot be a
    # typing slip, and it is the one route by which such rows leave the
    # table on a file wearing none of the shape.
    metadata_rows_confirmed = False
    if metadata_rows_given:
        if metadata_rows_given not in ("0", "2"):
            _warn(errors.metadata_rows_not_supported(_shown(metadata_rows_given)))
            return 2
        metadata_rows = int(metadata_rows_given)

    # WHICH CHARACTER SEPARATES THE COLUMNS, WHERE THE PERSON SAID (plan
    # P4-D110, review item CODEX-4). Refused before the table is opened
    # where it is not one of the four this format reads.
    declared_delimiter = ""
    if delimiter_given:
        if delimiter_given not in _DELIMITER_SPELLINGS:
            _warn(errors.delimiter_not_supported(_shown(delimiter_given)))
            return 2
        declared_delimiter = _DELIMITER_SPELLINGS[delimiter_given]

    # THE ANSWERS ARE READ BEFORE THE TABLE IS OPENED (amendment
    # A-P4-58). A file that is not a questions file, or that answers a
    # column with a word no question offered, is the person's mistake
    # to fix in one edit -- and telling them about it after their real
    # table has been read and described would make them wait for a run
    # whose whole point was to use the answers it did not have.
    #
    # AND THE FILE IS THE NEWER STATEMENT. A person who typed
    # `--code dose` last week and answers `measurement` for `dose`
    # today has changed their mind, so the answer replaces the typed
    # declaration rather than joining it: the pair `--code dose
    # --measurement dose` is refused a few lines below, and arriving at
    # that pair by a route that never re-checked is exactly the defect
    # review item P4-G3-R4-F3 found on the interview path.
    answers_were_handed_back = False
    # What the questions file answered about dates (plan P4-D381): the
    # order of day and month, and the columns whose few repeated codes
    # were answered `missing` or `real-value`.
    answered_day_first = False
    answered_month_first = False
    answered_missing_dates: "list[str]" = []
    answered_real_values: "list[str]" = []
    # ...and what each of those questions said it saw, by column, which
    # tells the run which codes the answer was about.
    answered_code_shapes: "dict[str, str]" = {}
    # ...and the columns whose centuries the file answered (landing R2a).
    answered_centuries: "list[str]" = []
    # ...and the columns whose Q6 the file answered `keep` (landing R2c):
    # nothing is declared, and Q6 is not put to them again.
    dates_kept: "list[str]" = []
    # ...and the columns whose question offering `identifier` the file
    # answered `keep` (plan P4-D401): nothing is declared, and their
    # values are published as their reading publishes them.
    identities_kept: "tuple[str, ...]" = ()
    # ...and the entries the file answered with a declaration, written
    # into the file this run writes again (plan P4-D401).
    answered_entries: "tuple[dict[str, object], ...]" = ()
    if answers_path is not None:
        try:
            written = asking.answers_in(
                contract.load_answers(answers_path), _shown(answers_path)
            )
        except ValueError as error:
            _warn(_shown(f"{error}"))
            return 2
        # THE FIFTH ANSWER IS READ BEFORE THE TABLE IS OPENED, which is
        # what makes it usable at all (plan P4-D81): it changes the
        # READING of the file, so an answer arriving after the read
        # would mean reading the table twice. A person answers the
        # question in the file their last run wrote, and their next run
        # reads their table the way they said.
        # AN ANSWER OF `data` IS AN ANSWER (plan P4-D172). It is nought
        # rows, and a truthiness test here read nought as "not answered"
        # and kept a typed `--metadata-rows 2`: measured, a file whose
        # two rows under the names were a person's record and a marker
        # row lost both to `header_rows` after the person had answered
        # that they were records.
        if written.metadata_rows_answered:
            metadata_rows = written.metadata_rows
            metadata_rows_confirmed = written.metadata_rows > 0
        # AN ANSWER THAT CHANGES THE READING MAY NOT STAND BESIDE ONE
        # THAT NAMES A COLUMN (review of stage 3, floor item 1). The
        # names in a questions file are the names of the reading that
        # WROTE it; an answer that changes the reading gives the same
        # names to different columns, and a declaration applied by name
        # afterwards lands on the wrong one. Measured on the tree before
        # this refusal: a header of `column_2,column_1` over 360 records
        # whose first field held twelve repeating subject codes, with
        # `names` answered for the first row and `identifier` answered
        # for `column_1` -- the FIRST field under the reading in force
        # -- reached all three writers with the declaration on the
        # SECOND field, counted 350 people and published the twelve real
        # subject codes with their visit counts. Declaring the first
        # field refuses the same table as twelve people.
        #
        # THE ANSWERS ARE NOT RANKED AND NOTHING IS GUESSED. Whether
        # `column_1` means the first field or a column the corrected
        # reading names `column_1` is exactly what cannot be told apart
        # -- the reproduction above is a file where both readings hold
        # -- so the pair is refused and the person is told to answer the
        # file's own question first. Two runs, each with one reading in
        # it, and no name means two columns.
        reading_changed = _answers_that_change_the_reading(
            written, first_row, declared_delimiter
        )
        named_columns: "list[str]" = []
        for one in (
            list(written.codes)
            + list(written.identifiers)
            + list(written.measurements)
            + list(written.decimal_commas)
            # -- 3b.R4 (P4-D384): and the columns answered with a system.
            + [one for one, _member in written.date_counts]
            + list(written.twelve_hours)
            # ...and the columns whose centuries were answered (landing R2a).
            + [one_century for one_century, _year in written.century_windows]
            + list(written.centuries_kept)
            # ...and the columns whose codes were answered (plan P4-D381):
            # each is found again by its name in the table, so a changed
            # reading would find them in a different column.
            + list(written.missing_date_columns)
            + list(written.real_value_columns)
            # ...and the columns answered `dates` (landing R2c), or `keep`.
            + list(written.date_columns)
            + list(written.date_columns_kept)
        ):
            # Each name once: a column answered in both sections of the
            # file would otherwise stand twice in one sentence.
            if one not in named_columns:
                named_columns += [one]
        if reading_changed and named_columns:
            _warn(
                errors.answers_change_the_reading_and_name_columns(
                    _shown(answers_path), reading_changed,
                    sorted(named_columns),
                )
            )
            return 2
        # ...AND THE SIXTH, FOR THE SAME REASON (plan P4-D110): which
        # delimiter the file is written with decides how it is read, so
        # the answer has to arrive before the read. It is the newer
        # statement and replaces a typed one.
        if written.delimiter:
            declared_delimiter = written.delimiter
        # ...AND THE SEVENTH, FOR THE SAME REASON (the owner's ruling of
        # 2026-09-17, item 8; plan P4-D232): which row holds the column
        # names decides how the file is read, so the answer has to
        # arrive before the read.
        #
        # BOTH ANSWERS ARE APPLIED, and only one of them was until the
        # review of stage 3 (floor item 2). `first-record` was called
        # "the reading that already stands", which it is only while
        # nothing else moves: answered BESIDE a delimiter correction it
        # is the one answer holding the first row in the table, and
        # dropping it let the corrected reading take that row as the
        # column names. Measured: a first record of `12,HEADER|LABEL`
        # over 360 records of `i,code{i}|other{i}`, answered
        # `first-record` and `vertical-bar`, described 360 records and
        # published `12,HEADER` and `LABEL` as two column names, where
        # `--first-row data --delimiter '|'` keeps all 361 records and
        # names the columns `column_1` and `column_2`. An answer that is
        # dropped is an answer a person was told had been heard.
        if written.first_row == asking.ANSWER_FIRST_ROW_NAMES:
            first_row = _FIRST_ROW_NAMES
        elif written.first_row == asking.ANSWER_FIRST_ROW_DATA:
            first_row = _FIRST_ROW_DATA
        spoken_for = (
            list(written.codes)
            + list(written.identifiers)
            + list(written.measurements)
            + list(written.decimal_commas)
        )
        forced_codes = sorted(
            [one for one in forced_codes if one not in spoken_for]
            + list(written.codes)
        )
        forced_identifiers = sorted(
            [one for one in forced_identifiers if one not in spoken_for]
            + list(written.identifiers)
        )
        forced_measurements = sorted(
            [one for one in forced_measurements if one not in spoken_for]
            + list(written.measurements)
        )
        # AN ANSWER THAT THE POINT GROUPS THOUSANDS IS `--decimal-comma`
        # (landing 2b.2), added to the typed ones rather than replacing
        # them: the declaration names a column, and naming it twice is
        # naming it once.
        forced_decimal_commas = sorted(
            [one for one in forced_decimal_commas if one not in written.decimal_commas]
            + list(written.decimal_commas)
        )
        # ...AND THE 12-HOUR CLOCKS (landing T1): a column answered
        # `twelve-hour` joins the typed ones.
        twelve_hours = sorted(
            {one: 1 for one in twelve_hours + list(written.twelve_hours)}
        )
        # ...AND THE CENTURIES OF TWO-FIGURE YEARS (landing R2a, question
        # Q5): an answer is the newer statement and replaces a typed
        # `--century` for its column; the window that stands declares
        # nothing, and is carried so the question is not put again.
        for one_century, first_year in written.century_windows:
            centuries[one_century] = first_year
        for one_century in written.centuries_kept:
            if one_century in centuries:
                del centuries[one_century]
        answered_centuries = [
            one_century for one_century, _year in written.century_windows
        ] + list(written.centuries_kept)
        # ...AND THE COLUMNS SAID TO HOLD DATES (landing R2c, question Q6):
        # an answer of `dates` joins the typed `--date-column`.
        date_columns = sorted(
            {one: 1 for one in date_columns + list(written.date_columns)}
        )
        # ...and those answered `keep`, carried so Q6 is not put again.
        dates_kept = list(written.date_columns_kept)
        # ...and the columns answered `keep` to a question offering
        # `identifier` (plan P4-D401). Under an answer that changes the
        # reading a name may land on another column, so there such a
        # `keep` holds nothing back from the hold below: the column is
        # asked again under the reading in force.
        if not reading_changed:
            identities_kept = written.identities_kept
            answered_entries = written.declared_entries
        # ...AND THE ORDER OF DAY AND MONTH (plan P4-D381): an answer of
        # `day-first` is `--day-first`, and it is applied before the read
        # because it decides how the columns of dates are read. It goes
        # on the repeat line only where it was not typed (landing T1,
        # repair item 4): a typed `--day-first` is on the line the person
        # typed already.
        if written.day_first:
            if not day_first:
                answered_day_first = True
            day_first = True
        # An answer of `month-first` declares nothing -- it is the
        # reading that stands -- and is carried so the question is not
        # put back to the person in the file this run writes again.
        answered_month_first = written.month_first
        # -- 3b.R4 (P4-D384): AND THE COLUMNS ANSWERED WITH A COUNTING
        # SYSTEM (question Q3), each the newer statement: it replaces a
        # typed `--date-count` for its column and a typed `--code`,
        # `--identifier` or `--measurement` for it, and a column answered
        # one of those three is no longer read as counted dates.
        for counted_name, counted_member in written.date_counts:
            counted[counted_name] = counted_member
        for counted_name in spoken_for:
            if counted_name in counted:
                del counted[counted_name]
        forced_codes = [one for one in forced_codes if one not in counted]
        forced_identifiers = [
            one for one in forced_identifiers if one not in counted
        ]
        forced_measurements = [
            one for one in forced_measurements if one not in counted
        ]
        # ...AND THE CODES OF A COLUMN OF DATES OR TIMES (plan P4-D381).
        # These name columns, and what each answer declares is found in
        # the table once it is open, below.
        answered_missing_dates = list(written.missing_date_columns)
        answered_real_values = list(written.real_value_columns)
        for one, saw in written.date_code_shapes:
            answered_code_shapes[one] = saw
        answers_were_handed_back = (
            bool(spoken_for)
            or bool(written.twelve_hours)
            or bool(written.date_counts)
            or written.day_first
            or bool(answered_missing_dates)
            or bool(answered_real_values)
            or bool(written.century_windows)
            or bool(written.date_columns)
        )
    # UNDER BOTH READINGS WHERE EITHER IS IN PLAY (review item
    # P4-G3-R6-F2). `--decimal-comma` names columns and these two name
    # values that reach the whole table, so a pair that is one number
    # on a declared column and two numbers elsewhere is still a pair
    # the person cannot have meant both halves of.
    # A DECLARED VALUE WHOSE NUMBER DEPENDS ON THE GRAMMAR IS REFUSED
    # BESIDE `--decimal-comma` (plan amendment; review item
    # P4-G3-R7-F1). The two kinds of declaration disagree about scope
    # -- one names columns, the other names values and reaches the
    # whole table -- and the settings block has one place to record
    # what a value means. Carried as a residual for a round on the
    # argument that the consequence was merely conservative; the
    # argument was refuted with a case where a checked file receives
    # MISSED verdicts on presence, role and its numbers against a
    # description correct about all three.
    if forced_decimal_commas:
        for spelling, option in (
            [(one, "--keep-value") for one in kept_values]
            + [(one, "--missing-value") for one in missing_values]
        ):
            if not parsing.reads_as_two_numbers(spelling):
                continue
            _warn(errors.a_declared_value_reads_two_ways(spelling, option))
            return 2

    clashes = taxonomy.contradictory_declarations(
        tuple(kept_values),
        tuple(missing_values),
        bool(forced_decimal_commas),
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
        forced_twelve_hour_clocks=tuple(twelve_hours),
        # The second cut's three declarations (plan P4-D386): the landing
        # that fills each passes it here, below its own line.
        # -- 3b.R2a (P4-D383)
        century_windows=tuple(
            (one_century, centuries[one_century])
            for one_century in sorted(centuries)
        ),
        # -- 3b.R2c (P4-D383)
        forced_date_columns=tuple(date_columns),
        # -- 3b.R4 (P4-D384)
        forced_date_counts=_counted_settings(counted),
    )
    read = reading.read_table(
        table, first_row, sheet=sheet, metadata_rows=metadata_rows,
        # ...and whether the person confirmed a declaration the file
        # does not bear out, which is what decides whether those rows
        # leave the table at all (review of landing 2b.17, MAJOR).
        metadata_rows_confirmed=metadata_rows_confirmed,
        # AND UNDER THE DECLARED GRAMMAR (review item CODEX-9). The
        # survey reads the row order off the cells as written, and a
        # column declared to write `0,5` and `10,0` reads as no number
        # at all under the ordinary grammar -- so it fell to the text
        # collation, where `10,0` sorts before `9,9`, and a table
        # genuinely sorted by it published no order. The declaration
        # has to reach the survey for the order to be read correctly.
        decimal_comma_columns=tuple(forced_decimal_commas),
        # AND WITH THE DELIMITER THE PERSON DECLARED, where they did
        # (plan P4-D110). Nothing is guessed about a declared one.
        declared_delimiter=declared_delimiter,
        # AND WITH THE SMALLEST GROUP, which both readers want. On a
        # workbook it decides whether a column's second number format is
        # a population of it or the one cell somebody reformatted (plan
        # P4-D283); on a delimited file the written form carries counts
        # and positions of its own lines, and those are held to the one
        # disclosure rule like every other count synthtwin publishes
        # (plan P4-D290). One number, so it is passed once.
        small_cell_floor=settings.small_cell_floor,
        # AND THE WORDS THAT MEAN NO VALUE (the repair of review item 3
        # of landing R3): a workbook's clock times beside `NA`, or beside
        # a word named with `--missing-value`, are read as clocks. The
        # codes a questions file answered `missing` are found in the
        # table this read opens, below, and reach the description but
        # not this reading: a refusal of clocks beside such a code names
        # `--missing-value`, which reaches both.
        missing_under=settings,
    )

    # A FILE THAT READS EQUALLY WELL UNDER TWO DELIMITERS IS SAID OUT
    # LOUD (review item CODEX-4, plan P4-D110). It is read the way the
    # cells favour, which is how every file this tool twinned before is
    # still read, and the person is told the other reading exists and
    # how to choose it: a silent misreading of their columns is the one
    # outcome this may not leave them with.
    delimiter_tie: "tuple[str, ...]" = ()
    if read.survey is not None and not declared_delimiter:
        delimiter_tie = read.survey.delimiter_tie
    if delimiter_tie:
        _say(f"\n{_delimiter_tie_notice(delimiter_tie)}\n")

    # AND THE PERSON IS TOLD WHAT WAS SEEN AND NOT ACTED ON (plan
    # P4-D81). The shape some survey exports wear is recognised and
    # deliberately left alone: saying nothing would leave a person
    # whose file really is such an export with two rows of machine
    # text among their records and no idea why.
    surveyed = read.survey
    if surveyed is not None and surveyed.metadata_shape and not metadata_rows:
        _say(f"\n{_metadata_rows_notice()}\n")

    # ...AND A DECLARATION THE FILE DOES NOT BEAR OUT IS QUESTIONED THE
    # OTHER WAY ROUND. The notice above exists because acting on a
    # resemblance published a person's record as schema; the
    # declaration itself is checked against nothing at all, so
    # `--metadata-rows 2` on an ordinary table takes two records out of
    # it and publishes them verbatim, exempt from the smallest group,
    # with nothing said. The reading still obeys the person -- it is
    # their file and their declaration -- and they are told what was
    # seen.
    metadata_declaration_unseen = (
        bool(metadata_rows)
        and (surveyed is None or not surveyed.metadata_shape)
        and not metadata_rows_confirmed
    )
    if metadata_declaration_unseen:
        _say(f"\n{_metadata_rows_unseen_notice(metadata_rows)}\n")

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

    # The same refusal for the other declaration, and for the same
    # reason: a misspelt name must not produce a description in which a
    # coding system was quietly read as a quantity (plan P4-D19).
    unknown_codes = [
        name for name in forced_codes if name not in read.column_names
    ]
    if unknown_codes:
        _warn(
            errors.unknown_column_named(
                "holding codes", unknown_codes[0], read.column_names
            )
        )
        return 2

    # A column named in BOTH declarations is refused rather than ranked.
    # `--identifier` publishes nothing and `--code` publishes the
    # distribution, so there is no reading of the pair that is not a
    # guess about which the person meant (the rule `profile_column`
    # applies to a value declared both data and missing).
    unknown_measured = [
        name for name in forced_measurements if name not in read.column_names
    ]
    if unknown_measured:
        _warn(
            errors.unknown_column_named(
                "holding measurements",
                unknown_measured[0],
                read.column_names,
            )
        )
        return 2

    unknown_twelve = [
        name for name in twelve_hours if name not in read.column_names
    ]
    if unknown_twelve:
        _warn(
            errors.unknown_column_named(
                "as a 12-hour clock", unknown_twelve[0], read.column_names
            )
        )
        return 2
    # -- 3b.R2a (P4-D383)
    unknown_centuries = [
        name for name in sorted(centuries) if name not in read.column_names
    ]
    if unknown_centuries:
        _warn(
            errors.unknown_column_named(
                "writing two-figure years in a century of its own",
                unknown_centuries[0],
                read.column_names,
            )
        )
        return 2

    # -- 3b.R2c (P4-D383)
    unknown_dates = [
        name for name in date_columns if name not in read.column_names
    ]
    if unknown_dates:
        _warn(
            errors.unknown_column_named(
                "as a column of dates", unknown_dates[0], read.column_names
            )
        )
        return 2

    unknown_commas = [
        name
        for name in forced_decimal_commas
        if name not in read.column_names
    ]
    if unknown_commas:
        _warn(
            errors.unknown_column_named(
                "writing its numbers with a comma",
                unknown_commas[0],
                read.column_names,
            )
        )
        return 2
    # -- 3b.R4 (P4-D384): A COLUMN WHOSE DATES ARE WRITTEN AS COUNTS is a
    # column of this table, and is read one way, as those dates: named
    # beside `--code`, `--identifier`, `--measurement` or `--twelve-hour`
    # it is refused, as the description's own rule S8d refuses it.
    unknown_counted = [
        name for name in sorted(counted) if name not in read.column_names
    ]
    if unknown_counted:
        _warn(
            errors.unknown_column_named(
                "writing its dates as counts",
                unknown_counted[0],
                read.column_names,
            )
        )
        return 2
    for name in sorted(counted):
        if (
            name in forced_codes
            or name in forced_identifiers
            or name in forced_measurements
            or name in twelve_hours
        ):
            _warn(errors.column_declared_twice(name))
            return 2

    # THE FOURTH DECLARATION IS NOT ONE OF THE THREE, and its refusals
    # are its own (plan P4-D26). It says how a column's numbers are
    # SPELLED, where the three below say what a column HOLDS, so it
    # does not join their mutual exclusion: `--measurement dose
    # --decimal-comma dose` is coherent and is the pairing this
    # declaration exists for. What it cannot stand beside is a
    # declaration that stops the column being read as numbers at all --
    # then synthtwin would take the instruction and ignore it, and the
    # person would never learn that it had.
    for name in forced_decimal_commas:
        if name in forced_identifiers:
            _warn(
                errors.comma_declaration_would_be_ignored(
                    name, "--identifier"
                )
            )
            return 2
        if name in forced_codes:
            _warn(
                errors.comma_declaration_would_be_ignored(name, "--code")
            )
            return 2

    # A column named in two declarations at once is refused rather than
    # ranked: they ask for different readings and there is no reading of
    # the pair that is not a guess about which the person meant.
    both = [name for name in forced_codes if name in forced_identifiers]
    both += [
        name for name in forced_measurements if name in forced_identifiers
    ]
    both += [
        name for name in forced_measurements if name in forced_codes
    ]
    if both:
        _warn(errors.column_declared_twice(both[0]))
        return 2

    # THE CODES THE QUESTIONS FILE ANSWERED, FOUND AGAIN IN THE TABLE
    # (plan P4-D381). The file names the column and never its codes --
    # it carries no value of the table -- so the codes are read here,
    # from the cells just opened, by the rule that asked about them, and
    # become the declarations the answers stand for: `missing` is
    # `--missing-value` naming each code, `real-value` is `--keep-value`
    # naming each. Both reach every column, which is what those options
    # do and what the answers said.
    held_names = {one: 1 for one in read.column_names}
    unknown_dates = [
        name
        for name in answered_missing_dates + answered_real_values
        if name not in held_names
    ]
    if unknown_dates:
        _warn(
            errors.unknown_column_named(
                "a column of dates or times beside a few repeated codes",
                unknown_dates[0],
                read.column_names,
            )
        )
        return 2
    added_missing: "list[str]" = []
    added_kept: "list[str]" = []
    # Each declaration once, by the identity it matches by: two columns
    # both answered `missing` about `UNK` declare it once, and the line
    # that repeats the run names it once. Once for EACH answer: `UNK`
    # answered `missing` in one column and `real-value` in another is
    # the contradiction refused below, and is not folded away here.
    missing_as: "dict[tuple[str, object], int]" = {}
    kept_as: "dict[tuple[str, object], int]" = {}
    # Each column found by its name once (the Codex review of lane R1,
    # item 9): a walk of the names per answer grew with their square.
    column_place: "dict[str, int]" = {}
    for named_at in range(len(read.column_names)):
        if read.column_names[named_at] not in column_place:
            column_place[read.column_names[named_at]] = named_at
    # THE CODES THE QUESTION DESCRIBED, AND NO OTHERS (the Codex review
    # of lane R1, item 5): found under the typed declarations where the
    # question's own words describe what is found -- the run that wrote
    # the file was typed the same way -- and otherwise with the typed
    # words a code of the column would match taken out, so the answer, the
    # newer statement (below), replaces a typed word it was about and
    # leaves alone one it never counted (`asking.date_codes_answered`).
    # Where neither reading is the one described, the typed words stand,
    # and a typed word the answer contradicts is said to be left as typed.
    for name, missing in (
        [(one, True) for one in answered_missing_dates]
        + [(one, False) for one in answered_real_values]
    ):
        column_at = column_place[name]
        seen, left = asking.date_codes_answered(
            read.columns[column_at],
            settings,
            answered_code_shapes[name] if name in answered_code_shapes else "",
            missing,
        )
        if left:
            _warn(
                errors.the_date_codes_answer_left_typed_words(
                    name,
                    "--keep-value" if missing else "--missing-value",
                    len(left),
                )
            )
        if seen is None:
            _warn(errors.the_date_codes_answer_reached_nothing(name))
            continue
        for spelling, _rows in seen.codes:
            identity = asking.declared_identity(spelling)
            if missing:
                if identity not in missing_as:
                    missing_as[identity] = 1
                    added_missing += [spelling]
            elif identity not in kept_as:
                kept_as[identity] = 1
                added_kept += [spelling]
    if added_missing or added_kept:
        commas = bool(forced_decimal_commas)
        for spelling, option in (
            [(one, "--keep-value") for one in added_kept]
            + [(one, "--missing-value") for one in added_missing]
        ):
            if commas and parsing.reads_as_two_numbers(spelling):
                _warn(errors.a_declared_value_reads_two_ways(spelling, option))
                return 2
        # THE ANSWER IS THE NEWER STATEMENT, as it is for a column's
        # role above: a typed value it contradicts gives way to it.
        kept_values = [
            one
            for one in kept_values
            if not taxonomy.contradictory_declarations(
                (one,), tuple(added_missing), commas
            )
        ] + added_kept
        missing_values = [
            one
            for one in missing_values
            if not taxonomy.contradictory_declarations(
                tuple(added_kept), (one,), commas
            )
        ] + added_missing
        clashes = taxonomy.contradictory_declarations(
            tuple(kept_values), tuple(missing_values), commas
        )
        if clashes:
            _warn(
                errors.answered_codes_contradict_each_other(
                    _shown(answers_path or ""), _shown(clashes[0])
                )
            )
            return 2
        settings = dataclasses.replace(
            settings,
            kept_values=tuple(kept_values),
            declared_missing_values=tuple(missing_values),
        )

    # THE POPULATION FLOOR, ASKED FIRST WITH WHAT IS DECLARED SO FAR
    # (plan P4-D341): the columns typed after `--identifier` and the
    # ones answered in the questions file, both of which were settled
    # before the table was opened. A declaration that arrives later --
    # on the screen, at the interview below -- can only LOWER the count
    # of people, because a repeating identifier splits the rows into
    # more groups than one, so this check is a necessary condition and
    # the one after the rebuild is the final one.
    #
    # NOTHING HAS BEEN WRITTEN AT THIS POINT and nothing has been
    # described. A table under the floor therefore costs the person one
    # message and no files at all.
    # HOW A WORKBOOK STORES EACH COLUMN, taken once and handed to the
    # census and the description alike (plan P4-D382), so the column
    # the census reads is read once.
    storage = profile.stored_as_of(read, settings)
    person_columns, population, unit, census_readings = _population_of(
        read.column_names,
        read.columns,
        settings,
        forced_identifiers,
        forced_codes,
        forced_measurements,
        forced_decimal_commas,
        storage,
    )
    if population < parsing.POPULATION_FLOOR:
        _warn(
            errors.the_population_is_too_small(
                population, unit, _joined(list(person_columns), " and ")
            )
        )
        return 1
    settings = dataclasses.replace(settings, person_columns=person_columns)
    population_notes = profile.notes_for_a_small_population(
        population, unit, parsing.POPULATION_NOTICE_LINE
    )

    census_box = [census_readings]
    census_readings = ()
    # The columns whose values the count in people changed (plan
    # P4-D406), named on the screen.
    counted_in_people: "list[str]" = []
    document = profile.build_document(
        read,
        settings,
        forced_identifiers,
        forced_codes,
        forced_measurements,
        forced_decimal_commas,
        forced_metadata_rows=metadata_rows,
        forced_delimiter=declared_delimiter,
        table_notes=population_notes,
        # HANDED OVER OUT OF A BOX (lane S4d, plan P4-D390): the box is
        # emptied as the call is made, so the description holds each
        # column's census reading alone and lets it go once that column
        # is described, rather than this frame keeping every one alive
        # until the whole table is.
        readings=_handed_once(census_box),
        stored_as=storage,
        # -- P4-D406: every value counted in the declared people too.
        subjects=list(person_columns),
        counted_in_subjects=counted_in_people,
    )
    # Handed over once: the description has taken the reading as its own.
    census_readings = ()

    # THE ONE QUESTION THE VALUES CANNOT SETTLE (plan P4-D19). Asked
    # after the description is built, because what a column was READ AS
    # is half the question, and asked BEFORE anything is written, so an
    # answer never arrives too late to be used. Where nobody is at the
    # keyboard the same columns are named on screen with the option that
    # corrects them, and the run goes on: a scripted run must not hang,
    # and must not be guessed at in silence either.
    # A DECLARATION THAT COULD NOT BE HONOURED IS SAID OUT LOUD
    # (residual R-P4-52; review item P4-G3-R2-F4). Which columns
    # `--decimal-comma` reaches depends on the ROLE the values take,
    # which is not known until the table has been read -- so the
    # refusals that can be made early were made early, and this one is
    # said here. Without it a person who declares the comma on a
    # column of `1,5/2,5` or `EUR 1,5` gets a description that read
    # those numbers by the ordinary rules, with nothing on the screen
    # saying so: principle 5's silent miscast, arriving through a
    # declaration rather than through a guess.
    for name in sorted(forced_decimal_commas):
        for described_column in _described_columns(document):
            if described_column["name"] != name:
                continue
            if described_column["role"] in contract.DECIMAL_COMMA_HONOURED_ROLES:
                continue
            _warn(
                errors.the_comma_declaration_did_not_reach(
                    name, f"{described_column['role']}"
                )
            )
    # -- 3b.R4 (P4-D384): ...AND A COLUMN DECLARED TO WRITE ITS DATES AS
    # COUNTS WHOSE CELLS DID NOT READ AS SUCH DATES, said here as the
    # description says it (NF115).
    for name in sorted(counted):
        for described_column in _described_columns(document):
            if described_column["name"] != name:
                continue
            if described_column["role"] == taxonomy.ROLE_DATETIME:
                continue
            _warn(
                errors.the_date_count_declaration_did_not_reach(
                    name, counted[name], f"{described_column['role']}"
                )
            )
    # ...AND THE 12-HOUR DECLARATION, WHICH REACHES ONLY AN UNMARKED CLOCK
    # (landing T1, plan P4-D370), said where it reached nothing.
    for name in twelve_hours:
        for described_column in _described_columns(document):
            if described_column["name"] != name:
                continue
            if _read_on_twelve_hours(described_column):
                continue
            # A WORD TOO RARE TO NAME IS NOT A DECLARATION THAT REACHED
            # NOTHING (the T1 review's item 9) -- unless the clocks write
            # AM or PM, which the declaration does not change.
            column_at = 0
            for held in read.column_names:
                if held == name:
                    break
                column_at = column_at + 1
            if _style_held_back(described_column) and _clocks_on_the_declared_face(
                read.columns[column_at]
            ):
                _warn(errors.the_twelve_hour_style_was_held_back(name))
                continue
            # A LAYOUT COLUMN READ IN PART is a time of day without a
            # marker the partial reader takes on the 24-hour clock alone
            # (the Codex review of landing I3a, item 2), said so.
            if asking.layout_read_in_part(described_column) and parsing.layout_asks_twelve_hours(
                f"{described_column['format']}"
            ):
                _warn(errors.the_twelve_hour_declaration_did_not_reach_in_part(name))
                continue
            _warn(
                errors.the_twelve_hour_declaration_did_not_reach(
                    name, f"{described_column['role']}"
                )
            )

    # ...AND THE CENTURY, WHICH REACHES ONLY A COLUMN OF DATES WITH A
    # TWO-FIGURE YEAR (landing R2a, question Q5), said where it reached
    # nothing.
    for name in sorted(centuries):
        for described_column in _described_columns(document):
            if described_column["name"] != name:
                continue
            if (
                described_column["role"] == "datetime"
                and "format" in described_column
                and parsing.layout_two_figure_year(
                    f"{described_column['format']}"
                )
                == centuries[name]
            ):
                continue
            _warn(
                errors.the_century_declaration_did_not_reach(
                    name, f"{described_column['role']}"
                )
            )

    # -- 3b.R2c (P4-D383): ...AND THE DATES DECLARATION, WHICH REACHES A
    # COLUMN HALF OF WHOSE VALUES READ AS DATES, said where it reached none.
    for name in date_columns:
        for described_column in _described_columns(document):
            if described_column["name"] != name:
                continue
            if described_column["role"] == "datetime":
                continue
            _warn(
                errors.the_dates_declaration_did_not_reach(
                    name, f"{described_column['role']}"
                )
            )

    # A COLUMN DECLARED A MEASUREMENT HAS BEEN ANSWERED TOO, and this
    # list left it out until amendment A-P4-60. It cost nothing while
    # every unanswered column of figures was read as a measurement
    # anyway -- asking again named the reading the run was taking. It
    # costs the file its one promise now that a PADDED column is read
    # as codes: `--measurement dose` was honoured, `dose` came back
    # holding numbers, and the questions file asked about it again
    # under `read_as_now: code`, which is a reading the run did not
    # take. All three declarations are answers, so all three suppress
    # the question.
    already_answered = (
        forced_identifiers + forced_codes + forced_measurements
        # -- 3b.R4 (P4-D384): a column declared to write its dates as
        # counts has answered question Q3.
        + sorted(counted)
    )
    asked_about, split_columns = asking.questions_and_splits_for(
        document,
        read.columns,
        settings,
        already_answered,
        tuple(forced_decimal_commas),
    )
    # ...AND THE COLUMNS OF DATES OR TIMES THAT WRITE A FEW REPEATED
    # CODES (plan P4-D381), which are asked that and nothing else: the
    # joined question `00/00/0000` raises would offer a blood pressure
    # reading of a column of dates. They are put in the questions file
    # and said on the screen below rather than at the keyboard, where
    # each answer changes one column's reading: these declare spellings
    # every column reads, which the file's answers apply before the
    # table is described.
    #
    # WORKED OUT ONCE A RUN where nothing it reads changes (review of
    # lane R1, item 7): the screen and the questions file below reuse
    # this pass unless the interview rebuilt the description or moved
    # the settings or the declarations.
    codes_seen = asking.date_codes_seen(
        document,
        read.columns,
        settings,
        already_answered,
        split_columns,
        tuple(forced_decimal_commas),
        storage,
    )
    seen_of = (
        document,
        settings,
        list(already_answered),
        list(forced_decimal_commas),
    )
    coded_about = list(codes_seen.questions)
    # A column whose codes were answered `real-value` is asked no
    # question of what kind its values are either: the answer kept its
    # codes, and the joined question is no more the column's for that.
    # Its checklist line as a measurement stands (`checklist_for`).
    coded_or_answered = coded_about + list(codes_seen.answered)
    asked_about = asking.without_columns_of(asked_about, coded_or_answered)
    # ...AND THE ONE QUESTION ABOUT WHO THE ROWS ARE (plan P4-D340).
    # Asked only where the population is STILL COUNTED IN ROWS -- where
    # `settings.person_columns` is empty, which is exactly where nobody
    # has settled who the rows are about -- of a column whose values
    # repeat and are many or are written as codes: the shape a table
    # with several rows per subject wears. Until it existed, such a
    # table was counted in rows with nothing said and every subject's
    # identifier published beside its visit count; and until the review
    # of stage 3 (floor item 4) a declared identifier DIFFERENT ON
    # EVERY ROW silenced it while leaving the count in rows, which is
    # the same silence by a shorter route.
    asked_about = asked_about + asking.person_questions(
        document,
        read.columns,
        settings,
        already_answered,
        asked_about + coded_or_answered,
        split_columns,
    )
    # EVERY COLUMN READ AS A NUMBER, LISTED UNDER ONE QUESTION
    # (owner ruling 2026-09-10, amendment A-P4-58). The questions
    # above are the columns whose VALUES raised a question; these
    # are the ones no rule can reach, because a register of concept
    # identifiers and a column of ages are written identically. A
    # person reads one list and names the codes.
    listed_about = asking.checklist_for(
        document,
        read.columns,
        settings,
        already_answered,
        asked_about + coded_about,
        codes_seen.answered,
    )
    answered = False
    assumptions_said = False
    if asked_about:
        if _there_is_somebody_to_ask():
            given = _put_the_questions(asked_about)
            if given is None:
                _warn(errors.the_questions_were_not_finished())
                return 1
            (
                new_codes, new_identifiers, new_measured, new_commas,
                new_twelve, new_counted,
            ) = given
            # -- 3b.R4 (P4-D384): a column answered with a counting system
            # is read as those dates from here, and is no measurement.
            if new_counted:
                for counted_name, counted_member in new_counted:
                    counted[counted_name] = counted_member
                forced_measurements = [
                    named for named in forced_measurements if named not in counted
                ]
                settings = dataclasses.replace(
                    settings, forced_date_counts=_counted_settings(counted)
                )
            if new_twelve:
                twelve_hours = sorted(
                    {one: 1 for one in twelve_hours + new_twelve}
                )
                settings = dataclasses.replace(
                    settings, forced_twelve_hour_clocks=tuple(twelve_hours)
                )
            if (
                new_codes
                or new_identifiers
                or new_measured
                or new_commas
                or new_twelve
                or new_counted
            ):
                forced_decimal_commas = sorted(
                    [
                        named
                        for named in forced_decimal_commas
                        if named not in new_commas
                    ]
                    + new_commas
                )
                forced_codes = sorted(forced_codes + new_codes)
                forced_identifiers = sorted(
                    forced_identifiers + new_identifiers
                )
                forced_measurements = sorted(
                    forced_measurements + new_measured
                )
                # THE THREE ROLE DECLARATIONS ARE STILL THREE ANSWERS
                # TO ONE QUESTION, and an answer replaces the earlier
                # one rather than joining it (review item P4-G3-R4-F3).
                # The questions are suppressed for a column already
                # declared a code or a record number, but NOT for one
                # declared a measurement -- so `--measurement dose`
                # answered "code" put `dose` into both arrays, which
                # the command line refuses when both are typed and the
                # contract forbids outright. The newer statement wins,
                # exactly as it does for the comma declaration below.
                spoken_for = new_codes + new_identifiers
                forced_measurements = [
                    named
                    for named in forced_measurements
                    if named not in spoken_for
                ]
                forced_codes = [
                    named
                    for named in forced_codes
                    if named not in new_identifiers
                ]
                # AN ANSWER CAN CREATE THE PAIR THE FLAGS REFUSE
                # (review item P4-G3-R3-F3). The conflict checks above
                # run on what was TYPED, and a question answered "this
                # column holds codes" can put a column into
                # `forced_codes` that `--decimal-comma` already names
                # -- the pair that is refused on the command line,
                # arriving by a route that never rechecked. The
                # declaration would then be recorded and silently
                # ignored. So the same rule is applied to the answer,
                # and here it drops the comma declaration rather than
                # refusing the run: the person has just said, in
                # answer to a direct question, what the column holds,
                # and that is the newer and better-informed statement.
                dropped: "list[str]" = []
                kept_commas: "list[str]" = []
                for named in forced_decimal_commas:
                    if named in forced_codes or named in forced_identifiers:
                        dropped += [named]
                        continue
                    kept_commas += [named]
                forced_decimal_commas = kept_commas
                for named in dropped:
                    _warn(
                        errors.the_comma_declaration_was_answered_away(named)
                    )
                # THE POPULATION FLOOR AGAIN, WITH THE FINAL SET (plan
                # P4-D341), and this time it is final: the person has
                # just said on the screen which columns hold record
                # numbers, so a table counted in rows a moment ago may
                # be counted in people now and may be too small. It is
                # asked HERE, before anything is announced and before
                # anything is written, so a refusal still costs one
                # message and no files.
                # READ AFRESH under the final declarations, and handed
                # over again: the first census's readings were the
                # first description's.
                person_columns, population, unit, census_readings = (
                    _population_of(
                        read.column_names,
                        read.columns,
                        settings,
                        forced_identifiers,
                        forced_codes,
                        forced_measurements,
                        forced_decimal_commas,
                        storage,
                    )
                )
                if population < parsing.POPULATION_FLOOR:
                    _warn(
                        errors.the_population_is_too_small(
                            population,
                            unit,
                            _joined(list(person_columns), " and "),
                        )
                    )
                    return 1
                settings = dataclasses.replace(
                    settings, person_columns=person_columns
                )
                population_notes = profile.notes_for_a_small_population(
                    population, unit, parsing.POPULATION_NOTICE_LINE
                )
                census_box = [census_readings]
                census_readings = ()
                counted_in_people = []
                document = profile.build_document(
                    read,
                    settings,
                    forced_identifiers,
                    forced_codes,
                    forced_measurements,
                    forced_decimal_commas,
                    forced_metadata_rows=metadata_rows,
                    forced_delimiter=declared_delimiter,
                    table_notes=population_notes,
                    readings=_handed_once(census_box),
                    stored_as=storage,
                    subjects=list(person_columns),
                    counted_in_subjects=counted_in_people,
                )
                census_readings = ()
                # And the role check is asked again of the rebuilt
                # description, for the same reason.
                for name in sorted(forced_decimal_commas):
                    for rebuilt in _described_columns(document):
                        if rebuilt["name"] != name:
                            continue
                        if rebuilt["role"] in contract.DECIMAL_COMMA_HONOURED_ROLES:
                            continue
                        _warn(
                            errors.the_comma_declaration_did_not_reach(
                                name, f"{rebuilt['role']}"
                            )
                        )
            answered = True
        else:
            _say(f"\n{_assumptions_notice(asked_about)}\n")
            # THAT NOTICE ALREADY SAYS THE POPULATION WAS COUNTED IN
            # ROWS, in its own block, so the sentence below is not said
            # a second time (plan P4-D340). One fact, one place, on the
            # screen as well as on a page.
            assumptions_said = True
    # THE CHECKLIST IS SHOWN ONCE PER RUN, WHOEVER IS THERE (review
    # round 1 of landing L17a, item 1). It hung off the scripted notice
    # above, which fires only where a column's VALUES raised a question
    # and only where nobody is at the keyboard -- so three of the four
    # ways a person runs this command never saw it, and a table whose
    # only finding IS this list showed nothing at all. It is the one
    # class of column nothing else can reach, so it is the last thing
    # that should depend on another column raising a question.
    if listed_about:
        _say(f"\n{_checklist_notice(listed_about)}\n")
    # ...AND THE TWO QUESTIONS ABOUT DATES, ONCE PER RUN AND WHOEVER IS
    # THERE (plan P4-D381), for the checklist's reason: each is put in
    # the questions file, and a run whose only finding is one of them
    # would otherwise show nothing.
    settled = forced_identifiers + forced_codes + forced_measurements
    if not (
        document is seen_of[0]
        and settings == seen_of[1]
        and settled == seen_of[2]
        and list(forced_decimal_commas) == seen_of[3]
    ):
        codes_seen = asking.date_codes_seen(
            document,
            read.columns,
            settings,
            settled,
            split_columns,
            tuple(forced_decimal_commas),
            storage,
        )
        seen_of = (
            document,
            settings,
            list(settled),
            list(forced_decimal_commas),
        )
    if codes_seen.questions:
        _say(f"\n{_date_codes_notice(list(codes_seen.questions))}\n")
    # -- 3b.R2c (P4-D383): question Q6, WORKED OUT ONCE A RUN as the codes
    # question is (the R2c repair, item 3): each candidate is described
    # again under the declaration, three to four times its own describe,
    # so the questions file below reuses this unless the interview moved
    # what it reads. Worked out before Q5 and Q1 are, since the reading
    # each answer `dates` proposes joins theirs (the Codex review of
    # landing R2c, item 7).
    dates_seen = asking.date_columns_seen(
        document,
        read.columns,
        settings,
        settled + date_columns + dates_kept,
        split_columns,
        tuple(forced_decimal_commas),
        storage,
    )
    dates_asked = list(dates_seen.questions)
    dates_of = (
        document,
        settings,
        list(settled + date_columns + dates_kept),
        list(forced_decimal_commas),
    )
    # -- 3b.R2a (P4-D383): question Q5, said as the date questions are --
    # and of a column of dates beside codes whose answer `missing` reads
    # its years as two figures, in the same file (the Codex review of
    # landing R2a, item 5), and of one Q6's answer `dates` would read so
    # (the Codex review of landing R2c, item 7).
    century_asked = asking.century_questions(
        document,
        tuple(sorted(centuries)) + tuple(answered_centuries),
        also=codes_seen.century,
        dated=dates_seen.century,
    )
    if century_asked:
        _say(f"\n{_century_notice(century_asked)}\n")
    # ...and Q6 itself, said as Q5 is.
    if dates_asked:
        _say(f"\n{_date_column_notice(dates_asked)}\n")
    # A column of dates beside codes whose other cells read either way
    # is asked the order too, in the same file (review of lane R1, item
    # 4): answered `missing` alone, it would be read month first and
    # asked the order only by the file the answering run writes.
    day_or_month: "tuple[asking.DayOrMonth, ...]" = ()
    if not answered_month_first:
        day_or_month = asking.day_or_month_columns(
            document, read.columns, settings, split_columns,
            also=codes_seen.day_or_month + dates_seen.day_or_month,
        )
    day_or_month_of = (document, settings)
    if day_or_month:
        _say(f"\n{_day_or_month_notice(day_or_month)}\n")
    # HOW LARGE THE TABLE IS, SAID ONCE, WHOEVER IS THERE (plan
    # P4-D341). It is printed here because here the count is final:
    # the interview above is the last thing that can change which
    # columns name people, and nothing has been announced or written
    # yet. The sentence is the one the description carries, rendered
    # from the note itself rather than written again at this call site,
    # so the screen cannot drift from the five pages.
    for spoken in population_notes:
        _warn(
            _small_population_notice(
                f"{spoken}", _joined(list(person_columns), " and ")
            )
        )
    # AND WHERE NOBODY HAS SAID WHO THE ROWS ARE, THE SCREEN SAYS SO
    # (plan P4-D340). A person asked about a column that might name
    # people has to be told what this run did in the meantime, or the
    # question reads as a request for information rather than a
    # decision with a standing answer.
    person_asked: "list[str]" = []
    for question in asked_about:
        if question.reason == asking.BECAUSE_REPEATS_AND_MANY:
            person_asked += [question.name]
    if person_asked and not person_columns and not assumptions_said:
        _warn(_counted_in_rows_notice(person_asked))

    # NO VALUE OF A COLUMN WHOSE IDENTITY QUESTION IS STILL OPEN (plan
    # P4-D401). Where nobody was at the keyboard, a column a question
    # offering `identifier` was put to -- the person question, or one
    # asked because its values are shaped like record numbers -- and
    # that the questions file did not answer is described as record
    # numbers until it is answered, and the run says so. The questions
    # below are worked out from the description as the rules read it, so
    # the file asks exactly what it asked before; only what is WRITTEN
    # holds the column back. A person at the keyboard answered every
    # question put, Enter included, and nothing is held.
    withheld: "tuple[str, ...]" = ()
    if not answered:
        # EVERY DECLARATION IS AN ANSWER (Codex's review of lane HX, item
        # 1): `--decimal-comma amount` says `amount` holds measurements,
        # and a column also held as a record number would stand in two
        # declarations the contract refuses together (S8a).
        withheld = asking.unanswered_identities(
            asked_about + dates_asked + coded_about,
            document,
            tuple(
                forced_identifiers
                + forced_codes
                + forced_measurements
                + list(forced_decimal_commas)
                + list(twelve_hours)
                + list(date_columns)
                + sorted(counted)
            )
            + identities_kept,
        )
    published = document
    if withheld:
        _warn(_withheld_notice(withheld))
        # ...and the candidates of the open person question are the
        # people every other value is counted in (plan P4-D406).
        counted_in_people = []
        published = profile.build_document(
            read,
            settings,
            forced_identifiers,
            forced_codes,
            forced_measurements,
            forced_decimal_commas,
            forced_metadata_rows=metadata_rows,
            forced_delimiter=declared_delimiter,
            table_notes=population_notes,
            stored_as=storage,
            unanswered=list(withheld),
            subjects=list(person_columns)
            + [name for name in person_asked if name in withheld],
            counted_in_subjects=counted_in_people,
        )
    if counted_in_people:
        _warn(
            _counted_in_people_notice(
                tuple(dict.fromkeys(counted_in_people)), settings.small_cell_floor
            )
        )

    # The summary crosses the boundary ONCE, here, and the same text is
    # what reaches the screen and what is written to disk. The two
    # cannot differ, and the file on disk carries the same guarantee the
    # screen does -- it is opened in an editor or a terminal by the same
    # person, so it is a human-facing sink like any other.
    text = parsing.visible_lines(
        summary.render(
            published,
            _encoding_note(read.encoding, read.used_fallback_encoding),
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
    questions_path = profile.questions_output_path(
        pathlib.Path(table), out_dir
    )
    shown_questions_path = _shown(questions_path)
    # AND THE COLLISION IS DECIDED BEFORE THE ANNOUNCEMENT, not left to
    # the write (review item L17b-R1-1, second half). The transaction
    # refuses to land on the table and the table survives -- but a run
    # that announces "these three files will be written" and names the
    # person's own table among them has already said the frightening
    # thing, and then said nothing about why the third never appeared.
    # A name that resolves onto the table, the description or the
    # summary is named here, once, before anything exists, and the run
    # goes on to write the pair: a questions file is not something
    # anything else is built from, so losing it is a caution and not a
    # failure of the run.
    questions_collides = ""
    for place, noun in (
        (pathlib.Path(source), errors.INPUT_TABLE),
        (profile_path, errors.INPUT_DESCRIPTION),
        (summary_path, errors.INPUT_SUMMARY),
    ):
        if questions_path == place or profile.is_the_same_file(
            questions_path, place
        ):
            questions_collides = noun
            break
    if questions_collides:
        _say(
            f"These two files will be written:\n"
            f"  {shown_profile_path}\n  {shown_summary_path}"
        )
        _warn(
            errors.questions_would_replace_a_file(
                shown_questions_path, questions_collides
            )
        )
        _say(
            "\nBoth are computed from your real data. Keep them "
            "under the same rules your institution applies to the table "
            "itself, and read the section above before moving them "
            "anywhere."
        )
    else:
        _say(
            f"These three files will be written:\n"
            f"  {shown_profile_path}\n  {shown_summary_path}\n"
            f"  {shown_questions_path}"
        )
        _say(
            "\nAll three are computed from your real data. Keep them "
            "under the same rules your institution applies to the table "
            "itself, and read the section above before moving them "
            "anywhere."
        )
    # THE THIRD FILE IS WRITTEN AGAIN OVER THE ONE THAT WAS ANSWERED,
    # and a person who has just spent ten minutes filling it in must be
    # told that before it happens rather than after. It is not a loss:
    # the answers are in the description, the options that repeat them
    # are printed below, and the file that replaces it holds the
    # questions still open and no longer asks the ones answered. Said
    # only where the file named is the file about to be written, so a
    # person who kept their answers somewhere else is not warned about
    # a file synthtwin is not touching.
    if (
        answers_path is not None
        and not questions_collides
        and profile.is_the_same_file(
            questions_path,
            pathlib.Path(
                validate_local_path(answers_path, purpose="questions file")
            ),
        )
    ):
        _say(
            f"\nYour answers were read from {shown_questions_path} and "
            f"are recorded in the description. That file is about to be "
            f"written again: it will hold the questions still open, and "
            f"will no longer ask the ones you have answered."
        )
    # BOTH WARNINGS GO HERE, before the write, for the one reason (plan
    # P1-D6): a person weighs what a file carries before it exists, not
    # after they have been told where it is. The declared-word notice is
    # printed first and the floor alarm last, because the floor alarm
    # has a reminder line of its own after the "Written:" confirmation
    # and reading the two in that order leaves the pointer beside the
    # block it points at.
    # WHAT AN ANSWER REPLACED, to be taken out of the typed command (the
    # Codex review of lane R1, item 7).
    taken_out: "list[str]" = []
    # -- 3b.R4 (P4-D384): a typed `--date-count` an answer replaced.
    for typed_name in sorted(typed_counted):
        if typed_name not in counted or counted[typed_name] != typed_counted[typed_name]:
            taken_out += [
                f"{_typed_option('--date-count', typed_name)} "
                f"{typed_counted[typed_name]}"
            ]
    for option, typed_list, final in (
        ("--code", typed_codes, forced_codes),
        ("--identifier", typed_identifiers, forced_identifiers),
        ("--measurement", typed_measurements, forced_measurements),
        ("--decimal-comma", typed_commas, list(forced_decimal_commas)),
        ("--keep-value", typed_kept, list(kept_values)),
        ("--missing-value", typed_missing, list(missing_values)),
    ):
        final_of = {one: 1 for one in final}
        for one in typed_list:
            if one not in final_of:
                taken_out += [_typed_option(option, one)]
    if (answered or answers_were_handed_back) and (
        counted
        or forced_codes
        or forced_identifiers
        or forced_measurements
        or forced_decimal_commas
        or twelve_hours
        or added_missing
        or added_kept
        or answered_day_first
        or taken_out
        or centuries
        or date_columns
    ):
        _say(
            _how_to_repeat(
                forced_codes,
                forced_identifiers,
                forced_measurements,
                tuple(forced_decimal_commas),
                tuple(twelve_hours),
                _counted_settings(counted),
                answered_missing=tuple(added_missing),
                answered_kept=tuple(added_kept),
                answered_day_first=answered_day_first,
                taken_out=tuple(taken_out),
                centuries=tuple(
                    (one_century, centuries[one_century])
                    for one_century in sorted(centuries)
                ),
                date_columns=tuple(date_columns),
            )
        )
    kept_of_yours = summary.words_of_your_own(published)
    if kept_of_yours:
        _warn(_declared_words_notice(kept_of_yours, tuple(added_missing)))
    if floor_chosen and smallest_group < _NOTICE_LINE:
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
            profile.serialize(published),
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
    # THE QUESTIONS FILE, AFTER THE PAIR AND OUTSIDE THEIR TRANSACTION
    # (amendment A-P4-58). The description and its summary are one
    # outcome because either alone is a failure state; nothing is built
    # from this one, so a run that wrote the pair and could not write
    # this has still produced a complete description, and says so
    # rather than undoing work that succeeded.
    #
    # THE QUESTIONS ARE RECOMPUTED HERE, FROM THE FINISHED DESCRIPTION
    # (review item L17b-R1-3). They were worked out before the
    # interview and reused after it, so a person who answered `code` at
    # the terminal got a rebuilt description holding labels and a
    # questions file still asking about that column under
    # `read_as_now: measurement` -- a file naming a reading the run did
    # not take, which is the one thing this file may never be. The
    # inputs here are the FINAL document and the FINAL declarations, so
    # an answered column is gone and every reading left is the one in
    # force.
    settled = forced_identifiers + forced_codes + forced_measurements
    asked_about, split_columns = asking.questions_and_splits_for(
        document, read.columns, settings, settled, tuple(forced_decimal_commas)
    )
    # ...AND THE COLUMNS OF DATES OR TIMES BESIDE A FEW CODES, recomputed
    # from the FINAL settings (plan P4-D381): a column whose codes were
    # answered `missing` reads as dates now and is asked nothing, and one
    # answered `real-value` has its codes declared kept.
    if not (
        document is seen_of[0]
        and settings == seen_of[1]
        and settled == seen_of[2]
        and list(forced_decimal_commas) == seen_of[3]
    ):
        codes_seen = asking.date_codes_seen(
            document,
            read.columns,
            settings,
            settled,
            split_columns,
            tuple(forced_decimal_commas),
            storage,
        )
    coded_about = list(codes_seen.questions)
    coded_or_answered = coded_about + list(codes_seen.answered)
    asked_about = asking.without_columns_of(asked_about, coded_or_answered)
    # -- 3b.R2c (P4-D383): QUESTION Q6 from the FINAL settings, worked out
    # again only where the interview moved what it reads, and before Q1
    # and Q5, whose collections take the reading each answer `dates`
    # proposes (the Codex review of landing R2c, item 7).
    dates_moved = not (
        document is dates_of[0]
        and settings == dates_of[1]
        and settled + date_columns + dates_kept == dates_of[2]
        and list(forced_decimal_commas) == dates_of[3]
    )
    if dates_moved:
        dates_seen = asking.date_columns_seen(
            document,
            read.columns,
            settings,
            settled + date_columns + dates_kept,
            split_columns,
            tuple(forced_decimal_commas),
            storage,
        )
        dates_asked = list(dates_seen.questions)
    if dates_moved or not (
        document is day_or_month_of[0] and settings == day_or_month_of[1]
    ):
        day_or_month = (
            ()
            if answered_month_first
            else asking.day_or_month_columns(
                document, read.columns, settings, split_columns,
                also=codes_seen.day_or_month + dates_seen.day_or_month,
            )
        )
    # ...AND THE PERSON QUESTION, recomputed from the FINAL
    # declarations like every other (plan P4-D340). A column answered
    # `identifier` at the terminal is declared now, so the file that
    # replaces this one no longer asks about it -- and the settings
    # carried here are the rebuilt ones, whose `person_columns` says
    # whether that answer settled who the rows are about.
    asked_about = asked_about + asking.person_questions(
        document,
        read.columns,
        settings,
        settled,
        asked_about + coded_or_answered,
        split_columns,
    )
    # -- 3b.R2c (P4-D383): QUESTION Q6, BESIDE every other question its
    # column raises: an accession number written `2024-252` is asked
    # whether it is dates and, as before, whether it is a code or a
    # record number, since only the person knows which.
    asked_about = asked_about + dates_asked
    listed_about = asking.checklist_for(
        document, read.columns, settings, settled,
        asked_about + coded_about, codes_seen.answered,
    )
    asked_about = asked_about + coded_about
    # ...AND QUESTION Q5, of every column of dates whose years are two
    # figures and whose century nobody gave (landing R2a), and of every
    # column the codes question would read so (the Codex review of
    # landing R2a, item 5), and of every column Q6's answer `dates` would
    # read so (the Codex review of landing R2c, item 7).
    asked_about = asked_about + asking.century_questions(
        document,
        tuple(sorted(centuries)) + tuple(answered_centuries),
        also=codes_seen.century,
        dated=dates_seen.century,
    )
    # AND ITS DESTINATION IS GUARDED LIKE ANY OTHER (review item
    # L17b-R1-1). On POSIX a link left at this name resolves to a
    # permitted local path, so the locality gate cannot catch it: what
    # would be destroyed is the person's own table, or the description
    # this run has just finished writing. The pair above is guarded
    # against the table by `is_the_same_file`; this write is guarded
    # against all three by the transaction itself, which asks by
    # lexical path, by resolved path, by the case-folded spelling and
    # by the filesystem's own identity -- and asks AGAIN once the file
    # is at its name, where a substitution made in between becomes
    # decidable.
    guarded_questions = [
        (pathlib.Path(source), errors.INPUT_TABLE),
        (profile_path, errors.INPUT_DESCRIPTION),
        (summary_path, errors.INPUT_SUMMARY),
    ]
    if questions_collides:
        # Said once, before the files existed. Repeating it here would
        # be the same sentence twice with the run's outcome between
        # them, which reads as two separate troubles.
        if floor_chosen and smallest_group < _NOTICE_LINE:
            _warn(f"\n{_LOWERED_FLOOR_REMINDER}")
        _say(_teaching_generate(profile_path))
        return 0
    written_questions = True
    questions_state = writing.DiskState()
    left_questions: "list[str]" = []
    try:
        left_questions = writing.write_one_file(
            questions_path,
            canonical.serialize(
                asking.questions_document(
                    _shown(pathlib.Path(table).name),
                    # -- P4-D401: a column held back is read as record
                    # numbers until answered, and its entry says so.
                    asking.held_back(asked_about, withheld),
                    listed_about,
                    asking.file_questions(
                        surveyed is not None
                        and surveyed.metadata_shape
                        and not metadata_rows,
                        # ...and the same subject from the other side:
                        # a declaration the file does not bear out was
                        # not acted on, so the person is asked here
                        # rather than having it done to their table.
                        metadata_rows if metadata_declaration_unseen else 0,
                        # ...and the delimiter, where the file reads
                        # equally well under more than one (P4-D110).
                        delimiter_tie,
                        # ...and which row the column names are in,
                        # where the first row could not be told from a
                        # record of the table (the owner's ruling of
                        # 2026-09-17, item 8; plan P4-D232). The words
                        # are what the FILE showed, and no cell of it.
                        read.first_row_seen,
                        # ...and which comes first, the day or the month,
                        # where no value of a column of dates can say
                        # (plan P4-D381), from the FINAL settings -- and
                        # not to a person whose file answered it. The
                        # screen's pass, where nothing has moved since.
                        day_or_month=day_or_month,
                    ),
                    # ...AND WHAT THIS RUN SAID ABOUT THE TABLE AS A
                    # WHOLE (plan P4-D341). The population notice, in
                    # the description's own words, because this file
                    # travels on its own and a page naming the columns
                    # of a small table without saying it is a small
                    # table says less than the other four do.
                    _table_sentences(document),
                    # ...and an entry the file answered with a
                    # declaration, written back answered so that handing
                    # this file back keeps the answer (plan P4-D401).
                    answered=asking.answered_again(
                        answered_entries, asked_about + listed_about
                    ),
                )
            ),
            sources=guarded_questions,
            state=questions_state,
        )
    except (KeyboardInterrupt, SystemExit):
        # THE PERSON STOPPING THEIR OWN COMMAND IS NOT A WRITE FAILURE
        # (review item L17b-R1-4). Swallowing it turned Ctrl-C into exit
        # 0 and told them the run had finished. The disk is described
        # first, then the stop continues as itself so that `main`'s
        # handler still recognizes it.
        if questions_state.sentence:
            _warn(_shown(questions_state.sentence))
        elif questions_state.target_written:
            _say(f"  {shown_questions_path}")
            if questions_state.left_behind:
                _warn(_left_behind_note([questions_state.left_behind]))
        raise
    except BaseException:
        written_questions = False
    if written_questions:
        _say(f"  {shown_questions_path}")
        if left_questions:
            # The same caution the pair above prints, for the same
            # reason: a working file this run could not clear away is a
            # real-derived file sitting in the person's folder under a
            # name nobody gave them (review item P1-R6-F5). Discarding
            # this list was item L17b-R1-4's other half.
            _warn(_left_behind_note(left_questions))
    else:
        if questions_state.sentence:
            _warn(_shown(questions_state.sentence))
        _warn(
            f"\nThe description is written and complete. synthtwin could "
            f"not write its questions beside it at "
            f"{shown_questions_path}, so the columns it could not "
            f"settle are named on the screen above and nowhere else."
        )

    if floor_chosen and smallest_group < _NOTICE_LINE:
        _warn(f"\n{_LOWERED_FLOOR_REMINDER}")
    _say(_teaching_generate(profile_path))
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
    description: pathlib.Path,
    out_dir: "str | None",
    packaged: bool = False,
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
    ending = _WORKBOOK_TWIN_SUFFIX if packaged else _TWIN_SUFFIX
    twin_target = validate_local_path(
        f"{folder / (stem + ending)}", purpose="output file"
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
    from synthtwin import (
        contract,
        generation,
        rendering,
        sheetwriting,
        writing,
    )

    seed, refusal = _seed_or_refusal(seed_given)
    if seed is None:
        _warn(refusal)
        return 2
    loaded = contract.load_profile(description)
    # A WORKBOOK'S TWIN IS A WORKBOOK, AND IT IS WRITTEN AS ONE (plan
    # P4-D79, which supersedes P4-D78's refusal). The description says
    # which the table was, so the twin's name, its bytes and the rules
    # it is written by all follow from `source.workbook` rather than
    # from anything this run reads.
    packaged = loaded.source.workbook is not None
    twin_path, report_path = _twin_paths(
        pathlib.Path(description), out_dir, packaged
    )
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
                taken += [_shown(target)]
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
    # A WORKBOOK TWIN IS BYTES AND A DELIMITED ONE IS TEXT, and the two
    # are kept apart from here to the write: a zip package put through
    # an encoding and a line-ending rule would be corrupted by both.
    # THE TWIN IS WRITTEN IN ITS TABLE'S OWN ENCODING (plan P4-D86), and
    # that is checked before anything is shown or written: a cell holding
    # a character the encoding has no byte for would otherwise stop the
    # write half way. Every published label was read in that encoding and
    # every made-up value is ASCII, so reaching this is a defect.
    #
    # A WORKBOOK ANSWERS NONE OF IT (plan P4-D79). Its parts are written
    # as UTF-8 inside a zip package whatever the source's encoding was,
    # because that is what a spreadsheet file IS; the source encoding
    # describes a delimited file's bytes and there are none here.
    twin_codec = dialect.WRITING_CODECS[loaded.source.encoding]
    twin_members: "list[tuple[str, str]] | None" = None
    twin_text = ""
    if packaged:
        twin_members = sheetwriting.workbook_members(loaded, twin)
    else:
        written = rendering.twin_csv(twin)
        try:
            written.encode(twin_codec)
        except UnicodeEncodeError:
            _warn(
                errors.twin_not_writable_in_encoding(
                    dialect.ENCODING_WORDS[loaded.source.encoding]
                )
            )
            return 1
        twin_text = written
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
            first_encoding=twin_codec,
            first_newline="",
            first_members=twin_members,
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


def _teaching_generate(description: pathlib.Path) -> str:
    """The lines that end every `profile` run that wrote a description (plan P4-D397).

    The first link of the teaching chain `_teaching_validate` describes:
    `profile` ends by teaching `generate`. Until this function it did
    not, although README and this module promised it (the R5 map's pain
    point 6). It is printed on each way a run that wrote the description
    can end -- with the questions file beside it or without -- and it
    is the last thing on the screen's ordinary output, so a person who
    reads nothing else reads what to type next. The path is the
    description just written, quoted for the shell (`_typed_path`).
    """
    line = f"synthtwin generate {_typed_path(description)}"
    return (
        f"\nNext, build the twin from this description:\n"
        f"  {line}{_quoting_said(line)}"
    )


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
    prints, and are quoted for the shell (`_typed_path`, the Codex review
    of lane R1, item 1), which the line then names where it quotes one.
    """
    line = (
        f"synthtwin validate {_typed_path(description)} "
        f"{_typed_option('--twin', twin_path)}"
    )
    return (
        f"\nNext, measure the twin against the description:\n"
        f"  {line}{_quoting_said(line)}\n"
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
    collide with any of the five artifacts that already exist by the time
    this command runs, which end '-profile.json', '-profile.txt',
    '-questions.json', '-twin.csv' and '-twin-report.txt'. The questions
    file joined that list when it shipped (amendment A-P4-58) and this
    sentence counted four until the review of 2026-09-23.
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


def _measured_path(
    description: str, twin_given: "str | None", packaged: bool = False
) -> str:
    """Which file this run measures: the one named, or the twin beside it.

    The default is derived from the DESCRIPTION's own folder rather than
    from `--out-dir`, because `--out-dir` says where this command writes
    and says nothing about where an earlier `generate` run put its twin.
    A person whose twin is somewhere else names it with `--twin`, which
    is the line the finished `generate` run taught them.
    """
    if twin_given is not None:
        return twin_given
    twin_path, _report_path = _twin_paths(
        pathlib.Path(description), None, packaged
    )
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
    sheet: str = "",
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
    measured = _measured_path(
        description, twin_given, loaded.source.workbook is not None
    )
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

    # `--sheet` REACHES THIS COMMAND TOO (repair of landing 2b.10). The
    # option was accepted here and then dropped on the floor: a person
    # checking a real workbook whose table is not on the first visible
    # sheet named the sheet, was given no error, and had a different
    # sheet measured against their description.
    outcome = validation.measure(loaded, measured, sheet)
    # The report is a human-facing sink like the profiler's summary and
    # the twin's report, so it crosses the display boundary once, here,
    # and the same text is what reaches the screen and what is written to
    # disk. The two cannot differ. AND IT IS NEVER MADE WHOLE (stage 4
    # lane S4c, plan P4-D390): it crosses in the pieces
    # `quality.report_pieces` hands over, which add up to
    # `quality.quality_report`'s text, and each is printed and written in
    # turn. The display boundary reads one character at a time, so the
    # pieces cross it as the whole text would.
    report_pieces = quality.report_pieces(loaded, outcome)
    for index in range(len(report_pieces)):
        report_pieces[index] = parsing.visible_lines(report_pieces[index])
    code = 3 if outcome.census.missed else 0

    _say_pieces(report_pieces)
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
            "",
            sources=guarded,
            state=state,
            words=errors.QUALITY_WORDS,
            pieces=report_pieces,
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


# -- checking this computer before a first run (plan P4-D397) ----------

# THE PYTHON THIS PACKAGE NEEDS, as pyproject.toml's `requires-python`
# states it. An older one cannot even install the package, so this line
# is for the person whose environment was built by another Python than
# the one they think. An older Python running `python -m synthtwin` from
# a source folder never reaches this module: `__main__.py` says so before
# importing it, since this module's own syntax needs 3.10.
_PYTHON_FLOOR = (3, 10)

# HOW MUCH MEMORY A TEXT TABLE TAKES TO READ, AS A MULTIPLE OF ITS FILE'S
# SIZE. Measured, not guessed: `K-S4-02` reads a fifty-column table of
# about 480 bytes a row at a peak of 4.38 kilobytes a row above the
# start, about nine times the file (plan P4-D387), and describing it
# needs more on top. Ten is that measurement rounded up. It holds for a
# file of plain text only, and the line says it is a guess from the
# size alone.
_MEMORY_PER_FILE_BYTE = 10

# A WORKBOOK'S SIZE SAYS NOTHING OF WHAT READING IT TAKES: it is a
# packed file, and a few megabytes of it can hold a million cells. What
# bounds it is the reader's cell cap (`workbook.MAXIMUM_CELLS`, one
# million), measured at 632 megabytes of peak memory for 1,048,708
# cells (workbook.py, plan A-P4-66). So a workbook is weighed at that
# bound whatever its size (the Codex review of lane TI, item 9).
# A workbook is known by its name's ending, `.xlsx` or `.xlsm`, since
# doctor reads none of its bytes (written out in `_check_table`).
_WORKBOOK_READ_BYTES = 632 * 1024 * 1024

# A table counts as large for this computer when what reading it takes
# passes half the memory, the other half being what the system and the
# person's other programs hold.

# The small file `doctor` writes and removes to learn whether the
# output folder takes a file. A leading point keeps it out of most
# folder views for the instant it exists.
_DOCTOR_PROBE = ".synthtwin-doctor-check"

# What to do when a package is missing or Python is the wrong one, in
# words a person who has never programmed can act on.
_INSTALL_AGAIN = (
    "run the install script again from the synthtwin folder -- "
    "sh scripts/install.sh on a Mac or Linux, scripts\\install.bat on "
    "Windows -- or see 'Installing' in README.md"
)

# Where a Mac lets a terminal reach a protected folder (the Desktop,
# Documents and Downloads, until the person allows it).
_MAC_FOLDER_ACCESS = (
    "On a Mac, let Terminal reach that folder (System Settings, then "
    "Privacy & Security, then Files and Folders)"
)


@dataclasses.dataclass(frozen=True)
class _Check:
    """One line of `synthtwin doctor`: whether it passed, whether it was made, its words.

    A check that could not be made -- this computer's memory where the
    standard library cannot read it -- is a note: no failure, and no
    pass either, so the closing line does not claim it.
    """

    passed: bool
    made: bool
    line: str


def _passed(line: str) -> _Check:
    return _Check(True, True, f"  ok       {line}")


def _noted(line: str) -> _Check:
    return _Check(True, False, f"  note     {line}")


def _failed(line: str) -> _Check:
    return _Check(False, True, f"  PROBLEM  {line}")


def _python_version() -> "tuple[int, int, int]":
    """The running Python's version, read in one place so a test can set it."""
    return (sys.version_info[0], sys.version_info[1], sys.version_info[2])


def _check_python(version: "tuple[int, int, int]") -> _Check:
    spoken = f"{version[0]}.{version[1]}.{version[2]}"
    if (version[0], version[1]) >= _PYTHON_FLOOR:
        return _passed(f"Python {spoken} (3.10 or later is needed)")
    return _failed(
        f"Python {spoken} is too old: synthtwin needs Python 3.10 or "
        f"later. Install a newer Python (see 'Before you start' in "
        f"README.md), then {_INSTALL_AGAIN}."
    )


def _not_loaded(package: str, needed_for: str) -> _Check:
    return _failed(
        f"{package} could not be loaded, and synthtwin needs it to "
        f"{needed_for}. To put it in place, {_INSTALL_AGAIN}."
    )


def _check_numpy() -> _Check:
    # A plain import, in this function alone: the check is whether the
    # package loads, and nothing of it is used here (plan P2-D1 keeps
    # the generator's own import inside `_run_generate`). Any exception
    # is a failed load, not ImportError alone: a build made for another
    # Python or another numpy raises ValueError or RuntimeError as it
    # loads, and the check says so instead of stopping (the Codex
    # review of lane TI, item 7).
    try:
        import numpy.random  # noqa: F401
    except Exception:  # noqa: BLE001 -- see above
        return _not_loaded("numpy", "build a twin")
    return _passed("numpy can be loaded")


def _check_pandas() -> _Check:
    # The same plain import, for the reader's one library. It is loaded
    # and nothing of it is called: `doctor` reads no table.
    try:
        import pandas  # noqa: F401
    except Exception:  # noqa: BLE001 -- as in _check_numpy
        return _not_loaded("pandas", "read a table")
    return _passed("pandas can be loaded")


def _total_memory() -> "int | None":
    """This computer's total memory in bytes, or None where it cannot be read.

    `os.sysconf` reports it on macOS and Linux and does not exist on
    Windows, and the standard library has no other way to ask without
    starting a program or calling native code, which this package never
    does (charter principle 3). Total memory, not free memory: no
    portable call reports what is free.
    """
    if sys.platform == "win32":
        return None
    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
    except (ValueError, OSError, AttributeError):
        return None
    if pages <= 0 or page_size <= 0:
        return None
    return pages * page_size


def _size_words(size: int) -> str:
    """A size in bytes as a person reads it: 512 bytes, 3.4 MB, 24.0 GB."""
    if size < 1024:
        return f"{size} bytes"
    amount = float(size)
    for unit in ("KB", "MB", "GB", "TB"):
        amount = amount / 1024
        if amount < 1024 or unit == "TB":
            return f"{amount:.1f} {unit}"
    return f"{size} bytes"


def _check_memory(memory: "int | None") -> _Check:
    if memory is None:
        # A note, not a failure: Windows simply does not say, and
        # nothing the person does changes that.
        return _noted(
            "This computer's memory could not be read here, so a table's "
            "size cannot be weighed against it"
        )
    return _passed(f"This computer has {_size_words(memory)} of memory")


def _not_allowed(shown: str, otherwise: str) -> _Check:
    """The file system refused to say anything of a path: what to do (lane TI, item 2)."""
    return _failed(
        f"synthtwin is not allowed to look at {shown}. "
        f"{_MAC_FOLDER_ACCESS}, or {otherwise}; then run synthtwin "
        f"doctor again."
    )


def _check_output_folder(raw: str) -> _Check:
    """Whether a file can be written in the folder, learned by writing one.

    The folder goes through the path validator like every path this
    module uses. The test file is created only where nothing at all
    stands at its name -- not a file, not a link, not a dangling link --
    and created exclusively, so it is made in this folder or not at all
    (the Codex review of lane TI, item 6); it is removed at once. Every
    question asked of the file system is answered with a line, a refusal
    of permission included, never a stack trace.
    """
    choose = "choose a folder of your own with --out-dir FOLDER"
    try:
        folder = validate_local_path(raw, purpose="output folder")
    except PathValidationError as error:
        return _failed(_shown(error))
    except OSError:
        return _not_allowed(_shown(raw), choose)
    shown = _shown(folder)
    named = os.path.join(f"{folder}", _DOCTOR_PROBE)
    # One `stat` asks whether the folder is there, and only a missing
    # path (or a file standing where a folder of the path should be) is
    # "not there": any other refusal is a refusal of permission. Path's
    # exists() and is_dir() are not asked, since from Python 3.14
    # they answer False where they may not look, which would send the
    # person to make a folder that already exists (lane TI, repair 2).
    try:
        folder.stat()
    except (FileNotFoundError, NotADirectoryError):
        there = False
    except OSError:
        return _not_allowed(shown, choose)
    else:
        there = True
    # Asked once the look succeeded, through os.path, which answers and
    # never raises.
    a_folder = there and os.path.isdir(folder)
    taken = a_folder and os.path.lexists(named)
    if not there:
        return _failed(
            f"The output folder {shown} does not exist. Make it first, or "
            f"name a folder that exists with --out-dir FOLDER."
        )
    if not a_folder:
        return _failed(
            f"{shown} is a file, not a folder. Name the folder synthtwin "
            f"should write into with --out-dir FOLDER."
        )
    taken_said = (
        f"Something named {_DOCTOR_PROBE} is already in {shown}, and "
        f"synthtwin does not touch what it did not just make. Move or "
        f"rename it, or {choose}; then run synthtwin doctor again."
    )
    if taken:
        return _failed(taken_said)
    # Built the way every file this package writes is built -- through
    # the path validator, then `pathlib.Path` -- so the offline audit
    # traces the handle it opens (plan D6.2).
    try:
        probe = pathlib.Path(
            validate_local_path(named, purpose="output folder")
        )
    except PathValidationError as error:
        return _failed(_shown(error))
    except OSError:
        return _not_allowed(shown, choose)
    try:
        # Exclusive creation: it fails on anything standing at the name,
        # a link included, rather than following it.
        probe.touch(exist_ok=False)
    except FileExistsError:
        return _failed(taken_said)
    except OSError:
        return _failed(
            f"synthtwin could not save a file in {shown}. Choose a folder "
            f"you can save files in, such as one inside your Documents "
            f"folder, and name it with --out-dir FOLDER."
        )
    try:
        probe.unlink()
    except OSError:
        return _passed(
            f"The output folder {shown} takes a file, but the test file "
            f"could not be removed: delete {_shown(probe)}"
        )
    return _passed(f"The output folder {shown} takes a file")


def _check_table(raw: str, memory: "int | None") -> _Check:
    """The table's size against this computer's memory; the table is never opened.

    The path is validated and its size asked of the file system, which
    reads no byte of the file. The size and the name's suffix are all
    `doctor` is told, and a refusal of permission is a line, not a stack
    trace (lane TI's skeptic, item 2).
    """
    try:
        table = validate_local_path(raw, purpose="table")
    except PathValidationError as error:
        return _failed(_shown(error))
    except OSError:
        return _not_allowed(
            _shown(raw), "move the table into a folder of your own"
        )
    shown = _shown(table)
    # As in _check_output_folder: one `stat`, whose only "not there" is
    # a missing path; any other refusal is a refusal of permission,
    # on every Python from 3.10 on (lane TI, repair 2).
    moved = "move the table into a folder of your own"
    try:
        size = table.stat().st_size
    except (FileNotFoundError, NotADirectoryError):
        there = False
        size = 0
    except OSError:
        return _not_allowed(shown, moved)
    else:
        there = True
    a_folder = there and os.path.isdir(table)
    if not there:
        return _failed(
            f"There is no file at {shown}. Check the spelling of the path, "
            f"and put quotation marks around it if it has a space in it."
        )
    if a_folder:
        return _failed(
            f"{shown} is a folder. Name the table's own file, such as "
            f"my-table.csv."
        )
    spelled = f"{table}".lower()
    workbook = spelled.endswith(".xlsx") or spelled.endswith(".xlsm")
    return _weighed(size, workbook, memory)


def _weighed(size: int, workbook: bool, memory: "int | None") -> _Check:
    """What reading a table of this size takes, against the memory, in words.

    A text table is weighed at ten times its size, said to be a guess
    from the size alone; a workbook at the reader's measured bound,
    whatever its size, since a packed file's size does not say.
    """
    if workbook:
        needed = _WORKBOOK_READ_BYTES
        estimate = (
            f"a workbook's size does not say what reading it takes, and "
            f"synthtwin reads at most a million cells of one, which takes "
            f"about {_size_words(needed)}"
        )
    else:
        needed = size * _MEMORY_PER_FILE_BYTE
        estimate = (
            f"reading it takes roughly {_size_words(needed)}, a guess "
            f"from the file's size alone"
        )
    said = f"The table is {_size_words(size)}; {estimate}"
    if memory is None:
        return _noted(
            f"{said}. This computer's memory could not be read, so that "
            f"could not be weighed against it"
        )
    if needed > memory // 2:
        return _failed(
            f"{said}, which is large for this computer's "
            f"{_size_words(memory)}. synthtwin may run out of memory on "
            f"it. Close other programs before you start, use a computer "
            f"with more memory, or describe a smaller extract of rows "
            f"taken from the whole table first."
        )
    return _passed(f"{said}, which fits this computer's {_size_words(memory)}")


def _doctor_checks(table: "str | None", out_dir: "str | None") -> "list[_Check]":
    """Every check `synthtwin doctor` makes, one line each, in order.

    The output folder is the one `--out-dir` names, else the table's
    folder (where `profile` writes), else the current folder.
    """
    memory = _total_memory()
    checks = [
        _check_python(_python_version()),
        _check_numpy(),
        _check_pandas(),
    ]
    if out_dir is not None:
        folder = out_dir
    elif table is not None:
        folder = os.path.dirname(os.path.abspath(table))
    else:
        folder = "."
    checks += [_check_output_folder(folder), _check_memory(memory)]
    if table is not None:
        checks += [_check_table(table, memory)]
    return checks


def _run_doctor(table: "str | None", out_dir: "str | None") -> int:
    """`synthtwin doctor`: one plain line per check, then what to do next.

    Guarantees: returns 0 when every check passed or could not be made,
    and 1 when any did not pass. Boundary: a named table is never opened
    -- its size is asked of the file system and nothing else -- and the
    one file written is the test file in the output folder, removed at
    once. No network, subprocess, native or dynamic-code operation.
    """
    _say(f"synthtwin {_version()}: checking this computer before a first run.")
    checks = _doctor_checks(table, out_dir)
    failed = 0
    unmade = 0
    for check in checks:
        _say(check.line)
        if not check.passed:
            failed += 1
        elif not check.made:
            unmade += 1
    if failed:
        _say(
            f"\n{failed} check(s) did not pass. Do what the line marked "
            f"PROBLEM says, then run this again:\n"
            f"{_doctor_again(table, out_dir)}"
        )
        return 1
    passed = "Every check that could be made passed." if unmade else "Every check passed."
    _say(f"\n{passed} {_teaching_profile(table, out_dir)}")
    return 0


def _typed_with_folder(line: str, out_dir: "str | None") -> str:
    """A command line, with `--out-dir` as the person typed it when they did."""
    if out_dir is None:
        return line
    return f"{line} {_typed_option('--out-dir', out_dir)}"


def _doctor_again(table: "str | None", out_dir: "str | None") -> str:
    """The line a failed `doctor` ends with: the same check, as the person typed it."""
    line = "synthtwin doctor"
    if table is not None:
        line = f"{line} {_typed_path(table)}"
    line = _typed_with_folder(line, out_dir)
    return f"  {line}{_quoting_said(line)}"


def _teaching_profile(table: "str | None", out_dir: "str | None" = None) -> str:
    """The line that ends a passing `doctor`: the first command of a run.

    It names the table and the output folder doctor was given, so the
    folder it checked is the one `profile` writes into.
    """
    named = "my-table.csv" if table is None else _typed_path(table)
    line = _typed_with_folder(f"synthtwin profile {named}", out_dir)
    return (
        f"Next, describe your table:\n"
        f"  {line}{_quoting_said(line)}"
    )


def main(argv: "list[str] | None" = None) -> int:
    """Run the `synthtwin` command.

    Guarantees:

    - Inputs: `argv` is the list of command-line arguments to parse, or
      `None` to parse `sys.argv[1:]`. Recognized: `--version`, `--help`,
      the `profile` command word with its options, the `generate`
      command word with `--seed`, `--out-dir` and `--replace`, the
      `validate` command word with `--twin`, `--out-dir` and
      `--replace`, and the `doctor` command word with an optional table
      path and `--out-dir` (plan P4-D397).
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

      `doctor` returns 0 when every check it printed passed and 1 when
      any did not, each failed line saying what to do next.
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
      re-encodes either of the two files it read. A `doctor` run opens
      no table: it asks the file system for a named table's size, and
      the one file it writes is a test file in the output folder,
      removed at once. No network,
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

    if options.command == _DOCTOR:
        return _run_doctor(options.given, options.out_dir)

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
                named,
                options.twin,
                options.out_dir,
                options.replace,
                options.sheet,
            )
        return _run_profile(
            named,
            options.out_dir,
            options.smallest_group,
            options.floor_chosen,
            options.identifiers,
            options.codes,
            options.measurements,
            options.decimal_commas,
            options.answers,
            options.kept_values,
            options.missing_values,
            options.first_row,
            options.day_first,
            options.sheet,
            options.metadata_rows,
            options.delimiter,
            options.date_counts,
            options.twelve_hours,
            options.centuries,
            options.date_columns,
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
    except RecursionError:
        # A STEP NESTED PAST PYTHON'S OWN LIMIT ends here and never as a
        # stack trace (plan P4-D380). The pool walk that did it on columns
        # of numbers written to full precision carries its own stack now;
        # this is what any step that still reaches the limit says, on the
        # file the person typed, whichever of the three commands it was.
        _warn(errors.stopped_nested_too_deep(_shown(named)))
        return 1


if __name__ == "__main__":
    sys.exit(main())

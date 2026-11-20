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
run: it checks this computer before the first one -- Python, the four
libraries it needs (numpy, pandas, pyarrow and scipy, each with its
version), the output folder, the memory against a named table's size --
and reads no table (plans P4-D397 and P4-D410). And `synthtwin twin
<table>` runs the three in one command and one folder, the questions on
screen before any file is written, while `synthtwin help` shows one page
for each command and the worked examples (plan P4-D460).

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

* `_say` and `_warn` are the only two places in this module that hand
  text to the screen, and both put what they are given through
  `parsing.visible_lines` first. A sink added later that shows text
  through either of them is covered without its author doing anything.
  The screen is the run's (`run`'s ``screen``, plan P4-D395 part 3):
  the terminal's, `_terminal_screen`, is this module's one `print`, and
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
import typing

from synthtwin import asking, computer, dialect, errors, parsing
# -- 3b.R4 (P4-D384): the twelve systems that write dates as counts, a
# module of the package's own that imports `parsing` alone.
from synthtwin import date_counts
# ...and the result a run returns (plan P4-D395, lane S5a): the standard
# library only, so every branch may import it.
from synthtwin import results
# ...and the lines a terminal shows while a run works (lane EZ-a, plan
# P4-D479): the standard library only.
from synthtwin import progress
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

# THE HELP FOR `--keep-value`, held as a constant beside `--missing-value`'s
# for the same reason (lane TT, plan P4-D460): it is printed whole on the
# whole-tool page and on the pages of `profile` and `twin`, which read it,
# so the disclosure a person reads before typing a value is one text.
_KEEP_VALUE_HELP = (
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
# ...THE WHOLE JOURNEY IN ONE COMMAND (lane TT, plan P4-D460): `twin` runs
# `profile`, the questions on screen, `generate` and `validate` in one run
# and one folder. And `help` shows one command's page, or the examples.
_TWIN = "twin"
_HELP_WORD = "help"
# The words `help` takes after it: a command's page, or the examples page.
_EXAMPLES = "examples"
# THE COMMAND WORDS THE PARSER SHOWS, as the base showed them: the
# whole-tool help page is the stage-5 battery's G10.2, held byte for byte
# (plan P4-D395 part 5), so the two new words are taken by the parser
# without being added to the line that page prints (lane TT, plan P4-D460),
# nor to the words a refused command word is told: argparse names an
# argument by its metavar where it has one, and `argument command:` read
# `argument {profile,generate,validate,doctor}:` with `'twin', 'help'` among
# the choices until lane TT's repair (skeptic 1's item 4). So a command line
# that names neither new word is read by the base's own argument -- its four
# choices, no metavar -- and only one that names `twin` or `help` takes all
# six, behind this metavar (`_parse_arguments`). The list the skeptic named
# (a list whose `in` takes the two words) would need a double-underscore
# method, which the offline audit refuses in synthtwin source.
_COMMANDS_SHOWN = "{profile,generate,validate,doctor}"

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
writes it in all 100 of its rows. 100 rows is the shortest true
example: `synthtwin profile` refuses, and writes nothing, any table
under 20,000 rows that hold a value, or under 1,000 people where a
column named as the person's gives one person several rows, and the
same arithmetic holds there for any column its published facts pin
completely. synthtwin offers no formal privacy guarantee.

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


# -- ONE HELP PAGE FOR EACH COMMAND (lane TT, plan P4-D460) ----------
#
# `synthtwin COMMAND --help` and `synthtwin help COMMAND` show that
# command's page: what it reads and writes, and each option it reads on a
# line, at most 60 lines at 80 columns (`K-S8-05`), the help of
# `--keep-value` and `--missing-value` printed whole wherever a command
# reads them, because it is the disclosure a person reads before typing a
# value (plan amendment A-P3-31). `synthtwin --help` keeps the page for the
# whole tool, every option in full, byte for byte (the stage-5 battery's
# G10.2), and `synthtwin help examples` the worked examples. The pages are
# reached through the one parser every command line is read by, and
# `tests/test_terminal_twin.py` holds every option a page names to the
# parser's own (`_LONG_OPTIONS`), and every option a command reads to its
# page (`_READ_BY`).

# The options each command reads, in the order its page lists them.
_PROFILE_DECLARATIONS = (
    "--person",
    "--identifier",
    "--code",
    "--measurement",
    "--decimal-comma",
    "--date-column",
    "--date-count",
    "--century",
    "--twelve-hour",
    "--day-first",
    "--first-row",
    "--metadata-rows",
    "--delimiter",
    "--sheet",
    "--answers",
    "--smallest-group",
    "--keep-value",
    "--missing-value",
)
# THE INSTALLATION'S FOUR (contract 4.6b.4; lane CHON, plan P4-D464): read
# by `profile` and handed on by `twin`, named on their pages in one sentence
# (`_RECORD_SENTENCE`), each said in full on the whole-tool page.
_RECORD_OPTIONS = ("--name", "--replace-description", "--new-key", "--private-folder")
_READ_BY = {
    _PROFILE: ("--out-dir", "--replace") + _PROFILE_DECLARATIONS + _RECORD_OPTIONS,
    _GENERATE: ("--seed", "--out-dir", "--replace"),
    _VALIDATE: ("--twin", "--out-dir", "--sheet", "--replace"),
    _DOCTOR: ("--out-dir",),
    _TWIN: ("--out-dir", "--replace", "--seed") + _PROFILE_DECLARATIONS + _RECORD_OPTIONS,
}

# Each option's line: what is typed after it, and what it does, short.
_SHORT_HELP = {
    "--out-dir": ("FOLDER", "write into FOLDER, which must exist"),
    "--replace": ("", "write over files an earlier run left there"),
    "--seed": ("NUMBER", "which twin to build, a whole number (default 0)"),
    "--twin": ("PATH", "the CSV file to measure (default: the twin)"),
    "--person": ("COLUMN", "who the rows are about: held, people counted"),
    "--identifier": ("COLUMN", "record numbers: no value of it is published"),
    "--code": ("COLUMN", "codes, not measurements: kept as written"),
    "--measurement": ("COLUMN", "numbers in one cell that are quantities: 120/80"),
    "--decimal-comma": ("COLUMN", "numbers with a comma for the decimal point"),
    "--date-column": ("COLUMN", "dates, though some values are written otherwise"),
    "--date-count": ("COLUMN SYSTEM", "dates written as numbers, counted in SYSTEM"),
    "--century": ("COLUMN=YEAR", "two-figure years: the first year of the century"),
    "--twelve-hour": ("COLUMN", "times on a 12-hour clock with no AM or PM"),
    "--day-first": ("", "dates are written day first: 03/04 is 3 April"),
    "--first-row": ("{names,data}", "the first row holds the names, or a record"),
    "--metadata-rows": ("N", "N rows under the names describe the columns"),
    "--delimiter": ("CHARACTER", "the character between columns: , ; | or tab"),
    "--sheet": ("NAME", "the sheet of a workbook that holds the table"),
    "--answers": ("FILE", "a questions file with your answers written in"),
    "--smallest-group": ("ROWS", "raise the smallest group from 11, never lower"),
    "--keep-value": ("VALUE", ""),
    "--missing-value": ("VALUE", ""),
    "--name": ("NAME", ""),
    "--replace-description": ("", ""),
    "--new-key": ("", ""),
    "--private-folder": ("FOLDER", ""),
}
# ...and the one sentence that names them on the pages of `profile` and
# `twin` (kept within `K-S8-05`'s 60 lines a page).
_RECORD_SENTENCE = "--name, --replace-description, --new-key, --private-folder: see --help"
_LONG_HELP = {"--keep-value": _KEEP_VALUE_HELP, "--missing-value": _MISSING_VALUE_HELP}

_PAGE_WIDTH = 79
_OPTION_COLUMN = 30

# What each command does, and what its page says first.
_PAGE_HEADS = {
    _PROFILE: (
        "usage: synthtwin profile TABLE [options]",
        # One line since batch 4u's merge of lane CHON, so that lane EZ-a's
        # --person line and the lane's line of the installation's four
        # options fit `K-S8-05`'s 60 lines a page together.
        "Describe TABLE (CSV or workbook): a description, its summary, a questions file.",
    ),
    _GENERATE: (
        "usage: synthtwin generate DESCRIPTION [options]",
        "Build the twin from DESCRIPTION, the file 'synthtwin profile' wrote, "
        "and from nothing else, and write the twin (TABLE-twin.csv, or "
        "TABLE-twin.xlsx for a workbook) and its report (TABLE-twin-report.txt) "
        "beside it. The same description, seed and version always give the "
        "same twin, byte for byte.",
    ),
    _VALIDATE: (
        "usage: synthtwin validate DESCRIPTION [options]",
        "Measure the twin beside DESCRIPTION, or the file --twin names, "
        "against the description, and write the quality report "
        "(TABLE-twin-quality.txt). It cannot tell a synthetic file from a "
        "real one. Exit status: 0 nothing was missed, 3 something was, 1 the "
        "check could not run, 2 the command line could not be used.",
    ),
    _DOCTOR: (
        "usage: synthtwin doctor [TABLE] [options]",
        "Check this computer before a first run: Python, the four libraries "
        "synthtwin needs (numpy, pandas, pyarrow and scipy), the output "
        "folder and the memory, and weigh TABLE's size against that memory "
        "when you name one. It never opens TABLE.",
    ),
    _TWIN: (
        "usage: synthtwin twin TABLE [options]",
        "The whole journey in one command: describe TABLE, ask on screen what "
        "its values cannot settle, build the twin and measure it. Nothing is "
        "written before the questions are answered. The six files go into one "
        "folder, TABLE-synthtwin beside the table unless --out-dir names "
        "another, and the answers stay in its questions file: the next run "
        "there asks nothing where it reads the same file with the same "
        "--smallest-group and as many --missing-value and --keep-value.",
    ),
}
# The options a page names in a sentence rather than a line each: the
# declarations `twin` hands to its profile step, which `profile`'s page
# lists one by one.
_PAGE_PROSE = {
    _TWIN: (
        "It reads every option of synthtwin profile that says what a column "
        "holds, and hands it to the profile step: --person, --identifier, --code, "
        "--measurement, --decimal-comma, --date-column, --date-count, "
        "--century, --twelve-hour, --day-first, --first-row, --metadata-rows, "
        "--delimiter, --sheet and --smallest-group (synthtwin help profile "
        "says what each does), and these two:"
    ),
}
_PROSE_NAMES = (
    "--person",
    "--identifier",
    "--code",
    "--measurement",
    "--decimal-comma",
    "--date-column",
    "--date-count",
    "--century",
    "--twelve-hour",
    "--day-first",
    "--first-row",
    "--metadata-rows",
    "--delimiter",
    "--sheet",
    "--smallest-group",
)
# ...and what it says last, its exit statuses where they differ.
_PAGE_FEET = {
    _TWIN: (
        "Exit status: 0 every step ran and nothing was missed; 3 a step missed "
        "something its report names; 1 a step could not run; 2 the command "
        "line could not be used.",
    ),
}
_PAGE_END = "In full: synthtwin --help. Examples: synthtwin help examples."

# THE INDEX `synthtwin help` shows, and the examples page.
_HELP_INDEX = """synthtwin makes a synthetic twin of a table, on this computer.

The whole journey in one command:
  synthtwin twin my-table.csv

The same three steps one at a time, each printing the next:
  synthtwin profile my-table.csv
  synthtwin generate my-table-profile.json
  synthtwin validate my-table-profile.json

Before a first run, check this computer:
  synthtwin doctor my-table.csv

One page for each command:
  synthtwin help twin
  synthtwin help profile
  synthtwin help generate
  synthtwin help validate
  synthtwin help doctor
Worked examples:
  synthtwin help examples
Every option in full:
  synthtwin --help
"""

_EXAMPLES_PAGE = """examples:
  synthtwin twin data.csv
      describe data.csv, ask on screen what its values cannot settle,
      build the twin and measure it, all into the folder data-synthtwin
      beside data.csv

  synthtwin twin data.csv --replace --seed 2
      a second twin in that folder, over the first: it asks nothing,
      because the answers given the first time are kept there

  synthtwin twin data.csv --out-dir reports --identifier record_no
      the same journey into the folder 'reports', the column record_no
      named as record numbers, so no question is asked about it

  synthtwin profile data.csv
      describe data.csv and write data-profile.json, data-profile.txt
      and data-questions.json beside it

  synthtwin profile data.csv --answers data-questions.json
      describe it again with the answers written into that file

  synthtwin profile data.csv --replace
      describe it again over the three files an earlier run left there

  synthtwin generate data-profile.json --seed 7
      build a different twin from the same description

  synthtwin validate data-profile.json
      measure data-twin.csv against that description and write
      data-twin-quality.txt beside it

  synthtwin validate data-profile.json --twin somewhere/other.csv
      measure that file instead, and write other-quality.txt

  synthtwin doctor data.csv
      check this computer before a first run, and weigh the size of
      data.csv against its memory without opening the file
"""


def _wrapped(text: str, indent: str, width: int = _PAGE_WIDTH) -> str:
    """``text`` laid out in lines of at most ``width`` characters, each after ``indent``.

    Words are cut at single spaces and never inside, the way the page's
    reader reads them. Built a character at a time, for the offline
    audit's reason (no method of the value is called). A fixed function
    of its arguments; raises nothing.
    """
    lines = ""
    line = ""
    word = ""
    for character in text + " ":
        if character != " ":
            word = word + character
            continue
        if not word:
            continue
        if line and len(indent) + len(line) + 1 + len(word) > width:
            lines = lines + indent + line + "\n"
            line = word
        else:
            line = word if not line else line + " " + word
        word = ""
    if line:
        lines = lines + indent + line + "\n"
    return lines


def _option_line(option: str) -> str:
    """One option's lines on a command's page: its name, what follows it, what it does."""
    metavar, said = _SHORT_HELP[option]
    named = option if not metavar else f"{option} {metavar}"
    if option in _LONG_HELP:
        return f"  {named}\n" + _wrapped(_LONG_HELP[option], "    ")
    lead = f"  {named}"
    if len(lead) + 1 > _OPTION_COLUMN:
        return f"{lead}\n{' ' * _OPTION_COLUMN}{said}\n"
    return f"{lead}{' ' * (_OPTION_COLUMN - len(lead))}{said}\n"


def command_page(command: str) -> str:
    """The help page of one command word (lane TT, plan P4-D460; `K-S8-05`).

    Guarantees: for each of `profile`, `generate`, `validate`, `doctor`
    and `twin`, a page of at most 60 lines of at most 79 characters: its
    usage line, what it reads and writes, and each option it reads
    (`_READ_BY`) -- on a line of its own, or named in its one sentence
    (`_PAGE_PROSE`, the declarations `twin` hands to its profile step),
    `--keep-value` and `--missing-value` always with their whole help, as
    the whole-tool page prints it -- and where every option is given in
    full. A fixed function of the word; raises KeyError for another word.
    No I/O.
    """
    usage, said = _PAGE_HEADS[command]
    page = f"{usage}\n\n" + _wrapped(said, "") + "\noptions:\n"
    prose = _PAGE_PROSE[command] if command in _PAGE_PROSE else ""
    for option in _READ_BY[command]:
        if option in _LONG_HELP or (prose and option in _PROSE_NAMES) or option in _RECORD_OPTIONS:
            continue
        page = page + _option_line(option)
    if any(option in _RECORD_OPTIONS for option in _READ_BY[command]):
        page = page + _wrapped(_RECORD_SENTENCE, "  ")
    if prose:
        page = page + "\n" + _wrapped(prose, "")
    for option in _READ_BY[command]:
        if option in _LONG_HELP:
            page = page + _option_line(option)
    for foot in _PAGE_FEET[command] if command in _PAGE_FEET else ():
        page = page + "\n" + _wrapped(foot, "")
    return page + "\n" + _wrapped(_PAGE_END, "")


def _page_for(command: "object", whole: str) -> str:
    """The page a help option shows: the command's own where one was read before it, else the whole page."""
    if isinstance(command, str) and command in _READ_BY:
        return command_page(command)
    return whole


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


# -- the run in progress: its screen, its reader, its result (plan P4-D395) --
#
# `run` opens one `_Session` per command line and closes it however the
# run ends; `_say`, `_warn` and the questions put at a prompt reach the
# person through it, and the run's result is gathered in it as the run
# goes, so a run stopped part way still says what it had shown. A
# helper called with no session open (the suite calls a few directly)
# shows its text on the terminal, as every helper did before.
_OUT = "out"
_ERR = "err"


class _Unusable(Exception):
    """The command line could not be used; its words are already on the screen."""


class _HelpShown(Exception):
    """The help page was asked for, and is already on the screen."""


@dataclasses.dataclass
class _Session:
    """One run's screen, reader and result as it is gathered.

    ``phase`` is the step a refusal raised from below would stop at
    (`results.STEPS`); ``step`` the step a refusal named itself where it
    did. The rest are `results.Result`'s fields as the run fills them.
    """

    screen: "list[tuple[str, str]] | str | None"
    ask: "list[str | None] | str | None"
    command: str = ""
    answered: int = 0
    phase: str = results.STEP_INPUT
    step: str = ""
    key: str = ""
    refusal_words: "list[str]" = dataclasses.field(default_factory=list)
    on_disk: str = ""
    misses: "tuple[results.Miss, ...]" = ()
    unjudged: "tuple[results.Unjudged, ...]" = ()
    carried: "tuple[results.Carried, ...]" = ()
    tally: "tuple[tuple[str, int], ...]" = ()
    floor: "int | None" = None
    floor_lowered: bool = False
    warnings: "list[results.Caution]" = dataclasses.field(default_factory=list)
    files: "list[results.FileWritten]" = dataclasses.field(default_factory=list)
    left_behind: "list[str]" = dataclasses.field(default_factory=list)
    next_command: "results.NextCommand | None" = None
    questions: "tuple[results.Asked, ...]" = ()
    # The questions put at a prompt in this run, each by its column, role
    # and reason, and how many were put, answered there or not (lane S5b).
    put: "list[tuple[str, str, str]]" = dataclasses.field(default_factory=list)
    prompted: int = 0
    # THE TWIN COMMAND'S (lane TT, plan P4-D460): each step's own result,
    # in order, on the twin's session; and on a step's session, that it is
    # one (its teaching line is not shown: the twin goes on by itself), the
    # verdict the steps before it reached (validate's exit line names the
    # twin's status), and the folder it makes once its questions are
    # answered, so nothing exists before then.
    steps: "list[results.Result]" = dataclasses.field(default_factory=list)
    twin_step: bool = False
    before: str = ""
    folder_to_make: str = ""
    # ...AND THE FILE THE ANSWERS IT KEEPS ARE BOUND TO (lane TT's repair;
    # `_bound_reading`): on a profile step handed its folder's own
    # questions file, the file's size, fingerprint and sheet the answers
    # were given about, which its reading must find again; and the
    # sentence binding the answers this step keeps to its own reading,
    # written into its questions file.
    bound_to: "tuple[int, int, str] | None" = None
    binding: str = ""
    # ...and, on the twin's session, the questions its profile step's
    # prompt puts, or would put with somebody at the keyboard, each by its
    # column, role and reason: what the taught answers command can put on
    # screen (Codex's item 9, skeptic 1's item 5).
    promptable: "list[tuple[str, str, str]]" = dataclasses.field(default_factory=list)
    # LANE EZ-a (plan P4-D479): the columns said to name the person
    # (`--person`, the person question's `identifier`, the subject question
    # at the keyboard; `--person` alone in ``persons_typed``); the answers
    # the keyboard reader takes for the question on screen, each with the
    # key shown beside it (`_read_one_answer`); the questions file a
    # plain-text answers file is matched against; whether the table floor
    # is the command's (`main`'s internal keyword); whether a second round
    # of questions may follow the files (`_run_profile`), and the closing
    # lines held back for it; and every text shown on the error stream, so
    # a run described again shows only what is new.
    persons_said: "list[str]" = dataclasses.field(default_factory=list)
    persons_typed: "list[str]" = dataclasses.field(default_factory=list)
    subject_put: "tuple[str, ...]" = ()
    # ...and the said columns the people were counted by where two or more
    # declared record-number columns repeat: only there does saying change
    # the count, so only there is it written into the questions file and
    # the repeat line (every other description and file keeps its bytes).
    persons_counted: "tuple[str, ...]" = ()
    offered_now: "tuple[tuple[str, str], ...]" = ()
    questions_beside: "tuple[str, str | None] | None" = None
    floor_refuses: bool = True
    rounds_follow: bool = False
    closing: str = ""
    err_shown: "list[str]" = dataclasses.field(default_factory=list)
    # LANE EZ-a'S REPAIR (LANE EZ RULINGS 4 (3) and (4)): the screen and the
    # reader a later round's description puts the subject question with,
    # while its own screen is held back and nobody else is asked, and
    # whether input ended at that question; each question whose answer
    # stands, by its column, role and reason (answered at the first prompt
    # other than with Enter, or in a later round described again), which
    # no closing line counts as open; and the command line as typed, from
    # which the command that answers the open questions is made.
    subject_reader: "tuple[list[tuple[str, str]] | str | None, list[str | None] | str | None] | None" = None
    ended_at_subject: bool = False
    answers_standing: "list[tuple[str, str, str]]" = dataclasses.field(default_factory=list)
    typed: "_Options | None" = None
    # LANE EZ-a'S SECOND REPAIR (LANE EZ RULINGS 7, Codex's item 1; 8 (5)):
    # each typed declaration, as (column, answer), that an answer the
    # questions file holds replaced -- typed at the keyboard in any round or
    # written in the file, so newer than the command line -- which no later
    # round, repeat line or taught command brings back; the person questions
    # answered `keep` at the first prompt, carried into `answered_before`;
    # and the line that says a said column counted the table in rows.
    typed_replaced: "list[tuple[str, str]]" = dataclasses.field(default_factory=list)
    persons_kept: "list[str]" = dataclasses.field(default_factory=list)
    rows_said: str = ""
    # THE RECORD REFUSED A LATER ROUND'S CHANGED DESCRIPTION (Codex's review
    # of batch 4u, item 7): its words ask for --replace-description, so the
    # answers given at the keyboard stay in the questions file and the
    # command taught applies them with that option (`_profile_rounds`).
    round_refused_by_record: bool = False
    # ...and whether this run put the subject question of the questions
    # file's `between_columns` entry at the keyboard (item 6).
    subject_entry_put: bool = False


@dataclasses.dataclass
class _Open:
    """The sessions open now, the innermost last: one per call of `run` in progress.

    A list rather than a single slot, so a run started from inside
    another (no command does that) still finds its own. One list for the
    whole module, so `run` serves one thread at a time (its docstring
    states the limit).
    """

    sessions: "list[_Session]" = dataclasses.field(default_factory=list)


_OPEN = _Open()

# WHAT `run` IS HANDED FOR ITS SCREEN AND ITS READER (plan P4-D395 part 3,
# as lane S5a built it, plan P4-D437): DATA, NEVER A CALLABLE. The offline
# audit (plan D6.2) admits no call of a function a caller hands in -- such
# a function could do anything -- so `screen` is `TERMINAL` (the terminal,
# `main`'s), a list the run adds each (stream, text) it shows to, in
# order, or None (shown nowhere); `ask` is `TERMINAL` (the person at the
# terminal), a list of the lines typed, read in order -- None, or the end
# of the list, where the person ended input -- or None (nobody is asked).
TERMINAL = "terminal"


def _current() -> "_Session | None":
    """The session of the run in progress, or None where no run is open."""
    if not _OPEN.sessions:
        return None
    return _OPEN.sessions[len(_OPEN.sessions) - 1]


def _at(step: str) -> None:
    """Say which step the run is at, for a refusal raised from below.

    ...and, at a terminal, that the files are being written (lane EZ-a,
    plan P4-D479: a line for each stage, `progress`; nothing while the
    sink is off).
    """
    session = _current()
    if session is not None:
        session.phase = step
    if step == results.STEP_WRITING:
        progress.stage("writing the files")


def _terminal_screen(stream: str, text: str) -> None:
    """The terminal's screen: this module's one `print` (plan P4-D395 part 3).

    ``stream`` is "out" for standard output and "err" for the error
    stream; ``text`` is exactly the characters to show, the display
    boundary already applied by whoever composed it.
    """
    if stream == _ERR:
        print(text, end="", file=sys.stderr)
    else:
        print(text, end="", file=sys.stdout)


def _terminal_ask(prompt: str) -> "str | None":
    """The terminal's reader: one typed line, or None where input ended.

    `input` writes ``prompt`` itself, so the prompt's bytes are the
    reader's and never the screen's. End of input and Ctrl-C at the
    prompt both mean the person stopped, as they did before results.
    """
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        return None


def _show(stream: str, text: str) -> None:
    """Hand text to the run's screen: the terminal where no run is open."""
    session = _current()
    if session is not None and stream == _ERR:
        session.err_shown += [text]
    if session is None or session.screen == TERMINAL:
        _terminal_screen(stream, text)
        return
    if isinstance(session.screen, list):
        session.screen += [(stream, text)]


def _record_floor(floor: int, said_on_no_screen: bool) -> None:
    """Record the description's smallest group size in the run's result.

    ``floor_lowered`` is true where it lies below `_NOTICE_LINE`
    (contract `SMALL_GROUP_NOTICE_LINE`), the test by which the summary,
    the twin's report and the quality report each state a lowered floor.
    ``said_on_no_screen`` adds the `lowered-floor` caution with no words,
    for a command whose screen prints none (generate, validate): a file
    the run writes states it (plan P4-D395 part 1).
    """
    session = _current()
    if session is None:
        return
    session.floor = floor
    session.floor_lowered = floor < _NOTICE_LINE
    if session.floor_lowered and said_on_no_screen:
        session.warnings += [results.Caution(results.CAUTION_LOWERED_FLOOR, "", "")]


def _stopped_writing(sentence: str) -> None:
    """Show the write transaction's own account of a stop, as the refusal's words.

    The sentence names what is on disk, so the result carries it as such.
    """
    _warn(sentence, step=results.STEP_WRITING)
    session = _current()
    if session is not None:
        session.on_disk = parsing.visible_lines(f"{sentence}")


def _wrote(*written: "tuple[str, pathlib.Path]") -> None:
    """Record files the run wrote, each with its kind, in the order written."""
    session = _current()
    if session is None:
        return
    for kind, place in written:
        session.files += [results.FileWritten(kind, f"{place}")]


def _put_at_a_prompt(questions: "list[asking.Question]") -> None:
    """Record the questions this run put at a prompt (lane S5b, plan P4-D441).

    Each by its column, role and reason (`asking.question_put`), so a
    second question on the same column that no prompt showed is not
    said put; and their count, answered at the prompt or not, which the
    questions file cannot give once an answer has taken its question out
    (Codex's review of lane S5b, items 1 and 2).
    """
    session = _current()
    if session is None:
        return
    for question in questions:
        put = asking.question_put(question)
        if put not in session.put:
            session.put += [put]
    session.prompted = session.prompted + len(questions)


def _asked_at_a_prompt() -> "tuple[tuple[str, str, str], ...]":
    """The questions this run put at a prompt, by column, role and reason, in the order put."""
    session = _current()
    return () if session is None else tuple(session.put)


def _questions_put_in_the_result(
    records: "tuple[results.Asked, ...]", columns: int
) -> None:
    """Put a profile's questions and their tally in its result (lane S5b, plan P4-D441).

    One record for each entry of the questions file, in its order, and
    the profile's tally (plan P4-D395 part 1, `tally`): its columns, the
    questions its file asks -- about the file and column by column --,
    the questions this run put at a prompt, answered there or not (an
    answer takes its question out of the file, so they are counted as
    put, not read off the records: Codex's review of lane S5b, item 2),
    the checklist's columns, and the columns held.
    """
    session = _current()
    if session is None:
        return
    session.questions = records
    asked = [
        one
        for one in records
        if one.section in (results.SECTION_ABOUT_FILE, results.SECTION_ASKED)
    ]
    session.tally = (
        ("columns", columns),
        ("questions-asked", len(asked)),
        ("questions-put", session.prompted),
        (
            "checklist",
            len([one for one in records if one.section == results.SECTION_CHECKLIST]),
        ),
        (
            "held",
            len([one for one in records if one.section == results.SECTION_HELD]),
        ),
    )


def _described_carried(written: pathlib.Path, chain: bool) -> None:
    """Put what a written description carries in the profile's result (lane S5b, plan P4-D441).

    Drawn from the description itself, read back through the loader
    generate reads it with, so a profile's `carried` is generate's for
    the same description: each column whose twin cells are made up,
    wholly or in part (`roles.made_up_class`), and the table's
    `not-modeled` entry while nothing between columns is carried. A
    description the loader refuses carries nothing here, as generate of
    it refuses; nothing is shown either way.
    """
    from synthtwin import contract

    session = _current()
    if session is None:
        return
    try:
        described = contract.load_profile(f"{written}", None if chain else False)
    except errors.ProfileError:
        return
    session.carried = tuple(_not_carried(described) + _table_not_modeled(described))


def _left_behind(left: "list[str]", note: str) -> None:
    """Show the caution for working files left behind, and record them."""
    _warn(note, caution=results.CAUTION_LEFT_BEHIND)
    session = _current()
    if session is not None:
        session.left_behind += [f"{one}" for one in left]


def _in_rank_order(found: "list[results.Miss]") -> "tuple[results.Miss, ...]":
    """The misses in `(tier, place, arrival)` order, and in no other (part 2)."""
    keyed = sorted(
        [
            (results.TIER_ORDER[miss.tier], miss.place, miss.arrival, index)
            for index, miss in enumerate(found)
        ]
    )
    return tuple([found[index] for _tier, _place, _arrival, index in keyed])


# THE CLASS A COLUMN'S INVENTION TAKES IN A RESULT (contract's
# `made_up_class`), as `results`' reasons name it.
_MADE_UP_REASONS = {
    "everything": results.REASON_MADE_UP,
    "held-back": results.REASON_HELD_BACK,
    "uncarried": results.REASON_UNCARRIED,
}

# The table's one entry while nothing between columns is carried: a
# description whose statistical block is null (plan P4-D395 part 1); one
# that carries a chain holds none (`_table_not_modeled`, plan P4-D464).
_NOT_MODELED = results.Carried(
    (), "", results.CLASS_NOT_CARRIED, results.REASON_NOT_MODELED
)


def _table_not_modeled(described: object) -> "list[results.Carried]":
    """The table's `not-modeled` entry where its description carries nothing between columns; none where it carries a chain.

    `results.REASON_NOT_MODELED` names the table "between whose columns
    nothing is carried while its statistical block is null": since the
    switch is on (plan P4-D464) a description may carry a chain, and its
    result then holds no such entry. Read off the loaded description
    (`RelationshipManifest.switched`: it publishes `statistical` or `grain`).
    """
    from synthtwin import contract

    if isinstance(described, contract.Profile) and described.relationships.switched:
        return []
    return [_NOT_MODELED]


def _not_carried(described: object) -> "list[results.Carried]":
    """Each column the description publishes no value for, or only some, in schema order."""
    from synthtwin import contract, roles

    if not isinstance(described, contract.Profile):
        raise TypeError("a loaded description is wanted")
    found: "list[results.Carried]" = []
    for column in described.columns:
        made_up = roles.made_up_class(column)
        if made_up in _MADE_UP_REASONS:
            found += [
                results.Carried(
                    (column.name,),
                    "",
                    results.CLASS_NOT_CARRIED,
                    _MADE_UP_REASONS[made_up],
                )
            ]
    return found


def _fact_head(fact: str) -> str:
    """A description key's first part: `mean` of `mean`, `length` of `length.p50`."""
    if not isinstance(fact, str):
        raise TypeError("a fact is named by text")
    head = ""
    for character in fact:
        if character in ".[":
            break
        head = head + character
    return head


# THE FACTS A DEVIATION NAMES OUTSIDE ITS ROLE'S GROUP (lane S5a's repair
# 1): the column-level counts the disposition registry files under
# `universal` -- present, missing, out of range -- and the column's time
# grain, a column-level key the description publishes beside them (plan
# P4-D417), which the registry files under `universal` too since lane
# S5b (plan P4-D441). `tests/test_stage5_gate.py` holds this list to the
# registry and to every key the generator writes. ...AND THE COLUMN'S ROLE
# (lane TR's follow-up, LANE TR RULINGS 7 (1)): a fraction clock whose twin
# reads back as one value or two names it (plan P4-D473, repair 2), and the
# registry files the role under `universal`.
_UNIVERSAL_FACTS = ("n_present", "n_missing", "n_out_of_range", "time_grain", "role")
# A generator key `levels -> field` names a field of the label group's
# levels block (`label.variants_withheld`, `label.shape_form_cells`).
_ARROW = " -> "


def _registry_fact(group: str, fact: str, end: str) -> str:
    """A generator's fact named as the disposition registry names it (plan P4-D395 part 1).

    Guarantees: `group.field`, where the field is the generator's key
    after its last `levels -> `, and the group is `universal` for the
    column-level keys of `_UNIVERSAL_FACTS` and ``group`` -- the one the
    column's role publishes under -- otherwise; then `.end` where
    ``end`` names the ladder end that gave way. A key on no column
    (``group`` empty) is the key itself. A pure function of the three;
    built without a method of the value, for the offline audit's reason.
    """
    if not isinstance(fact, str):
        raise TypeError("a fact is named by text")
    field = fact
    place = 0
    while place + len(_ARROW) <= len(field):
        if field[place : place + len(_ARROW)] == _ARROW:
            field = field[place + len(_ARROW) :]
            place = 0
            continue
        place = place + 1
    if _fact_head(field) in _UNIVERSAL_FACTS:
        group = "universal"
    named = f"{group}.{field}" if group else field
    return f"{named}.{end}" if end else named


def _generated(described: object, made: object) -> None:
    """Put a generated twin's misses, tally and carried entries in the run's result.

    One miss for each deviation, its fact named as the registry names it
    (`_registry_fact`: the group its column's role publishes under,
    `universal` for the column-level counts, and a ladder end that gives
    way by the end the generator pins); its rank read off
    `results.tier_of`. Every approximation is carried, inside or outside
    its bound, as the report lists it, its fact named by the same rule so
    it joins the miss its bound makes, and so is each column the twin
    made up. No cell of the twin is read (plan P4-D395 part 1, lane SG's
    seam).
    """
    from synthtwin import contract, generation, roles

    if not isinstance(described, contract.Profile):
        raise TypeError("a loaded description is wanted")
    if not isinstance(made, generation.Twin):
        raise TypeError("a twin is wanted")
    session = _current()
    if session is None:
        return
    places: "dict[str, int]" = {}
    groups: "dict[str, str]" = {}
    for column in described.columns:
        places[column.name] = column.position
        groups[column.name] = roles.registry_group(column.facts)
    found: "list[results.Miss]" = []
    for arrival in range(len(made.deviations)):
        deviation = made.deviations[arrival]
        group = groups[deviation.column] if deviation.column in groups else ""
        fact = _registry_fact(group, deviation.fact, deviation.end)
        found += [
            results.Miss(
                tier=results.tier_of(fact, "", deviation.judged),
                place=places[deviation.column] if deviation.column in places else 0,
                arrival=arrival,
                column=deviation.column,
                fact=fact,
                subcheck="",
                judged=deviation.judged,
                published=deviation.published,
                achieved=deviation.achieved,
                shown=bool(deviation.achieved),
                note=(deviation.note,) if deviation.note else (),
            )
        ]
    whole = 0
    part = 0
    carried = _not_carried(described)
    for entry in carried:
        if entry.reason == results.REASON_MADE_UP:
            whole = whole + 1
        else:
            part = part + 1
    for approximation in made.approximations:
        group = (
            groups[approximation.column] if approximation.column in groups else ""
        )
        carried += [
            results.Carried(
                (approximation.column,),
                _registry_fact(group, approximation.fact, ""),
                results.CLASS_APPROXIMATE,
                results.REASON_APPROXIMATED,
                measures=(
                    results.Measure(
                        approximation.published,
                        approximation.achieved,
                        approximation.lowest,
                        approximation.highest,
                        approximation.inside,
                        approximation.covers_published,
                    ),
                ),
            )
        ]
    session.misses = _in_rank_order(found)
    session.carried = tuple(carried + _table_not_modeled(described))
    session.tally = (
        ("deviations", len(made.deviations)),
        ("approximations", len(made.approximations)),
        (
            "approximations-inside",
            len([one for one in made.approximations if one.inside]),
        ),
        ("remarks", len(made.remarks)),
        ("columns-made-up", whole),
        ("columns-partly-made-up", part),
    )


def _validated(described: object, measured: object) -> None:
    """Put a validate run's misses, unjudged checks, tally and carried entries in its result.

    One miss for each MISSED check, its rank read off `results.tier_of`;
    one unjudged entry for each WITHHELD check, keyed by the rule that
    kept its outcome back and holding no measured value; the census's
    six counts; and carried, each check judged against a window with the
    verdict it got and its subcheck, `inside` None where it is WITHHELD
    or where V5 keeps its measured side back (lane S5a's repair 1). No
    string read from the measured file enters the result: every field is
    the validator's own, as the report prints it (plan P4-D395 part 1).

    WHAT IS CARRIED FOLLOWS THE DESCRIPTION (lane S5a's repair 2, Codex's
    item 5): an approximate entry for each check whose obligation the
    description grants a window (`Check.approximate`), the column the
    file lacks, a file of no rows or names and a closed gate included,
    where such a check's verdict was decided by the absence and its
    `inside` is None, since nothing of the subject was checked. Each
    measure carries the window's ends and whether it holds the
    description's value where the report prints that window (Codex's
    item 7), so no consumer parses them out of `published`.
    """
    from synthtwin import contract, validation

    if not isinstance(described, contract.Profile):
        raise TypeError("a loaded description is wanted")
    if not isinstance(measured, validation.Outcome):
        raise TypeError("a validator's outcome is wanted")
    session = _current()
    if session is None:
        return
    places: "dict[str, int]" = {}
    for column in described.columns:
        places[column.name] = column.position
    found: "list[results.Miss]" = []
    unjudged: "list[results.Unjudged]" = []
    carried = _not_carried(described)
    for arrival in range(len(measured.checks)):
        check = measured.checks[arrival]
        if check.verdict == validation.MISSED:
            found += [
                results.Miss(
                    tier=results.tier_of(check.fact, check.subcheck, check.judged),
                    place=places[check.column] if check.column in places else 0,
                    arrival=arrival,
                    column=check.column,
                    fact=check.fact,
                    subcheck=check.subcheck,
                    judged=check.judged,
                    published=check.published,
                    achieved=check.achieved,
                    shown=bool(check.achieved),
                    note=check.note,
                )
            ]
        if check.verdict == validation.WITHHELD:
            unjudged += [
                results.Unjudged(
                    check.column,
                    check.fact,
                    check.subcheck,
                    validation.withheld_rule(check),
                )
            ]
        if check.approximate:
            inside: "bool | None" = None
            if (
                check.judged == validation.JUDGED_WINDOW
                and check.verdict != validation.WITHHELD
                and check.achieved
            ):
                inside = check.verdict != validation.MISSED
            carried += [
                results.Carried(
                    (check.column,) if check.column else (),
                    check.fact,
                    results.CLASS_APPROXIMATE,
                    results.REASON_APPROXIMATED,
                    subcheck=check.subcheck,
                    verdict=check.verdict,
                    measures=(
                        results.Measure(
                            check.published,
                            check.achieved,
                            check.lowest,
                            check.highest,
                            inside,
                            check.covers,
                        ),
                    ),
                )
            ]
    census = measured.census
    session.misses = _in_rank_order(found)
    session.unjudged = tuple(unjudged)
    session.carried = tuple(carried + _table_not_modeled(described))
    session.tally = (
        ("held", census.held),
        ("within-bound", census.within_bound),
        ("authorized-deviation", census.authorized_deviation),
        ("withheld", census.withheld),
        ("missed", census.missed),
        ("not-checkable", census.not_checkable),
    )


def _next(purpose: str, *words: str) -> "results.NextCommand":
    """Record the next command in the run's result, and return it to be shown."""
    command = results.NextCommand(tuple([f"{word}" for word in words]), purpose)
    session = _current()
    if session is not None:
        session.next_command = command
    return command


def _typed_line(command: "results.NextCommand") -> str:
    """A next command's words as the person types them, quoted for the shell.

    The words are `synthtwin`, the command word, then the one path the
    command takes where there is one, then options each with its value:
    the path is `_typed_path`'s and each option `_typed_option`'s, so the
    line is the one lane TI's teaching lines printed (plan P4-D397).
    """
    words = command.words
    line = f"{words[0]} {words[1]}"
    rest = words[2:]
    if len(rest) % 2 == 1:
        line = f"{line} {_typed_path(rest[0])}"
        rest = rest[1:]
    place = 0
    while place + 1 < len(rest):
        line = f"{line} {_typed_option(rest[place], rest[place + 1])}"
        place = place + 2
    return line


def _say(message: str, end: str = "\n") -> None:
    """Show one message on the screen's ordinary output, through the display boundary.

    One of the two places in this module that hand text to the screen.
    Whatever it is given goes through `parsing.visible_lines` first, so
    a value that reached here without being shown safely still cannot
    instruct the terminal. Line breaks are kept: they are synthtwin's
    own layout. ``end`` is what follows the message, a line feed unless
    the caller is showing one message in pieces (`_say_pieces`).
    """
    _show(_OUT, parsing.visible_lines(f"{message}") + end)


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


def _marks_answered(ages_counted_in: "tuple[tuple[str, str], ...]") -> "dict[str, int]":
    """Each age column answered with its unit, and that unit's mark (plan P4-D454)."""
    marks: "dict[str, int]" = {}
    for name, unit in ages_counted_in:
        if unit in asking.AGE_UNIT_ANSWERS:
            marks[name] = asking.AGE_UNIT_ANSWERS[unit]
    return marks


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


def _released_while_a_question_is_open(
    identities_open: bool,
    rare_listed: "list[str]",
    levels_pooled: "list[str]",
    names_published: "list[str]",
) -> bool:
    """RULE U (c) in the command: whether the first describe released what an open question offering `identifier` withholds.

    The stand-ins page's ZS.1 and ZS.3 (lane GG's repair 1; lanes PL and
    CODES-2): while any question offering `identifier` is open, no released
    list names a value fewer cells than the floor hold (``rare_listed``),
    no pool counted in people publishes its levels (``levels_pooled``) and
    no pool is named (``names_published``, lane CODES-2, plan P4-D471), so
    a first describe that did any of them is described again with
    `rare_values_released` False. Its own function so the gate's case can
    be red without the lane's term (the verify of lane CODES-2's repair 1,
    item 8: the term had no case). Guarantees: a fixed function of the
    four. Raises nothing. No I/O.
    """
    return identities_open and bool(rare_listed or levels_pooled or names_published)


def _read_as_labels_in(document: "dict[str, object]") -> "frozenset[str]":
    """The columns a description still reads in a role that can name its pool (lane CODES-2's repair 1, P4-D471).

    The roles whose held-back levels a Safe Harbor `no` can name: the four
    label roles and a column of numbers with labels. A column the
    description holds -- by the count in people, as a record number, by an
    open question -- is read `identifier` or another role and names nothing
    whatever is answered, so the run puts it no question about the values
    too few rows hold (the orchestrator's LANE CODES-2 RULINGS 2 (4)).
    Guarantees: a function of the mapping. Raises nothing. No I/O.
    """
    from synthtwin import taxonomy

    roles = (
        taxonomy.ROLE_CONSTANT,
        taxonomy.ROLE_BINARY,
        taxonomy.ROLE_CATEGORICAL,
        taxonomy.ROLE_LONG_TAIL,
        taxonomy.ROLE_COMPOUND,
    )
    return frozenset(
        f"{block['name']}"
        for block in _described_columns(document)
        if "name" in block and "role" in block and block["role"] in roles
    )


def _warn(
    message: str, caution: str = "", column: str = "", step: str = ""
) -> None:
    """Show one refusal or caution on the error stream, likewise.

    The second and last place in this module that hand text to the
    screen. Same boundary, same reason; only the stream differs.

    And the run's result records it (plan P4-D395 part 1): a caution
    under its key ``caution`` (`results.CAUTIONS`), with the column it
    names where it names one, never moving the verdict; anything else is
    a refusal's words, and ``step`` names where the run stopped where
    the call site knows it.
    """
    shown = parsing.visible_lines(f"{message}")
    _show(_ERR, shown + "\n")
    session = _current()
    if session is None:
        return
    if caution:
        session.warnings += [results.Caution(caution, column, shown)]
        return
    session.refusal_words += [shown]
    if step and not session.step:
        session.step = step


def _refuse_the_command_line(reason: str) -> "typing.NoReturn":
    """Say why the command line could not be used, then stop: the run is `unusable`.

    Used instead of argparse's own refusal so that the words reach the
    screen through `_warn` like every other message, and so that the
    reader is told what to do next rather than shown a usage line.
    """
    _warn(reason)
    _warn("Run  synthtwin --help  to see how the command is used.")
    raise _Unusable()


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
    # Whether `--first-row` was typed, `auto` included (plan P4-D408).
    first_row_typed: bool = False
    # -- lane EZ-a (P4-D479): the columns named with `--person`.
    persons: "list[str]" = dataclasses.field(default_factory=list)
    # THE INSTALLATION'S FOUR (contract 4.6b.4; LANE ST RULINGS 1 (4); lane
    # CHON, plan P4-D464): the table's name, the two confirmations, and the
    # private report's folder, read by `profile` and handed on by `twin`.
    name: "str | None" = None
    replace_description: bool = False
    new_key: bool = False
    private_folder: "str | None" = None


def _typed_floor(typed: str) -> int:
    """The smallest group size typed after `--smallest-group`, or a refusal.

    THE FLOOR OF 11 IS A MINIMUM (plan P4-D426). Returns the number where
    it is a whole number of `_SMALLEST_GROUP` or more; otherwise says why
    in plain words and stops with code 2 (`_refuse_the_command_line`),
    before anything is read or written. `int` reads the text exactly as
    argparse's `type=int` read it before that plan, so every number of 11
    or more is taken as it was. Determinism: a fixed function of the text.
    """
    try:
        floor = int(typed)
    except ValueError:
        _refuse_the_command_line(errors.floor_not_a_whole_number(_shown(typed)))
        raise
    if floor < _SMALLEST_GROUP:
        _refuse_the_command_line(errors.floor_under_the_minimum(_shown(typed)))
    return floor


def _description_floor_refused(
    floor: int, least: int, description: str, building: bool
) -> bool:
    """Whether a description's recorded floor is refused; says so if it is.

    HIPAA FIRST (plan P4-D426): `generate` builds no twin from, and
    `validate` checks no file against, a description recording a smallest
    group size under ``least`` -- `_SMALLEST_GROUP` on every typed
    command -- and the refusal is put on the error stream here, before
    anything is written. ``building`` is True for `generate`.
    """
    if floor >= least:
        return False
    _warn(
        errors.description_floor_under_the_minimum(
            _shown(description), floor, building
        ),
        step=results.STEP_CONTENT,
    )
    return True


def _no_floor_at_all(given: "int | None") -> bool:
    """Whether `main`'s internal setting is under 1; says so if it is.

    NO FLOOR AT ALL, whichever command (plan P4-D426, Codex's review of
    lane MIN, item 6): `main` refuses it, with code 2, before any command
    is dispatched and before anything is read or written, in the words
    `profile` always gave it -- so `generate` and `validate` never read a
    description against a least size of 0 or less. None (the setting
    off) and every whole number of 1 or more pass.
    """
    if given is None or given >= 1:
        return False
    _warn(errors.floor_not_positive(f"{given}"))
    return True


# THE LONG OPTIONS, in the order the parser below is given them, `--help`
# (argparse's own) first: what a word abbreviating several of them is said
# to match, in argparse's own order and words (`_ambiguous_at`).
# `tests/test_stage5_gate.py` holds it to the parser's own list.
_LONG_OPTIONS = (
    "--help",
    "--version",
    "--twin",
    "--out-dir",
    "--seed",
    "--replace",
    "--smallest-group",
    "--person",
    "--identifier",
    "--code",
    "--decimal-comma",
    "--measurement",
    "--century",
    "--date-column",
    "--twelve-hour",
    "--date-count",
    "--metadata-rows",
    "--delimiter",
    "--answers",
    "--keep-value",
    "--missing-value",
    "--day-first",
    "--sheet",
    "--first-row",
    "--name",
    "--replace-description",
    "--new-key",
    "--private-folder",
)
# THE ABBREVIATIONS THE BASE READ AS `--replace` KEEP THAT MEANING (lane
# CHON, plan P4-D464). argparse takes a word that begins one long option
# alone as that option, and refuses one that begins several; `--replace`
# was the only option starting `--r`, so `--r` to `--replac` read as it.
# `--replace-description` begins with all of them, so each is put back to
# `--replace` before argparse reads the line (`_kept_abbreviations`), an
# `=` and its value kept; `--replace-` and longer begin the new option
# alone. Every other abbreviation reads as before: no long option of the
# base begins `--n` or `--p`.
_KEPT_ABBREVIATIONS = {"--r": "--replace", "--re": "--replace", "--rep": "--replace", "--repl": "--replace", "--repla": "--replace", "--replac": "--replace"}
# The words argparse reads as its help option: `-h`, and every prefix of
# `--help` it takes (no other long option starts with `--h`).
_HELP_WORDS = ("-h", "--h", "--he", "--hel", "--help")
# A WORD OF SHORT OPTIONS RUN TOGETHER THAT STARTS WITH `-h`, such as
# `-hh` or `-hfoo`, may ask for the help page too, as the Python that runs
# decides (lane S5a's repair 2, Codex's item 2): `-hh` does on every
# supported Python, and `-hfoo` did on 3.11.15 and 3.13.14 alike. Such a
# word, and every word of `_HELP_WORDS`, is a candidate; whether argparse
# takes it as the help option there is asked of argparse itself
# (`_parse_arguments`).
_HELP_PREFIX = "-h"


def _kept_abbreviations(words: "list[str]") -> "list[str]":
    """The words as argparse is to read them: each abbreviation of `--replace` the base took, written whole (`_KEPT_ABBREVIATIONS`).

    Up to `--`, after which every word is a value. A word's part before an
    `=` decides, and the rest is kept. A fixed function of the list.
    """
    read: "list[str]" = []
    ended = False
    for word in words:
        if ended or word == "--":
            ended = True
            read += [word]
            continue
        # The part before an `=`, read a character at a time (the offline
        # audit's reason: no method of the value is called).
        head = ""
        for character in f"{word}":
            if character == "=":
                break
            head = head + character
        tail = f"{word}"[len(head) :]
        read += [_KEPT_ABBREVIATIONS[head] + tail if head in _KEPT_ABBREVIATIONS else word]
    return read


def _could_ask_for_help(word: str) -> bool:
    """Whether argparse could read ``word`` as its help option: a help word, or `-h` run on."""
    if word in _HELP_WORDS:
        return True
    return len(word) > len(_HELP_PREFIX) and word[: len(_HELP_PREFIX)] == _HELP_PREFIX


# WHEN ARGPARSE REFUSES A WORD ABBREVIATING SEVERAL OPTIONS (lane S5a's
# repair 2, Codex's item 3). Python 3.11's argparse sorts every word into
# an option or a value before it acts on any, and refuses such a word as
# it sorts it -- printing and exiting whatever it was asked -- so the
# refusal comes first wherever the word stands, before the help page and
# before any other refusal. From Python 3.12.7 and 3.13 (CPython's change
# gh-58573 in their changelogs) it refuses the word only when it reaches
# it in order, raising the refusal as any other: the help word before it
# shows the help page, an option before it that wants a value is refused
# for the value it lacks, and an option of two values takes it as one.
# The rule this module follows is the one of the Python it runs on, read
# off its version: measured on 3.11.15 as the first and on 3.12.13,
# 3.13.14 and 3.14.6 as the second (the gate asks argparse itself on
# whichever Python runs it). On the first the word is refused here, in
# argparse's words, before argparse is handed anything; on the second
# argparse is handed it and raises the refusal, printing nothing.
_AMBIGUITY_SORTED_FIRST = sys.version_info < (3, 12, 7)


def _ambiguous_at(words: "list[str]") -> "tuple[int, str]":
    """Where the first option abbreviated past one meaning stands, and argparse's words for it.

    A word starting `--` that is no option itself (before any `=`) and
    begins several of them is refused by argparse as ambiguous, in these
    words; (-1, "") where none stands before `--`.
    """
    for place in range(len(words)):
        word = words[place]
        if word == "--":
            return (-1, "")
        if not isinstance(word, str) or word[:2] != "--":
            continue
        prefix = ""
        for character in word:
            if character == "=":
                break
            prefix = prefix + character
        if prefix in _LONG_OPTIONS:
            continue
        matches = ""
        count = 0
        for option in _LONG_OPTIONS:
            if option[: len(prefix)] == prefix:
                matches = option if not matches else matches + ", " + option
                count = count + 1
        if count > 1:
            return (place, f"ambiguous option: {word} could match {matches}")
    return (-1, "")


def _refused_as_argparse_refuses(help_page: str, message: str) -> "typing.NoReturn":
    """Show argparse's own refusal -- its usage line, then its error -- and stop.

    The usage line is the help page's first block, which is what
    `format_usage` gives (`tests/test_stage5_gate.py` holds the two
    equal); the error line is argparse's own shape. Both reach the error
    stream, as argparse writes them, and the run is `unusable` (exit 2).
    """
    if not isinstance(help_page, str):
        raise TypeError("argparse's help page is text")
    usage = ""
    for line in help_page.split("\n"):
        if not line:
            break
        usage = usage + line + "\n"
    error = f"synthtwin: error: {message}"
    _show(_ERR, usage)
    _show(_ERR, error + "\n")
    # ...AND THE RESULT KEEPS THEM AS THE REFUSAL'S WORDS (lane S5a's
    # repair 2, Codex's item 4), the characters shown less the last line
    # feed, as `_warn` keeps a refusal's: without them a run with no
    # screen would lose its only explanation.
    session = _current()
    if session is not None:
        session.refusal_words += [usage[: len(usage) - 1], error]
    raise _Unusable()


def _commands_read(argv: "list[str] | None") -> "list[str]":
    """The command words the parser takes for this line: the base's four, and `twin` and `help` where the line names one (skeptic 1's item 4)."""
    if _command_word(argv) in (_TWIN, results.HELP):
        return [_PROFILE, _GENERATE, _VALIDATE, _DOCTOR, _TWIN, _HELP_WORD]
    return [_PROFILE, _GENERATE, _VALIDATE, _DOCTOR]


def _parse_arguments(
    argv: "list[str] | None", internal_smallest_group: "int | None"
) -> _Options:
    """Build the command line and read it; return the options.

    THE SMALLEST GROUP SIZE IS RAISED, NEVER LOWERED (plan P4-D426, the
    owner's answer of 2026-10-23). `--smallest-group`, under any spelling
    argparse takes for it, is refused here with code 2 -- before any
    command word is acted on, so nothing is read or written -- where it
    is no whole number or a number under `_SMALLEST_GROUP`, whichever
    command it was typed with. ``internal_smallest_group`` is `main`'s
    internal keyword of the same name: given, it IS the floor and the typed
    option is not read, as though that number had been typed before plan
    P4-D426 (`floor_chosen` True, so a run under 11 shows the warnings
    such a run showed). Nothing on the command line sets it.

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
        # ITS REFUSALS ARE RAISED, NOT PRINTED (plan P4-D395 part 3): a run
        # prints nothing and never exits, so argparse's words reach the
        # run's screen from `_refused_as_argparse_refuses`.
        exit_on_error=False,
        # ...AND ITS HELP OPTION IS A SWITCH (lane S5a's repair 2): the one
        # argparse adds prints the page to the process's own output and
        # exits whatever it is asked, so the same option is added below,
        # first, under the same two names and words, as a switch that
        # prints nothing; `_parse_arguments` reads where it is taken.
        add_help=False,
    )
    parser.add_argument(
        "-h", "--help", action="store_true", help="show this help message and exit"
    )
    parser.add_argument(
        "--version", action="store_true", help="print the version and exit"
    )
    parser.add_argument(
        "command",
        nargs="?",
        default=None,
        # The four words it always showed; the two new ones only on a line
        # that names one of them, the page showing the four all the same.
        choices=_commands_read(argv),
        metavar=None if len(_commands_read(argv)) == 4 else _COMMANDS_SHOWN,
        help=(
            "what to do: 'profile' describes a CSV table on this "
            "computer, 'generate' builds the synthetic twin from a "
            "description 'profile' wrote, 'validate' measures a CSV "
            "file against that description and writes the quality "
            "report, and 'doctor' checks this computer before a first "
            "run -- Python, the libraries it needs (numpy, pandas, "
            "pyarrow and scipy), the output folder and the memory -- and "
            "weighs a table's size against that memory when you name "
            "one, without opening it"
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
        # TEXT, READ AS A NUMBER BELOW (plan P4-D426), so that a word that
        # is no number is refused in this module's words and through its
        # display boundary rather than in argparse's.
        # NONE RATHER THAN THE NUMBER, so that typing the default is
        # distinguishable from not typing it (plan A-P4-37).
        default=None,
        metavar="ROWS",
        help=(
            "advanced: a value shared by fewer rows than this is left out "
            "of the profile and counted into a pooled remainder instead of "
            f"being named. THE DEFAULT IS {_SMALLEST_GROUP}: no group named "
            "anywhere in the profile covers fewer than "
            f"{_SMALLEST_GROUP} rows, so a value that fewer rows share is "
            "not named and does not reach the twin by name. It can be "
            "raised -- --smallest-group 20 leaves out every value fewer "
            "than 20 rows share -- and never lowered: a number under "
            f"{_SMALLEST_GROUP} is refused and nothing is written "
            f"(default: {_SMALLEST_GROUP})"
        ),
    )
    parser.add_argument(
        "--person",
        action="append",
        default=None,
        metavar="COLUMN",
        help=(
            "name the column that says which person each row is about -- a "
            "patient or study number. It is held as --identifier holds a "
            "column, and the table's people are counted by it alone, so "
            "another record-number column named with --identifier beside it "
            "(a clinician's or an encounter's) is held and joins nobody. May "
            "be given more than once"
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
            "nanoseconds-since-1970, days-since-1840 (MUMPS, with a contact "
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
        help=_KEEP_VALUE_HELP,
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
        # None where it was not typed, so `--first-row auto` typed is told
        # from the default (Codex's review of lane AQ, item 3): typed, it
        # replaces a kept answer about the first row.
        default=None,
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
    # -- THE INSTALLATION'S FOUR (contract 4.6b.4; lane CHON, plan P4-D464):
    # read by `profile`, handed on by `twin`.
    parser.add_argument(
        "--name",
        default=None,
        metavar="NAME",
        help=(
            "the name this table goes by on this computer, so that a table "
            "described again is known as the same table (the default is the "
            "file's name without its ending). This computer keeps a private "
            "record of each table it describes, beside its private key: describe "
            "a table again under the name it was first described under. A name "
            "holds no folder: a slash, a backslash, '..' or a control character "
            "is refused. Used by 'profile' and 'twin'"
        ),
    )
    parser.add_argument(
        "--replace-description",
        action="store_true",
        help=(
            "say that the earlier description of this table, made on this "
            "computer, was never shared with anyone, so this run may publish a "
            "different one. Without it, a run that would publish a different "
            "description of a table described before stops, where either of "
            "the two publishes relationships between columns: someone holding "
            "both could narrow a small group of patients. So 'synthtwin profile "
            "TABLE --answers QUESTIONS', run with the questions file answered "
            "after a first run that waited for the subject question, stops with "
            "exit status 1 where it would publish them. Used by 'profile' and "
            "'twin'"
        ),
    )
    parser.add_argument(
        "--new-key",
        action="store_true",
        help=(
            "make a new private key where this computer's key file is lost "
            "but its record of earlier descriptions stands. Each table "
            "described before is then refused until --replace-description says "
            "its earlier descriptions were never shared. Used by 'profile' and "
            "'twin'"
        ),
    )
    parser.add_argument(
        "--private-folder",
        default=None,
        metavar="FOLDER",
        help=(
            "the folder the private report is written in: for you alone, never "
            "shared (the default is a folder beside this computer's private "
            "key). Never the folder that holds the description or a twin. Used "
            "by 'profile' and 'twin'"
        ),
    )
    # parse_known_args rather than parse_args: argparse's own report of
    # words it did not recognize copies them to the error stream exactly
    # as typed, so a word carrying an escape sequence would instruct the
    # terminal from inside argparse, where this module's display
    # boundary cannot reach it (review item P1-R6-F11). Taking the
    # leftovers back lets the refusal go through `_warn` like every
    # other message -- and say something a non-programmer can act on.
    # THE HELP PAGE, AND ARGPARSE'S OWN REFUSALS, REACH THE RUN'S SCREEN
    # (plan P4-D395 part 3). argparse shows its help page the moment it
    # reads the help option and stops there, so the words before it are
    # read first -- a refusal among them is still the run's -- and the
    # page is then shown; a refusal argparse raises is shown in its own
    # words; and a word abbreviating several options is refused before
    # argparse reads it, because Python 3.11's argparse prints and exits
    # on that one whatever it is asked. That argparse sorts EVERY word into
    # options and values before it acts on the help option, so there a
    # word abbreviating several options is refused wherever it stands,
    # after the help word too (lane S5a's repair 1): `_ambiguous_at` reads
    # them all, up to `--` (`_AMBIGUITY_SORTED_FIRST`).
    # ON A PYTHON WHOSE ARGPARSE REFUSES SUCH A WORD ONLY IN ORDER (lane
    # S5a's repair 2, Codex's item 3), argparse is handed it: it raises that
    # refusal, as any other, where it reaches the word, the help word before
    # it is taken first, and an option of two values takes it as a value,
    # as that Python's argparse did before results existed.
    words = _kept_abbreviations(sys.argv[1:] if argv is None else [f"{word}" for word in argv])
    help_page = parser.format_help()
    _place, ambiguous = _ambiguous_at(words)
    if ambiguous and _AMBIGUITY_SORTED_FIRST:
        _refused_as_argparse_refuses(help_page, ambiguous)
    # WHERE ARGPARSE TAKES THE HELP OPTION (lane S5a's repair 2, Codex's
    # items 2 and 3). It is a plain switch here, so reading it prints
    # nothing; argparse's own printed the page and stopped the moment it
    # was taken, refusing nothing after it. So for each candidate word in
    # order, up to `--`, the words up to and including it are read: where
    # they read without a refusal and the switch is set, the help option is
    # taken there, every word before it read as the whole line reads it --
    # a candidate that is an option's value ends no option's values, and
    # one cut short makes that reading a refusal, so a value is never taken
    # for the help word. A candidate whose reading argparse refuses is
    # passed over: the whole line then answers with that refusal, or reads
    # on. Here, beside the parser, because the offline policy uses a value
    # an allowlisted API produced where it was made (plan D6.2).
    for place in range(len(words)):
        if words[place] == "--":
            break
        if not _could_ask_for_help(words[place]):
            continue
        try:
            before, _rest = parser.parse_known_args(words[: place + 1])
        except Exception:  # noqa: BLE001,S112 -- the import allowlist (plan
            # D6.2) admits argparse's parser alone, so its ArgumentError
            # cannot be named; a refused reading takes no help option.
            continue
        if before.help:
            _show(_OUT, _page_for(before.command, help_page))
            raise _HelpShown()
    try:
        args, not_understood = parser.parse_known_args(words)
    except Exception as refused:  # noqa: BLE001 -- the import allowlist
        # (plan D6.2) admits argparse's parser alone, so its ArgumentError
        # cannot be named; argparse raises nothing else here.
        _refused_as_argparse_refuses(help_page, f"{refused}")
    if args.help:
        # Taken where no candidate stood (none is known): the whole line
        # read without a refusal, so the page is what argparse showed.
        _show(_OUT, _page_for(args.command, help_page))
        raise _HelpShown()
    # THE COMMAND IS THE ONE ARGPARSE READ (lane S5a's repair 2, Codex's
    # item 1): a command word standing as an option's value, such as
    # `--out-dir profile validate`, named the wrong command before, and the
    # exit status is read off the command.
    session = _current()
    if session is not None:
        session.command = "" if args.command is None else f"{args.command}"
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
    floor_typed: "int | None" = None
    if internal_smallest_group is None and args.smallest_group is not None:
        floor_typed = _typed_floor(f"{args.smallest_group}")
    if args.command == _PROFILE and args.path is None:
        _refuse_the_command_line(
            "Please say which file to describe, for example: "
            "synthtwin profile my-table.csv"
        )
    if args.command == _TWIN and args.path is None:
        _refuse_the_command_line(
            "Please say which table to make a twin of, for example: "
            "synthtwin twin my-table.csv"
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
    # -- lane EZ-a (P4-D479): the columns said to name the person.
    person_named = args.person if args.person is not None else []
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
            internal_smallest_group
            if internal_smallest_group is not None
            else _SMALLEST_GROUP
            if floor_typed is None
            else floor_typed
        ),
        floor_chosen=(
            internal_smallest_group is not None or floor_typed is not None
        ),
        identifiers=list(named),
        codes=list(code_named),
        measurements=list(measured_named),
        decimal_commas=list(comma_named),
        answers=args.answers,
        kept_values=list(kept),
        missing_values=list(declared_missing),
        first_row=(
            _FIRST_ROW_AUTOMATIC if args.first_row is None else f"{args.first_row}"
        ),
        first_row_typed=args.first_row is not None,
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
        persons=list(person_named),
        name=None if args.name is None else f"{args.name}",
        replace_description=bool(args.replace_description),
        new_key=bool(args.new_key),
        private_folder=None if args.private_folder is None else f"{args.private_folder}",
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
    # -- lane TR (P4-D473): Q-CLOCK's answer, its own key.
    "19": asking.ANSWER_CLOCK_FIGURES,
    # -- lane NOTES (P4-D481): a column of sentences is free text, its own key.
    "20": asking.ANSWER_TEXT,
    "m": asking.ANSWER_MEASUREMENT,
    "c": asking.ANSWER_CODE,
    "i": asking.ANSWER_IDENTIFIER,
    "j": asking.ANSWER_JOINED,
    "d": asking.ANSWER_DECIMAL_COMMA,
    "t": asking.ANSWER_TWELVE_HOUR,
    "f": asking.ANSWER_CLOCK_FIGURES,
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
    """True where the run has somebody to ask: a reader handed to `run`.

    `main` hands `run` the terminal's reader exactly where
    `_a_person_at_the_terminal` says somebody is there, so a run of the
    command asks where it asked before results existed; `run` called
    without ``ask`` puts no question and reads nothing (plan P4-D395
    part 3). With no run open (a helper called on its own), the
    terminal is asked.
    """
    session = _current()
    if session is not None:
        return session.ask is not None
    return _a_person_at_the_terminal()


def _a_person_at_the_terminal() -> bool:
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
    # -- lane TR (P4-D473): Q-CLOCK's answer, at the keyboard too.
    asking.ANSWER_CLOCK_FIGURES: "19",
    # -- lane NOTES (P4-D481): free text, at the keyboard too.
    asking.ANSWER_TEXT: "20",
    # THE STANDING READING SHARES KEY 1 WITH `measurement`, and the two
    # never appear on one question: a column of figures offers
    # `measurement` as the reading it already has, and a joined-looking
    # column offers `keep`, which is the reading IT already has. Both
    # mean "make no declaration", and `_put_the_questions` gives
    # neither a branch, so they are one behaviour under two words --
    # the words differing because what a person is keeping differs.
    asking.ANSWER_KEEP: "1",
}


def _keep_beside_measurement(question: asking.Question) -> bool:
    """Whether a question offers `keep` and `measurement` as two answers (plan P4-D438).

    Question Q-UNIT does, and so does any question it reaches
    (`asking.with_unit_answers`): there `measurement` is no longer the
    standing reading but a declaration, so the two cannot share key 1
    (Codex's review of lane UN-1a, item 2: both were shown as `[1]`, and
    the answer was recorded as no declaration at all).
    """
    offered = [choice.answer for choice in question.choices]
    return asking.ANSWER_KEEP in offered and asking.ANSWER_MEASUREMENT in offered


def _key_shown(answer: str, question: asking.Question) -> str:
    """The key a person types for one answer of this question.

    `measurement` beside `keep` is typed `m`, its letter key, since key 1
    is `keep` there (`_keep_beside_measurement`).
    """
    if answer == asking.ANSWER_MEASUREMENT and _keep_beside_measurement(question):
        return "m"
    return _KEY_OF[answer]


def _the_question(
    question: asking.Question, place: int, total: int, held: bool = False
) -> str:
    """One column's question, as the person sees it.

    ``held`` is whether the column is held back while the question is
    open (`asking.unanswered_identities`): Enter leaves the question
    open, as a run with nobody at the keyboard leaves it, so the last
    line says the column stays held rather than that the first reading
    above is kept (lane TT's repair, the orchestrator's LANE TT RULINGS
    2 (1)).

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
        key = _key_shown(choice.answer, question)
        lines = lines + (
            f"\n      [{key}] {choice.means}\n"
            f"          then the description publishes {choice.publishes}"
        )
    enter = (
        "    Press Enter to keep it held as record numbers until it is "
        "answered: none of its values is published."
        if held
        else "    Press Enter to keep the reading synthtwin made, which is "
        "the first one above."
    )
    return (
        f"\n  Column {place} of {total}: '{_shown(question.name)}'\n"
        f"    what synthtwin saw: {_one_stop(question.shape)}\n"
        f"    What does this column hold?{lines}\n"
        f"{enter}"
    )


def _one_stop(sentence: str) -> str:
    """A sentence ended by one full stop, whether or not it carried its own (lane EZ-a's repair, LANE EZ RULINGS 4 (7))."""
    if sentence[len(sentence) - 1 :] == ".":
        return sentence
    return f"{sentence}."


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
    written: asking.Answers,
    first_row: str,
    declared_delimiter: str,
    kept: "tuple[tuple[str, str], ...]" = (),
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
    # A QUESTION AN EARLIER RUN KEPT AN ANSWER TO IS NOT JUDGED HERE (plan
    # P4-D408): the run that wrote the file read the table by that
    # answer, so `_kept_reading_changed` sets the reading this run takes
    # against it instead of against what was typed.
    subjects = {subject: True for subject, _word in kept}
    if asking.FIRST_ROW_SUBJECT not in subjects:
        if written.first_row == asking.ANSWER_FIRST_ROW_NAMES:
            if first_row != _FIRST_ROW_NAMES:
                changed += [asking.FIRST_ROW_SUBJECT]
        elif written.first_row == asking.ANSWER_FIRST_ROW_DATA:
            if first_row == _FIRST_ROW_NAMES:
                changed += [asking.FIRST_ROW_SUBJECT]
    if asking.DELIMITER_SUBJECT not in subjects:
        if written.delimiter and written.delimiter != declared_delimiter:
            changed += [asking.DELIMITER_SUBJECT]
    return changed


def _kept_reading_changed(
    written: asking.Answers,
    first_row: str,
    declared_delimiter: str,
    kept: "tuple[tuple[str, str], ...]",
    automatic: bool = False,
) -> "list[str]":
    """The kept answers about how the file is read that this run would not follow.

    Plan P4-D408. `kept` is `asking.kept_reading` of
    the questions file as it was handed back: how the run that WROTE the
    file read the table, so the column names in the file are the names
    under that reading. This run's reading is the file's answer where it
    gives one -- the kept entry, edited or not, or the same question
    answered again -- and otherwise the typed option, which replaces the
    kept entry (`asking.typed_over_kept`). A subject is named where the
    two differ, or where the kept entry no longer says which reading it
    was. Measured before this check: a table whose header `column_2,
    column_1` reads as a record, answered `names` in round one and
    `identifier` / `keep` for its two columns in round two, then handed
    back in round three with the kept `names` edited to `first-record`
    -- or with `--first-row data` typed -- put `identifier` on the visit
    labels and `keep` on the subject column, and published 200 of 200
    real subject codes with their counts.

    `automatic` (Codex's review of lane AQ, item 3): `--first-row auto`
    was typed over the kept answer about the first row, and the file
    lists the names its answers use. That reading is the one a run given
    no answer takes, which the read itself settles, so it is not set
    against the kept answer here: the names it reads are set against the
    file's list after the read (`_answered_under_other_names`).

    Guarantees: each subject once, in the order `kept` names them. A
    fixed function of the five. Raises nothing. No I/O.
    """
    changed: "list[str]" = []
    for subject, before in kept:
        if subject in changed:
            continue
        now = ""
        if subject == asking.FIRST_ROW_SUBJECT:
            now = written.first_row
            if not now and automatic:
                continue
            if not now and first_row == _FIRST_ROW_NAMES:
                now = asking.ANSWER_FIRST_ROW_NAMES
            elif not now and first_row == _FIRST_ROW_DATA:
                now = asking.ANSWER_FIRST_ROW_DATA
        else:
            now = asking.delimiter_answer(
                written.delimiter if written.delimiter else declared_delimiter
            )
        if not before or now != before:
            changed += [subject]
    return changed


def _kept_reading_not_kept(
    path: str, changed: "list[str]", named: "list[str]"
) -> str:
    """The refusal of a run that would read the table another way than the file's writer (plan P4-D408)."""
    moved = ""
    for one in changed:
        moved = f"{moved}; {one}" if moved else one
    columns = ""
    for one in named:
        columns = f"{columns}, '{one}'" if columns else f"'{one}'"
    return (
        f"The questions file at {path} was written by a run that read "
        f"your table by an answer it keeps under '{asking.ANSWERED_BEFORE}' "
        f"-- {moved} -- and this run would read it another way, by an "
        f"answer changed in the file or typed on the command line, while "
        f"the file also names {columns}. synthtwin will not act on both "
        f"at once: the column names in that file are the names under the "
        f"earlier reading, and reading the table another way changes which "
        f"column each name stands for, so an answer made by name would "
        f"reach a column you were not looking at. Either keep the earlier "
        f"answer about how the file is read, or do it in two runs: clear "
        f"every answer that names a column, '{asking.ANSWERED_BEFORE}' "
        f"included, run the command again with the new reading, then "
        f"answer the columns in the questions file that run writes. "
        f"Nothing was written."
    )


def _typed_answers(
    codes: "list[str]",
    identifiers: "list[str]",
    measurements: "list[str]",
    commas: "list[str]",
    twelve_hours: "list[str]",
    counted: "dict[str, str]",
    centuries: "dict[str, int]",
    date_columns: "list[str]",
    day_first: bool,
    delimiter: str,
    first_row: str,
    centuries_reset: "list[str] | None" = None,
    first_row_typed: bool = False,
) -> "tuple[tuple[str, str], ...]":
    """This command line's declarations as `(column, answer)` (plan P4-D408).

    What `asking.answers_in` sets against the answers an earlier run
    kept: a declaration typed now is later than any of them, so it
    replaces one about the same column. A question about the whole file
    is named by its subject. A default typed all the same is a statement
    too (Codex's review of lane AQ, item 3): `--century NAME=1969`, in
    `centuries_reset`, is the answer naming the standing window, and
    `--first-row auto` typed is `asking.TYPED_FIRST_ROW_AUTOMATIC`; each
    replaces a kept answer of its family. A fixed function of the
    arguments. Raises nothing. No I/O.
    """
    said: "list[tuple[str, str]]" = []
    for answer, names in (
        (asking.ANSWER_CODE, codes),
        (asking.ANSWER_IDENTIFIER, identifiers),
        (asking.ANSWER_MEASUREMENT, measurements),
        (asking.ANSWER_DECIMAL_COMMA, commas),
        (asking.ANSWER_TWELVE_HOUR, twelve_hours),
        (asking.ANSWER_DATES, date_columns),
    ):
        for name in names:
            said += [(name, answer)]
    for name in sorted(counted):
        said += [(name, counted[name])]
    for name in sorted(centuries):
        word = asking.century_answer(centuries[name])
        if word:
            said += [(name, word)]
    for name in sorted(centuries_reset or []):
        said += [(name, asking.ANSWER_CENTURY_POSIX)]
    if day_first:
        said += [(asking.DAY_FIRST_SUBJECT, asking.ANSWER_DAY_FIRST)]
    word = asking.delimiter_answer(delimiter)
    if word:
        said += [(asking.DELIMITER_SUBJECT, word)]
    if first_row == _FIRST_ROW_NAMES:
        said += [(asking.FIRST_ROW_SUBJECT, asking.ANSWER_FIRST_ROW_NAMES)]
    elif first_row == _FIRST_ROW_DATA:
        said += [(asking.FIRST_ROW_SUBJECT, asking.ANSWER_FIRST_ROW_DATA)]
    elif first_row_typed:
        said += [(asking.FIRST_ROW_SUBJECT, asking.TYPED_FIRST_ROW_AUTOMATIC)]
    return tuple(said)


def _answers_given(
    columns: "list[str]",
    codes: "list[str]",
    identifiers: "list[str]",
    measurements: "list[str]",
    commas: "list[str]",
    twelve_hours: "list[str]",
    counted: "dict[str, str]",
    centuries: "dict[str, int]",
    centuries_kept: "list[str]",
    date_columns: "list[str]",
    dates_kept: "list[str]",
    identities_kept: "tuple[str, ...]",
    missing_dates: "list[str]",
    real_values: "list[str]",
    code_shapes: "dict[str, str]",
    first_row: str,
    metadata_answer: str,
    delimiter: str,
    day_first: bool,
    month_first: bool,
    safe_harbor_no: "tuple[str, ...]" = (),
    safe_harbor_yes: "tuple[str, ...]" = (),
    units_kept: "tuple[str, ...]" = (),
    commas_kept: "tuple[str, ...]" = (),
    ages_counted_in: "tuple[tuple[str, str], ...]" = (),
    safe_harbor_dates_no: "tuple[str, ...]" = (),
    safe_harbor_dates_yes: "tuple[str, ...]" = (),
    clock_figures: "tuple[str, ...]" = (),
    sentences_text: "tuple[str, ...]" = (),
    people_keys_kept: "tuple[str, ...]" = (),
    values_keyed: "tuple[str, ...]" = (),
    values_kept_whole: "tuple[str, ...]" = (),
) -> "asking.Given":
    """Every answer this run acts on, as `asking.answered_before` writes it.

    Plan P4-D408: the declarations in force, whichever route each came
    by -- a questions file, an earlier run's kept answers, the command
    line or the screen. A typed `--metadata-rows` is not among them: the
    file asks to confirm it where the file does not bear it out, and
    writing it as an answer would confirm it for the person. Typed
    `--keep-value` and `--missing-value` name values, and the questions
    file carries none. A fixed function of the arguments. Raises nothing.
    """
    day_order = ""
    if day_first:
        day_order = asking.ANSWER_DAY_FIRST
    elif month_first:
        day_order = asking.ANSWER_MONTH_FIRST
    first_row_word = ""
    if first_row == _FIRST_ROW_NAMES:
        first_row_word = asking.ANSWER_FIRST_ROW_NAMES
    elif first_row == _FIRST_ROW_DATA:
        first_row_word = asking.ANSWER_FIRST_ROW_DATA
    return asking.Given(
        columns=tuple(columns),
        codes=tuple(codes),
        identifiers=tuple(identifiers),
        measurements=tuple(measurements),
        decimal_commas=tuple(commas),
        twelve_hours=tuple(twelve_hours),
        date_counts=tuple((name, counted[name]) for name in sorted(counted)),
        centuries=tuple((name, centuries[name]) for name in sorted(centuries)),
        centuries_kept=tuple(centuries_kept),
        date_columns=tuple(date_columns),
        date_columns_kept=tuple(dates_kept),
        identities_kept=tuple(identities_kept) + _persons_kept_at_the_prompt(identities_kept),
        people_keys_kept=people_keys_kept,
        units_kept=units_kept,
        commas_kept=commas_kept,
        safe_harbor_no=safe_harbor_no,
        safe_harbor_yes=safe_harbor_yes,
        ages_counted_in=ages_counted_in,
        safe_harbor_dates_no=safe_harbor_dates_no,
        safe_harbor_dates_yes=safe_harbor_dates_yes,
        # -- lane TR (P4-D473)
        clock_figures=clock_figures,
        # -- lane NOTES (P4-D481)
        sentences_text=sentences_text,
        # -- lane KV (P4-D487)
        values_keyed=values_keyed,
        values_kept_whole=values_kept_whole,
        missing_dates=tuple(
            (name, code_shapes[name] if name in code_shapes else "")
            for name in missing_dates
        ),
        real_values=tuple(
            (name, code_shapes[name] if name in code_shapes else "")
            for name in real_values
        ),
        first_row=first_row_word,
        metadata=metadata_answer,
        delimiter=asking.delimiter_answer(delimiter),
        day_order=day_order,
    )


def _earlier_answers_dropped(
    carried: "tuple[tuple[str, str, str], ...]",
    columns: "list[str]",
    given: "asking.Given",
) -> "list[str]":
    """The columns whose kept answer this run would drop (plan P4-D408).

    Each answer an earlier run kept and no later one replaced that names
    a column `columns` does not hold, or that the section written from
    `given` would not keep (`asking.answers_not_kept`): each name once,
    in the order `carried` names them. A fixed function of the three.
    Raises nothing. No I/O.
    """
    held = {one: 1 for one in columns}
    dropped: "list[str]" = []
    for name, _answer, family in carried:
        if family in asking.FILE_FAMILIES or name in held:
            continue
        if name not in dropped:
            dropped += [name]
    for name in asking.answers_not_kept(carried, asking.answered_before(given)):
        if name not in dropped:
            dropped += [name]
    return dropped


def _answered_under_other_names(path: str) -> str:
    """The refusal of answers made by name under names this run does not read (plan P4-D408)."""
    return (
        f"The questions file at {path} answers columns by the names listed "
        f"under '{asking.ANSWERED_BEFORE_COLUMNS}', and this run reads your "
        f"table under other names: an answer about how the file is read "
        f"was taken out of the file or replaced by '--first-row auto', or "
        f"the file was written for another table. synthtwin will not act "
        f"on an answer made by name when "
        f"that name may now stand for another column. Put back the answer "
        f"about how the file is read, or clear every answer that names a "
        f"column, '{asking.ANSWERED_BEFORE}' included, and run the command "
        f"again. Nothing was written."
    )


def _earlier_answers_not_kept(path: str, dropped: "list[str]") -> str:
    """The refusal of a run that would drop an answer an earlier run kept (plan P4-D408)."""
    named = ""
    for one in dropped:
        named = f"{named}, '{one}'" if named else f"'{one}'"
    return (
        f"The questions file at {path} keeps answers given in an earlier "
        f"run, and this run cannot keep the ones about {named}: the table "
        f"has no column of that name, or another answer in the file or on "
        f"the command line contradicts it. synthtwin does not drop an "
        f"answer you gave without telling you. Check that the file was "
        f"written for this table, then answer those again under "
        f"'answered_before' -- or clear the answer that contradicts them "
        f"-- and run the command again. Nothing was written."
    )


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
        # QUOTED FOR THE SHELL like every other line to type (lane CF4b,
        # its skeptic's item 2): `--twelve-hour Visit time` printed bare
        # was two words, and a name holding `&` ran what followed it.
        flags = _joined(
            [_typed_option("--twelve-hour", one.name) for one in twelve], " "
        )
        said = said + (
            f" Where every hour lies from 1 to 12 and no cell writes AM or "
            f"PM, a 12-hour clock writes the same cells, and 12:15 is then "
            f"a quarter past midnight rather than past noon; only you know "
            f"which clock wrote them.\n\n"
            f"If any of them is a 12-hour clock, run the command again "
            f"naming it:\n  {flags}{_quoting_said(flags)}"
        )
    if joined:
        flags = _joined(
            [_typed_option("--measurement", one.name) for one in joined], " "
        )
        said = said + (
            f"\n\nA time whose hour is written in one figure is also two "
            f"numbers joined by a colon, which is how a duration in minutes "
            f"and seconds is written. If any of them holds such numbers, "
            f"run the command again naming it:\n  {flags}{_quoting_said(flags)}"
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


def _people_floor_said() -> str:
    """The sentence beside an open person question where the table floor is on.

    Plan P4-D425: an open question never refuses a table, and the
    people half of the table floor applies once the column is answered
    as one that names people. One sentence, said by both notices.
    """
    return (
        f"Once a column is answered as one that names people, the table "
        f"floor counts those people too: a table in which one person has "
        f"several rows needs at least {parsing.TABLE_PEOPLE_FLOOR:,} "
        f"people, beside {parsing.TABLE_ROW_FLOOR:,} rows that hold a "
        f"value, or synthtwin refuses it and writes nothing. An "
        f"unanswered question does not refuse the table."
    )


def _assumptions_notice(
    questions: "list[asking.Question]", small_tables_refused: bool = False
) -> str:
    """What is printed where there is nobody to ask.

    The person chose the tool; they did not choose to be guessed at.
    This says what was assumed and the exact words that correct it, so
    a scripted run is one rerun away from right rather than silently
    wrong. ``small_tables_refused`` adds, to the person question's block, when the
    table floor's people half applies (plan P4-D425).
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
    # ...AND A COLUMN OF LISTS WRITTEN AS RECORD NUMBERS (plan P4-D424),
    # which is read as labels or text, and is asked what its values are.
    records: list[asking.Question] = []
    # ...AND WHOLE NUMBERS EACH ON ONE ROW OR IN SEQUENCE (lane HX5, plan
    # P4-D436), held until answered: told what the hold is, never that it
    # is averaged.
    singles: list[asking.Question] = []
    # -- 3b.R4 (P4-D384): ...AND A COLUMN OF NUMBERS LYING WHERE A COUNTING
    # SYSTEM WRITES DATES (question Q3), which is told what it would gain
    # as dates and the option that reads it so.
    dated: list[asking.Question] = []
    # ...AND A UNIT COLUMN READ AS LABELS (question Q-UNIT, plan P4-D438),
    # which is not read as measurements: falling through would tell it so.
    units: list[asking.Question] = []
    # ...AND A COLUMN WHOSE COMMA MAY BE ITS DECIMAL POINT (question Q-COMMA
    # and its mirror, plan P4-D443), which is read as labels or with a
    # comma between thousands: falling through would say measurements.
    commas: list[asking.Question] = []
    grouped: list[asking.Question] = []
    for question in questions:
        if asking.asks_about_a_clock(question):
            clocks += [question]
        elif question.reason == asking.BECAUSE_UNIT:
            units += [question]
        elif question.reason == asking.BECAUSE_COMMA:
            commas += [question]
        elif question.reason == asking.BECAUSE_COMMA_THOUSANDS:
            grouped += [question]
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
        elif question.reason == asking.BECAUSE_LISTED_RECORD_NUMBERS:
            records += [question]
        elif question.reason == asking.BECAUSE_EACH_ON_ONE_ROW:
            singles += [question]
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
    if units:
        flags = _joined(
            [_typed_option("--measurement", one.name) for one in units], " "
        )
        blocks += [
            f"THESE COLUMNS WERE READ AS LABELS, AND MIGHT BE AMOUNTS IN A "
            f"UNIT.{_listing(units, False)}\n\n"
            f"Each column above is being described as a list of values, each "
            f"with its count; read as amounts, each unit's numbers would be "
            f"described with an average, a spread and points along its range, "
            f"and the twin would write numbers beside the same unit. Only you "
            f"know which this is.\n\n"
            f"If any of them holds amounts, run the command again naming "
            f"them:\n  {flags}{_quoting_said(flags)}"
        ]
    if commas:
        flags = _joined(
            [_typed_option("--decimal-comma", one.name) for one in commas], " "
        )
        blocks += [
            f"THESE COLUMNS WERE READ AS VALUES KEPT AS WRITTEN, AND MIGHT BE "
            f"NUMBERS WRITTEN WITH A COMMA FOR THEIR DECIMAL POINT."
            f"{_listing(commas, False)}\n\n"
            f"Each column above keeps its commas as written and is described "
            f"as labels or as text, never as numbers: as labels, the values "
            f"enough rows share are listed with their counts; as text, no "
            f"value is published. Read with a comma for the decimal point, "
            f"its numbers would be described with an average, a spread and "
            f"points along its range. Two figures with a comma between them "
            f"are a decimal and also two choices, and only you know which "
            f"this is.\n\n"
            f"If any of them writes a comma for its decimal point, run the "
            f"command again naming them:\n  {flags}{_quoting_said(flags)}"
        ]
    if grouped:
        flags = _joined(
            [_typed_option("--decimal-comma", one.name) for one in grouped], " "
        )
        blocks += [
            f"THESE COLUMNS WERE READ WITH A COMMA BETWEEN THOUSANDS, AND "
            f"MIGHT BE WRITTEN WITH A COMMA FOR THEIR DECIMAL POINT."
            f"{_listing(grouped, False)}\n\n"
            f"Each column above is being described with its comma as a mark "
            f"between thousands. If the comma is the decimal point, each value "
            f"written with a comma is being read a thousand times too large "
            f"(1,250 as 1250, not 1.25), while a value written without one "
            f"reads the same either way, so the column's average, spread and "
            f"points along its range are off by as much as those values weigh "
            f"in it. Only you know which it is.\n\n"
            f"If any of them writes a comma for its decimal point, run the "
            f"command again naming them:\n  {flags}{_quoting_said(flags)}"
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
    # ...WHERE NO `--person` WAS GIVEN: a column given so says who the people
    # are, and one that is different on every row counts the table in rows,
    # its people (lane EZ-a's repair; the statistics check's item 1: the
    # block told such a run that no column names people and taught
    # `--identifier` on the clinician number).
    if people and not _persons_given():
        flags = _joined(
            [_typed_option("--identifier", one.name) for one in people], " "
        )
        floor_said = f" {_people_floor_said()}" if small_tables_refused else ""
        blocks += [
            f"THESE COLUMNS MIGHT NAME THE PEOPLE YOUR ROWS ARE ABOUT."
            f"{_listing(people, False)}\n\n"
            f"No column that names PEOPLE has been declared, so this "
            f"table's population was counted in ROWS. If one row is one "
            f"visit rather than one person, that count is larger than "
            f"the number of people in the table, and synthtwin cannot "
            f"tell which it is: a column whose values repeat can be a "
            f"subject number or a ward.{floor_said}\n\n"
            f"If any of them names people, run the command again naming "
            f"them:\n  {flags}{_quoting_said(flags)}"
        ]
    if records:
        codes = _joined(
            [_typed_option("--code", one.name) for one in records], " "
        )
        flags = _joined(
            [_typed_option("--identifier", one.name) for one in records], " "
        )
        blocks += [
            f"THESE COLUMNS HOLD SEVERAL VALUES IN A CELL, WRITTEN AS RECORD "
            f"NUMBERS ARE.{_listing(records, False)}\n\n"
            f"Each cell above holds a list, and its values are written the "
            f"way record numbers are written -- and also the way codes are. "
            f"Only you know which they are.\n\n"
            f"If they are codes, run the command again naming them:\n  "
            f"{codes}{_quoting_said(codes)}\n"
            f"If they are record numbers, name them so instead:\n  "
            f"{flags}{_quoting_said(flags)}"
        ]
    if singles:
        codes = _joined(
            [_typed_option("--code", one.name) for one in singles], " "
        )
        flags = _joined(
            [_typed_option("--identifier", one.name) for one in singles], " "
        )
        blocks += [
            f"THESE COLUMNS HOLD WHOLE NUMBERS THAT EACH STAND ON ONE ROW, "
            f"RUN IN SEQUENCE, OR CARRY LETTERS BEFORE FIVE FIGURES OR MORE, "
            f"AS RECORD NUMBERS DO.{_listing(singles, False)}"
            f"\n\n"
            f"Each column above is written the way record numbers are -- "
            f"one value a row, numbers counting up, or letters and five "
            f"figures or more on fewer than two rows a value -- and also the "
            f"way some measurements are. Until you say which, no value of it is "
            f"published and its twin writes made-up record numbers. Only "
            f"you know which it is.\n\n"
            f"If they are measurements or counts, answer `keep` in the "
            f"questions file. If they are codes, run the command again "
            f"naming them:\n  {codes}{_quoting_said(codes)}\n"
            f"If they are record numbers, name them so instead:\n  "
            f"{flags}{_quoting_said(flags)}"
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


def _asked(prompt: str) -> "str | None":
    """One line from the run's reader, or None where the person ended input.

    The reader is `run`'s ``ask`` (the terminal's, `_terminal_ask`, under
    `main`); with no run open the terminal is read. A run with no reader
    reads nothing.
    """
    session = _current()
    if session is None or session.ask == TERMINAL:
        return _terminal_ask(prompt)
    if not isinstance(session.ask, list):
        return None
    if session.answered >= len(session.ask):
        return None
    line = session.ask[session.answered]
    session.answered = session.answered + 1
    if not isinstance(line, str):
        return None
    return line


# WHAT ENTER GIVES AT A PROMPT: NO ANSWER (lane TT's repair; the
# orchestrator's LANE TT RULINGS 2 (1)). The question is left open, as a
# run with nobody at the keyboard leaves it, so the key a person presses
# when they do not know never releases more than nobody's run does:
# measured on lane TT's head c4925cd8 at 20,000 rows, Enter at the record
# number's question took it as answered `keep`, and 19,998 of 20,000 real
# record numbers reached the twin, where the same run with nobody at the
# keyboard held the column and wrote none. No key reaches this word and no
# question offers it, so it is never recorded as an answer.
_LEFT_OPEN = "(left open)"

# WHAT CTRL+D AND CTRL+Z ARRIVE AS IN A WINDOWS CONSOLE (lane EZ-a, plan
# P4-D479; the orchestrator's LANE EZ RULINGS 2 (2)): typed there, each is
# a character of its own on the line, U+0004 or U+001A, handed over with
# Enter. A line made only of them ends the answers exactly as the end of
# input does, so a person who presses Ctrl+D on Windows is never told to
# type one of the answers offered. And the words that name the two keys,
# the same wherever a screen line names them (RULINGS 2 (1)).
_END_OF_INPUT_TYPED = "\x04\x1a"
_STOP_KEYS_SAID = (
    "To stop, press Ctrl+C; to end your answers, press Ctrl+D (on Windows: "
    "Ctrl+Z, then Enter)"
)


def _ends_input(line: str) -> bool:
    """Whether a typed line is made only of the characters Ctrl+D and Ctrl+Z arrive as in a Windows console.

    Spaces around them are not read. Raises TypeError for a line that is
    not text (the offline audit's type gate, as `_cleaned`).
    """
    if not isinstance(line, str):
        raise TypeError("a typed line must be text")
    typed = line.strip()
    if not typed:
        return False
    for character in typed:
        if character not in _END_OF_INPUT_TYPED:
            return False
    return True


def _read_one_answer(
    standing: str = asking.ANSWER_MEASUREMENT, keep_on_one: bool = False
) -> "str | None":
    """One typed answer, or None where the person ended the run.

    Enter alone gives ``standing``: the question put at the keyboard
    hands `_LEFT_OPEN`, so Enter leaves it unanswered and a person who
    does not know can press through and lose nothing they had, nor
    release anything a run with nobody at the keyboard holds.
    Anything unrecognized is asked again rather than assumed: this is
    the one place a wrong guess would be recorded in the profile as a
    fact the person had stated.

    THE QUESTION ON SCREEN MAY NAME ITS OWN ANSWERS (lane EZ-a, plan
    P4-D479): where the run's session holds them (`_Session.offered_now`,
    each answer with the key shown beside it, set by the second round and
    the subject question while their question is on screen), the key
    shown or the answer's own word is taken, whatever its capitals, and
    nothing else is. Called with one argument, as the suite's stand-ins
    for the person call it. A line made only of what Ctrl+D or Ctrl+Z
    arrive as in a Windows console ends the answers (`_ends_input`).
    """
    session = _current()
    offered = session.offered_now if session is not None else ()
    while True:
        line = _asked("    > ")
        if line is None or _ends_input(line):
            return None
        typed = _cleaned(line)
        if not typed:
            # ...and what it keeps is THIS question's standing reading,
            # not a fixed one (review round 1 of landing L17a, item 3).
            # A joined-looking column's standing reading is the text or
            # label reading it already has; returning `measurement`
            # there named a reading Enter does not give.
            return standing
        if offered:
            for key, word in offered:
                if typed == _cleaned(key) or typed == _cleaned(word):
                    return word
            _say(
                "    Please type one of the answers offered, or the key in "
                "square brackets beside it, or press Enter to leave the "
                "question open."
            )
            continue
        # KEY 1 IS `keep` WHERE `measurement` IS AN ANSWER OF ITS OWN
        # (plan P4-D438; `_keep_beside_measurement`), typed `m` there.
        if keep_on_one and typed == "1":
            return asking.ANSWER_KEEP
        if typed in _ANSWER_KEYS:
            return _ANSWER_KEYS[typed]
        _say(
            "    Please type one of the numbers offered, or press Enter "
            "to leave the question unanswered."
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


def _units_not_asked_again(
    questions: "list[asking.Question]",
    kept: "list[str]",
    persons_kept: "tuple[str, ...]" = (),
) -> "list[asking.Question]":
    """The questions less Q-UNIT and Q-COMMA where an earlier answer kept the labels (plans P4-D438, P4-D443).

    The orchestrator's LANE UN-1a RULINGS 1 (2), on plan P4-D408's rule
    that the questions file keeps every answer across rounds: a column
    answered `keep` to question Q-UNIT is not put the question again, as
    Q6's `keep` is not. A fixed function of the three. Raises nothing.

    ...AND LESS THE PERSON QUESTION WHERE AN ANSWER KEPT ITS COLUMN
    (``persons_kept``: `Answers.identities_kept_answered`; lane EZ-a, plan
    P4-D479; the orchestrator's LANE EZ RULINGS 1 (7)). The `keep` stands
    under `answered_before` and the column is described as that answer
    describes it; measured on the base at 20,000 rows, the question was
    put again under `read_as_now: keep` every round, the description the
    same byte for byte whether it was answered `keep` again or left blank.
    """
    if not kept and not persons_kept:
        return questions
    return [
        question
        for question in questions
        if not (
            question.reason in (asking.BECAUSE_UNIT, asking.BECAUSE_COMMA)
            and question.name in kept
        )
        and not (
            question.reason == asking.BECAUSE_REPEATS_AND_MANY
            and question.name in persons_kept
        )
    ]


def _answer_stands(answer: str, put: "tuple[str, str, str]") -> None:
    """Record that a question put at a prompt was answered other than with Enter, so no closing line counts it open.

    Lane EZ-a's repair (the orchestrator's LANE EZ RULINGS 4 (4)): the
    questions file puts such a question again under the reading its answer
    gave (plan P4-D401), its `your_answer` blank, and the closing lines
    counted it 'still open' and sent the person round again (measured at
    20,000 rows: a column of three-figure numbers answered at the first
    prompt was said open on every run). ``put`` is the question by its
    column, role and reason (`asking.question_put`).
    """
    session = _current()
    if session is not None and answer != _LEFT_OPEN and put not in session.answers_standing:
        session.answers_standing += [put]


def _answers_that_stand() -> "list[tuple[str, str, str]]":
    """The questions of this command whose answers stand (`_answer_stands`), each by its column, role and reason.

    A later round's description is handed the questions file that carries
    them (an answer at the first prompt that keeps a held column's reading
    is no option at all), so its repeat line names that file too (lane
    EZ-a's repair: measured, the repeat line printed after a column of
    three-figure numbers was answered at the first prompt held that column
    when run, and the description differed).
    """
    session = _current()
    return [] if session is None else list(session.answers_standing)


def _answer_typed(standing: str, keep_on_one: bool) -> "str | None":
    """One typed answer, key 1 read as `keep` where `measurement` is an answer of its own.

    The reader is asked with its second argument only there, so a
    question offering no such pair reads exactly as it always did.
    """
    if keep_on_one:
        return _read_one_answer(standing, True)
    return _read_one_answer(standing)


def _figures_not_taken_said(names: "list[str]", read: object, settings: object) -> None:
    """Say each `clock-figures` answer that is not taken because a time would be written as a missing spelling (plan P4-D473).

    Codex's review of lane TR, item 2: the description reads such a column
    as it read before the answer (`taxonomy.clock_figures_reading`), and
    the run says why, naming no value. Reads each named column's cells
    once. Raises TypeError where the settings are not settings or the
    table not a table (internal invariants), and whatever
    `reading.column_values` raises. No other I/O.
    """
    from synthtwin import reading, taxonomy

    if not names:
        return
    if not isinstance(settings, taxonomy.Settings):
        raise TypeError("internal check: the settings are not settings")
    if not isinstance(read, reading.Table):
        raise TypeError("internal check: the table is not a table")
    for name in names:
        for place, held in enumerate(read.column_names):
            if held != name:
                continue
            found = taxonomy.clock_figures_reading(reading.column_values(read, place), settings)
            if found == taxonomy.FIGURES_ABSENT:
                _warn(
                    errors.the_clock_figures_answer_was_not_taken(name),
                    caution=results.CAUTION_DECLARATION_DID_NOT_REACH,
                    column=name,
                )


def _put_the_questions(
    questions: "list[asking.Question]",
    held: "tuple[str, ...]" = (),
) -> "tuple[list[str], list[str], list[str], list[str], list[str], list[tuple[str, str]], list[tuple[str, str, str]], list[str]] | None":
    """Put every question; return the columns named as codes and as IDs, and the questions left open.

    None where the person ended the run at a prompt: Ctrl-C and Ctrl-D
    mean stop, and stopping must not write a profile built on half an
    interview. ``held`` names the columns held back while their
    question is open; the last item returned names each question Enter
    left unanswered (`_LEFT_OPEN`) by its column, role and reason
    (`asking.question_put`), which the run then reads as nobody's run
    reads an unanswered question (lane TT's repair; the orchestrator's
    LANE TT RULINGS 2 (1)).
    """
    total = len(questions)
    _say(
        f"\n{'=' * 66}\n"
        f"{total} COLUMN(S) CAN BE READ MORE THAN ONE WAY\n"
        f"{'=' * 66}\n"
        f"synthtwin cannot tell a coding system from a measurement -- "
        f"they are written identically, and only you know which these "
        f"are. Press Enter to leave a question unanswered, as a run with "
        f"nobody at the keyboard leaves it. Your answers "
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
    left_open: "list[tuple[str, str, str]]" = []
    # -- lane TR (P4-D473): the columns answered `clock-figures`.
    figures: list[str] = []
    place = 0
    for question in questions:
        place = place + 1
        _say(_the_question(question, place, total, question.name in held))
        both = _keep_beside_measurement(question)
        answer = _answer_typed(_LEFT_OPEN, both)
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
                "to leave the question unanswered."
            )
            answer = _answer_typed(_LEFT_OPEN, both)
        if answer is None:
            return None
        _answer_stands(answer, asking.question_put(question))
        _person_kept(answer, question)
        if answer == _LEFT_OPEN:
            left_open += [asking.question_put(question)]
        elif answer == asking.ANSWER_CODE:
            codes += [question.name]
        elif answer == asking.ANSWER_IDENTIFIER:
            identifiers += [question.name]
            # The person question's `identifier`, "the people the rows are
            # about", says the person (lane EZ-a, plan P4-D479).
            if question.reason == asking.BECAUSE_REPEATS_AND_MANY:
                _person_said(question.name)
        elif answer == asking.ANSWER_JOINED or (
            answer == asking.ANSWER_MEASUREMENT and both
        ):
            # ...and `measurement` where it is offered beside `keep`: a
            # declaration, as the questions file reads it (plan P4-D438;
            # Codex's review of lane UN-1a, item 2).
            measurements += [question.name]
        elif answer == asking.ANSWER_DECIMAL_COMMA:
            commas += [question.name]
        elif answer == asking.ANSWER_TWELVE_HOUR:
            twelve += [question.name]
        elif answer == asking.ANSWER_CLOCK_FIGURES:
            # -- lane TR (P4-D473): rule 5c's reading.
            figures += [question.name]
        elif answer in date_counts.MEMBERS:
            counted += [(question.name, answer)]
    return codes, identifiers, measurements, commas, twelve, counted, left_open, figures


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
    answers_file: str = "",
) -> str:
    """The options that repeat this run without asking anything.

    ``answers_file`` is `--answers` and the questions file this run
    writes, already written as it is typed, where an answer stands that no
    option repeats (lane EZ-a, plan P4-D479; the walkthrough's item 15): a
    Safe Harbor answer, the unit of an age, a `keep`, the month first
    (`_a_kept_answer_stands`), and `clock-figures` (lane TR, plan P4-D473;
    the lane's skeptic 1, item 3), whose reading the command line does not
    declare (`--clock-figures` is no option). The file keeps them under
    `answered_before`, so handing it back repeats the description byte for
    byte; the options stand beside it, each the same answer typed. A column
    said to name the person is repeated as `--person`
    (`_Session.persons_said`). ONE parameter carries both lanes' answers
    (batch 4t's merge of lane EZ-a).

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
    said = _persons_repeated()
    for name in sorted(forced_identifiers):
        parts += [_typed_option("--person" if name in said else "--identifier", name)]
    for name in sorted(forced_measurements):
        parts += [_typed_option("--measurement", name)]
    # -- lanes TR (P4-D473) and EZ-a (P4-D479): the questions file, for the
    # answers no option repeats (`clock-figures`, and the answers
    # `_a_kept_answer_stands` names).
    if answers_file:
        parts += [answers_file]
    # ...and every typed declaration a newer answer replaced in an earlier
    # round of this command (lane EZ-a's second repair; Codex's item 1).
    taken_out = tuple(taken_out) + tuple(one for one in _typed_replaced_said() if one not in taken_out)
    flags = _joined(parts, " ")
    out = ""
    if answers_file:
        out = (
            "The questions file named after --answers keeps your answers "
            "that no option repeats.\n"
        )
    if taken_out:
        out = out + (
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


def _a_kept_answer_stands(
    harbored: "list[str]", kept: "list[str]", month_first: bool
) -> bool:
    """Whether an answer stands that no option repeats (lane EZ-a, plan P4-D479; the walkthrough's item 15).

    A Safe Harbor answer (`no`, `yes`, or the unit of an age), a `keep`
    (to a question offering `identifier`, to Q-UNIT, Q-COMMA or Q6) and
    the month first: `answered_before` keeps each, and no typed option
    says it. A fixed function of the three. Raises nothing.
    """
    return bool(harbored) or bool(kept) or month_first


# THE PERSON SAID (lane EZ-a, plan P4-D479; the walkthrough's item 2). The
# words a kept `identifier` answer carries in `answered_before` where its
# column was said to name the person, so the next round counts the people
# by it again; and the opening every such `identifier` answer's words share,
# the person question's own among them.
_PERSON_MEANS_OPENING = "the people the rows are about"
_PERSON_KEPT_MEANS = (
    "the people the rows are about: rows sharing a value of it are one "
    "person, and no value of the column is published"
)


def _person_said(name: str) -> None:
    """Record that ``name`` was said to name the person this run's rows are about."""
    session = _current()
    if session is not None and name not in session.persons_said:
        session.persons_said += [name]


def _person_kept(answer: str, question: "asking.Question") -> None:
    """Record a `keep` typed at the first prompt to the person question, which the questions file then keeps (`_persons_kept_at_the_prompt`).

    Lane EZ-a's second repair (the orchestrator's LANE EZ RULINGS 8 (5), the
    verify's MINOR 3; RULINGS 1 (7)): written in the questions file, `keep`
    is carried under `answered_before` and the question is not put again
    (pending item (a)); typed at the keyboard it was put again at every
    run, three runs measured. Now it is carried as the file route carries
    it, and the description is the one `keep` every round gives. Key 1
    there reads `measurement`, the standing reading's word, which shares the
    key with `keep` where the question does not offer `measurement`
    (`_KEY_OF`).
    """
    session = _current()
    offered = [choice.answer for choice in question.choices]
    kept = answer == asking.ANSWER_KEEP or (
        answer == asking.ANSWER_MEASUREMENT
        and asking.ANSWER_MEASUREMENT not in offered
        and asking.ANSWER_KEEP in offered
    )
    if (
        session is not None
        and kept
        and question.reason == asking.BECAUSE_REPEATS_AND_MANY
        and question.name not in session.persons_kept
    ):
        session.persons_kept += [question.name]


def _persons_kept_at_the_prompt(kept: "tuple[str, ...]") -> "tuple[str, ...]":
    """The person questions answered `keep` at the first prompt of this run and not among ``kept``, for `answered_before` to keep (`_person_kept`)."""
    session = _current()
    return tuple(name for name in (session.persons_kept if session is not None else []) if name not in kept)


def _persons_said_now() -> "list[str]":
    """The columns said to name the person in this run, as the session holds them."""
    session = _current()
    return [] if session is None else list(session.persons_said)


def _persons_given() -> bool:
    """Whether `--person` was typed: the person has said who the rows are about, and no notice says nobody did (lane EZ-a's repair)."""
    session = _current()
    return session is not None and bool(session.persons_typed)


def _persons_answered() -> bool:
    """Whether an answer, and not `--person` typed, said the column the people were counted by: the repeat line then says it."""
    session = _current()
    return session is not None and any(one not in session.persons_typed for one in session.persons_counted)


def _persons_repeated() -> "list[str]":
    """The columns the repeat line writes as `--person`: those typed so, and those said where saying changed the count."""
    session = _current()
    return [] if session is None else list(session.persons_typed) + list(session.persons_counted)


def _says_the_person(means: str) -> bool:
    """Whether an `identifier` answer's words say the column names the person (lane EZ-a, plan P4-D479).

    The unswitched person question's words (`_PERSON_MEANS_OPENING`) and,
    since every shipped run is switched (lane CHON, plan P4-D464; batch
    4u's merge), the switched one's (`asking.PERSON_ANSWER_MEANS`, lane
    GRa, RULINGS 1 (1)); `record`'s words say a record of the person and
    are neither. Raises nothing.
    """
    return (
        means[: len(_PERSON_MEANS_OPENING)] == _PERSON_MEANS_OPENING
        or means[: len(asking.PERSON_ANSWER_MEANS)] == asking.PERSON_ANSWER_MEANS
    )


def _persons_in_the_answers(document: "dict[str, object]") -> "list[str]":
    """The columns a questions file says name the person (lane EZ-a, plan P4-D479).

    An entry answered `identifier` -- or, kept under `answered_before`,
    standing on it -- whose `identifier` answer's words say the person
    (`_says_the_person`: the unswitched question's opening or the switched
    one's): the person question's answer, or an earlier run's kept one.
    Read by index, never by `.get` (plan D6.2). Raises nothing.
    """
    from synthtwin import contract

    found: "list[str]" = []
    for section, entry in contract.answer_entries(document):
        written = entry["your_answer"] if "your_answer" in entry else ""
        if section == "answered_before" and isinstance(written, str) and not parsing.trimmed(written):
            written = entry["read_as_now"] if "read_as_now" in entry else ""
        if not isinstance(written, str) or parsing.trimmed(written) != asking.ANSWER_IDENTIFIER:
            continue
        choices = entry["answers_you_can_give"] if "answers_you_can_give" in entry else []
        name = entry["column"] if "column" in entry else ""
        if not isinstance(choices, list) or not isinstance(name, str):
            continue
        for choice in choices:
            if (
                isinstance(choice, dict)
                and "answer" in choice
                and choice["answer"] == asking.ANSWER_IDENTIFIER
                and "means" in choice
                and isinstance(choice["means"], str)
                and _says_the_person(choice["means"])
                and name not in found
            ):
                found += [name]
    return found


def _persons_marked(kept: "list[dict[str, object]]") -> "list[dict[str, object]]":
    """The `answered_before` section, each kept `identifier` of a column said to name the person saying so.

    Lane EZ-a, plan P4-D479: the next round reads it back
    (`_persons_in_the_answers`) and counts the people by that column again.
    Written wherever a column was said (`_Session.persons_said`), whether
    or not saying changed this run's count: a later round can declare a
    second repeating record-number column (the checklist's `identifier`
    on a clinician number), and the people are then still counted by the
    column said. Written only where saying changed the count, the said
    column was lost there and the second round counted both columns
    together, refusing the table as 1 person (K-HZ-31's first run, on
    9678254b). Every other entry is the one `asking.answered_before`
    wrote. Raises nothing.
    """
    session = _current()
    said = list(session.persons_said) if session is not None else []
    if not said:
        return kept
    marked: "list[dict[str, object]]" = []
    for entry in kept:
        if entry["column"] not in said or entry["your_answer"] != asking.ANSWER_IDENTIFIER:
            marked += [entry]
            continue
        offered: "list[object]" = []
        choices = entry["answers_you_can_give"]
        for choice in choices if isinstance(choices, list) else []:
            if isinstance(choice, dict) and "answer" in choice and choice["answer"] == asking.ANSWER_IDENTIFIER:
                changed = {key: choice[key] for key in choice}
                changed["means"] = _PERSON_KEPT_MEANS
                offered += [changed]
            else:
                offered += [choice]
        again = {key: entry[key] for key in entry}
        again["answers_you_can_give"] = offered
        marked += [again]
    return marked


def _answers_loaded(answers_path: str) -> "dict[str, object]":
    """A questions file or a plain-text answers file, read, and the persons it says recorded (lane EZ-a, plan P4-D479).

    `contract.load_answers`, matched where the file is plain text against
    the questions file the run writes beside the table
    (`_Session.questions_beside`); the columns the file says name the
    person join the run's (`_persons_in_the_answers`).
    """
    from synthtwin import contract

    session = _current()
    beside = None
    if session is not None and session.questions_beside is not None:
        beside = _questions_beside(*session.questions_beside) or None
    document = contract.load_answers(answers_path, beside)
    for name in _persons_in_the_answers(document):
        _person_said(name)
    return document


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

    SINCE PLAN P4-D426 NO PERSON REACHES IT. The owner answered on
    2026-10-23 that the floor of 11 is a minimum: `--smallest-group`
    under 11 is refused, writing nothing, and `generate` and `validate`
    refuse a description recorded under 11. Such a description is made
    now only through `cli.main`'s internal keyword
    `internal_smallest_group`, for
    the suite and the measurement drivers, and this warning is kept byte
    for byte for them.

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
    table: object,
    settings: object,
    declared: "list[str]",
    codes: "list[str] | None" = None,
    measurements: "list[str] | None" = None,
    decimal_commas: "list[str] | None" = None,
    stored_as: "tuple[str, ...]" = (),
    join: "list[str] | None" = None,
) -> "tuple[tuple[str, ...], int, str, tuple[object, ...], int, int]":
    """The person columns, the population and the word it is counted in.

    The census is `profile.population_census_of`'s: a table read in
    groups of columns (lane SR, plan P4-D400) is counted one column at a
    time, never every declared column at once. ``join`` names the columns
    the people are counted by where they are not every declared identifier
    (lane EZ-a's second repair, Codex's item 4): the declarations that read
    the cells stay ``declared``.

    Returns (person columns, how many, the unit word, the readings the
    census took, the rows that hold a value -- which the table floor
    asks beside the people, plan P4-D425 -- and the people with each
    person's spellings merged, `parsing.subject_key`, which is the
    people count the table floor asks). The readings are handed to `profile.build_document`
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

    Guarantees: accepts the table, the settings in force and the
    columns declared with `--identifier`, `--code`, `--measurement` and
    `--decimal-comma`, and how a workbook stores each column
    (`profile.stored_as_of`, plan P4-D382), which the description is
    handed too; returns the six. A fixed function of them.
    Raises TypeError where the settings are not settings or the table
    not a table, which are internal invariants, and what
    `reading.column_values` raises. Opens
    no file for a table read whole, reads a table read in groups again
    one column at a time, and prints nothing.
    """
    from synthtwin import profile, reading, taxonomy

    if not isinstance(settings, taxonomy.Settings):
        raise TypeError("internal check: the settings are not settings")
    if not isinstance(table, reading.Table):
        raise TypeError("internal check: the table is not a table")
    people, counted, merged, rows, readings = profile.population_and_rows_census_of(
        table,
        settings,
        declared,
        codes if codes is not None else [],
        measurements if measurements is not None else [],
        decimal_commas if decimal_commas is not None else [],
        stored_as,
        join,
    )
    unit = taxonomy.NOTE_UNIT_ROWS
    if people:
        unit = taxonomy.NOTE_UNIT_PEOPLE
    return people, counted, unit, readings, rows, merged


def _below_the_table_floor(
    rows: int, person_columns: "tuple[str, ...]", people: int
) -> bool:
    """Whether `synthtwin profile` refuses the table at the owner's table floor.

    Plan P4-D425 (the owner, 2026-10-22: "we don't make twins of small
    tables"). Refused: fewer than `parsing.TABLE_ROW_FLOOR` rows that
    hold a value; or, where a declared or answered person column
    REPEATS (one person, several rows), fewer than
    `parsing.TABLE_PEOPLE_FLOOR` people. ``people`` is the count with
    each person's spellings merged (`parsing.subject_key`: `P00001` and
    `P-00001` are one person, as the description counts them; skeptic 1
    of lane POP, item 2). A column a question only OFFERS as a person
    column is not among ``person_columns`` until it is answered, so an
    open question never refuses a table.

    Guarantees: a fixed function of the three. Raises nothing.
    """
    if rows < parsing.TABLE_ROW_FLOOR:
        return True
    return bool(person_columns) and people < parsing.TABLE_PEOPLE_FLOOR


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


def _held_as_counted_dates(described_column: "dict[str, object]") -> bool:
    """Whether a column block is held as counted dates its cells did not read as (NF127).

    Asked of the block's EVIDENCE, never of its role (lane HX2's close
    verify, item 1): the count in people (NF126) makes a declared column
    that DID read as dates a record number too, and naming it as a
    declaration that did not reach told the person something false and a
    remedy that changes nothing. Raises nothing, opens no file.
    """
    from synthtwin import taxonomy

    if "detection_evidence" not in described_column:
        return False
    return f"{described_column['detection_evidence']}" == taxonomy.rendered(
        taxonomy.EVIDENCE_COUNTED_DATES_HELD, ()
    )


def _held_counted_dates(
    document: "dict[str, object]", counted: "dict[str, str]"
) -> "list[tuple[str, str]]":
    """Each column declared as counted dates that did not read so, with its system.

    Plan P4-D406 (contract NF127): such a column is held on every table,
    and the questions file names it beside the screen and the summary
    (the orchestrator's LANE HX2 ADDENDUM 2). Read back out of the FINAL
    document, as `_table_sentences` is, in the table's column order: a
    declared column whose block carries NF127's evidence
    (`_held_as_counted_dates`). Raises nothing, opens no file.
    """
    held: "list[tuple[str, str]]" = []
    for described_column in _described_columns(document):
        name = f"{described_column['name']}"
        if name not in counted:
            continue
        if not _held_as_counted_dates(described_column):
            continue
        held += [(name, counted[name])]
    return held


def _counted_in_rows_notice(names: "list[str]", small_tables_refused: bool = False) -> str:
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

    AND WHERE THE TABLE FLOOR APPLIES IT SAYS WHEN ITS PEOPLE HALF
    STARTS TO (plan P4-D425): an open question never refuses a table,
    and the people floor applies once the column is answered as one
    that names people.

    Guarantees: accepts the columns asked about and whether the table
    floor is on; returns one paragraph. A fixed function of the two;
    the names are the table's own column names and are published in
    the description like every other. Raises nothing, opens no file.
    """
    floor_said = f" {_people_floor_said()}" if small_tables_refused else ""
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
        f"population will be counted in people.{floor_said}"
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


def _made_up_held_said(
    names: "tuple[str, ...]",
    as_record_numbers: "tuple[str, ...]" = (),
    unmade: "tuple[str, ...]" = (),
) -> str:
    """Why the columns `profile.made_up_spellings_named` named are written apart from their values, in plain words (plan P4-D489).

    One to three sentences for the screen and the questions file alike,
    naming the columns (the table's own names, published in the
    description like every other) and no value: those spelled one letter
    or figure longer (method G10.5 step 8), those held as record numbers
    because even such spellings would meet a value (``as_record_numbers``),
    and those held as record numbers because no spellings of their width
    can be made (``unmade``; Codex's review of lane ID-ROOM4, item 1).
    Raises nothing.
    """
    longer = [name for name in names if name not in as_record_numbers]
    held = [name for name in names if name in as_record_numbers and name not in unmade]
    cannot = [name for name in names if name in unmade]
    said: "list[str]" = []
    if longer:
        said += [
            f"{_joined(longer, ' and ')} hold numbers too large or too small "
            f"for this file format to hold, and synthtwin's own made-up "
            f"spellings for such numbers would be written like some of their "
            f"values, so whatever the answer the twin spells each of their "
            f"cells one letter or figure longer than their longest value, "
            f"keeping how many different values they hold, how often each "
            f"repeats, their signs and their kind of number, and none of "
            f"their values is published."
        ]
    if held:
        said += [
            f"{_joined(held, ' and ')} hold numbers too large or too small for "
            f"this file format to hold, and even made-up spellings one letter "
            f"or figure longer would be written like some of their values, so "
            f"whatever the answer they are described as record numbers, none "
            f"of their values is published, and the twin writes made-up "
            f"record numbers there that no value of theirs equals."
        ]
    if cannot:
        said += [
            f"{_joined(cannot, ' and ')} hold numbers too large or too small for "
            f"this file format to hold, and synthtwin cannot make up spellings "
            f"of their width for such numbers, so whatever the answer they are "
            f"described as record numbers, none of their values is published, "
            f"and the twin writes made-up record numbers there that no value of "
            f"theirs equals."
        ]
    text = ""
    for sentence in said:
        text = f"{text} {sentence}" if text else sentence
    return text


def _made_up_held_notice(
    names: "tuple[str, ...]",
    as_record_numbers: "tuple[str, ...]" = (),
    unmade: "tuple[str, ...]" = (),
) -> str:
    """What the screen says of the columns written apart because their made-up spellings would be real values or cannot be made (plan P4-D489)."""
    return (
        "\nCOLUMNS WRITTEN APART FROM THEIR OWN VALUES WHATEVER THE ANSWER\n"
        f"{_made_up_held_said(names, as_record_numbers, unmade)}"
    )


def _made_up_spellings_held(
    read: object,
    document: "dict[str, object]",
    settings: object,
    subjects: "list[str]",
) -> "tuple[tuple[str, ...], tuple[str, ...]]":
    """The columns whose made-up spellings name a value 1 to f-1 hold, by the writer's own function, and among them those whose spellings cannot be made (plan P4-D489).

    Each text `profile.made_up_dry_runs` hands over is read as `synthtwin
    generate` reads a description (`contract.checked_description`), and
    the writer's own spelling function gives each place's spellings
    (`generation.made_up_spellings`, the one source the writer calls:
    RULING D1); `profile.made_up_spellings_named` reads them against the
    real cells, counted in ``subjects``, and a block already spelled
    wider (NF139) against every real value (Codex's review of lane
    ID-ROOM4, item 5). A declared column whose reading with no
    declaration no description could carry is named whatever (HIPAA
    first: no dry run, so it is held). A DRY RUN THAT CANNOT MAKE THE
    SPELLINGS is named too, and returned second: such a column is held
    whole as record numbers (Codex's review, item 1; the orchestrator's
    LANE ID-ROOM4 RULINGS 6 (4)), never accepted with no spellings read.
    The generator is loaded here, in the profile command's own path, and
    only where a block of the role is read: the validator's modules never
    reach it. Guarantees: both in the table's column order, the second
    inside the first. Raises TypeError where the settings are not
    settings or the table not a table, which are internal invariants. No
    I/O.
    """
    from synthtwin import contract, profile, reading, taxonomy

    if not isinstance(settings, taxonomy.Settings):
        raise TypeError("internal check: the settings are not settings")
    if not isinstance(read, reading.Table):
        raise TypeError("internal check: the table is not a table")
    runs = profile.made_up_dry_runs(read, document, settings)
    if not runs:
        return (), ()
    from synthtwin import generation

    spelled: "dict[int, tuple[str, ...]]" = {}
    wider: "list[int]" = []
    anyway: "list[str]" = []
    unmade: "list[str]" = []
    for text, places in runs:
        try:
            typed = contract.checked_description(text)
        except errors.ProfileError:
            anyway += [f"{read.column_names[place]}" for place in places]
            continue
        for place in places:
            # ...a keyed value column's key blocks and pool included (batch
            # 4t's fix round, item 1): each is written by the same counters.
            made, spelled_wider = generation.made_up_spellings_keyed(typed, place)
            if made is None:
                unmade += [f"{read.column_names[place]}"]
                continue
            spelled[place] = made
            if (
                spelled_wider
                or typed.columns[place].detection_evidence == generation.SPELLED_WIDER_EVIDENCE
            ):
                wider += [place]
    named = profile.made_up_spellings_named(read, spelled, subjects, settings, tuple(wider))
    return (
        tuple(
            name
            for name in read.column_names
            if f"{name}" in named or f"{name}" in anyway or f"{name}" in unmade
        ),
        tuple(name for name in read.column_names if f"{name}" in unmade),
    )


def _safe_harbor_notice(names: "tuple[str, ...]", held: bool) -> str:
    """What the screen says of the columns the Safe Harbor question is put to.

    Plan P4-D427. ``held``: columns of numbers of four or five figures,
    as ZIP codes are written, or of ages that cannot be read as 90,
    held back whole; otherwise columns whose values above 89 are read as
    90. The sentence names the way back, which is
    answering the question in the questions file. Guarantees: a fixed
    function of the two. Raises nothing, opens no file.
    """
    if held:
        said = (
            f"{_joined(list(names), ' and ')} may hold ZIP codes (whole "
            f"numbers of four or five figures) or ages over 89, so this "
            f"description publishes none of their values and the twin writes "
            f"made-up record numbers there"
        )
    else:
        said = (
            f"{_joined(list(names), ' and ')} may hold ages, and an age over "
            f"89 is part of a birth date, so this description reads every "
            f"value above 89 as 90 (\"90 or more\") and the twin writes none "
            f"above 90"
        )
    return (
        f"\nTHE SAFE HARBOR QUESTION\n"
        f"{said}. Answer 'no' or 'yes' to the question about them in the "
        f"questions file, and run the command again with --answers."
    )


# The age a year of birth must show to be pooled (plan P4-D434): the
# Safe Harbor top-code's own 90.
_AGE_SHOWN = 90


def _safe_harbor_years_notice(names: "tuple[str, ...]", cutoff: int) -> str:
    """What the screen says of the columns whose years of birth were pooled (plan P4-D434)."""
    return (
        f"\nTHE SAFE HARBOR QUESTION\n"
        f"{_joined(list(names), ' and ')} may hold years of birth, and a year "
        f"that shows an age over 89 is part of a birth date, so this "
        f"description reads every year up to {cutoff} as {cutoff} (\"{cutoff} "
        f"or earlier\") and the twin writes none before it. Answer 'no' or "
        f"'yes' to the question about them in the questions file, and run the "
        f"command again with --answers."
    )


def _safe_harbor_held_notice(names: "tuple[str, ...]") -> str:
    """What the screen says of the columns lane SH2 holds whole (plan P4-D434)."""
    return (
        f"\nTHE SAFE HARBOR QUESTION\n"
        f"{_joined(list(names), ' and ')} may hold a person's name, a year or "
        f"date of birth that shows an age over 89, a place smaller than a "
        f"state, a ZIP code or a device number, so this description publishes "
        f"none of their "
        f"values and the twin writes made-up values there. Answer 'no' or "
        f"'yes' to the question about them in the questions file, and run the "
        f"command again with --answers."
    )


def _counted_in_people_notice(names: "tuple[str, ...]", floor: int) -> str:
    """What the screen says of the columns whose values were counted in people.

    Plan P4-D406. On a table of several rows a person, a value fewer
    than the smallest group size of PEOPLE hold is not published however
    many rows hold it: its column is described as record numbers, and the
    twin writes made-up values in the column's layouts.

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
        f"published however many rows hold it, so these columns are "
        f"described as record numbers and the twin writes made-up values "
        f"there. No answer gives such a value back."
    )


def _dates_held_in_rows_notice(names: "tuple[str, ...]", floor: int) -> str:
    """What the screen says of the columns of dates the count in rows held (plan P4-D433).

    On a table of one row a person, or with no person column, or whose
    person column names fewer people than the smallest group size, each
    row is counted as its own: a column of dates one of whose dates falls on
    fewer than the smallest group size of rows, at every grain from the
    day to the year, is described as record numbers, and the twin writes
    made-up dates in the column's own layouts.

    Guarantees: accepts the columns and the floor; returns one paragraph.
    A fixed function of the names, which are the table's own column names
    and are published in the description like every other. Raises
    nothing, opens no file.
    """
    return (
        f"\nDATES HELD BY FEWER THAN {floor} ROWS\n"
        f"No column of this table that names a person on several rows names "
        f"{floor} people or more, so each row of "
        f"{_joined(list(names), ' and ')} was counted as its own: "
        f"a date fewer than {floor} rows fall on is not published, at the "
        f"day, the month, the quarter or the year, so these columns are "
        f"described as record numbers and the twin writes made-up dates "
        f"there, in each column's own layouts."
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


@dataclasses.dataclass(frozen=True)
class ChainRun:
    """The chain's switch for one `synthtwin profile` run (lane CHa, plan P4-D418; IN FORCE since plan P4-D464).

    THE SWITCH IS ON (lane CHON, plan P4-D464, the landing that ships
    stage 6): `main` and `run`, given none, make one for every `profile`
    run from the command line's own options (`_shipped_chain`: `--name`,
    `--replace-description`, `--new-key`, `--private-folder`, the rule
    steps on); the tools and the tests may hand one in. Only the internal
    keyword `unswitched`, which no option or environment variable sets,
    runs a command without it, as every run was before that landing.
    `name` is the table's name (4.6b.4's `--name`; None reads the input
    file's name without its extension); `folder` the installation's data
    folder (None: the platform's own, `installation.data_folder`);
    `replace_description` and `new_key` are 4.6b.4's
    `--replace-description` and `--new-key`. `private_folder` is where the
    PRIVATE report goes (lane ST, plan P4-D458; contract 4.6b.8): None
    reads the `private-reports` folder inside the installation's data
    folder, where the key file lives; a folder that holds the description
    or a twin, or lies inside the description's folder, is refused.
    """

    name: "str | None" = None
    folder: "str | None" = None
    replace_description: bool = False
    new_key: bool = False
    # THE SUBJECT QUESTION ANSWERED IN ADVANCE (lane GRa, plan P4-D449):
    # `asking.ANSWER_ONE_ROW_EACH` or `asking.ANSWER_NO_PERSON_COLUMN`, as a
    # handed-back questions file would answer it (an answer in that file
    # stands over this one); empty, the question is put and holds the
    # chain until it is answered.
    rows_per_person: str = ""
    # The rule steps (contract 4.6b.7; lane RO, plan P4-D459), off unless
    # asked; the shipped run asks (`_shipped_chain`, LANE RO RULINGS 2 (4)).
    rules: bool = False
    private_folder: "str | None" = None
    # THE PATIENT LAYER'S SUB-SWITCH (LANE CHON RULINGS 1 (6)): a run that
    # leaves it True may publish `grain`, the patient layer (lane GRa, plan
    # P4-D449); the shipped run reads `_PATIENT_LAYER_SHIPPED`, False until
    # the generator reads the layer (lane GRb flips it in one line), so a
    # table of several rows a person publishes no chain until then.
    patient_layer: bool = True


# THE ONE LINE LANE GRb FLIPS (LANE CHON RULINGS 1 (6)): whether the shipped
# command publishes the patient layer (`grain`). False: no shipped
# description carries what the shipped generator does not yet read.
_PATIENT_LAYER_SHIPPED = False


@dataclasses.dataclass
class _ChainState:
    """One switched run's installation, opened before the table is read, and its pending entry."""

    run: ChainRun
    # `installation.Opened` and `installation.Entry`: the installation (its
    # key comes from `secrets`) is imported only behind the chain's switch,
    # never by a run of the internal unswitched setting (Codex's item 10 on
    # repair 1); every shipped run is switched since plan P4-D464.
    opened: "typing.Any"
    entry: "typing.Any" = None
    statistical: "dict[str, object] | None" = None
    notes: "tuple[str, ...]" = ()
    # The pairs the handed-back questions file asks to add and to drop,
    # and the requests it could not read (`asking.between_columns_requests`).
    add: "tuple[tuple[str, str], ...]" = ()
    drop: "tuple[tuple[str, str], ...]" = ()
    unread: "tuple[str, ...]" = ()
    # The caution's words where the moments' fail-safe left them out (''
    # where it did not): the summary file closes on them too (LANE MPp
    # RULINGS 7 (3), verify 2's C2).
    moments_left_out: str = ""
    # THE SUBJECT QUESTION'S ANSWER (lane GRa, plan P4-D449), as the
    # handed-back file wrote it, and the column it names, if any.
    rows_answer: str = ""
    person_named: str = ""
    # Whether this run put the subject question (nothing says who the rows
    # are about), the repeating keys it names, and what it decided.
    subject_put: bool = False
    subject_keys: "tuple[str, ...]" = ()
    rows_per_person: str = ""
    # THE PERSON QUESTION'S TWO READINGS (RULINGS 1 (1)): the columns said to
    # identify the person, and a record of the person, kept across rounds.
    persons_said: "tuple[str, ...]" = ()
    records_said: "tuple[str, ...]" = ()
    # What the PRIVATE report reads (lane ST, plan P4-D458): the table's
    # name, the self-test's inputs (`chain.SelftestInputs`, never
    # published), the chain's counters and the published patient layer.
    name: str = ""
    selftest: "typing.Any" = None
    counts: "dict[str, int]" = dataclasses.field(default_factory=dict)
    grain: "typing.Any" = None
    # The description's own readings, kept column by column for the chain
    # (`taxonomy.KeptSpellings`; lane CHs, plan P4-D462): filled by the
    # description and emptied by the chain.
    kept: "dict[int, typing.Any]" = dataclasses.field(default_factory=dict)
    # THE QUESTION A HOLD WAITS FOR (lane CHON, plan P4-D464): `subject`
    # where the subject question holds the chain, `person` where the open
    # person question holds a repeating column first, '' where no hold
    # keeps the chain back; the screen's one paragraph names it
    # (`_hold_paragraph`).
    waiting: str = ""
    # WHAT THE RUN LEFT IN THE DATA FOLDER (lane CHON's repair 1, LANE CHON
    # RULINGS 5 (2)): whether its ledger entry was written, and whether its
    # description was. A run that reached the chain and wrote no
    # description takes its entry and the key it made back
    # (`installation.withdraw`), and the folder it made.
    recorded: bool = False
    described: bool = False
    # The columns the open person question holds, which the hold's paragraph
    # names (lane CHON's repair 1, F2).
    person_held: "tuple[str, ...]" = ()


def _subject_named(chain_state: "_ChainState | None") -> "list[str]":
    """The column the subject question's handed-back answer names, as a list of none or one (lane GRa, plan P4-D449)."""
    if chain_state is None or not chain_state.person_named:
        return []
    return [chain_state.person_named]


def _persons_settled(chain_state: _ChainState, repeating: "tuple[str, ...]") -> "tuple[str, ...]":
    """Who the rows of a switched run are about: its person columns among the repeating keys, and the subject question's state.

    Lane GRa, plan P4-D449, RULINGS 1 (1). A repeating key is the person
    only where an answer says so or its name, read whole, says so; other
    repeating keys beside it are records of the person. Until something
    says the person the hold stands, and an answer saying only records
    holds as no column naming the person. Returns the columns the run
    counts people by. Guarantees: a fixed function of its arguments and
    the state's answers; reads no cell; called on a switched run alone.
    """
    from synthtwin import chain

    chain_state.subject_keys = ()
    chain_state.subject_put = False
    if not chain_state.rows_answer and chain_state.run.rows_per_person in (
        asking.ANSWER_ONE_ROW_EACH, asking.ANSWER_NO_PERSON_COLUMN
    ):
        chain_state.rows_answer = chain_state.run.rows_per_person
    if not repeating:
        # Nothing repeats among the declared keys: the question stands alone.
        chain_state.subject_put = True
        if chain_state.rows_answer == asking.ANSWER_NO_PERSON_COLUMN:
            chain_state.rows_per_person = chain.ROWS_UNNAMED
        elif chain_state.rows_answer == asking.ANSWER_ONE_ROW_EACH:
            chain_state.rows_per_person = chain.ROWS_ONE
        else:
            # AN ANSWER NAMING A COLUMN IS NEVER READ AS `one row each`
            # (Codex's review of lane GRa, item 4): where the column it
            # names is no repeating key here, the answer is dropped and the
            # question put again; the column stays declared, and the hold
            # stands until the next answer.
            chain_state.rows_answer = ""
            chain_state.rows_per_person = chain.ROWS_OPEN
        return repeating
    said = tuple(name for name in repeating if name in chain_state.persons_said or name == chain_state.person_named)
    if said:
        chain_state.persons_said = tuple(sorted(set(chain_state.persons_said) | set(said)))
        chain_state.rows_per_person = chain.ROWS_PERSON
        return said
    if chain_state.rows_answer == asking.ANSWER_ONE_ROW_EACH:
        # An answer that contradicts a key answered to repeat: no chain.
        chain_state.subject_put = True
        chain_state.subject_keys = repeating
        chain_state.rows_per_person = chain.ROWS_ONE
        return repeating
    unread = tuple(name for name in repeating if name not in chain_state.records_said)
    if chain_state.rows_answer == asking.ANSWER_NO_PERSON_COLUMN or not unread:
        chain_state.subject_put = True
        chain_state.subject_keys = repeating
        chain_state.rows_per_person = chain.ROWS_UNNAMED
        return repeating
    by_name = tuple(name for name in unread if asking.names_a_person(name))
    if len(by_name) == 1:
        chain_state.rows_per_person = chain.ROWS_PERSON
        return by_name
    chain_state.subject_put = True
    chain_state.subject_keys = unread
    chain_state.rows_per_person = chain.ROWS_OPEN
    return repeating


def _population_settled(
    chain_state: "_ChainState | None",
    table: object,
    settings: object,
    declared: "list[str]",
    codes: "list[str] | None",
    measurements: "list[str] | None",
    decimal_commas: "list[str] | None",
    stored_as: "tuple[str, ...]",
) -> "tuple[tuple[str, ...], int, str, tuple[object, ...], int, int]":
    """`_population_of`, its count over the columns said to identify the person alone.

    On a switched run, as `_persons_settled` decides. ON AN UNSWITCHED RUN
    TOO (lane EZ-a, plan P4-D479; the orchestrator's LANE EZ RULINGS 1
    (2), R1: explicit only), where two or more declared record-number
    columns repeat: `_people_said_settled`. `--person` feeds the switched
    run's `persons_said` as well: one option, one meaning on both paths.

    ONE DECISION TABLE ON BOTH PATHS (lane EZ-a's second repair; the
    orchestrator's LANE EZ RULINGS 8 (2), Codex's items 4 and 5 of RULINGS
    7): where every column said to name the person is different on every
    row, `_said_counted` counts the table on the switched path as on the
    other -- in rows, or by a repeating key that could name the patients
    as well -- where `_persons_settled` saw only the keys that repeat and
    counted forty clinicians as the people of 20,000 patients. Every recount
    reads the cells under every declaration (``declared``) and counts the
    people by the chosen columns alone (`_population_of`'s ``join``).
    """
    from synthtwin import chain

    progress.stage("counting the people in the table")
    found = _population_of(table, settings, declared, codes, measurements, decimal_commas, stored_as)
    if chain_state is None:
        return _people_said_settled(found, table, settings, codes, measurements, decimal_commas, stored_as, declared)
    session = _current()
    if session is not None and session.persons_typed:
        chain_state.persons_said = tuple(sorted(set(chain_state.persons_said) | set(session.persons_typed)))
    said = _named_once(
        [name for name in declared if name in chain_state.persons_said or name == chain_state.person_named]
    )
    if said and not [name for name in said if name in found[0]]:
        counted, governing = _said_counted(
            found, table, settings, declared, codes, measurements, decimal_commas, stored_as, said
        )
        chain_state.persons_said = tuple(sorted(set(chain_state.persons_said) | set(said)))
        chain_state.subject_keys = ()
        chain_state.subject_put = False
        chain_state.rows_per_person = chain.ROWS_PERSON if governing else chain.ROWS_ONE
        return counted
    persons = _persons_settled(chain_state, found[0])
    if persons == found[0] and len(found[0]) >= 2 and chain_state.rows_per_person == chain.ROWS_OPEN:
        # NOTHING SAYS WHICH OF SEVERAL REPEATING KEYS NAMES THE PERSON, AND NO
        # NAME DOES EITHER (lane GRa's rule left the hold open): lane EZ-a's
        # explicit route, as on the unswitched path (LANE EZ RULINGS 1 (2) and
        # 8 (2)) -- the subject question at the keyboard, and where nobody is
        # there and the keys together read the table below the people floor
        # while one alone would not, the refusal that names the cause and
        # `--person`. Batch 4u's checks: since every shipped run is switched,
        # two repeating record numbers whose names say no person were refused
        # in the floor's own words, naming neither, and no question was put.
        settled = _people_said_settled(found, table, settings, codes, measurements, decimal_commas, stored_as, declared)
        chosen = [name for name in _persons_said_now() if name in found[0]]
        if settled is not found and chosen:
            chain_state.persons_said = tuple(sorted(set(chain_state.persons_said) | set(chosen)))
            _persons_settled(chain_state, found[0])
            return settled
        return found
    if persons == found[0]:
        return found
    return _population_of(table, settings, declared, codes, measurements, decimal_commas, stored_as, list(persons))


def _named_once(names: "list[str]") -> "list[str]":
    """The names in their order, each once."""
    found: "list[str]" = []
    for name in names:
        if name not in found:
            found += [name]
    return found


def _said_counted(
    found: "tuple[tuple[str, ...], int, str, tuple[object, ...], int, int]",
    table: object,
    settings: object,
    declared: "list[str]",
    codes: "list[str] | None",
    measurements: "list[str] | None",
    decimal_commas: "list[str] | None",
    stored_as: "tuple[str, ...]",
    said: "list[str]",
) -> "tuple[tuple[tuple[str, ...], int, str, tuple[object, ...], int, int], list[str]]":
    """The people of a run where ``said`` (declared columns, one or more) are said to name the person, and the repeating keys that govern beside them.

    THE DECISION TABLE (lane EZ-a's second repair; the orchestrator's LANE
    EZ RULINGS 8 (2)); ``found`` is the census of every declared identifier,
    whose first item names those that repeat:

    (a) the choice of the columns counted is apart from the declarations
        that read the cells (`_population_of`'s ``join``);
    (b) a said key that repeats counts its patients, and every other
        repeating key is held and joins nobody;
    (c) a said key that never repeats -- its values differ on every row --
        counts the table in rows, the rows being its people, and the screen
        says so in one line (`_rows_counted_said`);
    (d) where (c) holds and another declared record-number column repeats
        with as many different values as the people floor or more, so that
        it could name the patients, the floor of 11 is counted by both: the
        people are the rows joined by that column, the fewer holders of
        each group, as the held keys already are;
    (e) a repeating key with fewer different values than the people floor
        cannot name the patients and never governs: forty clinician numbers
        beside a patient key of 20,000 values leave the table counted in
        its 20,000 rows, not refused as forty people.

    Measured before (d) at 20,000 rows over 1,000 patients: `--person
    visit_id --identifier subject_id`, a visit key different on every row
    said to name the people, published levels 5 and 8 patients hold and
    said nothing; both keys named `--identifier` withheld them. Returns the
    census (``found`` itself where saying changes nothing) and the keys of
    (d). Reads each repeating key once (`profile.people_of_each_key`).
    """
    repeating = found[0]
    others = [name for name in repeating if name not in said]
    if [name for name in said if name in repeating]:
        if not others:
            return found, []
        return (
            _population_of(table, settings, declared, codes, measurements, decimal_commas, stored_as, list(said)),
            [],
        )
    if not others:
        return found, []
    counts = _people_of_each_key(table, settings, declared, others, codes, measurements, decimal_commas, stored_as)
    governing = [others[place] for place in range(len(others)) if counts[place] >= parsing.TABLE_PEOPLE_FLOOR]
    # Every repeating key was counted here, so none governing is rule (e)'s
    # shape: none has as many different values as the people floor.
    _rows_counted_said(said, others, governing, too_few=not governing)
    return (
        _population_of(
            table, settings, declared, codes, measurements, decimal_commas, stored_as, list(said) + governing
        ),
        governing,
    )


def _people_of_each_key(
    table: object,
    settings: object,
    declared: "list[str]",
    keys: "list[str]",
    codes: "list[str] | None",
    measurements: "list[str] | None",
    decimal_commas: "list[str] | None",
    stored_as: "tuple[str, ...]",
) -> "tuple[int, ...]":
    """`profile.people_of_each_key`: each key's own people, in one walk (Codex's item 6). Raises TypeError for a table or settings that are not one, internal invariants."""
    from synthtwin import profile, reading, taxonomy

    if not isinstance(settings, taxonomy.Settings):
        raise TypeError("internal check: the settings are not settings")
    if not isinstance(table, reading.Table):
        raise TypeError("internal check: the table is not a table")
    return profile.people_of_each_key(
        table, settings, declared, keys,
        codes if codes is not None else [],
        measurements if measurements is not None else [],
        decimal_commas if decimal_commas is not None else [],
        stored_as,
    )


def _rows_counted_said(
    said: "list[str]", others: "list[str]", governing: "list[str]", too_few: bool = False
) -> None:
    """The one line where every column said to name the person differs on every row and another key repeats (LANE EZ RULINGS 8 (2) (c), (3)).

    In the words the verify of lane EZ-a suggested: the said column counted
    each row as one person, which column repeats, and the command to run if
    that column names the patients; where the repeating column governs too
    (rule (d)), that the smallest groups were counted in its people as well.
    ``too_few`` is rule (e)'s shape, every repeating key counted and none
    with as many different values as the people floor (the verify 2's
    MINOR 3, LANE EZ RULINGS 9 (1)): such a key cannot name the patients,
    so the line says that and offers no command, and the README's own line
    is never answered with a hint that the wrong column was named.
    Shown once a run; a caution, never the verdict.
    """
    session = _current()
    typed = list(session.persons_typed) if session is not None else []
    names = _joined([_shown(one) for one in said], " and ")
    one = len(said) == 1
    instead_of = [f"--person {_shown(name)}" for name in said if name in typed]
    instead = f" in place of {_joined(instead_of, ' ')}" if instead_of else ""
    opening = (
        f"You said {names} {'names' if one else 'name'} the people. "
        f"{'Its' if one else 'Their'} values are different on every row, so "
    )
    if governing:
        named = _joined([_shown(name) for name in governing], " and ")
        text = (
            f"{opening}{'it counts' if one else 'they count'} each row as one person. {named} "
            f"{'repeats' if len(governing) == 1 else 'repeat'} with as many different values as "
            f"{parsing.TABLE_PEOPLE_FLOOR:,} people or more, so every count was also counted in "
            f"{'its' if len(governing) == 1 else 'their'} people, and the fewer holders govern: if "
            f"{_shown(governing[0]) if len(governing) == 1 else 'one of them'} names the patients, "
            f"run the command again with --person "
            f"{_shown(governing[0]) if len(governing) == 1 else 'and that column'}{instead}."
        )
    elif too_few:
        single = len(others) == 1
        text = (
            f"{_joined([_shown(name) for name in others], ' and ')} {'repeats' if single else 'repeat'} "
            f"with fewer than {parsing.TABLE_PEOPLE_FLOOR:,} different values, so "
            f"{'it' if single else 'they'} cannot name the patients: each row was counted as one person."
        )
    elif len(others) == 1:
        text = (
            f"{opening}each row was counted as one person. {_shown(others[0])} repeats: if it "
            f"names the patients, run the command again with --person {_shown(others[0])}{instead}."
        )
    else:
        text = (
            f"{opening}each row was counted as one person. "
            f"{_joined([_shown(name) for name in others], ' and ')} repeat: if one of them names the "
            f"patients, run the command again with --person and that column{instead}."
        )
    if session is not None:
        if text in [caution.words for caution in session.warnings]:
            return
        session.rows_said = text
    _warn(text, caution=results.CAUTION_COUNTED_IN_ROWS)


def _rows_counted_beside(asked: "list[str]", person_columns: "tuple[str, ...]") -> None:
    """The same line where the column put the person question repeats beside a said column that counted the table in rows (LANE EZ RULINGS 8 (3)).

    The base's notice that no column names people is not shown where a
    column was said (`_persons_given`); this line takes its place there.
    """
    if not asked or person_columns:
        return
    said = [name for name in _persons_said_now() if name not in asked]
    if said:
        _rows_counted_said(said, list(asked), [])


def _people_said_settled(
    found: "tuple[tuple[str, ...], int, str, tuple[object, ...], int, int]",
    table: object,
    settings: object,
    codes: "list[str] | None",
    measurements: "list[str] | None",
    decimal_commas: "list[str] | None",
    stored_as: "tuple[str, ...]",
    declared: "list[str] | None" = None,
) -> "tuple[tuple[str, ...], int, str, tuple[object, ...], int, int]":
    """An unswitched run's people, counted by the columns said to name them (lane EZ-a, plan P4-D479).

    THE WALKTHROUGH'S ITEM 2: `--identifier subject_id --identifier
    clinician_id` refused a table of 1,000 patients as one person, because
    several repeating declared identifiers are a UNION
    (`taxonomy.repeating_identifiers`), and a clinician number shared by
    patients joins them all. Where some declared column is SAID to name the
    person -- `--person`, the person question's `identifier` ("the people
    the rows are about"), here or in an earlier round
    (`_persons_in_the_answers`), or the subject question below -- the
    people are counted as `_said_counted`'s decision table says
    (LANE EZ RULINGS 8 (2)): `settings.person_columns` names the columns
    counted, and every other key stays among the declared identifiers,
    held, joining nobody. Where nothing says and two or more repeat:

    - somebody is at the keyboard: the subject question is put
      (`_subject_question`), Enter keeping the union as before; and from
      inside a later round's description (`_Session.subject_reader`) it is
      put at the keyboard as in the first round (LANE EZ RULINGS 4 (3));
    - nobody is, and the union reads the table as fewer people than the
      floor where one of those columns alone would not: the run is refused
      in words that name the cause and offer each column as a choice
      (`errors.people_counted_together`), never as "1 people"; a table
      small by every count keeps the floor's own message. The question
      whether one column alone would reach the floor is asked of every key
      in one walk (`profile.people_of_each_key`; Codex's item 6: a census
      of each key alone read k (k + 1) columns).

    THE STATED LIMITS (P4-D479): a person who names an encounter key with
    `--person` while no other declared key could name the patients counts
    encounters as people; a table about two kinds of person (a mother and a
    baby) is counted in the kind said, and both said means their union. The
    census of `taxonomy` is not touched: the columns counted are handed to
    it. Guarantees: returns `_population_of`'s six; raises a ProfileError
    for the refusal above; reads the table only through `_population_of`
    and `profile.people_of_each_key`.
    """
    session = _current()
    if session is not None:
        session.persons_counted = ()
    named = _named_once(list(declared or []))
    repeating = found[0]
    said = [name for name in named if name in _persons_said_now()]
    if not said and len(repeating) < 2:
        return found
    if not said:
        # ...put once for one set of keys: Enter there keeps the union, and
        # the census after the first round's answers does not ask it again.
        reader = session.subject_reader if session is not None else None
        if (_there_is_somebody_to_ask() or reader is not None) and (
            session is None or session.subject_put != repeating
        ):
            if session is not None:
                session.subject_put = repeating
            chosen = _subject_question_put(repeating, reader)
            if chosen is None:
                _at(results.STEP_QUESTIONS)
                if session is not None and reader is not None:
                    session.ended_at_subject = True
                raise errors.ProfileError(errors.the_questions_were_not_finished())
            if chosen:
                _person_said(chosen)
                said = [chosen]
    if said:
        counted, _governing = _said_counted(
            found, table, settings, named, codes, measurements, decimal_commas, stored_as, said
        )
        if counted is not found and session is not None:
            session.persons_counted = tuple(said)
        return counted
    rows, merged = found[4], found[5]
    if (
        session is not None
        and session.floor_refuses
        and rows >= parsing.TABLE_ROW_FLOOR
        and merged < parsing.TABLE_PEOPLE_FLOOR
    ):
        alone = _people_of_each_key(
            table, settings, named, list(repeating), codes, measurements, decimal_commas, stored_as
        )
        if [count for count in alone if count >= parsing.TABLE_PEOPLE_FLOOR]:
            raise errors.ProfileError(errors.people_counted_together(rows, merged, list(repeating)))
    return found


def _subject_question_put(
    repeating: "tuple[str, ...]",
    reader: "tuple[list[tuple[str, str]] | str | None, list[str | None] | str | None] | None",
) -> "str | None":
    """`_subject_question`, put with ``reader``'s screen and reader where a later round's description holds its own back.

    Lane EZ-a's repair (the orchestrator's LANE EZ RULINGS 4 (3) (a)): the
    real screen and reader stand in for that one question only, and the
    description's held screen and its 'nobody asked' come back after it,
    however it ends. ``reader`` None: the run's own, as in the first round.
    """
    session = _current()
    if reader is None or session is None:
        return _subject_question(repeating)
    held = (session.screen, session.ask)
    session.screen, session.ask = reader
    try:
        return _subject_question(repeating)
    finally:
        session.screen, session.ask = held


def _subject_question(repeating: "tuple[str, ...]") -> "str | None":
    """Ask at the keyboard which repeating column names the people the rows are about (lane EZ-a, plan P4-D479).

    The columns numbered from 1; a number or a column's name is the answer,
    Enter keeps counting them together as before (the empty text, as
    `tests/keyboard.py`'s reader gives, too), and the end of input is None.
    Every read goes through `_read_one_answer`. No value of the table is
    shown: the columns' names, which the person typed.
    """
    lines = ""
    keys: "list[tuple[str, str]]" = []
    place = 0
    for name in repeating:
        place = place + 1
        keys += [(f"{place}", name)]
        lines = lines + f"\n      [{place}] {_shown(name)}"
    _say(
        f"\n{'=' * 66}\nWHO ARE THE ROWS ABOUT?\n{'=' * 66}\n"
        f"These columns hold record numbers, and the values of each repeat on "
        f"several rows. Which of these columns names the patients the rows are "
        f"about? The people are then counted by it alone, and the other "
        f"columns are held as record numbers and join nobody.{lines}\n"
        f"    Press Enter to count rows sharing a value of any of them as one "
        f"person, as before."
    )
    session = _current()
    if session is not None:
        session.offered_now = tuple(keys)
    try:
        answer = _read_one_answer(_LEFT_OPEN)
    finally:
        if session is not None:
            session.offered_now = ()
    if answer is None:
        return None
    if answer in repeating:
        return answer
    return ""


def _chained_description(
    chain_state: _ChainState,
    table: pathlib.Path,
    read: "typing.Any",
    published: "dict[str, object]",
    settings: "typing.Any",
    held: "tuple[str, ...]",
    forced_codes: "list[str]",
    forced_measurements: "list[str]",
    forced_decimal_commas: "list[str]",
    storage: "tuple[str, ...]",
    held_by_person: "tuple[str, ...]" = (),
    safe_harbor_no: "tuple[str, ...]" = (),
    unanswered: "tuple[str, ...]" = (),
    rare_values_released: bool = True,
    harbor_year: int = 0,
    kept_identities: "tuple[str, ...]" = (),
    ages_counted_in: "dict[str, int] | None" = None,
) -> "dict[str, object]":
    """The description with its chain, the ledger's decision on it, and the one line on the screen.

    Sets `chain_state.entry` to the ledger entry this run will write
    before its description, or leaves it None where the ledger refuses
    the run (its words printed): the caller then writes nothing. The
    private notes stay in `chain_state.notes`; no line names the key.
    ``ages_counted_in`` is each age column answered with its unit and
    that unit's mark, as the description was told it (`_marks_answered`).
    """
    from synthtwin import chain, installation

    run = chain_state.run
    name = run.name if run.name is not None else table.stem
    chain_state.person_held = tuple(held_by_person)
    # THE KEY, MADE AS THE RUN REACHES THE CHAIN (4.6b.4 amended 2026-11-09;
    # LANE CHON RULINGS 1 (4)): the data folder, its lock and its key, where
    # the installation read before the table holds none yet. A refusal here
    # is 4.6b.4's, in its words, and nothing is written.
    reached = installation.with_key(chain_state.opened, run.new_key)
    if reached is not chain_state.opened:
        chain_state.opened = reached
        if reached.refusal:
            _warn(reached.refusal, step=results.STEP_ENVIRONMENT)
            return published
        for line in reached.lines:
            _say(line)
    # Lane BT3a's repair 2 (LANE BT3 RULINGS 6 (2)): the reader reads a
    # column's dates in disguise in the unit its age was answered in.
    answered: "list[tuple[str, int]]" = []
    if ages_counted_in is not None:
        for column in sorted(ages_counted_in):
            answered += [(column, ages_counted_in[column])]
    # THE SIZE GUARD (CHAIN-NEXT 2.2; LANE CHON RULINGS 1 (9) and 2; contract
    # 4.6b.13 amended 2026-11-10), read after the table and before the chain:
    # the whole run, the chain on, projected against its time and memory
    # (`chain.size_decision`). Where it fits, the whole chain, with every
    # partner if that fits too; else THE DEGRADED CHAIN over the columns
    # whose pairs carry the most dependence, the others named; and where not
    # even two columns fit, no chain: one line on the screen with the
    # projections (never a count of the table's), one private note, and no
    # shared byte saying why.
    written = published["columns"] if "columns" in published else None
    sized = chain.size_decision(
        read.n_rows, len(written) if isinstance(written, list) else 0, chain.candidates_at_most(published, held)
    )
    too_large = sized.degraded and sized.drawn == 0
    if too_large:
        chained = chain.guarded(read, chain.size_note(sized))
    else:
        # THE SUBJECT QUESTION'S HOLD (lane GRa, plan P4-D449; `_persons_settled`
        # read it as the people were counted): while it is open, or answered with
        # no column naming the person, no chain and no patient layer is drawn.
        chained = chain.describe(
            read,
            published,
            settings,
            chain.ChainSwitch(
                name,
                chain_state.opened.key,
                held,
                chain_state.add,
                chain_state.drop,
                chain_state.rows_per_person,
                held_by_person,
                safe_harbor_no,
                unanswered,
                rare_values_released,
                harbor_year,
                kept_identities,
                rules=run.rules,
                ages_counted_in=tuple(answered),
                patient_layer=run.patient_layer,
                columns_at_most=sized.drawn if sized.degraded else 0,
                every_partner=sized.every_partner,
            ),
            list(forced_codes),
            list(forced_measurements),
            list(forced_decimal_commas),
            storage,
            chain_state.kept,
        )
        # The size guard's projections, in the private report's notes.
        if chained.statistical is not None:
            aside = len(_set_aside_for_size(chained.statistical))
            guard_said = list(chain.guard_notes(sized, aside))
            # ...and where the columns the carried rules read took the
            # degraded chain past the guard's bound (LANE CHON RULINGS 5 (1)).
            held_ladder = chained.statistical["ladder"]
            drawn_now = len(held_ladder) if isinstance(held_ladder, list) else 0
            if sized.degraded and drawn_now > sized.drawn:
                seconds_now = chain.projected_seconds(
                    read.n_rows, len(written) if isinstance(written, list) else 0, drawn_now, False
                )
                guard_said += [chain.rules_past_the_guard_note(sized, drawn_now, seconds_now)]
            chained = dataclasses.replace(chained, notes=chained.notes + tuple(guard_said))
    chain_state.kept = {}
    # A table of fewer than two eligible columns draws no chain whatever the
    # answer, and a table with no repeating key decides nothing then; nor
    # does one whose repeating column the open person question holds, until
    # that question is answered: the subject question is not put. The hold
    # stands either way.
    if (
        chain_state.subject_put
        and not chain_state.rows_answer
        and not chain_state.subject_keys
        and (chain.too_few_columns(chained) or chain.person_question_holds(chained))
    ):
        chain_state.subject_put = False
    # THE HOLD THE SCREEN NAMES (plan P4-D464; LANE CHON RULINGS 1 (2), LANE
    # BT3 RULINGS 1 (6)): only the subject question stands between this table
    # and a chain, or the person question before it.
    if chained.statistical is None and chain.off_reason(chained) == chain.OFF_SUBJECT:
        chain_state.waiting = _WAITS_FOR_PERSON if chain.person_question_holds(chained) else _WAITS_FOR_SUBJECT
    relationships = published["relationships"]
    if not isinstance(relationships, dict):
        return published
    # Each column a carried rule computes is written as its computed block
    # (contract 4.6b.7; lane RO, plan P4-D459), and the chain beside it.
    with_chain: "dict[str, object]" = chain.with_rules(published, chained)
    block_written = with_chain["relationships"]
    block: "dict[str, object]" = block_written if isinstance(block_written, dict) else {}
    # THE PATIENT LAYER (lane GRa, plan P4-D449): `grain`, and every column
    # block as the layer publishes it, where it stands.
    if chained.grain is not None:
        block["grain"] = chained.grain
    if chained.columns is not None:
        with_chain["columns"] = chained.columns
    with_chain["relationships"] = block
    statistical = chained.statistical
    selftest = chained.selftest
    notes_kept = list(chained.notes)
    # THE COMMAND NEVER WRITES A DESCRIPTION ITS OWN LOADER REFUSES (lane
    # MPp, plan P4-D455, LANE MPp RULINGS 6 (1); lane CHON's repair 1, LANE
    # CHON RULINGS 5 (1)(c) and 6 (3)): the chain's check runs on every
    # description whose `statistical` stands. THE MOMENTS' FAIL-SAFE: where
    # it refuses the description with rule B's moments and passes it
    # without them, the moments are left out and the caution says why.
    # THE CHAIN'S FAIL-SAFE: where it refuses the chain even without them,
    # the description written is the PLAIN one the chain was handed -- its
    # columns as described, every computed column's block and the patient
    # layer's left out with the chain -- and one private note names the
    # refusal; never the refused chain.
    if isinstance(statistical, dict):
        refused = _loader_refusal(with_chain)
        if refused and statistical["moments"] is not None:
            bare: "dict[str, object]" = {}
            for key in statistical:
                bare[key] = statistical[key]
            bare["moments"] = None
            block["statistical"] = bare
            if _loader_refusal(with_chain):
                block["statistical"] = statistical
            else:
                statistical = bare
                chain_state.moments_left_out = (
                    "Between columns: the moments (means, spreads, correlations and shares) were left out of this "
                    f"description, because the loader that reads it refused them: {refused} The family tables stand."
                )
                _warn(chain_state.moments_left_out, caution=results.CAUTION_CHAIN)
                refused = ""
        if refused:
            with_chain = published
            relationships_plain = published["relationships"]
            block = relationships_plain if isinstance(relationships_plain, dict) else {}
            statistical = None
            selftest = None
            notes_kept += [chain.chain_refused_note(refused)]
    digest = installation.description_digest(with_chain)
    between = installation.publishes_between(with_chain)
    decision = installation.decide(
        chain_state.opened,
        name,
        chained.content,
        digest,
        between,
        run.replace_description,
    )
    chain_state.notes = tuple(notes_kept)
    chain_state.statistical = statistical
    chain_state.name = name
    chain_state.selftest = selftest
    chain_state.counts = chained.counts
    # The patient layer as the description WRITES it (`block`: contract
    # 4.6b.8's patient words read from `grain` as 4.6c.9 writes it), never
    # the description as it stood before the chain, whose `grain` is null
    # (batch 4q's merge of lane ST beside lane GRa's layer).
    chain_state.grain = block["grain"] if "grain" in block else None
    if decision.verdict == installation.REFUSE:
        # WHICH ROUND THIS IS (LANE CHON RULINGS 1 (2)): the run after one a
        # hold kept at null, the first to publish between columns, is told so
        # before the contract's own words, which give the remedy and why.
        if between and _after_a_held_round(chain_state.opened, name, chained.content):
            _warn(_AFTER_A_HELD_ROUND, step=results.STEP_CONTENT)
        _warn(decision.words, step=results.STEP_CONTENT)
        # ...and a later round at the keyboard keeps the answers given since
        # where these words ask for --replace-description (Codex's review of
        # batch 4u, item 7); the record itself is changed by neither.
        session = _current()
        if session is not None and decision.words == installation.words_changed(name):
            session.round_refused_by_record = True
        return with_chain
    if decision.verdict == installation.WARN:
        _warn(decision.words, caution=results.CAUTION_CHAIN)
    chain_state.entry = installation.Entry(
        name,
        chained.content,
        installation.fingerprint(chain_state.opened.key),
        digest,
        between,
    )
    # Under a hold the screen's one paragraph names the question at the end
    # of the run (`_hold_paragraph`), in place of this line; above the size
    # guard its own line takes this one's place, and below the degraded
    # chain's line follows it.
    if too_large:
        _say(_guard_line(sized))
    elif not chain_state.waiting:
        _say(_chain_line(statistical))
        if isinstance(statistical, dict) and _set_aside_for_size(statistical):
            _say(_degraded_line(sized, statistical))
    if chain_state.add or chain_state.drop or chain_state.unread:
        _say(_requests_line(chain_state.add, chain_state.drop, chain_state.unread, statistical))
    return with_chain


def _held_once_a_value(cells: "list[str]") -> "list[str]":
    """A column's cells, each different text one object: a list of pointers beside the column's different texts."""
    one: "dict[str, str]" = {}
    out: "list[str]" = []
    for cell in cells:
        if cell not in one:
            one[cell] = cell
        out += [one[cell]]
    return out


def _inside_trajectories(read: "typing.Any", document: "dict[str, object]", written: pathlib.Path) -> None:
    """The trajectories zone written into the description's inside record (lane IN-3, plan P4-D498); nothing where no record stands for it.

    The person column and the record-number columns are the description's
    settings; every column is read through `reading.column_values`. BOUND
    AS THE RELATIONS ZONE IS (Codex's review of batch 4w, item 14): the zone
    joins the record `_inside_record_written` wrote at this description's
    own place (`_inside_record_at`, its resolved path) for these very bytes
    (the digest and size of the description written), and is written
    nowhere else: two tables of one name and header never share a model,
    and the zone stands or falls with the relations zone of the same
    description (one moved, renamed or edited afterwards finds neither).
    Nothing is printed: the record's path and size are the only things a
    screen may say of it, and IN-10 owns those words.
    """
    from synthtwin import inside, inside_relations, inside_trajectories, reading

    settings_block = document["settings"] if "settings" in document else None
    if not isinstance(settings_block, dict):
        return
    persons = settings_block["person_columns"] if "person_columns" in settings_block else None
    forced = settings_block["forced_identifiers"] if "forced_identifiers" in settings_block else None
    if not isinstance(persons, list) or len(persons) != 1:
        return
    rows = document["n_rows"] if "n_rows" in document else None
    if not isinstance(rows, int) or isinstance(rows, bool):
        return
    # THE ZONE IS AN ADDITION: a table it cannot read, or a record it cannot write, leaves the description and the
    # run as they were (the twin is then made without it), never a run stopped.
    try:
        places = inside.default_places()
        target = _inside_record_at(written, places.private)
        data = pathlib.Path(f"{written}").read_bytes()
        bound: "dict[str, object]" = {"digest": inside_relations.digest_of(data), "bytes": len(data)}
        del data
        names = [f"{name}" for name in read.column_names]
        # ...and only where that record stands: no column is read for a zone that could be written nowhere.
        if inside.place_refusal(target, places) or not inside.carries_marker(target):
            return
        identifiers = tuple(f"{name}" for name in forced) if isinstance(forced, list) else ()
        # THE MEMORY (lane IN-8, plan P4-D502): each column is read once, in the
        # table's order, and held once a value (a list of pointers, eight bytes a
        # row, each different text one object), never as the reader's own cells;
        # a record-number column, which the zone never reads, is not held.
        columns: "dict[str, list[str]]" = {}
        for place in range(len(names)):
            if names[place] in identifiers and names[place] != f"{persons[0]}":
                continue
            columns[names[place]] = _held_once_a_value(reading.column_values(read, place))
        zone = inside_trajectories.zone_from_columns(columns, f"{persons[0]}", identifiers)
        columns = {}
        if zone is None:
            return
        inside_trajectories.write_zone(zone, "", rows, names, places, at=target, description=bound)
    except (ArithmeticError, IndexError, KeyError, OSError, TypeError, ValueError):
        return


def _inside_trajectories_for(description: str, names: "list[str]", rows: int) -> "dict[str, object] | None":
    """The trajectories zone of the inside record bound to this description (its place and its bytes, Codex's review of batch 4w, item 14), or None."""
    from synthtwin import inside, inside_relations, inside_trajectories

    try:
        places = inside.default_places()
        target = _inside_record_at(description, places.private)
        data = pathlib.Path(f"{description}").read_bytes()
    except (OSError, ValueError):
        return None
    bound: "dict[str, object]" = {"digest": inside_relations.digest_of(data), "bytes": len(data)}
    return inside_trajectories.zone_of_record("", names, rows, places, at=target, description=bound)


def _dates_drawn(record: "dict[str, object] | None", drawn: "list[str]") -> "tuple[dict[str, object] | None, list[str]]":
    """The dates zone of the record a twin was drawn from and the date columns it wrote in that twin (None and none where the twin's dates are the description's)."""
    zones = record["zones"] if record is not None and "zones" in record else None
    found = zones["dates"] if isinstance(zones, dict) and "dates" in zones else None
    order = found["order"] if isinstance(found, dict) and "order" in found else None
    if not isinstance(found, dict) or not isinstance(order, list):
        return None, []
    return found, [name for name in order if isinstance(name, str) and name in drawn]


# THE QUESTIONS A HOLD WAITS FOR (`_ChainState.waiting`).
_WAITS_FOR_SUBJECT = "subject"
_WAITS_FOR_PERSON = "person"

# THE SCREEN'S ONE PARAGRAPH WHILE A HOLD STANDS (plan P4-D464; contract
# 4.6b.4 as written, LANE CHON RULINGS 1 (2)): the question to answer and the
# file it is in, and, before anything is shared, that the answered run will
# be refused unless this description was never shared and
# `--replace-description` is given. No count, and no reason a pair or a
# column is out (RULE W3).
_HOLD_SUBJECT = (
    "Between columns: nothing is published for this table yet. One question "
    "decides it, whether one person may stand on more than one row of this "
    "table, and it is in ",
    " under between_columns.",
)
_HOLD_PERSON = (
    "Between columns: nothing is published for this table yet. A question about "
    "a column of record numbers that repeat comes first, whether it identifies "
    "the person or a record of the person, then the question under "
    "between_columns, whether one person may stand on more than one row; both "
    "are in ",
    ".",
)
_HOLD_LEDGER = (
    "Answer there and run the command again with that file handed back "
    "(--answers). Where that run publishes relationships between columns, this "
    "computer's record of earlier descriptions refuses it unless this "
    "description was never shared and you add --replace-description, so keep "
    "this description to yourself until then."
)
# ...NAMING THE COLUMNS THE OPEN PERSON QUESTION HOLDS and the answers that
# turn the chain on (lane CHON's repair 1, LANE CHON RULINGS 3 (1), F2): the
# questions file's own answers, `keep`, `identifier` and `record`.
_HOLD_PERSON_NAMED = (
    "Between columns: nothing is published for this table yet, and none can "
    "be until a question about a column of record numbers that repeat is "
    "answered: ",
    ". Answer keep where its values are codes or a measurement, identifier "
    "where rows sharing a value are one person, or record where they are one "
    "record of a person (an encounter, an order, an account); then answer the "
    "question under between_columns, whether one person may stand on more "
    "than one row. Both are in ",
    ".",
)
# ...AND THE ROUND AFTER ONE (LANE CHON RULINGS 1 (2)), told before 4.6b.4's
# own refusal, which gives the remedy and why.
_AFTER_A_HELD_ROUND = (
    "This run is the one after a question held the relationships between "
    "columns back: the earlier description of this table published none, and "
    "this one would be the first to publish them."
)


def _guard_line(sized: "typing.Any") -> str:
    """The screen's one line above even the degraded chain's budget (plan P4-D464): the projections in words, never a count of the table's."""
    from synthtwin import chain

    return (
        "\nBetween columns: no relationship between columns is published for this table. The run without "
        f"them is projected at about {chain.hours_of(sized.seconds_plain)} hours of computing already, and "
        f"relating even two columns would take it past the {chain.hours_of(chain.RUN_SECONDS_AT_MOST)} hours "
        "this version allows a whole run (relating them all, about "
        f"{chain.hours_of(sized.seconds_whole)}), so every column of the twin is carried on its own."
    )


def _set_aside_for_size(statistical: "dict[str, object]") -> "tuple[str, ...]":
    """The columns a switched description's `statistical` sets aside for size (`ineligible` as `size`), in order (plan P4-D464)."""
    from synthtwin import contract

    return contract.size_set_aside({"relationships": {"statistical": statistical}})


def _degraded_line(sized: "typing.Any", statistical: "dict[str, object]") -> str:
    """The screen's line under THE DEGRADED CHAIN (plan P4-D464): how many columns it relates and the projections; no count of the table's."""
    from synthtwin import chain

    ladder = statistical["ladder"]
    drawn = len(ladder) if isinstance(ladder, list) else 0
    aside = len(_set_aside_for_size(statistical))
    return (
        f"Between columns, for this table's size: the relationships are kept among the {drawn} columns whose "
        "pairs carry the most dependence, so that the whole run stays within the "
        f"{chain.hours_of(chain.RUN_SECONDS_AT_MOST)} hours of computing this version allows (about "
        f"{chain.hours_of(sized.seconds)} projected; relating every column, about "
        f"{chain.hours_of(sized.seconds_whole)}). The other {aside} columns are carried on their own; the "
        "description lists them as set aside for size, and the private report names them."
    )


def _after_a_held_round(opened: "typing.Any", name: str, content: str) -> bool:
    """Whether the ledger's entry of this table, under this name, published nothing between columns (`installation.Entry.between`)."""
    for entry in opened.entries:
        if entry.content == content and entry.name == name:
            return not entry.between
    return False


def _hold_paragraph(waiting: str, questions: str, columns: "tuple[str, ...]" = ()) -> str:
    """The screen's one paragraph while a hold stands: the question, its file, and the record's refusal to come.

    Where the open person question holds `columns` (lane CHON's repair 1,
    LANE CHON RULINGS 3 (1), F2: the chain cannot be drawn at all until it
    is answered), the paragraph names them and the answers that turn the
    chain on, in the questions file's own words: no count, and no reason a
    pair or a column is out (RULE W3).
    """
    if waiting == _WAITS_FOR_PERSON and columns:
        named = ""
        for column in columns:
            named += (", " if named else "") + _shown(column)
        return "\n" + _HOLD_PERSON_NAMED[0] + named + _HOLD_PERSON_NAMED[1] + questions + _HOLD_PERSON_NAMED[2] + " " + _HOLD_LEDGER
    head, tail = _HOLD_PERSON if waiting == _WAITS_FOR_PERSON else _HOLD_SUBJECT
    return "\n" + head + questions + tail + " " + _HOLD_LEDGER


def _private_folder_refusal(folder: pathlib.Path, profile_path: pathlib.Path, os_name: str) -> str:
    """Why the private report may not go in `folder` ('' where it may): beside or inside the description's folder, beside a twin, or open.

    `os_name` is `installation.system_name()`: on POSIX a folder that
    already stands is refused where any group or other bit is set. Every
    look at the folder here may raise `OSError` (a folder no one may read):
    the caller holds that inside the report's own handler.
    """
    here = pathlib.Path(f"{pathlib.Path(f'{folder}').resolve()}")
    described = pathlib.Path(os.path.dirname(f"{pathlib.Path(f'{profile_path}').resolve()}"))
    if here == described or described in here.parents:
        return (
            "The private report was not written: the folder named for it, "
            f"{_shown(str(folder))}, is the folder that holds the description or lies inside it, and the private "
            "report never travels beside the files that are shared. Name a private folder of your own, outside it."
        )
    if here.is_dir():
        for entry in here.iterdir():
            named = os.path.basename(f"{entry}")
            if named.endswith((_TWIN_SUFFIX, _WORKBOOK_TWIN_SUFFIX, _REPORT_SUFFIX, "-profile.json")):
                return (
                    "The private report was not written: the folder named for it, "
                    f"{_shown(str(folder))}, holds a description or a twin, and the private report never travels "
                    "beside the files that are shared. Name a private folder of your own."
                )
        # A folder that already stands is the person's own only where no
        # other account may read or change it (LANE ST RULINGS 3 (1)(a)),
        # as the installation asks of its own data folder.
        if os_name != "nt" and here.stat().st_mode & 0o077 != 0:
            return (
                "The private report was not written: the folder named for it, "
                f"{_shown(str(folder))}, can be read or changed by other accounts on this computer, and the "
                "private report holds what was measured on your own table. Make it yours alone (on macOS or "
                f"Linux: chmod 700 '{folder}'), or name another private folder of your own, then run again."
            )
    return ""


def _private_report_lands_on(
    names: "tuple[pathlib.Path, ...]", places: "tuple[tuple[pathlib.Path, str], ...]"
) -> "tuple[pathlib.Path, str] | None":
    """The first of `names` that resolves onto one of `places` (a file this run reads or writes), with its noun; None where none does.

    The samefile test the profile step uses for its own outputs
    (`writing.is_the_same_file`): a link, a second name of one file, or the
    file itself (Codex's item 1 of lane ST's review).
    """
    from synthtwin import writing

    for name in names:
        for place, noun in places:
            if name == place or writing.is_the_same_file(name, place):
                return name, noun
    return None


def _dates_not_carried(document: "dict[str, object]") -> "tuple[str, ...]":
    """The columns of a description written whose twin writes record numbers where the table holds dates, shown.

    F10's line of the private report names them (Codex's review of batch
    4q, item 3; `chain_grades.NOT_DATES`), read off the column blocks as
    written by the rule the twin's shared report reads off the loaded
    description (`generation.dates_written_as_record_numbers`): a block
    held as an identifier whose published `made_up_years` holds no run of
    a kind of year one of its date layouts, or its grain's reading,
    writes. A block of any other shape names nothing. Raises nothing.
    """
    from synthtwin import generation

    columns = document["columns"] if "columns" in document else None
    named: "list[str]" = []
    if not isinstance(columns, list):
        return ()
    for block in columns:
        if not isinstance(block, dict) or "role" not in block or block["role"] != "identifier":
            continue
        years = block["made_up_years"] if "made_up_years" in block else None
        grain = block["time_grain"] if "time_grain" in block else None
        # ...a block with a grain publishing none read too: its twin draws
        # from the room alone (lane ID-ROOM3, plan P4-D488).
        if not isinstance(years, list) and not isinstance(grain, dict):
            continue
        runs: "list[tuple[int, int]]" = []
        for run in years if isinstance(years, list) else []:
            if isinstance(run, list) and len(run) == 2 and isinstance(run[0], int) and isinstance(run[1], int):
                runs += [(run[0], run[1])]
        forms = block["layout_forms"] if "layout_forms" in block else None
        kind = grain["kind"] if isinstance(grain, dict) and "kind" in grain else None
        member = grain["reading"] if isinstance(grain, dict) and "reading" in grain else None
        if generation.dates_written_as_record_numbers(
            [f"{layout}" for layout in forms] if isinstance(forms, dict) else [],
            tuple(runs) if isinstance(years, list) else None,
            kind if isinstance(kind, str) else None,
            member if isinstance(member, str) else "",
        ):
            named += [parsing.visible(f"{block['name'] if 'name' in block else ''}")]
    return tuple(named)


def _private_report(
    chain_state: _ChainState,
    profile_path: pathlib.Path,
    floor: int,
    places: "tuple[tuple[pathlib.Path, str], ...]" = (),
    not_dates: "tuple[str, ...]" = (),
) -> None:
    """Write the PRIVATE report of a switched profile run (lane ST, plan P4-D458; contract 4.6b.8, in force since plan P4-D464).

    THE ONE SITE that imports the zone P self-test (the offline scanner's
    `_PRIVATE_IMPORT_SITES`): it runs after the ledger recorded the run and
    the description, its summary and the questions' inputs were written,
    and nothing it computes reaches them. The report holds both grades for
    every pair and analysis family, says which to act on and which twin to
    use, and names the key file's PATH, never the key. It goes in the
    private folder (`ChainRun.private_folder`), made with mode 0700, as a
    file of mode 0600, written whole and moved into place; a folder beside
    the description or a twin is refused in plain words and nothing is
    written.

    THE PERSON'S OWN FILES FIRST (LANE ST RULINGS 5 (1), Codex's items 1, 2
    and 8): the folder named is validated AS GIVEN by the locality gate
    (`validate_local_path`: a network form is refused on the string, before
    any filesystem call, and on Windows a link on its own metadata) before
    anything looks at it; every look at the folder (whether it stands, its
    mode, what it holds) sits inside the report's own handler, so a folder
    no one may read leaves the exit code, every shared byte and the
    questions file as they are, and says so; the report's file and its
    temporary name are refused where either resolves onto `places` (the
    table, the answers file, the description, its summary and the
    questions file this run reads or writes), before anything is written
    or removed; and the file's name keeps a digest of the table's exact
    name (`chain_selftest.report_stem`), so two names never share a report.
    """
    from synthtwin import chain_selftest, installation

    run = chain_state.run
    raw = (
        run.private_folder
        if run.private_folder is not None
        else str(pathlib.Path(chain_state.opened.folder, chain_selftest.FOLDER))
    )
    try:
        folder = validate_local_path(raw, purpose="private folder")
    except (ValueError, OSError, RuntimeError) as refused:
        # `PathValidationError` is a ValueError; a link that loops, or a part
        # that cannot be examined, is refused alike, and never moves the run.
        _warn(
            f"The private report was not written. {refused} The description is written; nothing of the "
            "self-test reaches it.",
            caution=results.CAUTION_CHAIN,
        )
        return
    try:
        refusal = _private_folder_refusal(folder, profile_path, installation.system_name())
    except (OSError, RuntimeError) as failed:
        _warn(
            "The private report was not written: the folder named for it, "
            f"{_shown(str(folder))}, could not be looked into ({_shown(str(failed))}). The description, its "
            "summary and the questions file are written as they would be without it; make that folder yours "
            "and readable, or name another private folder of your own, then run again.",
            caution=results.CAUTION_CHAIN,
        )
        return
    if refusal:
        _warn(refusal, caution=results.CAUTION_CHAIN)
        return
    statistical = chain_state.statistical
    words = statistical["words"] if isinstance(statistical, dict) and isinstance(statistical["words"], list) else []
    off = ""
    prefix = chain_selftest.OFF_PREFIX
    for note in chain_state.notes:
        # The prefix read at its own length (Codex's item 16: 23 figures).
        if note[: len(prefix)] == prefix:
            off = note[len(prefix) :]
    # A chain is published where `statistical` stands: the table layer's,
    # whose self-test inputs `describe` hands over, or the patient layer's
    # (lane GRa, plan P4-D449), which hands none. The self-test judges a
    # chain of one row a person, so a patient layer's families read not
    # judged with that reason, never as a table whose chain is off (batch
    # 4q's merge of lane ST).
    published = isinstance(statistical, dict)
    why = chain_selftest.PATIENT_LAYER if published and chain_state.selftest is None else off
    key_file = str(installation.key_path(chain_state.opened.folder))
    text = ""
    for stopped in (False, True):
        # The description, its summary and the questions' inputs are
        # written: a self-test that stops (a fit, a number, any fault of
        # its own below the system-exit family) leaves them and the exit
        # code as they are, and its report then reads every word not
        # judged, the self-test having stopped (LANE ST RULINGS 3 (1)(b)).
        try:
            judged = (
                chain_selftest.not_judged(chain_selftest.STOPPED, words)
                if stopped
                else chain_selftest.run(chain_state.selftest, words, floor, why)
            )
            text = chain_selftest.report_text(
                judged, words, chain_state.notes, chain_state.counts, chain_state.name, key_file, chain_state.grain,
                None if published else off, not_dates,
            )
            break
        except Exception:  # noqa: BLE001 -- zone P never decides the run's exit code
            continue
    if not text:
        _warn(
            "The private report was not written: the self-test stopped. The description is written; "
            "nothing of the self-test reaches it.",
            caution=results.CAUTION_CHAIN,
        )
        return
    stem = chain_selftest.report_stem(f"{chain_state.name}")
    target = pathlib.Path(folder, stem + "-" + chain_selftest.REPORT_FILE + "." + "txt")
    temporary = pathlib.Path(folder, stem + "-" + chain_selftest.REPORT_FILE + ".new")
    try:
        landing = _private_report_lands_on((target, temporary), places)
        if landing is not None:
            _warn(
                "The private report was not written: its file, "
                f"{_shown(str(landing[0]))}, is the {landing[1]} under another name, and synthtwin never "
                "writes over or removes a file this run reads or writes. Name another private folder of your "
                "own, then run again.",
                caution=results.CAUTION_CHAIN,
            )
            return
        folder.mkdir(mode=0o700, parents=True, exist_ok=True)
        if temporary.exists():
            temporary.unlink()
        temporary.touch(mode=0o600, exist_ok=False)
        temporary.write_text(text, encoding="utf-8", newline="\n")
        temporary.replace(target)
    except OSError as failed:
        _warn(
            f"The private report could not be written in {_shown(str(folder))} ({_shown(str(failed))}). The "
            "description is written; run the command again once that folder can be written, or name another "
            "private folder of your own.",
            caution=results.CAUTION_CHAIN,
        )
        return
    _wrote((results.FILE_PRIVATE_REPORT, target))
    _say(f"The private report, for you alone (keep it out of anything you share): {_shown(str(target))}")


# -- the inside record (lane IN-2, plan P4-D496) ------------------------------------------------------


def _inside_record_at(description: "str | pathlib.Path", private: pathlib.Path) -> pathlib.Path:
    """Where a description's inside record lies: the private folder, the description's own name and a digest of its place.

    The place is the description's resolved path, so two tables of one
    name described into two folders keep two records, and a description
    moved elsewhere finds none (its twin is then built from it alone).
    """
    from synthtwin import inside, inside_relations

    resolved = pathlib.Path(f"{pathlib.Path(f'{description}').resolve()}")
    tag = inside_relations.digest_of(bytes(f"{resolved}", "utf-8", "surrogatepass"))
    return pathlib.Path(f"{private}", f"{resolved.stem}-{tag[:12]}{inside.SUFFIX}")


# THE INSIDE RECORD'S SUB-SWITCH (batch 4w): the record is written and the twin drawn from it only where this is on.
# On the shipped route since lane IN-2b: the drawn twin keeps the description's written forms (each drawn column is
# written with the description's twin's own cells; a made-up date column holds a date where that twin does and its
# months where it can). A gate file sets it in place; the product reads no environment. The flip is a ruling.
_INSIDE_RECORD_SHIPPED = True


def _inside_record_switched_on() -> bool:
    """Whether the inside record is written and the twin drawn from it: the sub-switch alone (the product reads no
    environment; a gate file sets the switch in place)."""
    return _INSIDE_RECORD_SHIPPED


# THE KEYED ZONE'S OWN SUB-SWITCH (batch 4x, plan P4-D503): the keyed zone (lane IN-4, plan P4-D499) is merged behind
# it and it is OFF on the shipped route. The zone writes cells of its own over the drawn twin (it re-cuts the persons
# to the record's census of rows a person and rewrites its numbers, flags, pairs and later clocks), so the drawn
# twin's columns are no longer the description's twin's cells and validate misses published facts on a long keyed
# table; batch 4x's outside review also found a held identifier level and an age past 89 it could write. While it is
# off the record is written without the zone and a record holding one is drawn without it; a gate file sets it in
# place, and the product reads no environment. Turning it on waits for the IN-4 follow-up named in plan P4-D503.
_KEYED_ZONE_SHIPPED = False


def _keyed_zone_switched_on() -> bool:
    """Whether the inside record's keyed zone is written and drawn: its own sub-switch alone (read in place)."""
    return _KEYED_ZONE_SHIPPED


def _record_without_keyed_zone(record: "dict[str, object]") -> "dict[str, object]":
    """The record as the twin is drawn from it: its keyed zone left out while that zone's sub-switch is off (each
    other zone as it stands). Raises nothing; no I/O."""
    zones = record["zones"] if "zones" in record else None
    if _keyed_zone_switched_on() or not isinstance(zones, dict) or "keyed" not in zones:
        return record
    kept: "dict[str, object]" = {}
    for name in zones:
        if name != "keyed":
            kept[name] = zones[name]
    out: "dict[str, object]" = {}
    for key in record:
        out[key] = kept if key == "zones" else record[key]
    return out


def _inside_record_written(read: object, published: "dict[str, object]", written: pathlib.Path) -> None:
    """Write the inside record of a table just described (lane IN-2, plan P4-D496): its marginals and its relations.

    THE TWIN IS BUILT FROM IT. Once the description is written, the table
    still open is read a column at a time (`reading.column_values`) into
    the record IN-0 contracted (`inside.write_record`: the protected
    marker, mode 0600 in the private folder, the guard first): the
    marginals zone (`inside.column_entry`) and the relations zone
    (`inside_relations.fit_zone`, the fitted responses), bound to the
    description by the digest of its bytes. `synthtwin generate` of that
    description then draws the twin from it. Nothing of the record is
    shown: one line names its path and its size.

    Where the guard refuses the private folder, the record is not written
    and the twin is built from the description alone; the refusal is said
    as a caution, except where the folder is a temporary one (a test's or
    a throwaway installation), where nothing is said. Raises TypeError on
    an internal mismatch; what `reading.column_values` raises; nothing
    else (a refused write is said, never raised).
    """
    from synthtwin import inside, inside_holds, inside_missing, inside_relations, reading

    if not isinstance(read, reading.Table):
        raise TypeError("internal check: the table is not a table")
    if not _inside_record_switched_on():
        return
    places = inside.default_places()
    target = _inside_record_at(written, places.private)
    refusal = inside.place_refusal(target, places)
    if refusal:
        if not inside.in_temporary(target, places):
            _warn(
                f"{refusal} The twin will be built from the description alone, without the relations between "
                "columns the record would carry.",
                caution=results.CAUTION_CHAIN,
            )
        return
    rows = published["n_rows"] if "n_rows" in published else None
    if not isinstance(rows, int):
        return
    # THE TABLE FLOOR (lane IN-2b): the product twins no table under the owner's floor (`_below_the_table_floor`), so
    # the record is written for a table at or above it alone (its rows, and its people where a person column
    # repeats); a table under it, described under a test's internal switch, keeps the twin of its description.
    if rows < parsing.TABLE_ROW_FLOOR:
        return
    specs = inside_relations.specs_of(published)
    if len(specs) != len(read.column_names):
        return
    # THE PERSONS FIRST, where a person column repeats: a column held once a
    # person is described and fitted a person at a time.
    persons: "inside_relations.Persons | None" = None
    person = ""
    for place in range(len(specs)):
        if specs[place].why_kept == inside_relations.NAMES_THE_PERSON and not person:
            found_persons = inside_relations.persons_of(reading.column_values(read, place))
            if found_persons.repeats:
                persons, person = found_persons, specs[place].name
    if persons is not None and len(persons.rows_of) < parsing.TABLE_PEOPLE_FLOOR:
        return
    sample = inside_relations.sample_rows(rows, persons=persons)
    marginals: "dict[str, object]" = {}
    encoded: "list[inside_relations.Encoded]" = []
    names: "list[str]" = []
    # THE KEPT COLUMNS' EMPTINESS (lane IN-7, plan P4-D501), read in the same
    # pass: each kept column with empty and filled cells enough, for the
    # missing-values zone fitted on the relations zone's frames below.
    kept: "list[inside_missing.Kept]" = []
    blocks = published["columns"] if "columns" in published and isinstance(published["columns"], list) else []
    settings_block = published["settings"] if "settings" in published else None
    frames: "dict[str, inside_relations.Frame]" = {}
    owners: "list[int] | None" = None
    # ONE READING OF THE TABLE FOR THE RECORD'S MARGINALS, RELATIONS AND DATES
    # (lane IN-8, plan P4-D502): each column is asked for once, in the table's
    # order, so a table read in groups of columns is read once a group, and
    # handed to the marginals, the relations' sample, the missing-values zone
    # and the dates zone's census (`inside_dates.take_column`, which keeps a
    # date column's days and a label's words, never the table); it is let go
    # before the next. A census that stops leaves the dates out. Each date
    # column is read as the description reads it (`--day-first`, the answers,
    # `--date-count`), and no other column is read as dates.
    from synthtwin import inside_dates

    skipped = tuple(specs[place].name for place in range(len(specs))
                    if specs[place].why_kept in inside_relations.RECORD_NUMBERS)
    gathered: "inside_dates.Census | None" = inside_dates.census(person, _inside_date_readings(published), skipped,
                                                                 True)
    try:
        for place, name in enumerate(read.column_names):
            if specs[place].name != name:
                return
            names += [name]
            cells = reading.column_values(read, place)
            marginals[name] = inside.column_entry(cells, specs[place].why_kept in inside_relations.RECORD_NUMBERS)
            # THE HOLDS NARROWED (lane IN-7, plan P4-D501): a column the person
            # answered a measurement is modelled though the description holds it
            # as record numbers, and an ordinary label carries its real spellings
            # the readers let through; identifiers and Safe Harbor columns stay held.
            block = blocks[place] if place < len(blocks) else None
            spec = inside_holds.narrowed_spec(specs[place], block, settings_block, cells)
            spec = inside_holds.carried_spec(spec, block, cells)
            found = inside_relations.encode(spec, cells, sample, persons)
            if found is not None:
                encoded += [found]
            else:
                missing = inside_missing.kept_column(spec, block, cells, sample, persons)
                if missing is not None:
                    kept += [missing]
            if gathered is not None:
                try:
                    inside_dates.take_column(gathered, name, cells)
                except (ValueError, ArithmeticError, IndexError, KeyError, TypeError, MemoryError):
                    gathered = None
            del cells
        owners = [persons.person[row] for row in sample] if persons is not None else None
        zone = inside_relations.fit_zone(encoded, len(sample), rows, owners, person, frames)
    except (ValueError, ArithmeticError, IndexError, KeyError, TypeError):
        # The description is written: a fit that stops leaves it and the exit
        # code as they are, and the twin is built from the description alone.
        # No word of the fault is shown, for it may quote a cell.
        _warn(
            "The inside record was not written: its fit stopped, a mistake in synthtwin; please report it. The twin "
            "will be built from the description alone, without the relations between columns the record would carry.",
            caution=results.CAUTION_CHAIN,
        )
        return
    persons = None
    encoded = []
    # THE MISSING-VALUES ZONE (lane IN-7, plan P4-D501): each kept column's
    # emptiness fitted on every modelled column and the kept ones before it.
    # An addition: a fit that stops leaves the record without it, and the
    # kept columns' empty cells where the description's twin puts them.
    missing_zone: "dict[str, object] | None" = None
    if kept:
        try:
            missing_zone = inside_missing.fit_zone(
                kept, frames, inside_missing.once_of(zone), len(sample), rows, owners)
        except (ValueError, ArithmeticError, IndexError, KeyError, TypeError):
            missing_zone = None
    kept = []
    frames = {}
    # THE DATES ZONE (lane IN-5, plan P4-D497): beside the relations, a census
    # of each date column's weekday, clock and gaps, so the twin's dates keep
    # them with the day of the month made up. Taken a column at a time above
    # (lane IN-8), at every size: the census holds a date column's days and
    # seconds and a label's words, about 16 and 8 bytes a row, never the table.
    dates_zone: "dict[str, object] | None" = None
    if gathered is not None:
        try:
            built = inside_dates.zone_of(gathered)
            if built["order"]:
                dates_zone = built
        except (ValueError, ArithmeticError, IndexError, KeyError, TypeError, MemoryError):
            dates_zone = None
    gathered = None
    # THE KEYED ZONE (lane IN-4, plan P4-D499): where one person's rows are
    # typed by a key (an item, a test), each key level's rules inside a row,
    # marginals and trajectories. It reads the table's columns whole, so it is
    # built only for a table of at most `_KEYED_ZONE_MOST_ROWS` rows (the
    # bound both zones kept before lane IN-8 read the dates a column at a
    # time); a larger table's twin keeps the description's keyed values. It is
    # written only where its own sub-switch is on (`_keyed_zone_switched_on`,
    # off on the shipped route since batch 4x, plan P4-D503).
    keyed_zone: "dict[str, object] | None" = None
    if person and rows <= _KEYED_ZONE_MOST_ROWS and _keyed_zone_switched_on():
        whole: "dict[str, list[str]] | None" = None
        try:
            from synthtwin import inside_keyed

            whole = {name: [str(cell) for cell in reading.column_values(read, place)]
                     for place, name in enumerate(read.column_names)}
            dated = (tuple(str(each) for each in typing.cast("list[object]", dates_zone["order"]))
                     if dates_zone is not None else ())
            tops, held = inside_keyed.key_blocks_of(published)
            keyed_zone = inside_keyed.build_zone(whole, person, skipped + inside_keyed.kept_by_description(published),
                                                 dated, tops, held)
        except (ValueError, ArithmeticError, IndexError, KeyError, TypeError, MemoryError):
            keyed_zone = None
        whole = None
    data = pathlib.Path(f"{written}").read_bytes()
    record: "dict[str, object]" = {
        "format": inside.FORMAT,
        "version": inside.VERSION,
        "mode": inside.MODE,
        "table": {
            "rows": rows,
            "columns": names,
            "description": {"digest": inside_relations.digest_of(data), "bytes": len(data)},
        },
        "zones": {"marginals": marginals, inside_relations.ZONE: zone},
    }
    if dates_zone is not None:
        record["zones"]["dates"] = dates_zone  # type: ignore[index]
    if missing_zone is not None and inside_missing.carried(missing_zone):
        record["zones"][inside_missing.ZONE] = missing_zone  # type: ignore[index]
    if keyed_zone is not None:
        record["zones"]["keyed"] = keyed_zone  # type: ignore[index]
    try:
        made = inside.write_record(record, target, places)
    except (inside.InsideError, OSError) as failed:
        _warn(
            f"The inside record was not written ({_shown(str(failed))}). The twin will be built from the description "
            "alone, without the relations between columns the record would carry.",
            caution=results.CAUTION_CHAIN,
        )
        return
    _say(f"The {inside.describe(made.path)}. synthtwin generate builds the twin from it.")


def _inside_report_head(drawn: "list[str]") -> str:
    """The lines a twin drawn from the inside record opens its report with ('' for a twin built from the description alone).

    They say what the rest of the report cannot: which columns were drawn
    from the record, what those carry, and that the report's sentences on
    columns and rows built independently speak of the other columns only.
    No value and no count of the record is printed.
    """
    if not drawn:
        return ""
    named = _joined([parsing.visible(name) for name in drawn], ", ")
    return (
        "THIS TWIN WAS DRAWN FROM THE INSIDE RECORD, which stays on this computer.\n"
        f"These {len(drawn)} column(s) were drawn from it: {named}.\n"
        "A number or a label among them holds the description's own twin's cells for\n"
        "it, each row's cell chosen by its relations to the drawn columns before it\n"
        "(interactions, curves and steps at a class's cut points included), fitted on\n"
        "the real table inside; a date among them keeps the real weekday and clock\n"
        "with the day of the month made up. Every other column is the description's\n"
        "own twin's, made by every rule it keeps. Where the report below says columns\n"
        "or rows were built independently, it speaks of those other columns only.\n\n"
    )


# THE KEYED ZONE'S BOUND (lane IN-4, kept at the 4x merge): the zone reads the table's columns whole.
_KEYED_ZONE_MOST_ROWS = 250_000


def _inside_date_readings(published: "dict[str, object]") -> "dict[str, str]":
    """Each date column's reading as the description written establishes it, for the dates zone (lane IN-5).

    The member its block names (`format`: the reading `--day-first` and
    the person's answers settled), or the counting system the person
    declared (`--date-count`, the settings' `forced_date_counts`). A column
    whose century the person declared, or whose member the zone does not
    read (a month, a quarter, a layout), is not named: the twin keeps the
    description's dates there. Raises nothing; no I/O.
    """
    from synthtwin import date_counts, inside_dates

    settings = published["settings"] if "settings" in published else None
    counted: "dict[str, str]" = {}
    centuries: "set[str]" = set()
    if isinstance(settings, dict):
        pairs = settings["forced_date_counts"] if "forced_date_counts" in settings else None
        for pair in pairs if isinstance(pairs, list) else []:
            if isinstance(pair, list) and len(pair) == 2 and isinstance(pair[0], str) and isinstance(pair[1], str):
                counted[pair[0]] = pair[1]
        windows = settings["century_windows"] if "century_windows" in settings else None
        for pair in windows if isinstance(windows, list) else []:
            if isinstance(pair, list) and pair and isinstance(pair[0], str):
                centuries = centuries | {pair[0]}
    readings: "dict[str, str]" = {}
    columns = published["columns"] if "columns" in published else None
    for block in columns if isinstance(columns, list) else []:
        if not isinstance(block, dict) or "name" not in block or not isinstance(block["name"], str):
            continue
        name = block["name"]
        if name in centuries:
            continue
        if name in counted:
            if counted[name] in date_counts.MEMBERS:
                readings[name] = counted[name]
            continue
        shown = block["format"] if "format" in block else None
        if isinstance(shown, str) and shown in inside_dates.TEXT_MEMBERS:
            readings[name] = shown
    return readings


def _outcome_of_a_drawn_twin(description: str, measured: str, outcome: "typing.Any") -> "typing.Any":
    """A twin drawn from the inside record: the only obligations excused are the calendar counts of a date column the
    dates zone made up (4w integration, narrowed by lane IN-2b).

    Every column the relations zone draws is written with the description's
    twin's own cells (`inside_relations.redeal_number`, `redeal_label`), so
    no obligation of a number or a label is excused. A date column the dates
    zone made up keeps its weekday pattern and clock and makes up its day of
    the month (the owner's ruling of 2026-11-18), so its counts at the day's
    grain (its distinct days, a day-level ladder and tails, the heavy days,
    the day-of-month and weekday counts) cannot be the description's, nor
    the counts of its hours and minutes (stamps at midnight among them),
    kept by their shares; its months are held where they are published
    (`inside_dates._held_months`:
    exactly for a column heading its own chain, as near as whole persons and
    chains allow for a person's timeline or a chained date). Where the report
    beside the measured file opens with the inside record's head line and
    the record lies beside this description, a MISSED check of
    `_INSIDE_EXCUSED_DATE_FACTS` on such a column is an AUTHORIZED-DEVIATION
    that cites the record; no other verdict moves (the presence of every
    date, its written form and every other obligation stay strict), and a
    file with no such report is judged as it always was. A COLUMN THE DATES
    ZONE DID NOT WRITE IS NOT EXCUSED (batch 4x's outside review, item 11):
    the column must be in the record's dates zone AND named by the report's
    head among the columns drawn from the record (`_drawn_in_report`), so a
    zone the writer refused (another version) or a column it left as the
    description's twin's is judged strictly; a head whose list cannot be
    read without doubt excuses nothing.
    """
    from synthtwin import inside, inside_relations, validation

    # The twin's report lies beside the measured file under its stem: 'visits-twin.csv' -> 'visits-twin-report.txt'.
    named = pathlib.Path(f"{measured}")
    report = f"{pathlib.Path(f'{named.parent}', f'{named.stem}-report.txt')}"
    try:
        if not os.path.isfile(report):
            return outcome
        opening = pathlib.Path(report).read_text(encoding="utf-8", errors="replace")
        if opening[: len(_INSIDE_REPORT_HEAD)] != _INSIDE_REPORT_HEAD:
            return outcome
        drawn = _drawn_in_report(opening)
        target = _inside_record_at(description, inside.default_places().private)
        if not os.path.isfile(f"{target}"):
            return outcome
        record = inside.load_record(target)
        made_up: "set[str]" = set()
        for each in _dates_made_up(record["zones"]):
            if parsing.visible(each) in drawn:
                made_up = made_up | {each}
    except (inside.InsideError, inside_relations.RelationsError, OSError, KeyError, TypeError, ValueError):
        return outcome
    changed = [
        dataclasses.replace(check, verdict=validation.AUTHORIZED_DEVIATION, citation=_INSIDE_CITATION)
        if check.verdict == validation.MISSED and check.column in made_up and check.fact in _INSIDE_EXCUSED_DATE_FACTS
        else check
        for check in outcome.checks
    ]
    counted = {verdict: 0 for verdict in validation.VERDICTS}
    for check in changed:
        counted[check.verdict] += 1
    census = validation.Census(
        held=counted[validation.HELD], within_bound=counted[validation.WITHIN_BOUND],
        authorized_deviation=counted[validation.AUTHORIZED_DEVIATION], withheld=counted[validation.WITHHELD],
        missed=counted[validation.MISSED], not_checkable=outcome.census.not_checkable,
    )
    return dataclasses.replace(outcome, checks=tuple(changed), census=census)


def _drawn_in_report(opening: str) -> "set[str]":
    """The columns a drawn twin's report names as drawn from the inside record, as its head writes them (`_inside_report_head`'s
    second line: 'These N column(s) were drawn from it: a, b.'); none where that line is not there, or where its list
    does not split into exactly N names (a name holding the separator), so a doubtful head excuses nothing.

    Raises TypeError for anything but text; nothing else; no I/O.
    """
    if not isinstance(opening, str):
        raise TypeError("internal check: a twin's report is read as text")
    found: "set[str]" = set()
    first = opening.find("\n")
    if first < 0:
        return found
    rest = opening[first + 1:]
    end = rest.find("\n")
    if end < 0:
        return found
    line = rest[:end]
    lead = "These "
    marker = " column(s) were drawn from it: "
    if line[: len(lead)] != lead:
        return found
    middle = line.find(marker)
    if middle < 0:
        return found
    counted = line[len(lead):middle]
    listed = line[middle + len(marker):]
    if not counted.isdigit() or listed[len(listed) - 1:] != ".":
        return found
    pieces = listed[: len(listed) - 1].split(", ")
    if len(pieces) != int(counted):
        return found
    for piece in pieces:
        found = found | {piece}
    return found


def _dates_made_up(zones: object) -> "set[str]":
    """The date columns a record's dates zone made up (read by subscript and type checks alone)."""
    made_up: "set[str]" = set()
    if isinstance(zones, dict) and "dates" in zones:
        dates = zones["dates"]
        if isinstance(dates, dict) and "order" in dates:
            listed = dates["order"]
            if isinstance(listed, list):
                for each in listed:
                    if isinstance(each, str):
                        made_up = made_up | {each}
    return made_up


# THE ONLY OBLIGATIONS EXCUSED: the calendar and clock counts of a date column the dates zone made up -- its distinct
# days, its ladder and tails, its heavy days, its day-of-month and weekday counts, and the counts of its hours,
# minutes and seconds, stamps at midnight among them (the zone keeps the weekday and the clock by their shares, not
# by the description's counts over rows). Every other obligation (identifiers, held columns, ages past 89, numbers,
# labels, the file's written form and each date's spelling, the presence of every date, moments, the row and patient
# copies) stays as strict as before; the twin checks of the inside record stay the gate.
_INSIDE_EXCUSED_DATE_FACTS = frozenset({"datetime.date_percentiles", "datetime.low_tail.rows",
                                        "datetime.low_tail.boundary", "datetime.low_tail.values",
                                        "datetime.low_tail.mean_distance", "datetime.low_tail.rms_distance",
                                        "datetime.high_tail.rows", "datetime.high_tail.boundary",
                                        "datetime.high_tail.values", "datetime.high_tail.mean_distance",
                                        "datetime.high_tail.rms_distance", "datetime.day_of_month_census",
                                        "datetime.heavy_dates", "datetime.weekday_census", "datetime.n_distinct",
                                        "datetime.n_distinct_folded", "datetime.hour_census",
                                        "datetime.n_at_midnight", "datetime.minute_census", "datetime.minute_heaps",
                                        "datetime.second_census", "datetime.second_heaps"})
_INSIDE_REPORT_HEAD = "THIS TWIN WAS DRAWN FROM THE INSIDE RECORD"
_INSIDE_CITATION = ("the twin's date column was made up by the inside record's dates zone (weekday and clock kept, "
                    "the day of the month made up), so its counts at the day's grain are not the description's")


def _inside_record_for(description: str) -> "dict[str, object] | None":
    """The inside record a description's twin is built from (lane IN-2, plan P4-D496), or None where there is none.

    None, silently, where no record lies at the description's place in the
    private folder. Where one lies there but cannot be read, or was written
    beside another version of the description (its digest differs), the
    twin is built from the description alone and a caution says so,
    naming the record's path and size, never a value of it. A keyed zone
    the record holds is left out while that zone's own sub-switch is off
    (`_record_without_keyed_zone`, batch 4x).
    """
    from synthtwin import inside, inside_relations

    if not _inside_record_switched_on():
        return None
    places = inside.default_places()
    target = _inside_record_at(description, places.private)
    if not os.path.isfile(f"{target}"):
        return None
    try:
        record = inside.load_record(target)
        table = record["table"]
        bound = table["description"] if isinstance(table, dict) and "description" in table else None
        digest = bound["digest"] if isinstance(bound, dict) and "digest" in bound else None
        inside_relations.zone_of(record)
    except (inside.InsideError, inside_relations.RelationsError, OSError) as refused:
        _warn(
            f"{_shown(str(refused))} The twin is built from the description alone.",
            caution=results.CAUTION_CHAIN,
        )
        return None
    if digest != inside_relations.digest_of(pathlib.Path(description).read_bytes()):
        _warn(
            f"The {inside.describe(target)} was written beside another version of this description, so the twin "
            "is built from the description alone. Describe the table again to write the record anew.",
            caution=results.CAUTION_CHAIN,
        )
        return None
    # The keyed zone is drawn only where its own sub-switch is on (batch 4x, plan P4-D503).
    return _record_without_keyed_zone(record)


def _loader_refusal(document: "dict[str, object]") -> str:
    """The words of the loader's refusal of a description as it will be written ('' where it loads).

    The whole shipped reading (`contract.load_profile_text`: every check
    `synthtwin generate` and `validate` run on the file, the column blocks
    as well as the chain's S23 to S43) on the description's own serialized
    bytes, before anything is written (lane CHON's repair 1: a carried
    rule's computed block the chain check passed was refused by the
    loader's column rules, so the command wrote a description its own
    loader refused).
    """
    from synthtwin import contract, profile

    try:
        contract.load_profile_text(profile.serialize(document), "the description this run would write")
    except errors.ProfileError as refusal:
        return f"{refusal}"
    return ""


def _requests_line(
    add: "tuple[tuple[str, str], ...]",
    drop: "tuple[tuple[str, str], ...]",
    unread: "tuple[str, ...]",
    statistical: "dict[str, object] | None",
) -> str:
    """The line naming what the questions file asked of the chain and what this run did with it."""
    eligible: "set[str]" = set()
    ladder = statistical["ladder"] if isinstance(statistical, dict) else None
    if isinstance(ladder, list):
        for entry in ladder:
            if isinstance(entry, dict) and isinstance(entry["column"], str):
                eligible |= {entry["column"]}
    taken_add = [pair for pair in add if pair[0] != pair[1] and pair[0] in eligible and pair[1] in eligible]
    taken_drop = [pair for pair in drop if pair[0] != pair[1] and pair[0] in eligible and pair[1] in eligible]
    done: "list[str]" = []
    if taken_add:
        done += [f"{len(taken_add)} pair(s) to add were offered to the chain with more weight (never forced)"]
    if taken_drop:
        done += [f"{len(taken_drop)} pair(s) to drop share no family table"]
    others = [pair for pair in add + drop if pair not in taken_add and pair not in taken_drop]
    if others:
        left = ""
        for one, other in others:
            left += ("; " if left else "") + f"{one} and {other}"
        done += ["these name a column the chain does not hold and were left: " + left]
    if unread:
        unread_text = ""
        for one in unread:
            unread_text += ("; " if unread_text else "") + one
        done += ["these requests could not be read (a pair is two column names of this table): " + unread_text]
    if statistical is None:
        done += ["no family table is published for this table"]
    said = ""
    for one in done:
        said += ("; " if said else "") + one
    return "Between columns, from the questions file: " + said + ". The requests stay in the questions file."


def _chain_line(statistical: "dict[str, object] | None") -> str:
    """The one line on the screen about the chain: how many pairs share a family table."""
    if statistical is None:
        return (
            "\nBetween columns: no family table is published for this table; "
            "every pair of columns is carried as the twin's columns on their own."
        )
    words = statistical["words"]
    exact = 0
    total = 0
    if isinstance(words, list):
        for entry in words:
            if isinstance(entry, dict) and "word" in entry:
                total += 1
                if entry["word"] == "exact":
                    exact += 1
    return (
        f"\nBetween columns: {exact} of the {total} pairs of eligible columns "
        "share a family table and are carried exactly; the others are carried "
        "as the chain implies. The questions file names the pairs, and a pair "
        "to add or drop can be named there; nothing waits for it."
    )


def _chain_pairs(chain_state: "_ChainState | None") -> "list[list[str]] | None":
    """The pairs a switched run carries exactly, for the questions file's one entry; None unswitched."""
    if chain_state is None:
        return None
    exact: "list[list[str]]" = []
    statistical = chain_state.statistical
    if isinstance(statistical, dict):
        words = statistical["words"]
        if isinstance(words, list):
            for entry in words:
                if isinstance(entry, dict) and entry["word"] == "exact":
                    columns = entry["columns"]
                    if isinstance(columns, list):
                        exact += [[f"{one}" for one in columns]]
    return exact


def _outputs_refused_before_the_chain(table: str, out_dir: "str | None") -> bool:
    """Whether the outputs step's own checks refuse this switched run, read BEFORE it reaches the chain.

    Lane CHON's repair 1 (LANE CHON RULINGS 5 (2); 4.6b.4 amended
    2026-11-09: a run refused before its description is written leaves no
    new key, folder or entry). The same calls the outputs step makes, in
    the same words and at the same step: `profile.default_output_paths`
    (the out-dir's locality gate, the out-dir standing as a folder, each
    name's gate, a folder standing at a name) RAISES what it raised there;
    a name that is the table itself is refused here with the outputs
    step's words (True). A twin's own folder, made once the questions are
    answered (`_make_the_twins_folder`), is settled by the twin's preflight
    before any step runs, so it is not read here. Writes nothing.
    """
    from synthtwin import profile

    session = _current()
    if session is not None and session.folder_to_make:
        return False
    phase = session.phase if session is not None else ""
    _at(results.STEP_OUTPUTS)
    profile_path, summary_path = profile.default_output_paths(pathlib.Path(table), out_dir)
    source = validate_local_path(table, purpose="input")
    if (
        profile_path == source
        or summary_path == source
        or profile.is_the_same_file(profile_path, source)
        or profile.is_the_same_file(summary_path, source)
    ):
        _warn(
            errors.output_would_replace_the_table(_shown(source)),
            step=results.STEP_OUTPUTS,
        )
        return True
    if session is not None:
        session.phase = phase
    return False


def _data_folder_refusal(folder: pathlib.Path, table: str, out_dir: "str | None") -> str:
    """Why the installation's data folder may not be used for this run ('' where it may), read before anything is made.

    Lane CHON's repair 1 (LANE CHON RULINGS 5 (2), skeptic 1's item 3;
    contract 4.6b.4: the ledger is never beside a run's output): the data
    folder holds the private key and the record of earlier descriptions,
    so it is refused where it IS the folder the description is written to
    or the table's own folder, where it stands directly in either, or
    where it lies deeper inside either -- the resolved-path test of the
    private report's folder (`_private_folder_refusal`) -- SAVE that the
    account's own home folder, or a folder above it, holds the platform's
    place for an account's private data deep inside it by design
    (~/Library/Application Support, ~/.local/share, AppData\\Local): a
    table or an output folder there is no reason to refuse the run (the
    rule as first built refused every table kept in the home folder).
    Screen only; the caller writes nothing.

    THE LOCALITY GATE COMES FIRST (batch 4u's outside review, item 2):
    every path is checked as it was typed, by `validate_local_path`'s
    lexical rules, before anything resolves it, so a shared network
    location (`\\\\server\\share\\table.csv`, a URL) is never looked up.
    A data folder that is no plain local folder refuses the run, in
    words that say so; a table or an output folder the gate refuses is
    left to the run's own step, which refuses it before the table is
    read, as it always did.
    """
    from synthtwin import installation

    variable = "LOCALAPPDATA" if installation.system_name() == "nt" else "XDG_DATA_HOME"
    try:
        here = validate_local_path(f"{folder}", purpose="synthtwin data folder")
    except (PathValidationError, OSError, RuntimeError) as refused:
        return (
            f"This computer's data folder for synthtwin, {_shown(str(folder))}, is not a plain folder on this "
            f"computer. {refused} It would hold the private key and the record of earlier descriptions, so "
            f"nothing was read or written. Point {variable} at a private folder of your own on this computer, "
            "and run the command again."
        )
    try:
        table_folder = pathlib.Path(os.path.dirname(f"{validate_local_path(table, purpose='input')}"))
        out_folder = (
            validate_local_path(out_dir, purpose="output folder") if out_dir is not None else table_folder
        )
    except (PathValidationError, OSError, RuntimeError):
        return ""
    try:
        home = pathlib.Path(f"{pathlib.Path(os.path.expanduser('~')).resolve()}")
    except (OSError, ValueError, RuntimeError):
        return ""
    for place in (out_folder, table_folder):
        above_home = place == home or place in home.parents
        if here == place or here.parent == place or (place in here.parents and not above_home):
            return (
                f"This computer's data folder for synthtwin, {_shown(str(folder))}, is the folder this run writes "
                "its description to, or the folder that holds the table, or lies inside one of them. It holds the "
                "private key and the record of earlier descriptions, which never travel beside the files that are "
                f"shared, so nothing was read or written. Point {variable} at a private folder of your own, outside "
                "both, and run the command again."
            )
    return ""


def _profile_outputs_taken(
    table: str, out_dir: "str | None"
) -> "tuple[list[str], list[str]]":
    """The files a profile run writes, and those already at their names, as shown (lane TT, plan P4-D460).

    Decided from the names alone, as `generate` and `validate` decide
    theirs, so the one overwrite rule refuses before the table is read.
    Guarantees: (written, taken), each a list of shown paths; both empty
    where a name cannot be settled yet -- a folder that is not there, a
    path the locality gate refuses -- which the run then refuses at the
    step it always did, in its own words. A description or summary name
    that resolves onto the table is left to the table's own guard (its
    refusal, later in the run, the stage-5 battery's L2), and a questions
    file name that resolves onto an input is no file of the run (it is
    never written, a caution, the battery's L1). Opens nothing. RAISES
    the ProfileError the names raise where something stands at one that
    cannot be written over -- a folder, or a name that cannot be looked
    at -- so the run refuses it before the table is read, in the words it
    always used (lane TT's repair; Codex's review of lane TT, item 7:
    with `data-profile.json` a folder, the empty lists let `profile`
    read, describe and ask about the table before refusing it).
    """
    from synthtwin import profile

    try:
        if out_dir is not None and not pathlib.Path(
            validate_local_path(out_dir, purpose="output folder")
        ).is_dir():
            return ([], [])
        source = pathlib.Path(validate_local_path(table, purpose="input"))
    except (PathValidationError, OSError):
        return ([], [])
    try:
        profile_path, summary_path = profile.default_output_paths(
            pathlib.Path(table), out_dir
        )
        questions_path = profile.questions_output_path(pathlib.Path(table), out_dir)
    except (PathValidationError, OSError):
        return ([], [])
    for target in (profile_path, summary_path):
        if target == source or profile.is_the_same_file(target, source):
            return ([], [])
    targets = [profile_path, summary_path]
    if not any(
        questions_path == place or profile.is_the_same_file(questions_path, place)
        for place in (source, profile_path, summary_path)
    ):
        targets += [questions_path]
    written = [_shown(target) for target in targets]
    taken = [_shown(target) for target in targets if _already_there(target)]
    return (written, taken)


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
    first_row_typed: bool = False,
    chain: "ChainRun | None" = None,
    small_tables_refused: bool = True,
    replace: bool = False,
    persons_given: "list[str] | None" = None,
) -> str:
    """Do the work of `synthtwin profile`; return the exit code (`_run_profile_body`).

    With the chain's switch (`chain`: every shipped run since plan
    P4-D464), the installation's data folder is read, and locked where it
    stands, BEFORE the table is read (contract 4.6b.4: a ledger without
    its key is refused before anything is read), and the lock is released
    however the run ends. NOTHING IS MADE THERE YET (4.6b.4 amended
    2026-11-09, LANE CHON RULINGS 1 (4)): a folder that does not stand, a
    key and the lock in a new folder wait until the run reaches the chain
    (`_chained_description`, `installation.with_key`), so a run refused
    before that -- the table floor, a path, the reader -- leaves no new
    key, folder or entry behind.

    LANE EZ-a (plan P4-D479): `--person` (``persons_given``) declares its
    columns held, as `--identifier` does, and says they name the person
    (`_people_said_settled`); at a terminal a first line comes at once,
    before the table is read, and a line for each stage after it
    (`progress`); and where somebody is at the keyboard, every question the
    written questions file holds open is put after the files are written
    (`_profile_rounds`).
    """
    persons: "list[str]" = []
    for one in persons_given or []:
        if one not in persons:
            persons += [one]
    forced_identifiers = list(forced_identifiers) + [one for one in persons if one not in forced_identifiers]
    session = _current()
    if session is not None:
        session.persons_said = list(persons)
        session.persons_typed = list(persons)
        session.floor_refuses = small_tables_refused
        session.questions_beside = (table, out_dir)
        # ...on a switched run too since lane CHON's merge (batch 4u, step 2):
        # every shipped run is switched, and each round's description is
        # `_described_once`'s.
        session.rounds_follow = _there_is_somebody_to_ask()
    if _progress_at_a_terminal():
        _say(_first_line("Reading", table))
    _counting_switched_on("describing")
    try:
        return _run_profile_switched(
            table, out_dir, smallest_group, floor_chosen, forced_identifiers, forced_codes,
            forced_measurements, forced_decimal_commas, answers_path, kept_values, missing_values,
            first_row, day_first, sheet, metadata_rows_given, delimiter_given, date_counts_given,
            forced_twelve_hours, centuries_given, date_columns_given, first_row_typed, chain,
            small_tables_refused, replace,
        )
    finally:
        progress.switch_off()


def _run_profile_switched(
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
    sheet: str,
    metadata_rows_given: str,
    delimiter_given: str,
    date_counts_given: "list[list[str]] | None",
    forced_twelve_hours: "list[str] | None",
    centuries_given: "list[str] | None",
    date_columns_given: "list[str] | None",
    first_row_typed: bool,
    chain: "ChainRun | None",
    small_tables_refused: bool,
    replace: bool,
) -> str:
    """`_run_profile`'s one road since lane CHON's merge (batch 4u, step 2): the rounds of questions of lane EZ-a.

    Every shipped run is switched since plan P4-D464, so the rounds -- every
    question at the keyboard after the files are written, lane EZ-a's plan
    P4-D479 -- are the switched run's too: each description of a round, the
    first and every later one, is made by `_described_once`, which opens,
    reads and locks the installation for that description alone and
    releases it after, so the record judges each round against the ledger
    as it then stands (contract 4.6b.4 as written; LANE CHON RULINGS 1 (2)).
    Without the switch (the internal unswitched setting) each round is
    `_run_profile_body` as before.
    """
    return _profile_rounds(
        table=table,
        out_dir=out_dir,
        smallest_group=smallest_group,
        floor_chosen=floor_chosen,
        forced_identifiers=forced_identifiers,
        forced_codes=forced_codes,
        forced_measurements=forced_measurements,
        forced_decimal_commas=forced_decimal_commas,
        answers_path=answers_path,
        kept_values=kept_values,
        missing_values=missing_values,
        first_row=first_row,
        day_first=day_first,
        sheet=sheet,
        metadata_rows_given=metadata_rows_given,
        delimiter_given=delimiter_given,
        date_counts_given=date_counts_given,
        forced_twelve_hours=forced_twelve_hours,
        centuries_given=centuries_given,
        date_columns_given=date_columns_given,
        first_row_typed=first_row_typed,
        small_tables_refused=small_tables_refused,
        replace=replace,
        chain=chain,
    )


def _switch_of_a_later_round(chain: "ChainRun | None") -> "ChainRun | None":
    """The switch a later round of the same run describes under (batch 4u's merge of lane CHON).

    --new-key is the run's: where an earlier round made the key, the
    installation opened again for this round would refuse a new one (a
    key stands), so `new_key` is off once the key file stands; until then
    it stays as typed. Every other setting is the run's. Reads whether
    the key file stands; writes nothing.
    """
    if chain is None or not chain.new_key:
        return chain
    from synthtwin import installation

    folder = pathlib.Path(chain.folder) if chain.folder is not None else installation.data_folder()
    if installation.key_path(folder).is_file():
        return dataclasses.replace(chain, new_key=False)
    return chain


def _described_once(
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
    sheet: str,
    metadata_rows_given: str,
    delimiter_given: str,
    date_counts_given: "list[list[str]] | None",
    forced_twelve_hours: "list[str] | None",
    centuries_given: "list[str] | None",
    date_columns_given: "list[str] | None",
    first_row_typed: bool,
    chain: "ChainRun | None",
    small_tables_refused: bool,
    replace: bool,
) -> str:
    """One description of the table: unswitched, `_run_profile_body`; switched, the lane's road (plan P4-D464).

    Lane CHON's switched road as it stands: the data folder never beside
    the output, the installation opened before the table is read and
    released however the description ends, and a description that was not
    written leaving no new key, folder or entry. `_profile_rounds` calls it
    for the first description and for each later round (batch 4u's merge).
    """
    if chain is None:
        return _run_profile_body(
            table=table,
            out_dir=out_dir,
            smallest_group=smallest_group,
            floor_chosen=floor_chosen,
            forced_identifiers=forced_identifiers,
            forced_codes=forced_codes,
            forced_measurements=forced_measurements,
            forced_decimal_commas=forced_decimal_commas,
            answers_path=answers_path,
            kept_values=kept_values,
            missing_values=missing_values,
            first_row=first_row,
            day_first=day_first,
            sheet=sheet,
            metadata_rows_given=metadata_rows_given,
            delimiter_given=delimiter_given,
            date_counts_given=date_counts_given,
            forced_twelve_hours=forced_twelve_hours,
            centuries_given=centuries_given,
            date_columns_given=date_columns_given,
            first_row_typed=first_row_typed,
            small_tables_refused=small_tables_refused,
            replace=replace,
        )
    from synthtwin import installation

    folder = (
        pathlib.Path(chain.folder)
        if chain.folder is not None
        else installation.data_folder()
    )
    # THE DATA FOLDER NEVER BESIDE THE OUTPUT (lane CHON's repair 1; 4.6b.4):
    # refused before anything is opened or made. The folder the platform
    # names (XDG_DATA_HOME, LOCALAPPDATA or the account's own) is read;
    # `ChainRun.folder`, an internal setting no option reaches, is a test's.
    beside = _data_folder_refusal(folder, table, out_dir) if chain.folder is None else ""
    if beside:
        _warn(beside, step=results.STEP_ENVIRONMENT)
        return results.REFUSED
    opened = installation.open_installation(folder, new_key=chain.new_key, key_now=False)
    state = _ChainState(chain, opened)
    try:
        if opened.refusal:
            # 4.6b.4's refusals, in its words, on the screen alone: nothing
            # is read or written, exit status 1 (plan P4-D464).
            _warn(opened.refusal, step=results.STEP_ENVIRONMENT)
            return results.REFUSED
        for line in opened.lines:
            _say(line)
        return _run_profile_body(
            table=table,
            out_dir=out_dir,
            smallest_group=smallest_group,
            floor_chosen=floor_chosen,
            forced_identifiers=forced_identifiers,
            forced_codes=forced_codes,
            forced_measurements=forced_measurements,
            forced_decimal_commas=forced_decimal_commas,
            answers_path=answers_path,
            kept_values=kept_values,
            missing_values=missing_values,
            first_row=first_row,
            day_first=day_first,
            sheet=sheet,
            metadata_rows_given=metadata_rows_given,
            delimiter_given=delimiter_given,
            date_counts_given=date_counts_given,
            forced_twelve_hours=forced_twelve_hours,
            centuries_given=centuries_given,
            date_columns_given=date_columns_given,
            first_row_typed=first_row_typed,
            chain_state=state,
            small_tables_refused=small_tables_refused,
            replace=replace,
        )
    finally:
        # A run that wrote no description leaves no new key, folder or
        # entry (4.6b.4 amended 2026-11-12; lane CHON's repair 1): what it
        # recorded and made is taken back under its lock, the folder it made
        # once the lock is gone.
        if not state.described:
            installation.withdraw(state.opened, state.recorded)
        # The installation as the run left it: the lock it holds, taken
        # before the table was read or as the run reached the chain.
        installation.release(state.opened)
        if not state.described:
            installation.remove_made_folder(state.opened)


# -- every question at the keyboard (lane EZ-a, plan P4-D479) ----------------
#
# THE WALKTHROUGH'S ITEM 4: the Safe Harbor question, the checklist and the
# questions about the file were put only in the questions file, and the one
# way to answer them was to hand-edit a nested JSON file of some twenty
# kilobytes. So, where somebody is at the keyboard, every entry the written
# questions file holds open and no prompt of this run put is put after the
# files are written, one renderer for every kind of entry, and the answers
# go into that file and the table is described again in this process
# exactly as `--answers` describes it: the keyboard IS the file.

# The rounds of answers a run puts at most: the first, and as many more as
# the zoo's own rounds allow (`tests/health_zoo.py`'s `ANSWER_ROUNDS_AT_MOST`).
_ANSWER_ROUNDS_AT_MOST = 6


def _questions_beside(table: str, out_dir: "str | None") -> str:
    """Where this run writes its questions file, as typed; empty where the names cannot be settled yet.

    Asked when an answers file is read, never before: a twin's folder is
    made only once its questions are answered (lane TT, plan P4-D460).
    """
    from synthtwin import profile

    try:
        return f"{profile.questions_output_path(pathlib.Path(table), out_dir)}"
    except (PathValidationError, errors.ProfileError, OSError, ValueError):
        return ""


def _progress_at_a_terminal(stream: int = 1) -> bool:
    """Whether a line written to ``stream`` is shown: the run's screen is the terminal, and that stream is a terminal.

    Lane EZ-a, plan P4-D479 (the walkthrough's item 7). The first line is
    asked of the output stream (1), which it is written to, as
    `_a_person_at_the_terminal` asks it; THE COUNTERS ARE ASKED OF THE ERROR
    STREAM (2), WHICH THEY ARE WRITTEN TO (lane EZ-a's second repair;
    Codex's item 10: with `2>run.log` the output stream stayed a terminal,
    the counters went on, and the log filled with lines written over in
    place). A piped, captured or library run shows nothing new. Raises
    nothing.
    """
    session = _current()
    if session is None or session.screen != TERMINAL:
        return False
    try:
        return bool(os.isatty(stream))
    except (OSError, ValueError):
        return False


def _counting_switched_on(what: str) -> None:
    """Switch the counters on (`progress.switch_on`) only where the error stream they are written to is a terminal (Codex's item 10)."""
    if _progress_at_a_terminal(2):
        progress.switch_on(what)


def _first_line(doing: str, path: str) -> str:
    """The line a terminal shows at once, before a long run reads anything (lane EZ-a, plan P4-D479)."""
    return (
        f"{doing} {_shown(pathlib.Path(path).name)}: on a large table this takes a "
        f"long time; do not close this window."
    )


def _entry_key(record: "results.Asked") -> "tuple[str, str, str, str]":
    """What makes an entry of the questions file the same entry in a later round: its section, subject, role and reason."""
    return (record.section, record.subject, record.role, record.reason)


def _entry_keys(record: "results.Asked") -> "tuple[tuple[str, str], ...]":
    """Each answer an entry offers, with the key the screen shows beside it.

    Today's key where the answer has one (`_KEY_OF`, `measurement` typed
    `m` beside `keep`), else the answer's own word; a key two answers would
    share is the second one's word. The riders that number every question
    1 to n (the walkthrough's items 8 to 10) are lane EZ-b's.
    """
    offered = [offer.answer for offer in record.offers]
    both = asking.ANSWER_KEEP in offered and asking.ANSWER_MEASUREMENT in offered
    found: "list[tuple[str, str]]" = []
    used: "list[str]" = []
    for answer in offered:
        key = answer
        if answer == asking.ANSWER_MEASUREMENT and both:
            key = "m"
        elif answer in _KEY_OF:
            key = _KEY_OF[answer]
        if key in used:
            key = answer
        used += [key]
        found += [(key, answer)]
    return tuple(found)


def _enter_said(record: "results.Asked") -> str:
    """What Enter does at one entry, from the reading it stands on unanswered (its `read_as_now`)."""
    now = record.read_as_now
    if record.section == asking.BETWEEN_COLUMNS:
        # The subject question (Codex's review of batch 4u, item 6): what
        # stands is its own sentence; a column is named in the file or typed.
        return (
            f"Press Enter to leave it open. {_one_stop(now)} A column that identifies "
            "the person is named in the questions file, or with --person when you run "
            "the command again."
        )
    if now == asking.ANSWER_IDENTIFIER:
        return (
            "Press Enter to leave it open: the column stays held as record "
            "numbers, and none of its values is published."
        )
    if now == asking.SAFE_HARBOR_TOP_CODED:
        return (
            "Press Enter to leave it open: the Safe Harbor top-code stays, so "
            "no value past it is published or written to the twin."
        )
    for offer in record.offers:
        if offer.answer == now:
            return f"Press Enter to leave it open: it stays read as {_one_stop(offer.means)}"
    return "Press Enter to leave it open: it keeps the reading it has now."


def _the_entry(record: "results.Asked", number: int, place: int, total: int) -> str:
    """One entry of the questions file, as the person sees it at the keyboard (lane EZ-a, plan P4-D479).

    THE ENTRY'S OWN WORDS AND NO CELL: what it is about, what synthtwin
    saw (a count, a width or a separator), each answer with what the
    description then publishes, and what Enter leaves standing.

    ITS NUMBER IS THE FILE'S (lane EZ-a's repair; the orchestrator's LANE EZ
    RULINGS 4 (2) (a)): ``number`` is the entry's place among every
    question the questions file holds open (`contract.question_number`),
    the number a plain-text answers file names it by; its place in this
    round follows in brackets. 0 where the file could not be read, and
    then no number is printed that a line could name.
    """
    about = f"'{_shown(record.subject)}'" if record.column else _shown(record.subject)
    lines = ""
    keys = _entry_keys(record)
    for place_offered in range(len(record.offers)):
        offer = record.offers[place_offered]
        lines = lines + (
            f"\n      [{_shown(keys[place_offered][0])}] {offer.means}\n"
            f"          then the description publishes {offer.publishes}"
        )
    named = f"Question {number} ({place} of {total} in this round)" if number else f"({place} of {total} in this round)"
    return (
        f"\n  {named}: {about}\n"
        f"    what synthtwin saw: {_one_stop(record.saw)}\n"
        f"    Which of these fits it?{lines}\n"
        f"    {_enter_said(record)}"
    )


def _numbers_in_the_file(records: "list[results.Asked]") -> "list[int]":
    """Each record's number in the questions file this run wrote last (`contract.question_number`); 0 where it cannot be read.

    Read from the file on disk at this moment, which is the file a
    plain-text answers file is matched against until the table is
    described again (lane EZ-a's repair, LANE EZ RULINGS 4 (2) (a)).
    """
    from synthtwin import contract

    where = _questions_written()
    if where is None:
        return [0 for _record in records]
    try:
        document = contract.load_answers(f"{where}")
    except (PathValidationError, errors.ProfileError):
        return [0 for _record in records]
    numbers: "list[int]" = []
    for record in records:
        entry = _entry_of(document, record)
        numbers += [0 if entry is None else contract.question_number(document, entry)]
    return numbers


def _put_the_entries(
    entries: "list[results.Asked]",
) -> "tuple[list[tuple[results.Asked, str]], bool]":
    """Put each entry at the keyboard; return each one read with its answer, and whether the person ended input.

    Every read goes through `_read_one_answer`, the entry's answers on the
    session while it is on screen. Enter (the reader's own word, or the
    empty text `tests/keyboard.py`'s reader gives) leaves the entry open,
    and so does a word the entry does not offer that a stand-in for the
    person hands back. Each entry read is recorded as put at a prompt.
    """
    session = _current()
    total = len(entries)
    _say(
        f"\n{'=' * 66}\n"
        f"{total} MORE QUESTION(S), FROM THE QUESTIONS FILE\n"
        f"{'=' * 66}\n"
        f"The files above are written. These questions are in the questions "
        f"file too: answer them here, and synthtwin describes the table again "
        f"with your answers. Press Enter to leave one open; what stands until "
        f"it is answered is said on its last line. In a text file of answers, "
        f"write a column's name exactly as shown; the numbers are labels. "
        f"{_STOP_KEYS_SAID}: the files above stay as they are."
    )
    given: "list[tuple[results.Asked, str]]" = []
    numbers = _numbers_in_the_file(entries)
    place = 0
    for record in entries:
        place = place + 1
        _say(_the_entry(record, numbers[place - 1], place, total))
        if session is not None:
            session.offered_now = _entry_keys(record)
        try:
            answer = _read_one_answer(_LEFT_OPEN)
        finally:
            if session is not None:
                session.offered_now = ()
        if answer is None:
            return given, True
        if answer not in [offer.answer for offer in record.offers]:
            answer = _LEFT_OPEN
        given += [(record, answer)]
        if session is not None:
            put = (record.column, record.role, record.reason)
            if put not in session.put:
                session.put += [put]
            session.prompted = session.prompted + 1
    return given, False


def _entry_of(document: "dict[str, object]", record: "results.Asked") -> "dict[object, object] | None":
    """The entry of a questions file's document a record stands for, by its section and order; None where it is not there."""
    if record.section == asking.BETWEEN_COLUMNS:
        # The subject question, under the chain's one entry (item 6).
        chained = document[asking.BETWEEN_COLUMNS] if asking.BETWEEN_COLUMNS in document else None
        found = chained[asking.ROWS_PER_PERSON] if isinstance(chained, dict) and asking.ROWS_PER_PERSON in chained else None
        return found if isinstance(found, dict) else None
    if record.section == results.SECTION_CHECKLIST:
        section = document["checklist"] if "checklist" in document else None
        entries = section["columns"] if isinstance(section, dict) and "columns" in section else None
    else:
        entries = document[record.section] if record.section in document else None
    if not isinstance(entries, list) or not 1 <= record.order <= len(entries):
        return None
    entry = entries[record.order - 1]
    if not isinstance(entry, dict) or "column" not in entry or entry["column"] != record.subject:
        return None
    return entry


def _subject_entry_now(questions: pathlib.Path) -> "list[results.Asked]":
    """The questions file's subject question as the one entry of a round at the keyboard, where it stands open; else none.

    Codex's review of batch 4u, item 6: the subject question (lane GRa,
    plan P4-D449: may one person stand on several rows?) is written under
    the chain's one entry, `between_columns`, and no record of the result
    stands for it, so where it was the only question no round put it and
    the twin carried no relationship until the person edited the file by
    hand. Put once a run, in a round of its own after the file's other
    entries (`_profile_rounds`), so ending input there loses no answer given
    to them. It offers the two answers that name no column; a column is
    named in the file or with --person (`_enter_said`). Reads the file; no
    value of the table is in it.
    """
    from synthtwin import contract

    session = _current()
    if session is None or session.subject_entry_put:
        return []
    try:
        document = contract.load_answers(f"{questions}")
    except (PathValidationError, errors.ProfileError):
        return []
    probe = results.Asked(asking.BETWEEN_COLUMNS, 1, "", "", asking.ROWS_PER_PERSON, "", "")
    entry = _entry_of(document, probe)
    if entry is None:
        return []
    written = entry["your_answer"] if "your_answer" in entry else ""
    if not isinstance(written, str) or parsing.trimmed(written):
        return []
    offers: "list[results.Offer]" = []
    choices = entry["answers_you_can_give"] if "answers_you_can_give" in entry else []
    for choice in choices if isinstance(choices, list) else []:
        if (
            isinstance(choice, dict)
            and "answer" in choice
            and "means" in choice
            and "publishes" in choice
            and choice["answer"] in (asking.ANSWER_ONE_ROW_EACH, asking.ANSWER_NO_PERSON_COLUMN)
        ):
            offers += [results.Offer(f"{choice['answer']}", f"{choice['means']}", f"{choice['publishes']}")]
    seen = entry["seen"] if "seen" in entry else ""
    asked = entry["question"] if "question" in entry else ""
    now = entry["read_as_now"] if "read_as_now" in entry else ""
    if not offers or not isinstance(seen, str) or not isinstance(asked, str) or not isinstance(now, str):
        return []
    session.subject_entry_put = True
    return [
        results.Asked(
            asking.BETWEEN_COLUMNS, 1, "", "", asking.ROWS_PER_PERSON,
            f"{_one_stop(seen)} {asked}", now, tuple(offers), False, asking.ROWS_PER_PERSON,
        )
    ]


def _answers_written_into(
    questions: pathlib.Path,
    answered: "list[tuple[results.Asked, str]]",
    guards: "list[tuple[pathlib.Path, str]]",
) -> str:
    """Write the keyboard's answers beside 'your_answer' in the questions file this run wrote (lane EZ-a, plan P4-D479).

    Returns the file's text before them, which `_questions_written_back`
    writes back where the table is not described with them (lane EZ-a's
    repair): the file was written by `canonical.serialize`, so the document
    read and serialized again is its text byte for byte.
    """
    from synthtwin import canonical, contract, writing

    document = contract.load_answers(f"{questions}")
    before = canonical.serialize(document)
    for record, answer in answered:
        entry = _entry_of(document, record)
        if entry is not None:
            entry["your_answer"] = answer
    writing.write_one_file(
        questions, canonical.serialize(document), sources=guards, state=writing.DiskState()
    )
    return before


def _questions_written_back(
    questions: pathlib.Path, text: str, guards: "list[tuple[pathlib.Path, str]]"
) -> None:
    """Write a questions file's earlier text back, where a later round's description did not finish (lane EZ-a's repair).

    Raises what `writing.write_one_file` raises, whose words name what is
    on disk.
    """
    from synthtwin import writing

    writing.write_one_file(questions, text, sources=guards, state=writing.DiskState())


def _ended_said() -> None:
    """What a later round says where the person ended input: the files stand (R7); the questions still open follow (`_still_open_said`)."""
    _say("\nYou ended the questions here. The files written above stand as they are.")


def _open_records() -> "list[results.Asked]":
    """The entries of this run's questions file that stand open: the questions about the file and the asked ones.

    A checklist entry left blank keeps the reading it names; one held under
    `identifier` is held by the count in people, which no answer gives back
    (plan P4-D406), so neither is said to be open. NOR IS A QUESTION WHOSE
    ANSWER STANDS (lane EZ-a's repair; LANE EZ RULINGS 4 (4)): answered at
    the first prompt other than with Enter, or in a later round described
    again, and put again in the file under the reading that answer gave
    (plan P4-D401) (`_Session.answers_standing`).
    """
    session = _current()
    if session is None:
        return []
    return [
        one
        for one in session.questions
        if one.offers
        and one.section in (results.SECTION_ABOUT_FILE, results.SECTION_ASKED)
        and (one.column, one.role, one.reason) not in session.answers_standing
    ]


def _questions_written() -> "pathlib.Path | None":
    """The questions file this run wrote, or None."""
    session = _current()
    if session is None:
        return None
    found = [one.path for one in session.files if one.kind == results.FILE_QUESTIONS]
    return pathlib.Path(found[len(found) - 1]) if found else None


def _still_open_said() -> None:
    """Say, before the next command, which questions stay open and what stands until they are answered (lane EZ-a, plan P4-D479).

    THE WALKTHROUGH'S ITEM 1, ITS SCREEN PART: 'Next, build the twin' was
    printed while the Safe Harbor question held weight and heart rate at
    90. Said where somebody is at the keyboard, from the entries' own
    readings; nothing where none stays open.
    """
    session = _current()
    if session is None or session.ask is None or session.twin_step:
        return
    still = _open_records()
    if not still:
        return
    capped = [one.subject for one in still if one.read_as_now == asking.SAFE_HARBOR_TOP_CODED]
    held = [
        one.subject for one in still if one.read_as_now == asking.ANSWER_IDENTIFIER and one.subject not in capped
    ]
    said = ""
    if capped:
        said = (
            f" Until you answer, values past the Safe Harbor top-code in "
            f"{_joined([_shown(one) for one in capped], ' and ')} are written as the "
            f"top-code (an age above 89 as 90), in the description and in the twin, "
            f"so the twin is wrong for those columns if they hold no ages."
        )
    if held:
        said = said + (
            f" {_joined([_shown(one) for one in held], ' and ')} "
            f"{'stays' if len(held) == 1 else 'stay'} held as "
            f"record numbers: none of their values is published, and the twin "
            f"makes them up."
        )
    count = len(still)
    where = _questions_written()
    named = f" in {_shown(where)}" if where is not None else ""
    numbers = _numbers_in_the_file(still)
    listed = [
        f"question {numbers[place]}, {_shown(still[place].subject)}"
        for place in range(len(still))
        if numbers[place]
    ]
    numbered = f" ({_joined(listed, '; ')})" if listed else ""
    _say(
        f"\n{count} question{'' if count == 1 else 's'} {'is' if count == 1 else 'are'} "
        f"still open{named}{numbered}.{said}{_how_to_answer_said(where, count)}"
    )


def _profile_again(questions: str, replacing: bool = False) -> str:
    """The person's own `profile` command line with `--answers` naming ``questions``, typed as a shell reads it; empty where none is known.

    Lane EZ-a's repair (the orchestrator's LANE EZ RULINGS 4 (4)): the
    closing lines said 'run the same command again', and the same command
    is refused at once once its files exist (the one overwrite rule, plan
    P4-D460: measured, exit 1 in 0.3 CPU seconds). `--answers` is the round
    that rule lets write over the files the round before wrote, and it
    hands back the questions still open, so this line runs. Every option
    the person typed is kept, as the twin's commands keep them
    (`_twin_again`); the seed and `--replace` are no options of this
    command's round.

    ``replacing`` (Codex's review of batch 4u, item 7): the record of
    earlier descriptions refused the description a later round made with
    the answers given since, in words that ask for --replace-description;
    the line then also types the record's own options the person typed
    (`--name`, `--private-folder`) and `--replace-description`, so it is
    the run those words describe.
    """
    session = _current()
    typed = session.typed if session is not None else None
    if session is None or typed is None or typed.given is None:
        return ""
    # ...less every typed declaration an answer of the file replaced, which
    # the file's newer answer would otherwise lose to (lane EZ-a's second
    # repair; Codex's item 1).
    typed = _options_left(typed, session.typed_replaced)
    words = _twin_again(f"{typed.given}", dataclasses.replace(typed, answers=questions, seed="0", replace=False))
    words[1] = _PROFILE
    if replacing:
        if typed.name is not None:
            words += _option_words("--name", typed.name)
        if typed.private_folder is not None:
            words += _option_words("--private-folder", typed.private_folder)
        words += ["--replace-description"]
    return _typed_words(words)


def _how_to_answer_said(where: "pathlib.Path | None", count: int = 2) -> str:
    """The sentence that tells a person at the keyboard how to answer the questions still open: a command that runs (LANE EZ RULINGS 4 (4)).

    'it' for one question still open, 'them' for several (LANE EZ RULINGS 8
    (5), the verify's MINOR 6).
    """
    them = "it" if count == 1 else "them"
    line = _profile_again(f"{where}") if where is not None else ""
    if not line:
        return (
            f" To answer {them}, run your command again with --answers and the "
            f"questions file, or write lines 'column = answer' in a text file "
            f"and name it after --answers."
        )
    return (
        f" To answer {them}, run this at the keyboard:\n  {line}{_quoting_said(line)}\n"
        f"or write lines 'column = answer' in a text file and name that file "
        f"after --answers in place of the questions file."
    )


def _closing(description: pathlib.Path) -> None:
    """The lines that end a profile run that wrote a description: what stays open, then the next command.

    Lane EZ-a, plan P4-D479. Where more rounds of questions may follow the
    files (`_Session.rounds_follow`), they are held back for `_profile_rounds`
    to show once, after the last round.
    """
    lines = _teaching_generate(description)
    session = _current()
    if session is not None and session.rounds_follow:
        session.closing = lines
        return
    _still_open_said()
    _teach(lines)


def _records_put(put: "set[tuple[str, str, str, str]]") -> None:
    """The run's records of its questions, each entry put at a prompt in any round said put, and the tally again."""
    session = _current()
    if session is None or not session.questions:
        return
    records = tuple(
        dataclasses.replace(one, put=True) if _entry_key(one) in put and not one.put else one
        for one in session.questions
    )
    columns = session.tally[0][1] if session.tally else 0
    _questions_put_in_the_result(records, columns)


# WHAT A REFUSAL ENDS WITH WHERE IT WROTE NOTHING, and what a refused later
# round says in its place: the files the description before it wrote stand
# (lane EZ-a's repair; the orchestrator's LANE EZ RULINGS 4 (3) (b): a later
# round refused with 'Nothing was written.' while the first round's three
# files stood on disk). Longest first, so a sentence is never cut in two;
# each a literal, as the offline audit reads a method's arguments.


def _after_the_files(text: str) -> str:
    """A refusal's words as a later round shows them: 'Nothing new was written.' where they said nothing was written.

    Raises TypeError for words that are not text (the offline audit's type
    gate, as `_ends_input`).
    """
    if not isinstance(text, str):
        raise TypeError("a refusal's words must be text")
    return (
        text.replace("Nothing was written and your table was not changed.", "Nothing new was written.")
        .replace("Nothing was written and nothing was changed.", "Nothing new was written.")
        .replace("Nothing was read and nothing was written.", "Nothing new was written.")
        .replace("Nothing has been written.", "Nothing new was written.")
        .replace("Nothing was written.", "Nothing new was written.")
    )


def _described_again(
    captured: "list[tuple[str, str]]",
    verdict: str,
    shown_before: "list[str]",
    questions: "pathlib.Path | None" = None,
    kept: bool = False,
) -> None:
    """Show what a run described again with the keyboard's answers said that the person needs: its closing lines.

    The long summary is read once a command: what the run printed from its
    repeat line, or its "Written:" list, onward is shown, and each warning
    the runs before it did not already show (``shown_before``); a refusal
    is shown whole, in words that match the files on disk (`_after_the_files`),
    and then that the files written before it stand, the questions file
    without the answers given since (``questions``, written back as it was:
    `_profile_rounds`), and the command that answers again. ``kept``: the
    record of earlier descriptions refused the round's description in words
    that ask for --replace-description, so the answers given since stay in
    the questions file and the command shown applies them with that option
    (Codex's review of batch 4u, item 7).
    """
    start = len(captured)
    if verdict == results.NO_MISS:
        for place in range(len(captured)):
            stream, text = captured[place]
            if stream == _OUT and ("TO REPEAT THIS RUN" in text or text[:9] == "\nWritten:"):
                start = place
                break
    for place in range(len(captured)):
        stream, text = captured[place]
        if verdict != results.NO_MISS or place >= start:
            if stream == _ERR and text in shown_before and verdict == results.NO_MISS:
                continue
            _show(stream, _after_the_files(text) if verdict != results.NO_MISS else text)
        elif stream == _ERR and text not in shown_before:
            _show(stream, text)
    if verdict != results.NO_MISS and questions is not None:
        stands = _answers_kept_said(questions) if kept else _files_stand_said(questions)
        session = _current()
        if session is not None:
            session.on_disk = parsing.visible_lines(stands)
        line = _profile_again(f"{questions}", replacing=kept)
        if kept:
            _say(
                f"\n{stands}"
                + (
                    " If the earlier description was never shared with anyone, run this to describe the "
                    f"table with them:\n  {line}{_quoting_said(line)}"
                    if line
                    else " If the earlier description was never shared with anyone, run your command again "
                    "with --answers, the questions file and --replace-description."
                )
            )
            return
        _say(
            f"\n{stands}"
            + (f" To answer again, run this at the keyboard:\n  {line}{_quoting_said(line)}" if line else "")
        )


# A LATER ROUND NEVER BRINGS BACK A TYPED DECLARATION THAT A NEWER ANSWER
# REPLACED (lane EZ-a's second repair; the orchestrator's LANE EZ RULINGS 7,
# Codex's item 1). Each round after the files hands the table back to
# `_run_profile_body` with the questions file as `--answers`, and that body
# reads a typed declaration as later than any answer the file keeps (plan
# P4-D408, `asking.typed_over_kept`). Inside one command the command line is
# the OLDEST statement: a keyboard answer at the first prompt is kept under
# `answered_before`, and a typed `--decimal-comma patient_no` handed on took
# it back from a newer `identifier`, read seven-figure patient numbers as
# counts and published them. So each later round, its repeat line and the
# command a run teaches leave off every typed declaration an answer of the
# file replaces (`asking.typed_answered_over`).


def _typed_said(
    identifiers: "list[str]",
    codes: "list[str]",
    measurements: "list[str]",
    commas: "list[str]",
    twelve_hours: "list[str] | None",
    date_counts_given: "list[list[str]] | None",
    centuries_given: "list[str] | None",
    date_columns_given: "list[str] | None",
    day_first: bool,
    delimiter_given: str,
    first_row: str,
    first_row_typed: bool,
) -> "tuple[tuple[str, str], ...]":
    """The command line's declarations as `(column, answer)`, read as `_run_profile_body` reads them (`_typed_answers`); a typed form it would refuse is left out."""
    counted: "dict[str, str]" = {}
    for pair in date_counts_given or []:
        if len(pair) == 2:
            counted[f"{pair[0]}"] = f"{pair[1]}"
    centuries: "dict[str, int]" = {}
    reset: "list[str]" = []
    for typed_century in centuries_given or []:
        found = _century_given(typed_century)
        if found is None:
            continue
        if found[1] in parsing.CENTURY_WINDOW_YEARS:
            centuries[found[0]] = found[1]
        elif found[0] not in reset:
            reset += [found[0]]
    delimiter = _DELIMITER_SPELLINGS[delimiter_given] if delimiter_given in _DELIMITER_SPELLINGS else ""
    return _typed_answers(
        list(codes), list(identifiers), list(measurements), list(commas), list(twelve_hours or []),
        counted, centuries, sorted({one: 1 for one in (date_columns_given or [])}), day_first, delimiter,
        first_row, reset, first_row_typed,
    )


def _typed_replaced_in(questions: "pathlib.Path | None", typed: "tuple[tuple[str, str], ...]") -> "list[tuple[str, str]]":
    """The typed declarations an answer of the questions file replaces (`asking.typed_answered_over`); none where the file cannot be read."""
    from synthtwin import contract

    if questions is None or not typed:
        return []
    try:
        document = contract.load_answers(f"{questions}")
    except (errors.ProfileError, PathValidationError):
        return []
    return list(asking.typed_answered_over(document, typed))


def _typed_left(names: "list[str] | None", answer: str, replaced: "list[tuple[str, str]]") -> "list[str]":
    """The names of one typed list no answer replaced."""
    return [name for name in names or [] if (name, answer) not in replaced]


def _century_left(typed: str, replaced: "list[tuple[str, str]]") -> bool:
    """Whether a typed `--century COLUMN=YEAR` stands: no answer replaced the window it names."""
    found = _century_given(typed)
    if found is None:
        return True
    word = asking.century_answer(found[1]) if found[1] in parsing.CENTURY_WINDOW_YEARS else asking.ANSWER_CENTURY_POSIX
    return (found[0], word) not in replaced


def _options_left(options: _Options, replaced: "list[tuple[str, str]]") -> _Options:
    """The typed command line less each declaration an answer replaced: what the command a run teaches types again."""
    if not replaced:
        return options
    delimiter = _DELIMITER_SPELLINGS[options.delimiter] if options.delimiter in _DELIMITER_SPELLINGS else ""
    first_row_word = (
        asking.ANSWER_FIRST_ROW_NAMES if options.first_row == _FIRST_ROW_NAMES
        else asking.ANSWER_FIRST_ROW_DATA if options.first_row == _FIRST_ROW_DATA
        else asking.TYPED_FIRST_ROW_AUTOMATIC
    )
    first_row_left = (asking.FIRST_ROW_SUBJECT, first_row_word) not in replaced
    return dataclasses.replace(
        options,
        persons=_typed_left(options.persons, asking.ANSWER_IDENTIFIER, replaced),
        identifiers=_typed_left(options.identifiers, asking.ANSWER_IDENTIFIER, replaced),
        codes=_typed_left(options.codes, asking.ANSWER_CODE, replaced),
        measurements=_typed_left(options.measurements, asking.ANSWER_MEASUREMENT, replaced),
        decimal_commas=_typed_left(options.decimal_commas, asking.ANSWER_DECIMAL_COMMA, replaced),
        twelve_hours=_typed_left(options.twelve_hours, asking.ANSWER_TWELVE_HOUR, replaced),
        date_columns=_typed_left(options.date_columns, asking.ANSWER_DATES, replaced),
        date_counts=[pair for pair in options.date_counts if len(pair) != 2 or (f"{pair[0]}", f"{pair[1]}") not in replaced],
        centuries=[one for one in options.centuries if _century_left(one, replaced)],
        day_first=options.day_first and (asking.DAY_FIRST_SUBJECT, asking.ANSWER_DAY_FIRST) not in replaced,
        delimiter=options.delimiter if (asking.DELIMITER_SUBJECT, asking.delimiter_answer(delimiter)) not in replaced else "",
        first_row=options.first_row if first_row_left else _FIRST_ROW_AUTOMATIC,
        first_row_typed=options.first_row_typed and first_row_left,
    )


def _typed_replaced_said() -> "list[str]":
    """Each typed declaration an answer replaced, written as it is typed: the repeat line says to take it out (`_how_to_repeat`)."""
    session = _current()
    said: "list[str]" = []
    for name, answer in session.typed_replaced if session is not None else []:
        option = {
            asking.ANSWER_IDENTIFIER: "--identifier",
            asking.ANSWER_CODE: "--code",
            asking.ANSWER_MEASUREMENT: "--measurement",
            asking.ANSWER_DECIMAL_COMMA: "--decimal-comma",
            asking.ANSWER_TWELVE_HOUR: "--twelve-hour",
            asking.ANSWER_DATES: "--date-column",
        }
        if answer in option:
            said += [_typed_option(option[answer], name)]
        elif answer in date_counts.MEMBERS:
            said += [f"{_typed_option('--date-count', name)} {answer}"]
    return said


def _files_stand_said(questions: pathlib.Path) -> str:
    """What is on disk after a later round's description was refused: the files written before it, its answers not among them.

    Said only where that description stopped before writing; a write it
    began and could not finish names what is on disk in its own words.
    """
    return (
        f"The files written before these answers stand as they were, "
        f"{_shown(questions)} among them, and hold none of the answers given since."
    )


def _answers_kept_said(questions: pathlib.Path) -> str:
    """What is on disk after the record refused a later round's description: the files before it, the answers given since kept.

    Codex's review of batch 4u, item 7: the description and its summary
    are the ones written before these answers; the questions file holds
    the answers given since, beside 'your_answer', so the command that
    follows applies them (`_profile_again`, ``replacing``).
    """
    return (
        f"The description and its summary written before these answers stand as they were. "
        f"The answers given since are kept in {_shown(questions)}."
    )


def _profile_rounds(
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
    first_row_typed: bool = False,
    small_tables_refused: bool = True,
    replace: bool = False,
    chain: "ChainRun | None" = None,
) -> str:
    """One description, then, where somebody is at the keyboard, every question left open (lane EZ-a, plan P4-D479).

    ROUNDS AFTER THE FILES. Once the first description and its questions
    file are written, each entry of the file -- about the file, asked, the
    checklist; the Safe Harbor questions among them -- that no prompt of
    this run put is put with one renderer (`_put_the_entries`); the answers
    are written beside 'your_answer' in that file, and the table is
    described again by `_run_profile_body` handed the file as `--answers`,
    in this process, nobody asked meanwhile and its screen held back but
    for its closing lines (`_described_again`). The rounds stop where
    nothing is left that no prompt put, where every question put was left
    open with Enter, or at `_ANSWER_ROUNDS_AT_MOST` descriptions. ENDING
    INPUT IN A LATER ROUND (Ctrl-D, Ctrl-C, or the end of a library run's
    list of lines) keeps the files the rounds before it wrote and says how
    many questions stay open (the orchestrator's LANE EZ RULINGS 1 (6));
    in the first round it still writes nothing. Nobody at the keyboard,
    the one description is the whole run, as before. EACH DESCRIPTION IS
    `_described_once`'s (batch 4u's merge of lane CHON): on a switched run
    each round opens and releases the installation, and the record judges
    it against the ledger as it then stands.
    """
    from synthtwin import profile

    verdict = _described_once(
        table=table, out_dir=out_dir, smallest_group=smallest_group, floor_chosen=floor_chosen,
        forced_identifiers=forced_identifiers, forced_codes=forced_codes,
        forced_measurements=forced_measurements, forced_decimal_commas=forced_decimal_commas,
        answers_path=answers_path, kept_values=kept_values, missing_values=missing_values,
        first_row=first_row, day_first=day_first, sheet=sheet, metadata_rows_given=metadata_rows_given,
        delimiter_given=delimiter_given, date_counts_given=date_counts_given,
        forced_twelve_hours=forced_twelve_hours, centuries_given=centuries_given,
        date_columns_given=date_columns_given, first_row_typed=first_row_typed,
        small_tables_refused=small_tables_refused, replace=replace, chain=chain,
    )
    session = _current()
    if session is None or not session.rounds_follow:
        return verdict
    put: "set[tuple[str, str, str, str]]" = {_entry_key(one) for one in session.questions if one.put}
    # THE COMMAND LINE IS THE OLDEST STATEMENT OF THE COMMAND (lane EZ-a's
    # second repair; Codex's item 1): what a later round, its repeat line and
    # the taught command leave off it, as each answer of the file replaces it.
    typed = _typed_said(
        forced_identifiers, forced_codes, forced_measurements, forced_decimal_commas, forced_twelve_hours,
        date_counts_given, centuries_given, date_columns_given, day_first, delimiter_given, first_row,
        first_row_typed,
    )
    session.typed_replaced = _typed_replaced_in(_questions_written(), typed)
    rounds = 1
    while verdict == results.NO_MISS and rounds < _ANSWER_ROUNDS_AT_MOST:
        questions = _questions_written()
        entries = [
            one
            for one in session.questions
            if one.section != results.SECTION_HELD and one.offers and _entry_key(one) not in put
        ]
        # THE SUBJECT QUESTION, IN A ROUND OF ITS OWN once the file's other
        # entries are put (Codex's review of batch 4u, item 6), the only
        # question or not: no record of the result stands for it.
        if questions is not None and not entries:
            entries = _subject_entry_now(questions)
        if questions is None or not entries:
            break
        given, ended = _put_the_entries(entries)
        put = put | {_entry_key(record) for record, _answer in given}
        answered = [(record, answer) for record, answer in given if answer not in ("", _LEFT_OPEN)]
        if ended:
            _ended_said()
            break
        if not answered:
            # ...and every entry of the round left open does not keep the
            # subject question from its own round (item 6).
            if not session.subject_entry_put:
                continue
            break
        source = pathlib.Path(validate_local_path(table, purpose="input"))
        described, summary = profile.default_output_paths(pathlib.Path(table), out_dir)
        guards = [(source, errors.INPUT_TABLE), (described, errors.INPUT_DESCRIPTION), (summary, errors.INPUT_SUMMARY)]
        # THE ANSWERS STAND IN THE FILE ONLY ONCE THE TABLE IS DESCRIBED WITH
        # THEM (lane EZ-a's repair; LANE EZ RULINGS 4 (3) (b)): the file's
        # text before them is kept and written back wherever the description
        # does not finish, so 'the files written before these answers stand
        # as they were' is true of the questions file too.
        kept_text = _answers_written_into(questions, answered, guards)
        replaced = _typed_replaced_in(questions, typed)
        session.typed_replaced = replaced
        captured: "list[tuple[str, str]]" = []
        screen, asking_now = session.screen, session.ask
        seen = list(session.err_shown)
        before = (session.files, session.warnings, session.left_behind)
        said_before = len(session.refusal_words)
        where_before = (session.step, session.phase, session.key)
        session.screen, session.ask = captured, None
        # ...and the subject question is put at the keyboard from inside
        # that description (LANE EZ RULINGS 4 (3) (a)), with the real screen
        # and reader, for that one question (`_people_said_settled`).
        session.subject_reader = (screen, asking_now)
        session.ended_at_subject = False
        session.files, session.warnings, session.left_behind = [], [], []
        session.on_disk = ""
        session.round_refused_by_record = False
        refused: "BaseException | None" = None
        verdict = results.REFUSED
        first_row_word = (
            asking.ANSWER_FIRST_ROW_NAMES if first_row == _FIRST_ROW_NAMES
            else asking.ANSWER_FIRST_ROW_DATA if first_row == _FIRST_ROW_DATA
            else asking.TYPED_FIRST_ROW_AUTOMATIC
        )
        first_row_left = (asking.FIRST_ROW_SUBJECT, first_row_word) not in replaced
        delimiter_word = asking.delimiter_answer(
            _DELIMITER_SPELLINGS[delimiter_given] if delimiter_given in _DELIMITER_SPELLINGS else ""
        )
        try:
            verdict = _described_once(
                table=table, out_dir=out_dir, smallest_group=smallest_group, floor_chosen=floor_chosen,
                forced_identifiers=_typed_left(forced_identifiers, asking.ANSWER_IDENTIFIER, replaced),
                forced_codes=_typed_left(forced_codes, asking.ANSWER_CODE, replaced),
                forced_measurements=_typed_left(forced_measurements, asking.ANSWER_MEASUREMENT, replaced),
                forced_decimal_commas=_typed_left(forced_decimal_commas, asking.ANSWER_DECIMAL_COMMA, replaced),
                answers_path=f"{questions}", kept_values=kept_values, missing_values=missing_values,
                first_row=first_row if first_row_left else _FIRST_ROW_AUTOMATIC,
                day_first=day_first and (asking.DAY_FIRST_SUBJECT, asking.ANSWER_DAY_FIRST) not in replaced,
                sheet=sheet, metadata_rows_given=metadata_rows_given,
                delimiter_given=delimiter_given if (asking.DELIMITER_SUBJECT, delimiter_word) not in replaced else "",
                date_counts_given=[
                    pair for pair in date_counts_given or []
                    if len(pair) != 2 or (f"{pair[0]}", f"{pair[1]}") not in replaced
                ],
                forced_twelve_hours=_typed_left(forced_twelve_hours, asking.ANSWER_TWELVE_HOUR, replaced),
                centuries_given=[one for one in centuries_given or [] if _century_left(one, replaced)],
                date_columns_given=_typed_left(date_columns_given, asking.ANSWER_DATES, replaced),
                first_row_typed=first_row_typed and first_row_left,
                small_tables_refused=small_tables_refused, replace=replace,
                chain=_switch_of_a_later_round(chain),
            )
        except (errors.ProfileError, PathValidationError) as error:
            # A refusal raised from below, said as the command says one, and
            # then that the files the rounds before wrote stand.
            refused = error
            verdict = results.REFUSED
        finally:
            session.screen, session.ask = screen, asking_now
            session.subject_reader = None
            # A write the description began and could not finish names what
            # is on disk itself (`_stopped_writing`); any other stop wrote
            # nothing, and the questions file goes back to what it held --
            # BUT WHERE THE RECORD OF EARLIER DESCRIPTIONS REFUSED THE ROUND'S
            # DESCRIPTION in words that ask for --replace-description, the
            # answers given since stay in it, for the command that applies
            # them (Codex's review of batch 4u, item 7: they were erased).
            stopped_writing = bool(session.on_disk)
            kept_answers = (
                verdict != results.NO_MISS
                and refused is None
                and not stopped_writing
                and session.round_refused_by_record
            )
            if verdict != results.NO_MISS and not stopped_writing and not kept_answers:
                _questions_written_back(questions, kept_text, guards)
                session.typed_replaced = _typed_replaced_in(questions, typed)
        if session.ended_at_subject:
            # ENDING INPUT AT THE SUBJECT QUESTION keeps the files the rounds
            # before wrote, as ending it at any later question does (R7).
            session.files, session.warnings, session.left_behind = before
            session.refusal_words = session.refusal_words[:said_before]
            session.step, session.phase, session.key = where_before
            verdict = results.NO_MISS
            _ended_said()
            break
        if refused is not None:
            if isinstance(refused, errors.KeyedRefusal):
                session.key = refused.key
            captured += [(_ERR, parsing.visible_lines(f"{_shown(refused)}") + "\n")]
            session.refusal_words += [parsing.visible_lines(f"{_shown(refused)}")]
        if verdict != results.NO_MISS:
            session.files, session.warnings, session.left_behind = (
                before[0] + session.files, before[1] + session.warnings, before[2] + session.left_behind
            )
            session.refusal_words = session.refusal_words[:said_before] + [
                _after_the_files(one) for one in session.refusal_words[said_before:]
            ]
        else:
            for record, _answer in answered:
                _answer_stands(_answer, (record.column, record.role, record.reason))
        _described_again(captured, verdict, seen, None if stopped_writing else questions, kept_answers)
        rounds = rounds + 1
    if verdict != results.NO_MISS:
        return verdict
    _records_put(put)
    session.rounds_follow = False
    session.typed_replaced = _typed_replaced_in(_questions_written(), typed)
    _still_open_said()
    if session.closing:
        _teach(session.closing)
    return verdict


def _run_profile_body(
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
    first_row_typed: bool = False,
    chain_state: "_ChainState | None" = None,
    small_tables_refused: bool = True,
    replace: bool = False,
) -> str:
    """Do the work of `synthtwin profile`; return the exit code.

    ``small_tables_refused`` is `main`'s internal parameter of the same name
    (plan P4-D425): no command-line option sets it. ``replace`` is
    `--replace` (lane TT, plan P4-D460): without it, and without
    `--answers`, a file already at one of the run's names is refused
    before the table is read (`_profile_outputs_taken`).

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
        return results.UNUSABLE
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
            return results.UNUSABLE
        if counted_name in counted and counted[counted_name] != counted_member:
            _warn(errors.column_declared_twice(counted_name))
            return results.UNUSABLE
        counted[counted_name] = counted_member
    typed_counted = dict(counted)
    # THE SEVENTH DECLARATION (landing T1, plan P4-D370): the columns
    # named 12-hour clocks written without AM or PM.
    twelve_hours = sorted(
        {one: 1 for one in (forced_twelve_hours or [])}
    )
    # -- 3b.R2c (P4-D383): THE COLUMNS SAID TO HOLD DATES (question Q6).
    date_columns = sorted({one: 1 for one in (date_columns_given or [])})
    # -- lane TR (P4-D473): THE COLUMNS SAID TO HOLD CLOCK TIMES WRITTEN AS
    # FIGURES (Q-CLOCK's answer `clock-figures`; rule 5c).
    clock_figures: "list[str]" = []
    # -- lane NOTES (P4-D481): THE COLUMNS OF SENTENCES ANSWERED `text`, which
    # declare nothing and are carried so their question is not put again.
    sentences_text: "list[str]" = []
    # THE CENTURIES OF TWO-FIGURE YEARS (landing R2a, question Q5): each
    # `--century COLUMN=YEAR`, refused before the table is opened where it
    # is not that, and the window that stands where nothing was said
    # (1969) taken as no declaration at all.
    centuries: "dict[str, int]" = {}
    # ...AND THE STANDING WINDOW TYPED all the same (plan P4-D408, third
    # round; Codex's review of lane AQ, item 3): it declares nothing, but
    # it is a statement about the column -- it replaces a window an earlier
    # run kept, and it is kept as the answer that names the standing
    # window, as an answered question Q5 is. Dropped here before, a kept
    # `--century event_date=1930` survived `--century event_date=1969`, and
    # `01/02/40` read 1940 where the person had asked for 2040. A window
    # nobody typed is still not stored.
    centuries_reset: "list[str]" = []
    for typed_century in centuries_given or []:
        found_century = _century_given(typed_century)
        if found_century is None:
            _warn(errors.century_not_supported(_shown(typed_century)))
            return results.UNUSABLE
        if found_century[1] in parsing.CENTURY_WINDOW_YEARS:
            centuries[found_century[0]] = found_century[1]
            centuries_reset = [
                one for one in centuries_reset if one != found_century[0]
            ]
        else:
            if found_century[0] in centuries:
                del centuries[found_century[0]]
            if found_century[0] not in centuries_reset:
                centuries_reset += [found_century[0]]

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
            return results.UNUSABLE
        metadata_rows = int(metadata_rows_given)

    # WHICH CHARACTER SEPARATES THE COLUMNS, WHERE THE PERSON SAID (plan
    # P4-D110, review item CODEX-4). Refused before the table is opened
    # where it is not one of the four this format reads.
    declared_delimiter = ""
    if delimiter_given:
        if delimiter_given not in _DELIMITER_SPELLINGS:
            _warn(errors.delimiter_not_supported(_shown(delimiter_given)))
            return results.UNUSABLE
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
    # ...and the columns whose question Q-UNIT the file answered `keep`
    # (plan P4-D438): nothing is declared, and Q-UNIT is not put again.
    units_kept: "list[str]" = []
    # ...and those whose question Q-COMMA the file answered `keep` (plan
    # P4-D443): nothing is declared, and Q-COMMA is not put again.
    commas_kept: "list[str]" = []
    # -- lane KV (P4-D487): the value columns answered `keyed` and `keep` to
    # question Q-KEYED; `keep` describes the column as one column, and
    # neither is put the question again.
    values_keyed: "list[str]" = []
    values_kept_whole: "list[str]" = []
    # ...and the columns whose question offering `identifier` the file
    # answered `keep` (plan P4-D401): nothing is declared, and their
    # values are published as their reading publishes them.
    identities_kept: "tuple[str, ...]" = ()
    # ...and the columns whose entry offering `identifier` the file left
    # blank under that reading (plan P4-D445): held as record numbers
    # until answered, a checklist entry's column among them.
    identities_held: "tuple[str, ...]" = ()
    # ...and the answers an earlier run kept that still stand, each set
    # against the section this run writes, and the answers the file gave
    # about the rows under the column names and the windows that stand
    # (plan P4-D408).
    carried_answers: "tuple[tuple[str, str, str], ...]" = ()
    identities_kept_answered: "tuple[str, ...]" = ()
    # ...and of those, the columns whose own question of a key beside a
    # person was answered `keep` (lane ID-ROOM4, plan P4-D489): only such
    # a `keep` releases that question's column (`asking.
    # kept_beside_own_questions`).
    people_keys_kept: "tuple[str, ...]" = ()
    # ...and the columns the file answered `no` to the Safe Harbor
    # question (plan P4-D427): read without the top-code, or no longer
    # held for their five figures.
    safe_harbor_no: "list[str]" = []
    safe_harbor_yes: "list[str]" = []
    # ...and the unit each age column was answered with (plan P4-D454).
    ages_counted_in: "tuple[tuple[str, str], ...]" = ()
    # -- P4-D446: the answers to the question about values that read as
    # dates, kept apart from the age or ZIP question's (the orchestrator's
    # LANE CZ-H RULINGS 6 (1), item 3).
    safe_harbor_dates_no: "list[str]" = []
    safe_harbor_dates_yes: "list[str]" = []
    # ...and the columns read as five-figure numbers beside a few words,
    # as the latest description found them (plan P4-D427).
    five_figures: "list[str]" = []
    # ...and the columns of ages whose top-code would make some of their
    # cells missing (90 is one of their missing values), held whole
    # instead (plan P4-D427).
    ages_held: "list[str]" = []
    # ...and the columns held for lane SH2's reasons, each with its own
    # (plan P4-D434), and the year the Safe Harbor years are judged
    # against: this release's (synthtwin reads no clock), written into the
    # blocks it top-codes, so generation and validation read the
    # description.
    harbor_reasons: "dict[str, str]" = {}
    # ...and what establishes each top-coded column as ages beside its
    # values (lane SH3's repair, plan P4-D454): the question's units and
    # the meaning of `yes` follow it.
    ages_established: "dict[str, str]" = {}
    harbor_year = taxonomy.SAFE_HARBOR_REFERENCE_YEAR
    # ...and the column names the file's answers use, with the columns
    # those answers name, set against the names this run reads (plan
    # P4-D408).
    answered_under: "tuple[str, ...] | None" = None
    names_by_answer: "list[str]" = []
    metadata_answer = ""
    centuries_kept: "list[str]" = []
    if answers_path is not None:
        try:
            handed_back = _answers_loaded(answers_path)
            # ...and, behind the chain's switch alone, the pairs its entry
            # asks to add or drop (lane CHa, repair 2, Codex's item 6).
            if chain_state is not None:
                (
                    chain_state.add,
                    chain_state.drop,
                    chain_state.unread,
                ) = asking.between_columns_requests(handed_back)
                # ...and the subject question's answer (lane GRa, plan
                # P4-D449): a column it names is declared as record numbers.
                (
                    chain_state.rows_answer,
                    chain_state.person_named,
                ) = asking.rows_per_person_answer(handed_back)
                # ...and the person question's two readings it kept.
                (
                    chain_state.persons_said,
                    chain_state.records_said,
                ) = asking.columns_said(handed_back)
            # HOW THE RUN THAT WROTE THE FILE READ THE TABLE, before
            # anything typed now takes a kept answer out (plan P4-D408).
            kept_reading = asking.kept_reading(handed_back)
            # ...and the column names its answers use (plan P4-D408).
            answered_under = asking.columns_answered_under(handed_back)
            written = asking.answers_in(
                # LESS THE KEPT ANSWERS THIS COMMAND LINE REPLACES: a
                # declaration typed now is later than any answer an
                # earlier run kept (plan P4-D408).
                asking.typed_over_kept(
                    handed_back,
                    _typed_answers(
                        typed_codes, typed_identifiers, typed_measurements,
                        typed_commas, twelve_hours, typed_counted, centuries,
                        date_columns, day_first, declared_delimiter,
                        first_row, centuries_reset, first_row_typed,
                    ),
                ),
                _shown(answers_path),
            )
        except ValueError as error:
            _warn(_shown(f"{error}"))
            return results.UNUSABLE
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
            written, first_row, declared_delimiter, kept_reading
        )
        # ...AND A READING OTHER THAN THE ONE THE FILE WAS WRITTEN UNDER
        # (plan P4-D408): a kept answer about how the file is read,
        # edited in the file or replaced by a typed option.
        # `--first-row auto` typed over a kept answer about the first row
        # (Codex's review of lane AQ, item 3) reads the table as a run
        # given no answer reads it; where the file lists the names its
        # answers use, whether that moved a name is told after the read,
        # by those names (`_answered_under_other_names`).
        kept_changed = _kept_reading_changed(
            written, first_row, declared_delimiter, kept_reading,
            automatic=(
                first_row_typed
                and first_row == _FIRST_ROW_AUTOMATIC
                and answered_under is not None
            ),
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
            # ...and the columns answered `keep` to Q-UNIT (plan P4-D438).
            + list(written.units_kept)
            # ...and the columns answered `keep` to Q-COMMA (plan P4-D443).
            + list(written.commas_kept)
            # -- lane KV (P4-D487): ...and to Q-KEYED, either way.
            + list(written.values_keyed)
            + list(written.values_kept_whole)
            # ...and the columns answered `no` or `yes` to the Safe Harbor
            # question (plan P4-D427; Codex's review of lane SH, item 7):
            # an answer beside a correction of the reading is refused, as
            # every other answer naming a column is, never dropped.
            + list(written.safe_harbor_no)
            + list(written.safe_harbor_yes)
            + list(written.safe_harbor_dates_no)
            + list(written.safe_harbor_dates_yes)
            # ...and every column an earlier run's answer kept (plan
            # P4-D408): its name is the name under the reading that run
            # took, which an answer changing the reading moves.
            + [
                one_name
                for one_name, _answer, family in written.carried
                if family not in asking.FILE_FAMILIES
            ]
            # ...and, behind the chain's switch, the column the subject
            # question's answer names (lane GRa, plan P4-D449; Codex's
            # review, item 3): it declares that column as record numbers,
            # by its name under the reading that wrote the file, so it is
            # bound by every check an `identifier` answer is bound by.
            + _subject_named(chain_state)
        ):
            # Each name once: a column answered in both sections of the
            # file would otherwise stand twice in one sentence.
            if one not in named_columns:
                named_columns += [one]
        if kept_changed and named_columns:
            _warn(
                _kept_reading_not_kept(
                    _shown(answers_path), kept_changed,
                    [_shown(one) for one in sorted(named_columns)],
                )
            )
            return results.UNUSABLE
        reading_changed += [
            one for one in kept_changed if one not in reading_changed
        ]
        if reading_changed and named_columns:
            _warn(
                errors.answers_change_the_reading_and_name_columns(
                    _shown(answers_path), reading_changed,
                    sorted(named_columns),
                )
            )
            return results.UNUSABLE
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
        # A COMMA KEPT ON ITS OWN SAYS ONLY HOW THE NUMBERS ARE WRITTEN
        # (plan P4-D408, third round), so a typed declaration of what the
        # column holds stands beside it; an answer to the question of a
        # point between thousands decides both, and replaces it as before.
        # ...and, behind the chain's switch, the person question's two
        # readings of `identifier` (lane GRa, RULINGS 1 (1)).
        if chain_state is not None:
            chain_state.persons_said = tuple(
                sorted(
                    (set(chain_state.persons_said) - set(written.records_said))
                    | set(written.persons_said)
                )
            )
            chain_state.records_said = tuple(
                sorted(
                    (set(chain_state.records_said) - set(written.persons_said))
                    | set(written.records_said)
                )
            )
        held_by_answer = (
            list(written.codes)
            + list(written.identifiers)
            + list(written.measurements)
            # ...and the column the subject question's answer names, the
            # newer statement in the ordinary way (Codex's review of lane
            # GRa, item 4): it replaces a typed `--date-count`, `--code` or
            # `--measurement` for its column as an `identifier` answer does.
            + _subject_named(chain_state)
        )
        spoken_for = held_by_answer + [
            one
            for one in written.decimal_commas
            if one not in written.decimal_commas_alone
        ]
        forced_codes = sorted(
            [one for one in forced_codes if one not in spoken_for]
            + list(written.codes)
        )
        forced_identifiers = sorted(
            [one for one in forced_identifiers if one not in spoken_for]
            + list(written.identifiers)
        )
        # ...AND, BEHIND THE CHAIN'S SWITCH ALONE, THE COLUMN THE SUBJECT
        # QUESTION'S ANSWER NAMES (lane GRa, plan P4-D449): declared as
        # record numbers, so that where it repeats it is the person column.
        for one in _subject_named(chain_state):
            if one not in forced_identifiers:
                forced_identifiers = sorted(forced_identifiers + [one])
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
        # -- lane TR (P4-D473): ...and an answer of `clock-figures`.
        clock_figures = sorted(
            {one: 1 for one in clock_figures + list(written.clock_figures)}
        )
        # -- lane NOTES (P4-D481): ...and a column of sentences answered `text`.
        sentences_text = list(written.sentences_text)
        names_by_answer += sentences_text
        # ...and those answered `keep`, carried so Q6 is not put again.
        dates_kept = list(written.date_columns_kept)
        # ...and Q-UNIT's `keep`, carried so Q-UNIT is not put again (plan
        # P4-D438; the orchestrator's LANE UN-1a RULINGS 1 (2)).
        units_kept = list(written.units_kept)
        # ...and Q-COMMA's `keep`, carried so Q-COMMA is not put again (plan
        # P4-D443).
        commas_kept = list(written.commas_kept)
        # -- lane KV (P4-D487): ...and Q-KEYED's answers, carried so it is
        # not put again; `keep` reads the column as one column.
        values_keyed = list(written.values_keyed)
        values_kept_whole = list(written.values_kept_whole)
        # ...and the columns answered `keep` to a question offering
        # `identifier` (plan P4-D401). Under an answer that changes the
        # reading a name may land on another column, so there such a
        # `keep` holds nothing back from the hold below: the column is
        # asked again under the reading in force.
        if not reading_changed:
            identities_kept = written.identities_kept
            identities_kept_answered = written.identities_kept_answered
            people_keys_kept = written.people_keys_kept
            identities_held = written.identities_held
            names_by_answer += named_columns
            names_by_answer += list(identities_kept_answered)
            safe_harbor_no = list(written.safe_harbor_no)
            safe_harbor_yes = list(written.safe_harbor_yes)
            ages_counted_in = written.ages_counted_in
            safe_harbor_dates_no = list(written.safe_harbor_dates_no)
            safe_harbor_dates_yes = list(written.safe_harbor_dates_yes)
            names_by_answer += safe_harbor_no + safe_harbor_yes
            names_by_answer += safe_harbor_dates_no + safe_harbor_dates_yes
        carried_answers = written.carried
        if written.metadata_rows_answered:
            metadata_answer = (
                asking.ANSWER_METADATA_ROWS
                if written.metadata_rows
                else asking.ANSWER_DATA
            )
        centuries_kept = list(written.centuries_kept)
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
        # ...and a comma before the decimals is no such answer: it says
        # how numbers are written and stands beside counted dates (plan
        # P4-D408, third round; Codex's review of lane AQ, item 2). Typed
        # with `--date-count visit excel-1900` and handed back unchanged,
        # the kept comma deleted the dates here and the run refused.
        for counted_name in held_by_answer:
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
            or bool(written.clock_figures)
        )
    # THE STANDING WINDOW TYPED IS KEPT AS AN ANSWER NAMING IT (plan
    # P4-D408, third round): it declares nothing, and question Q5 is not
    # put again for its column, as for the answer `1969-2068`. A window
    # the questions file answered for the column is the newer statement.
    for one_century in centuries_reset:
        if one_century in centuries or one_century in answered_centuries:
            continue
        centuries_kept += [one_century]
        answered_centuries += [one_century]
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
            return results.UNUSABLE

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
        return results.UNUSABLE
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
        # -- lane TR (P4-D473)
        forced_clock_figures=tuple(clock_figures),
    )
    # THE ONE OVERWRITE RULE (lane TT, plan P4-D460), decided from the
    # names alone, before a byte of the table is read: a run that would
    # write over a file already at one of its names stops and changes
    # nothing, in the words `generate` and `validate` use, unless the
    # command line says so -- `--replace`, as on every command, or
    # `--answers`, the round that hands back an earlier run's questions to
    # describe the same table again, which writes over that round's files
    # as it always has (the stage-5 battery's G7).
    if not replace and answers_path is None:
        try:
            names_written, names_taken = _profile_outputs_taken(table, out_dir)
        except errors.ProfileError as error:
            _warn(_shown(error), step=results.STEP_OUTPUTS)
            return results.REFUSED
        if names_taken:
            _warn(
                errors.outputs_taken(
                    names_written, names_taken, errors.DESCRIBING_AGAIN
                ),
                step=results.STEP_OUTPUTS,
            )
            return results.REFUSED
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
        # ONE GROUP OF COLUMNS AT A TIME where the table is large (lane
        # SR, plan P4-D400): its text is never held whole, and every
        # step below asks its columns of `reading.column_values`.
        in_groups=True,
    )
    # THE ANSWERS A TWIN KEEPS ARE BOUND TO THE FILE THEY WERE GIVEN ABOUT
    # (lane TT's repair; the orchestrator's LANE TT RULINGS 1 item 4,
    # Codex's item 4), decided from this one reading: a twin's profile step
    # handed its folder's own questions file reads the file those answers
    # name -- its size, fingerprint and sheet -- or stops here, having
    # written nothing (measured on c4925cd8: answers given about one table
    # decided the reading of another of the same name in the same folder).
    # And every twin's profile step binds the answers it keeps to its own
    # reading, in a sentence of its questions file (`_bound_reading`).
    reading_now = _current()
    if reading_now is not None and reading_now.twin_step:
        bound = (
            read.file_bytes,
            read.fingerprint,
            read.book.chosen if read.book is not None else "",
        )
        if reading_now.bound_to is not None and reading_now.bound_to != bound:
            kept_at = _shown(answers_path)
            _warn(
                errors.twin_answers_about_another_table(
                    kept_at, _shown(pathlib.Path(f"{answers_path}").parent)
                ),
                step=results.STEP_INPUT,
            )
            return results.REFUSED
        reading_now.binding = _binding_sentence(
            bound, smallest_group, len(typed_missing), len(typed_kept)
        )
    # FROM HERE A REFUSAL IS ABOUT WHAT THE TABLE HOLDS (plan P4-D395:
    # the step a run's result names).
    _at(results.STEP_CONTENT)

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
        return results.UNUSABLE

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
        return results.UNUSABLE

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
        return results.UNUSABLE

    unknown_twelve = [
        name for name in twelve_hours if name not in read.column_names
    ]
    if unknown_twelve:
        _warn(
            errors.unknown_column_named(
                "as a 12-hour clock", unknown_twelve[0], read.column_names
            )
        )
        return results.UNUSABLE
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
        return results.UNUSABLE

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
        return results.UNUSABLE

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
        return results.UNUSABLE
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
        return results.UNUSABLE
    for name in sorted(counted):
        if (
            name in forced_codes
            or name in forced_identifiers
            or name in forced_measurements
            or name in twelve_hours
        ):
            _warn(errors.column_declared_twice(name))
            return results.UNUSABLE

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
            return results.UNUSABLE
        if name in forced_codes:
            _warn(
                errors.comma_declaration_would_be_ignored(name, "--code")
            )
            return results.UNUSABLE

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
        return results.UNUSABLE

    # NO ANSWER AN EARLIER RUN KEPT IS DROPPED IN SILENCE (plan P4-D408).
    # Each still standing must reach the file this run writes, where the
    # next run reads it again; one naming a column this table does not
    # hold, or one another answer here contradicts, is refused in plain
    # words before anything is written -- an `identifier` answer lost
    # between rounds is a person column read as numbers, and a held
    # column's answer lost is the hold put back on it without a word.
    # ...AND NO ANSWER MADE BY NAME UNDER OTHER NAMES (plan P4-D408): the
    # file lists the names its answers use, and a run reading the table
    # under other names -- a kept answer about how the file is read
    # deleted, or another table -- would put each answer on a column the
    # person was not looking at. Measured: the kept `names` deleted, 200
    # of 200 real subject codes published.
    if (
        answered_under is not None
        and names_by_answer
        and tuple(read.column_names) != answered_under
    ):
        _warn(_answered_under_other_names(_shown(f"{answers_path}")))
        return results.UNUSABLE
    if carried_answers:
        not_kept = _earlier_answers_dropped(
            carried_answers,
            read.column_names,
            _answers_given(
                read.column_names, forced_codes, forced_identifiers,
                forced_measurements, forced_decimal_commas, twelve_hours,
                counted, centuries, centuries_kept, date_columns,
                dates_kept, identities_kept_answered,
                answered_missing_dates, answered_real_values,
                answered_code_shapes, first_row, metadata_answer,
                declared_delimiter, day_first, answered_month_first,
                tuple(safe_harbor_no), tuple(safe_harbor_yes),
                tuple(units_kept), tuple(commas_kept), ages_counted_in,
                tuple(safe_harbor_dates_no), tuple(safe_harbor_dates_yes),
                tuple(clock_figures), tuple(sentences_text),
                people_keys_kept=people_keys_kept,
                values_keyed=tuple(values_keyed), values_kept_whole=tuple(values_kept_whole),
            ),
        )
        if not_kept:
            _warn(
                _earlier_answers_not_kept(
                    _shown(f"{answers_path}"), [_shown(one) for one in not_kept]
                )
            )
            return results.UNUSABLE
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
        return results.UNUSABLE
    added_missing: "list[str]" = []
    added_kept: "list[str]" = []
    kept_code_shapes: "dict[str, str]" = dict(answered_code_shapes)
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
            reading.column_values(read, column_at),
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
                ),
                caution=results.CAUTION_ANSWER_LEFT_WORDS,
                column=name,
            )
        if seen is None:
            _warn(
                errors.the_date_codes_answer_reached_nothing(name),
                caution=results.CAUTION_ANSWER_REACHED_NOTHING,
                column=name,
            )
            continue
        # ...and the file this run writes keeps the answer by the codes
        # found here, which every round finds alike (plan P4-D408), and
        # not by the words of the question it answered, which count the
        # cells the reading of that round read.
        kept_code_shapes[name] = asking.kept_codes_saw(seen)
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
                return results.UNUSABLE
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
            return results.UNUSABLE
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
    person_columns, population, unit, census_readings, held_rows, floor_people = (
        _population_settled(
            chain_state,
            read,
            settings,
            forced_identifiers,
            forced_codes,
            forced_measurements,
            forced_decimal_commas,
            storage,
        )
    )
    # THE OWNER'S TABLE FLOOR (plan P4-D425), asked before today's
    # population floor, which it is above: no twin of a small table.
    if small_tables_refused and _below_the_table_floor(
        held_rows, person_columns, floor_people
    ):
        _warn(
            errors.the_table_is_below_the_floor(
                held_rows,
                floor_people if person_columns else 0,
                _joined(list(person_columns), " and "),
                settings.small_cell_floor,
            )
        )
        return results.REFUSED
    if population < parsing.POPULATION_FLOOR:
        _warn(
            errors.the_population_is_too_small(
                population, unit, _joined(list(person_columns), " and ")
            )
        )
        return results.REFUSED
    settings = dataclasses.replace(settings, person_columns=person_columns)
    population_notes = profile.notes_for_a_small_population(
        population, unit, parsing.POPULATION_NOTICE_LINE
    )

    # A reading of a table read in groups is not handed over (lane SR,
    # plan P4-D400): the description is handed its columns again, read
    # again, and the reading would only be held beside them.
    census_box = [census_readings if read.source is None else ()]
    census_readings = ()
    # The columns whose values the count in people changed (plan
    # P4-D406), named on the screen.
    counted_in_people: "list[str]" = []
    counted_in_rows: "list[str]" = []
    few_valued: "list[str]" = []
    # -- P4-D440, rule U (c): the columns whose released list names a
    # value fewer cells than the floor hold, named for the check below.
    rare_listed: "list[str]" = []
    # -- P4-D471 (lane CODES-2): the label columns whose `no` would name their
    # held-back levels, for their Safe Harbor question; and the columns that
    # name them, for rule U (c) as the two lists above.
    rare_named: "list[str]" = []
    names_published: "list[str]" = []
    # -- P4-D453: the columns whose pool is counted in people, named for the
    # same check: their levels wait while a question offering `identifier`
    # is open on the table.
    levels_pooled: "list[str]" = []
    # -- P4-D446: the columns holding dates in disguise, named for their
    # Safe Harbor question; those no question holds whole are written with
    # those values read as blank cells.
    dated_values: "list[str]" = []
    # -- P4-D487 (lane KV): the pairs the describe reads as keyed, for
    # question Q-KEYED; the value columns answered `keep` are not keyed.
    keyed_found: "list[profile.KeyedPair]" = []
    keyed_named: "list[str]" = []
    document = profile.build_document(
        read,
        settings,
        forced_identifiers,
        forced_codes,
        forced_measurements,
        forced_decimal_commas,
        forced_metadata_rows=metadata_rows,
        forced_delimiter=declared_delimiter,
        # Record numbers with a check digit (`1002345,7`) are read with
        # their comma only once P4-D401's question is answered `keep`
        # (plan P4-D443, repair 2 of lane UN-1b).
        kept_identities=list(identities_kept),
        table_notes=population_notes,
        # HANDED OVER IN A BOX (lane S4d, plan P4-D390): the description
        # takes the readings out of the box in its own frame, so it
        # holds each column's census reading alone and lets it go once
        # that column is described, rather than this frame keeping every
        # one alive until the whole table is. The box itself is the
        # argument (lane CF4b): an argument is held by the caller until
        # the call returns on CPython 3.10, so the readings handed over
        # as one lived through the whole description there.
        readings_box=census_box,
        stored_as=storage,
        # -- P4-D406: every value counted in the declared people too.
        subjects=list(person_columns),
        counted_in_subjects=counted_in_people,
        # -- P4-D427: the Safe Harbor top-code, but where answered `no`,
        # and the five-figure columns beside a few words, named.
        top_code=True,
        safe_harbor_no=safe_harbor_no,
        ages_counted_in=_marks_answered(ages_counted_in),
        five_figures=five_figures,
        ages_held=ages_held,
        counted_in_rows=counted_in_rows,
        # -- P4-D440: the few-valued columns with a wide gap, named for
        # their Safe Harbor question, listed where it was answered `no`.
        few_valued=few_valued,
        rare_listed=rare_listed,
        rare_named=rare_named,
        names_published=names_published,
        # -- P4-D434: the Safe Harbor years, places and devices.
        harbor_year=harbor_year,
        harbor_reasons=harbor_reasons,
        levels_pooled=levels_pooled,
        ages_established=ages_established,
        dated_values=dated_values,
        dated_values_no=safe_harbor_dates_no,
        dates_answered=tuple(answered_missing_dates + answered_real_values),
        # The description's own readings kept for the chain (lane CHs,
        # plan P4-D462): only behind the chain's switch.
        kept_spellings=chain_state.kept if chain_state is not None else None,
        keyed_kept=list(values_kept_whole),
        keyed_found=keyed_found,
        # ...a value column's `yes` to EITHER question carrying the keyed
        # clause -- its Safe Harbor question and its question about values
        # that read as dates, both asking whether a value could name a
        # person -- holds what the clause lists whatever the other was
        # answered: ANY YES HOLDS (the orchestrator's LANE KV RULINGS 6 (1)).
        keyed_yes=list(safe_harbor_yes) + list(safe_harbor_dates_yes),
        keyed_named=keyed_named,
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
                ),
                caution=results.CAUTION_DECLARATION_DID_NOT_REACH,
                column=name,
            )
    # -- 3b.R4 (P4-D384): ...AND A COLUMN DECLARED TO WRITE ITS DATES AS
    # COUNTS WHOSE CELLS DID NOT READ AS SUCH DATES, said here as the
    # description says it: held, on every table (plan P4-D406, NF127),
    # chosen by its evidence and never by its role, which the count in
    # people (NF126) sets to `identifier` for a column read as dates.
    for name in sorted(counted):
        for described_column in _described_columns(document):
            if described_column["name"] != name:
                continue
            if not _held_as_counted_dates(described_column):
                continue
            _warn(
                errors.the_date_count_declaration_did_not_reach(
                    name, counted[name]
                ),
                caution=results.CAUTION_DECLARATION_DID_NOT_REACH,
                column=name,
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
                reading.column_values(read, column_at)
            ):
                _warn(
                    errors.the_twelve_hour_style_was_held_back(name),
                    caution=results.CAUTION_DECLARATION_DID_NOT_REACH,
                    column=name,
                )
                continue
            # A LAYOUT COLUMN READ IN PART is a time of day without a
            # marker the partial reader takes on the 24-hour clock alone
            # (the Codex review of landing I3a, item 2), said so.
            if asking.layout_read_in_part(described_column) and parsing.layout_asks_twelve_hours(
                f"{described_column['format']}"
            ):
                _warn(
                    errors.the_twelve_hour_declaration_did_not_reach_in_part(name),
                    caution=results.CAUTION_DECLARATION_DID_NOT_REACH,
                    column=name,
                )
                continue
            _warn(
                errors.the_twelve_hour_declaration_did_not_reach(
                    name, f"{described_column['role']}"
                ),
                caution=results.CAUTION_DECLARATION_DID_NOT_REACH,
                column=name,
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
                ),
                caution=results.CAUTION_DECLARATION_DID_NOT_REACH,
                column=name,
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
                ),
                caution=results.CAUTION_DECLARATION_DID_NOT_REACH,
                column=name,
            )
    # -- lane TR (P4-D473): ...AND A `clock-figures` ANSWER THAT WOULD WRITE
    # A MISSING SPELLING, which is not taken (Codex's review of lane TR,
    # item 2), said here.
    _figures_not_taken_said(clock_figures, read, settings)

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
        # -- P4-D434: a column of dates lane SH2 holds is put the Safe
        # Harbor question and nothing else, one question a column (its
        # held block reads as no dates, so question Q6 would ask whether
        # it holds dates).
        + [name for name in harbor_reasons if harbor_reasons[name] == taxonomy.HELD_DATES]
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
    # A column whose codes were answered `real-value` is asked no
    # question of what kind its values are either: the answer kept its
    # codes, and the joined question is no more the column's for that.
    # Its checklist line as a measurement stands (`checklist_for`).
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
    # EVERY COLUMN READ AS A NUMBER, LISTED UNDER ONE QUESTION
    # (owner ruling 2026-09-10, amendment A-P4-58). The questions
    # above are the columns whose VALUES raised a question; these
    # are the ones no rule can reach, because a register of concept
    # identifiers and a column of ages are written identically. A
    # person reads one list and names the codes.
    # ALL OF THEM IN ONE WALK OF THE TABLE (lane SR, plan P4-D400): a
    # table read in groups of columns is asked them a group at a time.
    first_questions = profile.questions_of(
        read,
        document,
        settings,
        already_answered,
        tuple(forced_decimal_commas),
        storage,
        None,
        None,
        asking.DateColumnsSeen(),
        False,
        (),
        False,
    )
    # AN ANSWER GIVEN IS NOT ASKED AGAIN (plan P4-D408; the orchestrator's
    # LANE UN-1a RULINGS 1 (2)): Q-UNIT answered `keep` stays answered.
    asked_about = _units_not_asked_again(
        first_questions.asked, units_kept + commas_kept, identities_kept_answered
    )
    # THE PEOPLE'S QUESTION OF A KEY BESIDE A PERSON IS ITS OWN (lane
    # ID-ROOM4, plan P4-D489; skeptic 1's item 1, the orchestrator's LANE
    # ID-ROOM4 RULINGS 4, item 1): a `keep` given to another question --
    # the person question, the truthful answer for a key beside the patient,
    # or Q2 or Q6 -- in this round or an earlier one, releases no column
    # that question holds, so it leaves the answers kept here, and every
    # place below that a kept answer exempts from a hold reads the list
    # without it: the hold of an open question (`unanswered_identities`, at
    # the prompt and after it), a blank under `identifier`, the open person
    # question's candidates, the census places of an open question, the
    # Safe Harbor question's open questions, the questions it is put in
    # place of and those its answer closes, and the chain's describe; the
    # describe's own kept answers read only the comma of record numbers
    # with a check digit, which no such key holds. Only its own answer,
    # here (`answered_here`) or in the file (`Answers.people_keys_kept`),
    # releases it.
    identities_kept = asking.kept_beside_own_questions(
        tuple(identities_kept), asked_about, people_keys_kept
    )
    split_columns = first_questions.split
    codes_seen = first_questions.codes_seen
    seen_of = (
        document,
        settings,
        list(already_answered),
        list(forced_decimal_commas),
    )
    coded_about = list(codes_seen.questions)
    listed_about = first_questions.listed
    answered = False
    # THE QUESTIONS ANSWERED AT THE KEYBOARD, each by its column, role and
    # reason (`asking.question_put`): an answer typed by its key. Enter
    # leaves a question unanswered (`_LEFT_OPEN`), and every question this
    # list does not name -- left open by Enter, or put only in the
    # questions file -- is read below as a run with nobody at the keyboard
    # reads it: whatever nobody's run holds stays held (lane TT's repair;
    # the orchestrator's LANE TT RULINGS 2 (1)). Empty where nobody is
    # asked, so that run reads every question as it always did.
    answered_here: "list[tuple[str, str, str]]" = []
    assumptions_said = False
    if asked_about:
        # ...the questions this prompt puts, or would put, kept for the twin
        # that teaches the answers command (Codex's item 9).
        prompting = _current()
        if prompting is not None and prompting.twin_step:
            prompting.promptable = [asking.question_put(one) for one in asked_about]
        if _there_is_somebody_to_ask():
            given = _put_the_questions(
                asked_about,
                asking.unanswered_identities(
                    asked_about,
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
                ),
            )
            if given is not None:
                _put_at_a_prompt(asked_about)
            if given is None:
                _warn(
                    errors.the_questions_were_not_finished(),
                    step=results.STEP_QUESTIONS,
                )
                return results.REFUSED
            (
                new_codes, new_identifiers, new_measured, new_commas,
                new_twelve, new_counted, left_open, new_figures,
            ) = given
            answered_here = [
                asking.question_put(question)
                for question in asked_about
                if asking.question_put(question) not in left_open
            ]
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
            # -- lane TR (P4-D473): a column answered `clock-figures` at the
            # keyboard is read by rule 5c from here.
            if new_figures:
                clock_figures = sorted(
                    {one: 1 for one in clock_figures + new_figures}
                )
                settings = dataclasses.replace(
                    settings, forced_clock_figures=tuple(clock_figures)
                )
            # ...and a `clock-figures` answer rebuilds the description as
            # the other answers do (Codex's review of lane TR, item 1): left
            # out, the run's own description kept the column as it read
            # before the answer while its questions file recorded the answer,
            # and its twin wrote 9,902 of 20,000 six-figure cells that are no
            # clock time.
            if (
                new_codes
                or new_identifiers
                or new_measured
                or new_commas
                or new_twelve
                or new_counted
                or new_figures
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
                        errors.the_comma_declaration_was_answered_away(named),
                        caution=results.CAUTION_ANSWERED_AWAY,
                        column=named,
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
                (
                    person_columns,
                    population,
                    unit,
                    census_readings,
                    held_rows,
                    floor_people,
                ) = (
                    _population_settled(
                        chain_state,
                        read,
                        settings,
                        forced_identifiers,
                        forced_codes,
                        forced_measurements,
                        forced_decimal_commas,
                        storage,
                    )
                )
                # The table floor again, with the final person columns
                # (plan P4-D425): a column just answered as naming
                # people is where the people floor starts to apply.
                if small_tables_refused and _below_the_table_floor(
                    held_rows, person_columns, floor_people
                ):
                    _warn(
                        errors.the_table_is_below_the_floor(
                            held_rows,
                            floor_people if person_columns else 0,
                            _joined(list(person_columns), " and "),
                            settings.small_cell_floor,
                        )
                    )
                    return results.REFUSED
                if population < parsing.POPULATION_FLOOR:
                    _warn(
                        errors.the_population_is_too_small(
                            population,
                            unit,
                            _joined(list(person_columns), " and "),
                        )
                    )
                    return results.REFUSED
                settings = dataclasses.replace(
                    settings, person_columns=person_columns
                )
                population_notes = profile.notes_for_a_small_population(
                    population, unit, parsing.POPULATION_NOTICE_LINE
                )
                census_box = [census_readings if read.source is None else ()]
                census_readings = ()
                counted_in_people = []
                five_figures = []
                ages_held = []
                counted_in_rows = []
                few_valued = []
                rare_listed = []
                rare_named = []
                names_published = []
                levels_pooled = []
                harbor_reasons = {}
                ages_established = {}
                dated_values = []
                keyed_found = []
                keyed_named = []
                document = profile.build_document(
                    read,
                    settings,
                    forced_identifiers,
                    forced_codes,
                    forced_measurements,
                    forced_decimal_commas,
                    forced_metadata_rows=metadata_rows,
                    forced_delimiter=declared_delimiter,
                    kept_identities=list(identities_kept),
                    table_notes=population_notes,
                    readings_box=census_box,
                    stored_as=storage,
                    subjects=list(person_columns),
                    counted_in_subjects=counted_in_people,
                    top_code=True,
                    safe_harbor_no=safe_harbor_no,
                    ages_counted_in=_marks_answered(ages_counted_in),
                    five_figures=five_figures,
                    ages_held=ages_held,
                    counted_in_rows=counted_in_rows,
                    few_valued=few_valued,
                    rare_listed=rare_listed,
                    rare_named=rare_named,
                    names_published=names_published,
                    harbor_year=harbor_year,
                    harbor_reasons=harbor_reasons,
                    levels_pooled=levels_pooled,
                    ages_established=ages_established,
                    dated_values=dated_values,
                    dated_values_no=safe_harbor_dates_no,
                    dates_answered=tuple(answered_missing_dates + answered_real_values),
                    # The description's own readings kept for the chain (lane CHs,
                    # plan P4-D462): only behind the chain's switch.
                    kept_spellings=chain_state.kept if chain_state is not None else None,
                    keyed_kept=list(values_kept_whole),
                    keyed_found=keyed_found,
                    keyed_yes=list(safe_harbor_yes) + list(safe_harbor_dates_yes),
                    keyed_named=keyed_named,
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
                            ),
                            caution=results.CAUTION_DECLARATION_DID_NOT_REACH,
                            column=name,
                        )
                # -- lane TR (P4-D473): ...and a `clock-figures` answer typed
                # here that is not taken (Codex's review of lane TR, item 2).
                _figures_not_taken_said(sorted(new_figures), read, settings)
            answered = True
        else:
            _say(f"\n{_assumptions_notice(asked_about, small_tables_refused)}\n")
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
    # ...LESS THE COLUMNS SYNTHTWIN'S OWN MADE-UP SPELLINGS WOULD WRITE AS
    # REAL VALUES (lane ID-ROOM4, plan P4-D489): numbers too large or too
    # small to hold whose writer spells, from fixed counters, a value 1 to
    # f-1 people hold are spelled one letter or figure wider whatever the
    # answer (`_made_up_spellings_held`; method G10.5 step 8), so they are
    # no measurement to list; read again on the description written,
    # below. THE HOLDERS ARE COUNTED IN THE SUBJECTS THE DESCRIPTION IS
    # COUNTED IN (skeptic 1 of lane ID-ROOM4, item 2; the orchestrator's
    # LANE ID-ROOM4 RULINGS 4, item 2): here the person columns and every
    # column an open question offering `identifier` still names, the most
    # the final describe can count in (a code on twenty rows of one person
    # was copied while the person question was open, counted in rows).
    early_subjects = list(person_columns) + [
        question.name
        for question in asked_about
        if asking.question_put(question) not in answered_here
        and asking.offers_identifier(question)
        and question.name not in person_columns
        and question.name not in forced_identifiers + forced_codes + forced_measurements
        and question.name not in forced_decimal_commas
        and question.name not in identities_kept
    ]
    # ...and a column whose spellings cannot be made at all is held whole as
    # record numbers (Codex's review of lane ID-ROOM4, item 1).
    spelled_held, spelled_unmade = _made_up_spellings_held(read, document, settings, early_subjects)
    listed_about = [question for question in listed_about if question.name not in spelled_held]
    if listed_about:
        _say(f"\n{_checklist_notice(listed_about)}\n")
    # ...AND THE TWO QUESTIONS ABOUT DATES, ONCE PER RUN AND WHOEVER IS
    # THERE (plan P4-D381), for the checklist's reason: each is put in
    # the questions file, and a run whose only finding is one of them
    # would otherwise show nothing.
    settled = forced_identifiers + forced_codes + forced_measurements + [
        name for name in harbor_reasons if harbor_reasons[name] == taxonomy.HELD_DATES
    ]
    codes_moved = not (
        document is seen_of[0]
        and settings == seen_of[1]
        and settled == seen_of[2]
        and list(forced_decimal_commas) == seen_of[3]
    )
    # THE DATE QUESTIONS BELOW ARE WORKED OUT IN ONE WALK OF THE TABLE
    # (lane SR, plan P4-D400) -- the codes question again where the
    # interview moved what it reads, question Q6, and the day-or-month
    # question -- and said in the order they always were.
    day_or_month: "tuple[asking.DayOrMonth, ...]" = ()
    codes_seen, dates_seen, day_or_month = profile.dated_questions_of(
        read,
        document,
        settings,
        split_columns,
        None if codes_moved else codes_seen,
        settled,
        settled + date_columns + dates_kept,
        not answered_month_first,
        tuple(forced_decimal_commas),
        storage,
    )
    if codes_moved:
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
            ),
            caution=results.CAUTION_SMALL_POPULATION,
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
    if person_asked and not person_columns and not assumptions_said and not _persons_given():
        _warn(
            _counted_in_rows_notice(person_asked, small_tables_refused),
            caution=results.CAUTION_COUNTED_IN_ROWS,
        )
    _rows_counted_beside(person_asked, person_columns)

    # NO VALUE OF A COLUMN WHOSE IDENTITY QUESTION IS STILL OPEN (plan
    # P4-D401). Where nobody was at the keyboard, a column a question
    # offering `identifier` was put to -- the person question, or one
    # asked because its values are shaped like record numbers -- and
    # that the questions file did not answer is described as record
    # numbers until it is answered, and the run says so. The questions
    # below are worked out from the description as the rules read it, so
    # the file asks exactly what it asked before; only what is WRITTEN
    # holds the column back. A PERSON AT THE KEYBOARD ANSWERED ONLY WHAT
    # THEY TYPED A KEY FOR (lane TT's repair; the orchestrator's LANE TT
    # RULINGS 2 (1)): a question Enter left open, and one the prompt does
    # not put, holds its column exactly as it does with nobody there.
    # Until that repair, Enter took every question put as answered and
    # nothing was held: 19,998 of 20,000 real record numbers reached the
    # twin at 20,000 rows where nobody's run wrote none.
    still_open = [
        question
        for question in asked_about
        if asking.question_put(question) not in answered_here
    ]
    # EVERY DECLARATION IS AN ANSWER (Codex's review of lane HX, item
    # 1): `--decimal-comma amount` says `amount` holds measurements,
    # and a column also held as a record number would stand in two
    # declarations the contract refuses together (S8a).
    withheld: "tuple[str, ...]" = asking.unanswered_identities(
        still_open + dates_asked + coded_about,
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
    # ...AND A BLANK UNDER `identifier` HOLDS (plan P4-D445): a column
    # held whole in people while the person question was open had its
    # checklist entry written under `identifier` (`held_back` below),
    # and left blank it stays held once that question is answered
    # with no person column -- the checklist puts no open question
    # that would hold it, and the table is counted in rows. Where a
    # person column is declared or answered, every value is counted
    # in its people (plan P4-D406) as the same answers given at once
    # count it, so the blank keeps the column's own reading (plan
    # P4-D408: one round or several, the same bytes). It holds whoever is at
    # the keyboard, as every hold here does since lane TT's repair (batch 4q's
    # merge of lane CZ-A), and, as that hold does, not a column whose
    # question offering `identifier` the person answered at the prompt in
    # this run: what they typed stands (LANE TT RULINGS 2 (1)). Held anyway,
    # `1` typed in both rounds beside the Safe Harbor question answered `no`
    # in the file left a column of incomes in hundreds held as record
    # numbers at 20,000 rows, and the real table missed its own description.
    declared_by_blank = (
        forced_identifiers + forced_codes + forced_measurements
        + list(forced_decimal_commas) + list(twelve_hours) + list(date_columns)
        + sorted(counted) + list(identities_kept)
    )
    answered_at_the_prompt = asking.unanswered_identities(
        [question for question in asked_about if asking.question_put(question) in answered_here], document
    )
    withheld = withheld + tuple(
        name
        for name in identities_held
        if not person_columns
        and name in read.column_names
        and name not in withheld
        and name not in declared_by_blank
        and name not in answered_at_the_prompt
    )
    # THE CANDIDATES OF THE OPEN PERSON QUESTION ARE SUBJECTS whether or
    # not their own description is held (Codex's review of lane HX2,
    # item 4): a key read as free text publishes no value of its own, so
    # it is held by nothing above, yet every other value is still counted
    # in it.
    candidates: "list[str]" = []
    declared_here = (
        forced_identifiers
        + forced_codes
        + forced_measurements
        + list(forced_decimal_commas)
        + list(twelve_hours)
        + list(date_columns)
        + sorted(counted)
        + list(identities_kept)
    )
    for question in still_open:
        if (
            question.reason == asking.BECAUSE_REPEATS_AND_MANY
            and asking.offers_identifier(question)
            and question.name not in declared_here
            and question.name not in withheld
            and question.name not in candidates
        ):
            candidates += [question.name]
    # RULE U (c) (the stand-ins page's ZS.1 and ZS.3; repair 1 of lane GG,
    # its skeptic 1, item 3): while ANY question offering `identifier` is
    # open on any column of the table, `no` to a few-valued column's Safe
    # Harbor question releases no list naming a value fewer cells than the
    # floor hold (measured: a `7` on 5 rows of 20,000 listed and written on
    # exactly 5 twin cells beside a patient key whose question was open).
    identities_open = bool(withheld) or bool(candidates)
    if not identities_open:
        for question in still_open + dates_asked + coded_about:
            if asking.offers_identifier(question) and question.name not in (
                declared_here
            ):
                identities_open = True
    # A COLUMN OF ZIP-SHAPED NUMBERS IS HELD WHOLE until its Safe Harbor
    # question is answered `no` (plan P4-D427; ZR-b's verifies 2 to 6, the
    # orchestrator's LANE SH addenda): whole numbers of four or five
    # figures, ZIP codes with their leading zero or without it, in any
    # role, beside words and placeholders of any share -- one `UNKNOWN`
    # cell, three `HOMELESS`, `-99` on a third of the rows -- were read as
    # a count, binary, constant or labels with nothing asked and printed
    # every real ZIP. Held whoever is at the keyboard, since that question
    # is put in the questions file. ONLY `no` FREES IT (the second repair
    # of lane SH, item 6, and its third, the orchestrator's ruling R1 of
    # 2026-10-25 on ADDENDA 7 and 8): the other questions ask about record
    # numbers, dates and codes, not places, so `code`, `measurement` or
    # `keep` is the truthful answer for a ZIP, and each released 40 of 40
    # real ZIPs with no Safe Harbor question put (`code` the zoo's own
    # `zip5` too: 12 of 12); such an answer, or the same declaration,
    # leaves the column held and the Safe Harbor question is put in that
    # run, one question at a time. `yes` holds it (Codex's review of lane
    # SH, item 8: the column then stays held and the question is not put
    # again). A column of ages whose top-code would make cells missing is
    # held so too. It is no subject the other columns are counted in: it
    # names a place.
    # ONLY `--identifier` (which holds the column as record numbers) OR
    # `no` RELEASES IT, TYPED OR ANSWERED (the orchestrator's LANE SH2
    # RULINGS 1 (5), consistent with lane SH's ADDENDUM 7): a reading typed
    # on the command line that publishes values -- `--date-count`, a date
    # or clock reading, a code -- is no release either, so a typed
    # `--date-count` on ZIP codes, read as the dates they name one to one,
    # is held as the same answer in the questions file is, and the Safe
    # Harbor question follows in that run; and so are lane SH2's holds
    # (plan P4-D434): places, device numbers, ZIP areas, early dates and
    # years.
    declared_five = forced_identifiers + safe_harbor_no
    five_held: "list[str]" = []
    for name in five_figures + ages_held:
        if (
            (name not in declared_five or name in ages_held)
            and name not in safe_harbor_yes
            and name not in withheld
            and name not in five_held
            # ...but an identifier form the count in a DECLARED person
            # column's people holds whole already (plan P4-D406) is held so,
            # and put no Safe Harbor question: no answer could give one of
            # its values back (plan P4-D445; lane HX2's register beside a
            # declared person column). So is a column of persons' names
            # (plan P4-D478): beside a declared person column it keeps the
            # bytes it had.
            and not (
                name in harbor_reasons
                and harbor_reasons[name] in taxonomy.IDENTIFIER_FORM_HOLDS + taxonomy.PERSONS_NAMES_HOLDS
                and name in counted_in_people
            )
        ):
            five_held += [name]
    # ...AND A COLUMN OF PERSONS' NAMES BESIDE A PERSON COLUMN WHOSE QUESTION
    # IS STILL OPEN (lane CZ-F's repair, skeptic 1 item 6; plan P4-D478):
    # described below as the count in that column's people holds it, as
    # without the reader -- no level published, the same block and twin --
    # and put no Safe Harbor question that run: answered `keep` there, the
    # table is counted in rows and the question follows in the next run. One
    # the count does not hold whole is held as before, its question put.
    person_open: "list[str]" = []
    for question in still_open:
        if (
            question.reason == asking.BECAUSE_REPEATS_AND_MANY
            and asking.offers_identifier(question)
            and question.name not in declared_here
        ):
            person_open += [question.name]
    names_beside_open: "list[str]" = []
    for name in five_held:
        if (
            person_open
            and name in harbor_reasons
            and harbor_reasons[name] in taxonomy.PERSONS_NAMES_HOLDS
            and name not in person_open
        ):
            names_beside_open += [name]
    # ...and a column answered `yes` to that question is held so for good,
    # the run asking nothing more of it (plan P4-D427) -- but A COLUMN OF
    # AGES, which keeps its top-code for good (lane SH3, plan P4-D454): the
    # Safe Harbor rule asks an age over 89 to be pooled, and a truthful
    # `yes` held the whole column, its twin writing made-up numbers (999,
    # or 99,904 for ages in months) and every other statistic lost.
    # ONLY WHERE SOMETHING BESIDE ITS VALUES ESTABLISHES IT AS AGES (lane
    # SH3's repair, Codex's item 1 and the orchestrator's LANE SH3 RULINGS
    # 1 (1): an answer keeps the meaning it had when it was given): a unit
    # in its cells, its name, or a unit answered. A column its values alone
    # read as ages -- `patient_number` cycling through 1 to 100 -- is held
    # whole by `yes`, as before lane SH3, carried answers files too.
    ages_kept_top_coded: "dict[str, bool]" = {}
    for block in _described_columns(document):
        if (
            "top_coded" in block
            and f"{block['name']}" not in harbor_reasons
            and f"{block['name']}" in ages_established
            and ages_established[f"{block['name']}"]
        ):
            ages_kept_top_coded[f"{block['name']}"] = True
    # ...and a column answered with the unit of its ages: read in it, and
    # top-coded only where a value reaches that unit's mark.
    for name, _unit in ages_counted_in:
        if name not in harbor_reasons:
            ages_kept_top_coded[name] = True
    harbor_held: "list[str]" = []
    for name in safe_harbor_yes:
        if (
            name not in ages_kept_top_coded
            and name in read.column_names
            # ...a column of dates so early is held by the description
            # itself, its twin writing valid dates (plan P4-D434).
            and not (name in harbor_reasons and harbor_reasons[name] == taxonomy.HELD_DATES)
            # (A column answered `yes` about its dates in disguise is not
            # here but in `safe_harbor_dates_yes`: it keeps them read as
            # blank cells, its other values published, plan P4-D446.)
            and name not in forced_identifiers
            and name not in withheld
            and name not in five_held
            and name not in harbor_held
        ):
            harbor_held += [name]
    # ...and the values that read as dates in the other columns the first
    # description named (plan P4-D446): read as blank cells on the one
    # written, the questions having been worked out from every cell.
    dated_held = tuple(
        name
        for name in dated_values
        if name not in withheld and name not in five_held and name not in harbor_held
    )
    # ...AND THE MADE-UP SPELLINGS READ AGAIN IN THE SUBJECTS THE FINAL
    # DESCRIBE COUNTS IN (lane ID-ROOM4, plan P4-D489; the orchestrator's
    # LANE ID-ROOM4 RULINGS 4, item 2): the person columns, the keys an open
    # question holds and the open person question's candidates. A column
    # named above stays named (the rule errs toward holding).
    final_subjects = list(person_columns) + list(withheld) + candidates
    final_held, final_unmade = _made_up_spellings_held(read, document, settings, final_subjects)
    spelled_held = spelled_held + tuple(name for name in final_held if name not in spelled_held)
    spelled_unmade = spelled_unmade + tuple(
        name for name in final_unmade if name not in spelled_unmade
    )
    # ...and those whose spellings one letter or figure wider would still
    # meet a value, or whose spellings cannot be made, held as record
    # numbers (below).
    spelled_apart: "tuple[str, ...]" = spelled_unmade
    published = document
    if (
        withheld
        or candidates
        or five_held
        or harbor_held
        or _released_while_a_question_is_open(
            identities_open, rare_listed, levels_pooled, names_published
        )
        or dated_held
        or spelled_held
    ):
        if withheld:
            _warn(_withheld_notice(withheld), caution=results.CAUTION_WITHHELD)
        # ...and every column held so -- the candidates of the open
        # person question, and a key held by another identity question,
        # such as a patient number of figures padded with zeros that the
        # codes-or-measurements question was put to -- is a subject every
        # other value is counted in (plan P4-D406; lane HX2's skeptic,
        # round 2, item 1). One that never repeats counts in rows, as the
        # floor does, and is set aside by `profile.build_document`.
        # ...A NAMES COLUMN BESIDE AN OPEN PERSON QUESTION (`names_beside_open`)
        # is described first as the count in people holds it; one that count
        # does not hold whole is described again, held as the others are
        # (one more description, only for such a column).
        # ...AND THE MADE-UP SPELLINGS READ AGAIN ON THE DESCRIPTION WRITTEN
        # (lane ID-ROOM4, plan P4-D489): the writer steps over the hole
        # spellings of the description it is handed, and a hold above can
        # take one away, so a column its counters now spell as a value
        # few people hold is spelled wider too, and described once more; a
        # column already spelled wider whose wider spellings still meet
        # such a value -- a real cell the published `max_length` does not
        # measure, ordinary text of figures and marks -- is held as record
        # numbers (P4-D432's writer). This second reading is the path that
        # keeps NF139's promise, not a defensive one: it holds as a record
        # number a column whose wider spellings meet any real value or
        # cannot be made (live on codes beside eleven cells `t10000`, Codex's
        # review of lane ID-ROOM4, item 5); a hold changed no block's hole
        # spellings on any table measured.
        # ONE LOOP, TWO STOP CONDITIONS (the orchestrator's LANE ID-ROOM4
        # RULINGS 3 (5)): a pass ends it only when every names column waiting
        # is held whole by the count in people (`unheld` empty) and the second
        # reading names no column more (`again` and `apart` empty); every
        # further pass takes a name off `waiting` or adds one to the made-up
        # holds, so the loop ends.
        waiting = list(names_beside_open)
        while True:
            counted_in_people = []
            counted_in_rows = []
            published = profile.build_document(
                read,
                settings,
                forced_identifiers,
                forced_codes,
                forced_measurements,
                forced_decimal_commas,
                forced_metadata_rows=metadata_rows,
                forced_delimiter=declared_delimiter,
                kept_identities=list(identities_kept),
                table_notes=population_notes,
                stored_as=storage,
                unanswered=list(withheld)
                + [
                    name
                    for name in five_held
                    if not (name in harbor_reasons and harbor_reasons[name] == taxonomy.HELD_DATES)
                    and name not in waiting
                ]
                + harbor_held
                + list(spelled_apart),
                subjects=list(final_subjects),
                counted_in_subjects=counted_in_people,
                top_code=True,
                safe_harbor_no=safe_harbor_no,
                ages_counted_in=_marks_answered(ages_counted_in),
                counted_in_rows=counted_in_rows,
                rare_values_released=not identities_open,
                harbor_year=harbor_year,
                dated_held=dated_held,
                dated_values_no=safe_harbor_dates_no,
                dates_answered=tuple(answered_missing_dates + answered_real_values),
                # ...and the columns its Safe Harbor question holds for what
                # their numbers may be -- ZIP codes, years, dates -- so a held
                # column of counts that may be dates is read as such (lane
                # ID-ROOM3, plan P4-D488).
                counts_held_for_dates=tuple(five_held)
                + tuple(
                    name for name in harbor_held
                    if name in harbor_reasons and harbor_reasons[name] in profile.DATES_HOLD_REASONS
                ),
                # The description's own readings kept for the chain (lane CHs,
                # plan P4-D462): only behind the chain's switch.
                kept_spellings=chain_state.kept if chain_state is not None else None,
                made_up_held=list(spelled_held),
                # -- P4-D487 (lane KV): the value columns answered `keep`, the
                # Safe Harbor `yes`, and the columns an open question offering
                # `identifier` holds, whose value column is held whole.
                keyed_kept=list(values_kept_whole),
                keyed_yes=list(safe_harbor_yes) + list(safe_harbor_dates_yes),
                keyed_open=list(withheld) + list(candidates),
            )
            unheld = [name for name in waiting if name not in counted_in_people]
            named_again, unmade_again = _made_up_spellings_held(
                read, published, settings, final_subjects
            )
            again = tuple(name for name in named_again if name not in spelled_held)
            # ...a column already spelled wider whose wider spellings still
            # meet a value, or any column whose spellings cannot be made
            # (Codex's review of lane ID-ROOM4, item 1), held as record
            # numbers.
            apart = tuple(
                name
                for name in named_again
                if (name in spelled_held or name in unmade_again) and name not in spelled_apart
            )
            if not unheld and not again and not apart:
                break
            waiting = [name for name in waiting if name not in unheld]
            spelled_held = spelled_held + again
            spelled_apart = spelled_apart + apart
            spelled_unmade = spelled_unmade + tuple(
                name for name in unmade_again if name not in spelled_unmade
            )
        five_held = [name for name in five_held if name not in waiting]
        lane_sh = tuple(name for name in five_held if name not in harbor_reasons)
        lane_sh2 = tuple(name for name in five_held if name in harbor_reasons)
        if lane_sh:
            _warn(
                _safe_harbor_notice(lane_sh, True),
                caution=results.CAUTION_SAFE_HARBOR,
            )
        if lane_sh2:
            _warn(
                _safe_harbor_held_notice(lane_sh2),
                caution=results.CAUTION_SAFE_HARBOR,
            )
        if spelled_held:
            _warn(
                _made_up_held_notice(spelled_held, spelled_apart, spelled_unmade),
                caution=results.CAUTION_WITHHELD,
            )
    if counted_in_rows:
        _warn(
            _dates_held_in_rows_notice(tuple(counted_in_rows), settings.small_cell_floor),
            caution=results.CAUTION_DATES_HELD_IN_ROWS,
        )
    # RULE U OVER EVERY OPEN QUESTION OFFERING `identifier` (the stand-ins
    # page, ZS.1 (c); plan P4-D439; Codex's review of lane CODES-1's first
    # repair, item 8): while any is open on the table no column publishes
    # rule A2's positional census -- the free-text candidates of the person
    # question among them, which are subjects here and held by nothing, so
    # `profile.build_document`'s own rule, asked of the held columns, let a
    # declared code column beside 2,000 letter-only patient names publish
    # its census with that question open.
    questions_open: "list[str]" = []
    declared_now = (
        forced_identifiers
        + forced_codes
        + forced_measurements
        + list(forced_decimal_commas)
        + list(twelve_hours)
        + list(date_columns)
        + sorted(counted)
        + list(identities_kept)
    )
    # ...every question still open, Enter's among them (lane TT's repair).
    for question in still_open + dates_asked + coded_about:
        if (
            asking.offers_identifier(question)
            and question.name not in declared_now
            and question.name not in questions_open
        ):
            questions_open += [question.name]
    if questions_open:
        published = profile.without_census_places(published)
    if counted_in_people:
        named_once: "list[str]" = []
        for name in counted_in_people:
            if name not in named_once:
                named_once += [name]
        _warn(
            _counted_in_people_notice(
                tuple(named_once), settings.small_cell_floor
            ),
            caution=results.CAUTION_COUNTED_IN_PEOPLE,
        )

    # THE CHAIN BETWEEN COLUMNS, behind its switch (lane CHa, plan
    # P4-D418; contract 4.6b, in force since plan P4-D464): every shipped
    # run reaches this; the internal unswitched setting alone does not.
    if chain_state is not None:
        # THE OUTPUT'S NAMES ARE SETTLED BEFORE THE KEY (lane CHON's repair
        # 1, LANE CHON RULINGS 5 (2)): every refusal of the outputs step --
        # a network or missing out-dir, a name that is a folder or the table
        # itself -- comes before the run reaches the chain, where a new key
        # would be made.
        if _outputs_refused_before_the_chain(table, out_dir):
            return results.REFUSED
        published = _chained_description(
            chain_state,
            pathlib.Path(table),
            read,
            published,
            settings,
            tuple(withheld) + tuple(candidates),
            # ...a column held whatever the answer (plan P4-D489) declared as
            # nothing else.
            [name for name in forced_codes if name not in spelled_held],
            [name for name in forced_measurements if name not in spelled_held],
            [name for name in forced_decimal_commas if name not in spelled_held],
            storage,
            tuple(
                question.name
                for question in asked_about
                if question.reason == asking.BECAUSE_REPEATS_AND_MANY
                and (question.name in withheld or question.name in candidates)
            ),
            tuple(safe_harbor_no),
            tuple(withheld) + tuple(five_held) + tuple(harbor_held) + tuple(spelled_held),
            not identities_open,
            harbor_year,
            tuple(identities_kept),
            _marks_answered(ages_counted_in),
        )
        if chain_state.entry is None:
            return results.REFUSED

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
    # Where the moments' fail-safe left them out (behind the chain's switch
    # alone), the caution's one line closes the summary, so the file says
    # what the screen said (LANE MPp RULINGS 7 (3), verify 2's C2).
    if chain_state is not None and chain_state.moments_left_out:
        text = text + parsing.visible_lines(chain_state.moments_left_out) + "\n"
    _at(results.STEP_OUTPUTS)
    _make_the_twins_folder()
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
        _warn(
            errors.output_would_replace_the_table(_shown(source)),
            step=results.STEP_OUTPUTS,
        )
        return results.REFUSED

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
            ),
            caution=results.CAUTION_QUESTIONS_WOULD_REPLACE,
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
            f"written again: it will hold the questions still open, will "
            f"no longer ask the ones you have answered, and keeps every "
            f"answer given so far under '{asking.ANSWERED_BEFORE}'."
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
    # -- lane EZ-a (P4-D479): an answer no option repeats stands, or one
    # was typed at the keyboard, so the repeat line names the questions file.
    kept_stands = bool(answered_here) or bool(_answers_that_stand()) or _a_kept_answer_stands(
        safe_harbor_no + safe_harbor_yes + safe_harbor_dates_no + safe_harbor_dates_yes,
        list(identities_kept_answered) + units_kept + commas_kept + dates_kept, answered_month_first,
    )
    if (answered or answers_were_handed_back or kept_stands or _persons_answered()) and (
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
        or clock_figures
        or kept_stands
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
                # -- lanes TR (P4-D473; its skeptic 1, item 3) and EZ-a
                # (P4-D479): an answer of `clock-figures`, or an answer
                # `_a_kept_answer_stands` names, which no option repeats, is
                # repeated by the questions file this run writes.
                answers_file=(
                    f"--answers {_typed_path(questions_path)}"
                    if (kept_stands or clock_figures) and not questions_collides else ""
                ),
            )
        )
    kept_of_yours = summary.words_of_your_own(published)
    if kept_of_yours:
        _warn(
            _declared_words_notice(kept_of_yours, tuple(added_missing)),
            caution=results.CAUTION_DECLARED_WORDS,
        )
    if floor_chosen and smallest_group < _NOTICE_LINE:
        _warn(
            _lowered_floor_warning(smallest_group),
            caution=results.CAUTION_LOWERED_FLOOR,
        )
    # THE FLOOR THE DESCRIPTION IS WRITTEN AT, for the run's result.
    _record_floor(settings.small_cell_floor, False)
    _at(results.STEP_WRITING)

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
    # THE LEDGER'S ENTRY IS WRITTEN FIRST, the description after it, so
    # two runs can never both find no entry and both publish (contract
    # 4.6b.4); behind the chain's switch alone.
    if chain_state is not None and chain_state.entry is not None:
        from synthtwin import installation

        installation.record(chain_state.opened, chain_state.entry)
        chain_state.recorded = True
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
            _stopped_writing(_shown(state.sentence))
        elif state.both_files_written:
            if chain_state is not None:
                chain_state.described = True
            _wrote(
                (results.FILE_DESCRIPTION, profile_path),
                (results.FILE_SUMMARY, summary_path),
            )
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
                _left_behind([state.left_behind], _left_behind_note([state.left_behind]))
        raise
    if chain_state is not None:
        chain_state.described = True
    _wrote(
        (results.FILE_DESCRIPTION, profile_path),
        (results.FILE_SUMMARY, summary_path),
    )
    _described_carried(profile_path, chain_state is not None)
    # THE INSIDE RECORD (lane IN-2, plan P4-D496): the table, still open, read
    # into the record the twin is built from, once the description is written.
    _inside_record_written(read, published, profile_path)
    # THE TRAJECTORIES ZONE OF THE INSIDE RECORD (lane IN-3, plan P4-D498):
    # where the patient layer stands in the description written, its
    # patients' visits as a model, joining that record (Codex's review of
    # batch 4w, item 14), never in the description.
    if chain_state is not None and chain_state.grain is not None:
        _inside_trajectories(read, published, profile_path)
    # THE PRIVATE REPORT (lane ST, plan P4-D458), behind the chain's switch
    # alone, once the ledger holds the run and the description is written.
    if chain_state is not None:
        # A list grown in place and frozen once (the quadratic-growth guard,
        # tests/test_no_quadratic_list_growth.py), never a tuple copied.
        places: "list[tuple[pathlib.Path, str]]" = [
            (pathlib.Path(source), errors.INPUT_TABLE),
            (profile_path, errors.INPUT_DESCRIPTION),
            (summary_path, errors.INPUT_SUMMARY),
            (questions_path, "questions file"),
        ]
        if answers_path is not None:
            places += [(pathlib.Path(answers_path), "questions file you answered")]
        # ...F10 naming each column of dates whose twin writes record
        # numbers, read off the description written (Codex's review of batch
        # 4q, item 3; `_dates_not_carried`).
        _private_report(
            chain_state, profile_path, settings.small_cell_floor, tuple(places), _dates_not_carried(published)
        )
    if left_behind:
        # A caution, not a refusal. The profile is good, so the exit
        # code stays 0; the reader is simply told what to delete.
        #
        # This goes out BEFORE the "Written:" confirmation on purpose.
        # Both are ordinary prints and a stop can land between them; if
        # only one of the two reaches the person, it must be the one
        # naming a file that may hold text taken from their table, not
        # the one confirming what already went well.
        _left_behind(left_behind, _left_behind_note(left_behind))
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
    # force. (A column of dates lane SH2 holds is asked the Safe Harbor
    # question alone, plan P4-D434.)
    settled = forced_identifiers + forced_codes + forced_measurements + [
        name for name in harbor_reasons if harbor_reasons[name] == taxonomy.HELD_DATES
    ]
    # ...AND THE COLUMNS OF DATES OR TIMES BESIDE A FEW CODES, recomputed
    # from the FINAL settings (plan P4-D381): a column whose codes were
    # answered `missing` reads as dates now and is asked nothing, and one
    # answered `real-value` has its codes declared kept.
    # -- 3b.R2c (P4-D383): QUESTION Q6 from the FINAL settings, worked out
    # again only where the interview moved what it reads, and before Q1
    # and Q5, whose collections take the reading each answer `dates`
    # proposes (the Codex review of landing R2c, item 7).
    # ...AND THE PERSON QUESTION, recomputed from the FINAL
    # declarations like every other (plan P4-D340). A column answered
    # `identifier` at the terminal is declared now, so the file that
    # replaces this one no longer asks about it -- and the settings
    # carried here are the rebuilt ones, whose `person_columns` says
    # whether that answer settled who the rows are about.
    # -- 3b.R2c (P4-D383): QUESTION Q6, BESIDE every other question its
    # column raises: an accession number written `2024-252` is asked
    # whether it is dates and, as before, whether it is a code or a
    # record number, since only the person knows which.
    # ALL OF THEM IN ONE WALK OF THE TABLE (lane SR, plan P4-D400), each
    # date question worked out again only where the interview moved what
    # it reads.
    codes_moved = not (
        document is seen_of[0]
        and settings == seen_of[1]
        and settled == seen_of[2]
        and list(forced_decimal_commas) == seen_of[3]
    )
    dates_moved = not (
        document is dates_of[0]
        and settings == dates_of[1]
        and settled + date_columns + dates_kept == dates_of[2]
        and list(forced_decimal_commas) == dates_of[3]
    )
    month_moved = dates_moved or not (
        document is day_or_month_of[0] and settings == day_or_month_of[1]
    )
    if month_moved and answered_month_first:
        day_or_month = ()
    last_questions = profile.questions_of(
        read,
        document,
        settings,
        settled,
        tuple(forced_decimal_commas),
        storage,
        None if codes_moved else codes_seen,
        settled + date_columns + dates_kept if dates_moved else None,
        dates_seen,
        month_moved and not answered_month_first,
        day_or_month,
        True,
    )
    codes_seen = last_questions.codes_seen
    dates_seen = last_questions.dates_seen
    if dates_moved:
        dates_asked = list(dates_seen.questions)
    day_or_month = last_questions.day_or_month
    coded_about = list(codes_seen.questions)
    asked_about = _units_not_asked_again(
        last_questions.asked, units_kept + commas_kept, identities_kept_answered
    )
    # ...the people's own question read again on the last questions (plan
    # P4-D489): the Safe Harbor question and the file read the list below.
    identities_kept = asking.kept_beside_own_questions(
        tuple(identities_kept), asked_about, people_keys_kept
    )
    # ...less the columns held whatever the answer (plan P4-D489): no reading
    # of theirs is a measurement to name, and the file says why (below).
    listed_about = [question for question in last_questions.listed if question.name not in spelled_held]
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
    # ...AND THE SAFE HARBOR QUESTION (plan P4-D427), one to each column the
    # top-code reaches and each column of five-figure numbers held, where
    # no question above names the column; such a column leaves the
    # checklist, since it raised a question of its own.
    # ...where an open question offering `identifier` holds the column,
    # that question is the one put; a question answered at the keyboard
    # by a key holds nothing, so the Safe Harbor question is put to the
    # file then (measured: incomes in hundreds asked the date-count
    # question at the keyboard stayed held as ZIP-shaped with no question
    # to free them); one Enter left open is open (lane TT's repair).
    # EVERY OPEN QUESTION OFFERING `identifier` counts, not only those of
    # the columns held as record numbers (the second repair of lane SH,
    # item 2): ZIP+4 cells held for their figures and put the two-numbers
    # question were put the Safe Harbor question beside it. A question a
    # file answered `keep` is put again under its kept reading, and is no
    # longer open: there the Safe Harbor question is the one put, below.
    harbor_asked = asking.safe_harbor_questions(
        published,
        tuple(five_held),
        [
            question
            for question in asked_about
            if question.name in withheld
            or (
                asking.question_put(question) not in answered_here
                and asking.offers_identifier(question)
                and question.name not in identities_kept
            )
        ],
        tuple(ages_held),
        tuple(safe_harbor_no + safe_harbor_yes),
        tuple(few_valued),
        harbor_reasons,
        harbor_year,
        ages_established,
        tuple(dated_values),
        # ...and the question about values that read as dates answered, or
        # not to be put where `yes` holds the column whole (plan P4-D446),
        # nor beside another question to the same column this run.
        tuple(safe_harbor_dates_no + safe_harbor_dates_yes + safe_harbor_yes),
        # (A question the Safe Harbor one is put in place of, below, is no
        # question beside it.)
        tuple(
            question.name
            for question in asked_about
            if not (question.name in identities_kept and asking.offers_identifier(question))
            and question.reason != asking.BECAUSE_UNIT
        ),
        # ...and the label columns whose `no` would name the values too few
        # rows hold (plan P4-D471, lane CODES-2), put it on the same terms --
        # ONLY WHERE THE PUBLISHED DESCRIPTION STILL READS THE COLUMN AS
        # LABELS: one it holds, by the count in people, as a record number or
        # by a question, names nothing whatever is answered, so it is asked
        # nothing (the orchestrator's LANE CODES-2 RULINGS 2 (4): names
        # beside a padded key, held in people at 20,000 rows, were put it).
        rare_named=tuple(
            name for name in rare_named if name in _read_as_labels_in(published)
        ),
        # -- P4-D487 (lane KV): the clause each keyed pair's questions gain.
        keyed_keys=tuple(keyed_named),
        keyed_values=tuple(
            (pair.value, pair.key) for pair in keyed_found if pair.value not in values_kept_whole
        ),
    )
    if harbor_asked:
        harbored = [question.name for question in harbor_asked]
        # ...and the columns lane SH2 holds whole (plan P4-D434), each put
        # the Safe Harbor question ALONE: its held block reads no dates,
        # codes or labels, so a question about those -- Q6's `keep` or
        # `dates`, a century, a code -- waits for `no` (lane SH2's repair 1,
        # Codex item 4: a city column of dates beside words was put Q6
        # beside the Safe Harbor question).
        held_alone = [
            question.name
            for question in harbor_asked
            if question.reason in asking.SH2_HELD_REASONS
        ]
        # ...ONE QUESTION A COLUMN: a column answered `keep` to a question
        # offering `identifier` and held for its numbers is asked the Safe
        # Harbor question in place of that one, whose answer the file
        # carries (the second repair of lane SH, item 6).
        asked_about = [
            question
            for question in asked_about
            if question.name not in held_alone
            and not (
                question.name in harbored
                and question.name in identities_kept
                and asking.offers_identifier(question)
            )
            # ...and Q-UNIT (plan P4-D438) gives way to it on the same
            # column: one question a column, the Safe Harbor one first.
            and not (
                question.name in harbored
                and question.reason == asking.BECAUSE_UNIT
            )
        ] + harbor_asked
        # ...AND A FEW-VALUED COLUMN KEEPS ITS CHECKLIST ENTRY BESIDE ITS
        # SAFE HARBOR QUESTION (repair 1 of lane GG, its skeptic 1, item 5;
        # the stand-ins page's ZS.3, "in the first round ... so one round
        # settles them all"): the entry left the checklist for that
        # question, so `no` brought it back a round later and every such
        # column took a round more. Its question asks nothing the entry
        # asks, and holds nothing meanwhile.
        # ...AND SO DOES A LABEL COLUMN ASKED ABOUT THE VALUES TOO FEW ROWS
        # HOLD (plan P4-D471, lane CODES-2): its question holds nothing either.
        own_round = [
            question.name
            for question in harbor_asked
            if question.reason
            not in (asking.BECAUSE_SAFE_HARBOR_FEW_VALUES, asking.BECAUSE_SAFE_HARBOR_RARE_NAMES)
        ]
        listed_about = [
            question for question in listed_about if question.name not in own_round
        ]
        top_coded_names = [
            question.name
            for question in harbor_asked
            if question.reason == asking.BECAUSE_SAFE_HARBOR_AGES
        ]
        if top_coded_names:
            _warn(
                _safe_harbor_notice(tuple(top_coded_names), False),
                caution=results.CAUTION_SAFE_HARBOR,
            )
        years_coded = [
            question.name
            for question in harbor_asked
            if question.reason == asking.BECAUSE_SAFE_HARBOR_YEARS
        ]
        if years_coded:
            _warn(
                _safe_harbor_years_notice(
                    tuple(years_coded), harbor_year - _AGE_SHOWN
                ),
                caution=results.CAUTION_SAFE_HARBOR,
            )
    # ...AND ONCE THAT SAFE HARBOR QUESTION IS ANSWERED, `yes` or `no`, the
    # question offering `identifier` its column answered `keep` is put
    # neither again: both answers stand in the file's `answered_before`
    # section, and an answer given is not asked again (the orchestrator's
    # LANE SH2 RULINGS 4 (3), G3: DICOM ages and ZIP codes answered `keep`
    # and then `yes` were put the person question once more in every later
    # round, under `read_as_now: keep`).
    # ...AND QUESTION Q-KEYED (lane KV, plan P4-D487), one to each value
    # column the describe read as keyed and nobody answered, put beside the
    # others: it holds nothing (unanswered means keyed).
    # ...one question a column: a value column another question is put
    # this round is put Q-KEYED once that one is answered.
    asked_about = asked_about + asking.keyed_questions(
        published,
        [
            (pair.key, pair.value, len(pair.common), pair.readings)
            for pair in keyed_found
        ],
        tuple(values_keyed + values_kept_whole)
        + tuple(question.name for question in asked_about),
        settings.small_cell_floor,
    )
    harbor_answered = safe_harbor_no + safe_harbor_yes
    if harbor_answered:
        asked_about = [
            question
            for question in asked_about
            if not (
                question.name in harbor_answered
                and question.name in identities_kept
                and asking.offers_identifier(question)
            )
        ]
    # ...AND THE QUESTION OF A COLUMN OF SENTENCES (lane NOTES, plan P4-D481;
    # the orchestrator's LANE NOTES RULINGS 1 (3)): one to each column the
    # published description reads as free text for its sentences whose
    # question was not answered `text`; ONE QUESTION A COLUMN, so any other
    # question this file would put to such a column gives way to it -- and to
    # a column answered `text` too, which is put none again (lane NOTES's
    # repair 1: the question whether it names the person came back once its
    # own was answered).
    sentence_asked = asking.sentence_questions(
        published, tuple(sentences_text), settings.small_cell_floor
    )
    if sentence_asked or sentences_text:
        sentenced = [question.name for question in sentence_asked] + list(sentences_text)
        asked_about = [
            question for question in asked_about if question.name not in sentenced
        ] + sentence_asked
        listed_about = [
            question for question in listed_about if question.name not in sentenced
        ]
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
    # THE QUESTIONS AS DATA, BEFORE ANY FILE OF THEM IS WRITTEN (lane S5b,
    # plan P4-D441): the result holds one record for each entry of the
    # file, and the file is rendered from those records, so the two
    # cannot differ; a run whose questions file is not written keeps them.
    # ...and, behind the chain's switch alone, the person question's
    # `identifier` answer split in two (lane GRa, RULINGS 1 (1)).
    if chain_state is not None:
        asked_about = asking.with_the_record_answer(asked_about)
    question_records = asking.question_records(
        # -- P4-D401: a column held back is read as record
        # numbers until answered, and its entry says so (lane SH's
        # five-figure holds among them, plan P4-D427) -- AND A COLUMN
        # HELD WHOLE IN PEOPLE (plan P4-D445; lane CZ-H's skeptic 1, the
        # orchestrator's measurement wave6/OQ): its own question, put
        # beside the hold under another reading, named `measurement`,
        # and a blank kept that reading once the person question was
        # answered, so the column published with its question open. Its
        # entry names `identifier` now, and a blank keeps it held.
        asking.held_back(asked_about, withheld + tuple(five_held) + tuple(counted_in_people)),
        # ...and the checklist's entries too, so a blank keeps such a
        # column held (`Answers.identities_held`).
        asking.held_back(listed_about, withheld + tuple(five_held) + tuple(counted_in_people)),
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
        # ...and each column declared as counted dates that
        # did not read so, held on every table (P4-D406).
        _held_counted_dates(document, counted),
        put=_asked_at_a_prompt(),
    )
    _questions_put_in_the_result(question_records, len(read.column_names))
    if questions_collides:
        # Said once, before the files existed. Repeating it here would
        # be the same sentence twice with the run's outcome between
        # them, which reads as two separate troubles.
        if floor_chosen and smallest_group < _NOTICE_LINE:
            _warn(
                f"\n{_LOWERED_FLOOR_REMINDER}",
                caution=results.CAUTION_LOWERED_FLOOR_REMINDER,
            )
        _closing(profile_path)
        return results.NO_MISS
    written_questions = True
    questions_state = writing.DiskState()
    left_questions: "list[str]" = []
    try:
        left_questions = writing.write_one_file(
            questions_path,
            canonical.serialize(
                asking.questions_document_of(
                    _shown(pathlib.Path(table).name),
                    # Every entry, rendered from the result's records.
                    question_records,
                    # ...AND WHAT THIS RUN SAID ABOUT THE TABLE AS A
                    # WHOLE (plan P4-D341). The population notice, in
                    # the description's own words, because this file
                    # travels on its own and a page naming the columns
                    # of a small table without saying it is a small
                    # table says less than the other four do. A twin's
                    # profile step adds the sentence binding its answers
                    # to its reading (lane TT's repair, `_bound_reading`).
                    _table_sentences(document) + _binding_said()
                    # ...and why a column is held whatever the answer
                    # (lane ID-ROOM4, plan P4-D489).
                    + (
                        [_made_up_held_said(spelled_held, spelled_apart, spelled_unmade)]
                        if spelled_held
                        else []
                    ),
                    # ...and EVERY ANSWER THIS RUN ACTED ON, from the file,
                    # from an earlier run's kept answers or from the
                    # command line, so that handing this file back keeps
                    # them all (plans P4-D401 and P4-D408).
                    answered=_persons_marked(asking.answered_before(
                        _answers_given(
                            read.column_names, forced_codes,
                            forced_identifiers, forced_measurements,
                            forced_decimal_commas, twelve_hours, counted,
                            centuries, centuries_kept, date_columns,
                            dates_kept, identities_kept_answered,
                            answered_missing_dates, answered_real_values,
                            kept_code_shapes, first_row,
                            metadata_answer, declared_delimiter, day_first,
                            answered_month_first, tuple(safe_harbor_no),
                            tuple(safe_harbor_yes), tuple(units_kept),
                            tuple(commas_kept), ages_counted_in,
                            tuple(safe_harbor_dates_no),
                            tuple(safe_harbor_dates_yes),
                            tuple(clock_figures),
                            # -- lane NOTES (P4-D481): only a column whose
                            # question is still its own (the kind's answer
                            # replaces it, `asking.answered_before`).
                            tuple(sentences_text),
                            people_keys_kept=people_keys_kept,
                            values_keyed=tuple(values_keyed),
                            values_kept_whole=tuple(values_kept_whole),
                        )
                    )),
                    # ...with the names those answers use (P4-D408).
                    answered_columns=list(read.column_names),
                    # ...and, behind the chain's switch alone, its one
                    # entry (lane CHa, plan P4-D418).
                    chain_pairs=_chain_pairs(chain_state),
                    # ...and the subject question, where it was put (lane
                    # GRa, plan P4-D449), its answer written back.
                    chain_subject=(
                        asking.rows_per_person_entry(
                            chain_state.rows_answer, chain_state.subject_keys
                        )
                        if chain_state is not None and chain_state.subject_put
                        else None
                    ),
                    chain_said=(
                        (chain_state.persons_said, chain_state.records_said)
                        if chain_state is not None
                        else ((), ())
                    ),
                    chain_requests=(
                        (chain_state.add, chain_state.drop)
                        if chain_state is not None
                        else ((), ())
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
            _stopped_writing(_shown(questions_state.sentence))
        elif questions_state.target_written:
            _wrote((results.FILE_QUESTIONS, questions_path))
            _say(f"  {shown_questions_path}")
            if questions_state.left_behind:
                _left_behind(
                    [questions_state.left_behind],
                    _left_behind_note([questions_state.left_behind]),
                )
        raise
    except BaseException:
        written_questions = False
    if written_questions:
        _wrote((results.FILE_QUESTIONS, questions_path))
        _say(f"  {shown_questions_path}")
        # THE HOLD, NAMED WITH THE FILE IT IS IN (plan P4-D464), once that
        # file is written: a caution, which moves no exit status.
        if chain_state is not None and chain_state.waiting:
            _warn(
                _hold_paragraph(chain_state.waiting, shown_questions_path, chain_state.person_held),
                caution=results.CAUTION_CHAIN,
            )
        if left_questions:
            # The same caution the pair above prints, for the same
            # reason: a working file this run could not clear away is a
            # real-derived file sitting in the person's folder under a
            # name nobody gave them (review item P1-R6-F5). Discarding
            # this list was item L17b-R1-4's other half.
            _left_behind(left_questions, _left_behind_note(left_questions))
    else:
        if questions_state.sentence:
            _warn(
                _shown(questions_state.sentence),
                caution=results.CAUTION_QUESTIONS_NOT_WRITTEN,
            )
        _warn(
            f"\nThe description is written and complete. synthtwin could "
            f"not write its questions beside it at "
            f"{shown_questions_path}, so the columns it could not "
            f"settle are named on the screen above and nowhere else.",
            caution=results.CAUTION_QUESTIONS_NOT_WRITTEN,
        )

    if floor_chosen and smallest_group < _NOTICE_LINE:
        _warn(
            f"\n{_LOWERED_FLOOR_REMINDER}",
            caution=results.CAUTION_LOWERED_FLOOR_REMINDER,
        )
    _closing(profile_path)
    return results.NO_MISS


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
    least_floor: int,
    chain: bool = False,
) -> str:
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

    THE DESCRIPTION IS LOADED WITH ITS CHAIN (``chain``, every shipped run
    since plan P4-D464; contract 4.6b's S12 amended): layer L0, G16 and the
    polish run from what it publishes between columns, and one whose
    `statistical` and `grain` are null loads and generates exactly as
    before. False is the internal unswitched setting's: the loader of S12
    word for word.
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
        return results.UNUSABLE
    loaded = contract.load_profile(description, chain=None if chain else False)
    _record_floor(loaded.settings.small_cell_floor, True)
    # A DESCRIPTION WRITTEN UNDER A LOWERED FLOOR IS NOT BUILT FROM (plan
    # P4-D426, HIPAA first): the twin would hold every group it names,
    # however small, and decision D7 lets a twin travel freely.
    if _description_floor_refused(
        loaded.settings.small_cell_floor, least_floor, description, True
    ):
        return results.REFUSED
    _at(results.STEP_OUTPUTS)
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
        return results.REFUSED

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
            return results.REFUSED

    # THE TWIN IS HELD ONCE (plan P4-D415, lane SG): its columns held
    # compactly, never the whole table as Python objects, and its text
    # written from them a piece at a time, never made whole.
    # THE INSIDE RECORD (lane IN-2, plan P4-D496): where one stands beside this
    # description in the private folder, bound to its bytes, the twin is
    # drawn from it (a delimited twin; a workbook's is the description's).
    record = None if packaged else _inside_record_for(description)
    _at(results.STEP_CONTENT)
    # A FIRST LINE AND PROGRESS AT A TERMINAL (lane EZ-a, plan P4-D479).
    if _progress_at_a_terminal():
        _say(_first_line("Building the twin from", description))
    _counting_switched_on("building")
    drawn_inside: "list[str]" = []
    try:
        twin = None
        if record is not None:
            from synthtwin import inside_relations

            try:
                twin = generation.generate_inside(loaded, record, seed)
                drawn_inside = [each.column for each in twin.remarks if each.subject == generation.INSIDE_DRAWN_SUBJECT]
            except inside_relations.RelationsError as refused:
                _warn(f"{_shown(str(refused))} The twin is built from the description alone.",
                      caution=results.CAUTION_CHAIN)
            except (ValueError, ArithmeticError, IndexError, KeyError, TypeError):
                twin = None
                _warn("The twin could not be drawn from the inside record, a mistake in synthtwin; please report it. "
                      "It is built from the description alone.", caution=results.CAUTION_CHAIN)
        if twin is None:
            twin = generation.generate_held(loaded, seed)
        # THE TRAJECTORIES ZONE OF THE INSIDE RECORD (lane IN-3, plan P4-D498):
        # where the patient walk made the twin's patients and the record bound
        # to this description (its place and bytes, Codex's review of batch
        # 4w, item 14) holds the zone, their visits follow it. It times no
        # date (item 2): the date columns the dates zone wrote are written by
        # it again over the patients the rows then form.
        if loaded.relationships.grain is not None:
            from synthtwin import inside_trajectories

            zone = _inside_trajectories_for(description, list(twin.names), twin.n_rows)
            if zone is not None:
                dates_zone, dates_written = _dates_drawn(record, drawn_inside)
                # ...an addition: a zone the twin cannot take leaves the twin as the walk made it.
                try:
                    twin = inside_trajectories.twin_with_zone(twin, loaded, zone, seed, dates=dates_zone,
                                                              written=dates_written)
                except (ArithmeticError, IndexError, KeyError, TypeError, ValueError):
                    pass
        progress.stage("writing the twin and its report")
    finally:
        progress.switch_off()
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
    twin_members: "list[tuple[str, int, typing.Iterable[str]]] | None" = None
    twin_stream: "typing.Iterable[str] | None" = None
    if packaged:
        twin_members = sheetwriting.workbook_stream(loaded, twin)
    else:
        # EVERY PIECE IS ASKED BEFORE ANYTHING IS SHOWN OR WRITTEN, and
        # then made again for the write (plan P4-D415). Each of the
        # twin's codecs encodes a character at a time and a piece ends
        # with a line, so a text that encodes whole encodes piece by
        # piece and the other way round; the text is never made whole.
        try:
            for piece in rendering.twin_csv_pieces(twin):
                bytes(piece, twin_codec)
        except UnicodeEncodeError:
            _warn(
                errors.twin_not_writable_in_encoding(
                    dialect.ENCODING_WORDS[loaded.source.encoding]
                )
            )
            return results.REFUSED
        twin_stream = rendering.twin_csv_pieces(twin)
    report_text = parsing.visible_lines(_inside_report_head(drawn_inside) + rendering.report(loaded, twin))

    # THE RESULT TAKES THE TWIN'S MISSES AS ITS REPORT IS SHOWN (plan
    # P4-D395 part 1): a run stopped after this keeps them, one stopped
    # before it (the encoding refusal above) keeps none. No cell of the
    # twin enters the result.
    _generated(loaded, twin)
    _say(report_text)
    # ONE LINE ON THE SCREEN NAMING WHAT THE TWIN INVENTED (plan P4-D2
    # item 2). It is a warning rather than an ordinary line because a
    # person who reads one thing before opening the twin should read
    # this one; the exit code does not move for it, because a decline is
    # not a failure and a run that warned still succeeded.
    _warn(
        rendering.made_up_warning(loaded), caution=results.CAUTION_MADE_UP_COLUMNS
    )
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
    _at(results.STEP_WRITING)
    try:
        left_behind = writing.write_both_files(
            twin_path,
            report_path,
            "",
            report_text,
            table_path=pathlib.Path(source),
            state=state,
            words=errors.TWIN_WORDS,
            first_encoding=twin_codec,
            first_newline="",
            first_members=twin_members,
            first_stream=twin_stream,
        )
    except BaseException:
        if state.sentence:
            _stopped_writing(_shown(state.sentence))
        elif state.both_files_written:
            _wrote((results.FILE_TWIN, twin_path), (results.FILE_TWIN_REPORT, report_path))
            _say(f"\nWritten:\n  {shown_twin_path}\n  {shown_report_path}")
            if state.left_behind:
                _left_behind(
                    [state.left_behind],
                    _left_behind_note([state.left_behind], "twin"),
                )
        raise
    _wrote((results.FILE_TWIN, twin_path), (results.FILE_TWIN_REPORT, report_path))
    if left_behind:
        # A caution, not a refusal, and printed BEFORE the confirmation
        # for the same reason as in the profile command: if only one of
        # the two lines reaches the person, it must be the one naming a
        # file that may hold real-derived text.
        _left_behind(left_behind, _left_behind_note(left_behind, "twin"))
    _say(f"\nWritten:\n  {shown_twin_path}\n  {shown_report_path}")
    _teach(_teaching_validate(description, twin_path))
    return results.NO_MISS


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
    line = _typed_line(
        _next(results.PURPOSE_GENERATE, "synthtwin", "generate", f"{description}")
    )
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
    line = _typed_line(
        _next(
            results.PURPOSE_VALIDATE,
            "synthtwin",
            "validate",
            f"{description}",
            "--twin",
            f"{twin_path}",
        )
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
    sheet: str,
    least_floor: int,
    chain: bool = False,
) -> str:
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

    THE CHAIN'S SWITCH (`chain`, lane CHv, plan P4-D430; on for every
    shipped run since plan P4-D464). With it, the description is loaded
    with its chain (`contract.load_profile_document`: S23 to S28), and
    where it carries one the quality report gains V12's section and the
    screen ONE line in its place; a description carrying no chain is
    measured, reported and exited exactly as without the switch.
    """
    from synthtwin import contract, quality, validation, writing

    document: "dict[str, object] | None" = None
    if chain:
        loaded, document = contract.load_profile_document(description)
    else:
        # The internal unswitched setting: S12 as written before plan P4-D464.
        loaded = contract.load_profile(description, chain=False)
    _record_floor(loaded.settings.small_cell_floor, True)
    # A DESCRIPTION WRITTEN UNDER A LOWERED FLOOR IS NOT CHECKED AGAINST
    # (plan P4-D426, HIPAA first): the report would quote its small
    # groups and count the checked file's at that size.
    if _description_floor_refused(
        loaded.settings.small_cell_floor, least_floor, description, False
    ):
        return results.REFUSED
    _at(results.STEP_OUTPUTS)
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
            return results.REFUSED

    shown_quality_path = _shown(quality_path)
    if not replace and _already_there(quality_path):
        _warn(errors.quality_target_already_there(shown_quality_path))
        return results.REFUSED

    # `--sheet` REACHES THIS COMMAND TOO (repair of landing 2b.10). The
    # option was accepted here and then dropped on the floor: a person
    # checking a real workbook whose table is not on the first visible
    # sheet named the sheet, was given no error, and had a different
    # sheet measured against their description.
    # MEASURING STARTS BY OPENING THE FILE: a refusal there is about the
    # input (a G12 refusal names its own step, `content`).
    _at(results.STEP_INPUT)
    # A FIRST LINE AND PROGRESS AT A TERMINAL (lane EZ-a, plan P4-D479).
    if _progress_at_a_terminal():
        _say(_first_line("Measuring", measured))
    _counting_switched_on("checking")
    # THE DEFAULT CALL IS THE CALL IT WAS (skeptic 1 of lane CHv, item 1):
    # a run without the chain's switch hands `measure` the three arguments
    # it always took, so a caller that wraps `measure` with that signature
    # (the health zoo's battery) still runs; only the switched run hands it
    # the parsed document.
    # ...AND ON A DESCRIPTION THAT PUBLISHES NOTHING BETWEEN COLUMNS (plan
    # P4-D464: every shipped run is switched), the call it always was: it
    # measures, reports and exits exactly as before.
    try:
        if document is None or not loaded.relationships.switched:
            outcome = validation.measure(loaded, measured, sheet)
        else:
            outcome = validation.measure(loaded, measured, sheet, document)
    finally:
        progress.switch_off()
    outcome = _outcome_of_a_drawn_twin(description, measured, outcome)
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
    verdict = results.MISSED if outcome.census.missed else results.NO_MISS

    # THE RESULT TAKES THE CHECK'S MISSES AS ITS REPORT IS SHOWN (plan
    # P4-D395 part 1): a run stopped while writing keeps them.
    _validated(loaded, outcome)
    if outcome.chain is None:
        _say_pieces(report_pieces)
    else:
        # THE SCREEN KEEPS ONE LINE OF THE CHAIN'S SECTION (lane CHv): the
        # written report holds the pair section whole; the screen prints
        # the same report with that section as one summary line.
        screen_pieces = quality.report_pieces(loaded, outcome, screen=True)
        for index in range(len(screen_pieces)):
            screen_pieces[index] = parsing.visible_lines(screen_pieces[index])
        _say_pieces(screen_pieces)
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
    _at(results.STEP_WRITING)
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
            _stopped_writing(_shown(state.sentence))
        elif state.target_written:
            _wrote((results.FILE_QUALITY_REPORT, quality_path))
            _say(f"\nWritten:\n  {shown_quality_path}")
            if state.left_behind:
                _left_behind(
                    [state.left_behind],
                    _left_behind_note(
                        [state.left_behind], "quality report", True
                    ),
                )
        raise
    _wrote((results.FILE_QUALITY_REPORT, quality_path))
    if left_behind:
        # A caution, not a refusal, and printed BEFORE the confirmation
        # for the reason the other two commands give: if only one of the
        # two lines reaches the person, it must be the one naming a file
        # that may hold real-derived text.
        _left_behind(
            left_behind, _left_behind_note(left_behind, "quality report", True)
        )
    _say(f"\nWritten:\n  {shown_quality_path}")
    # THE STATUS THE LINES NAME IS THE RESULT'S (plan P4-D395 part 4).
    code = results.exit_code(results.Result(results.VALIDATE, verdict))
    # ...AND IN THE TWIN COMMAND, THE TWIN'S (lane TT, plan P4-D460): the
    # status its run will end with, the most severe of its steps'.
    session = _current()
    if session is not None and session.twin_step:
        code = results.exit_code(
            results.Result(results.TWIN, _more_severe(session.before, verdict))
        )
    _say(_verdict_lines(outcome.census.missed, code))
    return verdict


# -- checking this computer before a first run (plan P4-D397) ----------

# THE PYTHON THIS PACKAGE NEEDS, as pyproject.toml's `requires-python`
# states it. An older one cannot even install the package, so this line
# is for the person whose environment was built by another Python than
# the one they think. An older Python running `python -m synthtwin` from
# a source folder never reaches this module: `__main__.py` says so before
# importing it. 3.11 since plan P4-D410 (the owner's "3.11 and later" of
# 2026-10-19): the libraries' current releases need it.
_PYTHON_FLOOR = (3, 11)

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
    floor = f"{_PYTHON_FLOOR[0]}.{_PYTHON_FLOOR[1]}"
    if (version[0], version[1]) >= _PYTHON_FLOOR:
        return _passed(f"Python {spoken} ({floor} or later is needed)")
    return _failed(
        f"Python {spoken} is too old: synthtwin needs Python {floor} or "
        f"later. Install a newer Python (see 'Before you start' in "
        f"README.md), then {_INSTALL_AGAIN}."
    )


def _not_loaded(package: str, needed_for: str) -> _Check:
    return _failed(
        f"{package} could not be loaded, and synthtwin needs it to "
        f"{needed_for}. To put it in place, {_INSTALL_AGAIN}."
    )


def _library_version(package: str) -> str:
    """The installed version of one library, as its own metadata records it.

    EVERY RUNTIME LIBRARY IS NAMED WITH ITS VERSION (plan P4-D410): the
    twin's bytes are proved under exact pins, so the line a person copies
    into a question says which ones this computer holds. A library that
    loaded but carries no metadata -- a source folder on the path -- says
    so instead of a number.
    """
    try:
        return importlib.metadata.version(package)
    except Exception:  # noqa: BLE001 -- as in _version: the allowlist
        # (plan D6.2) permits only importlib.metadata.version.
        return "of no recorded version"


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
    return _passed(f"numpy {_library_version('numpy')} can be loaded")


def _check_pandas() -> _Check:
    # The same plain import, for the reader's checking library. It is
    # loaded and nothing of it is called: `doctor` reads no table.
    try:
        import pandas  # noqa: F401
    except Exception:  # noqa: BLE001 -- as in _check_numpy
        return _not_loaded("pandas", "read a table")
    return _passed(f"pandas {_library_version('pandas')} can be loaded")


def _check_pyarrow() -> _Check:
    # The same plain import, of the one admitted pyarrow module (plans
    # P4-D409 and P4-D410: zone R, and text held as exact bytes).
    try:
        import pyarrow.csv  # noqa: F401
    except Exception:  # noqa: BLE001 -- as in _check_numpy
        return _not_loaded("pyarrow", "read and hold a table")
    return _passed(f"pyarrow {_library_version('pyarrow')} can be loaded")


def _check_scipy() -> _Check:
    # The same plain import, of the two admitted scipy modules (plans
    # P4-D409 and P4-D410: the search side of zone D, and zone P).
    try:
        import scipy.linalg  # noqa: F401
        import scipy.optimize  # noqa: F401
    except Exception:  # noqa: BLE001 -- as in _check_numpy
        return _not_loaded("scipy", "check what is published")
    return _passed(f"scipy {_library_version('scipy')} can be loaded")


def _total_memory() -> "int | None":
    """This computer's installed memory in bytes, or None where it cannot be read (`computer.installed_memory`, plan P4-D466)."""
    return computer.installed_memory()


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


# THE KEY OF EACH OF DOCTOR'S CHECKS, in `_doctor_checks`' order: what
# names a check not made in a run's result (plan P4-D395 part 1).
_DOCTOR_CHECK_KEYS = (
    "python",
    "numpy",
    "pandas",
    "pyarrow",
    "scipy",
    "output-folder",
    "memory",
    "table",
)


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
        _check_pyarrow(),
        _check_scipy(),
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


def _run_doctor(table: "str | None", out_dir: "str | None") -> str:
    """`synthtwin doctor`: one plain line per check, then what to do next.

    Guarantees: returns `no-miss` when every check passed or could not
    be made, and `refused` (step `environment`) when any made did not
    pass (exit 0 and 1). The run's result counts the checks, those passed,
    failed and not made -- a check not made is never counted passed nor
    failed -- and lists each check not made in `unjudged`, keyed by the
    check that composes it (plan P4-D395 part 1). Boundary: a named table
    is never opened -- its size is asked of the file system and nothing
    else -- and the one file written is the test file in the output
    folder, removed at once. No network, subprocess, native or
    dynamic-code operation.
    """
    _say(f"synthtwin {_version()}: checking this computer before a first run.")
    checks = _doctor_checks(table, out_dir)
    failed = 0
    unmade = 0
    unjudged: "list[results.Unjudged]" = []
    for place in range(len(checks)):
        check = checks[place]
        _say(check.line)
        if not check.passed:
            failed += 1
        elif not check.made:
            unmade += 1
            unjudged += [results.Unjudged("", "", "", _DOCTOR_CHECK_KEYS[place])]
    session = _current()
    if session is not None:
        session.tally = (
            ("checks", len(checks)),
            ("passed", len(checks) - failed - unmade),
            ("failed", failed),
            ("not-made", unmade),
        )
        session.unjudged = tuple(unjudged)
        session.step = results.STEP_ENVIRONMENT
        for check in checks:
            if not check.passed:
                session.refusal_words += [parsing.visible_lines(check.line)]
    if failed:
        _say(
            f"\n{failed} check(s) did not pass. Do what the line marked "
            f"PROBLEM says, then run this again:\n"
            f"{_doctor_again(table, out_dir)}"
        )
        return results.REFUSED
    passed = "Every check that could be made passed." if unmade else "Every check passed."
    _say(f"\n{passed} {_teaching_profile(table, out_dir)}")
    return results.NO_MISS


def _doctor_again(table: "str | None", out_dir: "str | None") -> str:
    """The line a failed `doctor` ends with: the same check, as the person typed it."""
    words = ["synthtwin", "doctor"]
    if table is not None:
        words += [f"{table}"]
    if out_dir is not None:
        words += ["--out-dir", f"{out_dir}"]
    line = _typed_line(_next(results.PURPOSE_DOCTOR, *words))
    return f"  {line}{_quoting_said(line)}"


def _teaching_profile(table: "str | None", out_dir: "str | None" = None) -> str:
    """The line that ends a passing `doctor`: the first command of a run.

    It names the table and the output folder doctor was given, so the
    folder it checked is the one `profile` writes into.
    """
    words = ["synthtwin", "profile", "my-table.csv" if table is None else f"{table}"]
    if out_dir is not None:
        words += ["--out-dir", f"{out_dir}"]
    line = _typed_line(_next(results.PURPOSE_PROFILE, *words))
    return (
        f"Next, describe your table:\n"
        f"  {line}{_quoting_said(line)}"
    )


# -- the whole journey in one command (lane TT, plan P4-D460) ------------
#
# `synthtwin twin TABLE` runs `profile`, `generate` and `validate` in one
# run and one folder, each step the command line a person would type
# apart (`_twin_words`), read by the same parser and run by the same
# dispatch, so its six files are the three commands' files byte for byte
# and each step's result is that command's own (`steps`). The questions
# are the profile step's, put on screen before any file is written; the
# answers stay in the folder's questions file, beside the description,
# which a later run in the folder hands back and puts no question: it
# asks nothing and reads the table as the earlier run did. The run's
# verdict, misses, unjudged obligations and refusal are its most severe
# step's (plan P4-D395 part 4), its exit status `results.exit_code`'s.

# The folder a twin is written into when no `--out-dir` names one: the
# table's own name and this mark, beside the table and never the table's
# own folder, so the answers kept there are never beside the real table
# unless the person names that folder.
_TWIN_FOLDER_MARK = "-synthtwin"
# How severe each verdict is, the most first: the step a twin takes its
# verdict from (plan P4-D395 part 4: the later of two equally severe).
_SEVERITY = {results.UNUSABLE: 0, results.REFUSED: 1, results.MISSED: 2, results.NO_MISS: 3}


def _more_severe(earlier: str, later: str) -> str:
    """The more severe of two verdicts, the later where they are alike; the later where the earlier is empty."""
    if earlier not in _SEVERITY:
        return later
    if later not in _SEVERITY:
        return earlier
    return earlier if _SEVERITY[earlier] < _SEVERITY[later] else later


def _teach(lines: str) -> None:
    """Show a next-command teaching line, unless the run is a step of the twin (lane TT, plan P4-D460).

    A step's next command is still recorded in its result: the line is
    composed (`_next`), only not shown, because the twin goes on to that
    command by itself.
    """
    session = _current()
    if session is not None and session.twin_step:
        return
    _say(lines)


# THE SENTENCE BINDING A TWIN'S KEPT ANSWERS TO THE FILE THEY WERE GIVEN
# ABOUT (lane TT's repair; the orchestrator's LANE TT RULINGS 1 items 3 and
# 4, Codex's items 3 and 4): written by a twin's profile step among its
# questions file's sentences about the table, and read back by the next
# twin in that folder before it hands the file back by itself. It names the
# file's size, its fingerprint (`reading._fold_of`) and the sheet read, and
# the reading options the questions file does not carry -- the smallest
# group and how many times `--missing-value` and `--keep-value` were given
# -- so answers are never handed to another file, nor read under other
# options, without the person saying so. It names no value of the table:
# counts, one number of the file's bytes and a sheet's name, which the
# description publishes too.
_BINDING_HEAD = (
    "synthtwin twin hands these answers back by itself only to the file "
    "they were given about"
)
_BINDING_SIZE = ": a file of "
_BINDING_FOLD = " bytes whose fingerprint is "
_BINDING_SHEET = ", its sheet '"
_BINDING_FLOOR = ", read with the smallest group "
_BINDING_MISSING = ", --missing-value given "
_BINDING_KEPT = " time(s) and --keep-value given "
_BINDING_END = " time(s)."


def _binding_sentence(
    bound: "tuple[int, int, str]", floor: int, missing: int, kept: int
) -> str:
    """The sentence binding kept answers to ``bound`` (size, fingerprint, sheet) and to the reading options given."""
    size, fold, sheet = bound
    sheet_said = f"{_BINDING_SHEET}{sheet}'" if sheet else ""
    return (
        f"{_BINDING_HEAD}{_BINDING_SIZE}{size}{_BINDING_FOLD}{fold}"
        f"{sheet_said}{_BINDING_FLOOR}{floor}{_BINDING_MISSING}{missing}"
        f"{_BINDING_KEPT}{kept}{_BINDING_END}"
    )


def _binding_said() -> "list[str]":
    """The binding sentence a twin's profile step writes into its questions file; none on any other run."""
    session = _current()
    if session is None or not session.twin_step or not session.binding:
        return []
    return [session.binding]


def _place_of(text: str, marker: str, start: int = 0) -> int:
    """Where ``marker`` first stands in ``text`` from ``start``, or -1, compared a slice at a time (the offline audit's form)."""
    place = start
    while place + len(marker) <= len(text):
        if text[place : place + len(marker)] == marker:
            return place
        place = place + 1
    return -1


def _whole_number_after(text: str, marker: str) -> "int | None":
    """The figures standing right after ``marker`` in ``text`` as a number, or None."""
    place = _place_of(text, marker)
    if place < 0:
        return None
    start = place + len(marker)
    end = start
    while end < len(text) and text[end] in "0123456789":
        end = end + 1
    if end == start:
        return None
    return int(text[start:end])


def _bound_reading(
    kept_file: "dict[str, object]",
) -> "tuple[tuple[int, int, str], int, int, int] | None":
    """What a twin's questions file binds its answers to: (size, fingerprint, sheet), the floor and the two counts; None where it binds them to nothing.

    The sentence `_binding_sentence` writes, read back from the file's
    sentences about the table. A questions file `profile` wrote, or an
    edited one that lost the sentence, binds nothing. A fixed function of
    the file's content; raises nothing.
    """
    said = kept_file["about_your_table"] if "about_your_table" in kept_file else []
    if not isinstance(said, list):
        return None
    for sentence in said:
        if not isinstance(sentence, str) or sentence[: len(_BINDING_HEAD)] != _BINDING_HEAD:
            continue
        size = _whole_number_after(sentence, _BINDING_SIZE)
        fold = _whole_number_after(sentence, _BINDING_FOLD)
        floor = _whole_number_after(sentence, _BINDING_FLOOR)
        missing = _whole_number_after(sentence, _BINDING_MISSING)
        kept = _whole_number_after(sentence, _BINDING_KEPT)
        if size is None or fold is None or floor is None or missing is None or kept is None:
            return None
        sheet = ""
        opened = _place_of(sentence, _BINDING_SHEET)
        closed = _place_of(sentence, f"'{_BINDING_FLOOR}")
        if opened >= 0 and closed > opened:
            sheet = sentence[opened + len(_BINDING_SHEET) : closed]
        return ((size, fold, sheet), floor, missing, kept)
    return None


def _read_otherwise(
    options: _Options, floor: int, missing: int, kept: int
) -> "tuple[str, str, str] | None":
    """The first reading option given otherwise than when the kept answers were given: (option, then, now), or None.

    The options a questions file does not carry (Codex's item 3): the
    smallest group, and how many times `--missing-value` and `--keep-value`
    were given. Each is said in words: the floor as its number, the others
    as a count of times. A fixed function of its arguments; raises nothing.
    """

    def times(count: int) -> str:
        return "given once" if count == 1 else f"given {count} times"

    if options.smallest_group != floor:
        return ("--smallest-group", f"set to {floor}", f"set to {options.smallest_group}")
    if len(options.missing_values) != missing:
        return ("--missing-value", times(missing), times(len(options.missing_values)))
    if len(options.kept_values) != kept:
        return ("--keep-value", times(kept), times(len(options.kept_values)))
    return None


def _make_the_twins_folder() -> None:
    """Make the twin's own folder, where the run in progress is a twin's profile step that owns one.

    Called once the questions are answered and before any output name
    is settled, so a twin stopped at a question leaves no folder behind.
    """
    session = _current()
    if session is None or not session.folder_to_make:
        return
    folder = pathlib.Path(session.folder_to_make)
    # A FOLDER THAT CANNOT BE MADE IS A REFUSAL, NOT A STACK TRACE (lane
    # TT's repair; Codex's review of lane TT, item 8): a table in a folder
    # that takes no new folder was profiled, its questions answered, and
    # `mkdir` raised. The twin's preflight refuses it before the table is
    # read where the folder's own mode says so (`_a_folder_can_be_made_in`);
    # one this cannot foresee is refused here, before any file is written.
    try:
        folder.mkdir(exist_ok=True)
    except OSError as error:
        raise errors.ProfileError(errors.twin_folder_not_made(_shown(folder))) from error
    session.folder_to_make = ""


def _a_folder_can_be_made_in(parent: pathlib.Path) -> bool:
    """Whether a folder's own mode lets a folder be made in it, read without writing anything (lane TT's repair, Codex's item 8).

    On POSIX a folder whose mode grants nobody writing (no `w` bit at
    all, read from `stat`) takes no new folder; any other answer is left
    to `mkdir`, whose refusal `_make_the_twins_folder` turns into words.
    On Windows the read-only mark does not stop a folder being made, so
    nothing is decided here. A folder that cannot be looked at is one
    that takes nothing. Raises nothing.
    """
    if sys.platform == "win32":
        return True
    try:
        mode = pathlib.Path(f"{parent}").stat().st_mode
    except OSError:
        return False
    return (mode & 0o222) != 0


def _twin_folder(table: str, out_dir: "str | None") -> "tuple[pathlib.Path, bool]":
    """The twin's one output folder, and whether the run is to make it.

    `--out-dir` names a folder that must exist, as on every command;
    otherwise it is TABLE-synthtwin beside the table, made by the run
    once the questions are answered. Raises ProfileError where the named
    folder is not there or the default name is taken by something that
    is not a folder, and PathValidationError where a path is not a plain
    local one. Creates nothing.
    """
    from synthtwin import profile

    if out_dir is not None:
        named = pathlib.Path(validate_local_path(out_dir, purpose="output folder"))
        if not named.is_dir():
            raise errors.ProfileError(errors.twin_folder_missing(_shown(named)))
        return (named, False)
    source = pathlib.Path(table)
    folder = pathlib.Path(
        validate_local_path(
            f"{source.parent / (profile.table_stem(source.name) + _TWIN_FOLDER_MARK)}",
            purpose="output folder",
        )
    )
    if _already_there(folder) and not folder.is_dir():
        raise errors.ProfileError(errors.twin_folder_taken(_shown(folder)))
    return (folder, not folder.is_dir())


def _twin_outputs(table: str, folder: pathlib.Path) -> "list[pathlib.Path]":
    """The six files a twin writes into ``folder``, in the order written; none where the folder is not there yet.

    The names the three steps settle for themselves: the profile step's
    description, summary and questions file, the twin and its report
    (a workbook's twin is a workbook: the table's kind is read off its
    opening bytes by the reader's own test, never its name, Codex's item
    6), and the quality report. Each passes the locality gate, as the step
    that writes it passes it, so a link at a name is resolved to where it
    leads, and a folder standing at any of them is refused as the step
    would refuse it, before any step runs (Codex's item 7). Reads the
    table's opening bytes alone; raises what the locality gate raises,
    and ProfileError for a folder at a name.
    """
    from synthtwin import profile, reading, writing

    if not pathlib.Path(folder).is_dir():
        return []
    source = pathlib.Path(table)
    profile_path, summary_path = profile.default_output_paths(source, f"{folder}")
    questions_path = profile.questions_output_path(source, f"{folder}")
    packaged = reading.opens_as_a_workbook(table)
    twin_path, report_path = _twin_paths(profile_path, None, packaged)
    quality_path = _quality_path(profile_path, f"{twin_path}", None)
    for target, words in (
        (twin_path, errors.TWIN_WORDS),
        (report_path, errors.TWIN_WORDS),
        (quality_path, errors.QUALITY_WORDS),
    ):
        writing.refuse_if_folder(target, words)
    return [
        profile_path,
        summary_path,
        questions_path,
        twin_path,
        report_path,
        quality_path,
    ]


def _twin_output_on_the_table(
    named: "list[pathlib.Path]", source: pathlib.Path
) -> str:
    """The refusal of a twin one of whose six names leads onto its own table, or "" (lane TT's repair).

    Codex's review of lane TT, item 1, the orchestrator's LANE TT RULINGS
    1 item 1: with `TABLE-synthtwin/TABLE-twin.csv` a link to the table,
    `twin --replace` let generate write the twin over the real table,
    since each step guards only the file it was handed and generate is
    handed the description. So every name of the three steps is asked,
    before any step runs, by the test the profile step asks of its own
    two (`profile.is_the_same_file`, after the resolved paths are
    compared): the description's and the summary's refusal is the profile
    step's own words, every other name's says which file it is. A fixed
    function of the names and what the filesystem says of them; writes
    nothing.
    """
    from synthtwin import profile

    for place, target in enumerate(named):
        if target == source or profile.is_the_same_file(target, source):
            if place < 2:
                return errors.output_would_replace_the_table(_shown(source))
            return errors.twin_output_would_replace_the_table(
                _shown(target), _shown(source)
            )
    return ""


def _twin_words(
    command: str, given: str, folder: pathlib.Path, options: _Options
) -> "list[str]":
    """One step of the twin as the command line a person types apart (lane TT, plan P4-D460).

    The path first, then the folder, then every option the step reads,
    each in its `--option=value` form so a value is never read as an
    option; `--date-count`'s two values follow it. A fixed function of
    its arguments; raises nothing.
    """
    path = given if given[:1] != "-" else os.path.join(".", given)
    words = [command, path, f"--out-dir={folder}"]
    if command == _GENERATE:
        words += [f"--seed={options.seed}"]
    if command == _PROFILE:
        for option, values in (
            ("--person", options.persons),
            ("--identifier", options.identifiers),
            ("--code", options.codes),
            ("--measurement", options.measurements),
            ("--decimal-comma", options.decimal_commas),
            ("--twelve-hour", options.twelve_hours),
            ("--century", options.centuries),
            ("--date-column", options.date_columns),
            ("--keep-value", options.kept_values),
            ("--missing-value", options.missing_values),
        ):
            for value in values:
                words += [f"{option}={value}"]
        for pair in options.date_counts:
            words += ["--date-count"] + [f"{one}" for one in pair]
        if options.first_row_typed:
            words += [f"--first-row={options.first_row}"]
        if options.day_first:
            words += ["--day-first"]
        if options.metadata_rows:
            words += [f"--metadata-rows={options.metadata_rows}"]
        if options.delimiter:
            words += [f"--delimiter={options.delimiter}"]
        if options.sheet:
            words += [f"--sheet={options.sheet}"]
        if options.floor_chosen:
            words += [f"--smallest-group={options.smallest_group}"]
        if options.answers is not None:
            words += [f"--answers={options.answers}"]
        # ...and the installation's four (contract 4.6b.4; plan P4-D464).
        if options.name is not None:
            words += [f"--name={options.name}"]
        if options.replace_description:
            words += ["--replace-description"]
        if options.new_key:
            words += ["--new-key"]
        if options.private_folder is not None:
            words += [f"--private-folder={options.private_folder}"]
    if options.replace:
        words += ["--replace"]
    return words


def _twin_step(
    words: "list[str]",
    ask: "list[str | None] | str | None",
    before: str,
    folder_to_make: str,
    chain: "ChainRun | None",
    small_tables_refused: bool,
    internal_smallest_group: "int | None",
    bound_to: "tuple[int, int, str] | None" = None,
    unswitched: bool = False,
) -> results.Result:
    """Run one step of the twin as its own command, in a session of its own; return its result.

    The step shows on the twin's screen and reads from ``ask`` (None
    where nobody is asked); its result is the command's own, as `run`
    makes it for that command line. ``bound_to`` is the file a profile
    step handed its folder's own questions file must read (lane TT's
    repair); the questions its prompt puts, or would put, are kept on the
    twin's session (`_Session.promptable`).
    """
    parent = _current()
    assert parent is not None
    step = _Session(parent.screen, ask)
    step.twin_step = True
    step.before = before
    step.folder_to_make = folder_to_make
    step.bound_to = bound_to
    _OPEN.sessions += [step]
    try:
        verdict = _dispatch(words, chain, small_tables_refused, internal_smallest_group, unswitched)
    except (_Unusable, _HelpShown):
        verdict = results.UNUSABLE
    finally:
        del _OPEN.sessions[len(_OPEN.sessions) - 1]
    if step.promptable:
        parent.promptable = list(step.promptable)
    # ...and the questions whose answers stand, which the twin's last lines
    # count no more than profile's do (lane EZ-a's repair, LANE EZ RULINGS 4 (4)).
    parent.answers_standing += [one for one in step.answers_standing if one not in parent.answers_standing]
    return _result_of(step, verdict)


def _run_twin(
    options: _Options,
    chain: "ChainRun | None",
    small_tables_refused: bool,
    internal_smallest_group: "int | None",
    unswitched: bool = False,
) -> str:
    """Do the work of `synthtwin twin`; return the run's verdict (lane TT, plan P4-D460).

    Guarantees:

    - Order: the seed and the folder are settled, and the one overwrite
      rule decided from the six names, before the table is read; the
      profile step then reads the table once and puts its questions on
      screen where somebody is at the keyboard, before any file or the
      folder exists; `generate` and `validate` follow it in the same
      folder. A step that does not finish ends the run there.
    - The answers: a folder already holding this table's questions file
      hands it back to the profile step (`--answers`) and nobody is
      asked, so a second run asks nothing and reads the table as the
      first did; `--answers FILE` typed hands that file back, and the
      questions it leaves open are put at the keyboard, as `profile`
      puts them.
    - The result: each step's own result in `steps`; the verdict, the
      misses, the unjudged obligations, the carried entries, the tally
      and the refusal of the most severe step (the later of two alike);
      every step's files, cautions and leftovers in order; the profile
      step's questions; the next command its purposes `twin` and
      `answer-questions` name, where one is owed.
    - Boundary: the table is read by the profile step alone, once; the
      generate step never reaches the reader and the validate step never
      reaches the generator, each importing its modules in its own
      branch, as when the commands run apart. THE TABLE'S OWN PATH PASSES
      THE LOCALITY GATE FIRST (lane TT's repair; Codex's review of lane
      TT, item 2), its words checked before any call of the filesystem
      that involves it: on Windows `\\\\server\\share\\data.csv` with
      `--out-dir C:\\local` reached the check below, which resolves it,
      before the UNC check ran. And no name of the three steps may lead
      onto the table (`_twin_output_on_the_table`, Codex's item 1).
    """
    session = _current()
    assert session is not None
    table = f"{options.given}"
    seed, refusal = _seed_or_refusal(options.seed)
    if seed is None:
        _warn(refusal)
        return results.UNUSABLE
    try:
        source = pathlib.Path(validate_local_path(table, purpose="input"))
    except PathValidationError as error:
        _warn(_shown(error))
        return results.REFUSED
    _at(results.STEP_OUTPUTS)
    try:
        folder, to_make = _twin_folder(table, options.out_dir)
        named = _twin_outputs(table, folder)
    except PathValidationError as error:
        _warn(_shown(error))
        return results.REFUSED
    except errors.ProfileError as error:
        _warn(_shown(error), step=results.STEP_OUTPUTS)
        return results.REFUSED
    on_the_table = _twin_output_on_the_table(named, source)
    if on_the_table:
        _warn(on_the_table, step=results.STEP_OUTPUTS)
        return results.REFUSED
    if to_make and not _a_folder_can_be_made_in(folder.parent):
        _warn(errors.twin_folder_not_made(_shown(folder)), step=results.STEP_OUTPUTS)
        return results.REFUSED
    if not options.replace:
        taken = [target for target in named if _already_there(target)]
        if taken:
            _warn(
                errors.outputs_taken(
                    [_shown(target) for target in named],
                    [_shown(target) for target in taken],
                    errors.MAKING_AGAIN,
                ),
                step=results.STEP_OUTPUTS,
            )
            return results.REFUSED
    saved = named[2] if len(named) == 6 else None
    ask = session.ask
    # What the person typed, before the folder's own file is handed back:
    # the commands the run teaches are made from it (`_twin_again`).
    typed = options
    bound_to: "tuple[int, int, str] | None" = None
    if options.answers is None and saved is not None and pathlib.Path(saved).is_file():
        # HANDED BACK BY ITSELF ONLY TO THE FILE ITS ANSWERS NAME, READ AS
        # THEY WERE GIVEN (lane TT's repair; LANE TT RULINGS 1 items 3 and
        # 4): a questions file binding its answers to no file is not handed
        # back, nor one whose reading options this run gives otherwise; the
        # file it names is held to the profile step's own reading.
        from synthtwin import contract

        try:
            kept_file = contract.load_answers(f"{saved}")
        except (PathValidationError, errors.ProfileError) as error:
            _warn(_shown(error), step=results.STEP_INPUT)
            return results.REFUSED
        binding = _bound_reading(kept_file)
        if binding is None:
            _warn(errors.twin_answers_not_bound(_shown(saved)), step=results.STEP_INPUT)
            return results.REFUSED
        otherwise = _read_otherwise(options, binding[1], binding[2], binding[3])
        if otherwise is not None:
            _warn(
                errors.twin_answers_read_otherwise(_shown(saved), *otherwise),
                step=results.STEP_INPUT,
            )
            return results.REFUSED
        bound_to = binding[0]
        options = dataclasses.replace(options, answers=f"{saved}")
        ask = None
    session.steps += [
        _twin_step(
            _twin_words(_PROFILE, table, folder, options),
            ask,
            "",
            f"{folder}" if to_make else "",
            chain,
            small_tables_refused,
            internal_smallest_group,
            bound_to,
            unswitched,
        )
    ]
    reached = session.steps[0].verdict
    described = [one.path for one in session.steps[0].files if one.kind == results.FILE_DESCRIPTION]
    for command in (_GENERATE, _VALIDATE):
        if reached not in (results.NO_MISS, results.MISSED) or not described:
            break
        session.steps += [
            _twin_step(
                _twin_words(command, described[0], folder, options),
                None,
                reached,
                "",
                chain,
                small_tables_refused,
                internal_smallest_group,
                None,
                unswitched,
            )
        ]
        reached = _more_severe(reached, session.steps[len(session.steps) - 1].verdict)
    return _twin_ended(session, table, folder, typed, session.ask is not None)


# How many files, in the words the one overwrite rule counts them in.
_FILES_COUNTED = ("no files", "one file", "two files", "three files", "four files", "five files", "six files")


def _files_counted(count: int) -> str:
    """``count`` files in words: "six files", "five files", "one file"."""
    if 0 <= count < len(_FILES_COUNTED):
        return _FILES_COUNTED[count]
    return f"{count} files"


def _option_words(option: str, value: object) -> "list[str]":
    """An option and its value as the words a person types: two, or one joined by `=` where the value starts with a minus sign.

    argparse reads a word starting with `-` as an option of its own, so
    `--missing-value -99` is written `--missing-value=-99`, as
    `_typed_option` prints it. A fixed function of the two; raises nothing.
    """
    text = f"{value}"
    if text[:1] == "-":
        return [f"{option}={text}"]
    return [option, text]


def _twin_again(table: str, options: _Options) -> "list[str]":
    """The twin's command line as the person typed it, every option kept (lane TT's repair).

    The orchestrator's LANE TT RULINGS 2 (3) and RULINGS 1 item 5 (skeptic
    1's item 3, Codex's item 5): the commands a twin teaches dropped every
    option but `--out-dir`, so the one taught after a run stopped at a
    question was refused by the overwrite rule or asked nothing, and the
    answers command read the first sheet where the person had named
    `--sheet Study`, without their `--missing-value`, floor or seed.
    Here: `synthtwin twin TABLE`, then `--out-dir`, `--answers`,
    `--replace` and `--seed` where given, then each declaration the
    profile step reads in `_twin_words`'s order, each option and its value
    as `_option_words` writes them, `--date-count` with its two values, a
    flag alone. A seed of 0 is the one given where none is typed, so it is
    left out. A fixed function of its arguments; raises nothing.
    """
    words = ["synthtwin", _TWIN, table if table[:1] != "-" else os.path.join(".", table)]
    if options.out_dir is not None:
        words += _option_words("--out-dir", options.out_dir)
    if options.answers is not None:
        words += _option_words("--answers", options.answers)
    if options.replace:
        words += ["--replace"]
    if options.seed != "0":
        words += _option_words("--seed", options.seed)
    for option, values in (
        ("--person", options.persons),
        ("--identifier", options.identifiers),
        ("--code", options.codes),
        ("--measurement", options.measurements),
        ("--decimal-comma", options.decimal_commas),
        ("--twelve-hour", options.twelve_hours),
        ("--century", options.centuries),
        ("--date-column", options.date_columns),
        ("--keep-value", options.kept_values),
        ("--missing-value", options.missing_values),
    ):
        for value in values:
            words += _option_words(option, value)
    for pair in options.date_counts:
        words += ["--date-count"] + [f"{one}" for one in pair]
    if options.first_row_typed:
        words += _option_words("--first-row", options.first_row)
    if options.day_first:
        words += ["--day-first"]
    if options.metadata_rows:
        words += _option_words("--metadata-rows", options.metadata_rows)
    if options.delimiter:
        words += _option_words("--delimiter", options.delimiter)
    if options.sheet:
        words += _option_words("--sheet", options.sheet)
    if options.floor_chosen:
        words += _option_words("--smallest-group", options.smallest_group)
    return words


def _typed_words(words: "list[str] | tuple[str, ...]") -> str:
    """A command's words as the person types them, each value quoted for the shell (lane TT's repair).

    The words `_twin_again` makes: `synthtwin`, the command word and the
    path (`_typed_path`), then each option -- a flag alone, a word joined
    by `=` read as its option and value, `--date-count` with its two
    values, any other with the word after it -- and its value through
    `_typed_option`, so the line is the one lane TI's teaching lines
    print. A fixed function of the words and the platform; raises nothing.
    """
    line = f"{words[0]} {words[1]} {_typed_path(words[2])}"
    place = 3
    while place < len(words):
        word = words[place]
        if word[:2] == "--" and "=" in word:
            cut = _place_of(word, "=")
            line = f"{line} {_typed_option(word[:cut], word[cut + 1 :])}"
            place = place + 1
            continue
        if word == "--date-count" and place + 2 < len(words):
            line = (
                f"{line} {_typed_option(word, words[place + 1])} "
                f"{_shown(_quoted_for_the_shell(words[place + 2]))}"
            )
            place = place + 3
            continue
        if word in _SHORT_HELP and _SHORT_HELP[word][0] and place + 1 < len(words):
            line = f"{line} {_typed_option(word, words[place + 1])}"
            place = place + 2
            continue
        line = f"{line} {_shown(word)}"
        place = place + 1
    return line


def _twin_ended(
    session: _Session,
    table: str,
    folder: pathlib.Path,
    options: _Options,
    asked: bool,
) -> str:
    """Fill the twin's result from its steps, show its last lines, and return its verdict.

    ``options`` are the ones the person typed, before the folder's own
    questions file was handed back, so every command the run teaches is
    the person's own command line (`_twin_again`). Where the questions
    file holds questions still open, the next command is the one that
    puts them on screen at a terminal (`answer-questions`), whoever was at
    the keyboard: Enter leaves a question open, as nobody does (lane TT's
    repair 2; the orchestrator's LANE TT RULINGS 3 (1)). ``asked`` is
    whether somebody was at the keyboard, and chooses only the words the
    line opens with.
    """
    deciding = session.steps[0]
    for step in session.steps:
        if _more_severe(deciding.verdict, step.verdict) == step.verdict:
            deciding = step
    session.misses = deciding.misses
    session.unjudged = deciding.unjudged
    session.carried = deciding.carried
    session.tally = deciding.tally
    session.questions = session.steps[0].questions
    for step in session.steps:
        session.warnings += list(step.warnings)
        session.files += list(step.files)
        session.left_behind += list(step.left_behind)
        if step.floor is not None:
            session.floor = step.floor
            session.floor_lowered = step.floor_lowered
    if deciding.refusal is not None:
        session.step = deciding.refusal.step
        session.key = deciding.refusal.key
        session.refusal_words = [deciding.refusal.words]
        session.on_disk = deciding.refusal.on_disk
    first = session.steps[0]
    if first.refusal is not None and first.refusal.step == results.STEP_QUESTIONS:
        line = _typed_words(_next(results.PURPOSE_TWIN, *_twin_again(table, options)).words)
        _say(
            f"\nNothing was written. To answer the questions, run it again:\n"
            f"  {line}{_quoting_said(line)}"
        )
        return deciding.verdict
    if deciding.verdict not in (results.NO_MISS, results.MISSED):
        return deciding.verdict
    kept = [one.path for one in first.files if one.kind == results.FILE_QUESTIONS]
    # HOW MANY FILES, AS THE STEPS RECORDED THEM (lane TT's repair; Codex's
    # item 10): a questions file the profile step would not write -- its
    # name leading onto the description, a caution -- left five, and the
    # line said six.
    # ...THE PRIVATE REPORT AMONG THEM NEVER (LANE ST RULINGS 2 (5), plan
    # P4-D464): it is written outside the folder, for the person alone.
    in_the_folder = [one for one in session.files if one.kind != results.FILE_PRIVATE_REPORT]
    _say(
        f"\nThe twin's {_files_counted(len(in_the_folder))} are in:\n"
        f"  {_shown(folder)}"
    )
    open_now = [
        one
        for one in first.questions
        if one.section in (results.SECTION_ABOUT_FILE, results.SECTION_ASKED)
        and (one.column, one.role, one.reason) not in session.answers_standing
    ]
    # ...AND THE QUESTIONS THE ANSWERS COMMAND CAN PUT ON SCREEN, apart from
    # those answered in the file alone (lane TT's repair; Codex's item 9,
    # skeptic 1's item 5): the Safe Harbor questions and those about the
    # file itself are never put at a prompt, and the line counted them as
    # though they were (measured: 6 said, 3 put).
    # ...AND SINCE LANE EZ-a EVERY ONE OF THEM (plan P4-D479): where somebody
    # is at the keyboard, the rounds after the files put each entry no prompt
    # put, the Safe Harbor questions and those about the file among them.
    on_screen = list(open_now)
    if kept:
        _say(
            f"Its questions and the answers given stay in {_shown(kept[0])}: "
            f"the next run of synthtwin twin on this table and folder asks "
            f"nothing."
        )
        if open_now:
            # The person's own command line, into this folder, its
            # questions file handed back and its files written over:
            # taught wherever a question is still open, after Enter too
            # (lane TT's repair 2; the verify of repair 1 measured a
            # person who pressed Enter at 3 questions taught no command).
            # ...LESS EVERY TYPED DECLARATION AN ANSWER OF THAT FILE REPLACED
            # (lane EZ-a's second repair; Codex's item 1): handed back with
            # the file, a typed option is read as later than the file's kept
            # answer, and `--decimal-comma` typed over a record number
            # answered `identifier` at the first prompt published its values.
            typed_now = _typed_said(
                list(options.identifiers) + [one for one in options.persons if one not in options.identifiers],
                options.codes, options.measurements, options.decimal_commas, options.twelve_hours,
                options.date_counts, options.centuries, options.date_columns, options.day_first,
                options.delimiter, options.first_row, options.first_row_typed,
            )
            words = _twin_again(
                table,
                dataclasses.replace(
                    _options_left(options, _typed_replaced_in(pathlib.Path(kept[0]), typed_now)),
                    out_dir=f"{folder}", answers=kept[0], replace=True,
                ),
            )
            command = _next(results.PURPOSE_ANSWER_QUESTIONS, *words)
            line = _typed_words(command.words)
            in_the_file = len(open_now) - len(on_screen)
            opened = (
                f"{len(open_now)} question(s) are still open"
                if asked
                else f"Nobody was at the keyboard to answer {len(open_now)} question(s)"
            )
            said = (
                f"{opened}, so each of their columns kept the reading that "
                f"file names for it."
            )
            if on_screen:
                said = (
                    f"{said} {len(on_screen)} of them can be answered on "
                    f"screen: run this at a terminal\n  {line}"
                    f"{_quoting_said(line)}"
                )
                if in_the_file:
                    said = (
                        f"{said}\nThe other {in_the_file} are answered in "
                        f"{_shown(kept[0])} itself: write each answer beside "
                        f"'your_answer', then run that command."
                    )
            else:
                said = (
                    f"{said} They are answered in {_shown(kept[0])} itself: "
                    f"write each answer beside 'your_answer', then run this:"
                    f"\n  {line}{_quoting_said(line)}"
                )
            _say(said)
    return deciding.verdict


def main(
    argv: "list[str] | None" = None,
    chain: "ChainRun | None" = None,
    *,
    small_tables_refused: bool = True,
    internal_smallest_group: "int | None" = None,
    unswitched: bool = False,
) -> int:
    """Run the `synthtwin` command.

    THE CHAIN'S SWITCH IS ON (lane CHON, plan P4-D464, the landing that
    ships stage 6; contract 4.6b, S12 amended). `chain`, None from the
    console entry point, is made for every `profile` run from the command
    line's own options (`_shipped_chain`), and the tools and the tests may
    hand one in: `profile` describes between columns behind the
    installation's key, record and lock (4.6b.4), `generate` loads the
    description with its chain and `validate` measures it with V12's lines
    (lane CHv, plan P4-D430). A description whose `statistical` and
    `grain` are null is generated and measured exactly as before.
    - `unswitched`, keyword only and INTERNAL (plan P4-D464): False, the
      default and the only value a typed command ever runs with. True runs
      every command as it ran before that landing -- no installation, no
      chain, the loader of S12 word for word -- for the tests that pin that
      path and the before-and-after proof alone. No command-line option
      and no environment variable sets it.

    Guarantees:

    - Inputs: `argv` is the list of command-line arguments to parse, or
      `None` to parse `sys.argv[1:]`. Recognized: `--version`, `--help`,
      the `profile` command word with its options, the `generate`
      command word with `--seed`, `--out-dir` and `--replace`, the
      `validate` command word with `--twin`, `--out-dir` and
      `--replace`, the `doctor` command word with an optional table
      path and `--out-dir` (plan P4-D397), the `twin` command word with
      a table and the options of `profile` and `generate`, and the
      `help` command word with an optional command or `examples` (plan
      P4-D460). ONE OVERWRITE RULE (plan P4-D460): `profile`, `generate`,
      `validate` and `twin` each refuse, with code 1 and nothing
      written, a file already at one of their names, unless `--replace`
      is given (or, for `profile`, the answers round, `--answers`).
    - `small_tables_refused`, keyword only and INTERNAL (plan P4-D425): True, the
      default and the only value a typed command ever runs with, makes
      `profile` refuse, writing nothing, a table under
      `parsing.TABLE_ROW_FLOOR` rows that hold a value or, where a
      declared or answered person column repeats, under
      `parsing.TABLE_PEOPLE_FLOOR` people. False is for the suite's
      helpers and the measurement drivers, which run the command on
      small tables in this process; it leaves P4-D341's population
      floor and notice as they were. No command-line option, and no
      environment variable, sets it, and it changes no byte written for
      a table at or above the floor.
    - THE FLOOR OF 11 IS A MINIMUM (plan P4-D426, the owner's answer of
      2026-10-23). `--smallest-group` raises the smallest group size and
      never lowers it: a number under 11, or text that is no number, is
      refused with code 2 whichever command it is typed with, before
      anything is read or written. `generate` and `validate` refuse,
      with code 1 and nothing written, a description that records a
      smallest group size under 11, which a version before that plan
      could write.
    - `internal_smallest_group`, keyword only and INTERNAL (plan P4-D426;
      named without "floor" so the default-floor check stays whole): None,
      the default and the only value a typed command ever runs with, keeps
      the rules above. A whole number is for the suite's helpers and the
      measurement drivers, which describe tables at the floors they were
      written for: `profile` then works at that number, under 11
      included, with the warnings a lowered floor showed before that
      plan (the typed option is not read), and `generate` and `validate`
      read a description whose size is at least the smaller of that
      number and 11. A number under 1 is no floor at all: it is refused
      with code 2 by every command, before anything is read or written
      (`profile` refused it so before that plan; `generate` and
      `validate` would otherwise read a description at any floor). No
      command-line option, environment variable, questions file or
      settings file sets it -- synthtwin reads no settings file, and no
      environment variable but the two that place the chain's data
      folder behind `chain` (`installation.data_folder`: LOCALAPPDATA,
      XDG_DATA_HOME) -- and it changes no byte written at a floor of 11
      or more.
    - Return codes: 0 when the work finished; 1 when a file given could
      not be read or an output file could not be written, with a
      plain-language explanation on the error stream; 2 when an option's
      value was not usable, which includes naming one value both with
      `--keep-value` and with `--missing-value`, and a seed that is not a
      whole number in figures inside the stated range, and for a word on
      the command line that synthtwin does not recognize; 0 for `--help`.
      Every one is `results.exit_code` of the result `run` returns, and
      nothing else chooses it (plan P4-D395 part 4); `main` returns it
      and never raises `SystemExit` (the console entry point exits with
      what it returns). For
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

      `twin` returns the code of its most severe step: 0 when every step
      ran and nothing was missed, 3 when a step missed something (a fact
      the twin gave up, or an obligation the check found missed), 1 when
      a step could not run and 2 when the command line could not be
      used (plan P4-D395 part 4).
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
    # Whether somebody is there is asked before the run opens, so the
    # seam the suite patches (`_there_is_somebody_to_ask`) decides here
    # as it always did. The internal settings are handed on as they came.
    result = _run(
        argv,
        TERMINAL,
        TERMINAL if _there_is_somebody_to_ask() else None,
        chain,
        small_tables_refused,
        internal_smallest_group,
        unswitched,
    )
    return results.exit_code(result)


def run(
    argv: "list[str] | None" = None,
    *,
    screen: "list[tuple[str, str]] | str | None" = None,
    ask: "list[str | None] | str | None" = None,
    chain: "ChainRun | None" = None,
    small_tables_refused: bool = True,
    internal_smallest_group: "int | None" = None,
    unswitched: bool = False,
) -> results.Result:
    """Run one command line and return what it did, printing nothing (plan P4-D395 part 3).

    Guarantees:

    - Inputs: ``argv`` is the words a person types after `synthtwin`,
      read by the same parser as `main` (None reads `sys.argv[1:]`).
      ``screen`` is `TERMINAL` (the terminal: `main`'s), or a list to
      which the run adds ``(stream, text)`` -- "out" or "err", and
      exactly the characters the terminal is to show, the display
      boundary already applied -- at the moment and in the order the
      command shows them, so the disclosure still reaches the person
      before the files exist (plan P1-D6) and a run stopped while writing
      still shows what it shows; None shows it nowhere. ``ask`` is
      `TERMINAL` (the person at the terminal, `input`'s prompt its own),
      or the lines a person types, read in order, None or the end of the
      list where they ended input there; the question and the request to
      type again reach the person through ``screen``. Without ``ask`` no
      question is put and nothing is read. Both are data and never a
      function: the offline audit admits no call of a function a caller
      hands in (plan D6.2; plan P4-D437). ``chain``, ``small_tables_refused``,
      ``internal_smallest_group`` and ``unswitched`` are `main`'s, with the
      same meanings, and INTERNAL: no option or environment variable sets them.
    - Given neither ``screen`` nor ``ask``, nothing reaches standard
      output or the error stream by any route of this package -- a
      message, argparse's help or usage text -- nothing is read from
      standard input, `sys.exit` is not called and `SystemExit` is not
      raised: `--help`, `--version` and no words at all return results,
      and a word the parser does not know returns `unusable`. The files
      are written as the command writes them.
    - Errors raised: Ctrl-C anywhere but at a prompt still ends the run
      (`KeyboardInterrupt` passes), and an exception no refusal names
      still surfaces: a defect stays loud. Every refusal the command
      catches is a `refused` result instead, its words shown as before.
    - Determinism and boundary: as `main`'s. Each command's modules are
      still imported inside its own branch (plans P2-D1, P3-D1), so a
      validate run reaches no generator.
    - ONE RUN AT A TIME IN A PROCESS (a stated limit, plan P4-D437): the
      run in progress is found through one module-wide list of open
      sessions, so two threads calling `run` (or `main`) at once can each
      receive the other's command, screen text or misses (measured at
      lane S5a's skeptic 1: 82 of 600 results crossed). Run them one
      after another, or in separate processes.
    """
    return _run(
        argv, screen, ask, chain, small_tables_refused, internal_smallest_group, unswitched
    )


def _run(
    argv: "list[str] | None",
    screen: "list[tuple[str, str]] | str | None",
    ask: "list[str | None] | str | None",
    chain: "ChainRun | None",
    small_tables_refused: bool,
    internal_smallest_group: "int | None",
    unswitched: bool = False,
) -> results.Result:
    """The run `main` and `run` share: one session opened and closed, one result."""
    session = _Session(screen, ask)
    _OPEN.sessions += [session]
    try:
        verdict = _dispatch(
            argv, chain, small_tables_refused, internal_smallest_group, unswitched
        )
    except _Unusable:
        verdict = results.UNUSABLE
    except _HelpShown:
        session.command = results.HELP
        verdict = results.NO_MISS
    finally:
        del _OPEN.sessions[len(_OPEN.sessions) - 1]
    return _result_of(session, verdict)


def _result_of(session: _Session, verdict: str) -> results.Result:
    """The session's result, under the verdict the run ended with.

    A run that finished with a miss is `missed` whatever its branch
    returned; a refusal carries its step (the one the call site named,
    else the step the run was at), its catalog key and its words, and
    an unusable command line the step `command-line`.
    """
    if verdict == results.NO_MISS and session.misses:
        verdict = results.MISSED
    refusal: "results.Refusal | None" = None
    if verdict in (results.REFUSED, results.UNUSABLE):
        step = session.step or session.phase
        if verdict == results.UNUSABLE:
            step = results.STEP_COMMAND_LINE
        words = ""
        for line in session.refusal_words:
            words = line if not words else words + "\n" + line
        refusal = results.Refusal(step, session.key, words, session.on_disk)
    return results.Result(
        command=session.command,
        verdict=verdict,
        misses=session.misses,
        unjudged=session.unjudged,
        carried=session.carried,
        tally=session.tally,
        floor=session.floor,
        floor_lowered=session.floor_lowered,
        warnings=tuple(session.warnings),
        questions=session.questions,
        files=tuple(session.files),
        left_behind=tuple(session.left_behind),
        next_command=session.next_command,
        refusal=refusal,
        steps=tuple(session.steps),
    )


def _dispatch(
    argv: "list[str] | None",
    chain: "ChainRun | None",
    small_tables_refused: bool,
    internal_smallest_group: "int | None",
    unswitched: bool = False,
) -> str:
    """Read the command line and run its command; return the run's verdict.

    The body `main` had before results (plan P4-D395): every refusal it
    catches is shown as before and answered `refused`, and the step a
    stop was at is read off the session. THE SWITCH (plan P4-D464): a
    `profile` run handed no `chain` is given the shipped one
    (`_shipped_chain`), `generate` and `validate` read the description
    with its chain, unless ``unswitched``.
    """
    session = _current()
    assert session is not None
    session.command = _command_word(argv)
    options = _parse_arguments(argv, internal_smallest_group)
    if _no_floor_at_all(internal_smallest_group):
        return results.UNUSABLE
    # A NAME THAT WOULD LEAVE ITS FOLDER IS REFUSED BEFORE ANY WORK (plan
    # P4-D464): the private report's file and the record's entry are named
    # by it.
    if options.name is not None:
        refused_name = _name_refusal(options.name)
        if refused_name:
            _refuse_the_command_line(refused_name)
    switched = not unswitched
    if unswitched:
        chain = None
    elif chain is None and options.command == _PROFILE:
        chain = _shipped_chain(options)
    # The least smallest group size a description `generate` or
    # `validate` reads may record (plan P4-D426).
    least_read = (
        _SMALLEST_GROUP
        if internal_smallest_group is None
        else min(internal_smallest_group, _SMALLEST_GROUP)
    )

    if options.version:
        session.command = results.VERSION
        _say(_version())
        return results.NO_MISS

    if options.command == _DOCTOR:
        session.command = results.DOCTOR
        return _run_doctor(options.given, options.out_dir)

    # ONE PAGE FOR EACH COMMAND, AND THE EXAMPLES (lane TT, plan P4-D460).
    if options.command == _HELP_WORD:
        session.command = results.HELP
        return _run_help(options.given)

    # THE WHOLE JOURNEY IN ONE COMMAND (lane TT, plan P4-D460).
    if options.command == _TWIN and options.given is not None:
        session.command = results.TWIN
        return _run_twin(options, chain, small_tables_refused, internal_smallest_group, unswitched)

    named = options.given
    if named is None or options.command is None:
        session.command = results.STATUS
        _say(_STATUS.format(version=_version(), repo=_REPO_URL))
        return results.NO_MISS

    generating = options.command == _GENERATE
    validating = options.command == _VALIDATE
    try:
        if generating:
            return _run_generate(
                named,
                options.out_dir,
                options.seed,
                options.replace,
                least_read,
                chain=switched,
            )
        if validating:
            return _run_validate(
                named,
                options.twin,
                options.out_dir,
                options.replace,
                options.sheet,
                least_read,
                chain=switched,
            )
        session.typed = options
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
            options.first_row_typed,
            chain=chain,
            small_tables_refused=small_tables_refused,
            replace=options.replace,
            persons_given=options.persons,
        )
    except PathValidationError as error:
        # The message is treated as a VALUE, not as something synthtwin
        # composed: it carries the path the user typed, and the builders
        # that place it there do not show it safely (review item
        # P1-R6-F11). Every message in the catalog is one paragraph, so
        # showing the line feed too costs nothing and closes the last
        # way a path can forge a line of its own.
        _warn(_shown(error))
        return results.REFUSED
    except errors.ProfileError as error:
        # A refusal of method G12 names its catalog key, and is a refusal
        # of the description's content wherever it is raised.
        if isinstance(error, errors.KeyedRefusal):
            session.key = error.key
            session.step = session.step or results.STEP_CONTENT
        _warn(_shown(error))
        # The write transaction's own refusal names what is on disk in its
        # message, and holds that account apart too: the result carries it
        # as such (lane S5a's repair 2, Codex's item 8), shown as the words
        # show it.
        if isinstance(error, errors.TransactionRefusal) and error.on_disk:
            session.on_disk = parsing.visible_lines(_shown(error.on_disk))
        return results.REFUSED
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
        session.step = results.STEP_MEMORY
        return results.REFUSED
    except RecursionError:
        # A STEP NESTED PAST PYTHON'S OWN LIMIT ends here and never as a
        # stack trace (plan P4-D380). The pool walk that did it on columns
        # of numbers written to full precision carries its own stack now;
        # this is what any step that still reaches the limit says, on the
        # file the person typed, whichever of the three commands it was.
        _warn(errors.stopped_nested_too_deep(_shown(named)))
        session.step = results.STEP_NESTING
        return results.REFUSED


def _shipped_chain(options: _Options) -> ChainRun:
    """The switch of a typed `profile` run (lane CHON, plan P4-D464): its four options, the rule steps on, the layer's sub-switch."""
    return ChainRun(
        name=options.name,
        replace_description=options.replace_description,
        new_key=options.new_key,
        private_folder=options.private_folder,
        rules=True,
        patient_layer=_PATIENT_LAYER_SHIPPED,
    )


def _name_refusal(name: str) -> str:
    """Why `--name NAME` cannot be used ('' where it can): empty, a folder's part, or a control character (plan P4-D464)."""
    shown = _shown(name)
    if not name or name in (".", ".."):
        return (
            f"The name given after --name, '{shown}', names no table. Give the table a name of "
            "letters, figures and spaces, for example --name clinic-visits, or leave --name out to use "
            "the file's own name."
        )
    for character in name:
        if character in ("/", "\\") or ord(character) < 32 or ord(character) == 127:
            return (
                f"The name given after --name, '{shown}', holds a slash, a backslash or a control "
                "character, so it would name a place outside synthtwin's own folder. Give the table a name "
                "of letters, figures and spaces, for example --name clinic-visits."
            )
    return ""


def _run_help(topic: "str | None") -> str:
    """Show `synthtwin help [TOPIC]`: the index, one command's page, or the examples (lane TT, plan P4-D460).

    A word no page answers to is refused as an unusable command line,
    with the words to type instead (exit 2), and nothing else is shown.
    """
    if topic is None:
        _say(_HELP_INDEX, "")
        return results.NO_MISS
    if topic == _EXAMPLES:
        _say(_EXAMPLES_PAGE, "")
        return results.NO_MISS
    if topic in _READ_BY:
        _say(command_page(topic), "")
        return results.NO_MISS
    _warn(
        f"synthtwin has no help page called {_shown(topic)}. Type one of  "
        f"synthtwin help twin  ,  synthtwin help profile  ,  synthtwin help "
        f"generate  ,  synthtwin help validate  ,  synthtwin help doctor  or  "
        f"synthtwin help examples  , or  synthtwin --help  for every option "
        f"in full."
    )
    return results.UNUSABLE


def _command_word(argv: "list[str] | None") -> str:
    """The command a command line names, read before it is parsed, or "".

    The first of `profile`, `generate`, `validate`, `doctor`, `twin` and
    `help` among the words, so a command line refused before its command
    ran still says which command it was for; the branch that runs sets it
    again.
    """
    words = sys.argv[1:] if argv is None else argv
    for word in words:
        if word in (_PROFILE, _GENERATE, _VALIDATE, _DOCTOR, _TWIN):
            return f"{word}"
        if word == _HELP_WORD:
            return results.HELP
    return ""


if __name__ == "__main__":
    sys.exit(main())

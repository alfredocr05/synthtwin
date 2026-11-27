"""Building and writing the profile document (plan P1-D5, P1-D11).

The profile is the boundary artifact: everything downstream -- the
generator, the validator, the quality report -- will read this file and
never the real table. It is therefore written to be read by a program
AND by a person who wants to check what left their compliant
environment.

Three properties are deliberate:

* Nothing that varies between runs appears in it. There is no
  timestamp, no source path, no machine name, and no random anything,
  so the same table always produces the same bytes and a golden-hash
  test means what it says.
* Everything the rules decided travels with the result: the settings
  that produced the roles, the evidence for each role, and the notes
  saying what was withheld and why. A reader never has to guess which
  version of the rules made this file.
* NOTHING ELSE IS IN IT, and that is checked rather than intended
  (plan P2-D2). `check_publication` below walks the FINISHED document
  to its last leaf and refuses anything the publication rules do not
  authorize: a value at a place they do not allow, a count that never
  cleared the small-cell floor, a key nobody wrote a rule for, and any
  sentence this package cannot write again from the enumerated form
  the sentence carries. It runs at the end of `build_document`, after
  the per-column notes have been lifted to the top level, because the
  document that is about to be serialized is the one thing worth
  checking.

TWO THINGS THAT USED TO LIVE HERE NOW LIVE ELSEWHERE, and the move is
the whole of the change to them (plan P2-D1). The canonical serializer
is in `canonical.py` and the write transaction is in `writing.py`,
because both are code Phase 2's generator has to reach and this module
imports the reader's own table type -- which every module importing this
one would then inherit, whether or not it ever calls it. Both are
re-exported below under the names they had, so no caller written against
the earlier shape has to change.

Imports here stay within the allowlist (plan D6.2): dataclasses,
importlib.metadata.version, pathlib, and this package's own modules.
"""

import dataclasses
import importlib.metadata
import pathlib
import typing

from synthtwin import (
    asking,
    calendar_clock,
    calendar_rules,
    canonical,
    date_counts,
    dialect,
    errors,
    grains,
    native,
    offset_rules,
    parsing,
    progress,
    reading,
    taxonomy,
    twin_checks,
    workbook,
    writing,
)
from synthtwin.paths import validate_local_path
from synthtwin.reading import Table

# WHAT THIS MODULE STILL HANDS ON, after the two moves above (plan
# P2-D1). `profile.serialize`, `profile.write_both_files`,
# `profile.write_text_file`, `profile.is_the_same_file`,
# `profile.DiskState` and the transaction's own constants all still mean
# exactly what they meant: these names are the same objects, reached
# from the modules that now hold them.
#
# They are written as plain assignments rather than as imported names so
# that a reader of this module sees a list of what it hands on, in one
# place, rather than a longer import line whose purpose is not stated.
# Nothing here wraps or adapts: a caller of `profile.write_both_files`
# calls the transaction itself.
#
# What a caller may NOT do through these names is replace one for a
# test. Rebinding `profile.write_both_files` rebinds this alias and not
# the function the transaction's own code calls, so a test that stands
# something else in the way of one of these does it in `writing`, where
# the calls are.
serialize = canonical.serialize
DiskState = writing.DiskState
write_both_files = writing.write_both_files
write_text_file = writing.write_text_file
is_the_same_file = writing.is_the_same_file
PART_SUFFIX = writing.PART_SUFFIX
KEPT_SUFFIX = writing.KEPT_SUFFIX
WORKING_NAME_ATTEMPTS = writing.WORKING_NAME_ATTEMPTS
CLAIM_MADE = writing.CLAIM_MADE
CLAIM_REACHED = writing.CLAIM_REACHED

# Version 2: the settings block no longer reproduces the values the
# person declared with --keep-value and --missing-value; it records how
# many were named each way and the rule that matched them (review item
# P1-R7-F2). The field exists so that a change of this kind is explicit
# rather than something a consumer has to detect (plan P1-D5), so it
# moves with the change rather than after it.
#
# The wording of DECLARATION_PUBLICATION below was corrected afterwards
# without moving this number, and deliberately: no key changed shape and
# no key appeared or left, so a consumer's reading code is unaffected,
# and the token IS its own discriminator -- it names the rule in force,
# which is the one thing it exists to do. Version 2 has never been
# published, so the only profiles carrying the earlier token were
# written by a development tree.
#
# Version 3: a column the person declared with --identifier carries one
# new key, `n_distinct_by_occurrences` -- how many different values of
# it cover one row, two rows, and so on (review item P1-R8-F4, closed by
# owner decision). A key APPEARED, and a consumer that reads a v2
# profile will not find it, which is exactly the kind of change this
# number exists to make explicit rather than leave to be detected. Under
# v2 two declared columns with different repetition patterns serialized
# to identical bytes, so the profile could not be the generator's only
# input for them; `taxonomy._n_distinct_by_occurrences` states the key
# form and what the mapping does and does not disclose. Nothing else
# about the document moved: no other role gained or lost a key, and no
# value of any column is published that was not published before.
#
# Version 4: five additions, no removals, and every version 3 key keeps
# its name, its type and its meaning. `docs/spec/profile-contract-v4.md`
# is the normative statement of all of them; in one line each:
#
# 1. every column carries `statistical_type`, `quality_state` and
#    `structural_role` beside its role, and a consumer dispatches on
#    those three rather than on the role name (plan P2-D3);
# 2. `n_distinct_by_occurrences` -- version 3's declared-identifier key
#    -- is carried by free-text and unrepresentable-number columns too,
#    in the identical shape (plan P2-D4);
# 3. one top-level `relationships` block, eight keys, every one null:
#    this version carries no cross-column structure and says so in a
#    shape a later version can fill one slot of (plan P2-D5);
# 4. every PUBLISHED label carries `variants` and `variants_withheld`
#    -- how the rows that share it actually wrote it, under the same
#    small-cell floor that governs the label itself (owner decisions 9
#    and 11);
# 5. count and continuous columns carry `numeric_styles` -- how many
#    cells used each of six spelling forms, under the floor (owner
#    decision 10).
#
# Two of the five publish something version 3 did not: a spelling of a
# published label, and a count of cells per spelling form. Both are
# governed by the floor, and the first crosses nothing a whole label
# does not already cross -- a variant is a way of writing a label the
# profile already names, held to the same line. `SECURITY.md`, the
# summary and the taxonomy's own `_variants` say so where a reader will
# meet it.
#
# Version 5: three changes, no removals, and every version 4 key keeps
# its name and its type. `docs/spec/profile-contract-v5.md` is the
# normative statement, carrying version 4 by reference; plan amendment
# A-P3-27 is the ruling behind it. In one line each:
#
# 1. a `missing_by_source` key is the source spelling CHARACTER FOR
#    CHARACTER, and the display boundary is applied where a key is shown
#    rather than before it is stored -- which is what `variants` next
#    door has always done (contract 5 C5-1);
# 2. the two counts version 4 kept inside that map under synthtwin's own
#    words move out to `n_missing_blank` and `n_missing_withheld`, so
#    the map holds one key space, the table's own (contract 5 C5-11);
# 3. each of the two declaration records gains `built_in_texts` and
#    `built_in_numbers`, naming which members of synthtwin's own
#    twenty-three published words were typed -- and never the person's text
#    (contract 5 section 6).
#
# WHAT THAT COSTS AND WHAT IT BUYS. It buys a description a reader can
# rebuild the reading rule from: version 4 described two tables needing
# opposite readings with byte-identical files, so a table checked
# against its own genuine description came back with obligations
# reported as missed. It costs a version bump with no upgrade path -- a
# version 4 description is refused and the person is told to describe
# their table again with the same declarations -- and one bounded
# lowering of the Phase 1 settings-block rule, priced in
# `DECLARATION_PUBLICATION` below. Change 1 publishes, for a group the
# floor already permitted to be named, which of the spellings sharing
# one printable form it was; it is empty for every ordinary word, and in
# one corner it publishes strictly LESS, because the floor now falls on
# the exact spelling rather than on the escaped one.
PROFILE_VERSION = 6

# The two files a run writes, as suffixes added to the table's name.
PROFILE_SUFFIX = "-profile.json"
SUMMARY_SUFFIX = "-profile.txt"
# THE QUESTIONS FILE (amendment A-P4-58), and it is written on
# EVERY run of this command.
#
# WHY UNCONDITIONALLY, which is a decision and not an oversight.
# A file this command leaves in a person's folder must be named on
# every surface that states the institution's handling rules, and
# a file that exists only sometimes makes every one of those
# sentences conditional -- "a full run leaves the files below, and
# one more where synthtwin had a question" -- on eight surfaces at
# once. A file that always exists needs one true sentence instead.
# It is also the honest record of the check: a table with nothing
# ambiguous in it gets a file saying so, which is how a person
# knows the tool looked rather than assuming it did.
#
# It is written OUTSIDE the profile transaction: the description
# and its summary are one outcome because either alone is a
# failure state, and nothing is built from this one.
QUESTIONS_SUFFIX = "-questions.json"

# THE RESERVED CROSS-COLUMN MANIFEST (plan P2-D5, owner decision 3).
#
# Eight names, each carrying `null`, because this version of synthtwin
# preserves no structure BETWEEN columns and a consumer must be able to
# see that stated rather than infer it from an absence. A block reserved
# in the shape it will eventually take is what lets a later phase fill
# one slot without moving any other key, and filling any of them
# advances PROFILE_VERSION; versions 4 and 5 are both versions in which
# all eight are null.
#
# The names are written out here, sorted, rather than assembled
# anywhere: they are the whole of the contract's membership rule for
# this block, and a reader checking a document against the contract
# reads them in one place.
RELATIONSHIP_SLOTS = (
    "deterministic",
    "grain",
    "hierarchy",
    "keys",
    "missing_data_process",
    "statistical",
    "temporal",
    "validation_targets",
)

# What the profile's SETTINGS BLOCK records about a value the person
# declared with --keep-value or --missing-value, what it deliberately
# does not, and -- just as important -- what it does not claim about the
# rest of the document.
#
# A declaration is compared against every cell of every column, and the
# person types one BECAUSE that value is in their table. Writing the
# spelling into the settings therefore publishes a source value out of
# every column at once -- including the columns whose values never
# appear in a profile at all (record numbers, free text) and the labels
# held back for being shared by too few rows. The settings block did
# exactly that: a rare narrative value supplied as --missing-value was
# serialized verbatim while the column holding it published nothing,
# and the summary said nothing about it (review item P1-R7-F2).
#
# THE RULE: the settings block carries the POLICY -- how many values
# were named each way, and the rule that matched them -- and never a
# spelling of the person's own. That is what the settings block was
# always for: it tells a reader WHICH RULES produced a profile, and in
# the settings block never which values the table held. A column's own
# description is another matter and is section 3.2's, not this rule's:
# a declared spelling stands there, which is why the denial above names
# the block it holds in. No per-column exemption is
# made, and the reasons are that a declaration is table-wide (one
# spelling is compared against every cell of every column, so it could
# only be published if it were publishable in all of them, free-text and
# record-number columns included), that the typing of it is itself
# evidence about the source table whether or not any one cell matches,
# and that an exemption would have to be re-derived for every role and
# every publication rule added later -- which is a rule that will one
# day be missed.
#
# FROM CONTRACT VERSION 5 THE RULE HAS ONE EXCEPTION, AND THIS LOWERS
# THE PHASE 1 BAR BY EXACTLY THAT MUCH (owner ruling 2026-08-17, plan
# amendment A-P3-27, contract 5 section 6.6). The two declaration
# records also name WHICH MEMBERS of synthtwin's own twenty-three published
# words were typed: the ten spellings this package reads as "no value"
# and the three stand-in numbers it judges, listed in the contract's own
# appendix and identical in every installation.
#
# The size of the loss, because a lowering is stated at its size or it
# is not stated: what is added is which members of a THIRTEEN-MEMBER
# first-party list were among the values typed. It carries no count of
# cells, no column and no row; the MEMBER's spelling is written and
# never the person's, so their spacing and their capitals do not travel;
# and it is written identically whether or not the word occurs in the
# table (`taxonomy.built_in_values_named` reads no cell), so the field
# is not evidence that any cell wore the word. What a reader can still
# infer is that somebody usually types a word because it is in their
# table -- so the guess a version 4 description made coarsely ("one
# value was rescued") is made at twenty-three words. The word guessed at
# HERE can never be a name, a code, a diagnosis or a free-text answer,
# because a value outside the list is written nowhere in this block.
# That is a sentence about this block, and the paragraph below says why
# it may not be read any wider.
#
# What is NOT lowered: `values_recorded` stays false, a declared value
# that is not a member of the published vocabulary is recorded nowhere
# in the settings, and every publication class and every floor rule is
# unchanged.
#
# THE TOKEN BELOW KEEPS ITS VALUE, and that is a decision rather than an
# oversight. Contract 5 fixes the settings block at the same fifteen
# keys and names every key whose meaning moves; this one is not among
# them, and the loader admits exactly one word here. What the token says
# is still true of the block: what it carries about a declaration is
# counts and this package's own words, and the columns are unchanged.
#
# WHAT THIS RULE DOES NOT SAY. It governs the settings block and nothing
# else. Declaring a value does not withdraw that value from its own
# column: one named with --keep-value is data from that point on and is
# described wherever its column publishes values, and one named with
# --missing-value is counted as absent while the word
# itself is written into the description -- its spelling standing in
# `missing_by_source`, character for character, under the same
# small_cell_floor and the same role rule as any other missing spelling. The first wording of this token,
# `counts_only_no_spellings`, read as a claim about the whole document,
# and that claim is false: 200 readings and three cells of `-999`,
# profiled with `--keep-value -999`, publish `"min": -999.0`. That
# publication is CORRECT -- a kept value is an ordinary number of the
# column and a range is made of real values -- and it is not "counts
# only, no spellings". The token now names its own scope, so that a
# consumer or an auditor reading it cannot draw the wider conclusion.
#
# THE TOKEN NAMED ITS SCOPE AND THE PROSE AROUND THE PRODUCT DID NOT
# (review item P3-V9-F1). The paragraph above has been right since
# Phase 1 and the settings rule has never been wider than this block --
# and the profiler's own summary page, `SECURITY.md` and contract 5
# section 6 all went on denying, with no scope attached, that a word
# outside the twenty-three was written anywhere at all. The one that
# mattered was the summary: it printed `counted as missing: <the
# person's word> (12)` and, four screens below, that synthtwin would
# not keep any other word they typed. Both are now scoped where they
# are said, the summary names the words the columns kept, and the
# claim inventory holds every such sentence in this repository to the
# publication rules below rather than to a list somebody maintains.
DECLARATION_PUBLICATION = "settings_counts_only_columns_unchanged"


@dataclasses.dataclass(frozen=True)
class WrittenProfile:
    """Where a run put its two files, and what it put in them."""

    document: dict[str, object]
    profile_path: pathlib.Path
    summary_path: pathlib.Path




def _version() -> str:
    """The installed synthtwin version, or a plain placeholder."""
    try:
        return importlib.metadata.version("synthtwin")
    except Exception:  # noqa: BLE001 -- the import allowlist (plan
        # D6.2) permits only importlib.metadata.version, so the
        # specific PackageNotFoundError name cannot be referenced.
        return "0+unknown"


def _declaration_record(spellings: "tuple[str, ...]") -> dict[str, object]:
    """How many values were declared this way, and which of OUR words.

    `n_declared` counts DECLARATIONS and not keystrokes (contract 5
    C5-18 as amended; review item P3-V9-F7, plan amendment A-P3-37).
    `--missing-value n/a --missing-value " N/A "` is two things typed
    and one declaration: the producer's own matching rule folds them
    together and no description can tell them apart afterwards, so a
    consumer subtracting the two vocabulary lists from this count to
    learn how many words of the PERSON'S own were named used to be told
    there was one when there was none. `taxonomy.declarations_named`
    holds the rule and its docstring holds the reason.

    Guarantees:

    - Inputs: the spellings the person typed for one of the two options.
    - Determinism: the record depends only on those spellings, and on
      their set rather than their order. Both lists are sorted and
      pairwise distinct, so two runs with the same options write the
      same bytes (contract 5 C5-K2).
    - Errors raised: none.
    - Boundary: no spelling the person typed reaches the result, so
      nothing in the settings block can carry one out of this machine
      (review item P1-R7-F2). The two lists carry
      MEMBERS of synthtwin's own published vocabulary and nothing else
      (contract 5 C5-17); `taxonomy.built_in_values_named` is the whole
      of the rule, and it reads no cell of any table, so the record is
      the same whether or not the named word occurs (C5-16). What that
      gives up, at its size, is in DECLARATION_PUBLICATION above.

    The shape is deliberately NOT a list of spellings. A consumer
    holding a profile written before this rule finds one under the same
    key; one written after it finds this record, and can tell the two
    apart without guessing. Dropping the key instead would have made the
    two indistinguishable, which is the failure this shape avoids --
    which is also why `values_recorded` keeps its name and its value
    beside the two new lists rather than being retired (contract 5
    C5-S7, decision 13.9).
    """
    texts, numbers, days = taxonomy.built_in_values_named(spellings)
    return {
        "built_in_dates": list(days),
        "built_in_numbers": list(numbers),
        "built_in_texts": list(texts),
        "n_declared": taxonomy.declarations_named(spellings),
        "values_recorded": False,
    }


def _named_once(names: "list[str]") -> "list[str]":
    """One declaration's column names, in rising order, each of them once.

    THE TOOL WROTE A DESCRIPTION IT COULD NOT READ (review item
    P4-G3-R2-F7). Every declaration takes `--option NAME` and may be
    given more than once, so a person who types `--code dose --code
    dose` -- by repeating a line, or by pasting a command twice -- got
    a settings array holding `dose` twice. The contract requires these
    names to rise and to be distinct, so the loader then REFUSED the
    file, with a message telling the person to make the description
    again by running the same command, which reproduces the same file.
    They had done nothing wrong and had no way out of the loop.

    It is fixed HERE, in the producer, rather than in the command-line
    layer, because every path that builds a description passes through
    this block and the fault is in what gets WRITTEN. Saying a thing
    twice is not an error a person needs to be told about: they asked
    for the column to be read one way, and it is.

    This predates the fourth declaration and reached all four.

    Guarantees: accepts the names as given; returns them sorted with
    repeats removed. Determinism: a fixed function of the input.
    Raises nothing. No I/O of any kind.
    """
    once: "list[str]" = []
    for name in sorted(names):
        if once and once[len(once) - 1] == name:
            continue
        once += [name]
    return once


def notes_for_a_small_population(
    population: int, unit: str, line: int
) -> "list[taxonomy.Note]":
    """The table-wide note a small population carries, or none (P4-D341).

    ONE SENTENCE, BUILT ONCE. It is an enumerated form like every other
    sentence of a description, so `check_publication` rebuilds it from
    its two arguments -- the population and the word it was counted in
    -- and refuses the document if it cannot. The description carries
    it and every page of a run renders it from there, so the screen and
    the pages cannot say two different things.

    THE LINE IS PASSED IN and is not this module's. Which populations
    get a notice is the COMMAND's rule and is applied where the table
    is read; nothing here refuses a table, and `build_document` still
    describes one of any size. This function renders what it is told
    to.

    Guarantees: accepts the population, the unit word and the line;
    returns one note below the line and none at or above it.
    Determinism: a fixed function of the three. Errors raised:
    ValueError where the unit is not one of this package's two words,
    which is `taxonomy.note`'s own refusal. No I/O of any kind.
    """
    if population >= line:
        return []
    return [
        taxonomy.note(
            taxonomy.NOTE_SMALL_POPULATION, (population, unit)
        )
    ]


def _settings_block(
    settings: taxonomy.Settings,
    forced_identifiers: list[str],
    forced_codes: list[str],
    forced_measurements: list[str],
    forced_decimal_commas: list[str],
    forced_metadata_rows: int = 0,
    forced_delimiter: str = "",
) -> dict[str, object]:
    """The rules that produced this profile, recorded inside it.

    Every setting is written out by name. The offline policy forbids
    reaching an attribute through a name computed while the program
    runs (plan D6.2), and a hand-written list is what a reader can
    check anyway. A setting added to Settings and forgotten here fails
    the completeness test in the suite, which compares this block with
    the dataclass's own field list.

    Two of those settings are recorded by POLICY rather than by value:
    `kept_values` and `declared_missing_values` hold values of the real
    table, so what appears here is how many were named each way, beside
    the matching rule and the publication rule that governs them. The
    block still carries a key for every field of Settings, so the
    completeness check is unchanged; what changed is that two of those
    keys no longer reproduce source text (review item P1-R7-F2).
    """
    return {
        "small_cell_floor": settings.small_cell_floor,
        "identifier_uniqueness": settings.identifier_uniqueness,
        "identifier_minimum_rows": settings.identifier_minimum_rows,
        "minimum_parse_rate": settings.minimum_parse_rate,
        "categorical_share": settings.categorical_share,
        "categorical_ceiling": settings.categorical_ceiling,
        "categorical_floor": settings.categorical_floor,
        "sentinel_outlier_iqr_multiple": (
            settings.sentinel_outlier_iqr_multiple
        ),
        "sentinel_minimum_share": settings.sentinel_minimum_share,
        "kept_values": _declaration_record(settings.kept_values),
        "declared_missing_values": _declaration_record(
            settings.declared_missing_values
        ),
        "declaration_matching": settings.declaration_matching,
        "declaration_publication": DECLARATION_PUBLICATION,
        "near_threshold_slack": settings.near_threshold_slack,
        "day_first": settings.day_first,
        "long_tail_minimum_level": settings.long_tail_minimum_level,
        # WHICH DECLARED COLUMNS NAME THE PEOPLE THE ROWS BELONG TO
        # (plan P4-D340). Derived, never typed: the declared
        # identifiers that repeat. Empty means this table's population
        # is counted in rows. Every name here is also in
        # `forced_identifiers` below, so this key publishes no column
        # name the block did not already carry.
        "person_columns": _named_once(list(settings.person_columns)),
        "forced_identifiers": _named_once(forced_identifiers),
        # THE SECOND DECLARATION (plan P4-D19). Named columns are read
        # as labels and never as numbers, dates, clock times or
        # numbers wearing an affix, so a coding system written in
        # digits keeps its exact spellings -- padding included -- and
        # publishes which codes are common instead of a mean nobody
        # can use. Unlike `forced_identifiers` it does NOT silence the
        # column: the distribution is the point of declaring it.
        "forced_codes": _named_once(forced_codes),
        # THE THIRD DECLARATION (plan P4-D21). Named columns hold
        # quantities, including ones written as two or more whole
        # numbers in one cell -- a blood pressure. Where the column is
        # written that way it takes the `joined_numbers` role; where it
        # is not, this decides nothing.
        "forced_measurements": _named_once(forced_measurements),
        # THE FOURTH DECLARATION (plan P4-D26). The columns a person
        # said write their numbers with a comma for the point. It is
        # recorded because two readers downstream need it and neither
        # can work it out: the generator has to SPELL those numbers the
        # same way, or a twin hands a person cells their own tools read
        # as thousands separators; and the validator has to re-describe
        # a checked file under the declaration it was described under,
        # or every number of the column reads differently and the whole
        # column comes back missed.
        "forced_decimal_commas": _named_once(forced_decimal_commas),
        # THE SIXTH DECLARATION (plan P4-D110, review item CODEX-4): the
        # delimiter the person said their file is written with, or
        # empty. Recorded because the validator must read a checked
        # file with it -- a file that reads equally well two ways is
        # otherwise measured under whichever reading the cells favour
        # -- and FD13 holds it to the written form.
        "forced_delimiter": forced_delimiter,
        # THE FIFTH DECLARATION (plan P4-D81), and the only one that is
        # a COUNT rather than a list of names: how many rows under the
        # column names describe those columns rather than holding a
        # record. It is recorded because two readers downstream need
        # it and neither can work it out. The loader holds the
        # published rows of column descriptions to this number (FD9),
        # so a description cannot carry rows nobody declared; and the
        # validator re-reads a checked file under it, or the file's
        # first two records line up against the wrong rows and every
        # column comes back missed.
        "forced_metadata_rows": forced_metadata_rows,
        # THE SEVENTH DECLARATION (landing T1, plan P4-D370): the columns
        # the person said are 12-hour clocks written without AM or PM.
        # Recorded because the validator must re-read a checked file on
        # the same face, and the generator writes such a column's hours 1
        # to 12 only.
        "forced_twelve_hour_clocks": _named_once(
            list(settings.forced_twelve_hour_clocks)
        ),
        # THE THREE DECLARATIONS STAGE 3B RESERVES (plan P4-D386), empty
        # in every description until the landing that fills each: a
        # column's window for two-figure years (landing R2a), the columns
        # said to be dates (landing R2c), and the columns said to write
        # their dates as counts (landing R4).
        # -- 3b.R2a (P4-D383)
        # THE CENTURY OF EACH COLUMN'S TWO-FIGURE YEARS THE PERSON CHOSE
        # (question Q5, `--century`): `[column, first year]` in the
        # columns' rising order. Recorded because the validator must
        # re-read a checked file in the same window, and S8e holds the
        # column's layout to it.
        "century_windows": [
            [name, first_year]
            for name, first_year in sorted(settings.century_windows)
        ],
        # -- 3b.R2c (P4-D383)
        # THE COLUMNS THE PERSON SAID HOLD DATES (question Q6,
        # `--date-column`), in rising order. Recorded because the validator
        # must re-read a checked file at the same half line, and S8f holds
        # every layout of the day of the year to it.
        "forced_date_columns": _named_once(list(settings.forced_date_columns)),
        # -- 3b.R4 (P4-D384)
        # THE COLUMNS WHOSE DATES ARE WRITTEN AS COUNTS (question Q3,
        # `--date-count`): `[column, member]` in the columns' rising order.
        # Recorded because the validator reads a checked file's counts in
        # the same member, and the generator writes the twin's dates back
        # as that member's counts.
        "forced_date_counts": [
            [name, member] for name, member in sorted(settings.forced_date_counts)
        ],
    }


def _column_block(column: taxonomy.ColumnProfile) -> dict[str, object]:
    """One column's entry in the profile document."""
    missing: dict[str, int] = {}
    for spelling in sorted(column.missing_by_source):
        missing[spelling] = column.missing_by_source[spelling]
    classes: dict[str, int] = {}
    for name in sorted(column.missing_by_class):
        classes[name] = column.missing_by_class[name]
    block: dict[str, object] = {
        "name": column.name,
        "position": column.position,
        "role": column.role,
        # The three axes, on every column of every role (plan P2-D3).
        # They are fields of ColumnProfile, so this block cannot carry
        # them for one role and drop them for another, and
        # `taxonomy.axes_of` is the one place the rule that derives them
        # lives.
        "statistical_type": column.statistical_type,
        "quality_state": column.quality_state,
        "structural_role": column.structural_role,
        "detection_evidence": column.detection_evidence,
        "n_present": column.n_present,
        "n_missing": column.n_missing,
        "missing_by_source": missing,
        "missing_by_class": classes,
        # The two counts the spellings map carried in version 4 under
        # this package's own two words, moved out so that the map holds
        # one key space (contract 5 section 5). They are fields of
        # ColumnProfile, so every role carries them.
        "n_missing_blank": column.n_missing_blank,
        "n_missing_withheld": column.n_missing_withheld,
        "remarks": column.remarks,
        # Always present, on every role: a count that appears only where
        # someone remembered it goes missing exactly when it matters
        # (review items P1-R3-F3 and P1-R1-F9). These are fields of
        # ColumnProfile rather than keys of `details`, so the profile
        # cannot carry them for one role and drop them for another.
        "n_numeric": column.n_numeric,
        "n_out_of_range": column.n_out_of_range,
        "n_contradictory": column.n_contradictory,
        "n_not_numeric": column.n_not_numeric,
        "n_distinct": column.n_distinct,
        "n_distinct_folded": column.n_distinct_folded,
        "sentinel_verdicts": column.sentinel_verdicts,
        "n_sentinel_candidates_unpublished": (
            column.n_sentinel_candidates_unpublished
        ),
    }
    for key in sorted(column.details):
        block[key] = column.details[key]
    return block


def _relationships_block() -> dict[str, object]:
    """The eight reserved cross-column names, each carrying nothing.

    Guarantees:

    - Inputs: none. The block is a constant of this version, not a
      description of any table, which is the whole of what it says.
    - Determinism: the same eight keys and the same eight nulls on
      every run, in every profile.
    - Errors raised: none.
    - Boundary: no value of any column can reach it -- nothing about a
      column is consulted to build it.

    A consumer that finds anything but null under one of these names is
    holding a document a newer synthtwin wrote, and needs a newer
    synthtwin to read it.
    """
    block: dict[str, object] = {}
    for slot in RELATIONSHIP_SLOTS:
        block[slot] = None
    return block


# -- THE PUBLICATION GUARD, OVER THE FINISHED DOCUMENT -----------------
#
# WHAT IT IS FOR (plan P2-D2, review items P1-R8-F6 and P2-C1-F3). The
# rules that decide what a column may publish are applied where each
# part of the description is built. That leaves one question nobody
# else asks: is the FINISHED document -- the thing about to be written
# to disk -- made only of what those rules allow? A rule applied at
# three places covers three places, and the profile grew a fourth.
#
# The recursion below walks the whole finished tree, top-level
# publication notes included. Those notes are the reason it runs HERE,
# after `build_document` has lifted them out of the column blocks: a
# check over the completed column mapping would never see them, and a
# sentence that one day spelled a source value into itself would be
# serialized under a key every rule already permits, with no new key
# for a completeness check to notice.
#
# HOW A STRING IS ACCEPTED, and there are exactly two ways:
#
# 1. it stands at a path whose rule authorizes a value of that kind --
#    a column's name, a label that cleared the small-cell floor, a
#    canonical date, a word of this package's own vocabulary;
# 2. it is a SENTENCE, and the guard rebuilds it: `taxonomy.rendered`
#    is asked to write the sentence again from the form and the
#    arguments the sentence carries, and the leaf is accepted only when
#    the rebuilt text is identical.
#
# The second is why a path-and-type check was not enough. A source
# spelling formatted into an existing note keeps the note's path and
# its type, so no whitelist over paths and types can tell it from the
# prose it replaced; a rebuilt sentence cannot be told anything else --
# either this package can write those exact words from enumerated parts
# or it cannot.
#
# IT FAILS CLOSED. A path this table does not name, a leaf of a type
# its rule does not allow, a key in a mapping that has no rule: each
# stops the run before anything is serialized. Adding a field to the
# profile therefore means adding its rule here, which is the point.

# The three path steps that are not key names. A path is a tuple of
# steps, so `("columns", _EACH, "name")` is "the name of any column"
# and `("columns", _EACH, "variants", _ANY_KEY)` is "the count under
# any key of any level's variants".
_EACH = "[]"
_ANY_KEY = "{}"
_KEY_OF = "<key>"

# The kinds a rule can name.
_OBJECT = "object"
_ARRAY = "array"
_COUNT = "count"
_FLOOR_COUNT = "count-at-the-floor"
_FLOORED_ENTRY = "count-at-the-floor-or-withheld"
# A CENSUS ENTRY OF LANDING 2b.7, whose floor is never one and which
# speaks an unavailable state carrying no count (plan P4-D65.1,
# P4-D65.2). It is not `_FLOORED_ENTRY`: that kind admits a count at the
# settings floor and a pooled remainder below it, and both of those are
# exactly what these censuses may not publish.
_MIXTURE_ENTRY = "count-at-the-census-floor-or-unavailable"
# A CENSUS ENTRY OF HOW A COLUMN'S DATES WERE WRITTEN (plan P4-D131): a
# named count at `parsing.census_floor` or above, and no pool at all.
# It is not `_FLOORED_ENTRY`, which admits a count at a settings floor of
# one and a pooled remainder, and it is not `_MIXTURE_ENTRY`, which
# speaks an unavailable state: a census withheld whole is written `{}`.
# Whether what the named counts leave over of the published total is
# none or a group is invariants D17 to D20, checked where the total is.
_DISCLOSED_ENTRY = "count-at-the-disclosure-line"
# THE OFFSETS AND THE MARKS BETWEEN DAY AND CLOCK (plan P4-D220), AND THE
# FORMS MAP OF A NUMBER AND ITS THREE WIDTH CENSUSES (plan P4-D221): a named
# count at `parsing.census_floor` or above, and a pool at any floor --
# at a floor of one too, where the line is two and a count of one is
# pooled rather than named. Whether the pool beside a named count is a
# group is invariants D3, D12, P6, P5, P6b and P6c, checked where the
# total is.
_POOLED_CENSUS_ENTRY = "count-at-the-disclosure-line-or-withheld"

# THE KEYS EACH MIXTURE CENSUS MAY CARRY, read from the one place each
# convention is named so that the producer and this guard cannot drift.
# The notations are the four a negative may wear; the marks are the ones
# a description may publish, less the empty one -- a cell counted there
# PROVED a mark, so "no mark" is not a convention it can have worn. Both
# add the pooled word, which a census with several categories may speak
# because it names none of them, and the unavailable state.
_MIXTURE_NOTATIONS = parsing.NEGATIVE_FORMS + (
    taxonomy.SUPPRESSED_LABEL,
    taxonomy.UNAVAILABLE_LABEL,
)
_MIXTURE_MARKS = parsing.PUBLISHED_GROUP_MARKS[1:] + (
    taxonomy.SUPPRESSED_LABEL,
    taxonomy.UNAVAILABLE_LABEL,
)
# THE FLOOR'S OTHER HALF, which had no vocabulary here until amendment
# A-P3-16 and so could not be said. A description's counts divide in
# two: what it names, which the floor holds to "at least the floor", and
# what it holds back, which is the range BELOW the floor. `_HELD_BACK`
# is a tally of things in that range -- how many labels were suppressed,
# how many rows they covered, how many stand-in numbers were too rare to
# name -- and `_BELOW_THE_FLOOR` is one such group size written out.
# Both are empty at a floor of one, because the range is.
_HELD_BACK = "count-of-what-the-floor-held-back"
_BELOW_THE_FLOOR = "one-group-size-below-the-floor"
# A count that is either nothing at all or a named group at the floor.
# `n_missing_blank` is the one field of this kind: a blank group smaller
# than the floor is not named at all, it is pooled into
# `n_missing_withheld` with every other group the floor held back
# (contract 5 C5-N4). It is deliberately NOT `_HELD_BACK`: at a floor of
# one every blank group reaches the floor, so this count is written
# there rather than emptied (contract 5 C5-S13).
_ZERO_OR_AT_THE_FLOOR = "count-zero-or-at-the-floor"
# HOW MANY CELLS ONE POOLED AGGREGATE WAS TAKEN OVER (plan P4-D301):
# nought, or a group at `parsing.census_floor`. Nought is both "the
# pool holds no number" and "the disclosure rule refused to speak",
# which is the whole design: a refusal a reader could tell from nought
# would name the count the floor exists to withhold. It is NOT
# `_ZERO_OR_AT_THE_FLOOR`, whose line is the settings floor and is one
# wherever a person asks for a floor of one, and a pooled aggregate over
# one cell IS that cell.
_POOLED_SCALE_COUNT = "count-of-a-pooled-aggregate-or-nought"
# A count whose GROUP AND ITS COMPLEMENT are both at the floor, or
# nothing at all -- written `null`, never nought (landing 2b.6).
# `n_at_midnight` is the one field of this kind. Nought cannot stand for
# "not published" here the way it does above, because a reader who can
# tell a real nought from a suppressed count has been told the
# suppressed count: 400 moments at noon publish nought, the same 400
# with ONE moved to midnight published one, and that single difference
# was the whole of what separated the two documents. So the two states
# are one, and the field is absent for both. The rule itself -- both
# sides at the floor, and the floor never below two -- is invariant D15,
# checked with the invariants where the floor is in hand.
_BOTH_SIDES_OR_UNAVAILABLE = "count-on-both-sides-or-unavailable"
# THE FILE'S OWN FORM, HELD TO THE LINE IT IS PRODUCED AT (plan
# P4-D317). The producer withholds blank places that number fewer than
# the census line, writes a form fewer places wear as the commonest, and
# publishes an empty-row count only where it is nought or reaches the
# line (plan P4-D290), and this guard accepted any count and any list of
# places, so the rule lived in the producer alone. `_FORM_PLACES` is the
# list of blank places, asked as a whole; `_FORM_COUNT` is a count of
# records or lines of the file, nought or at the census line. Neither is
# asked at a floor of one, where the producer does not ask them either.
_FORM_PLACES = "blank-places-at-the-census-line"
# HOW A TRAILING DELIMITER IS CLOSED (plan P4-D387, lane R6): a side of
# the block is a flag, or the word `quoted`; the rows may instead be the
# runs of their two closings, every run and each closing's total at the
# census line, as `dialect.closing_runs_disclosed` publishes them.
_CLOSING = "closing-flag-or-quoted"
_CLOSING_RUNS = "closing-flag-quoted-or-runs-at-the-census-line"
# The block whose two sides are asked together: a header closed either
# way over records all closed `""` is read back as one column more
# (Codex's review of landing R6, item 3).
_TRAILING_BLOCK = ("source", "dialect", "trailing_delimiter")
_FORM_COUNT = "count-of-the-files-lines-zero-or-at-the-census-line"
# One of the three stand-in numbers this package judges, written as
# itself. The only path is the declaration records' `built_in_numbers`,
# which carries members of this package's own published vocabulary and
# no number of anybody's table (contract 5 C5-K1).
_STAND_IN_NUMBER = "numeric-sentinel-number"
_NUMBER = "number"
_MAYBE_NUMBER = "number-or-nothing"
# A SHEET'S NAME, OR NOTHING AT ALL (plan P4-D79). This is a kind with a
# GRAMMAR rather than a list, like `_WIDTH` and `_DIGITS` below and
# unlike `_WORD`: the names a description may publish are the safe names
# optionally followed by figures, which is `Sheet1` and `Table12` and
# every other numbering, and no fixed tuple can hold them. `None` is the
# withholding itself -- a sheet whose name could be somebody's is not
# published at all, and the twin writes it under a neutral name.
_SHEET_NAME = "sheet-name-or-nothing"
# A NUMBER FORMAT CODE (plan P4-D189): one of Excel's own, a canonical
# code, or one of the format language's own tokens alone, as
# `dialect.sheet_format_code_publishable` answers.
_SHEET_FORMAT_CODE = "sheet-format-code"
# The class most of a workbook column's value-holding cells are, by NAME
# and without a count, or nothing where no class is held by the line
# (plan P4-D164).
_SHEET_VALUE_CLASS = "a-value-class-or-nothing"
# The native block's texts (lane FORMATS), each held to its rule in
# `native`: a label `label_published` admits, a name `name_published`
# admits, a display format of a format language's own words, a code (a
# number written as text, or a text `label_published` admits), a truth
# value, and one of SPSS's three measures -- or nothing, for each.
_NATIVE_LABEL = "a-native-label-or-nothing"
_NATIVE_COLUMN_LABEL = "a-native-column-label-or-nothing"
_NATIVE_NAME = "a-native-name-or-nothing"
_NATIVE_FORMAT = "a-native-display-format-or-nothing"
_NATIVE_CODE = "a-native-code-or-nothing"
_NATIVE_FLAG = "a-truth-value-or-nothing"
_NATIVE_MEASURE = "a-measure-or-nothing"
_NATIVE_ZONE = "a-time-zone-name-or-nothing"
# The cell standing for an empty text in a Parquet text column (lane
# TOOLS): "" or a run of spaces, at most `native.EMPTY_TEXT_MOST`, or nothing.
_NATIVE_EMPTY_TEXT = "a-run-of-spaces-for-an-empty-text-or-nothing"
_FLAG = "flag"
_NOTHING = "nothing"
_SENTENCE = "sentence"
_WORD = "word"
_TABLE_NAME = "column-name"
_KNOWN_NAME = "a-name-of-this-table"
# THE SAME CLASS, WIDENED BY ONE VALUE: the empty spelling, which names
# no column and means the note is about the WHOLE TABLE (plan P4-D341).
# It is a class of its own rather than a relaxation of `_KNOWN_NAME`,
# because exactly one path may write a note about no column and every
# other path must still be held to a column this table has. The empty
# spelling is not a value of anybody's table: it is the absence of a
# name, and a note carrying it is checked by the same sentence rule as
# every other note.
_KNOWN_NAME_OR_THE_TABLE = "a-name-of-this-table-or-the-table"
_SPELLING = "authorized-spelling"
# A KEY BLOCK (lane KV, plan P4-D487): a column block the describe wrote of a
# key's cells as a column named by the key, checked under every rule of a
# column block, the key's name standing among the column names it may cite.
_KEY_BLOCK = "a-key-block"
# The ONE exception in the ranges class: an affixed column publishes the
# shared text its cells wore, on two keys and no others. It is a rule of
# its own rather than `_SPELLING` because either side may be EMPTY -- a
# column of `5mg` has no prefix -- and because an exception a reader can
# see in this table is an exception nobody widens by accident. That both
# sides are not empty at once is invariant AF1, checked with the
# invariants and not here.
_AFFIX = "affix-spelling"
_DIGITS = "whole-number-as-text"
# A SPELLING OF A FEW-VALUED COLUMN'S OWN NUMBER (lane GG, plan P4-D440):
# the plain decimal family, `-99` and `4.5`, and nothing else
# (`parsing.is_few_value_spelling`). An entry of a list naming numbers
# the owner's ruling of 2026-09-22 lets a column name, no count beside
# it, each held by two cells or more.
_VALUE_SPELLING = "a-number-as-the-column-writes-it"
# A KEY OF THE FRACTION CENSUS: a width written as decimal figures, or
# the pooled remainder. It is not `_DIGITS`, and the difference is the
# whole point of giving it a kind of its own: `_DIGITS` admits `02`
# beside `2`, and a census whose keys admit padding is a census two
# producers spell two ways and a consumer reads as two widths. The key
# grammar is CANONICAL -- no sign, no padding, `0` written as itself.
_WIDTH = "fraction-width-as-figures"
_BIN = "histogram-bin-number"
# ...AND A BIN NUMBER THAT HOLDS NOTHING, which is a kind of its own
# rather than `_BIN` reused (plan P4-D32). The two carry different
# disclosure prices and the audit is where that difference has to be
# visible: `_BIN` stands at the KEY of a census whose entries are
# counts of real cells and is therefore governed by the floor, while
# this one names a stretch of the scale no cell of the table is in and
# is governed by nothing, because there is no group smaller than
# nobody. Filing both under one word would hide the ONE fact in this
# document the floor does not reach.
_EMPTY_BIN = "histogram-bin-number-holding-nothing"
# THE TWO KINDS THE TAIL RULE ADDS (stage 3, plan P4-D344), neither of
# them a count of rows and so neither held to the floor: the boundary
# percent of a tail, a whole number from 1 to 99 that follows from the
# row count and the floor alone (contract L4), and a bin's number where
# a group of bins begins or ends (contract BG1). A counts gate that
# floored them would read "bin 3" as a group of three.
_TAIL_PERCENT = "tail-boundary-percent"
_BIN_INDEX = "histogram-bin-number-of-a-group"
# THE WEEKDAY CENSUS OF A COLUMN OF DATES (landing 3b.1, plan P4-D355):
# a group's first and last weekday, Monday 0 to Sunday 6, and its count,
# nought or at the census line. Which groupings may stand, and whether
# the census may stand at all, are invariants WC1 to WC4 and WC6 (plan
# P4-D365), asked with the block's other facts beside them.
_WEEKDAY = "a-weekday-number"
_WEEKDAY_COUNT = "a-weekday-group-count-zero-or-at-the-census-line"
# THE LANDINGS' ANCHORS (plan P4-D364): each landing of stage 3b adds its
# kinds below its own line, so two landings built side by side never
# touch the same lines.
# anchor 3b-D1 (P4-D365)
# anchor 3b-D0 (P4-D366)
# anchor 3b-D2 (P4-D367)
# anchor 3b-D3 (P4-D368)
# THE DAY-OF-MONTH CENSUS OF A COLUMN OF DATES (landing 3b.3, plan
# P4-D368): a group's first and last bin, 1 to 34 (contract DM1), and its
# count, nought or at the census line (DM2).
_MONTH_DAY = "a-day-of-month-bin-number"
_MONTH_DAY_COUNT = "a-day-of-month-group-count-zero-or-at-the-census-line"
# anchor 3b-D4 (P4-D369)
# THE DATES THAT STAND OUT (landing 3b.6, plan P4-D369): each a canonical
# date (contract HD1) and its count, at least the heavy line and never
# nought (HD2).
_HEAVY_DATE = "a-canonical-date-that-stands-out"
_HEAVY_COUNT = "a-heavy-date-count-at-the-heavy-line"
# anchor 3b-T1 (P4-D370)
# anchor 3b-T2 (P4-D371)
# THE HOUR CENSUS OF A COLUMN OF MOMENTS (landing 3b.2-H, plan P4-D371): a
# group's first and last hour, 0 to 23, and its count, nought or at the
# census line. Which groupings may stand, and whether the census may
# stand at all, are invariants HC1 to HC6, asked with the block's other
# facts beside them.
_HOUR = "an-hour-of-the-day"
_HOUR_COUNT = "an-hour-group-count-zero-or-at-the-census-line"
# anchor 3b-T3 (P4-D372)
# THE MINUTE AND SECOND CENSUSES AND HEAPS (landing 3b.4, plan P4-D372): a
# group's first and last value and a heap's value, 0 to 59; a group's count,
# nought or at the census line; a heap's, at the census line. Which groups
# and heaps may stand, and whether they may stand at all, are invariants
# MC1 to MC6, SE1 to SE6, MH1, MH2, SH1 and SH2.
_CLOCK_FIELD_VALUE = "a-minute-of-the-hour-or-second-of-the-minute"
_CLOCK_FIELD_COUNT = "a-minute-or-second-group-count-zero-or-at-the-census-line"
_CLOCK_FIELD_HEAP = "a-minute-or-second-heap-count-at-the-census-line"
# anchor 3b-C1 (P4-D373)
# THE CENSUS OF A COLUMN OF CLOCK TIMES (landing 3b.5, plan P4-D373): a
# group's first and last ten-minute bin of the dial and its count, nought
# or at the census line; a heap's clock value and a code's count, each at
# the census line; and the step the values stand on, in seconds -- or
# nothing, on a block its producer was not asked for. Which groups, heaps
# and codes may stand together is invariants CC1 to CC5 and CH1 to CH2,
# asked with the block's other facts beside them.
_TEN_MINUTE_BIN = "a-ten-minute-bin-of-the-dial"
_CLOCK_COUNT = "a-clock-group-count-zero-or-at-the-census-line"
_CLOCK_LINE_COUNT = "a-clock-count-at-the-census-line"
_CLOCK_VALUE = "a-clock-time-in-its-columns-form"
_CLOCK_STEP = "seconds-a-clock-steps-by-or-nothing"
# anchor 3b-C2 (P4-D374)
# anchor 3b-G1 (P4-D375)
# anchor 3b-G3 (P4-D376)
# anchor 3b-G2 (P4-D377)
# anchor 3b-7 (P4-D378)
# anchor 3b-J (P4-D379)
# anchor 3b-R2a (P4-D383)
# ONE HALF OF A DECLARED CENTURY (question Q5): a column of this table, or
# the first year of one of the three windows the question offers. No
# value of anybody's table is either.
_CENTURY_PART = "a-name-of-this-table-or-a-century-window"
# anchor 3b-R2b (P4-D383)
# anchor 3b-R2c (P4-D383)
# anchor 3b-R4 (P4-D384)
# ONE HALF OF A DECLARED COUNTING SYSTEM (question Q3): a column of this
# table, or one of the twelve members (`date_counts.MEMBERS`). No value of
# anybody's table is either.
_COUNTED_PART = "a-name-of-this-table-or-a-counting-system"
# HOW A COLUMN OF COUNTED DATES WRITES ITS COUNTS (`count_form`): the
# decimal mark, a point or a comma; the significant figures it writes to,
# fifteen or seventeen, or nothing; and a contact number of a
# `days-since-1840` column as its figures are written, or `(none)`.
_COUNT_MARK = "a-decimal-mark-of-a-count"
# ONE PART OF A SPAN OF A `time_grain` RECORD (plan P4-D417): the rung it
# stands at, a word of `grains.RUNGS`, or the start of a bucket at that
# rung, a canonical moment or a clock time -- the first and the last bucket
# the floor's number of people hold, which the record exists to publish.
_GRAIN_SPAN_PART = "a-rung-or-the-start-of-a-bucket"
# THE RULE AN OFFSET FOLLOWS ITS DATE BY (lane DST, plan P4-D474): a family
# of `offset_rules.FAMILIES`, a space and a standard offset, a zone's public
# calendar.
_OFFSET_RULE = "a-rule-family-and-a-standard-offset"
_COUNT_SIGNIFICANT = "fifteen-or-seventeen-significant-figures-or-nothing"
_CONTACT_WORD = "a-contact-number-in-figures-or-none"
_SHAPE_FORM = "a-written-form-a-cell-could-not-be-spelled-with"
# ONE PLACE OF RULE A2'S POSITIONAL CENSUS (lane CODES-1, plan P4-D439,
# contract C6-31h): the characters of one kind -- figures, capitals or
# small letters -- that at least the census line of a form's held-back
# cells hold at that place, each once and in ascending order, or nothing.
_PLACE_CHARACTERS = "the-characters-one-place-of-a-form-lists"
# A stand-in's start (lane PL, plan P4-D453): `parsing.is_a_stand_in_start`,
# or nothing where the pool holds no cell of that class.
_STAND_IN_START = "the-start-of-a-stand-in-walk-or-nothing"
_FLAG_TRUE = "true"
_LAYOUT_FORM = "a-layout-a-record-number-could-not-be-spelled-with"
# The two kinds `layout_prefixes` carries (owner ruling 2026-09-17,
# item 1): its keys, `(column)` or a layout, and its values, a literal
# prefix `parsing.is_a_literal_prefix` admits.
_PREFIX_SCOPE = "the-column-or-a-layout-a-record-number-could-not-be-spelled-with"
_LITERAL_PREFIX = "a-literal-prefix-of-letters-and-marks-with-no-figure"
# The two kinds `layout_exclusions` carries (lane ID-ROOM, plan P4-D432):
# its keys, `(spill)` or a layout, and its values, a layout with places
# written out (`parsing.is_a_layout_exclusion`), a list of several, or, for
# the spill, a layout.
_EXCLUSION_SCOPE = "the-spill-or-a-layout-a-record-number-could-not-be-spelled-with"
# The two kinds `figure_openings` carries (lane HB, plan P4-D442): its keys, a
# merged width of a run of figures (`parsing.is_a_figure_width`), and its
# values, an opening no real run of that width opens with, or nothing.
_FIGURE_WIDTH = "a-merged-width-of-a-run-of-figures-three-or-more"
_FIGURE_OPENING = "an-opening-no-real-run-of-its-width-opens-with"
_LAYOUT_EXCLUSION = "a-layout-with-places-written-as-characters-no-real-cell-holds"
_MOMENT_TEXT = "canonical-datetime"
_OFFSET = "utc-offset"
_SENTINEL = "numeric-sentinel-spelling"
_VERSION = "the-version-that-wrote-this"
# The kinds of `source.dialect` (plan P4-D86). An object that may be
# `null`; a header cell as the file writes it, which may be empty or a
# repeat; a blank line's own text, nothing or only spaces and tabs; and a
# the MARK a line before the table began with, which is punctuation and
# whitespace and never a word of that line (plan P4-D80).
_MAYBE_OBJECT = "object-or-nothing"
# A list, or nothing at all: the values a date or clock tail holds, which
# it publishes only where it holds few of them (stage 3, contract DT1).
_MAYBE_ARRAY = "array-or-nothing"
# A canonical moment, or nothing at all: a rung of a date or clock ladder
# the tail rule withholds (stage 3, contract D11 and T2).
_MAYBE_MOMENT = "canonical-datetime-or-nothing"
_HEADER_TEXT = "a-header-cell-as-written"
_BLANK_LINE = "a-blank-line-of-spaces-and-tabs"
_PREAMBLE_MARK = "the-mark-a-line-before-the-table-began-with"

# What a canonical datetime is made of. `parsing.parse_datetime` writes
# `2024-03-17`, `2024-03-17 14:05:00` and `2024-Q1`, and nothing else,
# so a spelling of the table standing at one of those keys fails on its
# first ordinary character.
_DATETIME_CHARACTERS = "0123456789-: Q"

# The offsets an endpoint may name: none at all, the withheld pool, or
# a signed clock offset.
_NO_OFFSET = "(none)"


@dataclasses.dataclass(frozen=True)
class _Publication:
    """What the guard has to know about the document it is checking."""

    floor: int
    names: "tuple[str, ...]"


def _relationship_rules() -> "dict[tuple[str, ...], str]":
    """One rule per reserved cross-column name: each carries nothing."""
    rules: dict[tuple[str, ...], str] = {}
    for slot in RELATIONSHIP_SLOTS:
        rules[("relationships", slot)] = _NOTHING
    return rules


# EVERY path of the finished document, with what may stand there. A
# path missing from this table is a refusal, which is what makes adding
# a field to the profile a decision somebody has to write down.
_STATED_RULES: "dict[tuple[str, ...], str]" = {
    (): _OBJECT,
    ("profile_version",): _COUNT,
    ("created_with",): _VERSION,
    ("n_rows",): _COUNT,
    ("n_columns",): _COUNT,
    # The settings: thresholds, counts and two tokens naming the rules
    # in force. No spelling the person typed is anywhere in the settings
    # block, which is what `DECLARATION_PUBLICATION` above says and this
    # table checks.
    ("settings",): _OBJECT,
    ("settings", "small_cell_floor"): _COUNT,
    ("settings", "identifier_uniqueness"): _NUMBER,
    ("settings", "identifier_minimum_rows"): _COUNT,
    ("settings", "minimum_parse_rate"): _NUMBER,
    ("settings", "categorical_share"): _NUMBER,
    ("settings", "categorical_ceiling"): _COUNT,
    ("settings", "categorical_floor"): _COUNT,
    ("settings", "sentinel_outlier_iqr_multiple"): _NUMBER,
    ("settings", "sentinel_minimum_share"): _NUMBER,
    ("settings", "kept_values"): _OBJECT,
    ("settings", "kept_values", "n_declared"): _COUNT,
    ("settings", "kept_values", "values_recorded"): _FLAG,
    # The two vocabulary lists (contract 5 section 6). Each element is
    # checked against this package's OWN published list, so a spelling
    # of the table standing here is refused before the file is written.
    ("settings", "kept_values", "built_in_texts"): _ARRAY,
    ("settings", "kept_values", "built_in_texts", _EACH): _WORD,
    ("settings", "kept_values", "built_in_dates"): _ARRAY,
    ("settings", "kept_values", "built_in_dates", _EACH): _WORD,
    ("settings", "kept_values", "built_in_numbers"): _ARRAY,
    ("settings", "kept_values", "built_in_numbers", _EACH): _STAND_IN_NUMBER,
    ("settings", "declared_missing_values"): _OBJECT,
    ("settings", "declared_missing_values", "n_declared"): _COUNT,
    ("settings", "declared_missing_values", "values_recorded"): _FLAG,
    ("settings", "declared_missing_values", "built_in_texts"): _ARRAY,
    ("settings", "declared_missing_values", "built_in_texts", _EACH): _WORD,
    ("settings", "declared_missing_values", "built_in_dates"): _ARRAY,
    ("settings", "declared_missing_values", "built_in_dates", _EACH): _WORD,
    ("settings", "declared_missing_values", "built_in_numbers"): _ARRAY,
    (
        "settings",
        "declared_missing_values",
        "built_in_numbers",
        _EACH,
    ): _STAND_IN_NUMBER,
    ("settings", "declaration_matching"): _WORD,
    ("settings", "declaration_publication"): _WORD,
    ("settings", "near_threshold_slack"): _COUNT,
    ("settings", "day_first"): _FLAG,
    ("settings", "long_tail_minimum_level"): _COUNT,
    ("settings", "person_columns"): _ARRAY,
    ("settings", "person_columns", _EACH): _KNOWN_NAME,
    ("settings", "forced_identifiers"): _ARRAY,
    ("settings", "forced_identifiers", _EACH): _KNOWN_NAME,
    ("settings", "forced_codes"): _ARRAY,
    ("settings", "forced_codes", _EACH): _KNOWN_NAME,
    ("settings", "forced_measurements"): _ARRAY,
    ("settings", "forced_measurements", _EACH): _KNOWN_NAME,
    # How many rows under the names describe the columns (plan P4-D81).
    ("settings", "forced_metadata_rows"): _COUNT,
    # Which delimiter the person declared (plan P4-D110): one of the
    # four this format reads, or nothing.
    ("settings", "forced_delimiter"): _WORD,
    ("settings", "forced_decimal_commas"): _ARRAY,
    ("settings", "forced_decimal_commas", _EACH): _KNOWN_NAME,
    ("settings", "forced_twelve_hour_clocks"): _ARRAY,
    ("settings", "forced_twelve_hour_clocks", _EACH): _KNOWN_NAME,
    # THE THREE DECLARATIONS STAGE 3B RESERVES (plan P4-D386): each an
    # EMPTY list until the landing that fills it adds the rows of what it
    # holds, so an entry is a path no rule names and is refused here.
    # -- 3b.R2a (P4-D383)
    ("settings", "century_windows"): _ARRAY,
    ("settings", "century_windows", _EACH): _ARRAY,
    ("settings", "century_windows", _EACH, _EACH): _CENTURY_PART,
    # -- 3b.R2c (P4-D383)
    ("settings", "forced_date_columns"): _ARRAY,
    ("settings", "forced_date_columns", _EACH): _KNOWN_NAME,
    # -- 3b.R4 (P4-D384)
    ("settings", "forced_date_counts"): _ARRAY,
    ("settings", "forced_date_counts", _EACH): _ARRAY,
    ("settings", "forced_date_counts", _EACH, _EACH): _COUNTED_PART,
    # How the table was read.
    ("source",): _OBJECT,
    ("source", "encoding"): _WORD,
    ("source", "used_fallback_encoding"): _FLAG,
    ("source", "header_source"): _WORD,
    ("source", "header_by_convention"): _FLAG,
    ("source", "header_evidence"): _SENTENCE,
    # How the table's FILE is written (owner ruling 2026-09-15, plan
    # P4-D86): every fact the twin needs to be written the way the table
    # was. None of them is a value of the table, and none is text a
    # person wrote, except the rows of column descriptions -- which are
    # schema, and reach a description only where a person DECLARED them
    # (plan P4-D81). The lines before the table carry their shape alone
    # (plan P4-D80). Each has a kind of its own here.
    # The workbook block (plan P4-D77, contract 4.3b). Every key is a
    # fact about the FILE: a count held to the floor, a flag, or one of
    # synthtwin's own words. None of them is text out of the workbook.
    ("source", "workbook"): _MAYBE_OBJECT,
    ("source", "workbook", "autofilter"): _FLAG,
    ("source", "workbook", "columns"): _ARRAY,
    ("source", "workbook", "columns", _EACH): _OBJECT,
    ("source", "workbook", "columns", _EACH, "cell_classes"): _OBJECT,
    # THE KEYS OF BOTH CENSUSES ARE SYNTHTWIN'S OWN WORDS, which is why
    # they are `_WORD` here and not the `_SPELLING` that `missing_by_
    # source` uses. That map's keys are spellings out of the person's
    # file; these are the closed sets `workbook.CELL_CLASSES` and
    # `workbook.FORMAT_KINDS`, and no text of a workbook reaches either.
    ("source", "workbook", "columns", _EACH, "cell_classes", _KEY_OF): _WORD,
    # A COUNT, NOTHING AT ALL, OR WITHHELD -- which is `_MAYBE_NUMBER`,
    # the kind `sequence_start` already uses, and NOT `_FLOORED_ENTRY`.
    # A census over a closed set of classes publishes `0` for a class no
    # cell of the column has, and `null` where the floor held the count
    # back; `_FLOORED_ENTRY` admits neither, because it describes a
    # count standing under a key the DATA chose, where the key's own
    # existence is the disclosure. Here the keys are fixed and carry no
    # news, so what the floor governs is the number, and it is governed
    # twice already: `workbook.floored` decides it and contract WB3
    # refuses a document that breaks it.
    ("source", "workbook", "columns", _EACH, "cell_classes", _ANY_KEY): (
        _MAYBE_NUMBER
    ),
    ("source", "workbook", "columns", _EACH, "format_kinds"): _OBJECT,
    ("source", "workbook", "columns", _EACH, "format_kinds", _KEY_OF): _WORD,
    ("source", "workbook", "columns", _EACH, "format_kinds", _ANY_KEY): (
        _MAYBE_NUMBER
    ),
    ("source", "workbook", "columns", _EACH, "format_code"): _SHEET_FORMAT_CODE,
    ("source", "workbook", "columns", _EACH, "formulas"): _MAYBE_NUMBER,
    # ONE OF SYNTHTWIN'S OWN CLASS WORDS, OR NOTHING (plan P4-D164). It
    # names which class is commonest without saying how common, which is
    # what a twin needs where the census beside it withheld every count.
    ("source", "workbook", "columns", _EACH, "value_class"): (
        _SHEET_VALUE_CLASS
    ),
    ("source", "workbook", "date_system"): _WORD,
    ("source", "workbook", "defined_names"): _COUNT,
    ("source", "workbook", "defined_table"): _FLAG,
    # A COUNT OR THE WITHHOLDING, like the censuses beside it and unlike
    # the layout counts below (repair of landing 2b.10). This counts
    # records of the table, so the smallest group holds it back where it
    # would name one, and `null` is then what the description publishes.
    ("source", "workbook", "empty_rows_inside"): _MAYBE_NUMBER,
    ("source", "workbook", "frozen_rows"): _COUNT,
    ("source", "workbook", "macro_project"): _FLAG,
    ("source", "workbook", "rows_above_header"): _COUNT,
    ("source", "workbook", "sheet_count"): _COUNT,
    ("source", "workbook", "sheet_hidden"): _FLAG,
    # ONE ENTRY PER SHEET, each a name this version would publish itself
    # or nothing at all (plan P4-D79). A sheet name is free text somebody
    # typed, so what stands here is never whatever the file said: it is
    # a name out of `dialect.SHEET_SAFE_NAMES`, optionally numbered, and
    # every other name is withheld and written neutral.
    ("source", "workbook", "sheet_names"): _ARRAY,
    ("source", "workbook", "sheet_names", _EACH): _SHEET_NAME,
    # HOW MUCH ROOM EVERY OTHER SHEET'S CELLS TAKE, and nothing about
    # what they held (plan P4-D82). Two counts of the sheet's own
    # furniture, in the same sense as the rows above a header: no value,
    # no name and no text of that sheet is published or written, and the
    # sheet the table was read from publishes nothing here at all.
    ("source", "workbook", "sheet_extents"): _ARRAY,
    ("source", "workbook", "sheet_extents", _EACH): _MAYBE_OBJECT,
    ("source", "workbook", "sheet_extents", _EACH, "columns"): _COUNT,
    ("source", "workbook", "sheet_extents", _EACH, "rows"): _COUNT,
    ("source", "workbook", "sheet_position"): _COUNT,
    ("source", "workbook", "trailing_blank_columns"): _COUNT,
    ("source", "workbook", "trailing_blank_rows"): _COUNT,
    # THE NATIVE BLOCK (lane FORMATS, contract 4.3c): what a Parquet, SAS,
    # Stata or SPSS file said about itself that the twin needs to be
    # written as the same kind of file. Present only for such a file, so a
    # description of a CSV or a workbook carries no key for it. Every text
    # is held to the rule `native` states for its kind, by the producer
    # (`_published_native`), here, and by the loader alike.
    ("source", "native"): _MAYBE_OBJECT,
    ("source", "native", "format"): _WORD,
    ("source", "native", "version"): _COUNT,
    ("source", "native", "table_name"): _NATIVE_NAME,
    ("source", "native", "index"): _MAYBE_OBJECT,
    ("source", "native", "index", "columns"): _ARRAY,
    ("source", "native", "index", "columns", _EACH): _KNOWN_NAME,
    ("source", "native", "index", "start"): _MAYBE_NUMBER,
    ("source", "native", "index", "step"): _MAYBE_NUMBER,
    ("source", "native", "columns"): _ARRAY,
    ("source", "native", "columns", _EACH): _OBJECT,
    ("source", "native", "columns", _EACH, "categories"): _MAYBE_ARRAY,
    ("source", "native", "columns", _EACH, "categories", _EACH): _NATIVE_LABEL,
    ("source", "native", "columns", _EACH, "display"): _NATIVE_FORMAT,
    ("source", "native", "columns", _EACH, "empty_text"): _NATIVE_EMPTY_TEXT,
    ("source", "native", "columns", _EACH, "fraction"): _COUNT,
    ("source", "native", "columns", _EACH, "label"): _NATIVE_COLUMN_LABEL,
    ("source", "native", "columns", _EACH, "label_set"): _NATIVE_NAME,
    ("source", "native", "columns", _EACH, "measure"): _NATIVE_MEASURE,
    ("source", "native", "columns", _EACH, "missing"): _MAYBE_OBJECT,
    ("source", "native", "columns", _EACH, "missing", "high"): _NATIVE_CODE,
    ("source", "native", "columns", _EACH, "missing", "low"): _NATIVE_CODE,
    ("source", "native", "columns", _EACH, "missing", "values"): _ARRAY,
    ("source", "native", "columns", _EACH, "missing", "values", _EACH): _NATIVE_CODE,
    ("source", "native", "columns", _EACH, "pandas"): _MAYBE_OBJECT,
    ("source", "native", "columns", _EACH, "pandas", "numpy_type"): _WORD,
    ("source", "native", "columns", _EACH, "pandas", "ordered"): _NATIVE_FLAG,
    ("source", "native", "columns", _EACH, "pandas", "pandas_type"): _WORD,
    ("source", "native", "columns", _EACH, "places"): _MAYBE_NUMBER,
    ("source", "native", "columns", _EACH, "precision"): _MAYBE_NUMBER,
    ("source", "native", "columns", _EACH, "required"): _FLAG,
    ("source", "native", "columns", _EACH, "scale"): _MAYBE_NUMBER,
    ("source", "native", "columns", _EACH, "storage"): _WORD,
    ("source", "native", "columns", _EACH, "utc"): _NATIVE_FLAG,
    ("source", "native", "columns", _EACH, "value_labels"): _MAYBE_OBJECT,
    ("source", "native", "columns", _EACH, "value_labels", _KEY_OF): _NATIVE_CODE,
    ("source", "native", "columns", _EACH, "value_labels", _ANY_KEY): _NATIVE_LABEL,
    ("source", "native", "columns", _EACH, "width"): _MAYBE_NUMBER,
    ("source", "native", "columns", _EACH, "written_as"): _WORD,
    ("source", "native", "columns", _EACH, "zone"): _NATIVE_ZONE,
    ("source", "dialect"): _OBJECT,
    ("source", "dialect", "blank_lines"): _FORM_PLACES,
    ("source", "dialect", "blank_lines", _EACH): _OBJECT,
    ("source", "dialect", "blank_lines", _EACH, "after"): _COUNT,
    ("source", "dialect", "blank_lines", _EACH, "lines"): _COUNT,
    ("source", "dialect", "blank_lines", _EACH, "text"): _BLANK_LINE,
    # Past the cap on places, the blank lines counted.
    ("source", "dialect", "blank_lines_spread"): _MAYBE_OBJECT,
    ("source", "dialect", "blank_lines_spread", "first"): _COUNT,
    ("source", "dialect", "blank_lines_spread", "last"): _COUNT,
    ("source", "dialect", "blank_lines_spread", "lines"): _FORM_COUNT,
    ("source", "dialect", "blank_lines_spread", "text"): _BLANK_LINE,
    ("source", "dialect", "byte_order_mark"): _FLAG,
    ("source", "dialect", "columns"): _ARRAY,
    ("source", "dialect", "columns", _EACH): _OBJECT,
    ("source", "dialect", "columns", _EACH, "pad"): _MAYBE_OBJECT,
    ("source", "dialect", "columns", _EACH, "pad", "side"): _WORD,
    ("source", "dialect", "columns", _EACH, "pad", "width"): _COUNT,
    ("source", "dialect", "columns", _EACH, "quoting"): _OBJECT,
    **{
        ("source", "dialect", "columns", _EACH, "quoting", kind): _WORD
        for kind in dialect.CELL_CLASSES
    },
    ("source", "dialect", "columns", _EACH, "sequence_start"): _MAYBE_NUMBER,
    ("source", "dialect", "delimiter"): _WORD,
    ("source", "dialect", "empty_rows"): _OBJECT,
    ("source", "dialect", "empty_rows", "interior"): _FORM_COUNT,
    ("source", "dialect", "empty_rows", "leading"): _FORM_COUNT,
    ("source", "dialect", "empty_rows", "trailing"): _FORM_COUNT,
    ("source", "dialect", "end_of_file_mark"): _FLAG,
    ("source", "dialect", "escape"): _WORD,
    ("source", "dialect", "final_line_ending"): _FLAG,
    ("source", "dialect", "header_quoting"): _WORD,
    # One cell per column saying what the column is, which is schema and
    # is published like a name.
    ("source", "dialect", "header_rows"): _ARRAY,
    ("source", "dialect", "header_rows", _EACH): _ARRAY,
    ("source", "dialect", "header_rows", _EACH, _EACH): _HEADER_TEXT,
    ("source", "dialect", "header_rows_quoting"): _WORD,
    ("source", "dialect", "initial_space"): _FLAG,
    ("source", "dialect", "line_endings"): _ARRAY,
    ("source", "dialect", "line_endings", _EACH): _OBJECT,
    ("source", "dialect", "line_endings", _EACH, "ending"): _WORD,
    ("source", "dialect", "line_endings", _EACH, "lines"): _COUNT,
    # Past the cap on runs, how many lines end each way.
    ("source", "dialect", "line_endings_spread"): _ARRAY,
    ("source", "dialect", "line_endings_spread", _EACH): _OBJECT,
    ("source", "dialect", "line_endings_spread", _EACH, "ending"): _WORD,
    ("source", "dialect", "line_endings_spread", _EACH, "lines"): _COUNT,
    # THE LINES BEFORE THE TABLE, AS SHAPES AND NEVER AS TEXT (plan
    # P4-D80). Each entry is a run of lines of one shape: what kind they
    # are, how many there are, and the punctuation or whitespace they
    # began with. The text of such a line is published at no floor, and
    # `_PREAMBLE_MARK` below is the check that none of it rode in.
    ("source", "dialect", "preamble"): _ARRAY,
    ("source", "dialect", "preamble", _EACH): _OBJECT,
    ("source", "dialect", "preamble", _EACH, "kind"): _WORD,
    ("source", "dialect", "preamble", _EACH, "lines"): _COUNT,
    ("source", "dialect", "preamble", _EACH, "mark"): _PREAMBLE_MARK,
    ("source", "dialect", "preamble_withheld"): _FLAG,
    ("source", "dialect", "row_order"): _MAYBE_OBJECT,
    ("source", "dialect", "row_order", "collation"): _WORD,
    ("source", "dialect", "row_order", "column"): _COUNT,
    ("source", "dialect", "row_order", "direction"): _WORD,
    ("source", "dialect", "separator_line"): _FLAG,
    ("source", "dialect", "short_rows"): _FLAG,
    ("source", "dialect", "trailing_delimiter"): _OBJECT,
    ("source", "dialect", "trailing_delimiter", "header"): _CLOSING,
    ("source", "dialect", "trailing_delimiter", "rows"): _CLOSING_RUNS,
    ("source", "dialect", "trailing_delimiter", "rows", _EACH): _OBJECT,
    ("source", "dialect", "trailing_delimiter", "rows", _EACH, "ending"): _WORD,
    ("source", "dialect", "trailing_delimiter", "rows", _EACH, "lines"): _FORM_COUNT,
    ("source", "dialect", "written_names"): _ARRAY,
    ("source", "dialect", "written_names", _EACH): _OBJECT,
    ("source", "dialect", "written_names", _EACH, "position"): _COUNT,
    ("source", "dialect", "written_names", _EACH, "text"): _HEADER_TEXT,
    # The reserved manifest, filled in below.
    ("relationships",): _OBJECT,
    # The notes, AFTER they were lifted here out of the column blocks.
    ("publication_notes",): _ARRAY,
    ("publication_notes", _EACH): _OBJECT,
    ("publication_notes", _EACH, "column"): _KNOWN_NAME_OR_THE_TABLE,
    ("publication_notes", _EACH, "note"): _SENTENCE,
    # The columns.
    ("columns",): _ARRAY,
    ("columns", _EACH): _OBJECT,
    ("columns", _EACH, "name"): _TABLE_NAME,
    ("columns", _EACH, "position"): _COUNT,
    ("columns", _EACH, "role"): _WORD,
    ("columns", _EACH, "statistical_type"): _WORD,
    ("columns", _EACH, "quality_state"): _WORD,
    ("columns", _EACH, "structural_role"): _WORD,
    ("columns", _EACH, "detection_evidence"): _SENTENCE,
    ("columns", _EACH, "n_present"): _COUNT,
    ("columns", _EACH, "n_missing"): _COUNT,
    # ONE KEY SPACE, AND EVERY ENTRY AT THE FLOOR (contract 5 C5-N4,
    # C5-N5). Version 4's kind here was `_FLOORED_ENTRY`, which exists
    # to let the pooled remainder stand under this package's own word
    # beside the table's spellings. There is no such entry any more --
    # the remainder is `n_missing_withheld` below -- so every count here
    # names a group and every group is at the floor.
    ("columns", _EACH, "missing_by_source"): _OBJECT,
    ("columns", _EACH, "missing_by_source", _KEY_OF): _SPELLING,
    ("columns", _EACH, "missing_by_source", _ANY_KEY): _FLOOR_COUNT,
    ("columns", _EACH, "n_missing_blank"): _ZERO_OR_AT_THE_FLOOR,
    ("columns", _EACH, "n_missing_withheld"): _HELD_BACK,
    ("columns", _EACH, "missing_by_class"): _OBJECT,
    ("columns", _EACH, "missing_by_class", _KEY_OF): _WORD,
    ("columns", _EACH, "missing_by_class", _ANY_KEY): _COUNT,
    ("columns", _EACH, "remarks"): _ARRAY,
    ("columns", _EACH, "remarks", _EACH): _SENTENCE,
    ("columns", _EACH, "n_numeric"): _COUNT,
    ("columns", _EACH, "n_out_of_range"): _COUNT,
    ("columns", _EACH, "n_contradictory"): _COUNT,
    ("columns", _EACH, "n_not_numeric"): _COUNT,
    ("columns", _EACH, "n_distinct"): _COUNT,
    ("columns", _EACH, "n_distinct_folded"): _COUNT,
    ("columns", _EACH, "n_sentinel_candidates_unpublished"): _HELD_BACK,
    ("columns", _EACH, "sentinel_verdicts"): _ARRAY,
    ("columns", _EACH, "sentinel_verdicts", _EACH): _OBJECT,
    ("columns", _EACH, "sentinel_verdicts", _EACH, "candidate"): _SENTINEL,
    ("columns", _EACH, "sentinel_verdicts", _EACH, "verdict"): _WORD,
    ("columns", _EACH, "sentinel_verdicts", _EACH, "reason"): _WORD,
    ("columns", _EACH, "sentinel_verdicts", _EACH, "n_occurrences"): _COUNT,
    # WHICH PUBLISHED ABSENT SPELLINGS THIS DECISION TOOK OUT (repair
    # pass of landing 2b.6). Every member is already a key of this
    # column's `missing_by_source`, so the floor has already governed
    # it and nothing new about the table is published here: what is
    # new is the LINK between a spelling and the pass that made it
    # absent, which no count in the document can supply and which two
    # readers were guessing at.
    ("columns", _EACH, "sentinel_verdicts", _EACH, "spellings"): _ARRAY,
    (
        "columns", _EACH, "sentinel_verdicts", _EACH, "spellings", _EACH
    ): _SPELLING,
    # The label roles.
    # ...and the names of the levels the floor held back (lane CODES-2, plan
    # P4-D471; the owner's answer Z1 = B): values of the real table, each a
    # spelling, published WITHOUT a count of its own beside the pooled
    # total, only where the column's `no`, or the word screen, names them.
    ("columns", _EACH, "held_back_names"): _ARRAY,
    ("columns", _EACH, "held_back_names", _EACH): _SPELLING,
    ("columns", _EACH, "levels"): _ARRAY,
    ("columns", _EACH, "levels", _EACH): _OBJECT,
    ("columns", _EACH, "levels", _EACH, "label"): _SPELLING,
    ("columns", _EACH, "levels", _EACH, "count"): _FLOOR_COUNT,
    # HOW MANY OF THE LEVEL'S CELLS WORE THE LABEL'S OWN WRITTEN FORM
    # (plan amendment A-P4-47). A plain `_COUNT` and not `_HELD_BACK`:
    # it is a count of the cells of a PUBLISHED level, so it is written
    # at every floor, and at a floor of one it is simply the level's
    # form-bearing cells with nothing held back anywhere.
    ("columns", _EACH, "levels", _EACH, "shape_form_cells"): _COUNT,
    ("columns", _EACH, "levels", _EACH, "variants"): _OBJECT,
    ("columns", _EACH, "levels", _EACH, "variants", _KEY_OF): _SPELLING,
    ("columns", _EACH, "levels", _EACH, "variants", _ANY_KEY): _FLOOR_COUNT,
    ("columns", _EACH, "levels", _EACH, "variants_withheld"): _OBJECT,
    (
        "columns",
        _EACH,
        "levels",
        _EACH,
        "variants_withheld",
        _KEY_OF,
    ): _BELOW_THE_FLOOR,
    (
        "columns",
        _EACH,
        "levels",
        _EACH,
        "variants_withheld",
        _ANY_KEY,
    ): _COUNT,
    ("columns", _EACH, "suppressed_levels"): _HELD_BACK,
    ("columns", _EACH, "suppressed_rows"): _HELD_BACK,
    # A POOL COUNTED IN PEOPLE (lane PL, plan P4-D453): where the twin's
    # stand-ins start, made-up spellings worked out from the published levels
    # alone.
    ("columns", _EACH, "pool_in_people"): _OBJECT,
    ("columns", _EACH, "pool_in_people", "number_from"): _STAND_IN_START,
    ("columns", _EACH, "pool_in_people", "word_from"): _STAND_IN_START,
    # VALUES TYPED BY A KEY (lane KV, plan P4-D487): a key column says which
    # value column its keys type (`keyed`); the value column carries its key
    # column's name and a block a common key, each the key's published label
    # beside a column block of the key's cells (`_KEY_BLOCK`), and the rare
    # keys' pooled block.
    ("columns", _EACH, "keyed"): _KNOWN_NAME,
    ("columns", _EACH, "by_key"): _OBJECT,
    ("columns", _EACH, "by_key", "key"): _KNOWN_NAME,
    ("columns", _EACH, "by_key", "key_blocks"): _ARRAY,
    ("columns", _EACH, "by_key", "key_blocks", _EACH): _OBJECT,
    ("columns", _EACH, "by_key", "key_blocks", _EACH, "key"): _SPELLING,
    ("columns", _EACH, "by_key", "key_blocks", _EACH, "block"): _KEY_BLOCK,
    ("columns", _EACH, "by_key", "pool"): _KEY_BLOCK,
    # ...and a column counted absent says the count is not published, and,
    # where its cells read as text, the word its twin writes (repair 1).
    ("columns", _EACH, "present_count_withheld"): _FLAG_TRUE,
    ("columns", _EACH, "withheld_words_from"): _STAND_IN_START,
    # THE SCALE OF THE POOLED NUMBERS (plan P4-D301, ledger K-2B-50):
    # how many cells of the held-back levels read as numbers, and that
    # group's mean. TWO aggregates over ONE group, which is why they
    # carry no floor of their own beyond the count's: a mean over a
    # group at the disclosure line is a fact about the group. The
    # POPULATION SPREAD that stood beside them is withdrawn by the
    # owner's decision of 2026-09-21 (plan P4-D302), because a mean and
    # a spread together solve for a tightly spaced pool's own values.
    ("columns", _EACH, "suppressed_numbers"): _OBJECT,
    ("columns", _EACH, "suppressed_numbers", "n_cells"): _POOLED_SCALE_COUNT,
    ("columns", _EACH, "suppressed_numbers", "mean"): _MAYBE_NUMBER,
    ("columns", _EACH, "level_ceiling"): _COUNT,
    # The numeric roles.
    ("columns", _EACH, "percentiles"): _OBJECT,
    ("columns", _EACH, "percentiles", _KEY_OF): _WORD,
    ("columns", _EACH, "percentiles", _ANY_KEY): _MAYBE_NUMBER,
    # The ninety rungs the ladder above does not name (plan P4-D4.10).
    ("columns", _EACH, "percentiles_between"): _OBJECT,
    ("columns", _EACH, "percentiles_between", _KEY_OF): _WORD,
    ("columns", _EACH, "percentiles_between", _ANY_KEY): _MAYBE_NUMBER,
    ("columns", _EACH, "mean"): _MAYBE_NUMBER,
    ("columns", _EACH, "std"): _MAYBE_NUMBER,
    ("columns", _EACH, "skew"): _MAYBE_NUMBER,
    ("columns", _EACH, "kurtosis"): _MAYBE_NUMBER,
    ("columns", _EACH, "n_distinct_values"): _COUNT,
    # THE MODE PAIR (plan P4-D4.11). The value is a published number
    # like a ladder rung and may be absent, which is what the withheld
    # pair looks like; the count is a count, and is nought exactly when
    # the value is absent.
    ("columns", _EACH, "mode"): _MAYBE_NUMBER,
    ("columns", _EACH, "mode_count"): _COUNT,
    ("columns", _EACH, "std_unrepresentable"): _FLAG,
    ("columns", _EACH, "n_zero"): _COUNT,
    ("columns", _EACH, "n_negative_unrepresentable"): _COUNT,
    ("columns", _EACH, "n_rows"): _COUNT,
    ("columns", _EACH, "integer_valued"): _FLAG,
    ("columns", _EACH, "n_used_in_statistics"): _COUNT,
    ("columns", _EACH, "n_left_out_of_statistics"): _COUNT,
    ("columns", _EACH, "numeric_share"): _NUMBER,
    # THE JOINED-NUMBER ROLE (plan P4-D21). `separator` is a spelling
    # the table's cells wear, admitted on exactly the terms the affix
    # pair is; `parts` holds one quantitative block per position, so
    # every numeric key is repeated one level down. `n_joined`,
    # `n_parts` and `n_unparsed` answer for the CELLS.
    ("columns", _EACH, "separator"): _AFFIX,
    ("columns", _EACH, "n_parts"): _COUNT,
    ("columns", _EACH, "n_joined"): _COUNT,
    ("columns", _EACH, "part_min_widths"): _ARRAY,
    ("columns", _EACH, "part_min_widths", _EACH): _COUNT,
    # How the positions move together, one pair at a time. An agreement
    # runs from -1 to 1 and is a number like any other statistic this
    # format publishes; a count of rows is a count.
    ("columns", _EACH, "part_agreements"): _ARRAY,
    ("columns", _EACH, "part_agreements", _EACH): _NUMBER,
    ("columns", _EACH, "part_above"): _ARRAY,
    ("columns", _EACH, "part_above", _EACH): _COUNT,
    # THE COMPOUND ROLE (residual R-P4-13, landing L8). Two counts of
    # CELLS that sum to `n_present`, so every present cell is in
    # exactly one published population and a reader can check the
    # arithmetic. That sum is the answer to review item P1-R6-F7,
    # which deleted a rule describing part of a column and saying
    # nothing about the rest.
    ("columns", _EACH, "n_numeric_cells"): _COUNT,
    # ...and the third population (residual R-P4-149).
    ("columns", _EACH, "n_numeric_out_of_range"): _COUNT,
    ("columns", _EACH, "n_numeric_contradictory"): _COUNT,
    ("columns", _EACH, "n_label_cells"): _COUNT,
    # The numeric half's own counts of different written cells, which
    # the generator spends as its spelling budget. They are stated
    # HERE, at the column's own level, rather than inside `numbers`:
    # the rules for that sub-block are derived from what one position
    # of a joined column publishes, and a position publishes neither.
    ("columns", _EACH, "n_numeric_distinct"): _COUNT,
    ("columns", _EACH, "n_numeric_distinct_folded"): _COUNT,
    ("columns", _EACH, "parts"): _ARRAY,
    ("columns", _EACH, "parts", _EACH): _OBJECT,
    ("columns", _EACH, "parts", _EACH, "percentiles"): _OBJECT,
    ("columns", _EACH, "parts", _EACH, "percentiles", _KEY_OF): _WORD,
    ("columns", _EACH, "parts", _EACH, "percentiles", _ANY_KEY): _MAYBE_NUMBER,
    ("columns", _EACH, "parts", _EACH, "mean"): _MAYBE_NUMBER,
    ("columns", _EACH, "parts", _EACH, "std"): _MAYBE_NUMBER,
    ("columns", _EACH, "parts", _EACH, "skew"): _MAYBE_NUMBER,
    ("columns", _EACH, "parts", _EACH, "kurtosis"): _MAYBE_NUMBER,
    ("columns", _EACH, "parts", _EACH, "n_distinct_values"): _COUNT,
    ("columns", _EACH, "parts", _EACH, "percentiles_between"): _OBJECT,
    ("columns", _EACH, "parts", _EACH, "percentiles_between", _KEY_OF): _WORD,
    (
        "columns", _EACH, "parts", _EACH, "percentiles_between", _ANY_KEY
    ): _MAYBE_NUMBER,
    ("columns", _EACH, "parts", _EACH, "mode"): _MAYBE_NUMBER,
    ("columns", _EACH, "parts", _EACH, "mode_count"): _COUNT,
    ("columns", _EACH, "parts", _EACH, "std_unrepresentable"): _FLAG,
    ("columns", _EACH, "parts", _EACH, "n_zero"): _COUNT,
    ("columns", _EACH, "parts", _EACH, "n_negative"): _COUNT,
    ("columns", _EACH, "parts", _EACH, "n_negative_unrepresentable"): _COUNT,
    ("columns", _EACH, "parts", _EACH, "n_rows"): _COUNT,
    ("columns", _EACH, "parts", _EACH, "integer_valued"): _FLAG,
    ("columns", _EACH, "parts", _EACH, "n_used_in_statistics"): _COUNT,
    ("columns", _EACH, "parts", _EACH, "n_left_out_of_statistics"): _COUNT,
    ("columns", _EACH, "parts", _EACH, "numeric_share"): _NUMBER,
    ("columns", _EACH, "parts", _EACH, "numeric_styles"): _OBJECT,
    ("columns", _EACH, "parts", _EACH, "numeric_styles", _KEY_OF): _WORD,
    ("columns", _EACH, "parts", _EACH, "numeric_styles", _ANY_KEY): _POOLED_CENSUS_ENTRY,
    ("columns", _EACH, "parts", _EACH, "group_separator"): _AFFIX,
    ("columns", _EACH, "parts", _EACH, "negative_form"): _WORD,
    ("columns", _EACH, "parts", _EACH, "wide_runs"): _WORD,
    ("columns", _EACH, "parts", _EACH, "decimal_plus"): _OBJECT,
    ("columns", _EACH, "parts", _EACH, "decimal_plus", _KEY_OF): _WORD,
    ("columns", _EACH, "parts", _EACH, "decimal_plus", _ANY_KEY): _MIXTURE_ENTRY,
    # THE TWO MIXTURE CENSUSES ONE LEVEL DOWN (landing 2b.7). A
    # position publishes neither -- it is read from figures and one
    # point alone, so it wears no notation and no mark, and the loader
    # holds it to the empty census under NS2 and TM1 -- but the paths
    # are stated all the same, because a path missing from this table
    # is a refusal and the empty mapping still stands at one.
    ("columns", _EACH, "parts", _EACH, "negative_notations"): _OBJECT,
    ("columns", _EACH, "parts", _EACH, "negative_notations", _KEY_OF): _WORD,
    (
        "columns", _EACH, "parts", _EACH, "negative_notations", _ANY_KEY
    ): _MIXTURE_ENTRY,
    ("columns", _EACH, "parts", _EACH, "thousands_marks"): _OBJECT,
    ("columns", _EACH, "parts", _EACH, "thousands_marks", _KEY_OF): _WORD,
    (
        "columns", _EACH, "parts", _EACH, "thousands_marks", _ANY_KEY
    ): _MIXTURE_ENTRY,
    ("columns", _EACH, "parts", _EACH, "fraction_widths"): _OBJECT,
    ("columns", _EACH, "parts", _EACH, "fraction_widths", _KEY_OF): _WIDTH,
    ("columns", _EACH, "parts", _EACH, "fraction_widths", _ANY_KEY): _POOLED_CENSUS_ENTRY,
    ("columns", _EACH, "parts", _EACH, "pad_widths"): _OBJECT,
    ("columns", _EACH, "parts", _EACH, "pad_widths", _KEY_OF): _WIDTH,
    ("columns", _EACH, "parts", _EACH, "pad_widths", _ANY_KEY): _POOLED_CENSUS_ENTRY,
    ("columns", _EACH, "parts", _EACH, "field_widths"): _OBJECT,
    ("columns", _EACH, "parts", _EACH, "field_widths", _KEY_OF): _WIDTH,
    ("columns", _EACH, "parts", _EACH, "field_widths", _ANY_KEY): _POOLED_CENSUS_ENTRY,
    ("columns", _EACH, "parts", _EACH, "value_histogram"): _OBJECT,
    ("columns", _EACH, "parts", _EACH, "value_histogram", _KEY_OF): _BIN,
    ("columns", _EACH, "parts", _EACH, "value_histogram", _ANY_KEY): _FLOORED_ENTRY,
    ("columns", _EACH, "parts", _EACH, "empty_bins"): _ARRAY,
    ("columns", _EACH, "parts", _EACH, "empty_bins", _EACH): _EMPTY_BIN,
    # ...and each position's own stretch edges (residual R-P4-138).
    ("columns", _EACH, "parts", _EACH, "empty_edges"): _ARRAY,
    ("columns", _EACH, "parts", _EACH, "empty_edges", _EACH): _ARRAY,
    ("columns", _EACH, "parts", _EACH, "empty_edges", _EACH, _EACH): _NUMBER,
    # THE TAIL FACTS (stage 3, plan P4-D344, contract L4 and T1 to T4):
    # null below the block floor, two nulls where only the moments are
    # published, otherwise per side the boundary percent, the rows
    # beyond it, their mean and root-mean-square distance from it, and on
    # a listed grid tail its values. EACH DISTANCE MAY BE NULL (plan
    # P4-D349): a tail whose published pair would give back an outer cell
    # or how many outer cells hold one value publishes its boundary and
    # its rows and neither distance, which is the numeric role taking the
    # answer the date and clock role already had.
    ("columns", _EACH, "parts", _EACH, "tails"): _MAYBE_OBJECT,
    ("columns", _EACH, "parts", _EACH, "tails", "low"): _MAYBE_OBJECT,
    ("columns", _EACH, "parts", _EACH, "tails", "high"): _MAYBE_OBJECT,
    **{
        ("columns", _EACH, "parts", _EACH, "tails", side, leaf): kind
        for side in ("low", "high")
        for leaf, kind in (
            ("percent", _TAIL_PERCENT),
            ("rows", _FLOOR_COUNT),
            ("mean_distance", _MAYBE_NUMBER),
            ("rms_distance", _MAYBE_NUMBER),
            ("values", _ARRAY),
        )
    },
    **{
        ("columns", _EACH, "parts", _EACH, "tails", side, "values", _EACH): _NUMBER
        for side in ("low", "high")
    },
    # ...and the histogram of a tail block, in groups of at least the
    # floor between the two boundary rungs (contract BG1).
    ("columns", _EACH, "parts", _EACH, "bin_groups"): _ARRAY,
    ("columns", _EACH, "parts", _EACH, "bin_groups", _EACH): _OBJECT,
    ("columns", _EACH, "parts", _EACH, "bin_groups", _EACH, "first"): _BIN_INDEX,
    ("columns", _EACH, "parts", _EACH, "bin_groups", _EACH, "last"): _BIN_INDEX,
    ("columns", _EACH, "parts", _EACH, "bin_groups", _EACH, "count"): _FLOOR_COUNT,
    # The affixed-number role: the pair it publishes, how many cells
    # wore it, and the four counts that answer for the CORES rather
    # than for the cells.
    ("columns", _EACH, "affix_prefix"): _AFFIX,
    ("columns", _EACH, "affix_suffix"): _AFFIX,
    # ...and the other wrappers this column wears (plan P4-D36), each
    # with the count of cells that wear it. The two sides are written
    # under the same rule the pair above is, so a wrapper is spelled
    # one way wherever it appears.
    ("columns", _EACH, "affix_variants"): _ARRAY,
    ("columns", _EACH, "affix_variants", _EACH): _OBJECT,
    ("columns", _EACH, "affix_variants", _EACH, "prefix"): _AFFIX,
    ("columns", _EACH, "affix_variants", _EACH, "suffix"): _AFFIX,
    ("columns", _EACH, "affix_variants", _EACH, "count"): _COUNT,
    # THE FOUR CLASSES OF ONE WRAPPER'S CORES (plan P4-D37), which
    # close on that wrapper's own count exactly as the column's four
    # close on `n_affixed`. The block beside them cannot be loaded
    # without them: a loader checking a block of a subset has to know
    # how many of its cores read as numbers.
    ("columns", _EACH, "affix_variants", _EACH, "n_core_numeric"): _COUNT,
    (
        "columns", _EACH, "affix_variants", _EACH, "n_core_out_of_range"
    ): _COUNT,
    (
        "columns", _EACH, "affix_variants", _EACH, "n_core_contradictory"
    ): _COUNT,
    (
        "columns", _EACH, "affix_variants", _EACH, "n_core_not_numeric"
    ): _COUNT,
    ("columns", _EACH, "affix_variants", _EACH, "n_core_distinct"): _COUNT,
    (
        "columns", _EACH, "affix_variants", _EACH, "n_core_distinct_folded"
    ): _COUNT,
    ("columns", _EACH, "n_affixed"): _COUNT,
    # ...and how many different CORES the cells carry (plan P4-D36),
    # which is not how many different cells they are once a column
    # wears more than one wrapper.
    ("columns", _EACH, "n_core_distinct"): _COUNT,
    ("columns", _EACH, "n_core_distinct_folded"): _COUNT,
    ("columns", _EACH, "n_core_numeric"): _COUNT,
    ("columns", _EACH, "n_core_out_of_range"): _COUNT,
    ("columns", _EACH, "n_core_contradictory"): _COUNT,
    ("columns", _EACH, "n_core_not_numeric"): _COUNT,
    ("columns", _EACH, "numeric_styles"): _OBJECT,
    ("columns", _EACH, "numeric_styles", _KEY_OF): _WORD,
    ("columns", _EACH, "numeric_styles", _ANY_KEY): _POOLED_CENSUS_ENTRY,
    # The forms map's sibling: how many figures the cells written with a
    # point wrote after it. Its keys are figures rather than words of
    # this package, so they are held to a grammar rather than to a
    # vocabulary -- and its counts are held to the floor exactly as the
    # forms map's are, the pooled remainder included.
    # THE MARK BETWEEN THOUSANDS. A spelling the table's cells wear,
    # admitted on the same terms as the affix pair and the joined
    # role's separator, because it is the same kind of fact: how
    # this column's numbers were written, carrying no value of any
    # cell and no count of any group.
    ("columns", _EACH, "group_separator"): _AFFIX,
    # ...and how its negatives and its signed decimals were written
    # (landing 2b.2): a word of this package's own four, and a count the
    # loader holds to the floor (contract DP1).
    ("columns", _EACH, "negative_form"): _WORD,
    # ...and whether its wide runs are their own values' text (landing
    # 2b.13, plan P4-D90): a word of this package's own three.
    ("columns", _EACH, "wide_runs"): _WORD,
    ("columns", _EACH, "decimal_plus"): _OBJECT,
    ("columns", _EACH, "decimal_plus", _KEY_OF): _WORD,
    ("columns", _EACH, "decimal_plus", _ANY_KEY): _MIXTURE_ENTRY,
    # THE TWO MIXTURE CENSUSES (landing 2b.7, plan P4-D65.2). Their keys
    # are conventions from a closed vocabulary, held to it by
    # `PUBLICATION_WORDS` as every other word-keyed map is, and their
    # counts to the census floor rather than to the settings floor.
    ("columns", _EACH, "negative_notations"): _OBJECT,
    ("columns", _EACH, "negative_notations", _KEY_OF): _WORD,
    ("columns", _EACH, "negative_notations", _ANY_KEY): _MIXTURE_ENTRY,
    ("columns", _EACH, "thousands_marks"): _OBJECT,
    ("columns", _EACH, "thousands_marks", _KEY_OF): _WORD,
    ("columns", _EACH, "thousands_marks", _ANY_KEY): _MIXTURE_ENTRY,
    ("columns", _EACH, "fraction_widths"): _OBJECT,
    ("columns", _EACH, "fraction_widths", _KEY_OF): _WIDTH,
    ("columns", _EACH, "fraction_widths", _ANY_KEY): _POOLED_CENSUS_ENTRY,
    ("columns", _EACH, "shape_forms"): _OBJECT,
    ("columns", _EACH, "shape_forms", _KEY_OF): _SHAPE_FORM,
    ("columns", _EACH, "shape_forms", _ANY_KEY): _FLOORED_ENTRY,
    # What no real run of figures of a column of free text, or of the held-back
    # labels of a label column, opens with (lane HB, plan P4-D442): keyed by a
    # merged width of four figures or more, or 3 beside nothing, each an opening
    # of one to four figures, the first never a nought, or nothing.
    ("columns", _EACH, "figure_openings"): _OBJECT,
    ("columns", _EACH, "figure_openings", _KEY_OF): _FIGURE_WIDTH,
    ("columns", _EACH, "figure_openings", _ANY_KEY): _FIGURE_OPENING,
    # ...and the widths at which a held key of noughts alone exists (lane
    # HB3-a, plan P4-D482): whole numbers of three or more.
    ("columns", _EACH, "figure_noughts"): _ARRAY,
    ("columns", _EACH, "figure_noughts", _EACH): _NUMBER,
    ("columns", _EACH, "pad_widths"): _OBJECT,
    ("columns", _EACH, "pad_widths", _KEY_OF): _WIDTH,
    ("columns", _EACH, "pad_widths", _ANY_KEY): _POOLED_CENSUS_ENTRY,
    # The spellings of a count column that wrote one number more than
    # one way (plan P4-D123). A key IS a spelling of the table -- `007`
    # beside `7` -- on the role that publishes its values, and it is
    # `_DIGITS` because `_DIGITS` admits the padding that is the point.
    ("columns", _EACH, "number_spellings"): _OBJECT,
    ("columns", _EACH, "number_spellings", _KEY_OF): _DIGITS,
    ("columns", _EACH, "number_spellings", _ANY_KEY): _FLOORED_ENTRY,
    # ...and a few-valued column's own numbers where a wide gap stands
    # among them (lane GG, plan P4-D440): spellings, no count.
    ("columns", _EACH, "few_values"): _ARRAY,
    ("columns", _EACH, "few_values", _EACH): _VALUE_SPELLING,
    # ...and the third census, over EVERY whole-written cell rather
    # than over one form of them (P4-D30). Same grammar, same floor.
    ("columns", _EACH, "field_widths"): _OBJECT,
    ("columns", _EACH, "field_widths", _KEY_OF): _WIDTH,
    ("columns", _EACH, "field_widths", _ANY_KEY): _POOLED_CENSUS_ENTRY,
    ("columns", _EACH, "value_histogram"): _OBJECT,
    ("columns", _EACH, "value_histogram", _KEY_OF): _BIN,
    ("columns", _EACH, "value_histogram", _ANY_KEY): _FLOORED_ENTRY,
    # ...and the bins that hold nothing, which is a LIST rather than a
    # census: there is no count beside a bin holding none, and writing
    # one would be a nought standing where every other entry of this
    # document stands for a cell somebody's table holds (P4-D32).
    ("columns", _EACH, "empty_bins"): _ARRAY,
    ("columns", _EACH, "empty_bins", _EACH): _EMPTY_BIN,
    # ...and the REAL edges of each of those stretches (residual
    # R-P4-138). One `[below, above]` pair per run of empty bins, each
    # a value of a real cell -- the same kind of fact a ladder rung is,
    # which is what the owner's ruling of 2026-09-03 on the small-cell
    # floor already covers.
    ("columns", _EACH, "empty_edges"): _ARRAY,
    ("columns", _EACH, "empty_edges", _EACH): _ARRAY,
    ("columns", _EACH, "empty_edges", _EACH, _EACH): _NUMBER,
    # THE TAIL FACTS (stage 3, plan P4-D344, contract L4 and T1 to T4):
    # null below the block floor, two nulls where only the moments are
    # published, otherwise per side the boundary percent, the rows
    # beyond it, their mean and root-mean-square distance from it, and on
    # a listed grid tail its values. EACH DISTANCE MAY BE NULL (plan
    # P4-D349): a tail whose published pair would give back an outer cell
    # or how many outer cells hold one value publishes its boundary and
    # its rows and neither distance, which is the numeric role taking the
    # answer the date and clock role already had.
    ("columns", _EACH, "tails"): _MAYBE_OBJECT,
    ("columns", _EACH, "tails", "low"): _MAYBE_OBJECT,
    ("columns", _EACH, "tails", "high"): _MAYBE_OBJECT,
    **{
        ("columns", _EACH, "tails", side, leaf): kind
        for side in ("low", "high")
        for leaf, kind in (
            ("percent", _TAIL_PERCENT),
            ("rows", _FLOOR_COUNT),
            ("mean_distance", _MAYBE_NUMBER),
            ("rms_distance", _MAYBE_NUMBER),
            ("values", _ARRAY),
        )
    },
    **{
        ("columns", _EACH, "tails", side, "values", _EACH): _NUMBER
        for side in ("low", "high")
    },
    # ...and the histogram of a tail block, in groups of at least the
    # floor between the two boundary rungs (contract BG1).
    ("columns", _EACH, "bin_groups"): _ARRAY,
    ("columns", _EACH, "bin_groups", _EACH): _OBJECT,
    ("columns", _EACH, "bin_groups", _EACH, "first"): _BIN_INDEX,
    ("columns", _EACH, "bin_groups", _EACH, "last"): _BIN_INDEX,
    ("columns", _EACH, "bin_groups", _EACH, "count"): _FLOOR_COUNT,
    # The counts every numeric-looking column carries, and the ones a
    # column of numbers nothing can hold carries in their place.
    ("columns", _EACH, "n_negative"): _COUNT,
    ("columns", _EACH, "n_positive"): _COUNT,
    ("columns", _EACH, "n_sign_unknown"): _COUNT,
    ("columns", _EACH, "n_whole"): _COUNT,
    ("columns", _EACH, "n_fraction"): _COUNT,
    ("columns", _EACH, "n_whole_unknown"): _COUNT,
    # The datetime role.
    ("columns", _EACH, "format"): _WORD,
    ("columns", _EACH, "resolution"): _WORD,
    ("columns", _EACH, "time_precision"): _WORD,
    ("columns", _EACH, "subsecond_digits"): _COUNT,
    ("columns", _EACH, "datetimes_read_at"): _WORD,
    ("columns", _EACH, "offset_rule"): _OFFSET_RULE,
    # A statement about every parsed cell at once, and a real yes or no
    # (plan P4-D39): a count standing in for it is refused.
    ("columns", _EACH, "all_at_midnight"): _FLAG,
    # ...and how many parsed cells stood at midnight, a group on both
    # sides of the floor or nothing at all (landing 2b.3). "Nothing at
    # all" is written `null` since landing 2b.6, and it covers a real
    # nought too: see `_BOTH_SIDES_OR_UNAVAILABLE`.
    ("columns", _EACH, "n_at_midnight"): _BOTH_SIDES_OR_UNAVAILABLE,
    # THE TWO TAILS AND THEIR UNIT (stage 3, plan P4-D328; contract DT1 to
    # DT4), in place of the first and last value and the offsets those two
    # rows wore. A tail is a boundary held by a real cell that is never one
    # of the outer ones, a count of cells at the floor or above, two
    # distances, and -- where it holds few values -- which values those are.
    # These rows serve the clock role too: they are keyed by PATH, and a
    # clock value is canonical moment text by the same character rule.
    ("columns", _EACH, "tail_unit"): _WORD,
    ("columns", _EACH, "low_tail"): _MAYBE_OBJECT,
    ("columns", _EACH, "low_tail", "boundary"): _MOMENT_TEXT,
    ("columns", _EACH, "low_tail", "rows"): _FLOOR_COUNT,
    ("columns", _EACH, "low_tail", "mean_distance"): _MAYBE_NUMBER,
    ("columns", _EACH, "low_tail", "rms_distance"): _MAYBE_NUMBER,
    ("columns", _EACH, "low_tail", "values"): _MAYBE_ARRAY,
    ("columns", _EACH, "low_tail", "values", _EACH): _MOMENT_TEXT,
    ("columns", _EACH, "high_tail"): _MAYBE_OBJECT,
    ("columns", _EACH, "high_tail", "boundary"): _MOMENT_TEXT,
    ("columns", _EACH, "high_tail", "rows"): _FLOOR_COUNT,
    ("columns", _EACH, "high_tail", "mean_distance"): _MAYBE_NUMBER,
    ("columns", _EACH, "high_tail", "rms_distance"): _MAYBE_NUMBER,
    ("columns", _EACH, "high_tail", "values"): _MAYBE_ARRAY,
    ("columns", _EACH, "high_tail", "values", _EACH): _MOMENT_TEXT,
    ("columns", _EACH, "date_percentiles"): _OBJECT,
    ("columns", _EACH, "date_percentiles", _KEY_OF): _WORD,
    ("columns", _EACH, "date_percentiles", _ANY_KEY): _MAYBE_MOMENT,
    # The clock role's own two. The tails and `n_unparsed` need no row of
    # their own and must not be given one: these rules are keyed by PATH
    # and not by role, so the rows above already serve both roles.
    ("columns", _EACH, "clock_form"): _WORD,
    # HOW MANY PARSED CELLS WORE EACH FORM. Its keys are members of
    # this package's own format vocabulary, so a spelling of the table
    # cannot become one; its counts are exact and no floor governs
    # them, which is why they are plain counts rather than floored
    # entries (contract C6-25).
    ("columns", _EACH, "resolution_mix"): _OBJECT,
    ("columns", _EACH, "resolution_mix", _KEY_OF): _WORD,
    ("columns", _EACH, "resolution_mix", _ANY_KEY): _COUNT,
    ("columns", _EACH, "clock_percentiles"): _OBJECT,
    ("columns", _EACH, "clock_percentiles", _KEY_OF): _WORD,
    ("columns", _EACH, "clock_percentiles", _ANY_KEY): _MAYBE_MOMENT,
    ("columns", _EACH, "n_unparsed"): _COUNT,
    ("columns", _EACH, "utc_offsets"): _OBJECT,
    ("columns", _EACH, "utc_offsets", _KEY_OF): _OFFSET,
    ("columns", _EACH, "utc_offsets", _ANY_KEY): _POOLED_CENSUS_ENTRY,
    # HOW MANY PARSED CELLS WORE EACH MARK BETWEEN DAY AND CLOCK (plan
    # P4-D39). Its keys are this package's own names, and unlike the form
    # census above its counts ARE floored, with a withheld pool.
    ("columns", _EACH, "datetime_separators"): _OBJECT,
    ("columns", _EACH, "datetime_separators", _KEY_OF): _WORD,
    ("columns", _EACH, "datetime_separators", _ANY_KEY): _POOLED_CENSUS_ENTRY,
    # HOW THE DATES WERE WRITTEN (landing 2b.6): four censuses of this
    # package's own form words, each floored with a withheld pool
    # exactly as the mark census above is. None of them carries a
    # spelling of anybody's table -- the keys are words this module
    # wrote, and the counts are counts of conventions.
    ("columns", _EACH, "date_field_widths"): _OBJECT,
    ("columns", _EACH, "date_field_widths", _KEY_OF): _WORD,
    ("columns", _EACH, "date_field_widths", _ANY_KEY): _DISCLOSED_ENTRY,
    ("columns", _EACH, "month_name_styles"): _OBJECT,
    ("columns", _EACH, "month_name_styles", _KEY_OF): _WORD,
    ("columns", _EACH, "month_name_styles", _ANY_KEY): _DISCLOSED_ENTRY,
    ("columns", _EACH, "quarter_marker_case"): _OBJECT,
    ("columns", _EACH, "quarter_marker_case", _KEY_OF): _WORD,
    ("columns", _EACH, "quarter_marker_case", _ANY_KEY): _DISCLOSED_ENTRY,
    ("columns", _EACH, "zulu_case"): _OBJECT,
    ("columns", _EACH, "zulu_case", _KEY_OF): _WORD,
    ("columns", _EACH, "zulu_case", _ANY_KEY): _DISCLOSED_ENTRY,
    # WHICH DAYS OF THE WEEK THE BODY FALLS ON (landing 3b.1): groups of
    # weekdays, each counted nought or at the census line.
    ("columns", _EACH, "weekday_census"): _ARRAY,
    ("columns", _EACH, "weekday_census", _EACH): _OBJECT,
    ("columns", _EACH, "weekday_census", _EACH, "first"): _WEEKDAY,
    ("columns", _EACH, "weekday_census", _EACH, "last"): _WEEKDAY,
    ("columns", _EACH, "weekday_census", _EACH, "count"): _WEEKDAY_COUNT,
    # THE CENSUSES STAGE 3B RESERVES (plan P4-D364): each an EMPTY list,
    # and `clock_step` nothing at all, until the landing that fills it
    # adds the rows of what it holds -- so a list holding anything is a
    # path no rule names, and is refused here before the loader sees it.
    ("columns", _EACH, "hour_census"): _ARRAY,
    ("columns", _EACH, "minute_census"): _ARRAY,
    ("columns", _EACH, "second_census"): _ARRAY,
    ("columns", _EACH, "minute_heaps"): _ARRAY,
    ("columns", _EACH, "second_heaps"): _ARRAY,
    ("columns", _EACH, "day_of_month_census"): _ARRAY,
    ("columns", _EACH, "heavy_dates"): _ARRAY,
    ("columns", _EACH, "clock_census"): _ARRAY,
    ("columns", _EACH, "clock_heaps"): _ARRAY,
    ("columns", _EACH, "clock_step"): _CLOCK_STEP,
    ("columns", _EACH, "clock_codes"): _ARRAY,
    # ...and the key the second cut reserved (plan P4-D386), which landing
    # R4 fills on a column of counted dates and leaves `null` on every
    # other: how the column writes its counts (`date_counts.CountForm`).
    # THE GRAIN A COLUMN OF DATES OR TIMES WAS POOLED AT (plan P4-D417,
    # contract NF128, NF129 and TG1): its rung, the column's precision, its kind,
    # how its cells read, the rows its walk read and the spans it passed.
    ("columns", _EACH, "time_grain"): _OBJECT,
    # THE SAFE HARBOR TOP-CODE (plan P4-D427): 90, read "90 or more", on a
    # column described with every value above 89 read as 90.
    ("columns", _EACH, "top_coded"): _COUNT,
    # ...and the rule its small top category was pooled under (lane SH3's
    # repair, plan P4-D454): the floor, written whether or not one was
    # pooled, and the subject columns it was counted in.
    ("columns", _EACH, "top_category_pooled"): _COUNT,
    ("columns", _EACH, "top_category_people"): _ARRAY,
    ("columns", _EACH, "top_category_people", _EACH): _KNOWN_NAME,
    # ...and the age words its top-code read around its numbers (lane HB2,
    # plan P4-D477): `true` where a cell holds them (`Age 95`).
    ("columns", _EACH, "top_coded_words"): _FLAG,
    # ...and the two values its ends were pooled into in people (lane HB2,
    # plan P4-D477): the low band's highest value and the top band's lowest,
    # each a value the floor's people hold.
    ("columns", _EACH, "top_coded_ends"): _ARRAY,
    ("columns", _EACH, "top_coded_ends", _EACH): _NUMBER,
    # ...and the ages its two end bands are written as, the mean age of each
    # mean age (lane RX-1; `taxonomy.ends_band_values`).
    ("columns", _EACH, "top_coded_band_values"): _ARRAY,
    ("columns", _EACH, "top_coded_band_values", _EACH): _NUMBER,
    # ...and that its bands of ages past 89 were written as one band (plan
    # P4-D472; the orchestrator's LANE CZ-E RULINGS 6 (3)).
    ("columns", _EACH, "top_coded_bands"): _FLAG_TRUE,
    # RULE A1'S DESTINATION (lane CODES-1, plan P4-D439, contract C6-31g):
    # a written form, which carries no figure or letter of the table.
    ("columns", _EACH, "shape_forms_absorbed"): _SHAPE_FORM,
    # RULE A2'S POSITIONAL CENSUS (lane CODES-1, plan P4-D439, contract
    # C6-31h): for each named form, one entry a character of the form.
    ("columns", _EACH, "shape_form_places"): _OBJECT,
    ("columns", _EACH, "shape_form_places", _KEY_OF): _SHAPE_FORM,
    ("columns", _EACH, "shape_form_places", _ANY_KEY): _ARRAY,
    ("columns", _EACH, "shape_form_places", _ANY_KEY, _EACH): _PLACE_CHARACTERS,
    # ...AND THE SAFE HARBOR YEARS (plan P4-D434): the year that reads
    # "that year or earlier" on a column of years of birth described with
    # every year from 1850 to it read as it.
    ("columns", _EACH, "top_coded_year"): _COUNT,
    ("columns", _EACH, "time_grain", "rung"): _WORD,
    ("columns", _EACH, "time_grain", "finest"): _WORD,
    ("columns", _EACH, "time_grain", "kind"): _WORD,
    ("columns", _EACH, "time_grain", "reading"): _WORD,
    ("columns", _EACH, "time_grain", "mark"): _COUNT_MARK,
    ("columns", _EACH, "time_grain", "rows"): _COUNT,
    ("columns", _EACH, "time_grain", "people"): _COUNT,
    ("columns", _EACH, "time_grain", "spans"): _ARRAY,
    ("columns", _EACH, "time_grain", "spans", _EACH): _ARRAY,
    ("columns", _EACH, "time_grain", "spans", _EACH, _EACH): _GRAIN_SPAN_PART,
    ("columns", _EACH, "count_form"): _MAYBE_OBJECT,
    ("columns", _EACH, "count_form", "places"): _COUNT,
    ("columns", _EACH, "count_form", "trimmed"): _FLAG,
    ("columns", _EACH, "count_form", "significant"): _COUNT_SIGNIFICANT,
    ("columns", _EACH, "count_form", "exponent"): _FLAG,
    ("columns", _EACH, "count_form", "mark"): _COUNT_MARK,
    ("columns", _EACH, "count_form", "contacts"): _MAYBE_OBJECT,
    ("columns", _EACH, "count_form", "contacts", _KEY_OF): _CONTACT_WORD,
    ("columns", _EACH, "count_form", "contacts", _ANY_KEY): _DISCLOSED_ENTRY,
    # THE LANDINGS' ANCHORS (plan P4-D364): each landing of stage 3b adds
    # its rows below its own line.
    # anchor 3b-D1 (P4-D365)
    # anchor 3b-D0 (P4-D366)
    # anchor 3b-D2 (P4-D367)
    # anchor 3b-D3 (P4-D368)
    # WHICH DAYS OF THE MONTH THE BODY FALLS ON (landing 3b.3): groups of
    # bins, each counted nought or at the census line.
    ("columns", _EACH, "day_of_month_census", _EACH): _OBJECT,
    ("columns", _EACH, "day_of_month_census", _EACH, "first"): _MONTH_DAY,
    ("columns", _EACH, "day_of_month_census", _EACH, "last"): _MONTH_DAY,
    ("columns", _EACH, "day_of_month_census", _EACH, "count"): _MONTH_DAY_COUNT,
    # anchor 3b-D4 (P4-D369)
    # THE DATES THAT STAND OUT (landing 3b.6): each date and its count.
    ("columns", _EACH, "heavy_dates", _EACH): _OBJECT,
    ("columns", _EACH, "heavy_dates", _EACH, "date"): _HEAVY_DATE,
    ("columns", _EACH, "heavy_dates", _EACH, "count"): _HEAVY_COUNT,
    # anchor 3b-T1 (P4-D370)
    # anchor 3b-T2 (P4-D371)
    # WHICH HOURS OF THE DAY THE BODY FALLS ON (landing 3b.2-H): groups of
    # hours, each counted nought or at the census line.
    ("columns", _EACH, "hour_census", _EACH): _OBJECT,
    ("columns", _EACH, "hour_census", _EACH, "first"): _HOUR,
    ("columns", _EACH, "hour_census", _EACH, "last"): _HOUR,
    ("columns", _EACH, "hour_census", _EACH, "count"): _HOUR_COUNT,
    # anchor 3b-T3 (P4-D372)
    # WHICH MINUTES AND SECONDS THE BODY FALLS ON (landing 3b.4): groups of
    # values, each counted nought or at the census line, and heaps.
    ("columns", _EACH, "minute_census", _EACH): _OBJECT,
    ("columns", _EACH, "minute_census", _EACH, "first"): _CLOCK_FIELD_VALUE,
    ("columns", _EACH, "minute_census", _EACH, "last"): _CLOCK_FIELD_VALUE,
    ("columns", _EACH, "minute_census", _EACH, "count"): _CLOCK_FIELD_COUNT,
    ("columns", _EACH, "second_census", _EACH): _OBJECT,
    ("columns", _EACH, "second_census", _EACH, "first"): _CLOCK_FIELD_VALUE,
    ("columns", _EACH, "second_census", _EACH, "last"): _CLOCK_FIELD_VALUE,
    ("columns", _EACH, "second_census", _EACH, "count"): _CLOCK_FIELD_COUNT,
    ("columns", _EACH, "minute_heaps", _EACH): _OBJECT,
    ("columns", _EACH, "minute_heaps", _EACH, "value"): _CLOCK_FIELD_VALUE,
    ("columns", _EACH, "minute_heaps", _EACH, "count"): _CLOCK_FIELD_HEAP,
    ("columns", _EACH, "second_heaps", _EACH): _OBJECT,
    ("columns", _EACH, "second_heaps", _EACH, "value"): _CLOCK_FIELD_VALUE,
    ("columns", _EACH, "second_heaps", _EACH, "count"): _CLOCK_FIELD_HEAP,
    # anchor 3b-C1 (P4-D373)
    ("columns", _EACH, "clock_census", _EACH): _OBJECT,
    ("columns", _EACH, "clock_census", _EACH, "first"): _TEN_MINUTE_BIN,
    ("columns", _EACH, "clock_census", _EACH, "last"): _TEN_MINUTE_BIN,
    ("columns", _EACH, "clock_census", _EACH, "count"): _CLOCK_COUNT,
    ("columns", _EACH, "clock_heaps", _EACH): _OBJECT,
    ("columns", _EACH, "clock_heaps", _EACH, "value"): _CLOCK_VALUE,
    ("columns", _EACH, "clock_heaps", _EACH, "count"): _CLOCK_LINE_COUNT,
    ("columns", _EACH, "clock_codes", _EACH): _OBJECT,
    ("columns", _EACH, "clock_codes", _EACH, "spelling"): _SPELLING,
    ("columns", _EACH, "clock_codes", _EACH, "count"): _CLOCK_LINE_COUNT,
    # anchor 3b-C2 (P4-D374)
    # anchor 3b-G1 (P4-D375)
    # anchor 3b-G3 (P4-D376)
    # anchor 3b-G2 (P4-D377)
    # anchor 3b-7 (P4-D378)
    # anchor 3b-J (P4-D379)
    # anchor 3b-R2a (P4-D383)
    # anchor 3b-R2b (P4-D383)
    # anchor 3b-R2c (P4-D383)
    # anchor 3b-R4 (P4-D384)
    # The roles that publish no value at all.
    ("columns", _EACH, "min_length"): _COUNT,
    ("columns", _EACH, "max_length"): _COUNT,
    ("columns", _EACH, "all_whole_numbers"): _FLAG,
    ("columns", _EACH, "n_all_digits"): _COUNT,
    ("columns", _EACH, "n_code_alphabet"): _COUNT,
    # The census of layouts a declared identifier wore (7.12, plan
    # P4-D120). Its key space is its own and is NOT `_SHAPE_FORM`: a
    # layout carries six placeholders and fifteen marks where a written
    # form carries two and thirteen, and it may run to sixty-four
    # characters because a braced GUID is thirty-eight.
    ("columns", _EACH, "layout_forms"): _OBJECT,
    ("columns", _EACH, "layout_forms", _KEY_OF): _LAYOUT_FORM,
    ("columns", _EACH, "layout_forms", _ANY_KEY): _FLOORED_ENTRY,
    # The literal prefix a declared identifier's cells open with (owner
    # ruling 2026-09-17, item 1; contract 7.12a): the one text of the
    # table this block carries, and only under that ruling. Its keys are
    # `(column)` or a layout, and its values are letters and marks with
    # no figure, which is all `parsing.literal_prefix` ever writes.
    ("columns", _EACH, "layout_prefixes"): _OBJECT,
    ("columns", _EACH, "layout_prefixes", _KEY_OF): _PREFIX_SCOPE,
    ("columns", _EACH, "layout_prefixes", _ANY_KEY): _LITERAL_PREFIX,
    # What no real cell holds (lane ID-ROOM, plan P4-D432): keyed by a
    # named layout, that layout with places written out as characters no
    # real cell of it holds there; keyed `(spill)`, a layout no real cell
    # wears.
    ("columns", _EACH, "layout_exclusions"): _OBJECT,
    ("columns", _EACH, "layout_exclusions", _KEY_OF): _EXCLUSION_SCOPE,
    ("columns", _EACH, "layout_exclusions", _ANY_KEY): _LAYOUT_EXCLUSION,
    # The years a held date column's made-up dates take (lane ID-ROOM2,
    # plan P4-D457, contract 7.12c): runs `[first, last]` of years no real
    # cell of it is a date of, four figures from the year after the
    # reference year, or two-figure years.
    ("columns", _EACH, "made_up_years"): _ARRAY,
    ("columns", _EACH, "made_up_years", _EACH): _ARRAY,
    ("columns", _EACH, "made_up_years", _EACH, _EACH): _COUNT,
    ("columns", _EACH, "n_distinct_by_occurrences"): _OBJECT,
    ("columns", _EACH, "n_distinct_by_occurrences", _KEY_OF): _DIGITS,
    ("columns", _EACH, "n_distinct_by_occurrences", _ANY_KEY): _COUNT,
    ("columns", _EACH, "length"): _OBJECT,
    ("columns", _EACH, "length", _KEY_OF): _WORD,
    ("columns", _EACH, "length", _ANY_KEY): _MAYBE_NUMBER,
    ("columns", _EACH, "words"): _OBJECT,
    ("columns", _EACH, "words", _KEY_OF): _WORD,
    ("columns", _EACH, "words", _ANY_KEY): _MAYBE_NUMBER,
    **_relationship_rules(),
}


def _compound_rules() -> "dict[tuple[str, ...], str]":
    """The two sub-blocks of a `numbers_with_labels` column (L8).

    DERIVED FROM THE BLOCKS THEY ARE, never written out a second time.
    The numeric half of a compound column carries exactly what one
    position of a joined column carries, and its label half exactly
    what a label-publishing column carries, because both are built by
    the same code over a view of their own cells. Writing the paths out
    again would be two lists to keep in step with two others, and the
    one that fell behind would be found by a person rather than by this
    guard.

    So they are read off the rules already stated above: everything
    under `parts[]` becomes the same thing under `numbers`, and every
    label key of a column becomes the same key under `labels`.
    """
    numeric_prefix = ("columns", _EACH, "parts", _EACH)
    # EVERY KEY THE LABEL BUILDER EMITS, and it is a list because
    # `_level_details` is in another module and this table is built at
    # import. The first writing of it left out the withheld level
    # sizes, a key since pooled away (plan P4-D201), and the guard caught
    # that at once,
    # which is the arrangement working: a key added to the builder and
    # not to this list is refused by the publication check rather than
    # published unaccounted for. `test_the_compound_label_block_carries
    # _every_key_a_label_column_does` compares the two so the failure
    # is a red test and not a run-time refusal.
    label_keys = (
        "levels",
        "n_distinct",
        "n_distinct_folded",
        "n_present",
        "suppressed_levels",
        "suppressed_numbers",
        "suppressed_rows",
        "suppressed_spellings",
        "shape_forms",
        # ...and what no real run of figures opens with, beside a label half
        # whose held-back rows hold such a run (lane HB, plan P4-D442).
        "figure_openings",
        # ...and the widths of its held keys of noughts alone (plan P4-D482).
        "figure_noughts",
        # ...and the names of its held-back words (lane CODES-2, P4-D471).
        "held_back_names",
        "level_ceiling",
        "n_distinct_by_occurrences",
        "n_all_digits",
        "n_code_alphabet",
        "length",
        "words",
    )
    built: "dict[tuple[str, ...], str]" = {
        ("columns", _EACH, "numbers"): _OBJECT,
        ("columns", _EACH, "labels"): _OBJECT,
    }
    for path in _STATED_RULES:
        if path[: len(numeric_prefix)] == numeric_prefix:
            built[
                ("columns", _EACH, "numbers") + path[len(numeric_prefix):]
            ] = _STATED_RULES[path]
        elif len(path) > 2 and path[0] == "columns" and path[2] in label_keys:
            built[("columns", _EACH, "labels") + path[2:]] = _STATED_RULES[path]
    return built


def _wrapper_rules() -> "dict[tuple[str, ...], str]":
    """The block each wrapper of a SET carries (plan P4-D37).

    DERIVED FROM THE BLOCK IT IS, for the reason the compound role's
    two sub-blocks are derived rather than written out: a wrapper's
    numbers are built by the same code that builds one POSITION of a
    joined column -- `_numeric_details` over a tally of that wrapper's
    own cores -- so the paths under it are the paths under `parts[]`,
    and a second copy of them would be a second list to keep in step.

    The one written out here is the container itself, because nothing
    above states it.
    """
    numeric_prefix = ("columns", _EACH, "parts", _EACH)
    under = ("columns", _EACH, "affix_variants", _EACH, "numbers")
    built: "dict[tuple[str, ...], str]" = {under: _OBJECT}
    for path in _STATED_RULES:
        if path[: len(numeric_prefix)] == numeric_prefix:
            built[under + path[len(numeric_prefix):]] = _STATED_RULES[path]
    return built


PUBLICATION_RULES: "dict[tuple[str, ...], str]" = {
    **_STATED_RULES,
    **_compound_rules(),
    **_wrapper_rules(),
}

# For every path whose rule is `_WORD`, the WHOLE of what may stand
# there. These are this package's own vocabularies, written out where
# they are defined and read from there: a set gathered from the
# document being checked would accept whatever it found.
_STATED_WORDS: "dict[tuple[str, ...], tuple[str, ...]]" = {
    ("settings", "declaration_matching"): (taxonomy.DECLARATION_MATCHING,),
    ("settings", "declaration_publication"): (DECLARATION_PUBLICATION,),
    # Every spelling this package reads as "no value", read from
    # where they are defined. A declared value that is not one of them
    # is written nowhere IN THE SETTINGS, so a spelling of the table
    # standing here is refused before anything is serialized (contract 5
    # C5-K1). Where such a spelling IS written is four entries below,
    # under `missing_by_source`, and its rule there is `_SPELLING`.
    ("settings", "kept_values", "built_in_texts", _EACH): (
        parsing.built_in_missing_texts()
    ),
    ("settings", "kept_values", "built_in_dates", _EACH): (
        parsing.calendar_placeholders()
    ),
    ("settings", "declared_missing_values", "built_in_dates", _EACH): (
        parsing.calendar_placeholders()
    ),
    ("settings", "declared_missing_values", "built_in_texts", _EACH): (
        parsing.built_in_missing_texts()
    ),
    ("source", "encoding"): reading.ENCODINGS,
    ("source", "dialect", "columns", _EACH, "pad", "side"): dialect.PAD_SIDES,
    **{
        ("source", "dialect", "columns", _EACH, "quoting", kind): dialect.QUOTE_RULES
        for kind in dialect.CELL_CLASSES
    },
    ("source", "dialect", "delimiter"): dialect.DELIMITERS,
    ("settings", "forced_delimiter"): ("",) + dialect.DELIMITERS,
    ("source", "dialect", "escape"): dialect.ESCAPES,
    ("source", "dialect", "header_quoting"): dialect.QUOTE_RULES,
    ("source", "dialect", "header_rows_quoting"): dialect.QUOTE_RULES,
    ("source", "dialect", "line_endings", _EACH, "ending"): dialect.ENDINGS,
    ("source", "dialect", "line_endings_spread", _EACH, "ending"): dialect.ENDINGS,
    ("source", "dialect", "trailing_delimiter", "rows", _EACH, "ending"): dialect.CLOSINGS,
    # WHICH SHAPE A RUN OF LINES BEFORE THE TABLE HAS (plan P4-D80):
    # blank, a comment, or a line of text. The MARK published beside it
    # is held by `_PREAMBLE_MARK`, which refuses any letter or digit --
    # so between the two, nothing of the line's own words can stand
    # here at any floor (review item CODEX-3).
    ("source", "dialect", "preamble", _EACH, "kind"): dialect.PREAMBLE_KINDS,
    ("source", "dialect", "row_order", "collation"): dialect.COLLATIONS,
    ("source", "dialect", "row_order", "direction"): dialect.DIRECTIONS,
    ("source", "header_source"): (
        reading.HEADER_FROM_FILE,
        reading.HEADER_GENERATED,
    ),
    ("columns", _EACH, "role"): taxonomy.ROLES,
    ("columns", _EACH, "statistical_type"): taxonomy.STATISTICAL_TYPES,
    ("columns", _EACH, "quality_state"): taxonomy.QUALITY_STATES,
    ("columns", _EACH, "structural_role"): taxonomy.STRUCTURAL_ROLES,
    ("columns", _EACH, "missing_by_class", _KEY_OF): parsing.MISSING_CLASSES,
    ("columns", _EACH, "sentinel_verdicts", _EACH, "verdict"): (
        taxonomy.SENTINEL_VERDICTS
    ),
    ("columns", _EACH, "sentinel_verdicts", _EACH, "reason"): (
        taxonomy.SENTINEL_REASONS
    ),
    ("columns", _EACH, "percentiles", _KEY_OF): taxonomy.LADDER_NAMES,
    # The ninety rungs the ladder does not name (plan P4-D4.10), whose
    # words come from the same one place for the same reason.
    ("columns", _EACH, "percentiles_between", _KEY_OF): (
        taxonomy.FINER_LADDER_NAMES
    ),
    # THE SAME TWO VOCABULARIES ONE LEVEL DOWN (plan P4-D21). A joined
    # column's `parts` holds one quantitative block per position, and a
    # block there publishes the same maps a top-level one does -- so the
    # words admitted in its keys are the same words, named again because
    # this table is matched on the whole path.
    ("columns", _EACH, "parts", _EACH, "percentiles", _KEY_OF): (
        taxonomy.LADDER_NAMES
    ),
    ("columns", _EACH, "parts", _EACH, "percentiles_between", _KEY_OF): (
        taxonomy.FINER_LADDER_NAMES
    ),
    # The notation a negative wore (landing 2b.2), from the one place
    # the four names are defined, at both depths a numeric block sits.
    ("columns", _EACH, "negative_form"): parsing.NEGATIVE_FORMS,
    # ...and the three words the wide-run fact speaks with (landing
    # 2b.13, plan P4-D90), at both depths a numeric block sits.
    ("columns", _EACH, "wide_runs"): parsing.WIDE_RUNS,
    ("columns", _EACH, "parts", _EACH, "wide_runs"): parsing.WIDE_RUNS,
    # THE SIGNED-DECIMAL CENSUS NO LONGER POOLS (landing 2b.7, plan
    # P4-D65.1). `+` is its only category, so a `(withheld)` remainder
    # beside it named the category it held back; the unavailable state
    # says nothing at all and is what it reaches instead.
    ("columns", _EACH, "decimal_plus", _KEY_OF): (
        "+",
        taxonomy.UNAVAILABLE_LABEL,
    ),
    ("columns", _EACH, "parts", _EACH, "decimal_plus", _KEY_OF): (
        "+",
        taxonomy.UNAVAILABLE_LABEL,
    ),
    ("columns", _EACH, "parts", _EACH, "negative_form"): parsing.NEGATIVE_FORMS,
    # THE TWO MIXTURE CENSUSES (landing 2b.7, plan P4-D65.2), at both
    # depths a numeric block sits. Their keys are the conventions
    # themselves -- the four notations and the marks a description may
    # publish -- read from the one place each is defined, plus the two
    # words a census speaks with when it cannot name a convention.
    ("columns", _EACH, "negative_notations", _KEY_OF): _MIXTURE_NOTATIONS,
    ("columns", _EACH, "parts", _EACH, "negative_notations", _KEY_OF): (
        _MIXTURE_NOTATIONS
    ),
    ("columns", _EACH, "thousands_marks", _KEY_OF): _MIXTURE_MARKS,
    ("columns", _EACH, "parts", _EACH, "thousands_marks", _KEY_OF): (
        _MIXTURE_MARKS
    ),
    ("columns", _EACH, "date_percentiles", _KEY_OF): taxonomy.LADDER_NAMES,
    ("columns", _EACH, "clock_percentiles", _KEY_OF): taxonomy.LADDER_NAMES,
    # Read from the one place the forty forms are named, so the word a
    # producer writes and the word this guard admits cannot drift.
    ("columns", _EACH, "clock_form"): parsing.CLOCK_FORMS,
    # ...and the unit a tail is counted in (stage 3, contract DT4), a
    # closed list read from the one place it is written.
    ("columns", _EACH, "tail_unit"): parsing.TAIL_UNITS,
    # The words of a `time_grain` record (plan P4-D417), each read from the
    # one place it is written.
    ("columns", _EACH, "time_grain", "rung"): grains.RUNGS + (grains.HELD,),
    ("columns", _EACH, "time_grain", "finest"): grains.RUNGS,
    ("columns", _EACH, "time_grain", "kind"): grains.KINDS,
    ("columns", _EACH, "time_grain", "reading"): (
        parsing.DATE_FORMATS + parsing.CLOCK_FORMS + date_counts.MEMBERS
    ),
    ("columns", _EACH, "resolution_mix", _KEY_OF): parsing.DATE_FORMATS,
    # ...and a slashed stamp's words, which name its written clock beside
    # its one space (landing T1).
    ("columns", _EACH, "datetime_separators", _KEY_OF): (
        parsing.DATETIME_SEPARATORS
        + parsing.STAMP_SEPARATORS[1:]
        + (parsing.MISSING_WITHHELD,)
    ),
    # The four written-form vocabularies, read from the one place each
    # is defined (landing 2b.6), so that a word a producer writes and a
    # word this guard admits cannot drift apart.
    # No pooled word among them (plan P4-D131): a census of a handful of
    # forms cannot pool without naming what it pools.
    ("columns", _EACH, "date_field_widths", _KEY_OF): (
        parsing.FIELD_WIDTH_STYLES
    ),
    ("columns", _EACH, "month_name_styles", _KEY_OF): (
        parsing.MONTH_NAME_STYLES
    ),
    ("columns", _EACH, "quarter_marker_case", _KEY_OF): (
        parsing.QUARTER_MARKER_CASES
    ),
    ("columns", _EACH, "zulu_case", _KEY_OF): parsing.ZULU_CASES,
    ("columns", _EACH, "length", _KEY_OF): taxonomy.LENGTH_KEYS,
    ("columns", _EACH, "words", _KEY_OF): taxonomy.WORD_KEYS,
    ("columns", _EACH, "numeric_styles", _KEY_OF): (
        taxonomy.NUMERIC_STYLES + (taxonomy.SUPPRESSED_LABEL,)
    ),
    ("columns", _EACH, "parts", _EACH, "numeric_styles", _KEY_OF): (
        taxonomy.NUMERIC_STYLES + (taxonomy.SUPPRESSED_LABEL,)
    ),
    ("columns", _EACH, "format"): parsing.DATE_FORMATS,
    ("columns", _EACH, "resolution"): taxonomy.RESOLUTIONS,
    ("columns", _EACH, "time_precision"): parsing.PRECISION_ORDER,
    ("columns", _EACH, "datetimes_read_at"): taxonomy.DATETIMES_READ_AT,
}


PUBLICATION_WORDS: "dict[tuple[str, ...], tuple[str, ...]]" = {
    # The workbook block's three word-valued places (plan P4-D77). Each
    # names a CLOSED set of synthtwin's own words -- the classes a
    # workbook cell can have, the kinds of thing a number format makes
    # of a number, and the two date systems a workbook can use. None of
    # them is text out of anybody's file, which is exactly why they may
    # stand as published words at all.
    ("source", "workbook", "columns", _EACH, "cell_classes", _KEY_OF): (
        workbook.CELL_CLASSES
    ),
    ("source", "workbook", "columns", _EACH, "format_kinds", _KEY_OF): (
        workbook.FORMAT_KINDS
    ),
    ("source", "workbook", "date_system"): workbook.DATE_SYSTEMS,
    # The native block's words (lane FORMATS), each a closed list of
    # synthtwin's own or of pandas' own type names.
    ("source", "native", "format"): native.FORMATS,
    ("source", "native", "columns", _EACH, "storage"): native.STORES,
    ("source", "native", "columns", _EACH, "written_as"): native.WRITTEN,
    ("source", "native", "columns", _EACH, "pandas", "pandas_type"): native.PANDAS_TYPES,
    ("source", "native", "columns", _EACH, "pandas", "numpy_type"): native.NUMPY_TYPES,
    **_STATED_WORDS,
    # THE SAME VOCABULARIES INSIDE ONE WRAPPER'S OWN BLOCK (plan
    # P4-D37), read off a joined position's for the reason the rules
    # under it are: a wrapper's numbers are built by the code that
    # builds a position's, so the words its maps admit are the same
    # words, and a second list of them is a second thing to keep in
    # step.
    **{
        ("columns", _EACH, "affix_variants", _EACH, "numbers") + path[4:]:
            _STATED_WORDS[path]
        for path in _STATED_WORDS
        if path[:4] == ("columns", _EACH, "parts", _EACH)
    },
    # THE SAME VOCABULARIES INSIDE A COMPOUND COLUMN'S TWO HALVES, read
    # off the ones above for the same reason the rules are: a style map
    # inside `numbers` may hold exactly what a style map holds anywhere
    # else, and a second list of the same words is a second thing to
    # keep in step.
    **{
        ("columns", _EACH, "numbers") + path[4:]: _STATED_WORDS[path]
        for path in _STATED_WORDS
        if path[:4] == ("columns", _EACH, "parts", _EACH)
    },
    **{
        ("columns", _EACH, "labels") + path[2:]: _STATED_WORDS[path]
        for path in _STATED_WORDS
        if len(path) > 2
        and path[0] == "columns"
        and path[2] in ("levels", "shape_forms", "length", "words")
    },
    **{
        ("columns", _EACH, "numbers") + path[2:]: _STATED_WORDS[path]
        for path in _STATED_WORDS
        if len(path) > 2
        and path[0] == "columns"
        and path[2] in (
            "numeric_styles",
            "fraction_widths",
            "pad_widths",
            "field_widths",
            "value_histogram",
            "percentiles",
            "percentiles_between",
            "empty_bins",
            "resolution_mix",
        )
    },
}


def _named(path: "tuple[str, ...]") -> str:
    """One path, in a form a person can be shown safely.

    It is built from the RULE's own steps -- key names this module
    wrote, plus `[]` for a list and `{}` for a mapping whose keys the
    data decides -- and never from the document's own keys. A mapping
    key can be a spelling of the real table, and a refusal that named
    one would publish, to a screen, the value it is refusing to publish
    to a file.
    """
    shown = ""
    for step in path:
        if step == _EACH:
            shown = shown + "[]"
        elif step in (_ANY_KEY, _KEY_OF):
            shown = shown + "{}"
        elif shown:
            shown = shown + "." + step
        else:
            shown = step
    if not shown:
        return "the whole description"
    return shown


def _refuse(path: "tuple[str, ...]") -> "errors.ProfileError":
    """The one refusal this guard makes, naming the place and no value."""
    return errors.ProfileError(errors.publication_guard_stopped(_named(path)))


def _is_count(value: object) -> bool:
    """A whole number of zero or more, and not a yes/no."""
    if isinstance(value, bool):
        return False
    return isinstance(value, int) and value >= 0


def _is_number(value: object) -> bool:
    """A number, whole or not, and not a yes/no."""
    if isinstance(value, bool):
        return False
    return isinstance(value, (int, float))


def _is_offset(value: object) -> bool:
    """`Z`, `(none)`, the withheld pool, or a signed clock offset.

    `Z` IS ONE OF THEM, and leaving it out made this guard refuse every
    table whose times are stamped in UTC (found while repairing review
    item P3-V5-F1; plan amendment A-P3-16 clause 4). The producer
    writes `Z` for a cell ending in one -- `parsing.split_offset` hands
    it back unchanged -- and the strict loader accepts it wherever an
    offset may stand (`contract._is_an_offset`), so a column of
    `2024-03-17T09:00:00Z` reached this guard with `earliest_utc_offset`
    set to `Z`, was refused as something the publication rules could not
    account for, and the person was told to report a fault in synthtwin
    and given no way to describe their table. The two writings of "what
    an offset is" now accept the same strings, and a test compares them
    string by string rather than trusting this sentence.
    """
    if not isinstance(value, str):
        return False
    if value in ("Z", _NO_OFFSET, parsing.MISSING_WITHHELD):
        return True
    if len(value) != 6 or value[0:1] not in ("+", "-") or value[3:4] != ":":
        return False
    if not parsing.is_digit_text(value[1:3]) or not parsing.is_digit_text(
        value[4:6]
    ):
        return False
    # AND THE RANGE, because the loader checks it (review item P2-C1-F6,
    # and the same disagreement `Z` was on the other side of). No zone
    # stands further than fourteen hours from UTC and no zone's minute
    # field reaches sixty. A guard looser here than the loader is a
    # guard that lets this package write a description it then refuses
    # to read.
    hours = int(value[1:3])
    minutes = int(value[4:6])
    if hours > 14 or minutes > 59:
        return False
    return not (hours == 14 and minutes != 0)


def _is_moment(value: object) -> bool:
    """Canonical date, datetime or quarter text, or a written clock time.

    A CLOCK TIME IN ANY OF ITS FORMS (landing T1): `2:05 PM` carries
    letters and a point the canonical alphabet has not, so it is asked of
    the one clock reader, which accepts figures, colons and the marker
    words and nothing else.
    """
    if not isinstance(value, str) or not value:
        return False
    for character in value:
        if character not in _DATETIME_CHARACTERS:
            # ...or a clock written as figures with a fraction (lane TR,
            # plan P4-D473), `074512.000000`: its point is not canonical.
            return (
                parsing.clock_form(value) is not None
                or parsing.clock_figure_form(value) is not None
            )
    return True


def _is_sentinel(value: object) -> bool:
    """One stand-in this package knows -- a number or a day -- or the pool.

    BOTH KINDS OF CANDIDATE, and the guard is what makes that a closed
    question: a verdict names a value of the table, so the only values
    it may name are this package's own constants, and a spelling
    outside them is refused before anything is written (plan amendment
    A-P4-1 item 3).
    """
    if not isinstance(value, str):
        return False
    if value == taxonomy.SUPPRESSED_LABEL:
        return True
    for candidate in parsing.NUMERIC_SENTINELS:
        if value == f"{candidate:g}":
            return True
    for day in parsing.calendar_placeholders():
        if value == day:
            return True
    return False


def _is_sentence(value: object) -> bool:
    """Whether this leaf is a sentence this package can write again.

    THE ONE CHECK THAT IS NOT A PATTERN. The leaf must be a
    `taxonomy.Note`, carrying the form it was built from and the
    arguments that filled it; every argument must be one the grammar
    enumerates; and `taxonomy.rendered` must write the identical text
    from those two. A sentence with a value of the table formatted into
    it fails at the first of those -- formatting a Note produces a plain
    string, which carries no form -- and could not pass the last one
    either, because no enumerated argument spells a value of a table.

    WHAT IT DELIBERATELY DOES NOT CHECK: which form stands at which
    sentence path. A column's remark carrying the header verdict's
    words would be odd, and it would be caught by the tests that read
    what a profile says; it would not publish anything, because no form
    of the grammar can carry a value of the table. This check is about
    where text CAME FROM, and that is the whole of what it claims.
    """
    if not isinstance(value, taxonomy.Note):
        return False
    if value.form not in taxonomy.NOTE_ARITY:
        return False
    if len(value.arguments) != taxonomy.NOTE_ARITY[value.form]:
        return False
    for place, argument in enumerate(value.arguments):
        if taxonomy.takes_a_bound_affix(value.form, place):
            # The fourth argument class: an affix spelling, admitted at
            # exactly the positions of exactly the forms that same
            # table names, so this guard and the builder cannot drift
            # apart. What it does NOT check here is the positional
            # identity with the block's own two keys -- residual
            # R-P4-15 -- because this walk reaches a leaf without the
            # block that owns it. `_affix_notes_are_bound` checks that
            # over the whole document, where the block IS in hand, and
            # it is what makes this position safe.
            if not isinstance(argument, str):
                return False
            continue
        if not taxonomy.argument_is_enumerated(argument):
            return False
    return f"{value}" == taxonomy.rendered(value.form, value.arguments)


# WHERE A KEY IS THE TABLE'S TEXT AND CARRIES NO FIRST-PARTY MEANING
# (contract 5 C5-N5; plan amendment A-P3-32, review item P3-V9-F2). The
# pooled-remainder rule below skips those mappings, because a key
# reading `(withheld)` in one of them means that cells of the table held
# exactly those ten characters.
#
# The list of them is `canonical.TABLE_TEXT_KEY_SPACES` and is read from
# there rather than written again here, so that this guard and the
# loader's own walk cannot answer the same question two ways. The
# version this replaces named `missing_by_source` alone and left
# `levels[].variants` out, so a table with twelve rows whose categorical
# label reads `(withheld)`, described at `--smallest-group 1`, stopped
# the profiler with an internal fault -- against a table that is
# perfectly ordinary and a label the format is required to publish.


def _remainder_is_published(
    value: object, key: str, path: "tuple[str, ...]", context: _Publication
) -> bool:
    """Whether a pooled remainder may stand here at this floor.

    THE POOLED REMAINDER IS FOUND BY THE WORD IT STANDS UNDER, NOT BY
    THE FIELD IT SITS IN (amendment A-P3-22, review item P3-V7-F6).
    `(withheld)` is the format's one word for "held back" (contract
    section 14), and the range the floor holds back is empty at a floor
    of one -- so a positive count standing under that word anywhere in
    the document is a document the strict loader's invariant S13
    refuses, and the guard that decides what may be WRITTEN has to say
    the same thing at the same reach.

    Amendment A-P3-16 clause 2 gave this rule to the three fields whose
    own kind is `_FLOORED_ENTRY` and left the fourth -- a
    `missing_by_class` count, whose kind is the generic `_COUNT` --
    accepting any number at any floor. That is the shape of the defect
    A-P3-16 clause 1 was written to stop: each field WAS checked where
    it was written, and one check did not know about the remainder. This
    runs before the leaf's own kind is consulted and independently of
    it, so a fifth field putting a count under that word is covered on
    the commit that adds it.

    WHERE THE TABLE DECIDES THE KEY, THE WORD IS NOT A WORD (contract 5
    C5-N5, C5-S13; plan amendment A-P3-32). The rule reads a key as this
    package's own word, which is sound while the mapping draws its keys
    from a first-party vocabulary. Two mappings do not: `missing_by_source`
    keys itself on the spelling that made a cell absent, and
    `levels[].variants` on the spelling some rows wrote a label with, so
    a table whose cells literally read `(withheld)` publishes that key
    with the count those cells came to. Refusing it would refuse the
    very description version 5 exists to make writable. Which mappings
    those are is `canonical.TABLE_TEXT_KEY_SPACES`, and reading it from
    there is what keeps this guard and `contract._held_back_in` from
    answering one question two ways -- which they did, both naming
    `missing_by_source` alone, until review item P3-V9-F2.

    The remainder that used to stand inside `missing_by_source` is
    `n_missing_withheld`, which this guard holds to the same rule under
    its own kind, `_HELD_BACK`.

    Guarantees:

    - Inputs: the leaf, the mapping key it stands under (empty when it
      stands under none), the path the leaf stands at, and what the
      guard knows about the document.
    - Determinism: the answer depends only on those four.
    - Errors raised: none.
    - Boundary: nothing is opened and no value is written anywhere.
      A leaf that is not a count under that word is left to its own
      rule, which is why this answers True for everything else.
    """
    # The path handed here is the LEAF's, so the mapping it stands in is
    # one step up. A leaf that stands under no mapping key at all is at
    # a path no key space names, and answers False there.
    if canonical.keys_are_the_tables_own_text(path[: len(path) - 1]):
        return True
    if key != parsing.MISSING_WITHHELD:
        return True
    if isinstance(value, bool) or not isinstance(value, int):
        return True
    if canonical.pools_at_any_floor(path[: len(path) - 1]):
        # The censuses that pool what `parsing.census_floor` cannot
        # name, at every floor (plans P4-D220, P4-D221): the leaf's own kind,
        # `_POOLED_CENSUS_ENTRY`, decides.
        return True
    return value <= 0 or context.floor > 1


def _leaf_is_published(
    kind: str,
    value: object,
    key: str,
    path: "tuple[str, ...]",
    context: _Publication,
) -> bool:
    """Whether one leaf is something this profile may publish.

    Guarantees:

    - Inputs: the rule for the leaf's own path, the leaf, the mapping
      key it stands under (empty when it does not stand under one), the
      path itself, and what the guard knows about the document.
    - Determinism: the answer depends only on those five.
    - Errors raised: none. An unknown kind is False, so a rule nobody
      taught this function refuses the leaf rather than passing it.
    - Boundary: nothing is opened and no value is written anywhere.
    """
    if not _remainder_is_published(value, key, path, context):
        return False
    if kind == _COUNT:
        return _is_count(value)
    if kind == _FLOOR_COUNT:
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        return value >= context.floor
    if kind == _FLOORED_ENTRY:
        # A count published under a key of its own has to have cleared
        # the small-cell floor; the pooled remainder is the one entry
        # that may be smaller, because it names nothing.
        #
        # AND AT A FLOOR OF ONE THERE IS NO REMAINDER (owner ruling
        # 2026-08-14, plan amendments A-P3-11 and A-P3-16; contract
        # invariant S13). The remainder holds what fell BELOW the floor,
        # and below one there is nothing, so this guard would otherwise
        # write out a document its own loader refuses.
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        if key == parsing.MISSING_WITHHELD:
            return value >= 1 and context.floor > 1
        return value >= context.floor
    if kind == _POOLED_CENSUS_ENTRY:
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        if key == parsing.MISSING_WITHHELD:
            return value >= 1
        return value >= parsing.census_floor(context.floor)
    if kind == _DISCLOSED_ENTRY:
        # A census of written forms (plan P4-D131): never one, never a
        # pool. `parsing.census_floor` is the producer's and the
        # loader's own number, so all three say it at the same reach.
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        if key == parsing.MISSING_WITHHELD:
            return False
        return value >= parsing.census_floor(context.floor)
    if kind == _MIXTURE_ENTRY:
        # A CENSUS OF LANDING 2b.7, WHOSE FLOOR IS NEVER ONE (plan
        # P4-D65.1, P4-D65.2; owner twin definition, clause 3). A
        # published count of one names an individual whatever the
        # settings floor says, so every count here clears
        # `taxonomy._census_floor` -- two, or the settings floor where
        # that is larger -- and the guard that decides what may be
        # WRITTEN says it at the same reach the loader does.
        #
        # THE UNAVAILABLE STATE CARRIES NOUGHT AND ONLY NOUGHT. It is
        # the state a census reaches where it cannot speak safely, and
        # a number beside it would be the disclosure it exists to
        # close.
        #
        # THE POOLED REMAINDER IS A REMAINDER STILL: it clears the same
        # floor, because these censuses pool only what is left after
        # every named convention, and it may not stand at all at a
        # settings floor of one, where the range below the floor is
        # empty and invariant S13 refuses anything held back.
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        if key == taxonomy.UNAVAILABLE_LABEL:
            return value == 0
        least = taxonomy.census_floor_of(context.floor)
        if key == taxonomy.SUPPRESSED_LABEL:
            return value >= least and context.floor > 1
        return value >= least
    if kind == _HELD_BACK:
        # A tally of what the floor took out of sight: how many labels,
        # how many rows they cover, how many stand-in numbers were too
        # rare to name, how many absent cells wore a spelling too few
        # rows shared. Same rule, said about a count that carries no key
        # of its own.
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        if value < 0:
            return False
        return value == 0 or context.floor > 1
    if kind == _POOLED_SCALE_COUNT:
        # Nought, or a group at the disclosure line. Whether the cells
        # LEFT OVER once this pool is taken off the column's numbers
        # are a group too needs that total beside it, so that half is
        # invariant B4d and is checked with the invariants.
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        return value == 0 or value >= parsing.census_floor(context.floor)
    if kind == _FORM_COUNT:
        # A count of the file's own records or lines (plan P4-D317):
        # nought, or at the census line wherever the floor is asked.
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        if value < 0:
            return False
        return (
            value == 0
            or context.floor <= 1
            or value >= parsing.census_floor(context.floor)
        )
    if kind == _ZERO_OR_AT_THE_FLOOR:
        # A named group, or nothing at all. There is no third answer:
        # a group the floor held back is not written here, it is added
        # to the pooled remainder beside it (contract 5 C5-N4).
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        return value == 0 or value >= context.floor
    if kind == _BOTH_SIDES_OR_UNAVAILABLE:
        # A count, or nothing at all written `null`. The SHAPE is all
        # this guard can ask: whether the group and its complement both
        # reach the floor needs the column's parsed count beside it, so
        # the rule itself is invariant D15. What is refused here is the
        # thing that made the count disclosive in the first place -- a
        # nought standing for "not published" -- because nought is no
        # longer a value this field takes at all.
        if value is None:
            return True
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        return value >= parsing.MIDNIGHT_DISCLOSURE_FLOOR
    if kind == _STAND_IN_NUMBER:
        # One of the three stand-in numbers this package publishes, and
        # no other number. A number of the table cannot stand here.
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False
        for candidate in parsing.NUMERIC_SENTINELS:
            if value == candidate:
                return True
        return False
    if kind == _BELOW_THE_FLOOR:
        # One group size the floor held back, whether it stands as a
        # count or -- for a multiplicity map -- as a key written in
        # figures. The permitted range is 1 up to the floor, which at a
        # floor of one is empty.
        if isinstance(value, str):
            if not value or not parsing.is_digit_text(value):
                return False
            return 1 <= int(value) < context.floor
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        return 1 <= value < context.floor
    if kind == _NUMBER:
        return _is_number(value)
    if kind == _MAYBE_NUMBER:
        return value is None or _is_number(value)
    if kind == _MAYBE_MOMENT:
        return value is None or _is_moment(value)
    if kind == _FLAG:
        return isinstance(value, bool)
    if kind in (_CLOSING, _CLOSING_RUNS):
        return isinstance(value, bool) or value == dialect.CLOSING_QUOTED
    if kind == _NOTHING:
        return value is None
    if kind == _SENTENCE:
        return _is_sentence(value)
    if kind == _HEADER_TEXT:
        # A header cell or a metadata cell exactly as the file writes it:
        # the schema text the twin's header lines have to carry, which a
        # blank or repeated name makes empty or a repeat (plan P4-D86). A
        # name may hold a line break, written quoted, like any other name.
        return isinstance(value, str)
    if kind == _BLANK_LINE:
        return isinstance(value, str) and all(
            character in " \t" for character in value
        )
    if kind == _PREAMBLE_MARK:
        # THE ONLY PART OF A LINE BEFORE THE TABLE THAT REACHES A
        # DESCRIPTION, and it may hold no letter and no digit at any
        # floor (plan P4-D80). The rule this replaced asked the floor
        # first and handed the WHOLE line over at a floor of one, which
        # is the default: review item CODEX-3 measured a person's name
        # travelling through it into the description and into the twin.
        # A floor is a rule about groups of rows and was never a
        # defence for a line of prose, so no floor is consulted here.
        if not isinstance(value, str) or "\r" in value or "\n" in value:
            return False
        # AND NO CHARACTER THAT WOULD STOP THE TWIN BEING A FILE (plan
        # P4-D83). A quote character in a mark makes the twin's first
        # line an unterminated quoted field. The delimiter is the
        # other such character and this guard has no form in hand, so
        # the loader -- which does -- holds that half (FD11).
        if dialect.mark_breaks_a_line(value, ""):
            return False
        return dialect.holds_no_letter_or_digit(value)
    if kind == _TABLE_NAME:
        # A column's name IS text of the real table, and the matrix
        # authorizes it: the twin's header row has to carry it. So this
        # rule asks only that it is text with something in it, and the
        # guard makes no attempt to tell a name from a cell -- nothing
        # could, and the profile is required to publish this one.
        return isinstance(value, str) and bool(parsing.trimmed(value))
    if kind == _KNOWN_NAME:
        return isinstance(value, str) and value in context.names
    if kind == _NATIVE_LABEL:
        return value is None or native.label_published(value)
    if kind == _NATIVE_COLUMN_LABEL:
        return value is None or native.column_label_published(value)
    if kind == _NATIVE_NAME:
        return value is None or native.name_published(value, 64)
    if kind == _NATIVE_FORMAT:
        return value is None or any(
            native.format_published(value, system) for system in native.FORMATS
        )
    if kind == _NATIVE_CODE:
        if value is None:
            return True
        if not isinstance(value, str):
            return False
        return native.number_spelled(value) or native.label_published(value)
    if kind == _NATIVE_FLAG:
        return value is None or isinstance(value, bool)
    if kind == _NATIVE_MEASURE:
        return value is None or value in native.MEASURES
    if kind == _NATIVE_ZONE:
        return value is None or native.zone_published(value)
    if kind == _NATIVE_EMPTY_TEXT:
        return value is None or native.empty_text_published(value)
    if kind == _CENTURY_PART:
        if isinstance(value, str):
            return value in context.names
        return (
            not isinstance(value, bool)
            and isinstance(value, int)
            and value in parsing.CENTURY_WINDOW_YEARS
        )
    if kind == _KNOWN_NAME_OR_THE_TABLE:
        # A note about the whole table names no column, and the empty
        # spelling is how it says so (plan P4-D341). Every other value
        # is held to the columns this table has, exactly as
        # `_KNOWN_NAME` holds them.
        if value == "":
            return True
        return isinstance(value, str) and value in context.names
    if kind == _SPELLING:
        # A value of the real table, at one of the few paths the
        # disposition matrix authorizes: a published label, one of its
        # spellings, or a spelling counted as "no value". What holds
        # each of them to the floor is the count beside it, checked
        # under its own rule.
        return isinstance(value, str) and bool(value)
    if kind == _AFFIX:
        # Any text, the empty spelling included. What bounds this is
        # not the shape of the value but the floor on `n_affixed`,
        # which the role's own detection rule reads BEFORE the role is
        # given: a pair too rare to publish sends the column to the
        # next rule instead.
        return isinstance(value, str)
    if kind == _SHEET_VALUE_CLASS:
        return value is None or (
            isinstance(value, str) and value in dialect.SHEET_VALUE_CLASSES
        )
    if kind == _SHEET_FORMAT_CODE:
        # The producer's own question, asked rather than restated.
        return isinstance(value, str) and dialect.sheet_format_code_publishable(value)
    if kind == _SHEET_NAME:
        # The grammar is the producer's own, asked here rather than
        # restated: a name this document publishes must be one
        # `dialect.sheet_name_published` would have published itself.
        if value is None:
            return True
        if not isinstance(value, str):
            return False
        return dialect.sheet_name_published(value) == value
    if kind == _DIGITS:
        return isinstance(value, str) and parsing.is_digit_text(value)
    if kind == _VALUE_SPELLING:
        return isinstance(value, str) and parsing.is_few_value_spelling(value)
    if kind == _WIDTH:
        if value == taxonomy.SUPPRESSED_LABEL:
            return True
        if not isinstance(value, str) or not parsing.is_digit_text(value):
            return False
        return value == "0" or value[:1] != "0"
    if kind == _BIN:
        # A BIN NUMBER IS NOT A WIDTH, and it has its own name here so
        # a refusal says which kind of key it met. The grammar is the
        # same canonical decimal one, and the range is fixed by the
        # method rather than by the column.
        if value == taxonomy.SUPPRESSED_LABEL:
            return True
        if not isinstance(value, str) or not parsing.is_digit_text(value):
            return False
        if value != "0" and value[:1] == "0":
            return False
        return 0 <= int(value) < parsing.HISTOGRAM_BINS
    if kind == _BIN_INDEX:
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        return 0 <= value < parsing.HISTOGRAM_BINS
    if kind == _WEEKDAY:
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        return 0 <= value < calendar_rules.WEEKDAYS
    if kind == _WEEKDAY_COUNT:
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        # WC2, ASKED OF THE ONE STATEMENT every census shares (plan P4-D364).
        return calendar_rules.calendar_floor_ok(
            value, parsing.census_floor(context.floor)
        )
    # THE LANDINGS' ANCHORS (plan P4-D364): each landing of stage 3b adds
    # the checks of its kinds below its own line.
    # anchor 3b-D1 (P4-D365)
    # anchor 3b-D0 (P4-D366)
    # anchor 3b-D2 (P4-D367)
    # anchor 3b-D3 (P4-D368)
    if kind == _MONTH_DAY:
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        return 1 <= value <= calendar_rules.MONTH_DAY_BINS
    if kind == _MONTH_DAY_COUNT:
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        # DM2, asked of the one statement every census shares.
        return calendar_rules.calendar_floor_ok(
            value, parsing.census_floor(context.floor)
        )
    # anchor 3b-D4 (P4-D369)
    if kind == _HEAVY_DATE:
        if not isinstance(value, str):
            return False
        read = parsing.parse_datetime(value, "iso-date")
        return read is not None and read[0] == value
    if kind == _HEAVY_COUNT:
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        # HD2: never nought, and at least the heavy line.
        return value >= calendar_rules.heavy_line(context.floor)
    # anchor 3b-T1 (P4-D370)
    # anchor 3b-T2 (P4-D371)
    if kind == _HOUR:
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        return 0 <= value < calendar_clock.HOURS
    if kind == _HOUR_COUNT:
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        # HC2, ASKED OF THE ONE STATEMENT every census shares (plan P4-D364).
        return calendar_rules.calendar_floor_ok(
            value, parsing.census_floor(context.floor)
        )
    # anchor 3b-T3 (P4-D372)
    if kind == _CLOCK_FIELD_VALUE:
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        return 0 <= value < calendar_clock.FIELD_VALUES
    if kind == _CLOCK_FIELD_COUNT:
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        return calendar_rules.calendar_floor_ok(
            value, parsing.census_floor(context.floor)
        )
    if kind == _CLOCK_FIELD_HEAP:
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        return value >= parsing.census_floor(context.floor)
    # anchor 3b-C1 (P4-D373)
    if kind == _TEN_MINUTE_BIN:
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        return 0 <= value < calendar_clock.clock_bin_count(parsing.CLOCK_HH_MM)
    if kind == _CLOCK_COUNT:
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        return calendar_rules.calendar_floor_ok(
            value, parsing.census_floor(context.floor)
        )
    if kind == _CLOCK_LINE_COUNT:
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        return value >= parsing.census_floor(context.floor)
    if kind == _CLOCK_VALUE:
        # ...in any form, a clock written as figures among them (plan P4-D473).
        return isinstance(value, str) and (
            parsing.clock_form(value) is not None
            or parsing.clock_figure_form(value) is not None
        )
    if kind == _CLOCK_STEP:
        if value is None:
            return True
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        return 1 <= value and calendar_clock.clock_day(parsing.CLOCK_HH_MM) % value == 0
    # anchor 3b-C2 (P4-D374)
    # anchor 3b-G1 (P4-D375)
    # anchor 3b-G3 (P4-D376)
    # anchor 3b-G2 (P4-D377)
    # anchor 3b-7 (P4-D378)
    # anchor 3b-J (P4-D379)
    # anchor 3b-R2a (P4-D383)
    # anchor 3b-R2b (P4-D383)
    # anchor 3b-R2c (P4-D383)
    # anchor 3b-R4 (P4-D384)
    if kind == _COUNTED_PART:
        if not isinstance(value, str):
            return False
        return value in context.names or value in date_counts.MEMBERS
    if kind == _COUNT_MARK:
        return isinstance(value, str) and value in date_counts.MARKS
    if kind == _GRAIN_SPAN_PART:
        return isinstance(value, str) and (value in grains.RUNGS or _is_moment(value))
    if kind == _OFFSET_RULE:
        return isinstance(value, str) and offset_rules.parsed_rule(value) is not None
    if kind == _COUNT_SIGNIFICANT:
        return value is None or (
            not isinstance(value, bool) and isinstance(value, int) and value in (15, 17)
        )
    if kind == _CONTACT_WORD:
        # FIGURES AFTER THE POINT OF AN 1840 DAY, AS WRITTEN, or the word for
        # none: a contact number, which the census beside it counts.
        if not isinstance(value, str):
            return False
        if value == date_counts.NO_CONTACT:
            return True
        return 0 < len(value) <= 9 and parsing.is_digit_text(value)
    if kind == _TAIL_PERCENT:
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        return 1 <= value <= 99
    if kind == _EMPTY_BIN:
        # A BIN NUMBER, WRITTEN AS A NUMBER AND NOT AS A KEY. It stands
        # in a list rather than at the key of a mapping, so the
        # canonical-decimal question `_BIN` asks does not arise: there
        # is one way to write a whole number in this format. `True` is
        # an integer to Python and is not one here, which is the check
        # every other whole-number rule in this file makes as well.
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        return 0 <= value < parsing.HISTOGRAM_BINS
    if kind == _SHAPE_FORM:
        return _is_shape_form(value)
    if kind == _PLACE_CHARACTERS:
        return isinstance(value, str) and parsing.is_a_place_list(value)
    if kind == _STAND_IN_START:
        return isinstance(value, str) and (
            value == "" or parsing.is_a_stand_in_start(value)
        )
    if kind == _FLAG_TRUE:
        return value is True
    if kind == _PREFIX_SCOPE:
        if value == parsing.PREFIX_OF_THE_COLUMN:
            return True
        return value != taxonomy.SUPPRESSED_LABEL and _is_layout_form(value)
    if kind == _LITERAL_PREFIX:
        return isinstance(value, str) and parsing.is_a_literal_prefix(value)
    if kind == _FIGURE_WIDTH:
        return isinstance(value, str) and parsing.is_a_figure_width(value)
    if kind == _FIGURE_OPENING:
        return _is_figure_opening(value)
    if kind == _EXCLUSION_SCOPE:
        if value == parsing.EXCLUSION_SPILL:
            return True
        return value != taxonomy.SUPPRESSED_LABEL and _is_layout_form(value)
    if kind == _LAYOUT_EXCLUSION:
        if isinstance(value, list):
            # SEVERAL SPELLINGS OF ONE LAYOUT'S BLOCK (plan P4-D432), each
            # an exclusion, two to `parsing.EXCLUSIONS_AT_MOST`.
            if not 2 <= len(value) <= parsing.EXCLUSIONS_AT_MOST:
                return False
            for each in value:
                if not isinstance(each, str) or not parsing.is_a_layout_exclusion(each):
                    return False
            return True
        return isinstance(value, str) and (
            parsing.is_a_layout_exclusion(value)
            or _is_layout_form(value)
            or parsing.is_a_spill_layout(value)
        )
    if kind == _LAYOUT_FORM:
        return _is_layout_form(value)
    if kind == _MOMENT_TEXT:
        return _is_moment(value)
    if kind == _OFFSET:
        return _is_offset(value)
    if kind == _SENTINEL:
        return _is_sentinel(value)
    if kind == _VERSION:
        return isinstance(value, str) and value == _version()
    return False


def _is_shape_form(value: object) -> bool:
    """Whether one key of the form census carries no value of the table.

    THIS IS THE GUARD THAT MAKES THE CENSUS PUBLISHABLE, and it asks
    the ONE definition rather than restating it. It restated it, and
    the restatement drifted: this accepted `AAAA` and `9999`, which the
    producer cannot write and no cell can wear, so a document carrying
    one passed here and missed its own census at every recount (review
    round 2 finding 2).

    What `parsing.is_a_written_form` guarantees is what this guard
    needs: a key is spelled from two placeholders and a closed list of
    marks, and neither placeholder is a letter, a digit or a mark -- so
    a cell carrying one has no form, and therefore NO CELL THAT HAS A
    FORM CAN BE SPELLED THE SAME AS ANY KEY. That is checkable here,
    where "the producer would not do that" is not.
    """
    if value == taxonomy.SUPPRESSED_LABEL:
        return True
    if not isinstance(value, str):
        return False
    return parsing.is_a_written_form(value)


def _is_figure_opening(value: object) -> bool:
    """Whether a value could be an opening of `figure_openings` (plan P4-D442): nothing, or one to four figures, the first never a nought."""
    return isinstance(value, str) and parsing.is_a_figure_opening(
        parsing.FIGURE_OPENING_DEPTH + 1, value
    )


def _is_layout_form(value: object) -> bool:
    """Whether one key of the layout census carries no record number.

    THE SAME GUARD THE FORM CENSUS HAS, asking the ONE definition
    rather than restating it. What `parsing.is_a_layout_form`
    guarantees is what this needs: a key is spelled from six
    placeholders and a closed list of marks, and a cell carrying any
    placeholder -- or made of marks alone -- has no layout at all. So
    no cell that HAS a layout can be spelled the same as any key, in
    any column, in any table, and admitting a key can never admit a
    value.
    """
    if value == taxonomy.SUPPRESSED_LABEL:
        return True
    if not isinstance(value, str):
        return False
    return parsing.is_a_layout_form(value)


def _places_are_published(places: "list[object]", floor: int) -> bool:
    """Whether a list of blank places is one the producer could write.

    Asked of the producer's own rule, `dialect.blank_places_broken`, so
    the guard and the loader say it at the same reach (plan P4-D317).
    Each place has already been held to its own rules by the walk; one
    missing a key of its three is refused here, because the rule cannot
    be asked of it.
    """
    read: "list[dialect.BlankPlace]" = []
    for place in places:
        if not isinstance(place, dict):
            return False
        after = place["after"] if "after" in place else None
        lines = place["lines"] if "lines" in place else None
        text = place["text"] if "text" in place else None
        if (
            not isinstance(after, int)
            or not isinstance(lines, int)
            or not isinstance(text, str)
        ):
            return False
        read += [dialect.BlankPlace(after=after, lines=lines, text=text)]
    return not dialect.blank_places_broken(read, floor)


# The two places a column's date FORMAT is published, where a layout of
# the closed grammar stands beside the named members (landing R2a, plan
# P4-D383; contract rule LY1).
_LAYOUT_WORD_PATHS = (
    ("columns", _EACH, "format"),
    ("columns", _EACH, "resolution_mix", _KEY_OF),
    # ...and the reading of a `time_grain` record (plan P4-D417), which
    # names the column's own date member.
    ("columns", _EACH, "time_grain", "reading"),
)


def _check_word(
    value: object, path: "tuple[str, ...]"
) -> None:
    """Refuse anything but a word of the vocabulary this path allows.

    A date format may also be a layout the closed grammar makes (landing
    R2a): built of this package's own fields and marks and admitted only
    where `parsing.is_layout_format` says the grammar's productions make
    it, so no text out of a cell can stand there.
    """
    if path not in PUBLICATION_WORDS:
        raise _refuse(path)
    if (
        path in _LAYOUT_WORD_PATHS
        and isinstance(value, str)
        and parsing.is_layout_format(value)
    ):
        return
    # -- 3b.R2c (P4-D383): A PARTIAL FORM a census of forms counts, built of
    # the same closed tables and the unknown markers alone.
    if (
        path == _LAYOUT_WORD_PATHS[1]
        and isinstance(value, str)
        and parsing.is_partial_layout_format(value)
    ):
        return
    if not isinstance(value, str) or value not in PUBLICATION_WORDS[path]:
        raise _refuse(path)


def _check_published(
    node: object, path: "tuple[str, ...]", key: str, context: _Publication
) -> None:
    """Walk one part of the finished document and refuse the rest.

    Guarantees:

    - Inputs: a node of the document, the path it stands at, the
      mapping key it stands under, and the guard's context.
    - Determinism: the answer depends only on the document; mappings are
      walked in sorted key order.
    - Errors raised: ProfileError, naming the path and never a value,
      for a path with no rule, a container of the wrong shape, a
      mapping key with no rule, and a leaf its rule does not allow.
    - Boundary: nothing is opened, nothing is written, and no value of
      the table reaches the refusal.
    """
    if path not in PUBLICATION_RULES:
        raise _refuse(path)
    kind = PUBLICATION_RULES[path]
    if kind == _MAYBE_OBJECT:
        if node is None:
            return
        kind = _OBJECT
    if kind == _MAYBE_ARRAY:
        if node is None:
            return
        kind = _ARRAY
    if kind == _OBJECT:
        if not isinstance(node, dict):
            raise _refuse(path)
        free = path + (_ANY_KEY,)
        # Every key is text before any of them is sorted: sorting a
        # mapping whose keys are of two kinds raises where a refusal
        # belongs, and a key that is not text is one this document has
        # no rule for either way.
        keys: list[str] = []
        for name in node:
            if not isinstance(name, str):
                raise _refuse(path)
            keys += [name]
        for name in sorted(keys):
            if free in PUBLICATION_RULES:
                # A mapping whose KEYS the data decides. The key is a
                # leaf of its own and is checked as one, so a spelling
                # can stand there only where a rule says a spelling may.
                where = path + (_KEY_OF,)
                if PUBLICATION_RULES[where] == _WORD:
                    _check_word(name, where)
                elif not _leaf_is_published(
                    PUBLICATION_RULES[where], name, name, where, context
                ):
                    raise _refuse(where)
                _check_published(node[name], free, name, context)
                continue
            named = path + (name,)
            if named not in PUBLICATION_RULES:
                raise _refuse(named)
            _check_published(node[name], named, name, context)
        # A header ending in its delimiter over records all closed `""`
        # is read back as one column more (Codex's review of landing R6,
        # item 3; the loader's FD10).
        if path == _TRAILING_BLOCK and "rows" in node and "header" in node:
            rows_side = node["rows"]
            header_side = node["header"]
            if rows_side == dialect.CLOSING_QUOTED and (
                header_side is True or header_side == dialect.CLOSING_QUOTED
            ):
                raise _refuse(path)
        return
    if kind == _ARRAY:
        if not isinstance(node, list):
            raise _refuse(path)
        for item in node:
            _check_published(item, path + (_EACH,), "", context)
        return
    if kind == _CLOSING_RUNS and isinstance(node, list):
        runs: "list[dialect.EndingRun]" = []
        for item in node:
            _check_published(item, path + (_EACH,), "", context)
            runs += [dialect.EndingRun(ending=item["ending"], lines=item["lines"])]
        kinds = set([run.ending for run in runs])
        if (
            len(kinds) < 2
            or dialect.endings_broken(tuple(runs), context.floor, 0)
            # ...and as the twin's closings are measured back (Codex's
            # review of landing R6, item 4): no run beside one of the
            # same closing, none past the cap on runs.
            or dialect.closing_runs_broken(tuple(runs))
        ):
            raise _refuse(path)
        return
    if kind == _FORM_PLACES:
        if not isinstance(node, list):
            raise _refuse(path)
        for item in node:
            _check_published(item, path + (_EACH,), "", context)
        if not _places_are_published(node, context.floor):
            raise _refuse(path)
        return
    if kind == _WORD:
        _check_word(node, path)
        return
    if kind == _KEY_BLOCK:
        # ...a key block is a column block (lane KV, plan P4-D487), its own
        # name a column it may cite.
        if not isinstance(node, dict) or "name" not in node or not isinstance(node["name"], str):
            raise _refuse(path)
        _check_published(
            node,
            ("columns", _EACH),
            "",
            dataclasses.replace(context, names=context.names + (node["name"],)),
        )
        return
    if not _leaf_is_published(kind, node, key, path, context):
        raise _refuse(path)


def _affix_notes_are_bound(document: "dict[str, object]") -> None:
    """Every affix spelling in a sentence is that column's own, positionally.

    THE COMPENSATING CONTROL for the fourth argument class (plan
    amendment A-P4-7). The walk above reaches a sentence without the
    block that owns it, so it can only ask whether an affix argument is
    text -- and that is not the rule. The rule is that argument 1 IS
    the block's `affix_prefix` and argument 2 IS its `affix_suffix`,
    character for character.

    Positional, because "one of the two" is satisfied by the pair
    SWAPPED: a sentence saying cells read `kg`, a number, then `$`
    misdescribes the column while passing a membership test.

    Without this, any value of anybody's table could ride into a
    published sentence through those two positions, which is the whole
    hole the argument class opened. The rendering round trip does NOT
    close it: a producer that builds the sentence from the wrong
    spelling renders consistently and passes.

    Raises ProfileError naming the column and the place, never the text
    that stood there.
    """
    columns = document["columns"] if "columns" in document else None
    if not isinstance(columns, list):
        return
    pairs: "dict[str, dict[int, str]]" = {}
    for block in columns:
        if not isinstance(block, dict):
            continue
        name = block["name"] if "name" in block else None
        prefix = block["affix_prefix"] if "affix_prefix" in block else None
        suffix = block["affix_suffix"] if "affix_suffix" in block else None
        if (
            isinstance(name, str)
            and isinstance(prefix, str)
            and isinstance(suffix, str)
        ):
            pairs[name] = {0: prefix, 1: suffix}
        # THE JOINED-NUMBER ROLE BINDS ONE PLACE, NOT TWO (plan
        # P4-D21). Its sentence names the character its cells are split
        # on, at argument 3, and that character is published in the same
        # block under `separator` -- so the binding is the same rule
        # read against a different key, and the table above is keyed by
        # POSITION rather than by side so that adding one did not mean
        # loosening the check to "one of the spellings this column
        # publishes", which the swap case rules out.
        separator = block["separator"] if "separator" in block else None
        if isinstance(name, str) and isinstance(separator, str):
            pairs[name] = {2: separator}
    for block in columns:
        if not isinstance(block, dict):
            continue
        name = block["name"] if "name" in block else None
        if not isinstance(name, str):
            continue
        said: "list[object]" = [block["detection_evidence"] if "detection_evidence" in block else None]
        remarks = block["remarks"] if "remarks" in block else None
        if isinstance(remarks, list):
            for remark in remarks:
                said += [remark]
        for sentence in said:
            _one_affix_note_is_bound(sentence, name, pairs)
    notes = document["publication_notes"] if "publication_notes" in document else None
    if isinstance(notes, list):
        for note in notes:
            if not isinstance(note, dict):
                continue
            named = note["column"] if "column" in note else None
            if isinstance(named, str):
                _one_affix_note_is_bound(note["note"] if "note" in note else None, named, pairs)
    # THE FOURTH SENTENCE PATH, and it is here because leaving it out
    # was not safe -- only unreached. `source.header_evidence` is one of
    # the four places this format carries a sentence, and it belongs to
    # no column, so no pair on earth can bind an affix spelling
    # standing in it. A note written there passed the whole guard while
    # the same note on a column's own evidence was refused, and the
    # only thing standing between that and a published spelling of
    # somebody's table was that no producer path writes one there
    # today. A control that holds because nothing currently exercises
    # it is not a control.
    source = document["source"] if "source" in document else None
    if isinstance(source, dict):
        _no_affix_stands_outside_a_column(
            source["header_evidence"] if "header_evidence" in source else None
        )


def _no_affix_stands_outside_a_column(sentence: object) -> None:
    """Refuse an affix spelling in a sentence that belongs to no column.

    The binding rule is positional against ONE column's published pair.
    A sentence about the file's header names no column, so there is
    nothing to bind it to and nothing that could make it right --
    which makes the only honest answer to refuse the form there
    outright rather than to invent a pair for it.
    """
    if not isinstance(sentence, taxonomy.Note):
        return
    for place in range(len(sentence.arguments)):
        if taxonomy.takes_a_bound_affix(sentence.form, place):
            raise _refuse(("source", "header_evidence"))


def _one_affix_note_is_bound(
    sentence: object, column: str, pairs: "dict[str, dict[int, str]]"
) -> None:
    """One sentence, checked against the spellings its column publishes.

    POSITIONAL, and the table is keyed by position for that reason: a
    sentence saying cells read `kg`, a number, then `$` misdescribes
    the column while passing any test that asks only whether the text
    is one of the two the column carries.
    """
    if not isinstance(sentence, taxonomy.Note):
        return
    for place, argument in enumerate(sentence.arguments):
        if not taxonomy.takes_a_bound_affix(sentence.form, place):
            continue
        if column not in pairs:
            # A sentence carrying such a spelling about a column that
            # publishes none has nothing to be bound to.
            raise _refuse(("columns", "[]", "affix argument"))
        bound = pairs[column]
        if place not in bound:
            raise _refuse(("columns", "[]", "affix argument"))
        if argument != bound[place]:
            raise _refuse(("columns", "[]", "affix argument"))


def _bound_key(block: object, dotted: str) -> "int | None":
    """One published key of a column block, by its dotted name."""
    if not isinstance(dotted, str):
        raise TypeError("a published key was asked for by something else")
    node: object = block
    for step in dotted.split("."):
        if not isinstance(node, dict) or step not in node:
            return None
        node = node[step]
    if isinstance(node, bool) or not isinstance(node, int):
        return None
    return node


def _main_wrapper_count(block: object) -> "int | None":
    """`n_affixed` less every named wrapper: the main wrapper's own cells."""
    if not isinstance(block, dict):
        return None
    affixed = _bound_key(block, "n_affixed")
    if affixed is None:
        return None
    variants = block["affix_variants"] if "affix_variants" in block else []
    if not isinstance(variants, list):
        return None
    named = 0
    for wrapper in variants:
        if not isinstance(wrapper, dict) or "count" not in wrapper:
            return None
        count = wrapper["count"]
        if isinstance(count, bool) or not isinstance(count, int):
            return None
        named = named + count
    return affixed - named


def _is_the_fragment(argument: object, line: int) -> bool:
    """Whether this argument is `said_fewer_than_the_line` carrying THE line.

    The line and no other number: a fragment built with a smaller one
    would say "fewer than 3" about a run whose smallest group is
    eleven, which is a narrower claim than the floor allows and a
    reader cannot tell from the truth.
    """
    if not isinstance(argument, tuple) or len(argument) != 2:
        return False
    if argument[0] != taxonomy.SAID_FEWER_THAN_THE_LINE:
        return False
    parts = argument[1]
    return isinstance(parts, tuple) and parts == (line,)


def _says_no_count(argument: object) -> bool:
    """Whether this argument is `said_some_but_not_all` or `said_some`, which name none.

    THE SECOND THING A FLOORED POSITION MAY CARRY INSTEAD OF DIGITS
    (contract NF61). `_is_the_fragment` above answers the small case:
    the count is one or more and below the line, and the reader is
    told the shape of the number. This answers the COMPLEMENT case: the
    count reaches the line and what it leaves over against its
    population does not, so the digits would publish that remainder by
    subtraction -- and NF60 cannot stand there either, because "fewer
    than 11" is false of a count of 1,199.

    It is accepted AT ANY FLOORED POSITION AND AT ANY LINE, and there
    is nothing to check about it: a form with no argument carries no
    number, so there is no line it could contradict and no key it
    could disagree with. That is the whole reason it exists. NF87,
    `said_some`, is accepted on the same terms.
    """
    if not isinstance(argument, tuple) or len(argument) != 2:
        return False
    if argument[0] not in (taxonomy.SAID_SOME_BUT_NOT_ALL, taxonomy.SAID_SOME):
        return False
    return isinstance(argument[1], tuple) and argument[1] == ()


def _floored_argument_is_bound(
    value: int,
    binding: "tuple[object, ...]",
    block: object,
    line: int,
    path: "tuple[str, ...]",
) -> None:
    """One floored position: nought, or a group, with no group left over.

    THE THIRD CLAUSE IS WHAT THE POPULATION IS FOR. A count that
    reaches the line is still refused where the population its binding
    names leaves a group of one to ten over, because a reader holding
    the sentence and the block does that subtraction in their head:
    1,199 comma-grouped prices printed beside a published `n_present`
    of 1,200 hands back the one bare cell. Four of the thirteen floored
    positions name a population, and `taxonomy.ARGUMENT_BINDINGS` says
    which and why.

    The producer does not reach this refusal, and that is a property
    rather than luck: `taxonomy._floored_stands` asks the same question
    one step earlier and writes `said_some_but_not_all` -- which
    `_says_no_count` accepts above -- where the sentence may not be
    withdrawn. Before the repair pass it wrote the digits instead, so
    the first binding to name a population turned an ordinary table
    into an internal fault here.
    """
    if value == 0:
        return
    if value < line:
        raise _refuse(path)
    if len(binding) < 2:
        return
    populations = binding[1]
    if not isinstance(populations, tuple):
        raise _refuse(path)
    for named in populations:
        name = f"{named}"
        if not isinstance(name, str):
            raise _refuse(path)
        total = _bound_key(block, name)
        if total is None:
            raise _refuse(path)
        rest = total - value
        if rest != 0 and rest < line:
            raise _refuse(path)


def _one_argument_is_bound(
    form: str,
    place: int,
    value: object,
    block: object,
    document: "dict[str, object]",
    line: int,
) -> None:
    """One argument of one sentence, held to what the grammar binds it to."""
    path = ("columns", _EACH, "sentence argument")
    binding = taxonomy.argument_binding(form, place)
    if not binding:
        # A POSITION NOBODY BOUND. The table is closed over every form,
        # so this is a form added without one -- a number a sentence
        # may print that no rule governs -- and the answer is a refusal
        # rather than a guess at which rule was meant.
        raise _refuse(path)
    kind = binding[0]
    if kind == taxonomy.BIND_FLOORED:
        if _is_the_fragment(value, line) or _says_no_count(value):
            return
        if isinstance(value, bool) or not isinstance(value, int):
            raise _refuse(path)
        _floored_argument_is_bound(value, binding, block, line, path)
        return
    if kind in (
        taxonomy.BIND_SETTING,
        taxonomy.BIND_VOCABULARY,
        taxonomy.BIND_STRUCTURAL,
        taxonomy.BIND_LEVELS_AT_THE_LINE,
        # THE DESCRIBED TABLE'S OWN POPULATION (contract NF59). There
        # is nothing here to compare it with and that is the rule, not
        # a gap: the population is the rows holding a value, counted in
        # people where a declared identifier repeats, and no key of the
        # description publishes either count. A loader accepts a
        # conforming document with the note or without it at any row
        # count, so a number checked against a key would be a check
        # this contract does not state.
        taxonomy.BIND_POPULATION,
        taxonomy.BIND_WORD,
        taxonomy.BIND_NESTED,
        taxonomy.BIND_AFFIX,
        # A VALUE OF THE COLUMN SAID A SECOND WAY, which the stage-3
        # tail rule governs and no count rule can: the epoch-band
        # remark reads the two published edges as calendar days. It is
        # exempt HERE and checked one level up, by
        # `_epoch_band_quotes_the_published_edges`, because the day at
        # one position is decided by the band argument and the block
        # together and not by that position alone.
        taxonomy.BIND_VALUE,
    ):
        return
    if isinstance(value, bool) or not isinstance(value, int):
        raise _refuse(path)
    if kind == taxonomy.BIND_DOCUMENT:
        named = f"{binding[1]}"
        stated = document[named] if named in document else None
        if stated != value:
            raise _refuse(path)
        return
    if block is None:
        # A SENTENCE BOUND TO A COLUMN'S KEY AND STANDING NOWHERE NEAR
        # ONE. `source.header_evidence` belongs to no column, so there
        # is no block to bind it to and nothing that could make it
        # right.
        raise _refuse(("source", "header_evidence"))
    if kind == taxonomy.BIND_KEY:
        published = _bound_key(block, f"{binding[1]}")
        if published is None or published != value:
            raise _refuse(path)
        return
    if kind == taxonomy.BIND_SUM:
        total = 0
        summed = binding[1]
        if not isinstance(summed, tuple):
            raise _refuse(path)
        for named in summed:
            part = _bound_key(block, f"{named}")
            if part is None:
                raise _refuse(path)
            total = total + part
        if total != value:
            raise _refuse(path)
        return
    if kind == taxonomy.BIND_DIFFERENCE:
        left = _bound_key(block, f"{binding[1]}")
        right = _bound_key(block, f"{binding[2]}")
        if left is None or right is None or left - right != value:
            raise _refuse(path)
        return
    if kind == taxonomy.BIND_MAIN_WRAPPER:
        main = _main_wrapper_count(block)
        if main is None or main != value:
            raise _refuse(path)
        return
    raise _refuse(path)


def _one_note_is_bound(
    sentence: object,
    block: object,
    document: "dict[str, object]",
    line: int,
) -> None:
    """Every argument of one sentence, nested fragments included."""
    if not isinstance(sentence, taxonomy.Note):
        return
    _arguments_of_one_form_are_bound(
        sentence.form, sentence.arguments, block, document, line
    )


def _epoch_band_quotes_the_published_edges(
    arguments: "tuple[object, ...]", block: object
) -> None:
    """NF51's two days are the two edges the block beside it publishes.

    **AN ADVISORY REMARK MAY NOT OUTLIVE THE FACTS IT QUOTES** (stage 3,
    plan P4-D345, contract NF51). Arguments 2 to 7 are one value of the
    column said a second way -- `BIND_VALUE` -- and until both tail
    landings stood in one tree there was nothing to say it against:
    they restated `percentiles.min` and `percentiles.max`, which the
    numeric tail rule then withdrew. Now each end is whatever the block
    publishes in its place (`taxonomy.published_ends`): the end itself
    where a group of `tail_units` rows holds it, and the side's
    boundary rung otherwise. This rebuilds both days from the block and
    the band argument and refuses the document where either differs, so
    a description whose ends are gone and whose prose still names them
    cannot be loaded.

    Guarantees: accepts NF51's seven arguments and the block the note
    stands on; returns where they agree. Errors raised: the loader's
    own refusal where the block publishes no edge, where an argument is
    not a whole number, or where a day differs. No I/O of any kind.
    """
    path = ("columns", _EACH, "sentence argument")
    if not isinstance(block, dict) or len(arguments) != 7:
        raise _refuse(path)
    for argument in arguments:
        if isinstance(argument, bool) or not isinstance(argument, int):
            raise _refuse(path)
    edges = taxonomy.published_ends(block)
    if edges is None:
        # THE BLOCK PUBLISHES NO EDGE ON ONE SIDE, so both days would be
        # values nothing else in the description holds -- which is the
        # one thing a sentence argument may never be (contract 4.5.1).
        raise _refuse(path)
    stated = taxonomy.epoch_band_days(arguments[0], edges)
    if stated is None or stated != tuple(arguments):
        raise _refuse(path)


def _counted_years_quote_the_published_edges(
    arguments: "tuple[object, ...]", block: object
) -> None:
    """NF114's two years are those the block beside it publishes (landing R4).

    NF51'S RULE FOR ITS DAYS, kept for the remark that replaced it: an
    advisory remark may not outlive the facts it quotes (plan P4-D345).
    Each year is the one the producer's own walk of the block's published
    rungs reads in the member at argument 1 (`taxonomy.counted_edge_years`)
    -- from the heaped end or the boundary rung inward, past every heap
    rung and the rungs read beside heaps, never an outermost value -- and
    the document is refused where either differs, or where the block
    publishes no such rung on one side. THE HEAPS ARE THE ONES THE
    REMARKS PUBLISH: the count, in every system an NF114 of the block
    names, of each set-aside word its NF113 names (`date_counts.heap_counts`;
    the second review of landing R4, item 3), as the producer asked them.

    Guarantees: accepts NF114's three arguments and the block; returns
    where they agree. Errors raised: the loader's own refusal otherwise. No
    I/O of any kind.
    """
    path = ("columns", _EACH, "sentence argument")
    if not isinstance(block, dict) or len(arguments) != 3:
        raise _refuse(path)
    member = arguments[0]
    if not isinstance(member, str) or member not in date_counts.MEMBERS:
        raise _refuse(path)
    words: "list[str]" = []
    members: "list[str]" = []
    remarks = block["remarks"] if "remarks" in block else None
    if isinstance(remarks, list):
        for remark in remarks:
            if not isinstance(remark, taxonomy.Note):
                continue
            if remark.form == taxonomy.REMARK_NUMBERS_COULD_BE_DATES:
                for word in remark.arguments[1:]:
                    if isinstance(word, str) and word != date_counts.ASIDE_NONE:
                        words += [word]
            elif remark.form == taxonomy.REMARK_READ_AS_COUNTED_DATES:
                named = remark.arguments[0] if remark.arguments else None
                if isinstance(named, str) and named in date_counts.MEMBERS:
                    members += [named]
    years = taxonomy.counted_edge_years(
        block, member, date_counts.heap_counts(tuple(words), tuple(members))
    )
    if years is None or years != (arguments[1], arguments[2]):
        raise _refuse(path)


def _arguments_of_one_form_are_bound(
    form: str,
    arguments: "tuple[object, ...]",
    block: object,
    document: "dict[str, object]",
    line: int,
) -> None:
    """`_one_note_is_bound` for one form's arguments."""
    for place in range(len(arguments)):
        argument = arguments[place]
        floored = taxonomy.argument_binding(form, place)[:1] == (
            taxonomy.BIND_FLOORED,
        )
        nested = (
            isinstance(argument, tuple)
            and len(argument) == 2
            and isinstance(argument[0], str)
            and isinstance(argument[1], tuple)
        )
        # A FLOORED POSITION IS ASKED WHOLE, fragment or digits, and is
        # never walked into. Walking in would ask the fragment's own
        # argument -- the LINE, which is a setting and exempt -- and a
        # fragment carrying any other number would pass on the strength
        # of its own exemption. Measured while this landing was built:
        # "fewer than 3" standing in a document whose smallest group is
        # eleven was accepted by the first writing of this walk.
        if nested and isinstance(argument, tuple) and not floored:
            if argument[0] in (
                taxonomy.SAID_FEWER_THAN_THE_LINE,
                taxonomy.SAID_SOME_BUT_NOT_ALL,
                taxonomy.SAID_SOME,
            ):
                # AND NEITHER FRAGMENT STANDS ANYWHERE ELSE. Each is
                # the answer to one question -- what a sentence says in
                # place of a count it may not print -- and a sentence
                # that used one anywhere else would be saying "fewer
                # than eleven", or "some but not all", about something
                # that is not a count.
                raise _refuse(("columns", _EACH, "sentence argument"))
            _arguments_of_one_form_are_bound(
                f"{argument[0]}", tuple(argument[1]), block, document, line
            )
            continue
        _one_argument_is_bound(
            form, place, argument, block, document, line
        )
    if form == taxonomy.REMARK_EPOCH_BAND:
        # ...AND THE SIX `value` POSITIONS ARE ASKED TOGETHER, because
        # the day at each of them is decided by the BAND at argument 1
        # and by the block, not by that position on its own.
        _epoch_band_quotes_the_published_edges(arguments, block)
    # -- 3b.R4 (P4-D384): ...AND NF114'S TWO YEARS, for the same reason:
    # each is decided by the member at argument 1 and the block's edge.
    if form == taxonomy.REMARK_READ_AS_COUNTED_DATES:
        _counted_years_quote_the_published_edges(arguments, block)


def _arguments_are_bound(document: "dict[str, object]") -> None:
    """Refuse a sentence carrying a count the keys beside it withhold.

    THE RULE IN ONE SENTENCE: a sentence may not carry a count a key
    withholds. Every published count of a column block is held to the
    smallest group size; a count written into a SENTENCE was held to
    nothing, and the two are the same disclosure. Measured over 56
    descriptions at a floor of eleven before this guard existed (the
    design's own `guard_measure.txt`): 252 sentences and 145 of them
    carrying whole numbers, of which NINE printed a count no key of the
    block published at all and 38 more restated a count the key itself
    published below the line. This guard closes the nine; the other 38
    are P4-D332's, which leaves those keys standing and holds their
    number at a ceiling. THE SECOND NUMBER READ 29 UNTIL THE REPAIR
    PASS, and 29 is what that same run records only under a rule-M
    prototype this landing did not build; 38 is what it records for the
    tool as shipped.
    `tests/test_p4d334_sentence_arguments.py::test_the_keys_a_sentence_restates_below_the_line_are_held_at_a_ceiling`
    re-measures the class over the committed battery, so the number is
    one a reader can run rather than one they must trust.

    HOW IT IS CHECKED, and why it is a table rather than a rule per
    remark. `taxonomy.ARGUMENT_BINDINGS` binds every argument position
    of every form to what it IS -- a key of the block, a sum or a
    difference of keys, a key of the document, the main wrapper's
    cells, a setting, the levels at the line, a place in one of this
    package's own lists, a column number, a value of the column said a
    second way, or one of the thirteen counts no key carries. A bound
    position must EQUAL what it is bound to, so the key's own floor
    rule governs the sentence; a floored one is nought, or reaches
    `parsing.census_floor` with no group left over against the
    populations its binding names, or carries the fragment
    `said_fewer_than_the_line`, or -- where it reaches the line and
    the population leaves a group below it -- `said_some_but_not_all`,
    which names no number at all. This is plan P4-D221's padded-remark
    rule -- "a count the map does not name is a count no sentence
    prints" -- made general instead of written once per remark.

    IT RUNS BESIDE `_affix_notes_are_bound` AND FOR THE SAME REASON:
    both need the BLOCK the sentence belongs to, which the walk itself
    does not carry.

    Guarantees:

    - Inputs: the finished document, publication notes lifted out.
    - Determinism: the answer depends only on the document and on this
      package's own binding table.
    - Errors raised: ProfileError naming the place and never a value.
    - Boundary: nothing is opened, nothing is written, and no value of
      the table reaches the refusal.
    """
    floor = _publication_context(document).floor
    line = parsing.census_floor(floor)
    blocks = document["columns"] if "columns" in document else []
    by_name: "dict[str, object]" = {}
    if isinstance(blocks, list):
        for block in blocks:
            if isinstance(block, dict) and "name" in block:
                name = block["name"]
                if isinstance(name, str):
                    by_name[name] = block
    if isinstance(blocks, list):
        for block in blocks:
            if not isinstance(block, dict):
                continue
            said: "list[object]" = [
                block["detection_evidence"]
                if "detection_evidence" in block
                else None
            ]
            remarks = block["remarks"] if "remarks" in block else None
            if isinstance(remarks, list):
                for remark in remarks:
                    said += [remark]
            for sentence in said:
                _one_note_is_bound(sentence, block, document, line)
    notes = (
        document["publication_notes"]
        if "publication_notes" in document
        else None
    )
    if isinstance(notes, list):
        for entry in notes:
            if not isinstance(entry, dict):
                continue
            named = entry["column"] if "column" in entry else None
            block = by_name[named] if isinstance(named, str) and named in by_name else None
            _one_note_is_bound(
                entry["note"] if "note" in entry else None,
                block,
                document,
                line,
            )
    source = document["source"] if "source" in document else None
    if isinstance(source, dict):
        _one_note_is_bound(
            source["header_evidence"] if "header_evidence" in source else None,
            None,
            document,
            line,
        )


def _publication_context(document: dict[str, object]) -> _Publication:
    """The floor and the column names, read out before the walk.

    Both are facts the guard checks other leaves against, so both are
    established first and refused here if they are not what they must
    be. A floor read out of a document that had none would make every
    floor check pass.
    """
    if "settings" not in document:
        raise _refuse(("settings",))
    settings = document["settings"]
    if not isinstance(settings, dict) or "small_cell_floor" not in settings:
        raise _refuse(("settings", "small_cell_floor"))
    floor = settings["small_cell_floor"]
    if not _is_count(floor) or not isinstance(floor, int) or floor < 1:
        raise _refuse(("settings", "small_cell_floor"))
    if "columns" not in document:
        raise _refuse(("columns",))
    blocks = document["columns"]
    if not isinstance(blocks, list):
        raise _refuse(("columns",))
    names: list[str] = []
    for block in blocks:
        if not isinstance(block, dict) or "name" not in block:
            raise _refuse(("columns", _EACH, "name"))
        name = block["name"]
        if not isinstance(name, str):
            raise _refuse(("columns", _EACH, "name"))
        names += [name]
    return _Publication(floor=floor, names=tuple(names))


def check_publication(document: dict[str, object]) -> None:
    """Refuse a finished profile that carries anything it may not.

    Guarantees:

    - Inputs: a finished profile document, exactly as it would be
      serialized -- top-level publication notes included, because they
      are lifted out of the column blocks before this runs and a check
      that walked only the columns would never see them.
    - Determinism: the answer depends only on the document. Mappings
      are walked in sorted key order and nothing outside the document
      is consulted, apart from this package's own vocabularies and the
      installed version.
    - Errors raised: ProfileError, with a plain-language message naming
      the PLACE in the description and never the text that stood there,
      for anything the rules above do not authorize: a path with no
      rule, a leaf of the wrong type, a mapping key with no rule, a
      count that did not clear the small-cell floor, and a sentence
      this package cannot write again from an enumerated form.
    - Boundary: nothing is opened, nothing is written, no value of the
      table travels into the message, and the document is not changed.

    It runs BEFORE serialization, so a document that fails here is
    never turned into bytes and never reaches a disk.
    """
    context = _publication_context(document)
    _check_published(document, (), "", context)
    _trailing_closings_are_headed(document)
    _affix_notes_are_bound(document)
    _arguments_are_bound(document)


def _trailing_closings_are_headed(document: dict[str, object]) -> None:
    """Refuse a trailing delimiter under a header not read from the file.

    Without a header from the file the survey takes the width from the
    first record, so a delimiter ending the records is a column more and
    the producer publishes both closings `false`; a twin written with
    rows closed otherwise is read back one column wider (the verifier of
    Codex's review of landing R6, open item 1; the loader's FD10). The
    trailing block cannot see the header's source, so this asks it from
    the document after the walk has checked both leaves' kinds.
    """
    if "source" not in document:
        return
    source = document["source"]
    if not isinstance(source, dict) or "dialect" not in source:
        return
    if "header_source" in source and source["header_source"] == reading.HEADER_FROM_FILE:
        return
    form = source["dialect"]
    if not isinstance(form, dict) or "trailing_delimiter" not in form:
        return
    trailing = form["trailing_delimiter"]
    if not isinstance(trailing, dict):
        return
    for side in ("header", "rows"):
        if side in trailing and trailing[side] is not False:
            raise _refuse(_TRAILING_BLOCK + (side,))


def _is_mechanical_index(
    position: int, names: "list[str]", declared: "list[str]"
) -> bool:
    """Whether this column is a written row index nobody declared.

    A mechanical index is the FIRST column and is named as one of the two
    writers that produce it name it. A column of its own name holding
    1, 2, 3, ... -- a REDCap `record_id`, a register's serial -- is not
    one: it is the table's own data, and publishing its sequence would
    let the generator write the real column back (plan P4-D76).
    """
    if position != 0 or position >= len(names):
        return False
    if names[position] in declared:
        return False
    return names[position] in dialect.INDEX_NAMES


def _published_form(
    table: Table,
    columns: "list[dict[str, object]]",
    declared_identifiers: "list[str]",
) -> dialect.Dialect:
    """The table's written form, with nothing of anybody's in it.

    THE LINES BEFORE THE TABLE ARE NOT HELD TO THE FLOOR HERE ANY MORE,
    because they are no longer text by the time they arrive: the survey
    publishes each run of them as a kind, a count and a mark (plan
    P4-D80). What this function still does is keep a DECLARED
    IDENTIFIER out of the written form -- the row sequence and the row
    order both hand back a declared column's own values -- and drop a
    row order the twin could not keep.
    """
    surveyed = table.survey
    if surveyed is None:
        plain = dialect.ordinary(
            len(table.column_names),
            table.n_rows,
            table.header_source == reading.HEADER_FROM_FILE,
        )
        if table.native is None:
            return plain
        # A FILE FROM ANOTHER SYSTEM IS WRITTEN IN THE ORDINARY FORM, AND ITS
        # ROWS' ORDER IS READ OFF ITS CELLS AS A SURVEY READS A CSV FILE'S
        # (lane FORMATS, `dialect.row_order_of`): the same table in CSV
        # publishes the column its rows are sorted by, so this does too, and
        # the rules below hold it to the declared identifiers and the absent
        # cells as they hold a survey's.
        width = len(table.column_names)
        rows_sorted = dialect.row_order_of(
            [reading.column_values(table, place) for place in range(width)],
            [-1] * width,
            table.n_rows,
        )
        form = dataclasses.replace(plain, row_order=rows_sorted)
    else:
        form = surveyed.form
    # NO FILE-LEVEL FACT MAY REBUILD A DECLARED IDENTIFIER, OR A REAL ROW
    # (plan P4-D76). `sequence_start` is written back by the generator as
    # the literal cells 0, 1, 2, ... or 1, 2, 3, ..., so a column
    # published as the row sequence is a column the twin reproduces
    # EXACTLY. On a declared identifier that publishes the very values
    # the declaration exists to withhold, and on two such columns beside
    # each other it reproduces whole real rows.
    #
    # So a sequence is published only for a MECHANICAL index -- a written
    # row index nobody declared, which is the file's own numbering and
    # not a value of anybody's -- and never for a column whose cells are
    # absent anywhere, which the loader could not hold to FD6 either.
    names = [f"{block['name']}" for block in columns]
    kept: "list[dialect.ColumnForm]" = []
    for index in range(len(form.columns)):
        column = form.columns[index]
        if column.sequence_start >= 0:
            missing = 0
            if index < len(columns) and "n_missing" in columns[index]:
                counted = columns[index]["n_missing"]
                missing = counted if isinstance(counted, int) else 0
            if missing or not _is_mechanical_index(index, names, declared_identifiers):
                column = dataclasses.replace(column, sequence_start=-1)
        kept += [column]
    form = dataclasses.replace(form, columns=tuple(kept))
    # ...and the order the rows stand in is a fact about the declared
    # column's own values, so it is not published of one either.
    sorted_by = form.row_order.column
    if sorted_by and sorted_by <= len(names) and names[sorted_by - 1] in declared_identifiers:
        form = dataclasses.replace(form, row_order=dialect.NO_ORDER)
    # A ROW ORDER THE TWIN COULD NOT KEEP IS NOT PUBLISHED. The survey
    # reads a sort column off cells that all hold something; the column's
    # own description may still count some of them absent -- cells of
    # nothing but spaces, or spellings too rare to publish -- and the twin
    # writes those empty, which no order of the published kind can hold.
    # Contract invariant FD7 refuses the pair, so the order is dropped
    # here, where both are in hand.
    #
    # The records holding nothing are the exception: each gives the sort
    # column one empty cell, which the twin writes in that record, so the
    # column may count exactly that many cells empty and no more.
    order = form.row_order.column
    empties = form.empty_rows_leading + form.empty_rows_interior + form.empty_rows_trailing
    if order and order <= len(columns):
        block = columns[order - 1]
        # EVERY ABSENT CELL THE TWIN WRITES EMPTY, counted the way the
        # generator decides it (plan P4-D173): the column's absent cells
        # less the spellings it reproduces -- every one of them, a judged
        # pass's included since plan P4-D6.4. It used to be
        # the blank and pooled counts with the judged cells added, which
        # left out every absent cell no field names -- measured: a sorted
        # free-text column with twenty `--missing-value ZZZ` cells
        # published its order, the twin wrote those twenty empty, and the
        # twin missed `rows.order` while the real file passed.
        absent_cells = block["n_missing"] if "n_missing" in block else 0
        spellings = (
            block["missing_by_source"] if "missing_by_source" in block else {}
        )
        reproduced = 0
        if isinstance(spellings, dict):
            for spelling in sorted(spellings):
                held = spellings[spelling]
                if isinstance(held, int):
                    reproduced = reproduced + held
        written_empty = -1
        if isinstance(absent_cells, int):
            written_empty = absent_cells - reproduced
            if written_empty < 0:
                written_empty = 0
        if written_empty != empties:
            form = dataclasses.replace(form, row_order=dialect.NO_ORDER)
    # AND THE LINES BEFORE THE TABLE ARE ALREADY SHAPES. The survey
    # publishes their kind, their count and their mark, so there is
    # nothing left here for a floor to hold back and no floor at which
    # anything more is published. The branch this replaced returned the
    # form untouched at a floor of one -- the default then, before plan
    # P4-D316 made it 11 -- which is how a title line naming a person
    # reached the description whole (review item CODEX-3).
    return form


def _published_workbook(
    table: Table,
    floor: int,
    columns: "list[dict[str, object]]",
    absent_spellings: "list[tuple[str, ...]]",
) -> "dict[str, object] | None":
    """The workbook block, or None where the table was not in one.

    EACH COLUMN'S CENSUS COUNTS WHAT ITS TWIN WRITES (plan P4-D174). The
    twin writes an absent cell empty unless its spelling is one the
    column publishes, and it reproduces every one of those (contract
    C6-115; a judged pass's too since plan P4-D6.4), so a
    workbook cell holding three spaces, `NA` or a declared missing value
    whose spelling the floor held back comes back from the twin as a cell
    holding nothing. The census counted it as the text it was, the twin
    could not write that text, and the twin missed
    `workbook.cell-classes` while the source passed -- measured on a
    column of a hundred labels, one of them three spaces, at a floor of
    five. So the spellings the twin writes empty are handed over, read
    off the column blocks as published by the rule FD7 shares, and such
    a cell is counted absent on both files alike.
    """
    if table.book is None or table.sheet is None:
        return None
    emptied: "list[tuple[str, ...]]" = []
    for index in range(len(columns)):
        block = columns[index]
        spellings = (
            block["missing_by_source"] if "missing_by_source" in block else {}
        )
        reproduced: "dict[str, bool]" = {}
        if isinstance(spellings, dict):
            for spelling in sorted(spellings):
                if isinstance(spelling, str):
                    reproduced[spelling] = True
        held = absent_spellings[index] if index < len(absent_spellings) else ()
        written_empty: "list[str]" = []
        for spelling in held:
            if spelling not in reproduced:
                written_empty += [spelling]
        emptied += [tuple(written_empty)]
    block = workbook.document_of(table.book, table.sheet, floor, tuple(emptied))
    return _stored_as_text_withheld(
        _pooled_absence_withheld(block, columns), columns, floor
    )


# The roles whose column publishes no value of its own (a key, free text,
# nothing at all): such a column's value labels are dropped whole.
_ROLES_WITHOUT_VALUES = (
    taxonomy.ROLE_IDENTIFIER,
    taxonomy.ROLE_TEXT,
    taxonomy.ROLE_EMPTY,
    taxonomy.ROLE_UNREPRESENTABLE,
)
# The different cells a value label's count reads once each (a column of two million different numbers holds a
# bounded map: past it a cell is read again).
_VALUE_LABEL_MEMO = 4096


def _published_native(
    table: Table,
    columns: "list[dict[str, object]]",
    floor: int,
    held_back: "list[str]",
) -> "dict[str, object] | None":
    """The native block of a description (lane FORMATS), or None where the table was no native file.

    WHAT OF THE FILE'S OWN FORM IS PUBLISHED (`native`'s docstring gives
    each rule's reason). The storage of every column, how its cells are
    written as text, its fraction of a second and its time zone's name
    where `native.name_published` admits it; its display format where
    `native.format_published` admits it; its label where
    `native.column_label_published` admits it (the identifier rules a
    column's name meets on the CSV route); a value label where the CODE is
    held by at least ``floor`` of the column's cells AND its text is
    admitted (a code of a column stored as numbers counted by its value),
    and no value label at all of a column whose
    role publishes no value, that the description holds back
    (``held_back``: a declared identifier, a column held for Safe Harbor
    or within each person) or that its block top-codes (any `top_coded`
    key: an age past 89 is a code the cap withholds); SPSS's missing codes where each is a number or an admitted
    text, of a column whose values are published only; a member name the rule admits; pandas' type words (a closed
    list) and the index pandas named, where it names columns of the
    table or a range starting at 0 or 1. The file's own label, notes,
    creator, dates and every other pair of text it carried are never
    read into the form at all (`nativereading`).

    Guarantees: a fixed function of the table, the blocks and the
    floor; reads the table's cells (`reading.column_values`) to count
    codes; raises nothing of its own.
    """
    found = table.native
    if found is None:
        return None
    form = found.form
    system = form.system
    kept: "list[native.NativeColumn]" = []
    for place in range(len(form.columns)):
        column = form.columns[place]
        name = table.column_names[place]
        role = columns[place]["role"] if place < len(columns) and "role" in columns[place] else ""
        published_values = role not in _ROLES_WITHOUT_VALUES and name not in held_back
        # NO VALUE LABEL OF A COLUMN THE DESCRIPTION TOP-CODES (batch 4zy's landing, the outside review's item 1,
        # HIPAA): a label's code is a value of the column, and the cap withholds every value past its mark, so an SPSS
        # age column whose 1,000 cells read `95.00` with the label `95: "Senior"` wrote the code 95 -- an age past
        # 89 -- into the twin's dictionary once codes were counted by value (and wrote it by spelling where the cells
        # read `95`). Every `top_coded` key the description can write (the mark, the year cut, the ends, the bands,
        # the words) withholds the column's labels whole.
        block_here = columns[place] if place < len(columns) else {}
        top_coded = False
        for key in block_here:
            written_key = f"{key}"
            if written_key[: len("top_coded")] == "top_coded":
                top_coded = True
        labels: "tuple[tuple[str, str], ...] | None" = None
        if column.value_labels and published_values and not top_coded:
            counted: "dict[str, int]" = {}
            for code, _text in column.value_labels:
                counted[code] = 0
            # A NUMBER'S CODE IS COUNTED BY ITS VALUE (lane LEDGER; Codex's review of batch 4zz, item 16): an SPSS
            # column of codes 1, 1.5 and 2.25 is written `1.00`, `1.50` and `2.25` by its display format, so read by
            # spelling only the third code was held by the floor's cells and the other two labels were dropped. A
            # cell of a column stored as numbers counts under every code whose value it holds; a text column's codes
            # are counted by spelling alone.
            by_value: "dict[float, list[str]]" = {}
            if column.storage != native.STORE_TEXT:
                for code, _text in column.value_labels:
                    code_value = native.exact_double(code)
                    if code_value is not None and code_value == code_value:
                        by_value[code_value] = (by_value[code_value] if code_value in by_value else []) + [code]
            read_once: "dict[str, float | None]" = {}
            for cell in reading.column_values(table, place):
                if cell in counted:
                    counted[cell] = counted[cell] + 1
                    continue
                if not by_value:
                    continue
                if cell in read_once:
                    held_value = read_once[cell]
                else:
                    held_value = native.exact_double(cell)
                    if len(read_once) < _VALUE_LABEL_MEMO:
                        read_once[cell] = held_value
                if held_value is not None and held_value in by_value:
                    for code in by_value[held_value]:
                        counted[code] = counted[code] + 1
            chosen: "list[tuple[str, str]]" = []
            for code, text in column.value_labels:
                if counted[code] < floor:
                    continue
                if not native.label_published(text):
                    continue
                if column.storage == native.STORE_TEXT and not native.label_published(code):
                    continue
                chosen += [(code, text)]
            labels = tuple(chosen) if chosen else None
        missing = column.missing
        # ...and no missing code of a column whose values are not published (batch 4zz's fix round, the outside
        # review's item 2): a real record number set as an SPSS missing code of a held identifier column reached
        # the twin's dictionary.
        if missing is not None and not published_values:
            missing = None
        if missing is not None:
            codes = tuple(
                [
                    code for code in missing.values
                    if native.exact_double(code) is not None or native.label_published(code)
                ]
            )
            missing = native.NativeMissing(values=codes, low=missing.low, high=missing.high)
            if not codes and missing.low is None:
                missing = None
        display = column.display if column.display is not None and native.format_published(column.display, system) else None
        label = column.label if column.label is not None and native.column_label_published(column.label) else None
        label_set = (
            column.label_set
            if labels is not None and column.label_set is not None and native.name_published(column.label_set, 32)
            else None
        )
        zone = column.zone if column.zone is not None and native.zone_published(column.zone) else None
        empty_text = (
            column.empty_text
            if column.empty_text is not None and native.empty_text_published(column.empty_text)
            else None
        )
        # A categorical's categories, in its file's order: each a value
        # its column publishes, held to the same floor and reading a value
        # label is (a category is a cell of the column).
        categories: "tuple[str, ...] | None" = None
        if column.categories and published_values:
            counted_levels: "dict[str, int]" = {}
            for level in column.categories:
                counted_levels[level] = 0
            for cell in reading.column_values(table, place):
                if cell in counted_levels:
                    counted_levels[cell] = counted_levels[cell] + 1
            kept_levels = tuple(
                [
                    level for level in column.categories
                    if counted_levels[level] >= floor and native.label_published(level)
                ]
            )
            categories = kept_levels if kept_levels else None
        kept += [
            dataclasses.replace(
                column,
                display=display,
                label=label,
                label_set=label_set if system == native.FORMAT_STATA else None,
                value_labels=labels,
                missing=missing,
                zone=zone,
                categories=categories,
                empty_text=empty_text,
            )
        ]
    index = form.index
    if index is not None:
        named = tuple([name for name in index.columns if name in table.column_names])
        index = native.NativeIndex(columns=named, start=index.start, step=index.step)
        if not named and index.start is None:
            index = None
    table_name = form.table_name
    if table_name is not None and not native.name_published(table_name, 32):
        table_name = None
    published = native.NativeForm(
        system=system,
        version=form.version,
        columns=tuple(kept),
        table_name=table_name,
        index=index,
    )
    return native.document_of(published)


def _pooled_absence_withheld(
    block: "dict[str, object]",
    columns: "list[dict[str, object]]",
) -> "dict[str, object]":
    """A column's class census withheld where the twin cannot be held to it.

    A CENSUS OF THE SHEET'S CELLS BESIDE A COLUMN THAT CALLS SOME OF
    THEM ABSENT. `cell_classes` counts every cell of the column as the
    SHEET stored it -- text, number, date -- and the column beside it
    says how many cells are absent under a spelling the floor would not
    let it name (`n_missing_withheld`). The twin writes those cells
    EMPTY, because nothing published says what they held, so its own
    census counts an empty cell where this one counts a text or a
    number, and the twin misses a census it was never able to meet.

    MEASURED while the owner's ruling of 2026-09-17, item 5 counted a
    lone label's cells as absent (plan P4-D231; set aside by P4-D390,
    which leaves those cells present): forty-one records of three texts
    at a floor of five, whose first record holds a lone `amber` and a
    lone `Northfield`, published `text: 41` on each column and wrote a
    twin whose census was withheld -- `workbook.cell-classes` MISSED on
    both, with the real workbook holding every obligation. A spelling of
    "no value" the floor will not name is the same cell today.

    So the census is withheld for such a column, exactly as
    `_stored_as_text_withheld` withholds one whose difference a reader
    could take. A withheld census publishes no count and is never
    missed, and what the column says about its own cells is unchanged.

    Guarantees: returns the block, changed only so; a fixed function of
    its arguments; raises nothing; no I/O of any kind.
    """
    censuses = block["columns"]
    if not isinstance(censuses, list):
        return block
    for index in range(min(len(censuses), len(columns))):
        entry = censuses[index]
        pooled = columns[index]["n_missing_withheld"]
        if not isinstance(entry, dict) or not isinstance(pooled, int):
            continue
        # ...AND A COLUMN COUNTED ABSENT (plan P4-D453): its census of text or
        # number cells would print the count its block withholds.
        counted_absent = "present_count_withheld" in columns[index]
        if (isinstance(pooled, bool) or pooled < 1) and not counted_absent:
            continue
        classes = entry["cell_classes"]
        if not isinstance(classes, dict):
            continue
        entry["cell_classes"] = {key: None for key in classes}
        if counted_absent:
            # ...nor the class of the few cells it has, which the twin writes
            # blank (a checked file is asked nothing of a class not published).
            entry["value_class"] = None
    return block


def _stored_as_text_withheld(
    block: "dict[str, object]",
    columns: "list[dict[str, object]]",
    floor: int,
) -> "dict[str, object]":
    """A column's census withheld where it would name figures stored as text.

    THE DIFFERENCE A READER CAN TAKE (plan P4-D197, final skeptic of stage
    2's close). A workbook column of numbers some of which are stored as
    text publishes its count of numbers beside its census of cell classes
    (plan P4-D187), and the one less the other is how many figures were
    stored as text: 400 readings, one stored as text and one the word
    `pending`, published `n_numeric` 399 beside `number` 398 at the
    default floor, which names one cell. So where a column's census counts
    number cells at all and its count of numbers passes that count by a
    difference `parsing.census_nameable` would not print, every count of
    the census is withheld. Guarantees: returns the block, changed only
    so; a fixed function of its arguments; raises nothing; no I/O.
    """
    censuses = block["columns"]
    if not isinstance(censuses, list):
        return block
    for index in range(min(len(censuses), len(columns))):
        entry = censuses[index]
        numbers = columns[index]["n_numeric"] if "n_numeric" in columns[index] else None
        if not isinstance(entry, dict) or not isinstance(numbers, int):
            continue
        classes = entry["cell_classes"]
        if not isinstance(classes, dict):
            continue
        counted = classes[dialect.SHEET_CELL_NUMBER]
        if isinstance(counted, bool) or not isinstance(counted, int) or counted < 1:
            continue
        stored = numbers - counted
        if stored <= 0 or parsing.census_nameable([stored], [], floor):
            continue
        entry["cell_classes"] = {key: None for key in classes}
    return block


def stored_as_of(
    table: Table, settings: "taxonomy.Settings | None" = None
) -> "tuple[str, ...]":
    """How a workbook stores each column of a table, one word a column.

    `taxonomy.STORED_AS_DATES` where the workbook stores most of the
    column's present cells as dates (`workbook.stored_as_dates`; a cell
    is present where `taxonomy.missing_cells` under ``settings`` -- the
    defaults where None -- does not take it out, review item 2 of
    landing R3),
    `taxonomy.STORED_AS_CLOCKS` where it stores every present one as a
    clock (`workbook.stored_as_clocks`, asked of the spellings the
    reading itself took as no value, `Sheet.no_value`: the repair of
    review item 3 of landing R3), and the empty word otherwise and for
    every column of a delimited file (plan P4-D382).

    ONE ANSWER FOR THE CENSUS AND THE DESCRIPTION. `synthtwin profile`
    takes it once and hands it to both `taxonomy.population_census` and
    `build_document`, so the census reads a column under the word the
    description reads it under and its reading is handed over. Measured
    with the census reading every column as stored nowhere: the column
    it read was read twice, and `synthtwin profile` of 100,000 typed
    dates went from 8.0 s to 12.7 s of CPU.

    Guarantees: accepts a Table as the reader produced it and the
    settings; returns one word per column, in column order.
    Determinism: a fixed function of the two. Raises nothing. No I/O of
    any kind.
    """
    words: "list[str]" = []
    sheet = table.sheet
    read_under = taxonomy.Settings() if settings is None else settings
    # Every column by its name (lane SR, plan P4-D400): a table read in
    # groups holds no column list, and only a workbook's are asked.
    for place in range(len(table.column_names)):
        word = ""
        if (
            sheet is not None
            and place < len(sheet.classes)
            and place < len(sheet.formats)
        ):
            cells = reading.column_values(table, place)
            # THE MISSING WORDS ARE ASKED FOR ONLY WHERE A DATE IS STORED
            # (review item 2 of landing R3): they cost 1.6 to 1.8 s of
            # CPU over a million cells, and a column storing no date is
            # not stored as dates whatever they are.
            if workbook.stored_date_counts(
                cells, sheet.classes[place], sheet.formats[place]
            )[1] and workbook.stored_as_dates(
                cells, sheet.classes[place], sheet.formats[place],
                taxonomy.missing_cells(cells, read_under),
            ):
                word = taxonomy.STORED_AS_DATES
            elif workbook.stored_as_clocks(
                cells, sheet.classes[place], sheet.formats[place],
                sheet.no_value,
            ):
                word = taxonomy.STORED_AS_CLOCKS
        words += [word]
    return tuple(words)


def _without_held_back_names(block: "dict[str, object]") -> "dict[str, object]":
    """A column's block with its held-back levels' names set aside, its label half's too (lane CODES-2, P4-D471)."""
    kept: "dict[str, object]" = {}
    for key in block:
        value = block[key]
        if key == "held_back_names":
            continue
        if key == "labels" and isinstance(value, dict) and "held_back_names" in value:
            value = {inner: value[inner] for inner in value if inner != "held_back_names"}
        kept[key] = value
    return kept


def _held_back_named_here(
    name: str,
    answered_no: "list[str]",
    released: bool,
    held: "list[str]",
    identifiers: "list[str]",
    checked: "tuple[str, ...] | None",
    at_the_floor: bool,
) -> str:
    """How a column may name its held-back levels (lane CODES-2, plan P4-D471), or "".

    The validator's ``checked`` decides alone: the columns whose description
    named its pool are read `taxonomy.HELD_BACK_NAMED_CHECKED`, and no other.
    Else A COMMAND'S RULE, as the top-code and the date floor are (THE
    OWNER'S TABLE FLOOR, point (3) amended): nothing on a table under
    `parsing.TABLE_ROW_FLOOR` rows (``at_the_floor`` False, REQUIRED of
    every caller, read off the table it describes, so no threshold is
    skipped by omission: the orchestrator's LANE CODES-2 RULINGS 2 (3)),
    which the command refuses and the library describes byte for byte as
    before. And
    RULE U (c), the stand-ins page's ZS.1: nothing while a question offering
    `identifier` is open on the table (``released`` False), nor on a column a
    question holds (``held``) or described as a record number;
    `taxonomy.HELD_BACK_NAMED_ANSWERED` where the column is answered `no` to
    its Safe Harbor question; `taxonomy.HELD_BACK_NAMED_SCREENED` elsewhere.
    Guarantees: a fixed function of the seven. Raises nothing. No I/O.
    """
    if checked is not None:
        return taxonomy.HELD_BACK_NAMED_CHECKED if name in checked else ""
    if not at_the_floor or not released or name in held or name in identifiers:
        return ""
    if name in answered_no:
        return taxonomy.HELD_BACK_NAMED_ANSWERED
    return taxonomy.HELD_BACK_NAMED_SCREENED


def _names_its_pool(details: "dict[str, object]") -> bool:
    """Whether a column's block names its held-back levels, or its label half does (lane CODES-2, P4-D471)."""
    if "held_back_names" in details:
        return True
    half = details["labels"] if "labels" in details else None
    return isinstance(half, dict) and "held_back_names" in half


def _few_values_released(name: str, answered_no: "list[str]") -> bool:
    """Whether a few-valued column may list its numbers: `no` to its Safe Harbor question.

    Lane GG, plan P4-D440; the stand-ins page's ZS.4, "GG acts only after
    `no` to the Safe Harbor question". One question, one release.
    """
    return name in answered_no


def _rare_list_released(rare: bool, released: bool) -> bool:
    """Whether a list answered `no` is released under rule U (c) (lane GG, P4-D440).

    A list naming no rare value always is; one naming a rare value only
    where no question offering `identifier` is open on any column
    (``released``). Raises nothing.
    """
    return released or not rare
# The roles whose cells are never read as a coordinate: no cell, cells
# no number holds, dates and clock times (lane SH2, plan P4-D434).
_NO_COORDINATE_ROLES = (
    taxonomy.ROLE_EMPTY,
    taxonomy.ROLE_UNREPRESENTABLE,
    taxonomy.ROLE_DATETIME,
    taxonomy.ROLE_CLOCK,
)


# The roles a date in disguise is published by, as a level, a rung or a
# tail: among them it is read as a blank cell (plan P4-D446).
_DATED_VALUE_ROLES = taxonomy.SAFE_HARBOR_LEVEL_ROLES + (
    taxonomy.ROLE_COMPOUND,
    taxonomy.ROLE_CONTINUOUS,
    taxonomy.ROLE_COUNT,
)
# The roles a hold may not move a column out of into numbers beside labels:
# it would be read otherwise than its own cells are (plan P4-D446).
_DATED_LABEL_ROLES = (taxonomy.ROLE_CATEGORICAL, taxonomy.ROLE_LONG_TAIL)


def _reach_here(
    cells: "list[str]",
    dated: "list[str] | None",
    comma: bool,
    absent: "frozenset[str]",
    floor: int,
    levels: bool,
    padded: bool,
    mark: int = taxonomy.TOP_CODE,
    named: bool = False,
    said: bool = False,
    measured: bool = False,
) -> str:
    """A column's Safe Harbor reach (`taxonomy.safe_harbor_reach`), read on its cells as written (plan P4-D446).

    A ZIP is a ZIP whatever band its five figures lie in, so the ZIP reach
    reads the cells as written. Where they reach neither, the cells the
    date rule leaves (``dated``, its values that read as dates blank) are
    read for ages alone: ages beside day counts on more cells than the
    ages' strays allow are ages once the day counts are set aside (the
    orchestrator's LANE CZ-H RULINGS 5 (1): the date rule decides first,
    the top-code acts on the cells it leaves). Both read the column's
    ages in their unit, ``mark``, and ``named`` where its name or an
    answer says it holds ages (`taxonomy.safe_harbor_reach`, lane SH3);
    ``said`` where its name or an answer says so whatever holds its name
    meanwhile, so the units its cells write never take it out of the reach
    (lane HB3-a2, plan P4-D486, R); ``measured`` where its name names a
    measurement no age is, so no age reach reads it unless a cell names an
    age (lane RX-1, R3; `taxonomy.named_as_a_measurement`).
    """
    reach = taxonomy.safe_harbor_reach(
        cells, comma, absent, floor, levels, padded, mark, named, said=said, measured=measured
    )
    if reach or dated is None:
        return reach
    if taxonomy.safe_harbor_reach(
        dated, comma, absent, floor, levels, padded, mark, named, said=said, measured=measured
    ) == taxonomy.SAFE_HARBOR_AGES:
        return taxonomy.SAFE_HARBOR_AGES
    return reach


def _declared_as_dates(settings: taxonomy.Settings, name: str) -> bool:
    """Whether a person said a column holds dates: counted (`--date-count`, Q3) or written (`--date-column`, Q6).

    Its dates are then read under the product's date rules (P4-D433),
    declined ones held whole (P4-D406, NF127): the value rule of plan
    P4-D446 is not the one that reads them.
    """
    for column, _member in settings.forced_date_counts:
        if column == name:
            return True
    return name in settings.forced_date_columns


def _date_question_answered_no(
    described: taxonomy.ColumnProfile, declared_measurement: bool
) -> bool:
    """Whether question Q3 was put to a column and a person said it holds numbers (plan P4-D446).

    `measurement` is an answer to the question about dates where Q3 is the
    question its column is put (NF113 stands among its remarks); given to
    a question about record numbers, it says nothing about dates.
    """
    if not declared_measurement:
        return False
    for remark in described.remarks:
        if remark.form == taxonomy.REMARK_NUMBERS_COULD_BE_DATES:
            return True
    return False


def _keep_for_the_chain(
    kept: "dict[int, taxonomy.KeptSpellings]",
    place: int,
    held: taxonomy.HeldReading,
    described: taxonomy.ColumnProfile,
    identifiers: "list[str]",
) -> None:
    """Keep one column's reading for the chain where the chain reads it and the table's bounds hold it (lane CHs, plan P4-D462).

    A READING THE CHAIN NEVER READS IS NOT KEPT (lane CHs's repair 2, the
    orchestrator's LANE CHs RULINGS 7 (1)): where the chain's own
    classifier sets the column aside on what its description says
    (`chain.ineligible_reason`: free text and notes, an identifier, an
    empty or unrepresentable column, a role the chain does not read),
    nothing is built, decided here, where the reading is. Its effect is
    what the byte counter counts (MEASURED, the lane's second verify): a
    note column of 4,096 characters a row kept its 80,000 spellings,
    about 341.8 MB, at 80,000 rows until the chain's loop let them go
    unread, and its 29,384, about 125.5 MB, at 30,000; it keeps none now,
    and every description and private note is the bytes it was. The
    footprints are single runs whose spread on one head is as large as
    the differences first quoted between the heads (541 to 926 MB
    through the chain's stages at 80,000 rows against repair 1's
    949 to 955; 608.7 to 1,656.6 MB at 30,000 read one column a group),
    so none is shown to be the fix's effect. What is kept counts its
    retained bytes beside its spellings, against the table's bounds.

    THE TABLE'S ROOM BEFORE THE COLUMN (RULINGS 7 (2)): what the kept
    readings already hold is counted before this column is begun; none is
    begun where nothing is left, and one is built only into the room left
    (`taxonomy.keep_spellings` stops at its first spelling past it).
    """
    from synthtwin import chain

    if chain.ineligible_reason({"name": described.name, "role": described.role}, False, False, set(identifiers)) is not None:
        return
    spellings = 0
    retained = 0
    for place_kept in kept:
        spellings += len(kept[place_kept].spellings)
        retained += kept[place_kept].retained
    room_spellings = taxonomy.KEPT_SPELLINGS_A_TABLE - spellings
    room_bytes = taxonomy.KEPT_BYTES_A_TABLE - retained
    if room_spellings <= 0 or room_bytes <= 0:
        return
    spelled = taxonomy.keep_spellings(held, room_spellings, room_bytes)
    if spelled is not None:
        kept[place] = spelled


# -- values typed by a key (lane KV, plan P4-D487) ----------------------
#
# A LONG TABLE (a vital-signs export, a question-and-answer export, a lab
# export) holds its measurements in one value column V whose kind and
# scale a key column K decides: one row says `heart_rate` and `82`, the
# next `temperature_c` and `36.9`. Described as one column, V's values are
# a mixture of every measurement's, and the twin draws each apart from its
# key. THE READING (no word list, nothing learnt from a real table): a pair
# (K, V) is KEYED where K is read as labels (or held only because some of
# its values are held by too few people, read as its pool would be) with
# two keys or more that the floor's people hold, the key varies within a
# person, V is present on half the rows or more and holds five different
# values a common key or more on average, V does not decide K, and EITHER
# (A) each common key's cells are of ONE reading on nine in ten of them for
# keys covering four in five of the common keys' rows, two readings each
# leading keys of one row in twenty or more, OR (B) V reads as numbers on
# nine cells in ten or more, K has three common keys or more, and the
# share of the variance of the scale of V's numbers between the common
# keys is four in five or more. Then V is DESCRIBED KEY BY KEY: each common
# key's cells read by the product's own rule order as a column named by
# the key (`_key_block`), the rare keys' cells as one pooled block, and
# the cells of rows that hold no key as V's own block; the twin writes K
# first and each row's value from its key's block (method G8.3f).

# The readings of a value cell, in their published order (P4-D487).
_READ_NUMBER = 0
_READ_PAIR = 1
_READ_CLOCK = 2
_READ_DATE = 3
_READ_WORD = 4
_READ_TEXT = 5
_READ_NONE = 6
KEYED_READING_WORDS = (
    "numbers", "pairs of numbers", "clock times", "dates", "words", "texts",
)
# Each different value is read once, up to this many in the reading's memo.
_KEYED_MEMO = 65536
# A key column of fewer common keys than this that its values decide is
# their dependent, not their key (`_reads_as_a_key`).
_KEYED_FEW_KEYS = 6
# The roles a key column is read in: labels.
_KEYED_KEY_ROLES = (
    taxonomy.ROLE_CATEGORICAL,
    taxonomy.ROLE_LONG_TAIL,
    taxonomy.ROLE_BINARY,
)
# The value-column answer's meaning (the orchestrator's LANE KV RULINGS 1
# (3), K8, the owner's veto): `yes` to the value column's Safe Harbor
# question holds the key blocks of words, free text and dates and those
# whose key's name reads as an identifier element, and keeps the blocks
# of numbers, joined numbers and screened labels described. True gives
# back the meaning `yes` had before this lane: every key block held.
KEYED_YES_HOLDS_EVERY_BLOCK = False


def _a_clock_text(text: str) -> bool:
    """Whether a value is a clock time alone: one or two figures, `:`, two figures, seconds after it or not, `am`/`pm` or not (P4-D487's readings). Raises TypeError for a value that is not text."""
    if not isinstance(text, str):
        raise TypeError("a cell is text")
    body = text
    lowered = body.lower()
    for mark in (" am", " pm", "am", "pm", " a.m.", " p.m.", "a.m.", "p.m."):
        # The end compared by a slice (`endswith` takes only a value the
        # offline audit resolves, and a loop's mark is none).
        if len(lowered) > len(mark) and lowered[len(lowered) - len(mark):] == mark:
            body = body[: len(body) - len(mark)]
            break
    parts = body.split(":")
    if len(parts) < 2 or len(parts) > 3:
        return False
    if not (1 <= len(parts[0]) <= 2):
        return False
    for place, part in enumerate(parts):
        if place and len(part) != 2:
            return False
        for character in part:
            if not ("0" <= character <= "9"):
                return False
    return True


def _holds_a_plain_figure(text: str) -> bool:
    """Whether a text holds one of the figures 0 to 9."""
    for character in text:
        if "0" <= character <= "9":
            return True
    return False


def keyed_value_reading(cell: str) -> int:
    """The reading one value cell takes for the keyed pair's rule (plan P4-D487).

    A number the reader of record holds (`parsing.classify_number`); two
    such numbers joined by one `/` (`120/80`); a clock time alone
    (`14:32`, `2:05 pm`); a text a word of which is written as a date
    (`taxonomy.reads_as_a_date_or_clock`: `03/14/2024`, `2024-03`,
    `2024-01-05 09:15`); a word, one or two words holding no figure
    (`Normal`, `Room air`); else a text. A blank cell reads as none.
    Guarantees: a fixed function of the text; one of the seven reading
    numbers. Raises TypeError for a value that is not text. No I/O.
    """
    if not isinstance(cell, str):
        raise TypeError("a cell is text")
    text = parsing.trimmed(cell)
    if not text:
        return _READ_NONE
    if parsing.classify_number(text) == parsing.NUMBER:
        return _READ_NUMBER
    halves = text.split("/")
    if (
        len(halves) == 2
        and parsing.classify_number(halves[0]) == parsing.NUMBER
        and parsing.classify_number(halves[1]) == parsing.NUMBER
    ):
        return _READ_PAIR
    if _a_clock_text(text):
        return _READ_CLOCK
    words = text.split()
    if _holds_a_plain_figure(text):
        for word in words:
            if taxonomy.reads_as_a_date_or_clock(word):
                return _READ_DATE
        return _READ_TEXT
    return _READ_WORD if len(words) <= 2 else _READ_TEXT


def _tens(power: int) -> int:
    """Ten to a whole power of nought or more, by multiplication alone."""
    found = 1
    for _step in range(power):
        found = found * 10
    return found


def _to_the_eighth(value: int) -> int:
    """A whole number to the eighth power, by three squarings."""
    square = value * value
    fourth = square * square
    return fourth * fourth


# The scale of a number beyond this many figures is read as its cap.
_KEYED_SCALE_FIGURES = 40
_KEYED_SCALE_CAP = 8 * 140


def keyed_scale_step(cell: str) -> "int | None":
    """The scale of a number cell, EXACTLY: the eighths of an octave of 1 + |x|, floored (plan P4-D487's rule B), or None.

    The reader of record's exact triple (`parsing.exact_of_spelling`)
    gives 1 + |x| as a ratio of whole numbers, and the answer is the
    largest whole number s with 2 ** (s / 8) at most that ratio, found by
    comparing whole numbers alone (an eighth power against a power of
    two), so every computer reads the same step: no logarithm, no float.
    A number written with more than `_KEYED_SCALE_FIGURES` figures or so
    many places reads as `_KEYED_SCALE_CAP`. Guarantees: a fixed function
    of the text; None for a cell that is no number. Raises TypeError for
    a value that is not text. No I/O.
    """
    triple = parsing.exact_of_spelling(cell)
    if triple is None:
        return None
    _sign, digits, power = triple
    if len(digits) > _KEYED_SCALE_FIGURES or power > _KEYED_SCALE_FIGURES or power < -_KEYED_SCALE_FIGURES:
        return _KEYED_SCALE_CAP
    whole = 0
    for digit in digits:
        whole = whole * 10 + (ord(digit) - ord("0"))
    if power >= 0:
        top = whole * _tens(power) + 1
        bottom = 1
    else:
        bottom = _tens(-power)
        top = whole + bottom
    # THE OCTAVE, the largest whole o with bottom * 2 ** o at most top (top
    # is at least bottom): doubled until it passes, then halved back, by
    # shifts and comparisons of whole numbers alone.
    octave = 0
    above = 1
    while (bottom << above) <= top:
        octave = above
        above = above * 2
    while above - octave > 1:
        middle = (octave + above) // 2
        if (bottom << middle) <= top:
            octave = middle
        else:
            above = middle
    top_eighth = _to_the_eighth(top)
    bottom_eighth = _to_the_eighth(bottom)
    eighths = 0
    for step in range(1, 8):
        if top_eighth >= (bottom_eighth << (8 * octave + step)):
            eighths = step
    return min(_KEYED_SCALE_CAP, 8 * octave + eighths)


@dataclasses.dataclass(frozen=True)
class KeyedPair:
    """One pair read as keyed (plan P4-D487): the key column, the value column, the common keys and the readings seen."""

    key: str
    value: str
    common: "tuple[str, ...]"
    readings: "tuple[str, ...]"


def _key_levels(
    cells: "list[str]", absent: "frozenset[str]"
) -> "list[str]":
    """Each row's key as its folded label, or "" where the row holds no key.

    Each different cell is folded once and its label shared by every row
    that writes it (kept to `_KEYED_MEMO` cells), so the list holds one
    reference a row, not one new text a row: a key column's labels cost
    the list itself at 2,000,000 rows.
    """
    found: "list[str]" = []
    seen: "dict[str, str]" = {}
    for cell in cells:
        if cell in seen:
            found += [seen[cell]]
            continue
        if cell in absent or not parsing.trimmed(cell):
            level = ""
        else:
            level = parsing.folded(cell)
        if len(seen) < _KEYED_MEMO:
            seen[cell] = level
        found += [level]
    return found


def _common_keys(
    levels: "list[str]",
    people: "list[str] | None",
    floor: int,
) -> "tuple[str, ...]":
    """The keys the floor's people hold (or rows, where no column counts people), sorted."""
    holders: "dict[str, dict[str, bool]]" = {}
    rows: "dict[str, int]" = {}
    for place, level in enumerate(levels):
        if not level:
            continue
        rows[level] = (rows[level] if level in rows else 0) + 1
        if people is not None:
            if level not in holders:
                holders[level] = {}
            holders[level][people[place]] = True
    if people is None:
        return tuple(sorted(level for level in rows if rows[level] >= floor))
    return tuple(sorted(level for level in holders if len(holders[level]) >= floor))


def _varies_within_a_person(levels: "list[str]", people: "list[str]") -> bool:
    """Whether half the people with two rows or more meet two keys or more (a key fixed per person is no key).

    False where no person holds two rows: a table of one row a person
    holds no key that varies within a person, and none of its columns is
    a value column typed by a key (stated limit (h); the orchestrator's
    LANE KV RULINGS 3 (4), skeptic 1's item 5).
    """
    first: "dict[str, str]" = {}
    rows: "dict[str, int]" = {}
    two_keys: "dict[str, bool]" = {}
    for place, level in enumerate(levels):
        if not level:
            continue
        person = people[place]
        rows[person] = (rows[person] if person in rows else 0) + 1
        if person not in first:
            first[person] = level
        elif first[person] != level:
            two_keys[person] = True
    repeated = [person for person in rows if rows[person] >= 2]
    if not repeated:
        return False
    return 2 * len([person for person in repeated if person in two_keys]) >= len(repeated)


@dataclasses.dataclass
class KeyedCodes:
    """A value column's cells as codes of its different cells, and each key column's rows as codes of its common keys
    (lane SPEED-2M), made once for all the pairs `keyed_pairs_read` reads: ``values`` the codes (a list, or a byte a
    row below 256 different cells), ``cells`` each code's cell, ``keys`` each key column's codes by its place."""

    values: "bytes | list[int]"
    cells: "list[str]"
    keys: "dict[int, bytes | list[int]]"
    key_place: int = -1


# The most cells a count of code pairs holds.
_KEYED_PAIR_CELLS = 65536


def keyed_codes(v_cells: "list[str]") -> KeyedCodes:
    """A value column's cells as codes of its different cells, in the order first met."""
    code_of: "dict[str, int]" = {}
    cells: "list[str]" = []
    for cell in v_cells:
        if cell not in code_of:
            code_of[cell] = len(cells)
            cells += [cell]
    codes = [code_of[cell] for cell in v_cells]
    return KeyedCodes(bytes(codes) if len(cells) <= 256 else codes, cells, {})


def _keyed_counts_by_pairs(
    coded: KeyedCodes,
    k_levels: "list[str]",
    place_of: "dict[str, int]",
    width: int,
    v_absent: "frozenset[str]",
    memo: "dict[str, int]",
    scales: "dict[str, int | None]",
) -> "tuple[list[list[int]], list[int], int, int, int, list[int], list[int], int] | None":
    """The counts `_reads_as_a_key`'s pass makes, from the rows each pair of codes holds; None past 65,536 cells.

    A row's key code is its common key's place, ``width`` for a key that
    is not common (or none). Each different cell is read once (its
    reading, its scale step), as the pass reads it.
    """
    values = len(coded.cells)
    if values == 0 or (width + 1) * values > _KEYED_PAIR_CELLS:
        return None
    if coded.key_place not in coded.keys:
        at_codes = [place_of[level] if level in place_of else width for level in k_levels]
        coded.keys[coded.key_place] = bytes(at_codes) if width + 1 <= 256 else at_codes
    # ...counted here in whole numbers, one step a row (batch 4zz's merge: `arrays` names numpy, and a validate run
    # reaches this module, which must name none; the counts are the ones `arrays.joint_counts` made).
    counts = [0 for _cell in range((width + 1) * values)]
    key_codes = coded.keys[coded.key_place]
    value_codes = coded.values
    for row in range(min(len(key_codes), len(value_codes))):
        cell_at = key_codes[row] * values + value_codes[row]
        counts[cell_at] = counts[cell_at] + 1
    kinds = [[0 for _kind in range(_READ_NONE)] for _key in range(width)]
    key_rows = [0 for _key in range(width)]
    present = 0
    numbers = 0
    distinct = 0
    scale_count = [0 for _key in range(width)]
    scale_sum = [0 for _key in range(width)]
    scale_squares = 0
    for code in range(values):
        cell = coded.cells[code]
        for at in range(width):
            key_rows[at] = key_rows[at] + counts[at * values + code]
        if cell in v_absent:
            continue
        if cell in memo:
            kind = memo[cell]
        else:
            kind = keyed_value_reading(cell)
            if len(memo) < _KEYED_MEMO:
                memo[cell] = kind
        if kind == _READ_NONE:
            continue
        held = 0
        for at in range(width + 1):
            held = held + counts[at * values + code]
        if held == 0:
            continue
        present = present + held
        distinct = distinct + 1
        if kind == _READ_NUMBER:
            numbers = numbers + held
        step: "int | None" = None
        if kind == _READ_NUMBER:
            if cell in scales:
                step = scales[cell]
            else:
                step = keyed_scale_step(cell)
                if len(scales) < _KEYED_MEMO:
                    scales[cell] = step
        for at in range(width):
            rows = counts[at * values + code]
            if rows == 0:
                continue
            kinds[at][kind] = kinds[at][kind] + rows
            if step is not None:
                scale_count[at] = scale_count[at] + rows
                scale_sum[at] = scale_sum[at] + rows * step
                scale_squares = scale_squares + rows * step * step
    return kinds, key_rows, present, numbers, distinct, scale_count, scale_sum, scale_squares


def _reads_as_a_key(
    k_levels: "list[str]",
    common: "tuple[str, ...]",
    v_cells: "list[str]",
    v_absent: "frozenset[str]",
    memo: "dict[str, int]",
    scales: "dict[str, int | None]",
    coded: "KeyedCodes | None" = None,
) -> "tuple[str, ...] | None":
    """The readings a value column takes under its key, where the pair reads as keyed by rule A or B, or None (plan P4-D487).

    One pass over the rows reads rules A and B; each different value read
    once, in ``memo`` (its reading) and ``scales`` (its scale step), each
    kept to `_KEYED_MEMO` values. Every share is a whole-number
    comparison. ONLY WHERE A RULE READS THE PAIR AS KEYED is a second pass
    made, for the direction (`_the_value_decides_the_key`): a wide table of
    labels and numbers that no key types makes one pass a pair and keeps no
    value's keys (G4; the orchestrator's LANE KV RULINGS 3 (5), skeptic 1's
    item 7: the first pass held every different value's keys for every
    pair, 8.25 CPU seconds at 20,000 rows on a table of 12 label and 24
    number columns).

    THE SAME COUNTS FROM A COUNT OF CODE PAIRS (lane SPEED-2M). With
    ``coded`` (the value column's cells as codes of its different cells,
    and this key column's rows as codes of their common keys), where the
    pairs of codes hold at most 65,536 cells, the pass is one count of
    the rows each pair holds (whole numbers), and
    each count the pass makes is the sum of its pairs' rows: every count
    is a whole number, so the readings are the pass's, whichever way the
    rows are counted. Any other pair is read row by row as before.
    """
    place_of = {level: place for place, level in enumerate(common)}
    width = len(common)
    if coded is not None:
        counted = _keyed_counts_by_pairs(coded, k_levels, place_of, width, v_absent, memo, scales)
        if counted is not None:
            kinds_c, key_rows_c, present_c, numbers_c, distinct_c, count_c, sum_c, squares_c = counted
            return _keyed_decision(k_levels, common, v_cells, v_absent, memo, width, kinds_c, key_rows_c, present_c,
                                   numbers_c, distinct_c, count_c, sum_c, squares_c)
    kinds = [[0 for _kind in range(_READ_NONE)] for _key in range(width)]
    key_rows = [0 for _key in range(width)]
    present = 0
    numbers = 0
    distinct: "dict[str, bool]" = {}
    scale_count = [0 for _key in range(width)]
    scale_sum = [0 for _key in range(width)]
    scale_squares = 0
    for place in range(len(v_cells)):
        cell = v_cells[place]
        level = k_levels[place]
        at = place_of[level] if level in place_of else -1
        if at >= 0:
            key_rows[at] = key_rows[at] + 1
        if cell in v_absent:
            continue
        if cell in memo:
            kind = memo[cell]
        else:
            kind = keyed_value_reading(cell)
            if len(memo) < _KEYED_MEMO:
                memo[cell] = kind
        if kind == _READ_NONE:
            continue
        present = present + 1
        distinct[cell] = True
        if kind == _READ_NUMBER:
            numbers = numbers + 1
        if at < 0:
            continue
        kinds[at][kind] = kinds[at][kind] + 1
        if kind == _READ_NUMBER:
            if cell in scales:
                step = scales[cell]
            else:
                step = keyed_scale_step(cell)
                if len(scales) < _KEYED_MEMO:
                    scales[cell] = step
            if step is not None:
                scale_count[at] = scale_count[at] + 1
                scale_sum[at] = scale_sum[at] + step
                scale_squares = scale_squares + step * step
    return _keyed_decision(k_levels, common, v_cells, v_absent, memo, width, kinds, key_rows, present, numbers,
                           len(distinct), scale_count, scale_sum, scale_squares)


def _keyed_decision(
    k_levels: "list[str]",
    common: "tuple[str, ...]",
    v_cells: "list[str]",
    v_absent: "frozenset[str]",
    memo: "dict[str, int]",
    width: int,
    kinds: "list[list[int]]",
    key_rows: "list[int]",
    present: int,
    numbers: int,
    distinct: int,
    scale_count: "list[int]",
    scale_sum: "list[int]",
    scale_squares: int,
) -> "tuple[str, ...] | None":
    """`_reads_as_a_key`'s decision from the pass's counts: rules A and B, then the direction (whole numbers only)."""
    if not _enough_values(present, len(v_cells), distinct, width):
        return None
    covered = 0
    pure = 0
    leading = [0 for _kind in range(_READ_NONE)]
    seen_readings: "dict[int, bool]" = {}
    for at in range(width):
        cells_here = 0
        top_kind = 0
        top = -1
        for kind in range(_READ_NONE):
            cells_here = cells_here + kinds[at][kind]
            if kinds[at][kind] > top:
                top = kinds[at][kind]
                top_kind = kind
        covered = covered + key_rows[at]
        if cells_here == 0:
            continue
        seen_readings[top_kind] = True
        leading[top_kind] = leading[top_kind] + key_rows[at]
        if 10 * top >= 9 * cells_here:
            pure = pure + key_rows[at]
    rule_a = False
    if covered:
        leaders = [kind for kind in range(_READ_NONE) if 20 * leading[kind] >= covered]
        rule_a = _rule_a(len(leaders), pure, covered)
    numeric = 10 * numbers >= 9 * present
    rule_b = False
    if numeric:
        holding = [at for at in range(width) if scale_count[at]]
        if len(holding) >= 3:
            total = 0
            whole = 0
            for at in holding:
                total = total + scale_count[at]
                whole = whole + scale_sum[at]
            scaled = 1 << 64
            between = 0
            for at in holding:
                between = between + (scale_sum[at] * scale_sum[at] * scaled) // scale_count[at]
            middle = (whole * whole * scaled) // total
            between = between - middle
            spread = scale_squares * scaled - middle
            rule_b = _rule_b(between, spread)
    if not rule_a and not rule_b:
        return None
    if _the_value_decides_the_key(
        k_levels, common, v_cells, v_absent, memo, width < _KEYED_FEW_KEYS and not rule_b, numeric
    ):
        return None
    return tuple(
        KEYED_READING_WORDS[kind] for kind in range(_READ_NONE) if kind in seen_readings
    )


def _enough_values(present: int, rows: int, distinct: int, width: int) -> bool:
    """THE VALUES' CONDITION of the reading (plan P4-D487): the value column present on half the rows or more, and five different present values a common key or more (`_five_values_a_key`)."""
    return 2 * present >= rows and _five_values_a_key(distinct, width)


def _five_values_a_key(distinct: int, width: int) -> bool:
    """Whether a value column holds five different present values or more for each common key of a key column (plan P4-D487): read before any pass under that key (`keyed_pairs_read`) and in it (`_enough_values`)."""
    return distinct >= 5 * width


def _rule_a(leaders: int, pure: int, covered: int) -> bool:
    """RULE A of the reading (plan P4-D487): two readings or more each leading keys of a twentieth of the common keys' rows, and the keys of one reading on nine cells in ten holding four fifths of those rows."""
    return leaders >= 2 and 5 * pure >= 4 * covered


def _rule_b(between: int, spread: int) -> bool:
    """RULE B of the reading (plan P4-D487): four fifths of the variance of the scale steps or more between the common keys, the variance read in whole numbers."""
    return spread > 0 and 5 * between >= 4 * spread


# A number written with more figures or places than this is set aside by
# the direction's ranges (`_exact_ratio`).
_KEYED_RANGE_FIGURES = 40


def _exact_ratio(cell: str) -> "tuple[int, int] | None":
    """A number cell's exact value as a whole numerator over a whole denominator, or None (`parsing.exact_of_spelling`; one of more than `_KEYED_RANGE_FIGURES` figures or places is None). No float. Raises TypeError for a value that is not text. No I/O."""
    triple = parsing.exact_of_spelling(cell)
    if triple is None:
        return None
    sign, digits, power = triple
    if len(digits) > _KEYED_RANGE_FIGURES or power > _KEYED_RANGE_FIGURES or power < -_KEYED_RANGE_FIGURES:
        return None
    whole = 0
    for digit in digits:
        whole = whole * 10 + (ord(digit) - ord("0"))
    if power >= 0:
        return (sign * whole * _tens(power), 1)
    return (sign * whole, _tens(-power))


def _below(first: "tuple[int, int]", second: "tuple[int, int]") -> bool:
    """Whether one exact ratio is smaller than another (positive denominators), by whole numbers alone."""
    return first[0] * second[1] < second[0] * first[1]


def _the_value_decides_the_key(
    k_levels: "list[str]",
    common: "tuple[str, ...]",
    v_cells: "list[str]",
    v_absent: "frozenset[str]",
    memo: "dict[str, int]",
    few: bool,
    numeric: bool,
) -> bool:
    """Whether the key column is the value column's DEPENDENT, not its key: THE DIRECTION RULE (plan P4-D487), a second pass over the rows.

    THE VALUE DECIDES THE KEY where each different value stands under one
    key on 95 rows in 100 of the rows holding a key and a value. Then the
    key is the value's dependent, and the pair is not keyed:
    - where the key column holds fewer than `_KEYED_FEW_KEYS` common keys
      and rule B does not set the keys' scales apart (``few``): a code
      decides its type;
    - where the value column reads as numbers on nine cells in ten
      (``numeric``) and the common keys' ranges, ordered by their smallest
      number, do not overlap (each key's largest number at most the next
      key's smallest; keys holding no number set aside, two holding one at
      least) and TOUCH (each gap between neighbours at most a quarter of the
      wider one's span: a band's edge meets the next band's, where the
      scales of measurements stand apart), AT ANY NUMBER OF KEYS AND
      WHATEVER RULE B SAYS: a band or a
      class worked out from the number -- an age and its ten-year band, a
      body mass and its class, a quarter and its times -- is the number's
      dependent, and a pair of them read as keyed would put a question no
      physician can read and leave the number's ties to every other column
      to its band alone (the orchestrator's LANE KV RULINGS 4 (3), the
      statistics check's item 4).
    Each different value read once (``memo``, and its exact value in a memo
    of this pass), linear in the rows. Guarantees: a fixed function of its
    arguments. Raises nothing of its own. No I/O.
    """
    if not few and not numeric:
        return False
    place_of = {level: place for place, level in enumerate(common)}
    width = len(common)
    by_value: "dict[str, dict[str, int]]" = {}
    exact: "dict[str, tuple[int, int] | None]" = {}
    lowest: "list[tuple[int, int] | None]" = [None for _key in range(width)]
    highest: "list[tuple[int, int] | None]" = [None for _key in range(width)]
    for place in range(len(v_cells)):
        level = k_levels[place]
        if not level:
            continue
        cell = v_cells[place]
        if cell in v_absent:
            continue
        if cell in memo:
            kind = memo[cell]
        else:
            kind = keyed_value_reading(cell)
        if kind == _READ_NONE:
            continue
        if cell not in by_value:
            by_value[cell] = {}
        seen = by_value[cell]
        seen[level] = (seen[level] if level in seen else 0) + 1
        if not numeric or kind != _READ_NUMBER or level not in place_of:
            continue
        if cell in exact:
            value = exact[cell]
        else:
            value = _exact_ratio(cell)
            if len(exact) < _KEYED_MEMO:
                exact[cell] = value
        if value is None:
            continue
        at = place_of[level]
        low = lowest[at]
        high = highest[at]
        if low is None or _below(value, low):
            lowest[at] = value
        if high is None or _below(high, value):
            highest[at] = value
    decided = 0
    keyed_rows = 0
    for cell in by_value:
        counts = by_value[cell]
        top = 0
        for level in counts:
            keyed_rows = keyed_rows + counts[level]
            if counts[level] > top:
                top = counts[level]
        decided = decided + top
    if keyed_rows == 0 or 20 * decided < 19 * keyed_rows:
        return False
    if few:
        return True
    ranges: "list[tuple[tuple[int, int], tuple[int, int]]]" = []
    for at in range(width):
        low = lowest[at]
        high = highest[at]
        if low is not None and high is not None:
            ranges += [(low, high)]
    if len(ranges) < 2:
        return False
    # ...ORDERED BY THEIR SMALLEST NUMBER, read exactly: every denominator is
    # a power of ten no larger than `_KEYED_RANGE_FIGURES` places, so each
    # smallest number scaled to that one denominator is a whole number.
    scale = _tens(_KEYED_RANGE_FIGURES)
    ordered = [
        pair for _low, _at, pair in sorted((one[0][0] * (scale // one[0][1]), at, one) for at, one in enumerate(ranges))
    ]
    for place in range(1, len(ordered)):
        low, high = ordered[place]
        before_low, before_high = ordered[place - 1]
        if _below(low, before_high):
            return False
        # ...AND THEY TOUCH, as a band touches the next: the gap between
        # two neighbours is at most a quarter of the wider one's span (ages
        # 0 to 9 and 10 to 19: a gap of 1 beside spans of 9; body masses
        # 18.5 to 24.9 and 25.0 to 29.9: a gap of 0.1). Measurements of their
        # own scales stand apart (potassium 3.4 to 4.5, hemoglobin 10.7 to
        # 14.9, glucose 95.3 to 124.3: gaps of 6.2 and 80.4) and stay keyed.
        gap = (low[0] * before_high[1] - before_high[0] * low[1], low[1] * before_high[1])
        wide = (high[0] * low[1] - low[0] * high[1], high[1] * low[1])
        wide_before = (
            before_high[0] * before_low[1] - before_low[0] * before_high[1],
            before_high[1] * before_low[1],
        )
        if _below(wide, wide_before):
            wide = wide_before
        if _below((wide[0], 4 * wide[1]), gap):
            return False
    return True


def _reads_as_dates_or_clocks(levels: "list[str]", cells: "list[str]") -> bool:
    """Whether half a key column's present cells or more read as dates or clock times (a period or a time is no key)."""
    present = 0
    dated = 0
    for place, level in enumerate(levels):
        if not level:
            continue
        present = present + 1
        kind = keyed_value_reading(cells[place])
        if kind == _READ_DATE or kind == _READ_CLOCK:
            dated = dated + 1
    return present > 0 and 2 * dated >= present


def _value_census(
    v_cells: "list[str]", v_absent: "frozenset[str]", memo: "dict[str, int]"
) -> int:
    """The number of different present values of a column some key column could type, or 0 where none could (plan P4-D487).

    One pass, each different value read once into ``memo`` (kept to
    `_KEYED_MEMO` values, the passes under each key reading it after).
    EXACT, by `_reads_as_a_key`'s own conditions, which it reads over
    every row whatever the key: a key of two common keys or more needs
    half the rows present and five different present values a common key
    (ten at least), and either two readings among the present cells (rule
    A: two readings each leading keys) or numbers on nine present cells in
    ten (rule B). A column that misses one is typed by no key column, so
    no pass under a key is made over it -- a questionnaire's items, words
    of a few levels each, are read once, not once a key column (a wide
    export of 300 items made 90,000 passes). Guarantees: a fixed function
    of the cells and the absent spellings. Raises nothing. No I/O.
    """
    present = 0
    numbers = 0
    kinds: "dict[int, bool]" = {}
    distinct: "dict[str, bool]" = {}
    for cell in v_cells:
        if cell in v_absent:
            continue
        if cell in memo:
            kind = memo[cell]
        else:
            kind = keyed_value_reading(cell)
            if len(memo) < _KEYED_MEMO:
                memo[cell] = kind
        if kind == _READ_NONE:
            continue
        present = present + 1
        distinct[cell] = True
        kinds[kind] = True
        if kind == _READ_NUMBER:
            numbers = numbers + 1
    if 2 * present < len(v_cells) or len(distinct) < 10:
        return 0
    if len(kinds) < 2 and 10 * numbers < 9 * present:
        return 0
    return len(distinct)


def keyed_pairs_read(
    table: Table,
    blocks: "list[dict[str, object]]",
    absent: "list[tuple[str, ...]]",
    people: "list[str] | None",
    excluded: "frozenset[str]",
    held_in_people: "frozenset[str]",
    floor: int,
) -> "list[KeyedPair]":
    """The pairs of columns read as keyed (plan P4-D487), each value column once, in the table's column order.

    ``blocks`` the described columns, ``absent`` each one's absent
    spellings, ``people`` each row's person (merged keys of the first
    column that counts people) or None, ``excluded`` the columns no pair
    takes (the person columns), ``held_in_people`` the columns held only
    because some of their values are held by too few people (read as
    their pool in people would be). A value column typed by two key
    columns takes the one with the most common keys, the earlier on a
    tie. Linear in the rows for each pair read; each different value of
    a value column read once; a column no key could type
    (`_value_census`) read once and under no key, before any key
    column's labels are held. Guarantees: a fixed function of its
    arguments. Raises nothing of its own. No I/O beyond the table's own
    access (`reading.column_values`).

    NO PAIR WITHOUT PEOPLE WHO REPEAT: where no column counts people
    (``people`` None: no subject column repeats, the command having set
    aside a person column that never repeats) or no person holds two
    rows, no pair is read -- a table of one row a person holds no key that
    varies within a person (stated limit (h); the orchestrator's LANE KV
    RULINGS 3 (4), skeptic 1's item 5: a visit type setting a duration's
    scale on 1,600 rows of 1,600 people was read as keyed).
    """
    if people is None:
        return []
    names = [f"{block['name']}" for block in blocks]
    if not any(
        names[place] not in excluded
        and (block["role"] in _KEYED_KEY_ROLES or names[place] in held_in_people)
        for place, block in enumerate(blocks)
    ):
        return []
    # THE COLUMNS SOME KEY COULD TYPE (`_value_census`, exact), each read
    # once before any key column's labels are held: a wide table of labels
    # that no key types holds none of them and makes no pass under a key.
    census: "dict[int, tuple[int, dict[str, int]]]" = {}
    for place, block in enumerate(blocks):
        if names[place] in excluded or block["role"] == taxonomy.ROLE_EMPTY:
            continue
        seen: "dict[str, int]" = {}
        distinct = _value_census(reading.column_values(table, place), frozenset(absent[place]), seen)
        if distinct:
            census[place] = (distinct, seen)
    if not census:
        return []
    keys: "list[tuple[int, list[str], tuple[str, ...]]]" = []
    for place, block in enumerate(blocks):
        name = names[place]
        if name in excluded:
            continue
        if block["role"] not in _KEYED_KEY_ROLES and name not in held_in_people:
            continue
        key_cells = reading.column_values(table, place)
        levels = _key_levels(key_cells, frozenset(absent[place]))
        common = _common_keys(levels, people, floor)
        if len(common) < 2:
            continue
        if not _varies_within_a_person(levels, people):
            continue
        if _reads_as_dates_or_clocks(levels, key_cells):
            continue
        keys += [(place, levels, common)]
        key_cells = []
    if not keys:
        return []
    read: "list[KeyedPair]" = []
    # Each key column's rows as codes of its common keys, made once for every value column (lane SPEED-2M).
    key_codes: "dict[int, bytes | list[int]]" = {}
    for place in sorted(census):
        name = names[place]
        distinct, memo = census[place]
        value_cells: "list[str]" = []
        scales: "dict[str, int | None]" = {}
        # The value column's cells as codes, made once for every key column it is read under (lane SPEED-2M).
        coded: "KeyedCodes | None" = None
        for key_place, levels, common in keys:
            # ...under no key of more common keys than a fifth of its values.
            if key_place == place or not _five_values_a_key(distinct, len(common)):
                continue
            if not value_cells:
                value_cells = reading.column_values(table, place)
                coded = keyed_codes(value_cells)
                coded.keys = key_codes
            if coded is not None:
                coded.key_place = key_place
            readings = _reads_as_a_key(levels, common, value_cells, frozenset(absent[place]), memo, scales, coded)
            if readings is not None:
                read += [KeyedPair(names[key_place], name, common, readings)]
        value_cells = []
        coded = None
    # A KEY COLUMN IS NO PAIR'S VALUE COLUMN (a unit beside a lab's test
    # reads as a key of the test names: the test is the key of the result),
    # and each value column takes one key column, the one of the most
    # common keys, the earlier in the table on a tie.
    keyed_columns = {pair.key: True for pair in read}
    found: "list[KeyedPair]" = []
    for place in range(len(names)):
        best: "KeyedPair | None" = None
        for pair in read:
            if pair.value != names[place] or pair.value in keyed_columns:
                continue
            if best is None or len(pair.common) > len(best.common):
                best = pair
        if best is not None:
            found += [best]
    return _one_value_a_key(found)


def _one_value_a_key(pairs: "list[KeyedPair]") -> "list[KeyedPair]":
    """The pairs read, each key column typing ONE value column, the first in the table (batch 4t's fix round, item 4; contract KV1: a key column's `keyed` names one value column).

    A second value column beside the same key -- a copy of the first, two
    results of one test -- is described as an ordinary column: its pair
    overwrote the key column's `keyed`, and the loader refused the
    description the command wrote (Codex's 24,000-row table with
    `secondary_value` a copy of `item_value`). Guarantees: the pairs in
    their order, less every later pair of a key already taken. Raises
    nothing. No I/O.
    """
    taken: "dict[str, bool]" = {}
    kept: "list[KeyedPair]" = []
    for pair in pairs:
        if pair.key in taken:
            continue
        taken[pair.key] = True
        kept += [pair]
    return kept


@dataclasses.dataclass(frozen=True)
class _KeyedAsked:
    """What the value column's answers say for its key blocks (plan P4-D487, K7 and K8).

    ``safe_no``: `no` to the value column's Safe Harbor question, which
    frees a key block's pool in people and the key blocks that question
    lists (`_listed_by_the_answer`), held while it is open or answered
    `yes`; ``safe_yes``: `yes` to EITHER question put to the value column
    that carries the keyed clause (its Safe Harbor question, or its
    question about values that read as dates: both ask whether a value
    could name a person, and the command passes the `yes` of each), which
    HOLDS what the clause lists -- its blocks of words, free text, dates
    and times of day, its dated values and its pool -- WHATEVER ELSE IS
    ANSWERED: ANY YES HOLDS, two answers to one question that differ hold
    (the orchestrator's LANE KV RULINGS 6 (1), HIPAA first; the scoped
    verify of repair 1: the Safe Harbor answer corrected to `yes` after
    the question about dates was answered `no` published 25 towns and 10
    family names on 1,939 twin cells each, where the base held the column
    whole); ``dates_no``: `no` to its question about
    values that read as dates, which frees every key block's dates and,
    as that question's words (the Safe Harbor rule's) say when it carries
    the keyed clause, the other listed blocks and the pools in people;
    ``dates_held``: the value column's values that
    read as dates are held in this description (that question open or
    answered `yes`), so its date blocks wait for that question whatever
    the Safe Harbor question was answered; ``question_put``: a question
    carrying the keyed clause is put to the value column (its Safe Harbor
    question or its question about values that read as dates, open or
    answered), the listed blocks waiting for it only then -- a value column
    put neither describes them, as its wide column is described (lane KV's
    repair 1: a lab table's blocks of labels were held with no question to
    answer); the declarations the value column carries, which each key
    block carries too; whether no question offering `identifier` is open on
    the table (rule U (c)); and the reference year.
    """

    safe_no: bool
    safe_yes: bool
    dates_no: bool
    dates_held: bool
    question_put: bool
    code: bool
    measurement: bool
    comma: bool
    kept_identity: bool
    released: bool
    harbor_year: int
    # ...and whether the value column is one `made_up_spellings_named` named
    # (batch 4t's fix round, item 1; plan P4-D489): its key blocks of numbers
    # too large or too small to hold are spelled one letter or figure wider.
    made_up: bool = False


def _both_readings(text: str) -> "tuple[str, ...]":
    """A key's name or a level as written, and as written with every character that prints nothing set aside (`taxonomy.printed_reading`): THE DOUBLE READING (plan P4-D487).

    Every reader this lane calls on a key's name or a key block's level --
    the readers of column names, lane CZ-E's identifier words, lane CZ-F's
    persons' names, the sentence reader -- reads it both ways and refuses
    it where EITHER reading is read (the orchestrator's LANE KV RULINGS 1
    (4) and 3 (3), LANE CODES-2 RULINGS 8 (2); skeptic 1's item 3: one
    zero-width space inside `Dr.` or `wife` took 990 of 5,870 titled names
    and 1,680 of 8,840 names beside a relative's word past every road).
    Guarantees: a fixed function of the text; the written reading first.
    Raises TypeError where it is no text. No I/O.
    """
    bare = taxonomy.printed_reading(text)
    return (text,) if bare == text else (text, bare)


def _key_names_an_identifier(name: str) -> bool:
    """Whether a key's name, read both ways (`_both_readings`), reads as an identifier element, by the product's own readers of column names (plan P4-D487, K8)."""
    for written in _both_readings(name):
        if (
            asking.named_as_a_key(written)
            or asking.names_a_person(written)
            or taxonomy.named_as_a_place(written)
            or taxonomy.named_as_a_coordinate(written)
            or taxonomy.named_as_an_address_part(written)
            or taxonomy.named_as_device_numbers(written)
            or taxonomy.named_as_persons_names(written)
        ):
            return True
    return False


def _a_persons_detail(text: str) -> bool:
    """Whether a text, read both ways (`_both_readings`), is read by lane CZ-F's persons' names or lane CZ-E's identifier words."""
    for written in _both_readings(text):
        if taxonomy.a_persons_name(written) or taxonomy.identifier_words_form(written):
            return True
    return False


def _read_as_identifiers(block: "dict[str, object]", name: str) -> bool:
    """Whether a key block's key name reads as an identifier element, or one of its published levels reads as a person's name or an identifier form (lanes CZ-F's and CZ-E's readers), each read both ways (`_both_readings`): HELD WHATEVER IS ANSWERED (plan P4-D487, HIPAA first).

    The value column's `no` is an answer about the column as a whole, given
    before any measurement's own values were shown: a measurement whose name
    or values the readers read as a person's details is freed by no answer
    in this lane (the per-key checklist is lane KV-b's), so a careless `no`
    publishes no more than the column-wide reading of the base held.
    """
    if _key_names_an_identifier(name):
        return True
    levels = block["levels"] if "levels" in block else []
    if not isinstance(levels, list):
        return False
    for entry in levels:
        if not isinstance(entry, dict):
            continue
        spellings = [f"{entry['label']}"]
        variants = entry["variants"] if "variants" in entry else None
        if isinstance(variants, dict):
            spellings += [f"{spelling}" for spelling in variants]
        for spelling in spellings:
            if _a_persons_detail(spelling):
                return True
    return False


# The roles of a key block the value column's Safe Harbor `yes` keeps
# described (`_listed_by_the_answer`): numbers (a number written with one
# shared unit among them), joined numbers and numbers with labels.
_KEYED_DESCRIBED_ROLES = (
    taxonomy.ROLE_COUNT,
    taxonomy.ROLE_CONTINUOUS,
    taxonomy.ROLE_UNREPRESENTABLE,
    taxonomy.ROLE_AFFIXED,
    taxonomy.ROLE_JOINED,
    taxonomy.ROLE_COMPOUND,
)


def _listed_by_the_answer(block: "dict[str, object]", name: str) -> bool:
    """Whether the value column's Safe Harbor `yes`, and that question while it is open, holds this key block (plan P4-D487, K8 and its condition, as ruled).

    LISTED: every block but those of numbers (one shared unit allowed),
    joined numbers and numbers with labels (`_KEYED_DESCRIBED_ROLES`) -- a
    block of a label role (categories, a long tail, two values, one
    value), of free text, of dates or of clock times -- and every block
    whose key's name, read both ways, reads as an identifier element
    (`_key_names_an_identifier`). A block of labels is listed
    WHATEVER ITS LEVELS: one-word towns and surnames under a coded question
    key pass every screen of a level, as they do in a wide column, and the
    truthful `yes` described them (25 towns and 10 surnames on 1,939 twin
    cells; the orchestrator's LANE KV RULINGS 3 (2), skeptic 1's item 2).
    An empty block, or one already held, holds nothing more.
    `KEYED_YES_HOLDS_EVERY_BLOCK` lists every block (the meaning `yes` had
    before this lane). Guarantees: a fixed function of the two. Raises
    nothing. No I/O.
    """
    if KEYED_YES_HOLDS_EVERY_BLOCK or _key_names_an_identifier(name):
        return True
    role = block["role"]
    return role not in _KEYED_DESCRIBED_ROLES and role not in (
        taxonomy.ROLE_EMPTY,
        taxonomy.ROLE_IDENTIFIER,
    )


def _sub_table(
    table: Table,
    name: str,
    cells: "list[str]",
    subjects: "list[tuple[str, list[str]]]",
) -> "tuple[Table, list[str]]":
    """A table of one value column named ``name`` first, and the person columns beside it, each cut to the same rows; and the person columns' names in it."""
    names = [name]
    columns = [cells]
    people: "list[str]" = []
    for subject, subject_cells in subjects:
        written = subject
        while written in names:
            written = written + "_"
        names += [written]
        columns += [subject_cells]
        people += [written]
    return (
        Table(
            column_names=names,
            columns=columns,
            n_rows=len(cells),
            encoding=table.encoding,
            used_fallback_encoding=table.used_fallback_encoding,
            header_source=table.header_source,
            header_evidence=table.header_evidence,
        ),
        people,
    )


def _key_block(
    table: Table,
    settings: taxonomy.Settings,
    name: str,
    cells: "list[str]",
    subjects: "list[tuple[str, list[str]]]",
    asked: _KeyedAsked,
    pooled: bool,
    owner: str = "",
    pools: "list[str] | None" = None,
    own: str = "",
    seen: "list[str] | None" = None,
) -> "dict[str, object]":
    """One key block: a key's cells described AS A COLUMN NAMED BY THE KEY (plan P4-D487, rule 0d; K2, K7, K8).

    ITS OWN QUESTION'S ANSWER (lane IN-4c, plan P4-D514): ``own`` is the
    answer the person gave this block's own question (`measurements_asked`
    of the questions file), or empty: `measurement` or `code` declares the
    block so, as the value column's declaration would (no question
    offering `identifier` holds it then; the age reach, the ZIP reach and
    every Safe Harbor hold stand); `identifier` holds it whatever else is
    answered. The caller hands it an answer only where the twin checks do
    not read the block's cells as an identifier column. ``seen``: where
    the block is held by a question offering `identifier` it would be put
    (and by no age reach), that question's words are added to it.

    The cells and each person column's cells on the key's rows make a
    table of their own, described by `build_document` under the command's
    rules: the floor counted in that key's people, every within-column
    rule, every Safe Harbor rule a column of that name would meet (its
    name read as the column's), the count of dates as at the table floor
    (``long_table_dates``), no name of a value too few hold (that is lane
    KV-b's). A KEY BLOCK PUTS NO QUESTION: where a column of that name and
    those values would be held until a question is answered -- a question
    offering `identifier`, a Safe Harbor question, the question about
    values that read as dates -- the block is described in that question's
    unanswered state (held, its twin made up in its own layouts), except
    where the value column's answers settle it (`_KeyedAsked`): its dates
    answer governs the block's dates, its Safe Harbor `no` the block's pool
    in people, its `yes` holds the blocks it lists. ``pooled``: the rare
    keys' pooled block, read with the value column's own name.
    Guarantees: a fixed function of its arguments; the block as the
    describe wrote it. Raises what `build_document` raises. No I/O.
    """
    sub, people = _sub_table(table, name, cells, subjects)
    # ...AT THE WHOLE TABLE'S CEILING OF CATEGORIES (`keyed_settings`).
    under = keyed_settings(settings, table.n_rows, tuple(people), owner, name)
    storage = tuple("" for _column in sub.column_names)
    codes = [name] if asked.code or own == asking.ANSWER_CODE else []
    measurements = [name] if asked.measurement or own == asking.ANSWER_MEASUREMENT else []
    commas = [name] if asked.comma else []
    kept = [name] if asked.kept_identity else []
    # The block's values that read as dates are freed by `no` to the question
    # about them, never beside a `yes` (ANY YES HOLDS, `_KeyedAsked`).
    dates_freed = asked.dates_no and not asked.safe_yes
    # A block of numbers too large or too small to hold, of a value column
    # `made_up_spellings_named` named (batch 4t's fix round, item 1): spelled
    # one letter or figure wider, NF139, as its own block would be.
    wider: "list[str]" = []

    def described(
        unanswered: "list[str]",
        safe_no: "list[str]",
        dated_held: "tuple[str, ...]",
        five: "list[str] | None",
        reasons: "dict[str, str] | None",
        ages: "list[str] | None",
        dated: "list[str] | None",
    ) -> "dict[str, object]":
        return build_document(
            sub,
            under,
            # ...a block answered `identifier` described as a column so
            # declared (lane IN-4c, plan P4-D514).
            list(people) + ([name] if own == asking.ANSWER_IDENTIFIER else []),
            codes,
            measurements,
            commas,
            stored_as=storage,
            unanswered=unanswered,
            subjects=list(people),
            top_code=True,
            safe_harbor_no=safe_no,
            five_figures=five,
            ages_held=ages,
            rare_values_released=asked.released,
            harbor_year=asked.harbor_year,
            harbor_reasons=reasons,
            kept_identities=kept,
            dated_values=dated,
            dated_held=dated_held,
            dated_values_no=[name] if dates_freed else [],
            long_table_dates=True,
            names_checked_only=(),
            people_whatever_their_number=True,
            made_up_held=list(wider) if wider else None,
        )

    five: "list[str]" = []
    reasons: "dict[str, str]" = {}
    ages: "list[str]" = []
    dated: "list[str]" = []
    first = described([], [], (), five, reasons, ages, dated)
    block = _first_block(first)
    if asked.made_up and block["role"] == taxonomy.ROLE_UNREPRESENTABLE:
        wider += [name]
        five, reasons, ages, dated = [], {}, [], []
        first = described([], [], (), five, reasons, ages, dated)
        block = _first_block(first)
    # THE HOLDS, IN THEIR UNANSWERED STATE (K7): a question offering
    # `identifier` the column would be put, a Safe Harbor hold, ages held.
    # ...THE VALUE COLUMN'S DECLARATION reaching the block as it reaches a
    # wide column: a key block of a column declared a measurement or a code
    # is put no question offering `identifier` for its numbers (the
    # orchestrator's LANE KV RULINGS 4 (2), the statistics check's item 3:
    # sodium's three-figure results were made up at 901 to 999 whatever was
    # declared). The age reach, the ZIP reach and every Safe Harbor hold
    # stand as they are.
    # ...AND THE BLOCK'S OWN ANSWER (lane IN-4c, plan P4-D514): `measurement`
    # or `code` declares it, as the value column's declaration would;
    # `identifier` holds it.
    declared = asked.code or asked.measurement or bool(codes) or bool(measurements)
    holding = name not in ages and _asked_as_an_identifier(sub, first, under, people, name, declared)
    hold = name in ages or holding or own == asking.ANSWER_IDENTIFIER
    if seen is not None and holding:
        question = _identifier_question(sub, first, under, people, name, declared)
        if question is not None:
            seen += [question.shape]
    pool_only = False
    if name in five:
        reason = reasons[name] if name in reasons else ""
        pool_only = (
            reason == taxonomy.HELD_LEVELS_OF_FEW_PEOPLE
            and "top_coded" not in block
            and "top_coded_year" not in block
        )
        # ...a pool counted in people only after `no` to the question put to
        # the value column (its Safe Harbor question, or its question about
        # values that read as dates, whose words are the Safe Harbor rule's),
        # and never while a question offering `identifier` is open on the
        # table (rule U (c)).
        hold = hold or not _pool_released(asked, pool_only)
    # A BLOCK THE READERS READ AS A PERSON'S DETAILS is held whatever is
    # answered (`_read_as_identifiers`); THE OTHER BLOCKS THE VALUE COLUMN'S
    # SAFE HARBOR QUESTION LISTS are held until the question put to the
    # value column that carries the keyed clause -- its Safe Harbor
    # question, or its question about values that read as dates -- is
    # answered `no` (K8, HIPAA first: unanswered is that question's own
    # state, as the value column was held whole while it was open); the
    # blocks of numbers, joined numbers and screened labels are described
    # whatever the answer.
    # (A block of dates waits for the question about values that read as
    # dates wherever that question holds them: open, or answered `yes`.)
    # ANY YES HOLDS (``safe_yes``, LANE KV RULINGS 6 (1)): a `yes` to either
    # question holds every listed block, the dates too, whatever `no` the
    # other was given.
    if not hold and _read_as_identifiers(block, name):
        hold = True
    if not hold and _listed_by_the_answer(block, name):
        if block["role"] == taxonomy.ROLE_DATETIME or "time_grain" in block:
            hold = asked.safe_yes or (not asked.dates_no and (asked.dates_held or not asked.safe_no))
        else:
            hold = asked.question_put and (asked.safe_yes or not (asked.safe_no or asked.dates_no))
    if hold:
        held_as = [] if own == asking.ANSWER_IDENTIFIER else [name]
        return _first_block(described(held_as, [], (), None, None, None, None))
    if _pool_released(asked, pool_only):
        pooled_block = _first_block(described([], [name], (), None, None, None, None))
        if pools is not None:
            pools += [name]
        return pooled_block
    # ...a described block's values that read as dates are read as blank
    # cells while the question about them holds them, and after any `yes`.
    if name in dated and not dates_freed:
        return _first_block(described([], [], (name,), None, None, None, None))
    return block


def _pool_released(asked: _KeyedAsked, pool_only: bool) -> bool:
    """Whether a key block held only because some of its values are held by too few people is described with its pool counted in people (plan P4-D487, K8): after `no` to the value column's Safe Harbor question or its question about values that read as dates, NEVER after a `yes` to either (ANY YES HOLDS, LANE KV RULINGS 6 (1)), and never while a question offering `identifier` is open on the table (rule U (c))."""
    return pool_only and (asked.safe_no or asked.dates_no) and not asked.safe_yes and asked.released


def keyed_settings(
    settings: taxonomy.Settings,
    n_rows: int,
    people: "tuple[str, ...]",
    own: str = "",
    inner: str = "",
) -> taxonomy.Settings:
    """The settings a key block is described under (plan P4-D487): the table's, its person columns those of the key's own table, the value column's clocks, centuries and dates carried to the block's name, and its ceiling of categories THE WHOLE TABLE'S.

    A key's rows are a part of the table, and the ceiling of a set of
    categories is a share of the rows (`taxonomy.categories_ceiling`): a
    key of 27 rows writing five words would read as free text, which
    publishes nothing, where the same words in the table's own column read
    as categories. So the key's floor of categories is the whole table's
    ceiling, which the loader reads back the same way (`contract`'s key
    blocks). Guarantees: a fixed function of the three. Raises nothing.
    No I/O.
    """
    return dataclasses.replace(
        settings,
        person_columns=people,
        categorical_floor=taxonomy.categories_ceiling(n_rows, settings),
        forced_twelve_hour_clocks=(inner,) if own in settings.forced_twelve_hour_clocks else (),
        century_windows=tuple((inner, year) for name, year in settings.century_windows if name == own),
        forced_date_columns=(inner,) if own in settings.forced_date_columns else (),
        forced_date_counts=tuple((inner, member) for name, member in settings.forced_date_counts if name == own),
    )


def _first_block(document: "dict[str, object]") -> "dict[str, object]":
    """The first column block of a description `build_document` wrote."""
    blocks = document["columns"]
    if not isinstance(blocks, list) or not blocks or not isinstance(blocks[0], dict):
        raise ValueError("synthtwin internal check: a key block was described without its column")
    return blocks[0]


def _asked_as_an_identifier(
    table: Table,
    document: "dict[str, object]",
    settings: taxonomy.Settings,
    people: "list[str]",
    name: str,
    declared: bool = False,
) -> bool:
    """Whether the questions `synthtwin profile` puts would hold the column until answered (`questions_of`, `asking.unanswered_identities`).

    The command's own rule: a question offering `identifier` put to the
    column and open holds it, its checklist entry does not; a column
    ``declared`` a measurement or a code is among the columns answered
    before (the command's `already_answered`), so no such question is put
    to it, as to a wide column so declared.
    """
    return _identifier_question(table, document, settings, people, name, declared) is not None


def _identifier_question(
    table: Table,
    document: "dict[str, object]",
    settings: taxonomy.Settings,
    people: "list[str]",
    name: str,
    declared: bool = False,
) -> "asking.Question | None":
    """The question `synthtwin profile` would put that holds the column until answered, or None (`_asked_as_an_identifier`'s rule).

    The first question offering `identifier` put to the column, where
    that question holds it (`asking.unanswered_identities`): its words are
    what a key block's own question says it saw (lane IN-4c, plan
    P4-D514). Guarantees: a fixed function of its arguments. Raises what
    `questions_of` raises. No I/O beyond the table's own access.
    """
    asked = questions_of(
        table,
        document,
        settings,
        list(people) + ([name] if declared else []),
        (),
        tuple("" for _column in table.column_names),
        None,
        None,
        asking.DateColumnsSeen(),
        False,
        (),
        False,
    )
    put = asked.asked + list(asked.codes_seen.questions)
    if name not in asking.unanswered_identities(put, document, tuple(people)):
        return None
    for question in put:
        if question.name == name and asking.offers_identifier(question):
            return question
    return None


def _rare_key_spellings(
    levels: "list[str]", cells: "list[str]", common: "frozenset[str]"
) -> "tuple[str, ...]":
    """The spellings of a key column's keys too few people hold, each once, sorted: every present cell whose key is not common, as the cell wrote it."""
    found: "dict[str, bool]" = {}
    for place, level in enumerate(levels):
        if level and level not in common:
            found[cells[place]] = True
    return tuple(sorted(found))


# The marks that end or join a sentence, and the breaks of a line
# (`_reads_as_a_sentence`): the full stop, the question and exclamation
# marks, the colon and the semicolon, the ellipsis, and their full-width,
# small, ideographic and double forms.
_KEYED_SENTENCE_MARKS = (
    ".?!:;\u2024\u2026\u203c\u2047\u2048\u2049\u3002\uff61\uff0e\uff01\uff1f\uff1a\uff1b"
    "\ufe52\ufe54\ufe55\ufe56\ufe57\n\r\x85\u2028\u2029"
)
# A name of this many words or more holding a mark of a sentence reads as one.
_KEYED_SENTENCE_WORDS = 3


def _reads_as_a_sentence(name: str) -> bool:
    """Whether a rare key's name reads as a sentence -- a question text written out (plan P4-D487; the orchestrator's LANE KV RULINGS 2 (2)).

    THREE WORDS OR MORE, the words cut at the product's one definition of
    a space (`taxonomy.words_of_the_screen`), AND A MARK OF A SENTENCE ANYWHERE IN IT
    (`_KEYED_SENTENCE_MARKS`: a full stop, a question or exclamation mark,
    a colon or a semicolon, an ellipsis, a line break, in any of their
    forms). THE STAND-IN FOR LANE NOTES'S READER (`taxonomy.a_sentence`,
    lane NOTES, plan P4-D481), which is not on this lane's base: it reads
    every text that reader reads -- three words and a mark placed as a
    sentence places it -- and more (a mark anywhere, a decimal point and a
    capitalised abbreviation among them), so a name it refuses that the
    other names is a false alarm, never a name let past. It counts words
    between spaces only, so a script written with no space between its
    sentences (parted by the ideographic full stop or another full-width
    mark) holds one word here: since batch 4t's merge of both lanes
    `keyed_names_pass` reads that reader beside this one, so either
    refuses (P4-D487's merge paragraph). Guarantees: a fixed function of
    the text. Raises
    TypeError where it is no text. No I/O.
    """
    if len(taxonomy.words_of_the_screen(name)) < _KEYED_SENTENCE_WORDS:
        return False
    for character in name:
        if character in _KEYED_SENTENCE_MARKS:
            return True
    return False


def keyed_names_pass(
    names: "tuple[str, ...]", role: str, code_declared: bool, decimal_comma: bool
) -> bool:
    """Whether every rare key's name passes the screens of its road, ALL OR NONE (plan P4-D487; LANE KV RULINGS 1 K4).

    THE ROADS ARE LANE CODES-2'S (`taxonomy.names_a_road_releases`, read as
    after the person's `no`): a key column read as categories goes path (iii) --
    no name that reads as a number, `taxonomy.passes_the_word_screen` as
    its net; one answered `code` or read as a long tail goes path (i)
    (`taxonomy._a_shape_no_code_wears`) AND path (iii)'s net on every name
    holding a letter (a run of five figures, a code's, allowed and one of six
    refused: `taxonomy.passes_the_word_screen`'s ``counting_figures``);
    a column of keys written as bare numbers goes path (i) alone. ON EVERY
    ROAD each name also passes lane CZ-E's identifier
    words (`taxonomy.identifier_words_form`: titles, relatives, dates,
    telephones, initials, record numbers) and lane CZ-F's persons' names
    (`taxonomy.a_persons_name`), EACH READ BOTH WAYS (`_both_readings`: as
    written, and with every character that prints nothing set aside, the
    double reading of LANE CODES-2 RULINGS 8 (2); LANE KV RULINGS 3 (3)),
    and NO NAME THAT READS AS A SENTENCE (`_reads_as_a_sentence`, and
    beside it lane NOTES's own reader, `taxonomy.a_sentence`, since batch
    4t's merge of both lanes, which also reads the sentences of a script
    written with no space between them; each read both ways: a rare
    question text written out is named after no answer, LANE KV RULINGS
    2 (2), the rule of LANE NOTES RULINGS 8 (1)): the person who
    answers `no` has never seen a rare key, so no screen rests on that
    answer for names and places. Every split of a name into words is the
    screens' own (`taxonomy._SCREEN_SPACE_RANGES`, LANE CODES-2 RULINGS 7
    (4)). Guarantees: a fixed function of the four; False for no name.
    Raises TypeError for a name that is not text. No I/O.
    """
    if not names:
        return False
    for name in names:
        if _a_persons_detail(name):
            return False
        for written in _both_readings(name):
            if _reads_as_a_sentence(written) or taxonomy.a_sentence(written):
                return False
    numbers = [name for name in names if parsing.classify_number(name) == parsing.NUMBER]
    if len(numbers) == len(names):
        return bool(taxonomy.names_a_road_releases(names, decimal_comma, True))
    if role == taxonomy.ROLE_CATEGORICAL and not code_declared:
        return bool(taxonomy.names_a_road_releases(names, decimal_comma, False))
    if not taxonomy.names_a_road_releases(names, decimal_comma, True):
        return False
    for name in names:
        if taxonomy.holds_a_letter(name) and not taxonomy.passes_the_word_screen(name, False, False):
            return False
    return True


def _rare_pool(
    levels: "list[str]", people: "list[str]", common: "frozenset[str]"
) -> "tuple[int, int]":
    """How many rare keys a key column holds and how many different people hold them: its keys that are not ``common``, and the people of their rows."""
    keys: "dict[str, bool]" = {}
    holders: "dict[str, bool]" = {}
    for place, level in enumerate(levels):
        if level and level not in common:
            keys[level] = True
            holders[people[place]] = True
    return len(keys), len(holders)


def keyed_names_of(
    pooled_in_people: bool,
    spellings: "tuple[str, ...]",
    rare_keys: int,
    rare_people: int,
    rows: int,
    people: int,
    released: bool,
    answered_no: bool,
    role: str,
    code_declared: bool,
    decimal_comma: bool,
    floor: int,
) -> "tuple[str, ...]":
    """The rare keys a keyed key column names beside its pooled total, or none (plan P4-D487, K4 and K5): ALL OR NONE.

    Named only where EVERY ONE of these holds: the key column's pool is
    counted in people (``pooled_in_people``: contract B4g's keyed pool); it
    holds TWO RARE KEYS OR MORE, held by ``floor`` people or more together
    -- a pool of one key, or of fewer people, would make its pooled total
    and its pooled block the properties of that key and of those people
    (the orchestrator's LANE KV RULINGS 3 (1), skeptic 1's item 1: one
    rare key of four people was named beside its 12 rows); both floors and
    rule U (c) hold and the key column is answered `no` to its Safe Harbor
    question (`keyed_names_released`); and every name passes its road's
    screens (`keyed_names_pass`). Guarantees: a fixed function of its
    arguments; the spellings as given, or an empty tuple. Raises TypeError
    for a name that is not text. No I/O.
    """
    if not pooled_in_people or not spellings:
        return ()
    if rare_keys < 2 or rare_people < floor:
        return ()
    if not keyed_names_released(rows, people, released, answered_no):
        return ()
    if not keyed_names_pass(spellings, role, code_declared, decimal_comma):
        return ()
    return spellings


def _keyed_names_would_pass(
    table: Table,
    settings: taxonomy.Settings,
    place: int,
    absent: "tuple[str, ...]",
    common: "tuple[str, ...]",
    people: "list[str]",
    released: bool,
    code_declared: bool,
    decimal_comma: bool,
) -> bool:
    """Whether a keyed key column's `no` would name its rare keys (plan P4-D487): the pool's keys and people, both floors, rule U (c) and the screens, the answer aside (`keyed_names_of`)."""
    cells = reading.column_values(table, place)
    levels = _key_levels(cells, frozenset(absent))
    spellings = _rare_key_spellings(levels, cells, frozenset(common))
    rare_keys, rare_people = _rare_pool(levels, people, frozenset(common))
    distinct = len({level for level in levels if level})
    role = (
        taxonomy.ROLE_CATEGORICAL
        if distinct <= taxonomy.categories_ceiling(table.n_rows, settings)
        else taxonomy.ROLE_LONG_TAIL
    )
    return bool(
        keyed_names_of(
            True, spellings, rare_keys, rare_people,
            len([level for level in levels if level]), len({person for person in people if person}),
            released, True, role, code_declared, decimal_comma, settings.small_cell_floor,
        )
    )


def keyed_names_released(rows: int, people: int, released: bool, answered_no: bool) -> bool:
    """Whether a keyed key column's rare keys may be named at all (plan P4-D487): BOTH FLOORS, read here on every path.

    The table holds `parsing.TABLE_ROW_FLOOR` rows holding a key AND
    `parsing.TABLE_PEOPLE_FLOOR` people or more (both REQUIRED of every
    caller, read off the table described, as LANE CODES-2 RULINGS 2 (3)
    made the row floor a required argument), no question offering
    `identifier` is open on the table (``released``, rule U (c)), and the
    key column is answered `no` to its Safe Harbor question. Guarantees:
    a fixed function of the four. Raises nothing. No I/O.
    """
    return (
        answered_no
        and released
        and rows >= parsing.TABLE_ROW_FLOOR
        and people >= parsing.TABLE_PEOPLE_FLOOR
    )


def _without_the_figure_openings(block: "dict[str, object]") -> "dict[str, object]":
    """A block with `figure_openings` set aside: a named pool makes up no stand-in (taxonomy `_level_details`)."""
    return {key: block[key] for key in block if key != "figure_openings"}


def _without_the_places(block: "dict[str, object]") -> "dict[str, object]":
    """The rare keys' pooled block with rule A2's places set aside (plan P4-D487, K6; taxonomy `held_back_places`).

    What the held-back cells hold at each place is, in a pool of the rare
    keys' values, what a few rare keys write: a question's own answer
    word, `Mark-020` to `Mark-029`, published its places `Mark-02` and
    the twin's stand-ins in those places met five such words on ten cells
    of the question-and-answer form, each held by one to three people. The
    pool's stand-ins are drawn in its forms alone. Every other key of the
    block is kept. Guarantees: a fixed function of the block. Raises
    nothing. No I/O.
    """
    kept = {key: block[key] for key in block if key != "shape_form_places"}
    labels = kept["labels"] if "labels" in kept else None
    if isinstance(labels, dict) and "shape_form_places" in labels:
        kept["labels"] = {key: labels[key] for key in labels if key != "shape_form_places"}
    return kept


def _keyed_value_held(
    value: str,
    open_held: "list[str]",
    described_identifiers: "list[str]",
    withheld_names: "list[str]",
    held_in_people: "list[str]",
) -> bool:
    """Whether a keyed value column stays held whole, described under no key (plan P4-D487): a question offering `identifier` open on it (``open_held``), or a column described as an identifier for any reason but its own unanswered question or its values few people hold."""
    if value in open_held:
        return True
    return value in described_identifiers and value not in withheld_names and value not in held_in_people


def _block_answer(answered: "tuple[tuple[str, str, str], ...]", value: str, label: str) -> str:
    """The answer a key block's own question was given (lane IN-4c, plan P4-D514): the first answer naming the value column and, folded, the block's key; empty where none does."""
    for column, measurement, answer in answered:
        if column == value and parsing.folded(measurement) == label:
            return answer
    return ""


def _reads_as_identifiers_to_the_checks(name: str, cells: "list[str]") -> bool:
    """Whether a key block's cells look like identifiers to the twin checks (lane IN-4c, plan P4-D514): C4's own reading of a column of that name and those cells (`twin_checks.reads_as_an_identifier`), or -- whatever they are read as, numbers included -- different values covering the checks' `KEY_LIKE_SHARE` of the present cells (a run of record numbers is read as numbers there and would pass that reading)."""
    if twin_checks.reads_as_an_identifier(name, cells):
        return True
    present = [cell for cell in cells if not parsing.is_missing_text(cell)]
    return bool(present) and len(set(present)) * 1000 >= twin_checks.KEY_LIKE_SHARE * len(present)


def _held_block(block: "dict[str, object]") -> bool:
    """Whether a key block is described as record numbers: held, its values unpublished (lane IN-4c)."""
    return (
        ("role" in block and block["role"] == taxonomy.ROLE_IDENTIFIER)
        or ("structural_role" in block and block["structural_role"] == taxonomy.ROLE_IDENTIFIER)
    )


def _key_cells_as_described(
    key_block: "dict[str, object]", cells: "list[str]", absent: "tuple[str, ...]", name: str
) -> "list[str]":
    """A key column's cells as its own block read them: its values that read as dates blank where it held them.

    THE KV3 REFUSAL AT 100,000 ROWS (lane LEDGER; carried at batch 4zz's
    landing, the same on the base): a key column whose description holds
    its values that read as dates as blank cells (its remark,
    `taxonomy.REMARK_DATED_VALUES_HELD`, plan P4-D446) counted 28 such cells
    blank, and the keyed pairs read them as rare keys, so the pool of rare
    keys held 28 rows more than the key column pools and `generate`
    refused the description (`n10`'s pooled rows 8,654, `n12`'s pool 8,682).
    The cells are held here as the column's describe held them
    (`date_counts.dated_values_blanked`, ages kept up to the reach of the
    unit its name states), so a rare key is a row the key column pools.
    A block with no such remark keeps its cells. Guarantees: a fixed
    function of the four; raises nothing; no I/O.
    """
    remarks = key_block["remarks"] if "remarks" in key_block else None
    if not isinstance(remarks, list) or taxonomy.note(taxonomy.REMARK_DATED_VALUES_HELD) not in remarks:
        return cells
    named = taxonomy.age_mark_named(name)
    mark = named if named else taxonomy.TOP_CODE
    blanked = date_counts.dated_values_blanked(
        cells, frozenset(absent), taxonomy.TOP_CODE_REACH_CEILING * mark / taxonomy.TOP_CODE
    )
    return cells if blanked is None else blanked


def _written_key(entry: "dict[str, object]") -> str:
    """A published key level's commonest spelling, the key block's name (`_commonest_written`)."""
    return _commonest_written(entry)


def _values_typed_by_key(
    table: Table,
    settings: taxonomy.Settings,
    columns: "list[dict[str, object]]",
    absent: "list[tuple[str, ...]]",
    notes: "list[dict[str, str]]",
    subject_names: "list[str]",
    subject_cells: "list[list[str]]",
    held_in_people: "list[str]",
    described_identifiers: "list[str]",
    withheld_names: "list[str]",
    kept: "list[str]",
    found: "list[KeyedPair] | None",
    answered_yes: "list[str]",
    open_held: "list[str]",
    no_safe_harbor: "list[str]",
    no_dates: "list[str]",
    declared_codes: "list[str]",
    declared_measurements: "list[str]",
    declared_commas: "list[str]",
    identities_kept: "list[str]",
    released: bool,
    harbor_year: int,
    rare_named: "list[str] | None",
    names_published: "list[str] | None",
    described: "dict[str, str] | None",
    names_checked: "tuple[str, ...] | None",
    keyed_named: "list[str] | None" = None,
    levels_pooled: "list[str] | None" = None,
    dates_held: "tuple[str, ...]" = (),
    made_up_held: "tuple[str, ...]" = (),
    harbor_put: "frozenset[str] | None" = None,
    answered_blocks: "tuple[tuple[str, str, str], ...]" = (),
    blocks_asked: "list[asking.MeasurementAsked] | None" = None,
) -> "list[tuple[str, str]]":
    """VALUES TYPED BY A KEY (lane KV, plan P4-D487): each keyed value column described key by key, in place; returns each such value column with the role of its own block.

    A KEY BLOCK'S OWN QUESTION (lane IN-4c, plan P4-D514): each common
    key's block takes the answer its own question was given
    (``answered_blocks``: value column, measurement, answer; the
    measurement matched folded) -- `identifier` always, `measurement` and
    `code` only where the twin checks do not read the block's cells as an
    identifier column (`twin_checks.reads_as_an_identifier`); and a block
    held by a question offering `identifier` that `measurement` or `code`
    would describe, unanswered and not so read, is added to
    ``blocks_asked`` with the answers that would describe it, for the
    questions file (`asking.measurement_section`). A pooled block puts no
    question (K6).

    A VALUE COLUMN `made_up_spellings_named` NAMED (``made_up_held``; batch
    4t's fix round, item 1, plan P4-D489): its key blocks of numbers too
    large or too small to hold are spelled one letter or figure wider
    (NF139), as its own block would be; one also named in
    ``withheld_names`` -- where even those spellings would meet a value, or
    none can be made -- stays held whole, described under no key.

    The pairs are read by `keyed_pairs_read` (or, ``described``, the
    validator's, taken from the description it checks, value column to
    key column, nothing read again); a value column answered `keep`
    (``kept``) is not keyed, and every pair read is added to ``found``
    for the command's question (unanswered meaning keyed). A pair whose
    key column publishes its levels and whose value column no open
    question offering `identifier` holds (``open_held``) is described:
    the value column's block becomes that of its cells on the rows that
    hold no key (`_key_block`, the value column's own name), carrying
    `by_key` -- the key column's name, one block a common key (each
    published level of the key column, the block named by its commonest
    spelling) and the rare keys' pooled block -- and the key column's
    block carries `keyed`, the value column's name. THE NAMES (K4, K5): a
    keyed key column whose pool is counted in people names its rare keys
    beside the pooled total where `keyed_names_released` and
    `keyed_names_pass` allow (its `figure_openings` set aside: no stand-in
    is made up), or is named in ``rare_named`` for its Safe Harbor
    question where only the answer is missing; the validator's
    ``names_checked`` reads exactly the names its description published.
    The person columns' notes stand; a replaced value column's notes go
    with its old block. The caller records each value column as held
    exactly where its new block is (S8d, A1). Guarantees: a fixed function
    of its arguments.
    Raises what `build_document` raises. No I/O beyond the table's own
    access.
    """
    names = [f"{block['name']}" for block in columns]
    positions: "dict[str, int]" = {}
    for place in range(len(names)):
        if names[place] not in positions:
            positions[names[place]] = place
    people = subject_cells[0] if subject_cells else None
    pairs: "list[tuple[str, str]]" = []
    commons: "dict[str, tuple[str, ...]]" = {}
    if described is not None:
        for value in names:
            if value in described and described[value] in names:
                pairs += [(described[value], value)]
    else:
        read = keyed_pairs_read(
            table, columns, absent, people, frozenset(subject_names),
            frozenset(held_in_people), settings.small_cell_floor,
        )
        for pair in read:
            if pair.value in kept:
                continue
            if found is not None:
                found += [pair]
            pairs += [(pair.key, pair.value)]
            commons[pair.key] = pair.common
    if not pairs:
        return []
    subjects_raw: "list[tuple[str, list[str]]]" = []
    for subject in subject_names:
        subjects_raw += [(subject, reading.column_values(table, positions[subject]))]
    count_people = 0
    if people is not None:
        count_people = len({person for person in people if person})
    typed: "list[tuple[str, str]]" = []
    for key, value in pairs:
        key_at = positions[key]
        value_at = positions[value]
        key_block = columns[key_at]
        # WHETHER `no` WOULD NAME THE RARE KEYS, for the clause the key
        # column's Safe Harbor question gains (K4), read before any hold.
        if (
            keyed_named is not None
            and people is not None
            and key in commons
            and key not in keyed_named
            and key not in no_safe_harbor
        ):
            if _keyed_names_would_pass(
                table, settings, key_at, absent[key_at], commons[key], people, released,
                key in declared_codes, key in declared_commas,
            ):
                keyed_named += [key]
        if described is not None:
            # THE VALIDATOR'S (validation V18, V19): the value column was read
            # with its rows of a key blank (`validation`'s own table), and the
            # key column names exactly the rare keys of the file it checks
            # where its description named them.
            listed_levels = key_block["levels"] if "levels" in key_block else None
            if (
                names_checked is not None
                and key in names_checked
                and isinstance(listed_levels, list)
            ):
                checked_cells = _key_cells_as_described(key_block, reading.column_values(table, key_at), absent[key_at], key)
                checked_levels = _key_levels(checked_cells, frozenset(absent[key_at]))
                kept_labels = frozenset(
                    f"{entry['label']}" for entry in listed_levels if isinstance(entry, dict)
                )
                spellings = _rare_key_spellings(checked_levels, checked_cells, kept_labels)
                named_key = dict(key_block)
                named_key["keyed"] = value
                if spellings:
                    named_key = _without_the_figure_openings(named_key)
                    named_key["held_back_names"] = list(spellings)
                columns[key_at] = named_key
            continue
        if _keyed_value_held(value, open_held, described_identifiers, withheld_names, held_in_people):
            continue
        if value in made_up_held and value in withheld_names:
            continue
        if (
            key_block["role"] not in _KEYED_KEY_ROLES
            or "levels" not in key_block
            or key in described_identifiers
        ):
            continue
        published = key_block["levels"]
        if not isinstance(published, list) or len(published) < 1:
            continue
        key_cells = _key_cells_as_described(key_block, reading.column_values(table, key_at), absent[key_at], key)
        levels = _key_levels(key_cells, frozenset(absent[key_at]))
        value_cells = reading.column_values(table, value_at)
        written: "dict[str, str]" = {}
        for entry in published:
            if isinstance(entry, dict):
                written[f"{entry['label']}"] = _written_key(entry)
        rows_of: "dict[str, list[int]]" = {label: [] for label in written}
        rare_rows: "list[int]" = []
        for place, level in enumerate(levels):
            if not level:
                continue
            if level in rows_of:
                rows_of[level] += [place]
            else:
                rare_rows += [place]
        asked = _KeyedAsked(
            safe_no=value in no_safe_harbor,
            safe_yes=value in answered_yes,
            dates_no=value in no_dates,
            dates_held=value in dates_held,
            # ...the value column's question put, or answered: every column the
            # command puts its Safe Harbor question or its question about values
            # that read as dates (``harbor_put``; None on the library's path,
            # which holds the listed blocks as an open question would).
            question_put=(
                harbor_put is None
                or value in harbor_put
                or value in answered_yes
                or value in no_safe_harbor
                or value in no_dates
                or value in dates_held
            ),
            code=value in declared_codes,
            measurement=value in declared_measurements,
            comma=value in declared_commas,
            kept_identity=value in identities_kept,
            released=released,
            harbor_year=harbor_year,
            made_up=value in made_up_held,
        )
        blocks: "list[dict[str, object]]" = []
        pooled_blocks: "list[str]" = []
        for label in sorted(written):
            rows = rows_of[label]
            if not rows:
                continue
            block_cells = [value_cells[place] for place in rows]
            block_subjects = [(subject, [cells[place] for place in rows]) for subject, cells in subjects_raw]
            answer = _block_answer(answered_blocks, value, label)
            # ...ITS OWN ANSWER, never where the twin checks read its cells
            # as an identifier column: there the block stays held and is
            # asked nothing (lane IN-4c, HIPAA first).
            looks = _reads_as_identifiers_to_the_checks(written[label], block_cells)
            own = answer if answer == asking.ANSWER_IDENTIFIER or not looks else ""
            seen: "list[str]" = []
            block = _key_block(
                table, settings, written[label], block_cells, block_subjects,
                asked, False, value, pooled_blocks, own, seen,
            )
            if blocks_asked is not None and not answer and not looks and seen and _held_block(block):
                releases: "list[tuple[str, str]]" = []
                for word in (asking.ANSWER_MEASUREMENT, asking.ANSWER_CODE):
                    tried = _key_block(
                        table, settings, written[label], block_cells, block_subjects,
                        asked, False, value, None, word,
                    )
                    if not _held_block(tried):
                        releases += [(word, f"{tried['role']}")]
                if releases:
                    blocks_asked += [asking.MeasurementAsked(value, key, written[label], seen[0], tuple(releases))]
            blocks += [{"key": label, "block": block}]
        by_key: "dict[str, object]" = {"key": key, "key_blocks": blocks}
        if rare_rows:
            # ...ITS PLACES SET ASIDE: no property of a few rare keys (K6).
            by_key["pool"] = _without_the_places(_key_block(
                table, settings, value,
                [value_cells[place] for place in rare_rows],
                [(subject, [cells[place] for place in rare_rows]) for subject, cells in subjects_raw],
                asked, True, value, pooled_blocks,
            ))
        top = dict(_key_block(
            table, settings, value,
            [value_cells[place] if not levels[place] else "" for place in range(len(levels))],
            subjects_raw, asked, True, value, pooled_blocks,
        ))
        # ...a key block whose pool is counted in people is the value
        # column's pool for rule U (c): the command describes the table
        # again with nothing released while a question offering `identifier`
        # is open, and then no key block pools in people.
        if pooled_blocks and levels_pooled is not None and value not in levels_pooled:
            levels_pooled += [value]
        top["position"] = value_at + 1
        top["by_key"] = by_key
        columns[value_at] = top
        typed += [(value, f"{top['role']}")]
        kept_notes = [note for note in notes if note["column"] != value]
        del notes[:]
        notes += kept_notes
        named_key = dict(key_block)
        named_key["keyed"] = value
        spellings = _rare_key_spellings(levels, key_cells, frozenset(written))
        if names_checked is not None:
            if "pool_in_people" in key_block and key in names_checked and spellings:
                named_key = _without_the_figure_openings(named_key)
                named_key["held_back_names"] = list(spellings)
        elif spellings and people is not None:
            # THE NAMES (K4, K5; `keyed_names_of`): all or none, only of a
            # pool counted in people of two rare keys or more held by the
            # floor's people, both floors, rule U (c), the screens, and the
            # key column's `no`; where only that answer is missing, the key
            # column is named for its question's clause.
            rare_keys, rare_people = _rare_pool(levels, people, frozenset(written))
            road = (
                "pool_in_people" in key_block,
                spellings,
                rare_keys,
                rare_people,
                len([level for level in levels if level]),
                count_people,
                released,
            )
            screened = (
                f"{key_block['role']}",
                key in declared_codes,
                key in declared_commas,
                settings.small_cell_floor,
            )
            # ...the key column's `no`, and no `yes` to a question put to it
            # beside that `no` (ANY YES HOLDS, LANE KV RULINGS 6 (1)).
            named = keyed_names_of(*road, key in no_safe_harbor and key not in answered_yes, *screened)
            if named:
                named_key = _without_the_figure_openings(named_key)
                named_key["held_back_names"] = list(named)
                if names_published is not None:
                    names_published += [key]
            elif (
                key not in no_safe_harbor
                and rare_named is not None
                and key not in rare_named
                and keyed_names_of(*road, True, *screened)
            ):
                rare_named += [key]
        columns[key_at] = named_key
    return typed


def build_document(
    table: Table,
    settings: taxonomy.Settings,
    forced_identifiers: list[str],
    forced_codes: list[str] | None = None,
    forced_measurements: list[str] | None = None,
    forced_decimal_commas: list[str] | None = None,
    declarations_are_reconstructed: bool = False,
    described_pairs: list[str] | None = None,
    forced_metadata_rows: int = 0,
    forced_delimiter: str = "",
    kept_placeholder_days: "dict[str, tuple[str, ...]] | None" = None,
    judged_candidates: "dict[str, tuple[str, ...]] | None" = None,
    table_notes: "list[taxonomy.Note] | None" = None,
    readings_box: "list[tuple[object, ...]] | None" = None,
    calendar_censuses: bool = True,
    stored_as: "tuple[str, ...] | None" = None,
    counted_units: "dict[str, int] | None" = None,
    unanswered: "list[str] | None" = None,
    subjects: "list[str] | None" = None,
    counted_in_subjects: "list[str] | None" = None,
    time_grains: "dict[str, grains.Grain] | None" = None,
    absent_read: "dict[str, tuple[str, ...]] | None" = None,
    top_code: bool = False,
    safe_harbor_no: "list[str] | None" = None,
    top_coded_only: "dict[str, int] | None" = None,
    ages_counted_in: "dict[str, int] | None" = None,
    top_pooled_only: "dict[str, tuple[int, tuple[str, ...]]] | None" = None,
    ages_established: "dict[str, str] | None" = None,
    five_figures: "list[str] | None" = None,
    ages_held: "list[str] | None" = None,
    counted_in_rows: "list[str] | None" = None,
    described_affixed: "list[str] | None" = None,
    described_labels: "dict[str, str] | None" = None,
    few_valued: "list[str] | None" = None,
    rare_values_released: bool = True,
    rare_listed: "list[str] | None" = None,
    harbor_year: int = 0,
    harbor_reasons: "dict[str, str] | None" = None,
    year_top_coded_only: "dict[str, int] | None" = None,
    top_banded_only: "frozenset[str] | None" = None,
    kept_identities: "list[str] | None" = None,
    levels_pooled: "list[str] | None" = None,
    levels_kept_only: "dict[str, tuple[str, ...]] | None" = None,
    counted_absent_only: "tuple[str, ...] | None" = None,
    dated_values: "list[str] | None" = None,
    dated_held: "tuple[str, ...]" = (),
    dated_values_no: "list[str] | None" = None,
    dates_answered: "tuple[str, ...]" = (),
    long_table_dates: bool = False,
    people_whatever_their_number: bool = False,
    kept_spellings: "dict[int, taxonomy.KeptSpellings] | None" = None,
    rules_published: "dict[str, str] | None" = None,
    rare_named: "list[str] | None" = None,
    names_published: "list[str] | None" = None,
    names_checked_only: "tuple[str, ...] | None" = None,
    top_words_only: "list[str] | None" = None,
    top_ends_only: "dict[str, tuple[int, ...]] | None" = None,
    described_text: "list[str] | None" = None,
    made_up_held: "list[str] | None" = None,
    counts_held_for_dates: "tuple[str, ...]" = (),
    keyed_kept: "list[str] | None" = None,
    keyed_found: "list[KeyedPair] | None" = None,
    keyed_yes: "list[str] | None" = None,
    keyed_open: "list[str] | None" = None,
    keyed_described: "dict[str, str] | None" = None,
    keyed_named: "list[str] | None" = None,
    keyed_answered: "tuple[tuple[str, str, str], ...]" = (),
    keyed_asked: "list[asking.MeasurementAsked] | None" = None,
) -> dict[str, object]:
    """Describe a whole table: the profile document, ready to serialize.

    - A KEY BLOCK'S OWN QUESTION (lane IN-4c, plan P4-D514):
      ``keyed_answered`` holds each answer a key block's own question was
      given (value column, measurement, answer) and ``keyed_asked``, where
      given, gathers the blocks that question is put to
      (`_values_typed_by_key`); both empty describe every table as before.

    - A COLUMN OF SENTENCES IS DESCRIBED AS FREE TEXT (lane NOTES, plan
      P4-D481): a column whose reading would publish its levels and half
      or more of whose present cells are sentences (`taxonomy.a_sentence`)
      is described as free text -- lengths, word counts and how often its
      values repeat, no value -- with the evidence
      `taxonomy.EVIDENCE_SENTENCES_AS_TEXT`, where nothing else holds it:
      a Safe Harbor hold (lane SH2's, CZ-E's and CZ-F's) keeps precedence
      and its reason, a declared identifier stays one, and a column an
      open question offering `identifier` holds stays held. In place of
      the count in people's hold of such a column, which published every
      sentence's layout and generated slowly. The profile command puts it
      its question (`asking.sentence_questions`). A validator's
      re-description reads a column its description read as labels as
      labels (``described_labels``, ``levels_kept_only``).
      ``described_text``, where given, is the validator's hand-over of
      the columns its description read so: each is described as free
      text wherever its reading would publish its levels, its cells
      sentences or not (the twin writes such a column as filler), and no
      other column is.

    Guarantees:

    - Inputs: a Table as produced by the reader, the settings that
      govern the taxonomy, and the names of columns the user declared
      to be record numbers. THE TABLE MUST HAVE BEEN READ AT THE FLOOR
      IT IS DESCRIBED AT: `reading.read_table` holds a delimited file's
      own lines and a workbook's number formats to the floor it is
      given (plans P4-D283 and P4-D290), and this function publishes
      the form the reader settled without asking the floor again. A
      table read at a floor of one and described here at
      eleven publishes its line facts as a floor of one would -- a run
      of trailing blank lines at one place, which the floor-eleven rule
      withholds -- and is a description `synthtwin profile` never
      writes. `synthtwin profile` and the validator both pass
      ``settings.small_cell_floor`` to the reader; nothing here checks
      that a library caller did (the merge skeptic of the carried date
      items of 2026-09-18, measured and carried).
    - Determinism: the document depends only on those inputs. No clock,
      no environment, no random source, and every mapping written out
      is written in sorted key order.
    - Errors raised: TypeError if a cell is not text (an internal
      invariant of the readers); and, for a table read in groups of
      columns (`reading.Table.source`, lane SR, plan P4-D400), whatever
      `reading.column_values` raises: ProfileError where the file
      changed since it was first read, or can no longer be read
      (`errors.file_changed_while_read`).
    - Boundary: a table read whole opens no file here. A table read in
      groups of columns is READ AGAIN FROM ITS FILE, one group at a
      time, as each group's first column is described (Codex's review of
      lane SR, item 8): its file must stay where it was, readable and
      unchanged, until this returns. No value of a suppressed
      kind reaches the document. The settings block records how many
      values were named with --keep-value and --missing-value and the
      rule that matched them, never the spellings (review item
      P1-R7-F2). Declaring a value does not take it out of its own
      column, and this docstring does not claim it does: a kept value
      is data from that point on and is described wherever its column
      publishes values, and a declared-missing value is counted absent
      with its spelling published only under the same floor and role
      rules as any other missing spelling. DECLARATION_PUBLICATION
      above states the scope of the settings rule exactly.
    - ``described_pairs`` is handed over by the validator alone: the
      columns the description it checks against read as a slashed pair
      of whole numbers from their values, which the checked file is
      then read as ahead of the long-tail rule (plan P4-D40, validation
      method V2.2-A2). It is not a declaration and the settings block
      does not record it. `synthtwin profile` never passes it.
    - ``described_affixed`` is handed over by the validator alone, as
      ``described_pairs`` is: the columns the description it checks
      against read as `affixed_number` without `--measurement`, which
      the checked file is read as wherever its cells allow, ahead of the
      categories rule (plan P4-D438). Not a declaration either.
    - ``described_labels`` is the validator's too: per column the
      description it checks read as labels or as joined numbers, that
      reading (`taxonomy.KEPT_LABELS`, `taxonomy.KEPT_JOINED`), which the
      checked file is read under as before plan P4-D438 -- neither of
      rule 7's unit stand-asides taken, and a joined column's rule 0c
      reading kept -- so a
      description that reads the column so, written by this version or
      an earlier one, is checked against the reading it published
      (Codex's review of lane UN-1a, item 4).
    - ``kept_placeholder_days`` is handed over by the validator alone too:
      per column, the placeholder days the description it checks against
      published as `kept_by_you` there (plan P4-D136). A `--keep-value`
      spelled as the table spelled the day reaches the settings block as
      nothing, so this is how the checked file keeps what the description
      kept, column by column and no wider. `synthtwin profile` never
      passes it.
    - ``judged_candidates`` is the validator's too, and the other side
      of the same hand-over: per column, the stand-in numbers and
      placeholder days the description it checks against published as
      `read_as_missing` there (plan P4-D6.4). The twin writes those
      cells as the source wrote them, and this is how the checked file
      reads them as the description did without its own values having
      to fire the judgement again. `synthtwin profile` never passes it.
    - ``readings_box`` is a list holding one thing, what `synthtwin
      profile`'s population census read (`taxonomy.population_census`),
      handed over so a column the census read is not read again; the box
      is empty when this returns. Each reading is passed to
      `profile_column` for the
      column whose cells it was read from, once, and `profile_column`
      takes it only where every argument of the reading is the one it
      would have read under; an entry that is not a
      `taxonomy.HeldReading` is passed to nothing. The document is the
      same with or without them, PROVIDED no column list has been
      changed in place since the census read it: a column is matched to
      its reading by the identity of its list, not by its cells.
    - ``stored_as`` is `stored_as_of` of this table, handed over by the
      command that already took it for the census; None takes it here.
    - ``unanswered`` names the columns a question offering `identifier`
      was put to and nobody answered (plan P4-D401). Each is described as
      a record number is, with no prefix and the evidence that says why
      (`taxonomy.as_unanswered_identity`), and is recorded beside the
      declared ones so the twin and the validator read it as one. None
      or empty describes every column as before, byte for byte.
    - ``subjects`` names the columns whose values are the people the
      rows are about (plan P4-D406): the declared person columns and the
      candidates of an open person question. Every other column's
      published values are counted in them (`_counted_in_subjects`),
      and each subject column publishes the census of repetition its
      counts imply (`taxonomy.with_even_census`). None, empty, or
      subject columns that are each different on every row describe
      every column as before, byte for byte. ``counted_in_subjects``,
      where given, is a list this call extends with the name of each
      column whose description that count changed, for the screen;
      ``counted_in_rows`` likewise with each column of dates the count
      in rows held (plan P4-D433).
    - A column of dates, stamps, clock times or counted dates that the
      count in people would hold is described at a coarser calendar grain
      instead where one serves (plan P4-D417, `_grain_walk`): its cells
      written as the starts of their buckets, the record `time_grain`
      beside them; and where none serves it is held with that record,
      rung `held`, so its twin writes valid dates and times.
      ``time_grains`` names the grains a description published (the
      validator's): each such column's cells are described at its rung,
      the tails pooled into its published ends, and nothing is decided.
      ``absent_read``, where given, receives for each such column the
      spellings its own reading of the cells as written took as no value
      (``absent_spellings``), the ones its cells kept as written: the
      validator measures the file's own cells with the same (repair round
      3 of lane PS, the second verify's item 1).
    - A column a person declared as counted dates whose cells did not
      read as such dates is held as a record number on EVERY table, with
      or without ``subjects`` (`taxonomy.as_counted_dates_held`, contract
      NF127): read without the declaration, its numbers would be those
      dates published as plain numbers. Declarations reconstructed from
      a description (``declarations_are_reconstructed``, the validator's)
      hold nothing: a checked file is described as its cells read.
    - A FEW-VALUED COLUMN WITH A WIDE GAP (lane GG, plan P4-D440; lane
      ZR-b's ZS.4), read `count` or `continuous` and held by no question,
      publishes `few_values` -- its own numbers, no count -- only where
      it is named in ``safe_harbor_no``; every other such column is
      described as before, byte for byte, and its name is added to
      ``few_valued`` where that list is given, for the command to put the
      Safe Harbor question to it. A list naming a RARE VALUE -- one held
      by fewer cells than the floor -- is released only where
      ``rare_values_released`` (the command passes False while a question
      offering `identifier` is open on any column of the table: the
      stand-ins page's rule U (c), repair 1 of lane GG); each column so
      released is named in ``rare_listed`` where that list is given.
    - ``long_table_dates`` (lane GRa, plan P4-D449; behind the chain's
      switch alone): the patient table, one row a patient, is usually far
      under the owner's table floor, and its date columns count each
      patient as a holder as a table at the floor counts each row, as its
      top-coded category is pooled (plan P4-D454); only `patient_layer`
      passes it, so every shipped byte stands.
    - ``people_whatever_their_number`` (lane KV, plan P4-D487; only a key
      block passes it, `_key_block`): every subject column that repeats
      counts its columns in people WHATEVER ITS NUMBER OF DIFFERENT
      PEOPLE, as one holding the floor's number does. A key block is a part
      of a table whose person column holds the floor's people; its own
      rows may hold fewer -- the rare keys' pooled block of one rare key
      held by four people on twelve rows -- and counted in rows there, its
      values, statistics and kind were published as the properties of
      that key, a Safe Harbor town among them (the orchestrator's LANE KV
      RULINGS 3 (1), skeptic 1's item 1). So counted, a block whose present
      cells fewer than the floor's people hold is counted absent, and
      every level and statistic of it is counted in people.
    - THE SAFE HARBOR NUMBERS (plan P4-D427, lane ZR-b's ZS.1 and ZS.3),
      the command's rule as P4-D401's hold is (``top_code``, which
      `synthtwin profile` passes; False describes every column as
      before, byte for byte). A column of any role that prints a value
      (`taxonomy.SAFE_HARBOR_UNREACHED_ROLES` aside), not held and not
      named in ``safe_harbor_no`` -- answered `no` to its Safe Harbor
      question -- is read by `taxonomy.safe_harbor_reach` on its present
      cells, its absent ones set aside: AGES are described with every
      value from 90 to 125 read as 90 (`taxonomy.top_coded_cells`, its
      absent cells kept) and the key `top_coded`, or, where so reading
      them would change which cells are absent (90 is one of its missing
      values), named in ``ages_held`` for the command to hold;
      ``five_figures``, where given, is extended with the name of each
      column of ZIP-shaped numbers, for the command to hold. A column of
      ages held as record numbers -- by its open question or by the count
      in people -- is held from its top-coded cells and keeps the key
      (Codex's review of lane SH, item 2). ``top_coded_only``, the validator's, names exactly the
      columns to read so, each with the mark its description published
      (`taxonomy.TOP_CODE_MARKS`), each read so whatever its cells, and no
      other. AGES IN OTHER UNITS (lane SH3, plan P4-D454): a column whose
      name says its ages are counted in months, weeks or days
      (`taxonomy.age_mark_named`) is read in that unit, its mark (1,080
      months, 4,695 weeks, 32,871 days) standing for 90 and published as
      `top_coded`, and never as ZIP codes; a cell writing its own unit
      (`14 months`, `92 y/o`) is read in it, then the name's unit, then
      the unit answered (``ages_counted_in``: each column answered with
      one, and that unit's mark); a column the name says holds ages with
      no unit stated is read in years until its unit is answered, its
      strays past 125 whatever their share read 90 (lane SH3's repair,
      the orchestrator's LANE SH3 RULINGS 2 (1)), and its question offers
      the units. A top category fewer than the floor's rows -- or people
      of a subject column that repeats -- hold is pooled below the mark
      at the table floor and above; the block records the rule as
      `top_category_pooled` (and `top_category_people`), whether or not a
      category was pooled, and ``top_pooled_only``, the validator's,
      gives each column's recorded rule back; a column whose top-code
      wrote a band of ages as its one band past 89 records
      `top_coded_bands`, and ``top_banded_only``, the validator's, names
      the columns that record it, a description read again reading the
      bands of no other (plan P4-D472). The age words around a
      number (`Age 95`, `(95 yrs)`; `taxonomy.AGE_VOCABULARY`, lane HB2,
      plan P4-D477) are read by the reach and the top-code, and a block
      whose cells hold them records `top_coded_words`; ``top_words_only``,
      the validator's, names the columns whose recorded block says so,
      every other top-coded column read again without them as it was
      made. A top-coded column the count in people would hold, beside a
      subject column that repeats, at the table floor and above, has its
      ENDS POOLED IN PEOPLE where that frees it (each end's values few
      people hold joined into one band the floor's people hold, the low
      band written as its highest value and the top band as its lowest,
      never past the top code: `taxonomy.ends_pooled_in_people`), recorded
      as `top_coded_ends`; ``top_ends_only``, the validator's, gives each
      column's recorded ends back. ``ages_established``, filled for
      the command: each column top-coded here, and what establishes it
      as ages beside its values (`taxonomy.AGE_UNIT_IN_CELLS` and the
      rest; "" for its values alone).
    - THE SAFE HARBOR YEARS, PLACES AND DEVICES (plan P4-D434), the
      command's rule too: with ``harbor_year``, the reference year (the
      command passes `taxonomy.SAFE_HARBOR_REFERENCE_YEAR`), a column lane SH's reach did not take and whose cells,
      judged on their bulk, are four-figure years from 1850 to that year,
      one at most 90 years before it (`taxonomy.safe_harbor_years`), is
      described with every year from 1850 to that one read as it
      (`taxonomy.year_top_coded_cells`) and the key `top_coded_year`; and
      with ``harbor_reasons`` given, a column held for one of lane SH2's
      reasons (`taxonomy.safe_harbor_hold`: dates in a year showing an
      age over 89, ZIP codes read as counted dates, GS1 device numbers,
      ZIP codes cut to three figures, a name that says it holds a place;
      and years that are also ZIP-shaped) is named in ``five_figures``
      and in ``harbor_reasons`` with its reason, for the command to hold.
      ``year_top_coded_only``, the validator's, names the columns to read
      so and each one's year, and no other. LANE SH2'S REPAIR 1: a column
      held whole for a place, a device number or a ZIP area is so before
      lane SH's age top-code is asked (county codes `001` to `101`
      answered `code` were top-coded as ages and published); years are
      judged on two in three of the cells left, a year beside a word or a
      mark (`born 1930`) is a year, and years beside as many other numbers
      as the floor's rows (`30` for 1930) are held whole
      (`taxonomy.HELD_YEARS_BESIDE`) rather than pooled.
    - ``kept_identities`` names the columns whose question offering
      `identifier` was answered `keep` (plan P4-D401, `synthtwin
      profile`'s). A column of them whose cells would read as decimals
      with a comma but for five figures or more before every comma
      (`parsing.COMMA_RECORD_NUMBERS`, `1002345,7`) is read with the
      comma, as an inferred one is (repair 2 of lane UN-1b); None or
      empty infers no such column, so P4-D401's question is put first.
    - DATES IN DISGUISE (plan P4-D446, lane CZ-H), the command's rule as
      the top-code is (``top_code``): a column read as labels or as numbers
      that holds values reading as dates -- day counts, epoch seconds,
      dates written as text -- not held and not named in
      ``safe_harbor_no``, nor answered `measurement` to question Q3, is
      named in ``dated_values`` where that list is given, for the command
      to put the Safe Harbor question to it, and described with those
      values read as blank cells where ``dated_held`` names it. So the
      command's first description, which its questions are worked out
      from, reads every column's cells as written, as ``unanswered``'s
      holds leave it to. Only ``dated_values_no`` -- `no` to THAT
      question -- frees them: ``safe_harbor_no``, `no` to the column's age
      or ZIP question, frees its top-code or ZIP hold alone (the
      orchestrator's LANE CZ-H RULINGS 6 (1), item 3). The rule decides
      before the age top-code, which reads the cells it leaves (RULINGS
      5 (1)). A column whose date-codes question (P4-D381) was answered,
      named in ``dates_answered``, is read under the date rules, as one
      declared as dates is, and the rule does not read it.
      A count no older than 125 years in the unit of the column's ages
      is an age and is kept: the mark its description, its name or its
      answer states (lane SH3, plan P4-D454; years where none does)
      stands for 90 years (limit (h), wired at lane SH3's merge).
    - THE NAMES OF RARE LEVELS (lane CODES-2, plan P4-D471; the owner's
      answer Z1 = B): a column named in ``safe_harbor_no`` -- `no` to its
      Safe Harbor question, the one sentence every reason of it asks (not
      the dates-in-disguise question's, ``dated_values_no``) -- is read
      `taxonomy.HELD_BACK_NAMED_ANSWERED`, so a label column names its
      held-back levels beside their pooled total where
      `taxonomy.held_back_names_published` allows; every other column is
      read `taxonomy.HELD_BACK_NAMED_SCREENED`, which names only a column of
      numbers with labels' held-back words that pass the word screen. Rule
      U (c): none while ``rare_values_released`` is False, and never a
      column ``unanswered`` holds or one described as a record number. A
      label column whose `no` would name its pool (`held_back_nameable`)
      and that is not answered `no` is added to ``rare_named``, for the
      command to put that question; a column that names its pool to
      ``names_published``. ``names_checked_only``, the validator's, reads
      exactly those columns `taxonomy.HELD_BACK_NAMED_CHECKED` and no
      other column any way that names a pool.
    - ``made_up_held`` names the columns `made_up_spellings_named` found
      (lane ID-ROOM4, plan P4-D489): numbers too large or too small to
      hold whose made-up spellings would be written as real values. Each
      is described as its cells read with its declarations of a code, a
      measurement or a decimal comma set aside, since the hold is whatever
      the answer, and its block of that role carries the evidence NF139,
      so the twin spells each of its cells one letter or figure wider than
      its longest value (method G10.5 step 8; the orchestrator's LANE
      ID-ROOM4 RULINGS 5 (2)); one also named in ``unanswered`` -- where
      even those spellings would meet a value -- is held there with NF139
      in place of NF125. It is no subject the other columns are counted
      in. None or empty describes every column as before, byte for byte.
    """
    spelled_held = [] if made_up_held is None else made_up_held
    withheld_names = [] if unanswered is None else unanswered
    identities_kept = [] if kept_identities is None else kept_identities
    no_safe_harbor = [] if safe_harbor_no is None else safe_harbor_no
    no_dates = [] if dated_values_no is None else dated_values_no
    # THE SUBJECT COLUMNS THAT REPEAT (plan P4-D406): one different on
    # every row counts each value in rows already, as the floor does.
    # Each is kept with whether it holds the floor's number of different
    # values (`_reaches_the_floor`): one of fewer is counted in too, but
    # only for the columns attached to it (`_counted_in_subjects`).
    subject_cells: "list[list[str]]" = []
    subject_names: "list[str]" = []
    subject_enough: "list[bool]" = []
    for subject in subjects if subjects else []:
        if subject in subject_names or subject not in table.column_names:
            continue
        held_cells: "list[str]" = []
        for place, column_name in enumerate(table.column_names):
            if column_name == subject:
                # THROUGH THE GENERIC ACCESS (lane SR, plan P4-D400): a
                # table read in groups holds one group, and the subject
                # column is read from its own (batch 4e's integration).
                held_cells = reading.column_values(table, place)
        # Each cell read as the subject it names, its spellings merged
        # and every spelling of nobody one unknown person (`subject_keys`):
        # `REC-7`, `rec7` and `REC0007` are one person, never three, and
        # whether the column REPEATS is asked of those subjects, not of
        # the spellings (Codex's review of lane HX2, items 2 and 3).
        keyed_subjects = subject_keys(
            held_cells, settings.declared_missing_values
        )
        # ...and the column's own cells are let go, so no column outlives
        # its group while the walk below reads the next (lane SR).
        held_cells = []
        # ...A KEY BLOCK'S PERSON COLUMN COUNTS ITS PEOPLE WHETHER OR NOT IT
        # REPEATS ON THE BLOCK'S ROWS (lane KV, plan P4-D487): the table's
        # person column repeats and holds the floor, and a key's rows of one
        # row a person are still rows of people -- three rare keys held by
        # three people on one row each were described in rows, their pooled
        # block publishing its three present cells.
        if _repeats(keyed_subjects) or people_whatever_their_number:
            subject_cells += [keyed_subjects]
            subject_names += [subject]
            subject_enough += [
                people_whatever_their_number
                or _reaches_the_floor(keyed_subjects, settings.small_cell_floor)
            ]
    # DATES ARE COUNTED IN PEOPLE WHATEVER THEIR NUMBER (plan P4-D433,
    # repair round 2, the combined verify's item 1): at the table floor and
    # above, every subject column that repeats counts a column of dates in
    # its people, one of fewer people than the floor included -- no bucket
    # then reaches the floor and the column is held (NF129). Counted in
    # rows instead, a raised floor above the table's number of people let
    # 2,500 rows of ONE patient publish that patient's day. The rows count
    # stays where no subject column repeats, never in place of people.
    # Below the table floor, which the command refuses (P4-D425), the
    # library keeps P4-D406's reading.
    dates_in_people: "list[bool]" = []
    for enough in subject_enough:
        dates_in_people += [enough or table.n_rows >= parsing.TABLE_ROW_FLOOR or long_table_dates]
    described_identifiers = forced_identifiers + [
        name for name in withheld_names if name not in forced_identifiers
    ]
    declared_codes = [] if forced_codes is None else forced_codes
    declared_measurements = (
        [] if forced_measurements is None else forced_measurements
    )
    if spelled_held:
        declared_codes = [one for one in declared_codes if one not in spelled_held]
        declared_measurements = [
            one for one in declared_measurements if one not in spelled_held
        ]
    # The columns a person said write their numbers with a comma for
    # the point (plan P4-D26). Named columns only: a comma inside an
    # address or a note is not a decimal point, and no rule here can
    # tell the difference, which is why the declaration exists.
    # A FRESH LIST (repair 1 of lane UN-1b, skeptic 1 item 1): the columns
    # inferred below join it, and the caller's list is never touched.
    declared_commas: "list[str]" = []
    if forced_decimal_commas is not None:
        declared_commas += [
            one for one in forced_decimal_commas if one not in spelled_held
        ]
    read_as_pairs = [] if described_pairs is None else described_pairs
    read_as_affixed = [] if described_affixed is None else described_affixed
    read_as_labels: "dict[str, str]" = (
        {} if described_labels is None else described_labels
    )
    kept_days: "dict[str, tuple[str, ...]]" = (
        {} if kept_placeholder_days is None else kept_placeholder_days
    )
    judged_here: "dict[str, tuple[str, ...]]" = (
        {} if judged_candidates is None else judged_candidates
    )
    # REFUSED AT THE PRODUCER, so that every path is covered and not
    # only the command line (R-P4-54; review item P4-G3-R8-F2). A
    # declared value whose number depends on which grammar reads it
    # means one thing on a declared column and another everywhere
    # else, and the settings block has one place to record it -- so a
    # description carrying the pair can tell a correct file it missed
    # its own presence, role and numbers. `build_document` is a public
    # entry point; the CLI refusal alone left that one call away.
    #
    # `declarations_are_reconstructed` says these declarations came
    # from a DESCRIPTION rather than from a person, which is what the
    # validator hands over: it reads back the spellings a column
    # published among its absent cells so that it can take the checked
    # file the way the description was made. Those are not a person's
    # words and were gated when the description was written, and one of
    # them can legitimately be a spelling whose number depends on the
    # grammar -- `--missing-value -999` is safe and matches a cell
    # spelled `-999,0` by NUMBER on a declared column, which is what
    # the matching rule says it should do. Refusing the reconstruction
    # turned away a correct description while checking a correct file.
    # ...and THE SAME CHECK KEEPS A COMMA FROM BEING INFERRED (repair 1 of
    # lane UN-1b, Codex item 4): a declared value whose number depends on
    # the grammar (`--missing-value -9.98` is -998 under a comma) would
    # mean one thing on an inferred column and another on the rest, which
    # the person declaring it never chose. A column whose comma only the
    # cells would settle is then read as it was before plan P4-D443.
    commas_inferable = not declarations_are_reconstructed
    for spelling in (
        list(settings.kept_values) + list(settings.declared_missing_values)
    ):
        if parsing.reads_as_two_numbers(spelling):
            commas_inferable = False
            if declared_commas and not declarations_are_reconstructed:
                raise ValueError(
                    f"{taxonomy.AMBIGUOUS_DECLARED_VALUE}: {spelling}"
                )
    columns: list[dict[str, object]] = []
    absent_spellings: "list[tuple[str, ...]]" = []
    notes: list[dict[str, str]] = []
    # The columns held as record numbers (plan P4-D406): by the count in
    # people, or declared as counted dates their cells did not read as.
    held_in_people: "list[str]" = []
    # THE NOTES ABOUT THE WHOLE TABLE COME FIRST (plan P4-D341), each
    # naming no column. They are PASSED IN and never decided here: this
    # function describes a table of any size and refuses none, so
    # nothing about a table's population is judged in it. The command
    # is the one place that judges, and it hands the sentence it has
    # already printed on the screen so that the page and the screen
    # cannot say two different things.
    for spoken in table_notes if table_notes else []:
        notes += [{"column": "", "note": spoken}]
    # EACH CENSUS READING IS HANDED OVER ONCE, to the column it was read
    # from: the description takes the reading's lists as its own.
    waiting: "list[object]" = []
    # THE LIST IS THE ONLY HOLDER FROM HERE ON (lane S4d, plan P4-D390):
    # a reading leaves it when its column takes it, and is let go once
    # that column is described. The readings arrive IN THEIR BOX and are
    # taken out of it here, in this frame (lane CF4b): handed over as an
    # argument of their own, they were held by the caller until this
    # returned on CPython 3.10, whose caller keeps every argument of a
    # call on its stack until the call returns -- from 3.11 a call from
    # Python to Python moves them into the callee's frame -- so on 3.10
    # every reading lived until the whole table was described.
    if readings_box:
        waiting = [held for held in readings_box[0]]
        del readings_box[0]
    # HOW A WORKBOOK STORES EACH COLUMN (plan P4-D382): most of its
    # cells as dates, which lets the dates be read beside a few text
    # cells, or every one as a clock, which keeps the clocks from a
    # list of labels the twin could not write back. The validator
    # describes a checked workbook through this same line, so a twin is
    # read the way its source was.
    storage = (
        stored_as_of(table, settings) if stored_as is None else stored_as
    )
    # Lane SH2's pairs of coordinates (plan P4-D434): each column's reading
    # as one, and the columns still open to be held for it.
    coordinate_readings: "list[tuple[str, str]]" = []
    coordinates_open: "list[str]" = []
    # A describe of its own: the readings an earlier describe kept are let go.
    if kept_spellings is not None:
        for place in [place for place in kept_spellings]:
            del kept_spellings[place]
    for position, name in enumerate(table.column_names, start=1):
        # The column count at a terminal only, written over in place (lane EZ-a, P4-D479).
        progress.column(position, len(table.column_names))
        # EACH COLUMN ASKED OF THE GENERIC ACCESS (lane SR, plan P4-D400):
        # a table read in groups holds one group, and the next is read
        # when its first column is described.
        cells = reading.column_values(table, position - 1)
        # ...as the table holds them, for the `clock-figures` answer's
        # declined check (Codex's review of lane TR, items 2 and 3).
        cells_as_read = cells
        # A DECIMAL COMMA INFERRED (lane UN-1b, plan P4-D443; the zoo-fix
        # plan's 2.1b (c) v2.1): where the column's cells settle that its
        # comma is the decimal point (`parsing.decimal_comma_inferred`),
        # it is read as a column declared `--decimal-comma` is read, and
        # published among `forced_decimal_commas`, so `synthtwin generate`
        # writes its numbers with the comma and `synthtwin validate` reads
        # the twin alike. Never for a column a person named a code or a
        # record number, nor one an open question holds, nor where the
        # validator hands over the description's own declarations.
        # Nor where a declared value reads by the grammar (Codex item 4),
        # nor on record numbers with a check digit (`1002345,7`; skeptic 1
        # item 8): five figures or more before every comma, at any count
        # of different numbers (repair 2), P4-D401's reach -- read with
        # the comma only once its question offering `identifier` is
        # answered `keep`, the base's reading coming first.
        if (
            commas_inferable
            and name not in declared_commas
            and name not in declared_codes
            and name not in described_identifiers
        ):
            verdict = parsing.decimal_comma_inferred(cells)
            if verdict == parsing.COMMA_INFERRED or (
                verdict == parsing.COMMA_RECORD_NUMBERS
                and name in identities_kept
            ):
                declared_commas += [name]
        handed_over: "taxonomy.HeldReading | None" = None
        still_waiting: "list[object]" = []
        for held in waiting:
            if (
                handed_over is None
                and isinstance(held, taxonomy.HeldReading)
                and held.values is cells
            ):
                handed_over = held
                continue
            still_waiting += [held]
        waiting = still_waiting
        # ...and the walk's own name lets go of the last reading it met,
        # which would otherwise stay held through every later column.
        held = None
        # ONE STORAGE CLASS PER WORKBOOK COLUMN, or no weekday census
        # (landing 3b.1): a column whose dates are stored partly as dates
        # and partly as text is read back differently cell by cell.
        stored_one_way = True
        if table.sheet is not None and position - 1 < len(table.sheet.classes):
            stored_one_way = calendar_rules.stored_one_way(
                table.sheet.classes[position - 1]
            )
        def described_from(
            column_cells: "list[str]",
            reading: "taxonomy.HeldReading | None",
            held: bool = False,
            pinned: "grains.Reading | None" = None,
            units_kept: str = "",
            kept: "tuple[str, ...] | None" = None,
            as_code: bool = False,
            read_as_labels_here: bool = False,
            readings_kept: "list[taxonomy.HeldReading] | None" = None,
            as_text: bool = False,
        ) -> taxonomy.ColumnProfile:
            # A column the count in people holds is read under no other
            # declaration than the record number it is described as, as
            # the description then records it (`_without_held`). A column
            # written at a grain is read in the order its own cells were
            # (`_read_in_its_order`): every bucket starts on the first.
            # A POOL COUNTED IN PEOPLE (lane PL, plan P4-D453): the levels the
            # column keeps, chosen below or, in the validator, read off the
            # block it checks -- and read as labels there, as its producer
            # read it, with nothing recorded as declared that nobody declared.
            if kept is None and levels_kept_only is not None and name in levels_kept_only:
                kept = levels_kept_only[name]
                as_code = True
            read_under = (
                _without_held(settings, [name])
                if held
                else _read_in_its_order(settings, pinned)
            )
            if kept is not None and not held:
                read_under = dataclasses.replace(
                    read_under, levels_kept=frozenset(kept)
                )
            # THE NAMES OF RARE LEVELS (lane CODES-2, plan P4-D471): how this
            # column may name its held-back levels, `_held_back_named_here`.
            named_how = _held_back_named_here(
                name,
                no_safe_harbor,
                rare_values_released,
                withheld_names,
                described_identifiers,
                names_checked_only,
                table.n_rows >= parsing.TABLE_ROW_FLOOR,
            )
            if named_how and not held:
                read_under = dataclasses.replace(
                    read_under, held_back_named=named_how
                )
            return taxonomy.profile_column(
                name,
                position,
                column_cells,
                table.n_rows,
                read_under,
                name in described_identifiers,
                (
                    name in declared_codes
                    or as_code
                    or read_as_labels_here
                    or (
                        name in read_as_labels
                        and read_as_labels[name] == taxonomy.KEPT_DATED_LABELS
                    )
                )
                and not held,
                name in declared_measurements and not held,
                name in declared_commas and not held,
                name in read_as_pairs,
                kept_days[name] if name in kept_days else (),
                judged_here[name] if name in judged_here else (),
                reading,
                calendar_censuses,
                stored_one_way,
                storage[position - 1] if position - 1 < len(storage) else "",
                # -- 3b.R4 (P4-D384): the unit a validator reads a column
                # of counted dates at, the one its description published.
                counted_unit=(
                    counted_units[name]
                    if counted_units is not None and name in counted_units
                    else 0
                ),
                # -- UN-1a (P4-D438): the validator's carried affixed reading,
                # and the reading kept from before it (the count in people,
                # or the validator's carried labels).
                described_as_affixed=name in read_as_affixed and not held,
                units_kept=(
                    units_kept
                    if units_kept or held or name not in read_as_labels
                    else read_as_labels[name]
                ),
                kept=readings_kept,
                # -- lane NOTES (P4-D481): a column of sentences as free text,
                # and the validator's hand-over of one its description read so.
                forced_text=as_text and not held and described_text is None,
                described_as_text=as_text and not held and described_text is not None,
                # ...the reading handed over here being the one this column's
                # first description found a column of sentences (lane NOTES's
                # repair 1): its free-text block is built from it at once.
                sentences_read=as_text and reading is not None,
            )

        # THE SETTLED READING KEPT FOR THE CHAIN (lane CHs, plan P4-D462;
        # the orchestrator's LANE CHs RULINGS 2 (2)): in a switched describe
        # the reading this column is described from is kept as the chain
        # reads it (`taxonomy.keep_spellings`: one entry a distinct
        # spelling, with every argument it was read under), and the reading
        # itself is let go here, one column at a time. The chain takes it
        # only where it would read under the same arguments.
        # ...AND KEPT FOR A COLUMN OF SENTENCES (lane NOTES, plan P4-D481), whose
        # free-text description below is worked out from it, not read again;
        # any other column's reading is let go here as before.
        readings_here: "list[taxonomy.HeldReading] | None" = []
        described = described_from(cells, handed_over, readings_kept=readings_here)
        handed_over = None
        sentences_reading = readings_here[0] if readings_here and described.sentences else None
        # THE RULE AN OFFSET FOLLOWS, DECIDED ON THE CELLS AS HANDED (lane DST's
        # repair 2, Codex's items 3 and 6): on a description's own table, the
        # rule its stamps were read under; where a published rule is checked
        # (``rules_published``, validation's redescription), that rule where
        # every stamp keeps it over its family's whole calendar and both its
        # offsets are worn (`grains.wears_the_rule`), none where one breaks it.
        # A grain's description carries this verdict, never one read again off
        # cells coarsened at their own offsets, which a cell in the hour the
        # clocks skip could pass as valid.
        offset_verdict = _offset_rule_of(described)
        if rules_published is not None and name in rules_published:
            offset_verdict = _kept_rule(
                cells, _stamp_reading(described), rules_published[name], frozenset(described.absent_spellings)
            )
            described = _with_offset_rule(described, offset_verdict)
        if kept_spellings is not None and readings_here:
            _keep_for_the_chain(kept_spellings, position - 1, readings_here[0], described, described_identifiers)
        readings_here = None
        # THE UNIT OF THE COLUMN'S AGES, read before the date rule below,
        # which keeps as an age every count no older than 125 years in it
        # (limit (h) of plan P4-D446, wired at lane SH3's merge), and by the
        # Safe Harbor numbers after it. The validator reads first the mark
        # the description published (``top_coded_only``).
        # IN THE UNIT ITS NAME STATES (lane SH3, plan P4-D454): `1300`
        # in `age_in_months` is 108 years, not 1,300 -- or, where the name
        # states none, the unit its Safe Harbor question was answered with:
        # a unit written in a cell, then the name's, then the answer's
        # (lane SH3's repair, the orchestrator's LANE SH3 RULINGS 1 (3),
        # Codex's item 7: `months` answered under `age_in_days` read days as
        # months and published percentiles past 32,871 days).
        # ...NEVER THE NAME OF A COLUMN AN OPEN QUESTION HOLDS (the
        # orchestrator's LANE I4m RULINGS 21 (1), Codex's review of batch
        # 4o, item 1): `age_key` holding record numbers `00001` to `02000`,
        # its question unanswered, was top-coded by its name, its hold and
        # its exclusions read from the top-coded cells, and its twin wrote
        # 19,600 real keys at 20,000 rows. Such a column is read as its
        # cells and its answers read it, as before lane SH3, until an
        # answer says it holds ages.
        name_read = name not in withheld_names
        unit_named = taxonomy.age_mark_named(name) if name_read else 0
        unit_answered = (
            ages_counted_in[name]
            if ages_counted_in is not None and name in ages_counted_in
            else 0
        )
        named_mark = unit_named if unit_named else unit_answered
        # ...and a column the name says holds ages, or answered with a
        # unit, is reached in years where nothing states another unit,
        # whatever share of its cells lies past 125 (the orchestrator's
        # LANE SH3 RULINGS 2 (1)).
        age_named = bool(named_mark) or (
            name_read and taxonomy.named_as_an_age(name)
        )
        units_in_cells = False
        words_in_cells = False
        mark_here = (
            top_coded_only[name]
            if top_coded_only is not None and name in top_coded_only
            else (named_mark if named_mark else taxonomy.TOP_CODE)
        )
        # DATES IN DISGUISE (plan P4-D446, lane CZ-H): in a column read as
        # labels or as numbers, a value that reads as a date -- a day count,
        # epoch seconds, a date as text
        # (`date_counts.dated_values_blanked`) -- is read as a blank cell
        # while the column's Safe Harbor question about them is open or
        # answered yes, so no level, rung, tail or twin cell is a person's
        # date; `no` TO THAT QUESTION (``dated_values_no``) describes the
        # column as before, byte for byte, and so does `measurement` where
        # it answers Q3, the question about dates. `no` to the column's age
        # or ZIP question frees its top-code or its ZIP hold and nothing
        # else (the orchestrator's LANE CZ-H RULINGS 6 (1), item 3). The
        # command's rule, as the top-code is (``top_code``); not where a
        # question holds the column whole. Named on the description the
        # questions are worked out from; blanked on the one written
        # (``dated_held``). IT DECIDES BEFORE THE AGE TOP-CODE (LANE CZ-H
        # RULINGS 5 (1)): a cell it holds is blank and never top-coded, and
        # the age reach reads the cells it leaves -- 19,200 ages of 40 to
        # 100 beside 800 admission days `66274` printed `66274` as p99 and
        # the maximum, the reach setting them aside as values past 125
        # (Codex's review of lane CZ-H's first repair, item 1).
        dated_here = False
        held_as_labels = False
        dated_cells: "list[str] | None" = None
        cells_as_written = cells
        role_as_written = described.role
        absent_here = frozenset(described.absent_spellings)
        if (
            top_code
            and top_coded_only is None
            and name not in no_dates
            and name not in withheld_names
            and described.role in _DATED_VALUE_ROLES
            and not _date_question_answered_no(described, name in declared_measurements)
            and not _declared_as_dates(settings, name)
            and name not in dates_answered
            and (dated_values is not None or name in dated_held)
        ) or (
            # THE VALIDATOR reads a checked file as its description read it:
            # the columns whose dates in disguise the description held hold
            # them here too, so the real table meets its own description.
            not top_code and dated_values is None and name in dated_held
        ):
            # A count no older than the oldest age the age reach reads is an
            # age, whatever band it lies in: 125 years, the reach's own
            # ceiling (`taxonomy.TOP_CODE_REACH_CEILING`), so in years no
            # count of five figures or more is one -- READ IN THE UNIT OF
            # THE COLUMN'S AGES (limit (h), wired at lane SH3's merge): its
            # mark (`mark_here`, plan P4-D454) stands for 90 years, so 125
            # years are 1,500 months, 6,520 weeks or 45,654 days, as the age
            # reach reads them, and ages written in days keep every age and
            # hold only the day counts past it.
            dated_cells = date_counts.dated_values_blanked(
                cells,
                absent_here,
                taxonomy.TOP_CODE_REACH_CEILING * mark_here / taxonomy.TOP_CODE,
            )
            if dated_cells is not None:
                if dated_values is not None:
                    dated_values += [name]
                if name in dated_held:
                    # A HOLD MOVES NO ROLE (the statistics skeptic of lane
                    # CZ-H, item 8): an answer column read as labels whose
                    # date text pushed it over the labels' line is still
                    # labels, or its number half would be read as numbers
                    # beside labels and the twin miss it.
                    recoded = described_from(dated_cells, None)
                    if (
                        described.role in _DATED_LABEL_ROLES
                        and recoded.role == taxonomy.ROLE_COMPOUND
                    ):
                        recoded = described_from(dated_cells, None, read_as_labels_here=True)
                        held_as_labels = True
                    cells = dated_cells
                    described = taxonomy.with_dated_values_held(recoded)
                    dated_here = True
        # A COLUMN WHOSE PRESENT CELLS ARE TOO FEW TO COUNT (lane PL, plan
        # P4-D453; the orchestrator's LANE CZ-D RULINGS 1 (2)). One to ten
        # people fill it, or one to ten rows where no subject column
        # repeats: with no level it may publish, its count of cells is
        # itself the size of a group of one to ten, and for a yes-only
        # column a NAMED group. It is counted absent and written blank; the
        # description says the count is not published, and the validator
        # reads a checked file's present cells of it as blank, so the real
        # table meets it. A question offering `identifier` holds such a
        # column as P4-D401 holds it, unchanged, while it is open; a column
        # declared or answered a record number is counted absent too, its
        # count a group of one to ten whatever it is called (lane PL's
        # repair 1, skeptic 1's item 2).
        if counted_absent_only is not None:
            thin_here = name in counted_absent_only
        else:
            thin_here = (
                not declarations_are_reconstructed
                and time_grains is None
                and name not in withheld_names
                and _present_too_few(
                    cells,
                    frozenset(described.absent_spellings),
                    [
                        subject_cells[place]
                        for place in range(len(subject_names))
                    ],
                    subject_enough,
                    settings.small_cell_floor,
                    table.n_rows,
                )
            )
        if thin_here:
            kept_absent = frozenset(described.absent_spellings)
            # ...A COLUMN OF TEXT STAYS TEXT (the orchestrator's LANE PL
            # RULINGS 1 (1)): where a present cell reads as no number, the
            # twin writes a word in the floor's number of its cells, a
            # constant that says nothing of the real count, from a start
            # that reads nothing real (RULINGS 2 (1)).
            words = counted_absent_only is None and _reads_as_text(
                cells, kept_absent
            )
            cells = [
                "" if parsing.folded(cell) and cell not in kept_absent else cell
                for cell in cells
            ]
            if counted_absent_only is None:
                held_in_people += [name]
            described = taxonomy.as_counted_absent(
                described_from(cells, None, counted_absent_only is None),
                taxonomy.thin_word_start(settings, kept_absent) if words else "",
            )
            # ...AND THE DATE RULE ABOVE HAS READ FIRST (batch 4o's merge of
            # lanes CZ-H and PL): the cells counted here are those it leaves,
            # so the count of a column's other cells beside its held dates is
            # never a group of one to ten published; a column so counted absent
            # is read by the Safe Harbor reach below as it is written now, blank,
            # as every column counted absent is.
            cells_as_written = cells
            role_as_written = described.role
            dated_cells = None
        # THE SAFE HARBOR NUMBERS (plan P4-D427): while the column's Safe
        # Harbor question is open, every age over 89 is read as 90 for the
        # whole description, so no rung, mode, tail, level, bin, mean or
        # spread is one of those values, and every step below reads the
        # cells so written; a column of ZIP-shaped numbers is named for the
        # command to hold. A column held as record numbers -- by an open
        # question (P4-D401) or by the count in people (P4-D406) -- is held
        # from its top-coded cells and keeps the key, so its layouts name
        # no age over 89 and the validator reads the checked file the same
        # way (Codex's review of lane SH, item 2). The reach reads the cells
        # the date rule leaves (above).
        forced_top = top_coded_only is not None and name in top_coded_only
        # ...AND THE AGE WORDS AROUND ITS NUMBERS (lane HB2, plan P4-D477):
        # read by the reach and the top-code (`Age 95` is 95, written `Age
        # 90`), and recorded where a cell holds them (`top_coded_words`), so
        # a description the validator reads again is read as it was made --
        # with them only where it records them, as a description written
        # before them never does.
        words_here = (
            top_words_only is not None and name in top_words_only
            if forced_top
            else True
        )
        words_recorded = False
        # ...and the ends its ages were pooled into in people, where they were
        # (plan P4-D477), with the cells as they stood before.
        ends_here: "tuple[int, int] | None" = None
        # ...and the ages each end band is written as, the mean age of its rows
        # (lane RX-1, `taxonomy.ends_band_values`), where they keep every
        # count in people the edges kept; None writes each band at its edge.
        band_values_here: "tuple[int, int] | None" = None
        cells_before_ends: "list[str]" = []
        top_coded_here = False
        top_pool_floor = -1
        top_pool_people: "tuple[str, ...]" = ()
        # ...and whether its bands of ages past 89 are read as one band: a
        # description read again reads them only where it records so
        # (`top_coded_bands`; plan P4-D472, the orchestrator's LANE CZ-E
        # RULINGS 6 (3): a description made before the band reading
        # validates as it did), and whether this description wrote any.
        bands_read = not forced_top or (top_banded_only is not None and name in top_banded_only)
        top_banded = False
        reach = ""
        # ...and whether only the column's name put it in the age reach (lane
        # SH3's rule), its cells read in years reaching nothing: such a column
        # is never held from the cells the top-code wrote (below).
        reached_by_name = False
        # ...and whether lane HB3-a2's widening read it in the reach (plan
        # P4-D486, W (1)): its cells reach no age past 89, so where the count
        # in people still holds it, it is held from them as before.
        widened_whole = False
        # LANE SH2'S WHOLE-COLUMN HOLDS ARE ASKED FIRST (plan P4-D434; its
        # repair 1, Codex item 2): a column named as a place, or holding a
        # device number or a ZIP area, is held whole, and neither the
        # ages' top-code nor the years' publishes it meanwhile -- county
        # codes `001` to `101` answered `code` were top-coded as ages and
        # published three real counties and a fourth as `090`.
        held_first = ""
        if (
            top_coded_only is None
            and year_top_coded_only is None
            and top_code
            and harbor_year
            and name not in no_safe_harbor
            and name not in withheld_names
        ):
            held_first = taxonomy.safe_harbor_hold(
                name,
                described,
                cells,
                name in declared_commas,
                settings.small_cell_floor,
                harbor_year,
                taxonomy.counted_member(taxonomy.counted_for_the_column(settings, name)),
                # ...and whether its question about dates in disguise was
                # answered `no`: the value readers never ask it again
                # (plan P4-D472).
                name in no_dates,
            )
        if (
            top_coded_only is None
            and top_code
            and name not in no_safe_harbor
            and (
                role_as_written not in taxonomy.SAFE_HARBOR_UNREACHED_ROLES
                or name in withheld_names
            )
        ):
            # ...AN AGE WORD BEFORE ITS NUMBERS SAYS, AS ITS NAME WOULD, THAT
            # IT HOLDS AGES, BEFORE THE REACH IS DECIDED (lane HB2's repair 2;
            # Codex's item 2, the orchestrator's LANE HB2 RULINGS 5 (2)): a
            # column named `record_label` writing `Age 18` to `Age 105` on
            # 18,000 cells and `Age 126` to `Age 225` on 2,000 was taken out of
            # the reach by its strays past 125 before its words were read, and
            # published `Age 95` and wrote it in its twin, where the same cells
            # named `age` were top-coded.
            words_named = taxonomy.ages_written_with_words(
                cells_as_written, name in declared_commas, frozenset(described.absent_spellings)
            )
            # ...and whether its name or an answer says it holds ages,
            # whatever holds its name meanwhile: such a column never leaves
            # the reach by the units its cells write (lane HB3-a2, plan
            # P4-D486, the reading rule R).
            said_age = taxonomy.named_as_an_age(name) or bool(unit_answered)
            # ...AND A NAME THAT NAMES A MEASUREMENT NO AGE IS keeps the
            # column out of the age reach (lane RX-1, the fidelity plan's R3,
            # under the owner's ruling of 2026-11-15: the age cap is for
            # ages): `oxygen_saturation`, `temp_f`, `pulse`, `pain_score`,
            # a key named so in a long table. Read where the name is read
            # (never a column an open question holds), and never where a
            # unit of age is named or answered or a cell names an age.
            measured_name = name_read and not named_mark and taxonomy.named_as_a_measurement(name)
            reach = _reach_here(
                cells_as_written,
                dated_cells,
                name in declared_commas,
                frozenset(described.absent_spellings),
                settings.small_cell_floor,
                role_as_written in taxonomy.SAFE_HARBOR_LEVEL_ROLES,
                # ...and a column a person has said is a measurement or a
                # code -- P4-D401's padded question answered, or declared
                # -- is no longer judged a code by its leading zeros (the
                # second repair of lane SH, item 1: ages written `000` to
                # `120`, answered `measurement`, printed 91 to 105; and
                # its third, the orchestrator's ruling R2 of 2026-10-25:
                # answered `code` they printed 93 and 100 to 105, so a
                # column in the age reach is top-coded whatever its other
                # answer, and put the Safe Harbor question), nor is one
                # held meanwhile by an open question, which publishes
                # nothing: its held block is read from the top-coded
                # cells.
                name in declared_codes
                or name in declared_measurements
                or name in withheld_names,
                mark_here,
                age_named or words_named,
                said_age,
                measured_name,
            )
            reached_by_name = (
                reach == taxonomy.SAFE_HARBOR_AGES
                and age_named
                and not unit_answered
                and not words_named
                and _reach_here(
                    cells_as_written,
                    dated_cells,
                    name in declared_commas,
                    frozenset(described.absent_spellings),
                    settings.small_cell_floor,
                    role_as_written in taxonomy.SAFE_HARBOR_LEVEL_ROLES,
                    name in declared_codes
                    or name in declared_measurements
                    or name in withheld_names,
                    said=said_age,
                )
                != taxonomy.SAFE_HARBOR_AGES
            )
            # A COLUMN NAMED AS AN AGE WHOSE CELLS ARE PLAIN WHOLE AGES BELOW
            # THE TOP CODE, BESIDE A SUBJECT THAT REPEATS, IS READ IN THE AGE
            # REACH WHERE ITS COUNT IN PEOPLE WOULD HOLD IT (lane HB3-a2, plan
            # P4-D486, W (1); the orchestrator's LANE HB2 RULINGS 4 (3)): a
            # visit table's ages capped at 89 were held whole as record
            # numbers -- one age of the youngest or the oldest held by 1 to 10
            # people -- and the twin wrote made-up keys (mean 555.8 against a
            # real 54.4), where the same ages with one person past 89 were
            # described. Lane HB2's ends' rounds then pool its ends in people,
            # the top code reading nothing past 89; where they free nothing
            # the column is held from its own cells, as before (below). Never
            # a column an open question holds (the orchestrator's LANE I4m
            # RULINGS 21 (1): its name is not read), nor one counted on fewer
            # rows than the table floor.
            if (
                reach == ""
                and name_read
                and taxonomy.named_as_an_age(name)
                and (table.n_rows >= parsing.TABLE_ROW_FLOOR or long_table_dates)
                and taxonomy.ages_whole_below_the_top_code(
                    cells, name in declared_commas, frozenset(described.absent_spellings)
                )
            ):
                below_people, below_enough = _subjects_beside(
                    name, subject_names, subject_cells, subject_enough
                )
                if below_people and _counted_in_subjects(
                    described, cells, below_people, settings.small_cell_floor, below_enough,
                    _plain_reading(described, name in declared_commas),
                ):
                    reach = taxonomy.SAFE_HARBOR_AGES
                    widened_whole = True
                below_people = []
            # (The fallback of lane SH3's build -- a column named `age`
            # whose values are no years read in the coarsest unit they fit
            # -- is withdrawn by the orchestrator's LANE SH3 RULINGS 2 (1):
            # it read years beside strays past 125 in months and published
            # every age from 90 to 105. Such a column is read in years
            # until its unit is answered.)
            if reach in (taxonomy.SAFE_HARBOR_AGES, taxonomy.SAFE_HARBOR_ZIPS):
                units_in_cells = taxonomy.ages_written_with_units(
                    cells, name in declared_commas, frozenset(described.absent_spellings)
                )
                # ...and an age word before its numbers says, as its name
                # would, that it holds ages (plan P4-D477).
                words_in_cells = taxonomy.ages_written_with_words(
                    cells, name in declared_commas, frozenset(described.absent_spellings)
                )
            # ...and a column whose name, cells or answer state its ages'
            # unit holds no ZIP code: ages in days younger than 90 are
            # published as numbers (RULINGS 1 (3)).
            if (named_mark or units_in_cells) and reach == taxonomy.SAFE_HARBOR_ZIPS:
                reach = ""
        if reach == taxonomy.SAFE_HARBOR_AGES and held_first:
            reach = ""
        # ...and a house number of five figures is held as a part of an
        # address, its question saying so, not as a ZIP code (plan P4-D454).
        if reach == taxonomy.SAFE_HARBOR_ZIPS and held_first == taxonomy.HELD_ADDRESS_PARTS:
            reach = ""
        # ...a description written before lane SH3's repair, which records
        # no pooling rule, is read again as it was made (Codex's item 4) --
        # but one that records the age words or the ends, which no such
        # description holds, is read with them (lane HB2's repair 2, Codex's
        # item 5: `top_coded_words` beside no `top_category_pooled` was read
        # by the older reader, which left `Age 95` as it was) -- and so is one
        # that records its band reading (`top_coded_bands`), which no such
        # description holds either (Codex's review of batch 4s, item 6; the
        # orchestrator's LANE I4s RULINGS 1 (2): `90-94` and `95+` beside no
        # pooling rule were published again where the generator wrote `90+`).
        before_sh3 = (
            forced_top
            and (top_pooled_only is None or name not in top_pooled_only)
            and not words_here
            and not (top_ends_only is not None and name in top_ends_only)
            and not (top_banded_only is not None and name in top_banded_only)
        )
        cells_before_ages = cells
        if forced_top or reach == taxonomy.SAFE_HARBOR_AGES:
            words_recorded = (
                words_here
                if forced_top
                else taxonomy.age_words_written(
                    cells, name in declared_commas, frozenset(described.absent_spellings)
                )
            )
            coded = (
                taxonomy.top_coded_cells_before_sh3(
                    cells, name in declared_commas, frozenset(described.absent_spellings)
                )
                if before_sh3
                else taxonomy.top_coded_cells(
                    cells, name in declared_commas, frozenset(described.absent_spellings),
                    mark_here, words_here, bands_read,
                )
            )
            banded_cells = (
                not before_sh3
                and bands_read
                and taxonomy.bands_top_coded(
                    cells, name in declared_commas, frozenset(described.absent_spellings), mark_here
                )
            )
            recoded = described_from(coded, None, read_as_labels_here=held_as_labels)
            if forced_top or (
                recoded.n_missing == described.n_missing
                and recoded.n_present == described.n_present
            ):
                # ...AND ITS PLACEHOLDERS SET ASIDE BEFORE ANY RUNG IS READ
                # (plan P4-D434, the orchestrator's LANE SH2 ADDENDUM 1):
                # `999` beside ages printed p99 99.09 and a mean of 106.8.
                aside = taxonomy.age_placeholders_set_aside(
                    coded,
                    name in declared_commas,
                    frozenset(described.absent_spellings),
                    settings.small_cell_floor,
                    mark_here,
                    words_here,
                )
                if aside != coded:
                    coded = aside
                    recoded = described_from(coded, None, read_as_labels_here=held_as_labels)
                # ...AND A TOP CATEGORY FEWER ROWS THAN THE FLOOR HOLD IS
                # POOLED WITH THE VALUE BELOW IT, never named (plan P4-D454:
                # six ages past 89 published `90.0` as a tail value).
                # The command's rule at the table floor and above (the
                # orchestrator's reading (3) of THE OWNER'S TABLE FLOOR,
                # amended 2026-10-25: a Safe Harbor top-code's size rule
                # reaches tables of 20,000 rows and more, below which the
                # command refuses the table and the library keeps its bytes).
                # IN PEOPLE TOO, beside each subject column that repeats
                # (lane SH3's repair, skeptic 1's item 6: 4 patients aged 92
                # to 101 on 40 rows of a long table were no pool of rows,
                # and the count in people then held the whole age column).
                # A description checked again pools as it records, and
                # never by a newer rule (Codex's item 4; the orchestrator's
                # LANE SH3 RULINGS 1 (2)): `top_category_pooled` and
                # `top_category_people`, written whether or not a category
                # was pooled. The patient table (``long_table_dates``, lane
                # GRa's patient layer alone) pools as a table at the floor
                # does, each patient a holder, as its rows' description pools
                # in people (batch 4p's merge of lanes GRa and SH3).
                pool_floor = (
                    settings.small_cell_floor
                    if table.n_rows >= parsing.TABLE_ROW_FLOOR or long_table_dates
                    else 0
                )
                pool_people: "tuple[str, ...]" = tuple(
                    subject for subject in subject_names if subject != name
                )
                if forced_top:
                    pool_floor, pool_people = (
                        top_pooled_only[name]
                        if top_pooled_only is not None and name in top_pooled_only
                        else (-1, ())
                    )
                pool_holders: "list[list[str]]" = []
                for subject in pool_people if pool_floor > 0 else ():
                    found_subject = False
                    for place_held, held_name in enumerate(subject_names):
                        if held_name == subject and not found_subject:
                            pool_holders += [subject_cells[place_held]]
                            found_subject = True
                    for place_named, column_name in enumerate(table.column_names):
                        if column_name == subject and not found_subject:
                            pool_holders += [
                                subject_keys(
                                    reading.column_values(table, place_named),
                                    settings.declared_missing_values,
                                )
                            ]
                            found_subject = True
                top_pooled = taxonomy.top_category_pooled(
                    coded,
                    name in declared_commas,
                    frozenset(described.absent_spellings),
                    max(pool_floor, 0),
                    mark_here,
                    pool_holders if pool_holders else None,
                    words_here,
                )
                pool_holders = []
                if top_pooled != coded:
                    coded = top_pooled
                    recoded = described_from(coded, None, read_as_labels_here=held_as_labels)
                top_pool_floor = pool_floor
                top_pool_people = pool_people if pool_floor > 0 else ()
                # ...AND ITS ENDS POOLED IN PEOPLE WHERE THE COUNT IN PEOPLE
                # WOULD HOLD IT (lane HB2, plan P4-D477; the orchestrator's
                # LANE GRb RULINGS 2 (2) and 3 (4)): a visit table's ages of
                # 3,000 patients, about 20,000 rows, were held whole as record
                # numbers -- its youngest ages, its first and 99th percentiles
                # and its largest each held by 4 to 10 patients -- so its twin
                # wrote two stand-ins a row and a twin patient held two ages.
                # Each end's values few people hold join one band the floor's
                # people hold, the column is described again and counted in
                # people again, and held as before only where that fails; a
                # description checked again reads the ends it records.
                cells_before_ends = coded
                if forced_top:
                    recorded = top_ends_only[name] if top_ends_only is not None and name in top_ends_only else None
                    ends_here = (recorded[0], recorded[1]) if recorded is not None else None
                    band_values_here = (
                        (recorded[2], recorded[3]) if recorded is not None and len(recorded) == 4 else None
                    )
                elif pool_floor > 0 and not reached_by_name:
                    # ...DESCRIBED AGAIN AND COUNTED IN PEOPLE AGAIN, at most
                    # `_END_ROUNDS` times: a value the pooled block still
                    # publishes that 1 to `floor` - 1 people hold (a bin's edge
                    # beside its low tail: `30`, 6 patients of 3,020) is taken
                    # into the band of the nearer end, and the ends drawn again;
                    # held as before where none is left to take.
                    ends_people, ends_enough = _subjects_beside(
                        name, subject_names, subject_cells, subject_enough
                    )
                    ends_held = bool(ends_people) and _counted_in_subjects(
                        taxonomy.with_top_code(recoded, mark_here, top_pool_floor, top_pool_people, words_recorded),
                        coded, ends_people, settings.small_cell_floor, ends_enough,
                        _plain_reading(recoded, name in declared_commas),
                    )
                    ends_low_need = -1
                    ends_high_need = -1
                    for _round in range(_END_ROUNDS if ends_held else 0):
                        ends_drawn = taxonomy.ends_pooled_in_people(
                            coded, name in declared_commas, frozenset(described.absent_spellings),
                            settings.small_cell_floor, mark_here, ends_people, words_here, ends_low_need, ends_high_need,
                        )
                        if ends_drawn is None and _round == 0:
                            # ...AND WHERE NEITHER END NEEDS A BAND BUT A VALUE
                            # FEW PEOPLE HOLD STANDS INSIDE (lane HB3-a2, plan
                            # P4-D486, W (4)): 10,000 people of 20 rows wrote
                            # `Age 3` for 9 people beside `Age 0` to `Age 2` held
                            # by more, every level published with its count, so
                            # the first draw found no band and the word forms
                            # were held whole where the plain column was
                            # described; that value is taken into the nearer
                            # band first, as a later round takes one.
                            ends_seeded = _ends_seeded(
                                coded, name in declared_commas, frozenset(described.absent_spellings),
                                taxonomy.with_top_code(recoded, mark_here, top_pool_floor, top_pool_people, words_recorded),
                                settings.small_cell_floor, mark_here, ends_people, words_here,
                            )
                            if ends_seeded is not None:
                                ends_low_need, ends_high_need = ends_seeded[2], ends_seeded[3]
                                ends_drawn = (ends_seeded[0], ends_seeded[1])
                        if ends_drawn is None:
                            break
                        ends_cells = taxonomy.cells_within_the_ends(
                            coded, name in declared_commas, frozenset(described.absent_spellings),
                            ends_drawn[0], ends_drawn[1], mark_here, words_here,
                        )
                        # ...each cell read as the block reads it and in the
                        # column's unit (lane HB2's repair 2, Codex's item 1).
                        ends_ages = taxonomy.ages_as_read(
                            ends_cells, name in declared_commas, frozenset(described.absent_spellings),
                            mark_here, words_here,
                        )
                        ends_described = described_from(ends_cells, None, read_as_labels_here=held_as_labels)
                        ends_candidate = taxonomy.with_top_ends(
                            taxonomy.with_top_code(ends_described, mark_here, top_pool_floor, top_pool_people, words_recorded),
                            ends_drawn[0], ends_drawn[1],
                        )
                        if not _counted_in_subjects(
                            ends_candidate, ends_cells, ends_people, settings.small_cell_floor, ends_enough,
                            _plain_reading(ends_described, name in declared_commas),
                        ):
                            # ...and every bin group it publishes held by the
                            # floor's people too, a group few people hold taken
                            # into the nearer band (lane HB2's repair 1).
                            ends_few = _groups_few(ends_candidate, ends_ages, ends_people, settings.small_cell_floor)
                            if not ends_few:
                                ends_here = ends_drawn
                                # ...EACH BAND WRITTEN AT THE MEAN AGE OF ITS ROWS
                                # (lane RX-1; P4-D486 (6)(e)), where the column
                                # so written keeps every count in people the
                                # edges kept; else at its edges, as before.
                                values_drawn = taxonomy.ends_band_values(
                                    coded, name in declared_commas, frozenset(described.absent_spellings),
                                    ends_drawn[0], ends_drawn[1], mark_here, words_here,
                                )
                                if values_drawn != ends_drawn:
                                    values_cells = taxonomy.cells_within_the_ends(
                                        coded, name in declared_commas, frozenset(described.absent_spellings),
                                        ends_drawn[0], ends_drawn[1], mark_here, words_here, values=values_drawn,
                                    )
                                    values_candidate = taxonomy.with_top_ends(
                                        taxonomy.with_top_code(
                                            described_from(values_cells, None, read_as_labels_here=held_as_labels),
                                            mark_here, top_pool_floor, top_pool_people, words_recorded,
                                        ),
                                        ends_drawn[0], ends_drawn[1], values_drawn,
                                    )
                                    if _band_values_keep_the_floor(
                                        values_candidate, values_cells, name in declared_commas,
                                        frozenset(described.absent_spellings), mark_here, words_here,
                                        ends_people, ends_enough, settings.small_cell_floor,
                                    ):
                                        band_values_here = values_drawn
                                break
                        else:
                            ends_few = _published_few(ends_candidate, ends_ages, ends_people, settings.small_cell_floor)
                        if not ends_few:
                            # ...or, where no value it publishes is few people's,
                            # the values of its remainder, the cells that read as
                            # none, where 1 to `floor` - 1 people hold it (lane
                            # HB2's repair 1; the statistics check's item 3).
                            ends_few = _remainder_few(ends_candidate, ends_ages, ends_people, settings.small_cell_floor)
                        ends_moved, ends_low_need, ends_high_need = _ends_asked(
                            ends_drawn, ends_few, ends_low_need, ends_high_need,
                        )
                        if not ends_moved:
                            break
                if ends_here is not None:
                    coded = taxonomy.cells_within_the_ends(
                        coded, name in declared_commas, frozenset(described.absent_spellings),
                        ends_here[0], ends_here[1], mark_here, words_here, values=band_values_here,
                    )
                    recoded = described_from(coded, None, read_as_labels_here=held_as_labels)
                cells = coded
                top_banded = banded_cells
                described = taxonomy.with_top_code(
                    recoded, mark_here, top_pool_floor, top_pool_people,
                    words_recorded, top_banded,
                )
                if ends_here is not None:
                    described = taxonomy.with_top_ends(described, ends_here[0], ends_here[1], band_values_here)
                if dated_here:
                    described = taxonomy.with_dated_values_held(described)
                top_coded_here = True
                if ages_established is not None and not forced_top:
                    # ...and what establishes it as ages beside its values,
                    # for the question's units and the meaning of `yes`.
                    ages_established[name] = (
                        taxonomy.AGE_UNIT_IN_CELLS if units_in_cells
                        else taxonomy.AGE_UNIT_IN_NAME if unit_named
                        else taxonomy.AGE_UNIT_ANSWERED if unit_answered
                        else taxonomy.AGE_NAMED if age_named or words_in_cells
                        else ""
                    )
            elif ages_held is not None:
                # 90 is one of the column's missing values, so reading its
                # ages as 90 would make them missing: held whole instead
                # until the question is answered (Codex's review, item 1).
                ages_held += [name]
            coded = []
        elif reach == taxonomy.SAFE_HARBOR_ZIPS and five_figures is not None:
            five_figures += [name]
        # THE SAFE HARBOR YEARS, PLACES AND DEVICES (plan P4-D434, lane
        # SH2): while the column's Safe Harbor question is open, a column
        # of years of birth is read with every year that shows an age of
        # 90 or more against the reference year written as
        # the latest such year ("that year or earlier"), as the ages are
        # read 90; a column of ZIP-shaped years stays lane SH's hold, so
        # no ZIP code that lost its nought is published as a year; and a
        # column of dates so early, of ZIP codes read as counted dates, of
        # device numbers, of ZIP codes cut to three figures, or named as a
        # place, is named for the command to hold whole.
        year_here = 0
        forced_year = (
            year_top_coded_only[name]
            if year_top_coded_only is not None and name in year_top_coded_only
            else 0
        )
        open_here = (
            top_coded_only is None
            and year_top_coded_only is None
            and top_code
            and name not in no_safe_harbor
            and name not in withheld_names
            and not top_coded_here
            and (five_figures is None or name not in five_figures)
            and (ages_held is None or name not in ages_held)
        )
        years_reached = (
            reach != taxonomy.SAFE_HARBOR_ZIPS
            and not held_first
            and not forced_year
            and open_here
            and bool(harbor_year)
            # ...and never a column whose name or answer states the unit of
            # its ages (lane SH3's repair, Codex's item 5: `1900` to `1999`
            # in `age_in_days`, a measurement, were read as years of birth).
            and not named_mark
            and described.role not in taxonomy.SAFE_HARBOR_UNREACHED_ROLES
            and taxonomy.safe_harbor_years(
                cells,
                name in declared_commas,
                frozenset(described.absent_spellings),
                settings.small_cell_floor,
                harbor_year,
            )
            # ...nor one whose cells write it (`1950 days`).
            and not taxonomy.ages_written_with_units(
                cells, name in declared_commas, frozenset(described.absent_spellings)
            )
        )
        if reach == taxonomy.SAFE_HARBOR_ZIPS:
            if (
                harbor_reasons is not None
                and harbor_year
                and taxonomy.safe_harbor_years(
                    cells,
                    name in declared_commas,
                    frozenset(described.absent_spellings),
                    settings.small_cell_floor,
                    harbor_year,
                )
            ):
                harbor_reasons[name] = taxonomy.HELD_YEARS
        elif open_here and held_first:
            # ...held whole: places, device numbers, ZIP areas, dates so
            # early and ZIP codes read as counted dates.
            held_for = held_first
            if five_figures is not None and harbor_reasons is not None:
                five_figures += [name]
                harbor_reasons[name] = held_for
            if held_for == taxonomy.HELD_DATES:
                # ...A COLUMN OF DATES SO EARLY IS HELD HERE, in every
                # description of the run, as lane PS holds dates few people
                # hold (plan P4-D417): described as a record number with the
                # record its twin writes valid dates from, so code that reads
                # the twin's dates as dates still runs (a held block's
                # made-up record numbers in a date's layout, `4102-11-65`,
                # parse as no date); the command puts the question, and
                # holds nothing more.
                time_reading = _time_reading(described, settings, name, declared_commas)
                described_identifiers += [name]
                held_in_people += [name]
                held_here = taxonomy.as_unanswered_identity(
                    described_from(cells, None, True)
                )
                if time_reading is not None:
                    held_here = taxonomy.with_held_dates(
                        held_here,
                        grains.record(
                            _held_dates_grain(
                                cells,
                                time_reading,
                                held_here.n_present,
                                frozenset(described.absent_spellings),
                            )
                        ),
                    )
                described = held_here
        elif forced_year or (
            years_reached
            and taxonomy.years_with_few_strays(
                cells,
                name in declared_commas,
                frozenset(described.absent_spellings),
                settings.small_cell_floor,
                harbor_year,
            )
        ):
            cutoff = forced_year if forced_year else taxonomy.year_cutoff(harbor_year)
            coded = taxonomy.year_top_coded_cells(
                cells,
                name in declared_commas,
                frozenset(described.absent_spellings),
                cutoff,
            )
            recoded = described_from(coded, None, read_as_labels_here=held_as_labels)
            if forced_year or (
                recoded.n_missing == described.n_missing
                and recoded.n_present == described.n_present
            ):
                cells = coded
                described = taxonomy.with_year_top_code(recoded, cutoff)
                # ...and a column whose values that read as dates are held
                # says so still (plan P4-D446, NF135), as the ages' top-code
                # does: the validator reads that remark to hold them too.
                if dated_here:
                    described = taxonomy.with_dated_values_held(described)
                year_here = cutoff
            elif five_figures is not None and harbor_reasons is not None:
                # ...a year of the group is one of the column's missing
                # values: held whole instead, as the ages are.
                five_figures += [name]
                harbor_reasons[name] = taxonomy.HELD_YEARS
            coded = []
        elif years_reached and five_figures is not None and harbor_reasons is not None:
            # ...YEARS OF BIRTH BESIDE AS MANY OTHER NUMBERS AS THE FLOOR'S
            # ROWS (two-figure years, `30` for 1930) are held whole: pooling
            # the years would leave the others showing them (lane SH2's
            # repair 1, skeptic 1 item 4).
            five_figures += [name]
            harbor_reasons[name] = taxonomy.HELD_YEARS_BESIDE
        # A PAIR OF COORDINATES READ FROM THEIR CELLS (plan P4-D434, the
        # orchestrator's LANE SH2 ADDENDUM 3): each column's reading as a
        # latitude or a longitude is kept -- held or answered columns too,
        # as the other of a pair -- and a column still open is held after
        # the walk where another column reads as a coordinate beside it
        # (`taxonomy.coordinates_held`); a column named as a coordinate is
        # held above (`taxonomy.safe_harbor_hold`).
        if (
            harbor_reasons is not None
            and five_figures is not None
            and top_code
            and harbor_year
            and top_coded_only is None
            and year_top_coded_only is None
            and described.role not in _NO_COORDINATE_ROLES
        ):
            coordinate_readings += [
                (
                    name,
                    taxonomy.coordinate_reading(
                        cells,
                        name in declared_commas,
                        frozenset(described.absent_spellings),
                    ),
                )
            ]
            if (
                open_here
                and not held_first
                and not reach
                and not year_here
                and name not in five_figures
                and name not in described_identifiers
                and described.role not in taxonomy.ROLES_PUBLISHING_NOTHING
            ):
                coordinates_open += [name]
        dated_cells = None
        cells_as_written = []
        # A FEW-VALUED COLUMN WITH A WIDE GAP (lane GG, plan P4-D440; the
        # stand-ins page's ZS.4): it publishes its own numbers only after
        # `no` to its Safe Harbor question, and is named meanwhile for the
        # command to put that question -- unanswered it is the block it
        # was, byte for byte. Not where a question holds it, and not where
        # the top-code reads its ages, whose question is SH's own.
        counting: "list[list[str]]" = []
        counting_enough: "list[bool]" = []
        counting_dates: "list[bool]" = []
        for place, subject_name in enumerate(subject_names):
            if subject_name != name:
                counting += [subject_cells[place]]
                counting_enough += [subject_enough[place]]
                counting_dates += [dates_in_people[place]]
        # ...AND NOT WHERE THE LIST WOULD BE HELD IN PEOPLE (Codex's review
        # of lane GG, item 5): a score whose `7` is one patient's, 20 rows,
        # named few-valued before the count in people held it, so its
        # question offered `no` with a list `no` could never release. The
        # count in people reads the block as `no` would publish it, list
        # and all; where it holds that block, the column is not of the
        # class and is described as before, by the steps below.
        if (
            described.few_values
            and not top_coded_here
            and reach == ""
            and name not in withheld_names
            # ...and not where lane SH2 holds the column whole or reads its
            # years (plan P4-D434): its question is SH2's, one question a
            # column, HIPAA first (batch 4m's merge of lanes GG and SH2).
            and not year_here
            and (five_figures is None or name not in five_figures)
            and not (
                not declarations_are_reconstructed
                and _counted_dates_declined(settings, name, described, cells_as_read)
            )
            and not (
                counting
                and name not in described_identifiers
                and _counted_in_subjects(
                    taxonomy.with_few_values(described),
                    cells,
                    counting,
                    settings.small_cell_floor,
                    counting_enough,
                    _CellReading("", name in declared_commas),
                )
            )
        ):
            if _few_values_released(name, no_safe_harbor):
                # RULE U (c) (the stand-ins page's ZS.1 and ZS.3; repair 1
                # of lane GG, its skeptic 1, item 3): `no` widens what is
                # published, so a list naming a value fewer cells than the
                # floor hold waits while a question offering `identifier`
                # is open on any column; unanswered meanwhile, as before.
                if _rare_list_released(
                    described.few_values_rare, rare_values_released
                ):
                    described = taxonomy.with_few_values(described)
                    if described.few_values_rare and rare_listed is not None:
                        rare_listed += [name]
            elif few_valued is not None:
                few_valued += [name]
        # A COLUMN OF SENTENCES IS DESCRIBED AS FREE TEXT (lane NOTES, plan
        # P4-D481; the orchestrator's LANE NOTES RULINGS 1 (3) and (5)):
        # where its reading would publish its levels and half or more of its
        # present cells are sentences, and nothing else holds it -- a Safe
        # Harbor hold keeps precedence and its reason (N5), a declared or
        # held record number stays one, an open question offering
        # `identifier` keeps it held, and the ages' or years' top-code keeps
        # its own question -- before the count in people, so its hold of a
        # level few people hold (which published each sentence's layout and
        # generated slowly) gives way to free text (N10). A validator's
        # re-description reads a column its description read as labels as
        # labels; given the validator's hand-over (``described_text``) it
        # reads exactly the columns named there as free text.
        as_text_here = False
        if described_text is not None:
            as_text_here = name in described_text and described.role in taxonomy.SENTENCE_ROLES
        elif (
            described.sentences
            and described.role in taxonomy.SENTENCE_ROLES
            and not held_first
            and name not in withheld_names
            and name not in described_identifiers
            and (five_figures is None or name not in five_figures)
            and (harbor_reasons is None or name not in harbor_reasons)
            and not top_coded_here
            and not year_here
            and name not in read_as_labels
            and not (levels_kept_only is not None and name in levels_kept_only)
        ):
            as_text_here = True
        if as_text_here:
            # ...its dates in disguise still held where they were (plan
            # P4-D446): the cells read are those the date rule left, and the
            # remark the validator reads them by stays. The reading kept above
            # is taken where it is of these cells under these arguments
            # (`taxonomy.profile_column`'s hand-over), else they are read again.
            described = described_from(cells, sentences_reading, as_text=True)
            if dated_here:
                described = taxonomy.with_dated_values_held(described)
        sentences_reading = None
        # COUNTED IN PEOPLE, NOT ROWS (plan P4-D406). A column of record
        # numbers names no layout fewer than the floor's number of
        # subjects wear, before its census of repetition is drawn from
        # its layouts.
        # COUNTED IN EVERY SUBJECT COLUMN BUT ITSELF: a subject column's
        # own values are counted in the others too (Codex's review of lane
        # HX2, item 4: a candidate of the person question that is not held
        # by its own question publishes no value one to ten people of
        # another subject column hold).
        # ...and a subject column's own layouts are counted in every
        # OTHER subject column (lane HX2's skeptic, round 2, item 3): a
        # plan number declared beside the patient names no layout three
        # patients' plans wear. A person column's layouts are not counted
        # in its own people (plan P4-D406's stated limit (c), lane MG): a
        # placeholder key such as `UNKNOWN`, one subject on a few rows,
        # would pool every layout of the column.
        if counting:
            described = _layouts_in_subjects(
                described,
                cells,
                counting,
                counting_enough,
                settings.small_cell_floor,
            )
        real_census = _census_of(described)
        # A column of dates is counted in every subject column that repeats
        # (`dates_in_people`); any other as P4-D406 counts it.
        people_enough = (
            counting_dates
            if described.role == taxonomy.ROLE_DATETIME
            else counting_enough
        )
        # EVERY DATE IS COUNTED, IN PEOPLE OR ELSE IN ROWS (plan P4-D433,
        # lane PS2). A full date is a Safe Harbor element whoever's rows it
        # sits on: where no subject column beside the column counts in
        # people -- a table of one row a person, whose person column never
        # repeats, or one with no person column -- each ROW is its own
        # holder, so a percentile, a tail, a mode or a census day that one
        # to ten rows hold is pooled or held as one that one to ten people
        # hold is (`_counted_in_subjects`, `_grain_walk`). On one row a
        # person a row IS a person. Counting in rows is implied by counting
        # in people, so a column a subject column counts in people is
        # counted as before; a column whose every published date the floor's
        # rows already hold keeps its bytes. Clock times of day, which name
        # no date, are not reached.
        # IN ROWS THE DATE IS COUNTED, not the instant: each published
        # point's calendar day (its month, its quarter where it names one)
        # against the rows that fall on it (`_dates_few_in_rows`), so a
        # stamp whose every published day the floor's rows hold keeps its
        # time of day and its bytes; only where one does not is the column
        # walked down its ladder, each row its own holder.
        # AT THE TABLE FLOOR AND ABOVE: the command describes no table
        # under `parsing.TABLE_ROW_FLOOR` rows (plan P4-D425), so the count
        # in rows reaches every table a description is published of; the
        # library keeps its bytes below it, where the suite's fixtures of a
        # few hundred rows test what each date column does (measured: the
        # count there turned 581 cases of stage 3b's 28 test files red).
        # DECIDED ONLY WHERE A DESCRIPTION IS MADE (repair round 1, Codex's
        # item 3): the validator hands the grains its description published
        # (``time_grains``, empty where it named none) and reads each
        # column at that grain or at none, so an unchanged source still
        # meets a description written before this count, or without it.
        in_rows = (
            described.role == taxonomy.ROLE_DATETIME
            and not any(people_enough)
            and (table.n_rows >= parsing.TABLE_ROW_FLOOR or long_table_dates)
            and time_grains is None
            and not declarations_are_reconstructed
        )
        # The walk counts the rows beside every subject column there is (a
        # subject column of fewer than the floor's people, attached to the
        # column, still holds it, as P4-D406 holds it), each row its own
        # holder with no text a row (`in_rows`; lane SR2a, plan P4-D463).
        walking = counting
        walking_enough = people_enough
        # DATES DECLARED AS COUNTS AND NOT READ AS DATES are never
        # published as plain numbers (the orchestrator's LANE HX2 ADDENDUM
        # 2, from lane AQ's close verify): `42.345` for an Excel day leaves
        # the column read as a count, whose mean and points are those
        # dates, so it is held whole -- ON EVERY TABLE, one row a person as
        # well as several (the orchestrator's ruling on lane HX2's second
        # verify, item 3): 600 such days beside 600 patients, one row each,
        # published their mean and percentiles, each date a person's own.
        # A PERSON'S declaration only: the validator hands over the
        # description's (`declarations_are_reconstructed`), and a checked
        # file whose counts do not read so is described as before, which
        # is how its report says what it misses.
        declined = (
            not declarations_are_reconstructed
            and name not in withheld_names
            and name not in described_identifiers
            and _counted_dates_declined(settings, name, described, cells_as_read)
        )
        cell_reading = _CellReading(
            taxonomy.counted_member(
                taxonomy.counted_for_the_column(settings, name)
            )
            if described.role == taxonomy.ROLE_DATETIME
            else "",
            name in declared_commas,
            # A NUMBER BESIDE A UNIT IS COUNTED AS THE SAME NUMBER WRITTEN
            # BARE (lane UN-1b, plan P4-D443; the orchestrator's LANE UN-1a
            # RULINGS 2 (2)): `98.4 F` is the 98.4 its block prints, so
            # the count in people reads it as it reads `98.4`.
            described.role == taxonomy.ROLE_AFFIXED,
            _published_wrappers(described.details)
            if described.role == taxonomy.ROLE_AFFIXED
            else (),
        )
        # THE GRAIN A DESCRIPTION PUBLISHED IS READ, NEVER DECIDED (plan
        # P4-D417): the validator describes a checked file's cells at the
        # rung its description named, the tails pooled into its ends.
        published_grain = (
            time_grains[name]
            if time_grains is not None and name in time_grains
            else None
        )
        held_dates: "grains.Grain | None" = None
        read_at_its_grain = (
            published_grain is not None
            and published_grain.rung != grains.HELD
            and name not in withheld_names
            and not declined
        )
        # COUNTED IN PEOPLE FIRST (P4-D406), and only where no person
        # holds it back, in rows (P4-D433): a column a subject column holds
        # keeps that subject's evidence.
        reaches_the_count = (
            not read_at_its_grain
            and name not in withheld_names
            and not declined
            and name not in described_identifiers
        )
        held_by_people = (
            reaches_the_count
            and bool(counting)
            and _counted_in_subjects(
                described,
                cells,
                counting,
                settings.small_cell_floor,
                people_enough,
                cell_reading,
            )
        )
        # ...AND EVERY BIN GROUP ITS INTERIOR PUBLISHES HELD BY THE FLOOR'S
        # PEOPLE (lane HB3-a2, plan P4-D486; the orchestrator's LANE HB3-a
        # RULINGS 4 (3) (i)): a group fewer hold is joined to its neighbour,
        # and a column whose whole interior fewer hold is held. A column of
        # dates or times is counted at its grain (P4-D417), not here; and a
        # checked file the validator describes again is read as before, so
        # a description written before this lane validates as it did.
        if (
            reaches_the_count
            and counting
            and not held_by_people
            and not declarations_are_reconstructed
            and described.role not in (taxonomy.ROLE_DATETIME, taxonomy.ROLE_CLOCK)
        ):
            grouped = _groups_in_people(
                described, cells, counting, settings.small_cell_floor, people_enough, cell_reading,
            )
            if grouped is None:
                held_by_people = True
            else:
                described = grouped
        by_rows = (
            reaches_the_count
            and in_rows
            and not held_by_people
            and _dates_few_in_rows(
                described, cells, settings.small_cell_floor, cell_reading
            )
        )
        # A COLUMN THE COUNT IN PEOPLE HOLDS IS HELD FROM ITS CELLS AS
        # WRITTEN WHERE ONLY ITS NAME READ IT AS AGES (the orchestrator's
        # LANE I4m RULINGS 21 (1), Codex's review of batch 4o, item 1): its
        # hold and its exclusions are read off the real values, as before
        # lane SH3, never off the cells the top-code wrote -- record numbers
        # `1` to `1000` in `age_key` beside a person column, top-coded by
        # the name, were held from `1` to `90` and their twin wrote real
        # keys. A column whose cells reach the ages keeps lane SH's hold from
        # its top-coded cells (Codex's review of lane SH, item 2).
        if (reached_by_name or widened_whole) and top_coded_here and held_by_people:
            cells = cells_before_ages
            top_coded_here = False
            if ages_established is not None and name in ages_established:
                del ages_established[name]
        cells_before_ages = []
        if read_at_its_grain and published_grain is not None:
            if absent_read is not None:
                absent_read[name] = described.absent_spellings
            pooled_cells = grains.coarse_cells(
                cells, published_grain, None, frozenset(described.absent_spellings), offset_verdict,
            )
            described = taxonomy.with_time_grain(
                _with_offset_rule(
                    described_from(pooled_cells, None, False, published_grain.reading),
                    _kept_rule(pooled_cells, published_grain.reading, offset_verdict, frozenset(described.absent_spellings)),
                ),
                grains.record(published_grain),
                in_rows,
            )
            pooled_cells = []
        elif name in withheld_names:
            described = taxonomy.as_unanswered_identity(described)
            if name in spelled_held:
                # ...WHATEVER THE ANSWER (lane ID-ROOM4, plan P4-D489): its
                # own sentence, since an answer may have been given.
                described = dataclasses.replace(
                    described,
                    detection_evidence=taxonomy.note(
                        taxonomy.EVIDENCE_MADE_UP_SPELLED_REAL
                    ),
                )
        elif declined or held_by_people or by_rows:
            # DATES AND TIMES POOLED IN PEOPLE (plan P4-D417): described at
            # the grain their published facts choose where every point it
            # publishes holds the floor in people, else held with the
            # record their twin writes valid values from.
            pooled: "taxonomy.ColumnProfile | None" = None
            time_reading = (
                None
                if declined
                else _time_reading(described, settings, name, declared_commas)
            )
            if time_reading is not None:
                # ...ON THE CLOCK THE BLOCK PUBLISHES: where the column's
                # stamps follow a rule (lane DST, plan P4-D474, repair 1, the
                # statistics check's item 1), its description prints ONE text
                # for each bucket, its start at the offset the rule puts in
                # force there (`_cells_at`, `grains.coarse_cell`), so the walk
                # counts each bucket whole, as it prints it, and not each of
                # its two offsets apart: split, the side of a bucket a change
                # of the clocks cuts thin marked the month and the quarter
                # thin, the walk stepped back to the year, where the rule
                # cannot stand, and the twin spent its offsets by counts
                # (9,684 to 10,043 of 20,000 cells off their date on eight
                # columns of the check's invented tables). The step back's
                # count of the printed candidate (`_counted_in_subjects`)
                # stands as before, on whatever `_cells_at` prints.
                # ...AND A RULE IS NOT ADMITTED AT A RUNG FINER THAN THE HOUR
                # ACROSS AN HOUR THE CLOCKS REPEAT (lane DST's repair 2, Codex's
                # item 1): there each bucket of the hour holds both its
                # occurrences' instants while its start names only the first,
                # so no placement of the twin's instants keeps both the census
                # and the buckets' counts; the column is walked again as it was
                # before the rule, and keeps that description and its bytes.
                for ruled in (offset_verdict, "") if offset_verdict else ("",):
                    pooled = None
                    chosen: "tuple[str, int, int] | None" = None
                    walked = _grain_walk(
                        cells,
                        described.n_present,
                        time_reading,
                        walking,
                        walking_enough,
                        settings.small_cell_floor,
                        frozenset(described.absent_spellings),
                        _on_the_shared_clock(_column_block(described)) and not ruled,
                        in_rows,
                    )
                    held_dates = _held_record(walked.grain)
                    spans = walked.grain.spans
                    # THE STEP BACK (plan P4-D417, repair round 1): from the
                    # rung the walk reached up to the top, the first rung whose
                    # description publishes no count one to ten people hold.
                    place = len(spans) if walked.grain.rung != grains.HELD else 0
                    while place > 0 and pooled is None and not walked.unread_thin:
                        place = place - 1
                        if walked.thin[spans[place][0]]:
                            continue
                        coarse = _cells_at(cells, walked, spans[place], ruled)
                        if coarse is None:
                            continue
                        candidate = _with_offset_rule(
                            described_from(coarse, None, False, walked.grain.reading),
                            _kept_rule(coarse, walked.grain.reading, ruled, frozenset(described.absent_spellings)),
                        )
                        if (
                            candidate.role in _GRAIN_ROLES
                            and _reads_its_member(candidate, walked.grain.reading)
                        ) and not _counted_in_subjects(
                            candidate,
                            coarse,
                            walking,
                            settings.small_cell_floor,
                            walking_enough,
                            cell_reading,
                            rows_hold=in_rows,
                        ):
                            pooled = taxonomy.with_time_grain(
                                candidate,
                                grains.record(
                                    dataclasses.replace(
                                        walked.grain,
                                        rung=spans[place][0],
                                        spans=spans[: place + 1],
                                    )
                                ),
                                by_rows,
                            )
                            chosen = spans[place]
                        coarse = None
                    if (
                        pooled is None
                        or chosen is None
                        or not _offset_rule_of(pooled)
                        or _rule_admitted_at(_offset_rule_of(pooled), chosen)
                    ):
                        break
            # A LEVEL FEW PEOPLE HOLD NO LONGER COSTS THE WHOLE COLUMN (lane
            # PL, plan P4-D453; the orchestrator's LANE CZ-D RULINGS 1 (1)).
            # In a label reading it is pooled as a held-back level, whatever
            # its rows, and the other levels keep their spelling and share:
            # once the column's own question is answered `code` or `no`, or,
            # with no question offering `identifier` open on the table, where
            # the column is plainly a list of codes. Anything else a shape
            # cannot tell from an identifier stays held, and its Safe Harbor
            # question is put. A column with no level to keep stays held.
            in_levels: "taxonomy.ColumnProfile | None" = None
            # ...A FEW WHOLE NUMBERS READ AS A COUNT MAY BE CODES: its shape
            # cannot tell, so it is read as codes only once its Safe Harbor
            # question is answered `no` (a measurement stays lane PS3's).
            # ...NOT A COLUMN ANSWERED OR DECLARED A MEASUREMENT: a
            # measurement's own reading is lane PS3's.
            whole_codes = (
                described.role == taxonomy.ROLE_COUNT
                and name not in declared_measurements
                and taxonomy.few_whole_numbers(
                    cells,
                    frozenset(described.absent_spellings),
                    taxonomy.LEVELS_READ_AS_CODES_AT_MOST,
                )
            )
            if (
                pooled is None
                and held_by_people
                and time_reading is None
                and not declined
                and not by_rows
                and (described.role in _LEVELS_POOLED_ROLES or whole_codes)
            ):
                levels_read = (
                    described_from(cells, None, False, None, "", None, True)
                    if whole_codes
                    else described
                )
                kept_labels = _levels_many_people_hold(
                    levels_read,
                    cells,
                    counting,
                    counting_enough,
                    settings.small_cell_floor,
                )
                own_answer = name in declared_codes or name in no_safe_harbor
                plainly = not whole_codes and taxonomy.levels_read_as_codes(
                    name,
                    list(kept_labels),
                    _levels_counted(levels_read),
                    _levels_written(levels_read),
                )
                if kept_labels and (
                    own_answer or (plainly and rare_values_released)
                ):
                    in_levels = _described_with_pool(
                        described_from(
                            cells, None, False, None, "", kept_labels, whole_codes
                        ),
                        cells,
                        counting,
                        counting_enough,
                        settings,
                        cell_reading,
                        name in declared_commas,
                        # ...after the person's `no`, its stand-ins kept off
                        # every value the pool holds back (plan P4-D477).
                        name in no_safe_harbor,
                    )
                elif (
                    kept_labels
                    and not plainly
                    and five_figures is not None
                    and harbor_reasons is not None
                    # ...its own reason before the persons' names' (plan
                    # P4-D478), which the people count makes no wider: the
                    # column keeps the bytes it had.
                    and (
                        name not in five_figures
                        or (name in harbor_reasons and harbor_reasons[name] in taxonomy.PERSONS_NAMES_HOLDS)
                    )
                ):
                    if name not in five_figures:
                        five_figures += [name]
                    harbor_reasons[name] = taxonomy.HELD_LEVELS_OF_FEW_PEOPLE
            if pooled is not None:
                described = pooled
            elif in_levels is not None:
                described = in_levels
                if levels_pooled is not None:
                    levels_pooled += [name]
            else:
                described_identifiers += [name]
                held_in_people += [name]
                cells = _held_from(cells, cells_before_ends, ends_here, forced_top)
                fresh = described_from(cells, None, True)
                if counting:
                    fresh = _layouts_in_subjects(
                        fresh,
                        cells,
                        counting,
                        counting_enough,
                        settings.small_cell_floor,
                    )
                real_census = _census_of(fresh)
                if declined:
                    # Named on the screen and in the questions file as a
                    # declaration that did not reach, not as a count in people.
                    described = taxonomy.as_counted_dates_held(fresh)
                else:
                    described = taxonomy.as_held_in_people(fresh, by_rows)
                    if held_dates is not None:
                        described = taxonomy.with_held_dates(
                            described, grains.record(held_dates)
                        )
                    # ...named apart where the rows held it (plan P4-D433),
                    # so the screen never says the table has several rows a
                    # person when it has one.
                    if by_rows:
                        if counted_in_rows is not None:
                            counted_in_rows += [name]
                    elif counted_in_subjects is not None:
                        counted_in_subjects += [name]
        if (
            not declarations_are_reconstructed
            and name in forced_identifiers
            and name not in withheld_names
            and name not in held_in_people
        ):
            # RULE A1 ON A DECLARED, PREFIXED RECORD NUMBER (lane CODES-3,
            # plan P4-D428): its layout pool counted in its commonest
            # layout. The validator reads the published prefix and absorbs
            # the measured file's pool alike (`validation._identifier_checks`).
            described = taxonomy.with_layout_pool_absorbed(
                described, cells, settings.small_cell_floor
            )
        if (
            name in subject_names
            and name not in withheld_names
            and name not in held_in_people
        ):
            # The person column's census of rows a person, counted in
            # people (Codex's review of lane HX2, items 1 and 6). A
            # candidate whose question is open, or a subject the count
            # held, keeps the census its printed counts imply, which
            # `as_unanswered_identity` gave it (lane HX's, P4-D401).
            described = taxonomy.with_census_in_people(
                described,
                settings.small_cell_floor,
                # Read only where a group of fewer people is to be pooled.
                _census_parts(described, cells)
                if _a_small_group(real_census, settings.small_cell_floor)
                else None,
            )
        # RULE A2'S CENSUS UNDER RULE U (lane CODES-1, plan P4-D439; the
        # stand-ins page, ZS.1 (c)): none while any question offering
        # `identifier` is open on the table -- until it is answered nobody
        # knows who the rows are about -- and beside a subject column each
        # listed character counted in people too.
        if "shape_form_places" in described.details:
            if withheld_names:
                described = taxonomy.without_places(described)
            elif counting:
                described = _places_in_subjects(
                    described, cells, counting, counting_enough,
                    settings.small_cell_floor,
                )
        # WHAT NO REAL CELL HOLDS, read last, off the census as published
        # (lane ID-ROOM, plan P4-D432): beside each named layout of a
        # record number, places no real cell of it holds, and the spill no
        # real cell wears, so no twin cell is spelled as a real one.
        described = taxonomy.with_layout_exclusions(
            described, cells, settings.small_cell_floor
        )
        # ...A HELD COLUMN OF COUNTS WITH NO GRAIN (lane ID-ROOM3, plan
        # P4-D488; the orchestrator's ruling D3): declared as counted dates
        # of a member the G1 floor writes, it takes that member's counted
        # grain record, its twin written in the room by the one writer of
        # counted dates; held by a question about dates, its counts longer
        # than any ZIP code, it publishes the room its counts would take and
        # its walk keeps only values off every real day.
        described = _held_counts_read(
            described, cells, settings, name,
            name in counts_held_for_dates
            or (five_figures is not None and name in five_figures)
            or (
                harbor_reasons is not None
                and name in harbor_reasons
                and harbor_reasons[name] in DATES_HOLD_REASONS
            ),
            name in declared_codes,
        )
        # ...AND THE YEARS ITS MADE-UP DATES TAKE, read off the same cells
        # (lane ID-ROOM2, plan P4-D457): no twin date of a column of dates
        # held as record numbers is a real date of it, exact or merged.
        described = taxonomy.with_made_up_years(described, cells)
        # ...and the walk's own name lets go of the column it described,
        # so no column of one group outlives it while the next is read.
        cells = []
        # A column held as a record number from its top-coded cells says so
        # too (plan P4-D427): its twin and the validator read it so.
        if top_coded_here:
            described = taxonomy.with_top_code(
                described, mark_here, top_pool_floor, top_pool_people,
                words_recorded, top_banded,
            )
        if year_here:
            described = taxonomy.with_year_top_code(described, year_here)
        # THE NAMES OF RARE LEVELS (lane CODES-2, plan P4-D471): a label
        # column whose `no` would name its held-back levels, not answered
        # `no`, is named for the command to put its Safe Harbor question to
        # (never a held column: its question is HX's); one that names them,
        # for rule U (c).
        if (
            rare_named is not None
            and described.held_back_nameable
            and name not in no_safe_harbor
            and name not in withheld_names
            and name not in described_identifiers
        ):
            rare_named += [name]
        if names_published is not None and _names_its_pool(described.details):
            names_published += [name]
        # ...AND A COLUMN OF NUMBERS TOO LARGE OR TOO SMALL TO HOLD WHOSE
        # MADE-UP SPELLINGS WOULD BE REAL VALUES (lane ID-ROOM4, plan
        # P4-D489; the orchestrator's LANE ID-ROOM4 RULINGS 5 (2)) keeps its
        # block, and its evidence tells the writer to spell each of its cells
        # one letter or figure wider than its longest value (method G10.5
        # step 8), whatever the answer.
        if (
            name in spelled_held
            and name not in withheld_names
            and described.role == taxonomy.ROLE_UNREPRESENTABLE
        ):
            described = dataclasses.replace(
                described,
                detection_evidence=taxonomy.note(
                    taxonomy.EVIDENCE_MADE_UP_SPELLED_REAL
                ),
            )
        columns += [_column_block(described)]
        absent_spellings += [described.absent_spellings]
        for note in described.publication_notes:
            notes += [{"column": name, "note": note}]
    # VALUES TYPED BY A KEY (lane KV, plan P4-D487), once every column is
    # described: the command's rule (``keyed_kept`` given, the columns
    # answered `keep` to the keyed question; None reads no pair, so the
    # library describes every table as before, byte for byte), and the
    # validator's (``keyed_described``, the pairs the description it checks
    # published). A table of delimited text only: a workbook's long table is
    # described as before (a stated limit of P4-D487, owner lane KV-b).
    if (keyed_kept is not None or keyed_described is not None) and table.sheet is None:
        typed = _values_typed_by_key(
            table,
            settings,
            columns,
            absent_spellings,
            notes,
            subject_names,
            subject_cells,
            held_in_people,
            described_identifiers,
            withheld_names,
            [] if keyed_kept is None else keyed_kept,
            keyed_found,
            # ...the columns answered `yes` to a question carrying the keyed
            # clause: the command passes its Safe Harbor `yes` and its `yes`
            # about values that read as dates (ANY YES HOLDS, `_KeyedAsked`).
            [] if keyed_yes is None else keyed_yes,
            [] if keyed_open is None else keyed_open,
            no_safe_harbor,
            no_dates,
            declared_codes,
            declared_measurements,
            declared_commas,
            identities_kept,
            rare_values_released,
            harbor_year,
            rare_named,
            names_published,
            keyed_described,
            names_checked_only,
            keyed_named,
            levels_pooled,
            dated_held,
            # ...the columns whose made-up spellings would be real values
            # (batch 4t's fix round, item 1).
            tuple(spelled_held),
            # ...the columns the command puts the Safe Harbor question
            # (`five_figures`, `ages_held`) or the question about values that
            # read as dates (`dated_values`); None on the library's path.
            None if five_figures is None else (
                frozenset(five_figures)
                | frozenset([] if ages_held is None else ages_held)
                | frozenset([] if dated_values is None else dated_values)
            ),
            # ...and each key block's own question's answer, and the blocks
            # that question is put to (lane IN-4c, plan P4-D514).
            answered_blocks=keyed_answered,
            blocks_asked=keyed_asked,
        )
        # ...each value column so described recorded as held exactly where
        # its own block is (S8d, A1): its old block's hold goes with it.
        for value, role in typed:
            if role == taxonomy.ROLE_IDENTIFIER:
                if value not in described_identifiers:
                    described_identifiers += [value]
                continue
            held_in_people = [one for one in held_in_people if one != value]
            described_identifiers = [one for one in described_identifiers if one != value]
            withheld_names = [one for one in withheld_names if one != value]
    # ...THE PAIRS, ONCE EVERY COLUMN IS READ: a column of a pair is named
    # for the command to hold whole, as a city column is, and put the Safe
    # Harbor question alone; `no` describes it as before.
    if coordinates_open and five_figures is not None and harbor_reasons is not None:
        for name in taxonomy.coordinates_held(coordinate_readings):
            if name in coordinates_open and name not in five_figures:
                five_figures += [name]
                harbor_reasons[name] = taxonomy.HELD_COORDINATES
    document: dict[str, object] = {
        "profile_version": PROFILE_VERSION,
        "created_with": _version(),
        "settings": _settings_block(
            # ...and a column held whole meanwhile, whose question is open
            # or answered `yes`, is recorded as held too (plan P4-D434: ZIP
            # codes answered as counted dates are held as record numbers,
            # and the contract reads a column one way only, S8d).
            _without_held(
                settings,
                held_in_people
                + [one for one in withheld_names if one not in held_in_people],
            ),
            described_identifiers,
            [one for one in declared_codes if one not in held_in_people],
            [one for one in declared_measurements if one not in held_in_people],
            [one for one in declared_commas if one not in held_in_people],
        
            forced_metadata_rows,
            forced_delimiter,
        ),
        # How the table was read. It belongs in the profile because the
        # twin has to be written in a form the same tools can open, and
        # it is fixed by the input bytes, so it does not make two runs
        # over the same file differ.
        "source": {
            "encoding": table.encoding,
            "used_fallback_encoding": table.used_fallback_encoding,
            # Where the column names came from: the file's own first row,
            # or names synthtwin generated because the reader could not
            # tell and the user said the first row was data. A consumer
            # must be able to tell those apart.
            "header_source": table.header_source,
            # Whether that first row was READ as names because the file
            # showed it was, or merely ASSUMED to be names because nothing
            # in the file said otherwise. The two are not the same claim,
            # and a consumer of this profile -- including Phase 2 -- must
            # not have to guess which one it is holding. When this is
            # true, the names may in fact be somebody's first record, and
            # `--first-row data` re-reads the file that way.
            "header_by_convention": table.header_by_convention,
            # The verdict in words, so a person reading the profile sees
            # the same sentence the summary gave them.
            "header_evidence": table.header_evidence,
            # How the table's file is written -- its delimiter, quoting,
            # line endings and the lines that are not records -- so the
            # twin is written the same way (plan P4-D86).
            "dialect": dialect.document_of(
                _published_form(
                    table, columns, described_identifiers,
                )
            ),
            # What the table's file said about itself as a WORKBOOK, or
            # nothing where it was delimited text (plan P4-D77). Every
            # count is held to the smallest group, and the facts the
            # disclosure rule names -- the sheet's own name, a column
            # width, a comment, a hidden row, a hyperlink's target, the
            # document's author -- are not in it at all.
            "workbook": _published_workbook(
                table, settings.small_cell_floor, columns, absent_spellings
            ),
        },
        "n_rows": table.n_rows,
        "n_columns": len(table.column_names),
        "columns": columns,
        "publication_notes": notes,
        # What this profile says about how the columns move TOGETHER:
        # nothing, in eight named places, so that a consumer reads a
        # stated "not carried" rather than guessing from a block that is
        # not there (plan P2-D5). RELATIONSHIP_SLOTS above says why the
        # shape is reserved now and what filling one would cost.
        "relationships": _relationships_block(),
    }
    # A FILE FROM ANOTHER SYSTEM (lane FORMATS): its native block, held to
    # the rules `_published_native` states, under a key of its own that a
    # description of a CSV file or a workbook never carries.
    if table.native is not None:
        held_back = (
            list(described_identifiers) + list(held_in_people) + list(withheld_names)
            + (list(five_figures) if five_figures is not None else [])
        )
        native_block = _published_native(table, columns, settings.small_cell_floor, held_back)
        source_block = document["source"]
        if native_block is not None and isinstance(source_block, dict):
            source_block["native"] = native_block
    # THE LAST THING THAT HAPPENS, and it happens to the FINISHED
    # document (plan P2-D2). The notes were lifted out of the column
    # blocks a few lines above, so a check made anywhere earlier would
    # not have seen them; this one walks everything that is about to be
    # serialized and stops the run rather than write a description
    # carrying anything the rules do not authorize.
    check_publication(document)
    return document


# -- the profile command's walks, a group of columns at a time ---------
#
# A TABLE READ IN GROUPS HOLDS ONE GROUP (lane SR, plan P4-D400), so every
# step of `synthtwin profile` that reads the table's cells after the
# description -- the population census and the questions -- walks it a
# group at a time: each step is asked of the group's columns beside the
# description's blocks for those columns alone, and its answers, made
# column by column, are put together in column order. A table read whole
# is asked exactly as before.


def _parts_of(
    table: Table, document: "dict[str, object]"
) -> "typing.Iterator[tuple[int, dict[str, object], list[list[str]]]]":
    """Each walk of a table read in groups (`reading.column_walks`): its first column, the description cut to its blocks, and its columns."""
    blocks = document["columns"]
    for start, end in reading.column_walks(table):
        part: "dict[str, object]" = {}
        for key in document:
            part[key] = document[key]
        if isinstance(blocks, list):
            part["columns"] = blocks[start:end]
        reading.hold_columns(table, tuple(range(start, end)))
        cells = [reading.column_values(table, place) for place in range(start, end)]
        yield start, part, cells
        # Let go before the next group is read.
        cells = []


@dataclasses.dataclass
class _GroupAsked:
    """What one group of a table read in groups answers `questions_of` or `dated_questions_of`, put together in column order.

    The questions kept, the codes question's walk moved to the table's
    places (None where the codes are given), Q6 (None where it is not
    asked), the day-or-month columns, the person questions, the record
    number lists' questions (plan P4-D424) and the checklist;
    `dated_questions_of` fills the three date fields alone.
    """

    kept: "list[asking.Question]"
    moved: "asking.DateCodesPending | None"
    dated: "asking.DateColumnsSeen | None"
    months: "list[asking.DayOrMonth]"
    person: "list[asking.Question]"
    lists: "list[asking.Question]"
    listed: "list[asking.Question]"
    # -- UN-1a (P4-D438): question Q-UNIT, after the lists' questions.
    units: "list[asking.Question]" = dataclasses.field(default_factory=list)


def _person_places(
    document: "dict[str, object]", settings: taxonomy.Settings, width: int
) -> "tuple[int, ...]":
    """The places of the description's blocks that name a person column (`settings.person_columns`), in the table's order (plan P4-D489).

    The columns `asking._people_of` reads of a table read whole, so that a
    table read in groups reads the same people (`_by_groups`). Raises
    nothing.
    """
    blocks = document["columns"]
    if not settings.person_columns or not isinstance(blocks, list):
        return ()
    return tuple(
        place
        for place in range(min(len(blocks), width))
        if isinstance(blocks[place], dict) and f"{blocks[place]['name']}" in settings.person_columns
    )


def _part_of(document: "dict[str, object]", start: int, end: int) -> "dict[str, object]":
    """The description cut to the blocks of columns ``start`` to ``end``, every other key as it stands."""
    blocks = document["columns"]
    part: "dict[str, object]" = {}
    for key in document:
        part[key] = document[key]
    if isinstance(blocks, list):
        part["columns"] = blocks[start:end]
    return part


@dataclasses.dataclass(frozen=True)
class _GroupStep:
    """What every group of a table read in groups is asked under, by `questions_of` (``dates_only`` False) or `dated_questions_of`.

    Named fields, not a function handed over: the offline audit reads
    every call by its written-out name (`_group_asked`).
    """

    dates_only: bool
    settings: taxonomy.Settings
    already: "list[str]"
    decimal_commas: "tuple[str, ...]"
    stored_as: "tuple[str, ...]"
    codes_seen: "asking.DateCodesSeen | None"
    dates_already: "list[str] | None"
    dates_seen: asking.DateColumnsSeen
    month: bool
    with_dates: bool


def _group_asked(
    step: _GroupStep,
    start: int,
    part: "dict[str, object]",
    cells: "list[list[str]]",
    describes: bool,
    people: "list[tuple[str, list[str]]] | None" = None,
) -> "_GroupAsked | None":
    """One group's answer to ``step``, or None where ``describes`` is False and a column of it would be described.

    ``people`` is the whole table's person columns read as people
    (`asking.people_of`), for `questions_of`'s steps (lane ID-ROOM4, plan
    P4-D489).
    """
    if step.dates_only:
        return _dated_group(step, start, part, cells, describes)
    return _questions_group(step, start, part, cells, describes, people)


def _questions_group(
    step: _GroupStep,
    start: int,
    part: "dict[str, object]",
    cells: "list[list[str]]",
    describes: bool,
    people: "list[tuple[str, list[str]]] | None" = None,
) -> "_GroupAsked | None":
    """`questions_of`'s steps asked of one group, in its order: the questions, the codes walk, Q6, day or month, the person questions, the checklist."""
    group_storage = step.stored_as[start : start + len(cells)]
    found, split = asking.questions_and_splits_for(
        part, cells, step.settings, step.already, step.decimal_commas, people
    )
    moved: "asking.DateCodesPending | None" = None
    if step.codes_seen is None:
        walked = asking.date_codes_pending_in_a_walk(
            part, cells, step.settings, step.already, split, step.decimal_commas,
            group_storage, describes,
        )
        if walked is None:
            return None
        moved = _moved_by(walked, start)
        group_codes = asking.date_codes_found(walked, {}, step.settings)
    else:
        group_codes = step.codes_seen
    coded_about = list(group_codes.questions)
    coded_or_answered = coded_about + list(group_codes.answered)
    kept = asking.without_columns_of(found, coded_or_answered)
    group_dates = step.dates_seen
    dated: "asking.DateColumnsSeen | None" = None
    if step.dates_already is not None:
        dated = asking.date_columns_seen_in_a_walk(
            part, cells, step.settings, step.dates_already, split, step.decimal_commas,
            group_storage, describes,
        )
        if dated is None:
            return None
        group_dates = dated
    months: "list[asking.DayOrMonth]" = []
    if step.month:
        months = list(
            asking.day_or_month_columns(
                part, cells, step.settings, split,
                also=group_codes.day_or_month + group_dates.day_or_month,
            )
        )
    person = asking.person_questions(
        part, cells, step.settings, step.already, kept + coded_or_answered, split
    )
    # ...after which the whole table's lists are asked, as in
    # `questions_of` (plan P4-D424): kept apart so the file's order is
    # the same. The lists' question reads the blocks' roles and the
    # cells, and describes no column.
    lists = asking.listed_record_number_questions(
        part, cells, step.settings, step.already, kept + coded_or_answered + person,
        split, step.decimal_commas,
    )
    # ...and question Q-UNIT (plan P4-D438), one question a column: a
    # column another question reaches has that question offer its answers.
    units, reached = asking.unit_questions(
        part, cells, step.settings, step.already,
        kept + coded_or_answered + person + lists, split, step.decimal_commas,
    )
    # ...and question Q-COMMA and its mirror (plan P4-D443), to a column no
    # question above reaches.
    units = units + asking.comma_questions(
        part, cells, step.settings, step.already,
        kept + coded_or_answered + person + lists + units, split,
        step.decimal_commas,
    )
    floor = step.settings.small_cell_floor
    kept = asking.with_unit_answers(kept, reached, floor)
    person = asking.with_unit_answers(person, reached, floor)
    lists = asking.with_unit_answers(lists, reached, floor)
    dated_about = list(group_dates.questions) if step.with_dates else []
    checked = asking.checklist_for(
        part, cells, step.settings, step.already,
        kept + person + lists + units + dated_about + coded_about,
        group_codes.answered,
    )
    return _GroupAsked(kept, moved, dated, months, person, lists, checked, units)


def _dated_group(
    step: _GroupStep, start: int, part: "dict[str, object]", cells: "list[list[str]]", describes: bool
) -> "_GroupAsked | None":
    """`dated_questions_of`'s steps asked of one group: the codes walk where the codes are not given, Q6 and day or month."""
    group_storage = step.stored_as[start : start + len(cells)]
    split_cells: "dict[int, list[str]]" = {}
    split_present: "dict[int, list[str]]" = {}
    for place in range(len(cells)):
        split_cells[place] = cells[place]
        split_present[place] = taxonomy.split_missing(cells[place], step.settings)[0]
    group_split = asking.SplitColumns(step.settings, split_cells, split_present)
    group_codes = step.codes_seen
    moved: "asking.DateCodesPending | None" = None
    if step.codes_seen is None:
        walked = asking.date_codes_pending_in_a_walk(
            part, cells, step.settings, step.already, group_split,
            step.decimal_commas, group_storage, describes,
        )
        if walked is None:
            return None
        moved = _moved_by(walked, start)
        group_codes = asking.date_codes_found(walked, {}, step.settings)
    group_dates = asking.date_columns_seen_in_a_walk(
        part, cells, step.settings,
        step.dates_already if step.dates_already is not None else [],
        group_split, step.decimal_commas, group_storage, describes,
    )
    if group_dates is None:
        return None
    months: "list[asking.DayOrMonth]" = []
    if step.month and group_codes is not None:
        months = list(
            asking.day_or_month_columns(
                part, cells, step.settings, group_split,
                also=group_codes.day_or_month + group_dates.day_or_month,
            )
        )
    return _GroupAsked([], moved, group_dates, months, [], [], [])


def _by_groups(
    table: Table,
    document: "dict[str, object]",
    step: _GroupStep,
) -> "list[_GroupAsked]":
    """``step`` asked of each group of a table read in groups, in column order, every column described beside its own group alone.

    A COLUMN DESCRIBED IS DESCRIBED BESIDE ITS GROUP, NEVER BESIDE A WALK
    (lane H3's second repair, plan P4-D423; the orchestrator's H3
    addendum 2 of 2026-10-23). A walk (`reading.column_walks`) holds up
    to `reading.WALK_BYTES` of cells, three times `reading.GROUP_BYTES`,
    for steps that describe nothing; the date questions describe a
    candidate column under its declaration (`taxonomy.role_read`), and
    on the mixed table with a declared person column Q6 described nine
    columns of dates and stamps beside their walks, the command's peak
    at 20,000 rows (14.2 MB traced against the description's 12.3), and
    the 2,000,000-row person leg stopped at 2,400 MB. So each group of a
    walk is asked with ``describes`` False, of the walk's cells held
    once, and a group whose answer is None -- a column of it would be
    described -- is asked again with ``describes`` True, the walk's
    other columns let go and its own alone held
    (`reading.hold_columns_alone`): the first such group of a walk as the
    walk read it, each further one read again, one more reading of the
    file. A walk of one group is asked so at once. Each step's answer is
    made column by column, so a group's answer is the same asked within
    its walk or alone.

    THE PEOPLE ARE READ ACROSS THE GROUPS (Codex's review of lane
    ID-ROOM4, item 2; the orchestrator's LANE ID-ROOM4 RULINGS 6 (2)):
    lane HX5's rule counted in people reads each key beside the person
    columns, and a group holding the key without them read it in rows
    (19,990 real keys written where the table read whole held the
    column). So `questions_of`'s steps read the person columns
    (`settings.person_columns`) with the FIRST walk, in that walk's one
    reading of the file, as the people they name (`asking.people_of`),
    and every group is asked beside them: one key a row a person column
    held from the first walk to the last, its cells let go once read.
    """
    groups = reading.column_groups(table)
    answers: "list[_GroupAsked | None]" = []
    people: "list[tuple[str, list[str]]] | None" = None
    persons = (
        ()
        if step.dates_only
        else _person_places(document, step.settings, len(table.column_names))
    )
    for walk_start, walk_end in reading.column_walks(table):
        walk = tuple(range(walk_start, walk_end))
        if people is None and persons:
            reading.hold_columns(
                table, walk + tuple(place for place in persons if place not in walk)
            )
            people = asking.people_of(
                [
                    (f"{table.column_names[place]}", reading.column_values(table, place))
                    for place in persons
                ],
                step.settings,
            )
        else:
            reading.hold_columns(table, walk)
        inside = [one for one in groups if walk_start <= one[0] < walk_end]
        later: "list[tuple[int, int, int]]" = []
        for start, end in inside:
            cells = [reading.column_values(table, place) for place in range(start, end)]
            answer = _group_asked(
                step, start, _part_of(document, start, end), cells, len(inside) == 1, people
            )
            cells = []
            if answer is None:
                later += [(len(answers), start, end)]
            answers += [answer]
        # The walk's other columns let go, each such group alone: the
        # first kept as the walk read it, the others read again.
        for index, start, end in later:
            reading.hold_columns_alone(table, tuple(range(start, end)))
            cells = [reading.column_values(table, place) for place in range(start, end)]
            answers[index] = _group_asked(
                step, start, _part_of(document, start, end), cells, True, people
            )
            cells = []
    answered: "list[_GroupAsked]" = []
    for answer in answers:
        if answer is None:
            raise ValueError("synthtwin internal check: a group asked alone refused to describe")
        answered += [answer]
    return answered


def population_census_of(
    table: Table,
    settings: taxonomy.Settings,
    declared: "list[str]",
    codes: "list[str]",
    measurements: "list[str]",
    decimal_commas: "list[str]",
    stored_as: "tuple[str, ...]",
) -> "tuple[tuple[str, ...], int, tuple[taxonomy.HeldReading, ...]]":
    """`taxonomy.population_census` of this table: the person columns, how many people, and the readings kept.

    `population_and_rows_census_of`'s answer less the rows that hold a
    value, which that function says how it works out.
    """
    people, counted, _merged, _rows, readings = population_and_rows_census_of(
        table, settings, declared, codes, measurements, decimal_commas,
        stored_as,
    )
    return people, counted, readings


def population_and_rows_census_of(
    table: Table,
    settings: taxonomy.Settings,
    declared: "list[str]",
    codes: "list[str]",
    measurements: "list[str]",
    decimal_commas: "list[str]",
    stored_as: "tuple[str, ...]",
    join: "list[str] | None" = None,
) -> "tuple[tuple[str, ...], int, int, int, tuple[taxonomy.HeldReading, ...]]":
    """`taxonomy.population_and_rows_census` of this table (plan P4-D425).

    The person columns, how many people, how many people with each
    person's spellings merged (`parsing.subject_key`: the count the
    command's table floor asks), how many rows hold a value (the floor
    asks it too), and the readings kept.

    THE COLUMNS THE PEOPLE ARE COUNTED BY ARE ``join`` WHERE GIVEN, and the
    declarations that read every cell are ``declared`` all the same (lane
    EZ-a's second repair; Codex's item 4 of that lane): choosing the column
    said to name the person never changes how another declared identifier's
    cells are read. Measured before this at 20,000 rows: a declared
    identifier of repeated date strings closing on `1900-01-01` was read as
    a column of dates once it was left out of the declarations, its last
    1,000 cells as no value, and a table of 20,000 rows was refused as
    19,000. ``join`` None counts by every declared identifier, as before.

    A table read whole is handed over whole. A table read in groups
    (lane SR, plan P4-D400) is counted ONE COLUMN AT A TIME, every
    column asked of `reading.column_values` and let go before the next
    (Codex's review of lane SR, item 2: every declared identifier was
    held at once, about 3 GB for fifty of them at a million rows): the
    rows holding a value worked out a column at a time, in column order,
    until every row holds one (`taxonomy.rows_holding_a_value_in`); then
    each declared column, in `taxonomy.repeating_identifiers`' order,
    read ONCE to ask whether it repeats and, where it does, to join the
    rows it names (`taxonomy.people_joined_if_repeating`; the tripwire
    skeptic of lane SR, item 1). Its answers are the census's; it keeps
    no reading, which the description reads again.
    """
    declarations = taxonomy.Declarations(
        identifiers=tuple(declared),
        codes=tuple(codes),
        measurements=tuple(measurements),
        decimal_commas=tuple(decimal_commas),
    )
    counted_by = list(join) if join is not None else list(declared)
    if table.source is None:
        return taxonomy.population_and_rows_census(
            table.column_names, table.columns, counted_by, settings,
            declarations, stored_as,
        )
    names = table.column_names
    holding = _rows_holding_a_value(table, settings, declarations, stored_as)
    people: "list[str]" = []
    joined: "taxonomy.PeopleJoined | None" = None
    for name in sorted(counted_by):
        if people and people[len(people) - 1] == name:
            continue
        place = _first_place_named(names, name)
        if place < 0:
            continue
        repeats, joined = taxonomy.people_joined_if_repeating(
            joined,
            table.n_rows,
            reading.column_values(table, place),
            name,
            settings,
            declarations,
            stored_as[place] if place < len(stored_as) else "",
        )
        if repeats:
            people += [name]
    counted = 0
    for row in range(table.n_rows):
        if holding[row]:
            counted = counted + 1
    if joined is None:
        return (), counted, counted, counted, ()
    return (
        tuple(people),
        taxonomy.people_counted(joined, holding),
        taxonomy.people_counted_merged(joined, holding),
        counted,
        (),
    )


def _first_place_named(names: "list[str]", name: str) -> int:
    """The place of the first column called ``name``, as `taxonomy`'s census finds it, or -1."""
    for place in range(len(names)):
        if names[place] == name:
            return place
    return -1


def _rows_holding_a_value(
    table: Table,
    settings: taxonomy.Settings,
    declarations: taxonomy.Declarations,
    stored_as: "tuple[str, ...]",
) -> "list[bool]":
    """Which rows hold a value, worked out a column at a time in column order until every row holds one (`taxonomy.rows_holding_a_value_in`)."""
    names = table.column_names
    holding: "list[bool]" = [False for _row in range(table.n_rows)]
    outstanding = table.n_rows
    for start, end in reading.column_groups(table):
        for place in range(start, end):
            if not outstanding:
                break
            outstanding = taxonomy.rows_holding_a_value_in(
                reading.column_values(table, place),
                names[place],
                holding,
                outstanding,
                settings,
                declarations,
                stored_as[place] if place < len(stored_as) else "",
            )
    return holding


def people_of_each_key(
    table: Table,
    settings: taxonomy.Settings,
    declared: "list[str]",
    keys: "list[str]",
    codes: "list[str]",
    measurements: "list[str]",
    decimal_commas: "list[str]",
    stored_as: "tuple[str, ...]",
) -> "tuple[int, ...]":
    """For each of ``keys``, in order, the people counted by that key ALONE with each person's spellings merged; 0 where it does not repeat.

    Lane EZ-a's second repair (the orchestrator's LANE EZ RULINGS 7, Codex's
    item 6, and 8 (2) (d) and (e)): whether a repeating record-number column
    could name the patients, asked of each key at once. ONE WALK for the
    rows that hold a value, then each key's column read ONCE
    (`taxonomy.people_joined_if_repeating`): k keys cost one walk and k
    readings, where a census of each key alone cost k walks over every
    column the walk reads -- k (k + 1) readings measured on a table whose
    keys hold values in its first rows alone. Every cell is read under
    every declaration in force (``declared``, ``codes``, ``measurements``,
    ``decimal_commas``), as the census reads it. The count is the one the
    table floor asks of a person column (`population_and_rows_census_of`'s
    third). Guarantees: a fixed function of the arguments. Raises what
    `reading.column_values` raises. Keeps no reading and publishes nothing.
    """
    declarations = taxonomy.Declarations(
        identifiers=tuple(declared),
        codes=tuple(codes),
        measurements=tuple(measurements),
        decimal_commas=tuple(decimal_commas),
    )
    holding = _rows_holding_a_value(table, settings, declarations, stored_as)
    names = table.column_names
    found: "list[int]" = []
    for name in keys:
        place = _first_place_named(names, name)
        if place < 0:
            found += [0]
            continue
        repeats, joined = taxonomy.people_joined_if_repeating(
            None,
            table.n_rows,
            reading.column_values(table, place),
            name,
            settings,
            declarations,
            stored_as[place] if place < len(stored_as) else "",
        )
        found += [taxonomy.people_counted_merged(joined, holding) if repeats and joined is not None else 0]
    return tuple(found)


@dataclasses.dataclass
class Asked:
    """What one walk of a table's questions works out (`questions_of`).

    ``asked`` are the questions asked of what each column holds -- less
    those the codes question answers in their place, then the person
    question's, then, where the walk was asked to, question Q6's --
    ``split`` the cells split for them where the table was read whole,
    ``codes_seen``, ``dates_seen`` and ``day_or_month`` the date
    questions' and ``listed`` the checklist.
    """

    asked: "list[asking.Question]"
    split: "asking.SplitColumns | None"
    codes_seen: asking.DateCodesSeen
    dates_seen: asking.DateColumnsSeen
    day_or_month: "tuple[asking.DayOrMonth, ...]"
    listed: "list[asking.Question]"


def commas_read(
    document: "dict[str, object]", declared: "tuple[str, ...]"
) -> "tuple[str, ...]":
    """The columns whose comma is read as the decimal point: ``declared``, then those the description adds.

    A description publishes in `forced_decimal_commas` every column it
    read with a decimal comma, inferred ones included (plan P4-D443), so
    each question reads a column as the description did. ``declared``
    first, in its own order. A fixed function of the two. Raises
    nothing. No I/O.
    """
    found = list(declared)
    block = document["settings"] if "settings" in document else None
    named = (
        block["forced_decimal_commas"]
        if isinstance(block, dict) and "forced_decimal_commas" in block
        else []
    )
    if isinstance(named, list):
        for name in named:
            if isinstance(name, str) and name not in found:
                found += [name]
    return tuple(found)


def questions_of(
    table: Table,
    document: "dict[str, object]",
    settings: taxonomy.Settings,
    already: "list[str]",
    decimal_commas: "tuple[str, ...]",
    stored_as: "tuple[str, ...]",
    codes_seen: "asking.DateCodesSeen | None",
    dates_already: "list[str] | None",
    dates_seen: asking.DateColumnsSeen,
    month: bool,
    day_or_month: "tuple[asking.DayOrMonth, ...]",
    with_dates: bool,
) -> Asked:
    """The questions `synthtwin profile` puts, worked out in one walk of the table.

    In this order, each over the description and the table's columns:
    `asking.questions_and_splits_for`; the codes question
    (`asking.date_codes_seen`) where ``codes_seen`` is None, otherwise
    ``codes_seen`` as it stands; the first questions less those the codes
    question answers (`asking.without_columns_of`); question Q6
    (`asking.date_columns_seen`) where ``dates_already`` is given,
    otherwise ``dates_seen``; the day-or-month question where ``month``
    says so, otherwise ``day_or_month``; the person question; the question
    put to a column of lists written as record numbers (plan P4-D424);
    Q6's questions where ``with_dates`` says so; and the checklist. A table
    read whole is asked exactly that way. A table read in groups (lane
    SR, plan P4-D400) is asked it ONE GROUP AT A TIME, every step of a
    group asked of the cells split once for that group, and each step's
    answers, made column by column, put together in column order: the
    codes question's count of the other columns, the one step that reads
    across columns, is made in a second walk where some column asks it.

    The columns whose comma is read as the decimal point are those
    ``decimal_commas`` names and those the description inferred
    (`commas_read`, plan P4-D443).
    """
    decimal_commas = commas_read(document, decimal_commas)
    if table.source is None:
        columns = table.columns
        asked, split = asking.questions_and_splits_for(
            document, columns, settings, already, decimal_commas
        )
        if codes_seen is None:
            codes_seen = asking.date_codes_seen(
                document, columns, settings, already, split,
                decimal_commas, stored_as,
            )
        coded_about = list(codes_seen.questions)
        coded_or_answered = coded_about + list(codes_seen.answered)
        asked = asking.without_columns_of(asked, coded_or_answered)
        if dates_already is not None:
            dates_seen = asking.date_columns_seen(
                document, columns, settings, dates_already, split,
                decimal_commas, stored_as,
            )
        if month:
            day_or_month = asking.day_or_month_columns(
                document, columns, settings, split,
                also=codes_seen.day_or_month + dates_seen.day_or_month,
            )
        asked = asked + asking.person_questions(
            document, columns, settings, already, asked + coded_or_answered,
            split,
        )
        # ...and a column of lists written as record numbers no question
        # above reached (plan P4-D424, lane HX4).
        asked = asked + asking.listed_record_number_questions(
            document, columns, settings, already, asked + coded_or_answered,
            split, decimal_commas,
        )
        # ...and question Q-UNIT (plan P4-D438), one question a column: a
        # column another question reaches has that question offer its
        # answers (`asking.with_unit_answers`).
        units, reached = asking.unit_questions(
            document, columns, settings, already, asked + coded_or_answered,
            split, decimal_commas,
        )
        # ...and question Q-COMMA and its mirror (plan P4-D443), to a
        # column no question above reaches.
        units = units + asking.comma_questions(
            document, columns, settings, already,
            asked + coded_or_answered + units, split, decimal_commas,
        )
        asked = (
            asking.with_unit_answers(asked, reached, settings.small_cell_floor)
            + units
        )
        if with_dates:
            # ...one question a column where Q6 takes lane HX5's place
            # (plan P4-D436).
            asked = asking.without_merged_questions(asked + list(dates_seen.questions))
        return Asked(
            asked, split, codes_seen, dates_seen, day_or_month,
            asking.checklist_for(
                document, columns, settings, already, asked + coded_about,
                codes_seen.answered,
            ),
        )
    # Each group's questions, every column described beside its own group
    # (`_by_groups`).
    step = _GroupStep(
        False, settings, already, decimal_commas, stored_as, codes_seen,
        dates_already, dates_seen, month, with_dates,
    )
    kept_all: "list[asking.Question]" = []
    person_all: "list[asking.Question]" = []
    listed_all: "list[asking.Question]" = []
    units_all: "list[asking.Question]" = []
    listed: "list[asking.Question]" = []
    walked_all: "list[asking.DateCodesPending]" = []
    dated_all: "list[asking.DateColumnsSeen]" = []
    found_months: "list[asking.DayOrMonth]" = []
    for group in _by_groups(table, document, step):
        kept_all += group.kept
        if group.moved is not None:
            walked_all += [group.moved]
        if group.dated is not None:
            dated_all += [group.dated]
        found_months += group.months
        person_all += group.person
        listed_all += group.lists
        units_all += group.units
        listed += group.listed
    if codes_seen is None:
        codes_seen = _codes_counted(table, document, settings, decimal_commas, walked_all)
    if dates_already is not None:
        dates_seen = _dates_joined(dated_all)
    if month:
        day_or_month = tuple(found_months)
    asked = kept_all + person_all + listed_all + units_all
    if with_dates:
        asked = asking.without_merged_questions(asked + list(dates_seen.questions))
    return Asked(asked, None, codes_seen, dates_seen, day_or_month, listed)


def dated_questions_of(
    table: Table,
    document: "dict[str, object]",
    settings: taxonomy.Settings,
    split: "asking.SplitColumns | None",
    codes_seen: "asking.DateCodesSeen | None",
    codes_already: "list[str]",
    dates_already: "list[str]",
    month: bool,
    decimal_commas: "tuple[str, ...]",
    stored_as: "tuple[str, ...]",
) -> "tuple[asking.DateCodesSeen, asking.DateColumnsSeen, tuple[asking.DayOrMonth, ...]]":
    """The date questions worked out after the interview, in one walk of the table.

    The codes question with ``codes_already`` where ``codes_seen`` is
    None, otherwise ``codes_seen`` as it stands; question Q6 with
    ``dates_already``; and, where ``month`` says so, the day-or-month
    question beside what both found -- as `questions_of` walks a
    table: a table read whole asked each in turn over ``split``, a table
    read in groups one group at a time, its cells split once a group.
    The columns whose comma is read as the decimal point include those
    the description inferred (`commas_read`, plan P4-D443).
    """
    decimal_commas = commas_read(document, decimal_commas)
    if table.source is None:
        columns = table.columns
        if codes_seen is None:
            codes_seen = asking.date_codes_seen(
                document, columns, settings, codes_already, split,
                decimal_commas, stored_as,
            )
        dates_seen = asking.date_columns_seen(
            document, columns, settings, dates_already, split,
            decimal_commas, stored_as,
        )
        day_or_month: "tuple[asking.DayOrMonth, ...]" = ()
        if month:
            day_or_month = asking.day_or_month_columns(
                document, columns, settings, split,
                also=codes_seen.day_or_month + dates_seen.day_or_month,
            )
        return codes_seen, dates_seen, day_or_month
    # Each group's codes walk (None where the codes are given), Q6 and
    # day-or-month answers, every column described beside its own group
    # (`_by_groups`).
    step = _GroupStep(
        True, settings, codes_already, decimal_commas, stored_as, codes_seen,
        dates_already, asking.DateColumnsSeen(), month, False,
    )
    walked_all: "list[asking.DateCodesPending]" = []
    dated_all: "list[asking.DateColumnsSeen]" = []
    found_months: "list[asking.DayOrMonth]" = []
    for group in _by_groups(table, document, step):
        if group.moved is not None:
            walked_all += [group.moved]
        if group.dated is not None:
            dated_all += [group.dated]
        found_months += group.months
    if codes_seen is None:
        codes_seen = _codes_counted(table, document, settings, decimal_commas, walked_all)
    return codes_seen, _dates_joined(dated_all), tuple(found_months)


def _moved_by(walked: asking.DateCodesPending, start: int) -> asking.DateCodesPending:
    """A group's `asking.DateCodesPending` with each column's place counted from the table's first column."""
    return asking.DateCodesPending(
        tuple(
            (name, role, place + start, codes)
            for name, role, place, codes in walked.pending
        ),
        walked.answered,
        walked.day_or_month,
        walked.century,
    )


def _dates_joined(parts: "list[asking.DateColumnsSeen]") -> asking.DateColumnsSeen:
    """Each group's `asking.DateColumnsSeen`, put together in column order."""
    questions: "list[asking.Question]" = []
    order: "list[asking.DayOrMonth]" = []
    centuries: "list[str]" = []
    for part in parts:
        questions += list(part.questions)
        order += list(part.day_or_month)
        centuries += list(part.century)
    return asking.DateColumnsSeen(tuple(questions), tuple(order), tuple(centuries))


def _codes_counted(
    table: Table,
    document: "dict[str, object]",
    settings: taxonomy.Settings,
    decimal_commas: "tuple[str, ...]",
    walked_all: "list[asking.DateCodesPending]",
) -> asking.DateCodesSeen:
    """`asking.date_codes_seen` from each group's walk: the other columns counted a group at a time, where any column asks."""
    pending: "list[tuple[str, str, int, asking.DateCodes]]" = []
    answered: "list[asking.Question]" = []
    order: "list[asking.DayOrMonth]" = []
    centuries: "list[str]" = []
    for walked in walked_all:
        pending += list(walked.pending)
        answered += list(walked.answered)
        order += list(walked.day_or_month)
        centuries += list(walked.century)
    elsewhere: "dict[int, tuple[asking.Elsewhere, ...]]" = {}
    if pending:
        for start, part, cells in _parts_of(table, document):
            counted = asking.codes_elsewhere(
                part,
                cells,
                [(place - start, codes) for _name, _role, place, codes in pending],
                settings,
                decimal_commas,
            )
            for place in sorted(counted):
                before = elsewhere[place + start] if place + start in elsewhere else ()
                elsewhere[place + start] = before + counted[place]
            cells = []
    return asking.date_codes_found(
        asking.DateCodesPending(
            tuple(pending), tuple(answered), tuple(order), tuple(centuries)
        ),
        elsewhere,
        settings,
    )


# ---------------------------------------------------------------------------
# COUNTED IN PEOPLE, NOT ROWS (plan P4-D406, lane HX2).
#
# THE FINDING. The floor -- every printed count nought or at least the
# smallest group size -- counts ROWS. On a table of several rows a
# person, a value one patient holds on fourteen rows passes it: measured
# on lane HX's head, a patient's name, street address or birth date, and
# a health plan or account number beside a declared person column, were
# published and copied into the twin (P4-D401, K-S3-64's stated shapes).
#
# THE RULE. Where the table has a SUBJECT column -- a person column a
# person declared or answered, or every candidate of the person question
# while it is open -- a value the description publishes for any other
# column is held to the floor in DIFFERENT SUBJECTS as well as in rows,
# under every subject column at once. A column that would publish a
# value one to ten subjects hold is described as a held record number,
# as lane HX describes a column whose identity question is open: no
# level, rung, percentile, mode, tail value or prefix, the census its
# counts imply, and made-up values in its layouts in the twin. Its
# printed counts are the whole column's, held by every subject of it.
# The real table still meets its own description, which a description
# with the withheld cells counted as blanks would not.
#
# WHICH VALUES. A column ATTACHED to a subject -- one value a person, as
# a name, a birth date or a plan number is (`_attached`) -- is a fact
# about the person, so every value of it is counted. Any other column's
# value is counted where the row floor's own reason for publishing it
# fails: at least `floor` rows hold it but fewer than `floor` subjects
# do. A measurement one patient holds on one row is judged as the floor
# judges it on a table of one row a person, which is the base product.
#
# WHICH SUBJECTS. A subject column that repeats and holds at least
# `floor` different values (`_reaches_the_floor`): one of fewer is under
# the population floor once declared, and counted in it no value could
# be published at all.
#
# SCALE. The count is a distinct count capped at the floor: at most
# `floor` subject identifiers are kept a value (`subjects_holding`), and
# only for the values the description publishes, in one pass over the
# column's cells beside each subject column's. A column it holds is
# described once more. A table whose subject columns are each different
# on every row, or that has none, is described byte for byte as before.
# THE SHARE OF REPEATED ROWS THAT MAY DIFFER FROM THE SUBJECT'S FIRST
# VALUE in a column still attached to it: one in ten, so a typing slip
# or a changed address does not undo the attachment.
ATTACHED_DIFFERENT_AT_MOST = 10

# Where in a column block a NUMBER is a count, a share or a size rather
# than a value of the column: a leaf whose own key holds any of these is
# no value, and nor is one whose key is a value of the column itself
# (`variants`, a census), which is the count beside it. `percent` is a
# whole key: `percentiles` are values.
_COUNT_KEYS = (
    "count",
    "rows",
    "n_",
    "share",
    "width",
    "length",
    "position",
    "ceiling",
    "floor",
    "distance",
    "std",
    "mean",
    "skew",
    "kurtosis",
    "digits",
    "cells",
    "line",
    "minimum",
    "maximum",
    "multiple",
    "slack",
    "uniqueness",
    "suppressed",
    # The places of a histogram's bins and of a calendar census -- a bin,
    # a weekday, a day of the month, an hour -- are no value of a cell.
    "first",
    "last",
    "bins",
)

# Where a whole entry -- its keys and its leaves -- holds no value of the
# column: spellings of nothing, withheld totals, repetition censuses.
# ...and rule A2's positional census (lane CODES-1, plan P4-D439): its
# lists are characters a place holds, never a cell's value, so a list such
# as `ABC` is not read as the code `ABC` some subjects hold.
_NO_VALUE_KEYS = ("missing", "withheld", "occurrences", "widths", "form_places")

# THE RUNGS: points along a column's range and the boundaries of its
# tails. The floor publishes them whatever the rows at the point, so a
# column NOT attached to the subject keeps them as a table of one row a
# person does (a measurement one patient holds on a row or two); a column
# attached to the subject counts them like every other value.
_RUNG_KEYS = (
    "percentiles",
    "percentiles_between",
    "date_percentiles",
    "clock_percentiles",
    "boundary",
)

# What is trimmed from each word of a sentence before it is compared.
_WORD_EDGES = ",.;:()[]{}'\"`"


@dataclasses.dataclass(frozen=True)
class SubjectCount:
    """How many rows hold one value, and who holds it, up to the floor.

    ``holders`` keeps at most `floor` different subject values: only
    whether a value reaches the floor matters, so a value held by more
    keeps exactly `floor` and costs no more.
    """

    rows: int
    holders: "tuple[str, ...]"


def subjects_holding(
    values: "list[str]",
    subjects: "list[str]",
    floor: int,
    absent: "tuple[str, ...]" = (),
) -> "dict[str, SubjectCount]":
    """Each value's rows and its different subjects, capped at the floor.

    PLAN P4-D406. ``values`` is one column's cells and ``subjects`` the
    subject column's cells, both in row order and of one length; each
    present cell, as written, is a value. Lanes MG and GR reuse it for a
    family read in patients, and it reads lane SR's `reading.
    column_values` unchanged. A subject cell is read as the subject it
    names, its spellings merged (`subject_keys`), and blank cells and
    every spelling of nobody are one subject between them (``absent``
    names the run's declared spellings of nothing): both readings can
    only make a value look held by FEWER people.

    Guarantees: accepts two lists of text of one length and the floor;
    returns, for every value some present cell holds, its rows and at
    most `floor` different subjects in the order first met. Memory: one
    entry a value, each at most `floor` subjects. Determinism: a fixed
    function of the arguments. Raises nothing. No I/O.
    """
    keyed: "list[tuple[str, ...]]" = []
    for cell in values:
        keyed += [(cell,) if parsing.folded(cell) else ()]
    return _holding(keyed, subject_keys(subjects, absent), floor)


def rows_as_holders(rows: int) -> "list[str]":
    """One holder a row, each told apart by its place (plan P4-D433).

    A date column no subject column counts in people is counted in rows:
    every row its own holder, so `_holding` keeps a date's first `floor`
    rows and a date one to `floor` - 1 rows hold is one the description
    may not publish. On a table of one row a person each row is a person.
    """
    return [f"{place}" for place in range(rows)]


def subject_keys(
    subjects: "list[str]", absent: "tuple[str, ...]" = ()
) -> "list[str]":
    """Each subject cell as the subject it names, its spellings merged.

    PLAN P4-D406 (lane HX2's skeptic, round 2, item 6). One patient's key
    written `REC20000007`, `rec20000007` and `REC-20000007` is one
    subject, not three: counted as written, a code six patients hold on
    eighteen spellings passed the floor of eleven. Each cell is folded
    (`parsing.folded`), every character of the ASCII range that is neither
    a letter nor a figure is dropped (one outside it is kept: the reading
    may merge fewer spellings, never split one), and so is every zero
    that opens a run of figures
    (a run of zeros alone stays one zero): `REC-0007`, `rec7` and
    `Rec 7` are all `rec7`. The reading can only MERGE spellings, never
    split one, so a value can only look held by fewer people than it is
    -- the side the floor errs on. Blank cells, and every cell the
    package's own vocabulary of nothing reads as absent (`NA`, `null`,
    `#DIV/0!`, `NaT`: `parsing.is_missing_text`) or that ``absent``
    names folded, are ONE unknown subject between them, as the
    population count reads them (`taxonomy.people_in`; Codex's review of
    lane HX2, item 3): eleven spellings of one unnamed patient are one
    person, never eleven.

    Guarantees: accepts a list of text; returns a list of one key a
    cell, in row order. Memory: one entry a different spelling, and a
    cell already in its merged form is returned as the same object.
    Determinism: a fixed function of the argument. Raises TypeError if a
    cell is not text. No I/O.
    """
    merged: "dict[str, str]" = {}
    keys: "list[str]" = []
    nobody: "dict[str, bool]" = {}
    for spelling in absent:
        nobody[parsing.folded(spelling)] = True
    for cell in subjects:
        if cell in merged:
            keys += [merged[cell]]
            continue
        if parsing.is_missing_text(cell) or parsing.folded(cell) in nobody:
            merged[cell] = ""
            keys += [""]
            continue
        key = _subject_key(cell)
        if key == cell:
            key = cell
        merged[cell] = key
        keys += [key]
    return keys


def _subject_key(cell: str) -> str:
    """One subject cell's merged form (`subject_keys`): `parsing.merged_key`, the one rule.

    Lane ID-ROOM reads its exclusions on the same form (plan P4-D432),
    so the rule lives once, in `parsing`, and both ask it.
    """
    return parsing.merged_key(cell)


# -- the made-up spellings read against the real cells (lane ID-ROOM4) --


def made_up_dry_runs(
    table: Table,
    document: "dict[str, object]",
    settings: taxonomy.Settings,
) -> "tuple[tuple[str, tuple[int, ...]], ...]":
    """The description texts the made-up spellings are read off, each with the places to read (plan P4-D489).

    A column of numbers too large or too small to hold publishes counts
    and widths and no value, and its twin is spelled by fixed counters
    (`generation.unrepresentable_spellings`: `1e400` onward at width 5,
    the mantissa zero-padded at width 6, a leading minus, `e-400`, `(-N)`,
    digit strings, `text-N`) in the very grammar code columns are written
    in: a column of 2,000 such codes, ten rows each, got 20,000 of its
    20,000 cells back as its own codes, with nothing in any file. So, once
    a description is final, `synthtwin profile` hands every block of that
    role to that one function -- the writer calls it too -- on the text
    the description is written as (`canonical.serialize`), read as
    `synthtwin generate` reads it (`cli._made_up_spellings_held`; the
    generator is no module the profile loads, so the validator never
    reaches it), and reads the spellings against the real cells
    (`made_up_spellings_named`). WHATEVER ITS ANSWER: a column the
    description declares `--code`, `--measurement` or `--decimal-comma`
    is read as its cells read with no declaration
    (`_unanswered_unrepresentable`), and that block is the one handed
    over, in a description of its own (`_with_unanswered_block`), since
    the writer copies by construction and no answer makes it safe --
    answered `code`, such a column became a long tail of labels whose
    stand-ins still wrote 6,440 real codes.

    Guarantees: the description's own text with the places of every
    block of the role, first, where there is one, then one text a declared
    column so read, in the table's column order; () where no column is of
    that role or so declared, without reading a cell. Linear in the cells
    of the columns read (a declared column is read once more by the role's
    own reader only where its cells mostly look numeric and one cannot be
    held). Reads the table only through `reading.column_values`. Raises
    nothing. No I/O.
    """
    blocks = document["columns"] if "columns" in document else None
    if not isinstance(blocks, list):
        return ()
    declared = _declared_readings(document)
    now: "list[int]" = []
    unanswered: "dict[int, dict[str, object]]" = {}
    storage: "tuple[str, ...] | None" = None
    for place in range(len(blocks)):
        block = blocks[place]
        if not isinstance(block, dict) or place >= len(table.column_names):
            continue
        role = block["role"] if "role" in block else None
        if role == taxonomy.ROLE_UNREPRESENTABLE or _a_key_block_unrepresentable(block):
            now += [place]
            continue
        if f"{block['name']}" not in declared or role == taxonomy.ROLE_IDENTIFIER:
            continue
        if storage is None:
            storage = stored_as_of(table, settings)
        found = _unanswered_unrepresentable(table, place, settings, storage)
        if found is not None:
            unanswered[place] = found
    runs: "list[tuple[str, tuple[int, ...]]]" = []
    if now:
        runs += [(canonical.serialize(document), tuple(now))]
    for place in sorted(unanswered):
        runs += [
            (
                canonical.serialize(
                    _with_unanswered_block(document, place, unanswered[place])
                ),
                (place,),
            )
        ]
    return tuple(runs)


def _a_key_block_unrepresentable(block: "dict[str, object]") -> bool:
    """Whether a keyed value column's block holds a key block, or the pooled block of its rare keys, of numbers too large or too small to hold (batch 4t's fix round, item 1).

    Such a block is written by the same writer from the same fixed
    counters (`generation.made_up_spellings_keyed`): a long table's assay
    of codes past a double's range, one code a person, nested under its
    key, got 4,000 of its 4,000 cells back as real codes while this check
    read the top-level blocks only. Raises nothing.
    """
    by_key = block["by_key"] if "by_key" in block else None
    if not isinstance(by_key, dict):
        return False
    inner: "list[object]" = []
    entries = by_key["key_blocks"] if "key_blocks" in by_key else None
    for entry in entries if isinstance(entries, list) else []:
        if isinstance(entry, dict) and "block" in entry:
            inner += [entry["block"]]
    if "pool" in by_key:
        inner += [by_key["pool"]]
    for one in inner:
        if isinstance(one, dict) and "role" in one and one["role"] == taxonomy.ROLE_UNREPRESENTABLE:
            return True
    return False


def made_up_spellings_named(
    table: Table,
    spelled: "dict[int, tuple[str, ...]]",
    subjects: "list[str]",
    settings: taxonomy.Settings,
    wider: "tuple[int, ...]" = (),
) -> "tuple[str, ...]":
    """The columns a made-up spelling of which equals a real value 1 to f-1 hold, counted in the description's subjects (plan P4-D489).

    ``spelled`` is each place's spellings, as the writer would write them
    (`made_up_dry_runs`). Each is read against the column's present real
    cells by merged key (`parsing.merged_key`, the form people are counted
    by; exact and case-folded equality are inside it) and by the number it
    writes (`parsing.exact_of_a_number`; batch 4t's last code round), and each real
    spelling so met is counted in its holders: the rows, and the people of
    every subject column the description is counted in (``subjects``:
    `synthtwin profile`'s final describe counts the person columns, the
    keys an open question holds and the open person question's
    candidates; each read as `subject_keys` reads a subject), the fewest of
    them (skeptic 1 of lane ID-ROOM4, item 2: a code on twenty rows of one
    person was copied while the person question was open, counted in
    rows). A column where the fewest holders are 1 to f-1 (f the smallest
    group size) is named: the rule errs toward naming.

    A PLACE OF ``wider`` -- a block already spelled one letter or figure
    wider, carrying NF139 -- IS NAMED WHERE ANY SPELLING EQUALS ANY REAL
    VALUE, however many hold it (Codex's review of lane ID-ROOM4, item 5;
    the orchestrator's LANE ID-ROOM4 RULINGS 6 (3)): NF139 promises that no
    cell of the twin equals one of the column's values, and the floor of
    11 is a rule about published counts, never about a twin cell equal to
    a real one (eleven cells `t10000` among codes `1e400` onward were
    written back as real while the promise stood). Guarantees: the names
    in the table's column order, each once. Linear in the cells of the
    columns read. Reads the table only through `reading.column_values`.
    Raises nothing. No I/O.
    """
    if not spelled:
        return ()
    holders: "list[tuple[int, list[str]]]" = []
    for place in range(len(table.column_names)):
        if f"{table.column_names[place]}" in subjects:
            holders += [
                (
                    place,
                    subject_keys(
                        reading.column_values(table, place),
                        settings.declared_missing_values,
                    ),
                )
            ]
    named: "list[str]" = []
    for place in range(len(table.column_names)):
        if place not in spelled or not spelled[place]:
            continue
        people = [keys for subject, keys in holders if subject != place]
        if _a_spelling_names_a_few(
            reading.column_values(table, place), spelled[place], people, settings, place in wider
        ):
            named += [f"{table.column_names[place]}"]
    return tuple(named)


def _declared_readings(document: "dict[str, object]") -> "list[str]":
    """The columns a description records as declared `--code`, `--measurement` or `--decimal-comma` (plan P4-D489)."""
    found: "list[str]" = []
    recorded = document["settings"] if "settings" in document else None
    if not isinstance(recorded, dict):
        return found
    for key in ("forced_codes", "forced_measurements", "forced_decimal_commas"):
        named = recorded[key] if key in recorded else None
        for name in named if isinstance(named, list) else []:
            if f"{name}" not in found:
                found += [f"{name}"]
    return found


def _unanswered_unrepresentable(
    table: Table,
    place: int,
    settings: taxonomy.Settings,
    storage: "tuple[str, ...]",
) -> "dict[str, object] | None":
    """A declared column's block as its cells read with no declaration, where that reading is of the unrepresentable role (plan P4-D489).

    The role's own reader decides (`taxonomy.profile_column`, nothing
    declared); it is asked only where most present cells look numeric and
    one at least is a number this format cannot hold (`parsing.
    classify_number`, each spelling read once, stopping as soon as more
    than half the cells are no number). None otherwise. Raises nothing.
    """
    cells = reading.column_values(table, place)
    present, _absent = taxonomy.split_missing(cells, settings)
    kinds: "dict[str, str]" = {}
    unholdable = 0
    other = 0
    for cell in present:
        if cell in kinds:
            kind = kinds[cell]
        else:
            kind = parsing.classify_number(cell)
            kinds[cell] = kind
        if kind == parsing.NOT_A_NUMBER:
            other = other + 1
            if other * 2 > len(present):
                return None
        elif kind != parsing.NUMBER:
            unholdable = unholdable + 1
    if not unholdable:
        return None
    read = taxonomy.profile_column(
        table.column_names[place],
        place + 1,
        cells,
        table.n_rows,
        settings,
        stored_as=storage[place] if place < len(storage) else "",
    )
    if read.role != taxonomy.ROLE_UNREPRESENTABLE:
        return None
    return _column_block(read)


def _with_unanswered_block(
    document: "dict[str, object]",
    place: int,
    block: "dict[str, object]",
) -> "dict[str, object]":
    """The description with one declared column read as its cells read unanswered: its block, and no declaration of it (plan P4-D489).

    A new document: ``document`` is not changed. Raises nothing.
    """
    blocks = document["columns"]
    columns: "list[object]" = []
    if isinstance(blocks, list):
        for index in range(len(blocks)):
            columns += [block if index == place else blocks[index]]
    name = f"{block['name']}"
    recorded = document["settings"]
    changed: "dict[str, object]" = {}
    if isinstance(recorded, dict):
        for key in recorded:
            value = recorded[key]
            if key in ("forced_codes", "forced_measurements", "forced_decimal_commas") and isinstance(value, list):
                value = [one for one in value if one != name]
            changed[key] = value
    variant: "dict[str, object]" = {}
    for key in document:
        variant[key] = document[key]
    variant["columns"] = columns
    variant["settings"] = changed
    return variant


def _a_spelling_names_a_few(
    cells: "list[str]",
    spellings: "tuple[str, ...]",
    people: "list[list[str]]",
    settings: taxonomy.Settings,
    every: bool = False,
) -> bool:
    """Whether a made-up spelling equals, by merged key or by value, a real present spelling 1 to f-1 people hold (plan P4-D489).

    Each real spelling whose merged key a made-up spelling has, or whose
    number a made-up spelling writes, is counted in its holders, one pass
    over the rows: its rows and the people of every subject column
    (``people``, merged keys a row), the fewest of them; a count stops at
    the floor. Exactly, case-folded, merged or as one number, a twin cell
    spelled so would name a value so few hold. BY VALUE (batch 4t's last
    code round, item 1; the orchestrator's LANE I4t RULINGS 2 (1), on the
    scoped verify's carry 1): a number is read by the reader of record,
    held by this format or not (`parsing.exact_of_a_number`), so `30e404`
    meets a real `3e405` and `-2e411` a real code written with the minus
    sign U+2212, which no merged key joins. With ``every`` (a column
    spelled wider, whose evidence promises that no twin cell equals a real
    one), any real present spelling met is enough, however many hold it.
    Raises nothing.
    """
    floor = settings.small_cell_floor
    wanted: "dict[str, bool]" = {}
    numbers: "dict[tuple[int, tuple[str, ...], int], bool]" = {}
    for spelling in spellings:
        wanted[parsing.merged_key(spelling)] = True
        number = parsing.exact_of_a_number(spelling)
        if number is not None:
            numbers[number] = True
    _present, absent = taxonomy.split_missing(cells, settings)
    nobody: "dict[str, bool]" = {}
    for spelling, _class in absent:
        nobody[spelling] = True
    rows: "dict[str, int]" = {}
    seen: "list[dict[str, dict[str, bool]]]" = [{} for _each in people]
    met: "dict[str, bool]" = {}
    for row in range(len(cells)):
        cell = cells[row]
        if cell in nobody or not parsing.trimmed(cell):
            continue
        if cell not in met:
            written = parsing.exact_of_a_number(cell) if numbers else None
            met[cell] = parsing.merged_key(cell) in wanted or (
                written is not None and written in numbers
            )
        if not met[cell]:
            continue
        if every:
            return True
        rows[cell] = rows[cell] + 1 if cell in rows else 1
        for index in range(len(people)):
            if cell not in seen[index]:
                seen[index][cell] = {}
            holders = seen[index][cell]
            if len(holders) < floor and row < len(people[index]):
                holders[people[index][row]] = True
    for cell in rows:
        held = rows[cell]
        for index in range(len(people)):
            held = min(held, len(seen[index][cell]))
        if held < floor:
            return True
    return False


def _holding(
    keyed: "typing.Iterable[tuple[str, ...]]", subjects: "list[str]", floor: int
) -> "dict[str, SubjectCount]":
    """`subjects_holding` over the keys each row's cell is counted as."""
    rows: "dict[str, int]" = {}
    held: "dict[str, list[str]]" = {}
    # ...and, past a small floor, a mapping beside each list, so a raised
    # floor never asks a long list whether it holds a subject (Codex's
    # review of lane HX2, item 10). At the default floor of eleven the
    # list alone is asked, and costs no more memory than it did.
    sets: "dict[str, dict[str, bool]]" = {}
    small = floor <= _LIST_ASKED_UP_TO
    for place, keys in enumerate(keyed):
        if not keys:
            continue
        subject = subjects[place]
        for key in keys:
            if key in rows:
                rows[key] = rows[key] + 1
                holders = held[key]
                if len(holders) >= floor:
                    continue
                if small:
                    if subject not in holders:
                        holders += [subject]
                elif subject not in sets[key]:
                    holders += [subject]
                    met = sets[key]
                    met[subject] = True
                    if len(holders) >= floor:
                        del sets[key]
            else:
                rows[key] = 1
                held[key] = [subject]
                if not small:
                    sets[key] = {subject: True}
    counted: "dict[str, SubjectCount]" = {}
    for key in rows:
        counted[key] = SubjectCount(rows[key], tuple(held[key]))
    return counted


# The floor up to which `_holding` asks each value's list of subjects
# whether it holds one: a list of sixteen is asked as fast as a set.
_LIST_ASKED_UP_TO = 16


def _repeats(cells: "list[str]") -> bool:
    """Whether two present cells of a column hold the same text."""
    seen: "dict[str, bool]" = {}
    for cell in cells:
        if not parsing.folded(cell):
            continue
        if cell in seen:
            return True
        seen[cell] = True
    return False


def _reaches_the_floor(cells: "list[str]", floor: int) -> bool:
    """Whether a subject column holds at least `floor` different values.

    A candidate of fewer cannot be the people of a table this command
    describes once answered -- declared, it is under the population floor
    and the run is refused -- and, counted in, no value of any other
    column could reach the floor, so the description would publish
    nothing: a ward code of eight values put the person question would
    blank every other column of its table (plan P4-D406).
    """
    seen: "dict[str, bool]" = {}
    for cell in cells:
        if parsing.folded(cell) and cell not in seen:
            seen[cell] = True
            if len(seen) >= floor:
                return True
    return False


def _attached(values: "list[str]", subjects: "list[str]") -> bool:
    """Whether a column holds one value a subject: a fact about the person.

    Counted over the present cells of subjects met before: attached when
    at least one is met again and at most one in
    `ATTACHED_DIFFERENT_AT_MOST` of those differs, folded, from the value
    the subject was first met with.
    """
    first: "dict[str, str]" = {}
    again = 0
    different = 0
    for place, cell in enumerate(values):
        text = parsing.folded(cell)
        if not text:
            continue
        subject = subjects[place]
        if subject in first:
            again = again + 1
            if first[subject] != text:
                different = different + 1
        else:
            first[subject] = text
    return again > 0 and different * ATTACHED_DIFFERENT_AT_MOST <= again


def _names_its_people(values: "list[str]", subjects: "list[str]") -> bool:
    """Whether an attached column tells its subjects apart (plan P4-D406).

    A column all but constant is attached to any key that repeats: four
    hundred `north` beside fifteen `south` and one `west` hold one value a
    filler code of seven values nearly everywhere. It says which subject
    a row is only where no one value is the first one met for more than
    half the subjects -- a name, a birth date, a plan number. Asked under
    a subject column of fewer than the floor's number of values, where
    every value is held by fewer subjects than the floor.
    """
    first: "dict[str, str]" = {}
    for place, cell in enumerate(values):
        text = parsing.folded(cell)
        if text and subjects[place] not in first:
            first[subjects[place]] = text
    met: "dict[str, int]" = {}
    commonest = 0
    for subject in first:
        text = first[subject]
        met[text] = (met[text] if text in met else 0) + 1
        commonest = max(commonest, met[text])
    return len(first) >= 2 and commonest * 2 <= len(first)


@dataclasses.dataclass(frozen=True)
class _Published:
    """What a column block publishes that a cell could be: its values."""

    words: "frozenset[str]"
    numbers: "frozenset[float]"
    prefixes: "tuple[str, ...]"
    date_format: str
    # A column of clock times: the form its block reads them in, and each
    # published time as a count of its unit (`parsing.clock_ordinal`), so
    # a cell `8:30` is counted under the `08:30` the block prints (Codex's
    # review of lane HX2, item 5).
    clock_form: str = ""
    clocks: "frozenset[int]" = frozenset()
    # A column whose offsets differ publishes every date on the shared
    # clock (`datetimes_read_at` `utc`): a cell is counted under the
    # instant it names there, never its local text (plan P4-D433, repair
    # round 2, the combined verify's item 2).
    at_utc: bool = False


@dataclasses.dataclass(frozen=True)
class _CellReading:
    """How the run reads one column's cells, beyond its block (plan P4-D406).

    ``member`` is the system a column of counted dates is declared in
    (`--date-count`, read as dates), "" for any other; ``comma`` whether
    the column was declared to write a decimal comma. Its block alone does
    not say either, and a cell `19000` or `10,07` is the date or the
    number the block publishes only read so (Codex's review of lane HX2,
    item 5).
    """

    member: str = ""
    comma: bool = False
    # A unit column rule 7 stood aside for (plan P4-D438): a cell is the
    # number beside its unit, `98.4 F` the 98.4 its block publishes.
    affixed: bool = False
    # ...read inside the wrappers the block publishes (repair 1 of lane
    # UN-1b, Codex item 2): `5 mL/min/1.73m2` is the 5 its block prints,
    # never the 1.73 of its unit. Longest wrapper first.
    wrappers: "tuple[tuple[str, str], ...]" = ()


# The figures a cell's longest run may hold and still be read as a
# number: past this a run is no value a block can publish, and reading
# it would overflow a float (Codex's review of lane HX2, item 8).
_FIGURES_READ_AT_MOST = 300


def _under(key: str, names: "tuple[str, ...]") -> bool:
    for one in names:
        if one in key:
            return True
    return False


def _parts(key: str) -> "list[str]":
    """A block path's parts, between its points."""
    if not isinstance(key, str):
        raise TypeError("internal check: a block path was not text")
    found: "list[str]" = []
    part = ""
    for character in key:
        if character == ".":
            found += [part]
            part = ""
        else:
            part = part + character
    return found + [part]


def _words(text: str) -> "list[str]":
    """A sentence's words, each without the marks at its ends."""
    if not isinstance(text, str):
        raise TypeError("internal check: a sentence was not text")
    found: "list[str]" = []
    word = ""
    for character in text + " ":
        if character in " \t\r\n":
            while word and word[0] in _WORD_EDGES:
                word = word[1:]
            while word and word[-1] in _WORD_EDGES:
                word = word[:-1]
            if word:
                found += [word]
            word = ""
        else:
            word = word + character
    return found


def _a_rung(key: str) -> bool:
    """Whether a leaf's path runs through a rung (`_RUNG_KEYS`)."""
    for part in _parts(key):
        if part in _RUNG_KEYS:
            return True
    return False


def _plainly(key: str, plain: _Published) -> bool:
    """Whether a counted key is published off the rungs too."""
    if key[:1] == "c":
        return int(key[1:]) in plain.clocks
    if key[:1] == "w":
        return key[1:] in plain.words
    if key[:1] == "p":
        return key[1:] in plain.prefixes
    if key[:1] == "n":
        return _number_of(key[1:]) in plain.numbers
    return True


def _a_field(key: str) -> bool:
    """Whether a block key is a field's name: small letters, figures, `_`."""
    if not key or not ("a" <= key[0] <= "z"):
        return False
    for character in key:
        if not ("a" <= character <= "z" or "0" <= character <= "9" or character == "_"):
            return False
    return True


def _number_of(text: str) -> "float | None":
    try:
        return parsing.parse_number(text)
    except (TypeError, ValueError):
        return None


def _published_in(block: "dict[str, object]", rungs: bool) -> _Published:
    """Every value a column block publishes, read as a cell could be.

    Each text leaf and each mapping key, folded, and each word of a
    sentence; each number leaf that is not a count, share or size
    (`_COUNT_KEYS`); each text leaf under a key naming a prefix; and the
    format the block reads its dates in, so a cell is compared with the
    date as the block writes it. ``rungs`` false leaves out the points
    along the range and the tails' boundaries (`_RUNG_KEYS`).
    """
    words: "dict[str, bool]" = {}
    numbers: "dict[float, bool]" = {}
    prefixes: "dict[str, bool]" = {}
    clocks: "dict[int, bool]" = {}
    clock_form = ""
    if (
        "role" in block
        and block["role"] == taxonomy.ROLE_CLOCK
        and "clock_form" in block
        and isinstance(block["clock_form"], str)
        and block["clock_form"] in parsing.CLOCK_FORMS
    ):
        clock_form = block["clock_form"]
    waiting: "list[tuple[str, object]]" = []
    for key in block:
        if key != "name":
            waiting += [(key, block[key])]
    cursor = 0
    while cursor < len(waiting):
        key, leaf = waiting[cursor]
        cursor = cursor + 1
        if _under(key, _NO_VALUE_KEYS):
            continue
        if not rungs and _a_rung(key):
            continue
        if isinstance(leaf, bool) or leaf is None:
            continue
        if isinstance(leaf, dict):
            for inner in leaf:
                words[parsing.folded(f"{inner}")] = True
                waiting += [(f"{key}.{inner}", leaf[inner])]
            continue
        if isinstance(leaf, list):
            for item in leaf:
                waiting += [(key, item)]
            continue
        if isinstance(leaf, (int, float)):
            own = _parts(key)[-1]
            if own != "percent" and _a_field(own) and not _under(
                own, _COUNT_KEYS
            ):
                numbers[float(leaf)] = True
            continue
        if not isinstance(leaf, str):
            continue
        words[parsing.folded(leaf)] = True
        if clock_form:
            ordinal = parsing.clock_ordinal(leaf, clock_form)
            if ordinal is not None:
                clocks[ordinal] = True
        if "prefix" in key and leaf:
            prefixes[parsing.folded(leaf)] = True
        number = _number_of(leaf)
        if number is not None:
            numbers[number] = True
        for word in _words(leaf):
            trimmed = parsing.folded(word)
            words[trimmed] = True
            number = _number_of(trimmed)
            if number is not None:
                numbers[number] = True
    shown = block["format"] if "format" in block else ""
    role = block["role"] if "role" in block else ""
    # A cell is read again on its day only where the block publishes a
    # date in the form a reading gives it (`YYYY-MM-DD`, `YYYY-Qn`): with
    # none, no cell's day can be a published value, and a column of
    # date-and-time cells each different is not parsed twice (lane HX2's
    # skeptic, round 2, item 7).
    days = False
    for word in words:
        if _a_read_date(word):
            days = True
            break
    return _Published(
        frozenset(words),
        frozenset(numbers),
        tuple(sorted(prefixes)),
        shown
        if isinstance(shown, str) and role == taxonomy.ROLE_DATETIME and days
        else "",
        clock_form,
        frozenset(clocks),
        _on_the_shared_clock(block),
    )


def _on_the_shared_clock(block: "dict[str, object]") -> bool:
    """Whether a block publishes its dates on the shared clock (`datetimes_read_at` `utc`)."""
    return (
        "datetimes_read_at" in block
        and block["datetimes_read_at"] == taxonomy.READ_AT_UTC
    )


def _a_read_date(word: str) -> bool:
    """Whether a published word opens as a reading writes a date: four figures and a dash."""
    if len(word) < 7 or word[4:5] != "-":
        return False
    for character in word[:4]:
        if not "0" <= character <= "9":
            return False
    return True


def _longest_figures(text: str) -> str:
    """A cell's longest run of figures, or nothing."""
    longest = ""
    run = ""
    for character in text:
        if "0" <= character <= "9":
            run = run + character
            continue
        if len(run) > len(longest):
            longest = run
        run = ""
    return run if len(run) > len(longest) else longest


def _keys_of(
    cell: str,
    published: _Published,
    memo: "dict[str, tuple[str, ...]]",
    reading: "_CellReading | None" = None,
) -> "tuple[str, ...]":
    """What a cell is counted as: each published value it reads as.

    As the run reads the column (``reading``): a declared decimal comma
    read as the point, a declared count of days read as the date it
    counts, and a clock time as its count of minutes or seconds, so
    `10,07`, `19000` and `8:30` are counted under the `10.07`,
    `2022-01-08` and `08:30` the block prints.
    """
    if cell in memo:
        return memo[cell]
    how = _CellReading() if reading is None else reading
    found: "list[str]" = []
    folded = parsing.folded(cell)
    if folded:
        if folded in published.words:
            found += [f"w{folded}"]
        if published.numbers:
            number = _number_of(
                parsing.written_with_a_decimal_comma(cell) if how.comma else cell
            )
            if number is None and how.affixed:
                number = _number_inside(cell, how.wrappers, how.comma)
            if number is None and how.affixed:
                number = _number_beside(cell, how.comma)
            if number is None:
                figures = _longest_figures(folded)
                if figures and len(figures) <= _FIGURES_READ_AT_MOST:
                    number = float(int(figures))
            if number is not None and number in published.numbers:
                found += [f"n{number!r}"]
        if published.date_format:
            read = parsing.parse_datetime(cell, published.date_format)
            if read is not None:
                # ON THE CLOCK THE BLOCK PUBLISHES: a cell written with its
                # offset is counted under its instant at UTC, the text the
                # block prints for it (`parsing.utc_moment`).
                moved = (
                    parsing.utc_moment(read[0], read[1])
                    if published.at_utc and read[1]
                    else None
                )
                day = parsing.folded(read[0] if moved is None else moved)
                if day in published.words and day != folded:
                    found += [f"w{day}"]
        if how.member:
            for day in _counted_days(cell, how):
                if day in published.words and f"w{day}" not in found:
                    found += [f"w{day}"]
        if published.clock_form:
            ordinal = parsing.clock_ordinal(cell, published.clock_form)
            if ordinal is not None and ordinal in published.clocks:
                found += [f"c{ordinal}"]
        for prefix in published.prefixes:
            if folded[: len(prefix)] == prefix:
                found += [f"p{prefix}"]
    frozen = tuple(found)
    if len(memo) < 65536:
        memo[cell] = frozen
    return frozen


def _published_wrappers(
    details: "dict[str, object]",
) -> "tuple[tuple[str, str], ...]":
    """The wrappers an affixed block publishes, the longest first (repair 1 of lane UN-1b, Codex item 2).

    The commonest pair (`affix_prefix`, `affix_suffix`) and every entry of
    `affix_variants`; ties in the order the block lists them. A fixed
    function of the details. Raises nothing. No I/O.
    """
    found: "list[tuple[str, str]]" = []
    prefix = details["affix_prefix"] if "affix_prefix" in details else ""
    suffix = details["affix_suffix"] if "affix_suffix" in details else ""
    if isinstance(prefix, str) and isinstance(suffix, str):
        found += [(prefix, suffix)]
    variants = details["affix_variants"] if "affix_variants" in details else []
    if isinstance(variants, list):
        for entry in variants:
            if not isinstance(entry, dict):
                continue
            front = entry["prefix"] if "prefix" in entry else None
            back = entry["suffix"] if "suffix" in entry else None
            if isinstance(front, str) and isinstance(back, str):
                if (front, back) not in found:
                    found += [(front, back)]
    longest = 0
    for front, back in found:
        longest = max(longest, len(front) + len(back))
    ordered: "list[tuple[str, str]]" = []
    for size in range(longest, -1, -1):
        for front, back in found:
            if len(front) + len(back) == size:
                ordered += [(front, back)]
    return tuple(ordered)


def _number_inside(
    cell: str, wrappers: "tuple[tuple[str, str], ...]", comma: bool
) -> "float | None":
    """The number a cell writes inside one of its column's published wrappers, or None.

    The cell trimmed, its prefix and suffix taken off as the block reads
    them (`taxonomy.affixed_split` trims a cell before splitting it), the
    rest read as a number under the column's grammar. The first wrapper
    that reads wins, the longest first. Raises nothing. No I/O.
    """
    text = parsing.trimmed(cell)
    for prefix, suffix in wrappers:
        if not prefix and not suffix:
            continue
        if len(text) <= len(prefix) + len(suffix):
            continue
        if text[: len(prefix)] != prefix:
            continue
        if suffix and text[len(text) - len(suffix) :] != suffix:
            continue
        core = text[len(prefix) : len(text) - len(suffix)]
        if len(core) > _FIGURES_READ_AT_MOST:
            continue
        number = _number_of(
            parsing.written_with_a_decimal_comma(core) if comma else core
        )
        if number is not None:
            return number
    return None


def _number_beside(cell: str, comma: bool) -> "float | None":
    """The number a cell writes beside its unit: its longest run of figures and one point.

    Read for a unit column rule 7 stood aside for (plan P4-D438), whose
    block publishes `98.4` for the cell `98.4 F`; a minus directly in
    front is the number's. None where no such run reads as a number.
    """
    point = "," if comma else "."
    best = ""
    run = ""
    for character in cell + " ":
        if "0" <= character <= "9" or (character == point and point not in run):
            run = run + ("." if character == point else character)
            continue
        if len(_longest_figures(run)) > 0 and len(run) > len(best):
            best = run
        run = "-" if character == "-" else ""
    if not best or len(best) > _FIGURES_READ_AT_MOST:
        return None
    return _number_of(best)


def _counted_days(cell: str, reading: _CellReading) -> "list[str]":
    """The date a counted cell names, as a reading writes it: day, minute, second."""
    mark = date_counts.COMMA if reading.comma else date_counts.POINT
    written = date_counts.counted(reading.member, cell, mark)
    if written is None:
        return []
    numerator, denominator = date_counts.exact_value(written)
    moment = date_counts.moment_of(
        reading.member, numerator, denominator, date_counts.SECOND
    )
    if moment is None:
        return []
    found: "list[str]" = []
    for unit in (date_counts.DAY, date_counts.MINUTE, date_counts.SECOND):
        found += [
            parsing.folded(date_counts.iso_text(moment, date_counts.SECOND, unit))
        ]
    return found


# THE KEYS A CELL IS COUNTED UNDER beside the values it reads as
# (`_cell_keys`): every present cell counts under `_KEY_PRESENT`, the
# column's printed totals -- its present rows, its mean, its spread -- and
# a present cell that reads as no published value counts under
# `_KEY_REMAINDER`, the remainder the row floor merges and prints as one
# count. A cell wearing a published written form counts under `f` and
# that form.
_KEY_PRESENT = "a"
_KEY_REMAINDER = "r"
_PRESENT_ONLY = (_KEY_PRESENT,)
# The block's sentences, set aside where a pool counted in people is read again.
_SENTENCE_KEYS = ("detection_evidence", "remarks")


def _named_forms(block: "dict[str, object]") -> "dict[str, int]":
    """The written forms a block's `shape_forms` census names, pool apart."""
    forms = block["shape_forms"] if "shape_forms" in block else None
    named: "dict[str, int]" = {}
    if isinstance(forms, dict):
        for form in forms:
            count = forms[form]
            if form != taxonomy.SUPPRESSED_LABEL and isinstance(count, int):
                named[f"{form}"] = count
    return named


def _cell_keys(
    cell: str,
    published: _Published,
    forms: "dict[str, int]",
    absent: "frozenset[str]",
    memo: "dict[str, tuple[str, ...]] | None",
    interned: "dict[tuple[str, ...], tuple[str, ...]]",
    reading: "_CellReading | None" = None,
) -> "tuple[str, ...]":
    """Every key one cell is counted under, nothing for an absent cell.

    The tuple returned is the one ``interned`` already holds for the same
    keys, so a column of cells each different -- every one a miss of the
    capped ``memo`` -- keeps one reference a row and not one tuple a row
    (lane HX2's skeptic, round 2, item 7). A caller that keeps its own memo
    of what each cell is counted as passes None, and none is kept here.
    """
    if memo is not None and cell in memo:
        return memo[cell]
    found: "list[str]" = []
    if parsing.folded(cell) and cell not in absent:
        values = _keys_of(cell, published, {}, reading)
        found += list(values)
        found += [_KEY_PRESENT]
        if not values:
            found += [_KEY_REMAINDER]
        if forms:
            form = parsing.census_form(cell, forms)
            if form in forms:
                found += [f"f{form}"]
    frozen = tuple(found)
    if frozen in interned:
        frozen = interned[frozen]
    else:
        interned[frozen] = frozen
    if memo is not None and len(memo) < _PEOPLE_MEMO_TEXTS:
        memo[cell] = frozen
    return frozen


def _subjects_beside(
    name: str,
    subject_names: "list[str]",
    subject_cells: "list[list[str]]",
    subject_enough: "list[bool]",
) -> "tuple[list[list[str]], list[bool]]":
    """The subject columns a column is counted in, every one but itself, and whether each holds the floor's values (plan P4-D477). No I/O."""
    people: "list[list[str]]" = []
    enough: "list[bool]" = []
    for place in range(len(subject_names)):
        if subject_names[place] != name:
            people += [subject_cells[place]]
            enough += [subject_enough[place]]
    return people, enough


def _plain_reading(described: taxonomy.ColumnProfile, comma: bool) -> "_CellReading":
    """How the count in people reads a column that is no date (`_CellReading`, plan P4-D406): its comma, its unit and its wrappers. No I/O."""
    return _CellReading(
        "", comma, described.role == taxonomy.ROLE_AFFIXED, _published_wrappers(described.details)
    )


def _ends_asked(
    ends: "tuple[int, int]", few: "list[int]", low_need: int, high_need: int
) -> "tuple[bool, int, int]":
    """Each value 1 to `floor` - 1 people still hold taken into the band of the nearer end (plan P4-D477): whether one moved, and the two reaches.

    A value nearer the low band than the top one moves the low band's
    reach up to it, any other the top band's down to it; the reaches only
    ever widen. A fixed function of its arguments. No I/O.
    """
    moved = False
    for value in few:
        if value - ends[0] <= ends[1] - value:
            if value > low_need:
                low_need = value
                moved = True
        elif high_need < 0 or value < high_need:
            high_need = value
            moved = True
    return moved, low_need, high_need


# How many times an age column's ends are drawn again (plan P4-D477).
_END_ROUNDS = 8


def _ends_seeded(
    cells: "list[str]",
    comma: bool,
    absent: "frozenset[str]",
    described: taxonomy.ColumnProfile,
    floor: int,
    mark: int,
    people: "list[list[str]]",
    words: bool,
) -> "tuple[int, int, int, int] | None":
    """The ends drawn where neither end needs a band but a value few people hold stands inside: (low, high, the low band's reach, the top band's), or None (plan P4-D486).

    Lane HB3-a2's widening, W (4): each whole age a value the block
    publishes, or its remainder, 1 to `floor` - 1 people hold
    (`_published_few`, `_remainder_few`) is taken into the band of the nearer
    of the column's least and largest ages (`_ends_asked`), and the ends are
    drawn again with those reaches (`taxonomy.ends_pooled_in_people`). None
    where no such value is, or no ends are drawn even so. Linear in the
    rows. No I/O.
    """
    ages = taxonomy.ages_as_read(cells, comma, absent, mark, words)
    least = -1
    largest = -1
    for entry in ages:
        if entry is not None and entry[1] >= 0:
            least = entry[1] if least < 0 or entry[1] < least else least
            largest = entry[1] if entry[1] > largest else largest
    if least < 0 or largest <= least:
        return None
    few = _published_few(described, ages, people, floor)
    if not few:
        few = _remainder_few(described, ages, people, floor)
    moved, low_need, high_need = _ends_asked((least, largest), few, -1, -1)
    if not moved:
        return None
    drawn = taxonomy.ends_pooled_in_people(cells, comma, absent, floor, mark, people, words, low_need, high_need)
    if drawn is None:
        return None
    return drawn[0], drawn[1], low_need, high_need


def _published_few(
    described: taxonomy.ColumnProfile,
    ages: "list[tuple[float, int] | None]",
    people: "list[list[str]]",
    floor: int,
) -> "list[int]":
    """The ages, in the column's unit, of each whole number a block publishes that 1 to ``floor`` - 1 people hold under some subject column (plan P4-D477).

    ``ages``: each cell's number as the block reads it and its age in the
    column's unit (`taxonomy.ages_as_read`; lane HB2's repair 2, Codex's
    item 1: a cell written `960 months` or `Age 95` was read as no
    published value). Linear in the rows. No I/O.
    """
    shown = _published_in(_column_block(described), True)
    wanted: "dict[float, bool]" = {}
    for number in shown.numbers:
        if number == int(number) and number >= 0:
            wanted[number] = True
    held: "list[dict[float, dict[str, bool]]]" = [{} for _subjects in people]
    aged: "dict[float, dict[int, bool]]" = {}
    for place in range(len(ages)):
        entry = ages[place]
        if entry is None or entry[0] not in wanted:
            continue
        if entry[1] >= 0:
            if entry[0] not in aged:
                aged[entry[0]] = {}
            aged[entry[0]][entry[1]] = True
        for column in range(len(people)):
            holders = held[column]
            if entry[0] not in holders:
                holders[entry[0]] = {}
            if len(holders[entry[0]]) < floor:
                holders[entry[0]][people[column][place]] = True
    few: "dict[int, bool]" = {}
    for number in wanted:
        if any(0 < len(holders[number]) < floor for holders in held if number in holders):
            for age in aged[number] if number in aged else {}:
                few[age] = True
    return sorted(few)


def _groups_few(
    described: taxonomy.ColumnProfile,
    ages: "list[tuple[float, int] | None]",
    people: "list[list[str]]",
    floor: int,
) -> "list[int]":
    """The whole numbers of each bin group a block publishes that 1 to ``floor`` - 1 people hold under some subject column (plan P4-D477).

    LANE HB2'S REPAIR 1 (LANE HB2 RULINGS 4 (4): every published group held
    by the floor's people): a tail block's histogram closes a group once it
    holds the floor's ROWS (`taxonomy._tail_bins`), and beside a subject
    column whose people hold 20 rows each one person's age closes a group
    alone -- three such groups over the statistics check's 34 draws at
    1,000 people of 20 rows. The interior rows are read by rank as the block
    read them (its tails' rows set aside at each end, ties in row order),
    each in its bin of the scale between the tails' boundary rungs
    (`parsing.histogram_bin`), and each group's people counted, the floor's
    at most. Such a group's values are taken into the nearer band as a
    published value few people hold is, each in the column's unit
    (``ages``, `taxonomy.ages_as_read`: each cell's number as the block
    reads it, a number written with words or a unit too -- lane HB2's
    repair 2, Codex's item 1). Empty where the block publishes no group.
    Sorts the rows once. No I/O.
    """
    block = _column_block(described)
    groups = block["bin_groups"] if "bin_groups" in block else None
    tails = block["tails"] if "tails" in block else None
    if not isinstance(groups, list) or not groups or not isinstance(tails, dict):
        return []
    low = tails["low"] if "low" in tails else None
    high = tails["high"] if "high" in tails else None
    if not isinstance(low, dict) or not isinstance(high, dict):
        return []
    points: "dict[str, object]" = {}
    for key in ("percentiles", "percentiles_between"):
        found = block[key] if key in block else None
        if isinstance(found, dict):
            for rung in found:
                points[rung] = found[rung]
    low_percent = low["percent"] if "percent" in low else None
    high_percent = high["percent"] if "percent" in high else None
    low_rows = low["rows"] if "rows" in low else None
    high_rows = high["rows"] if "rows" in high else None
    if not (
        isinstance(low_percent, int) and isinstance(high_percent, int)
        and isinstance(low_rows, int) and isinstance(high_rows, int)
    ):
        return []
    low_rung = f"p{low_percent:02d}"
    high_rung = f"p{high_percent:02d}"
    lowest = points[low_rung] if low_rung in points else None
    highest = points[high_rung] if high_rung in points else None
    if not isinstance(lowest, float) or not isinstance(highest, float) or not highest > lowest:
        return []
    read: "list[tuple[float, int]]" = []
    for place in range(len(ages)):
        entry = ages[place]
        if entry is not None:
            read += [(entry[0], place)]
    interior = sorted(read)[low_rows: len(read) - high_rows]
    holders: "list[dict[int, dict[str, bool]]]" = [{} for _subjects in people]
    values: "dict[int, dict[int, bool]]" = {}
    for value, place in interior:
        at = parsing.histogram_bin(value, lowest, highest)
        found = ages[place]
        if found is not None and found[1] >= 0:
            if at not in values:
                values[at] = {}
            values[at][found[1]] = True
        for column in range(len(people)):
            if at not in holders[column]:
                holders[column][at] = {}
            held = holders[column][at]
            if len(held) < floor:
                held[people[column][place]] = True
    few: "dict[int, bool]" = {}
    for group in groups:
        first = group["first"] if isinstance(group, dict) and "first" in group else None
        last = group["last"] if isinstance(group, dict) and "last" in group else None
        if not isinstance(first, int) or not isinstance(last, int):
            continue
        for column in range(len(people)):
            union: "dict[str, bool]" = {}
            for at in range(first, last + 1):
                for subject in holders[column][at] if at in holders[column] else {}:
                    if len(union) < floor:
                        union[subject] = True
            if 0 < len(union) < floor:
                for at in range(first, last + 1):
                    for whole in values[at] if at in values else {}:
                        few[whole] = True
    return sorted(few)


def _band_values_keep_the_floor(
    candidate: taxonomy.ColumnProfile,
    written: "list[str]",
    comma: bool,
    absent: "frozenset[str]",
    mark: int,
    words: bool,
    people: "list[list[str]]",
    enough: "list[bool] | None",
    floor: int,
) -> bool:
    """Whether a top-coded column whose end bands are written at the mean age of their rows (`taxonomy.ends_band_values`) publishes no value, remainder or bin group 1 to ``floor`` - 1 people hold (lane RX-1, the fidelity plan; P4-D486 (6)(e)).

    The checks the ends' rounds made of the column with its bands at their
    edges (`_counted_in_subjects`, `_groups_few`), made again of
    ``candidate``, the column described from ``written``, its bands at their
    means: the bands hold the same people, and only where every count in
    people the edges kept still holds is the column written so. Guarantees:
    a fixed function of its arguments. Raises nothing of its own. No I/O.
    """
    if _counted_in_subjects(candidate, written, people, floor, enough, _plain_reading(candidate, comma)):
        return False
    return not _groups_few(candidate, taxonomy.ages_as_read(written, comma, absent, mark, words), people, floor)


def _held_from(
    cells: "list[str]",
    before_ends: "list[str]",
    ends: "tuple[int, int] | None",
    forced: bool,
) -> "list[str]":
    """The cells a column the count in people holds is held from: as they stood before its ends were pooled, where they were (plan P4-D477).

    A held column's block is read off its cells as the line before the lane
    read them, never off the bands its ends were written as; a description
    checked again (``forced``) is read as it was made. Lane HB2's repair 1
    (skeptic 1's item 6, M20): the describe reaches it only where its count
    in people holds a column whose ends a round freed, which no table
    measured has reached (the rounds' count and this one read the same
    block, cells and people); it is a guard, pinned on its own. A fixed
    function of the four. No I/O.
    """
    if ends is not None and not forced:
        return before_ends
    return cells


def _remainder_few(
    described: taxonomy.ColumnProfile,
    ages: "list[tuple[float, int] | None]",
    people: "list[list[str]]",
    floor: int,
) -> "list[int]":
    """The whole numbers of a block's remainder where 1 to ``floor`` - 1 people hold it under some subject column, read off its cells as written (plan P4-D477).

    The remainder is the cells that read as no value the block publishes
    (`_KEY_REMAINDER`), counted in people as one count. LANE HB2'S REPAIR
    1 (the statistics check's item 3): at 1,000 people of 20 rows a round
    drew the ends (37, 74) and the count in people still held the column
    on its remainder alone -- one age no published point named, 140 rows of
    7 people -- which `_published_few` cannot see, so the rounds stopped
    and the column was held; such values are taken into the nearer band as
    `_published_few`'s are, each in the column's unit (``ages``,
    `taxonomy.ages_as_read`; lane HB2's repair 2). Empty where the remainder
    is held by none or by the floor's people. Linear in the rows. No I/O.
    """
    shown = _published_in(_column_block(described), True)
    published: "dict[float, bool]" = {}
    for number in shown.numbers:
        if number == int(number) and number >= 0:
            published[number] = True
    values: "dict[int, bool]" = {}
    held: "list[dict[str, bool]]" = [{} for _subjects in people]
    for place in range(len(ages)):
        entry = ages[place]
        if entry is None or entry[1] < 0 or entry[0] in published:
            continue
        values[entry[1]] = True
        for column in range(len(people)):
            if len(held[column]) < floor:
                held[column][people[column][place]] = True
    if not any(0 < len(holders) < floor for holders in held):
        return []
    return sorted(values)


def _block_at(
    details: "dict[str, object]", path: "tuple[str, ...]", at: int
) -> "dict[str, object] | None":
    """The numeric block at a path of `taxonomy.numbers_by_block` in a column's details, or None where the details hold none there. No I/O."""
    if path == taxonomy.BLOCK_TOP:
        return details
    if path == taxonomy.BLOCK_NUMBERS:
        found = details["numbers"] if "numbers" in details else None
        return found if isinstance(found, dict) else None
    listed = details[path[0]] if path[0] in details else None
    if not isinstance(listed, list) or not 0 <= at < len(listed):
        return None
    entry = listed[at]
    if path == taxonomy.BLOCK_VARIANT:
        entry = entry["numbers"] if isinstance(entry, dict) and "numbers" in entry else None
    return entry if isinstance(entry, dict) else None


def _groups_written(
    details: "dict[str, object]", path: "tuple[str, ...]", at: int, groups: "list[dict[str, int]]"
) -> None:
    """Writes ``groups`` as the bin groups of the block at a path of `taxonomy.numbers_by_block` in ``details``, a copy of a column's details: every dictionary and list on the way copied first, so the column the details were copied from keeps its own. No I/O."""
    if path == taxonomy.BLOCK_TOP:
        details["bin_groups"] = groups
        return
    if path == taxonomy.BLOCK_NUMBERS:
        found = details["numbers"]
        if isinstance(found, dict):
            numbers = dict(found)
            numbers["bin_groups"] = groups
            details["numbers"] = numbers
        return
    listed = details[path[0]]
    if not isinstance(listed, list):
        return
    copied = list(listed)
    entry = copied[at]
    if not isinstance(entry, dict):
        return
    entry = dict(entry)
    if path == taxonomy.BLOCK_VARIANT:
        inner = entry["numbers"]
        if not isinstance(inner, dict):
            return
        numbers = dict(inner)
        numbers["bin_groups"] = groups
        entry["numbers"] = numbers
    else:
        entry["bin_groups"] = groups
    copied[at] = entry
    details[path[0]] = copied


def _block_groups_joined(
    block: "dict[str, object]",
    read: "list[tuple[float, int]]",
    counted: "list[list[str]]",
    floor: int,
) -> "tuple[bool, list[tuple[int, int, int]] | None]":
    """One numeric block's bin groups joined until each holds ``floor`` people under every subject column of ``counted``: (whether the column is held, the joined groups or None where they stand as published) (plan P4-D486, C5).

    ``read``: the (number, row) pairs the block was read over
    (`taxonomy.numbers_by_block`). The interior rows are read by rank as the
    block read them -- the tails' rows set aside at each end, ties in row
    order -- each in its bin of the scale between the tails' boundary rungs.
    Each group fewer than the floor's people hold is joined to the group
    after it until the run holds them, a short last run joined to the group
    before; the column is held where no run does. Where the numbers read do
    not number the block's own rows (its tails' rows and its groups' counts),
    the rank is not the block's: the groups are then joined into one,
    published only where the rows strictly between the two boundary rungs
    hold the floor's people, else the column is held. A block whose groups,
    tails or boundary rungs cannot be read holds the column. Sorts the rows
    once. No I/O.
    """
    groups = block["bin_groups"] if "bin_groups" in block else None
    tails = block["tails"] if "tails" in block else None
    if not isinstance(groups, list) or not groups or not isinstance(tails, dict):
        return False, None
    low = tails["low"] if "low" in tails else None
    high = tails["high"] if "high" in tails else None
    points: "dict[str, object]" = {}
    for key in ("percentiles", "percentiles_between"):
        found = block[key] if key in block else None
        if isinstance(found, dict):
            for rung in found:
                points[rung] = found[rung]
    low_percent = low["percent"] if isinstance(low, dict) and "percent" in low else None
    high_percent = high["percent"] if isinstance(high, dict) and "percent" in high else None
    low_rows = low["rows"] if isinstance(low, dict) and "rows" in low else None
    high_rows = high["rows"] if isinstance(high, dict) and "rows" in high else None
    if not (
        isinstance(low_percent, int) and isinstance(high_percent, int)
        and isinstance(low_rows, int) and isinstance(high_rows, int)
    ):
        return True, None
    lowest = points[f"p{low_percent:02d}"] if f"p{low_percent:02d}" in points else None
    highest = points[f"p{high_percent:02d}"] if f"p{high_percent:02d}" in points else None
    # ...two equal boundary rungs read every interior row in the first bin,
    # as `parsing.histogram_bin` reads a column of one number.
    if not isinstance(lowest, (int, float)) or not isinstance(highest, (int, float)) or highest < lowest:
        return True, None
    spans: "list[tuple[int, int, int]]" = []
    for group in groups:
        first = group["first"] if isinstance(group, dict) and "first" in group else None
        last = group["last"] if isinstance(group, dict) and "last" in group else None
        rows = group["count"] if isinstance(group, dict) and "count" in group else None
        if not isinstance(first, int) or not isinstance(last, int) or not isinstance(rows, int):
            return True, None
        spans += [(first, last, rows)]
    by_rank = len(read) == low_rows + high_rows + sum(span[2] for span in spans)
    interior = (
        sorted(read)[low_rows: len(read) - high_rows]
        if by_rank
        else [entry for entry in read if lowest < entry[0] < highest]
    )
    holders: "list[dict[int, dict[str, bool]]]" = [{} for _subjects in counted]
    for value, place in interior:
        at = parsing.histogram_bin(value, float(lowest), float(highest))
        for column in range(len(counted)):
            if at not in holders[column]:
                holders[column][at] = {}
            held = holders[column][at]
            if len(held) < floor:
                held[counted[column][place]] = True
    interior = []

    def holds_the_floor(first: int, last: int) -> bool:
        for column in range(len(counted)):
            union: "dict[str, bool]" = {}
            for at in range(first, last + 1):
                for subject in holders[column][at] if at in holders[column] else {}:
                    if len(union) < floor:
                        union[subject] = True
            if len(union) < floor:
                return False
        return True

    if not by_rank:
        whole = (spans[0][0], spans[len(spans) - 1][1], sum(span[2] for span in spans))
        if not holds_the_floor(whole[0], whole[1]):
            return True, None
        joined = [whole]
    else:
        joined = []
        start = -1
        rows_run = 0
        for first, last, rows in spans:
            if start < 0:
                start = first
                rows_run = 0
            rows_run = rows_run + rows
            if holds_the_floor(start, last):
                joined += [(start, last, rows_run)]
                start = -1
        if start >= 0:
            if not joined:
                return True, None
            closing = joined[len(joined) - 1]
            joined = joined[: len(joined) - 1] + [(closing[0], spans[len(spans) - 1][1], closing[2] + rows_run)]
    if joined == spans:
        return False, None
    return False, joined


def _groups_in_people(
    described: taxonomy.ColumnProfile,
    cells: "list[str]",
    subject_cells: "list[list[str]]",
    floor: int,
    enough: "list[bool] | None",
    reading: "_CellReading | None",
) -> "taxonomy.ColumnProfile | None":
    """A column every numeric block of whose description publishes bin groups each held by ``floor`` people or more under every subject column it is counted in; None where a block's interior as a whole is held by fewer (plan P4-D486).

    THE INTERIOR'S BIN GROUPS COUNTED IN PEOPLE FOR EVERY NUMBER COLUMN
    BESIDE A SUBJECT COLUMN (lane HB3-a2; the orchestrator's LANE HB3-a
    RULINGS 4 (3) (i), carry C5 of lane HB2's verify): a tail block's
    histogram closes a group once it holds the floor's ROWS
    (`taxonomy._tail_bins`), and `_counted_in_subjects` counts the values,
    forms, rows and remainder a block publishes, not its groups -- lane
    HB2's rounds counted them (`_groups_few`), but only a column the rounds
    ran on. A top-coded age column of 1,000 people of 20 rows, 15 people
    aged 25 and 10 of them inside the 200-row low tail, published bin group
    0, 100 interior rows of 5 people; a one-decimal column of the same
    values the same. Each group fewer than the floor's people hold is
    joined to its neighbour (`_block_groups_joined`): wider groups, never a
    value, so the twin's interior keeps its shape and every published group
    holds the floor's people.

    EVERY BLOCK THAT PUBLISHES TAILS AND BIN GROUPS (lane HB3-a2's repair 1,
    skeptic 1's item 1; the orchestrator's LANE HB3-a2 RULINGS 7 (1)): the
    column's own block, each wrapper's numbers beside the commonest, the
    numeric half of numbers and labels and each position of joined numbers,
    each read by rank on the cells it was read over
    (`taxonomy.numbers_by_block`; the column's own block of wrapped numbers
    on the commonest wrapper's cells, so the rank is the block's) -- a
    glucose written `NNN.N mg/dL` by 900 people and `NNN.N mmol/L` by 100
    published the minority unit's 30 groups, 11 of them held by 4 to 9
    people, and the column's own block, counted over every cell, lost its
    rank and its 32 groups. Subject columns are counted as
    `_counted_in_subjects` counts them: one of fewer than the floor's values
    only where the column is attached to it and tells its people apart. The
    column unchanged where every group already holds the floor's people.
    Linear in the rows but for one sort of each block's rows. No I/O.
    """
    # ...read only where a block publishes a group: a column of labels or of
    # no numbers is passed over without reading a cell, as it was.
    grouped = False
    details_in = described.details
    for holder in (details_in, details_in["numbers"] if "numbers" in details_in else None):
        if isinstance(holder, dict) and "bin_groups" in holder and holder["bin_groups"]:
            grouped = True
    for key, inner in (("affix_variants", "numbers"), ("parts", "")):
        listed = details_in[key] if key in details_in else None
        for entry in listed if isinstance(listed, list) else []:
            nested = entry[inner] if inner and isinstance(entry, dict) and inner in entry else entry
            if isinstance(nested, dict) and "bin_groups" in nested and nested["bin_groups"]:
                grouped = True
    if not grouped:
        return described
    counted: "list[list[str]]" = []
    for place in range(len(subject_cells)):
        if enough is None or enough[place] or (
            _attached(cells, subject_cells[place]) and _names_its_people(cells, subject_cells[place])
        ):
            counted += [subject_cells[place]]
    if not counted:
        return described
    how = _CellReading() if reading is None else reading
    blocks = taxonomy.numbers_by_block(
        cells, how.comma, frozenset(described.absent_spellings), described.role, described.details,
    )
    details: "dict[str, object] | None" = None
    for path, at, read in blocks:
        block = _block_at(described.details, path, at)
        if block is None:
            continue
        held, joined = _block_groups_joined(block, read, counted, floor)
        if held:
            return None
        if joined is None:
            continue
        if details is None:
            details = {}
            for key in described.details:
                details[key] = described.details[key]
        _groups_written(
            details, path, at, [{"first": first, "last": last, "count": rows} for first, last, rows in joined],
        )
    if details is None:
        return described
    return dataclasses.replace(described, details=details)


def _counted_in_subjects(
    described: taxonomy.ColumnProfile,
    cells: "list[str]",
    subject_cells: "list[list[str]]",
    floor: int,
    enough: "list[bool] | None" = None,
    reading: "_CellReading | None" = None,
    pooled_in_people: bool = False,
    rows_hold: bool = False,
) -> bool:
    """Whether a column publishes a value fewer than `floor` subjects hold.

    PLAN P4-D406. Every value the column's description publishes is read
    back off its block (`_published_in`), and every written form its
    `shape_forms` census names, and each is counted in each subject
    column (`_holding`): one held by one to `floor` - 1 different
    subjects, under any subject column, is one the column may not
    publish -- in a column attached to that subject, or a column of
    dates or times of day, whatever its rows; in any other where `floor`
    rows or more hold it and it stands off the rungs. So are the
    column's present rows as a whole and the remainder of rows that read
    as no published value, wherever `floor` rows or more hold either: a
    column all of whose rows, or whose merged remainder, belong to one
    to `floor` - 1 subjects prints a count of that few people.

    ``enough`` says, per subject column, whether it holds `floor`
    different values (None: every one does). Under one of fewer every
    value is held by fewer subjects than the floor, so only a column
    attached to it, and telling its subjects apart (`_names_its_people`),
    is counted there: the filler code of seven values a question was put
    to blanks no column of measurements, labels or dates beside it, and
    the names and birth dates of seven patients are held.
    Their visit dates, attached to nobody's one value, are counted in
    rows there (plan P4-D406's stated limit, lane PS).

    Such a column is then described as a held record number
    (`taxonomy.as_held_in_people`), as lane HX describes a column whose
    identity question is open, so the twin writes made-up values in the
    column's layouts and the real table still meets its own description.
    A number beside a unit is counted as the same number written bare
    (``reading.affixed``; plan P4-D443).

    ``pooled_in_people`` reads a block whose pool is counted in people (plan
    P4-D453): its remainder is that pool, which names no group and whose
    count is a count in the pool (P4-D363), so it is not asked of the
    remainder; every value the block publishes is asked as ever.

    ``rows_hold``: the rows count as one more subject column, each row its
    own holder (plan P4-D433), which tells no subject apart and is attached
    to none: a column of dates or times one of whose published values one to
    `floor` - 1 rows hold publishes it.

    ONE SUBJECT COLUMN AT A TIME, COUNTED BY CODE (lane SR2a, plan P4-D463,
    repairs 1 and 2): the different sets of keys the cells are counted under
    are numbered as first met, each different cell read once while the memo
    lasts (`_KeyCodes`), and each subject column is counted in one pass, in
    c47a6aee's order: each set's rows and its first `floor` subjects
    (`_few_hold_a_key`). The first column that finds a key few hold ends the
    count, as c47a6aee's did, so no more rows times subject columns are read
    than it read; and a column's subjects are let go before the next column
    is counted, so the subjects held at once are one column's, at most
    `floor` a set of keys (Codex's review of the lane, item 1: counted under
    every column at once, a code column of 181,818 published labels beside
    49 open candidates held about 4 GB of subjects at 2,000,000 rows). A
    key's rows are the sum over the sets that hold it and its subjects the
    first `floor` of their union (`_keys_counted`): what `_holding` counted
    row by row. A subject column of too few values is asked whether the
    column is attached to it before its pass, as before; one that counts in
    people, only where the answer decides.
    """
    # THE NAMES OF THE HELD-BACK LEVELS (lane CODES-2, plan P4-D471) are no
    # value this rule asks of: the owner's answer Z1 = B names exactly the
    # values few rows or people hold, without a count or a row, and only
    # after the person's `no` -- whose pool it is, counted in rows or in
    # people, is what the rule asks of the rest of the block.
    shown = _without_held_back_names(_column_block(described))
    if pooled_in_people:
        # ...and not of a sentence's words: `there are 6 different values`
        # names no value `6`, and every value a sentence of this block could
        # name is a published level, itself read here. Nor of the stand-ins'
        # starts: a function of the published levels alone, which says
        # nothing of any cell, even where it spells one (the orchestrator's
        # LANE PL RULINGS 2 (1)).
        shown = {
            key: shown[key]
            for key in shown
            if key not in _SENTENCE_KEYS and key != "pool_in_people"
        }
    published = _published_in(shown, True)
    plain = _published_in(shown, False)
    forms = _named_forms(shown)
    absent = frozenset(described.absent_spellings)
    dated = described.role in (taxonomy.ROLE_DATETIME, taxonomy.ROLE_CLOCK)
    # WHETHER THE COLUMN IS ATTACHED TO A SUBJECT COLUMN OF TOO FEW VALUES,
    # asked before its pass (plan P4-D406): only one it is attached to, and
    # that tells its people apart, is counted. Under a column that counts in
    # people it is asked only where its answer decides (plan P4-D463): it
    # costs a map of every subject, and a column of dates is held by a key
    # few people hold whatever it answers.
    codes = _KeyCodes(published, forms, absent, reading, [], [], {}, _Codes(bytearray(0), 0), False)
    last = len(subject_cells) - 1
    for place in range(len(subject_cells)):
        people = enough is None or enough[place]
        attached: "bool | None" = None
        if not people:
            attached = _attached(cells, subject_cells[place])
            if not (attached and _names_its_people(cells, subject_cells[place])):
                continue
        if _few_hold_a_key(
            cells, subject_cells[place], floor, codes, place < last, plain, people, attached, dated, pooled_in_people
        ):
            return True
    if rows_hold and dated:
        # EACH ROW ITS OWN HOLDER, counted with no text a row (lane SR2a,
        # plan P4-D463): a key's holders are its rows.
        if not codes.counted:
            _counted_by_code(cells, None, floor, codes, False)
        rows_keyed: "dict[str, int]" = {}
        for code in range(len(codes.met)):
            for key in codes.met[code]:
                rows_keyed[key] = rows_keyed[key] + codes.rows[code] if key in rows_keyed else codes.rows[code]
        for key in rows_keyed:
            if rows_keyed[key] < floor and key not in (_KEY_PRESENT, _KEY_REMAINDER):
                return True
    return False


@dataclasses.dataclass
class _KeyCodes:
    """A column's cells numbered by the set of keys each is counted under (`_counted_in_subjects`, plan P4-D463).

    ``published``, ``forms``, ``absent`` and ``reading`` say what a cell is
    counted as (`_cell_keys`). The first pass (`_counted_by_code`) fills the
    rest and sets ``counted``: ``met`` holds the different sets of keys in
    the order first met and ``rows`` each set's rows; ``code_of`` each
    different cell's number while the memo lasts (`_PEOPLE_MEMO_TEXTS`), -1
    for a cell counted under no key; ``past`` the number, plus one, of each
    row whose cell the memo could not hold, one to three bytes a row
    (`_Codes`), kept only where a later pass reads it.
    """

    published: _Published
    forms: "dict[str, int]"
    absent: "frozenset[str]"
    reading: "_CellReading | None"
    met: "list[tuple[str, ...]]"
    rows: "list[int]"
    code_of: "dict[str, int]"
    past: "_Codes"
    counted: bool


def _counted_by_code(
    cells: "list[str]",
    subjects: "list[str] | None",
    floor: int,
    codes: _KeyCodes,
    keep: bool,
) -> "list[dict[str, bool]]":
    """One pass over a column's cells under one subject column: each set of keys' first `floor` subjects (P4-D463).

    The first pass numbers the different sets of keys as first met
    (``codes``), reading each different cell once while the memo lasts
    (`_PEOPLE_MEMO_TEXTS`, as `_cell_keys`' own) and each cell past it
    again, as ever, and counts each set's rows; where ``keep`` (another
    subject column may follow), it keeps the number of each row past the
    memo (`_code_kept`), so a later pass reads no cell again but each row's
    number back. A cell counted under no key, blank or absent, is passed
    over and its subject not read, as `_holding` passed it. Returns, under
    ``subjects`` (None: the rows alone, and nothing), each set's first
    `floor` subjects in the order met; nothing is kept a row.
    """
    first = not codes.counted
    met = codes.met
    rows = codes.rows
    code_of = codes.code_of
    held: "list[dict[str, bool]]" = []
    if subjects is not None:
        held = [{} for _code in met]
    coded: "dict[tuple[str, ...], int]" = {}
    interned: "dict[tuple[str, ...], tuple[str, ...]]" = {}
    total = len(cells)
    for place in range(total):
        cell = cells[place]
        if cell in code_of:
            code = code_of[cell]
        elif not first:
            code = _code_at(codes.past, place) - 1
        else:
            keys = _cell_keys(cell, codes.published, codes.forms, codes.absent, None, interned, codes.reading)
            if not keys:
                code = -1
            elif keys in coded:
                code = coded[keys]
            else:
                code = len(met)
                coded[keys] = code
                met += [keys]
                rows += [0]
                if subjects is not None:
                    held += [{}]
            if len(code_of) < _PEOPLE_MEMO_TEXTS:
                code_of[cell] = code
            elif keep:
                _code_kept(codes.past, place, code + 1, total)
        if code < 0:
            continue
        if first:
            rows[code] = rows[code] + 1
        if subjects is not None:
            holders = held[code]
            if len(holders) < floor:
                subject = subjects[place]
                if subject not in holders:
                    holders[subject] = True
    codes.counted = True
    return held


def _few_hold_a_key(
    cells: "list[str]",
    subjects: "list[str]",
    floor: int,
    codes: _KeyCodes,
    keep: bool,
    plain: _Published,
    people: bool,
    attached: "bool | None",
    dated: bool,
    pooled_in_people: bool,
) -> bool:
    """Whether one subject column finds a key one to `floor` - 1 of its subjects hold that is a group (P4-D463).

    Its subjects are counted in one pass (`_counted_by_code`) and let go as
    this returns, before another column is counted. The rules are
    `_counted_in_subjects`'s (plan P4-D406), key by key, in the order the
    keys are first met.
    """
    held = _counted_by_code(cells, subjects, floor, codes, keep)
    rows, holders = _keys_counted(codes, held, floor)
    for key in rows:
        if len(holders[key]) >= floor:
            continue
        if key in (_KEY_PRESENT, _KEY_REMAINDER):
            if (
                people
                and rows[key] >= floor
                and not (pooled_in_people and key == _KEY_REMAINDER)
            ):
                return True
            continue
        if not people or dated:
            return True
        if attached is None:
            attached = _attached(cells, subjects)
        if attached:
            return True
        if rows[key] >= floor and _plainly(key, plain):
            return True
    return False


def _keys_counted(
    codes: _KeyCodes, held: "list[dict[str, bool]]", floor: int
) -> "tuple[dict[str, int], dict[str, dict[str, bool]]]":
    """Each key's rows, and up to `floor` of the different subjects of one column that hold it (P4-D463).

    A key's rows are the sum over the sets of keys that hold it; its
    subjects are the first `floor` of the union of theirs, which is
    `floor` wherever a set's own reached it, and every subject otherwise:
    what `_holding` counts row by row. A key one set holds is given that
    set's own subjects; one that several hold, a union of its own.
    """
    rows: "dict[str, int]" = {}
    holders: "dict[str, dict[str, bool]]" = {}
    unions: "dict[str, bool]" = {}
    for code in range(len(codes.met)):
        own = held[code]
        for key in codes.met[code]:
            if key not in rows:
                rows[key] = codes.rows[code]
                holders[key] = own
                continue
            rows[key] = rows[key] + codes.rows[code]
            into = holders[key]
            if len(into) >= floor:
                continue
            if key not in unions:
                union: "dict[str, bool]" = {}
                for subject in into:
                    union[subject] = True
                holders[key] = union
                unions[key] = True
                into = union
            for subject in own:
                if len(into) >= floor:
                    break
                if subject not in into:
                    into[subject] = True
    return rows, holders


def _reads_as_text(cells: "list[str]", absent: "frozenset[str]") -> bool:
    """Whether a present cell of a column reads as no number: its column is text (P4-D453, RULINGS 1 (1))."""
    for cell in cells:
        if (
            parsing.folded(cell)
            and cell not in absent
            and parsing.classify_number(cell) == parsing.NOT_A_NUMBER
        ):
            return True
    return False


# The readings whose levels a pool counted in people may hold (plan P4-D453).
# A constant column has one level, so its only pool is a column too few people
# fill (`_present_too_few`); numbers beside labels are a measurement's reading,
# lane PS3's sibling.
_LEVELS_POOLED_ROLES = (
    taxonomy.ROLE_BINARY,
    taxonomy.ROLE_CATEGORICAL,
    taxonomy.ROLE_LONG_TAIL,
)


def _present_too_few(
    cells: "list[str]",
    absent: "frozenset[str]",
    subject_cells: "list[list[str]]",
    enough: "list[bool]",
    floor: int,
    n_rows: int,
) -> bool:
    """Whether a column's present cells are held by one to `floor` - 1 people (plan P4-D453).

    Counted in people under every subject column that repeats and holds the
    floor's number of different values: fewer than that under any of them is
    a group of that few. Where none does, in rows, each row its own holder,
    on a table the command describes (`parsing.TABLE_ROW_FLOOR`), the library
    keeping its bytes below it as the count of dates in rows does (P4-D433).

    Guarantees: a fixed function of the six, linear in the cells. Raises
    nothing. No I/O.

    ONE PASS THAT STOPS AT THE FLOOR (lane SR2a, plan P4-D463, repair 1):
    the present cells' first `floor` different subjects are met under each
    subject column that counts, as `_holding` keeps them, and the pass ends
    once every such column has met `floor` of them, or, where none counts,
    once `floor` cells are present: the answer is then known. Nothing is
    kept a row.
    """
    counting: "list[list[str]]" = []
    for place in range(len(subject_cells)):
        if enough[place]:
            counting += [subject_cells[place]]
    met: "list[dict[str, bool]]" = [{} for _subject in counting]
    short = len(counting)
    rows = 0
    for place in range(len(cells)):
        cell = cells[place]
        if not parsing.folded(cell) or cell in absent:
            continue
        rows = rows + 1
        if not counting:
            if rows >= floor:
                return False
            continue
        for column in range(len(counting)):
            holders = met[column]
            if len(holders) < floor:
                subject = counting[column][place]
                if subject not in holders:
                    holders[subject] = True
                    if len(holders) >= floor:
                        short = short - 1
        if short == 0:
            return False
    if rows == 0:
        return False
    if counting:
        for holders in met:
            if len(holders) < floor:
                return True
        return False
    return rows < floor and n_rows >= parsing.TABLE_ROW_FLOOR


def _commonest_written(entry: "dict[str, object]") -> str:
    """The spelling a published level's cells most wear, its label where it names none."""
    best = f"{entry['label']}"
    most = 0
    variants = entry["variants"] if "variants" in entry else None
    if isinstance(variants, dict):
        for spelling in sorted(variants):
            count = variants[spelling]
            if isinstance(count, int) and count > most:
                best = f"{spelling}"
                most = count
    return best


def _levels_written(described: taxonomy.ColumnProfile) -> "dict[str, list[str]]":
    """Each published level's spellings, as its `variants` name them, its label where they name none.

    What `taxonomy.levels_read_as_codes` reads the case of a yes-no letter
    off (the orchestrator's LANE I4m RULINGS 27 (1)). Raises nothing. No I/O.
    """
    written: "dict[str, list[str]]" = {}
    levels = described.details["levels"] if "levels" in described.details else ()
    if isinstance(levels, (list, tuple)):
        for entry in levels:
            if isinstance(entry, dict):
                label = f"{entry['label']}"
                variants = entry["variants"] if "variants" in entry else None
                written[label] = [label]
                if isinstance(variants, dict) and variants:
                    written[label] = [f"{spelling}" for spelling in sorted(variants)]
    return written


def _levels_counted(described: taxonomy.ColumnProfile) -> int:
    """How many different labels a label block counts, published and held back."""
    levels = described.details["levels"] if "levels" in described.details else ()
    held = (
        described.details["suppressed_levels"]
        if "suppressed_levels" in described.details
        else 0
    )
    named = len(levels) if isinstance(levels, (list, tuple)) else 0
    return named + (held if isinstance(held, int) else 0)


def _levels_many_people_hold(
    described: taxonomy.ColumnProfile,
    cells: "list[str]",
    subject_cells: "list[list[str]]",
    enough: "list[bool]",
    floor: int,
) -> "tuple[str, ...]":
    """The published levels the floor's number of people hold, under every subject counted (P4-D453).

    A subject of fewer than the floor's different values counts only a column
    attached to it that tells its people apart, as `_counted_in_subjects`
    reads it.

    Guarantees: a fixed function of the five, one pass of the cells a subject.
    Raises nothing. No I/O.
    """
    labels: "dict[str, bool]" = {}
    levels = described.details["levels"] if "levels" in described.details else ()
    if isinstance(levels, (list, tuple)):
        for entry in levels:
            if isinstance(entry, dict):
                labels[f"{entry['label']}"] = True
    interned: "dict[str, tuple[str, ...]]" = {}
    keyed: "list[tuple[str, ...]]" = []
    for cell in cells:
        if cell not in interned:
            label = parsing.folded(cell)
            interned[cell] = (label,) if label in labels else ()
        keyed += [interned[cell]]
    for place, subject in enumerate(subject_cells):
        if not enough[place] and not (
            _attached(cells, subject) and _names_its_people(cells, subject)
        ):
            continue
        counted = _holding(keyed, subject, floor)
        for label in counted:
            if len(counted[label].holders) < floor and label in labels:
                del labels[label]
    return tuple(sorted(labels))


def _pool_owes(
    candidate: taxonomy.ColumnProfile, decimal_comma: bool
) -> "dict[str, int]":
    """The cells of each numeric class a pool holds, from the block's published facts alone (P4-D453).

    What the column's published `n_numeric`, `n_out_of_range` and
    `n_contradictory` leave once the published levels' counts have paid, each
    level reading as its commonest spelling reads: the generator's own
    debt (`generation._classes_owed`), so the profiler and the generator
    split the pool alike, and no unpublished cell is read.
    """
    paid = {
        parsing.NUMBER: 0,
        parsing.NUMBER_OUT_OF_RANGE: 0,
        parsing.NUMBER_CONTRADICTORY: 0,
    }
    levels = candidate.details["levels"] if "levels" in candidate.details else ()
    if isinstance(levels, (list, tuple)):
        for entry in levels:
            if not isinstance(entry, dict) or not isinstance(entry["count"], int):
                continue
            found = parsing.number_as_declared(
                _commonest_written(entry), decimal_comma
            )[0]
            if found in paid:
                paid[found] = paid[found] + entry["count"]
    return {
        parsing.NUMBER: candidate.n_numeric - paid[parsing.NUMBER],
        parsing.NUMBER_OUT_OF_RANGE: candidate.n_out_of_range
        - paid[parsing.NUMBER_OUT_OF_RANGE],
        parsing.NUMBER_CONTRADICTORY: candidate.n_contradictory
        - paid[parsing.NUMBER_CONTRADICTORY],
    }


def _a_fraction_among_whole_numbers(
    cells: "list[str]",
    published: "list[str]",
    absent: "frozenset[str]",
    decimal_comma: bool = False,
) -> bool:
    """Whether a pool holds a number written with a decimal mark where every published number is whole (P4-D453).

    Such a column is held whole, as P4-D406 holds it (skeptic 1's item 5 of
    lane PL, its first remedy): the real reads as decimals (`2.5`, `8.0`)
    and its stand-ins could keep that dtype only by saying that the few
    people's values are written with a point. Whole and not are read in the
    column's declared grammar (`parsing.number_as_declared`; lane PL's
    repair 2, Codex's item 3): a sign before figures is whole (`+1`), and
    under a declared decimal comma `2,5` is two and a half.
    """
    whole = False
    for label in published:
        found, _value, integral = parsing.number_as_declared(label, decimal_comma)
        if found == parsing.NUMBER:
            if not integral:
                return False
            whole = True
    if not whole:
        return False
    kept = frozenset(published)
    for cell in cells:
        label = parsing.folded(cell)
        if label and cell not in absent and label not in kept:
            found, _value, integral = parsing.number_as_declared(cell, decimal_comma)
            if found == parsing.NUMBER and not integral:
                return True
    return False


def _described_with_pool(
    candidate: taxonomy.ColumnProfile,
    cells: "list[str]",
    subject_cells: "list[list[str]]",
    enough: "list[bool]",
    settings: taxonomy.Settings,
    reading: "_CellReading | None",
    decimal_comma: bool = False,
    after_no: bool = False,
) -> "taxonomy.ColumnProfile | None":
    """A column's block with its pool counted in people, or None where it cannot be (P4-D453).

    None where the column's reading changed, where the pool holds a cell no
    stand-in can pay (a number out of range or contradictory, or a fraction
    beside whole numbers), where no start fits (one wider than
    `taxonomy.STAND_IN_FIGURES_AT_MOST` figures fits nowhere: lane PL's
    repair 2, Codex's item 2), or where the block so
    written still publishes a value fewer people than the floor hold (a
    word of a sentence, a form). The column's hold answers each of them.
    The stand-ins' starts read the block's published facts alone
    (`taxonomy.pool_stand_in_starts`; the orchestrator's LANE PL RULINGS 2
    (1)), its published `figure_openings` among them, so no start holds a
    run of figures they keep back; and NONE WHERE A STAND-IN WOULD BE A
    PERSON'S KEY (the orchestrator's LANE I4m RULINGS 21 (3), Codex's review
    of batch 4o, item 3): a spelling the walks write that merges with a key
    of a subject column (``subject_cells``, merged as `subject_keys` merges
    them) leaves the column held, so the start stays a function of published
    facts and no key is printed or written (`8888`, person 0's key and one
    of the column's own rare values, was published as `number_from` and
    written into 20 twin cells at 20,000 rows).

    AFTER THE PERSON'S `no` (``after_no``; lane HB2, plan P4-D477, the
    orchestrator's LANE I4m RULINGS 30 (1)): P4-D442's stand-in rule
    applies to the pool as to a label column's held-back stand-ins. Its
    block names the `figure_openings` of the widths its held-back rows
    hold (`taxonomy.label_figure_openings`) where the reading as whole-number
    codes named none, and its number class's start is at least four
    figures wide (`taxonomy.pool_stand_in_starts`), so a start the openings
    keep back leaves the column held, as the public line held it: `8888`
    beside the key `8889` and `88` beside levels `1` to `5`, each the
    column's one rare value, were the constant starts and were written on
    that person's 20 rows.
    """
    if candidate.role not in _LEVELS_POOLED_ROLES:
        return None
    published: "list[str]" = []
    written: "list[str]" = []
    levels = candidate.details["levels"] if "levels" in candidate.details else ()
    if isinstance(levels, (list, tuple)):
        for entry in levels:
            if isinstance(entry, dict):
                published += [f"{entry['label']}"]
                written += [_commonest_written(entry)]
    absent = frozenset(candidate.absent_spellings)
    wanted = candidate.details["suppressed_levels"]
    rows = candidate.details["suppressed_rows"]
    if not isinstance(wanted, int) or not isinstance(rows, int):
        return None
    # ...NOTHING HELD BACK, the column was held for a sentence's word alone,
    # and is described as it reads.
    pooled = candidate
    if wanted:
        owed = _pool_owes(candidate, decimal_comma)
        if (
            owed[parsing.NUMBER_OUT_OF_RANGE] > 0
            or owed[parsing.NUMBER_CONTRADICTORY] > 0
            or _a_fraction_among_whole_numbers(
                cells, published, absent, decimal_comma
            )
        ):
            return None
        classes = parsing.pool_levels_split(wanted, rows, owed[parsing.NUMBER])
        if after_no and "figure_openings" not in candidate.details:
            census = candidate.details["shape_forms"] if "shape_forms" in candidate.details else None
            labels: "list[object]" = []
            for label in published:
                labels += [label]
            openings = taxonomy.label_figure_openings(
                [cell for cell in cells if parsing.folded(cell) and cell not in absent],
                labels,
                settings.small_cell_floor,
                census if isinstance(census, dict) else None,
            )
            if openings:
                opened: "dict[str, object]" = {}
                for key in candidate.details:
                    opened[key] = candidate.details[key]
                opened["figure_openings"] = openings
                candidate = dataclasses.replace(candidate, details=opened)
        starts = taxonomy.pool_stand_in_starts(
            published,
            written,
            classes,
            settings,
            absent,
            decimal_comma,
            taxonomy.figure_openings_read(candidate.details),
            parsing.FIGURE_RUN_KEY_WIDTH if after_no else 0,
        )
        if starts is None or _a_stand_in_is_a_key(
            starts, classes, published, subject_cells
        ):
            return None
        pooled = taxonomy.with_pool_in_people(candidate, starts)
    if _counted_in_subjects(
        pooled,
        cells,
        subject_cells,
        settings.small_cell_floor,
        enough,
        reading,
        True,
    ):
        return None
    return pooled


def _a_stand_in_is_a_key(
    starts: "dict[str, str]",
    classes: "tuple[int, int]",
    published: "list[str]",
    subject_cells: "list[list[str]]",
) -> bool:
    """Whether a spelling a pool's walks write merges with a person's key (LANE I4m RULINGS 21 (3)).

    The walks are the generator's own (`parsing.stand_ins_from`, from each
    class's start, as many spellings as the class takes, past the published
    levels); each is read in its merged form (`parsing.merged_key`, the form
    `subject_keys` gave ``subject_cells``), so `08888` and `8888` are one key.
    A fixed function of the four. Raises nothing. No I/O.
    """
    walked: "list[str]" = []
    folded_published = frozenset(published)
    for start, wanted in ((starts["number_from"], classes[0]), (starts["word_from"], classes[1])):
        if start and wanted:
            walked += parsing.stand_ins_from(start, wanted, folded_published)
    if not walked:
        return False
    merged: "dict[str, bool]" = {}
    for spelling in walked:
        merged[parsing.merged_key(spelling)] = True
    for keys in subject_cells:
        for key in keys:
            # (`` is every unknown person's key, no spelling's.)
            if key and key in merged:
                return True
    return False


def _read_in_its_order(
    settings: taxonomy.Settings, pinned: "grains.Reading | None"
) -> taxonomy.Settings:
    """The settings a column's cells written at a grain are read under (plan P4-D433).

    Every bucket a grain writes starts on the first of its month, so a
    day-first date written at the month (`01/03/2022`) reads either way and
    the tie goes to month-first: the description would publish a member
    its own record does not read, and the loader refuses it. A column
    whose reading writes the day first is read with the tie given to the
    day (`settings.day_first`), and one whose reading writes the month
    first with the tie given to the month; any other is read as before.
    """
    if pinned is None or pinned.kind not in (grains.DATE, grains.STAMP):
        return settings
    # IN BOTH DIRECTIONS (repair round 1, Codex's item 4): a column whose
    # days above twelve settled it month-first reads month-first at its
    # grain too, whatever the run's own preference.
    if not settings.day_first and _day_before_month(pinned.member):
        return dataclasses.replace(settings, day_first=True)
    if settings.day_first and _month_before_day(pinned.member):
        return dataclasses.replace(settings, day_first=False)
    return settings


def _day_before_month(member: str) -> bool:
    """Whether a date member writes the day's figures before the month's."""
    if not isinstance(member, str):
        raise TypeError("a date member is text")
    if "day-first" in member:
        return True
    if member[0:7] != parsing.LAYOUT_PREFIX:
        return False
    day = member.find("{DD}")
    month = member.find("{MM}")
    return 0 <= day < month


def _month_before_day(member: str) -> bool:
    """Whether a date member writes the month's figures before the day's."""
    if not isinstance(member, str):
        raise TypeError("a date member is text")
    if "month-first" in member:
        return True
    if member[0:7] != parsing.LAYOUT_PREFIX:
        return False
    day = member.find("{DD}")
    month = member.find("{MM}")
    return 0 <= month < day


def _reads_its_member(column: taxonomy.ColumnProfile, reading: grains.Reading) -> bool:
    """Whether a column described at a grain publishes the member its record reads (TG1).

    The loader refuses a block whose `format` is another member than its
    record's reading; such a rung does not serve. A clock or counted
    reading, or a block of one or two values, publishes no member to
    compare.
    """
    if reading.kind not in (grains.DATE, grains.STAMP):
        return True
    shown = column.details["format"] if "format" in column.details else None
    return not isinstance(shown, str) or shown == reading.member


def _date_parts(text: str) -> "tuple[str, ...]":
    """The calendar parts a canonical date text names, finest first: its day, its month, its quarter.

    `2023-01-05 18:07:00` and `2023-01-05` give `2023-01-05`, `2023-01`
    and `2023-q1`; `2023-01` its month and quarter; `2023-q1` its quarter;
    any other text nothing. Folded text, as `_published_in` keeps words.
    """
    if len(text) < 7 or text[4:5] != "-" or not _all_figures(text[:4]):
        return ()
    if text[5:6] in ("q", "Q") and text[6:7] in ("1", "2", "3", "4"):
        return (f"{text[:4]}-q{text[6]}",)
    if not _all_figures(text[5:7]) or not "01" <= text[5:7] <= "12":
        return ()
    quarter = f"{text[:4]}-q{(int(text[5:7]) - 1) // 3 + 1}"
    if len(text) >= 10 and text[7:8] == "-" and _all_figures(text[8:10]):
        return (text[:10], text[:7], quarter)
    return (text[:7], quarter)


def _all_figures(part: str) -> bool:
    """Whether a piece of text is one or more of the figures 0 to 9 and nothing else."""
    if not part:
        return False
    for character in part:
        if not "0" <= character <= "9":
            return False
    return True


def _dates_few_in_rows(
    described: taxonomy.ColumnProfile,
    cells: "list[str]",
    floor: int,
    reading: "_CellReading | None" = None,
) -> bool:
    """Whether a date the column publishes names a day one to `floor` - 1 rows hold (plan P4-D433).

    THE COUNT IN ROWS, where no subject column counts the column in
    people. Every word the column's block publishes that names a date --
    a percentile, a tail's boundary or value, a mode, a heavy date, a
    census entry -- is read as the calendar part it names (`_date_parts`:
    its day; a month or a quarter where it names only that), and each
    present cell, read by the column's own reading (its format, or the
    declared count of days), counts once under its day, its month and its
    quarter. A published part one to `floor` - 1 rows fall on is a date
    that few rows hold: the column is then walked down its ladder, each
    row its own holder (`_grain_walk`). A part no row falls on names no
    row. A written form, a remainder and the present rows are counts the
    row floor already holds.
    ON THE CLOCK THE BLOCK PUBLISHES (repair round 1, Codex's item 1): a
    column whose offsets differ is published on the shared clock
    (`datetimes_read_at` `utc`), so each cell counts under the day of its
    instant at UTC (`parsing.utc_moment`), not of its local text.
    COUNTED DATES BY THEIR OWN CALENDAR DAY (Codex's item 2): a count's
    true day, the instant floored to its midnight and never rounded
    forward, and beside it the day of each text its reading writes at the
    day, the minute and the second (`_counted_days`), each a tally of its
    own: a published part one to `floor` - 1 rows fall on in any of them
    is few, so neither an afternoon rounded to the next day nor a moment
    a second before midnight hides its day.
    """
    shown = _column_block(described)
    published = _published_in(shown, True)
    wanted: "dict[str, bool]" = {}
    for word in published.words:
        parts = _date_parts(word)
        if parts:
            wanted[parts[0]] = True
    if not wanted:
        return False
    how = _CellReading() if reading is None else reading
    written = shown["format"] if "format" in shown else ""
    at_utc = (
        "datetimes_read_at" in shown
        and shown["datetimes_read_at"] == taxonomy.READ_AT_UTC
    )
    absent = frozenset(described.absent_spellings)
    rows: "dict[tuple[int, str], int]" = {}
    memo: "dict[str, tuple[tuple[int, str], ...]]" = {}
    for cell in cells:
        if cell in memo:
            keyed = memo[cell]
        else:
            texts: "list[str]" = []
            if parsing.folded(cell) and cell not in absent:
                if how.member:
                    texts = [_counted_true_day(cell, how)] + _counted_days(cell, how)
                elif isinstance(written, str) and written:
                    read = parsing.parse_datetime(cell, written)
                    if read is not None:
                        moved = (
                            parsing.utc_moment(read[0], read[1])
                            if at_utc and read[1]
                            else None
                        )
                        texts = [parsing.folded(read[0] if moved is None else moved)]
            found: "list[tuple[int, str]]" = []
            for tally in range(len(texts)):
                for part in _date_parts(texts[tally]):
                    if part in wanted:
                        found += [(tally, part)]
            keyed = tuple(found)
            if len(memo) < 65536:
                memo[cell] = keyed
        for key in keyed:
            rows[key] = rows[key] + 1 if key in rows else 1
    for key in rows:
        if rows[key] < floor:
            return True
    return False


def _counted_true_day(cell: str, reading: _CellReading) -> str:
    """The calendar day a counted cell's instant falls on, floored, never rounded (plan P4-D433).

    The count read exactly, to the nanosecond, and the instant floored to
    its own midnight: `946731600` seconds since 1970 (13:00 on 1 January
    2000) is `2000-01-01`, where the day's own rendering rounds it to the
    2nd; a millisecond before midnight stays on its day. "" where the
    cell names no date.
    """
    mark = date_counts.COMMA if reading.comma else date_counts.POINT
    written = date_counts.counted(reading.member, cell, mark)
    if written is None:
        return ""
    numerator, denominator = date_counts.exact_value(written)
    moment = date_counts.moment_of(
        reading.member, numerator, denominator, date_counts.NANOSECOND
    )
    if moment is None:
        return ""
    year, month, day = parsing.civil_from_days(moment // date_counts.DAY)
    return f"{year:04d}-{month:02d}-{day:02d}"


# THE ROLES A COLUMN DESCRIBED AT A GRAIN MAY TAKE (plan P4-D417): its own,
# or, where the grain leaves one or two different values, the constant and
# binary roles every column of one or two values takes first.
_GRAIN_ROLES = (
    taxonomy.ROLE_DATETIME,
    taxonomy.ROLE_CLOCK,
    "constant",
    "binary",
)


def _time_reading(
    described: taxonomy.ColumnProfile,
    settings: taxonomy.Settings,
    name: str,
    commas: "list[str]",
) -> "grains.Reading | None":
    """How a column of dates, stamps, clock times or counted dates reads its cells, or None."""
    details = described.details
    if described.role == taxonomy.ROLE_CLOCK:
        form = details["clock_form"] if "clock_form" in details else None
        if isinstance(form, str) and form in parsing.CLOCK_FORMS:
            return grains.Reading(grains.CLOCK, form)
        return None
    if described.role != taxonomy.ROLE_DATETIME:
        return None
    member = taxonomy.counted_member(taxonomy.counted_for_the_column(settings, name))
    if member:
        return grains.Reading(
            grains.COUNTED,
            member,
            date_counts.COMMA if name in commas else date_counts.POINT,
        )
    shown = details["format"] if "format" in details else None
    if not isinstance(shown, str):
        return None
    return grains.Reading(grains.STAMP, shown)


@dataclasses.dataclass(frozen=True)
class _Walked:
    """What `_grain_walk` found of one column: its record, and what the step back reads.

    ``grain`` is the record at the rung the walk reached (or `held`, where
    the top rung has no span or a subject column of few people tells its
    people apart); ``read`` holds one byte a row, 1 where the row's cell
    reads as a moment (lane SR2a, plan P4-D463: a byte a row, where a list
    held each row's moment); ``thin`` names, for every rung, whether some
    bucket inside that rung's span holds one to `floor` - 1 people under
    some subject column; ``unread_thin`` whether the cells that read as no
    moment, or a written shape or offset of those that do, are held so.
    """

    grain: grains.Grain
    read: bytearray
    thin: "dict[str, bool]"
    unread_thin: bool
    padded: bool


# The different texts each memo of the count in people holds at most
# (`_cell_keys`, the walk's `_moments_keyed` and its step back `_cells_at`):
# a fixed few megabytes at 2,000,000 rows.
_PEOPLE_MEMO_TEXTS = 65536


@dataclasses.dataclass
class _WalkPass:
    """What `_grain_walk`'s one pass over a column keeps beside its moments in order (plan P4-D463).

    ``finest`` is the finest rung a cell writes; ``unread`` holds, for each
    subject column the walk counts in people, the holders of every written
    shape and offset key, at most `floor` of each (`_holding`'s count),
    and ``rows`` the rows of each where each row is its own holder;
    ``offsets`` each row's offset code where the block prints the shared
    clock (no byte else), ``named`` the code of each offset key, `""` the
    code 0 of a cell written with none.
    """

    finest: str
    unread: "list[dict[str, dict[str, bool]]]"
    rows: "dict[str, int]"
    offsets: "_Codes"
    named: "dict[str, int]"


def _grain_walk(
    cells: "list[str]",
    present: int,
    time_reading: grains.Reading,
    subject_cells: "list[list[str]]",
    enough: "list[bool]",
    floor: int,
    absent: "frozenset[str]" = frozenset(),
    at_utc: bool = False,
    rows_hold: bool = False,
) -> _Walked:
    """The walk of a column of dates or times down its ladder (plan P4-D417).

    Each present cell is read as its moment; the column's finest rung is
    the finest any cell writes; the walk reads ``present``, the block's
    `n_present`, published on every column, and the people the subject
    columns name, the description's population. At every rung of its
    ladder the ENDS are the first and the last bucket held by `floor`
    different subjects or more under every subject column that counts in
    people (`_holding`'s count), and `grains.ladder_walk` chooses
    the rung the walk reaches from the spans and the estimate. A rung is
    THIN where a bucket strictly inside its span holds one to `floor` - 1
    people under some subject column (the description there would name a
    bucket whose count one to ten people hold, by subtraction where it is
    not printed: the skeptic's item 1), and the cells that read as no
    moment (present, not an absent spelling) are counted as one value,
    each written shape apart, beside every written shape and offset of
    the cells that read (the skeptic's items 1 and 2: `n_unparsed`,
    `resolution_mix` and every census of how a date is written count
    unions of them, at every rung alike). A subject column of fewer than
    `floor` values counts the column only where it is attached to it and
    tells its people apart (plan P4-D406), and then no bucket can reach
    the floor: the column is held.
    ON THE CLOCK THE BLOCK PUBLISHES (``at_utc``, plan P4-D433, repair
    round 2): a column whose offsets differ prints each bucket start a
    cell is written at as its instant at UTC, one text for each bucket
    and offset; the walk counts the people of each bucket and offset
    apart, the texts the description would print, never the local bucket
    whole.
    EACH ROW ITS OWN HOLDER (``rows_hold``, plan P4-D433): the rows count as
    one more subject column that counts in people, of as many subjects as
    rows, each key held by its rows.
    NOTHING KEPT A ROW (lane SR2a, plan P4-D463): each cell is read once,
    whether it reads as a moment kept as one byte a row, and each moment
    as ONE whole number, its second shifted past the row's place, sorted
    once (`_moments_keyed`). Every rung is a second or coarser, so the
    second decides a moment's bucket at every rung, and a rung's buckets
    are runs of that order: each rung is counted in one walk of it, each
    bucket let go before the next (`_rung_counted`), where a key, a start,
    a holder list and a count were kept for every bucket of every rung
    (about 460 bytes a row at 500,000 rows of a stamp to the second).
    """
    kind_reading = time_reading
    held = False
    for place in range(len(subject_cells)):
        if not enough[place] and _attached(cells, subject_cells[place]) and (
            _names_its_people(cells, subject_cells[place])
        ):
            held = True
            break
    counted: "list[list[str]]" = []
    for place in range(len(subject_cells)):
        if enough[place] and not held:
            counted += [subject_cells[place]]
    rows = rows_hold and not held
    # THE PEOPLE THE SUBJECT COLUMNS NAME, the fewest under several: the
    # population the description counts, which the walk reads beside the
    # rows (`grains.estimate`); counted before the moments are, so the two
    # are never held at once.
    people = 0
    for place in range(len(subject_cells)):
        if held or not enough[place]:
            continue
        named: "dict[str, bool]" = {}
        for key in subject_cells[place]:
            named[key] = True
        if people == 0 or len(named) < people:
            people = len(named)
        named = {}
    if rows and (people == 0 or len(cells) < people):
        people = len(cells)
    marked = (
        at_utc
        and (bool(counted) or rows)
        and time_reading.kind in (grains.DATE, grains.STAMP)
    )
    walk = _WalkPass(
        grains.YEAR,
        [{} for _subject in counted],
        {},
        _Codes(bytearray(len(cells) if marked else 0), 1 if marked else 0),
        {"": 0},
    )
    read = bytearray(len(cells))
    # Each row's place in the low bits of its moment's whole number.
    shift = 1
    while 1 << shift <= len(cells):
        shift = shift + 1
    keyed = _moments_keyed(
        cells, time_reading, absent, read, walk, counted, rows, floor, shift
    )
    ordered: "list[int]" = []
    if counted or rows:
        ordered = sorted(keyed)
    else:
        for _moment in keyed:
            continue
    finest = walk.finest
    if time_reading.kind == grains.CLOCK and grains.RANK[finest] < grains.RANK[grains.MINUTE]:
        finest = grains.MINUTE
    if time_reading.kind == grains.STAMP and grains.RANK[finest] <= grains.RANK[grains.DAY]:
        kind_reading = grains.Reading(grains.DATE, time_reading.member, time_reading.mark)
    if held:
        return _Walked(
            grains.Grain(grains.HELD, kind_reading, present, (), finest, 0),
            read, {}, True, True,
        )
    # THE CELLS THAT READ AS NO MOMENT, AND EVERY WRITTEN FORM OF THOSE THAT
    # DO: counts the description at every rung publishes the same --
    # `n_unparsed`, `resolution_mix`, `datetime_separators`,
    # `date_field_widths`, `utc_offsets` and the other censuses of how a
    # date is written, each a union of written shapes (a figure `9`, a
    # letter `a` or `A`) or of offsets, which a cell keeps at every rung,
    # counted in `_moments_keyed`'s pass.
    unread_thin = False
    for holding in walk.unread:
        for key in holding:
            if len(holding[key]) < floor:
                unread_thin = True
    for key in walk.rows:
        if walk.rows[key] < floor:
            unread_thin = True
    walk.unread = []
    walk.rows = {}
    ends: "dict[str, tuple[int, int] | None]" = {}
    thin: "dict[str, bool]" = {}
    for rung in grains.ladder(kind_reading.kind, finest):
        ends[rung], thin[rung] = _rung_counted(
            ordered, shift, rung, counted, rows, floor, walk
        )
    ordered = []
    rung, spans = grains.ladder_walk(
        grains.estimate(present, people), floor, finest, kind_reading.kind, ends
    )
    return _Walked(
        grains.Grain(rung, kind_reading, present, spans, finest, people),
        read,
        thin,
        unread_thin,
        grains.column_padded(cells, kind_reading) if rung != grains.HELD else True,
    )


def _moments_keyed(
    cells: "list[str]",
    time_reading: grains.Reading,
    absent: "frozenset[str]",
    read: bytearray,
    walk: _WalkPass,
    counted: "list[list[str]]",
    rows: bool,
    floor: int,
    shift: int,
) -> "typing.Iterator[int]":
    """Each row whose cell reads as a moment, as ONE whole number: its second times `2 ** shift`, plus its row (P4-D463).

    One pass over the cells: the row is marked in ``read``, ``walk`` keeps
    the finest rung any cell writes and, where ``counted`` names subject
    columns or each row is its own holder (``rows``), each written shape's
    and offset's holders under each, or its rows (a cell
    that reads as no moment, present and not an absent spelling, counted
    under `u` and its own shape apart) and, where its offsets are kept,
    each row's offset code. Each different cell is read once while the
    memos last, as the walk read it before.
    """
    memo: "dict[str, int | None]" = {}
    shaped: "dict[str, tuple[str, ...]]" = {}
    interned: "dict[tuple[str, ...], tuple[str, ...]]" = {}
    dated = time_reading.kind in (grains.DATE, grains.STAMP)
    for place in range(len(cells)):
        cell = cells[place]
        if cell in memo:
            moment = memo[cell]
        else:
            # AN ABSENT CELL IS NO MOMENT (repair round 2, Codex's item 3): a
            # spelling of no value that reads as a date -- one declared with
            # `--missing-value`, a placeholder day such as `1900-01-01` -- is
            # kept out of the walk, so it is never coarsened into a present
            # cell nor counted into a span.
            moment = None if cell in absent else grains.moment_of(cell, time_reading)
            if moment is not None:
                own = grains.finest_of(cell, time_reading)
                if grains.RANK[own] > grains.RANK[walk.finest]:
                    walk.finest = own
            if len(memo) < _PEOPLE_MEMO_TEXTS:
                memo[cell] = moment
        if counted or rows:
            keys: "tuple[str, ...]" = ()
            if moment is None:
                if parsing.folded(cell) and cell not in absent:
                    keys = ("u", f"u{grains.shape_of(cell)}")
            elif cell in shaped:
                keys = shaped[cell]
            else:
                parsed = (
                    parsing.parse_datetime(cell, time_reading.member) if dated else None
                )
                keys = (
                    (f"s{grains.shape_of(cell)}", f"o{parsed[1]}")
                    if parsed is not None and parsed[1]
                    else (f"s{grains.shape_of(cell)}",)
                )
                if keys in interned:
                    keys = interned[keys]
                else:
                    interned[keys] = keys
                if len(shaped) < _PEOPLE_MEMO_TEXTS:
                    shaped[cell] = keys
            for column in range(len(counted)):
                holding = walk.unread[column]
                subject = counted[column][place]
                for key in keys:
                    if key not in holding:
                        holding[key] = {subject: True}
                    elif len(holding[key]) < floor and subject not in holding[key]:
                        holding[key][subject] = True
            if rows:
                for key in keys:
                    walk.rows[key] = walk.rows[key] + 1 if key in walk.rows else 1
            if walk.offsets.width and moment is not None and len(keys) > 1:
                if keys[1] not in walk.named:
                    walk.named[keys[1]] = len(walk.named)
                _code_kept(walk.offsets, place, walk.named[keys[1]], len(cells))
        if moment is None:
            continue
        read[place] = 1
        yield ((moment // date_counts.SECOND) << shift) + place


@dataclasses.dataclass
class _Codes:
    """A small whole number a row, ``width`` bytes each, least significant first (plan P4-D463).

    Where a list held a reference a row, one to three bytes do; the store
    grows a byte wider wherever a number needs it (`_code_kept`). A width of
    0 keeps none, and every row then reads 0.
    """

    store: bytearray
    width: int


def _code_kept(codes: _Codes, place: int, code: int, rows: int) -> None:
    """Row ``place``'s number in ``codes``, the store a byte wider wherever the number needs it."""
    while code >= 1 << (8 * codes.width):
        wider = bytearray((codes.width + 1) * rows)
        for row in range(rows):
            for at in range(codes.width):
                wider[row * (codes.width + 1) + at] = codes.store[row * codes.width + at]
        codes.store = wider
        codes.width = codes.width + 1
    for at in range(codes.width):
        codes.store[place * codes.width + at] = (code >> (8 * at)) & 255


def _code_at(codes: _Codes, place: int) -> int:
    """Row ``place``'s number in ``codes`` (`_code_kept`), 0 where none is kept."""
    code = 0
    for at in range(codes.width):
        code = code | (codes.store[place * codes.width + at] << (8 * at))
    return code


def _rung_counted(
    ordered: "list[int]",
    shift: int,
    rung: str,
    counted: "list[list[str]]",
    rows: bool,
    floor: int,
    walk: _WalkPass,
) -> "tuple[tuple[int, int] | None, bool]":
    """One rung's ends and whether it is thin, from one walk of the moments in order (plans P4-D417, P4-D463).

    A rung's buckets are runs of ``ordered`` (`_moments_keyed`), each
    counted as the walk passes it and let go before the next. A key is a
    bucket, or a bucket and an offset where the block prints the shared
    clock; it is HELD where every subject column of ``counted`` names
    `floor` different subjects or more among its rows (`_holding`'s
    count), and, where each row is its own holder (``rows``), it has
    `floor` rows or more; a bucket of fewer rows than the floor holds none. The
    ENDS are the starts of the first and the last bucket some key of which
    is held, None where none is; the rung is THIN where a key not held
    lies in a bucket strictly between them, or where no key is held.
    """
    if not counted and not rows:
        return None, True
    mask = (1 << shift) - 1
    first: "int | None" = None
    last = 0
    pending = False
    inside = False
    at = 0
    total = len(ordered)
    while at < total:
        start = grains.start_of((ordered[at] >> shift) * date_counts.SECOND, rung)
        end = grains.after(start, rung) // date_counts.SECOND
        stop = at + 1
        while stop < total and (ordered[stop] >> shift) < end:
            stop = stop + 1
        held = False
        missed = True
        if stop - at >= floor:
            held, missed = _bucket_counted(ordered, at, stop, mask, counted, rows, floor, walk)
        if held:
            if pending:
                inside = True
            if first is None:
                first = start
            last = start
        if missed and first is not None and start > first:
            pending = True
        at = stop
    return (None if first is None else (first, last)), first is None or inside


def _bucket_counted(
    ordered: "list[int]",
    at: int,
    stop: int,
    mask: int,
    counted: "list[list[str]]",
    rows: bool,
    floor: int,
    walk: _WalkPass,
) -> "tuple[bool, bool]":
    """Whether some key of one bucket is held, and whether some key is not (`_rung_counted`, P4-D463).

    Each key's subjects under each subject column are kept up to the floor,
    for this bucket alone.
    """
    keys: "dict[int, list[dict[str, bool]]]" = {}
    held_rows: "dict[int, int]" = {}
    for index in range(at, stop):
        place = ordered[index] & mask
        code = _code_at(walk.offsets, place) if walk.offsets.width else 0
        if code not in keys:
            keys[code] = [{} for _subject in counted]
            held_rows[code] = 0
        held_rows[code] = held_rows[code] + 1
        holders = keys[code]
        for column in range(len(counted)):
            met = holders[column]
            if len(met) < floor:
                subject = counted[column][place]
                if subject not in met:
                    met[subject] = True
    held = False
    missed = False
    for code in keys:
        if all([len(met) >= floor for met in keys[code]]) and (
            not rows or held_rows[code] >= floor
        ):
            held = True
        else:
            missed = True
    return held, missed


def _offset_rule_of(column: taxonomy.ColumnProfile) -> str:
    """The rule a described column's stamps follow (`offset_rule`, lane DST, plan P4-D474), or `""`."""
    details = column.details
    rule = details["offset_rule"] if isinstance(details, dict) and "offset_rule" in details else ""
    return rule if isinstance(rule, str) else ""


def _rule_admitted_at(rule_text: str, span: "tuple[str, int, int]") -> bool:
    """Whether a pooled column's rule stands at its rung (lane DST's repair 2): at the hour or coarser always; at the minute or the second only where no hour the clocks repeat falls inside the span (Codex's item 1)."""
    rung, first, last = span
    rule = offset_rules.parsed_rule(rule_text)
    if rule is None or rung not in (grains.MINUTE, grains.SECOND):
        return True
    low = first // date_counts.SECOND
    high = grains.after(last, rung) // date_counts.SECOND
    for year in range(parsing.civil_from_days(low // 86400)[0] - 1, parsing.civil_from_days(high // 86400)[0] + 2):
        back = offset_rules.changes(rule, year)[1]
        if back + rule.standard < high and back + rule.standard + 3600 > low:
            return False
    return True


def _stamp_reading(column: taxonomy.ColumnProfile) -> "grains.Reading | None":
    """How a described column of stamps reads its cells (its member), or None for any other column."""
    details = column.details
    shown = details["format"] if isinstance(details, dict) and "format" in details else None
    if column.role != taxonomy.ROLE_DATETIME or not isinstance(shown, str):
        return None
    return grains.Reading(grains.STAMP, shown)


def _kept_rule(
    cells: "list[str]", cell_reading: "grains.Reading | None", rule_text: str, absent: "frozenset[str]"
) -> str:
    """``rule_text`` where the cells are a column of it (`grains.wears_the_rule`, over its family's whole calendar), else `""` (lane DST's repair 2)."""
    rule = offset_rules.parsed_rule(rule_text) if rule_text else None
    if rule is None or cell_reading is None:
        return ""
    return rule_text if grains.wears_the_rule(cells, cell_reading, rule, absent) else ""


def _with_offset_rule(column: taxonomy.ColumnProfile, rule_text: str) -> taxonomy.ColumnProfile:
    """The column with ``rule_text`` as its `offset_rule` where its census names exactly the rule's two offsets on the shared clock, and with none elsewhere (lane DST's repair 2).

    The verdict decided on the cells as handed (`build_document`'s
    ``offset_verdict``) is what a column of stamps, or the description of
    its grain, publishes: never a rule read again off cells coarsened at
    their own offsets, and never one beside a census the loader would not
    admit it beside (invariant OR1). A column with no rule and no verdict is
    returned as it is.
    """
    details = column.details
    if not isinstance(details, dict) or column.role != taxonomy.ROLE_DATETIME:
        return column
    rule = offset_rules.parsed_rule(rule_text) if rule_text else None
    census = details["utc_offsets"] if "utc_offsets" in details else None
    if rule is not None and (
        details["datetimes_read_at"] if "datetimes_read_at" in details else ""
    ) == taxonomy.READ_AT_UTC and isinstance(census, dict) and sorted(census) == sorted(
        [offset_rules.offset_text(rule.standard), offset_rules.offset_text(rule.standard + 3600)]
    ):
        return taxonomy.with_offset_rule(column, rule_text)
    if "offset_rule" not in details:
        return column
    return taxonomy.with_offset_rule(column, "")


def _cells_at(
    cells: "list[str]", walked: _Walked, span: "tuple[str, int, int]", rule_text: str = ""
) -> "list[str] | None":
    """Every cell written as the start of its bucket at ``span``'s rung, the tails pooled into its ends.

    A cell that reads as no moment is kept as written; None where a cell
    that reads cannot be written at the rung in its own form.
    ONE TEXT FOR EACH DIFFERENT COARSE CELL, UP TO 65,536 OF THEM (lane
    SR2a, plan P4-D463): the cells at a rung coarser than the column's own
    repeat, and each equal text is the one object the first such cell made,
    where a column whose cells all differ made a new text a row once its
    memo was full (about 85 bytes a row for stamps to the second). THE
    LIMIT (Codex's review of the lane, item 2): the texts shared are the
    first `_PEOPLE_MEMO_TEXTS` different ones met; one first met after them
    is made again at each of its cells, equal in value, as before this
    lane, so a column of more different buckets than that at the rung
    keeps a text a row for the rows past them (2,000,000 stamps over 80,000
    minutes read at the minute: 361,600 rows).
    """
    rung, first, last = span
    reading = walked.grain.reading
    # ...EACH AT THE OFFSET ITS RULE PUTS IN FORCE AT THE BUCKET'S START where
    # the column's stamps follow one (lane DST, plan P4-D474, method G7.4r;
    # `grains.coarse_cell`), unless the starts would then wear one offset.
    rule = grains.cell_rule(rule_text, reading)
    if rule is not None and not grains.keeps_the_rule(cells, reading, rule):
        rule = None
    years: "dict[tuple[str, int, int], tuple[int, int]]" = {}
    coarse: "list[str]" = []
    written: "dict[str, str | None]" = {}
    shared: "dict[str, str]" = {}
    for place in range(len(cells)):
        cell = cells[place]
        if not walked.read[place]:
            coarse += [cell]
            continue
        if cell in written:
            made = written[cell]
        else:
            made = grains.coarse_cell(cell, reading, rung, first, last, walked.padded, rule, years)
            if made is not None:
                if made in shared:
                    made = shared[made]
                elif len(shared) < _PEOPLE_MEMO_TEXTS:
                    shared[made] = made
            if len(written) < _PEOPLE_MEMO_TEXTS:
                written[cell] = made
        if made is None:
            return None
        coarse += [made]
    if rule is not None and not grains.two_offsets(coarse, reading, frozenset()):
        return _cells_at(cells, walked, span)
    return coarse


def _held_dates_grain(
    cells: "list[str]",
    time_reading: grains.Reading,
    present: int,
    absent: "frozenset[str]",
) -> grains.Grain:
    """The record a column of dates lane SH2 holds publishes (plan P4-D434): rung `held`, no span.

    As `_grain_walk` records a column it holds for its subjects: the
    finest detail its cells write, read cell by cell (an absent cell
    none), and a stamp written to the day read as a date; no span, so its
    twin draws its valid dates from the fixed span (`grains.fixed_span`).
    """
    finest = grains.YEAR
    seen: "dict[str, bool]" = {}
    for cell in cells:
        if cell in seen or cell in absent:
            continue
        if len(seen) < 65536:
            seen[cell] = True
        if grains.moment_of(cell, time_reading) is not None:
            own = grains.finest_of(cell, time_reading)
            if grains.RANK[own] > grains.RANK[finest]:
                finest = own
    kind_reading = time_reading
    if time_reading.kind == grains.CLOCK and grains.RANK[finest] < grains.RANK[grains.MINUTE]:
        finest = grains.MINUTE
    if time_reading.kind == grains.STAMP and grains.RANK[finest] <= grains.RANK[grains.DAY]:
        kind_reading = grains.Reading(grains.DATE, time_reading.member, time_reading.mark)
    return grains.Grain(grains.HELD, kind_reading, present, (), finest, 0)


# THE ARMS OF THE SAFE HARBOR QUESTION THAT HOLD A COLUMN OF NUMBERS THAT MAY
# BE DATES (lane ID-ROOM3, plan P4-D488): its years or ZIP codes, dates
# showing an age over 89, ZIP codes read as counted dates.
DATES_HOLD_REASONS = (
    taxonomy.HELD_YEARS,
    taxonomy.HELD_YEARS_BESIDE,
    taxonomy.HELD_DATES,
    taxonomy.HELD_ZIP_DATES,
)


def _held_counts_read(
    described: taxonomy.ColumnProfile,
    cells: "list[str]",
    settings: taxonomy.Settings,
    name: str,
    held_for_dates: bool,
    said_codes: bool = False,
) -> taxonomy.ColumnProfile:
    """A held column of counts with no grain, read as the counted dates it may be (lane ID-ROOM3, plan P4-D488; ruling D3).

    Only a column whose cells judged are counts (`taxonomy.held_count_cores`:
    a stray word holding no figure set aside whatever its share, a numeric
    placeholder and a cell holding a figure the count grammar does not read
    -- one patient's rows written as ISO dates -- up to one present cell in
    three, lane ID-ROOM3's repairs 1 and 2), whose census names counts
    alone beside its words and such strays
    (`taxonomy.held_count_layouts_aside`), and whose counts hold
    six whole figures or more (no ZIP code is as long: a column of five
    figures stays lane SH's question, lane ID-ROOM3-b's item): DECLARED as
    counted dates of a member the G1 floor writes, every count judged read
    in it, it takes that member's counted grain record
    (`_held_dates_grain`), so the one writer of counted dates writes it in
    the room (`taxonomy.with_made_up_years`'s counted arm); a declaration
    DECLINED (NF127: no unit reads its cells keeping their figures)
    publishes the room its counts would take (`taxonomy.with_made_up_counts`),
    so its twin's walk keeps only values off every real day. So does a
    column held by a question about dates (``held_for_dates``: the Safe
    Harbor question's arms about years, ZIP codes and dates, and its reach
    of levels few people hold; the command names them to the description
    it writes in ``counts_held_for_dates``), by an open question offering
    `identifier` (the measurement, code or identifier question, and Q3,
    whose answers offer it too), or in people or in rows -- each ONLY where
    the span-and-density test reads its counts as dates in some counting
    system (`taxonomy.counts_may_be_dates`; LANE ID-ROOM3 RULINGS 5 (1) and
    (2)), and never one the person said holds codes (``said_codes``: the
    person's word, as a column typed `--identifier` is record numbers by
    it, LANE ID-ROOM3 RULINGS 4 (2)). Any other column -- a column typed or
    answered `identifier` among them -- is returned as it came. Linear in
    the cells. Raises nothing. No I/O.
    """
    if described.role != taxonomy.ROLE_IDENTIFIER or "time_grain" in described.details:
        return described
    widest = taxonomy.held_counts_widest(described, cells)
    if widest < taxonomy.HELD_COUNTS_WIDEST_AT_LEAST:
        return described
    member = taxonomy.counted_member(taxonomy.counted_for_the_column(settings, name))
    absent = frozenset(described.absent_spellings)
    # ...a declaration whose cells no unit reads keeping their figures was
    # declined (NF127): its walk is tested, it takes no grain.
    declined = described.detection_evidence.form == taxonomy.EVIDENCE_COUNTED_DATES_HELD
    if member and member in date_counts.MEMBERS and not date_counts.TABLE[member].contacts and not declined:
        cores = taxonomy.held_count_cores(described, cells)
        mark = date_counts.POINT
        for core in cores:
            if "," in core and "." not in core:
                mark = date_counts.COMMA
                break
        reading = grains.Reading(grains.COUNTED, member, mark)
        reads = bool(cores)
        for core in cores:
            if grains.moment_of(core, reading) is None:
                reads = False
                break
        if reads:
            return taxonomy.with_held_dates(
                described,
                grains.record(_held_dates_grain(cells, reading, described.n_present, absent)),
            )
    if member and declined:
        return taxonomy.with_made_up_counts(described, cells)
    # ...and a column held in people or in rows (a value few hold), or while
    # an open question offers `identifier`, a count being a date for all its
    # figures tell -- where they read as dates by the test.
    evidence = described.detection_evidence.form
    held = held_for_dates or evidence in (
        taxonomy.EVIDENCE_HELD_IN_PEOPLE,
        taxonomy.EVIDENCE_HELD_IN_ROWS,
        taxonomy.EVIDENCE_UNANSWERED_IDENTITY,
    )
    if held and not said_codes and taxonomy.counts_may_be_dates(described, cells):
        return taxonomy.with_made_up_counts(described, cells)
    return described


def _held_record(grain: grains.Grain) -> grains.Grain:
    """The record a held column of dates or times publishes (plan P4-D417, NF129).

    Rung `held`, the spans its walk passed -- each end a bucket the floor's
    number of people hold -- and none for a clock: a clock's day is
    bounded, so beside the held block's count of different values a span
    could leave one bucket outside it that must hold someone, so its twin
    draws from the whole day.
    """
    return dataclasses.replace(
        grain,
        rung=grains.HELD,
        spans=() if grain.reading.kind == grains.CLOCK else grain.spans,
    )


def without_census_places(document: "dict[str, object]") -> "dict[str, object]":
    """A description with no column's positional census (rule U, plan P4-D439).

    The command's half of rule U (the stand-ins page, ZS.1 (c); Codex's
    review of lane CODES-1's first repair, item 8): while any question
    offering `identifier` is open on the table -- whether or not it holds
    its own column -- no column publishes `shape_form_places`. Every other
    key of every block keeps its bytes, and a description with no census
    is returned as it was. Raises nothing.
    """
    columns = document["columns"] if "columns" in document else None
    if not isinstance(columns, list):
        return document
    if not any(
        [isinstance(block, dict) and "shape_form_places" in block for block in columns]
    ):
        return document
    kept: "list[object]" = []
    for block in columns:
        if isinstance(block, dict) and "shape_form_places" in block:
            stripped: "dict[str, object]" = {}
            for key in block:
                if key != "shape_form_places":
                    stripped[key] = block[key]
            kept += [stripped]
        else:
            kept += [block]
    answer: "dict[str, object]" = {}
    for key in document:
        answer[key] = kept if key == "columns" else document[key]
    return answer


def _places_in_subjects(
    described: taxonomy.ColumnProfile,
    cells: "list[str]",
    subject_cells: "list[list[str]]",
    enough: "list[bool]",
    floor: int,
) -> taxonomy.ColumnProfile:
    """Rule A2's positional census with no character fewer subjects hold (P4-D439).

    THE CENSUS COUNTED IN PEOPLE BESIDE A SUBJECT COLUMN (the stand-ins
    page, ZS.2 and ZS.5; plan P4-D406's rule). A listed character says
    the census line of the form's held-back cells hold it at that place;
    beside a subject column it must be held by the floor's different
    subjects too, under every subject column the column is counted in (as
    `enough` says, as `_layouts_in_subjects` reads it). Each held-back
    cell of a named form -- its label no published level's, read off the
    raw cell -- is keyed by the characters it holds at the places its
    form lists (`_holding`), and a character too few subjects hold is
    taken off its list. The forced case is asked again with the form's
    held-back cells counted in rows, the stricter reading: a place left
    with no character beside more than (a - 1)(f - 1) such cells takes
    the whole form off, a form left listing nothing is not named, and
    nor is one whose lists, one character at every place, name a
    held-back spelling outright (`taxonomy.places_name_a_spelling`).
    """
    places = described.details["shape_form_places"]
    census = described.details["shape_forms"] if "shape_forms" in described.details else None
    levels = described.details["levels"] if "levels" in described.details else None
    if not isinstance(places, dict) or not isinstance(census, dict) or not isinstance(levels, list):
        return taxonomy.without_places(described)
    named: "dict[str, bool]" = {}
    for entry in levels:
        if isinstance(entry, dict) and isinstance(entry["label"], str):
            named[parsing.folded(entry["label"])] = True
    absent = frozenset(described.absent_spellings)
    held: "dict[str, int]" = {}
    # EACH DIFFERENT HELD-BACK CELL KEYED ONCE, ITS KEYS SHARED (Codex's
    # review of lane CODES-1's first repair, item 4): a key a held row,
    # built afresh on every row and kept for the walk, cost about 1,900
    # bytes a held row of a 24-character code (38 MB at 20,011 rows, some
    # 1.9 GB at a million); now a cell's keys are worked out once and each
    # key spelled once (`_listed_keys`), and the rows are read through
    # them as the count walks (`_rows_keyed`), so nothing is kept a row.
    keyed: "dict[str, tuple[str, tuple[str, ...]]]" = {}
    spelled: "dict[tuple[str, int, str], str]" = {}
    # THE PUBLISHED SPELLINGS WEARING EACH FORM, each once: the forced
    # reading counts them as spellings of a product holding no held-back
    # cell (`taxonomy.places_name_a_spelling`).
    worn: "dict[str, dict[str, bool]]" = {}
    seen: "dict[str, bool]" = {}
    for cell in cells:
        if cell in keyed:
            form = keyed[cell][0]
            held[form] = held[form] + 1
            continue
        if cell in seen:
            continue
        if parsing.trimmed(cell) and cell not in absent and parsing.folded(cell) in named:
            seen[cell] = True
            form = parsing.census_form(cell, census)
            if form in places:
                if form not in worn:
                    worn[form] = {}
                worn[form][cell] = True
            continue
        if parsing.trimmed(cell) and cell not in absent and parsing.folded(cell) not in named:
            form = parsing.census_form(cell, census)
            if form in places and len(form) == len(cell):
                held[form] = (held[form] if form in held else 0) + 1
                keyed[cell] = (form, _listed_keys(form, cell, places[form], spelled))
    spelled = {}
    countings: "list[dict[str, SubjectCount]]" = []
    for place, subject in enumerate(subject_cells):
        if not enough[place] and not (
            _attached(cells, subject) and _names_its_people(cells, subject)
        ):
            continue
        countings += [_holding(_rows_keyed(cells, keyed), subject, floor)]
    keyed = {}
    line = parsing.census_floor(floor)
    kept: "dict[str, list[str]]" = {}
    for form in sorted(places):
        lists = places[form]
        built: "list[str]" = []
        refused = False
        for at in range(len(form)):
            listed = lists[at] if isinstance(lists[at], str) else ""
            remaining = ""
            for mark in listed:
                key = f"{form}\u0000{at}\u0000{mark}"
                fewest = floor
                for counted in countings:
                    fewest = min(
                        fewest, len(counted[key].holders) if key in counted else 0
                    )
                if fewest >= floor:
                    remaining = remaining + mark
            kind = form[at]
            if (
                kind in taxonomy.PLACE_ALPHABETS
                and not remaining
                and (held[form] if form in held else 0)
                > (len(taxonomy.PLACE_ALPHABETS[kind]) - 1) * (line - 1)
            ):
                refused = True
            built += [remaining]
        if (
            not refused
            and any([bool(entry) for entry in built])
            and not taxonomy.places_name_a_spelling(
                form,
                built,
                held[form] if form in held else 0,
                line,
                len(worn[form]) if form in worn else 0,
            )
        ):
            kept[form] = built
    return taxonomy.with_places(described, kept)


def _listed_keys(
    form: str,
    cell: str,
    lists: "list[str]",
    spelled: "dict[tuple[str, int, str], str]",
) -> "tuple[str, ...]":
    """The keys one held-back cell is counted under: its listed character at each place (P4-D439).

    `_places_in_subjects`' key `form NUL place NUL character`, spelled once
    for each different key and shared through ``spelled``. Raises nothing.
    """
    keys: "list[str]" = []
    for at in range(len(form)):
        listed = lists[at]
        if isinstance(listed, str) and cell[at] in listed:
            pair = (form, at, cell[at])
            if pair not in spelled:
                spelled[pair] = f"{form}\u0000{at}\u0000{cell[at]}"
            keys += [spelled[pair]]
    return tuple(keys)


def _rows_keyed(
    cells: "list[str]", keyed: "dict[str, tuple[str, tuple[str, ...]]]"
) -> "typing.Iterator[tuple[str, ...]]":
    """Each row's keys, read through its held-back cell's shared ones as `_holding` walks (P4-D439).

    ``keyed`` holds each different held-back cell of a censused form with
    its form and keys; any other cell is counted under none.
    """
    for cell in cells:
        yield keyed[cell][1] if cell in keyed else ()


def _layouts_in_subjects(
    described: taxonomy.ColumnProfile,
    cells: "list[str]",
    subject_cells: "list[list[str]]",
    enough: "list[bool]",
    floor: int,
) -> taxonomy.ColumnProfile:
    """A record-number column's layout census, no layout named that few subjects wear.

    PLAN P4-D406. A layout says what kind of character stood at each
    place, so one that one to `floor` - 1 subjects wear is a fact about
    those people -- the letters of one patient's name, the figures of
    one house number -- however many of their rows wear it. Each named
    layout's cells are counted in each subject column (as `enough` says:
    one of fewer than `floor` values counts only a column attached to
    it), and a layout too few subjects wear goes to the `(withheld)`
    pool before the whole-census rule (`taxonomy.layouts_counted_in_
    people`). A column of any other role, or whose layouts and pool every
    subject column reaches, is returned as it was.

    THE POOL IS COUNTED IN SUBJECTS TOO (lane HX2's skeptic, round 2,
    item 4), and so is a census that names nothing BUT its pool (Codex's
    review of lane HX2, item 7): the cells no named layout takes --
    printed as `(withheld)` or left to subtraction from the present rows
    -- are a count of their subjects' rows. While one to `floor` - 1
    subjects hold them under any subject column, the named layout the
    fewest subjects wear joins them (the earliest in sorted order on a
    tie); with none left, no layout is named and no pool printed.

    SCALE (Codex's review of lane HX2, item 9). Each layout's fewest
    subjects is counted once and the layouts are pooled in that order,
    each joining the pool's subjects (kept up to the floor) in one step:
    a census of many layouts costs a sort, not a pass a layout.
    """
    if described.role != taxonomy.ROLE_IDENTIFIER:
        return described
    forms = (
        described.details["layout_forms"]
        if "layout_forms" in described.details
        else None
    )
    if not isinstance(forms, dict) or not forms:
        return described
    named: "dict[str, bool]" = {}
    for layout in forms:
        if layout != taxonomy.SUPPRESSED_LABEL:
            named[f"{layout}"] = True
    absent = frozenset(described.absent_spellings)
    present: "list[str]" = []
    for cell in cells:
        if parsing.folded(cell) and cell not in absent:
            present += [cell]
    convention = parsing.layout_convention(present)
    present = []
    memo: "dict[str, tuple[str, ...]]" = {}
    pool_key = (taxonomy.SUPPRESSED_LABEL,)
    named_keys: "dict[str, tuple[str, ...]]" = {}
    for layout in named:
        named_keys[layout] = (layout,)
    keyed: "list[tuple[str, ...]]" = []
    for cell in cells:
        if cell in memo:
            keyed += [memo[cell]]
            continue
        key: "tuple[str, ...]" = ()
        if parsing.folded(cell) and cell not in absent:
            layout = parsing.layout_form(cell, convention)
            while layout and layout not in named and parsing.layout_fill(layout) >= 2:
                layout = parsing.layout_shallower(layout)
            # A present cell no named layout takes is in the remainder the
            # census pools or leaves to subtraction: counted as one key.
            key = named_keys[layout] if layout in named else pool_key
        if len(memo) < 65536:
            memo[cell] = key
        keyed += [key]
    countings: "list[dict[str, SubjectCount]]" = []
    for place, subject in enumerate(subject_cells):
        if not enough[place] and not (
            _attached(cells, subject) and _names_its_people(cells, subject)
        ):
            continue
        countings += [_holding(keyed, subject, floor)]
    keyed = []
    held: "dict[str, bool]" = {}
    fewest: "dict[str, int]" = {}
    for layout in named:
        least = floor
        for counted in countings:
            if layout in counted:
                least = min(least, len(counted[layout].holders))
        fewest[layout] = least
        if least < floor:
            held[layout] = True
    # The pool's subjects under each subject column, kept up to the floor.
    pools: "list[dict[str, bool]]" = []
    for counted in countings:
        people: "dict[str, bool]" = {}
        for layout in counted:
            if layout == taxonomy.SUPPRESSED_LABEL or layout in held:
                _joined_up_to(people, counted[layout].holders, floor)
        pools += [people]
    waiting: "list[tuple[int, str]]" = []
    for layout in named:
        if layout not in held:
            waiting += [(fewest[layout], layout)]
    waiting = sorted(waiting)
    cursor = 0
    while _short(pools, floor) and cursor < len(waiting):
        layout = waiting[cursor][1]
        cursor = cursor + 1
        held[layout] = True
        for place, counted in enumerate(countings):
            if layout in counted:
                _joined_up_to(pools[place], counted[layout].holders, floor)
    if not held and not _short(pools, floor):
        return described
    pooled = (
        taxonomy.layouts_counted_in_people(
            described,
            tuple(sorted(held)),
            floor,
            convention == parsing.LAYOUT_PLAIN,
        )
        if held
        else described
    )
    if not _short(pools, floor):
        return pooled
    # EVERY LAYOUT POOLED AND THE POOL STILL FEWER THAN `floor` SUBJECTS'
    # (a dose written for two patients only), or a census of nothing but
    # a pool that few hold: no layout census at all.
    details: "dict[str, object]" = {}
    for field in sorted(pooled.details):
        details[field] = pooled.details[field]
    details["layout_forms"] = {}
    if "layout_prefixes" in details:
        details["layout_prefixes"] = {}
    return dataclasses.replace(pooled, details=details)


def _joined_up_to(
    people: "dict[str, bool]", holders: "tuple[str, ...]", floor: int
) -> None:
    """Join ``holders`` into ``people`` until it holds ``floor`` of them.

    A union of sets each kept up to the floor reaches the floor exactly
    when the whole sets' union does, so no second pass is needed.
    """
    for subject in holders:
        if len(people) >= floor:
            return
        people[subject] = True


def _short(pools: "list[dict[str, bool]]", floor: int) -> bool:
    """Whether any subject column's pool is held by one to `floor` - 1 subjects."""
    for people in pools:
        if 0 < len(people) < floor:
            return True
    return False


def _without_held(
    settings: taxonomy.Settings, held: "list[str]"
) -> taxonomy.Settings:
    """The settings a description records, each held column taken out of the readings it was declared under.

    PLAN P4-D406. A column held as a record number -- counted in people,
    or declared as counted dates its cells did not read as -- is
    described as one, and the contract reads a column one way only (S8a,
    S8d): one also named as writing a decimal comma, counted dates, dates
    of another reading, two-figure years or a 12-hour clock would be
    refused by the generator. The declaration stays on the screen and in
    the questions; the description records the column as held. With
    nothing held the settings are returned as they are.
    """
    if not held:
        return settings
    return dataclasses.replace(
        settings,
        forced_date_counts=tuple(
            pair for pair in settings.forced_date_counts if pair[0] not in held
        ),
        forced_twelve_hour_clocks=tuple(
            one for one in settings.forced_twelve_hour_clocks if one not in held
        ),
        forced_date_columns=tuple(
            one for one in settings.forced_date_columns if one not in held
        ),
        century_windows=tuple(
            pair for pair in settings.century_windows if pair[0] not in held
        ),
        # -- lane TR (P4-D473)
        forced_clock_figures=tuple(
            one for one in settings.forced_clock_figures if one not in held
        ),
    )


def _counted_dates_declined(
    settings: taxonomy.Settings,
    name: str,
    described: taxonomy.ColumnProfile,
    cells: "list[str] | None" = None,
) -> bool:
    """Whether a column declared as counted dates was read as anything but dates.

    ...or, since lane TR (plan P4-D473), a column answered `clock-figures`
    as anything but clock times: rule 5c's declaration that does not read
    holds the column, contract NF127's treatment of a declined counted-date
    declaration (the zoo-fix reading page's ZR.1), so its figures are
    never published as plain numbers. BUT NOT where ``cells`` (the
    column's cells as the table holds them) show the answer was not
    refused by them (Codex's review of lane TR, items 2 and 3): every
    present cell fits rule 5c and an EARLIER rule read the column -- one
    value or two, rules 3 and 4, which keep their precedence, so `0800`
    and `1600` alternating are the two values they always were, never
    record numbers -- or a time among them would be written as a spelling
    the table reads as no value, so the answer is not taken and the column
    is read as it was before the answer (`taxonomy.clock_figures_reading`).
    """
    if name in settings.forced_clock_figures:
        if described.role == taxonomy.ROLE_CLOCK:
            return False
        found = taxonomy.clock_figures_reading(cells, settings) if cells is not None else ""
        if found == taxonomy.FIGURES_ABSENT:
            return False
        return not (
            found == taxonomy.FIGURES_READ
            and described.role in (taxonomy.ROLE_CONSTANT, taxonomy.ROLE_BINARY)
        )
    for column, _member in settings.forced_date_counts:
        if column == name:
            return described.role != taxonomy.ROLE_DATETIME
    return False


# The patient table's settings (lane GRa, plan P4-D449): the function under a
# name another module may read.
settings_without_held = _without_held


def _census_of(described: taxonomy.ColumnProfile) -> "dict[str, object] | None":
    """A described column's census of repetition, or None where it has none."""
    if "n_distinct_by_occurrences" in described.details:
        found = described.details["n_distinct_by_occurrences"]
        if isinstance(found, dict):
            return found
    return None


def _a_small_group(census: object, floor: int) -> bool:
    """Whether a census of repetition holds an entry of one to `floor` - 1."""
    if not isinstance(census, dict):
        return False
    for key in census:
        entry = census[key]
        if isinstance(entry, int) and 0 < entry < floor:
            return True
    return False


def _census_parts(
    described: taxonomy.ColumnProfile, cells: "list[str]"
) -> "list[dict[int, int]] | None":
    """The real census of rows a value in each part of a record number's layouts.

    PLAN P4-D406 (Codex's review of lane HX2, item 1). The parts are the
    named layouts with rows (`taxonomy.census_part_names`) and one more
    for every present cell none of them takes; each value (a present
    cell as written, as `taxonomy._n_distinct_by_occurrences` counts it)
    is in the part its layout falls into. `taxonomy.with_census_in_people`
    deals its pooled people into these parts, the groups it keeps where
    they really are. None where the block names no layout census, where
    the pool and cells left to subtraction both hold rows, or where the
    parts' rows are not the census's own.
    """
    forms = (
        described.details["layout_forms"]
        if "layout_forms" in described.details
        else None
    )
    if described.role != taxonomy.ROLE_IDENTIFIER or not isinstance(forms, dict):
        return None
    names = taxonomy.census_part_names(forms)
    if len(names) < 1:
        # One part: any census that closes is dealt into it.
        return None
    pool = forms[taxonomy.SUPPRESSED_LABEL] if taxonomy.SUPPRESSED_LABEL in forms else 0
    named_rows = 0
    for layout in names:
        named_rows = named_rows + int(f"{forms[layout]}")
    left = described.n_present - named_rows - (pool if isinstance(pool, int) else 0)
    if isinstance(pool, int) and pool > 0 and left > 0:
        return None
    absent = frozenset(described.absent_spellings)
    present: "list[str]" = []
    for cell in cells:
        if parsing.folded(cell) and cell not in absent:
            present += [cell]
    convention = parsing.layout_convention(present)
    place_of: "dict[str, int]" = {}
    for place, layout in enumerate(names):
        place_of[layout] = place
    occurrences: "dict[str, int]" = {}
    for cell in present:
        occurrences[cell] = (occurrences[cell] if cell in occurrences else 0) + 1
    present = []
    parts: "list[dict[int, int]]" = []
    rows: "list[int]" = []
    for _place in range(len(names) + 1):
        parts += [{}]
        rows += [0]
    for value in occurrences:
        layout = parsing.layout_form(value, convention)
        while layout and layout not in place_of and parsing.layout_fill(layout) >= 2:
            layout = parsing.layout_shallower(layout)
        place = place_of[layout] if layout in place_of else len(names)
        part = parts[place]
        size = occurrences[value]
        part[size] = (part[size] if size in part else 0) + 1
        rows[place] = rows[place] + size
    for place, layout in enumerate(names):
        if rows[place] != int(f"{forms[layout]}"):
            return None
    return parts


def _without_table_suffix(name: str) -> str:
    """Drop a .csv or .txt ending from a file name, whatever its case."""
    if not isinstance(name, str):
        raise TypeError("internal check: a file name was not text")
    # Each ending is tested on its own: the offline policy accepts a
    # text method only with arguments it has resolved, and a tuple
    # built at the call site is not one (plan D6.2).
    lowered = name.casefold()
    if lowered.endswith(".csv"):
        return name[: len(name) - 4]
    if lowered.endswith(".txt"):
        return name[: len(name) - 4]
    # A WORKBOOK'S ENDING COMES OFF TOO (plan P4-D77). Without this a
    # table read from `clinic.xlsx` is described into
    # `clinic.xlsx-profile.json`, which reads as a mistake and which the
    # commands this run prints would then have to quote back.
    if lowered.endswith(".xlsx"):
        return name[: len(name) - 5]
    if lowered.endswith(".xlsm"):
        return name[: len(name) - 5]
    # ...AND A FILE FROM ANOTHER SYSTEM'S (lane FORMATS): `visits.dta` is
    # described into `visits-profile.json`, as `visits.csv` is.
    if lowered.endswith(".parquet"):
        return name[: len(name) - 8]
    if lowered.endswith(".sas7bdat"):
        return name[: len(name) - 9]
    if lowered.endswith(".xpt"):
        return name[: len(name) - 4]
    if lowered.endswith(".dta"):
        return name[: len(name) - 4]
    if lowered.endswith(".sav"):
        return name[: len(name) - 4]
    return name


def table_stem(name: str) -> str:
    """A table's file name without its .csv, .txt, .xlsx or .xlsm ending (lane TT, plan P4-D460).

    The stem every file the profile step names starts with, which
    `synthtwin twin` names its folder after. A fixed function of the
    name; raises TypeError where it is not text.
    """
    return _without_table_suffix(name)


def default_output_paths(
    table_path: pathlib.Path, out_dir: "str | None"
) -> "tuple[pathlib.Path, pathlib.Path]":
    """Where the two files go: beside the table unless a folder is given.

    Raises ProfileError with a plain-language message when a given
    folder does not exist, and PathValidationError when it is not a
    plain local path.
    """
    source = pathlib.Path(table_path)
    stem = _without_table_suffix(f"{source.name}")
    if out_dir is None:
        folder = pathlib.Path(source.parent)
    else:
        validated = validate_local_path(out_dir, purpose="output folder")
        folder = pathlib.Path(validated)
        if not folder.is_dir():
            raise errors.ProfileError(errors.output_folder_missing(f"{folder}"))
    # Every exact target goes through the locality gate, not just the
    # folder the user named. Phase 0's D6.1 rule covers output paths,
    # and review round 1 found the gap: a link left at the profile's
    # name sent the file wherever it pointed -- including, on POSIX,
    # over the user's own table.
    profile_target = validate_local_path(
        f"{folder / (stem + PROFILE_SUFFIX)}", purpose="output file"
    )
    summary_target = validate_local_path(
        f"{folder / (stem + SUMMARY_SUFFIX)}", purpose="output file"
    )
    first = pathlib.Path(profile_target)
    second = pathlib.Path(summary_target)
    writing.refuse_if_folder(first)
    writing.refuse_if_folder(second)
    return (first, second)


def questions_output_path(
    table_path: pathlib.Path, out_dir: "str | None"
) -> pathlib.Path:
    """Where the questions file goes, under the same rules as the pair.

    Every exact target goes through the locality gate rather than the
    folder alone, which is the rule review round 1 of Phase 1 wrote
    after a link left at an output name sent the file wherever it
    pointed. This one is no exception for being advisory.

    Raises ProfileError when a given folder does not exist and
    PathValidationError when it is not a plain local path, exactly as
    `default_output_paths` does.
    """
    source = pathlib.Path(table_path)
    stem = _without_table_suffix(f"{source.name}")
    if out_dir is None:
        folder = pathlib.Path(source.parent)
    else:
        validated = validate_local_path(out_dir, purpose="output folder")
        folder = pathlib.Path(validated)
        if not folder.is_dir():
            raise errors.ProfileError(errors.output_folder_missing(f"{folder}"))
    target = validate_local_path(
        f"{folder / (stem + QUESTIONS_SUFFIX)}", purpose="output file"
    )
    path = pathlib.Path(target)
    writing.refuse_if_folder(path)
    return path



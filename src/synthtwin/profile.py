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

from synthtwin import canonical, errors, parsing, reading, taxonomy, writing
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


def _settings_block(
    settings: taxonomy.Settings,
    forced_identifiers: list[str],
    forced_codes: list[str],
    forced_measurements: list[str],
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
        "forced_identifiers": sorted(forced_identifiers),
        # THE SECOND DECLARATION (plan P4-D19). Named columns are read
        # as labels and never as numbers, dates, clock times or
        # numbers wearing an affix, so a coding system written in
        # digits keeps its exact spellings -- padding included -- and
        # publishes which codes are common instead of a mean nobody
        # can use. Unlike `forced_identifiers` it does NOT silence the
        # column: the distribution is the point of declaring it.
        "forced_codes": sorted(forced_codes),
        # THE THIRD DECLARATION (plan P4-D21). Named columns hold
        # quantities, including ones written as two or more whole
        # numbers in one cell -- a blood pressure. Where the column is
        # written that way it takes the `joined_numbers` role; where it
        # is not, this decides nothing.
        "forced_measurements": sorted(forced_measurements),
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
# One of the three stand-in numbers this package judges, written as
# itself. The only path is the declaration records' `built_in_numbers`,
# which carries members of this package's own published vocabulary and
# no number of anybody's table (contract 5 C5-K1).
_STAND_IN_NUMBER = "numeric-sentinel-number"
_NUMBER = "number"
_MAYBE_NUMBER = "number-or-nothing"
_FLAG = "flag"
_NOTHING = "nothing"
_SENTENCE = "sentence"
_WORD = "word"
_TABLE_NAME = "column-name"
_KNOWN_NAME = "a-name-of-this-table"
_SPELLING = "authorized-spelling"
# The ONE exception in the ranges class: an affixed column publishes the
# shared text its cells wore, on two keys and no others. It is a rule of
# its own rather than `_SPELLING` because either side may be EMPTY -- a
# column of `5mg` has no prefix -- and because an exception a reader can
# see in this table is an exception nobody widens by accident. That both
# sides are not empty at once is invariant AF1, checked with the
# invariants and not here.
_AFFIX = "affix-spelling"
_DIGITS = "whole-number-as-text"
# A KEY OF THE FRACTION CENSUS: a width written as decimal figures, or
# the pooled remainder. It is not `_DIGITS`, and the difference is the
# whole point of giving it a kind of its own: `_DIGITS` admits `02`
# beside `2`, and a census whose keys admit padding is a census two
# producers spell two ways and a consumer reads as two widths. The key
# grammar is CANONICAL -- no sign, no padding, `0` written as itself.
_WIDTH = "fraction-width-as-figures"
_BIN = "histogram-bin-number"
_SHAPE_FORM = "a-written-form-a-cell-could-not-be-spelled-with"
_MOMENT_TEXT = "canonical-datetime"
_OFFSET = "utc-offset"
_SENTINEL = "numeric-sentinel-spelling"
_VERSION = "the-version-that-wrote-this"

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
PUBLICATION_RULES: "dict[tuple[str, ...], str]" = {
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
    ("settings", "forced_identifiers"): _ARRAY,
    ("settings", "forced_identifiers", _EACH): _KNOWN_NAME,
    ("settings", "forced_codes"): _ARRAY,
    ("settings", "forced_codes", _EACH): _KNOWN_NAME,
    ("settings", "forced_measurements"): _ARRAY,
    ("settings", "forced_measurements", _EACH): _KNOWN_NAME,
    # How the table was read.
    ("source",): _OBJECT,
    ("source", "encoding"): _WORD,
    ("source", "used_fallback_encoding"): _FLAG,
    ("source", "header_source"): _WORD,
    ("source", "header_by_convention"): _FLAG,
    ("source", "header_evidence"): _SENTENCE,
    # The reserved manifest, filled in below.
    ("relationships",): _OBJECT,
    # The notes, AFTER they were lifted here out of the column blocks.
    ("publication_notes",): _ARRAY,
    ("publication_notes", _EACH): _OBJECT,
    ("publication_notes", _EACH, "column"): _KNOWN_NAME,
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
    # The label roles.
    ("columns", _EACH, "levels"): _ARRAY,
    ("columns", _EACH, "levels", _EACH): _OBJECT,
    ("columns", _EACH, "levels", _EACH, "label"): _SPELLING,
    ("columns", _EACH, "levels", _EACH, "count"): _FLOOR_COUNT,
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
    ("columns", _EACH, "suppressed_level_counts"): _ARRAY,
    ("columns", _EACH, "suppressed_level_counts", _EACH): _BELOW_THE_FLOOR,
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
    ("columns", _EACH, "parts", _EACH, "numeric_styles", _ANY_KEY): _FLOORED_ENTRY,
    ("columns", _EACH, "parts", _EACH, "fraction_widths"): _OBJECT,
    ("columns", _EACH, "parts", _EACH, "fraction_widths", _KEY_OF): _WIDTH,
    ("columns", _EACH, "parts", _EACH, "fraction_widths", _ANY_KEY): _FLOORED_ENTRY,
    ("columns", _EACH, "parts", _EACH, "pad_widths"): _OBJECT,
    ("columns", _EACH, "parts", _EACH, "pad_widths", _KEY_OF): _WIDTH,
    ("columns", _EACH, "parts", _EACH, "pad_widths", _ANY_KEY): _FLOORED_ENTRY,
    ("columns", _EACH, "parts", _EACH, "value_histogram"): _OBJECT,
    ("columns", _EACH, "parts", _EACH, "value_histogram", _KEY_OF): _BIN,
    ("columns", _EACH, "parts", _EACH, "value_histogram", _ANY_KEY): _FLOORED_ENTRY,
    # The affixed-number role: the pair it publishes, how many cells
    # wore it, and the four counts that answer for the CORES rather
    # than for the cells.
    ("columns", _EACH, "affix_prefix"): _AFFIX,
    ("columns", _EACH, "affix_suffix"): _AFFIX,
    ("columns", _EACH, "n_affixed"): _COUNT,
    ("columns", _EACH, "n_core_numeric"): _COUNT,
    ("columns", _EACH, "n_core_out_of_range"): _COUNT,
    ("columns", _EACH, "n_core_contradictory"): _COUNT,
    ("columns", _EACH, "n_core_not_numeric"): _COUNT,
    ("columns", _EACH, "numeric_styles"): _OBJECT,
    ("columns", _EACH, "numeric_styles", _KEY_OF): _WORD,
    ("columns", _EACH, "numeric_styles", _ANY_KEY): _FLOORED_ENTRY,
    # The forms map's sibling: how many figures the cells written with a
    # point wrote after it. Its keys are figures rather than words of
    # this package, so they are held to a grammar rather than to a
    # vocabulary -- and its counts are held to the floor exactly as the
    # forms map's are, the pooled remainder included.
    ("columns", _EACH, "fraction_widths"): _OBJECT,
    ("columns", _EACH, "fraction_widths", _KEY_OF): _WIDTH,
    ("columns", _EACH, "fraction_widths", _ANY_KEY): _FLOORED_ENTRY,
    ("columns", _EACH, "shape_forms"): _OBJECT,
    ("columns", _EACH, "shape_forms", _KEY_OF): _SHAPE_FORM,
    ("columns", _EACH, "shape_forms", _ANY_KEY): _FLOORED_ENTRY,
    ("columns", _EACH, "pad_widths"): _OBJECT,
    ("columns", _EACH, "pad_widths", _KEY_OF): _WIDTH,
    ("columns", _EACH, "pad_widths", _ANY_KEY): _FLOORED_ENTRY,
    ("columns", _EACH, "value_histogram"): _OBJECT,
    ("columns", _EACH, "value_histogram", _KEY_OF): _BIN,
    ("columns", _EACH, "value_histogram", _ANY_KEY): _FLOORED_ENTRY,
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
    ("columns", _EACH, "earliest"): _MOMENT_TEXT,
    ("columns", _EACH, "latest"): _MOMENT_TEXT,
    ("columns", _EACH, "earliest_utc_offset"): _OFFSET,
    ("columns", _EACH, "latest_utc_offset"): _OFFSET,
    ("columns", _EACH, "date_percentiles"): _OBJECT,
    ("columns", _EACH, "date_percentiles", _KEY_OF): _WORD,
    ("columns", _EACH, "date_percentiles", _ANY_KEY): _MOMENT_TEXT,
    # The clock role's own two. `earliest`, `latest` and `n_unparsed`
    # need no row of their own and must not be given one: these rules
    # are keyed by PATH and not by role, so the rows above already
    # serve both roles -- a clock value is canonical moment text by the
    # same character rule a date is.
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
    ("columns", _EACH, "clock_percentiles", _ANY_KEY): _MOMENT_TEXT,
    ("columns", _EACH, "n_unparsed"): _COUNT,
    ("columns", _EACH, "utc_offsets"): _OBJECT,
    ("columns", _EACH, "utc_offsets", _KEY_OF): _OFFSET,
    ("columns", _EACH, "utc_offsets", _ANY_KEY): _FLOORED_ENTRY,
    # The roles that publish no value at all.
    ("columns", _EACH, "min_length"): _COUNT,
    ("columns", _EACH, "max_length"): _COUNT,
    ("columns", _EACH, "all_whole_numbers"): _FLAG,
    ("columns", _EACH, "n_all_digits"): _COUNT,
    ("columns", _EACH, "n_code_alphabet"): _COUNT,
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

# For every path whose rule is `_WORD`, the WHOLE of what may stand
# there. These are this package's own vocabularies, written out where
# they are defined and read from there: a set gathered from the
# document being checked would accept whatever it found.
PUBLICATION_WORDS: "dict[tuple[str, ...], tuple[str, ...]]" = {
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
    ("columns", _EACH, "date_percentiles", _KEY_OF): taxonomy.LADDER_NAMES,
    ("columns", _EACH, "clock_percentiles", _KEY_OF): taxonomy.LADDER_NAMES,
    # Read from the one place the two forms are named, so the word a
    # producer writes and the word this guard admits cannot drift.
    ("columns", _EACH, "clock_form"): parsing.CLOCK_FORMS,
    ("columns", _EACH, "resolution_mix", _KEY_OF): parsing.DATE_FORMATS,
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
    """Canonical date, datetime or quarter text, and nothing else."""
    if not isinstance(value, str) or not value:
        return False
    for character in value:
        if character not in _DATETIME_CHARACTERS:
            return False
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
    if kind == _ZERO_OR_AT_THE_FLOOR:
        # A named group, or nothing at all. There is no third answer:
        # a group the floor held back is not written here, it is added
        # to the pooled remainder beside it (contract 5 C5-N4).
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        return value == 0 or value >= context.floor
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
    if kind == _FLAG:
        return isinstance(value, bool)
    if kind == _NOTHING:
        return value is None
    if kind == _SENTENCE:
        return _is_sentence(value)
    if kind == _TABLE_NAME:
        # A column's name IS text of the real table, and the matrix
        # authorizes it: the twin's header row has to carry it. So this
        # rule asks only that it is text with something in it, and the
        # guard makes no attempt to tell a name from a cell -- nothing
        # could, and the profile is required to publish this one.
        return isinstance(value, str) and bool(parsing.trimmed(value))
    if kind == _KNOWN_NAME:
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
    if kind == _DIGITS:
        return isinstance(value, str) and parsing.is_digit_text(value)
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
    if kind == _SHAPE_FORM:
        return _is_shape_form(value)
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


def _check_word(
    value: object, path: "tuple[str, ...]"
) -> None:
    """Refuse anything but a word of the vocabulary this path allows."""
    if path not in PUBLICATION_WORDS:
        raise _refuse(path)
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
        return
    if kind == _ARRAY:
        if not isinstance(node, list):
            raise _refuse(path)
        for item in node:
            _check_published(item, path + (_EACH,), "", context)
        return
    if kind == _WORD:
        _check_word(node, path)
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
                said = said + [remark]
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
    _affix_notes_are_bound(document)


def build_document(
    table: Table,
    settings: taxonomy.Settings,
    forced_identifiers: list[str],
    forced_codes: list[str] | None = None,
    forced_measurements: list[str] | None = None,
) -> dict[str, object]:
    """Describe a whole table: the profile document, ready to serialize.

    Guarantees:

    - Inputs: a Table as produced by the reader, the settings that
      govern the taxonomy, and the names of columns the user declared
      to be record numbers.
    - Determinism: the document depends only on those inputs. No clock,
      no environment, no random source, and every mapping written out
      is written in sorted key order.
    - Errors raised: TypeError if a cell is not text (an internal
      invariant of the readers).
    - Boundary: no file is opened here, and no value of a suppressed
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
    """
    declared_codes = [] if forced_codes is None else forced_codes
    declared_measurements = (
        [] if forced_measurements is None else forced_measurements
    )
    columns: list[dict[str, object]] = []
    notes: list[dict[str, str]] = []
    for position, name in enumerate(table.column_names, start=1):
        described = taxonomy.profile_column(
            name,
            position,
            table.columns[position - 1],
            table.n_rows,
            settings,
            name in forced_identifiers,
            name in declared_codes,
            name in declared_measurements,
        )
        columns = columns + [_column_block(described)]
        for note in described.publication_notes:
            notes = notes + [{"column": name, "note": note}]
    document: dict[str, object] = {
        "profile_version": PROFILE_VERSION,
        "created_with": _version(),
        "settings": _settings_block(
            settings,
            forced_identifiers,
            declared_codes,
            declared_measurements,
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
    # THE LAST THING THAT HAPPENS, and it happens to the FINISHED
    # document (plan P2-D2). The notes were lifted out of the column
    # blocks a few lines above, so a check made anywhere earlier would
    # not have seen them; this one walks everything that is about to be
    # serialized and stops the run rather than write a description
    # carrying anything the rules do not authorize.
    check_publication(document)
    return document


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
    return name


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



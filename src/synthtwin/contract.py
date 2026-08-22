"""The strict profile loader: the only way generation gets a profile.

The normative text is `docs/spec/profile-contract-v5.md`, which carries
`docs/spec/profile-contract-v4.md` by reference: every rule version 5
does not supersede is a rule of version 5 at its version 4 wording, and
a superseding clause is written into version 5 with the version 4 rule
it names. This module carries both out rule for rule. Nothing here
decides anything either contract left open; where a contract states a
fact, the check below cites it by its own identifier so a reader can
hold the two side by side -- an identifier beginning `C5-` is version
5's, and every other is version 4's, carried.

WHAT THIS MODULE IS FOR. A twin is built from a profile and a seed, and
from nothing else (plan P2-D1). That makes the profile the whole of what
the generator knows about the real table, so a profile it cannot prove
conforming is a profile it must not use: every later stage would then be
reading a fact nobody checked. This loader is therefore FAIL-CLOSED. A
document it cannot prove conforming is refused, never repaired, never
partly accepted, and the refusal says what happened and what to do next
in words a person who has never programmed can act on.

THE BOUNDARY THIS MODULE UPHOLDS. It accepts one filesystem path to a
profile document and nothing else. It never constructs a table path, a
table handle, a table object or a collection of raw cells, and it
imports neither the reader nor pandas, directly or through anything it
does import: `canonical` imports json alone, `errors` and `parsing`
import nothing outside this package, and `paths` imports os, pathlib,
sys and typing (plan P2-D1).

THE ORDER OF THE CHECKS IS NORMATIVE (contract section 10.1), because it
decides which message a person sees when a file is wrong in more than
one way, and the most useful message is the one nearest the cause:

  1. resolve and open the path                     R1, R2, R3
  2. read the bytes and decode them as UTF-8       R4, R19
  3. the bounded structural pre-scan over the TEXT R8, R9
  4. parse with a plain JSON parse                 R5
  5. read `profile_version`, which must be 5       R11, R12
  6. the canonical round trip                      R6, R7, R10
  7. schema and invariant validation               R13 - R18
  8. build and return typed objects                --

Step 5 comes before step 6 because direction-correct version advice is
more use to a person than a complaint about canonical form, and an older
or a newer document is very likely canonical under its own rules. The
consequence is stated rather than hidden: at step 5 the version has not
yet been proved unique, so a document with the key written twice is
described by its last value -- and is refused a moment later at step 6
anyway.

WHY THE PRE-SCAN COMES BEFORE THE PARSE. Both bounds exist to protect
the parser itself, and a bound checked afterwards is a bound checked
after the cost has been paid.

WHAT THIS MODULE DOES NOT DO. It runs no generation feasibility check of
any kind: whether a generator can meet what a valid profile asks of it
is a separate stage that runs after loading, so that a contract-valid
document never becomes unloadable and a refusal to GENERATE is never
mistaken for a claim that the description is invalid (contract 10.2). It
also repairs nothing: it does not normalize, reorder, coerce, default or
fill.

WHAT IT RETURNS. Typed objects, never the parsed mapping. A consumer
that reads `column.facts.percentiles` on a column that has no ladder
gets an error where it made the mistake, rather than a None it will
carry three modules further. The list order of the returned columns IS
the order of `columns` in the document, which is the schema order, the
order the twin's columns are written in, and the order the one random
stream is consumed in (contract S3).

THREE ATTRIBUTE NAMES DIFFER FROM THEIR KEYS IN THE FILE, and the
difference is forced rather than chosen: `min` and `max` -- the two end
rungs of a ladder and the ends of the length and word counts -- and
`format` on a datetime column are all names of Python built-ins, and the
offline audit refuses source that binds a built-in name to anything at
all (plan D6.2), because a rebound built-in could make a checked call
mean something else. They are `minimum`, `maximum` and `parser_family`
here. Every other attribute has exactly the name the file uses.

Imports here stay within the allowlist (plan D6.2): dataclasses, json,
math, pathlib, and this package's own `canonical`, `errors`, `parsing`
and `paths` -- none of which reaches the reader or pandas.
"""

import dataclasses
import json
import math
import pathlib

from synthtwin import canonical, errors, parsing
from synthtwin.paths import validate_local_path

# The one version this loader reads. `profile_version` must be exactly
# this integer: an older document gets advice to make the description
# again, a newer one gets advice to update synthtwin and NEVER to re-run
# a profiler on a machine that may not hold the table (contract 10.6).
#
# IT IS FIVE FROM AMENDMENT A-P3-27, AND THERE IS NO UPGRADE PATH
# (contract 5 sections 10.1 and 10.2, owner ruling 2026-08-17). A
# version 4 document is refused, not converted: it records a declaration
# only as a count, so converting it would mean making up the facts the
# older rules did not record, which is the whole reason this version
# exists. The refusal names both versions, says WHY the older file
# cannot be read back, and tells the person to describe their table
# again WITH THE SAME `--keep-value` AND `--missing-value` OPTIONS --
# advice that is safe today because there is no release and every
# description belongs to somebody who still holds the table, and that
# is re-examined rather than inherited after the first one.
PROFILE_VERSION = 5

# THE TWO PARSER BOUNDS, AND THERE ARE EXACTLY TWO (contract 10.3).
# Neither is reachable by any producible profile, because neither scales
# with the table: a conforming document is six levels deep whatever the
# data is, and the producer's longest published number is far shorter
# than this. There is no document-size cap, no container-entry cap and
# no producer-side cap anywhere in this phase -- a description too large
# for the machine fails on the memory path (R19), exactly as the
# profiler's own reader does, so the two halves of the product promise
# the same thing.
MAXIMUM_DEPTH = 32
MAXIMUM_NUMBER_CHARACTERS = 64

# The pooled-remainder key, everywhere it appears; the blank spelling;
# and the no-offset marker (contract section 14).
WITHHELD = "(withheld)"
BLANK = "(blank)"
NO_OFFSET = "(none)"

TOP_LEVEL_KEYS = (
    "columns",
    "created_with",
    "n_columns",
    "n_rows",
    "profile_version",
    "publication_notes",
    "relationships",
    "settings",
    "source",
)

SOURCE_KEYS = (
    "encoding",
    "header_by_convention",
    "header_evidence",
    "header_source",
    "used_fallback_encoding",
)

SETTINGS_KEYS = (
    "categorical_ceiling",
    "categorical_floor",
    "categorical_share",
    "declaration_matching",
    "declaration_publication",
    "declared_missing_values",
    "forced_identifiers",
    "identifier_minimum_rows",
    "identifier_uniqueness",
    "kept_values",
    "minimum_parse_rate",
    "near_threshold_slack",
    "sentinel_minimum_share",
    "sentinel_outlier_iqr_multiple",
    "small_cell_floor",
)

# The four keys of each declaration record (contract 5 section 6.2,
# invariant C5-S14). Version 4 had the first two; version 5 adds the two
# lists that say which members of this package's OWN published
# vocabulary a declaration named, and never a spelling of the person's.
DECLARATION_KEYS = (
    "built_in_numbers",
    "built_in_texts",
    "n_declared",
    "values_recorded",
)

# THE FLOOR `synthtwin profile` WRITES WHEN NOBODY ASKS FOR ANOTHER
# (contract 4.4). The loader accepts any whole number of 1 or more --
# the owner's ruling of 2026-08-14, plan amendment A-P3-11 -- so this is
# not a bound and no refusal is taken against it. It is the number the
# reports compare a description's own floor against, so that a
# description made with a LOWER one can be recognized and said out loud
# on the face of every file built from it.
#
# It is the same number `taxonomy.Settings` defaults to. The two are
# written in two modules because the generation and validation paths may
# not import the profiler's taxonomy at all, and the suite compares them
# so a change in one cannot pass unnoticed in the other.
DEFAULT_SMALL_CELL_FLOOR = 11

# The eight reserved cross-column names. This version of synthtwin
# carries no structure between columns and says so in eight named
# places, every one of them empty (contract 4.6, S12).
RELATIONSHIP_KEYS = (
    "deterministic",
    "grain",
    "hierarchy",
    "keys",
    "missing_data_process",
    "statistical",
    "temporal",
    "validation_targets",
)

NOTE_KEYS = ("column", "note")

# Present on every column of every role, whatever the role adds
# (contract 5.1). There are no optional keys in version 4: a key that
# appears only sometimes is a key a consumer comes to guess about.
UNIVERSAL_COLUMN_KEYS = (
    "detection_evidence",
    "missing_by_class",
    "missing_by_source",
    "n_contradictory",
    "n_distinct",
    "n_distinct_folded",
    "n_missing",
    "n_missing_blank",
    "n_missing_withheld",
    "n_not_numeric",
    "n_numeric",
    "n_out_of_range",
    "n_present",
    "n_sentinel_candidates_unpublished",
    "name",
    "position",
    "quality_state",
    "remarks",
    "role",
    "sentinel_verdicts",
    "statistical_type",
    "structural_role",
)

ROLE_EMPTY = "empty"
ROLE_UNREPRESENTABLE = "numeric_unrepresentable"
ROLE_CONSTANT = "constant"
ROLE_BINARY = "binary"
ROLE_DATETIME = "datetime"
ROLE_COUNT = "count"
ROLE_CONTINUOUS = "continuous"
ROLE_CATEGORICAL = "categorical"
ROLE_IDENTIFIER = "identifier"
ROLE_AFFIXED = "affixed_number"
ROLE_TEXT = "free_text"

ROLES = (
    ROLE_EMPTY,
    ROLE_UNREPRESENTABLE,
    ROLE_CONSTANT,
    ROLE_BINARY,
    ROLE_DATETIME,
    ROLE_COUNT,
    ROLE_CONTINUOUS,
    ROLE_CATEGORICAL,
    ROLE_IDENTIFIER,
    ROLE_AFFIXED,
    ROLE_TEXT,
)

# The three roles whose block may carry no value of the table anywhere,
# to which is added any column the person declared with --identifier
# whatever role it reached (contract 6.10). On those columns, and only
# those, `missing_by_source` is empty and every stand-in candidate reads
# `(withheld)`.
ROLES_PUBLISHING_NOTHING = (
    ROLE_UNREPRESENTABLE,
    ROLE_IDENTIFIER,
    ROLE_TEXT,
)

# The derivation table of contract 5.2, in full: (role, statistical
# type, quality state). It is total over the ten roles and admits no
# other combination, and the generator dispatches on the axes rather
# than on the role name.
AXIS_ROWS = (
    (ROLE_EMPTY, "unknown", "empty"),
    (ROLE_UNREPRESENTABLE, "numeric", "unrepresentable"),
    (ROLE_CONSTANT, "constant", "ok"),
    (ROLE_BINARY, "binary", "ok"),
    (ROLE_DATETIME, "datetime", "ok"),
    (ROLE_COUNT, "count", "ok"),
    (ROLE_CONTINUOUS, "continuous", "ok"),
    (ROLE_CATEGORICAL, "categorical", "ok"),
    (ROLE_IDENTIFIER, "code", "ok"),
    (ROLE_AFFIXED, "affixed_number", "ok"),
    (ROLE_TEXT, "text", "ok"),
)

STATISTICAL_TYPES = (
    "unknown",
    "numeric",
    "constant",
    "binary",
    "datetime",
    "count",
    "continuous",
    "categorical",
    "code",
    "affixed_number",
    "text",
)

QUALITY_STATES = ("ok", "empty", "unrepresentable")

STRUCTURAL_ROLES = ("data", "identifier")

ENCODINGS = ("utf-8-sig", "latin-1")

HEADER_SOURCES = ("file", "generated")

MISSING_CLASS_KEYS = (
    BLANK,
    "(declared-missing)",
    "(numeric-sentinel)",
    "(text-code)",
    WITHHELD,
)

SENTINEL_KEYS = ("candidate", "n_occurrences", "reason", "verdict")

VERDICT_MISSING = "read_as_missing"

VERDICTS = (VERDICT_MISSING, "kept_as_a_number")

REASON_OUTLIER_AND_FREQUENT = "outlier_and_frequent"

REASONS = (
    REASON_OUTLIER_AND_FREQUENT,
    "not_an_outlier",
    "too_rare",
    "too_few_other_values",
    "kept_by_you",
)

LEVEL_KEYS = ("count", "label", "variants", "variants_withheld")

LABEL_KEYS = (
    "levels",
    "suppressed_level_counts",
    "suppressed_levels",
    "suppressed_rows",
)

CATEGORICAL_KEYS = LABEL_KEYS + ("level_ceiling",)

DATETIME_KEYS = (
    "date_percentiles",
    "datetimes_read_at",
    "earliest",
    "earliest_utc_offset",
    "format",
    "latest",
    "latest_utc_offset",
    "n_unparsed",
    "resolution",
    "subsecond_digits",
    "time_precision",
    "utc_offsets",
)

NUMERIC_KEYS = (
    "fraction_widths",
    "integer_valued",
    "mean",
    "n_left_out_of_statistics",
    "n_negative",
    "n_negative_unrepresentable",
    "n_rows",
    "n_used_in_statistics",
    "n_zero",
    "numeric_share",
    "numeric_styles",
    "percentiles",
    "skew",
    "std",
    "std_unrepresentable",
)

# The affixed-number role: everything a numeric column carries, plus
# the pair it publishes, how many cells wore it, and the four counts
# that answer for the CORES rather than for the cells. The two
# populations are never the same one, and the key names say which each
# answers for.
AFFIXED_KEYS = NUMERIC_KEYS + (
    "affix_prefix",
    "affix_suffix",
    "n_affixed",
    "n_core_contradictory",
    "n_core_not_numeric",
    "n_core_numeric",
    "n_core_out_of_range",
)

UNREPRESENTABLE_KEYS = (
    "n_distinct_by_occurrences",
    "n_fraction",
    "n_negative",
    "n_positive",
    "n_sign_unknown",
    "n_whole",
    "n_whole_unknown",
)

IDENTIFIER_KEYS = (
    "all_whole_numbers",
    "max_length",
    "min_length",
    "n_all_digits",
    "n_code_alphabet",
    "n_distinct_by_occurrences",
)

TEXT_KEYS = (
    "length",
    "n_all_digits",
    "n_code_alphabet",
    "n_distinct_by_occurrences",
    "words",
)

LENGTH_KEYS = ("max", "mean", "min", "p50")

WORD_KEYS = ("max", "mean", "min")

# The eleven rungs, in ladder order. The order is the rule: a ladder is
# checked non-decreasing by walking it in exactly this sequence.
LADDER_KEYS = (
    "min",
    "p01",
    "p05",
    "p10",
    "p25",
    "p50",
    "p75",
    "p90",
    "p95",
    "p99",
    "max",
)

DATE_FORMATS = (
    "iso-date",
    "iso-datetime",
    "compact-date",
    "month-first-date",
    "day-first-date",
    "year-quarter",
)

RESOLUTIONS = ("date", "datetime", "quarter")

TIME_PRECISIONS = ("subsecond", "second", "minute", "date", "quarter")

CLOCKS = ("local", "utc")

NUMERIC_STYLES = (
    "plain",
    "leading_zero",
    "leading_plus",
    "decimal",
    "exponent_lower",
    "exponent_upper",
)

# WHAT AN AFFIXED COLUMN'S OWN REMARK READS, in the one clause of it
# that carries no argument. Invariant AF-R says every `affixed_number`
# column bears the remark that names the pair, says how many cells wore
# it, and names `--identifier` as the route for a column of codes -- and
# a document that dropped it would publish a distribution over what may
# be a column of account numbers with nothing warning its reader.
#
# THIS IS A SECOND SPELLING OF ONE SENTENCE, and it is one deliberately,
# for the reason `DEFAULT_SMALL_CELL_FLOOR` is: the generation and
# validation paths may not import the profiler's taxonomy, so the loader
# cannot render the sentence it is looking for. Two modules holding one
# phrase is the arrangement, and
# `tests/test_p4d4_affixed_role.py` is the comparison that keeps it
# honest -- it renders the real form and asserts this phrase is in it.
AFFIXED_REMARK_MARK = "If these are codes rather than measurements"

# ...AND THE REST OF ITS FIXED SKELETON, in the order the sentence
# writes them. One marker was not enough and the gap was not a small
# one: a description carrying the marker ALONE as its whole remark --
# thirty-nine characters naming no pair, no count and no command --
# satisfied AF-R while telling its reader nothing the invariant exists
# to tell them. A sentence holding every fragment below, in order,
# around the block's own count IS the sentence; a forgery that
# reproduces all of it has written the remark.
AFFIXED_REMARK_PARTS = (
    "of this column's values are written as",
    "and synthtwin described those numbers as quantities: their "
    "average, their spread and their ends are in this profile.",
    AFFIXED_REMARK_MARK,
    "run the command again with --identifier and no value of this "
    "column will be published at all",
)

# The one form of the six the fraction census is taken over, named here
# rather than spelled at the place it is read: the census and the forms
# map have to agree about which form they are talking about, and a
# spelling repeated at two sites is a spelling one site can change.
DECIMAL_STYLE = "decimal"

DECLARATION_MATCHING = "exact_number_when_it_reads_as_one_else_spelling"

DECLARATION_PUBLICATION = "settings_counts_only_columns_unchanged"

# EVERY INVARIANT THIS LOADER REFUSES BY NAME, UNDER THE CONTRACT'S OWN
# IDENTIFIER, with the words a person reads when it is broken. The
# mapping is here rather than at each call site for two reasons: a rule
# is then worded in exactly one place, and the test battery can prove
# that every rule named here has at least one document that must be
# refused.
#
# A NAMED RULE OF THE CONTRACT THAT IS NOT HERE IS EITHER ENFORCED AS
# SOMETHING MORE USEFUL TO SAY, OR IMPLIED BY A RULE THAT IS, OR NOT A
# REFUSAL AT ALL. The whole list, so that a reviewer can check it
# against the contract rather than trust it:
#
# * S12 is the empty relationship block, refused by R18, whose message
#   says that a newer synthtwin is needed -- which is what the person
#   has to do about it. Its key set is enforced as keys (R13, R14).
# * L4, and the eleven keys of a ladder, are enforced as the key set:
#   naming the rung that is missing or unknown is more use than naming
#   the rule.
# * M1 and M2 are the generic sums of a repetition pattern, and every
#   place a pattern appears has its own identifier for them -- U3 on a
#   column of numbers too large to hold, I2 on record numbers, F2 on
#   text, and W4 for a label's held-back spellings. Those are the ones
#   raised, because they name the rule in the section a reader will
#   look the column up in.
# * U4, I3 and F3 are N3 and V2 stated again for one role each. N3 and
#   V2 are the ones raised, and they are checked on every column.
# * F4 (a value of a column of text is at least one character long) and
#   the range of a repetition pattern's row counts are ranges, refused
#   by R16, which names the key and the range.
# * X5 (a position is one of the table's places) cannot be broken on its
#   own: S1 fixes the length of the list and S2 fixes each position to
#   its place in it, so a document that breaks X5 breaks one of those
#   first. The range check on `position` stands anyway, so that a
#   nonsensical position gets a message about the key rather than about
#   the list.
# * L2 (the ends of a ladder are its smallest and largest) follows from
#   L1 on a ladder that is checked non-decreasing.
# * B8 (a column may publish no labels at all) and G2 (the level
#   ceiling imposes no obligation) are permissions, not refusals.
# * S3 (list order is schema order, output order and draw order) is not
#   a property of one document: it is what this loader UPHOLDS by
#   returning the columns in the document's own order.
# * Q8 (the integer rule is routed by the published fact) and P4 (the
#   style map and `integer_valued` are independent) are rules about what
#   a generator does, and a loader that checked them would be refusing
#   conforming input.
# * W1 (variants appear on published level entries only) and W6 (variant
#   keys are distinct) are enforced by the key sets and by the canonical
#   round trip: a repeated key cannot survive it.
# * C2 and Y2 -- that a column of one value publishes or holds back one
#   label, and a column of two exactly two -- follow from B2 together
#   with C1 and Y1, which are all checked. A check that cannot fail is a
#   defect, so they are not written twice.
# * I1 follows the same way: a column whose type path is `identifier`
#   holds codes by A4 and is therefore a declared column by A2, and E1
#   already refuses any column that holds no value under a type path
#   other than `empty`.
INVARIANTS = {
    "S1": (
        "the list of columns holds one block for every column the "
        "description says the table has"
    ),
    "S2": (
        "each column block's position is its own place in the list, "
        "counting from one"
    ),
    "S4": (
        "every column has a name, and no two columns share one"
    ),
    "S5": (
        "the description records that it fell back to another encoding "
        "exactly when the encoding it names is the fallback one"
    ),
    "S6": (
        "the first row can only have been taken as names by convention "
        "when the names came from the file at all"
    ),
    "C5-S7": (
        "this record says how many values were declared and which of "
        "synthtwin's own published words were among them, and no "
        "spelling of the person's own stands in this record -- the "
        "spelling itself can stand in a column's `missing_by_source` "
        "instead"
    ),
    "S8": (
        "every column named as holding record numbers is a column of "
        "this table"
    ),
    "S9": (
        "the smallest number of categories allowed is not larger than "
        "the largest"
    ),
    "S10": "every note is about a column of this table",
    "S11": (
        "the notes are grouped by column, in the order the columns come "
        "in the table"
    ),
    "C5-S13": (
        "a description made with a smallest group size of one holds "
        "nothing back, because there is no group below that size for it "
        "to hold back"
    ),
    "A1": (
        "a column is marked as holding record numbers exactly when its "
        "name is one of the names the person declared"
    ),
    "A2": (
        "only a column the person declared can be described as holding "
        "codes"
    ),
    "A3": (
        "a column the person declared holds either codes or nothing at "
        "all, and is described as record numbers or as empty"
    ),
    "A4": (
        "a column's kind and its condition are the pair its type path "
        "always produces"
    ),
    "X1": (
        "the values a column holds and the cells it leaves empty "
        "together come to the number of rows in the table"
    ),
    "X2": (
        "every value of a column is counted once, as a number, as not a "
        "number, as too large to hold, or as contradicting itself"
    ),
    "X3": (
        "a column cannot hold more different values ignoring case than "
        "different values, nor more different values than values"
    ),
    "X4": (
        "a column has no different values exactly when it has no values "
        "at all"
    ),
    "N1": (
        "the empty cells counted by reason come to the number of empty "
        "cells"
    ),
    "N2": (
        "a reason for an empty cell is either not used at all or used "
        "by at least the smallest group size"
    ),
    "C5-N3": (
        "the empty spellings, the blank cells and the cells held back "
        "come to the number of empty cells, and a column that publishes "
        "no value of the table accounts for none of them"
    ),
    "C5-N4": (
        "an empty spelling is named only when at least the smallest "
        "group size of rows wrote it, and so is the blank count"
    ),
    "C5-K1": (
        "a declaration record names only synthtwin's own published "
        "words for 'no value', never a value out of the table"
    ),
    "C5-K3": (
        "a declaration record never names more of synthtwin's own words "
        "than the number of values it says were declared"
    ),
    "C5-K4": (
        "no word is named both as a value to keep and as a value to "
        "read as 'no value'"
    ),
    "V1": (
        "a stand-in number is named only when at least the smallest "
        "group size of rows held it"
    ),
    "V2": (
        "a column that publishes no value of the table does not name a "
        "stand-in number either"
    ),
    "V3": (
        "a stand-in number is read as no value only when it was both "
        "far out and frequent"
    ),
    "V4": (
        "the decisions about stand-in numbers are in the order the "
        "description publishes them in"
    ),
    "M3": (
        "every row count in a repetition pattern is written in the same "
        "width, that of the largest of them"
    ),
    "M4": "a repetition pattern counts one thing or more at each size",
    "L1": "the eleven points of a ladder never go down",
    "L3": (
        "a point of a ladder of dates is always a date, and never "
        "nothing"
    ),
    "E1": "a column is empty exactly when it holds no value",
    "U1": (
        "every value of a column of numbers too large to hold is "
        "counted once, as whole, as not whole, or as neither settled"
    ),
    "U2": (
        "every value of a column of numbers too large to hold is "
        "counted once, as positive, as negative, or as neither settled"
    ),
    "U3": (
        "the repetition pattern accounts for every different value and "
        "every row that holds one"
    ),
    "B1": (
        "a published label is written trimmed and with its case folded"
    ),
    "B2": (
        "the labels published and the labels held back together are all "
        "the different values, ignoring case"
    ),
    "B3": (
        "the rows under the published labels and the rows under the "
        "ones held back together are all the rows that hold a value"
    ),
    "B4": (
        "the sizes of the labels held back are as many as the labels "
        "held back, come to the rows they cover, and rise"
    ),
    "B5": (
        "a label is published only at the smallest group size or more, "
        "and a label held back covers fewer rows than that"
    ),
    "B6": (
        "the labels come in order of how many rows they cover, largest "
        "first, and by name where two cover the same number"
    ),
    "B7": "no two published labels are the same label",
    "C1": "a column of one value has one value, ignoring case",
    "Y1": "a column of two values has two, ignoring case",
    "G1": (
        "a column of categories has no more different values than the "
        "line it passed allows"
    ),
    "D1": (
        "the form the dates are published in follows the form they were "
        "read in"
    ),
    "D2": (
        "the counted time offsets come to the values that were read as "
        "dates"
    ),
    "D3": (
        "a time offset is named only when at least the smallest group "
        "size of rows carried it"
    ),
    "D4": (
        "the offset of the first or last value is never one the "
        "description is holding back"
    ),
    "D5": (
        "dates written under two or more different offsets are "
        "published on the shared clock"
    ),
    "D6": (
        "the finest time detail a column writes fits the form its dates "
        "are published in"
    ),
    "D7": (
        "fractions of a second are counted exactly when the column "
        "writes them"
    ),
    "D8": "a column of dates has at least one value that read as a date",
    "D9": (
        "an offset from the shared clock is named only where the column "
        "publishes a date AND a time of day for it to move"
    ),
    "D10": (
        "the first and last values of a column of dates are ones a cell "
        "of that column's own recorded detail and clock can show"
    ),
    "D11": (
        "the two ends of the ladder of dates are the column's first and "
        "last values themselves"
    ),
    "Q1": (
        "the row count a column of numbers repeats is the row count of "
        "the table"
    ),
    "Q2": (
        "the statistics were computed from the values that read as "
        "numbers, and the rest were left out"
    ),
    "Q3": "a column of numbers holds at least one number",
    "Q4": (
        "the spread is left out exactly when there are fewer than two "
        "values or the spread is too large to hold"
    ),
    "Q5": (
        "the shape is left out when there are fewer than three values "
        "or every value is the same, and is given otherwise"
    ),
    "Q6": (
        "a column whose values are all the same has a spread of zero "
        "that this format can hold"
    ),
    "Q7": (
        "the average is left out only when it is not a number this "
        "format can hold"
    ),
    "Q9": (
        "the share of values meant as numbers is that count divided by "
        "the values the column holds"
    ),
    "Q10": (
        "the negative values too large to hold are not more than the "
        "values too large to hold, nor more than the negative ones"
    ),
    "Q11": (
        "the zeroes are not more than the values that read as numbers"
    ),
    "I2": (
        "the repetition pattern accounts for every different value and "
        "every row that holds one"
    ),
    "I4": (
        "the shortest value of a column of record numbers is at least "
        "one character long and no longer than the longest"
    ),
    "F1": (
        "the length and word counts of a column of text lie between "
        "their own smallest and largest"
    ),
    "F2": (
        "the repetition pattern accounts for every different value and "
        "every row that holds one"
    ),
    "W2": (
        "a spelling of a published label folds to that label and to no "
        "other"
    ),
    "W3": (
        "a spelling of a label is not written by more rows than the "
        "label itself"
    ),
    "W4": (
        "the spellings named and the spellings held back together "
        "account for every row under the label"
    ),
    "W5": (
        "a spelling is named only at the smallest group size or more, "
        "and a spelling held back was written by fewer rows than that"
    ),
    "W7": (
        "a published label was written some way, so it has a named "
        "spelling or a held-back one"
    ),
    "P1": (
        "the cells counted by the form they were written in come to the "
        "cells that read as numbers"
    ),
    "P2": (
        "a way of writing a number is named only when at least the "
        "smallest group size of cells used it"
    ),
    "P3": (
        "a column of numbers says how its numbers were written"
    ),
    "P6": (
        "the cells held back from the forms map fit inside the forms "
        "that map does not name"
    ),
    "P5": (
        "the cells counted by the figures they wrote after the point "
        "come to the cells that were written with a point"
    ),
}


# -- what the loader returns ------------------------------------------
#
# Typed objects, one per block of the document. Every one is frozen: a
# profile is a description of something that has already happened, and
# nothing downstream has any business editing it. The mappings inside
# (the spelling counts, the repetition patterns) are ordinary
# dictionaries, because their keys are data rather than a fixed set of
# names, and their contents have been checked before they are placed
# here.


@dataclasses.dataclass(frozen=True)
class SourceBlock:
    """How the real table was read (contract 4.3)."""

    encoding: str
    used_fallback_encoding: bool
    header_source: str
    header_by_convention: bool
    header_evidence: str


@dataclasses.dataclass(frozen=True)
class DeclarationRecord:
    """How many values were declared one way, and which of OUR words.

    `n_declared` and `values_recorded` are version 4's, unchanged: how
    many values were named this way, and the standing statement that the
    person's own text is not carried here.

    The two lists are version 5's (contract 5 section 6). They hold
    members of the published vocabulary of that contract's section 14.1
    -- the ten spellings this package reads as "no value" and the three
    stand-in numbers it judges -- and nothing else, so a consumer can
    tell a word this package supplied from a word somebody typed. They
    are a function of the command line alone: a word named but held by
    no cell is recorded exactly as one held by every cell (C5-16), so
    neither list is evidence about the table.
    """

    n_declared: int
    values_recorded: bool
    built_in_texts: "tuple[str, ...]"
    built_in_numbers: "tuple[float, ...]"



@dataclasses.dataclass(frozen=True)
class SettingsBlock:
    """The rules that produced this description (contract 4.4)."""

    small_cell_floor: int
    identifier_uniqueness: float
    identifier_minimum_rows: int
    minimum_parse_rate: float
    categorical_share: float
    categorical_ceiling: int
    categorical_floor: int
    sentinel_outlier_iqr_multiple: float
    sentinel_minimum_share: float
    kept_values: DeclarationRecord
    declared_missing_values: DeclarationRecord
    declaration_matching: str
    declaration_publication: str
    near_threshold_slack: int
    forced_identifiers: "tuple[str, ...]"


@dataclasses.dataclass(frozen=True)
class RelationshipManifest:
    """The eight reserved names, every one of them empty (S12).

    The object carries the eight names rather than eight null fields,
    because eight fields that can only ever be null are eight names a
    consumer has to learn to ignore. What a consumer needs from this
    block is the one fact the loader has already proved: this version of
    synthtwin carries no structure between columns, so a generator's one
    dispatch seam reads `slots`, sees the eight, and generates the
    columns independently (plan P2-D5).
    """

    slots: "tuple[str, ...]"


@dataclasses.dataclass(frozen=True)
class PublicationNote:
    """One plain-language note about what was held back, and why."""

    column: str
    note: str


@dataclasses.dataclass(frozen=True)
class SentinelVerdict:
    """What was decided about one stand-in number, and why."""

    candidate: str
    verdict: str
    reason: str
    n_occurrences: int


@dataclasses.dataclass(frozen=True)
class MissingByClass:
    """Absent cells by the reason each was counted absent (contract 5.4).

    The five keys of the document are five fields here, because the
    document's own key spellings -- `(blank)` and the rest -- are not
    names a program can carry, and a consumer that reads a sixth reason
    should find out where it made the mistake.
    """

    blank: int
    declared_missing: int
    numeric_sentinel: int
    text_code: int
    withheld: int


@dataclasses.dataclass(frozen=True)
class LevelEntry:
    """One published label, its rows, and how those rows wrote it."""

    label: str
    count: int
    variants: "dict[str, int]"
    variants_withheld: "dict[str, int]"


@dataclasses.dataclass(frozen=True)
class NumberLadder:
    """The eleven rungs over the parsed values (contract 5.6).

    `rungs` holds the same eleven values in ladder order, which is what
    a consumer walking the ladder wants; the named fields are what a
    consumer naming one rung wants. `minimum` and `maximum` are the
    document's `min` and `max` (see the module docstring for why they
    are spelled differently here). A rung may be null, meaning the exact
    rung is not a finite value this format can hold, and carrying no
    obligation at that rung (L3).
    """

    rungs: "tuple[float | None, ...]"
    minimum: "float | None"
    p01: "float | None"
    p05: "float | None"
    p10: "float | None"
    p25: "float | None"
    p50: "float | None"
    p75: "float | None"
    p90: "float | None"
    p95: "float | None"
    p99: "float | None"
    maximum: "float | None"


@dataclasses.dataclass(frozen=True)
class DateLadder:
    """The eleven rungs over the ordered instants (contract 5.6).

    No rung of a date ladder is ever null (L3), so every field is text.
    """

    rungs: "tuple[str, ...]"
    minimum: str
    p01: str
    p05: str
    p10: str
    p25: str
    p50: str
    p75: str
    p90: str
    p95: str
    p99: str
    maximum: str


@dataclasses.dataclass(frozen=True)
class LengthStats:
    """The lengths of the present values of a column of text."""

    minimum: int
    maximum: int
    mean: "float | None"
    p50: "float | None"


@dataclasses.dataclass(frozen=True)
class WordStats:
    """The word counts of the present values of a column of text."""

    minimum: int
    maximum: int
    mean: "float | None"


@dataclasses.dataclass(frozen=True)
class EmptyFacts:
    """What an empty column adds to the universal keys: nothing.

    The class exists so that dispatch on the facts object is total: a
    consumer that reaches an empty column finds an object saying so,
    rather than a None it has to test for.
    """


@dataclasses.dataclass(frozen=True)
class UnrepresentableFacts:
    """A column of numbers too large or too small to hold (6.2).

    There is no width fact and no magnitude fact here, and the omission
    is load-bearing: two columns of overflowing values, one about four
    hundred characters wide and one about four thousand, publish
    identically.
    """

    n_whole: int
    n_fraction: int
    n_whole_unknown: int
    n_positive: int
    n_negative: int
    n_sign_unknown: int
    n_distinct_by_occurrences: "dict[str, int]"


@dataclasses.dataclass(frozen=True)
class LabelFacts:
    """The published labels of a constant or binary column (6.3)."""

    levels: "tuple[LevelEntry, ...]"
    suppressed_levels: int
    suppressed_rows: int
    suppressed_level_counts: "tuple[int, ...]"


@dataclasses.dataclass(frozen=True)
class CategoricalFacts(LabelFacts):
    """The published labels of a column of categories (6.6.1).

    `level_ceiling` records the line the column passed and imposes no
    obligation on the twin (G2): it is not a cap the generator has to
    respect, because the generator reproduces counts, not the rule that
    produced them.
    """

    level_ceiling: int


@dataclasses.dataclass(frozen=True)
class DatetimeFacts:
    """A column of dates and times (contract 6.6.2).

    `parser_family` is the document's `format`: the parser family that
    read the REAL file, which the twin does not reproduce -- twin cells
    are written in ISO syntax at the recorded precision, not in the
    source's lexical family.
    """

    parser_family: str
    resolution: str
    time_precision: str
    subsecond_digits: int
    datetimes_read_at: str
    earliest: str
    latest: str
    earliest_utc_offset: str
    latest_utc_offset: str
    date_percentiles: DateLadder
    n_unparsed: int
    utc_offsets: "dict[str, int]"


@dataclasses.dataclass(frozen=True)
class NumericFacts:
    """A column of counts or of continuous values (contract 6.7).

    `n_rows` is the per-column echo of the table's row count, and it is
    a different quantity from the description's own `n_rows`: the
    document-level one carries the row-count obligation and this one
    carries none.
    """

    percentiles: NumberLadder
    mean: "float | None"
    std: "float | None"
    skew: "float | None"
    std_unrepresentable: bool
    n_zero: int
    n_negative: int
    n_negative_unrepresentable: int
    n_used_in_statistics: int
    n_left_out_of_statistics: int
    numeric_share: float
    integer_valued: bool
    n_rows: int
    numeric_styles: "dict[str, int]"
    fraction_widths: "dict[str, int]"


@dataclasses.dataclass(frozen=True)
class IdentifierFacts:
    """A column the person declared to hold record numbers (6.8)."""

    min_length: int
    max_length: int
    all_whole_numbers: bool
    n_all_digits: int
    n_code_alphabet: int
    n_distinct_by_occurrences: "dict[str, int]"


@dataclasses.dataclass(frozen=True)
class TextFacts:
    """A column no rule claimed, publishing none of its values (6.9)."""

    length: LengthStats
    words: WordStats
    n_all_digits: int
    n_code_alphabet: int
    n_distinct_by_occurrences: "dict[str, int]"


@dataclasses.dataclass(frozen=True)
class AffixedFacts:
    """A column of numbers each wearing one shared piece of text.

    TWO POPULATIONS, and they are never the same one. `numbers` holds
    the quantitative block, read over the CORES the cells carry. The
    four `n_core_*` counts answer for those cores. `n_affixed` and
    everything the universal keys count answer for the CELLS.

    The pair is the one place a ranges-class role publishes a spelling
    of the table, and it is confined to these two fields by the
    forbidden-key rule rather than by anybody remembering the
    exception.
    """

    numbers: NumericFacts
    affix_prefix: str
    affix_suffix: str
    n_affixed: int
    n_core_numeric: int
    n_core_out_of_range: int
    n_core_contradictory: int
    n_core_not_numeric: int


@dataclasses.dataclass(frozen=True)
class ClockFacts:
    """A column of clock times (contract section 6, the clock role).

    FIVE FACTS AND NO SIXTH: which of the two forms the cells wore, the
    earliest and latest value, the eleven-rung ladder over the values
    that parsed, and how many present cells no clock reading accepted.

    Every clock value here is written in the form `clock_form` names,
    two digits a field. The ladder is SELECTION -- eleven order
    statistics of cells the column really holds -- so its two ends ARE
    the endpoints, which the loader checks rather than assumes.
    """

    clock_form: str
    earliest: str
    latest: str
    clock_percentiles: "dict[str, str]"
    n_unparsed: int


ColumnFacts = (
    EmptyFacts
    | UnrepresentableFacts
    | LabelFacts
    | DatetimeFacts
    | NumericFacts
    | IdentifierFacts
    | TextFacts
    | AffixedFacts
    | ClockFacts
)


@dataclasses.dataclass(frozen=True)
class ColumnBlock:
    """One column of the table, described (contract section 5).

    The universal facts are fields here; everything the ROLE adds is in
    `facts`, whose type says which role this is. A consumer dispatches
    on the three axes -- `statistical_type`, `quality_state` and
    `structural_role` -- rather than on `role`, because the axes are the
    three questions the generator actually asks (plan P2-D3).
    """

    name: str
    position: int
    role: str
    statistical_type: str
    quality_state: str
    structural_role: str
    n_present: int
    n_missing: int
    missing_by_class: MissingByClass
    missing_by_source: "dict[str, int]"
    # The two counts version 4 kept inside `missing_by_source` under
    # this package's own two words (contract 5 section 5). How many
    # absent cells held nothing but space -- zero unless at least the
    # floor did -- and how many wore a spelling, or a blankness, that
    # fewer than the floor shared.
    n_missing_blank: int
    n_missing_withheld: int
    n_distinct: int
    n_distinct_folded: int
    n_numeric: int
    n_not_numeric: int
    n_out_of_range: int
    n_contradictory: int
    n_sentinel_candidates_unpublished: int
    sentinel_verdicts: "tuple[SentinelVerdict, ...]"
    detection_evidence: str
    remarks: "tuple[str, ...]"
    facts: ColumnFacts


@dataclasses.dataclass(frozen=True)
class Profile:
    """A whole conforming version 5 description (contract 10.8).

    `columns` is in the document's own list order, which IS the schema
    order, the order the twin's columns are written in, and the order
    the one random stream is consumed in (S3). Every consumer walks it
    in that order.
    """

    profile_version: int
    created_with: str
    n_rows: int
    n_columns: int
    source: SourceBlock
    settings: SettingsBlock
    relationships: RelationshipManifest
    publication_notes: "tuple[PublicationNote, ...]"
    columns: "tuple[ColumnBlock, ...]"


@dataclasses.dataclass(frozen=True)
class _Frame:
    """The facts a column block is checked against, gathered once."""

    floor: int
    n_rows: int
    n_columns: int
    declared: "tuple[str, ...]"
    # The share a role's detection line is drawn at, carried here
    # because one invariant is stated over it: AF3 holds an affixed
    # column's pair to the line its own detection had to clear, and a
    # loader without the setting could not check it at all.
    parse_rate: float


# -- reading the file -------------------------------------------------


def _read_text(place: pathlib.Path) -> str:
    """Read the whole file as UTF-8 text.

    Guarantees: accepts a path that has already passed
    `validate_local_path`; returns the file's text. Determinism: the
    same bytes always give the same text. Raises UnicodeDecodeError when
    the bytes are not UTF-8, OSError when the file cannot be read, and
    MemoryError when the machine cannot hold it -- each of which the
    caller turns into a refusal written for a person.

    Boundary: this is the only place in the generation path that opens
    anything, and the only thing it opens is the description file.

    It is a function of its own, and called through this module's own
    name, so that the two failures a test cannot arrange on a real
    filesystem -- no permission, and no memory -- have somewhere to be
    stood in front of.

    The path is rebuilt here rather than used as it arrives, which is
    the shape the offline audit reads: a value an allowlisted API built
    is a value whose methods that audit has already checked, and a
    parameter is not (plan D6.2).
    """
    file_path = pathlib.Path(place)
    return file_path.read_text(encoding="utf-8")


def _file_size(place: pathlib.Path) -> int:
    """How many bytes the file holds.

    Guarantees: accepts a path; returns its size in bytes. Raises
    OSError when the size cannot be read. No value of any table is
    consulted.
    """
    file_path = pathlib.Path(place)
    return int(file_path.stat().st_size)


def _is_plain_ascii(text: str) -> bool:
    """True when every character of ``text`` is ASCII.

    Guarantees: accepts text; returns a truth value; raises TypeError if
    handed anything that is not a string instance. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a document was not text")
    return text.isascii()


def _utf8_length(text: str) -> int:
    """How many bytes ``text`` takes when written as UTF-8.

    WHY THIS EXISTS, because it looks like arithmetic nobody needs. The
    contract requires the round trip to compare BYTES, and the only
    reading call this code is permitted to make translates line endings
    on the way in: a file written with carriage returns arrives as text
    with none, so a text-only comparison would accept a file whose bytes
    are not the ones synthtwin writes. Comparing the byte LENGTH as well
    closes that, because equal text plus equal byte length leaves only
    one possible byte sequence -- UTF-8 is a one-to-one encoding of text
    that is not a lone surrogate, and translation is the only step that
    can change the text without changing the file.

    Guarantees: accepts text; returns the number of bytes; raises
    TypeError if handed anything that is not a string instance. The
    all-ASCII case, which is nearly every description, costs one call.
    No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a document was not text")
    if _is_plain_ascii(text):
        return len(text)
    total = 0
    for character in text:
        point = ord(character)
        if point < 0x80:
            total = total + 1
        elif point < 0x800:
            total = total + 2
        elif point < 0x10000:
            total = total + 3
        else:
            total = total + 4
    return total


def _holds_a_lone_surrogate(text: str) -> bool:
    """True when ``text`` holds a character that is not writable text.

    A lone surrogate cannot be written as UTF-8 at all. It cannot arrive
    by decoding a file either, so the only way one reaches a parsed
    document is an escape sequence written into the file by hand, which
    is exactly the case R6 names.

    Guarantees: accepts text; returns a truth value; raises TypeError if
    handed anything that is not a string instance. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a document was not text")
    if _is_plain_ascii(text):
        return False
    for character in text:
        point = ord(character)
        if 0xD800 <= point <= 0xDFFF:
            return True
    return False


def _begins_a_number(character: str) -> bool:
    """True when a numeric token can begin at this character."""
    return character == "-" or ("0" <= character <= "9")


def _continues_a_number(character: str) -> bool:
    """True when this character can continue a numeric token."""
    if "0" <= character <= "9":
        return True
    return (
        character == "."
        or character == "e"
        or character == "E"
        or character == "+"
        or character == "-"
    )


def _scanned(text: str, shown: str) -> None:
    """Check the two parser bounds, before anything parses (10.3).

    Guarantees:

    - Inputs: the document's text and the path to name in a refusal.
    - Determinism: the answer depends only on the text.
    - Errors raised: ProfileError when the text nests deeper than
      `MAXIMUM_DEPTH` (R8) or holds a numeric token longer than
      `MAXIMUM_NUMBER_CHARACTERS` characters (R9). Nothing else: this is
      not a parser and it does not decide whether the text is JSON.
    - Boundary: string operations only. No parse, no callback, no
      allocation that grows with the document.

    The scan is string-literal aware, because a brace inside a quoted
    value is a character of that value and not a level of nesting: a
    quotation mark outside a string opens one and one inside closes it,
    unless an odd number of backslashes precedes it, and inside a string
    nothing counts at all.
    """
    depth = 0
    deepest = 0
    inside = False
    escaped = False
    token = 0
    for character in text:
        if inside:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                inside = False
            continue
        if character == '"':
            inside = True
            token = 0
            continue
        if character == "{" or character == "[":
            depth = depth + 1
            deepest = max(deepest, depth)
            if deepest > MAXIMUM_DEPTH:
                raise errors.ProfileError(
                    errors.profile_nested_too_deeply(shown, MAXIMUM_DEPTH)
                )
            token = 0
            continue
        if character == "}" or character == "]":
            depth = depth - 1
            token = 0
            continue
        if token:
            if _continues_a_number(character):
                token = token + 1
                if token > MAXIMUM_NUMBER_CHARACTERS:
                    raise errors.ProfileError(
                        errors.profile_number_too_long(
                            shown, MAXIMUM_NUMBER_CHARACTERS
                        )
                    )
                continue
            token = 0
            continue
        if _begins_a_number(character):
            token = 1


def _parsed(text: str, shown: str) -> object:
    """Parse the text with a plain JSON parse (step 4).

    Guarantees:

    - Inputs: the document's text and the path to name in a refusal.
    - Determinism: the same text always gives the same value.
    - Errors raised: ProfileError naming where the parse stopped when
      the text is not JSON (R5).
    - Boundary: NO CALLBACK SLOT IS FILLED. `json.loads` is called with
      the text and nothing else -- no object hook, no pairs hook, no
      parse hook of any kind -- because the offline policy forbids
      handing a callable to a library API (plan D6.2), and because the
      duplicate keys a pairs hook is usually reached for are caught by
      the canonical round trip instead.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise errors.ProfileError(
            errors.profile_not_json(shown, error.lineno, error.colno)
        ) from error


def _versioned(parsed: object, shown: str) -> "dict[str, object]":
    """Check `profile_version` is exactly 5, before anything else (10.6).

    Guarantees:

    - Inputs: the parsed value and the path to name in a refusal.
    - Determinism: the answer depends only on the parsed value.
    - Errors raised: ProfileError when the whole document is not a block
      of named entries (R15), when it has no `profile_version` (R14),
      when that value is not a whole number (R15), when it is older than
      this loader reads (R11), and when it is newer (R12).
    - Boundary: nothing is opened and no other key is read.

    The two version messages differ on purpose and the difference is the
    whole point. An older description is made again by re-running
    `synthtwin profile`, which is safe advice because the person holding
    an old description of their own table is normally the person holding
    the table -- and from version 5 that message also says WHY the older
    file cannot be read and asks for the same declarations back, because
    a description re-made without them reads the table differently
    (contract 5 C5-26). A NEWER description means this synthtwin is
    behind, and
    the advice is to update synthtwin and never to re-run a profiler:
    that advice would be given to somebody who may not hold the table at
    all, and cannot be followed while looking as though it can.
    """
    if not isinstance(parsed, dict):
        raise errors.ProfileError(
            errors.profile_wrong_type(
                "the description",
                "in this file",
                _kind(parsed),
                "a block of named entries",
            )
        )
    if "profile_version" not in parsed:
        raise errors.ProfileError(
            errors.profile_missing_key(
                "profile_version",
                _AT_THE_TOP,
                "every description synthtwin writes",
            )
        )
    stated = parsed["profile_version"]
    if isinstance(stated, bool) or not isinstance(stated, int):
        raise errors.ProfileError(
            errors.profile_wrong_type(
                "profile_version",
                _AT_THE_TOP,
                _kind(stated),
                "a whole number",
            )
        )
    if stated < PROFILE_VERSION:
        raise errors.ProfileError(
            errors.profile_version_is_older(stated, PROFILE_VERSION)
        )
    if stated > PROFILE_VERSION:
        raise errors.ProfileError(
            errors.profile_version_is_newer(stated, PROFILE_VERSION)
        )
    return parsed


def _round_tripped(
    document: "dict[str, object]", text: str, size: int, shown: str
) -> None:
    """Require the file to be exactly the bytes synthtwin writes (10.4).

    Guarantees:

    - Inputs: the parsed document, the file's text, the file's size in
      bytes, and the path to name in a refusal.
    - Determinism: the canonical text is a function of the parsed value
      alone.
    - Errors raised: ProfileError when a value cannot be written as
      canonical text because it is not a number (R7), when the document
      holds a character that cannot be written as text at all (R6), and
      when the canonical text is not what the file holds (R10).
    - Boundary: nothing is opened; the serializer reaches nothing but
      `json`.

    ONE CHECK CATCHES SEVEN DEFECTS, each verified before being relied
    on: a duplicated key (the parse keeps one value, so writing it again
    gives shorter text), keys in any order but ascending, a non-canonical
    number spelling such as `1.0e2` or `05`, any indentation or
    separator but the canonical one, the three non-finite numbers a
    plain parse accepts, an escaped lone surrogate, and a missing or
    extra terminal newline. No callback slot is involved in any of it.
    """
    try:
        rewritten = canonical.serialize(document)
    except ValueError as error:
        raise errors.ProfileError(
            errors.profile_holds_a_number_that_is_not_one(shown)
        ) from error
    if _holds_a_lone_surrogate(rewritten):
        raise errors.ProfileError(
            errors.profile_holds_unwritable_text(shown)
        )
    if rewritten != text:
        raise errors.ProfileError(errors.profile_not_canonical(shown))
    if _utf8_length(rewritten) != size:
        raise errors.ProfileError(errors.profile_not_canonical(shown))


# -- the small checks every rule is built from ------------------------

_AT_THE_TOP = "at the top of the description"


def _kind(value: object) -> str:
    """What kind of value this is, in words a person reads.

    A refusal says what was found, never the value itself: a value of
    the wrong kind is quoted nowhere, because the thing that is wrong is
    its kind.
    """
    if value is None:
        return "nothing at all"
    if isinstance(value, bool):
        return "a yes or no value"
    if isinstance(value, int):
        return "a whole number"
    if isinstance(value, float):
        return "a number with a fractional part"
    if isinstance(value, str):
        return "a piece of text"
    if isinstance(value, list):
        return "a list"
    if isinstance(value, dict):
        return "a block of named entries"
    return "a kind of value synthtwin does not know"


def _listed(items: "tuple[str, ...]") -> str:
    """Join items with commas for a message, without calling join().

    The offline policy accepts a text method only when every argument is
    a value it has resolved, and a list built while the program runs is
    not one (plan D6.2).
    """
    text = ""
    for item in items:
        piece = f"'{item}'"
        if not text:
            text = piece
        else:
            text = f"{text}, {piece}"
    return text


def _unknown(key: str, where: str) -> "errors.ProfileError":
    """R13: a key this version of synthtwin does not know."""
    return errors.ProfileError(errors.profile_unknown_key(key, where))


def _missing(key: str, where: str, required_by: str) -> "errors.ProfileError":
    """R14: a key that every block of this kind has."""
    return errors.ProfileError(
        errors.profile_missing_key(key, where, required_by)
    )


def _wrong_type(
    key: str, where: str, value: object, required: str
) -> "errors.ProfileError":
    """R15: a key holding a kind of value it may not hold."""
    return errors.ProfileError(
        errors.profile_wrong_type(key, where, _kind(value), required)
    )


def _out_of_range(
    key: str, where: str, shown: str, permitted: str
) -> "errors.ProfileError":
    """R16: a value outside its range or its list of allowed values."""
    return errors.ProfileError(
        errors.profile_out_of_range(key, where, shown, permitted)
    )


def _row_count_out_of_range(
    key: str, where: str, permitted: str
) -> "errors.ProfileError":
    """R16 for a row count, whose value is deliberately not shown.

    No message on this path quotes a row count (contract 10.7): reading
    a description can run out of memory before any field has been
    checked, and a message that names a row count it never read is a
    message that lies. The rule is applied to every row count, valid or
    not, so that there is no case to get wrong.
    """
    return errors.ProfileError(
        errors.profile_out_of_range_unquoted(key, where, permitted)
    )


def _broken(
    rule: str, where: str, first: str, second: str
) -> "errors.ProfileError":
    """R17: an invariant of the contract that this document breaks.

    ``rule`` is the contract's own identifier for it; the words a person
    reads come from INVARIANTS above, so that a rule is worded in one
    place. ``first`` and ``second`` are the two quantities that disagree
    and where each of them lives.
    """
    return errors.ProfileError(
        errors.profile_invariant_broken(
            rule, INVARIANTS[rule], where, first, second
        )
    )


def _mapping(value: object, key: str, where: str) -> "dict[str, object]":
    """The value under ``key``, required to be a block of entries."""
    if not isinstance(value, dict):
        raise _wrong_type(key, where, value, "a block of named entries")
    return value


def _listing(value: object, key: str, where: str) -> "list[object]":
    """The value under ``key``, required to be a list."""
    if not isinstance(value, list):
        raise _wrong_type(key, where, value, "a list")
    return value


def _text(value: object, key: str, where: str) -> str:
    """The value under ``key``, required to be text."""
    if not isinstance(value, str):
        raise _wrong_type(key, where, value, "a piece of text")
    return value


def _filled_text(value: object, key: str, where: str) -> str:
    """The value under ``key``, required to be text with something in it."""
    found = _text(value, key, where)
    if not parsing.trimmed(found):
        raise _out_of_range(
            key, where, "nothing but spaces", "a piece of text with words in it"
        )
    return found


def _truth(value: object, key: str, where: str) -> bool:
    """The value under ``key``, required to be a yes or no value.

    A yes or no value is not a whole number here, and a whole number is
    not a yes or no value: in several host languages one is a kind of
    the other, and this contract keeps them apart (T2).
    """
    if not isinstance(value, bool):
        raise _wrong_type(key, where, value, "a yes or no value")
    return value


def _whole(value: object, key: str, where: str, least: int) -> int:
    """The value under ``key``, required to be a whole number at least ``least``.

    A whole number is a JSON integer and nothing else: `2.0` is refused
    where `2` is required (T1), because `2.0` survives the canonical
    round trip unchanged and so cannot be caught anywhere else.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise _wrong_type(key, where, value, "a whole number")
    if value < least:
        raise _out_of_range(
            key, where, f"{value}", f"a whole number of {least} or more"
        )
    return value


def _bounded(
    value: object, key: str, where: str, least: int, most: int, ceiling: str
) -> int:
    """A whole number from ``least`` to ``most``, ``ceiling`` naming the top."""
    found = _whole(value, key, where, least)
    if found > most:
        raise _out_of_range(
            key,
            where,
            f"{found}",
            f"a whole number of {least} or more, and no more than {ceiling}",
        )
    return found


def _figure(value: object, key: str, where: str) -> float:
    """The value under ``key``, required to be a number.

    Guarantees: both kinds of canonical number are accepted and read
    the same way (contract T3 and 3.2.1). A mean of exactly two reads
    `2.0` when the producer held it as a fraction-bearing number, which
    is what this producer does, and `2` when it held it as a whole
    number; refusing either would refuse a conforming description.
    Raises the wrong-type refusal for anything that is not a number,
    booleans included (T2).
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _wrong_type(key, where, value, "a number")
    return float(value)


def _share(value: object, key: str, where: str) -> float:
    """A number from zero to one, as a share of something is."""
    found = _figure(value, key, where)
    if found < 0.0 or found > 1.0:
        raise _out_of_range(
            key, where, f"{found}", "a number from 0 to 1"
        )
    return found


def _figure_or_nothing(
    value: object, key: str, where: str
) -> "float | None":
    """A number, or nothing at all where the exact value is not one.

    Null is a value here and not an absence: the key is still present
    (T4), and a key that is absent is a missing key, never a null.
    """
    if value is None:
        return None
    return _figure(value, key, where)


def _one_of(
    value: object, key: str, where: str, permitted: "tuple[str, ...]"
) -> str:
    """The value under ``key``, required to be one of ``permitted``."""
    found = _text(value, key, where)
    if found not in permitted:
        raise _out_of_range(key, where, f"'{found}'", _listed(permitted))
    return found


def _keys(
    mapping: "dict[str, object]",
    where: str,
    required: "tuple[str, ...]",
    required_by: str,
) -> None:
    """Require exactly these keys: no others, and none of them absent.

    Unknown keys are reported before missing ones, because a document
    carrying a key this synthtwin does not know is usually a document a
    newer synthtwin wrote, and that is the more useful thing to say
    first.
    """
    for key in sorted(mapping):
        if key not in required:
            raise _unknown(key, where)
    for key in required:
        if key not in mapping:
            raise _missing(key, where, required_by)


# How an entry of a table-keyed mapping is named on the screen when the
# value under it is wrong (review item P3-V11-F2). The key itself is a
# spelling some cell of the table held, character for character, so it
# is named by WHAT IT IS and never quoted -- the same rule R15 already
# follows for the value it found.
_A_SPELLING_OF_YOURS = "(a spelling out of your own table)"

# The two places the format lets the table decide a mapping's keys, in
# the shape `canonical` writes them. They are not a second list: the
# suite holds them to `canonical.TABLE_TEXT_KEY_SPACES` itself, and that
# tuple is in turn derived from the producer's publication rules.
_THE_SOURCE_KEYS = ("columns", canonical.EACH, "missing_by_source")
_THE_VARIANT_KEYS = (
    "columns", canonical.EACH, "levels", canonical.EACH, "variants"
)


def _entry_named(path: "tuple[object, ...]", key: str, name: str) -> str:
    """How one entry of a block is named in a refusal about its value.

    THE DEFECT THIS EXISTS FOR (review item P3-V11-F2). The wrong-type
    and out-of-range refusals name the entry by its own key, which is
    right everywhere the format keys a mapping on one of synthtwin's own
    published words -- a percentile name, a UTC offset, a numeric style,
    a group size in figures. In the two mappings `canonical` names it is
    wrong: the key is a spelling out of somebody's table, and the
    earlier repair for review item P3-V10-F3 stopped the S13 walk from
    printing one while leaving the ORDINARY wrong-type path printing it
    verbatim, which is the same disclosure through the other door.

    The answer comes from the one key-space table both halves of the
    product already share, so a mapping added to the format with the
    table's text for keys is covered the moment it is named there.

    Guarantees:

    - Inputs: the path of the MAPPING, its field name as a person reads
      it, and the key standing inside it.
    - Determinism: a fixed function of the path and of `canonical`'s
      table; the key's own characters change nothing but whether they
      are shown.
    - Errors raised: none.
    - Boundary: where the table decides the keys, no character of the
      key reaches the answer.
    """
    if canonical.keys_are_the_tables_own_text(path):
        return f"{key} -> {_A_SPELLING_OF_YOURS}"
    return f"{key} -> {name}"


def _counts(
    value: object,
    key: str,
    where: str,
    least: int,
    path: "tuple[object, ...]" = (),
) -> "dict[str, int]":
    """A block of entries whose values are whole numbers of ``least`` up.

    ``path`` is where this mapping sits in the document, and it is what
    decides whether an entry may be named by its own key: a mapping the
    TABLE keys is named by what its keys are and never by one of them
    (review item P3-V11-F2). The default is the empty path, which no
    key space holds, so a caller that names no path gets the ordinary
    naming -- and every caller whose mapping is table-keyed passes one.
    `tests/test_p3v11f2_no_refusal_quotes_your_spelling.py` holds every
    caller in this module to that, from `canonical`'s own table.
    """
    mapping = _mapping(value, key, where)
    counted: dict[str, int] = {}
    for name in sorted(mapping):
        counted[name] = _whole(
            mapping[name], _entry_named(path, key, name), where, least
        )
    return counted


def _added(counted: "dict[str, int]") -> int:
    """The sum of a block of counts."""
    total = 0
    for name in sorted(counted):
        total = total + counted[name]
    return total


def _below_the_floor(floor: int) -> range:
    """The group sizes this floor holds back: 1 up to the floor.

    THE FLOOR HAS TWO HALVES AND THIS NAMES THE SECOND ONE. Every
    floor-governed rule of the contract is written as "at least the
    floor" and "below the floor"; B5, N2, N4, D3, P2, V1 and W5 are the
    first half, and everything a description pools, suppresses or counts
    unnamed is the second. At a floor of one this range is EMPTY, which
    is not a corner case to be handled but the whole of invariant S13:
    there is no group below one, so a description written at that floor
    has nothing to hold back and holds nothing back (owner ruling
    2026-08-14, plan amendment A-P3-11 clause 1, amended by A-P3-16).

    It is a `range` rather than a pair of numbers so that "is this size
    held back" and "is anything held back at all" are the same question
    asked two ways -- `size in _below_the_floor(floor)` and the
    emptiness of the range itself -- and neither can drift from the
    other.
    """
    return range(1, floor)


def _all_digits(text: str) -> bool:
    """True when ``text`` is one or more ASCII digits and nothing else."""
    if not text:
        return False
    for character in text:
        if not ("0" <= character <= "9"):
            return False
    return True


def _digits_at(text: str, start: int, count: int) -> bool:
    """True when ``count`` ASCII digits stand at ``start`` in ``text``."""
    return _all_digits(text[start : start + count])


# -- the multiplicity map, one shape used in three places -------------


def occurrence_size(key: str) -> "int | None":
    """A multiplicity map's key, read as the row count it names (G9.5).

    THE KEY IS DECIMAL TEXT AND IT IS READ AS DECIMAL TEXT. This is the
    one reader for it, and it exists because the alternative kept coming
    back: a key handed to a reader that answers in binary64 is a key
    rounded to the nearest number that format holds, and a row count is
    not a number that format holds past nine quadrillion. The key
    `'9007199254740993'` reads back as `9007199254740992` through such a
    reader -- one row short -- and one row short is one group more when
    a band's cells are divided by it, which is how a description ten
    spellings answer exactly came to be refused as needing eleven
    (review item P3-V8-F5). Leading zeros are padding that does not
    change the number, which `int` already knows.

    Guarantees:

    - Inputs: one key of a map `_multiplicity` admitted, or any text.
    - Determinism: a pure function of the text; the answer is exact at
      every size, because Python's whole numbers are.
    - Errors raised: none. Text that is not a row count returns None,
      and each caller says in its own words which way that leaves it --
      the safe direction differs between a refusal and a corner, so it
      is decided there and not here.
    - Boundary: no I/O, no float, and nothing of the measured file.

    This is what `_multiplicity` itself reads the key with when it
    admits it (`rows = int(name)` above the range check), so a caller
    reading it again here gets the same number the loader checked.
    """
    if not isinstance(key, str):
        return None
    if not _all_digits(key):
        return None
    return int(key)


def _multiplicity(
    value: object,
    key: str,
    where: str,
    floor: "int | None",
) -> "tuple[dict[str, int], list[tuple[int, int]]]":
    """A repetition pattern: how many things covered how many rows (5.3).

    Guarantees:

    - Inputs: the value under ``key``, where it lives, and the top of
      the permitted key range -- `floor - 1` where the floor governs the
      pattern (a held-back spelling, W5), or None where nothing bounds
      it (a column's own repetition pattern).

      A TOP OF ZERO IS A REAL CASE AND IT MEANS "EMPTY" (owner ruling
      2026-08-14, plan amendment A-P3-11). A description made with a
      smallest group size of one holds nothing back, so a floor-governed
      pattern under it has no permitted key at all. The refusal says
      that in those words: "a number of rows from 1 to 0" would send a
      person looking for a number that cannot exist.
    - Determinism: the answer depends only on the value.
    - Errors raised: ProfileError when it is not a block of entries
      (R15), when a key is not a row count written in base ten or is
      outside the permitted range (R16), when the keys are not all
      written to the width of the largest of them (M3), or when an entry
      counts nothing (M4).
    - Boundary: no value of the table reaches it -- the pattern is a
      function of the group SIZES alone.

    Returns the mapping exactly as the document writes it, together with
    its entries read as (rows covered, how many things covered that
    many), which is what the sums M1 and M2 are checked against.

    The keys are padded with zeros to a common width on purpose: written
    bare, `"10"` sorts before `"2"`, and the document's keys are sorted.
    """
    mapping = _mapping(value, key, where)
    kept: dict[str, int] = {}
    pairs: list[tuple[int, int]] = []
    width = 0
    largest = 0
    for name in sorted(mapping):
        if not _all_digits(name):
            raise _out_of_range(
                f"{key} -> {name}",
                where,
                f"'{name}'",
                "a number of rows written in figures",
            )
        rows = int(name)
        top = "a number of rows of 1 or more"
        if floor is not None:
            top = f"a number of rows from 1 to {floor}"
        if floor is not None and floor < 1:
            top = (
                "no entry at all -- this description was made with a "
                "smallest group size of 1, so nothing was held back and "
                "this block is empty"
            )
        if rows < 1 or (floor is not None and rows > floor):
            raise _out_of_range(f"{key} -> {name}", where, f"{rows}", top)
        if width and len(name) != width:
            raise _broken(
                "M3",
                where,
                f"the entry '{name}' of {key} is {len(name)} characters wide",
                f"another entry of it is {width} characters wide",
            )
        width = len(name)
        largest = max(largest, rows)
        kept[name] = _whole(mapping[name], f"{key} -> {name}", where, 0)
        if kept[name] < 1:
            raise _broken(
                "M4",
                where,
                f"the entry for {rows} row(s) of {key} counts nothing",
                "a size that covered nothing has no entry at all",
            )
        pairs = pairs + [(rows, kept[name])]
    if largest and width != len(f"{largest}"):
        raise _broken(
            "M3",
            where,
            f"the entries of {key} are {width} characters wide",
            f"the largest of them, {largest}, needs {len(f'{largest}')}",
        )
    return kept, pairs


def _multiplicity_totals(
    pairs: "list[tuple[int, int]]",
) -> "tuple[int, int]":
    """(how many things the pattern describes, how many rows they cover)."""
    things = 0
    rows = 0
    for covered, howmany in pairs:
        things = things + howmany
        rows = rows + covered * howmany
    return things, rows


# -- the eleven rungs ------------------------------------------------


def _number_ladder(
    value: object, key: str, where: str
) -> NumberLadder:
    """The eleven rungs of a column of numbers (contract 5.6).

    Guarantees: accepts the value under ``key``; returns the ladder as a
    typed object. Raises ProfileError when it is not a block of entries
    (R15), when its keys are not exactly the eleven rungs (L4), when a
    rung is neither a number nor null (R15), or when the rungs go down
    somewhere along the ladder (L1). A null rung carries no obligation
    and is skipped by the comparison rather than treated as a value.
    """
    mapping = _mapping(value, key, where)
    _keys(mapping, where, LADDER_KEYS, "every ladder of numbers")
    rungs: list[float | None] = []
    previous: float | None = None
    previous_name = ""
    for name in LADDER_KEYS:
        rung = _figure_or_nothing(mapping[name], f"{key} -> {name}", where)
        rungs = rungs + [rung]
        if rung is None:
            continue
        if previous is not None and rung < previous:
            raise _broken(
                "L1",
                where,
                f"the rung '{previous_name}' of {key} is {previous}",
                f"the rung '{name}' after it is {rung}",
            )
        previous = rung
        previous_name = name
    return NumberLadder(
        rungs=tuple(rungs),
        minimum=rungs[0],
        p01=rungs[1],
        p05=rungs[2],
        p10=rungs[3],
        p25=rungs[4],
        p50=rungs[5],
        p75=rungs[6],
        p90=rungs[7],
        p95=rungs[8],
        p99=rungs[9],
        maximum=rungs[10],
    )


def _date_ladder(
    value: object, key: str, where: str, resolution: str
) -> DateLadder:
    """The eleven rungs of a column of dates (contract 5.6).

    Guarantees: accepts the value under ``key`` and the form the dates
    are published in; returns the ladder as a typed object. Raises
    ProfileError when it is not a block of entries (R15), when its keys
    are not exactly the eleven rungs (L4), when a rung is not text (L3
    -- a rung of a date ladder is never null), when a rung is not in the
    canonical form for this resolution (R16), or when the rungs go down
    (L1). The comparison is plain text comparison, which is why the
    canonical forms are chosen to sort as text.
    """
    mapping = _mapping(value, key, where)
    _keys(mapping, where, LADDER_KEYS, "every ladder of dates")
    rungs: list[str] = []
    previous = ""
    previous_name = ""
    for name in LADDER_KEYS:
        rung = mapping[name]
        if rung is None:
            raise _broken(
                "L3",
                where,
                f"the rung '{name}' of {key} holds nothing",
                "a ladder of dates has a date at every rung",
            )
        found = _canonical_datetime(rung, f"{key} -> {name}", where, resolution)
        rungs = rungs + [found]
        if previous and found < previous:
            raise _broken(
                "L1",
                where,
                f"the rung '{previous_name}' of {key} is {previous}",
                f"the rung '{name}' after it is {found}",
            )
        previous = found
        previous_name = name
    return DateLadder(
        rungs=tuple(rungs),
        minimum=rungs[0],
        p01=rungs[1],
        p05=rungs[2],
        p10=rungs[3],
        p25=rungs[4],
        p50=rungs[5],
        p75=rungs[6],
        p90=rungs[7],
        p95=rungs[8],
        p99=rungs[9],
        maximum=rungs[10],
    )


def _canonical_datetime(
    value: object, key: str, where: str, resolution: str
) -> str:
    """One instant in the canonical form its resolution fixes (6.6.2).

    The three forms are `YYYY-MM-DD`, `YYYY-MM-DD HH:MM:SS` and
    `YYYY-Qn`, and all three sort correctly as plain text. Both the
    SHAPE and the RANGES are checked -- how many characters, which of
    them are figures, where the separators stand, AND that the fields
    name an instant the calendar and the clock have.

    THE RANGES ARE PART OF THE CONTRACT, not decoration (review item
    P2-C1-F6). A published instant is a fact a twin has to be able to
    write back unchanged, and a month of 99 is not one: the generator
    works in whole days and seconds from these fields, so an impossible
    field would be carried silently into a real-looking date somewhere
    else in the calendar. The producer never writes one -- the shipped
    date reader refuses a 31st of February before the value reaches a
    description at all -- so this refuses nothing a description can
    honestly carry.

    The one place this is wider than a wall clock is the second, which
    may be 60: a leap second is a real reading a real table can hold,
    the shipped reader accepts it, and refusing it here would make a
    description the producer wrote unloadable. Accepting it obliges the
    other end to write it back, and it does -- an end of a column of
    dates is written from the published instant's own fields, so both
    ends stay exact facts (review item P2-C2-F5). Where it is accepted
    it is written back: D10 refuses the one clock no cell can show a
    sixtieth second on, rather than accepting such a column and then
    reporting the end as a loss (review item P2-C3-F2).
    """
    found = _text(value, key, where)
    if resolution == "quarter":
        wanted = "a quarter written like 2024-Q1"
        good = (
            len(found) == 7
            and _digits_at(found, 0, 4)
            and found[4] == "-"
            and found[5] == "Q"
            and "1" <= found[6] <= "4"
        )
    elif resolution == "datetime":
        wanted = (
            "a date and time the calendar and the clock have, written "
            "like 2024-03-15 14:05:00"
        )
        good = (
            len(found) == 19
            and _is_a_date(found)
            and found[10] == " "
            and _digits_at(found, 11, 2)
            and found[13] == ":"
            and _digits_at(found, 14, 2)
            and found[16] == ":"
            and _digits_at(found, 17, 2)
            and _is_a_clock(found[11:13], found[14:16], found[17:19])
        )
    else:
        wanted = "a date the calendar has, written like 2024-03-15"
        good = len(found) == 10 and _is_a_date(found)
    if not good:
        raise _out_of_range(key, where, f"'{found}'", wanted)
    return found


_DAYS_IN_MONTH = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def _is_a_date(text: str) -> bool:
    """True when the first ten characters read a real `YYYY-MM-DD`.

    The shape and the calendar, in one question, because a description
    that carries a 31st of February carries a date no twin cell can be
    written as. The leap rule is the Gregorian one the shipped reader
    uses: a year divisible by four is a leap year, except a century not
    divisible by four hundred.
    """
    shaped = (
        _digits_at(text, 0, 4)
        and text[4] == "-"
        and _digits_at(text, 5, 2)
        and text[7] == "-"
        and _digits_at(text, 8, 2)
    )
    if not shaped:
        return False
    year = int(text[0:4])
    month = int(text[5:7])
    day = int(text[8:10])
    if year < 1 or month < 1 or month > 12 or day < 1:
        return False
    limit = _DAYS_IN_MONTH[month - 1]
    if month == 2 and (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
        limit = 29
    return day <= limit


def _is_a_clock(hours: str, minutes: str, seconds: str) -> bool:
    """True when three two-figure fields name a time of day.

    Hours run to 23 and minutes to 59. Seconds run to 60, and the extra
    one is deliberate: a leap second is a reading a real table can hold
    and the shipped date reader accepts it, so a description may carry
    one.
    """
    return int(hours) <= 23 and int(minutes) <= 59 and int(seconds) <= 60


def _is_an_offset(text: str) -> bool:
    """True when ``text`` is one of the four forms an offset takes.

    `Z`; `(none)` for a cell that carried no offset; `(withheld)` for
    the pooled remainder; or a signed offset in the form the contract's
    own examples fix, `+02:00` and `-05:00`. The producer writes the
    signed form and no other, so this is the shape a generator can
    expect to be able to read back.

    THE RANGE IS CHECKED, NOT ONLY THE SHAPE (review item P2-C1-F6). No
    zone stands further than fourteen hours from UTC and no zone's
    minute field reaches sixty, and the generator does whole-second
    arithmetic with these two fields, so `+99:99` would move a written
    cell to an instant no offset could ever produce. These are exactly
    the bounds the shipped date reader enforces, so every offset the
    producer can publish is accepted here.
    """
    if text == "Z" or text == NO_OFFSET or text == WITHHELD:
        return True
    shaped = (
        len(text) == 6
        and (text[0] == "+" or text[0] == "-")
        and _digits_at(text, 1, 2)
        and text[3] == ":"
        and _digits_at(text, 4, 2)
    )
    if not shaped:
        return False
    hours = int(text[1:3])
    minutes = int(text[4:6])
    if hours > 14 or minutes > 59:
        return False
    return not (hours == 14 and minutes != 0)


# -- the top-level blocks ---------------------------------------------


def _source(value: object) -> SourceBlock:
    """The five keys saying how the table was read (contract 4.3).

    Guarantees: accepts the value under `source`; returns it as a typed
    object. Raises ProfileError for an unknown or missing key, a wrong
    type, a value outside its list, and for either of the two
    invariants: S5, which ties the fallback flag to the encoding it
    names, and S6, which refuses a first row taken as names by
    convention when the names did not come from the file at all --
    generated names are not a convention about somebody's first record;
    they are names synthtwin made.
    """
    where = "in the block saying how the table was read"
    mapping = _mapping(value, "source", _AT_THE_TOP)
    _keys(mapping, where, SOURCE_KEYS, "that block")
    encoding = _one_of(mapping["encoding"], "encoding", where, ENCODINGS)
    fallback = _truth(
        mapping["used_fallback_encoding"], "used_fallback_encoding", where
    )
    header_source = _one_of(
        mapping["header_source"], "header_source", where, HEADER_SOURCES
    )
    by_convention = _truth(
        mapping["header_by_convention"], "header_by_convention", where
    )
    evidence = _filled_text(
        mapping["header_evidence"], "header_evidence", where
    )
    if fallback != (encoding == "latin-1"):
        raise _broken(
            "S5",
            where,
            f"the encoding named is '{encoding}'",
            f"the record of falling back to it says {fallback}",
        )
    if by_convention and header_source != "file":
        raise _broken(
            "S6",
            where,
            "the first row was taken as names by convention",
            f"the names came from '{header_source}' rather than the file",
        )
    return SourceBlock(
        encoding=encoding,
        used_fallback_encoding=fallback,
        header_source=header_source,
        header_by_convention=by_convention,
        header_evidence=evidence,
    )


def _declaration(value: object, key: str, where: str) -> DeclarationRecord:
    """One declaration record: the count, the flag, the two lists.

    Contract 5 section 6.2 and invariants C5-S7, C5-S14, C5-K1 to C5-K3.

    `values_recorded` is a discriminator and not a switch: a description
    written before this rule carried an array of spellings under the
    same key, and a consumer must be able to tell the two apart without
    guessing. A description claiming to record the person's own declared
    spellings is not a version 5 description, whatever else it says.

    THE TWO LISTS ARE NOT THAT TEXT, and C5-S7 fixes the wording so the
    flag beside them cannot be read as contradicting them: each holds
    MEMBERS of the closed vocabulary the contract prints in its own
    appendix, which is this package's and identical in every
    installation. A value outside those lists is a value from somebody's
    table, so it is refused here by name rather than accepted and
    ignored (C5-K1).
    """
    mapping = _mapping(value, key, where)
    _keys(mapping, where, DECLARATION_KEYS, f"the '{key}' record")
    declared = _whole(mapping["n_declared"], f"{key} -> n_declared", where, 0)
    recorded = _truth(
        mapping["values_recorded"], f"{key} -> values_recorded", where
    )
    if recorded:
        raise _broken(
            "C5-S7",
            where,
            f"the record '{key}' says the declared values were kept",
            (
                "in a version 5 description no text of the person's own "
                "stands in that block, so the flag reads false in both "
                "records"
            ),
        )
    texts = _built_in_texts(mapping["built_in_texts"], key, where)
    numbers = _built_in_numbers(mapping["built_in_numbers"], key, where)
    if len(texts) + len(numbers) > declared:
        raise _broken(
            "C5-K3",
            where,
            (
                f"the record '{key}' names "
                f"{len(texts) + len(numbers)} of synthtwin's own words"
            ),
            f"it says {declared} value(s) were named that way",
        )
    return DeclarationRecord(
        n_declared=declared,
        values_recorded=recorded,
        built_in_texts=texts,
        built_in_numbers=numbers,
    )


def _built_in_texts(
    value: object, key: str, where: str
) -> "tuple[str, ...]":
    """Which of the ten spellings this declaration named (C5-K1, C5-K2).

    Every element must be a member of `parsing.MISSING_TEXTS`, the list
    the contract prints in its section 14.1, and the elements must rise
    with no repeat. A value outside the list is a value out of somebody's
    table, and it is refused rather than read -- so the refusal names the
    FIELD and never quotes what stood there.
    """
    field = f"{key} -> built_in_texts"
    listed = _listing(value, field, where)
    found: list[str] = []
    place = 0
    for item in listed:
        member = _text(item, f"{field}[{place + 1}]", where)
        if member not in parsing.MISSING_TEXTS:
            raise _broken(
                "C5-K1",
                where,
                (
                    f"'{field}' in the settings names a word that is "
                    f"not one of synthtwin's"
                ),
                (
                    "only synthtwin's own published words for 'no "
                    "value' may be written in either list"
                ),
            )
        if found and member <= found[len(found) - 1]:
            raise _out_of_range(
                field,
                where,
                "the words out of order, or one of them twice",
                "synthtwin's own words in rising order, each of them once",
            )
        found = found + [member]
        place = place + 1
    return tuple(found)


def _built_in_numbers(
    value: object, key: str, where: str
) -> "tuple[float, ...]":
    """Which of the three stand-ins this declaration named (C5-K1, C5-K2).

    The same rule as the spellings, over `parsing.NUMERIC_SENTINELS`.
    The comparison is by number, which is what the whole format's
    declaration rule compares by, so a document writing `-999` where the
    producer writes `-999.0` fails the canonical round trip long before
    it reaches here and never has to be judged twice.
    """
    field = f"{key} -> built_in_numbers"
    listed = _listing(value, field, where)
    found: list[float] = []
    place = 0
    for item in listed:
        member = _figure(item, f"{field}[{place + 1}]", where)
        named = False
        for candidate in parsing.NUMERIC_SENTINELS:
            if member == candidate:
                named = True
        if not named:
            raise _broken(
                "C5-K1",
                where,
                f"'{field}' names a number that is not one of synthtwin's",
                (
                    "only synthtwin's own three stand-in numbers may be "
                    "written there"
                ),
            )
        if found and member <= found[len(found) - 1]:
            raise _out_of_range(
                field,
                where,
                "the numbers out of order, or one of them twice",
                (
                    "synthtwin's own stand-in numbers in rising order, "
                    "each of them once"
                ),
            )
        found = found + [member]
        place = place + 1
    return tuple(found)


def _no_word_is_named_both_ways(
    kept: DeclarationRecord, absent: DeclarationRecord, where: str
) -> None:
    """Invariant C5-K4: the two records never name one of our words twice.

    A value named with `--keep-value` and with `--missing-value` at once
    is refused before the table is opened, and the refusal names the two
    words -- so a description carrying one member in both records is a
    description its own settings contradict. The refusal says which
    record pair clashed and never quotes the member: it is one of
    synthtwin's own thirteen words, but naming it here would put the
    loader in the business of quoting a settings value, which nothing
    else on this path does.

    Guarantees: accepts the two parsed records and the place a refusal
    reads at; returns nothing when they are disjoint. Raises
    ProfileError (R17, rule C5-K4). No I/O of any kind.
    """
    for member in kept.built_in_texts:
        if member in absent.built_in_texts:
            raise _broken(
                "C5-K4",
                where,
                "one of synthtwin's own spellings is named in both records",
                "a value can be kept or read as 'no value', never both",
            )
    for number in kept.built_in_numbers:
        if number in absent.built_in_numbers:
            raise _broken(
                "C5-K4",
                where,
                "one of synthtwin's own stand-in numbers is in both records",
                "a value can be kept or read as 'no value', never both",
            )


def _settings(value: object) -> SettingsBlock:
    """The rules that produced this description (contract 4.4).

    Guarantees: accepts the value under `settings`; returns it as a
    typed object. Raises ProfileError for an unknown or missing key, a
    wrong type, a value outside its range, and for S7 and S9. The whole
    subtree is read-only to a generator: nothing in it is an output
    obligation, and it is read only to interpret the facts elsewhere in
    the description that the floor governs.

    S8 -- that every declared name is a column of this table -- is not
    checked here, because it needs the columns. It is checked once they
    have been read.

    THE FLOOR'S MINIMUM IS ONE, NOT ELEVEN (owner ruling 2026-08-14,
    plan amendment A-P3-11). `--smallest-group` is a documented option
    and it accepted any positive number, so `synthtwin profile
    t.csv --smallest-group 2` wrote a description that this loader then
    refused -- and the refusal told the person to run `synthtwin
    profile` and use the file exactly as written, which is what they
    had done. One is the smallest number the rest of the format can
    carry: every floor-governed rule is stated as "at least the floor"
    and "below the floor", and at a floor of one the second half is the
    empty range, so nothing is ever held back and every invariant above
    still holds. Zero is refused here as it always was -- a floor of
    zero would make "below the floor" reach counts of nothing at all,
    which no count is.

    WHAT LOWERING IT GIVES UP is not this loader's to soften: the
    description then names groups as small as the floor, and the twin,
    both reports and the plain-language summary carry those counts too.
    Every one of those four says so on its face when the floor is under
    the default, which is the other half of the ruling.
    """
    where = "in the block of rules that produced the description"
    mapping = _mapping(value, "settings", _AT_THE_TOP)
    _keys(mapping, where, SETTINGS_KEYS, "that block")
    floor = _whole(mapping["small_cell_floor"], "small_cell_floor", where, 1)
    ceiling = _whole(
        mapping["categorical_ceiling"], "categorical_ceiling", where, 1
    )
    smallest = _whole(
        mapping["categorical_floor"], "categorical_floor", where, 1
    )
    if smallest > ceiling:
        raise _broken(
            "S9",
            where,
            f"the smallest number of categories allowed is {smallest}",
            f"the largest is {ceiling}",
        )
    declared: list[str] = []
    names = _listing(
        mapping["forced_identifiers"], "forced_identifiers", where
    )
    place = 0
    for name in names:
        found = _text(name, f"forced_identifiers[{place}]", where)
        if declared and found <= declared[len(declared) - 1]:
            raise _out_of_range(
                "forced_identifiers",
                where,
                f"'{found}'",
                "names in rising order, each of them once",
            )
        declared = declared + [found]
        place = place + 1
    block = SettingsBlock(
        small_cell_floor=floor,
        identifier_uniqueness=_share(
            mapping["identifier_uniqueness"], "identifier_uniqueness", where
        ),
        identifier_minimum_rows=_whole(
            mapping["identifier_minimum_rows"],
            "identifier_minimum_rows",
            where,
            0,
        ),
        minimum_parse_rate=_share(
            mapping["minimum_parse_rate"], "minimum_parse_rate", where
        ),
        categorical_share=_share(
            mapping["categorical_share"], "categorical_share", where
        ),
        categorical_ceiling=ceiling,
        categorical_floor=smallest,
        sentinel_outlier_iqr_multiple=_figure(
            mapping["sentinel_outlier_iqr_multiple"],
            "sentinel_outlier_iqr_multiple",
            where,
        ),
        sentinel_minimum_share=_share(
            mapping["sentinel_minimum_share"], "sentinel_minimum_share", where
        ),
        kept_values=_declaration(
            mapping["kept_values"], "kept_values", where
        ),
        declared_missing_values=_declaration(
            mapping["declared_missing_values"],
            "declared_missing_values",
            where,
        ),
        declaration_matching=_one_of(
            mapping["declaration_matching"],
            "declaration_matching",
            where,
            (DECLARATION_MATCHING,),
        ),
        declaration_publication=_one_of(
            mapping["declaration_publication"],
            "declaration_publication",
            where,
            (DECLARATION_PUBLICATION,),
        ),
        near_threshold_slack=_whole(
            mapping["near_threshold_slack"], "near_threshold_slack", where, 0
        ),
        forced_identifiers=tuple(declared),
    )
    # C5-K4 LAST, because it is the one rule here that needs BOTH
    # records: every other check is about one entry and is raised where
    # that entry is read, which is what keeps a refusal near its cause.
    _no_word_is_named_both_ways(
        block.kept_values, block.declared_missing_values, where
    )
    return block


def _relationships(value: object) -> RelationshipManifest:
    """The eight reserved names, every one of them empty (S12).

    Guarantees: accepts the value under `relationships`; returns the
    manifest. Raises ProfileError when a ninth name appears (R13), when
    one of the eight is absent (R14), and when any of them carries
    anything at all (R18) -- whose message says that this version of
    synthtwin does not carry structure between columns and that a newer
    synthtwin is needed to read a description that does.

    The block exists empty on purpose: a block reserved in the shape it
    will eventually take is what lets a later phase fill one slot
    without moving any other key, and filling any slot advances the
    version number.
    """
    where = "in the block about how the columns move together"
    mapping = _mapping(value, "relationships", _AT_THE_TOP)
    _keys(mapping, where, RELATIONSHIP_KEYS, "that block")
    for name in RELATIONSHIP_KEYS:
        if mapping[name] is not None:
            raise errors.ProfileError(
                errors.profile_relationships_carried(name)
            )
    return RelationshipManifest(slots=RELATIONSHIP_KEYS)


def _notes(value: object) -> "tuple[PublicationNote, ...]":
    """The per-column notes about what was held back, and why (4.5).

    Guarantees: accepts the value under `publication_notes`; returns the
    notes in the document's own order. Raises ProfileError when it is
    not a list, when a note is not a block of exactly `column` and
    `note`, or when either is not text.

    S10 and S11 -- that every note is about a column of this table, and
    that the notes are grouped by column in schema order -- need the
    columns, and are checked once those have been read.
    """
    where = "in the notes about what was held back"
    listed = _listing(value, "publication_notes", _AT_THE_TOP)
    notes: list[PublicationNote] = []
    place = 0
    for entry in listed:
        seat = f"in note number {place + 1} of the notes about what was held back"
        mapping = _mapping(entry, f"publication_notes[{place}]", where)
        _keys(mapping, seat, NOTE_KEYS, "every note")
        notes = notes + [
            PublicationNote(
                column=_text(mapping["column"], "column", seat),
                note=_text(mapping["note"], "note", seat),
            )
        ]
        place = place + 1
    return tuple(notes)


# -- the column block -------------------------------------------------


def _publishes_nothing(role: str, structural_role: str) -> bool:
    """True when no value of the table may appear in this block (6.10).

    Three roles publish no value of the table anywhere in their block,
    and so does any column the person declared, whatever role it
    reached. This is a property of the whole BLOCK and not of any one
    field: it is what stops the next field somebody adds from being the
    one that leaks.
    """
    return structural_role == "identifier" or role in ROLES_PUBLISHING_NOTHING


def _axes(mapping: "dict[str, object]", where: str, frame: _Frame) -> "tuple[str, str, str, str]":
    """The role and the three axes, checked against each other (5.2).

    Returns (role, statistical type, quality state, structural role).
    Raises ProfileError for a value outside its list (R16) and for A1 to
    A4. A4 is a refusal rather than a repair because the generator
    dispatches on the axes, and a document whose axes and role disagree
    would route a column somewhere its own role says it does not belong.
    """
    role = _one_of(mapping["role"], "role", where, ROLES)
    statistical = _one_of(
        mapping["statistical_type"], "statistical_type", where,
        STATISTICAL_TYPES,
    )
    quality = _one_of(
        mapping["quality_state"], "quality_state", where, QUALITY_STATES
    )
    structural = _one_of(
        mapping["structural_role"], "structural_role", where, STRUCTURAL_ROLES
    )
    name = _text(mapping["name"], "name", where)
    if (role, statistical, quality) not in AXIS_ROWS:
        raise _broken(
            "A4",
            where,
            f"the type path is '{role}'",
            (
                f"its kind and condition are given as '{statistical}' and "
                f"'{quality}'"
            ),
        )
    if (structural == "identifier") != (name in frame.declared):
        raise _broken(
            "A1",
            where,
            f"the column is marked '{structural}'",
            (
                "the names declared as holding record numbers are "
                f"{_listed(frame.declared)}"
                if frame.declared
                else "no column was declared as holding record numbers"
            ),
        )
    if statistical == "code" and structural != "identifier":
        raise _broken(
            "A2",
            where,
            "the column is described as holding codes",
            f"it is marked '{structural}' rather than declared",
        )
    if structural == "identifier":
        if statistical != "code" and statistical != "unknown":
            raise _broken(
                "A3",
                where,
                "the column was declared as holding record numbers",
                f"it is described as holding '{statistical}'",
            )
        if role != ROLE_IDENTIFIER and role != ROLE_EMPTY:
            raise _broken(
                "A3",
                where,
                "the column was declared as holding record numbers",
                f"its type path is '{role}'",
            )
    return role, statistical, quality, structural


def _missing_by_class(
    value: object, where: str, n_missing: int, floor: int
) -> MissingByClass:
    """Absent cells by the reason each was counted absent (5.4).

    Raises ProfileError for a missing or unknown reason, a value that is
    not a whole number, N1 (the five come to the number of empty cells)
    and N2 (a reason other than the pooled one is either unused or used
    by at least the smallest group size, so that a rare spelling cannot
    be singled out).
    """
    mapping = _mapping(value, "missing_by_class", where)
    _keys(mapping, where, MISSING_CLASS_KEYS, "every column")
    counted: dict[str, int] = {}
    for name in MISSING_CLASS_KEYS:
        counted[name] = _whole(
            mapping[name], f"missing_by_class -> {name}", where, 0
        )
    total = _added(counted)
    if total != n_missing:
        raise _broken(
            "N1",
            where,
            f"the reasons for an empty cell come to {total}",
            f"the column counts {n_missing} empty cells",
        )
    for name in MISSING_CLASS_KEYS:
        if name == WITHHELD:
            continue
        if counted[name] and counted[name] < floor:
            raise _broken(
                "N2",
                where,
                f"the reason '{name}' is used {counted[name]} times",
                f"the smallest group size is {floor}",
            )
    return MissingByClass(
        blank=counted[BLANK],
        declared_missing=counted["(declared-missing)"],
        numeric_sentinel=counted["(numeric-sentinel)"],
        text_code=counted["(text-code)"],
        withheld=counted[WITHHELD],
    )


def _missing_by_source(
    value: object,
    where: str,
    n_missing: int,
    floor: int,
    publishes_nothing: bool,
    n_blank: int,
    n_withheld: int,
) -> "dict[str, int]":
    """Absent cells by the exact spelling that made them absent (5.4).

    Contract 5 invariants C5-N3, C5-N4 and C5-N5.

    Raises ProfileError for a value that is not a count, for C5-N3 and
    for C5-N4. C5-N3 is checked in the two directions the document
    supports: a column whose class permits no value of the table names
    no spelling and accounts for no absent cell at all, and on every
    other column the spellings, the blank cells and the cells held back
    come to the number of empty cells -- which forces the empty mapping
    when there are no empty cells, and forbids it when there are.

    NO KEY HERE IS ONE OF THIS PACKAGE'S OWN WORDS (C5-N5). Version 4
    exempted `(blank)` and `(withheld)` from the floor because it kept
    two of its own counts in this map; version 5 keeps them in two
    fields of their own, so a key reading `(withheld)` means that cells
    of the table held exactly those ten characters and is held to the
    floor like every other spelling. The exemption is gone rather than
    narrowed, which makes the rule the one the producer already
    followed.
    """
    counted = _counts(
        value, "missing_by_source", where, 1, _THE_SOURCE_KEYS
    )
    if publishes_nothing:
        if counted:
            raise _broken(
                "C5-N3",
                where,
                "this column publishes no value of the table",
                f"it names {len(counted)} spelling(s) of an empty cell",
            )
        if n_blank or n_withheld:
            raise _broken(
                "C5-N3",
                where,
                "this column publishes no value of the table",
                (
                    f"it accounts for {n_blank + n_withheld} of its empty "
                    f"cells anyway"
                ),
            )
        return counted
    total = _added(counted) + n_blank + n_withheld
    if total != n_missing:
        raise _broken(
            "C5-N3",
            where,
            f"the empty cells accounted for come to {total}",
            f"the column counts {n_missing} empty cells",
        )
    for name in sorted(counted):
        if counted[name] < floor:
            raise _broken(
                "C5-N4",
                where,
                f"the spelling named there was written by {counted[name]} rows",
                f"the smallest group size is {floor}",
            )
    if n_blank and n_blank < floor:
        raise _broken(
            "C5-N4",
            where,
            f"{n_blank} cell(s) of the column held nothing but space",
            f"the smallest group size is {floor}",
        )
    return counted


def _sentinel_verdicts(
    value: object, where: str, floor: int, publishes_nothing: bool
) -> "tuple[SentinelVerdict, ...]":
    """What was decided about each named stand-in number, and why (5.5).

    Raises ProfileError for an unknown or missing key, a wrong type, a
    value outside its list, and for V1 to V4. V2 is the publication
    class applied to this block: on a column that publishes no value of
    the table every candidate reads `(withheld)`, and on every other
    column none of them does, because naming a candidate there would
    publish a value out of a column that publishes none.
    """
    listed = _listing(value, "sentinel_verdicts", where)
    entries: list[SentinelVerdict] = []
    place = 0
    previous: tuple[int, str, str] | None = None
    previous_number: float | None = None
    for entry in listed:
        seat = f"{where}, in decision number {place + 1} about a stand-in number"
        mapping = _mapping(entry, f"sentinel_verdicts[{place}]", where)
        _keys(mapping, seat, SENTINEL_KEYS, "every decision of that kind")
        candidate = _text(mapping["candidate"], "candidate", seat)
        verdict = _one_of(mapping["verdict"], "verdict", seat, VERDICTS)
        reason = _one_of(mapping["reason"], "reason", seat, REASONS)
        occurrences = _whole(
            mapping["n_occurrences"], "n_occurrences", seat, 1
        )
        if occurrences < floor:
            raise _broken(
                "V1",
                seat,
                f"the stand-in number was held by {occurrences} rows",
                f"the smallest group size is {floor}",
            )
        if publishes_nothing != (candidate == WITHHELD):
            raise _broken(
                "V2",
                seat,
                (
                    "this column publishes no value of the table"
                    if publishes_nothing
                    else "this column publishes values of the table"
                ),
                f"the stand-in number is written '{candidate}'",
            )
        if verdict == VERDICT_MISSING and reason != REASON_OUTLIER_AND_FREQUENT:
            raise _broken(
                "V3",
                seat,
                "the stand-in number was read as meaning no value",
                f"the reason given is '{reason}'",
            )
        if publishes_nothing:
            ranked = (occurrences, verdict, reason)
            if previous is not None and ranked < previous:
                raise _broken(
                    "V4",
                    seat,
                    "this decision comes after the one before it",
                    (
                        "the decisions of a column that names no stand-in "
                        "number are ordered by rows, then verdict, then reason"
                    ),
                )
            previous = ranked
        else:
            number = _reads_as_a_number(candidate, "candidate", seat)
            if previous_number is not None and number < previous_number:
                raise _broken(
                    "V4",
                    seat,
                    f"this decision is about {number}",
                    f"the one before it is about {previous_number}",
                )
            previous_number = number
        entries = entries + [
            SentinelVerdict(
                candidate=candidate,
                verdict=verdict,
                reason=reason,
                n_occurrences=occurrences,
            )
        ]
        place = place + 1
    return tuple(entries)


def _reads_as_a_number(text: str, key: str, where: str) -> float:
    """A named stand-in number, read back as the number it names."""
    try:
        found = float(text)
    except ValueError as error:
        raise _out_of_range(
            key, where, f"'{text}'", "a number, or the word '(withheld)'"
        ) from error
    if not math.isfinite(found):
        raise _out_of_range(
            key, where, f"'{text}'", "a number, or the word '(withheld)'"
        )
    return found


def _column(
    value: object, index: int, frame: _Frame
) -> ColumnBlock:
    """One column block, checked in full (contract section 5).

    Guarantees:

    - Inputs: the block, its place in the list counting from zero, and
      the facts of the document it is checked against.
    - Determinism: the answer depends only on those.
    - Errors raised: ProfileError for every unknown key, missing key,
      wrong type, out-of-range value and broken invariant this block can
      carry. Nothing is repaired.
    - Boundary: no value of the table is read out of the block; the
      checks read counts, names and the column's own published labels.

    THE ROLE IS READ FIRST, because the set of keys a block may carry is
    the universal set plus what its role adds, and every key not listed
    for a role is forbidden on it. "Forbidden" is the half of a contract
    a loader can only enforce if it is written down, and it is written
    down here as the role's own key tuple.

    THE UNIVERSAL FACTS ARE THEN CHECKED BEFORE THE ROLE'S OWN, so that
    a person meets the outermost thing that is wrong: a block whose
    counts do not add up and whose ladder is also damaged is a block
    whose counts are the more useful thing to be told about.
    """
    seat = f"in the block for column number {index + 1}"
    mapping = _mapping(value, f"columns[{index}]", "in the list of columns")
    for key in ("name", "role", "statistical_type", "quality_state",
                "structural_role"):
        if key not in mapping:
            raise _missing(key, seat, "every column")
    name = _filled_text(mapping["name"], "name", seat)
    where = f"in the block for the column named '{name}'"
    role, statistical, quality, structural = _axes(mapping, where, frame)
    _keys(
        mapping,
        where,
        UNIVERSAL_COLUMN_KEYS + _role_keys(role),
        f"every column whose type path is '{role}'",
    )
    position = _bounded(
        mapping["position"], "position", where, 1, frame.n_columns,
        "the number of columns the table has",
    )
    if position != index + 1:
        raise _broken(
            "S2",
            where,
            f"the block says its place is {position}",
            f"it is the block at place {index + 1} of the list",
        )
    n_present = _whole(mapping["n_present"], "n_present", where, 0)
    n_missing = _whole(mapping["n_missing"], "n_missing", where, 0)
    if n_present + n_missing != frame.n_rows:
        raise _broken(
            "X1",
            where,
            (
                f"the column holds {n_present} values and leaves "
                f"{n_missing} cells empty"
            ),
            "the description gives the table a different number of rows",
        )
    n_distinct = _whole(mapping["n_distinct"], "n_distinct", where, 0)
    n_folded = _whole(
        mapping["n_distinct_folded"], "n_distinct_folded", where, 0
    )
    if n_folded > n_distinct or n_distinct > n_present:
        raise _broken(
            "X3",
            where,
            (
                f"the column holds {n_present} values, {n_distinct} of them "
                f"different"
            ),
            f"{n_folded} of them are different ignoring case",
        )
    if (n_present == 0) != (n_distinct == 0) or (n_present == 0) != (
        n_folded == 0
    ):
        raise _broken(
            "X4",
            where,
            f"the column holds {n_present} values",
            (
                f"{n_distinct} of them are different, and {n_folded} "
                f"ignoring case"
            ),
        )
    n_numeric = _whole(mapping["n_numeric"], "n_numeric", where, 0)
    n_not_numeric = _whole(mapping["n_not_numeric"], "n_not_numeric", where, 0)
    n_out_of_range = _whole(
        mapping["n_out_of_range"], "n_out_of_range", where, 0
    )
    n_contradictory = _whole(
        mapping["n_contradictory"], "n_contradictory", where, 0
    )
    counted = n_numeric + n_not_numeric + n_out_of_range + n_contradictory
    if counted != n_present:
        raise _broken(
            "X2",
            where,
            f"the values counted by what they read as come to {counted}",
            f"the column holds {n_present} values",
        )
    if (role == ROLE_EMPTY) != (n_present == 0):
        raise _broken(
            "E1",
            where,
            f"the type path is '{role}'",
            f"the column holds {n_present} values",
        )
    publishes_nothing = _publishes_nothing(role, structural)
    by_class = _missing_by_class(
        mapping["missing_by_class"], where, n_missing, frame.floor
    )
    n_blank = _whole(
        mapping["n_missing_blank"], "n_missing_blank", where, 0
    )
    n_withheld = _whole(
        mapping["n_missing_withheld"], "n_missing_withheld", where, 0
    )
    by_source = _missing_by_source(
        mapping["missing_by_source"],
        where,
        n_missing,
        frame.floor,
        publishes_nothing,
        n_blank,
        n_withheld,
    )
    verdicts = _sentinel_verdicts(
        mapping["sentinel_verdicts"], where, frame.floor, publishes_nothing
    )
    unpublished = _whole(
        mapping["n_sentinel_candidates_unpublished"],
        "n_sentinel_candidates_unpublished",
        where,
        0,
    )
    evidence = _filled_text(
        mapping["detection_evidence"], "detection_evidence", where
    )
    remarks: list[str] = []
    place = 0
    for remark in _listing(mapping["remarks"], "remarks", where):
        remarks = remarks + [_text(remark, f"remarks[{place}]", where)]
        place = place + 1
    facts = _facts(
        mapping,
        where,
        role,
        frame,
        n_present,
        n_distinct,
        n_folded,
        n_numeric,
        n_out_of_range,
        n_contradictory,
        remarks,
    )
    return ColumnBlock(
        name=name,
        position=position,
        role=role,
        statistical_type=statistical,
        quality_state=quality,
        structural_role=structural,
        n_present=n_present,
        n_missing=n_missing,
        missing_by_class=by_class,
        missing_by_source=by_source,
        n_missing_blank=n_blank,
        n_missing_withheld=n_withheld,
        n_distinct=n_distinct,
        n_distinct_folded=n_folded,
        n_numeric=n_numeric,
        n_not_numeric=n_not_numeric,
        n_out_of_range=n_out_of_range,
        n_contradictory=n_contradictory,
        n_sentinel_candidates_unpublished=unpublished,
        sentinel_verdicts=verdicts,
        detection_evidence=evidence,
        remarks=tuple(remarks),
        facts=facts,
    )


def _where(said: str, part: str) -> int:
    """Where one fragment stands in a sentence, or -1.

    Written with slicing rather than `find`, and that is the offline
    audit's rule rather than a preference: a method call whose argument
    the audit cannot resolve is a call it cannot judge, and one of
    these fragments is built from the block's own pair. Slicing and
    equality are neither of them method calls on an untraced value.
    """
    if not isinstance(said, str) or not isinstance(part, str):
        raise TypeError("internal check: a sentence was not text")
    span = len(part)
    for start in range(len(said) - span + 1):
        if said[start : start + span] == part:
            return start
    return -1


def _affix_clause(prefix: str, suffix: str) -> str:
    """The clause the required remark writes about THIS block's pair.

    Three shapes, because one side is usually empty and a sentence
    saying "written as nothing, a number, then 'mg'" describes a shape
    no cell has. Built from the block's OWN two spellings, so a remark
    holding this clause names the pair the block publishes, character
    for character -- which is what AF-R asks and what a check of the
    sentence's generic fragments alone could not tell: a block
    publishing `$` accepted a remark saying `'kg' followed by a
    number`, a required warning that misdescribes the column it warns
    about.
    """
    if prefix and suffix:
        return f"written as '{prefix}', a number, then '{suffix}'"
    if prefix:
        return f"written as '{prefix}' followed by a number"
    return f"written as a number followed by '{suffix}'"


def _is_the_affixed_remark(
    remark: str, n_affixed: int, clause: str
) -> bool:
    """Whether one sentence is the remark AF-R requires, not a token of it.

    Every fixed fragment, IN ORDER, and the block's own count in front
    of them. The loader may not import the profiler's taxonomy and so
    cannot render the sentence; what it can do is refuse anything that
    is not shaped like it, which is the difference between an invariant
    and a password.
    """
    if not isinstance(remark, str):
        raise TypeError("internal check: a remark was not text")
    if isinstance(n_affixed, bool) or not isinstance(n_affixed, int):
        raise TypeError("internal check: a count was not a whole number")
    # THE FRAGMENTS ARE WRITTEN OUT HERE AS LITERALS rather than walked
    # out of the tuple beside them, and the reason is the offline
    # audit's: a method call whose argument it cannot resolve is a call
    # it cannot judge, and a loop variable is not resolvable. The tuple
    # stays as the record of what the sentence is made of, and
    # `tests/test_p4d4_affixed_role.py` holds these calls to it.
    if remark[: len(f"{n_affixed} ")] != f"{n_affixed} ":
        return False
    # The pair's own clause, which is where the block's two published
    # spellings have to appear.
    if _where(remark, clause) < 0:
        return False
    first = _where(remark, "of this column's values are written as")
    second = _where(
        remark,
        "and synthtwin described those numbers as quantities: their "
        "average, their spread and their ends are in this profile.",
    )
    third = _where(remark, "If these are codes rather than measurements")
    fourth = _where(
        remark,
        "run the command again with --identifier and no value of this "
        "column will be published at all",
    )
    if first < 0 or second < 0 or third < 0 or fourth < 0:
        return False
    return first < second < third < fourth


def _role_keys(role: str) -> "tuple[str, ...]":
    """The keys this role ADDS to the universal set (contract 6.11)."""
    if role == ROLE_EMPTY:
        return ()
    if role == ROLE_UNREPRESENTABLE:
        return UNREPRESENTABLE_KEYS
    if role == ROLE_CONSTANT or role == ROLE_BINARY:
        return LABEL_KEYS
    if role == ROLE_CATEGORICAL:
        return CATEGORICAL_KEYS
    if role == ROLE_DATETIME:
        return DATETIME_KEYS
    if role == ROLE_COUNT or role == ROLE_CONTINUOUS:
        return NUMERIC_KEYS
    if role == ROLE_AFFIXED:
        return AFFIXED_KEYS
    if role == ROLE_IDENTIFIER:
        return IDENTIFIER_KEYS
    return TEXT_KEYS


def _facts(
    mapping: "dict[str, object]",
    where: str,
    role: str,
    frame: _Frame,
    n_present: int,
    n_distinct: int,
    n_folded: int,
    n_numeric: int,
    n_out_of_range: int,
    n_contradictory: int,
    remarks: "list[str]",
) -> ColumnFacts:
    """Everything the ROLE adds, checked by the rules of its section."""
    if role == ROLE_EMPTY:
        return _empty_facts(mapping, where)
    if role == ROLE_UNREPRESENTABLE:
        return _unrepresentable_facts(
            mapping, where, n_present, n_distinct
        )
    if role == ROLE_CONSTANT or role == ROLE_BINARY:
        return _label_facts(
            mapping, where, role, frame.floor, n_present, n_folded
        )
    if role == ROLE_CATEGORICAL:
        return _categorical_facts(
            mapping, where, frame.floor, n_present, n_folded
        )
    if role == ROLE_DATETIME:
        return _datetime_facts(mapping, where, frame.floor, n_present)
    if role == ROLE_COUNT or role == ROLE_CONTINUOUS:
        return _numeric_facts(
            mapping,
            where,
            frame,
            n_present,
            n_numeric,
            n_out_of_range,
            n_contradictory,
        )
    if role == ROLE_AFFIXED:
        return _affixed_facts(mapping, where, frame, n_present, remarks)
    if role == ROLE_IDENTIFIER:
        return _identifier_facts(
            mapping, where, n_present, n_distinct
        )
    return _text_facts(mapping, where, n_present, n_distinct)


def _empty_facts(mapping: "dict[str, object]", where: str) -> EmptyFacts:
    """A column with no present cells at all (contract 6.1).

    An empty block is exactly the universal key set: it adds nothing,
    and it carries no per-column row count, which lives only inside the
    numeric blocks. The two facts checked here are the ones section 6.1
    states and no other rule reaches: there is nothing to have decided
    about a stand-in number in a column that holds no value.
    """
    verdicts = _listing(mapping["sentinel_verdicts"], "sentinel_verdicts", where)
    unpublished = _whole(
        mapping["n_sentinel_candidates_unpublished"],
        "n_sentinel_candidates_unpublished",
        where,
        0,
    )
    if verdicts:
        raise _out_of_range(
            "sentinel_verdicts",
            where,
            f"{len(verdicts)} decision(s) about a stand-in number",
            (
                "no decisions at all, because a column that holds no value "
                "has no stand-in number to judge"
            ),
        )
    if unpublished:
        raise _out_of_range(
            "n_sentinel_candidates_unpublished",
            where,
            f"{unpublished}",
            (
                "0, because a column that holds no value has no stand-in "
                "number to judge"
            ),
        )
    return EmptyFacts()


def _unrepresentable_facts(
    mapping: "dict[str, object]",
    where: str,
    n_present: int,
    n_distinct: int,
) -> UnrepresentableFacts:
    """A column of numbers this format cannot hold (contract 6.2).

    Raises ProfileError for a wrong type or an out-of-range count, and
    for U1, U2 and U3. There is no width fact here to check, because the
    contract publishes none: the omission is load-bearing and is
    recorded as a residual rather than closed.
    """
    n_whole = _whole(mapping["n_whole"], "n_whole", where, 0)
    n_fraction = _whole(mapping["n_fraction"], "n_fraction", where, 0)
    n_whole_unknown = _whole(
        mapping["n_whole_unknown"], "n_whole_unknown", where, 0
    )
    n_positive = _whole(mapping["n_positive"], "n_positive", where, 0)
    n_negative = _whole(mapping["n_negative"], "n_negative", where, 0)
    n_sign_unknown = _whole(
        mapping["n_sign_unknown"], "n_sign_unknown", where, 0
    )
    if n_whole + n_fraction + n_whole_unknown != n_present:
        raise _broken(
            "U1",
            where,
            (
                f"{n_whole} values are whole, {n_fraction} are not, and "
                f"{n_whole_unknown} are neither settled"
            ),
            f"the column holds {n_present} values",
        )
    if n_positive + n_negative + n_sign_unknown != n_present:
        raise _broken(
            "U2",
            where,
            (
                f"{n_positive} values are positive, {n_negative} are "
                f"negative, and {n_sign_unknown} are neither settled"
            ),
            f"the column holds {n_present} values",
        )
    pattern, pairs = _multiplicity(
        mapping["n_distinct_by_occurrences"],
        "n_distinct_by_occurrences",
        where,
        None,
    )
    _pattern_closes(pairs, where, "U3", n_distinct, n_present)
    return UnrepresentableFacts(
        n_whole=n_whole,
        n_fraction=n_fraction,
        n_whole_unknown=n_whole_unknown,
        n_positive=n_positive,
        n_negative=n_negative,
        n_sign_unknown=n_sign_unknown,
        n_distinct_by_occurrences=pattern,
    )


def _pattern_closes(
    pairs: "list[tuple[int, int]]",
    where: str,
    rule: str,
    n_distinct: int,
    n_present: int,
) -> None:
    """M1 and M2 for a column's own repetition pattern.

    ``rule`` is the role's own identifier for the pair of sums -- U3 on
    a column of numbers too large to hold, I2 on a column of record
    numbers, F2 on a column of text -- so the refusal cites the rule the
    reader will find in that role's section.
    """
    things, rows = _multiplicity_totals(pairs)
    if things != n_distinct:
        raise _broken(
            rule,
            where,
            f"the repetition pattern describes {things} different values",
            f"the column records {n_distinct}",
        )
    if rows != n_present:
        raise _broken(
            rule,
            where,
            f"the repetition pattern covers {rows} rows",
            f"the column holds {n_present} values",
        )


def _levels(
    mapping: "dict[str, object]",
    where: str,
    floor: int,
    n_present: int,
    n_folded: int,
) -> "tuple[tuple[LevelEntry, ...], int, int, tuple[int, ...]]":
    """The published labels and everything the floor held back (6.3).

    Raises ProfileError for a wrong type or an out-of-range count, and
    for B1 to B7 and W2 to W7. B8 is a permission rather than a rule: an
    empty list of labels is a column every one of whose labels fell
    below the floor, and it is valid.
    """
    listed = _listing(mapping["levels"], "levels", where)
    suppressed_levels = _whole(
        mapping["suppressed_levels"], "suppressed_levels", where, 0
    )
    suppressed_rows = _whole(
        mapping["suppressed_rows"], "suppressed_rows", where, 0
    )
    sizes: list[int] = []
    place = 0
    previous_size = 0
    for size in _listing(
        mapping["suppressed_level_counts"], "suppressed_level_counts", where
    ):
        found = _whole(
            size, f"suppressed_level_counts[{place}]", where, 1
        )
        # B5's second half, read against the range the floor holds back
        # rather than against the floor itself, so that this site and
        # S13 cannot drift: at a floor of one the range is empty and no
        # size at all may be listed here.
        if found not in _below_the_floor(floor):
            raise _broken(
                "B5",
                where,
                f"a label held back covers {found} rows",
                f"the smallest group size is {floor}",
            )
        if place and found < previous_size:
            raise _broken(
                "B4",
                where,
                f"a label held back covers {found} rows",
                f"the one before it covers {previous_size}",
            )
        sizes = sizes + [found]
        previous_size = found
        place = place + 1
    if len(sizes) != suppressed_levels:
        raise _broken(
            "B4",
            where,
            f"{len(sizes)} sizes of held-back labels are listed",
            f"the column says {suppressed_levels} labels were held back",
        )
    total_sizes = 0
    for size_kept in sizes:
        total_sizes = total_sizes + size_kept
    if total_sizes != suppressed_rows:
        raise _broken(
            "B4",
            where,
            f"the sizes of the held-back labels come to {total_sizes}",
            f"the column says they cover {suppressed_rows} rows",
        )
    entries: list[LevelEntry] = []
    seen: list[str] = []
    covered = 0
    previous_count = 0
    previous_label = ""
    place = 0
    for entry in listed:
        seat = f"{where}, in published label number {place + 1}"
        block = _mapping(entry, f"levels[{place}]", where)
        _keys(block, seat, LEVEL_KEYS, "every published label")
        label = _text(block["label"], "label", seat)
        count = _whole(block["count"], "count", seat, 1)
        if parsing.folded(label) != label:
            raise _broken(
                "B1",
                seat,
                f"the label is written '{label}'",
                "a published label is trimmed and has its case folded",
            )
        if count < floor:
            raise _broken(
                "B5",
                seat,
                f"the label covers {count} rows",
                f"the smallest group size is {floor}",
            )
        if label in seen:
            raise _broken(
                "B7",
                seat,
                f"the label '{label}' appears more than once",
                "each published label appears exactly once",
            )
        if place and (
            count > previous_count
            or (count == previous_count and label < previous_label)
        ):
            raise _broken(
                "B6",
                seat,
                f"the label '{label}' covers {count} rows",
                (
                    f"the label '{previous_label}' before it covers "
                    f"{previous_count}"
                ),
            )
        variants, withheld = _variants(block, seat, floor, label, count)
        entries = entries + [
            LevelEntry(
                label=label,
                count=count,
                variants=variants,
                variants_withheld=withheld,
            )
        ]
        seen = seen + [label]
        covered = covered + count
        previous_count = count
        previous_label = label
        place = place + 1
    if len(entries) + suppressed_levels != n_folded:
        raise _broken(
            "B2",
            where,
            (
                f"{len(entries)} labels are published and "
                f"{suppressed_levels} held back"
            ),
            (
                f"the column has {n_folded} different values ignoring "
                f"case"
            ),
        )
    if covered + suppressed_rows != n_present:
        raise _broken(
            "B3",
            where,
            (
                f"the published labels cover {covered} rows and the "
                f"held-back ones {suppressed_rows}"
            ),
            f"the column holds {n_present} values",
        )
    return tuple(entries), suppressed_levels, suppressed_rows, tuple(sizes)


def _variants(
    block: "dict[str, object]", seat: str, floor: int, label: str, count: int
) -> "tuple[dict[str, int], dict[str, int]]":
    """How the rows under one published label actually wrote it (7.4).

    Raises ProfileError for a wrong type or an out-of-range count, and
    for W2 to W5 and W7. The keys are stored EXACTLY as the file wrote
    them, before trimming and before the fold, because a variant is a
    generation input that the twin writes into a cell and must read back
    byte for byte -- unlike the spellings of an empty cell, which are
    for a person to read and are escaped for display.
    """
    named = _counts(
        block["variants"], "variants", seat, 1, _THE_VARIANT_KEYS
    )
    for spelling in sorted(named):
        if named[spelling] < floor:
            raise _broken(
                "W5",
                seat,
                f"the spelling '{spelling}' was written by "
                f"{named[spelling]} rows",
                f"the smallest group size is {floor}",
            )
        if parsing.folded(spelling) != label:
            raise _broken(
                "W2",
                seat,
                f"the spelling '{spelling}' is filed under '{label}'",
                f"trimmed and folded it reads '{parsing.folded(spelling)}'",
            )
        if named[spelling] > count:
            raise _broken(
                "W3",
                seat,
                f"the spelling '{spelling}' was written by {named[spelling]} rows",
                f"the label itself covers {count}",
            )
    withheld, pairs = _multiplicity(
        block["variants_withheld"], "variants_withheld", seat, floor - 1
    )
    if not named and not withheld:
        raise _broken(
            "W7",
            seat,
            "the label names no spelling and holds none back",
            "every row under a published label wrote it some way",
        )
    _things, rows = _multiplicity_totals(pairs)
    total = _added(named) + rows
    if total != count:
        raise _broken(
            "W4",
            seat,
            f"the spellings account for {total} rows",
            f"the label covers {count}",
        )
    return named, withheld


def _label_facts(
    mapping: "dict[str, object]",
    where: str,
    role: str,
    floor: int,
    n_present: int,
    n_folded: int,
) -> LabelFacts:
    """A constant or a binary column (contract 6.4 and 6.5)."""
    entries, suppressed, rows, sizes = _levels(
        mapping, where, floor, n_present, n_folded
    )
    wanted = 1 if role == ROLE_CONSTANT else 2
    rule_one = "C1" if role == ROLE_CONSTANT else "Y1"
    if n_folded != wanted:
        raise _broken(
            rule_one,
            where,
            f"the type path is '{role}'",
            (
                f"the column has {n_folded} different values ignoring "
                f"case, not {wanted}"
            ),
        )
    return LabelFacts(
        levels=entries,
        suppressed_levels=suppressed,
        suppressed_rows=rows,
        suppressed_level_counts=sizes,
    )


def _categorical_facts(
    mapping: "dict[str, object]",
    where: str,
    floor: int,
    n_present: int,
    n_folded: int,
) -> CategoricalFacts:
    """A column of categories (contract 6.6.1)."""
    entries, suppressed, rows, sizes = _levels(
        mapping, where, floor, n_present, n_folded
    )
    ceiling = _whole(mapping["level_ceiling"], "level_ceiling", where, 1)
    if n_folded > ceiling:
        raise _broken(
            "G1",
            where,
            (
                f"the column has {n_folded} different values ignoring "
                f"case"
            ),
            f"the line it passed allows {ceiling}",
        )
    return CategoricalFacts(
        levels=entries,
        suppressed_levels=suppressed,
        suppressed_rows=rows,
        suppressed_level_counts=sizes,
        level_ceiling=ceiling,
    )


def _datetime_facts(
    mapping: "dict[str, object]", where: str, floor: int, n_present: int
) -> DatetimeFacts:
    """A column of dates and times (contract 6.6.2).

    Raises ProfileError for a wrong type or a value outside its list,
    and for D1 to D11. D5 is checked in the one direction the document
    supports: where every offset in a column fell below the floor the
    map collapses to a single pooled entry whether one offset wrote the
    column or ten did, so the map alone cannot settle the question --
    which is exactly why the clock is published as its own fact and a
    consumer never has to combine two fields to know what it holds.
    """
    parser_family = _one_of(mapping["format"], "format", where, DATE_FORMATS)
    resolution = _one_of(
        mapping["resolution"], "resolution", where, RESOLUTIONS
    )
    precision = _one_of(
        mapping["time_precision"], "time_precision", where, TIME_PRECISIONS
    )
    digits = _whole(mapping["subsecond_digits"], "subsecond_digits", where, 0)
    clock = _one_of(
        mapping["datetimes_read_at"], "datetimes_read_at", where, CLOCKS
    )
    unparsed = _whole(mapping["n_unparsed"], "n_unparsed", where, 0)
    wanted = "date"
    if parser_family == "iso-datetime":
        wanted = "datetime"
    elif parser_family == "year-quarter":
        wanted = "quarter"
    if resolution != wanted:
        raise _broken(
            "D1",
            where,
            f"the dates were read as '{parser_family}'",
            f"they are published as '{resolution}' rather than '{wanted}'",
        )
    if precision == "quarter" and resolution != "quarter":
        raise _broken(
            "D6",
            where,
            "the finest detail the column writes is a quarter",
            f"its dates are published as '{resolution}'",
        )
    if precision == "date" and resolution != "date":
        # A WHOLE DATE IS THE FINEST DETAIL ONLY OF A DATE COLUMN
        # (review item P2-C1-F6). Both halves of this refusal are real.
        # Against `quarter`, a whole date is finer than the column's own
        # values. Against `datetime`, the two facts cannot both be
        # written: a cell written `2024-03-15` reads back as a column of
        # dates, so the published resolution is lost, and a cell written
        # `2024-03-15T00:00:00` reads back at the second, so the
        # published precision is lost. Both are EXACT-OBSERVABLE, so
        # there is no honest twin for the pair, and the producer cannot
        # make one: a cell with no time of day does not read as a date
        # AND time at all, so a column read that way never has a whole
        # date as its finest detail.
        raise _broken(
            "D6",
            where,
            "the finest detail the column writes is a whole date",
            f"its dates are published as '{resolution}'",
        )
    if (
        precision == "minute" or precision == "second"
        or precision == "subsecond"
    ) and resolution != "datetime":
        raise _broken(
            "D6",
            where,
            f"the finest detail the column writes is '{precision}'",
            f"its dates are published as '{resolution}'",
        )
    if (digits > 0) != (precision == "subsecond"):
        raise _broken(
            "D7",
            where,
            f"the column writes {digits} figures after the second",
            f"the finest detail it writes is given as '{precision}'",
        )
    if unparsed >= n_present:
        raise _broken(
            "D8",
            where,
            f"{unparsed} values did not read as a date",
            f"the column holds {n_present} values",
        )
    offsets = _counts(mapping["utc_offsets"], "utc_offsets", where, 1)
    named = 0
    for key in sorted(offsets):
        if not _is_an_offset(key):
            raise _out_of_range(
                f"utc_offsets -> {key}",
                where,
                f"'{key}'",
                "'Z', a signed offset like '+02:00', '(none)', or '(withheld)'",
            )
        if key == WITHHELD:
            continue
        named = named + 1
        if offsets[key] < floor:
            raise _broken(
                "D3",
                where,
                f"the offset '{key}' was carried by {offsets[key]} rows",
                f"the smallest group size is {floor}",
            )
    total = _added(offsets)
    if total != n_present - unparsed:
        raise _broken(
            "D2",
            where,
            f"the counted offsets come to {total}",
            (
                f"{n_present - unparsed} of the column's values read as a "
                f"date"
            ),
        )
    if named >= 2 and clock != "utc":
        raise _broken(
            "D5",
            where,
            f"{named} different offsets are named",
            f"the dates are published on the '{clock}' clock",
        )
    if resolution != "datetime":
        # ONLY A DATE AND TIME CARRIES AN OFFSET (invariant D9, review
        # item P2-C1-F6). A whole date and a quarter have no time of day
        # for an offset to move, and the shipped date reader reads
        # neither with one, so a description naming a real offset on
        # such a column asks for a cell -- a date with `+02:00` written
        # after it -- that reads back as no date at all. The producer
        # never writes one: an offset reaches a description only from a
        # value the date-and-time reading accepted.
        for key in sorted(offsets):
            if key == WITHHELD or key == NO_OFFSET:
                continue
            raise _broken(
                "D9",
                where,
                f"the offset '{key}' is named for a value of the column",
                f"its values are published as '{resolution}'",
            )
    earliest_offset = _endpoint_offset(
        mapping["earliest_utc_offset"], "earliest_utc_offset", where, offsets
    )
    latest_offset = _endpoint_offset(
        mapping["latest_utc_offset"], "latest_utc_offset", where, offsets
    )
    earliest = _canonical_datetime(
        mapping["earliest"], "earliest", where, resolution
    )
    latest = _canonical_datetime(mapping["latest"], "latest", where, resolution)
    ladder = _date_ladder(
        mapping["date_percentiles"], "date_percentiles", where, resolution
    )
    _endpoints_a_cell_can_show(
        where,
        resolution,
        precision,
        clock,
        earliest,
        latest,
        earliest_offset,
        latest_offset,
    )
    if ladder.minimum != earliest:
        raise _broken(
            "D11",
            where,
            f"the ladder of dates begins at {ladder.minimum}",
            f"the column's first value is {earliest}",
        )
    if ladder.maximum != latest:
        raise _broken(
            "D11",
            where,
            f"the ladder of dates ends at {ladder.maximum}",
            f"the column's last value is {latest}",
        )
    return DatetimeFacts(
        parser_family=parser_family,
        resolution=resolution,
        time_precision=precision,
        subsecond_digits=digits,
        datetimes_read_at=clock,
        earliest=earliest,
        latest=latest,
        earliest_utc_offset=earliest_offset,
        latest_utc_offset=latest_offset,
        date_percentiles=ladder,
        n_unparsed=unparsed,
        utc_offsets=offsets,
    )


def _minute_of(canonical: str) -> int:
    """The whole minute one canonical date and time names, in seconds.

    The seconds field is deliberately dropped: an end is written by
    moving its own minute onto the clock its offset names and then
    writing the published seconds field back unchanged, so the minute is
    what the move can carry out of the calendar. Whole-number arithmetic
    only, so the answer is the same on every machine.
    """
    days = parsing.days_from_civil(
        int(canonical[0:4]), int(canonical[5:7]), int(canonical[8:10])
    )
    return (
        86400 * days + 3600 * int(canonical[11:13]) + 60 * int(canonical[14:16])
    )


def _offset_seconds(offset: str) -> int:
    """How far one offset stands from the shared clock, in whole seconds.

    The two marker keys and an empty offset stand for a cell carrying no
    offset at all, which is written where the shared clock already put
    it and therefore moves by nothing.
    """
    if not offset or offset == "Z" or offset == NO_OFFSET or offset == WITHHELD:
        return 0
    seconds = 3600 * int(offset[1:3]) + 60 * int(offset[4:6])
    if offset[0] == "-":
        return -seconds
    return seconds


# The first and last minute the canonical form of 6.6.2 can spell. A cell
# outside them reads back as no date at all, which is why the pair that
# asks for one is refused here rather than written and named.
_FIRST_MINUTE = -62135596800
_LAST_MINUTE = 253402300740


def _endpoints_a_cell_can_show(
    where: str,
    resolution: str,
    precision: str,
    clock: str,
    earliest: str,
    latest: str,
    earliest_offset: str,
    latest_offset: str,
) -> None:
    """D10: an end no cell of this column's own shape could show.

    Both ends of a column of dates are exact facts with no corner and no
    exception (contract 9.6), so a pair of published facts that no cell
    can show AT ONCE is settled here, where it is decided, rather than
    paid for in the twin -- exactly as D6 settles the whole-date-beside-
    date-and-time pair. There are three such pairs, and the producer
    writes none of them:

    * the finest detail the column writes is a whole minute while an end
      carries seconds. A cell written to the minute has no seconds field
      to put them in, and the finest detail is the finest ANY cell
      writes, so a column that wrote seconds somewhere does not record
      the minute;
    * an end whose seconds field is 60 while the column's values are
      published on the shared clock. There the end names the instant on
      that clock, and reading any wall-clock cell back onto it moves a
      sixtieth second to the following minute, whatever cell carried it.
      A column reaches the shared clock only by having its ends put on
      that clock first, which is where a sixtieth second is resolved;
    * an end published on the shared clock whose own offset moves its
      cell off either end of the calendar this form can spell (review
      item P2-C4-F1). A column on the shared clock writes each cell on
      the wall clock its offset names, so an end within one offset's
      distance of the first or last minute of the years 0001 to 9999
      asks for a cell no reader can read back. Both directions are
      refused: an early end behind the shared clock and a late end ahead
      of it.

    The third pair was the fourth lowering of this one obligation, and
    the reason it is here: the loader holds the end, its offset and the
    clock, so the pair is decidable in the description and the twin owes
    nobody a lesser answer. Refusing costs the last second of a leap
    minute nothing on the local clock -- which is every column but the
    few that mix offsets -- where it is accepted and written back
    unchanged (review item P2-C3-F2).
    """
    if resolution != "datetime":
        return
    for key, published, offset in [
        ("earliest", earliest, earliest_offset),
        ("latest", latest, latest_offset),
    ]:
        seconds = published[17:19]
        if precision == "minute" and seconds != "00":
            raise _broken(
                "D10",
                where,
                f"the column's {key} value is {published}",
                (
                    "the finest detail it writes is a whole minute, which "
                    "leaves no place to write those seconds"
                ),
            )
        if clock == "utc" and seconds == "60":
            raise _broken(
                "D10",
                where,
                f"the column's {key} value is {published}",
                (
                    "its values are published on the shared clock, on "
                    "which no value reads back as a sixtieth second"
                ),
            )
        if clock != "utc":
            continue
        moved = _minute_of(published) + _offset_seconds(offset)
        if moved < _FIRST_MINUTE or moved > _LAST_MINUTE:
            raise _broken(
                "D10",
                where,
                (
                    f"the column's {key} value is {published} and the "
                    f"offset it was written under is '{offset}'"
                ),
                (
                    "moving that value onto the clock that offset names "
                    "leaves the years 0001 to 9999, which no value of "
                    "this form can spell"
                ),
            )


def _endpoint_offset(
    value: object, key: str, where: str, offsets: "dict[str, int]"
) -> str:
    """One endpoint's offset, which may not out-name the map (D4).

    An endpoint holds `(none)` when that endpoint's cell carried no
    offset at all; otherwise it holds that offset when the map names it,
    and `(withheld)` when the map is holding it back. A value published
    in one field of a block that another field of the same block
    promises to withhold is a contradiction the contract forbids.
    """
    found = _text(value, key, where)
    if not _is_an_offset(found):
        raise _out_of_range(
            key,
            where,
            f"'{found}'",
            "'Z', a signed offset like '+02:00', '(none)', or '(withheld)'",
        )
    if found == NO_OFFSET:
        return found
    if found not in offsets:
        raise _broken(
            "D4",
            where,
            f"the offset at that end is given as '{found}'",
            "the counted offsets of the column do not include it",
        )
    return found


def _numeric_facts(
    mapping: "dict[str, object]",
    where: str,
    frame: _Frame,
    n_present: int,
    n_numeric: int,
    n_out_of_range: int,
    n_contradictory: int,
) -> NumericFacts:
    """A column of counts or of continuous values (contract 6.7).

    Raises ProfileError for a wrong type or an out-of-range value, and
    for Q1 to Q11 and P1 to P3, in the directions the document supports.
    Where every parsed value is identical -- which the document states
    by giving the ladder the same value at both ends -- the spread, the
    shape and the average are all settled, and each is checked. Where it
    does not, `skew` being null cannot be checked against anything, and
    the contract says so rather than pretending otherwise.
    """
    ladder = _number_ladder(mapping["percentiles"], "percentiles", where)
    mean = _figure_or_nothing(mapping["mean"], "mean", where)
    std = _figure_or_nothing(mapping["std"], "std", where)
    skew = _figure_or_nothing(mapping["skew"], "skew", where)
    unrepresentable = _truth(
        mapping["std_unrepresentable"], "std_unrepresentable", where
    )
    n_zero = _whole(mapping["n_zero"], "n_zero", where, 0)
    n_negative = _whole(mapping["n_negative"], "n_negative", where, 0)
    n_negative_unrepresentable = _whole(
        mapping["n_negative_unrepresentable"],
        "n_negative_unrepresentable",
        where,
        0,
    )
    used = _whole(
        mapping["n_used_in_statistics"], "n_used_in_statistics", where, 0
    )
    left_out = _whole(
        mapping["n_left_out_of_statistics"],
        "n_left_out_of_statistics",
        where,
        0,
    )
    share = _share(mapping["numeric_share"], "numeric_share", where)
    integer_valued = _truth(
        mapping["integer_valued"], "integer_valued", where
    )
    echoed = _whole_row_count(mapping["n_rows"], "n_rows", where)
    if echoed != frame.n_rows:
        raise _broken(
            "Q1",
            where,
            "the row count this column repeats",
            "the row count at the top of the description",
        )
    if std is not None and std < 0.0:
        raise _out_of_range("std", where, f"{std}", "a number of 0 or more")
    if n_numeric < 1:
        raise _broken(
            "Q3",
            where,
            "the column records no value that reads as a number",
            "its type path needs at least one",
        )
    if used != n_numeric or left_out != n_present - n_numeric:
        raise _broken(
            "Q2",
            where,
            (
                f"the statistics used {used} values and left out "
                f"{left_out}"
            ),
            (
                f"{n_numeric} of the column's {n_present} values read as a "
                f"number"
            ),
        )
    if (std is None) != (used < 2 or unrepresentable):
        raise _broken(
            "Q4",
            where,
            (
                "the spread is left out"
                if std is None
                else f"the spread is {std}"
            ),
            (
                f"the statistics used {used} values, and the spread is "
                f"recorded as too large to hold: {unrepresentable}"
            ),
        )
    if used < 3 and skew is not None:
        raise _broken(
            "Q5",
            where,
            f"the shape is given as {skew}",
            f"the statistics used only {used} values",
        )
    flat = (
        ladder.minimum is not None
        and ladder.maximum is not None
        and ladder.minimum == ladder.maximum
    )
    if flat and skew is not None:
        raise _broken(
            "Q5",
            where,
            f"the shape is given as {skew}",
            "every value the statistics used is the same",
        )
    if not flat and used >= 3 and skew is None:
        raise _broken(
            "Q5",
            where,
            "the shape is left out",
            (
                f"the statistics used {used} values and they are not all "
                f"the same"
            ),
        )
    if flat and used >= 2 and (std != 0.0 or unrepresentable):
        raise _broken(
            "Q6",
            where,
            "every value the statistics used is the same",
            (
                f"the spread is given as {std}, and as too large to hold: "
                f"{unrepresentable}"
            ),
        )
    if flat and mean is None:
        raise _broken(
            "Q7",
            where,
            "the average is left out",
            (
                "every value is the same, so the average is that value and "
                "this format holds it"
            ),
        )
    exact = (n_numeric + n_out_of_range + n_contradictory) / n_present
    if share != exact:
        raise _broken(
            "Q9",
            where,
            f"the share of values meant as numbers is given as {share}",
            f"the counts in the block come to {exact}",
        )
    if (
        n_negative_unrepresentable > n_out_of_range
        or n_negative_unrepresentable > n_negative
    ):
        raise _broken(
            "Q10",
            where,
            (
                f"{n_negative_unrepresentable} values are negative and too "
                f"large to hold"
            ),
            (
                f"{n_out_of_range} values are too large to hold and "
                f"{n_negative} are negative"
            ),
        )
    if n_zero > n_numeric:
        raise _broken(
            "Q11",
            where,
            f"{n_zero} values are zero",
            f"{n_numeric} values read as a number",
        )
    styles = _numeric_styles(mapping, where, frame.floor, n_numeric)
    widths = _fraction_widths(mapping, where, frame.floor, styles)
    return NumericFacts(
        percentiles=ladder,
        mean=mean,
        std=std,
        skew=skew,
        std_unrepresentable=unrepresentable,
        n_zero=n_zero,
        n_negative=n_negative,
        n_negative_unrepresentable=n_negative_unrepresentable,
        n_used_in_statistics=used,
        n_left_out_of_statistics=left_out,
        numeric_share=share,
        integer_valued=integer_valued,
        n_rows=echoed,
        numeric_styles=styles,
        fraction_widths=widths,
    )


def _whole_row_count(value: object, key: str, where: str) -> int:
    """A row count, whose value never appears in a refusal.

    Reading a description can run out of memory before any field has
    been checked, so no message on this path may quote a row count
    (contract 10.7). The rule is applied to every row count rather than
    only to the ones a failing run would have reached, because a rule
    with an exception is a rule somebody applies wrongly later.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise _wrong_type(key, where, value, "a whole number")
    if value < 0:
        raise _row_count_out_of_range(
            key, where, "a whole number of 0 or more"
        )
    return value


def _numeric_styles(
    mapping: "dict[str, object]", where: str, floor: int, n_numeric: int
) -> "dict[str, int]":
    """How many cells used each way of writing a number (7.5).

    Raises ProfileError for an unknown style name, a wrong type, and for
    P1 to P3. The fact is about FORM and not about values: it carries no
    value, no magnitude and no spelling. `integer_valued` is checked
    against nothing here, and deliberately (P4): a cell written `5.0` is
    a whole number written with a point, so the two facts are
    independent.
    """
    styles = _counts(mapping["numeric_styles"], "numeric_styles", where, 1)
    if not styles:
        raise _broken(
            "P3",
            where,
            "the column says nothing about how its numbers were written",
            f"{n_numeric} of its values read as a number",
        )
    for name in sorted(styles):
        if name != WITHHELD and name not in NUMERIC_STYLES:
            raise _out_of_range(
                f"numeric_styles -> {name}",
                where,
                f"'{name}'",
                _listed(NUMERIC_STYLES + (WITHHELD,)),
            )
        if name != WITHHELD and styles[name] < floor:
            raise _broken(
                "P2",
                where,
                f"the form '{name}' was used by {styles[name]} cells",
                f"the smallest group size is {floor}",
            )
    total = _added(styles)
    if total != n_numeric:
        raise _broken(
            "P1",
            where,
            f"the cells counted by the form they were written in come to {total}",
            f"{n_numeric} of the column's values read as a number",
        )
    # P6. THE POOL CANNOT HOLD MORE THAN THE FORMS IN IT. There are
    # exactly six ways to write a number, a form is pooled only when
    # its own count falls BELOW the floor, and a form this map names is
    # not in the pool -- so the remainder is bounded by however many
    # forms are left times one less than the floor. Nothing checked it,
    # and the gap was not small: a column of two hundred and forty
    # numbers naming `plain` and `decimal` could publish a pool of
    # sixty, which four forms holding at most ten each cannot make.
    # `generate` then told its reader the TWIN had missed a fact, when
    # what had happened is that the description was altered after
    # synthtwin wrote it.
    named = 0
    for name in sorted(styles):
        if name != WITHHELD:
            named = named + 1
    pooled = styles[WITHHELD] if WITHHELD in styles else 0
    room = (len(NUMERIC_STYLES) - named) * (floor - 1)
    if pooled > room:
        raise _broken(
            "P6",
            where,
            f"{pooled} cells are held back from the forms map",
            f"the {len(NUMERIC_STYLES) - named} form(s) it does not "
            f"name can hold at most {floor - 1} cells each",
        )
    return styles


def _fraction_widths(
    mapping: "dict[str, object]",
    where: str,
    floor: int,
    styles: "dict[str, int]",
) -> "dict[str, int]":
    """How many figures the cells written with a point wrote after it.

    ITS SUM IS STATED OVER A NUMBER THAT MAY NOT EXIST, and that is the
    whole difficulty this reads through (plan amendments A-P4-5 and
    A-P4-6). Where the floor named the decimal form, `numeric_styles`
    carries a `decimal` key and the census sums to it exactly. Where
    the floor POOLED that form, no published number holds the count of
    decimal cells -- and an earlier reading concluded the sum obligation
    then binds nothing, which would have admitted a census of a
    thousand decimal cells in a column of a hundred. Three published
    numbers bound it instead:

    1. non-empty means a total of at least one;
    2. the total is strictly BELOW the floor, because a form is pooled
       only when its own count falls below it;
    3. the total is at most the pooled remainder of the forms map,
       because the pooled decimal cells are a subset of that pool.

    The census may also be empty in the pooled case, which is what a
    column with no decimal cell at all writes.

    Raises ProfileError for a wrong type, a key that is not a canonical
    width, a named width below the floor, and for each of the four
    cases above.
    """
    widths = _counts(mapping["fraction_widths"], "fraction_widths", where, 1)
    for name in sorted(widths):
        if name == WITHHELD:
            continue
        if not _is_canonical_width(name):
            raise _out_of_range(
                f"fraction_widths -> {name}",
                where,
                f"'{name}'",
                "a whole number of figures written without padding",
            )
        if widths[name] < floor:
            raise _broken(
                "P5",
                where,
                f"the width '{name}' was written by {widths[name]} cells",
                f"the smallest group size is {floor}",
            )
    total = _added(widths)
    if DECIMAL_STYLE in styles:
        if total != styles[DECIMAL_STYLE]:
            raise _broken(
                "P5",
                where,
                f"the cells counted by the figures they wrote after the "
                f"point come to {total}",
                f"{styles[DECIMAL_STYLE]} cells were written with a point",
            )
        return widths
    # THE POOL'S CAPACITY IS CHECKED BEFORE THE EMPTY CASE AND NOT
    # AFTER IT. An empty census is a claim -- that NO cell of this
    # column was written with a point -- and it is as checkable as any
    # other: the pool then holds five forms rather than six, so a
    # column whose forms map pools fifty-one cells at a floor of eleven
    # is impossible with an empty census and was accepted. Returning
    # early on a total of zero is what skipped the one condition an
    # empty census can break.
    pooled = styles[WITHHELD] if WITHHELD in styles else 0
    room = 5 * (floor - 1)
    if pooled - total > room:
        raise _broken(
            "P5",
            where,
            f"{total} of the {pooled} cells held back from the forms "
            "map are counted as written with a point",
            f"the {pooled - total} others would have to share five "
            f"forms holding at most {floor - 1} cells each",
        )
    if not total:
        return widths
    if total >= floor:
        raise _broken(
            "P5",
            where,
            f"{total} cells are counted as written with a point",
            "no such form is named at all, so every one of them was "
            f"held back and there are fewer than {floor}",
        )
    if total > pooled:
        raise _broken(
            "P5",
            where,
            f"{total} cells are counted as written with a point",
            f"{pooled} cells in all were held back from the forms map",
        )
    return widths


def _is_canonical_width(name: str) -> bool:
    """Whether one census key is a width written the one permitted way.

    Decimal figures, no sign, no padding: `0` written as itself and
    nothing else beginning with a zero. A grammar left to be inferred is
    a grammar two producers spell differently and a consumer reads as
    two widths.
    """
    if not name:
        return False
    for character in name:
        if character not in "0123456789":
            return False
    if name == "0":
        return True
    return name[:1] != "0"


def _identifier_facts(
    mapping: "dict[str, object]",
    where: str,
    n_present: int,
    n_distinct: int,
) -> IdentifierFacts:
    """A column the person declared to hold record numbers (6.8).

    Raises ProfileError for a wrong type or an out-of-range count, and
    for I1, I2 and I4. I3 -- that no value of the table appears anywhere
    in the block -- is checked where the two fields it governs are read,
    because it is a property of the whole block and not of this half of
    it.
    """
    smallest = _whole(mapping["min_length"], "min_length", where, 1)
    largest = _whole(mapping["max_length"], "max_length", where, 1)
    if smallest > largest:
        raise _broken(
            "I4",
            where,
            f"the shortest value is {smallest} characters",
            f"the longest is {largest}",
        )
    pattern, pairs = _multiplicity(
        mapping["n_distinct_by_occurrences"],
        "n_distinct_by_occurrences",
        where,
        None,
    )
    _pattern_closes(pairs, where, "I2", n_distinct, n_present)
    return IdentifierFacts(
        min_length=smallest,
        max_length=largest,
        all_whole_numbers=_truth(
            mapping["all_whole_numbers"], "all_whole_numbers", where
        ),
        n_all_digits=_bounded(
            mapping["n_all_digits"], "n_all_digits", where, 0, n_present,
            "the number of values the column holds",
        ),
        n_code_alphabet=_bounded(
            mapping["n_code_alphabet"], "n_code_alphabet", where, 0, n_present,
            "the number of values the column holds",
        ),
        n_distinct_by_occurrences=pattern,
    )


def _line_count(share: float, total: int) -> int:
    """The smallest whole number of values that reaches ``share``.

    THE PRODUCER'S OWN RULE, written again here rather than imported:
    the loader may not import the describing side, and a threshold
    applied as a count on one side and as a compared share on the other
    is a threshold two implementations disagree about at the boundary.
    A count is what both apply.
    """
    exact = share * total
    whole = int(exact)
    if whole < exact:
        return whole + 1
    return whole


def _affixed_facts(
    mapping: "dict[str, object]",
    where: str,
    frame: _Frame,
    n_present: int,
    remarks: "list[str]",
) -> AffixedFacts:
    """Read an affixed-number block (contract 6.12).

    The quantitative invariants are read over the CORE counts, because
    that is the population the statistics were computed from -- except
    the two the contract defines over present CELLS, which the numeric
    reader is given `n_present` for and which would otherwise leave a
    straggler in neither count.
    """
    prefix = _text(mapping["affix_prefix"], "affix_prefix", where)
    suffix = _text(mapping["affix_suffix"], "affix_suffix", where)
    if not prefix and not suffix:
        # AF1. A pair with nothing on either side describes no shape,
        # and a cell wearing it is a bare number, which is a different
        # role.
        raise _out_of_range(
            "affix_prefix", where, "two empty spellings",
            "at least one side carrying text",
        )
    n_affixed = _bounded(
        mapping["n_affixed"], "n_affixed", where, frame.floor, n_present,
        "the number of values the column holds",
    )
    # AF3. The pair had to clear the detection line for this role to be
    # given at all, and the line is a COUNT of the present cells rather
    # than a share compared after a division -- so a block claiming the
    # role with fewer cells wearing the pair than its own settings
    # demand describes a column the producer would have declined.
    # Applied here because nothing else could: the loader holds one
    # document and the settings that wrote it, which is exactly what
    # this invariant is stated over.
    line = _line_count(frame.parse_rate, n_present)
    if n_affixed < line:
        raise _out_of_range(
            "n_affixed", where, f"{n_affixed}",
            f"at least {line}, the number of this column's values that "
            "had to wear one shared piece of text for it to be read "
            "this way at all",
        )
    core_numeric = _bounded(
        mapping["n_core_numeric"], "n_core_numeric", where, 0, n_affixed,
        "the number of values wearing the pair",
    )
    core_out_of_range = _bounded(
        mapping["n_core_out_of_range"], "n_core_out_of_range", where,
        0, n_affixed, "the number of values wearing the pair",
    )
    core_contradictory = _bounded(
        mapping["n_core_contradictory"], "n_core_contradictory", where,
        0, n_affixed, "the number of values wearing the pair",
    )
    core_not_numeric = _bounded(
        mapping["n_core_not_numeric"], "n_core_not_numeric", where,
        0, n_affixed, "the number of values wearing the pair",
    )
    # AF4: the four core classes are a partition of the cells wearing
    # the pair, so they close on `n_affixed` and on nothing else.
    total = (
        core_numeric
        + core_out_of_range
        + core_contradictory
        + core_not_numeric
    )
    if total != n_affixed:
        raise _out_of_range(
            "n_core_numeric", where, f"a total of {total}",
            f"a total of {n_affixed}, the number of values wearing the pair",
        )
    # AF-R, ASKED WHERE THE BLOCK'S OWN NUMBERS ARE. It is
    # unconditional -- no test of the values can separate a column of
    # measurements from a column of codes, so the sentence is owed by
    # every column of this role and not by the ones some rule found
    # doubtful. It is asked HERE rather than beside the other remarks
    # because here the pair and the count are already read: a check
    # written where the facts are still a union of every role's would
    # have to ask which role it holds, and asking that is a construct
    # the offline audit refuses on a value it cannot trace.
    carried = False
    for remark in remarks:
        if _is_the_affixed_remark(
            remark, n_affixed, _affix_clause(prefix, suffix)
        ):
            carried = True
    if not carried:
        raise _out_of_range(
            "remarks",
            where,
            f"{len(remarks)} remark(s), none of them that one",
            "the sentence every column read this way carries, "
            "which names the shared text its values wear, says how "
            "many of them wore it, and says what to run if they "
            "are codes rather than measurements",
        )
    return AffixedFacts(
        numbers=_numeric_facts(
            mapping,
            where,
            frame,
            n_present,
            core_numeric,
            core_out_of_range,
            core_contradictory,
        ),
        affix_prefix=prefix,
        affix_suffix=suffix,
        n_affixed=n_affixed,
        n_core_numeric=core_numeric,
        n_core_out_of_range=core_out_of_range,
        n_core_contradictory=core_contradictory,
        n_core_not_numeric=core_not_numeric,
    )


def _text_facts(
    mapping: "dict[str, object]",
    where: str,
    n_present: int,
    n_distinct: int,
) -> TextFacts:
    """A column no rule claimed (contract 6.9).

    Raises ProfileError for a wrong type or an out-of-range count, and
    for F1, F2 and F4. F3 -- that no value of the table appears anywhere
    in the block -- is checked where the two fields it governs are read.
    """
    length = _mapping(mapping["length"], "length", where)
    _keys(length, where, LENGTH_KEYS, "every column of text")
    words = _mapping(mapping["words"], "words", where)
    _keys(words, where, WORD_KEYS, "every column of text")
    shortest = _whole(length["min"], "length -> min", where, 1)
    longest = _whole(length["max"], "length -> max", where, 1)
    mean_length = _figure_or_nothing(length["mean"], "length -> mean", where)
    middle = _figure_or_nothing(length["p50"], "length -> p50", where)
    fewest = _whole(words["min"], "words -> min", where, 0)
    most = _whole(words["max"], "words -> max", where, 0)
    mean_words = _figure_or_nothing(words["mean"], "words -> mean", where)
    _between(shortest, longest, mean_length, where, "the average length")
    _between(shortest, longest, middle, where, "the middle length")
    _between(fewest, most, mean_words, where, "the average word count")
    if shortest > longest:
        raise _broken(
            "F1",
            where,
            f"the shortest value is {shortest} characters",
            f"the longest is {longest}",
        )
    if fewest > most:
        raise _broken(
            "F1",
            where,
            f"the fewest words in a value is {fewest}",
            f"the most is {most}",
        )
    pattern, pairs = _multiplicity(
        mapping["n_distinct_by_occurrences"],
        "n_distinct_by_occurrences",
        where,
        None,
    )
    _pattern_closes(pairs, where, "F2", n_distinct, n_present)
    return TextFacts(
        length=LengthStats(
            minimum=shortest, maximum=longest, mean=mean_length, p50=middle
        ),
        words=WordStats(minimum=fewest, maximum=most, mean=mean_words),
        n_all_digits=_bounded(
            mapping["n_all_digits"], "n_all_digits", where, 0, n_present,
            "the number of values the column holds",
        ),
        n_code_alphabet=_bounded(
            mapping["n_code_alphabet"], "n_code_alphabet", where, 0, n_present,
            "the number of values the column holds",
        ),
        n_distinct_by_occurrences=pattern,
    )


def _between(
    least: int, most: int, value: "float | None", where: str, what: str
) -> None:
    """F1: one statistic of a column of text lies inside its own ends."""
    if value is None:
        return
    if value < least or value > most:
        raise _broken(
            "F1",
            where,
            f"{what} is {value}",
            f"the values it describes run from {least} to {most}",
        )
    return


# -- the whole document -----------------------------------------------


def _columns(
    value: object, frame: _Frame
) -> "tuple[ColumnBlock, ...]":
    """Every column block, in the document's own list order (S1 to S4)."""
    listed = _listing(value, "columns", _AT_THE_TOP)
    if len(listed) != frame.n_columns:
        raise _broken(
            "S1",
            _AT_THE_TOP,
            f"the list of columns holds {len(listed)} blocks",
            f"the description says the table has {frame.n_columns} columns",
        )
    blocks: list[ColumnBlock] = []
    seen: list[str] = []
    index = 0
    for entry in listed:
        block = _column(entry, index, frame)
        if block.name in seen:
            raise _broken(
                "S4",
                f"in the block for the column named '{block.name}'",
                f"the name '{block.name}' is used more than once",
                "every column of a table has its own name",
            )
        seen = seen + [block.name]
        blocks = blocks + [block]
        index = index + 1
    return tuple(blocks)


def _cross_checks(
    columns: "tuple[ColumnBlock, ...]",
    settings: SettingsBlock,
    notes: "tuple[PublicationNote, ...]",
) -> None:
    """The three rules that need the columns and something else.

    S8: every name declared as holding record numbers is a column of
    this table -- a name that matches no column means the description
    and the schema disagree about which columns were declared. S10:
    every note is about a column of this table. S11: the notes are
    grouped by column, in the order the columns come in the table.
    """
    places: dict[str, int] = {}
    for column in columns:
        places[column.name] = column.position
    for name in settings.forced_identifiers:
        if name not in places:
            raise _broken(
                "S8",
                "in the block of rules that produced the description",
                f"'{name}' is named as holding record numbers",
                "this table has no column of that name",
            )
    previous = 0
    place = 0
    for note in notes:
        seat = f"in note number {place + 1} of the notes about what was held back"
        if note.column not in places:
            raise _broken(
                "S10",
                seat,
                f"the note is about a column called '{note.column}'",
                "this table has no column of that name",
            )
        if places[note.column] < previous:
            raise _broken(
                "S11",
                seat,
                f"the note is about the column at place {places[note.column]}",
                f"the note before it is about the column at place {previous}",
            )
        previous = places[note.column]
        place = place + 1


# -- S13: what a floor of one leaves no room for ----------------------
#
# The floor's second half is the range below it, and at a floor of one
# that range is empty. Everything a description writes into that half
# therefore has to be empty too. There are five ways to write into it,
# and three of them were already refused by the rule that governs them:
# B5 reads `suppressed_level_counts` against the range, `_multiplicity`
# reads `variants_withheld`'s keys against it, and B4 ties
# `suppressed_levels` and `suppressed_rows` to the sizes. The other two
# were refused nowhere until amendment A-P3-16, and they are what this
# section adds.
#
# THE POOLED REMAINDER IS FOUND BY WALKING, NOT BY A LIST OF FIELDS.
# `(withheld)` is the format's one word for "held back" (section 14),
# and every pooled remainder in the document is a count standing under
# it: `missing_by_class`, `utc_offsets` and `numeric_styles` today, and
# `missing_by_source` too until version 5 moved its remainder out into
# `n_missing_withheld`. Listing those would leave the next one somebody
# adds unchecked, in exactly the way that left this rule unenforced for
# the first four -- each of them WAS checked where it was written, and
# each check exempted the remainder. The walk below reaches a counted
# entry under that word wherever a field puts it, except where the TABLE
# rather than the format decides the key: that bound is below.
#
# THE UNNAMED TALLY IS NAMED, because the format gives it no marker to
# be found by. `n_sentinel_candidates_unpublished` counts the stand-in
# numbers held by fewer rows than the floor (invariant V1), and it says
# so in a field name rather than in the pooled-remainder word. It is the
# only such field in version 4, and that is measured rather than
# assumed: `tests/test_p3v5f1_floor_one.py` describes one table at the
# default floor and at one and requires every position of the document
# that moves to be a position this rule reaches.

# The two fields that say "held back" in their name rather than under
# the pooled-remainder word, and the two ways a refusal reads. Both are
# FIELD names, so both are read as names only where the format decides
# the keys -- a cell that spells one of them is a cell, not a field.
#
# `n_missing_withheld` joined them at contract version 5 (C5-S13): it is
# the pooled remainder that used to stand under the word inside
# `missing_by_source`, moved out so that the map holds one key space.
# The rule it is held to is unchanged -- at a floor of one nothing may
# be pooled, because the range below one is empty.
_UNNAMED_TALLY = "n_sentinel_candidates_unpublished"
_NAMED_REMAINDER = "n_missing_withheld"
_POOLED = "pooled"
_TOO_RARE = "too-rare"

# WHERE THE WALK MAY NOT READ A KEY AS A WORD (C5-N5; plan amendment
# A-P3-32, review item P3-V9-F2). The walk below reads a key as this
# package's own word, which is sound wherever the format fixes the key
# names and wrong wherever the TABLE fixes them: a cell can say
# `(withheld)`, and a cell can just as easily say `n_missing_withheld`
# or `n_sentinel_candidates_unpublished`. Refusing those would refuse
# descriptions version 5 exists to make writable.
#
# Which mappings those are is `canonical.TABLE_TEXT_KEY_SPACES`, read
# from there rather than named here, because the producer's guard has to
# answer this question the same way and a second list would let the two
# drift. The version this replaces named ONE mapping and only for the
# word `(withheld)`, so three doors were left open: a categorical label
# reading `n_missing_withheld` wrote a description this loader refused,
# the same label reading `(withheld)` was refused by the producer before
# it could be written, and both told the person their untouched file had
# been edited.
#
# AND THE WALK STOPS AT SUCH A KEY RATHER THAN READING PAST IT (review
# item P3-V10-F3). Not reading the KEY as a word was half the answer.
# The walk went on into the value anyway, so a document whose
# `missing_by_source` held a BLOCK instead of a count -- which is not a
# document this producer can write, and not one this loader may accept
# -- had that block's own field names read as names again, one step
# below a key the table decided. Two things then went wrong at once:
# this rule fired where the type rule should have, so the person was
# told their file had been edited in a place that says nothing about
# editing; and the path it printed carried the table's spelling onto
# the screen, which is the one thing this walk's stated boundary says
# it never does. What stands under a key the table decides is a COUNT
# (C5-N5), a count has nothing under it, and a value that is not one is
# refused by the rule that reads its type -- naming the kind and never
# the spelling (R15).


def _step(path: "tuple[object, ...]", key: object) -> "tuple[object, ...]":
    """One step further into the document."""
    return path + (key,)


def _is_a_row_count(value: object) -> bool:
    """A whole number of one or more, and not a yes/no."""
    if isinstance(value, bool):
        return False
    return isinstance(value, int) and value > 0


def _held_back_in(
    node: object, path: "tuple[object, ...]"
) -> "list[tuple[tuple[object, ...], int, str]]":
    """Every place this part of the document holds something back.

    Guarantees:

    - Inputs: any part of the parsed document, and the path of keys and
      list places that reached it.
    - Determinism: the answer depends only on the value; every block's
      keys are read in sorted order and every list in its own order.
    - Errors raised: none. It reports, and the rule above decides.
    - Boundary: nothing is opened, and no value of the table is read --
      the two things this finds are counts of rows and counts of
      candidates, and a held-back thing names nothing by definition. NO
      PATH THIS RETURNS EVER STEPS THROUGH A KEY THE TABLE DECIDES, so
      the place the refusal names above can be printed whole without
      quoting a spelling: the walk stops at such a mapping instead of
      reading past it.

    Returns (path, count, what kind of holding back) for each one.
    """
    found: list[tuple[tuple[object, ...], int, str]] = []
    if isinstance(node, dict):
        # Whether the TABLE decides the keys here. Where it does the
        # walk stops: no key is read as one of this package's words --
        # not the pooled remainder's word and not either field name,
        # because every one of them is something a cell can say -- and
        # nothing under such a key is read at all, because what stands
        # there is a count and a count has nothing under it. A document
        # that puts a block there is malformed, and the rule that reads
        # the value's TYPE refuses it, naming the kind and not the
        # spelling.
        if canonical.keys_are_the_tables_own_text(path):
            return found
        for key in sorted(node):
            value = node[key]
            here = _step(path, key)
            if key == WITHHELD and _is_a_row_count(value):
                found = found + [(here, value, _POOLED)]
            if key == _NAMED_REMAINDER and _is_a_row_count(value):
                found = found + [(here, value, _POOLED)]
            if key == _UNNAMED_TALLY and _is_a_row_count(value):
                found = found + [(here, value, _TOO_RARE)]
            found = found + _held_back_in(value, here)
    elif isinstance(node, list):
        place = 0
        for item in node:
            found = found + _held_back_in(item, _step(path, place))
            place = place + 1
    return found


def _named_place(
    document: "dict[str, object]", path: "tuple[object, ...]"
) -> "tuple[str, str]":
    """Where a path sits, and what it is called, in a person's words.

    A path inside a column block is read to the person as that column's
    name, exactly as every other refusal about a block is; anything else
    is at the top of the description. The field is then written from
    whatever is left, in the document's own key names, because that is
    what somebody looking at the file will be searching for.

    EVERY STEP IT PRINTS IS ONE OF THE DOCUMENT'S OWN KEY NAMES, and
    that is a property of the only walk that feeds it: `_held_back_in`
    stops at a mapping the table keys, so no path reaching here has ever
    stepped through a spelling out of somebody's table (review item
    P3-V10-F3). This function does not re-check it -- it is not the
    place where the question can be answered, because a key name and a
    cell's text are the same kind of thing by the time they are here.
    `tests/test_p3v10f3_the_walk_stops_at_the_tables_keys.py` measures it
    on the walk instead.
    """
    rest = path
    seat = _AT_THE_TOP
    if len(path) > 1 and path[0] == "columns":
        blocks = document["columns"]
        index = path[1]
        if isinstance(blocks, list) and isinstance(index, int):
            block = blocks[index]
            if isinstance(block, dict) and "name" in block:
                name = block["name"]
                if isinstance(name, str):
                    seat = f"in the block for the column named '{name}'"
                    rest = path[2:]
    field = ""
    for step in rest:
        if isinstance(step, int):
            field = f"{field}[{step + 1}]"
        elif field:
            field = f"{field} -> {step}"
        else:
            field = f"{step}"
    return seat, field


def _nothing_is_held_back(document: "dict[str, object]", floor: int) -> None:
    """Invariant S13, over the whole document at once.

    Guarantees:

    - Inputs: the parsed document and the floor its settings carry. It
      runs with the top-level rules, before any column is read: what it
      reads is the floor, which is a top-level setting, and what it says
      is a fact about the whole description rather than about one block.
      Nothing here assumes a column block has been checked -- every step
      of the walk asks what it has before it uses it -- because the
      columns have not been.
    - Determinism: a fixed function of the document and the floor. The
      walk is ordered, so a document breaking this rule twice always
      meets the same refusal.
    - Errors raised: ProfileError (R17, rule S13), naming the field and
      the count. It may say the count because a held-back thing names
      nothing: it is the number of rows the floor took out of sight, and
      at a floor of one no row was.
    - Boundary: no value of the table is read or quoted.

    ABOVE A FLOOR OF ONE THIS RULE SAYS NOTHING, and deliberately. A
    remainder pools SEVERAL groups that each fell below the floor, so at
    a floor of eleven a remainder of twelve is ordinary -- three
    spellings of four rows each, say. The only bound the arithmetic
    gives is the one at the bottom, where the range below the floor is
    empty and every remainder must be nothing at all.
    """
    if _below_the_floor(floor):
        return
    for path, count, kind in _held_back_in(document, ()):
        seat, field = _named_place(document, path)
        raise _broken(
            "C5-S13",
            seat,
            (
                f"'{field}' holds {count} row(s) back"
                if kind == _POOLED
                else (
                    f"'{field}' counts {count} stand-in number(s) as too "
                    f"rare to name"
                )
            ),
            # The second clause is the house wording every other
            # floor-governed refusal ends with, so that a person who has
            # met one of them reads this one the same way.
            f"the smallest group size is {floor}",
        )


def _validated(document: "dict[str, object]") -> Profile:
    """Step 7 and step 8: every rule, then the typed objects (10.1).

    The top level is checked first and the columns afterwards, in list
    order, so that a person reading a refusal meets the outermost thing
    that is wrong. The three rules that need both halves -- S8, S10 and
    S11 -- run at the end, because until the columns have been read
    there is nothing to check the names against.
    """
    _keys(
        document,
        _AT_THE_TOP,
        TOP_LEVEL_KEYS,
        "every description synthtwin writes",
    )
    n_columns = _whole(document["n_columns"], "n_columns", _AT_THE_TOP, 1)
    n_rows = _whole_row_count(document["n_rows"], "n_rows", _AT_THE_TOP)
    created_with = _filled_text(
        document["created_with"], "created_with", _AT_THE_TOP
    )
    source = _source(document["source"])
    settings = _settings(document["settings"])
    relationships = _relationships(document["relationships"])
    notes = _notes(document["publication_notes"])
    # S13 IS A TOP-LEVEL RULE AND RUNS WITH THE TOP LEVEL. What it reads
    # is the floor, which lives in `settings`, and what it says is a fact
    # about the whole description: it was made at a floor of one and it
    # holds something back. That is outermost, and it is nearer the cause
    # than the column rule a spliced-in field breaks on the way past --
    # a total that does not add up, when the reason it does not is that
    # somebody moved a field out of a description made at another floor.
    _nothing_is_held_back(document, settings.small_cell_floor)
    columns = _columns(
        document["columns"],
        _Frame(
            floor=settings.small_cell_floor,
            n_rows=n_rows,
            n_columns=n_columns,
            declared=settings.forced_identifiers,
            parse_rate=settings.minimum_parse_rate,
        ),
    )
    _cross_checks(columns, settings, notes)
    return Profile(
        profile_version=PROFILE_VERSION,
        created_with=created_with,
        n_rows=n_rows,
        n_columns=n_columns,
        source=source,
        settings=settings,
        relationships=relationships,
        publication_notes=notes,
        columns=columns,
    )


def load_profile(raw_path: str) -> Profile:
    """Read one profile document, or refuse it (contract section 10).

    Guarantees:

    - Inputs: ``raw_path`` is the path a person typed or a command
      built. It passes `validate_local_path` (plan D6.1) before anything
      is opened, so a URL form, a shared-network form and a Windows
      device form are all refused lexically before any filesystem call.
      Nothing else is accepted: no table path, no open file, no already
      parsed value.
    - Determinism: the same bytes always give the same result. Nothing
      here reads a clock, an environment variable or a random source,
      and the returned columns are in the document's own list order.
    - Errors raised: ProfileError, with one plain-language message for
      each of the nineteen ways this can fail (contract 10.7), and
      PathValidationError when the path is not a plain local one. Every
      message says what happened and what to do next; none of them
      quotes a row count, because reading can run out of memory before
      any field has been checked and a message that names a row count it
      never read is a message that lies.
    - Boundary: THE GENERATOR NEVER READS THE REAL TABLE. This function
      opens the description and nothing else, builds no table path and
      no table object, and reaches neither the reader nor pandas through
      anything it imports (plan P2-D1). It is the only way generation
      receives a profile.

    It is fail-closed: a description it cannot prove conforming is
    refused, never repaired and never partly accepted. It performs no
    generation feasibility check -- whether a valid description can be
    met is a separate stage that runs afterwards, so that a valid
    description never becomes unloadable.
    """
    validated = validate_local_path(raw_path, purpose="description")
    place = pathlib.Path(validated)
    shown = f"{place}"
    if not place.exists():
        raise errors.ProfileError(errors.profile_file_missing(shown))
    if place.is_dir():
        raise errors.ProfileError(errors.profile_path_is_a_folder(shown))
    try:
        text = _read_text(place)
        size = _file_size(place)
    except UnicodeDecodeError as error:
        raise errors.ProfileError(errors.profile_not_text(shown)) from error
    except MemoryError as error:
        raise errors.ProfileError(
            errors.profile_out_of_memory(shown)
        ) from error
    except PermissionError as error:
        raise errors.ProfileError(
            errors.profile_file_unreadable(shown, f"{error}")
        ) from error
    except OSError as error:
        raise errors.ProfileError(
            errors.profile_file_unreadable(shown, f"{error}")
        ) from error
    try:
        _scanned(text, shown)
        document = _versioned(_parsed(text, shown), shown)
        _round_tripped(document, text, size, shown)
        return _validated(document)
    except MemoryError as error:
        raise errors.ProfileError(
            errors.profile_out_of_memory(shown)
        ) from error

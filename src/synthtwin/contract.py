"""The strict profile loader: the only way generation gets a profile.

The normative text is `docs/spec/profile-contract-v6.md`, and
`PROFILE_VERSION` below is 6: a description this tree writes is a
version 6 one, and this loader accepts no other. Version 6 states the
whole contract, and it stands on the two documents it supersedes --
version 5, which carried version 4 by reference. This module carries
the rules out one for one. Nothing here decides anything the contract
left open; where it states a fact, the check below cites it by its own
identifier so a reader can hold the two side by side. An identifier
beginning `C6-` is version 6's own, one beginning `C5-` is a version 5
rule version 6 keeps, and every other is a version 4 rule carried
through both -- the identifier records where a rule was WRITTEN, not
which document governs, and the document that governs is version 6.

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
  5. read `profile_version`, which must be 6       R11, R12
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

from synthtwin import canonical, dialect, errors, parsing
from synthtwin.paths import validate_local_path

# The one version this loader reads. `profile_version` must be exactly
# this integer: an older document gets advice to make the description
# again, a newer one gets advice to update synthtwin and NEVER to re-run
# a profiler on a machine that may not hold the table (contract 10.6).
#
# IT IS SIX, AND THERE IS NO UPGRADE PATH FROM EITHER OLDER VERSION
# (owner ruling 2026-08-17 for version 5; amendment A-P4-41, which
# extends version 6 IN PLACE until the first release rather than
# bumping it each time a key is added). The value is written once,
# below, and every sentence about it says "this integer" rather than
# naming a number -- three sites said FIVE while the value was 6, and a
# contributor following any of them prepares a description the loader
# refuses (residual R-P4-63).
#
# An older document is refused, not converted: it records a declaration
# only as a count, so converting it would mean making up the facts the
# older rules did not record, which is the whole reason a new version
# exists. The refusal names both versions, says WHY the older file
# cannot be read back, and tells the person to describe their table
# again WITH THE SAME `--keep-value` AND `--missing-value` OPTIONS --
# advice that is safe today because there is no release and every
# description belongs to somebody who still holds the table, and that
# is re-examined rather than inherited after the first one.
PROFILE_VERSION = 6

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

# THE STATE A CENSUS REACHES WHERE IT CANNOT SPEAK WITHOUT NAMING
# SOMEBODY (landing 2b.7; the producer's own `taxonomy.UNAVAILABLE_LABEL`).
#
# It is NOT `(withheld)` and the difference is the whole of the key.
# That word says "these cells, and fewer of them than the floor", which
# still names the category it is holding back wherever the census has
# only one category to name -- so `{}` beside `{"(withheld)": 1}` told a
# reader which single cell of 1,200 carried a plus. This says nothing:
# not the count, and not whether the count is nought, which is what
# makes nought and a below-floor count ONE published state. Its count is
# always nought, because a number beside it would be the disclosure over
# again.
UNAVAILABLE = "(unavailable)"

# EVERY MARK A CENSUS OF MARKS MAY NAME: the marks a description may
# publish, less the empty one. A cell counted here PROVED a mark, so
# "no mark" is not a convention it can have worn -- an ungrouped cell is
# counted nowhere in that census rather than under a key of its own.
# Taken from the published tuple rather than written out again, so the
# two cannot drift.
_PUBLISHED_MARKS_NAMED = parsing.PUBLISHED_GROUP_MARKS[1:]
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
    "dialect",
    "encoding",
    "header_by_convention",
    "header_evidence",
    "header_source",
    "used_fallback_encoding",
    "workbook",
)

SETTINGS_KEYS = (
    "categorical_ceiling",
    "categorical_floor",
    "categorical_share",
    "declaration_matching",
    "declaration_publication",
    "declared_missing_values",
    "forced_codes",
    "forced_decimal_commas",
    "forced_delimiter",
    "forced_identifiers",
    "forced_measurements",
    "forced_metadata_rows",
    "identifier_minimum_rows",
    "identifier_uniqueness",
    "kept_values",
    "minimum_parse_rate",
    "near_threshold_slack",
    "day_first",
    "long_tail_minimum_level",
    "sentinel_minimum_share",
    "sentinel_outlier_iqr_multiple",
    "small_cell_floor",
)

# The four keys of each declaration record (contract 5 section 6.2,
# invariant C5-S14). Version 4 had the first two; version 5 adds the two
# lists that say which members of this package's OWN published
# vocabulary a declaration named, and never a spelling of the person's.
DECLARATION_KEYS = (
    "built_in_dates",
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
DEFAULT_SMALL_CELL_FLOOR = 1

# THE NUMBER BELOW WHICH A PUBLISHED GROUP CAN POINT AT ONE PERSON, and
# it is NOT the default any more (plan amendment A-P4-37). Until
# 2026-08-25 these were one number, and every page that discloses what a
# description carries asked "is the floor below the default?". The owner
# ruled the default to 1, which made that question always false and
# silently took the disclosure off every page -- the pages went quiet
# exactly when they had the most to say.
#
# They are two different facts and now have two names. The DEFAULT is
# what `synthtwin profile` writes when nobody asks for another. This is
# the line under which a group is small enough that naming it says
# something about a person, which is a fact about people and did not
# move when the default did. Every page that tells a reader what a
# description contains asks about THIS one.
SMALL_GROUP_NOTICE_LINE = 11

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
ROLE_CLOCK = "time_of_day"
ROLE_AFFIXED = "affixed_number"
ROLE_LONG_TAIL = "long_tail_labels"
# THE FOURTEENTH ROLE (plan P4-D21). Two or more numbers written
# in one cell and joined by one repeated separator. Reached only where
# the person named the column with `--measurement`, never from values.
ROLE_JOINED = "joined_numbers"
# The fifteenth role (residual R-P4-13, landing L8): numbers and
# labels sharing one cell space, each half described in its own
# terms, with two counts of cells that sum to `n_present`.
ROLE_COMPOUND = "numbers_with_labels"
ROLE_TEXT = "free_text"

# The lower bound of the long-tail detection line (plan P4-D5). The
# producer's own constant, written again here for the reason every
# threshold is written twice: the loader may not import the describing
# side, and a line applied on one side only is a line two
# implementations disagree about.
LONG_TAIL_LINE = 11

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
    ROLE_CLOCK,
    ROLE_AFFIXED,
    ROLE_LONG_TAIL,
    ROLE_JOINED,
    ROLE_COMPOUND,
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
    (ROLE_CLOCK, "time_of_day", "ok"),
    (ROLE_AFFIXED, "affixed_number", "ok"),
    # IT NAMES ITS OWN SHAPE (contract 14.1, C6-19). The axis table is
    # a bijection -- thirteen roles onto thirteen types, one row each --
    # and a role sharing another's type breaks the totality discipline
    # the axes exist for.
    (ROLE_LONG_TAIL, ROLE_LONG_TAIL, "ok"),
    # AND SO DOES THIS ONE, for the same reason (plan P4-D21). Fourteen
    # roles onto fourteen types now. Its shape is neither `count` nor
    # `continuous`: both name ONE number per cell, and a consumer that
    # read this column as either would take the whole cell for a value
    # and find that `120/80` is not one.
    (ROLE_JOINED, ROLE_JOINED, "ok"),
    # AND THE FIFTEENTH (residual R-P4-13, landing L8). Fifteen roles
    # onto fifteen types. Its shape is neither `continuous` nor
    # `long_tail_labels` though it holds a population of each: a
    # consumer told this column is a quantity would compute over cells
    # that are not numbers, and one told it is a set of labels would
    # miss that most of its cells are.
    (ROLE_COMPOUND, ROLE_COMPOUND, "ok"),
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
    "time_of_day",
    "affixed_number",
    "long_tail_labels",
    "joined_numbers",
    "numbers_with_labels",
    "text",
)

QUALITY_STATES = ("ok", "empty", "unrepresentable")

STRUCTURAL_ROLES = ("data", "identifier")

ENCODINGS = dialect.ENCODINGS

HEADER_SOURCES = ("file", "generated")

DATE_SENTINEL = "(date-sentinel)"

MISSING_CLASS_KEYS = (
    BLANK,
    DATE_SENTINEL,
    "(declared-missing)",
    "(numeric-sentinel)",
    "(text-code)",
    WITHHELD,
)

SENTINEL_KEYS = (
    "candidate",
    "n_occurrences",
    "reason",
    # THE PUBLISHED ABSENT SPELLINGS THIS DECISION TOOK OUT (repair
    # pass of landing 2b.6, invariant V5). It is the one fact that says
    # which of a column's published hole spellings a JUDGED pass put
    # there and which the person's own declaration did, and no count in
    # the document can supply it: two keys writing the same placeholder
    # day are one judgement and one declaration, and every walk that
    # tried to tell them apart by counting got one of the two wrong.
    "spellings",
    "verdict",
)

VERDICT_MISSING = "read_as_missing"


def _written_empty(column: "ColumnBlock") -> int:
    """How many of a column's absent cells the twin writes EMPTY (plan P4-D173).

    The generator's rule (contract C6-115) read from the other side:
    every absent cell is written empty except a `missing_by_source`
    spelling, which is written at its count. So this is the column's
    absent cells less the spellings reproduced -- and NOT the blank and
    pooled counts added up, which is what FD7 counted until a review
    measured the gap: a free-text column publishes no spelling of the
    twenty cells `--missing-value ZZZ` made absent, counts them in
    `n_missing` alone, and the twin wrote all twenty empty while the
    order was published. The real file validated and the twin missed
    `rows.order`.

    A JUDGED PASS'S SPELLINGS ARE REPRODUCED TOO, since plan P4-D6.4 (the
    owner's ruling of 2026-09-15). Until then the cells a `read_as_missing`
    verdict named were written empty and were added back here; the twin
    now writes them as the source wrote them, so nothing is added back.
    """
    reproduced = 0
    for spelling in sorted(column.missing_by_source):
        reproduced = reproduced + column.missing_by_source[spelling]
    left = column.n_missing - reproduced
    return left if left > 0 else 0

VERDICTS = (VERDICT_MISSING, "kept_as_a_number")

REASON_OUTLIER_AND_FREQUENT = "outlier_and_frequent"

REASONS = (
    REASON_OUTLIER_AND_FREQUENT,
    "not_an_outlier",
    "too_rare",
    "too_few_other_values",
    "kept_by_you",
)

LEVEL_KEYS = (
    "count",
    "label",
    "shape_form_cells",
    "variants",
    "variants_withheld",
)

LABEL_KEYS = (
    "levels",
    "shape_forms",
    "suppressed_levels",
    # THE SCALE OF THE NUMBERS THE FLOOR HELD BACK (plan P4-D301,
    # ledger K-2B-50): one block of three aggregates over the pool.
    "suppressed_numbers",
    "suppressed_rows",
)

CATEGORICAL_KEYS = LABEL_KEYS + ("level_ceiling",)

# The label half of a compound column: the four above, plus the two
# counts the half carries for ITSELF because the column's own counts
# include the numbers (invariant NL2). Written as an extension of
# LABEL_KEYS rather than as a list of its own, so a key added to a
# label block reaches this one.
COMPOUND_LABEL_KEYS = LABEL_KEYS + (
    "n_distinct",
    "n_distinct_folded",
    "n_present",
)

# The clock role's own five, and the two forms its cells can wear.
# Nothing else joins them: these five are the whole of what this role
# adds to the universal keys, and the forbidden-key rule is what stops
# a sixth.
CLOCK_KEYS = (
    "clock_form",
    "clock_percentiles",
    "earliest",
    "latest",
    "n_unparsed",
)
CLOCK_FORMS = ("hh-mm", "hh-mm-ss")

DATETIME_KEYS = (
    "date_percentiles",
    "resolution_mix",
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
    "datetime_separators",
    "all_at_midnight",
    # How many parsed cells stood at midnight, floored on both sides
    # (landing 2b.3, invariant D15).
    "n_at_midnight",
    # HOW THE COLUMN'S DATES WERE WRITTEN, four censuses of FORMS
    # (landing 2b.6, invariants D17 to D20). They are what lets the twin
    # be written in the source's own spelling rather than in ISO, which
    # is the reversal of owner decision 5.
    "date_field_widths",
    "month_name_styles",
    "quarter_marker_case",
    "zulu_case",
)

NUMERIC_KEYS = (
    "group_separator",
    # How a negative number and a signed decimal were written (landing
    # 2b.2): the notation the negatives wore, and how many cells written
    # with a point carried a plus.
    "negative_form",
    # ...and whether the column's WIDE runs of figures are their own
    # values' text (landing 2b.13, plan P4-D90). One word of three, and
    # the fact the canonical ceiling of a point-free cell past 2**53 is
    # read against: past that bound more than one run reads back as one
    # value, so nothing derived from the number can settle which run the
    # column wrote.
    "wide_runs",
    # ...and the MIXTURE those two majority keys collapse (landing
    # 2b.7, plan P4-D65.2): how many negatives wore each notation and
    # how many grouped cells wore each mark, floored per convention.
    # Siblings of the two singular keys rather than replacements: a
    # reader with no use for the mixture reads `negative_form` and
    # `group_separator` exactly as before.
    "negative_notations",
    "thousands_marks",
    "decimal_plus",
    "fraction_widths",
    "pad_widths",
    "field_widths",
    "value_histogram",
    "empty_bins",
    # ...and the REAL edges of each stretch of empty bins (residual
    # R-P4-138). Two values a run, and they are values of real cells.
    "empty_edges",
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
    "kurtosis",
    "n_distinct_values",
    # The ninety rungs the named ladder does not carry (plan P4-D4.10).
    "percentiles_between",
    # The mode PAIR (plan P4-D4.11). Both keys are always present on a
    # column of this role; a withheld mode is `null` beside a count of
    # nought, never an absent key, so a reader never has to tell "this
    # column had no dominant value" from "this description was written
    # by something older".
    "mode",
    "mode_count",
    "percentiles",
    "skew",
    "std",
    "std_unrepresentable",
)

# THE COUNT ROLE'S ONE KEY OF ITS OWN (plan P4-D123): the census of
# spellings a column writing one number more than one way publishes --
# `7`, `07`, `007` -- and `{}` everywhere else. It is the count role's and
# not `continuous`'s, and it is not in NUMERIC_KEYS, because the affixed,
# joined and compound blocks that reuse that list read a column of
# quantities, never one of codes written in figures.
COUNT_KEYS = NUMERIC_KEYS + ("number_spellings",)

# The affixed-number role: everything a numeric column carries, plus
# the pair it publishes, how many cells wore it, and the four counts
# that answer for the CORES rather than for the cells. The two
# populations are never the same one, and the key names say which each
# answers for.
AFFIXED_KEYS = NUMERIC_KEYS + (
    "affix_prefix",
    "affix_suffix",
    # ...and the other wrappers this column wears (plan P4-D36),
    # beside the counts of different cores the cells carry.
    "affix_variants",
    "n_core_distinct",
    "n_core_distinct_folded",
    "n_affixed",
    "n_core_contradictory",
    "n_core_not_numeric",
    "n_core_numeric",
    "n_core_out_of_range",
)

# The joined-number role's own six. `separator` is the one key of this
# role that carries a spelling off the table's cells, on exactly the
# terms `affix_prefix` and `affix_suffix` carry theirs, and the
# forbidden-key rule is what stops a seventh. `parts` holds one block of
# NUMERIC_KEYS per position, in cell order, so the ladder and the mean
# a consumer reads are the same ones every quantitative role publishes.
# The characters a joined cell may be split on. Fixed and short, and
# deliberately without the point and the comma: both are written INSIDE
# numbers this format already reads, and admitting either would make
# every decimal column a candidate pair.
JOINED_SEPARATORS = ("/", "-", ":", "|", ";", "_")


def _is_a_joined_separator(text: str) -> bool:
    """Whether this is a whole separator a joined cell may be split on.

    One mark of the list above, with at most one space before it and at
    most one after (plan P4-D24). A pressure charted `120 / 80` is the
    same reading as `120/80`, and the spacing is part of what the twin
    writes back.
    """
    if not text or len(text) > 3:
        return False
    core = text
    if core[0] == " ":
        core = core[1:]
    if core and core[len(core) - 1] == " ":
        core = core[: len(core) - 1]
    return core in JOINED_SEPARATORS

COMPOUND_KEYS = (
    # THE FIFTEENTH ROLE, at its first step (residual R-P4-13, landing
    # L8). Two counts of CELLS that sum to `n_present`, so every
    # present cell is in exactly one published population -- the answer
    # to review item P1-R6-F7, which deleted a rule that described part
    # of a column and said nothing about the rest.
    #
    "n_numeric_cells",
    # ...AND THE THIRD POPULATION (residual R-P4-149, closed by the
    # owner's ruling of 2026-09-04): the cells the number rules
    # recognise as a numeral this format cannot hold. They are counted
    # with the NUMERIC half rather than with the labels, so a lab
    # column with one `9e999` no longer describes that cell as a word.
    "n_numeric_out_of_range",
    "n_numeric_contradictory",
    "n_label_cells",
    # ...AND THE NUMERIC HALF'S TWO COUNTS OF DIFFERENT WRITTEN CELLS,
    # which the generator spends as its budget of different SPELLINGS.
    # They were not here at first, and the twin could not reach the
    # column's own count of different cells because of it: a count of
    # different NUMBERS buys one spelling per number, so a column
    # holding `07` beside `7` lost every second spelling (review round
    # 1 of this landing, item 1; measured at 113 published against 56
    # written).
    "n_numeric_distinct",
    "n_numeric_distinct_folded",
    # ...AND THE TWO HALVES THEMSELVES. `numbers` holds a quantitative
    # block read over the numeric cells and `labels` a label block read
    # over the rest, each by the reader that reads its own kind of
    # column. The counts above are what a reader checks them against.
    "numbers",
    "labels",
)

JOINED_KEYS = (
    "part_above",
    "part_agreements",
    "n_joined",
    "n_parts",
    "n_unparsed",
    "part_min_widths",
    "parts",
    "separator",
)

UNREPRESENTABLE_KEYS = (
    "n_distinct_by_occurrences",
    "n_fraction",
    "n_negative",
    "n_positive",
    "n_sign_unknown",
    "n_whole",
    "n_whole_unknown",
    # THE TWO WIDTH FACTS (residual R-P4-37). Stated on this role by
    # the contract in four places since version 6 and never written by
    # the producer, so a producer written to the contract emitted a
    # block this loader refused for an unknown key.
    "min_length",
    "max_length",
)

IDENTIFIER_KEYS = (
    "all_whole_numbers",
    # THE SEVENTH KEY, AND THE ONE THAT CARRIES THE SHAPE (landing
    # 2b.18, plan P4-D120). The six beside it say how LONG the shortest
    # and the longest value are and which alphabet the cells came from,
    # and between them they said nothing about what a record number
    # LOOKS like -- so a column of UUIDs published every fact it had and
    # its twin still wrote `A----------------------------------J`.
    "layout_forms",
    # THE EIGHTH KEY, AND THE ONE TEXT OF THE TABLE THIS BLOCK CARRIES
    # (owner ruling of 2026-09-17, item 1; contract 7.12a). A layout
    # says a letter stood at a position and never which one, so `REC`
    # in front of every record number came back as three random
    # capitals and `^REC\d{7}$` matched 800 real cells and 0 twin ones.
    # The owner ruled a constant prefix published where the column
    # clears the smallest group size; invariants LP1 and LP2 hold it.
    "layout_prefixes",
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
    "shape_forms",
    "words",
)

# The long-tail role adds no key to the five every label role carries:
# the form census stands on all four of them (P4-D18, corrected).
LONG_TAIL_KEYS = LABEL_KEYS

LENGTH_KEYS = ("max", "mean", "min", "p50")

WORD_KEYS = ("max", "mean", "min")

# The eleven rungs, in ladder order. The order is the rule: a ladder is
# checked non-decreasing by walking it in exactly this sequence.
# THE NINETY RUNGS THE LADDER DOES NOT NAME (plan P4-D4.10). Built
# from the same rule the producer builds them by, so the names a
# description carries and the names this loader admits cannot drift:
# every percent from 1 to 99 that `LADDER_KEYS` does not already name.
FINER_LADDER_KEYS = tuple(
    f"p{percent:02d}"
    for percent in range(1, 100)
    if percent not in (1, 5, 10, 25, 50, 75, 90, 95, 99)
)

# The percent each of the hundred and one rungs stands at, in ladder
# order, which is what the joint monotone check of Q19 walks.
LADDER_PERCENTS = (0, 1, 5, 10, 25, 50, 75, 90, 95, 99, 100)

# What each of those percents is CALLED in the document, so a refusal
# names the rung the way the description spells it.
_LADDER_NAME_AT = {
    0: "min", 1: "p01", 5: "p05", 10: "p10", 25: "p25", 50: "p50",
    75: "p75", 90: "p90", 95: "p95", 99: "p99", 100: "max",
}

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
    "slashed-iso-date",
    "iso-month",
    "compact-date",
    "month-first-date",
    "day-first-date",
    "textual-day-first-date",
    "textual-month-first-date",
    "dotted-month-first-date",
    "dotted-day-first-date",
    "two-digit-month-first-date",
    "two-digit-day-first-date",
    "dotted-two-digit-month-first-date",
    "dotted-two-digit-day-first-date",
    "month-first-datetime",
    "day-first-datetime",
    "slashed-iso-datetime",
    "year-quarter",
    "iso-mixed",
)

# The two members the joint ISO reading joins. A column that took that
# reading publishes exactly these two counts and no other key.
ISO_MEMBERS = ("iso-date", "iso-datetime")
FORMAT_ISO_MIXED = "iso-mixed"

# The two readings that reach `datetime` resolution through a clock in
# the time-of-day role's own two forms -- `HH:MM` and `HH:MM:SS`, and
# nothing else. THEY CARRY NEITHER A FRACTION NOR AN OFFSET, because
# their own reader takes neither (plan amendment A-P4-1 item 2), so a
# description claiming one of those for such a column describes a
# column no table can hold. That is a rule about the FORMAT and not
# about the resolution, which is why D6 and D9 each need a clause of
# their own for it (review item P4-DATE4-F1).
CLOCK_FORM_MEMBERS = (
    "month-first-datetime",
    "day-first-datetime",
    # The year-first stamp reads its clock the same way (landing 2b.3).
    "slashed-iso-datetime",
)

RESOLUTIONS = ("date", "datetime", "quarter", "month")

TIME_PRECISIONS = (
    "subsecond",
    "second",
    "minute",
    "date",
    "month",
    "quarter",
)

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
    # THE OPENING STOPS BEFORE "written as", because those two words
    # are the CLAUSE's (review item L19-R1-1). The checker pins this
    # fragment at position zero after the count and the clause
    # immediately after it, so the two must not overlap or the
    # structural test could never hold of the producer's own sentence.
    "of this column's values are",
    "and synthtwin described those numbers as quantities: their "
    "average, their spread and their ends are in this profile.",
    AFFIXED_REMARK_MARK,
    # IT NAMES `--code` FIRST (residual R-P4-72, landing L19). The
    # fragment read "--identifier and no value of this column will be
    # published at all", which is the OPPOSITE declaration from the one
    # a person with a code column wants: `--code` keeps every code with
    # the rows that carried it and `--identifier` publishes none of
    # them. Both are still named, in the order that answers the
    # sentence's own question first.
    "run the command again with --code NAME",
    "--identifier NAME leaves them out of the profile altogether",
)

# The one form of the six the fraction census is taken over, named here
# rather than spelled at the place it is read: the census and the forms
# map have to agree about which form they are talking about, and a
# spelling repeated at two sites is a spelling one site can change.
DECIMAL_STYLE = "decimal"
LEADING_ZERO_STYLE = "leading_zero"
# ...and the three of the six that carry no point and no exponent,
# which are exactly the cells the FIELD-width census counts (P4-D30).
PLAIN_STYLE = "plain"
LEADING_PLUS_STYLE = "leading_plus"

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
        "exactly when the encoding it names is a fallback one, Latin-1 or "
        "Windows-1252"
    ),
    # How the table's file is written (plan P4-D86, contract 4.3a).
    "FD1": (
        "the written form describes one column for every column the "
        "table has"
    ),
    "FD2": (
        "the line endings account for every line the file holds -- the "
        "separator hint, the preamble, the header, the rows of column "
        "descriptions, the records and the blank lines -- less the last "
        "where the file does not end its last line, in runs that each "
        "end their lines one way, or, past the cap on runs and in their "
        "place, as how many lines end each of two or more ways in the "
        "listed order of endings; and above a smallest group size of "
        "one every ending's total, every run's own length, and both of "
        "those over the records alone once the lines above the table "
        "are taken off, reach that size and never fall under two"
    ),
    "FD3": (
        "a byte-order mark is recorded only for UTF-8 or UTF-16 text, "
        "and always for UTF-16"
    ),
    "FD4": (
        "blank lines stand in file order after no more records than the "
        "table has, hold nothing but spaces and tabs, and stand inside a "
        "one-column table nowhere but after its last record; neither the "
        "blank places nor the runs of line endings pass their caps; and "
        "blank lines published counted stand in place of places, only "
        "past that cap, in a table of two or more columns, from a first "
        "place no later than the last and the last no later than the "
        "table's end, holding nothing but spaces and tabs"
    ),
    "FD5": (
        "records holding nothing are published only in a table of two or "
        "more columns with no row sequence, and no more of them than any "
        "column has absent cells"
    ),
    "FD6": (
        "a column published as the row sequence has every cell present, "
        "in a table of two or more rows"
    ),
    "FD7": (
        "the column the rows are sorted by is a column of the table and "
        "not the row sequence, holding no empty cell and no absent cell "
        "the twin writes empty outside the records holding nothing -- "
        "exactly as many of them as there are such records -- in a table "
        "of three or more rows"
    ),
    "FD8": (
        "a header cell written differently from its column's name stands "
        "under a header read from the file, in column order, and the "
        "header as written names every column what the description names "
        "it"
    ),
    "FD9": (
        "rows of column descriptions stand only under a header read from "
        "the file, exactly as many of them as the person declared and no "
        "more than two, each as wide as the table, and carry a quoting "
        "rule only where they exist"
    ),
    "FD10": (
        "only a header read from the file carries a trailing delimiter or "
        "a quoting rule of its own, and rows do not both carry a trailing "
        "delimiter and leave out their empty cells"
    ),
    # The rule that keeps a declared identifier out of the written form
    # (plan P4-D76). The producer's half is `profile._published_form`.
    "FD12": (
        "a column the person declared to hold record numbers publishes "
        "no row sequence and is not the column the rows are sorted by, "
        "and a row sequence is published only for the first column, "
        "named as a written row index is"
    ),
    # The rule that holds a declared delimiter to the written form (plan
    # P4-D110, review item CODEX-4). The producer's half is the survey,
    # which reads a declared delimiter and guesses none.
    "FD13": (
        "a delimiter the person declared is the delimiter the written "
        "form publishes, and a workbook carries no such declaration"
    ),
    "FD11": (
        "the lines before the table are published as runs of one shape, "
        "within the cap, each carrying a mark holding no line break, no "
        "quote character, not the table's own delimiter and no text of "
        "the line, each the shape the line the twin writes for it is "
        "read back as, and recorded as withheld exactly when one of "
        "them held text"
    ),
    # How the table's file is a WORKBOOK (plan P4-D77, contract 4.3b).
    "WB1": (
        "a description of a workbook describes one column for every "
        "column the table has"
    ),
    "WB2": (
        "the sheet the table was read from is one of the sheets the "
        "workbook has, counted from one"
    ),
    "WB3": (
        "every published count of cells, and the count of records "
        "holding nothing, is all of them or reaches the line -- the "
        "smallest group, and never under two -- at both ends; a census "
        "that withholds a count withholds at least two, publishes no "
        "nought beside them, and leaves them together at nought, at "
        "the line or more, or at the whole column where nothing is "
        "published, and a column's count of numbers passes its census's "
        "number cells by nought or by the line or more, so that no "
        "count, no complement and no difference a reader can take names "
        "one row"
    ),
    "WB4": (
        "the records holding nothing inside the table are no more than "
        "the table itself holds, and no more rows are frozen than the "
        "sheet has"
    ),
    "WB5": (
        "a workbook names one sheet for every sheet it has, every "
        "name it publishes is one this version would publish itself, "
        "and no two of them are the same name whatever their case"
    ),
    "WB6": (
        "the number format a column's twin wears is one of the codes "
        "this version publishes -- one of Excel's own codes, a canonical "
        "code of its kind, or a code built of the number format "
        "language's own tokens alone -- and its kind is one the column's "
        "own census does not say no cell wears"
    ),
    "WB7": (
        "a workbook describes the block of cells held by every sheet "
        "that is not the table's, and none for the sheet the table was "
        "read from; a block is nought by nought or reaches at most one "
        "row, because a block of two rows is records of a table this "
        "description does not carry, however many columns it spans"
    ),
    "WB8": (
        "the class a workbook column names as its commonest is one its "
        "own census does not say no cell holds"
    ),
    # THE FIRST WB5 AND WB6 WERE WRITTEN AND TAKEN OUT AGAIN, and the reason
    # is worth keeping. One said that a column's cell classes are the
    # closed set and its format kinds the named kinds; the other that a
    # workbook publishes no name of its own. Both are TRUE and neither
    # is an invariant: the first is already the block loader's own key
    # and range check, which refuses an unknown class by name before any
    # rule runs, and the second is a property of what the producer never
    # writes -- there is no field it could put a sheet name in. A rule
    # in this table has to be one a description can BREAK, because every
    # one of them owes a mutation that must be refused (the loader's own
    # completeness guard). A rule that cannot fail is a defect here, so
    # these two are stated where they are enforced and not counted as
    # invariants.
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
        "every column named in a declaration is a column of this table"
    ),
    "S8a": (
        "no column is named as writing its numbers with a comma and "
        "also as holding codes or record numbers"
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
    "V5": (
        "a decision names only spellings this column publishes among "
        "its absent cells, each once and in order, no spelling is "
        "named by two decisions of one column, the cells those "
        "spellings cover never outnumber the rows the decision says "
        "held its candidate and what is left over is nought or names "
        "at least the smallest group, the cells the column's decisions "
        "took out and name no spelling for fit among the absent cells whose "
        "spellings it holds back, and a decision that kept its candidate "
        "as a number names none"
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
        "the labels held back cover at least one row each and fewer "
        "rows than the smallest group size"
    ),
    "B4b": (
        "the labels held back never come to one label on one row, "
        "because that pool is a count of one a reader works out by "
        "subtraction"
    ),
    "B4c": (
        "no total saying what the column's cells read as, less the "
        "published labels that read that way, leaves exactly one row, "
        "because that row is a held-back label of one -- and a total no "
        "published label reads into is read the same way"
    ),
    "B4d": (
        "the scale published for the held-back numbers is taken over a "
        "group: the cells it speaks of are nought, or they and the "
        "column's other numbers each reach the census line -- and its "
        "mean and its spread stand exactly where those cells do"
    ),
    "B5": (
        "a label is published only at the smallest group size or more"
    ),
    "B6": (
        "the labels come in order of how many rows they cover, largest "
        "first, and by name where two cover the same number"
    ),
    "B7": "no two published labels are the same label",
    "C1": "a column of one value has one value, ignoring case",
    "Y1": "a column of two values has two, ignoring case",
    "LT1": (
        "a long tail of labels has at least one value shared by as "
        "many rows as its own detection line asks"
    ),
    "LT2": (
        "a long tail of labels holds more different values than a set "
        "of categories may"
    ),
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
        "size of rows carried it, and never by fewer than two, and offsets "
        "are held back only all together"
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
    "D12": (
        "a mark between a moment's day and its clock is named only when at "
        "least the smallest group size of values wrote it, and never by "
        "fewer than two, and marks are held back only all together and "
        "only where holding them back does not say every mark was written"
    ),
    "D13": (
        "the marks between day and clock are counted over exactly the "
        "values that write a clock"
    ),
    "GS1": (
        "a column groups its thousands with a point only where it writes "
        "its decimals with a comma, and never with a comma there; a space, "
        "an apostrophe, a right single quotation mark, a no-break space, a "
        "narrow no-break space or a thin space may group either; and a "
        "position of a joined column, read from figures and one point "
        "alone, groups with no mark"
    ),
    "NS1": (
        "a column says its negatives are written some other way than with "
        "a minus in front only where at least the smallest group size of "
        "its values are negative"
    ),
    "WR1": (
        "a column says something about its wide runs of figures only "
        "where the forms map leaves room for at least the smallest "
        "group size of them -- the cells written plain or with a "
        "leading plus, and the remainder it withheld -- and says one of "
        "the three words this format fixes and nothing else"
    ),
    "DP1": (
        "the count of numbers written with a point and a plus names at "
        "least two of them and never one, is no more than the cells the "
        "forms map can put in the form written with a point, leaves of "
        "the numbers written with a point either nothing or at least two, "
        "is unavailable rather than held back wherever it cannot say that "
        "much, and says nothing at all on a position of a joined column, "
        "whose parts carry no sign"
    ),
    "NS2": (
        "every notation the negatives were written in is counted for at "
        "least two of them and never one, what is left over is either "
        "nothing or a remainder covering at least two, no more numbers "
        "are counted than the column says are negative, and what the "
        "count leaves of those negatives is either nothing or at least two"
    ),
    "TM1": (
        "every mark the grouped numbers were written with is counted for "
        "at least two of them and never one, what is left over is either "
        "nothing or a remainder covering at least two, what the count "
        "leaves of the column's numbers is either nothing or at least two, "
        "a count that cannot be published is empty rather than "
        "unavailable, and the one mark the column publishes between its "
        "thousands is a mark this count names"
    ),
    "D14": (
        "a column said to stand at midnight is a column of moments large "
        "enough to be a group, whose published moments all stand at "
        "midnight of their own day, and on the shared clock one that holds "
        "back no offset"
    ),
    "D15": (
        "the count of values at midnight is not published at all, or it "
        "is every value, or it is a group of at least the smallest group "
        "size -- and never fewer than two -- leaving at least that many "
        "off midnight; and it is every value exactly where the column is "
        "said to stand at midnight"
    ),
    "D16": (
        "a column mixing whole dates with moments counts at least as many "
        "values with no offset as it holds whole dates"
    ),
    "D17": (
        "the joint width a cell wrote its month and day fields at is "
        "counted only for a member whose fields can show one, is named "
        "only when at least the smallest group size of cells wrote it "
        "and never fewer than two, names no pool, and comes to no more "
        "than the values that read as dates while leaving none of them "
        "over or at least that many"
    ),
    "D18": (
        "the case, length, mark and comma a cell wrote a month NAME with "
        "are counted only for the two textual members, only in the "
        "combinations that member can write -- a name of May with its "
        "length as either -- and only where at least the smallest group "
        "size of cells, and never fewer than two, wrote each, with no pool "
        "and none or at least that many of the values over"
    ),
    "D19": (
        "the case of a quarter's marker is counted only for a column of "
        "quarters, and named only when at least the smallest group size "
        "of cells, and never fewer than two, wrote it, with no pool and "
        "none or at least that many of the values over"
    ),
    "D20": (
        "the case of a zulu offset marker is counted only where the "
        "offset map names 'Z', comes to no more than the values carrying "
        "it while leaving none of them over or at least the smallest group "
        "size, names no pool, and is named only when at least the smallest "
        "group size of cells, and never fewer than two, wrote it"
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
    "Q17": (
        "a column of numbers holds no more different numbers than it "
        "holds cells that read as a number, and holds at least one "
        "wherever its statistics used a value"
    ),
    "Q19": (
        "the ninety finer rungs of a column of numbers are named "
        "exactly, each holds a number or nothing, and the hundred and "
        "one rungs of the named ladder and this one together never go down"
    ),
    "Q18": (
        "the commonest number of a column and the count of cells that "
        "held it are published together or not at all, and where they "
        "are published at least two cells held it and no more cells "
        "than the column has numbers"
    ),
    "Q16": (
        "the weight of a column's tails is given when four or more "
        "values are not all the same one, is left out when they are, "
        "and lies where every sample of that many values must"
    ),
    "Q15": (
        "the shape of a column's numbers accounts for every value the "
        "statistics used and for no more, names each of its stretches "
        "by number, holds back none of them where the smallest group "
        "size is one, and holds back all of them otherwise"
    ),
    # The bins holding nothing (plan P4-D32). Three conditions, and
    # each one is a way a hand-written description could say something
    # about the shape of a column that no column has.
    "Q20": (
        "the bins a column of numbers names as holding nothing are "
        "named once each and in order, are never the bin its smallest "
        "value is in nor the bin its largest is in, and where the "
        "shape of its numbers is published name exactly the bins that "
        "shape does not"
    ),
    # The edges of those stretches (residual R-P4-138), which are what
    # a twin keeps out of: the bins are strictly inside the stretch the
    # source really leaves empty, and these two values are the stretch.
    "Q21": (
        "a column of numbers names one pair of edges for each stretch "
        "of bins it says holds nothing: the value just below the "
        "stretch and the value just above it, each pair ascending, "
        "the pairs themselves ascending and never crossing (two "
        "stretches may share the one value that stands between them), "
        "and every "
        "one of them inside the two ends the column publishes"
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
    "W5b": (
        "no spelling of a label is held back as one that ONE row wrote, "
        "because that is a count of one stated outright"
    ),
    "W7": (
        "a published label was written some way, so it has a named "
        "spelling or a held-back one"
    ),
    "W8": (
        "the rows that wrote a label in its own written form are at "
        "least the named spellings that wear one and at most those "
        "plus every row the floor held back, and a label with no "
        "written form was written in none"
    ),
    "W9": (
        "the different spellings a column of labels is said to hold are "
        "the spellings its published labels name, and at least one and "
        "at most one per row for each label held back"
    ),
    "P1": (
        "the cells counted by the form they were written in come to the "
        "cells that read as numbers"
    ),
    "P2": (
        "a way of writing a number is named only when at least the "
        "smallest group size of cells used it, and never by fewer than two"
    ),
    "P3": (
        "a column of numbers says how its numbers were written"
    ),
    "RM1": (
        "a column of dates says how many of its values wore each form, "
        "and names the form it was read under"
    ),
    "RM2": (
        "the values counted by the form they were written in come to "
        "the values that were read as dates at all"
    ),
    "RM3": (
        "where a column's values are counted under more than one form, "
        "each form is named only when at least the smallest group size "
        "of them wore it, and never by fewer than two"
    ),
    "T1": (
        "every time of day this description publishes is written the "
        "way this column's own times were written"
    ),
    "T2": (
        "the ladder of clock times begins at the column's earliest "
        "time and ends at its latest"
    ),
    "T3": (
        "the ladder of clock times never goes backwards"
    ),
    "T4": (
        "a column read as clock times holds at least one"
    ),
    "T5": (
        "enough of a column's values are clock times for it to be read "
        "that way"
    ),
    "P6": (
        "the cells of a column's numbers are held back from the forms map "
        "only all together, and only where holding them back does not say "
        "every form was written"
    ),
    "P5": (
        "the cells counted by the figures they wrote after the point "
        "come to the cells that were written with a point, and a width "
        "is named, or cells held back, only where at least the smallest "
        "group size and never fewer than two wrote them, and cells are "
        "held back only all together"
    ),
    "P5b": (
        "the cells counted by the width of the field they wrote come "
        "to at least the cells written in the leading-zero form and at "
        "most those together with the cells written with a plus and the "
        "cells held back from the forms map, and what they count past "
        "the leading-zero form, and what that leaves of the cells written "
        "with a plus, is either nothing or at least two"
    ),
    "P6b": (
        "every field width the census names, and the cells it holds back, "
        "number at least the smallest group size and never fewer than two, "
        "and cells are held back only all together"
    ),
    "P7b": (
        "a field width narrower than two figures is a width no padded "
        "cell can wear"
    ),
    "P8": (
        "a form the forms map holds back has no widths published beside "
        "it"
    ),
    # The census of WHOLE-WRITTEN field widths (plan P4-D30). Its sum
    # is bounded on two sides rather than pinned on one, because it
    # counts three of the six forms rather than one.
    "P6c": (
        "every whole-number field width the census names, and the cells "
        "it holds back, number at least the smallest group size and never "
        "fewer than two, cells are held back only all together, and at a "
        "width the padded census names too, the cells written without a "
        "redundant zero are either nothing or at least two"
    ),
    "P7c": (
        "a field width of no figures at all is a width no cell written "
        "as a whole number can wear"
    ),
    "P9c": (
        "the cells counted by the width of the field they wrote come "
        "to the cells written in a form that carries no point, give or "
        "take the cells the forms map held back"
    ),
    # The census of written forms. Registered here because a rule this
    # module RAISES and this table does not hold reaches a person as a
    # bare KeyError rather than as the refusal it is -- which is what a
    # hand-edited document with a below-floor named form did (review
    # round 1 finding 9).
    "SF1": (
        "every written form the census names was written by at least "
        "the smallest group size and by at least two cells, and a "
        "lower-case key, with the form's "
        "own key beside it, by at least two cells as well, and the "
        "census holds no pool of one cell"
    ),
    "SF3": (
        "the census counts no more cells than the column has present, "
        "a cell too long to have a form being counted nowhere, and, where "
        "it counts any, never exactly one fewer, nor exactly one fewer "
        "than n_not_numeric among its forms no number is written in, nor, "
        "on a column of free text, exactly one fewer than n_code_alphabet, "
        "or than n_code_alphabet less n_all_digits, among its forms of "
        "that alphabet"
    ),
    "SC1": (
        "every spelling a count column's census names was written by at "
        "least the smallest group size and by at least two cells"
    ),
    "SC2": (
        "a count column's census of spellings, where it names any, names "
        "every cell read as a number, holds one number written two ways, "
        "and names no more spellings than a set of categories may hold"
    ),
    "SC3": (
        "the spellings of nought a count column's census names count "
        "exactly the cells published as nought"
    ),
    "SF5": (
        "a lower-case key of the form census is named only on a column "
        "whose different values are as many once case and edge spacing "
        "are set aside"
    ),
    "LF1": (
        "every layout the census names was written by at least the "
        "smallest group size and by at least two cells"
    ),
    "LF2": (
        "the pool of a layout census, where it is written, holds at least "
        "two cells"
    ),
    "LF3": (
        "the census counts no more cells than the column has present, "
        "a cell this census does not describe being counted nowhere"
    ),
    "LF4": (
        "a census counting any cell does not count exactly one cell fewer "
        "than the column has present"
    ),
    "LF5": (
        "the named layouts inside the code alphabet, or in a plain column "
        "inside the figures, do not count exactly one cell fewer than the "
        "column publishes in that alphabet"
    ),
    "LF6": (
        "every key of a layout census is written under one convention"
    ),
    "LF7": (
        "every layout the census names could have been worn by at least "
        "as many different cells as the column has different values, and "
        "the smallest group size besides"
    ),
    "LP1": (
        "a prefix is published for the whole column alone, or for layouts "
        "the census names, and only beside a census naming a layout"
    ),
    "LP2": (
        "a prefix's own layout, read under the census's own convention, "
        "is the opening every layout it is published for starts with, and "
        "a figure or a letter stands after it in each of them"
    ),
    "LP3": (
        "every layout a prefix is published for could still have come "
        "from at least the column's different values plus the smallest "
        "group size, once the prefix's own characters are fixed"
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
    # How the table's FILE is written (contract 4.3a, plan P4-D86).
    dialect: "dialect.Dialect"
    # What the table's file said about itself as a WORKBOOK (contract
    # 4.3b, plan P4-D77), or None where the file was delimited text.
    workbook: "WorkbookForm | None" = None


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
    built_in_dates: "tuple[str, ...]"



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
    day_first: bool
    long_tail_minimum_level: int
    forced_identifiers: "tuple[str, ...]"
    # THE SECOND DECLARATION (plan P4-D19). Columns the person named as
    # holding codes rather than measurements. Unlike the record-number
    # declaration above this one does not silence a column: it moves it
    # off the rules that read a cell as a number, a date, a clock time
    # or a number wearing an affix, and onto the label roles, where the
    # exact spellings and their counts are what get published.
    forced_codes: "tuple[str, ...]"
    # THE THIRD DECLARATION (plan P4-D21). Columns the person named as
    # holding quantities, including ones written as two or more whole
    # numbers in one cell. Like `forced_codes` and unlike
    # `forced_identifiers` it does not silence a column.
    forced_measurements: "tuple[str, ...]"
    # THE FOURTH DECLARATION (plan P4-D26). Columns the person named as
    # writing their numbers with a comma where this tool's default
    # reading expects a point. It is unlike the three above it in what
    # it answers: they say WHAT a column holds and are three answers to
    # one question, so no column may carry two of them. This one says
    # HOW the numbers of a column are spelled, which is a different
    # question, and a column declared a measurement may perfectly well
    # also be declared to spell its numbers with a comma -- that pairing
    # is the commonest true thing a person has to say about a European
    # file, and refusing it would refuse the case this declaration was
    # built for.
    forced_decimal_commas: "tuple[str, ...]"
    # THE FIFTH DECLARATION (plan P4-D81). How many rows under the
    # column names DESCRIBE those columns -- a survey export writes two
    # -- rather than holding somebody's record. It is a count and not a
    # list of names, and it is the only thing that lets rows be taken
    # out of the table and published as schema: without it they are
    # data, which is what a file synthtwin has guessed wrong about
    # needs them to be (review item CODEX-2).
    forced_metadata_rows: int = 0
    # THE SIXTH DECLARATION (plan P4-D110, review item CODEX-4). The
    # character the person said separates the columns of their file, or
    # empty where they said nothing. A file that reads equally well
    # under two delimiters cannot be settled by anything in its cells,
    # so this is the one thing that settles it; FD13 holds it to the
    # delimiter the written form publishes.
    forced_delimiter: str = ""


# TWO QUESTIONS, TWO NAMES, because a first version asked one and
# answered the other (review item P4-G3-R5-F2).
#
# THIS is the roles on which the declaration is HONOURED -- where the
# published description differs because it was made. The profiler
# swaps every declared column's cells BEFORE it chooses a role, so a
# column of `1,5` cells reads as ones and a halves whatever role it
# ends up with, `constant` and `binary` included; those two are chosen
# before the numeric roles and were missing from the first version of
# this list, so the command line told a person their numbers were "NOT
# read" with the comma about a description whose profiler had read
# exactly that way.
#
# It is used by the one caller holding a description rather than a
# loaded profile: the command line, which must say when a declaration
# landed somewhere it cannot help. Its COMPLEMENT is what gets the
# warning.
DECIMAL_COMMA_HONOURED_ROLES = (
    # THE AFFIXED ROLE, whose cores the declaration now reaches (landing
    # 2b.16, plan P4-D106; the audit's item NC-11). A price written
    # `795,64 EUR` and a percentage written `37,5 %` are the commonest
    # European exports there are, and the splitter that finds the number
    # inside the wrapper asked the ORDINARY reader whether a substring
    # was a number -- so `795,64` was not one, every cell proposed a
    # pair of its own, and the column fell to free text and came back as
    # punctuation stand-ins. Which mark inside a larger spelling is the
    # decimal point is the question residual R-P4-52 carries, and on a
    # DECLARED column it is the declaration that answers it; the joined
    # role stays outside, where the same mark may be the separator
    # between two readings and no declaration settles which.
    "affixed_number",
    "binary",
    "constant",
    "continuous",
    "count",
    # The compound role, whose numeric half the declaration reaches
    # (plan P4-D34). It was missing while `a_decimal_comma_reaches`
    # already answered yes for the role, so the two statements of the
    # same fact disagreed and the CLI told a person their declaration
    # had not reached a column it had reached (review round 5 of
    # landing L8, item 4).
    "numbers_with_labels",
    "numeric_unrepresentable",
)


def a_decimal_comma_reaches(column: "ColumnBlock") -> bool:
    """Whether the GENERATOR must spell this column's numbers with a
    comma, and whether the validator must read them back that way.

    THE NARROWER OF THE TWO QUESTIONS, and not the same one
    `DECIMAL_COMMA_HONOURED_ROLES` answers. A declaration is HONOURED
    on more roles than this: the profiler reads every declared column
    with the comma, so a `constant` column of `1,5` publishes ones and
    a halves. But that column's twin writes the published SPELLING,
    `1,5`, straight out -- there is nothing for a swap to do, and
    swapping would corrupt it. This predicate is about the cells the
    numeric machinery WRITES as numbers, which are the only ones the
    twin spells itself.

    It reaches the plain numeric roles and the unrepresentable one,
    whose cells are numbers too large or too small for this format to
    hold but are numbers all the same, spelled by the same rules.

    It does NOT reach the label and text roles: those publish spellings
    the file itself held, and swapping a character inside one of them
    would rewrite a value the description publishes exactly.

    IT REACHES THE AFFIXED ROLE SINCE LANDING 2b.16 (plan P4-D106,
    closing the affixed half of residual R-P4-52), and it reaches it
    OVER THE CORE alone. Such a cell carries a number inside a larger
    spelling, and R-P4-52 asked which mark of that spelling is the
    decimal point; on a column the person DECLARED, the declaration is
    the answer -- that is the one question it exists to answer -- and
    the wrapper is not translated at all, because a wrapper is
    published text and a mark inside `U.S.$` is no decimal point. What
    stays outside is the JOINED role, where the same mark may be the
    separator between two readings and nothing published chooses; that
    half of R-P4-52 is open and is named in the plan rather than
    quietly widened.

    IT LIVES HERE BECAUSE FOUR PLACES ASK IT (review item P4-G3-R2-F2).
    The profiler's censuses, the generator's writeback, the validator's
    cell reading and the refusal that turns away a declaration it
    cannot honour must all agree about which columns are reached, and
    the validator may not import the generator. A first version wrote
    the test twice, said `NumericFacts` in both, and silently dropped
    the unrepresentable role from a feature whose whole subject is how
    a number is spelled.

    Guarantees: accepts one column's block; returns whether the swap
    applies. Determinism: a fixed function of the block. Raises
    nothing. No I/O of any kind.
    """
    # AND THE COMPOUND ROLE, whose numeric HALF is written by the same
    # machinery and must be spelled the same way (review round 4 of
    # landing L8, item 1). Excluding it left a declared column of
    # `1,5` cells profiled under the comma grammar and written back
    # with points: sixteen checks missed on a twin that was otherwise
    # correct. Its LABEL half is not touched -- both the writeback and
    # the validator's reading translate a cell of this role only where
    # the translation makes it a number, so a label spelled `E11.9`
    # keeps its dot.
    return isinstance(
        column.facts,
        (NumericFacts, UnrepresentableFacts, CompoundFacts, AffixedFacts),
    )


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
    """What was decided about one stand-in number, and why.

    `spellings` are the keys of this column's `missing_by_source` whose
    cells THIS decision took out (repair pass of landing 2b.6). It is
    empty on a decision that kept the candidate as a number, empty on a
    column that publishes no value of the table, and empty where every
    spelling the pass took fell below the floor. It carries the
    provenance of a published hole spelling -- judged here, or declared
    by the person -- which nothing else in the document carries.
    """

    candidate: str
    verdict: str
    reason: str
    n_occurrences: int
    spellings: "tuple[str, ...]"


@dataclasses.dataclass(frozen=True)
class MissingByClass:
    """Absent cells by the reason each was counted absent (contract 5.4).

    The six keys of the document are six fields here, because the
    document's own key spellings -- `(blank)` and the rest -- are not
    names a program can carry, and a consumer that reads a seventh
    reason should find out where it made the mistake.

    THE SIXTH ARRIVED WITH THE CALENDAR PLACEHOLDERS (plan amendment
    A-P4-1 item 3): a cell taken out because it wrote a placeholder day
    is absent for its own reason, and pooling it with the numeric
    stand-ins would tell a reader a column of dates held a stand-in
    NUMBER.
    """

    blank: int
    date_sentinel: int
    declared_missing: int
    numeric_sentinel: int
    text_code: int
    withheld: int


@dataclasses.dataclass(frozen=True)
class LevelEntry:
    """One published label, its rows, and how those rows wrote it.

    `shape_form_cells` is how many of those rows wrote it in the
    label's own written form (7.4.8, plan amendment A-P4-47). It is one
    number and not a census because every form-bearing spelling of a
    level wears exactly `parsing.shape_form(label)`; a label with no
    form of its own carries 0. It is the fact the twin needs to give
    the level's made-up spellings the shape the source's held-back ones
    wore, which the column-wide `shape_forms` cannot say.
    """

    label: str
    count: int
    variants: "dict[str, int]"
    variants_withheld: "dict[str, int]"
    shape_form_cells: int


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

    THE TWO WIDTH FACTS ARE HERE NOW (residual R-P4-37), and the
    docstring said the opposite until 2026-08-26: "there is no width
    fact and no magnitude fact here, and the omission is load-bearing".
    That was never true of the CONTRACT, which has stated
    `min_length` and `max_length` on this role in four places since
    version 6; it was true only of the producer, which never wrote
    them, and of this loader, which refused them. The consequence was
    that a twin of a twenty-figure identifier column came out at one
    made-up canonical width, so code checking `len(x)` behaved
    differently on the twin than on the real table.

    WHAT THE PAIR COSTS, kept from the old docstring because it is the
    honest half of it: for decimal numerals a length bounds a
    magnitude, so `max_length` states the order of magnitude of the
    largest withheld numeral. That is one cell's worth of floor-free
    fact, and section 12 prices it. What it buys is a twin whose
    invented digit strings are the width the real ones were.
    """

    min_length: int
    max_length: int
    n_whole: int
    n_fraction: int
    n_whole_unknown: int
    n_positive: int
    n_negative: int
    n_sign_unknown: int
    n_distinct_by_occurrences: "dict[str, int]"


@dataclasses.dataclass(frozen=True)
class PooledNumbers:
    """The scale of the numbers the floor held back (6.3, invariant B4d).

    THREE AGGREGATES OVER ONE GROUP and no fourth: how many cells of the
    held-back levels read as numbers, their mean, and their POPULATION
    spread -- divided by the count of them, not by one less, because
    what it describes is the whole of a pool and not a sample of
    something larger.

    `n_cells` nought is the one state this block has to say nothing
    with. It is reached both by a column whose held-back levels hold no
    number at all and by a column where naming the pool would let a
    reader subtract their way to a row, and the two are deliberately
    indistinguishable: a refusal that looked different from nought would
    itself publish that the pool holds numbers and how few.

    `mean` and `spread` are both absent exactly there, which is what the
    loader holds them to.
    """

    n_cells: int
    mean: "float | None"
    spread: "float | None"


# WHAT A LABEL BLOCK CARRIES WHERE NO POOLED SCALE IS PUBLISHED. One
# value, so that no caller builds a second spelling of the same state.
NO_POOLED_NUMBERS = PooledNumbers(n_cells=0, mean=None, spread=None)


@dataclasses.dataclass(frozen=True)
class LabelFacts:
    """The published labels of a label column (6.3), and their forms.

    `shape_forms` is carried by ALL FOUR label roles (P4-D18,
    corrected). It first stood on `long_tail_labels` alone, on the
    reasoning that the other three publish their levels so their twins
    hold them and have no stand-in to shape. That reasoning was wrong.
    A diagnosis column of five common codes and twenty-six rare ones
    is under the categorical ceiling, so it takes `categorical` -- and
    the floor holds back every rare one, whose twin cells came out
    `group-1` through `group-24`, which is the defect the census was
    raised to close, in the shape a real table most often has it.
    Whether a label role suppresses levels is a fact about the FLOOR,
    not about the role.

    THE HELD-BACK LABELS ARE A POOL (owner ruling of 2026-09-17, item 2,
    option A; plan P4-D201): `suppressed_levels` and `suppressed_rows`,
    and no size of any one of them.
    """

    levels: "tuple[LevelEntry, ...]"
    suppressed_levels: int
    suppressed_rows: int
    shape_forms: "dict[str, int]"
    suppressed_numbers: "PooledNumbers"


@dataclasses.dataclass(frozen=True)
class LongTailFacts(LabelFacts):
    """A long tail of labels. It adds no key of its own."""


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
    resolution_mix: "dict[str, int]"
    datetime_separators: "dict[str, int]"
    all_at_midnight: bool
    # How many parsed cells stood at midnight, or `None` where the count
    # is not published at all (landing 2b.3, invariant D15; the
    # unavailable state is landing 2b.6's). Either side of the count
    # below the floor -- and the floor here is never below two, because a
    # count of one names one person -- leaves this absent rather than
    # nought, so that a reader cannot tell a column holding no midnight
    # from one holding a single one.
    n_at_midnight: "int | None" = None
    # HOW THE CELLS WERE WRITTEN (landing 2b.6, the reversal of owner
    # decision 5). Each is a census of FORMS held to the smallest group
    # size, and each is empty on a column whose member cannot show that
    # convention: the widths on a member of fixed field width, the name
    # styles outside the two textual members, the quarter marker outside
    # `year-quarter`, and the zulu case where no `Z` is named.
    date_field_widths: "dict[str, int]" = dataclasses.field(
        default_factory=dict
    )
    month_name_styles: "dict[str, int]" = dataclasses.field(
        default_factory=dict
    )
    quarter_marker_case: "dict[str, int]" = dataclasses.field(
        default_factory=dict
    )
    zulu_case: "dict[str, int]" = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True)
class NumericFacts:
    """A column of counts or of continuous values (contract 6.7).

    `n_rows` is the per-column echo of the table's row count, and it is
    a different quantity from the description's own `n_rows`: the
    document-level one carries the row-count obligation and this one
    carries none.
    """

    percentiles: NumberLadder
    # The ninety rungs `percentiles` does not name, in percent
    # order (plan P4-D4.10, contract Q19). One fact, no subcheck
    # of its own, consumed by the generator's interpolation.
    percentiles_between: "tuple[float | None, ...]"
    mean: "float | None"
    std: "float | None"
    skew: "float | None"
    # HOW HEAVY THIS COLUMN'S TAILS ARE (plan P4-D4.8). The moment
    # ratio and not the excess, so a normal curve reads 3 here rather
    # than 0 -- the same measure the skewness beside it uses. Undefined,
    # and written as null, below four values or where every value is
    # the same one.
    kurtosis: "float | None"
    # HOW MANY DIFFERENT NUMBERS, as distinct from how many different
    # SPELLINGS (plan P4-D4.9, closing residual R-P4-20). `n_distinct`
    # on the column block counts spellings, so `1` and `01` are two of
    # them and one number; this counts the numbers.
    n_distinct_values: int
    # The number the column held most often and how many cells held it,
    # or None beside 0 where the pair was withheld (plan P4-D4.11).
    mode: "float | None"
    mode_count: int
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
    # THE MARK BETWEEN THOUSANDS, or the empty string where the
    # column proves none. Published beside the styles map rather
    # than inside it: that map is a partition whose counts close
    # on the numeric total, and a grouped cell is also a decimal
    # one, so a seventh form would break the closure. Amendment
    # A-P4-5 set this precedent for the fraction widths.
    group_separator: str
    # HOW THE NEGATIVES WERE WRITTEN, one name of `parsing.NEGATIVE_FORMS`
    # (landing 2b.2): `minus` unless brackets, the minus sign of the
    # character tables or a trailing minus was the column's majority.
    negative_form: str
    # WHETHER THE COLUMN'S WIDE RUNS ARE THEIR OWN VALUES' TEXT (landing
    # 2b.13, plan P4-D90): one word of `parsing.WIDE_RUNS`. Carries no
    # count, so it carries no floor.
    wide_runs: str
    # HOW MANY NEGATIVES WORE EACH NOTATION, AND HOW MANY GROUPED CELLS
    # EACH MARK (landing 2b.7, plan P4-D65.2). The two keys above
    # publish the column's MAJORITY convention and the generator writes
    # every cell that way, so a column mixing two came back written
    # wholly as one with every check passing. These censuses carry the
    # mixture, floored per convention by `taxonomy._census_floor`, and
    # the generator spends them cell by cell. Each is `{}` where the
    # population is empty, a map of named conventions with possibly a
    # `(withheld)` remainder, or `{"(unavailable)": 0}`.
    negative_notations: "dict[str, int]"
    thousands_marks: "dict[str, int]"
    # HOW MANY CELLS WRITTEN WITH A POINT CARRIED A PLUS (landing 2b.2).
    # The form ladder files `+12.5` under `decimal`, so this is the count
    # `leading_plus` is for a whole number: `{"+": n}` at or above the
    # floor, `{"(withheld)": n}` below it, `{}` where none did.
    decimal_plus: "dict[str, int]"
    fraction_widths: "dict[str, int]"
    pad_widths: "dict[str, int]"
    # HOW WIDE EVERY WHOLE-WRITTEN CELL WROTE ITS FIGURE FIELD (plan
    # P4-D30, closing R-P4-30 and R-P4-35). The other two censuses
    # cover the padded cells and the figures after a point; a cell
    # written `199` is in neither, so nothing published said how wide
    # it was.
    field_widths: "dict[str, int]"
    # HOW MANY OF THIS COLUMN'S NUMBERS FALL IN EACH OF THE THIRTY-TWO
    # EQUAL BINS between its published ends (plan P4-D4.7). A ladder and
    # the moments cannot show two peaks; this can, and it is the one
    # fact in this block a person plotting a distribution or fitting a
    # mixture is actually reading.
    value_histogram: "dict[str, int]"
    # ...AND WHICH OF THOSE BINS HOLD NOTHING (plan P4-D32, the owner's
    # ruling of 2026-08-31). The census above is all or nothing and is
    # therefore absent from every description written above a floor of
    # one; this list survives the floor, because a bin holding nobody
    # is not a small group. It is the one fact of this block the
    # smallest group size does not reach, and the value stage reads it
    # as a set of stretches no cell may land in.
    empty_bins: "tuple[int, ...]"
    # One `(below, above)` pair per run of empty bins: the largest
    # value under the stretch and the smallest over it, both real
    # (residual R-P4-138).
    empty_edges: "tuple[tuple[float, float], ...]"
    # EVERY SPELLING OF A COUNT COLUMN THAT WROTE ONE NUMBER MORE THAN
    # ONE WAY, with its cells (7.13, plan P4-D123); `{}` on every other
    # column and on every block that is not a `count` block.
    number_spellings: "dict[str, int]" = dataclasses.field(
        default_factory=dict
    )


@dataclasses.dataclass(frozen=True)
class IdentifierFacts:
    """A column the person declared to hold record numbers (6.8)."""

    min_length: int
    max_length: int
    all_whole_numbers: bool
    n_all_digits: int
    n_code_alphabet: int
    n_distinct_by_occurrences: "dict[str, int]"
    # THE CENSUS OF LAYOUTS (7.12, plan P4-D120). Where at least
    # `small_cell_floor` cells were written to one layout, that layout
    # is named with its count; the rest are pooled under `(withheld)`.
    # The key says what KIND of character stood at each position and
    # never which one, so it carries no value of the table, no spelling
    # of one and no fragment of one -- which is what lets it stand in a
    # block invariant I3 governs.
    layout_forms: "dict[str, int]"
    # THE LITERAL PREFIX (7.12a; owner ruling of 2026-09-17, item 1).
    # `(column)` mapped to the text every present cell opens with, or
    # each named layout mapped to the text its own cells open with. The
    # one fragment of the table this block may carry, by that ruling,
    # which amends I3 for this case only. Empty on every other column.
    layout_prefixes: "dict[str, str]"


@dataclasses.dataclass(frozen=True)
class TextFacts:
    """A column no rule claimed, publishing none of its values (6.9)."""

    length: LengthStats
    words: WordStats
    n_all_digits: int
    n_code_alphabet: int
    n_distinct_by_occurrences: "dict[str, int]"
    shape_forms: "dict[str, int]"


@dataclasses.dataclass(frozen=True)
class AffixWrapper:
    """One wrapper a column wears, with its own numbers (plan P4-D37).

    A column wearing a SET of wrappers published ONE ladder over every
    core it held, and that is a statistic of no quantity where the
    wrappers are units: a hundred weights written `60.0 kg` to
    `69.9 kg` beside a hundred written `132.3 lb` to `153.8 lb`
    published mean 104.722, with the column's own ends running from 60
    to 153.8. Every published wrapper carries its own block now.

    THE FOUR CLASS COUNTS CLOSE ON `count`, exactly as the column's
    four close on `n_affixed`. They are here rather than derived
    because the block beside them cannot be checked without them: a
    loader reading a block of a subset has to know how many of that
    subset's cores read as numbers.

    `numbers` echoes `count` rather than the table's row count, on the
    joined role's own precedent -- a block describing a subset of a
    column's cells answers for that subset.
    """

    prefix: str
    suffix: str
    count: int
    n_core_numeric: int
    n_core_out_of_range: int
    n_core_contradictory: int
    n_core_not_numeric: int
    # HOW MANY DIFFERENT CORES THIS WRAPPER HOLDS. The generator lays
    # each wrapper's cores out from its own block, and a layout is
    # divided by a count of different things: handed the COLUMN's
    # count, a wrapper worn by fifty cells is asked for the spellings
    # of every core in the column.
    n_core_distinct: int
    n_core_distinct_folded: int
    numbers: NumericFacts


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

    # THE COMMONEST WRAPPER'S NUMBERS, AND NOT THE COLUMN'S (plan
    # P4-D37). On a column wearing ONE wrapper those are the same
    # thing, which is every column of this role until a set is worn.
    # On a column wearing a SET they are not, and pooling them
    # published a statistic of no quantity: a hundred weights in
    # kilograms beside a hundred in pounds gave mean 104.722.
    numbers: NumericFacts
    affix_prefix: str
    affix_suffix: str
    # THE OTHER WRAPPERS THIS COLUMN WEARS (plan P4-D36), each with the
    # count of cells wearing it AND ITS OWN NUMBERS (plan P4-D37).
    # Empty on a column wearing one wrapper, which is most of them, so
    # a description written before this key existed reads the same way.
    affix_variants: "tuple[AffixWrapper, ...]"
    n_affixed: int
    # HOW MANY DIFFERENT CORES (plan P4-D36). The generator spends
    # these as its budget of different core SPELLINGS; the column's own
    # counts are of different CELLS, and once a column wears more than
    # one wrapper the two are different numbers.
    n_core_distinct: int
    n_core_distinct_folded: int
    n_core_numeric: int
    n_core_out_of_range: int
    n_core_contradictory: int
    n_core_not_numeric: int


@dataclasses.dataclass(frozen=True)
class CompoundFacts:
    """Numbers and labels in one cell space (residual R-P4-13, L8).

    THREE COUNTS OF CELLS THAT SUM TO `n_present`, so every present
    cell is in exactly one published population: the numbers, the
    numerals this format cannot hold, and the labels. That sum is the whole
    answer to review item P1-R6-F7, which deleted a rule describing
    part of a column and saying nothing about the rest: a reader can
    check the arithmetic without trusting any prose.

    AND BOTH HALVES DESCRIBED, each by the reader that reads its own
    kind of column: `numbers` is read by the SAME reader every
    quantitative block is read by, over the numeric cells, and
    `labels` by the same reader a column of labels is read by, over
    the rest. Nothing here reads a fact a second way, so the two
    halves cannot come to disagree with the roles they are borrowed
    from.
    """

    n_numeric_cells: int
    # THE THIRD POPULATION (residual R-P4-149, closed by the owner's
    # ruling of 2026-09-04): cells the number rules recognise as a
    # numeral this format cannot hold. They are counted with the
    # NUMERIC half, because an unusable numeral is a number, and the
    # two counts are the two a plain numeric column publishes.
    n_numeric_out_of_range: int
    n_numeric_contradictory: int
    n_label_cells: int
    n_numeric_distinct: int
    n_numeric_distinct_folded: int
    # ...and the label half's own two, so neither view has to borrow a
    # count from the whole column.
    n_label_distinct: int
    n_label_distinct_folded: int
    numbers: "NumericFacts"
    labels: "LabelFacts"


@dataclasses.dataclass(frozen=True)
class JoinedFacts:
    """Two or more numbers written in one cell (contract 6.15).

    TWO POPULATIONS, as `AffixedFacts` has. `parts` holds one
    quantitative block PER POSITION, each read over that position's
    numbers alone, so the ladder a consumer reads for the first number
    is a ladder of first numbers and nothing else. `n_joined` and
    everything the universal keys count answer for the CELLS.

    `separator` is the one key of this role that carries a spelling of
    the table, on exactly the terms the affixed role's pair does, and
    the forbidden-key rule is what confines it to that key.

    `part_min_widths` is what tells a padded position from a plain one:
    `95` and `133` differ in width because the NUMBERS differ, while a
    padded position writes `007` and `080` at one width whatever the
    number. It is a width and never a spelling.
    """

    parts: "tuple[NumericFacts, ...]"
    separator: str
    n_parts: int
    n_joined: int
    n_unparsed: int
    part_min_widths: "tuple[int, ...]"
    # HOW THE POSITIONS MOVE TOGETHER, one entry per PAIR of positions
    # in the order (1,2), (1,3), ... (2,3), ... `part_agreements` is
    # the rank agreement between the two, from -1 to 1, and
    # `part_above` is the number of rows in which the earlier position
    # held the larger number.
    #
    # THEY ARE FACTS ABOUT THE PAIRING AND NOTHING ELSE. What each
    # position holds is published exactly in `parts`, so neither of
    # these repeats a number the block already carries; between them
    # they say the one thing it did not -- which numbers met in a row.
    part_agreements: "tuple[float, ...]"
    part_above: "tuple[int, ...]"


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
    | JoinedFacts
    # THE FIFTEENTH ROLE, and it was missing from this union while
    # every reader dispatched on it (review round 3 of landing L8,
    # item 1). A strict type run named it: `_facts_of` returns one of
    # these and returned a `CompoundFacts` that the union did not
    # carry, so the checker could not hold any reader to the branch.
    | CompoundFacts
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


# -- the two halves of a compound column, as columns ------------------
#
# THE HALVES ARE READ THE SAME WAY BY BOTH SIDES. The generator builds
# each half with the machinery that builds a whole column of that kind,
# and the validator checks each half with the checks that check a whole
# column of that kind -- so what a half IS has to be one definition,
# read from here by both. Writing it twice is how a producer and a
# reader come to disagree about the same cells.


def _not_its_own_facts(name: str) -> "errors.ProfileError":
    """A column handed a view builder that its own kind does not have.

    An internal check, and it stays one: both halves of a compound
    column are read into `CompoundFacts` when the description is
    loaded, so a column reaching either view without them is a mistake
    in synthtwin rather than anything a description did.
    """
    return errors.ProfileError(
        f"synthtwin internal check: the description of the column "
        f"'{parsing.visible(name)}' does not carry the facts its own kind "
        f"of column needs. Both are checked when the description is "
        f"read, so this means a mistake in synthtwin; please report it."
    )


def compound_numbers_view(
    column: "ColumnBlock",
) -> "ColumnBlock":
    """The numeric half of a compound column, as a column of numbers.

    THE SAME MOVE `_core_view` MAKES, for the same reason. A compound
    column has two populations and the numeric machinery is written
    over one of them; its universal counts answer for the CELLS, and a
    cell reading `NOT DETECTED` is not a number, so those counts say
    the column holds fewer numbers than its numeric half does. The
    quantitative block answers for the numeric cells alone.

    Handed over as a column in its own right, every rule of G5 and G6
    applies unchanged -- which is the point: the numbers inside a
    compound column are built by exactly the code that builds a plain
    numeric column.
    """
    facts = column.facts
    # The TUPLE form of the type gate, which is how this module writes
    # one (`a_decimal_comma_reaches` above). The offline audit refuses
    # a bare class name handed to a callee it does not scan, and
    # `isinstance` is not scanned code: it cannot tell a class from any
    # other callable a caller might keep and run later.
    if not isinstance(facts, (CompoundFacts,)):
        raise _not_its_own_facts(column.name)
    return dataclasses.replace(
        column,
        statistical_type="continuous",
        # THE HALF'S POPULATION IS ITS NUMBERS AND ITS UNUSABLE
        # NUMERALS (residual R-P4-149). A plain numeric column's
        # `n_present` is the sum of its four class counts, and this
        # view is handed to the same machinery, so it is that sum here
        # too -- with `n_not_numeric` nought, because a cell that is
        # not a numeral at all is in the OTHER half.
        n_present=(
            facts.n_numeric_cells
            + facts.n_numeric_out_of_range
            + facts.n_numeric_contradictory
        ),
        # A HALF HAS NO ABSENT CELLS OF ITS OWN. A blank cell is in
        # neither population -- the two counts of the split are taken
        # over the PRESENT cells and sum to `n_present` -- so carrying
        # the column's own missing count into a half would say the half
        # has room for cells it cannot hold. It is read: the style
        # ceiling asks how many cells of this population a file could
        # write in one form, and with the column's blanks left in, that
        # capacity came out above the half's own size and an obligation
        # no file can exceed was filed as a check that cannot fail.
        n_missing=0,
        n_numeric=facts.n_numeric_cells,
        n_not_numeric=0,
        n_out_of_range=facts.n_numeric_out_of_range,
        n_contradictory=facts.n_numeric_contradictory,
        # THE HALF'S OWN COUNTS OF DIFFERENT WRITTEN CELLS, and NOT
        # its count of different numbers. The layout spends these two
        # as a budget of SPELLINGS, and `07` and `7` are one number
        # written two ways: a budget of numbers cannot buy the second
        # way, so a column publishing 113 different cells produced a
        # twin holding 56 (review round 1, item 1).
        n_distinct=facts.n_numeric_distinct,
        n_distinct_folded=facts.n_numeric_distinct_folded,
        facts=facts.numbers,
    )


def compound_labels_view(
    column: "ColumnBlock",
) -> "ColumnBlock":
    """The label half of a compound column, as a column of labels."""
    facts = column.facts
    # The TUPLE form of the type gate, which is how this module writes
    # one (`a_decimal_comma_reaches` above). The offline audit refuses
    # a bare class name handed to a callee it does not scan, and
    # `isinstance` is not scanned code: it cannot tell a class from any
    # other callable a caller might keep and run later.
    if not isinstance(facts, (CompoundFacts,)):
        raise _not_its_own_facts(column.name)
    return dataclasses.replace(
        column,
        statistical_type="long_tail_labels",
        role="long_tail_labels",
        n_present=facts.n_label_cells,
        n_missing=0,
        # THE HALF'S OWN COUNTS OF DIFFERENT CELLS, and this view
        # carried the WHOLE COLUMN's until review round 3 named it:
        # `n_present` said five and `n_distinct` said two hundred and
        # ninety-six, which is not a column any file could hold.
        n_distinct=facts.n_label_distinct,
        n_distinct_folded=facts.n_label_distinct_folded,
        n_numeric=0,
        n_not_numeric=facts.n_label_cells,
        n_out_of_range=0,
        n_contradictory=0,
        facts=facts.labels,
    )



@dataclasses.dataclass(frozen=True)
class Profile:
    """A whole conforming description at `PROFILE_VERSION` (10.8).

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
    # The columns the person named with `--code`. LT1 is stated over
    # this: the long-tail detection line is a stand-in for a judgement
    # nobody had made, and a declared code column is one where they
    # have made it (plan P4-D22).
    declared_codes: "tuple[str, ...]"
    # The columns the person named with `--decimal-comma`. Invariant
    # NL5 is stated over this: whether a published label of a compound
    # column is a NUMBER depends on the grammar that column is read
    # with, and `1,5` is a number on a declared column and text on
    # every other.
    declared_commas: "tuple[str, ...]"
    # The share a role's detection line is drawn at, carried here
    # because one invariant is stated over it: AF3 holds an affixed
    # column's pair to the line its own detection had to clear, and a
    # loader without the setting could not check it at all.
    parse_rate: float
    # The three settings the categorical ceiling is computed from,
    # carried here because LT2 is stated over it: a long-tail block has
    # to hold more different values than a set of categories may, and a
    # loader without these could not ask the producer's own question.
    category_share: float
    category_ceiling: int
    category_floor: int


def _category_ceiling(frame: _Frame) -> int:
    """The most different values a set of categories may hold here.

    THE PRODUCER'S OWN RULE, written again for the reason every
    threshold is written twice: the loader may not import the
    describing side. `min(categorical_ceiling, categorical_share of the
    table's ROWS)`, never below `categorical_floor` -- rows, not the
    values the column happens to hold, which is what the producer
    computes and what every profile records the settings for.
    """
    # THE EXACT PRODUCT, like every other threshold in this file
    # (amendments A-P4-21 and A-P4-23). A ceiling computed by
    # multiplying in binary64 is a ceiling the two sides can disagree
    # about at the boundary, which is the whole reason the rule is
    # written twice.
    numerator, denominator = _exact_ratio(frame.category_share)
    share = (numerator * frame.n_rows) // denominator
    ceiling = frame.category_ceiling
    if share < ceiling:
        ceiling = share
    if ceiling < frame.category_floor:
        ceiling = frame.category_floor
    return ceiling


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
    anything, and the two files it opens are the description and the
    questions file `profile` is handed with `--answers` (amendment
    A-P4-58). NEITHER IS A TABLE, which is the guarantee that matters
    and the one this sentence used to make by counting to one. The
    questions file is not on the generation path at all: nothing in
    `generate` can reach `load_answers`.

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
    """Check `profile_version` is exactly `PROFILE_VERSION`, first (10.6).

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


def _whole_or_nothing(value: object, key: str, where: str) -> "int | None":
    """A whole number of nought or more, or nothing at all.

    `null` is this format's spelling of "not published" for a count
    whose group and whose complement are both held to a floor, and
    `n_at_midnight` is the field of that kind (landing 2b.6). NOUGHT IS
    NOT THAT SPELLING and this helper exists to keep the two apart: a
    field that says "nothing here" with a nought has told every reader
    who can tell that nought from a real one exactly what it withheld.

    Guarantees: accepts the value, its key and where it stands; returns
    the whole number, or `None` where the document writes `null`. Raises
    ProfileError for anything else. No I/O of any kind.
    """
    if value is None:
        return None
    return _whole(value, key, where, 0)


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


def _exactly(value: object, key: str, where: str, permitted: int) -> int:
    """The value under ``key``, required to be one whole number.

    A setting with exactly one permitted value, on the
    `declaration_matching` precedent. It is recorded rather than
    assumed so that the number is on the document's own face, and it is
    refused at any other value because moving it is a change to the
    contract rather than a choice a run may make.
    """
    found = _whole(value, key, where, 0)
    if found != permitted:
        raise _out_of_range(key, where, f"{found}", f"{permitted}")
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

# THE SAME MAPPING ONE STEP DEEPER, inside the label half of a compound
# column (residual R-P4-13, landing L8). The half publishes levels
# exactly as a label column does, so a person's own spellings stand
# here too -- and a refusal that quoted one would be a refusal printing
# the data it refused. The path is passed rather than inferred for the
# reason every other table-keyed mapping passes one: a caller that
# forgot would fail OPEN.
_THE_COMPOUND_VARIANT_KEYS = (
    "columns", canonical.EACH, "labels", "levels", canonical.EACH, "variants"
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
        pairs += [(rows, kept[name])]
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


def _finer_ladder(
    value: object, key: str, where: str, ladder: NumberLadder
) -> "tuple[float | None, ...]":
    """The ninety rungs the named ladder does not carry (contract Q19).

    They are ONE FACT and not ninety: no rung here has a subcheck of
    its own, and the fidelity they buy comes from the generator
    interpolating them rather than from a file being held to each
    (plan P4-D4.10).

    What IS checked is the shape a consumer relies on. The keys are
    exactly the ninety percents, every entry is a number or null, and
    -- the half that matters -- the HUNDRED AND ONE rungs of this and
    the named ladder together never go down. Checking the ninety alone
    would let a finer rung sit outside the named pair it lies between,
    and a generator interpolating that ladder would then place a value
    outside two rungs the description publishes as exact.

    Guarantees: accepts the value under ``key`` and the named ladder
    beside it; returns the ninety rungs in percent order. Raises
    ProfileError for a value that is not a block (R15), for keys that
    are not exactly the ninety (L4), for an entry that is neither a
    number nor null (R15), and for Q19. No I/O of any kind.
    """
    mapping = _mapping(value, key, where)
    _keys(mapping, where, FINER_LADDER_KEYS, "every finer ladder")
    finer: "dict[int, float | None]" = {}
    rungs: list[float | None] = []
    for name in FINER_LADDER_KEYS:
        rung = _figure_or_nothing(mapping[name], f"{key} -> {name}", where)
        rungs += [rung]
        finer[int(name[1:])] = rung
    # THE JOINT WALK, over all hundred and one rungs in percent order.
    named: "dict[int, float | None]" = {}
    for index in range(len(LADDER_PERCENTS)):
        named[LADDER_PERCENTS[index]] = ladder.rungs[index]
    previous: "float | None" = None
    previous_percent = 0
    for percent in range(101):
        if percent in named:
            rung = named[percent]
            shown = f"percentiles -> {_LADDER_NAME_AT[percent]}"
        else:
            rung = finer[percent]
            shown = f"{key} -> p{percent:02d}"
        if rung is None:
            continue
        if previous is not None and rung < previous:
            raise _broken(
                "Q19",
                where,
                f"the rung at {previous_percent} per cent is {previous}",
                f"{shown} is {rung}",
            )
        previous = rung
        previous_percent = percent
    return tuple(rungs)


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
        rungs += [rung]
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
        rungs += [found]
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
    if resolution == "month":
        wanted = "a month written like 2024-03"
        good = (
            len(found) == 7
            and _digits_at(found, 0, 4)
            and found[4] == "-"
            and _digits_at(found, 5, 2)
            and "01" <= found[5:7] <= "12"
            and found[0:4] != "0000"
        )
    elif resolution == "quarter":
        wanted = "a quarter written like 2024-Q1"
        good = (
            len(found) == 7
            and _digits_at(found, 0, 4)
            and found[4] == "-"
            and found[5] == "Q"
            and "1" <= found[6] <= "4"
            and found[0:4] != "0000"
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
    """The six keys saying how the table was read (contract 4.3, 4.3a).

    Guarantees: accepts the value under `source`; returns it as a typed
    object. Raises ProfileError for an unknown or missing key, a wrong
    type, a value outside its list, and for either of the two
    invariants: S5, which ties the fallback flag to the encoding it
    names -- Latin-1 or Windows-1252 -- and S6, which refuses a first row taken as names by
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
    if fallback != (encoding in dialect.FALLBACK_ENCODINGS):
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
        dialect=_dialect_block(mapping["dialect"]),
        workbook=_workbook_block(mapping["workbook"]),
    )


_WORKBOOK = "in the block saying how the table's workbook holds it"


@dataclasses.dataclass(frozen=True)
class WorkbookColumn:
    """One column's census, as the description publishes it."""

    cell_classes: "dict[str, int | None]"
    # The number format the twin WEARS (plan P4-D79). One of
    # `dialect.SHEET_FORMAT_CODES` and never a code out of the person's
    # file: a custom code is published as the canonical code of its kind.
    format_code: str
    format_kinds: "dict[str, int | None]"
    formulas: "int | None"
    # The class most of the column's value-holding cells are, named
    # without a count, or None where no class is held by the line (plan
    # P4-D164). One of `dialect.SHEET_VALUE_CLASSES`.
    value_class: "str | None" = None


@dataclasses.dataclass(frozen=True)
class WorkbookForm:
    """How a workbook holds the table (contract 4.3b)."""

    autofilter: bool
    columns: "tuple[WorkbookColumn, ...]"
    date_system: str
    defined_names: int
    defined_table: bool
    # Nothing where the smallest group held it back: this counts records
    # of the table, so a count of one names one record (WB3).
    empty_rows_inside: "int | None"
    frozen_rows: int
    macro_project: bool
    rows_above_header: int
    sheet_count: int
    sheet_hidden: bool
    # One entry per sheet in workbook order: the name where it may be
    # published, or None where it was withheld (plan P4-D79).
    sheet_names: "tuple[str | None, ...]"
    # One entry per sheet in workbook order: the block of cells a sheet
    # that is not the table's holds, as (rows, columns), and None for the
    # sheet the table was read from (plan P4-D82).
    sheet_extents: "tuple[tuple[int, int] | None, ...]"
    sheet_position: int
    trailing_blank_columns: int
    trailing_blank_rows: int


def _held_count(value: object, key: str, where: str) -> "int | None":
    """A count the floor may have held back: a whole number, or nothing."""
    if value is None:
        return None
    return _whole(value, key, where, 0)


def _format_kind_of(code: str) -> str:
    """Which kind a published format code is (`dialect.sheet_format_kind`).

    THE LOADER MUST NOT REACH THE READER to answer this. `workbook`
    opens and parses; putting it in the loader's import graph is what
    broke the profile/generator boundary in part 1 of this landing. The
    rule lives in `dialect`, which opens nothing, since a code may be
    published as the source wrote it (plan P4-D189).
    """
    return dialect.sheet_format_kind(code)


def _format_code(value: object, where: str) -> str:
    """A column's published number format code (contract 4.3b, WB6).

    One `dialect.sheet_format_code_publishable` admits -- Excel's own
    vocabulary, a canonical code, or a code of the format language's own
    tokens alone (plan P4-D189) -- and refused otherwise: a hand-made
    description may not put a code carrying somebody's words into a twin.
    """
    found = _text(value, "format_code", where)
    if not dialect.sheet_format_code_publishable(found):
        raise _broken(
            "WB6", where,
            f"a column's twin wears the format code '{found}'",
            "one of Excel's own codes, a canonical code, or a code of the "
            "number format language's own tokens alone",
        )
    return found


def _sheet_names(value: object, where: str) -> "tuple[str | None, ...]":
    """Each sheet's published name, or None where it was withheld.

    A name that is not one `dialect.sheet_name_published` would publish
    is refused rather than carried: the whole point of the rule is that
    a description never holds a sheet name synthtwin could not have
    written itself, and a loader that accepted one would let a hand-made
    description put somebody's name back into a twin.
    """
    out: "list[str | None]" = []
    for item in _listing(value, "sheet_names", where):
        if item is None:
            out += [None]
            continue
        name = _text(item, "sheet_names", where)
        if dialect.sheet_name_published(name) != name:
            raise _out_of_range(
                "sheet_names", where, f"'{name}'",
                "a name this version would publish itself",
            )
        out += [name]
    return tuple(out)


_SHEET_EXTENT_KEYS = ("columns", "rows")


def _sheet_extents(
    value: object, where: str
) -> "tuple[tuple[int, int] | None, ...]":
    """The block of cells each sheet that is not the table's holds.

    `null` for the sheet the table was read from, whose own facts
    describe it, and a block of two whole numbers for every other sheet
    (plan P4-D82). What the block may be is WB7's rule, checked with the
    other workbook invariants once the sheet count is known.
    """
    out: "list[tuple[int, int] | None]" = []
    for item in _listing(value, "sheet_extents", where):
        if item is None:
            out += [None]
            continue
        entry = _mapping(item, "sheet_extents", where)
        _keys(entry, where, _SHEET_EXTENT_KEYS, "a sheet's block of cells")
        out += [
            (
                _whole(entry["rows"], "rows", where, 0),
                _whole(entry["columns"], "columns", where, 0),
            )
        ]
    return tuple(out)


def _value_class(value: object, where: str) -> "str | None":
    """A column's commonest value class, by name, or nothing (P4-D164)."""
    if value is None:
        return None
    return _one_of(value, "value_class", where, dialect.SHEET_VALUE_CLASSES)


def _workbook_block(value: object) -> "WorkbookForm | None":
    """The workbook block, typed, or None where the file was not one.

    Guarantees: accepts the value under `source.workbook`; returns it as
    a typed object or None. Raises ProfileError for an unknown or
    missing key, a wrong type, and a value outside its list. The rules
    that tie it to the columns and the row count are `_workbook_rules`.
    """
    if value is None:
        return None
    where = _WORKBOOK
    mapping = _mapping(value, "workbook", where)
    _keys(mapping, where, dialect.SHEET_KEYS, "that block")
    columns: "list[WorkbookColumn]" = []
    for item in _listing(mapping["columns"], "columns", where):
        entry = _mapping(item, "columns", where)
        _keys(entry, where, dialect.SHEET_COLUMN_KEYS, "a column's census")
        classes = _mapping(entry["cell_classes"], "cell_classes", where)
        _keys(classes, where, dialect.SHEET_CELL_CLASSES, "a column's cell classes")
        counted: "dict[str, int | None]" = {}
        for kind in dialect.SHEET_CELL_CLASSES:
            counted[kind] = _held_count(classes[kind], kind, where)
        formats = _mapping(entry["format_kinds"], "format_kinds", where)
        _keys(formats, where, dialect.SHEET_FORMAT_KINDS, "a column's format kinds")
        wearing: "dict[str, int | None]" = {}
        for kind in dialect.SHEET_FORMAT_KINDS:
            wearing[kind] = _held_count(formats[kind], kind, where)
        columns += [
            WorkbookColumn(
                cell_classes=counted,
                format_code=_format_code(entry["format_code"], where),
                format_kinds=wearing,
                formulas=_held_count(entry["formulas"], "formulas", where),
                value_class=_value_class(entry["value_class"], where),
            )
        ]
    return WorkbookForm(
        autofilter=_truth(mapping["autofilter"], "autofilter", where),
        columns=tuple(columns),
        date_system=_one_of(
            mapping["date_system"], "date_system", where,
            dialect.SHEET_DATE_SYSTEMS,
        ),
        defined_names=_whole(mapping["defined_names"], "defined_names", where, 0),
        defined_table=_truth(mapping["defined_table"], "defined_table", where),
        empty_rows_inside=_held_count(
            mapping["empty_rows_inside"], "empty_rows_inside", where
        ),
        frozen_rows=_whole(mapping["frozen_rows"], "frozen_rows", where, 0),
        macro_project=_truth(mapping["macro_project"], "macro_project", where),
        rows_above_header=_whole(
            mapping["rows_above_header"], "rows_above_header", where, 0
        ),
        sheet_count=_whole(mapping["sheet_count"], "sheet_count", where, 1),
        sheet_hidden=_truth(mapping["sheet_hidden"], "sheet_hidden", where),
        sheet_names=_sheet_names(mapping["sheet_names"], where),
        sheet_extents=_sheet_extents(mapping["sheet_extents"], where),
        sheet_position=_whole(
            mapping["sheet_position"], "sheet_position", where, 1
        ),
        trailing_blank_columns=_whole(
            mapping["trailing_blank_columns"], "trailing_blank_columns", where, 0
        ),
        trailing_blank_rows=_whole(
            mapping["trailing_blank_rows"], "trailing_blank_rows", where, 0
        ),
    )


def _present_sheet_cells(column: WorkbookColumn) -> "int | None":
    """How many cells a workbook column's census says the sheet carries.

    The producer's side of this is `workbook._present_cells`; the two
    ask one question so the loader refuses exactly what the producer
    will not write (round 2 of the review, the disclosure pass, item 6).
    Every class but `absent` holds a cell that is there, and a census
    withholding any count publishes no such total at all -- None, which
    leaves a reader nothing to subtract.

    Guarantees: accepts one workbook column block; returns the present
    cells or None. Determinism: a fixed function of the block, whose
    classes are read in the closed order. Raises nothing. No I/O.
    """
    present = 0
    for key in dialect.SHEET_CELL_CLASSES:
        if key not in column.cell_classes:
            return None
        counted = column.cell_classes[key]
        if counted is None:
            return None
        if key == dialect.SHEET_CELL_ABSENT:
            continue
        present = present + counted
    return present


def _workbook_rules(
    source: SourceBlock,
    columns: "tuple[ColumnBlock, ...]",
    n_rows: int,
    floor: int,
) -> None:
    """The invariants that tie a workbook block to the table (WB1-WB8)."""
    form = source.workbook
    if form is None:
        return
    where = _WORKBOOK
    width = len(columns)
    if len(form.columns) != width:
        raise _broken(
            "WB1", where,
            f"the workbook describes {len(form.columns)} columns",
            f"the table has {width}",
        )
    if form.sheet_position > form.sheet_count:
        raise _broken(
            "WB2", where,
            f"the table was read from sheet {form.sheet_position}",
            f"the workbook has {form.sheet_count}",
        )
    # ONE RULE FOR EVERY COUNT OF CELLS, AND IT IS THE PRODUCER'S OWN
    # (plan P4-D164). Each census was held to the floor count by count,
    # and a review measured the gap: `60, 39, null` over a hundred cells,
    # beside noughts, handed a reader the withheld count of one by
    # subtraction, and the loader passed it at a floor of five. The rules
    # are `dialect.sheet_census`'s, checked here by the function written
    # beside them.
    for place in range(len(form.columns)):
        column = form.columns[place]
        for census in (column.cell_classes, column.format_kinds):
            trouble = dialect.sheet_census_broken(census, n_rows, floor)
            if trouble:
                raise _broken(
                    "WB3", where, trouble,
                    "no count, complement or difference of fewer than "
                    "the line",
                )
        # AND NO DIFFERENCE WITH THE COLUMN'S COUNT OF NUMBERS (plan
        # P4-D197): the count of numbers less the census's number cells is
        # how many figures were stored as text.
        counted = column.cell_classes[dialect.SHEET_CELL_NUMBER]
        if counted is not None and counted >= 1:
            stored = columns[place].n_numeric - counted
            if stored > 0 and not parsing.census_nameable([stored], [], floor):
                raise _broken(
                    "WB3", where,
                    f"a column counts {columns[place].n_numeric} numbers "
                    f"beside {counted} cells stored as numbers",
                    "no difference of fewer than the line between them",
                )
        # AND NO DIFFERENCE WITH THE PRESENT CELLS EITHER (round 2 of
        # the review, the disclosure pass, item 6). A formula cell is a
        # cell the sheet carries, so the formula count lies inside the
        # census's own present classes as well as inside the rows -- and
        # on a column of holes those are far fewer. Measured at a floor
        # of eleven on 400 rows: twenty formulas, one literal number and
        # 379 absent cells published `{"number": 21, "absent": 379}`
        # beside `formulas` 20, and 21 less 20 named the literal cell.
        trouble = dialect.sheet_count_broken(
            column.formulas, n_rows, floor, _present_sheet_cells(column)
        )
        if trouble or (
            column.formulas is not None and column.formulas > n_rows
        ):
            raise _broken(
                "WB3", where,
                trouble
                or f"a column publishes {column.formulas} cells holding a "
                "formula",
                f"the table has {n_rows} rows, and no count of fewer than "
                "the line is published",
            )
        # WB8: the commonest class a column names is one it holds.
        if column.value_class is not None:
            holding = column.cell_classes[column.value_class]
            if holding is not None and holding == 0:
                raise _broken(
                    "WB8", where,
                    f"a column names {column.value_class} as its "
                    "commonest class",
                    "a class its own census does not say no cell holds",
                )
    if len(form.sheet_names) != form.sheet_count:
        raise _broken(
            "WB5", where,
            f"the workbook names {len(form.sheet_names)} sheets",
            f"it has {form.sheet_count}",
        )
    claimed: "dict[str, bool]" = {}
    for name in form.sheet_names:
        if name is None:
            continue
        if dialect.sheet_name_published(name) != name:
            raise _broken(
                "WB5", where,
                f"a sheet is named '{name}'",
                "a name this version would publish itself",
            )
        # A SPREADSHEET HOLDS NO TWO SHEETS OF ONE NAME IN ANY CASE (plan
        # P4-D171), so a description naming two could only be written
        # back under a name the application chose.
        if dialect.sheet_name_key(name) in claimed:
            raise _broken(
                "WB5", where,
                f"two sheets are named '{name}' whatever their case",
                "no two sheets of one name",
            )
        claimed[dialect.sheet_name_key(name)] = True
    # WHAT EVERY OTHER SHEET HOLDS (WB7, plan P4-D82). The twin writes
    # each such sheet with a block of this shape, so a description that
    # named a block for the table's own sheet, left one out, or asked
    # for a block two rows by two columns -- a table this description
    # does not carry -- would put a workbook on disk that no reading of
    # the person's file could have produced.
    if len(form.sheet_extents) != form.sheet_count:
        raise _broken(
            "WB7", where,
            f"the workbook describes the cells of "
            f"{len(form.sheet_extents)} sheets",
            f"it has {form.sheet_count}",
        )
    for index in range(len(form.sheet_extents)):
        extent = form.sheet_extents[index]
        if index + 1 == form.sheet_position:
            if extent is not None:
                raise _broken(
                    "WB7", where,
                    "the sheet the table was read from describes a block "
                    "of cells of its own",
                    "the table's own facts, which describe that sheet",
                )
            continue
        if extent is None:
            raise _broken(
                "WB7", where,
                f"sheet {index + 1} describes no block of cells",
                "one for every sheet that is not the table's",
            )
        if extent[0] >= 2:
            raise _broken(
                "WB7", where,
                f"sheet {index + 1} holds {extent[0]} rows and "
                f"{extent[1]} columns of cells",
                "a block of at most one row",
            )
        if (extent[0] == 0) != (extent[1] == 0):
            raise _broken(
                "WB7", where,
                f"sheet {index + 1} holds {extent[0]} rows and "
                f"{extent[1]} columns of cells",
                "both nought, or both more than nought",
            )
    if n_rows:
        for column in form.columns:
            kind = _format_kind_of(column.format_code)
            wearing = column.format_kinds[kind]
            if wearing is not None and wearing == 0:
                raise _broken(
                    "WB6", where,
                    f"a column's twin wears a {kind} format",
                    "a kind its own census says no cell wears",
                )
    if form.empty_rows_inside is not None:
        if form.empty_rows_inside > n_rows:
            raise _broken(
                "WB4", where,
                f"{form.empty_rows_inside} records hold nothing inside "
                "the table",
                f"the table has {n_rows} rows",
            )
        # THE RECORDS HOLDING NOTHING ARE A COUNT OF ROWS, so the rule
        # that holds every census holds this too (repair of landing
        # 2b.10, plan P4-D164). One such record inside a table names that
        # row as surely as a census of one cell does.
        trouble = dialect.sheet_count_broken(
            form.empty_rows_inside, n_rows, floor
        )
        if trouble:
            raise _broken(
                "WB3", where,
                f"{form.empty_rows_inside} of {n_rows} records hold nothing",
                f"the line is {dialect.sheet_line(floor)}",
            )
    # A FREEZE IS BOUNDED BY THE SHEET AND NOT BY THE TABLE (plan
    # P4-D288, the repair of review item 9 of the files review of
    # 2026-09-18). Freezing rows splits the WINDOW, and a person may
    # split it below everything they have written: `ySplit="200"` over a
    # header and 120 records is a layout Excel writes and every reader
    # accepts. This rule held the split to the rows the table fills,
    # so profiling such a sheet published `frozen_rows 200` and the
    # loader then refused the very description the profiler had just
    # written -- with advice to describe the table again, which repeats
    # the refusal for ever. What a description may not claim is a split
    # AT or past the last row a worksheet has: the split's own top-left
    # cell is the row BELOW it, so a freeze of every row spells
    # `A1048577` and no spreadsheet has that cell (the repair of the
    # skeptic's finding 5 on P4-D288 -- measured: `ySplit="1048576"`
    # loaded, and the twin's pane came out `topLeftCell="A1048577"`).
    # `workbook.sheet_cells` holds such a pane one row inside the sheet,
    # so no description synthtwin writes reaches this rule.
    if form.frozen_rows >= dialect.SHEET_MAXIMUM_ROWS:
        raise _broken(
            "WB4", where,
            f"{form.frozen_rows} rows are frozen at the top",
            f"fewer rows than a worksheet has "
            f"({dialect.SHEET_MAXIMUM_ROWS}), so that the split has a row "
            f"below it",
        )


_WRITTEN = "in the block saying how the table's file is written"


def _dialect_block(value: object) -> dialect.Dialect:
    """The written form of the table's file, typed (contract 4.3a).

    Guarantees: accepts the value under `source.dialect`; returns it as a
    typed object. Raises ProfileError for an unknown or missing key, a
    wrong type, and a value outside its list. The rules that tie the form
    to the columns and the row count are `_dialect_rules`, run once the
    columns are read.
    """
    where = _WRITTEN
    mapping = _mapping(value, "dialect", "in the block saying how the table was read")
    _keys(mapping, where, dialect.DOCUMENT_KEYS, "that block")
    runs: list[dialect.EndingRun] = []
    for item in _listing(mapping["line_endings"], "line_endings", where):
        entry = _mapping(item, "line_endings", where)
        _keys(entry, where, ("ending", "lines"), "a run of line endings")
        runs += [
            dialect.EndingRun(
                ending=_one_of(entry["ending"], "ending", where, dialect.ENDINGS),
                lines=_whole(entry["lines"], "lines", where, 1),
            )
        ]
    census: list[dialect.EndingRun] = []
    for item in _listing(mapping["line_endings_spread"], "line_endings_spread", where):
        entry = _mapping(item, "line_endings_spread", where)
        _keys(entry, where, ("ending", "lines"), "a count of line endings")
        census += [
            dialect.EndingRun(
                ending=_one_of(entry["ending"], "ending", where, dialect.ENDINGS),
                lines=_whole(entry["lines"], "lines", where, 1),
            )
        ]
    spread: "dialect.BlankSpread | None" = None
    if mapping["blank_lines_spread"] is not None:
        counted = _mapping(mapping["blank_lines_spread"], "blank_lines_spread", where)
        _keys(counted, where, ("first", "last", "lines", "text"), "the blank lines counted")
        spread = dialect.BlankSpread(
            first=_whole(counted["first"], "first", where, 0),
            last=_whole(counted["last"], "last", where, 0),
            lines=_whole(counted["lines"], "lines", where, 1),
            text=_text(counted["text"], "text", where),
        )
    blanks: list[dialect.BlankPlace] = []
    for item in _listing(mapping["blank_lines"], "blank_lines", where):
        entry = _mapping(item, "blank_lines", where)
        _keys(entry, where, ("after", "lines", "text"), "a place of blank lines")
        blanks += [
            dialect.BlankPlace(
                after=_whole(entry["after"], "after", where, 0),
                lines=_whole(entry["lines"], "lines", where, 1),
                text=_text(entry["text"], "text", where),
            )
        ]
    preamble: list[dialect.PreambleRun] = []
    for item in _listing(mapping["preamble"], "preamble", where):
        run = _mapping(item, "preamble", where)
        _keys(
            run, where, ("kind", "lines", "mark"),
            "a run of lines before the table",
        )
        preamble += [
            dialect.PreambleRun(
                kind=_one_of(run["kind"], "kind", where, dialect.PREAMBLE_KINDS),
                lines=_whole(run["lines"], "lines", where, 1),
                mark=_text(run["mark"], "mark", where),
            )
        ]
    header_rows: list[tuple[str, ...]] = []
    for item in _listing(mapping["header_rows"], "header_rows", where):
        header_rows += [
            tuple(
                [
                    _text(cell, "header_rows", where)
                    for cell in _listing(item, "header_rows", where)
                ]
            )
        ]
    written: list[dialect.WrittenName] = []
    for item in _listing(mapping["written_names"], "written_names", where):
        entry = _mapping(item, "written_names", where)
        _keys(entry, where, ("position", "text"), "a header cell as written")
        written += [
            dialect.WrittenName(
                position=_whole(entry["position"], "position", where, 1),
                text=_text(entry["text"], "text", where),
            )
        ]
    trailing = _mapping(mapping["trailing_delimiter"], "trailing_delimiter", where)
    _keys(trailing, where, ("header", "rows"), "the trailing delimiter block")
    empty = _mapping(mapping["empty_rows"], "empty_rows", where)
    _keys(empty, where, ("interior", "leading", "trailing"), "the empty records block")
    columns: list[dialect.ColumnForm] = []
    for item in _listing(mapping["columns"], "columns", where):
        entry = _mapping(item, "columns", where)
        _keys(entry, where, ("pad", "quoting", "sequence_start"), "a column's written form")
        quoting = _mapping(entry["quoting"], "quoting", where)
        _keys(quoting, where, dialect.CELL_CLASSES, "a column's quoting")
        rules = tuple(
            [
                _one_of(quoting[kind], kind, where, dialect.QUOTE_RULES)
                for kind in dialect.CELL_CLASSES
            ]
        )
        side = ""
        width = 0
        if entry["pad"] is not None:
            pad = _mapping(entry["pad"], "pad", where)
            _keys(pad, where, ("side", "width"), "a column's padding")
            side = _one_of(pad["side"], "side", where, dialect.PAD_SIDES)
            width = _whole(pad["width"], "width", where, 2)
        start = -1
        if entry["sequence_start"] is not None:
            start = _whole(entry["sequence_start"], "sequence_start", where, 0)
            if start not in dialect.SEQUENCE_STARTS:
                raise _out_of_range(
                    "sequence_start", where, f"{start}", "0 or 1"
                )
        columns += [
            dialect.ColumnForm(
                quoting=rules, pad_side=side, pad_width=width, sequence_start=start
            )
        ]
    order = dialect.NO_ORDER
    if mapping["row_order"] is not None:
        sorted_by = _mapping(mapping["row_order"], "row_order", where)
        _keys(sorted_by, where, ("collation", "column", "direction"), "the row order")
        order = dialect.RowOrder(
            column=_whole(sorted_by["column"], "column", where, 1),
            direction=_one_of(sorted_by["direction"], "direction", where, dialect.DIRECTIONS),
            collation=_one_of(sorted_by["collation"], "collation", where, dialect.COLLATIONS),
        )
    return dialect.Dialect(
        delimiter=_one_of(mapping["delimiter"], "delimiter", where, dialect.DELIMITERS),
        initial_space=_truth(mapping["initial_space"], "initial_space", where),
        escape=_one_of(mapping["escape"], "escape", where, dialect.ESCAPES),
        separator_line=_truth(mapping["separator_line"], "separator_line", where),
        byte_order_mark=_truth(mapping["byte_order_mark"], "byte_order_mark", where),
        line_endings=tuple(runs),
        final_line_ending=_truth(mapping["final_line_ending"], "final_line_ending", where),
        end_of_file_mark=_truth(mapping["end_of_file_mark"], "end_of_file_mark", where),
        preamble=tuple(preamble),
        preamble_withheld=_truth(mapping["preamble_withheld"], "preamble_withheld", where),
        header_quoting=_one_of(mapping["header_quoting"], "header_quoting", where, dialect.QUOTE_RULES),
        header_rows=tuple(header_rows),
        header_rows_quoting=_one_of(
            mapping["header_rows_quoting"], "header_rows_quoting", where, dialect.QUOTE_RULES
        ),
        written_names=tuple(written),
        header_trailing_delimiter=_truth(trailing["header"], "header", where),
        rows_trailing_delimiter=_truth(trailing["rows"], "rows", where),
        short_rows=_truth(mapping["short_rows"], "short_rows", where),
        blank_lines=tuple(blanks),
        empty_rows_leading=_whole(empty["leading"], "leading", where, 0),
        empty_rows_interior=_whole(empty["interior"], "interior", where, 0),
        empty_rows_trailing=_whole(empty["trailing"], "trailing", where, 0),
        columns=tuple(columns),
        row_order=order,
        line_endings_spread=tuple(census),
        blank_lines_spread=spread,
    )


def _dialect_rules(
    source: SourceBlock,
    columns: "tuple[ColumnBlock, ...]",
    n_rows: int,
    floor: int,
    declared: "tuple[str, ...]" = (),
    metadata_rows: int = 0,
    declared_delimiter: str = "",
) -> None:
    """The invariants that tie the file's written form to the table (FD1-FD13).

    Run after the columns are read, because every one of them needs the
    columns, the row count or the floor. Each names what it compared.
    """
    form = source.dialect
    where = _WRITTEN
    # A DECLARED DELIMITER IS THE ONE THE FILE WAS READ WITH (FD13, plan
    # P4-D110). The declaration exists because nothing in the cells can
    # settle a file that reads equally well two ways, so a description
    # whose written form names another delimiter says two things about
    # one file, and a twin written from it would be read back under the
    # one the settings block does not name. A workbook has no delimiter
    # at all, so it carries no such declaration.
    if declared_delimiter and (
        source.workbook is not None or form.delimiter != declared_delimiter
    ):
        raise _broken(
            "FD13", where,
            f"the person declared {dialect.DELIMITER_WORDS[declared_delimiter]} "
            f"as the delimiter",
            "a delimited file whose written form publishes that same delimiter",
        )
    headed = source.header_source == "file"
    width = len(columns)
    if len(form.columns) != width:
        raise _broken(
            "FD1", where,
            f"the form describes {len(form.columns)} columns",
            f"the table has {width}",
        )
    total = dialect.lines_of(form, n_rows, headed)
    counted = 0
    for index in range(len(form.line_endings)):
        counted = counted + form.line_endings[index].lines
        if index and form.line_endings[index].ending == form.line_endings[index - 1].ending:
            raise _broken(
                "FD2", where,
                "two runs of line endings next to each other end lines the same way",
                "a run is every consecutive line ending one way",
            )
    places = {dialect.ENDINGS[index]: index for index in range(len(dialect.ENDINGS))}
    census = form.line_endings_spread
    for index in range(len(census)):
        counted = counted + census[index].lines
    if census and (
        form.line_endings
        or len(census) < 2
        or counted <= dialect.MAXIMUM_ENDING_RUNS
        or any(
            places[census[index].ending] <= places[census[index - 1].ending]
            for index in range(1, len(census))
        )
    ):
        raise _broken(
            "FD2", where,
            "the line endings are published counted",
            "counts stand in place of runs, for two or more endings in their listed order, only past the cap on runs",
        )
    owed = total - (0 if form.final_line_ending or not total else 1)
    if counted != owed or (form.final_line_ending and not total):
        raise _broken(
            "FD2", where,
            f"the line endings account for {counted} lines",
            f"the file holds {total} lines",
        )
    # ...AND NO RUN OF THEM POINTS AT A RECORD (round 2 of the review,
    # the disclosure pass, item 7; the rule is plan P4-D290's). The
    # producer collapses the runs where an ending's total or a run's
    # own length falls below the line, and now where the RECORDS' own
    # do -- with the lines above the table, which this block publishes,
    # taken off the front. Measured at a floor of eleven: ten title
    # lines, a header and record 1 written with a bare newline against
    # 119 records written with a carriage return and a newline
    # published `[{lf: 12}, {crlf: 119}]`, and 12 less 11 is the first
    # record. `dialect.endings_broken` is that rule, read from this
    # side, so a hand-edited description meets the one the producer
    # writes under.
    lines_above = (
        dialect.preamble_lines_total(form.preamble)
        + len(form.header_rows)
        + (1 if headed else 0)
        + (1 if form.separator_line else 0)
    )
    trouble = dialect.endings_broken(form.line_endings, floor, lines_above)
    if trouble:
        raise _broken(
            "FD2", where,
            trouble,
            "runs whose endings, lengths and records' own each reach the "
            "smallest group size, and never under two",
        )
    wide_encodings = (dialect.ENCODING_UTF16_LE, dialect.ENCODING_UTF16_BE)
    if (form.byte_order_mark and source.encoding in dialect.FALLBACK_ENCODINGS) or (
        source.encoding in wide_encodings and not form.byte_order_mark
    ):
        raise _broken(
            "FD3", where,
            f"the file is named as '{source.encoding}'",
            f"the record of a byte-order mark says {form.byte_order_mark}",
        )
    previous_after = -1
    previous_text = ""
    for place in form.blank_lines:
        spaces_only = all(character in " \t" for character in place.text)
        out_of_order = place.after < previous_after or (
            place.after == previous_after and place.text == previous_text
        )
        inside_one_column = width == 1 and place.after < n_rows
        if not spaces_only or out_of_order or place.after > n_rows or inside_one_column:
            raise _broken(
                "FD4", where,
                f"blank lines are placed after {place.after} records",
                f"the table has {n_rows} records and {width} columns",
            )
        previous_after = place.after
        previous_text = place.text
    if len(form.blank_lines) > dialect.MAXIMUM_BLANK_PLACES or len(
        form.line_endings
    ) > dialect.MAXIMUM_ENDING_RUNS:
        raise _broken(
            "FD4", where,
            "the form is longer than a description may carry",
            "the caps past which the producer publishes counts instead",
        )
    counted_blanks = form.blank_lines_spread
    if counted_blanks is not None and (
        form.blank_lines
        or width < 2
        or counted_blanks.first > counted_blanks.last
        or counted_blanks.last > n_rows
        or counted_blanks.lines <= dialect.MAXIMUM_BLANK_PLACES
        or not all(character in " \t" for character in counted_blanks.text)
    ):
        raise _broken(
            "FD4", where,
            f"{counted_blanks.lines} blank lines are published counted, from after {counted_blanks.first} records to after {counted_blanks.last}",
            f"counts stand in place of places, only past the cap on places, in file order within a table of {n_rows} records and two or more columns",
        )
    sequences = [column.sequence_start >= 0 for column in form.columns]
    empties = form.empty_rows_leading + form.empty_rows_interior + form.empty_rows_trailing
    if empties:
        fewest = min([column.n_missing for column in columns]) if columns else 0
        if (
            width < 2
            or empties > n_rows
            or empties > fewest
            or any(sequences)
        ):
            raise _broken(
                "FD5", where,
                f"{empties} records are published as holding nothing",
                "every column holds at least that many absent cells, in a table of two or more columns with no row sequence",
            )
    for index in range(min(width, len(form.columns))):
        if sequences[index] and (columns[index].n_missing or n_rows < 2):
            raise _broken(
                "FD6", where,
                f"column {index + 1} is published as the row sequence",
                "every one of its cells is present, in a table of two or more rows",
            )
    if form.row_order.column:
        at = form.row_order.column
        if (
            at > width
            or n_rows < 3
            or sequences[at - 1]
            or _written_empty(columns[at - 1]) != empties
        ):
            raise _broken(
                "FD7", where,
                f"the rows are published as sorted by column {at}",
                "a column of the table, not the row sequence, with no empty cell and no absent cell written empty outside the records holding nothing, in a table of three or more rows",
            )
    if form.written_names:
        header = [column.name for column in columns]
        last = 0
        for written in form.written_names:
            if (
                not headed
                or written.position <= last
                or written.position > width
                or written.text == columns[written.position - 1].name
            ):
                raise _broken(
                    "FD8", where,
                    f"a header cell is published as written at column {written.position}",
                    "a header read from the file, with the cells in order and each differing from its column's name",
                )
            header[written.position - 1] = written.text
            last = written.position
        named = dialect.named_columns(tuple(header))
        for index in range(width):
            if named[index] != columns[index].name:
                raise _broken(
                    "FD8", where,
                    f"the header as written names column {index + 1} differently",
                    "the name the description gives that column",
                )
    # FD9 (plan P4-D81). THE PUBLISHED ROWS ARE THE DECLARED ROWS.
    # Without the last clause a description could carry rows of column
    # descriptions that nobody declared -- which is exactly what the
    # producer used to write from a guess, publishing a person's own
    # record as schema text (review item CODEX-2). The count is in the
    # settings block, so the loader can hold the two to each other.
    if form.header_rows and (
        not headed
        or len(form.header_rows) != 2
        or len(form.header_rows) != metadata_rows
        or any(len(row) != width for row in form.header_rows)
    ):
        raise _broken(
            "FD9", where,
            f"{len(form.header_rows)} rows of column descriptions are published",
            f"the {metadata_rows} row(s) the person declared, under a header "
            f"read from the file, each as wide as the table",
        )
    # A DECLARATION THAT FOUND NOTHING IS NOT A REFUSAL. Where a person
    # declares rows of column descriptions and the file turns out not to
    # have them -- they are narrower than the header, or the file is not
    # the export they thought -- the survey takes none and the
    # description publishes none. Refusing that would make a person's
    # honest mistake about their own file into a run that cannot
    # finish, and the reading it produces is the SAFE one: the rows
    # stayed in the table.
    if not form.header_rows and form.header_rows_quoting != dialect.QUOTE_NEEDED:
        raise _broken(
            "FD9", where,
            "a quoting rule is published for rows of column descriptions",
            "there are none",
        )
    if (not headed and (form.header_trailing_delimiter or form.header_quoting != dialect.QUOTE_NEEDED)) or (
        form.short_rows and form.rows_trailing_delimiter
    ):
        raise _broken(
            "FD10", where,
            "the header is published with a trailing delimiter or a quoting rule, or the rows with both a trailing delimiter and left-out empty cells",
            "a header read from the file, and rows written one of those ways at most",
        )
    # FD11 (plan P4-D80). THE FLOOR IS GONE FROM THIS RULE, and that is
    # the point of it: a line before the table is free text somebody
    # wrote, a floor governs how many rows share a value, and one line
    # of prose is not a group of rows -- so the old rule let the whole
    # line through at a floor of one, which is the default (review item
    # CODEX-3). What a description may carry now is the line's SHAPE,
    # and the check that no text rode in with it is that the twin's own
    # neutral line is read back as the very shape published.
    held_text = False
    for run in form.preamble:
        if run.kind != dialect.PREAMBLE_BLANK:
            held_text = True
        if "\r" in run.mark or "\n" in run.mark:
            raise _broken(
                "FD11", where,
                "a run of lines before the table is marked with a line break",
                "one line each",
            )
        # A MARK THE TWIN COULD NOT WRITE IS REFUSED BY NAME (plan
        # P4-D83). The shape check below catches it too, but only by
        # accident of what the stand-in is read back as; this says the
        # rule itself, and it is the clause a description carrying the
        # mark `"` breaks. The twin's first line was then
        # `"withheld line` -- a quoted field nothing closes -- and the
        # twin missed about 120 obligations of the very description
        # that asked for it.
        if dialect.mark_breaks_a_line(run.mark, form.delimiter):
            raise _broken(
                "FD11", where,
                "a run of lines before the table carries a quote "
                "character or the table's own delimiter in its mark",
                "a mark the line the twin writes for it survives, which "
                "is one record of the file",
            )
        standing = dialect.preamble_line(run)
        kind, mark = dialect.preamble_shape(standing)
        if kind != run.kind or mark != run.mark:
            raise _broken(
                "FD11", where,
                f"a run of lines before the table is published as {run.kind}",
                "a shape the line the twin writes for it is read back as",
            )
    if len(form.preamble) > dialect.MAXIMUM_PREAMBLE_LINES:
        raise _broken(
            "FD11", where,
            f"{len(form.preamble)} runs of lines stand before the table",
            f"at most {dialect.MAXIMUM_PREAMBLE_LINES}",
        )
    if form.preamble_withheld != held_text:
        raise _broken(
            "FD11", where,
            f"the lines before the table are published as withheld: "
            f"{form.preamble_withheld}",
            "withheld exactly when one of them held text",
        )
    # FD12 (plan P4-D76). A row sequence is written back by the generator
    # as the cells themselves, so it is published only for a written row
    # index nobody declared; on a declared identifier it would hand back
    # the values the declaration withholds.
    for index in range(min(width, len(form.columns))):
        if form.columns[index].sequence_start < 0:
            continue
        name = columns[index].name
        if name in declared or index != 0 or name not in dialect.INDEX_NAMES:
            raise _broken(
                "FD12", where,
                f"column {index + 1}, {name!r}, is published as the row sequence",
                "a first column named as a written row index is, and not one declared to hold record numbers",
            )
    if form.row_order.column and form.row_order.column <= width:
        name = columns[form.row_order.column - 1].name
        if name in declared:
            raise _broken(
                "FD12", where,
                f"the rows are published as sorted by {name!r}",
                "a column not declared to hold record numbers",
            )


def _declaration(value: object, key: str, where: str) -> DeclarationRecord:
    """One declaration record: the count, the flag, the two lists.

    Contract 5 section 6.2 and invariants C5-S7, C5-S14, C5-K1 to C5-K3.

    `values_recorded` is a discriminator and not a switch: a description
    written before this rule carried an array of spellings under the
    same key, and a consumer must be able to tell the two apart without
    guessing. A description claiming to record the person's own declared
    spellings is not a description this loader accepts, whatever else
    it says.

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
                "in a description this tool writes no text of the "
                "person's own "
                "stands in that block, so the flag reads false in both "
                "records"
            ),
        )
    texts = _built_in_texts(mapping["built_in_texts"], key, where)
    numbers = _built_in_numbers(mapping["built_in_numbers"], key, where)
    days = _built_in_dates(mapping["built_in_dates"], key, where)
    # THE COUNT IDENTITY REACHES ALL THREE LISTS (plan amendment
    # A-P4-1 item 3): a record naming more of this package's own words
    # than it says values were declared is a record that cannot be
    # read back, whichever list the words are in.
    named = len(texts) + len(numbers) + len(days)
    if named > declared:
        raise _broken(
            "C5-K3",
            where,
            f"the record '{key}' names {named} of synthtwin's own words",
            f"it says {declared} value(s) were named that way",
        )
    return DeclarationRecord(
        n_declared=declared,
        values_recorded=recorded,
        built_in_texts=texts,
        built_in_numbers=numbers,
        built_in_dates=days,
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
        if member not in parsing.built_in_missing_texts():
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
        found += [member]
        place = place + 1
    return tuple(found)


def _built_in_dates(
    value: object, key: str, where: str
) -> "tuple[str, ...]":
    """The placeholder days one declaration named (A-P4-1 item 3).

    Every element must be a member of `parsing.calendar_placeholders()`,
    the two days this package judges, and the list is sorted and holds
    no repeat -- the same shape and the same identity rules the numeric
    list carries, so a consumer can tell a day this package supplied
    from a day somebody typed.
    """
    listed = _listing(value, f"{key} -> built_in_dates", where)
    seen: list[str] = []
    for item in listed:
        member = _text(item, f"{key} -> built_in_dates", where)
        if member not in parsing.calendar_placeholders():
            raise _out_of_range(
                f"{key} -> built_in_dates",
                where,
                f"'{member}'",
                _listed(parsing.calendar_placeholders()),
            )
        if seen and member <= seen[len(seen) - 1]:
            raise _broken(
                "C5-K2",
                where,
                f"the record '{key}' names '{member}' out of order",
                "the days it names are sorted and none is repeated",
            )
        seen += [member]
    return tuple(seen)


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
        found += [member]
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
    synthtwin's own twenty-three words, but naming it here would put the
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
        declared += [found]
        place = place + 1
    declared_measurements: list[str] = []
    measured_names = _listing(
        mapping["forced_measurements"], "forced_measurements", where
    )
    place = 0
    for name in measured_names:
        found = _text(name, f"forced_measurements[{place}]", where)
        if declared_measurements and found <= declared_measurements[
            len(declared_measurements) - 1
        ]:
            raise _out_of_range(
                "forced_measurements",
                where,
                f"'{found}'",
                "names in rising order, each of them once",
            )
        declared_measurements += [found]
        place = place + 1
    declared_commas: list[str] = []
    comma_names = _listing(
        mapping["forced_decimal_commas"], "forced_decimal_commas", where
    )
    place = 0
    for name in comma_names:
        found = _text(name, f"forced_decimal_commas[{place}]", where)
        if declared_commas and found <= declared_commas[
            len(declared_commas) - 1
        ]:
            raise _out_of_range(
                "forced_decimal_commas",
                where,
                f"'{found}'",
                "names in rising order, each of them once",
            )
        declared_commas += [found]
        place = place + 1
    declared_codes: list[str] = []
    code_names = _listing(mapping["forced_codes"], "forced_codes", where)
    place = 0
    for name in code_names:
        found = _text(name, f"forced_codes[{place}]", where)
        if declared_codes and found <= declared_codes[len(declared_codes) - 1]:
            raise _out_of_range(
                "forced_codes",
                where,
                f"'{found}'",
                "names in rising order, each of them once",
            )
        declared_codes += [found]
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
        day_first=_truth(mapping["day_first"], "day_first", where),
        long_tail_minimum_level=_exactly(
            mapping["long_tail_minimum_level"],
            "long_tail_minimum_level",
            where,
            LONG_TAIL_LINE,
        ),
        forced_identifiers=tuple(declared),
        forced_codes=tuple(declared_codes),
        forced_measurements=tuple(declared_measurements),
        forced_decimal_commas=tuple(declared_commas),
        # HOW MANY ROWS UNDER THE NAMES DESCRIBE THE COLUMNS (plan
        # P4-D81). Read here so that FD9 can hold the published rows of
        # column descriptions to the declaration, and so that the
        # validator re-reads a checked file the way the description was
        # written: without it, rows nobody declared could stand in a
        # description as schema, which is how a person's own record was
        # published verbatim (review item CODEX-2).
        forced_metadata_rows=_whole(
            mapping["forced_metadata_rows"], "forced_metadata_rows", where, 0
        ),
        # WHICH DELIMITER THE PERSON DECLARED (plan P4-D110). Nothing,
        # or one of the four this format reads; FD13 then holds it to
        # the written form once the source block and the table are both
        # read.
        forced_delimiter=_one_of(
            mapping["forced_delimiter"],
            "forced_delimiter",
            where,
            ("",) + dialect.DELIMITERS,
        ),
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
        notes += [
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
        date_sentinel=counted[DATE_SENTINEL],
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
    # THE EMPTY SPELLING IS NEVER A KEY (C5-N3, plan P4-D74). It has a
    # field of its own, `n_missing_blank`, and a document naming it here
    # as well would count one cell twice in the accounting below. A key
    # that is only SPACE is a different matter and is admitted: a space
    # is a mark the file holds, the twin reproduces it, and the floor
    # governs it exactly as it governs every other spelling.
    for name in sorted(counted):
        if name == "":
            raise _broken(
                "C5-N3",
                where,
                "a spelling of an empty cell is named with no characters",
                "cells that held nothing are counted in `n_missing_blank`",
            )
    if publishes_nothing:
        # THE KEYS OF SUCH A COLUMN ARE THIS PACKAGE'S OWN WORDS, AND
        # THAT IS CHECKED HERE RATHER THAN TRUSTED (plan P4-D85). A
        # column publishing no value of the table may still say that
        # some of its absent cells were spelled `NA` -- because `NA` is
        # not a value of anybody's table, it is a member of the
        # published vocabulary C6-31 fixes, identical in every
        # installation. What it may not say is anything else, and the
        # rule is enforceable exactly because the vocabulary is closed:
        # a key that names no member is a spelling out of the column,
        # and it is refused by name.
        #
        # A DECLARED SPELLING OF THE PERSON'S OWN WORDS IS NOT ADMITTED
        # HERE, and the reason is this loader's own reach. A declaration
        # is recorded as a COUNT and never as text (C5-17), so no
        # document tells `Not documented` declared apart from
        # `Not documented` written in a cell, and a rule admitting it
        # could not be checked by anything holding one document. Those
        # cells stay in the pooled remainder.
        for name in sorted(counted):
            if not parsing.names_a_published_word(name):
                raise _broken(
                    "C5-N3",
                    where,
                    "this column publishes no value of the table",
                    (
                        "it names a spelling of an empty cell that is no "
                        "word of synthtwin's own published vocabulary"
                    ),
                )
        # ...AND THE SUM IS AN UPPER BOUND HERE, NOT AN EQUALITY. A
        # spelling that is none of synthtwin's own words is withheld by
        # the CLASS, at every floor, and it is not added to the pooled
        # remainder, because that remainder is what the FLOOR held back
        # and a floor-one description holds nothing back (C5-S13). So
        # such cells are counted in `n_missing` and accounted for by
        # nothing, and what a loader can check is that the accounting
        # never claims MORE cells than the column has.
        accounted = _added(counted) + n_blank + n_withheld
        if accounted > n_missing:
            raise _broken(
                "C5-N3",
                where,
                f"the empty cells accounted for come to {accounted}",
                f"the column counts {n_missing} empty cells",
            )
        for name in sorted(counted):
            if counted[name] < floor:
                raise _broken(
                    "C5-N4",
                    where,
                    (
                        f"the spelling named there was written by "
                        f"{counted[name]} rows"
                    ),
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


def _judged_spellings(
    value: object,
    where: str,
    verdict: str,
    counts: "dict[str, int]",
    occurrences: int,
    claimed: "dict[str, int]",
    floor: int,
) -> "tuple[str, ...]":
    """The published hole spellings one decision took out (5.5, V5).

    THE PROVENANCE OF A HOLE SPELLING, WHICH NO COUNT CAN SUPPLY
    (repair pass of landing 2b.6). A spelling standing here was made
    absent by THIS column's judged pass; every other key of
    `missing_by_source` was made absent by something that reaches the
    whole table -- a word the person declared, or one of this package's
    own. The walk that tried to tell the two apart by counting cells
    could not: twenty judged `1900-01-01 00:00:00` beside thirty
    declared `1900-01-01T00:00:00` are two keys writing one day, and
    every count the document carries is the same under either reading.

    Raises ProfileError for a value that is not a list of text and for
    V5 in its six parts: a decision that kept its candidate names no
    spelling, every spelling it names is one this column publishes
    among its absent cells, the names are in order and distinct (which
    is also what the canonical bytes require), no spelling is named by
    two decisions of one column, the cells those spellings cover never
    outnumber the rows the decision says held its candidate, and they
    never fall exactly one short of them either -- the sixth is round
    2's item 2, and the comment on it says what one short gives away.

    THE LAST TWO ARE LANDING 2b.14'S, AND THEY CLOSE THE LOOP THE
    REPAIR PASS OF LANDING 2b.6 LEFT OPEN (decision P4-D95). That pass
    moved the question out of the two consumers and into the document,
    which was right; what it did not do was CHECK the answer on the way
    back in. Every count in the block reads the same under either
    assignment -- that is the whole reason the key exists -- so a
    description could say that a word the PERSON DECLARED was one
    column's own judged pass, and this loader read it and passed it on.
    Measured on the reviewer's own 500-row table, hand-edited: the
    generator then stops reserving that word for the whole table and
    writes it into a second column as a present value, and the
    validator stops recovering it as a declaration, which is landing
    2b.3's defect restored through a document rather than through a
    count. Both new parts are arithmetic on the block itself, they need
    no cell of any table, and together they refuse every such document
    while accepting every one a producer can write.

    THE BOUND IS `AT MOST` AND NOT `EXACTLY`, which is the floor's
    doing and was measured before it was written. A pass takes every
    cell of its candidate, but the description names only those
    spellings the floor let it publish: a column holding twenty
    `1900-01-01 00:00:00` beside five `1900-01-01T00:00:00`, both
    judged, publishes at a floor of eleven one spelling worth twenty
    cells against an `n_occurrences` of twenty-five, and pools the
    other five. Demanding equality would refuse that description.

    ...AND WHAT IS LEFT OVER IS NOUGHT OR REACHES THE FLOOR (the repair
    pass of this landing, round 2's disclosure finding 3). The bound
    above is still `at most`, and it is not equality; what changed is
    the SIZE of the difference this loader will read. The remainder
    counts cells wearing spellings the description never names and
    publishes no total for, so five of twenty-five at a floor of eleven
    is five people recoverable by subtraction, not an acceptable
    rounding -- the producer next door (`taxonomy._judged_totals`) now
    pools until that remainder is nought or reaches the floor, and
    `synthtwin generate` refuses any description that says otherwise,
    hand-written or not. At the DEFAULT floor of one nothing moves:
    `parsing.census_floor(1)` is two, which is the line this part
    already asked.

    NO REFUSAL HERE PRINTS A SPELLING. A key of `missing_by_source` is
    a value out of somebody's table (C5-N5, R15), so what is wrong is
    named by WHAT IT IS and counted, never quoted -- the rule
    `_entry_named` follows one field over. The two new refusals are
    written to the same rule: each counts, and neither quotes.

    Guarantees: accepts the list, where it stands, the decision's own
    verdict, this column's published hole spellings WITH THEIR COUNTS,
    the rows the decision says held its candidate, the spellings every
    earlier decision of this column already named -- which this
    function adds to -- and the smallest group size. Determinism: a
    function of the seven. No I/O.
    """
    listed = _listing(value, "spellings", where)
    found: list[str] = []
    place = 0
    for entry in listed:
        found += [_text(entry, f"spellings[{place}]", where)]
        place = place + 1
    if verdict != VERDICT_MISSING and found:
        raise _broken(
            "V5",
            where,
            "this decision kept the stand-in number as a number",
            f"it names {len(found)} spelling(s) of an empty cell anyway",
        )
    unnamed = 0
    for spelling in found:
        if spelling not in counts:
            unnamed = unnamed + 1
    if unnamed:
        raise _broken(
            "V5",
            where,
            f"this decision names {unnamed} spelling(s) of an empty cell",
            "this column publishes no such spelling among its absent cells",
        )
    if found != sorted(found) or len(found) != len(set(found)):
        raise _broken(
            "V5",
            where,
            f"this decision names {len(found)} spelling(s)",
            "the spellings of one decision are in order and each named once",
        )
    # A CELL IS TAKEN OUT ONCE, so two decisions of one column cannot
    # both have taken the cells of one spelling (P4-D95).
    twice = 0
    for spelling in found:
        if spelling in claimed:
            twice = twice + 1
    if twice:
        raise _broken(
            "V5",
            where,
            f"this decision names {twice} spelling(s) of an empty cell",
            "an earlier decision of this column already named them",
        )
    # ...and a decision cannot have taken out more cells than the rows
    # it says held its candidate. This is what refuses a description
    # claiming a DECLARED word was this column's own judgement: the
    # declared spelling's cells push the total past `n_occurrences`,
    # and no count in the block could say so before (P4-D95).
    covered = 0
    for spelling in found:
        covered = covered + counts[spelling]
    if covered > occurrences:
        raise _broken(
            "V5",
            where,
            f"the spellings this decision names cover {covered} absent cell(s)",
            f"it says {occurrences} row(s) held its stand-in number",
        )
    # ...AND THE DIFFERENCE BETWEEN THEM IS A CENSUS READING LIKE ANY
    # OTHER (round 2 of the review, the disclosure pass, item 2; its
    # repair pass raised the line). What the decision's occurrences
    # leave over its named spellings is the count of cells wearing the
    # spellings the floor POOLED, and the pool exists to hide exactly
    # that. The question is the producer's own,
    # `parsing.census_names_one_row` over the pair at the settings
    # floor -- so a decision naming no spelling at all is asked
    # nothing, as an empty census always is, and what is left over is
    # nought or names a group the floor lets a reader see.
    if parsing.census_names_one_row({}, [(occurrences, covered)], floor) == 0:
        raise _broken(
            "V5",
            where,
            f"the spellings this decision names cover {covered} absent cell(s)",
            (
                f"it says {occurrences} row(s) held its stand-in number, and "
                f"what is left over names fewer than "
                f"{parsing.census_floor(floor)} of them"
            ),
        )
    for spelling in found:
        claimed[spelling] = 1
    return tuple(found)


def _sentinel_verdicts(
    value: object,
    where: str,
    floor: int,
    publishes_nothing: bool,
    counts: "dict[str, int]",
    n_withheld: int = 0,
) -> "tuple[SentinelVerdict, ...]":
    """What was decided about each named stand-in number, and why (5.5).

    Raises ProfileError for an unknown or missing key, a wrong type, a
    value outside its list, and for V1 to V4. V5 is raised one field
    over, in `_judged_spellings`; two of its five parts are questions
    about the column's decisions TOGETHER rather than about one of
    them, so this walk carries `claimed` down the list and each
    decision adds the spellings it names to it (P4-D95).

    IT TAKES THE COUNTS AND NOT THE KEYS, and that is the whole of the
    change landing 2b.14 made here: the bound V5 now enforces is how
    many CELLS a decision's named spellings cover, which the keys alone
    cannot say. V2 is the publication
    class applied to this block: on a column that publishes no value of
    the table every candidate reads `(withheld)`, and on every other
    column none of them does, because naming a candidate there would
    publish a value out of a column that publishes none.
    """
    listed = _listing(value, "sentinel_verdicts", where)
    entries: list[SentinelVerdict] = []
    # The spellings every decision read so far has named, so that no two
    # of them claim one spelling's cells (V5, P4-D95).
    claimed: "dict[str, int]" = {}
    place = 0
    previous: tuple[int, str, str] | None = None
    previous_number: float | None = None
    previous_day: "str | None" = None
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
        # THE FLOOR IS ASKED FIRST, and the order is part of the rule
        # rather than an accident of writing (landing 2b.14). V5's count
        # bound compares this decision's `n_occurrences` against the
        # cells its spellings cover, so a decision naming FEWER rows
        # than the floor breaks the bound as well -- and V1 is the
        # narrower, truer diagnosis of that document. Asked the other
        # way round, a description held by too few rows to be named at
        # all was refused for its arithmetic instead of for being
        # unpublishable, and the battery's V1 entry stopped exercising
        # V1.
        if occurrences < floor:
            raise _broken(
                "V1",
                seat,
                f"the stand-in number was held by {occurrences} rows",
                f"the smallest group size is {floor}",
            )
        spellings = _judged_spellings(
            mapping["spellings"],
            seat,
            verdict,
            counts,
            occurrences,
            claimed,
            floor,
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
        elif candidate in parsing.calendar_placeholders():
            # A PLACEHOLDER DAY, WHICH IS NOT A NUMBER AND IS NOT
            # ORDERED AS ONE (plan amendment A-P4-1 item 3, invariant
            # V4). The decisions of one column carry every numeric
            # candidate first, ascending by number, then every
            # placeholder day, ascending as text -- so a reader
            # checking the order has one rule per kind and the two
            # kinds never interleave.
            if previous_day is not None and candidate < previous_day:
                raise _broken(
                    "V4",
                    seat,
                    f"this decision is about '{candidate}'",
                    f"the one before it is about '{previous_day}'",
                )
            previous_day = candidate
        else:
            if previous_day is not None:
                raise _broken(
                    "V4",
                    seat,
                    "this decision is about a stand-in number",
                    (
                        "the one before it is about a placeholder day, "
                        "and every number comes first"
                    ),
                )
            number = _reads_as_a_number(candidate, "candidate", seat)
            if previous_number is not None and number < previous_number:
                raise _broken(
                    "V4",
                    seat,
                    f"this decision is about {number}",
                    f"the one before it is about {previous_number}",
                )
            previous_number = number
        entries += [
            SentinelVerdict(
                candidate=candidate,
                verdict=verdict,
                reason=reason,
                n_occurrences=occurrences,
                spellings=spellings,
            )
        ]
        place = place + 1
    _unnamed_judged_cells(entries, where, publishes_nothing, counts, n_withheld)
    return tuple(entries)


def _unnamed_judged_cells(
    entries: "list[SentinelVerdict]",
    where: str,
    publishes_nothing: bool,
    counts: "dict[str, int]",
    n_withheld: int,
) -> None:
    """V5's last part: a judged cell no spelling names is a pooled cell.

    A decision that read its candidate as "no value" took out
    `n_occurrences` cells. Those its `spellings` name are counted under
    those keys; every OTHER one was pooled, because a spelling the floor
    did not let the column name goes to `n_missing_withheld` and nowhere
    else. So the cells the decisions of one column leave unnamed, added
    over ALL of them, fit in that one pool -- the pool is spent once, not
    once per decision (plan P4-D135).

    WHY (review of 158c811, item 6). The two parts before it bound a
    decision's named spellings from above and left the omission open: a
    judged decision taking twenty `1900-01-01 00:00:00` cells, edited to
    name no spelling beside a pool of nought, loaded -- and with the link
    gone the validator read that spelling as a declaration reaching the
    whole table, so an unchanged second column fell from 500 values to
    420 and missed 13 obligations. No producer writes that document: the
    twenty cells are counted under a key or in the pool, and nowhere else.

    A column that publishes no value of the table accounts for no absent
    cell by spelling at all (C5-N3), so there is nothing here to add up.

    Guarantees: accepts the column's decisions, where they stand, whether
    the column publishes values, its hole spellings with their counts and
    its pooled count; returns nothing. Raises ProfileError for V5. No I/O.
    """
    if publishes_nothing:
        return
    unnamed = 0
    for entry in entries:
        if entry.verdict != VERDICT_MISSING:
            continue
        covered = 0
        for spelling in entry.spellings:
            covered = covered + counts[spelling]
        unnamed = unnamed + (entry.n_occurrences - covered)
    if unnamed > n_withheld:
        raise _broken(
            "V5",
            where,
            f"the decisions that read a stand-in as no value leave "
            f"{unnamed} of the cells they took out named by no spelling",
            f"the column holds back the spellings of {n_withheld} absent "
            f"cell(s)",
        )


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
        mapping["sentinel_verdicts"],
        where,
        frame.floor,
        publishes_nothing,
        by_source,
        n_withheld,
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
        remarks += [_text(remark, f"remarks[{place}]", where)]
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


def _where_after(said: str, part: str, start: int) -> int:
    """Where one fragment stands at or after `start`, or -1.

    THE STRUCTURAL HALF OF AF-R (review item L19-R1-1). The fragments
    of the required remark were each looked for in the WHOLE sentence,
    and one of them is quoted inside the block's own affix pair: a
    column whose cells read `12 run the command again with --code NAME`
    publishes that text as its suffix, so the advice fragment was found
    inside the quotation -- before the advice itself -- the order test
    failed, and the LOADER REFUSED A DESCRIPTION ITS OWN PROFILER HAD
    JUST WRITTEN. The refusal told the person to make the description
    again, which reproduced it exactly.

    A person's own data may spell anything. The fragments after the
    affix clause are therefore looked for after the affix clause, which
    is a position the data cannot reach.

    Written with slicing rather than `find` for the reason `_where`
    gives: a method call whose argument the offline audit cannot
    resolve is a call it cannot judge.
    """
    if not isinstance(said, str) or not isinstance(part, str):
        raise TypeError("internal check: a sentence was not text")
    span = len(part)
    for place in range(max(start, 0), len(said) - span + 1):
        if said[place : place + span] == part:
            return place
    return -1


def _affix_clause(prefix: str, suffix: str) -> str:
    """The clause the required remark writes about THIS block's pair.

    Four shapes, because one side is usually empty and a sentence
    saying "written as nothing, a number, then 'mg'" describes a shape
    no cell has. Built from the block's OWN two spellings, so a remark
    holding this clause names the pair the block publishes, character
    for character -- which is what AF-R asks and what a check of the
    sentence's generic fragments alone could not tell: a block
    publishing `$` accepted a remark saying `'kg' followed by a
    number`, a required warning that misdescribes the column it warns
    about.

    AND THE FOURTH IS THE BARE WRAPPER (plan P4-D36), which a column
    wearing a SET may publish as its commonest: most laboratory results
    carry no abnormal flag, so on the shape that landing was written
    for, the wrapper worn by most cells is no text at all. With three
    shapes this clause read `written as a number followed by ''`, the
    producer's own sentence read the same, and THIS LOADER REFUSED THE
    PRODUCER'S OWN DOCUMENT -- `synthtwin profile` wrote a file
    `synthtwin generate` would not take. The sentence must stay
    character-for-character the one `taxonomy._affix_shape` renders,
    which is what `tests/test_p4d4_affixed_role.py` holds it to.
    """
    if prefix and suffix:
        return f"written as '{prefix}', a number, then '{suffix}'"
    if prefix:
        return f"written as '{prefix}' followed by a number"
    if suffix:
        return f"written as a number followed by '{suffix}'"
    return "written as a number, with others wearing text beside it"


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
    # THE OPENING IS A POSITION, NOT A SEARCH (review item L19-R1-1).
    # The count and the fixed opening words stand at the front of the
    # sentence or the sentence is not the one AF-R requires -- and
    # pinning them here is also what keeps the block's own affix pair,
    # which a person's data spells and this loader cannot bound, out of
    # the way of every fragment after it.
    head = f"{n_affixed} of this column's values are "
    if remark[: len(head)] != head:
        return False
    # The pair's own clause, which is where the block's two published
    # spellings have to appear, AT the position the opening leaves for
    # it rather than anywhere in the sentence.
    if remark[len(head) : len(head) + len(clause)] != clause:
        return False
    after = len(head) + len(clause)
    second = _where_after(
        remark,
        "and synthtwin described those numbers as quantities: their "
        "average, their spread and their ends are in this profile.",
        after,
    )
    third = _where_after(
        remark, "If these are codes rather than measurements", after
    )
    fourth = _where_after(
        remark, "run the command again with --code NAME", after
    )
    fifth = _where_after(
        remark,
        "--identifier NAME leaves them out of the profile altogether",
        after,
    )
    if second < 0 or third < 0 or fourth < 0 or fifth < 0:
        return False
    return second < third < fourth < fifth


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
    if role == ROLE_LONG_TAIL:
        # THE FOUR SHARED LABEL KEYS AND NOT `level_ceiling` (plan
        # P4-D5, stated there so no ambiguity survives into this
        # contract). That key is categorical's own, and its invariant --
        # folded distinctness at or under the ceiling -- is exactly what
        # a long-tail column breaks by definition. The format has no
        # optional keys, so the ceiling this column PASSED is recorded
        # in its evidence sentence instead.
        #
        # The form census is NOT among them: it is one of the five
        # every label role carries (P4-D18, corrected).
        return LONG_TAIL_KEYS
    if role == ROLE_DATETIME:
        return DATETIME_KEYS
    if role == ROLE_COUNT:
        return COUNT_KEYS
    if role == ROLE_CONTINUOUS:
        return NUMERIC_KEYS
    if role == ROLE_CLOCK:
        return CLOCK_KEYS
    if role == ROLE_JOINED:
        return JOINED_KEYS
    if role == ROLE_COMPOUND:
        return COMPOUND_KEYS
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
    # W9 IS ASKED OF ALL FOUR LEVEL ROLES HERE, where `n_distinct` is in
    # hand, and of a compound column's label half by its own reader.
    if role == ROLE_CONSTANT or role == ROLE_BINARY:
        labelled = _label_facts(
            mapping, where, role, frame.floor, n_present, n_folded
        )
        _spellings_spoken(
            labelled.levels,
            labelled.suppressed_levels,
            labelled.suppressed_rows,
            n_distinct,
            where,
        )
        return labelled
    if role == ROLE_CATEGORICAL:
        categories = _categorical_facts(
            mapping, where, frame.floor, n_present, n_folded
        )
        _spellings_spoken(
            categories.levels,
            categories.suppressed_levels,
            categories.suppressed_rows,
            n_distinct,
            where,
        )
        return categories
    if role == ROLE_LONG_TAIL:
        named = mapping["name"] if "name" in mapping else None
        tail = _long_tail_facts(
            mapping,
            where,
            frame.floor,
            n_present,
            n_folded,
            _category_ceiling(frame),
            isinstance(named, str) and named in frame.declared_codes,
        )
        _spellings_spoken(
            tail.levels,
            tail.suppressed_levels,
            tail.suppressed_rows,
            n_distinct,
            where,
        )
        return tail
    if role == ROLE_DATETIME:
        return _datetime_facts(mapping, where, frame.floor, n_present)
    if role == ROLE_COUNT or role == ROLE_CONTINUOUS:
        numeric = _numeric_facts(
            mapping,
            where,
            frame,
            n_present,
            n_numeric,
            n_out_of_range,
            n_contradictory,
        )
        if role == ROLE_CONTINUOUS:
            return numeric
        return dataclasses.replace(
            numeric,
            number_spellings=_number_spellings(
                mapping, where, frame, n_numeric, numeric.n_zero
            ),
        )
    if role == ROLE_CLOCK:
        return _clock_facts(mapping, where, frame, n_present)
    if role == ROLE_JOINED:
        return _joined_facts(mapping, where, frame, n_present)
    if role == ROLE_COMPOUND:
        named = mapping["name"] if "name" in mapping else None
        return _compound_facts(
            mapping,
            where,
            frame,
            n_present,
            n_distinct,
            n_folded,
            isinstance(named, str) and named in frame.declared_commas,
        )
    if role == ROLE_AFFIXED:
        return _affixed_facts(mapping, where, frame, n_present, remarks)
    if role == ROLE_IDENTIFIER:
        return _identifier_facts(
            mapping, where, n_present, n_distinct, frame.floor
        )
    return _text_facts(mapping, where, n_present, n_distinct, frame.floor)


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
    for U1, U2, U3 and U5.

    THIS ROLE PUBLISHES A WIDTH PAIR AND THIS DOCSTRING SAID IT
    PUBLISHED NONE (review item P4-A2-R3, item 4). `min_length` and
    `max_length` are loaded below, each a counting number from one
    upward, and U5 refuses the pair where the shortest value is longer
    than the longest. The sentence this replaces was written while the
    contract really did publish neither, was carried unchanged through
    the landing that added both, and stood immediately above the two
    lines that read them -- so a contributor reading the loader's own
    stated word was told the opposite of what the loader does.
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
    smallest = _whole(mapping["min_length"], "min_length", where, 1)
    largest = _whole(mapping["max_length"], "max_length", where, 1)
    if smallest > largest:
        raise _broken(
            "U5",
            where,
            f"the shortest value is {smallest} character(s)",
            f"the longest is {largest}",
        )
    return UnrepresentableFacts(
        min_length=smallest,
        max_length=largest,
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
    inside_a_half: bool = False,
) -> "tuple[tuple[LevelEntry, ...], int, int]":
    """The published labels and everything the floor held back (6.3).

    Raises ProfileError for a wrong type or an out-of-range count, and
    for B1 to B7 and W2 to W7 -- B4 over the pooled total alone since the
    owner's ruling of 2026-09-17 (plan P4-D201), and B4b over the pool a
    reader takes by subtraction since item 5 of the same ruling (plan
    P4-D231). B8 is a permission rather than a rule: an
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
    # B4, THE POOL (owner ruling of 2026-09-17, item 2, option A; plan
    # P4-D201). No size of any held-back label is published, so what can
    # be refused is the pool: every held-back label covers at least one
    # row and fewer than the floor, which bounds the rows by the labels
    # both ways -- and at a floor of one both are nought, which is S13.
    if suppressed_rows < suppressed_levels:
        raise _broken(
            "B4",
            where,
            f"{suppressed_levels} labels are said to be held back",
            f"they cover only {suppressed_rows} rows between them",
        )
    if suppressed_rows > suppressed_levels * (floor - 1):
        raise _broken(
            "B4",
            where,
            (
                f"{suppressed_levels} labels held back are said to cover "
                f"{suppressed_rows} rows"
            ),
            (
                f"a label held back covers fewer rows than the smallest "
                f"group size of {floor}"
            ),
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
        variants, withheld = _variants(
            block, seat, floor, label, count, inside_a_half
        )
        entries += [
            LevelEntry(
                label=label,
                count=count,
                variants=variants,
                variants_withheld=withheld,
                shape_form_cells=_shape_form_cells(
                    block, seat, label, variants, withheld
                ),
            )
        ]
        seen += [label]
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
    # B4b, THE POOL A READER SUBTRACTS (the owner's ruling of
    # 2026-09-17, item 5; plan P4-D231). B3 above says the pool IS
    # `n_present` less the published counts, so a reader holds it
    # whether or not a key prints it; this asks the one disclosure rule
    # of that subtraction. The pool is nought or reaches
    # `parsing.census_floor`, and a document whose levels leave one row,
    # or any group below that line, unaccounted for is refused. The
    # producer counts those cells as missing instead, so no description
    # it writes reaches this refusal.
    if parsing.pool_names_a_level(
        suppressed_levels, suppressed_rows, covered
    ):
        raise _broken(
            "B4b",
            where,
            (
                f"{suppressed_levels} label(s) held back are said to "
                f"cover {suppressed_rows} row(s) between them"
            ),
            (
                "held-back labels covering fewer rows than twice their "
                "number, or exactly their own number of rows while "
                "covering fewer than the published labels do, force a "
                "count of one, which a reader works out by subtraction"
            ),
        )
    _levels_against_their_classes(mapping, where, entries, inside_a_half)
    _levels_against_their_forms(mapping, where, entries)
    return tuple(entries), suppressed_levels, suppressed_rows


# What one published label READS AS, and the total that counts it. The
# four are the U-family of contract 6.2 and they come to `n_present`.
_READING_TOTALS = (
    (parsing.NUMBER, "n_numeric"),
    (parsing.NOT_A_NUMBER, "n_not_numeric"),
    (parsing.NUMBER_OUT_OF_RANGE, "n_out_of_range"),
    (parsing.NUMBER_CONTRADICTORY, "n_contradictory"),
)


def _levels_against_their_classes(
    mapping: "dict[str, object]",
    where: str,
    entries: "list[LevelEntry]",
    inside_a_half: bool,
) -> None:
    """B4c: no SIBLING TOTAL leaves exactly one held-back row (P4-D261).

    B4b asks the disclosure rule of the whole pool. This asks it of each
    of the four totals a reader holds beside the levels -- `n_numeric`,
    `n_not_numeric`, `n_out_of_range` and `n_contradictory` -- because a
    pool far too large to force a count of one can still leave ONE row
    inside one of them. Measured before this check: `alpha` and `beta` a
    hundred rows each, `1` five rows, `2` six rows and `gamma` one row at
    a floor of eleven published `n_not_numeric` 201 with both words at
    100, and 201 less 200 is the withheld word's own count of one.

    THE QUESTION IS `parsing.census_names_one_row`, over the same pairs
    the form and layout censuses hand it, so the difference of one is
    refused by the one rule and not by a second copy of it. A total no
    published label counts into is not read, exactly as there: a census
    that says nothing about a total leaves a reader nothing to subtract.

    A LABEL WHOSE CLASS THE TWO GRAMMARS DISAGREE ABOUT IS NOT READ, and
    nor is any other label of that column. A column declared
    `--decimal-comma` is read by the producer with the comma as a point,
    and a loader that guessed wrong would refuse a description nobody had
    touched -- which this repository treats as the worst refusal there
    is. Where every label reads the same way under both grammars there is
    nothing to guess, and that covers the shape this rule is for.

    Raises ProfileError for B4c. No I/O of any kind.
    """
    if inside_a_half or "n_numeric" not in mapping:
        return
    covered: "dict[str, int]" = {}
    for entry in entries:
        plain = parsing.classify_number(entry.label)
        commaed = parsing.classify_number(
            parsing.written_with_a_decimal_comma(entry.label)
        )
        if plain != commaed:
            return
        covered[plain] = (covered[plain] if plain in covered else 0) + entry.count
    for reading, key in _READING_TOTALS:
        total = _whole(mapping[key], key, where, 0)
        seen = covered[reading] if reading in covered else 0
        rest = total - seen
        if rest < 0:
            continue
        if parsing.census_names_one_row({reading: rest}, [(total, seen)]) == -1:
            continue
        raise _broken(
            "B4c",
            where,
            (
                f"the published labels that read as '{reading}' cover "
                f"{seen} of the {total} rows {key} counts"
            ),
            (
                f"the {rest} row(s) left over are held back, so one "
                f"held-back label covers that one row"
            ),
        )


def _levels_against_their_forms(
    mapping: "dict[str, object]",
    where: str,
    entries: "list[LevelEntry]",
) -> None:
    """B4c over the FORM census, the other total the levels subtract from.

    (Round 2 of the review, the disclosure pass, item 3.) Every level
    entry publishes `shape_form_cells`, how many of its rows wrote the
    label in the label's own form, and the block publishes a
    column-wide `shape_forms` census beside them. Those count the same
    cells, so a named form less the published levels' own contributions
    is the cells of HELD-BACK levels wearing that form -- and one of
    them is one row, with its form published. **Measured** on the
    reviewer's column at a floor of eleven: `ABC-100` and `ABC-200` a
    hundred rows each at `shape_form_cells` 100, one `ABC-300`, five
    `QQ-400` and six `RR-500`, published `shape_forms {"@@@-%%%": 201,
    "@@-%%%": 11}`, and 201 less 200 is that one row. The producer now
    counts such a level's cells as missing (the owner's ruling of
    2026-09-17, item 5), so no description it writes reaches here.

    THE QUESTION IS `parsing.census_names_one_row`, the pair the class
    check beside it hands over and the same one the form census's own
    `_form_census_names_no_row` asks of its other totals.

    WHAT IS NOT READ, and it is the case rule's doing. A form whose
    lower-case cells were named apart stands in the census under two
    keys, and which of a level's cells went under which is a fact of
    the SPELLINGS rather than of the folded label this walk holds -- so
    a form with a lower-case sibling in the census, and a lower-case key
    itself, are passed over rather than guessed at. Guessing would
    refuse descriptions a producer writes, which this repository treats
    as the worst refusal there is; the producer's own pass reads the
    split faithfully, and this stays the backstop for the shape the
    reviewer reproduced.

    Raises ProfileError for B4c. No I/O of any kind.
    """
    if "shape_forms" not in mapping:
        return
    forms = _counts(mapping["shape_forms"], "shape_forms", where, 1)
    covered: "dict[str, int]" = {}
    for entry in entries:
        key = parsing.shape_form(entry.label)
        if not key:
            continue
        covered[key] = (
            covered[key] if key in covered else 0
        ) + entry.shape_form_cells
    for name in sorted(forms):
        if name == WITHHELD or parsing.SHAPE_LOWER in name:
            continue
        if parsing.lower_case_form(name) in forms:
            continue
        total = forms[name]
        seen = covered[name] if name in covered else 0
        rest = total - seen
        if rest < 0:
            continue
        if parsing.census_names_one_row({}, [(total, seen)]) == -1:
            continue
        raise _broken(
            "B4c",
            where,
            (
                f"the published labels written in one form cover {seen} "
                f"of the {total} cells that form counts"
            ),
            (
                f"the {rest} cell(s) left over belong to held-back "
                f"labels, so one held-back label covers that one cell "
                f"and its written form is published"
            ),
        )


def _shape_form_cells(
    block: "dict[str, object]",
    seat: str,
    label: str,
    variants: "dict[str, int]",
    withheld: "dict[str, int]",
) -> int:
    """How many rows wrote this label in its own form (7.4.8, W8).

    THE FACT THAT LETS A LEVEL'S MADE-UP SPELLINGS KEEP ITS SHAPE. The
    column-wide `shape_forms` census cannot say which of a level's
    held-back spellings wore the label's form, so a generator reading
    the description alone guessed -- and missed in both directions
    (residual R-P4-34, plan amendment A-P4-47).

    **W8, and it is TWO bounds and no sum.** The named spellings that
    have a form already account for cells this number may not fall
    below; the cells that could still be wearing one are the rows the
    floor held back, so the number may not rise above the two together.
    Both ends are facts of THIS ENTRY -- nothing here is compared
    against the column's own census, and residual R-P4-80 is why: the
    column census pools below the floor, refuses a form the column has
    no room for, and counts cells of levels that are not published at
    all, so it is a fact of its own beside these and not their sum. A
    reader looking here for a sum rule is looking for something this
    format deliberately does not state.

    **AND A LABEL WITH NO FORM CARRIES 0.** A spelling belongs to this
    level when trimming and folding it gives the label; a spelling that
    has a form holds no space, so trimming changes nothing, and folding
    an ASCII letter leaves an ASCII letter in place -- so a
    form-bearing spelling and its fold wear the same form, which is the
    label's. A label with no form of its own therefore has no
    form-bearing spelling, and a document saying otherwise describes a
    column no table can hold.

    **WHAT IS NOT CHECKED HERE, said rather than left to be noticed.**
    That the outstanding cells can be MADE UP of whole held-back groups
    is a subset-sum question, and its cost is bounded by nothing this
    document states. The generator asks it under a budget of its own
    and NAMES the shortfall where it cannot pay it exactly, which is
    what this package does with every other search.

    Raises ProfileError for a wrong type, a negative count, and for W8.
    """
    shaped = _whole(block["shape_form_cells"], "shape_form_cells", seat, 0)
    named_in_form = 0
    for spelling in sorted(variants):
        if parsing.shape_form(spelling):
            named_in_form = named_in_form + variants[spelling]
    _things, held_back_rows = _multiplicity_totals(
        [(int(key), withheld[key]) for key in sorted(withheld)]
    )
    if not parsing.shape_form(label):
        if shaped:
            raise _broken(
                "W8",
                seat,
                f"{shaped} rows are said to have written the label in a "
                "form",
                f"the label '{label}' has no written form, so no spelling "
                "of it can have one",
            )
        return shaped
    if shaped < named_in_form:
        raise _broken(
            "W8",
            seat,
            f"{shaped} rows are said to have written the label in a form",
            f"the named spellings that wear one already cover "
            f"{named_in_form}",
        )
    if shaped > named_in_form + held_back_rows:
        raise _broken(
            "W8",
            seat,
            f"{shaped} rows are said to have written the label in a form",
            (
                f"{named_in_form} named rows wear one and only the "
                f"{held_back_rows} held-back rows could join them"
            ),
        )
    return shaped


def _variants(
    block: "dict[str, object]",
    seat: str,
    floor: int,
    label: str,
    count: int,
    inside_a_half: bool = False,
) -> "tuple[dict[str, int], dict[str, int]]":
    """How the rows under one published label actually wrote it (7.4).

    Raises ProfileError for a wrong type or an out-of-range count, and
    for W2 to W5 and W7. The keys are stored EXACTLY as the file wrote
    them, before trimming and before the fold, because a variant is a
    generation input that the twin writes into a cell and must read back
    byte for byte -- unlike the spellings of an empty cell, which are
    for a person to read and are escaped for display.
    """
    keys: "tuple[str, ...]" = _THE_VARIANT_KEYS
    if inside_a_half:
        keys = _THE_COMPOUND_VARIANT_KEYS
    named = _counts(block["variants"], "variants", seat, 1, keys)
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
    # W5b, A SPELLING ONE ROW WROTE (the owner's ruling of 2026-09-17,
    # item 5; plan P4-D240). A multiplicity map keyed `1` says, in the
    # census's own definition, that a held-back spelling covered exactly
    # one row -- a count of one stated outright rather than derived, and
    # a twin then writes that row's spelling in exactly one row. The
    # producer counts such a cell into the level's commonest spelling
    # first (`taxonomy._absorb_lone_spellings`), so no description it
    # writes reaches this refusal.
    # ASKED OF THE PAIRS AND NOT OF THE KEYS, because a multiplicity
    # key is padded with zeros to the width of the largest key present:
    # `1` and `01` are the same row count written under two widths.
    lone = 0
    for rows, things in pairs:
        if rows == 1:
            lone = lone + things
    if lone:
        raise _broken(
            "W5b",
            seat,
            (
                f"{lone} spelling(s) of '{label}' are held back "
                f"as spellings ONE row wrote"
            ),
            (
                "a spelling one row wrote is a count of one, so it is "
                "counted into the label's commonest spelling instead"
            ),
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


def _spellings_spoken(
    levels: "tuple[LevelEntry, ...]",
    suppressed_levels: int,
    suppressed_rows: int,
    n_distinct: int,
    where: str,
) -> None:
    """W9: `n_distinct` is the spellings the block SPEAKS OF (plan P4-D276).

    WHAT MADE IT A RULE (the carried numbers pass of 2026-09-18). Plan
    P4-D276 made a label column's `n_distinct` count the spellings its
    block speaks of -- the spellings each published level names, after
    ruling 6 counts a spelling below the floor into the level's
    commonest, and the own spellings of every level held back -- so the
    count moved with the floor, and no rule of the loader tied it to the
    levels beside it. `tests/test_p3v5f1_floor_one.py` grafts every
    position the floor moves from a floor-eleven description into the
    floor-one description of the same table and requires the loader to
    refuse it; the level `yes` of its witness, written `yes` 67 times
    and `YES` 3 times, publishes `{"yes": 70}` and `n_distinct 2` at
    eleven and `{"YES": 3, "yes": 67}` and `n_distinct 3` at one, and
    both grafts -- `n_distinct 2` beside three named spellings, and one
    named spelling beside `n_distinct 3` with nothing held back -- were
    accepted. Each is a description whose count contradicts its own
    levels, and the twin written from it is held to both.

    THE RULE, derived from P4-D276's own statement. Let `S` be the
    spellings the published levels name -- the keys of every `variants`
    and the spellings every `variants_withheld` counts. A held-back
    level wrote at least one spelling and at most one per row, so
    `S + suppressed_levels <= n_distinct <= S + suppressed_rows`; with
    nothing held back, which is every floor-one description, the two
    ends meet and `n_distinct == S`.

    Raises ProfileError for W9. No I/O of any kind.
    """
    named = 0
    for entry in levels:
        named = named + len(entry.variants)
        for size in sorted(entry.variants_withheld):
            named = named + entry.variants_withheld[size]
    lowest = named + suppressed_levels
    highest = named + suppressed_rows
    if lowest <= n_distinct <= highest:
        return
    raise _broken(
        "W9",
        where,
        f"the column is said to hold {n_distinct} different spellings",
        (
            f"its published labels name {named}, and the "
            f"{suppressed_levels} label(s) held back cover "
            f"{suppressed_rows} row(s), so it holds between {lowest} "
            f"and {highest}"
        ),
    )


def _pooled_numbers(
    mapping: "dict[str, object]",
    where: str,
    floor: int,
    inside_a_half: bool = False,
) -> PooledNumbers:
    """The scale of the held-back numbers, read and held to B4d.

    THE DISCLOSURE QUESTION IS ASKED HERE AND NOT ASSUMED. The block
    names a group of cells and two aggregates over it, so the rule it
    has to meet is the one every census of this format meets:
    `parsing.census_nameable`, with the pooled count as the one count it
    prints and the column's numeric total as the population a reader
    subtracts it from. Both sides of that subtraction are then a group
    or nothing at all -- a pool of one cell would BE that cell's value
    written under the name `mean`, and a pool leaving one published
    numeric cell behind hands that cell over the same way.

    THE SECOND HALF OF THE RULE IS THAT SILENCE IS TOTAL. Where the
    count is nought the mean and the spread are absent, and where it is
    not they are both present; a block that spoke one of them would say
    by its shape what the count is for.

    INSIDE A COMPOUND COLUMN'S LABEL HALF the numeric total is the
    column's and counts the numbers of the OTHER half, so it is not a
    population this pool can be subtracted from and the population
    clause is not asked. The count's own line still is.

    Guarantees: accepts the block, where it stands, the floor and
    whether this is a compound column's half; returns the three values.
    Raises ProfileError for B4d, and the shape refusals for a value of
    the wrong kind. No I/O of any kind.
    """
    inner = _mapping(
        mapping["suppressed_numbers"], "suppressed_numbers", where
    )
    for key in ("n_cells", "mean", "spread"):
        if key not in inner:
            raise _missing(
                f"suppressed_numbers -> {key}",
                where,
                "every block that publishes levels",
            )
    cells = _whole(
        inner["n_cells"], "suppressed_numbers -> n_cells", where, 0
    )
    middle = _figure_or_nothing(
        inner["mean"], "suppressed_numbers -> mean", where
    )
    spread = _figure_or_nothing(
        inner["spread"], "suppressed_numbers -> spread", where
    )
    spoken = middle is not None and spread is not None
    if spoken != (cells > 0) or (middle is None) != (spread is None):
        raise _broken(
            "B4d",
            where,
            f"the pooled scale speaks of {cells} cell(s)",
            (
                "its mean and its spread are "
                + ("written" if spoken else "absent")
            ),
        )
    if spread is not None and spread < 0.0:
        raise _out_of_range(
            "suppressed_numbers -> spread",
            where,
            f"{spread}",
            "a number of 0 or more",
        )
    if cells < 1:
        return NO_POOLED_NUMBERS
    population: "list[int]" = []
    if not inside_a_half and "n_numeric" in mapping:
        total = _whole(mapping["n_numeric"], "n_numeric", where, 0)
        if cells > total:
            raise _broken(
                "B4d",
                where,
                f"the pooled scale speaks of {cells} cell(s)",
                f"the column counts only {total} number(s) in all",
            )
        population = [total]
    if not parsing.census_nameable([cells], population, floor):
        raise _broken(
            "B4d",
            where,
            f"the pooled scale speaks of {cells} cell(s)",
            (
                "that count, or what it leaves of the column's numbers, "
                f"is below the census line of {parsing.census_floor(floor)}"
            ),
        )
    return PooledNumbers(n_cells=cells, mean=middle, spread=spread)


def _label_facts(
    mapping: "dict[str, object]",
    where: str,
    role: str,
    floor: int,
    n_present: int,
    n_folded: int,
) -> LabelFacts:
    """A constant or a binary column (contract 6.4 and 6.5)."""
    entries, suppressed, rows = _levels(
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
        shape_forms=_shape_forms(mapping, where, floor),
        suppressed_numbers=_pooled_numbers(mapping, where, floor),
    )


def _compound_label_facts(
    mapping: "dict[str, object]",
    where: str,
    floor: int,
    n_present: int,
    n_folded: int,
) -> "LongTailFacts":
    """The label half of a compound column (residual R-P4-13, L8).

    THE LEVELS, THE HELD-BACK REMAINDER AND THE FORM CENSUS, read
    exactly as a label-publishing column's are -- so B2 holds here as
    it holds anywhere: what is published and what is held back are
    together all the different values, ignoring case.

    WHAT IS NOT ASKED OF IT IS ANOTHER ROLE'S ENTRY CONDITION, and that
    is the whole reason this reader exists rather than one of the two
    beside it. `_label_facts` is the CONSTANT and BINARY reader and
    demands one value or two; the long-tail reader demands a level
    covering the detection line and a count above the categorical
    ceiling. This half is neither of those columns. Rule 7b decided
    what it is -- words that repeat, in a short list or a longer one
    that comes back -- and a loader that re-asked a different rule's
    question would refuse descriptions the producer correctly wrote.

    Measured while writing it: a lab column of 295 readings beside five
    `NOT DETECTED` was refused by the binary rule for having one value
    and then by the long-tail rule for having no level on eleven rows.
    Both refusals were about roles this half does not have.
    """
    entries, suppressed, rows = _levels(
        mapping, where, floor, n_present, n_folded, True
    )
    return LongTailFacts(
        levels=entries,
        suppressed_levels=suppressed,
        suppressed_rows=rows,
        shape_forms=_shape_forms(mapping, where, floor, False, False),
        suppressed_numbers=_pooled_numbers(mapping, where, floor, True),
    )


def _long_tail_facts(
    mapping: "dict[str, object]",
    where: str,
    floor: int,
    n_present: int,
    n_folded: int,
    ceiling: int,
    code_declared: bool = False,
) -> LabelFacts:
    """A long tail of labels (plan P4-D5).

    The same four keys under the same shared label invariants a
    constant, a binary and a categorical column are held to. What it
    adds is the rule that made it this role rather than free text, and
    the loader can check it: at least one published level covers the
    detection line, which is the recorded floor or eleven, whichever is
    larger. A document whose every level falls below that line
    describes a column this rule would not have claimed.
    """
    entries, suppressed, rows = _levels(
        mapping, where, floor, n_present, n_folded
    )
    line = LONG_TAIL_LINE
    if floor > line:
        line = floor
    covering = 0
    for entry in entries:
        if entry.count >= line:
            covering = covering + 1
    # THE DECLARATION LIFTS THE LINE (plan P4-D22), and it is the ONLY
    # thing that lifts it. The line keeps a column of names or free
    # comments out of the label roles, so that lowering the floor never
    # widens which columns publish. Where the person has said `--code`
    # that judgement is theirs and is made, and holding a laboratory-code
    # column to the line is what left it publishing nothing at all.
    if covering < 1 and not code_declared:
        raise _broken(
            "LT1",
            where,
            f"the type path is '{ROLE_LONG_TAIL}'",
            (
                f"no value of it is shared by {line} rows or more, so "
                f"this rule would not have claimed the column"
            ),
        )
    # LT2. THE COLUMN HAS TO BE PAST THE CEILING TOO, and checking only
    # the line let a plain set of categories be relabelled by hand
    # (review item P4-TAIL-F3). The ceiling is recomputed from the
    # settings the document itself records, so the loader asks the
    # producer's own question rather than trusting the answer.
    if n_folded <= ceiling:
        raise _broken(
            "LT2",
            where,
            f"the type path is '{ROLE_LONG_TAIL}'",
            (
                f"the column has {n_folded} different values ignoring "
                f"case, which is within the {ceiling} a set of "
                f"categories may have, so the earlier rule would have "
                f"claimed it"
            ),
        )
    return LongTailFacts(
        levels=entries,
        suppressed_levels=suppressed,
        suppressed_rows=rows,
        shape_forms=_shape_forms(mapping, where, floor),
        suppressed_numbers=_pooled_numbers(mapping, where, floor),
    )


def _categorical_facts(
    mapping: "dict[str, object]",
    where: str,
    floor: int,
    n_present: int,
    n_folded: int,
) -> CategoricalFacts:
    """A column of categories (contract 6.6.1)."""
    entries, suppressed, rows = _levels(
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
        shape_forms=_shape_forms(mapping, where, floor),
        suppressed_numbers=_pooled_numbers(mapping, where, floor),
        level_ceiling=ceiling,
    )


def _resolution_mix(
    value: object,
    where: str,
    parser_family: str,
    parsed: int,
    floor: int,
) -> "dict[str, int]":
    """How many parsed cells wore each form (contract C6-25).

    TWO PERMITTED KEY SETS AND NO THIRD. A column read under one form
    names that form and nothing else; a column the joint ISO reading
    claimed names exactly the two members it joins. Anything else is a
    document describing a column no producer writes.

    AND NO COUNT IT PRINTS NAMES A ROW (invariant RM3, plan P4-D250).
    This docstring said the counts needed no floor, because a
    two-member space beside the published parsed total makes a pooled
    remainder recoverable by subtraction. That is true of a POOL and is
    no defence of the count itself: 118 ISO dates beside one
    `2024-07-01T00:00:00` published `{"iso-date": 118, "iso-datetime":
    1}` at a floor of eleven, and the one is that row. The producer
    counts a form below `parsing.census_floor` into the commonest form
    and publishes the column wholly in that form
    (`taxonomy._forms_as_published`), so every count reaching this
    loader is either nought -- the form no cell of the column wore,
    which names nobody -- or at the line.

    Raises ProfileError for RM1 -- the wrong key set -- for RM2, the
    total that does not come to the cells that parsed, and for RM3.
    """
    mix = _counts(value, "resolution_mix", where, 0)
    wanted: "tuple[str, ...]" = ISO_MEMBERS
    if parser_family != FORMAT_ISO_MIXED:
        wanted = (parser_family,)
    if sorted(mix) != sorted(wanted):
        raise _broken(
            "RM1",
            where,
            f"the forms it counts are {_listed(tuple(sorted(mix)))}",
            f"a column read as '{parser_family}' counts "
            f"{_listed(tuple(sorted(wanted)))}",
        )
    total = _added(mix)
    if total != parsed:
        raise _broken(
            "RM2",
            where,
            f"the values counted by their form come to {total}",
            f"{parsed} of the column's values were read as dates",
        )
    split = 0
    for key in sorted(mix):
        if mix[key] > 0:
            split = split + 1
    if split < 2:
        # ONE FORM IS NOT A CENSUS. Its count IS `n_present -
        # n_unparsed`, which the block prints two fields away, so it
        # cuts the column nowhere and names nobody however small the
        # column is -- thirteen moments at a smallest group size of
        # twenty are thirteen moments, and the document says so.
        return mix
    for key in sorted(mix):
        # NOUGHT IS NOT A GROUP AND IS NOT REFUSED either: it says no
        # cell of the column wore the form. What RM3 refuses is a form
        # some cells wore, counted by fewer of them than a published
        # count may name, beside another form that holds the rest.
        if 0 < mix[key] < parsing.census_floor(floor):
            raise _broken(
                "RM3",
                where,
                f"the form '{key}' was written by {mix[key]} of the "
                f"column's values",
                f"a published count names at least "
                f"{parsing.census_floor(floor)} of them",
            )
    return mix


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
    elif parser_family == "month-first-datetime":
        wanted = "datetime"
    elif parser_family == "day-first-datetime":
        wanted = "datetime"
    elif parser_family == "slashed-iso-datetime":
        wanted = "datetime"
    elif parser_family == FORMAT_ISO_MIXED:
        # THE JOINT READING PUBLISHES AT THE FINER OF THE TWO FORMS it
        # joins. A column holding both `2024-03-15` and
        # `2024-03-15 08:30:00` writes a time of day in some of its
        # cells, so the column reaches the second; publishing it as a
        # column of whole dates would lose every one of those times.
        # The cells that carry no time of day are placed at midnight,
        # which is what `resolution_mix` is published for -- it says
        # how many of them there were, so a reader is never left to
        # infer that all of them wrote a time (contract C6-25).
        wanted = "datetime"
    elif parser_family == "year-quarter":
        wanted = "quarter"
    elif parser_family == "iso-month":
        wanted = "month"
    if resolution != wanted:
        raise _broken(
            "D1",
            where,
            f"the dates were read as '{parser_family}'",
            f"they are published as '{resolution}' rather than '{wanted}'",
        )
    if precision == "subsecond" and parser_family in CLOCK_FORM_MEMBERS:
        raise _broken(
            "D6",
            where,
            f"the dates were read as '{parser_family}', whose clock is "
            f"a whole number of minutes or seconds",
            "the finest detail the column writes is given as a "
            "fraction of a second",
        )
    if precision == "month" and resolution != "month":
        # A WHOLE MONTH IS THE FINEST DETAIL ONLY OF A COLUMN OF
        # MONTHS, on the quarter's own precedent below. A cell written
        # `2024-03` reads back as a column of months, so a description
        # publishing that precision beside any other resolution
        # publishes two facts no file can carry at once.
        raise _broken(
            "D6",
            where,
            "the finest detail the column writes is a whole month",
            f"its dates are published as '{resolution}'",
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
    # AFTER D8, WHICH IS WHAT MAKES THE CENSUS'S KEY SET CLOSED. A
    # column where nothing read as a date would carry an empty census
    # honestly, and RM1 would then have a third permitted key set for a
    # document D8 has already refused. Asking D8 first leaves RM1 with
    # the two key sets a real producer writes and nothing else.
    mix = _resolution_mix(
        mapping["resolution_mix"],
        where,
        parser_family,
        n_present - unparsed,
        floor,
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
        if offsets[key] < parsing.census_floor(floor):
            raise _broken(
                "D3",
                where,
                f"the offset '{key}' was carried by {offsets[key]} rows",
                f"a published count names at least "
                f"{parsing.census_floor(floor)} of them",
            )
    _pool_stands_alone(offsets, "D3", where, "values' offsets")
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
    _joint_offsets_name_no_row(where, floor, mix, offsets)
    separators = _separator_census(
        mapping, where, floor, resolution, parser_family, mix,
        n_present - unparsed,
    )
    if named >= 2 and clock != "utc":
        raise _broken(
            "D5",
            where,
            f"{named} different offsets are named",
            f"the dates are published on the '{clock}' clock",
        )
    if parser_family in CLOCK_FORM_MEMBERS and clock != "local":
        # AND A COLUMN WHOSE READER TAKES NO OFFSET IS ON ONE CLOCK
        # (review item P4-DATE5-F1). D5 lets either reading stand where
        # the offset map is fully withheld, because a withheld map
        # reads the same whether one offset wrote the column or ten --
        # true of every reading that CAN carry an offset. These two
        # cannot: their own reader returns an empty offset for every
        # cell it accepts, so no column of theirs ever held two, and a
        # description claiming the shared clock states an
        # EXACT-OBSERVABLE fact no twin of it can meet.
        raise _broken(
            "D5",
            where,
            f"the dates are published on the '{clock}' clock",
            f"they were read as '{parser_family}', which reads no "
            f"offset at all, so every value of the column wore the same "
            f"one",
        )
    if parser_family in CLOCK_FORM_MEMBERS:
        # ...AND SO DOES A READING WHOSE CLOCK CARRIES NO OFFSET
        # (review item P4-DATE4-F1). These two members reach `datetime`
        # resolution, so the resolution test below lets them through;
        # their own reader takes a clock in two fixed forms and stops,
        # so a cell of theirs with `+02:00` after it reads back as no
        # date at all, exactly as a whole date with one does.
        for key in sorted(offsets):
            if key == WITHHELD or key == NO_OFFSET:
                continue
            raise _broken(
                "D9",
                where,
                f"the offset '{key}' is named",
                f"the dates were read as '{parser_family}', which reads "
                f"no offset at all",
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
    if parser_family in CLOCK_FORM_MEMBERS:
        # The two ENDPOINT offset fields, held to the same rule as the
        # map above and asked here because this is where they are read
        # (review item P4-DATE4-F1).
        for key, field in (
            (earliest_offset, "earliest_utc_offset"),
            (latest_offset, "latest_utc_offset"),
        ):
            if key == WITHHELD or key == NO_OFFSET:
                continue
            raise _broken(
                "D9",
                where,
                f"{field} names the offset '{key}'",
                f"the dates were read as '{parser_family}', which reads "
                f"no offset at all",
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
    midnight = _truth(mapping["all_at_midnight"], "all_at_midnight", where)
    if midnight:
        _stands_at_midnight(
            where, floor, resolution, clock, n_present - unparsed,
            earliest, latest, ladder, offsets, earliest_offset, latest_offset,
        )
    at_midnight = _whole_or_nothing(
        mapping["n_at_midnight"], "n_at_midnight", where
    )
    _counted_at_midnight(
        where, floor, resolution, clock, n_present - unparsed, midnight,
        at_midnight, offsets, mix,
    )
    # THE FOUR CENSUSES OF HOW THE DATES WERE WRITTEN (landing 2b.6).
    widths = _written_census(
        mapping,
        "date_field_widths",
        where,
        floor,
        _width_vocabulary(parser_family),
        parser_family in parsing.VARIABLE_WIDTH_MEMBERS
        or parser_family in parsing.TEXTUAL_MEMBERS,
        n_present - unparsed,
        "D17",
    )
    name_styles = _written_census(
        mapping,
        "month_name_styles",
        where,
        floor,
        _name_vocabulary(parser_family),
        parser_family in parsing.TEXTUAL_MEMBERS,
        n_present - unparsed,
        "D18",
    )
    markers = _written_census(
        mapping,
        "quarter_marker_case",
        where,
        floor,
        parsing.QUARTER_MARKER_CASES,
        parser_family == "year-quarter",
        n_present - unparsed,
        "D19",
    )
    zulu = _written_census(
        mapping,
        "zulu_case",
        where,
        floor,
        parsing.ZULU_CASES,
        "Z" in offsets,
        offsets["Z"] if "Z" in offsets else 0,
        "D20",
    )
    if parser_family == FORMAT_ISO_MIXED:
        # D16: A WHOLE DATE CARRIES NO OFFSET (landing 2b.3). Every
        # whole-date cell is counted under `(none)`, or pooled with it
        # under `(withheld)` where too few rows wore no offset, so a
        # description giving whole dates more than those two hold asks a
        # twin to write a whole date with an offset, which no cell can.
        without = 0
        for key in (NO_OFFSET, WITHHELD):
            if key in offsets:
                without = without + offsets[key]
        if mix["iso-date"] > without:
            raise _broken(
                "D16",
                where,
                f"{mix['iso-date']} values are counted as whole dates",
                f"only {without} values are counted with no offset",
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
        resolution_mix=mix,
        utc_offsets=offsets,
        datetime_separators=separators,
        all_at_midnight=midnight,
        n_at_midnight=at_midnight,
        date_field_widths=widths,
        month_name_styles=name_styles,
        quarter_marker_case=markers,
        zulu_case=zulu,
    )


def _joint_offsets_name_no_row(
    where: str,
    floor: int,
    mix: "dict[str, int]",
    offsets: "dict[str, int]",
) -> None:
    """D3 over the TIMESTAMPS of a joint column (round 2, item 4).

    A whole DATE carries no offset and can carry none, so on a joint
    ISO column the `(none)` key counts every date-only cell before it
    counts anything anybody wrote -- and `resolution_mix` publishes how
    many of those there are, exactly. The difference is the timestamps
    written with no offset, and D3's line over the whole key says
    nothing about it. **Measured** at a floor of eleven: 100 ISO dates,
    299 noon timestamps ending `Z` and ONE unzoned noon timestamp
    published `{"(none)": 101, "Z": 299}` beside `{"iso-date": 100,
    "iso-datetime": 300}`, and 101 less 100 is that one cell.

    The producer counts a rare offset of the timestamps into the
    commonest one they wrote (ruling 6 of 2026-09-17, decided over the
    timestamps), so its own descriptions leave this difference at
    nought or at the census line.

    THE LINE IS D3'S OWN, `parsing.census_nameable` with
    `parsing.census_floor`, because the difference is a count of that
    census and not a subtraction from some other total.

    Raises ProfileError for D3. No I/O of any kind.
    """
    if ISO_MEMBERS[0] not in mix or ISO_MEMBERS[1] not in mix:
        return
    if WITHHELD in offsets or NO_OFFSET not in offsets:
        return
    dated = mix[ISO_MEMBERS[0]]
    unzoned = offsets[NO_OFFSET]
    rest = unzoned - dated
    if dated <= 0 or rest <= 0:
        return
    if parsing.census_nameable([], [rest], floor):
        return
    raise _broken(
        "D3",
        where,
        (
            f"{unzoned} values carry no offset while {dated} of the "
            f"column's values are whole dates, which carry none"
        ),
        (
            f"the {rest} timestamp(s) written with no offset are a group "
            f"smaller than {parsing.census_floor(floor)}"
        ),
    )


def _counted_at_midnight(
    where: str,
    floor: int,
    resolution: str,
    clock: str,
    parsed: int,
    midnight: bool,
    counted: "int | None",
    offsets: "dict[str, int]",
    mix: "dict[str, int] | None" = None,
) -> None:
    """D15: the count of values at midnight is one a producer can write.

    ABSENT NAMES NOTHING, and nought is not a value this field takes at
    all (landing 2b.6). Otherwise it is at most the parsed cells, at
    least the floor, and either every parsed cell or leaves at least the
    floor off midnight, so neither side of the count is a group smaller
    than the floor. It is every parsed cell EXACTLY where the column is
    said to stand at midnight, which is how the statement and the count
    cannot disagree; below the floor both are empty, so the statement's
    own floor is not contradicted. And like the statement it is refused
    on a column that writes no clock, or on the shared clock where an
    offset is held back.

    THE FLOOR HERE IS NEVER BELOW TWO, whatever the run's own smallest
    group size is (`parsing.MIDNIGHT_DISCLOSURE_FLOOR`), because one is
    not a group: a count of one names the person who holds the value and
    a count one short of every value names the person who does not.
    Measured on 400 moments a day apart at noon, described once as they
    stood and once with a single row moved to midnight -- the two
    documents differed in `n_at_midnight: 0 -> 1` and in nothing else
    anywhere, so the difference WAS that person's time of day. Both
    publish no count now, which is why nought had to stop being this
    field's word for silence: a silence a reader can tell from a real
    nought is not silence.

    Guarantees: accepts the facts already read; returns nothing. Raises
    ProfileError for D15. No I/O of any kind.
    """
    least = parsing.census_floor(floor)
    if counted is None:
        if midnight:
            raise _broken(
                "D15",
                where,
                "no count of the values at midnight is published",
                "every value is said to stand at midnight",
            )
        return
    if resolution != "datetime":
        raise _broken(
            "D15",
            where,
            f"{counted} values are counted at midnight",
            f"the dates are published at '{resolution}', which writes no clock",
        )
    if clock != "local" and WITHHELD in offsets:
        raise _broken(
            "D15",
            where,
            f"{counted} values are counted at midnight",
            "the dates are on the shared clock and an offset is held back",
        )
    if counted > parsed:
        raise _broken(
            "D15",
            where,
            f"{counted} values are counted at midnight",
            f"{parsed} of the column's values were read as dates",
        )
    if counted < least:
        raise _broken(
            "D15",
            where,
            f"{counted} values are counted at midnight",
            f"a published count names at least {least} of them",
        )
    if counted < parsed and parsed - counted < least:
        raise _broken(
            "D15",
            where,
            f"{parsed - counted} values are counted off midnight",
            f"a published count leaves at least {least} of them",
        )
    if (counted == parsed) != midnight:
        raise _broken(
            "D15",
            where,
            f"{counted} of {parsed} values are counted at midnight",
            "the column is said to stand at midnight"
            if midnight
            else "the column is said not to stand wholly at midnight",
        )
    # ...AND ON A JOINT COLUMN THE DATES COME OUT FIRST (round 2 of the
    # review, the disclosure pass, item 4). A whole date of such a
    # column stands at midnight by definition and `resolution_mix`
    # counts them exactly, so this count less that one is the
    # TIMESTAMPS at midnight, and the floor above is about the whole
    # column rather than about them. **Measured** at a floor of eleven:
    # 100 ISO dates, 299 timestamps at noon and one at midnight
    # published `n_at_midnight` 101 beside `{"iso-date": 100,
    # "iso-datetime": 300}`, and 101 less 100 is that person's time of
    # day. The producer publishes no count at all in that case, which
    # is this field's one silence.
    if mix is None or ISO_MEMBERS[0] not in mix or ISO_MEMBERS[1] not in mix:
        return
    dated = mix[ISO_MEMBERS[0]]
    stamped = mix[ISO_MEMBERS[1]]
    at_midnight = counted - dated
    if dated <= 0 or at_midnight <= 0 or at_midnight == stamped:
        return
    if at_midnight >= least and stamped - at_midnight >= least:
        return
    raise _broken(
        "D15",
        where,
        (
            f"{counted} values are counted at midnight while {dated} of "
            f"the column's values are whole dates, which stand there"
        ),
        (
            f"that leaves {at_midnight} of the {stamped} timestamp(s) at "
            f"midnight, and a published count names at least {least} of "
            f"them and leaves at least {least}"
        ),
    )


def _width_vocabulary(parser_family: str) -> "tuple[str, ...]":
    """Which width words this member's own cells can show (landing 2b.6).

    A textual member writes the month as a NAME, so its one numeric
    field is the day and there is no second field for `first-padded` or
    `second-padded` to be about.
    """
    if parser_family in parsing.TEXTUAL_MEMBERS:
        return parsing.FIELD_WIDTH_STYLES_ONE_FIELD
    return parsing.FIELD_WIDTH_STYLES


def _name_vocabulary(parser_family: str) -> "tuple[str, ...]":
    """Which month-name styles this member's own cells can show (2b.6).

    The day-first textual member writes no comma: a comma there would
    follow a month name, which `_textual_fields` refuses, so half the
    joint vocabulary is unreachable and a document naming one of those
    styles describes a column no producer wrote.
    """
    if parser_family == "textual-day-first-date":
        return parsing.MONTH_NAME_STYLES_NO_COMMA
    return parsing.MONTH_NAME_STYLES


def midnight_withheld_for_its_size(facts: "DatetimeFacts") -> bool:
    """Whether `n_at_midnight` is withheld because a side was too small.

    THE ONE READING OF A WITHHELD COUNT (plan P4-D191), asked by the
    generator and the validator alike. The describing step withholds the
    count for FOUR reasons (`taxonomy._midnight_count`): the column is
    not one of moments; it is read on the shared clock with its offsets
    pooled; the joint reading's TIMESTAMP residual names a row; or too
    few moments stood at midnight, or too few did not. A column wholly
    at midnight publishes `all_at_midnight` instead. Only the last says
    anything about a file's own count: fewer than the line at midnight,
    or fewer than the line off it.

    A JOINT COLUMN OWES NOTHING HERE, AND THAT IS WHAT THE FOURTH REASON
    COSTS (round 2 of the review, the disclosure pass; the repair pass
    of this landing). `taxonomy._joint_midnight_nameable` withholds the
    count of a column holding whole dates and moments together where the
    timestamps' own residual would name one person's time of day --
    and nothing in the LOADED facts can tell that silence from the
    older one, because the residual is exactly what the withheld count
    would have supplied. The two readings are indistinguishable to this
    function by construction, so a joint column is owed neither.

    **Measured** before the guard, on the disclosure pass's own item-4
    input at the DEFAULT floor of one -- 100 ISO dates, 299 timestamps
    at noon and one at midnight: `synthtwin generate` wrote a twin and
    `synthtwin validate` then exited 3 on `midnight.withheld
    [datetime.n_at_midnight]: MISSED`, on every seed tried and at floors
    two and five as well. The generator cannot meet the obligation on
    this shape whatever it does: by `_ordinals_off_midnight`'s own
    statement "a bare-date rank of an `iso-mixed` column is left as it
    is", so the hundred whole dates stand at midnight and no rank shift
    can bring that side under the line. After the guard: no rank is
    shifted, no deviation is noted, the validator LISTS the field
    instead of checking it, and the twin and the real file both exit 0
    while `n_at_midnight` stays silent.

    `resolution_mix` is the one fact that says which reading a column
    was given: a single-format column carries one key, and only the
    joint reading carries two (`taxonomy._resolution_mix`).

    Guarantees: accepts loaded datetime facts; returns a bool. A function
    of the facts. Raises nothing. No I/O of any kind.
    """
    if facts.resolution != "datetime" or facts.n_at_midnight is not None:
        return False
    if facts.all_at_midnight:
        return False
    if len(facts.resolution_mix) > 1:
        return False
    return not (facts.datetimes_read_at != "local" and WITHHELD in facts.utc_offsets)


def datetime_counts_reachable(column: "ColumnBlock") -> bool:
    """Whether method G7.3's count pass reaches a date column's distinct count.

    THE ONE STATEMENT OF WHERE THE CONSTRUCTION REACHES IT (plan
    P4-D192), asked by the generator's pass and report and by the
    validator alike. The pass counts different written UNITS -- days, or
    minutes or seconds at the column's precision -- so it reaches the
    count of different cells only where one instant is written one way:
    read on the column's own clock; at `date` or `datetime` resolution;
    carrying no offset at all and no pooled offset; writing at most one
    mark between day and clock and pooling none; each census of written
    forms naming at most one form; writing no bare date beside moments;
    and publishing the same count folded as raw.

    Guarantees: accepts a loaded column block; returns False for any
    column not of dates. A function of the block. Raises nothing. No I/O
    of any kind.
    """
    facts = column.facts
    if not isinstance(facts, (DatetimeFacts,)):
        return False
    if facts.datetimes_read_at != "local":
        return False
    if facts.resolution not in ("date", "datetime"):
        return False
    for key in facts.utc_offsets:
        if key != NO_OFFSET:
            return False
    if WITHHELD in facts.datetime_separators or len(facts.datetime_separators) > 1:
        return False
    for census in (
        facts.date_field_widths,
        facts.month_name_styles,
        facts.quarter_marker_case,
        facts.zulu_case,
    ):
        if len(census) > 1:
            return False
    if facts.parser_family == FORMAT_ISO_MIXED and (
        "iso-date" in facts.resolution_mix and facts.resolution_mix["iso-date"] > 0
    ):
        return False
    return column.n_distinct == column.n_distinct_folded


def written_forms_of_an_instant(facts: "DatetimeFacts") -> int:
    """How many written forms one instant of this column can take (P4-D137).

    The product, over the four censuses of how the dates were written, of
    how many forms each names -- one where it names none. One value is
    written in one form per census, and a twin spreads each census's named
    forms over its cells, so one day of a month-first column can come back
    `3/5/2024` and `03/05/2024`, and one quarter `2024-Q1` and `2024-q1`:
    two different cells a count of distinct values counts twice. The
    generator's report (method G12.5) and the validator both multiply the
    ways an instant is written by this, because a bound that leaves it out
    calls a faithful twin of a mixed column MISSED: 300 quarters over twelve
    years, a quarter of them written `q`, publish 81 different values
    against an upper end of 48, and both the table and its twin were told
    so.

    Guarantees: accepts loaded datetime facts; returns a whole number of
    at least one. Determinism: a function of the facts. Raises nothing.
    No I/O of any kind.
    """
    forms = 1
    for census in (
        facts.date_field_widths,
        facts.month_name_styles,
        facts.quarter_marker_case,
        facts.zulu_case,
    ):
        forms = forms * max(1, len(census))
    return forms


def _written_census(
    mapping: "dict[str, object]",
    key: str,
    where: str,
    floor: int,
    permitted: "tuple[str, ...]",
    reachable: bool,
    most: int,
    rule: str,
) -> "dict[str, int]":
    """One census of HOW a column's dates were written (landing 2b.6).

    The four censuses that reverse owner decision 5 are held by one rule
    each, and this is the shape of all four -- written once, because four
    copies of a floor rule are four things to keep in step. In order: a
    key outside the member's own vocabulary is refused, and `(withheld)`
    is outside every one of them; every named count reaches the floor
    and never falls below two, since a form held by one row describes how
    that row was written; a member that cannot show the convention at all
    carries an empty census; the total is at most the cells that could
    carry one; and what the named counts leave over of that published
    total is none or reaches the same line (plan P4-D131). The last three
    are `parsing.census_nameable`, the one disclosure rule the producer
    asks too, asked here rather than written a second time.

    WHY NO POOL, AND WHY THE REMAINDER (review of 158c811, item 1). The
    pool used to be bounded as D12 bounds the marks' pool, and that bound
    let a census of two forms publish `{"upper": 399, "(withheld)": 1}`:
    with one form left the pool is that form's count, so the loader
    accepted a description naming the one row that wrote a lower-case
    `z`. And where no pool is written, the published total less the named
    counts is the same count by subtraction.

    THE TOTAL IS A CEILING AND NOT AN EQUALITY, and that is a real
    difference from D13 rather than a looser copy of it. Whether a cell
    can SHOW a convention depends on its own value -- a day above the
    ninth shows no width, a month of May shows no name length -- so the
    number of cells that could carry one is a fact about the values, and
    a twin whose values differ by a day carries a different number of
    them. What the twin is held to is the SET of conventions and each
    one's floor, which is what `_written_form_checks` measures.

    AND THE WIDTHS' REMAINDER IS PUBLISHED AFTER ALL (plan P4-D278,
    reversing P4-D139's half of this). The remainder used to be counted
    against the cells that COULD show a width, which no field of the
    block states -- but a reader holds the PARSED total and subtracts
    from that, and 399 dates written `1/1/2000` through `1/9/2044`
    beside one `12/25/2020` published `{"unpadded": 399}` against 400
    parsed cells. The producer counts a cell that could show no width
    into the commonest width, which is true of it because both
    conventions spell it the same way, so the census reaches the parsed
    total whenever it names anything and this rule is asked of it like
    the other three.

    Guarantees: accepts the datetime block, the census's key, where it
    stands, the floor, the member's vocabulary, whether the member can
    show the convention, the ceiling on the total and the invariant's
    name; returns the census. Raises ProfileError for a key outside the
    vocabulary and for the named invariant. No I/O of any kind.
    """
    value: object = mapping[key] if key in mapping else {}
    census = _counts(value, key, where, 1)
    line = parsing.census_floor(floor)
    for name in sorted(census):
        if name not in permitted:
            raise _out_of_range(
                f"{key} -> {name}",
                where,
                f"'{name}'",
                _listed(permitted),
            )
        if census[name] < line:
            raise _broken(
                rule,
                where,
                f"the written form '{name}' was used by {census[name]} rows",
                f"a published count names at least {line} of them",
            )
    total = _added(census)
    if not reachable:
        if total != 0:
            raise _broken(
                rule,
                where,
                f"{total} values are counted by how they wrote this form",
                "no cell of this column's dates can show it",
            )
        return census
    if total > most:
        raise _broken(
            rule,
            where,
            f"the counted written forms come to {total}",
            f"at most {most} of the column's values could show one",
        )
    if total and not parsing.census_nameable(
        [census[name] for name in sorted(census)], [most], floor
    ):
        raise _broken(
            rule,
            where,
            f"the counted written forms leave {most - total} of {most} "
            f"values over",
            f"what a census leaves over is none or at least {line}",
        )
    return census


def _pool_stands_alone(
    census: "dict[str, int]", rule: str, where: str, what: str
) -> None:
    """D3, P6, P5, P5b and P6c: no pool beside a named count (plan P4-D222).

    The older spelling censuses count a name below `parsing.census_floor`
    into the commonest named count (`parsing.absorbed_census`), so a pool
    stands only where the census names nothing, and its one count is the
    total the block already publishes. A pool beside a named count is a
    count a reader subtracts, and on the branch this repairs a pool at
    the line beside named forms gave back exact counts of one: 7, +8, 09,
    1.5e3 and 2.5E3 among 995 prices at a floor of one published
    `{"decimal": 995, "(withheld)": 5}`, five forms of one cell each.

    Guarantees: accepts a loaded census, the invariant's name, where it
    stands and the words for what the pool holds; returns nothing. Raises
    ProfileError for the named invariant. No I/O of any kind.
    """
    if WITHHELD not in census or len(census) == 1:
        return
    raise _broken(
        rule,
        where,
        f"{census[WITHHELD]} {what} are held back beside a named count",
        "a census holds its counts back only all together",
    )


def _census_may_speak(
    census: "dict[str, int]",
    rule: str,
    where: str,
    floor: int,
    names: int,
    what: str,
) -> None:
    """D12 and P6: a closed census pools only where a pool names no one (P4-D222).

    `parsing.census_pools`, the one statement: on a closed vocabulary a
    pool over more cells than all but one name can hold below the line
    would say every name was written, so the producer never writes one.

    Raises ProfileError for the named invariant. No I/O of any kind.
    """
    if WITHHELD not in census or len(census) != 1:
        return
    total = census[WITHHELD]
    if not parsing.census_pools(total, floor, names):
        raise _broken(
            rule,
            where,
            f"all {total} {what} are held back",
            f"over {total} of them a census names its commonest one "
            f"(the line is {parsing.census_floor(floor)})",
        )


def _separator_census(
    mapping: "dict[str, object]",
    where: str,
    floor: int,
    resolution: str,
    parser_family: str,
    mix: "dict[str, int]",
    parsed: int,
) -> "dict[str, int]":
    """D12 and D13: the census of marks between a moment's day and clock.

    Asked after the form census, because the total an `iso-mixed` column
    owes is that census's count of the cells that wrote a clock.

    Guarantees: accepts the datetime block and the facts already read
    from it; returns the census. Raises ProfileError for a name outside the
    vocabulary, for D12 and for D13. No I/O of any kind.
    """
    census = _counts(
        mapping["datetime_separators"], "datetime_separators", where, 1
    )
    for key in sorted(census):
        if key == WITHHELD:
            continue
        if key not in parsing.DATETIME_SEPARATORS:
            raise _out_of_range(
                f"datetime_separators -> {key}",
                where,
                f"'{key}'",
                "'upper_t', 'space', 'lower_t', or '(withheld)'",
            )
        if census[key] < parsing.census_floor(floor):
            raise _broken(
                "D12",
                where,
                f"the mark '{key}' was written by {census[key]} rows",
                f"a published count names at least "
                f"{parsing.census_floor(floor)} of them",
            )
        if WITHHELD in census:
            # A POOL OF MARKS IS THE WHOLE CENSUS (plan P4-D220). The
            # marks are a closed vocabulary, so a pool beside a named
            # mark covers at most two others, each held by fewer rows
            # than the line: below the line the pool is a count too small
            # to print, and at the line or above it says that neither
            # mark is nought -- which tells the state nought reaches from
            # the state a count below the floor reaches. The bound this
            # replaces, (floor - 1) times the unnamed marks, admitted
            # both.
            raise _broken(
                "D12",
                where,
                f"{census[WITHHELD]} values' marks are held back beside "
                f"the mark '{key}'",
                "a census of marks names every mark or holds all of them back",
            )
    _census_may_speak(
        census,
        "D12",
        where,
        floor,
        parsing.separator_names(parser_family),
        "values' marks",
    )
    total = _added(census)
    if resolution != "datetime":
        if total != 0:
            raise _broken(
                "D13",
                where,
                f"{total} values are counted by the mark before their clock",
                f"a column published at '{resolution}' writes no clock",
            )
        return census
    owed = parsed
    if parser_family == FORMAT_ISO_MIXED:
        owed = mix["iso-datetime"]
    if total != owed:
        raise _broken(
            "D13",
            where,
            f"the counted marks before the clock come to {total}",
            f"{owed} of the column's values write a clock",
        )
    if parser_family in CLOCK_FORM_MEMBERS:
        for key in sorted(census):
            if key == WITHHELD or key == parsing.SEPARATOR_SPACE:
                continue
            raise _broken(
                "D13",
                where,
                f"the mark '{key}' is counted",
                f"a column read as '{parser_family}' separates its day "
                f"and its clock with a space",
            )
    return census


def _stands_at_midnight(
    where: str,
    floor: int,
    resolution: str,
    clock: str,
    parsed: int,
    earliest: str,
    latest: str,
    ladder: DateLadder,
    offsets: "dict[str, int]",
    earliest_offset: str,
    latest_offset: str,
) -> None:
    """D14: a column said to stand at midnight can be one.

    One direction only. The canonical form drops a fraction of a second,
    so a published moment of `00:00:00` cannot show that the cell behind
    it wrote no fraction; what a loader CAN refuse is a description whose
    own published moments, clock or size contradict the statement.

    ON THE SHARED CLOCK TOO (landing 2b.3). A published instant is then a
    moment on the shared clock, and it stands at midnight of its own day
    where some offset the map names moves it there -- `2024-03-09
    23:00:00` under `+01:00`; each END under the offset published for
    that end. A map holding an offset back is refused, because a pooled
    offset is written with none and no midnight of it can be written.

    Guarantees: accepts the facts already read; returns nothing. Raises
    ProfileError for D14. No I/O of any kind.
    """
    if resolution != "datetime" or (clock != "local" and WITHHELD in offsets):
        raise _broken(
            "D14",
            where,
            "every value is said to stand at midnight",
            f"the dates are published at '{resolution}' on the '{clock}' "
            f"clock",
        )
    least = floor
    if least < parsing.MIDNIGHT_DISCLOSURE_FLOOR:
        # THE SAME FLOOR THE COUNT IS HELD TO (landing 2b.6). Saying
        # "every value" of a column of one value is a count of one said
        # in words, and D15 would refuse the count beside it, so the two
        # are held to one number rather than left to contradict.
        least = parsing.MIDNIGHT_DISCLOSURE_FLOOR
    if parsed < least:
        raise _broken(
            "D14",
            where,
            f"all {parsed} values are said to stand at midnight",
            f"a column saying so holds at least {least} of them",
        )
    for moment, offset in ((earliest, earliest_offset), (latest, latest_offset)):
        keys: "tuple[str, ...]" = (offset,)
        if clock == "local":
            keys = (NO_OFFSET,)
        if not _local_midnight_under(moment, keys):
            raise _broken(
                "D14",
                where,
                f"the column's value {moment} is published",
                "every value is said to stand at midnight",
            )
    named: "tuple[str, ...]" = (NO_OFFSET,)
    if clock != "local":
        named = tuple(sorted(offsets))
    for rung in ladder.rungs:
        if not _local_midnight_under(rung, named):
            raise _broken(
                "D14",
                where,
                f"the ladder of dates holds {rung}",
                "every value is said to stand at midnight",
            )


def _local_midnight_under(moment: str, offsets: "tuple[str, ...]") -> bool:
    """Whether a published moment is a midnight under one of these offsets.

    Each offset moves the moment onto its own wall clock, and the moment
    stands at midnight where that clock reads `00:00:00`; the two marker
    keys move it by nothing. Whole-number arithmetic only.
    """
    if len(moment) < 19:
        return False
    seconds = _minute_of(moment) + int(moment[17:19])
    for offset in offsets:
        if (seconds + _offset_seconds(offset)) % 86400 == 0:
            return True
    return False


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


# EXACTLY THE KEYS ONE WRAPPER OF A SET CARRIES, AND NO OTHERS (plan
# P4-D37). Without this an entry carried whatever a file put in it, and
# the compound role's own sub-blocks were found holding text nothing in
# this package ever reads.
# The four class keys in the order AF4 and AF16 read them.
_CORE_CLASS_KEYS = (
    "n_core_numeric",
    "n_core_out_of_range",
    "n_core_contradictory",
    "n_core_not_numeric",
)

_WRAPPER_KEYS = (
    "prefix",
    "suffix",
    "count",
    "n_core_numeric",
    "n_core_out_of_range",
    "n_core_contradictory",
    "n_core_not_numeric",
    "n_core_distinct",
    "n_core_distinct_folded",
    "numbers",
)


def _affix_variants(
    mapping: "dict[str, object]",
    where: str,
    frame: "_Frame",
) -> "tuple[AffixWrapper, ...]":
    """The other wrappers a column of this role wears (AF9, P4-D36).

    A column wears ONE wrapper on most tables and a small SET of them
    on some that matter: a laboratory column whose readings carry an
    abnormal flag wears three, and one recorded in two units wears
    two. Each entry names a wrapper and how many cells wear it.

    AF9, in four conditions:

    1. Each count is at least the smallest group size. A wrapper is
       PUBLISHED text, so one worn by fewer cells than may be named is
       not published at all and its cells are stragglers.
    2. No wrapper appears twice, and none of them is the pair the
       block names. Two entries for one wrapper are two counts of one
       thing.
    3. The entries ascend by their own text, so a producer writes them
       one way and two producers write them the same way.
    4. They are read before AF1, because AF1 is stated over the whole
       set: the bare wrapper is a member of a vocabulary even though it
       cannot be the whole of one.

    Guarantees: accepts the block, its place and the frame; returns the
    wrappers in the order the file states them. Determinism: a function
    of those inputs. Raises `ProfileError` on a description no column
    could have. No I/O of any kind.
    """
    given = mapping["affix_variants"]
    if not isinstance(given, list):
        raise _wrong_type(
            "affix_variants", where, given, "a list of wrappers"
        )
    found: "list[AffixWrapper]" = []
    last: "tuple[str, str] | None" = None
    for entry in given:
        if not isinstance(entry, dict):
            raise _wrong_type(
                "affix_variants", where, entry,
                "a wrapper with its two sides and its count",
            )
        for key in (
            "prefix",
            "suffix",
            "count",
            # ...AND ITS OWN FOUR CLASSES AND ITS OWN NUMBERS (plan
            # P4-D37). A wrapper with no block is a wrapper whose cells
            # nothing describes, which is the state this ruling ended.
            "n_core_numeric",
            "n_core_out_of_range",
            "n_core_contradictory",
            "n_core_not_numeric",
            "n_core_distinct",
            "n_core_distinct_folded",
            "numbers",
        ):
            if key not in entry:
                raise _wrong_type(
                    "affix_variants", where, entry,
                    f"a wrapper carrying {key}",
                )
        for key in entry:
            if key not in _WRAPPER_KEYS:
                raise _wrong_type(
                    "affix_variants", where, entry,
                    "a wrapper carrying only the keys this format "
                    "gives one",
                )
        prefix = _text(entry["prefix"], "affix_variants", where)
        suffix = _text(entry["suffix"], "affix_variants", where)
        count = _bounded(
            entry["count"], "affix_variants", where,
            frame.floor, frame.n_rows,
            "the number of rows the table has",
        )
        pair = (prefix, suffix)
        if last is not None and not last < pair:
            raise _out_of_range(
                "affix_variants", where,
                f"the wrapper {prefix!r}/{suffix!r} after "
                f"{last[0]!r}/{last[1]!r}",
                "the wrappers ascending, each named once",
            )
        last = pair
        # AF11. THE WRAPPER'S FOUR CLASSES CLOSE ON ITS OWN COUNT,
        # exactly as AF4 closes the column's four on `n_affixed`. A set
        # of four that closes on something else describes a wrapper
        # whose cells are in no class or in two.
        classes: "list[int]" = []
        for key in (
            "n_core_numeric",
            "n_core_out_of_range",
            "n_core_contradictory",
            "n_core_not_numeric",
        ):
            classes += [
                _bounded(
                    entry[key], key, where, 0, count,
                    "the number of cells wearing this wrapper",
                )
            ]
        total = classes[0] + classes[1] + classes[2] + classes[3]
        if total != count:
            raise _out_of_range(
                "affix_variants", where, f"a total of {total}",
                f"a total of {count}, the number of cells wearing the "
                f"wrapper {prefix!r}/{suffix!r}",
            )
        # AF13. A WRAPPER CANNOT HOLD MORE DIFFERENT CORES THAN IT HAS
        # CELLS, and folding never separates two spellings that were
        # the same.
        # AT LEAST ONE, exactly as AF10 asks of the column's own pair
        # (review round 4, item 2). The bound here was zero while the
        # column's was one, so a description saying a wrapper worn by
        # sixty cells holds no different core at all loaded, and
        # generation then built 236 identities inside an interval it
        # reported as 0 to 236.
        wrapper_distinct = _bounded(
            entry["n_core_distinct"], "n_core_distinct", where,
            1, count, "the number of cells wearing this wrapper",
        )
        wrapper_folded = _bounded(
            entry["n_core_distinct_folded"], "n_core_distinct_folded",
            where, 1, wrapper_distinct,
            "the raw count of different cores under this wrapper",
        )
        block = _mapping(entry["numbers"], "numbers", where)
        _keys(
            block, where, NUMERIC_KEYS,
            f"the block for the wrapper {prefix!r}/{suffix!r}",
        )
        found += [
            AffixWrapper(
                prefix=prefix,
                suffix=suffix,
                count=count,
                n_core_numeric=classes[0],
                n_core_out_of_range=classes[1],
                n_core_contradictory=classes[2],
                n_core_not_numeric=classes[3],
                n_core_distinct=wrapper_distinct,
                n_core_distinct_folded=wrapper_folded,
                numbers=_numeric_facts(
                    block,
                    f"{where}, the wrapper {prefix!r}/{suffix!r}",
                    frame,
                    count,
                    classes[0],
                    classes[1],
                    classes[2],
                    # THE ROW COUNT A WRAPPER'S BLOCK ECHOES IS ITS OWN
                    # COUNT, on the joined role's precedent: a block
                    # describing a SUBSET of the column's cells echoes
                    # the count of that subset.
                    echoes=count,
                ),
            )
        ]
    return tuple(found)


def _numeric_facts(
    mapping: "dict[str, object]",
    where: str,
    frame: _Frame,
    n_present: int,
    n_numeric: int,
    n_out_of_range: int,
    n_contradictory: int,
    echoes: "int | None" = None,
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
    finer = _finer_ladder(
        mapping["percentiles_between"], "percentiles_between", where, ladder
    )
    mean = _figure_or_nothing(mapping["mean"], "mean", where)
    std = _figure_or_nothing(mapping["std"], "std", where)
    skew = _figure_or_nothing(mapping["skew"], "skew", where)
    kurtosis = _figure_or_nothing(mapping["kurtosis"], "kurtosis", where)
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
    # WHICH ROW COUNT A BLOCK OF NUMBERS ECHOES. For a column it is the
    # table's, which is what Q1 says. For one POSITION of a joined
    # column it is not: that block describes only the cells that split,
    # so the profiler writes `n_joined` there and every other count in
    # the block is measured over those same cells.
    #
    # Comparing a position against the TABLE's row count made the tool
    # write a file it then refused to read. Measured: a 200-row column
    # of joined readings with ONE cell that does not split is published
    # with `n_joined` 199, and `load_profile` raised Q1 against it --
    # telling the user the file "has been changed since it was written"
    # and to make it again, which produces the same file. Every joined
    # column carrying any unparsed cell was unreadable this way; with
    # none, the two counts coincide and nothing showed.
    wanted = frame.n_rows if echoes is None else echoes
    if echoed != wanted:
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
    # INVARIANT Q16, the kurtosis's own, and it is the shape of Q5 one
    # moment further along. A column whose values are all one value has
    # no tails to weigh; a column of four or more values that are not
    # all one has tails, and leaving the weight out is a description
    # holding something back that it measured.
    if flat and kurtosis is not None:
        raise _broken(
            "Q16",
            where,
            f"the weight of the tails is given as {kurtosis}",
            "every value the statistics used is the same",
        )
    # AND BELOW FOUR VALUES IT IS NOT THERE AT ALL (item P4-K-R1-F3).
    # Q16 refused a MISSING weight at four values and up, and never
    # refused a PRESENT one below four -- so a description could carry
    # a tail weight for three values, which the producer never writes
    # and which no three points can support.
    if not flat and used < 4 and kurtosis is not None:
        raise _broken(
            "Q16",
            where,
            f"the weight of the tails is given as {kurtosis}",
            (
                f"the statistics used {used} value(s), and a fourth "
                f"moment asks for four"
            ),
        )
    if not flat and used >= 4 and kurtosis is None:
        raise _broken(
            "Q16",
            where,
            "the weight of the tails is left out",
            (
                f"the statistics used {used} values and they are not all "
                f"the same"
            ),
        )
    # AND IT LIES WHERE EVERY SAMPLE OF THAT SIZE MUST. The moment
    # ratio of `n` values is at least 1 and at most `n - 2 + 1/(n - 1)`,
    # whatever the values are -- the upper end reached exactly when one
    # value stands apart from `n - 1` equal ones. A number outside that
    # is not a kurtosis of this column at any spelling.
    if kurtosis is not None and used >= 4:
        ceiling = used - 2 + 1 / (used - 1)
        if kurtosis < 1.0 or kurtosis > ceiling:
            raise _broken(
                "Q16",
                where,
                f"the weight of the tails is given as {kurtosis}",
                (
                    f"a weight between 1 and {ceiling}, which is where "
                    f"every {used}-value sample lies"
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
    mark = _group_separator(mapping, where)
    negative = _negative_form(mapping, where)
    wide = _wide_runs(mapping, where)
    # INVARIANT WR1 (landing 2b.13, plan P4-D90; the floor and the
    # second form added by its repair pass, plan P4-D91; the THIRD form
    # by landing 2b.16 part 2, plan P4-D107), the room the forms map
    # leaves. A wide run is a cell written point-free, and all THREE
    # point-free forms are point-free: plain, a leading plus, and a
    # padded cell whose pad the producer reads off before it asks
    # whether the run is its own value's text. So a column saying
    # anything but `none` about its wide runs claims at least the
    # smallest group size of them among those three, and where such a
    # form was pooled the pool is where they would be. Read the same way
    # DP1 reads the room for a signed decimal, and floored the way NS1
    # floors the notation beside it: the word names the FORM of the
    # cells it is about, so a description naming it for fewer cells than
    # the floor would say what the forms map pooled them to avoid
    # saying. Measured before the third form was counted here: a column
    # of 800 padded wide keys publishing `canonical` was refused by this
    # loader on room of nought, so the description its own producer
    # writes could not be read back.
    if wide != parsing.WIDE_NONE:
        point_free_room = 0
        if parsing.STYLE_PLAIN in styles:
            point_free_room = point_free_room + styles[parsing.STYLE_PLAIN]
        if parsing.STYLE_LEADING_PLUS in styles:
            point_free_room = point_free_room + styles[parsing.STYLE_LEADING_PLUS]
        if parsing.STYLE_LEADING_ZERO in styles:
            point_free_room = point_free_room + styles[parsing.STYLE_LEADING_ZERO]
        if WITHHELD in styles:
            point_free_room = point_free_room + styles[WITHHELD]
        if point_free_room < 1 or point_free_room < frame.floor:
            raise _broken(
                "WR1",
                where,
                f"the wide runs of figures are said to be '{wide}'",
                f"the forms map leaves room for {point_free_room} point-free "
                f"cell(s) and the smallest group size is {frame.floor}",
            )
    # INVARIANT NS1 (landing 2b.2). A notation is a majority of the
    # negative cells that reached the floor, so a column naming one holds
    # at least that many negatives -- and at least one, whatever the floor.
    if negative != parsing.NEGATIVE_MINUS and (
        n_negative < 1 or n_negative < frame.floor
    ):
        raise _broken(
            "NS1",
            where,
            f"the negatives are said to be written as '{negative}'",
            f"{n_negative} values are negative",
        )
    # THE TWO MIXTURE CENSUSES, READ BESIDE THE MAJORITY KEYS THEY
    # QUALIFY (landing 2b.7, plan P4-D65.2). The mark census is read
    # against the published mark, so a description whose majority no
    # cell proved is refused here rather than at the twin.
    notations = _negative_notations(
        mapping,
        where,
        frame.floor,
        n_negative,
        n_negative - n_negative_unrepresentable,
    )
    marks = _thousands_marks(mapping, where, frame.floor, n_numeric)
    plus = _decimal_plus(mapping, where, frame.floor)
    # INVARIANT DP1 (landing 2b.2), the floor and the room. The census is
    # published under the floor like every form count, and it counts
    # cells the forms map files under `decimal` -- which, where that
    # form was pooled, is at most the pool.
    room = 0
    if "decimal" in styles:
        room = room + styles["decimal"]
    if "(withheld)" in styles:
        room = room + styles["(withheld)"]
    signed = _added(plus)
    if signed > room:
        raise _broken(
            "DP1",
            where,
            f"{signed} numbers are written with a point and a plus",
            f"the forms map leaves room for {room}",
        )
    # ...AND ITS COMPLEMENT (plan P4-D140). Where the forms map names the
    # `decimal` count, a reader takes the signed count from it, so what is
    # left -- the decimals WITHOUT a plus -- is nought or a group, by the
    # one statement of the disclosure rule the producer reads.
    # ...AND OVER THE SECOND POPULATION THE READER DERIVES (round 2 of
    # the review, the disclosure pass, item 5). A negative cell is
    # written with a minus and never with a plus, so the decimals LESS
    # `n_negative` -- both published -- are the cells that could have
    # carried one, and the signed count taken from THAT is the unsigned
    # non-negative cells. **Measured** at a floor of eleven on 500
    # cells, 400 written `+100.5` upward, 99 written `-100.5` downward
    # and one written `250.5`: `n_numeric` 500, `n_negative` 99 and
    # `decimal_plus {"+": 400}`, so 500 less 99 less 400 is that one
    # cell. `n_negative` counts the whole column, so the difference is a
    # LOWER bound on the room and erring low errs toward refusing less.
    # The producer counts such a rare unsigned spelling into the plus
    # (the owner's ruling of 2026-09-17, item 6), so its own
    # descriptions leave nought over here.
    if "+" in plus and "decimal" in styles:
        populations = [styles["decimal"]]
        signable = styles["decimal"] - n_negative
        # READ ONLY WHERE THE SUBTRACTION IS CONSISTENT: `n_negative`
        # counts the negative WHOLE numbers too, so on a column holding
        # both kinds the difference falls below the signed count and
        # says nothing except that a reader's arithmetic does not apply
        # there. Refusing on it would refuse every such description.
        if signable >= plus["+"]:
            populations += [signable]
        if not parsing.census_nameable(
            [plus["+"]], populations, frame.floor
        ):
            raise _broken(
                "DP1",
                where,
                f"{plus['+']} of the {styles['decimal']} numbers written "
                f"with a point are said to carry a plus, beside "
                f"{n_negative} written with a minus",
                f"what is left over, of the decimals and of the ones that "
                f"could carry a plus alike, is nought or at least "
                f"{_census_floor(frame.floor)}",
            )
    widths = _fraction_widths(mapping, where, frame.floor, styles)
    padded = _padded_widths(mapping, where, frame.floor, styles)
    _pool_holds_both(where, frame.floor, styles, widths, padded)
    fields = _field_widths(mapping, where, frame.floor, styles)
    if WITHHELD in styles and fields:
        # P8 FOR THE WHOLE-NUMBER FIELD WIDTHS TOO (plan P4-D222): a forms
        # map that names nothing names no point-free form either.
        raise _broken(
            "P8",
            where,
            f"{_added(fields)} cells are counted by the width of the field "
            f"they wrote",
            "a form held back from the forms map has no widths published",
        )
    # P6's band, asked once both width censuses are read, so a width census
    # speaking for a pooled map is refused as P8 whatever its size.
    _census_may_speak(
        styles, "P6", where, frame.floor, len(NUMERIC_STYLES), "numbers' forms"
    )
    _widths_leave_no_one(where, frame.floor, styles, padded, fields)
    histogram = _value_histogram(mapping, where, frame.floor, used, ladder)
    hollow = _empty_bins(mapping, where, used, ladder, histogram)
    edges = _empty_edges(mapping, where, hollow, ladder)
    values = _whole(mapping["n_distinct_values"], "n_distinct_values", where, 0)
    # THE MODE PAIR, and its own invariant (plan P4-D4.11, contract
    # Q18). The two keys stand or fall together: a value with no count
    # says "this number dominated" without saying by how much, and a
    # count with no value says a number dominated without saying which,
    # so a block carrying one and not the other is refused. Where the
    # pair is published the count is at least two -- one cell is not a
    # mode, every value ties there -- and no more than the numeric
    # cells the block holds.
    mode = _figure_or_nothing(mapping["mode"], "mode", where)
    mode_count = _whole(mapping["mode_count"], "mode_count", where, 0)
    if (mode is None) != (mode_count == 0):
        raise _broken(
            "Q18",
            where,
            "the number this column held most often"
            + (" is not published" if mode is None else f" is {mode}"),
            f"the count of cells that held it is {mode_count}",
        )
    if mode is not None:
        if mode_count < 2:
            raise _broken(
                "Q18",
                where,
                f"the commonest number {mode} is published",
                f"only {mode_count} cell(s) held it",
            )
        if mode_count > n_numeric:
            raise _broken(
                "Q18",
                where,
                f"{mode_count} cells held the commonest number",
                f"{n_numeric} values read as a number",
            )
    # INVARIANT Q17. A block cannot hold more different numbers than it
    # holds numeric CELLS, and a block whose statistics used a value
    # holds at least one number. Both halves matter: the first is what
    # stops a description claiming a fidelity no twin could give it,
    # and the second is what stops a column of numbers saying it holds
    # none.
    #
    # THE BOUND IS AGAINST THE CELL COUNT AND NOT AGAINST `n_distinct`,
    # which would be the tighter statement on a whole column. This
    # function is asked the same question at three grains -- a column,
    # one part of a joined column, and the cores of an affixed one --
    # and only the first of the three has a spelling count that counts
    # the same cells. A bound that is true at one grain and quietly
    # false at the other two is worse than a looser one true at all
    # three.
    if values > n_numeric:
        raise _broken(
            "Q17",
            where,
            f"{values} different number(s)",
            f"{n_numeric} cell(s) that read as a number",
        )
    if used > 0 and values < 1:
        raise _broken(
            "Q17",
            where,
            "no different numbers at all",
            f"the {used} value(s) the statistics used",
        )
    return NumericFacts(
        percentiles=ladder,
        percentiles_between=finer,
        mean=mean,
        std=std,
        skew=skew,
        kurtosis=kurtosis,
        n_distinct_values=values,
        mode=mode,
        mode_count=mode_count,
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
        group_separator=mark,
        negative_form=negative,
        wide_runs=wide,
        negative_notations=notations,
        thousands_marks=marks,
        decimal_plus=plus,
        fraction_widths=widths,
        pad_widths=padded,
        field_widths=fields,
        value_histogram=histogram,
        empty_bins=hollow,
        empty_edges=edges,
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


def _group_separator(mapping: "dict[str, object]", where: str) -> str:
    """The mark between thousands, refused unless it is one this writes.

    A SPELLING, NOT A COUNT, so it carries no floor of its own: it
    names how the column's numbers were written, not how many cells
    any value had. The accepted marks are `parsing.PUBLISHED_GROUP_MARKS`:
    a comma, a space, an apostrophe, the right single quotation mark, a
    no-break space, a narrow no-break space and a thin space (landing
    2b.2, which read the last six for the first time), or a point on a column that
    writes its decimals with a comma (GS1 holds the comma and the point
    to the declaration). Any other value is refused rather than
    half-honoured.

    Guarantees: accepts the numeric mapping and where it sits; returns
    the empty string or one accepted mark. Determinism: a fixed
    function of the two. Raises ProfileError where the value is not
    text, or is text this producer never writes. No I/O of any kind.
    """
    value = mapping["group_separator"]
    if not isinstance(value, str):
        raise _wrong_type("group_separator", where, value, "a piece of text")
    if value not in parsing.PUBLISHED_GROUP_MARKS:
        shown: "list[str]" = []
        for mark in parsing.PUBLISHED_GROUP_MARKS:
            shown += [parsing.visible(mark)]
        raise _out_of_range(
            "group_separator",
            where,
            f"'{parsing.visible(value)}'",
            _listed(tuple(shown)),
        )
    return value


def _decimal_plus(
    mapping: "dict[str, object]", where: str, floor: int
) -> "dict[str, int]":
    """The census of signed decimals, refused unless the floor governs it.

    DP1 (landing 2b.2): `+` is the only name, and a named count is at
    least the smallest group size; `(withheld)` holds a count below it,
    and at a floor of one nothing is held back, so a pool there is
    refused -- which is what makes a count this block held back one its
    loader can see.

    Guarantees: accepts the numeric mapping, where it sits and the
    floor; returns the census. Determinism: a fixed function of the
    three. Raises ProfileError for a wrong type and for DP1. No I/O.
    """
    counted = _counts(mapping["decimal_plus"], "decimal_plus", where, 0)
    least = _census_floor(floor)
    for name in sorted(counted):
        if name == "+":
            if counted[name] < least:
                raise _broken(
                    "DP1",
                    where,
                    f"{counted[name]} numbers written with a point and a plus are named",
                    f"a published count names at least {least} of them",
                )
            continue
        if name == UNAVAILABLE:
            if counted[name] != 0:
                raise _broken(
                    "DP1",
                    where,
                    f"{counted[name]} is counted under '{UNAVAILABLE}'",
                    "the unavailable state carries no count at all",
                )
            continue
        raise _out_of_range(
            "decimal_plus",
            where,
            f"'{parsing.visible(name)}'",
            _listed(("+", UNAVAILABLE)),
        )
    if len(counted) > 1:
        raise _broken(
            "DP1",
            where,
            "the signed decimals are both counted and unavailable",
            "one census is either a count or unavailable",
        )
    return counted


def _census_floor(floor: int) -> int:
    """The smallest count the spelling censuses of landing 2b.7 publish.

    NEVER ONE, WHATEVER THE SETTINGS FLOOR (owner twin definition,
    clause 3; plan P4-D65.1). This is `taxonomy._census_floor`'s rule
    read from the other side: the producer publishes no count below it
    and the loader refuses a description that does. The rule is stated
    ONCE, in `parsing.census_floor`, and both sides read it (plan
    P4-D140).

    Guarantees: accepts the settings floor; returns two or the floor,
    whichever is larger. Determinism: a fixed function of the floor.
    Raises nothing. No I/O of any kind.
    """
    return parsing.census_floor(floor)


def _mixture_census(
    mapping: "dict[str, object]",
    key: str,
    where: str,
    floor: int,
    names: "tuple[str, ...]",
    invariant: str,
    thing: str,
) -> "dict[str, int]":
    """One census of a column's mixed conventions, held to its floor.

    THE LOADER'S HALF OF `taxonomy._mixture_census` (landing 2b.7, plan
    P4-D65.2). Every count it prints names a group: a named convention
    reaches `_census_floor`, and so does a `(withheld)` remainder, which
    is refused outright at a settings floor of one because the range
    below one is empty and S13 says a description written there holds
    nothing back. The unavailable state carries no count, and it is the
    one state a census reaches where it cannot speak safely.

    Raises ProfileError for a wrong type, an unknown convention, a
    count below the floor, a pool at a floor of one, a count beside the
    unavailable state, and a number under the unavailable state.
    """
    counted = _counts(mapping[key], key, where, 0)
    least = _census_floor(floor)
    if UNAVAILABLE in counted:
        if counted[UNAVAILABLE] != 0:
            raise _broken(
                invariant,
                where,
                f"{counted[UNAVAILABLE]} is counted under '{UNAVAILABLE}'",
                "the unavailable state carries no count at all",
            )
        if len(counted) > 1:
            raise _broken(
                invariant,
                where,
                f"the {thing} are both counted and unavailable",
                "one census is either a count or unavailable",
            )
        return counted
    for name in sorted(counted):
        if name == WITHHELD:
            if floor < 2:
                raise _broken(
                    "C5-S13",
                    where,
                    f"{counted[name]} {thing} are held back",
                    f"the smallest group size is {floor}",
                )
            if counted[name] < least:
                raise _broken(
                    invariant,
                    where,
                    f"{counted[name]} {thing} are held back",
                    f"a pooled remainder covers at least {least} of them",
                )
            continue
        if name not in names:
            raise _out_of_range(
                key,
                where,
                f"'{parsing.visible(name)}'",
                _listed(names + (WITHHELD, UNAVAILABLE)),
            )
        if counted[name] < least:
            raise _broken(
                invariant,
                where,
                f"{counted[name]} {thing} are named under "
                f"'{parsing.visible(name)}'",
                f"a published count names at least {least} of them",
            )
    return counted


def _negative_notations(
    mapping: "dict[str, object]",
    where: str,
    floor: int,
    n_negative: int,
    n_held: int,
) -> "dict[str, int]":
    """How many negatives wore each notation (7.5a; invariant NS2).

    NS2: every count reaches `_census_floor`; the census covers no more
    cells than the column says are negative; what it leaves of the
    negatives a double holds -- ``n_held``, `n_negative` less
    `n_negative_unrepresentable` -- is nought or a group, by
    `parsing.census_nameable` (plan P4-D140); and a position of a joined
    column, whose parts carry no sign, publishes none at all.

    Raises ProfileError for a wrong type, an unknown notation, a count
    below the floor, a census larger than the column's negatives and a
    remainder a reader could take that names fewer than the floor.
    """
    counted = _mixture_census(
        mapping,
        "negative_notations",
        where,
        floor,
        parsing.NEGATIVE_FORMS,
        "NS2",
        "negative numbers",
    )
    total = _added(counted)
    if total > n_negative:
        raise _broken(
            "NS2",
            where,
            f"the notations counted come to {total}",
            f"{n_negative} of the column's values are negative",
        )
    if UNAVAILABLE not in counted and counted:
        printed: "list[int]" = []
        for name in sorted(counted):
            printed += [counted[name]]
        if not parsing.census_nameable(printed, [n_held], floor):
            raise _broken(
                "NS2",
                where,
                f"the notations counted come to {total}",
                f"{n_held} of the column's values are negative numbers a "
                f"reader can take them from, and what is left over is "
                f"nought or at least {_census_floor(floor)}",
            )
    return counted


def _thousands_marks(
    mapping: "dict[str, object]", where: str, floor: int, n_numeric: int
) -> "dict[str, int]":
    """How many grouped cells wore each mark (7.5a; invariant TM1).

    TM1: every count reaches `_census_floor`; a mark this census names
    is one a description may publish; what it leaves of the column's
    numbers is nought or a group, by `parsing.census_nameable`; it is
    never `(unavailable)`, because a census that cannot speak is `{}`
    (plan P4-D140); and where the column publishes a mark of its own,
    that mark is one this census names -- a majority the mixture does
    not carry is a majority no cell proved. That last clause is asked in
    `_group_marks_agree`, after GS1, so a point on an undeclared column
    is refused for what it is.

    Raises ProfileError for a wrong type, an unknown mark, a count below
    the floor, the unavailable state and a remainder a reader could take
    that names fewer than the floor.
    """
    counted = _mixture_census(
        mapping,
        "thousands_marks",
        where,
        floor,
        _PUBLISHED_MARKS_NAMED,
        "TM1",
        "grouped numbers",
    )
    if UNAVAILABLE in counted:
        # THE SILENT STATE OF THIS CENSUS IS EMPTY (plan P4-D140). Where
        # no cell proves a mark it is `{}`, so a census holding back a
        # count below the floor must read the same; a second silent state
        # would let a reader tell nought from one.
        raise _broken(
            "TM1",
            where,
            "the census of marks is said to be unavailable",
            "a census of marks that cannot be published is empty",
        )
    if counted and UNAVAILABLE not in counted:
        printed: "list[int]" = []
        for name in sorted(counted):
            printed += [counted[name]]
        if not parsing.census_nameable(printed, [n_numeric], floor):
            raise _broken(
                "TM1",
                where,
                f"the grouped numbers counted come to {_added(counted)}",
                f"{n_numeric} of the column's values read as a number, and "
                f"what is left over is nought or at least "
                f"{_census_floor(floor)}",
            )
    return counted


def _wide_runs(mapping: "dict[str, object]", where: str) -> str:
    """Whether the column's wide runs are their own values' text.

    A WORD, like the notation and the mark beside it (landing 2b.13):
    `none`, `canonical` or `respelled`, and nothing else. It carries no
    count and never pools, which is the whole reason the fact was
    published as a word -- but a floor DOES hold it, as one holds the
    notation beside it (NS1). The word names the form of the cells it is
    about, and below the floor the forms map has pooled that form away
    on purpose; WR1 above reads the room and the floor together (the
    repair pass of landing 2b.13, plan P4-D91).

    Guarantees: accepts the numeric mapping and where it sits; returns
    one word of `parsing.WIDE_RUNS`. Determinism: a fixed function of
    the two. Raises ProfileError where the value is not text, or is a
    word this producer never writes. No I/O of any kind.
    """
    value = mapping["wide_runs"]
    if not isinstance(value, str):
        raise _wrong_type("wide_runs", where, value, "a piece of text")
    if value not in parsing.WIDE_RUNS:
        raise _out_of_range(
            "wide_runs",
            where,
            f"'{parsing.visible(value)}'",
            _listed(parsing.WIDE_RUNS),
        )
    return value


def _negative_form(mapping: "dict[str, object]", where: str) -> str:
    """How the column's negatives were written, one name of the four.

    A SPELLING, like the mark beside it (landing 2b.2): `minus`,
    `brackets`, `minus_sign` or `trailing_minus`, and nothing else.

    Guarantees: accepts the numeric mapping and where it sits; returns
    one name of `parsing.NEGATIVE_FORMS`. Determinism: a fixed function
    of the two. Raises ProfileError where the value is not text, or is
    a name this producer never writes. No I/O of any kind.
    """
    value = mapping["negative_form"]
    if not isinstance(value, str):
        raise _wrong_type("negative_form", where, value, "a piece of text")
    if value not in parsing.NEGATIVE_FORMS:
        raise _out_of_range(
            "negative_form",
            where,
            f"'{parsing.visible(value)}'",
            _listed(parsing.NEGATIVE_FORMS),
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
        if name != WITHHELD and styles[name] < _census_floor(floor):
            raise _broken(
                "P2",
                where,
                f"the form '{name}' was used by {styles[name]} cells",
                f"a published count names at least {_census_floor(floor)} "
                f"of them",
            )
    total = _added(styles)
    if total != n_numeric:
        raise _broken(
            "P1",
            where,
            f"the cells counted by the form they were written in come to {total}",
            f"{n_numeric} of the column's values read as a number",
        )
    # P6. A POOL STANDS ALONE, AND ONLY WHERE THE MAP CANNOT SPEAK (plans
    # P4-D221 and P4-D222; stage 2 closed by the owner rulings of
    # 2026-09-17). The forms map asks `parsing.census_nameable` through
    # `parsing.absorbed_census`: a form fewer cells than
    # `parsing.census_floor` wrote is counted into the commonest named
    # form, so a pool beside a named form is a description no producer
    # writes, and a reader subtracts it -- five forms of one cell each
    # read off a pool of five at a floor of one. The capacity bound this
    # replaces, the forms the map does not name times one less than the
    # floor, bounded exactly that pool.
    _pool_stands_alone(styles, "P6", where, "cells' forms")
    return styles


def _fraction_widths(
    mapping: "dict[str, object]",
    where: str,
    floor: int,
    styles: "dict[str, int]",
) -> "dict[str, int]":
    """How many figures the cells written with a point wrote after it.

    One of the two width censuses, and the rule they are both read
    under is `_width_census`. Raises ProfileError for a wrong type, a
    key that is not a canonical width, a named width below the floor,
    and for each of the four sum cases that rule states.
    """
    return _width_census(
        mapping,
        "fraction_widths",
        where,
        floor,
        styles,
        DECIMAL_STYLE,
        "written with a point",
        "the cells counted by the figures they wrote after the point",
        "P5",
        "P5",
        0,
        "P5",
        "a fraction may be written to no figures at all",
    )


def _value_histogram(
    mapping: "dict[str, object]",
    where: str,
    floor: int,
    used: int,
    ladder: NumberLadder,
) -> "dict[str, int]":
    """How many of a column's numbers fall in each published bin.

    INVARIANT Q15: the bins account for EVERY value the statistics
    used, and for no more. A histogram that counted fewer would let a
    twin place the missing ones anywhere it liked while the description
    looked complete; one that counted more would describe a column
    nobody has. The `(withheld)` remainder is part of the sum, because
    a bin below the floor is a bin whose values were counted and whose
    edges were not named.

    THE KEYS ARE BIN NUMBERS, canonically written and inside the fixed
    range the method sets. A key outside it is a description this
    version cannot place, and the loader is normative, so it refuses
    rather than guessing which bin was meant.

    Raises ProfileError for a wrong type, a key that is not a canonical
    bin number, a bin at or below zero, a named bin below the floor,
    and for a sum that is not the count of values used.
    """
    # READ THE SAME WAY ITS SIBLING CENSUSES ARE, through `_counts`,
    # which is where the type of the block and the type of every entry
    # are settled. Reaching for `mapping.get` instead put a method call
    # on a value the offline audit cannot trace, and the audit is right
    # to refuse it: a caller-supplied object may define `get` to do
    # anything at all.
    counts = _counts(mapping["value_histogram"], "value_histogram", where, 1)
    total = 0
    for key in sorted(counts):
        entry = counts[key]
        if key != WITHHELD:
            if not _is_bin_key(key):
                raise _broken(
                    "Q15",
                    where,
                    "a key of the histogram is not a bin number",
                    "a bin number written plainly, from 0 upwards",
                )
            if entry < floor:
                raise _broken(
                    "Q15",
                    where,
                    f"a bin of the histogram counts {entry} cell(s)",
                    f"the publication floor of {floor}",
                )
        total = total + entry
    if counts and total != used:
        raise _broken(
            "Q15",
            where,
            f"the bins of the histogram count {total} value(s)",
            f"the {used} value(s) the statistics used",
        )
    # AND AT A FLOOR OF ONE AN EMPTY HISTOGRAM IS IMPOSSIBLE. Every bin
    # that holds anything holds at least one value, so no bin can fall
    # below a floor of one and the census is always publishable. An
    # empty object there is a description built at a HIGHER floor and
    # handed over as though it were this one -- a position the floor
    # moves that nothing else in the document records, which is the gap
    # `tests/test_p3v5f1_floor_one.py` exists to close.
    #
    # The one honest empty at a floor of one is a column whose ends
    # this format cannot hold, or whose ends are finite and whose WIDTH
    # is not: the bins then have no width to divide and the producer
    # publishes none.
    if not counts and used > 0 and floor <= 1 and _has_width(ladder):
        raise _broken(
            "Q15",
            where,
            "the histogram is empty",
            (
                "a bin for every value, since at a smallest group size "
                "of one no bin can be held back"
            ),
        )
    return counts


def _empty_edges(
    mapping: "dict[str, object]",
    where: str,
    bins: "tuple[int, ...]",
    ladder: "NumberLadder",
) -> "tuple[tuple[float, float], ...]":
    """The real boundaries of each stretch this column leaves empty.

    RESIDUAL R-P4-138, closed by the owner's ruling of 2026-09-04. One
    `[below, above]` pair per RUN of empty bins: the largest value
    under the stretch and the smallest over it. The twin keeps out of
    the open interval between them, which the bins alone cannot ask
    for -- the bins a column leaves empty sit strictly INSIDE the
    stretch it really leaves empty, so a cell repaired to a bin edge
    still lands in the source's own gap. Measured on a 300-row column
    whose real gap runs 26.9 to 74.0: five cells of three hundred sat
    in it at every seed, about a unit past the cluster edge.

    Q21: as many pairs as the bins have runs, each pair ascending, each
    inside the published ends, and the pairs themselves ascending and
    not overlapping. A description that cannot be read as a set of
    stretches is refused rather than repaired.
    """
    given = mapping["empty_edges"]
    if not isinstance(given, list):
        raise _wrong_type(
            "empty_edges", where, given, "a list of edge pairs"
        )
    # THE RUNS THEMSELVES and not just how many, because each pair has
    # to be bound to the stretch it belongs to (review round 1 item 4).
    stretches: "list[tuple[int, int]]" = []
    for place in bins:
        if stretches and place == stretches[-1][1] + 1:
            stretches[-1] = (stretches[-1][0], place)
        else:
            stretches += [(place, place)]
    if len(given) != len(stretches):
        raise _broken(
            "Q21",
            where,
            f"{len(given)} pair(s) of edges are named",
            f"one pair for each of the {len(stretches)} stretch(es) of "
            "empty bins this column names",
        )
    edges: "list[tuple[float, float]]" = []
    for entry in given:
        if not isinstance(entry, list) or len(entry) != 2:
            raise _wrong_type(
                "empty_edges", where, entry, "a pair of two numbers"
            )
        below = _figure(entry[0], "empty_edges", where)
        above = _figure(entry[1], "empty_edges", where)
        if not below < above:
            raise _broken(
                "Q21",
                where,
                f"the stretch runs from {below} to {above}",
                "a stretch whose lower edge is below its upper one",
            )
        # TWO STRETCHES MAY SHARE AN EDGE, and refusing that was wrong:
        # a single value standing between two gaps is the upper edge of
        # one and the lower edge of the next, and it is one real cell.
        # A 240-row column with a value at 47.0 between two stretches
        # was refused by its own producer's description.
        if edges and below < edges[-1][1]:
            raise _broken(
                "Q21",
                where,
                f"the stretch starting at {below} overlaps the one "
                f"ending at {edges[-1][1]}",
                "stretches that ascend and do not overlap",
            )
        edges += [(below, above)]
    # THE TWO ENDS, READ ONCE AND GUARDED. A rung may be null, meaning
    # the exact value is not one this format can hold, and a block
    # whose ends are not both finite has no scale to divide -- so it
    # publishes no empty bin, and a pair naming values it lies between
    # would be naming a stretch of nothing.
    low = ladder.rungs[0]
    high = ladder.rungs[-1]
    if low is None or high is None:
        if edges:
            raise _broken(
                "Q21",
                where,
                f"{len(edges)} pair(s) of edges are named",
                "no pair at all, on a column one of whose two ends is "
                "not a value this format can hold",
            )
        return tuple(edges)
    for below, above in edges:
        if below < low or above > high:
            raise _broken(
                "Q21",
                where,
                f"the stretch runs from {below} to {above}",
                "a stretch inside the two ends this column publishes",
            )
    # AND EACH PAIR STANDS EITHER SIDE OF ITS OWN RUN OF BINS (review
    # round 1 item 4). Without this a description could name a pair
    # BOTH of whose values fall in bins it also says hold nothing --
    # ends 0 and 32, a run of bins 10 to 12, the pair [11, 12] -- which
    # met every condition above and describes no column any table
    # holds, while the value stage read the two numbers as real cells.
    # The edge below a run is a value in an EARLIER bin and the edge
    # above it a value in a LATER one, which is what "the largest value
    # under the stretch and the smallest over it" means.
    for index in range(len(edges)):
        below = edges[index][0]
        above = edges[index][1]
        under = parsing.histogram_bin(below, low, high)
        over = parsing.histogram_bin(above, low, high)
        first = stretches[index][0]
        last = stretches[index][1]
        # THE EDGES STAND IN THE BINS NEXT TO THE RUN, not merely
        # somewhere before and after it (review round 7 item 4). Every
        # bin the description does not name as empty holds something,
        # so the LARGEST value below a run is in the bin immediately
        # before it and the SMALLEST above it in the bin immediately
        # after. A pair naming the two ends of the whole scale for a
        # run of three bins met the weaker test and describes no
        # column: the bins between its values and the run are said to
        # hold something, and that something is nearer.
        if under != first - 1 or over != last + 1:
            raise _broken(
                "Q21",
                where,
                f"the stretch of bins {first} to {last} is named as "
                f"lying between {below} and {above}, which stand in "
                f"bins {under} and {over}",
                f"a stretch whose lower edge is a value in bin "
                f"{first - 1} and whose upper edge is a value in bin "
                f"{last + 1}, the bins either side of it",
            )
    return tuple(edges)


def _empty_bins(
    mapping: "dict[str, object]",
    where: str,
    used: int,
    ladder: NumberLadder,
    histogram: "dict[str, int]",
) -> "tuple[int, ...]":
    """Which bins a column says hold none of its numbers (7.11).

    INVARIANT Q20, in three conditions, and each one refuses a
    description that says something about a shape no column has.

    1. THE LIST IS A LIST OF BINS, each named once and in order. Order
       is not decoration here: this is the one fact of the block that
       is read as a set of stretches rather than as a mapping, and a
       list a producer may write two ways is a list two producers write
       two ways.
    2. THE TWO END BINS ARE NEVER AMONG THEM. The scale runs from the
       column's smallest number to its largest, so the smallest is in
       the first bin and the largest in the last, and a column with a
       scale has both occupied. A description naming either is
       describing a column with no smallest value, which is not a
       column.
    3. WHERE THE CENSUS IS PUBLISHED AND THERE IS A SCALE, THE TWO ARE
       COMPLEMENTS. The census is all or nothing, so where it is
       published at all it names every bin that holds something; the
       bins holding nothing are then exactly the rest. This is the
       guard against the fact being written twice and one copy moving:
       a description whose two shape facts disagree is refused rather
       than read.

       THE SCALE CONDITION IS NOT A SOFTENING, and it is where a real
       disagreement between the producer and this rule was found. A
       column whose values are all ONE number has two equal ends, so
       there is no width to divide; the bin rule is TOTAL and answers
       "the first bin" for every value, so the census reads `{"0": n}`
       while the other thirty-one bins are empty of a division that
       does not exist. Requiring the complement there would demand that
       a description name thirty-one bins of a scale it does not have,
       and the producer -- rightly -- names none.

    AND WHERE THE COLUMN HAS NO SCALE THE LIST IS EMPTY. A ladder whose
    ends this format cannot hold, or whose ends are finite and whose
    width is not, divides into no bins at all, and "no bin holds
    anything" is a different sentence from "there is nothing to
    divide". The same is true of a block whose statistics used no
    value.

    Raises ProfileError for a wrong type, a bin outside the range this
    method has, a repeat, an entry out of order, an end bin, a list on
    a column with no scale, and for disagreement with the census.
    """
    given = mapping["empty_bins"]
    if not isinstance(given, list):
        raise _wrong_type(
            "empty_bins", where, given, "a list of bin numbers"
        )
    bins: list[int] = []
    for entry in given:
        if isinstance(entry, bool) or not isinstance(entry, int):
            raise _wrong_type(
                "empty_bins", where, entry, "a whole bin number"
            )
        if not 0 <= entry < parsing.HISTOGRAM_BINS:
            raise _out_of_range(
                "empty_bins",
                where,
                f"{entry}",
                f"a bin number from 0 to {parsing.HISTOGRAM_BINS - 1}",
            )
        if bins and entry <= bins[-1]:
            raise _broken(
                "Q20",
                where,
                f"the bin {entry} is named after the bin {bins[-1]}",
                "each bin named once, in ascending order",
            )
        bins += [entry]
    scaled = used > 0 and _has_width(ladder)
    if bins and not scaled:
        raise _broken(
            "Q20",
            where,
            f"{len(bins)} bin(s) are named as holding nothing",
            "this column's numbers divide into no bins at all",
        )
    if scaled:
        for entry in bins:
            if entry == 0 or entry == parsing.HISTOGRAM_BINS - 1:
                raise _broken(
                    "Q20",
                    where,
                    f"the bin {entry} is named as holding nothing",
                    "the smallest value is in the first bin and the "
                    "largest in the last, so neither is ever empty",
                )
    if histogram and scaled:
        named = {key for key in histogram if key != WITHHELD}
        for entry in bins:
            if f"{entry}" in named:
                raise _broken(
                    "Q20",
                    where,
                    f"the bin {entry} is named as holding nothing",
                    f"the shape of this column's numbers says it holds "
                    f"{histogram[f'{entry}']}",
                )
        for place in range(parsing.HISTOGRAM_BINS):
            if f"{place}" in named or place in bins:
                continue
            raise _broken(
                "Q20",
                where,
                f"the bin {place} is named neither as holding nothing "
                f"nor by the shape of this column's numbers",
                "every bin is named by exactly one of the two",
            )
    return tuple(bins)


def _has_width(ladder: NumberLadder) -> bool:
    """Whether a ladder's two ends leave a width the bins can divide."""
    lowest = ladder.minimum
    highest = ladder.maximum
    if lowest is None or highest is None:
        return False
    if lowest - lowest != 0.0 or highest - highest != 0.0:
        return False
    reach = highest - lowest
    if reach - reach != 0.0:
        return False
    return reach > 0.0


def _is_bin_key(key: object) -> bool:
    """Whether ``key`` names a bin this version of the method has."""
    if not isinstance(key, str):
        return False
    if not key:
        return False
    for character in key:
        if character not in "0123456789":
            return False
    if key != "0" and key[:1] == "0":
        return False
    return 0 <= int(key) < parsing.HISTOGRAM_BINS


def _padded_widths(
    mapping: "dict[str, object]",
    where: str,
    floor: int,
    styles: "dict[str, int]",
) -> "dict[str, int]":
    """How wide the cells written with a redundant zero wrote a field.

    The second width census (P4-D14). A forms map counting two hundred
    and forty `leading_zero` cells cannot say whether the field was
    five figures wide or nine, so a twin honouring that map exactly
    wrote fields of another width and no report could say so.

    Raises ProfileError for a wrong type, a key that is not a canonical
    width, a named width below the floor, and for each of the four sum
    cases `_width_census` states.
    """
    return _width_census(
        mapping,
        "pad_widths",
        where,
        floor,
        styles,
        LEADING_ZERO_STYLE,
        "written with a redundant zero",
        "the cells counted by the width of the field they wrote",
        "P5b",
        "P6b",
        2,
        "P7b",
        "a padded cell writes at least one zero in front of at least "
        "one figure, so its narrowest field is two",
        LEADING_PLUS_STYLE,
    )


POINT_FREE_STYLES = (PLAIN_STYLE, LEADING_PLUS_STYLE, LEADING_ZERO_STYLE)


def _widths_leave_no_one(
    where: str,
    floor: int,
    styles: "dict[str, int]",
    padded: "dict[str, int]",
    fields: "dict[str, int]",
) -> None:
    """The width censuses, read against each other by the disclosure rule.

    WHAT A READER SUBTRACTS, THE LOADER CHECKS (plan P4-D148). Each width
    census floors its own counts, and two of them are subtracted from
    each other and from the forms map: `pad_widths` less the named
    `leading_zero` count is the plus-signed padded cells, and the
    `leading_plus` count less that is the ones with no pad (P5b); at a
    width both censuses name, `field_widths` less `pad_widths` is the
    cells written there with no pad (P6c). `parsing.width_census_breaches`
    states both, once, for the producer and for this loader; a
    description in which either difference is neither nought nor a group
    is refused rather than read.

    Raises ProfileError naming P5b or P6c; returns None when both hold.
    """
    plus_broken, broken = parsing.width_census_breaches(
        styles, padded, fields, floor
    )
    least = _census_floor(floor)
    if plus_broken:
        raise _broken(
            "P5b",
            where,
            "the cells counted by the width of the field they wrote leave "
            "a count of cells written with a plus and a redundant zero, or "
            "of cells written with a plus and none, that is neither nought "
            "nor a group",
            f"each is nought or at least {least}",
        )
    for width in broken:
        raise _broken(
            "P6c",
            where,
            f"the width '{width}' is named by both width censuses, and the "
            f"cells written there without a redundant zero number neither "
            f"nought nor a group",
            f"that number is nought or at least {least}",
        )


def _field_widths(
    mapping: "dict[str, object]",
    where: str,
    floor: int,
    styles: "dict[str, int]",
) -> "dict[str, int]":
    """How wide every whole-written cell wrote its figure field (7.9).

    THE THIRD CENSUS, AND IT IS NOT READ UNDER `_width_census` (plan
    P4-D30). That reading is written for a census of ONE form, whose
    sum equals that form's count exactly or else lives inside the
    styles map's pooled remainder. This census covers THREE forms at
    once -- `plain`, `leading_plus` and `leading_zero`, which are
    exactly the forms carrying no point and no exponent -- so its sum
    is bounded on two sides rather than pinned on one, and forcing it
    through the other reading would have meant asking a rule a question
    it was not written to answer.

    WHAT BINDS IT, and each of the three is provable from the
    definition rather than assumed:

    1. every cell counted by a NAMED point-free style is a cell this
       census counts, so the total is at least their sum;
    2. every further cell it counts was held back from the styles map,
       so the total is at most that sum plus the pooled remainder;
    There is deliberately no THIRD condition against `n_numeric`: P1
    makes the styles map sum to the numeric count exactly, so the
    second bound above IS that ceiling, and writing it again would be
    a check that cannot fail.

    WHAT IT DOES NOT CHECK IS STATED RATHER THAN LEFT TO BE FOUND. A
    loader holds no table, so nothing here checks that a width count IS
    the count of source cells at that width -- that is producer
    obligation XW-P -- and nothing here compares this census against
    `pad_widths`, whose cells are a SUBSET of these and whose widths
    are reached by padding rather than by magnitude.

    Raises ProfileError for a wrong type, a key that is not a canonical
    width, a named width below the floor, a width of nought, and for
    either end of the sum bound.
    """
    widths = _counts(mapping["field_widths"], "field_widths", where, 1)
    for name in sorted(widths):
        if name == WITHHELD:
            continue
        if not _is_canonical_width(name):
            raise _out_of_range(
                f"field_widths -> {name}",
                where,
                f"'{name}'",
                "a whole number of figures written without padding",
            )
        if int(name) < 1:
            # A CELL WRITTEN WHOLE WRITES AT LEAST ONE FIGURE. A census
            # naming width 0 describes cells no producer can have read
            # and no twin can write.
            raise _broken(
                "P7c",
                where,
                "the width '0' is named",
                "a cell written as a whole number writes at least one "
                "figure",
            )
        if widths[name] < _census_floor(floor):
            raise _broken(
                "P6c",
                where,
                f"the width '{name}' was written by {widths[name]} cells",
                f"a published count names at least {_census_floor(floor)} "
                f"of them",
            )
    # A POOL OF WIDTHS STANDS ALONE (plan P4-D222).
    _pool_stands_alone(
        widths, "P6c", where, "cells' whole-number field widths"
    )
    total = _added(widths)
    named = 0
    for style in POINT_FREE_STYLES:
        if style in styles:
            named = named + styles[style]
    pooled = styles[WITHHELD] if WITHHELD in styles else 0
    if total < named:
        raise _broken(
            "P9c",
            where,
            f"{total} cells are counted by the width of the field they "
            f"wrote",
            f"{named} cells were written in a form that carries no point",
        )
    if total > named + pooled:
        raise _broken(
            "P9c",
            where,
            f"{total} cells are counted by the width of the field they "
            f"wrote",
            f"{named} cells were written in a named form that carries no "
            f"point, and {pooled} cells in all were held back from the "
            f"forms map",
        )
    # AND THERE IS NO SEPARATE CEILING AGAINST `n_numeric`, which is
    # stated here rather than left as a gap. P1 makes the styles map
    # sum to the numeric count exactly, so `named + pooled` IS
    # `n_numeric` and the bound above is that ceiling already. A third
    # comparison would be a check that cannot fail, which this
    # repository counts as a defect rather than as caution.
    return widths


def _width_census(
    mapping: "dict[str, object]",
    key: str,
    where: str,
    floor: int,
    styles: "dict[str, int]",
    style: str,
    wrote: str,
    counted: str,
    sum_rule: str,
    floor_rule: str,
    least: int,
    least_rule: str,
    least_rule_says: str,
    also: str = "",
) -> "dict[str, int]":
    """The one reading both width censuses are checked under.

    ONE RULE, ASKED TWICE, IN ONE PLACE. Two censuses of the same shape
    with two copies of this arithmetic is the shape of defect this
    repository has already paid for more than once: a rule that lives
    in two places comes apart from itself, and the half nobody edited
    is the half that stays wrong. The wording each census shows a
    person differs, so the words are arguments; the arithmetic does
    not, so it is written once.

    ITS SUM IS STATED OVER A NUMBER THAT MAY NOT EXIST, and that is the
    whole difficulty this reads through (plan amendments A-P4-5 and
    A-P4-6). Where the floor named the form, `numeric_styles` carries
    its key and the census sums to it exactly. Where the floor POOLED
    that form, no published number holds the count of its cells -- and
    an earlier reading concluded the sum obligation then binds nothing,
    which would have admitted a census of a thousand cells in a column
    of a hundred. Three published numbers bound it instead:

    1. non-empty means a total of at least one;
    2. the total is strictly BELOW the floor, because a form is pooled
       only when its own count falls below it;
    3. the total is at most the pooled remainder of the forms map,
       because the pooled cells of this form are a subset of that pool.

    The census may also be empty in the pooled case, which is what a
    column with no cell of the form at all writes.

    ``also`` NAMES A SECOND FORM SOME OF WHOSE CELLS THE CENSUS COUNTS
    (plan P4-D145). The padding census counts every `leading_zero` cell
    and, since a plus stopped hiding a pad, the `leading_plus` cells whose
    figures begin with a redundant zero -- a number no published key
    holds. So where ``also`` is given the sum is a WINDOW and not a
    point: at least the first form's named count, and at most that count
    plus the second form's and the pooled remainder; and in the pooled
    case the two forms' pooled cells may each fall just below the floor.
    """
    widths = _counts(mapping[key], key, where, 1)
    for name in sorted(widths):
        if name == WITHHELD:
            continue
        if not _is_canonical_width(name):
            raise _out_of_range(
                f"{key} -> {name}",
                where,
                f"'{name}'",
                "a whole number of figures written without padding",
            )
        if int(name) < least:
            # A WIDTH NO CELL OF THIS FORM CAN WEAR. The padded style
            # writes at least one zero in front of at least one figure,
            # so its narrowest field is two: a census naming width 0 or
            # 1 describes cells no producer can have read and no twin
            # can write, and admitting it left the generator refusing a
            # width the loader had accepted.
            raise _broken(
                least_rule,
                where,
                f"the width '{name}' is named",
                least_rule_says,
            )
        if widths[name] < _census_floor(floor):
            raise _broken(
                floor_rule,
                where,
                f"the width '{name}' was written by {widths[name]} cells",
                f"a published count names at least {_census_floor(floor)} "
                f"of them",
            )
    total = _added(widths)
    # A POOL OF WIDTHS STANDS ALONE (plan P4-D222): a width below the line
    # is counted into the commonest width.
    _pool_stands_alone(widths, floor_rule, where, f"cells {wrote}")
    extra = styles[also] if also and also in styles else 0
    pool = styles[WITHHELD] if WITHHELD in styles else 0
    if style in styles:
        if also and styles[style] <= total <= styles[style] + extra + pool:
            return widths
        if total != styles[style]:
            raise _broken(
                sum_rule,
                where,
                f"{counted} come to {total}",
                f"{styles[style]} cells were {wrote}",
            )
        return widths
    # A FORM THE FORMS MAP HOLDS BACK HAS NO WIDTHS PUBLISHED (plan
    # P4-D221). How many cells the pool holds of it is invariant P8's,
    # read against both censuses at once; the pool's own capacity is P6.
    pooled = styles[WITHHELD] if WITHHELD in styles else 0
    if not total or pooled:
        return widths
    if also:
        # NOTHING HELD BACK AND THE FIRST FORM NOT NAMED (plan P4-D145, as
        # amended by the repair pass): no cell of the first form exists, so every cell the
        # census counts is a cell of the second form, and there are no
        # more of them than that form's named count.
        if total > extra:
            raise _broken(
                sum_rule,
                where,
                f"{total} cells are counted as {wrote}",
                f"no cell was written in the first form, and {extra} were "
                f"written in the second",
            )
        return widths
    raise _broken(
        sum_rule,
        where,
        f"{total} cells are counted as {wrote}",
        f"{pooled} cells in all were held back from the forms map",
    )
    return widths


def _pool_holds_both(
    where: str,
    floor: int,
    styles: "dict[str, int]",
    widths: "dict[str, int]",
    padded: "dict[str, int]",
) -> None:
    """The pooled remainder, read against BOTH censuses at once (P8).

    A WIDTH CENSUS OF A HELD-BACK FORM IS EMPTY (plan P4-D221; stage 2
    closed by the owner rulings of 2026-09-17). Before, each census
    counted the pooled cells of its own form, fewer than the floor, and
    this rule asked whether what the two censuses left over could be
    shared out among the forms left to hold it. Every such count names
    rows: since plan P4-D222 a map holds cells back only all together,
    where no form reaches `parsing.census_floor`, so a width census there
    says how many of those cells wore a point or a pad.
    1,200 prices with one padded cell at a floor of eleven published
    `pad_widths {"(withheld)": 1}`. So where the forms map holds cells
    back, neither census speaks for a form it does not name, and the
    pool's capacity is P6's alone.

    Raises ProfileError naming P8; returns None when the counts hold.
    """
    if WITHHELD not in styles:
        return
    for style, census in (
        (DECIMAL_STYLE, widths),
        (LEADING_ZERO_STYLE, padded),
    ):
        if style in styles or not census:
            continue
        raise _broken(
            "P8",
            where,
            f"{_added(census)} cells are counted by width in the form "
            f"'{style}', which the forms map holds back",
            "a form held back from the forms map has no widths published",
        )


def _shape_forms(
    mapping: "dict[str, object]",
    where: str,
    floor: int,
    with_code_total: bool = False,
    with_text_total: bool = True,
) -> "dict[str, int]":
    """The census of written forms, checked key by key (C6-D18).

    A KEY CARRIES NO FIGURE AND NO LETTER OF THE TABLE, and that is
    checked here rather than assumed: every ASCII digit of a key must
    be `9` and every ASCII letter must be `A`, because the producer
    builds a form by replacing them and a key where another survived is
    a key carrying a fragment of somebody's value. A loader that
    accepted one would let a producer -- or a hand-edited file -- put a
    real code into the one field this role has for saying what its
    values look like.

    The floor governs a named form as it governs a level, and the
    `(withheld)` pool takes what it holds back.

    Raises ProfileError for a wrong type, a key that is not a form, a
    key longer than the limit, and a named form below the floor.
    """
    forms = _counts(mapping["shape_forms"], "shape_forms", where, 1)
    counted = 0
    for name in sorted(forms):
        counted = counted + forms[name]
    present = _whole(mapping["n_present"], "n_present", where, 0)
    if counted > present:
        # SF3. AT MOST, AND NOT EXACTLY. A cell over the length limit
        # has no form and is counted nowhere in this census, so the
        # sum falls short of `n_present` on any column holding one and
        # only an upper bound is checkable here.
        raise _broken(
            "SF3",
            where,
            f"the census counts {counted} cells",
            f"the column holds {present} present cells",
        )
    for name in sorted(forms):
        if name == WITHHELD:
            # THE POOL IS THE FLOOR'S OWN, AND AT A FLOOR OF ONE THERE
            # IS NONE -- but that rule is C5-S13's and is checked at
            # the top of the document, before any column block is
            # read. `shape_forms` is in C5-S13's own list, so a census
            # holding a pool at a floor of one is refused there and a
            # rule of this function's own would be unreachable. It was
            # written and withdrawn for exactly that reason (review
            # round 1 finding 9): a rule no document can reach is a
            # rule no test can exercise.
            continue
        if not _is_shape_form(name):
            raise _out_of_range(
                f"shape_forms -> {name}",
                where,
                "a key of that shape",
                "a written form: a figure written '%', a letter "
                "written '@' -- or '&' throughout, where every letter "
                "was lower case -- and between them only the marks "
                "- . / _ : # * ( ) [ ] + , -- carrying at least two "
                "of those three kinds",
            )
        if forms[name] < parsing.census_floor(floor):
            raise _broken(
                "SF1",
                where,
                f"the form '{name}' was written by {forms[name]} cells",
                f"a form is named only at {parsing.census_floor(floor)} "
                "cells or more: the smallest group size, and never under two",
            )
        _lower_case_key_line(forms, name, where, floor)
        if parsing.SHAPE_LOWER in name:
            distinct = _whole(mapping["n_distinct"], "n_distinct", where, 0)
            folded_distinct = _whole(
                mapping["n_distinct_folded"], "n_distinct_folded", where, 0
            )
            if distinct != folded_distinct:
                # SF5. The census writes a lower-case key only on a
                # column whose values do not fold onto one another,
                # because the twin's case partners could never pay one
                # (P4-D121).
                raise _broken(
                    "SF5",
                    where,
                    f"the lower-case key '{name}' is named",
                    f"the column holds {distinct} different values that "
                    f"fold to {folded_distinct}",
                )
    _form_census_names_no_row(
        mapping, forms, where, present, with_code_total, with_text_total
    )
    return forms


def _form_census_names_no_row(
    mapping: "dict[str, object]",
    forms: "dict[str, int]",
    where: str,
    present: int,
    with_code_total: bool,
    with_text_total: bool = True,
) -> None:
    """SF1 and SF3's last lines: no reading names one row (plan P4-D160).

    The producer's own question, `parsing.census_names_one_row`, asked of
    the same three readings: the pool, which is never one; `n_present`
    less every cell the census counts, the pool included; and, on a
    free-text column, `n_code_alphabet` less the cells of the named forms
    made of figures, letters, the hyphen and the underscore, and
    `n_code_alphabet` less `n_all_digits` less the same cells; and
    `n_not_numeric` less the cells of the named forms no number can be
    written in (`parsing.form_never_a_number`, plan P4-D175). A census
    that counts no cell is asked nothing: it leaves nothing to subtract.

    Raises ProfileError for SF1 (a pool of one) and SF3 (a difference of
    one).
    """
    pool: "dict[str, int]" = {}
    counted = 0
    coded = 0
    texted = 0
    for name in sorted(forms):
        counted = counted + forms[name]
        if name == WITHHELD:
            pool = {WITHHELD: forms[name]}
            continue
        if _layout_within(name, _FORM_CODE_MARKS):
            coded = coded + forms[name]
        if parsing.form_never_a_number(name):
            texted = texted + forms[name]
    if parsing.census_names_one_row(pool, []) == -2:
        raise _broken(
            "SF1",
            where,
            "the pool holds 1 cell",
            "a pool is written only where it holds two or more",
        )
    if parsing.census_names_one_row({}, [(present, counted)]) == 0:
        raise _broken(
            "SF3",
            where,
            f"the census counts {counted} cells",
            f"the column holds {present} present cells, one more",
        )
    if with_code_total:
        total = _whole(mapping["n_code_alphabet"], "n_code_alphabet", where, 0)
        if parsing.census_names_one_row({}, [(total, coded)]) == 0:
            raise _broken(
                "SF3",
                where,
                f"the forms inside the code alphabet count {coded} cells",
                f"n_code_alphabet is {total}, one more",
            )
        # A FORM CARRIES TWO KINDS, so no cell of figures alone wears one
        # and a code form counts cells of the code alphabet that are not
        # figures alone (plan P4-D175).
        digits = _whole(mapping["n_all_digits"], "n_all_digits", where, 0)
        if parsing.census_names_one_row({}, [(total - digits, coded)]) == 0:
            raise _broken(
                "SF3",
                where,
                f"the forms inside the code alphabet count {coded} cells",
                f"n_code_alphabet less n_all_digits is {total - digits}, "
                "one more",
            )
    if not with_text_total:
        # The label half of a compound column publishes no
        # `n_not_numeric`; every cell of it is text.
        return
    text = _whole(mapping["n_not_numeric"], "n_not_numeric", where, 0)
    if parsing.census_names_one_row({}, [(text, texted)]) == 0:
        raise _broken(
            "SF3",
            where,
            f"the forms no number can be written in count {texted} cells",
            f"n_not_numeric is {text}, one more",
        )


# The characters a form key may hold for every cell wearing it to lie
# inside the alphabet `n_code_alphabet` counts (C6-31a, plan P4-D160).
_FORM_CODE_MARKS = "%@&-_"


def _lower_case_key_line(
    forms: "dict[str, int]", name: str, where: str, floor: int
) -> None:
    """SF1's second line: a lower-case key and its partner clear two.

    (Plan P4-D121.) At a floor of two or more this is the floor line
    itself and is already met by the time it is asked; at a floor of one
    it is the line a count of one person may not cross.

    A key written with `&` names the cells of one form whose every
    letter was lower case, and the census writes it only where they
    number at least the floor AND at least two -- and where the form's
    own key stands beside it, only where the other cells do too. Below
    that the census names the form blind to case instead, because a
    pair of keys one of which counts a single cell publishes a count of
    one, and a pair whose sum is known makes one of them the complement
    of the other. A loader that admitted either would carry a count of
    one person the producer refuses to write.

    Raises ProfileError for SF1.
    """
    if parsing.SHAPE_LOWER not in name:
        return
    line = parsing.census_floor(floor)
    partner = ""
    for character in name:
        partner = partner + (
            parsing.SHAPE_LETTER if character == parsing.SHAPE_LOWER
            else character
        )
    if forms[name] < line:
        raise _broken(
            "SF1",
            where,
            f"the lower-case key '{name}' counts {forms[name]} cells",
            f"a lower-case key is named only at {line} cells or more",
        )
    if partner in forms and forms[partner] < line:
        raise _broken(
            "SF1",
            where,
            f"the key '{partner}' beside '{name}' counts "
            f"{forms[partner]} cells",
            f"beside a lower-case key it is named only at {line} cells "
            "or more",
        )


def _number_spellings(
    mapping: "dict[str, object]",
    where: str,
    frame: _Frame,
    n_numeric: int,
    n_zero: int,
) -> "dict[str, int]":
    """The spelling census of a count column, checked (7.13, P4-D123).

    ALL OR NOTHING, and every rule here is one the producer keeps:

    - SC1: every key is one to fifteen figures and nothing else, and
      every count is at least the smallest group size and at least two
      -- a census naming a spelling one cell wrote publishes that cell;
    - SC2: a census that names anything names every number cell, so its
      counts sum to `n_numeric`, and at least two of its keys are one
      number written two ways, which is the only thing it is for; and
      it names no more spellings than a set of categories may hold;
    - SC3: its spellings of nought count exactly `n_zero` cells.

    Raises ProfileError for a wrong type, and for SC1, SC2 and SC3.
    """
    spellings = _counts(
        mapping["number_spellings"], "number_spellings", where, 1
    )
    if not spellings:
        return spellings
    line = parsing.census_floor(frame.floor)
    total = 0
    zeros = 0
    seen: "dict[str, int]" = {}
    twice = False
    for name in sorted(spellings):
        if (
            name == WITHHELD
            or len(name) > 15
            or not parsing.is_digit_text(name)
        ):
            raise _out_of_range(
                "number_spellings -> (a key)",
                where,
                "a key of that shape",
                "a whole number written in one to fifteen figures and "
                "nothing else",
            )
        if spellings[name] < line:
            raise _broken(
                "SC1",
                where,
                f"a spelling written by {spellings[name]} cell(s)",
                f"a spelling is named only at {line} cells or more",
            )
        total = total + spellings[name]
        bare = name
        while len(bare) > 1 and bare[0] == "0":
            bare = bare[1:]
        if bare == "0":
            zeros = zeros + spellings[name]
        if bare in seen:
            twice = True
        seen[bare] = 1
    if total != n_numeric or not twice or len(spellings) > _category_ceiling(
        frame
    ):
        raise _broken(
            "SC2",
            where,
            f"a census of {len(spellings)} spelling(s) counting {total} "
            "cell(s)",
            f"the column's {n_numeric} number cell(s), with one number "
            "written two ways",
        )
    if zeros != n_zero:
        raise _broken(
            "SC3",
            where,
            f"{zeros} cell(s) spelled as nought",
            f"n_zero is {n_zero}",
        )
    return spellings


def _layout_forms(
    mapping: "dict[str, object]", where: str, floor: int
) -> "dict[str, int]":
    """The census of LAYOUTS, checked key by key (7.12, plan P4-D120).

    A KEY CARRIES NO FIGURE AND NO LETTER OF THE TABLE, and it is
    checked here rather than assumed, for the reason `_shape_forms`
    gives: the producer builds a layout by replacing every figure and
    every letter, and a key where one survived is a key carrying a
    fragment of somebody's record number. A loader that accepted one
    would let a producer -- or a hand-edited file -- put a real
    identifier into the one field this role has for saying what its
    values look like.

    The line governs a named layout as it governs a level, and the
    `(withheld)` pool takes what it holds back. AND NO COUNT OF ONE
    REACHES A READER BY SUBTRACTION EITHER (C6-131b, plan P4-D124): the
    census is checked against the three totals a reader holds beside it.

    AND NO LAYOUT WITH A SMALL SUPPLY IS NAMED (C6-130, LF7, plan
    P4-D260). The rule is over PUBLISHED facts alone -- the key's own
    supply, `n_distinct` and the floor are all on the page -- so the
    loader asks it exactly as the producer does, with
    `parsing.layout_supply` and not `parsing.layout_room`: the supply is
    how many cells could have been COUNTED under the key, and on a key of
    figures alone the zero fill takes the leading noughts into a key of
    their own. Measured before this check: 900 record numbers `100` to
    `999` at a floor of eleven published `{"%%%": 900}` beside
    `n_distinct` 900, and the census then named every cell that could
    wear the layout, which is the source's own value set.

    Raises ProfileError for a wrong type, a key that is not a layout, a
    key longer than the limit, a named layout below the line, a named
    layout with a small supply, a pool of
    one, a census that leaves one cell over against a total, and keys
    built under two conventions.
    """
    layouts = _counts(mapping["layout_forms"], "layout_forms", where, 1)
    counted = 0
    for name in sorted(layouts):
        counted = counted + layouts[name]
    present = _whole(mapping["n_present"], "n_present", where, 0)
    if counted > present:
        # LF3. AT MOST, AND NOT EXACTLY, on SF3's own reasoning: a cell
        # this census does not describe -- one too long, one holding a
        # space it may not hold, one of marks alone -- is counted
        # nowhere at all, so the sum falls short on any column holding
        # one and only an upper bound is checkable here.
        raise _broken(
            "LF3",
            where,
            f"the census counts {counted} cells",
            f"the column holds {present} present cells",
        )
    line = parsing.census_floor(floor)
    distinct = _whole(mapping["n_distinct"], "n_distinct", where, 0)
    needed = distinct + floor
    for name in sorted(layouts):
        if name == WITHHELD:
            # THE POOL IS THE FLOOR'S OWN, AND AT A FLOOR OF ONE THERE
            # IS NONE. That rule is C5-S13's and is checked before any
            # column block is read; `layout_forms` is in its list, so a
            # rule of this function's own would be unreachable. What is
            # this function's own is the pool's SIZE.
            if layouts[name] < 2:
                raise _broken(
                    "LF2",
                    where,
                    f"the pool holds {layouts[name]} cell",
                    "a pool is written only where it holds two or more",
                )
            continue
        if not _is_layout_form(name):
            raise _out_of_range(
                f"layout_forms -> {name}",
                where,
                "a key of that shape",
                "a layout: a figure written '%', a nought of a zero fill "
                "written '!' in a run before the figures of a key of "
                "figures alone, an upper-case letter '@', a lower-case "
                "letter '&', a hexadecimal character '~' or '^', and "
                "between them only the marks - . / _ : # * ( ) [ ] "
                "+ , { } and single spaces inside the key -- carrying at "
                "least one placeholder",
            )
        if layouts[name] < line:
            raise _broken(
                "LF1",
                where,
                f"the layout '{name}' was written by {layouts[name]} cells",
                f"the line is {line}: the smallest group size, and never "
                "under two",
            )
        if parsing.layout_supply(name) < needed:
            raise _broken(
                "LF7",
                where,
                (
                    f"the layout '{name}' could have been worn by "
                    f"{parsing.layout_supply(name)} different cells"
                ),
                (
                    f"the column has {distinct} different values, and with "
                    f"the smallest group size of {floor} a layout naming "
                    f"fewer than {needed} names the values it describes"
                ),
            )
    _layout_conventions_agree(layouts, where)
    # LF4 AND LF5 ASK THE PRODUCER'S OWN QUESTION, `parsing.
    # census_names_one_row` (plan P4-D150), and so an EMPTY census is
    # asked nothing (plan P4-D152): it covers no cell, leaves a reader
    # nothing to subtract, and is what the producer writes for a column
    # of one present cell. Refusing it told a person their unchanged
    # description had been edited.
    if parsing.census_names_one_row({}, [(present, counted)]) == 0:
        raise _broken(
            "LF4",
            where,
            f"the census counts {counted} cells",
            f"the column holds {present} present cells, one more",
        )
    totals = [
        (
            "n_code_alphabet",
            _whole(mapping["n_code_alphabet"], "n_code_alphabet", where, 0),
            _LAYOUT_CODE_MARKS,
        ),
    ]
    if not _layout_is_hexadecimal(layouts):
        totals += [
            (
                "n_all_digits",
                _whole(mapping["n_all_digits"], "n_all_digits", where, 0),
                _LAYOUT_FIGURE_MARKS,
            )
        ]
    for total_name, total, marks in totals:
        covered = 0
        for name in sorted(layouts):
            if name == WITHHELD or not _layout_within(name, marks):
                continue
            covered = covered + layouts[name]
        if parsing.census_names_one_row({}, [(total, covered)]) == 0:
            raise _broken(
                "LF5",
                where,
                f"the layouts inside that alphabet count {covered} cells",
                f"{total_name} is {total}, one more",
            )
    return layouts


def _layout_prefixes(
    mapping: "dict[str, object]",
    where: str,
    layouts: "dict[str, int]",
    n_distinct: int,
    floor: int,
) -> "dict[str, str]":
    """The literal prefixes of a declared column, checked (7.12a).

    OWNER RULING OF 2026-09-17, ITEM 1. The one text of the table an
    identifier block may carry is the literal opening every present cell
    -- or every cell of one named layout -- shares, and it is checked
    here rather than trusted, because it is text: a value that is not a
    prefix `parsing.is_a_literal_prefix` admits, or a key that is neither
    `(column)` nor a named layout, is a hand-edited document that could
    carry a record number in the one field allowed text.

    NO REFUSAL QUOTES A PREFIX. It is text out of the table, and a
    refusal names the key and the layout it stands under instead.

    AND LP3, THE ROOM THE PREFIX LEAVES (plan P4-D270). `layout_census`
    names a layout only where it could have come from `n_distinct` plus
    the floor different cells; a published prefix fixes characters of
    that layout, so the count that has to clear the line is the one
    `parsing.prefix_room` gives. `@@@%%%` beside `REC` leaves a thousand
    cells, and a document publishing them beside `n_distinct 1000` spells
    out every record number the column holds -- so it is refused here and
    the producer writes no prefix in its place.

    Raises ProfileError for a wrong type, a prefix that is not one, and
    LP1, LP2 and LP3. That a `(column)` prefix stands on a column reaching
    the line needs no check of its own: LP1 puts it beside a named layout,
    and LF1 puts that layout's cells, all of them present, at the line.
    """
    found = _mapping(mapping["layout_prefixes"], "layout_prefixes", where)
    prefixes: "dict[str, str]" = {}
    for scope in sorted(found):
        text = found[scope]
        if not isinstance(text, str) or not parsing.is_a_literal_prefix(text):
            raise _out_of_range(
                "layout_prefixes",
                where,
                "an entry that is not a prefix",
                "a literal prefix: ASCII letters, the marks - . / _ : # * "
                "( ) [ ] + , { } and single spaces inside it, with at "
                "least one letter and no figure",
            )
        prefixes[scope] = text
    if not prefixes:
        return prefixes
    named: "list[str]" = []
    for name in sorted(layouts):
        if name != WITHHELD:
            named += [name]
    if not named:
        raise _broken(
            "LP1",
            where,
            f"{len(prefixes)} prefix(es) published",
            "the layout census names no layout",
        )
    if parsing.PREFIX_OF_THE_COLUMN in prefixes and len(prefixes) > 1:
        raise _broken(
            "LP1",
            where,
            f"a prefix for the whole column beside {len(prefixes) - 1} "
            "for layouts",
            "the whole column's prefix is written alone",
        )
    # A HEXADECIMAL CENSUS CARRIES A PREFIX TOO (plan P4-D233). It was
    # refused here while `parsing.literal_prefix` wrote none for such a
    # column; the prefix is now read under rule 3, which in a column
    # whose every letter is a figure of base sixteen ends it at a mark,
    # and LP2 below checks it against the census's own marks.
    convention = _layout_census_convention(layouts)
    for scope in sorted(prefixes):
        governed = named
        if scope != parsing.PREFIX_OF_THE_COLUMN:
            if scope not in named:
                raise _broken(
                    "LP1",
                    where,
                    "a prefix published for a layout the census does not "
                    "name",
                    f"the census names {len(named)} layout(s)",
                )
            governed = [scope]
        opening = parsing.prefix_layout(prefixes[scope], convention)
        for layout in governed:
            after = layout[len(opening):]
            if layout[: len(opening)] != opening or not _holds_a_placeholder(
                after
            ):
                raise _broken(
                    "LP2",
                    where,
                    f"the layout '{layout}' does not open with the "
                    "prefix's own layout",
                    "a prefix opens every layout it is published for",
                )
            if not parsing.prefix_leaves_room(
                layout, prefixes[scope], convention, n_distinct, floor
            ):
                raise _broken(
                    "LP3",
                    where,
                    (
                        f"the layout '{layout}' spells "
                        f"{parsing.prefix_room(layout, prefixes[scope], convention)}"
                        " different cells once the prefix is fixed"
                    ),
                    (
                        f"the column holds {n_distinct} different values, "
                        f"and a shape is named only where it leaves room "
                        f"for {n_distinct + floor}"
                    ),
                )
    return prefixes


def _holds_a_placeholder(text: str) -> bool:
    """Whether a stretch of a layout marks at least one figure or letter."""
    for character in text:
        if character in "%!@&~^":
            return True
    return False


# The characters a layout key may hold for every cell wearing it to lie
# inside the alphabet `n_code_alphabet` counts, and inside the one
# `n_all_digits` counts (C6-131b).
_LAYOUT_CODE_MARKS = "%@&~^!-_"
_LAYOUT_FIGURE_MARKS = "%!"


def _layout_within(name: str, marks: str) -> bool:
    """Whether every character of a key is one of ``marks``."""
    for character in name:
        if character not in marks:
            return False
    return True


def _layout_is_hexadecimal(layouts: "dict[str, int]") -> bool:
    """Whether any key of a census carries a hexadecimal mark."""
    for name in sorted(layouts):
        for character in name:
            if character == "~" or character == "^":
                return True
    return False


def _layout_census_convention(layouts: "dict[str, int]") -> str:
    """The alphabet convention a published layout census was built under.

    Read off the keys and off nothing else, exactly as the generator
    reads it (`generation._layout_convention`): one hexadecimal mark
    anywhere settles the column, and LF6 has already refused a census
    whose keys say two conventions. It is needed so that LP2 asks a
    prefix's own marks of the census's own marks (plan P4-D233).
    """
    for name in sorted(layouts):
        for character in name:
            if character == parsing.LAYOUT_LOWER_HEX:
                return parsing.LAYOUT_HEX_LOWER
            if character == parsing.LAYOUT_UPPER_HEX:
                return parsing.LAYOUT_HEX_UPPER
    return parsing.LAYOUT_PLAIN


def _layout_conventions_agree(
    layouts: "dict[str, int]", where: str
) -> None:
    """LF6: every key of one census was built under ONE convention.

    The producer decides the convention once for the whole column
    (C6-128), and the generator reads it back off the keys, so a census
    whose keys say two conventions -- `~` beside `^`, a hexadecimal mark
    beside a case letter, or a hexadecimal mark beside a zero fill, which
    only a plain column writes -- is one no producer wrote and no
    generator can read one way.
    """
    seen = ""
    for name in sorted(layouts):
        if name == WITHHELD:
            continue
        for character in name:
            if character == "~":
                kind = "lower-hexadecimal"
            elif character == "^":
                kind = "upper-hexadecimal"
            elif character in "@&!":
                kind = "plain"
            else:
                continue
            if seen and kind != seen:
                raise _broken(
                    "LF6",
                    where,
                    f"one key is written {seen}",
                    f"another is written {kind}",
                )
            seen = kind


def _is_layout_form(name: str) -> bool:
    """Whether one census key is a layout -- asked of the ONE definition.

    `parsing.is_a_layout_form` is that definition, and this loader must
    not hold a second reading of it: the form census learned at cost
    what happens when the producer, the loader and the publication
    guard each read the same rule for themselves (review round 2
    finding 2).
    """
    return parsing.is_a_layout_form(name)


def _is_shape_form(name: str) -> bool:
    """Whether one census key is a form -- asked of the ONE definition.

    THE LOADER MUST NOT HOLD A SECOND READING OF THIS RULE. It did, and
    the two parted: the producer refuses a key of one kind of symbol
    and this accepted `AAAA`, `9999` and `----`, so a document
    carrying one loaded, passed the publication guard, and then missed
    its own census at every recount because no cell can ever wear such
    a form (review round 2 finding 2).

    `parsing.is_a_written_form` is that definition. Calling it also
    carries the property finding 1 turned on: a key is spelled from
    placeholders no cell that has a form may contain, so admitting a
    key can never admit a value.
    """
    return parsing.is_a_written_form(name)


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


def _is_a_clock_value(text: object, form: str) -> bool:
    """Whether one published value is a clock time in one form.

    Two digits a field, the separators where the form puts them, hours
    to 23 and minutes and seconds to 59 -- invariant T1, asked of every
    one of the thirteen clock values a block publishes.

    Built out of character comparisons rather than string methods: the
    offline audit refuses a method call on a value it cannot trace to
    text, and a value read out of somebody's document is exactly such a
    value.
    """
    if not isinstance(text, str):
        return False
    if form == CLOCK_FORMS[0]:
        if len(text) != 5 or text[2] != ":":
            return False
    else:
        if len(text) != 8 or text[2] != ":" or text[5] != ":":
            return False
        seconds = _digits_at(text, 6, 2)
        if seconds is None or int(seconds) > 59:
            return False
    hours = _digits_at(text, 0, 2)
    minutes = _digits_at(text, 3, 2)
    if hours is None or minutes is None:
        return False
    return int(hours) <= 23 and int(minutes) <= 59


def _clock_value(
    value: object, key: str, where: str, form: str
) -> str:
    """One published clock time, checked against the column's own form."""
    if not _is_a_clock_value(value, form):
        # T1, raised in the invariant's own words rather than as a
        # range error: what is wrong is not that one entry holds an odd
        # value, it is that the block publishes a time in a form its
        # own cells did not wear, and a reader is owed that sentence.
        raise _broken(
            "T1",
            where,
            f"the entry called '{key}' does not hold a time of day "
            "written that way",
            f"this column's times are written as {_clock_shape_said(form)}",
        )
    return f"{value}"


def _clock_shape_said(form: str) -> str:
    """The form named in the words a person reads."""
    if form == CLOCK_FORMS[0]:
        return "two digits for the hour and two for the minute, `09:30`"
    return (
        "two digits each for the hour, the minute and the second, "
        "`09:30:00`"
    )


def _clock_ladder(
    value: object, key: str, where: str, form: str
) -> "dict[str, str]":
    """The eleven rungs of a column of clock times (contract 5.6).

    Guarantees: accepts the value under ``key`` and the form the column
    publishes; returns the ladder as a mapping from rung name to clock
    text. Raises ProfileError when it is not a block of entries (R15),
    when its keys are not exactly the eleven rungs (L4), when a rung
    holds nothing -- a rung of a clock ladder is never null -- when a
    rung is not a clock time in this column's form (T1), or when the
    rungs go DOWN (T3).

    T3 IS A PLAIN TEXT COMPARISON, and that is sound rather than
    convenient: both forms are fixed width and zero padded, so
    comparing the written rungs character by character puts them in the
    same order their ordinals do. It is checked only after T1 has
    passed on the rung, because the equivalence rests on the shape.
    """
    mapping = _mapping(value, key, where)
    _keys(mapping, where, LADDER_KEYS, "every ladder of clock times")
    ladder: "dict[str, str]" = {}
    previous = ""
    previous_name = ""
    for name in LADDER_KEYS:
        rung = mapping[name]
        if rung is None:
            raise _broken(
                "T1",
                where,
                f"the rung '{name}' of {key} holds nothing",
                "a ladder of clock times has a time at every rung",
            )
        found = _clock_value(rung, f"{key} -> {name}", where, form)
        ladder[name] = found
        if previous and found < previous:
            raise _broken(
                "T3",
                where,
                f"the rung '{previous_name}' of {key} is {previous}",
                f"the rung '{name}' after it is {found}",
            )
        previous = found
        previous_name = name
    return ladder


def _clock_facts(
    mapping: "dict[str, object]",
    where: str,
    frame: _Frame,
    n_present: int,
) -> ClockFacts:
    """Read a clock block (contract section 6, the clock role).

    The form is read FIRST, because every other value of the block is
    checked against it: a ladder rung is a clock time in THIS column's
    form, and asking that question without the form first would either
    accept both shapes or invent one.

    The five invariants, each raised in the words of the rule it broke:
    T1 every published clock value is written in the column's own form;
    T2 the ladder's two ends ARE the endpoints; T3 the rungs never go
    backwards; T4 some cell parsed; T5 enough of them did.
    """
    form = _one_of(mapping["clock_form"], "clock_form", where, CLOCK_FORMS)
    earliest = _clock_value(mapping["earliest"], "earliest", where, form)
    latest = _clock_value(mapping["latest"], "latest", where, form)
    ladder = _clock_ladder(
        mapping["clock_percentiles"], "clock_percentiles", where, form
    )
    # T2. Both ends of the ladder ARE the endpoints. Untied, a twin
    # pinned to the ladder could hold values earlier than the earliest
    # this description publishes.
    if ladder["min"] != earliest:
        raise _broken(
            "T2",
            where,
            f"the ladder of clock times begins at {ladder['min']}",
            f"the column's earliest time is {earliest}",
        )
    if ladder["max"] != latest:
        raise _broken(
            "T2",
            where,
            f"the ladder of clock times ends at {ladder['max']}",
            f"the column's latest time is {latest}",
        )
    unparsed = _whole(mapping["n_unparsed"], "n_unparsed", where, 0)
    # T4. Some cell parsed, and this is NOT implied by T5: at a parse
    # rate of zero the line is zero and T5 says nothing, and this is
    # then the only rule keeping a cell for the endpoints to be values
    # of.
    if unparsed >= n_present:
        raise _broken(
            "T4",
            where,
            f"{unparsed} of this column's values are not clock times",
            f"the column holds {n_present} values in all",
        )
    # T5. Enough of them parsed -- the parse line, applied as a COUNT
    # and never as a compared share, exactly as the producer applied it.
    line = _line_count(frame.parse_rate, n_present)
    if n_present - unparsed < line:
        raise _broken(
            "T5",
            where,
            f"{n_present - unparsed} of this column's values are clock times",
            f"at least {line} of them had to be for it to be read this way",
        )
    return ClockFacts(
        clock_form=form,
        earliest=earliest,
        latest=latest,
        clock_percentiles=ladder,
        n_unparsed=unparsed,
    )


def _identifier_facts(
    mapping: "dict[str, object]",
    where: str,
    n_present: int,
    n_distinct: int,
    floor: int,
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
    layouts = _layout_forms(mapping, where, floor)
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
        layout_forms=layouts,
        layout_prefixes=_layout_prefixes(
            mapping, where, layouts, n_distinct, floor
        ),
    )


def _exact_ratio(share: float) -> "tuple[int, int]":
    """One rate as the exact pair of whole numbers it really is.

    THE PRODUCER'S OWN RULE AGAIN, and written again for the same
    reason the line itself is. A rate recorded as `0.01` is not one
    hundredth: the nearest binary64 to one hundredth sits a shade above
    it, and a line computed by multiplying in binary64 rounds the
    product back down, so a document the producer refuses is one the
    loader accepts. Every binary64 is a whole number times a power of
    two, which is what `frexp` hands back.

    Guarantees: accepts a rate of zero or more; returns a numerator and
    a denominator whose quotient IS the rate. Determinism: a function
    of the rate. Raises TypeError if handed anything that is not a
    float instance, and ValueError for a negative rate. No I/O.
    """
    if not isinstance(share, float):
        raise TypeError("a rate reached the count rule as something else")
    if share < 0.0:
        raise ValueError("a rate reached the count rule below zero")
    fraction, power = math.frexp(share)
    numerator = int(fraction * float(1 << 53))
    place = power - 53
    if place >= 0:
        return numerator << place, 1
    return numerator, 1 << -place


def _line_count(share: float, total: int) -> int:
    """The smallest whole number of values that reaches ``share``.

    THE PRODUCER'S OWN RULE, written again here rather than imported:
    the loader may not import the describing side, and a threshold
    applied as a count on one side and as a compared share on the other
    is a threshold two implementations disagree about at the boundary.
    A count is what both apply.

    AND THE PRODUCT IS EXACT ON BOTH SIDES, which for a while it was on
    only one (review item P4-DATE2-F1). Writing the rule twice is what
    keeps the two sides independent; it is also what let one of them be
    repaired alone, and a loader that admits a description the producer
    would never write is a loader that admits a forged one. The rate is
    carried as the whole numbers it stands for and the ceiling is taken
    there, with no rounding left to happen.
    """
    numerator, denominator = _exact_ratio(share)
    exact = numerator * total
    whole = exact // denominator
    if whole * denominator < exact:
        return whole + 1
    return whole


def _joined_facts(
    mapping: "dict[str, object]",
    where: str,
    frame: _Frame,
    n_present: int,
) -> JoinedFacts:
    """Read a joined-number block (contract 6.13, plan P4-D21).

    Six invariants, and each one is a fact the producer cannot have
    written otherwise:

    - J1: `separator` is ONE character of the admitted list. A longer
      one, or one outside the list, describes a split this format does
      not perform.
    - J2: `n_parts` is at least two. One part is a bare number, which
      is a different role.
    - J3: `n_joined` and `n_unparsed` are a partition of the present
      cells, and `n_joined` clears the detection line -- the role was
      given because that many cells split this way, so a block claiming
      it with fewer describes a column the producer would have declined.
    - J4: `parts` and `part_min_widths` each hold exactly `n_parts`
      entries, in cell order.
    - J5: every part block is read by the SAME reader every
      quantitative role's block is read by, over `n_joined` values.
    - J6: every published width is at least one character.
    - J7: every agreement is a rank agreement, so it lies in -1..1, and
      there is exactly one for each PAIR of positions.
    - J8: every above-count is a number of rows that split, and there
      is exactly one for each pair.
    """
    separator = _text(mapping["separator"], "separator", where)
    if not _is_a_joined_separator(separator):
        raise _out_of_range(
            "separator", where, f"'{separator}'",
            "one of the marks this format splits a joined cell on, with "
            "at most one space on each side of it",
        )
    n_parts = _bounded(
        mapping["n_parts"], "n_parts", where, 2, n_present + 2,
        "at least two numbers in a cell",
    )
    n_joined = _bounded(
        mapping["n_joined"], "n_joined", where, 0, n_present,
        "the number of values the column holds",
    )
    n_unparsed = _bounded(
        mapping["n_unparsed"], "n_unparsed", where, 0, n_present,
        "the number of values the column holds",
    )
    if n_joined + n_unparsed != n_present:
        raise _out_of_range(
            "n_joined", where, f"a total of {n_joined + n_unparsed}",
            f"a total of {n_present}, the number of values the column "
            "holds: every present cell either splits this way or does not",
        )
    line = _line_count(frame.parse_rate, n_present)
    if n_joined < line:
        raise _out_of_range(
            "n_joined", where, f"{n_joined}",
            f"at least {line}, the number of this column's values that "
            "had to split into whole numbers for it to be read this way "
            "at all",
        )
    widths_read = _listing(
        mapping["part_min_widths"], "part_min_widths", where
    )
    if len(widths_read) != n_parts:
        raise _out_of_range(
            "part_min_widths", where, f"{len(widths_read)} width(s)",
            f"{n_parts}, one for each number in a cell",
        )
    widths: "list[int]" = []
    place = 0
    for value in widths_read:
        widths += [
            _bounded(
                value, f"part_min_widths[{place}]", where, 1, 4096,
                "a width of at least one character",
            )
        ]
        place = place + 1
    blocks_read = _listing(mapping["parts"], "parts", where)
    if len(blocks_read) != n_parts:
        raise _out_of_range(
            "parts", where, f"{len(blocks_read)} block(s)",
            f"{n_parts}, one for each number in a cell",
        )
    pairs = (n_parts * (n_parts - 1)) // 2
    agreements_read = _listing(
        mapping["part_agreements"], "part_agreements", where
    )
    if len(agreements_read) != pairs:
        raise _out_of_range(
            "part_agreements", where, f"{len(agreements_read)}",
            f"{pairs}, one for each pair of numbers in a cell",
        )
    agreements: "list[float]" = []
    place = 0
    for value in agreements_read:
        # J7. An agreement is a rank agreement and cannot leave -1..1.
        found = _figure(value, f"part_agreements[{place}]", where)
        if found < -1.0 or found > 1.0:
            raise _out_of_range(
                f"part_agreements[{place}]", where, f"{found}",
                "a number from -1 to 1, as a rank agreement is",
            )
        agreements += [found]
        place = place + 1
    above_read = _listing(mapping["part_above"], "part_above", where)
    if len(above_read) != pairs:
        raise _out_of_range(
            "part_above", where, f"{len(above_read)}",
            f"{pairs}, one for each pair of numbers in a cell",
        )
    above: "list[int]" = []
    place = 0
    for value in above_read:
        # J8. A count of rows cannot exceed the rows that split.
        above += [
            _bounded(
                value, f"part_above[{place}]", where, 0, n_joined,
                "the number of values that split into whole numbers",
            )
        ]
        place = place + 1
    blocks: "list[NumericFacts]" = []
    place = 0
    for value in blocks_read:
        seat = f"parts[{place}]"
        block = _mapping(value, seat, where)
        _keys(block, where, NUMERIC_KEYS, f"the block for {seat}")
        blocks += [
            _numeric_facts(
                block,
                f"{where}, {seat}",
                frame,
                n_joined,
                n_joined,
                0,
                0,
                echoes=n_joined,
            )
        ]
        place = place + 1
    return JoinedFacts(
        parts=tuple(blocks),
        separator=separator,
        n_parts=n_parts,
        n_joined=n_joined,
        n_unparsed=n_unparsed,
        part_min_widths=tuple(widths),
        part_agreements=tuple(agreements),
        part_above=tuple(above),
    )


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
    # THE OTHER WRAPPERS (plan P4-D36), read before AF1 because AF1 is
    # stated over the whole set.
    variants = _affix_variants(mapping, where, frame)
    if not prefix and not suffix and not variants:
        # AF1. A pair with nothing on either side describes no shape,
        # and a cell wearing it is a bare number, which is a different
        # role. WHERE THERE ARE OTHER WRAPPERS the bare one is a
        # member of the vocabulary rather than the whole of it: a
        # laboratory column of `13.5`, `4.2 H` and `9.8 L` wears three
        # and the commonest may be the bare one.
        raise _out_of_range(
            "affix_prefix", where, "two empty spellings",
            "at least one side carrying text, or another wrapper "
            "beside this one that does",
        )
    carrying = bool(prefix) or bool(suffix)
    for one in variants:
        if one.prefix or one.suffix:
            carrying = True
    if not carrying:
        raise _out_of_range(
            "affix_prefix", where, "wrappers that all carry nothing",
            "at least one wrapper carrying text, because a column "
            "whose every cell wears nothing is a column of bare "
            "numbers and that is a different role",
        )
    # AF14. NO WRAPPER IS NAMED TWICE ACROSS THE WHOLE VOCABULARY
    # (review round 1 of the wrapper set, item 8). AF9 orders the
    # variants and so refuses a duplicate AMONG them, and the commonest
    # pair is read here rather than there -- so a variant repeating the
    # pair this block already names passed both. Two entries for one
    # wrapper are two counts of one thing, and the count of cells
    # wearing the commonest would then be the column's total less a
    # slice of itself.
    for one in variants:
        if (one.prefix, one.suffix) == (prefix, suffix):
            raise _out_of_range(
                "affix_variants", where,
                f"the wrapper {prefix!r}/{suffix!r} named twice",
                "each wrapper named once, the commonest one under "
                "`affix_prefix` and `affix_suffix` and every other "
                "under `affix_variants`",
            )
    # AF15. A SET OF WRAPPERS IS NOT LARGER THAN A SET OF CATEGORIES
    # MAY BE. The wrappers are published text drawn from the table, so
    # what bounds how many of them may be named is what bounds how many
    # levels a categorical column may name. Without it a column of a
    # thousand one-off units published a thousand spellings under a key
    # nothing bounded.
    ceiling = _category_ceiling(frame)
    if len(variants) + 1 > ceiling:
        raise _out_of_range(
            "affix_variants", where,
            f"{len(variants) + 1} wrappers",
            f"no more than {ceiling}, the most different published "
            "spellings a column of this table may name",
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
    # AF12. THE COMMONEST WRAPPER'S OWN POPULATION (plan P4-D37). The
    # column's block is that wrapper's, so what it is checked against
    # is that wrapper's counts: the column's totals less every other
    # wrapper's. A column wearing ONE wrapper has nothing to subtract
    # and is read exactly as it was, against the present cells and the
    # table's row count.
    worn_by_others = 0
    numeric_elsewhere = 0
    out_elsewhere = 0
    contradictory_elsewhere = 0
    for one in variants:
        worn_by_others = worn_by_others + one.count
        numeric_elsewhere = numeric_elsewhere + one.n_core_numeric
        out_elsewhere = out_elsewhere + one.n_core_out_of_range
        contradictory_elsewhere = (
            contradictory_elsewhere + one.n_core_contradictory
        )
    text_elsewhere = 0
    for one in variants:
        text_elsewhere = text_elsewhere + one.n_core_not_numeric
    common_count = n_affixed - worn_by_others
    if variants and common_count < frame.floor:
        raise _out_of_range(
            "affix_variants", where,
            f"{worn_by_others} cell(s) wearing the other wrappers, "
            f"leaving {common_count} for the one this block names",
            f"at least {frame.floor} left for the commonest wrapper, "
            "because it is published like any other and a wrapper "
            "worn by fewer cells than may be named is not published "
            "at all",
        )
    # AF17. THE PAIR THIS BLOCK NAMES IS THE COMMONEST WRAPPER, and
    # nothing said so until review round 3 (item 5). The subtraction
    # above is nonnegative and closes, and a description can still be
    # written with the two populations SWAPPED: the block naming the
    # eighty cells wearing pounds and the entry naming the hundred and
    # twenty wearing kilograms. Such a document loaded, and the twin
    # built from it re-described with kilograms commonest and missed
    # twenty-one of its own obligations -- a description no producer
    # writes, accepted, and then failed by its own twin.
    #
    # THE TIE GOES THE PRODUCER'S WAY. Where a variant's count equals
    # the commonest's, the producer keeps whichever pair sorts first,
    # so an equal count is only admitted when the block's own pair
    # sorts before the entry's.
    for one in variants:
        if one.count > common_count or (
            one.count == common_count
            and (one.prefix, one.suffix) < (prefix, suffix)
        ):
            raise _out_of_range(
                "affix_variants", where,
                f"the wrapper {one.prefix!r}/{one.suffix!r} worn by "
                f"{one.count} cell(s) beside a commonest worn by "
                f"{common_count}",
                "the pair this block names to be the wrapper the most "
                "cells wear, ties going to the pair that sorts first, "
                "because that is the one a producer publishes there",
            )
    # AF10. HOW MANY DIFFERENT CORES, held inside the bounds a file
    # cannot argue with: a set of cores cannot hold more different
    # spellings than it has cells, and folding never separates two
    # spellings that were the same.
    #
    # THE CELLS ARE THE COMMONEST WRAPPER'S, NOT THE COLUMN'S (plan
    # P4-D37, and review round 1 item 8). These two counts belong to
    # the block above them, that block is the commonest wrapper's, and
    # bounding them by `n_affixed` let a description say a wrapper worn
    # by fifty cells holds two hundred different cores.
    #
    # AND AT LEAST ONE. A block whose numbers a file is held to
    # describes at least one core, so a published zero is a description
    # no column could have written; the bound was zero and a document
    # saying so loaded.
    core_distinct = _bounded(
        mapping["n_core_distinct"], "n_core_distinct", where,
        1, common_count,
        "the number of cells wearing the commonest wrapper",
    )
    core_distinct_folded = _bounded(
        mapping["n_core_distinct_folded"], "n_core_distinct_folded",
        where, 1, core_distinct,
        "the raw count of different cores",
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
    # AF16. EVERY ONE OF THE COMMONEST WRAPPER'S FOUR CLASS RESIDUALS
    # IS A COUNT, and they close on its own cell count (review round 2,
    # item 3). AF4 closes the column's four on `n_affixed` and AF11
    # closes each entry's four on its own count, and a document can
    # satisfy BOTH while leaving the commonest wrapper a negative
    # remainder: move two contradictory cores into a variant, call the
    # column's contradictory count zero and its not-numeric count two,
    # and AF4 still adds up. The commonest wrapper's contradictory
    # count is then `0 - 2`. Such a document loaded, and generation
    # stopped with the internal-check message that tells its user
    # synthtwin has a bug -- it had built 202 cells for a 200-row
    # description.
    residuals = (
        core_numeric - numeric_elsewhere,
        core_out_of_range - out_elsewhere,
        core_contradictory - contradictory_elsewhere,
        core_not_numeric - text_elsewhere,
    )
    for place in range(len(residuals)):
        if residuals[place] < 0:
            raise _out_of_range(
                _CORE_CLASS_KEYS[place], where,
                f"{residuals[place]} left for the commonest wrapper "
                f"once every other wrapper's count is taken from it",
                "a count of 0 or more, because the commonest wrapper's "
                "cells are the column's less the other wrappers' and "
                "no wrapper holds fewer than none",
            )
    left = residuals[0] + residuals[1] + residuals[2] + residuals[3]
    if left != common_count:
        raise _out_of_range(
            "n_core_numeric", where,
            f"a total of {left} for the commonest wrapper",
            f"a total of {common_count}, the number of cells wearing "
            "it, because its four classes are a partition of them "
            "exactly as AF4's are of every counted cell",
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
        # AGAINST THE COMMONEST WRAPPER'S OWN COUNT, which is the
        # count the sentence names (review round 8, item 3): it names
        # ONE spelling, so the number beside it is how many cells wear
        # THAT spelling and not how many wear any of them.
        if _is_the_affixed_remark(
            remark, common_count, _affix_clause(prefix, suffix)
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
            n_present if not variants else common_count,
            residuals[0],
            residuals[1],
            residuals[2],
            echoes=None if not variants else common_count,
        ),
        affix_prefix=prefix,
        affix_variants=variants,
        n_core_distinct=core_distinct,
        n_core_distinct_folded=core_distinct_folded,
        affix_suffix=suffix,
        n_affixed=n_affixed,
        n_core_numeric=core_numeric,
        n_core_out_of_range=core_out_of_range,
        n_core_contradictory=core_contradictory,
        n_core_not_numeric=core_not_numeric,
    )


def _a_label_and_not_a_number(
    spelling: str, where: str, decimal_comma: bool
) -> None:
    """Refuse a published label of a compound column that is a number.

    The split rule of section 5.2 puts a cell in the label half exactly
    when it does not read as a plain number, so a label that IS one
    describes a cell of the other half. A description carrying one is
    a description no file can satisfy: its twin writes that spelling,
    and re-describing the twin counts the cell into the numeric half.
    """
    read = spelling
    if decimal_comma:
        read = parsing.written_with_a_decimal_comma(spelling)
    if parsing.classify_number(read) != parsing.NUMBER:
        return
    raise _out_of_range(
        "labels -> levels",
        where,
        "a published label that reads as an ordinary number",
        "a spelling that is NOT a number, because the rule that makes "
        "this role puts every cell reading as a number in the other "
        "half -- a label of this column is by definition a cell that "
        "does not",
    )


def _compound_facts(
    mapping: "dict[str, object]",
    where: str,
    frame: _Frame,
    n_present: int,
    n_distinct: int,
    n_distinct_folded: int,
    decimal_comma: bool,
) -> CompoundFacts:
    """A column of numbers beside labels (residual R-P4-13, landing L8).

    THE SUM IS CHECKED HERE AND NOT ASSUMED. Two counts that did not
    account for every present cell would be a description of part of a
    column, which outcome principle 5 forbids and review item P1-R6-F7
    deleted a rule for. A file whose counts do not add up is refused
    rather than repaired, on the same terms as every other arithmetic
    the loader holds.
    """
    numeric = _bounded(
        mapping["n_numeric_cells"],
        "n_numeric_cells",
        where,
        0,
        n_present,
        "the number of present cells",
    )
    labels = _bounded(
        mapping["n_label_cells"],
        "n_label_cells",
        where,
        0,
        n_present,
        "the number of present cells",
    )
    # BOTH HALVES HOLD SOMETHING, which is what this role IS. The
    # producer never writes an empty half -- rule 7b refuses a column
    # with one -- and the loader accepted it, so a plain numeric
    # description rewritten with `n_label_cells: 0` and an empty label
    # block was read as this role: a column whose statistical type says
    # two populations and whose twin has one (review round 2 of this
    # landing, item 3).
    # THE THIRD POPULATION (residual R-P4-149). Numerals this format
    # cannot hold. They used to be counted with the LABELS, which said
    # a number was a word; they are counted with the numeric half now,
    # and the sum below is three-way.
    unusable_out = _bounded(
        mapping["n_numeric_out_of_range"],
        "n_numeric_out_of_range",
        where,
        0,
        n_present,
        "the number of present cells",
    )
    unusable_contradictory = _bounded(
        mapping["n_numeric_contradictory"],
        "n_numeric_contradictory",
        where,
        0,
        n_present,
        "the number of present cells",
    )
    for count, key in ((numeric, "n_numeric_cells"), (labels, "n_label_cells")):
        if count == 0:
            raise _out_of_range(
                key,
                where,
                "0",
                "at least one cell, because a column of numbers beside "
                "labels holds both populations and a description of "
                "one of them is a description of some other kind of "
                "column",
            )
    total = numeric + unusable_out + unusable_contradictory + labels
    if total != n_present:
        raise _out_of_range(
            "n_numeric_cells",
            where,
            f"a total of {total} with n_numeric_out_of_range, "
            f"n_numeric_contradictory and n_label_cells",
            f"a total of exactly the {n_present} present cell(s) this "
            "column has, so that every one of them is in one published "
            "population and none is in two",
        )
    # THE NUMERIC HALF'S COUNTS OF DIFFERENT WRITTEN CELLS, held inside
    # two bounds a file cannot argue with: a half cannot hold more
    # different cells than it has cells, and the two halves together
    # cannot hold more than the column does. Folding never separates
    # two cells that were the same, so the folded count is at most the
    # raw one.
    numeric_distinct = _bounded(
        mapping["n_numeric_distinct"],
        "n_numeric_distinct",
        where,
        0,
        numeric,
        "the number of cells in the numeric half",
    )
    _bounded(
        mapping["n_numeric_distinct"],
        "n_numeric_distinct",
        where,
        0,
        n_distinct,
        "the number of different cells the whole column holds",
    )
    numeric_distinct_folded = _bounded(
        mapping["n_numeric_distinct_folded"],
        "n_numeric_distinct_folded",
        where,
        0,
        numeric_distinct,
        "the raw count of different cells in the numeric half",
    )
    # THE HALF'S WHOLE POPULATION: its numbers and its unusable
    # numerals (residual R-P4-149). The four class counts of the block
    # sum to this, exactly as they do on a plain numeric column.
    half = numeric + unusable_out + unusable_contradictory
    numbers = _numeric_facts(
        _mapping(mapping["numbers"], "numbers", where),
        f"{where} -> numbers",
        frame,
        half,
        numeric,
        unusable_out,
        unusable_contradictory,
        # THE ROW COUNT THIS BLOCK ECHOES IS THE HALF'S OWN, on the
        # joined role's precedent: a block that describes a SUBSET of
        # the column's cells echoes the count of that subset, and
        # holding it to the table's count is what made a joined column
        # with one unsplit cell unreadable by the tool that wrote it.
        echoes=half,
    )
    label_block = _mapping(mapping["labels"], "labels", where)
    # EXACTLY THESE KEYS IN EACH HALF, AND NO OTHERS. Without this a
    # sub-block carried whatever a file put in it: `raw_note: "Jane
    # Doe"` inside `labels` was ACCEPTED, survived the canonical
    # round trip, and was read by nothing -- so a description could
    # carry text nothing in this package ever looks at (review round 1
    # of this landing, item 2). Every other block of the description is
    # held to its key set, including each POSITION of a joined column,
    # and these two were the exception.
    _keys(
        _mapping(mapping["numbers"], "numbers", where),
        where,
        NUMERIC_KEYS,
        "the numeric half of a column of numbers beside labels",
    )
    _keys(
        label_block,
        where,
        COMPOUND_LABEL_KEYS,
        "the label half of a column of numbers beside labels",
    )
    # AND THE HALF'S OWN CELL COUNT IS THE SPLIT'S, which is invariant
    # NL2 and was stated in the contract and enforced nowhere: a file
    # publishing `n_label_cells: 20` beside `labels -> n_present: 999`
    # was accepted, and every fact of that half is stated over the
    # count it carries.
    _bounded(
        label_block["n_present"],
        "labels -> n_present",
        where,
        labels,
        labels,
        "the number of cells the split puts in the label half",
    )
    label_distinct = _bounded(
        label_block["n_distinct"],
        "labels -> n_distinct",
        where,
        1,
        labels,
        "the number of cells in the label half",
    )
    folded = _bounded(
        label_block["n_distinct_folded"],
        "labels -> n_distinct_folded",
        where,
        1,
        label_distinct,
        "the raw count of different cells in the label half",
    )
    # THE FOUR COUNTS OF DIFFERENT CELLS ARE ONE ARITHMETIC, and until
    # this they were four separate bounds that could each hold while
    # the set of them was impossible (review round 2 of this landing,
    # item 2). A file publishing ninety-seven different numeric cells
    # in the half and ONE in `n_numeric_distinct` cleared every bound
    # there was, and the generator writes ninety-seven whatever the
    # budget says.
    #
    # The two halves hold disjoint spellings -- a cell that reads as a
    # number is in the numeric half by the rule that made the column,
    # so no label cell can wear a numeric cell's folded identity -- so
    # the folded counts ADD. Measured before it was asserted, over
    # sixty generated compound columns of three shapes: readings that
    # repeat, values written two ways each, and exponents in both
    # cases. The equality held on every one.
    if (
        numeric_distinct_folded + folded != n_distinct_folded
        and n_distinct_folded > 0
    ):
        raise _out_of_range(
            "n_numeric_distinct_folded",
            where,
            f"a total of {numeric_distinct_folded + folded} with the "
            "label half's own count",
            f"a total of exactly the {n_distinct_folded} folded "
            "identities this column holds, because the two halves hold "
            "no spelling in common",
        )
    # AND THE HALF'S FOLDED COUNT IS AT LEAST ITS COUNT OF DIFFERENT
    # NUMBERS: two spellings of one value fold to two identities, and
    # two different values can never fold to one.
    if numeric_distinct_folded < numbers.n_distinct_values:
        raise _out_of_range(
            "n_numeric_distinct_folded",
            where,
            f"{numeric_distinct_folded}",
            f"at least the {numbers.n_distinct_values} different "
            "number(s) the numeric half holds, because two different "
            "numbers are never written the same way",
        )
    # ...and the column's own raw count is the two halves' counts
    # ADDED, now that both are published. It was a range between them
    # while the label half published only a folded count (review round
    # 3, item 5): every different numeric cell is a different cell of
    # the column, the two halves share no spelling, and nothing else
    # can contribute.
    if numeric_distinct + label_distinct != n_distinct:
        raise _out_of_range(
            "n_numeric_distinct",
            where,
            f"a total of {numeric_distinct + label_distinct} with the "
            "label half's own count",
            f"a total of exactly the {n_distinct} different cell(s) "
            "this column holds, because the two halves share no "
            "spelling and nothing else can add one",
        )
    # READ BY THIS HALF'S OWN READER, and the docstring beside it says
    # why the two readers already here would not do.
    label_facts = _compound_label_facts(
        label_block,
        f"{where} -> labels",
        frame.floor,
        labels,
        folded,
    )
    # W9 over the half's own count, which is the one P4-D276 moved here.
    _spellings_spoken(
        label_facts.levels,
        label_facts.suppressed_levels,
        label_facts.suppressed_rows,
        label_distinct,
        f"{where} -> labels",
    )
    # AND EVERY PUBLISHED LABEL IS A CELL THE SPLIT WOULD PUT IN THE
    # LABEL HALF (invariant NL5, review round 8 of this landing, item
    # 2). The rule that makes this role puts a cell in the label half
    # exactly when it does NOT read as a plain number, so a published
    # label spelled `1` describes a cell that belongs to the other
    # half. The loader checked the arithmetic of the split and never
    # what the halves HOLD: a description whose every label was `1` was
    # accepted, and its twin wrote 294 numeric-looking cells against a
    # published 274 -- a file that cannot be re-described as the
    # column it claims to be.
    #
    # Asked of the level's own spelling and of every published variant,
    # under the column's own grammar: a declared column reads `1,5` as
    # a number, so `1,5` is not a label of THAT column either.
    for level in label_facts.levels:
        _a_label_and_not_a_number(level.label, where, decimal_comma)
        for spelling in sorted(level.variants):
            _a_label_and_not_a_number(spelling, where, decimal_comma)
    return CompoundFacts(
        n_numeric_cells=numeric,
        n_numeric_out_of_range=unusable_out,
        n_numeric_contradictory=unusable_contradictory,
        n_label_cells=labels,
        n_numeric_distinct=numeric_distinct,
        n_numeric_distinct_folded=numeric_distinct_folded,
        n_label_distinct=label_distinct,
        n_label_distinct_folded=folded,
        numbers=numbers,
        labels=label_facts,
    )


def _text_facts(
    mapping: "dict[str, object]",
    where: str,
    n_present: int,
    n_distinct: int,
    floor: int,
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
        shape_forms=_shape_forms(mapping, where, floor, True),
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
        seen += [block.name]
        blocks += [block]
        index = index + 1
    return tuple(blocks)


def _group_marks_agree(
    columns: "tuple[ColumnBlock, ...]", settings: SettingsBlock
) -> None:
    """GS1: a mark between thousands agrees with the column's decimal mark.

    A `.` is the mark of a column declared to write its decimals with a
    comma, and a `,` never is: under that declaration the twin would
    write `23,648,37`, which no reader takes for a number. The other
    marks -- a space, an apostrophe, a no-break space -- are neither
    decimal mark, so they stand under either (landing 2b.2). Whether the
    declaration reaches a column is `a_decimal_comma_reaches`' answer and
    no other, so a labelled column's numbers may carry a `.` and so may
    the CORES of a declared affixed column since landing 2b.16, while a
    joined column's position never does (the first version refused the
    profiler's own labelled column: stage 2 closure). Asking the one
    predicate rather than listing roles here is what made that last
    change a change in one place.

    Guarantees: accepts every column and the settings; returns nothing.
    Raises ProfileError for GS1. No I/O of any kind.
    """
    for column in columns:
        facts = column.facts
        blocks: "list[NumericFacts]" = []
        if isinstance(facts, (NumericFacts,)):
            blocks += [facts]
        elif isinstance(facts, (AffixedFacts,)):
            blocks += [facts.numbers]
            for wrapper in facts.affix_variants:
                blocks += [wrapper.numbers]
        elif isinstance(facts, (CompoundFacts,)):
            blocks += [facts.numbers]
        elif isinstance(facts, (JoinedFacts,)):
            for part in facts.parts:
                blocks += [part]
        declared = (
            column.name in settings.forced_decimal_commas
            and a_decimal_comma_reaches(column)
        )
        for block in blocks:
            mark = block.group_separator
            # A POSITION OF A JOINED COLUMN is read from figures and one
            # point alone (landing 2b.2), so no mark, and no plus, can
            # stand in it: a block claiming either describes a column no
            # reading of this package produces.
            if isinstance(facts, (JoinedFacts,)) and mark != "":
                raise _broken(
                    "GS1",
                    f"in the block for the column named '{column.name}'",
                    "a position of two numbers in one cell groups its "
                    "thousands with a mark",
                    "a position is read from figures and one point alone",
                )
            if isinstance(facts, (JoinedFacts,)) and _added(block.decimal_plus) != 0:
                raise _broken(
                    "DP1",
                    f"in the block for the column named '{column.name}'",
                    f"{_added(block.decimal_plus)} numbers of one position carry a plus",
                    "a position is read from figures and one point alone",
                )
            # ...AND NEITHER MIXTURE CENSUS SPEAKS THERE EITHER (landing
            # 2b.7). A position is read from figures and one point
            # alone, so it wears no notation and no mark, and a census
            # naming either describes cells the reading cannot produce.
            if isinstance(facts, (JoinedFacts,)) and block.thousands_marks:
                raise _broken(
                    "TM1",
                    f"in the block for the column named '{column.name}'",
                    "the grouped numbers of one position are counted by "
                    "the mark they wore",
                    "a position is read from figures and one point alone",
                )
            if isinstance(facts, (JoinedFacts,)) and block.negative_notations:
                raise _broken(
                    "NS2",
                    f"in the block for the column named '{column.name}'",
                    "the negative numbers of one position are counted by "
                    "the notation they wore",
                    "a position is read from figures and one point alone",
                )
            if declared and mark == ",":
                raise _broken(
                    "GS1",
                    f"in the block for the column named '{column.name}'",
                    "the mark between thousands is a comma",
                    "the column is declared to write its decimals with a "
                    "comma",
                )
            if not declared and mark == ".":
                raise _broken(
                    "GS1",
                    f"in the block for the column named '{column.name}'",
                    "the mark between thousands is a point",
                    "only a column declared to write its decimals with a "
                    "comma groups with a point",
                )
            # TM1's LAST CLAUSE, asked after GS1 so a mark no reading
            # publishes is refused for that before it is refused for
            # being uncounted (the carried refusal test of landing 2b.2).
            census = block.thousands_marks
            if mark != "" and census and mark not in census:
                raise _broken(
                    "TM1",
                    f"in the block for the column named '{column.name}'",
                    f"the column groups its thousands with "
                    f"'{parsing.visible(mark)}'",
                    "the census of marks does not count that mark at all",
                )


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
    for name in settings.forced_codes:
        if name not in places:
            raise _broken(
                "S8",
                "in the block of rules that produced the description",
                f"'{name}' is named as holding codes",
                "this table has no column of that name",
            )
    for name in settings.forced_measurements:
        if name not in places:
            raise _broken(
                "S8",
                "in the block of rules that produced the description",
                f"'{name}' is named as holding measurements",
                "this table has no column of that name",
            )
    for name in settings.forced_decimal_commas:
        if name not in places:
            raise _broken(
                "S8",
                "in the block of rules that produced the description",
                f"'{name}' is named as writing its numbers with a comma",
                "this table has no column of that name",
            )
    _group_marks_agree(columns, settings)
    # AND NOT BESIDE A DECLARATION THAT WOULD SILENCE IT (review item
    # P4-G3-R3-F3). The contract forbids the overlap and nothing
    # enforced it, so a hand-written description could name a column
    # both a code and a decimal-comma column and be accepted -- and the
    # generator would then quietly not apply the comma, because a code
    # column carries no numeric facts. The command line refuses the
    # pair; a document carrying it is a document this contract does not
    # describe, and the loader is where that is settled.
    # S8b WAS BUILT HERE AND WITHDRAWN, and the reason is worth the
    # space because it looks enforceable and is not (review item
    # P4-G3-R8-F2).
    #
    # The thought was: on a column named `--decimal-comma`, an absent
    # spelling whose number depends on the reading came either from a
    # judged pass -- and then one of that column's own stand-in
    # verdicts names its number -- or from a declared value, which the
    # producer now refuses. Refuse the rest.
    #
    # THERE IS A THIRD SOURCE. A declaration the producer ALLOWS,
    # because its own number does not depend on the grammar, can still
    # match a cell whose spelling does: `--missing-value -999` is safe,
    # and on a declared column it matches cells spelled `-999,0` by
    # NUMBER, which is what the matching rule says it should do. That
    # column then publishes `-999,0` among its absent spellings,
    # legitimately, with no verdict to account for it -- and the rule
    # above turned it away. A correct description, refused.
    #
    # The three sources cannot be told apart from the document,
    # because a declaration is unrecoverable from it: the settings
    # block carries no spelling a person typed (C5-16). So the
    # producer is the gate, `profile.build_document` is where it
    # stands, and every path this package offers goes through it.
    for name in settings.forced_decimal_commas:
        for other, what in (
            (settings.forced_codes, "holding codes"),
            (settings.forced_identifiers, "holding record numbers"),
        ):
            if name not in other:
                continue
            raise _broken(
                "S8a",
                "in the block of rules that produced the description",
                f"'{name}' is named as writing its numbers with a "
                f"comma and also as {what}",
                "a column read as codes or as record numbers is not "
                "read as numbers at all, so the comma reading could "
                "never be used",
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
# B4 bounds `suppressed_rows` by `suppressed_levels` times one less than
# the floor and from below by `suppressed_levels` (a pooled total since
# the owner's ruling of 2026-09-17, plan P4-D201), `_multiplicity`
# reads `variants_withheld`'s keys against the range. The other two
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
            if (
                key == WITHHELD
                and _is_a_row_count(value)
                and not canonical.pools_at_any_floor(path)
            ):
                found += [(here, value, _POOLED)]
            if key == _NAMED_REMAINDER and _is_a_row_count(value):
                found += [(here, value, _POOLED)]
            if key == _UNNAMED_TALLY and _is_a_row_count(value):
                found += [(here, value, _TOO_RARE)]
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
            declared_codes=settings.forced_codes,
            declared_commas=settings.forced_decimal_commas,
            parse_rate=settings.minimum_parse_rate,
            category_share=settings.categorical_share,
            category_ceiling=settings.categorical_ceiling,
            category_floor=settings.categorical_floor,
        ),
    )
    _cross_checks(columns, settings, notes)
    _dialect_rules(
        source, columns, n_rows, settings.small_cell_floor,
        settings.forced_identifiers, settings.forced_metadata_rows,
        settings.forced_delimiter,
    )
    # ...and the same for a workbook, where the file was one (plan
    # P4-D77). Run beside the written form's rules and for the same
    # reason: every one of them needs the columns, the row count or the
    # floor, so none of them can be checked while the block is read.
    _workbook_rules(
        source, columns, n_rows, settings.small_cell_floor
    )
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


def _no_duplicate_keys(text: str, shown: str) -> None:
    """Refuse a document that names one key twice in one object.

    WHY THIS EXISTS SEPARATELY FROM `_round_tripped` (review item
    L17b-R1-2). A description is refused unless its bytes are exactly
    the bytes synthtwin writes, and that one check catches a duplicated
    key among six other defects. A QUESTIONS FILE cannot be held to
    that: it is handed to a person to edit, and an editor that
    re-indents on save would have their answers refused for the
    formatting. Removing the canonical check removed the duplicate-key
    protection with it, and a parse keeps only the LAST value -- so an
    entry holding `"column": "x"` followed by `"column": "y"` declares
    `y` a code and leaves `x` alone, with nothing said. Both names can
    be real columns, so no later check sees anything wrong.

    This is that one protection, on its own, so an edited file keeps
    every freedom of layout and loses only the ambiguity.

    Guarantees:

    - Inputs: the document's text, ALREADY KNOWN TO PARSE, and the path
      to name in a refusal. The order matters: the key literals are
      read with the same parser the document was read with, so a key
      written `"a"` and a key written `"\u0061"` are compared as the
      one key they are.
    - Determinism: the answer depends only on the text.
    - Errors raised: ProfileError naming the key and its object.
    - Boundary: string operations and `json.loads` on one key literal
      at a time. No callback slot is filled, and nothing is opened.

    The walk is string-literal aware for the reason `_scanned`'s is: a
    brace or a colon inside a quoted value is a character of that
    value. A key is a string literal that is followed, across
    whitespace, by a colon, while the innermost open container is an
    object.
    """
    seen: "list[dict[str, int]]" = []
    is_object: list[bool] = []
    inside = False
    escaped = False
    literal = ""
    pending = ""
    have_pending = False
    for character in text:
        if inside:
            literal = literal + character
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                inside = False
                pending = literal
                have_pending = True
            continue
        if character == '"':
            inside = True
            literal = '"'
            have_pending = False
            continue
        if character == "{":
            seen += [{}]
            is_object += [True]
            have_pending = False
            continue
        if character == "[":
            seen += [{}]
            is_object += [False]
            have_pending = False
            continue
        if character == "}" or character == "]":
            if seen:
                seen = seen[:-1]
                is_object = is_object[:-1]
            have_pending = False
            continue
        if character == ":":
            if have_pending and is_object and is_object[-1]:
                key = _parsed(pending, shown)
                if isinstance(key, str):
                    here = seen[-1]
                    if key in here:
                        raise errors.ProfileError(
                            errors.answers_names_one_key_twice(shown, key)
                        )
                    here[key] = 1
            have_pending = False
            continue
        if character == " " or character == "\t":
            continue
        if character == "\n" or character == "\r":
            continue
        have_pending = False


def load_answers(raw_path: str) -> "dict[str, object]":
    """Read one questions file, or refuse it (amendment A-P4-58).

    Guarantees:

    - Inputs: ``raw_path`` is the path a person typed after
      `--answers`. It passes `validate_local_path` before anything is
      opened, exactly as a description does, so a URL form, a shared
      network form and a Windows device form are refused lexically.
    - Determinism: the same bytes always give the same result.
    - Errors raised: ProfileError, with a plain-language message, for
      each way the file cannot be read at all; PathValidationError when
      the path is not a plain local one. Whether the CONTENT is a
      questions file is `asking.answers_in`'s question and not this
      one's.
    - Boundary: opens the one file it is given and nothing else. It
      builds no table path, and it is unreachable from `generate`.

    THREE OF THE DESCRIPTION'S CHECKS ARE NOT RUN HERE, and each is
    left out for the same reason. `_versioned` asks for a
    `profile_version`, which a questions file does not carry and is not
    a document of. `_round_tripped` asks that the bytes be exactly what
    synthtwin would have written -- which is right for a machine-written
    description and wrong for the one file in this product a person is
    HANDED IN ORDER TO EDIT: a text editor that re-indents on save, or
    a person who deletes a section they have finished with, would then
    have their answers refused for the formatting rather than read.
    `_validated` checks the profile contract, which this is not.

    What IS run is every bound that protects the parser itself -- the
    nesting depth and the numeric token length of `_scanned` -- because
    those bound what a hostile file can cost, and the file arriving
    from a person is exactly the file that might be one.
    """
    validated = validate_local_path(raw_path, purpose="questions file")
    place = pathlib.Path(validated)
    shown = f"{place}"
    if not place.exists():
        raise errors.ProfileError(errors.profile_file_missing(shown))
    if place.is_dir():
        raise errors.ProfileError(errors.profile_path_is_a_folder(shown))
    try:
        text = _read_text(place)
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
        document = _answers_mapping(_parsed(text, shown), shown)
        # AFTER the parse, so the key literals are known to be
        # well-formed and can be read with the same parser (review item
        # L17b-R1-2).
        _no_duplicate_keys(text, shown)
        return document
    except MemoryError as error:
        raise errors.ProfileError(
            errors.profile_out_of_memory(shown)
        ) from error


def _answers_mapping(
    parsed: object, shown: str
) -> "dict[str, object]":
    """The parsed questions file as a mapping, or a refusal."""
    if not isinstance(parsed, dict):
        raise errors.ProfileError(errors.answers_file_is_not_one(shown))
    return parsed


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

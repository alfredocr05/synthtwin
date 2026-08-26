"""Measure a written CSV against the description that describes it.

This is the measurement half of `synthtwin validate`, written to
`docs/spec/validation-method-v1.md` under the ratified Phase 3 plan
(`docs/plans/phase-3-product.md`), which governs on every conflict. It
produces an `Outcome` -- verdicts, listings and the census -- and
writes nothing. The quality report, the command and its exit codes are
the wiring phase's work; nothing here prints, opens an output, or knows
what a report looks like.

WHAT IT MEASURES WITH, AND WHY THAT MATTERS (V2.1). The recount is the
PROFILER'S OWN: this module reads the measured file with
`reading.read_table` and describes it with `profile.build_document`,
then compares that description to the one it was handed. It
re-implements no count. A second implementation of seventy-two recounts
beside the producer's would drift from it, and the disposition matrix's
EXACT-OBSERVABLE means "recounted from the written CSV" by the same
measurement the description was made with.

AND WHY THE FILE IS DESCRIBED TWICE (V2.4). Presence is BLANKNESS: a
twin writes every absent cell empty, so every cell holding anything at
all holds a value -- and a generated number can legitimately BE the text
of a built-in missing marker (method residual R-P2-13), which the
producer's own absence machinery would read as a hole. So the file is
described TWICE by the same producer over the same cells. The first
description is the file's OWN -- what `synthtwin profile` would write
about it -- and it decides how the cells read, which role the column is,
and what the disclosure gate of V5 lets a report say. The second is
taken over the blank/non-blank split, with absence pinned to blankness,
and every measurement whose input is the set of present cells is read
off it. The two never decide the same number: one owns which cells are
counted, the other owns how they read.

The version this replaces built one description and WITHHELD every
presence-dependent obligation of a column wherever the two readings of
presence disagreed. That let the measured file decide which of its own
checks ran: one cell spelling `NA` turned every level, distinctness and
suppression obligation of a column from a potential MISS into a
withholding, and a file carrying none of its published labels passed.
V2.4 sets the bound that broke -- no gap in the reconstruction may move
a verdict -- and that gap is closed here by MEASURING over the split
rather than by declining to.

THAT BOUND IS NOT MET IN FULL, AND SAYING IT WAS COST FIVE VERDICTS
(review items P3-V4-F1 and P3-V5-F2; plan amendment A-P3-15). The
"reconstruction" is not one thing. Two of its parts are faithful
wherever the description publishes what they need -- which cells are
present, taken from blankness, and the two DECLARATION tuples of V2.2.
The part that is NOT faithful is a declaration the description publishes
nowhere, and the split is taken only where the file's own description
publishes the split (V2.4-A3), so a spelling the recovery misses is a
spelling that description reads as a hole, and the gate then closes on
a file that meets every published fact. No sentence in this module may
say the bound is met while that stands.

AND WHERE IT IS NOT MET, THE REPORT SAYS SO INSTEAD OF PRINTING A
FAILURE IT CANNOT SUPPORT (owner ruling 2026-08-16; plan amendment
A-P3-26; validation method V2.4-A5 and V3.5-A3). The MISSED verdicts
that used to be put on a table that is its own description's perfect
match were a confident falsehood with numbers beside it, which is the
mirror of the rule this project holds a passing report to.
`unrebuildable_columns` asks the DESCRIPTION whether the reading rule
can be rebuilt for each column; where it cannot, that column's
cell-counted obligations go to the NOT-CHECKABLE census with the
sentence saying what the description does not record.

AND THE DESCRIPTION NOW CARRIES MOST OF WHAT IT USED TO LOSE, so that
question answers yes far more often (owner ruling 2026-08-17; plan
amendments A-P3-27, A-P3-28 and A-P3-29; validation method V2.3-A3,
V2.3-A4 and V2.4-A6). Contract version 5 stores a declared spelling
exactly, keeps this package's own two counts out of the spellings map,
and records which members of its own published vocabulary each
declaration named. So the two tuples are READ rather than inferred:
`kept_spellings` from the settings block alone, which contract 5
section 6.4 proves is the whole of the kept side, and
`declared_spellings` from the settings block and every column's
`missing_by_source` together. The witness that named this class -- two
hundred readings and one `n/a` kept as data, seven obligations MISSED
against the table's own description -- is measured in full and misses
nothing.

WHAT IS LEFT UNRECOVERABLE, and it is two things rather than five. A
word of the PERSON'S OWN that the publication floor pooled, and a word
of the person's own on a column whose publication class permits no
value of the table. Both are groups the format exists to refuse to
publish; neither is closable here or by any version of the format
(contract 5 section 7). Residual R-P3-8 carries them and carries the
two costs they leave standing.

WHAT IS NOT CHECKED HERE, AND CANNOT BE, STATED BEFORE ANY VERDICT
BELOW READS AS COVERAGE (V7.3, plan P2-D11 residual R-P2-3). A
validator's silence is read as a pass: somebody holding a report that
missed nothing will believe the file was checked for whatever they came
to it for. This version checks not one cross-column fact, because the
description publishes none -- it
carries no cross-column structure at all: no correlation between two
columns, no formula tying one to another, no shared pattern of which
cells are empty, no ordering between two event columns. There is
therefore nothing of that kind for a check here to measure against.
For the same reason,
rows are treated as independent and the grain is undescribed: the
description
never says what one row of the real table is, so nothing here checks
anything about groups of rows -- per person, per visit, per site.
Cross-column structure arrives in a later phase (Phase 5), and the
quality report states both limits on every run rather than leaving a
reader to notice their absence.

WHAT IT NEVER IMPORTS (V1.4). The generation module. The corner
classifier below is written from the specification, so a shared design
error needs the same mistake written twice from two texts. No random
number generator is constructed or consumed anywhere on this path.

WHAT MAY BE SAID OUT LOUD (V5). The measured file may be anything --
a twin, somebody's real table, or the wrong real table -- so a
measurement is reported only where profiling THAT FILE would publish
it. Where the file's own description would not, the subcheck's verdict
is WITHHELD and neither the measurement nor its outcome is shown.
Sub-floor counts are named as "fewer than the floor" and the exact
number never appears beside a name.

AND WHAT THAT RULE IS NOT, SAID HERE SO THAT NOBODY BUILDS ON IT (owner
ruling 2026-08-14; plan amendment A-P3-13). It is a rule about what ONE
report says, because a report travels and its reader may not hold the
file it is about. It is NOT a defence against somebody who holds the
measured file and runs this check over and over with descriptions they
wrote themselves, watching which verdicts change: that person can
narrow a number a single report withholds, and this module does not try
to stop them, because they are asking questions about a file they have
in front of them. Nothing in this module may be written as though that
defence existed.

**No string read from the measured file leaves this module**, in any
field of any result. That is narrower than V5.4 requires -- the file's
own description would publish some of them -- and it is deliberate: it
makes the disclosure obligation one an exact test can prove, and it
costs the report only detail it can live without. Every string in a
result is either the submitted profile's own published text or one of
this module's fixed words.

WHAT A VERDICT HERE DOES NOT SAY ABOUT THE ROWS IT MEASURED (plan
P2-D11 and P3-D7 stage 2). This module decides what a person is told
about a file, so the qualified claim belongs in it and not only in the
report it feeds. Building a twin reads no table: it samples or copies
no row of anyone's data, and every cell is worked out from the
description and the seed. That is a statement about where a twin's
values come from and it is NOT a statement that no row of a twin can
equal a row of the real table -- holding a published count exactly can
force a twin row to match a real one, with nothing copied, and a check
here confirming that count does not change it. synthtwin offers no
formal privacy guarantee. Every measurement this module returns is
taken from a file derived from real data, so the description, the
plain-language summary beside it, the twin, the twin's report and the
quality report are all real-derived material and are kept under the
rules the real table is kept under.
"""

import csv
import dataclasses
import math
import pathlib

from synthtwin import contract, errors, parsing, profile, reading, taxonomy
from synthtwin.paths import validate_local_path

# -- the five verdicts (V6.1) -----------------------------------------

HELD = "HELD"
WITHIN_BOUND = "WITHIN-BOUND"
AUTHORIZED_DEVIATION = "AUTHORIZED-DEVIATION"
WITHHELD = "WITHHELD"
MISSED = "MISSED"

VERDICTS = (HELD, WITHIN_BOUND, AUTHORIZED_DEVIATION, WITHHELD, MISSED)

# -- the three kinds an entry can be (V3.3) ---------------------------
#
# Only the first two reach an Outcome. An input-side entry may neither
# carry a verdict nor be listed as an unverified twin fact -- the
# contract says such a fact imposes no obligation on the written CSV --
# so the strict loader the caller already ran is its whole discharge,
# and INPUT_SIDE_ENTRIES below is where a projection test finds it.

EXECUTABLE = "executable-subcheck"
LISTING = "listing-entry"
INPUT_SIDE = "input-side-entry"

# -- the four corners (V4.1) ------------------------------------------

CORNER_IDENTIFIER_INFEASIBLE = "identifier-infeasible"
CORNER_DATETIME_OFFSETS_WITHHELD = "datetime-offsets-withheld"
CORNER_LABEL_VARIANTS_SHORT = "label-variants-short"
CORNER_NUMERIC_SPELLINGS_SHORT = "numeric-spellings-short"

CORNERS = (
    CORNER_IDENTIFIER_INFEASIBLE,
    CORNER_DATETIME_OFFSETS_WITHHELD,
    CORNER_LABEL_VARIANTS_SHORT,
    CORNER_NUMERIC_SPELLINGS_SHORT,
)

# The two distinctness counts, named rather than spelled, because which
# of them a corner reaches is part of that corner's own passage and not
# a property of the column (V4.1; review item P3-V8-F3).
_RAW_DISTINCT = "n_distinct"
_FOLDED_DISTINCT = "n_distinct_folded"

# What authorizes each lesser outcome, in the words of the document that
# grants it. An AUTHORIZED-DEVIATION shown without its citation is a
# lowering nobody can check, so the citation travels with the verdict.
CORNER_CITATIONS = {
    CORNER_IDENTIFIER_INFEASIBLE: (
        "phase-2 plan P2-D0 owner decision 6, as the disposition "
        "registry cites it: in that decision's infeasible corner, "
        "three distinctness facts are REPORT-ONLY, not one"
    ),
    CORNER_DATETIME_OFFSETS_WITHHELD: (
        "phase-2 plan P2-D9, as the disposition registry cites it: "
        "datetime columns whose offsets are withheld"
    ),
    CORNER_LABEL_VARIANTS_SHORT: (
        "phase-2 plan P2-D6: raw n_distinct is APPROXIMATED under the "
        "two-sided envelope only where the published variants and the "
        "withheld-variant multiset do not supply enough spellings "
        "(docs/spec/generation-method-v1.md G12.7)"
    ),
    CORNER_NUMERIC_SPELLINGS_SHORT: (
        "phase-2 plan P2-D6: falling back to the two-sided envelope "
        "only where even the permitted spellings cannot supply the "
        "count (docs/spec/generation-method-v1.md G12.8)"
    ),
}

# -- the envelopes an APPROXIMATED fact is measured against ------------
#
# Every bound lives in the generation method and is CITED here, never
# restated, so the two can never drift apart (validation method's own
# opening rule).

ENVELOPE_NUMERIC_RUNGS = (
    "docs/spec/generation-method-v1.md G12.2, which states G5.6's "
    "two-sided rung envelope"
)
ENVELOPE_MOMENTS = "docs/spec/generation-method-v1.md G12.3"
ENVELOPE_DATETIME_RUNGS = "docs/spec/generation-method-v1.md G12.4"
ENVELOPE_DATETIME_DISTINCT = "docs/spec/generation-method-v1.md G12.5"
# The clock role's two, cited and never restated. Both point at the
# clause the generation method carries for this role, which is written
# in the same landing as the construction it bounds.
ENVELOPE_CLOCK_RUNG = "docs/spec/generation-method-v1.md G12.9"
ENVELOPE_CLOCK_DISTINCT = "docs/spec/generation-method-v1.md G12.9"

ENVELOPE_TEXT_SHAPE = "docs/spec/generation-method-v1.md G12.6"
ENVELOPE_LABEL_DISTINCT = "docs/spec/generation-method-v1.md G12.7"
ENVELOPE_NUMERIC_DISTINCT = "docs/spec/generation-method-v1.md G12.8"

# -- the refusals of method G12 (V4.3, V9) ----------------------------
#
# These refuse GENERATION, so no conforming twin exists for such a
# profile at all: a validate run on one is a refusal, never a verdict
# and never a pass. Treating one as an authorized corner would launder
# an impossible obligation into a passing report.

# THE FOUR NAMES ARE `errors`' OWN (amendment A-P3-23, review item
# P3-V7-F7). The message a person reads when no twin of a description
# exists is a refusal like every other, so it lives in the failure
# catalog with the rest -- and the catalog's rules, its exact-shape test
# and its driven CLI case all reach it there. These four are the names
# that message is written for, spelled once, and `refusal_of` may answer
# nothing else.
REFUSAL_COUNTS_CONTRADICT = errors.REFUSAL_COUNTS_CONTRADICT
REFUSAL_WORDS_EXCEED_LENGTH = errors.REFUSAL_WORDS_EXCEED_LENGTH
REFUSAL_WHOLE_NUMBERS_NEED_ROOM = errors.REFUSAL_WHOLE_NUMBERS_NEED_ROOM

# The fourth refusal method G12 names. It is decided here from the
# published facts alone (review item P3-V1-F5), and WHAT IT DECIDES IS
# NARROWER THAN THE GENERATOR'S OWN QUESTION, which is said here rather
# than left for a reader to discover:
#
# * G9.4 raises the refusal when the WALK runs out -- the same walk that
#   would have written the cells -- and the walk's answer depends on the
#   packing of G9.5, which decides each group's class, band and length.
#   Rebuilding that packing here would be a second implementation of the
#   planning stage, which V1.4 forbids by name: a validator sharing the
#   planner's defects is not a second opinion.
# * What a validator CAN settle is the direction that cannot be wrong.
#   G9.4 states that capacity is an upper bound on what the walk
#   produces and never a lower one, so a column demanding more different
#   spellings than its published lengths can supply AT ALL is a column
#   whose walk must run out, whatever the packing does. That is the
#   condition below, and it is the one the shipped refusal's own
#   boundary case is: twenty-six one-character values outside the code
#   alphabet, where twenty-five exist.
# * So this is SOUND and INCOMPLETE. It never refuses a description a
#   twin exists for -- every bound it compares against is an upper bound
#   on the construction -- and a description whose walk runs out for a
#   subtler reason (a packing that cannot place the groups it has, a
#   fold-collision partner with no parent) still reaches verdicts here
#   instead of this refusal. That residue needs the planner, and the
#   boundary that keeps the planner out is worth more than the residue.
REFUSAL_DOMAIN_TOO_SMALL = errors.REFUSAL_DOMAIN_TOO_SMALL

# The alphabets of method G9.1 and the positional rules that narrow
# them, restated from the specification rather than imported (V1.4).
# `CODE` and the missing spellings are asked of `parsing`, which is the
# shipped classifier both sides are written against; the two counts
# below are the ones a person can check against G9.1's own table.
_WIDE_LOW = 32
_WIDE_HIGH = 127
_WIDE_SIZE = _WIDE_HIGH - _WIDE_LOW
_CODE_SIZE = 64
_DIGIT_SIZE = 10
_FORMULA_LEADERS = ("=", "+", "-", "@")
_SPACE = " "

# The three bands a made-up value sits in (G9.5 step 4).
_BAND_DIGITS = "digits"
_BAND_CODE = "code"
_BAND_WIDE = "wide"

# Where every count in the capacity arithmetic stops climbing. G9.4
# fixes the saturating rule and the value: far above any row count a
# table can hold, so every comparison made with it is exact.
_SATURATION = 1 << 62

# -- entries whose whole obligation lives on the profile (V3.3) -------
#
# LOADER-ONLY facts and the profile-side membership rules of the
# STRUCTURAL containers, as the disposition registry classes them. They
# are named here, and nowhere else, because the projection test has to
# find each one bound to the loader rather than silently absent -- and
# because a fact listed as an unverified twin fact would be an
# obligation the matrix refuses to state.
# -- the obligations that are the METHOD's and not a published fact's --
#
# V6.2's byte rules are obligations on the twin that no field of the
# description states: the description records how the REAL table was
# read (`source.encoding` and its neighbours, all REPORT-ONLY), and what
# the twin's own bytes must be comes from the contract's writing rules.
# So these two do not bind to a registry fact, and the list is written
# out HERE, closed, so that the projection test can insist every other
# fact a check names is one the registry carries. A third name added to
# this tuple is a fact somebody took out of the registry's reach, which
# is a decision a reviewer reads in the diff.
BYTE_RULE_FACTS = ("document.encoding", "document.line-endings")

INPUT_SIDE_ENTRIES = (
    ("document", "profile_version"),
    ("document", "settings"),
    ("document", "created_with"),
    ("document", "publication_notes"),
    ("document", "relationships"),
    ("document", "columns"),
    ("document", "source"),
    ("numeric", "n_rows"),
    ("label", "level_ceiling"),
    ("free_text", "length"),
    ("free_text", "words"),
)

# -- what a listing entry says, in one fixed sentence each ------------

_NOT_CHECKABLE_REPORT_ONLY = (
    "no CSV can evidence this fact: the description records how the "
    "real table was read, and a written file cannot show it"
)
_NOT_CHECKABLE_RESOLUTION_MIX = (
    "the description records which written form each of the real "
    "table's dates wore, and how many wore each, and it asks no file "
    "to write them the same way: a file that writes them all one way "
    "misses no obligation this description makes"
)
_NOT_CHECKABLE_HEADERLESS_ORDER = (
    "the description says the column names were generated, so the file "
    "carries no header line and nothing in it can evidence the order "
    "the names were given in"
)
_NOT_CHECKABLE_ZERO_ROWS = (
    "the description publishes no rows, so the file this description "
    "asks for holds nothing that could evidence this fact"
)
_NOT_CHECKABLE_NO_LADDER = (
    "the published ladder is null at every rung, so the description "
    "carries no shape for these values and there is no window to "
    "measure against"
)
_NOT_CHECKABLE_DECLARED_AXIS = (
    "this says whether the person who owns the table declared this "
    "column as a record number when the description was written. It is "
    "a fact about the description and not about any file: the same "
    "declaration is what this file was described under, so no CSV can "
    "make the two answers differ either way"
)
_NOT_CHECKABLE_FIRST_COLUMN = (
    "the description says the column names were generated, so nothing "
    "in the file names this column and the only thing a CSV could show "
    "about its number is that the file carries at least that many "
    "columns -- which for the first column is true of every file that "
    "can be read at all. How many columns the file has is checked, and "
    "is the whole of what this fact can be evidenced by here"
)
_NOT_CHECKABLE_SKEW_UNBOUNDED = (
    "the published ladder for this column is too coarse for the "
    "generation method's own envelope to narrow: its bound falls back "
    "to the range every column of this many values lies in whatever "
    "they are, so a comparison against it would admit every file and "
    "prove nothing"
)
_NOT_CHECKABLE_STYLE_CEILING = (
    "the description names this form for as many cells as the file has "
    "rows, so every cell the file can carry in it is already accounted "
    "for and there is no unnamed cell left for this ceiling to govern"
)
_NOT_CHECKABLE_OFFSETS_WITHHELD = (
    "the description withholds this column's offsets, so it publishes "
    "no offset for a file to be measured against, and no CSV can "
    "evidence one either way. Authorized by "
)
_NOT_CHECKABLE_IDENTIFIER_CORNER = (
    "the description's own published lengths cannot supply this many "
    "different record numbers, so the ratified plan makes this fact one "
    "the report states rather than one a file is measured against. "
    "Authorized by "
)
_NOT_CHECKABLE_ENDPOINT_WITHHELD = (
    "the publication floor held this end's own offset back, so the "
    "description names no offset for it and no file can carry one "
    "either way. The offsets the description does name are checked, "
    "and are the whole of what a CSV can evidence here"
)
_NOT_CHECKABLE_SPELLING_ENVELOPE = (
    "the description's own permitted spellings settle nothing about how "
    "many different values a twin of it carries: the envelope the "
    "ratified plan authorizes here reaches from one value to every value "
    "a column of this length can hold, so a file whose every cell "
    "repeated one value would land inside it and a comparison against it "
    "would prove nothing. Authorized by "
)

# -- and the three a description that cannot be read back gives --------
#
# THE READING RULE IS THE ONE INPUT THIS COMMAND HAS NO SECOND SOURCE
# FOR (owner ruling 2026-08-16; plan amendment A-P3-26). To describe the
# measured file the way the description was written, `settings_for` must
# rebuild the words the person named -- and it rebuilds them from the
# description's own published text, which does not always carry them.
# Where it cannot, the obligations counted over that column's cells are
# obligations this description does not support asking, and saying so is
# what these three sentences do. Each is BUILT rather than fixed,
# because each states a number the description publishes; none names a
# spelling, out of the description or out of the measured file.
#
# THE LAST CLAUSE IS SHARED AND IS PUBLIC, so that a reader who meets
# two of these lines in one report sees one limit stated twice rather
# than two limits, and so that the suite can find these entries in a
# census without matching on prose it would then have to keep in step.
UNREBUILDABLE_REASON_TAIL = (
    "measuring this column the way the description was written is not "
    "something this description supports"
)


def _holes_no_word_accounts_for(unnamed: int) -> str:
    """A column with holes no recovered spelling accounts for."""
    return (
        f"the description records {_shown_count(unnamed)} cell(s) of "
        f"this column made absent by a word you named, and does not "
        f"record the word, so " + UNREBUILDABLE_REASON_TAIL
    )


def _absence_words_not_recorded(named: int, recovered: int) -> str:
    """Words of the person's own, named as "no value" and not carried.

    The counts are of the person's OWN words, which is what changed at
    contract version 5 (plan amendment A-P3-29): a word of synthtwin's
    own that somebody named is written in the description whatever the
    floor did with its cells, so counting it here would tell a reader
    that something is missing which is not.
    """
    return (
        f"the description says {_shown_count(named)} word(s) of your own "
        f"were named as meaning \"no value\" when it was written and "
        f"records {_shown_count(recovered)} of them, so a cell of this "
        f"column can be one the description read as absent and this "
        f"report would read as a value; " + UNREBUILDABLE_REASON_TAIL
    )


# -- what a file that cannot carry an obligation is told, in one --------
#    fixed sentence each (review item P3-V1-F11)
#
# THE OBLIGATION SET IS A FUNCTION OF THE DESCRIPTION, NOT OF WHAT THE
# FILE HAPPENED TO HOLD. A file missing a column, or holding no rows at
# all, does not thereby owe less: it MISSES what it cannot carry, and
# the census says so on the same line it would have carried a verdict
# on. The version this replaces dropped those obligations, so a file
# with one column removed was measured against five obligations and the
# report still called them every measurable one.
_NO_COLUMN_HERE = (
    "no column of this file stands at this position, so nothing in it "
    "carries what this obligation asks for"
)
_NO_ROWS_HERE = (
    "this file holds no rows at all, so this column holds no cells for "
    "this obligation to be met by"
)
_NO_NAMES_HERE = (
    "the first row of this file does not name a table's columns, so "
    "nothing in it stands for this column of the description and "
    "nothing in it carries what this obligation asks for"
)

# -- what a withheld subcheck says, in one fixed sentence each --------

_GATE_CLOSED = (
    "describing this file on its own would not publish what this check "
    "measures, so neither the measurement nor its outcome is shown"
)

# THE SECOND WAY THE GATE CLOSES, AND WHY IT NEEDED ITS OWN SENTENCE
# (review item P3-V2-D-F2; V5.3, V5.4).
#
# The one above is for a check whose whole KIND the file's own
# description does not carry -- a numeric summary of a column that file
# describes as labels. This one is for a check whose kind it does carry
# and whose NUMBER it pools: a form used by fewer cells than the
# publication floor is never named in a description, and every
# description of that file names the same single pooled total instead.
# So two files the producer describes byte for byte alike can differ in
# which form those pooled cells wear, and a verdict that told them apart
# would state about the file a count the file's own description withheld
# -- which is what V5.1 forbids ONE report to say, whoever reads it.
#
# THAT IS THE WHOLE OF WHY THIS GATE IS HERE, since 2026-08-14. It used
# to give a second reason: that repeated candidate descriptions would
# read the count off the verdicts. The owner ruled that reason out of
# scope (plan amendment A-P3-13) -- a person who can run the check again
# with a description they wrote is holding the file -- so nothing here
# rests on it. The first reason is untouched and is enough on its own:
# the report travels, and a reader of one report may not be told a count
# that describing the file would pool.
#
# The verdict is only withheld where the file's own description leaves
# it OPEN. Where what that description does publish settles the answer
# either way -- a published floor no pooled count can reach, a pool with
# nothing in it -- the verdict is shown, because stating it says nothing
# the file's own description does not already say.
_GATE_POOLED = (
    "the file's own description does not publish the count this check "
    "compares -- fewer cells are written that way than its publication "
    "floor names, so every description of this file pools them into one "
    "total -- and what it does publish does not settle the comparison "
    "either way"
)

# THE THIRD WAY THE GATE CLOSES: THERE IS NO DESCRIPTION AT ALL (review
# item P3-V3-F3; V5.1).
#
# The two above are for a file `synthtwin profile` describes, whose
# description carries no fact of this kind or pools the count this one
# compares. This one is for a file it REFUSES: a file with no data rows
# to describe, and a file whose first row cannot name a table's columns.
# Describing those publishes nothing whatever -- not the header's names,
# not its width, not how many records the file holds -- so a report
# stating any of it states about the measured file something no run of
# the profiler on that file would ever say. That is V5.1 about ONE
# report, and it is the whole reason this gate is here: the report
# travels to people who do not hold the file. The second reason this
# comment used to give -- that repeated candidate descriptions would
# read the header off the verdicts -- is out of scope from 2026-08-14
# (plan amendment A-P3-13) and nothing here rests on it.
#
# What the refusal itself publishes is still said, because it is what a
# reader gets by running the profiler on the file: that the file holds
# no rows, or that its first row repeats a name or leaves one blank, at
# the column NUMBERS the profiler's own refusal names.
_GATE_REFUSED = (
    "describing this file on its own would publish nothing at all -- "
    "`synthtwin profile` refuses a file it cannot read a table out of -- "
    "so neither the measurement nor its outcome is shown"
)

# The fact whose whole evidence is the header line, named once because
# two places have to agree about which check that is.
_POSITION_FACT = "universal.position"

# What a column carries instead of a measurement when its cells, counted
# the way V2.4 counts them, are not of the kind this obligation asks for
# at all (review item P3-V2-A1). This is a MISS and not a withholding:
# the description says this column publishes a fact of this kind, and
# describing the file's own non-blank cells produces no fact of that kind
# -- which is what "the file does not meet the obligation" means. It
# names no number and no spelling.
_NOT_OF_THAT_KIND = (
    "nothing of the kind this obligation asks about, counting every cell "
    "that is not blank as a value"
)

# What a line says when the file holds the description's own value and
# the method's window for that fact does not reach it (review item
# P3-V10-F5; plan amendment A-P3-40, validation method clause V6.1-A1).
#
# THE PHRASE "does NOT reach the" IS LOAD-BEARING and is the same phrase
# the within-bound note uses. Both pages carry the same envelopes for the
# same facts, and `tests/test_shipped_page_review.py` reads that phrase
# off the check to decide whether the quality report agrees with the
# twin's own report about a window that misses the published value. A
# verdict changing from WITHIN-BOUND to HELD may not make the second
# opinion go silent about the window; it changes what the window
# DECIDED, not what it is.
_MET_OUTSIDE_ITS_WINDOW = (
    "      the file holds the description's own value exactly, so this",
    "      obligation is met. The method's window here does NOT reach the",
    "      description's own value -- it is what the method allows the",
    "      file, worked out from the description and the size of this",
    "      column, and not a margin around that value. It is printed",
    "      here for the record; it did not settle the verdict above.",
)

# WHAT A MISSED LINE SAYS WHERE THE MEASURED SIDE MAY NOT BE PRINTED
# (review item P3-V12-F2 clause (a); plan amendment A-P3-45; validation
# method clause V5.4-A1).
#
# A MISSED verdict tells a person that their file does not carry a fact
# the description publishes. Where the measurement behind it is one
# V5.4 keeps back, the line printed the description's request and
# stopped -- no found line, no reason, nothing. Measured on the shipped
# tree: a one-column table of sixty readings written to two decimal
# places, validated against its own genuine description, printed
# `styles.spelled ... MISSED` and one line under it, so a researcher
# was told their file failed and not what it holds. The page was worse
# than silent, because two of its own sentences promise that every
# missed obligation is printed with what the file was found to hold.
#
# So the found value is shown, or the line says why it is not. Below
# are the two reasons there are, each written as the rule that keeps
# the value back and what a person can do about it.
_NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE = (
    "      what this file holds here is NOT SHOWN, and this is why: it",
    "      is text written in the file itself, and no text read out of",
    "      a measured file is printed in this report, under any verdict",
    "      -- which is what lets one report be handed to a person who",
    "      does not hold that file. The comparison above was made in",
    "      full and the verdict is its outcome; only the measured side",
    "      is kept back. Open the file itself to read what stands here.",
)

_NOT_SHOWN_IT_IS_A_COUNT_OF_THE_FILE = (
    "      what this file holds here is NOT SHOWN, and this is why: it",
    "      is a number counted in the file, and this obligation is",
    "      reported with what the description asks for and the outcome",
    "      alone and never with that count, on any file -- which is what",
    "      lets one report be handed to a person who does not hold that",
    "      file. The comparison above was made in full and the verdict",
    "      is its outcome; only the measured side is kept back. To read",
    "      it, describe the file itself with `synthtwin profile` and",
    "      read the count that description publishes.",
)

# THE FLOOR UNDER BOTH, and it is a floor and not a third reason. Every
# outcome this module assembles goes through `_readable`, so a MISSED
# line naming neither what was found nor why it is not shown cannot
# reach a page: it carries this sentence instead. No subcheck that
# ships needs it -- `tests/test_p3v12f2_a_miss_says_what_it_found.py`
# asserts that every one of them names its own reason on a file that
# misses it -- and it is here so that a subcheck written next year
# fails where a reader can see it rather than printing a blank.
_NOT_SHOWN_AND_THIS_LINE_CANNOT_SAY_WHY = (
    "      what this file holds here is NOT SHOWN, and this line cannot",
    "      say which rule kept it back: it is either text read out of",
    "      the file or a count this obligation is never reported with.",
    "      The comparison above was made in full and the verdict is its",
    "      outcome. This sentence is a defect in synthtwin and not a",
    "      fact about your file -- every missed obligation is meant to",
    "      name its own reason. Please report it.",
)

# The byte-order mark as one character, written as its code point so
# that nobody has to trust an invisible character in this file.
_BYTE_ORDER_MARK = "\ufeff"

# The characters method G7.1's ordinal space is read off, and the ten
# figures a whole number is spelled with. First-party constants: nothing
# here is ever read from a file, and membership against them is how this
# module takes a text apart without calling a method the offline audit
# cannot trace (plan D6.2).
_DIGITS = "0123456789"
_DATE_DASH = "-"
_QUARTER_MARK = "Q"

# The characters method G2's writing rule turns on, and the two it
# writes with. A field is quoted when and only when it holds one of
# `_MUST_BE_QUOTED`, and a quote character inside a quoted field is
# written twice.
_QUOTE = '"'
_COMMA = ","
_LINE_FEED = "\n"
_CARRIAGE_RETURN = "\r"
_MUST_BE_QUOTED = _COMMA + _QUOTE + _LINE_FEED + _CARRIAGE_RETURN

# The three ways a written record can end, longest first so that the
# two-character one is recognised before its own first half.
_LINE_BREAKS = (
    _CARRIAGE_RETURN + _LINE_FEED,
    _LINE_FEED,
    _CARRIAGE_RETURN,
)

# WHICH SUBCHECKS THIS MODULE MEASURES FROM THE WRITTEN CELLS (V2.4).
#
# Every other measurement in a result is read out of a re-description,
# which counts over ITS OWN reading of which cells are present. These
# ones are not: `_style_checks` recounts the styles from the written
# cells, skipping the blank ones and nothing else, so they are ALREADY
# taken over the blank/non-blank split and the second description has
# nothing to say about them. What still governs them is the disclosure
# gate, which is why they are gated with everything else and only their
# MEASUREMENT is taken from the side that measured the cells.
#
# `styles.published.*` is deliberately not here: it compares a map the
# re-description carries, so it is presence-dependent like the rest.
#
# The list is written out rather than matched by prefix so that adding a
# style subcheck is a decision somebody makes here on purpose.
_MEASURED_FROM_THE_CELLS = (
    f"styles.exact.{parsing.STYLE_LEADING_ZERO}",
    f"styles.exact.{parsing.STYLE_LEADING_PLUS}",
    f"styles.exact.{parsing.STYLE_EXPONENT_UPPER}",
    f"styles.at-least.{parsing.STYLE_PLAIN}",
    f"styles.at-least.{parsing.STYLE_DECIMAL}",
    f"styles.at-least.{parsing.STYLE_EXPONENT_LOWER}",
    "styles.spill",
    "styles.remainder",
    "styles.spelled",
    f"styles.canonical.{parsing.STYLE_DECIMAL}",
    f"styles.canonical.{parsing.STYLE_EXPONENT_LOWER}",
)

# THE SPELLINGS THE MEASUREMENT SIDE KEEPS AS DATA (V2.4).
#
# Presence is BLANKNESS on the verdict side: every absent cell of a twin
# is written empty, so a cell that holds anything at all holds a value.
# The producer's own absence machinery disagrees on exactly two kinds of
# cell -- a spelling in its built-in table of missing markers, and a
# number it judges to be a stand-in for "no value" -- and both are named
# here so that the measurement re-description keeps them as the data
# V2.4 says they are. The blank spelling is deliberately NOT among them:
# a blank cell is absent under both readings, and declaring it kept
# would make every empty field a value.
#
# These are the producer's own first-party constants, not anything read
# from a file, so this tuple is the same on every run and no measured
# string reaches the settings.
_KEPT_OVER_THE_SPLIT = tuple(
    sorted(
        [
            spelling
            for spelling in parsing.built_in_missing_texts()
            if spelling
        ]
        + [f"{value:g}" for value in parsing.NUMERIC_SENTINELS]
    )
)

# The TEXT half of that table on its own, which is the half a column's
# `missing_by_source` can name (plan amendment A-P3-39, validation
# method clause V2.4-A10). The number half is answered from
# `sentinel_verdicts` instead, because a stand-in is judged per column
# and a published key alone does not say which way that judgment went.
_BUILT_IN_TEXTS = tuple(
    sorted(
        [
            spelling
            for spelling in parsing.built_in_missing_texts()
            if spelling
        ]
    )
)

# The same three stand-ins, as the EXACT numbers the producer decides
# them by (review items P1-R8-F2 and P3-V4-F1).
#
# WHY NOT THE BINARY64 VALUES. The producer asks which cells ARE a
# candidate by the number the cell's digits denote, exactly, and Phase 1
# made it exact for a reason it wrote down: two decimal spellings a
# person can tell apart round to one binary64 value, so a rule that
# compares the rounded values makes one number out of two. This module
# re-describes the measured file with that producer, so a cell it
# decides differently is a cell the two sides disagree about -- and
# comparing the rounded values here erased eleven cells of
# `-999.00000000000001` that the producer's own description of the same
# file counts as ordinary readings, and reported two style obligations
# MISSED against that description. The identity is `taxonomy`'s own
# published rule and is not written a second time here.
_STAND_IN_EXACTS = tuple(
    [taxonomy.exact_of_number(value) for value in parsing.NUMERIC_SENTINELS]
)

# And the same three, paired with a spelling that denotes each of them,
# because contract version 5 records a declared stand-in as a NUMBER and
# the producer's settings take a SPELLING (contract 5 section 6.2, its
# `built_in_numbers`; plan amendment A-P3-29).
#
# ANY SPELLING OF THE SAME NUMBER WOULD DO, and that is the point rather
# than a shortcut: `settings.declaration_matching` has one permitted
# value, "the exact number when it reads as one, else the spelling", so
# the producer compares a declared stand-in with a cell by the number
# both denote. These are the spellings `_KEPT_OVER_THE_SPLIT` above
# already hands the producer for the same three numbers, written the
# same way, so this module names each stand-in one way and not two.
#
# A NUMBER OUTSIDE THE THREE NAMES NOTHING HERE. The loader has already
# refused a document whose `built_in_numbers` holds anything else
# (contract 5 C5-K1), and a table that admits only the three cannot turn
# a fourth number into a declaration this module then applies to
# somebody's cells.
_STAND_IN_SPELLINGS = tuple(
    [(value, f"{value:g}") for value in parsing.NUMERIC_SENTINELS]
)

# The eleven ladder positions as probabilities, in ladder order.
_LADDER_SHARES = tuple(
    [number / denominator for _name, number, denominator in taxonomy.LADDER]
)
# ...and as the WHOLE PERCENTAGES method G7.3 and G12.4 are written in.
# Every datetime step is exact integer arithmetic in the ordinal space of
# G7.1 -- "no float is formed anywhere in G7" is the method's own
# sentence -- so the rung selection and the interpolation take the
# percentage rather than the probability. The producer's ladder carries
# each rung out of a hundred; a rung carrying any other denominator is a
# ladder this arithmetic is not written for, and the suite says so on
# the commit that adds one rather than letting it round away here.
_LADDER_PERCENTS = tuple(
    [number for _name, number, _denominator in taxonomy.LADDER]
)
_LADDER_DENOMINATORS = tuple(
    [denominator for _name, _number, denominator in taxonomy.LADDER]
)
_LADDER_KEYS = taxonomy.LADDER_NAMES


@dataclasses.dataclass(frozen=True)
class Check:
    """One executable subcheck, measured, with its verdict.

    ``column`` is the profile's own published column name, or "" for a
    document-level obligation. ``fact`` is the (group, field) the
    disposition registry carries, written as `group.field`.
    ``subcheck`` is the obligation at the finest grain the contract
    governs -- one rung, one style, one level, one byte rule -- and is
    the identity a red case names when it says which check must fail.

    ``published`` is what the description asks for and ``achieved``
    what the file was found to hold, both already written for a person.
    Both are "" where there is nothing to show. ``citation`` is filled
    only for AUTHORIZED-DEVIATION, where it carries the passage that
    authorizes the lesser outcome, and for WITHIN-BOUND, where it
    carries the envelope the window came from.

    ``note`` is the report's further lines under this one, already
    broken where they are to be broken, and it says the two things the
    fields above cannot. THE FIRST is why the measured side of a MISSED
    obligation is not shown, wherever it is not: a verdict that tells a
    person their file failed and then says nothing about what the file
    holds is unreadable, so every MISSED check carries either
    ``achieved`` or a note saying which rule keeps it back, and
    `_readable` is the floor under that (review item P3-V12-F2;
    amendment A-P3-45). THE SECOND is that a window is worked out from
    the description and the size of the column, not as a margin around
    the published value, so it can lie wholly to one side of the value
    it stands beside. Printed without that sentence the page contradicts
    itself -- "asks for 2023-11-23 (between two instants neither of
    which is 2023-11-23): WITHIN-BOUND" -- and the reader has no way to
    tell an honest bound from an arithmetic mistake (review of the
    shipped reports, 2026-08-15). It is empty wherever there is nothing
    further to say.

    NO TEXT FIELD EVER HOLDS A STRING READ FROM THE MEASURED FILE.
    """

    column: str
    fact: str
    subcheck: str
    verdict: str
    published: str = ""
    achieved: str = ""
    citation: str = ""
    note: "tuple[str, ...]" = ()


@dataclasses.dataclass(frozen=True)
class Listing:
    """One obligation no CSV can evidence, and why (V3.3).

    A listing entry carries no verdict and is never counted toward a
    pass. Its failure mode is the census itself: a line removed from it
    is a line missing from the report.

    ``subcheck`` carries the SAME identity a `Check` carries, and it is
    there so that an obligation which is a verdict against one file and
    a listing against another can be recognised as the one obligation it
    is (review items P3-V1-F3 and P3-V1-F11). It is "" where the whole
    fact is unevidencible however the file turns out -- a REPORT-ONLY
    fact has no finer grain to name.
    """

    column: str
    fact: str
    subcheck: str
    reason: str


@dataclasses.dataclass(frozen=True)
class Census:
    """How many subchecks landed on each verdict, and how many did not.

    The summary of a quality report is generated from this and nothing
    else, so no sentence can claim more than the counts support.
    ``not_checkable`` is the number of listing entries.
    """

    held: int
    within_bound: int
    authorized_deviation: int
    withheld: int
    missed: int
    not_checkable: int


@dataclasses.dataclass(frozen=True)
class Outcome:
    """Everything one validate run measured, and which file it measured.

    ``checks`` is every executable subcheck with its verdict, in a
    fixed order: the document-level obligations first, then the columns
    in the description's own order. ``listings`` is every obligation no
    CSV can evidence. ``census`` counts both.

    ``measured_name`` is the NAME of the file these verdicts are about,
    as the person spelled it on the command line -- the last component
    of it, never the folders above. It is on the outcome rather than
    handed separately to the report because WHICH FILE a verdict is
    about is part of the measurement, not part of the rendering: a
    report whose identity is optional is a report that can be written
    without one, which is exactly what happened (review item P3-V2-G).
    It is not read from the file and cannot be: it is a string the
    person typed.
    """

    checks: "tuple[Check, ...]"
    listings: "tuple[Listing, ...]"
    census: Census
    measured_name: str


# -- V2.2: the settings the file is re-described under ----------------


def settings_for(description: contract.Profile) -> taxonomy.Settings:
    """Rebuild the taxonomy settings the description was written under.

    Guarantees:

    - Inputs: one loaded description. Nothing else is consulted -- no
      command line, no default, no environment.
    - Determinism: the same description always gives the same settings.
    - Errors raised: none.
    - Boundary: every spelling in either declaration tuple is either a
      member of the closed vocabulary contract 5 section 14.1 publishes
      -- this package's own ten words and three stand-in numbers,
      identical in every installation and containing no text of any
      table -- or a key of a column's `missing_by_source`, which is
      what `synthtwin profile` publishes about the file it described.
      Nothing is guessed. The read mode is NOT a settings key and is
      not decided here; it comes from `source.header_source`.

    Every one of the fifteen keys the settings block carries is used,
    and no sixteenth is invented: a skipped key would describe the file
    under rules the description was not written under, which is the one
    way the disclosure gate can be walked past.

    WHAT CONTRACT VERSION 5 CHANGED HERE, AND IT IS THE WHOLE OF THIS
    FUNCTION'S JOB (plan amendments A-P3-27, A-P3-28 and A-P3-29;
    validation method clauses V2.3-A3 and V2.4-A6). Until version 5 the
    settings block recorded a declaration as a COUNT and never as text,
    so both tuples had to be INFERRED from facts published for other
    reasons -- a level's label, a level's variants, a sentinel verdict
    reading `kept_by_you`. Version 5 records which members of this
    package's own vocabulary each declaration named, and contract 5
    section 6.4 PROVES those members are the whole of what a
    `--keep-value` can change about any cell's reading. So the kept
    tuple is now READ rather than inferred, and the three inference
    routes are gone: each of them existed only because version 4 lost
    the fact, and each of them answered a question about the
    description's LEVELS that the settings block now answers about the
    COMMAND LINE.

    WHY `declared_missing_values` IS NO LONGER EMPTY (review item
    P3-V4-F1, the direction the finding did not name). This tuple was
    empty exactly, under the note "a declared-missing spelling is
    genuinely absent from every twin, whose absent cells are written
    empty". That is true of a twin and false of the OTHER file this
    command is pointed at -- the table itself (V1.2) -- and the file the
    description was written from is exactly the file that still holds
    those spellings. A researcher who runs `--missing-value XX` and then
    validates their own table had twelve `XX` cells read back as data:
    the column changed role, and `presence.n_present`,
    `presence.n_missing`, `axes.role`, `axes.statistical_type`,
    `counts.n_not_numeric` and both distinctness counts were reported
    MISSED against the table's own profile. With `--missing-value -777`
    the same table missed SEVENTEEN, the ladder and the moments among
    them. The spelling is not guessed: it is the description's own
    published text, exactly as `kept_spellings`' three routes are.
    """
    block = description.settings
    return taxonomy.Settings(
        small_cell_floor=block.small_cell_floor,
        identifier_uniqueness=block.identifier_uniqueness,
        identifier_minimum_rows=block.identifier_minimum_rows,
        minimum_parse_rate=block.minimum_parse_rate,
        categorical_share=block.categorical_share,
        categorical_ceiling=block.categorical_ceiling,
        categorical_floor=block.categorical_floor,
        sentinel_outlier_iqr_multiple=block.sentinel_outlier_iqr_multiple,
        sentinel_minimum_share=block.sentinel_minimum_share,
        kept_values=kept_spellings(description),
        declared_missing_values=declared_spellings(description),
        declaration_matching=block.declaration_matching,
        near_threshold_slack=block.near_threshold_slack,
        day_first=block.day_first,
        long_tail_minimum_level=block.long_tail_minimum_level,
    )


def settings_over_the_split(
    description: contract.Profile,
) -> taxonomy.Settings:
    """The same settings, with absence pinned to blankness (V2.4).

    Guarantees:

    - Inputs: one loaded description. Nothing else is consulted, and no
      file is read: the extra kept spellings are the producer's own
      first-party constants, so this tuple is the same on every run and
      no string out of the measured file reaches the settings.
    - Determinism: the same description always gives the same settings.
    - Errors raised: none.
    - Boundary: every one of the fifteen keys is `settings_for`'s, and
      exactly one differs -- `kept_values` also carries every non-blank
      built-in missing marker and every numeric stand-in for "no value"
      THAT THIS DESCRIPTION PASSES NO VERDICT ON. Three things take a
      spelling back off that list and all three are the description's
      own words: a declaration of it, a column's sentinel verdict on it,
      and a column publishing it as the source of its holes.
      `declared_missing_values` is `settings_for`'s own recovered tuple,
      unchanged.

    WHY THERE ARE TWO SETTINGS AND WHAT EACH ONE DECIDES. The method
    splits the question in two and says so in terms (V2.4): the
    re-description under `settings_for` -- the file's own description,
    the one `synthtwin profile` would write about this file -- governs
    HOW the cells read, which role the column is, and the disclosure
    gate of V5; the measurement over the blank split governs WHICH
    CELLS ARE COUNTED. "Every count that depends on [presence] is
    recounted from blank and non-blank cells alone, with no sentinel
    machinery anywhere in the verdict path" is the ratified plan's own
    sentence (P3-D3, owner decision 8, as narrowed by amendment A-P3-15
    clause 2, which struck "or declaration" from it and says why), and
    these settings are how it is met: naming those spellings as kept is
    the producer's own switch for "this is data, not a hole", so the
    recount is still the producer's own machinery over the same cells
    (V2.1) and not a second implementation of anything.

    The two never decide the same number. What this settings object may
    NOT be used for is the gate: a description built under it would say
    more about the file than describing that file on its own would
    publish, which is the one thing V5 forbids.

    WHAT "BLANKNESS" REACHES, AND WHAT IT DOES NOT (review item
    P3-V4-F1). V2.4 pins absence to blankness "by naming as kept data
    every non-blank spelling THE PRODUCER'S OWN BUILT-IN TABLES would
    read as an absence", and the scope in those words is the whole of
    it: `_KEPT_OVER_THE_SPLIT` is that table and nothing else. A
    spelling the PERSON declared to be "no value" is not in it and is
    not moved here. The reason is the reason the pinning exists -- a
    generated value can legitimately BE the text of a built-in marker
    (residual R-P2-13), so a file may not be failed for a collision with
    synthtwin's own vocabulary. Nothing of the kind is at stake in a
    spelling the description itself publishes as the source of its
    holes: the producer reads those cells as holes in every column of
    every file it describes, so counting them as values here would
    measure the file under a rule its description was not written under,
    and it did: twelve `XX` cells in the table a `--missing-value XX`
    description was written from turned that column into free text and
    put twenty-eight subchecks on MISSED.

    AND FROM CONTRACT VERSION 5 THAT SENTENCE HAS SOMETHING TO EXCLUDE
    (plan amendment A-P3-29). A spelling the person declared to be "no
    value" CAN now be one of this package's own words, because the
    settings block records which of them a declaration named and
    `declared_spellings` reads it back. So a built-in marker the
    description declares as missing is not moved to the kept side here:
    it stays a hole, exactly as the paragraph above says it should, and
    the producer's own refusal is what would otherwise be raised --
    naming one value both ways is a contradiction it declines to profile
    under, and the two settings this module builds may not manufacture
    one the person never typed.

    AND A STAND-IN NUMBER THE DESCRIPTION'S OWN VERDICT READS AS A HOLE
    IS NOT PINNED TO DATA EITHER (review item P3-V9-F5; plan amendment
    A-P3-35, validation method clause V2.4-A8). This is the same
    sentence as the two above, said about the third way a cell becomes
    absent. The blankness pin exists because a file may not be failed
    for colliding with synthtwin's own vocabulary; it does not exist to
    overrule what the description SAYS about a cell. And the description
    says it outright: contract 5 section 3.2 way 3 publishes, per
    column, the candidate, the verdict, the reason and the occurrences,
    so `read_as_missing` on `-999` is that description stating that a
    cell reading `-999` in that column is a hole. A 180-row column of
    168 ordinary decimals and twelve `-999` cells, checked against the
    description written from it, reported SEVENTEEN obligations MISSED
    -- both presence counts, both distinctness counts, three other
    counts, seven ladder rungs and all three moments -- with the
    incomplete reading's numbers printed beside them, on a table that is
    its own description's perfect match.

    WHAT IS DROPPED IS THE PIN, NOT THE MACHINERY. A stand-in the
    description settles as a hole is simply left out of the kept list,
    which hands the question back to the producer's own per-column
    sentinel rule under the settings the description was written with
    (`settings_for`). So the split description reaches the verdict the
    description publishes because it is the same rule over the same
    cells, and no second reading of `sentinel_verdicts` is implemented
    here -- V2.1 is met exactly as it is for every other measurement.

    WHY THE ANSWER IS TAKEN PER DOCUMENT WHEN THE VERDICT IS PER COLUMN.
    `taxonomy.Settings` names kept values for the whole table, so the pin
    can be dropped for a NUMBER and not for one column's use of it. The
    other direction was measured and is worse: pinning per document and
    unpinning nowhere is what printed the seventeen. Where one column
    reads `-999` as a hole and another reads it as data, both are then
    judged by the producer's own rule on the measured file -- which is
    what the description was written under, so the file it was written
    from agrees on both columns exactly.

    WHAT IT COSTS, and it is R-P2-13's own shape on the third class of
    marker. A twin whose generated numbers include a stand-in the
    description settles as a hole can now have those cells counted as
    holes here, where they used to be counted as data. It is bounded by
    the cells wearing that number, it needs the producer's outlier and
    share rules to fire on the twin's own values, and it is exactly the
    exposure the GATE side has carried all along, because `settings_for`
    never pinned anything.

    AND NEITHER IS A BUILT-IN WORD THE DESCRIPTION PUBLISHES AS THE
    SOURCE OF ITS OWN HOLES (review item P3-V10-F4; plan amendment
    A-P3-39, validation method clause V2.4-A10). The paragraph three
    above says a spelling the description publishes as the source of its
    holes has nothing of R-P2-13 at stake in it, and then said the
    built-in table at large stays pinned anyway. Both cannot be true,
    and the first one is the true one: `missing_by_source` is the
    description NAMING the spelling twelve of its holes wore, and
    reading that spelling as data here measures the file under a rule
    its description was not written under. It did, on the plainest run
    the product has: one column of sixty numbers and twelve `n/a` cells,
    profiled with no options at all, checked against its own
    description, reported TWENTY-EIGHT obligations MISSED and exited 3 --
    both presence counts, both distinctness counts, `n_not_numeric`,
    eleven ladder rungs, three moments and the rest, each with the
    pinned reading's number printed beside the description's own.

    WHERE THE PIN IS STILL REQUIRED, and this is the narrower boundary
    rather than a smaller version of the old one. A built-in text stays
    pinned on a description NO column of which publishes it as a hole
    source. On such a description the pin cannot reach a verdict on the
    file the description was written from, and the reason is structural:
    for the pin to move a verdict on a column, that column's own
    description must publish its split (`_split_is_published`), which
    asks that every absent cell of the column be blank or named by a key
    of `missing_by_source`. A cell the built-in table made absent is not
    blank, so it must be named by a key -- and a named key IS the
    publication this function now reads. So the two cases are exhaustive:
    either the spelling is published, and it is unpinned here, or the
    column pools it and `_governed` takes that column's verdicts from
    the file's own description instead. The one place a pooled spelling
    still reaches a number is the two presence COUNTS, which ask the
    weaker publication question of A-P3-5 clause 1, and that residual is
    stated at its size in the plan (R-P3-11) rather than papered over.

    WHAT IT COSTS, and it is R-P2-13's own shape on the FIRST class of
    marker -- the class the residual was written about. A twin holding a
    generated value that collides with a built-in word the description
    publishes as a hole source now has those cells counted as holes
    here. It needs the description to publish that word (so the table it
    was written from wore it, at or above the publication floor), and it
    needs the twin's own invention to land on the same spelling in some
    other column whose split is published. It is bounded by the cells
    wearing that word, and it is the same exposure A-P3-29 took for a
    built-in word the person declared and A-P3-35 took for a stand-in
    number -- said now about the one route those two left.
    """
    block = settings_for(description)
    # A mapping rather than a set, for the reason `kept_spellings` gives:
    # the offline policy accepts no method call on a value it cannot
    # trace, and `set.add` is one. The values are never read.
    found: dict[str, int] = {}
    for spelling in block.kept_values:
        found[spelling] = 1
    settled = _stand_ins_the_description_reads_as_holes(description)
    named = _built_in_words_the_description_names_as_holes(description)
    for spelling in _KEPT_OVER_THE_SPLIT:
        if _names_this_member(spelling, block.declared_missing_values):
            continue
        if _names_this_member(spelling, settled):
            continue
        if _names_this_member(spelling, named):
            continue
        found[spelling] = 1
    return dataclasses.replace(block, kept_values=tuple(sorted(found)))


def _names_this_member(member: str, recovered: "tuple[str, ...]") -> bool:
    """Whether anything recovered from the description names THIS member.

    `_explained_by` answers the DECLARATION's question -- would this
    declaration take a cell spelled this way -- and folds to do it. This
    answers the VOCABULARY's question, which for the one exact-spelling
    member is a different question with a different answer (contract
    C6-32, which names the validator's reconstruction as one of the
    places the one operation applies).

    The two came apart here. Somebody may declare a value of their
    own that folds onto the exact member, and their column then
    names that value among its own hole spellings. The validator reads
    it back as a declaration, compared it folded against the member, and took
    the member off the measured side's kept list -- so a file whose
    own cells wear the member exactly had them counted absent on a
    description that says nothing about the member at all.

    Guarantees: accepts a member and the recovered spellings; returns a
    truth value; raises TypeError if handed anything that is not text.
    No I/O of any kind.
    """
    if member in parsing.MISSING_TEXTS_EXACT:
        for declared in recovered:
            if parsing.missing_text_matches(declared, member):
                return True
        return False
    return _explained_by(member, recovered)


def _built_in_words_the_description_names_as_holes(
    description: contract.Profile,
) -> "tuple[str, ...]":
    """The built-in missing words some column publishes as a hole source.

    Guarantees:

    - Inputs: one loaded description. No file is read and no cell is
      consulted, so what comes back is a function of the DESCRIPTION
      alone.
    - Determinism: the returned tuple is sorted.
    - Errors raised: none.
    - Boundary: every spelling here is a member of this package's own
      built-in table of missing texts, written the one way
      `_BUILT_IN_TEXTS` writes it. **No text of anybody's table leaves
      this function**: a published key decides only WHICH of ten
      first-party words comes back, and the key itself never does.

    WHY A PUBLISHED KEY SETTLES IT OUTRIGHT. The producer has five ways
    to make a cell absent and it tries them in one order (`taxonomy.
    _split_missing`): a `--keep-value` rescue first, then a declaration,
    then a blank, then this table. A key of `missing_by_source` is a
    spelling some absent cell of that column wore. So a key that folds
    to one of these ten words is a cell the built-in table read as a
    hole unless a rescue took it first -- and a rescued value is present,
    so it is no column's hole and no key of this map. There is nothing
    left to check and nothing to guess.

    THE MATCH IS THE PRODUCER'S OWN DECLARATION IDENTITY, not an exact
    key lookup, for the reason `_holes_no_spelling_accounts_for` gives:
    `settings.declaration_matching` folds and trims, so a column
    publishing `" N/A "` names the same word as one publishing `n/a`,
    and the word that comes back is the vocabulary's own spelling
    either way. A key that reads as a NUMBER matches none of these ten,
    because no built-in missing text reads as one -- which is what
    `tests/test_p1r6f9_declared_values.py` asserts of the table itself --
    so a published `-999` is left to `_stand_ins_the_description_reads_
    as_holes`, where the column's own verdict answers for it.
    """
    # A mapping rather than a set, for the reason `kept_spellings` gives
    # (plan D6.2). The values are never read.
    found: dict[str, int] = {}
    for column in description.columns:
        for key in sorted(column.missing_by_source):
            for spelling in _BUILT_IN_TEXTS:
                # THE VOCABULARY'S OWN RULE, NOT THE DECLARATION'S
                # (contract C6-32, which names this reconstruction as
                # one of the places the one operation applies). Asking
                # `_explained_by` here folded both sides, so a column
                # publishing the key `nat` -- which it can, under a
                # declaration of the person's own -- was read as naming
                # the member `NaT` and un-pinned it from the measured
                # side's kept values. That is the exception coming
                # apart from the rule it excepts.
                if parsing.missing_text_matches(key, spelling):
                    found[spelling] = 1
    return tuple(sorted(found))


def _stand_ins_the_description_reads_as_holes(
    description: contract.Profile,
) -> "tuple[str, ...]":
    """The stand-in numbers some column of this description drops.

    Guarantees:

    - Inputs: one loaded description. No file is read and no cell is
      consulted, so what comes back is a function of the DESCRIPTION
      alone.
    - Determinism: the returned tuple is sorted.
    - Errors raised: none.
    - Boundary: every spelling here is one of this package's own three
      stand-in numbers, written the one way `_STAND_IN_SPELLINGS`
      writes them. A candidate the loader let through that is not one of
      the three names nothing, and no text of the description leaves
      this function.

    A published candidate is matched to the three at the EXACT number
    both denote, which is the identity the producer decides a candidate
    by -- so a description writing `-999.0` and one writing `-999` name
    the same stand-in here, as they do everywhere else in this module.
    """
    found: dict[str, int] = {}
    for column in description.columns:
        for verdict in column.sentinel_verdicts:
            if verdict.verdict != taxonomy.VERDICT_MISSING:
                continue
            exact = taxonomy.exact_of_spelling(verdict.candidate)
            if exact is None:
                continue
            for value, spelling in _STAND_IN_SPELLINGS:
                if exact == taxonomy.exact_of_number(value):
                    found[spelling] = 1
    return tuple(sorted(found))


def kept_spellings(description: contract.Profile) -> "tuple[str, ...]":
    """Every `--keep-value` the description was written under.

    Guarantees:

    - Inputs: one loaded description. Nothing is read from any file.
    - Determinism: the returned tuple is sorted, so the same
      description always gives the same tuple in the same order.
    - Errors raised: none.
    - Boundary: every spelling here is a member of the closed vocabulary
      contract 5 section 14.1 publishes -- ten words and three stand-in
      numbers, this package's own, identical in every installation.
      **No text of anybody's table can reach this tuple**, out of the
      description or out of the measured file, and the tuple is the same
      whether or not the named word occurs anywhere (contract 5 C5-16).

    IT IS THE WHOLE OF THE KEPT SIDE, AND THAT IS A PROOF RATHER THAN A
    HOPE (contract 5 section 6.4 and its C5-19; plan amendment A-P3-29).
    A rescue can only matter for a cell that would otherwise have been
    absent, and the producer has five ways to make a cell absent and no
    sixth: a blank, one of this package's built-in words, a stand-in
    number the column's own rule judged, and the person's own
    declaration by spelling or by number. A `--keep-value` reaches the
    first three only by naming a member of the vocabulary; it cannot
    reach the last two, because a value named both ways is refused
    before the table is opened; and a cell that would have been present
    anyway is unaffected by being rescued. So a rescue of anything else
    changes no cell's reading, and the two lists the settings block
    carries are the reading rule's kept half entire.

    WHAT THIS REPLACED, AND WHY IT IS DELETED RATHER THAN KEPT BESIDE
    (owner ruling 2026-08-17; plan amendments A-P3-27 and A-P3-29). Under
    contract version 4 the settings block recorded `kept_values` as a
    COUNT and never as text, so this function INFERRED the tuple from
    three facts the description publishes for other reasons: every
    `sentinel_verdicts` candidate whose reason reads `kept_by_you`,
    every published `levels[].label`, and every key of every level's
    `variants`. Those three routes are gone.

    - The `kept_by_you` route is a strict subset of what is read now: a
      candidate exists only for one of the three stand-in numbers, and a
      candidate is judged `kept_by_you` only where a `--keep-value`
      named it, so every spelling it brought back is a member of
      `built_in_numbers` today.
    - The two LABEL routes never answered this question at all. A label
      or a variant is a spelling of a cell the producer read as a VALUE,
      and naming a value as kept changes nothing: `_split_missing` only
      consults the kept set for a cell it would otherwise have called
      absent. The one case where a label CAN be such a spelling is a
      label that is one of this package's own words -- and that label
      exists only because a `--keep-value` rescued it, which is exactly
      what `built_in_texts` now records.

    Keeping them beside the two lists would have cost more than
    duplication. The inference reached only what a LABEL column
    publishes, so it answered "was this word rescued?" with "does some
    column publish it as a level?", and the witness that made this
    review round is the case where those two answers differ: two hundred
    readings and one `n/a`, described with `--keep-value n/a`, publishes
    no level and no variant and no verdict, so the inference brought
    back nothing and the table validated against its own genuine
    description reported seven obligations MISSED. That witness now
    misses nothing and is measured in full.
    """
    return _vocabulary_spellings(description.settings.kept_values)


def _vocabulary_spellings(
    record: contract.DeclarationRecord,
) -> "tuple[str, ...]":
    """One declaration record's named members, as spellings.

    The texts are written into the document in the vocabulary's own
    spelling already (contract 5 C5-17), so they are used as they
    stand. The numbers are written as numbers, and the producer's
    settings take spellings, so each is paired with a spelling that
    denotes it -- which is all the producer's matching rule asks of it.
    """
    # A mapping rather than a set: the offline policy accepts no method
    # call on a value it cannot trace, and `set.add` is one, while
    # setting a key is not (plan D6.2). The values are never read.
    found: dict[str, int] = {}
    for member in record.built_in_texts:
        found[member] = 1
    for number in record.built_in_numbers:
        for value, spelling in _STAND_IN_SPELLINGS:
            if number == value:
                found[spelling] = 1
    # AND THE THIRD LIST (plan amendment A-P4-1 item 3). A placeholder
    # day the person named is a value they kept, and a reconstruction
    # that stopped at two lists could not rebuild the reading rule of a
    # column whose placeholder they rescued.
    for day in record.built_in_dates:
        found[day] = 1
    return tuple(sorted(found))


def declared_spellings(description: contract.Profile) -> "tuple[str, ...]":
    """The spellings the description reads as "no value" BY DECLARATION.

    Guarantees:

    - Inputs: one loaded description. Nothing is read from any file.
    - Determinism: the returned tuple is sorted, so the same
      description always gives the same tuple in the same order.
    - Errors raised: none.
    - Boundary: every spelling here is either the description's OWN
      published text -- a key of a column's `missing_by_source`, which
      is what `synthtwin profile` publishes about the file it described
      -- or a member of the closed vocabulary of contract 5 section
      14.1, which is this package's own and carries no text of any
      table. Nothing is guessed.

    TWO PUBLISHED ROUTES, AND THE SECOND IS CONTRACT VERSION 5'S (review
    item P3-V4-F1; plan amendments A-P3-27 and A-P3-29).

    **The columns.** V2.2 said both declaration tuples come
    back empty "because the contract deliberately does not record
    declared spellings", and that is true of the SETTINGS BLOCK and
    false of the description: a column publishes the spelling of every
    hole whose count reaches `small_cell_floor`, in `missing_by_source`.
    So a `--missing-value` declaration IS published, wherever the floor
    lets the column name it, and recovering it is the same act as
    recovering a level's variants.

    **The settings block, for this package's own words.** Version 5
    records which members of the published vocabulary each declaration
    named, and the `--missing-value` record's two lists are read here
    exactly as `kept_spellings` reads the `--keep-value` record's.
    Naming a built-in word as missing does not make its cells absent --
    they already were -- but it moves them from class `(text-code)` to
    class `(declared-missing)`, and a report comparing class counts has
    to know that (contract 5 C5-20). Naming a stand-in NUMBER as missing
    does more: it takes those cells out before the column's own sentinel
    rule ever judges them.

    WHICH KEYS ARE A DECLARATION, DERIVED RATHER THAN GUESSED. The
    producer has exactly five ways to call a cell a hole
    (`taxonomy._split_missing`, `taxonomy._declared_numbers_removed` and
    the sentinel removal): the person's declaration by spelling, the
    person's declaration by number, a blank, one of the built-in missing
    texts, and a numeric stand-in the column's own verdict turned down.
    A published key is therefore a declaration unless it is one of the
    other three, which are all recognisable without consulting a cell:

    - a blank has no spelling to be a key of, and from contract version
      5 it has a count of its own, `n_missing_blank`, so no key of this
      map is ever a blank;
    - a key the built-in table already reads as an absence needs no
      declaration to be a hole, so it is skipped HERE and answered from
      the settings block instead, which says whether it was named;
    - a key that reads as one of the three numeric stand-ins is the
      sentinel machinery's business, judged per column and published per
      column in `sentinel_verdicts`, so it is skipped here and answered
      from the settings block in the same way. **Both skips stopped
      being losses at contract version 5**: each used to leave a
      declaration unrecovered and was recorded as a residual, and each
      now defers to a list that answers the same question outright.

    Every other key reads as neither a stand-in nor a built-in marker,
    and the producer has no remaining way to make it a hole. It is a
    declaration, and a number it denotes is matched as a number by the
    producer's own rule, which is why the SPELLING is enough to recover.

    TWO EXCLUSIONS OF VERSION 4 ARE GONE, AND CONTRACT VERSION 5 IS WHY
    (its C5-1 and C5-N5; plan amendments A-P3-27 and A-P3-28, and
    validation method clause V2.3-A3, which withdraws A-P3-19's fourth
    exclusion and the class-word exclusion beside it).

    The first was that a key could be one of this package's own five
    class words. Version 4 put `(blank)` and `(withheld)` into this map
    beside the person's spellings, so a key had to be tested against
    that vocabulary before it could be trusted -- and a table whose
    cells literally read `(withheld)` published a key nothing could tell
    from the pool. Version 5 gives the map one key space: a key is a
    spelling some cell held and nothing else, and the two counts moved
    to fields of their own. So the test is not merely unnecessary, it is
    WRONG -- it would walk past a spelling the table really wore.

    The second was that a key was not the exact spelling. Version 4
    passed each key through the DISPLAY BOUNDARY before storing it, so
    the map was not one-to-one: seventy-two rows whose holes are spelled
    ``X`` U+0001 ``Y`` published the same key as seventy-two rows
    spelled with those six printable characters, the two whole
    descriptions came out byte for byte alike, and reading the key as
    exact did both wrong things -- seven obligations reported MISSED
    against a file's own description, and a census of ZERO MISSED on a
    file that file's description does not describe. Version 5 stores the
    key character for character and escapes it where it is SHOWN, so a
    key IS the exact spelling and the two tables no longer describe
    alike. `parsing.shows_only_itself` is therefore no longer consulted
    here; it remains the property `tests/test_p3v7f1_escaped_declarations.py`
    proves about the display boundary itself.

    WHAT IS LEFT OPEN, at its size (contract 5 section 7; plan
    amendments A-P3-15, A-P3-26, A-P3-27 and A-P3-29). Exactly one kind
    of declaration is still not recovered here, and no version of this
    format closes it: **a word of the person's OWN** -- one that is not
    a member of the published vocabulary -- that no column names,
    because every cell wearing it sits below `small_cell_floor` or
    because the column's publication class permits no value of the
    table. Those are contract 5's two stated limits, its 7.1 and 7.2,
    and each names a group the format exists to refuse to publish.

    Every OTHER declaration comes back. A word of this package's own,
    however few cells wore it and whatever column it landed on, is in
    the settings block. A word of the person's own that any column names
    is in that column's map, exactly, whatever characters it holds.

    Both remaining cases are measured in
    `tests/test_p3v4f1_kept_values.py` and
    `tests/test_p3v7f1_escaped_declarations.py`, which turn red if
    either of them grows.
    """
    # A mapping rather than a set, for the reason `kept_spellings` gives
    # (plan D6.2). The values are never read.
    found: dict[str, int] = {}
    for spelling in _named_in_the_columns(description):
        found[spelling] = 1
    for spelling in _vocabulary_spellings(
        description.settings.declared_missing_values
    ):
        found[spelling] = 1
    return tuple(sorted(found))


def _named_in_the_columns(
    description: contract.Profile,
) -> "tuple[str, ...]":
    """The person's OWN declared words, out of the published columns.

    The half of `declared_spellings` that reads the table's own text: a
    key of some column's `missing_by_source` that the built-in table
    does not already read as an absence and that does not read as one
    of the three stand-in numbers. Whatever this returns is a word
    somebody typed after `--missing-value`, and whatever it does NOT
    return is a word of theirs no column names.

    It is separate from `declared_spellings` because
    `unrebuildable_columns` has to count these on their own: the
    settings block says how many words were named and how many of them
    were this package's, so the difference is how many were the
    person's, and this is what came back of them.
    """
    found: dict[str, int] = {}
    for column in description.columns:
        for spelling in sorted(column.missing_by_source):
            # The membership question is asked in ONE place for the whole
            # package (`taxonomy.is_published_vocabulary`), because the
            # summary and the command line now ask it too: they tell a
            # person which of their own words the description carries,
            # and three answers that could drift apart would put three
            # different sentences in front of one researcher about one
            # word. What stood here was this function's own copy of it.
            if taxonomy.is_published_vocabulary(spelling):
                continue
            found[spelling] = 1
    return tuple(sorted(found))


def _own_declarations_recovered(description: contract.Profile) -> int:
    """How many DECLARATIONS of the person's own the columns bring back.

    Not how many keys: how many words those keys are spellings of
    (review item P3-V9-F3's neighbour, P3-V9-F4; plan amendment
    A-P3-34). A declaration is matched at `settings.declaration_matching`'s
    own identity -- the exact number where the spelling reads as one,
    else the trimmed and folded spelling -- so `XX` and ` XX ` are two
    published keys of ONE declared word. The head count in the caller
    compares this against how many words the settings block says were
    named, and a comparison between a count of keys and a count of words
    is not a comparison at all.

    WHAT COUNTING KEYS COST, measured. Declare `XX` and `YY`; let a
    column of numbers publish twelve `XX` holes and twelve ` XX ` ones
    while a free-text column holds twelve `YY` holes and publishes no
    spelling of anything, because its publication class permits none.
    Two keys came back, two words were named, the head count saw no
    shortfall, the structural test is not asked on a column of that
    class -- so nothing was routed anywhere and the free-text column
    reported ELEVEN obligations MISSED against the table its own
    description was written from. Counting words instead: one word came
    back, two were named, the column is routed to NOT CHECKABLE, and the
    known limit of contract 5 section 7.2 is stated instead of a false
    failure printed.

    IT IS THE SOUND DIRECTION AND THE OTHER ONE IS NOT. What comes back
    is a subset of what was named, so a count of words that equals the
    named count means every named word came back; a count of KEYS can
    exceed the number of words and mask a loss.

    THE COST OF THE SOUND DIRECTION WAS ONE MORE SHAPE OF OVER-FIRE AND
    IT IS PAID OFF (review item P3-V9-F7; plan amendment A-P3-37). Both
    sides now count declarations at ONE identity: this one because
    A-P3-34 changed it, and the named side because `n_declared` counts
    declarations rather than keystrokes. `--missing-value XX
    --missing-value xx` is one word named and one word back, level, on a
    description whose reading rule is rebuildable -- where it used to be
    one back against two named, and 43 obligations left the checked
    census of a file that passes every one of them.

    Guarantees:

    - Inputs: one loaded description. No file is read.
    - Determinism: a fixed function of the description.
    - Errors raised: none.
    - Boundary: nothing is printed and no spelling leaves this function.
    """
    numbers: list[tuple[int, tuple[str, ...], int]] = []
    words: dict[str, int] = {}
    for spelling in _named_in_the_columns(description):
        exact = taxonomy.exact_of_spelling(spelling)
        if exact is None:
            words[parsing.folded(spelling)] = 1
        elif not _named(numbers, exact):
            numbers = numbers + [exact]
    return len(words) + len(numbers)


def _own_words_named(record: contract.DeclarationRecord) -> int:
    """How many words of the PERSON'S own one declaration named.

    `n_declared` counts every DIFFERENT value named that way; the two
    vocabulary lists name the ones that were this package's own. The
    difference is how many were the person's, which is the number the
    description can only carry through a column (contract 5 C5-18, and
    its C5-K3 is why this cannot go below zero on a document a loader
    accepted).

    THE SUBTRACTION IS EXACT, AND IT WAS AN UPPER BOUND UNTIL 2026-08-17
    (review item P3-V9-F7; plan amendment A-P3-37). `n_declared` counted
    KEYSTROKES, so `--missing-value n/a --missing-value " N/A "` wrote
    two beside a list holding one member and this returned one -- a word
    of the person's own that nobody typed. Nothing on this side could
    have repaired it: the document that names one word of their own and
    the document that names the same built-in word twice were the same
    document, so the fix had to be the producer's and is (contract 5
    C5-18 as amended). What this function does is unchanged; what
    changed is that the number it is handed answers the question it is
    being asked.
    """
    named = record.n_declared - len(record.built_in_texts)
    named = named - len(record.built_in_numbers)
    return named - len(record.built_in_dates)


def unrebuildable_columns(
    description: contract.Profile,
) -> "dict[str, str]":
    """The columns whose reading rule this description cannot rebuild.

    Guarantees:

    - Inputs: one loaded description, and nothing else. No file is read
      and no cell is consulted, so which columns are named here is a
      function of the DESCRIPTION alone -- exactly as V3.3 requires of
      anything that decides which obligations exist.
    - Determinism: a fixed function of the description.
    - Errors raised: none.
    - Boundary: the reasons are built from published counts. No
      spelling appears in any of them, out of the description or out of
      any file.

    WHAT THIS IS FOR (owner ruling 2026-08-16, plan amendment A-P3-26).
    `validate` is defined as: rebuild the reading rule from the
    description, re-describe the file with it, compare (V2.2). The
    description does not always pin the reading rule. Where it cannot be
    rebuilt, this validator used to re-describe the file under a rule
    the description was not written under and report the difference as a
    MISS, which is a confident false alarm on a file that is its own
    description's perfect match. The obligations counted over that
    column's cells go to the NOT-CHECKABLE census instead, with the
    sentence saying what the description lacks.

    WHAT IS LEFT FOR IT TO FIRE ON, AFTER CONTRACT VERSION 5 (owner
    ruling 2026-08-17; plan amendments A-P3-27, A-P3-28 and A-P3-29).
    A-P3-26 listed five routes by which the rule was lost. Three of them
    are gone from the FORMAT and one more is gone from this function:

    - the escaped key and the two key spaces in one map are closed by
      the producer, so a published spelling is now the exact one and a
      key reading `(withheld)` is somebody's cell rather than a pool;
    - **the KEPT side is closed entirely, and that removes the wider of
      A-P3-26's two costs.** That amendment asked its head count of
      EVERY column on the kept side, "because no published number says
      how many present cells were rescued". Version 5 publishes the
      rescued members of this package's own vocabulary, and contract 5
      section 6.4 proves those are the whole of what a rescue can
      change, so the question is DECIDED rather than assumed and the
      kept-side head count is deleted rather than narrowed;
    - and on the absence side the head count now asks only about words
      of the PERSON'S own, because the ones that were this package's
      come back from the settings block whatever the floor did.

    Two routes remain, they are contract 5 section 7's two, and no
    version of this format closes either: a word of the person's own
    pooled below `small_cell_floor`, and a word of the person's own on a
    column whose publication class permits no value of the table.

    IT IS DECIDABLE FROM THE DESCRIPTION EVEN WHERE THE RULE IS NOT
    RECOVERABLE, which is the whole reason this is possible. Two tests
    are run and the UNION is taken, because neither alone is both sound
    and complete:

    - the HEAD COUNT, per document: the settings block says how many
      words were named as "no value" and how many of them were this
      package's own, so the difference is how many were the person's,
      and `_own_declarations_recovered` is what came back of those.
      Fewer back than named means a word the reading rule needs is
      written nowhere. A declaration is a document-wide rule, so a
      column publishing nothing about it is still a column that could
      hold it.
    - the STRUCTURAL test, per column: the column publishes cells made
      absent by a declaration that no recovered spelling accounts for.
      Its inputs are `missing_by_class.declared_missing` and the
      published counts of the spellings `declared_spellings` brings
      back, matched at the producer's own declaration identity.

    WHY BOTH ARE STILL NEEDED. The head count counts WORDS and the
    structural test counts CELLS, and each catches what the other
    cannot. A word named that the table never held is invisible to the
    structural test and is exactly what the head count is for; a word
    the table held on a column that publishes its spellings is seen by
    the structural test cell by cell, wherever the head count comes out
    level.

    AND BOTH SIDES COUNT WORDS NOW, WHICH THEY DID NOT (review item
    P3-V9-F4; plan amendment A-P3-34). The head count used to compare
    how many KEYS came back with how many WORDS were named, and one
    declared word can be worn by several published keys -- ` XX ` and
    `XX` are two keys of one word. Two keys of one word then made a
    second word's loss invisible, and the structural test does not cover
    for it, because the column that lost the second word was a
    free-text one and the structural test is not asked there at all (the
    paragraph on C5-N6 below). Both halves reported nothing and the
    column reported eleven false misses. `_own_declarations_recovered`
    is what closed it.

    THE HEAD COUNT OVER-FIRES IN ONE PLACE, and it is asserted at its
    size rather than hoped away. A description written with
    `--missing-value` naming two words of the person's own, of which the
    table holds one, reports a gap that is not there. It is the safe
    direction: where the union over-fires it moves obligations to NOT
    CHECKABLE on a file that would have passed anyway, and the other
    direction prints a number about a file that is not true of it.
    Closing it needs the description to say which named words the table
    HELD, which is a fact about the table and not about the command
    line, so it does not close.

    THERE WERE TWO UNTIL 2026-08-17 (review item P3-V9-F7; plan
    amendment A-P3-37). The second was a description naming two
    SPELLINGS of one word -- `XX` and `xx`, or `n/a` and `" N/A "` --
    which the producer folds into a single declaration while
    `n_declared` counted the two somebody typed. Measured at 43
    obligations moved to NOT CHECKABLE on a file that passes every one
    of them. That one is CLOSED, at the producer, because it had to be:
    from the document alone, two spellings of one built-in word are
    indistinguishable from one built-in word and one word of the
    person's own. `n_declared` counts declarations now (contract 5
    C5-18 as amended) and the subtraction in `_own_words_named` is
    exact rather than an upper bound.

    THE ONE PLACE THE HEAD COUNT IS HELD BACK, and it is a proof rather
    than a preference. A column whose `missing_by_class` publishes no
    declared holes AND no pooled remainder is a column no declaration
    touched: the producer counts every absent cell into one of five
    classes and pools any class below the floor into the fifth, so a
    declared hole is either in `declared_missing` or inside `withheld`,
    and zero in both is zero of them. A word nobody's cell wore cannot
    change how that column reads, so listing its obligations would state
    a limit that is not this column's.

    AND THE ONE PLACE THE STRUCTURAL TEST IS NOT ASKED, which is new
    with version 5 and is the contract's own instruction (its C5-N6). A
    column whose publication class permits no value of the table
    publishes an EMPTY source accounting -- no key, no blank count, no
    pooled count -- because of its class and not because of its cells.
    The structural test has nothing to read there, and asking it anyway
    made every declared hole of such a column look unattributable even
    when the word that made them absent was one of this package's own
    and is written in the settings block. C5-N6 makes the two cases
    tellable apart from `role` and `structural_role`, which every block
    publishes, so this asks the head count there and nothing else.

    WHAT IT DOES NOT REACH. This says a column's reading rule cannot be
    rebuilt; it does not repair the description. The two remaining words
    are not recoverable, and each is a group the format exists to refuse
    to publish rather than an oversight.
    """
    settings = description.settings
    recovered = declared_spellings(description)
    own_named = _own_words_named(settings.declared_missing_values)
    own_recovered = _own_declarations_recovered(description)
    short = own_recovered < own_named
    unrebuildable: dict[str, str] = {}
    for column in description.columns:
        # A CELL RESCUED OVER ITS CORE, whose spelling this description
        # does not carry. On the affixed role a `--keep-value` names a
        # WHOLE CELL -- `-999 mg` -- and the rescue is recorded as a
        # verdict about the core `-999`, so the document holds the
        # decision without holding the word that made it. Rebuilding
        # the reading rule from the description would judge those cells
        # holes again, which is a rule the description was not written
        # under: a hundred-cell column checked against the file it was
        # written from reported fifteen obligations MISSED, every one
        # of them a number untrue of that file. The obligations go to
        # the NOT-CHECKABLE census instead, which is what this function
        # exists for.
        if _rescued_over_a_core(column):
            unrebuildable[column.name] = _core_rescue_not_recorded(
                _cells_rescued_over_cores(column)
            )
            continue
        if not _publishes_no_source_accounting(column):
            unnamed = _holes_no_spelling_accounts_for(column, recovered)
            if unnamed > 0:
                unrebuildable[column.name] = _holes_no_word_accounts_for(
                    unnamed
                )
                continue
        if short and _a_declaration_could_reach(column):
            unrebuildable[column.name] = _absence_words_not_recorded(
                own_named, own_recovered
            )
    return unrebuildable


def _rescued_over_a_core(column: contract.ColumnBlock) -> bool:
    """Whether a declaration rescued this column's cells over their cores.

    Read from the description alone, as V3.3 requires: the role says
    the stand-in pass ran over cores, and a verdict reading
    `kept_by_you` says a declaration decided one. What the document
    does NOT carry is the spelling that decided it -- the cell, not the
    core -- so the rule cannot be rebuilt from here.
    """
    if column.role != contract.ROLE_AFFIXED:
        return False
    for entry in column.sentinel_verdicts:
        if entry.reason == "kept_by_you":
            return True
    return False


def _cells_rescued_over_cores(column: contract.ColumnBlock) -> int:
    """How many cells the rescue kept, from the published verdicts."""
    found = 0
    for entry in column.sentinel_verdicts:
        if entry.reason == "kept_by_you":
            found = found + entry.n_occurrences
    return found


def _core_rescue_not_recorded(kept: int) -> str:
    """A column whose rescue this description records without its word."""
    return (
        f"the description records {_shown_count(kept)} cell(s) of this "
        f"column kept as values by a word you named, and the word names "
        f"the whole cell while the description records only the number "
        f"inside it, so " + UNREBUILDABLE_REASON_TAIL
    )


def _publishes_no_source_accounting(column: contract.ColumnBlock) -> bool:
    """Whether this column's publication class empties its accounting.

    Contract 5 section 6.10 as carried, and its C5-N6: on a column whose
    role publishes no value of the table -- free text, declared
    identifiers, record numbers, numbers this format cannot represent --
    `missing_by_source` is empty and both new counts are zero, whatever
    made the cells absent. The class is derivable from two fields every
    block publishes, so "this column publishes no source accounting" is
    always tellable from "this column had nothing to account for".
    """
    if column.structural_role == "identifier":
        return True
    return column.role in contract.ROLES_PUBLISHING_NOTHING


def _holes_no_spelling_accounts_for(
    column: contract.ColumnBlock, recovered: "tuple[str, ...]"
) -> int:
    """How many declared holes of this column no recovered word covers.

    `missing_by_class.declared_missing` is how many of this column's
    absent cells the producer made absent BY DECLARATION, and a key of
    `missing_by_source` carries how many cells wore that spelling. What
    the recovered declarations do not account for is what the validator
    will read back as data.

    THE KEYS ARE MATCHED AT THE PRODUCER'S OWN DECLARATION IDENTITY, not
    by exact key lookup (plan amendment A-P3-29).
    `settings.declaration_matching` has one permitted value -- the exact
    number where the value reads as one, else the trimmed and folded
    spelling -- and it is the rule that decided which cells the
    declaration took. Looking the key up exactly asked a narrower
    question than the producer asked and answered it wrongly twice: a
    declared stand-in comes back from the settings block as `-999` while
    the column's key is however the file wrote it, and a declaration
    worn by ` XX ` as well as `XX` publishes two keys for one word.
    Both reported cells as unattributable that the rebuilt rule
    attributes exactly.

    THE POOLED REMAINDER IS NOT ADDED HERE, and that is deliberate. A
    class whose count falls below the publication floor is pooled into
    `withheld`, so declared holes CAN hide there -- but a declaration
    hiding there is a declaration no column published, which is exactly
    what the head count in the caller catches. Adding the pooled
    remainder to this side would report a gap on the ordinary
    description that names one word and holds three blank cells, where
    the rule is rebuilt exactly.

    THE BLANK COUNT IS ADDED, on one condition. A person may name a
    blank as "no value" -- `--missing-value " "` folds to the empty
    spelling, which is a member of the published vocabulary -- and those
    cells are then class `(declared-missing)` while their count is in
    `n_missing_blank`, since a blank has no spelling to be a key of. So
    where the empty spelling is one of the recovered declarations, that
    count is one this rule accounts for.
    """
    accounted = 0
    for key in sorted(column.missing_by_source):
        if _explained_by(key, recovered):
            accounted = accounted + column.missing_by_source[key]
    if _explained_by("", recovered):
        accounted = accounted + column.n_missing_blank
    unnamed = column.missing_by_class.declared_missing - accounted
    return max(0, unnamed)


def _explained_by(spelling: str, recovered: "tuple[str, ...]") -> bool:
    """Whether some recovered declaration takes a cell spelled this way.

    The producer's own rule, written once: a declaration and a cell that
    both read as numbers are the same when they denote the same number,
    and otherwise they are the same when their trimmed, case-folded
    spellings are equal (`settings.declaration_matching`, whose one
    permitted value says exactly this).
    """
    exact = taxonomy.exact_of_spelling(spelling)
    folded = parsing.folded(spelling)
    for declared in recovered:
        other = taxonomy.exact_of_spelling(declared)
        if exact is not None and other is not None:
            if exact == other:
                return True
            continue
        if exact is None and other is None and folded == parsing.folded(
            declared
        ):
            return True
    return False


def _a_declaration_could_reach(column: contract.ColumnBlock) -> bool:
    """Whether any cell of this column was made absent by a declaration.

    Not "was it", but "could it have been", which is the question the
    description answers. The producer counts every absent cell into one
    of five classes and pools any class whose count falls below the
    publication floor into the fifth, so a cell a declaration made
    absent is counted either in `declared_missing` or inside the pooled
    `withheld` remainder. Both zero is a column no declared word
    appeared in, whatever words the settings block says were named.
    """
    classes = column.missing_by_class
    return classes.declared_missing > 0 or classes.withheld > 0


# -- V4: the corner classifier, written from the specification --------


def corners_of(
    description: contract.Profile,
) -> "dict[str, tuple[str, ...]]":
    """Which lesser outcomes the ratified plan names for this profile.

    Guarantees:

    - Inputs: one loaded description, and nothing else. A corner is a
      condition on published numbers, so no file is read and no cell is
      consulted.
    - Determinism: the answer is a pure function of the description;
      the returned tuples are in the fixed order of `CORNERS`.
    - Errors raised: none.
    - Boundary: this is INDEPENDENT code. The generator decides the
      same question from its own text and the two are compared in the
      suite; importing its planner would share every planner defect
      with the generator this is a second opinion on.

    Returns one entry per column that has a corner, keyed by the
    column's published name. A column with none does not appear.
    """
    found: dict[str, tuple[str, ...]] = {}
    for column in description.columns:
        corners: list[str] = []
        facts = column.facts
        if isinstance(
            facts, contract.IdentifierFacts
        ) and _identifier_is_infeasible(column, facts):
            corners = corners + [CORNER_IDENTIFIER_INFEASIBLE]
        if isinstance(
            facts, contract.DatetimeFacts
        ) and _offsets_are_withheld(facts):
            corners = corners + [CORNER_DATETIME_OFFSETS_WITHHELD]
        if isinstance(
            facts, contract.LabelFacts
        ) and _label_variants_are_short(column, facts):
            corners = corners + [CORNER_LABEL_VARIANTS_SHORT]
        # G12.8's corner is asked of the QUANTITATIVE facts, so a column
        # whose numbers are held inside its own facts reaches it: an
        # affixed column's cells stand one for one with its cores under
        # a shared pair, so the supply its core spellings carry is the
        # supply its cells carry.
        quantitative = _quantitative(facts)
        if isinstance(
            quantitative, contract.NumericFacts
        ) and _numeric_spellings_are_short(column, quantitative):
            corners = corners + [CORNER_NUMERIC_SPELLINGS_SHORT]
        if corners:
            found[column.name] = tuple(corners)
    return found


def _identifier_is_infeasible(
    column: contract.ColumnBlock, facts: contract.IdentifierFacts
) -> bool:
    """True when the published facts cannot supply the spellings asked for.

    Owner decision 6's corner, and it is the FAMILY capacity rule of
    method G9.4 rather than a ceiling of this module's own invention
    (review item P3-V6-F1). The version this replaced summed
    `alphabet ** length` over the published range with the alphabet
    read off one published count -- ten characters where
    `n_code_alphabet` is zero, thirty-six otherwise -- and neither
    number is a domain this product writes from. A declared column of
    eleven different one-character values outside the code alphabet
    was called infeasible by it while the shipped generator wrote all
    eleven, and a candidate file whose whole identifier column had
    collapsed to one repeated value then lost its raw-distinctness,
    folded-distinctness and occurrence-multiset checks and received a
    passing report.

    THE DIRECTION THIS ARITHMETIC IS SAFE IN, stated before the rule:
    what is asked for is the published count of groups, taken exactly,
    and every supply below is an UPPER bound on what the construction
    writes, so this returns True only where no construction of the
    method can answer the description -- which is the direction that
    matters, because a corner claimed in error REMOVES three checks
    from the report.

    The rule, from methods G9.5 step 4 and G9.6:

    - Each present cell sits in one of three alphabet bands, and the
      description's own two counts fix how many sit in each:
      `n_all_digits` are figures alone, a further
      `n_code_alphabet - n_all_digits` are written in the code
      alphabet, and the rest stand outside it.
    - Every cell of one GROUP carries the same spelling, so a group
      lies wholly in one band. A band whose cells number `cells` can
      therefore hold no more groups than the smallest published groups
      fit into that many cells, and no more than its own domain can
      spell. The smaller of those two is all it can supply.
    - Where `all_whole_numbers` is published and every present cell
      reads as a number the format holds, each band writes the
      whole-number family G9.6 fixes for it, which is a narrower domain
      than the band's own alphabet.

    THE THREE BANDS ARE ASKED TOGETHER AND NOT ONE AT A TIME, which is
    the shape a single-band reading misses: a 115-row column of
    one-character codes publishing 89 groups splits 16 cells into the
    figures, 53 into the code alphabet and 46 outside it, and no ONE of
    those bands is short on its own -- while ten, fifty-three and
    twenty-five spellings are eighty-eight between them and the
    description asks for eighty-nine.

    Where the three together fall short of the published groups, no
    packing of any kind reaches the published distinctness, the twin
    repeats values, and owner decision 6's three REPORT-ONLY facts are
    what the description is owed instead.

    TWO THINGS ROUND 7 ADDED, both of them the same correction -- the
    supply was above what the construction can actually write, which is
    the direction that reports a conforming twin MISSED (review item
    P3-V7-F2):

    - the supply of a band is the FAMILY's, not the alphabet's. Above
      one character this section used to count every string the
      positional rules of G9.1 leave, which is a domain no family of
      G9.6 writes from: the widest band spells 8,460 values two
      characters wide by that reading and 2,538 by its own family's, so
      a producer-derived column of 2,539 two-character values was called
      feasible while the shipped generator necessarily repeated;
    - a band whose cells number `cells` needs at least
      `ceil(cells / widest group)` different spellings to cover them,
      and where its own supply is below that the description is
      infeasible however the other two bands are packed. That is G9.4's
      own sentence, and the summed reach below can miss it because it
      lets the smallest published groups answer for every band at once.
    """
    low = facts.min_length
    high = facts.max_length
    if low < 1 or high < low:
        # A range the loader cannot produce. No corner is the safe
        # answer: it keeps every check the report would otherwise drop.
        return False
    sizes = _group_sizes(facts.n_distinct_by_occurrences)
    groups = _group_total(sizes)
    if groups < 1:
        return False
    coded = facts.n_code_alphabet - facts.n_all_digits
    outside = column.n_present - facts.n_code_alphabet
    if coded < 0 or outside < 0:
        # The two published counts do not divide the cells the way G9.5
        # step 4 divides them -- a value in figures alone is a value the
        # code alphabet holds, so no document a producer writes gets
        # here. With no band split to reason from there is no supply to
        # compare against, and claiming the corner on a reading this
        # section does not describe would take three checks off a column
        # for a reason nobody could state.
        return False
    # Every present cell reads as a number the format holds, so the
    # four class counts of X2 leave only the whole-number families.
    whole = facts.all_whole_numbers and column.n_numeric == column.n_present
    widest = _widest_group(facts.n_distinct_by_occurrences)
    split = (
        (_BAND_DIGITS, facts.n_all_digits),
        (_BAND_CODE, coded),
        (_BAND_WIDE, outside),
    )
    supply: list[int] = []
    for band, cells in split:
        if cells < 1:
            supply = supply + [0]
            continue
        room = _identifier_capacity(column, facts, band, whole)
        if _band_falls_short(cells, widest, room):
            return True
        supply = supply + [room]
    reach = 0
    for place, pair in enumerate(split):
        if pair[1] < 1:
            continue
        reach = reach + min(supply[place], _most_groups(sizes, pair[1]))
        if reach >= groups:
            return False
    return reach < groups


def _band_falls_short(cells: int, widest: int, room: int) -> bool:
    """Whether one band cannot cover its own cells, whatever the rest do.

    METHOD G9.4'S OWN SENTENCE, and the free-text refusal reads the same
    one: a band answering for `cells` of them needs at least
    `ceil(cells / widest group)` different spellings, because every cell
    of one group carries the same spelling and no group is wider than
    the widest the description publishes. Where its own domain cannot
    supply that many, no packing of the other two bands repairs it.

    IT IS ASKED BESIDE THE SUMMED REACH AND NOT INSTEAD OF IT (review
    item P3-V7-F2). The summed reach lets the smallest published groups
    answer for every band at once, so it can read a supply the bands
    cannot jointly deliver: a fifty-four-cell column of one-character
    values whose widest group is two rows, splitting fifty-one cells
    outside the code alphabet, is short by exactly one spelling there
    and the summed reach reads twenty-eight against twenty-eight.
    """
    if cells < 1 or widest < 1:
        return False
    return _rounded_up(cells, widest) > room


def _group_sizes(occurrences: "dict[str, int]") -> "tuple[tuple[int, int], ...]":
    """The published repetition pattern as (size, how many groups) pairs.

    The map's keys are row counts written in base ten and leading zeros
    are padding that does not change the number (G9.5 step 1), so two
    keys can name the same size; the pairs are returned in ascending
    size order and a caller that walks them takes the smallest groups
    first. A key that is not a row count cannot come through the strict
    loader, and one that did is skipped, which asks for no corner --
    the safe direction.

    THE KEY IS READ AS THE FIGURES IT IS (review item P3-V8-F5). It
    used to be read through the reader that answers in binary64, which
    is exact only below nine quadrillion and silently one row out above
    it -- and a size one row out divides a band's cells into one group
    more than the description names.
    """
    found: list[tuple[int, int]] = []
    for key in sorted(occurrences):
        size = contract.occurrence_size(key)
        if size is None:
            continue
        found = found + [(size, occurrences[key])]
    return tuple(sorted(found))


def _group_total(sizes: "tuple[tuple[int, int], ...]") -> int:
    """How many groups the published pattern names in all."""
    total = 0
    for pair in sizes:
        total = total + pair[1]
    return total


def _most_groups(
    sizes: "tuple[tuple[int, int], ...]", cells: int
) -> int:
    """The most groups whose sizes can fit inside ``cells`` cells.

    An UPPER bound on how many groups the bands other than one can hold
    between them, so that `groups - this` is a lower bound on the groups
    that one band must hold. Taking the smallest groups first is what
    maximizes the count, since every group taken costs at least as much
    room as any group it was preferred to.
    """
    room = cells
    found = 0
    for pair in sizes:
        size = pair[0]
        if size < 1 or size > room:
            continue
        taken = min(pair[1], room // size)
        found = found + taken
        room = room - taken * size
    return found


def _identifier_capacity(
    column: contract.ColumnBlock,
    facts: contract.IdentifierFacts,
    band: str,
    whole: bool,
) -> int:
    """How many record numbers one band can spell over a length range.

    THE CLASSES ARE PART OF THE QUESTION (method G9.6). A group of a
    declared column belongs to one of four classes, the description
    publishes how many cells each class holds, and a class the
    description gives no cell to writes nothing here. Two of the four --
    a well-formed number too large or too small to hold, and a notation
    that conflicts with itself inside accounting parentheses -- are
    G10.3's constructions, whose widths this section does not count, so
    a column publishing either is given a supply nothing can exceed:
    that keeps its three distinctness checks, which is the direction a
    wrong answer costs least.
    """
    if column.n_out_of_range > 0 or column.n_contradictory > 0:
        return _SATURATION
    numbers = column.n_numeric > 0
    total = 0
    for length in range(facts.min_length, facts.max_length + 1):
        total = total + _identifier_capacity_at(band, length, whole, numbers)
        if total >= _SATURATION:
            return _SATURATION
    return total


def _identifier_capacity_at(
    band: str, length: int, whole: bool, numbers: bool = True
) -> int:
    """An upper bound on one band's record numbers at one length (G9.6).

    Where every value IS a whole number, G9.6 fixes one family per band
    and each is far narrower than the alphabet:

    - figures alone open with a digit that is not zero, so a value's
      length is its count of figures;
    - inside the code alphabet the form is `<digits>e0`, which needs
      two characters beyond its digits and has nothing at all to write
      at one character -- one character that reads as a whole number IS
      a figure. At exactly two characters the only spellings are the
      ten that open with a sign, which owner decision 9 permits here;
    - outside the code alphabet the form is `<digits>.`, one character
      beyond its digits and empty at one character for the same reason.

    Where it does not, TWO families remain and this counts both: the
    band's ordinary-text walk and, where the description gives the
    numbers class a cell, the ordinary-number family of G9.5 step 3.
    The version this replaces counted every string the positional rules
    of G9.1 leave at that length, which is not a domain any family
    writes from and is far above all of them together above one
    character -- 8,460 two-character values in the widest band against
    the 2,538 its family actually holds (review item P3-V7-F2).
    """
    if whole:
        if band == _BAND_DIGITS:
            return (_DIGIT_SIZE - 1) * _to_the_power(_DIGIT_SIZE, length - 1)
        if band == _BAND_CODE:
            if length == 2:
                return _DIGIT_SIZE
            if length < 2:
                return 0
            return _to_the_power(_DIGIT_SIZE, length - 2)
        if length < 2:
            return 0
        return _to_the_power(_DIGIT_SIZE, length - 1)
    if length < 1:
        return 0
    if length == 1:
        if band == _BAND_DIGITS:
            # One figure reads as a number whatever else it is, so this
            # band carries no cell of the ordinary-text class at all.
            return _number_family_at(_BAND_DIGITS, 1) if numbers else 0
        # At one character the value IS its own leading character, so
        # G9.4's counting settles every family at once and the two
        # spellings that already mean "no value" are counted out.
        return _one_character_values(band)
    total = _text_family_at(band, length)
    if numbers:
        total = total + _number_family_at(band, length)
    return total


def _text_family_at(band: str, length: int) -> int:
    """The ordinary-text family of one band at one length (G9.2, G9.6).

    The band's own alphabet counted by plain mixed-radix arithmetic,
    with the leftmost character drawn from the smaller set that holds
    the value inside its band -- which is what makes this a FAMILY's
    count rather than an alphabet's. Figures alone read as a number
    whatever else they are, so no cell of this class is ever written in
    that band.

    The widest alphabet holds the space and the two narrower ones do
    not, and the space is refused at the last position as well as the
    first (G9.1), so the last position of a wide spelling carries one
    character fewer than its alphabet has.
    """
    if band == _BAND_DIGITS:
        return 0
    if band == _BAND_CODE:
        return _head_values(_BAND_CODE) * _to_the_power(_CODE_SIZE, length - 1)
    return (
        _head_values(_BAND_WIDE)
        * _to_the_power(_WIDE_SIZE, length - 2)
        * (_WIDE_SIZE - 1)
    )


def _number_family_at(band: str, length: int) -> int:
    """The ordinary-number family of one band at one length (G9.5 step 3).

    In figures alone it is a plain number, so every string of figures of
    that width is one. Inside the code alphabet it carries an exponent
    and outside it a decimal point, each costing characters the figures
    themselves do not need: at exactly two characters the only spellings
    are the ten that open with a sign, and above that two characters go
    to the notation.
    """
    if band == _BAND_DIGITS:
        return _to_the_power(_DIGIT_SIZE, length)
    if length < 2:
        return 0
    if length == 2:
        return _DIGIT_SIZE
    return _to_the_power(_DIGIT_SIZE, length - 2)


def _head_values(band: str) -> int:
    """How many characters one band permits as a value's leftmost.

    The band rule of method G9.5 step 4 and the positional rules of
    G9.1, counted through the shipped classifier exactly as
    `_one_character_values` counts them -- less the one question that
    belongs to a whole value rather than to its first character, since
    a spelling two characters wide is not made to mean "no value" by
    the character it opens with.
    """
    found = 0
    for code in range(_WIDE_LOW, _WIDE_HIGH):
        letter = chr(code)
        if band == _BAND_CODE and not parsing.is_code_text(letter):
            continue
        if band == _BAND_CODE and parsing.is_digit_text(letter):
            continue
        if band == _BAND_WIDE and parsing.is_code_text(letter):
            continue
        if letter == _SPACE:
            continue
        if letter in _FORMULA_LEADERS:
            continue
        found = found + 1
    return found


def _offsets_are_withheld(facts: contract.DatetimeFacts) -> bool:
    """True when the offset map is the single withheld key (P2-D9)."""
    if len(facts.utc_offsets) != 1:
        return False
    return taxonomy.SUPPRESSED_LABEL in facts.utc_offsets


def _label_variants_are_short(
    column: contract.ColumnBlock, facts: contract.LabelFacts
) -> bool:
    """True when the published spellings cannot reach raw distinctness.

    The count `S` of method G12.7: one spelling for each published
    variant, one for each variant the floor held back, one for each
    level whose variants do not cover its own count, and one for each
    level held back whole. Where `S` reaches the published raw count the
    fact is exact and there is no corner; where it falls short the
    envelope of G12.7 is what the twin owes instead.
    """
    supply = _spelling_supply(column, facts, column.n_distinct)
    return supply is not None and supply != column.n_distinct


def _numeric_spellings_are_short(
    column: contract.ColumnBlock, facts: contract.NumericFacts
) -> bool:
    """True when the permitted spellings do not settle distinctness.

    The `supply` of method G12.8, read off the published map: all the
    `plain` cells together carry one spelling of one value, and every
    other style carries the leading-zero family, so its cells can each
    carry their own. Where the supply MEETS the published count the two
    ends of G12.8's envelope meet on it and the fact is exact -- the
    ordinary case. Where they differ the envelope is what the twin owes,
    AND IT IS TWO-SIDED IN BOTH DIRECTIONS.

    That last word is round 7's correction (review item P3-V7-F4). This
    predicate used to ask only whether the supply fell SHORT, so a
    description whose own permitted spellings force MORE identities than
    it publishes -- a floored style map naming fifteen leading-zero
    cells on a column publishing nine different values -- was given the
    exact bar, and the shipped generator's twin, which G12.8 authorizes
    at twelve, was reported MISSED against its own description.

    AND IT IS ASKED OF EACH COUNT WITH THAT COUNT'S OWN BUDGET (review
    item P3-V8-F4). G6.5 allocates the spelling budget separately for
    the raw count and for the folded one, so the two bounds are two
    different numbers on a column whose two published counts differ, and
    reading one of them for both would put a bar drawn from the raw
    allocation on the folded fact.
    """
    column = _core_column(column)
    quantitative = _quantitative(facts)
    if not isinstance(quantitative, contract.NumericFacts):
        return False
    facts = quantitative
    for published in (column.n_distinct, column.n_distinct_folded):
        supply = _spelling_supply(column, facts, published)
        ceiling = _spelling_ceiling(column, facts, published)
        if supply is None or ceiling is None:
            return False
        if supply != published or ceiling != published:
            return True
    return False


# -- V9 and V4.3: the refusals that mean no conforming twin exists ----


def refusal_of(description: contract.Profile) -> str:
    """The name of the G12 refusal this description meets, or "".

    Guarantees:

    - Inputs: one loaded description. No file is read.
    - Determinism: a pure function of the description.
    - Errors raised: none -- this NAMES a refusal, it does not raise
      one; `measure` turns the name into a message.
    - Boundary: all four refusals method G12 fixes are decided here,
      each from the published numbers its own passage names. The fourth
      is decided at the reach a validator can settle without rebuilding
      the planning stage V1.4 keeps out, and the comment on
      `REFUSAL_DOMAIN_TOO_SMALL` says exactly where that reach ends.
    """
    for column in description.columns:
        facts = column.facts
        if isinstance(facts, contract.NumericFacts) and (
            facts.n_zero + facts.n_negative > column.n_numeric
        ):
            return REFUSAL_COUNTS_CONTRADICT
        if isinstance(facts, contract.TextFacts):
            if facts.words.maximum > (facts.length.maximum + 1) // 2:
                return REFUSAL_WORDS_EXCEED_LENGTH
            if facts.words.minimum > (facts.length.minimum + 1) // 2:
                return REFUSAL_WORDS_EXCEED_LENGTH
            if _too_few_spellings(column, facts):
                return REFUSAL_DOMAIN_TOO_SMALL
        if isinstance(facts, contract.IdentifierFacts) and (
            facts.all_whole_numbers
        ):
            if facts.max_length == 1 and facts.n_all_digits < column.n_present:
                return REFUSAL_WHOLE_NUMBERS_NEED_ROOM
            if facts.min_length == 1 and facts.n_all_digits == 0:
                return REFUSAL_WHOLE_NUMBERS_NEED_ROOM
    return ""


def _too_few_spellings(
    column: contract.ColumnBlock, facts: contract.TextFacts
) -> bool:
    """Whether this column asks for more spellings than it can be given.

    METHOD G9.4, AT THE REACH THE PUBLISHED FACTS SETTLE. Each cell of a
    column of text sits in one of three alphabet bands, and which band
    is fixed by the two counts the description publishes: `n_all_digits`
    cells are written from the digits, a further
    `n_code_alphabet - n_all_digits` from the code alphabet, and every
    remaining cell from the wide one (G9.5 step 4). Every cell of one
    GROUP carries the same spelling, so a group lies wholly in one band,
    and a band answering for `cells` of them needs at least
    `ceil(cells / widest group)` different spellings. Where a band
    cannot supply that many at the column's own published lengths, no
    packing of any kind can, and the walk of G9.2 must run out.

    Every capacity below is an UPPER bound on what the construction
    writes -- which is the direction G9.4 fixes and the direction that
    makes this safe: a description a twin exists for can never be
    refused by it. It is not the whole question, and the comment on
    `REFUSAL_DOMAIN_TOO_SMALL` says which part it leaves.

    A column of unrepresentable numbers is the other role G9.4's table
    sends to this refusal and is not asked about here, for a reason of
    its own: it publishes no length fact at all -- deliberately, so that
    two columns of overflowing values four hundred and four thousand
    characters wide describe identically -- so there is no published
    ceiling for a demand to exceed.
    """
    widest = _widest_group(facts.n_distinct_by_occurrences)
    if widest < 1:
        return False
    low = facts.length.minimum
    high = facts.length.maximum
    if low < 1 or high < low:
        return False
    for band, cells in (
        (_BAND_DIGITS, facts.n_all_digits),
        (_BAND_CODE, facts.n_code_alphabet - facts.n_all_digits),
        (_BAND_WIDE, column.n_present - facts.n_code_alphabet),
    ):
        if cells < 1:
            continue
        if _rounded_up(cells, widest) > _band_capacity(band, low, high):
            return True
    return False


def _widest_group(occurrences: "dict[str, int]") -> int:
    """The largest repetition count the multiplicity map publishes.

    The map's keys are row counts written in base ten, and leading
    zeros are padding that does not change the number (G9.5 step 1). A
    key that is not a row count at all cannot come through the strict
    loader, and one that did would leave this at zero, which asks for no
    refusal -- the safe direction.

    THE KEY IS READ AS THE FIGURES IT IS (review item P3-V8-F5). Read
    through the binary64 reader this used to ask, the key
    `'9007199254740993'` came back one row short, ten one-character
    figures were told they had to cover eleven groups, and a validate
    run refused a description a twin exists for with the sentence that
    no file can be its twin.
    """
    widest = 0
    for key in occurrences:
        size = contract.occurrence_size(key)
        if size is None:
            continue
        widest = max(widest, size)
    return widest


def _band_capacity(band: str, low: int, high: int) -> int:
    """How many different spellings one band holds over a length range."""
    total = 0
    for length in range(low, high + 1):
        total = total + _capacity_at(band, length)
        if total >= _SATURATION:
            return _SATURATION
    return total


def _capacity_at(band: str, length: int) -> int:
    """An upper bound on one band's spellings at one length (G9.1, G9.4).

    The positional rules are G9.1's: the first and last character is
    never a space, and the first is never one of the four a spreadsheet
    reads as the start of a formula. The band rules are G9.5 step 4's: a
    code-alphabet value carries a character that is not a figure, so it
    is not counted as all-figures, and a wide value carries one outside
    the code alphabet, so it is not counted as code.

    At length one every rule bites on the same character and there is no
    arithmetic to do: the characters are counted one by one, through the
    shipped classifier, which is where the twenty-five of G9.4 comes
    from. Above length one the bound is deliberately the loose one --
    only the positional rules, not the band rule, which could otherwise
    under-count a construction that places its band character elsewhere.
    """
    if length < 1:
        return 0
    if band == _BAND_DIGITS:
        return _to_the_power(_DIGIT_SIZE, length)
    if length == 1:
        return _one_character_values(band)
    if band == _BAND_CODE:
        # Every code character but the one formula leader it holds.
        first = _CODE_SIZE - 1
        return first * _to_the_power(_CODE_SIZE, length - 1)
    first = _WIDE_SIZE - 1 - len(_FORMULA_LEADERS)
    last = _WIDE_SIZE - 1
    return first * _to_the_power(_WIDE_SIZE, length - 2) * last


def _one_character_values(band: str) -> int:
    """How many one-character values one band can hold, counted out.

    Every character of the printable range is asked the same four
    questions the construction asks: is it in this band, is it the space
    the first and last character may not be, is it one of the four
    leaders the first character may not be, and is it one of the
    spellings that already mean "no value" -- which a made-up value may
    never be, or the cell it is written into would read as absent.
    """
    found = 0
    for code in range(_WIDE_LOW, _WIDE_HIGH):
        letter = chr(code)
        if band == _BAND_CODE and not parsing.is_code_text(letter):
            continue
        if band == _BAND_CODE and parsing.is_digit_text(letter):
            continue
        if band == _BAND_WIDE and parsing.is_code_text(letter):
            continue
        if letter == _SPACE:
            continue
        if letter in _FORMULA_LEADERS:
            continue
        if parsing.is_missing_text(letter):
            continue
        found = found + 1
    return found


def _to_the_power(base: int, exponent: int) -> int:
    """``base`` to the ``exponent``, stopping at the saturating ceiling.

    G9.4's own rule: every power stops accumulating once it passes the
    ceiling, so a description publishing a four-thousand-character
    length costs a few dozen multiplications rather than an integer
    nobody can hold.
    """
    total = 1
    for _step in range(exponent):
        total = total * base
        if total >= _SATURATION:
            return _SATURATION
    return total


# -- reading the measured file ----------------------------------------


def _read_bytes(place: pathlib.Path) -> bytes:
    """The file's bytes.

    The path is rebuilt here rather than used as it arrives, which is
    the shape the offline audit reads: a value an allowlisted API built
    is a value whose methods that audit has already checked, and a
    parameter is not (plan D6.2).
    """
    file_path = pathlib.Path(place)
    return file_path.read_bytes()


def _read_utf8(place: pathlib.Path) -> "str | None":
    """The file as UTF-8 text, or None when its bytes are not UTF-8.

    THE BYTES ARE DECODED AND NOT RE-READ, so that no line ending is
    translated on the way in (review item P3-V3-F6). The reader opens
    the measured file with `newline=""` and translates nothing: a
    carriage return inside a quoted value stays the character it is.
    Reading the same file as text in the ordinary way turns every one of
    them into a line feed, and this module then stood in for a reader
    that had read something else -- so a conforming twin whose column
    name holds a carriage return read back under a name it does not
    have, and missed its names, its order and its header presence. Every
    walk below is written for untranslated text (`_split_lines`), and
    this is where it gets it.

    The bytes are turned into text by the BUILT-IN and not by a method
    of their own: the offline audit accepts no method call on a value it
    cannot trace, and the one accepted way to obtain a path's bytes
    hands back exactly such a value (plan D6.2). `str(data, "utf-8")` is
    `data.decode("utf-8")` written the way the audit reads.

    The path is rebuilt here for the reason `_read_bytes` gives: a value
    an allowlisted API built is a value whose methods the offline audit
    has already checked, and a parameter is not (plan D6.2).
    """
    file_path = pathlib.Path(place)
    data = file_path.read_bytes()
    try:
        return str(data, "utf-8")
    except UnicodeDecodeError:
        return None


def _read_fallback(place: pathlib.Path) -> str:
    """The file as text in the reader's FALLBACK encoding.

    Latin-1 maps every byte to a character, so this reads any file at
    all -- which is the point: a file whose bytes are not UTF-8 still
    has a first row, and the reader still reads it, so the header
    question below has to be settled on the same text the reader would
    settle it on. Decoded rather than re-read, for the reason
    `_read_utf8` gives.

    The path is rebuilt here for the reason `_read_bytes` gives.
    """
    file_path = pathlib.Path(place)
    data = file_path.read_bytes()
    return str(data, "latin-1")


def _starts_with_a_mark(data: bytes) -> bool:
    """True when the file's first bytes are a UTF-8 byte-order mark.

    A column name that genuinely begins with U+FEFF is written QUOTED,
    so the file's first byte is the quote and the mark that follows is
    inside a field rather than in front of the file. That exception is
    why this looks at the file's first three bytes and at nothing else.
    """
    return data[:3] == b"\xef\xbb\xbf"


def _a_return_ends_a_line(text: str) -> bool:
    """True when a carriage return in this file ends one of its lines.

    THE OBLIGATION IS ABOUT LINE ENDINGS, AND A QUOTED RETURN IS NOT ONE
    (review item P3-V3-F5's second witness, re-derived). This was
    `\\r in the bytes`, and the method writes a carriage return inside a
    quoted field whenever a published name or label holds one -- so the
    twin the shipped renderer writes for such a description was reported
    as carrying carriage returns, which is a conforming file told it
    broke a rule it kept. What is checked is what V6.2 names: that the
    file's RECORDS are ended by line feeds.

    The walk is the CSV quoting rule and nothing more: a field is quoted
    when it opens with a quote character, a doubled quote inside one is
    a quote and not the end of the field, and everything outside a
    quoted field is the file's own punctuation. A carriage return found
    there ends a line.
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a file's text was not text")
    # A file with no carriage return in it at all has none ending a
    # line, and that is nearly every file: the walk below is a character
    # at a time and this settles the ordinary case in one pass at the
    # language's own speed.
    if text.find(_CARRIAGE_RETURN) < 0:
        return False
    inside = False
    opening = True
    skip = False
    for index in range(len(text)):
        if skip:
            skip = False
            continue
        character = text[index]
        if inside:
            if character != _QUOTE:
                continue
            if text[index + 1 : index + 2] == _QUOTE:
                skip = True
                continue
            inside = False
            opening = False
            continue
        if character == _QUOTE and opening:
            inside = True
            opening = False
            continue
        if character == _CARRIAGE_RETURN:
            return True
        if character == _COMMA or character == _LINE_FEED:
            opening = True
            continue
        opening = False
    return False


# WHAT USED TO STAND HERE, and why it does not (review item P3-V3-F5).
# `_first_line` returned the text up to the first line feed, and it was
# the whole of the zero-row byte check: one physical line, ending in a
# feed. A record is not a line -- a published name holding a line feed
# is written as one record over two of them -- so nothing in this module
# settles a question about the file's shape on a physical line any more,
# and the function is gone rather than left for the next caller to
# reach for. `_header_names` went with it: it read one line's names with
# the CSV rules, which is `_first_record`'s job over the whole record.


def _without_a_mark(line: str) -> str:
    """One line with a byte-order mark in FRONT of it taken off.

    A mark at the start of the file is a byte rule of its own
    (`bytes.byte-order-mark`), and letting it decide the header question
    as well would accuse a file twice for one fault -- and would say the
    wrong thing, because such a file does carry its header line. A
    published name that genuinely BEGINS with U+FEFF is written QUOTED,
    so that line opens with the quotation mark and nothing is taken off
    here; that is the exception V6.2 names.
    """
    if line[:1] == _BYTE_ORDER_MARK:
        return line[1:]
    return line


def _split_lines(text: str) -> "list[str]":
    """The file's lines, split where the READER's own reader splits them.

    The reader opens the file in text mode with ``newline=""``, so all
    three of `\\r\\n`, `\\r` and `\\n` end a line and none of them is
    translated: the terminator stays on the line it ends, and a
    carriage return inside a quoted value stays the character it was.
    This walks the same three, so a record here is a record there.

    Guarantees:

    - Inputs: the file's characters, in the encoding the reader settled
      on.
    - Determinism: a fixed function of that text.
    - Errors raised: none.
    """
    # The offline audit's own type gate (plan D6.2): a method call on a
    # value it cannot trace is refused, and this is the exact shape it
    # accepts as proof that the value is a string.
    if not isinstance(text, str):
        raise TypeError("internal check: a file's text was not text")
    # Cut on the line feeds first, then on the carriage returns inside
    # each piece -- two passes with a literal each, which is what the
    # audit accepts and what keeps this linear in the file's size. A
    # carriage return at the very END of a piece is the first half of
    # the `\r\n` that piece was cut at, and is not a line of its own.
    lines: list[str] = []
    pieces = text.split("\n")
    for index in range(len(pieces)):
        lines += _cut_at_returns(pieces[index], index < len(pieces) - 1)
    return lines


def _cut_at_returns(piece: str, cut_at_a_feed: bool) -> "list[str]":
    """One line-feed piece cut again at every carriage return in it.

    ``cut_at_a_feed`` says the piece was followed by a line feed, so a
    carriage return at its very END is the first half of one `\\r\\n`
    terminator and not a line of its own. Every other carriage return
    ends a line, which is what universal-newline mode does.
    """
    # The offline audit's type gate again (plan D6.2), at the top of the
    # function that calls a method on the value.
    if not isinstance(piece, str):
        raise TypeError("internal check: a file's line was not text")
    lines: list[str] = []
    parts = piece.split("\r")
    last = len(parts) - 1
    for at in range(last):
        body = parts[at] + "\r"
        if at == last - 1 and cut_at_a_feed and not parts[last]:
            body = parts[at] + "\r\n"
        lines += [body]
    tail = parts[last]
    if cut_at_a_feed and not (last > 0 and not tail):
        return lines + [tail + "\n"]
    if not cut_at_a_feed and tail:
        return lines + [tail]
    return lines


def _records_of(text: str) -> "list[list[str]]":
    """Every record the file holds, read as `reading` reads them.

    WHY THIS IS A RECORD WALK AND NOT A LINE (review items P3-V2-D-F1
    and P3-V2-E-F4). Two questions are settled before the reader is
    called -- whether the first row can name a table's columns, and
    whether the file holds any rows at all -- and both used to be
    settled on the first PHYSICAL LINE and on the text's LENGTH. The
    reader settles neither that way: it drops blank lines and it honours
    a newline inside a quoted value. Where the two disagreed the reader
    refused a file this module had already decided was reportable, and
    its refusal for a repeated name QUOTES that name -- so a leading
    blank line, or a newline inside a header name, put a string out of
    the measured file onto the screen, and a blank line after a header
    turned a full report into "validation could not run at all".

    A csv.Error is not raised on: a file the reader cannot parse is a
    catalogued refusal of its own, raised where the reader raises it and
    in the position-naming form V9 asks for, so this returns what it has
    and leaves the refusal where it belongs. `_walked` is the same walk
    with its second answer kept: whether the file was read to its end.

    Guarantees:

    - Inputs: the file's characters, in the encoding the reader settled
      on, with any byte-order mark already taken off the front.
    - Determinism: a fixed function of that text.
    - Errors raised: none.
    """
    records, _whole = _walked(text)
    return records


def _walked(text: str) -> "tuple[list[list[str]], bool]":
    """The records, and whether the walk reached the end of the file.

    THIS STANDS IN FOR THE READER, SO IT READS UNDER THE READER'S OWN
    LIMITS (review item P3-V3-F6). The module-wide field size limit is a
    setting of the `csv` module, not of one reader: `reading` raises it
    to its own published ceiling for the length of its pass and puts it
    back afterwards, and this walk used to run under whatever the
    interpreter's default happened to be -- 131,072 characters. A
    conforming twin holding eleven values one character longer than that
    therefore parsed here as a header and nothing else, was classified as
    a file holding no rows, and got a whole report of MISSED verdicts
    without the reader ever being asked. The limit here is
    `reading.FIELD_SIZE_LIMIT` itself rather than a number of this
    module's own, so the two cannot be moved apart by editing one place.

    AND THE SECOND HALF OF THE SAME DISAGREEMENT is what the flag is
    for. A field longer than even that limit stops this walk part way,
    and the truncated record list read as "this file holds no rows" --
    which is a verdict about a file nobody managed to read. A caller
    that is deciding what the file HOLDS asks for the flag and hands an
    unfinished reading on to the reader, which refuses it in the
    position-naming form V9 asks for.

    Guarantees:

    - Inputs: the file's characters, in the encoding the reader settled
      on, with any byte-order mark already taken off the front.
    - Determinism: a fixed function of that text.
    - Errors raised: none. The limit is restored on every path.
    """
    records: list[list[str]] = []
    previous_limit = csv.field_size_limit()
    try:
        csv.field_size_limit(reading.FIELD_SIZE_LIMIT)
        try:
            for row in csv.reader(_split_lines(text)):
                if not row:
                    # A blank line carries no values, exactly as
                    # `reading._read_streamed` drops it.
                    continue
                records += [[f"{cell}" for cell in row]]
        except csv.Error:
            return (records, False)
    finally:
        csv.field_size_limit(previous_limit)
    return (records, True)


def _first_record(text: str) -> "list[str]":
    """The names the file's first RECORD holds, as the READER reads it.

    It has to reach the answer `read_table` would reach, which is why
    the caller hands over the text in the encoding the reader would
    settle on rather than the UTF-8 reading alone: this is what decides,
    before the reader is called, whether the file's first row can name a
    table's columns at all, and a file that passed here and was refused
    there would be a structural mismatch turned back into a refusal
    (V9) -- with a measured name in the refusal, which is the fault
    review item P3-V2-D-F1 was found on.
    """
    records = _records_of(_without_a_mark(text))
    if not records:
        return []
    return records[0]


def _without_the_last_break(text: str) -> str:
    """``text`` with the line ending of its LAST record taken off.

    The three the reader recognises, longest first. What a record ends
    with is `bytes.line-endings`' obligation and `bytes.terminal-newline`'s
    between them, and a check that answered for it as well would accuse
    one file twice for one fault (V3.6).
    """
    for ending in _LINE_BREAKS:
        if len(text) >= len(ending) and text[len(text) - len(ending) :] == ending:
            return text[: len(text) - len(ending)]
    return text


# -- method G2's writing rule, written from the method (V1.4) ---------
#
# THE VALIDATOR MAY NOT IMPORT THE RENDERER, so the one canonical
# writing a check needs -- the header line of the degenerate zero-row
# form -- is derived here from the method's own words instead. That is
# the same arrangement V4.2 makes for the corner classifier: a shared
# mistake now needs writing twice from two texts. Where both may be
# imported, the suite compares the two writings character for character
# over every class of name the loader admits.


def _canonical_record(cells: "list[str]") -> str:
    """One record as method G2 writes it, without its line ending.

    Fields are joined by a comma; each is written by `_canonical_field`;
    and the two canonical exceptions to minimal quoting are here: the
    first cell of a header record beginning with the byte-order mark is
    quoted whatever else it holds, and the one cell of a one-cell record
    holding nothing is written as two quote characters, because a line
    with nothing on it is not a record any reader agrees about.
    """
    if len(cells) == 1 and not cells[0]:
        return _QUOTE + _QUOTE
    text = ""
    for place in range(len(cells)):
        if place:
            text = text + _COMMA
        always = place == 0 and cells[place][:1] == _BYTE_ORDER_MARK
        text = text + _canonical_field(cells[place], always)
    return text


def _canonical_field(cell: str, always: bool) -> str:
    """One cell as method G2 writes it.

    Quoted when and only when it holds a comma, a quote character, a
    carriage return or a line feed -- or when ``always`` says it is the
    byte-order-mark exception -- and a quote character inside a quoted
    field is written twice. There is no escape character.
    """
    special = False
    quoted = False
    for character in cell:
        if character == _QUOTE:
            quoted = True
            special = True
        elif character in _MUST_BE_QUOTED:
            special = True
    if not special and not always:
        return cell
    if not quoted:
        return _QUOTE + cell + _QUOTE
    body = ""
    for character in cell:
        body = body + character
        if character == _QUOTE:
            body = body + _QUOTE
    return _QUOTE + body + _QUOTE


# WHAT USED TO STAND HERE, and why nothing does (review item P3-V4-F3).
# `_unusable_header` said why a file's first row cannot name columns,
# and `_holds_no_data` said whether a file the description expects rows
# from holds none. Both were this module's own reading of the file, made
# BEFORE the reader was called, and the branch `measure` took was taken
# on them. The reader answers both questions itself, in its own order,
# with a NUL check and a ragged check standing between them -- so the
# two readings had a precedence to agree about as well as a pair of
# answers, and they did not. `measure` now calls the reader and reports
# from the refusal it raises, so neither predicate has a second writing
# to drift from. What remains of the walk is `_records_of` and its
# callers on the degenerate zero-row path, where there is no reader
# reading to take an answer from: the producer refuses every file that
# path is reached with, and plan amendment A-P3-7 clause 3 rules that
# gate open and states what it leaves open.


# -- three lookups, written once ---------------------------------------
#
# Each of these is one `key in mapping` question with a stated answer
# when the key is absent. They are functions rather than expressions at
# every call site because a default written out fourteen times is a
# default fourteen readers have to check is the same one.


def _counted(mapping: "dict[str, int]", key: str) -> int:
    """How many ``mapping`` holds under ``key``; none is none."""
    if key in mapping:
        return mapping[key]
    return 0


def _corner_names(
    corners: "dict[str, tuple[str, ...]]", name: str
) -> "tuple[str, ...]":
    """The corners one column is in, or none at all."""
    if name in corners:
        return corners[name]
    return ()


def _window_named(
    windows: "dict[str, tuple[float, float]]", field: str
) -> "tuple[float, float] | None":
    """The window computed for one field, where one was computed."""
    if field in windows:
        return windows[field]
    return None


# -- the ladder, read as a function of a share ------------------------


def _ladder_points(
    rungs: "tuple[float | None, ...]",
) -> "list[tuple[float, float]]":
    """The published ladder as (share, value) points, nulls dropped.

    A null rung is a rung the format cannot hold, carrying no
    obligation (contract rule L3), so it is not a point the window can
    be drawn through.
    """
    points: list[tuple[float, float]] = []
    for index, value in enumerate(rungs):
        if value is not None:
            points = points + [(_LADDER_SHARES[index], float(value))]
    return points


def _ladder_at(points: "list[tuple[float, float]]", share: float) -> float:
    """The ladder's value at ``share``, read piecewise-linearly.

    The convex form of method G5.3: between two published rungs the
    ladder is a straight line, and outside the published ends it is
    flat, because no rung beyond them says otherwise.
    """
    if share <= points[0][0]:
        return points[0][1]
    last = len(points) - 1
    if share >= points[last][0]:
        return points[last][1]
    index = 0
    while index < last:
        low_share, low_value = points[index]
        high_share, high_value = points[index + 1]
        if share <= high_share:
            width = high_share - low_share
            if width <= 0.0:
                return high_value
            return low_value + (high_value - low_value) * (
                (share - low_share) / width
            )
        index = index + 1
    return points[last][1]


def _rounded_up(number: int, divisor: int) -> int:
    """``number`` divided by ``divisor``, rounded up, in whole numbers."""
    if divisor <= 0:
        return 0
    return -((-number) // divisor)


def _numeric_cells(facts: contract.NumericFacts) -> int:
    """How many cells of this column read as a number the format holds."""
    return max(
        1, facts.n_used_in_statistics + facts.n_left_out_of_statistics
    )


def _largest_stratum(
    facts: contract.NumericFacts, present: int, distinct_folded: int
) -> int:
    """How many cells the largest of method G5.2's strata can hold.

    The strata are what the rung window's displacement is made of: a
    cell landing at a recomputed rank comes from the stratum covering
    that rank, so the widest stratum is the widest displacement the
    construction can produce. Every term here is read off the
    description -- the sign counts, the numeric count, and how many
    different folded spellings the numbers may use -- and never off the
    generator, which this module may not import.

    THE BUDGET IS TAKEN AT ITS SMALLEST DEFENSIBLE READING, and the
    direction is the point. Cells of every other class are allowed a
    folded spelling each before the numbers get one, so a column whose
    cells are not all numbers is credited with fewer different values,
    larger strata, and a WIDER window. Wide is the safe direction: a
    window too wide can fail to catch a twin that missed, while a window
    too narrow would accuse a conforming one, and this module may never
    do the second.
    """
    numbers = _numeric_cells(facts)
    zeros = min(facts.n_zero, numbers)
    negatives = min(facts.n_negative, numbers)
    positives = max(0, numbers - zeros - negatives)
    # Every cell of another class may need a folded spelling of its own
    # before the numbers may spend one (method G6.5).
    spent = max(0, present - numbers)
    budget = max(1, distinct_folded - spent)
    values = min(numbers, budget)
    zero_values = 1 if zeros > 0 else 0
    rest = min(values - zero_values, negatives + positives)
    if negatives > 0 and positives > 0:
        # The sign facts win where fewer values are permitted than they
        # require: both bands keep a value (method G5.2, rule 4).
        rest = max(rest, 2)
    elif negatives + positives > 0:
        rest = max(rest, 1)
    else:
        rest = 0
    if rest <= 0:
        return max(1, zeros)
    if negatives > 0 and positives > 0:
        total = negatives + positives
        share = (2 * rest * negatives + total) // (2 * total)
        negative_values = min(max(share, 1), rest - 1)
    elif negatives > 0:
        negative_values = rest
    else:
        negative_values = 0
    positive_values = rest - negative_values
    widest = zeros
    if negative_values > 0:
        widest = max(widest, _rounded_up(negatives, negative_values))
    if positive_values > 0:
        widest = max(widest, _rounded_up(positives, positive_values))
    return max(1, widest)


def _half_unit(facts: contract.NumericFacts) -> float:
    """The half unit method G12.2 lets exactly two rules spend.

    A column publishing whole numbers rounds each value once, and a
    column whose own style map holds a point-free form may take a
    stratum to the nearest whole number so that form can be written at
    all. Either way the widening is one half unit and nothing more, and
    a column whose map holds none of the three keeps the tighter window.
    """
    if facts.integer_valued:
        return 0.5
    for style in (
        parsing.STYLE_PLAIN,
        parsing.STYLE_LEADING_ZERO,
        parsing.STYLE_LEADING_PLUS,
    ):
        if style in facts.numeric_styles:
            return 0.5
    return 0.0


# -- reading the re-description ---------------------------------------


def _column_at(
    document: "dict[str, object]", position: int
) -> "dict[str, object] | None":
    """The re-description's block for one position, or None."""
    blocks = document["columns"]
    if not isinstance(blocks, list):
        return None
    if position < 1 or position > len(blocks):
        return None
    block = blocks[position - 1]
    if not isinstance(block, dict):
        return None
    return block


def _count_at(block: "dict[str, object]", key: str) -> "int | None":
    """One whole number of a re-described block, or None if it is not there."""
    if key not in block:
        return None
    value = block[key]
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def _truth_at(block: "dict[str, object]", key: str) -> "bool | None":
    """One truth value of a re-described block, or None."""
    if key not in block:
        return None
    value = block[key]
    if isinstance(value, bool):
        return value
    return None


def _number_at(block: "dict[str, object]", key: str) -> "float | None":
    """One number of a re-described block, or None."""
    if key not in block:
        return None
    value = block[key]
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return float(value)
    if isinstance(value, float):
        return value
    return None


def _text_at(block: "dict[str, object]", key: str) -> "str | None":
    """One string of a re-described block, or None."""
    if key not in block:
        return None
    value = block[key]
    if isinstance(value, str):
        return value
    return None


def _map_at(block: "dict[str, object]", key: str) -> "dict[str, int] | None":
    """One count map of a re-described block, or None."""
    if key not in block:
        return None
    value = block[key]
    if not isinstance(value, dict):
        return None
    found: dict[str, int] = {}
    for name in value:
        counted = value[name]
        if isinstance(counted, bool):
            continue
        if isinstance(counted, int) and isinstance(name, str):
            found[name] = counted
    return found


def _inner_at(
    block: "dict[str, object]", key: str
) -> "dict[str, object] | None":
    """One nested block of a re-described block, or None."""
    if key not in block:
        return None
    value = block[key]
    if not isinstance(value, dict):
        return None
    found: dict[str, object] = {}
    for name in value:
        if isinstance(name, str):
            found[name] = value[name]
    return found


def _levels_at(
    block: "dict[str, object]",
) -> "dict[str, dict[str, object]] | None":
    """The re-described levels, keyed by their folded label, or None."""
    if "levels" not in block:
        return None
    value = block["levels"]
    if not isinstance(value, list):
        return None
    found: dict[str, dict[str, object]] = {}
    for entry in value:
        if not isinstance(entry, dict):
            continue
        label = _text_at(entry, "label")
        if label is not None:
            found[parsing.folded(parsing.trimmed(label))] = entry
    return found


# -- writing a measurement out for a person ---------------------------


def _shown_count(value: int) -> str:
    """A whole number, written out."""
    return f"{value}"


def _below_the_floor(floor: int) -> str:
    """What a count under the publication floor prints as.

    The exact number never appears beside a name. What omission from
    the file's own description already publishes is one thing only --
    that the identity covers fewer rows than the floor in this file,
    and possibly none -- so that is what this says, and no more.
    """
    return f"fewer than {floor}"


def _shown_number(value: "float | None") -> str:
    """A number, written out, or "" where the description holds none."""
    if value is None:
        return ""
    return f"{value}"


def _shown_truth(value: bool) -> str:
    """A published yes-or-no fact, in words."""
    return "yes" if value else "no"


def _shown_window(low: float, high: float) -> str:
    """The two ends of an envelope, written out."""
    return f"between {low} and {high}"


# -- building one check at a time -------------------------------------


def _exact(
    column: str,
    fact: str,
    subcheck: str,
    published: str,
    measured: "str | None",
) -> Check:
    """One exact obligation: HELD, MISSED, or WITHHELD by the gate."""
    if measured is None:
        return Check(column, fact, subcheck, WITHHELD, published, "", _GATE_CLOSED)
    if measured == published:
        return Check(column, fact, subcheck, HELD, published, measured)
    return Check(column, fact, subcheck, MISSED, published, measured)


def _silent(
    column: str,
    fact: str,
    subcheck: str,
    published: str,
    held: "bool | None",
    kept_back: "tuple[str, ...]",
    why: str = _GATE_CLOSED,
) -> Check:
    """One exact obligation whose measured value may not be shown.

    Used where the achieved value is a STRING taken from the measured
    file, or a count this obligation is never reported with. The
    comparison is made in full and the verdict is reported; the value
    itself never leaves this module.

    ``held`` is three-valued and the third value is the point: None is
    "the file's own description does not settle this", and ``why`` says
    which of the two ways the gate closed -- the kind of measurement is
    not one that description carries (`_GATE_CLOSED`), or the count it
    compares is one that description pools (`_GATE_POOLED`).

    ``kept_back`` IS WHY THE MEASURED SIDE IS NOT PRINTED, and it has
    no default because only the caller knows which of the two rules
    keeps it (review item P3-V12-F2; amendment A-P3-45). It is printed
    under MISSED, where a person is told their file failed and would
    otherwise be told nothing else at all. It is NOT printed under
    HELD: nothing failed there, so nobody is owed an account of a value
    they were not going to be shown either way.
    """
    if held is None:
        return Check(column, fact, subcheck, WITHHELD, published, "", why)
    if held:
        return Check(column, fact, subcheck, HELD, published)
    return Check(column, fact, subcheck, MISSED, published, "", "", kept_back)


def _within(
    column: str,
    fact: str,
    subcheck: str,
    published: str,
    measured: "float | None",
    window: "tuple[float, float] | None",
    citation: str,
    value: "float | None" = None,
) -> Check:
    """One approximated obligation, against both ends of its envelope.

    ``value`` is the published number the window is printed beside, and
    it is here so the line can say when the window does not reach it
    (review of the shipped reports, 2026-08-15). None of these windows
    is a margin around the published value -- each is worked out from
    the description and the size of the column -- so a window can lie
    wholly to one side of it, and on a column of dates the cardinality
    envelope G12.5 draws ordinarily does: "asks for 84 (between 106.0
    and 240.0): WITHIN-BOUND" is three true statements a reader can
    only read as a page contradicting itself. Where ``value`` is not
    given the line says nothing extra, which is right for a window
    whose published number is not one of these numbers at all.

    AND THE FILE HOLDING THAT VALUE EXACTLY IS HELD, WHATEVER THE WINDOW
    SAYS (review item P3-V10-F5; plan amendment A-P3-40, validation
    method clause V6.1-A1). A window here is not a margin around the
    published value and can lie wholly to one side of it, so a file
    holding the description's own number can fall outside it -- and the
    verdict was read off the window alone, so the page said "the
    description asks for 84 ... the file was found to hold 84: MISSED".
    That is not a strict reading of an approximated fact; it is a line
    that contradicts itself, and no reader can act on it. V6.1's two
    definitions overlap here rather than conflict -- HELD is "the exact
    obligation was met" and it WAS met -- so the exact one is taken and
    the window is left to explain itself in the note.
    """
    if measured is None or window is None:
        return Check(column, fact, subcheck, WITHHELD, published, "", _GATE_CLOSED)
    low, high = window
    reaches = value is None or low <= value <= high
    if value is not None and measured == value:
        return Check(
            column,
            fact,
            subcheck,
            HELD,
            published,
            _shown_number(measured),
            "",
            () if reaches else _MET_OUTSIDE_ITS_WINDOW,
        )
    verdict = WITHIN_BOUND if low <= measured <= high else MISSED
    note: tuple[str, ...] = ()
    if not reaches:
        note = (
            (
                "      this window does NOT reach the description's own "
                "value. It is"
            ),
            "      what the method allows the file here, worked out from",
            "      the description and the size of this column; it is not",
            "      a margin around that value.",
        )
    return Check(
        column,
        fact,
        subcheck,
        verdict,
        f"{published} ({_shown_window(low, high)})",
        _shown_number(measured),
        citation,
        note,
    )


def _deviation(
    column: str, fact: str, subcheck: str, published: str, corner: str
) -> Check:
    """One lesser outcome the ratified plan names for this profile."""
    return Check(
        column,
        fact,
        subcheck,
        AUTHORIZED_DEVIATION,
        published,
        "",
        CORNER_CITATIONS[corner],
    )


def _withheld(column: str, fact: str, subcheck: str, why: str) -> Check:
    """One subcheck the disclosure gate closed over."""
    return Check(column, fact, subcheck, WITHHELD, "", "", why)


# -- the measurement --------------------------------------------------


def measure(description: contract.Profile, path: str) -> Outcome:
    """Measure one CSV against one description; return every verdict.

    Guarantees:

    - Inputs: a description already through the strict loader
      (`contract.load_profile`, no second loader and no relaxed mode),
      and the path of the file to measure. The generation report is
      never read: every corner is recomputed from the description
      alone, so no prose is an input to a verdict. The measured file
      may be ANYTHING -- a twin, a real table, or the wrong real table
      -- and every rule here holds whichever it turns out to be.
    - Determinism: the outcome is a fixed function of the description
      and the file's bytes. No clock, no environment, and NO RANDOM
      SOURCE is constructed or consumed anywhere on this path.
    - Errors raised: `errors.ProfileError` with a plain-language
      message when validation cannot run at all -- the file missing,
      unreadable, a folder, or not readable as CSV; the description
      meeting one of the generation refusals, where no conforming twin
      exists for it; and running out of memory. Every one of them names
      positions and never values, because on this path the file may not
      be the person's own table and a refusal travels as freely as a
      report does -- which is why the reader is asked for its
      position-naming forms (`reading.REFUSALS_NAME_POSITIONS`) rather
      than the ones it gives the profiler.
      `PathValidationError` when the path is not a plain local one. A
      structural mismatch is NOT a refusal: a wrong column count, a
      wrong name or a wrong row count is a MISSED verdict with a plain
      explanation, because the report is the product even when the news
      is bad -- and that holds for the three the reader itself refuses,
      a file with no rows to describe and a first row leaving a name
      blank or using one twice, which are caught FROM the reader's own
      refusal and reported on rather than passed along (review item
      P3-V4-F3). Every other refusal of the reader's is passed along
      unchanged, so no report is ever built on a file no reading of it
      finished.
    - Boundary: this reads two files and writes none. It never writes,
      moves, truncates or re-encodes the measured file or the
      description. It does not import the generation module, and no
      string read from the measured file appears in any field of the
      result. `measured_name` is the one field holding a string that
      came from outside the description, and it came from the COMMAND
      LINE, not from the file: it is the last component of the path as
      the person wrote it, so that the report can say which file it is
      about (V7.1). No folder above it is kept, so the same check on the
      same bytes writes the same report wherever the file sits (V10).
    - Cost, stated because it is deliberate: the measured file is
      DESCRIBED TWICE by the producer -- once as the file's own
      description, which governs the disclosure gate, and once over the
      blank/non-blank split, which governs every measurement whose input
      is the set of present cells (V2.4). Both are built on every run,
      whatever the file turns out to hold, because nothing about a
      measured file may decide which of its own checks run.
    - And a column whose reading rule the description cannot rebuild
      (`unrebuildable_columns`) carries ONE check -- `position.at`,
      measured from the file's names -- with every other obligation of
      that column in the not-checkable census, saying what the
      description does not record (V2.4-A5; plan amendment A-P3-26).
      That split is a function of the description, so the twin of such
      a description carries it too.
    """
    named = refusal_of(description)
    validated = validate_local_path(path, purpose="input")
    place = pathlib.Path(validated)
    shown = f"{place}"
    # WHICH FILE THIS OUTCOME IS ABOUT (V7.1, review item P3-V2-G). The
    # name is taken from the path AS THE PERSON WROTE IT, not from the
    # resolved one: somebody who typed a link's name goes looking for
    # that name afterwards, and printing the name the link resolves to
    # would put a word in the report they never wrote. Only the last
    # component is kept -- the folders above it are where the file sits,
    # which is not what the report is about and would make the same
    # check write different bytes in different folders (V10).
    measured_name = pathlib.Path(path).name
    if named:
        raise errors.ProfileError(
            errors.no_twin_of_this_description_exists(named, shown)
        )
    if not place.exists():
        raise errors.ProfileError(errors.file_missing(shown))
    if place.is_dir():
        raise errors.ProfileError(errors.path_is_a_folder(shown))
    try:
        data = _read_bytes(place)
        text = _read_utf8(place)
        # The reader falls back to Latin-1 where the bytes are not
        # UTF-8, so the header question below is settled on the same
        # text the reader would settle it on. Every other check reads
        # `text`, because whether the file IS UTF-8 is a byte rule of
        # its own.
        as_read = text if text is not None else _read_fallback(place)
    except MemoryError as error:
        raise errors.ProfileError(errors.out_of_memory(shown, 0)) from error
    except PermissionError as error:
        raise errors.ProfileError(
            errors.file_unreadable(shown, f"{error}")
        ) from error
    except OSError as error:
        raise errors.ProfileError(
            errors.file_unreadable(shown, f"{error}")
        ) from error

    headed = description.source.header_source == reading.HEADER_FROM_FILE
    # THE REPORT IS CHOSEN BY THE REFUSAL THE READER ACTUALLY RAISED, ON
    # EVERY PATH THERE IS (review item P3-V4-F3; plan amendment A-P3-10
    # clause 2 and amendment A-P3-20). V9 makes a structural mismatch a
    # MISSED verdict with a plain explanation, so two of the reader's own
    # refusals are REPORTED on rather than passed along; which of them a
    # file gets is the reader's question and the reader answers it.
    #
    # WHAT USED TO STAND HERE, and why nothing does. Two predicates of
    # this module's own -- does this file hold any rows, and can its
    # first row name a table's columns -- were answered by walking the
    # file BEFORE the reader was called, and the branch was taken on
    # them. That is the same rule written twice, and V4.2's own account
    # of what a second writing costs applies to it: the two drifted, and
    # every place they drifted was a place two files the producer
    # refuses identically got different reports. Four were found in one
    # round -- a NUL in a header stopped being a refusal when a row was
    # taken away, a ragged file changed refusal class when a name was
    # repeated in it, and the walk's own precedence between the two
    # predicates was not the reader's -- and the class is not four
    # things but one: a precedence kept in step by hand.
    #
    # AND A FIFTH PREDICATE OF THIS MODULE'S OWN OUTLIVED THAT REPAIR,
    # ON THE ONE BRANCH IT NEVER REACHED (review round 7). "Is this a
    # zero-row description?" is not about the file and is sound; what
    # was unsound is that answering it RETURNED, so a zero-row
    # description never called the reader at all and its whole report
    # was built on this module's own record walk. The same class came
    # back with it: `column_1` over `1,2` and `other` over `1,2` are one
    # ragged refusal to the producer and drew 8 HELD / 1 MISSED against
    # 5 HELD / 4 MISSED, and `header.names` reported HELD on a file no
    # reading of which finishes. So the reader is called FIRST here too,
    # and the degenerate report is reached only through the reader's own
    # no-data refusal or through a reading that finished.
    first_row = reading.FIRST_ROW_NAMES if headed else reading.FIRST_ROW_DATA
    try:
        table = reading.read_table(
            path,
            first_row=first_row,
            refusals=reading.REFUSALS_NAME_POSITIONS,
        )
    except errors.ShapeRefusal as refusal:
        # THE ONE PREDICATE THE DISCLOSURE GATE DOES NOT CLOSE ON A FILE
        # THE PRODUCER REFUSES (review item P3-V3-F3; V5.1 against V3.4).
        # A zero-row description's own conforming twin IS a file the
        # producer refuses for holding no rows -- the header line and
        # nothing more, or no bytes at all (V1.5) -- so withholding here
        # would silence the whole obligation on the only file the
        # description says is right, and owner decision 7's byte form
        # could never HOLD on any file at all. That is the vacuity
        # V3.4-A1 names, and it takes review item P3-V3-F5's repair with
        # it. What escapes is written out in plan amendment A-P3-7
        # clause 3 rather than left to be found. It is reached by the
        # reader's OWN no-data word and by no other, so a file refused
        # for any other reason -- a header that cannot name columns, and
        # every refusal that stands before the reader's two questions --
        # gets the report that refusal chooses, exactly as it does
        # against a description that publishes rows.
        if description.n_rows == 0 and (
            refusal.kind == errors.NO_DATA_TO_DESCRIBE
        ):
            return _degenerate_report(
                description, data, text, headed, as_read, measured_name
            )
        return _report_on_a_refused_file(
            description, refusal, data, text, headed, as_read, measured_name
        )
    except MemoryError as error:
        raise errors.ProfileError(
            errors.out_of_memory_while_describing(shown)
        ) from error
    if description.n_rows == 0:
        # A READING THAT FINISHED, against a description asking for the
        # degenerate form. The file holds rows and the description says
        # it should hold none, so the byte form MISSES -- and it misses
        # having been measured against a file the producer describes,
        # rather than against a walk nobody read back.
        return _degenerate_report(
            description, data, text, headed, as_read, measured_name
        )
    try:
        declared = _declared_here(description, table)
        declared_codes = _declared_codes_here(description, table)
        declared_measured = _declared_measured_here(description, table)
        # TWO DESCRIPTIONS, ALWAYS BOTH, AND WHAT EACH ONE DECIDES
        # (V2.1 and V2.4; review item P3-V2-A1). The first is the file's
        # OWN description -- what `synthtwin profile` would write about
        # this file -- and it governs how the cells read and what the
        # disclosure gate of V5 lets a report say. The second is the
        # same producer over the same cells with absence pinned to
        # blankness, and it governs which cells every presence-dependent
        # measurement is counted over.
        #
        # BOTH ARE BUILT ON EVERY RUN, AND THAT IS THE POINT. The
        # version this replaces built one and then, where the two
        # readings of presence disagreed, WITHHELD every level,
        # distinctness, ladder and suppression obligation of the column
        # -- so one cell spelling a missing marker turned every one of
        # them from a potential MISS into a withholding, and a file that
        # carried none of its published labels passed with two hundred
        # obligations unevaluated. Nothing about the file may decide
        # which of its own checks run, so nothing about the file decides
        # which of these is built.
        redescribed = profile.build_document(
            table,
            settings_for(description),
            declared,
            declared_codes,
            declared_measured,
        )
        over_the_split = profile.build_document(
            table,
            settings_over_the_split(description),
            declared,
            declared_codes,
            declared_measured,
        )
    except MemoryError as error:
        raise errors.ProfileError(
            errors.out_of_memory_while_describing(shown)
        ) from error
    checks = _byte_checks(description, data, text, headed, as_read, False)
    checks = checks + _structure_checks(description, table, headed)
    # THE COLUMNS THIS DESCRIPTION CANNOT BE READ BACK FOR (owner ruling
    # 2026-08-16; plan amendment A-P3-26). Asked once, of the
    # description alone, and asked HERE rather than inside the column
    # walk so that the checks a column loses and the listings it gains
    # are made by one decision: an obligation that fell out of both
    # would leave the census calling itself every obligation while it
    # was not, and one that landed in both would be counted twice.
    #
    # AND ASKED ON THIS PATH ONLY, which is the whole of its scope. The
    # zero-row report already lists every per-column obligation, so
    # there is nothing there to move and asking would bind one twice.
    # The report on a file the reader refuses misses every obligation
    # for a reason that holds whatever the reading rule was -- no rows,
    # or a first row that names no columns -- so what it states is true
    # of the file without the rule being rebuilt at all.
    unrebuildable = unrebuildable_columns(description)
    listings = _listings(description, headed)
    for column in description.columns:
        # A membership test and a subscript, never `get`: the offline
        # policy accepts no method call on a value it cannot trace
        # (plan D6.2), and this mapping's values are prose.
        why = ""
        if column.name in unrebuildable:
            why = unrebuildable[column.name]
        if not why:
            checks = checks + _column_checks(
                description, column, table, redescribed, over_the_split, headed
            )
            continue
        checks = checks + _still_evidencible(column, table, headed)
        listings = listings + _unrebuildable_listings(
            description, column, headed, why
        )
    return _assembled(checks, listings, measured_name)


def _still_evidencible(
    column: contract.ColumnBlock,
    table: reading.Table,
    headed: bool,
) -> "list[Check]":
    """What a column with an unrebuildable reading rule is still asked.

    One obligation, and it is the one measured from the file's NAMES
    rather than from its cells: does a column of this number stand
    there, under this name where a header was written. Nothing about
    how a cell reads touches it, so nothing the description failed to
    record can move it, and it stays a check with a verdict.

    Everything else this column carries is counted over its cells, and
    the cells cannot be read the way the description was written. Those
    go to the not-checkable census in `_unrebuildable_listings`.
    """
    if not _position_is_evidencible(column, headed):
        return []
    return [_position_check(column, table.column_names, headed)]


def _unrebuildable_listings(
    description: contract.Profile,
    column: contract.ColumnBlock,
    headed: bool,
    why: str,
) -> "list[Listing]":
    """Every cell-counted obligation of one column, listed with the why.

    THE IDENTITIES COME FROM THE OBLIGATION WALK ITSELF, handed no cells
    and no re-description, which is the same construction
    `_zero_row_listings` uses and for the same reason: an obligation
    named here by hand would drift from the obligation the ordinary run
    checks, and a reader comparing the two censuses would be unable to
    see they are the same one. `position.at` is dropped because
    `_still_evidencible` keeps it as a check, and V3.3 forbids one
    obligation being bound twice as firmly as it forbids one bound not
    at all.
    """
    return [
        Listing(check.column, check.fact, check.subcheck, why)
        for check in _obligations(
            description, column, [], {}, {}, None, headed
        )
        if check.subcheck != "position.at"
    ]


def _degenerate_report(
    description: contract.Profile,
    data: bytes,
    text: "str | None",
    headed: bool,
    as_read: str,
    measured_name: str,
) -> Outcome:
    """The report a ZERO-ROW description gives, whatever the file holds.

    Owner decision 7 makes the expected byte form the executable
    subcheck of this predicate, and V6.4 fixes the two forms: a
    description whose names were GENERATED asks for a file of no bytes
    at all, and one whose names came from the file asks for the header
    line and nothing more.

    IT IS REACHED THROUGH THE READER AND NOT AROUND IT (review item
    P3-V4-F3, carried; plan amendment A-P3-20). Two routes reach it and
    both have had the reader speak first: the reader's own NO-DATA
    refusal, which is what the conforming file draws, and a reading that
    finished, which is a file holding rows against a description asking
    for none. A file the reader refuses for anything else -- ragged, a
    zero byte, an unusable header, a file that is not text -- reaches
    the report that refusal chooses, exactly as it does against a
    description that publishes rows. Before that, this branch returned
    ahead of the reader and the header line of an unreadable file was
    compared with the published names: two ragged files the producer
    refuses with one sentence got 8 HELD / 1 MISSED and 5 HELD / 4
    MISSED between them, and `header.names` reported HELD about a file
    no reading of which finishes.

    WHAT IS STILL READ HERE, and why it is not the walk that was
    removed. The header line is read out of the file's own characters,
    because on the no-data route the reader refuses before it hands any
    name back and there is nowhere else to get one. That reading no
    longer chooses anything: which report a file gets is settled before
    it runs. The residual it leaves -- two header-only files the
    producer refuses alike still receive different reports -- is plan
    amendment A-P3-7 clause 3's ruling, at the size stated there.

    Guarantees:

    - Inputs: the description, the measured file's bytes and characters,
      whether the names came from the file, and the text the reader
      settled on.
    - Determinism: a fixed function of those.
    - Errors raised: none.
    """
    return _assembled(
        _byte_checks(description, data, text, headed, as_read, False)
        + [_zero_row_form(description, data, text, headed)]
        + _zero_row_structure(description, text, headed),
        _zero_row_listings(description, headed),
        measured_name,
    )


def _report_on_a_refused_file(
    description: contract.Profile,
    refusal: errors.ShapeRefusal,
    data: bytes,
    text: "str | None",
    headed: bool,
    as_read: str,
    measured_name: str,
) -> Outcome:
    """The report on a file the producer refuses, chosen by the refusal.

    V9 makes a structural mismatch a MISSED verdict with a plain
    explanation rather than a refusal, and V5.1-A1 says what such a
    report may state: what that refusal states, and nothing else. Which
    of the two reports a file gets is therefore the reader's own
    question, answered by the reader, and this is the whole of the
    answering (review item P3-V4-F3).

    THAT IS THE REPAIR, AND IT IS A CONSTRUCTION RATHER THAN A RULE. The
    version this replaces asked two predicates of its own about the file
    before the reader was called; every disagreement between those
    predicates and the reader's own precedence was a pair of files the
    producer refuses identically that got different reports. Here the
    branch is the reader's shape word, so no such pair can exist: the
    files that share a word share a report.

    Guarantees:

    - Inputs: the description, the reader's own shape refusal, and the
      measured file's bytes and text for the byte rules.
    - Determinism: a fixed function of those. Nothing measured beyond
      what the byte rules and the refusal itself carry reaches the
      result.
    - Errors raised: the refusal itself, re-raised, where it names a
      header fault about a description whose names were GENERATED. The
      reader asks the header question only where they came from the
      file, so nothing reaches that; re-raising rather than assuming is
      what keeps the assumption from becoming a wrong report.
    """
    byte_rules = _byte_checks(description, data, text, headed, as_read, True)
    if refusal.kind == errors.NO_DATA_TO_DESCRIBE:
        return _assembled(
            byte_rules + _no_rows_at_all(description, headed),
            _listings(description, headed),
            measured_name,
        )
    if not headed:
        raise refusal
    why = _why_no_column_is_named(refusal)
    return _assembled(
        byte_rules
        + _unnamed_column_checks(description, why)
        + _no_column_is_named(description, why, headed),
        _listings(description, headed),
        measured_name,
    )


def _why_no_column_is_named(refusal: errors.ShapeRefusal) -> str:
    """What the reader's refusal of this first row says, and no more.

    The two are not the same size and that is the whole of this
    function (review item P3-V4-F3; plan amendment A-P3-10 clause 2).
    The profiler's own refusal for a BLANK name names the column number,
    so a report may state it. Its refusal for a REPEATED name quotes the
    name and names no position -- `dup,a,dup` and `a,dup,dup` get one
    sentence between them -- so a report that named the positions would
    state about the measured file something no run of the producer on
    that file publishes. That is true of ONE report and is why this
    function exists; the sentence that used to follow it, about a
    candidate reading the repeat's place off the report, is out of scope
    from 2026-08-14 (plan amendment A-P3-13) and nothing here rests on
    it. The fact itself is what that refusal carries, and the fact is
    what this says.
    """
    if refusal.kind == errors.HEADER_NAME_MISSING:
        return f"no name at column number {refusal.position}"
    return "one name used for two of the columns"


def _declared_here(
    description: contract.Profile, table: reading.Table
) -> "list[str]":
    """The declared identifier names the measured file actually carries.

    `forced_identifiers` is applied, so a declared identifier is
    described as one (P3-D3's settings table). A declared name the
    measured file does not carry is dropped, and the omission is not a
    softening: a column that is not there cannot be classified as
    anything, and the producer refuses a declaration naming a column of
    a table it was not given. Without the filter a file with an edited
    header would STOP the run, when the plan is explicit that a wrong
    name is a MISSED verdict with a plain explanation -- so the filter
    is what keeps a structural mismatch reportable.
    """
    return [
        name
        for name in description.settings.forced_identifiers
        if name in table.column_names
    ]


def _declared_codes_here(
    description: contract.Profile, table: reading.Table
) -> "list[str]":
    """The declared code columns the measured file actually carries.

    The same rule as `_declared_here` above, for the other declaration
    (plan P4-D19), and it is needed for the same reason. Describing the
    measured file is how its obligations are checked, and a description
    made WITHOUT the declaration reads a coding system written in
    digits as a quantity -- so every declared code column reported its
    role as MISSED against a twin that was correct in every cell. What
    is being checked is whether the file matches the description; both
    sides must therefore be described under the same declarations.

    A declared name the measured file does not carry is dropped, for
    the reason `_declared_here` gives: a column that is not there
    cannot be classified as anything, and a wrong name must stay a
    reportable MISSED verdict rather than stop the run.
    """
    return [
        name
        for name in description.settings.forced_codes
        if name in table.column_names
    ]


def _declared_measured_here(
    description: contract.Profile, table: reading.Table
) -> "list[str]":
    """The declared measurement columns the measured file carries.

    The third declaration (plan P4-D21), on the rule the two above
    carry and for the reason they carry it: describing the measured
    file is how its obligations are checked, and a description made
    WITHOUT the declaration reads `120/80` as free text -- so every
    declared column reported its role MISSED against a twin whose every
    cell was right. Both sides must be described under the same
    declarations.
    """
    return [
        name
        for name in description.settings.forced_measurements
        if name in table.column_names
    ]


def _readable(checks: "list[Check]") -> "list[Check]":
    """No MISSED verdict leaves here saying nothing about the file.

    THE FLOOR UNDER THE TWO REASONS, and it is a floor and not a third
    one (review item P3-V12-F2 clause (a); amendment A-P3-45). Every
    subcheck that ships names its own reason where it keeps the
    measured side back, and the suite asserts that on a file that
    misses each of them. This is what happens to the one somebody
    writes next year and forgets: the line says that it cannot say,
    and names itself a defect in synthtwin, which a reader can act on
    and a blank line cannot.

    HELD IS LEFT ALONE ON PURPOSE. Nothing failed there, so no reader
    is waiting to be told what their file holds; the same silence that
    is unreadable under MISSED is ordinary under HELD, and widening
    this to every verdict would put a paragraph under every line of a
    passing report.
    """
    settled: list[Check] = []
    for check in checks:
        if check.verdict != MISSED or check.achieved or check.note:
            settled = settled + [check]
            continue
        settled = settled + [
            dataclasses.replace(
                check, note=_NOT_SHOWN_AND_THIS_LINE_CANNOT_SAY_WHY
            )
        ]
    return settled


def _assembled(
    checks: "list[Check]", listings: "list[Listing]", measured_name: str
) -> Outcome:
    """One outcome, with the census counted from the verdicts alone.

    ``measured_name`` is carried through every one of the four exits
    `measure` has, which is why it is a parameter here rather than
    stamped on afterwards: an exit that forgot it would produce an
    anonymous report, and the shortest of those exits is the zero-row
    one nobody looks at twice.

    EVERY OUTCOME IS ASSEMBLED HERE, which is why the readability floor
    is applied here: the four exits are four places to forget it.
    """
    checks = _readable(checks)
    counted = {verdict: 0 for verdict in VERDICTS}
    for check in checks:
        counted[check.verdict] = counted[check.verdict] + 1
    census = Census(
        held=counted[HELD],
        within_bound=counted[WITHIN_BOUND],
        authorized_deviation=counted[AUTHORIZED_DEVIATION],
        withheld=counted[WITHHELD],
        missed=counted[MISSED],
        not_checkable=len(listings),
    )
    return Outcome(tuple(checks), tuple(listings), census, measured_name)


# -- V6.2 and V6.4: the byte rules ------------------------------------


def _byte_checks(
    description: contract.Profile,
    data: bytes,
    text: "str | None",
    headed: bool,
    as_read: str,
    refused: bool,
) -> "list[Check]":
    """Every rule about the file's bytes, each one able to fail.

    ``as_read`` is the file in the encoding the READER settled on, and
    it is what the line-ending rule is asked about: which characters are
    line endings is a question about records, and only the text the
    reader read can answer it.

    ``refused`` says the producer would refuse this file, and exactly ONE
    of these four rules is gated on it (review item P3-V3-F3). Which
    encoding a file was read under is a fact the producer PUBLISHES --
    `source.encoding`, and `used_fallback_encoding` beside it -- so on a
    file it publishes nothing about, stating it states what describing
    that file never would (V5.1). The other three are not published about
    any file at any count, which is the test amendment A-P3-3 clause 6
    ruled them outside the envelope on and A-P3-5 clause 3 wrote down:
    no cell, no name, no count and no person is in a line ending, a
    terminal newline or a byte-order mark.
    """
    checks = [
        Check(
            "",
            "document.encoding",
            "bytes.utf8",
            WITHHELD,
            "written as UTF-8",
            "",
            _GATE_REFUSED,
        )
        if refused
        else _exact(
            "",
            "document.encoding",
            "bytes.utf8",
            "written as UTF-8",
            "written as UTF-8" if text is not None else "not UTF-8",
        ),
        _exact(
            "",
            "document.encoding",
            "bytes.byte-order-mark",
            "no byte-order mark",
            (
                "a byte-order mark"
                if _starts_with_a_mark(data)
                else "no byte-order mark"
            ),
        ),
        _exact(
            "",
            "document.line-endings",
            "bytes.line-endings",
            "line feed endings",
            (
                "carriage returns"
                if _a_return_ends_a_line(as_read)
                else "line feed endings"
            ),
        ),
        _exact(
            "",
            "document.line-endings",
            "bytes.terminal-newline",
            "a newline at the end",
            (
                "a newline at the end"
                if data[len(data) - 1 :] == b"\n"
                else "no newline at the end"
            ),
        ),
    ]
    return checks


def _zero_row_form(
    description: contract.Profile,
    data: bytes,
    text: "str | None",
    headed: bool,
) -> Check:
    """The degenerate zero-row form: the byte form IS the check.

    Owner decision 7. A zero-row description whose names were generated
    asks for exactly zero bytes -- twenty columns and one column write
    the same nothing -- and one whose names came from the file asks for
    the header line and its terminal newline and nothing more. A
    nonempty or wrong-byte file MISSES.

    AND THE HEADED FORM NO LONGER ANSWERS FOR THE NAMES (V3.6; review
    item P3-V2-E-F5). This was a conjunction over three obligations --
    the names read back, the file stops there, and it ends in a newline
    -- and a subcheck whose verdict is a conjunction is only as strong
    as the conjunct an edit can pay off separately. Worse, the two it
    absorbed are two other facts' whole obligation, so `universal.name`
    and `document.columns` were bound by NOTHING on that predicate while
    a census called itself every obligation the description sets. They
    are checks of their own there now.

    WHAT IS LEFT IS THE WRITING, AND IT IS MEASURED IN RECORDS RATHER
    THAN IN PHYSICAL LINES (review item P3-V3-F5). The version this
    replaces asked for one physical line ending in a line feed, which is
    neither exact nor record-aware, and it was wrong in both directions:

    * `"reading"` quoted is not the twin's writing of the name
      `reading`, and every quoting of every name passed, because reading
      the names back is `header.names`' question and how they are
      SPELLED was nobody's;
    * a published name holding a line feed is written `"alpha\\nbeta"`,
      which is ONE record over two physical lines -- so the conforming
      file the shipped renderer writes was reported MISSED.

    So this subcheck answers for exactly what no other one does: the
    file holds ONE record, that record is written the way method G2
    fixes -- minimal quoting, a doubled quote inside a quoted field, the
    byte-order-mark exception -- and nothing follows it. Which names
    they are stays `header.names`', the count stays
    `document.n_columns`', the order stays `document.columns`', and how
    the record's own line ends stays the two byte rules', which is why
    the terminator is taken off before the comparison instead of being
    a fourth thing this one answers for.
    """
    subcheck = "bytes.zero-row-form"
    fact = "document.n_rows"
    if not headed:
        published = "a file of no bytes at all"
        measured = published if len(data) == 0 else "a file holding bytes"
        return _exact("", fact, subcheck, published, measured)
    published = "the header line as the twin writes it, and nothing more"
    if text is None:
        return Check("", fact, subcheck, MISSED, published, "not UTF-8")
    body = _without_a_mark(text)
    records = _records_of(body)
    if len(records) != 1:
        return _silent(
            "",
            fact,
            subcheck,
            published,
            False,
            _NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE,
        )
    written = _canonical_record(records[0])
    return _silent(
        "",
        fact,
        subcheck,
        published,
        _without_the_last_break(body) == written,
        _NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE,
    )


def _zero_row_structure(
    description: contract.Profile, text: "str | None", headed: bool
) -> "list[Check]":
    """What a zero-row file still evidences about its own shape.

    REVIEW ITEM P3-V2-E-F5. V6.4 makes the expected byte form the
    executable subcheck and the structural facts ZERO BYTES cannot
    evidence listing entries -- and a headed zero-row file is not zero
    bytes. It carries its header line, so how many columns the schema
    has, what they are called and what order they stand in are all
    evidenced by it, and each is its own fact with its own obligation.
    Leaving them inside the byte form's conjunction left two of them
    bound by nothing at all.

    The headerless form really is zero bytes and keeps its listings --
    with one check, because "no header line was written" is exactly what
    a file of no bytes shows, and it is the one structural fact that
    form can miss: a file carrying the published names on its first line
    is a file that wrote a header where the description says none was.

    Guarantees:

    - Inputs: the description, the file's characters (None where its
      bytes are not text), and whether the names came from the file.
    - Determinism: a fixed function of those three.
    - Errors raised: none.
    """
    names = [column.name for column in description.columns]
    found = _first_record(text) if text is not None else []
    if not headed:
        return [
            _exact(
                "",
                "document.source.header_source",
                "header.presence",
                "no header line, the first row is a record",
                _header_presence(found, names, False),
            )
        ]
    return [
        _exact(
            "",
            "document.n_columns",
            "columns.n_columns",
            _shown_count(description.n_columns),
            _shown_count(len(found)),
        ),
        _exact(
            "",
            "document.source.header_source",
            "header.presence",
            "a header line",
            _header_presence(found, names, True),
        ),
        _silent(
            "",
            "universal.name",
            "header.names",
            "the published names, in the published order",
            found == names,
            _NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE,
        ),
        _silent(
            "",
            "document.columns",
            "columns.order",
            "the published column order",
            found == names,
            _NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE,
        ),
    ]


def _unnamed_column_checks(
    description: contract.Profile,
    why: str,
) -> "list[Check]":
    """The verdicts a file whose first row cannot name columns still gets.

    Three obligations are settled by that first row alone and all three
    are missed: the header line the description says was written is not
    one, the published names did not read back, and the published order
    is not there to read. They are the same three for every file that
    reaches here, and what makes them sayable is that they are what the
    profiler's own refusal of this file says -- at the column NUMBERS
    that refusal names, never what stood in them.

    AND THE TWO COUNTS ARE NOT (review item P3-V3-F3). They were
    measured here and shown: the header's width, and the file's record
    count counted the way the reader counts rows. `synthtwin profile`
    stops at this file's first row and publishes neither, so a report
    that shows them states about the measured file two numbers no run of
    the producer on that file would ever publish (V5.1) -- and the
    review's own witness was the row count, which moved with the file
    while the refusal class did not. Both are WITHHELD, and nothing is
    lost by it: the three obligations above miss on every file that
    reaches here, and so does every obligation of every column, so this
    report is an exit-3 report whatever the file holds.
    """
    return [
        Check(
            "",
            "document.n_rows",
            "rows.n_rows",
            WITHHELD,
            _shown_count(description.n_rows),
            "",
            _GATE_REFUSED,
        ),
        Check(
            "",
            "document.n_columns",
            "columns.n_columns",
            WITHHELD,
            _shown_count(description.n_columns),
            "",
            _GATE_REFUSED,
        ),
        Check(
            "",
            "document.source.header_source",
            "header.presence",
            MISSED,
            "a header line",
            "no header line",
        ),
        Check(
            "",
            "universal.name",
            "header.names",
            MISSED,
            "the published names, in the published order",
            why,
        ),
        Check(
            "",
            "document.columns",
            "columns.order",
            MISSED,
            "the published column order",
            why,
        ),
    ]


def _no_column_is_named(
    description: contract.Profile, why: str, headed: bool
) -> "list[Check]":
    """Every per-column obligation of a file whose first row names none.

    THEY MISS; THEY ARE NOT NOT-CHECKABLE (review item P3-V2-E-F2, and
    disclosure F4). The version this replaces filed them as LISTINGS,
    and a listing says something specific and false: that no written CSV
    can evidence this obligation either way. The twin of the same
    description evidences every one of them, three commands earlier --
    so the same description told one reader it set three hundred and
    fifteen checkable obligations and another that it set eight, and
    told the second that three hundred and seventy-two of its
    obligations were beyond any CSV. V7.2 fixes that the census names
    the obligations the DESCRIPTION sets, not a number the file chose,
    and V3.3 fixes what a listing means; both were broken by the same
    line.

    What is true of this file is that its first row does not name a
    table's columns, so nothing in it stands for the column the
    description is talking about, and the obligation is not met. That is
    a MISS, with the reason on the line -- the same shape a file that
    stops before a column gets, for the same reason.

    ``why`` names the column NUMBERS at fault, never what stood in them.
    """
    missed: list[Check] = []
    for column in description.columns:
        for check in _obligations(
            description, column, [], {}, {}, None, headed
        ):
            missed = missed + [
                Check(
                    check.column,
                    check.fact,
                    check.subcheck,
                    MISSED,
                    check.published,
                    _NO_NAMES_HERE,
                )
            ]
    return missed


def _no_rows_at_all(
    description: contract.Profile, headed: bool
) -> "list[Check]":
    """Every verdict a file the description expects rows from still gets.

    A file holding no records where the description publishes some is
    not a file with fewer obligations (review item P3-V1-F11): the row
    count misses, and every per-column obligation is missed, because a
    column with no cells carries none of them. The version this replaces
    returned the row count alone and a listing per column, so a report
    on a header-only file said five obligations were every measurable
    one.

    AND NOTHING IS SAID ABOUT THE HEADER LINE (review item P3-V3-F3).
    The version this replaces read the file's first record and settled
    the width, the names, the order and each column's position against
    it. `synthtwin profile` REFUSES a file with no rows to describe: it
    publishes none of those, about this file or any other file with no
    rows, so a report stating them states what describing the file never
    would (V5.1). Two header-only files named alike -- one carrying the
    published names, one carrying two other words -- got four different
    verdicts and a different census, so one report told its reader what
    the checked file's header line spells -- about a file `synthtwin
    profile` will not say a word about. All four are WITHHELD now, and
    the file is told what the profiler's own refusal of it tells: it
    holds no rows, so it holds nothing for any obligation of any column
    to be met by.

    THE REASON IS THE ONE REPORT, not a sequence of them (plan amendment
    A-P3-13, 2026-08-14). This paragraph used to say the defect was that
    a person holding the file could read its header off one candidate
    description at a time. The owner ruled that out of scope -- such a
    person has the file open -- and the withholding stands on the other
    half, which is untouched: the report travels, and a reader of one
    report may not be told what describing the file would not publish.

    NOTHING IS LOST BY IT, and that is why it is a withholding rather
    than a conflict. This description publishes rows, so its own twin
    carries them and never reaches here: every one of these obligations
    still answers on the file the description says is right, and the
    file that reaches here misses its row count and every obligation of
    every column whatever its header says.

    The headerless form keeps its header question, because it is not
    about the file's own header at all: a description whose names were
    generated asks for no header line, a file with no records carries no
    line of any kind, and the answer is the same for every file that
    reaches here.
    """
    names = [column.name for column in description.columns]
    checks = [
        Check(
            "",
            "document.n_rows",
            "rows.n_rows",
            MISSED,
            _shown_count(description.n_rows),
            _shown_count(0),
        ),
        Check(
            "",
            "document.n_columns",
            "columns.n_columns",
            WITHHELD,
            _shown_count(description.n_columns),
            "",
            _GATE_REFUSED,
        ),
    ]
    if headed:
        checks = checks + [
            Check(
                "",
                "document.source.header_source",
                "header.presence",
                WITHHELD,
                "a header line",
                "",
                _GATE_REFUSED,
            ),
            Check(
                "",
                "universal.name",
                "header.names",
                WITHHELD,
                "the published names, in the published order",
                "",
                _GATE_REFUSED,
            ),
            Check(
                "",
                "document.columns",
                "columns.order",
                WITHHELD,
                "the published column order",
                "",
                _GATE_REFUSED,
            ),
        ]
    else:
        checks = checks + [
            _exact(
                "",
                "document.source.header_source",
                "header.presence",
                "no header line, the first row is a record",
                # ONE RULE, NOT TWO. The version this replaces wrote the
                # header question out a second time here, and the two
                # copies then had to be kept in step by hand.
                # `_header_presence` carries the rule and its reasons;
                # this path differs only in the text it is asked about,
                # which for a headerless description reaching here is a
                # file with no record in it at all.
                _header_presence([], names, False),
            )
        ]
    for column in description.columns:
        checks = checks + _nothing_left_to_measure(
            description, column, None if headed else [], headed
        )
    return checks


# -- V6.2: the structure the file must have ---------------------------


def _structure_checks(
    description: contract.Profile,
    table: reading.Table,
    headed: bool,
) -> "list[Check]":
    """Row count, column count and order, and the header read-back.

    THE FIRST RECORD IS THE READER'S OWN AND NOT A SECOND READING OF THE
    BYTES (review item P3-V4-F3). This used to hand `_header_presence`
    the file's characters and let it walk them again, which is the same
    rule written twice -- and every question about which characters the
    reader settled on, where a byte-order mark went, and which record
    came first had then to be answered the same way in two places. The
    reader has already answered all of them: where the names came from
    the file they ARE its first record, and where they were generated
    the first record is the first value of every column.
    """
    names = [column.name for column in description.columns]
    first = table.column_names if headed else _first_values(table)
    checks = [
        _exact(
            "",
            "document.n_rows",
            "rows.n_rows",
            _shown_count(description.n_rows),
            _shown_count(table.n_rows),
        ),
        _exact(
            "",
            "document.n_columns",
            "columns.n_columns",
            _shown_count(description.n_columns),
            _shown_count(len(table.column_names)),
        ),
        _exact(
            "",
            "document.source.header_source",
            "header.presence",
            (
                "a header line"
                if headed
                else "no header line, the first row is a record"
            ),
            _header_presence(first, names, headed),
        ),
    ]
    if headed:
        checks = checks + [
            _silent(
                "",
                "universal.name",
                "header.names",
                "the published names, in the published order",
                table.column_names == names,
                _NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE,
            ),
            _silent(
                "",
                "document.columns",
                "columns.order",
                "the published column order",
                table.column_names == names,
                _NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE,
            ),
        ]
    return checks


def _first_values(table: reading.Table) -> "list[str]":
    """The first record of a table the reader read as data throughout.

    The reader is asked for FIRST_ROW_DATA where the description's names
    were generated, so the file's first record is the first value of
    every column and the reader has already settled which record that
    is -- blank lines dropped, a quoted line break honoured, a
    byte-order mark taken off. A table reaching here holds at least one
    row, because a table holding none is a refusal the caller reported
    on before this.
    """
    found: list[str] = []
    for cells in table.columns:
        if not cells:
            return []
        found = found + [cells[0]]
    return found


def _header_presence(
    found: "list[str]",
    published: "list[str]",
    headed: bool,
) -> str:
    """What the file shows about whether a header line was written.

    THE COMPARISON IS AGAINST THE DESCRIPTION'S OWN NAMES, and that is
    the whole of what makes this a check (review item P3-V1-F8). The
    version this replaces compared the file's first line with
    `table.column_names` -- which the reader had just DERIVED from that
    same line under the read mode the description chose -- so the two
    agreed whatever the file held, and a headered twin with its header
    line taken away reported HELD. In the headerless mode it returned
    the expected words unconditionally. A named check that cannot fail
    is forbidden by V3.4 and by the charter, and both halves of that one
    could not.

    The question is two-sided, because the obligation is: a header line
    exactly when `source.header_source` says the names came from the
    file, and none when it says they were generated.

    * WHERE A HEADER WAS WRITTEN, the evidence is the first line reading
      back as the published names. A file whose first line is a record
      does not, and misses.
    * WHERE NONE WAS, the evidence is the same first line NOT reading
      back as the published names, and that alone (review item
      P3-V2-C-F8). The version this replaces asked for a second thing
      as well -- that the file hold more rows than the description
      publishes -- on the reasoning that a written header ALSO adds a
      line. A conjunction is only as strong as the conjunct an editor
      can pay off separately: a header line written in AND one data row
      taken out leaves the row count where it was, and this check then
      reported "no header line, the first row is a record" about a file
      whose first line was the published names. It reported the opposite
      of the truth about the bytes it governs, defeated by the exact
      perturbation class it exists for. So the row count is not a
      conjunct here; it is `rows.n_rows`, which is its own subcheck and
      misses on its own terms.

      WHAT THE ONE-SIDED RULE COSTS, stated rather than left to be
      found. A conforming twin whose FIRST RECORD spells every published
      name -- `column_1` in column one, `column_2` in column two -- is
      reported as carrying a header line it does not carry. That file is
      one no reader could tell from a headered file, which is the
      confusion `source.header_source` exists to settle, so the report
      naming it is the honest answer and not a false accusation. The
      generated names are the only names in play, because a description
      whose names came from the file is the headed branch above.

    ``found`` is the file's FIRST RECORD, and the caller takes it from
    the reading that governs: the reader's own where there is one, and
    the walk's where there is none, which is the degenerate zero-row
    path alone. Which characters that record was read from -- the UTF-8
    reading or the fallback -- is then the reader's answer and not a
    second one taken here. Whether the file IS UTF-8 is a byte rule of
    its own and is not re-asked here either.
    """
    if headed:
        if found == published:
            return "a header line"
        return "no header line"
    if found == published:
        return "a header line"
    return "no header line, the first row is a record"


# -- the per-column measurement ---------------------------------------


def _column_checks(
    description: contract.Profile,
    column: contract.ColumnBlock,
    table: reading.Table,
    redescribed: "dict[str, object]",
    over_the_split: "dict[str, object]",
    headed: bool,
) -> "list[Check]":
    """Every subcheck one published column carries, whatever the file is.

    A file with no column at this position does not owe less than one
    that has it (review item P3-V1-F11): the same obligations are built,
    by the same walk, and every one of them MISSES with the sentence
    that says why. The version this replaced returned a single invented
    `column.present` miss and dropped the rest, so a description setting
    forty obligations for a column could lose all forty by having that
    column deleted from the file.
    """
    cells = _cells_of(table, column.position)
    if cells is None:
        return _nothing_stands_here(
            description, column, table.column_names, headed
        )
    block = _column_at(redescribed, column.position)
    split = _column_at(over_the_split, column.position)
    return _obligations(
        description,
        column,
        cells,
        block if block is not None else {},
        split if split is not None else {},
        table.column_names,
        headed,
    )


def _obligations(
    description: contract.Profile,
    column: contract.ColumnBlock,
    cells: "list[str]",
    block: "dict[str, object]",
    split: "dict[str, object]",
    names: "list[str] | None",
    headed: bool,
) -> "list[Check]":
    """One column's whole obligation set, measured against what there is.

    ``block`` is this column in the file's OWN description and ``split``
    is the same column described over the blank/non-blank split (V2.4).
    The first decides what may be said; the second says it.

    THE IDENTITIES THIS PRODUCES ARE A FUNCTION OF THE DESCRIPTION
    ALONE. Which cells were read and what either re-description made of
    them decide the VERDICTS; they never decide which obligations exist.
    Handed no cells and no re-description at all this still names every
    obligation the column carries, which is what lets the degenerate
    paths above report a full census instead of a short one.
    """
    name = column.name
    floor = description.settings.small_cell_floor
    # WHICH READING OF PRESENCE MAY BE REPORTED (plan amendment A-P3-5).
    # The blank split is the measurement V2.4 asks for, and it is the one
    # taken wherever the file's own description publishes the split. Where
    # that description pools its missing sources under the publication
    # floor, the split is a fact about the file it does not publish, and
    # the two counts come off the description itself -- which says the
    # same thing about every file it describes, which is the whole of
    # V5.1.
    #
    # THE TWO COUNTS ASK THE WEAKER QUESTION, deliberately. They need
    # only how MANY holes are non-blank, which the class map publishes
    # for every role; the rest need the SPELLINGS too. Asking both the
    # same way would have thrown away the round-2 witness on every column
    # whose role publishes no spelling of its own.
    split_published = _split_is_published(block)
    if _split_size_is_published(block):
        present, missing = _presence_over_the_split(split, cells)
    else:
        present, missing = _own_presence(block, cells)
    checks: list[Check] = []
    if _position_is_evidencible(column, headed):
        checks = checks + [_position_check(column, names, headed)]
    checks = checks + [
        _exact(
            name,
            "universal.n_present",
            "presence.n_present",
            _shown_count(column.n_present),
            _shown_count(present),
        ),
        _exact(
            name,
            "universal.n_missing",
            "presence.n_missing",
            _shown_count(column.n_missing),
            _shown_count(missing),
        ),
    ]
    # THE FOUR AXES, and all four rather than one (review item
    # P3-V1-F3). The re-description publishes each of them for the file's
    # own column, so each is a read-back a file can evidence: the twin
    # re-reads as the same kind of column or it does not. The version
    # this replaces checked `statistical_type` and left `role`,
    # `quality_state` and `structural_role` in no check, no listing and
    # no input-side binding at all, while the report called its counts
    # every obligation.
    #
    # ...AND THREE OF THE FOUR, because the fourth is not a fact about
    # any file (review item P3-V2-C-F3; plan amendment A-P3-2, which
    # records the lowering in those words). `structural_role` answers
    # whether the person who owns the table declared this column with
    # `--identifier`; the taxonomy computes it from that declaration
    # alone and says in its own docstring that no value of the column is
    # consulted. The validator re-describes the measured file under the
    # description's OWN declaration list (V2.2), so both sides read the
    # same word for every column of every description that declares no
    # identifier -- the zero-code default -- and every column of every
    # ordinary report carried one HELD obligation no file could miss.
    # It is a listing entry now: the EXACT-CONTROL remainder a CSV
    # cannot evidence, which is V3.3's own words for it.
    for field, published in (
        ("role", column.role),
        ("statistical_type", column.statistical_type),
        ("quality_state", column.quality_state),
    ):
        checks = checks + [
            _exact(
                name,
                f"universal.{field}",
                f"axes.{field}",
                published,
                _text_at(block, field),
            )
        ]
    mine = _corner_names(corners_of(description), name)
    # V2.4. Every measurement whose input is the set of present cells is
    # taken over the blank/non-blank split. So the same obligations are
    # built twice over the same cells: once against the file's own
    # description, which decides only whether the gate lets this check
    # say anything at all (V5), and once against the description taken
    # over the split, which supplies the measurement. `_governed` puts
    # the two together. A re-description that never happened is a
    # different case and is not this one: it is settled by the callers
    # above, which hand both sides the same empty block.
    # AND THE CELLS THE GATED SIDE SEES ARE THE ONES THAT DESCRIPTION
    # READS (plan amendment A-P3-5). The style clauses recount the
    # WRITTEN cells rather than a re-description, and settle each recount
    # against the room the file's own description leaves -- room that
    # `_unread_cells` widens by exactly the disputed cells. So the same
    # two files leaked there too: fifty-nine numbers and one empty cell
    # beside fifty-nine numbers and one `n/a`, one description between
    # them, and SEVEN style subchecks changed verdict, nineteen misses
    # becoming seventeen misses and seven withholdings. The reviewer's
    # witness named the presence counts; repairing only those would have
    # left this half of the same class open.
    own_cells = cells
    if not split_published:
        own_cells = _cells_that_description_reads(
            block,
            cells,
            kept_spellings(description),
            declared_spellings(description),
        )
    gated = _universal_checks(column, block, mine)
    gated = gated + _role_checks(column, block, own_cells, floor, mine)
    measured = _universal_checks(column, split, mine)
    measured = measured + _role_checks(column, split, cells, floor, mine)
    return checks + _governed(gated, measured, split_published)


def _cells_that_description_reads(
    block: "dict[str, object]",
    cells: "list[str]",
    kept: "tuple[str, ...]",
    declared: "tuple[str, ...]",
) -> "list[str]":
    """The cells the file's OWN description counts as values, plus its blanks.

    WHAT THIS IS FOR (plan amendment A-P3-5 clause 2). The style clauses
    recount the written cells and settle each recount against the room
    the file's own description leaves, so the cells they recount have to
    be the cells that description counts -- otherwise two files the
    producer describes byte for byte alike are recounted differently and
    the report tells them apart, which V5.1 forbids.

    AND A CELL THAT DESCRIPTION READS AS DATA STAYS (review item
    P3-V4-F1). The version this replaces dropped every cell wearing a
    built-in missing spelling and every cell whose value is one of the
    three built-in numeric stand-ins, UNCONDITIONALLY -- and the
    producer reads neither kind as a hole where the description names it
    as data. A researcher who keeps `-999` as a real measurement has a
    description publishing that candidate `kept_by_you`; the file's own
    description then counts those cells as values, this function deleted
    them, and the twin the shipped generator wrote from that very
    description was reported MISSING style obligations -- 60 held, 15
    within, 2 MISSED and exit 3 on a conforming file. The old note
    called that "recount detail, in the safe direction". It was neither:
    a smaller recount is a smaller count against a floor the description
    publishes exactly, and `styles.at-least.plain` is a floor.

    SO A CELL IS DROPPED ONLY WHERE THAT DESCRIPTION READS IT AS A HOLE,
    and which cells those are is asked of the description, four ways:

    - the producer's own absence rules are applied in the producer's
      order -- a non-blank cell wearing one of its built-in missing
      spellings is a hole UNLESS the settings name that spelling as
      data, which `kept` carries (V2.3, the three published routes);
    - a cell wearing a spelling the person DECLARED to be "no value" is
      a hole ahead of every rule below, which `declared` carries
      (`declared_spellings`, the fourth published route). Leaving this
      out was the other half of review item P3-V4-F1: those cells stayed
      in a recount settled against a floor the description publishes
      exactly, which is the same arithmetic error as dropping a kept
      cell, in the other direction;
    - a cell whose VALUE is one of the three built-in numeric stand-ins
      is a hole only where the column's own verdict on that candidate
      says so, and the file's own description publishes that verdict per
      candidate. A candidate it publishes as kept is data, whatever the
      submitted description says about it;
    - and a candidate the file's own description publishes NO verdict
      for -- fewer than the publication floor of its cells share it, so
      naming it would publish a count the floor exists to hide -- is
      settled by the one number that description does publish: how many
      of its cells are non-blank and read as holes (`_unread_cells`).
      Where the certain holes already account for every one of them, no
      unpublished candidate is a hole and none of its cells is dropped.

    A NUMERIC STAND-IN IS MATCHED ON THE EXACT NUMBER ITS DIGITS
    DENOTE, on both sides, which is neither its text nor the binary64
    value that text rounds to (review item P3-V4-F1, and it reopened the
    class Phase 1 closed as P1-R8-F2). Not the text, because the
    producer decides a stand-in from the number: `-9999.0` and `-9999`
    are one candidate to it and would be two spellings to a text
    comparison. And not the rounded value, because two decimal spellings
    a person can tell apart round to one binary64 value: this function
    read `-999.00000000000001` as the stand-in `-999`, while the
    producer -- whose comparison Phase 1 made exact for that very reason
    -- reads it as an ordinary reading and publishes it as one. Eleven
    such cells were deleted from a recount settled against a floor that
    same description publishes exactly, and `styles.at-least.decimal`
    was reported MISSED against the file's own description. The rule
    used here is `taxonomy.exact_of_spelling`, the producer's own, by
    name; there is no second writing of it to drift.

    WHAT IS LEFT OPEN, at its exact size. Where the description does
    leave an unpublished candidate's verdict undecided -- it pools some
    missing source, holds fewer than `small_cell_floor` cells of a
    stand-in, and reads at least one OTHER non-blank cell as a hole --
    those cells are dropped. That is fewer than `small_cell_floor` cells
    per candidate, it can only happen on a column whose own
    description pools its holes, and it is exactly residual R-P2-13's
    corner, which plan amendment A-P3-5 clause 1 already records as a
    place a generated value reading back as a hole can cost a verdict. A
    twin whose absent cells are all written empty -- which is every
    conforming twin but that corner -- reaches this function with
    nothing disputed at all and loses no cell.

    THAT BOUND IS TRUE OF THE EXACT RULE AND WAS FALSE OF THE ROUNDING
    ONE, which is how the size of this residual hid the defect above. A
    candidate goes unnamed only because fewer than `small_cell_floor`
    cells hold it, so "fewer than the floor per candidate" follows from
    the identity being the producer's -- but under a rounding identity a
    cell that is NOT the candidate counted as one, and a column holding
    eleven such cells lost all eleven while the sentence above still
    said fewer than eleven. The suite asserts the bound by counting the
    cells rather than by trusting it, which is what makes the sentence
    checkable rather than merely written.

    Guarantees:

    - Inputs: one column of the file's OWN description, that column's
      written cells, and the two declaration sets the description
      publishes -- what it names as data and what it names as "no
      value". No submitted count decides which cells are read.
    - Determinism: a fixed function of those four.
    - Errors raised: none.
    """
    holes = _holes_by_the_description(block, cells, kept, declared)
    read: list[str] = []
    for index, cell in enumerate(cells):
        if not holes[index]:
            read = read + [cell]
    return read


def _holes_by_the_description(
    block: "dict[str, object]",
    cells: "list[str]",
    kept: "tuple[str, ...]",
    declared: "tuple[str, ...]",
) -> "list[bool]":
    """Which cells the file's own description reads as non-blank holes.

    The two certainties and the one budget `_cells_that_description_reads`
    describes, in that order. Split out so the rule can be read on its
    own and tested on its own.

    EVERY NUMBER HERE IS AN EXACT ONE, and the two names that make it so
    are the producer's own: `taxonomy.exact_of_spelling` for a cell or a
    declared spelling, `taxonomy.exact_of_number` for a candidate the
    producer carries as a number. Nothing in this function compares two
    numbers any other way, because a cell's identity decided in binary64
    beside a producer that decides it exactly is a cell the two sides can
    disagree about (review item P3-V4-F1).

    AND NO COMPARISON HERE RUNS ON ESCAPED TEXT (review item P3-V9-F3;
    plan amendment A-P3-33). The version this replaces put a cell
    through `parsing.visible` before folding it against a declared
    spelling, on the reasoning that the description publishes the
    spelling in its shown form. Contract version 5 withdrew that: a
    source spelling is stored character for character and escaped only
    where it is PRINTED (C5-1 to C5-4), so `declared_spellings` hands
    back the exact text and escaping the cell compared one text that had
    crossed the display boundary with one that had not. Twelve holes
    spelled `X`, U+0001, `Y` were then recognised as none of them, the
    column's cells were recounted as though the description read them
    all as values, and a file whose written numbers do not match the
    description's published styles came back with those style
    obligations WITHHELD and nothing missed.

    The boundary is for a person reading a screen. A comparison is not a
    screen, and the rule that keeps this true is asserted rather than
    remembered: `tests/test_p3v9f3_escaping_is_display_only.py` walks
    this whole module for a call to the display boundary and turns the
    suite red on one, because this module states verdicts and prints
    nothing -- `quality.py` is what puts a spelling on a screen.
    """
    kept_spellings_folded: dict[str, int] = {}
    kept_numbers: list[tuple[int, tuple[str, ...], int]] = []
    for spelling in kept:
        number = taxonomy.exact_of_spelling(spelling)
        if number is None:
            # The producer matches a declaration that names no number by
            # its folded spelling, and one that names a number by the
            # number alone (`taxonomy._split_missing`, and V2.3). Which
            # of the two a spelling is, is the reader of record's own
            # answer, asked here through the same name the producer asks
            # it through rather than through a second reading of it.
            kept_spellings_folded[parsing.folded(spelling)] = 1
        else:
            kept_numbers = kept_numbers + [number]
    declared_folded: dict[str, int] = {}
    declared_numbers: list[tuple[int, tuple[str, ...], int]] = []
    for spelling in declared:
        number = taxonomy.exact_of_spelling(spelling)
        if number is None:
            declared_folded[parsing.folded(spelling)] = 1
        else:
            declared_numbers = declared_numbers + [number]
    for candidate in _candidates_the_description_keeps(block):
        kept_numbers = kept_numbers + [candidate]
    missing_candidates = _candidates_the_description_drops(block)
    certain: list[bool] = []
    unsettled: list[bool] = []
    for cell in cells:
        body = parsing.trimmed(cell)
        is_hole = False
        undecided = False
        if body:
            exact = taxonomy.exact_of_spelling(cell)
            stand_in = _stand_in_of(exact)
            # The producer's own order: what the settings name as data
            # beats every rule below it, what they name as "no value"
            # comes next, the built-in table of missing spellings after
            # that, and a stand-in's fate is the column's own verdict on
            # that candidate (`_split_missing`,
            # `_declared_numbers_removed` and `_sentinel_verdicts`, in
            # that order).
            named_as_data = _named(kept_numbers, stand_in) or _spelled_alike(
                cell, kept_spellings_folded
            )
            named_as_a_hole = _named(
                declared_numbers, exact
            ) or _spelled_alike(cell, declared_folded)
            if named_as_data:
                is_hole = False
            elif named_as_a_hole or parsing.is_missing_text(cell):
                # Two rules of the producer's, in its order, and the
                # order survives the `or`: a declaration is asked first
                # and the built-in table second, exactly as
                # `_split_missing` asks them.
                is_hole = True
            elif stand_in is not None:
                is_hole = _named(missing_candidates, stand_in)
                undecided = not is_hole
        certain = certain + [is_hole]
        unsettled = unsettled + [undecided]
    counted = 0
    for is_hole in certain:
        if is_hole:
            counted = counted + 1
    if _unread_cells(block, cells) <= counted:
        return certain
    # The description reads more non-blank cells as holes than the
    # verdicts it publishes account for, so a candidate it does not name
    # is one of them. Which is not published, so all of them go.
    settled: list[bool] = []
    for index in range(len(cells)):
        settled = settled + [certain[index] or unsettled[index]]
    return settled


def _spelled_alike(cell: str, folded: "dict[str, int]") -> bool:
    """Whether a declaration folded into ``folded`` takes this cell.

    ONE PLACE, AND IT IS WHERE THE DISPLAY BOUNDARY IS NOT (review item
    P3-V9-F3). The producer matches a declaration that names no number
    by the trimmed, case-folded spelling and nothing else
    (`settings.declaration_matching`, whose one permitted value says
    so). Both sides of this comparison are the raw text: the keys were
    folded from spellings `declared_spellings` read out of the
    description exactly as it stores them, and the cell is folded here
    exactly as the file wrote it.

    The version this replaces put the CELL through `parsing.visible`
    first, which compared an escaped text with an unescaped one and made
    twelve holes spelled with a control character invisible to the rule.
    Named as a function of its own so that the property has somewhere to
    be replaced from, which is what lets the suite prove the assertion
    can fail.

    Guarantees: takes a cell and a mapping of folded spellings; returns
    whether one of them takes the cell. Raises nothing. No I/O, nothing
    printed, and nothing escaped.
    """
    return parsing.folded(cell) in folded


def _stand_in_of(
    number: "tuple[int, tuple[str, ...], int] | None",
) -> "tuple[int, tuple[str, ...], int] | None":
    """The built-in numeric stand-in this cell IS, or None.

    Matched on the EXACT number the cell's digits denote, which is how
    the producer decides a candidate (V2.3, and `_sentinel_verdicts`
    counts a candidate's rows that way for review item P1-R8-F2). So
    `-999`, `-999.0` and `-999.00` are one candidate here as they are
    one candidate there -- and `-999.00000000000001` is not that
    candidate on either side, though it rounds to the same binary64
    value, because it is a different number and the producer describes
    it as one (review item P3-V4-F1).
    """
    if number is None:
        return None
    for candidate in _STAND_IN_EXACTS:
        if number == candidate:
            return candidate
    return None


def _named(
    numbers: "list[tuple[int, tuple[str, ...], int]]",
    value: "tuple[int, tuple[str, ...], int] | None",
) -> bool:
    """Whether ``value`` is one of ``numbers``; False for no number.

    Both sides are canonical triples, so this is the producer's own
    `_declared_number` comparison and not a rounding of it.
    """
    if value is None:
        return False
    for number in numbers:
        if number == value:
            return True
    return False


def _candidates_the_description_keeps(
    block: "dict[str, object]",
) -> "list[tuple[int, tuple[str, ...], int]]":
    """The stand-ins the file's own description read as ordinary numbers."""
    return _candidates_with(block, taxonomy.VERDICT_KEPT)


def _candidates_the_description_drops(
    block: "dict[str, object]",
) -> "list[tuple[int, tuple[str, ...], int]]":
    """The stand-ins the file's own description read as "no value"."""
    return _candidates_with(block, taxonomy.VERDICT_MISSING)


def _candidates_with(
    block: "dict[str, object]", verdict: str
) -> "list[tuple[int, tuple[str, ...], int]]":
    """Every published sentinel candidate carrying one verdict, as numbers.

    Each one as the EXACT number its published spelling denotes, which
    is the identity the cells are compared at.

    A candidate below the publication floor is published by no entry at
    all, so it appears in neither list and the caller settles it from
    the count of holes instead.
    """
    found: list[tuple[int, tuple[str, ...], int]] = []
    if "sentinel_verdicts" not in block:
        return found
    entries = block["sentinel_verdicts"]
    if not isinstance(entries, list):
        return found
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        inner: dict[str, object] = {}
        for name in entry:
            if isinstance(name, str):
                inner[name] = entry[name]
        if _text_at(inner, "verdict") != verdict:
            continue
        candidate = _text_at(inner, "candidate")
        if candidate is None:
            continue
        number = taxonomy.exact_of_spelling(candidate)
        if number is not None:
            found = found + [number]
    return found


def _position_is_evidencible(column: contract.ColumnBlock, headed: bool) -> bool:
    """Whether a file can show this column standing anywhere but here.

    REVIEW ITEM P3-V2-C-F7, and plan amendment A-P3-2, which records the
    lowering in those words. `_position_check` below has exactly two
    failure branches, and where the names were GENERATED only one of
    them is live: the file stops before this column number. The first
    column is the one number no file that reaches a verdict can stop
    before -- a file carrying no columns at all is refused by the reader
    before any verdict exists -- so `position.at` on the first column of
    a headerless description is a check whose failure set is empty,
    which V3.4 and the charter both call a defect.

    NOTHING ELSE IS NARROWED. Where a header was written the name at
    that number is the evidence and every column carries it. Where the
    names were generated, the second and later columns are still checked
    and still miss on a file that stops short. This is the first column
    of a headerless description and nothing else, and it becomes a
    listing entry with a sentence saying what the column count already
    states.

    Guarantees:

    - Inputs: one published column and whether the names came from the
      file. No measured value is consulted, because which obligations
      exist is a function of the description alone.
    - Determinism: a fixed function of those two.
    - Errors raised: none.
    """
    return headed or column.position > 1


def _position_check(
    column: contract.ColumnBlock,
    names: "list[str] | None",
    headed: bool,
) -> Check:
    """That the file carries THIS column where the description puts it.

    `universal.position` is EXACT-CONTROL, and this is the part of it a
    written CSV can evidence: a file that stops before this column
    number does not carry the column, and where a header was written a
    file whose column of that number is named something else does not
    carry it either. Where the names were generated the file carries no
    names to compare, so the obligation is the weaker one the file can
    still answer -- that a column stands there at all.

    This is also what makes a dropped column a full census rather than
    one invented line: the obligation belongs to the description, so it
    is asked of every file.
    """
    fact = _POSITION_FACT
    subcheck = "position.at"
    published = f"column number {column.position}"
    if headed:
        published = (
            f"column number {column.position}, under this column's "
            f"published name"
        )
    if names is None:
        return Check(column.name, fact, subcheck, WITHHELD, published, "", _GATE_CLOSED)
    index = column.position - 1
    if index < 0 or index >= len(names):
        return Check(
            column.name,
            fact,
            subcheck,
            MISSED,
            published,
            "no column of that number",
        )
    if headed and names[index] != column.name:
        return Check(
            column.name,
            fact,
            subcheck,
            MISSED,
            published,
            "a column of that number, under another name",
        )
    return Check(column.name, fact, subcheck, HELD, published, published)


def _nothing_stands_here(
    description: contract.Profile,
    column: contract.ColumnBlock,
    names: "list[str] | None",
    headed: bool,
) -> "list[Check]":
    """Every obligation of a column the file does not carry, MISSED."""
    missed: list[Check] = []
    for check in _obligations(
        description, column, [], {}, {}, names, headed
    ):
        missed = missed + [
            Check(
                check.column,
                check.fact,
                check.subcheck,
                MISSED,
                check.published,
                _NO_COLUMN_HERE,
            )
        ]
    return missed


def _nothing_left_to_measure(
    description: contract.Profile,
    column: contract.ColumnBlock,
    names: "list[str] | None",
    headed: bool,
) -> "list[Check]":
    """Every obligation of a column in a file that holds no rows.

    Everything a cell would have had to carry is MISSED, because there
    are no cells. The gate's own sentence would be the wrong reason for
    those: nothing was withheld, there was nothing to describe.

    WHERE THIS COLUMN STANDS IS THE ONE QUESTION THE HEADER LINE ANSWERS,
    AND ON A FILE THE PRODUCER REFUSES IT IS NOT ANSWERED (review item
    P3-V3-F3). ``names`` is None exactly where the caller has a header
    line it may not read anything off -- a headed description against a
    file with no rows -- and there the position check is WITHHELD under
    the refusal's own sentence rather than turned into the miss the rest
    of the column takes. A headerless description hands over the empty
    record it really has, and the answer is the same for every file that
    reaches there: no column stands at any number in a file with no
    records.
    """
    filled: list[Check] = []
    for check in _obligations(
        description, column, [], {}, {}, names, headed
    ):
        if check.fact == _POSITION_FACT and names is None:
            filled = filled + [
                Check(
                    check.column,
                    check.fact,
                    check.subcheck,
                    WITHHELD,
                    check.published,
                    "",
                    _GATE_REFUSED,
                )
            ]
            continue
        if check.verdict == WITHHELD and check.citation == _GATE_CLOSED:
            filled = filled + [
                Check(
                    check.column,
                    check.fact,
                    check.subcheck,
                    MISSED,
                    check.published,
                    _NO_ROWS_HERE,
                )
            ]
            continue
        filled = filled + [check]
    return filled


def _cells_of(
    table: reading.Table, position: int
) -> "list[str] | None":
    """The measured cells at one position, or None when there are none."""
    if position < 1 or position > len(table.columns):
        return None
    return table.columns[position - 1]


def _presence_over_the_split(
    split: "dict[str, object]", cells: "list[str]"
) -> "tuple[int, int]":
    """The two presence counts, off the SPLIT description (V2.4).

    THE ONE PLACE THEY MAY COME FROM, and it was two (review item
    P3-V4-F1, plan amendment A-P3-15 clause 3). V2.4 says every
    measurement whose input is the set of present cells is read off the
    split description; every other one is, and these two were recounted
    beside it by `_presence_of`. While `declared_missing_values` was
    empty on both sides the two answers were the same number, so nothing
    showed. They are not the same number once a `--missing-value`
    declaration is recovered: the split description reads those cells as
    the holes the description publishes them as, and a raw blank count
    reads them as values. One column then reported 199 present against a
    recount of 211 while its own distinctness, ladder and moments -- all
    read off the split -- agreed with the description exactly. Two
    numbers for one question is not a measurement, and the one that
    stands is the description's, because that is the one every other
    presence-dependent obligation is settled from.

    THE DIRECTION IT MOVES, said as a cost. A non-blank cell can now be
    absent to this count, where before only an empty field could be, and
    the cells that can are exactly those wearing a spelling the
    description ITSELF publishes as the source of its holes.

    **AND ONE OF THIS PACKAGE'S OWN WORDS CAN BE IN THAT SET, from plan
    amendments A-P3-29, A-P3-35 and A-P3-39.** This paragraph used to end
    "nothing of synthtwin's own vocabulary is in that set, so residual
    R-P2-13's collision cannot reach it", and each of those three
    amendments took one route by which it can: a built-in word the
    description declares, a stand-in number a column of it settles, and
    a built-in word a column publishes as the source of its holes. The
    collision is therefore reachable and is stated at its size where
    each of them states it, in `settings_over_the_split`. What has not
    changed is that a spelling reaches this set only where the
    description's own words put it there.

    Guarantees:

    - Inputs: one column of the SPLIT description, and that column's
      written cells for the degenerate case below.
    - Determinism: a fixed function of the two.
    - Errors raised: none.
    - Boundary: where the split description carries neither count --
      the degenerate paths hand both sides the same empty block -- the
      blank split is what there is, and `_presence_of` supplies it.
    """
    present = _count_at(split, "n_present")
    missing = _count_at(split, "n_missing")
    if present is None or missing is None:
        return _presence_of(cells)
    return present, missing


def _presence_of(cells: "list[str]") -> "tuple[int, int]":
    """How many cells are present and how many absent, by BLANKNESS.

    The contract's own rule for twins: every absent cell is written as
    an empty field.

    WHETHER THIS COUNT MAY BE REPORTED is a separate question and
    `_split_is_published` below is where it is asked (plan amendment
    A-P3-5). This function says what the split holds; that one says
    whether describing the file would publish it.
    """
    present = 0
    for cell in cells:
        if parsing.trimmed(cell):
            present = present + 1
    return present, len(cells) - present


def _own_presence(
    block: "dict[str, object]", cells: "list[str]"
) -> "tuple[int, int]":
    """The two presence counts as the file's OWN description states them.

    Used where that description pools its missing sources, so that the
    blank split may not be reported (`_split_is_published`). It is the
    same file and the same cells; what differs is only which cells the
    producer's own absence rules count as holes, and those are the ones
    a description of this file publishes.

    A description that carries neither count cannot answer, and there the
    blank split is what there is -- no statement about a fact the
    description does not carry can be narrower than one it does.
    """
    present = _count_at(block, "n_present")
    missing = _count_at(block, "n_missing")
    if present is None or missing is None:
        return _presence_of(cells)
    return present, missing


def _split_is_published(block: "dict[str, object]") -> bool:
    """Whether describing this file publishes its own blank/non-blank split.

    THE CONFLICT THIS SETTLES, IN ONE SENTENCE (plan amendment A-P3-5;
    review items P3-V3-F1 and P3-V3-F2). V2.4 counts presence by
    BLANKNESS; the producer counts it by its own absence rules; and the
    two differ exactly on the cells that are non-blank and read as
    absences -- a built-in missing marker, or a number it judges a
    stand-in for "no value". V5.1 lets the report state only what
    describing the file would publish about it. So a verdict taken over
    the blank split is a statement the file's own description makes only
    when that description says how many of its missing cells were spelled
    which way -- and that is a floored fact, published per spelling in
    `missing_by_source` and pooled into one unnamed total below the
    publication floor, because a count of two cells sharing a rare
    spelling is a count the floor exists to hide.

    WHERE THE DESCRIPTION NAMES EVERY MISSING CELL'S SOURCE, a reader of
    that description knows the exact multiset of spellings the missing
    cells wear, so every measurement the split takes is derivable from
    what `synthtwin profile` publishes about this file, and reporting it
    states nothing new. That is what this returns True for, and it is
    the ordinary case: a column with no missing cells at all, and a twin
    whose blanks reach the floor, both name every source.

    WHERE IT POOLS ANY OF THEM the split is not derivable, two files the
    producer describes byte for byte alike hold different splits, and
    `_governed` falls back to the file's own description -- which is
    inside the envelope by construction, because it IS the description.
    It does not fall back to a withholding: a silence any file could buy
    by writing one marker cell is the defect amendment V2.4-A1 exists to
    close, and this returns False on exactly the files that could buy it.

    Guarantees:

    - Inputs: one column of the file's OWN description. Not the split
      description, and no measured cell: what may be said has to be a
      function of what describing the file publishes, or the file
      decides what may be said about it (V5.2).
    - Determinism: a fixed function of that block.
    - Errors raised: none.
    """
    missing = _count_at(block, "n_missing")
    if missing is None:
        # No re-description at all. The degenerate paths hand both sides
        # the same empty block, so there is no second reading to choose
        # between and nothing here can move a verdict.
        return True
    by_source = _map_at(block, "missing_by_source")
    if by_source is None:
        return missing == 0
    # THE POOLED REMAINDER IS A FIELD, NOT A KEY, from contract version
    # 5 (its section 5). It used to stand inside the map under this
    # package's own word; it now stands beside the map, and the blank
    # cells with it. What this asks is unchanged: is every absent cell
    # of this column accounted for BY A NAMED SPELLING, so that a reader
    # of the description knows the exact multiset the absent cells wore?
    # A pooled cell is one that is not, whichever field carries it.
    pooled = _count_at(block, "n_missing_withheld")
    if pooled is None or pooled:
        return False
    blank = _count_at(block, "n_missing_blank")
    if blank is None:
        return False
    named = blank
    for key in sorted(by_source):
        named = named + by_source[key]
    return named == missing


def _split_size_is_published(block: "dict[str, object]") -> bool:
    """Whether describing this file publishes HOW MANY cells the split adds.

    A weaker question than `_split_is_published` above, and worth asking
    separately because it has a different answer and buys back real
    teeth (plan amendment A-P3-5 clause 1).

    `missing_by_class` counts a column's holes under synthtwin's own five
    words -- blank, declared-missing, numeric-sentinel, text-code, and
    the pooled remainder -- and because those words carry nothing from
    the table it is published for EVERY role, including the three that
    publish no value of the table at all. So where its pooled remainder
    is empty, the number of holes that are non-blank is published
    exactly, even where their SPELLINGS are not. The two counts the blank
    split owns are then derivable from what describing the file
    publishes, and reporting them says nothing new -- while the
    measurements that need the spellings, distinctness among them, still
    do not.

    That difference is what keeps the round-2 witness caught on a column
    whose role publishes no spellings: thirty holes all spelled the same
    way reach the publication floor, the class map names them
    `(text-code): 30`, and `presence.n_present` misses again.

    Guarantees:

    - Inputs: one column of the file's OWN description. No measured
      cell, for the reason `_split_is_published` gives.
    - Determinism: a fixed function of that block.
    - Errors raised: none.
    """
    missing = _count_at(block, "n_missing")
    if missing is None:
        return True
    by_class = _map_at(block, "missing_by_class")
    if by_class is None:
        return missing == 0
    return _counted(by_class, parsing.MISSING_WITHHELD) == 0


def _governed(
    gated: "list[Check]", measured: "list[Check]", split_published: bool
) -> "list[Check]":
    """One verdict per obligation: the gate's say, then the split's number.

    THE TWO SIDES, AND WHY NEITHER ONE ALONE IS THE ANSWER (V2.4, V5.3;
    review item P3-V2-A1). ``gated`` was built against the file's own
    description -- what `synthtwin profile` would write about this file
    -- and it answers one question only: may a report say anything at
    all about this obligation? ``measured`` was built against the same
    producer's description of the same cells with absence pinned to
    blankness, and it answers the other: what does the file hold,
    counted the way V2.4 counts it? The identities are the same list in
    the same order, because which obligations exist is a function of the
    DESCRIPTION alone and neither block is consulted for it.

    Four cases, and the last is the repair.

    * The gate is closed -- the file's own description would not publish
      what this check measures. WITHHELD, exactly as V5.3 requires, and
      the split's number is not shown, because showing it is what the
      gate exists to prevent.
    * The gate is open and this subcheck measures the WRITTEN CELLS
      rather than a re-description (`_MEASURED_FROM_THE_CELLS`). Either
      side's measurement is the same one; the gated side's is taken.
    * The gate is open and the split has the measurement. The split's
      verdict, which is the only one taken over the right set of cells.
    * The gate is open and the split has NO measurement of that kind:
      counted with every non-blank cell as a value, this column is not a
      column of the kind the obligation is about. That is a MISS. It is
      not a withholding, and the difference is the whole of this
      function's reason to exist: withholding is for what the file's own
      description will not publish, never for what the validator found
      hard to reconstruct.

    WHAT THIS REPLACES. The version before this one withheld every
    presence-dependent obligation of a column whenever the file's own
    description and the blank split disagreed about how many cells were
    present -- so writing ONE cell spelling a built-in missing marker
    turned every level, distinctness and suppression obligation of that
    column from a potential MISS into a withholding. A file could then
    carry none of its published labels, hold counts and dates nothing
    published, and exit 0 under "no checkable obligation was missed"
    with two thirds of its obligations unevaluated. That is a gap in the
    reconstruction moving a verdict, which V2.4 forbids in terms, and it
    let any registered red case be defeated by one added cell. The gap
    is closed by MEASURING over the split rather than by declining to,
    which is what V2.4 asked for all along.

    AND THE SPLIT'S NUMBER IS ONLY TAKEN WHERE THE FILE'S OWN
    DESCRIPTION PUBLISHES THE SPLIT (``split_published``; plan amendment
    A-P3-5, review item P3-V3-F1). Where it pools its missing sources
    below the publication floor, two files that description cannot tell
    apart hold different splits -- fifty-nine labels and one empty cell
    beside fifty-nine labels and one `n/a` -- and the split's verdict
    told them apart, at eight subchecks, two censuses and two exit
    statuses, which V5.1 forbids. There the file's OWN description
    supplies the verdict instead. That is inside the envelope by
    construction, it is never a silence, and it never lets a file stop
    a check: every obligation still lands on a verdict taken from one
    description or the other.
    """
    settled: list[Check] = []
    # Paired strictly: the two sides are the same obligations in the
    # same order, and a build that ever made them differ would be a
    # defect worth stopping on rather than one worth pairing past.
    for closed, found in zip(gated, measured, strict=True):
        if closed.verdict == WITHHELD and closed.citation == _GATE_CLOSED:
            settled = settled + [closed]
            continue
        if closed.subcheck in _MEASURED_FROM_THE_CELLS:
            settled = settled + [closed]
            continue
        if not split_published:
            settled = settled + [closed]
            continue
        if found.verdict == WITHHELD and found.citation == _GATE_CLOSED:
            settled = settled + [
                Check(
                    closed.column,
                    closed.fact,
                    closed.subcheck,
                    MISSED,
                    closed.published,
                    _NOT_OF_THAT_KIND,
                )
            ]
            continue
        settled = settled + [found]
    return settled


def _universal_checks(
    column: contract.ColumnBlock,
    block: "dict[str, object]",
    mine: "tuple[str, ...]",
) -> "list[Check]":
    """The counts every role publishes, whatever its role is."""
    name = column.name
    checks: list[Check] = []
    for field, published in (
        ("n_numeric", column.n_numeric),
        ("n_not_numeric", column.n_not_numeric),
        ("n_out_of_range", column.n_out_of_range),
        ("n_contradictory", column.n_contradictory),
    ):
        measured = _count_at(block, field)
        checks = checks + [
            _exact(
                name,
                f"universal.{field}",
                f"counts.{field}",
                _shown_count(published),
                None if measured is None else _shown_count(measured),
            )
        ]
    checks = checks + _distinctness_checks(column, block, mine)
    return checks


def _distinctness_checks(
    column: contract.ColumnBlock,
    block: "dict[str, object]",
    mine: "tuple[str, ...]",
) -> "list[Check]":
    """The two distinctness counts, at whatever bar this profile sets.

    A CORNER IS ASKED PER FIELD, because the corners are not all
    two-field facts (review item P3-V8-F3). Owner decision 6's
    identifier corner names both counts and the multiset; G12.8's
    numeric envelope is written for the raw count "and the same over
    the folded identities"; G12.7's label envelope is raw `n_distinct`
    and nothing else, in V4.1's words and in the registry's. Asking one
    field-blind question for both put G12.7's authorization on a folded
    count it does not name, and a file whose folded count the
    description publishes EXACTLY was given an AUTHORIZED DEVIATION for
    missing it.
    """
    name = column.name
    facts = column.facts
    group = _group_of(facts)
    checks: list[Check] = []
    for field, published in (
        (_RAW_DISTINCT, column.n_distinct),
        (_FOLDED_DISTINCT, column.n_distinct_folded),
    ):
        measured = _count_at(block, field)
        fact = f"{group}.{field}"
        subcheck = f"distinct.{field}"
        if isinstance(facts, contract.ClockFacts):
            # This role's own explicit cardinality bound, for the
            # reason the date role has one: the construction writes a
            # value per RANK, so a column publishing fewer different
            # times than it has rows is met by a twin holding more.
            checks = checks + [
                _within(
                    name,
                    fact,
                    subcheck,
                    _shown_count(published),
                    None if measured is None else float(measured),
                    _clock_distinct_window(column, facts),
                    ENVELOPE_CLOCK_DISTINCT,
                    float(published),
                )
            ]
            continue
        if isinstance(facts, contract.DatetimeFacts):
            # A column of dates has its own explicit cardinality bound:
            # the construction writes a value per rank and holds far
            # more identities than the published count, so the matrix
            # sets both counts APPROXIMATED here and nowhere else.
            checks = checks + [
                _within(
                    name,
                    fact,
                    subcheck,
                    _shown_count(published),
                    None if measured is None else float(measured),
                    _datetime_distinct_window(column, facts),
                    ENVELOPE_DATETIME_DISTINCT,
                    float(published),
                )
            ]
            continue
        corner = _distinct_corner(facts, mine, field)
        if corner == CORNER_IDENTIFIER_INFEASIBLE:
            # REPORT-ONLY in this corner, so it is a listing entry and
            # not a check (owner decision 6; review item P3-V1-F4).
            # `_corner_listings` names it in the census with the
            # decision that authorizes it.
            continue
        if corner and _envelope_admits_every_count(column, facts, published):
            # V3.5, taken per entry: the envelope this corner authorizes
            # licenses every count a column of this description's length
            # can hold, so nothing written in a CSV settles it and it is
            # a listing rather than a check that cannot fail.
            continue
        if corner:
            checks = checks + [
                _lesser_or_held(
                    name, fact, subcheck, published, measured, corner, column
                )
            ]
            continue
        checks = checks + [
            _exact(
                name,
                fact,
                subcheck,
                _shown_count(published),
                None if measured is None else _shown_count(measured),
            )
        ]
    return checks


def _lesser_or_held(
    name: str,
    fact: str,
    subcheck: str,
    published: int,
    measured: "int | None",
    corner: str,
    column: contract.ColumnBlock,
) -> Check:
    """One distinctness count in a corner the ratified plan names.

    THE EXACT BAR IS TRIED FIRST, and that order is the point. A corner
    AUTHORIZES a lesser outcome; it does not impose one. A twin that
    met the published count in a column whose description sits in a
    corner met the published count, and reporting that as a deviation
    would lower an obligation the twin actually held -- which is the
    class of quiet lowering this project refuses by name. So the corner
    is consulted only once the exact comparison has already failed.
    """
    shown = _shown_count(published)
    if measured is None:
        return Check(name, fact, subcheck, WITHHELD, shown, "", _GATE_CLOSED)
    if measured == published:
        return Check(name, fact, subcheck, HELD, shown, _shown_count(measured))
    facts = column.facts
    supply = _spelling_supply(column, facts, published)
    ceiling = _spelling_ceiling(column, facts, published)
    if supply is None or ceiling is None:
        return _deviation(name, fact, subcheck, shown, corner)
    low = min(supply, published)
    high = max(ceiling, published)
    if low <= measured <= high:
        return Check(
            name,
            fact,
            subcheck,
            AUTHORIZED_DEVIATION,
            f"{shown} ({_shown_window(float(low), float(high))})",
            _shown_count(measured),
            CORNER_CITATIONS[corner],
        )
    return Check(
        name,
        fact,
        subcheck,
        MISSED,
        f"{shown} ({_shown_window(float(low), float(high))})",
        _shown_count(measured),
    )


def _spelling_supply(
    column: contract.ColumnBlock,
    facts: contract.ColumnFacts,
    published: int,
) -> "int | None":
    """How many different spellings this column's own rules can supply.

    The `S` of method G12.7 on a column of labels and the LOW end of
    G12.8's `supply` on a column of numbers, each read off the published
    fields alone. `published` is the count this bar is being drawn for --
    the raw one or the folded one -- because the budget of G6.5 is
    allocated separately for each and the two allocations differ.

    ON A COLUMN OF LABELS a withheld-variant key is an OCCURRENCE COUNT
    and its value is how many spellings covered that many rows each, so
    the rows such an entry covers are `key x value` and not `value`
    (contract 7.4, and method G12.7 writes it `int(key) * count`). The
    version this replaces added the value alone, so a level whose
    withheld variants covered it exactly looked short, an extra spelling
    was invented for it, and a description whose own twin the shipped
    generator writes with three spellings was told four were available
    and reported MISSED against that twin (review item P3-V7-F3).

    ON A COLUMN OF NUMBERS the canonical spelling has no family of its
    own, so all the `plain` cells together supply ONE identity; every
    other style carries the leading-zero family, so each of its cells
    can carry its own. A WITHHELD style count is not a style: the floor
    pooled cells whose styles this description does not name, and the
    generator writes them in whatever style its own construction
    reaches -- `plain` among them. Counting them as leading-zero cells
    read a supply of twenty off a column whose twin could carry sixteen
    (review item P3-V7-F4), so they are counted with the plain cells
    here, which is the side that cannot claim more than the
    construction has.

    AND THE OTHER CLASSES ARE PART OF G12.8'S SUM, which this left out
    altogether (review item P3-V8-F4). The formula has two summands and
    only the first was written: beside the numbers class it adds, for
    each other class, `min(its cell count, its share of the budget in
    G6.5)` -- and both of those are published numbers, so the term needs
    nothing this module may not import. Leaving it out put the floor at
    ONE on every numeric column whose cells are all `plain`, however
    many unreadable, out-of-range or contradictory cells stood beside
    them, and a floor of one is what makes the bar admit every count and
    become a listing. Twenty whole numbers beside two cells that are not
    numbers were told a twin could hold as few as one different value,
    where the classes alone settle three.
    """
    column = _core_column(column)
    facts = _quantitative(facts)
    if isinstance(facts, contract.LabelFacts):
        supply = 0
        for level in facts.levels:
            named = 0
            for spelling in level.variants:
                supply = supply + 1
                named = named + level.variants[spelling]
            for spelling in level.variants_withheld:
                held = level.variants_withheld[spelling]
                supply = supply + held
                named = named + _occurrence_key(spelling) * held
            if named < level.count:
                supply = supply + 1
        return supply + facts.suppressed_levels
    if isinstance(facts, contract.NumericFacts):
        supply = 0
        pooled = 0
        for style in facts.numeric_styles:
            if style in (parsing.STYLE_PLAIN, taxonomy.SUPPRESSED_LABEL):
                pooled = pooled + facts.numeric_styles[style]
            else:
                supply = supply + facts.numeric_styles[style]
        # ...less the padded cells the width census pins, which carry no
        # family of their own -- but NOT folded into the plain pool,
        # because a padded cell and a plain one spell the SAME VALUE
        # differently: `5` and `05` are two identities wherever both
        # forms appear. So each named width keeps one spelling of its
        # own, which is the floor a column all of whose cells carried a
        # single value would still reach.
        pinned = _pinned_padding(facts)
        if pinned > 0:
            supply = max(0, supply - pinned) + _named_pad_widths(facts)
        if pooled > 0:
            supply = supply + 1
        return supply + _other_class_spellings(column, published)
    return None


# The four classes a numeric column's present cells divide into, in the
# order method G6.5 offers them the budget. The numbers class is first
# and is the one G12.8 counts by (value, style) group; the other three
# are written as class-preserving stand-ins (G10.4), and each writes
# exactly as many different ones as the budget hands it.
_CLASSES_IN_BUDGET_ORDER = (
    "n_numeric",
    "n_out_of_range",
    "n_contradictory",
    "n_not_numeric",
)


def _class_cells(column: contract.ColumnBlock) -> "tuple[int, ...]":
    """How many cells each class holds, in the budget order of G6.5."""
    return (
        column.n_numeric,
        column.n_out_of_range,
        column.n_contradictory,
        column.n_not_numeric,
    )


def _class_budget(
    column: contract.ColumnBlock, published: int
) -> "tuple[int, ...]":
    """The G6.5 budget allocation, class by class, in that method's order.

    METHOD G6.5, WRITTEN OUT FROM THE PUBLISHED COUNTS AND NOTHING ELSE.
    Every non-empty class receives one spelling; the remainder of the
    published count is then offered to the classes in the fixed order
    `numbers, out_of_range, contradictory, not_numeric`, each taking as
    much as it can use and never more than its own cell count, until the
    remainder is spent. The four cell counts and the published count are
    all fields of the description, so this is arithmetic on published
    numbers and imports nothing (V1.4).

    WHERE THE PUBLISHED COUNT IS BELOW THE NUMBER OF NON-EMPTY CLASSES
    the published facts do not hold together, and G6.5 says what the
    twin does then: one spelling per class. That is what this returns,
    which is also the number such a twin actually writes -- so the bound
    built on it stays true in the one case the method calls impossible.

    Guarantees: a pure function of the description; every entry is
    between zero and that class's own cell count; a class with no cell
    gets nothing.
    """
    cells = _class_cells(column)
    shares = [1 if held > 0 else 0 for held in cells]
    spent = 0
    for share in shares:
        spent = spent + share
    remainder = max(published - spent, 0)
    for place, held in enumerate(cells):
        if held < 1 or remainder < 1:
            continue
        take = min(remainder, held - shares[place])
        shares[place] = shares[place] + take
        remainder = remainder - take
    return tuple(shares)


def _other_class_spellings(
    column: contract.ColumnBlock, published: int
) -> int:
    """G12.8's second summand: the classes that are not the numbers class.

    `min(its cell count, its share of the budget in G6.5)` for each of
    the three, which is the share itself -- the allocation never hands a
    class more than its own cells. It is the same number at BOTH ends of
    this method's bracket, and that is the point of the repair (review
    item P3-V8-F4): the classes are exactly knowable from the
    description, so they narrow the bracket rather than widening it.
    What stays unknowable is the numbers class alone, and only the part
    of it written `plain`.
    """
    shares = _class_budget(column, published)
    cells = _class_cells(column)
    found = 0
    for place in range(1, len(shares)):
        found = found + min(cells[place], shares[place])
    return found


def _pinned_padding(facts: "contract.NumericFacts") -> int:
    """How many padded cells the width census pins to a field width.

    A CELL WHOSE FIELD WIDTH IS PUBLISHED IS KEYED BY ITS VALUE, exactly
    as a `plain` cell is, and that is the whole of why this number is
    needed on both ends of G12.8's supply. The leading-zero family is
    the one unbounded supply of alternate spellings a numeric column
    has -- `5`, `05`, `005` -- and every step of it writes ONE MORE
    FIGURE. So where the census names the width, the family is spent:
    a value has exactly one leading-zero spelling five figures wide,
    and a twin reaching for a second would leave the published width.

    Both ends read this. Counting a pinned cell as carrying a family it
    cannot reach put the exact bar on a column whose twin cannot meet
    it, and reported a twin that honoured every published width as
    MISSED for the distinctness that honouring them costs -- which is
    the case owner decision 11 already authorizes the envelope for,
    "only where even those cannot supply".

    The `(withheld)` remainder is NOT pinned: the floor held those cells
    back precisely because no width of theirs was named, so the twin
    writes them at whatever width its construction reaches and the
    family is still open to them.
    """
    pinned = 0
    for key in facts.pad_widths:
        if key == taxonomy.SUPPRESSED_LABEL:
            continue
        pinned = pinned + facts.pad_widths[key]
    return pinned


def _named_pad_widths(facts: "contract.NumericFacts") -> int:
    """How many field widths the census names, the `(withheld)` pool aside.

    Each named width is a spelling family of its own: one value written
    two figures wide is `05` and five figures wide is `00005`, so a
    column whose cells all carried one value still holds one identity
    per named width. That is why the pinned cells do not simply join
    the plain pool at the floor.
    """
    named = 0
    for key in facts.pad_widths:
        if key == taxonomy.SUPPRESSED_LABEL:
            continue
        named = named + 1
    return named


def _spelling_ceiling(
    column: contract.ColumnBlock,
    facts: contract.ColumnFacts,
    published: int,
) -> "int | None":
    """The OTHER end of G12.8's supply, and why the two are not one number.

    G12.8's supply is a property of the twin's FINISHED CELLS: each
    (value, style) group of the numbers class supplies one spelling where
    the style is `plain` and its own cell count otherwise, and each
    other class supplies `min(its cell count, its share of the budget in
    G6.5)`. The second summand and the style half of the first are fixed
    exactly by the description. ONE THING IS NOT, and it is the whole of
    the gap: how many different VALUES the plain cells carry is decided
    by the value construction of G5 and G7, which this module may not
    import and does not rewrite. So the description settles two numbers
    rather than one: a FLOOR, where all the plain cells carry one value
    between them, and this CEILING, where each carries its own.

    Reading the floor at both ends is what reported a conforming twin
    MISSED (review item P3-V7-F4): a twenty-two-cell column whose two
    plain cells carried two values holds twenty-two identities where the
    floor reads twenty-one, and the generation report calls that inside
    its own bound. On a column of labels there is no second number --
    G12.7's `S` is settled by the published level blocks alone -- so the
    ceiling IS the floor there and both ends are exact.
    """
    column = _core_column(column)
    facts = _quantitative(facts)
    if isinstance(facts, contract.LabelFacts):
        return _spelling_supply(column, facts, published)
    if not isinstance(facts, contract.NumericFacts):
        return None
    plain = 0
    others = 0
    for style in facts.numeric_styles:
        if style == parsing.STYLE_PLAIN:
            plain = plain + facts.numeric_styles[style]
        else:
            others = others + facts.numeric_styles[style]
    # A PINNED PADDED CELL IS KEYED BY ITS VALUE TOO -- the census fixed
    # its width, and every further spelling of its value is a figure
    # wider -- BUT IT IS NOT KEYED WITH THE PLAIN CELLS. `5` and `05`
    # are two spellings of one value, so a column holding both carries
    # two identities for it, and folding the padded cells into the plain
    # bucket capped the pair at the plain bucket's own ceiling. That put
    # the twin the shipped generator writes OUTSIDE its own bound: a
    # description with three plain and three padded cells over three
    # values was given a ceiling of three where the construction writes
    # four, and a conforming twin was reported MISSED -- which is review
    # item P3-V7-F4's defect reached by a new route. The padded cells
    # take a bucket of their own, capped the same way.
    pinned = _pinned_padding(facts)
    padded_room = 0
    if pinned > 0:
        others = max(0, others - pinned)
        # ONE SPELLING PER VALUE PER NAMED WIDTH, which is why the count
        # of named widths is a factor here and not an afterthought. A
        # value has exactly one padded spelling at one field width, so
        # where a single width is named this is the plain bucket's own
        # cap; where SEVERAL are, the same value reaches a different
        # spelling in each -- `01`, `001` and `0001` are one number and
        # three identities -- and a cap of `n_distinct` then excludes
        # twins the construction actually writes. A column of
        # thirty-three padded cells over three named widths wrote
        # thirty-one identities against a ceiling of thirty and was
        # reported MISSED for it.
        padded_room = min(pinned, column.n_distinct * _named_pad_widths(facts))
    # A PLAIN GROUP IS KEYED BY ITS VALUE, so the plain cells supply one
    # spelling for each different value among them and no more -- and
    # the value construction of G5 and G7 is built to the published
    # count of different values, so there are no more of those than the
    # description publishes. A withheld style count is not a style and
    # is counted here at its own cell count, which is the side that
    # claims MORE room: those cells may each be wearing a style with a
    # leading-zero family of its own.
    room = others + min(plain, column.n_distinct) + padded_room
    # Cells outside the numbers class carry their own share of the G6.5
    # budget, never more than one identity per cell -- and the share is
    # what is added, not the cell count. Adding the cell count was the
    # ceiling saying what the comment beside it already said it did not
    # (review item P3-V8-F4); the share is the same number this method's
    # floor adds, so the two ends move together and the bracket narrows
    # from both sides at once.
    return room + _other_class_spellings(column, published)


def _occurrence_key(key: str) -> int:
    """A multiplicity map's key read as the row count it names (G9.5).

    Leading zeros are padding that does not change the number. A key
    that is not a row count cannot come through the strict loader, and
    one that did is read as covering nothing, which leaves the level
    looking short and invents one more spelling for it -- the side that
    claims MORE supply, and so the side that keeps the exact bar rather
    than lowering it onto a description nobody can state.

    THE KEY IS READ AS THE FIGURES IT IS (review item P3-V8-F5), by the
    contract's own reader and not by one that answers in binary64.
    """
    size = contract.occurrence_size(key)
    if size is None:
        return 0
    return size


def _envelope_admits_every_count(
    column: contract.ColumnBlock,
    facts: contract.ColumnFacts,
    published: int,
) -> bool:
    """Whether this corner's envelope licenses every count a file can hold.

    V3.4 FORBIDS A SUBCHECK THAT CANNOT FAIL AND V3.5 DECIDES IT PER
    ENTRY, and the two distinctness counts of a column in a spelling
    corner are exactly that case (review item P3-V7-F4). The envelope
    G12.8 fixes runs between the published count and the supply, and a
    supply of one is what the published map leaves on the ordinary
    column whose cells are all written one way: the bar then runs from
    one value to every value the column's own cells can hold, a file
    whose whole column collapsed onto one repeated value lands inside
    it, and the only files it can refuse are ones that carry more
    present cells than the description publishes -- which
    `universal.n_present` already refuses, and V3.6 gives a fact
    another subcheck checks to that subcheck.

    So the entry is a LISTING with the sentence saying why. This is not
    a lesser bar quietly taken: a bar admitting every answer is not a
    bar, and the census counts this where it counts every obligation
    nothing in a CSV settles.
    """
    supply = _spelling_supply(column, facts, published)
    ceiling = _spelling_ceiling(column, facts, published)
    if supply is None or ceiling is None:
        return False
    return min(supply, published) <= 1 and (
        max(ceiling, published) >= column.n_present
    )


def _distinct_corner(
    facts: contract.ColumnFacts, mine: "tuple[str, ...]", field: str
) -> str:
    """Which corner, if any, lowers this column's bar on THIS count.

    THE FIELD IS PART OF THE QUESTION (review item P3-V8-F3). A corner
    authorizes a lesser outcome for the facts its own passage names,
    and the three that reach a distinctness count do not name the same
    ones:

    - owner decision 6's identifier corner names `n_distinct`,
      `n_distinct_folded` AND `n_distinct_by_occurrences`, in V4.1's
      words, so both counts are its;
    - G12.8's numeric envelope is written for the raw count and, in its
      own last sentence, "the same over the folded identities", so both
      counts are its;
    - G12.7's label envelope is RAW `n_distinct`. V4.1 says so -- "then
      raw `n_distinct` falls to the G12.7 envelope" -- and so does the
      registry. Folding is not a spelling question: however few
      spellings the published variants supply, the folded identities a
      label column publishes are settled by its published levels, and
      the construction meets that count exactly.

    Asking this without the field gave a label column's FOLDED count
    G12.7's authorization. A description publishing folded 2 whose
    supply is 3 then printed the bar `2 (from 2 to 3)`, and a file
    holding three folded identities where the description publishes two
    was reported an AUTHORIZED DEVIATION instead of a MISS.
    """
    facts = _quantitative(facts)
    if CORNER_IDENTIFIER_INFEASIBLE in mine:
        return CORNER_IDENTIFIER_INFEASIBLE
    if (
        isinstance(facts, contract.LabelFacts)
        and CORNER_LABEL_VARIANTS_SHORT in mine
        and field == _RAW_DISTINCT
    ):
        return CORNER_LABEL_VARIANTS_SHORT
    if isinstance(facts, contract.NumericFacts) and (
        CORNER_NUMERIC_SPELLINGS_SHORT in mine
    ):
        return CORNER_NUMERIC_SPELLINGS_SHORT
    return ""


# What an EMPTY side of the pair is called where a person reads it.
# One side is permitted to be empty and the report prints a value only
# where there is one, so an empty side printed itself as nothing at all:
# the line `counts.affix_prefix: HELD` stood with neither what was
# asked for nor what was found under it, and a check whose two sides
# are both invisible tells a reader nothing about what was checked.
_NO_AFFIX_FRONT = "nothing in front of the number"
_NO_AFFIX_BEHIND = "nothing after the number"


def _shown_affix(side: str, front: bool) -> str:
    """One side of the pair as a person reads it in the report."""
    if side:
        return side
    if front:
        return _NO_AFFIX_FRONT
    return _NO_AFFIX_BEHIND


def _core_column(column: contract.ColumnBlock) -> contract.ColumnBlock:
    """An affixed column seen as the column its own cores make.

    The universal counts of an affixed column answer for its CELLS, and
    a cell reading `250 mg` is not a number, so those counts say the
    column holds no numbers at all. Every G12.8 supply is written over
    a column's number classes, so reading them off the cells put all
    two hundred and forty cells in the "not a number" class and handed
    the bracket an identity for each -- a floor at the published count
    and a ceiling at twice it, which is a bracket that authorizes
    nothing below and everything above. The cores are what those rules
    mean, so they are what the rules are handed.

    IT IS WRITTEN HERE RATHER THAN SHARED WITH THE GENERATOR'S OWN.
    The generator holds a view of the same shape, and importing it
    would put the planner inside the validator's import graph, which
    the profile/generator boundary forbids outright: a validator that
    read the planner could inherit the planner's defects and call the
    result a measurement.

    A column of any other role is returned unchanged, so callers do not
    have to ask which kind they hold.
    """
    facts = column.facts
    if not isinstance(facts, contract.AffixedFacts):
        return column
    return dataclasses.replace(
        column,
        n_present=facts.n_affixed,
        n_numeric=facts.n_core_numeric,
        n_not_numeric=facts.n_core_not_numeric,
        n_out_of_range=facts.n_core_out_of_range,
        n_contradictory=facts.n_core_contradictory,
        facts=facts.numbers,
    )


def _quantitative(facts: contract.ColumnFacts) -> contract.ColumnFacts:
    """The facts the numeric machinery reads, for any role that has some.

    An affixed column's quantitative block is a `NumericFacts` HELD BY
    its own facts rather than being one, so every rule written as "if
    this is a numeric column" walked straight past it -- and walking
    past an envelope is not a neutral omission, because a fact with no
    envelope is compared exactly. That is how the distinctness of a
    column of whole cores came to miss on a correct twin: two hundred
    and forty different cores published, two hundred and thirty-three
    written, and no envelope to say which of the two G12.8 authorizes.
    Unwrapping here puts the affixed role under the same brackets as
    the plain numeric one, which is what its axes already promise.
    """
    if isinstance(facts, contract.AffixedFacts):
        return facts.numbers
    return facts


def _group_of(facts: contract.ColumnFacts) -> str:
    """Which registry group a column's role publishes under."""
    if isinstance(facts, contract.ClockFacts):
        return "clock"
    if isinstance(facts, contract.AffixedFacts):
        # Its quantitative block IS the numeric block, read over the
        # cores, so it takes the numeric group's dispositions entire.
        return "numeric"
    if isinstance(facts, contract.NumericFacts):
        return "numeric"
    if isinstance(facts, contract.LabelFacts):
        return "label"
    if isinstance(facts, contract.DatetimeFacts):
        return "datetime"
    if isinstance(facts, contract.IdentifierFacts):
        return "identifier"
    if isinstance(facts, contract.TextFacts):
        return "free_text"
    if isinstance(facts, contract.UnrepresentableFacts):
        return "numeric_unrepresentable"
    return "empty"


def _role_checks(
    column: contract.ColumnBlock,
    block: "dict[str, object]",
    cells: "list[str]",
    floor: int,
    mine: "tuple[str, ...]",
) -> "list[Check]":
    """Everything the column's own role adds."""
    facts = column.facts
    if isinstance(facts, contract.ClockFacts):
        return _clock_checks(column, facts, block)
    if isinstance(facts, contract.AffixedFacts):
        return _affixed_checks(column, facts, block, cells, floor)
    if isinstance(facts, contract.NumericFacts):
        return _numeric_checks(column, facts, block, cells, floor)
    if isinstance(facts, contract.LabelFacts):
        # THE CENSUS IS CHECKED ON ALL FOUR LABEL ROLES (P4-D18,
        # corrected). It was dispatched on `LongTailFacts` alone while
        # it stood on that role alone; a categorical column with a rare
        # tail carries it too, and it is exactly the case the census
        # was raised for.
        return _label_checks(column, facts, block, floor) + _form_checks(
            column.name, "label.shape_forms", facts.shape_forms,
            block, floor,
        )
    if isinstance(facts, contract.DatetimeFacts):
        return _datetime_checks(column, facts, block, floor, mine)
    if isinstance(facts, contract.TextFacts):
        return _text_checks(column, facts, block, floor)
    if isinstance(facts, contract.IdentifierFacts):
        return _identifier_checks(column, facts, block, mine)
    if isinstance(facts, contract.UnrepresentableFacts):
        return _unrepresentable_checks(column, facts, block)
    return []


# -- the numeric roles ------------------------------------------------


def _affixed_checks(
    column: contract.ColumnBlock,
    facts: contract.AffixedFacts,
    block: "dict[str, object]",
    cells: "list[str]",
    floor: int,
) -> "list[Check]":
    """A column of numbers each wearing one shared piece of text.

    TWO POPULATIONS, and the checks keep them apart exactly as the
    producer does. The pair and how many cells wear it are read off the
    CELLS. Everything quantitative is read off the CORES those cells
    hold, which is why this re-describes the column's cores and hands
    them to the numeric checks: the same window, the same envelope, the
    same arithmetic that a plain numeric column is held to.

    Written because the role shipped with none of this: `AffixedFacts`
    fell through to the empty group and `_role_checks` returned nothing,
    so a file could keep the role, the pair, the row count and the
    distinctness while missing the ladder and every moment, and the
    quality report said not a word (review item P4-AFX-F8).
    """
    name = column.name
    checks: list[Check] = []
    prefix = facts.affix_prefix
    suffix = facts.affix_suffix
    # The CELL population: which cells wear the pair, counted the way
    # the producer counts them.
    cores: list[str] = []
    for cell in cells:
        trimmed = parsing.trimmed(cell)
        if not trimmed.startswith(prefix) or not trimmed.endswith(suffix):
            continue
        core = trimmed[len(prefix) : len(trimmed) - len(suffix)]
        if core:
            cores = cores + [core]
    # `n_affixed` COMES OFF THE FILE'S OWN DESCRIPTION, not off a
    # recount of its cells under the published pair. The difference is
    # V5.1: this report may state about the measured file only what
    # `synthtwin profile`, run on THAT FILE, would publish about it.
    # Counting the file's cells against a pair the DESCRIPTION's author
    # chose states something else -- and `n_affixed` is floor-bounded
    # from below (AF2), so the recount printed exact counts BELOW the
    # publication floor, live functions of a file whose own description
    # publishes no affixed fact at all. A description of one pair
    # checked against a file of another printed "found: 5" beside the
    # pair, which is five cells of somebody's table counted for a
    # reader who may not hold it.
    checks = checks + [
        _exact(
            name,
            "affixed.n_affixed",
            "counts.n_affixed",
            f"{facts.n_affixed}",
            _shown_count_or_none(_count_at(block, "n_affixed")),
        )
    ]
    # THE PAIR ITSELF, compared as the two SPELLINGS they are. Counting
    # how many cells wear one side is not the same check and cannot be
    # substituted for it: one side is permitted to be empty (AF1 forbids
    # only both), every cell in the file wears an empty side, and a
    # count-shaped check would then read the whole column and miss on a
    # file that carried the pair exactly. So each side is settled
    # against what the file's OWN description read off it, which is the
    # producer's reading of the file and is empty-side-correct by
    # construction. A file whose description reads no affix at all
    # carries no such key, and the sentence below says that rather than
    # comparing against a spelling nothing wrote.
    for field, published in (
        ("affix_prefix", prefix),
        ("affix_suffix", suffix),
    ):
        found = _text_at(block, field)
        front = field == "affix_prefix"
        shown = _shown_affix(published, front)
        if found is None:
            # THE FILE'S OWN DESCRIPTION READS NO AFFIX AT ALL, which
            # is the DISCLOSURE GATE closing and is reported in the
            # gate's own words: describing this file on its own
            # publishes no pair, so neither the measurement nor its
            # outcome is shown, and the role axis of this same column
            # reports the MISS that says why.
            #
            # Substituting the PUBLISHED spelling for the missing
            # measured one made the comparison hold by construction: a
            # description of `USD 1 mg` to `USD 100 mg` checked against
            # a file of bare `1` to `100` reported both affix spellings
            # HELD, which is a check stating something about a file it
            # had not looked at.
            checks = checks + [
                Check(
                    name,
                    f"affixed.{field}",
                    f"counts.{field}",
                    WITHHELD,
                    shown,
                    "",
                    _GATE_CLOSED,
                )
            ]
            continue
        # THE COMPARISON IS MADE IN FULL AND THE MEASURED SPELLING IS
        # NEVER PRINTED. It is text read out of the file, and V5.4 is
        # unconditional about that: no string from a measured file
        # reaches this report under any verdict, which is what lets one
        # report be handed to a person who does not hold the file. The
        # affix pair looked like an exception because the DESCRIPTION
        # may publish its own pair -- that is contract C6-9, a rule
        # about the description's own block, and it says nothing about
        # what a report may print about somebody else's file. A
        # milligram description checked against a file of `SECRET-5.16`
        # cells printed `SECRET` on the achieved line.
        #
        # Deciding the verdict on the DISPLAYED text was the other half
        # of the same mistake: a file whose prefix is literally this
        # report's phrase for an empty side compared equal to a
        # description that publishes none. The spellings decide; the
        # report says only which way it came out.
        checks = checks + [
            _silent(
                name,
                f"affixed.{field}",
                f"counts.{field}",
                shown,
                found == published,
                _NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE,
            )
        ]
    # THE FOUR CORE CLASSES, read off the file's own description for
    # the same reason: they are counts of the cells that wear the pair,
    # so a recount under a pair the file does not wear is a count of
    # the file rather than a description of it.
    for field, counted in (
        ("n_core_numeric", facts.n_core_numeric),
        ("n_core_out_of_range", facts.n_core_out_of_range),
        ("n_core_contradictory", facts.n_core_contradictory),
        ("n_core_not_numeric", facts.n_core_not_numeric),
    ):
        checks = checks + [
            _exact(
                name,
                f"affixed.{field}",
                f"counts.{field}",
                f"{counted}",
                _shown_count_or_none(_count_at(block, field)),
            )
        ]
    # The CORE population, handed to the numeric checks as the column
    # its cores make -- so every quantitative obligation is measured by
    # the code that measures a plain numeric column.
    checks = checks + _numeric_checks(
        column, facts.numbers, block, cores, floor
    )
    return checks


def _numeric_checks(
    column: contract.ColumnBlock,
    facts: contract.NumericFacts,
    block: "dict[str, object]",
    cells: "list[str]",
    floor: int,
) -> "list[Check]":
    """A column of counts or of continuous values."""
    name = column.name
    checks: list[Check] = []
    for field, published in (
        ("n_zero", facts.n_zero),
        ("n_negative", facts.n_negative),
        ("n_negative_unrepresentable", facts.n_negative_unrepresentable),
        ("n_used_in_statistics", facts.n_used_in_statistics),
        ("n_left_out_of_statistics", facts.n_left_out_of_statistics),
    ):
        measured = _count_at(block, field)
        checks = checks + [
            _exact(
                name,
                f"numeric.{field}",
                f"counts.{field}",
                _shown_count(published),
                None if measured is None else _shown_count(measured),
            )
        ]
    for field, subcheck, published_truth in (
        ("integer_valued", "type.integer_valued", facts.integer_valued),
        (
            "std_unrepresentable",
            "type.std_unrepresentable",
            facts.std_unrepresentable,
        ),
    ):
        measured_truth = _truth_at(block, field)
        checks = checks + [
            _exact(
                name,
                f"numeric.{field}",
                subcheck,
                _shown_truth(published_truth),
                (
                    None
                    if measured_truth is None
                    else _shown_truth(measured_truth)
                ),
            )
        ]
    share = _number_at(block, "numeric_share")
    checks = checks + [
        _exact(
            name,
            "numeric.numeric_share",
            "counts.numeric_share",
            _shown_number(facts.numeric_share),
            None if share is None else _shown_number(share),
        )
    ]
    checks = checks + _ladder_checks(column, facts, block)
    checks = checks + _moment_checks(column, facts, block)
    checks = checks + _style_checks(column, facts, block, cells, floor)
    return checks


def _ladder_checks(
    column: contract.ColumnBlock,
    facts: contract.NumericFacts,
    block: "dict[str, object]",
) -> "list[Check]":
    """The eleven rungs: the two ends exact, the nine interior in windows."""
    name = column.name
    measured = _inner_at(block, "percentiles")
    published = facts.percentiles
    checks: list[Check] = []
    checks = checks + [
        _rung_end(name, "min", published.minimum, measured),
        _rung_end(name, "max", published.maximum, measured),
    ]
    points = _ladder_points(published.rungs)
    if not points:
        return checks
    reach = _displacement(facts, column.n_present, column.n_distinct_folded)
    for index in range(1, len(_LADDER_KEYS) - 1):
        key = _LADDER_KEYS[index]
        expected = published.rungs[index]
        found = None if measured is None else _number_at(measured, key)
        if expected is None:
            checks = checks + [
                _exact(
                    name,
                    "numeric.percentiles",
                    f"ladder.{key}",
                    "no value at this rung",
                    "no value at this rung" if found is None else "a value",
                )
            ]
            continue
        checks = checks + [
            _within(
                name,
                "numeric.percentiles",
                f"ladder.{key}",
                _shown_number(expected),
                found,
                _rung_window(points, _LADDER_SHARES[index], reach),
                ENVELOPE_NUMERIC_RUNGS,
                expected,
            )
        ]
    return checks


def _rung_end(
    name: str,
    key: str,
    published: "float | None",
    measured: "dict[str, object] | None",
) -> Check:
    """One of the two ends of a numeric ladder, which are exact."""
    found = None if measured is None else _number_at(measured, key)
    return _exact(
        name,
        f"numeric.percentiles.{key}",
        f"ladder.{key}",
        _shown_number(published),
        None if measured is None else _shown_number(found),
    )


def _displacement(
    facts: contract.NumericFacts, present: int, distinct_folded: int
) -> "tuple[float, float]":
    """How far a rung may be displaced, and by how much it then widens.

    Method G12.2, which states G5.6's envelope: the displacement is the
    widest stratum the construction can produce, plus the one extra
    rank a recomputed rung interpolates, over the numeric cells; and
    both ends widen by the half unit exactly two rules can spend.
    """
    numbers = _numeric_cells(facts)
    widest = _largest_stratum(facts, present, distinct_folded)
    return ((widest + 2) / numbers, _half_unit(facts))


def _rung_window(
    points: "list[tuple[float, float]]",
    share: float,
    reach: "tuple[float, float]",
) -> "tuple[float, float]":
    """The window one rung at ``share`` may land in."""
    displacement, half = reach
    low = _ladder_at(points, max(0.0, share - displacement)) - half
    high = _ladder_at(points, min(1.0, share + displacement)) + half
    return (low, high)


def _windows_of(
    column: contract.ColumnBlock, facts: contract.NumericFacts
) -> "dict[str, tuple[float, float]]":
    """The three G12.3 windows this description draws, or none at all.

    Drawn from the published ladder alone, so the answer is a function
    of the description and never of the measured file. An empty mapping
    says the ladder is null at every rung: G12.3's "one column with no
    bound at all", where the three moments are listing entries.

    Guarantees:

    - Inputs: one published column's numeric facts. No measured value.
    - Determinism: a fixed function of the published ladder, the
      published cell counts and the half unit G12.2 grants.
    - Errors raised: none.
    """
    points = _ladder_points(facts.percentiles.rungs)
    if not points:
        return {}
    numbers = _numeric_cells(facts)
    displacement, half = _displacement(
        facts, column.n_present, column.n_distinct_folded
    )
    lows: list[float] = []
    highs: list[float] = []
    ladder: list[float] = []
    for rank in range(numbers):
        share = 0.0 if numbers < 2 else rank / (numbers - 1)
        lows = lows + [
            _ladder_at(points, max(0.0, share - displacement)) - half
        ]
        highs = highs + [
            _ladder_at(points, min(1.0, share + displacement)) + half
        ]
        ladder = ladder + [_ladder_at(points, share)]
    return _moment_windows(lows, highs, ladder, numbers)


def _skew_admits_every_value(
    column: contract.ColumnBlock, facts: contract.NumericFacts
) -> bool:
    """Whether this description's skew window is the whole attainable range.

    REVIEW ITEM P3-V2-C-F2. `moments.skew` is checked against G12.3's
    envelope, and G12.3 ends with a FINITE FALLBACK: where the ladder's
    own spread does not exceed the displacement the construction can
    produce, the denominator's lower end is zero, the quotient has no
    finite upper end, and the published bound falls back to

        -(K - 2) / sqrt(K - 1)   <=   skew   <=   +(K - 2) / sqrt(K - 1)

    which is the range EVERY sample of K values lies in whatever its
    values are. G12.3 is right to print that, because a wide bound tells
    a reader the ladder is too coarse to say anything about the shape --
    but a CHECK against it admits every file there is, and two of the
    six skew windows the suite's own fixtures draw are exactly it.
    Measured: a column rewritten to 227 ones, one nine and one hundred
    thousand achieved the endpoint itself and was reported WITHIN-BOUND.

    THE VALIDATOR MAY NOT DRAW A NARROWER WINDOW OF ITS OWN. V1's
    opening paragraph says every bound an APPROXIMATED fact is checked
    against lives in G12 and is CITED here, never restated, so the two
    can never drift apart. A tighter envelope is a change to the
    generation method, made where that method is written and reviewed
    against the construction it describes -- not invented in the thing
    that checks it, where it would start accusing conforming twins. So
    where G12.3's own bound is the whole range, the honest answer is
    that this description cannot be checked on this fact, and the report
    says that in the census instead of counting a pass.

    Guarantees:

    - Inputs: one published column's numeric facts. No measured value,
      because which obligations exist is a function of the description.
    - Determinism: a fixed function of the published ladder and counts.
    - Errors raised: none.
    """
    if facts.skew is None:
        return False
    windows = _windows_of(column, facts)
    if "skew" not in windows:
        return False
    numbers = _numeric_cells(facts)
    if numbers < 3:
        return False
    reach = (numbers - 2) / math.sqrt(numbers - 1)
    low, high = windows["skew"]
    return low <= -reach and high >= reach


def _moment_checks(
    column: contract.ColumnBlock,
    facts: contract.NumericFacts,
    block: "dict[str, object]",
) -> "list[Check]":
    """`mean`, `std` and `skew`, each against both ends of G12.3.

    A description whose ladder is null at every rung publishes no shape
    at all, so there is no window to draw and the three are listed as
    not checkable rather than passed. So is a skew whose window is the
    statistic's whole attainable range (`_skew_admits_every_value`).
    """
    name = column.name
    published = (
        ("mean", facts.mean),
        ("std", facts.std),
        ("skew", facts.skew),
    )
    checks: list[Check] = []
    windows = _windows_of(column, facts)
    if not windows:
        return checks
    for field, value in published:
        if value is None:
            continue
        # THE ONE MOMENT WHOSE ENVELOPE CAN SAY NOTHING (review item
        # P3-V2-C-F2). Where G12.3's own finite fallback stands, the
        # window IS every value the statistic can take, and a comparison
        # against it admits every file there is. It is a listing entry
        # on that description -- `_listings` files it with the sentence
        # that says why -- and never a check, because a check that
        # cannot fail is the vacuity V3.4 refuses by name.
        if field == "skew" and _skew_admits_every_value(column, facts):
            continue
        found = _number_at(block, field)
        checks = checks + [
            _within(
                name,
                f"numeric.{field}",
                f"moments.{field}",
                _shown_number(value),
                found,
                _window_named(windows, field),
                ENVELOPE_MOMENTS,
                value,
            )
        ]
    return checks


def _moment_windows(
    lows: "list[float]",
    highs: "list[float]",
    ladder: "list[float]",
    numbers: int,
) -> "dict[str, tuple[float, float]]":
    """The three moment windows of method G12.3, from the rank form."""
    found: dict[str, tuple[float, float]] = {}
    mean_low = math.fsum(lows) / numbers
    mean_high = math.fsum(highs) / numbers
    found["mean"] = (mean_low, mean_high)
    if numbers < 2:
        return found
    spread = 0.0
    for rank in range(numbers):
        reach = max(
            ladder[rank] - lows[rank], highs[rank] - ladder[rank]
        )
        spread = spread + reach * reach
    displacement = math.sqrt(spread / numbers)
    sample = _sample_deviation(ladder, numbers)
    widen = displacement * math.sqrt(numbers / (numbers - 1))
    found["std"] = (max(0.0, sample - widen), sample + widen)
    if numbers < 3:
        return found
    population = _population_deviation(ladder, numbers)
    low_end = max(0.0, population - displacement)
    high_end = population + displacement
    cubed_low = math.fsum(
        [(lows[rank] - mean_high) ** 3 for rank in range(numbers)]
    ) / numbers
    cubed_high = math.fsum(
        [(highs[rank] - mean_low) ** 3 for rank in range(numbers)]
    ) / numbers
    reach = (numbers - 2) / math.sqrt(numbers - 1)
    if low_end <= 0.0:
        found["skew"] = (-reach, reach)
        return found
    ends = [
        cubed_low / (low_end**3),
        cubed_low / (high_end**3),
        cubed_high / (low_end**3),
        cubed_high / (high_end**3),
    ]
    found["skew"] = (max(-reach, min(ends)), min(reach, max(ends)))
    return found


def _sample_deviation(values: "list[float]", count: int) -> float:
    """The standard deviation the profiler's own formula computes."""
    mean = math.fsum(values) / count
    total = math.fsum([(value - mean) ** 2 for value in values])
    return math.sqrt(total / (count - 1))


def _population_deviation(values: "list[float]", count: int) -> float:
    """The population deviation the skewness divides by."""
    mean = math.fsum(values) / count
    total = math.fsum([(value - mean) ** 2 for value in values])
    return math.sqrt(total / count)


# The two forms a value's canonical text can carry a decimal point in,
# which is the pair contract 7.5.7's spill clause is stated over. Named
# once so the clause and the window it is settled against count over the
# same two forms.
_POINT_CARRYING = (parsing.STYLE_DECIMAL, parsing.STYLE_EXPONENT_LOWER)


def _own_styles(block: "dict[str, object]") -> "dict[str, int]":
    """The style map the file's OWN description publishes for a column.

    Empty where that description carries none, which the caller has
    already settled: `_style_checks` returns before this is reached
    where `numeric_styles` is not in the block at all.
    """
    found = _map_at(block, "numeric_styles")
    if found is None:
        return {}
    return found


def _unread_cells(block: "dict[str, object]", cells: "list[str]") -> int:
    """Non-blank cells the file's own description does not count as values.

    The recount below counts every non-blank cell, because V2.4 says
    presence on the verdict side is BLANKNESS. The file's own
    description counts the cells IT reads as present, and a spelling in
    the producer's built-in missing table is non-blank and read as
    absent -- residual R-P2-13's own case. So the two denominators can
    differ, and the difference is how many more cells the recount can
    find in a form than that description's own map accounts for. It
    widens the room the window below leaves and never narrows it: a
    count the description does not carry may not be settled from it.

    Guarantees:

    - Inputs: one re-described block and the column's written cells.
    - Determinism: a fixed function of the two.
    - Errors raised: none.
    """
    present = 0
    for cell in cells:
        if parsing.trimmed(cell):
            present = present + 1
    counted = _count_at(block, "n_present")
    if counted is None or counted > present:
        return 0
    return present - counted


def _recount_window(
    own: "dict[str, int]",
    floor: int,
    unread: int,
    styles: "tuple[str, ...]",
) -> "tuple[int, int]":
    """How many cells of these forms the file's own description allows.

    THE ENVELOPE V5.1 DRAWS, IN ARITHMETIC (review item P3-V2-D-F2). A
    description names a form only where at least `floor` cells wear it;
    everything below that goes into one pooled total and the form is
    never named. So what `synthtwin profile` publishes about this file's
    spellings is: an exact count for each named form, one total for all
    the rest together, and nothing else. Every count vector consistent
    with those numbers is a file that description could equally be
    describing, and a report may state only what is true of all of them.

    The two ends follow from that and from nothing measured:

    * each named form contributes its published count exactly, and the
      `unread` cells above can add to any form, so they widen the top;
    * the unnamed forms share the pooled total, none of them reaching
      the floor -- so the forms asked about here can take at most
      `floor - 1` each of it, and at least whatever the OTHER unnamed
      forms cannot hold.

    Guarantees:

    - Inputs: the file's own published style map, the publication floor
      it was written under, how many non-blank cells that description
      does not count as values, and the forms being asked about.
    - Determinism: a fixed function of those four. No measured recount
      is consulted: this says what the description allows, and the
      caller compares it with what the file holds.
    - Errors raised: none.
    """
    pooled = _counted(own, taxonomy.SUPPRESSED_LABEL)
    room = floor - 1
    room = max(room, 0)
    known = 0
    asked_unnamed = 0
    for style in styles:
        if style in own:
            known = known + own[style]
        else:
            asked_unnamed = asked_unnamed + 1
    other_unnamed = 0
    for style in contract.NUMERIC_STYLES:
        if style not in own and style not in styles:
            other_unnamed = other_unnamed + 1
    high = asked_unnamed * room
    high = min(high, pooled)
    low = pooled - other_unnamed * room
    low = max(low, 0)
    return known + low, known + high + unread


def _window_equals(
    window: "tuple[int, int]", found: int, target: int
) -> "bool | None":
    """Whether ``found`` is ``target``, or None where saying would tell.

    The verdict is the recount's own -- the window decides only whether
    it may be reported. Where the window holds more than one count and
    the target is one of them, two files the producer describes alike
    would get different verdicts, so nothing is said (V5.3).
    """
    low, high = window
    if low < high and low <= target <= high:
        return None
    return found == target


def _window_at_least(
    window: "tuple[int, int]", found: int, target: int
) -> "bool | None":
    """Whether ``found`` reaches ``target``, or None where saying would tell."""
    low, high = window
    if low >= target or high < target:
        return found >= target
    return None


def _window_at_most(
    window: "tuple[int, int]", found: int, target: int
) -> "bool | None":
    """Whether ``found`` stays under ``target``, or None where saying tells."""
    low, high = window
    if high <= target or low > target:
        return found <= target
    return None


def _style_checks(
    column: contract.ColumnBlock,
    facts: contract.NumericFacts,
    block: "dict[str, object]",
    cells: "list[str]",
    floor: int,
) -> "list[Check]":
    """The numeric-style identity of contract 7.5.7, clause by clause.

    Every clause is computable from the written cells and the published
    map alone, and each is its own subcheck so a red case can name the
    one it must fail. The recount is per cell, through the profiler's
    own `parsing.numeric_style`, so it is the same classification the
    description was made with.

    AND EVERY CLAUSE IS READ THROUGH THE FILE'S OWN DESCRIPTION (review
    item P3-V2-D-F2; V5.1, V5.3 and V5.4). The counts were never printed
    -- that much was already true -- but nine of the ten clauses
    compared the exact recount against a published number and reported
    the outcome, and a form fewer cells wear than the publication floor
    is a form no description of that file names. The witness this stands
    on: two files `synthtwin profile` describes byte for byte alike,
    differing only in whether one pooled cell was written `1E5` or
    `1e5`, produced different reports, different censuses and different
    screen output. ONE report told them apart, which is the thing V5.1
    forbids however few times it is run.

    A SECOND WITNESS USED TO STAND HERE AND NO LONGER CARRIES ANY WEIGHT
    (plan amendment A-P3-13, owner ruling 2026-08-14): six candidate
    descriptions differing only in their style map pinned a sub-floor
    count exactly, by trying each and finding the one that HELD. The
    owner ruled that a person who can submit descriptions of their own
    choosing and re-run the check is holding the file, so this product
    no longer promises to stop them. Nothing in this function changed
    for it, because the first witness settles every clause here on its
    own.

    So each clause is settled against a WINDOW rather than against the
    recount: what the file's own description publishes about its own
    style map fixes some of the six counts exactly, leaves the rest
    inside the room its pooled total leaves them, and the clause is
    reported only where every count in that window answers it the same
    way. Where they do not, the verdict is WITHHELD with `_GATE_POOLED`.
    Nothing about which subchecks exist changes, and no count is printed
    that was not printed before.
    """
    name = column.name
    if "numeric_styles" not in block:
        # The gate closed. Every obligation this column carries is still
        # ACCOUNTED FOR -- withheld one by one rather than dropped --
        # because an obligation that leaves the census without a line is
        # an obligation a reader cannot tell was never measured. AND
        # UNDER THE SAME IDENTITIES it would have carried verdicts under
        # (review item P3-V1-F11): the version this replaces withheld
        # one invented `styles.identity` and three keys, so the same
        # description set nine style obligations against one file and
        # four against another, while the census called each of them
        # every obligation there was.
        withheld: list[Check] = []
        for subcheck in _style_subchecks(column, facts):
            # The census of widths is its own published fact, so its
            # withheld identities carry its own name. Filing them under
            # the forms map would make the two sides of `_governed`
            # disagree about which fact a subcheck binds, and one of the
            # two would then be reported under a fact it is not about.
            fact = "numeric.numeric_styles"
            if subcheck[:17] == "widths.published.":
                fact = "numeric.fraction_widths"
            if subcheck[:15] == "pads.published.":
                fact = "numeric.pad_widths"
            withheld = withheld + [
                _withheld(name, fact, subcheck, _GATE_CLOSED)
            ]
        return withheld
    recount, no_point_free = _recounted_styles(cells)
    published = facts.numeric_styles
    remainder = _counted(published, taxonomy.SUPPRESSED_LABEL)
    own = _own_styles(block)
    unread = _unread_cells(block, cells)

    def named(style: str) -> int:
        return _counted(published, style)

    def found(styles: "tuple[str, ...]") -> int:
        total = 0
        for style in styles:
            total = total + _counted(recount, style)
        return total

    def window(styles: "tuple[str, ...]") -> "tuple[int, int]":
        return _recount_window(own, floor, unread, styles)

    checks: list[Check] = []
    for style in (
        parsing.STYLE_LEADING_ZERO,
        parsing.STYLE_LEADING_PLUS,
        parsing.STYLE_EXPONENT_UPPER,
    ):
        checks = checks + [
            _silent(
                name,
                "numeric.numeric_styles",
                f"styles.exact.{style}",
                _shown_count(named(style)),
                _window_equals(
                    window((style,)), found((style,)), named(style)
                ),
                _NOT_SHOWN_IT_IS_A_COUNT_OF_THE_FILE,
                _GATE_POOLED,
            )
        ]
    for style in _floor_styles(facts):
        checks = checks + [
            _silent(
                name,
                "numeric.numeric_styles",
                f"styles.at-least.{style}",
                _shown_count(named(style)),
                _window_at_least(
                    window((style,)), found((style,)), named(style)
                ),
                _NOT_SHOWN_IT_IS_A_COUNT_OF_THE_FILE,
                _GATE_POOLED,
            )
        ]
    spill = max(
        0,
        no_point_free
        - named(parsing.STYLE_DECIMAL)
        - named(parsing.STYLE_EXPONENT_LOWER)
        - named(parsing.STYLE_EXPONENT_UPPER),
    )
    checks = checks + [
        _silent(
            name,
            "numeric.numeric_styles",
            "styles.spill",
            "the two canonical point-carrying forms carry the spill",
            _window_equals(
                window(_POINT_CARRYING),
                found(_POINT_CARRYING),
                named(parsing.STYLE_DECIMAL)
                + named(parsing.STYLE_EXPONENT_LOWER)
                + spill,
            ),
            _NOT_SHOWN_IT_IS_A_COUNT_OF_THE_FILE,
            _GATE_POOLED,
        ),
        _silent(
            name,
            "numeric.numeric_styles",
            "styles.remainder",
            "the pooled cells are spelled by their own values",
            _window_equals(
                window((parsing.STYLE_PLAIN,)),
                found((parsing.STYLE_PLAIN,)),
                named(parsing.STYLE_PLAIN) + remainder - spill,
            ),
            _NOT_SHOWN_IT_IS_A_COUNT_OF_THE_FILE,
            _GATE_POOLED,
        ),
    ]
    # EVERY CELL WEARS A SPELLING OF ITS OWN VALUE (G6.1, G6.3; review
    # item P3-V2-C-F1). "A numeric cell is written in exactly one of six
    # styles, and in no other form" is G6.1's own sentence, and G6.3
    # fixes the exact text of each of the six for a value, with the
    # leading-zero family available inside every style but `plain`. Until
    # this subcheck existed nothing in the validator asked that question
    # at all: the style checks counted how many cells wore each FORM and
    # the ceiling below asked how many were not canonical, and both are
    # arithmetic over counts. So a twin whose every decimal cell carried
    # a trailing zero -- `66.60138701960640` where the shortest round
    # trip of that same number is `66.6013870196064` -- met every one of
    # them and validated with exit 0. The ceiling below could not catch
    # it, because on that column the published decimal count is the cell
    # count and the ceiling is every cell there is.
    checks = checks + [
        _silent(
            name,
            "numeric.numeric_styles",
            "styles.spelled",
            (
                "every cell written as a number spelled in one of the "
                "six published forms of its own value"
            ),
            _cells_outside_the_styles(
                cells, facts.integer_valued, _published_widths(facts)
            )
            == 0,
            _NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE,
        )
    ]
    # THE POOL'S SPLIT BETWEEN THE TWO CANONICAL FORMS, PER CELL (plan
    # P3-D8.1's last clause; review item P3-V1-F7). Everything above is
    # arithmetic over COUNTS, and round 4 of the Phase 2 review showed
    # what counts alone allow: a withheld pool re-spelled wholesale from
    # one canonical form into the other leaves every total where it was.
    # A pooled cell has no published form -- that is what pooling MEANS
    # -- so the only thing it can owe is its own value's canonical text,
    # and the published counts are the ONLY licence for a point-carrying
    # spelling that is not that text. So each of the two forms is owed a
    # ceiling as well as a floor, counted per cell from the value alone.
    # The generator checks itself against this same clause; until this
    # subcheck existed the validator did not, and a twin holding `2.50`
    # where its value's canonical text is `2.5` passed every style
    # check.
    #
    # AND A POOLED FORM'S CEILING IS READ THROUGH THE FILE'S OWN
    # DESCRIPTION TOO (review item P3-V2-D-F2). A cell written in a form
    # that description POOLS is a cell it does not name, so a verdict
    # that counted the pooled cells of one form and reported whether
    # they were canonical would tell two pooled files apart -- which is
    # what the `1E5`/`1e5` witness did here, this subcheck HELD on one
    # file and MISSED on the other for two descriptions that were byte
    # for byte the same. Where the form is pooled the ceiling is reported
    # only where the ROOM that description leaves the form settles it: a
    # form the pool cannot fill past the ceiling is HELD whatever those
    # cells wear, because a cell that is not canonical IN a form is
    # first of all a cell in that form.
    #
    # WHERE THE FORM IS NAMED the recount is compared EXACTLY, and one
    # cell over the licence misses (owner ruling 2026-08-14; plan
    # amendment A-P3-13, which withdraws A-P3-10 clause 1's rounding).
    # Between the two rounds this line rounded the recount DOWN to a
    # whole number of publication floors, so that a person trying one
    # candidate description after another could locate the count no
    # closer than a floor-wide block. That defence is no longer owed:
    # the owner ruled that `validate` answers questions about a file the
    # person running it already holds, so narrowing a withheld number by
    # submitting descriptions and watching verdicts flip is not a thing
    # this product defends against. It bought a bound that round 5 then
    # showed it did not even have -- the floor is itself a number the
    # candidate chooses, so sweeping `small_cell_floor` read the exact
    # count straight back off the rounded comparison -- and it cost
    # every file between one cell and one floor over its licence.
    #
    # WHAT STILL HOLDS HERE, and it is the half that governs the report
    # a reader is handed. No measured count is printed by this subcheck
    # on any file: the line says the licence and the verdict, never the
    # recount, and V5.4 is untouched. And the FORM counts are gated as
    # they were -- which of the six forms a cell wears is published and
    # floored, so the pooled branch below still settles against the room
    # the file's own description leaves and never against the recount.
    #
    # WHY THE EXACT COMPARISON IS INSIDE THE RULING at all. Amendment
    # A-P3-5 clause 3 ruled canonicality outside V5.1's envelope: the
    # producer's own form ladder discards it, so it publishes it about no
    # file at any count, there is no floor to appeal to and no window to
    # draw, and withholding would withhold it forever. Two files that
    # description cannot tell apart therefore get different verdicts here
    # BY RULING, and always did; what A-P3-10 clause 1 added was a bound
    # against the candidate sweep, and the sweep is what the owner ruled
    # out of scope.
    for style in _ceilinged_styles(column, facts):
        odd = _noncanonical_cells(cells, style, facts.integer_valued)
        settled: bool | None = odd <= named(style)
        if style not in own:
            settled = _window_at_most(
                (0, window((style,))[1]), odd, named(style)
            )
        checks = checks + [
            _silent(
                name,
                "numeric.numeric_styles",
                f"styles.canonical.{style}",
                (
                    f"at most {named(style)} cell(s) written in the "
                    f"{style} form in any way but their own value's "
                    f"canonical spelling"
                ),
                settled,
                _NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE,
                _GATE_POOLED,
            )
        ]
    measured = _map_at(block, "numeric_styles")
    # HOW MANY CELLS THIS DESCRIPTION DOES NOT NAME A FORM FOR. The
    # publication floor pools every form fewer cells wear than the floor
    # into one key and publishes no count for any of them, so a cell in
    # that pool has no published form at all -- and whatever form a twin
    # of this description gives it is a form the description permitted.
    # Where the pool is empty the named counts are exact, which is the
    # ordinary case and the one every earlier round measured.
    pooled = 0
    if taxonomy.SUPPRESSED_LABEL in published:
        pooled = published[taxonomy.SUPPRESSED_LABEL]
    for style in sorted(published):
        if style == taxonomy.SUPPRESSED_LABEL:
            continue
        checks = checks + [
            _floor_governed(
                name,
                "numeric.numeric_styles",
                f"styles.published.{style}",
                published[style],
                measured,
                style,
                floor,
                pooled,
            )
        ]
    # THE CENSUS OF WIDTHS, ON THE SAME TERMS AS THE FORMS MAP. Each
    # named width is a count of cells the file evidences by holding
    # them, and the pooled remainder names no width so it is checked as
    # the pool it is. Without this the twin owed the widths nothing: a
    # column of eleven `1.00` cells and eleven `2.000` cells would have
    # been carried by a twin writing every cell at one place, and the
    # quality report would have called it held.
    widths = _map_at(block, "fraction_widths")
    census = facts.fraction_widths
    held_back = 0
    if taxonomy.SUPPRESSED_LABEL in census:
        held_back = census[taxonomy.SUPPRESSED_LABEL]
    for width in sorted(census):
        if width == taxonomy.SUPPRESSED_LABEL:
            continue
        checks = checks + [
            _floor_governed(
                name,
                "numeric.fraction_widths",
                f"widths.published.{width}",
                census[width],
                widths,
                width,
                floor,
                held_back,
            )
        ]
    # THE CENSUS OF FIELD WIDTHS, ON THOSE SAME TERMS (P4-D14). Without
    # this the twin owed the widths nothing: a column of two hundred
    # and forty six-figure codes would have been carried by a twin
    # writing fields two to five figures wide, and the quality report
    # would have called it held -- which is exactly what it did before
    # this census existed.
    pads = _map_at(block, "pad_widths")
    padding = facts.pad_widths
    pooled_pads = 0
    if taxonomy.SUPPRESSED_LABEL in padding:
        pooled_pads = padding[taxonomy.SUPPRESSED_LABEL]
    for width in sorted(padding):
        if width == taxonomy.SUPPRESSED_LABEL:
            continue
        checks = checks + [
            _floor_governed(
                name,
                "numeric.pad_widths",
                f"pads.published.{width}",
                padding[width],
                pads,
                width,
                floor,
                pooled_pads,
            )
        ]
    return checks


# WHAT USED TO STAND HERE, and why nothing does (owner ruling
# 2026-08-14; plan amendment A-P3-13). `_at_the_floors_resolution`
# rounded the canonical recount DOWN to a whole number of publication
# floors before it reached a verdict, so that a person submitting one
# candidate description after another could locate the count no closer
# than a floor-wide block. The owner ruled that defence out of scope --
# `validate` answers questions about a file the person running it holds
# -- and the amendment withdraws it in those words. The function is
# deleted rather than left unused so that no later reader takes it for a
# rule still in force, and the ceiling's teeth are back at one cell.


def _floor_styles(facts: contract.NumericFacts) -> "list[str]":
    """The three floor forms this description actually asks for.

    Contract 7.5.7 makes the published count of these three forms a
    FLOOR: the recount must be at least the published number. Where the
    description publishes none of a form, "at least none" is an
    obligation every file on earth meets -- so it is not an obligation
    at all, and emitting it as an executable subcheck is the vacuity
    V3.4 refuses by name (review item P3-V2-B-F10). The census counted
    thirteen such lines as HELD across the five suite fixtures, which
    made the held count say that something had been checked that
    nothing could have failed.

    NOTHING IS LOWERED BY LEAVING THEM OUT. The form is still governed
    where the description says anything about it at all: its published
    key carries `styles.published.<form>`, and both canonical forms
    carry `styles.canonical.<form>`, whose ceiling of zero non-canonical
    cells is exactly what a description publishing none of that form
    asks for. What goes is a comparison against nothing.

    Guarantees:

    - Inputs: one column's published numeric facts. Nothing else.
    - Determinism: a fixed function of the published style map, in the
      contract's own order.
    - Errors raised: none.
    """
    asked: list[str] = []
    for style in (
        parsing.STYLE_PLAIN,
        parsing.STYLE_DECIMAL,
        parsing.STYLE_EXPONENT_LOWER,
    ):
        if _counted(facts.numeric_styles, style) > 0:
            asked = asked + [style]
    return asked


def _ceilinged_styles(
    column: contract.ColumnBlock, facts: contract.NumericFacts
) -> "list[str]":
    """The canonical forms whose ceiling this description can be over.

    REVIEW ITEM P3-V2-C-F1, and plan amendment A-P3-2, which records the
    lowering in those words. The ceiling P3-D8.1 ratifies is the
    PUBLISHED count of cells in the form: at most `p(s)` of the cells
    written in form `s` may carry anything but their own value's
    canonical text, because the pooled cells -- the ones the count does
    not name -- are the ones that owe it. The arithmetic is right and it
    is the ratified clause; what was wrong was filing it where it cannot
    bite. A column of two hundred and forty cells publishing two hundred
    and forty `decimal` ones has a ceiling of two hundred and forty and
    admits every file that carries the rows the description publishes,
    so every cell of it could be re-spelled and the check still HELD.

    So the entry is filed where a file of the PUBLISHED LENGTH can carry
    more cells in that form than the ceiling licenses -- `p(s)` below
    the description's own row count -- and is a listing entry otherwise,
    with a sentence saying the description already names that form for
    every cell the file can hold. A longer file can exceed it, and such
    a file misses `rows.n_rows` and every count taken over the cells;
    what it no longer does is contribute a MISSED line here, and that is
    the whole of what this costs.

    NOTHING THIS CHANGE TOUCHES IS THE PER-CELL OBLIGATION. Every cell
    still owes a spelling of its own value in one of the six forms, on
    every column, and `styles.spelled` is that check.

    Guarantees:

    - Inputs: one published column and its numeric facts. No measured
      value, because which obligations exist is a function of the
      description alone.
    - Determinism: a fixed function of the published style map and the
      published row count, in the contract's own order.
    - Errors raised: none.
    """
    rows = column.n_present + column.n_missing
    asked: list[str] = []
    for style in (parsing.STYLE_DECIMAL, parsing.STYLE_EXPONENT_LOWER):
        if _counted(facts.numeric_styles, style) < rows:
            asked = asked + [style]
    return asked


def _style_subchecks(
    column: contract.ColumnBlock, facts: contract.NumericFacts
) -> "list[str]":
    """Every style obligation this column carries, in the order they are
    built.

    One list, read by both halves of `_style_checks`, so the identities
    a withheld column carries are the identities a measured one carries.
    Two lists said to be the same by hand were two lists that stopped
    being the same.
    """
    named = [
        f"styles.exact.{style}"
        for style in (
            parsing.STYLE_LEADING_ZERO,
            parsing.STYLE_LEADING_PLUS,
            parsing.STYLE_EXPONENT_UPPER,
        )
    ]
    named = named + [
        f"styles.at-least.{style}" for style in _floor_styles(facts)
    ]
    named = named + ["styles.spill", "styles.remainder", "styles.spelled"]
    named = named + [
        f"styles.canonical.{style}"
        for style in _ceilinged_styles(column, facts)
    ]
    for style in sorted(facts.numeric_styles):
        if style == taxonomy.SUPPRESSED_LABEL:
            continue
        named = named + [f"styles.published.{style}"]
    for width in sorted(facts.fraction_widths):
        if width == taxonomy.SUPPRESSED_LABEL:
            continue
        named = named + [f"widths.published.{width}"]
    for width in sorted(facts.pad_widths):
        if width == taxonomy.SUPPRESSED_LABEL:
            continue
        named = named + [f"pads.published.{width}"]
    return named


def _recounted_styles(
    cells: "list[str]",
) -> "tuple[dict[str, int], int]":
    """How the present numeric cells were written, and how many need a point.

    The second number is method 7.5.7's `NW`: written numeric cells
    whose VALUE has no point-free spelling at all. It is read off the
    values and never off the spellings, because counting the cells that
    were written with a point would make the identity circular.
    """
    counted: dict[str, int] = {}
    no_point_free = 0
    for cell in cells:
        body = parsing.trimmed(cell)
        if not body:
            continue
        if parsing.classify_number(body) != parsing.NUMBER:
            continue
        style = parsing.numeric_style(body)
        counted[style] = _counted(counted, style) + 1
        value = parsing.parse_number(body)
        if value is not None and not parsing.is_whole_number(value):
            no_point_free = no_point_free + 1
    return counted, no_point_free


def _canonical_text(value: float, whole_column: bool) -> str:
    """The canonical spelling of one value, written from method G6.2.

    WRITTEN FROM THE DOCUMENT, NOT IMPORTED (V1.4, V4.2). The generator
    has its own copy of this rule; a validator that called it would
    share every spelling defect with the thing it is a second opinion
    on, so the rule is carried out here from G6.2's own sentences:

    - where the column publishes that every value is a whole number,
      the base-ten digits of the exact integer, with a leading `-` when
      negative, no decimal point and no exponent, and zero written `0`
      and never `-0`;
    - otherwise the shortest decimal digits that read back as exactly
      this value, in fixed-point notation while the decimal point sits
      inside G6.2's window and in lower-case exponent notation outside
      it -- which is what `repr` of a float produces, as the method says
      in as many words. Zero is written `0.0` and never `-0.0`, which
      is the same rule one line up: the sign of a zero is not a fact
      any description publishes.
    """
    if whole_column:
        return f"{int(value)}"
    if value == 0.0:
        return "0.0"
    return repr(value)


def _noncanonical_cells(
    cells: "list[str]", style: str, whole_column: bool
) -> int:
    """How many cells in one style are NOT their value's canonical text.

    Counted per cell from the value alone, which is what makes it
    independent: the spelling is read off the finished text and the
    text it is compared against is computed from the number that text
    reads back as, with no generator bookkeeping anywhere between them.
    """
    odd = 0
    for cell in cells:
        body = parsing.trimmed(cell)
        if not body:
            continue
        if parsing.numeric_style(body) != style:
            continue
        if parsing.classify_number(body) != parsing.NUMBER:
            continue
        value = parsing.parse_number(body)
        if value is None:
            continue
        if body != _canonical_text(value, whole_column):
            odd = odd + 1
    return odd


def _figures_of(value: float) -> "tuple[str, str, int]":
    """The shortest round-trip figures of one value, and its point.

    WRITTEN FROM THE DOCUMENT, NOT IMPORTED (V1.4, V4.2), exactly as
    `_canonical_text` above is. Returns the sign, the figures and the
    position of the decimal point relative to them, so that
    `value = 0.figures x 10 ** point` -- the three pieces G6.2 names,
    and the three every spelling in G6.3 is built from. The figures are
    the shortest decimal string that reads back as exactly this number,
    which is what `repr` of a float produces, and G6.2 says so in as
    many words.

    Guarantees:

    - Inputs: one finite binary64. Sensible only for a value a written
      cell read back as.
    - Determinism: the answer depends only on the value.
    - Errors raised: none for a finite value.
    - Boundary: no I/O of any kind, and nothing measured travels out --
      the figures come from the NUMBER a cell read back as, never from
      the cell's own characters.
    """
    text = repr(value)
    sign = ""
    body = text
    if text[:1] == "-":
        sign = "-"
        body = text[1:]
    mantissa = body
    exponent = 0
    marker = -1
    for index in range(len(body)):
        if body[index] == "e":
            marker = index
    if marker >= 0:
        mantissa = body[:marker]
        exponent = int(body[marker + 1 :])
    point = -1
    for index in range(len(mantissa)):
        if mantissa[index] == ".":
            point = index
    if point < 0:
        figures = mantissa
        place = len(mantissa) + exponent
    else:
        figures = f"{mantissa[:point]}{mantissa[point + 1 :]}"
        place = point + exponent
    lead = 0
    while lead < len(figures) - 1 and figures[lead] == "0":
        lead = lead + 1
    figures = figures[lead:]
    place = place - lead
    end = len(figures)
    while end > 1 and figures[end - 1] == "0":
        end = end - 1
    figures = figures[:end]
    if figures == "0":
        return sign, "0", 1
    return sign, figures, place


def _fixed_text(sign: str, figures: str, place: int) -> str:
    """G6.3's `decimal` spelling: the figures in full, with a point."""
    if place <= 0:
        return f"{sign}0.{'0' * (-place)}{figures}"
    if place >= len(figures):
        return f"{sign}{figures}{'0' * (place - len(figures))}.0"
    return f"{sign}{figures[:place]}.{figures[place:]}"


def _exponent_text(sign: str, figures: str, place: int, marker: str) -> str:
    """G6.3's two exponent spellings: `d[.ddd]e+XX`, sign always written."""
    power = place - 1
    body = figures[:1]
    if len(figures) > 1:
        body = f"{figures[:1]}.{figures[1:]}"
    lead = "+"
    if power < 0:
        lead = "-"
    return f"{sign}{body}{marker}{lead}{abs(power):02d}"


def _point_free_text(value: float, canonical: str) -> "str | None":
    """G6.2's point-free spelling, or None where the value has none.

    A whole value's figures with its trailing zeros written out and no
    point and no exponent, AT ANY WIDTH -- owner decision 10 withdrew
    the sixteen-figure ceiling, which belongs to the canonical spelling
    of a number inside a profile document and not to a cell of a twin.
    Where the value is not whole no point-free spelling of it exists,
    and this says so rather than handing back the canonical text: the
    caller is asking which spellings the six styles can write, and
    `plain` cannot write this one.
    """
    if "." not in canonical and "e" not in canonical and "E" not in canonical:
        return canonical
    sign, figures, place = _figures_of(value)
    if figures == "0":
        return "0"
    if place >= len(figures):
        return f"{sign}{figures}{'0' * (place - len(figures))}"
    return None


def _permitted_spellings(
    value: float, whole_column: bool, widths: "tuple[int, ...]" = ()
) -> "tuple[str, ...]":
    """Every base text the six styles of G6.1 can write for one value.

    THE FAMILY, WRITTEN OUT FROM THE METHOD (G6.1's table, G6.3's five
    alternates, G6.2's canonical). `plain` writes the point-free
    spelling; `decimal` writes the figures in fixed point; the two
    exponent styles write them in exponent notation with their own case;
    and the canonical spelling stands in wherever a style has nothing
    else to write -- which is what `leading_plus` falls back to for a
    value with no point-free spelling, so the `+` is offered in front of
    EVERY base a non-negative value has and not only in front of the
    point-free one. The LEADING-ZERO FAMILY is not here: it is zeros
    written straight after the sign of any of these, at any order, and
    `_wears` below is what admits it, because its order has no ceiling
    and a set of texts could not hold it.

    THE FAMILY IS GENEROUS ON PURPOSE where the method leaves a choice.
    A text this holds that no style would actually have chosen costs a
    MISS the aggregate style counts make anyway; a text this omits costs
    a MISSED verdict against a conforming twin, which is the direction
    nothing may drift in.
    `test_the_spelling_family_accepts_every_spelling_the_generator_writes`
    holds the two writings of G6.3 to agreeing over every style, every
    leading-zero order and the values that pin G6.2's own boundaries.

    Guarantees:

    - Inputs: one finite binary64 and whether the column publishes that
      every value is a whole number. No measured text.
    - Determinism: a fixed function of those two.
    - Errors raised: none.
    - Boundary: every text returned is computed from the NUMBER, so
      nothing a file spells can travel out through here.
    """
    canonical = _canonical_text(value, whole_column)
    sign, figures, place = _figures_of(value)
    spellings = [
        canonical,
        _fixed_text(sign, figures, place),
        _exponent_text(sign, figures, place, "e"),
        _exponent_text(sign, figures, place, "E"),
    ]
    plain = _point_free_text(value, canonical)
    if plain is not None:
        spellings = spellings + [plain]
    # ...AND THE FIXED-POINT FORM AT EVERY WIDTH THIS COLUMN'S OWN
    # CENSUS NAMES, and at no other. A trailing zero is not free: the
    # whole point of this subcheck is the twin whose every decimal cell
    # carried one, which met every count and validated with exit 0. What
    # the census changes is that a width is now a PUBLISHED fact, so a
    # cell wearing a named width wears something the description asked
    # for, and its count is checked on its own line. A width the census
    # does not name authorizes nothing here.
    #
    # Only the PADDING direction is offered, and that is not a
    # narrowing: the text is read off the file, the value is what that
    # text reads back as, and a text already written to a width needs
    # no rounding to be written to that same width again.
    for width in widths:
        padded = _text_at_width(sign, figures, place, width)
        if padded is not None:
            spellings = spellings + [padded]
    plussed: list[str] = []
    for spelling in spellings:
        if spelling[:1] != "-":
            plussed = plussed + [f"+{spelling}"]
    return tuple(spellings + plussed)


def _text_at_width(
    sign: str, figures: str, place: int, width: int
) -> "str | None":
    """The fixed-point spelling padded to one width, or None.

    None where the value needs MORE figures after the point than the
    width holds: such a cell is not this value written at this width,
    and offering the rounded text instead would admit a spelling of a
    value the file does not hold.
    """
    text = _fixed_text(sign, figures, place)
    point = -1
    for index in range(len(text)):
        if text[index] == ".":
            point = index
    if point < 0:
        return None
    held = len(text) - point - 1
    if width == 0:
        for character in text[point + 1 :]:
            if character != "0":
                return None
        return text[: point + 1]
    if held > width:
        return None
    return text + ("0" * (width - held))


def _wears(text: str, spelling: str) -> bool:
    """Whether one cell's text is one base spelling, at any zero order.

    Owner decision 8's invention family is `order` zeros written
    straight after the sign, and it is available inside every style but
    `plain` -- where a zero in front of a plain spelling is exactly what
    makes the cell `leading_zero`, so the same test covers both. The
    order has no ceiling, so this strips rather than enumerates: the
    sign, then any run of zeros, then the base spelling's own body,
    ending exactly where the text ends.
    """
    lead = ""
    body = spelling
    if spelling[:1] == "-" or spelling[:1] == "+":
        lead = spelling[:1]
        body = spelling[1:]
    if text[: len(lead)] != lead:
        return False
    rest = text[len(lead) :]
    if len(rest) < len(body):
        return False
    cut = len(rest) - len(body)
    if rest[cut:] != body:
        return False
    for character in rest[:cut]:
        if character != "0":
            return False
    return True


def _shown_count_or_none(found: "int | None") -> "str | None":
    """One measured count as the report shows it, or nothing at all.

    None where the file's own description does not carry the key,
    which is the disclosure gate closing: `_exact` then reports
    WITHHELD in the gate's own words, and the role axis of the same
    column carries the MISS that says why.
    """
    if found is None:
        return None
    return _shown_count(found)


def _published_widths(
    facts: contract.NumericFacts,
) -> "tuple[int, ...]":
    """The fraction widths this column's own census names, ascending.

    The pooled remainder is not one of them: it names no width, so it
    authorizes no spelling, and its cells are held to the spelling of
    their own value exactly as every cell was before the census
    existed.
    """
    named: list[int] = []
    for key in sorted(facts.fraction_widths):
        if key == taxonomy.SUPPRESSED_LABEL:
            continue
        named = named + [int(key)]
    return tuple(sorted(named))


def _cells_outside_the_styles(
    cells: "list[str]", whole_column: bool, widths: "tuple[int, ...]"
) -> int:
    """How many written cells are in no permitted spelling of their value.

    REVIEW ITEM P3-V2-C-F1. G6.1 says a numeric cell is written in
    exactly one of six styles "and in no other form", and G6.3 fixes
    what each of the six writes for a value. This is that sentence,
    counted per cell from the value alone: the text is read off the
    file, the texts it is compared against are computed from the number
    that text reads back as, and nothing between them is a generator's
    bookkeeping.

    A cell that does not read back as a number this format holds is not
    counted here. What it IS -- unreadable, out of range, contradictory
    -- is its own published count and its own subcheck; asking this
    question of it as well would report one fault twice.
    """
    outside = 0
    for cell in cells:
        body = parsing.trimmed(cell)
        if not body:
            continue
        if parsing.classify_number(body) != parsing.NUMBER:
            continue
        value = parsing.parse_number(body)
        if value is None:
            continue
        worn = False
        for spelling in _permitted_spellings(value, whole_column, widths):
            if _wears(body, spelling):
                worn = True
        if not worn:
            outside = outside + 1
    return outside


def _floor_governed(
    name: str,
    fact: str,
    subcheck: str,
    published: int,
    measured: "dict[str, int] | None",
    key: str,
    floor: int,
    pooled: int = 0,
) -> Check:
    """One named count, printed exactly only when it clears the floor.

    Where the file's own description omits the key, that omission
    already publishes exactly one thing: the identity covers fewer rows
    than the floor in this file, and possibly none. So the line says
    that and no more, the exact sub-floor number never appears beside
    the name, and the MISSED verdict follows from the two statements
    already made -- published at or above the floor, measured below it.

    ``pooled`` IS HOW MANY CELLS THE DESCRIPTION NAMES NO IDENTITY FOR
    at all -- the count under its own withheld key -- and where there
    are any, the bar is a window and not a point (review item P3-V7-F2's
    battery). A pooled cell has no published identity, so a file may
    give it this one: the count owed is at least the published number
    and at most that number plus the pool. The exact comparison refused
    the shipped generator's own twin on every description whose style
    map the floor had pooled -- eleven plain cells published, forty-five
    written, and MISSED against the product's own output.
    """
    if measured is None:
        return Check(
            name, fact, subcheck, WITHHELD, _shown_count(published), "", _GATE_CLOSED
        )
    if key in measured and pooled > 0:
        found = measured[key]
        inside = published <= found <= published + pooled
        return Check(
            name,
            fact,
            subcheck,
            HELD if inside else MISSED,
            f"{_shown_count(published)} "
            f"({_shown_window(float(published), float(published + pooled))})",
            _shown_count(found),
        )
    if key in measured:
        return _exact(
            name, fact, subcheck, _shown_count(published), _shown_count(measured[key])
        )
    return Check(
        name,
        fact,
        subcheck,
        MISSED,
        _shown_count(published),
        _below_the_floor(floor),
    )


# -- the label roles --------------------------------------------------


def _label_checks(
    column: contract.ColumnBlock,
    facts: contract.LabelFacts,
    block: "dict[str, object]",
    floor: int,
) -> "list[Check]":
    """A constant, binary or categorical column, level by level."""
    name = column.name
    measured = _levels_at(block)
    checks: list[Check] = []
    published_keys: list[str] = []
    for level in facts.levels:
        key = parsing.folded(parsing.trimmed(level.label))
        published_keys = published_keys + [key]
        entry = (
            measured[key] if measured is not None and key in measured else None
        )
        checks = checks + [
            _level_spelling(name, level, entry, measured),
            _level_count(name, level, entry, measured, floor),
            _variant_map(name, level, entry, measured, "variants"),
            _variant_map(name, level, entry, measured, "variants_withheld"),
        ]
    checks = checks + [_level_set(name, published_keys, measured)]
    for field, published in (
        ("suppressed_levels", facts.suppressed_levels),
        ("suppressed_rows", facts.suppressed_rows),
    ):
        found = _count_at(block, field)
        checks = checks + [
            _exact(
                name,
                f"label.{field}",
                f"suppressed.{field}",
                _shown_count(published),
                None if found is None else _shown_count(found),
            )
        ]
    counts = _counts_at(block, "suppressed_level_counts")
    held_back = len(facts.suppressed_level_counts)
    asked = (
        "no label of this column is held back, so there is no row count "
        "of one to carry"
    )
    if held_back:
        asked = (
            f"the rows covered by each of the {_shown_count(held_back)} "
            f"label(s) this description holds back"
        )
    checks = checks + [
        _silent(
            name,
            "label.suppressed_level_counts",
            "suppressed.counts",
            asked,
            None if counts is None else counts == list(
                facts.suppressed_level_counts
            ),
            _NOT_SHOWN_IT_IS_A_COUNT_OF_THE_FILE,
        )
    ]
    return checks


def _level_spelling(
    name: str,
    level: contract.LevelEntry,
    entry: "dict[str, object] | None",
    measured: "dict[str, dict[str, object]] | None",
) -> Check:
    """That the file holds cells that fold to this published label.

    `label.label` is EXACT-OBSERVABLE and is its own obligation: a twin
    that wrote the right NUMBER of cells for this level under a spelling
    that folds to something else has met the count and not the label.
    The measured spelling is never shown -- what the line names is the
    description's own published label.

    AND WHAT IT ASKS FOR IS SAID IN WORDS (review of the shipped
    reports, 2026-08-15). This obligation is not a number, and it
    printed as one: "levels.east.label: HELD -- the description asks
    for: 1", with no found line under it, because the one was a
    placeholder standing where a count goes. Withholding the found
    value is the disclosure rule and stays; printing `1` as what a
    LABEL obligation asks for tells a reader nothing they can check.
    """
    fact = "label.label"
    subcheck = f"levels.{level.label}.label"
    shown = "cells of this file that read as this label"
    if measured is None:
        return Check(name, fact, subcheck, WITHHELD, shown, "", _GATE_CLOSED)
    return _silent(
        name,
        fact,
        subcheck,
        shown,
        entry is not None,
        _NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE,
    )


def _level_set(
    name: str,
    published: "list[str]",
    measured: "dict[str, dict[str, object]] | None",
) -> Check:
    """That the file's own description publishes these levels and no more.

    `label.levels` states the SET, which no per-level check states: a
    file holding every published label and one more meets every level's
    own count and still carries content the description does not
    publish. What the line says is how many levels the description
    publishes; the extra one is never named, because naming it would
    print a string out of the measured file.
    """
    fact = "label.levels"
    subcheck = "levels.set"
    shown = (
        f"the {_shown_count(len(published))} published label(s) of this "
        f"column, and no label the description does not publish"
    )
    if measured is None:
        return Check(name, fact, subcheck, WITHHELD, shown, "", _GATE_CLOSED)
    same = len(measured) == len(published)
    for key in published:
        if key not in measured:
            same = False
    return _silent(name, fact, subcheck, shown, same, _NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE)


def _counts_at(
    block: "dict[str, object]", key: str
) -> "list[int] | None":
    """One list of whole numbers out of a re-described block, or None."""
    if key not in block:
        return None
    value = block[key]
    if not isinstance(value, list):
        return None
    found: list[int] = []
    for entry in value:
        if isinstance(entry, bool):
            return None
        if not isinstance(entry, int):
            return None
        found = found + [entry]
    return found


def _level_count(
    name: str,
    level: contract.LevelEntry,
    entry: "dict[str, object] | None",
    measured: "dict[str, dict[str, object]] | None",
    floor: int,
) -> Check:
    """How many rows one published label covers."""
    fact = "label.count"
    subcheck = f"levels.{level.label}.count"
    if measured is None:
        return Check(
            name, fact, subcheck, WITHHELD, _shown_count(level.count), "", _GATE_CLOSED
        )
    if entry is None:
        return Check(
            name,
            fact,
            subcheck,
            MISSED,
            _shown_count(level.count),
            _below_the_floor(floor),
        )
    found = _count_at(entry, "count")
    return _exact(
        name,
        fact,
        subcheck,
        _shown_count(level.count),
        None if found is None else _shown_count(found),
    )


def _variant_map(
    name: str,
    level: contract.LevelEntry,
    entry: "dict[str, object] | None",
    measured: "dict[str, dict[str, object]] | None",
    field: str,
) -> Check:
    """One level's spelling map, compared whole.

    The map's KEYS are spellings; a difference is reported as a verdict
    and never by naming a spelling the measured file holds. What the
    line names is the description's own label.

    A LEVEL THE FILE DOES NOT CARRY MISSES THIS, it does not withhold it
    (review item P3-V2-A1). Where the file's own description publishes
    levels but not this one, the file holds fewer rows of it than the
    floor and possibly none -- so it cannot be holding the published
    spellings of it either, and the verdict follows from what
    `levels.<label>.count` has already said out loud on the line above.
    Withholding it instead would have been silence bought by dropping a
    published label altogether, and it sat oddly beside
    `_level_spelling`, which has always MISSED on exactly this case.

    WHAT IT ASKS FOR IS A COUNT OF SPELLINGS, AND SAYS SO (review of
    the shipped reports, 2026-08-15). The bare number printed under a
    line named `levels.east.variants` reads as a count of rows, of
    labels, or of anything else the reader supplies; nothing on the
    page said the map was a map of spellings. The count is the same
    count -- how many entries the description's map holds -- with the
    noun it counts written beside it.
    """
    published = (
        level.variants if field == "variants" else level.variants_withheld
    )
    fact = f"label.{field}"
    subcheck = f"levels.{level.label}.{field}"
    kept_back: tuple[str, ...] = _NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE
    if field == "variants":
        shown = (
            f"{_shown_count(len(published))} published spelling(s) of "
            f"this label, and the rows each covers"
        )
    else:
        kept_back = _NOT_SHOWN_IT_IS_A_COUNT_OF_THE_FILE
        # The keys of `variants_withheld` are GROUP SIZES and its values
        # are how many spellings wore each, so the number of entries is
        # not the number of spellings and must not be printed as one.
        spellings = 0
        for key in published:
            spellings = spellings + published[key]
        shown = (
            f"{_shown_count(spellings)} spelling(s) of this label held "
            f"back as too rare to name, and the rows each covers"
        )
        if not spellings:
            shown = "no spelling of this label held back as too rare to name"
    if measured is None:
        return Check(name, fact, subcheck, WITHHELD, shown, "", _GATE_CLOSED)
    if entry is None:
        return _silent(name, fact, subcheck, shown, False, kept_back)
    found = _map_at(entry, field)
    if found is None:
        return Check(name, fact, subcheck, WITHHELD, shown, "", _GATE_CLOSED)
    return _silent(name, fact, subcheck, shown, found == published, kept_back)


# -- the datetime role ------------------------------------------------


def _clock_checks(
    column: contract.ColumnBlock,
    facts: contract.ClockFacts,
    block: "dict[str, object]",
) -> "list[Check]":
    """A column of clock times.

    THE THREE KINDS OF OBLIGATION THIS ROLE CARRIES. The form and the
    unparsed count are exact and are COUNTS or words of this package's
    own, so both sides print. The two endpoints and the ladder's two
    ends are exact too, but their measured side is TEXT READ OUT OF THE
    FILE, so the comparison is made in full and only the verdict is
    shown -- the same treatment the datetime role's endpoints get, and
    for the same rule. The nine interior rungs are approximated inside
    the window this role's own construction leaves them.
    """
    name = column.name
    checks: "list[Check]" = []
    found = _text_at(block, "clock_form")
    checks = checks + [
        _exact(
            name,
            "clock.clock_form",
            "form.clock_form",
            facts.clock_form,
            found,
        )
    ]
    for field, published in (
        ("earliest", facts.earliest),
        ("latest", facts.latest),
    ):
        seen = _text_at(block, field)
        checks = checks + [
            _silent(
                name,
                f"clock.{field}",
                f"ends.{field}",
                published,
                None if seen is None else seen == published,
                _NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE,
            )
        ]
    counted = _count_at(block, "n_unparsed")
    checks = checks + [
        _exact(
            name,
            "clock.n_unparsed",
            "counts.n_unparsed",
            _shown_count(facts.n_unparsed),
            None if counted is None else _shown_count(counted),
        )
    ]
    checks = checks + _clock_ladder_checks(column, facts, block)
    return checks


def _clock_ladder_checks(
    column: contract.ColumnBlock,
    facts: contract.ClockFacts,
    block: "dict[str, object]",
) -> "list[Check]":
    """The clock ladder: the two ends exact, the nine interior windowed.

    The window is this role's own construction written out here rather
    than imported: the validator may not read the generator, so the
    arithmetic is taken from the method's clause and the suite holds the
    two writings to agreeing.

    Rank `k` is its own stratum -- its share of the day runs from `k/P`
    to `(k+1)/P` and no word can carry it outside that band -- so the
    rank sits between the ladder read at those two shares, less one unit
    of the form at the low end for the flooring. The two ends are PINNED
    and have no room at all: the construction writes rank 0 at the
    published earliest and rank `P-1` at the published latest, and T2
    makes those the ladder's own two ends.
    """
    name = column.name
    measured = _inner_at(block, "clock_percentiles")
    form = facts.clock_form
    checks: "list[Check]" = []
    for key, expected in (
        ("min", facts.earliest),
        ("max", facts.latest),
    ):
        seen = None if measured is None else _text_at(measured, key)
        checks = checks + [
            _silent(
                name,
                f"clock.clock_percentiles.{key}",
                f"clock-ladder.{key}",
                expected,
                None if seen is None else seen == expected,
                _NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE,
            )
        ]
    parsed = max(1, column.n_present - facts.n_unparsed)
    lows, highs = _clock_rank_windows(facts, parsed)
    for index in range(1, len(_LADDER_KEYS) - 1):
        key = _LADDER_KEYS[index]
        seen = None if measured is None else _text_at(measured, key)
        # READ IN THE FILE'S OWN FORM AND COMPARED IN ONE UNIT. A file
        # whose cells wear the other shape publishes a ladder in that
        # shape, and reading it under the DESCRIPTION's form finds
        # nothing -- so every rung went silent, on a file whose own
        # description publishes exactly the measurement being asked
        # for. That is not the disclosure gate closing; it is the
        # validator unable to read, which V5.3 does not permit as a
        # reason for silence. Both sides are read in their own form and
        # compared in seconds of day, where a minute is sixty and the
        # two spaces are one.
        held = None if seen is None else _clock_seconds(seen, block)
        rank = _rung_rank(_LADDER_PERCENTS[index], parsed)
        checks = checks + [
            _within_clock(
                name,
                f"clock-ladder.{key}",
                facts,
                facts.clock_percentiles[key],
                held,
                (lows[rank], highs[rank]),
            )
        ]
    return checks


def _clock_seconds(text: str, block: "dict[str, object]") -> "int | None":
    """One measured clock value in SECONDS of day, read in its own form.

    The file's own description says which form its cells wore, and that
    is the form its ladder is written in. Reading it under somebody
    else's form is reading it wrongly, and answering "cannot tell" is
    worse than answering wrongly: it makes the check silent on a file
    whose own description publishes the very value being compared.
    """
    found = _text_at(block, "clock_form")
    if found is None:
        return None
    ordinal = parsing.clock_ordinal(text, found)
    if ordinal is None:
        return None
    if found == contract.CLOCK_FORMS[0]:
        return ordinal * 60
    return ordinal


def _clock_units(form: str) -> str:
    """The word for one step of this form's own ordinal space."""
    if form == contract.CLOCK_FORMS[0]:
        return "minute"
    return "second"


def _shown_clock_distance(ordinal: int, rung: int, form: str) -> str:
    """One clock ordinal said as its distance from the published rung.

    A DISTANCE AND NOT A TIME, for the reason the datetime rungs are
    said that way: the measured side is a value read out of the file,
    and no text of a measured file is printed in this report. A
    distance is arithmetic on two numbers the reader already has -- the
    published rung is on the line above -- and carries no spelling of
    anybody's table.
    """
    # The two numbers arrive in seconds; a column of minutes says its
    # distance in minutes, which is what its reader has in front of
    # them. An odd number of seconds on such a column is a file that
    # wore the other form, and it is said in seconds rather than
    # rounded into a lie.
    away = ordinal - rung
    word = _clock_units(form)
    if form == contract.CLOCK_FORMS[0]:
        if away % 60 == 0:
            away = away // 60
        else:
            word = "second"
    if away == 0:
        return "that same time"
    if away < 0:
        return f"{-away} {word}(s) before that"
    return f"{away} {word}(s) after that"


def _within_clock(
    column: str,
    subcheck: str,
    facts: contract.ClockFacts,
    published: str,
    measured: "int | None",
    window: "tuple[int, int]",
) -> Check:
    """One interior rung of a clock ladder, against its own window.

    The same shape the datetime rungs take: the exact reading is tried
    first, so a file holding the published rung is HELD whatever the
    window says; the three numbers are said as distances from that
    rung; and a window that does not reach the published value says so
    rather than leaving a reader to think the page is wrong.
    """
    # IN SECONDS OF DAY, the one unit the two forms share, because the
    # measured side was read in the FILE's own form and this one is
    # read in the description's.
    step = 60 if facts.clock_form == contract.CLOCK_FORMS[0] else 1
    rung = step * _clock_ordinal_or_zero(published, facts.clock_form)
    low, high = window
    form = facts.clock_form
    allowed = (
        f"      this rung of the file is allowed from "
        f"{_shown_clock_distance(low, rung, form)}"
    )
    note: "tuple[str, ...]" = (
        allowed,
        (
            f"        to {_shown_clock_distance(high, rung, form)}, and "
            f"it covers the value above"
        ),
    )
    reaches = low <= rung <= high
    if not reaches:
        note = (
            allowed,
            (
                f"        to {_shown_clock_distance(high, rung, form)}, "
                f"and it does NOT reach the"
            ),
            "        value above. This window is what the method allows",
            "        the file's own rung, worked out from the description",
            "        and the size of this column; it is not a margin",
            "        around the description's value.",
        )
    if measured is None:
        return Check(
            column,
            "clock.clock_percentiles",
            subcheck,
            WITHHELD,
            published,
            "",
            _GATE_CLOSED,
        )
    if measured == rung:
        return Check(
            column,
            "clock.clock_percentiles",
            subcheck,
            HELD,
            published,
            _shown_clock_distance(measured, rung, form),
            "",
            () if reaches else _MET_OUTSIDE_ITS_WINDOW,
        )
    verdict = WITHIN_BOUND if low <= measured <= high else MISSED
    return Check(
        column,
        "clock.clock_percentiles",
        subcheck,
        verdict,
        published,
        _shown_clock_distance(measured, rung, form),
        ENVELOPE_CLOCK_RUNG,
        note,
    )


def _clock_rank_windows(
    facts: contract.ClockFacts, parsed: int
) -> "tuple[list[int], list[int]]":
    """The window every rank of a column of clock times sits in.

    Whole-number arithmetic throughout, in the ordinal unit the
    published FORM sets -- minutes of day, or seconds of day -- because
    that is the unit the construction interpolates in and a window drawn
    in another one would floor to a different place.

    Guarantees: accepts one column's published clock facts and how many
    of its cells read back as clock times; returns the two ends of every
    rank's window. Nothing measured is consulted -- this is what the
    DESCRIPTION obliges. Determinism: a fixed function of those two.
    Errors raised: none.
    """
    ladder = [
        _clock_ordinal_or_zero(facts.clock_percentiles[name], facts.clock_form)
        for name in _LADDER_KEYS
    ]
    last = len(_LADDER_KEYS) - 1
    # THE WINDOWS ARE DRAWN IN THE FORM'S OWN UNIT AND HANDED BACK IN
    # SECONDS, because the measured side is read in the FILE's form and
    # the two have to meet in one space. The interpolation itself must
    # happen in the column's own unit -- it floors, and flooring in
    # seconds lands part way through a minute the construction cannot
    # write -- so the conversion is the last step and never the first.
    step = 60 if facts.clock_form == contract.CLOCK_FORMS[0] else 1
    lows: "list[int]" = []
    highs: "list[int]" = []
    for rank in range(parsed):
        if rank == 0:
            lows = lows + [step * ladder[0]]
            highs = highs + [step * ladder[0]]
            continue
        if rank == parsed - 1 and parsed >= 2:
            lows = lows + [step * ladder[last]]
            highs = highs + [step * ladder[last]]
            continue
        lows = lows + [
            step * _ladder_ordinal_at(ladder, rank, parsed) - step
        ]
        highs = highs + [step * _ladder_ordinal_at(ladder, rank + 1, parsed)]
    return (lows, highs)


def _clock_ordinal_or_zero(text: str, form: str) -> int:
    """One published clock value as its ordinal, or zero.

    The loader has held every published clock value to the column's own
    form (T1), so the reader answers for every value that reaches here.
    Zero is what a value it cannot read would give, and it is a value
    inside the space rather than an exception, because a window is a
    statement about the description and a description that got this far
    has already been refused if it could not be read.
    """
    found = parsing.clock_ordinal(text, form)
    if found is None:
        return 0
    return found


def _datetime_checks(
    column: contract.ColumnBlock,
    facts: contract.DatetimeFacts,
    block: "dict[str, object]",
    floor: int,
    mine: "tuple[str, ...]",
) -> "list[Check]":
    """A column of dates and times."""
    name = column.name
    checks: list[Check] = []
    for field, published in (
        ("earliest", facts.earliest),
        ("latest", facts.latest),
    ):
        found = _text_at(block, field)
        checks = checks + [
            _silent(
                name,
                f"datetime.{field}",
                f"ends.{field}",
                published,
                None if found is None else found == published,
                _NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE,
            )
        ]
    for field, published in (
        ("resolution", facts.resolution),
        ("time_precision", facts.time_precision),
    ):
        found = _text_at(block, field)
        checks = checks + [
            _exact(name, f"datetime.{field}", f"precision.{field}", published, found)
        ]
    for field, counted in (
        ("subsecond_digits", facts.subsecond_digits),
        ("n_unparsed", facts.n_unparsed),
    ):
        seen = _count_at(block, field)
        checks = checks + [
            _exact(
                name,
                f"datetime.{field}",
                f"counts.{field}",
                _shown_count(counted),
                None if seen is None else _shown_count(seen),
            )
        ]
    checks = checks + _offset_checks(column, facts, block, floor, mine)
    checks = checks + _date_ladder_checks(column, facts, block)
    return checks


def _offset_checks(
    column: contract.ColumnBlock,
    facts: contract.DatetimeFacts,
    block: "dict[str, object]",
    floor: int,
    mine: "tuple[str, ...]",
) -> "list[Check]":
    """The offset map, the two endpoint offsets, and how they were read."""
    name = column.name
    corner = CORNER_DATETIME_OFFSETS_WITHHELD
    if corner in mine:
        # REPORT-ONLY, so no verdict at all (V4.1, V6.1; review item
        # P3-V1-F4). The four obligations are named in the census by
        # `_corner_listings`, with the passage that authorizes the
        # lesser outcome; returning them as AUTHORIZED-DEVIATION checks
        # counted four unmeasurable facts as facts this file had been
        # checked against.
        return []
    measured = _map_at(block, "utc_offsets")
    checks: list[Check] = []
    for key in sorted(facts.utc_offsets):
        if key == taxonomy.SUPPRESSED_LABEL:
            continue
        checks = checks + [
            _floor_governed(
                name,
                "datetime.utc_offsets",
                f"offsets.{key}",
                facts.utc_offsets[key],
                measured,
                key,
                floor,
            )
        ]
    for field, published, subcheck in (
        ("earliest_utc_offset", facts.earliest_utc_offset, "offsets.earliest"),
        ("latest_utc_offset", facts.latest_utc_offset, "offsets.latest"),
    ):
        if published == taxonomy.SUPPRESSED_LABEL:
            # THE ENDPOINT ITSELF IS WITHHELD, so the description names
            # no offset for this end at all and there is nothing for a
            # file to carry. `_endpoint_listings` files it in the
            # not-checkable census; checking it compared a file's own
            # floor against the source's, which is a fact about how many
            # rows shared an offset and not about the file's dates, and
            # reported MISSED against the shipped generator's own twin
            # (review item P3-V7-F2's battery).
            continue
        found = _text_at(block, field)
        checks = checks + [
            _silent(
                name,
                f"datetime.{field}",
                subcheck,
                published,
                None if found is None else found == published,
                _NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE,
            )
        ]
    read_at = _text_at(block, "datetimes_read_at")
    checks = checks + [
        _exact(
            name,
            "datetime.datetimes_read_at",
            "offsets.read-at",
            facts.datetimes_read_at,
            read_at,
        )
    ]
    return checks


def _date_ladder_checks(
    column: contract.ColumnBlock,
    facts: contract.DatetimeFacts,
    block: "dict[str, object]",
) -> "list[Check]":
    """The date ladder: the two ends exact, the nine interior in windows.

    The window is method G12.4's, taken in the ordinal space method
    G7.1 fixes for the resolution this column publishes (`_instant_of`)
    and drawn by `_rank_windows` below, which is the method's own
    construction written out. The rung a description publishes is
    SELECTED, not interpolated -- there is no half-way point between two
    dates a calendar recognises -- so the rung is read off ONE RANK, the
    rank G12.4 names, and the window is that rank's own.

    EVERY RESOLUTION, INCLUDING QUARTERS (review item P3-V3-F4). These
    nine rungs used to be WITHHELD one by one on any column of quarters,
    because the space was `parsing.instant_key`'s alone and a quarter
    names no instant in it. The method defines a quarter's ordinal and
    applies this bound to quarters in as many words, so the obligation
    was there and only the measurement was missing: a file holding three
    of the twelve published quarters passed with these nine and both
    distinctness counts silenced. There is no branch here that a
    resolution can silence any more.

    AND THE RANK IS THE METHOD'S, IN WHOLE NUMBERS (review item
    P3-V4-F4). The version this replaces worked the rank out as
    `((P - 1) * share * 100) // 100` over a floating-point share and
    then read the ladder through the float reader the numeric ladder
    uses, neither of which is the arithmetic G12.4 fixes. `_rung_rank`
    and `_ladder_ordinal_at` are that arithmetic, and the suite compares
    them with the generator's own writing of it at every resolution.
    """
    name = column.name
    measured = _inner_at(block, "date_percentiles")
    published = facts.date_percentiles
    checks: list[Check] = []
    for key, expected in (("min", published.minimum), ("max", published.maximum)):
        found = None if measured is None else _text_at(measured, key)
        checks = checks + [
            _silent(
                name,
                f"datetime.date_percentiles.{key}",
                f"date-ladder.{key}",
                expected,
                None if found is None else found == expected,
                _NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE,
            )
        ]
    dated = max(1, column.n_present - facts.n_unparsed)
    lows, highs = _rank_windows(facts, dated)
    for index in range(1, len(_LADDER_KEYS) - 1):
        key = _LADDER_KEYS[index]
        found = None if measured is None else _text_at(measured, key)
        seen = None if found is None else _instant_of(found, facts.resolution)
        rank = _rung_rank(_LADDER_PERCENTS[index], dated)
        checks = checks + [
            _within_instant(
                name,
                f"date-ladder.{key}",
                facts,
                published.rungs[index],
                seen,
                (lows[rank], highs[rank]),
            )
        ]
    return checks


# -- one rung of a date ladder, written for a person -------------------

_INSTANT_UNITS = {
    taxonomy.RESOLUTION_QUARTER: "quarter",
    taxonomy.RESOLUTION_MONTH: "month",
    taxonomy.RESOLUTION_DATE: "day",
    taxonomy.RESOLUTION_DATETIME: "second",
}


def _instant_units(facts: contract.DatetimeFacts) -> str:
    """The word for one unit of this column's own ordinal space."""
    if facts.resolution in _INSTANT_UNITS:
        return _INSTANT_UNITS[facts.resolution]
    return "unit"


def _shown_distance(
    ordinal: int, rung: int, facts: contract.DatetimeFacts
) -> str:
    """One instant said as its distance from the published rung.

    WHY A DISTANCE AND NOT AN INSTANT (review of the shipped reports,
    2026-08-15). These four numbers -- the measured rung and the two
    ends of its window -- used to print as the raw ordinals the
    arithmetic runs in, so an ordinary quality report told a researcher
    their column's ninetieth rung was "2023-11-23 (between 1700352000.0
    and 1700524800.0)" and was "found to hold 1700438400.0". Charter
    principle 2 asks every message to be written for a person, and three
    numbers of ten figures are not: nobody can see from them that the
    window sits four days below the value it is printed beside.

    Writing them as dates instead would mean a calendar in this module,
    and V1.4 keeps the validator's arithmetic to what the method fixes
    and the suite compares against the generator's own writing of it --
    a date formatter here would be new machinery with no reference
    vectors, in the one module whose whole value is being a second
    opinion. So each is said as a whole number of the resolution's own
    units away from the description's published rung, which the reader
    already has in front of them: one subtraction and one exact
    division, in the space `_space_unit` fixes, where every window end
    and every canonical instant is a whole multiple.
    """
    step = _space_unit(facts)
    away = (ordinal - rung) // step
    word = _instant_units(facts)
    if away == 0:
        return "that same value"
    if away < 0:
        return f"{-away} {word}(s) before that"
    return f"{away} {word}(s) after that"


def _within_instant(
    column: str,
    subcheck: str,
    facts: contract.DatetimeFacts,
    published: str,
    measured: "int | None",
    window: "tuple[int, int]",
) -> Check:
    """One interior rung of a date ladder, against G12.4's window.

    The verdict is the same comparison `_within` makes; what differs is
    that all three numbers are said as distances from the published
    rung, and that a window which does not cover the published rung says
    so. G12.4's window is the band the twin's own RANK was built in, and
    the rank holding a named rung covers a slightly different share of
    the column from the share that rung's name names -- so at the top of
    an ordinary ladder the window sits wholly below the published value.
    That is the method working, and a page that shows it without saying
    it reads as a page that is wrong.

    AND THE RUNG THE FILE HOLDS EXACTLY IS HELD (review item P3-V10-F5;
    plan amendment A-P3-40, validation method clause V6.1-A1). The
    verdict was window membership and nothing else, so the shipped
    source table -- checked against its own description -- printed "the
    description asks for: 2024-12-24 / the file was found to hold: that
    same value" and MISSED under it, because G12.4's window for that
    rung ends a day earlier. Four rungs of that one table said it. A
    file holding the published value cannot be missing the obligation to
    hold it, so the exact reading is taken first here exactly as
    `_within` takes it, and what the window has to say is said in the
    note rather than in the verdict.
    """
    rung = _ordinal_of(published, facts.resolution)
    low, high = window
    allowed = (
        f"      this rung of the file is allowed from "
        f"{_shown_distance(low, rung, facts)}"
    )
    note: tuple[str, ...] = (
        allowed,
        (
            f"        to {_shown_distance(high, rung, facts)}, and it "
            f"covers the value above"
        ),
    )
    reaches = low <= rung <= high
    if not reaches:
        note = (
            allowed,
            (
                f"        to {_shown_distance(high, rung, facts)}, and it "
                f"does NOT reach the"
            ),
            "        value above. This window is what the method allows",
            "        the file's own rung, worked out from the description",
            "        and the size of this column; it is not a margin",
            "        around the description's value.",
        )
    if measured is None:
        return Check(
            column,
            "datetime.date_percentiles",
            subcheck,
            WITHHELD,
            published,
            "",
            _GATE_CLOSED,
        )
    if measured == rung:
        return Check(
            column,
            "datetime.date_percentiles",
            subcheck,
            HELD,
            published,
            _shown_distance(measured, rung, facts),
            "",
            () if reaches else _MET_OUTSIDE_ITS_WINDOW,
        )
    verdict = WITHIN_BOUND if low <= measured <= high else MISSED
    return Check(
        column,
        "datetime.date_percentiles",
        subcheck,
        verdict,
        published,
        _shown_distance(measured, rung, facts),
        ENVELOPE_DATETIME_RUNGS,
        note,
    )


def _clock_distinct_window(
    column: contract.ColumnBlock, facts: contract.ClockFacts
) -> "tuple[float, float]":
    """How many different values a column of clock times may hold.

    The same two ends the date role's envelope has, in this role's own
    ordinal space. The LOWER end counts ranks whose windows do not
    overlap -- two ranks that cannot hold the same time are two
    identities the twin must carry -- plus every stand-in, each spelled
    differently from every other cell. The UPPER end is how many times
    the published range holds at all, plus those stand-ins, and never
    more cells than the column has.

    IT NEED NOT CONTAIN THE PUBLISHED COUNT, and on an ordinary column
    it does not: a column of two hundred and forty rows over a hundred
    and twenty different times publishes a hundred and twenty while the
    construction writes a value per rank. That is what an explicit
    cardinality bound is for, and it is why this role's two distinctness
    counts are approximated rather than exact.
    """
    parsed = max(1, column.n_present - facts.n_unparsed)
    lows, highs = _clock_rank_windows(facts, parsed)
    separate = _ranks_forced_apart(lows, highs)
    earliest = _clock_ordinal_or_zero(facts.earliest, facts.clock_form)
    latest = _clock_ordinal_or_zero(facts.latest, facts.clock_form)
    room = latest - earliest + 1
    upper = min(column.n_present, room + facts.n_unparsed)
    lower = min(separate + facts.n_unparsed, upper)
    return (float(lower), float(upper))


def _datetime_distinct_window(
    column: contract.ColumnBlock, facts: contract.DatetimeFacts
) -> "tuple[float, float]":
    """How many different values a column of dates may hold (G12.5).

    The LOWER end counts ranks whose windows of G12.4 do not overlap:
    two ranks that cannot hold the same instant are two identities the
    twin must carry, and every cell that did not read as a date is a
    counted stand-in spelled differently from every other. The UPPER
    end is how many instants the published range holds at the published
    precision, once per offset the description names by name, plus
    those same stand-ins, and never more cells than the column has.

    This envelope need not contain the published count, and on an
    ordinary column it does not: a column of 240 rows over 84 different
    dates publishes 84 while the construction writes a value per rank.
    That is what the matrix means by giving a column of dates its own
    explicit cardinality bound.

    IT IS DRAWN FOR EVERY RESOLUTION AND RETURNS NO "CANNOT SAY"
    (review item P3-V3-F4). It used to hand back nothing for a column of
    quarters, and both distinctness counts were then WITHHELD whatever
    the file held -- so a twelve-row file carrying three of twelve
    published quarters was told its distinctness could not be shown. The
    ordinal space below is the method's own for each resolution, so
    there is nothing left here for a resolution to silence.

    AND THE WINDOWS IT WALKS ARE G12.4'S, ENDS AND ALL (review item
    P3-V4-F4). The version this replaces drew every rank's window from
    the ladder alone, including the two the construction PINS -- so the
    first rank's window ran from the published earliest back by one unit
    and forward to the second rank's share, and swallowed ranks the
    construction cannot put on the same instant as rank zero. Measured
    on a twelve-rank quarterly description, the walk returned four
    separate ranks where the pinned construction forces six, and a file
    holding four different quarters was told it was inside the envelope.
    The walk itself is unchanged; it now walks the right windows, which
    is the whole of the repair.
    """
    dated = max(1, column.n_present - facts.n_unparsed)
    lows, highs = _rank_windows(facts, dated)
    separate = _ranks_forced_apart(lows, highs)
    step = _precision_step(facts)
    earliest = _ordinal_of(facts.earliest, facts.resolution)
    latest = _ordinal_of(facts.latest, facts.resolution)
    room = (latest - earliest) // step + 1
    upper = min(
        column.n_present,
        room * _spellings_of_an_instant(facts) + facts.n_unparsed,
    )
    lower = min(separate + facts.n_unparsed, upper)
    return (float(lower), float(upper))


def _spellings_of_an_instant(facts: contract.DatetimeFacts) -> int:
    """How many ways one instant can be written in this column (G7.4).

    One per offset the description names BY NAME, plus one for a cell
    that carries no offset at all -- and G7.4 gives two keys that route
    a cell there: `(none)`, which counts the cells that carried none,
    and `(withheld)`, which pools the offsets below the publication
    floor and is written with no offset as well, "and this is a loss,
    named as one". A column that names nothing gets one, because its
    cells are all written the same way.

    WHY THIS IS NOT `generation._spellings_of_a_date`, WHICH COUNTS THE
    NAMED OFFSETS ALONE. G12.5's sentence for the upper end says "M the
    number of named offsets", and its derivation says every cell is
    "spelled with one of the offsets `utc_offsets` names by name" --
    which G7.4 contradicts for exactly these two keys, since the cells
    they cover are written with no offset and are therefore a spelling
    of their own. Where a column mixes a named offset with either key,
    the literal count is one short of the ways its own twin writes an
    instant, and a bound one factor too tight is a bound a conforming
    twin can be reported MISSED against. This reading is the wider of
    the two on exactly those columns and identical on every other, so it
    can turn no verdict against a file; the tighter one is method
    G12.5's to fix, and this document may not narrow a cited envelope on
    its own (V3.5). The suite compares the two writings and pins where
    they may differ.
    """
    named = 0
    unnamed = 0
    for key in facts.utc_offsets:
        if key in (contract.NO_OFFSET, taxonomy.SUPPRESSED_LABEL):
            unnamed = 1
        else:
            named = named + 1
    return max(1, named + unnamed)


def _ranks_forced_apart(lows: "list[int]", highs: "list[int]") -> int:
    """How many different instants the published ladder FORCES (G12.5).

    Two ranks whose windows of G12.4 do not overlap cannot hold the same
    instant, so the largest set of ranks with pairwise separate windows
    is a lower bound on how many different values the twin holds. The
    windows arrive in non-decreasing order of both ends, so the count is
    taken in one walk: keep the first rank, then keep each later rank
    whose lower end is strictly above the last kept rank's upper end.
    """
    count = 0
    frontier = 0
    for rank in range(len(lows)):
        if count == 0 or lows[rank] > frontier:
            count = count + 1
            frontier = highs[rank]
    return count


def _rank_windows(
    facts: contract.DatetimeFacts, dated: int
) -> "tuple[list[int], list[int]]":
    """The window every rank of a column of dates sits in (method G12.4).

    THE CONSTRUCTION, WRITTEN FROM THE METHOD AND NOT IMPORTED (V1.4,
    V4.2; review items P3-V4-F4 and P3-V4-F5). Rank `k` of G7.3 is its
    own stratum: its share of the distribution is the band from `k / P`
    to `(k + 1) / P` and no word can take it outside that band, so

        Ladder(k / P) - u   <=   O[k]   <=   Ladder((k + 1) / P)

    with `Ladder` read by the SAME whole-number interpolation G7.3
    builds cells with (`_ladder_ordinal_at`) and `u` the reading unit
    below. **The two ends are PINNED**: G7.3 writes rank `0` at the
    published `earliest` and rank `P - 1` at the published `latest`,
    exactly as published, so those two ranks have no room at all. The
    profile contract's D11 makes those two instants the ladder's own two
    ends, which is why they are read off the ladder here.

    Leaving the pinning out was review item P3-V4-F4: the first and last
    ranks got the interior band, the separateness walk of G12.5 then let
    the first window swallow ranks that cannot share its instant, and a
    file with four different quarters passed a bound the construction
    puts at six.

    Guarantees:

    - Inputs: one column's published datetime facts, and how many of its
      cells read back as a date. Nothing measured is consulted: this is
      what the DESCRIPTION obliges, and the caller compares the file
      with it.
    - Determinism: a fixed function of those two, in whole-number
      arithmetic throughout -- no float is formed anywhere in it, as
      G7.1 requires of every step in this space.
    - Errors raised: TypeError through `_ordinal_of` where a published
      instant names no point in its own resolution's space, which is a
      contradiction between the strict loader and this reading rather
      than a fact about any file (V3.4-A1).
    """
    step = _space_unit(facts)
    ladder = _ladder_ordinals(facts)
    unit = _reading_unit(facts)
    last = len(_LADDER_KEYS) - 1
    lows: list[int] = []
    highs: list[int] = []
    for rank in range(dated):
        if rank == 0:
            lows = lows + [step * ladder[0]]
            highs = highs + [step * ladder[0]]
            continue
        if rank == dated - 1 and dated >= 2:
            lows = lows + [step * ladder[last]]
            highs = highs + [step * ladder[last]]
            continue
        lows = lows + [
            step * _ladder_ordinal_at(ladder, rank, dated) - unit
        ]
        highs = highs + [step * _ladder_ordinal_at(ladder, rank + 1, dated)]
    return (lows, highs)


def _ladder_ordinals(facts: contract.DatetimeFacts) -> "list[int]":
    """The eleven published rungs, in the unit the METHOD counts them in.

    AND THAT IS NOT ALWAYS THE UNIT THIS READING COUNTS IN, which is the
    third divergence of review item P3-V4-F4. `_instant_of` reads a
    whole date into the SECONDS its two neighbours already speak, and
    the method's ordinal unit for a column of whole dates is ONE DAY --
    so the interpolation of G7.3, which FLOORS, gives a different answer
    in the two units: floored in seconds it lands part way through a
    day, and floored in days it lands on the day the construction can
    actually write. The scaling does not cancel through a floor, and a
    window drawn the finer way sat up to a whole day above the
    construction's own lower end.

    So the arithmetic is done in the method's unit and put back into
    this reading's afterwards (`_space_unit`). A published rung of a
    date column names midnight, so the division is exact.
    """
    step = _space_unit(facts)
    return [
        _ordinal_of(rung, facts.resolution) // step
        for rung in facts.date_percentiles.rungs
    ]


def _space_unit(facts: contract.DatetimeFacts) -> int:
    """One ordinal unit of the resolution's own space (method G7.1).

    One quarter for a column of quarters and one second for a column of
    dates and times, both of which this reading counts in directly; one
    DAY for a column of whole dates, which this reading counts as 86400
    of its own units.
    """
    if facts.resolution == taxonomy.RESOLUTION_DATE:
        return 86400
    return 1


def _rung_rank(percent: int, dated: int) -> int:
    """Which sorted rank one published rung is read off (method G12.4).

    "The ordinal at sorted position `k = floor((P - 1) * c / 100)`,
    SELECTED and not interpolated" -- the profiler's own rung rule, in
    the whole numbers it is written in. The last rank is the furthest
    any percentage can reach.
    """
    return min(dated - 1, ((dated - 1) * percent) // 100)


def _ladder_segment(numerator: int, denominator: int) -> int:
    """The ladder segment one share falls in (method G7.3).

    The unique step with `PCT[j] * D <= 100 * N < PCT[j+1] * D`,
    scanning upward from zero and stopping at the first that holds. The
    percentages strictly increase, so the answer is unique; a share at
    or above the top of the ladder belongs to the last segment.
    """
    scaled = 100 * numerator
    for step in range(len(_LADDER_PERCENTS) - 1):
        below = _LADDER_PERCENTS[step] * denominator <= scaled
        if below and scaled < _LADDER_PERCENTS[step + 1] * denominator:
            return step
    return len(_LADDER_PERCENTS) - 2


def _ladder_ordinal_at(
    ladder: "list[int]", numerator: int, denominator: int
) -> int:
    """The published date ladder read at one share (method G7.3).

    The same whole-number interpolation the generator builds cells with,
    rounding DOWNWARD always -- Python's floor division floors toward
    negative infinity, which is the method's stated direction on both
    sides of the epoch. The float reader the numeric ladder uses is not
    this arithmetic and drawing a datetime window with it was review
    item P3-V4-F4's second half.
    """
    step = _ladder_segment(numerator, denominator)
    above = 100 * numerator - _LADDER_PERCENTS[step] * denominator
    span = (
        _LADDER_PERCENTS[step + 1] - _LADDER_PERCENTS[step]
    ) * denominator
    return ladder[step] + (
        above * (ladder[step + 1] - ladder[step])
    ) // span


def _precision_step(facts: contract.DatetimeFacts) -> int:
    """How far apart two neighbouring instants are, in this column's unit.

    The unit is the resolution's own (`_instant_of`): one quarter for a
    column of quarters, one day for a column of dates, one second for a
    column of dates and times -- so a column written to the minute steps
    sixty of its own units.
    """
    if facts.resolution == taxonomy.RESOLUTION_QUARTER:
        return 1
    if facts.resolution == taxonomy.RESOLUTION_MONTH:
        return 1
    if facts.resolution == taxonomy.RESOLUTION_DATE:
        return 86400
    if facts.time_precision == parsing.PRECISION_MINUTE:
        return 60
    return 1


def _reading_unit(facts: contract.DatetimeFacts) -> int:
    """What reading one written cell back can lose, in this column's unit.

    Method G12.4's `u`, and it is a SUM OF TWO THINGS: one unit of the
    ordinal space G7.1 fixes, for the downward rounding of the
    whole-number interpolation itself, PLUS the fifty-nine seconds a
    cell written to the minute carries no room for. A date, a quarter, a
    second and a subsecond cell each carry their own unit exactly and
    lose nothing further, so each of those is one unit of its own space.

    ONE UNIT IS ONE UNIT OF THE SPACE, NOT ONE STEP OF THE PRECISION
    (review item P3-V4-F5). The version this replaces read the first
    term as the distance between two neighbouring instants at the
    published precision and returned 60 + 59 = 119 seconds for a column
    written to the minute. The interpolation is done in the ordinal
    space, whose unit for a column of dates and times is ONE SECOND
    whatever the precision, so the allowance is 1 + 59 = 60 -- the
    number the generator computes from the same sentence. The extra
    fifty-nine seconds admitted a rung that misses its window by most of
    a minute, and the shipped test asserted the wrong number rather than
    the method's.

    The unit is the resolution's own (`_space_unit`), counted in what
    this reading counts in: one quarter for a column of quarters, one
    day -- 86400 of the seconds this reading speaks -- for a column of
    whole dates, one second for a column of dates and times. The
    fifty-nine are seconds either way, and only a column written to the
    minute carries them.
    """
    unit = _space_unit(facts)
    if (
        facts.resolution == taxonomy.RESOLUTION_DATETIME
        and facts.time_precision == parsing.PRECISION_MINUTE
    ):
        return unit + 59
    return unit


# -- method G7.1's ordinal space, one per resolution -------------------


def _ordinal_of(published: str, resolution: str) -> int:
    """One published instant as a whole number (method G7.1).

    ``published`` is text the strict loader has already admitted as a
    canonical value of ``resolution`` -- an endpoint or a ladder rung --
    so it always names an ordinal. A description that reached here
    carrying anything else is a loader that stopped checking, and the
    internal check below says so rather than letting a window be drawn
    round a number nobody computed.
    """
    ordinal = _instant_of(published, resolution)
    if ordinal is None:
        raise TypeError(
            "internal check: a published instant names no point in the "
            "ordinal space its own resolution fixes"
        )
    return ordinal


def _instant_of(moment: str, resolution: str) -> "int | None":
    """One canonical instant as a whole number, or None (method G7.1).

    THE SPACE IS THE RESOLUTION'S OWN, AND THERE ARE THREE OF THEM. The
    method's own table fixes one ordinal unit per resolution: one
    quarter for a quarter, one day for a date, one second for a date and
    time. Two of the three are what `parsing.instant_key` already reads
    a canonical instant into, scaled to whole seconds; the third is
    written out here because a quarter names no instant at all and that
    function returns None for one by design.

    WHY THIS IS WRITTEN HERE AND NOT IMPORTED (V1.4, review item
    P3-V3-F4). The generator computes the same ordinal from the same
    table, and a validator that called its function would share every
    arithmetic error with the code it is a second opinion on. So this is
    the method's table written a second time, from the method, and the
    suite compares the two writings where both may be imported.

    Returns None where the text is not a canonical value of that
    resolution -- which is how a measured file that re-describes as
    another kind of column reaches its own verdict rather than a number
    taken in the wrong space.
    """
    if resolution == taxonomy.RESOLUTION_QUARTER:
        return _quarter_ordinal(moment)
    if resolution == taxonomy.RESOLUTION_MONTH:
        return _month_ordinal(moment)
    return parsing.instant_key(moment, "")


def _month_ordinal(moment: str) -> "int | None":
    """`YYYY-MM` as `12 * (year - 1970) + (month - 1)`, or None (G7.1).

    Whole-number arithmetic on six digits, so the answer is the same on
    every machine and no calendar is consulted: a month names a span
    rather than an instant, which is exactly why it has a space of its
    own, as a quarter does below.
    """
    if len(moment) != 7:
        return None
    if moment[4] != "-":
        return None
    if not parsing.is_digit_text(moment[0:4]):
        return None
    if not parsing.is_digit_text(moment[5:7]):
        return None
    month = int(moment[5:7])
    if month < 1 or month > 12:
        return None
    year = int(moment[0:4])
    if year < 1:
        return None
    return 12 * (year - 1970) + month - 1


def _quarter_ordinal(moment: str) -> "int | None":
    """`YYYY-Qn` as `4 * (year - 1970) + (n - 1)`, or None (G7.1).

    Whole-number arithmetic on four digits and one, so the answer is the
    same on every machine and no calendar is consulted: a quarter names
    a span rather than an instant, which is exactly why it has a space
    of its own.
    """
    if len(moment) != 7:
        return None
    if moment[4:5] != _DATE_DASH or moment[5:6] != _QUARTER_MARK:
        return None
    year = _whole_number(moment[0:4])
    quarter = _whole_number(moment[6:7])
    if year is None or quarter is None:
        return None
    if quarter < 1 or quarter > 4:
        return None
    if year < 1:
        return None
    return 4 * (year - 1970) + (quarter - 1)


def _whole_number(figures: str) -> "int | None":
    """``figures`` as a whole number, or None when it is not all digits."""
    if not figures:
        return None
    for character in figures:
        if character not in _DIGITS:
            return None
    return int(figures)


# -- free text, identifiers, and the unrepresentable role -------------


def _text_checks(
    column: contract.ColumnBlock,
    facts: contract.TextFacts,
    block: "dict[str, object]",
    floor: int,
) -> "list[Check]":
    """A column no rule claimed, which publishes none of its values."""
    name = column.name
    checks: list[Check] = []
    for field, published in (
        ("n_all_digits", facts.n_all_digits),
        ("n_code_alphabet", facts.n_code_alphabet),
    ):
        found = _count_at(block, field)
        checks = checks + [
            _exact(
                name,
                f"free_text.{field}",
                f"counts.{field}",
                _shown_count(published),
                None if found is None else _shown_count(found),
            )
        ]
    lengths = _inner_at(block, "length")
    words = _inner_at(block, "words")
    for key, published in (
        ("min", facts.length.minimum),
        ("max", facts.length.maximum),
    ):
        found = None if lengths is None else _count_at(lengths, key)
        checks = checks + [
            _exact(
                name,
                f"free_text.length.{key}",
                f"length.{key}",
                _shown_count(published),
                None if found is None else _shown_count(found),
            )
        ]
    for key, published in (
        ("min", facts.words.minimum),
        ("max", facts.words.maximum),
    ):
        found = None if words is None else _count_at(words, key)
        checks = checks + [
            _exact(
                name,
                f"free_text.words.{key}",
                f"words.{key}",
                _shown_count(published),
                None if found is None else _shown_count(found),
            )
        ]
    checks = checks + _text_shape_checks(column, facts, lengths, words)
    checks = checks + [
        _occurrences(
            name,
            "free_text.n_distinct_by_occurrences",
            facts.n_distinct_by_occurrences,
            block,
        )
    ]
    checks = checks + _form_checks(
        name, "free_text.shape_forms", facts.shape_forms, block, floor
    )
    return checks


def _form_checks(
    name: str,
    fact: str,
    census: "dict[str, int]",
    block: "dict[str, object]",
    floor: int,
) -> "list[Check]":
    """The census of written forms, recounted on the measured file.

    ON THE SAME TERMS AS THE TWO WIDTH CENSUSES. Each named form is a
    count of cells the file evidences by holding them, and the pooled
    remainder names no form, so it is checked as the pool it is: a
    recounted form numbers at least its published count and at most
    that count plus the pool. Without this the twin owed the forms
    nothing, and the fact that lets a held-back value have a stand-in
    shaped like one would be published and never checked.
    """
    measured = _map_at(block, "shape_forms")
    held_back = 0
    if taxonomy.SUPPRESSED_LABEL in census:
        held_back = census[taxonomy.SUPPRESSED_LABEL]
    checks: "list[Check]" = []
    for form in sorted(census):
        if form == taxonomy.SUPPRESSED_LABEL:
            continue
        checks = checks + [
            _floor_governed(
                name,
                fact,
                f"forms.published.{form}",
                census[form],
                measured,
                form,
                floor,
                held_back,
            )
        ]
    return checks


def _group_span(
    occurrences: "dict[str, int]",
) -> "tuple[int, int, int] | None":
    """The smallest group, the largest group, and how many there are.

    The groups of method G9.5 step 1, read straight off the published
    multiplicity map: each key is a repetition count and its value is
    how many different values repeat that many times. Nothing here reads
    a cell, and the key is read as the figures it is rather than through
    a reader that answers in binary64 (review item P3-V8-F5).
    """
    smallest = 0
    largest = 0
    counted = 0
    for key in occurrences:
        found = contract.occurrence_size(key)
        if found is None:
            return None
        counted = counted + occurrences[key]
        largest = max(largest, found)
        if smallest == 0 or found < smallest:
            smallest = found
    if counted < 2 or smallest < 1:
        return None
    return (smallest, largest, counted)


def _length_mean_window(
    column: contract.ColumnBlock, facts: contract.TextFacts
) -> "tuple[float, float] | None":
    """The window `length.mean` may land in (method G12.6).

    WHY THIS IS NOT THE PUBLISHED ENDS (review item P3-V1-F9). Bounding
    the average by the two published lengths is true and nearly
    useless: a column of eighty singleton groups whose lengths run 48 to
    50 and whose published average is 49.525 was accepted at an achieved
    49.0, because 49.0 is between 48 and 50. G12.6 states the reach of
    G9.5's WALK, which is narrower by two orders of magnitude here: the
    walk starts every free group at the same place, moves one character
    at a time toward the whole target `T = round(a * N)`, and stops as
    soon as the residual changes sign -- so it overshoots by less than
    the largest group it moved.

    ``lo`` and ``hi`` -- which two groups carry the published ends -- are
    settled by G9.5's packing, which this module may not rebuild (V1.4).
    So the clamp is taken over the WIDEST reading of every pair the
    packing could have chosen, which depends on those groups' sizes
    alone. That is wider than the run's own window and never narrower,
    which is the only safe direction: a wider window can fail to catch a
    bad file, and a narrower one would accuse a conforming twin.
    """
    span = _group_span(facts.n_distinct_by_occurrences)
    if span is None or facts.length.mean is None:
        return None
    smallest_group, largest_group, _counted = span
    cells = column.n_present
    if cells < 1:
        return None
    low = facts.length.minimum
    high = facts.length.maximum
    if high < low:
        return None
    reach = high - low
    target = round(facts.length.mean * cells)
    floor_low = low * cells + smallest_group * reach
    floor_high = low * cells + largest_group * reach
    ceiling_low = high * cells - largest_group * reach
    ceiling_high = high * cells - smallest_group * reach
    written_low = max(floor_low, min(target - largest_group, ceiling_low))
    written_high = min(ceiling_high, max(target + largest_group, floor_high))
    return (written_low / cells, written_high / cells)


def _length_middle_window(
    column: contract.ColumnBlock, facts: contract.TextFacts
) -> "tuple[float, float] | None":
    """The window `length.p50` may land in (method G12.6).

    Every free group starts at the published middle, brought inside the
    two published ends, and the walk moves it in ONE direction only. Its
    whole movement is at most `M = |T - Built| + g_max`, and a group
    that moved `t` characters spent `t` of that for every row it covers,
    so at most `M / floor(N / 2)` characters of movement can reach the
    middle of the column.

    `Built` depends on which two groups carry the published ends, which
    is the packing's choice again, so it is taken over the widest
    reading of it -- and where a single group could cover half the
    column the method's own two exceptions apply and that end falls to
    the published one.
    """
    span = _group_span(facts.n_distinct_by_occurrences)
    if span is None or facts.length.p50 is None or facts.length.mean is None:
        return None
    smallest_group, largest_group, _counted = span
    cells = column.n_present
    if cells < 1:
        return None
    low = facts.length.minimum
    high = facts.length.maximum
    if high < low:
        return None
    start = max(low, min(high, round(facts.length.p50)))
    target = round(facts.length.mean * cells)
    built_low = (
        start * cells
        + largest_group * (low - start)
        + smallest_group * (high - start)
    )
    built_high = (
        start * cells
        + smallest_group * (low - start)
        + largest_group * (high - start)
    )
    movement = max(abs(target - built_low), abs(target - built_high))
    movement = movement + largest_group
    covered = max(1, cells // 2)
    reach = _rounded_up(movement, covered)
    lower = float(max(low, start - reach))
    upper = float(min(high, start + reach))
    if 2 * largest_group >= cells:
        # G12.6's two exceptions: a group that covers half the column
        # holds the middle itself, so the end it carries is the
        # published one.
        lower = float(low)
        upper = float(high)
    return (lower, upper)


def _text_shape_checks(
    column: contract.ColumnBlock,
    facts: contract.TextFacts,
    lengths: "dict[str, object] | None",
    words: "dict[str, object] | None",
) -> "list[Check]":
    """The three averages of method G12.6, each inside its own window.

    The two LENGTH windows are G12.6's own arithmetic, taken over the
    widest reading of the one thing the packing settles and this module
    may not rebuild -- which pair of groups carries the published ends.

    THE WORD AVERAGE IS STILL AT THE PUBLISHED ENDS, and that is stated
    rather than left to be found. G12.6 bounds it by the same walk and
    then by the clamp of G9.5 step 6, whose widening term `Allow` is a
    sum over the MEASURED cells' own lengths. Two things follow. The
    bound cannot be computed from the description alone, and the window
    would then be printed beside the verdict -- a number worked out from
    every cell of a file the description of that file does not publish,
    which is the disclosure gate's own line (V5.3). So this window stays
    the wider one until the report can carry the tighter one without
    saying more about the file than describing it would, and the miss
    that costs is a word average inside the published ends and outside
    the walk's reach.
    """
    name = column.name
    checks: list[Check] = []
    length_mean = _length_mean_window(column, facts)
    length_middle = _length_middle_window(column, facts)
    published_ends = (
        float(facts.length.minimum),
        float(facts.length.maximum),
    )
    for key, published, holder, low, high, fact, subcheck in (
        (
            "mean",
            facts.length.mean,
            lengths,
            (length_mean if length_mean else published_ends)[0],
            (length_mean if length_mean else published_ends)[1],
            "free_text.length.mean",
            "length.mean",
        ),
        (
            "p50",
            facts.length.p50,
            lengths,
            (length_middle if length_middle else published_ends)[0],
            (length_middle if length_middle else published_ends)[1],
            "free_text.length.p50",
            "length.p50",
        ),
        (
            "mean",
            facts.words.mean,
            words,
            float(max(1, facts.words.minimum)),
            float(max(1, facts.words.maximum)),
            "free_text.words.mean",
            "words.mean",
        ),
    ):
        # THE IDENTITY IS WRITTEN OUT, not worked out from which map was
        # handed in. Deriving it by asking whether this row's map IS the
        # length map made the words average answer to `length.mean`
        # whenever both maps were absent -- two different obligations
        # under one identity, which is the one thing a subcheck name may
        # never be.
        if published is None:
            continue
        found = None if holder is None else _number_at(holder, key)
        checks = checks + [
            _within(
                name,
                fact,
                subcheck,
                _shown_number(published),
                found,
                (low, high),
                ENVELOPE_TEXT_SHAPE,
                published,
            )
        ]
    return checks


def _identifier_checks(
    column: contract.ColumnBlock,
    facts: contract.IdentifierFacts,
    block: "dict[str, object]",
    mine: "tuple[str, ...]",
) -> "list[Check]":
    """A column the person declared to hold record numbers."""
    name = column.name
    checks: list[Check] = []
    for field, published, subcheck in (
        ("min_length", facts.min_length, "length.min"),
        ("max_length", facts.max_length, "length.max"),
        ("n_all_digits", facts.n_all_digits, "counts.n_all_digits"),
        ("n_code_alphabet", facts.n_code_alphabet, "counts.n_code_alphabet"),
    ):
        found = _count_at(block, field)
        checks = checks + [
            _exact(
                name,
                f"identifier.{field}",
                subcheck,
                _shown_count(published),
                None if found is None else _shown_count(found),
            )
        ]
    found_truth = _truth_at(block, "all_whole_numbers")
    checks = checks + [
        _exact(
            name,
            "identifier.all_whole_numbers",
            "type.all_whole_numbers",
            _shown_truth(facts.all_whole_numbers),
            None if found_truth is None else _shown_truth(found_truth),
        )
    ]
    if CORNER_IDENTIFIER_INFEASIBLE in mine:
        # REPORT-ONLY in this corner, listed rather than checked (owner
        # decision 6; review item P3-V1-F4).
        return checks
    checks = checks + [
        _occurrences(
            name,
            "identifier.n_distinct_by_occurrences",
            facts.n_distinct_by_occurrences,
            block,
        )
    ]
    return checks


def _unrepresentable_checks(
    column: contract.ColumnBlock,
    facts: contract.UnrepresentableFacts,
    block: "dict[str, object]",
) -> "list[Check]":
    """A column of numbers too large or too small to hold."""
    name = column.name
    checks: list[Check] = []
    for field, published in (
        ("n_whole", facts.n_whole),
        ("n_fraction", facts.n_fraction),
        ("n_whole_unknown", facts.n_whole_unknown),
        ("n_positive", facts.n_positive),
        ("n_negative", facts.n_negative),
        ("n_sign_unknown", facts.n_sign_unknown),
    ):
        found = _count_at(block, field)
        checks = checks + [
            _exact(
                name,
                f"numeric_unrepresentable.{field}",
                f"counts.{field}",
                _shown_count(published),
                None if found is None else _shown_count(found),
            )
        ]
    checks = checks + [
        _occurrences(
            name,
            "numeric_unrepresentable.n_distinct_by_occurrences",
            facts.n_distinct_by_occurrences,
            block,
        )
    ]
    return checks


def _occurrences(
    name: str,
    fact: str,
    published: "dict[str, int]",
    block: "dict[str, object]",
) -> Check:
    """The multiplicity map, compared whole and never spelled out.

    The identifier corner never reaches here: in that corner this fact
    is REPORT-ONLY and is a listing entry, so the caller does not build
    the check at all (review item P3-V1-F4).
    """
    subcheck = "distinct.n_distinct_by_occurrences"
    # The map's keys are group SIZES and its values how many values wore
    # each, so the number of entries is neither a count of values nor a
    # count of rows and is never printed as a bare number (review of the
    # shipped reports, 2026-08-15).
    shown = (
        f"the repetition pattern this description publishes, in "
        f"{_shown_count(len(published))} group size(s)"
    )
    found = _map_at(block, "n_distinct_by_occurrences")
    if found is None:
        return Check(name, fact, subcheck, WITHHELD, shown, "", _GATE_CLOSED)
    if found == published:
        return Check(name, fact, subcheck, HELD, shown)
    return Check(
        name,
        fact,
        subcheck,
        MISSED,
        shown,
        "",
        "",
        _NOT_SHOWN_IT_IS_A_COUNT_OF_THE_FILE,
    )


# -- V3.3: the obligations no CSV can evidence ------------------------


def _listings(
    description: contract.Profile, headed: bool
) -> "list[Listing]":
    """Every REPORT-ONLY obligation, and the ones a predicate strands."""
    listings = [
        Listing("", f"document.{field}", "", _NOT_CHECKABLE_REPORT_ONLY)
        for field in (
            "source.encoding",
            "source.used_fallback_encoding",
            "source.header_by_convention",
            "source.header_evidence",
        )
    ]
    if not headed:
        # THE SAME IDENTITY A VERDICT CARRIES, which is what `subcheck`
        # is for: both of these facts ARE checked on a file with a
        # header line, as `header.names` and `columns.order`, and a
        # listing that names neither leaves a reader comparing this
        # census with an ordinary run's unable to see they are the same
        # obligation (review of the shipped reports, 2026-08-15).
        listings = listings + [
            Listing(
                "",
                "universal.name",
                "header.names",
                _NOT_CHECKABLE_HEADERLESS_ORDER,
            ),
            Listing(
                "",
                "document.columns",
                "columns.order",
                _NOT_CHECKABLE_HEADERLESS_ORDER,
            ),
        ]
    corners = corners_of(description)
    for column in description.columns:
        for field in (
            "missing_by_class",
            "missing_by_source",
            # The two counts contract version 5 moved out of the map
            # above (its section 5). They are REPORT-ONLY for the map's
            # own reason -- the twin writes every absent cell empty --
            # so they belong on this census beside it, at the same
            # width, rather than being the two facts the census forgets.
            "n_missing_blank",
            "n_missing_withheld",
            "n_sentinel_candidates_unpublished",
            "sentinel_verdicts",
            "detection_evidence",
            "remarks",
        ):
            listings = listings + [
                Listing(
                    column.name,
                    f"universal.{field}",
                    "",
                    _NOT_CHECKABLE_REPORT_ONLY,
                )
            ]
        # THE AXIS THAT IS A FACT ABOUT THE DESCRIPTION (review item
        # P3-V2-C-F3; plan amendment A-P3-2). The other three axes are
        # read back off the file's own description and a file can make
        # each of them differ; this one is computed from the
        # declaration list the file is described under, so it reads the
        # same word on both sides whatever the file holds.
        listings = listings + [
            Listing(
                column.name,
                "universal.structural_role",
                "axes.structural_role",
                _NOT_CHECKABLE_DECLARED_AXIS,
            )
        ]
        if not _position_is_evidencible(column, headed):
            listings = listings + [
                Listing(
                    column.name,
                    "universal.position",
                    "position.at",
                    _NOT_CHECKABLE_FIRST_COLUMN,
                )
            ]
        facts = column.facts
        if isinstance(facts, contract.DatetimeFacts):
            listings = listings + [
                Listing(
                    column.name,
                    "datetime.format",
                    "",
                    _NOT_CHECKABLE_REPORT_ONLY,
                ),
                Listing(
                    column.name,
                    "datetime.resolution_mix",
                    "",
                    _NOT_CHECKABLE_RESOLUTION_MIX,
                ),
            ]
            listings = listings + _endpoint_listings(column, facts, corners)
        if isinstance(facts, contract.NumericFacts) and not _ladder_points(
            facts.percentiles.rungs
        ):
            listings = listings + [
                Listing(
                    column.name,
                    f"numeric.{field}",
                    f"moments.{field}",
                    _NOT_CHECKABLE_NO_LADDER,
                )
                for field in ("mean", "std", "skew")
            ]
        if isinstance(facts, contract.NumericFacts):
            listings = listings + _unbounded_style_listings(column, facts)
        listings = listings + _corner_listings(
            column, _corner_names(corners, column.name)
        )
    return listings


def _endpoint_listings(
    column: contract.ColumnBlock,
    facts: contract.DatetimeFacts,
    corners: "dict[str, tuple[str, ...]]",
) -> "list[Listing]":
    """An endpoint offset the publication floor held back on its own.

    P2-D9's corner is the map that is NOTHING BUT the withheld key, and
    `_corner_listings` files all four obligations there. This is the
    other shape: a map naming real offsets whose own earliest or latest
    END fell below the floor and was published as the withheld label.
    The description then names no offset for that end, so no file
    carries one either way -- and the comparison that stood here asked
    whether the file's OWN floor had suppressed the same end, which is a
    fact about how many rows shared an offset rather than about the
    file's dates, and reported MISSED against the shipped generator's
    own twin.
    """
    if CORNER_DATETIME_OFFSETS_WITHHELD in _corner_names(
        corners, column.name
    ):
        return []
    listings: list[Listing] = []
    for field, published, subcheck in (
        ("earliest_utc_offset", facts.earliest_utc_offset, "offsets.earliest"),
        ("latest_utc_offset", facts.latest_utc_offset, "offsets.latest"),
    ):
        if published != taxonomy.SUPPRESSED_LABEL:
            continue
        listings = listings + [
            Listing(
                column.name,
                f"datetime.{field}",
                subcheck,
                _NOT_CHECKABLE_ENDPOINT_WITHHELD,
            )
        ]
    return listings


def _unbounded_style_listings(
    column: contract.ColumnBlock, facts: contract.NumericFacts
) -> "list[Listing]":
    """The numeric obligations this description leaves nothing to check.

    Two of them, both review items of round 2 and both recorded in plan
    amendment A-P3-2: the canonical-form ceiling a description licenses
    every cell against (`_ceilinged_styles`), and the skew whose G12.3
    window is the statistic's whole attainable range
    (`_skew_admits_every_value`). Each is an obligation the description
    states and no file of the length it publishes can be found to miss,
    so each is a line in the NOT-CHECKABLE census with the sentence that
    says why, and neither is counted toward a pass.
    """
    listings: list[Listing] = []
    for style in (parsing.STYLE_DECIMAL, parsing.STYLE_EXPONENT_LOWER):
        if style in _ceilinged_styles(column, facts):
            continue
        listings = listings + [
            Listing(
                column.name,
                "numeric.numeric_styles",
                f"styles.canonical.{style}",
                _NOT_CHECKABLE_STYLE_CEILING,
            )
        ]
    if _skew_admits_every_value(column, facts):
        listings = listings + [
            Listing(
                column.name,
                "numeric.skew",
                "moments.skew",
                _NOT_CHECKABLE_SKEW_UNBOUNDED,
            )
        ]
    return listings


def _corner_listings(
    column: contract.ColumnBlock, mine: "tuple[str, ...]"
) -> "list[Listing]":
    """The facts a corner makes REPORT-ONLY, listed and never verdicted.

    REVIEW ITEM P3-V1-F4, AND WHY THIS IS NOT A LOWERING. A corner the
    ratified plan names does two different things depending on which
    corner it is. Two of them send a fact to an ENVELOPE -- it is still
    measured, and a file outside both ends still MISSES -- and those
    stay executable subchecks with the AUTHORIZED-DEVIATION verdict the
    registry authorizes. The other two send facts to REPORT-ONLY, which
    the matrix says a CSV cannot evidence at all: the description
    withheld the offsets, or its own published lengths cannot supply the
    distinct values it publishes. There is nothing there to measure, and
    the version this replaces returned four AUTHORIZED-DEVIATION checks
    and three more for the identifier corner -- counted in the census as
    obligations a file had been checked against, which they had not
    been. They are listing entries, they carry the plan passage that
    authorizes the lesser outcome, and they are counted where a
    not-checkable obligation is counted.
    """
    facts = column.facts
    listings: list[Listing] = []
    if CORNER_DATETIME_OFFSETS_WITHHELD in mine and isinstance(
        facts, contract.DatetimeFacts
    ):
        why = _NOT_CHECKABLE_OFFSETS_WITHHELD + CORNER_CITATIONS[
            CORNER_DATETIME_OFFSETS_WITHHELD
        ]
        for field, subcheck in (
            ("utc_offsets", "offsets.map"),
            ("earliest_utc_offset", "offsets.earliest"),
            ("latest_utc_offset", "offsets.latest"),
            ("datetimes_read_at", "offsets.read-at"),
        ):
            listings = listings + [
                Listing(column.name, f"datetime.{field}", subcheck, why)
            ]
    if CORNER_IDENTIFIER_INFEASIBLE in mine and isinstance(
        facts, contract.IdentifierFacts
    ):
        why = _NOT_CHECKABLE_IDENTIFIER_CORNER + CORNER_CITATIONS[
            CORNER_IDENTIFIER_INFEASIBLE
        ]
        for field in (
            "n_distinct",
            "n_distinct_folded",
            "n_distinct_by_occurrences",
        ):
            listings = listings + [
                Listing(
                    column.name,
                    f"identifier.{field}",
                    f"distinct.{field}",
                    why,
                )
            ]
    group = _group_of(facts)
    for field, published in (
        (_RAW_DISTINCT, column.n_distinct),
        (_FOLDED_DISTINCT, column.n_distinct_folded),
    ):
        # PER FIELD, exactly as `_distinctness_checks` asks it (review
        # item P3-V8-F3): a listing here and a check there are the two
        # halves of one decision, so they are made by one rule and the
        # census cannot count an entry the checks never dropped.
        corner = _distinct_corner(facts, mine, field)
        if corner and corner != CORNER_IDENTIFIER_INFEASIBLE:
            why = _NOT_CHECKABLE_SPELLING_ENVELOPE + CORNER_CITATIONS[corner]
            if not _envelope_admits_every_count(column, facts, published):
                continue
            listings = listings + [
                Listing(
                    column.name,
                    f"{group}.{field}",
                    f"distinct.{field}",
                    why,
                )
            ]
    return listings


def _zero_row_listings(
    description: contract.Profile, headed: bool
) -> "list[Listing]":
    """What a file of no rows cannot evidence (owner decision 7).

    The byte form IS the check on this predicate (V6.4), so every
    per-column obligation the description still states is listed at the
    grain it would have been checked at rather than left out of the
    census: a description publishing no rows publishes little about each
    column, and what it does publish a file of no bytes cannot evidence.
    """
    listings = _listings(description, headed)
    for column in description.columns:
        for check in _obligations(
            description, column, [], {}, {}, None, headed
        ):
            listings = listings + [
                Listing(
                    check.column,
                    check.fact,
                    check.subcheck,
                    _NOT_CHECKABLE_ZERO_ROWS,
                )
            ]
    if headed:
        # The headed form's structural facts are CHECKS, not listings:
        # its file carries a header line and that line evidences them
        # (`_zero_row_structure`; review item P3-V2-E-F5).
        return listings
    # ONE LISTING, NOT TWO (review item P3-V2-E-F5). `universal.position`
    # is bound already, once per column, by the walk above -- the same
    # walk that binds every other per-column obligation. A second
    # document-level line for the same fact bound it twice and counted
    # one obligation the description does not set: V3.3 forbids a
    # double binding in the same words it forbids an unbound one.
    return listings + [
        Listing(
            "",
            "document.n_columns",
            "columns.n_columns",
            _NOT_CHECKABLE_ZERO_ROWS,
        ),
    ]

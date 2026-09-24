"""The generation transform against an oracle it did not produce (P2-D7).

The charter forbids generated values being their own oracle. So
`tools/reference/make_generation_reference_vectors.py` implements
`docs/spec/generation-method-v1.md` from that document alone, importing
neither this package nor any numeric library, and its output is
committed as a provenance-manifest fixture: CI rebuilds it from the
generator and byte-compares it on every run, so the oracle cannot drift
towards the implementation without the provenance guard going red.

Two halves are tested here, and they are different claims.

**The implementation reproduces the committed cells.** The vectors are a
pure function of GIVEN words -- the oracle draws none and holds no
generator, because the fixture guard refuses an import of `ctypes` and
numpy imports `ctypes`. The words each case carries are the opening
words of the single stream at the seed named in `SEEDS` below, which is
what lets the same case be put through `generate` and compared cell for
cell. That binding is asserted here rather than assumed, and so is the
property section G3.3 rests on: the word sequence does not depend on how
the calls are cut.

**Every number the vector file publishes was proved.** The proof layer
is only worth what it refuses, so the tests at the bottom of this file
try to make it certify a lie, exactly as `tests/test_oracle_proof_layer.py`
does for the Phase 1 vectors: a number outside a wrapper, a whole number
under one, a number inside a tuple the JSON encoder writes as an array,
a container the walk has no rule for, and each of those driven through
the whole generator so that nothing is written.

All nine cases are asserted the same way. The identifier case once
disagreed and was carried as a strict expected failure while the
implementation was repaired to the oracle rather than the other way
round: it missed the fold collisions method section G9.3 requires and
wrote ten cells that were figures and nothing else against a published
count of none. The vectors were never adjusted to match the code they
exist to check, and `tests/test_generation.py` now holds a standing
check on both obligations for profiles the vectors do not cover.

`identifier_whole_numbers` is the ninth case, added when review item
P2-C2-F7 found the ORACLE carrying a rule the method had withdrawn --
that `all_whole_numbers` true means every group is written from the
figures -- with no frozen case reaching the branch, so byte equality
never tested it. The oracle was reconciled to method section G9.6 by
that tool's owner, from the specification alone, and the case exists so
that the branch is covered rather than merely corrected.

**The five branch cases are the same oracle's second file** (review
items P2-C3-F3 and P2-C4-C3). The nine above reached no unrepresentable
column, no joint class-and-alphabet packing of free text, no fold
collision that a case change cannot build, no cell carrying the literal
`decimal`, `leading_zero` or `leading_plus` style, and no published end
whose seconds field is 60, so a defect on any of those branches left
every committed byte unchanged. They live in a second fixture because a
committed fixture must stay under the provenance manifest's 100000-byte
cap and the nine already spend 88207 of it; they are one oracle, one
transform and one proof layer, and the tests below hold both files to
the same claims.

**Every one of the forty carries a mutant that removes or reverts the
branch it exists for** (G14.3; review item P2-C4-C2). They are one table
at the bottom of this file, `CASE_MUTANTS`, whose keys are asserted
equal to the whole case set, because four cases with a mutant and ten
without is the same gap in a quieter form: a case whose own rule can be
reverted with every committed byte unchanged tests nothing. Each entry
builds its case unmutated first, so a mutant cannot pass by refusing for
some reason of its own.

`identifier_edge_spacing` was carried as a strict expected failure for
one round while the oracle and the implementation disagreed about which
partner method section G9.3's family hands to which slot. It is bound
normally here now. The vectors were not adjusted: G9.3 states the
selection rule the two implementations had worked out differently
(review item P2-C4-F4), and it is the rule these committed bytes already
followed -- every slot walks its parent's family from that family's own
start and takes the first member the column has not written whose length
its own window admits.
"""

import ast
import importlib.util
import json
import math
import pathlib
import sys
import typing

import numpy
import numpy.ctypeslib
import pytest

import fixtures
from synthtwin import (
    contract,
    dialect,
    generation,
    parsing,
    rendering,
    sheetwriting,
    taxonomy,
    workbook,
)

REPOSITORY = pathlib.Path(__file__).resolve().parent.parent
GENERATOR = REPOSITORY / "tools" / "reference" / "make_generation_reference_vectors.py"
BRANCH_GENERATOR = (
    REPOSITORY / "tools" / "reference" / "make_generation_branch_vectors.py"
)
SECOND_BRANCH_GENERATOR = (
    REPOSITORY / "tools" / "reference" / "make_generation_branch_vectors_2.py"
)
# THE FIFTH FILE (the repair of the final Codex review of the number
# censuses, plans P4-D142, P4-D145, P4-D147 and P4-D149).
THIRD_BRANCH_GENERATOR = (
    REPOSITORY / "tools" / "reference" / "make_generation_branch_vectors_3.py"
)
VECTORS = (
    pathlib.Path(__file__).resolve().parent
    / "reference"
    / "generation-reference-vectors.json"
)
BRANCH_VECTORS = (
    pathlib.Path(__file__).resolve().parent
    / "reference"
    / "generation-branch-vectors.json"
)
SECOND_BRANCH_VECTORS = (
    pathlib.Path(__file__).resolve().parent
    / "reference"
    / "generation-branch-vectors-2.json"
)
THIRD_BRANCH_VECTORS = (
    pathlib.Path(__file__).resolve().parent
    / "reference"
    / "generation-branch-vectors-3.json"
)
# THE SIXTH FILE (the repair of the carried items of landing 2b, plans
# P4-D176, P4-D178, P4-D183 and P4-D185).
FOURTH_BRANCH_GENERATOR = (
    REPOSITORY / "tools" / "reference" / "make_generation_branch_vectors_4.py"
)
FOURTH_BRANCH_VECTORS = (
    pathlib.Path(__file__).resolve().parent
    / "reference"
    / "generation-branch-vectors-4.json"
)
# THE SEVENTH FILE (the final pass over the close of stage 2, plan P4-D193).
FIFTH_BRANCH_GENERATOR = (
    REPOSITORY / "tools" / "reference" / "make_generation_branch_vectors_5.py"
)
FIFTH_BRANCH_VECTORS = (
    pathlib.Path(__file__).resolve().parent
    / "reference"
    / "generation-branch-vectors-5.json"
)
# THE EIGHTH FILE (the extra review round of 2026-09-18, its date pass and
# its number pass together). They are a file of their own because the
# seventh, rebuilt at the integration to hold them, stood at 276235 bytes
# against the manifest's 250000-byte cap.
SIXTH_BRANCH_GENERATOR = (
    REPOSITORY / "tools" / "reference" / "make_generation_branch_vectors_6.py"
)
SIXTH_BRANCH_VECTORS = (
    pathlib.Path(__file__).resolve().parent
    / "reference"
    / "generation-branch-vectors-6.json"
)
# THE NINTH FILE (the carried numbers repair pass of 2026-09-19). The
# eighth's output had passed 200000 bytes, the line plan P4-D295 draws for
# opening the next entry point.
SEVENTH_BRANCH_GENERATOR = (
    REPOSITORY / "tools" / "reference" / "make_generation_branch_vectors_7.py"
)
SEVENTH_BRANCH_VECTORS = (
    pathlib.Path(__file__).resolve().parent
    / "reference"
    / "generation-branch-vectors-7.json"
)
# THE TENTH AND ELEVENTH FILES, and BOTH stage-3 tail landings are in
# them. The tenth (plan P4-D328) was opened by the date and clock tails
# for the four cases that landing grew past the room their own files
# had -- grown in place they carried the second file to 261857 bytes
# and the first to 258476 against the manifest's 250000-byte cap -- and
# it carries two of the NUMERIC tail rule's five cases beside them
# (landing 3.3). The other three are the eleventh: five cases of one
# rule do not fit under that cap in one file, and the tenth had no room
# for them once the date cases stood in it.
EIGHTH_BRANCH_GENERATOR = (
    REPOSITORY / "tools" / "reference" / "make_generation_branch_vectors_8.py"
)
EIGHTH_BRANCH_VECTORS = (
    pathlib.Path(__file__).resolve().parent
    / "reference"
    / "generation-branch-vectors-8.json"
)
NINTH_BRANCH_GENERATOR = (
    REPOSITORY / "tools" / "reference" / "make_generation_branch_vectors_9.py"
)
NINTH_BRANCH_VECTORS = (
    pathlib.Path(__file__).resolve().parent
    / "reference"
    / "generation-branch-vectors-9.json"
)
# THE FOURTH FILE (landing 2b.17): the cases for the transforms that
# produce a whole DOCUMENT rather than one column's cells.
DOCUMENT_GENERATOR = (
    REPOSITORY / "tools" / "reference" / "make_generation_document_vectors.py"
)
DOCUMENT_VECTORS = (
    pathlib.Path(__file__).resolve().parent
    / "reference"
    / "generation-document-vectors.json"
)


def _generator():
    """The vector generator, loaded from its path (it is not a package)."""
    spec = importlib.util.spec_from_file_location(
        "make_generation_reference_vectors", GENERATOR
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gen = _generator()

# The oracle's own filling and numeric content, held before any test
# patches them, so a mutant calls the rule it replaces rather than itself.
gen_filled_form = gen.filled_form
gen_numeric_content = gen._numeric_content
gen_grouped_enough = gen.grouped_enough
gen_layout_preferences = gen.layout_preferences
gen_alphabet_readings = gen.alphabet_readings
gen_identifier_readings = gen.identifier_readings
gen_traded = gen.traded_merges
gen_form_places = gen.form_places
# The oracle's own ramp, held before any test patches it, so the moment
# ladder's mutant can read the block as the ramp of G5.3d without calling
# the mutant it replaces.
made_up_ramp_of = gen.made_up_ramp



def _document() -> dict:
    return json.loads(VECTORS.read_text(encoding="utf-8"))


def _branch_document() -> dict:
    return json.loads(BRANCH_VECTORS.read_text(encoding="utf-8"))


def _second_branch_document() -> dict:
    return json.loads(SECOND_BRANCH_VECTORS.read_text(encoding="utf-8"))


def _third_branch_document() -> dict:
    return json.loads(THIRD_BRANCH_VECTORS.read_text(encoding="utf-8"))


def _fourth_branch_document() -> dict:
    return json.loads(FOURTH_BRANCH_VECTORS.read_text(encoding="utf-8"))


def _fifth_branch_document() -> dict:
    return json.loads(FIFTH_BRANCH_VECTORS.read_text(encoding="utf-8"))


def _sixth_branch_document() -> dict:
    return json.loads(SIXTH_BRANCH_VECTORS.read_text(encoding="utf-8"))


def _seventh_branch_document() -> dict:
    return json.loads(SEVENTH_BRANCH_VECTORS.read_text(encoding="utf-8"))


def _eighth_branch_document() -> dict:
    return json.loads(EIGHTH_BRANCH_VECTORS.read_text(encoding="utf-8"))


def _ninth_branch_document() -> dict:
    return json.loads(NINTH_BRANCH_VECTORS.read_text(encoding="utf-8"))


# The nine cases method section G14.3 names, and the four the review of
# 158c811 added beside them (plans P4-D130, P4-D132, P4-D133), and the two
# its skeptic added (plan P4-D138), which live in this file because it
# has the room.
REQUIRED_CASES = (
    "date_gap_places",
    "date_only",
    "date_peak_heap",
    "date_thinning_week",
    "identifier_fold_collisions",
    "identifier_whole_numbers",
    "label_variants",
    "may_month_names",
    "mixed_parsed_unparsed",
    "month_first_widths",
    "numeric_decimal_styles",
    "numeric_integer",
    "offset_bearing",
    "quarter",
    "reserved_name_floor",
)

# The eight that section adds for the branches those nine leave
# unexercised (review items P2-C3-F3 and P2-C4-C3, and owner decision
# 11's pooled-spelling case), which are the second committed file of the
# same oracle.
BRANCH_CASES = (
    # THE THIRD FROZEN CASE FOR A ROLE PHASE 4 ADDED (residual
    # R-P4-17). It pins the rule the affixed role exists for: the
    # universal class counts answer for the CELLS and the quantitative
    # block for the CORES, and they are not the same set.
    "affixed_brackets",
    # THE CENSUS OF SPELLINGS OF A COUNT COLUMN (landing 2b.18 part 2,
    # plan P4-D123). Every count case before it wrote each number one
    # way, so it publishes an empty census and the rule could be
    # withdrawn with every committed byte unchanged.
    "count_spellings",
    "free_text_joint",
    "identifier_edge_spacing",
    # THE LAYOUT OF A RECORD NUMBER (contract 7.12, landing 2b.18). The
    # three identifier cases beside it publish an EMPTY census, so the
    # whole layout rule -- the seventh published key of the role, and
    # the generator walk that writes each cell to it -- could have been
    # withdrawn with every committed byte unchanged. This is the case
    # that holds it up.
    "identifier_layout",
    # THE FILL, THE SPACE AND THE MIXES OF A LAYOUT CENSUS (landing
    # 2b.18's repair pass, plans P4-D126 to P4-D128). `identifier_layout`
    # names two layouts that pay every cell, so a zero fill two noughts
    # deep, a space inside a layout and a pool written to mixes of the
    # named kinds could each be withdrawn with every committed byte
    # unchanged.
    "identifier_layout_mixes",
    # THE PROVEN SIGN OF A LAYOUT CENSUS (plan P4-D156): a sign before
    # figures written where the census proves the table held one.
    "identifier_signed_layout",
    # THE FOURTH AND LAST OF THE ROLES PHASE 4 ADDED (residual
    # R-P4-17). It pins the pairing walk of G6B.4, the only search in
    # the method and the only place synthtwin reproduces structure
    # between two quantities at all.
    "joined_readings",
    "leap_second_endpoint",
    # THE SHAPE OF A PUBLISHED LABEL (landing 2b.18 part 2, plan
    # P4-D122). No label case before it reaches a stand-in the census
    # owes no form, so the rule could be withdrawn with every committed
    # byte unchanged.
    "level_shape_stand_ins",
    # THE FIRST FROZEN CASE FOR A ROLE PHASE 4 ADDED (residual
    # R-P4-17). Every other case here exercises a role Phase 1 to 3
    # built; the four Phase 4 roles had no independent vector at all,
    # so their generator branches were checked only against
    # themselves. This is one of the four.
    "long_tail_levels",
    # THE CASE OF A LETTER (landing 2b.18 part 2, plan P4-D121). Every
    # label case before it publishes a census blind to case.
    "lower_case_stand_ins",
    # THE CASE FOR THE SPELLING OF A MOMENT that stayed here (plan
    # P4-D39, stage 2): the evenly spread rotation of marks, its tie
    # rule and the withheld pool. Its neighbour, the day-unit case,
    # moved to the tenth file at the tail landing for the room it
    # needed there.
    # THE ONE CASE IN ANY OF THE THREE FILES THAT NAMES MORE THAN ONE
    # CONVENTION (landing 2b.7, plan P4-D65.2). A census naming ONE
    # notation or ONE mark cannot pin the allocators that spend it: the
    # census path and the majority path write the same cell, so a
    # mutant that withdraws the census leaves every frozen byte where it
    # was, and both oracle mutants were GREEN against the nine spelling
    # cases already here. This one names two of each at eleven cells
    # apiece, so the cells divide and a mutant moves them.
    "mixed_conventions",
    "mixed_marks",
    # The month, added with the second SPAN resolution (plan P4-D4.3
    # item 2). A new transform reaching the twin without an independent
    # frozen case is a transform the generator and the validator agree
    # about with nobody else in the room (review item P4-DATE3-F1).
    "month_span",
    "numeric_point_free_styles",
    "numeric_pooled_spelling",
    # THE SECOND SPELLING FAMILY OF G10.5, added with revision 5
    # (residuals R-P4-48 and R-P4-68). `unrepresentable_joint` below
    # reaches this role, and every cell it freezes is a digit string
    # four hundred characters wide or the fixed contradictory
    # construction -- so the exponent family could have been withdrawn
    # entirely with both committed files byte-identical. This case is
    # six cells published at five and six characters, widths no digit
    # string can be written at.
    #
    # THE ORDER OF THIS TUPLE IS ITS SORTED ORDER, which one test below
    # compares against the committed file's own key order.
    "unrepresentable_exponent",
    "unrepresentable_joint",
)

# The third committed file: the cases the carried landings 2b.4, 2b.3 and
# 2b.2 added, split out when the second would have passed the provenance
# guard's byte cap (G14.2). The order of this tuple is its sorted order too.
SECOND_BRANCH_CASES = (
    # LANDING 2b.3'S REPAIR PASS left one case in this file, and landing 2b.6
    # withdrew it: an accidental value at midnight was moved off a column
    # publishing a count of nought, and no column publishes that nought any
    # more, because a reader able to tell it from a suppressed count of one had
    # been told that count. Its neighbour -- bare dates beside moments at local
    # midnight on a real offset, whose ranks with a published instant settle
    # their form and offset before the rotation -- is in the first file.
    # THE REST OF LANDING 2b.2'S MARKS AND NOTATIONS, frozen at the
    # integration of landings 2b.1 to 2b.5 once the branch cases had a file
    # with room: the apostrophe with the minus sign, U+2019 with the trailing
    # minus, U+00A0 on a declared decimal comma (whose mutant is the exchange),
    # U+202F and U+2009. Eleven rows each: at twenty-two the five carried
    # this file past the provenance guard's byte cap.
    "apostrophe_minus_sign",
    # THE SPELLINGS OF A NUMBER LANDING 2b.2 FREEZES, in their sorted
    # places: a comma between thousands beside signed decimals with
    # zeros spent past order nought, a point on a declared decimal-comma
    # column beside two absent cells, and a space with accounting
    # brackets. They were three and not four while every branch case
    # shared one file, whose byte cap a fourth would have passed; the
    # other five followed when this file was split out.
    "grouped_charges",
    "grouped_decimal_comma",
    # TWO RULES OF G9.6 the repair of the final review of the labels
    # added (plans P4-D157 and P4-D158): a record number never written in
    # a spelling read as absent, and a partner wearing the layout its
    # identity reserved. The layout cases could each have lost its rule
    # with every committed byte unchanged.
    "identifier_absent_words",
    "identifier_layout_partners",
    # WHAT THE CENSUS COULD HOLD, AND THE PLACES A NUMBER MAY TAKE (method
    # G8.3a, landing 2b.4's repair). `label_numbers` pools two cells, so a
    # number stepping past every named `%.%` value may write `10.0` there;
    # this one pools none, and the rule that ends that side instead -- and
    # takes the published whole numbers' places -- could be withdrawn with
    # every other committed byte unchanged.
    "label_number_tiers",
    # THE CLASS DEBT OF A COLUMN OF LABELS (method G8.3a, landing 2b.4).
    # Every earlier label case publishes no number, so the rule that
    # writes a held-back number AS a number -- stepped from the published
    # numbers, gaps first -- could be withdrawn with every committed byte
    # unchanged.
    "label_numbers",
    # THREE OF THE FIVE CASES OF LANDING 2b.3 stayed here: midnight on
    # two offsets, a withheld pool spent on the unnamed marks, and a
    # slashed stamp's one permitted mark. The bare dates beside midnight
    # moments and the column partly at midnight moved to the tenth file
    # at the tail landing, for the room they needed there.
    "midnight_mixed_forms",
    "midnight_two_offsets",
    "narrow_spaced",
    "pooled_marks",
    "quoted_trailing_minus",
    "slashed_pool",
    "spaced_brackets",
    "spaced_decimal_comma",
    "thin_spaced",
)

# The fifth committed file: the cases the repair of the final Codex review
# of the number censuses added (plans P4-D142, P4-D145 and its amendment,
# P4-D147 and P4-D149), each of
# whose rules could otherwise be withdrawn with every committed byte
# unchanged. Sorted, like the tuples above.
THIRD_BRANCH_CASES = (
    "bare_mark_remainder",
    # G9.6's LAYOUT PACKING (plan P4-D182): a census no class-and-alphabet
    # packing can lay out, which the packing with the census as a third
    # margin lays out exactly.
    "identifier_layout_packing",
    "plus_padded_field",
    "pooled_mark_cells",
    "saturated_integers",
    "signed_pads",
    "spread_conventions",
    "unpublished_majority_marks",
)

# The sixth committed file: the cases the repair of the carried items of
# landing 2b added -- G6.5a's walks reach by reach (plan P4-D183), its two
# fills of plans P4-D176 and P4-D178, the census of marks held at a
# thousand (plan P4-D185), the numbers of a free-text column carrying
# the average (plan P4-D190), a withheld count at midnight kept on its side
# (plan P4-D191), the counts of different dates and widths reached
# (plan P4-D192), the sizes of the held-back labels read off their pooled
# total (plan P4-D201), and a record number's literal prefix written as
# part of its layout (plan P4-D202). Sorted, like the tuples above.
FOURTH_BRANCH_CASES = (
    "date_distinct_reached",
    "date_widths_reached",
    "grouped_thousands",
    "identifier_column_prefix",
    "identifier_layout_prefixes",
    "midnight_withheld_kept",
    "numbers_carry_the_average",
    "pooled_level_sizes",
    "saturated_levels",
    "saturated_tenths",
    "separated_in_order",
)

# The seventh committed file: a whole number a column writes two ways,
# held by two strata (plan P4-D193), the census of marks held on a column
# with refunds (plan P4-D194), and a declared identifier's partners held to
# its unnamed cells (plan P4-D196), and a workbook column's truth values
# (plan P4-D198). Sorted, like the tuples above.
FIFTH_BRANCH_CASES = (
    "code_band_words",
    # G7.9's spend of a mark the census absorbed out of reach (plan
    # P4-D245, ledger K-2B-51, the owner on 2026-09-21). It comes here
    # for the reason the two exponent cases below do.
    "date_absorbed_mark",
    # THE TWO RULES OF G8.3a STEP 3 (the repair pass of the second Codex
    # round, 2026-09-19, closing its skeptic's finding 1). They come here
    # because the eighth committed file stands at 212306 bytes and the
    # ninth at 214367, both past plan P4-D295's 200000-byte line, while
    # this one stands at 162761 -- which is the case the eighth entry
    # point's own account provides for when it says the fifth takes a case
    # where it cannot.
    "exponent_fitted",
    "exponent_scaled",
    "grouped_thousands_signed",
    "identifier_unnamed_partners",
    # THE POOL'S OWN SCALE (method G8.3c, plan P4-D301, ledger K-2B-50).
    # It comes here for the reason the two above it did: this file has
    # room under the byte cap and the two newest do not.
    "pooled_number_scale",
    "truth_values_written",
    "twice_written_filled",
    "twice_written_merged",
)

# The seven cases the extra review round of 2026-09-18 added: the five of
# its date pass (plans P4-D254 to P4-D258) -- the feasible spend of the
# offsets, the offsets of the ranks tied at an end, the census key carried
# into the width pass, and G7.3's two merges, the traded one and the one
# onto a unit that is no rank neighbour -- and the two of its number pass
# (plans P4-D269 and P4-D265). Sorted, like the tuples above.
SIXTH_BRANCH_CASES = (
    # The joint word of a rank showing both fields where the census names
    # one-field words alone (the repair pass of the carried date items of
    # 2026-09-18, plan P4-D294 amended).
    "date_both_fields_disagree",
    "date_endpoint_ties",
    "date_midnight_feasible",
    # The MIDNIGHT half of P4-D258's paid merge (the dates pass of the
    # second Codex round of 2026-09-19).
    "date_midnight_traded",
    "date_nonadjacent_merge",
    "date_second_field_class",
    "date_traded_merge",
    # P4-D258's two merges reached again, on a column carrying two width
    # kinds (the carried date items of 2026-09-18).
    "date_two_kinds_nonadjacent",
    "date_two_kinds_traded",
    # THE READINGS OF AN ABSORBED COUNT (plan P4-D298): a published count
    # the disclosure rule absorbed has no packing, and the method answers
    # it with a reading the rule publishes the same way.
    "free_text_absorbed_figures",
    "identifier_absorbed_figure",
    "judged_stand_in_written",
    "saturated_representable",
    "unmarked_duplicates_first",
)

# The six cases of the carried numbers pass of 2026-09-18 and its repair
# pass of 2026-09-19: G6.5a's band fill, the mode's own stratum (plan
# P4-D267), G8.3a's dressing and anchors (plan P4-D268), G6.5a's push of a
# collision the walks leave, and the column-wide fill on a column where the
# band fill and the push both stand aside. The first four were built into
# the eighth file and moved here whole at the integration of the carried
# passes, where the eighth would have passed the byte cap. Sorted, like the
# tuples above.
SEVENTH_BRANCH_CASES = (
    "held_back_anchored",
    "held_back_dressed",
    "mode_held",
    "pushed_along_band",
    "saturated_band",
    "saturated_grid_alone",
)

# THE TENTH FILE'S SIX. Four are the cases the date and clock tail
# landing grew past the room their own files had (plan P4-D328); two are
# the numeric tail rule's reading of G5.3b with its two derived ends and
# its made-up ramp of a block below its own floor (landing 3.3).
EIGHTH_BRANCH_CASES = (
    "clock_ladder",
    "midnight_bare_offsets",
    "midnight_days",
    "partial_midnight",
    # G6.5a's last resort on a representable grid with SPARE points
    # (stage 3's review, verdict item 4). It is here rather than beside
    # `saturated_representable` because plan P4-D295 routes the next
    # case to the file whose output still stands under 200000 bytes.
    "representable_with_room",
    # THE TWO THE GOVERNANCE PASS OF STAGE 3'S REVIEW ADDS, routed here
    # by plan P4-D295 because this file's output still stands under
    # 200000 bytes: G5.3e's FLOOR under each listed value (item 1),
    # which every case frozen before it answers the same counts either
    # side of, and the tail that publishes NEITHER distance, the
    # construction plan P4-D349 added and no frozen case reached.
    "tail_listed_floor",
    "tail_made_up_ramp",
    "tail_shape_ends",
    "tail_withheld_pair",
)

# THE ELEVENTH FILE: the listed tail of G5.3e and the counts solved for
# it, the sign rule of G5.5a on a derived end, the moment ladder of a
# block too thin for two tails, and -- added by the dates pass of the
# stage-3 review, item 5 -- G7A.4's hole step, which no clock case
# frozen before it reaches because none of them carries an absent
# spelling at all.
NINTH_BRANCH_CASES = (
    "clock_declared_hole",
    "mark_spend_at_the_line",
    "tail_listed_counts",
    "tail_moment_ladder",
    "tail_sign_clamped",
)

ALL_CASES = tuple(
    sorted(
        REQUIRED_CASES
        + BRANCH_CASES
        + SECOND_BRANCH_CASES
        + THIRD_BRANCH_CASES
        + FOURTH_BRANCH_CASES
        + FIFTH_BRANCH_CASES
        + SIXTH_BRANCH_CASES
        + SEVENTH_BRANCH_CASES
        + EIGHTH_BRANCH_CASES
        + NINTH_BRANCH_CASES
    )
)

# Which seed's opening words each case is given. This mapping lives here
# and not in the oracle: the oracle is a pure function of the words, and
# a seed inside it would be a random operation it is not allowed to hold.
SEEDS = {
    # The dates pass of the stage-3 review takes the next seed after the
    # highest in use.
    "clock_declared_hole": 306,
    "mark_spend_at_the_line": 307,
    "date_only": 101,
    # The review of 158c811 takes the next seeds after the highest in use.
    "date_gap_places": 141,
    "month_first_widths": 142,
    "may_month_names": 143,
    "reserved_name_floor": 144,
    "date_thinning_week": 145,
    "date_peak_heap": 146,
    "quarter": 102,
    "offset_bearing": 103,
    "mixed_parsed_unparsed": 104,
    "numeric_integer": 105,
    "numeric_decimal_styles": 106,
    "label_variants": 107,
    "identifier_fold_collisions": 108,
    "identifier_whole_numbers": 109,
    "numeric_point_free_styles": 110,
    "unrepresentable_joint": 111,
    "unrepresentable_exponent": 121,
    "free_text_joint": 112,
    "identifier_edge_spacing": 113,
    "identifier_layout": 136,
    "identifier_layout_mixes": 140,
    "identifier_absent_words": 141,
    "identifier_signed_layout": 142,
    "identifier_layout_partners": 143,
    "lower_case_stand_ins": 137,
    "level_shape_stand_ins": 138,
    "count_spellings": 139,
    "leap_second_endpoint": 114,
    "numeric_pooled_spelling": 115,
    "month_span": 116,
    "long_tail_levels": 117,
    "clock_ladder": 118,
    "affixed_brackets": 119,
    "joined_readings": 120,
    "midnight_days": 122,
    "mixed_marks": 123,
    # Landing 2b.7's own case takes the next seed after the carried
    # landings' block, which ran to 135.
    "mixed_conventions": 136,
    # The repair of the final Codex review of the number censuses takes
    # 160 onward, clear of every block the carried landings and their
    # repairs took.
    "bare_mark_remainder": 160,
    "plus_padded_field": 161,
    "pooled_mark_cells": 162,
    "saturated_integers": 163,
    "unpublished_majority_marks": 164,
    "spread_conventions": 165,
    "signed_pads": 166,
    # The repair of the carried items of landing 2b. `separated_in_order`
    # is `signed_pads` publishing eleven values, and takes its seed: the
    # opening words at that seed are the ones whose walk the reaches move.
    "separated_in_order": 166,
    "saturated_tenths": 168,
    "saturated_levels": 169,
    "grouped_thousands": 175,
    # Part 2 of the carried items takes 180 onward.
    "numbers_carry_the_average": 180,
    "date_widths_reached": 181,
    "date_distinct_reached": 182,
    "midnight_withheld_kept": 183,
    # The final pass over stage 2's close takes 190 onward.
    "grouped_thousands_signed": 176,
    # The close of landing 2b takes 192 onward.
    "code_band_words": 192,
    # The extra round's repair pass takes the next seeds after 192.
    "saturated_representable": 193,
    # Stage 3's review takes 400 onward, clear of every block above.
    "representable_with_room": 400,
    "unmarked_duplicates_first": 194,
    # The readings of an absorbed count (plan P4-D298) take 210 onward,
    # clear of every block in use.
    "free_text_absorbed_figures": 210,
    "identifier_absorbed_figure": 211,
    # THE TAIL RULE OF STAGE 3 (landing 3.3) takes 300 onward, clear of
    # every block above it.
    "tail_shape_ends": 300,
    "tail_listed_counts": 301,
    "tail_sign_clamped": 303,
    "tail_moment_ladder": 304,
    "tail_made_up_ramp": 305,
    # ...and the governance pass's two.
    "tail_listed_floor": 302,
    "tail_withheld_pair": 306,
    "identifier_unnamed_partners": 184,
    "truth_values_written": 189,
    "twice_written_filled": 190,
    "twice_written_merged": 191,
    # The extra review of c5d09d5 takes 200 onward, clear of every block
    # above it.
    "date_midnight_feasible": 200,
    "date_endpoint_ties": 201,
    "date_second_field_class": 202,
    "date_traded_merge": 203,
    "date_nonadjacent_merge": 204,
    # The carried date items of 2026-09-18 take the next two.
    "date_two_kinds_traded": 205,
    "date_two_kinds_nonadjacent": 206,
    # Its repair pass takes the next.
    "date_both_fields_disagree": 207,
    # The dates pass of the second Codex round of 2026-09-19 takes 270
    # onward, clear of every block above it, and its repair pass the two
    # after that.
    "date_midnight_traded": 270,
    "exponent_fitted": 271,
    "exponent_scaled": 272,
    # G7.9's absorbed mark (plan P4-D245) takes the next, clear of every
    # block in use.
    "date_absorbed_mark": 273,
    # The carried numbers pass of 2026-09-18 takes 260 onward, clear of
    # the blocks above and of the other carried passes.
    "saturated_band": 260,
    "mode_held": 261,
    "held_back_dressed": 262,
    "held_back_anchored": 263,
    "pushed_along_band": 264,
    "saturated_grid_alone": 265,
    # G10.1's write rule with a judged stand-in (plan P4-D6.4) took the
    # next seed after the highest in use on its own branch; it shares 205
    # with date_two_kinds_traded, as the merged blocks below share theirs,
    # because its committed words are the opening words of that stream.
    "judged_stand_in_written": 205,
    # The owner's rulings of 2026-09-17 take 181 onward.
    "pooled_level_sizes": 181,
    "identifier_column_prefix": 182,
    "identifier_layout_prefixes": 183,
    "identifier_layout_packing": 167,
    # Landings 2b.4, 2b.3 and 2b.2 were built side by side and each took
    # 124 onward for its own cases. A seed only names the opening words a
    # case is given, and each case's committed cells were chosen from
    # those words, so both keep their seed rather than move to new words.
    "label_numbers": 124,
    "label_number_tiers": 125,
    "pooled_marks": 124,
    "slashed_pool": 125,
    "midnight_mixed_forms": 126,
    "partial_midnight": 127,
    "midnight_two_offsets": 128,
    "midnight_bare_offsets": 129,
    "grouped_charges": 124,
    "grouped_decimal_comma": 125,
    "spaced_brackets": 126,
    "apostrophe_minus_sign": 131,
    "quoted_trailing_minus": 132,
    "spaced_decimal_comma": 133,
    "narrow_spaced": 134,
    "thin_spaced": 135,
    # The pool's own scale (plan P4-D301) takes 280, clear of every
    # block above it.
    "pooled_number_scale": 280,
}

# The cases whose column was declared with --decimal-comma, which the
# contract's invariant GS1 binds to settings.forced_decimal_commas.
DECLARED_DECIMAL_COMMAS = frozenset({"grouped_decimal_comma", "spaced_decimal_comma"})

# The cases whose column was declared with --identifier, which the
# contract's invariant A1 binds to settings.forced_identifiers.
DECLARED_IDENTIFIERS = frozenset(
    {
        "identifier_fold_collisions",
        "identifier_whole_numbers",
        "identifier_edge_spacing",
        "identifier_layout",
        "identifier_layout_mixes",
        "identifier_absent_words",
        "identifier_signed_layout",
        "identifier_layout_partners",
        "identifier_layout_packing",
        "identifier_unnamed_partners",
        "identifier_column_prefix",
        "identifier_layout_prefixes",
        "identifier_absorbed_figure",
    }
)

def _case(name: str) -> dict:
    """One case, from whichever of the committed files carries it."""
    if name in EIGHTH_BRANCH_CASES:
        document = _eighth_branch_document()
    elif name in NINTH_BRANCH_CASES:
        document = _ninth_branch_document()
    elif name in SEVENTH_BRANCH_CASES:
        document = _seventh_branch_document()
    elif name in SIXTH_BRANCH_CASES:
        document = _sixth_branch_document()
    elif name in FIFTH_BRANCH_CASES:
        document = _fifth_branch_document()
    elif name in FOURTH_BRANCH_CASES:
        document = _fourth_branch_document()
    elif name in THIRD_BRANCH_CASES:
        document = _third_branch_document()
    elif name in SECOND_BRANCH_CASES:
        document = _second_branch_document()
    elif name in BRANCH_CASES:
        document = _branch_document()
    else:
        document = _document()
    return document["cases"][name]


def _relationships() -> dict:
    return {
        key: None
        for key in (
            "deterministic",
            "grain",
            "hierarchy",
            "keys",
            "missing_data_process",
            "statistical",
            "temporal",
            "validation_targets",
        )
    }


def _settings(declared: list, commas: "list | None" = None) -> dict:
    return {
        "small_cell_floor": 11,
        "identifier_uniqueness": 0.95,
        "identifier_minimum_rows": 0,
        "minimum_parse_rate": 0.9,
        "categorical_share": 0.5,
        "categorical_ceiling": 50,
        "categorical_floor": 1,
        "sentinel_outlier_iqr_multiple": 1.5,
        "sentinel_minimum_share": 0.02,
        "kept_values": {
            "n_declared": 0,
            "values_recorded": False,
            "built_in_texts": [],
            "built_in_dates": [],
            "built_in_numbers": [],
        },
        "declared_missing_values": {
            "n_declared": 0,
            "values_recorded": False,
            "built_in_texts": [],
            "built_in_dates": [],
            "built_in_numbers": [],
        },
        "declaration_matching": "exact_number_when_it_reads_as_one_else_spelling",
        "declaration_publication": "settings_counts_only_columns_unchanged",
        "near_threshold_slack": 0,
        "day_first": False,
        "long_tail_minimum_level": 11,
        # WHO THE ROWS ARE ABOUT (plan P4-D340). Empty on every case
        # here, which says the population was counted in ROWS: the
        # oracle's tables are columns of cells and not people's
        # records, and no case turns on a person column -- the
        # disclosure floor is counted in rows whatever this key says.
        "person_columns": [],
        "forced_identifiers": declared,
        # The second declaration (plan P4-D19). The oracle declares no
        # code column: every case here is built from the generation
        # method's own text, and none of them turns on the reading a
        # declaration changes.
        "forced_codes": [],
        # The third declaration (plan P4-D21). The oracle declares no
        # measurement column: every case here is built from the
        # generation method's own text.
        "forced_measurements": [],
        # The fourth (plan P4-D26), named for the one case frozen with
        # it (landing 2b.2): its column is grouped with a point.
        "forced_decimal_commas": [] if commas is None else commas,
        # The fifth (plan P4-D81). The oracle declares no rows of column
        # descriptions: every case here is built from the generation
        # method's own text, and none of them has a header at all.
        "forced_metadata_rows": 0,
        # The sixth (plan P4-D110). The oracle declares no delimiter: the
        # delimited cases read their own published one.
        "forced_delimiter": "",
    }


def _unwrap(node):
    """The wire value of a case's column block.

    The oracle writes every published binary64 inside a `float64` wrapper
    carrying the exact rational it stands for, because a number in that
    file with nothing proving it is the one thing the file may not hold.
    The wire value is the wrapper's own `float64` field.
    """
    if isinstance(node, dict):
        inside = node.get("float64")
        if isinstance(inside, float):
            return inside
        return {key: _unwrap(value) for key, value in node.items()}
    if isinstance(node, list):
        return [_unwrap(value) for value in node]
    return node


def _profile_document(case: dict, name: str) -> dict:
    """A whole profile document carrying one case's column and nothing else."""
    column = _unwrap(case["column"])
    declared = [column["name"]] if name in DECLARED_IDENTIFIERS else []
    commas = [column["name"]] if name in DECLARED_DECIMAL_COMMAS else []
    return {
        "columns": [column],
        "created_with": "0+unknown",
        "n_columns": 1,
        "n_rows": len(case["cells"]),
        "profile_version": 6,
        "publication_notes": [],
        "relationships": _relationships(),
        "settings": _settings(declared, commas),
        "source": {
            "dialect": dialect.document_of(
                dialect.ordinary(1, len(case["cells"]), False)
            ),
            "encoding": "utf-8-sig",
            "used_fallback_encoding": False,
            "header_source": "generated",
            "header_by_convention": False,
            "header_evidence": "the file carried no names of its own, so the "
            "columns were named for it.",
            # Every frozen case is a DELIMITED file -- one column of
            # cells written as text -- so it carries no workbook block
            # (plan P4-D77, contract 4.3b). The key is required of every
            # description, and `null` is what a description of delimited
            # text says there. The one exception carries a census of
            # truth values, which only a workbook publishes (plan P4-D198).
            "workbook": _truth_workbook(case, column),
        },
    }


def _truth_workbook(case: dict, column: dict) -> "dict | None":
    """The workbook block of a case carrying a census of truth values.

    None for every other case. For such a case: one sheet, the column's
    cells counted as numbers, text and the truth values, all in the
    general format -- the block the producer writes for such a book.
    """
    if "workbook_truths" not in case:
        return None
    rows = len(case["cells"])
    truths = case["workbook_truths"]
    classes = {kind: 0 for kind in workbook.CELL_CLASSES}
    classes["number"] = column["n_numeric"]
    classes["text"] = column["n_not_numeric"] - truths
    classes["boolean"] = truths
    kinds = {kind: 0 for kind in workbook.FORMAT_KINDS}
    kinds["plain"] = rows
    return {
        "autofilter": False,
        "columns": [
            {
                "cell_classes": classes,
                "format_code": "General",
                "format_kinds": kinds,
                "formulas": None,
                "value_class": "text",
            }
        ],
        "date_system": "1900",
        "defined_names": 0,
        "defined_table": False,
        "empty_rows_inside": None,
        "frozen_rows": 0,
        "macro_project": False,
        "rows_above_header": 0,
        "sheet_count": 1,
        "sheet_extents": [None],
        "sheet_hidden": False,
        "sheet_names": [None],
        "sheet_position": 1,
        "trailing_blank_columns": 0,
        "trailing_blank_rows": 0,
    }


def _load(case: dict, name: str, folder: pathlib.Path) -> contract.Profile:
    path = fixtures.write_profile(
        folder, f"{name}.json", _profile_document(case, name)
    )
    return contract.load_profile(str(path))


def _words(count: int, seed: int) -> list:
    """The opening ``count`` words of the single stream at ``seed``.

    Exactly the draw form method section G3.2 fixes and no other: the
    whole of 0 .. 2**64 - 1 inclusive at both ends, the type named by the
    string "uint64", every element converted to a first-party whole
    number before any other use.
    """
    stream = numpy.random.default_rng(seed)
    return [
        int(word)
        for word in stream.integers(
            0, 18446744073709551615, size=count, dtype="uint64", endpoint=True
        )
    ]


# ----------------------------------------------- what the oracle says it is


def test_the_oracle_is_present_and_says_what_it_is() -> None:
    document = _document()
    assert document["never_imports"] == ["synthtwin", "numpy", "pandas"]
    assert document["method"] == "docs/spec/generation-method-v1.md"
    assert document["method_revision"] == 1
    assert tuple(sorted(document["cases"])) == REQUIRED_CASES


def test_the_branch_file_is_the_same_oracle_and_says_which_half_it_is() -> None:
    """No file may be read as the whole of the oracle.

    The ten carry disjoint case sets and together carry every case
    method section G14.3 names, and each one's own account says where
    the others live -- so a reader who opens any of them is told at
    once that it is part of one artifact rather than all of it.
    """
    named = _document()
    branch = _branch_document()
    second = _second_branch_document()
    third = _third_branch_document()
    fourth = _fourth_branch_document()
    fifth = _fifth_branch_document()
    sixth = _sixth_branch_document()
    seventh = _seventh_branch_document()
    eighth = _eighth_branch_document()
    ninth = _ninth_branch_document()
    papers = _document_document()
    assert tuple(sorted(branch["cases"])) == BRANCH_CASES
    assert tuple(sorted(second["cases"])) == SECOND_BRANCH_CASES
    assert tuple(sorted(third["cases"])) == THIRD_BRANCH_CASES
    assert tuple(sorted(fourth["cases"])) == FOURTH_BRANCH_CASES
    assert tuple(sorted(fifth["cases"])) == FIFTH_BRANCH_CASES
    assert tuple(sorted(sixth["cases"])) == SIXTH_BRANCH_CASES
    assert tuple(sorted(seventh["cases"])) == SEVENTH_BRANCH_CASES
    assert tuple(sorted(eighth["cases"])) == EIGHTH_BRANCH_CASES
    assert tuple(sorted(ninth["cases"])) == NINTH_BRANCH_CASES
    assert tuple(sorted(papers["cases"])) == DOCUMENT_CASES
    every = (
        named, branch, second, third, fourth, fifth, sixth, seventh,
        eighth, ninth, papers,
    )
    for index in range(len(every)):
        for other in range(index + 1, len(every)):
            assert not set(every[index]["cases"]) & set(every[other]["cases"])
    held: "set" = set()
    for one in every:
        held = held | set(one["cases"])
    assert tuple(sorted(held)) == EVERY_CASE
    files = (
        (named, VECTORS),
        (branch, BRANCH_VECTORS),
        (second, SECOND_BRANCH_VECTORS),
        (third, THIRD_BRANCH_VECTORS),
        (fourth, FOURTH_BRANCH_VECTORS),
        (fifth, FIFTH_BRANCH_VECTORS),
        (sixth, SIXTH_BRANCH_VECTORS),
        (seventh, SEVENTH_BRANCH_VECTORS),
        (eighth, EIGHTH_BRANCH_VECTORS),
        (ninth, NINTH_BRANCH_VECTORS),
        (papers, DOCUMENT_VECTORS),
    )
    for document, own in files:
        assert document["never_imports"] == ["synthtwin", "numpy", "pandas"]
        assert document["method"] == "docs/spec/generation-method-v1.md"
        assert document["generated_by"] == (
            "tools/reference/make_generation_reference_vectors.py"
        )
        for _other, path in files:
            if path != own:
                assert f"tests/reference/{path.name}" in document["case_set"]


@pytest.mark.parametrize(
    "script",
    [
        GENERATOR,
        BRANCH_GENERATOR,
        SECOND_BRANCH_GENERATOR,
        THIRD_BRANCH_GENERATOR,
        FOURTH_BRANCH_GENERATOR,
        FIFTH_BRANCH_GENERATOR,
        SIXTH_BRANCH_GENERATOR,
        SEVENTH_BRANCH_GENERATOR,
        EIGHTH_BRANCH_GENERATOR,
        NINTH_BRANCH_GENERATOR,
        DOCUMENT_GENERATOR,
    ],
)
def test_the_oracle_imports_none_of_the_code_it_checks(script) -> None:
    """The claim in the file's own header, held up against its source.

    An oracle that imported the package, or the library whose one random
    operation the method retains, would be recomputing a value beside the
    code it checks -- which is the defect the vectors exist to prevent.
    Both entry points are held to it, because the second one runs the
    first and a forbidden import in either would reach the vectors.
    """
    source = script.read_text(encoding="utf-8")
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped.startswith(("import ", "from ")):
            continue
        module = stripped.split()[1].partition(".")[0]
        assert module not in ("synthtwin", "numpy", "pandas"), stripped


def test_the_guard_refuses_the_import_that_shapes_the_oracle() -> None:
    """Why the oracle may not use numpy, checked rather than asserted.

    The reason is mechanical, not stylistic: every fixture generator runs
    under an audit hook that refuses `ctypes`, and numpy imports
    `ctypes`, so a generator that imported numpy would be stopped before
    it wrote a byte. Both halves are checked here, because the design of
    the whole vector file rests on them.
    """
    guard = importlib.util.spec_from_file_location(
        "guard_runner", REPOSITORY / "tools" / "provenance" / "guard_runner.py"
    )
    runner = importlib.util.module_from_spec(guard)
    guard.loader.exec_module(runner)
    assert "ctypes" in runner.BLOCKED_IMPORT_MODULES
    assert runner.import_is_blocked("ctypes")
    assert runner.import_is_blocked("ctypes.util")
    # And numpy really does reach for it: this module of numpy's own
    # holds the module object the guard refuses.
    assert numpy.ctypeslib.ctypes.__name__ == "ctypes"
    assert "ctypes" in sys.modules


# ------------------------------------------- the words the cases are given


@pytest.mark.parametrize("name", ALL_CASES)
def test_the_given_words_are_the_opening_words_of_one_stream(name: str) -> None:
    """The vectors take words as inputs; this is what binds them to a run.

    The oracle holds no generator, so nothing inside it could make this
    true. Asserting it here is what lets the same case be handed to
    `generate` and compared cell for cell.
    """
    case = _case(name)
    given = [int(word) for word in case["words"]]
    assert given == _words(len(given), SEEDS[name])


@pytest.mark.parametrize("name", ALL_CASES)
def test_the_word_sequence_does_not_depend_on_how_the_calls_are_cut(
    name: str,
) -> None:
    """The property method section G3.3 rests on, re-checked every run.

    The implementation makes one call per stage; the full-width range
    needs no rejection and no buffering, so drawing the content words and
    the placement words in two calls yields the same sequence as one. A
    library change that broke this would turn this test red rather than
    move a twin.
    """
    case = _case(name)
    budget = case["word_budget"]
    seed = SEEDS[name]
    together = _words(budget["content"] + budget["placement"], seed)
    stream = numpy.random.default_rng(seed)
    apart = []
    for size in (budget["content"], budget["placement"]):
        if not size:
            continue
        apart.extend(
            int(word)
            for word in stream.integers(
                0, 18446744073709551615, size=size, dtype="uint64", endpoint=True
            )
        )
    assert together == apart
    assert [int(word) for word in case["words"]] == together


# ------------------------------ the implementation against the committed cells


@pytest.mark.parametrize("name", ALL_CASES)
def test_the_implementation_writes_the_committed_cells(
    name: str, tmp_path: pathlib.Path
) -> None:
    """Cell for cell, and then byte for byte, against a value it did not make.

    All forty bind normally, with no exception of any kind. The one
    that once did not was `identifier_edge_spacing` (review item
    P2-C4-F4): the column publishes four raw spellings, one folded
    identity and the length range 1 to 3, in figures alone, so every
    partner comes from the edge spacing of method section G9.3. Both
    sides pinned the identity `1` at the shortest published length and
    the partner `1  ` at the longest, and parted company on the other
    two -- the oracle writing `1 ` and then ` 1`, the implementation
    ` 1` and then ` 1 `, leaving `1 ` unwritten. Both columns satisfy
    every published fact, so the loss was never fidelity: it was the
    property this whole artifact exists for, that an independent
    implementer working from the text alone writes the same bytes. G9.3
    step 2 now states which member of the family a slot takes -- the
    first one the column has not written whose length the slot's own
    window admits, with the family walked from its start for every slot
    -- and the committed bytes are what that rule produces. A strict
    expected failure was never a substitute for it: an expected failure
    records a disagreement, and this file exists to end one.
    """
    case = _case(name)
    profile = _load(case, name, tmp_path)
    twin = generation.generate(profile, SEEDS[name])
    written = [row[0] for row in twin.rows]
    assert written == case["cells"], (
        f"{name}: the twin's cells are not the ones the method requires. The "
        "oracle is the specification's answer; do not change it to match the "
        f"implementation. The content list this case requires, before "
        f"placement, is {case['content']}, and the written column is "
        f"{case['cells']}."
    )
    assert rendering.twin_csv(twin) == case["csv_bytes"]


@pytest.mark.parametrize("name", ALL_CASES)
def test_the_word_budget_of_the_method_is_the_budget_the_run_spends(
    name: str, tmp_path: pathlib.Path
) -> None:
    """Conformance item 3: the count per column matches G4.3 exactly.

    Asserted for every case as a claim of its own: a disagreement about
    which values a column holds is a different failure from a
    disagreement about how many words it consumes, and keeping them
    apart is what says the two are unrelated. The identifier case proved
    the point while it was still failing on its cells -- its word budget
    was right throughout, and the repair to its cells did not move it.
    """
    case = _case(name)
    budget = case["word_budget"]
    assert budget["content"] + budget["placement"] == len(case["words"])
    profile = _load(case, name, tmp_path)
    twin = generation.generate(profile, SEEDS[name])
    outcome = twin.outcomes[0]
    assert (outcome.content_words, outcome.placement_words) == (
        budget["content"],
        budget["placement"],
    )
    assert twin.words_drawn == len(case["words"])


@pytest.mark.parametrize("name", ALL_CASES)
def test_every_committed_cell_reads_back_as_the_class_it_was_built_for(
    name: str,
) -> None:
    """The class-preserving claim of G10.2, checked on the oracle's own text.

    Each of the four classes has its own construction, and each
    construction's output must classify back into its own class through
    the shipped classifier. That is a property of the cells the method
    requires, so it is asserted over the committed vectors rather than
    over whatever the implementation happened to write.

    Asked of the CONTENT list -- the present cells, before the absent ones
    join them -- because since plan P4-D6.4 an absent cell can hold a
    judged stand-in such as `-999`, which reads as a number and is counted
    in no class of the column. The content and the absent cells are held
    to the written column by the arrangement test above.
    """
    case = _case(name)
    column = _unwrap(case["column"])
    counted = dict.fromkeys(
        (
            parsing.NUMBER,
            parsing.NUMBER_OUT_OF_RANGE,
            parsing.NUMBER_CONTRADICTORY,
            parsing.NOT_A_NUMBER,
        ),
        0,
    )
    for cell in case["content"]:
        if cell == "":
            continue
        # A declared column's cells read in its own grammar, as the
        # profiler read the column the case describes (P4-D26).
        if name in DECLARED_DECIMAL_COMMAS:
            cell = parsing.written_with_a_decimal_comma(cell)
        counted[parsing.classify_number(cell)] += 1
    assert counted[parsing.NUMBER] == column["n_numeric"]
    assert counted[parsing.NUMBER_OUT_OF_RANGE] == column["n_out_of_range"]
    assert counted[parsing.NUMBER_CONTRADICTORY] == column["n_contradictory"]
    assert counted[parsing.NOT_A_NUMBER] == column["n_not_numeric"]


@pytest.mark.parametrize("name", ALL_CASES)
def test_the_committed_cells_are_the_content_list_arranged(name: str) -> None:
    """G4.2, checked inside the vectors themselves.

    The written column is the content list plus the absent cells, placed
    by one arrangement. That makes the two lists the same multiset, which
    is a property no seed can change and the one thing a wrong
    arrangement cannot fake. The absent cells are G10.1's: each published
    `missing_by_source` spelling at its count, a judged pass's included
    (plan P4-D6.4), and every other one empty.
    """
    case = _case(name)
    column = _unwrap(case["column"])
    assert len(case["content"]) == column["n_present"]
    absent: list = []
    holes = column.get("missing_by_source") or {}
    for spelling in sorted(holes):
        absent += [spelling] * holes[spelling]
    absent += [""] * (column["n_missing"] - len(absent))
    assert sorted(case["cells"]) == sorted(list(case["content"]) + absent)
    # A CELL HOLDING A COMMA IS QUOTED, which no committed cell did until
    # landing 2b.2 froze a column grouped with one: the rule is G2's, and
    # a quote inside a cell would be doubled, which no case writes.
    expected = "".join(
        ('""' if cell == "" else f'"{cell}"' if "," in cell else cell) + "\n"
        for cell in case["cells"]
    )
    assert case["csv_bytes"] == expected


# ---------------------------------------------------- the proof layer itself


PUBLISHED_NUMBERS = 210
NAMED_COUNTS = 270
BRANCH_PUBLISHED_NUMBERS = 23
BRANCH_NAMED_COUNTS = 121
SECOND_BRANCH_PUBLISHED_NUMBERS = 336
SECOND_BRANCH_NAMED_COUNTS = 370
THIRD_BRANCH_PUBLISHED_NUMBERS = 1083
THIRD_BRANCH_NAMED_COUNTS = 339
FOURTH_BRANCH_PUBLISHED_NUMBERS = 864
FOURTH_BRANCH_NAMED_COUNTS = 270
# The seventh file's floor was measured again at the repair pass of the
# second Codex round (2026-09-19), which added `exponent_scaled` and
# `exponent_fitted` to it: 623 and 254 with the six cases before them.
FIFTH_BRANCH_PUBLISHED_NUMBERS = 626
FIFTH_BRANCH_NAMED_COUNTS = 342
# The eighth and ninth floors were measured again at the integration of
# the carried passes of 2026-09-18 and 2026-09-19, when the numbers pass's
# four cases moved whole from the eighth file to the ninth: each file's
# floor is what its own rebuilt proof reports, so the numbers those four
# publish are held by the ninth file's floor rather than the eighth's.
SIXTH_BRANCH_PUBLISHED_NUMBERS = 321
SIXTH_BRANCH_NAMED_COUNTS = 365
SEVENTH_BRANCH_PUBLISHED_NUMBERS = 866
SEVENTH_BRANCH_NAMED_COUNTS = 357
# The tenth file's four cases publish the two distances of each tail
# they carry and nothing else that is a number rather than a count.
EIGHTH_BRANCH_PUBLISHED_NUMBERS = 16
EIGHTH_BRANCH_NAMED_COUNTS = 110
# The document file publishes NO binary64 at all, and that is a fact
# about its transforms rather than a gap in its proof: the written form,
# the arrangement, the workbook writer, the shape of a line before a
# table and the reading of a delimiter produce bytes and counts and
# never a measurement. Its whole-number floor is what holds it: every
# count it publishes is named among the oracle's own whole-number
# fields, and a number at any other path stops the run.
DOCUMENT_PUBLISHED_NUMBERS = 0
DOCUMENT_NAMED_COUNTS = 70

# Each committed file, with the floors its own proof must clear and the
# case set the oracle writes it from.
COMMITTED_FILES = (
    (VECTORS, None, PUBLISHED_NUMBERS, NAMED_COUNTS),
    (BRANCH_VECTORS, gen.BRANCH_PART, BRANCH_PUBLISHED_NUMBERS, BRANCH_NAMED_COUNTS),
    (
        SECOND_BRANCH_VECTORS,
        gen.SECOND_BRANCH_PART,
        SECOND_BRANCH_PUBLISHED_NUMBERS,
        SECOND_BRANCH_NAMED_COUNTS,
    ),
    (
        THIRD_BRANCH_VECTORS,
        gen.THIRD_BRANCH_PART,
        THIRD_BRANCH_PUBLISHED_NUMBERS,
        THIRD_BRANCH_NAMED_COUNTS,
    ),
    (
        FOURTH_BRANCH_VECTORS,
        gen.FOURTH_BRANCH_PART,
        FOURTH_BRANCH_PUBLISHED_NUMBERS,
        FOURTH_BRANCH_NAMED_COUNTS,
    ),
    (
        FIFTH_BRANCH_VECTORS,
        gen.FIFTH_BRANCH_PART,
        FIFTH_BRANCH_PUBLISHED_NUMBERS,
        FIFTH_BRANCH_NAMED_COUNTS,
    ),
    (
        SIXTH_BRANCH_VECTORS,
        gen.SIXTH_BRANCH_PART,
        SIXTH_BRANCH_PUBLISHED_NUMBERS,
        SIXTH_BRANCH_NAMED_COUNTS,
    ),
    (
        EIGHTH_BRANCH_VECTORS,
        gen.EIGHTH_BRANCH_PART,
        EIGHTH_BRANCH_PUBLISHED_NUMBERS,
        EIGHTH_BRANCH_NAMED_COUNTS,
    ),
    (
        SEVENTH_BRANCH_VECTORS,
        gen.SEVENTH_BRANCH_PART,
        SEVENTH_BRANCH_PUBLISHED_NUMBERS,
        SEVENTH_BRANCH_NAMED_COUNTS,
    ),
    (
        DOCUMENT_VECTORS,
        gen.DOCUMENT_PART,
        DOCUMENT_PUBLISHED_NUMBERS,
        DOCUMENT_NAMED_COUNTS,
    ),
)


def _fields(document: dict) -> frozenset:
    return gen.whole_number_fields(document)


@pytest.mark.parametrize(
    "committed,part,published,named", COMMITTED_FILES, ids=["named", "branches", "branches-2", "branches-3", "branches-4", "branches-5", "branches-6", "branches-8", "branches-7", "documents"]
)
def test_the_committed_file_publishes_no_number_that_escapes_the_proof(
    committed, part, published, named
) -> None:
    """Every number in the file, one by one, read back off the disk.

    The proof is only as wide as the walk that feeds it, so this reads
    the committed bytes and checks that nothing written as a number sits
    anywhere but in a `float64` wrapper holding a binary64 value or at
    one of the whole-number paths the generator names.
    """
    document = json.loads(committed.read_text(encoding="utf-8"))
    allowed = _fields(document)
    measurements = 0
    counts = 0
    for path, value in gen._published_numbers(document, (), gen.SECTION_FIELDS):
        if path in gen.DOCUMENT_TEXT_FIELDS:
            assert isinstance(value, str), gen._where(path)
            continue
        if path[-1] == "float64":
            assert isinstance(value, float), (
                f"{gen._where(path)} carries {value!r}, which is not a "
                "binary64 value, so the proof could not be applied to it"
            )
            measurements += 1
        else:
            assert path in allowed, (
                f"{gen._where(path)} publishes {value!r} outside a 'float64' "
                "field and is not one of the named counts"
            )
            assert isinstance(value, int) and not isinstance(value, bool)
            counts += 1
    assert measurements >= published, (
        f"the file now publishes {measurements} proved numbers, fewer than "
        f"the {published} it carried when this floor was written; a "
        "field has left the file"
    )
    assert counts >= named


@pytest.mark.parametrize(
    "committed,part,published,named", COMMITTED_FILES, ids=["named", "branches", "branches-2", "branches-3", "branches-4", "branches-5", "branches-6", "branches-8", "branches-7", "documents"]
)
def test_the_committed_bytes_are_proved_against_the_recorded_exact_values(
    committed, part, published, named
) -> None:
    """The file as it sits on disk, put through the proof it claims to carry."""
    _document_in_memory, claims = gen.build_document(part)
    document = json.loads(committed.read_text(encoding="utf-8"))
    proved = gen.prove_every_published_float(
        document,
        claims,
        _fields(document),
        gen.DOCUMENT_TEXT_FIELDS,
        gen.SECTION_FIELDS,
    )
    assert proved >= published


@pytest.mark.parametrize(
    "committed,part,published,named", COMMITTED_FILES, ids=["named", "branches", "branches-2", "branches-3", "branches-4", "branches-5", "branches-6", "branches-8", "branches-7", "documents"]
)
def test_the_generator_says_how_many_numbers_it_proved(
    tmp_path, capsys, committed, part, published, named
) -> None:
    """The count is reported, and it is the count of what the file holds.

    Tying the reported number to the rebuilt file is what stops the
    report from being a constant. The rebuilt bytes are compared with the
    committed ones as well -- the provenance guard's own check, restated
    here so that a change to the proof layer that moved a number is
    visible in this suite too.
    """
    rebuilt = tmp_path / committed.name
    assert gen.main(["--seed", "0", "--out", str(rebuilt)], part=part) == 0
    reported = capsys.readouterr().err
    document = json.loads(rebuilt.read_text(encoding="utf-8"))
    measurements = sum(
        1
        for path, _value in gen._published_numbers(document, (), gen.SECTION_FIELDS)
        if path[-1] == "float64" and path not in gen.DOCUMENT_TEXT_FIELDS
    )
    counts = sum(
        1
        for path, _value in gen._published_numbers(document, (), gen.SECTION_FIELDS)
        if path[-1] != "float64"
    )
    assert measurements >= published
    assert counts >= named
    assert f"proved {measurements} published numbers" in reported
    assert f"beside {counts} named whole-number counts" in reported
    assert rebuilt.read_bytes() == committed.read_bytes()


def test_a_value_past_the_overflow_boundary_is_not_certified() -> None:
    """The boundary the bracketing comparison cannot see on its own."""
    with pytest.raises(AssertionError) as refusal:
        gen.prove_nearest_float(gen.F(1 << 1024), sys.float_info.max)
    assert "infinity" in str(refusal.value)
    gen.prove_nearest_float(gen.F(sys.float_info.max), sys.float_info.max)


def test_the_sign_of_a_zero_is_read_from_its_bit() -> None:
    """`+0.0 == -0.0`, so a numeric sign test says nothing about which is which."""
    with pytest.raises(AssertionError) as refusal:
        gen.prove_nearest_float(gen.F(-1, 1 << 2000), 0.0)
    assert "sign" in str(refusal.value)
    gen.prove_nearest_float(gen.F(-1, 1 << 2000), -0.0)
    with pytest.raises(AssertionError):
        gen.prove_exact_float(gen.F(0), -0.0)
    assert gen.sign_bit_is_set(-0.0) is True
    assert gen.sign_bit_is_set(0.0) is False


def test_the_exact_claim_refuses_a_value_that_was_rounded() -> None:
    """`exact` is the stronger claim, and it is held to being stronger.

    A value the transform reaches without rounding must be published as
    exactly the rational recorded beside it. The weaker "nearest" claim
    would pass any float held up against its own exact value, so a field
    that quietly started rounding would go unnoticed.
    """
    gen.prove_exact_float(gen.F(5, 4), 1.25)
    with pytest.raises(AssertionError) as refusal:
        gen.prove_exact_float(gen.F(1, 3), 0.3333333333333333)
    assert "exactly" in str(refusal.value)


def test_the_walk_refuses_a_number_with_nothing_proving_it() -> None:
    published = {"value": {"float64": 1.0}, "loose": 2.0}
    claims = {("value",): (gen.NEAREST, gen.F(1))}
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float(published, claims)
    assert "nothing proved it" in str(refusal.value)


def test_the_walk_refuses_a_wrapper_with_no_exact_value_recorded() -> None:
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float({"value": {"float64": 1.0}}, {})
    assert "no exact value" in str(refusal.value)


def test_the_walk_refuses_a_whole_number_under_a_wrapper() -> None:
    """JSON writes a Python int and a float as the same kind of thing."""
    claims = {("value",): (gen.NEAREST, gen.F(1, 3))}
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float({"value": {"float64": 7}}, claims)
    assert "binary64" in str(refusal.value)


def test_the_walk_refuses_an_exact_value_that_nothing_spends() -> None:
    """The match is one-to-one, so a skipped field cannot hide behind a claim."""
    published = {"value": {"float64": 0.5}}
    claims = {
        ("value",): (gen.NEAREST, gen.F(1, 2)),
        ("absent",): (gen.NEAREST, gen.F(0)),
    }
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float(published, claims)
    assert "absent" in str(refusal.value)


def test_a_number_inside_a_tuple_is_not_skipped() -> None:
    """P1-R8-F3: the encoder writes a tuple as an array exactly as a list."""
    published = {"new_field": (7.0,)}
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float(published, {})
    assert "nothing proved it" in str(refusal.value)
    assert "new_field.0" in str(refusal.value)
    assert json.dumps(published, allow_nan=False) == '{"new_field": [7.0]}'


@pytest.mark.parametrize(
    "value",
    [{7.0}, frozenset({7.0}), b"\x07", bytearray(b"\x07"), 3 + 4j],
)
def test_a_shape_the_walk_has_no_rule_for_stops_the_run(value: object) -> None:
    """Fail closed: what the walk does not recognise is where a number hides."""
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float({"odd": value}, {})
    assert "no rule for" in str(refusal.value)


def test_a_key_that_is_not_text_stops_the_run() -> None:
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float({"a": {1.5: 0.5}}, {})
    assert "not text" in str(refusal.value)


def test_the_section_named_float64_is_still_walked_into() -> None:
    """The one exemption, and the mutant that would use it as a hiding place.

    A case's chain of interior values is published under the same word
    the value wrapper uses, so the walk is told to descend there instead
    of handing the section over. Descending is the point: a bare number
    put directly inside a section is still refused.
    """
    section = frozenset({("cases", "one", "float64")})
    document = {"cases": {"one": {"float64": [{"value": {"float64": 0.5}}]}}}
    claims = {("cases", "one", "float64", 0, "value"): (gen.NEAREST, gen.F(1, 2))}
    assert (
        gen.prove_every_published_float(
            document, claims, frozenset(), frozenset(), section
        )
        == 1
    )
    smuggled = {"cases": {"one": {"float64": [7.0]}}}
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float(
            smuggled, {}, frozenset(), frozenset(), section
        )
    assert "nothing proved it" in str(refusal.value)


# Each row is a field added to every case, and what the refusal must
# say. The encoder writes each of these tuples as a JSON array, so every
# one of them really would have reached the file.
GENERATOR_MUTANTS = (
    ((7.0,), "nothing proved it"),
    ((7,), "no rule for"),
    (({"float64": 7.0},), "no exact value"),
    (({"float64": 7},), "binary64"),
    ({7.0}, "no rule for"),
)


@pytest.mark.parametrize("added,refusal_says", GENERATOR_MUTANTS)
def test_a_field_added_to_every_case_stops_the_generator(
    tmp_path, monkeypatch, added: object, refusal_says: str
) -> None:
    """The mutant driven through the whole generator, where the review ran it.

    Checking the committed fixture after a rebuild would not catch this:
    the fixture holds no such field. So the mutant goes through `main`,
    and nothing may be written.
    """
    real = gen.build_case

    def with_one_more(name):
        case, claims = real(name)
        case["added_later"] = added
        return case, claims

    monkeypatch.setattr(gen, "build_case", with_one_more)
    out = tmp_path / "vectors.json"
    with pytest.raises(AssertionError) as refusal:
        gen.main(["--seed", "0", "--out", str(out)])
    assert refusal_says in str(refusal.value)
    assert not out.exists(), "the file was written although a number was unproved"


def test_the_generator_refuses_to_write_when_its_own_mutant_is_certified(
    tmp_path, monkeypatch
) -> None:
    """The self-check is not decoration: a proof layer that passes it stops.

    The run drives a full-generator mutant through the proof layer before
    it serializes anything. Weakening the layer so the mutant is
    certified must stop the run rather than produce a file whose claim is
    no longer true.
    """
    monkeypatch.setattr(
        gen,
        "prove_every_published_float",
        lambda *args, **kwargs: 0,
    )
    out = tmp_path / "vectors.json"
    with pytest.raises(AssertionError) as refusal:
        gen.main(["--seed", "0", "--out", str(out)])
    assert "certified by the proof layer" in str(refusal.value)
    assert not out.exists()


def test_the_generator_checks_its_own_calendar_and_its_own_digits(
    monkeypatch,
) -> None:
    """Two foundations no case can check, checked before any case is built.

    A wrong leap rule leaves a civil-date round trip self-consistent, and
    the shortest round-trip digits are the generator's own rather than
    the interpreter's, so each is held up against an outside answer. A
    check that cannot fail is a defect, so it is made to fail here.
    """
    gen._self_check_arithmetic()
    calendar = gen.days_from_civil
    monkeypatch.setattr(
        gen, "days_from_civil", lambda year, month, day: calendar(year, month, day) + 1
    )
    with pytest.raises(AssertionError) as refusal:
        gen._self_check_arithmetic()
    assert "proleptic Gregorian" in str(refusal.value)



# ------------------------------------ every case, with its own branch reverted


# G14.3 requires EVERY case to fail when the branch it exists for is
# removed or reverted, and review item P2-C4-C2 found four of thirteen
# carrying such a mutant and nine carrying none. Four with and ten
# without is the same gap in a quieter form: a case whose own rule can
# be withdrawn while every committed byte stays where it was proves
# nothing about that rule, and that is exactly how the ninth case's
# branch carried a withdrawn rule for two rounds.
#
# So the mutants are ONE TABLE. Its keys are asserted equal to the whole
# case set below, which is what stops a case from being added without
# one; each entry replaces one named piece of the oracle with the rule
# its case exists to rule out; and each must either move that case's
# cells or stop the oracle from building it. Every entry builds its case
# UNMUTATED first, so a mutant that would have refused for some reason
# of its own cannot pass by refusing.


CHANGES_THE_CELLS = "changes the cells"


def _nothing_placed_at_the_pools_scale(*_arguments):
    """Method G8.3c withdrawn: no group is placed at the pool's scale.

    What the state before plan P4-D301 was, exactly: the description
    said how many held-back levels there were and how many rows they
    covered and nothing about what they were worth, so every one of them
    fell to the ordinary walk of G8.3a step 3.
    """
    return {}


def _partners_with_no_unnamed_quota(column, *arguments):
    """Plan P4-D196 withdrawn: the unnamed cells read as without end."""
    return gen_layout_preferences(dict(column, n_present=10**9), *arguments)


def _marks_on_the_positive_side_alone(column, *arguments):
    """Plan P4-D194 withdrawn: the census of marks asked of positives only."""
    unsigned = dict(column)
    unsigned["n_negative"] = 0
    return gen_grouped_enough(unsigned, *arguments)


# -- the rival rules the tails could have taken (stage 3, plan P4-D328)
#
# Four cases were frozen for branches the stage-3 format puts out of
# their reach: a column publishes no end any more, so a rank tied at an
# end is nothing to hold, and a column whose outer cells stand in a tail
# no longer falls short of a distinct count the way the mark spend and
# the two merges were witnessed by. Each of those cases now holds up a
# rule of the TAILS instead -- machinery this landing added, which needs
# a frozen witness of its own -- and the coverage each one leaves is
# stated in the method's G14.3 beside its row rather than left to be
# discovered.


# The real rules, bound before any mutant replaces them, so a rival
# that keeps part of one calls what the method states and not itself.
_real_tail_distances = gen.tail_distances
_real_tail_step = gen.tail_step_of
_real_ramp_places = gen.ramp_places


def _stratum_end_instead(shape, rows, mean, root, edge):
    """G7.3b step 3 withdrawn: the end at its stratum's root-mean-square.

    The rival the clause names and measures: instead of solving both
    moment equations together, the outermost rank stands at the
    root-mean-square of the shape over its own stratum and the ranks
    inside it are not stretched at all. It is what the tail did before
    the moment-matched end, and on a lone far value it misses the
    published mean square by 14 to 22 per cent.
    """
    inner = (rows - 1) / rows
    end = math.sqrt(
        max(rows * (gen.squares_upto(shape, 1.0) - gen.squares_upto(shape, inner)), 0.0)
    )
    return 1.0, min(end, float(edge))


def _never_apart(rows, mean, root, floor, edge, apart, words):
    """G7.3b step 5's two-pass step withdrawn: the tail may fold onto one value.

    The ranks are raised to the one inside them and no further, so a
    column whose own values were all different comes back holding two
    of its tail's ranks on one value.
    """
    return _real_tail_distances(rows, mean, root, floor, edge, False, words)


def _no_day_of_room(column):
    """G7.3b step 8's widening withdrawn: a tail rank keeps its stratum alone.

    Where one tail unit is a day of the shared clock the rank's room is
    the whole day it may be moved inside; the mutant leaves it the two
    distances its own construction gives it, and the move onto a local
    midnight has nowhere to take it.
    """
    step, _half = _real_tail_step(column)
    return step, 0


def _ramp_over_the_ranks(column, parsed):
    """G7.3d's step count withdrawn: the ramp spread over the RANKS.

    The rule puts rank `P - 1` at `D - 1` steps from 1970-01-01, `D` the
    column's published count of different values; the mutant puts it at
    `P - 1` steps, so the ramp spreads one rank to a step and the counts
    of different values, of widths and of marks are reached elsewhere or
    not at all.
    """
    step = 86400 if gen.ordinal_space(column) == "datetime" else 1
    pins = {0: 0}
    if parsed >= 2:
        pins[parsed - 1] = (parsed - 1) * step
    return pins


def _ramp_from_one(column, parsed):
    """G7.3d's START withdrawn: the ramp begins one step later.

    Rank nought stands at 1970-01-01, ordinal nought in every space of
    G7.1, and the mutant starts the whole ramp one step along -- which is
    the same shape a step later, and every cell of the column moves.
    """
    pins = dict(_real_ramp_places(column, parsed))
    for rank in sorted(pins):
        pins[rank] = pins[rank] + 1
    return pins


def _always_apart(rows, mean, root, floor, edge, apart, words):
    """G7A.4's CONDITION withdrawn: every tail kept apart, all-different or not.

    The two-pass step belongs to a column whose own values all differ;
    the mutant runs it on every column, so a tail whose real cells
    shared a value comes back holding as many different ones as it has
    ranks.
    """
    return _real_tail_distances(rows, mean, root, floor, edge, True, words)


def _no_fold_guard(rows, mean, root, floor, edge, apart, words):
    """G7.3b step 5's ordering withdrawn: each rank at its own stratum alone.

    The distances are left exactly as the shape gives them, with no rank
    raised to the one inside it, so a tail can fold back on itself where
    two neighbouring strata round to the same whole unit.
    """
    shape = gen.mixture_of(rows, mean, root)
    stretch, end = gen.stretched_end(shape, rows, mean, root, edge)
    found = [min(max(1, gen.whole_unit(end)), edge)]
    for index in range(1, rows):
        word = words.get(index, 0)
        share = ((rows - 1 - index) * gen.TWO64 + word) / (rows * gen.TWO64)
        found.append(
            min(max(1, gen.whole_unit(stretch * gen.mixture_at(shape, share))), edge)
        )
    return found


class Mutant(typing.NamedTuple):
    """One case's own branch, put back the way the method rules out.

    ``also`` names further attributes the SAME rule is stated in, each
    with its replacement, withdrawn together with ``attribute``. It is
    empty for every case but two: G6.5a's fill of a grid with no spare
    point is stated column-wide (plans P4-D147 and P4-D176) and, since the
    carried numbers pass of 2026-09-18, band by band as well -- on a
    column of one sign the band fill IS the column fill, so withdrawing
    the column-wide statement alone left the band fill writing the same
    cells, and the two cases that pin the fill stopped holding it up.
    Since the repair pass of 2026-09-19 the push of G6.5a reaches the
    same assignment on a grid of tenths with no spare point, so the tenths
    case withdraws it on a written grid too. EACH STATEMENT IS ALSO HELD UP
    ALONE, by a case whose mutant withdraws it and nothing else:
    `saturated_grid_alone` for the column-wide fill, `saturated_band` for
    the band fill and `pushed_along_band` for the push.
    """

    branch: str
    attribute: str
    replacement: object
    outcome: str
    also: tuple = ()


def _only_when_saturated(total, bands, values):
    """G6.5a's last resort as it stood before stage 3's review.

    The fill ran only where the two published ends hold EXACTLY as many
    representable numbers as the column has strata; three spare numbers
    withdrew it whole, which verdict item 4 measured as 100 subnormal
    cells coming back as 82 different numbers.
    """
    if total < 3 or not values or not math.isfinite(values[0]):
        return None
    if values[0] <= 0.0:
        return None
    ceiling = values[total - 1]
    if not math.isfinite(ceiling) or ceiling <= values[0]:
        return None
    grid = [values[0]]
    for _each in range(total - 1):
        step = gen.next_representable(grid[-1])
        if step is None or step > ceiling:
            return None
        grid.append(step)
    if grid[total - 1] != ceiling:
        return None
    if not all(gen._band_holds(bands[place], grid[place]) for place in range(total)):
        return None
    return grid

def _a_spend_that_never_looks_at_the_line(_wearing, _floor):
    """G7.9 item 2's last clause withdrawn: the spend counts its budget
    and never asks what the mark it spends from is left holding."""
    return True


def _no_spelling_reads_as_absent(_ordinal, _form, _absent):
    """G7A.4's hole step withdrawn: no clock value reads as no value.

    What this role did until the dates pass of the stage-3 review, item
    5, exactly: G7A.5 stepped the STAND-INS past every spelling the
    table calls absent and the parsed clock values were asked nothing at
    all, so a body rank landing on one was written as a clock time the
    twin's own reader counts as absent.
    """
    return False


def _either_field_below_ten(column, day_number, word=""):
    """G7.3's width question as it stood before plan P4-D256: does the day
    show a width AT ALL, whatever convention the census names."""
    _year, month, day = gen.civil_from_days(day_number)
    if column["format"] in gen.TEXTUAL_MEMBERS:
        return day < 10
    return month < 10 or day < 10


def _shows_it(column, day_number, word):
    """The day's width KIND as it stood before plan P4-D294: does the day
    SHOW the census's width, rather than is it COUNTED into it.

    The narrower of the two questions. It differs on the day that shows
    NO width at all, which the producer and the checker absorb into the
    column's one convention and this one counts out.
    """
    return gen.shows_a_width(column, day_number, word)


def _toward_the_later_instant(position, denominator, rungs):
    """G7.3's rounding turned over: ceiling instead of floor."""
    segment = gen.ladder_segment(position, denominator)
    above = 100 * position - gen.PCT[segment] * denominator
    width = (gen.PCT[segment + 1] - gen.PCT[segment]) * denominator
    return rungs[segment] - (
        (above * (rungs[segment + 1] - rungs[segment])) // -width
    )


def _pool_shared_evenly(held_back, rows, numbers, words, floor=11):
    """G8.3's sizes with the pool shared out evenly, its debts unread."""
    if held_back == 0:
        return []
    base = rows // held_back
    extra = rows % held_back
    return [base] * (held_back - extra) + [base + 1] * extra


def _rungs_of(column, parsed):
    """The ladder a withdrawn placement reads, from what the column publishes.

    The two TAIL BOUNDARIES stand where the two ends stood (stage 3,
    plan P4-D328) and a rung the tail rule withholds is not published at
    all, so a rule that wants eleven rungs is given the boundary in its
    place -- which is what the ladder said about those ranks before the
    tails took them.
    """
    space = gen.ordinal_space(column)
    low, high = column["low_tail"], column["high_tail"]
    if low is None or high is None:
        return [0] * len(gen.LADDER_KEYS)
    first = gen.ordinal_of(low["boundary"], space)
    last = gen.ordinal_of(high["boundary"], space)
    found = []
    for place, key in enumerate(gen.LADDER_KEYS):
        rung = column[
            "clock_percentiles" if column["role"] == "time_of_day"
            else "date_percentiles"
        ][key]
        if rung is None:
            found.append(first if place * 2 < len(gen.LADDER_KEYS) else last)
        else:
            found.append(gen.ordinal_of(rung, space))
    return found


def _stratified_ranks(column, parsed, words):
    """G7.3's WITHDRAWN placement: one cell per rank in its own stratum.

    THE RULE LANDING 2b.6 REPLACED, restored here so the case that pins
    the date form still fails when the placement rule is withdrawn. The
    two ends are pinned and no interior rung is: each interior rank is
    interpolated inside the band from `k / P` to `(k + 1) / P`, which is
    what gave every day almost exactly its expected count and put every
    published rung a day or more early.

    It spends one word per interior rank, exactly as the real rule does,
    so the mutant differs from it in WHERE the ranks land and in nothing
    else -- not in how many words the column draws, which would move
    every column generated after it and make the case fail for a second
    reason.
    """
    rungs = _rungs_of(column, parsed)
    pins = gen.date_pins(column, parsed)[0]
    ordinals = []
    for rank in range(parsed):
        if rank in pins:
            ordinals.append(pins[rank])
        else:
            ordinals.append(
                gen.interpolated_ordinal(
                    rank * gen.TWO64 + next(words), parsed * gen.TWO64, rungs
                )
            )
    return ordinals


def _inclusive_gap_draws(column, parsed, words):
    """G7.3 as it shipped at 158c811: every gap drawn over its two pinned days.

    Each rank between two pins takes one word over `[low, high]`
    inclusive, so each pinned day receives a day's share from the gap on
    either side of it. The same words go to the same ranks; only where a
    rank lands differs from the rule in force (plan P4-D130).
    """
    ordinals = [0] * parsed
    if parsed <= 0:
        return ordinals
    pins = gen.date_pins(column, parsed)[0]
    for rank, value in pins.items():
        ordinals[rank] = value
    places = sorted(pins)
    for step in range(len(places) - 1):
        below, above = places[step], places[step + 1]
        low, high = ordinals[below], ordinals[above]
        drawn = sorted(
            min(low + (next(words) * (high - low + 1)) // gen.TWO64, high)
            for _rank in range(below + 1, above)
        )
        for place, value in enumerate(drawn):
            ordinals[below + 1 + place] = value
    return ordinals


def _straightest_places_alone(pins):
    """G7.3's places with the middles never chosen (plan P4-D138).

    The heaps stay at their middles; what is withdrawn is the choice, so
    every column takes the straightest count.
    """
    ranks = sorted(pins)
    places = {rank: pins[rank] * gen.PIN_STEPS + gen.PIN_STEPS // 2 for rank in ranks}
    places[ranks[0]] = pins[ranks[0]] * gen.PIN_STEPS
    places[ranks[-1]] = pins[ranks[-1]] * gen.PIN_STEPS + gen.PIN_STEPS
    ends = {pins[ranks[0]], pins[ranks[-1]]}
    shared = {}
    for rank in ranks:
        shared[pins[rank]] = shared.get(pins[rank], 0) + 1
    for _pass in range(gen.PIN_PASSES):
        for index in range(1, len(ranks) - 1):
            here = ranks[index]
            if pins[here] not in ends and shared[pins[here]] >= 2:
                continue
            before, after = ranks[index - 1], ranks[index + 1]
            line = places[before] + (
                (here - before) * (places[after] - places[before])
            ) // (after - before)
            first = pins[here] * gen.PIN_STEPS
            places[here] = min(max(line, first), first + gen.PIN_STEPS - 1)
    return places


def _no_heap_held(pins):
    """G7.3's places with every heap moved onto the line like any pin (P4-D138)."""
    ranks = sorted(pins)
    middles = {rank: pins[rank] * gen.PIN_STEPS + gen.PIN_STEPS // 2 for rank in ranks}
    middles[ranks[0]] = pins[ranks[0]] * gen.PIN_STEPS
    middles[ranks[-1]] = pins[ranks[-1]] * gen.PIN_STEPS + gen.PIN_STEPS
    places = dict(middles)
    for _pass in range(gen.PIN_PASSES):
        for index in range(1, len(ranks) - 1):
            here = ranks[index]
            before, after = ranks[index - 1], ranks[index + 1]
            line = places[before] + (
                (here - before) * (places[after] - places[before])
            ) // (after - before)
            first = pins[here] * gen.PIN_STEPS
            places[here] = min(max(line, first), first + gen.PIN_STEPS - 1)
    if len(ranks) >= 3 and gen.bend_of_places(pins, middles) < gen.bend_of_places(pins, places):
        return middles
    return places


def _field_class_from_the_joint_words(census, which):
    """G7.5's one-field class written as the joint words pad that field.

    The census's own count of the class is ignored, which is what a
    census that folded one-field cells into the joint words amounted to
    (plan P4-D132).
    """
    words = gen.FIELD_WIDTH_FIRST if which == 1 else gen.FIELD_WIDTH_SECOND
    owed = {}
    for name in gen.FIELD_WIDTH_BOTH:
        if name in census:
            word = words[0] if gen.pair_widths(name)[which - 1] else words[1]
            owed[word] = owed.get(word, 0) + census[name]
    return owed


def _no_either_length(member, length_words=("abbreviated", "full")):
    """G7.5's name styles with the `either` length withdrawn (plan P4-D133)."""
    return _named_lengths_only(member)


_named_lengths_only = gen.month_name_styles_of


def _rotation_alone(weights, count, floor):
    """G7.5's reservation withdrawn: the smooth rotation and nothing else."""
    return gen.rotated(weights, count)


_precision_form = gen.precision_form


def _zero_based_quarter(
    ordinal, resolution, time_precision, subsecond_digits, mark="T", **written
):
    """G7.5's quarter form off by one: `2024-Q0` for the first quarter.

    The keyword arguments the reversal of owner decision 5 added --
    which member the date half is written in, and at which conventions
    (landing 2b.6) -- ride through untouched, so this mutant still
    differs from the real rule in the quarter's own figure and in
    nothing else.
    """
    if resolution == "quarter":
        return f"{1970 + ordinal // 4:04d}-Q{ordinal % 4}"
    return _precision_form(
        ordinal, resolution, time_precision, subsecond_digits, mark, **written
    )


def _month_as_a_day(
    ordinal, resolution, time_precision, subsecond_digits, mark="T", **written
):
    """G7.1's month row withdrawn: the month read in the DAY space.

    The one mistake a month invites, because both spaces count from the
    same origin and both write four figures, a dash and two more: an
    implementation that let the month fall through to the day branch
    would put a value in the column that no cell of it holds. Every
    cell moves.
    """
    if resolution == "month":
        return f"{1970 + ordinal // 12:04d}-{ordinal % 12 + 1:02d}-01"
    return _precision_form(
        ordinal, resolution, time_precision, subsecond_digits, mark, **written
    )


_offset_form = gen.offset_form


def _no_clock_conversion(offset):
    """G7.4's clock conversion made optional: the suffix without the move."""
    suffix, _shift = _offset_form(offset)
    return suffix, 0


def _reproduce_instead_of_standing_in(used, wanted):
    """G10.4 withdrawn: an unparsed cell copied from a parsed one."""
    return [min(used)] * wanted


def _through_the_ordinal_space(
    text, resolution, time_precision, subsecond_digits, shift, mark="T",
    **written,
):
    """G7.5's endpoint route withdrawn: both ends back through G7.1.

    The mark rides through unchanged, and so do the arguments the
    reversal of owner decision 5 added -- which member the date half is
    written in, and at which conventions (landing 2b.6) -- so the mutant
    differs from the real rule only in the ROUTE and never in the
    separator or the spelling.
    """
    return gen.precision_form(
        gen.ordinal_of(text, resolution) + shift,
        resolution,
        time_precision,
        subsecond_digits,
        mark,
        **written,
    )


def _marks_from_the_first_rank(column, parsed):
    """P4-D39's rotation withdrawn: the names spent from the first rank up."""
    if column["resolution"] != "datetime" or parsed == 0:
        return ["T"] * parsed
    named = {
        name: count
        for name, count in column["datetime_separators"].items()
        if name != "(withheld)"
    }
    if not named:
        return ["T"] * parsed
    order = sorted(named)
    commonest = max(order, key=lambda name: (named[name], -order.index(name)))
    marks = []
    for name in order:
        marks += [gen.MARK_OF[name]] * named[name]
    marks += [gen.MARK_OF[commonest]] * (parsed - len(marks))
    return marks[:parsed]


def _named_counts_only(column):
    """Landing 2b.3's pool withdrawn: the withheld pool back on the commonest mark."""
    return {
        name: count
        for name, count in column.get("datetime_separators", {}).items()
        if name != "(withheld)"
    }


def _three_marks_everywhere(column):
    """Landing 2b.3's permitted marks withdrawn: a slashed stamp offered all three."""
    return gen.MARKS_BY_COMMONNESS


def _every_rank_a_moment(column, parsed):
    """Owner decision 4's narrowing withdrawn: every rank written with a clock."""
    return [False] * parsed


def _no_move_onto_midnight(column, ordinals, shifts, bounds=None):
    """Landing 2b.3's move onto a midnight withdrawn: the interpolated instants kept."""
    return list(ordinals)


def _ends_alone(column, parsed):
    """The repair pass withdrawn: only the two BOUNDARY ranks settle theirs.

    The two ends went with stage 3 (plan P4-D328), so what the withdrawn
    rule leaves is the two ranks the description still names a value
    for: the low boundary and the high one, each with the offsets its
    own instant stands at a local midnight under. Every rung rank and
    every rank between two pinned ranks of one instant is left to the
    rotation, which is the defect the repair pass closed.
    """
    fixed = {}
    low, high = column.get("low_tail"), column.get("high_tail")
    if low is None or high is None or parsed == 0:
        return fixed
    for rank, text in (
        (low["rows"], low["boundary"]),
        (parsed - 1 - high["rows"], high["boundary"]),
    ):
        seconds = gen.ordinal_of(text, "datetime")
        fixed[rank] = gen.midnight_offsets(seconds, column)
    return fixed


def _days_on_either_clock(column):
    """Landing 2b.3's shared-clock rule withdrawn: counted in days on either clock."""
    if column.get("all_at_midnight", False):
        return "date"
    return column["resolution"]


_REAL_STYLED_SPELLING = gen.styled_spelling


def _grouped_at_every_order(
    style, value, integer_valued, order, mark="", negative="minus", plus=False,
    pad=-1, figures=-1,
):
    """P4-D38's order rule withdrawn: a cell that spent zeros is grouped too."""
    text = _REAL_STYLED_SPELLING(
        style, value, integer_valued, order, "", negative, plus, pad, figures
    )
    if style in ("plain", "leading_plus", "decimal"):
        return gen._group_thousands(text, mark)
    return text


def _exchange_withdrawn(content):
    """P4-D26's exchange withdrawn: a declared column keeps its point."""
    return list(content)


def _notation_withdrawn(text, notation):
    """Landing 2b.2's notation withdrawn: every negative keeps its minus."""
    return text


def _every_mark_a_comma(column):
    """Landing 2b.2's other marks withdrawn: every published mark is a comma."""
    return ","


def _plus_from_the_first_cell(count, styles, values):
    """Landing 2b.2's spread withdrawn: the plus taken from the first cell up."""
    carries = [False] * len(values)
    left = count
    for index, (style, value) in enumerate(zip(styles, values)):
        if left and style == "decimal" and not value < 0:
            carries[index] = True
            left -= 1
    return carries


def _ties_toward_zero(value):
    """G5.4's integer rule with the tie direction taken out."""
    whole = int(value)
    rest = value - float(whole)
    if rest > 0.5:
        return float(whole + 1)
    if rest < -0.5:
        return float(whole - 1)
    return float(whole)


def _a_one_digit_exponent(digits, decpt, marker):
    """G6.2's exponent form with the two-digit rule taken out."""
    body = digits[0] + ("." + digits[1:] if len(digits) > 1 else "")
    power = decpt - 1
    return f"{body}{marker}{'-' if power < 0 else '+'}{abs(power)}"


def _outward_without_the_gaps(ladder, places, position, low_ended=False, high_ended=False):
    """G8.3a's walk with its first part withdrawn: outward steps only.

    The method takes the values BETWEEN the published numbers that no
    published number holds before it steps beyond either end, because a
    held-back reading is as often inside the published span as outside
    it. This steps outward from the first position, so the largest
    held-back group is written below the smallest published number
    instead of in the gap beside it.
    """
    step = position // 2 + 1
    low = gen.rescaled(ladder["lowest"], ladder["places"], places, True) - step
    high = gen.rescaled(ladder["highest"], ladder["places"], places, False) + step
    if not ladder["anchored"]:
        low, high = -step, step
    low_held = not low_ended and gen.sign_held(low, ladder["signs"])
    high_held = not high_ended and gen.sign_held(high, ladder["signs"])
    if not low_held and not high_held:
        return ("end", None, None)
    if position % 2 == 0:
        return ("here", low, "low") if low_held else ("skip", None, "low")
    return ("here", high, "high") if high_held else ("skip", None, "high")


_NEXT_ON_THE_LADDER = gen.next_on_ladder


def _next_on_the_ladder_without_the_census(
    ladder, name, cursor, named, seen, folds, needed=0, pool=None,
    bounded=False, scaled=False,
):
    """G8.3a's walk with the rule on what the census could hold withdrawn.

    A number wearing no named form may then wear any form the census does
    not name, whether or not the census could have counted and pooled it,
    so the level of two in `label_number_tiers` steps past every named
    `%.%` value and writes `10.0` -- the form the census proves the column
    never wore -- instead of ending that side and writing `6`. It ignores
    ``bounded`` with the rest, so the narrow walk of the integration
    repair -- which holds a made-up number to the widest number the column
    shows -- is withdrawn here too: withdrawn alone, the census rule left
    the narrow walk deciding these cells and the case no longer moved.
    """
    return _NEXT_ON_THE_LADDER(
        ladder, name, cursor, named, seen, folds, 0, None, False, scaled
    )


def _levels_from_the_second_spelling(
    used, sizes, census=None, written=(), placed=None, level_shape=""
):
    """G8.3's stand-in walk, started one spelling along.

    The method enumerates a form's spellings IN ORDER and takes the
    first that survives the collision skips and the four neutrality
    tests. This starts at the second instead. Every other property of
    the walk is left exactly as stated -- the skips, the tests, the
    debt the census owes -- so what moves is which spelling each
    suppressed level gets, and nothing else.

    An earlier mutant here turned the LEVEL ORDER over instead, and the
    vacuity check caught it: the spelling comes from a running counter
    and not from the level's size, so reordering the levels changed no
    byte and the branch it named was not one this case holds up.
    """
    seen = set(used)
    folds = {gen.folded(text) for text in used}
    owing = gen.forms_owed(census or {}, written)
    produced: list = []
    counter = 0
    for size in sizes:
        form = gen.neediest_form(owing)
        while True:
            counter += 1
            if form:
                candidate = gen.filled_form(form, counter)
            else:
                candidate = f"group-{counter + 1}"
            if candidate in seen or gen.folded(candidate) in folds:
                continue
            if not gen.usable_stand_in(candidate):
                continue
            seen.add(candidate)
            folds.add(gen.folded(candidate))
            produced.append((candidate, size))
            break
        if form:
            owing[form] = max(0, owing[form] - size)
    return produced


def _spaces_before_flips(parent, used, _target):
    """G8.2's order turned over: the trailing spaces before the case flips.

    It ignores the target form G8.2a asks for, which is the point: the
    order and the form rule are one walk, and turning the order over
    loses the form as well as the spelling.
    """
    seen = set(used)
    spaces = 1
    while True:
        candidate = parent + " " * spaces
        spaces += 1
        if candidate not in seen:
            return candidate


def _no_length_pins(slot, low, high):
    """G9.2's two length pins withdrawn: every slot takes any length."""
    return tuple(range(low, high + 1))


_identifier_family = gen.identifier_family


def _every_band_from_the_figures(band, whole_numbers, length):
    """G9.6's withdrawn rule put back: `all_whole_numbers` means figures."""
    return _identifier_family(gen.FIGURES, whole_numbers, length)


def _no_layout_offered(column):
    """G9.6's layout offer withdrawn: the census is published and unread.

    This is the state landing 2b.18 found and closed -- a column that
    publishes what its record numbers look like and a generator that
    writes them from the band enumeration anyway.
    """
    return []


def _no_layout_mixed(column):
    """G9.6's mixes withdrawn: a group no named layout serves is not mixed.

    Every such group then falls to the band enumeration, which is what
    wrote `A-----5V` for a pooled record number before the mixes existed.
    """
    return []


def _nothing_read_as_absent(text, holes=()):
    """G9.6's absent spellings withdrawn: no spelling is read as absent."""
    return False


def _no_sign_proven(layout):
    """G9.6's proven sign withdrawn: every sign opens a formula again."""
    return False


def _partners_wear_no_layout(layout, convention, count, column, offered):
    """G9.6's partner layouts withdrawn: a partner is predicted to wear none."""
    return [""] * count


def _no_layout_preferred(
    column, groups, families, bands, windows, pinned, demands=None
):
    """G9.6's smooth rotation withdrawn: every group takes the first layout.

    The layouts are then offered in sorted order alone, so the identities
    written once -- which the walk reaches first -- take the first layout
    and the identities written twice take the second.
    """
    return [""] * len(groups)


def _lower_filled_in_capitals(form, step):
    """C6-31a's lower-case key withdrawn: `&` is filled as `@` is."""
    return gen_filled_form(form.replace("&", "@"), step)


def _no_spelling_census(column):
    """G6.8 withdrawn: a count column's census of spellings is not read.

    The ladder walk of G5 and the style walk of G6 write the column, as
    they did before the census existed.
    """
    return gen_numeric_content(dict(column, number_spellings={}))


def _no_level_shape_trade(sizes, shared, level_shape, fixed, seen, folds):
    """G8.3b's trade withdrawn: the shape covers the places as settled.

    The named forms keep the places the census settlement gave them, so
    the places owed no form past the shape's supply take the neutral
    spelling -- which carries a figure, and this oracle refuses to reason
    about one.
    """
    free = [
        place for place in range(len(sizes))
        if place not in fixed and not shared[place]
    ]
    supply = gen.usable_room(level_shape, len(free), seen, folds)
    owed = sorted((-sizes[place], place) for place in free)
    return list(shared), {place for _size, place in owed[:supply]}


def _case_flips_only(parent, longest):
    """G9.3's partner family before edge spacing: case flips and nothing else."""
    for counter in range(1, 1 << sum(1 for c in parent if c.isalpha())):
        yield gen.case_flip(parent, counter)


_packed_grid = gen._packed_grid


def _one_margin_after_another(groups, margins, demanded=True):
    """G9.5 steps 3 and 4 as TWO walks, which the method calls not conforming.

    ``demanded`` is the shape rule's "does THIS shape pack" reading
    (review item P2-C4-F2). The mutant answers the same way whichever
    shape asks it, which is the point: packing one margin after another
    has no answer for this case under any shape the description leaves
    open.
    """
    answers: list = [() for _group in groups]
    placed = list(groups)
    for margin in margins:
        narrowed = [
            (
                size,
                frozenset(
                    name for name in {cell[len(answers[0])] for cell in permitted}
                ),
            )
            for size, permitted in placed
        ]
        taken = _packed_grid(
            [
                (size, frozenset((name,) for name in names))
                for size, names in narrowed
            ],
            (margin,),
        )
        answers = [answer + cell for answer, cell in zip(answers, taken)]
        placed = [
            (
                size,
                frozenset(
                    cell for cell in permitted if cell[: len(answer)] == answer
                ),
            )
            for (size, permitted), answer in zip(placed, answers)
        ]
    return answers


def _point_free_within_the_old_window(value, integer_valued):
    """The sixteen-figure ceiling owner decision 10 lifted, put back.

    The mutant for the pooled-spelling case, and it reverts exactly one
    sentence: a whole value wider than the canonical spelling's
    fixed-point window is told it has no point-free spelling, which is
    what used to send a column of very wide whole numbers back with a
    decimal point on cells its source had written in figures.
    """
    if integer_valued:
        return gen.canonical_spelling(value, True)
    digits, decpt = gen.shortest_round_trip(value)
    if not (-4 < decpt <= 16) or decpt < len(digits):
        return None
    sign = "-" if value < 0 else ""
    return sign + digits + "0" * (decpt - len(digits))


def _one_style_for_the_whole_map(published):
    """G6.4's placement withdrawn: every published form written as `plain`."""
    return {
        style: (sum(published.values()) if style == "plain" else 0)
        for style in gen.STYLE_ORDER
    }


def _clamp_without_the_step(ordinal, last, ceiling):
    """G7A.4's repair with its step-up withdrawn: the clamp alone.

    The clamp keeps a rank inside the published `latest` and does
    nothing whatever about two ranks landing on one time, so a column
    with no slack between its ends comes out holding a time twice.
    """
    if ordinal > ceiling:
        ordinal = ceiling
    return ordinal


def _the_cell_counts_as_if_they_were_the_cores(column):
    """G6A.2's core view withdrawn: the CELL counts handed over instead.

    An affixed column publishes `n_numeric` about its CELLS. On the
    bracket case no cell is itself a number, so that count is nought
    and handing it to the numeric machinery builds no values at all.
    That is a property of the CASE and not of the role: a column whose
    pair is `0` holds cells such as `0191` that wear the pair and read
    as numbers too, so this substitution is not nought everywhere.
    """
    core = dict(column)
    core["n_present"] = column["n_affixed"]
    return core


def _the_sorted_start_and_no_walk(drawn, column, wanted, words):
    """G6B.4 step 5 withdrawn: the sorted start kept, the walk removed.

    Steps 1 and 2 still run -- each position sorted, and the last one
    reversed, permuted or left rank for rank by the mean of the
    published agreements -- and nothing after them.

    The walk moves a rank-for-rank pairing, which agrees at about 1.0,
    TOWARD the agreement the column published. It does not arrive: on
    this column it stops at its try ceiling at 0.2226 against a
    published 0.4323, and calling that reaching the target would be a
    claim the committed bytes contradict.
    """
    total = column["n_joined"]
    last = column["n_parts"] - 1
    running = 0.0
    for value in column["part_agreements"]:
        running = running + gen._field_value(value)
    agreements = column["part_agreements"]
    average = running / float(len(agreements)) if agreements else 0.0
    held = []
    for place in range(column["n_parts"]):
        pairs = sorted((float(text), text) for text in drawn[place])
        held.append([pair[1] for pair in pairs])
    if average < -0.4:
        held[last] = [held[last][total - 1 - seat] for seat in range(total)]
    elif average < 0.4 and len(words) >= max(total - 1, 0):
        order = gen.permutation(total, list(words[: max(total - 1, 0)]))
        held[last] = [held[last][seat] for seat in order]
    return held


# Each row: the case, the branch it exists for, and the rule the method
# rules out put back in its place.
def _notations_from_the_majority(census, default, styles, values):
    """Landing 2b.7's notation census withdrawn from the oracle.

    The rule this puts back is the one the twin followed before plan
    P4-D65.2: `negative_form` publishes the column's MAJORITY and every
    negative cell is written that way, whatever mixture the column
    really held. On `mixed_conventions` that turns eleven cells written
    with a minus into eleven more written in brackets.
    """
    return [default] * len(values)


# The oracle's own rules the seven cases of plans P4-D142, P4-D145, P4-D149 and
# P4-D147 pin, held before any test patches them.
gen_mark_places = gen.mark_places
gen_pad_places = gen.pad_places
gen_apart_values = gen.apart_values
gen_saturated_grid = gen.saturated_grid
gen_saturated_bands = gen.saturated_bands
gen_plus_cells_by_value = gen.plus_cells_by_value


def _marks_without_the_bare_remainder(
    census, published, groupable, floor=gen.CASE_SMALL_CELL_FLOOR, values=None
):
    """Plan P4-D142's bare remainder withdrawn: the leftover wears the mark."""
    worn = gen_mark_places(census, published, groupable, floor, values)
    return [
        published if groupable[index] and worn[index] == "" else worn[index]
        for index in range(len(worn))
    ]


def _pool_on_the_published_mark(
    census, published, groupable, floor=gen.CASE_SMALL_CELL_FLOOR, values=None
):
    """Plan P4-D142's pool mark withdrawn: the pool wears the published mark."""
    named = {gen.mark_written(mark) for mark, _count in gen.named_conventions(
        census, gen.GROUP_MARK_ORDER
    )}
    worn = gen_mark_places(census, published, groupable, floor, values)
    return [
        published if groupable[index] and worn[index] and worn[index] not in named
        else worn[index]
        for index in range(len(worn))
    ]


def _conventions_packed_from_the_first_cell(eligible, values, placed, in_order=False):
    """Plan P4-D149's spread withdrawn from both censuses of conventions.

    Where the censuses of marks and notations ask for their cells, the
    first ``placed`` eligible cells are taken, as the first version's walk
    took them; the plus sign's own spread is left as it is.
    """
    if in_order:
        return list(eligible[:placed])
    return gen_plus_cells_by_value(eligible, values, placed, in_order)


def _without_the_padded_sign_exchange(
    styles, values, integer_valued, pads, marks, notations, plussed, content,
    owed,
):
    """Plan P4-D145's exchange withdrawn: every padded cell keeps its form."""
    return list(styles), list(content), owed


def _asked_with_the_published_mark(census, published):
    """Plan P4-D142's candidate withdrawn: groupability asked of the majority."""
    return published


def _pads_on_the_padded_form_alone(
    census, styles, values, integer_valued, forms=None
):
    """Plan P4-D145's second tier withdrawn: no plus-signed cell is padded."""
    masked = ["plain" if style == "leading_plus" else style for style in styles]
    return gen_pad_places(census, masked, values, integer_valued, forms)


def _apart_without_the_fill(*_arguments, **_keywords):
    """Plan P4-D147's fill withdrawn: the grid is never recognised.

    It asked the rule with a count one larger, which kept every step of
    the walk and stopped the fill -- and once the walk reaches as far as
    amendment A-P4-55 lets it (plan P4-D183), that walk ALSO passes the
    published count and writes all twenty-two, so the mutant moved no
    cell. Withdrawing the fill itself leaves the walk at the published
    count, and it stops at twenty-one.
    """
    return None


def _no_tenths_fill(wanted, figures, total, bands, ladder):
    """Plan P4-D176's fill withdrawn on a written grid, the integers' kept."""
    if figures > 0:
        return None
    return gen_saturated_grid(wanted, figures, total, bands, ladder)


def _no_band_fill(wanted, figures, values, *_rest):
    """The band fill of the carried numbers pass withdrawn: values as given."""
    return values


def _no_tenths_band_fill(wanted, figures, values, *rest):
    """The band fill withdrawn on a written grid, the integers' kept."""
    if figures > 0:
        return values
    return gen_saturated_bands(wanted, figures, values, *rest)


def _no_tenths_push(figures):
    """The push of the repair pass withdrawn on a written grid, the
    integers' kept."""
    return figures == 0


def _no_levels_fill(*_arguments, **_keywords):
    """Plan P4-D178's fill withdrawn: no column's levels are its strata."""
    return None


def _reaches_stratum_by_stratum():
    """Plan P4-D183 withdrawn: one walk reaching as far as it may."""
    return (2,)


def _thousands_not_held(column, values, *_rest):
    """Plan P4-D185 withdrawn: the values come back as the ladder left them."""
    return values


def _prefixes_not_templated(column: dict) -> dict:
    """Plan P4-D202 withdrawn: the census is read as published, no template."""
    return dict(column.get("layout_forms") or {})


def _no_layout_packing(*_arguments, **_keywords):
    """G9.6's layout packing withdrawn (plan P4-D182): no packing is found."""
    return None


def _judged_keys_written_blank(column: dict) -> list:
    """G10.1 as it stood before plan P4-D6.4: a judged pass's key written empty.

    Written out in full rather than calling the oracle's own rule, which
    the battery replaces by this.
    """
    judged: set = set()
    for verdict in column.get("sentinel_verdicts") or []:
        if verdict["verdict"] == "read_as_missing":
            judged |= set(verdict["spellings"])
    holes = column.get("missing_by_source") or {}
    written: list = []
    for spelling in sorted(holes):
        if spelling not in judged:
            written += [spelling] * holes[spelling]
    written += [""] * (column["n_missing"] - len(written))
    return written[: column["n_missing"]]


CASE_MUTANTS = {
    # THE SIX CASES OF STAGE 3'S TAIL RULE (landing 3.3). Each mutant
    # withdraws one statement of the rule and nothing else, and the
    # oracle then writes different cells for that case.
    "tail_shape_ends": Mutant(
        branch="the OUTWARD move of method G5.3b step 4 (plan P4-D326), "
        "which takes a derived end out to where the largest of the tail's "
        "rows is expected to stand; the mutant leaves the end at the "
        "reading of the outermost row alone, and the high end of this "
        "column falls back inside the rows it stands for",
        attribute="outward_move",
        replacement=lambda reach, mean, rows, power: reach,
        outcome=CHANGES_THE_CELLS,
    ),
    "tail_made_up_ramp": Mutant(
        branch="the made-up ramp of method G5.3d, which a block below "
        "its own floor is read as; the mutant leaves the ramp flat at "
        "nought, which is what the sign fallback wrote before the ramp "
        "existed",
        attribute="made_up_ramp",
        replacement=lambda column, figures: [0.0] * 101,
        outcome=CHANGES_THE_CELLS,
    ),
    "tail_listed_counts": Mutant(
        branch="the counts method G5.3e solves for a listed tail -- every "
        "value at least one row, the rest spread on at most three of them, "
        "nearest the published mean distance and then the published "
        "root-mean-square. The mutant gives every listed value one row and "
        "the rest to the outermost, which is the obvious rule and the "
        "wrong one: the staircase moves and the twin's cells with it",
        attribute="listed_counts",
        replacement=lambda boundary, listed, rows, mean, root: (
            [rows - len(listed) + 1] + [1] * (len(listed) - 1)
            if listed
            else []
        ),
        outcome=CHANGES_THE_CELLS,
    ),
    "tail_listed_floor": Mutant(
        branch="G5.3e's FLOOR `q` under each listed value (plan "
        "P4-D346): two rows apiece on a tail the LISTING RULE admitted, "
        "because that rule admits a tail only where every value it "
        "names stands on at least two of the column's cells, and one on "
        "a tail listed under contract TL6's other road. The mutant "
        "counts from one on both, which is the allocation the shipped "
        "rule retired: this column's high tail goes from [2, 2, 2, 6] "
        "-- the real column's own counts beyond that boundary -- to "
        "[1, 4, 1, 6], and the staircase moves with it",
        attribute="listed_floor",
        replacement=lambda size, rows: 1,
        outcome=CHANGES_THE_CELLS,
    ),
    "tail_withheld_pair": Mutant(
        branch="the reading of a tail that publishes NEITHER distance "
        "(method G5.3b's first clause, plan P4-D349): no shape is "
        "fitted, the rows stand on even shares of the room between the "
        "boundary rung and an end `m` grid steps beyond it. The mutant "
        "leaves the end AT the boundary, which is the FLAT reading a "
        "fitted tail of reach nought gets, and every row of both tails "
        "falls back onto its own boundary rung",
        attribute="withheld_step",
        replacement=lambda boundary, steps, low, figures: boundary,
        outcome=CHANGES_THE_CELLS,
    ),
    "tail_sign_clamped": Mutant(
        branch="the sign rule of method G5.5a on a derived end, which "
        "holds the low end of a column with no negative number at nought "
        "or above; the mutant withdraws it and the twin writes a negative "
        "cell on a column whose description says it has none",
        attribute="end_sign_held",
        replacement=lambda value, low, boundary, column, figures: value,
        outcome=CHANGES_THE_CELLS,
    ),
    "tail_moment_ladder": Mutant(
        branch="the moment ladder of method G5.3c, the uniform with the "
        "published mean and spread that a block publishing its moments "
        "and no rung is read as; the mutant reads that block as the ramp "
        "of G5.3d instead, which is what a block one row thinner gets",
        attribute="moment_ladder",
        replacement=lambda column, figures: made_up_ramp_of(column, figures),
        outcome=CHANGES_THE_CELLS,
    ),
    "date_absorbed_mark": Mutant(
        branch="G7.3d's RAMP (stage 3, plan P4-D330), which is what this "
        "column publishes now: two days hold all 125 of its cells, so the "
        "two boundaries would cross, the description publishes no value "
        "of the table at all, and the twin spreads its ranks evenly from "
        "1970-01-01 over the published count of different values. The "
        "mutant spreads them over the RANKS instead, and every cell "
        "moves. G7.9's spend of an absorbed mark, which this case was "
        "frozen for, is out of its reach here: the ramp reaches the "
        "published count of different values by itself, so there is no "
        "shortfall for a mark to buy, and G14.3 records that loss beside "
        "this row",
        attribute="ramp_places",
        replacement=_ramp_over_the_ranks,
        outcome=CHANGES_THE_CELLS,
    ),
    "free_text_absorbed_figures": Mutant(
        branch="G9.5's packing against the READINGS of an absorbed count "
        "(plan P4-D298); the mutant packs the published alphabet counts "
        "alone, sixteen cells in figures beside fifteen numbers, and no "
        "assignment of whole groups meets them",
        attribute="alphabet_readings",
        replacement=lambda column: gen_alphabet_readings(column)[:1],
        outcome="no assignment of whole groups meets every quota",
    ),
    "identifier_absorbed_figure": Mutant(
        branch="G9.6 built against the READINGS of an absorbed count (plan "
        "P4-D298); the mutant builds the published counts alone, and a "
        "one-character whole number outside the figures does not exist",
        attribute="identifier_readings",
        replacement=lambda column: gen_identifier_readings(column)[:1],
        outcome="no assignment of whole groups meets every quota",
    ),
    "saturated_band": Mutant(
        branch="G6.5a's fill of a sign band whose own grid has no spare point "
        "(the carried numbers pass of 2026-09-18, amending plan P4-D147); the "
        "mutant withdraws it, and a positive stratum the ladder put inside "
        "the published empty pair stays there",
        attribute="saturated_bands",
        replacement=lambda wanted, figures, values, *rest: values,
        outcome=CHANGES_THE_CELLS,
    ),
    "pushed_along_band": Mutant(
        branch="G6.5a's push of a collision the walks leave along its band "
        "to the nearest free point (the carried numbers repair pass of "
        "2026-09-19); the mutant withdraws it, and the twin writes 3.4 a "
        "second way and holds seventeen numbers against eighteen",
        attribute="pushing_on",
        replacement=lambda figures: False,
        outcome=CHANGES_THE_CELLS,
    ),
    "saturated_grid_alone": Mutant(
        branch="G6.5a's column-wide fill of a grid with no spare point (plans "
        "P4-D147 and P4-D176) where the band fill and the push both stand "
        "aside; the mutant withdraws the column-wide fill and nothing else, "
        "and the twin writes -1.9 a second way and holds twenty-five "
        "numbers against twenty-six",
        attribute="saturated_grid",
        replacement=lambda *arguments: None,
        outcome=CHANGES_THE_CELLS,
    ),
    "mode_held": Mutant(
        branch="plan P4-D267's last value pass, which puts the published mode "
        "on the stratum its count sizes; the mutant withdraws it and the "
        "mode is written nowhere",
        attribute="mode_held",
        replacement=lambda values, *rest: values,
        outcome=CHANGES_THE_CELLS,
    ),
    "date_midnight_traded": Mutant(
        branch="G7.3b step 3's MOMENT-MATCHED END (stage 3, plan "
        "P4-D328), which both of this column's tails are drawn through. "
        "The stretch on the drawn ranks and the outermost rank's own "
        "distance solve the two moment equations together, so the "
        "expected sum of the tail's distances and of their squares are "
        "the two published numbers; the mutant puts the end back where "
        "the tail had it before -- the root-mean-square of the shape "
        "over the outermost stratum, with no stretch on the ranks inside "
        "it, which on a lone far value misses the published mean square "
        "by 14 to 22 per cent -- and every tail cell of the column "
        "moves. The MIDNIGHT half of P4-D258's paid merge, which this "
        "case was frozen for, is out of its reach here: a tail rank "
        "moves only inside its own stratum, so the merge that settles for "
        "a stranded run has nowhere to take one, and G14.3 records that "
        "loss beside this row",
        attribute="stretched_end",
        replacement=_stratum_end_instead,
        outcome=CHANGES_THE_CELLS,
    ),
    "held_back_dressed": Mutant(
        branch="plan P4-D268's dressing, which writes a ladder number through "
        "the published form its group owes; the mutant withdraws it and the "
        "held-back rows are written as bare numbers",
        attribute="dressed_in_form",
        replacement=lambda *arguments: "",
        outcome=CHANGES_THE_CELLS,
    ),
    "held_back_anchored": Mutant(
        branch="plan P4-D268's anchors, which read a published number spelled "
        "with a plus a second way so it anchors the ladder; the mutant reads "
        "the plain spelling alone and the ladder counts up from nought",
        attribute="anchor_units",
        replacement=lambda text, value: gen.plain_units(text),
        outcome=CHANGES_THE_CELLS,
    ),
    "judged_stand_in_written": Mutant(
        branch="G10.1's write rule with a judged stand-in among the absent "
        "cells (plan P4-D6.4, the owner's ruling of 2026-09-15); the mutant "
        "is the rule it replaced, which wrote a judged pass's cells blank, "
        "and the eleven -999 cells come back empty",
        attribute="absent_cells",
        replacement=_judged_keys_written_blank,
        outcome=CHANGES_THE_CELLS,
    ),
    "unmarked_duplicates_first": Mutant(
        branch="plan P4-D265's visiting order for the distinct-spelling "
        "repair of G6.5; the mutant visits the duplicates in index order, "
        "spends a raised order on cells the census of marks had already "
        "marked, and four of the eleven marks come off the column",
        attribute="unmarked_duplicates_first",
        replacement=lambda repeats, marks: list(repeats),
        outcome=CHANGES_THE_CELLS,
    ),
    "representable_with_room": Mutant(
        branch="G6.5a's last resort on a representable grid with SPARE "
        "points (stage 3's review, verdict item 4); the mutant restores "
        "the rule as it stood before that verdict -- the fill only where "
        "the two ends hold exactly as many representable numbers as the "
        "column has strata -- and the three spare numbers withdraw it, "
        "the ladder interpolates between rungs one binary64 apart, and "
        "several strata land on one number",
        attribute="representable_grid",
        replacement=lambda total, bands, values: _only_when_saturated(
            total, bands, values
        ),
        outcome=CHANGES_THE_CELLS,
    ),
    "saturated_representable": Mutant(
        branch="plan P4-D269's fill of a saturated REPRESENTABLE grid, the "
        "last resort where the published widths fix no decimal grid at "
        "all; the mutant withdraws it, the ladder interpolates between "
        "rungs one binary64 apart, and several strata land on one number",
        attribute="representable_grid",
        replacement=lambda *arguments: None,
        outcome=CHANGES_THE_CELLS,
    ),
    "identifier_column_prefix": Mutant(
        branch="G9.6a's templates, which write a published prefix as part "
        "of its layout (plan P4-D202, owner ruling of 2026-09-17); the mutant "
        "leaves every layout as published, the prefix's letters are filled "
        "from the step, and the recount of 7.12a stops the oracle",
        attribute="templated_census",
        replacement=_prefixes_not_templated,
        outcome="do not open with a prefix the case publishes",
    ),
    "identifier_layout_prefixes": Mutant(
        branch="G9.6a's templates, per layout (plan P4-D202); the mutant "
        "leaves both layouts as published, and the recount of 7.12a stops "
        "the oracle",
        attribute="templated_census",
        replacement=_prefixes_not_templated,
        outcome="do not open with a prefix the case publishes",
    ),
    "saturated_tenths": Mutant(
        branch="plan P4-D176's fill of a saturated grid of tenths; the mutant "
        "keeps the fill on the integers alone, and the walk places the "
        "strata elsewhere. The band fill of the carried numbers pass states "
        "the same fill band by band, and the push of its repair pass ends at "
        "the same assignment on a grid with no spare point, so both are "
        "withdrawn on a written grid too",
        attribute="saturated_grid",
        replacement=_no_tenths_fill,
        outcome=CHANGES_THE_CELLS,
        also=(
            ("saturated_bands", _no_tenths_band_fill),
            ("pushing_on", _no_tenths_push),
        ),
    ),
    "pooled_level_sizes": Mutant(
        branch="plan P4-D201's sizes read off a pooled total; the mutant "
        "shares the pool out evenly, and the stand-ins' rows move",
        attribute="held_back_sizes",
        replacement=_pool_shared_evenly,
        outcome=CHANGES_THE_CELLS,
    ),
    "saturated_levels": Mutant(
        branch="plan P4-D178's fill of a column's published levels; the "
        "mutant withdraws it, and the walk writes a level no source cell "
        "held",
        attribute="saturated_levels",
        replacement=_no_levels_fill,
        outcome=CHANGES_THE_CELLS,
    ),
    "separated_in_order": Mutant(
        branch="plan P4-D183's walks taken reach by reach; the mutant takes "
        "all three reaches stratum by stratum, and an early stratum walks "
        "out of its share onto a point a later stratum held inside its own",
        attribute="separation_reaches",
        replacement=_reaches_stratum_by_stratum,
        outcome=CHANGES_THE_CELLS,
    ),
    "date_midnight_feasible": Mutant(
        branch="plan P4-D254's feasible spend of G7.4's offsets; the mutant "
        "makes every offset look feasible, which is the lexical spend it "
        "replaces, and the ranks whose gap holds no midnight under the "
        "offset their block reached are left off midnight",
        attribute="a_midnight_inside",
        replacement=lambda *arguments: True,
        outcome=CHANGES_THE_CELLS,
    ),
    "date_endpoint_ties": Mutant(
        branch="the CONDITION on G7A.4's two-pass step inside a tail "
        "(stage 3, plan P4-D328): the step keeps a tail's ranks apart on "
        "a column whose own values all differ, and on no other. The "
        "mutant runs it on every column, and this column's tail cells "
        "move. Plan P4-D255's hold on the ranks tied at an end, which "
        "this case was frozen for, is gone with the two ends themselves: "
        "the description names no offset for an end row because it "
        "describes no end row, and G14.3 records that beside this row",
        attribute="tail_distances",
        replacement=_always_apart,
        outcome=CHANGES_THE_CELLS,
    ),
    "date_second_field_class": Mutant(
        branch="plan P4-D256's census key in the width pass; the mutant asks "
        "the older question -- is either field below ten -- and the twin's "
        "dates fall on days counted under a joint word instead",
        attribute="shows_a_width",
        replacement=_either_field_below_ten,
        outcome=CHANGES_THE_CELLS,
    ),
    # THESE TWO WERE FROZEN FOR PLAN P4-D258's TWO MERGES AND NO LONGER
    # REACH THEM (plan P4-D294, the merge-close of 2026-09-18). Both are
    # textual columns under a JOINT width word, and a joint word absorbs
    # every day that shows no width at all, so the column carries ONE
    # width kind and no gap of it can be without a unit of its own kind
    # -- which is the situation both branches exist for. 500 candidate
    # columns were measured and none reached either branch, so they are
    # registered here against the rule they DO pin, which is P4-D294
    # itself. The loss of coverage is stated in G14.3 under the case
    # table rather than left to be discovered.
    "date_traded_merge": Mutant(
        branch="plan P4-D294's width KIND; the mutant asks whether the day "
        "SHOWS the census's width in place of whether it is COUNTED into "
        "it, and the twin's dates move",
        attribute="counts_into_width",
        replacement=_shows_it,
        outcome=CHANGES_THE_CELLS,
    ),
    "date_nonadjacent_merge": Mutant(
        branch="plan P4-D294's width KIND, asked of the same three days at "
        "other words; the mutant is the same narrowing and it moves these "
        "cells too",
        attribute="counts_into_width",
        replacement=_shows_it,
        outcome=CHANGES_THE_CELLS,
    ),
    # P4-D258's TWO MERGES, REACHED AGAIN (the carried date items of
    # 2026-09-18). A one-field census whose unnamed remainder stands on
    # days of the other kind is a column carrying two width kinds, which
    # is the situation both merges exist for and which the two cases
    # above no longer describe. Each mutant withdraws exactly its own
    # merge and moves its own case's cells. REBUILT BY THE REPAIR PASS OF
    # THE SAME DAY from the descriptions the producer writes of the tables
    # the two cases describe, which publish FOUR different values -- the
    # remainder's day is written two ways -- where the first freezing
    # published three, a count no such table can reach.
    "date_two_kinds_traded": Mutant(
        branch="plan P4-D258's traded merge; the mutant makes no trade, "
        "and the twin's fourth date falls on another day while the three "
        "published days hold other numbers of cells",
        attribute="traded_merges",
        replacement=lambda *arguments: 0,
        outcome=CHANGES_THE_CELLS,
    ),
    "date_two_kinds_nonadjacent": Mutant(
        branch="G7.3d's START (stage 3, plan P4-D330), which is what "
        "this column publishes now: three days hold all thirty-six of "
        "its cells, so the two boundaries would cross and the "
        "description publishes no value of the table at all. Rank "
        "nought of its ramp stands at 1970-01-01, ordinal nought in "
        "every space of G7.1; the mutant starts the ramp one step "
        "later and every cell moves. Plan P4-D258's merge onto a held "
        "unit that is no rank neighbour, which this case was frozen "
        "for, is out of its reach here: the ramp places one rank to a "
        "step over the published count of different values, so no run "
        "is left needing a merge, and G14.3 records that loss beside "
        "this row",
        attribute="ramp_places",
        replacement=_ramp_from_one,
        outcome=CHANGES_THE_CELLS,
    ),
    # THE JOINT WORD OF A RANK SHOWING BOTH FIELDS (the repair pass of the
    # carried date items of 2026-09-18, plan P4-D294 amended). The mutant
    # is the rule it replaced: the joint word that AGREES with the named
    # one-field word, which folds the whole named count into itself.
    "date_both_fields_disagree": Mutant(
        branch="method G7.5 step 1's joint word for a rank showing both "
        "fields under a census naming one-field words alone; the mutant "
        "builds the joint word that agrees with the census, and the "
        "twin's dates of the third of March are written with the month "
        "padded, which folds the twenty-two named cells into `padded`",
        attribute="both_fields_width_of",
        replacement=lambda census: gen.joint_width_of(census),
        outcome=CHANGES_THE_CELLS,
    ),
    "date_widths_reached": Mutant(
        branch="plan P4-D192's widths pass; the mutant leaves the ranks where "
        "they were drawn, and a different number of dates show a width than "
        "the one convention the census names counts",
        attribute="widths_pass",
        replacement=lambda *arguments: False,
        outcome=CHANGES_THE_CELLS,
    ),
    "date_distinct_reached": Mutant(
        branch="plan P4-D192's pass on the count of different values; the "
        "mutant leaves the ranks where they were drawn, and the twin holds "
        "more different days than the description publishes",
        attribute="distinct_pass",
        replacement=lambda *arguments: False,
        outcome=CHANGES_THE_CELLS,
    ),
    "midnight_withheld_kept": Mutant(
        branch="plan P4-D191's rule for a withheld count at midnight; the "
        "mutant leaves the ranks where they were drawn, and a count the "
        "description would publish stands in the minute of midnight",
        attribute="kept_off_midnight",
        replacement=lambda column, ordinals, *arguments, **keywords: list(ordinals),
        outcome=CHANGES_THE_CELLS,
    ),
    "numbers_carry_the_average": Mutant(
        branch="plan P4-D190's walk of the numbers' own lengths; the mutant "
        "leaves every number at its shortest, and the recount finds the "
        "average the words carrying both ends could not reach",
        attribute="numbers_walked",
        replacement=lambda column, groups, lengths, packed, carriers, fixed: list(lengths),
        outcome="recount length.mean as",
    ),
    "grouped_thousands_signed": Mutant(
        branch="plan P4-D194's negative side of the census of marks; the "
        "mutant reads the column as holding no negative value, and one cell "
        "fewer than the census wears a comma",
        attribute="grouped_enough",
        replacement=_marks_on_the_positive_side_alone,
        outcome=CHANGES_THE_CELLS,
    ),
    "identifier_unnamed_partners": Mutant(
        branch="plan P4-D196's quota of the cells a layout census names no "
        "layout for; the mutant reads that quota as unbounded, an identity "
        "owed a partner takes `@-%%`, and the check of 7.12 finds `@%%%` "
        "worn one time too few",
        attribute="layout_preferences",
        replacement=_partners_with_no_unnamed_quota,
        outcome="wear the layout '@%%%' 21 times",
    ),
    "code_band_words": Mutant(
        branch="plan P4-D234's headed enumeration of a band's made-up "
        "words; the mutant counts the whole word over the alphabet and "
        "puts the first permitted character in the leading place, and writes "
        "`A-`, `A0`, `A1` for `A-`, `B-`, `C-`",
        attribute="headed_spelling",
        replacement=lambda head, alphabet, length, index: (
            _SHIPPED_ENUMERATED_SPELLING(
                alphabet, length, index, lambda figure: figure not in "0123456789"
            )
        ),
        outcome=CHANGES_THE_CELLS,
    ),
    "truth_values_written": Mutant(
        branch="plan P4-D198's truth values; the mutant spells none, and the "
        "group of eleven is a made-up word",
        attribute="truth_words",
        replacement=lambda *arguments: {},
        outcome=CHANGES_THE_CELLS,
    ),
    "twice_written_filled": Mutant(
        branch="plan P4-D193's fill of a grid whose whole number is written "
        "two ways; the mutant withdraws the rule, and the walk leaves two "
        "strata on a tenth that is not whole",
        attribute="twice_written",
        replacement=lambda column, values, *arguments: list(values),
        outcome=CHANGES_THE_CELLS,
    ),
    "exponent_scaled": Mutant(
        branch="G8.3a step 3's SCALED walk (item 3 of the numbers pass of "
        "the second Codex round, 2026-09-19); the mutant walks the ladder "
        "at the form's plain places, every step it offers is a thousand "
        "times finer than `%.%%&+%` can spell, and the held-back rows are "
        "written `1101` and `1099` as bare numbers wearing no form",
        attribute="form_scale",
        replacement=lambda form, ladder: gen_form_places(form),
        outcome=CHANGES_THE_CELLS,
    ),
    "exponent_fitted": Mutant(
        branch="G8.3a step 3's EXPONENT FITTINGS (item 3 of the numbers "
        "pass of the second Codex round, 2026-09-19); the mutant offers no "
        "exponent filling, the two placements of step 2 answer alone, and "
        "the held-back rows are written `22001` and `21999`",
        attribute="exponent_fittings",
        replacement=lambda candidate, form: [],
        outcome=CHANGES_THE_CELLS,
    ),
    "twice_written_merged": Mutant(
        branch="plan P4-D193's merge onto a whole neighbour; the mutant "
        "withdraws the rule, and every stratum keeps a number of its own",
        attribute="twice_written",
        replacement=lambda column, values, *arguments: list(values),
        outcome=CHANGES_THE_CELLS,
    ),
    "grouped_thousands": Mutant(
        branch="plan P4-D185's census of marks held at a thousand; the mutant "
        "leaves the values where the ladder put them, and one reading fewer "
        "reaches a thousand and wears a comma",
        attribute="grouped_enough",
        replacement=_thousands_not_held,
        outcome=CHANGES_THE_CELLS,
    ),
    "identifier_layout_packing": Mutant(
        branch="G9.6's layout packing (plan P4-D182); the mutant finds no "
        "packing of the census, the column keeps its class-and-alphabet "
        "packing, and the check of 7.12 finds the wide layouts unworn",
        attribute="packed_layouts",
        replacement=_no_layout_packing,
        outcome="wear the layout '@@#%%' 0 times",
    ),
    "bare_mark_remainder": Mutant(
        branch="plan P4-D142's bare remainder; the mutant writes every "
        "groupable cell no named count covers with the published mark, as "
        "the twin did before that decision, and the eleven bare cells are "
        "grouped",
        attribute="mark_places",
        replacement=_marks_without_the_bare_remainder,
        outcome=CHANGES_THE_CELLS,
    ),
    "plus_padded_field": Mutant(
        branch="plan P4-D145's second tier of named field widths; the mutant "
        "serves the padded form alone and every plus-signed cell is written "
        "two figures short of its field",
        attribute="pad_places",
        replacement=_pads_on_the_padded_form_alone,
        outcome=CHANGES_THE_CELLS,
    ),
    "pooled_mark_cells": Mutant(
        branch="plan P4-D142's pool mark; the mutant writes the pooled "
        "remainder with the published comma, so the comma count passes the "
        "published one",
        attribute="mark_places",
        replacement=_pool_on_the_published_mark,
        outcome=CHANGES_THE_CELLS,
    ),
    "saturated_integers": Mutant(
        branch="plan P4-D147's fill of a saturated integer grid; the mutant "
        "withdraws the fill and the walk alone, which lands strata on points "
        "other strata still need, writes twenty-one numbers. The band fill "
        "of the carried numbers pass states the same fill band by band, and "
        "on this column of one sign it is the same fill, so it is withdrawn "
        "with it",
        attribute="saturated_grid",
        replacement=_apart_without_the_fill,
        outcome=CHANGES_THE_CELLS,
        also=(("saturated_bands", _no_band_fill),),
    ),
    "signed_pads": Mutant(
        branch="plan P4-D145's padded sign exchange; the mutant leaves every "
        "padded cell in the form the style walk gave it, and the column "
        "comes back with fewer spellings",
        attribute="padded_sign_exchange",
        replacement=_without_the_padded_sign_exchange,
        outcome=CHANGES_THE_CELLS,
    ),
    "spread_conventions": Mutant(
        branch="plan P4-D149's spread of the censuses of conventions; the "
        "mutant takes each count from the first eligible cell upward, which "
        "ties a notation and a mark to the most negative numbers",
        attribute="plus_cells_by_value",
        replacement=_conventions_packed_from_the_first_cell,
        outcome=CHANGES_THE_CELLS,
    ),
    "unpublished_majority_marks": Mutant(
        branch="plan P4-D142's groupable cells asked with a mark that writes "
        "one; the mutant asks with the published mark, which is none, and "
        "no cell is grouped",
        attribute="candidate_mark",
        replacement=_asked_with_the_published_mark,
        outcome=CHANGES_THE_CELLS,
    ),
    "grouped_charges": Mutant(
        branch="landing 2b.2's spread of signed decimals; the mutant takes "
        "the plus from the first eligible cell upward, which ties a plus to "
        "the smallest values",
        attribute="plus_places",
        replacement=_plus_from_the_first_cell,
        outcome=CHANGES_THE_CELLS,
    ),
    "grouped_decimal_comma": Mutant(
        branch="P4-D38's rule that the mark reaches a cell at leading-zero "
        "order nought only; the mutant groups the cell that spent a zero as "
        "well, and after the exchange it wears a point inside its padding",
        attribute="styled_spelling",
        replacement=_grouped_at_every_order,
        outcome=CHANGES_THE_CELLS,
    ),
    "spaced_brackets": Mutant(
        branch="landing 2b.2's negative notation; the mutant withdraws it and "
        "every negative is written with a hyphen-minus in front",
        attribute="negative_spelled",
        replacement=_notation_withdrawn,
        outcome=CHANGES_THE_CELLS,
    ),
    "apostrophe_minus_sign": Mutant(
        branch="landing 2b.2's minus sign U+2212; the mutant withdraws the "
        "notation and every negative is written with a hyphen-minus in front",
        attribute="negative_spelled",
        replacement=_notation_withdrawn,
        outcome=CHANGES_THE_CELLS,
    ),
    "quoted_trailing_minus": Mutant(
        branch="the right single quotation mark between thousands; the mutant "
        "writes every published mark as a comma",
        attribute="grouping_mark_of",
        replacement=_every_mark_a_comma,
        outcome=CHANGES_THE_CELLS,
    ),
    "spaced_decimal_comma": Mutant(
        branch="P4-D26's exchange beside a no-break space, a mark neither decimal "
        "mark; the mutant withdraws the exchange and every present cell keeps "
        "its point",
        attribute="decimal_comma_spelled",
        replacement=_exchange_withdrawn,
        outcome=CHANGES_THE_CELLS,
    ),
    "narrow_spaced": Mutant(
        branch="the narrow no-break space between thousands; the mutant writes "
        "every published mark as a comma",
        attribute="grouping_mark_of",
        replacement=_every_mark_a_comma,
        outcome=CHANGES_THE_CELLS,
    ),
    "thin_spaced": Mutant(
        branch="the thin space between thousands; the mutant writes every "
        "published mark as a comma",
        attribute="grouping_mark_of",
        replacement=_every_mark_a_comma,
        outcome=CHANGES_THE_CELLS,
    ),
    "lower_case_stand_ins": Mutant(
        branch="C6-31a's lower-case key, filled from the lower-case "
        "alphabet at the positions a `@` takes; the mutant fills it in "
        "capitals, and every stand-in moves",
        attribute="filled_form",
        replacement=_lower_filled_in_capitals,
        outcome=CHANGES_THE_CELLS,
    ),
    "count_spellings": Mutant(
        branch="G6.8's census of spellings, which writes a count column "
        "that wrote one number more than one way as its published "
        "spellings; the mutant withdraws it, and the ladder and style walks "
        "write the column instead",
        attribute="_numeric_content",
        replacement=_no_spelling_census,
        outcome=CHANGES_THE_CELLS,
    ),
    "level_shape_stand_ins": Mutant(
        branch="G8.3b's trade, which moves a large held-back group paying a "
        "named form onto the published labels' shape and settles the form "
        "with single rows summing to it; the mutant withdraws the trade, "
        "and a place past the shape's supply is left the neutral spelling",
        attribute="level_shape_spent",
        replacement=_no_level_shape_trade,
        outcome="reasons only about stand-ins with no figure",
    ),
    "identifier_layout": Mutant(
        branch="G9.6's smooth weighted rotation of a layout census over the "
        "identities (contract 7.12); the mutant withdraws it, so every "
        "identity written once takes `@%%%%%` and every identity written "
        "twice takes `@@%%%%`, binding a layout to how often it recurs",
        attribute="layout_preferences",
        replacement=_no_layout_preferred,
        outcome=CHANGES_THE_CELLS,
    ),
    "identifier_absent_words": Mutant(
        branch="G9.6's refusal of a spelling a reader reads as absent (plan "
        "P4-D158); the mutant reads nothing as absent, the layout walk "
        "writes `NA`, and the cells move",
        attribute="reads_as_absent",
        replacement=_nothing_read_as_absent,
        outcome=CHANGES_THE_CELLS,
    ),
    "identifier_signed_layout": Mutant(
        branch="G9.6's proven sign (plan P4-D156); the mutant refuses every "
        "opening sign, no filling of `-%%%%` is written, and the check of "
        "7.12 finds the layout worn nought times",
        attribute="_a_signed_number",
        replacement=_no_sign_proven,
        outcome="wear the layout '-%%%%' 0 times",
    ),
    "identifier_layout_partners": Mutant(
        branch="G9.6's partner layouts (plan P4-D157); the mutant predicts "
        "no partner wears a layout, the identities take the whole census, "
        "and their partners overpay the other layout",
        attribute="partner_layouts",
        replacement=_partners_wear_no_layout,
        outcome="wear the layout '&%%' 14 times",
    ),
    "identifier_layout_mixes": Mutant(
        branch="G9.6's mixes of a layout census's kinds, which write the "
        "cells no named layout serves (plan P4-D128); the mutant withdraws "
        "them, and the fourteen pooled cells fall to the band enumeration",
        attribute="layout_stand_in_bases",
        replacement=_no_layout_mixed,
        outcome=CHANGES_THE_CELLS,
    ),
    "date_only": Mutant(
        branch="G7.3's placement as landing 2b.6 rewrites it: the nine "
        "interior rungs pinned to their PUBLISHED values and every other "
        "rank drawn inside the gap between the pinned ranks either side "
        "of it; the mutant restores the withdrawn stratified placement, "
        "and the interior ranks move",
        attribute="spread_ordinals",
        replacement=_stratified_ranks,
        outcome=CHANGES_THE_CELLS,
    ),
    "date_gap_places": Mutant(
        branch="G7.3's places for its pins inside their own days (plan "
        "P4-D130); the mutant draws each gap over its two pinned days whole, "
        "as 158c811 did, and the ranks next to the pinned days move",
        attribute="spread_ordinals",
        replacement=_inclusive_gap_draws,
        outcome=CHANGES_THE_CELLS,
    ),
    "date_thinning_week": Mutant(
        branch="G7.3's choice of the middles (plan P4-D138); the mutant keeps "
        "the straightest count on every column, and the ranks the first day "
        "would have taken move to the days after it",
        attribute="pin_places",
        replacement=_straightest_places_alone,
        outcome=CHANGES_THE_CELLS,
    ),
    "date_peak_heap": Mutant(
        branch="G7.3's heaps (plan P4-D138); the mutant moves every pin "
        "sharing a day onto the straight line like any other, and the ranks "
        "beside the peak's days move",
        attribute="pin_places",
        replacement=_no_heap_held,
        outcome=CHANGES_THE_CELLS,
    ),
    "month_first_widths": Mutant(
        branch="G7.5's one-field classes of width (plan P4-D132); the mutant "
        "writes the dates whose month alone shows a width as the joint words "
        "pad that field, and those dates take the other padding",
        attribute="field_weights",
        replacement=_field_class_from_the_joint_words,
        outcome=CHANGES_THE_CELLS,
    ),
    "may_month_names": Mutant(
        branch="G7.5's `either` length of a name of May (plan P4-D133); the "
        "mutant offers the ranks of May no `either` word, and they are "
        "written in the other ranks' style",
        attribute="month_name_styles_of",
        replacement=_no_either_length,
        outcome=CHANGES_THE_CELLS,
    ),
    "reserved_name_floor": Mutant(
        branch="G7.5's reservation of a named form's least (plan P4-D132); "
        "the mutant spends the class by the rotation alone, and the style "
        "published at the floor falls under it",
        attribute="reserved",
        replacement=_rotation_alone,
        outcome=CHANGES_THE_CELLS,
    ),
    "free_text_joint": Mutant(
        branch="G9.5 steps 3 and 4 as ONE packing; the mutant walks the "
        "class counts first and the alphabet counts second, and no whole "
        "group can answer for what the second walk is left with",
        attribute="_packed_grid",
        replacement=_one_margin_after_another,
        outcome="no assignment of whole groups meets every quota",
    ),
    "identifier_edge_spacing": Mutant(
        branch="G9.3's partner family as a case flip, edge spacing, or "
        "both; the mutant is the case-flip-only construction, and this "
        "column is written in figures, so it supplies nothing at all",
        attribute="partner_family",
        replacement=_case_flips_only,
        outcome="infeasible corner",
    ),
    "identifier_fold_collisions": Mutant(
        branch="G9.2's two length pins, which are what make `min_length` "
        "and `max_length` exact at no cost in words; the mutant lets every "
        "slot take any length in the range",
        attribute="slot_lengths",
        replacement=_no_length_pins,
        outcome="recount max_length as 2 and the case publishes 4",
    ),
    "identifier_whole_numbers": Mutant(
        branch="G9.6's bands, which come from the two published alphabet "
        "counts; the mutant is revision 1's withdrawn rule, that "
        "`all_whole_numbers` true means every group is written from the "
        "figures",
        attribute="identifier_family",
        replacement=_every_band_from_the_figures,
        outcome="recount n_all_digits as 12 and the case publishes 4",
    ),
    "joined_readings": Mutant(
        branch="G6B.4 step 5, the pairing walk itself; the mutant keeps "
        "the sorted start of steps 1 and 2 and removes the search "
        "after it. A rank-for-rank start pairs largest with largest "
        "and agrees at about 1.0, while this column publishes 0.4323 "
        "and holds the earlier position above the later in only seven "
        "of twelve rows, so the walk has real work here -- measured, "
        "six of its twelve cells move. The walk does NOT reach the "
        "published agreement even so: it stops at its try ceiling at "
        "0.2226, which the case records rather than hides",
        attribute="repaired_pairing",
        replacement=_the_sorted_start_and_no_walk,
        outcome=CHANGES_THE_CELLS,
    ),
    "affixed_brackets": Mutant(
        branch="G6A.2's core view, which hands the numeric machinery "
        "the CORE class counts and not the cell counts; the mutant "
        "hands over the cell counts. On THIS column no cell is itself "
        "a number -- every one wears a bracket pair -- so the cell "
        "count is nought and the column comes out with nothing in it. "
        "The oracle stops at the WORD BUDGET, which is the first place "
        "the swap shows: G4.3 reads that budget over the cores too, so "
        "a nought cell count asks for no content words at all. This is "
        "a property of the CASE and not of the role: a column whose "
        "pair is `0` can hold cells such as `0191` that wear the pair "
        "AND read as numbers, so an affixed column's cell `n_numeric` "
        "is not nought in general",
        attribute="affixed_core_view",
        replacement=_the_cell_counts_as_if_they_were_the_cores,
        outcome="asks for 0 content words",
    ),
    "mark_spend_at_the_line": Mutant(
        branch="G7.9 item 2's last clause, which stops the spend while "
        "the mark it is taken FROM is at `census_floor(floor)`; the "
        "mutant lets the spend run to the budget alone, which is what "
        "it did until the dates pass of the stage-3 review, and this "
        "column's census of eleven `T` marks -- the floor itself -- "
        "comes back ten and one, a census no twin's own description "
        "may print at all",
        attribute="mark_spend_leaves_a_named_count",
        replacement=_a_spend_that_never_looks_at_the_line,
        outcome=CHANGES_THE_CELLS,
    ),
    "clock_declared_hole": Mutant(
        branch="G7A.4's HOLE STEP, which moves a body rank off a "
        "spelling the table calls absent and onto the nearest unit of "
        "its own window that is not one; the mutant answers that no "
        "spelling reads as absent, which is what this role did until "
        "the dates pass of the stage-3 review -- its stand-ins were "
        "stepped past the absent spellings and its clock values were "
        "checked against nothing -- and the column then writes "
        "THIRTEEN `08:00` cells against the eleven its description "
        "publishes absent",
        attribute="_clock_reads_absent",
        replacement=_no_spelling_reads_as_absent,
        outcome=CHANGES_THE_CELLS,
    ),
    "clock_ladder": Mutant(
        branch="G7A.4's all-different repair, which steps a rank that "
        "landed on the previous rank's time up to the next ordinal "
        "before clamping it to the published latest; the mutant keeps "
        "the clamp and withdraws the step, and this column has no "
        "slack to absorb it -- eleven seconds for eleven parsed cells "
        "-- so two times come out written twice",
        attribute="clock_repair",
        replacement=_clamp_without_the_step,
        outcome=CHANGES_THE_CELLS,
    ),
    "long_tail_levels": Mutant(
        branch="G8.3's stand-in walk, which enumerates a form's "
        "spellings IN ORDER and takes the first that survives the "
        "collision skips; the mutant starts one spelling along, so "
        "every one of the twenty suppressed levels gets a different "
        "stand-in",
        attribute="invented_levels",
        replacement=_levels_from_the_second_spelling,
        outcome=CHANGES_THE_CELLS,
    ),
    "label_numbers": Mutant(
        branch="G8.3a's walk for a held-back number, which fills the "
        "gaps between the published numbers before it steps beyond "
        "either end; the mutant steps outward from the start, so the "
        "largest held-back group leaves the gap and every number moves",
        attribute="outward_at",
        replacement=_outward_without_the_gaps,
        outcome=CHANGES_THE_CELLS,
    ),
    "label_number_tiers": Mutant(
        branch="G8.3a's rule on what the census could hold, which ends a "
        "side of the walk where the next form is one the census would have "
        "counted and pooled and it pooled nothing; the mutant writes that "
        "form, and the level of two moves from `6` to `10.0`",
        attribute="next_on_ladder",
        replacement=_next_on_the_ladder_without_the_census,
        outcome=CHANGES_THE_CELLS,
    ),
    # THE POOL'S OWN SCALE (method G8.3c, plan P4-D301). The mutant is
    # the whole of G8.3c withdrawn -- every group handed back to the
    # ordinary walk of G8.3a step 3 -- because that IS the state this
    # landing found: the rule did not exist, the ladder was unanchored
    # on a column publishing no number, and the twin counted upward from
    # nought.
    "pooled_number_scale": Mutant(
        branch="G8.3c, which places the pool's made-up numbers on the "
        "mean and the population spread contract 6.3.3 publishes for "
        "them; the mutant withdraws the placement, the unanchored ladder "
        "of G8.3a step 3 answers instead, and the four held-back levels "
        "come back as the smallest numbers that walk can write",
        attribute="pooled_placements",
        replacement=_nothing_placed_at_the_pools_scale,
        outcome=CHANGES_THE_CELLS,
    ),
    "label_variants": Mutant(
        branch="G8.2's order, case flips before trailing spaces; the "
        "mutant goes straight to the spaces and every invented variant "
        "moves",
        attribute="invented_variant",
        replacement=_spaces_before_flips,
        outcome=CHANGES_THE_CELLS,
    ),
    # RETARGETED AT LANDING 2b.6 PART 2, and the reason is a coverage
    # loss named rather than hidden. This case used to withdraw P4-D39's
    # day-unit rule by counting a column wholly at midnight in seconds,
    # and its interior ranks then landed part-way through a day. They
    # still do -- measured: rank 3 moves from day 19846 to 19846 days
    # plus 25,374 seconds -- but the CELLS no longer move, because
    # counting in seconds also turns `snaps_to_midnight` on, and landing
    # 2b.3's snap pulls every rank back to the nearest midnight INSIDE
    # ITS OWN GAP. Since G7.3 now pins the rungs and confines each draw
    # to a gap, the snap reproduces the day-unit rule exactly, so
    # withdrawing either rule alone leaves the same twin. A mutant whose
    # branch is genuinely redundant cannot move a byte, and pretending
    # otherwise would be the "guard that passes" this file exists to
    # refuse. So this case now holds up the PLACEMENT rule, which is
    # load-bearing for it, and the day-unit rule's own frozen mutant is
    # recorded as withdrawn in G14.3.
    "midnight_days": Mutant(
        branch="G7.3's placement as landing 2b.6 rewrites it, on a column "
        "counted in whole days: the nine interior rungs pinned to their "
        "PUBLISHED values and every other rank drawn inside the gap "
        "between the pinned ranks either side of it; the mutant restores "
        "the withdrawn stratified placement and the interior days move",
        attribute="spread_ordinals",
        replacement=_stratified_ranks,
        outcome=CHANGES_THE_CELLS,
    ),
    "mixed_conventions": Mutant(
        branch="P4-D65.2's census of notations, spent cell by cell over the "
        "negative cells; the mutant writes every negative in the column's "
        "majority, brackets, which is what the twin wrote before that "
        "decision and is the defect it repairs",
        attribute="notation_places",
        replacement=_notations_from_the_majority,
        outcome=CHANGES_THE_CELLS,
    ),
    "mixed_marks": Mutant(
        branch="P4-D39's rotation, which spreads the census of marks evenly "
        "over the ranks; the mutant spends the names from the first rank "
        "upward, and the marks cluster by date",
        attribute="_separator_allocation",
        replacement=_marks_from_the_first_rank,
        outcome=CHANGES_THE_CELLS,
    ),
    "pooled_marks": Mutant(
        branch="landing 2b.3's withheld pool, which is written with the marks "
        "the census leaves unnamed; the mutant puts it back on the commonest "
        "named mark, and the space and the t the pool stood for are erased",
        attribute="mark_weights",
        replacement=_named_counts_only,
        outcome=CHANGES_THE_CELLS,
    ),
    "slashed_pool": Mutant(
        branch="landing 2b.3's permitted marks, a space alone on a slashed "
        "stamp; the mutant offers the pool all three, and the cells take marks "
        "no such table writes",
        attribute="permitted_marks",
        replacement=_three_marks_everywhere,
        outcome=CHANGES_THE_CELLS,
    ),
    "midnight_mixed_forms": Mutant(
        branch="the narrowing of owner decision 4, which writes the bare-date "
        "ranks of a joint column counted in days as bare dates; the mutant "
        "writes every rank as a moment",
        attribute="form_allocation",
        replacement=_every_rank_a_moment,
        outcome=CHANGES_THE_CELLS,
    ),
    "partial_midnight": Mutant(
        branch="landing 2b.3's move onto midnight; the mutant keeps the "
        "interpolated instants, and the values at midnight owed are not written",
        attribute="snapped_to_midnight",
        replacement=_no_move_onto_midnight,
        outcome=CHANGES_THE_CELLS,
    ),
    "midnight_two_offsets": Mutant(
        branch="landing 2b.3's reading of a column wholly at local midnight "
        "on the shared clock, counted in seconds and moved onto a midnight of "
        "each rank's own offset; the mutant counts it in days, and a rung "
        "published at 23:00 lands on the day before",
        attribute="ordinal_space",
        replacement=_days_on_either_clock,
        outcome=CHANGES_THE_CELLS,
    ),
    "midnight_bare_offsets": Mutant(
        branch="the repair pass of landing 2b.3, which settles the form and "
        "the offset of every rank whose instant the published tail fixes "
        "before the rotation; the mutant settles the two ends alone, and rung "
        "ranks are written as the day before and at T02:00:00+02:00",
        attribute="instant_offsets",
        replacement=_ends_alone,
        outcome=CHANGES_THE_CELLS,
    ),
    "leap_second_endpoint": Mutant(
        branch="G7.5's endpoint route, which builds the two ends from the "
        "published endpoint's own fields; the mutant sends them back "
        "through the ordinal space of G7.1, which has no place for a "
        "seconds field of 60",
        attribute="endpoint_cell",
        replacement=_through_the_ordinal_space,
        outcome=CHANGES_THE_CELLS,
    ),
    "mixed_parsed_unparsed": Mutant(
        branch="G10.4's stand-ins, which are counted rather than "
        "reproduced; the mutant copies a parsed cell into their place and "
        "the three unparsed cells read back as dates",
        attribute="text_stand_ins",
        replacement=_reproduce_instead_of_standing_in,
        outcome=CHANGES_THE_CELLS,
    ),
    "numeric_decimal_styles": Mutant(
        branch="G6.2's canonical spelling at the two boundaries of the "
        "fixed-point window; the mutant drops the two-digit exponent rule, "
        "and the pinned smallest value stops writing `1e-05`",
        attribute="_exponent_form",
        replacement=_a_one_digit_exponent,
        outcome=CHANGES_THE_CELLS,
    ),
    "numeric_integer": Mutant(
        branch="G5.4's integer rule, to nearest with ties toward POSITIVE "
        "INFINITY; the mutant rounds ties toward zero, and the four strata "
        "sitting on exactly 2.5 write 2 instead of 3",
        attribute="integer_rule",
        replacement=_ties_toward_zero,
        outcome=CHANGES_THE_CELLS,
    ),
    "numeric_pooled_spelling": Mutant(
        branch="owner decision 10's point-free spelling at any width, and "
        "the pooled cell spelled by its own value beside it; the mutant "
        "puts the sixteen-figure ceiling back, so a whole value wider than "
        "the canonical window is told it has no point-free spelling",
        attribute="point_free_spelling",
        replacement=_point_free_within_the_old_window,
        outcome=CHANGES_THE_CELLS,
    ),
    "numeric_point_free_styles": Mutant(
        branch="G6.1's literal placements, where a cell named `decimal` "
        "carries a point and one named `leading_plus` a `+`; the mutant "
        "sends the whole published map to one form",
        attribute="_effective_style_map",
        replacement=_one_style_for_the_whole_map,
        outcome=CHANGES_THE_CELLS,
    ),
    "offset_bearing": Mutant(
        branch="G7.4's clock conversion, which is not optional: a "
        "published instant is written on the wall clock of the offset its "
        "own cell carries; the mutant writes the instant itself",
        attribute="offset_form",
        replacement=_no_clock_conversion,
        outcome=CHANGES_THE_CELLS,
    ),
    "quarter": Mutant(
        branch="G7.5's quarter form and the quarter ordinal; the mutant "
        "counts the quarter from nought and every cell moves",
        attribute="precision_form",
        replacement=_zero_based_quarter,
        outcome=CHANGES_THE_CELLS,
    ),
    "month_span": Mutant(
        branch="G7.1's month ordinal and G7.5's month cell form; the "
        "mutant writes the month as the first day of that month, which "
        "is the day space the month must not fall into, and every cell "
        "moves",
        attribute="precision_form",
        replacement=_month_as_a_day,
        outcome=CHANGES_THE_CELLS,
    ),
    "unrepresentable_joint": Mutant(
        branch="G10.5's three margins packed together on the six-row "
        "column of its step 2; the mutant withdraws the too-small shape, "
        "which is what spending `n_whole` on the too-large cells amounts "
        "to, and the column has no packing at all",
        attribute="UNREPRESENTABLE_SHAPES",
        replacement=tuple(
            shape for shape in gen.UNREPRESENTABLE_SHAPES if shape[0] != "too_small"
        ),
        outcome="no assignment of whole groups meets every quota",
    ),
    "unrepresentable_exponent": Mutant(
        branch="G10.5 revision 5's exponent spelling family; the mutant "
        "puts the too-large shape's floor back to the digit string's own "
        "310 characters, which is the rule revision 4 carried, and the "
        "column published at five and six characters is then written "
        "three hundred and ten wide with neither published end held",
        attribute="EXPONENT_LARGE_ROOM",
        replacement=gen.OVERFLOW_FIGURES,
        outcome="recount min_length as 310",
    ),
}


def test_withdrawing_the_layout_offer_stops_the_oracle(monkeypatch) -> None:
    """The layout census is EXACT-OBSERVABLE, and the oracle holds itself to it.

    The registered mutant of `identifier_layout` withdraws the ROTATION,
    which moves cells. Withdrawing the OFFER altogether is a different
    reversal and is held up here: the twenty-four cells then come from
    the band enumeration, wear no published layout, and the recount of
    contract 7.12 stops the oracle before any byte could be written.
    """
    before, _claims = gen.build_case("identifier_layout")
    assert before["cells"]
    monkeypatch.setattr(gen, "layout_offer", _no_layout_offered)
    with pytest.raises(AssertionError) as refusal:
        gen.build_case("identifier_layout")
    assert "wear the layout '@%%%%%' 0 times" in str(refusal.value)


def test_the_mutant_table_names_every_case_and_nothing_else() -> None:
    """The keys ARE the case set, which is what closes the gap.

    Review item P2-C4-C2: four of thirteen cases carried an own-branch
    mutant, and the claim that all thirteen were covered rested on a
    sentence rather than on a check. This is the check. A case added to
    either committed file without a mutant beside it turns it red, and so
    does a mutant left behind by a case that has gone.
    """
    assert tuple(sorted(CASE_MUTANTS)) == ALL_CASES


@pytest.mark.parametrize("name", ALL_CASES)
def test_each_case_fails_when_its_own_branch_is_reverted(
    name: str, monkeypatch
) -> None:
    """Every case, put through the rule the method rules out for it.

    A case that would still be written after its own rule was withdrawn
    is a case that tests nothing (G14.3). Each mutant must therefore move
    its case's cells or stop the oracle from building it -- and the
    unmutated build above it is the vacuity check: a mutant that passed
    because the case cannot be built at all would prove nothing either.
    """
    mutant = CASE_MUTANTS[name]
    before, _claims = gen.build_case(name)
    assert before["cells"], f"{name} builds no cells unmutated"
    monkeypatch.setattr(gen, mutant.attribute, mutant.replacement)
    for attribute, replacement in mutant.also:
        monkeypatch.setattr(gen, attribute, replacement)
    # THE ORACLE'S OWN DISTINCT RECOUNT IS NOT ASKED OF A MUTATED BUILD
    # (plan P4-D237). It proves that a case's cells hold the counts the
    # case publishes; a mutant that moves those counts would stop the
    # oracle where this battery is there to see the cells MOVE.
    monkeypatch.setattr(gen, "RECOUNT_DISTINCT", False)
    if mutant.outcome == CHANGES_THE_CELLS:
        after, _mutant_claims = gen.build_case(name)
        assert after["cells"] != before["cells"], (
            f"{name} is written the same way with its own branch reverted "
            f"({mutant.branch}), so no committed byte holds that branch up"
        )
    else:
        with pytest.raises(AssertionError) as refusal:
            gen.build_case(name)
        assert mutant.outcome in str(refusal.value), (
            f"{name}: the mutant of {mutant.branch} stopped the oracle for "
            "some other reason than its own"
        )


_GENERATOR_NEAREST_HELD_UNIT = generation._nearest_held_unit


def _no_unit_past_the_neighbours(*arguments, **named):
    """The generator's plain merge offered its rank neighbours alone.

    The traded merge asks the same search with ``flip`` set, and keeps
    it: only the offer of a held unit of the run's OWN kind is withdrawn.
    ``flip`` is the thirteenth positional argument since the search took
    its sorted ``order`` after ``spot`` (K-2B-14).
    """
    flip = arguments[12] if len(arguments) > 12 else named.get("flip", False)
    if flip:
        return _GENERATOR_NEAREST_HELD_UNIT(*arguments, **named)
    return None


@pytest.mark.parametrize(
    ("name", "attribute", "replacement"),
    [
        ("date_two_kinds_traded", "_traded_merges", lambda *arguments: 0),
    ],
)
def test_the_generator_s_own_merge_writes_the_two_kinds_cases(
    name: str, attribute: str, replacement, tmp_path: pathlib.Path, monkeypatch
) -> None:
    """P4-D258's traded merge, withdrawn from the IMPLEMENTATION this time.

    The mutant table above withdraws the merge from the oracle. This is
    the same question asked of `synthtwin.generation`: its own traded
    merge is what writes this committed column, so withdrawing it writes
    different cells -- which is what makes the case a pin on the
    generator and not only on the oracle beside it.

    THE SECOND ROW OF THIS TABLE IS GONE (stage 3, plan P4-D328). It
    asked the same of P4-D258's offer of a held unit past the rank
    NEIGHBOURS, on `date_two_kinds_nonadjacent` -- a column of
    thirty-six dates on three days, which at a floor of eleven now
    publishes no tail, no rung and no value of the table at all
    (P4-D330). Its twin is the ramp, which places one rank to a step
    over the published count of different values, so no run is left for
    any merge to move and neither implementation reaches the branch. The
    loss is recorded in the generation method's G14.3 beside that case's
    row, and the case holds up the ramp's own START instead.
    """
    case = _case(name)
    profile = _load(case, name, tmp_path)
    assert [row[0] for row in generation.generate(profile, SEEDS[name]).rows] == (
        case["cells"]
    )
    monkeypatch.setattr(generation, attribute, replacement)
    withdrawn = [row[0] for row in generation.generate(profile, SEEDS[name]).rows]
    assert withdrawn != case["cells"], name


def test_the_generator_s_own_joint_word_keeps_the_named_one_field_count(
    tmp_path: pathlib.Path, monkeypatch
) -> None:
    """Method G7.5 step 1's joint word for a rank showing both fields.

    The repair pass of the carried date items of 2026-09-18 (plan
    P4-D294, amended). Where the census names a one-field word and no
    joint word, a rank of the twin showing both fields is written in the
    convention no named one-field word wears. Asked of the committed cells
    the way the producer counts them -- tallied, folded, absorbed -- they
    give back the named count exactly, with the third of March counted
    under a joint word of its own. Withdrawn from `synthtwin.generation`
    itself, the joint word that AGREES with the census is written instead
    and the fold takes the named count away: the committed cells move, and
    the moved cells count no `second-field-padded` at all.
    """
    name = "date_both_fields_disagree"
    case = _case(name)
    member = case["column"]["format"]

    def census_of(cells: "list[str]") -> "dict[str, int]":
        written = [cell for cell in cells if cell]
        folded = parsing.folded_width_tally(taxonomy.width_tally(written, member))
        return taxonomy.absorbed_width_tally(folded, len(written))

    profile = _load(case, name, tmp_path)
    kept = [row[0] for row in generation.generate(profile, SEEDS[name]).rows]
    assert kept == case["cells"]
    assert census_of(kept) == {"first-padded": 14, "second-field-padded": 22}
    monkeypatch.setattr(
        generation, "_both_fields_width_of", generation._joint_width_of
    )
    moved = [row[0] for row in generation.generate(profile, SEEDS[name]).rows]
    assert moved != case["cells"]
    assert census_of(moved) == {"padded": 36}


def test_the_style_case_writes_each_published_form_as_itself() -> None:
    """The claim `numeric_point_free_styles` freezes, beside its mutant.

    A cell named `decimal` carries a point, one named `leading_plus` a
    `+` and one named `leading_zero` a redundant `0`, each recounted by
    the contract's own first-match ladder. This is the affirmative half;
    the table above holds the mutant that sends the whole map to one
    form, which is the silent change of the reader's inferred type that
    owner decision 10 was taken to close.
    """
    case, _claims = gen.build_case("numeric_point_free_styles")
    written = dict.fromkeys(gen.STYLE_ORDER, 0)
    for cell in case["content"]:
        written[parsing.numeric_style(cell)] += 1
    published = _unwrap(case["column"])["numeric_styles"]
    assert {name: count for name, count in written.items() if count} == published


def _every_empty_record_at_the_top(form, n_rows):
    """G2.1's placing withdrawn: every record holding nothing leading.

    The rule puts `leading` at the top, `trailing` at the bottom and
    `interior` spread evenly between; this puts all of them at the top,
    which is the arrangement a reader would take for a table whose first
    rows were lost.
    """
    empties = form["empty_rows"]
    total = empties["interior"] + empties["leading"] + empties["trailing"]
    targets = [False for _row in range(n_rows)]
    for row in range(min(total, n_rows)):
        targets[row] = True
    return targets


def _one_reading_for_each_candidate(text, candidate, at):
    """CODEX-5 withdrawn: one reading per candidate, settings afterwards.

    The walk this replaced read each candidate ONE way -- no space after
    the delimiter, doubled quotes -- and left the spacing and the
    escaping to be settled from the delimiter it had already chosen.
    """
    sample = gen.doc_read_records(
        text, candidate, gen.DOC_ESCAPE_DOUBLED, False, at,
        gen.DOC_SAMPLE_RECORDS,
    )
    at_width, total, width = gen.width_share(sample)
    if width < 2:
        return None
    opening = 0
    while opening < len(sample) and gen.leads_the_table(sample[opening]):
        opening = opening + 1
    if opening < len(sample) and len(sample[opening]["fields"]) != width:
        return None
    return {"at_that_width": at_width, "records": total, "width": width}


def _classed_by_their_characters(census, cells, value_class=None):
    """G2.2 withdrawn: a cell's class read off the twin's own characters.

    This is the defect the whole seam exists to prevent: the census says
    the column held TEXT, its cells are digit strings, and a twin written
    this way hands a reader a column of numbers where the source had
    codes.
    """
    out = []
    for cell in cells:
        if cell == "":
            out += ["absent"]
            continue
        out += ["number" if gen.sheet_number_spelling(cell) else "text"]
    return out


def _without_the_published_value_class(census, cells, value_class=None):
    """G2.2 step 1 withdrawn: the published commonest class is ignored."""
    return _SHIPPED_CELL_CLASSES(census, cells, None)


def _every_unclaimed_kind_plain(census, classes, format_code="General", dated=None):
    """G2.2 step 2 withdrawn: a cell no count claims is written plain."""
    return _SHIPPED_FORMAT_KINDS(census, classes, "General", dated)


def _names_taken_by_their_exact_spelling(published):
    """G2.2 step 9 withdrawn: a placeholder is compared as written."""
    taken = {name: True for name in published if name is not None}
    out = []
    for index in range(len(published)):
        if published[index] is not None:
            out += [published[index]]
            continue
        number = index + 1
        while f"Sheet{number}" in taken:
            number = number + 1
        taken[f"Sheet{number}"] = True
        out += [f"Sheet{number}"]
    return out


def _carriage_return_written_raw(text):
    """G2.2 step 11 withdrawn: a carriage return is written as itself."""
    out = text
    for mark, written in (
        ("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"), ('"', "&quot;"),
    ):
        out = out.replace(mark, written)
    return out


_SHIPPED_CELL_CLASSES = gen.sheet_cell_classes
_SHIPPED_FORMAT_KINDS = gen.sheet_format_kinds
# The reading of G9.2 this file held until plan P4-D234: the whole word
# counted over the alphabet, with the band's leading rule applied by
# substitution afterwards. It is the registered mutant of
# `code_band_words` and nothing else.
_SHIPPED_ENUMERATED_SPELLING = gen.enumerated_spelling


# ----------------------------------------- the document cases, bound

# THE FIVE TRANSFORMS THAT PRODUCE A WHOLE DOCUMENT (landing 2b.17).
# Every case above answers "what does one COLUMN hold". These five
# answer "what does the FILE look like", and until this landing not one
# of them had a second implementation of any kind: landings 2b.9, 2b.10
# and 2b.11 built the written form, the row arrangement and the workbook
# writer, each recorded the gap in its own report, and none could close
# it -- the workbook writer's rules were stated in no specification at
# all, so there was nothing to write a second implementation FROM. Method
# section G2.2 was written at this landing for that reason, and these
# bind the oracle written from it to the shipped code.
#
# A document case carries no column, no words and no word budget, so it
# is NOT in `ALL_CASES` and the parametrized tests above do not reach it.
# Its own bindings are below, one per transform, and its own mutant table
# is at the foot of this file beside the other.
DOCUMENT_CASES = (
    "delimiter_reading",
    "row_arrangement",
    "withheld_line_marks",
    "workbook_as_written",
    "workbook_classes_by_spelling",
    "workbook_made_up_dates",
    "workbook_sheet",
    "written_form_classes",
    "written_form_lines",
)

EVERY_CASE = tuple(sorted(ALL_CASES + DOCUMENT_CASES))

# WHICH TEST BINDS WHICH DOCUMENT CASE, stated once so that coverage is
# derived from the transforms and not from how many cases happen to be
# stored (round-2 ledger item 3). The KPI ledger promised "every frozen
# case" (K-P2-01) and "each document binding" (K-2B-39) while pinning
# neither `written_form_classes`, `withheld_line_marks` nor
# `delimiter_reading`: measured at 05e7d89, moving
# `dialect.cell_class("NaT")` from absent to text left all 103 pinned
# cases of those two entries green -- the 98 column cases, the four
# workbook cases, the case-count checks and the three document pins --
# while the unpinned `written_form_classes` binding failed at once
# against the frozen bytes. `tests/test_kpi_ledger_integrity.py` holds
# the ledger to pinning every node named here.
DOCUMENT_BINDINGS = {
    "delimiter_reading":
        "tests/test_generation_reference.py::"
        "test_the_delimiter_is_settled_the_way_the_method_settles_it",
    "row_arrangement":
        "tests/test_generation_reference.py::"
        "test_the_rows_stand_where_the_method_puts_them",
    "withheld_line_marks":
        "tests/test_generation_reference.py::"
        "test_the_lines_before_the_table_are_published_as_their_shape",
    "workbook_as_written":
        "tests/test_generation_reference.py::"
        "test_the_workbook_twin_is_the_package_the_method_requires",
    "workbook_classes_by_spelling":
        "tests/test_generation_reference.py::"
        "test_the_workbook_twin_is_the_package_the_method_requires",
    "workbook_made_up_dates":
        "tests/test_generation_reference.py::"
        "test_the_workbook_twin_is_the_package_the_method_requires",
    "workbook_sheet":
        "tests/test_generation_reference.py::"
        "test_the_workbook_twin_is_the_package_the_method_requires",
    "written_form_classes":
        "tests/test_generation_reference.py::"
        "test_each_cell_is_quoted_under_the_rule_of_its_own_class",
    "written_form_lines":
        "tests/test_generation_reference.py::"
        "test_the_written_form_is_the_file_the_method_requires",
}


def _document_document() -> dict:
    return json.loads(DOCUMENT_VECTORS.read_text(encoding="utf-8"))


def _document_case(name: str) -> dict:
    return _document_document()["cases"][name]


def _form_of(case: dict) -> "dialect.Dialect":
    """One case's published dialect block, typed by the shipped loader.

    The block is the INPUT the written form and the arrangement really
    take, so the loader that reads it is the right way in: a block this
    oracle wrote that the loader would refuse is a block no description
    could carry, and that would be worth knowing here rather than later.
    """
    return contract._dialect_block(case["dialect"])


def test_the_written_form_is_the_file_the_method_requires() -> None:
    """Method G2, byte for byte, against a file the oracle wrote alone.

    The whole text is one assertion and the lines are another, and they
    are kept apart on purpose: a disagreement about the BYTES BETWEEN
    lines -- an ending, the mark, the end-of-file byte -- is a different
    defect from a disagreement about what a line holds, and a single
    comparison of the finished text would report either as the other.
    """
    case = _document_case("written_form_lines")
    form = _form_of(case)
    names = tuple(case["names"])
    rows = tuple(tuple(row) for row in case["rows"])
    assert dialect.twin_text(names, rows, case["write_header"], form) == (
        case["text"]
    ), (
        "the twin's bytes are not the ones method section G2 requires. The "
        "oracle is the specification's answer; do not change it to match "
        "the implementation."
    )
    # ...and each line, through the shipped writer's own parts, so that a
    # failure names which line rather than which file.
    lines = list(case["lines"])
    at = 0
    assert lines[at] == "sep=" + form.delimiter
    at = at + 1
    for run in form.preamble:
        for _line in range(run.lines):
            assert lines[at] == dialect.preamble_line(run)
            at = at + 1
    assert lines[at] == dialect.header_line(names, form)
    at = at + 1
    written = [line for line in lines[at:] if line != ""]
    for index in range(len(rows)):
        assert written[index] == dialect.data_line(rows[index], form)


def test_each_cell_is_quoted_under_the_rule_of_its_own_class() -> None:
    """Method G2's quoting per cell class, on the classes that disagree.

    Files review MAJOR 19 (plan P4-D173): the case above holds no number
    and no absent cell in its column of differing rules, so the oracle's
    reading of those two classes was never held to the product's. This
    case writes both beside text and empty cells at each class's edge --
    `.5`, `2.5e3`, `0012`; `-`, `?`, `#N/A`, spaces, `NaT` beside `nat` --
    and the shipped writer must write the bytes the oracle wrote alone.
    """
    case = _document_case("written_form_classes")
    form = _form_of(case)
    names = tuple(case["names"])
    rows = tuple(tuple(row) for row in case["rows"])
    assert dialect.twin_text(names, rows, case["write_header"], form) == (
        case["text"]
    ), (
        "a cell is quoted under another class's rule than method section G2 "
        "gives it. The oracle is the specification's answer; do not change "
        "it to match the implementation."
    )
    for index in range(len(rows)):
        for place in range(len(names)):
            cell = rows[index][place]
            assert dialect.cell_class(cell) == gen.written_cell_class(cell), cell


def _absence_read_from_seven_spellings(text):
    """The vocabulary this mirror held before plan P4-D173: seven spellings."""
    body = text.strip().casefold()
    return body in ("na", "n/a", "nan", "null", "none")


def test_the_rows_stand_where_the_method_puts_them() -> None:
    """Method G2.1, both halves, against the shipped arrangement.

    Two arrangements, because no one file can carry both rules: contract
    FD5 refuses records holding nothing beside a row sequence, and a
    table with a row order publishes records holding nothing only where
    it has some.
    """
    case = _document_case("row_arrangement")
    for entry in case["arrangements"]:
        form = contract._dialect_block(entry["dialect"])
        columns = [tuple(column) for column in entry["columns"]]
        placed = dialect.arranged(columns, form, entry["n_rows"])
        assert [list(column) for column in placed] == entry["arranged"], (
            entry["why"]
        )


def test_the_lines_before_the_table_are_published_as_their_shape() -> None:
    """Contract FD11 and plan P4-D83, on the two marks a twin cannot write.

    Three rules in one case, asserted one at a time: what a line's shape
    is, what the mark is narrowed to, and what the twin writes for it.
    """
    case = _document_case("withheld_line_marks")
    delimiter = case["delimiter"]
    runs = dialect.preamble_runs(list(case["lines"]), delimiter)
    published = [
        {"kind": run.kind, "lines": run.lines, "mark": run.mark}
        for run in runs
    ]
    assert published == case["runs"]
    written: list = []
    for run in runs:
        for _line in range(run.lines):
            written += [dialect.preamble_line(run)]
    assert written == case["written"]
    # The narrowing itself, line by line, so that a failure names the
    # line whose mark the twin could not have written.
    for index in range(len(case["lines"])):
        line = case["lines"][index]
        kind, mark = dialect.writable_shape(
            *dialect.preamble_shape(line), delimiter
        )
        assert not dialect.mark_breaks_a_line(mark, delimiter), line
        assert written[index] == dialect.preamble_line(
            dialect.PreambleRun(kind=kind, lines=1, mark=mark)
        )


def test_the_delimiter_is_settled_the_way_the_method_settles_it() -> None:
    """Review item CODEX-5, on the file the item was measured on.

    Each candidate's own best reading is asserted before the choice
    between them, because the defect that item found was in the SCORING
    and not in the comparison: a candidate scored one way reads a
    two-column file as one column, and the comparison then picks
    correctly between two wrong answers.
    """
    case = _document_case("delimiter_reading")
    text = case["text"]
    for candidate in dialect.DELIMITERS:
        found = dialect._best_reading(text, candidate, 0)
        published = case["readings"][candidate]
        if published is None:
            assert found is None, candidate
            continue
        assert found is not None, candidate
        share, width, _sample = found
        assert width == published["width"], candidate
        assert share == published["at_that_width"] / published["records"], (
            candidate
        )
    assert dialect.detected_delimiter(text, 0) == case["delimiter"]


def _workbook_profile(case: dict, folder: pathlib.Path) -> contract.Profile:
    """A description carrying this case's workbook block, loaded.

    THE COLUMN BLOCKS ARE INERT HERE, and it is said rather than left to
    be discovered: `sheetwriting.workbook_members` reads
    `source.workbook` and the twin's own cells, and never a column
    block's published facts. Two are carried because a description must
    have one per column and the loader holds the workbook block to that
    count (contract WB1); they are one frozen case's own column, twice,
    so that nothing about them was invented here.
    """
    block = case["workbook"]
    borrowed = _unwrap(_case("spaced_brackets")["column"])
    columns = []
    for index in range(len(case["names"])):
        column = dict(borrowed)
        column["name"] = case["names"][index]
        column["position"] = index + 1
        columns += [column]
    document = {
        "columns": columns,
        "created_with": "0+unknown",
        "n_columns": len(columns),
        "n_rows": case["n_rows"],
        "profile_version": 6,
        "publication_notes": [],
        "relationships": _relationships(),
        "settings": _settings([]),
        "source": {
            "dialect": dialect.document_of(
                dialect.ordinary(len(columns), case["n_rows"], True)
            ),
            "encoding": "utf-8-sig",
            "used_fallback_encoding": False,
            "header_source": "file",
            "header_by_convention": False,
            "header_evidence": "the first row of the sheet held the "
            "columns' names.",
            "workbook": block,
        },
    }
    path = fixtures.write_profile(folder, "workbook.json", document)
    return contract.load_profile(str(path))


def test_the_workbook_twin_is_the_package_the_method_requires(
    tmp_path: pathlib.Path,
) -> None:
    """Method G2.2, part by part, against a package the oracle wrote alone.

    The twin is built by hand from the case's own cells rather than
    generated, and that is what the transform takes: the writer is
    handed a description and a twin's CELLS, and turns them into the
    parts of a package. Nothing about which cells a column generator
    would produce is in question here, and a case that generated them
    would be testing two transforms at once.
    """
    for name in (
        "workbook_sheet",
        "workbook_classes_by_spelling",
        "workbook_as_written",
        "workbook_made_up_dates",
    ):
        _package_matches(_document_case(name), tmp_path / name)


def _package_matches(case: dict, folder: pathlib.Path) -> None:
    """One workbook case's package, part by part, against the product's."""
    folder.mkdir()
    profile = _workbook_profile(case, folder)
    columns = tuple(tuple(column) for column in case["cells"])
    rows = tuple(
        tuple(columns[place][row] for place in range(len(columns)))
        for row in range(case["n_rows"])
    )
    twin = generation.Twin(
        names=tuple(case["names"]),
        write_header=case["write_header"],
        n_rows=case["n_rows"],
        columns=columns,
        rows=rows,
        outcomes=(),
        deviations=(),
        approximations=(),
        remarks=(),
        words_drawn=0,
        seed=0,
    )
    members = sheetwriting.workbook_members(profile, twin)
    assert [name for name, _text in members] == case["members"], (
        "the parts of the twin's package, or their order, are not the "
        "ones method section G2.2 requires"
    )
    for name, text in members:
        assert text == case["parts"][name], name


def _row_order_format_kinds(census: dict, classes: list) -> list:
    """G2.2 step 2 as it stood before a date format went to a date first."""
    written = [
        index for index in range(len(classes)) if classes[index] != "absent"
    ]
    out = ["plain" for _index in range(len(classes))]
    at = 0
    for kind in ("date", "datetime", "time", "elapsed", "text"):
        found = census.get(kind)
        left = found if isinstance(found, int) else 0
        while left > 0 and at < len(written):
            out[written[at]] = kind
            at = at + 1
            left = left - 1
    return out


DOCUMENT_MUTANTS = {
    "written_form_classes": (
        Mutant(
            branch="G2's rule that a cell takes the quoting of its OWN "
            "class; the mutant writes every cell under its column's text "
            "rule, and the numbers and absent cells of both columns move",
            attribute="quoting_rule_for",
            replacement=lambda column, cell: column["quoting"]["text"],
            outcome=CHANGES_THE_CELLS,
        ),
        Mutant(
            branch="contract 5.4.1's whole vocabulary of absence as G2's "
            "absent class; the mutant reads absence from the seven "
            "spellings this mirror used to hold, and `-`, `?`, `#N/A`, the "
            "spaces and `NaT` are quoted as text",
            attribute="doc_reads_as_nothing",
            replacement=_absence_read_from_seven_spellings,
            outcome=CHANGES_THE_CELLS,
        ),
    ),
    "written_form_lines": (
        Mutant(
            branch="G2's lines before the table; the mutant writes none "
            "of them, which is what withdrawing the stand-in amounts to, "
            "and the file loses four lines",
            attribute="preamble_lines_for",
            replacement=lambda form: [],
            outcome=CHANGES_THE_CELLS,
        ),
    ),
    "row_arrangement": (
        Mutant(
            branch="G2.1's rule that a row-sequence column is written in "
            "place LAST; the mutant withdraws that step and the sequence "
            "column keeps the generated cells the sort moved",
            attribute="sequence_columns_written",
            replacement=lambda grid, form, n_rows: None,
            outcome=CHANGES_THE_CELLS,
        ),
        Mutant(
            branch="G2.1's placing of the records holding nothing -- "
            "leading at the top, trailing at the bottom, interior spread "
            "evenly between; the mutant puts every one of them at the top",
            attribute="empty_record_targets",
            replacement=_every_empty_record_at_the_top,
            outcome=CHANGES_THE_CELLS,
        ),
    ),
    "withheld_line_marks": (
        Mutant(
            branch="plan P4-D83's narrowing of a mark the twin could not "
            "write; the mutant hands back the shape unchanged, and the "
            "twin's first line is then a quoted field nothing closes",
            attribute="writable_mark",
            replacement=lambda kind, mark, delimiter: (kind, mark),
            outcome=CHANGES_THE_CELLS,
        ),
    ),
    "delimiter_reading": (
        Mutant(
            branch="review item CODEX-5's rule that every setting is "
            "scored WITH the delimiter; the mutant scores each candidate "
            "one way -- no space skipped, doubled quotes -- which is the "
            "rule it replaced, and the file is read as one column",
            attribute="best_reading",
            replacement=_one_reading_for_each_candidate,
            outcome=CHANGES_THE_CELLS,
        ),
    ),
    "workbook_as_written": (
        Mutant(
            branch="G2.2 step 1's rule that a count is spread over the "
            "cells a class fits where more fit than it names (plan "
            "P4-D187); the mutant hands it out in row order, and the "
            "first column's eleven text cells stand in its last eleven rows",
            attribute="sheet_spread_over",
            replacement=lambda fitting, wanted: list(fitting[:max(wanted, 0)]),
            outcome=CHANGES_THE_CELLS,
        ),
        Mutant(
            branch="G2.2 step 3's rule that a published code's kind is read "
            "off the code (plan P4-D189); the mutant looks it up in the "
            "closed map of built-in and canonical codes, and the third "
            "column's moments wear the canonical datetime code instead of "
            "the code the source wrote",
            attribute="sheet_code_kind",
            replacement=lambda code: gen.SHEET_FORMAT_CODE_KINDS.get(code, "plain"),
            outcome=CHANGES_THE_CELLS,
        ),
        Mutant(
            branch="G2.2 step 0's rule that a cell the census stores as "
            "a DATE keeps its ISO text and only a cell to be stored as a "
            "number becomes a day count (plan P4-D284); the mutant "
            "converts every date, as the rule it replaced did, and the "
            "fourth column's twenty-two `t=\"d\"` cells are written as "
            "text holding day counts instead",
            attribute="sheet_stores_dates",
            replacement=lambda column: False,
            outcome=CHANGES_THE_CELLS,
        ),
    ),
    "workbook_made_up_dates": (
        Mutant(
            branch="G2.2 step 0a's rule that a column the description "
            "stores as dates has its made-up cells brought onto the "
            "calendar before anything is allocated (plan P4-D291); the "
            "mutant hands every cell back as it came, and the first "
            "column's sixteen cells that name no day fit no class but "
            "`text` and are written as shared strings instead of date "
            "cells",
            attribute="sheet_on_the_calendar",
            replacement=lambda text: text,
            outcome=CHANGES_THE_CELLS,
        ),
        Mutant(
            branch="G2.2 step 1's rule that the `date` class fits only a "
            "cell naming a day of the calendar (plan P4-D291); the "
            "mutant asks the SHAPE alone, as the rule it replaced did, "
            "and the third column's twenty made-up cells are written as "
            'date cells (`t="d"`) holding days no month has -- which is '
            "the twin openpyxl could not open at all",
            attribute="sheet_date_is_real",
            replacement=lambda text: gen.sheet_is_iso_date(text),
            outcome=CHANGES_THE_CELLS,
        ),
    ),
    "workbook_classes_by_spelling": (
        Mutant(
            branch="G2.2 step 1's rule that a class goes only to a cell "
            "it FITS; the mutant lets every class fit every cell, and the "
            "first column's error and boolean counts land on its labels "
            "in row order again",
            attribute="sheet_fits",
            replacement=lambda kind, text: True,
            outcome=CHANGES_THE_CELLS,
        ),
        Mutant(
            branch="G2.2 step 1's rule that a withheld census falls to "
            "the column's published commonest class; the mutant ignores "
            "it, and the second column's digit strings are written as "
            "numbers",
            attribute="sheet_cell_classes",
            replacement=_without_the_published_value_class,
            outcome=CHANGES_THE_CELLS,
        ),
        Mutant(
            branch="G2.2 step 2's rule that a cell no count claims wears "
            "its published code's kind where that kind was withheld; the "
            "mutant writes it plain, and the third column's dates lose "
            "their format",
            attribute="sheet_format_kinds",
            replacement=_every_unclaimed_kind_plain,
            outcome=CHANGES_THE_CELLS,
        ),
        Mutant(
            branch="G2.2 step 9's rule that a sheet name is taken whatever "
            "its case; the mutant compares names as written, and the "
            "withheld sheet's placeholder is `Sheet2` beside `sheet2`",
            attribute="sheet_twin_names",
            replacement=_names_taken_by_their_exact_spelling,
            outcome=CHANGES_THE_CELLS,
        ),
        Mutant(
            branch="G2.2 step 11's character reference for a carriage "
            "return; the mutant writes it raw, and the first column's "
            "name reaches a reader with a line feed in it",
            attribute="sheet_escaped",
            replacement=_carriage_return_written_raw,
            outcome=CHANGES_THE_CELLS,
        ),
    ),
    "workbook_sheet": (
        Mutant(
            branch="G2.2's rule that a cell's class comes from the "
            "column's published census and never from the twin's own "
            "characters; the mutant classes each cell by what its "
            "characters could be read as, and a column of text whose "
            "cells are digit strings is written as numbers",
            attribute="sheet_cell_classes",
            replacement=_classed_by_their_characters,
            outcome=CHANGES_THE_CELLS,
        ),
        Mutant(
            branch="G2.2's rule that a date the reader took out of a date "
            "cell is written back as the day count it was read as; the "
            "mutant writes the date as text, which every reader then "
            "hands back as text",
            attribute="sheet_dates_as_day_counts",
            replacement=lambda column, own, epoch_1904, stored=(): (
                list(own), ["" for _cell in own]
            ),
            outcome=CHANGES_THE_CELLS,
        ),
        Mutant(
            branch="G2.2's rule that a date format goes to a date first and "
            "that a date left over keeps a date format the census does not "
            "deny; the mutant hands the formats out in row order alone, "
            "and dates are written wearing the general format",
            attribute="sheet_format_kinds",
            replacement=lambda census, classes, format_code="General", dated=None: (
                _row_order_format_kinds(census, classes)
            ),
            outcome=CHANGES_THE_CELLS,
        ),
    ),
}


def test_the_document_mutant_table_names_every_document_case() -> None:
    """The keys ARE the document case set, for the reason the other is.

    A document case added without a mutant beside it turns this red, and
    so does a mutant left behind by a case that has gone.
    """
    assert tuple(sorted(DOCUMENT_MUTANTS)) == DOCUMENT_CASES
    for name in DOCUMENT_CASES:
        assert DOCUMENT_MUTANTS[name], name


def test_the_binding_table_names_every_document_case_and_a_test_that_exists() -> None:
    """Coverage is derived from the transforms, not from the stored case count.

    Round-2 ledger item 3: the ledger's two oracle KPIs promised "every
    frozen case" and "each document binding" while three transforms --
    `written_form_classes`, `withheld_line_marks`, `delimiter_reading` --
    were pinned by nothing. A binding added without a test, or a test
    renamed out from under one, turns this red here; that the LEDGER pins
    each of them is held in tests/test_kpi_ledger_integrity.py.
    """
    assert tuple(sorted(DOCUMENT_BINDINGS)) == DOCUMENT_CASES
    here = pathlib.Path(__file__).resolve()
    defined = {
        node.name
        for node in ast.walk(ast.parse(here.read_text(encoding="utf-8")))
        if isinstance(node, ast.FunctionDef)
    }
    for name in DOCUMENT_CASES:
        path, _mark, function = DOCUMENT_BINDINGS[name].partition("::")
        assert path == "tests/" + here.name, name
        assert function in defined, (name, function)


@pytest.mark.parametrize("name", DOCUMENT_CASES)
def test_each_document_case_fails_when_its_own_rule_is_reverted(
    name: str, monkeypatch
) -> None:
    """Every document case, put through the rule the method rules out.

    `row_arrangement` carries two, because it pins two rules that no one
    file can carry together, and a case with one mutant for two rules is
    a case whose second rule could be withdrawn with every committed
    byte where it was.
    """
    before, _claims = gen.build_document_case(name)
    for mutant in DOCUMENT_MUTANTS[name]:
        with monkeypatch.context() as patched:
            patched.setattr(gen, mutant.attribute, mutant.replacement)
            after, _mutant_claims = gen.build_document_case(name)
            assert after != before, (
                f"{name} is written the same way with its own branch "
                f"reverted ({mutant.branch}), so no committed byte holds "
                "that branch up"
            )


# -------------------------------------- the count G14.3 states, off the files


METHOD_TEXT = REPOSITORY / "docs" / "spec" / "generation-method-v1.md"

_UNITS = (
    "zero one two three four five six seven eight nine ten eleven twelve "
    "thirteen fourteen fifteen sixteen seventeen eighteen nineteen"
).split()
_TENS = "twenty thirty forty fifty sixty seventy eighty ninety".split()


def _in_words(number: int) -> str:
    """A count as the method writes it: `seventy-three`, and from a hundred
    `one hundred and one` -- the count passed a hundred at the carried
    numbers repair pass of 2026-09-19."""
    if number >= 100:
        said = f"{_UNITS[number // 100]} hundred"
        if number % 100:
            said = f"{said} and {_in_words(number % 100)}"
        return said
    if number < 20:
        return _UNITS[number]
    tens = _TENS[number // 10 - 2]
    return tens if number % 10 == 0 else f"{tens}-{_UNITS[number % 10]}"


def test_the_method_states_the_count_the_committed_files_hold() -> None:
    """G14.3's count sentence, held to the six committed case sets.

    THE SENTENCE WENT STALE BY TWENTY-ONE CASES with every test green: it
    said fifty-two, split nine, twenty, sixteen and seven, while the files
    held seventy-three, because each repair that added a case added a
    clause to the growth list and moved no number. So the total and each
    file's own count are read out of the section and compared with the
    files, and the table's rows with the case names.

    Mutation: adding a case to any file, or writing any other number into
    the sentence, turns this red.
    """
    text = METHOD_TEXT.read_text(encoding="utf-8")
    section = text[text.index("### G14.3"):text.index("### G14.4")]
    assert f"**All {_in_words(len(EVERY_CASE))} are required.**" in section
    held = (
        (VECTORS, _document()),
        (BRANCH_VECTORS, _branch_document()),
        (SECOND_BRANCH_VECTORS, _second_branch_document()),
        (DOCUMENT_VECTORS, _document_document()),
        (THIRD_BRANCH_VECTORS, _third_branch_document()),
        (FOURTH_BRANCH_VECTORS, _fourth_branch_document()),
        (FIFTH_BRANCH_VECTORS, _fifth_branch_document()),
        (SIXTH_BRANCH_VECTORS, _sixth_branch_document()),
        (SEVENTH_BRANCH_VECTORS, _seventh_branch_document()),
        (EIGHTH_BRANCH_VECTORS, _eighth_branch_document()),
        (NINTH_BRANCH_VECTORS, _ninth_branch_document()),
    )
    flat = " ".join(section.split())
    for path, document in held:
        said = (
            f"`tests/reference/{path.name}`, holds "
            f"{_in_words(len(document['cases']))}"
        )
        assert said in flat, (path.name, len(document["cases"]))
    rows = sorted(
        line.split("`")[1]
        for line in section.splitlines()
        if line.startswith("| `")
    )
    assert tuple(rows) == EVERY_CASE

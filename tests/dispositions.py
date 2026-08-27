"""The registry: every published fact against the bar the plan sets it.

THIS FILE EXISTS BECAUSE ONE OBLIGATION WAS LOWERED FOUR TIMES. Each
time, a repair closed the review item that named the previous lowering
and made the next defect disappear by writing a quieter sentence into a
specification instead of meeting the bar. The audit trail is in
`test_p2c4f1_disposition_registry.py`, which reads this file and turns
red when any of the three governing documents states less than the
ratified plan does.

WHAT THIS FILE IS. `docs/plans/phase-2-generator.md` section P2-D6 is
the single source of truth for what every published fact owes. P2-D6 is
prose written for a person. This is the same content in a shape a test
can compare: one entry per (group, field), carrying the disposition, the
plan's own words for it, and -- where the plan names a lesser outcome --
that authorization in the plan's own words too.

WHAT IT IS NOT. It is not an independent decision about any fact. A
disposition here that the plan does not state is a defect in this file,
and `test_the_plan_states_every_registered_disposition` is what finds
it. Changing an entry here without changing P2-D6 does not lower a bar;
it turns the guard red.

WHY THE MECHANISM CHANGED AT ROUND 5. The first version of this guard
looked for a fixed tuple of lesser-outcome phrases standing near a
fact's name. Round 5 defeated it six ways out of eight, and every one of
the six was some form of "say the same thing in other words, or say it
somewhere else". Reading prose for meaning is a contest a phrase list
loses, so the phrase list is no longer what carries the guarantee. Three
mechanisms carry it now, and each one is a comparison rather than a
reading:

1. THE THREE DOCUMENTS ARE SEALED, PASSAGE BY PASSAGE. Every passage of
   the plan and both specifications is digested; the digests live in the
   generated `disposition_seal.py`. A passage that is not in the seal is
   a passage nobody reviewed, whatever it says, so writing a new
   sentence or changing an old one turns the guard red BEFORE anyone
   asks what the sentence means. Re-sealing is a separate, counted,
   self-describing edit to a file that says what signing it asserts.
2. THE REGISTRY'S OWN JUDGMENT IS SEALED THE SAME WAY. The class each
   fact carries, the plan text each fact is bound by, every
   authorization, and the two report lines that are notes rather than
   misses are four digests in the same generated file. Round 5 defeated
   the old guard by editing entries here; an edit here now has to be
   countersigned there.
3. THE PLAN IS PARSED, NOT SEARCHED. A fact's class may never be weaker
   than any class the plan's own region writes beside that fact's name,
   and an authorization has to declare the fact, the plan region that
   carries its words, and the lesser class it grants. That is a
   structural comparison against the ratified plan, so a registry entry
   cannot be softened while the plan still says otherwise -- however
   genuine the sentence quoted beside it.

AND THE OBLIGATIONS ARE EXECUTABLE, which is what makes a quieter
sentence useless on its own. Every disposition drives an assertion over
the shipped generator: a producer battery runs it across every role and
requires each report line to be one the plan allows. Lowering a sentence
does not move that assertion by one character.

The phrase list survives as a SECOND net that names known lowerings in
plain terms. It is no longer the guarantee, and its reach is stated
rather than implied.

THE ONE WAY TO LOWER A BAR, and it is deliberately loud: amend the
ratified plan, in the open, so that P2-D6 names the lesser outcome; then
the registry may carry it as an authorized entry, whose text this file
must quote from the plan; then the specifications may state it. Every
one of those steps now moves a seal as well, so the count of moved seals
is itself the visible record.

THE SECOND WAY, which is temporary and reviewer-gated: an adversarial
review names a lowering as a defect that is still open. The OPEN mapping
below carries it with the review item's own identifier, and that
identifier has to be an item the NEWEST review record leaves open in its
own round -- parsed from that record's item headings and its verdict,
not looked for anywhere in the file. An implementer cannot open one, an
entry cannot be carried by quoting an item a later review closed, and no
entry can excuse a sentence that was not already in the seal.
"""

import hashlib
import pathlib
import re
import typing

# -- the governing documents, and how a passage of one is named --
#
# The Phase 2 plan is the source of truth for the generator's
# obligations and both specifications restate it, so a lowering can be
# written into any of the three. The Phase 3 plan joined the set at its
# ratification (its own P3-D5): it fixes the validator's obligations,
# and a quieter sentence written into it would be the same defect this
# seal exists to catch. They are named here, relative to the repository
# root, because the seal file and the guard have to split them into
# passages the same way -- a splitter that disagreed with the one that
# wrote the seal would report every passage as unsealed.

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]

# THE SEAL IS PAUSED UNTIL PHASE 4 CLOSES (owner ruling 2026-08-26,
# plan amendment A-P4-46.2), then re-sealed once over the whole tree.
#
# WHAT PAUSING MEANS, exactly: the seal is still WRITTEN and the two
# passage checks still run, so a landing that edits a governing
# document and forgets to re-seal is still told. What stops is the
# obligation to treat every such edit as a counted, reviewed act -- the
# re-seal becomes a mechanical step at the end of a landing rather than
# a gate in the middle of one.
#
# WHAT IT COSTS, and it is real: four lowerings in this project's
# history reached a document unnoticed, which is why the seal was built.
# The trade holds only while nothing is released and every change
# passes the owner. `PAUSED_UNTIL_PHASE_CLOSE` is read by the close
# audit, which refuses to close the phase while it is True.
PAUSED_UNTIL_PHASE_CLOSE = True

GOVERNING = (
    "docs/plans/phase-2-generator.md",
    "docs/plans/phase-3-product.md",
    # The Phase 4 plan joined at its ratification (2026-08-19, plan
    # review round 5): it fixes the column-handling obligations of the
    # next phase — new roles, the reproduction rule, the version 6
    # delta — and a quieter sentence written into it would be the same
    # defect this seal exists to catch.
    "docs/plans/phase-4-columns.md",
    "docs/spec/profile-contract-v4.md",
    "docs/spec/profile-contract-v5.md",
    # VERSION 6 JOINS AT ITS FIRST SHIPPED LANDING, not at a
    # ratification that never came. It was carried as a draft "under
    # adversarial review" while `PROFILE_VERSION` was already 6 in both
    # the producer and the loader -- so the document that governs every
    # description this tree writes was the one document outside the
    # seal, and a disposition quietly lowered in it moved nothing red.
    # Found at the third adversarial read of the obligations landing,
    # 2026-08-26.
    "docs/spec/profile-contract-v6.md",
    "docs/spec/generation-method-v1.md",
    "docs/spec/validation-method-v1.md",
)


def passages(path: pathlib.Path) -> "tuple[str, ...]":
    """One document as the units a statement is made in.

    A table ROW is a unit of its own: the matrix disposes one row's
    fields in that row's second cell, and reading a whole table as one
    block made every field of it answer for every other field's clause.
    A heading is a unit of its own. Everything else is a block between
    blank lines, because the two lowerings that mattered ran across a
    full stop and a dash inside one paragraph.

    Whitespace is collapsed inside each unit, so re-wrapping a paragraph
    to a different column width leaves every passage unchanged and only
    a change of WORDS moves a digest.
    """
    found: list[str] = []
    block: list[str] = []

    def close() -> None:
        if block:
            found.append(" ".join(" ".join(block).split()))
            block.clear()

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or line.lstrip().startswith("|"):
            close()
            found.append(" ".join(line.split()))
            continue
        if line.strip():
            block.append(line)
        else:
            close()
    close()
    return tuple(found)


def digest(text: str) -> str:
    """The seal of one passage, or of one line of registry judgment.

    Sixteen hexadecimal characters of SHA-256. Sixty-four bits is far
    past what a person rewording an English sentence can collide with,
    and short enough that the seal file stays one readable line per
    passage -- which is what makes a re-seal countable in a diff.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# -- the six dispositions of plan P2-D6 -------------------------------

EXACT_OBSERVABLE = "EXACT-OBSERVABLE"
EXACT_CONTROL = "EXACT-CONTROL"
APPROXIMATED = "APPROXIMATED"
REPORT_ONLY = "REPORT-ONLY"
LOADER_ONLY = "LOADER-ONLY"
STRUCTURAL = "STRUCTURAL"

DISPOSITIONS = (
    EXACT_OBSERVABLE,
    EXACT_CONTROL,
    APPROXIMATED,
    REPORT_ONLY,
    LOADER_ONLY,
    STRUCTURAL,
)

# How much each disposition owes the reader of the twin, as an order.
# Only the four output classes compare: an exact fact is owed exactly,
# an APPROXIMATED one inside a measured bound, a REPORT-ONLY one only in
# words. LOADER-ONLY and STRUCTURAL are not on this axis at all -- they
# carry no value obligation over the written CSV -- so a document may
# state them only for a fact the registry gives them to, never as a
# softer answer for a fact it does not.
STRENGTH = {
    EXACT_OBSERVABLE: 3,
    EXACT_CONTROL: 3,
    APPROXIMATED: 2,
    REPORT_ONLY: 1,
}

# The exact classes, whose facts this registry has the prose scanned for.
EXACT = (EXACT_OBSERVABLE, EXACT_CONTROL)


class Fact(typing.NamedTuple):
    """One published fact, and everything the guard needs to check it."""

    group: str
    field: str
    disposition: str
    # How the ratified plan writes this field's name, where that is not
    # simply the backticked field name. The plan's own region for the
    # group must bind this name to the disposition above.
    plan_phrase: str = ""
    # ...or, where the plan states the bar in a sentence rather than by
    # naming the class beside the field, the plan's own words for it.
    # One of the two mechanisms carries every fact, and both go red when
    # the plan's sentence is softened, which is the point of reading the
    # plan at all.
    plan_words: str = ""
    # Which part of the plan states it. Empty means the group's own
    # paragraph of the matrix; a few facts are set elsewhere -- by an
    # owner decision in P2-D0, or in a matrix paragraph that covers
    # several roles at once -- and name that region instead.
    plan_region: str = ""
    # Extra phrases by which a passage speaks about this fact without
    # writing its name. `earliest` and `latest` carry one because the
    # paragraph that survived two reviews called them "the endpoint" and
    # named neither field.
    aliases: "tuple[str, ...]" = ()
    # Lesser outcomes the RATIFIED PLAN names for this fact. Each entry
    # is (phrase as the specifications write it, the plan's own words for
    # the same authorization). The second half is checked against the
    # plan on every run, so an authorization the plan does not carry
    # cannot be written here.
    authorized: "tuple[tuple[str, str], ...]" = ()


def _facts(group: str, disposition: str, *fields: str) -> "list[Fact]":
    """Every field of one group that shares one disposition."""
    return [Fact(group, field, disposition) for field in fields]


# The plan's own paragraph markers inside P2-D6, and the two owner
# decisions that set a fact outside it. A group's facts are looked for
# in its own region, so one field name -- `n_distinct` above all -- can
# mean a different thing on a different role without the two colliding.
PLAN_REGIONS = {
    "document": "**Top-level dispositions**",
    "universal": "**Universal fields**",
    "empty": "**`empty` gets its own dispositions.**",
    "numeric": "**Numeric (count, continuous)**",
    "label": "**Label roles (categorical, binary, constant)**",
    "datetime": "**Datetime**",
    "free_text": "**Free text**",
    "identifier": "**Identifier**",
    "numeric_unrepresentable": "**Numeric unrepresentable**",
    # The paragraph reconciling raw against folded distinctness, which
    # covers the label and the two invention roles in one place.
    "raw-versus-folded": "**Raw versus folded, reconciled",
    # ...and the one giving a column of dates its own cardinality bound.
    "datetime-cardinality": "**Datetime cardinality has its own explicit",
    "closing": "**Enforced by a test",
}

# Facts the plan settles in an owner decision rather than in the matrix
# name this region instead.
DECISIONS = "P2-D0"

# Whole plan sections that are regions in their own right: the owner
# decisions, and the generation-semantics section that states the one
# corner a column of dates is given. A region named here is cut from the
# plan the same way P2-D6's paragraphs are, so an authorization can name
# the section that actually carries it instead of being looked for in
# the whole document -- which is how round 5 propped one up with an
# unrelated sentence.
PLAN_SECTIONS = (DECISIONS, "P2-D9")

# Regions of the PHASE 3 plan, for facts that plan settles. The Phase 2
# matrix is closed and its wording is the record of what Phase 2 ruled;
# a field added by a Phase 3 amendment is stated in that amendment, and
# is looked for there. Each entry is (region name, the marker the
# amendment opens with); the region runs to the next heading.
PLAN3_REGIONS = {
    "A-P3-28": "**Amendment A-P3-28 —",
}

# ...and the Phase 4 plan's own sections, for the roles Phase 4 adds.
# The Phase 2 matrix is the record of what Phase 2 ruled and is not
# edited to carry a role Phase 2 never had, so a role a later phase
# adds is disposed in that phase's plan and looked for there.
PLAN4_REGIONS = {
    "affixed": "### P4-D4.1 The affixed-number role",
    "clock": "### P4-D4.2 The time-of-day role",
    "clock-cardinality": (
        "## Amendment A-P4-20 — the clock role's distinctness is "
        "approximated, under its own envelope"
    ),
    "date-readings": "### P4-D4.3 The widened date readings",
    "holes": (
        "### P4-D6.1 The twin reproduces recorded hole spellings "
        "(decision 2)"
    ),
    "fraction": (
        "### P4-D4.5 The fixed-fraction spelling fact "
        "(closes R-P3-12's route)"
    ),
    "padding": "### P4-D14 The padded-field width fact",
    "histogram": "### P4-D4.7 The value histogram (owner instruction 2026-08-26)",
    "kurtosis": "### P4-D4.8 The kurtosis (owner instruction 2026-08-26)",
    "forms": "### P4-D18 A held-back value gets a stand-in that looks like one",
}

# Groups whose facts are NOT in the version 4 contract matrix, and why.
# That matrix is the record of what version 4 disposed; it is not
# edited to carry a role version 4 never had. The affixed role's own
# seven keys are disposed in the Phase 4 plan and checked against it by
# `PLAN4_REGIONS` above -- so they are held to a document, just not to
# that one. Its QUANTITATIVE keys are not here: they are registered
# under `numeric` and checked against the numeric section like every
# other numeric fact, which is the half that carries a distribution.
GROUPS_OUTSIDE_THE_VERSION_4_MATRIX = ("affixed", "clock")

# ...and the same thing one grain finer: a fact registered under a group
# version 4 DOES have, about something version 4 never published. The
# census of fraction widths is a numeric fact and belongs in the numeric
# group, and version 4's matrix has no row for it because version 4 has
# no such key. Its disposition is decided in the Phase 4 plan and
# checked against it by `PLAN4_REGIONS`, exactly as the affixed group's
# own facts are -- held to a document, just not to that one.
FACTS_OUTSIDE_THE_VERSION_4_MATRIX = (
    ("numeric", "fraction_widths"),
    ("numeric", "pad_widths"),
    ("numeric", "value_histogram"),
    ("numeric", "kurtosis"),
    ("datetime", "resolution_mix"),
    ("free_text", "shape_forms"),
    ("label", "shape_forms"),
)

# THE ONE FACT WHOSE DISPOSITION A VERSION CHANGED, and the reason it
# needs a tuple of its own rather than the one above. Version 4 and
# version 5 both HAVE a row for `missing_by_source` and both say
# REPORT-ONLY -- and both were right when they said it: their twins
# wrote every absent cell empty, so the field owed the twin nothing. A
# version 6 twin writes each spelling at its published count (C6-115),
# so the field is recounted off the written cells like any other exact
# fact, and version 6's own 9.2 row says so.
#
# The older rows are NOT edited: they are the record of what those
# versions required. So the matrix still states this fact and is still
# checked for stating it -- what is not checked against the older
# matrices is its CLASS, which is version 6's to give.
#
# Residual R-P4-25 carries the wider job: since the flip, version 6
# governs all one hundred and thirty facts, and this machinery still
# reads version 4's tables for the other hundred and twenty-nine.
FACTS_A_LATER_VERSION_REDISPOSES = (("universal", "missing_by_source"),)


# -- the registry ------------------------------------------------------
#
# Derived from plan P2-D6 (revision 5, ratified) and checked against it
# on every run.

REGISTRY: "list[Fact]" = []

# The document itself.
REGISTRY += [
    Fact("document", "columns", STRUCTURAL),
    Fact("document", "source", STRUCTURAL),
]
REGISTRY += _facts(
    "document",
    LOADER_ONLY,
    "profile_version",
    "settings",
    "created_with",
    "publication_notes",
    "relationships",
)
REGISTRY += [
    Fact(
        "document",
        "n_rows",
        EXACT_OBSERVABLE,
        plan_phrase="document `n_rows`",
    ),
    Fact("document", "n_columns", EXACT_OBSERVABLE),
    Fact("document", "source.encoding", REPORT_ONLY),
    Fact("document", "source.used_fallback_encoding", REPORT_ONLY),
    Fact("document", "source.header_source", EXACT_CONTROL),
    Fact(
        "document",
        "source.header_by_convention",
        REPORT_ONLY,
        plan_words="`source.header_by_convention` and `source.header_evidence` "
        "are REPORT-ONLY **with a required sentence**",
    ),
    Fact(
        "document",
        "source.header_evidence",
        REPORT_ONLY,
        plan_words="`source.header_by_convention` and `source.header_evidence` "
        "are REPORT-ONLY **with a required sentence**",
    ),
]

# Every role carries these.
REGISTRY += _facts("universal", EXACT_OBSERVABLE, "n_present", "n_missing")
REGISTRY += [
    # Both halves of this row are exact, so neither is a lesser outcome
    # of the other; the plan's own sentence is the anchor.
    Fact(
        "universal",
        "name",
        EXACT_OBSERVABLE,
        plan_words="| `name` | EXACT-OBSERVABLE when a header is written, "
        "else EXACT-CONTROL |",
    ),
]
REGISTRY += _facts("universal", EXACT_CONTROL, "position", "role")
REGISTRY += [
    Fact(group, field, EXACT_CONTROL, plan_phrase="the three axes")
    for group, field in [
        ("universal", "statistical_type"),
        ("universal", "quality_state"),
        ("universal", "structural_role"),
    ]
]
# The version 6 write rule's one authorization, quoted from the plan
# region that states it so a softened sentence stops being found.
_JUDGED_PASS_SAID = (
    "**A spelling a JUDGED PASS put there** (P4-D6.1, contract C6-116) "
    "is REPORT-ONLY for that key"
)

REGISTRY += _facts("universal", REPORT_ONLY, "missing_by_class")
# `missing_by_source` STOPPED BEING REPORT-ONLY at version 6 (plan
# P4-D6.1, contract C6-115 and its 9.2 row). Version 5 wrote every
# absent cell empty, so the field owed the twin nothing; a version 6
# twin writes each spelling at its published count and the field is
# recounted from the written cells like any other exact fact.
#
# The exception is the judged passes'. A key a stand-in number or a
# calendar placeholder put there stays blank in the twin, for the
# reason C6-116 gives -- reproducing it would make the twin's own
# measurement contingent on a re-judgement -- and for THAT key the
# field is report-only, with the achieved zero named beside the
# published count.
REGISTRY += [
    Fact(
        "universal",
        "missing_by_source",
        EXACT_OBSERVABLE,
        plan_region="holes",
        plan_words="each `missing_by_source` spelling at exactly its "
        "count",
        authorized=(
            ("judged", _JUDGED_PASS_SAID),
        ),
    )
]
# The two counts contract version 5 moved out of `missing_by_source`
# (its section 5). The Phase 2 plan's matrix predates them, so they
# bind to the Phase 3 amendment that landed them, which writes their
# row and the reason in one place.
REGISTRY += [
    Fact(
        "universal",
        field,
        REPORT_ONLY,
        plan_region="A-P3-28",
        plan_words="| `n_missing_blank`, `n_missing_withheld` | "
        "REPORT-ONLY — every absent cell is written empty |",
    )
    for field in ("n_missing_blank", "n_missing_withheld")
]
REGISTRY += _facts(
    "universal",
    EXACT_OBSERVABLE,
    "n_numeric",
    "n_not_numeric",
    "n_out_of_range",
    "n_contradictory",
)
REGISTRY += _facts(
    "universal",
    REPORT_ONLY,
    "n_sentinel_candidates_unpublished",
    "sentinel_verdicts",
    "detection_evidence",
    "remarks",
)

# An all-absent column.
_EMPTY_WORDS = (
    "An empty column publishes `n_distinct = n_distinct_folded = 0` and no "
    "per-column `n_rows`; both counts are EXACT-OBSERVABLE"
)
REGISTRY += [
    Fact("empty", "n_distinct", EXACT_OBSERVABLE, plan_words=_EMPTY_WORDS),
    Fact(
        "empty", "n_distinct_folded", EXACT_OBSERVABLE, plan_words=_EMPTY_WORDS
    ),
]

# `count` and `continuous`.
_ENVELOPE = (
    "falling back to the two-sided envelope only where even those cannot "
    "supply the count"
)
# The clause both specifications write for the same authorization.
_ENVELOPE_SAID = "two-sided envelope only where even those cannot supply"
REGISTRY += [
    Fact(
        "numeric",
        "percentiles.min",
        EXACT_OBSERVABLE,
        plan_phrase="`percentiles` endpoints",
    ),
    Fact(
        "numeric",
        "percentiles.max",
        EXACT_OBSERVABLE,
        plan_phrase="`percentiles` endpoints",
    ),
    Fact(
        "numeric",
        "percentiles",
        APPROXIMATED,
        plan_phrase="interior rungs",
    ),
]
REGISTRY += _facts(
    "numeric",
    EXACT_OBSERVABLE,
    "n_zero",
    "n_negative",
    "std_unrepresentable",
    "n_negative_unrepresentable",
    "n_used_in_statistics",
    "n_left_out_of_statistics",
    "numeric_share",
    "integer_valued",
)
REGISTRY += _facts("numeric", APPROXIMATED, "mean", "std", "skew")
# Plan P4-D4.8. APPROXIMATED as the skewness beside it is, under the
# window method G12.3a states. Version 4's matrix has no row for it,
# because version 4 published no such key, so it is registered here
# against the Phase 4 plan the way the other later keys are.
REGISTRY += (
    Fact(
        "numeric",
        "kurtosis",
        APPROXIMATED,
        plan_words="how heavy this column's tails are",
        plan_region="kurtosis",
        aliases=("tail weight", "moment ratio"),
    ),
)
# THE AFFIXED ROLE'S OWN FACTS. Its quantitative block is the numeric
# block read over the cores and is registered above under `numeric`;
# these are the five it adds, and every one is a count or a spelling a
# written twin carries in plain sight.
# THE CLOCK ROLE'S FIVE. Four are exactly observable off a written
# twin -- the form its cells wear, its two ends, and how many cells no
# clock reading accepted -- and the ladder is the one approximated
# fact, for the reason the date ladder is: the construction writes a
# value per rank, so an interior rung lands inside a window rather than
# on the published value.
REGISTRY += [
    Fact(
        "clock",
        field,
        EXACT_OBSERVABLE,
        plan_words="an eleven-rung ordinal ladder",
        plan_region="clock",
    )
    for field in ("clock_form", "earliest", "latest", "n_unparsed")
]
# The ladder's two ENDS are exact, and its interior is not: T2 makes
# the ends the column's own two endpoints, which a written twin carries
# character for character, while every rank between them is
# interpolated into a window.
REGISTRY += [
    Fact(
        "clock",
        f"clock_percentiles.{end}",
        EXACT_OBSERVABLE,
        plan_words="an eleven-rung ordinal ladder",
        plan_region="clock",
    )
    for end in ("min", "max")
]
REGISTRY += [
    Fact(
        "clock",
        "clock_percentiles",
        APPROXIMATED,
        plan_words="an eleven-rung ordinal ladder",
        plan_region="clock",
    ),
]
# ...and its two distinctness counts, lowered to the envelope by
# amendment A-P4-20 for the reason the date role's are: the
# construction writes a value per RANK, so a conforming twin of an
# ordinary column cannot meet the exact bar.
REGISTRY += [
    Fact(
        "clock",
        field,
        APPROXIMATED,
        plan_words="Both distinctness counts on a `time_of_day` column",
        plan_region="clock-cardinality",
    )
    for field in ("n_distinct", "n_distinct_folded")
]
REGISTRY += [
    Fact(
        "affixed",
        field,
        EXACT_OBSERVABLE,
        plan_words=(
            "Re-profiling the twin re-detects the role with the same "
            "facts"
        ),
        plan_region="affixed",
    )
    for field in (
        "n_affixed",
        "affix_prefix",
        "affix_suffix",
        "n_core_numeric",
        "n_core_out_of_range",
        "n_core_contradictory",
        "n_core_not_numeric",
    )
]
REGISTRY += [
    Fact(
        "numeric",
        field,
        EXACT_OBSERVABLE,
        authorized=((_ENVELOPE_SAID, _ENVELOPE),),
    )
    for field in ("n_distinct", "n_distinct_folded")
]
REGISTRY += [
    # Owner decision 10. The plan states the bar in words rather than in
    # the matrix, and states no lesser outcome for it anywhere.
    Fact(
        "numeric",
        "numeric_styles",
        EXACT_OBSERVABLE,
        plan_words="The twin writes each style in its published count",
        plan_region=DECISIONS,
        aliases=("style map", "quota"),
    ),
    # Plan P4-D4.5. The census of widths is the styles map's sibling and
    # takes its disposition: a written file carries every one of its
    # counts in plain sight, so a reader of the twin can recount them.
    Fact(
        "numeric",
        "fraction_widths",
        EXACT_OBSERVABLE,
        plan_words="the count sharing each fraction width",
        plan_region="fraction",
        aliases=("width census", "fraction census"),
    ),
    # Plan P4-D14. The census of field widths is the other sibling of the
    # styles map and takes the same disposition for the same reason: a
    # person opens the twin, counts the figures each padded cell writes,
    # and gets the published census back.
    Fact(
        "numeric",
        "pad_widths",
        EXACT_OBSERVABLE,
        plan_words="the count sharing each field width",
        plan_region="padding",
        aliases=("padding census", "field-width census"),
    ),
    # Plan P4-D4.7. REPORT-ONLY, and the reason is worth stating where
    # a reader meets it. The twin's shape FOLLOWS this census -- on a
    # 300-row column of two populations the empty stretch went from
    # about a hundred twin values to sixteen -- but it is not held to
    # it exactly, because meeting a bin count exactly means the CELL
    # ALLOCATION following the histogram, and that allocation is
    # G5.2's even share over the distinctness budget. Upgrading this to
    # EXACT-OBSERVABLE is residual R-P4-49 and its own landing.
    Fact(
        "numeric",
        "value_histogram",
        REPORT_ONLY,
        plan_words="the count falling in each bin",
        plan_region="histogram",
        aliases=("value histogram", "binned counts"),
    ),
    Fact(
        "numeric",
        "n_rows",
        LOADER_ONLY,
        plan_phrase="per-column `n_rows` echo",
        plan_region="document",
    ),
]

# `constant`, `binary`, `categorical`.
_LABEL_RAW = (
    "raw `n_distinct` is **EXACT-OBSERVABLE where the published variants and "
    "the withheld-variant multiset supply enough spellings**"
)
_LABEL_ENVELOPE = (
    "APPROXIMATED under the two-sided envelope only where they do not"
)
REGISTRY += _facts(
    "label",
    EXACT_OBSERVABLE,
    "levels",
    "suppressed_levels",
    "suppressed_level_counts",
    "suppressed_rows",
)
REGISTRY += [
    Fact(
        "label",
        field,
        EXACT_OBSERVABLE,
        plan_phrase="(normalized label and count)",
    )
    for field in ("label", "count")
]
REGISTRY += [
    # Owner decision 11 fixes the wire shape of both keys and P2-D6 then
    # rests exact raw distinctness on them supplying the spellings, which
    # is only true of keys the twin reproduces exactly.
    Fact(
        "label",
        "variants",
        EXACT_OBSERVABLE,
        plan_words=_LABEL_RAW,
        plan_region="raw-versus-folded",
    ),
    Fact(
        "label",
        "variants_withheld",
        EXACT_OBSERVABLE,
        plan_words=_LABEL_RAW,
        plan_region="raw-versus-folded",
    ),
    Fact(
        "label",
        "n_distinct_folded",
        EXACT_OBSERVABLE,
        plan_words="for **label roles** `n_distinct_folded` is "
        "EXACT-OBSERVABLE",
        plan_region="raw-versus-folded",
    ),
    Fact(
        "label",
        "n_distinct",
        EXACT_OBSERVABLE,
        plan_words=_LABEL_RAW,
        plan_region="raw-versus-folded",
        authorized=((_LABEL_ENVELOPE, _LABEL_ENVELOPE),),
    ),
    Fact("label", "level_ceiling", LOADER_ONLY),
]

# `datetime`. The two ends carry no authorization at all, which is the
# whole subject of review items P2-C2-F5, P2-C3-F2 and P2-C4-F1: the
# plan names no lesser outcome for them, so no document may state one.
# The plan names this instance itself, under the all-different rule: a
# fact the disclosure rules withheld is a fact no twin can put back
# without making one up. It is the ONLY corner the plan gives a column
# of dates, and it reaches the offset fields, never the two ends.
_WITHHELD_OFFSETS = (
    "**Datetime columns whose offsets are withheld** (P2-R5-F3, verified "
    "against the producer)"
)

REGISTRY += [
    Fact(
        "datetime",
        field,
        EXACT_OBSERVABLE,
        plan_words="`earliest`, `latest` EXACT-OBSERVABLE in the "
        "representation owner decision 5 fixes",
        aliases=("endpoint", "end of a column of dates"),
    )
    for field in ("earliest", "latest")
]
REGISTRY += [
    Fact(
        "datetime",
        field,
        EXACT_OBSERVABLE,
        plan_words="`date_percentiles` endpoints exact",
        aliases=("ladder end",),
    )
    for field in ("date_percentiles.min", "date_percentiles.max")
]
REGISTRY += [
    Fact(
        "datetime",
        "date_percentiles",
        APPROXIMATED,
        plan_words="interior rungs APPROXIMATED",
    ),
]
REGISTRY += [
    Fact(
        "datetime",
        field,
        EXACT_OBSERVABLE,
        authorized=(
            ("withheld", _WITHHELD_OFFSETS),
        ),
    )
    for field in (
        "utc_offsets",
        "earliest_utc_offset",
        "latest_utc_offset",
    )
]
REGISTRY += [
    Fact(
        "datetime",
        "datetimes_read_at",
        EXACT_OBSERVABLE,
        plan_words="**`datetimes_read_at` is EXACT-OBSERVABLE, not "
        "EXACT-CONTROL.**",
        authorized=(("withheld", _WITHHELD_OFFSETS),),
    ),
]
REGISTRY += _facts(
    "datetime",
    EXACT_OBSERVABLE,
    "resolution",
    "time_precision",
    "subsecond_digits",
    "n_unparsed",
)
REGISTRY += [
    Fact(
        "datetime",
        "format",
        REPORT_ONLY,
        plan_words="**`format` is REPORT-ONLY, not EXACT-OBSERVABLE.**",
    ),
]
REGISTRY += [
    Fact(
        "datetime",
        "resolution_mix",
        REPORT_ONLY,
        plan_region="date-readings",
        plan_words="And it is REPORT-ONLY, deliberately, on the exact "
        "precedent of the `format` fact itself",
        aliases=("form census", "how many wore each form"),
    ),
]
REGISTRY += [
    Fact(
        "datetime",
        field,
        APPROXIMATED,
        plan_words="`n_distinct` and `n_distinct_folded` on datetime columns "
        "are APPROXIMATED",
        plan_region="datetime-cardinality",
    )
    for field in ("n_distinct", "n_distinct_folded")
]

# `free_text`.
_INVENTION_RAW = (
    "For **invention roles** raw `n_distinct` is EXACT-OBSERVABLE and "
    "`n_distinct_folded` is EXACT-OBSERVABLE too"
)
REGISTRY += [
    # The two containers. P2-D6 gives STRUCTURAL its meaning once, for
    # every container in the matrix, and the contract's own free-text
    # table applies it to these two.
    Fact(
        "free_text",
        field,
        STRUCTURAL,
        plan_words="the completeness assertion accepts a container only when "
        "every leaf under it is disposed AND its membership rule is stated",
        plan_region="document",
    )
    for field in ("length", "words")
]
REGISTRY += [
    # Plan P4-D18. The census of written forms is the fact that lets a
    # held-back value have a stand-in that looks like one, and it is
    # EXACT-OBSERVABLE for the reason the width censuses are: a person
    # opens the twin, reads the form off each cell, and gets the
    # published census back.
    Fact(
        "free_text",
        "shape_forms",
        EXACT_OBSERVABLE,
        plan_words="the count sharing each written form",
        plan_region="forms",
        aliases=("form census", "shape census"),
    ),
    Fact(
        "label",
        "shape_forms",
        EXACT_OBSERVABLE,
        plan_words="the count sharing each written form",
        plan_region="forms",
        aliases=("form census", "shape census"),
    ),
]
REGISTRY += _facts(
    "free_text",
    EXACT_OBSERVABLE,
    "length.min",
    "length.max",
    "words.min",
    "words.max",
    "n_all_digits",
    "n_code_alphabet",
    "n_distinct_by_occurrences",
)
REGISTRY += _facts(
    "free_text", APPROXIMATED, "length.mean", "length.p50", "words.mean"
)
REGISTRY += [
    Fact(
        "free_text",
        field,
        EXACT_OBSERVABLE,
        plan_words=_INVENTION_RAW,
        plan_region="raw-versus-folded",
    )
    for field in ("n_distinct", "n_distinct_folded")
]

# A declared identifier. Owner decision 6's corner is the one
# authorization here, and it reaches exactly three facts.
_CORNER = (
    "**In that decision's infeasible corner, THREE distinctness facts are "
    "REPORT-ONLY, not one**"
)
REGISTRY += _facts(
    "identifier",
    EXACT_OBSERVABLE,
    "min_length",
    "max_length",
    "all_whole_numbers",
    "n_all_digits",
    "n_code_alphabet",
)
REGISTRY += [
    Fact(
        "identifier",
        field,
        EXACT_OBSERVABLE,
        plan_words="Outside that corner every one of them is EXACT-OBSERVABLE",
        authorized=(("infeasible corner", _CORNER),),
    )
    for field in (
        "n_distinct",
        "n_distinct_folded",
        "n_distinct_by_occurrences",
    )
]

# `numeric_unrepresentable`.
REGISTRY += _facts(
    "numeric_unrepresentable",
    EXACT_OBSERVABLE,
    "n_whole",
    "n_fraction",
    "n_whole_unknown",
    "n_positive",
    "n_negative",
    "n_sign_unknown",
    "n_distinct_by_occurrences",
)
REGISTRY += [
    Fact(
        "numeric_unrepresentable",
        field,
        EXACT_OBSERVABLE,
        plan_words=_INVENTION_RAW,
        plan_region="raw-versus-folded",
    )
    for field in ("n_distinct", "n_distinct_folded")
]

BY_KEY = {(fact.group, fact.field): fact for fact in REGISTRY}


# -- what each authorization binds itself to ---------------------------
#
# Round 5 added an authorization to a fact the plan authorizes nothing
# for, propped it up with a genuine sentence from somewhere else in the
# plan, and the guard was satisfied that "some phrase and some plan text
# exist". So an authorization now declares three things about itself and
# is checked on all three: WHICH FACT it belongs to (the key), WHICH
# PLAN REGION has to carry its words, and WHICH LESSER CLASS it
# authorizes -- which has to be genuinely weaker than the fact's own.
#
# There is no default. An authorization with no entry here is refused,
# so writing one takes two edits, in two places, both of them sealed.

AUTHORIZED_BY: "dict[tuple[str, str, str], tuple[str, str]]" = {
    # Owner decision 7's spellings reach the published count; the
    # envelope is what P2-D6's own numeric paragraph falls back to.
    ("numeric", "n_distinct", _ENVELOPE_SAID): ("numeric", APPROXIMATED),
    ("numeric", "n_distinct_folded", _ENVELOPE_SAID): (
        "numeric",
        APPROXIMATED,
    ),
    # ...and the same fallback on a column of labels, in the paragraph
    # that sets raw distinctness beside the folded one.
    ("label", "n_distinct", _LABEL_ENVELOPE): (
        "raw-versus-folded",
        APPROXIMATED,
    ),
    # The one authorization the version 6 write rule carries: a
    # spelling a JUDGED PASS put there stays blank in the twin, so for
    # THAT key the field is report-only with the achieved zero named
    # beside the published count (plan P4-D6.1, contract C6-116).
    ("universal", "missing_by_source", "judged"): ("holes", REPORT_ONLY),
    # The one corner P2-D9 gives a column of dates: offsets the
    # disclosure rules withheld cannot be put back without making them
    # up. It reaches the offset fields, never the two ends.
    ("datetime", "utc_offsets", "withheld"): ("P2-D9", REPORT_ONLY),
    ("datetime", "earliest_utc_offset", "withheld"): ("P2-D9", REPORT_ONLY),
    ("datetime", "latest_utc_offset", "withheld"): ("P2-D9", REPORT_ONLY),
    ("datetime", "datetimes_read_at", "withheld"): ("P2-D9", REPORT_ONLY),
    # Owner decision 6's infeasible corner, and the three distinctness
    # facts P2-D6 names inside it.
    ("identifier", "n_distinct", "infeasible corner"): (
        "identifier",
        REPORT_ONLY,
    ),
    ("identifier", "n_distinct_folded", "infeasible corner"): (
        "identifier",
        REPORT_ONLY,
    ),
    ("identifier", "n_distinct_by_occurrences", "infeasible corner"): (
        "identifier",
        REPORT_ONLY,
    ),
}

# The rows contract version 5's section 11 adds to the version 4 matrix,
# and which of that matrix's tables each one belongs to. Version 5
# carries version 4 by reference and states only its delta, so the two
# documents are read TOGETHER wherever the matrix is read at all
# (contract 5 C5-30). A field appearing in that delta with no entry here
# stops the guard rather than being filed by guesswork.
CONTRACT5_SECTIONS = {
    "n_missing_blank": "9.2 Universal per-column fields",
    "n_missing_withheld": "9.2 Universal per-column fields",
}


def contract5_delta(path: pathlib.Path) -> "list[tuple[tuple[str, ...], str]]":
    """Section 11 of contract version 5, as rows of names and a class.

    Returns one entry per table row: the backticked names in its first
    cell, and its second cell's text. The caller decides which of the
    version 4 tables each row belongs to, using CONTRACT5_SECTIONS
    above, because the delta table does not repeat the version 4
    headings.
    """
    text = path.read_text(encoding="utf-8")
    start = text.index("## 11. The disposition matrix")
    body = text[start : text.index("\n## ", start + 10)]
    rows: list[tuple[tuple[str, ...], str]] = []
    for line in body.split("\n"):
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2 or set(cells[0]) <= set("-: "):
            continue
        names = tuple(re.findall(r"`([^`]+)`", cells[0]))
        if names:
            rows.append((names, cells[1]))
    return rows


# Which contract table states which group.
CONTRACT_SECTIONS = {
    "document": "9.1 Top level",
    "universal": "9.2 Universal per-column fields",
    "empty": "9.3 `empty`",
    "numeric": "9.4 The numeric roles: `count`, `continuous`",
    "label": "9.5 The label roles: `constant`, `binary`, `categorical`",
    "datetime": "9.6 `datetime`",
    "free_text": "9.7 free_text",
    "identifier": "9.7 identifier",
    "numeric_unrepresentable": "9.7 numeric_unrepresentable",
}

# The rung names of a ladder, which the matrix disposes by naming the
# ladder itself, and which are therefore not fields of their own.
RUNGS = ("p01", "p05", "p10", "p25", "p50", "p75", "p90", "p95", "p99")

# Which registry group each role of the taxonomy publishes under, so a
# report line naming a column and a fact can be looked up as one entry
# of this file. A fact a role does not carry falls back to the universal
# and top-level groups, which every role shares.
ROLE_GROUPS = {
    "time_of_day": "clock",
    "count": "numeric",
    "continuous": "numeric",
    # The affixed role's quantitative block IS the numeric block, read
    # over the CORES its cells carry rather than over the cells: the
    # same ladder, the same styles, the same statistics, built by the
    # same code. So it takes the numeric group's dispositions entire,
    # including the distinctness envelope -- a twin of an affixed
    # column reaches its distinct count exactly as closely as a twin
    # of the numeric column its cores make, because it IS that twin
    # with a pair written round each cell. Its own seven keys are
    # registered separately below.
    "affixed_number": "numeric",
    "constant": "label",
    "binary": "label",
    "categorical": "label",
    # A long tail publishes the label group's four keys and no key of
    # its own, so it takes that group's dispositions entire -- the
    # invented labels behind withheld levels included, which is the one
    # authorization these roles carry (plan P4-D5).
    "long_tail_labels": "label",
    "datetime": "datetime",
    "identifier": "identifier",
    "free_text": "free_text",
    "numeric_unrepresentable": "numeric_unrepresentable",
    "empty": "empty",
}


# -- what the shipped generator may write a report line about ----------
#
# THIS IS THE EXECUTABLE HALF OF THE GUARD, and it is what makes a
# quieter sentence useless on its own. A run measures its own twin and
# files a line for every published fact it did not meet. A producer
# battery runs the shipped generator over every role and requires each
# line to be one the plan allows: an APPROXIMATED or REPORT-ONLY fact,
# an exact fact the plan authorizes a lesser outcome for, an exact fact
# a reviewer has left open, or one of the two entries below. So an
# implementation that starts missing an exact count turns the suite red
# whatever any document says about it, and softening the document does
# not change the assertion -- weakening THAT is a code change a reviewer
# reads in the diff.

# Report lines that do NOT say a fact was missed. Each one carries the
# published value on both sides and discloses something else about the
# cells; the rule that ratifies each is named, because "it is only a
# note" is exactly the claim a lowering would like to make.
REPORTED_NOTES: "dict[tuple[str, str], str]" = {
    # The count is written on both sides of this line -- the twin holds
    # exactly as many held-back labels, with exactly the sizes the
    # description publishes. What it cannot hold is their SPELLINGS,
    # which is the small-cell floor doing its job (owner decisions 9 and
    # 11; contract 7.4). The exact fact is the count and the count is met.
    ("label", "suppressed_levels"): (
        "the published count is written on both sides of the line; the "
        "floor is what withholds the spellings"
    ),
}

# Report lines about something the profile publishes NO fact for, so no
# disposition is implicated at all. A column of numbers too large to
# hold publishes no width (residual R-P2-1), and the run says which
# width it chose rather than letting the reader assume the real one.
UNPUBLISHED_NOTES: "tuple[str, ...]" = ("width",)


# -- lowerings an adversarial review has already named ------------------
#
# Each entry says: a document states a lesser outcome for this fact, the
# ratified plan does not authorize it, and a REVIEWER has already named
# it as an open defect under the item given here.
#
# FOUR CONDITIONS BIND AN ENTRY, and round 5 defeated a guard that had
# only the first half of the first one:
#
# 1. The item has to be an item of the NEWEST review record's OWN round
#    -- its number carries that round, it has to stand as one of that
#    record's item headings, and the record's verdict has to name it. An
#    item a later review CLOSED can no longer carry an entry, which is
#    what round 5's escape-hatch attack relied on.
# 2. The lowering the entry excuses has to be prose that was already in
#    the seal. A new sentence is unsealed, so no entry can be opened to
#    cover a lowering somebody has just written.
# 3. The fact has to still carry a lowering the scan finds, so a repaired
#    fact's line has to be deleted rather than left to cover the next one.
# 4. When a review stops rejecting the phase, this mapping has to be
#    empty. An open defect cannot be carried into a ratified phase.
#
# An entry is not permission. It is a defect with an owner and a number,
# and these belong to round 5's items P2-C5-F2, P2-C5-F3 and P2-C5-F4
# rather than to this repair.

OPEN: "dict[tuple[str, str], str]" = {
    # G9.5's packing fallback and its report path are CLOSED. The
    # sentence that granted an implementation a lesser outcome where no
    # packing meets every count is gone: the walk is complete, the four
    # class counts are packed with the two alphabet counts on declared
    # identifiers as they already were on free text, and a producer
    # battery of 200 declared-identifier descriptions at four seeds --
    # 800 runs -- writes every one of the six counts exactly (review
    # item P2-C5-F2, `tests/test_p2c5f2_identifier_classes.py`).
    #
    # G6.4 still names two shapes on which a style map is missed. The
    # crowded-ladder shape round 5 named as P2-C5-F3 is closed: G5.2's
    # reach step asks the LADDER which strata a whole number is left
    # for, moves the cells and, where a band's strata all sit on
    # fractions, one stratum's window; the item's own 82-cell producer
    # column writes its published 34/48 on every seed, and a battery of
    # 240 producer descriptions at eight seeds -- 1,920 runs -- writes
    # every NAMED published style count exactly
    # (`tests/test_p2c5f3_style_reach.py`).
    #
    # P2-C5-F3 IS CLOSED (Phase 3 plan P3-D8.1, owner decision 1,
    # 2026-08-12). What was left of it was the pooled remainder: contract
    # 7.5.7 wrote every pooled cell `plain`, and a column whose published
    # `min` or `max` carries a point has a cell that cannot be, so the
    # remainder came out short by that cell on 8 of the producer
    # battery's 240 columns. The owner directed a repair rather than an
    # amendment that names the miss, and the repair is that a pooled cell
    # -- which names no form at all, that being what pooling MEANS -- is
    # spelled by its own value: plainly where the value has a point-free
    # spelling, canonically where it has none. Contract 7.5.7 and method
    # G6.4 carry the amended rule and its recount identity, both sealed;
    # the eight columns file no line; and `_style_notes` checks the
    # identity clause by clause, with the published counts as floors so
    # no form can be substituted away.
    #
    # P2-C5-F4 IS CLOSED (same decision). Its second shape -- a length
    # end pinned onto a group whose band cannot spell a whole number at
    # that length -- was already closed by the joint packing of
    # `_identifier_families`, which settles length and band together over
    # every carrier pair, and only the contract's prose still asserted
    # it. Its first shape, the two-character code value whose only
    # whole-number spellings open with a sign G9.1 bars, is settled the
    # way the owner directed: the family is withdrawn, and the
    # descriptions it leaves with no answer meet the FIFTH refusal of
    # method G12 by name rather than being written with a leading `-`.
    #
}

# A LESSER OUTCOME AN OLDER DOCUMENT STATES ABOUT ITS OWN VERSION, and
# it is not the same thing as an open lowering. `OPEN` above is for a
# bar this project has not yet met and a review leaves standing; every
# entry there names that review's own item. This is the other case:
# the bar IS met, and the sentence the scan finds is an older
# contract's account of what IT required.
#
# Version 4 and version 5 both say `missing_by_source` is REPORT-ONLY,
# and both were right: their twins wrote every absent cell empty, so
# the field owed the twin nothing. A version 6 twin writes each
# recorded spelling at its published count (plan P4-D6.1, contract
# C6-115), so the field is EXACT-OBSERVABLE from that version, with
# the judged passes' keys as its one authorized exception. The older
# sentences are the record of what those versions required and are
# never edited to carry a later version's rule -- so the scan meets
# them for as long as those documents stand, and this is where it is
# told why.
HISTORICAL: "dict[tuple[str, str], str]" = {
    ("universal", "missing_by_source"): (
        "version 4 and version 5 wrote every absent cell empty; "
        "version 6 reproduces the recorded spellings (P4-D6.1)"
    ),
}


# -- the sentences that RAISE a bar, and may not quietly go away -------
#
# A seal catches a sentence that was written or reworded. It does not
# catch a sentence that was DELETED, and the deletions that matter are
# the ones that take a raising sentence away: "no corner, no exception"
# removed from a row leaves the row true and the obligation open to a
# corner again. Each entry below is one such sentence, quoted from the
# document that carries it, and a test requires it to still be there.
#
# The plan carries most of them on purpose: it is the ratified source,
# it is the document a lowering has to get past LAST, and it is the one
# no repair of a specification has a reason to touch.

ANCHORS: "tuple[tuple[str, str], ...]" = (
    # The plan's own definition of what the exact classes owe.
    (
        "docs/plans/phase-2-generator.md",
        (
            "EXACT-OBSERVABLE (reproduced and independently recounted "
            "from the written CSV)"
        ),
    ),
    # The four parser classes, exact by construction rather than by
    # recount -- the obligation round 5 reopened as P2-C5-F2.
    (
        "docs/plans/phase-2-generator.md",
        (
            "| `n_numeric`, `n_not_numeric`, `n_out_of_range`, "
            "`n_contradictory` | EXACT-OBSERVABLE by class-preserving "
            "construction |"
        ),
    ),
    # The two counts every role owes.
    (
        "docs/plans/phase-2-generator.md",
        (
            "| `n_present`, `n_missing`, document `n_rows`, `n_columns` "
            "| EXACT-OBSERVABLE |"
        ),
    ),
    # Feasibility rule 4: a published count beats the ladder.
    (
        "docs/plans/phase-2-generator.md",
        "**Published counts take precedence over ladder conformance**",
    ),
    # Feasibility rule 5: what a refusal is reserved for.
    (
        "docs/plans/phase-2-generator.md",
        "**Refusal is reserved for documents no rule above can satisfy**",
    ),
    # The completeness assertion may not grow exceptions.
    (
        "docs/plans/phase-2-generator.md",
        (
            "It must pass against the ratified matrix as written — it "
            "may not acquire exceptions during implementation."
        ),
    ),
    # The two ends of a column of dates, and the ladder ends tied to them.
    (
        "docs/spec/profile-contract-v4.md",
        (
            "No corner, no exception: the last second of a leap minute "
            "is written back unchanged"
        ),
    ),
    (
        "docs/spec/profile-contract-v4.md",
        "No corner, no exception: they are the same two instants",
    ),
    # The sentence that stops section 9's head from becoming a licence.
    (
        "docs/spec/profile-contract-v4.md",
        "Where an exact answer exists, producing it is the obligation",
    ),
    # ...and the reading of "cannot all hold" that goes with it.
    (
        "docs/spec/profile-contract-v4.md",
        (
            '"The published facts cannot all hold" means no assignment '
            'satisfies them, proved, not "the first rule I tried did '
            'not find one".'
        ),
    ),
    # The sentence that stops the one named corner spreading to the rest
    # of the datetime table, and the two that keep the leap second and
    # the endpoints out of the report.
    (
        "docs/spec/profile-contract-v4.md",
        (
            "Outside that one corner, every field in this table means "
            "exactly what its disposition says."
        ),
    ),
    (
        "docs/spec/profile-contract-v4.md",
        (
            "**THE LAST SECOND OF A LEAP MINUTE IS NOT A CORNER, AND MAY "
            "NOT BE MADE ONE**"
        ),
    ),
    (
        "docs/spec/profile-contract-v4.md",
        (
            "It is not a route by which an end this contract calls exact "
            "becomes a line in the report."
        ),
    ),
    # What owner decision 6's corner costs, said in the plan rather than
    # left to whoever writes the report.
    (
        "docs/plans/phase-2-generator.md",
        (
            "The report names all three lost facts with the achieved "
            "value beside the published one, and the feasibility battery "
            "asserts all three."
        ),
    ),
    # ...and that a refusal is a refusal of GENERATION, so a document
    # nobody can satisfy is settled rather than half-written.
    (
        "docs/plans/phase-2-generator.md",
        (
            "and is a refusal of GENERATION, never a claim that the "
            "profile is invalid"
        ),
    ),
    # The four sentences that turn the plan's rule 5 into an outcome the
    # specifications carry (review item P2-C5-F4). The contract's
    # section-9 head is where the blanket "meets what it can" lived for
    # four rounds, and each of the two rows below is where one of the
    # two generated corners was written down as a lesser outcome.
    # Deleting any of them puts a description the plan settles back in
    # the hands of a walk that writes a twin instead.
    (
        "docs/spec/profile-contract-v4.md",
        "**Such a document is REFUSED, and a twin is never written from it.**",
    ),
    (
        "docs/spec/profile-contract-v4.md",
        (
            "generation is refused before any cell is built "
            "(`docs/spec/generation-method-v1.md` G12, "
            "`generation-words-exceed-length`)"
        ),
    ),
    (
        "docs/spec/profile-contract-v4.md",
        (
            "generation is refused before any cell is built "
            "(`docs/spec/generation-method-v1.md` G12, "
            "`generation-whole-numbers-need-room`)"
        ),
    ),
    (
        # THE COUNT MOVED FROM FOUR TO FIVE, and the anchor moved with
        # it (Phase 3 plan P3-D8.1, owner decision 1). What this anchor
        # holds is the SENTENCE that reserves refusal for descriptions
        # no rule can satisfy, not the number after it: the number is
        # what the method's own next paragraph says a change to this
        # document may move, and moving it is how the fifth refusal
        # landed. Deleting the sentence would still lower the bar, and
        # that is what stays asserted.
        "docs/spec/generation-method-v1.md",
        (
            "**Refusal is reserved for documents no rule above can "
            "satisfy.** This method has exactly four"
        ),
    ),
)


# -- the registry's own judgment, in a shape a seal can hold -----------
#
# Four surfaces, because four different edits lower a bar and a
# reviewer should be able to see WHICH one moved: the class each fact
# carries, the plan text each fact is bound by, and every authorized
# lesser outcome. Round 5 walked through the second and third of these.


def judgment(registry: "typing.Sequence[Fact]") -> "dict[str, str]":
    """The three digests that stand for this registry's decisions.

    Accepts any sequence of facts, so a mutation battery can ask what
    the seal would be for a registry somebody edited, without editing
    this file. Deterministic: the lines are sorted before they are
    digested, so the order entries were appended in never matters.
    Raises nothing.
    """
    classes = sorted(
        f"{fact.group}/{fact.field} = {fact.disposition}" for fact in registry
    )
    bindings = sorted(
        f"{fact.group}/{fact.field} | {fact.plan_region} | "
        f"{fact.plan_phrase} | {fact.plan_words} | {'; '.join(fact.aliases)}"
        for fact in registry
    )
    grants = sorted(
        f"{fact.group}/{fact.field} | {phrase} | {words}"
        for fact in registry
        for phrase, words in fact.authorized
    ) + sorted(
        f"{group}/{field} | {phrase} -> {region} | {lesser}"
        for (group, field, phrase), (
            region,
            lesser,
        ) in AUTHORIZED_BY.items()
    )
    notes = sorted(
        f"{group}/{field} | {why}"
        for (group, field), why in REPORTED_NOTES.items()
    ) + sorted(f"(unpublished) | {name}" for name in UNPUBLISHED_NOTES)
    return {
        "classes": digest("\n".join(classes)),
        "bindings": digest("\n".join(bindings)),
        "authorizations": digest("\n".join(grants)),
        "reports": digest("\n".join(notes)),
    }


# -- the vocabulary of a lesser outcome --------------------------------
#
# The SECOND net, and no longer the guarantee. Every phrase below was
# taken from a sentence that actually lowered an obligation in this
# repository, or is the same statement in words no repair has used yet.
# A statement about an exact fact that carries one of these, and no
# authorization the plan grants, is a lowering.
#
# What it cannot do is recognize a lowering written in words nobody
# listed, and round 5 proved that in four separate ways. The seal above
# is what covers those; this list is what names a lowering in terms a
# person reading the failure can act on.

LESSER = (
    # The endpoint lowerings of rounds 1 to 4.
    "met as far as",
    "meets what it can",
    "no cell can show",
    "no cell of its own recorded shape can show",
    "recounted from the written cell",
    "recounted from the finished cells and named",
    "writes the following minute",
    "wrote the following minute",
    "the following minute instead",
    # The free-text and style lowerings.
    "may still fall back",
    "fall back to a deterministic",
    "not exactly reproduced",
    "may miss",
    "can miss",
    "left unplaced",
    "unplaced",
    "is clamped",
    "clamped to that",
    # Ways of saying it nobody has used here yet.
    "is not reproduced",
    "cannot be met",
    "need not be met",
    "is met only as far as",
    "is best effort",
    "the twin writes what it can",
)

# ...unless the same statement settles the description instead, which is
# what a refusal does, or says in as many words that the lesser outcome
# does not reach this fact.
CLEARING = (
    "refus",
    "and no others",
    "no corner, no exception",
    "with no leap-second exception",
    "not loadable",
)

# How far from a fact's own name a lesser statement counts as being
# about it. Sentence boundaries are unreliable in these documents -- the
# calendar lowering ran across a dash and a full stop -- so the window is
# measured in characters and clipped to the passage.
WINDOW = 600

# How close two names have to stand to count as one list, so that a
# statement beside a run of names is read as being about all of them.
TOGETHER = 100

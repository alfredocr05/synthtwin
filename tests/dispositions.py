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

GOVERNING = (
    "docs/plans/phase-2-generator.md",
    "docs/plans/phase-3-product.md",
    "docs/spec/profile-contract-v4.md",
    "docs/spec/generation-method-v1.md",
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
REGISTRY += _facts(
    "universal", REPORT_ONLY, "missing_by_class", "missing_by_source"
)
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
    "count": "numeric",
    "continuous": "numeric",
    "constant": "label",
    "binary": "label",
    "categorical": "label",
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
            "satisfy.** This method has exactly five"
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

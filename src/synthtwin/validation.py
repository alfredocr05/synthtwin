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

AND WHAT DOES NOT COME FROM THE RE-DESCRIPTION (V2.4). Presence is
BLANKNESS. `n_present`, `n_missing`, and the agreement between them and
the re-description are taken over blank and non-blank cells, never over
the re-description's own absence classification: a twin writes every
absent cell empty, and a generated number can legitimately BE the text
of a built-in missing marker (method residual R-P2-13). Where the two
disagree the re-description is the one that yields: no gap in the
reconstruction moves a verdict, and the worst it can do is WITHHOLD a
measurement that could have been printed, which is the safe direction.

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

**No string read from the measured file leaves this module**, in any
field of any result. That is narrower than V5.4 requires -- the file's
own description would publish some of them -- and it is deliberate: it
makes the disclosure obligation one an exact test can prove, and it
costs the report only detail it can live without. Every string in a
result is either the submitted profile's own published text or one of
this module's fixed words.
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
ENVELOPE_TEXT_SHAPE = "docs/spec/generation-method-v1.md G12.6"
ENVELOPE_LABEL_DISTINCT = "docs/spec/generation-method-v1.md G12.7"
ENVELOPE_NUMERIC_DISTINCT = "docs/spec/generation-method-v1.md G12.8"

# -- the refusals of method G12 (V4.3, V9) ----------------------------
#
# These refuse GENERATION, so no conforming twin exists for such a
# profile at all: a validate run on one is a refusal, never a verdict
# and never a pass. Treating one as an authorized corner would launder
# an impossible obligation into a passing report.

REFUSAL_COUNTS_CONTRADICT = "generation-counts-contradict"
REFUSAL_WORDS_EXCEED_LENGTH = "generation-words-exceed-length"
REFUSAL_WHOLE_NUMBERS_NEED_ROOM = "generation-whole-numbers-need-room"

# The fourth refusal method G12 names, `generation-domain-too-small`, is
# NOT detected here, and this module says so rather than implying it is
# complete: deciding it needs the whole packing stage of G9.5 and the
# mixed-radix capacity of G9.2 written independently, which this slice
# does not carry. A profile meeting only that refusal reaches verdicts
# instead of the refusal the specification requires. Stated as a gap so
# a reader is not misled by silence.
REFUSAL_DOMAIN_TOO_SMALL_NOT_DETECTED = "generation-domain-too-small"

# -- entries whose whole obligation lives on the profile (V3.3) -------
#
# LOADER-ONLY facts and the profile-side membership rules of the
# STRUCTURAL containers, as the disposition registry classes them. They
# are named here, and nowhere else, because the projection test has to
# find each one bound to the loader rather than silently absent -- and
# because a fact listed as an unverified twin fact would be an
# obligation the matrix refuses to state.
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

# -- what a withheld subcheck says, in one fixed sentence each --------

_GATE_CLOSED = (
    "describing this file on its own would not publish what this check "
    "measures, so neither the measurement nor its outcome is shown"
)
_GATE_PRESENCE = (
    "this file holds cells the description of it reads as absent that "
    "are not blank, so a measurement taken over its present cells is "
    "not the measurement this check needs"
)

# The eleven ladder positions as probabilities, in ladder order.
_LADDER_SHARES = tuple(
    [number / denominator for _name, number, denominator in taxonomy.LADDER]
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

    NEITHER TEXT FIELD EVER HOLDS A STRING READ FROM THE MEASURED FILE.
    """

    column: str
    fact: str
    subcheck: str
    verdict: str
    published: str = ""
    achieved: str = ""
    citation: str = ""


@dataclasses.dataclass(frozen=True)
class Listing:
    """One obligation no CSV can evidence, and why (V3.3).

    A listing entry carries no verdict and is never counted toward a
    pass. Its failure mode is the census itself: a line removed from it
    is a line missing from the report.
    """

    column: str
    fact: str
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
    """Everything one validate run measured.

    ``checks`` is every executable subcheck with its verdict, in a
    fixed order: the document-level obligations first, then the columns
    in the description's own order. ``listings`` is every obligation no
    CSV can evidence. ``census`` counts both.
    """

    checks: "tuple[Check, ...]"
    listings: "tuple[Listing, ...]"
    census: Census


# -- V2.2: the settings the file is re-described under ----------------


def settings_for(description: contract.Profile) -> taxonomy.Settings:
    """Rebuild the taxonomy settings the description was written under.

    Guarantees:

    - Inputs: one loaded description. Nothing else is consulted -- no
      command line, no default, no environment.
    - Determinism: the same description always gives the same settings.
    - Errors raised: none.
    - Boundary: the two declaration tuples come back EMPTY of the
      person's own spellings, because the contract deliberately does not
      record them (`values_recorded` is false by invariant), and
      `kept_values` instead carries the set recovered from the
      description itself (`kept_spellings`). `declared_missing_values`
      is empty exactly: a declared-missing spelling is genuinely absent
      from every twin, whose absent cells are written empty. The read
      mode is NOT a settings key and is not decided here; it comes from
      `source.header_source`.

    Every one of the fifteen keys the settings block carries is used,
    and no sixteenth is invented: a skipped key would describe the file
    under rules the description was not written under, which is the one
    way the disclosure gate can be walked past.
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
        declared_missing_values=(),
        declaration_matching=block.declaration_matching,
        near_threshold_slack=block.near_threshold_slack,
    )


def kept_spellings(description: contract.Profile) -> "tuple[str, ...]":
    """The spellings a conforming twin may hold that read as absences.

    Guarantees:

    - Inputs: one loaded description. Nothing is read from any file.
    - Determinism: the returned tuple is sorted, so the same
      description always gives the same tuple in the same order.
    - Errors raised: none.
    - Boundary: every spelling here is the description's OWN published
      text. Nothing is guessed, and nothing the person typed is
      recovered, because the contract records no declared spelling at
      all.

    Three published routes, all of them recovered (owner decision 8 as
    amended):

    - every key of every published level's `variants`, which is the
      exact spelling a kept value published as a label carries;
    - every `sentinel_verdicts` candidate whose reason is exactly
      `kept_by_you`, which is how a kept NUMERIC value is published.
      It is matched at the profiler's own declaration-matching identity
      -- numeric identity for a candidate that reads as a number --
      because the settings carry that rule and it is applied to this
      set exactly as it is applied to a declared one;
    - every published `levels[].label`, which a measured cell meets at
      the FOLDED identity, the producer's own pooling rule. A level
      whose spellings all sit below the floor publishes no variant at
      all and the twin invents spellings that fold to the parent, so
      without this route the gate would read the very twin it must
      validate as a column of absences.

    A gap here costs detail and never a verdict: presence is measured
    from blank and non-blank cells (V2.4), so nothing this tuple misses
    can move an outcome.
    """
    # A mapping rather than a set: the offline policy accepts no method
    # call on a value it cannot trace, and `set.add` is one, while
    # setting a key is not (plan D6.2). The values are never read.
    found: dict[str, int] = {}
    for column in description.columns:
        for verdict in column.sentinel_verdicts:
            if verdict.reason == taxonomy.REASON_KEPT_BY_USER:
                found[verdict.candidate] = 1
        facts = column.facts
        if isinstance(facts, contract.LabelFacts):
            for level in facts.levels:
                found[level.label] = 1
                for spelling in level.variants:
                    found[spelling] = 1
    return tuple(sorted(found))


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
        if isinstance(
            facts, contract.NumericFacts
        ) and _numeric_spellings_are_short(column, facts):
            corners = corners + [CORNER_NUMERIC_SPELLINGS_SHORT]
        if corners:
            found[column.name] = tuple(corners)
    return found


def _identifier_is_infeasible(
    column: contract.ColumnBlock, facts: contract.IdentifierFacts
) -> bool:
    """True when the published lengths cannot supply that many codes.

    Owner decision 6's corner: a declared identifier whose published
    length range cannot spell `n_present` different values. The count
    below is a CEILING on what any construction can reach, so a column
    it clears is never called a corner it is not in.

    The alphabet a length can draw on is bounded by the description's
    own two counts: a column whose cells are all digits can spell ten
    characters per position, and one that reaches the code alphabet can
    spell the thirty-six a digit-and-letter code has. Whichever of the
    two the description publishes, the ceiling is taken at the wider
    one, so the corner is claimed only where even the wide reading
    falls short.
    """
    if facts.max_length < 1:
        return column.n_present > 1
    alphabet = 10 if facts.n_code_alphabet == 0 else 36
    room = 0
    length = facts.min_length
    while length <= facts.max_length:
        room = room + alphabet**length
        if room >= column.n_present:
            return False
        length = length + 1
    return room < column.n_present


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
    supply = _spelling_supply(facts)
    return supply is not None and supply < column.n_distinct


def _numeric_spellings_are_short(
    column: contract.ColumnBlock, facts: contract.NumericFacts
) -> bool:
    """True when the permitted spellings cannot reach distinctness.

    The `supply` of method G12.8, read off the published map: a `plain`
    group can carry one spelling of its value, and every other style
    carries the leading-zero family, so its cells can each carry their
    own. Where the supply reaches the published counts the two facts
    are exact -- the ordinary case -- and where it does not, the twin
    owes the two-sided envelope instead.
    """
    supply = _spelling_supply(facts)
    if supply is None:
        return False
    if supply < column.n_distinct:
        return True
    return supply < column.n_distinct_folded


# -- V9 and V4.3: the refusals that mean no conforming twin exists ----


def refusal_of(description: contract.Profile) -> str:
    """The name of the G12 refusal this description meets, or "".

    Guarantees:

    - Inputs: one loaded description. No file is read.
    - Determinism: a pure function of the description.
    - Errors raised: none -- this NAMES a refusal, it does not raise
      one; `measure` turns the name into a message.
    - Boundary: three of the four refusals method G12 fixes are decided
      here, each from the published numbers its own passage names.
      `generation-domain-too-small` is NOT among them; the module
      docstring for `REFUSAL_DOMAIN_TOO_SMALL_NOT_DETECTED` says what
      that costs, plainly, rather than letting silence read as
      coverage.
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
        if isinstance(facts, contract.IdentifierFacts) and (
            facts.all_whole_numbers
        ):
            if facts.max_length == 1 and facts.n_all_digits < column.n_present:
                return REFUSAL_WHOLE_NUMBERS_NEED_ROOM
            if facts.min_length == 1 and facts.n_all_digits == 0:
                return REFUSAL_WHOLE_NUMBERS_NEED_ROOM
    return ""


def _refusal_message(named: str, shown: str) -> str:
    """The refusal a person reads when no twin of this profile exists.

    It mirrors the generation refusal -- the description is valid, and
    two published facts cannot both hold -- and adds the sentence this
    path needs: whatever the measured file is, it cannot be that
    description's twin. It names no value of the measured file, because
    on this path that file may not be the person's own table.
    """
    trouble = {
        REFUSAL_COUNTS_CONTRADICT: (
            "one column says how many of its numbers are zero and how "
            "many are negative, and those two counts together are more "
            "numbers than the column has"
        ),
        REFUSAL_WORDS_EXCEED_LENGTH: (
            "one column of text says its values hold more words than "
            "their own published lengths have room for"
        ),
        REFUSAL_WHOLE_NUMBERS_NEED_ROOM: (
            "one column of record numbers says its codes are whole "
            "numbers and gives them a length that leaves no room to "
            "write one"
        ),
    }[named]
    return (
        f"synthtwin stopped because the description asks for a table "
        f"that cannot exist: {trouble}. The description itself is "
        f"valid -- it was written by synthtwin and it loads -- but no "
        f"file can hold both of those facts at once, so whatever is in "
        f"{shown}, it cannot be this description's twin and there is "
        f"nothing to measure it against. Describe the table again to "
        f"get a description these two facts agree in, and if you no "
        f"longer hold the table, ask whoever wrote the description to "
        f"do so."
    )


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

    The path is rebuilt here for the reason `_read_bytes` gives: a value
    an allowlisted API built is a value whose methods the offline audit
    has already checked, and a parameter is not (plan D6.2).
    """
    file_path = pathlib.Path(place)
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def _starts_with_a_mark(data: bytes) -> bool:
    """True when the file's first bytes are a UTF-8 byte-order mark.

    A column name that genuinely begins with U+FEFF is written QUOTED,
    so the file's first byte is the quote and the mark that follows is
    inside a field rather than in front of the file. That exception is
    why this looks at the file's first three bytes and at nothing else.
    """
    return data[:3] == b"\xef\xbb\xbf"


def _first_line(text: str) -> str:
    """The text up to and including its first line feed, or all of it."""
    if not isinstance(text, str):
        raise TypeError("internal check: a file's text was not text")
    at = text.find("\n")
    if at < 0:
        return text
    return text[: at + 1]


def _header_names(line: str) -> "list[str]":
    """The column names one header line holds, by the CSV rules."""
    for row in csv.reader([line]):
        return [f"{cell}" for cell in row]
    return []


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
) -> Check:
    """One exact obligation whose measured value may not be shown.

    Used where the achieved value is a STRING taken from the measured
    file. The comparison is made in full and the verdict is reported;
    the value itself never leaves this module.
    """
    if held is None:
        return Check(column, fact, subcheck, WITHHELD, published, "", _GATE_CLOSED)
    return Check(column, fact, subcheck, HELD if held else MISSED, published)


def _within(
    column: str,
    fact: str,
    subcheck: str,
    published: str,
    measured: "float | None",
    window: "tuple[float, float] | None",
    citation: str,
) -> Check:
    """One approximated obligation, against both ends of its envelope."""
    if measured is None or window is None:
        return Check(column, fact, subcheck, WITHHELD, published, "", _GATE_CLOSED)
    low, high = window
    verdict = WITHIN_BOUND if low <= measured <= high else MISSED
    return Check(
        column,
        fact,
        subcheck,
        verdict,
        f"{published} ({_shown_window(low, high)})",
        _shown_number(measured),
        citation,
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
      report does. `PathValidationError` when the path is not a plain
      local one. A structural mismatch is NOT a refusal: a wrong column
      count, a wrong name or a wrong row count is a MISSED verdict with
      a plain explanation, because the report is the product even when
      the news is bad.
    - Boundary: this reads two files and writes none. It never writes,
      moves, truncates or re-encodes the measured file or the
      description. It does not import the generation module, and no
      string read from the measured file appears in any field of the
      result.
    """
    named = refusal_of(description)
    validated = validate_local_path(path, purpose="input")
    place = pathlib.Path(validated)
    shown = f"{place}"
    if named:
        raise errors.ProfileError(_refusal_message(named, shown))
    if not place.exists():
        raise errors.ProfileError(errors.file_missing(shown))
    if place.is_dir():
        raise errors.ProfileError(errors.path_is_a_folder(shown))
    try:
        data = _read_bytes(place)
        text = _read_utf8(place)
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
    checks = _byte_checks(description, data, text, headed)
    if description.n_rows == 0:
        return _assembled(
            checks + [_zero_row_form(description, data, text, headed)],
            _zero_row_listings(description, headed),
        )
    if _holds_no_data(text, headed):
        return _assembled(
            checks + _no_rows_at_all(description),
            _no_rows_listings(description),
        )
    settings = settings_for(description)
    first_row = reading.FIRST_ROW_NAMES if headed else reading.FIRST_ROW_DATA
    try:
        table = reading.read_table(path, first_row=first_row)
        redescribed = profile.build_document(
            table, settings, _declared_here(description, table)
        )
    except MemoryError as error:
        raise errors.ProfileError(
            errors.out_of_memory_while_describing(shown)
        ) from error
    checks = checks + _structure_checks(description, table, text, headed)
    for column in description.columns:
        checks = checks + _column_checks(
            description, column, table, redescribed
        )
    return _assembled(checks, _listings(description, headed))


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


def _assembled(
    checks: "list[Check]", listings: "list[Listing]"
) -> Outcome:
    """One outcome, with the census counted from the verdicts alone."""
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
    return Outcome(tuple(checks), tuple(listings), census)


# -- V6.2 and V6.4: the byte rules ------------------------------------


def _byte_checks(
    description: contract.Profile,
    data: bytes,
    text: "str | None",
    headed: bool,
) -> "list[Check]":
    """Every rule about the file's bytes, each one able to fail."""
    checks = [
        _exact(
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
                if b"\r" in data
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
    """
    subcheck = "bytes.zero-row-form"
    fact = "document.n_rows"
    if not headed:
        published = "a file of no bytes at all"
        measured = published if len(data) == 0 else "a file holding bytes"
        return _exact("", fact, subcheck, published, measured)
    published = "the header line and its newline, and nothing more"
    if text is None:
        return Check("", fact, subcheck, MISSED, published, "not UTF-8")
    line = _first_line(text)
    names = _header_names(line)
    holds = (
        len(text) == len(line)
        and line[len(line) - 1 :] == "\n"
        and names == [column.name for column in description.columns]
    )
    return _silent("", fact, subcheck, published, holds)


def _holds_no_data(text: "str | None", headed: bool) -> bool:
    """True when a file the description expects rows from holds none.

    The profiler's own reader refuses such a file, and refusing here
    would turn a structural mismatch into a run that never happened.
    The plan is explicit that a structural mismatch is a MISSED verdict
    with a plain explanation, so this is settled before the reader is
    called at all.
    """
    if text is None:
        return False
    if not headed:
        return len(text) == 0
    return len(text) == len(_first_line(text))


def _no_rows_at_all(description: contract.Profile) -> "list[Check]":
    """The one verdict a file with no rows can carry."""
    return [
        Check(
            "",
            "document.n_rows",
            "rows.n_rows",
            MISSED,
            _shown_count(description.n_rows),
            _shown_count(0),
        )
    ]


# -- V6.2: the structure the file must have ---------------------------


def _structure_checks(
    description: contract.Profile,
    table: reading.Table,
    text: "str | None",
    headed: bool,
) -> "list[Check]":
    """Row count, column count and order, and the header read-back."""
    names = [column.name for column in description.columns]
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
            _header_presence(text, table, headed),
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
            ),
            _silent(
                "",
                "document.columns",
                "columns.order",
                "the published column order",
                table.column_names == names,
            ),
        ]
    return checks


def _header_presence(
    text: "str | None", table: reading.Table, headed: bool
) -> str:
    """What the file shows about whether a header was written.

    With a header the question is answerable: the first line either
    reads back as the published names or it does not. Without one there
    is nothing in a CSV that distinguishes an absent header from a first
    record, and this says so instead of inventing an answer -- the
    obligation is carried as a listing entry for that predicate.
    """
    if not headed:
        return "no header line, the first row is a record"
    if text is None:
        return "no header line"
    if _header_names(_first_line(text)) == table.column_names:
        return "a header line"
    return "no header line"


# -- the per-column measurement ---------------------------------------


def _column_checks(
    description: contract.Profile,
    column: contract.ColumnBlock,
    table: reading.Table,
    redescribed: "dict[str, object]",
) -> "list[Check]":
    """Every subcheck one published column carries."""
    name = column.name
    floor = description.settings.small_cell_floor
    cells = _cells_of(table, column.position)
    if cells is None:
        return [
            Check(
                name,
                "document.n_columns",
                "column.present",
                MISSED,
                "a column at this position",
                "no column at this position",
            )
        ]
    present, missing = _presence_of(cells)
    checks = [
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
    block = _column_at(redescribed, column.position)
    if block is None:
        return checks
    checks = checks + [
        _exact(
            name,
            "universal.statistical_type",
            "axes.statistical_type",
            column.statistical_type,
            _text_at(block, "statistical_type"),
        )
    ]
    # V2.4. Every measurement whose input is the set of present cells is
    # taken over the blank/non-blank split, so where the re-description
    # read some non-blank cell as an absence its numbers are not the
    # numbers these checks need. That gap withholds; it never verdicts.
    if _count_at(block, "n_present") != present:
        return checks + _presence_gap(column)
    mine = _corner_names(corners_of(description), name)
    checks = checks + _universal_checks(column, block, mine)
    checks = checks + _role_checks(column, block, cells, floor, mine)
    return checks


def _cells_of(
    table: reading.Table, position: int
) -> "list[str] | None":
    """The measured cells at one position, or None when there are none."""
    if position < 1 or position > len(table.columns):
        return None
    return table.columns[position - 1]


def _presence_of(cells: "list[str]") -> "tuple[int, int]":
    """How many cells are present and how many absent, by BLANKNESS.

    The contract's own rule for twins: every absent cell is written as
    an empty field. So presence is decided here and nowhere else, with
    no sentinel and no declaration machinery anywhere near a verdict.
    """
    present = 0
    for cell in cells:
        if parsing.trimmed(cell):
            present = present + 1
    return present, len(cells) - present


def _presence_gap(column: contract.ColumnBlock) -> "list[Check]":
    """What is withheld when the reconstruction did not close the gap."""
    return [
        _withheld(
            column.name,
            "universal.n_present",
            "presence.agreement",
            _GATE_PRESENCE,
        )
    ]


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
    """The two distinctness counts, at whatever bar this profile sets."""
    name = column.name
    facts = column.facts
    group = _group_of(facts)
    checks: list[Check] = []
    for field, published in (
        ("n_distinct", column.n_distinct),
        ("n_distinct_folded", column.n_distinct_folded),
    ):
        measured = _count_at(block, field)
        fact = f"{group}.{field}"
        subcheck = f"distinct.{field}"
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
                )
            ]
            continue
        corner = _distinct_corner(facts, mine)
        if corner:
            checks = checks + [
                _lesser_or_held(
                    name, fact, subcheck, published, measured, corner, facts
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
    facts: contract.ColumnFacts,
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
    if corner == CORNER_IDENTIFIER_INFEASIBLE:
        # Owner decision 6 makes the three distinctness facts
        # REPORT-ONLY in this corner, with no envelope of any kind, so
        # there is no window to land inside.
        return _deviation(name, fact, subcheck, shown, corner)
    supply = _spelling_supply(facts)
    if supply is None:
        return _deviation(name, fact, subcheck, shown, corner)
    low = min(supply, published)
    high = max(supply, published)
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


def _spelling_supply(facts: contract.ColumnFacts) -> "int | None":
    """How many different spellings this column's own rules can supply.

    The `S` of method G12.7 on a column of labels and the `supply` of
    G12.8 on a column of numbers, each read off the published fields
    alone. On a numeric column the canonical spelling has no family of
    its own, so the whole `plain` key supplies ONE identity between all
    its cells; every other style carries the leading-zero family, so
    each of its cells can carry its own.
    """
    if isinstance(facts, contract.LabelFacts):
        supply = 0
        for level in facts.levels:
            named = 0
            for spelling in level.variants:
                supply = supply + 1
                named = named + level.variants[spelling]
            for spelling in level.variants_withheld:
                supply = supply + level.variants_withheld[spelling]
                named = named + level.variants_withheld[spelling]
            if named < level.count:
                supply = supply + 1
        return supply + facts.suppressed_levels
    if isinstance(facts, contract.NumericFacts):
        supply = 0
        for style in facts.numeric_styles:
            if style == parsing.STYLE_PLAIN:
                supply = supply + 1
            else:
                supply = supply + facts.numeric_styles[style]
        return supply
    return None


def _distinct_corner(
    facts: contract.ColumnFacts, mine: "tuple[str, ...]"
) -> str:
    """Which corner, if any, lowers this column's distinctness bar."""
    if CORNER_IDENTIFIER_INFEASIBLE in mine:
        return CORNER_IDENTIFIER_INFEASIBLE
    if isinstance(facts, contract.LabelFacts) and (
        CORNER_LABEL_VARIANTS_SHORT in mine
    ):
        return CORNER_LABEL_VARIANTS_SHORT
    if isinstance(facts, contract.NumericFacts) and (
        CORNER_NUMERIC_SPELLINGS_SHORT in mine
    ):
        return CORNER_NUMERIC_SPELLINGS_SHORT
    return ""


def _group_of(facts: contract.ColumnFacts) -> str:
    """Which registry group a column's role publishes under."""
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
    if isinstance(facts, contract.NumericFacts):
        return _numeric_checks(column, facts, block, cells, floor)
    if isinstance(facts, contract.LabelFacts):
        return _label_checks(column, facts, block, floor)
    if isinstance(facts, contract.DatetimeFacts):
        return _datetime_checks(column, facts, block, floor, mine)
    if isinstance(facts, contract.TextFacts):
        return _text_checks(column, facts, block)
    if isinstance(facts, contract.IdentifierFacts):
        return _identifier_checks(column, facts, block, mine)
    if isinstance(facts, contract.UnrepresentableFacts):
        return _unrepresentable_checks(column, facts, block)
    return []


# -- the numeric roles ------------------------------------------------


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
    measured_truth = _truth_at(block, "integer_valued")
    checks = checks + [
        _exact(
            name,
            "numeric.integer_valued",
            "type.integer_valued",
            _shown_truth(facts.integer_valued),
            None if measured_truth is None else _shown_truth(measured_truth),
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


def _moment_checks(
    column: contract.ColumnBlock,
    facts: contract.NumericFacts,
    block: "dict[str, object]",
) -> "list[Check]":
    """`mean`, `std` and `skew`, each against both ends of G12.3.

    A description whose ladder is null at every rung publishes no shape
    at all, so there is no window to draw and the three are listed as
    not checkable rather than passed.
    """
    name = column.name
    points = _ladder_points(facts.percentiles.rungs)
    published = (
        ("mean", facts.mean),
        ("std", facts.std),
        ("skew", facts.skew),
    )
    checks: list[Check] = []
    if not points:
        return checks
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
    windows = _moment_windows(lows, highs, ladder, numbers)
    for field, value in published:
        if value is None:
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

    The counts themselves are not printed: a recount below the floor is
    a number the file's own description would pool away, and the exact
    sub-floor number never appears beside a name. The comparison is
    still made in full, and the verdict is reported.
    """
    name = column.name
    if "numeric_styles" not in block:
        # The gate closed. Every obligation this column carries is still
        # ACCOUNTED FOR -- withheld one by one rather than dropped --
        # because an obligation that leaves the census without a line is
        # an obligation a reader cannot tell was never measured.
        withheld = [
            _withheld(
                name, "numeric.numeric_styles", "styles.identity", _GATE_CLOSED
            )
        ]
        for style in sorted(facts.numeric_styles):
            if style == taxonomy.SUPPRESSED_LABEL:
                continue
            withheld = withheld + [
                _withheld(
                    name,
                    "numeric.numeric_styles",
                    f"styles.published.{style}",
                    _GATE_CLOSED,
                )
            ]
        return withheld
    recount, no_point_free = _recounted_styles(cells)
    published = facts.numeric_styles
    remainder = _counted(published, taxonomy.SUPPRESSED_LABEL)

    def named(style: str) -> int:
        return _counted(published, style)

    def found(style: str) -> int:
        return _counted(recount, style)

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
                found(style) == named(style),
            )
        ]
    for style in (
        parsing.STYLE_PLAIN,
        parsing.STYLE_DECIMAL,
        parsing.STYLE_EXPONENT_LOWER,
    ):
        checks = checks + [
            _silent(
                name,
                "numeric.numeric_styles",
                f"styles.at-least.{style}",
                _shown_count(named(style)),
                found(style) >= named(style),
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
            found(parsing.STYLE_DECIMAL) + found(parsing.STYLE_EXPONENT_LOWER)
            == named(parsing.STYLE_DECIMAL)
            + named(parsing.STYLE_EXPONENT_LOWER)
            + spill,
        ),
        _silent(
            name,
            "numeric.numeric_styles",
            "styles.remainder",
            "the pooled cells are spelled by their own values",
            found(parsing.STYLE_PLAIN)
            == named(parsing.STYLE_PLAIN) + remainder - spill,
        ),
    ]
    measured = _map_at(block, "numeric_styles")
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
            )
        ]
    return checks


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


def _floor_governed(
    name: str,
    fact: str,
    subcheck: str,
    published: int,
    measured: "dict[str, int] | None",
    key: str,
    floor: int,
) -> Check:
    """One named count, printed exactly only when it clears the floor.

    Where the file's own description omits the key, that omission
    already publishes exactly one thing: the identity covers fewer rows
    than the floor in this file, and possibly none. So the line says
    that and no more, the exact sub-floor number never appears beside
    the name, and the MISSED verdict follows from the two statements
    already made -- published at or above the floor, measured below it.
    """
    if measured is None:
        return Check(
            name, fact, subcheck, WITHHELD, _shown_count(published), "", _GATE_CLOSED
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
    for level in facts.levels:
        key = parsing.folded(parsing.trimmed(level.label))
        entry = (
            measured[key] if measured is not None and key in measured else None
        )
        checks = checks + [
            _level_count(name, level, entry, measured, floor),
            _variant_map(name, level, entry, measured, "variants"),
            _variant_map(name, level, entry, measured, "variants_withheld"),
        ]
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
    return checks


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
    """
    published = (
        level.variants if field == "variants" else level.variants_withheld
    )
    fact = f"label.{field}"
    subcheck = f"levels.{level.label}.{field}"
    shown = _shown_count(len(published))
    if measured is None or entry is None:
        return Check(name, fact, subcheck, WITHHELD, shown, "", _GATE_CLOSED)
    found = _map_at(entry, field)
    if found is None:
        return Check(name, fact, subcheck, WITHHELD, shown, "", _GATE_CLOSED)
    return _silent(name, fact, subcheck, shown, found == published)


# -- the datetime role ------------------------------------------------


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
        return [
            _deviation(name, "datetime.utc_offsets", "offsets.map", "withheld", corner),
            _deviation(
                name,
                "datetime.earliest_utc_offset",
                "offsets.earliest",
                facts.earliest_utc_offset,
                corner,
            ),
            _deviation(
                name,
                "datetime.latest_utc_offset",
                "offsets.latest",
                facts.latest_utc_offset,
                corner,
            ),
            _deviation(
                name,
                "datetime.datetimes_read_at",
                "offsets.read-at",
                facts.datetimes_read_at,
                corner,
            ),
        ]
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
        found = _text_at(block, field)
        checks = checks + [
            _silent(
                name,
                f"datetime.{field}",
                subcheck,
                published,
                None if found is None else found == published,
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

    The window is method G12.4's, taken in the ordinal space of whole
    seconds the profiler's own `parsing.instant_key` reads a canonical
    instant into. The rung a description publishes is SELECTED, not
    interpolated -- there is no half-way point between two dates a
    calendar recognises -- so the window is the band the rank's own two
    ends make, widened by what reading a written cell back can lose.
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
            )
        ]
    ordinals = _date_points(published.rungs)
    if ordinals is None:
        # A ladder whose rungs name no instant -- a column of quarters --
        # has no ordinal space to draw a window in. The nine rungs are
        # withheld one by one rather than dropped, for the reason the
        # style gate gives.
        for index in range(1, len(_LADDER_KEYS) - 1):
            checks = checks + [
                _withheld(
                    name,
                    "datetime.date_percentiles",
                    f"date-ladder.{_LADDER_KEYS[index]}",
                    _GATE_CLOSED,
                )
            ]
        return checks
    dated = max(1, column.n_present - facts.n_unparsed)
    unit = _reading_unit(facts)
    for index in range(1, len(_LADDER_KEYS) - 1):
        key = _LADDER_KEYS[index]
        found = None if measured is None else _text_at(measured, key)
        seen = None if found is None else parsing.instant_key(found, "")
        rank = ((dated - 1) * _LADDER_SHARES[index] * 100) // 100
        low = _ladder_at(ordinals, rank / dated) - unit
        high = _ladder_at(ordinals, min(1.0, (rank + 1) / dated))
        checks = checks + [
            _within(
                name,
                "datetime.date_percentiles",
                f"date-ladder.{key}",
                published.rungs[index],
                None if seen is None else float(seen),
                (low, high),
                ENVELOPE_DATETIME_RUNGS,
            )
        ]
    return checks


def _datetime_distinct_window(
    column: contract.ColumnBlock, facts: contract.DatetimeFacts
) -> "tuple[float, float] | None":
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
    """
    ordinals = _date_points(facts.date_percentiles.rungs)
    if ordinals is None:
        return None
    dated = max(1, column.n_present - facts.n_unparsed)
    unit = _reading_unit(facts)
    separate = 0
    ceiling = None
    for rank in range(dated):
        low = _ladder_at(ordinals, rank / dated) - unit
        high = _ladder_at(ordinals, min(1.0, (rank + 1) / dated))
        if ceiling is None or low > ceiling:
            separate = separate + 1
            ceiling = high
    step = _precision_step(facts)
    earliest = parsing.instant_key(facts.earliest, "")
    latest = parsing.instant_key(facts.latest, "")
    if earliest is None or latest is None:
        return None
    named = 0
    for key in facts.utc_offsets:
        if key != taxonomy.SUPPRESSED_LABEL:
            named = named + 1
    room = (latest - earliest) // step + 1
    upper = min(column.n_present, room * max(1, named) + facts.n_unparsed)
    lower = min(separate + facts.n_unparsed, upper)
    return (float(lower), float(upper))


def _precision_step(facts: contract.DatetimeFacts) -> int:
    """How many whole seconds apart two neighbouring instants are."""
    if facts.resolution == taxonomy.RESOLUTION_DATE:
        return 86400
    if facts.time_precision == parsing.PRECISION_MINUTE:
        return 60
    return 1


def _date_points(
    rungs: "tuple[str, ...]",
) -> "list[tuple[float, float]] | None":
    """The published date ladder as (share, whole seconds) points."""
    points: list[tuple[float, float]] = []
    for index, moment in enumerate(rungs):
        seconds = parsing.instant_key(moment, "")
        if seconds is None:
            return None
        points = points + [(_LADDER_SHARES[index], float(seconds))]
    return points


def _reading_unit(facts: contract.DatetimeFacts) -> float:
    """What reading one written cell back can lose, in whole seconds.

    One unit for the downward rounding of the whole-number
    interpolation itself, plus the fifty-nine seconds a cell written to
    the minute carries no room for.
    """
    if facts.resolution == taxonomy.RESOLUTION_DATE:
        return 86400.0
    if facts.time_precision == parsing.PRECISION_MINUTE:
        return 119.0
    return 1.0


# -- free text, identifiers, and the unrepresentable role -------------


def _text_checks(
    column: contract.ColumnBlock,
    facts: contract.TextFacts,
    block: "dict[str, object]",
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
    return checks


def _text_shape_checks(
    column: contract.ColumnBlock,
    facts: contract.TextFacts,
    lengths: "dict[str, object] | None",
    words: "dict[str, object] | None",
) -> "list[Check]":
    """The three averages of method G12.6, each inside its own window.

    The window is the reach of G9.5's walk expressed at the grain this
    module can derive from the description alone: the walk pins one
    group to each published end and leaves the rest between them, so
    every achieved average lies between the two ends the column
    publishes. The bound is the outer one of the pair the method names,
    which is the safe direction -- a wider window can fail to catch a
    twin, never accuse a conforming one -- and it is still able to
    fail, because a twin writing values outside its own published ends
    leaves it.
    """
    name = column.name
    checks: list[Check] = []
    for key, published, holder, low, high, fact in (
        (
            "mean",
            facts.length.mean,
            lengths,
            float(facts.length.minimum),
            float(facts.length.maximum),
            "free_text.length.mean",
        ),
        (
            "p50",
            facts.length.p50,
            lengths,
            float(facts.length.minimum),
            float(facts.length.maximum),
            "free_text.length.p50",
        ),
        (
            "mean",
            facts.words.mean,
            words,
            float(max(1, facts.words.minimum)),
            float(max(1, facts.words.maximum)),
            "free_text.words.mean",
        ),
    ):
        if published is None:
            continue
        found = None if holder is None else _number_at(holder, key)
        subcheck = f"{'length' if holder is lengths else 'words'}.{key}"
        checks = checks + [
            _within(
                name,
                fact,
                subcheck,
                _shown_number(published),
                found,
                (low, high),
                ENVELOPE_TEXT_SHAPE,
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
    checks = checks + [
        _occurrences(
            name,
            "identifier.n_distinct_by_occurrences",
            facts.n_distinct_by_occurrences,
            block,
            mine,
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
            (),
        )
    ]
    return checks


def _occurrences(
    name: str,
    fact: str,
    published: "dict[str, int]",
    block: "dict[str, object]",
    mine: "tuple[str, ...]",
) -> Check:
    """The multiplicity map, compared whole and never spelled out."""
    subcheck = "distinct.n_distinct_by_occurrences"
    shown = _shown_count(len(published))
    found = _map_at(block, "n_distinct_by_occurrences")
    if found is None:
        return Check(name, fact, subcheck, WITHHELD, shown, "", _GATE_CLOSED)
    if found == published:
        return Check(name, fact, subcheck, HELD, shown)
    if CORNER_IDENTIFIER_INFEASIBLE in mine:
        return _deviation(
            name, fact, subcheck, shown, CORNER_IDENTIFIER_INFEASIBLE
        )
    return Check(name, fact, subcheck, MISSED, shown)


# -- V3.3: the obligations no CSV can evidence ------------------------


def _listings(
    description: contract.Profile, headed: bool
) -> "list[Listing]":
    """Every REPORT-ONLY obligation, and the ones a predicate strands."""
    listings = [
        Listing("", f"document.{field}", _NOT_CHECKABLE_REPORT_ONLY)
        for field in (
            "source.encoding",
            "source.used_fallback_encoding",
            "source.header_by_convention",
            "source.header_evidence",
        )
    ]
    if not headed:
        listings = listings + [
            Listing("", "universal.name", _NOT_CHECKABLE_HEADERLESS_ORDER),
            Listing("", "document.columns", _NOT_CHECKABLE_HEADERLESS_ORDER),
        ]
    for column in description.columns:
        for field in (
            "missing_by_class",
            "missing_by_source",
            "n_sentinel_candidates_unpublished",
            "sentinel_verdicts",
            "detection_evidence",
            "remarks",
        ):
            listings = listings + [
                Listing(
                    column.name,
                    f"universal.{field}",
                    _NOT_CHECKABLE_REPORT_ONLY,
                )
            ]
        facts = column.facts
        if isinstance(facts, contract.DatetimeFacts):
            listings = listings + [
                Listing(
                    column.name, "datetime.format", _NOT_CHECKABLE_REPORT_ONLY
                )
            ]
        if isinstance(facts, contract.NumericFacts) and not _ladder_points(
            facts.percentiles.rungs
        ):
            listings = listings + [
                Listing(
                    column.name,
                    f"numeric.{field}",
                    _NOT_CHECKABLE_NO_LADDER,
                )
                for field in ("mean", "std", "skew")
            ]
    return listings


def _zero_row_listings(
    description: contract.Profile, headed: bool
) -> "list[Listing]":
    """What a file of no rows cannot evidence (owner decision 7)."""
    listings = _listings(description, headed)
    if headed:
        return listings
    return listings + [
        Listing("", "document.n_columns", _NOT_CHECKABLE_ZERO_ROWS),
        Listing("", "universal.position", _NOT_CHECKABLE_ZERO_ROWS),
    ]


def _no_rows_listings(
    description: contract.Profile,
) -> "list[Listing]":
    """What a file holding no rows at all leaves unmeasurable."""
    listings: list[Listing] = []
    for column in description.columns:
        listings = listings + [
            Listing(column.name, "universal.n_present", _NOT_CHECKABLE_ZERO_ROWS)
        ]
    return listings

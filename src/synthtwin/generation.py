"""The generator: a twin table from the description and the seed alone.

The normative text is `docs/spec/generation-method-v1.md`, and this
module carries out its sections G1 to G12 rule for rule. Where that text
names a section -- G5.3, G7.4, G9.2 -- the function below that carries it
out cites the same name, so the two can be held side by side.

THE BOUNDARY THIS MODULE UPHOLDS (method G1, plan P2-D1). Every input to
every rule here is one of exactly three things: a field of the loaded
description, a word from the one random stream, or a constant written
into this file. There is no fourth. This module never reads the real
table, never accepts a table path, a table handle, a table object or a
collection of raw cells, and imports neither `reading` nor pandas,
directly or through anything it does import: `contract` reads one
description file and nothing else, `errors` and `parsing` import nothing
outside this package. It reads no file at all. It writes no file at all.
It hands back values, and the command decides what becomes of them.

ONE STREAM, ONE DRAW SHAPE (method G3, plan P2-D8). Exactly one random
generator exists in a run, made once from the seed and threaded through
by hand. Every random quantity is a full-width unsigned 64-bit word, and
uniforms, bounded ranges and arrangements are derived from those words in
first-party whole-number arithmetic, so that no rounding mode and no
platform difference can reach a twin cell. Columns are consumed in the
description's own list order, and the first word of a run belongs to the
first column. Special elements -- the ends of a ladder, the zeros, the
class stand-ins, every made-up spelling, every label and every label
variant -- are placed by fixed rule and cost no word at all: where this
module pins a value, no word is drawn for it and none is thrown away.

DISPATCH IS ON THE THREE AXES, NEVER ON THE ROLE (plan P2-D3). A column
is routed by its `quality_state` and its `statistical_type`, which is
what those axes are for; the role name is carried into the report and is
never asked a question here.

WHAT IT HANDS BACK. The twin's cells, and a record of what the twin
ACHIEVED beside what the description PUBLISHED, column by column. Every
deviation the method permits is measured against the published fact and
named in that record, every run (method G12), so the report renders a
list this module produced rather than a claim it made up. The same
record carries every fact the contract calls APPROXIMATED -- an
average, an interior rung, a count of different dates, the length and
word summaries of free text -- each measured on the finished cells
against BOTH ends of the bound method G12.1 to G12.8 fix for it, so a
fact that is not exact is a fact with a printed range beside it rather
than a silence (review item P2-C1-F4).

WHERE THE CELLS OF A MADE-UP COLUMN ARE BUILT, and why it is not where a
reader expects. The three roles that make their values up -- record
numbers, free text and numbers too large or too small to hold -- draw no
random word at all: every one of their cells is fixed by published
counts, so the same cells come out at every seed. Those cells are
therefore built while the PLAN is settled, and carried on the plan. That
is what makes the question "can this column be built?" and the answer
"here is the column" the same walk rather than two that could disagree,
and it is what lets the refusal below land before any output file
exists.

EVERY WALK HERE ENDS, and the bound is stated at each one. A made-up
value is taken from a family of spellings whose size is worked out
before the walk begins; the walk visits each index of that family at
most once and stops at the end of it, and where it stops the caller
either refuses generation, in the words method G12 fixes, or -- on a
declared column of record numbers, where owner decision 6 governs --
lets values repeat and names what that cost.

PLACES WHERE THIS FILE DECIDES SOMETHING THE METHOD LEFT TO IT, each
stated so a reviewer can find it rather than discover it:

* A LADDER RUNG THAT HOLDS NOTHING -- SETTLED IN THE METHOD, no longer
  a decision this file takes. Revision 1 of method G5.1 said a null rung
  was a loader refusal, while the shipped loader accepts one (contract
  rule L3: a rung may be null, carrying no obligation at that rung), so
  a conforming description could arrive with one and this module had to
  choose a rule. Review item P2-C1-F8 wrote this module's rule into
  G5.1, where every implementation reads the same one: a null rung takes
  the nearest rung below it that holds a number, or the first rung that
  holds one where none below does; a ladder that is null at every rung
  leaves the column with no ladder at all and its values come from the
  sign counts, with a deviation named either way. `_filled_rungs` is
  where it is applied.
* HOW GROUPS ARE SHARED OUT AMONG PUBLISHED COUNTS. On the roles that
  publish a repetition pattern, one made-up spelling covers a whole
  group of rows, so a count that has to be met exactly -- how many cells
  read as a number, how many are written in figures alone -- has to be
  met by whole groups. The rule is in `_allotted`, which meets every
  count exactly wherever any packing of whole groups does, and every
  count that is missed anyway is recounted from the finished cells and
  named there.
* HOW FAR THE EXACT PACKING SEARCHES. Meeting several published cell
  counts at once with whole groups is a packing question, and packing
  questions have no known quick answer in general. Coupled families --
  the class and the alphabet of a piece of free text, the notation
  class, the whole-number status and the sign of a number too large to
  hold -- are decided in ONE walk over a grid carrying every one of
  their published counts as a margin, because deciding them one after
  the other throws away answers that exist. NO CEILING OF ANY KIND
  bounds that walk now: the two structural ones review item P2-C2-F1
  withdrew, and the work ceiling review item P2-C3-F1 found a producer
  description reaching, are all gone. The walk runs to its own end and
  the greedy packing behind it runs only where the walk has proved that
  no packing meets every count; the recount then names every count that
  was missed anyway.
* WHERE THE TWO GENERATION REFUSALS ARE WORDED. The refusal catalog is
  `errors.py`, and these two messages belong there. They are built here,
  in the catalog's own shape, because the catalog is being extended for
  the command in the same phase; moving them costs one call site.

Imports here stay within the allowlist (plan D6.2): `dataclasses`,
`math` (ldexp, frexp and isfinite -- two exact scalings by a power of
two and one question -- and sqrt, which the approximation bounds of
method G12.3 need and which this format requires to be correctly
rounded, so it gives the same answer on every machine), and this
package's own `contract`, `errors` and `parsing`.

THE ONE THIRD-PARTY IMPORT HERE is numpy, admitted by the scanner under
extensions E7 and E8 and written in exactly the form plan P2-D13
enumerates so that the enumeration can be checked against it line by
line: `import numpy.random`; one call to `numpy.random.default_rng`; one
call to `integers` on what that returns, in the one draw form of method
G3.2; and `int(...)` on each element, which is the only operation
performed on a library value and the point where its origin ends. Those
three lines are the whole of the surface, and
`tools/offline_scan/scan_imports.py` refuses any other numpy name, any
other method on the stream, and any attribute at all on what the draw
returns.

WHAT THIS MODULE DOES NOT BUILD (plan P2-D11, residual R-P2-3). Columns
are generated independently and the twin therefore carries no
cross-column structure at all -- no correlation, no formula between two
columns, no shared pattern of empty cells, no ordering between two event
columns. Rows are treated as independent and the grain is undescribed:
the description never says what one row of the real table is. The
relationship manifest a loaded description carries is eight reserved
slots, every one empty -- the loader refuses a description that fills
any of them -- and nothing here reads it, because there is nothing in it
to read. The report states both limits on every run. Cross-column
structure arrives in a later phase (Phase 5).
"""

import dataclasses
import math

import numpy.random

from synthtwin import contract, errors, parsing

# The one draw form of method G3.2, written out so the numbers are
# checkable against the specification: the whole of 0 .. 2**64 - 1,
# inclusive at both ends, and the scale that turns a word into the exact
# rational word / 2**64.
_WORD_CEILING = 18446744073709551615
_WORD_SCALE = 18446744073709551616

# The eleven ladder probabilities in hundredths, held as whole numbers
# for the reason the profiler holds them that way: 0.99 has no exact
# binary spelling and the nearest one moves a rung onto the wrong pair
# of neighbours in a large column (method G5.1).
_PCT = (0, 1, 5, 10, 25, 50, 75, 90, 95, 99, 100)

# The eleven rungs by name, in ladder order, which is the order `_PCT`
# is in. A ladder read out of a document is a MAPPING, so a walk over
# it needs the order written down; taking the mapping's own order would
# make the twin depend on how a document happened to be serialised.
_LADDER_NAMES = (
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

# What is said when a published clock value the loader already checked
# cannot be read back. No document a person can write reaches it.
_INTERNAL_CLOCK = (
    "synthtwin internal check: a clock time this description publishes "
    "could not be read back in the form the same description names. "
    "This means a mistake in synthtwin; please report it. Nothing has "
    "been written."
)

# The three alphabets of method G9.1. The ORDER is part of the
# specification, because it decides which spellings are produced first.
# `_CODE` is exactly the alphabet `parsing.is_code_text` accepts, in
# ASCII code-point order, which is what makes the code-alphabet count
# reproducible; `_DIGITS` is a subset of it, which is what makes an
# all-figures value count toward that same fact.
_DIGITS = tuple("0123456789")
# The letters of the code alphabet, written out here so that asking
# whether a spelling holds one is a MEMBERSHIP test against a
# first-party constant rather than a method call on a value the offline
# audit cannot trace (plan D6.2). A case flip needs a letter, which is
# what `_partner_of` asks before it chooses a parent.
_LETTERS = tuple(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
)

_CODE = tuple(
    "-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz"
)
_WIDE = tuple([chr(code) for code in range(32, 127)])

# The characters a WORD of made-up text is written from: the wide
# alphabet without the space, because the space is what separates one
# word from the next and a word holding one would be counted as two
# (method G9.5 step 6).
_WIDE_WORD = tuple([figure for figure in _WIDE if figure != " "])

# The characters a made-up value may not begin with. The first four are
# the ones common spreadsheet software reads as the start of a formula
# (plan P2-D10); the space is refused at both ends, so no made-up value
# can be changed by trimming or read as blank (method G9.1). A PUBLISHED
# label is a different matter and is written exactly as published,
# counted and warned about, never altered.
_FORMULA_LEADERS = ("=", "+", "-", "@")
_SPACE = " "

# The four classes every present cell of every role belongs to, in the
# order method G6.5 shares a distinctness budget out among them.
_CLASS_NUMBER = "number"
_CLASS_OUT_OF_RANGE = "out_of_range"
_CLASS_CONTRADICTORY = "contradictory"
_CLASS_TEXT = "text"
_CLASSES = (
    _CLASS_NUMBER,
    _CLASS_OUT_OF_RANGE,
    _CLASS_CONTRADICTORY,
    _CLASS_TEXT,
)

# The three alphabet bands a made-up value can sit in, and the counts
# that decide how many cells belong to each (method G9.5 step 3).
_BAND_DIGITS = "digits"
_BAND_CODE = "code"
_BAND_WIDE = "wide"
_BANDS = (_BAND_DIGITS, _BAND_CODE, _BAND_WIDE)

# WHICH TWO VALUES CARRY THE TWO PUBLISHED LENGTH ENDS. A column of
# record numbers gives them to its first two made-up values, which is
# the whole of method G9.2's pinning rule: its groups differ in nothing
# a length end could be traded for. A column of free text does not, and
# may not: which of its groups carries an end decides which published
# counts the grid of G9.5 can then meet, so that pairing is one of the
# things the allocation itself settles (review item P2-C4-F2).
_FIRST_TWO = (0, 1)

# The width every column of numbers too large or too small to hold is
# written at (method G10.5). The width is MADE UP: the description
# publishes none, two columns four hundred and four thousand characters
# wide publish identically, and the report says so in those words.
_CANONICAL_WIDTH = 400

# The three bands a stratum of a column of numbers sits in, in the fixed
# order of method G5.2, which is the sorted order of the column's own
# values.
_BAND_NEGATIVE = "negative"
_BAND_ZERO = "zero"
_BAND_POSITIVE = "positive"

# A deviation is filed under the description's OWN key -- `percentiles`,
# `numeric_styles`, `n_distinct` -- rather than under a name this module
# invents for it, so a reader can look the fact up in the contract and a
# test can name the fact it is checking without learning a second
# vocabulary. The complete list of deviations this method permits is
# method G12, and every one of them is built by a call to `_deviation`.


# -- what a run hands back --------------------------------------------
#
# Four frozen records, for the same reason the loader returns typed
# objects: a report that reads `outcome.n_distinct` on a column that has
# no such count should find out where it made the mistake, rather than
# carry a None three modules further.


@dataclasses.dataclass(frozen=True)
class Deviation:
    """One published fact the twin could not meet, measured and named.

    `fact` is the description's own key; `published` and `achieved` are
    that key's two values written out for a person to read; `note` is
    one plain sentence saying what the difference means for somebody
    developing code against the twin. `column` is the column's name
    exactly as the description spells it -- the report escapes it for
    display at its own boundary, because that is where a name reaches a
    screen.
    """

    column: str
    fact: str
    published: str
    achieved: str
    note: str


@dataclasses.dataclass(frozen=True)
class Approximation:
    """One APPROXIMATED fact, measured on the twin against its bound.

    A fact the contract calls APPROXIMATED is not free to come out
    anywhere: it owes a stated two-sided bound, and BOTH sides of that
    bound are checked against the twin's own finished cells (contract
    section 2.2, method G12.1). `fact` is the description's own key --
    `mean`, `percentiles.p25`, `length.p50` -- so a reader can look it
    up in the contract rather than learn a second vocabulary.

    `published` is what the description says, `achieved` is what the
    twin's cells hold, `lowest` and `highest` are the two ends of the
    bound method G12 fixes for that fact, and `inside` says whether the
    achieved value landed between them. The four values are carried as
    text because a date rung and a count are not both numbers, and
    because the report prints exactly these characters; `inside` carries
    the answer, so no consumer has to parse them back to learn it.

    `note` is one plain sentence saying what the fact is and what the
    bound is made of, in the words the report uses.

    `covers_published` SAYS WHETHER THE BOUND CONTAINS THE PUBLISHED
    VALUE AT ALL, and it is carried because a report that does not say
    so contradicts itself on the page (review of the shipped reports,
    2026-08-15). None of these bounds is a margin around the published
    value: each is worked out from the description and the size of the
    column, so a bound can lie wholly to one side of the value printed
    beside it. A column of 233 dates printed "the description says
    2023-11-23; the twin holds 2023-11-20 / allowed anywhere from
    2023-11-19 to 2023-11-21: inside the range" -- three true
    statements whose only possible joint reading, for a reader told
    that "inside the range" means the method kept its promise, is that
    the page is wrong somewhere. It is not: G12.4 bounds the twin's
    rung by the band its own RANK was built in, and the rank holding a
    named rung covers a slightly different share of the column from the
    share the rung's name names. The report now says so where it
    happens, and this field is the answer computed where the values are
    still numbers -- the four text fields are what the report prints
    and nothing is ever parsed back out of them.
    """

    column: str
    fact: str
    published: str
    achieved: str
    lowest: str
    highest: str
    inside: bool
    note: str
    covers_published: bool


@dataclasses.dataclass(frozen=True)
class ColumnOutcome:
    """What one column of the twin holds, recounted from its own cells.

    The four axis fields are carried through unchanged so the report can
    say which path a column took without asking the description again.
    The counts are RECOUNTED from the written cells rather than restated
    from the description: a check that cannot fail is a defect, and a
    count copied from the input would be exactly that.

    `approximations` is the same measurement for every fact the contract
    calls APPROXIMATED: each one's published value, the value this
    column's own cells hold, and the two ends of the bound it owes.
    """

    name: str
    position: int
    role: str
    statistical_type: str
    quality_state: str
    structural_role: str
    n_present: int
    n_missing: int
    n_distinct: int
    n_distinct_folded: int
    content_words: int
    placement_words: int
    deviations: "tuple[Deviation, ...]"
    approximations: "tuple[Approximation, ...]"


@dataclasses.dataclass(frozen=True)
class Twin:
    """A whole synthetic table, and the record of how well it matches.

    `names` is the header row and `write_header` says whether it is
    written at all, which follows `source.header_source` (plan P2-D10):
    the names came from the file, or they were made up by the profiler
    for a table that had none.

    `columns` is column-major and `rows` is row-major, and both are
    given on purpose. The writer walks rows; a check that recounts one
    column's published facts walks that column. They hold the same text
    objects, so carrying both costs one pointer per cell and saves every
    consumer a transpose.

    `deviations` and `approximations` are the two halves of the record
    of how well the twin matches, and they answer two different
    questions. A deviation is a published fact the twin could not MEET.
    An approximation is a published fact the twin was never obliged to
    meet exactly -- an average, an interior rung, a datetime's count of
    different values -- measured on the finished cells against the
    two-sided bound method G12 fixes for it. Both are measured, never
    predicted, and the report prints both.
    """

    names: "tuple[str, ...]"
    write_header: bool
    n_rows: int
    columns: "tuple[tuple[str, ...], ...]"
    rows: "tuple[tuple[str, ...], ...]"
    outcomes: "tuple[ColumnOutcome, ...]"
    deviations: "tuple[Deviation, ...]"
    approximations: "tuple[Approximation, ...]"
    words_drawn: int
    seed: int


@dataclasses.dataclass(frozen=True)
class _NumericLayout:
    """How the cells of a column of numbers divide (method G5.2, G6.5).

    `sizes` and `starts` are the strata in the fixed order negatives
    ascending, then the zero stratum, then positives ascending; `bands`
    says which of the three each stratum is in. The two budget tuples
    are the raw and folded spelling shares of the four classes, in the
    order of `_CLASSES`.
    """

    sizes: "tuple[int, ...]"
    starts: "tuple[int, ...]"
    bands: "tuple[str, ...]"
    raw_budgets: "tuple[int, ...]"
    folded_budgets: "tuple[int, ...]"


@dataclasses.dataclass(frozen=True)
class _ColumnPlan:
    """One column's whole generation plan, settled before any cell.

    Everything a decision depends on is decided here, before the first
    word of the run is drawn: how many words the column will consume,
    how its cells divide, whether the made-up domain can hold what the
    description asks for. That is what lets a shortfall be refused
    before any output file exists (method G9.4).

    `cells` CARRIES THE FINISHED VALUES for the three roles that make
    their values up -- record numbers, free text and numbers too large
    or too small to hold. Those roles draw no word at all: every one of
    their cells is fixed by published counts, so the values are the same
    for every seed and building them here is what makes the capacity
    question and the generation answer the SAME walk rather than two
    that could disagree (review item P2-C1-F2). For every other role it
    is empty and the cells are built from the run's own words.
    """

    column: contract.ColumnBlock
    content_words: int
    placement_words: int
    layout: "_NumericLayout | None"
    cells: "tuple[str, ...]"
    notes: "tuple[Deviation, ...]"
    # WHICH TWO GROUPS CARRY THE PUBLISHED LENGTH AND WORD ENDS. On a
    # column of free text the allocation settles this rather than
    # inheriting it (review item P2-C4-F2), and the two ends of every
    # approximated bound of G12.6 are statements about the walk that
    # filled the groups AROUND those two. So the answer is recorded here
    # rather than assumed again where the bounds are measured.
    carriers: "tuple[int, int]" = _FIRST_TWO
    # EVERY SPELLING ANY COLUMN OF THIS DOCUMENT CALLS ABSENT. A
    # declaration made on the command line reaches the WHOLE table, so
    # a spelling one column publishes among its absent cells means "no
    # value" in every column -- and the validator reads it that way
    # (review round 5 finding 3). A stand-in walk that knew only its
    # own column's holes wrote `group-1` into a second column while a
    # first published `group-1` as absent, and ten obligations missed
    # on a twin whose own report said nothing about it.
    all_holes: "tuple[str, ...]" = ()


@dataclasses.dataclass(frozen=True)
class GenerationPlan:
    """Every column's plan, and the whole run's word budget.

    Building one is the generation-feasibility stage of plan P2-D6: it
    runs after the loader and before any generation, it never calls a
    conforming description invalid, and it is where the four refusals of
    method G12 are raised -- so a refused run leaves the folder exactly
    as it found it.
    """

    columns: "tuple[_ColumnPlan, ...]"
    words_planned: int


# -- the one stream (method G3) ---------------------------------------


# WHY THE DRAW IS WRITTEN WHERE THE GENERATOR IS MADE, rather than in a
# helper taking it as a parameter (method G3.2, plan P2-D13 E8). The
# offline scanner establishes what a value IS from where it was built,
# and a parameter holds whatever a caller handed over: a helper reading
# `generator.integers(...)` would be calling a method on a value the
# audit cannot trace, which is the one thing that policy never accepts,
# and it would be right to refuse -- any object with an `integers`
# attribute would be called there. So the two draws of a column stand in
# `generate_twin`, in the same scope as `numpy.random.default_rng`, in
# exactly the one draw form the method fixes: the whole of
# 0 .. 2**64 - 1 inclusive at both ends, the type named by the text
# "uint64", no call at all for a stage whose count is zero, `size` given
# as a first-party whole number, and `int(...)` on each element straight
# away -- the one operation permitted on a library value and the point
# where its origin ends.


def _bounded(word: int, span: int) -> int:
    """One word into ``0 .. span - 1`` by the multiply-high rule (G3.4b).

    Chosen over a rejection loop for one reason that matters more than
    its bias: it consumes exactly one word every time, so the word count
    of a run is a fixed function of the published facts and can be
    stated in advance. The cost is stated rather than hidden: each
    outcome receives either floor or ceil of 2**64 / span of the words,
    so the largest departure from an even chance is below span / 2**64.
    """
    return (word * span) >> 64


def _arrangement(words: "list[int]", count: int) -> "list[int]":
    """An arrangement of ``0 .. count - 1`` (method G3.4c).

    Consumes exactly ``max(count - 1, 0)`` words. The loop runs
    downward, the drawn index includes the position itself, and the swap
    happens even when a position draws itself; all three are stated
    because all three change the bytes.
    """
    order = [place for place in range(count)]
    place = count - 1
    taken = 0
    while place >= 1:
        drawn = _bounded(words[taken], place + 1)
        taken = taken + 1
        keep = order[place]
        order[place] = order[drawn]
        order[drawn] = keep
        place = place - 1
    return order


# -- small shared helpers ---------------------------------------------


def _wrong_facts(name: str) -> "errors.ProfileError":
    """The internal check for a column whose facts do not fit its axes."""
    return errors.ProfileError(
        f"synthtwin internal check: the description of the column "
        f"'{parsing.visible(name)}' does not carry the facts its own kind "
        f"of column needs. Both are checked when the description is "
        f"read, so this means a mistake in synthtwin; please report it."
    )


def _deviation(
    column: str, fact: str, published: str, achieved: str, note: str
) -> Deviation:
    """One measured difference between the description and the twin."""
    return Deviation(
        column=column,
        fact=fact,
        published=published,
        achieved=achieved,
        note=note,
    )


def _flipped_case(character: str) -> str:
    """``character`` with its case turned over, or unchanged.

    A character is only turned over when both cases are single
    characters and the two agree once folded; anything else -- a letter
    whose upper case is two characters, a character with no case at all
    -- is left alone, so that a spelling built from these still folds
    onto the label it belongs to.
    """
    if not isinstance(character, str):
        raise TypeError("a character reached the case rule as something else")
    upper = character.upper()
    lower = character.lower()
    if len(upper) != 1 or len(lower) != 1 or upper == lower:
        return character
    if parsing.folded(upper) != parsing.folded(lower):
        return character
    if character == lower:
        return upper
    return lower


def _has_case(character: str) -> bool:
    """True when `_flipped_case` would change this character."""
    return _flipped_case(character) != character


def _case_variant(spelling: str, order: int) -> "str | None":
    """The ``order``-th case variant of ``spelling`` (method G8.2, G9.3).

    Write ``order`` in binary and turn over the case of the alphabetic
    position named by every set bit, with bit zero the LEFTMOST such
    position. A spelling with L such positions supplies 2**L - 1
    variants; None says this one has run out.
    """
    places = [place for place in range(len(spelling))
              if _has_case(spelling[place])]
    if not places or order < 1 or order >= (1 << len(places)):
        return None
    built = ""
    turned = {}
    for index in range(len(places)):
        if (order >> index) & 1:
            turned[places[index]] = 1
    for place in range(len(spelling)):
        if place in turned:
            built = f"{built}{_flipped_case(spelling[place])}"
        else:
            built = f"{built}{spelling[place]}"
    return built


def _budget_split(total: int, counts: "tuple[int, ...]") -> "tuple[int, ...]":
    """Share a distinctness budget out among the classes (method G6.5).

    Every non-empty class receives one spelling, then the remainder is
    offered to the classes in the fixed order of `_CLASSES`, each taking
    as much as it can use and never more than its own cell count, until
    the remainder is spent.
    """
    shares = [0 for _each in counts]
    filled = [place for place in range(len(counts)) if counts[place] > 0]
    if not filled or total < 1:
        return tuple(shares)
    for place in filled:
        shares[place] = 1
    remainder = total - len(filled)
    for place in filled:
        if remainder < 1:
            break
        take = min(remainder, counts[place] - 1)
        shares[place] = shares[place] + take
        remainder = remainder - take
    return tuple(shares)


# WHERE A COUNT OF SPELLINGS STOPS BEING WORTH COUNTING. A made-up
# family is often astronomically large -- ten to the four thousandth
# power for a column recording a four-thousand-character value -- and no
# question this module asks needs the exact number. Every count of a
# domain therefore stops here, which is far above any row count a table
# can hold, so the comparisons that matter are exact and the arithmetic
# costs a few dozen multiplications instead of thousands.
_DOMAIN_CEILING = 1 << 62


def _power_at_most(base: int, exponent: int, ceiling: int) -> int:
    """``base ** exponent``, stopped as soon as it reaches ``ceiling``.

    The saturating rule of method G9.4: the running product stops
    growing once the answer can no longer change the comparison the
    caller is making, so a column recording a four-thousand-character
    maximum costs no more than one recording ten.
    """
    running = 1
    for _step in range(exponent):
        if running >= ceiling:
            return running
        running = running * base
    return running


def _lettered_domain_size(
    alphabet: "tuple[str, ...]", shortest: int, longest: int, wanted: int
) -> int:
    """How many spellings hold at least one letter, saturated (G9.3).

    A fold collision built by a CASE FLIP needs a value with a case to
    flip, and this counts the values that have one. It is one of the two
    halves of the collision sub-domain; `_padded_room` counts the other,
    which needs no letter. The count for one length is the whole count less
    the count of spellings that hold no letter, and it is computed
    exactly: where the lower bound `letters * size ** (length - 1)`
    already reaches ``wanted`` the answer is settled without the
    subtraction, and where it does not, both powers are below
    ``wanted * size`` and cost nothing to work out.
    """
    letters = len([place for place in alphabet if _has_case(place)])
    if letters < 1:
        return 0
    size = len(alphabet)
    total = 0
    for length in range(shortest, longest + 1):
        if total >= wanted:
            return total
        smaller = _power_at_most(size, length - 1, wanted)
        if letters * smaller >= wanted:
            return wanted
        total = total + size ** length - (size - letters) ** length
    return total


def _spelling_at(
    alphabet: "tuple[str, ...]",
    length: int,
    index: int,
    head: "tuple[str, ...] | None" = None,
) -> str:
    """The ``index``-th spelling of one alphabet at one length (G9.2).

    Plain base-``len(alphabet)`` counting with the first character of
    the alphabet as the zero figure and the leftmost character most
    significant, followed by the positional rules: neither end is ever a
    space and the first character is never one a spreadsheet reads as
    the start of a formula. Where a positional rule refuses a character,
    the first character of the same alphabet that meets it stands in its
    place, in the alphabet's own order.

    ``head`` is the leftmost character's own permitted set, already in
    the alphabet's order, and it carries the band rule of method G9.5
    step 3 as one more positional rule: a value the description counts
    in the code alphabet but not among the all-figures values leads with
    a character that is not a figure, so it cannot read as figures
    alone.
    """
    return _fixed_ends(_raw_spelling(alphabet, length, index), alphabet, head)


def _raw_spelling(
    alphabet: "tuple[str, ...]", length: int, index: int
) -> str:
    """Plain base-``len(alphabet)`` counting, before the positional rules."""
    size = len(alphabet)
    figures: list[str] = []
    rest = index
    for _step in range(length):
        figures = [alphabet[rest % size]] + figures
        rest = rest // size
    built = ""
    for figure in figures:
        built = f"{built}{figure}"
    return built


def _fixed_ends(
    spelling: str,
    alphabet: "tuple[str, ...]",
    head: "tuple[str, ...] | None" = None,
) -> str:
    """The positional rules of method G9.1, applied to a whole value.

    Neither end is ever a space, so no made-up value can be changed by
    trimming or read as blank, and the first character is never one that
    common spreadsheet software reads as the start of a formula. Where a
    rule refuses a character, the first character of the same alphabet
    that meets it stands in its place, in the alphabet's own order.

    ``head``, where a caller gives one, is the whole permitted set for
    the leftmost character and already excludes the space and the
    formula leaders, so it replaces the general rule rather than being
    checked beside it.
    """
    if not spelling:
        return spelling
    built = spelling
    first = built[0]
    if head is not None:
        if first not in head:
            built = f"{head[0]}{built[1:]}"
    elif first == _SPACE or first in _FORMULA_LEADERS:
        built = f"{_first_meeting(alphabet, True)}{built[1:]}"
    if len(built) > 1 and built[len(built) - 1] == _SPACE:
        built = f"{built[:len(built) - 1]}{_first_meeting(alphabet, False)}"
    return built


def _first_meeting(alphabet: "tuple[str, ...]", first: bool) -> str:
    """The first character of ``alphabet`` the positional rules allow."""
    for figure in alphabet:
        if figure == _SPACE:
            continue
        if first and figure in _FORMULA_LEADERS:
            continue
        return figure
    return alphabet[0]


# -- the exact packing (method G9.5 step 3, review item P2-C2-F1) ------
#
# WHY THIS SEARCH NO LONGER STOPS EARLY. Sharing whole groups out so that
# several published cell counts are all met exactly is a packing
# question. An earlier revision bounded the search with two constants --
# a state budget and a call-chain depth -- and handed the rest to a
# greedy packing. Review item P2-C2-F1 showed a description the PRODUCER
# emits reaching the depth constant: a declared column of record numbers
# publishing 132 different group sizes made the depth expression 402
# against a ceiling of 400, so an exact packing that the real column's
# own values prove exists was never looked for, and three published
# counts came out wrong. A ceiling a genuine description reaches is not
# a bound on the answer, it is a loss of one.
#
# So there is no ceiling here now. The search below is COMPLETE: it
# returns a packing meeting every published count exactly whenever any
# packing of whole groups does, for every description the loader
# accepts. What replaces the constants is the pruning of `_reach_bits`:
# before the walk descends past one group size it asks, in one whole-
# number test, whether the sizes it has not yet decided can still reach
# a total this bucket accepts. Every branch it enters can therefore
# finish the bucket it is filling, so the walk never explores a
# dead-ended fill of one bucket at all.
#
# WHY IT ENDS, stated rather than assumed. Every state the walk can
# stand in is a triple of (which cell is being filled, how many groups
# of each size are still unplaced, how much of each published count is
# still owed). A state that turns out to have no answer is written down
# and never entered twice, and the number of different states is at most
# `cells * product over sizes of (copies of that size + 1)` -- a finite
# number fixed by the description before the walk starts. So the walk
# stops on every input. Its worst case is exponential in the number of
# DIFFERENT group sizes, which is inherent rather than a choice of this
# file: deciding whether whole groups can meet several exact totals is
# the classic partition question and has no known quick answer. What
# makes it cheap in practice is that a genuine description always HAS an
# answer -- the real column's own values are one, since each real value
# covered a whole group of rows and belonged to one class, one alphabet
# and one sign -- and the first fill the ordered walk tries is usually
# that answer.
#
# THE FALLBACK BELOW IS THEREFORE UNREACHABLE FROM A PRODUCER
# DESCRIPTION. `_share_out` runs only where NO packing of whole groups
# meets every count, which cannot happen for a description a real table
# produced, because that table's own values are such a packing. It stays
# because a contract-valid document need not have come from a table, and
# because the generator's own choice of length can leave a group unable
# to stand in the class the real value stood in; every count it misses
# is measured from the finished cells and named there.
#
# NO CEILING ON WORK REMAINS EITHER, AND THE ONE THAT DID IS WITHDRAWN
# (review item P2-C3-F1). It stopped the walk after a stated number of
# trips and handed the answer to the greedy packing below, on the
# recorded belief that no description a producer emits could reach it.
# A producer description reached it: a 2,710-row column of numbers too
# large to hold, with 38 groups, class counts 592, 879 and 1,239 and
# sign counts 1,578, 540 and 592, used more than five million trips
# before the walk it stopped would have answered. A ceiling a genuine
# description reaches is not a bound on cost, it is a published count
# traded away, and neither this file nor either specification may trade
# one. So the walk now runs to its own end on every description the
# loader accepts, and the greedy packing runs only where the walk has
# PROVED that no packing of whole groups meets every count.
#
# WHAT THAT COSTS, SAID PLAINLY. The packing question has no known quick
# answer, so a contract-valid document nobody produced could take a long
# time here. That cost is accepted for the same reason plan P2-D2
# accepts a description too large for the machine failing on the
# memory-exhaustion path rather than being refused by a cap: a bound
# that keeps the run short by writing a number the description did not
# publish is the worse of the two. What keeps genuine descriptions quick
# is stated above -- their own values are an answer, and the walk is
# handed only the relationships the description actually publishes, so
# it is never asked to solve a harder question than the real column
# already answered.


def _spread(mask: int, rows: int, width: int) -> int:
    """One bucket permission set written over a grid of cells.

    A single-axis packing is the two-axis one with a grid one cell wide,
    so bit ``b`` of a bucket mask becomes bit ``b * width`` of a cell
    mask. Written out once so the two callers cannot drift.
    """
    built = 0
    for row in range(rows):
        if (mask >> row) & 1:
            for column in range(width):
                built = built | (1 << (row * width + column))
    return built


def _allotted(
    groups: "tuple[int, ...]",
    quotas: "list[int]",
    allowed: "list[int]",
) -> "list[int] | None":
    """Give every group to one bucket so that EVERY quota is met exactly.

    One made-up spelling covers a whole group of rows, so a published
    count of CELLS has to be met by whole GROUPS. This finds a packing
    that meets every count exactly whenever any packing of whole groups
    does, and returns None only where none does at all.

    ``allowed[i]`` is the set of buckets group ``i`` may take, written as
    a whole number whose bit ``b`` is set when bucket ``b`` is permitted.
    That is what carries the rules one published fact places on another
    -- a cell whose notation contradicts itself is written in
    parentheses, so it can never be counted among the cells written in
    figures alone.

    THE ORDER IS PART OF THE RULE, so two implementations pack the same
    way. Buckets are filled in ascending order of their own published
    counts, ties by the description's own order, so the count that
    absorbs whatever is left over is filled last. Within a bucket the
    different group SIZES are offered in ascending order, and each size
    offers as many copies as the bucket can still hold, falling back to
    fewer. A packing that leaves a later bucket unable to finish is
    undone and the next one is tried. Groups are then handed to their
    buckets in the description's own group order, so the first bucket
    takes the earliest groups -- which is what makes a column of
    all-different values, whose groups are all of size one, pack exactly
    as it reads.
    """
    total = 0
    for quota in quotas:
        total = total + quota
    return _allotted_pairs(
        groups,
        quotas,
        [total],
        [_spread(mask, len(quotas), 1) for mask in allowed],
    )


def _allotted_pairs(
    groups: "tuple[int, ...]",
    rows: "list[int]",
    columns: "list[int]",
    allowed: "list[int]",
) -> "list[int] | None":
    """Give every group to one CELL of a grid, meeting both margins exactly.

    Two published counts are often coupled: a column of free text
    publishes how many cells read as a number AND how many are written
    in figures alone, and one group answers for one of each at the same
    time. Deciding the two in separate walks throws away joint answers
    that exist -- review item P2-C2-F1 built a five-row column with an
    exact joint class-and-alphabet answer that two separate walks did
    not reach -- so both are decided here in ONE walk over a grid whose
    rows are the first family of counts and whose columns are the
    second.

    ``allowed[i]`` names the cells group ``i`` may take, bit
    ``row * len(columns) + column``. The answer is one cell index per
    group, in group order, or None where no assignment of whole groups
    meets every count of both margins.

    THE ORDER IS THE SAME RULE the single-axis packing states, read over
    the grid: the margins are taken in ascending order of their own
    published counts, ties by the description's own order; cells are
    filled row-major within that order; inside a cell the different
    group SIZES are offered in ascending order and each offers as many
    copies as the cell can still hold, falling back to fewer; and groups
    are handed to their cells in group order. A grid one cell wide is
    exactly the single-axis rule, which is why `_allotted` is written as
    a call to this.

    Two margins is the common case and not the rule: `_allotted_over`
    takes as many as the description publishes, and this is the two-
    margin reading of it.
    """
    width = len(columns)
    cells = len(rows) * width
    return _allotted_over(
        groups,
        [
            (rows, [cell // width for cell in range(cells)]),
            (
                columns,
                [cell - (cell // width) * width for cell in range(cells)],
            ),
        ],
        allowed,
    )


def _allotted_over(
    groups: "tuple[int, ...]",
    margins: "list[tuple[list[int], list[int]]]",
    allowed: "list[int]",
) -> "list[int] | None":
    """Give every group to one cell, meeting EVERY margin exactly.

    THE GRID CARRIES THE DESCRIPTION'S OWN COUNTS AND NOTHING ELSE
    (review item P2-C3-F1). A margin is a family of published counts
    that divides the cells between them: ``(quotas, part_of)``, where
    ``part_of[cell]`` says which count of that family the cell answers
    for. A column of numbers too large to hold publishes THREE such
    families over one set of cells -- what the notation classifies as,
    whether the value is a whole number, and what sign it settles -- and
    publishes no cross-tabulation of them at all. Packing over two
    margins invented from them, rather than over the three the
    description carries, is how an earlier revision asked the walk to
    solve a question the real column never answered and then reported
    six exact counts as missed.

    ``allowed[i]`` names the cells group ``i`` may take. The answer is
    one cell index per group, in group order, or None where no
    assignment of whole groups meets every count of every margin.

    THE ORDER IS PART OF THE RULE, so two implementations pack the same
    way. Inside each margin the counts are ranked in ascending order of
    their own published values, ties by the description's own order, so
    the count that absorbs whatever is left over is answered for last.
    Cells are then filled in ascending order of the ranks they carry,
    margin by margin, ties by the cell's own number -- which for two
    margins is exactly the row-major order over ranked rows and columns
    that `_allotted_pairs` states. Within a cell the different group
    SIZES are offered in ascending order and each offers as many copies
    as the cell can still hold, falling back to fewer; a fill that
    leaves a later cell unable to finish is undone and the next is
    tried; and groups are handed to their cells in group order.
    """
    counted = 0
    for size in groups:
        counted = counted + size
    for margin in margins:
        total = 0
        for quota in margin[0]:
            total = total + quota
        if total != counted:
            return None
    cells = len(margins[0][1])
    # THE SMALLEST COUNT IS ANSWERED FOR FIRST, and the largest last.
    # The order is fixed by the published values themselves, ascending,
    # ties by the contract's own order, so it is a function of the
    # description and of nothing else. It is chosen rather than inherited
    # for a reason a ceiling used to hide: the largest count is the one
    # that absorbs whatever is left over, so filling it first spends the
    # small group sizes on it and leaves the small counts to be made out
    # of the large sizes, which is the shape a packing walk can spend an
    # unbounded amount of time undoing. Answering the small counts first
    # is what keeps a genuine description answered at once now that no
    # ceiling stops the walk (review items P2-C2-F1 and P2-C3-F1).
    order = _cell_order(margins, cells)
    ranked = [-1 for _each in range(cells)]
    for step in range(cells):
        ranked[order[step]] = step
    part_at = [
        [margin[1][order[step]] for step in range(cells)]
        for margin in margins
    ]
    last_of = [_last_cells(places, cells) for places in part_at]
    masks = [
        _ranked_mask(allowed[place], ranked) for place in range(len(groups))
    ]
    keys = sorted({
        (groups[place], masks[place]) for place in range(len(groups))
    })
    place_of = {keys[index]: index for index in range(len(keys))}
    counts = [0 for _each in keys]
    for place in range(len(groups)):
        counts[place_of[(groups[place], masks[place])]] = (
            counts[place_of[(groups[place], masks[place])]] + 1
        )
    taken = _cell_walk(
        keys,
        counts,
        [[quota for quota in margin[0]] for margin in margins],
        part_at,
        last_of,
    )
    if taken is None:
        return None
    chosen = [-1 for _each in groups]
    for cell in range(cells):
        for place in range(len(groups)):
            if chosen[place] >= 0:
                continue
            found = place_of[(groups[place], masks[place])]
            if taken[cell][found] < 1:
                continue
            chosen[place] = order[cell]
            taken[cell][found] = taken[cell][found] - 1
    for cell in chosen:
        if cell < 0:
            return None
    return chosen


def _cell_order(
    margins: "list[tuple[list[int], list[int]]]", cells: int
) -> "list[int]":
    """The order the cells are filled in, as cell numbers.

    Each margin ranks its own counts ascending, ties by the order the
    description states them in; a cell then carries one rank per margin,
    and the cells are filled in ascending order of those ranks read left
    to right, ties by the cell's own number. Over two margins this is
    the row-major order over ranked rows and ranked columns exactly.
    """
    ranks: list[list[int]] = []
    for margin in margins:
        quotas = margin[0]
        placed = [
            pair[1]
            for pair in sorted(
                [(quotas[place], place) for place in range(len(quotas))]
            )
        ]
        rank = [0 for _each in quotas]
        for step in range(len(placed)):
            rank[placed[step]] = step
        ranks = ranks + [rank]
    keyed = sorted([
        (
            tuple(
                ranks[place][margins[place][1][cell]]
                for place in range(len(margins))
            ),
            cell,
        )
        for cell in range(cells)
    ])
    return [pair[1] for pair in keyed]


def _last_cells(places: "list[int]", cells: int) -> "list[bool]":
    """Which cells are the last of their own count, in the fill order.

    A count has nothing after that cell to answer for it, so the cell
    takes exactly what the count still owes rather than choosing.
    """
    seen: dict[int, int] = {}
    flags = [False for _each in range(cells)]
    for step in range(cells - 1, -1, -1):
        if places[step] not in seen:
            flags[step] = True
            seen[places[step]] = 1
    return flags


def _ranked_mask(mask: int, ranked: "list[int]") -> int:
    """One permission set written over the cells in the order they fill."""
    built = 0
    for cell in range(len(ranked)):
        if (mask >> cell) & 1:
            built = built | (1 << ranked[cell])
    return built


def _cell_room(
    owed: "list[list[int]]",
    part_at: "list[list[int]]",
    last_of: "list[list[bool]]",
    cell: int,
) -> "tuple[int, int]":
    """The smallest and largest total one cell of the grid may hold.

    A cell may never hold more than what ANY of the counts it answers
    for still owes. It holds EXACTLY what one of them still owes when it
    is that count's last cell, because nothing after it can answer for
    that count. Where those demands cross, the pair returned has its
    ends the wrong way round and the caller reads that as "no fill".
    """
    lowest = 0
    highest = -1
    for margin in range(len(owed)):
        left = owed[margin][part_at[margin][cell]]
        if last_of[margin][cell] and left > lowest:
            lowest = left
        if highest < 0 or left < highest:
            highest = left
    return lowest, highest


def _reach_bits(
    keys: "list[tuple[int, int]]",
    left: "list[int]",
    cell: int,
    ceiling: int,
) -> "list[int]":
    """Which totals the sizes from each place onward can still make.

    Entry ``k`` is a whole number whose bit ``t`` is set when the group
    sizes at places ``k`` and after, in the copies still unplaced, can be
    chosen to total exactly ``t``. It is built from the last place
    backward, one size at a time, by the halving rule -- one copy, then
    two, then four, then what is left -- so a size with a thousand
    copies costs ten shifts rather than a thousand. Bits above
    ``ceiling`` are dropped, because no fill of this cell may reach
    them.

    This is what makes the walk of `_cell_walk` enter only branches that
    can finish the cell they are filling, which is what let the state
    and depth ceilings of the earlier revision be removed (review item
    P2-C2-F1).
    """
    total = len(keys)
    limit = (1 << (ceiling + 1)) - 1
    bits = [0 for _each in range(total + 1)]
    bits[total] = 1
    for place in range(total - 1, -1, -1):
        reach = bits[place + 1]
        if (keys[place][1] >> cell) & 1:
            copies = left[place]
            step = 1
            while copies > 0:
                take = min(step, copies)
                reach = (reach | (reach << (take * keys[place][0]))) & limit
                copies = copies - take
                step = step * 2
        bits[place] = reach
    return bits


def _reach_any(
    keys: "list[tuple[int, int]]",
    left: "list[int]",
    cells: int,
    target: int,
) -> bool:
    """Whether the groups allowed in ANY of ``cells`` can total ``target``.

    The same halving walk as `_reach_bits`, over the union of a set of
    cells rather than one cell, and answering one question instead of
    building a table.
    """
    if target < 1:
        return True
    limit = (1 << (target + 1)) - 1
    reach = 1
    for place in range(len(keys)):
        if keys[place][1] & cells == 0:
            continue
        copies = left[place]
        step = 1
        while copies > 0:
            take = min(step, copies)
            reach = (reach | (reach << (take * keys[place][0]))) & limit
            copies = copies - take
            step = step * 2
        if (reach >> target) & 1:
            return True
    return (reach >> target) & 1 == 1


def _margins_left(
    keys: "list[tuple[int, int]]",
    left: "list[int]",
    owed: "list[list[int]]",
    part_at: "list[list[int]]",
    cell: int,
    cells: int,
) -> bool:
    """Whether every count still owed can be made from what is unplaced.

    A NECESSARY CONDITION, checked once per state rather than discovered
    at the bottom of a walk. Every count of every margin that still owes
    something must be able to total exactly that from the group sizes
    still unplaced that its own remaining cells permit. It says nothing
    about whether the margins can be satisfied TOGETHER -- that is the
    question the walk itself answers -- but it cuts the branch where one
    of them cannot be satisfied at all, which is where a walk with no
    ceiling would otherwise spend an unbounded amount of time (review
    items P2-C2-F1 and P2-C3-F1).
    """
    for margin in range(len(owed)):
        for part in range(len(owed[margin])):
            if owed[margin][part] < 1:
                continue
            reachable = 0
            for step in range(cell, cells):
                if part_at[margin][step] == part:
                    reachable = reachable | (1 << step)
            if not _reach_any(keys, left, reachable, owed[margin][part]):
                return False
    return True


def _within(bits: int, lowest: int, highest: int) -> bool:
    """True when some total between the two ends is still reachable."""
    if highest < 0:
        return False
    low = max(lowest, 0)
    if low > highest:
        return False
    return bits & (((1 << (highest - low + 1)) - 1) << low) != 0


def _cell_next(
    keys: "list[tuple[int, int]]",
    left: "list[int]",
    state: "list[int]",
    reach: "list[int]",
    room: "tuple[int, int]",
    cell: int,
) -> "tuple[list[int], list[int] | None]":
    """The next fill of one cell in the fixed order, and the walk after it.

    ``state`` is how many groups of each size this cell is taking, as far
    as the walk has decided. An empty ``state`` asks for the first fill;
    a complete one asks for the fill after it, which is what lets the
    caller resume this cell after a later one failed. Sizes are decided
    in ascending order and each offers as many copies as the cell can
    still hold, falling back to fewer -- the order method G9.5 fixes.

    Returns the walk to hand back on the next call and the fill, or None
    for the fill where this cell's walk is spent.

    Every branch entered can still reach a total the cell accepts,
    because `reach` is consulted before descending, so a complete state
    is always a fill and no fill is ever visited twice.
    """
    total = len(keys)
    lowest, highest = room
    walk = [number for number in state]
    if total == 0:
        if walk or not (lowest <= 0 <= highest):
            return walk, None
        return walk, []
    used = 0
    for place in range(len(walk)):
        used = used + walk[place] * keys[place][0]
    if len(walk) == total:
        while walk and walk[len(walk) - 1] == 0:
            walk = walk[:len(walk) - 1]
        if not walk:
            return walk, None
        place = len(walk) - 1
        walk[place] = walk[place] - 1
        used = used - keys[place][0]
    while True:
        place = len(walk) - 1
        if place >= 0 and walk[place] < 0:
            used = used + keys[place][0]
            walk = walk[:place]
            if not walk:
                return walk, None
            walk[place - 1] = walk[place - 1] - 1
            used = used - keys[place - 1][0]
            continue
        if place >= 0 and not _within(
            reach[place + 1], lowest - used, highest - used
        ):
            walk[place] = walk[place] - 1
            used = used - keys[place][0]
            continue
        if len(walk) == total:
            return walk, [number for number in walk]
        ahead = len(walk)
        most = 0
        if (keys[ahead][1] >> cell) & 1:
            most = min(left[ahead], (highest - used) // keys[ahead][0])
        walk = walk + [most]
        used = used + most * keys[ahead][0]


def _moved_by(
    fill: "list[int]",
    keys: "list[tuple[int, int]]",
    left: "list[int]",
    owed: "list[list[int]]",
    part_at: "list[list[int]]",
    cell: int,
    way: int,
) -> None:
    """Apply one cell's fill to the running tallies, or take it back.

    ``way`` is -1 to place the fill and 1 to undo it, which is what lets
    the walk of `_cell_walk` step back over a cell it has already tried.
    """
    moved = 0
    for place in range(len(fill)):
        left[place] = left[place] + way * fill[place]
        moved = moved + fill[place] * keys[place][0]
    for margin in range(len(owed)):
        owed[margin][part_at[margin][cell]] = (
            owed[margin][part_at[margin][cell]] + way * moved
        )


def _cell_walk(
    keys: "list[tuple[int, int]]",
    counts: "list[int]",
    owed: "list[list[int]]",
    part_at: "list[list[int]]",
    last_of: "list[list[bool]]",
) -> "list[list[int]] | None":
    """Fill every cell of the grid exactly, or say no filling does.

    Written as a loop over an explicit list of walks rather than as
    nested calls, so that a description publishing many different group
    sizes cannot grow a call chain without end -- which is the shape the
    removed depth ceiling was guarding against, now handled rather than
    refused (review item P2-C2-F1).

    A cell whose walk is spent is written down as having no answer under
    the state it was entered in -- which sizes were still unplaced and
    what every count of every margin still owed -- so the same state is
    never explored twice, and the number of different states is finite
    and fixed by the description before the walk begins. That is the
    whole termination argument, and it is the only thing that ends this
    walk now: NOTHING counts trips and stops (review item P2-C3-F1).
    """
    cells = len(part_at[0])
    left = [count for count in counts]
    walks: list[list[int]] = []
    reaches: list[list[int]] = []
    rooms: list[tuple[int, int]] = []
    placed: list[list[int]] = []
    marks: list[tuple[int, tuple[int, ...], tuple[tuple[int, ...], ...]]]
    marks = []
    failed: dict[
        tuple[int, tuple[int, ...], tuple[tuple[int, ...], ...]], int
    ] = {}
    cell = 0
    while True:
        if cell == cells:
            return placed
        if len(walks) == cell:
            mark = (
                cell,
                tuple(left),
                tuple(tuple(margin) for margin in owed),
            )
            room = _cell_room(owed, part_at, last_of, cell)
            if mark in failed or room[0] > room[1] or not _margins_left(
                keys, left, owed, part_at, cell, cells
            ):
                failed[mark] = 1
                cell = cell - 1
                if cell < 0:
                    return None
                continue
            marks = marks + [mark]
            rooms = rooms + [room]
            reaches = reaches + [_reach_bits(keys, left, cell, room[1])]
            walks = walks + [[]]
            placed = placed + [[]]
        else:
            _moved_by(
                placed[cell], keys, left, owed, part_at, cell, 1,
            )
        walk, found = _cell_next(
            keys, left, walks[cell], reaches[cell], rooms[cell], cell
        )
        walks[cell] = walk
        if found is None:
            failed[marks[cell]] = 1
            walks = walks[:cell]
            reaches = reaches[:cell]
            rooms = rooms[:cell]
            placed = placed[:cell]
            marks = marks[:cell]
            cell = cell - 1
            if cell < 0:
                return None
            continue
        _moved_by(found, keys, left, owed, part_at, cell, -1)
        placed[cell] = found
        cell = cell + 1


def _share_out(
    groups: "tuple[int, ...]", quotas: "list[int]", allowed: "list[int]"
) -> "tuple[list[int], list[int]]":
    """Give every group to one bucket, meeting cell quotas where it can.

    THE FALLBACK PACKING, used only where NO packing of whole groups
    meets every count -- which a description a real table produced never
    reaches, because that table's own values are such a packing. One
    made-up spelling covers a whole group of rows, so a published count
    of CELLS has to be met by whole GROUPS.
    Groups are offered largest first, ties by their own order, and each
    goes to the first bucket it is allowed to take whose remaining quota
    can still hold it; a group no bucket can hold goes to the allowed
    bucket with the most room left.

    Returns the bucket of every group, in group order, and how far each
    bucket fell short or ran over, so the caller can name it.
    """
    ranked = sorted([(-groups[place], place) for place in range(len(groups))])
    order = [pair[1] for pair in ranked]
    left = [quota for quota in quotas]
    chosen = [0 for _each in groups]
    for place in order:
        picked = -1
        for bucket in range(len(left)):
            if (allowed[place] >> bucket) & 1 == 0:
                continue
            if left[bucket] >= groups[place] and left[bucket] > 0:
                picked = bucket
                break
        if picked < 0:
            for bucket in range(len(left)):
                if (allowed[place] >> bucket) & 1 == 0:
                    continue
                if picked < 0 or left[bucket] > left[picked]:
                    picked = bucket
        picked = max(picked, 0)
        chosen[place] = picked
        left[picked] = left[picked] - groups[place]
    return chosen, left


def _every_bucket(count: int) -> int:
    """The permission set naming all ``count`` buckets."""
    return (1 << count) - 1


def _allocation(
    groups: "tuple[int, ...]",
    quotas: "list[int]",
    allowed: "list[int]",
) -> "list[int]":
    """Pack the groups exactly if any packing does; fall back if none does.

    The exact packing is tried first, and it is COMPLETE: it finds one
    whenever any packing of whole groups meets every count (review item
    P2-C2-F1). A genuine description always has one -- the real column's
    own values are a packing, since each real value covered a whole
    group of rows and belonged to one class and one alphabet -- so the
    greedy packing below runs only on a document no real table produced.

    NOTHING IS NAMED HERE, and that is deliberate. Every count these
    packings answer for is recounted from the FINISHED cells in
    `generate` and named there, against the description's own key. A
    shortfall this packing predicted and a shortfall it did not are then
    named the same way, by the same measurement, which is what stops a
    miss no rule foresaw from going out in silence (review item
    P2-C1-F1).
    """
    exact = _allotted(groups, quotas, allowed)
    if exact is not None:
        return exact
    chosen, _left = _share_out(groups, quotas, allowed)
    return chosen


def _joint_allocation(
    groups: "tuple[int, ...]",
    rows: "list[int]",
    columns: "list[int]",
    allowed: "list[int]",
) -> "list[int] | None":
    """Meet two coupled families of counts in ONE packing, or say none does.

    Returns one cell index per group -- `row * len(columns) + column` --
    or None where no assignment of whole groups meets both margins
    exactly. The caller then decides the two families one after the
    other, which is what the earlier revision did for every description
    and what review item P2-C2-F1 showed throwing away joint answers
    that exist.
    """
    return _allotted_pairs(groups, rows, columns, allowed)


def _groups_of(pattern: "dict[str, int]") -> "tuple[int, ...]":
    """The repetition pattern as one group size per made-up value.

    For each key in ascending order -- the keys are row counts written
    in figures and padded to a common width, so plain sorting IS
    ascending order -- and for each of that key's distinct values, one
    group of that many rows (method G9.5 step 2).
    """
    sizes: list[int] = []
    for key in sorted(pattern):
        rows = int(key)
        sizes = sizes + [rows for _each in range(pattern[key])]
    return tuple(sizes)


def _recounted(
    cells: "list[str]", holes: "tuple[str, ...]"
) -> "tuple[int, int, int, int]":
    """Recount a written column: present, absent, different, folded.

    COUNTED THE WAY THE TWIN'S OWN DESCRIPTION WILL COUNT IT (review
    item P4-DATE-F2). A cell is present when it holds something the
    description does not read as absent -- not merely when it is not
    empty. A run that wrote a cell wearing a spelling the column
    publishes among its absent ones has written a cell its own reader
    will not count, and a recount that called it present would report
    a count the twin does not hold.
    """
    present = [
        cell
        for cell in cells
        if cell != "" and not _wears_a_published_hole(cell, holes)
    ]
    folded = {parsing.folded(cell) for cell in present}
    return (
        len(present),
        len(cells) - len(present),
        len(set(present)),
        len(folded),
    )


# -- the ladder (method G5.3) -----------------------------------------


def _filled_rungs(
    rungs: "tuple[float | None, ...]",
) -> "tuple[float, ...] | None":
    """The eleven rungs with every empty one filled in, or None.

    Guarantees: the rule is method G5.1's, which fixes it for every
    implementation rather than leaving it to this one. Contract rule L3
    accepts a rung that holds nothing, saying it carries no obligation,
    so a conforming description can arrive with one; that rung takes the
    nearest rung below it that holds a number, or the first rung of the
    ladder that holds one where none below does. Both keep the ladder
    non-decreasing and keep every value inside the rungs that ARE
    published. A ladder that holds nothing anywhere returns None, and
    the caller falls back to the sign counts. Nothing is read but the
    rungs given.
    """
    holds = [place for place in range(len(rungs)) if rungs[place] is not None]
    if not holds:
        return None
    filled: list[float] = []
    for place in range(len(rungs)):
        found = rungs[place]
        if found is None:
            below = [step for step in holds if step < place]
            if below:
                found = rungs[below[len(below) - 1]]
            else:
                found = rungs[holds[0]]
        filled = filled + [found if found is not None else 0.0]
    return tuple(filled)


def _segment(numerator: int, denominator: int) -> int:
    """The ladder segment a stratum's share falls in (method G5.3).

    The unique step with ``PCT[j] * D <= 100 * N < PCT[j+1] * D``,
    scanning upward from zero and stopping at the first that holds. The
    probabilities strictly increase, so the answer is unique.
    """
    scaled = 100 * numerator
    for step in range(10):
        below = _PCT[step] * denominator <= scaled
        if below and scaled < _PCT[step + 1] * denominator:
            return step
    return 9


def _interpolated(
    rungs: "tuple[float, ...]", numerator: int, denominator: int
) -> float:
    """One value from the ladder by the convex form (method G5.3).

    The share is worked out exactly in whole numbers and scaled by a
    power of two, so nothing rounds before the four floating-point
    operations the method fixes: one subtraction, two multiplications
    and one addition, in that order, followed by the clamp.

    The convex form rather than ``low + t * (high - low)`` because the
    difference form overflows to an infinity when two rungs sit at
    opposite ends of the representable range and loses the reading
    entirely between neighbouring very small values. The clamp is not
    decoration: ``1 - t`` rounds, so the pair can otherwise leave the
    segment by one unit in the last place, and the published ends are
    facts a recount would catch.
    """
    step = _segment(numerator, denominator)
    low = rungs[step]
    high = rungs[step + 1]
    above = 100 * numerator - _PCT[step] * denominator
    span = (_PCT[step + 1] - _PCT[step]) * denominator
    share = math.ldexp((above << 53) // span, -53)
    rest = 1 - share
    first = rest * low
    second = share * high
    value = first + second
    value = max(value, low)
    value = min(value, high)
    return value


def _whole_valued(value: float) -> float:
    """``value`` rounded to a whole number, ties toward +infinity (G5.4).

    To nearest, and ties toward positive infinity: not banker's
    rounding, because half-even would make a twin's rounding depend on
    the parity of a neighbour, and not toward zero, because two
    implementations that disagree here disagree on bytes. Both
    subtractions are exact, so no rounding happens inside the rule.
    """
    if not math.isfinite(value):
        return value
    below = int(value)
    rest = value - float(below)
    if rest > 0.5:
        return float(below + 1)
    if rest == 0.5:
        return float(below + 1)
    if rest < -0.5:
        return float(below - 1)
    return float(below)


def _exact_product(value: float, times: int) -> int:
    """``value * times`` rounded to a whole number, ties upward, exactly.

    The published number is a binary64, so it IS an exact rational: its
    significand and its power of two are read with `frexp`, and the
    product and the rounding are then whole-number arithmetic. Doing it
    in floating point would round twice and put two implementations a
    character apart on a long column (method G9.5 step 4).
    """
    if not math.isfinite(value):
        return 0
    fraction, exponent = math.frexp(value)
    significand = int(math.ldexp(fraction, 53))
    shift = 53 - exponent
    if shift <= 0:
        return significand * times * (1 << -shift)
    denominator = 1 << shift
    return (2 * significand * times + denominator) // (2 * denominator)


# -- how a number is written (method G6) ------------------------------


def _digits_and_point(value: float) -> "tuple[str, str, int]":
    """The shortest round-trip figures of ``value`` and its point.

    Returns the sign, the figures, and the position of the decimal point
    relative to them, so that ``value = 0.figures x 10 ** point``. The
    figures are the shortest decimal string that reads back as exactly
    this number, which is what Python's own `repr` produces; every
    spelling in method G6 is built from these three.
    """
    text = repr(value)
    sign = ""
    body = text
    if text[0] == "-":
        sign = "-"
        body = text[1:]
    mantissa = body
    exponent = 0
    marker = body.find("e")
    if marker >= 0:
        mantissa = body[:marker]
        exponent = int(body[marker + 1:])
    point = mantissa.find(".")
    if point < 0:
        figures = mantissa
        point = len(mantissa)
    else:
        figures = f"{mantissa[:point]}{mantissa[point + 1:]}"
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


def _fixed_point(sign: str, figures: str, place: int) -> str:
    """The figures written out in full, with at least one after the point."""
    if place <= 0:
        return f"{sign}0.{'0' * (-place)}{figures}"
    if place >= len(figures):
        return f"{sign}{figures}{'0' * (place - len(figures))}.0"
    return f"{sign}{figures[:place]}.{figures[place:]}"


def _incremented(digits: str) -> str:
    """One string of figures with one added to it, carrying to the left."""
    carried = "1"
    built = ""
    for place in range(len(digits) - 1, -1, -1):
        step = int(digits[place]) + int(carried)
        carried = "1" if step > 9 else "0"
        built = f"{step % 10}{built}"
    if carried == "1":
        return f"1{built}"
    return built


def _at_width(sign: str, figures: str, place: int, width: int) -> str:
    """The figures written with EXACTLY ``width`` of them after the point.

    THE CENSUS OF WIDTHS IS A PUBLISHED FACT AND THIS IS HOW A TWIN
    CARRIES IT (contract C6-27 to C6-30). A column of eleven `1.00`
    cells and eleven `2.000` cells publishes both widths, and a twin
    writing every cell at whatever width its own value happened to need
    carried the forms map exactly while writing a column no reader of
    the real one would recognize.

    SHORT OF THE WIDTH THE VALUE IS PADDED, WHICH COSTS NOTHING: a zero
    on the end changes no value. PAST it the value is ROUNDED, which
    costs something real and is stated rather than hidden -- the value
    moves by less than half of the last place the width can hold, and
    `_width_notes` recounts the finished text so the report says which
    width the column actually came out at.

    TIES GO TO EVEN, which is the plan's own word for this snap
    (P4-D4.5) and is NOT the tie rule the rest of this method uses.
    Every other rounding here places ONE value and a bias in it moves
    that value; this one places a whole column of them, and a bias
    toward positive infinity applied to every tie would walk the
    column's own mean up with it. The difference is stated here because
    a second implementer reading this function is owed one answer and
    this docstring gave the other one.

    A width of zero writes the point with nothing after it, which is
    what a cell reading `12.` is: the forms ladder counts it `decimal`
    and its width is none.
    """
    if place <= 0:
        whole = "0"
        fraction = ("0" * (-place)) + figures
    elif place >= len(figures):
        whole = figures + ("0" * (place - len(figures)))
        fraction = ""
    else:
        whole = figures[:place]
        fraction = figures[place:]
    if len(fraction) <= width:
        return f"{sign}{whole}.{fraction}{'0' * (width - len(fraction))}"
    kept = fraction[:width]
    following = fraction[width]
    rest = fraction[width + 1 :]
    trailing = False
    for character in rest:
        if character != "0":
            trailing = True
    if following > "5":
        up = True
    elif following < "5":
        up = False
    elif trailing:
        up = True
    else:
        # HALF TO EVEN, which is the plan's own word for this snap
        # (P4-D4.5). It is not the tie rule the rest of this method
        # uses, and that is deliberate rather than an oversight: every
        # other rounding here places ONE value and a bias in it moves
        # that value; this one places a whole column of them, and a
        # bias toward positive infinity applied to every tie would walk
        # the column's own mean up with it.
        last = kept[len(kept) - 1 :] if kept else whole[len(whole) - 1 :]
        up = last in "13579"
    digits = whole + kept
    if up:
        digits = _incremented(digits)
    cut = len(digits) - width
    return f"{sign}{digits[:cut]}.{digits[cut:]}"


def _exponent_form(sign: str, figures: str, place: int, marker: str) -> str:
    """The figures written in exponent notation, `d[.ddd]e+XX`."""
    power = place - 1
    body = figures[0]
    if len(figures) > 1:
        body = f"{figures[0]}.{figures[1:]}"
    lead = "+"
    if power < 0:
        lead = "-"
    return f"{sign}{body}{marker}{lead}{abs(power):02d}"


def _canonical_number(value: float, whole_column: bool) -> str:
    """The canonical spelling of one value (method G6.2).

    Where the column publishes that every value is a whole number, the
    figures of that whole number and nothing else, so a reader infers
    the same kind of column the real one was; zero is written `0` and
    never `-0`. Otherwise the shortest spelling that reads back as
    exactly this number, in fixed-point notation between the two
    boundaries the method names and in exponent notation outside them --
    which is what `repr` produces, and the method states the rule in
    full so an independent implementer does not have to work it out.
    """
    if whole_column:
        return f"{int(value)}"
    if value == 0.0:
        return "0.0"
    return repr(value)


# THE THREE STYLES A VALUE HAS TO BE WHOLE TO WEAR. `plain`,
# `leading_zero` and `leading_plus` are the styles whose finished text
# carries neither a decimal point nor an exponent, and the contract's
# own first-match ladder is what a twin cell's style IS (contract
# 7.5.4). So a cell can be counted in one of them only where the value
# it holds can be written with neither mark.
_WHOLE_STYLES = ("plain", "leading_zero", "leading_plus")


def _point_free(value: float, canonical: str) -> str:
    """The spelling of one value with neither a point nor an exponent.

    WHY THIS IS NOT SIMPLY THE CANONICAL SPELLING (review item
    P2-C2-F2). A column publishing `integer_valued: false` writes its
    canonical spellings by the shortest-round-trip rule, so the
    canonical spelling of the whole value 100 in such a column is
    `100.0` -- which the contract's ladder counts as `decimal`. A real
    column holding `1.5` beside `100` publishes eleven `decimal` cells
    and forty `plain` ones, and the forty were written `100`, `101` and
    so on. Writing them `100.0` misses the published form on every one
    of those cells, so the styles that need a point-free text take one
    where the value has one: the figures of the whole number, which read
    back as exactly the same value.

    Where the value is not whole, or stands outside the window in which
    the shortest round trip is written in fixed-point notation, no
    point-free spelling of it exists and the canonical spelling comes
    back. `_carries_plainly` asks that question, and G6.4's placement
    never puts one of the three styles on such a cell unless every other
    quota is already spent.
    """
    if "." not in canonical and "e" not in canonical and "E" not in canonical:
        return canonical
    sign, figures, place = _digits_and_point(value)
    if figures == "0":
        return "0"
    if place >= len(figures):
        # A WHOLE VALUE IS WRITTEN WITHOUT A POINT AT ANY WIDTH (owner
        # decision 10, 2026-08-13). The sixteen-figure ceiling that used
        # to stand here belongs to the CANONICAL spelling of contract
        # 3.2.1, which turns to an exponent above it -- and that grammar
        # governs the profile document's own numbers, not the twin's
        # plain cells. A `plain` cell owes exactly two things: it reads
        # back as the same number, and it classifies as `plain`. The
        # full digit expansion of a whole value does both however wide
        # it is, because the figures are the shortest round trip and the
        # zeros after them carry no information the float does not
        # already hold.
        #
        # What the ceiling cost was a column whose source wrote very
        # wide whole numbers in figures: it published them `plain`, and
        # the twin wrote `100000000000000000000.0`, which a reader takes
        # for a decimal column. That is the type change owner decision
        # 10 of Phase 2 exists to prevent, arriving through the door
        # this line left open.
        return f"{sign}{figures}{'0' * (place - len(figures))}"
    return canonical


def _carries_plainly(value: float, whole_column: bool) -> bool:
    """True when this value can wear a style that carries no point."""
    written = _point_free(value, _canonical_number(value, whole_column))
    return (
        "." not in written and "e" not in written and "E" not in written
    )


def _with_zeros(spelling: str, order: int) -> str:
    """``order`` zeros written straight after the sign (owner decision 8).

    THE INVENTION FAMILY, AVAILABLE INSIDE EVERY STYLE THAT CAN HOLD IT
    (review item P2-C2-F3). Owner decision 8 chose the leading-zero
    family because it has no ceiling and changes no type a reader
    infers. An earlier revision reached for it only where the assigned
    style was literally `leading_zero`, which left a column reproducing
    a `decimal` or an exponent form with one spelling of a value and no
    way to make a second. Zeros written after the sign leave the
    contract's ladder where it was for every style but `plain`: a point
    keeps a cell `decimal`, an `e` keeps it `exponent_lower`, a leading
    plus keeps it `leading_plus`, and the value each reads back as is
    unchanged. `plain` is the one style with no family, because a zero
    in front of a plain spelling is exactly what makes it
    `leading_zero`.
    """
    if order < 1:
        return spelling
    lead = ""
    body = spelling
    if spelling[0] == "-" or spelling[0] == "+":
        lead = spelling[0]
        body = spelling[1:]
    return f"{lead}{'0' * order}{body}"


def _styled_number(
    value: float,
    style: str,
    order: int,
    whole_column: bool,
    width: int = -1,
    pad: int = -1,
) -> str:
    """One value written in one of the six permitted styles (G6.1, G6.3).

    ``order`` is the leading-zero order of owner decision 8, counted
    from zero: order zero is the style's own base spelling, and each
    step adds one zero after the sign. The `leading_zero` style starts
    at one, because that is what makes it that style at all.

    Never a thousands separator -- the comma breaks the CSV row itself
    -- and never accounting parentheses, which are kept for the
    contradictory-notation stand-in and would otherwise move a cell into
    another class.
    """
    canonical = _canonical_number(value, whole_column)
    if style == "plain":
        return _point_free(value, canonical)
    if style == "leading_zero":
        plain = _point_free(value, canonical)
        # A PUBLISHED FIELD WIDTH OUTRANKS THE ORDER, because the order
        # is a count of zeros and the width is the fact a person sees.
        # `pad` of -1 is "no census reached this cell", which is the
        # pooled remainder's rule and the behaviour of every profile
        # written before the census existed.
        if pad >= 0:
            carried = len(plain) - 1 if plain[:1] == "-" else len(plain)
            return _with_zeros(plain, max(order, pad - carried))
        return _with_zeros(plain, max(order, 1))
    if style == "leading_plus":
        plain = _point_free(value, canonical)
        if plain[0] == "-":
            return plain
        return _with_zeros(f"+{plain}", order)
    figures = _digits_and_point(value)
    if style == "decimal":
        # A width of -1 is "whatever this value needs", which is what a
        # column publishing no census of widths asks for. Any other
        # width is one the census named, and the cell is written at it.
        if width < 0:
            return _with_zeros(
                _fixed_point(figures[0], figures[1], figures[2]), order
            )
        return _with_zeros(
            _at_width(figures[0], figures[1], figures[2], width), order
        )
    if style == "exponent_lower":
        return _with_zeros(
            _exponent_form(figures[0], figures[1], figures[2], "e"), order
        )
    if style == "exponent_upper":
        return _with_zeros(
            _exponent_form(figures[0], figures[1], figures[2], "E"), order
        )
    return canonical


def _pinned_cells(
    layout: "_NumericLayout", values: "list[float]"
) -> "list[int]":
    """Which cells hold a value no snap may move, in the plan's order.

    The minimum, then the maximum, then every cell of the zero stratum
    (plan P4-D4.5). Each is an EXACT-OBSERVABLE fact of its own -- two
    rungs the ladder pins and a published count of zeros -- so a width
    census may never be met by moving one of them.

    The indexes are into the COLUMN'S CELLS, which is what the width
    walk holds: a stratum can cover several cells, and the zero stratum
    covers all of its own.

    A CELL IS PINNED BY THE VALUE IT HOLDS AND NOT BY WHERE IT STANDS.
    An endpoint stratum can cover several cells and two strata can hold
    the same number, so pinning the first cell of each and leaving its
    twins free let a snap move a copy of the published minimum: at one
    figure after the point a column whose smallest value is -745.75
    wrote -745.8 into a second cell holding that same value, and the
    file's own smallest value was then a number the description does
    not publish. Every cell holding a pinned value is pinned.
    """
    starts: list[int] = []
    at = 0
    for place in range(len(layout.sizes)):
        starts = starts + [at]
        at = at + layout.sizes[place]
    total = len(layout.sizes)
    kept: list[float] = []
    if total >= 1:
        kept = kept + [values[0]]
    if total >= 2:
        kept = kept + [values[total - 1]]
    found: list[int] = []
    for value in kept:
        for place in range(total):
            if values[place] != value:
                continue
            for step in range(layout.sizes[place]):
                found = found + [starts[place] + step]
    for place in range(total):
        if layout.bands[place] != _BAND_ZERO:
            continue
        for step in range(layout.sizes[place]):
            found = found + [starts[place] + step]
    settled: list[int] = []
    seen: dict[int, int] = {}
    for index in found:
        if index in seen:
            continue
        seen[index] = 1
        settled = settled + [index]
    return settled


def _fraction_need(value: float) -> int:
    """How many figures after the point this value's own spelling needs."""
    sign, figures, place = _digits_and_point(value)
    if place <= 0:
        return (-place) + len(figures)
    if place >= len(figures):
        return 1
    return len(figures) - place


def _published_ends(
    facts: contract.NumericFacts, values: "list[float]"
) -> "tuple[float, float]":
    """The two rungs no cell of this column may be carried outside.

    The published ladder's own ends where it has them, and the drawn
    values' ends where a rung is null -- a null rung carries no
    obligation at that rung (contract L3), so nothing is bounded by it
    and the column's own spread is what remains.
    """
    rungs = facts.percentiles.rungs
    low = rungs[0]
    high = rungs[10]
    if low is None or high is None:
        found = sorted(values)
        if not found:
            return (0.0, 0.0)
        return (found[0], found[len(found) - 1])
    return (low, high)


def _segment_of(
    value: float, bounds: "dict[float, tuple[float, float]]"
) -> "tuple[float, float]":
    """The stretch of the ladder one value's cells were drawn from."""
    if value in bounds:
        return bounds[value]
    return (value, value)


def _segment_bounds(
    column: contract.ColumnBlock,
    facts: contract.NumericFacts,
    layout: "_NumericLayout | None",
    values: "list[float]",
) -> "dict[float, tuple[float, float]]":
    """Where on the ladder each drawn value came from, by value.

    A stratum covers a stretch of the ladder and its value was
    interpolated inside that stretch, so the stretch is what a snap of
    that value may not leave. The two ENDPOINT strata are pinned and
    their stretch is the single published rung, which is what keeps a
    snap off `min` and `max`.

    Keyed by VALUE rather than by cell, because that is what the width
    walk holds and because two strata carrying the same number are one
    number however many stretches drew it: where that happens the
    widest stretch would be too generous, so the tightest is kept.

    A null rung carries no obligation at that rung (contract L3), so a
    ladder with one is bounded by the drawn values' own ends instead.
    """
    rungs = facts.percentiles.rungs
    found: dict[float, tuple[float, float]] = {}
    # ANY null rung, not only an end. A rung that is not a finite
    # binary64 carries no obligation at that rung (contract L3), and
    # interpolating THROUGH it is arithmetic on nothing -- which is a
    # crash rather than a wrong answer, and was one.
    settled = True
    for rung in rungs:
        if rung is None:
            settled = False
    if layout is None or not settled:
        held = sorted(values)
        if not held:
            return found
        whole: "tuple[float, float]" = (held[0], held[len(held) - 1])
        for value in values:
            found[value] = whole
        return found
    total = len(layout.sizes)
    # Read out once, past the null test above, so the interpolation
    # takes the finite ladder this function has already established.
    settled_rungs = tuple(rung for rung in rungs if rung is not None)
    for place in range(total):
        value = values[place]
        span: "tuple[float, float]" = (value, value)
        if not (place == 0 or (place == total - 1 and total >= 2)):
            span = (
                _interpolated(
                    settled_rungs, layout.starts[place], column.n_numeric
                ),
                _interpolated(
                    settled_rungs,
                    layout.starts[place] + layout.sizes[place],
                    column.n_numeric,
                ),
            )
        if value in found:
            seen = found[value]
            span = (max(seen[0], span[0]), min(seen[1], span[1]))
        found[value] = span
    return found


def _snaps_away(
    value: float,
    width: int,
    bounds: "dict[float, tuple[float, float]]",
    ends: "tuple[float, float]",
) -> bool:
    """Whether writing this value at this width would erase what it is.

    A SNAP MAY NEVER CHANGE A CELL'S ZERO-NESS OR ITS SIGN CLASS
    (P4-D4.5). `n_zero` and `n_negative` are EXACT published counts, so
    a value rounded onto zero would buy a published width with a
    published count -- and the plan's repair, "the nearest same-class
    value at that width inside the cell's segment", has no answer at
    WIDTH ZERO: the nearest non-zero whole number is a whole unit away
    and lands outside the segment the ladder gave the cell.

    So the width is refused for that value instead, and A-P4-15's route
    carries it: the value keeps its own width, the quota goes unmet,
    and the report names the width that went unplaced. The alternative
    was silent, and it fired on an ordinary column -- eighty-nine cells
    written `1.` through `11.` beside eleven written `0.01` to `0.11`
    publishes eighty-nine cells at width zero, and the twin wrote four
    of its own positive values as `0.` while its description published
    no zero at all.
    """
    sign, figures, place = _digits_and_point(value)
    written = _at_width(sign, figures, place, width)
    read = parsing.parse_number(written)
    if read is None:
        return True
    # ...AND ITS REACH MAY NOT EXCEED THE STRETCH OF LADDER THE CELL
    # WAS DRAWN FROM. A snap at width w moves a value by less than half
    # of the last place that width holds; the stratum it came from
    # covers a stretch of the published ladder. Where the reach is
    # smaller than the stretch, the cell stays in the neighbourhood the
    # ladder put it in and every rung window absorbs it -- which is
    # what the plan means by landing "in the same G12 envelopes".
    # Where the reach is BIGGER, the snap is not an adjustment inside a
    # neighbourhood, it is the neighbourhood being erased.
    #
    # That case is not hypothetical and it is loud. Thirty cells
    # written `5.` beside thirty written `5.01` to `5.30` publish a
    # width of zero for half the column; the drawn values hold every
    # window before the snap, and after it twenty-six of them read
    # `5.` -- p50, p75, p90, p95, the mean and the spread all MISSED,
    # at every seed tried, on a description a real table produced.
    # G12.2 grants this method exactly one widening and says so, and it
    # is not this one, so the answer cannot be a wider window.
    #
    # The two pinned rungs come through this rule rather than beside
    # it: their stretch is the single published value, so no reach at
    # all fits inside it and no snap may touch them.
    low, high = _segment_of(value, bounds)
    reach = 0.5
    for _step in range(width):
        reach = reach / 10.0
    if reach > high - low:
        return True
    # AND NEVER OUTSIDE THE COLUMN'S OWN TWO ENDS, which are exact.
    # The stretch test above keeps a cell in its neighbourhood; this
    # keeps the whole column inside the two rungs the ladder pins, for
    # the cell whose neighbourhood touches one of them.
    if read < ends[0] or read > ends[1]:
        return True
    if value == 0.0:
        return False
    if read == 0.0:
        return True
    return (read < 0.0) != (value < 0.0)


def _width_places(
    widths: "dict[str, int]",
    styles: "list[str]",
    holds: "list[float]",
    pinned: "list[int]",
    bounds: "dict[float, tuple[float, float]]",
    ends: "tuple[float, float]",
    whole_column: bool,
) -> "list[int]":
    """Which width each cell is written at, or -1 for the value's own.

    THE PINNED CELLS ARE SERVED FIRST AND ARE NEVER SNAPPED (plan
    P4-D4.5). The two endpoints and the zero stratum are
    EXACT-OBSERVABLE facts of their own, so a snap that moved one of
    them would buy a published width with a published rung. A pinned
    cell counts toward a width only where its value ALREADY fits it,
    and where it fits several it takes the largest still-unfilled one,
    walked in the plan's stated order -- minimum, maximum, zero -- so
    that no byte is left to an implementation's taste.

    THE REST ARE SERVED LARGEST WIDTH FIRST, against the cells whose
    drawn values need the most figures. A wide value put into a narrow
    width loses figures it needed; a narrow value put into a wide width
    is padded and loses nothing. So the cells that need the most are
    matched to the widths that hold the most, and what rounding remains
    is as little as the census allows.

    A cell the census does not reach is written at whatever width its
    own value needs -- the pooled remainder's rule of G6.4, unchanged.
    """
    quotas: dict[int, int] = {}
    for key in sorted(widths):
        if key == contract.WITHHELD:
            continue
        quotas[int(key)] = widths[key]
    places = [-1 for _index in range(len(styles))]
    served = {index: 1 for index in pinned}
    # THE PINNED CELLS ARE SERVED BY VALUE TOO, not one cell at a time.
    # The plan fixes the ORDER a pinned value takes its width in --
    # minimum, maximum, zero, each taking the largest still-unfilled
    # width its value fits -- and that order is kept. What is not kept
    # is doing it per CELL: a pinned value can cover a dozen cells, and
    # a quota that holds eleven of them handed the twelfth to another
    # width, so one number came out as `9.50` eleven times and `9.5`
    # once. That is two spellings of one value, which spends the
    # column's published count of different values -- and it buys
    # nothing, because the quotas close either way. A pinned value now
    # takes a width only where the width can hold its whole group.
    pinned_order: "list[float]" = []
    pinned_groups: "dict[float, list[int]]" = {}
    for index in pinned:
        if index >= len(styles) or styles[index] != "decimal":
            continue
        value = holds[index]
        if value in pinned_groups:
            pinned_groups[value] = pinned_groups[value] + [index]
            continue
        pinned_order = pinned_order + [value]
        pinned_groups[value] = [index]
    for value in pinned_order:
        members = pinned_groups[value]
        need = _fraction_need(value)
        for width in sorted(quotas, reverse=True):
            if quotas[width] < len(members) or need > width:
                continue
            quotas[width] = quotas[width] - len(members)
            for index in members:
                places[index] = width
            break
    # ONE WIDTH PER VALUE WHERE THE QUOTAS ALLOW IT, which is the width
    # walk's form of the rule the style walk already keeps. A value
    # written at two widths is TWO spellings of one number, so a walk
    # that handed a value's cells to different widths spent a published
    # spelling count to meet a published width count -- one exact fact
    # bought with another, which is the trade this method refuses
    # everywhere else. A real column's cells wear one width per value
    # because that is what a person writing them does.
    groups: dict[float, list[int]] = {}
    order: list[tuple[int, float]] = []
    for index in range(len(styles)):
        if styles[index] != "decimal" or index in served:
            continue
        value = holds[index]
        if value in groups:
            groups[value] = groups[value] + [index]
            continue
        groups[value] = [index]
        order = order + [(-_fraction_need(value), value)]
    # HOW MANY CELLS EACH VALUE HOLDS IN ALL, not just how many of them
    # the style step made decimal. A snap moves the VALUE, so snapping
    # the decimal cells of a value some of whose cells were written
    # another way splits one number into two -- and the count of
    # different values is a published fact of its own. Such a value may
    # still be PADDED, which changes nothing about it, so the rule is
    # written over the two cases separately rather than refusing the
    # value outright.
    everywhere: dict[float, int] = {}
    for index in range(len(styles)):
        value = holds[index]
        if value in everywhere:
            everywhere[value] = everywhere[value] + 1
            continue
        everywhere[value] = 1
    for _need, value in sorted(order):
        members = groups[value]
        alone = everywhere[value] == len(members)
        need = _fraction_need(value)
        whole = None
        for width in sorted(quotas, reverse=True):
            if quotas[width] < len(members):
                continue
            if not alone:
                # A VALUE SOME OF WHOSE CELLS WERE WRITTEN ANOTHER WAY
                # TAKES NO WIDTH AT ALL, and that covers padding as
                # well as snapping. Snapping such a value splits the
                # NUMBER; padding it splits its SPELLING, because the
                # cells the style step wrote plainly keep the value's
                # own canonical text -- one column came out holding
                # `0.500` beside `0.5`, two spellings of one number
                # bought with a width quota that closed either way.
                continue
            if _snaps_away(value, width, bounds, ends):
                continue
            whole = width
            break
        if whole is None:
            # NO WIDTH HOLDS THE WHOLE GROUP, so this group takes none.
            # Splitting it would write ONE value at two widths, which is
            # two spellings of one number -- a published spelling count
            # spent to buy a published width count, and that trade is
            # refused here as it is refused for the forms map. The
            # group's cells are written at their own value's width
            # instead, and `_width_notes` names the width that went
            # unplaced so a reader is told rather than left to recount.
            continue
        quotas[whole] = quotas[whole] - len(members)
        for index in members:
            places[index] = whole
    return _some_fraction_survives(places, styles, holds, whole_column)


def _pad_need(value: float, whole_column: bool) -> int:
    """How many figures this value's own point-free spelling writes.

    The sign is not a figure, for the reason `parsing.pad_width` gives:
    the width a person sees in a code column is the field.
    """
    plain = _point_free(value, _canonical_number(value, whole_column))
    return len(plain) - 1 if plain[:1] == "-" else len(plain)


def _can_wear(style: str, value: float, whole_column: bool) -> bool:
    """Whether one value may be written in one style at all.

    Two rules, and the styles impose both: there is no leading-plus
    spelling of a negative value, and no point-free spelling of a value
    that has none.
    """
    if style == "leading_plus" and value < 0.0:
        return False
    if style in _WHOLE_STYLES and not _carries_plainly(value, whole_column):
        return False
    return True


def _first_giver(
    moved: "list[str]",
    holds: "list[float]",
    reserved: "dict[int, int]",
    taken: "dict[int, int]",
    width: int,
    taking: str,
    whole_column: bool,
) -> int:
    """The first padded cell free to give the style up, or -1.

    Written outside the walk so a whole value's exchange can be tried
    before any of it is applied: ``taken`` holds the cells this trial
    has already spoken for, which the walk's own bookkeeping does not
    know about until the trial is accepted.

    IT TAKES THE VALUES AND NOT TWO FUNCTIONS. Handing a callable to a
    helper is a call this repository's offline audit cannot read, and
    the audit is right to refuse it: a function passed as a value is a
    function nobody can check by reading the source.
    """
    for other in range(len(moved)):
        if moved[other] != "leading_zero":
            continue
        if other in reserved or other in taken:
            continue
        if _pad_need(holds[other], whole_column) < width:
            continue
        if not _can_wear(taking, holds[other], whole_column):
            continue
        return other
    return -1


def _eligible_groups(
    eligible: "list[int]",
    moved: "list[str]",
    holds: "list[float]",
    spent: "dict[int, int]",
) -> "list[list[int]]":
    """The eligible cells, gathered into one group per value.

    The walk that fills a published field width takes a WHOLE group or
    none of it, so a value never ends up wearing the padded style on
    some of its cells and another style on the rest. Groups are walked
    largest first, and the value itself breaks every tie, so the order
    is a function of the description rather than of the order a mapping
    happens to hold.
    """
    groups: "dict[float, list[int]]" = {}
    seen: "list[float]" = []
    for index in eligible:
        if index in spent or moved[index] == "leading_zero":
            continue
        value = holds[index]
        if value in groups:
            groups[value] = groups[value] + [index]
            continue
        groups[value] = [index]
        seen = seen + [value]
    ranked: "list[tuple[int, float]]" = []
    for value in seen:
        ranked = ranked + [(-len(groups[value]), value)]
    ordered: "list[list[int]]" = []
    for _size, value in sorted(ranked):
        ordered = ordered + [groups[value]]
    return ordered


def _padded_style_swaps(
    styles: "list[str]",
    holds: "list[float]",
    widths: "dict[str, int]",
    pinned: "list[int]",
    whole_column: bool,
) -> "list[str]":
    """Move the padded style onto values a published field width can hold.

    THE STYLE WALK CHOOSES CELLS AND THE CENSUS CHOOSES WIDTHS, and
    before this pass the two never spoke. A description publishing
    fifteen padded cells all two figures wide is met only by padding
    fifteen SINGLE-FIGURE values: a two-figure value wearing a leading
    zero is three figures wide, and no amount of padding makes it two.
    The style walk, which knows nothing of the census, handed the style
    to values needing two figures, so the twin wrote fourteen cells at
    width three, missed a census it could have met, and the report
    accused a twin whose description was perfectly satisfiable.

    THE EXCHANGE IS BETWEEN TWO CELLS, so every published style count is
    the same afterwards as before: one cell gives up `leading_zero` and
    takes the partner's style, and the partner takes `leading_zero`.
    Nothing is invented and no quota moves.

    WHAT GUARDS IT. A pinned cell -- an endpoint or the zero stratum --
    is never a partner, because those are exact-observable positions
    the style walk placed deliberately. A partner must be able to WEAR
    the padded style, which the whole-value test decides; and the cell
    giving it up must be able to wear what it receives, which is the
    same test wherever the partner's own style carries no point. A
    value already fitting a published width is left alone, so a twin
    that was already meeting the census is not stirred.

    Guarantees: accepts the assigned styles, the drawn values, the
    published census, the pinned positions and whether the column is
    whole; returns one style per cell, a permutation of the styles
    handed in. Determinism: every walk is over an ascending index
    order. Raises nothing. No I/O of any kind.
    """
    quotas: dict[int, int] = {}
    for key in sorted(widths):
        if key == contract.WITHHELD:
            continue
        quotas[int(key)] = widths[key]
    if not quotas:
        return styles
    moved = list(styles)

    def need_of(index: int) -> int:
        return _pad_need(holds[index], whole_column)

    def receivable(index: int, other: str) -> bool:
        """Whether the cell giving up the padded style can wear ``other``."""
        return _can_wear(other, holds[index], whole_column)

    # Every cell that could WEAR the padded style but is not wearing it,
    # in ascending index order so the partner chosen is the same on
    # every run.
    # A PINNED CELL IS NOT SPECIAL HERE, EITHER WAY ROUND, and that is
    # the whole rule rather than an exception to one. What pins a cell
    # is its VALUE -- it is a published endpoint or the zero stratum --
    # and a style carries no value: `1` and `01` read back as the same
    # number, so neither taking the padding off a pinned cell nor
    # putting it on moves a published fact. Guarding pinned cells left
    # the census unmeetable on a real column whose ONLY value narrow
    # enough for the published field was the endpoint: eleven `+1`,
    # eleven `-99` and eleven `-02` publish one field of two figures,
    # and the twin wrote three-figure fields because the one cell that
    # could have worn it was refused.
    eligible: "list[int]" = []
    for index in range(len(moved)):
        if moved[index] == "leading_zero":
            continue
        if not _carries_plainly(holds[index], whole_column):
            continue
        eligible = eligible + [index]

    # THE CENSUS ASKS FOR WIDTHS, NOT FOR A WIDTH, and this walk is the
    # difference. An earlier pass asked only whether a value fitted the
    # WIDEST published field, which on a column publishing several
    # widths is barely a question at all: a six-figure value "fits" a
    # width of eight and is still hopeless for the width of three that
    # the census also asks for. So the narrow widths went unfilled, the
    # cells that could have filled them sat in another style, and the
    # twin missed most of a census it could largely have met.
    #
    # Narrow fields first, because they are the hard ones: a value that
    # can wear a field of three can wear every wider field too, so
    # spending it on a wide field is what makes a narrow one
    # unfillable.
    reserved: "dict[int, int]" = {}
    spent: "dict[int, int]" = {}

    def give_up(width: int, taking: str) -> int:
        """A padded cell this width cannot hold, free to give the style up."""
        for other in range(len(moved)):
            if moved[other] != "leading_zero" or other in reserved:
                continue
            # A PINNED CELL MAY GIVE THE STYLE UP, though it may never
            # be handed it. What pins a cell is its VALUE -- it is a
            # published endpoint or the zero stratum -- and a style
            # carries no value: `27` and `027` read back as the same
            # number, so taking the padding off the maximum moves no
            # published fact. Refusing it left the census unmeetable on
            # every column whose widest value was also its endpoint.
            if need_of(other) < width:
                continue
            if not receivable(other, taking):
                continue
            return other
        return -1

    def hand_over(index: int, width: int) -> bool:
        """Swap the padded style onto ``index``; say whether it happened."""
        partner = give_up(width, moved[index])
        if partner < 0:
            return False
        moved[partner] = moved[index]
        moved[index] = "leading_zero"
        spent[index] = 1
        reserved[index] = width
        return True

    for width in sorted(quotas):
        owing = quotas[width]
        for index in range(len(moved)):
            if owing < 1:
                break
            if moved[index] != "leading_zero" or index in reserved:
                continue
            if need_of(index) >= width:
                continue
            reserved[index] = width
            owing = owing - 1
        # A WHOLE VALUE AT A TIME, AND ONLY WHERE THE WHOLE OF IT FITS.
        # Taking SOME of a value's cells leaves that value wearing the
        # padded style on those and another style on the rest: `0185`
        # beside `185` in one column is one number written two ways,
        # and on a column of codes it is worse than that, because the
        # two are different LENGTHS and somebody checking how long a
        # code is meets both. An earlier version of this walk ordered
        # the cells so a value's travelled together but still stopped
        # mid-value when the count ran out, which is the same defect
        # arrived at more tidily.
        for group in _eligible_groups(eligible, moved, holds, spent):
            if owing < 1:
                break
            if len(group) > owing:
                continue
            if need_of(group[0]) >= width:
                continue
            # ALL OF IT OR NONE OF IT. Handing the style over one cell
            # at a time and stopping when the givers run out splits the
            # value just as surely as stopping when the count does, so
            # the exchange is tried first and applied only if every
            # cell of the group found a partner.
            trial: "list[tuple[int, int]]" = []
            taken: "dict[int, int]" = {}
            for index in group:
                partner = _first_giver(
                    moved, holds, reserved, taken, width,
                    moved[index], whole_column,
                )
                if partner < 0:
                    trial = []
                    break
                taken[partner] = 1
                trial = trial + [(index, partner)]
            if not trial:
                continue
            for index, partner in trial:
                moved[partner] = moved[index]
                moved[index] = "leading_zero"
                spent[index] = 1
                reserved[index] = width
                owing = owing - 1
        # ...and cell by cell for a count no whole value fits. This
        # SPLITS a value -- `0185` beside `185` is one number in two
        # spellings at two lengths -- and it is kept because the
        # alternative is worse rather than because it is good. Leaving
        # the count short sends the cells to the identity walk instead,
        # which spends leading zeros to make spellings differ and wrote
        # one number at FOUR widths on the same column. One split is
        # the smaller harm, and the shortfall it avoids is the one a
        # person measuring a code's length would meet everywhere
        # rather than once.
        for index in eligible:
            if owing < 1:
                break
            if index in spent or moved[index] == "leading_zero":
                continue
            if need_of(index) >= width:
                continue
            if not hand_over(index, width):
                break
            owing = owing - 1
    return moved


def _pad_places(
    widths: "dict[str, int]",
    styles: "list[str]",
    holds: "list[float]",
    whole_column: bool,
) -> "list[int]":
    """Which field width each padded cell is written at, or -1 for none.

    THE SIMPLER OF THE TWO WIDTH WALKS, and it is worth saying why it
    is allowed to be. A fraction width MOVES THE VALUE: writing 9.53 at
    one place makes it 9.5, so that walk has to protect the published
    endpoints, the zero stratum and every pinned rung from being bought
    with a width. Padding moves nothing -- `000123` and `123` read back
    as the same number -- so no rung, no endpoint and no statistic is
    at stake here, and the walk has only one published fact to keep
    faith with besides the census itself.

    THAT ONE FACT IS THE COUNT OF DIFFERENT VALUES. A value written at
    two field widths is TWO spellings of one number, so a width is
    taken only where it holds a value's WHOLE group of cells -- the
    same rule the fraction walk keeps, for the same reason, and the
    reason the identity walk downstream is left its own room.

    A WIDTH NARROWER THAN THE VALUE IS NOT A WIDTH. Nine figures cannot
    be written in a field of five without losing figures the value
    needs, and losing them would move the value -- which is the one
    thing padding must never do. Such a pairing is skipped, and the
    cells fall to the pooled remainder's rule.

    SERVED NARROWEST FIRST, CELL BY CELL, IN INDEX ORDER. A value that
    can wear a field of three can wear every wider field too, so a walk
    that spends it on a wide field is the walk that leaves a narrow one
    unfillable. Serving the narrow quotas first is what makes a census
    of several widths reachable at all.

    IT IS A WALK AND NOT AN OPTIMUM, and that is stated rather than
    implied: filling counted quotas from cells of differing capacities
    is the shape of problem packing bins is, and no rule of this size
    settles every case. What makes that safe is that a width the walk
    cannot fill is RECOUNTED off the finished cells and named in the
    twin's report by `_pad_notes`, rather than passed over in silence.

    Guarantees: accepts the published census, the assigned styles, the
    drawn values and whether the column is whole; returns one entry per
    cell, either a published width or -1. Determinism: the answer
    depends only on those inputs, and every walk is over a sorted
    order. Raises nothing. No I/O of any kind.
    """
    quotas: dict[int, int] = {}
    for key in sorted(widths):
        if key == contract.WITHHELD:
            continue
        quotas[int(key)] = widths[key]
    places = [-1 for _index in range(len(styles))]
    if not quotas:
        return places
    # THE CELLS THIS WALK MAY PLACE, GROUPED BY THE VALUE THEY HOLD.
    groups: "dict[float, list[int]]" = {}
    seen: "list[float]" = []
    for index in range(len(styles)):
        if styles[index] != "leading_zero":
            continue
        value = holds[index]
        if value in groups:
            groups[value] = groups[value] + [index]
            continue
        groups[value] = [index]
        seen = seen + [value]
    # NARROW FIELDS FIRST, because a value that fits a field of three
    # fits every wider one, so spending it on a wide field is what
    # makes a narrow field unfillable.
    #
    # WHOLE VALUES FIRST WITHIN EACH FIELD, AND A VALUE IS SPLIT ONLY
    # AS FAR AS THE CENSUS FORCES IT. Both halves of that sentence were
    # learned from a defect. Holding every value to ONE field collapsed
    # a column publishing `01`, `001` and `0001` -- one number written
    # three ways -- onto a single spelling, meeting none of its three
    # published counts. Splitting freely did the opposite: a column of
    # seventeen `01`, seventeen `002` and eleven `3` came out wearing
    # six spellings where three were published, because the walk cut
    # values across fields it had no need to cut. So a field is filled
    # from WHOLE value groups while whole groups still fit it, and one
    # group is divided only to finish a count that nothing else can.
    for width in sorted(quotas):
        owing = quotas[width]
        ranked: "list[tuple[int, float]]" = []
        for value in seen:
            waiting = 0
            for index in groups[value]:
                if places[index] < 0:
                    waiting = waiting + 1
            if waiting < 1 or _pad_need(value, whole_column) >= width:
                continue
            ranked = ranked + [(-waiting, value)]
        for _size, value in sorted(ranked):
            if owing < 1:
                break
            unplaced: "list[int]" = []
            for index in groups[value]:
                if places[index] < 0:
                    unplaced = unplaced + [index]
            if len(unplaced) > owing:
                continue
            for index in unplaced:
                places[index] = width
            owing = owing - len(unplaced)
        # ...and then, and only then, one value is divided.
        for _size, value in sorted(ranked):
            if owing < 1:
                break
            for index in groups[value]:
                if owing < 1:
                    break
                if places[index] >= 0:
                    continue
                places[index] = width
                owing = owing - 1
    # A cell no count could hold takes the narrowest PUBLISHED width
    # its value can still wear, over that width's count rather than
    # outside the census altogether. A cell left to its own value
    # writes a field the census never named -- a seventh figure where
    # the census names three and six -- so the twin would carry a field
    # width the source column never had. Over-filling a published width
    # is a miss the recount names; writing an unpublished width is a
    # shape that was never there to begin with.
    for index in range(len(styles)):
        if styles[index] != "leading_zero" or places[index] >= 0:
            continue
        need = _pad_need(holds[index], whole_column)
        for width in sorted(quotas):
            if need >= width:
                continue
            places[index] = width
            break
    return places


def _some_fraction_survives(
    places: "list[int]",
    styles: "list[str]",
    holds: "list[float]",
    whole_column: bool,
) -> "list[int]":
    """Give one width back where the snap would make every value whole.

    `integer_valued` is a fact about the COLUMN -- "every value it
    holds is a whole number" -- and it is the fact a consumer routes on
    (AF6), recounted from the written cells. A column publishing FALSE
    whose every value the snap rounded onto a whole number is
    re-profiled as `count` rather than `continuous`, so the twin's own
    type is not the type its description publishes: twenty-six cells
    written `1.`, twenty-five `2.` and twenty-nine at one figure
    published a width of zero for fifty-one of them, the twin came back
    a column of counts, and `validate` reported the ROLE missed.

    THE GRAIN IS THE COLUMN AND NOT THE CELL. Refusing every snap that
    makes one value whole is far too strong -- a column of halves may
    round one of them to `2.0` and still hold plenty that are not --
    and it spends published width quotas for nothing. So the walk runs,
    and only where NOTHING non-whole survived does one group give its
    width back: the one that needed the most figures, which is the one
    the snap took the most from.
    """
    if whole_column:
        return places
    widest = -1
    biggest = -1
    for index in range(len(styles)):
        value = holds[index]
        if value == int(value):
            continue
        if places[index] < 0:
            return places
        sign, figures, place = _digits_and_point(value)
        written = _at_width(sign, figures, place, places[index])
        read = parsing.parse_number(written)
        if read is not None and read != int(read):
            return places
        need = _fraction_need(value)
        if need > biggest:
            biggest = need
            widest = index
    if widest < 0:
        return places
    kept = holds[widest]
    given: list[int] = []
    for index in range(len(places)):
        if styles[index] == "decimal" and holds[index] == kept:
            given = given + [-1]
            continue
        given = given + [places[index]]
    return given


def _style_quotas(styles: "dict[str, int]") -> "dict[str, int]":
    """The published count of every style, the held-back share pooled.

    A style used by fewer rows than the smallest group size is held back
    and pooled, exactly as a rare label is. The pooled share is written
    in the plain style, because plain is the style that changes nothing
    a reader infers, and the report says how many cells it covered.
    """
    quotas = {name: 0 for name in contract.NUMERIC_STYLES}
    for name in sorted(styles):
        if name == contract.WITHHELD:
            quotas["plain"] = quotas["plain"] + styles[name]
        else:
            quotas[name] = quotas[name] + styles[name]
    return quotas


def _style_pool(styles: "dict[str, int]") -> int:
    """How many cells the description held back below the floor (G6.4).

    A style used by fewer rows than the smallest group size is pooled
    into an anonymous remainder, so the description says how MANY cells
    it covered and never which form they took. The remainder is written
    in the plain style, and this count is what tells the placement which
    part of the plain quota is a NAMED published count and which part is
    the pool standing in for forms the description withheld.
    """
    for name in sorted(styles):
        if name == contract.WITHHELD:
            return styles[name]
    return 0


def _whole_demand(facts: contract.NumericFacts) -> int:
    """How many cells the published map asks to be written point-free."""
    quotas = _style_quotas(facts.numeric_styles)
    owed = 0
    for name in _WHOLE_STYLES:
        owed = owed + quotas[name]
    return owed


def _style_for(
    left: "dict[str, int]",
    pool: int,
    carries: bool,
    negative: bool,
    room: int,
    plus_room: int,
) -> str:
    """The style one cell takes, by largest remaining quota (G6.4).

    Largest remaining rather than a block per style, and the reason is
    fidelity: a block would put every exponent-styled cell at one end of
    the distribution, so a reader of the twin would find the way a
    number is written tied to its size where the real column had no such
    pattern. Ties are broken by the enumeration order.

    TWO THINGS NARROW THE CHOICE, and both are what make the published
    map reachable rather than merely aimed at (review item P2-C2-F2).
    First, a style is offered only where the finished TEXT would read
    back as that style: `leading_plus` needs a value that is not
    negative, and the three point-free styles need a value that can be
    written without a point. Second, a choice that would leave a later
    quota unplaceable is passed over: ``room`` is how many cells after
    this one can wear a point-free style and ``plus_room`` how many of
    those are not negative, so a cell that is one of the last that can
    carry such a style takes one rather than spending itself on a form
    any cell could have worn. Together those two make every
    producer-feasible style map come out exactly.

    THE ANONYMOUS POOL GIVES WAY BEFORE A NAMED COUNT DOES (review item
    P2-C4-F3). ``pool`` is how many of the plain quota still standing
    are the held-back remainder rather than a NAMED published count. A
    description that pools a form below the floor says how many cells it
    covered and never which form they took, so the pool is the claim
    that yields where the point-free cells cannot carry every quota.
    That gives the look-ahead four answers rather than two, and they are
    tried in this order: the choice that keeps EVERY quota placeable,
    the pool included; then, where none does, the choice that keeps
    every NAMED quota placeable; then -- since being here means the
    point-free counts cannot all be placed however the rest of the
    column goes -- a point-free style on every cell that can wear one,
    because a carrier spent on a form any cell could have worn makes the
    shortfall one worse than the column's own values force; and only
    then the largest remaining quota this cell can wear at all. The
    recount of `_style_notes` names whatever the last two answers cost.

    AND THE POOL IS OFFERED TO A CELL THAT CANNOT BE WRITTEN PLAINLY,
    where it is spelled canonically instead (Phase 3 plan P3-D8.1,
    closing the open defect the registry held under P2-C5-F3). The
    remainder used to be placeable only on a cell with a point-free
    spelling, because contract 7.5.7 wrote every pooled cell `plain`;
    a column whose published `min` or `max` carries a point has a cell
    that cannot be plain, so the remainder came out short by that cell
    and the twin missed a published total it could have met. A pooled
    cell has no published form -- that is what pooling MEANS -- so
    nothing is owed by writing it in its own value's canonical text,
    and `_styled_number` already does exactly that: `_point_free` hands
    the canonical spelling back where no point-free one exists. The
    named counts are untouched, because the offer is made only while
    the pool is still standing and the look-ahead's second answer keeps
    every NAMED quota placeable on the carriers that remain.

    THE OFFER IS MADE ONLY WHERE THE CARRIERS ARE ALREADY SHORT, which
    is what keeps the repair to the shape it was taken for. A column
    whose point-free claims still fit on the cells that can wear them
    is placed exactly as it was before the repair, byte for byte; the
    offer opens only once the claims standing outnumber the carriers
    left, and then it is the pool -- never a named count -- that moves
    onto a cell spelling itself canonically.
    """
    best = ""
    saved = ""
    carrier = ""
    kept = ""
    demand = 0
    for name in _WHOLE_STYLES:
        demand = demand + left[name]
    crowded = demand > room
    for name in contract.NUMERIC_STYLES:
        if left[name] <= 0:
            continue
        pooled_plain = name == "plain" and pool > 0 and crowded
        if name in _WHOLE_STYLES and not carries and not pooled_plain:
            continue
        if name == "leading_plus" and negative:
            continue
        if not kept or left[name] > left[kept]:
            kept = name
        if (
            name in _WHOLE_STYLES
            and carries
            and (not carrier or left[name] > left[carrier])
        ):
            carrier = name
        owed = 0
        for other in _WHOLE_STYLES:
            owed = owed + left[other]
        spent = 1 if name == "plain" and pool > 0 else 0
        if name in _WHOLE_STYLES:
            owed = owed - 1
        owed_plus = left["leading_plus"]
        if name == "leading_plus":
            owed_plus = owed_plus - 1
        if owed_plus > plus_room:
            continue
        if owed - (pool - spent) <= room and (
            not saved or left[name] > left[saved]
        ):
            saved = name
        if owed > room:
            continue
        if not best or left[name] > left[best]:
            best = name
    if best:
        return best
    if saved:
        return saved
    if carrier:
        return carrier
    if kept:
        return kept
    if carries:
        return "plain"
    return "decimal"


def _style_places(
    quotas: "dict[str, int]",
    holds: "list[float]",
    whole_column: bool,
    pool: int = 0,
) -> "list[str]":
    """The style of every numeric cell, in stratum order (method G6.4).

    Decided over the whole column rather than one cell at a time,
    because whether a quota can still be placed depends on how many
    cells that can wear it are still to come. ``pool`` is the held-back
    remainder inside the plain quota, which is served after every named
    count (review item P2-C4-F3).
    """
    total = len(holds)
    carries = [
        _carries_plainly(holds[place], whole_column) for place in range(total)
    ]
    room = [0 for _each in range(total + 1)]
    plus_room = [0 for _each in range(total + 1)]
    for place in range(total - 1, -1, -1):
        step = 1 if carries[place] else 0
        room[place] = room[place + 1] + step
        plus_room[place] = plus_room[place + 1] + (
            step if holds[place] >= 0.0 else 0
        )
    left = {name: quotas[name] for name in contract.NUMERIC_STYLES}
    held = min(max(pool, 0), left["plain"])
    styles: list[str] = []
    for place in range(total):
        picked = _style_for(
            left,
            held,
            carries[place],
            holds[place] < 0.0,
            room[place + 1],
            plus_room[place + 1],
        )
        left[picked] = left[picked] - 1
        if picked == "plain" and held > 0:
            held = held - 1
        styles = styles + [picked]
    return styles


# -- dates and times (method G7) --------------------------------------


def _ordinal_of(canonical: str, resolution: str) -> int:
    """One published instant as a whole number (method G7.1).

    The unit is fixed by the resolution: one day for a date, one second
    for a date and time, one quarter for a quarter. All datetime
    arithmetic in this module is whole-number arithmetic in this space,
    so no floating-point value is formed anywhere near a calendar.
    """
    if resolution == "quarter":
        return 4 * (int(canonical[0:4]) - 1970) + int(canonical[6]) - 1
    if resolution == "month":
        # TWELVE MONTHS TO THE YEAR, counted from the same origin the
        # quarter counts from, so a month is a whole number of months
        # and no calendar is consulted to place it (plan P4-D4.3).
        return 12 * (int(canonical[0:4]) - 1970) + int(canonical[5:7]) - 1
    days = parsing.days_from_civil(
        int(canonical[0:4]), int(canonical[5:7]), int(canonical[8:10])
    )
    if resolution == "date":
        return days
    return (
        86400 * days
        + 3600 * int(canonical[11:13])
        + 60 * int(canonical[14:16])
        + int(canonical[17:19])
    )


def _cell_of_ordinal(
    ordinal: int, resolution: str, precision: str, figures: int
) -> str:
    """One instant written at the precision the description records (G7.5).

    Owner decision 5: a twin datetime cell is written in the ISO form
    matching the precision the description records, so the twin
    re-profiles to the same precision and the same offset state. The
    separator is `T`, because the parser accepts three and the bytes
    have to be fixed. The figures after the second are zeros: the
    description says how MANY the finest cell carried and nothing about
    their values, so any other figure would be a made-up fact.
    """
    if resolution == "quarter":
        year = 1970 + (ordinal // 4)
        return f"{year:04d}-Q{(ordinal % 4) + 1}"
    if resolution == "month":
        year = 1970 + (ordinal // 12)
        return f"{year:04d}-{(ordinal % 12) + 1:02d}"
    if resolution == "date":
        year, month, day = parsing.civil_from_days(ordinal)
        return f"{year:04d}-{month:02d}-{day:02d}"
    days = ordinal // 86400
    rest = ordinal - days * 86400
    year, month, day = parsing.civil_from_days(days)
    hours = rest // 3600
    minutes = (rest - hours * 3600) // 60
    seconds = rest - hours * 3600 - minutes * 60
    stamp = f"{year:04d}-{month:02d}-{day:02d}T{hours:02d}:{minutes:02d}"
    if precision == "minute":
        return stamp
    stamp = f"{stamp}:{seconds:02d}"
    if precision == "subsecond":
        return f"{stamp}.{'0' * figures}"
    return stamp


def _endpoint_cell(
    facts: contract.DatetimeFacts, published: str, offset: str
) -> str:
    """One END of a column of dates, from the published fields (G7.5).

    The method pins the first and last ranks to `earliest` and `latest`
    "used exactly as published", and this is what makes that literal.
    Ranks between them travel through the whole-number space of G7.1,
    which gives back every instant that space has a place for. It has no
    place for one a real reader still accepts and a description may
    therefore carry: the last second of a leap minute, a seconds field
    of 60, which the profile contract admits at 6.6.2 for that reason.
    Sending an end through the space wrote the following minute instead
    and reported the loss; taking the end's own fields keeps it, so both
    ends stay exact facts as the ratified plan requires (review item
    P2-C2-F5).

    For a seconds field of 00 through 59 this returns exactly the text
    the ordinal route returns, so no other cell and no frozen vector
    moves.

    THERE IS NO CASE HERE THAT DECLINES (review item P2-C3-F2). An
    earlier revision returned nothing for a sixtieth second published on
    the shared clock, so the caller wrote the ordinal cell -- the
    following minute -- and the report named the end as a loss. That is
    an exception to a fact both specifications call exact with none, and
    the description carrying it is now refused where it is decided, by
    the contract's D10, along with the one recording whole minutes whose
    end carries seconds. Both ends are written from their own published
    fields on both clocks.

    Guarantees: accepts loaded datetime facts, a published canonical
    instant and the offset allocated to that cell; returns the cell
    text; whole-number arithmetic only. No I/O of any kind.
    """
    if facts.resolution != "datetime":
        # A whole date and a quarter ARE their canonical text, and the
        # ordinal route already gives it back character for character.
        return published
    seconds = published[17:19]
    minute = _ordinal_of(f"{published[0:17]}00", "datetime")
    if facts.datetimes_read_at == "utc":
        # A cell carrying an offset is written on that offset's own wall
        # clock (G7.4). Every offset is a whole number of minutes, so
        # the move cannot disturb the seconds field, and a 60 survives
        # it on this clock exactly as it does on the local one.
        minute = minute + _offset_seconds(offset)
    stamp = _cell_of_ordinal(minute, "datetime", "minute", 0)
    if facts.time_precision == "minute":
        # A cell written to the minute has no seconds field. D10 admits
        # this precision only where both ends carry a seconds field of
        # 00, so the cut drops nothing the description published.
        return stamp
    stamp = f"{stamp}:{seconds}"
    if facts.time_precision == "subsecond":
        return f"{stamp}.{'0' * facts.subsecond_digits}"
    return stamp


def _offset_seconds(offset: str) -> int:
    """How far one offset stands from UTC, in whole seconds."""
    if offset == "Z" or not offset:
        return 0
    if offset == contract.NO_OFFSET or offset == contract.WITHHELD:
        return 0
    seconds = 3600 * int(offset[1:3]) + 60 * int(offset[4:6])
    if offset[0] == "-":
        return -seconds
    return seconds


def _is_real_offset(offset: str) -> bool:
    """True when this key names an offset a cell can actually carry."""
    return offset != contract.NO_OFFSET and offset != contract.WITHHELD


# -- made-up spellings, class by class (method G10.3) ------------------


# A column's record of what it has already written says two DIFFERENT
# things about one piece of text, and keeping them apart is what makes a
# fold collision buildable at all. `_WRITTEN` says the text has been
# written as a value of this column. `_FOLDED_ONTO` says some value of
# this column comes down to that text once case and edge spacing are
# ignored. An ordinary made-up value has to be new in BOTH senses. The
# fold-collision partner of method G9.3 -- a case flip, edge spacing,
# or both -- is the one construction that is new only in the first: folding onto a value already there is its whole
# purpose, so a record that could not tell the two apart could never
# build one, and the published folded count would be missed on every
# column that publishes one below its raw count.
_WRITTEN = 1
_FOLDED_ONTO = 2


def _recorded(candidate: str, used: "dict[str, int]") -> int:
    """In which of the two senses this piece of text is already spoken for."""
    if candidate not in used:
        return 0
    return used[candidate]


def _unused(candidate: str, used: "dict[str, int]") -> bool:
    """True when this exact spelling has not been written in this column."""
    return _recorded(candidate, used) & _WRITTEN == 0


def _take(candidate: str, used: "dict[str, int]") -> str:
    """Record a spelling as written in this column, and hand it back.

    Only the spelling itself is recorded, not the identity it folds
    onto: this is how a fold-collision partner is written, and a partner
    is meant to share its identity with the value it varies.
    """
    used[candidate] = _recorded(candidate, used) | _WRITTEN
    return candidate


def _free(candidate: str, used: "dict[str, int]") -> bool:
    """True when neither this spelling nor its folded identity is used.

    The made-up roles have to reach a published count of DIFFERENT
    spellings and a published count of different FOLDED identities, so
    an ordinary made-up value has to be new in both senses. The one
    construction that is allowed to fold onto something already there is
    the fold-collision partner of method G9.3, which asks the raw
    question on its own.
    """
    return _unused(candidate, used) and (
        _recorded(parsing.folded(candidate), used) & _FOLDED_ONTO == 0
    )


def _claim(candidate: str, used: "dict[str, int]") -> str:
    """Record a spelling and its folded identity as used, and hand it back."""
    used[candidate] = _recorded(candidate, used) | _WRITTEN
    identity = parsing.folded(candidate)
    used[identity] = _recorded(identity, used) | _FOLDED_ONTO
    return candidate


def _out_of_range_spelling(order: int, negative: bool) -> str:
    """A well-formed number too large to hold (method G10.3).

    `1e999`, `2e999`, `3e999` and so on, with a leading minus for a
    negative one. The description does not say, on a column of numbers,
    how the out-of-range cells split between too large and too small, so
    every one of them is written too LARGE and the report names that.
    """
    lead = "-" if negative else ""
    return f"{lead}{order}e999"


def _contradictory_spelling(order: int) -> str:
    """A sign inside accounting parentheses (method G10.3).

    Numeric notation whose meaning conflicts with itself: `(-1)` says
    negative twice. It carries neither a sign nor whole-number status --
    the shipped parser answers "unknown" for both and never guesses --
    so cells like these account for exactly the counts of unknown sign
    and unknown whole-number status wherever those are published.
    """
    return f"(-{order})"


def _text_spelling(
    order: int, used: "dict[str, int]", holes: "tuple[str, ...]"
) -> str:
    """Ordinary text that reads as no number and no date (G10.3, G10.4).

    `text-1`, `text-2` and so on, stepped past any spelling that means
    "no value", any spelling already used in this column, any spelling
    that would read as a date under one of the formats the profiler
    tries, and any spelling THIS COLUMN publishes among its absent
    cells -- so a stand-in can never quietly change a count.

    THE LAST OF THOSE FOUR WAS MISSING, and the argument that every
    invention site guards itself was false because of it (review item
    P4-DATE3-F3). A column publishing `missing_by_source {"text-1":
    11}` got `text-1` invented for its one ordinary-text stand-in, and
    describing the twin again then found twelve absent cells and no
    unparsed one -- an EXACT-OBSERVABLE count gone, with the class-
    preserving construction the method promises already broken by the
    time any recount could name it. Asking here rather than at each
    caller is what makes the guard total.
    """
    step = order
    while True:
        candidate = f"text-{step}"
        if (
            not _is_a_hole_spelling(candidate, holes)
            and _unused(candidate, used)
            and not _reads_as_a_date(candidate)
        ):
            return candidate
        step = step + 1


def _reads_as_a_date(candidate: str) -> bool:
    """True when any format the profiler tries would read this as a date."""
    for name in parsing.DATE_FORMATS:
        if parsing.parse_datetime(candidate, name) is not None:
            return True
    return False


def _class_spellings(
    kind: str,
    count: int,
    folded_budget: int,
    raw_budget: int,
    negatives: int,
    used: "dict[str, int]",
    holes: "tuple[str, ...]",
) -> "list[str]":
    """Every cell of one straggler class, in one fixed order (G10.3).

    Distinctness inside a class is supplied by stepping the order on
    from one; the budget of method G6.5 says how many different
    spellings the class may use, and a class that has spent its budget
    repeats its last spelling. A class whose raw budget is above its
    folded budget spends the difference on case variants, which is the
    only construction that adds a spelling without adding a folded
    identity.
    """
    cells: list[str] = []
    order = 0
    made: list[str] = []
    extra: list[str] = []
    steps: dict[str, int] = {}
    last: dict[str, str] = {}
    for place in range(count):
        negative = place < negatives
        side = "-" if negative else "+"
        room = len(made) < folded_budget or side not in last
        if room:
            order = order + 1
            spelling = _base_spelling(kind, order, negative, used, holes)
            made = made + [spelling]
            _take(spelling, used)
        elif len(made) + len(extra) < raw_budget:
            candidate = _first_variant(made, steps, used)
            if candidate is None:
                spelling = last[side]
            else:
                extra = extra + [candidate]
                _take(candidate, used)
                spelling = candidate
        else:
            spelling = last[side]
        last[side] = spelling
        cells = cells + [spelling]
    return cells


def _base_spelling(
    kind: str,
    order: int,
    negative: bool,
    used: "dict[str, int]",
    holes: "tuple[str, ...]",
) -> str:
    """The ``order``-th base spelling of one straggler class."""
    if kind == _CLASS_OUT_OF_RANGE:
        return _out_of_range_spelling(order, negative)
    if kind == _CLASS_CONTRADICTORY:
        return _contradictory_spelling(order)
    return _text_spelling(order, used, holes)


def _first_variant(
    made: "list[str]",
    steps: "dict[str, int]",
    used: "dict[str, int]",
) -> "str | None":
    """The next case variant of a spelling this class already used.

    Spellings are tried in the order they were made, and each supplies
    its variants in the order of method G8.2, so two implementations
    build the same list. None says the class holds no letter anywhere
    and can supply no variant at all -- which is true of accounting
    parentheses -- and the caller names the shortfall.
    """
    for spelling in made:
        step = 0
        if spelling in steps:
            step = steps[spelling]
        while step < 4096:
            step = step + 1
            candidate = _case_variant(spelling, step)
            if candidate is None:
                break
            if _unused(candidate, used):
                steps[spelling] = step
                return candidate
        steps[spelling] = step
    return None


# -- columns of numbers (method G5, G6) -------------------------------


def _band_sizes(
    negatives: int,
    zeros: int,
    positives: int,
    negative_strata: int,
    positive_strata: int,
) -> "tuple[list[int], list[str]]":
    """The even split of method G5.2, band by band.

    Negatives ascending, then the zero stratum, then positives
    ascending, because that is the sorted order of the column's own
    values and the ladder is a statement about sorted order.
    """
    sizes: list[int] = []
    bands: list[str] = []
    for step in range(negative_strata):
        sizes = sizes + [
            (step + 1) * negatives // negative_strata
            - step * negatives // negative_strata
        ]
        bands = bands + [_BAND_NEGATIVE]
    if zeros > 0:
        sizes = sizes + [zeros]
        bands = bands + [_BAND_ZERO]
    for step in range(positive_strata):
        sizes = sizes + [
            (step + 1) * positives // positive_strata
            - step * positives // positive_strata
        ]
        bands = bands + [_BAND_POSITIVE]
    return sizes, bands


def _carrier_flags(
    sizes: "list[int]",
    bands: "list[str]",
    rungs: "tuple[float, ...] | None",
    whole_column: bool,
) -> "list[bool]":
    """Which strata can hold a value with no point (method G5.2).

    A cell can wear `plain`, `leading_zero` or `leading_plus` only where
    the value it holds has a point-free spelling, so how many such cells
    a column HAS is decided by the strata, before any style is chosen.
    Three answers, and each is fixed by a published fact rather than by
    a drawn value:

    - the zero stratum holds exactly `0`, which is point-free;
    - a pinned end holds the published `min` or `max` exactly, so it can
      carry a point-free style exactly when that published number has a
      point-free spelling -- and when the ladder holds nothing anywhere,
      the sign fallback of G5.5 puts a whole number there;
    - every other stratum can, because the values step of G6.4 may take
      it to the nearest whole number.

    The last answer is a plan rather than a certainty: the values step
    leaves a stratum alone where the whole number it would take is
    already another stratum's or would cross zero. Those two guards
    protect facts that are themselves EXACT-OBSERVABLE, so the plan is
    made optimistically and `_style_notes` recounts what was written.
    """
    total = len(sizes)
    flags: list[bool] = []
    for place in range(total):
        if bands[place] == _BAND_ZERO:
            flags = flags + [True]
            continue
        pinned = place == 0 or (place == total - 1 and total >= 2)
        if not pinned or rungs is None:
            flags = flags + [True]
            continue
        end = rungs[0] if place == 0 else rungs[10]
        flags = flags + [_carries_plainly(end, whole_column)]
    return flags


_REACHABLE = (
    (_BAND_ZERO, _BAND_POSITIVE),
    (_BAND_NEGATIVE, _BAND_ZERO, _BAND_POSITIVE),
)


def _carrier_room(
    sizes: "list[int]",
    bands: "list[str]",
    flags: "list[bool]",
    reachable: "tuple[str, ...]",
) -> int:
    """The most cells the strata that can carry could ever cover (G5.2).

    A band with no stratum that can carry a point-free value offers
    nothing at all, because cells never cross a sign band. A band that
    has one offers every cell it holds except the one each of its other
    strata must keep, since no stratum may be emptied. `reachable` is
    which bands the demand can be written in: every band for the
    point-free demand, and the two that are not negative for the
    `leading_plus` share, because there is no leading-plus spelling of a
    negative value. This is the ceiling the cell step reaches for, and
    it is also what tells the band step whether moving a stratum would
    raise it.
    """
    room = 0
    for band in reachable:
        holds = [
            place for place in range(len(sizes)) if bands[place] == band
        ]
        if not [place for place in holds if flags[place]]:
            continue
        for place in holds:
            room = room + (
                sizes[place] if flags[place] else sizes[place] - 1
            )
    return room


def _carrier_bands(
    negatives: int,
    zeros: int,
    positives: int,
    negative_strata: int,
    positive_strata: int,
    rungs: "tuple[float, ...] | None",
    whole_column: bool,
    demand: int,
    plus_demand: int,
) -> "tuple[int, int]":
    """Give a sign band a stratum that can carry, where it has none.

    THE SECOND HALF OF THE CARRIER STEP (review item P2-C4-F3). How the
    different values divide between the negative and the positive side
    is no more published than how many cells each holds: G5.2 shares
    them out in proportion to the cells, which is this method's own
    default. A band left with ONE stratum, where that stratum is a
    pinned end whose published rung carries a point, can then carry no
    point-free cell at all -- and every cell of that band is stuck on
    it. A 58-cell column publishing forty-one `leading_zero` cells and
    a `min` of `-45.5` put ten cells there and missed two NAMED counts.

    So one stratum moves into such a band from the other divided band,
    the negative side considered first, and only where the other band
    keeps at least one and the move actually raises the ceiling of
    `_carrier_room`. `S`, the zero stratum and the sign counts are
    untouched: both bands keep a stratum, so the zero stratum stays
    where it was in the order and the draw budget of G4.3 is unchanged.
    """
    pair = (negative_strata, positive_strata)
    for wanted, reachable in ((plus_demand, _REACHABLE[0]), (demand, _REACHABLE[1])):
        for step in range(2):
            sizes, bands = _band_sizes(
                negatives, zeros, positives, pair[0], pair[1]
            )
            flags = _carrier_flags(sizes, bands, rungs, whole_column)
            room = _carrier_room(sizes, bands, flags, reachable)
            if room >= wanted:
                break
            moved = pair
            if step == 0 and negatives > 0 and pair[1] >= 2:
                moved = (pair[0] + 1, pair[1] - 1)
            if step == 1 and positives > 0 and pair[0] >= 2:
                moved = (pair[0] - 1, pair[1] + 1)
            if moved == pair:
                continue
            other, other_bands = _band_sizes(
                negatives, zeros, positives, moved[0], moved[1]
            )
            other_flags = _carrier_flags(
                other, other_bands, rungs, whole_column
            )
            if _carrier_room(other, other_bands, other_flags, reachable) > room:
                pair = moved
    return pair


def _carrier_sizes(
    sizes: "list[int]",
    bands: "list[str]",
    flags: "list[bool]",
    demand: int,
    plus_demand: int,
) -> "list[int]":
    """Divide the cells so the published point-free counts can be WRITTEN.

    THE STRATUM SIZES ARE THE TWIN'S OWN CHOICE, AND A PUBLISHED COUNT
    OUTRANKS THEM (review item P2-C4-F3). Nothing in a numeric block
    says how many cells hold each different value -- there is no
    multiplicity map on `count` or `continuous` -- so the even split of
    G5.2 is a default, not a published fact. `numeric_styles` IS a
    published fact, and an EXACT-OBSERVABLE one. Where the even split
    leaves the strata that can hold a point-free value covering fewer
    cells than the map asks to be written that way, the split is the
    thing that gives: cells move into those strata until the count fits.
    Plan P2-D6's feasibility rule 4 fixes that order -- published counts
    take precedence over ladder conformance where the conflict is
    otherwise resolvable -- and the cost is paid in the open, because
    G5.6's rung envelope is derived from the widest stratum and widens
    by exactly what this step spends.

    Two rules bound the move, and both protect facts of their own:

    - cells move only WITHIN a sign band, so `n_zero` and `n_negative`
      are exactly what they were;
    - no stratum is emptied, so the count of different values is exactly
      what it was.

    The `leading_plus` share is settled first and only over the bands
    that are not negative, because there is no leading-plus spelling of
    a negative value. The fewest cells the two demands need are moved,
    taken from the strata that cannot carry a point-free value in
    ascending order and shared out over those that can by the same even
    split G5.2 uses everywhere else.
    """
    moved = [size for size in sizes]
    total = len(moved)
    for wanted, reachable in (
        (plus_demand, _REACHABLE[0]),
        (demand, _REACHABLE[1]),
    ):
        room = 0
        for place in range(total):
            if flags[place] and bands[place] in reachable:
                room = room + moved[place]
        short = wanted - room
        for band in reachable:
            if short <= 0:
                break
            takers = [
                place
                for place in range(total)
                if flags[place] and bands[place] == band
            ]
            givers = [
                place
                for place in range(total)
                if not flags[place] and bands[place] == band
            ]
            if not takers or not givers:
                continue
            spare = 0
            for place in givers:
                spare = spare + moved[place] - 1
            take = min(short, spare)
            if take <= 0:
                continue
            short = short - take
            left = take
            for place in givers:
                step = min(moved[place] - 1, left)
                moved[place] = moved[place] - step
                left = left - step
            for step in range(len(takers)):
                moved[takers[step]] = moved[takers[step]] + (
                    (step + 1) * take // len(takers)
                    - step * take // len(takers)
                )
    return moved


# THE LARGEST WHOLE NUMBER A POINT-FREE SPELLING REACHES. Method G6.2
# writes the shortest round trip in fixed-point notation up to `1e+16`
# and in exponent notation above it, so a value at or beyond that has no
# spelling free of a point or an exponent however whole it is. The reach
# step below never offers a stratum a whole number outside this bound,
# because such a number buys no style at all.
_PLAIN_LIMIT = 10 ** 16 - 1

# HOW FAR OUTSIDE ITS OWN SHARE A STRATUM MAY REACH FOR A WHOLE NUMBER.
# The nearest whole number to any value inside a share is at most this
# far outside it, and method G12.2 widens the rung window by exactly
# this much for every column the values step of G6.4 can touch. Every
# candidate of that step is held to the same distance, so the window
# covers one rule rather than two.
_HALF_UNIT = 0.5


def _starts_of(sizes: "list[int]") -> "list[int]":
    """The rank the cells of every stratum begin at."""
    starts: list[int] = []
    running = 0
    for size in sizes:
        starts = starts + [running]
        running = running + size
    return starts


def _totalled(sizes: "list[int]") -> int:
    """How many cells a list of stratum sizes covers."""
    counted = 0
    for size in sizes:
        counted = counted + size
    return counted


def _ceiling_of(value: float) -> int:
    """The smallest whole number at or above ``value``.

    Written out in first-party arithmetic rather than taken from the
    library, because the offline policy (plan P2-D13) enumerates the
    library names this product may use one at a time and this is not one
    of them. Truncation toward zero is exact for every finite binary64,
    and one comparison turns it into the direction wanted.
    """
    below = int(value)
    if float(below) < value:
        return below + 1
    return below


def _floor_of(value: float) -> int:
    """The largest whole number at or below ``value``."""
    below = int(value)
    if float(below) > value:
        return below - 1
    return below


def _free_whole(
    low: float,
    high: float,
    band: str,
    rungs: "tuple[float, ...]",
    held: "dict[float, int]",
    reach: int,
    nearest: bool,
) -> "float | None":
    """A whole number this share can hold that no stratum holds already.

    THE SAME THREE RULES `_whole_inside` OBEYS, asked before the values
    are drawn rather than after (method G5.2's reach step, review item
    P2-C5-F3). A candidate stays inside the stratum's own sign band, so
    `n_zero` and `n_negative` are untouched; it stays inside the
    published `min` and `max`, which are EXACT-OBSERVABLE; and it is
    never a number another stratum holds, so the count of different
    values does not fall. It must also HAVE a point-free spelling, which
    is what `_PLAIN_LIMIT` bounds.

    ``nearest`` asks the two questions this is put to in their own
    order. Asking whether ONE stratum can carry, the candidates are
    offered outward from the middle of its own share, because that is
    where a drawn value sits on average and `_whole_inside` takes the
    nearest whole number to the value it was handed -- so two strata
    sharing a boundary do not each claim the other's number. Asking
    which whole number a band can REACH, they are offered in ascending
    distance from zero, which is where the ladder's own steps are
    closest together and so where the narrowest window lies.

    The walk is bounded and the bound is stated: at most one candidate
    per value already held can be refused, so ``reach`` steps out from
    the starting point settle the question.
    """
    lowest = max(low, float(rungs[0]))
    highest = min(high, float(rungs[10]))
    if band == _BAND_POSITIVE:
        lowest = max(lowest, 1.0)
    if band == _BAND_NEGATIVE:
        highest = min(highest, -1.0)
    if not math.isfinite(lowest) or not math.isfinite(highest):
        return None
    lowest = max(lowest, -float(_PLAIN_LIMIT))
    highest = min(highest, float(_PLAIN_LIMIT))
    first = max(_ceiling_of(lowest), -_PLAIN_LIMIT)
    last = min(_floor_of(highest), _PLAIN_LIMIT)
    if first > last:
        return None
    steps = max(reach, 1)
    candidates: list[int] = []
    if nearest:
        middle = _ceiling_of(lowest + (highest - lowest) / 2)
        middle = max(first, min(last, middle))
        for step in range(steps + 1):
            if step == 0:
                candidates = candidates + [middle]
                continue
            candidates = candidates + [middle + step, middle - step]
    elif band == _BAND_NEGATIVE:
        for step in range(steps + 1):
            candidates = candidates + [last - step]
    else:
        for step in range(steps + 1):
            candidates = candidates + [first + step]
    for number in candidates:
        if number < first or number > last:
            continue
        value = float(number)
        if value in held or not _carries_plainly(value, False):
            continue
        return value
    return None


def _reach_held(
    sizes: "list[int]",
    bands: "list[str]",
    rungs: "tuple[float, ...]",
    whole_column: bool,
    numbers: int,
) -> "tuple[list[bool], dict[float, int]]":
    """Which strata can REALLY hold a point-free value, and what they hold.

    `_carrier_flags` answers the same question optimistically -- every
    stratum that is neither a pinned end nor the zero stratum "can,
    because the values step may take it to the nearest whole number".
    That is a plan, and on a crowded ladder it is a plan that does not
    come true: four different values between `0.125` and `1` leave their
    strata one whole number between them, so four strata are counted as
    carriers and one of them carries (review item P2-C5-F3). The cell
    step then moved no cell, because by its own count there was nothing
    to fix, and a producer's own 82-cell column published 34 point-free
    cells while the twin wrote 20.

    So this asks the LADDER. Each stratum is offered the whole numbers
    of its own share of the published ladder, in the order
    `_whole_inside` may take them and under the same three rules, and a
    stratum that finds one holds it -- which is what stops two strata of
    one flat rung from both being counted for the single whole number
    that rung reaches.

    TWO VALUES ARE RESERVED BEFORE THE WALK BEGINS. G5.5 repairs a
    stratum whose drawn value falls on the wrong side of its own band
    onto that band's fallback, and which side a value falls on is a
    function of the seed. A stratum whose share crosses its own band's
    sign may therefore arrive holding that fallback, so the fallback is
    treated as spoken for on every seed rather than on some of them; a
    sizing that depended on the seed would put the twin's own byte
    stream at the mercy of a draw that has not happened yet.
    """
    total = len(sizes)
    starts = _starts_of(sizes)
    held: dict[float, int] = {}
    for place in range(total):
        band = bands[place]
        pinned = place == 0 or (place == total - 1 and total >= 2)
        if pinned or band == _BAND_ZERO:
            continue
        low = _interpolated(rungs, starts[place], numbers)
        high = _interpolated(rungs, starts[place] + sizes[place], numbers)
        crosses = band == _BAND_POSITIVE and low <= 0.0
        crosses = crosses or (band == _BAND_NEGATIVE and high >= 0.0)
        if not crosses:
            continue
        fallback = _sign_fallback(band, rungs)
        if band == _BAND_NEGATIVE and fallback >= 0.0:
            fallback = -1.0
        if band == _BAND_POSITIVE and fallback <= 0.0:
            fallback = 1.0
        if whole_column:
            fallback = _whole_valued(fallback)
        if _carries_plainly(fallback, False):
            held[fallback] = 1
    # A STRATUM WHOLLY INSIDE A FLAT RUNG HOLDS THAT RUNG'S NUMBER, AND
    # HOLDS IT FIRST. Where the published ladder does not move across a
    # stratum's whole share, the interpolation of G5.3 hands that
    # stratum exactly the one value the share holds, whatever word was
    # drawn -- so if that value is a whole number the stratum is already
    # a carrier before the walk below asks anybody. Letting the walk
    # decide in stratum order instead gave the number to an EARLIER
    # stratum whose share only touched the flat rung, and at run time
    # the flat stratum took it anyway and the earlier one came back with
    # nothing: a 78-cell producer column published 39 point-free cells
    # and wrote 36 on five of eight seeds while the sizing believed all
    # 39 were placed.
    settled: dict[int, int] = {}
    for place in range(total):
        band = bands[place]
        pinned = place == 0 or (place == total - 1 and total >= 2)
        if pinned or band == _BAND_ZERO:
            continue
        low = _interpolated(rungs, starts[place], numbers)
        high = _interpolated(rungs, starts[place] + sizes[place], numbers)
        if low != high or low in held:
            continue
        if band == _BAND_POSITIVE and low <= 0.0:
            continue
        if band == _BAND_NEGATIVE and low >= 0.0:
            continue
        if not _carries_plainly(low, whole_column):
            continue
        held[low] = 1
        settled[place] = 1
    flags: list[bool] = []
    for place in range(total):
        band = bands[place]
        pinned = place == 0 or (place == total - 1 and total >= 2)
        if band == _BAND_ZERO:
            held[0.0] = 1
            flags = flags + [True]
            continue
        if pinned:
            end = rungs[0] if place == 0 else rungs[10]
            held[end] = 1
            flags = flags + [_carries_plainly(end, whole_column)]
            continue
        if place in settled:
            flags = flags + [True]
            continue
        low = _interpolated(rungs, starts[place], numbers)
        high = _interpolated(rungs, starts[place] + sizes[place], numbers)
        want = _free_whole(low, high, band, rungs, held, total + 1, True)
        if want is None:
            flags = flags + [False]
            continue
        held[want] = 1
        flags = flags + [True]
    return flags, held


def _reach_met(
    sizes: "list[int]",
    bands: "list[str]",
    flags: "list[bool]",
    demand: int,
    plus_demand: int,
) -> bool:
    """True when the strata that really carry cover both demands."""
    for wanted, reachable in (
        (plus_demand, _REACHABLE[0]),
        (demand, _REACHABLE[1]),
    ):
        covered = 0
        for place in range(len(sizes)):
            if flags[place] and bands[place] in reachable:
                covered = covered + sizes[place]
        if covered < wanted:
            return False
    return True


def _reach_rank(
    rungs: "tuple[float, ...]", numbers: int, value: float, upper: bool
) -> int:
    """The cell rank at which the published ladder reaches ``value``.

    ``upper`` asks for the FIRST rank whose ladder value is at or above
    ``value``; otherwise the LAST rank whose ladder value is at or below
    it. The ladder never decreases, so both are found by halving the
    range rather than by walking it, which keeps the cost of the reach
    step logarithmic in a column's own row count.
    """
    low = 0
    high = numbers
    if upper:
        while low < high:
            middle = (low + high) // 2
            if _interpolated(rungs, middle, numbers) >= value:
                high = middle
            else:
                low = middle + 1
        return low
    while low < high:
        middle = (low + high + 1) // 2
        if _interpolated(rungs, middle, numbers) <= value:
            low = middle
        else:
            high = middle - 1
    return low


def _reach_window(
    rungs: "tuple[float, ...]",
    numbers: int,
    band: str,
    held: "dict[float, int]",
    floor: int,
    ceiling: int,
    reach: int,
) -> "tuple[int, int] | None":
    """The fewest cells of the ladder that hold a whole number of their own.

    A stratum's share is the piece of the published ladder its own cells
    cover, so which whole numbers it can take is decided by WHERE its
    cells sit, not only by how many there are. This finds the narrowest
    window inside ``floor`` and ``ceiling`` that reaches a whole number
    no other stratum holds; the caller then widens it to the cells the
    published count still needs.

    Candidates are offered from both ends of the reachable value range,
    in `_free_whole`'s own order, and the narrowest window wins with
    ties going to the earliest candidate -- so two implementations
    choose the same window from the same description.
    """
    if floor >= ceiling:
        return None
    lowest = _interpolated(rungs, floor, numbers)
    highest = _interpolated(rungs, ceiling, numbers)
    seen: dict[float, int] = {name: 1 for name in held}
    best: tuple[int, int, int] | None = None
    for _step in range(max(reach, 1)):
        found = _free_whole(
            lowest, highest, band, rungs, seen, reach, False
        )
        if found is None:
            break
        seen[found] = 1
        low = max(_reach_rank(rungs, numbers, found, False), floor)
        high = min(_reach_rank(rungs, numbers, found, True), ceiling)
        low = min(low, ceiling)
        high = max(high, floor)
        if low > high:
            low, high = high, low
        if high == low:
            if high < ceiling:
                high = high + 1
            else:
                low = low - 1
        if _interpolated(rungs, low, numbers) > found:
            continue
        if _interpolated(rungs, high, numbers) < found:
            continue
        if best is None or high - low < best[0]:
            best = (high - low, low, high)
    if best is None:
        return None
    return best[1], best[2]


def _reach_grow(
    sizes: "list[int]",
    bands: "list[str]",
    flags: "list[bool]",
    held: "dict[float, int]",
    rungs: "tuple[float, ...]",
    numbers: int,
    demand: int,
    plus_demand: int,
) -> "list[int]":
    """Give ONE stratum a piece of the ladder that holds a whole number.

    THE CELL STEP CANNOT HELP A BAND WHOSE STRATA ALL SIT ON FRACTIONS
    (review item P2-C5-F3). It moves cells INTO the strata that carry,
    which does nothing at all where none of them does: the 82-cell
    column of the review item has five positive strata crowded between
    `0.125` and `1`, and the one whole number that region reaches is
    spoken for. Moving cells between those five leaves every one of them
    on a fraction.

    What is not published is WHERE each stratum sits, and that is what
    moves here. The band's LAST stratum that may take a value -- the
    pinned ends hold the published `min` and `max` and the zero stratum
    holds `0`, so neither may -- is given the narrowest window of the
    ladder that reaches a free whole number, widened to the cells the
    published count still needs, its start moving first so the window
    stays as high in the band as the demand allows. The band's other
    strata divide what is left by the same even split G5.2 uses
    everywhere else, each keeping one cell, so `S`, the sign counts and
    the draw budget are exactly what they were and only the split moves.

    Plan P2-D6's feasibility rule 4 is what ranks the two: the split is
    this method's own default and `numeric_styles` is a published
    EXACT-OBSERVABLE count. The cost is paid in the open, because
    G5.6 reads `g_max` off the strata this step produces.
    """
    total = len(sizes)
    starts = _starts_of(sizes)
    for wanted, reachable in (
        (plus_demand, _REACHABLE[0]),
        (demand, _REACHABLE[1]),
    ):
        covered = 0
        for place in range(total):
            if flags[place] and bands[place] in reachable:
                covered = covered + sizes[place]
        if covered >= wanted:
            continue
        short = wanted - covered
        for band in reachable:
            places = [
                place for place in range(total) if bands[place] == band
            ]
            if not places:
                continue
            free = [
                place
                for place in places
                if not flags[place]
                and band != _BAND_ZERO
                and place != 0
                and not (place == total - 1 and total >= 2)
            ]
            if not free:
                continue
            taking = free[-1]
            before = 0
            for place in places:
                if place < taking:
                    before = before + 1
            after = len(places) - 1 - before
            band_low = starts[places[0]]
            band_high = starts[places[-1]] + sizes[places[-1]]
            window = _reach_window(
                rungs,
                numbers,
                band,
                held,
                band_low + before,
                band_high - after,
                total + 1,
            )
            if window is None:
                continue
            low, high = window
            while high - low < short:
                if low > band_low + before:
                    low = low - 1
                    continue
                if high < band_high - after:
                    high = high + 1
                    continue
                break
            moved = [size for size in sizes]
            for step in range(before):
                moved[places[step]] = (
                    (step + 1) * (low - band_low) // before
                    - step * (low - band_low) // before
                )
            moved[taking] = high - low
            for step in range(after):
                moved[places[before + 1 + step]] = (
                    (step + 1) * (band_high - high) // after
                    - step * (band_high - high) // after
                )
            if min(moved) < 1 or _totalled(moved) != _totalled(sizes):
                continue
            return moved
    return sizes


def _reach_sizes(
    sizes: "list[int]",
    bands: "list[str]",
    rungs: "tuple[float, ...] | None",
    whole_column: bool,
    numbers: int,
    demand: int,
    plus_demand: int,
) -> "list[int]":
    """Divide the cells so the point-free counts can REALLY be written.

    The third and last part of G5.2's carrier step (review item
    P2-C5-F3). The band step gives a stranded sign band a stratum; the
    cell step moves cells into the strata that can carry; and this
    repeats both against the LADDER'S OWN answer to which strata can,
    growing one stratum's window where the answer is none at all.

    It runs to a fixed point rather than once, because moving a cell
    moves every later stratum's share and therefore the whole numbers
    that share reaches. The number of rounds is bounded by the strata
    themselves: each round either meets both demands and stops, moves
    cells into a carrier, gives one stratum a window it did not have, or
    changes nothing and stops.

    Where no round can reach the demand, the sizes come back as they
    were and the shortfall is recounted from the finished cells and
    named under `numeric_styles` -- which is the honest outcome for the
    one shape left, a ladder whose own rungs hold no whole number for a
    stratum to take.
    """
    # A COLUMN OF WHOLE NUMBERS NEEDS NOTHING FROM THIS STEP. G5.4
    # rounds every value of such a column to a whole number, so every
    # stratum can wear a point-free style already and the values step of
    # G6.4 returns without moving anything. Asking the ladder which
    # strata can carry would answer a question the integer rule has
    # already settled, and any cell it moved would be a cost paid for
    # nothing.
    if rungs is None or whole_column or (demand < 1 and plus_demand < 1):
        return sizes
    moved = [size for size in sizes]
    for _round in range(len(sizes) + 2):
        flags, held = _reach_held(
            moved, bands, rungs, whole_column, numbers
        )
        if _reach_met(moved, bands, flags, demand, plus_demand):
            break
        stepped = _carrier_sizes(
            moved, bands, flags, demand, plus_demand
        )
        if stepped != moved:
            moved = stepped
            continue
        grown = _reach_grow(
            moved, bands, flags, held, rungs, numbers, demand, plus_demand
        )
        if grown == moved:
            break
        moved = grown
    return moved


def _numeric_layout(
    column: contract.ColumnBlock, facts: contract.NumericFacts
) -> "tuple[_NumericLayout, list[Deviation], int]":
    """How a column of numbers divides, and what it costs (G5.2, G4.3).

    Returns the layout, the deviations the division itself forces, and
    the number of words the column's content stage will consume. The
    strata are laid out negatives ascending, then the zero stratum, then
    positives ascending, because that is the sorted order of the
    column's own values and the ladder is a statement about sorted
    order.
    """
    numbers = column.n_numeric
    counts = (
        numbers,
        column.n_out_of_range,
        column.n_contradictory,
        column.n_not_numeric,
    )
    negatives = facts.n_negative - facts.n_negative_unrepresentable
    zeros = facts.n_zero
    positives = numbers - negatives - zeros
    if positives < 0:
        raise errors.ProfileError(
            _counts_contradict(column.name, zeros, negatives, numbers)
        )
    notes: list[Deviation] = []
    raw_budgets = _budget_split(column.n_distinct, counts)
    folded_budgets = _budget_split(column.n_distinct_folded, counts)
    values = min(numbers, max(folded_budgets[0], 1))
    zero_strata = 1 if zeros > 0 else 0
    rest = values - zero_strata
    needed = 0
    if negatives > 0:
        needed = needed + 1
    if positives > 0:
        needed = needed + 1
    # A STRATUM WITH NO CELLS IS NOT A VALUE. Only the negatives and the
    # positives are divided into strata, so at most that many strata can
    # hold a cell; asking for more built strata of size zero, and a
    # stratum of size zero still took an end of the ladder, still had its
    # sign repaired, and still named a deviation about a value the twin
    # never wrote. A column of nothing but zeros is the plain case: its
    # different SPELLINGS come from the leading-zero family of owner
    # decision 8, which is a rule about how a value is written, not about
    # how many values there are.
    rest = min(rest, negatives + positives)
    if rest < needed:
        rest = needed
        notes = notes + [
            _deviation(
                column.name,
                "n_distinct_folded",
                f"{column.n_distinct_folded}",
                f"{rest + zero_strata} different values in this column",
                "The column records fewer different values than its own "
                "counts of negative, zero and positive values need, so the "
                "twin holds one more value than the description names.",
            )
        ]
    if negatives > 0 and positives > 0:
        share = negatives + positives
        negative_strata = (2 * rest * negatives + share) // (2 * share)
        negative_strata = max(1, min(negative_strata, rest - 1))
    elif negatives > 0:
        negative_strata = rest
    else:
        negative_strata = 0
    positive_strata = rest - negative_strata
    # THE CELLS THE PUBLISHED STYLE MAP NEEDS TO BE POINT-FREE, PUT
    # WHERE THEY CAN BE WRITTEN (review item P2-C4-F3). The even split
    # is the twin's own default -- a numeric block publishes no
    # multiplicity map, so nothing says how many cells hold each value,
    # nor how the different values divide between the negative and the
    # positive side -- and `numeric_styles` is EXACT-OBSERVABLE, so the
    # default gives way to the published count rather than the other way
    # round. The band step comes first, because moving a stratum changes
    # which cells the cell step can then reach.
    quotas = _style_quotas(facts.numeric_styles)
    demand = min(_whole_demand(facts), numbers)
    rungs = _filled_rungs(facts.percentiles.rungs)
    if demand > 0:
        negative_strata, positive_strata = _carrier_bands(
            negatives,
            zeros,
            positives,
            negative_strata,
            positive_strata,
            rungs,
            facts.integer_valued,
            demand,
            min(quotas["leading_plus"], zeros + positives),
        )
    sizes, bands = _band_sizes(
        negatives, zeros, positives, negative_strata, positive_strata
    )
    if demand > 0:
        flags = _carrier_flags(sizes, bands, rungs, facts.integer_valued)
        sizes = _carrier_sizes(
            sizes,
            bands,
            flags,
            demand,
            min(quotas["leading_plus"], zeros + positives),
        )
        # AND THEN THE SAME QUESTION, ASKED OF THE LADDER (review item
        # P2-C5-F3). The two steps above count a stratum as a carrier
        # because the values step MAY take it to a whole number. Where
        # the ladder crowds several different values inside one unit,
        # that plan does not come true and the step above moves no cell,
        # because by its own count nothing needed moving. The reach step
        # asks which strata the published rungs actually leave a whole
        # number for, and moves cells -- and, where a band's strata all
        # sit on fractions, one stratum's window -- until the published
        # point-free counts have cells that can wear them.
        sizes = _reach_sizes(
            sizes,
            bands,
            rungs,
            facts.integer_valued,
            numbers,
            demand,
            min(quotas["leading_plus"], zeros + positives),
        )
    starts = _starts_of(sizes)
    total = len(sizes)
    pinned = 0
    if total >= 2:
        pinned = 2
    elif total == 1:
        pinned = 1
    zeroed = 0
    if zero_strata:
        place = negative_strata
        if place != 0 and not (total >= 2 and place == total - 1):
            zeroed = 1
    layout = _NumericLayout(
        sizes=tuple(sizes),
        starts=tuple(starts),
        bands=tuple(bands),
        raw_budgets=raw_budgets,
        folded_budgets=folded_budgets,
    )
    return layout, notes, max(total - pinned - zeroed, 0)


def _core_view(column: "contract.ColumnBlock") -> "contract.ColumnBlock":
    """The affixed column as the numeric machinery needs to see it.

    An affixed column has TWO populations and the numeric machinery is
    written over one of them. Its universal counts answer for the
    CELLS -- and a cell reading `$100` is not itself a number, so those
    counts say a column of prices holds no numbers at all. The
    quantitative block answers for the CORES.

    So the cores are handed over as a column in their own right: the
    same block, with the core counts standing where the cell counts
    were and the quantitative facts standing alone. Every rule of G5
    and G6 then applies unchanged, which is the point -- the numbers
    inside an affixed column are built by exactly the code that builds
    a plain numeric column, and the pair is put on afterwards.
    """
    facts = column.facts
    if not isinstance(facts, contract.AffixedFacts):
        raise _wrong_facts(column.name)
    return dataclasses.replace(
        column,
        statistical_type="continuous",
        n_present=facts.n_affixed,
        n_numeric=facts.n_core_numeric,
        n_not_numeric=facts.n_core_not_numeric,
        n_out_of_range=facts.n_core_out_of_range,
        n_contradictory=facts.n_core_contradictory,
        facts=facts.numbers,
    )


def _part_view(
    column: "contract.ColumnBlock", place: int
) -> "contract.ColumnBlock":
    """One position of a joined column, as a numeric column of its own.

    The same trick `_core_view` plays for the affixed role, and for the
    same reason: a joined column has one population PER POSITION, and
    the numeric machinery is written over one population. A cell
    reading `120/80` is not itself a number, so the universal counts
    say the column holds none; the quantitative block for position one
    answers for the first numbers alone.

    Handing each position over as a column in its own right means the
    ladder, the mean, the spread, the styles and the widths of every
    number in the twin are built by exactly the code that builds a
    plain numeric column. Nothing about the arithmetic is written twice.
    """
    facts = column.facts
    if not isinstance(facts, contract.JoinedFacts):
        raise _wrong_facts(column.name)
    return dataclasses.replace(
        column,
        statistical_type="continuous",
        n_present=facts.n_joined,
        n_numeric=facts.n_joined,
        n_not_numeric=0,
        n_out_of_range=0,
        n_contradictory=0,
        facts=facts.parts[place],
    )


def _padded_to(text: str, width: int) -> str:
    """One number written at least `width` characters wide.

    A position whose smallest published width is wider than the number
    needs was WRITTEN padded -- `007` beside `080` -- so the twin pads
    it back. A position whose widths differ because its numbers differ
    publishes the width of its smallest number, and nothing is added.
    """
    out = text
    while len(out) < width:
        out = "0" + out
    return out


def _joined_written(
    drawn: "list[list[str]]", facts: "contract.JoinedFacts", row: int
) -> str:
    """One cell of a joined column, from the numbers each position drew."""
    written = ""
    for place in range(facts.n_parts):
        if place:
            written = written + facts.separator
        held = drawn[place]
        text = held[row] if row < len(held) else "0"
        written = written + _padded_to(text, facts.part_min_widths[place])
    return written


def _ranks_of(values: "list[float]") -> "list[float]":
    """The rank of each value, ties sharing the average of their ranks."""
    pairs: "list[tuple[float, int]]" = []
    for seat in range(len(values)):
        pairs = pairs + [(values[seat], seat)]
    pairs = sorted(pairs)
    ranks = [0.0 for _each in values]
    at = 0
    while at < len(pairs):
        last = at
        while last + 1 < len(pairs) and pairs[last + 1][0] == pairs[at][0]:
            last = last + 1
        shared = (at + last) / 2.0
        for seat in range(at, last + 1):
            ranks[pairs[seat][1]] = shared
        at = last + 1
    return ranks


def _repaired_pairing(
    drawn: "list[list[str]]",
    facts: "contract.JoinedFacts",
    wanted: int,
    words: "list[int]",
) -> "list[list[str]]":
    """Choose WHICH numbers meet in a row, to the facts published.

    WHAT EACH POSITION HOLDS IS ALREADY EXACT when this is reached, and
    nothing here changes it. Every step swaps two rows' numbers within
    ONE position, so each position keeps its multiset to the last cell
    and every published number about it -- ladder, mean, spread, styles,
    widths -- is untouched. What moves is only the pairing, which is the
    one thing `parts` does not describe.

    IT STARTS RANK FOR RANK, largest with largest, where the agreement
    is 1 and the earlier position is above the later one as often as it
    can be. Both are usually ABOVE what the description publishes, and
    swaps bring them down to it. Starting from a shuffle was built
    first and was worse: it begins far from every target at once.

    WHY THIS IS NEEDED. Drawn independently, the two numbers of a blood
    pressure agreed at -0.02 where the real column agreed at 0.83, and
    a twin cell could hold a diastolic above its systolic. The numbers
    were right one at a time and the pairs were not readings.

    EVERY STEP COSTS THE SAME, however long the column. Scoring a
    pairing from scratch is a sort and a walk, and a walk that scored
    every attempt that way spent fourteen seconds on four hundred rows.
    Nothing about a swap needs it: two cells change, so the count of
    different cells moves by what those two were and are; two rows
    change, so the above-count moves by those two; and the two ranks
    trade places, which moves the agreement's numerator by exactly
    `(a_i - a_j) * (b_j - b_i)` and moves its divisor not at all,
    because neither position's ranks have changed as a MULTISET. So
    every quantity here is carried and adjusted, never recomputed.
    """
    total = facts.n_joined
    if total < 2 or facts.n_parts < 2:
        return drawn
    # WHERE THE WALK STARTS IS CHOSEN BY WHAT IT IS WALKING TOWARDS.
    # Rank for rank is where the agreement is 1; it is the right place
    # to start for a blood pressure, whose numbers agree at 0.83, and
    # the WORST place to start for a column whose numbers agree at zero
    # -- measured, a pulmonary-artery column publishing -0.009 was left
    # at 0.216, because the walk could not travel the whole way inside
    # its try ceiling. So a low target starts from a shuffle, which is
    # already near it, and a strongly negative one starts from rank
    # against rank.
    wanted_agreement = 0.0
    for value in facts.part_agreements:
        wanted_agreement = wanted_agreement + value
    if facts.part_agreements:
        wanted_agreement = wanted_agreement / float(len(facts.part_agreements))
    held: "list[list[str]]" = []
    for column in drawn:
        pairs: "list[tuple[float, str]]" = []
        for spelling in column:
            pairs = pairs + [(float(spelling), spelling)]
        pairs = sorted(pairs)
        held = held + [[pair[1] for pair in pairs]]
    last = facts.n_parts - 1
    if wanted_agreement < -0.4:
        held[last] = [
            held[last][total - 1 - seat] for seat in range(total)
        ]
    elif wanted_agreement < 0.4 and len(words) >= max(total - 1, 0):
        order = _arrangement(words, total)
        held[last] = [held[last][seat] for seat in order]
    numbers: "list[list[float]]" = []
    ranks: "list[list[float]]" = []
    for place in range(facts.n_parts):
        counted_here: "list[float]" = []
        for spelling in held[place]:
            counted_here = counted_here + [float(spelling)]
        numbers = numbers + [counted_here]
        ranks = ranks + [_ranks_of(counted_here)]
    middle = (total - 1) / 2.0
    # The divisor of every agreement, which no swap can move.
    spread: "list[float]" = []
    for place in range(facts.n_parts):
        summed = 0.0
        for row in range(total):
            away = ranks[place][row] - middle
            summed = summed + away * away
        spread = spread + [summed]
    # The pairs this walk can move are the ones the last position is in.
    seats: "list[int]" = []
    firsts: "list[int]" = []
    seat = 0
    for first in range(facts.n_parts):
        for second in range(first + 1, facts.n_parts):
            if second == last:
                seats = seats + [seat]
                firsts = firsts + [first]
            seat = seat + 1
    tops: "list[float]" = []
    aboves: "list[int]" = []
    for index in range(len(seats)):
        first = firsts[index]
        summed = 0.0
        counted = 0
        for row in range(total):
            summed = summed + (ranks[first][row] - middle) * (
                ranks[last][row] - middle
            )
            if numbers[first][row] > numbers[last][row]:
                counted = counted + 1
        tops = tops + [summed]
        aboves = aboves + [counted]
    cells: "list[str]" = []
    seen: "dict[str, int]" = {}
    for row in range(total):
        text = _joined_written(held, facts, row)
        cells = cells + [text]
        seen[text] = seen[text] + 1 if text in seen else 1

    def _away() -> float:
        """How far this pairing is from every pairing fact published.

        THE THREE ARE SCALED TO THEIR OWN SIZES, and the reason is a
        measurement rather than a preference. Weighting the count of
        different cells in ROWS -- one row out costing a whole unit --
        was built and was worse at everything: the agreement fell from
        0.834 to 0.559, two cells came out impossible, and the count it
        was chasing STILL stopped short, at 317 of 324. It stops short
        because it cannot be reached: each position's numbers are drawn
        to the ladder the description publishes, which repeats a value
        more evenly than the real column did, and pairs drawn from
        values that repeat more can only be so many. Spending the
        agreement on it buys nothing and costs the readings.

        So the count of different cells is scaled against the column's
        rows, where it competes fairly and yields where it cannot win,
        and the shortfall is REPORTED by the caller rather than paid
        for. Residual R-P4-40 records the cause, which is upstream of
        this walk.
        """
        out = abs(len(seen) - wanted) / float(total)
        for index in range(len(seats)):
            place = seats[index]
            first = firsts[index]
            # A ROW OF THIS ONE OUTWEIGHS THE WHOLE AGREEMENT, and it
            # should: `part_above` is an exact count that a pairing can
            # always meet, and one row out of it is one cell holding a
            # reading that cannot happen -- a diastolic at or above its
            # systolic. Measured at the same weight as the others, the
            # walk sold a row of it for a thousandth of agreement and a
            # blood-pressure twin came out with one impossible cell.
            # The count of different cells is NOT weighted this way,
            # because that one cannot always be met (R-P4-40) and a
            # walk that insists on it wrecks everything else.
            out = out + float(abs(aboves[index] - facts.part_above[place]))
            divisor = (spread[first] * spread[last]) ** 0.5
            agreed = tops[index] / divisor if divisor > 0.0 else 0.0
            out = out + abs(agreed - facts.part_agreements[place])
        return out

    away = _away()
    tries = 0
    at = 0
    ceiling = 200 * total
    while away > 0.0005 and tries < ceiling and len(words) >= 2:
        tries = tries + 1
        if at + 1 >= len(words):
            at = 0
        one = _bounded(words[at], total)
        two = _bounded(words[at + 1], total)
        at = at + 2
        if one == two or held[last][one] == held[last][two]:
            continue
        kept_tops = [value for value in tops]
        kept_aboves = [value for value in aboves]
        for index in range(len(seats)):
            first = firsts[index]
            tops[index] = tops[index] + (
                ranks[first][one] - ranks[first][two]
            ) * (ranks[last][two] - ranks[last][one])
            for row in (one, two):
                if numbers[first][row] > numbers[last][row]:
                    aboves[index] = aboves[index] - 1
        held[last][one], held[last][two] = held[last][two], held[last][one]
        numbers[last][one], numbers[last][two] = (
            numbers[last][two],
            numbers[last][one],
        )
        ranks[last][one], ranks[last][two] = (
            ranks[last][two],
            ranks[last][one],
        )
        for index in range(len(seats)):
            first = firsts[index]
            for row in (one, two):
                if numbers[first][row] > numbers[last][row]:
                    aboves[index] = aboves[index] + 1
        made_one = _joined_written(held, facts, one)
        made_two = _joined_written(held, facts, two)
        for gone in (cells[one], cells[two]):
            seen[gone] = seen[gone] - 1
            if seen[gone] < 1:
                del seen[gone]
        for made in (made_one, made_two):
            seen[made] = seen[made] + 1 if made in seen else 1
        now = _away()
        # AN EQUAL SWAP IS TAKEN, NOT ONLY A BETTER ONE. Three facts are
        # being met at once and they pull against each other: a swap
        # that breaks a repeated cell often costs a little agreement and
        # gains it back two swaps later. Taking only strict improvements
        # stops on the first ridge -- measured, it left a column of 324
        # different readings at 276 while the agreement was already
        # right. Equal moves let the walk cross the ridge, and the try
        # ceiling is what stops it wandering.
        if now <= away:
            away = now
            cells[one] = made_one
            cells[two] = made_two
            continue
        # Put every carried quantity back, exactly as it was.
        for made in (made_one, made_two):
            seen[made] = seen[made] - 1
            if seen[made] < 1:
                del seen[made]
        for back in (cells[one], cells[two]):
            seen[back] = seen[back] + 1 if back in seen else 1
        held[last][one], held[last][two] = held[last][two], held[last][one]
        numbers[last][one], numbers[last][two] = (
            numbers[last][two],
            numbers[last][one],
        )
        ranks[last][one], ranks[last][two] = (
            ranks[last][two],
            ranks[last][one],
        )
        tops = kept_tops
        aboves = kept_aboves
    return held


def _joined_content(
    plan: "_ColumnPlan", words: "list[int]"
) -> "tuple[list[str], list[Deviation]]":
    """Every present cell of a joined-number column (contract 6.13).

    Each position is built first, by the numeric rules, over that
    position's view of this column. The separator goes on afterwards,
    character for character as the description publishes it, and each
    number is padded back to the smallest width its position was
    written at.

    THE POSITIONS ARE DRAWN INDEPENDENTLY, and that is a limit worth
    stating rather than hiding: this format publishes no structure
    between one position and another, so nothing in the description
    says that a high first number went with a high second one. The
    twin's pairs are therefore believable ONE NUMBER AT A TIME. That is
    the same promise the whole format makes between columns (contract
    4.6, S12), arriving inside a cell.
    """
    column = plan.column
    facts = column.facts
    if not isinstance(facts, contract.JoinedFacts):
        raise _wrong_facts(column.name)
    notes: "list[Deviation]" = []
    drawn: "list[list[str]]" = []
    # EACH POSITION DRAWS ITS OWN WORDS, and that is what makes the
    # pairs pairs. Handing every position the same list was measured
    # first and is wrong twice: each drew the same words, so position
    # two moved in lockstep with position one -- a 400-row column whose
    # real cells hold 387 different readings came out with 117, in runs
    # like `105/63`, `104/63`. The marginals were right either way; the
    # PAIRING was an artefact of the word stream. The plan's word budget
    # is the sum of what the positions need, so this walks it.
    at = 0
    for place in range(facts.n_parts):
        view = _part_view(column, place)
        layout, layout_notes, part_content = _numeric_layout(
            view, facts.parts[place]
        )
        part_words: "list[int]" = []
        step = 0
        while step < part_content and at + step < len(words):
            part_words = part_words + [words[at + step]]
            step = step + 1
        at = at + part_content
        part_plan = dataclasses.replace(plan, column=view, layout=layout)
        values, part_notes = _numeric_content(part_plan, part_words)
        notes = notes + layout_notes + part_notes
        # EVERY POSITION AFTER THE FIRST IS SHUFFLED AGAINST IT, and
        # this is the step that makes a pair a pair. `_numeric_content`
        # places its values by rule, not by chance -- the words decide
        # arrangement, not which numbers come out -- so two positions
        # built from it come out in the SAME order and pair up in
        # lockstep. Measured: a column whose real cells hold 387
        # different readings came out with 117, in runs like `105/63`,
        # `104/63`, while each position's own distribution was right to
        # the digit.
        #
        # A shuffle keeps every position's MULTISET exactly, so every
        # published number about it -- ladder, mean, spread, styles,
        # widths -- is untouched, and only the pairing moves. It is the
        # honest choice among the pairings the description admits: this
        # format publishes no structure between one position and
        # another (contract 4.6, S12), so no pairing is asked for, and
        # the one that also meets the published `n_distinct` is better
        # than one that does not. A fixed reversal would meet it too and
        # would invent a strong negative correlation nothing published
        # says is there.
        drawn = drawn + [values]
    # WHICH NUMBERS MEET IN A ROW. The words the shuffle used to spend
    # are spent here instead: the pairing is chosen to the facts the
    # description publishes about it rather than left to chance.
    spare: "list[int]" = []
    step = at
    while step < len(words):
        spare = spare + [words[step]]
        step = step + 1
    drawn = _repaired_pairing(drawn, facts, column.n_distinct, spare)
    # WHAT THE PAIRING COULD NOT REACH IS SAID, not swallowed. The count
    # of different cells is a fact of the real column that a pairing of
    # THESE numbers may be unable to meet (residual R-P4-40), and a twin
    # that quietly holds fewer is a twin whose own report should say so.
    made_cells: "dict[str, int]" = {}
    for row in range(facts.n_joined):
        text = _joined_written(drawn, facts, row)
        made_cells[text] = 1
    if len(made_cells) != column.n_distinct:
        notes = notes + [
            _deviation(
                column.name,
                "n_distinct",
                f"{column.n_distinct} different value(s)",
                f"{len(made_cells)} different value(s)",
                "Each number in this column's cells follows the "
                "description exactly. Which numbers meet in a cell is "
                "chosen to the facts the description publishes about "
                "that, and those cannot always be met together: numbers "
                "drawn to a published ladder repeat more evenly than the "
                "real ones did, so fewer different pairs can be made.",
            )
        ]
    cells: "list[str]" = []
    for row in range(facts.n_joined):
        cells = cells + [_joined_written(drawn, facts, row)]
    # THE CELLS THAT SPLIT NO SUCH WAY -- the stragglers the parse line
    # tolerated. The description says how MANY there were and nothing
    # else about them, so they are invented, and invention is what they
    # are reported as.
    stragglers = column.n_present - facts.n_joined
    if stragglers > 0:
        used: "dict[str, int]" = {cell: 1 for cell in cells}
        cells = cells + _class_spellings(
            _CLASS_TEXT,
            stragglers,
            1,
            1,
            0,
            used,
            _hole_spellings(column),
        )
        notes = notes + [
            _deviation(
                column.name,
                "n_unparsed",
                f"{stragglers} value(s) that are not numbers joined this "
                "way",
                "made-up text stands in for them",
                "This column holds some cells that do not split into "
                "whole numbers. The description records how many and "
                "nothing else about them, so the twin invents them.",
            )
        ]
    return cells, notes


def _affixed_content(
    plan: "_ColumnPlan", words: "list[int]"
) -> "tuple[list[str], list[Deviation]]":
    """Every present cell of an affixed column (contract 6.12).

    The cores are built first, by the numeric rules, over the core
    view of this column. The pair goes on afterwards, character for
    character as the description publishes it. The cells that wore no
    pair -- the stragglers the parse line tolerated -- are invented
    last, and are marked as invention because nothing about them is
    published: the description says how MANY there were and nothing
    else.
    """
    column = plan.column
    facts = column.facts
    if not isinstance(facts, contract.AffixedFacts):
        raise _wrong_facts(column.name)
    core_plan = dataclasses.replace(plan, column=_core_view(column))
    cores, notes = _numeric_content(core_plan, words)
    cells = [f"{facts.affix_prefix}{core}{facts.affix_suffix}" for core in cores]
    # THE STRAGGLERS: the cells wearing no pair. Their count is
    # `n_present - n_affixed`, and their CLASSES are published -- the
    # universal census counts cells, and an affixed cell is not a
    # number, so every numeric, out-of-range and contradictory cell of
    # this column is a straggler and the rest of `n_not_numeric` is the
    # ordinary text among them.
    #
    # Writing them all as text was wrong twice over: it lost the
    # published class of a plain number sitting beside the affixed
    # cells, and it reported the loss as a deviation instead of not
    # committing it (review item P4-AFX-F6). G10.2 requires the
    # construction to preserve the class, not to apologize for it.
    layout = plan.layout
    used: "dict[str, int]" = {cell: 1 for cell in cells}
    pair = (facts.affix_prefix, facts.affix_suffix)
    # WHAT THE AFFIXED CELLS ALREADY PAID, class by class. The two
    # populations OVERLAP and the earlier arithmetic assumed they could
    # not: a cell wearing the pair is still a cell, so it lands in one
    # of the four universal classes like any other, and a column whose
    # pair is `1` holds cells such as `12` that wear it AND read as
    # numbers. Subtracting `n_affixed` from the text class alone and
    # clamping the result at zero swallowed that overlap in a class
    # that did not hold it, then wrote the number class again on top --
    # so a hundred-row column came out with a hundred and one cells and
    # `generate` stopped with an internal-check message telling its
    # user that synthtwin has a bug. It has one; this is it.
    #
    # The classes the written cells already fill are RECOUNTED here
    # rather than assumed, by the same classifier the description was
    # built with, and only the shortfall is written. What the twin
    # cannot then reach is named by `_class_notes`, which recounts all
    # four from the finished text.
    worn = {name: 0 for name in _CLASSES}
    for cell in cells:
        found = parsing.classify_number(cell)
        worn[found] = worn[found] + 1
    stragglers = column.n_present - facts.n_affixed
    if stragglers < 0:
        stragglers = 0
    owed: "dict[str, int]" = {}
    room = stragglers
    for kind, published in (
        (_CLASS_NUMBER, column.n_numeric),
        (_CLASS_OUT_OF_RANGE, column.n_out_of_range),
        (_CLASS_CONTRADICTORY, column.n_contradictory),
    ):
        short = published - worn[kind]
        if short < 0:
            short = 0
        if short > room:
            short = room
        owed[kind] = short
        room = room - short
    # Whatever the three named classes did not claim is ordinary text,
    # which is the class the contract gives every cell no other class
    # names.
    owed[_CLASS_TEXT] = room
    holes = _hole_spellings(column)
    if owed[_CLASS_NUMBER]:
        cells = cells + _unaffixed_numbers(
            owed[_CLASS_NUMBER], pair, used, holes
        )
    for kind, count, place in (
        (_CLASS_OUT_OF_RANGE, owed[_CLASS_OUT_OF_RANGE], 1),
        (_CLASS_CONTRADICTORY, owed[_CLASS_CONTRADICTORY], 2),
        (_CLASS_TEXT, owed[_CLASS_TEXT], 3),
    ):
        if not count:
            continue
        cells = cells + _unaffixed_spellings(
            kind,
            count,
            layout.folded_budgets[place] if layout else 1,
            layout.raw_budgets[place] if layout else 1,
            pair,
            used,
            holes,
        )
    return cells, notes


def _wears(text: str, pair: "tuple[str, str]") -> bool:
    """Whether this cell would be read as wearing the published pair.

    A straggler that wears it is counted as affixed when the twin is
    described again, so `n_affixed` comes out higher than the
    description published and the collision is silent (review item
    P4-AFX-F7). The invented spelling `text-1` wearing the published
    prefix `text-` is exactly that case.
    """
    prefix, suffix = pair
    trimmed = parsing.trimmed(text)
    if not trimmed.startswith(prefix) or not trimmed.endswith(suffix):
        return False
    return bool(trimmed[len(prefix) : len(trimmed) - len(suffix)])


def _unaffixed_spellings(
    kind: str,
    count: int,
    folded_budget: int,
    raw_budget: int,
    pair: "tuple[str, str]",
    used: "dict[str, int]",
    holes: "tuple[str, ...]" = (),
) -> "list[str]":
    """One straggler class, with nothing in it wearing the pair.

    THE FILTER USED TO REJECT EVERY CANDIDATE, and the two published
    classes it feeds were unreachable because of it. `_class_spellings`
    RECORDS each spelling it builds before handing it back, so testing
    `spelling in used` after the call was testing whether the builder
    had just done its own bookkeeping -- always true. Every cell fell
    through to the last resort below, so a thousand-row column of
    prices beside five cells too large to hold and five of
    contradictory notation wrote `(no pair 0)` through `(no pair 4)`
    for all ten: two exact published counts missed, the count of
    different values missed with them, and the deviation note blamed
    group granularity for cells that were never built at all.
    What must be refused is a spelling used BEFORE this walk began, so
    the snapshot is taken at entry. A repeat WITHIN the walk is not a
    collision: a class whose spelling budget is spent repeats its last
    spelling on purpose (G6.5).
    """
    built: list[str] = []
    already = {spelling: 1 for spelling in used}
    step = 0
    while len(built) < count and step < count * 8 + 64:
        wanted = count - len(built)
        batch = _class_spellings(
            kind, wanted + step, folded_budget, raw_budget, 0, used, holes
        )
        for spelling in batch:
            if len(built) >= count:
                break
            if _wears(spelling, pair):
                continue
            if spelling in already:
                continue
            if _is_a_hole_spelling(spelling, holes):
                continue
            built = built + [spelling]
            used[spelling] = 1
        step = step + wanted + 1
    while len(built) < count:
        # A last resort that cannot wear the pair whatever it is: a
        # spelling of this package's own, made distinct by its place.
        made = f"(no pair {len(built)})"
        if not _wears(made, pair) and made not in used:
            used[made] = 1
            built = built + [made]
        else:
            built = built + [f"(no pair {len(built)}{len(used)})"]
    return built


def _absent_cells(column: contract.ColumnBlock) -> "list[str]":
    """Every absent cell of one column, as the text it is written with.

    THE VERSION 6 WRITE RULE (contract C6-115, plan P4-D6.1). Version 5
    wrote every absent cell empty and said so in a sealed sentence
    (C5-9); a person's own `NA`, `#N/A` or `Not recorded` was recorded
    in the description and then thrown away by the twin, so code that
    filtered on it -- `df[df.status != "NA"]`, or a `na_values=` list
    handed to a reader -- did something on the real table and nothing
    at all on the twin.

    Three parts, and the exception is the whole of the second:

    1. each `missing_by_source` spelling at exactly its published
       count, EXCEPT a spelling a judged pass put there;
    2. every other absent cell empty -- the blank count, the withheld
       remainder, and every judged-pass-sourced cell;
    3. in a fixed sorted order, so the permutation that places
       everything else places these too and the bytes stay a pure
       function of the description and the seed.

    WHY A JUDGED PASS'S CELLS STAY BLANK (C6-116). A reproduced TEXT
    spelling reads back as absence by a fixed rule of the description
    alone -- it is a member of the published vocabulary, or a value the
    person named -- and that reading does not depend on the twin's own
    values. A stand-in NUMBER and a calendar PLACEHOLDER are that
    rule's named exclusions: the absence reading of both runs through
    the producer's outlier-and-share judgement over the measured file's
    own values, which a twin's generated distribution is not
    guaranteed to re-fire. Reproducing them would make the twin's own
    measurement contingent on a re-judgement. Nothing is lost by it:
    the twin's report names those cells, per column.

    Guarantees: accepts one loaded column block; returns exactly
    `n_missing` cells. Determinism: a fixed function of the block.
    Raises nothing. No I/O of any kind.
    """
    written: list[str] = []
    for spelling in sorted(column.missing_by_source):
        if _a_judged_pass_put_it_there(column, spelling):
            continue
        for _each in range(column.missing_by_source[spelling]):
            written = written + [spelling]
    while len(written) < column.n_missing:
        written = written + [""]
    return written[: column.n_missing]


def _a_judged_pass_put_it_there(
    column: contract.ColumnBlock, spelling: str
) -> bool:
    """Whether a judged pass is what made cells of this spelling absent.

    The two passes this version has are the stand-in number pass and
    the calendar placeholder pass, and each records its decision as a
    verdict naming the candidate. A published hole spelling that
    denotes a candidate this column read as missing is that pass's
    doing, and C6-116 keeps it blank.
    """
    for verdict in column.sentinel_verdicts:
        if verdict.verdict != contract.VERDICT_MISSING:
            continue
        if verdict.candidate == contract.WITHHELD:
            continue
        if _is_the_same_candidate(spelling, verdict.candidate):
            return True
    return False


def _is_the_same_candidate(spelling: str, candidate: str) -> bool:
    """Whether a hole spelling denotes one judged candidate.

    A day is compared as its canonical spelling and a number as the
    NUMBER it denotes, which is how the producer counted the
    candidate's own rows in the first place.
    """
    if candidate in parsing.calendar_placeholders():
        for name in parsing.DATE_FORMATS:
            if parsing.placeholder_day_of(spelling, name) == candidate:
                return True
        return False
    held = parsing.exact_of_spelling(spelling)
    if held is None:
        return False
    return held == parsing.exact_of_spelling(candidate)


def _every_hole_spelling(
    profile: contract.Profile,
) -> "tuple[str, ...]":
    """Every spelling ANY column of this document calls absent.

    A `--missing-value` declaration is made once and reaches the whole
    table, so a spelling one column publishes among its absent cells
    means "no value" wherever it appears. The validator reconstructs it
    that way; a walk that invented spellings knowing only its own
    column's holes did not, and wrote one column's hole into another
    column as a present value (review round 5 finding 3).

    Used where a spelling is CHOSEN, never where one is recounted: a
    recount asks what THIS column's description says, which is the
    narrower question `_wears_a_published_hole` answers.
    """
    found: "list[str]" = []
    for column in profile.columns:
        for spelling in _hole_spellings(column):
            if spelling not in found:
                found = found + [spelling]
    return tuple(sorted(found))


def _hole_spellings(
    column: contract.ColumnBlock,
) -> "tuple[str, ...]":
    """Every spelling this column publishes among its absent cells.

    The keys of `missing_by_source`, which are the spellings the column
    ACTUALLY held where the floor let it name them. What is NOT here is
    anything the floor pooled: those spellings the description does not
    publish, so a generator cannot avoid them and does not pretend to.
    The blank spelling is not here either, for the same reason it is
    not a key of that map -- a twin's absent cells are written empty
    and no present cell of one is blank.
    """
    found: list[str] = []
    for spelling in sorted(column.missing_by_source):
        found = found + [spelling]
    return tuple(found)


def _unaffixed_numbers(
    count: int,
    pair: "tuple[str, str]",
    used: "dict[str, int]",
    holes: "tuple[str, ...]",
) -> "list[str]":
    """Plain numbers standing beside the affixed cells.

    A cell of an affixed column that IS a number wears no pair -- the
    detection rule requires one side to carry text -- so these are
    stragglers, and the description publishes how many. Written as
    whole numbers because nothing else about them is published: the
    ladder and every moment belong to the CORES.

    THREE SPELLINGS ARE REFUSED, and the third was missing. A spelling
    already written would repeat a cell; one that WEARS the pair would
    be counted affixed when the twin is described again; and one this
    column publishes as a HOLE SPELLING is read back as no value at
    all. A column of prices beside eleven cells spelled `1`, declared
    with `--missing-value 1`, published `missing_by_source {"1": 11}`
    and its twin then wrote a present cell spelled `1` -- so the twin's
    own description read it as absent, and five exact counts moved
    against a description the twin was built from.
    """
    built: list[str] = []
    value = 1
    while len(built) < count:
        spelling = f"{value}"
        if (
            spelling not in used
            and not _wears(spelling, pair)
            and not _is_a_hole_spelling(spelling, holes)
        ):
            used[spelling] = 1
            built = built + [spelling]
        value = value + 1
    return built


def _is_a_hole_spelling(text: str, holes: "tuple[str, ...]") -> bool:
    """Whether a spelling is one this run must not INVENT.

    Three ways, and all three are the reader's own: the spelling is one
    this format always reads as "no value"; the person named it when
    the description was written; or this column publishes it among the
    spellings its absent cells wore.

    THIS IS THE CONSERVATIVE HALF OF THE QUESTION, and it is asked
    where a spelling is being CHOSEN -- an invented straggler, a
    stand-in, a withheld variant. There the safe answer is to avoid
    anything a reader might call absent, so the built-in vocabulary
    counts even where no cell of this column ever wore it.

    It is NOT the question a recount asks (review item P4-DATE2-F2).
    `--keep-value NA` makes `NA` a real label of a real column, and a
    twin that writes it writes a present cell; a recount that used this
    predicate called forty such cells absent and reported distinctness
    deviations no file has. `_wears_a_published_hole` is that other
    half.
    """
    if parsing.is_missing_text(text):
        return True
    return _wears_a_published_hole(text, holes)


def _wears_a_published_hole(text: str, holes: "tuple[str, ...]") -> bool:
    """Whether the twin's own description reads this WRITTEN cell as absent.

    The honest half of the question above, and the one a recount asks:
    not "might a reader call this absent" but "does this column's own
    description". What answers it is what the column PUBLISHES among
    the spellings its absent cells wore -- facts of this column, not of
    the vocabulary.

    The built-in words are deliberately not consulted here. A twin cell
    can only wear one of them where the description publishes it as a
    VALUE, which happens only where a `--keep-value` rescued it, and
    such a cell is present; every place that INVENTS a spelling asks
    the conservative predicate above instead, so no cell reaches a
    recount wearing a built-in word by accident.
    """
    body = parsing.trimmed(text)
    folded = parsing.folded(body)
    held = parsing.exact_of_spelling(body)
    for spelling in holes:
        # A PUBLISHED HOLE THAT IS A VOCABULARY MEMBER IS MATCHED THE
        # MEMBER'S OWN WAY (contract C6-32, review item P4-HOLE-F3).
        # This predicate folded every hole spelling, so a column
        # publishing the exact member `NaT` had its sixty ordinary
        # `nat` cells counted as holes by the recount -- and the twin
        # report then said the column held sixty values where the file
        # holds a hundred and twenty.
        if spelling in parsing.MISSING_TEXTS_EXACT:
            if text == spelling:
                return True
            continue
        other = parsing.trimmed(spelling)
        if parsing.folded(other) == folded:
            return True
        # ...AND A NUMBER IS MATCHED AS A NUMBER, which is how the
        # description's own reader matches a declared value: `1` and
        # `1.0` are one value and one of them being published as a hole
        # makes the other one a hole too. Comparing spellings alone let
        # the straggler walk write `1` into a column publishing
        # `missing_by_source {"1.0": 11}`, and the twin's own
        # description then counted that present cell absent. The same
        # holds for `01`, `1.00` and `1e0`.
        #
        # MATCHED EXACTLY, and it was matched after rounding (review
        # item P4-DATE3-F2). The producer's rule is that two spellings
        # are one number when they denote one number, however close the
        # binary64 values they round to -- so `-999` and
        # `-999.00000000000001` are two numbers, and a comparison made
        # in binary64 called them one and counted a present cell
        # absent. This asks the producer's own rule, by its own name.
        if held is None:
            continue
        found = parsing.exact_of_spelling(other)
        if found is not None and found == held:
            return True
    return False


def _numeric_content(
    plan: "_ColumnPlan", words: "list[int]"
) -> "tuple[list[str], list[Deviation]]":
    """Every present cell of a column of numbers (method G5, G6, G10.3).

    The content is built in one fixed order -- the numbers in stratum
    order, then the cells that are out of range, then the contradictory
    ones, then the ordinary text -- so that two implementations build
    the same list. The rows are made random by the arrangement of G4.2,
    not by this order.
    """
    column = plan.column
    facts = column.facts
    layout = plan.layout
    if not isinstance(facts, contract.NumericFacts) or layout is None:
        raise _wrong_facts(column.name)
    notes: list[Deviation] = []
    rungs = _filled_rungs(facts.percentiles.rungs)
    if len([rung for rung in facts.percentiles.rungs if rung is None]) > 0:
        notes = notes + [
            _deviation(
                column.name,
                "percentiles",
                "a ladder with a rung that holds nothing",
                "the nearest rung that holds a number stands in its place",
                "One of the eleven steps of this column's ladder holds no "
                "number, so the twin's values follow the steps that do.",
            )
        ]
    values, endpoint_notes = _stratum_values(column, facts, layout, rungs, words)
    notes = notes + endpoint_notes
    values = _whole_enough(column, facts, layout, rungs, values)
    cells, style_notes = _number_cells(column, facts, layout, values)
    notes = notes + style_notes
    used: dict[str, int] = {cell: 1 for cell in cells}
    if column.n_out_of_range:
        cells = cells + _class_spellings(
            _CLASS_OUT_OF_RANGE,
            column.n_out_of_range,
            layout.folded_budgets[1],
            layout.raw_budgets[1],
            facts.n_negative_unrepresentable,
            used,
            _hole_spellings(column),
        )
        notes = notes + [
            _deviation(
                column.name,
                "n_out_of_range",
                f"{column.n_out_of_range} values too large or too small "
                f"to hold",
                "every one of them written too large",
                "The description does not say how those values split "
                "between too large and too small, so the twin writes them "
                "all too large.",
            )
        ]
    if column.n_contradictory:
        cells = cells + _class_spellings(
            _CLASS_CONTRADICTORY,
            column.n_contradictory,
            layout.folded_budgets[2],
            layout.raw_budgets[2],
            0,
            used,
            _hole_spellings(column),
        )
    if column.n_not_numeric:
        cells = cells + _class_spellings(
            _CLASS_TEXT,
            column.n_not_numeric,
            layout.folded_budgets[3],
            layout.raw_budgets[3],
            0,
            used,
            _hole_spellings(column),
        )
    return cells, notes


def _stratum_values(
    column: contract.ColumnBlock,
    facts: contract.NumericFacts,
    layout: "_NumericLayout",
    rungs: "tuple[float, ...] | None",
    words: "list[int]",
) -> "tuple[list[float], list[Deviation]]":
    """The one value every stratum holds (method G5.3, G5.4, G5.5)."""
    total = len(layout.sizes)
    numbers = column.n_numeric
    notes: list[Deviation] = []
    taken = 0
    values: list[float] = []
    for place in range(total):
        band = layout.bands[place]
        pinned = place == 0 or (place == total - 1 and total >= 2)
        if band == _BAND_ZERO:
            values = values + [0.0]
            if pinned and rungs is not None:
                published = rungs[0] if place == 0 else rungs[10]
                if published != 0.0:
                    notes = notes + [
                        _deviation(
                            column.name,
                            "percentiles",
                            f"{published}",
                            "0",
                            "The column's count of values that are zero and "
                            "the end of its ladder cannot both hold, and the "
                            "count is the one the twin keeps.",
                        )
                    ]
            continue
        if pinned:
            if rungs is None:
                values = values + [_sign_fallback(band, None)]
            else:
                values = values + [rungs[0] if place == 0 else rungs[10]]
            continue
        if rungs is None:
            values = values + [_sign_fallback(band, None)]
            taken = taken + 1
            continue
        word = words[taken]
        taken = taken + 1
        numerator = layout.starts[place] * _WORD_SCALE + layout.sizes[place] * word
        found = _interpolated(rungs, numerator, numbers * _WORD_SCALE)
        if facts.integer_valued:
            found = _whole_valued(found)
        values = values + [found]
    repaired, repair_notes = _sign_repairs(column, facts, layout, rungs, values)
    return repaired, notes + repair_notes


def _sign_fallback(band: str, rungs: "tuple[float, ...] | None") -> float:
    """The value a stratum takes when the ladder cannot supply one."""
    if band == _BAND_NEGATIVE:
        if rungs is None:
            return -1.0
        return max(rungs[0], -1.0)
    if band == _BAND_POSITIVE:
        if rungs is None:
            return 1.0
        return min(rungs[10], 1.0)
    return 0.0


def _sign_repairs(
    column: contract.ColumnBlock,
    facts: contract.NumericFacts,
    layout: "_NumericLayout",
    rungs: "tuple[float, ...] | None",
    values: "list[float]",
) -> "tuple[list[float], list[Deviation]]":
    """Make every stratum's value carry its own sign (method G5.5).

    The ladder and the sign counts are separate published facts and
    nothing forces them to agree. Where they disagree the COUNTS win,
    because they are recounted from the written twin, and the deviation
    is measured against the ladder and named. A repair that moves an END
    of the ladder is named separately, because that end stops being a
    fact a recount can confirm.
    """
    total = len(values)
    notes: list[Deviation] = []
    repaired: list[float] = []
    for place in range(total):
        band = layout.bands[place]
        value = values[place]
        fallback = _sign_fallback(band, rungs)
        wrong = False
        if band == _BAND_NEGATIVE and value >= 0.0:
            wrong = True
        if band == _BAND_POSITIVE and value <= 0.0:
            wrong = True
        if wrong:
            if band == _BAND_NEGATIVE and fallback >= 0.0:
                fallback = -1.0
            if band == _BAND_POSITIVE and fallback <= 0.0:
                fallback = 1.0
            if facts.integer_valued:
                fallback = _whole_valued(fallback)
            value = fallback
            pinned = place == 0 or (place == total - 1 and total >= 2)
            if pinned:
                notes = notes + [
                    _deviation(
                        column.name,
                        "percentiles",
                        f"{values[place]}",
                        f"{value}",
                        "The end of this column's ladder and its counts of "
                        "negative and zero values cannot both hold, so the "
                        "twin keeps the counts and that end moves.",
                    )
                ]
        repaired = repaired + [value]
    return repaired, notes


def _whole_inside(
    value: float,
    band: str,
    share: "tuple[float, float] | None",
    ends: "tuple[float, float] | None",
    reach: int,
    taken: "dict[float, int]",
    later: "tuple[tuple[float, float], ...]" = (),
) -> "float | None":
    """A whole number this stratum can take, or None (method G6.4).

    The nearest whole number first, which is the half unit the rung
    window of G12.2 already owes. Where that one is another stratum's
    already -- which happens exactly where the ladder is FLAT, so the
    commonest value of a column and its published `min` are the same
    number -- the walk steps one unit at a time inside the stratum's own
    share of the ladder, and takes the first whole number no other
    stratum holds (review item P2-C4-F3). A value inside the stratum's
    own share costs the rung window nothing at all: G5.6 already bounds
    a rank by the width of the stratum covering it.

    THREE THINGS THE ANSWER MAY NEVER COST, whichever candidate it is.
    It never crosses zero, so `n_zero` and `n_negative` stay exactly
    what they were. It is never a number another stratum holds, so the
    count of different values does not fall. And it never leaves the
    published `min` and `max`, which is why `ends` binds the nearest
    candidate as well as the stepped ones: a stratum whose value
    interpolated to `88.5` rounds to `89` by the ties rule of G5.4, and
    on a column whose published `max` IS `88.5` that would move an
    EXACT-OBSERVABLE end of the ladder to buy a form. The walk takes
    `88` instead.

    HALF A UNIT OUTSIDE THE SHARE IS AS FAR AS ANY CANDIDATE GOES, and
    the stepped ones go exactly as far as the nearest one already does
    (review item P2-C5-F3). The nearest whole number to a value inside
    the share is at most half a unit outside it, and G12.2 widens the
    rung window by that half unit for every column this rule can touch;
    holding the stepped candidates to the share ITSELF bought nothing
    for that window and lost a form a column could write. A 39-cell
    producer column whose ladder is flat at `18` gave the flat stratum
    that number, and the stratum just below it -- whose share stops AT
    `18` and whose own `17` sits a fraction below the share -- was left
    with no candidate at all on the seeds where the nearest rounded up.

    A STRATUM REACHES OUTSIDE ITS OWN SHARE ONLY FOR A NUMBER NO LATER
    STRATUM'S SHARE HOLDS (review item P2-C5-F3). A stratum sitting just
    under a flat rung can round ONTO that rung's number -- the one
    number the stratum whose share IS that rung can ever be given -- and
    which of the two got it then turned on a drawn value: a 54-cell
    producer column publishing 26 point-free cells wrote 26 on some
    seeds and 20 on others, with nothing in the description telling
    those seeds apart. `later` is the shares of the strata still to be
    walked, and a candidate outside this stratum's own share that falls
    inside one of them is passed over. The pass costs this stratum
    nothing it was owed: every whole number of its OWN share, and every
    one within the half unit around it that no later stratum holds, is
    still open to it.

    The walk is bounded by `reach`, one more than the number of strata,
    because at most that many values can be taken.
    """
    want = _whole_valued(value)
    step = 0
    while step <= reach:
        for candidate in ([want] if step == 0 else [want + step, want - step]):
            if candidate in taken or not _carries_plainly(candidate, False):
                continue
            if band == _BAND_NEGATIVE and candidate >= 0.0:
                continue
            if band == _BAND_POSITIVE and candidate <= 0.0:
                continue
            if ends is not None and (
                candidate < ends[0] or candidate > ends[1]
            ):
                continue
            outside = share is None or (
                candidate < share[0] or candidate > share[1]
            )
            if outside:
                if share is None:
                    if step > 0:
                        continue
                elif (
                    candidate < share[0] - _HALF_UNIT
                    or candidate > share[1] + _HALF_UNIT
                ):
                    continue
                if _held_later(candidate, later):
                    continue
            return candidate
        step = step + 1
    return None


def _held_later(
    candidate: float, later: "tuple[tuple[float, float], ...]"
) -> bool:
    """True when a stratum still to be walked holds this number in its share.

    The later stratum's OWN share, not the half unit around it: a
    stratum whose share holds a number has no other claim on it to
    argue with, while one that can only reach the number from outside is
    asking for a neighbour's. Reading the widened range here instead
    made every small stratum a claimant over a span far wider than its
    cells cover, and cost more forms on a producer battery than it
    saved.
    """
    for share in later:
        if share[0] <= candidate <= share[1]:
            return True
    return False


def _whole_enough(
    column: contract.ColumnBlock,
    facts: contract.NumericFacts,
    layout: "_NumericLayout",
    rungs: "tuple[float, ...] | None",
    values: "list[float]",
) -> "list[float]":
    """Put whole values where the published style map needs them (G6.4).

    THE STYLE MAP AND THE VALUES ARE ONE QUESTION (review item
    P2-C2-F2). `plain`, `leading_zero` and `leading_plus` need a value
    that can be written with no point, and on a column publishing
    `integer_valued: false` the ladder hands back values that mostly
    cannot. A real column holding eleven fractions and forty whole
    numbers publishes forty `plain` cells, and its own values prove
    those forty are reachable, so the twin puts whole values on as many
    strata as the map asks for -- the FEWEST it needs, in stratum order
    -- rather than reporting a form it could have written.

    Three things are never traded for a style. The two pinned strata
    hold the published ends of the ladder and are left alone; a stratum
    is left alone where rounding would carry it across zero, so the
    counts of negative and zero values stay exactly what they were; and
    no stratum takes a whole number another stratum already holds, so
    the count of different values does not fall. What the NEAREST whole
    number costs is half a unit of the ladder, which is the same half
    unit the whole-number rule of G5.4 already spends, and method G12.2
    widens the rung window by it for exactly the columns this rule can
    touch. Where the nearest is another stratum's already, the stratum
    takes the nearest whole number inside its OWN SHARE of the ladder
    instead of giving up the published form (review item P2-C4-F3): a
    value inside its own share is what G5.6's window already allows, so
    that step costs the window nothing.
    """
    if facts.integer_valued:
        return values
    owed = min(_whole_demand(facts), column.n_numeric)
    if owed < 1:
        return values
    total = len(values)
    free = 0
    for place in range(total):
        if layout.bands[place] != _BAND_NEGATIVE:
            free = free + layout.sizes[place]
    quotas = _style_quotas(facts.numeric_styles)
    taken = {value: 1 for value in values}
    moved = [value for value in values]
    # THE LEADING-PLUS SHARE IS SERVED FIRST, AND ONLY WHERE IT CAN BE
    # WRITTEN (review item P2-C4-F3). A plus needs a value that is not
    # negative as well as one with no point, so a walk that stopped as
    # soon as the point-free count was covered could cover it entirely
    # out of the negative band and leave a published `leading_plus`
    # count with nowhere to go. This is the same order G5.2's carrier
    # step takes for the same reason.
    for wanted, reachable in (
        (min(quotas["leading_plus"], free), _REACHABLE[0]),
        (owed, _REACHABLE[1]),
    ):
        carried = 0
        for place in range(total):
            if layout.bands[place] not in reachable:
                continue
            if _carries_plainly(moved[place], False):
                carried = carried + layout.sizes[place]
        for place in range(total):
            if carried >= wanted:
                break
            if place == 0 or (place == total - 1 and total >= 2):
                continue
            if layout.bands[place] not in reachable:
                continue
            if _carries_plainly(moved[place], False):
                continue
            band = layout.bands[place]
            if band == _BAND_ZERO:
                continue
            share = None
            ends = None
            if rungs is not None:
                share = (
                    _interpolated(
                        rungs, layout.starts[place], column.n_numeric
                    ),
                    _interpolated(
                        rungs,
                        layout.starts[place] + layout.sizes[place],
                        column.n_numeric,
                    ),
                )
                ends = (rungs[0], rungs[10])
            want = _whole_inside(
                moved[place],
                band,
                share,
                ends,
                total + 1,
                taken,
                _shares_after(place, layout, rungs, column.n_numeric),
            )
            if want is None:
                continue
            taken[want] = 1
            moved[place] = want
            carried = carried + layout.sizes[place]
    return moved


def _shares_after(
    place: int,
    layout: "_NumericLayout",
    rungs: "tuple[float, ...] | None",
    numbers: int,
) -> "tuple[tuple[float, float], ...]":
    """The shares of the strata this walk has not reached yet (G6.4).

    Only the strata a whole number could still be given to: the two
    pinned ends hold the published `min` and `max` and the zero stratum
    holds `0`, so none of them is waiting for one.
    """
    if rungs is None:
        return ()
    total = len(layout.sizes)
    after: list[tuple[float, float]] = []
    for later in range(place + 1, total):
        if later == 0 or (later == total - 1 and total >= 2):
            continue
        if layout.bands[later] == _BAND_ZERO:
            continue
        after = after + [
            (
                _interpolated(rungs, layout.starts[later], numbers),
                _interpolated(
                    rungs,
                    layout.starts[later] + layout.sizes[later],
                    numbers,
                ),
            )
        ]
    return tuple(after)


def _style_wearable(value: float, whole_column: bool) -> int:
    """Which of the six styles one value's finished text could read as."""
    mask = 0
    for place in range(len(contract.NUMERIC_STYLES)):
        name = contract.NUMERIC_STYLES[place]
        if name in _WHOLE_STYLES and not _carries_plainly(value, whole_column):
            continue
        if name == "leading_plus" and value < 0.0:
            continue
        mask = mask | (1 << place)
    return mask


def _style_strata(
    quotas: "dict[str, int]",
    layout: "_NumericLayout",
    values: "list[float]",
    whole_column: bool,
    wanted: int,
    styles: "list[str]",
) -> "list[str]":
    """One form per stratum, where two forms would cost a spelling.

    A STYLE IS A WAY OF WRITING A VALUE, SO TWO STYLES INSIDE ONE
    STRATUM ARE TWO SPELLINGS OF ONE NUMBER (review item P2-C5-F3). The
    cell walk of G6.4 shares the styles out cell by cell, which is what
    keeps the way a number is written from being tied to its size -- a
    preference, and a good one, but not a published fact. `n_distinct`
    and `n_distinct_folded` ARE published, and a column with as many
    strata as it has spellings has no room for a split at all: the walk
    then meets the style map by missing the count of different values,
    which is one published count bought with another.

    So where the walk's own answer would spend more spellings than the
    column has, the styles are packed over whole strata instead, by the
    complete rule of `_allocation`: every quota is met exactly whenever
    any assignment of whole strata meets them all, and each stratum
    keeps one form. Where no such assignment exists the walk's answer
    stands and the recount names whatever it cost, which is the same
    honesty the rest of this module owes.
    """
    total = len(layout.sizes)
    if total < 1 or wanted < 1:
        return styles
    # THE PAIR IS THE VALUE AND THE FORM, NOT THE STRATUM AND THE FORM.
    # Two strata can hold the SAME number -- a column whose published
    # ladder is flat pins both ends onto one value -- and one number
    # written one way is one spelling however many strata wrote it. A
    # count over strata would see three claims where the column holds
    # three spellings and pack a map that was already exact.
    spent: dict[tuple[float, str], int] = {}
    at = 0
    for place in range(total):
        for _step in range(layout.sizes[place]):
            spent[(values[place], styles[at])] = 1
            at = at + 1
    if len(spent) <= wanted:
        return styles
    counts = [quotas[name] for name in contract.NUMERIC_STYLES]
    allowed = [
        _style_wearable(values[place], whole_column) for place in range(total)
    ]
    packed = _allotted(tuple(layout.sizes), counts, allowed)
    if packed is None:
        return styles
    settled: list[str] = []
    for place in range(total):
        name = contract.NUMERIC_STYLES[packed[place]]
        settled = settled + [name for _step in range(layout.sizes[place])]
    return settled


def _number_cells(
    column: contract.ColumnBlock,
    facts: contract.NumericFacts,
    layout: "_NumericLayout",
    values: "list[float]",
) -> "tuple[list[str], list[Deviation]]":
    """Write every cell that reads as a number (method G6.4, G6.5).

    Styles are shared out over the cells in stratum order by largest
    remaining quota, narrowed to the styles each cell's own value can
    actually wear and to the choices that leave every later quota
    placeable (method G6.4, review item P2-C2-F2). The leading-zero
    order is then the one degree of freedom left, spent on reaching the
    published count of different values -- and it is available INSIDE
    every style but `plain`, so a column reproducing a decimal or an
    exponent form can still hold more than one identity (review item
    P2-C2-F3). The published style counts are met FIRST and distinctness
    is met within them, which is the order plan P2-D6 fixes.

    WHERE THE CELL WALK WOULD SPEND A SPELLING THE COLUMN HAS NOT GOT,
    THE STRATA TAKE WHOLE STYLES INSTEAD (review item P2-C5-F3). Two
    styles inside one stratum write one value two ways, so they cost a
    spelling; a numeric column publishes how many different spellings it
    wrote, and where that count leaves no room the cell walk's split
    buys one published count with another. The styles are then packed
    over whole STRATA by the same complete rule the other roles use,
    which meets every style quota exactly whenever any assignment of
    whole strata does and leaves each stratum one form. It is reached
    for ONLY there: G6.4 shares styles out cell by cell so that the way
    a number is written is not tied to its size, and that preference is
    not a published fact while both of these are.
    """
    quotas = _style_quotas(facts.numeric_styles)
    wanted = min(layout.folded_budgets[0], column.n_numeric)
    holds: list[float] = []
    for place in range(len(layout.sizes)):
        for _step in range(layout.sizes[place]):
            holds = holds + [values[place]]
    styles = _style_places(
        quotas, holds, facts.integer_valued, _style_pool(facts.numeric_styles)
    )
    styles = _style_strata(
        quotas, layout, values, facts.integer_valued, wanted, styles
    )
    # THE PADDED EXCHANGE RUNS BEFORE ANY WIDTH IS ASSIGNED, and the
    # order is the whole of the rule. `_width_places` assigns a
    # FRACTION width to each cell it finds wearing `decimal`; the
    # exchange then moves styles between cells. Run the other way round
    # those assignments end up on cells that are no longer decimal,
    # while the cells that now are carry none -- a column publishing
    # forty-four cells at three figures after the point kept twenty-two
    # of them and wrote the rest at one, having met the padding census
    # exactly. One census was bought with another. Choosing the styles
    # first and the widths afterwards is what makes both reachable.
    styles = _padded_style_swaps(
        styles,
        holds,
        facts.pad_widths,
        _pinned_cells(layout, values),
        facts.integer_valued,
    )
    widths = _width_places(
        facts.fraction_widths,
        styles,
        holds,
        _pinned_cells(layout, values),
        _segment_bounds(column, facts, layout, values),
        _published_ends(facts, values),
        facts.integer_valued,
    )
    pads = _pad_places(
        facts.pad_widths, styles, holds, facts.integer_valued
    )
    base: list[str] = []
    for index in range(len(holds)):
        base = base + [
            _styled_number(
                holds[index],
                styles[index],
                1 if styles[index] == "leading_zero" else 0,
                facts.integer_valued,
                widths[index],
                pads[index],
            )
        ]
    # HOW MANY IDENTITIES THE COLUMN IS SHORT BEFORE ANY ZERO IS SPENT.
    # Counted over the whole column first, because a cell cannot tell
    # from where it stands whether the identities still to come will
    # cover the published count on their own. Spending a zero that was
    # not needed would carry the count PAST the published one, which is
    # a miss in the other direction and just as visible to somebody
    # grouping rows by this column.
    settled: dict[str, int] = {}
    for spelling in base:
        settled[parsing.folded(spelling)] = 1
    owed = max(0, wanted - len(settled))
    identities: dict[str, int] = {}
    spellings: dict[str, int] = {}
    cells: list[str] = []
    for index in range(len(holds)):
        style = styles[index]
        spelling = base[index]
        if (
            style != "plain"
            and owed > 0
            and pads[index] < 0
            and parsing.folded(spelling) in identities
        ):
            # A PUBLISHED FIELD WIDTH IS NOT SPENT ON AN IDENTITY, and
            # the ratified text is what says which way this goes. Every
            # order of the family writes ONE MORE FIGURE, so a column
            # whose census pins the field at five has exactly one
            # leading-zero spelling of each value and the family cannot
            # supply a second without leaving the width. That is the
            # case owner decision 11's authorization already names --
            # raw distinctness falls to the two-sided envelope "only
            # where even those cannot supply" -- so the shortfall is an
            # authorized approximation the report prints, while a
            # broken width would be a silent miss on the one fact a
            # person reading a code column actually depends on: a
            # width check, a slice, or a join against a five-figure
            # code fails on a six-figure cell, and nothing said a word.
            #
            # NO CEILING, BY OWNER DECISION 8. `0`, `00`, `000` and so
            # on supply as many different spellings of one value as a
            # description can ask for, and that unbounded supply is the
            # whole reason the owner chose this family over the
            # decimal-point pair. A fixed ceiling here would put the
            # ceiling back and lose a published count on any column
            # that asked for more. The family is reached for inside
            # every style but `plain`, so a column reproducing a decimal
            # or an exponent form can hold as many identities as the
            # description asks for (review item P2-C2-F3).
            #
            # The loop still terminates, and its bound is stated rather
            # than imposed: every order writes a different spelling of
            # the same value, so at most one order per identity already
            # taken can be refused, and the walk ends by the time it has
            # tried one more than that -- at most `len(identities) + 1`
            # steps, which is at most one more than the column's own
            # count of numbers.
            order = 1 if style == "leading_zero" else 0
            while parsing.folded(spelling) in identities:
                order = order + 1
                spelling = _styled_number(
                    holds[index],
                    style,
                    order,
                    facts.integer_valued,
                    widths[index],
                    pads[index],
                )
            owed = owed - 1
        identities[parsing.folded(spelling)] = 1
        spellings[spelling] = 1
        cells = cells + [spelling]
    # NO NOTE IS MADE HERE, and that is deliberate. This function used
    # to predict one style miss -- a leading plus with only negative
    # values left to put it on -- from its own bookkeeping. A prediction
    # made from what the writer INTENDED cannot see the miss that
    # matters most: on a column publishing `integer_valued: false` the
    # canonical spelling already carries a decimal point, so a cell this
    # function counted as `plain` reads back as `decimal` and the
    # published map is missed with the bookkeeping still balanced.
    # `_style_notes` recounts every form from the finished text instead,
    # which catches that case and this one, and reporting both would
    # name the same fact twice.
    return cells, []


# -- columns of dates and times (method G7) ---------------------------


def _clock_content(
    plan: "_ColumnPlan", words: "list[int]"
) -> "tuple[list[str], list[Deviation]]":
    """Every present cell of a column of clock times.

    TWO POPULATIONS AND ONE SUBTRACTION. `n_present - n_unparsed` cells
    parsed as clock times and are built first in rank order; exactly
    `n_unparsed` stand-ins follow. Nothing else divides the column.

    THE TWO ENDS ARE THE PUBLISHED TEXT, character for character, and
    neither draws a word. Every rank between them travels through the
    ordinal space the PUBLISHED FORM sets -- minutes of day for
    `hh-mm`, seconds of day for `hh-mm-ss` -- by the same floor-division
    interpolation the date rule uses, so no interpolated value is ever
    truncated or widened to fit its cell.

    WHY THE INTERPOLATION ALWAYS HAS AN ANSWER, written down rather than
    assumed. Each interior ordinal is computed inside one segment of
    the ladder, so it lies between that segment's two rungs; the ladder
    never goes backwards (T3), so no segment is inverted; and its two
    ends ARE the column's endpoints (T2), so every ordinal lies between
    them. Both endpoints are real cells of a closed finite space, so
    every ordinal is inside that space and has exactly one spelling in
    the column's form.

    THIS ROLE HAS NO OFFSET MACHINERY AND MAY NOT INVENT ANY. The clock
    role publishes none of the datetime role's ten offset and
    resolution keys, so there is no zone to carry, no reading to
    convert and no endpoint field surgery: a clock time is a place in
    the day and nothing else.
    """
    column = plan.column
    facts = column.facts
    if not isinstance(facts, contract.ClockFacts):
        raise _wrong_facts(column.name)
    form = facts.clock_form
    parsed = column.n_present - facts.n_unparsed
    ladder = [
        _clock_ordinal_of(facts.clock_percentiles[name], form)
        for name in _LADDER_NAMES
    ]
    # WHETHER THIS COLUMN'S VALUES WERE ALL DIFFERENT. The description
    # says so when its count of different values, net of the cells that
    # are stand-ins, is the count of cells that parsed -- and that
    # obligation is EXACT: the plan keeps it for this case even though
    # every other shape's distinctness falls to an envelope, because a
    # closed finite space of times has a place for each of them and the
    # construction can simply take the next one.
    apart = column.n_distinct - facts.n_unparsed >= parsed
    ceiling = _clock_ordinal_of(facts.latest, form)
    last = _clock_ordinal_of(facts.earliest, form)
    cells: "list[str]" = []
    taken = 0
    for rank in range(parsed):
        if rank == 0:
            cells = cells + [facts.earliest]
            continue
        if rank == parsed - 1 and parsed >= 2:
            cells = cells + [facts.latest]
            continue
        word = words[taken]
        taken = taken + 1
        numerator = rank * _WORD_SCALE + word
        denominator = parsed * _WORD_SCALE
        step = _segment(numerator, denominator)
        above = 100 * numerator - _PCT[step] * denominator
        span = (_PCT[step + 1] - _PCT[step]) * denominator
        ordinal = ladder[step] + (
            above * (ladder[step + 1] - ladder[step])
        ) // span
        if apart:
            # WHERE THE COLUMN'S OWN VALUES WERE ALL DIFFERENT, so are
            # the twin's. The interpolation is non-decreasing across
            # ranks -- each rank's share is larger than the last -- so
            # two ranks land on one time only where the ladder is
            # tighter than the ranks are numerous, and stepping the
            # later one up by a minute is what the source column itself
            # did. Bounded by the last rank, which is pinned to the
            # published latest: the room test above is what guarantees
            # there is a place for every one of them.
            if ordinal <= last:
                ordinal = last + 1
            if ordinal > ceiling:
                ordinal = ceiling
        last = ordinal
        cells = cells + [parsing.clock_spelling(ordinal, form)]
    # THE STAND-INS, which are outside the obligation to reproduce a
    # clock value and are counted rather than described. Each is
    # stepped past four things: a spelling this column already wrote, a
    # word this format reads as "no value", a spelling that would read
    # as a clock time in EITHER form -- which would quietly move
    # `n_unparsed` -- and a spelling this column publishes as a hole.
    used: "dict[str, int]" = {cell: 1 for cell in cells}
    holes = _hole_spellings(column)
    step = 1
    while len(cells) < column.n_present:
        candidate = _text_spelling(step, used, holes)
        step = step + 1
        if _reads_as_a_clock(candidate):
            continue
        if _is_a_hole_spelling(candidate, holes):
            continue
        cells = cells + [_take(candidate, used)]
    return cells, []


def _reads_as_a_clock(text: str) -> bool:
    """Whether this spelling would be read as a clock time at all.

    Either form, because a stand-in that reads as one under the form
    the column did NOT publish is still a cell the twin's own
    description counts differently from the description it was built
    from.
    """
    return parsing.clock_form(text) is not None


def _clock_ordinal_of(text: str, form: str) -> int:
    """One published clock value as its place in the form's own unit.

    The loader has already held every published clock value to that
    form (invariant T1), so the reader answers; a None here would be an
    internal contradiction rather than a document a person can write,
    and it is raised as one.
    """
    found = parsing.clock_ordinal(text, form)
    if found is None:
        raise errors.ProfileError(_INTERNAL_CLOCK)
    return found


def _datetime_content(
    plan: "_ColumnPlan", words: "list[int]"
) -> "tuple[list[str], list[Deviation]]":
    """Every present cell of a column of dates (method G7, G10.4).

    The parsed cells come first, in rank order, and the cells that did
    not read as a date follow as counted neutral stand-ins, which are
    explicitly outside the obligation to reproduce parsed values.
    """
    column = plan.column
    facts = column.facts
    if not isinstance(facts, contract.DatetimeFacts):
        raise _wrong_facts(column.name)
    parsed = column.n_present - facts.n_unparsed
    ladder = [
        _ordinal_of(rung, facts.resolution)
        for rung in facts.date_percentiles.rungs
    ]
    first = _ordinal_of(facts.earliest, facts.resolution)
    last = _ordinal_of(facts.latest, facts.resolution)
    offsets, notes = _offset_allocation(column, facts, parsed)
    # The spellings this column publishes among its absent cells, so
    # that no cell this run writes wears one (review item P4-DATE-F2).
    holes = _hole_spellings(column)
    cells: list[str] = []
    taken = 0
    for rank in range(parsed):
        end = ""
        if rank == 0:
            ordinal = first
            end = facts.earliest
        elif rank == parsed - 1 and parsed >= 2:
            ordinal = last
            end = facts.latest
        else:
            word = words[taken]
            taken = taken + 1
            numerator = rank * _WORD_SCALE + word
            denominator = parsed * _WORD_SCALE
            step = _segment(numerator, denominator)
            above = 100 * numerator - _PCT[step] * denominator
            span = (_PCT[step + 1] - _PCT[step]) * denominator
            ordinal = ladder[step] + (
                above * (ladder[step + 1] - ladder[step])
            ) // span
        offset = offsets[rank]
        # An end is written from the PUBLISHED instant's own fields, on
        # either clock and with no case that declines; only the ranks
        # between them travel through the ordinal space, which is exact
        # for every second the space has a place for (G7.3, G7.5).
        if end:
            written = _endpoint_cell(facts, end, offset)
        else:
            local = ordinal
            if (
                facts.datetimes_read_at == "utc"
                and facts.resolution == "datetime"
            ):
                local = ordinal + _offset_seconds(offset)
            written = _cell_of_ordinal(
                local,
                facts.resolution,
                facts.time_precision,
                facts.subsecond_digits,
            )
        text = written
        if _is_real_offset(offset) and offset:
            text = f"{text}{offset}"
        cells = cells + [_kept_datetime_cell(text, holes)]
    if parsed >= 1:
        notes = notes + _endpoint_notes(
            column, facts, "earliest", facts.earliest, cells[0], holes
        )
    if parsed >= 2:
        notes = notes + _endpoint_notes(
            column, facts, "latest", facts.latest, cells[parsed - 1], holes
        )
    used: dict[str, int] = {cell: 1 for cell in cells}
    for step in range(facts.n_unparsed):
        cells = cells + [_take(_text_spelling(step + 1, used, holes), used)]
    carried = [offset for offset in offsets if offset]
    if facts.datetimes_read_at == "utc" and len(set(carried)) < 2:
        notes = notes + [
            _deviation(
                column.name,
                "datetimes_read_at",
                "utc",
                "local",
                "Every offset this column carried was held back as too "
                "rare to publish, so the twin writes one kind of offset "
                "and reads back as a column on one clock.",
            )
        ]
    return cells, notes


def _parser_family(resolution: str) -> str:
    """The shipped date reader's name for one published resolution."""
    if resolution == "date":
        return "iso-date"
    if resolution == "quarter":
        return "year-quarter"
    if resolution == "month":
        return "iso-month"
    return "iso-datetime"


def _instant_written(text: str, facts: contract.DatetimeFacts) -> "str | None":
    """The instant one written twin cell reads back as, or None.

    The cell is read with the SHIPPED date reader, under the format its
    own resolution names, and put back on the clock the description
    says the published instants are written on -- so what comes out is
    comparable, character for character, with `earliest` and `latest`
    themselves. None says the cell did not read as a date at all.
    """
    found = parsing.parse_datetime(text, _parser_family(facts.resolution))
    if found is None:
        return None
    if facts.datetimes_read_at == "utc" and facts.resolution == "datetime":
        # The clock is put back only where it was applied. A whole date
        # and a quarter carry no time of day for an offset to move, so
        # the cell text IS the published instant for them, and asking
        # for a shared-clock reading of a quarter has no answer at all.
        return parsing.utc_canonical(found[0], found[1])
    return found[0]


def _kept_datetime_cell(text: str, holes: "tuple[str, ...]") -> str:
    """The same instant, spelled so the twin's own reader still sees it.

    THE COLLISION IS THE TWIN'S OWN DOING, WHICH IS WHY IT CAN BE
    UNDONE (review item P4-DATE-F2). A real table can hold a present
    cell at midnight written `2024-01-01` and, in the same column,
    eleven absent cells the person declared as `2024-01-01T00:00:00`.
    Those are two spellings and the description carries both facts
    honestly. The twin then writes every parsed cell at the column's
    finest precision, reaches for the second spelling, and hands back a
    cell its OWN description reads as absent -- so an exact endpoint
    walks out of the twin over a separator nobody chose.

    The date reader accepts three separators between the day and the
    time. The fixed one is `T`, and it stays fixed: this is asked only
    where that spelling is one the column publishes among its absent
    cells, and then the space form is offered, which reads back as the
    same instant at the same precision on the same clock. Where BOTH
    spellings are declared absent, nothing here can help and the
    original is returned so that the recount names the loss rather than
    hiding it behind a third spelling.

    Guarantees: accepts a written cell and the column's own absent
    spellings; returns that cell or an equivalent one. Determinism: a
    function of the two. Raises TypeError if handed anything that is
    not a string instance. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError("a twin cell reached the spelling rule as something else")
    if not _is_a_hole_spelling(text, holes):
        return text
    if len(text) < 11 or text[10] != "T":
        return text
    other = f"{text[0:10]} {text[11:]}"
    if _is_a_hole_spelling(other, holes):
        return text
    return other


def _endpoint_notes(
    column: contract.ColumnBlock,
    facts: contract.DatetimeFacts,
    key: str,
    published: str,
    written: str,
    holes: "tuple[str, ...]",
) -> "list[Deviation]":
    """Catch an end of a column of dates this run failed to write back.

    `earliest` and `latest` are EXACT-OBSERVABLE, with no corner and no
    exception, which means a person can read the twin, describe it again
    and find the same two instants. This asks that question of the cell
    this run actually wrote, rather than trusting the writing rule.

    THIS IS A DEFECT DETECTOR, NOT A ROUTE TO A LESSER END (review items
    P2-C3-F2 and P2-C4-F1). All three descriptions this used to name are
    refused where they are decided, by the contract's D10: seconds on a
    column recording whole minutes, a sixtieth second on the shared
    clock, and an end whose own offset carries its cell off the end of
    the calendar. So every description that reaches this function has an
    end the writing rule of G7.5 produces exactly, and anything else is
    a fault in this module -- the one the check exists to catch, which
    is a writing rule that stopped taking the end's own fields. It is
    still printed rather than swallowed, in the shape every other
    unmet fact is printed in, because a run that quietly drops the
    evidence of its own defect is the worse of the two failures.
    """
    found = _instant_written(written, facts)
    absent = _wears_a_published_hole(written, holes)
    if found == published and not absent:
        return []
    achieved = "a value that does not read as a date at all"
    if found is not None:
        achieved = found
    if absent:
        # ASKED THE WAY THE TWIN WILL BE READ (review item P4-DATE-F2).
        # A cell wearing a spelling this column publishes among its
        # absent ones is not a value at all when the twin is described
        # again, whatever instant its text would otherwise read as, so
        # the end is gone even though the bytes look right.
        achieved = "no value: the twin's own description reads that cell as absent"
    return [
        _deviation(
            column.name,
            key,
            published,
            achieved,
            "Describing the twin again finds the instant shown here "
            "rather than the published one. Every description this tool "
            "accepts has an end it can write exactly, so this line is a "
            "fault in the tool: please report it with the description "
            "that produced it.",
        )
    ]


def _offset_allocation(
    column: contract.ColumnBlock, facts: contract.DatetimeFacts, parsed: int
) -> "tuple[list[str], list[Deviation]]":
    """Which offset every parsed cell carries (method G7.4).

    The two ends take the offsets the description names for them, which
    is what makes those two facts ones a recount can confirm. The rest
    is spent over the remaining ranks in ascending order, taking the
    offset keys in the description's own sorted order with the two
    marker keys last.
    """
    left = {key: facts.utc_offsets[key] for key in facts.utc_offsets}
    given = ["" for _rank in range(parsed)]
    settled = [False for _rank in range(parsed)]
    notes: list[Deviation] = []
    if parsed >= 1:
        _pin_offset(0, facts.earliest_utc_offset, given, settled, left)
    if parsed >= 2:
        _pin_offset(parsed - 1, facts.latest_utc_offset, given, settled, left)
    keys = [key for key in sorted(left) if _is_real_offset(key)]
    keys = keys + [key for key in sorted(left) if not _is_real_offset(key)]
    open_ranks = [rank for rank in range(parsed) if not settled[rank]]
    pointer = 0
    for key in keys:
        while left[key] > 0 and pointer < len(open_ranks):
            if _is_real_offset(key):
                given[open_ranks[pointer]] = key
            left[key] = left[key] - 1
            pointer = pointer + 1
    if contract.WITHHELD in facts.utc_offsets and parsed > 0:
        notes = notes + [
            _deviation(
                column.name,
                "utc_offsets",
                f"{facts.utc_offsets[contract.WITHHELD]} values whose offset "
                f"was held back",
                "written with no offset at all",
                "The description does not say which offsets those values "
                "carried, so the twin has no published way to write them "
                "apart and writes them without one.",
            )
        ]
    return given, notes


def _pin_offset(
    rank: int,
    key: str,
    given: "list[str]",
    settled: "list[bool]",
    left: "dict[str, int]",
) -> None:
    """Give one end of the column the offset the description names (G7.4).

    The two ends are what make `earliest_utc_offset` and
    `latest_utc_offset` facts a recount can confirm, so an end that
    publishes "no offset" is settled here too rather than left in the
    general allocation, where it could otherwise be handed one.
    """
    if key not in left or left[key] < 1 or settled[rank]:
        return
    if _is_real_offset(key):
        given[rank] = key
    settled[rank] = True
    left[key] = left[key] - 1
    return


# -- columns of labels (method G8) ------------------------------------


def _label_content(
    plan: "_ColumnPlan",
) -> "tuple[list[str], list[Deviation]]":
    """Every present cell of a column of labels (method G8).

    A column of labels consumes no words: everything is fixed by
    published counts, which is why a fully determined one produces the
    same bytes whatever the seed is. The published levels come first in
    the description's own order, each level's spellings in the order
    method G8.1 fixes, then the levels the smallest-group-size rule held
    back.
    """
    column = plan.column
    facts = column.facts
    if not isinstance(facts, contract.LabelFacts):
        raise _wrong_facts(column.name)
    used: dict[str, int] = {}
    owners: dict[str, str] = {}
    cells: list[str] = []
    notes: list[Deviation] = []
    made_up = 0
    for entry in facts.levels:
        covered = 0
        for spelling in sorted(entry.variants):
            cells = cells + [spelling for _each in range(entry.variants[spelling])]
            covered = covered + entry.variants[spelling]
            used[spelling] = 1
            owners[parsing.folded(spelling)] = entry.label
        # WHETHER THE LABEL'S OWN SPELLING IS SPOKEN FOR. A level whose
        # published and held-back spellings do not reach its count is
        # finished below by writing the label itself, so that spelling
        # is reserved and a variant may not take it. Where they DO
        # reach the count nothing is left to write and the label's own
        # spelling is free -- and it is worth having, because it is the
        # one further spelling that folds onto the label while KEEPING
        # ITS WRITTEN FORM, where a trailing space does not (P4-D18).
        spare = _spare_label_rows(entry)
        for key in _withheld_keys(entry.variants_withheld):
            rows = int(key)
            for _each in range(entry.variants_withheld[key]):
                take = rows == spare
                variant = _variant_spelling(
                    entry.label, used, owners, take
                )
                if take:
                    spare = 0
                made_up = made_up + 1
                cells = cells + [variant for _row in range(rows)]
                covered = covered + rows
        if covered < entry.count:
            cells = cells + [
                entry.label for _row in range(entry.count - covered)
            ]
            used[entry.label] = 1
            owners[parsing.folded(entry.label)] = entry.label
    if made_up:
        notes = notes + [
            _deviation(
                column.name,
                "levels -> variants_withheld",
                f"{made_up} spellings that were held back",
                f"{made_up} neutral spellings made up in their place",
                "Those spellings were written by too few rows to publish, "
                "so the twin keeps the count and the values distinct; "
                "below the floor the spellings themselves are in no "
                "file synthtwin writes.",
            )
        ]
    number = 0
    # THE FORMS THIS COLUMN WAS WRITTEN IN, IF IT PUBLISHED ANY (plan
    # P4-D18). A long tail publishes a census of them, and it is the
    # role whose twin is mostly stand-ins; the sibling label roles
    # publish none, so the debt is empty for them and the neutral
    # `group-N` spelling stands as before.
    owing = _forms_owed(facts, cells)
    wanted = _shared_out(
        facts.suppressed_level_counts,
        owing,
        used,
        owners,
        _hole_spellings(column),
    )
    # Each form's place in its own supply, carried across the whole
    # column so no spelling is walked twice.
    walked: "dict[str, int]" = {}
    shaped = 0
    for place in range(len(facts.suppressed_level_counts)):
        size = facts.suppressed_level_counts[place]
        form = wanted[place]
        number, label = _made_up_label(
            number, used, owners, form, plan.all_holes, walked
        )
        # WHAT THE LABEL ACTUALLY WEARS, not what it was asked to wear
        # (review round 2 finding 12). The walk gives a form up when
        # its supply is spent or every spelling of it is refused, and
        # this counted the ASKING -- so a report said thirty-three
        # stand-ins were written in a published form when five of them
        # were `group-N`.
        if form and parsing.shape_form(label) == form:
            shaped = shaped + 1
        cells = cells + [label for _row in range(size)]
    if facts.suppressed_levels:
        # WHAT THE STAND-INS WERE WRITTEN IN IS PART OF THE NOTE (plan
        # P4-D18). A column publishing a census of written forms has
        # its stand-ins written in them, and a column publishing none
        # has the neutral spelling as before -- and a column can have
        # both, where the forms the held-back cells wore were
        # themselves too rare to name, so the count is given rather
        # than the reader left to guess which happened.
        made = (
            f"{facts.suppressed_levels} neutral labels made up in their place"
        )
        if shaped:
            made = (
                f"{facts.suppressed_levels} labels made up in their place, "
                f"{shaped} of them written in a form this column published"
            )
        notes = notes + [
            _deviation(
                column.name,
                "suppressed_levels",
                f"{facts.suppressed_levels} labels that were held back",
                made,
                "Those labels covered too few rows to publish, so the twin "
                "keeps their number and their sizes but not the labels.",
            )
        ]
    return cells, notes


def _withheld_keys(withheld: "dict[str, int]") -> "list[str]":
    """The keys of a multiplicity map in ASCENDING NUMERIC order (G8.1).

    Method G8.1 step 2 says ascending numeric order; the code sorted
    the key STRINGS, which in general puts `10` before `2`.

    ON A CONFORMING DOCUMENT THE TWO ORDERS AGREE, and this changes no
    twin's bytes (review round 1, test weakening 8). Section 5.3 of the
    contract pads a multiplicity key with leading zeros to a uniform
    width, and section 3.1 gives THIS as the reason for the padding:
    padded, the canonical key order and the numeric order coincide. So
    the string sort was right on every document a loader accepts.

    It is written this way anyway, and stated rather than left implied:
    the method says numeric, so the code says numeric, and a reader
    checking one against the other finds them agreeing on the words as
    well as on the answer. It costs one integer conversion per key.
    """
    ordered = [(int(key), key) for key in withheld]
    return [pair[1] for pair in sorted(ordered)]


def _spare_label_rows(entry: "contract.LevelEntry") -> int:
    """How many rows the level's own spelling may cover, or 0 for none.

    THE LABEL'S OWN SPELLING IS ONE MORE SPELLING, and where nothing
    else of the level needs it, it is the only further one that folds
    onto the label while KEEPING ITS WRITTEN FORM -- a case flip may
    already be published and a trailing space changes the form. So it
    is worth spending where it covers most: on the LARGEST held-back
    group, whose rows are the most cells that would otherwise be
    written in a form the column never had.

    It is spare only when the published and held-back spellings already
    cover the level's count. A level they do not cover is finished by
    writing the label itself, so that spelling is spoken for and a
    variant may not take it.
    """
    covered = 0
    for spelling in sorted(entry.variants):
        covered = covered + entry.variants[spelling]
    largest = 0
    for key in _withheld_keys(entry.variants_withheld):
        covered = covered + int(key) * entry.variants_withheld[key]
        largest = max(largest, int(key))
    if covered < entry.count:
        return 0
    return largest


def _variant_spelling(
    parent: str,
    used: "dict[str, int]",
    owners: "dict[str, str]",
    spare: bool = False,
) -> str:
    """One made-up spelling of a published label (method G8.2).

    Case flips first, in the binary-counter order the method fixes, and
    then trailing spaces, whose supply has no end. A candidate is
    stepped past when it is already used in this column, or when it
    would fold onto a DIFFERENT label -- so the published counts of
    folded identities stay exactly what the description says.

    ``spare`` OFFERS THE LABEL'S OWN SPELLING FIRST where nothing else
    of the level needs it. `E11.9` published beside three rows of
    `e11.9` held back is a level with exactly two spellings and one of
    them is the label; without this the walk skipped the label -- the
    binary counter calls it order zero and starts at one -- found its
    single case flip already published, and fell through to `E11.9 `,
    which is a DIFFERENT WRITTEN FORM. The form census then went
    unpaid, which is how this was found (P4-D18).
    """
    if spare and parent not in used:
        used[parent] = 1
        owners[parsing.folded(parent)] = parent
        return parent
    order = 0
    while order < 4096:
        order = order + 1
        candidate = _case_variant(parent, order)
        if candidate is None:
            break
        if candidate in used or parsing.folded(candidate) != parent:
            continue
        taken = parsing.folded(candidate) in owners
        if taken and owners[parsing.folded(candidate)] != parent:
            continue
        used[candidate] = 1
        owners[parsing.folded(candidate)] = parent
        return candidate
    spaces = 0
    while True:
        spaces = spaces + 1
        candidate = f"{parent}{_SPACE * spaces}"
        if candidate in used:
            continue
        used[candidate] = 1
        owners[parsing.folded(candidate)] = parent
        return candidate


def _forms_owed(
    facts: "contract.LabelFacts", written: "list[str]"
) -> "dict[str, int]":
    """Cells each published form still owes after what is already written.

    THE CELLS ALREADY WRITTEN PAY FIRST, and they are read rather than
    reasoned about. A twin writes the published spellings byte for byte
    and makes up the held-back ones, and every one of those cells wears
    a form -- so a debt taken from the census alone would be paid twice
    over and the census missed by exactly the cells the walk forgot it
    had written. This counts the column's own cells.

    Only the NAMED forms are here: the pooled key names no form, and a
    stand-in cannot be written in a form nobody published.
    """
    if not isinstance(facts, contract.LabelFacts):
        return {}
    owing: "dict[str, int]" = {}
    for form in sorted(facts.shape_forms):
        if form == contract.WITHHELD:
            continue
        owing[form] = facts.shape_forms[form]
    for cell in written:
        form = parsing.shape_form(cell)
        if form not in owing:
            continue
        if owing[form] > 0:
            owing[form] = owing[form] - 1
    return owing


# How many assignments the search below will look at before it settles
# for the greedy answer. A column with one published form settles at
# the first node; the bound is here so a column with many forms and
# many held-back levels cannot spend an unbounded time on an
# arrangement the report would name either way.
_SHARE_OUT_NODES = 20000

# How many held-back levels the search will walk at all. Past this the
# budget above runs out before an answer does, and the greedy walk is
# what the search would settle for -- so it is taken directly, which
# also keeps the walk's own bookkeeping small on a long tail.
_SHARE_OUT_PLACES = 256


def _shared_out(
    sizes: "tuple[int, ...]",
    owing: "dict[str, int]",
    used: "dict[str, int]",
    owners: "dict[str, str]",
    holes: "tuple[str, ...]",
) -> "list[str]":
    """Which published form each stand-in is written in, one per size.

    LARGEST DEBT FIRST IS NOT ENOUGH, and the case that breaks it is
    ordinary (review round 1 finding 4). Two forms owing 76 and 164
    cells, and twenty-five stand-ins covering five levels of eight rows
    and twenty of ten: the source's own arrangement is exact -- two
    eights and six tens make 76, three eights and fourteen tens make
    164 -- and paying the largest debt first hands every eight to the
    larger form and reaches neither count.

    So the arrangement is SEARCHED, over the sizes in descending order,
    trying the forms in descending order of what they still owe. The
    first arrangement that settles every debt exactly is taken; where
    none is found inside the node bound, the greedy walk's answer is
    taken instead and the twin's own report names whatever it missed.

    The search is a function of the description alone -- the sizes come
    from `suppressed_level_counts`, the debts from the census and the
    cells already written -- so two implementations reading one
    document reach the same arrangement.
    """
    names = [form for form in sorted(owing) if owing[form] > 0]
    if not names:
        return ["" for _each in sizes]
    order = sorted([(0 - sizes[place], place) for place in range(len(sizes))])
    places = [pair[1] for pair in order]
    left = {form: owing[form] for form in names}
    # HOW MANY DISTINCT SPELLINGS EACH FORM CAN STILL SUPPLY (review
    # round 2 finding 5). The debt is in CELLS and the supply is in
    # SPELLINGS, and they are not the same quantity: `@-%` owes 31
    # cells and can spell 260 of them, but a form of one figure owes 31
    # and can spell ten. An arrangement that settles every debt
    # arithmetically and asks a form for more distinct stand-ins than
    # it HAS is not an arrangement at all -- the walk exhausts the form
    # and writes neutral spellings, and the census is missed by the
    # cells it was built to meet.
    supply = {
        form: _usable_room(form, len(sizes), used, owners, holes)
        for form in names
    }
    chosen: "dict[int, str]" = {}
    # SETTLE EACH DEBT EXACTLY BY ARITHMETIC BEFORE SEARCHING FOR IT
    # (review round 3 finding 7). The walk below is a search over
    # arrangements and a search needs a bound; bounded at twenty
    # thousand nodes it missed an arrangement the SOURCE ITSELF
    # exhibits -- twelve levels whose debts of 31 and 74 are reached
    # only at node 67,208 -- and settled for 41 and 83 instead.
    #
    # Which sizes make one debt exactly is a question with an answer,
    # not a thing to hunt for: it is reachable-sums over the sizes,
    # and this walks the debts largest first, takes an exact subset
    # for each and hands the rest on. Where every debt is settled that
    # way the search is never entered.
    # THE SIZE GUARD COMES FIRST, BEFORE ANY ARRANGEMENT IS WORKED OUT
    # (review round 4 finding 5). It stood after the arithmetic pass,
    # so a long tail of a hundred thousand held-back levels reached
    # four thousand sums and then rescanned them for every remaining
    # group -- some four hundred million visits -- before the guard
    # that exists to stop exactly that was consulted. Past this many
    # places the greedy walk is what either pass would settle for
    # anyway, so it is taken directly.
    if len(places) > _SHARE_OUT_PLACES:
        return _greedily(sizes, places, owing, names, used, owners, holes)
    # BOTH WAYS ROUND BEFORE GIVING UP (review round 4 finding 4). One
    # debt taking an exact subset can leave another unreachable where
    # a different subset would not: debts of four and two, with sizes
    # three, two, two and one, are settled by `3+1` and `2` -- and
    # taking the larger debt first picks `2+2` and strands the other.
    # Trying the smaller debt first costs one more pass and reaches
    # the arrangement the source itself had.
    for biggest_first in (True, False):
        settled = _settled_by_sums(
            sizes, places, owing, names, supply, biggest_first
        )
        if settled is not None:
            return settled
    budget = [_SHARE_OUT_NODES]
    # SEARCHING ONLY THE SMALL CASES. Past this many places the search
    # would spend its budget without reaching an answer, and the greedy
    # walk below is what it would settle for anyway.
    if len(places) > _SHARE_OUT_PLACES:
        names = []
    if names and _settles(
        places, sizes, left, names, chosen, budget, supply
    ):
        return [
            chosen[place] if place in chosen else ""
            for place in range(len(sizes))
        ]
    return _greedily(sizes, places, owing, names, used, owners, holes)


def _greedily(
    sizes: "tuple[int, ...]",
    places: "list[int]",
    owing: "dict[str, int]",
    names: "list[str]",
    used: "dict[str, int]",
    owners: "dict[str, str]",
    holes: "tuple[str, ...]",
) -> "list[str]":
    """The one-pass arrangement, settling the largest debt first.

    Taken where no exact arrangement was found, and taken DIRECTLY on
    a column with more held-back levels than the search will walk. It
    is the arrangement this walk had before either the search or the
    arithmetic was written, and it leaves the smallest remainder a
    one-pass rule can.

    IT OWES THE SUPPLY RULE TOO, and its own comment promised it
    before the code did: a form of twenty-six spellings must not be
    handed a twenty-seventh place.
    """
    # NO EXACT ARRANGEMENT WAS FOUND, so the greedy one stands. It is
    # the arrangement this walk had before the search was written, and
    # it leaves the smallest remainder a one-pass rule can.
    #
    # IT OWES THE SUPPLY RULE TOO. The search learned that a form can
    # be asked for more distinct stand-ins than it can spell (review
    # round 2 finding 5); the fallback is reached on exactly the large
    # arrangements where that is most likely, so it counts spellings as
    # well as cells. Without this the fallback handed a form of
    # twenty-six spellings thirty-one places.
    _unused = names
    every = [form for form in sorted(owing) if owing[form] > 0]
    left = {form: owing[form] for form in every}
    spare = {
        form: _usable_room(form, len(sizes), used, owners, holes)
        for form in every
    }
    taken: "list[str]" = ["" for _each in sizes]
    for place in places:
        form = _neediest_form(_within_supply(left, spare))
        if not form:
            break
        taken[place] = form
        left[form] = max(0, left[form] - sizes[place])
        spare[form] = spare[form] - 1
    return taken


def _within_supply(
    left: "dict[str, int]", spare: "dict[str, int]"
) -> "dict[str, int]":
    """The debts of the forms that can still spell one more stand-in."""
    open_still: "dict[str, int]" = {}
    for form in sorted(left):
        if spare[form] > 0:
            open_still[form] = left[form]
    return open_still


def _settled_by_sums(
    sizes: "tuple[int, ...]",
    places: "list[int]",
    owing: "dict[str, int]",
    names: "list[str]",
    supply: "dict[str, int]",
    biggest_first: bool,
) -> "list[str] | None":
    """An arrangement settling every debt exactly, or None.

    Each debt in turn, largest first, takes an exact subset of the
    sizes still going spare. `_subset_making` answers which sizes make
    one total, by reachable sums rather than by search, so a debt no
    subset can make is known at once instead of hunted for.

    Not complete, and said so plainly: an exact subset taken for an
    early debt can leave a later one unreachable where another subset
    would not have. Where that happens this answers None and the
    search below runs exactly as it did. What it buys is every case
    where the debts are settled one at a time, which is the shape a
    real column has.
    """
    spare = [sizes[place] for place in places]
    where = list(places)
    taken: "dict[int, str]" = {}
    ordered = sorted([(0 - owing[form], form) for form in names])
    if not biggest_first:
        ordered = sorted([(owing[form], form) for form in names])
    for pair in ordered:
        form = pair[1]
        picked = _subset_making(spare, owing[form], supply[form])
        if picked is None:
            return None
        for slot in sorted(picked, reverse=True):
            taken[where[slot]] = form
            del spare[slot]
            del where[slot]
    answer = ["" for _each in sizes]
    for place in taken:
        answer[place] = taken[place]
    return answer


def _subset_making(
    spare: "list[int]", total: int, most: int
) -> "list[int] | None":
    """Which of ``spare`` sum to ``total`` in at most ``most`` parts.

    Reachable sums, walked once per size: `made[sum]` remembers which
    size was laid down to reach that sum and which smaller sum it was
    laid on, so the answer is read back rather than searched for.

    TWO RULES KEEP THE CHAIN HONEST, and the first version had neither
    (review round 4 finding 3). Each size is offered against the sums
    reachable WITHOUT it -- a snapshot taken before it is laid down --
    so no size is used twice. And a sum once reached is NEVER
    rewritten: rewriting it improved `3+3+3` to `8+1` after a larger
    sum had already been recorded as resting on it, and reading that
    chain back returned the same slot twice. It returned `[4, 4, 0]`
    for `[8,3,3,3,1]` making ten, which crashed the caller outright on
    one arrangement of sizes and silently underpaid on another.

    Both rules together make the chain strictly decreasing in slot, so
    a slot cannot repeat -- which is the property the caller needs and
    the one it did not have.
    """
    if total < 1:
        return []
    if most < 1:
        return None
    made: "dict[int, tuple[int, int]]" = {}
    reached: "dict[int, int]" = {0: 0}
    for slot in range(len(spare)):
        size = spare[slot]
        before = [(sum_so_far, reached[sum_so_far]) for sum_so_far in reached]
        for pair in before:
            sum_so_far = pair[0]
            parts = pair[1] + 1
            step = sum_so_far + size
            if step > total or step in reached or parts > most:
                continue
            reached[step] = parts
            made[step] = (slot, sum_so_far)
    if total not in made:
        return None
    picked: "list[int]" = []
    at = total
    while at:
        slot, before_sum = made[at]
        picked = picked + [slot]
        at = before_sum
    return picked


def _settles(
    places: "list[int]",
    sizes: "tuple[int, ...]",
    left: "dict[str, int]",
    names: "list[str]",
    chosen: "dict[int, str]",
    budget: "list[int]",
    supply: "dict[str, int]",
) -> bool:
    """Whether the sizes can settle every debt exactly, walked ITERATIVELY.

    IT RECURSED, AND A PRODUCER-VALID COLUMN CRASHED (review round 2
    finding 6). One frame per suppressed level, and a long tail can
    hold twelve hundred of them: a column of `steady` beside twelve
    hundred singleton codes raised a bare `RecursionError` before ever
    reaching the greedy fallback this function documents. The node
    budget bounded the WORK and could not bound the STACK.

    So the walk carries its own stack. Each entry is one place and how
    many of that place's forms have been tried; stepping forward pushes,
    exhausting a place's forms pops and undoes what that place took.
    The answer, the order and the budget are exactly what the recursive
    walk gave, so no arrangement moves.
    """
    depth = 0
    tried: "list[int]" = [0 for _each in places]
    while True:
        if depth >= len(places):
            settled = True
            for form in names:
                if left[form] != 0:
                    settled = False
            if settled:
                return True
            depth = depth - 1
            if depth < 0:
                return False
            place = places[depth]
            _given_back(left, supply, sizes, chosen, place)
            continue
        budget[0] = budget[0] - 1
        if budget[0] < 0:
            return False
        place = places[depth]
        size = sizes[place]
        # A PLACE MAY BE LEFT NEUTRAL, and the empty string is how
        # (review round 2 finding 4). Without it the search had to give
        # every held-back level a form, so a column owing six cells
        # with levels of three, three and four could not reach the
        # arrangement its own source had -- two threes and the four
        # left alone -- and overshot by one. The neutral choice is
        # offered LAST, so an arrangement that uses a form is preferred
        # to one that does not.
        offers = [(0 - left[form], form) for form in names]
        taken = False
        for step in range(tried[depth], len(offers) + 1):
            if step == len(offers):
                tried[depth] = step + 1
                chosen[place] = ""
                taken = True
                break
            form = sorted(offers)[step][1]
            if left[form] < size:
                continue
            if supply[form] < 1:
                continue
            tried[depth] = step + 1
            left[form] = left[form] - size
            supply[form] = supply[form] - 1
            chosen[place] = form
            taken = True
            break
        if taken:
            depth = depth + 1
            if depth < len(places):
                tried[depth] = 0
            continue
        # THIS PLACE IS SPENT: undo the place before it and try its
        # next form. Where there is no place before it, no arrangement
        # settles every debt and the caller falls back.
        tried[depth] = 0
        depth = depth - 1
        if depth < 0:
            return False
        _given_back(left, supply, sizes, chosen, places[depth])


def _given_back(
    left: "dict[str, int]",
    supply: "dict[str, int]",
    sizes: "tuple[int, ...]",
    chosen: "dict[int, str]",
    place: int,
) -> None:
    """Undo what one place took, so the walk can try its next choice."""
    form = chosen[place]
    if form:
        left[form] = left[form] + sizes[place]
        supply[form] = supply[form] + 1
    del chosen[place]


def _usable_room(
    form: str,
    wanted: int,
    used: "dict[str, int]",
    owners: "dict[str, str]",
    holes: "tuple[str, ...]",
) -> int:
    """How many spellings of one form this walk could still write.

    `_form_room` counts the spellings the form HAS; this counts the
    ones a stand-in may still wear HERE. Three differences, and each
    was a defect in turn:

    - a spelling may be refused outright -- `-@%%` has two thousand
      six hundred spellings and NOT ONE of them usable, every one
      opening with the character a spreadsheet reads as the start of a
      formula (review round 2 finding 5);
    - a spelling may already be TAKEN by a published label or an
      earlier stand-in, or fold onto one, so a form whose supply is
      twenty-six can have one left when twenty-five are spent (review
      round 3 finding 5);
    - and a spelling may be one this column reads as absent.

    IT STOPS AT `wanted`. The caller never needs a number larger than
    the places it has to fill, so a form of many letters costs this the
    number of stand-ins and not four thousand candidates -- which is
    what made it a cost on a wide table (round 3 finding 8).
    """
    room = min(_form_room(form), _STAND_IN_STEPS)
    usable = 0
    for step in range(room):
        if usable >= wanted:
            return usable
        candidate = _filled_form(form, step)
        if candidate in used or parsing.folded(candidate) in owners:
            continue
        if not _is_a_usable_stand_in(candidate, holes):
            continue
        usable = usable + 1
    return usable


def _neediest_form(owing: "dict[str, int]") -> str:
    """The published form owing the most cells, or "" where none owes any.

    Largest debt first, ties broken by the form's own spelling
    ascending, so the walk is a function of the description and of
    nothing else. A stand-in covers a fixed number of rows -- its
    level's size, which the description gives -- so the walk cannot
    choose HOW MUCH to pay, only WHERE, and paying the largest debt
    first is what leaves the smallest remainder when the sizes do not
    divide the debts evenly.
    """
    ordered = [(0 - owing[form], form) for form in sorted(owing)
               if owing[form] > 0]
    if not ordered:
        return ""
    return sorted(ordered)[0][1]


def _filled_form(form: str, step: int) -> str:
    """One spelling of one published form, stepped by ``step``.

    THE FORM SAYS THE SHAPE AND THE STEP SAYS WHICH ONE. Every `9` of
    the form takes a figure and every `@` takes a letter; every other
    character stands as itself, because the marks ARE the form. The
    step is taken apart into those positions by plain mixed-radix
    arithmetic, LEFTMOST FIRST, so consecutive steps differ and the
    form's whole supply is reachable: `@%%.%` at step 0 is `A00.0`, at
    step 1 `B00.0`, and the form holds 26 x 10 x 10 x 10 spellings
    before any repeats. Past that the spellings come round again, and
    the caller steps past what it has already written.

    IT CARRIES NO FRAGMENT OF ANY REAL VALUE. The form is built by
    replacing every figure and letter of a cell before it is published,
    and the figures and letters put back here come from the step, which
    is a count of made-up values and not a reading of anything.
    """
    figures = "0123456789"
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    spelling = ""
    place = _stepped_around(step, _form_room(form))
    for character in form:
        if character == parsing.SHAPE_DIGIT:
            spelling = spelling + figures[place % 10]
            place = place // 10
            continue
        if character == parsing.SHAPE_LETTER:
            spelling = spelling + letters[place % 26]
            place = place // 26
            continue
        spelling = spelling + character
    return spelling


# How many spellings of one form a stand-in walk will try before it
# gives the form up and writes the neutral spelling instead. A form of
# many letters holds more spellings than any run needs, and a walk that
# insisted on finding a usable one could spend an unbounded time on a
# document the loader accepted.
_STAND_IN_STEPS = 4096


def _form_room(form: str) -> int:
    """How many different spellings one form holds."""
    room = 1
    for character in form:
        if character == parsing.SHAPE_DIGIT:
            room = room * 10
        elif character == parsing.SHAPE_LETTER:
            room = room * 26
    return room


def _stepped_around(step: int, room: int) -> int:
    """``step`` moved around ``room`` so that every position varies.

    WHY THE PLAIN COUNTER WAS WRONG, and it was wrong in a way that
    changed a twin's ROLE. Two hundred and forty values taken in order
    out of a form holding a hundred thousand leave every position but
    the lowest at zero, so every cell ended `-0` -- and a column whose
    cells all end in the same three characters is not free text to the
    describer, it is a column of numbers wearing an affix. The twin's
    role no longer matched the source's.

    A STRIDE COPRIME TO THE ROOM IS A BIJECTION ON IT, so no two steps
    below the room collide and consecutive steps land far apart. The
    stride is taken near the golden section of the room, which spreads
    a short run about as evenly as a single multiplier can, and then
    walked up to the first value sharing no factor with the room.
    """
    if room < 4:
        return step % max(room, 1)
    stride = max(room * 61803 // 100000, 1)
    while _shares_a_factor(stride, room):
        stride = stride + 1
    return (step * stride) % room


def _shares_a_factor(one: int, other: int) -> bool:
    """Whether two whole numbers have any divisor above one."""
    left = one
    right = other
    while right:
        left, right = right, left % right
    return left != 1


def _form_words(form: str) -> int:
    """How many whitespace-separated words a form's spellings hold.

    Read off the FORM, because a space in a cell survives into its form
    unchanged -- only figures and letters are replaced -- so the word
    count of every spelling of a form is the form's own.

    Counted character by character rather than by splitting, because a
    census key comes off a document a loader read and the offline audit
    accepts no method call on a value it cannot trace to a string.
    """
    if not isinstance(form, str):
        raise TypeError("a written form is text")
    words = 0
    inside = False
    for character in form:
        if character == _SPACE or character == "\t":
            inside = False
            continue
        if not inside:
            words = words + 1
        inside = True
    return words


def _length_budget(
    facts: "contract.TextFacts",
    groups: "tuple[int, ...]",
    lengths: "list[int]",
) -> "list[int]":
    """How far this column's total length may move, each way, in cells.

    ONE CHARACTER EACH WAY, AND THE ONE IS MEASURED RATHER THAN
    CHOSEN. G12.6 holds the achieved mean inside a window narrower than
    a hundredth of a character on an ordinary column -- four
    thousandths on the case that found this defect -- so a budget
    stated as a fraction of the column is not a budget at all. Swept
    against two real columns: at a budget of half the rows, a fiftieth
    and a hundredth, a column whose census asks for lengths its average
    does not want misses `length.mean` outright; at ONE character each
    way it holds, and a blood-pressure column -- whose census asks for
    exactly the lengths its own values had -- still meets all four of
    its forms and its average.

    That is the precedence rule made arithmetic. An exact count
    outranks an approximated average (method G9.5), and here it spends
    the average's own slack to the last character and no further.

    The budget opens at whatever the packing's own lengths already
    spend, so a swap is measured against the walk that would have
    happened, not against a perfect one. Both halves are clamped at
    zero: a packing that already overspends buys no room by it.
    """
    total = 0
    for place in range(len(groups)):
        total = total + lengths[place] * groups[place]
    rows = 0
    for size in groups:
        rows = rows + size
    if rows < 1:
        return [0, 0]
    average = facts.length.mean
    if average is None:
        # NO PUBLISHED AVERAGE MEANS NO BUDGET TO KEEP, so the length a
        # form asks for costs nothing and every admitted one is open.
        return [total, total]
    wanted = int(round(average * rows))
    room = 1
    return [max(wanted + room - total, 0), max(total - (wanted - room), 0)]


def _spend_length(budget: "list[int]", moved: int, size: int) -> None:
    """Take one group's length swap out of the budget, both ways."""
    if moved == 0:
        return
    cost = moved * size
    if cost > 0:
        budget[0] = max(budget[0] - cost, 0)
        budget[1] = budget[1] + cost
        return
    budget[1] = max(budget[1] + cost, 0)
    budget[0] = budget[0] - cost


def _text_debt(facts: "contract.TextFacts") -> "dict[str, int]":
    """Cells each published form still owes, before anything is written."""
    owing: "dict[str, int]" = {}
    for form in sorted(facts.shape_forms):
        if form == contract.WITHHELD:
            continue
        owing[form] = facts.shape_forms[form]
    return owing


def _settle(owing: "dict[str, int]", spelling: str, cells: int) -> None:
    """Take one group's cells off the debt of the form it wears."""
    form = parsing.shape_form(spelling)
    if form not in owing:
        return
    owing[form] = max(0, owing[form] - cells)


def _wanted_form(
    owing: "dict[str, int]",
    length: int,
    words: int,
    carrier: bool,
    shortest: int,
    longest: int,
    budget: "list[int]",
    covering: int = 1,
) -> str:
    """Which published form this group is offered, or "" for none.

    A FORM FIXES A LENGTH -- every cell that wore one was exactly as
    long as it -- so which lengths a group may be offered is the whole
    question here, and the answer is not the one length the packing
    gave it.

    A GROUP CARRYING A PUBLISHED LENGTH END keeps its length exactly,
    because `length.min` and `length.max` are EXACT-OBSERVABLE and a
    twin that moved one would miss a fact it could have met. EVERY
    OTHER GROUP may take a form of another length, but ONLY WHILE THAT
    LEAVES THE PUBLISHED AVERAGE NO WORSE THAN IT FOUND IT.

    THE SECOND CLAUSE IS THE PRICE OF THE FIRST, and it was missing
    (review round 2 finding 9). Holding every group to its assigned
    length was how a blood-pressure column met the ONE form its middle
    length carried and missed the two beside it -- the packing had put
    almost every group at six characters, so nothing was left to write
    `%%/%%` or `%%%/%%%` and sixty cells came out of the wide alphabet.
    But letting every group move freely cost the average outright: a
    column publishing `length.mean` 4.8333 within a band four
    thousandths wide had a twin at 5.4875, which its own quality report
    called MISSED. An exact count outranks an approximated average
    (method G9.5) -- it does not get to spend one without limit.

    So a swap is offered only where the projected total length, taken
    over the groups already written and the groups still to come at the
    lengths the packing gave them, ends no further from the published
    total than it would have without the swap. The census is then paid
    out of the slack the average actually has, and no further. Where
    there is no slack the form is not offered and `_form_notes` says
    which counts went unmet.

    A space survives into a form unchanged, so the form's own word
    count must equal the group's either way.

    The debt is over CELLS and a group covers its own number of them,
    so the walk chooses only WHERE to settle: the form owing the most
    cells this group can be written in, ties broken by the form's own
    spelling. A group no form fits is written the way every free-text
    value was written before this rule, and the empty string says so.
    """
    fits: "list[tuple[int, int, str]]" = []
    for form in sorted(owing):
        if owing[form] < 1:
            continue
        if _form_words(form) != max(words, 1):
            continue
        if carrier:
            if len(form) != length:
                continue
        elif len(form) < shortest or len(form) > longest:
            continue
        elif not _length_affords(len(form) - length, budget):
            continue
        # A GROUP COVERS ITS OWN NUMBER OF CELLS AND GIVES THEM ALL TO
        # ONE FORM, so a form owing FEWER cells than this group covers
        # is overpaid by the difference. Such a form is offered LAST
        # rather than refused: refusing it outright was built and
        # measured WORSE -- the debt went unpaid AND the group fell out
        # of the form alphabet into ordinary text (residual R-P4-38).
        snug = 0 if owing[form] >= covering else 1
        fits = fits + [(snug, 0 - owing[form], form)]
    if not fits:
        return ""
    return sorted(fits)[0][2]


def _form_asks(
    owing: "dict[str, int]",
    groups: "tuple[int, ...]",
    lengths: "list[int]",
    counts: "list[int]",
    carriers: "tuple[int, int]",
    shortest: int,
    longest: int,
    budget: "list[int]",
) -> "list[str]":
    """One form asked of each group, decided LARGEST GROUP FIRST.

    WHY THE ORDER IS THE WHOLE RULE, and it is the lesson `_shared_out`
    already carries for a label column's stand-ins (review round 1
    finding 4): largest debt first is not enough. A group is a
    REPETITION group -- every cell of it holds the same value, so every
    cell of it wears one form -- and a walk that spends its single-cell
    groups early arrives at the last debts holding only groups too big
    to pay them.

    THE ORDINARY CASE IS A BLOOD PRESSURE COLUMN (residual R-P4-38).
    The demonstration table's has 374 groups of one cell and 13 of two,
    against form debts of 339, 32, 24 and 5. Taken in file order the
    walk reached `%%/%%` owing 1 and `%%/%%%` owing 1 while holding a
    group of TWO, which can pay neither, and paid one of them twice --
    a published census of 24 met with 25, at every seed. Taken largest
    group first the thirteen twos go to the 339, whose remainder 313
    and the debts 32, 24 and 5 come to exactly the 374 single-cell
    groups left over, and every count is met.

    THIS DECIDES THE ASK ONLY. The debt and the length budget are still
    settled in the walk against the spelling actually WRITTEN, because
    a form is an ask and not a promise, and a cell that comes back
    wearing something else must be counted as what it wears.
    """
    total = len(groups)
    asks = ["" for _each in range(total)]
    left = dict(owing)
    spare = list(budget)
    order = sorted([(0 - groups[place], place) for place in range(total)])
    for pair in order:
        place = pair[1]
        form = _wanted_form(
            left,
            lengths[place],
            counts[place],
            place in carriers,
            shortest,
            longest,
            spare,
            groups[place],
        )
        asks[place] = form
        if form:
            left[form] = max(0, left[form] - groups[place])
            _spend_length(spare, len(form) - lengths[place], groups[place])
    return asks


def _length_affords(moved: int, budget: "list[int]") -> bool:
    """Whether the published average can still afford one length swap.

    ``budget`` carries how far the twin's total length may still move
    from the total the published average asks for, in each direction:
    `budget[0]` is how much it may still grow and `budget[1]` how much
    it may still shrink. A swap that costs nothing -- the same length
    -- is always afforded and spends nothing.
    """
    if moved == 0:
        return True
    if moved > 0:
        return budget[0] >= moved
    return budget[1] >= 0 - moved


def _is_a_usable_stand_in(
    candidate: str, holes: "tuple[str, ...]" = ()
) -> bool:
    """Whether a made-up spelling may stand in a twin cell at all.

    The four properties `group-N` had by construction, asked of a
    spelling that no longer has them for free: it must not be one of
    the words that mean "no value", must read as neither a number nor a
    date, must carry no comma or quote, and must not begin with a
    character a spreadsheet reads as the start of a formula.

    AND A FIFTH THE GLOBAL VOCABULARY DOES NOT COVER (review round 2
    finding 8). `holes` is what THIS COLUMN publishes among its absent
    cells: the keys of its own `missing_by_source`, which this format
    writes character for character wherever the floor lets the column
    name them. Such a spelling means "no value" in THIS column and in
    no other. A shaped stand-in walked straight onto one: a diagnosis
    column whose absent cells were written `A00.0` had
    thirteen twin cells spelled `A00.0`, so the twin read back with two
    hundred and forty-one present cells where the description published
    two hundred and forty-three. The numeric walks have taken this
    population since they were written; these two did not.
    """
    if not candidate:
        return False
    if _is_a_hole_spelling(candidate, holes):
        # THE CONSERVATIVE HALF, because a spelling is being CHOSEN
        # here (review round 2 finding 8). It matches the way the
        # READER matches -- folded, and a vocabulary member its own
        # way -- so a column declaring `a-00` absent cannot be handed
        # a stand-in spelled `A-00`, which the reader would call
        # absent too. Raw membership missed exactly that.
        return False
    if parsing.is_missing_text(candidate):
        return False
    if parsing.classify_number(candidate) == parsing.NUMBER:
        return False
    for name in parsing.DATE_FORMATS:
        if parsing.parse_datetime(candidate, name) is not None:
            return False
    for character in candidate:
        if character == "," or character == '"':
            return False
    return candidate[0] not in "=+-@"


def _made_up_label(
    number: int,
    used: "dict[str, int]",
    owners: "dict[str, str]",
    form: str,
    holes: "tuple[str, ...]",
    walked: "dict[str, int]",
) -> "tuple[int, str]":
    """One label standing in for one that was held back (G8.3, P4-D18).

    WHERE THE COLUMN PUBLISHED THE FORMS ITS VALUES WERE WRITTEN IN,
    the stand-in is written in one of them. `group-14` is not a code:
    it is the wrong length, it is lower-case where the codes are not,
    and on a hyphenated scheme it carries a hyphen of its own -- so it
    passes a "looks segmented" check, crashes a split into fixed parts,
    and, the word being exactly five characters, makes a width check on
    the leading segment answer plausibly and wrongly.

    WHERE THE COLUMN PUBLISHED NONE it is `group-1`, `group-2` and so
    on, exactly as before: the three sibling label roles publish their
    levels, so their twins hold them and have no stand-in to shape.

    A COLLISION MOVES THE SPELLING AND NEVER THE FORM. The step is what
    the candidate is built from, so an earlier walk that advanced the
    step on a collision threw away the form that stand-in owed and the
    census went unpaid by exactly the collisions.

    Either way the spelling is stepped past anything already used in
    this column, raw or folded, and either way it is checked against
    the four properties the neutral spelling had by construction --
    `_is_a_usable_stand_in` asks them, because a spelling built to look
    like a code no longer has them for free.
    """
    if form:
        # THE FORM'S CURSOR IS CARRIED ACROSS STAND-INS, and the
        # counter for the neutral spelling is NOT TOUCHED here (review
        # round 2 finding 13, and the second defect its verification
        # found).
        #
        # It restarted at zero on every call, so two hundred stand-ins
        # of one form cost 1+2+...+200 probes and four thousand cost
        # eight million -- twelve seconds. The worst case was not the
        # big one: a form every spelling of which is refused, `-@%%`,
        # re-walked its whole supply for EVERY stand-in, so three
        # hundred held-back levels on a small column cost six seconds
        # against a fortieth of a second here.
        #
        # And the shaped probes were counted as neutral ones. Method
        # G8.3 says the invented labels are `group-1`, `group-2`, ...
        # in order, each number advanced WHEN IT COLLIDES; a mixed
        # column advanced it twenty thousand times without a single
        # collision and its twin held `group-20101`. A shaped walk now
        # leaves `number` exactly where it found it.
        room = min(_form_room(form), _STAND_IN_STEPS)
        if form not in walked:
            walked[form] = 0
        while walked[form] < room:
            candidate = _filled_form(form, walked[form])
            walked[form] = walked[form] + 1
            if candidate in used or parsing.folded(candidate) in owners:
                continue
            if not _is_a_usable_stand_in(candidate, holes):
                continue
            used[candidate] = 1
            owners[parsing.folded(candidate)] = candidate
            return number, candidate
    step = number
    while True:
        step = step + 1
        candidate = f"group-{step}"
        if candidate in used or parsing.folded(candidate) in owners:
            continue
        if not _is_a_usable_stand_in(candidate, holes):
            continue
        used[candidate] = 1
        owners[parsing.folded(candidate)] = candidate
        return step, candidate


# -- made-up values: the walk through a domain (method G9.2) ----------


def _has_letter(spelling: str) -> bool:
    """True when at least one character of ``spelling`` has a case."""
    return len([place for place in spelling if _has_case(place)]) > 0


def _letters_of(alphabet: "tuple[str, ...]") -> "tuple[str, ...]":
    """The characters of one alphabet that have a case, in its own order."""
    return tuple([figure for figure in alphabet if _has_case(figure)])


def _headed_spelling(
    head: "tuple[str, ...]",
    alphabet: "tuple[str, ...]",
    length: int,
    index: int,
) -> str:
    """The ``index``-th spelling whose first character comes from ``head``.

    The same plain counting as method G9.2, with the leftmost position
    drawn from a smaller alphabet: that is how a made-up value is held
    inside a band -- a first character that is a letter keeps a value
    out of the numbers, a first character outside the code alphabet
    keeps it out of the code-alphabet count -- without giving up the
    rest of the domain.
    """
    first = head[index % len(head)]
    rest = index // len(head)
    body = ""
    if length > 1:
        body = _raw_spelling(alphabet, length - 1, rest)
    return _fixed_ends(f"{first}{body}", alphabet)


def _pinned_spelling(
    alphabet: "tuple[str, ...]",
    length: int,
    used: "dict[str, int]",
    letter: bool,
    head: "tuple[str, ...] | None" = None,
) -> str:
    """The first free spelling of one alphabet at one exact length.

    The two extreme lengths of a column are pinned onto its first two
    made-up values, which is what makes the shortest and longest lengths
    facts a recount can confirm. Pinning costs no word, exactly like the
    ends of a ladder.
    """
    index = 0
    while index < 1000000:
        candidate = _spelling_at(alphabet, length, index, head)
        index = index + 1
        if letter and not _has_letter(candidate):
            continue
        if _free(candidate, used):
            return candidate
    return _spelling_at(alphabet, length, 0, head)


def _next_spelling(
    alphabet: "tuple[str, ...]",
    shortest: int,
    longest: int,
    state: "list[int]",
    used: "dict[str, int]",
    letter: bool,
    head: "tuple[str, ...] | None" = None,
) -> "tuple[str, bool]":
    """The next spelling of a column's domain, and whether it repeats.

    The domain is walked by ascending length from the shortest to the
    longest, and inside a length by ascending count, stepping past any
    spelling already used in this column. When the whole domain is spent
    the walk starts again FROM THE BEGINNING AND STOPS STEPPING PAST
    used spellings, so the repeats are spread evenly over the whole
    domain rather than piled onto one value: the fewest necessary values
    repeat, which is what owner decision 6 asks for on a declared column
    of record numbers, and the caller names it as a deviation.

    ``state`` is [length, count, spent], carried between calls, which is
    what makes a column's walk one walk rather than one per value.
    """
    length = state[0]
    index = state[1]
    spent = state[2] == 1
    steps = 0
    while steps < 1000000:
        steps = steps + 1
        if length > longest:
            length = shortest
            index = 0
            spent = True
            state[2] = 1
        if index >= _power_at_most(len(alphabet), length, index + 1):
            length = length + 1
            index = 0
            continue
        candidate = _spelling_at(alphabet, length, index, head)
        index = index + 1
        if letter and not _has_letter(candidate):
            continue
        if not spent and not _free(candidate, used):
            continue
        state[0] = length
        state[1] = index
        return candidate, spent
    return _spelling_at(alphabet, shortest, 0, head), True


def _whole_at(band: str, length: int, index: int) -> "str | None":
    """The ``index``-th whole number of one length, outside the figures.

    A description of record numbers can say all three of these at once:
    every value is a whole number, none is written in figures alone, and
    none is written in the code alphabet. A genuine column of `+1`, `+2`
    does say exactly that. All three hold together, and this is the
    construction that holds them: `1.` reads back as the whole number 1,
    is not figures alone, and holds a character the code alphabet does
    not. In the code band the exponent form `10e0` does the same job
    with characters the code alphabet does hold.

    None says this length has no such spelling -- one character cannot
    be a whole number and stand outside the figures at the same time --
    and the caller falls back to the ordinary walk and names what that
    costs.
    """
    if band == _BAND_CODE:
        if length < 3:
            return None
        return f"{_spelling_at(_DIGITS, length - 2, index)}e0"
    if length < 2:
        return None
    return f"{_spelling_at(_DIGITS, length - 1, index)}."


def _whole_room(band: str, length: int) -> int:
    """How many spellings `_whole_at` holds at one length, saturated."""
    if band == _BAND_CODE:
        if length < 3:
            return 0
        return _power_at_most(10, length - 2, _DOMAIN_CEILING)
    if length < 2:
        return 0
    return _power_at_most(10, length - 1, _DOMAIN_CEILING)


def _pinned_whole(
    band: str, length: int, used: "dict[str, int]"
) -> "str | None":
    """The first free whole-number spelling at one exact length.

    The walk is bounded and the bound is stated: every index writes a
    different spelling, so at most one index per piece of text already
    spoken for in this column can be refused.
    """
    ceiling = min(_whole_room(band, length), len(used) + 2)
    index = 0
    while index < ceiling:
        candidate = _whole_at(band, length, index)
        index = index + 1
        if candidate is None:
            return None
        if _free(candidate, used):
            return candidate
    return None


def _whole_spelling(
    band: str,
    shortest: int,
    longest: int,
    state: "list[int]",
    used: "dict[str, int]",
) -> "str | None":
    """The next whole-number spelling of a column's domain, or None.

    Lengths ascend from the shortest to the longest and, inside a
    length, the spellings ascend by count. None says the domain is spent
    -- and the walk is bounded, because a step either takes a fresh
    spelling, advances the length, or refuses a piece of text already
    spoken for, and there are only so many of each.
    """
    steps = 0
    ceiling = len(used) + (longest - shortest) + 2
    while state[0] <= longest and steps < ceiling:
        steps = steps + 1
        if state[1] >= _whole_room(band, state[0]):
            state[0] = state[0] + 1
            state[1] = 0
            continue
        candidate = _whole_at(band, state[0], state[1])
        state[1] = state[1] + 1
        if candidate is None:
            state[0] = state[0] + 1
            state[1] = 0
            continue
        if _free(candidate, used):
            return candidate
    return None


def _band_alphabet(band: str) -> "tuple[str, ...]":
    """The alphabet one band is written from (method G9.1)."""
    if band == _BAND_DIGITS:
        return _DIGITS
    if band == _BAND_CODE:
        return _CODE
    return _WIDE


def _band_head(band: str, whole: bool) -> "tuple[str, ...]":
    """What one band allows as a value's leftmost character (G9.5 step 3).

    The three bands exist to meet two published counts -- how many
    present cells are figures alone, and how many are written in the
    code alphabet -- and each band keeps its own count by what it puts
    first:

    - figures alone: any figure, or any figure but zero where the
      description records that every value is a whole number, so that a
      value's length is its count of figures (method G9.6);
    - the code alphabet: never a figure, so the value cannot be counted
      among the ones written in figures alone;
    - outside the code alphabet: a character the code alphabet does not
      hold, so the value cannot be counted among the ones that are.

    The space and the four characters a spreadsheet reads as the start
    of a formula are excluded from every band, so this set carries the
    positional rules of method G9.1 as well.
    """
    alphabet = _band_alphabet(band)
    permitted: list[str] = []
    for figure in alphabet:
        if figure == _SPACE or figure in _FORMULA_LEADERS:
            continue
        if band == _BAND_DIGITS and whole and figure == "0":
            continue
        if band == _BAND_CODE and parsing.is_digit_text(figure):
            continue
        if band == _BAND_WIDE and parsing.is_code_text(figure):
            continue
        permitted = permitted + [figure]
    return tuple(permitted)


# -- columns of record numbers (method G9.6) --------------------------


def _identifier_cells(
    column: contract.ColumnBlock, groups: "tuple[int, ...]"
) -> "tuple[list[str], list[Deviation]]":
    """Every present cell of a declared column of record numbers (G9.6).

    The values are made up. What this promises:

    - the length range, the whole-number fact and the two alphabet
      counts are kept in EVERY case, because owner decision 6 keeps the
      length. Each band leads with a character that holds its own
      alphabet count -- a value the description counts in the code
      alphabet never reads as figures alone -- so a person who recounts
      either count on the twin finds the published number;
    - where the description publishes fewer folded identities than
      spellings, the difference is BUILT, not named. The fold trims
      before it turns the case over, so a partner may differ from the
      value it folds onto in case, in edge spacing, or in both, and
      either construction leaves the trimmed characters -- and with them
      both alphabet counts -- exactly where they were. Edge spacing also
      lengthens, so a partner can carry the LONGEST published length
      while folding onto the shortest, which is how a column of one-,
      two- and three-character spellings of one identity is built rather
      than named (review item P2-C2-F6). Method G12 grants the fallback
      of naming a folded count that could not fall below its raw count
      to columns of numbers, and to no other role;
    - AND THE LAYOUT IS CHECKED AND REPAIRED, because whether a family
      can supply the collisions a layout asks it for is not knowable
      when the layout is chosen (method G9.3 step 5, plan amendment
      A-P3-12). A family's supply is its identities' own case positions
      plus whatever edge spacing their lengths leave over, and edge
      spacing only LENGTHENS, so an identity pinned to the longest
      published length supplies nothing at all. This walk laid the
      column out once and named the shortfall; on 44 of a 1,200-column
      battery of descriptions a real producer wrote -- every one of
      which its own values answer exactly -- that shortfall was the
      published folded count. The column is now laid out AGAIN where a
      collision could not be built: a family is asked for no more
      collisions than it was just shown to supply, a family owing one
      takes it on the slot carrying a published length end before any
      other, and a description whose first packing gives every group a
      family of its own is offered a packing that does not. **The first
      layout is tried first and is unchanged**, so a description the
      earlier rule answered exactly is answered the same way, byte for
      byte, and the repair can only reach a column the earlier rule
      already missed;
    - where the published length range cannot supply as many different
      values as the column has rows, values repeat and THREE facts about
      distinctness stop being reproduced -- raw, folded, and the
      repetition pattern itself -- each named beside what the
      description publishes, with the consequence for a join said in the
      person's own words.

    THE FOUR PARSER CLASSES ARE PACKED WITH THE TWO ALPHABET COUNTS, IN
    ONE ALLOCATION (review item P2-C5-F2). Revision 5 read the bands off
    the two alphabet counts and nothing else, and then wrote every value
    from its band's alphabet -- which decides what the shipped
    classifier makes of the cell without ever asking. A declared column
    of `N_7`, `no!!`, `x-y`, `913` and `-3` publishes 23 cells that read
    as numbers and 26 that do not, and its own five values are an exact
    assignment; the twin wrote 12 and 37 and named both. The four class
    counts are EXACT-OBSERVABLE on every role (plan P2-D6), so they are
    packed here beside the alphabets rather than recounted afterwards.

    Any count this cannot reach is measured from the written cells and
    named, never left for a reader to discover.
    """
    facts = column.facts
    if not isinstance(facts, contract.IdentifierFacts):
        raise _wrong_facts(column.name)
    total = len(groups)
    folded = min(column.n_distinct_folded, total)
    partners = total - folded
    room = len(_CLASSES) * len(_BANDS)
    shapes = [_identifier_families(column, facts, groups, folded, partners)]
    kept: tuple[list[str], list[Deviation]] | None = None
    # A REPAIR MAY NOT GIVE UP A COUNT THE FIRST LAYOUT HELD, AND THAT
    # IS MEASURED (review item P3-V6-F2). This read the rule off the
    # construction instead: it counted the notes a layout files for
    # itself -- the repeated spelling that gives up raw distinctness --
    # and argued that no other published count could move, because every
    # candidate packing meets every margin in ARITHMETIC. It can. A
    # packing settles which class and which alphabet each group answers
    # for; whether the family it names holds a spelling AT THE LENGTH the
    # slot is pinned to is a different question, and where it does not
    # `_pinned_identifier` falls back to the band's own alphabet and the
    # class count the packing met on paper is lost on the page. The
    # earlier enumeration never reached such a candidate because it
    # spent its budget on questions it had already answered; with the
    # budget repaired it does, so the guard stops arguing and RECOUNTS
    # the finished cells. A candidate is accepted only when it gives up
    # nothing the first layout held.
    allowance = -1
    conceded: frozenset[str] = frozenset()
    for tier in range(2):
        if tier == 1:
            wider = _identifier_packings(
                column, facts, groups, folded, partners, _FOLD_PACKINGS
            )
            if len(wider) < 2:
                break
            shapes = wider
        for step in range(len(shapes)):
            if tier == 1 and step < 1:
                continue
            for asking in range(2):
                asked: tuple[int, ...] = ()
                if asking:
                    asked = shapes[step][1]
                caps = [-1 for _cell in range(room)]
                for _again in range(total + 1):
                    built, notes, short, supply = _laid_identifiers(
                        column, facts, groups, folded, partners,
                        shapes[step], caps, asked,
                    )
                    if kept is None:
                        kept = (built, notes)
                        allowance = len(notes)
                        conceded = _identifier_shortfall(
                            column, facts, built
                        )
                    if _fully_folded(short) and len(notes) <= allowance and (
                        _identifier_shortfall(column, facts, built)
                        <= conceded
                    ):
                        return built, notes
                    moved = False
                    for cell in range(room):
                        if short[cell] < 1:
                            continue
                        if caps[cell] < 0 or caps[cell] > supply[cell]:
                            caps[cell] = supply[cell]
                            moved = True
                    if not moved:
                        break
    if kept is None:
        raise errors.ProfileError(
            f"synthtwin internal check: no layout at all was built for "
            f"the twin column '{parsing.visible(column.name)}'. This "
            f"means a mistake in synthtwin; please report it. Nothing "
            f"has been written."
        )
    return kept


def _fully_folded(short: "list[int]") -> bool:
    """Whether every collision this layout owed was actually built."""
    for cell in range(len(short)):
        if short[cell] > 0:
            return False
    return True


def _identifier_shortfall(
    column: contract.ColumnBlock,
    facts: contract.IdentifierFacts,
    written: "list[str]",
) -> "frozenset[str]":
    """Every published count of THIS column the written cells do not hold.

    RECOUNTED FROM THE CELLS, never restated from the packing (review
    item P3-V6-F2). A candidate packing meets the four class counts and
    the three alphabet counts as arithmetic over whole groups, which is
    what `_joint_allocation` answers; what a family can actually SPELL
    at the length its slot is pinned to is a separate question, and
    where the answer is nothing at all the walk falls back to the band's
    own alphabet and a count met on paper is missed on the page. So the
    layout the fold repair reaches for is held to what it wrote.

    The names are the description's own keys, so the comparison in
    `_identifier_cells` reads as the sentence it enforces: a repaired
    layout may give up no fact the first layout held. Counts that cannot
    move -- how many cells are present, how many are absent, and the
    occurrence multiset, which the groups fix before any spelling
    exists -- are not measured here; the two distinctness counts are,
    because they are exactly what the repair is trading in.

    Guarantees: reads only its arguments; no randomness and no I/O. The
    classifier and the two alphabet readers are the shipped ones, so
    this measures what a person recounting the twin would measure.
    """
    seen: dict[str, int] = {}
    for cell in written:
        if cell == "":
            continue
        if cell not in seen:
            seen[cell] = 0
        seen[cell] = seen[cell] + 1
    classes = {name: 0 for name in _CLASSES}
    digits = 0
    coded = 0
    shortest = 0
    longest = 0
    identities: dict[str, int] = {}
    for spelling in sorted(seen):
        many = seen[spelling]
        classes[parsing.classify_number(spelling)] = (
            classes[parsing.classify_number(spelling)] + many
        )
        bare = parsing.trimmed(spelling)
        if parsing.is_digit_text(bare):
            digits = digits + many
        if parsing.is_code_text(bare):
            coded = coded + many
        if shortest == 0 or len(spelling) < shortest:
            shortest = len(spelling)
        longest = max(longest, len(spelling))
        identities[parsing.folded(spelling)] = 1
    missed: list[str] = []
    owed = [
        ("n_numeric", classes[_CLASS_NUMBER], column.n_numeric),
        (
            "n_out_of_range",
            classes[_CLASS_OUT_OF_RANGE],
            column.n_out_of_range,
        ),
        (
            "n_contradictory",
            classes[_CLASS_CONTRADICTORY],
            column.n_contradictory,
        ),
        ("n_not_numeric", classes[_CLASS_TEXT], column.n_not_numeric),
        ("n_all_digits", digits, facts.n_all_digits),
        ("n_code_alphabet", coded, facts.n_code_alphabet),
        ("min_length", shortest, facts.min_length),
        ("max_length", longest, facts.max_length),
        ("n_distinct", len(seen), column.n_distinct),
        ("n_distinct_folded", len(identities), column.n_distinct_folded),
    ]
    for name, counted, published in owed:
        if counted != published:
            missed = missed + [name]
    return frozenset(missed)


def _laid_identifiers(
    column: contract.ColumnBlock,
    facts: contract.IdentifierFacts,
    groups: "tuple[int, ...]",
    folded: int,
    partners: int,
    shape: "tuple[list[int], tuple[int, int], bool]",
    caps: "list[int]",
    asked: "tuple[int, ...]",
) -> "tuple[list[str], list[Deviation], list[int], list[int]]":
    """One whole layout of a column of record numbers, and what it cost.

    This is the walk of G9.6 as it has always been, taken out of
    `_identifier_cells` so the repair above can run it more than once.
    Beside the cells it hands back two counts per family: how many
    collisions that family was ASKED for and could not build, and how
    many it did build. Those two are what the repair reads; nothing
    else about this walk changed.
    """
    total = len(groups)
    width = len(_BANDS)
    used: dict[str, int] = {}
    notes: list[Deviation] = []
    packed, pinned, signed = shape
    order = _collision_order(
        packed,
        folded,
        partners,
        [
            _family_folds(
                _CLASSES[cell // width],
                _BANDS[cell - (cell // width) * width],
                facts,
            )
            for cell in packed
        ],
        caps,
        asked,
    )
    cells = [packed[place] for place in order]
    groups = tuple([groups[place] for place in order])
    carriers = (_moved_to(order, pinned[0]), _moved_to(order, pinned[1]))
    kinds = [_CLASSES[cell // width] for cell in cells]
    bands = [_BANDS[cell - (cell // width) * width] for cell in cells]
    families = [
        f"{kinds[index]}/{bands[index]}" for index in range(total)
    ]
    asks = _letter_asks(families, folded)
    windows = _length_windows(
        total,
        facts.min_length,
        facts.max_length,
        facts.max_length > facts.min_length,
        carriers,
    )
    states: dict[str, list[int]] = {
        name: [facts.min_length, 0, 0] for name in families
    }
    short = [0 for _cell in range(len(_CLASSES) * width)]
    supply = [0 for _cell in range(len(_CLASSES) * width)]
    spellings: list[str] = []
    repeated = 0
    for index in range(total):
        kind = kinds[index]
        band = bands[index]
        # THE PERMISSION IS THIS GROUP'S, NOT THE COLUMN'S (review item
        # P3-C5-F1). The packing answers one question for the whole
        # column -- is there any assignment without the two-character
        # signed family -- and handing that one answer to every group
        # let groups with room for three characters take a sign as well,
        # because the walk starts at the shortest length and stops at
        # the first spelling it finds. A group may reach for the sign
        # only where its OWN length window admits nothing else: where
        # the window is the single width of two, which is what a
        # carrier pinned to a two-character end has, and what every
        # group has on a column no value of which may be longer.
        signed_here = signed and windows[index][0] == windows[index][1] == 2
        partner = _partner_of(
            index, folded, spellings, families, used, windows
        )
        if index >= folded >= 1 and index >= 1:
            if partner is None:
                short[cells[index]] = short[cells[index]] + 1
            else:
                supply[cells[index]] = supply[cells[index]] + 1
        if partner is not None:
            spellings = spellings + [_take(partner, used)]
            continue
        letter = asks[index] and band != _BAND_DIGITS
        spelling: str | None = None
        if index == carriers[0]:
            spelling = _pinned_identifier(
                kind, band, facts, facts.min_length, used, letter,
                signed_here,
            )
        elif index == carriers[1] and facts.max_length > facts.min_length:
            spelling = _pinned_identifier(
                kind, band, facts, facts.max_length, used, letter,
                signed_here,
            )
        else:
            spelling, again = _next_identifier(
                kind,
                band,
                facts,
                states[families[index]],
                used,
                letter,
                signed_here,
            )
            if again:
                repeated = repeated + 1
        _claim(spelling, used)
        spellings = spellings + [spelling]
    if repeated or len(set(spellings)) < total:
        notes = notes + _repeat_notes(column)
    return _grouped(groups, spellings), notes, short, supply


def _moved_to(order: "list[int]", place: int) -> int:
    """Where one group sits after the layout of `_collision_order`."""
    for step in range(len(order)):
        if order[step] == place:
            return step
    return place


def _family_folds(
    kind: str, band: str, facts: contract.IdentifierFacts
) -> bool:
    """Whether one record-number family can carry a fold collision at all.

    A partner is built by flipping a case or by adding edge spacing
    (G9.3). Edge spacing needs room in the published length range, and a
    case flip needs a value that HAS a case -- which a cell written
    inside accounting parentheses never does, and a cell written in
    figures alone never does either. A family that can do neither can
    carry no collision, so the layout below leaves the collisions to a
    family that can.
    """
    if facts.max_length > facts.min_length:
        return True
    if kind == _CLASS_TEXT:
        return len(_letters_of(_band_alphabet(band))) > 0
    if kind == _CLASS_CONTRADICTORY:
        return False
    if kind == _CLASS_OUT_OF_RANGE:
        return band != _BAND_DIGITS
    return band == _BAND_CODE and facts.max_length >= 3


def _collision_order(
    cells: "list[int]",
    folded: int,
    partners: int,
    folds: "list[bool]",
    caps: "list[int]",
    asked: "tuple[int, ...]",
) -> "list[int]":
    """Lay the groups out so a collision slot sits after its own family.

    A FOLD-COLLISION PARTNER CARRIES ITS PARENT'S FAMILY (G9.3), so a
    slot that has to carry one and whose family no earlier slot has can
    carry nothing at all. Which slot is an identity and which is a
    partner was the ascending occurrence order alone -- the last
    `partners` groups carried the collisions -- and that order knows
    nothing about the classes and alphabets the packing has just
    settled. On a producer column of `$D`, `$d`, `(-8)`, `*SMo`, `-0`,
    `38E999` and `38e999` the packing sends the three largest groups to
    three DIFFERENT families and every one of them to the tail, so two
    slots owe a collision and neither has a parent: the twin wrote seven
    folded identities where the description publishes five (review item
    P2-C5-F2, on the fold path the class packing reaches).

    So the tail is CHOSEN rather than taken. Each collision slot in
    turn is the LAST group whose family still has another member left
    among the groups not yet chosen -- so an earlier slot of that family
    is certain to remain an identity -- and where no family has one, the
    last remaining group, which is exactly the old order. Groups keep
    their relative order otherwise, so a column whose groups all share
    one family is laid out exactly as it was, byte for byte.

    Nothing published moves. The occurrence multiset pairs a size with a
    made-up value and never with a position; the packing's own margins
    are counts of cells, and every group keeps its own class, alphabet
    and size wherever it sits.

    ``caps`` AND ``asked`` ARE THE REPAIR'S TWO HANDLES, and both are
    empty on the layout every column is offered first (G9.3 step 5).
    ``caps`` holds one number per family -- the most collisions that
    family may be asked for, or -1 for no ceiling -- and is how a
    shortfall a finished layout MEASURED is handed back to the choice
    that caused it, since what a family can supply is a fact about
    spellings that do not exist here. ``asked`` names slots to take a
    collision before any other, and the repair puts the two carrying the
    published length ends in it: an identity pinned to the longest
    published length can be lengthened by nothing, so a family whose one
    identity sits there supplies no spaced partner at all, while the
    same family with the pin on its PARTNER instead supplies one. With
    both empty every pass below falls through to the rule above it, so
    the first layout is the layout this function always gave.
    """
    total = len(cells)
    if partners < 1 or partners >= total or folded < 1:
        return [place for place in range(total)]
    left = [place for place in range(total)]
    tail: list[int] = []
    taken = [0 for _cell in range(len(caps))]
    for _step in range(partners):
        picked = -1
        for capped in (True, False):
            for first in (True, False):
                for wanted in (True, False):
                    for place in range(len(left) - 1, -1, -1):
                        cell = cells[left[place]]
                        if folds[left[place]] != wanted:
                            continue
                        if first and left[place] not in asked:
                            continue
                        if capped and caps[cell] >= 0 and (
                            taken[cell] >= caps[cell]
                        ):
                            continue
                        kept = 0
                        for other in left:
                            if cells[other] == cell:
                                kept = kept + 1
                        if kept >= 2:
                            picked = place
                            break
                    if picked >= 0:
                        break
                if picked >= 0:
                    break
            if picked >= 0:
                break
        if picked < 0:
            picked = len(left) - 1
        taken[cells[left[picked]]] = taken[cells[left[picked]]] + 1
        tail = [left[picked]] + tail
        left = left[:picked] + left[picked + 1:]
    return left + tail


def _identifier_at(
    kind: str,
    band: str,
    facts: contract.IdentifierFacts,
    length: int,
    index: int,
    signed: bool = False,
) -> "str | None":
    """The ``index``-th record number of one class, band and length (G9.6).

    Each of the four families is the one method G9.6 fixes for it, and
    each is CLASS-PRESERVING by construction rather than by hope:

    - ordinary text is the band's own alphabet walk of G9.2, led by a
      character that keeps the value inside its band -- which is what
      revision 5 wrote for every group of every class;
    - a value that reads as a NUMBER is the whole-number spelling of
      G9.6 where the description says every value is a whole number --
      the figures themselves, `<digits>e0` inside the code alphabet,
      `<digits>.` outside it -- and otherwise the ordinary numeric
      family of G9.5 step 3;
    - a value too large or too small to hold, and one whose notation
      conflicts with itself, are G10.3's own constructions, which is how
      a description publishing them can be answered at all.

    None says this class cannot be written at this length in this band,
    and the packing rule never chooses such a pairing.
    """
    if kind == _CLASS_TEXT:
        return _spelling_at(
            _band_alphabet(band),
            length,
            index,
            _band_head(band, facts.all_whole_numbers),
        )
    if kind == _CLASS_NUMBER and facts.all_whole_numbers:
        if band == _BAND_DIGITS:
            return _spelling_at(
                _DIGITS, length, index, _band_head(band, True)
            )
        # THE TWO-CHARACTER CODE FAMILY IS KEPT, AND FLAGGED (owner
        # decision 9, 2026-08-13). `-0` through `-9` are the only
        # two-character spellings that are code-alphabet, not figures
        # alone, and read back as whole numbers, and each opens with the
        # character a spreadsheet reads as the start of a formula.
        #
        # The owner weighed the two ways of being wrong and chose this
        # one. A description carrying these counts PROVES the real
        # column held sign-leading values, since no other spelling of
        # that width exists -- so the twin inherits a hazard the table
        # already had rather than manufacturing one, which is the
        # distinction G9.1's bar was written to draw. Refusing instead
        # would leave the person with no twin at all over a character
        # their own file used; writing something else would leave them
        # developing code against a column that behaves differently from
        # the one they will run it on, which is the failure that costs
        # them a working analysis rather than a warning.
        #
        # So the cells are written, COUNTED, and named in the report's
        # formula paragraph every run -- which says plainly that these
        # were made up by synthtwin, so nobody reads them as values
        # their description published.
        if band == _BAND_CODE and length == 2 and signed:
            return _number_at(_BAND_CODE, 2, index)
        return _whole_at(band, length, index)
    # THE SAME GUARD ON THE PATH BESIDE IT. A column whose values are
    # not all whole numbers reaches the same two-character code family
    # through `_family_at`, and the reasoning does not change with the
    # published flag: the sign is permitted where the counts leave no
    # other spelling and refused where they do. Without this, a column
    # with room for three characters took the sign anyway, which is a
    # hazard the description never required.
    if kind == _CLASS_NUMBER and band == _BAND_CODE and length == 2 and (
        not signed
    ):
        return None
    return _family_at(kind, band, length, 1, index)


def _identifier_room(
    kind: str,
    band: str,
    facts: contract.IdentifierFacts,
    length: int,
    signed: bool = False,
) -> int:
    """How many spellings one record-number family holds, saturated (G9.4)."""
    if kind == _CLASS_TEXT:
        if band == _BAND_DIGITS:
            # FIGURES ALONE READ AS A NUMBER, whatever else they are, so
            # no cell of the ordinary-text class can be written in this
            # band at any length.
            return 0
        return _power_at_most(
            len(_band_alphabet(band)), length, _DOMAIN_CEILING
        )
    # A FAMILY WHOSE SPELLING IS NOT THIS WIDE DOES NOT EXIST HERE
    # (review item P2-C5-F2). On a column of free text the class
    # outranks the length -- a whole number too large to hold needs
    # three hundred and ten figures however short the column is, and
    # every length but the two pinned ones is approximated there. A
    # declared identifier has no approximated length at all:
    # `min_length` and `max_length` are EXACT-OBSERVABLE in every case,
    # since owner decision 6 keeps the length, and keeping the length is
    # the whole of what that decision buys. So the width the family
    # actually writes is checked against the width asked for, and a
    # family that cannot answer at this one is not offered to the
    # packing at all.
    first = _identifier_at(kind, band, facts, length, 0, signed)
    if first is None or len(first) != length:
        return 0
    if kind == _CLASS_NUMBER and facts.all_whole_numbers:
        if band == _BAND_DIGITS:
            return _power_at_most(10, max(length, 1), _DOMAIN_CEILING)
        if band == _BAND_CODE and length == 2 and signed:
            return 10
        return _whole_room(band, length)
    if kind == _CLASS_NUMBER and band == _BAND_CODE and length == 2 and (
        not signed
    ):
        return 0
    return _family_room(kind, band, length, 1)


def _identifier_permits(
    facts: contract.IdentifierFacts,
    shortest: int,
    longest: int,
    signed: bool = False,
) -> int:
    """The class-and-alphabet pairs one group may stand in (G9.6).

    A group of a declared column carries no length of its own -- the
    walk of G9.2 takes each value at the first length of the published
    range that still has a spelling free -- so the pairs it may stand in
    are the pairs SOME length of ``shortest`` to ``longest`` can write.
    The two groups carrying the published ends are held to one length
    each, and are asked about that one.
    """
    width = len(_BANDS)
    mask = 0
    for place in range(len(_CLASSES)):
        for band in range(width):
            for length in range(shortest, max(longest, shortest) + 1):
                if _identifier_room(
                    _CLASSES[place], _BANDS[band], facts, length, signed
                ) > 0:
                    mask = mask | (1 << (place * width + band))
                    break
    if mask == 0:
        return _every_bucket(len(_CLASSES) * width)
    return mask


# HOW MANY CANDIDATE PACKINGS THE FOLD REPAIR MAY EXAMINE on one column
# (method G9.3 step 5). The walk below is finite on its own -- the shape
# choices and the families are both finite -- but a column with many
# groups has a great many of both, and a run has to end in a stated
# number of steps rather than in however many the description happens to
# have. Where the budget is spent the column keeps the layout it already
# had and the shortfall is measured off the cells and named, exactly as
# before this repair existed.
_FOLD_PACKINGS = 256

# HOW MANY POSITIONS THE SECOND TIER MAY LOOK AT (review item P3-V6-F2).
# A budget counted in positions LOOKED AT rather than in questions
# ANSWERED buys whatever share of itself the loop order happens to leave
# over, because the same permission vector recurs under many candidate
# end-carriers and the allocation is a fixed function of that vector
# alone. Measured on the review's own witness: 2,466 positions carrying
# 246 different questions, and the stated ceiling of 256 ran out having
# answered 82 of them -- 168 of the 250 it gave this tier bought
# nothing -- so the walk stopped four candidates in, before the first
# candidate this tier had to offer. So the two are counted separately
# and both are stated: a
# question is answered at most `_FOLD_PACKINGS` times, and a position
# whose question is already answered costs a dictionary lookup and is
# not charged for it. This bounds the looking as well, since a walk that
# only ever re-asks still has to end.
_FOLD_LOOKS = 8192


def _identifier_packings(
    column: contract.ColumnBlock,
    facts: contract.IdentifierFacts,
    groups: "tuple[int, ...]",
    folded: int,
    partners: int,
    budget: int,
) -> "list[tuple[list[int], tuple[int, int], bool]]":
    """Every packing of G9.6 that meets every published count, in order.

    ``budget`` is how many DIFFERENT questions may be answered. A
    question here is one permission vector -- one mask per group -- and
    the allocation is a fixed function of that vector and of the
    published counts, so a vector already answered is answered from
    memory and is not charged for (review item P3-V6-F2). The ordinary
    run asks one question and gets the same answer, from the same walk
    in the same order, that this rule gave before the fold repair
    existed. More are asked only where a laid-out column could not build
    a collision it owes (G9.3 step 5).

    Two tiers, in this order, so the first answer is never a new one:

    1. **The shape search itself.** The two sign attempts of owner
       decision 9, and within each the candidate end-carriers in the
       fixed order of `_shape_choices`. A shape whose two carrying
       groups are the same SIZE as a shape already tried, or whose
       permissions come out the same, is stepped over: it can only
       repeat an answer already offered.
    2. **The same search with ONE group held to ONE family.** A
       description can have several exact packings and this walk returns
       the first; where that first gives every group a family of its
       own, no slot has a same-family sibling and the collision the
       description publishes can be built nowhere. Holding one group to
       one family and packing the rest is how the others are reached.
       THE PACKING WALK ITSELF IS UNTOUCHED -- what moves is the
       permission mask handed to it -- so this adds answers and changes
       none, and `_allotted_over`'s stated fill order, which four roles
       share, is exactly where it was.

    WHY THE COUNTING CHANGED, since a budget is a promise about what a
    walk reaches. The second tier's positions are a candidate end-carrier
    pair, a group and a family, and the permission vector it hands the
    allocator does not depend on the end-carriers except through the two
    places that carry them -- so the same question comes round again and
    again under end-carriers that make no difference to it. Charging the
    budget for a repeat spends the ceiling on nothing: the review's
    witness carried 246 different questions among 2,466 positions, the
    ceiling of 256 ran out having answered 82 of them, and the first
    candidate this tier had to offer sat at position 420. Charging only
    for a
    question actually put to the allocator leaves the allocator's work
    exactly where the amendment priced it -- at most `budget` packings
    solved -- while the walk reaches every question inside `_FOLD_LOOKS`
    positions. Both ceilings are stated, and where either is reached the
    column keeps the layout it already had and the shortfall is measured
    off the cells and named, exactly as before.

    Guarantees: reads only the description; a fixed function of its
    arguments, with no randomness and no I/O. The list may be empty,
    which says no assignment of whole groups meets every published
    count and the caller falls back.
    """
    total = len(groups)
    width = len(_BANDS)
    classes = [
        column.n_numeric,
        column.n_out_of_range,
        column.n_contradictory,
        column.n_not_numeric,
    ]
    alphabets = [
        facts.n_all_digits,
        facts.n_code_alphabet - facts.n_all_digits,
        column.n_present - facts.n_code_alphabet,
    ]
    found: list[tuple[list[int], tuple[int, int], bool]] = []
    # ONE QUESTION IS ONE PERMISSION VECTOR, and its answer is a fixed
    # function of that vector and of the counts above, so it is asked
    # once. `spent` counts the questions PUT TO THE ALLOCATOR, which is
    # the work the budget was always meant to bound.
    answers: dict[tuple[int, ...], list[int] | None] = {}
    spent = 0
    # THE PACKING DECIDES WHETHER THE SIGN IS THE LAST WAY, and no
    # predicate written by hand does (owner decision 9, 2026-08-13).
    # Two attempts are made in order: first with the two-character code
    # family CLOSED, so a description that can meet every published
    # count some other way does, and only then with it OPEN. Whichever
    # attempt succeeds is the answer, and the flag it succeeded under
    # travels back so the walk spells its cells the same way.
    #
    # This replaces two predicates that both got it wrong from the
    # published numbers alone -- one permitted a sign where three
    # characters were available, the other refused one where the
    # remaining bands genuinely could not carry a short cell -- because
    # what "no other spelling" means is exactly "no other assignment of
    # whole groups meets every published count", which is the question
    # this packer already answers completely.
    for signing in (False, True):
        sized: dict[tuple[int, int], int] = {}
        seen_permits: dict[tuple[tuple[int, int], ...], int] = {}
        for carriers in _shape_choices(total):
            if len(found) >= budget:
                return found
            shape = (groups[carriers[0]], groups[carriers[1]])
            if shape in sized:
                continue
            sized[shape] = 1
            permits = _identifier_windows(facts, total, carriers, signing)
            seen = tuple(sorted(
                [(groups[place], permits[place]) for place in range(total)]
            ))
            if seen in seen_permits:
                continue
            seen_permits[seen] = 1
            # THE FIRST TIER IS BOUNDED BY ITS OWN SHAPES, not by the
            # budget, and that is load-bearing: `_identifier_families`
            # asks for ONE candidate and the first shape it tries may
            # meet no count at all, so a tier that stopped spending
            # would hand back nothing and send the first layout of every
            # such column down the fallback walk. It stops at the first
            # candidate FOUND, exactly as it always did.
            question = tuple(permits)
            if question not in answers:
                spent = spent + 1
                answers[question] = _joint_allocation(
                    groups, classes, alphabets, permits
                )
            together = answers[question]
            if together is None:
                continue
            found = found + [(
                _collision_slots(
                    together,
                    groups,
                    folded,
                    partners,
                    permits,
                    _caseless_slots(together, facts, carriers, total),
                ),
                carriers,
                signing,
            )]
    if len(found) >= budget or not found:
        return found
    looked = 0
    for signing in (False, True):
        for carriers in _shape_choices(total):
            permits = _identifier_windows(facts, total, carriers, signing)
            for place in range(total):
                for cell in range(len(_CLASSES) * width):
                    if looked >= _FOLD_LOOKS or len(found) >= budget:
                        return found
                    if (permits[place] >> cell) & 1 == 0:
                        continue
                    looked = looked + 1
                    held = [permits[each] for each in range(total)]
                    held[place] = 1 << cell
                    question = tuple(held)
                    if question not in answers:
                        if spent >= budget:
                            return found
                        spent = spent + 1
                        answers[question] = _joint_allocation(
                            groups, classes, alphabets, held
                        )
                    together = answers[question]
                    if together is None:
                        continue
                    found = found + [(
                        _collision_slots(
                            together,
                            groups,
                            folded,
                            partners,
                            permits,
                            _caseless_slots(
                                together, facts, carriers, total
                            ),
                        ),
                        carriers,
                        signing,
                    )]
    return found


def _identifier_families(
    column: contract.ColumnBlock,
    facts: contract.IdentifierFacts,
    groups: "tuple[int, ...]",
    folded: int,
    partners: int,
) -> "tuple[list[int], tuple[int, int], bool]":
    """Which class and which alphabet every group of record numbers answers for.

    THE FOUR CLASS COUNTS AND THE TWO ALPHABET COUNTS ARE ONE QUESTION
    (review item P2-C5-F2). Revision 5 packed the alphabets alone and
    let the class fall out of the band's alphabet, which reads a
    published fact off a construction instead of meeting it: a group
    written from the figures reads as a number whether or not the
    description counts it as one, and a group written from the code
    alphabet reads as text whether or not it does. Both counts are
    EXACT-OBSERVABLE on every role (plan P2-D6), a group answers for one
    of each at the same time, and which PAIRS it can stand in depends on
    the lengths the description leaves open -- so the two are packed
    together, over the same grid the free-text rule of G9.5 uses and by
    the same complete walk.

    AND WHICH TWO GROUPS CARRY THE PUBLISHED LENGTH ENDS IS PART OF THAT
    SAME PACKING. Revision 5 gave the two ends to the description's
    first two values and said the shape search of G9.5 could not reach
    here, "because the band packing reads the two published alphabet
    counts and nothing else -- no group's length is an input to it".
    Once the classes are packed with the alphabets that reason is gone:
    a length decides which pairs a group can stand in at all -- one
    character cannot be a number and stand outside the figures at the
    same time -- so pinning an end onto a group chosen in advance can
    make a count unreachable that another pinning meets. A producer
    column of `-48562`, `14618`, `3`, `37e999`, `^slX` and `tA`
    publishes an exact assignment in its own values, and pinning the
    shortest length onto its two-row group -- whose value is six
    characters long and reads as a number outside the figures -- puts it
    somewhere that assignment never had it. The candidate shapes are
    offered in the fixed order of `_shape_choices`, so the
    description's own first two groups are tried first and a column the
    earlier rule already answered is answered the same way, byte for
    byte.

    Where NO shape and no packing of whole groups meets every count --
    which a description a real table produced does not reach, because
    that table's own values are such a packing -- the description's own
    first two groups carry the ends, the two families are decided one
    after the other, and every count missed is recounted from the
    finished cells and named.
    """
    total = len(groups)
    width = len(_BANDS)
    classes = [
        column.n_numeric,
        column.n_out_of_range,
        column.n_contradictory,
        column.n_not_numeric,
    ]
    alphabets = [
        facts.n_all_digits,
        facts.n_code_alphabet - facts.n_all_digits,
        column.n_present - facts.n_code_alphabet,
    ]
    found = _identifier_packings(column, facts, groups, folded, partners, 1)
    if found:
        return found[0]
    # NO EXACT ALLOCATION EXISTS, SO THE SIGN SECURES NOTHING (review
    # item P3-C5-F2). Reaching this line means neither search found an
    # assignment of whole groups meeting every published count, with the
    # family closed or open. Decision 9 permits the sign to MEET a count;
    # where no arrangement meets them, taking the hazard buys the person
    # nothing and the miss is named either way. So the fallback is
    # walked with the family closed.
    carriers = _shape_choices(total)[0]
    permits = _identifier_windows(facts, total, carriers, False)
    kinds = _allocation(
        groups,
        classes,
        [_identifier_classes(permits[index]) for index in range(total)],
    )
    bands = _allocation(
        groups,
        alphabets,
        [
            _identifier_bands_of(permits[index], kinds[index])
            for index in range(total)
        ],
    )
    together = [
        kinds[index] * width + bands[index] for index in range(total)
    ]
    return (
        _collision_slots(
            together,
            groups,
            folded,
            partners,
            permits,
            _caseless_slots(together, facts, carriers, total),
        ),
        carriers,
        False,
    )


def _identifier_windows(
    facts: contract.IdentifierFacts,
    total: int,
    carriers: "tuple[int, int]",
    signed: bool = False,
) -> "list[int]":
    """The pairs every group may stand in, under one choice of end carriers."""
    permits: list[int] = []
    for index in range(total):
        shortest = facts.min_length
        highest = facts.max_length
        if index == carriers[0]:
            highest = facts.min_length
        elif index == carriers[1] and facts.max_length > facts.min_length:
            shortest = facts.max_length
        permits = permits + [
            _identifier_permits(facts, shortest, highest, signed)
        ]
    return permits


def _identifier_classes(pairs: int) -> int:
    """Which classes one group can be written in at all, over its lengths."""
    width = len(_BANDS)
    mask = 0
    for place in range(len(_CLASSES)):
        for band in range(width):
            if (pairs >> (place * width + band)) & 1:
                mask = mask | (1 << place)
    if mask == 0:
        return _every_bucket(len(_CLASSES))
    return mask


def _identifier_bands_of(pairs: int, kind: int) -> int:
    """Which alphabets one group's class can be written in, over its lengths."""
    width = len(_BANDS)
    mask = 0
    for band in range(width):
        if (pairs >> (kind * width + band)) & 1:
            mask = mask | (1 << band)
    if mask == 0:
        return _every_bucket(width)
    return mask


def _pinned_identifier(
    kind: str,
    band: str,
    facts: contract.IdentifierFacts,
    length: int,
    used: "dict[str, int]",
    letter: bool,
    signed: bool = False,
) -> str:
    """The first free record number of one family at one exact length.

    The two extreme lengths of a declared column go to its first two
    made-up values (G9.2), which is what makes `min_length` and
    `max_length` facts a recount confirms at no cost in words. Where the
    family holds no spelling of that length at all, the walk falls back
    to the band's own alphabet and the recount names whichever published
    count that cost.
    """
    for asking in ((True, False) if letter else (False,)):
        ceiling = _identifier_room(kind, band, facts, length, signed)
        index = 0
        asked = 0
        while index < min(ceiling, len(used) + _ASK_STEPS + 2):
            candidate = _identifier_at(
                kind, band, facts, length, index, signed
            )
            index = index + 1
            if candidate is None:
                break
            if asking and not _has_letter(candidate):
                asked = asked + 1
                if asked >= _ASK_STEPS:
                    break
                continue
            if not _free(candidate, used):
                continue
            if parsing.classify_number(candidate) != _reads_as(kind):
                continue
            if parsing.is_missing_text(candidate):
                continue
            if _reads_as_a_date(candidate):
                continue
            return candidate
    return _pinned_spelling(
        _band_alphabet(band),
        length,
        used,
        letter,
        _band_head(band, facts.all_whole_numbers),
    )


def _next_identifier(
    kind: str,
    band: str,
    facts: contract.IdentifierFacts,
    state: "list[int]",
    used: "dict[str, int]",
    letter: bool,
    signed: bool = False,
) -> "tuple[str, bool]":
    """The next record number of one family, and whether it repeats.

    The domain is walked by ascending length from the shortest published
    to the longest and, inside a length, by ascending count, stepping
    past a spelling this column has already written and past one the
    shipped classifier does not read back as this family's own class.
    When the whole domain is spent the walk starts again from the
    beginning and stops stepping past used spellings, so the fewest
    necessary values repeat -- which is what owner decision 6 asks for,
    and the caller names it.

    THE FOLD-COLLISION ASK IS AN ASK AND NOT A CONDITION (method G9.2),
    and a family that holds no letter at all is the case that proves it
    (review item P2-C5-F2). A cell whose notation conflicts with itself
    is written inside accounting parentheses and holds no character with
    a case, so a walk that insisted on one there would step past its
    whole family for ever. After `_ASK_STEPS` refusals the pass gives
    up, the walk is put back exactly where that pass began, and the
    ordinary rule takes the same value it would have taken anyway; the
    folded count then comes up short and the recount names it, which is
    better than losing the class count as well.

    ``state`` is [length, count, spent], carried between calls, which is
    what makes a column's walk one walk rather than one per value.
    """
    began = [state[0], state[1], state[2]]
    found = _walked_identifier(
        kind, band, facts, state, used, letter, signed
    )
    if found is None and letter:
        state[0] = began[0]
        state[1] = began[1]
        state[2] = began[2]
        found = _walked_identifier(
            kind, band, facts, state, used, False, signed
        )
    if found is not None:
        return found
    return (
        _spelling_at(
            _band_alphabet(band),
            facts.min_length,
            0,
            _band_head(band, facts.all_whole_numbers),
        ),
        True,
    )


def _walked_identifier(
    kind: str,
    band: str,
    facts: contract.IdentifierFacts,
    state: "list[int]",
    used: "dict[str, int]",
    letter: bool,
    signed: bool = False,
) -> "tuple[str, bool] | None":
    """One pass of a record-number family's walk, from where it stopped."""
    length = state[0]
    index = state[1]
    spent = state[2] == 1
    steps = 0
    asked = 0
    while steps < 1000000:
        steps = steps + 1
        if length > facts.max_length:
            length = facts.min_length
            index = 0
            spent = True
            state[2] = 1
        if index >= _identifier_room(kind, band, facts, length, signed):
            length = length + 1
            index = 0
            continue
        candidate = _identifier_at(
            kind, band, facts, length, index, signed
        )
        index = index + 1
        if candidate is None:
            length = length + 1
            index = 0
            continue
        if letter and not _has_letter(candidate):
            asked = asked + 1
            if asked >= _ASK_STEPS:
                return None
            continue
        if not spent and not _free(candidate, used):
            continue
        if parsing.classify_number(candidate) != _reads_as(kind):
            continue
        if parsing.is_missing_text(candidate):
            continue
        if _reads_as_a_date(candidate):
            continue
        state[0] = length
        state[1] = index
        return candidate, spent
    return None


def _partner_at(
    parent: str, order: int, shortest: int, longest: "int | None"
) -> "str | None":
    """The ``order``-th fold-collision partner of ``parent`` (G9.3).

    THE FOLD IS TRIM-THEN-CASE-FOLD, AND SO IS THIS FAMILY. The shipped
    fold used by the producer and by every recount here trims the two
    ends of a value before it turns the case over, so a partner may
    differ from its parent in case, in edge spacing, or in both, and all
    three fold onto the same identity. An earlier rule offered case
    alone, which left a whole set of feasible collisions unbuildable --
    a value one character wide with a single letter carries exactly one
    case variant, so a description asking three collisions of it lost
    the published folded count even though its own source column shows
    the pattern being asked for (review item P2-C2-F6).

    The family is enumerated in a fixed order, so two implementations
    build the same partners:

    * the spacing is taken in ascending TOTAL, and within one total the
      leading share ascends: no spacing, then one space (trailing, then
      leading), then two (trailing pair, one each side, leading pair),
      and so on;
    * within one spacing, the case flips of method G8.2 are taken in
      ascending binary-counter order, the unflipped parent first;
    * the parent itself -- no spacing and no flip -- is not one of its
      own partners and is stepped over.

    Case flips therefore come first and in exactly the order they came
    in before this family was widened, so a column whose collisions case
    alone could carry writes what it wrote before.

    ``shortest`` and ``longest`` are the lengths this partner is
    permitted to take -- the published length range of the column, or
    the one pinned length where this value carries a published end.
    ``longest`` of None says the description publishes no longest
    length, and the spacing then has no end. Spacing only ever LENGTHENS
    a value, so a parent already longer than ``longest`` has no partner
    at all and None is handed back.

    Guarantees: accepts text, a counting number from one upward and a
    length window; returns text or None, where None says this parent's
    family is spent inside that window. A fixed function of its
    arguments, with no randomness and no I/O.
    """
    if order < 1:
        return None
    places = len([place for place in range(len(parent))
                  if _has_case(parent[place])])
    flips = 1 << places
    spread = max(0, shortest - len(parent))
    left = order
    while longest is None or len(parent) + spread <= longest:
        room = (spread + 1) * flips
        if spread == 0:
            room = room - 1
        if left <= room:
            seat = left - 1
            if spread == 0:
                seat = seat + 1
            lead = seat // flips
            flip = seat % flips
            built = parent
            if flip:
                turned = _case_variant(parent, flip)
                if turned is None:
                    return None
                built = turned
            return f"{_SPACE * lead}{built}{_SPACE * (spread - lead)}"
        left = left - room
        spread = spread + 1
    return None


def _levels_past_the_line(
    spellings: "list[str]", groups: "tuple[int, ...]", line: int
) -> int:
    """How many folded levels of these spellings reach the long-tail line.

    MEASURED ON THE FINISHED SPELLINGS rather than counted inside the
    walk that made them, and that is deliberate. A count taken in the
    walk knows only about pairs the walk itself made; this one sees
    every level however it arose, which is the thing a reader of the
    twin actually meets. It also keeps `_partner_of` returning one
    value: three roles ask that function, and a test pins that it is
    one function.

    Guarantees: accepts the spellings and the row count each covers, in
    one index space, and the line; returns a count. Raises nothing
    beyond the type check its own folding does. No I/O.
    """
    if line < 1:
        return 0
    covered: "dict[str, int]" = {}
    for index, spelling in enumerate(spellings):
        if index >= len(groups):
            break
        key = parsing.folded(spelling)
        # Indexed behind an `in` test rather than `.get`: the offline
        # audit refuses a method call on a value it cannot trace, and
        # this module reads every one of its own tallies this way.
        if key in covered:
            covered[key] = covered[key] + groups[index]
        else:
            covered[key] = groups[index]
    past = 0
    for key in sorted(covered):
        if covered[key] >= line:
            past = past + 1
    return past


def _partner_of(
    index: int,
    folded: int,
    spellings: list[str],
    families: "list[str]",
    used: "dict[str, int]",
    windows: "list[tuple[int, int | None]]",
    sizes: "list[int] | None" = None,
    long_tail_line: int = 0,
    carried: "dict[int, int] | None" = None,
) -> "str | None":
    """The fold-collision partner this value carries, when one is owed.

    Where a column publishes fewer folded identities than spellings, the
    difference is exactly the number of values that must fold onto one
    already there (method G9.3). Partners are handed out to the
    identities in ascending order, one each and then a second each, so
    the collisions are spread rather than piled on one value. None says
    this value owes no partner, or that no earlier value of the same
    family has a partner left inside this value's own length window.

    ``families`` says which published counts each value is answering
    for -- its alphabet, and on a column of free text its numeric class
    as well. A partner is only ever taken from a value of its own
    family, because a partner carries its parent's family with it: both
    constructions leave the trimmed characters alone, so the alphabet
    counts and the numeric class a recount reads are the parent's, and
    varying a value of some other family would meet the folded count by
    quietly missing a different published one -- the trade this module
    never makes silently.

    ``windows`` gives, for each value, the lengths that value is
    permitted to take. A value carrying a published END of the length
    range gets that one length, so the pin survives being answered by a
    partner; every other value gets the whole published range. The FIRST
    value is never a partner, because there is nothing yet to fold onto.
    The second no longer is barred: edge spacing lengthens a value, so a
    partner CAN carry the longest published length while folding onto
    the shortest, which is exactly the pattern a real column of one-,
    two- and three-character spellings of one identity shows (review
    item P2-C2-F6).

    EVERY SLOT WALKS ITS PARENT'S FAMILY FROM THAT FAMILY'S OWN START
    (method G9.3 step 2, review item P2-C4-F4). Which member a slot
    takes is the FIRST one the column has not written whose length this
    slot's window admits; it is not the member whose position matches
    this slot's own ordinal among the partners. Starting at that ordinal
    steps over a member no window turned down and nothing has written --
    on a four-spelling column of one identity in figures it wrote `1  `,
    ` 1`, ` 1 ` where the family order gives `1  `, `1 `, ` 1` -- and
    two conforming implementations then write different bytes for one
    description, which is the one thing the frozen vectors exist to
    stop. The number of partners a parent has already supplied still
    decides which PARENT comes next, below; it never decides which
    member of a family is taken. Where the slot's shortest permitted
    length is longer than the parent, `_partner_at` starts at the total
    of spaces that reaches it, which is the only place the start moves.

    The walk over one parent's family is bounded and the bound is stated
    rather than imposed: distinct orders build distinct spellings, so at
    most one order per piece of text this column has already recorded
    can be refused, and the walk ends by the time it has tried one more
    than that.
    """
    if index < folded or folded < 1 or index < 1:
        return None
    place = index - folded
    shortest, longest = windows[index]
    # A PARENT THAT CAN BE CASE-FLIPPED IS TAKEN FIRST (review item
    # P3-C6-F1). The partner that keeps the length exactly where it was
    # is a case flip, and it needs a letter; a parent holding none can
    # only be answered by an edge-spaced copy. That costs nothing on
    # most columns and costs a SECOND spreadsheet hazard on one: where
    # the parent is the two-character signed family owner decision 9
    # permits, `-0` has no letter, so the partner came out `-0 ` and a
    # column of `-3`, `-3 ` and `1e0` wrote twenty-two hazardous cells
    # where eleven would do. Both passes keep the cyclic order the
    # method fixes, so a column whose parents all hold letters, or none
    # of which do, is laid out exactly as it was.
    # AND A PARENT THAT KEEPS THE FOLDED LEVEL UNDER THE LONG-TAIL LINE
    # IS TAKEN FIRST (residual R-P4-36). A partner folds onto its
    # parent, so the level the pair makes covers BOTH their rows, and a
    # level at the detection line is what makes a reader call a column
    # a long tail of LABELS rather than free text.
    #
    # THE LEVEL, NOT THE PAIR. A parent may already carry partners from
    # earlier in this walk. Sizes 1, 2 and 9 give pairwise sums of 3
    # and 10, both under a line of eleven, and a level of twelve.
    #
    # THIS PASS WAS WITHDRAWN ONCE AND RESTORED, and the reason is
    # worth keeping. It was measured across 190 randomly built
    # free-text columns and changed no outcome, so it was removed as
    # inert -- and the sample was HOMOGENEOUS. Within one family the
    # sorted group order usually makes the choice for it. ACROSS
    # families the cyclic walk can meet an unsafe same-family parent
    # before a safe one, and then this pass decides: on twenty-four
    # rows of `alpha phrase`/`codeaa` shapes, sizes 1, 2, 2, 2, 8 and
    # 9 split between an ordinary-text family and a code-alphabet one,
    # the walk without it reaches eleven and the twin reads back as
    # `long_tail_labels`; with it the largest level is ten and the twin
    # reads back as free text. A measurement over one family is a
    # measurement of one family.
    under_first: "tuple[bool, ...]" = (True, False)
    if sizes is None or long_tail_line < 1:
        under_first = (False,)
    for under in under_first:
        for lettered in (True, False):
            for step in range(folded):
                parent_place = (place + step) % folded
                if families[parent_place] != families[index]:
                    continue
                if under and sizes is not None:
                    already = sizes[parent_place]
                    if carried is not None and parent_place in carried:
                        already = carried[parent_place]
                    if already + sizes[index] >= long_tail_line:
                        continue
                has_letter = False
                for character in spellings[parent_place]:
                    if character in _LETTERS:
                        has_letter = True
                        break
                if has_letter != lettered:
                    continue
                found = _partner_from(
                    parent_place, index, spellings, used, shortest, longest
                )
                if found is None:
                    continue
                if carried is not None and sizes is not None:
                    already = sizes[parent_place]
                    if parent_place in carried:
                        already = carried[parent_place]
                    carried[parent_place] = already + sizes[index]
                return found
    return None


def _partner_from(
    parent_place: int,
    index: int,
    spellings: "list[str]",
    used: "dict[str, int]",
    shortest: int,
    longest: "int | None",
) -> "str | None":
    """One parent's family, walked from its own start (G9.3 step 2)."""
    if True:
        parent = spellings[parent_place]
        order = 1
        steps = len(used) + 1
        while steps > 0:
            candidate = _partner_at(parent, order, shortest, longest)
            if candidate is None:
                break
            if _unused(candidate, used):
                return candidate
            order = order + 1
            steps = steps - 1
    return None


def _length_windows(
    total: int,
    shortest: int,
    longest: "int | None",
    pinned: bool,
    carriers: "tuple[int, int]",
) -> "list[tuple[int, int | None]]":
    """The lengths every value of an invented column may take (G9.3).

    One value carries the shortest published length and one the longest,
    which is what makes both ends facts a recount confirms (method
    G9.2), and ``carriers`` says which two -- the first two values on a
    column of record numbers, and on a column of free text whichever two
    the allocation of G9.5 settled on. A value carrying an end is held
    to that one length even when a fold-collision partner answers for
    it; every other value may take any length in the published range.
    ``pinned`` is False where the two ends are the same length, or where
    the column has no second value to pin.
    """
    windows: list[tuple[int, int | None]] = [
        (shortest, longest) for _each in range(total)
    ]
    if total >= 1:
        windows[carriers[0]] = (shortest, shortest)
    if total >= 2 and pinned and longest is not None:
        windows[carriers[1]] = (longest, longest)
    return windows


def _letter_asks(families: "list[str]", folded: int) -> "list[bool]":
    """Which identities are asked to hold a letter (method G9.3 step 1).

    A case flip is the FIRST partner method G9.3 reaches for, because it
    is the one construction that leaves the length exactly where it was,
    and it needs a value with a case to flip. Edge spacing carries the
    collisions this ask cannot reach, so the ask is a preference and
    never a condition. Either partner carries its parent's FAMILY with
    it -- the alphabet the value is written from, and on a column of free
    text the numeric class it has to read back as -- so the ask cannot
    simply go to the first few identities: it goes to the identities the
    collisions will actually be taken from, which is, for each family,
    as many of that family's earliest identities as that family has
    collisions to place.
    """
    total = len(families)
    wanted: dict[str, int] = {}
    for index in range(folded, total):
        family = families[index]
        if family not in wanted:
            wanted[family] = 0
        wanted[family] = wanted[family] + 1
    asks = [False for _each in families]
    for index in range(min(folded, total)):
        family = families[index]
        if family in wanted and wanted[family] > 0:
            asks[index] = True
            wanted[family] = wanted[family] - 1
    return asks


def _caseless_slots(
    cells: "list[int]",
    facts: contract.IdentifierFacts,
    carriers: "tuple[int, int]",
    total: int,
) -> "frozenset[int]":
    """The groups whose spelling holds no letter to flip (review P3-C6-F1).

    A fold-collision partner is built from its parent's spelling, and
    the partner that keeps the length exactly where it was is a CASE
    FLIP -- which needs a letter. Where the parent holds none, the
    partner has to be an edge-spaced copy instead, and an edge-spaced
    copy of a value opening with a sign is a SECOND cell a spreadsheet
    reads as a formula.

    `_collision_slots` already trades the collision slots away from the
    band written in figures alone, for exactly this reason. The
    two-character code family owner decision 9 permits is caseless in
    the same way and was not named: `-0` through `-9` hold no letter
    either, so a column of `-3`, `-3 ` and `1e0` wrote twenty-two
    hazardous cells where eleven would do. This names those slots so the
    same trade reaches them, and the collision lands on `0e0`/`0E0`
    instead -- one flip, no second hazard, every published count where
    the packing put it.
    """
    width = len(_BANDS)
    number = 0
    for place in range(len(_CLASSES)):
        if _CLASSES[place] == _CLASS_NUMBER:
            number = place
    code = 0
    for place in range(width):
        if _BANDS[place] == _BAND_CODE:
            code = place
    caught: list[int] = []
    for place in range(total):
        low = facts.min_length
        high = facts.max_length
        if place == carriers[0]:
            high = facts.min_length
        elif place == carriers[1] and facts.max_length > facts.min_length:
            low = facts.max_length
        if low != high or low != 2:
            continue
        if cells[place] // width == number and (
            cells[place] - (cells[place] // width) * width
        ) == code:
            caught = caught + [place]
    return frozenset(caught)


def _collision_slots(
    cells: "list[int]",
    groups: "tuple[int, ...]",
    folded: int,
    partners: int,
    permits: "list[int]",
    caseless: "frozenset[int] | None" = None,
) -> "list[int]":
    """Prefer a band with a case for the fold-collision slots (G9.3).

    A value written in figures alone has no case at all, so a case flip
    -- the partner that keeps the length exactly where it was -- cannot
    be built from it. The slots that have to carry a collision -- the
    first few identities, and the partners that follow them -- are
    therefore given a band that can, by trading bands with a group of
    EXACTLY the same size. Trading between equal sizes is what leaves
    both published alphabet counts where they were, since each is a
    count of cells and the two groups cover the same number of them.

    Where too few groups can carry a letter, some collision slot keeps
    the all-figures band. That is no longer a lost count on its own:
    edge spacing folds a figures-only value onto another one, and the
    trimmed characters -- which is what both alphabet counts are read
    from -- do not move (review item P2-C2-F6). This trade stays because
    a case flip needs no room in the length range and edge spacing does.

    THE WHOLE PAIR TRADES, not the band alone (review item P2-C5-F2).
    A group answers for one of the four class counts and one of the two
    alphabet counts at the same time, so moving a band between two
    groups without its class would leave the class counts short by
    exactly what it moved. Trading the pair between groups of equal size
    leaves both margins exactly where the packing put them.
    """
    total = len(groups)
    if partners < 1 or total < 1:
        return cells
    width = len(_BANDS)
    needed = [place for place in range(min(partners, folded))]
    needed = needed + [place for place in range(folded, total)]
    barren = caseless if caseless is not None else frozenset()
    moved = [cell for cell in cells]
    for place in needed:
        # A SLOT NEEDS TRADING WHERE ITS SPELLING HOLDS NO LETTER: the
        # band written in figures alone, and the two-character signed
        # code family beside it (review item P3-C6-F1).
        if (
            moved[place] - (moved[place] // width) * width != 0
            and place not in barren
        ):
            continue
        for other in range(total):
            if other in needed or groups[other] != groups[place]:
                continue
            if (
                moved[other] - (moved[other] // width) * width == 0
                or other in barren
            ):
                continue
            # A TRADE IS ONLY A TRADE WHERE BOTH SLOTS CAN WRITE WHAT
            # THEY ARE HANDED (review item P2-C5-F2). A slot carrying a
            # published length end is held to that one length, and a
            # class-and-alphabet pair the packing gave to a slot with
            # the whole range open to it may have no spelling there at
            # all: swapping without asking put a value that must read
            # as a number too large to hold onto a three-character pin,
            # where its family is empty, and the walk fell back to the
            # band alphabet and lost the class count the packing had
            # just met.
            if (permits[place] >> moved[other]) & 1 == 0:
                continue
            if (permits[other] >> moved[place]) & 1 == 0:
                continue
            moved[place], moved[other] = moved[other], moved[place]
            break
    return moved


def _repeat_notes(column: contract.ColumnBlock) -> "list[Deviation]":
    """The repetition fact a repeating column of record numbers gives up.

    Owner decision 6: where a declared column's published width and its
    all-different fact cannot both hold, the WIDTH is kept and values
    repeat. THREE facts stop being reproduced then, not one -- the count
    of different spellings, the count of different folded identities,
    and the pattern of repeats itself. The first two are named by the
    recount, which measures them from the written twin; this is the
    third, and it carries the consequence for a join in the person's own
    words, because a made-up pattern of repeats is exactly what
    publishing that pattern was meant to prevent.
    """
    return [
        _deviation(
            column.name,
            "n_distinct_by_occurrences",
            "one group of rows for every different value",
            "some values repeat, so the groups are not the published ones",
            "The twin's record numbers keep the width the real ones had, "
            "so code that checks or cuts them by width still works; but "
            "some values repeat where the real column's were all "
            "different, so a join or a de-duplication developed against "
            "the twin can match more rows, or fewer, than it will on the "
            "real table.",
        ),
    ]


def _grouped(
    groups: "tuple[int, ...]", spellings: "list[str]"
) -> "list[str]":
    """Every group's own spelling, repeated its own number of times."""
    return [
        spellings[index]
        for index in range(len(groups))
        for _row in range(groups[index])
    ]


# -- columns of free text (method G9.5) -------------------------------


def _text_cells(
    column: contract.ColumnBlock,
    groups: "tuple[int, ...]",
    long_tail_line: int = 0,
) -> "tuple[list[str], list[Deviation], tuple[int, int]]":
    """Every present cell of a column of free text (method G9.5).

    The text is MADE UP. This module never samples, quotes, templates
    from, or paraphrases source text, and no source text is available to
    it in any case: the description carries none.

    THE SHAPE AND THE COUNTS ARE ONE QUESTION (review item P2-C4-F2).
    Which group carries each published end, what length every other
    group takes, which of the four numeric classes each group answers
    for and which of the three alphabets it is written from are settled
    TOGETHER by `_text_plan`, because a shape chosen before the packing
    can make a count impossible that another shape meets -- and a count
    the description publishes is exact while the average length it was
    traded for is approximated. Each packing is EXACT wherever any
    packing is (review items P2-C1-F1, P2-C4-F2), and every count that
    is missed anyway is measured from the finished cells and named
    there.

    Returns the cells, the deviations the shape itself forced, and the
    two groups that ended up carrying the published ends, which the
    approximation bounds of G12.6 are measured against.

    Raises `errors.ProfileError` where a family of spellings cannot
    supply the different values the repetition pattern requires. That is
    the `generation-domain-too-small` refusal of method G9.4, it says
    the description is VALID, and it is raised while the plan is being
    settled -- before any output file exists.
    """
    facts = column.facts
    if not isinstance(facts, contract.TextFacts):
        raise _wrong_facts(column.name)
    total = len(groups)
    lengths, counts, kinds, bands, carriers, notes = _text_plan(
        column, facts, groups
    )
    shortened = 0
    for index in range(total):
        if index in carriers or counts[index] == 1:
            continue
        if _family_room(
            _CLASSES[kinds[index]],
            _BANDS[bands[index]],
            lengths[index],
            counts[index],
        ) > 0:
            continue
        counts[index] = 1
        shortened = shortened + 1
    if shortened:
        notes = notes + [
            _deviation(
                column.name,
                "words",
                "the published word counts",
                f"{shortened} of the twin's values hold one word",
                "A value counted in the code alphabet cannot hold a "
                "space, and a value that has to read back as a number "
                "holds no space either, so a value the description gives "
                "one of those shapes to is written as one word however "
                "many the description records.",
            )
        ]
    used: dict[str, int] = {}
    states: dict[str, list[int]] = {}
    spellings: list[str] = []
    folded = min(column.n_distinct_folded, total)
    families = [
        f"{_CLASSES[kinds[index]]}/{_BANDS[bands[index]]}"
        for index in range(total)
    ]
    asks = _letter_asks(families, folded)
    windows = _length_windows(
        total,
        facts.length.minimum,
        facts.length.maximum,
        facts.length.maximum > facts.length.minimum,
        carriers,
    )
    wanted = _demand(kinds, bands, lengths, counts)
    # THE FORMS THIS COLUMN WAS WRITTEN IN, IF IT PUBLISHED ANY (plan
    # P4-D18). A free-text column of prose publishes none, so the debt
    # is empty, every group is offered nothing and the walk is what it
    # was. The debt is settled by the spelling ACTUALLY WRITTEN, read
    # back off it, because a form is an ask: a group offered one may be
    # written without it, and a partner spelling wears whatever a case
    # flip or an edge space left it wearing.
    owing = _text_debt(facts)
    # HOW FAR THE TWIN'S TOTAL LENGTH MAY STILL MOVE, in each direction
    # (review round 2 finding 9). `length.mean` is approximated, so it
    # has a window rather than a value -- and a window is a budget, not
    # a licence. A form of another length is offered only while the
    # projected total stays inside it.
    budget = _length_budget(facts, groups, lengths)
    # WHICH FORM EACH GROUP IS ASKED FOR, decided before the walk and in
    # order of how many cells a group covers (residual R-P4-38).
    form_asks = _form_asks(
        owing,
        groups,
        lengths,
        counts,
        carriers,
        facts.length.minimum,
        facts.length.maximum,
        budget,
    )
    made: dict[str, int] = {}
    # How many rows each parent's folded level covers so far, so the
    # preference reads the level rather than the pair.
    carried: "dict[int, int]" = {}
    for index in range(total):
        partner = _partner_of(
            index, folded, spellings, families, used, windows,
            list(groups), long_tail_line, carried,
        )
        if partner is not None:
            taken = _take(partner, used)
            _settle(owing, taken, groups[index])
            _spend_length(budget, len(taken) - lengths[index], groups[index])
            spellings = spellings + [taken]
            continue
        kind = _CLASSES[kinds[index]]
        band = _BANDS[bands[index]]
        # THE PRE-DECIDED ASK, RE-ASKED WHERE IT HAS GONE STALE. The
        # order-aware pass above cannot know which groups will take a
        # fold-collision partner instead of a made-up spelling, because
        # that depends on `used`, which this walk is what fills. Where a
        # partner has already settled the debt this group was going to
        # settle, the pre-decided form is no longer owed anything and
        # asking for it would write a form the column does not owe. The
        # live rules answer instead, exactly as they did before the
        # order-aware pass existed.
        asked_form = form_asks[index]
        stale = asked_form not in owing or owing[asked_form] < 1
        if asked_form and stale:
            asked_form = _wanted_form(
                owing,
                lengths[index],
                counts[index],
                index in carriers,
                facts.length.minimum,
                facts.length.maximum,
                budget,
                groups[index],
            )
        key = f"{kind}/{band}/{lengths[index]}/{counts[index]}"
        spelling = _made_up_cell(
            kind, band, lengths[index], counts[index],
            asks[index], states, used,
            asked_form,
            _hole_spellings(column),
        )
        if spelling is None:
            held = 0
            if key in made:
                held = made[key]
            raise errors.ProfileError(
                _domain_too_small(
                    column.name,
                    _shape_words(kind, band, lengths[index]),
                    wanted[key],
                    held,
                )
            )
        if key not in made:
            made[key] = 0
        made[key] = made[key] + 1
        _settle(owing, spelling, groups[index])
        _spend_length(budget, len(spelling) - lengths[index], groups[index])
        spellings = spellings + [spelling]
    # THE TWIN CAN REPROFILE INTO A DIFFERENT ROLE, AND NOW IT SAYS SO
    # (residual R-P4-36). A fold-collision partner folds onto its
    # parent, so the pair makes a level covering BOTH their rows -- and
    # a level at the long-tail detection line is what makes a reader
    # call a column a long tail of LABELS rather than free text.
    #
    # TWO THINGS ANSWER IT, and only the second is a guarantee. The
    # walk above PREFERS a parent that keeps the LEVEL under the line,
    # which avoids the change wherever a safe parent exists -- and
    # across families, which is where it decides, it does. Where no
    # safe parent exists at all, as on the column this residual was
    # opened for, the change happens and is NAMED here. That was the
    # residual's complaint: the column changed kind "and says nothing".
    #
    # MEASURED ON THE FINISHED SPELLINGS rather than counted inside the
    # walk, so a crossing is seen however it arose -- including one no
    # walk-side rule could have anticipated. It also keeps
    # `_partner_of` returning one value, which a test pins.
    #
    # THE SENTENCE HEDGES ON PURPOSE. Whether a later reading really
    # calls this a long tail depends on how the twin is read: declared
    # missing words and the categorical share both move it, and under
    # some declarations the twin reads back as free text after all. So
    # the sentence names what the twin HOLDS.
    crossed = _levels_past_the_line(spellings, groups, long_tail_line)
    if crossed:
        notes = notes + [
            _deviation(
                column.name,
                "n_distinct_folded",
                f"{folded} folded value(s), none of them a published level",
                f"{crossed} of them cover(s) at least {long_tail_line} rows",
                "folding this twin's spellings made a group of cells "
                "large enough that describing the twin again may call "
                "this column a long tail of labels rather than free "
                "text. Whether it does depends on how the twin is read "
                "-- which words are called missing, and what share of "
                "the rows a set of categories may cover -- so this "
                "names what the twin HOLDS rather than predicting what "
                "a later reading will say about it. Code that "
                "dispatches on a column's type is what this reaches.",
            )
        ]
    return _grouped(groups, spellings), notes, carriers


def _shape_choices(total: int) -> "list[tuple[int, int]]":
    """Every pair of groups that could carry the two published ends.

    THE ORDER IS PART OF THE RULE, so two implementations settle on the
    same shape. The pairs are offered in ascending order of the pair
    itself -- the group taking the shortest length first, then the group
    taking the longest -- so the first pair offered is the description's
    own first two groups, which is the shape every earlier revision took
    without asking. A column with one group has nothing to pair and its
    one group carries the shortest length.
    """
    if total < 2:
        return [(0, 0)]
    return [
        (low, high)
        for low in range(total)
        for high in range(total)
        if high != low
    ]


def _pair_reach(
    shortest: int, longest: int, words: int, room: "dict[tuple[int, int], int]"
) -> int:
    """Which pairs a group may stand in at ANY length it is allowed.

    A group carrying neither published end is held to no length at all
    by the description: every length in the published range is open to
    it, and only the approximated average prefers one. So the pairs it
    can stand in are the pairs SOME permitted length allows, which is
    what this unions up (review item P2-C4-F2). The union is taken
    rather than reasoned about, so a change to what a family can write
    cannot quietly narrow it.

    ``room`` is this column's own memory of the answer, because the same
    span is asked about once per candidate shape and the answer depends
    on nothing else.
    """
    key = (max(shortest, 1), words)
    if key in room:
        return room[key]
    mask = 0
    for length in range(key[0], max(longest, key[0]) + 1):
        mask = mask | _pair_permits(length, words, False)
    room[key] = mask
    return mask


def _text_permits(
    facts: contract.TextFacts,
    lengths: "list[int]",
    counts: "list[int]",
    carriers: "tuple[int, int]",
    reach: bool,
    room: "dict[tuple[int, int], int]",
) -> "list[int]":
    """The cells of the grid every group may take, under one shape.

    ``reach`` is False for the reading that holds every group to the
    length the approximated walk gave it, and True for the reading that
    holds only the two end-carrying groups to their lengths and lets
    every other group be written at any length the description allows.
    The first is preferred because it keeps the approximated average
    where the walk put it; the second is tried where the first meets no
    published count, because an exact count outranks an approximated
    average (method G9.5).
    """
    permits: list[int] = []
    for place in range(len(lengths)):
        if reach and place not in carriers:
            permits = permits + [
                _pair_reach(
                    lengths[place], facts.length.maximum, counts[place], room
                )
            ]
            continue
        permits = permits + [
            _pair_permits(lengths[place], counts[place], place in carriers)
        ]
    return permits


def _lengthened(
    facts: contract.TextFacts,
    lengths: "list[int]",
    counts: "list[int]",
    cells: "list[int]",
    carriers: "tuple[int, int]",
) -> "list[int]":
    """Give every group a length its own cell of the grid can be written at.

    The companion of the wider reading of `_text_permits`: a group that
    was allowed into a cell because SOME permitted length can write it
    is now given the shortest such length at or above the one the walk
    preferred, so the approximated average moves as little as the exact
    counts require. A group carrying a published end never moves.
    """
    moved = [length for length in lengths]
    for place in range(len(lengths)):
        if place in carriers:
            continue
        length = moved[place]
        while length < facts.length.maximum and (
            _pair_permits(length, counts[place], False) >> cells[place]
        ) & 1 == 0:
            length = length + 1
        moved[place] = length
    return moved


def _text_plan(
    column: contract.ColumnBlock,
    facts: contract.TextFacts,
    groups: "tuple[int, ...]",
) -> "tuple[list[int], list[int], list[int], list[int], tuple[int, int], list[Deviation]]":
    """The whole shape of a column of free text, settled in ONE allocation.

    WHY THIS IS ONE QUESTION AND NOT THREE (review item P2-C4-F2).
    Revision 5 gave the two published length ends to the description's
    first two groups, walked every other length toward the published
    average, and only then asked the grid of classes and alphabets to
    find a packing inside that shape. The shape it chose can make a
    published count unreachable that another shape reaches: a source of
    one three-character two-word value, five copies of a one-character
    value inside the code alphabet and six copies of a two-character
    value outside it publishes `n_code_alphabet = 5`, and its own values
    are an assignment meeting every count -- but pinning the longest
    length and the largest word count onto the five-row group bars that
    group from the code alphabet, and no other group has five rows. The
    count was then reported as missed although the description was
    satisfiable, which is a published fact lost to a shape the profile
    never published.

    So the ends, the lengths, the classes and the alphabets are settled
    together here. The candidate shapes are offered in the fixed order
    of `_shape_choices`, and under each of two readings of what a group
    that carries no end may be written at: first the length the
    approximated walk gave it, then any length the description allows.
    The FIRST candidate whose grid packs every published count exactly
    is taken, so a description the earlier rule already answered is
    answered the same way, byte for byte, and the search costs nothing
    on it. A shape whose grid has no exact packing is never chosen while
    one that does exists.

    Where NO shape and no reading packs every count -- which a
    description a real table produced does not reach, because that
    table's own values are one such shape -- the description's own first
    two groups carry the ends and the two families are decided one after
    the other, exactly as they were. Every count missed either way is
    recounted from the finished cells and named in the report.

    A shape is skipped without walking its grid where an earlier
    candidate already offered the same group sizes with the same
    permitted cells, since the answer to "does this pack" depends on
    nothing else.
    """
    total = len(groups)
    classes = [
        column.n_numeric,
        column.n_out_of_range,
        column.n_contradictory,
        column.n_not_numeric,
    ]
    alphabets = [
        facts.n_all_digits,
        facts.n_code_alphabet - facts.n_all_digits,
        column.n_present - facts.n_code_alphabet,
    ]
    width = len(_BANDS)
    room: dict[tuple[int, int], int] = {}
    spent: dict[tuple[tuple[int, int], ...], int] = {}
    for reach in (False, True):
        sized: dict[tuple[int, int], int] = {}
        for carriers in _shape_choices(total):
            # TWO GROUPS OF THE SAME SIZE ARE THE SAME QUESTION. No
            # published count tells two groups covering the same number
            # of cells apart: the grid collapses them, and the walk of
            # step 5 gives the groups carrying no end the same lengths
            # in the same amounts whichever of two equal-sized groups
            # took the end. So a pair whose two sizes have already been
            # offered can only fail the same way, and skipping it costs
            # no assignment at all -- which is what keeps this bounded
            # by the number of different group SIZES rather than by the
            # number of groups.
            shape = (groups[carriers[0]], groups[carriers[1]])
            if shape in sized:
                continue
            sized[shape] = 1
            lengths, counts, notes = _text_shape(
                column, facts, groups, carriers
            )
            permits = _text_permits(
                facts, lengths, counts, carriers, reach, room
            )
            seen = tuple(sorted(
                [(groups[place], permits[place]) for place in range(total)]
            ))
            if seen in spent:
                continue
            spent[seen] = 1
            together = _joint_allocation(
                groups, classes, alphabets, permits
            )
            if together is None:
                continue
            if reach:
                lengths = _lengthened(
                    facts, lengths, counts, together, carriers
                )
            return (
                lengths,
                counts,
                [cell // width for cell in together],
                [cell - (cell // width) * width for cell in together],
                carriers,
                notes,
            )
    carriers = _shape_choices(total)[0]
    lengths, counts, notes = _text_shape(column, facts, groups, carriers)
    kinds, bands = _text_families(
        column, facts, groups, lengths, counts, carriers
    )
    return lengths, counts, kinds, bands, carriers, notes


def _text_families(
    column: contract.ColumnBlock,
    facts: contract.TextFacts,
    groups: "tuple[int, ...]",
    lengths: "list[int]",
    counts: "list[int]",
    carriers: "tuple[int, int]",
) -> "tuple[list[int], list[int]]":
    """The classes and the alphabets where NO shape packs them together.

    THE TWO ARE ONE QUESTION and this is not the answer to it: every
    group answers for one of the four class counts and one of the three
    alphabet counts at the same time, and a group's length settles which
    PAIRS it can stand in, so deciding the classes in one walk and the
    alphabets in a second throws away joint answers that exist (review
    item P2-C2-F1). `_text_plan` asks the grid of pairs first, under
    every shape the description leaves open, and only where not one of
    them packs every count -- which a description a real table produced
    does not reach, because that table's own values are such a shape --
    does it come here.

    Every count missed this way is measured from the finished cells and
    named there.
    """
    total = len(groups)
    classes = [
        column.n_numeric,
        column.n_out_of_range,
        column.n_contradictory,
        column.n_not_numeric,
    ]
    alphabets = [
        facts.n_all_digits,
        facts.n_code_alphabet - facts.n_all_digits,
        column.n_present - facts.n_code_alphabet,
    ]
    kinds = _allocation(
        groups,
        classes,
        [
            _class_permits(lengths[index], counts[index])
            for index in range(total)
        ],
    )
    bands = _allocation(
        groups,
        alphabets,
        [
            _band_permits(
                _CLASSES[kinds[index]], lengths[index], counts[index],
                index in carriers,
            )
            for index in range(total)
        ],
    )
    return kinds, bands


def _pair_permits(length: int, words: int, pinned: bool) -> int:
    """Which class-and-alphabet PAIRS one group can stand in (G9.5 step 3).

    The single answer to the question `_class_permits` and
    `_band_permits` each answered half of. ``pinned`` says this group
    carries one of the two published word counts, which are
    EXACT-OBSERVABLE and may not be brought down for it.

    A FAMILY THAT CANNOT HOLD THAT MANY WORDS IS NOT PERMITTED TO A
    PINNED GROUP, and reading the rule as being only about the code
    alphabet lost `words.max` in silence (review item P2-C4-F2). A cell
    counted in that alphabet holds one word because a space is not one
    of its characters -- but a cell that reads as a number holds one
    word for a plainer reason: every construction of a number in G9.5
    step 3 writes a single run of characters with no space anywhere in
    it. So a group pinned to two words and given a numeric class wrote
    one word, the published word extreme was not reached, and nothing
    said so. `_family_room` answers that question for every family, and
    this asks it rather than naming one band.

    Every group that carries NEITHER end may still have its word count
    brought down to one wherever the family it is given needs that,
    because those counts are EXACT-OBSERVABLE while `words.mean` is
    APPROXIMATED and an exact fact outranks an approximated one.
    """
    width = len(_BANDS)
    mask = 0
    for place in range(len(_CLASSES)):
        for band in range(width):
            asked = words
            if not pinned and _family_room(
                _CLASSES[place], _BANDS[band], length, asked
            ) < 1:
                asked = 1
            if _family_room(_CLASSES[place], _BANDS[band], length, asked) > 0:
                mask = mask | (1 << (place * width + band))
    if mask == 0:
        return _every_bucket(len(_CLASSES) * width)
    return mask


def _demand(
    kinds: "list[int]",
    bands: "list[int]",
    lengths: "list[int]",
    counts: "list[int]",
) -> "dict[str, int]":
    """How many different values each family of spellings is asked for."""
    wanted: dict[str, int] = {}
    for index in range(len(kinds)):
        key = (
            f"{_CLASSES[kinds[index]]}/{_BANDS[bands[index]]}/"
            f"{lengths[index]}/{counts[index]}"
        )
        if key not in wanted:
            wanted[key] = 0
        wanted[key] = wanted[key] + 1
    return wanted


def _class_permits(length: int, words: int) -> int:
    """Which numeric classes can be written at one length at all."""
    mask = 0
    for place in range(len(_CLASSES)):
        for band in range(len(_BANDS)):
            if _family_room(_CLASSES[place], _BANDS[band], length, words) > 0:
                mask = mask | (1 << place)
                break
    if mask == 0:
        return _every_bucket(len(_CLASSES))
    return mask


def _band_permits(kind: str, length: int, words: int, pinned: bool) -> int:
    """Which alphabet bands one class can be written in at one length.

    This is what carries the rules one published fact places on another
    into the packing itself (review item P2-C1-F1). A cell whose
    notation contradicts itself is written inside accounting
    parentheses, which the code alphabet does not hold, so such a group
    can never be counted among the cells written in figures alone or
    among those written in the code alphabet. Packing the two alphabet
    counts without that rule is what let a count the description
    publishes be missed while a construction that could have met it went
    unused.

    ``pinned`` says this group carries one of the two published word
    counts, which are EXACT-OBSERVABLE and may not be changed for it.
    Every OTHER group's word count may be brought down to one so that it
    can stand in the code alphabet -- a cell of several words holds a
    space, and a space is not a character that alphabet has -- because
    the count of cells in the code alphabet is exact while the average
    word count is approximated, and an exact fact outranks an
    approximated one.
    """
    mask = 0
    for band in range(len(_BANDS)):
        asked = words
        if not pinned and _family_room(kind, _BANDS[band], length, asked) < 1:
            asked = 1
        if _family_room(kind, _BANDS[band], length, asked) > 0:
            mask = mask | (1 << band)
    if mask == 0:
        return _every_bucket(len(_BANDS))
    return mask


def _shape_words(kind: str, band: str, length: int) -> str:
    """What a family of spellings is, in the words a person reads."""
    wide = f"{length} characters long"
    if length == 1:
        wide = "one character long"
    written = "written with any character a keyboard writes"
    if band == _BAND_DIGITS:
        written = "written in figures alone"
    elif band == _BAND_CODE:
        written = (
            "written with letters, figures, hyphens and underscores only"
        )
    else:
        written = (
            "written with at least one character that is not a letter, a "
            "figure, a hyphen or an underscore"
        )
    reads = "read as ordinary text"
    if kind == _CLASS_NUMBER:
        reads = "read as a number"
    elif kind == _CLASS_OUT_OF_RANGE:
        reads = "read as a number too large or too small to hold"
    elif kind == _CLASS_CONTRADICTORY:
        reads = "read as numeric notation that conflicts with itself"
    return f"{wide}, {written}, and {reads}"


def _text_shape(
    column: contract.ColumnBlock,
    facts: contract.TextFacts,
    groups: "tuple[int, ...]",
    carriers: "tuple[int, int]",
) -> "tuple[list[int], list[int], list[Deviation]]":
    """The length and the word count of every group (G9.5 steps 4 and 5).

    ``carriers`` names the two groups that carry the published ends --
    the first takes the shortest length and the smallest word count, the
    second takes the longest and the largest -- which is what makes all
    four of them facts a recount can confirm. WHICH two groups those are
    is not settled here and is not settled before the packing: it is one
    of the things the packing of `_text_plan` decides, because pinning
    an end onto a group chosen in advance can make a published count
    that some other pinning meets impossible (review item P2-C4-F2).

    The rest start at the middle length and are walked toward the
    published average one character at a time, largest group first,
    which is the fixed rule the average is measured against. Lengths and
    word counts are paired by ascending order -- the longest cells take
    the most words -- so a clamp bites as rarely as the published facts
    allow.
    """
    total = len(groups)
    notes: list[Deviation] = []
    lengths = _walked(
        groups,
        facts.length.minimum,
        facts.length.maximum,
        facts.length.p50,
        facts.length.mean,
        column.n_present,
        carriers,
    )
    counts = _walked(
        groups,
        max(facts.words.minimum, 1),
        max(facts.words.maximum, 1),
        facts.words.mean,
        facts.words.mean,
        column.n_present,
        carriers,
    )
    free = [place for place in range(total) if place not in carriers]
    ranked = sorted([(lengths[place], place) for place in free])
    ordered = sorted([counts[place] for place in free])
    for step in range(len(ranked)):
        counts[ranked[step][1]] = ordered[step]
    clamped = 0
    for place in range(total):
        ceiling = max((lengths[place] + 1) // 2, 1)
        if counts[place] > ceiling:
            counts[place] = ceiling
            clamped = clamped + 1
        if counts[place] < 1:
            counts[place] = 1
            clamped = clamped + 1
    if clamped:
        notes = notes + [
            _deviation(
                column.name,
                "words",
                "the published word counts",
                f"{clamped} of the twin's values hold fewer words",
                "A value can hold only so many words in the number of "
                "characters the description gives it, so the twin writes "
                "as many as fit.",
            )
        ]
    return lengths, counts, notes


def _walked(
    groups: "tuple[int, ...]",
    smallest: int,
    largest: int,
    middle: "float | None",
    average: "float | None",
    rows: int,
    carriers: "tuple[int, int]",
) -> "list[int]":
    """One whole number per group, pinned at the ends and walked to a mean.

    The residual walk of method G9.5 step 4: the two groups ``carriers``
    names take the two ends, every other group starts at the middle, and
    the difference between the published total and the built one is
    spent one character at a time on the group with the most rows that
    can still move. The published average is turned into a whole total
    by exact arithmetic on the rational the binary64 stands for, never
    in floating point.
    """
    total = len(groups)
    start = smallest
    if middle is not None:
        start = max(smallest, min(largest, int(_whole_valued(middle))))
    values = [start for _each in groups]
    if total >= 1:
        values[carriers[0]] = smallest
    if total >= 2:
        values[carriers[1]] = largest
    if average is None:
        return values
    wanted = _exact_product(average, rows)
    built = 0
    for place in range(total):
        built = built + groups[place] * values[place]
    residual = wanted - built
    if residual == 0 or total < 3:
        return values
    upward = residual > 0
    ranked = sorted([(-groups[place], place) for place in range(total)
                     if place not in carriers])
    steps = 0
    ceiling = total * (largest - smallest + 1) + 1
    while residual != 0 and steps < ceiling:
        moved = False
        for pair in ranked:
            place = pair[1]
            if upward and values[place] < largest:
                values[place] = values[place] + 1
                residual = residual - groups[place]
                moved = True
            elif not upward and values[place] > smallest:
                values[place] = values[place] - 1
                residual = residual + groups[place]
                moved = True
            if moved:
                break
        steps = steps + 1
        if not moved:
            break
        if upward and residual < 0:
            break
        if not upward and residual > 0:
            break
    return values


def _reads_as(kind: str) -> str:
    """What the shipped classifier must say about a cell of one class."""
    if kind == _CLASS_NUMBER:
        return parsing.NUMBER
    if kind == _CLASS_OUT_OF_RANGE:
        return parsing.NUMBER_OUT_OF_RANGE
    if kind == _CLASS_CONTRADICTORY:
        return parsing.NUMBER_CONTRADICTORY
    return parsing.NOT_A_NUMBER


def _text_alphabet(band: str) -> "tuple[str, ...]":
    """The characters a made-up cell of ordinary text is written from."""
    if band == _BAND_WIDE:
        return _WIDE_WORD
    return _CODE


def _text_head(band: str) -> "tuple[str, ...]":
    """What a made-up cell of ordinary text may begin with.

    A letter in the code band, so the cell can never read as a number,
    and a character outside the code alphabet in the wide band, so it
    can never be counted as one written in the code alphabet.
    """
    if band == _BAND_WIDE:
        return tuple([figure for figure in _WIDE_WORD
                      if not parsing.is_code_text(figure)
                      and figure not in _FORMULA_LEADERS])
    return _letters_of(_CODE)


def _family_at(
    kind: str, band: str, length: int, words: int, index: int
) -> "str | None":
    """The ``index``-th spelling of one class, band, length and word count.

    A DIRECT MAPPING FROM A NUMBER TO A SPELLING, with no search of any
    kind (method G9.2, review item P2-C1-F2): the index is taken apart
    into the positions of the spelling by plain mixed-radix arithmetic,
    so the family's size is a number this module can state in advance
    and a walk over it always ends. None says this class cannot be
    written at this length in this band at all -- one character cannot
    be a number and stand outside the figures at the same time -- and
    the packing rule keeps such a pairing from being chosen.
    """
    if kind == _CLASS_NUMBER:
        return _number_at(band, length, index)
    if kind == _CLASS_OUT_OF_RANGE:
        return _out_of_range_at(band, length, index)
    if kind == _CLASS_CONTRADICTORY:
        return _contradictory_at(length, index)
    return _worded(
        _text_head(band),
        _text_alphabet(band),
        max(length, 1),
        max(words, 1),
        index,
    )


def _family_room(kind: str, band: str, length: int, words: int) -> int:
    """How many spellings one family holds, saturated (method G9.4).

    THE CAPACITY IS THE FAMILY'S OWN, not the alphabet's. An earlier
    rule counted every string of the alphabet at every permitted length,
    which is a much larger number than the construction can actually
    write: the class the cell has to read back as, the character it has
    to begin with, and the shape that keeps it inside its band all
    narrow it (review item P2-C1-F2). What is counted here is the
    mapping `_family_at` actually walks, so a description asking for
    more different values than the family holds is refused before a
    single cell is built rather than searched for forever.

    A FAMILY THAT CANNOT HOLD ``words`` WORDS HOLDS NOTHING AT ALL, and
    that is the honest answer rather than a technicality (review item
    P2-C4-F2). The three numeric classes each write one unbroken run of
    characters -- a number, a number too large to hold, a notation
    inside accounting parentheses -- and none of them has a space
    anywhere, so no cell of theirs holds two words however long it is.
    Answering with a capacity here let a group pinned to the published
    largest word count be given a numeric class, write one word, and
    miss `words.max` with nothing said.
    """
    if words > 1 and kind != _CLASS_TEXT:
        return 0
    if kind == _CLASS_NUMBER:
        if band == _BAND_DIGITS:
            return _power_at_most(10, max(length, 1), _DOMAIN_CEILING)
        if band == _BAND_CODE:
            if length < 2:
                return 0
            if length == 2:
                return 10
            return _power_at_most(10, length - 2, _DOMAIN_CEILING)
        if length < 2:
            return 0
        if length == 2:
            return 10
        return _power_at_most(10, length - 2, _DOMAIN_CEILING)
    if kind == _CLASS_OUT_OF_RANGE:
        if band == _BAND_DIGITS:
            return 9 * _power_at_most(
                10, max(length, 310) - 1, _DOMAIN_CEILING
            )
        if band == _BAND_CODE:
            if length < 5:
                return _DOMAIN_CEILING
            return _power_at_most(10, length - 4, _DOMAIN_CEILING)
        if length < 8:
            return _DOMAIN_CEILING
        return _power_at_most(10, length - 7, _DOMAIN_CEILING)
    if kind == _CLASS_CONTRADICTORY:
        if band != _BAND_WIDE:
            return 0
        if length < 4:
            return _DOMAIN_CEILING
        return _power_at_most(10, length - 3, _DOMAIN_CEILING)
    if band == _BAND_DIGITS:
        return 0
    if band == _BAND_CODE and words > 1:
        # A CELL OF SEVERAL WORDS IS NEVER IN THE CODE ALPHABET. The
        # words are separated by a space, and a space is not one of the
        # characters that alphabet holds, so a group that has to carry
        # more than one word cannot answer for `n_code_alphabet` however
        # it is written. Saying so here is what lets the packing put the
        # code-alphabet count on the groups that can actually hold it
        # rather than spending it on groups that cannot (review item
        # P2-C1-F1).
        return 0
    return _worded_room(
        _text_head(band), _text_alphabet(band), max(length, 1), max(words, 1)
    )


def _number_at(band: str, length: int, index: int) -> "str | None":
    """A cell that reads as an ordinary number, in one band (G9.5 step 3).

    In figures alone it is a plain whole number; in the code alphabet it
    carries an exponent, which holds a letter and so keeps it out of the
    all-figures count; outside the code alphabet it carries a decimal
    point, which is a character the code alphabet does not hold.

    TWO CHARACTERS ARE ENOUGH FOR THE CODE ALPHABET, and saying they
    were not lost published counts a real table reaches (review item
    P2-C4-F2). An exponent needs three characters, so this family used
    to begin at three and a group of two-character values that had to
    answer for the code-alphabet count could not: a source of one
    one-character number, five two-letter words and six copies of `-3`
    publishes twelve code-alphabet cells, of which six read as numbers,
    and its own values are the assignment. A leading minus sign is a
    character the code alphabet holds and the figures do not, and what
    follows it is still read as a number, so the family begins at two.
    """
    if band == _BAND_DIGITS:
        return _spelling_at(_DIGITS, max(length, 1), index)
    if band == _BAND_CODE:
        if length < 2:
            return None
        if length == 2:
            return f"-{_spelling_at(_DIGITS, 1, index)}"
        return f"{_spelling_at(_DIGITS, length - 2, index)}e1"
    if length < 2:
        return None
    if length == 2:
        return f"{_spelling_at(_DIGITS, 1, index)}."
    return f"{_spelling_at(_DIGITS, length - 2, index)}.5"


def _out_of_range_at(band: str, length: int, index: int) -> "str | None":
    """A cell holding a well-formed number too large or too small to hold.

    In figures alone it is a whole number wider than this format can
    hold, which needs three hundred and ten figures however short the
    published length is -- the class outranks the length, because the
    class is recounted and a length is approximated on every group but
    the two pinned ones. In the code alphabet it carries an exponent.
    Outside the code alphabet it is a fraction too small to hold, whose
    decimal point is the character the code alphabet does not have.
    """
    if band == _BAND_DIGITS:
        width = max(length, 310)
        return f"{(index % 9) + 1}{_spelling_at(_DIGITS, width - 1, index // 9)}"
    if band == _BAND_CODE:
        if length < 5:
            return f"{index + 1}e999"
        return f"{_spelling_at(_DIGITS, length - 4, index)}e999"
    if length < 8:
        return f"0.{index + 1}e-999"
    return f"0.{_spelling_at(_DIGITS, length - 7, index)}e-999"


def _contradictory_at(length: int, index: int) -> "str | None":
    """A cell whose numeric notation conflicts with itself.

    Accounting parentheses hold a sign twice over. They are characters
    the code alphabet does not have, so a cell like this always stands
    outside both alphabet counts, which is why the packing rule never
    offers this class either of the other two bands.
    """
    if length < 4:
        return _contradictory_spelling(index + 1)
    return f"(-{_spelling_at(_DIGITS, length - 3, index)})"


def _worded(
    head: "tuple[str, ...]",
    alphabet: "tuple[str, ...]",
    length: int,
    words: int,
    index: int,
) -> str:
    """``words`` words of nearly equal length, longer first, in one cell.

    The index is taken apart by the radix each word actually has -- the
    first word's permitted opening characters times the alphabet for the
    rest of it, and the whole alphabet for every word after that. An
    earlier rule used two fixed radices instead, so the walk came back
    to spellings it had already written and a column asking for more
    than that many different values could never finish (review item
    P2-C1-F2).
    """
    room = length - (words - 1)
    if room < words:
        words = 1
        room = length
    base = room // words
    extra = room - base * words
    built = ""
    rest = index
    for place in range(words):
        size = base + (1 if place < extra else 0)
        if place == 0:
            radix = len(head) * _power_at_most(
                len(alphabet), size - 1, _DOMAIN_CEILING
            )
            built = _headed_spelling(head, alphabet, size, rest % max(radix, 1))
            rest = rest // max(radix, 1)
        else:
            radix = _power_at_most(len(alphabet), size, _DOMAIN_CEILING)
            built = (
                f"{built}{_SPACE}"
                f"{_spelling_at(alphabet, size, rest % max(radix, 1))}"
            )
            rest = rest // max(radix, 1)
    return _fixed_ends(built, alphabet)


def _worded_room(
    head: "tuple[str, ...]",
    alphabet: "tuple[str, ...]",
    length: int,
    words: int,
) -> int:
    """How many different cells `_worded` can write, saturated.

    The product of every word's own radix. It is an upper bound rather
    than an exact count, because the positional rules of method G9.1 put
    two different indices onto the same spelling where a word would
    otherwise begin with a character no made-up value may begin with.
    That costs nothing: the walk steps past a spelling it has already
    written, so what a column is finally offered is the number the walk
    itself produced, and that is the number a refusal quotes.
    """
    room = length - (words - 1)
    if room < words:
        words = 1
        room = length
    base = room // words
    extra = room - base * words
    total = 1
    for place in range(words):
        size = base + (1 if place < extra else 0)
        if place == 0:
            total = total * len(head) * _power_at_most(
                len(alphabet), size - 1, _DOMAIN_CEILING
            )
        else:
            total = total * _power_at_most(
                len(alphabet), size, _DOMAIN_CEILING
            )
        if total >= _DOMAIN_CEILING:
            return _DOMAIN_CEILING
    return total


# HOW FAR THE FOLD-COLLISION ASK MAY WALK. A value owed a case variant
# has to hold a character that has a case, and the pass that asks for
# one steps past values that do not. The ask is an ASK and not a
# promise: after this many steps that PASS gives up and hands back "no
# more", which puts the walk back exactly where the pass began (method
# G9.2) so the ordinary rule takes the same indices it would have taken
# anyway. Edge spacing then carries the collision instead where the
# length range leaves room for it, and where it does not the folded
# count comes up short and the recount names it -- either of which is
# better than spending a whole family looking for a letter that a
# class's own shape may never produce.
#
# THE NUMBER IS NORMATIVE, not a local choice. Two programs giving up
# at different points would part company on the first family holding a
# value with a case between their two ceilings, and the twin's bytes
# would stop being a function of the description and the seed, so the
# method states this number and this module spells it the same.
#
# The give-up used to drop the ask and CARRY ON in the same pass, which
# left every index the ask had stepped over spent for good -- so a
# column whose family began with more than this many letterless
# spellings lost that many different values it could otherwise have
# written, and the walk's stated promise that an ask never spends a
# family the ordinary rule could still have used was not true of it
# (review item P2-C2-F8).
_ASK_STEPS = 4096


def _reads_in_band(candidate: str, band: str) -> bool:
    """Whether a finished cell recounts into the band it was made for.

    Asked with the SHIPPED readers, on the trimmed cell, exactly as
    `_alphabet_notes` recounts the twin -- so what this permits and
    what a person recounting the column measures are one predicate and
    cannot drift apart.
    """
    bare = parsing.trimmed(candidate)
    if band == _BAND_DIGITS:
        return parsing.is_digit_text(bare)
    if band == _BAND_CODE:
        return parsing.is_code_text(bare) and not parsing.is_digit_text(bare)
    return not parsing.is_code_text(bare) and not parsing.is_digit_text(bare)


def _made_up_cell(
    kind: str,
    band: str,
    length: int,
    words: int,
    letter: bool,
    states: "dict[str, list[int]]",
    used: "dict[str, int]",
    form: str = "",
    holes: "tuple[str, ...]" = (),
) -> "str | None":
    """One made-up cell of one class, one band and one length, or None.

    Each construction is class-preserving, and that is CHECKED here
    rather than assumed: what comes out reads back through the shipped
    classifier as the class it was built for, and a candidate that does
    not is stepped past. The walk runs over the family's own index
    range, so it always ends: None says the family is spent, and the
    caller either refuses generation before anything is written or, on a
    declared column of record numbers, lets values repeat by the rule
    owner decision 6 fixes.

    ``letter`` asks for a value holding a character that has a case,
    because this one is owed a fold collision and only such a value can
    carry one (method G9.3 step 1). It is an ASK, not a promise: where
    no value of the family holds a letter, the walk is put back exactly
    where it started and taken again without the ask, so the ask cannot
    spend a family that the ordinary rule could still have used. The
    folded count then comes up short and the recount names it.
    """
    # THE CURSOR IS THE FAMILY'S AND THE FORM'S, NOT THE FAMILY'S ALONE
    # (review round 2 finding 3). Two forms of one family shared it, so
    # after the first form had walked two hundred and twenty spellings
    # the second -- whose whole supply is twenty-six -- began past its
    # own end and was never tried at all: the twin wrote two hundred
    # and forty cells of the first form and none of the second. A form
    # walks its own supply from its own start.
    key = f"{kind}/{band}/{length}/{words}"
    if key not in states:
        states[key] = [0]
    state = states[key]
    began = state[0]
    if form:
        # THE FORM'S CURSOR IS KEYED WITH A SPACE, not with a slash. A
        # slash is one of the thirteen marks a form may hold, so a
        # slashed key is injective only by an argument about how many
        # fields each kind of key has; no class name, band name, whole
        # number or admitted form can hold a SPACE, so this one is
        # injective by inspection.
        shaped = f"{key} {form}"
        if shaped not in states:
            states[shaped] = [0]
        # THE FORM IS AN ASK TOO, AND IT IS ASKED FIRST. Where the
        # column published one that fits this value, the value is
        # written in it; where the form's own spellings cannot satisfy
        # the family -- they read back as another class, or the form's
        # supply is spent -- the walk is taken again WITHOUT it, so a
        # form can cost the column no value it would otherwise have had
        # (P4-D18).
        #
        # A FORM PASS THAT GAVE UP UNDER THE LETTER ASK IS PUT BACK
        # EXACTLY WHERE IT BEGAN; ONE THAT GAVE UP WITHOUT THE ASK
        # LEAVES ITS CURSOR WHERE IT STOPPED. That is verbatim the rule
        # the family cursor two lines below already obeys, so one
        # sentence governs both.
        #
        # NEITHER HALF IS OPTIONAL, and both were got wrong in turn.
        # Sharing one cursor between two forms left the second never
        # tried at all (review round 2 finding 3). Never putting the
        # form's cursor back -- the first repair -- let the letter
        # ask's give-up path walk a form's WHOLE supply producing
        # nothing, so a column publishing two hundred cells of one
        # shape got zero of them where this rule gets a hundred and
        # eighty. And putting it back UNCONDITIONALLY costs the run:
        # measured on a column whose every spelling of a form is
        # refused, a thousand fillings under this rule against two
        # hundred and forty thousand under that one.
        shaped_state = states[shaped]
        marked = shaped_state[0]
        found = _walked_cell(
            kind, band, length, words, letter, shaped_state, used, form,
            holes,
        )
        if found is not None:
            return found
        if letter:
            shaped_state[0] = marked
    found = _walked_cell(kind, band, length, words, letter, state, used)
    if found is None and letter:
        state[0] = began
        found = _walked_cell(kind, band, length, words, False, state, used)
    return found


def _walked_cell(
    kind: str,
    band: str,
    length: int,
    words: int,
    letter: bool,
    state: "list[int]",
    used: "dict[str, int]",
    form: str = "",
    holes: "tuple[str, ...]" = (),
) -> "str | None":
    """One pass of the family's walk, from where the last one stopped.

    The pass visits the family's indices in order and stops at the
    family's own size, which is settled before it begins. What it can
    step past is fixed here and nowhere else: a candidate the column has
    already written or already folded onto, one that reads back as some
    other numeric class, one that means "no value", one that reads as a
    date, and -- only while a fold collision is being asked for -- one
    that holds no character with a case. THE LAST FOUR HAVE NOTHING TO
    DO WITH WHAT THIS COLUMN HAS WRITTEN, so the number of indices one
    value costs is bounded by the family's own size and by the ask
    ceiling, and by nothing smaller (review item P2-C2-F8).
    """
    room = _family_room(kind, band, length, words)
    if form:
        # A FORM'S SUPPLY IS ITS OWN AND IS USUALLY MUCH SMALLER THAN
        # THE FAMILY'S (review round 1 finding 3, found again on this
        # side of the walk). Every spelling of `-999-A` opens with the
        # character a spreadsheet reads as the start of a formula, so
        # every candidate is refused -- and bounded by the WIDE band's
        # room at six characters, that refusal loop runs for minutes
        # before the walk gives up. Bounded by the form's own supply it
        # gives up at once, and the caller then takes the walk again
        # without the form.
        room = min(room, _form_room(form), _STAND_IN_STEPS)
    asked = 0
    while state[0] < room:
        index = state[0]
        state[0] = state[0] + 1
        candidate: "str | None" = None
        if form:
            candidate = _filled_form(form, index)
        else:
            candidate = _family_at(kind, band, length, words, index)
        if candidate is None:
            return None
        if letter and not _has_letter(candidate):
            asked = asked + 1
            if asked >= _ASK_STEPS:
                return None
            continue
        if not _free(candidate, used):
            continue
        if parsing.classify_number(candidate) != _reads_as(kind):
            continue
        if parsing.is_missing_text(candidate):
            continue
        if _reads_as_a_date(candidate):
            continue
        if not _reads_in_band(candidate, band):
            # THE BAND IS NOT THE CLASS, AND ONLY THE CLASS WAS ASKED
            # (review round 2 finding 7). A form's spelling is built
            # from the CELL's shape and filled from ASCII, so a column
            # of Greek-letter codes published `n_code_alphabet: 0` and
            # its twin recounted 240. Both counts are exact facts of
            # the description, so the form yields to them: the
            # candidate is refused, the walk is taken again without the
            # form, and the census is missed instead -- which
            # `_form_notes` then says.
            #
            # ASKED OF EVERY CANDIDATE AND NOT ONLY OF A FORM'S. Every
            # spelling `_family_at` builds is in its band by
            # construction, so gating this on `form` would change
            # nothing -- measured across all sixty-one class, band,
            # length and word combinations the packing can assign, not
            # one candidate leaves its band. But "by construction" is
            # an argument and this is a check, and a check that runs
            # on everything cannot be quietly weakened to run on
            # nothing. `tests/test_p4d18_shape_forms.py` holds the
            # enumeration.
            continue
        if form and not _is_a_usable_stand_in(candidate, holes):
            # THE FORM'S OWN MARKS ARE NOT THE ALPHABETS' (review round
            # 1 finding 6). Every candidate `_family_at` builds comes
            # from an alphabet with the four hazardous characters taken
            # out, so the checks above were the whole of what a
            # candidate owed. A form is built from the CELL, so it can
            # open with `=` -- a column of `=A00` published `=A99` and
            # its twin wrote two hundred and forty cells a spreadsheet
            # reads as formulas. The four properties are asked here on
            # the same terms the label walk asks them.
            continue
        return _claim(candidate, used)
    return None


# -- columns of numbers too large or too small to hold (method G10.5) --


def _unrepresentable_cells(
    column: contract.ColumnBlock, groups: "tuple[int, ...]"
) -> "tuple[list[str], list[Deviation]]":
    """Every present cell of a column of numbers that cannot be held.

    The description publishes no width and no magnitude for this role --
    two columns of overflowing values, one about four hundred characters
    wide and one about four thousand, publish identically -- so one
    canonical width is made up, used for every such column, and named in
    the report in those words.

    What IS published is packed exactly wherever any packing exists
    (review item P2-C1-F1): how many values are whole, how many are
    fractions, how many fell off the range, and how the signs divide.
    Every one of those counts is then recounted from the finished cells
    in `generate` and named there where it was missed, so a whole or a
    sign the group sizes could not reach is never silent.
    """
    facts = column.facts
    if not isinstance(facts, contract.UnrepresentableFacts):
        raise _wrong_facts(column.name)
    kinds, signs = _unrepresentable_families(column, facts, groups)
    used: dict[str, int] = {}
    states: dict[str, list[int]] = {}
    spellings: list[str] = []
    folded = min(column.n_distinct_folded, len(groups))
    families = [
        f"{kinds[index]}/{signs[index]}" for index in range(len(groups))
    ]
    # NO PUBLISHED LENGTH AT ALL on this role (residual R-P2-1), so the
    # fold-collision partners of method G9.3 are held to no length
    # window: edge spacing may run on as far as the collisions need,
    # and nothing a person can recount on the twin moves when it does.
    windows: list[tuple[int, int | None]] = [
        (1, None) for _each in groups
    ]
    for index in range(len(groups)):
        partner = _partner_of(
            index, folded, spellings, families, used, windows
        )
        if partner is not None:
            spellings = spellings + [_take(partner, used)]
            continue
        spelling = _wide_number(
            kinds[index], signs[index], states, used, _hole_spellings(column)
        )
        if spelling is None:
            raise errors.ProfileError(
                _domain_too_small(
                    column.name,
                    _wide_shape_words(kinds[index], signs[index]),
                    len(groups),
                    index,
                )
            )
        spellings = spellings + [spelling]
    notes = [
        _deviation(
            column.name,
            "width",
            "no width at all: the description publishes none",
            f"every value written {_CANONICAL_WIDTH} figures wide",
            "The description of a column like this carries no width, so "
            "the twin uses one made-up width for every such column and "
            "says so here rather than implying the real one was this wide.",
        )
    ]
    return _grouped(groups, spellings), notes


def _wide_shape_words(kind: int, negative: bool) -> str:
    """What one kind of unrepresentable value is, in a person's words."""
    sign = "positive"
    if negative:
        sign = "negative"
    if kind == 0:
        return "written in numeric notation that conflicts with itself"
    if kind == 1:
        return f"{sign} whole numbers too large for this format to hold"
    if kind == 2:
        return f"{sign} fractions too small for this format to hold"
    if kind == 3:
        return f"{sign} whole numbers this format can hold"
    if kind == 4:
        return f"{sign} fractions this format can hold"
    return "written as ordinary text"


def _sign_permits(kind: int) -> int:
    """Which of the three sign counts one magnitude class can answer for.

    A value whose notation conflicts with itself carries NO sign -- the
    shipped parser answers "unknown" and never guesses -- and so does a
    cell of ordinary text, so those two classes answer only for the
    unknown count. Every other class carries a sign of its own.

    Read from the same table the whole-number permission is read from,
    so the two cannot drift apart: a class settles both questions or
    neither, which is what the parser answers (method G10.5 step 1).
    """
    if _wide_settles(_WIDE_CLASS_OF[kind]):
        return 0b011
    return 0b100


# WHICH PUBLISHED COUNT EACH MAGNITUDE CLASS ANSWERS FOR. The six
# classes a wide cell can be written in are an implementation's own
# spelling shapes; the description publishes three families of counts
# over the same cells and NO cross-tabulation of them (contract 6.2,
# invariants X2, U1 and U2). These two tables are the whole of the tie
# between the two, and they are read from the shipped parser's own
# answers: what the notation classifies as, and whether it settles the
# value as a whole number.
_WIDE_CLASS_OF = (0, 1, 1, 2, 2, 3)
_WIDE_WHOLE_OF = (2, 0, 1, 0, 1, 2)


def _wide_settles(notation: int) -> bool:
    """Whether one notation class settles a sign and a whole-number status.

    Notation that conflicts with itself and ordinary text settle
    neither: the shipped parser answers "unknown" to both questions and
    never guesses. Numbers the format holds and numbers that fell off
    its range settle both.
    """
    return notation == 1 or notation == 2


def _wide_kind(notation: int, whole: int) -> int:
    """The magnitude class one notation class and whole status write as."""
    if notation == 0:
        return 0
    if notation == 3:
        return 5
    for kind in range(len(_WIDE_CLASS_OF)):
        if _WIDE_CLASS_OF[kind] == notation and _WIDE_WHOLE_OF[kind] == whole:
            return kind
    return 0


def _unrepresentable_families(
    column: contract.ColumnBlock,
    facts: contract.UnrepresentableFacts,
    groups: "tuple[int, ...]",
) -> "tuple[list[int], list[bool]]":
    """The magnitude class AND the sign of every group, decided together.

    THE THREE PUBLISHED FAMILIES ARE ONE QUESTION (review items P2-C2-F1
    and P2-C3-F1). Which class a group takes settles which sign counts
    and which whole-number counts it can answer for, so deciding them
    one after the other throws away joint answers that exist: a
    five-row column with groups 1, 1, 1 and 2 has an exact
    class-and-sign assignment that two separate walks miss, writing two
    negative cells and none positive against one of each.

    THE GRID CARRIES THE COUNTS THE DESCRIPTION PUBLISHES AND NOT ONE
    MORE. An earlier revision split `n_out_of_range` between whole
    numbers and fractions with a `min(...)` of its own, packed the six
    classes that split produced against the sign counts, and so asked
    the walk to answer a cross-tabulation the description never carried.
    Review item P2-C3-F1 built the six-row column that breaks: four
    groups of 2, 2, 1 and 1 publishing two numeric, one out of range and
    three contradictory cells, two whole, one fraction and three
    settling neither, and three negative cells against three settling no
    sign. Sending the one out-of-range cell to "whole" leaves quotas no
    packing of those groups meets, and six exact counts came out wrong
    -- while sending it to "fraction" answers every one of them. The
    real column proves only that SOME cross-tabulation of the published
    counts exists, never which, so no cross-tabulation is assumed here:
    the three published families are three margins over one grid, and
    the walk chooses among every cross-tabulation they permit.

    Where no packing meets all three at once -- which no description a
    real table produced can reach, because that table's own values are
    such a packing -- each family is packed after the one before it, and
    every count missed either way is measured from the finished cells
    and named in the report there.
    """
    signs = [facts.n_negative, facts.n_positive, facts.n_sign_unknown]
    notations = [
        column.n_contradictory,
        column.n_out_of_range,
        column.n_numeric,
        column.n_not_numeric,
    ]
    wholes = [facts.n_whole, facts.n_fraction, facts.n_whole_unknown]
    width = len(signs)
    kinds = len(_WIDE_CLASS_OF)
    cells = kinds * width
    together = _allotted_over(
        groups,
        [
            (
                notations,
                [_WIDE_CLASS_OF[cell // width] for cell in range(cells)],
            ),
            (
                wholes,
                [_WIDE_WHOLE_OF[cell // width] for cell in range(cells)],
            ),
            (
                signs,
                [cell - (cell // width) * width for cell in range(cells)],
            ),
        ],
        [_spread_pairs(kinds, width) for _each in groups],
    )
    if together is not None:
        return (
            [cell // width for cell in together],
            [cell - (cell // width) * width == 0 for cell in together],
        )
    written = _allocation(
        groups, notations, [_every_bucket(len(notations)) for _each in groups]
    )
    settled = [
        0b011 if _wide_settles(written[place]) else 0b100
        for place in range(len(groups))
    ]
    parted = _allocation(groups, wholes, settled)
    chosen = _allocation(groups, signs, settled)
    return (
        [
            _wide_kind(written[place], parted[place])
            for place in range(len(groups))
        ],
        [chosen[place] == 0 for place in range(len(groups))],
    )


def _spread_pairs(kinds: int, width: int) -> int:
    """The class-and-sign pairs any group of a wide column may stand in."""
    mask = 0
    for kind in range(kinds):
        permitted = _sign_permits(kind)
        for sign in range(width):
            if (permitted >> sign) & 1:
                mask = mask | (1 << (kind * width + sign))
    return mask


def _wide_number(
    kind: int, negative: bool, states: "dict[str, list[int]]",
    used: "dict[str, int]", holes: "tuple[str, ...]",
) -> "str | None":
    """One value at the canonical width, of one kind and one sign.

    Every index writes a different spelling, so the walk ends: at most
    one index per piece of text already written in this column can be
    refused, and the ceiling says exactly that. None says the family is
    spent, which no producible description reaches, and the caller
    refuses generation rather than searching on.
    """
    key = f"{kind}/{negative}"
    if key not in states:
        states[key] = [0]
    state = states[key]
    lead = "-" if negative else ""
    steps = 0
    while steps < len(used) + 2:
        steps = steps + 1
        index = state[0]
        state[0] = state[0] + 1
        if kind == 0:
            candidate = _contradictory_spelling(index + 1)
        elif kind == 1:
            figures = _spelling_at(_DIGITS, _CANONICAL_WIDTH - 1, index // 9)
            candidate = f"{lead}{(index % 9) + 1}{figures}"
        elif kind == 2:
            figures = f"{index + 1}"
            zeros = max(_CANONICAL_WIDTH - len(figures), 1)
            candidate = f"{lead}0.{'0' * zeros}{figures}"
        elif kind == 3:
            candidate = f"{lead}{'0' * index}1"
        elif kind == 4:
            candidate = f"{lead}{'0' * index}0.5"
        else:
            candidate = _text_spelling(index + 1, used, holes)
        if _unused(candidate, used):
            return _take(candidate, used)
    return None


# -- the generation refusals (method G12) -----------------------------


def _counts_contradict(
    name: str, zeros: int, negatives: int, numbers: int
) -> str:
    """A column whose zero and negative counts leave no room (G12).

    A refusal of GENERATION, and it says so: the description is valid,
    and what cannot be done is building a column of numbers that holds
    all three counts at once.
    """
    return (
        f"The description of the column '{parsing.visible(name)}' is "
        f"valid, but synthtwin cannot build a twin column from it. It says "
        f"{numbers} of the column's values read as a number, that {zeros} "
        f"of them are zero and that {negatives} of them are negative, and "
        f"those three counts leave fewer than none over for the values "
        f"that are greater than zero. No table can hold all three at once, "
        f"so there is nothing to build. Nothing has been written and every "
        f"file in the folder is as it was. What to do next: if the "
        f"description file was edited by hand, put those three counts "
        f"back; otherwise describe the table again with 'synthtwin "
        f"profile', which works these counts out from the table itself."
    )


def _domain_too_small(
    name: str, shape: str, wanted: int, held: int
) -> str:
    """A column needing more different values than its own shape can spell.

    The `generation-domain-too-small` refusal of method G9.4. ``shape``
    says, in a person's words, exactly what kind of value the column
    asked for -- how long, written with which characters, and what it
    has to read back as -- and ``held`` is the number synthtwin could
    actually write of that kind, counted by the same walk that would
    have written them.
    """
    return (
        f"The description of the column '{parsing.visible(name)}' is "
        f"valid, but synthtwin cannot build a twin column from it. It says "
        f"{wanted} of the column's different values are {shape}. There are "
        f"only {held} different values synthtwin can write that way, so "
        f"the two facts cannot both hold in any table. Nothing has been "
        f"written and every file in the folder is as it was. What to do "
        f"next: if this column holds record numbers, describe the table "
        f"again with '--identifier {parsing.visible(name)}', which keeps "
        f"the width and lets values repeat. If you no longer have the "
        f"table, this column cannot be built from the description on its "
        f"own; please report it, with this message, so the rule can be "
        f"looked at."
    )


def _edited_by_hand(first: str, second: str) -> str:
    """What to do about a pair of facts no described table produces.

    The remediation a refusal owes is remediation THE PERSON CAN CARRY
    OUT, and plan P2-D6 rule 5 fixes the one thing it may not assume:
    that the table is still in reach. So the description file itself --
    which the person is holding, since they just handed it over -- comes
    first, and describing the table again is offered afterwards for the
    people who still can. ``first`` and ``second`` are the two edits that
    settle this particular pair, each written as an instruction.
    """
    return (
        f"Nothing has been written and every file in the folder is as it "
        f"was. What to do next: no described table produces this pair, so "
        f"the description has been edited since synthtwin wrote it. If you "
        f"kept the description synthtwin wrote, use that one. If you did "
        f"not, either of two edits to the description file settles it, and "
        f"the twin then carries the fact you wrote rather than the one it "
        f"replaced: {first}, or {second}. The description file is all "
        f"synthtwin needs for this, so neither edit asks you for the "
        f"table. If you do still have the table, describing it again with "
        f"'synthtwin profile' works both facts out from the table itself."
    )


def _words_exceed_length(
    name: str, shortest: bool, words: int, length: int, held: int, needed: int
) -> str:
    """A column of text whose word extreme its own lengths cannot hold.

    The `generation-words-exceed-length` refusal of method G12. A value
    of `L` characters holds at most `(L + 1) // 2` words -- every word
    needs a character of its own and every word after the first needs a
    space in front of it -- so a published word extreme above that
    number and the published length it is measured against cannot both
    hold in any table. This is a refusal of GENERATION and it says so:
    the description is valid, and what cannot be done is building the
    column.
    """
    wide = f"{length} character" if length == 1 else f"{length} characters"
    said = (
        f"no value holds fewer than {words} words, and that the shortest "
        f"value is {wide} long"
        if shortest
        else f"the largest number of words in a value is {words}, and that "
        f"no value is longer than {wide}"
    )
    carries = (
        f"the shortest value therefore cannot hold the {words} words every "
        f"value is said to hold"
        if shortest
        else f"no value is long enough to hold {words} of them"
    )
    most = "one word" if held == 1 else f"{held} words"
    return (
        f"The description of the column '{parsing.visible(name)}' is "
        f"valid, but synthtwin cannot build a twin column from it. It says "
        f"{said}. A value of {wide} holds at most {most}"
        f", because every word needs a character of its own and every "
        f"word after the first needs a space in front of it -- {words} "
        f"words need {needed} characters -- and {carries}. The two facts "
        f"cannot both hold in any table, so there is nothing to build. "
        + _edited_by_hand(
            f"bring the word count down to {held}",
            f"take the length up to {needed}",
        )
    )


def _whole_numbers_need_room(
    name: str, shortest: bool, present: int, digits: int, length: int
) -> str:
    """Record numbers published as whole numbers one character cannot spell.

    The `generation-whole-numbers-need-room` refusal of method G12. One
    character that reads as a whole number is a figure, and a value
    written in figures alone is counted in `n_all_digits`. So a
    description saying every value is a whole number, that some value is
    one character long, and that some value is NOT written in figures
    alone is a description no table can hold -- proved from the
    published numbers themselves, not from the shape of any walk this
    module happens to take.
    """
    wide = f"{length} character" if length == 1 else f"{length} characters"
    said = (
        f"the shortest value is {wide} long, and that none of "
        f"the {present} values is written in figures alone"
        if shortest
        else f"no value is longer than {wide}, and that "
        f"{present - digits} of the {present} values are not written in "
        f"figures alone"
    )
    carries = (
        "so the shortest value would have to be written in figures alone"
        if shortest
        else "so every one of these values would have to be written in "
        "figures alone"
    )
    return (
        f"The description of the column '{parsing.visible(name)}' is "
        f"valid, but synthtwin cannot build a twin column from it. It says "
        f"every value reads as a whole number, that {said}. One character "
        f"that reads as a whole number is a figure, {carries}. The two "
        f"facts cannot both hold in any table, so there is nothing to "
        f"build. "
        + _edited_by_hand(
            "say that the values are not all whole numbers",
            "give the values room for a second character",
        )
    )


def _seed_out_of_range(seed: int) -> str:
    """A seed outside the range synthtwin states for itself (P2-D8)."""
    return (
        f"The seed {seed} is outside the range synthtwin uses. Please give "
        f"a whole number from 0 to {_WORD_CEILING}, written in figures with "
        f"no sign and no spaces, for example --seed 0 or --seed 12345."
    )


# -- the generation-feasibility stage (plan P2-D6) --------------------


def plan_generation(profile: contract.Profile) -> GenerationPlan:
    """Settle every generation decision before a single cell is built.

    Guarantees:

    - Inputs: one loaded description and nothing else. No path, no
      table, no handle, no seed: this stage decides only what the
      published facts allow, so its answer is the same for every seed.
    - Determinism: a fixed function of the description. It reads no
      clock, no environment and no random source.
    - Errors raised: `errors.ProfileError`, and only for the four
      refusals method G12 names -- a column of numbers whose counts of
      zero and negative values leave no room; a column of text or of
      unheld numbers needing more different values than its own length
      range can spell; a column of text whose published word extreme
      needs more characters than its own published length carries; a
      declared column of record numbers published as whole numbers that
      one character cannot write outside the figures. A fifth stood
      here for one day, for whole record numbers in the code alphabet
      with no room for a third character; owner decision 9 withdrew it,
      because the counts that reach it prove the real column held
      sign-leading values and refusing denied a person a twin over a
      character their own file used. Each says the description is VALID,
      names the two facts that cannot both hold, and gives something to
      do next that does not assume the person still has the table. All are raised HERE, before any generation,
      so a refused run leaves every byte on disk exactly as it found it.
    - Boundary: reads only the typed description (method G1). It widens
      the domains first -- the alphabets hold both cases and the whole
      printable ASCII range -- and refuses only where no rule can meet
      what is published; a shortfall a rule CAN meet becomes a named
      deviation instead of a refusal.
    """
    plans: list[_ColumnPlan] = []
    words = 0
    everywhere = _every_hole_spelling(profile)
    for column in profile.columns:
        # THE LONG-TAIL DETECTION LINE reaches the free-text walk from
        # here, because only the profile carries the settings and only
        # the walk can act on them (residual R-P4-36).
        line = max(
            profile.settings.small_cell_floor,
            profile.settings.long_tail_minimum_level,
        )
        plan = _plan_column(column, profile.n_rows, everywhere, line)
        plans = plans + [plan]
        words = words + plan.content_words + plan.placement_words
    return GenerationPlan(columns=tuple(plans), words_planned=words)


def _plan_column(
    column: contract.ColumnBlock,
    n_rows: int,
    all_holes: "tuple[str, ...]" = (),
    long_tail_line: int = 0,
) -> "_ColumnPlan":
    """One column's plan: its word budget, its layout, its refusals."""
    facts = column.facts
    placement = max(n_rows - 1, 0)
    layout: _NumericLayout | None = None
    notes: list[Deviation] = []
    groups: tuple[int, ...] = ()
    cells: list[str] = []
    carriers = _FIRST_TWO
    content = 0
    if isinstance(facts, contract.JoinedFacts):
        # ONE LAYOUT PER POSITION, so the plan holds none of its own and
        # `_joined_content` builds each where it builds that position's
        # numbers. What is settled here is the WORD BUDGET, which the
        # capacity question needs before any cell exists: it is the sum
        # of what each position will draw.
        for place in range(facts.n_parts):
            _each, each_notes, each_content = _numeric_layout(
                _part_view(column, place), facts.parts[place]
            )
            notes = notes + each_notes
            content = content + each_content
            # ...and the words that shuffle this position against the
            # first, which every position after it needs.
            if place:
                content = content + max(facts.n_joined - 1, 0)
    elif isinstance(facts, contract.AffixedFacts):
        # The layout is the CORES' -- see `_core_view`.
        core = _core_view(column)
        layout, notes, content = _numeric_layout(core, facts.numbers)
    elif isinstance(facts, contract.NumericFacts):
        layout, notes, content = _numeric_layout(column, facts)
    elif isinstance(facts, contract.ClockFacts):
        _clock_room(column, facts)
        # THE SAME SHAPE THE DATE ROLE BUDGETS BY, and for the same
        # reason: both ends are pinned by fixed rule and cost no word,
        # every stand-in is stepped past its neighbours and costs none,
        # and each rank between the ends takes exactly one. `max(..., 0)`
        # covers a column of one parsed cell, and invariant T4 -- some
        # cell parsed -- is what stops it being none.
        content = max(column.n_present - facts.n_unparsed - 2, 0)
    elif isinstance(facts, contract.DatetimeFacts):
        content = max(column.n_present - facts.n_unparsed - 2, 0)
    elif isinstance(facts, contract.IdentifierFacts):
        _whole_number_room(column, facts)
        groups = _groups_of(facts.n_distinct_by_occurrences)
        cells, notes = _identifier_cells(column, groups)
    elif isinstance(facts, contract.TextFacts):
        groups = _groups_of(facts.n_distinct_by_occurrences)
        _word_room(column, facts)
        _fold_room(
            column, facts.length.minimum, facts.length.maximum, len(groups)
        )
        cells, notes, carriers = _text_cells(
            column, groups, long_tail_line
        )
    elif isinstance(facts, contract.UnrepresentableFacts):
        groups = _groups_of(facts.n_distinct_by_occurrences)
        cells, notes = _unrepresentable_cells(column, groups)
    return _ColumnPlan(
        column=column,
        all_holes=all_holes,
        content_words=content,
        placement_words=placement,
        layout=layout,
        cells=tuple(cells),
        notes=tuple(notes),
        carriers=carriers,
    )


def _word_capacity(length: int) -> int:
    """The most words a value of ``length`` characters can hold (G9.5).

    Every word holds at least one character and every word after the
    first is preceded by a space, so `w` words need `2w - 1` characters
    and a value of `L` characters holds at most `(L + 1) // 2` of them.
    One is the floor: a present value holds a word whatever its length.
    """
    return max((length + 1) // 2, 1)


def _word_room(
    column: contract.ColumnBlock, facts: contract.TextFacts
) -> None:
    """Refuse a column whose word extremes its own lengths cannot hold.

    The `generation-words-exceed-length` refusal of method G12 (review
    item P2-C5-F4). Plan P2-D6's feasibility rule 5 reserves refusal for
    descriptions no rule above it can satisfy, and this is one, PROVED
    from four published numbers rather than found by a walk giving up:
    `words.max` is the largest word count any value holds and
    `length.max` is the longest any value is, so the value carrying
    `words.max` is at most `length.max` characters long and cannot hold
    more words than that length carries; `words.min` is a floor under
    EVERY value, so the value carrying `length.min` has to hold it too.

    Until this check existed the shape stage clamped the word count
    instead, wrote a twin, and named the exact fact as missed -- which
    is the outcome the ratified plan reserves for facts a rule CAN meet.
    A person then received a twin the plan says they were never to get.
    """
    for shortest in (False, True):
        words = facts.words.minimum if shortest else facts.words.maximum
        length = (
            facts.length.minimum if shortest else facts.length.maximum
        )
        held = _word_capacity(length)
        if words <= held:
            continue
        raise errors.ProfileError(
            _words_exceed_length(
                column.name, shortest, words, length, held, 2 * words - 1
            )
        )


def _clock_room(
    column: contract.ColumnBlock, facts: contract.ClockFacts
) -> None:
    """Refuse a clock column asking for more times than a day holds.

    THE ONE REFUSAL THIS ROLE ADDS, and it is decided from the published
    facts alone, before a single cell exists. A day holds 1,440
    different minutes and 86,400 different seconds, and nothing else can
    be written in the column's form. So a description whose count of
    different values, NET of the cells that are stand-ins, exceeds its
    form's own space describes a column no table of that form can hold.

    THE TEST IS THE FORM'S CAPACITY AND NOT THE SPAN BETWEEN THE ENDS.
    A description whose own source met every count -- stand-ins
    included -- is never refused here: that is the difference between a
    description nothing can satisfy and one this method finds hard.

    Raised as a REFUSAL rather than reported as a deviation because
    there is no twin to report about: every arrangement of cells fails,
    so the honest answer is to say so before writing anything and to
    say that the description itself is valid -- what cannot be done is
    building a table from it.
    """
    wanted = column.n_distinct - facts.n_unparsed
    room = parsing.CLOCK_CAPACITY[facts.clock_form]
    if wanted <= room:
        return
    raise errors.ProfileError(_clock_needs_room(column.name, wanted, room))


def _clock_needs_room(name: str, wanted: int, room: int) -> str:
    """What a person is told when a day is not long enough."""
    return (
        f"synthtwin cannot build a twin of the column '{parsing.visible(name)}'. "
        f"Its description says the column holds {wanted} different "
        f"times of day, and it says those times are written with "
        f"{room} different ones available -- there are only {room} of "
        f"them in a day at that precision. Both statements can be true "
        f"of the description and neither can be true of any table, so "
        f"no file synthtwin could write would match it.\n\n"
        f"The description is not damaged and nothing is wrong with your "
        f"file. If the real column recorded seconds as well as minutes, "
        f"profile it again from the table that has them; if it did not, "
        f"there is nothing here to fix and this column cannot be "
        f"twinned. Nothing has been written."
    )


def _whole_number_room(
    column: contract.ColumnBlock, facts: contract.IdentifierFacts
) -> None:
    """Refuse record numbers no length range can write outside the figures.

    The `generation-whole-numbers-need-room` refusal of method G12
    (review item P2-C5-F4). ONE CHARACTER THAT READS AS A WHOLE NUMBER
    IS A FIGURE, and a value written in figures alone is one the
    description counts in `n_all_digits`. Two published pairs therefore
    contradict each other outright, and each is proved from the numbers
    themselves:

    - every value is a whole number, no value is longer than one
      character, and fewer than all of them are written in figures
      alone -- but every one-character whole number IS written in
      figures alone;
    - every value is a whole number, the shortest value is one
      character long, and NONE of them is written in figures alone --
      but that shortest value would have to be.

    Both were generated before this check existed, with
    `all_whole_numbers` recounted as false and named in the report. The
    ratified plan holds that fact EXACT-OBSERVABLE in every case and
    reserves the report line for facts a rule can meet, so the outcome
    the plan fixes for these two is a refusal of generation.

    What this does NOT refuse is a length range some spelling of some
    band can still use: two characters carry `1.` and three carry `1e0`,
    so a description this check passes is one the ordinary walk may
    attempt, and a shortfall it then meets is named rather than refused.

    AND ONE BAND IN, THE ANSWER IS A FLAG RATHER THAN A STOP (owner
    decision 9, 2026-08-13). Two characters carry `1.` outside the code
    alphabet, and inside it only a sign in front of a figure. A refusal
    stood here briefly; the owner withdrew it, because the counts that
    reach it prove the real column held such values, and refusing would
    deny someone a twin over a character their own table used. The
    cells are written and the report's formula paragraph names them.
    """
    if not facts.all_whole_numbers:
        return
    outside = column.n_present - facts.n_all_digits
    if facts.max_length < 2 and outside > 0:
        raise errors.ProfileError(
            _whole_numbers_need_room(
                column.name,
                False,
                column.n_present,
                facts.n_all_digits,
                facts.max_length,
            )
        )
    if facts.min_length < 2 and facts.n_all_digits < 1 and column.n_present:
        raise errors.ProfileError(
            _whole_numbers_need_room(
                column.name,
                True,
                column.n_present,
                facts.n_all_digits,
                facts.min_length,
            )
        )
    return


def _fold_room(
    column: contract.ColumnBlock, shortest: int, longest: int, wanted: int
) -> None:
    """Check the sub-domain that can carry a fold collision (G9.3).

    Where a column publishes fewer folded identities than raw spellings,
    the difference has to be carried by values a partner can be built
    from. THE FOLD TRIMS BEFORE IT TURNS THE CASE OVER, so there are two
    such values and this counts both: one that holds a character with a
    case, which a case flip varies, and one shorter than the longest
    published length, which edge spacing lengthens (review item
    P2-C2-F6). Counting only the first refused descriptions whose
    collisions the second can build. Both counts are worked out
    saturated, exactly as the capacity rule is.
    """
    partners = column.n_distinct - column.n_distinct_folded
    if partners < 1:
        return
    held = _lettered_domain_size(_WIDE, 1, longest, partners)
    if held < partners:
        held = held + _padded_room(_WIDE, shortest, longest, partners - held)
    if held < partners:
        raise errors.ProfileError(
            _domain_too_small(
                column.name,
                f"at most {longest} characters long and either hold a "
                f"character that has an upper and a lower case or leave "
                f"room for a space at one end, so that another value can "
                f"come down to it once case and edge spacing are ignored",
                partners,
                held,
            )
        )
    return


def _padded_room(
    alphabet: "tuple[str, ...]", shortest: int, longest: int, wanted: int
) -> int:
    """How many partners edge spacing supplies, saturated (G9.3).

    A value shorter than the longest published length carries a partner
    with no letter needed at all, because folding trims the two ends: a
    space added to either end comes down to the value itself. One parent
    of length ``L`` supplies one partner per way of spreading the spaces
    over its two ends without passing ``longest``, and two different
    parents never supply the same partner, so the counts add.
    """
    total = 0
    for length in range(max(shortest, 1), longest):
        if total >= wanted:
            return total
        shapes = 0
        for spread in range(1, longest - length + 1):
            shapes = shapes + spread + 1
        total = total + shapes * _power_at_most(
            len(alphabet), length, _DOMAIN_CEILING
        )
    return total


# -- the run (method G4) ----------------------------------------------


def _content_of(
    plan: "_ColumnPlan", words: "list[int]"
) -> "tuple[list[str], list[Deviation]]":
    """Build one column's present cells, dispatching on the AXES.

    The three axes are the three questions this module asks -- what
    condition the column is in, what kind of values it holds, and
    whether the person declared it as record numbers -- and the role
    name is never one of them (plan P2-D3).
    """
    column = plan.column
    if column.quality_state == "empty":
        return [], []
    if column.quality_state == "unrepresentable":
        return [cell for cell in plan.cells], []
    kind = column.statistical_type
    if kind == "constant" or kind == "binary" or kind == "categorical":
        return _label_content(plan)
    # THE LONG TAIL NAMES ITS OWN SHAPE (contract 14.1, C6-19) and is
    # written by the label rule verbatim: published labels at their
    # counts, invented neutral labels at the exact suppressed sizes.
    # Naming it here rather than folding it into the line above keeps
    # the axis table a bijection while leaving one construction.
    if kind == "long_tail_labels":
        return _label_content(plan)
    if kind == "count" or kind == "continuous":
        return _numeric_content(plan, words)
    if kind == "affixed_number":
        return _affixed_content(plan, words)
    if kind == "joined_numbers":
        return _joined_content(plan, words)
    if kind == "time_of_day":
        return _clock_content(plan, words)
    if kind == "datetime":
        return _datetime_content(plan, words)
    if kind == "code":
        return [cell for cell in plan.cells], []
    if kind == "text":
        return [cell for cell in plan.cells], []
    raise _wrong_facts(column.name)


def generate(profile: contract.Profile, seed: int) -> Twin:
    """Build the whole twin table from the description and the seed.

    Guarantees:

    - Inputs: one description loaded by `contract.load_profile`, and one
      whole number from 0 to 2**64 - 1. Nothing else: no path, no table,
      no handle, no file of any kind. The twin is a function of these
      two values and of this version of synthtwin, and of nothing else.
    - Determinism: the same description and the same seed produce the
      same cells, in the same order, on every machine -- one generator,
      made once from the seed and threaded through by hand; columns
      consumed in the description's own list order; every quantity
      derived from full-width words in whole-number arithmetic. A
      description whose published counts pin every cell produces the
      same cells whatever the seed is, because an arrangement of
      identical entries is identical. A change to this method's word
      counts shifts every later column at the same seed, which is why
      regenerating after a version change is a recorded event.
    - Errors raised: `errors.ProfileError` for a seed outside the stated
      range, and the generation refusals of `plan_generation`, which
      run BEFORE anything is built. It raises nothing else: a
      description the loader accepted is never called invalid here.
    - Boundary: the real table is never read, never named and never
      reachable from here (method G1). Nothing is written: this function
      hands back values, and the command decides what becomes of them.

    What comes back is the twin's cells both ways round, the header the
    description asks for, and one outcome per column recounted from the
    cells themselves, carrying every deviation measured against the fact
    it missed.
    """
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise errors.ProfileError(_seed_out_of_range(0))
    if seed < 0 or seed > _WORD_CEILING:
        raise errors.ProfileError(_seed_out_of_range(seed))
    plan = plan_generation(profile)
    generator = numpy.random.default_rng(seed)
    columns: list[tuple[str, ...]] = []
    outcomes: list[ColumnOutcome] = []
    deviations: list[Deviation] = []
    approximated: list[Approximation] = []
    drawn = 0
    for step in range(len(plan.columns)):
        each = plan.columns[step]
        column = each.column
        words: list[int] = []
        if each.content_words > 0:
            words = [
                int(word)
                for word in generator.integers(
                    0,
                    _WORD_CEILING,
                    size=int(each.content_words),
                    dtype="uint64",
                    endpoint=True,
                )
            ]
        drawn = drawn + len(words)
        content, notes = _content_of(each, words)
        if len(content) != column.n_present:
            raise errors.ProfileError(
                f"synthtwin internal check: the twin column for "
                f"'{parsing.visible(column.name)}' came out with "
                f"{len(content)} values where the description records "
                f"{column.n_present}. This means a mistake in synthtwin; "
                f"please report it. Nothing has been written."
            )
        content = content + _absent_cells(column)
        places: list[int] = []
        if each.placement_words > 0:
            places = [
                int(word)
                for word in generator.integers(
                    0,
                    _WORD_CEILING,
                    size=int(each.placement_words),
                    dtype="uint64",
                    endpoint=True,
                )
            ]
        drawn = drawn + len(places)
        order = _arrangement(places, profile.n_rows)
        written = [content[order[place]] for place in range(profile.n_rows)]
        columns = columns + [tuple(written)]
        counted = _recounted(written, _hole_spellings(column))
        notes = (
            list(each.notes)
            + notes
            + _recount_notes(column, counted)
            + _form_notes(column, written)
            + _class_notes(column, written)
            + _alphabet_notes(column, written)
            + _extreme_notes(column, written)
            + _width_notes(column, written)
            + _fraction_notes(column, written)
            + _pad_notes(column, written)
            + _whole_notes(column, written)
            + _magnitude_notes(column, written)
            + _style_notes(column, written)
            + _mix_notes(column, written)
        )
        # Every APPROXIMATED fact of this column, measured on the cells
        # just written and checked against both ends of the bound
        # method G12 fixes for it. One that landed outside its bound is
        # a fact the twin did not hold, so it joins the deviations too.
        measured = _approximations(column, each, written)
        notes = notes + _bound_notes(measured)
        approximated = approximated + measured
        deviations = deviations + notes
        outcomes = outcomes + [
            ColumnOutcome(
                name=column.name,
                position=column.position,
                role=column.role,
                statistical_type=column.statistical_type,
                quality_state=column.quality_state,
                structural_role=column.structural_role,
                n_present=counted[0],
                n_missing=counted[1],
                n_distinct=counted[2],
                n_distinct_folded=counted[3],
                content_words=each.content_words,
                placement_words=each.placement_words,
                deviations=tuple(notes),
                approximations=tuple(measured),
            )
        ]
    rows = [
        tuple([columns[place][row] for place in range(len(columns))])
        for row in range(profile.n_rows)
    ]
    return Twin(
        names=tuple([column.name for column in profile.columns]),
        write_header=profile.source.header_source == "file",
        n_rows=profile.n_rows,
        columns=tuple(columns),
        rows=tuple(rows),
        outcomes=tuple(outcomes),
        deviations=tuple(deviations),
        approximations=tuple(approximated),
        words_drawn=drawn,
        seed=seed,
    )


def _folded_excess_reason(column: contract.ColumnBlock) -> str:
    """Why a twin holds MORE folded identities than the description does.

    THE SENTENCE WRITTEN FOR A COLUMN OF DATES WAS REACHING A COLUMN IT
    IS FALSE OF (plan amendment A-P3-12). A column of dates is spread
    over its published ladder and its rule fixes no repetition at all,
    which is what "how often a value repeats is not a fact this
    column's rule holds on to" says. A DECLARED COLUMN OF RECORD
    NUMBERS is the one role where that is false: the repetition pattern
    is a published count that rule meets, and a run naming this line
    meets it in the same breath. What went wrong there is the one thing
    a reader has to be told in order to act -- the description asks for
    two spellings that come down to one value once case and edge
    spacing are ignored, and there was nowhere inside the published
    length range to write the second (method G9.3 step 5).
    """
    if isinstance(column.facts, contract.IdentifierFacts):
        return (
            "The description records two or more spellings that come "
            "down to the same value once upper and lower case and "
            "spaces at the ends are ignored, and the twin could not "
            "write them: the published length range and the kinds of "
            "value this column holds left no second way to spell one "
            "of them. So the twin holds MORE different values, "
            "ignoring case and edge spacing, than the description "
            "records. Code that groups rows by this column, or that "
            "matches it case-insensitively, sees more groups here than "
            "it will on your table."
        )
    return (
        "The twin holds MORE different values, ignoring case and edge "
        "spacing, than the description records, for the same reason: "
        "how often a value repeats is not a fact this column's rule "
        "holds on to."
    )


def _recount_notes(
    column: contract.ColumnBlock, counted: "tuple[int, int, int, int]"
) -> "list[Deviation]":
    """Name every distinctness count the written column did not reach.

    The counts are RECOUNTED from the cells this run built, not restated
    from the description, so a shortfall no rule predicted is named just
    as loudly as one a rule did. This runs on EVERY column, a declared
    column of record numbers included: that is where two of the three
    facts owner decision 6 gives up are measured.
    """
    notes: list[Deviation] = []
    # WHICH WAY the count went decides which sentence is true. A twin
    # holding FEWER different values ran out of ways to write one; a
    # twin holding MORE was never told how often a value repeats, which
    # is what a column of dates gets: this method spreads its values
    # over the published ladder and fixes no repetition at all. One
    # sentence for both directions read as a shortfall in both, and a
    # reader grouping rows by that column would have been told the
    # opposite of what happened (review item P2-C1-F4).
    if counted[2] != column.n_distinct:
        reason = (
            "The twin holds fewer different spellings than the "
            "description records, because the ways of writing a value "
            "that the description allows could not supply that many."
        )
        if counted[2] > column.n_distinct:
            reason = (
                "The twin holds MORE different spellings than the "
                "description records, because the rule that places this "
                "column's values does not fix how often one of them "
                "repeats. Code that groups rows by this column, or that "
                "removes duplicates, sees more groups here than it will "
                "on your table."
            )
        notes = notes + [
            _deviation(
                column.name,
                "n_distinct",
                f"{column.n_distinct}",
                f"{counted[2]}",
                reason,
            )
        ]
    if counted[3] != column.n_distinct_folded:
        reason = (
            "The twin holds fewer different values, ignoring case and "
            "edge spacing, than the description records."
        )
        if counted[3] > column.n_distinct_folded:
            reason = _folded_excess_reason(column)
        notes = notes + [
            _deviation(
                column.name,
                "n_distinct_folded",
                f"{column.n_distinct_folded}",
                f"{counted[3]}",
                reason,
            )
        ]
    return notes


def _present_of(
    written: "list[str]", holes: "tuple[str, ...]"
) -> "list[str]":
    """The cells of a written column that are PRESENT cells.

    NOT "every cell that is not blank", which is what nine recounts of
    this module asked and which is a different question (review round
    2 finding 11, widened by its own verification). A twin reproduces
    the spellings its source's absent cells wore (7.7), so a numeric
    column whose holes were written `-999` has twenty cells that LOOK
    like numbers and are not values -- and counting them recounted a
    mean of -40.4 against a published 39.5, a standard deviation of
    277 against 11.6, and a first percentile of -999.

    The validator was right about that file the whole time and said
    so; only the report written beside the twin accused it. Eleven
    fabricated deviations on a conforming twin is worse than none at
    all, because a person reading them abandons a twin that was fine.

    `_wears_a_published_hole` is the question a recount asks, and this
    is every recount asking it once.
    """
    return [
        cell for cell in written
        if cell != "" and not _wears_a_published_hole(cell, holes)
    ]


def _alphabet_notes(
    column: contract.ColumnBlock, written: "list[str]"
) -> "list[Deviation]":
    """Name either alphabet count the written column did not reach.

    The two roles that make their values up -- record numbers and free
    text -- publish how many present cells are figures alone and how
    many are written in the code alphabet, and a person can recount
    both on the twin. So a twin that misses one has to say so. This is
    measured from the cells this run wrote, never restated from the
    description, which is what makes it able to catch a shortfall no
    rule of this module predicted; the roles that publish neither count
    are passed over.
    """
    facts = column.facts
    if not isinstance(
        facts, (contract.IdentifierFacts, contract.TextFacts)
    ):
        return []
    published = (facts.n_all_digits, facts.n_code_alphabet)
    trimmed = [
        parsing.trimmed(cell)
        for cell in _present_of(written, _hole_spellings(column))
    ]
    counted = (
        len([cell for cell in trimmed if parsing.is_digit_text(cell)]),
        len([cell for cell in trimmed if parsing.is_code_text(cell)]),
    )
    notes: list[Deviation] = []
    if counted[0] != published[0]:
        notes = notes + [
            _deviation(
                column.name,
                "n_all_digits",
                f"{published[0]}",
                f"{counted[0]}",
                "The twin writes a different number of cells that are "
                "figures and nothing else, so a check that tells a "
                "written-out number from a code by looking at its "
                "characters can behave differently here than on the real "
                "table.",
            )
        ]
    if counted[1] != published[1]:
        notes = notes + [
            _deviation(
                column.name,
                "n_code_alphabet",
                f"{published[1]}",
                f"{counted[1]}",
                "The twin writes a different number of cells made only of "
                "letters, figures, hyphens and underscores, so a check "
                "that accepts or refuses a value by its characters can "
                "behave differently here than on the real table.",
            )
        ]
    return notes


def _named_miss(
    column: contract.ColumnBlock,
    fact: str,
    published: int,
    achieved: int,
    note: str,
) -> "list[Deviation]":
    """One deviation, or none, for a count recounted from the cells."""
    if published == achieved:
        return []
    return [
        _deviation(column.name, fact, f"{published}", f"{achieved}", note)
    ]


def _extreme_notes(
    column: contract.ColumnBlock, written: "list[str]"
) -> "list[Deviation]":
    """Name a published length or word end the written column did not reach.

    THE FOUR ENDS OF A COLUMN OF FREE TEXT ARE EXACT-OBSERVABLE (plan
    P2-D6), AND NOTHING WAS RECOUNTING THEM (review item P2-C4-F2). The
    shortest and longest value, and the fewest and most words in one
    value, are all four things a person measures on the twin in one
    pass. The construction pins each of them onto a group, so the run
    believes it holds them -- and a run that believes a fact is exactly
    the run that stops checking it. A group pinned to the published
    largest word count and then given a class that writes one unbroken
    run of characters wrote one word, and no line of the report said so.

    So the ends are measured here, from the cells this run wrote, beside
    the alphabet and class counts and by the same kind of recount. A
    fact this names is a fact the twin does not hold, whatever the plan
    that wrote it believed.
    """
    facts = column.facts
    if not isinstance(facts, contract.TextFacts):
        return []
    present = _present_of(written, _hole_spellings(column))
    if not present:
        return []
    lengths = [len(cell) for cell in present]
    counts = [parsing.token_count(cell) for cell in present]
    measured = (
        ("length.min", facts.length.minimum, min(lengths)),
        ("length.max", facts.length.maximum, max(lengths)),
        ("words.min", max(facts.words.minimum, 1), min(counts)),
        ("words.max", max(facts.words.maximum, 1), max(counts)),
    )
    reasons = {
        "length.min": "The twin's shortest value is not as long as the "
        "description records, so a check on the smallest size a value "
        "can take can behave differently here than on the real table.",
        "length.max": "The twin's longest value is not as long as the "
        "description records, so a check on the largest size a value "
        "can take, or a column width, can behave differently here than "
        "on the real table.",
        "words.min": "The twin's plainest value holds a different number "
        "of words than the description records, so code that splits a "
        "value into words sees a different smallest count here.",
        "words.max": "The twin's fullest value holds fewer words than "
        "the description records, so code that splits a value into "
        "words sees a different largest count here.",
    }
    notes: list[Deviation] = []
    for fact, published, achieved in measured:
        notes = notes + _named_miss(
            column, fact, published, achieved, reasons[fact]
        )
    return notes


def _quantitative_facts(
    column: contract.ColumnBlock,
) -> "contract.NumericFacts | None":
    """The numeric facts of a column that has some, or None.

    An affixed column HOLDS a numeric block rather than being one, so a
    reader written as "if this is a numeric column" walks past it -- and
    the census of widths is taken over its cores exactly as every other
    quantitative fact of that role is.
    """
    facts = column.facts
    if isinstance(facts, contract.AffixedFacts):
        return facts.numbers
    if isinstance(facts, contract.NumericFacts):
        return facts
    return None


def _fraction_notes(
    column: contract.ColumnBlock, written: "list[str]"
) -> "list[Deviation]":
    """Name a published fraction width the column could not place.

    The census is EXACT-OBSERVABLE: a person opens the twin, counts the
    figures after the point on every cell written with one, and gets the
    published census back. Where the twin cannot pay -- because no
    remaining width holds a whole value's cells, or because snapping
    that value would have split it -- it owes the reader a sentence
    rather than a silence.

    THIS IS A RECOUNT, taken off the finished text with the same reader
    the contract's own ladder uses, so a width the writer intended and
    a width the cell actually wears cannot come apart here.
    """
    facts = _quantitative_facts(column)
    if facts is None:
        return []
    published: dict[int, int] = {}
    for key in sorted(facts.fraction_widths):
        if key == contract.WITHHELD:
            continue
        published[int(key)] = facts.fraction_widths[key]
    if not published:
        return []
    pooled = 0
    if contract.WITHHELD in facts.fraction_widths:
        pooled = facts.fraction_widths[contract.WITHHELD]
    # THE RECOUNT IS OVER THE CORES ON THE AFFIXED ROLE, because that
    # is the population the census is about. Reading `$1.20` as a bare
    # number finds no number at all, so every cell of a column of
    # prices failed the test and the report said the published width
    # was written by NO cell of a twin that had in fact written every
    # one of them at it -- a report that accuses a correct twin is
    # worse than one that says nothing.
    prefix = ""
    suffix = ""
    if isinstance(column.facts, contract.AffixedFacts):
        prefix = column.facts.affix_prefix
        suffix = column.facts.affix_suffix
    counted: dict[int, int] = {}
    for cell in _present_of(written, _hole_spellings(column)):
        # A cell the column's own description reads as absent
        # is not a present cell (review round 3 finding 4).
        trimmed = parsing.trimmed(cell)
        body = trimmed
        if prefix or suffix:
            if not trimmed.startswith(prefix):
                continue
            if not trimmed.endswith(suffix):
                continue
            body = trimmed[len(prefix) : len(trimmed) - len(suffix)]
            if not body:
                continue
        if parsing.classify_number(body) != parsing.NUMBER:
            continue
        if parsing.numeric_style(body) != parsing.STYLE_DECIMAL:
            continue
        width = parsing.fraction_width(body)
        if width in counted:
            counted[width] = counted[width] + 1
            continue
        counted[width] = 1
    sense = (
        "The description says how many of this column's cells wrote "
        "each number of figures after the decimal point, and the twin "
        "wrote a different number of them that way. The values are "
        "within the bounds the description sets; what changes is the "
        "PRECISION each cell appears to carry, so a reader of the twin "
        "sees a column written more raggedly -- or more evenly -- than "
        "the real one."
    )
    notes: list[Deviation] = []
    for width in sorted(published):
        found = counted[width] if width in counted else 0
        if published[width] <= found <= published[width] + pooled:
            continue
        notes = notes + [
            _deviation(
                column.name,
                "fraction_widths",
                f"{published[width]} cell(s) written with {width} "
                f"figure(s) after the point",
                f"{found}",
                sense,
            )
        ]
    return notes


def _pad_notes(
    column: contract.ColumnBlock, written: "list[str]"
) -> "list[Deviation]":
    """Name a published field width the padded cells did not reach.

    The census is EXACT-OBSERVABLE for the reason the fraction census
    is: a person opens the twin, counts the figures each padded cell
    writes, and gets the published census back. Where the twin cannot
    pay -- because no remaining width holds a whole value's cells, or
    because the value needs more figures than the width holds -- it
    owes the reader a sentence rather than a silence.

    THIS IS A RECOUNT, taken off the finished text with the same reader
    the census itself used, so a width the writer intended and a width
    the cell actually wears cannot come apart here.
    """
    facts = _quantitative_facts(column)
    if facts is None:
        return []
    published: dict[int, int] = {}
    for key in sorted(facts.pad_widths):
        if key == contract.WITHHELD:
            continue
        published[int(key)] = facts.pad_widths[key]
    if not published:
        return []
    pooled = 0
    if contract.WITHHELD in facts.pad_widths:
        pooled = facts.pad_widths[contract.WITHHELD]
    # THE RECOUNT IS OVER THE CORES ON THE AFFIXED ROLE, for the reason
    # `_fraction_notes` gives: reading a padded core still wearing its
    # prefix as a bare number finds no number at all, and a report that
    # accuses a correct twin is worse than one that says nothing.
    prefix = ""
    suffix = ""
    if isinstance(column.facts, contract.AffixedFacts):
        prefix = column.facts.affix_prefix
        suffix = column.facts.affix_suffix
    counted: dict[int, int] = {}
    for cell in _present_of(written, _hole_spellings(column)):
        # A cell the column's own description reads as absent
        # is not a present cell (review round 3 finding 4).
        trimmed = parsing.trimmed(cell)
        body = trimmed
        if prefix or suffix:
            if not trimmed.startswith(prefix):
                continue
            if not trimmed.endswith(suffix):
                continue
            body = trimmed[len(prefix) : len(trimmed) - len(suffix)]
            if not body:
                continue
        if parsing.classify_number(body) != parsing.NUMBER:
            continue
        if parsing.numeric_style(body) != parsing.STYLE_LEADING_ZERO:
            continue
        width = parsing.pad_width(body)
        if width in counted:
            counted[width] = counted[width] + 1
            continue
        counted[width] = 1
    sense = (
        "The description says how many of this column's cells wrote "
        "each field width with a leading zero, and the twin wrote a "
        "different number of them that way. The values are within the "
        "bounds the description sets; what changes is the WIDTH each "
        "cell appears to carry, so code developed against the twin "
        "that checks a length, slices a fixed-width code, or joins on "
        "one can behave differently on the real table."
    )
    notes: list[Deviation] = []
    for width in sorted(published):
        found = counted[width] if width in counted else 0
        if published[width] <= found <= published[width] + pooled:
            continue
        notes = notes + [
            _deviation(
                column.name,
                "pad_widths",
                f"{published[width]} cell(s) written {width} "
                f"figure(s) wide with a leading zero",
                f"{found}",
                sense,
            )
        ]
    return notes


def _form_notes(
    column: contract.ColumnBlock, written: "list[str]"
) -> "list[Deviation]":
    """Name a published written form the twin's cells did not reach.

    THE TWIN'S OWN REPORT OWED THIS AND DID NOT PAY IT (review round 1
    finding 10). The census is EXACT-OBSERVABLE, and every other
    EXACT-OBSERVABLE census this module writes is recounted off the
    finished cells here and named where it was missed -- the styles,
    both width censuses, the classes, the alphabets. The form census
    was checked only by `synthtwin validate`, run later and by
    somebody who might not run it, so a twin that could not reach a
    form said nothing about it in the file written beside it.

    IT IS REACHABLE and not a theoretical shortfall. A form every
    spelling of which opens with the character a spreadsheet reads as
    the start of a formula is refused cell by cell and the walk gives
    the form up; a form whose length no group could take is never
    offered; and the sizes a column's suppressed levels come in need
    not divide its debts evenly.

    THIS IS A RECOUNT, taken off the finished text with the same reader
    the census itself used.
    """
    facts = column.facts
    census: "dict[str, int]" = {}
    if isinstance(facts, contract.LabelFacts):
        census = facts.shape_forms
    elif isinstance(facts, contract.TextFacts):
        census = facts.shape_forms
    if not census:
        return []
    pooled = 0
    if contract.WITHHELD in census:
        pooled = census[contract.WITHHELD]
    # THE COLUMN'S OWN ABSENT CELLS ARE NOT PRESENT CELLS, and this
    # counted them (review round 2 finding 11). A twin reproduces the
    # spellings its source's absent cells wore (7.7), so a column whose
    # holes were written `N/A` has eleven twin cells wearing the form
    # `@/@` -- and the census counts PRESENT cells. The note therefore
    # accused a twin the validator, which excludes them correctly, had
    # just called conforming.
    holes = _hole_spellings(column)
    counted: "dict[str, int]" = {}
    for cell in written:
        if cell == "":
            continue
        if _wears_a_published_hole(cell, holes):
            # THE RECOUNTING HALF, not the conservative one. The
            # question here is whether THIS COLUMN'S DESCRIPTION reads
            # the cell as absent, and raw membership answered a
            # narrower question -- so a hole the twin wrote in another
            # case was counted as a present cell and a conforming twin
            # was accused (review round 2 finding 11).
            continue
        form = parsing.shape_form(cell)
        if not form:
            continue
        if form in counted:
            counted[form] = counted[form] + 1
            continue
        counted[form] = 1
    sense = (
        "The description says how many of this column's cells were "
        "written in each SHAPE -- every figure of a cell read as `%`, "
        "every letter as `@`, the marks between them standing -- and "
        "the twin wrote a different number of them that way. Code "
        "developed against the twin that splits a value on a mark, "
        "checks the width of a part, or matches a pattern can behave "
        "differently on the real table."
    )
    notes: "list[Deviation]" = []
    for form in sorted(census):
        if form == contract.WITHHELD:
            continue
        found = counted[form] if form in counted else 0
        if census[form] <= found <= census[form] + pooled:
            continue
        notes = notes + [
            _deviation(
                column.name,
                "shape_forms",
                f"{census[form]} cell(s) written in the shape {form}",
                f"{found}",
                sense,
            )
        ]
    return notes


def _width_notes(
    column: contract.ColumnBlock, written: "list[str]"
) -> "list[Deviation]":
    """Name a published width a column of record numbers did not reach.

    `min_length` and `max_length` are EXACT-OBSERVABLE in every case for
    a declared identifier -- owner decision 6 keeps the length, which is
    the whole of what that decision buys -- so a person measures both on
    the twin and finds the published numbers. NOTHING WAS MEASURING
    THEM (review item P2-C5-F2). The free-text path recounts its four
    ends and this one recounted none, so a construction whose own shape
    is wider than the published range -- a whole number too large to
    hold needs three hundred and ten figures however short the column is
    -- could write it and say nothing at all. The family is now barred
    from a declared column instead, and this is the check that would
    have caught it: a run that believes a fact is exactly the run that
    stops checking it.
    """
    facts = column.facts
    if not isinstance(facts, contract.IdentifierFacts):
        return []
    present = _present_of(written, _hole_spellings(column))
    if not present:
        return []
    lengths = [len(cell) for cell in present]
    reasons = {
        "min_length": "The twin's shortest record number is not as wide as "
        "the description records, so fixed-width parsing or a width check "
        "developed against the twin can behave differently on the real "
        "table.",
        "max_length": "The twin's widest record number is not as wide as "
        "the description records, so fixed-width parsing, a column width "
        "or a length check developed against the twin can behave "
        "differently on the real table.",
    }
    return _named_miss(
        column, "min_length", facts.min_length, min(lengths),
        reasons["min_length"],
    ) + _named_miss(
        column, "max_length", facts.max_length, max(lengths),
        reasons["max_length"],
    )


def _class_notes(
    column: contract.ColumnBlock, written: "list[str]"
) -> "list[Deviation]":
    """Name any of the four class counts the written column did not reach.

    THE FOUR CLASSES ARE EXACT-OBSERVABLE ON EVERY ROLE (method G10.2,
    plan P2-D6): every present cell of a twin reads back through the
    shipped classifier as a number, a number too large or too small to
    hold, notation that conflicts with itself, or ordinary text, and the
    description publishes all four counts for every column. So this
    measures all four on the cells this run actually wrote and names
    every one that moved.

    It is a RECOUNT, not a restatement. That is what lets it catch a
    shortfall no rule of this module predicted -- one made-up value
    covers a whole group of rows, so a count that falls part-way inside
    a group can be missed by a packing, and a packing that missed it in
    silence is the defect this closes (review item P2-C1-F1).
    """
    present = _present_of(written, _hole_spellings(column))
    counted = {name: 0 for name in _CLASSES}
    for cell in present:
        found = parsing.classify_number(cell)
        counted[found] = counted[found] + 1
    reason = (
        "Every made-up value covers a whole group of rows, so a count "
        "that falls part-way inside a group cannot always be met "
        "exactly. A check that sorts cells into numbers and text can "
        "therefore see a different number of each here than on the real "
        "table."
    )
    return (
        _named_miss(
            column, "n_numeric", column.n_numeric,
            counted[_CLASS_NUMBER], reason,
        )
        + _named_miss(
            column, "n_out_of_range", column.n_out_of_range,
            counted[_CLASS_OUT_OF_RANGE], reason,
        )
        + _named_miss(
            column, "n_contradictory", column.n_contradictory,
            counted[_CLASS_CONTRADICTORY], reason,
        )
        + _named_miss(
            column, "n_not_numeric", column.n_not_numeric,
            counted[_CLASS_TEXT], reason,
        )
    )


def _whole_notes(
    column: contract.ColumnBlock, written: "list[str]"
) -> "list[Deviation]":
    """Name the whole-number fact a column of record numbers did not reach.

    `all_whole_numbers` is EXACT-OBSERVABLE, so a person can read the
    twin and find the same answer. Where the published alphabet counts
    put a value outside the figures and no spelling of the published
    length is both a whole number and outside them, the twin cannot hold
    both facts, and this is where that is said rather than left for a
    reader to discover (review item P2-C1-F1).
    """
    facts = column.facts
    if not isinstance(facts, contract.IdentifierFacts):
        return []
    present = [
        parsing.trimmed(cell)
        for cell in _present_of(written, _hole_spellings(column))
    ]
    whole = len(present) > 0
    for cell in present:
        if parsing.numeric_whole(cell) != parsing.WHOLE_YES:
            whole = False
    if whole == facts.all_whole_numbers:
        return []
    published = "every value is a whole number"
    achieved = "at least one value is not a whole number"
    if whole:
        published = "not every value is a whole number"
        achieved = "every value the twin holds is a whole number"
    return [
        _deviation(
            column.name,
            "all_whole_numbers",
            published,
            achieved,
            "The two counts of how these record numbers are written and "
            "the fact that they are whole numbers cannot both hold at "
            "the width the description publishes, so a check that reads "
            "them as numbers can behave differently here than on the "
            "real table.",
        )
    ]


def _mix_notes(
    column: contract.ColumnBlock, written: "list[str]"
) -> "list[Deviation]":
    """Name the form census a column read under the joint ISO reading loses.

    `resolution_mix` is REPORT-ONLY and the plan says why: the twin
    writes every parsed cell of such a column at the column's finest
    recorded precision, exactly as the ratified rule writes every
    column of dates today, because a cell spelled as a whole date
    cannot carry an interior value of a column published at the
    second. So the census is recorded and not reproduced -- and this is
    where the report says so, per column, every run (plan P4-D4.3).

    IT IS RECOUNTED RATHER THAN PREDICTED, like every other count in
    this part of the report. The rule above says the twin writes no
    whole dates at all, and a run that finds otherwise has found a
    defect in itself; recounting is what lets the line say which it
    was.

    Only the joint reading reaches here. On a column read under one
    format the census restates that format's own name beside the parsed
    total, and the report already discloses the format as recorded
    rather than reproduced, so a second line would name the same loss
    twice.
    """
    facts = column.facts
    if not isinstance(facts, contract.DatetimeFacts):
        return []
    if facts.parser_family != contract.FORMAT_ISO_MIXED:
        return []
    counted = {"iso-date": 0, "iso-datetime": 0}
    holes = _hole_spellings(column)
    for cell in written:
        if cell == "":
            continue
        # AND A CELL THE COLUMN'S OWN DECLARATION READS AS ABSENT IS
        # NOT A DATE OF ANY FORM (review item P4-DATE-F2). Counting it
        # would make this line say the twin wrote a value where its own
        # description finds none.
        if _wears_a_published_hole(cell, holes):
            continue
        if parsing.parse_datetime(cell, "iso-datetime") is not None:
            counted["iso-datetime"] = counted["iso-datetime"] + 1
            continue
        if parsing.parse_datetime(cell, "iso-date") is not None:
            counted["iso-date"] = counted["iso-date"] + 1
    # THE TWO KEYS ARE THE LOADER'S OWN GUARANTEE. RM1 refuses a joint
    # reading whose census names any other pair, so both are read
    # straight rather than asked for with a stand-in value that would
    # quietly answer zero if the pair ever changed.
    published = facts.resolution_mix
    whole_dates = published["iso-date"]
    with_a_time = published["iso-datetime"]
    if counted["iso-date"] == whole_dates:
        if counted["iso-datetime"] == with_a_time:
            return []
    return [
        _deviation(
            column.name,
            "resolution_mix",
            f"{whole_dates} of these dates were written "
            f"as a whole date and "
            f"{with_a_time} carried a time of day",
            f"{counted['iso-date']} of the twin's are written as a whole "
            f"date and {counted['iso-datetime']} carry a time of day",
            "The real column mixed the two ways of writing a date and "
            "the twin writes them all the same way, at the finer of the "
            "two, so code that reads these cells as text -- taking the "
            "first ten characters, or testing how long a cell is -- can "
            "behave differently here than on the real table. Code that "
            "reads them as dates is unaffected: every cell of the twin "
            "reads back as the same moment it would on the real table's "
            "own terms, with a cell that carried no time of day placed "
            "at midnight.",
        )
    ]


def _style_notes(
    column: contract.ColumnBlock, written: "list[str]"
) -> "list[Deviation]":
    """Name every spelling form the written column did not reach.

    `numeric_styles` is EXACT-OBSERVABLE (contract 9.4): a person can
    open the twin, read each numeric cell's form off the contract's own
    first-match ladder, and get the published map back. So the twin owes
    that map, and where it cannot pay, it owes the reader a sentence.

    THIS IS A RECOUNT, not a restatement of what the writer intended. A
    style is not a label kept beside a cell -- it is what the finished
    TEXT classifies as (method G6.4) -- and the two come apart on a
    column publishing `integer_valued: false`, where the canonical
    spelling of a value that is not whole already carries a decimal
    point: a cell the writer counted as `plain` reads back as `decimal`,
    and inserting zeros or a plus in front of it does not move the
    point. The method fixes both halves of that case and says neither
    may pass unnoticed; only the placement half was built, so a column
    in that corner missed its published map in silence. This is the
    half that speaks.

    EVERY NAMED COUNT IS EXACT, AND THE POOL IS SPELLED BY ITS OWN
    VALUES (Phase 3 plan P3-D8.1). The held-back remainder used to be
    compared as part of `plain`, which contract 7.5.7 fixed as the form
    of every pooled cell. That rule and a published end carrying a
    decimal point cannot both be met -- such an end has no point-free
    spelling at all -- so the remainder came out short by that cell on
    a shape a real table produces. The amended rule spells a pooled
    cell by its own value: point-free where the value has such a
    spelling, and the value's canonical text where it has none. What
    the recount owes is therefore an identity rather than six
    equalities, and each of its clauses is checked here separately so a
    miss names the clause it broke:

    - `leading_zero`, `leading_plus` and `exponent_upper` are exact
      against their published counts. The pool never reaches them: the
      first two are the invention family, and canonical text never
      carries an upper-case exponent.
    - `plain`, `decimal` and `exponent_lower` are never BELOW their
      published counts, so a published form can never be substituted
      away.
    - the two canonical point-carrying forms carry, between them,
      exactly the cells whose values have no point-free spelling and
      whose forms the published counts do not already name.
    - and `plain` carries the rest of the pool exactly.

    WHERE THE POOL IS PART OF A FIGURE, THE SENTENCE SAYS SO (review
    item P2-C4-F3): a description publishing forty `plain` cells and
    holding six back is owed forty and may be written up to forty-six,
    and a reader who went looking for either number in the description
    alone would not find it, so the note names both.
    """
    # THE AFFIXED ROLE IS READ OVER ITS CORES HERE TOO. Its
    # quantitative block IS the numeric block (P4-D4.1), styles map
    # included, so a styles obligation it could not meet is owed the
    # same sentence a plain numeric column gets. Returning empty for
    # `AffixedFacts` meant an unmet EXACT count was reported on one
    # role and silent on the other, with the same facts underneath.
    facts = _quantitative_facts(column)
    if facts is None:
        return []
    prefix = ""
    suffix = ""
    if isinstance(column.facts, contract.AffixedFacts):
        prefix = column.facts.affix_prefix
        suffix = column.facts.affix_suffix
    published = {name: 0 for name in contract.NUMERIC_STYLES}
    for name in sorted(facts.numeric_styles):
        if name != contract.WITHHELD:
            published[name] = facts.numeric_styles[name]
    pooled = _style_pool(facts.numeric_styles)
    counted = {name: 0 for name in contract.NUMERIC_STYLES}
    pointless = 0
    for cell in _present_of(written, _hole_spellings(column)):
        trimmed = parsing.trimmed(cell)
        body = trimmed
        if prefix or suffix:
            if not trimmed.startswith(prefix):
                continue
            if not trimmed.endswith(suffix):
                continue
            body = trimmed[len(prefix) : len(trimmed) - len(suffix)]
            if not body:
                continue
        cell = body
        if parsing.classify_number(cell) != parsing.NUMBER:
            continue
        counted[parsing.numeric_style(cell)] = (
            counted[parsing.numeric_style(cell)] + 1
        )
        # THE SPILL IS READ OFF THE VALUES, NEVER OFF THE SPELLINGS
        # (review item P3-C1-F2). Counting the cells that were WRITTEN
        # with a point makes the identity circular: a twin that spells a
        # whole value `1000000000000000.0` instead of plainly inflates
        # its own spill by one and the arithmetic then balances against
        # itself, so a re-spelled column passes a check meant to catch
        # exactly that. What the plan fixes is the count of cells whose
        # VALUE has no point-free spelling, which is a property of the
        # number the cell reads back as and not of how it was written --
        # and it is therefore a quantity the writer cannot move.
        held = parsing.parse_number(parsing.trimmed(cell))
        if held is None:
            continue
        if not _carries_plainly(held, facts.integer_valued):
            pointless = pointless + 1
    canonical_room = (
        published["decimal"]
        + published["exponent_lower"]
        + published["exponent_upper"]
    )
    # How many pooled cells have no point-free spelling of their own,
    # and so are written in their values' canonical text rather than
    # plainly. The published point-carrying counts are spent on such
    # cells first, so this is what is left over -- and it is a function
    # of the finished cells and the published map alone, which is what
    # lets a reader recompute it.
    spilled = max(0, pointless - canonical_room)
    owing = {name: published[name] for name in contract.NUMERIC_STYLES}
    owing["plain"] = published["plain"] + pooled - spilled
    sense = (
        "The description says how many of this column's cells were "
        "written in each form -- with a decimal point, with leading "
        "zeros, plainly, and so on -- and the twin wrote a different "
        "number of them that way. The values are unaffected; what "
        "changes is how they LOOK, so a program that decides a "
        "column's type by reading its cells, or that matches them "
        "against a pattern, can behave differently here than on the "
        "real table."
    )
    notes: list[Deviation] = []
    for name in contract.NUMERIC_STYLES:
        if name in ("decimal", "exponent_lower"):
            # These two carry the spill between them; which of the two
            # a cell lands in is its own value's canonical text, so
            # they are owed a floor each and a total together.
            if counted[name] >= published[name]:
                continue
            notes = notes + [
                _deviation(
                    column.name,
                    "numeric_styles",
                    f"at least {published[name]} cell(s) written in the "
                    f"{name} form",
                    f"{counted[name]}",
                    sense,
                )
            ]
            continue
        if name == "plain" and counted[name] < published[name]:
            # THE FLOOR, AND WHY IT IS CHECKED BEFORE THE TOTAL. The
            # spill is read off the finished cells, so a column that
            # wrote every cell with a point would compute a spill as
            # large as the plain quota and balance the total against
            # itself. A published form is never substituted away: the
            # count named in the description is a floor under the
            # recount, whatever the pool does above it.
            notes = notes + [
                _deviation(
                    column.name,
                    "numeric_styles",
                    f"at least {published[name]} cell(s) written in the "
                    "plain form",
                    f"{counted[name]}",
                    sense,
                )
            ]
            continue
        if counted[name] == owing[name]:
            continue
        owed = f"{owing[name]} cell(s) written in the {name} form"
        if name == "plain" and pooled > 0:
            owed = (
                f"{owing[name]} cell(s) written in the plain form -- "
                f"{published[name]} the description names, and "
                f"{pooled - spilled} of the {pooled} it held back "
                "below the smallest group size, which are written "
                "plainly because that form changes nothing a reader "
                "infers"
            )
        notes = notes + [
            _deviation(
                column.name, "numeric_styles", owed, f"{counted[name]}", sense
            )
        ]
    # NO CELL IS SPELLED NON-CANONICALLY WITHOUT A PUBLISHED COUNT
    # ENTITLING IT (review item P3-C1-F1). The published counts are the
    # only licence for a point-carrying spelling that is not the value's
    # own canonical text, so a pooled cell must carry exactly that text
    # and a pool cannot be re-spelled into a form the description never
    # named. Without this clause the totals alone would let a column
    # trade one canonical form for the other.
    for name in ("decimal", "exponent_lower"):
        odd = 0
        for cell in _present_of(written, _hole_spellings(column)):
            # THE SECONDARY LOOP OWES THE SAME RULE AS THE MAIN ONE
            # (review round 3 finding 4). One reproduced hole spelled
            # `1.00` counted as a non-canonical decimal on a column
            # publishing none.
            if parsing.numeric_style(cell) != name:
                continue
            if parsing.classify_number(cell) != parsing.NUMBER:
                continue
            held = parsing.parse_number(parsing.trimmed(cell))
            if held is None:
                continue
            if cell != _canonical_number(held, facts.integer_valued):
                odd = odd + 1
        if odd > published[name]:
            notes = notes + [
                _deviation(
                    column.name,
                    "numeric_styles",
                    f"at most {published[name]} cell(s) written in the "
                    f"{name} form in any way but their own value's "
                    "canonical spelling",
                    f"{odd}",
                    sense,
                )
            ]
    carried = counted["decimal"] + counted["exponent_lower"]
    owed_together = published["decimal"] + published["exponent_lower"] + spilled
    if carried != owed_together:
        notes = notes + [
            _deviation(
                column.name,
                "numeric_styles",
                f"{owed_together} cell(s) written with a decimal point or "
                "a lower-case exponent between them",
                f"{carried}",
                sense,
            )
        ]
    return notes


def _magnitude_notes(
    column: contract.ColumnBlock, written: "list[str]"
) -> "list[Deviation]":
    """Name every sign or whole/fraction count a wide column did not reach.

    All six are EXACT-OBSERVABLE for a column of numbers too large or
    too small to hold, and all six are measured HERE from the finished
    cells, by the same three questions the profiler asks of a real cell:
    what the notation classifies as, what sign it settles, and whether
    it is a whole number. A count the packing could not reach is named
    under the description's own key -- `n_whole`, `n_negative` -- and
    never left silent (review item P2-C1-F1).
    """
    facts = column.facts
    if not isinstance(facts, contract.UnrepresentableFacts):
        return []
    whole = 0
    fraction = 0
    whole_unknown = 0
    negative = 0
    positive = 0
    sign_unknown = 0
    for cell in _present_of(written, _hole_spellings(column)):
        # A cell the column's own description reads as absent is not a
        # present cell (review round 3 finding 4) -- but a cell that
        # is not a NUMBER still is, and this used to skip those
        # (review round 4 finding 6).
        #
        # This role tolerates a slack of ordinary-text stragglers, and
        # they are exactly what `n_whole_unknown` and `n_sign_unknown`
        # count: a word settles no sign and settles no whole-number
        # status, which is what the readers say of it. Skipping them
        # recounted both as zero on a column publishing two, and
        # accused a twin that had written them correctly. They fall
        # into the two `unknown` arms below on their own; nothing else
        # here has to know they are words.
        sign = parsing.numeric_sign(cell)
        if sign == parsing.SIGN_NEGATIVE:
            negative = negative + 1
        elif sign == parsing.SIGN_POSITIVE or sign == parsing.SIGN_ZERO:
            positive = positive + 1
        else:
            sign_unknown = sign_unknown + 1
        settled = parsing.numeric_whole(cell)
        if settled == parsing.WHOLE_YES:
            whole = whole + 1
        elif settled == parsing.WHOLE_NO:
            fraction = fraction + 1
        else:
            whole_unknown = whole_unknown + 1
    reason = (
        "Every made-up value covers a whole group of rows, so a count "
        "that falls part-way inside a group cannot always be met "
        "exactly, and this one was missed by the number shown."
    )
    return (
        _named_miss(column, "n_whole", facts.n_whole, whole, reason)
        + _named_miss(
            column, "n_fraction", facts.n_fraction, fraction, reason
        )
        + _named_miss(
            column, "n_whole_unknown", facts.n_whole_unknown,
            whole_unknown, reason,
        )
        + _named_miss(
            column, "n_negative", facts.n_negative, negative, reason
        )
        + _named_miss(
            column, "n_positive", facts.n_positive, positive, reason
        )
        + _named_miss(
            column, "n_sign_unknown", facts.n_sign_unknown,
            sign_unknown, reason,
        )
    )


# -- how close an approximated fact came (contract 2.2, method G12) -----
#
# WHAT THIS SECTION IS ANSWERABLE FOR. The contract gives every
# published field exactly one disposition, and one of the six is
# APPROXIMATED: a fact the twin reproduces "under a stated rule inside a
# two-sided finite-sample bound", measured on the written cells and
# named in the report with the achieved value beside the published one.
# Method G12.1 to G12.8 state the rule and both ends of the bound for
# them; the functions below are that text carried out. The complete
# list, by role, so that a reader can check this section against the
# contract's own matrix rather than against a summary of it:
#
#   count, continuous -- the nine INTERIOR rungs of `percentiles`,
#     `mean`, `std` and `skew`, and `n_distinct` and
#     `n_distinct_folded` in the fallback method G12.8 fixes;
#   datetime -- the nine interior rungs of `date_percentiles`, and
#     `n_distinct` and `n_distinct_folded`;
#   free_text -- `length.mean`, `length.p50` and `words.mean`;
#   constant, binary, categorical -- `n_distinct`, which is exact
#     wherever the description's own spellings supply it and
#     approximated where they do not.
#
# Nothing else is approximated. The two ends of every ladder, every
# class and sign count, every alphabet count and both distinctness
# counts of the invention roles are EXACT-OBSERVABLE and are recounted
# elsewhere in this file; a fact that is measured in both places would
# be a fact with two dispositions. The two numeric cardinalities sit in
# the list above rather than beside them because the contract gives
# them ONE disposition with a named fallback, and a fallback whose
# range is never printed is a fallback a reader cannot check.
# be a fact with two dispositions.
#
# EVERY BOUND HERE IS A STATEMENT ABOUT THE CONSTRUCTION, never a
# tolerance somebody measured on an output and rounded up. Each one is
# derived in method G12 from the rule that builds the cells, so a
# generator that ignored the published ladder, collapsed the interior
# rungs, or wrote values at the wrong precision leaves it. That is what
# makes the check able to fail, which is what makes a passing report
# worth reading.
#
# AND EVERY NUMBER HERE IS THE SAME ON EVERY MACHINE. The counts, the
# ranks and the shares are whole-number arithmetic; the rest is ordinary
# binary64 addition, subtraction, multiplication, division and square
# root, in one fixed order, every one of which this format requires to
# be correctly rounded. So the report's bytes are a fixed function of
# the description and the seed (plan D12) and can be pinned by a digest
# on every cell of the matrix.


def _size(value: float) -> float:
    """The size of ``value`` regardless of its sign."""
    return -value if value < 0 else value


def _summed(values: "list[float]") -> float:
    """The sum of ``values`` in list order, with the lost part carried.

    Ordinary addition loses the low bits of the smaller operand every
    time two numbers of different sizes meet. The lost part is worked
    out exactly by one subtraction -- the two cases below are which of
    the pair is the larger -- and carried to the end, so the total is
    the correctly rounded sum for every ordinary column and is a fixed
    function of the list order either way. Two implementations that add
    the same list in the same order get the same answer on every
    machine, which is what the report's bytes need.
    """
    total = 0.0
    lost = 0.0
    for value in values:
        step = total + value
        if _size(total) >= _size(value):
            lost = lost + ((total - step) + value)
        else:
            lost = lost + ((value - step) + total)
        total = step
    return total + lost


def _mean_of(values: "list[float]") -> float:
    """The arithmetic mean of a non-empty list, in list order."""
    return _summed(values) / len(values)


def _moments_of(
    values: "list[float]",
) -> "tuple[float, float | None, float | None]":
    """The three moments the description publishes, from the twin's cells.

    The FORMULAS are the profiler's, so that the two numbers the report
    puts side by side are the same statistic: the arithmetic mean; the
    SAMPLE standard deviation, divided by one less than the count; and
    the moment skewness, the average cubed deviation over the cube of
    the POPULATION standard deviation. The standard deviation is None
    for fewer than two values and the skewness is None for fewer than
    three or where every value is identical, exactly as the contract's
    Q4 and Q5 say the published fields are.

    The arithmetic is ordinary binary64 in a fixed order, with the sum's
    lost part carried; the deviations are scaled as they are summed, so
    a column whose spread the format can hold cannot overflow on the way
    to its own spread.
    """
    held = len(values)
    mean = _mean_of(values)
    if held < 2:
        return (mean, None, None)
    spread = _summed(
        [(value - mean) * (value - mean) / held for value in values]
    )
    if not math.isfinite(spread) or spread <= 0:
        return (mean, 0.0 if spread == 0 else None, None)
    deviation = math.sqrt(spread) * math.sqrt(held / (held - 1))
    if held < 3:
        return (mean, deviation, None)
    root = math.sqrt(spread)
    shape = _summed(
        [
            ((value - mean) / root)
            * ((value - mean) / root)
            * ((value - mean) / root)
            / held
            for value in values
        ]
    )
    return (mean, deviation, shape)


def _rung_of(ordered: "list[float]", percent: int) -> float:
    """One rung of the ladder recomputed from the twin's own values.

    The profiler's own rule (`taxonomy._quantile`): the position is
    worked out in whole numbers so that no binary spelling of a decimal
    fraction can move a rung onto the wrong pair of neighbours, and the
    two neighbours are combined in the convex form, which cannot
    overflow on a pair at opposite ends of the representable range.
    """
    held = len(ordered)
    if held == 1:
        return ordered[0]
    steps = (held - 1) * percent
    lower = steps // 100
    rest = steps - lower * 100
    if lower >= held - 1:
        return ordered[held - 1]
    if rest == 0:
        return ordered[lower]
    below = ordered[lower] * ((100 - rest) / 100)
    above = ordered[lower + 1] * (rest / 100)
    return below + above


def _figure(value: float) -> str:
    """One measured number written for the report, shortest round trip."""
    return f"{value}"


def _numeric_window(
    rungs: "tuple[float, ...]", held: int, widest: int, slack: float
) -> "tuple[list[float], list[float], list[float]]":
    """The window every RANK of a column of numbers sits in (method G12.2).

    Returns the lowest value, the highest value and the ladder's own
    value for each of the `held` ranks in order. The width is method
    G5.6's: the cell at rank `k` comes from the stratum covering that
    rank, whose share of the distribution is at most `widest / held`
    wide, and a recomputed rung interpolates one further rank, so the
    displacement in probability is at most `(widest + 2) / held` on
    either side. `slack` is the half unit the whole-number rule of G5.4
    can add on a column of whole numbers, and nothing else.

    The shares are formed as exact whole-number fractions and read
    through the same `_interpolated` the generator itself builds values
    with, so the window is the construction's own arithmetic rather than
    a second reading of it.
    """
    if held < 2:
        value = _interpolated(rungs, 0, 1)
        return ([value - slack], [value + slack], [value])
    denominator = held * (held - 1)
    span = (widest + 2) * (held - 1)
    lows: list[float] = []
    highs: list[float] = []
    middles: list[float] = []
    for rank in range(held):
        middle = rank * held
        lows = lows + [
            _interpolated(rungs, max(0, middle - span), denominator) - slack
        ]
        highs = highs + [
            _interpolated(
                rungs, min(denominator, middle + span), denominator
            )
            + slack
        ]
        middles = middles + [_interpolated(rungs, middle, denominator)]
    return (lows, highs, middles)


def _inside(value: float, lowest: float, highest: float) -> bool:
    """Whether a measured number landed between the two ends of its bound."""
    if not math.isfinite(value):
        return False
    return lowest <= value <= highest


def _at_a_named_width(cell: str, style: str, named: "dict[int, int]") -> bool:
    """Whether this padded cell wears a field width the census names.

    Read off the cell's own text, because this is a recount and a width
    the writer intended is not a width the cell wears.
    """
    if style != parsing.STYLE_LEADING_ZERO:
        return False
    return parsing.pad_width(cell) in named


def _numeric_supply(
    layout: "_NumericLayout",
    written: "list[str]",
    pad_widths: "dict[str, int]",
) -> "tuple[int, int]":
    """How many spellings and identities this column's own cells can hold.

    THE TWO ENDS OF THE FALLBACK ENVELOPE OF METHOD G12.8 (review item
    P2-C2-F4). Both distinctness counts of a column of numbers are
    exact where the permitted spellings can supply them, and fall back
    to a two-sided envelope where they cannot. What that envelope needs
    is a number the twin's own construction can be held to, and it is
    this one: how many DIFFERENT spellings the finished cells are
    capable of carrying.

    - Inside the numbers class, cells are grouped by the value they hold
      and the style they wear. A style with a leading-zero family --
      every style but `plain` -- can give each of its cells a different
      spelling and a different identity, so such a group supplies as
      many as it has cells. A `plain` group supplies exactly one,
      because a plain spelling of one value is unique; that is the whole
      shape of the corner G12.8 names, where the whole-number rule of
      G5.4 rounds two strata onto one value and no spelling rule brings
      the second back.
    - A PADDED CELL AT A NAMED FIELD WIDTH IS THE ONE EXCEPTION to the
      family rule above, and it is the exception method G12.8 states
      (plan P4-D14). Every order of the leading-zero family writes one
      more figure, so where `pad_widths` names a cell's width the
      family is spent: that value has exactly one padded spelling at
      that width, and such a group supplies ONE, like a plain group.
      Counting those cells one apiece put this report's bound above the
      validator's on the same twin -- two surfaces disagreeing about
      one method's formula, which is the defect a shared formula
      exists to prevent.
    - Each other class supplies what its own share of the budget allows,
      never more than its cell count.

    Returns the raw and the folded supply. Neither is a measurement of
    what was written: a twin that wrote one spelling where its own cells
    could have carried two leaves the bound, which is what makes the
    bound able to fail.
    """
    present = [cell for cell in written if cell != ""]
    named: dict[int, int] = {}
    for key in sorted(pad_widths):
        if key == contract.WITHHELD:
            continue
        named[int(key)] = pad_widths[key]
    counted = {name: 0 for name in _CLASSES}
    seen: dict[tuple[float, str, int], int] = {}
    raw_room = 0
    folded_room = 0
    for cell in present:
        found = parsing.classify_number(cell)
        counted[found] = counted[found] + 1
        if found != _CLASS_NUMBER:
            continue
        value = parsing.parse_number(cell)
        if value is None:
            continue
        style = parsing.numeric_style(cell)
        if style != "plain" and not _at_a_named_width(cell, style, named):
            raw_room = raw_room + 1
            folded_room = folded_room + 1
            continue
        # THE FIELD WIDTH IS PART OF THE KEY, not a detail below it. One
        # value at two named widths is TWO spellings -- `01` and `001`
        # are the same number and different identities -- so a group
        # keyed by value and style alone collapsed all three widths of
        # a column publishing three and reported a supply of one. The
        # validator meanwhile allowed one identity per named width, so
        # the twin's own report and the check disagreed about the same
        # twin, which is the failure a shared formula exists to stop.
        field = -1
        if style == parsing.STYLE_LEADING_ZERO:
            field = parsing.pad_width(cell)
        if (value, style, field) not in seen:
            seen[(value, style, field)] = 1
            raw_room = raw_room + 1
            folded_room = folded_room + 1
    for place in range(1, len(_CLASSES)):
        cells = counted[_CLASSES[place]]
        raw_room = raw_room + min(cells, layout.raw_budgets[place])
        folded_room = folded_room + min(cells, layout.folded_budgets[place])
    return raw_room, folded_room


def _numeric_cardinalities(
    column: contract.ColumnBlock,
    plan: "_ColumnPlan",
    written: "list[str]",
) -> "list[Approximation]":
    """Both distinctness counts of a column of numbers, bounded (G12.8).

    The contract sends these two to a two-sided envelope where the
    permitted spellings cannot supply the published count, and the
    method's own complete list of approximated facts names them. An
    earlier revision measured neither, so a reader of the report was
    told every approximation had been measured while two had not
    (review item P2-C2-F4). Both are measured here, every run, against
    the supply the twin's own cells carry: where that supply reaches the
    published count the two ends of the bound meet on it and the fact is
    exact, which is the ordinary case, and where it does not the printed
    range says how far the count could fall.
    """
    layout = plan.layout
    if layout is None:
        return []
    facts = _quantitative_facts(column)
    supply = _numeric_supply(
        layout, written, facts.pad_widths if facts is not None else {}
    )
    counted = _recounted(written, _hole_spellings(column))
    found: list[Approximation] = []
    for place, name, room, note in (
        (
            2, "n_distinct", supply[0],
            "how many different spellings this column holds",
        ),
        (
            3, "n_distinct_folded", supply[1],
            (
                "how many different values it holds, ignoring case and "
                "edge spacing"
            ),
        ),
    ):
        published = column.n_distinct if place == 2 else column.n_distinct_folded
        found = found + [
            Approximation(
                column=column.name,
                fact=name,
                published=f"{published}",
                achieved=f"{counted[place]}",
                lowest=f"{min(room, published)}",
                highest=f"{max(room, published)}",
                inside=(
                    min(room, published) <= counted[place] <= max(
                        room, published
                    )
                ),
                note=note,
                covers_published=True,
            )
        ]
    return found


def _numeric_approximations(
    column: contract.ColumnBlock,
    facts: contract.NumericFacts,
    plan: "_ColumnPlan",
    written: "list[str]",
) -> "list[Approximation]":
    """The four approximated families of a column of numbers (G12.2, G12.3).

    Measured from the cells this run wrote, read back through the
    shipped number reader -- so what is checked is the file a person
    opens, not the values this module held in memory on the way to it.

    THE ONE CASE THAT MEASURES NOTHING, stated rather than left to be
    discovered: a description whose ladder holds nothing at ANY of its
    eleven rungs publishes no shape for the values to take, method G5.3
    puts them on the sign counts alone, and there is then no ladder for
    a bound to be derived from. No moment is measured for such a column.
    It is not silent: `_numeric_content` names the empty ladder as a
    deviation on every run, so the report tells a reader that this
    column's values follow no published shape at all -- which is a
    larger fact than any bound would have been. A rung that is null
    while others hold numbers is filled by `_filled_rungs` and bounded
    like any other.
    """
    values = sorted(
        [
            value
            for value in [
                parsing.parse_number(cell)
                for cell in _present_of(written, _hole_spellings(column))
                if parsing.classify_number(cell) == parsing.NUMBER
            ]
            if value is not None
        ]
    )
    held = len(values)
    rungs = _filled_rungs(facts.percentiles.rungs)
    if held < 1 or rungs is None:
        return _numeric_cardinalities(column, plan, written)
    layout = plan.layout
    widest = held
    if layout is not None and layout.sizes:
        widest = max(layout.sizes)
    # THE HALF UNIT, AND THE TWO RULES THAT CAN SPEND IT. The
    # whole-number rule of G5.4 moves a value by at most half a unit on
    # a column publishing `integer_valued: true`. On a column publishing
    # a point-free style count, `_whole_enough` may move a stratum by
    # the same half unit so that the published form can be written at
    # all (review item P2-C2-F2), so the window owes the same half unit
    # there. It is granted only to columns publishing such a count: a
    # column publishing none keeps the tighter window it had.
    slack = 0.0
    if facts.integer_valued or _whole_demand(facts) > 0:
        slack = 0.5
    lows, highs, middles = _numeric_window(rungs, held, widest, slack)
    found: list[Approximation] = []
    for step in range(1, 10):
        percent = _PCT[step]
        rung = facts.percentiles.rungs[step]
        if rung is None:
            continue
        achieved = _rung_of(values, percent)
        lowest = _interpolated(
            rungs, max(0, percent * held - 100 * (widest + 2)), 100 * held
        ) - slack
        highest = _interpolated(
            rungs,
            min(100 * held, percent * held + 100 * (widest + 2)),
            100 * held,
        ) + slack
        found = found + [
            Approximation(
                column=column.name,
                fact=f"percentiles.p{percent:02d}",
                published=_figure(rung),
                achieved=_figure(achieved),
                lowest=_figure(lowest),
                highest=_figure(highest),
                inside=_inside(achieved, lowest, highest),
                note=(
                    "the value that stands "
                    f"{percent} percent of the way up this column"
                ),
                covers_published=_inside(rung, lowest, highest),
            )
        ]
    mean, deviation, shape = _moments_of(values)
    if facts.mean is not None:
        lowest = _mean_of(lows)
        highest = _mean_of(highs)
        found = found + [
            Approximation(
                column=column.name,
                fact="mean",
                published=_figure(facts.mean),
                achieved=_figure(mean),
                lowest=_figure(lowest),
                highest=_figure(highest),
                inside=_inside(mean, lowest, highest),
                note="this column's average",
                covers_published=_inside(facts.mean, lowest, highest),
            )
        ]
    # How far one rank's value can stand from the ladder's own value
    # there, measured over the whole column: the displacement bound the
    # standard deviation and the skewness are both derived from.
    steps = [
        max(middles[rank] - lows[rank], highs[rank] - middles[rank])
        for rank in range(held)
    ]
    reach = math.sqrt(_mean_of([step * step for step in steps]))
    centre = _moments_of(middles)
    if facts.std is not None and deviation is not None:
        room = reach * math.sqrt(held / (held - 1))
        middle = centre[1] if centre[1] is not None else 0.0
        lowest = max(0.0, middle - room)
        highest = middle + room
        found = found + [
            Approximation(
                column=column.name,
                fact="std",
                published=_figure(facts.std),
                achieved=_figure(deviation),
                lowest=_figure(lowest),
                highest=_figure(highest),
                inside=_inside(deviation, lowest, highest),
                note="how far this column's values spread out",
                covers_published=_inside(facts.std, lowest, highest),
            )
        ]
    if facts.skew is not None and shape is not None:
        lowest, highest = _shape_window(lows, highs, middles, reach, held)
        found = found + [
            Approximation(
                column=column.name,
                fact="skew",
                published=_figure(facts.skew),
                achieved=_figure(shape),
                lowest=_figure(lowest),
                highest=_figure(highest),
                inside=_inside(shape, lowest, highest),
                note="which side of this column's average is the longer tail",
                covers_published=_inside(facts.skew, lowest, highest),
            )
        ]
    return found + _numeric_cardinalities(column, plan, written)


def _shape_window(
    lows: "list[float]",
    highs: "list[float]",
    middles: "list[float]",
    reach: float,
    held: int,
) -> "tuple[float, float]":
    """The two ends of the skewness bound (method G12.3).

    The skewness is a ratio, so its bound is worked out from the bounds
    of the two parts. The average cubed deviation is bounded by cubing
    the ends of each rank's own window -- cubing keeps the order, so the
    ends stay the ends -- and the population spread is bounded by the
    same displacement `reach` that bounds the standard deviation. The
    ratio of the two intervals is then taken with the sign rules
    division needs.

    Every sample of `held` values has a skewness between
    `-(held - 2) / sqrt(held - 1)` and `+(held - 2) / sqrt(held - 1)`,
    whatever the values are, so the window is intersected with that: the
    bound is FINITE on both sides even where the spread's own lower end
    reaches zero, which is what the contract asks an approximated fact
    for.
    """
    ceiling = (held - 2) / math.sqrt(held - 1)
    floor_mean = _mean_of(lows)
    ceiling_mean = _mean_of(highs)
    low_cubes: list[float] = []
    high_cubes: list[float] = []
    for rank in range(held):
        below = lows[rank] - ceiling_mean
        above = highs[rank] - floor_mean
        low_cubes = low_cubes + [below * below * below / held]
        high_cubes = high_cubes + [above * above * above / held]
    lowest_shape = _summed(low_cubes)
    highest_shape = _summed(high_cubes)
    spread = _moments_of(middles)
    root = 0.0
    if spread[1] is not None and held >= 2:
        root = spread[1] * math.sqrt((held - 1) / held)
    low_root = max(0.0, root - reach)
    high_root = root + reach
    low_cube = low_root * low_root * low_root
    high_cube = high_root * high_root * high_root
    if low_cube <= 0 or not math.isfinite(high_cube):
        return (-ceiling, ceiling)
    lowest = lowest_shape / (low_cube if lowest_shape < 0 else high_cube)
    highest = highest_shape / (high_cube if highest_shape < 0 else low_cube)
    return (max(-ceiling, lowest), min(ceiling, highest))


def _written_ordinal(
    cell: str, facts: contract.DatetimeFacts
) -> "int | None":
    """The instant one written twin cell reads back as, or None.

    The cell is read with the SHIPPED date reader and put back on the
    clock the description says the published instants are written on, so
    what comes out is comparable with `earliest`, `latest` and every
    rung. None says the cell is not a date at all, which is what a
    counted stand-in for an unreadable cell is.
    """
    found = _instant_written(cell, facts)
    if found is None:
        return None
    if facts.resolution == "quarter" or facts.resolution == "month":
        if len(found) < 7:
            return None
        return _ordinal_of(found, facts.resolution)
    if len(found) < 10:
        return None
    if facts.resolution == "datetime" and len(found) < 19:
        return None
    return _ordinal_of(found, facts.resolution)


def _ordinal_at(
    ladder: "list[int]", numerator: int, denominator: int
) -> int:
    """The published date ladder read at one share (method G7.3).

    The same whole-number interpolation `_datetime_content` builds cells
    with, so the window below is the construction's own arithmetic.
    """
    step = _segment(numerator, denominator)
    above = 100 * numerator - _PCT[step] * denominator
    span = (_PCT[step + 1] - _PCT[step]) * denominator
    return ladder[step] + (
        above * (ladder[step + 1] - ladder[step])
    ) // span


def _precision_slack(facts: contract.DatetimeFacts) -> int:
    """How far writing at the published precision can move an instant.

    A cell written at minute precision carries no seconds, so reading it
    back gives an instant up to fifty-nine seconds BELOW the one the
    ladder asked for. A whole date, a quarter, a second and a subsecond
    cell each carry their own unit exactly and lose nothing.
    """
    if facts.resolution != "datetime":
        return 0
    if facts.time_precision == "minute":
        return 59
    return 0


def _datetime_window(
    ladder: "list[int]", facts: contract.DatetimeFacts, held: int
) -> "tuple[list[int], list[int]]":
    """The window every rank of a column of dates sits in (method G12.4).

    Rank `k` of method G7.3 is its own stratum: its share of the
    distribution is the band from `k / held` to `(k + 1) / held`, and no
    word can take it outside that band. The two ends of the ladder are
    PINNED, so the first and last ranks have no room at all. Reading the
    written cell back can lose part of a minute where the published
    precision is minutes, and the interpolation itself rounds downward,
    so the lower end carries both.
    """
    slack = _precision_slack(facts) + 1
    lows: list[int] = []
    highs: list[int] = []
    for rank in range(held):
        if rank == 0:
            lows = lows + [ladder[0]]
            highs = highs + [ladder[0]]
            continue
        if rank == held - 1 and held >= 2:
            lows = lows + [ladder[10]]
            highs = highs + [ladder[10]]
            continue
        lows = lows + [_ordinal_at(ladder, rank, held) - slack]
        highs = highs + [_ordinal_at(ladder, rank + 1, held)]
    return (lows, highs)


def _forced_apart(lows: "list[int]", highs: "list[int]") -> int:
    """How many different instants the published ladder FORCES.

    Two ranks whose windows do not overlap cannot hold the same instant,
    so the largest set of ranks with pairwise separate windows is a
    lower bound on the number of different values the twin holds. The
    windows arrive in non-decreasing order of both ends, so the count is
    taken in one walk: keep a window, then skip every later one that
    still touches it.
    """
    count = 0
    frontier = 0
    for rank in range(len(lows)):
        if count == 0 or lows[rank] > frontier:
            count = count + 1
            frontier = highs[rank]
    return count


def _spellings_of_a_date(facts: contract.DatetimeFacts) -> int:
    """How many ways one instant can be written in this column.

    One for a column that carries no offset at all; otherwise one per
    offset the description publishes by name, since a withheld offset is
    never written (method G7.4).
    """
    carried = 0
    for offset in facts.utc_offsets:
        if _is_real_offset(offset):
            carried = carried + 1
    return max(1, carried)


def _clock_approximations(
    column: contract.ColumnBlock,
    facts: contract.ClockFacts,
    written: "list[str]",
) -> "list[Approximation]":
    """The two approximated families of a column of clock times.

    The nine interior rungs against the window each rank was built in,
    and the two distinctness counts against the envelope amendment
    A-P4-20 fixes. Both are measured off the FINISHED cells and neither
    is restated from what this module intended.
    """
    present = _present_of(written, _hole_spellings(column))
    form = facts.clock_form
    ordinals = sorted(
        [
            found
            for found in [parsing.clock_ordinal(cell, form) for cell in present]
            if found is not None
        ]
    )
    held = len(ordinals)
    ladder = [
        _clock_ordinal_of(facts.clock_percentiles[name], form)
        for name in _LADDER_NAMES
    ]
    lows, highs = _clock_windows(ladder, held)
    found_facts: "list[Approximation]" = []
    rungs = 10 if held >= 1 else 1
    for step in range(1, rungs):
        percent = _PCT[step]
        place = min(held - 1, ((held - 1) * percent) // 100)
        achieved = ordinals[place]
        lowest = lows[place]
        highest = highs[place]
        found_facts = found_facts + [
            Approximation(
                column=column.name,
                fact=f"clock_percentiles.p{percent:02d}",
                published=facts.clock_percentiles[_LADDER_NAMES[step]],
                achieved=parsing.clock_spelling(achieved, form),
                lowest=parsing.clock_spelling(max(0, lowest), form),
                highest=parsing.clock_spelling(highest, form),
                inside=lowest <= achieved <= highest,
                note=(
                    "the time of day that stands "
                    f"{percent} percent of the way up this column"
                ),
                covers_published=lowest <= ladder[step] <= highest,
            )
        ]
    stand_ins = len(present) - held
    lowest_count = _forced_apart(lows, highs) + stand_ins
    reachable = ladder[10] - ladder[0] + 1
    highest_count = min(len(present), reachable + stand_ins)
    lowest_count = min(lowest_count, highest_count)
    counted = _recounted(written, _hole_spellings(column))
    for place, name in ((2, "n_distinct"), (3, "n_distinct_folded")):
        published = column.n_distinct
        if place == 3:
            published = column.n_distinct_folded
        found_facts = found_facts + [
            Approximation(
                column=column.name,
                fact=name,
                published=f"{published}",
                achieved=f"{counted[place]}",
                lowest=f"{lowest_count}",
                highest=f"{highest_count}",
                inside=lowest_count <= counted[place] <= highest_count,
                note=(
                    "how many different values this column holds"
                    if place == 2
                    else "how many different values it holds, ignoring "
                    "case and edge spacing"
                ),
                covers_published=lowest_count <= published <= highest_count,
            )
        ]
    return found_facts


def _clock_windows(
    ladder: "list[int]", held: int
) -> "tuple[list[int], list[int]]":
    """The window every rank of a clock column was built in.

    The two ends are PINNED and have no room at all; every rank between
    them was interpolated inside one segment of the ladder, so it sits
    between the ladder read at its own two shares, one unit lower at
    the bottom for the flooring.
    """
    lows: "list[int]" = []
    highs: "list[int]" = []
    for rank in range(held):
        if rank == 0:
            lows = lows + [ladder[0]]
            highs = highs + [ladder[0]]
            continue
        if rank == held - 1 and held >= 2:
            lows = lows + [ladder[10]]
            highs = highs + [ladder[10]]
            continue
        lows = lows + [_ladder_at(ladder, rank, held) - 1]
        highs = highs + [_ladder_at(ladder, rank + 1, held)]
    return (lows, highs)


def _ladder_at(ladder: "list[int]", numerator: int, denominator: int) -> int:
    """One ladder read at one share, by the construction's own walk."""
    step = _segment(numerator, denominator)
    above = 100 * numerator - _PCT[step] * denominator
    span = (_PCT[step + 1] - _PCT[step]) * denominator
    return ladder[step] + (above * (ladder[step + 1] - ladder[step])) // span


def _datetime_approximations(
    column: contract.ColumnBlock,
    facts: contract.DatetimeFacts,
    written: "list[str]",
) -> "list[Approximation]":
    """The two approximated families of a column of dates (G12.4, G12.5)."""
    present = _present_of(written, _hole_spellings(column))
    ordinals = sorted(
        [
            found
            for found in [
                _written_ordinal(cell, facts) for cell in present
            ]
            if found is not None
        ]
    )
    held = len(ordinals)
    ladder = [
        _ordinal_of(rung, facts.resolution)
        for rung in facts.date_percentiles.rungs
    ]
    lows, highs = _datetime_window(ladder, facts, held)
    found_facts: list[Approximation] = []
    # A column holding no readable date has no rung to measure, and the
    # loader's own D8 keeps at least one cell parsed, so this walk is
    # skipped only where the twin holds nothing a date reader accepts.
    # The two counts below are measured either way, because a column of
    # nothing but stand-ins still has a number of different spellings.
    rungs = 10 if held >= 1 else 1
    for step in range(1, rungs):
        percent = _PCT[step]
        place = min(held - 1, ((held - 1) * percent) // 100)
        achieved = ordinals[place]
        lowest = lows[place]
        highest = highs[place]
        found_facts = found_facts + [
            Approximation(
                column=column.name,
                fact=f"date_percentiles.p{percent:02d}",
                published=facts.date_percentiles.rungs[step],
                achieved=_cell_of_ordinal(
                    achieved,
                    facts.resolution,
                    facts.time_precision,
                    facts.subsecond_digits,
                ),
                lowest=_cell_of_ordinal(
                    lowest,
                    facts.resolution,
                    facts.time_precision,
                    facts.subsecond_digits,
                ),
                highest=_cell_of_ordinal(
                    highest,
                    facts.resolution,
                    facts.time_precision,
                    facts.subsecond_digits,
                ),
                inside=lowest <= achieved <= highest,
                note=(
                    "the date that stands "
                    f"{percent} percent of the way up this column"
                ),
                covers_published=(
                    lowest <= ladder[step] <= highest
                ),
            )
        ]
    # The number of different values, both ways of counting. A stand-in
    # for a cell that did not read as a date is a different spelling
    # from every other cell of the column, so both ends carry them.
    stand_ins = len(present) - held
    lowest_count = _forced_apart(lows, highs) + stand_ins
    reachable = ladder[10] - ladder[0] + 1
    unit = _precision_slack(facts) + 1
    reachable = (reachable + unit - 1) // unit
    highest_count = min(
        len(present),
        reachable * _spellings_of_a_date(facts) + stand_ins,
    )
    lowest_count = min(lowest_count, highest_count)
    counted = _recounted(written, _hole_spellings(column))
    for place, name in ((2, "n_distinct"), (3, "n_distinct_folded")):
        published = column.n_distinct
        if place == 3:
            published = column.n_distinct_folded
        found_facts = found_facts + [
            Approximation(
                column=column.name,
                fact=name,
                published=f"{published}",
                achieved=f"{counted[place]}",
                lowest=f"{lowest_count}",
                highest=f"{highest_count}",
                inside=lowest_count <= counted[place] <= highest_count,
                note=(
                    "how many different values this column holds"
                    if place == 2
                    else "how many different values it holds, ignoring "
                    "case and edge spacing"
                ),
                # G12.5's own docstring says this envelope need not
                # contain the published count and on an ordinary column
                # does not: it counts what the construction FORCES, and
                # a column of 240 rows over 84 dates publishes 84 while
                # the construction writes a value per rank.
                covers_published=(
                    lowest_count <= published <= highest_count
                ),
            )
        ]
    return found_facts


def _pinned_totals(
    groups: "tuple[int, ...]",
    smallest: int,
    largest: int,
    carriers: "tuple[int, int]",
) -> "tuple[int, int]":
    """The smallest and largest total the walk of G9.5 step 4 can build.

    One group takes the smallest value and one the largest -- the two
    the allocation settled on, which ``carriers`` names -- and that is
    what makes those two facts a recount can confirm; every other group
    is free between the two. So the total this column can reach at all
    lies between these two numbers, whatever the published average asks
    for.
    """
    fixed = 0
    free = 0
    for place in range(len(groups)):
        if place == carriers[0]:
            fixed = fixed + groups[place] * smallest
        elif len(groups) >= 2 and place == carriers[1]:
            fixed = fixed + groups[place] * largest
        else:
            free = free + groups[place]
    return (fixed + free * smallest, fixed + free * largest)


def _held_between(value: int, lowest: int, highest: int) -> int:
    """``value`` brought inside the two ends, which never cross."""
    return max(lowest, min(highest, value))


def _text_approximations(
    column: contract.ColumnBlock,
    facts: contract.TextFacts,
    written: "list[str]",
    carriers: "tuple[int, int]",
) -> "list[Approximation]":
    """The three approximated facts of a column of free text (G12.6).

    ``carriers`` is the pair of groups the allocation of G9.5 gave the
    published ends to. Every bound below is a statement about the walk
    that filled the groups AROUND those two, so it is measured against
    the pair the run actually used and never against an assumed one.
    """
    present = _present_of(written, _hole_spellings(column))
    rows = len(present)
    if rows < 1:
        return []
    groups = _groups_of(facts.n_distinct_by_occurrences)
    widest = 0
    for size in groups:
        widest = max(widest, size)
    lengths = sorted([len(cell) for cell in present])
    found: list[Approximation] = []
    if facts.length.mean is not None:
        wanted = _exact_product(facts.length.mean, rows)
        floor_total, ceiling_total = _pinned_totals(
            groups, facts.length.minimum, facts.length.maximum, carriers
        )
        lowest = _held_between(wanted - widest, floor_total, ceiling_total)
        highest = _held_between(wanted + widest, floor_total, ceiling_total)
        achieved = 0
        for length in lengths:
            achieved = achieved + length
        found = found + [
            Approximation(
                column=column.name,
                fact="length.mean",
                published=_figure(facts.length.mean),
                achieved=_figure(achieved / rows),
                lowest=_figure(lowest / rows),
                highest=_figure(highest / rows),
                inside=lowest <= achieved <= highest,
                note="how many characters a value holds on average",
                covers_published=lowest <= wanted <= highest,
            )
        ]
    # The middle length is measured whether or not an average was
    # published: with no average there is no walk, and the bound is the
    # published middle itself. Leaving it out on that corner would drop
    # a fact the matrix disposes.
    found = found + _median_length(
        column, facts, groups, lengths, rows, widest, carriers
    )
    if facts.words.mean is not None:
        found = found + _word_average(
            column, facts, present, groups, rows, widest, carriers
        )
    return found


def _median_length(
    column: contract.ColumnBlock,
    facts: contract.TextFacts,
    groups: "tuple[int, ...]",
    lengths: "list[int]",
    rows: int,
    widest: int,
    carriers: "tuple[int, int]",
) -> "list[Approximation]":
    """The middle length, and how far the average can drag it (G12.6).

    Every group that carries neither published end starts at the
    published middle length and is walked TOWARD the published average,
    one character at a time and in one direction only. So the middle
    length of the twin can move only that way, and only as far as the
    walk's own total movement allows: a value that moved by `step`
    characters cost `step` of that movement for every row it covers, so
    at most `movement / half the rows` characters of movement can reach
    the middle of the column. The two end-carrying groups are the
    exception -- a group covering half the column's rows holds the
    middle itself -- and each is allowed for by name.

    THIS BOUND IS THE WALK'S OWN REACH AND IS NOT WIDENED BY ANYTHING
    ELSE. Where no shape the walk prefers meets the published counts,
    method G9.5 lengthens a group so an exact count can be met -- an
    exact count outranks this approximated one -- and the middle length
    can then land outside these two ends. That is a fact the twin does
    not hold as promised, so the recount says so and the report names
    it, which is the whole point of measuring against a bound the
    construction can miss.
    """
    if facts.length.p50 is None:
        return []
    start = _held_between(
        int(_whole_valued(facts.length.p50)),
        facts.length.minimum,
        facts.length.maximum,
    )
    built = 0
    for place in range(len(groups)):
        value = start
        if place == carriers[0]:
            value = facts.length.minimum
        elif len(groups) >= 2 and place == carriers[1]:
            value = facts.length.maximum
        built = built + groups[place] * value
    wanted = built
    if facts.length.mean is not None:
        wanted = _exact_product(facts.length.mean, rows)
    movement = _size(float(wanted - built)) + widest
    half = max(1, rows // 2)
    room = int((movement + half - 1) // half)
    lowest = start
    highest = start
    if wanted < built:
        lowest = start - room
    if wanted > built:
        highest = start + room
    if len(groups) >= 1 and 2 * groups[carriers[0]] >= rows:
        lowest = facts.length.minimum
    if len(groups) >= 2 and 2 * groups[carriers[1]] >= rows:
        highest = facts.length.maximum
    lowest = _held_between(lowest, facts.length.minimum, facts.length.maximum)
    highest = _held_between(
        highest, facts.length.minimum, facts.length.maximum
    )
    achieved = _rung_of([float(length) for length in lengths], 50)
    return [
        Approximation(
            column=column.name,
            fact="length.p50",
            published=_figure(facts.length.p50),
            achieved=_figure(achieved),
            lowest=_figure(float(lowest)),
            highest=_figure(float(highest)),
            inside=_inside(achieved, float(lowest), float(highest)),
            note="the middle length: half the values are shorter",
            covers_published=_inside(
                facts.length.p50, float(lowest), float(highest)
            ),
        )
    ]


def _word_average(
    column: contract.ColumnBlock,
    facts: contract.TextFacts,
    present: "list[str]",
    groups: "tuple[int, ...]",
    rows: int,
    widest: int,
    carriers: "tuple[int, int]",
) -> "list[Approximation]":
    """The average word count, and what the written lengths allow (G12.6).

    A value of `L` characters holds at most `(L + 1) // 2` words,
    because every word needs a character and every gap between two words
    needs one too. Where the published average asks for more words than
    the lengths can hold, method G9.5 writes as many as fit and names
    the shortfall; the bound widens by exactly that allowance rather
    than pretending the shortfall did not happen.
    """
    if facts.words.mean is None:
        return []
    smallest = max(facts.words.minimum, 1)
    largest = max(facts.words.maximum, 1)
    wanted = _exact_product(facts.words.mean, rows)
    floor_total, ceiling_total = _pinned_totals(
        groups, smallest, largest, carriers
    )
    walk_low = _held_between(wanted - widest, floor_total, ceiling_total)
    walk_high = _held_between(wanted + widest, floor_total, ceiling_total)
    room_low = 0
    room_high = 0
    allowance = 0
    achieved = 0
    for cell in present:
        ceiling = max(1, (len(cell) + 1) // 2)
        room_low = room_low + max(1, min(smallest, ceiling))
        room_high = room_high + max(1, min(largest, ceiling))
        allowance = allowance + max(0, largest - ceiling)
        achieved = achieved + parsing.token_count(cell)
    lowest = max(room_low, walk_low - allowance)
    highest = min(room_high, walk_high)
    lowest = min(lowest, highest)
    return [
        Approximation(
            column=column.name,
            fact="words.mean",
            published=_figure(facts.words.mean),
            achieved=_figure(achieved / rows),
            lowest=_figure(lowest / rows),
            highest=_figure(highest / rows),
            inside=lowest <= achieved <= highest,
            note="how many words a value holds on average",
            covers_published=lowest <= wanted <= highest,
        )
    ]


def _label_supply(facts: contract.LabelFacts) -> int:
    """How many different spellings a column of labels is given (G8).

    One per published variant, one per variant the floor held back --
    for which method G8.2 makes a neutral spelling up -- one per level
    whose variants do not cover its own count, and one per level held
    back whole. That is the number of different spellings the twin
    writes, and where it differs from the published count of different
    spellings, the published count is the one that cannot be met.
    """
    supply = 0
    for entry in facts.levels:
        covered = 0
        for spelling in entry.variants:
            supply = supply + 1
            covered = covered + entry.variants[spelling]
        for key in entry.variants_withheld:
            supply = supply + entry.variants_withheld[key]
            covered = covered + int(key) * entry.variants_withheld[key]
        if covered < entry.count:
            supply = supply + 1
    return supply + facts.suppressed_levels


def _label_approximations(
    column: contract.ColumnBlock,
    facts: contract.LabelFacts,
    written: "list[str]",
) -> "list[Approximation]":
    """The one approximated fact of a column of labels (method G12.7).

    The count of different spellings is EXACT wherever the description's
    own spellings supply it, which is the ordinary case, and approximated
    only where they do not. Both cases are the same measurement, so it is
    made every run: the twin holds either the published count or the
    number of spellings the description supplies, and the two ends of the
    bound are exactly those two numbers.
    """
    supply = _label_supply(facts)
    counted = _recounted(written, _hole_spellings(column))
    lowest = min(supply, column.n_distinct)
    highest = max(supply, column.n_distinct)
    return [
        Approximation(
            column=column.name,
            fact="n_distinct",
            published=f"{column.n_distinct}",
            achieved=f"{counted[2]}",
            lowest=f"{lowest}",
            highest=f"{highest}",
            inside=lowest <= counted[2] <= highest,
            note="how many different spellings this column holds",
            covers_published=True,
        )
    ]


def _approximations(
    column: contract.ColumnBlock,
    plan: "_ColumnPlan",
    written: "list[str]",
) -> "list[Approximation]":
    """Every APPROXIMATED fact of one column, measured and bounded.

    Guarantees: accepts one column of the loaded description, the plan
    this run built for it and the cells this run wrote for it, in row
    order; returns one record per approximated fact the column's role
    publishes, in the fixed order of method G12.1, each carrying the
    published value, the value MEASURED from the written cells, the two
    ends of the bound and whether the measurement landed between them.
    Returns an empty list for a role that publishes no approximated
    fact. Raises nothing: a description the loader accepted and cells
    this module wrote are always measurable. Reads no file and draws no
    random word -- the measurement is a fixed function of the
    description and the cells, so the same run always reports the same
    numbers.
    """
    facts = column.facts
    if isinstance(facts, contract.AffixedFacts):
        # Measured over the CORES the written cells hold, because that
        # is the population every approximated fact of this role is
        # about. Without this the role reported no approximation at
        # all, so a ladder that landed outside its own window said
        # nothing -- the twin's report is where a person reads that,
        # and it was silent.
        cores: list[str] = []
        for cell in written:
            trimmed = parsing.trimmed(cell)
            if not trimmed.startswith(facts.affix_prefix):
                continue
            if not trimmed.endswith(facts.affix_suffix):
                continue
            core = trimmed[
                len(facts.affix_prefix) : len(trimmed)
                - len(facts.affix_suffix)
            ]
            if core:
                cores = cores + [core]
        return _numeric_approximations(
            _core_view(column), facts.numbers, plan, cores
        )
    if isinstance(facts, contract.JoinedFacts):
        # THIS ROLE REPORTS NO APPROXIMATION, AND THAT IS A KNOWN
        # DEFECT rather than a decision -- residual R-P4-44. A twin of
        # a joined column carries a report saying it gave nothing up
        # while every position's ladder is approximated by
        # construction, which is the same defect the affixed branch
        # above records and repairs one role earlier.
        #
        # A BRANCH THAT MEASURED EACH POSITION WAS BUILT HERE AND
        # WITHDRAWN, and what it cost is why: `_part_view` hands a
        # position the WHOLE CELL's distinctness counts, so the report
        # printed per-position comparisons of facts the profile
        # publishes for no position; the renderer has no way to say
        # WHICH position a record belongs to, so both printed as "this
        # column" with `percentiles.p01` appearing twice at different
        # values; an unsplit stand-in `text-1` splits on `-` and was
        # measured into position two; and `part_agreements`, the one
        # fact this role's own decision calls approximated, was not
        # measured at all. Measured on three columns before the
        # withdrawal. A report that prints ambiguous numbers is worse
        # than one that prints none, so the honest state is the silent
        # one until the role's landing does it properly.
        return []
    if isinstance(facts, contract.NumericFacts):
        return _numeric_approximations(column, facts, plan, written)
    if isinstance(facts, contract.ClockFacts):
        return _clock_approximations(column, facts, written)
    if isinstance(facts, contract.DatetimeFacts):
        return _datetime_approximations(column, facts, written)
    if isinstance(facts, contract.TextFacts):
        return _text_approximations(column, facts, written, plan.carriers)
    if isinstance(facts, contract.LabelFacts):
        return _label_approximations(column, facts, written)
    return []


def _bound_notes(measured: "list[Approximation]") -> "list[Deviation]":
    """Name every approximated fact that landed outside its own bound.

    An approximated fact is not a fact the twin may miss quietly. Its
    bound is a statement about the construction (method G12.1), so a
    measurement outside it means the twin does not hold what this method
    promises -- which belongs in the list of facts the twin could not
    meet, beside every other one, and not only in the section that shows
    how close the approximations came.
    """
    notes: list[Deviation] = []
    for found in measured:
        if found.inside:
            continue
        notes = notes + [
            _deviation(
                found.column,
                found.fact,
                found.published,
                found.achieved,
                "This fact is approximate by construction, and the twin "
                f"landed outside the range this method promises for it "
                f"({found.lowest} to {found.highest}). Treat it as not "
                "reproduced: a check that depends on it can behave "
                "differently here than on the real table.",
            )
        ]
    return notes

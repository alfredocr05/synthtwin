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

# The three alphabets of method G9.1. The ORDER is part of the
# specification, because it decides which spellings are produced first.
# `_CODE` is exactly the alphabet `parsing.is_code_text` accepts, in
# ASCII code-point order, which is what makes the code-alphabet count
# reproducible; `_DIGITS` is a subset of it, which is what makes an
# all-figures value count toward that same fact.
_DIGITS = tuple("0123456789")
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
    """

    column: str
    fact: str
    published: str
    achieved: str
    lowest: str
    highest: str
    inside: bool
    note: str


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


@dataclasses.dataclass(frozen=True)
class GenerationPlan:
    """Every column's plan, and the whole run's word budget.

    Building one is the generation-feasibility stage of plan P2-D6: it
    runs after the loader and before any generation, it never calls a
    conforming description invalid, and it is where the two refusals of
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


def _recounted(cells: "list[str]") -> "tuple[int, int, int, int]":
    """Recount a written column: present, absent, different, folded."""
    present = [cell for cell in cells if cell != ""]
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
    if place >= len(figures) and -4 < place <= 16:
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
    value: float, style: str, order: int, whole_column: bool
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
        return _with_zeros(_point_free(value, canonical), max(order, 1))
    if style == "leading_plus":
        plain = _point_free(value, canonical)
        if plain[0] == "-":
            return plain
        return _with_zeros(f"+{plain}", order)
    figures = _digits_and_point(value)
    if style == "decimal":
        return _with_zeros(
            _fixed_point(figures[0], figures[1], figures[2]), order
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


def _text_spelling(order: int, used: "dict[str, int]") -> str:
    """Ordinary text that reads as no number and no date (G10.3, G10.4).

    `text-1`, `text-2` and so on, stepped past any spelling that means
    "no value", any spelling already used in this column, and any
    spelling that would read as a date under one of the formats the
    profiler tries -- so a stand-in can never quietly change a count.
    """
    step = order
    while True:
        candidate = f"text-{step}"
        if (
            not parsing.is_missing_text(candidate)
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
            spelling = _base_spelling(kind, order, negative, used)
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
    kind: str, order: int, negative: bool, used: "dict[str, int]"
) -> str:
    """The ``order``-th base spelling of one straggler class."""
    if kind == _CLASS_OUT_OF_RANGE:
        return _out_of_range_spelling(order, negative)
    if kind == _CLASS_CONTRADICTORY:
        return _contradictory_spelling(order)
    return _text_spelling(order, used)


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
        )
    if column.n_not_numeric:
        cells = cells + _class_spellings(
            _CLASS_TEXT,
            column.n_not_numeric,
            layout.folded_budgets[3],
            layout.raw_budgets[3],
            0,
            used,
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
    base: list[str] = []
    for index in range(len(holds)):
        base = base + [
            _styled_number(
                holds[index],
                styles[index],
                1 if styles[index] == "leading_zero" else 0,
                facts.integer_valued,
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
            and parsing.folded(spelling) in identities
        ):
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
                    holds[index], style, order, facts.integer_valued
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
        cells = cells + [text]
    if parsed >= 1:
        notes = notes + _endpoint_notes(
            column, facts, "earliest", facts.earliest, cells[0]
        )
    if parsed >= 2:
        notes = notes + _endpoint_notes(
            column, facts, "latest", facts.latest, cells[parsed - 1]
        )
    used: dict[str, int] = {cell: 1 for cell in cells}
    for step in range(facts.n_unparsed):
        cells = cells + [_take(_text_spelling(step + 1, used), used)]
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


def _endpoint_notes(
    column: contract.ColumnBlock,
    facts: contract.DatetimeFacts,
    key: str,
    published: str,
    written: str,
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
    if found == published:
        return []
    achieved = "a value that does not read as a date at all"
    if found is not None:
        achieved = found
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
        for key in sorted(entry.variants_withheld):
            rows = int(key)
            for _each in range(entry.variants_withheld[key]):
                variant = _variant_spelling(entry.label, used, owners)
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
                "so the twin keeps the count and the values distinct but "
                "not the spellings themselves.",
            )
        ]
    number = 0
    for size in facts.suppressed_level_counts:
        number, label = _made_up_label(number, used, owners)
        cells = cells + [label for _row in range(size)]
    if facts.suppressed_levels:
        notes = notes + [
            _deviation(
                column.name,
                "suppressed_levels",
                f"{facts.suppressed_levels} labels that were held back",
                f"{facts.suppressed_levels} neutral labels made up in their "
                f"place",
                "Those labels covered too few rows to publish, so the twin "
                "keeps their number and their sizes but not the labels.",
            )
        ]
    return cells, notes


def _variant_spelling(
    parent: str, used: "dict[str, int]", owners: "dict[str, str]"
) -> str:
    """One made-up spelling of a published label (method G8.2).

    Case flips first, in the binary-counter order the method fixes, and
    then trailing spaces, whose supply has no end. A candidate is
    stepped past when it is already used in this column, or when it
    would fold onto a DIFFERENT label -- so the published counts of
    folded identities stay exactly what the description says.
    """
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


def _made_up_label(
    number: int, used: "dict[str, int]", owners: "dict[str, str]"
) -> "tuple[int, str]":
    """One neutral label standing in for one that was held back (G8.3).

    `group-1`, `group-2`, `group-3` and so on, stepped past any spelling
    already used in this column, raw or folded. They are neutral by
    construction: they carry no fragment of any real value, they are not
    one of the spellings that mean "no value", they read as neither a
    number nor a date, they hold no comma or quote so they need no
    quoting, and they do not begin with a character a spreadsheet reads
    as the start of a formula.
    """
    step = number
    while True:
        step = step + 1
        candidate = f"group-{step}"
        if candidate in used or parsing.folded(candidate) in owners:
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
    used: dict[str, int] = {}
    notes: list[Deviation] = []
    folded = min(column.n_distinct_folded, total)
    partners = total - folded
    width = len(_BANDS)
    packed, pinned = _identifier_families(
        column, facts, groups, folded, partners
    )
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
    spellings: list[str] = []
    repeated = 0
    for index in range(total):
        kind = kinds[index]
        band = bands[index]
        partner = _partner_of(
            index, folded, spellings, families, used, windows
        )
        if partner is not None:
            spellings = spellings + [_take(partner, used)]
            continue
        letter = asks[index] and band != _BAND_DIGITS
        spelling: str | None = None
        if index == carriers[0]:
            spelling = _pinned_identifier(
                kind, band, facts, facts.min_length, used, letter
            )
        elif index == carriers[1] and facts.max_length > facts.min_length:
            spelling = _pinned_identifier(
                kind, band, facts, facts.max_length, used, letter
            )
        else:
            spelling, again = _next_identifier(
                kind,
                band,
                facts,
                states[families[index]],
                used,
                letter,
            )
            if again:
                repeated = repeated + 1
        _claim(spelling, used)
        spellings = spellings + [spelling]
    if repeated or len(set(spellings)) < total:
        notes = notes + _repeat_notes(column)
    return _grouped(groups, spellings), notes


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
    """
    total = len(cells)
    if partners < 1 or partners >= total or folded < 1:
        return [place for place in range(total)]
    left = [place for place in range(total)]
    tail: list[int] = []
    for _step in range(partners):
        picked = -1
        for wanted in (True, False):
            for place in range(len(left) - 1, -1, -1):
                if folds[left[place]] != wanted:
                    continue
                kept = 0
                for other in left:
                    if cells[other] == cells[left[place]]:
                        kept = kept + 1
                if kept >= 2:
                    picked = place
                    break
            if picked >= 0:
                break
        if picked < 0:
            picked = len(left) - 1
        tail = [left[picked]] + tail
        left = left[:picked] + left[picked + 1:]
    return left + tail


def _identifier_at(
    kind: str,
    band: str,
    facts: contract.IdentifierFacts,
    length: int,
    index: int,
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
        # THE TWO-CHARACTER CODE FAMILY IS GONE (Phase 3 plan P3-D8.1,
        # closing the registry's open P2-C5-F4). It wrote `-0` through
        # `-9`, which are the only two-character spellings that are
        # code-alphabet, not figures alone, and read back as whole
        # numbers -- and every one of them opens with a character G9.1
        # bars from the first position, because a leading `-` is what a
        # spreadsheet reads as a formula. Meeting one published count by
        # breaking a ratified rule is not a repair, and the report then
        # said something false besides: its formula paragraph tells the
        # reader that a hazardous cell is a value the description
        # published, and `-0` was invented here. So the family is
        # withdrawn, the code band starts at three characters
        # (`<digits>e0`), and the descriptions that leaves with no
        # answer at all are REFUSED by name in `_whole_number_room`
        # rather than written wrong and reported.
        return _whole_at(band, length, index)
    return _family_at(kind, band, length, 1, index)


def _identifier_room(
    kind: str, band: str, facts: contract.IdentifierFacts, length: int
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
    first = _identifier_at(kind, band, facts, length, 0)
    if first is None or len(first) != length:
        return 0
    if kind == _CLASS_NUMBER and facts.all_whole_numbers:
        if band == _BAND_DIGITS:
            return _power_at_most(10, max(length, 1), _DOMAIN_CEILING)
        return _whole_room(band, length)
    return _family_room(kind, band, length, 1)


def _identifier_permits(
    facts: contract.IdentifierFacts, shortest: int, longest: int
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
                    _CLASSES[place], _BANDS[band], facts, length
                ) > 0:
                    mask = mask | (1 << (place * width + band))
                    break
    if mask == 0:
        return _every_bucket(len(_CLASSES) * width)
    return mask


def _identifier_families(
    column: contract.ColumnBlock,
    facts: contract.IdentifierFacts,
    groups: "tuple[int, ...]",
    folded: int,
    partners: int,
) -> "tuple[list[int], tuple[int, int]]":
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
    sized: dict[tuple[int, int], int] = {}
    spent: dict[tuple[tuple[int, int], ...], int] = {}
    for carriers in _shape_choices(total):
        shape = (groups[carriers[0]], groups[carriers[1]])
        if shape in sized:
            continue
        sized[shape] = 1
        permits = _identifier_windows(facts, total, carriers)
        seen = tuple(sorted(
            [(groups[place], permits[place]) for place in range(total)]
        ))
        if seen in spent:
            continue
        spent[seen] = 1
        together = _joint_allocation(groups, classes, alphabets, permits)
        if together is None:
            continue
        return (
            _collision_slots(
                together, groups, folded, partners, permits
            ),
            carriers,
        )
    carriers = _shape_choices(total)[0]
    permits = _identifier_windows(facts, total, carriers)
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
        _collision_slots(together, groups, folded, partners, permits),
        carriers,
    )


def _identifier_windows(
    facts: contract.IdentifierFacts,
    total: int,
    carriers: "tuple[int, int]",
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
        permits = permits + [_identifier_permits(facts, shortest, highest)]
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
        ceiling = _identifier_room(kind, band, facts, length)
        index = 0
        asked = 0
        while index < min(ceiling, len(used) + _ASK_STEPS + 2):
            candidate = _identifier_at(kind, band, facts, length, index)
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
    found = _walked_identifier(kind, band, facts, state, used, letter)
    if found is None and letter:
        state[0] = began[0]
        state[1] = began[1]
        state[2] = began[2]
        found = _walked_identifier(kind, band, facts, state, used, False)
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
        if index >= _identifier_room(kind, band, facts, length):
            length = length + 1
            index = 0
            continue
        candidate = _identifier_at(kind, band, facts, length, index)
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


def _partner_of(
    index: int,
    folded: int,
    spellings: list[str],
    families: "list[str]",
    used: "dict[str, int]",
    windows: "list[tuple[int, int | None]]",
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
    for step in range(folded):
        parent_place = (place + step) % folded
        if families[parent_place] != families[index]:
            continue
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


def _collision_slots(
    cells: "list[int]",
    groups: "tuple[int, ...]",
    folded: int,
    partners: int,
    permits: "list[int]",
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
    moved = [cell for cell in cells]
    for place in needed:
        if moved[place] - (moved[place] // width) * width != 0:
            continue
        for other in range(total):
            if other in needed or groups[other] != groups[place]:
                continue
            if moved[other] - (moved[other] // width) * width == 0:
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
    column: contract.ColumnBlock, groups: "tuple[int, ...]"
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
    made: dict[str, int] = {}
    for index in range(total):
        partner = _partner_of(
            index, folded, spellings, families, used, windows
        )
        if partner is not None:
            spellings = spellings + [_take(partner, used)]
            continue
        kind = _CLASSES[kinds[index]]
        band = _BANDS[bands[index]]
        key = f"{kind}/{band}/{lengths[index]}/{counts[index]}"
        spelling = _made_up_cell(
            kind, band, lengths[index], counts[index],
            asks[index], states, used,
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
        spellings = spellings + [spelling]
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


def _made_up_cell(
    kind: str,
    band: str,
    length: int,
    words: int,
    letter: bool,
    states: "dict[str, list[int]]",
    used: "dict[str, int]",
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
    key = f"{kind}/{band}/{length}/{words}"
    if key not in states:
        states[key] = [0]
    state = states[key]
    began = state[0]
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
    asked = 0
    while state[0] < room:
        index = state[0]
        state[0] = state[0] + 1
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
        spelling = _wide_number(kinds[index], signs[index], states, used)
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
    used: "dict[str, int]",
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
            candidate = _text_spelling(index + 1, used)
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


def _whole_numbers_need_code_room(
    name: str, shortest: bool, present: int, coded: int, length: int
) -> str:
    """Whole record numbers in the code alphabet two characters cannot spell.

    The `generation-whole-numbers-need-code-room` refusal of method
    G12, and the FIFTH -- landed by the Phase 3 plan's owner decision 1
    as an amendment to that section rather than as an unannounced
    branch, which is what the section's own sentence about a fifth
    refusal requires.

    THE ARITHMETIC, FROM PUBLISHED NUMBERS ALONE. A value written in
    the code alphabet but not in figures alone, and reading back as a
    whole number, is at least three characters long. Every shorter
    candidate is barred by a rule that was ratified before this one: a
    single character that reads as a whole number is a figure, so it
    would be counted in `n_all_digits`; and the only two-character
    spellings left are a sign in front of a figure, which G9.1 refuses
    at the first position because a leading `-` is what common
    spreadsheet software reads as the start of a formula. `<digits>e0`
    is the shortest that remains, and it is three.

    WHAT IS IMPOSSIBLE IS THE TWIN, NOT THE TABLE (review item
    P3-C1-F6). A real table holds these facts easily -- it holds them by
    writing `-3` -- and the message says so rather than telling a person
    their own data cannot exist. What no conforming twin can do is hold
    them while keeping G9.1's bar, because every spelling left to an
    INVENTED value opens with the sign. So two published pairs are
    jointly unwritable here:

    - every value is a whole number, no value is longer than two
      characters, and some of them are written in the code alphabet
      without being figures alone;
    - every value is a whole number, the shortest value is two
      characters long, none of them is written in figures alone, and
      every one of them is written in the code alphabet -- so that
      shortest value has no band left that can spell it.

    Before this refusal the generator wrote `-0` through `-9` here,
    which met the count by breaking the formula-context rule and left
    the report saying a hazardous cell was a value the description had
    published. Neither fact is traded: the refusal says the description
    is valid and stops.
    """
    wide = f"{length} character" if length == 1 else f"{length} characters"
    said = (
        f"the shortest value is {wide} long, that none of the {present} "
        "values is written in figures alone, and that every one of them "
        "is written in the code alphabet"
        if shortest
        else f"no value is longer than {wide}, and that {coded} of the "
        f"{present} values are written in the code alphabet without "
        "being figures alone"
    )
    carries = (
        "so that shortest value has no way left to be written"
        if shortest
        else "so each of those values would need a third character"
    )
    return (
        f"The description of the column '{parsing.visible(name)}' is "
        f"valid, but synthtwin cannot build a twin column from it. It says "
        f"every value reads as a whole number, that {said}. The shortest "
        f"whole number written in the code alphabet without being figures "
        f"alone is three characters long, like '1e0' -- the two-character "
        f"spellings are a sign in front of a figure, and synthtwin never "
        f"begins an invented value with a sign, because a spreadsheet "
        f"reads it as a formula, {carries}. Your own table can hold "
        f"these two facts together -- it holds them with the sign -- "
        f"but synthtwin cannot write a twin that does, so there is "
        f"nothing to build. "
        + _no_twin_can_hold_it(
            "say that the values are not all whole numbers",
            "give the values room for a third character",
        )
    )


def _no_twin_can_hold_it(first: str, second: str) -> str:
    """What to do about a pair a real table holds and no twin can.

    THE OTHER TAIL WOULD BE FALSE HERE (review item P3-C2-F3).
    `_edited_by_hand` tells the person that no described table produces
    this pair, that their description must have been edited, and that
    describing the table again would settle it. For the four refusals it
    serves, all three are true. For the fifth they are all false: the
    shipped producer writes this pair from a real table of values like
    `-3`, so describing that table again produces exactly the same pair,
    and sending the person around that loop would waste their time and
    tell them their file is corrupt when it is not.

    So this tail says the true thing instead -- the twin is what cannot
    be written, the description is fine, and the two edits are offered
    as choices about what the twin should carry rather than as repairs
    to something broken.
    """
    return (
        f"Nothing has been written and every file in the folder is as it "
        f"was. What to do next: the description is not damaged and does "
        f"not need making again -- describing the same table would "
        f"produce the same pair. What synthtwin cannot do is invent "
        f"values that hold both facts at once. Either of two edits to "
        f"the description file lets it build, and the twin then carries "
        f"the fact you chose rather than the one it replaced: {first}, "
        f"or {second}. Either way the twin's record numbers stop "
        f"matching your table's on the fact you gave up, which the "
        f"report says in as many words. The description file is all "
        f"synthtwin needs for this, so neither edit asks you for the "
        f"table."
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
    - Errors raised: `errors.ProfileError`, and only for the five
      refusals method G12 names -- a column of numbers whose counts of
      zero and negative values leave no room; a column of text or of
      unheld numbers needing more different values than its own length
      range can spell; a column of text whose published word extreme
      needs more characters than its own published length carries; a
      declared column of record numbers published as whole numbers that
      one character cannot write outside the figures; and one whose
      whole numbers must stand in the code alphabet with no room for a
      third character, the shortest such spelling being three long once
      a leading sign is barred. Each says the description is VALID,
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
    for column in profile.columns:
        plan = _plan_column(column, profile.n_rows)
        plans = plans + [plan]
        words = words + plan.content_words + plan.placement_words
    return GenerationPlan(columns=tuple(plans), words_planned=words)


def _plan_column(
    column: contract.ColumnBlock, n_rows: int
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
    if isinstance(facts, contract.NumericFacts):
        layout, notes, content = _numeric_layout(column, facts)
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
        cells, notes, carriers = _text_cells(column, groups)
    elif isinstance(facts, contract.UnrepresentableFacts):
        groups = _groups_of(facts.n_distinct_by_occurrences)
        cells, notes = _unrepresentable_cells(column, groups)
    return _ColumnPlan(
        column=column,
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

    AND THE SAME ARITHMETIC ONE BAND IN (Phase 3 plan P3-D8.1, closing
    the registry's open P2-C5-F4). Two characters carry `1.` in the
    band OUTSIDE the code alphabet, and nothing at all inside it: the
    two-character code spellings that read as whole numbers all open
    with a sign, which G9.1 bars at the first position. So a
    description whose code-alphabet values have no third character to
    use, or whose shortest value has no band left but that one, is
    refused here too rather than written with a leading `-`.
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
    coded = facts.n_code_alphabet - facts.n_all_digits
    wide = column.n_present - facts.n_code_alphabet
    if facts.max_length < 3 and coded > 0:
        raise errors.ProfileError(
            _whole_numbers_need_code_room(
                column.name,
                False,
                column.n_present,
                coded,
                facts.max_length,
            )
        )
    if (
        facts.min_length < 3
        and facts.n_all_digits < 1
        and wide < 1
        and column.n_present
    ):
        raise errors.ProfileError(
            _whole_numbers_need_code_room(
                column.name,
                True,
                column.n_present,
                coded,
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
    if kind == "count" or kind == "continuous":
        return _numeric_content(plan, words)
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
      range, and the two generation refusals of `plan_generation`, which
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
        content = content + ["" for _cell in range(column.n_missing)]
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
        counted = _recounted(written)
        notes = (
            list(each.notes)
            + notes
            + _recount_notes(column, counted)
            + _class_notes(column, written)
            + _alphabet_notes(column, written)
            + _extreme_notes(column, written)
            + _width_notes(column, written)
            + _whole_notes(column, written)
            + _magnitude_notes(column, written)
            + _style_notes(column, written)
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
            reason = (
                "The twin holds MORE different values, ignoring case and "
                "edge spacing, than the description records, for the same "
                "reason: how often a value repeats is not a fact this "
                "column's rule holds on to."
            )
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
        parsing.trimmed(cell) for cell in written if cell != ""
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
    present = [cell for cell in written if cell != ""]
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
    present = [cell for cell in written if cell != ""]
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
    present = [cell for cell in written if cell != ""]
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
    present = [parsing.trimmed(cell) for cell in written if cell != ""]
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
    facts = column.facts
    if not isinstance(facts, contract.NumericFacts):
        return []
    published = {name: 0 for name in contract.NUMERIC_STYLES}
    for name in sorted(facts.numeric_styles):
        if name != contract.WITHHELD:
            published[name] = facts.numeric_styles[name]
    pooled = _style_pool(facts.numeric_styles)
    counted = {name: 0 for name in contract.NUMERIC_STYLES}
    pointless = 0
    for cell in written:
        if cell == "":
            continue
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
        for cell in written:
            if cell == "" or parsing.numeric_style(cell) != name:
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
    for cell in written:
        if cell == "":
            continue
        if parsing.classify_number(cell) == parsing.NOT_A_NUMBER:
            continue
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


def _numeric_supply(
    layout: "_NumericLayout", written: "list[str]"
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
    - Each other class supplies what its own share of the budget allows,
      never more than its cell count.

    Returns the raw and the folded supply. Neither is a measurement of
    what was written: a twin that wrote one spelling where its own cells
    could have carried two leaves the bound, which is what makes the
    bound able to fail.
    """
    present = [cell for cell in written if cell != ""]
    counted = {name: 0 for name in _CLASSES}
    seen: dict[tuple[float, str], int] = {}
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
        if style != "plain":
            raw_room = raw_room + 1
            folded_room = folded_room + 1
            continue
        if (value, style) not in seen:
            seen[(value, style)] = 1
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
    supply = _numeric_supply(layout, written)
    counted = _recounted(written)
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
                for cell in written
                if cell != ""
                and parsing.classify_number(cell) == parsing.NUMBER
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
    if facts.resolution == "quarter":
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


def _datetime_approximations(
    column: contract.ColumnBlock,
    facts: contract.DatetimeFacts,
    written: "list[str]",
) -> "list[Approximation]":
    """The two approximated families of a column of dates (G12.4, G12.5)."""
    present = [cell for cell in written if cell != ""]
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
    counted = _recounted(written)
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
    present = [cell for cell in written if cell != ""]
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
    counted = _recounted(written)
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
    if isinstance(facts, contract.NumericFacts):
        return _numeric_approximations(column, facts, plan, written)
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

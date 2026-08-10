"""What kind of column is this, and how is it described (plan P1-D4).

Every column gets exactly one role, decided by rules that are written
out here and tested in the order they appear. The first rule that
matches wins, and the profile records which one it was and why, so a
reader can always see how a column was routed. There is no
"unsupported column" outcome: a column that matches no rule is
described as free text, which publishes no values at all.

ONE ROLE IS NOT DECIDED HERE AT ALL. `identifier` is reached only when
the person who owns the table names the column with `--identifier`. It
was inferred from the values until review item P1-R6-F8, and three
successive inferences were each defeated by an ordinary column that
happened to look the same: `1mg` and `code1` are the same shape of
string, and what tells a dose from a label is what the column MEANS,
which the values do not carry. The guess also had nothing to win --
when right it published no more than free text does, and when wrong it
destroyed a real distribution -- so it is withdrawn rather than
sharpened for a fourth time.

Sending a column down the wrong path is the failure this module exists
to prevent -- numeric-looking codes treated as quantities, categories
treated as free text -- because it corrupts the twin quietly, while
every test stays green and nothing crashes. Three habits guard against
it: thresholds are named constants recorded in every profile, a column
that lands close to a threshold is reported as close, and competing
readings are named in the evidence rather than hidden.

THERE IS ONE LINE FOR THE NUMERIC ROLES AND ONE CEILING FOR THE
CATEGORY ROLE, and both are the plan's (review item P1-R6-F7).

* A column is described as numbers -- count or continuous -- only when
  at least `minimum_parse_rate` (0.99) of its present values read as
  numbers this format can hold. A second, lower line stood beside it
  through round 6: a column that was merely a MAJORITY numbers kept a
  published distribution. Sixty numbers beside forty two-word notes
  were then published with role `count`, a mean computed over the
  sixty, and the other forty left out of the distribution and named
  nowhere in it -- a column dropped, miscast and approximated at once,
  which is the one outcome charter principle 5 forbids. That line is
  deleted.
* FALLING BELOW THAT LINE SETTLES NOTHING BY ITSELF. It rules the
  numeric roles out, and role selection CONTINUES down the remaining
  rules in their order: the category rule is tested next, and free text
  is the last rule rather than the consequence of the numeric one.
  Ninety-eight repeated numeric spellings beside two words are a set of
  categories in a hundred-row table, not free text. A column that does
  reach free text carries a remark naming every reading that was tried
  and how much of the column each one read.
* A column is described as a set of categories only when the number of
  different values it holds, after trimming and case folding, is at
  most `min(categorical_ceiling, categorical_share of the TABLE'S
  ROWS)`, never below `categorical_floor`. Rows rather than present
  values, and the two differ on a sparse column: `_categorical_ceiling`
  states the rule where it is applied and gives the case. The rule that
  stood here through round 6 -- an average repetition of two, with a
  separate cap of twelve on mostly numeric columns -- called forty
  different labels in a hundred rows a set of categories and published
  the one that cleared the floor. Real labels crossing the privacy
  boundary is the direction to be conservative in, so the plan's
  ceiling is what is implemented.
* NOTHING IS ROUTED BY THE WIDTH OF ITS TEXT. A rule that read
  same-width digit strings carrying a leading zero as codes ran ahead
  of the dates and the numbers until the same review item; it is
  deleted, and such a column now lands where the ordinary rules put it.

WHAT THE PERSON RUNNING THE TOOL DECLARES HAS THE LAST WORD, and one
rule says what a declaration matches (review item P1-R6-F9):

* a declared value that READS AS A NUMBER this format can hold matches
  every cell holding that EXACT NUMBER, whatever either of them is
  spelled like: `--keep-value -999` covers a file that writes
  `-999.00`, which is the whole reason the comparison is on the number;
* EXACT means exact, and not "equal once both are rounded". Two decimal
  spellings that are different numbers can round to one binary64 value,
  and comparing the rounded values removed cells nobody had named and
  called two different declarations a contradiction (review item
  P1-R7-F3). Both sides are therefore compared as the numbers their
  digits denote, by `_exact_value` and `_exact_number`. The
  numeric-sentinel rule asks that same exact question of those same
  records -- which cells ARE a candidate, how many rows hold it, and
  which cells are taken out -- because a later rule that rounds undoes
  a comparison that did not (review item P1-R8-F2);
* a declared value that does not read as such a number matches by
  SPELLING, after trimming and case folding: `--keep-value NA` covers
  `na` and ` NA `, and covers nothing else;
* the same value named both ways is refused, never resolved, on both
  paths that exist: the command refuses it before it opens the table,
  and `profile_column` raises ValueError before it describes anything.
  Building `Settings` is not one of those paths -- the class docstring
  says why -- so both callers ask `contradictory_declarations`.

THREE STRUCTURAL RULES hold this module together, and each one closes a
whole family of defects rather than one instance of it.

* ONE CELL RECORD. Every present cell is classified exactly once, by
  `_classify`, into an immutable `_Cell` carrying what the cell is
  numerically, the value it parsed to, its sign and whether it is a
  whole number. Every rule below reads that record and nothing else:
  no rule asks the parser about a cell a second time, and dropping a
  numeric sentinel FILTERS the records rather than reading the column
  again. Round 5's claim to this was not true of the code -- the sign
  and whole-number helpers each classified the cell again, and
  sentinel removal reparsed the whole column -- so two rules could in
  principle have disagreed about the same cell (review items
  P1-R3-F3, P1-R4-F2, P1-R5-F2, P1-R6-F10).
* ONE CONSTRUCTION SITE. `profile_column` builds exactly one
  ColumnProfile, at the end, whatever role was decided. A count cannot
  therefore be present on the roles someone remembered and absent on
  the rest -- which is exactly how a count goes missing at the moment it
  matters.
* ROLE DECIDES PUBLICATION, NOTHING ELSE DOES. Each role belongs to one
  of three publication classes, and the class governs every field of
  the output: the levels, the missing spellings, the evidence, the
  remarks, the notes. A fact about the table reaches the profile only
  through a channel its role opens (review item P1-R1-F10).

Every published number is computed so that the answer does not
depend on the machine, the row order, or the magnitude of the data
(plan P1-D11). Nothing is accumulated in floating point at all, which
is what makes that exact rather than nearly true:

* every finite binary64 value IS a whole number times a power of two,
  and `_parts` splits it into exactly that. A column becomes one shared
  power of two and one whole significand per value;
* `_totals` adds those significands, their squares and their cubes as
  WHOLE NUMBERS, in groups sharing one exponent. Whole-number addition
  neither rounds nor depends on the order it is done in, so the three
  power sums are exact and the row order cannot reach them;
* the mean, the standard deviation and the skewness are then exact
  fractions of those whole numbers, written out in `_moments`, and each
  is rounded to binary64 exactly ONCE -- by `_rounded_ratio` for a
  quotient and `_rounded_root` for a square root. Both settle the last
  digit by comparing whole numbers, so the rounding is the correct one
  on every platform, with a tie going to the even significand;
* a ladder rung is the same shape of computation: its position is
  located in whole numbers, and the interpolation between its two
  neighbours is one exact fraction rounded once (`_quantile`).

HISTORY, recorded because the accuracy contract rests on the change.
Revision 1 of the plan computed all of this as a two-pass FLOATING-
POINT reduction -- sorted values, `math.fsum`, a power-of-two rescale
before every sum, the deviations recentred once -- and recorded with it
a "conditioning limit" saying that a sample such as {1e16, 1, -1e16}
could not have a correctly rounded skewness. Both were retired at
review round 5: the limit was a property of that reduction rather than
of binary64, and a cancellation that defeats floating point costs whole
numbers nothing. Neither `math.fsum` nor `math.sqrt` is called anywhere
in this module now.

Every list built one item at a time is grown with `+= [item]`, which
extends the list in place. `values = values + [item]` copies everything
accumulated so far, so the work of describing a column grew as the
SQUARE of its length: a column of twenty thousand numbers spent most of
its run copying its own prefix (review item P1-R6-F10). The `+=` form
is used rather than a method call because the offline policy accepts no
method call on a computed value (plan D6.2).

`**` is used for one thing only, and it is not arithmetic on a
measured value: `5 ** -twos` in `_exact_number`, a whole number raised
to a whole power, which Python computes exactly. It is never used for
a square or a square root, because on floats it calls the platform's
`pow`, which no standard requires to be correctly rounded. Every
square here is `x * x` on whole numbers and every square root is
`_root_of`, Newton's method on whole numbers, so both are exact by
construction rather than by trusting a library to round well.

The accuracy this buys is stated as a contract in plan P1-D11 and is
tested against reference vectors computed by exact rational arithmetic
in `tools/reference/`, never by this code.

Imports here stay within the allowlist (plan D6.2 with the Phase 1
additions in P1-D10): dataclasses, math, and this package's own
modules. Nothing in this module reads a file.
"""

import dataclasses
import math

from synthtwin import parsing

# The eleven points of the percentile ladder: the shape-carrying
# summary of a numeric column (plan P1-D4).
# The rungs are written as exact fractions rather than as decimals,
# because 0.99 has no exact binary spelling and the nearest one can move
# a rung to the wrong pair of neighbours in a large column.
LADDER = (
    ("min", 0, 100),
    ("p01", 1, 100),
    ("p05", 5, 100),
    ("p10", 10, 100),
    ("p25", 25, 100),
    ("p50", 50, 100),
    ("p75", 75, 100),
    ("p90", 90, 100),
    ("p95", 95, 100),
    ("p99", 99, 100),
    ("max", 100, 100),
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
ROLE_TEXT = "free_text"

# Every role a column can be given. The order is the order the rules
# are tested in, with one exception worth naming: `identifier` is not in
# that order at all, because NO rule decides it. It is reached only when
# the person who owns the table names the column with `--identifier`.
#
# It was inferred from the values until review item P1-R6-F8, and three
# repairs to the inference were each defeated by the column next door.
# The reason is not that the rules were badly drawn: `1mg` and `code1`
# are the same shape of string, and what separates a dose from a label
# is what the column MEANS, which no property of the values carries.
# Guessing has no upside either -- a right guess publishes nothing a
# free-text column would not have published, and a wrong guess destroys
# a real distribution -- so the guess is withdrawn rather than sharpened.
#
# A column that no rule below claims is described as free text, which
# publishes no value at all. Free text is what a column becomes when no
# positive reading fits it.
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
    ROLE_TEXT,
)

# THE THREE PUBLICATION CLASSES. A role belongs to exactly one, and the
# class -- not the branch that happened to build the block -- decides
# what may appear in the output.
#
# * labels: the values themselves appear, case-folded, with counts, and
#   only when at least `small_cell_floor` rows share them.
# * ranges: no spelling appears; order statistics computed from the
#   values do.
# * nothing: no value, no spelling, no fragment of one, anywhere --
#   not in levels, not in missing_by_source, not in the evidence, not
#   in a remark, not in a publication note, not in a sentinel verdict.
ROLES_PUBLISHING_LABELS = (ROLE_CONSTANT, ROLE_BINARY, ROLE_CATEGORICAL)
ROLES_PUBLISHING_RANGES = (ROLE_COUNT, ROLE_CONTINUOUS, ROLE_DATETIME)
ROLES_PUBLISHING_NOTHING = (
    ROLE_UNREPRESENTABLE,
    ROLE_IDENTIFIER,
    ROLE_TEXT,
)

# The label a suppressed value is replaced by, and the key under which
# blank cells are counted.
SUPPRESSED_LABEL = "(withheld)"
BLANK_SPELLING = parsing.MISSING_BLANK

# EVERY key a column block of a nothing-publishing role may carry with
# its own contents intact. The list is a WHITELIST on purpose. A
# blacklist of the keys that hold a spelling was the shape that failed:
# `missing_by_source` and the levels were each closed by name, and
# `sentinel_verdicts` -- added later, holding the spelling of a
# candidate under `candidate` -- was not on anybody's list, so an
# identifier column published `-999` while its own summary promised
# nothing of its values would appear (review item P1-R7-F2). Under a
# whitelist the next field added anywhere in this module is withheld
# from those roles until somebody names it here and says why it carries
# no value.
#
# Every name below is a count, a length, a word count, or a yes/no
# about the column as a whole. `length` and `words` are named as whole
# containers because everything inside them is a length or a word
# count; no other container is named, so no other container passes.
#
# `n_distinct_by_occurrences` is named as a whole container too, and it
# is the first one here whose KEYS are built rather than written out, so
# it is worth saying why they pass. Its keys are row counts written in
# base ten -- how many rows one value covers -- and its values are
# counts of different values. No spelling of the column reaches either
# side, and `_n_distinct_by_occurrences` below is the one function that
# builds it.
KEYS_THAT_CARRY_NO_VALUE = (
    "all_whole_numbers",
    "length",
    "max_length",
    "min_length",
    "n_all_digits",
    "n_code_alphabet",
    "n_distinct_by_occurrences",
    "n_fraction",
    "n_negative",
    "n_occurrences",
    "n_positive",
    "n_sign_unknown",
    "n_whole",
    "n_whole_unknown",
    "reason",
    "verdict",
    "words",
)

# What was decided about one numeric sentinel candidate, and why. The
# reasons are codes rather than sentences so a program can act on them
# and the summary can render them; none of them carries a value.
VERDICT_MISSING = "read_as_missing"
VERDICT_KEPT = "kept_as_a_number"
REASON_OUTLIER_AND_FREQUENT = "outlier_and_frequent"
REASON_NOT_AN_OUTLIER = "not_an_outlier"
REASON_TOO_RARE = "too_rare"
REASON_TOO_FEW_OTHERS = "too_few_other_values"
REASON_KEPT_BY_USER = "kept_by_you"

# What a declared value is compared with, recorded inside every profile
# so that a reader never has to guess which rule removed a value.
DECLARATION_MATCHING = "exact_number_when_it_reads_as_one_else_spelling"

# What `profile_column` says when one value is named both ways. The
# command says it in its own words, because it can name the two options
# the person typed.
CONTRADICTORY_DECLARATION = (
    "the same value cannot be both kept as data and read as 'no value'"
)


@dataclasses.dataclass(frozen=True)
class Settings:
    """The decisions the taxonomy is made of, in one place (plan P1-D4).

    Every one of these travels inside the profile, so a reader of a
    profile never has to guess which version of the rules produced it.

    ONE VALUE NAMED BOTH WAYS IS REFUSED, never resolved. There is no
    reading of `--keep-value -999 --missing-value -999.0` that is not a
    guess, and a guess between two contradictory instructions is exactly
    what a person cannot check afterwards (review item P1-R6-F9). The
    refusal happens twice, on the two paths that exist: the command
    refuses it before it opens the table, and `profile_column` raises
    ValueError before it describes anything. It is not done in a
    `dataclass` hook because the offline policy accepts no
    double-underscore name in this source (plan D6.2), so the check is
    `contradictory_declarations`, called by both.
    """

    small_cell_floor: int = 11
    # How different a column's values have to be before synthtwin SAYS
    # SO. This decides no role. Nothing decides the identifier role but
    # the person who owns the table, so this threshold governs one thing
    # only: whether that person is told their column never repeats, and
    # pointed at --identifier in case it holds record numbers (review
    # item P1-R6-F8).
    identifier_uniqueness: float = 0.95
    # Below this many rows, "every value is different" means nothing --
    # in a short column almost every measurement is all-different -- so
    # nothing is said about it. Like the threshold above, this decides
    # no role: it decides when a sentence is worth printing.
    identifier_minimum_rows: int = 20
    # THE line for the numeric roles AND for the datetime role, and the
    # only one. At least this share of the present values must read as
    # numbers this format can hold before the column is described as
    # numbers, and at least this share must parse under one date format
    # before it is described as dates. Applied as a COUNT, never as a
    # compared share, so no rounding of a division decides a role.
    #
    # A second line at half the values stood beside this one until
    # review item P1-R6-F7 and is deleted: it published a mean over
    # sixty numbers while dropping forty notes out of the distribution.
    minimum_parse_rate: float = 0.99
    # A set of categories is a set of values each shared by many rows.
    # The most different values one may hold is
    # `min(categorical_ceiling, categorical_share of the table's ROWS)`,
    # and never fewer than `categorical_floor`, so that a tiny table
    # still has a categorical path. Rows rather than present values:
    # `_categorical_ceiling` applies the rule and says why. A column
    # above that ceiling is described as free text, which publishes
    # nothing, and is told its own distinct count and the ceiling it
    # passed.
    categorical_share: float = 0.10
    categorical_ceiling: int = 1000
    categorical_floor: int = 2
    sentinel_outlier_iqr_multiple: float = 4.0
    sentinel_minimum_share: float = 0.005
    # What the person running the tool declared with --keep-value and
    # --missing-value. `kept_values` are real data whatever the rules
    # would have said (a region genuinely coded `NA`);
    # `declared_missing_values` are "no value" whatever the rules would
    # have said.
    #
    # ONE RULE SAYS WHAT EITHER OF THEM MATCHES, and it is recorded in
    # `declaration_matching`: a declared value that reads as a number
    # this format can hold matches every cell holding that EXACT NUMBER,
    # whatever either is spelled like, so `-999` covers a file that
    # writes `-999.00`; any other declared value matches by spelling,
    # after trimming and case folding. Naming one value both ways is
    # refused, never resolved by an order of precedence nobody can see.
    # Building this class does not itself refuse it -- the class
    # docstring says why, and names the two callers that do.
    #
    # The number comparison is on the number itself and not on the
    # binary64 value it rounds to. Rounding first makes one number out
    # of two, and then a declaration reaches cells nobody named (review
    # item P1-R7-F3).
    kept_values: tuple[str, ...] = ()
    declared_missing_values: tuple[str, ...] = ()
    # The rule above, written into the profile beside HOW MANY values
    # were named each way. A reader of a profile that records fifteen
    # values removed by a declaration must be able to see WHICH
    # comparison removed them. The declared spellings do not travel in
    # the SETTINGS BLOCK: they are values of the real table, so that
    # block carries their count and never their text (review item
    # P1-R7-F2, applied in `profile._declaration_record`).
    #
    # That is a statement about the settings block and nothing else. The
    # wider reading -- that a declared spelling reaches no part of the
    # document -- is false and was retired with the token that carried
    # it: a value declared KEPT is data from that point on and appears
    # wherever its column publishes values, and a value declared MISSING
    # reaches `missing_by_source` when its count clears the small-cell
    # floor and its column publishes at all. See the note beside
    # `profile.DECLARATION_PUBLICATION`.
    declaration_matching: str = DECLARATION_MATCHING
    # A column is reported as borderline when this many values, or
    # fewer, separate it from a different reading. Counting values
    # rather than comparing shares keeps the report meaningful at the
    # ends of the scale: a column where every value parses is not
    # "close to the line", while one where a single extra bad value
    # would have changed its role is.
    near_threshold_slack: int = 1


@dataclasses.dataclass(frozen=True)
class ColumnProfile:
    """One column's description, ready to be written into the profile.

    Every field below the details block is present on EVERY role,
    because it is a field of this class rather than a key some branch
    remembered to add. A count that appears only on the roles someone
    remembered is a count that goes missing exactly when it matters
    (review items P1-R1-F9, P1-R3-F3).
    """

    name: str
    position: int
    role: str
    detection_evidence: str
    n_present: int
    n_missing: int
    # Exact source spellings, published only for a role whose values may
    # appear at all, and only at or above the small-cell floor.
    missing_by_source: dict[str, int]
    # The named classes a missing cell fell into. These are synthtwin's
    # own words, so this mapping is safe on every role and is always
    # written in full.
    missing_by_class: dict[str, int]
    details: dict[str, object]
    publication_notes: list[str]
    remarks: list[str]
    # The one classification of the column's cells, as counts. Present
    # on every role, and they always add up to n_present.
    n_numeric: int = 0
    n_out_of_range: int = 0
    n_contradictory: int = 0
    n_not_numeric: int = 0
    # How many different values there are, counted both ways: raw, and
    # after trimming and case folding. Two different answers is exactly
    # the fact that says a column varies only in case.
    n_distinct: int = 0
    n_distinct_folded: int = 0
    # What was decided about each numeric sentinel that occurred, and
    # how many candidates were too rare to name at all. On a role that
    # publishes no values the decision, the reason and the row count
    # survive and the candidate reads `(withheld)`: the reader still
    # sees that a decision happened and which way it went, and no
    # spelling of a value leaves with it (review item P1-R7-F2).
    sentinel_verdicts: list[dict[str, object]] = dataclasses.field(
        default_factory=list
    )
    n_sentinel_candidates_unpublished: int = 0


SIGNIFICAND_BITS = 53

SMALLEST_EXPONENT = -1074

_SIGNIFICAND_CEILING = 1 << SIGNIFICAND_BITS

# The largest finite binary64 number, written as the exact whole numbers
# it is made of: a significand of 53 ones times two to the 971st. Having
# it as whole numbers is what lets "too large for this format" be
# decided by an exact comparison instead of by waiting for a rounding
# step to complain (review item P1-R6-F3).
LARGEST_FINITE_SIGNIFICAND = _SIGNIFICAND_CEILING - 1

LARGEST_FINITE_EXPONENT = 971

# A guess wide enough that the first integer square root always
# has at least as many digits as a significand needs.
_SIXTY_FOUR_DIGITS = 1 << 64

def _bits(value: int) -> int:
    """How many binary digits a whole number of zero or more has.

    `int.bit_length` says the same thing in one step, but the offline
    policy accepts no method call on a computed value (plan D6.2), so
    the digits are counted here: sixty-four at a time while that is
    possible, then one at a time. The numbers this is asked about are a
    few thousand digits long at the very worst, so the cost never
    matters.

    Guarantees: accepts a whole number of zero or more; returns 0 for
    zero and otherwise the position of its highest set digit. Raises
    nothing. No I/O of any kind.
    """
    total = 0
    rest = value
    while rest >= _SIXTY_FOUR_DIGITS:
        rest = rest >> 64
        total = total + 64
    while rest > 0:
        rest = rest >> 1
        total = total + 1
    return total

def _root_of(value: int) -> int:
    """The whole part of the square root of a whole number.

    Newton's method on whole numbers. The first guess is the smallest
    power of two at or above the true root, so the sequence falls
    towards the answer and never below it; the step that fails to fall
    is the one that has arrived. Every step is exact whole-number
    arithmetic, so the result is the same on every platform.

    Guarantees: accepts a whole number of zero or more; returns the
    largest whole number whose square is at most ``value``. Raises
    nothing. No I/O of any kind.
    """
    if value < 2:
        return value
    guess = 1 << ((_bits(value) + 1) // 2)
    while True:
        nearer = (guess + value // guess) // 2
        if nearer >= guess:
            return guess
        guess = nearer

def _over_two(top: int, bottom: int, twos: int) -> "tuple[int, int]":
    """``top * 2 ** twos / bottom`` written as one pair of whole numbers."""
    if twos >= 0:
        return top << twos, bottom
    return top, bottom << -twos

def _quotient_pair(top: int, bottom: int, exponent: int) -> "tuple[int, int]":
    """The pair whose quotient is ``top / bottom`` divided by 2 ** exponent."""
    if exponent >= 0:
        return top, bottom << exponent
    return top << -exponent, bottom

def _root_pair(top: int, bottom: int, exponent: int) -> "tuple[int, int]":
    """The pair whose square root is that of ``top / bottom`` over 2 ** exponent."""
    if exponent >= 0:
        return top, bottom << (exponent + exponent)
    return top << (-exponent - exponent), bottom

def _rounded_ratio(numerator: int, denominator: int) -> float:
    """The binary64 number nearest to one whole number over another.

    This is the module's single rounding step, and it is the correctly
    rounded one: the significand is the exact whole-number quotient at
    the right power of two, and the last digit is decided by comparing
    twice the exact remainder against the divisor -- greater rounds up,
    equal is a tie and goes to the even significand. Nothing but whole
    numbers is compared, so the answer does not depend on the processor.

    The exponent starts one estimate away: a quotient has the difference
    of the two digit counts, give or take one, so the first quotient has
    53 or 54 digits and at most one correction is needed. It is never
    allowed below -1074, which is what makes the subnormal results come
    out with the digits they really have instead of being rounded twice.

    Guarantees: accepts whole numbers with ``denominator`` above zero;
    returns the nearest binary64 value to ``numerator / denominator``,
    ties to even, exactly and on every platform. Raises OverflowError
    when that value is larger than binary64 can hold -- the caller
    decides what to say about it. No I/O of any kind.
    """
    if numerator == 0:
        return 0.0
    negative = numerator < 0
    top = -numerator if negative else numerator
    exponent = max(
        _bits(top) - _bits(denominator) - SIGNIFICAND_BITS, SMALLEST_EXPONENT
    )
    above, below = _quotient_pair(top, denominator, exponent)
    digits = above // below
    if digits >= _SIGNIFICAND_CEILING:
        exponent = exponent + 1
        above, below = _quotient_pair(top, denominator, exponent)
        digits = above // below
    rest = above - digits * below
    twice = rest + rest
    if twice > below or (twice == below and digits % 2 == 1):
        digits = digits + 1
    if digits >= _SIGNIFICAND_CEILING:
        digits = digits >> 1
        exponent = exponent + 1
    size = math.ldexp(float(digits), exponent)
    return -size if negative else size

def _rounded_root(numerator: int, denominator: int) -> float:
    """The binary64 number nearest to the square root of a fraction.

    The same single rounding step as `_rounded_ratio`, for the square
    root instead of the quotient. The significand is the whole-number
    square root at the right power of two, and the last digit is decided
    by comparing the fraction against the SQUARE of the midpoint between
    the two candidate results -- an exact comparison of whole numbers,
    the square of `2 * digits + 1` times `below` against four times
    `above`, so a value sitting exactly on a midpoint is recognised as
    the tie it is and goes to the even significand.

    Guarantees: accepts whole numbers with ``numerator`` at or above
    zero and ``denominator`` above zero; returns the nearest binary64
    value to the square root of ``numerator / denominator``, ties to
    even, exactly and on every platform. Raises OverflowError when that
    value is larger than binary64 can hold. No I/O of any kind.
    """
    if numerator == 0:
        return 0.0
    halved = (_bits(numerator) - _bits(denominator) - 1) // 2
    exponent = max(halved - SIGNIFICAND_BITS, SMALLEST_EXPONENT)
    above, below = _root_pair(numerator, denominator, exponent)
    digits = _root_of(above // below)
    # The estimate above is deliberately low, so the first root has 53,
    # 54 or 55 digits; its digit count says exactly how far to move.
    extra = _bits(digits) - SIGNIFICAND_BITS
    if extra > 0:
        exponent = exponent + extra
        above, below = _root_pair(numerator, denominator, exponent)
        digits = _root_of(above // below)
    midpoint = digits + digits + 1
    gap = below * midpoint * midpoint - (above + above + above + above)
    if gap < 0 or (gap == 0 and digits % 2 == 1):
        digits = digits + 1
    if digits >= _SIGNIFICAND_CEILING:
        digits = digits >> 1
        exponent = exponent + 1
    return math.ldexp(float(digits), exponent)

def _root_beyond_binary64(numerator: int, denominator: int) -> bool:
    """True when the square root of a fraction is too large to hold.

    The question is asked about the SQUARE, on whole numbers, BEFORE
    anything is rounded: the square root of ``numerator / denominator``
    is larger than the largest finite binary64 number exactly when
    ``numerator`` is larger than that number squared times
    ``denominator``. Nothing but whole numbers is compared, so the
    answer is the same on every platform, and it is the exact answer
    rather than an answer about a rounded stand-in.

    Asking afterwards -- by letting the rounding step complain -- is not
    the same question. An exact value sitting between the largest finite
    number and the point where rounding overflows rounds DOWN onto that
    largest finite number, correctly and without complaint, so a spread
    that had saturated was published as an ordinary finite maximum with
    nothing to say so (review item P1-R6-F3).

    Guarantees: accepts whole numbers with ``numerator`` at or above
    zero and ``denominator`` above zero; returns a truth value. Raises
    nothing. No I/O of any kind.
    """
    largest = LARGEST_FINITE_SIGNIFICAND << LARGEST_FINITE_EXPONENT
    return numerator > largest * largest * denominator


def _parts(value: float) -> "tuple[int, int]":
    """A finite number split into a whole significand and a power of two.

    Every finite binary64 value is a whole number of at most 53 binary
    digits times a power of two. `math.frexp` puts the significand in
    [0.5, 1) and reports that power, and shifting the significand up by
    53 places with `math.ldexp` lands it exactly on a whole number: the
    shift cannot overflow or underflow from that interval, and no
    significand carries more than 53 digits, so nothing is rounded. It
    holds for the subnormal values near zero too, which is what makes
    the smallest steps arithmetic here rather than something rounded
    away.

    Guarantees: accepts a finite number; returns the pair
    ``(significand, exponent)`` with
    ``value == significand * 2 ** (exponent - 53)`` exactly, and
    ``(0, 0)`` for either zero. Raises nothing. No I/O of any kind.
    """
    fraction, exponent = math.frexp(value)
    return int(math.ldexp(fraction, SIGNIFICAND_BITS)), exponent

def _totals(numbers: list[float]) -> "tuple[int, int, int, int]":
    """The exact sums of the values, of their squares, and of their cubes.

    Returns ``(total, squares, cubes, base)``, where the values are
    ``a_1 ... a_n`` measured in units of ``2 ** base``:
    ``sum(x) == total * 2 ** base``,
    ``sum(x * x) == squares * 2 ** (2 * base)`` and
    ``sum(x * x * x) == cubes * 2 ** (3 * base)``. All four are whole
    numbers and all three sums are EXACT -- that is the whole point of
    the module docstring's one rule.

    Values are added up in groups sharing one power of two, and each
    group is shifted onto the common unit once, after its own sum. This
    is a regrouping of a sum of whole numbers, which is exact whatever
    the grouping is, and it keeps the arithmetic on numbers the size of
    a significand instead of numbers the size of the column's whole
    dynamic range: a column mixing 1e-300 with 1e300 would otherwise
    carry two thousand binary digits into every one of its
    multiplications. There are at most 2099 groups, because that is how
    many exponents a binary64 number has.

    Zeros contribute nothing to any of the three sums and are skipped,
    so a zero never drags the shared unit down and inflates every other
    value's digits for nothing.

    Guarantees: accepts a list of finite numbers, in any order; returns
    the four whole numbers above, and the same four whatever order the
    values arrive in, because whole-number addition is associative and
    commutative. Raises nothing. No I/O of any kind.
    """
    ones: dict[int, int] = {}
    squares: dict[int, int] = {}
    cubes: dict[int, int] = {}
    smallest = SIGNIFICAND_BITS
    started = False
    for value in numbers:
        significand, exponent = _parts(value)
        if significand == 0:
            continue
        if started:
            smallest = min(smallest, exponent)
        else:
            smallest = exponent
            started = True
        square = significand * significand
        if exponent in ones:
            ones[exponent] = ones[exponent] + significand
            squares[exponent] = squares[exponent] + square
            cubes[exponent] = cubes[exponent] + square * significand
        else:
            ones[exponent] = significand
            squares[exponent] = square
            cubes[exponent] = square * significand
    total = 0
    total_squares = 0
    total_cubes = 0
    # Sorted, so that the order the groups are added in is a property of
    # the values and not of the rows -- the sum is the same either way,
    # and this way a reader can see that it is.
    for exponent in sorted(ones):
        shift = exponent - smallest
        total = total + (ones[exponent] << shift)
        total_squares = total_squares + (squares[exponent] << (shift + shift))
        total_cubes = total_cubes + (
            cubes[exponent] << (shift + shift + shift)
        )
    return total, total_squares, total_cubes, smallest - SIGNIFICAND_BITS


def published(value: float) -> "float | None":
    """Prepare one computed number for the profile.

    The value is published exactly as computed, in its shortest form
    that reads back as the same number. An earlier revision rounded
    every number to twelve significant digits to hide differences
    between machines; that destroyed real data -- ten values around
    1e15 all collapsed onto one, so the profile said the range was zero
    while also reporting a spread -- and it has been replaced by making
    the computation itself machine-independent (see the module
    docstring and plan P1-D11).

    Guarantees: accepts a float; returns it unchanged, or None when it
    is not finite (an infinity or a not-a-number never reaches the
    profile, where it would not even be valid JSON). Negative zero is
    normalised to zero so that the order of the rows cannot change the
    bytes. Raises nothing. No I/O of any kind.
    """
    if not math.isfinite(value):
        return None
    if value == 0.0:
        return 0.0
    return value


def _share(part: int, whole: int) -> float:
    """``part`` divided by ``whole``, with zero standing in for 0/0."""
    if whole <= 0:
        return 0.0
    return part / whole


def _needed(share: float, total: int) -> int:
    """The smallest whole number of values that reaches ``share``.

    Thresholds are applied as counts rather than as compared shares, so
    that no rounding of a division can decide a column's role.
    """
    exact = share * total
    whole = int(exact)
    if whole < exact:
        return whole + 1
    return whole


def _at_most(share: float, total: int) -> int:
    """The largest whole number of values that stays within ``share``.

    The ceiling counterpart of `_needed`, and a count for the same
    reason: `distinct <= 10% of the values` is decided by comparing two
    whole numbers, so no rounding of a division decides a role.
    """
    exact = share * total
    whole = int(exact)
    if whole > exact:
        return whole - 1
    return whole


def _barely_above(count: int, needed: int, slack: int) -> bool:
    """True when ``count`` cleared ``needed`` by ``slack`` or fewer."""
    return needed <= count <= needed + slack


def _barely_below(count: int, needed: int, slack: int) -> bool:
    """True when ``count`` fell short of ``needed`` by ``slack`` or fewer."""
    return needed - slack <= count < needed


def _lengths(values: list[str]) -> list[int]:
    """The character length of every value."""
    return [len(value) for value in values]


def _quantile(ordered: list[float], num: int, den: int) -> float:
    """One rung of the ladder, by linear interpolation between neighbours.

    The position is computed in whole numbers -- ``(n - 1) * num`` split
    by ``den`` -- so no binary spelling of a decimal fraction can move a
    rung onto the wrong pair of values.

    The rung itself is computed in whole numbers too. Written out, it is
    ``((den - rest) * below + rest * above) / den``, and with both
    neighbours expressed as whole numbers of one shared power of two
    that whole expression is an exact fraction, rounded to a binary64
    value exactly once. Review item P1-R2-F4 found the arithmetic this
    replaces failing at both ends of the range: ``below + share *
    (above - below)`` lost the interpolation entirely between two
    neighbouring subnormal values, where the weighted gap is smaller
    than the smallest representable step, and it could overflow on a
    gap wider than binary64 can hold. Neither can happen to a fraction
    of whole numbers, and the result of this one always lies between
    the two neighbours, so it is always representable.

    Guarantees: accepts a non-empty list of finite numbers in
    non-decreasing order and a rung written as ``num / den``; returns
    the correctly rounded binary64 value of the exact interpolated rung.
    Raises nothing. No I/O of any kind.
    """
    count = len(ordered)
    if count == 1:
        return ordered[0]
    steps = (count - 1) * num
    lower = steps // den
    rest = steps - lower * den
    if lower >= count - 1:
        return ordered[count - 1]
    below = ordered[lower]
    if rest == 0:
        return below
    above = ordered[lower + 1]
    below_significand, below_exponent = _parts(below)
    above_significand, above_exponent = _parts(above)
    smallest = min(below_exponent, above_exponent)
    weighted = (den - rest) * (
        below_significand << (below_exponent - smallest)
    ) + rest * (above_significand << (above_exponent - smallest))
    numerator, denominator = _over_two(
        weighted, den, smallest - SIGNIFICAND_BITS
    )
    return _rounded_ratio(numerator, denominator)


def _quantiles(numbers: list[float]) -> dict[str, "float | None"]:
    """The eleven-point percentile ladder of ``numbers``."""
    ordered = sorted(numbers)
    ladder: dict[str, float | None] = {}
    for label, num, den in LADDER:
        ladder[label] = published(_quantile(ordered, num, den))
    return ladder


def _ordinal_rung(ordered: list[str], num: int, den: int) -> str:
    """One rung of the ladder over values that cannot be averaged.

    There is no half-way point between two dates that a calendar would
    recognise, so this picks the value at the rung rather than
    interpolating. Selecting rather than interpolating is what makes the
    eleven rungs of a date column meaningful.
    """
    count = len(ordered)
    if count == 1:
        return ordered[0]
    steps = (count - 1) * num
    lower = steps // den
    if lower >= count - 1:
        return ordered[count - 1]
    return ordered[lower]


def _date_ladder(ordered: list[str]) -> dict[str, str]:
    """The eleven-point ladder of a datetime column, as canonical text."""
    ladder: dict[str, str] = {}
    for label, num, den in LADDER:
        ladder[label] = _ordinal_rung(ordered, num, den)
    return ladder




def _moments(numbers: list[float]) -> dict[str, "float | None"]:
    """Mean, standard deviation and skewness of ``numbers``.

    The standard deviation is the sample one (divided by n-1) and is
    undefined -- written as null -- for a single value. Skewness is the
    moment-based measure: the average cubed deviation divided by the
    cube of the population standard deviation. It is undefined, and
    written as null, when every value is identical or fewer than three
    values are present, because there is no shape to report.

    A null standard deviation therefore means "undefined". A spread too
    large for this format to hold is a different fact and is reported as
    its own field, `std_unrepresentable`, so that a reader never has to
    guess which of the two happened. Which of the two it is, is settled
    on the EXACT variance against the exact square of the largest finite
    number, before anything is rounded: an exact spread just above that
    number rounds quietly down onto it, so a saturated spread was
    published as an ordinary finite maximum for as long as the flag
    waited for a rounding step to overflow (review item P1-R6-F3).

    HOW THE THREE ARE COMPUTED (plan P1-D11). Write every value as a
    whole number of one shared power of two, ``x_i = a_i * 2 ** base``.
    With ``n`` values, ``T1 = sum a_i``, ``T2 = sum a_i * a_i`` and
    ``T3 = sum a_i * a_i * a_i`` -- all exact, all order-independent --
    the three statistics are exact fractions of whole numbers:

        mean       = T1 * 2 ** base / n
        variance   = V2 * 2 ** (2 * base) / (n * (n - 1))
        skewness   = sign(V3) * sqrt(V3 * V3 / (V2 * V2 * V2))

    where ``V2 = n * T2 - T1 * T1`` is ``n`` squared times the second
    central moment and
    ``V3 = n * n * T3 - 3 * n * T1 * T2 + 2 * T1 * T1 * T1`` is ``n``
    cubed times the third, each cleared of its denominator. In the
    skewness the shared power of two and every factor of ``n`` cancel
    between the numerator and the denominator, exactly, which is why no
    scaling appears in it at all. Each of the three is then rounded to
    binary64 exactly once.

    That is what retires the conditioning limit revision 1 recorded for
    a sample like {1e16, 1, -1e16}: the third moment of that sample
    cancels by a factor of 1e32, which is beyond what binary64 can carry
    but nothing at all to whole numbers, so the published skewness is
    now the correctly rounded exact one.

    ``V2`` is zero exactly when every value is identical, which is the
    one case where there is no shape to report, so the same test serves
    for both the zero spread and the undefined skewness.

    Guarantees: accepts a non-empty list of finite numbers, in any
    order; returns a dict whose "mean", "std" and "skew" are each the
    correctly rounded binary64 value of the exact statistic, or None
    where the statistic is undefined, plus "std_unrepresentable", which
    is present on EVERY result and is true when and only when the exact
    spread is larger than binary64 can hold. It is present either way
    because a fact a reader has to have is not a fact that appears only
    on the branch someone remembered: a null "std" beside no flag at all
    is a reader guessing which of the two things happened. The result
    depends on the multiset of values and nothing else, so the row order
    cannot change it. Raises nothing. No I/O of any kind.
    """
    count = len(numbers)
    moments: dict[str, float | None] = {
        "mean": None,
        "std": None,
        "skew": None,
        "std_unrepresentable": False,
    }
    total, squares, cubes, base = _totals(numbers)
    numerator, denominator = _over_two(total, count, base)
    moments["mean"] = published(_rounded_ratio(numerator, denominator))
    if count < 2:
        return moments

    # n squared times the second central moment, cleared of its
    # denominator. It is zero exactly when every value is the same one.
    spread = count * squares - total * total
    if spread == 0:
        moments["std"] = 0.0
        return moments
    numerator, denominator = _over_two(
        spread, count * (count - 1), base + base
    )
    if _root_beyond_binary64(numerator, denominator):
        # The spread is larger than this format can hold. Reported as a
        # fact of its own rather than as a bare null, which would be
        # indistinguishable from "undefined".
        #
        # The test is on the EXACT variance against the exact square of
        # the largest finite number, so it catches every spread the
        # format cannot hold -- including the ones that round quietly
        # DOWN onto that largest finite number instead of overflowing.
        # Three values at about 1.5568479229996504e+308 have exactly
        # such a spread, and they used to publish
        # 1.7976931348623157e+308 as an ordinary standard deviation
        # (review item P1-R6-F3).
        moments["std"] = None
        moments["std_unrepresentable"] = True
    else:
        moments["std"] = published(_rounded_root(numerator, denominator))
    if count < 3:
        return moments

    # n cubed times the third central moment, cleared likewise. The
    # skewness is its sign times the square root of shape * shape over
    # spread cubed: the shared power of two and every factor of n
    # cancel between the two, so this fraction is the whole story.
    shape = (
        count * count * cubes
        - 3 * count * total * squares
        + 2 * total * total * total
    )
    size = _rounded_root(shape * shape, spread * spread * spread)
    moments["skew"] = published(-size if shape < 0 else size)
    return moments


# -- the exact number a spelling denotes ------------------------------
#
# WHY THIS EXISTS AT ALL. A declared value is compared with a cell by
# the NUMBER both of them denote, not by the way either is written, so
# that `--keep-value -999` covers a file that writes `-999.00`. Round 6
# did that comparison on the binary64 value each side rounded to, and a
# rounded value is not the number: two decimal spellings that are
# different numbers can round to one binary64 value, and then a cell
# nobody named was removed as though it had been named, and two
# declarations naming two different numbers were refused as though they
# were one (review item P1-R7-F3). So the comparison is on the exact
# number instead -- whole numbers only, no rounding anywhere in it, the
# same rule the statistics above already work under.
#
# THE FORM. A decimal spelling denotes `sign * digits * 10 ** power`.
# Written as `(sign, digits, power)` with the digits stripped of both
# leading and trailing zeros, that triple is CANONICAL: two spellings
# denote the same number exactly when their triples are equal, so the
# comparison is `==` on the triple and nothing more. Zero has one
# triple, `(0, (), 0)`, which is what makes `0` and `-0` one number.
# The digits are kept as a tuple of characters rather than as one whole
# number on purpose: a cell may hold a spelling with tens of thousands
# of digits, and building the whole number it denotes would cost time
# quadratic in that length, while comparing two tuples costs its length.

_EXACTLY_ZERO: "tuple[int, tuple[str, ...], int]" = (0, (), 0)

_ASCII_ZERO = ord("0")


def _exact_digits(text: str) -> "tuple[int, tuple[str, ...], int]":
    """The canonical triple of a spelling ALREADY READ AS A NUMBER.

    Asked only about text the reader of record has classified as a
    number this format can hold, which is what lets the scan below be
    arithmetic over the characters rather than a second opinion about
    what the cell is: nothing here decides whether a spelling is a
    number, so nothing here can disagree with the answer already given.

    Guarantees: accepts text the reader has accepted; returns the
    canonical triple denoting exactly that number; raises TypeError if
    handed anything that is not a string instance. No I/O of any kind.
    """
    body = parsing.trimmed(text)
    negative = False
    if body[:1] == "(" and body[len(body) - 1 : len(body)] == ")":
        # Accounting parentheses mean negative, and the reader has
        # already refused a sign inside them, so nothing can say
        # "negative" twice here.
        negative = True
        body = parsing.trimmed(body[1 : len(body) - 1])
    if body[:1] == "-":
        negative = True
        body = body[1:]
    elif body[:1] == "+":
        body = body[1:]
    # One pass over the characters. The digits are collected in order
    # with the leading zeros left out, the decimal places are counted,
    # and the exponent is added up after the `e`. A thousands separator
    # is none of those things and contributes nothing to the value, so
    # it falls through every branch, which is exactly right.
    digits: list[str] = []
    places = 0
    after_point = False
    in_exponent = False
    exponent_negative = False
    magnitude = 0
    for character in body:
        if in_exponent:
            if character == "-":
                exponent_negative = True
            elif "0" <= character <= "9" and len(digits):
                # The exponent is added up only while a digit that is
                # not a leading zero has been seen. That keeps `0e`
                # followed by a thousand nines cheap -- such a spelling
                # is zero whatever its exponent says -- and it is why
                # the magnitude below stays small: a spelling this
                # format can hold, whose digits are not all zeros, has
                # an exponent within a few hundred of the number of
                # digits written.
                magnitude = magnitude * 10 + (ord(character) - _ASCII_ZERO)
        elif "0" <= character <= "9":
            if after_point:
                places = places + 1
            if character != "0" or len(digits):
                digits += [character]
        elif character == ".":
            after_point = True
        elif character == "e" or character == "E":
            in_exponent = True
    if not len(digits):
        return _EXACTLY_ZERO
    if exponent_negative:
        power = -places - magnitude
    else:
        power = -places + magnitude
    kept = len(digits)
    while kept > 0 and digits[kept - 1] == "0":
        kept = kept - 1
        power = power + 1
    return (-1 if negative else 1, tuple(digits[:kept]), power)


def _exact_value(text: str) -> "tuple[int, tuple[str, ...], int] | None":
    """The exact number a spelling denotes, or None when it denotes none.

    The reader of record decides FIRST whether the text is a number this
    format can hold: nothing is exact about a spelling the rest of the
    tool refuses, and asking the question here a second way is how two
    parts of one program come to disagree about what a value is.

    Guarantees: accepts text; returns the canonical triple described
    above, or None when the text does not read as a number this format
    can hold; raises TypeError if handed anything that is not a string
    instance. Two texts give equal triples exactly when they denote the
    same number. No I/O of any kind.
    """
    if parsing.classify_number(text) != parsing.NUMBER:
        return None
    return _exact_digits(text)


def _exact_number(value: float) -> "tuple[int, tuple[str, ...], int]":
    """The same canonical triple, for a number already held as binary64.

    A finite binary64 value is a whole significand times a power of two,
    which `_parts` gives exactly, and a power of two is a whole number
    of tenths, hundredths and so on: multiplying by five as often as the
    power of two is negative turns it into a whole number of decimal
    places with nothing rounded. The digit count stays under about eight
    hundred for every finite value this format holds, which is what
    makes writing the whole number out affordable here.

    Guarantees: accepts a finite number; returns the canonical triple
    denoting exactly that number. Raises nothing. No I/O of any kind.
    """
    significand, exponent = _parts(value)
    if significand == 0:
        return _EXACTLY_ZERO
    negative = significand < 0
    top = -significand if negative else significand
    twos = exponent - SIGNIFICAND_BITS
    if twos >= 0:
        whole = top << twos
        power = 0
    else:
        whole = top * (5 ** -twos)
        power = twos
    written = f"{whole}"
    kept = len(written)
    while kept > 0 and written[kept - 1 : kept] == "0":
        kept = kept - 1
        power = power + 1
    return (-1 if negative else 1, tuple(written[:kept]), power)


# -- the one cell record --------------------------------------------


@dataclasses.dataclass(frozen=True)
class _Cell:
    """One present cell, decided once and never read from the text again.

    This is the record STRUCTURAL RULE A is about. It is built by
    `_classify`, once per cell, and it is frozen: what a cell is
    numerically, the number it parsed to, that same number exactly, its
    sign, whether it is a whole number, and the lexical facts the role
    rules ask about.

    It carried two more lexical facts until review item P1-R6-F8 --
    whether the cell was one word, and whether it held a letter -- and
    they existed for one purpose: guessing which all-different columns
    were record numbers. That guess is withdrawn, so the facts that fed
    it are gone rather than left lying about for a later rule to pick
    up again.

    Everything below consults this record. Round 5's code asked the
    parser three separate questions per cell -- classify, sign,
    whole-number -- and the last two classified the cell again from its
    text, so "classified exactly once" was a comment rather than a
    property of the code (review item P1-R6-F10).
    """

    text: str
    # One of parsing.NUMBER, NUMBER_OUT_OF_RANGE, NUMBER_CONTRADICTORY,
    # NOT_A_NUMBER.
    kind: str
    # The number the cell holds, and None whenever no number was held.
    value: "float | None"
    # The same number EXACTLY, as the canonical triple above, and None
    # whenever no number was held. `value` is what the profile publishes
    # and what the statistics are computed from; this is what a declared
    # value is compared with, and what the numeric-sentinel rule decides
    # a candidate's own cells by, because a comparison of rounded values
    # makes one number out of two (review items P1-R7-F3 and P1-R8-F2).
    exact: "tuple[int, tuple[str, ...], int] | None"
    sign: str
    whole: str
    # The cell after trimming and case folding: the key the levels, the
    # binary rule and the categorical rule all count with.
    folded: str
    # Both of these are published as COUNTS on a free-text column, which
    # is what a generator needs to build text of the same shape. Neither
    # decides a role.
    all_digits: bool
    code_alphabet: bool


def _written_negative(text: str) -> bool:
    """True when the NOTATION of a well-formed number says "negative".

    Asked only about a cell already classified as a number too large or
    too small for this format to hold, where there is no value left to
    read the sign from. Two marks say negative, and they are the two the
    reader accepts: accounting parentheses around the value, and a
    leading minus. Such a cell can carry only one of them -- a sign
    INSIDE parentheses is contradictory notation, which is a different
    kind of cell entirely -- so reading both is safe.

    Guarantees: accepts text; returns a truth value. Raises nothing.
    No I/O of any kind.
    """
    body = parsing.trimmed(text)
    negative = False
    if body[:1] == "(" and body[len(body) - 1 : len(body)] == ")":
        negative = True
        body = parsing.trimmed(body[1 : len(body) - 1])
    if body[:1] == "-":
        negative = True
    return negative


def _classify(text: str) -> _Cell:
    """Classify one present cell, once, into the record every rule reads.

    The parser is asked what the cell is exactly once. Everything else
    is derived from that answer:

    * a cell this format can hold has its sign and its whole-number
      status settled by the NUMBER it parsed to -- a parsed zero is
      exactly a cell whose digits are all zeros, because a value that
      collapses to zero from something larger is refused by the reader
      and comes back as out-of-range instead -- and it carries the exact
      number its spelling denotes beside the rounded one, so that a
      declared value is compared with the number and not with a rounding
      of it;
    * a cell too large or too small to hold has no value to read, so its
      whole-number status comes from which end of the range it fell off
      (too large is whole, too small lies strictly between zero and one)
      and its sign from the notation;
    * contradictory notation and ordinary text settle neither, and
      "unknown" is a real answer here, never guessed at.

    Guarantees: accepts text; returns a frozen `_Cell`; raises TypeError
    if handed anything that is not a string instance. The record depends
    on the text and nothing else. No I/O of any kind.
    """
    kind = parsing.classify_number(text)
    value: float | None = None
    exact: tuple[int, tuple[str, ...], int] | None = None
    sign = parsing.SIGN_UNKNOWN
    whole = parsing.WHOLE_UNKNOWN
    if kind == parsing.NUMBER:
        value = parsing.parse_number(text)
        exact = _exact_digits(text)
        if value is not None:
            if value < 0.0:
                sign = parsing.SIGN_NEGATIVE
            elif value == 0.0:
                sign = parsing.SIGN_ZERO
            else:
                sign = parsing.SIGN_POSITIVE
            if parsing.is_whole_number(value):
                whole = parsing.WHOLE_YES
            else:
                whole = parsing.WHOLE_NO
    elif kind == parsing.NUMBER_OUT_OF_RANGE:
        if parsing.overflowed(text):
            whole = parsing.WHOLE_YES
        else:
            whole = parsing.WHOLE_NO
        if _written_negative(text):
            sign = parsing.SIGN_NEGATIVE
        else:
            sign = parsing.SIGN_POSITIVE
    trimmed = parsing.trimmed(text)
    return _Cell(
        text=text,
        kind=kind,
        value=value,
        exact=exact,
        sign=sign,
        whole=whole,
        folded=parsing.folded(text),
        all_digits=parsing.is_digit_text(trimmed),
        code_alphabet=parsing.is_code_text(trimmed),
    )


@dataclasses.dataclass(frozen=True)
class _Cells:
    """Everything the role rules are allowed to consult, decided once.

    Nothing below this point re-reads a cell. Every rule reads these
    fields. That is what prevents one rule and the next from
    counting different sets of cells under the same name.
    """

    # The one classification of each present cell, in row order. Every
    # count below is a tally of these records, and dropping a numeric
    # sentinel drops records from this list -- the column is never read
    # a second time.
    classified: list[_Cell]
    present: list[str]
    n_rows: int
    settings: Settings
    numbers: list[float]
    n_out_of_range: int
    n_contradictory: int
    n_not_numeric: int
    n_negative: int
    n_positive: int
    n_sign_unknown: int
    n_whole: int
    n_fraction: int
    n_whole_unknown: int
    n_negative_unrepresentable: int
    raw_distinct: int
    folded_counts: dict[str, int]
    all_digits: int
    code_alphabet: int


def _classify_all(present: list[str]) -> list[_Cell]:
    """Classify every present cell exactly once, in row order."""
    return [_classify(value) for value in present]


def _tally(
    classified: list[_Cell], n_rows: int, settings: Settings
) -> _Cells:
    """Count the one classification of each cell, in one pass.

    This function reads the records and never the text: it is arithmetic
    over `_classify`'s answers. That is what lets a numeric sentinel be
    dropped by filtering the records and counting again, instead of
    reading the whole column a second time and hoping the second reading
    agrees with the first (review item P1-R6-F10).
    """
    present: list[str] = []
    numbers: list[float] = []
    out_of_range = 0
    contradictory = 0
    not_a_number = 0
    negative = 0
    positive = 0
    sign_unknown = 0
    whole = 0
    fraction = 0
    whole_unknown = 0
    negative_unrepresentable = 0
    all_digits = 0
    code_alphabet = 0
    folded_counts: dict[str, int] = {}
    for cell in classified:
        present += [cell.text]
        if cell.kind == parsing.NUMBER:
            if cell.value is not None:
                numbers += [cell.value]
        elif cell.kind == parsing.NUMBER_OUT_OF_RANGE:
            out_of_range = out_of_range + 1
        elif cell.kind == parsing.NUMBER_CONTRADICTORY:
            contradictory = contradictory + 1
        else:
            not_a_number = not_a_number + 1
        if cell.kind != parsing.NOT_A_NUMBER:
            if cell.sign == parsing.SIGN_NEGATIVE:
                negative = negative + 1
                if cell.kind != parsing.NUMBER:
                    negative_unrepresentable = negative_unrepresentable + 1
            elif (
                cell.sign == parsing.SIGN_POSITIVE
                or cell.sign == parsing.SIGN_ZERO
            ):
                positive = positive + 1
            else:
                sign_unknown = sign_unknown + 1
            if cell.whole == parsing.WHOLE_YES:
                whole = whole + 1
            elif cell.whole == parsing.WHOLE_NO:
                fraction = fraction + 1
            else:
                whole_unknown = whole_unknown + 1
        if cell.all_digits:
            all_digits = all_digits + 1
        if cell.code_alphabet:
            code_alphabet = code_alphabet + 1
        if cell.folded in folded_counts:
            folded_counts[cell.folded] = folded_counts[cell.folded] + 1
        else:
            folded_counts[cell.folded] = 1
    return _Cells(
        classified=classified,
        present=present,
        n_rows=n_rows,
        settings=settings,
        numbers=numbers,
        n_out_of_range=out_of_range,
        n_contradictory=contradictory,
        n_not_numeric=not_a_number,
        n_negative=negative,
        n_positive=positive,
        n_sign_unknown=sign_unknown,
        n_whole=whole,
        n_fraction=fraction,
        n_whole_unknown=whole_unknown,
        n_negative_unrepresentable=negative_unrepresentable,
        raw_distinct=len(set(present)),
        folded_counts=folded_counts,
        all_digits=all_digits,
        code_alphabet=code_alphabet,
    )


def _numeric_looking(cells: _Cells) -> int:
    """The cells whose writer meant a number, however it came out."""
    return (
        len(cells.numbers) + cells.n_out_of_range + cells.n_contradictory
    )


# -- missing values ---------------------------------------------------


@dataclasses.dataclass(frozen=True)
class _Declaration:
    """One value the person running the tool named, and what it names.

    `exact` is the EXACT number the declaration denotes, and None
    whenever it denotes no number this format can carry. Which of the
    two it is, is the whole of the matching rule: a declaration that
    names a number matches cells by that NUMBER and by nothing else; a
    declaration that names no number matches cells by SPELLING and by
    nothing else.

    The number is held exactly rather than as the binary64 value it
    rounds to. Rounding first makes one number out of two: two decimal
    spellings a person can tell apart at a glance can round to the same
    binary64 value, and then a declaration reached cells the person
    never named, and a pair of declarations naming two different numbers
    was refused as a contradiction (review item P1-R7-F3).
    """

    text: str
    folded: str
    exact: "tuple[int, tuple[str, ...], int] | None"


def _declarations(spellings: tuple[str, ...]) -> "list[_Declaration]":
    """Read each declared value once, into the record the rules compare.

    Guarantees: accepts the spellings a person typed; returns one record
    per spelling, in the order given. Raises TypeError if handed
    anything that is not text. No I/O of any kind.
    """
    made: list[_Declaration] = []
    for spelling in spellings:
        made += [
            _Declaration(
                text=spelling,
                folded=parsing.folded(spelling),
                exact=_exact_value(spelling),
            )
        ]
    return made


def _same_declaration(one: _Declaration, other: _Declaration) -> bool:
    """True when two declarations name the same thing, under the one rule."""
    if one.exact is not None and other.exact is not None:
        return one.exact == other.exact
    if one.exact is None and other.exact is None:
        return one.folded == other.folded
    return False


def contradictory_declarations(
    kept_values: "tuple[str, ...]", declared_missing_values: "tuple[str, ...]"
) -> "list[str]":
    """Every value named BOTH as data and as "no value", said in words.

    A person who writes `--keep-value -999 --missing-value -999.0` has
    asked for two opposite things about one number, and no order of
    precedence can turn that into what they meant. The pair is named
    here so that the caller can refuse it and say which two words
    clashed (review item P1-R6-F9).

    The comparison is the SAME one that decides what a declaration
    matches, so a pair this reports is exactly a pair that would have
    fought over the same cells: `-999` and `-999.00` are one number,
    `NA` and ` na ` are one spelling, and `-999` and `NA` are neither.
    It is also EXACT, so two numbers a person can tell apart are never
    reported as one: the pair reported here is a pair that is equal, not
    a pair that rounds to one binary64 value (review item P1-R7-F3).

    Guarantees: accepts the two lists of declared values; returns one
    plain sentence per clashing pair, in the order the kept values were
    given, and an empty list when nothing clashes. Raises TypeError if
    handed anything that is not text. No I/O of any kind.
    """
    kept = _declarations(kept_values)
    missing = _declarations(declared_missing_values)
    named: list[str] = []
    for one in kept:
        for other in missing:
            if not _same_declaration(one, other):
                continue
            if one.exact is None:
                how = "the same spelling"
            else:
                how = "the same number"
            named += [
                (
                    f"you asked to keep '{one.text}' and to read "
                    f"'{other.text}' as 'no value', and they are {how}"
                )
            ]
    return named


def _declared_spelling(
    text: str, declarations: "list[_Declaration]"
) -> bool:
    """True when a declaration that names no number matches this spelling."""
    folded = parsing.folded(text)
    for declaration in declarations:
        if declaration.exact is None and folded == declaration.folded:
            return True
    return False


def _declared_number(
    exact: "tuple[int, tuple[str, ...], int] | None",
    declarations: "list[_Declaration]",
) -> bool:
    """True when a declaration names EXACTLY the number handed in.

    The comparison is on the exact number both sides denote. Two
    spellings that denote different numbers never match here, however
    close together the binary64 values they round to are, and two
    spellings that denote one number always match, however differently
    they are written.

    Guarantees: accepts the canonical triple of the number in hand, or
    None when there is no number; returns a truth value. Raises nothing.
    No I/O of any kind.
    """
    if exact is None:
        return False
    for declaration in declarations:
        if declaration.exact is not None and exact == declaration.exact:
            return True
    return False


def _split_missing(
    values: list[str], settings: Settings
) -> "tuple[list[str], list[tuple[str, str]]]":
    """Split values into (present, [(exact spelling, named class), ...]).

    This is the first of the two steps that apply what the person
    declared, and it is the step that reads SPELLINGS: it overrules the
    documented table of missing spellings in both directions. A value
    named with `--keep-value` is data even though the table lists it --
    a region genuinely coded `NA` is a region, not a hole (review item
    P1-R1-F7) -- and a value named with `--missing-value` is a hole even
    though the table does not list it.

    The second step is `_declared_numbers_removed`, which runs on the
    classified cells, because a declaration that names a NUMBER has to
    be compared with the number a cell holds rather than with the way it
    is written. Nothing in the documented table of missing spellings
    reads as a number -- `tests/test_p1r6f9_declared_values.py` states
    that as a check of its own -- so no declared number is ever needed
    here to rescue a value from that table.

    Guarantees: accepts the column's cells as text; returns the values
    that are present and the pairs that are not, in row order. Raises
    TypeError if a value is not text. No I/O of any kind.
    """
    kept = _declarations(settings.kept_values)
    declared_missing = _declarations(settings.declared_missing_values)
    present: list[str] = []
    missing: list[tuple[str, str]] = []
    for value in values:
        if _declared_spelling(value, kept):
            present += [value]
        elif _declared_spelling(value, declared_missing):
            missing += [(value, parsing.MISSING_DECLARED)]
        elif not parsing.trimmed(value):
            missing += [(value, parsing.MISSING_BLANK)]
        elif parsing.is_missing_text(value):
            missing += [(value, parsing.MISSING_TEXT_CODE)]
        else:
            present += [value]
    return present, missing


def _declared_numbers_removed(
    classified: "list[_Cell]", settings: Settings
) -> "tuple[list[_Cell], list[tuple[str, str]]]":
    """Take out the cells whose NUMBER the person declared to be missing.

    The second of the two steps, and the one that closes review item
    P1-R6-F9's second half. It runs on the cells the column was
    classified into, BEFORE any role is decided and before the numeric
    sentinels are judged, so a declaration has its say ahead of every
    rule -- and it compares the number a cell holds, so `-999`,
    `-999.0`, `-999.00` and `(999)` are one declaration's business
    whichever of them the file writes.

    The number compared is the EXACT one, read from the cell's own
    record. Round 6 compared the binary64 values instead, and a column
    of two whole numbers one apart, with only one of them declared
    missing, lost every row of both (review item P1-R7-F3).

    A declared number that is KEPT needs nothing here: keeping is the
    default for any cell that reads as a number, and the one rule that
    would have removed it -- the numeric-sentinel rule -- asks the same
    question of the same declarations before it removes anything.

    Guarantees: accepts the classified present cells and the settings;
    returns the cells that survive, in row order, and the pairs that
    left. Raises nothing. No I/O of any kind.
    """
    declared_missing = _declarations(settings.declared_missing_values)
    numeric = [
        declaration
        for declaration in declared_missing
        if declaration.exact is not None
    ]
    if not numeric:
        return classified, []
    kept: list[_Cell] = []
    missing: list[tuple[str, str]] = []
    for cell in classified:
        if _declared_number(cell.exact, numeric):
            missing += [(cell.text, parsing.MISSING_DECLARED)]
        else:
            kept += [cell]
    return kept, missing


def _missing_maps(
    missing: list[tuple[str, str]], settings: Settings
) -> "tuple[dict[str, int], dict[str, int]]":
    """Both missing mappings, under the small-cell floor.

    `missing_by_class` uses only synthtwin's own five words, so it is
    safe on every role and is always written in full. An exact source
    spelling reaches `missing_by_source` only when at least
    `small_cell_floor` rows share that spelling; everything else is
    pooled, unnamed, into `(withheld)`.

    THE ROLE IS NOT CONSULTED HERE. This function used to hold half of
    the publication rule as well -- an early return that emptied
    `missing_by_source` for a role that publishes nothing, which is why
    a free-text column stopped publishing `{"-9.99e2": 1}` beside a note
    promising no value would appear (review item P1-R1-F10). Holding
    that half here left the other half nowhere, and the field added
    afterwards was published by a role that publishes nothing (review
    item P1-R7-F2). The whole rule now lives in
    `_publication_class_applied`, which sees the whole block; this
    function applies the floor and nothing else.
    """
    by_class: dict[str, int] = {}
    for name in parsing.MISSING_CLASSES:
        by_class[name] = 0
    for _spelling, name in missing:
        by_class[name] = by_class[name] + 1
    pooled: dict[str, int] = {}
    for name in parsing.MISSING_CLASSES:
        pooled[name] = 0
    for name in parsing.MISSING_CLASSES:
        if name == parsing.MISSING_WITHHELD:
            continue
        count = by_class[name]
        if count >= settings.small_cell_floor:
            pooled[name] = count
        elif count:
            pooled[parsing.MISSING_WITHHELD] = (
                pooled[parsing.MISSING_WITHHELD] + count
            )
    by_source: dict[str, int] = {}
    exact: dict[str, int] = {}
    for spelling, _name in missing:
        if parsing.trimmed(spelling):
            key = parsing.visible(spelling)
        else:
            key = parsing.MISSING_BLANK
        if key in exact:
            exact[key] = exact[key] + 1
        else:
            exact[key] = 1
    withheld = 0
    for key in sorted(exact):
        if exact[key] >= settings.small_cell_floor:
            by_source[key] = exact[key]
        else:
            withheld = withheld + exact[key]
    if withheld:
        by_source[parsing.MISSING_WITHHELD] = withheld
    return by_source, pooled


# -- numeric sentinels ------------------------------------------------


def _sentinel_verdicts(
    cells: _Cells, n_present: int
) -> "dict[float, tuple[bool, str, int]]":
    """Decide, for each numeric sentinel present, whether it means "missing".

    Three rules, and each closes a reproduced defect:

    * the REFERENCE POPULATION excludes EVERY candidate, not only the
      one being judged. With 60 zeros, 20 `-999` and 20 `9999`, judging
      `-999` against a population that still held `9999` made it look
      ordinary, so one convention was removed and the other was
      published as a level of a binary column (review item P1-R1-F7);
    * the DENOMINATOR is every present value, including the ones that
      do not read as numbers (review item P1-R4-F2);
    * the person running the tool has the last word, and the last word
      is compared as a NUMBER. Round 6 turned the candidate into the
      spelling `-999` and looked for that spelling in the declarations,
      so `--keep-value -999.0` was not found, the candidate was removed
      as missing anyway, and the profile published a minimum computed
      without it -- the exact opposite of what was asked (review item
      P1-R6-F9). Nothing here spells a candidate to decide anything.
      The candidate arrives as a number rather than as text, so it is
      turned into the same exact form the declarations carry before the
      two are compared (review item P1-R7-F3);
    * WHICH CELLS ARE THE CANDIDATE is decided by the exact number each
      one denotes, and so is the reference population everything is
      judged against. Round 7 made the declaration comparison exact and
      left this question on the rounded value, so a column holding
      fifteen copies of `-999.00000000000001` -- a different number
      that rounds to the same binary64 value as `-999` -- reported a
      candidate of `-999` in fifteen rows and removed all fifteen,
      including when the person had typed that exact spelling after
      `--keep-value` (review item P1-R8-F2). A number that merely
      rounds to a candidate is not that candidate: it is not counted
      towards it, it is not removed with it, and it stays in the
      reference population as the ordinary number it is.

    A candidate declared MISSING never reaches this function: a declared
    number is taken out of the column by `_declared_numbers_removed`
    before the cells are counted, so by the time a candidate exists it
    has already survived every declaration. That is why only the kept
    side is asked about here.

    Returns candidate -> (is missing, reason code, occurrences).
    """
    settings = cells.settings
    kept = _declarations(settings.kept_values)
    verdicts: dict[float, tuple[bool, str, int]] = {}
    candidates: list[float] = []
    # The exact number of each candidate this column actually holds,
    # and how many rows hold it. Both are read from the cell records'
    # own exact numbers, which is what keeps a near neighbour of a
    # sentinel out of its count (review item P1-R8-F2).
    named: list[tuple[int, tuple[str, ...], int]] = []
    occurrences_of: dict[float, int] = {}
    for candidate in parsing.NUMERIC_SENTINELS:
        exact = _exact_number(candidate)
        held = len(
            [cell for cell in cells.classified if cell.exact == exact]
        )
        if held:
            candidates += [candidate]
            named += [exact]
            occurrences_of[candidate] = held
    # Judge every candidate against the SAME reference population: the
    # numbers that are not a candidate of any kind. A cell holding no
    # number this format can carry has no value to contribute.
    others: list[float] = []
    for cell in cells.classified:
        value = cell.value
        if value is None or cell.exact in named:
            continue
        others += [value]
    for candidate in candidates:
        occurrences = occurrences_of[candidate]
        if _declared_number(_exact_number(candidate), kept):
            verdicts[candidate] = (False, REASON_KEPT_BY_USER, occurrences)
            continue
        if len(others) < 4:
            verdicts[candidate] = (
                False,
                REASON_TOO_FEW_OTHERS,
                occurrences,
            )
            continue
        ordered_others = sorted(others)
        lower = _quantile(ordered_others, 25, 100)
        upper = _quantile(ordered_others, 75, 100)
        spread = upper - lower
        distance = settings.sentinel_outlier_iqr_multiple * spread
        is_outlier = candidate < lower - distance or candidate > upper + distance
        frequent = _share(occurrences, n_present) >= settings.sentinel_minimum_share
        if is_outlier and frequent:
            verdicts[candidate] = (
                True,
                REASON_OUTLIER_AND_FREQUENT,
                occurrences,
            )
        elif is_outlier:
            verdicts[candidate] = (False, REASON_TOO_RARE, occurrences)
        else:
            verdicts[candidate] = (False, REASON_NOT_AN_OUTLIER, occurrences)
    return verdicts


def _published_verdicts(
    verdicts: "dict[float, tuple[bool, str, int]]", settings: Settings
) -> "tuple[list[dict[str, object]], int]":
    """The verdicts that may be named, and the count of those that may not.

    A verdict naming a candidate says that value occurred in the column.
    When fewer than `small_cell_floor` rows held it, saying so would
    publish a value the levels are withholding at the same moment --
    which is exactly the contradiction review item P1-R1-F10 found, a
    remark printing `-999` beside a note promising it was not published.
    Such candidates are counted, unnamed.
    """
    entries: list[dict[str, object]] = []
    unpublished = 0
    for candidate in sorted(verdicts):
        missing, reason, occurrences = verdicts[candidate]
        if occurrences < settings.small_cell_floor:
            unpublished = unpublished + 1
            continue
        entries += [
            {
                "candidate": f"{candidate:g}",
                "verdict": VERDICT_MISSING if missing else VERDICT_KEPT,
                "reason": reason,
                "n_occurrences": occurrences,
            }
        ]
    return entries, unpublished


# -- levels -----------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class _Levels:
    """The published level list and everything pooled out of it."""

    published: list[dict[str, object]]
    suppressed_levels: int
    suppressed_rows: int
    suppressed_counts: list[int]


def _levels(counts: dict[str, int], settings: Settings) -> _Levels:
    """Published levels, plus everything that did not reach the profile.

    Levels are keyed on the value AFTER trimming and case folding --
    the same key the binary and categorical rules count distinct values
    with. Deciding the role on one key and counting the levels on
    another is what let a column the profile called binary publish
    THREE labels, and what let a lone differently-cased row become a
    level of its own (review item P1-R1-F10).

    `suppressed_counts` is the anonymous multiset of the withheld
    levels' sizes. Without it a binary column split 1/9 and one split
    5/5 serialise to the same profile, so a generator built from the
    profile alone cannot reproduce either (review item P1-R1-F9).

    There is no "beyond the cap" outcome here any more. `categorical_
    ceiling` decides the ROLE again, as the plan says (review item
    P1-R6-F7), so a column that reaches this function holds at most
    that many different values by construction, and a pair of counts
    that can only ever be zero is a field a reader has to learn to
    ignore.
    """
    ordered = [
        label for _rank, label in sorted(
            [(-counts[label], label) for label in counts]
        )
    ]
    entries: list[dict[str, object]] = []
    suppressed_levels = 0
    suppressed_rows = 0
    suppressed_counts: list[int] = []
    for label in ordered:
        count = counts[label]
        if count >= settings.small_cell_floor:
            entries += [{"label": label, "count": count}]
        else:
            suppressed_levels = suppressed_levels + 1
            suppressed_rows = suppressed_rows + count
            suppressed_counts += [count]
    return _Levels(
        published=entries,
        suppressed_levels=suppressed_levels,
        suppressed_rows=suppressed_rows,
        suppressed_counts=sorted(suppressed_counts),
    )


def _level_details(levels: _Levels) -> dict[str, object]:
    """The published block a label-publishing role carries."""
    return {
        "levels": levels.published,
        "suppressed_levels": levels.suppressed_levels,
        "suppressed_rows": levels.suppressed_rows,
        "suppressed_level_counts": levels.suppressed_counts,
    }


# -- role-specific blocks ---------------------------------------------


def _text_details(cells: _Cells) -> dict[str, object]:
    """Length and word-count statistics for a column of free text."""
    lengths = [float(length) for length in _lengths(cells.present)]
    words = [
        float(parsing.token_count(value)) for value in cells.present
    ]
    return {
        "length": {
            "min": int(min(lengths)),
            "max": int(max(lengths)),
            "mean": _moments(lengths)["mean"],
            "p50": published(_quantile(sorted(lengths), 50, 100)),
        },
        "words": {
            "min": int(min(words)),
            "max": int(max(words)),
            "mean": _moments(words)["mean"],
        },
        "n_all_digits": cells.all_digits,
        "n_code_alphabet": cells.code_alphabet,
    }


def _numeric_details(cells: _Cells, whole: bool) -> dict[str, object]:
    """The published description of a numeric column."""
    numbers = cells.numbers
    n_present = len(cells.present)
    details: dict[str, object] = {
        "percentiles": _quantiles(numbers),
        "n_zero": len([value for value in numbers if value == 0.0]),
        # Every cell whose sign the text settles, not only the ones the
        # statistics could use. The sign of `(1e999)` ruled the count
        # role out; it must not then vanish from the counts (review item
        # P1-R5-F2).
        "n_negative": cells.n_negative,
        "n_negative_unrepresentable": cells.n_negative_unrepresentable,
        "n_rows": cells.n_rows,
        "integer_valued": whole,
        # How much of the column the statistics were computed from. A
        # generator must not have to read an English remark to learn
        # that part of the column was left out (review item P1-R1-F9).
        "n_used_in_statistics": len(numbers),
        "n_left_out_of_statistics": n_present - len(numbers),
        "numeric_share": _share(_numeric_looking(cells), n_present),
    }
    moments = _moments(numbers)
    for key in sorted(moments):
        details[key] = moments[key]
    return details


def _offset_counts(
    pairs: list[tuple[str, str]], settings: Settings
) -> dict[str, int]:
    """How often each UTC offset appeared, with the small-cell floor.

    The earlier revision reduced every offset in a column to the single
    word `mixed`, so a profile could not say that most rows were written
    in one zone and a handful in another (review item P1-R1-F9).
    """
    counts: dict[str, int] = {}
    for _canonical, offset in pairs:
        key = offset if offset else "(none)"
        if key in counts:
            counts[key] = counts[key] + 1
        else:
            counts[key] = 1
    published_counts: dict[str, int] = {}
    withheld = 0
    for key in sorted(counts):
        if counts[key] >= settings.small_cell_floor:
            published_counts[key] = counts[key]
        else:
            withheld = withheld + counts[key]
    if withheld:
        published_counts[parsing.MISSING_WITHHELD] = withheld
    return published_counts


def _matching_date_format(
    present: list[str], settings: Settings
) -> "tuple[str, list[tuple[str, str]], list[str], int] | None":
    """The first date format that parses enough of the values.

    Returns (format name, parsed (canonical, offset) pairs, the source
    cells that parsed, count of cells that did not), or None.
    """
    needed = _needed(settings.minimum_parse_rate, len(present))
    for format_name in parsing.DATE_FORMATS:
        good: list[tuple[str, str]] = []
        sources: list[str] = []
        for value in present:
            pair = parsing.parse_datetime(value, format_name)
            if pair is not None:
                good += [pair]
                sources += [value]
        if len(good) >= needed and good:
            return format_name, good, sources, len(present) - len(good)
    return None


def _best_date_reading(present: list[str]) -> "tuple[str, int]":
    """The date format that reads the MOST of these values, and how many.

    Asked only of a column no rule claimed, where the profile owes the
    reader the competing readings and how far each one got (review item
    P1-R6-F7). It is a separate pass from `_matching_date_format` on
    purpose: that function stops at the first format that clears the
    line, and stopping early is what keeps an ordinary date column
    cheap. A column that no format claimed has already been through
    every format either way, so this costs one more pass over a column
    that is about to be described as free text.

    Guarantees: accepts the present values; returns the first format in
    the documented order that parses the most of them, with that count,
    and a count of zero when nothing parses. Raises nothing. No I/O.
    """
    best_name = parsing.DATE_FORMATS[0]
    best_count = 0
    for format_name in parsing.DATE_FORMATS:
        parsed = 0
        for value in present:
            if parsing.parse_datetime(value, format_name) is not None:
                parsed = parsed + 1
        if parsed > best_count:
            best_name = format_name
            best_count = parsed
    return best_name, best_count


def _datetime_details(
    format_name: str,
    pairs: list[tuple[str, str]],
    sources: list[str],
    unparsed: int,
    settings: Settings,
) -> dict[str, object]:
    """The published description of a datetime column."""
    # Order by the INSTANT each value names, not by its local text. Two
    # values written in different offsets sorted the wrong way round
    # before this (review item P1-R1-F9).
    #
    # A column that mixes offsets is also PUBLISHED in the quantity it
    # was ordered by. Ordering by the instant and then writing out the
    # local wall clock made the two disagree: with values at +14:00 and
    # at -12:00 the profile published `earliest` LATER than `latest` as
    # text and eleven date rungs that ran backwards, breaking the plan's
    # non-decreasing-ladder property (P1-D8) for the new field and
    # handing a generator an inverted range. The canonical form exists
    # to be compared as plain text, so the text has to be the ordered
    # quantity.
    reading = _datetime_reading(pairs)
    keyed: list[tuple[int, str, str]] = []
    unkeyed: list[str] = []
    for canonical, offset in pairs:
        instant = parsing.instant_key(canonical, offset)
        shown = canonical
        if reading == "utc":
            at_utc = parsing.utc_canonical(canonical, offset)
            if at_utc is not None:
                shown = at_utc
        if instant is None:
            unkeyed += [shown]
        else:
            keyed += [(instant, shown, offset)]
    if keyed:
        ordered = sorted(keyed)
        canonical_order = [entry[1] for entry in ordered]
        earliest = ordered[0][1]
        latest = ordered[len(ordered) - 1][1]
        earliest_offset = ordered[0][2]
        latest_offset = ordered[len(ordered) - 1][2]
    else:
        canonical_order = sorted(unkeyed)
        earliest = canonical_order[0]
        latest = canonical_order[len(canonical_order) - 1]
        earliest_offset = ""
        latest_offset = ""
    digits = 0
    for value in sources:
        digits = max(digits, parsing.subsecond_digits(value, format_name))
    resolution = "date"
    if format_name == "iso-datetime":
        resolution = "datetime"
    if format_name == "year-quarter":
        resolution = "quarter"
    # An offset is NAMED only where at least `small_cell_floor` rows
    # carry it. Publishing the endpoint's offset unconditionally beside a
    # floored `utc_offsets` map named the one rare zone the map had just
    # pooled into `(withheld)` -- a value published in one field of the
    # same block that another field promises to withhold, which is
    # exactly the contradiction review item P1-R1-F10 found.
    offsets = _offset_counts(pairs, settings)
    return {
        "format": format_name,
        "resolution": resolution,
        "time_precision": _finest_precision(sources, format_name),
        "subsecond_digits": digits,
        # Which clock `earliest`, `latest` and `date_percentiles` are
        # written on. A reader never has to guess, and never has to
        # combine two fields to know what it is holding.
        "datetimes_read_at": reading,
        "earliest": earliest,
        "latest": latest,
        "earliest_utc_offset": _named_offset(earliest_offset, offsets),
        "latest_utc_offset": _named_offset(latest_offset, offsets),
        # The eleven-point ladder over the ordered values. Two columns
        # with the same first and last date and opposite shapes used to
        # serialise identically (review item P1-R1-F9).
        "date_percentiles": _date_ladder(canonical_order),
        "n_unparsed": unparsed,
        "utc_offsets": offsets,
    }


def _datetime_reading(pairs: list[tuple[str, str]]) -> str:
    """The clock this column's datetimes are published on.

    Returns `local` when one offset wrote the whole column, `utc`
    otherwise.

    Local text is what the table holds and is the more faithful thing to
    publish, so it is kept whenever every value shares one offset --
    which is every real column but a few. The moment two offsets appear,
    local text no longer orders the values, and the profile publishes
    the instants instead.
    """
    seen: dict[str, int] = {}
    for _canonical, offset in pairs:
        key = offset if offset else "(none)"
        seen[key] = 1
    if len(seen) <= 1:
        return "local"
    return "utc"


def _named_offset(offset: str, published_offsets: dict[str, int]) -> str:
    """One endpoint's UTC offset, named only if the floor let it be named."""
    if not offset:
        return "(none)"
    if offset in published_offsets:
        return offset
    return parsing.MISSING_WITHHELD


def _finest_precision(sources: list[str], format_name: str) -> str:
    """The finest time precision any value in the column writes."""
    best = len(parsing.PRECISION_ORDER) - 1
    for value in sources:
        found = parsing.datetime_precision(value, format_name)
        rank = best
        index = 0
        for name in parsing.PRECISION_ORDER:
            if name == found:
                rank = index
            index = index + 1
        best = min(best, rank)
    return parsing.PRECISION_ORDER[best]


# -- the role rules, in the order they are tested ---------------------


@dataclasses.dataclass(frozen=True)
class _Verdict:
    """One role decision, with everything it wants to publish."""

    role: str
    evidence: str
    details: dict[str, object]
    notes: list[str]
    remarks: list[str]


def _all_different(cells: _Cells) -> bool:
    """True when the column's values hardly ever repeat, in a table big
    enough for that to mean anything.

    This answer decides NO role. It was the first clause of the
    identifier rule through three revisions, and every revision was
    defeated by a column of measurements that also never repeated, so
    the rule it served no longer exists (review item P1-R6-F8). What is
    left is the one thing uniqueness is honestly good for: deciding
    whether to SAY that the values never repeat, and to point at
    `--identifier` for the person who knows what they are. In a short
    column almost every measurement is all-different, so below
    `identifier_minimum_rows` nothing is said about it at all.

    Guarantees: accepts a tally of a column; returns a truth value that
    depends on the tally alone. Raises nothing. No I/O of any kind.
    """
    settings = cells.settings
    n_present = len(cells.present)
    if n_present < settings.identifier_minimum_rows:
        return False
    return cells.raw_distinct >= _needed(
        settings.identifier_uniqueness, n_present
    )


def _categorical_ceiling(cells: _Cells) -> int:
    """The most different values a set of categories may hold here.

    The plan's rule, restored by review item P1-R6-F7:
    ``min(categorical_ceiling, categorical_share of the table's ROWS)``
    and never below ``categorical_floor``.

    ROWS, not the values the column happens to hold, and the two differ
    on a sparse column. A 100-row table whose coded field is filled in
    30 times with 6 labels has a ceiling of 10 here and is a set of
    categories; a share of the present values would have put its ceiling
    at 3 and sent an ordinary shape to free text with nothing published.
    Which labels may then be SHOWN is a separate question, already
    settled by the small-cell floor. Rows are also what the plan states,
    and the code and the plan must not disagree about a threshold every
    profile records.

    What this replaces was an average repetition of two, plus a separate
    cap of twelve on mostly numeric columns. That rule called forty
    different labels in a hundred rows a set of categories and published
    the one label that cleared the small-cell floor; this ceiling sends
    the same column to free text, which publishes nothing at all.

    Guarantees: accepts a tally of a column; returns a whole number of
    at least ``categorical_floor``, decided by comparing whole numbers.
    Raises nothing. No I/O of any kind.
    """
    settings = cells.settings
    # The table's ROWS, for the reasons in the docstring above (review
    # item P1-R6-F7).
    share = _at_most(settings.categorical_share, cells.n_rows)
    ceiling = min(settings.categorical_ceiling, share)
    return max(ceiling, settings.categorical_floor)


def _decide(cells: _Cells, forced_identifier: bool) -> _Verdict:
    """Pick the one role, testing the rules in the documented order.

    Every rule here routes a column to a role decided by its VALUES.
    Exactly one role is not on that list: `identifier` comes from
    ``forced_identifier`` and from nowhere else, so a column no rule
    claims becomes free text rather than a guessed record number
    (review item P1-R6-F8).

    THE ORDER, and there is only one:

    0. the person's own declaration -- `identifier`;
    1. no present value at all -- `empty`, settled by the caller;
    2. written as numbers, too few of them holdable -- the
       `numeric_unrepresentable` role;
    3. one distinct value -- `constant`;
    4. two distinct values -- `binary`;
    5. dates, under one documented format, at the parse rate;
    6. numbers, at the parse rate -- `count` or `continuous`;
    7. at most the ceiling of different values -- `categorical`;
    8. everything else -- `free_text`, which publishes nothing.

    Two rules that stood in this list through round 6 are gone (review
    item P1-R6-F7): a fixed-width digit-code rule that ran ahead of the
    dates, because nothing may be routed by the WIDTH of its text, and a
    second numeric rule at half the values, because it published a mean
    over the part of a column that read as numbers while dropping the
    rest out of the distribution.
    """
    settings = cells.settings
    present = cells.present
    n_present = len(present)
    notes: list[str] = []
    remarks: list[str] = []
    numeric_looking = _numeric_looking(cells)
    strict_needed = _needed(settings.minimum_parse_rate, n_present)
    folded_distinct = len(cells.folded_counts)
    ceiling = _categorical_ceiling(cells)

    # RULE 0 -- the person who knows the table has the last word, and
    # since review item P1-R6-F8 it is also the ONLY word: this is the
    # one route to the identifier role, and every rule below can only
    # send a column somewhere else. A declared identifier beats every
    # rule, including the ones that publish. Eleven identical values
    # used to take the constant branch and publish the value while the
    # user had asked for exactly the opposite (review item P1-R1-F10).
    if forced_identifier:
        return _identifier_verdict(cells, notes=notes, remarks=remarks)

    # RULE 2 -- numeric intent that nothing can hold. Tested before any
    # rule that publishes a value, because the alternative is a column
    # of huge numbers published as free-text lengths or, worse, three
    # repeated spellings published as categorical labels (review items
    # P1-R3-F3, P1-R4-F2, P1-R5-F2). RULE 1, the empty column, is
    # settled before this function is called.
    #
    # This rule and the numeric rule share ONE line, and it is the
    # plan's 0.99. The test is on how much of the column can be HELD,
    # not merely on how much of it was written as a number:
    # `numeric_looking` counts cells that contribute nothing to a
    # percentile, so deciding the numeric roles on it alone let a ladder
    # be built from a single representable cell out of a hundred -- one
    # row's exact value published as eleven statistics. The population
    # that decides the role and the population the statistics are
    # computed from are one population, which is what STRUCTURAL RULE A
    # already promises.
    if numeric_looking >= strict_needed and (
        len(cells.numbers) < strict_needed
    ):
        remarks = remarks + [
            (
                f"this column is written as numbers, but only "
                f"{len(cells.numbers)} of its {numeric_looking} numeric "
                f"values is a number this file format can hold -- the rest "
                f"are too large or too small, or in a form whose meaning "
                f"contradicts itself. Too few of them are left to describe "
                f"the column, and synthtwin will not invent values in their "
                f"place, so no statistic and no value of this column is "
                f"published. Rescale the column (for example, record "
                f"thousands instead of units) and run the command again"
            )
        ]
        notes = notes + [
            (
                "no value of this column is published: too few of them are "
                "numbers this file format can hold"
            )
        ]
        return _Verdict(
            role=ROLE_UNREPRESENTABLE,
            # "all N of the M values" was false whenever N < M, and the
            # review's own complaint was a detection_evidence sentence
            # that stated something the column did not show.
            evidence=(
                f"{numeric_looking} of the {n_present} values are written as "
                f"numbers, and "
                + (
                    "none of them is a number this file format can hold"
                    if not cells.numbers
                    else (
                        f"only {len(cells.numbers)} of them is a number this "
                        f"file format can hold"
                    )
                )
            ),
            details={
                "n_negative": cells.n_negative,
                "n_positive": cells.n_positive,
                "n_sign_unknown": cells.n_sign_unknown,
                "n_whole": cells.n_whole,
                "n_fraction": cells.n_fraction,
                "n_whole_unknown": cells.n_whole_unknown,
            },
            notes=notes,
            remarks=remarks,
        )

    # RULE 3 -- one value, repeated.
    if folded_distinct == 1:
        levels = _levels(cells.folded_counts, settings)
        if levels.suppressed_levels:
            notes = notes + [
                (
                    "the single value in this column is shared by fewer rows "
                    f"than the smallest group size ({settings.small_cell_floor}), "
                    "so the value itself is not published"
                )
            ]
        return _Verdict(
            role=ROLE_CONSTANT,
            evidence=f"all {n_present} values that are present are the same",
            details=_level_details(levels),
            notes=notes,
            remarks=remarks,
        )

    # RULE 4 -- two values. Decided on the SAME key the levels are
    # counted with, so the role and the published list can never
    # disagree about how many values there are.
    if folded_distinct == 2:
        levels = _levels(cells.folded_counts, settings)
        if levels.suppressed_levels:
            notes = notes + [
                (
                    f"{levels.suppressed_levels} of the two labels in this "
                    f"column are shared by fewer than "
                    f"{settings.small_cell_floor} rows, so that label is not "
                    f"published"
                )
            ]
        if cells.raw_distinct != 2:
            remarks = remarks + [
                (
                    "this column has values that differ only in upper and "
                    "lower case; they are counted, and published, as one"
                )
            ]
        if numeric_looking >= strict_needed or _matching_date_format(
            present, settings
        ):
            remarks = remarks + [
                (
                    "the two values in this column also read as numbers or "
                    "dates; because there are only two of them, the profile "
                    "records the two values and how often each appears, "
                    "which describes the column exactly"
                )
            ]
        return _Verdict(
            role=ROLE_BINARY,
            evidence=(
                "there are exactly two different values, ignoring upper "
                "and lower case"
            ),
            details=_level_details(levels),
            notes=notes,
            remarks=remarks,
        )

    # RULE 5 -- dates, under one documented format, at the parse rate.
    #
    # A rule stood ahead of this one until review item P1-R6-F7: a
    # column of same-width all-digit values, at least one carrying a
    # leading zero, was read as codes rather than as quantities. It is
    # deleted. Nothing may be routed by the WIDTH of its text: the
    # padding says how the value was WRITTEN, and a rule that reads a
    # writing convention as a meaning claims something the values do not
    # carry -- the identical text is a clock time, a padded account
    # number and a postal code, and only the person who owns the table
    # knows which. Such a column now lands where the ordinary rules put
    # it, and `--identifier` is how a column of codes is declared.
    matched = _matching_date_format(present, settings)
    if matched is not None:
        format_name, pairs, sources, unparsed = matched
        details = _datetime_details(
            format_name, pairs, sources, unparsed, settings
        )
        if numeric_looking >= strict_needed:
            remarks = remarks + [
                (
                    "the values in this column read both as dates and as "
                    "plain numbers; they were read as dates"
                )
            ]
        if format_name == "month-first-date":
            remarks = remarks + [
                (
                    "dates written with slashes are read month first "
                    "(03/04/2024 is the 4th of March); if this table writes "
                    "the day first, the profile has the month and day the "
                    "wrong way round"
                )
            ]
        return _Verdict(
            role=ROLE_DATETIME,
            evidence=(
                f"{len(pairs)} of the {n_present} values are dates written "
                f"as {parsing.format_example(format_name)}"
            ),
            notes=notes,
            remarks=remarks,
            details=details,
        )

    # RULE 6 -- numbers, at the one parse rate there is. A column that
    # reads as numbers in essentially every cell is a quantity however
    # many different values it holds.
    #
    # Falling short here decides nothing but this rule: the column goes
    # on to RULE 7 and may still be a set of categories. Below the line
    # is not a synonym for free text.
    if numeric_looking >= strict_needed:
        return _numeric_verdict(cells, notes, remarks)

    # RULE 7 -- a set of categories: at most the ceiling of different
    # values, counted after trimming and case folding. Tested after the
    # numeric rule, so a column of measurements is described as
    # measurements and a small set of labels that happen to be digits is
    # described as labels.
    if folded_distinct <= ceiling:
        levels = _levels(cells.folded_counts, settings)
        details = _level_details(levels)
        details["level_ceiling"] = ceiling
        if levels.suppressed_levels:
            notes = notes + [_pooled_note(levels, settings)]
        if cells.raw_distinct != folded_distinct:
            remarks = remarks + [
                (
                    "some values in this column differ only in upper and "
                    "lower case; they are counted, and published, as one"
                )
            ]
        if ceiling - folded_distinct <= settings.near_threshold_slack:
            remarks = remarks + [
                (
                    f"this column was close to the line between a set of "
                    f"categories and free text: it has {folded_distinct} "
                    f"different values and the line is at {ceiling}"
                )
            ]
        return _Verdict(
            role=ROLE_CATEGORICAL,
            evidence=(
                f"there are {folded_distinct} different values, which is "
                f"within the {ceiling} a set of categories may have in a "
                f"table of {cells.n_rows} rows, so this column is a set "
                f"of categories"
            ),
            details=details,
            notes=notes,
            remarks=remarks,
        )

    # RULE 8 -- everything else is free text, which publishes nothing.
    #
    # There is no rule between RULE 7 and this one. Two rules used to
    # stand here. One read all-different single tokens as record
    # numbers, and three revisions of it were each defeated by the
    # column next door: `0930` (a clock), `000042` (a padded count),
    # `1mg` (a dose). The last of those is why it is gone rather than
    # mended -- `1mg` and `code1` are the same shape of string, so no
    # property of the values can separate the measurement from the
    # label (review item P1-R6-F8). The other described a column that
    # was merely a MAJORITY numbers as a quantity, which published a
    # mean over the part that read as numbers and left the rest out of
    # the distribution entirely (review item P1-R6-F7).
    #
    # Free text is the honest answer to "no positive reading fits". It
    # withholds every value exactly as the identifier role does, so
    # nothing is disclosed that was not disclosed before, but it claims
    # nothing about what the values mean, and it keeps the shape facts
    # (lengths, word counts, how many different values there are) that
    # a generator needs. Guessing had no upside to trade against that:
    # a correct guess would have published nothing more than this.
    #
    # Both readings are counted ONCE, here, and the same two counts go
    # into the evidence and into the remark. A sentence a person reads
    # and a field a program reads that were computed twice are two
    # sentences that can disagree.
    numbers_said = _read_as_numbers(numeric_looking, n_present)
    dates_said = _read_as_dates(present)
    remarks = remarks + [
        _competing_readings(cells, ceiling, numbers_said, dates_said)
    ]
    return _free_text_verdict(
        cells,
        notes=notes,
        remarks=remarks,
        evidence=(
            f"{numbers_said}, {dates_said}, and there are "
            f"{folded_distinct} different values where a set of categories "
            f"may have at most {ceiling} in a table of {cells.n_rows} rows"
        ),
    )


def _read_as_numbers(numeric_looking: int, n_present: int) -> str:
    """How much of a column is written as numbers, in words.

    "Written as" rather than "read as", and deliberately: this is the
    count the numeric line is compared against, and it includes the
    cells whose writer meant a number that no format can hold. Saying
    they "read as numbers" would claim more than the column shows.
    """
    if not numeric_looking:
        return f"none of the {n_present} values is written as a number"
    return (
        f"{numeric_looking} of the {n_present} values are written as numbers"
    )


def _read_as_dates(present: list[str]) -> str:
    """How much of a column read as dates, and under which format."""
    best_name, best_count = _best_date_reading(present)
    if not best_count:
        return "none of them reads as a date in any form synthtwin knows"
    return (
        f"{best_count} read as dates written as "
        f"{parsing.format_example(best_name)}"
    )


def _competing_readings(
    cells: _Cells, ceiling: int, numbers_said: str, dates_said: str
) -> str:
    """Why no reading fitted this column, with the rate each one reached.

    A column that publishes nothing owes its owner the reason, and the
    reason is a set of counts rather than a verdict: how much of the
    column each reading accounted for, and how much each reading
    needed (review item P1-R6-F7). Without it the person is told only
    that synthtwin declined, which is the report the plan calls useless.

    Guarantees: accepts a tally of a non-empty column, the ceiling that
    was applied to it, and the two readings already counted by the
    caller; returns one paragraph naming the readings that were tried,
    the count each one reached, and the count each one needed. No value
    of the column appears in it. Raises nothing. No I/O of any kind.
    """
    settings = cells.settings
    n_present = len(cells.present)
    strict_needed = _needed(settings.minimum_parse_rate, n_present)
    folded_distinct = len(cells.folded_counts)
    return (
        f"synthtwin could not settle what this column holds, so none of "
        f"its values is published. Here is why: "
        f"{numbers_said} and {dates_said}; a column is described as "
        f"numbers, or as dates, only when at least {strict_needed} of them "
        f"read that way. It holds {folded_distinct} different values, where "
        f"a set of categories may hold at most {ceiling}. Describing it "
        f"from the part that does read would publish an average, a smallest "
        f"and a largest value that the rest of the column contradicts, so "
        f"synthtwin describes it as free text and publishes no value of it "
        f"at all. If these are measurements written with a currency sign, a "
        f"per-cent sign, a unit such as mg, or a clock time, write them as "
        f"plain numbers -- one column for the number, and the unit in the "
        f"column name -- and run the command again"
    )


def _free_text_verdict(
    cells: _Cells,
    notes: list[str],
    remarks: list[str],
    evidence: str,
) -> _Verdict:
    """The free-text block: shape statistics only, and no value at all.

    ONE rule ends here, the last one, and it ends here with everything
    no positive reading fitted. That includes every all-different column
    of code-shaped tokens, because `1mg` and `code1` are the same shape
    of string and the reading that used to be taken here was a guess
    about MEANING dressed as a rule (review item P1-R6-F8); it includes
    the column that is only PART numbers, because publishing a mean over
    the part that reads leaves the rest out of the distribution while
    the profile looks complete (review item P1-R6-F7); and it includes
    the column with more different values than a set of categories may
    have. In every case synthtwin has ruled readings OUT and has
    established none, and free text is what saying so looks like: the
    values are withheld exactly as the identifier role withholds them,
    and nothing is claimed about what they mean. The caller's remark
    names each reading that was tried and how far it got, so the person
    can see the arithmetic rather than only the verdict.

    When the values are also all different, the person running the tool
    is told so in one remark -- that synthtwin did not assume they are
    record numbers, that nothing from the column is published either
    way, and that `--identifier` is how they declare it if that is what
    it holds. The remark points BOTH ways on purpose: naming only
    `--identifier` told the owner of a column of prices, percentages or
    clock times to mark a MEASUREMENT as a record number, which withholds
    its values permanently and silently.

    Guarantees: accepts a tally of a non-empty column; returns a
    `_Verdict` whose role is free text and whose details carry no value
    of the column, only lengths and word counts. Raises nothing. No I/O.
    """
    notes = notes + [
        (
            "this column is described as free text, so none of its values "
            "are published: only how long they are and how many words they "
            "hold"
        )
    ]
    if _all_different(cells):
        remarks = remarks + [
            (
                "every value in this column is different, and none of the "
                "forms synthtwin can read fits them. synthtwin did NOT "
                "assume they are record numbers: it cannot tell from the "
                "values alone whether these are record numbers or "
                "measurements written in a form it does not read yet, and a "
                "wrong guess would throw away the whole distribution. "
                "Nothing from this column is published either way -- no "
                "value of it, and no distribution. If these ARE record "
                "numbers, run the command again with --identifier NAME, "
                "where NAME is this column's name, and the profile will say "
                "so. If they are measurements written with a currency sign, "
                "a per-cent sign, a unit such as mg, or a clock time, write "
                "them as plain numbers -- one column for the number, and the "
                "unit in the column name -- and their distribution will be "
                "described. Do not use --identifier on a measurement: it "
                "withholds the column entirely"
            )
        ]
    return _Verdict(
        role=ROLE_TEXT,
        evidence=evidence,
        details=_text_details(cells),
        notes=notes,
        remarks=remarks,
    )


def _pooled_note(levels: _Levels, settings: Settings) -> str:
    """The note that says how many levels were withheld and how many rows."""
    return (
        f"{levels.suppressed_levels} value(s) of this column are each "
        f"shared by fewer than {settings.small_cell_floor} rows, so "
        f"they are counted together instead of being published "
        f"({levels.suppressed_rows} rows in total)"
    )


def _left_padded(number: int, width: int) -> str:
    """``number`` in base ten, padded with zeros to at least ``width``.

    Guarantees: accepts a whole number of zero or more and a width of
    zero or more; returns its base-ten spelling, never shorter than
    ``width``. Raises nothing. No I/O of any kind.
    """
    text = f"{number}"
    while len(text) < width:
        text = "0" + text
    return text


def _occurrences_of_each(present: list[str]) -> dict[str, int]:
    """How many rows each different value covers, keyed by the value.

    This mapping holds spellings and is never published; it is the
    intermediate `_n_distinct_by_occurrences` counts its own answer
    from. Values are counted EXACTLY as the file spells them, which is
    the same question `n_distinct` answers, so the two always agree.

    Guarantees: accepts the present cells of one column, as text, in row
    order; returns one entry per different spelling whose counts sum to
    the length of the input. Determinism: the answer depends only on the
    input. Raises nothing. No I/O of any kind.
    """
    counts: dict[str, int] = {}
    for value in present:
        if value in counts:
            counts[value] = counts[value] + 1
        else:
            counts[value] = 1
    return counts


def _n_distinct_by_occurrences(present: list[str]) -> dict[str, int]:
    """How many different values cover one row, two rows, and so on.

    THE SHAPE OF REPETITION WITHOUT THE VALUES. Each key is a number of
    rows, and the entry under it is how many different values of this
    column cover exactly that many rows. A column of six rows holding
    one value four times and two values once each becomes
    ``{"1": 2, "4": 1}``; one holding three values twice each becomes
    ``{"2": 3}``.

    WHY IT EXISTS (review item P1-R8-F4). Those two columns used to
    serialize to identical bytes: both record `n_present` 6 and
    `n_distinct` 3 and nothing about multiplicity, so a generator
    reading the profile alone had to pick one repetition pattern for
    both, and any grouped analysis on the twin diverged from the real
    table. The two mappings above tell them apart.

    WHY IT IS PUBLISHABLE FROM A COLUMN THAT PUBLISHES NO VALUES. The
    mapping is a function of the group SIZES alone: rename every value,
    or shuffle every row, and it does not move. No spelling, no order,
    no row position and no link to any other column reaches it. It is
    the same class of fact as `suppressed_level_counts`, which publishes
    the sizes of the withheld levels for the same reason -- and the
    reason was checked here rather than assumed:

    * at the extremes it adds nothing that was not already published.
      One present value gives ``{"1": 1}``; every value different gives
      ``{"1": n_distinct}``; every value the same gives one entry keyed
      on `n_present`. Each of those is forced by `n_present` and
      `n_distinct`, which this profile has always carried.
    * between the extremes it adds exactly one thing: the size of each
      repetition group, with nothing saying which group. Knowing that
      some value covers four of six rows does not say which value, and
      no value of this column appears anywhere in its block.
    * what it does disclose, and this is stated rather than waved away:
      the sizes themselves. A mapping containing ``"1": 1`` says that
      some one row holds a value no other row holds. That is a count
      about an unnamed group, which is precisely what
      `suppressed_level_counts` already publishes, and it is why the
      profile is described as real-derived material rather than as
      anonymous.

    THE KEY FORM, because JSON object keys are text and the document is
    serialized with sorted keys: each key is the row count in base ten,
    left-padded with zeros to the width of the largest key in the SAME
    mapping. Padding is what makes the sorted-key order a numeric order:
    written bare, `"10"` sorts before `"2"`. A consumer reads a key as a
    number in base ten; leading zeros do not change it.

    Guarantees: accepts the present cells of one column, as text, in row
    order; returns a mapping whose entries sum to the number of
    DIFFERENT values in the input and whose keys, read as numbers and
    weighted by their entries, sum to the length of the input. An empty
    input gives an empty mapping. Determinism: the answer depends only
    on the input, and the keys are built in increasing numeric order.
    Raises nothing. No I/O of any kind.
    """
    counts = _occurrences_of_each(present)
    tally: dict[int, int] = {}
    for value in counts:
        occurrences = counts[value]
        if occurrences in tally:
            tally[occurrences] = tally[occurrences] + 1
        else:
            tally[occurrences] = 1
    if not tally:
        return {}
    width = len(f"{max(tally)}")
    shape: dict[str, int] = {}
    for occurrences in sorted(tally):
        shape[_left_padded(occurrences, width)] = tally[occurrences]
    return shape


def _identifier_verdict(
    cells: _Cells,
    notes: list[str],
    remarks: list[str],
) -> _Verdict:
    """The identifier block. No value of the column reaches it.

    ONE way in: the person who owns the table named the column with
    `--identifier` (RULE 0). There is no second way, and there is no
    rule anywhere in this module that can produce this role by reading
    values (review item P1-R6-F8). That is why this function takes no
    ``evidence`` argument -- the evidence is always the same sentence,
    and the sentence is true by construction: somebody said so.

    Three inferences used to arrive here as well, each defeated by a
    column of measurements shaped exactly like a column of labels. The
    trade was never worth taking: when the guess was right it published
    no more than free text publishes, and when it was wrong it destroyed
    a distribution the twin exists to reproduce.

    What is published is the role, the counts, the shortest and longest
    value, whether every value is a whole number, and -- since review
    item P1-R8-F4 -- how many different values cover one row, two rows
    and so on. Those are counts and lengths, never values;
    `_n_distinct_by_occurrences` above states what the last of them
    does and does not disclose.
    """
    n_present = len(cells.present)
    lengths = _lengths(cells.present)
    # The note has to cover the WHOLE block, not the part of it this
    # function builds. It said "only how many there are and how long
    # they are" while a sentinel verdict elsewhere in the same block
    # carried the spelling of a value out of the column (review item
    # P1-R7-F2). The spelling is withheld now; the note also stops
    # promising less than the block contains, because a claim that is
    # too narrow is how the next field slips past unnoticed -- which is
    # why "how often they repeat" joined it with the field that made it
    # true (review item P1-R8-F4).
    notes = notes + [
        (
            "this column holds record numbers or codes, so no value of it "
            "is published anywhere in its description: only how many there "
            "are, how long they are, how often they repeat, and what "
            "synthtwin decided about them"
        )
    ]
    return _Verdict(
        role=ROLE_IDENTIFIER,
        evidence=(
            "you told synthtwin that this column holds record numbers "
            "rather than measurements"
        ),
        details={
            "min_length": min(lengths),
            "max_length": max(lengths),
            "all_whole_numbers": (
                cells.n_whole == n_present and cells.n_whole > 0
            ),
            "n_all_digits": cells.all_digits,
            "n_code_alphabet": cells.code_alphabet,
            # The shape of repetition, with no value attached to it: the
            # one fact a generator needs to rebuild a column of codes
            # that repeat, and the one this block did not carry (review
            # item P1-R8-F4). Its key form and what it discloses are in
            # `_n_distinct_by_occurrences`.
            "n_distinct_by_occurrences": _n_distinct_by_occurrences(
                cells.present
            ),
        },
        notes=notes,
        remarks=remarks,
    )


def _numeric_verdict(
    cells: _Cells, notes: list[str], remarks: list[str]
) -> _Verdict:
    """The count/continuous block, at the one strength there is.

    This function took a ``strict`` flag until review item P1-R6-F7,
    because two rules reached it: one at the plan's parse rate and one
    at a majority. The second is deleted, so there is one caller, one
    line, and one sentence of evidence.
    """
    settings = cells.settings
    n_present = len(cells.present)
    numeric_looking = _numeric_looking(cells)
    strict_needed = _needed(settings.minimum_parse_rate, n_present)
    unparsed = n_present - numeric_looking
    if unparsed:
        remarks = remarks + [
            (
                f"{unparsed} value(s) in this column are not numbers; they "
                f"were left out of the statistics and are not published"
            )
        ]
    # A column where EVERY value is written as a number is not "close to
    # the line": no value of it could have been different without the
    # data being different. Reporting it as borderline is the useless
    # report the plan warns against.
    if numeric_looking < n_present and (
        _barely_above(
            numeric_looking, strict_needed, settings.near_threshold_slack
        )
        or _barely_below(
            numeric_looking, strict_needed, settings.near_threshold_slack
        )
    ):
        remarks = remarks + [
            (
                f"this column was close to the line between numbers "
                f"and text: {numeric_looking} of its {n_present} values are "
                f"written as numbers, and the line is at {strict_needed}"
            )
        ]
    if cells.raw_distinct >= _needed(
        settings.identifier_uniqueness, n_present
    ):
        remarks = remarks + [
            (
                "every value in this column is different. That is not "
                "treated as evidence of anything: the column is described "
                "as numbers, which keeps its distribution. If it is really "
                "a record number, run the command again with --identifier "
                "NAME, where NAME is this column's name, and its values "
                "will be left out of the profile altogether"
            )
        ]
    # A column of counts must be whole and non-negative in EVERY cell
    # whose writer meant a number -- including the ones no format can
    # hold. `(1e999)` is visibly negative and `1e-999` is visibly a
    # fraction, and both were published as whole non-negative counts
    # before this (review item P1-R5-F2). A cell whose sign or whole-
    # ness the text does not settle is enough to rule the role out too:
    # missing evidence is not evidence of nothing.
    whole_everywhere = (
        cells.n_whole == numeric_looking and numeric_looking > 0
    )
    counts_things = (
        whole_everywhere and cells.n_negative == 0 and cells.n_sign_unknown == 0
    )
    role = ROLE_COUNT if counts_things else ROLE_CONTINUOUS
    if role == ROLE_COUNT:
        evidence = (
            f"all {numeric_looking} numeric values are whole and none is "
            f"negative, so this column counts things"
        )
    else:
        evidence = (
            f"{numeric_looking} of the {n_present} values are written as "
            f"numbers"
        )
    details = _numeric_details(cells, whole_everywhere)
    # A spread larger than this file format can hold is a fact the
    # profile records in a field of its own, and it is also a fact the
    # person running the tool has to be told in words: without this
    # remark the only sign of it is a null where a number belongs
    # (review item P1-R6-F3).
    if details["std_unrepresentable"]:
        remarks = remarks + [
            (
                "the values in this column are so far apart that their "
                "spread is a number too large for this file format to hold, "
                "so no standard deviation is published for it: the profile "
                "records that the spread is out of range rather than a "
                "number that would be wrong. Every other statistic of this "
                "column is published as usual. If you need the spread, "
                "record the column in larger units -- thousands or millions "
                "instead of units, with the unit in the column name -- and "
                "run the command again"
            )
        ]
    return _Verdict(
        role=role,
        evidence=evidence,
        details=details,
        notes=notes,
        remarks=remarks,
    )


# -- the publication class, applied to the whole block ----------------


def _count_at(entry: dict[str, object], key: str) -> int:
    """The whole number stored under ``key``, or zero."""
    value = entry[key]
    if isinstance(value, int):
        return value
    return 0


def _text_at(entry: dict[str, object], key: str) -> str:
    """The text stored under ``key``, or the empty text."""
    value = entry[key]
    if isinstance(value, str):
        return value
    return ""


def _counts_only(block: dict[str, object]) -> dict[str, object]:
    """One mapping with everything but the named counts withheld.

    A key on `KEYS_THAT_CARRY_NO_VALUE` keeps its contents; every other
    key keeps its PLACE and loses its contents to `(withheld)`. Losing
    the place instead would have hidden the withholding: a reader
    comparing two columns cannot see a key that is not there, and a
    program reading the profile would find the shape of a block
    changing with its role.
    """
    kept: dict[str, object] = {}
    # Sorted rather than in the order the block was built: the profile
    # writes every mapping with sorted keys anyway, and iterating a
    # mapping's keys without reaching for a method on it is how the rest
    # of this module reads one (plan D6.2).
    for key in sorted(block):
        if key in KEYS_THAT_CARRY_NO_VALUE:
            kept[key] = block[key]
        else:
            kept[key] = SUPPRESSED_LABEL
    return kept


def publishes_no_values(role: str, forced_identifier: bool) -> bool:
    """Whether a column's block may carry a value of the table at all.

    The role's publication class decides it, with ONE addition: a column
    the person named with `--identifier` publishes nothing whatever role
    it ends up with.

    That addition is not decoration. A declared column whose cells are
    ALL spellings that mean "no value" never reaches the identifier role
    -- the empty-column rule settles it before any rule runs -- so it
    was described as an empty column and published the person's own
    spelling in `missing_by_source`, 200 rows of it, while the same
    run's summary told them that a column of record numbers publishes
    nothing either way. RULE 0 says a declaration beats every rule; this
    is that sentence applied to what the column PUBLISHES rather than
    only to which role it is given.

    Guarantees: accepts a role from `ROLES` and whether the person
    declared the column; returns True when no value of the column may
    appear anywhere in its block. Determinism: the answer depends only
    on those two arguments -- no value of the column is consulted, so
    the rule cannot vary with the data it governs. Raises nothing. No
    I/O of any kind.
    """
    return forced_identifier or role in ROLES_PUBLISHING_NOTHING


def _publication_class_applied(
    publishes_nothing: bool,
    details: dict[str, object],
    by_source: dict[str, int],
    entries: list[dict[str, object]],
) -> "tuple[dict[str, object], dict[str, int], list[dict[str, object]]]":
    """Everything a column block publishes, filtered by its class.

    THE RULE IS A PROPERTY OF THE BLOCK, and this is the one place it
    is applied. A column that publishes no values publishes no values
    anywhere in its block: not in its details, not in the spellings it
    counted as missing, and not in what it decided about a numeric
    stand-in for "no value". `publishes_no_values` above says which
    columns those are.

    That last one is why this function exists. `sentinel_verdicts`
    carried the exact spelling of a candidate under `candidate`, and
    nothing looked at the role before writing it, so a column the
    person had declared with `--identifier` -- declared precisely to
    keep its values out -- published `-999` in a field beside a summary
    saying nothing of its values would appear (review item P1-R7-F2).
    Closing that one field would have left the same hole open for the
    next field somebody adds, which is exactly how this field came to
    be open in the first place.

    WHAT SURVIVES for such a column is every fact that carries no value:
    how many candidates were named, how many rows each one accounted
    for, what was decided about each and why. A reader can still see
    that a decision about a stand-in happened and which way it went;
    only the spelling goes. The candidates too rare to name at all are
    counted separately, in `n_sentinel_candidates_unpublished`, which
    is a count and needs no filtering.

    THE ORDER carries nothing either. Candidates reach here sorted by
    the number they are, so on a block that keeps the spelling the
    order is readable and means what it shows; on a block that withholds
    it, position would have said which of two withheld candidates is the
    smaller. The withheld list is therefore ordered by the facts it
    publishes -- occurrences, then verdict, then reason -- so that
    nothing about a value of the table decides where a line appears.

    Guarantees: accepts whether the column may publish a value, the
    details block built for it, the missing-spelling map under the
    small-cell floor, and the sentinel verdicts that cleared the floor;
    returns the three of them unchanged for a column whose class permits
    values, and filtered for a column whose class does not. Raises
    nothing. No I/O of any kind.
    """
    if not publishes_nothing:
        return details, by_source, entries
    ranked: list[tuple[int, str, str, int]] = []
    index = 0
    for entry in entries:
        ranked += [
            (
                _count_at(entry, "n_occurrences"),
                _text_at(entry, "verdict"),
                _text_at(entry, "reason"),
                index,
            )
        ]
        index = index + 1
    withheld: list[dict[str, object]] = []
    for _occurrences, _verdict, _reason, place in sorted(ranked):
        withheld += [_counts_only(entries[place])]
    no_spellings: dict[str, int] = {}
    return _counts_only(details), no_spellings, withheld


def profile_column(
    name: str,
    position: int,
    values: list[str],
    n_rows: int,
    settings: Settings,
    forced_identifier: bool = False,
) -> ColumnProfile:
    """Describe one column: its role, its statistics, what was withheld.

    Guarantees:

    - Inputs: ``values`` is every cell of the column, as text, in row
      order; ``position`` is the column's 1-based place in the source
      file; ``n_rows`` is the table's row count, which must equal
      ``len(values)``; ``forced_identifier`` records that the person
      running the tool named this column as holding record numbers, in
      which case no value of it is published whatever the rules would
      otherwise have decided. It is also the ONLY way the returned role
      can be `identifier`: with it false, no column of any shape is
      given that role (review item P1-R6-F8).
    - Determinism: the result depends only on the arguments. Nothing
      here consults a clock, an environment variable, or a random
      source, and every ordering that reaches the output is sorted.
    - Declarations: what the person named with `--keep-value` and
      `--missing-value` is applied HERE, before any role is decided and
      before any value is removed for any other reason. A declaration
      that reads as a number this format can hold is compared with the
      NUMBER each cell holds, so `-999` covers a file that writes
      `-999.00`; any other declaration is compared with the spelling,
      after trimming and case folding (review item P1-R6-F9).
    - Errors raised: TypeError if a value is not text (an internal
      invariant: both readers produce text), and ValueError when the
      settings name one value BOTH as data and as "no value" -- there
      is no reading of that pair that is not a guess, so it is refused
      before anything is described (review item P1-R6-F9). No refusal
      comes from the VALUES of a column: one that matches no rule is
      described as free text rather than rejected.
    - Boundary: no file is opened, and no value of a suppressed kind
      (identifier, free text, a number no format can hold, or a label
      below the small-cell floor) appears in the returned description.
      This is a property of the column's publication CLASS -- its role,
      plus the declaration that beats every role -- applied to the WHOLE
      block by `_publication_class_applied` once both are known, not of
      the branch that built the block and not of any one field. A column
      that publishes no values keeps its counts, its lengths and the
      decisions it made -- including what it decided about each numeric
      stand-in for "no value" and how many rows that accounted for, and,
      on a declared identifier, how many different values cover one row,
      two rows and so on -- and keeps not one spelling of a value.
    """
    clashes = contradictory_declarations(
        settings.kept_values, settings.declared_missing_values
    )
    if clashes:
        raise ValueError(f"{CONTRADICTORY_DECLARATION}: {clashes[0]}")
    present, missing = _split_missing(values, settings)
    # THE one classification of this column's cells. Everything below
    # reads these records; not one line of it reads the column again.
    classified = _classify_all(present)
    # The second half of what the person declared, and the half that has
    # to wait for the classification: a declared NUMBER is compared with
    # the number a cell holds, not with the way the file spells it
    # (review item P1-R6-F9). It runs before the cells are counted, so
    # no rule and no statistic ever sees a value the person called "no
    # value".
    classified, declared = _declared_numbers_removed(classified, settings)
    missing = missing + declared
    cells = _tally(classified, n_rows, settings)
    # One list of what is present, rebuilt from the surviving records.
    # Keeping the pre-declaration list here would have counted values
    # the person removed towards every share below it.
    present = cells.present

    # The numeric sentinels are judged only for a column that can end up
    # in a numeric role, and that is the one line there is: the COMBINED
    # numeric-looking population against the plan's parse rate. Asking
    # about the representable numbers alone let three unrepresentable
    # cells stop the question being asked at all, and `-999` was then
    # published as the column's minimum (review item P1-R5-F1).
    verdicts: dict[float, tuple[bool, str, int]] = {}
    if _numeric_looking(cells) >= _needed(
        settings.minimum_parse_rate, len(present)
    ):
        verdicts = _sentinel_verdicts(cells, len(present))
        withheld = sorted(
            candidate for candidate in verdicts if verdicts[candidate][0]
        )
        if withheld:
            # Removed by the EXACT number a cell holds, the same
            # question `_sentinel_verdicts` counted the candidate's
            # rows with. Removing by the rounded value instead took
            # out cells holding a different number that rounds to the
            # candidate -- including cells the person had named with
            # `--keep-value` (review item P1-R8-F2).
            removed = [_exact_number(candidate) for candidate in withheld]
            kept: list[_Cell] = []
            for cell in classified:
                if cell.exact in removed:
                    missing += [
                        (cell.text, parsing.MISSING_NUMERIC_SENTINEL)
                    ]
                else:
                    kept += [cell]
            classified = kept
            # Every population is counted again from the surviving
            # RECORDS; none is patched, and no cell is classified twice.
            # Reading the column a second time here was the last place
            # where two readings of one cell could have differed
            # (review item P1-R6-F10).
            cells = _tally(classified, n_rows, settings)
            present = cells.present
    entries, unpublished = _published_verdicts(verdicts, settings)

    n_present = len(present)
    n_missing = n_rows - n_present
    remarks: list[str] = []
    if cells.n_out_of_range:
        remarks = remarks + [
            (
                f"{cells.n_out_of_range} value(s) are numbers too large or "
                f"too small for this file format to hold. They are counted "
                f"as numbers for deciding what this column is, and their "
                f"sign and whole-number status are counted too, but they "
                f"are left out of every statistic"
            )
        ]
    if cells.n_contradictory:
        remarks = remarks + [
            (
                f"{cells.n_contradictory} value(s) are written in a form "
                f"whose meaning contradicts itself -- a plus or minus sign "
                f"inside brackets, where the brackets already mean negative. "
                f"synthtwin will not guess which was meant, so these values "
                f"are left out of every statistic. Write them with a sign "
                f"or with brackets, not both, and run the command again"
            )
        ]
    if unpublished:
        remarks = remarks + [
            (
                f"{unpublished} of the numbers synthtwin uses as stand-ins "
                f"for 'no value' appeared in this column too few times to be "
                f"named here; the decision about each of them is recorded in "
                f"the counts above"
            )
        ]

    if not present:
        verdict = _Verdict(
            role=ROLE_EMPTY,
            evidence=(
                "every value in this column is blank or one of the "
                "spellings that mean 'no value'"
            ),
            details={},
            notes=[],
            remarks=[],
        )
    else:
        verdict = _decide(cells, forced_identifier)

    by_source, by_class = _missing_maps(missing, settings)
    # ONE application of the publication class, over everything the
    # block can publish, after the role is known and before anything is
    # built. Doing it per field is what let one field be forgotten
    # (review item P1-R7-F2).
    details, by_source, entries = _publication_class_applied(
        publishes_no_values(verdict.role, forced_identifier),
        verdict.details,
        by_source,
        entries,
    )
    # ONE construction site. Every count below is a field of the class,
    # so it exists on every role by construction rather than by
    # somebody remembering to add it in ten places.
    return ColumnProfile(
        name=name,
        position=position,
        role=verdict.role,
        detection_evidence=verdict.evidence,
        n_present=n_present,
        n_missing=n_missing,
        missing_by_source=by_source,
        missing_by_class=by_class,
        details=details,
        publication_notes=verdict.notes,
        remarks=remarks + verdict.remarks,
        n_numeric=len(cells.numbers),
        n_out_of_range=cells.n_out_of_range,
        n_contradictory=cells.n_contradictory,
        n_not_numeric=cells.n_not_numeric,
        n_distinct=cells.raw_distinct,
        n_distinct_folded=len(cells.folded_counts),
        sentinel_verdicts=entries,
        n_sentinel_candidates_unpublished=unpublished,
    )

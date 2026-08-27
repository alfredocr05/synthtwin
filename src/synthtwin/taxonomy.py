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
  digits denote, by `exact_of_spelling` and `exact_of_number`. The
  numeric-sentinel rule asks that same exact question of those same
  records -- which cells ARE a candidate, how many rows hold it, and
  which cells are taken out -- because a later rule that rounds undoes
  a comparison that did not (review item P1-R8-F2). Both names are
  PUBLIC for that reason and not by accident: the validating side has
  to reach the same answer about the same cells, and a module that
  asked the question in binary64 beside this one erased eleven cells
  this one keeps (review item P3-V4-F1). One question, one rule, one
  name;
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
measured value: `5 ** -twos` in `exact_of_number`, a whole number raised
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
ROLE_CLOCK = "time_of_day"
ROLE_AFFIXED = "affixed_number"
ROLE_LONG_TAIL = "long_tail_labels"
# THE FOURTEENTH ROLE (plan P4-D21). Two or more numbers written
# in one cell, joined by one repeated separator: `120/80`, `12-05-3`.
# It is reached ONLY where the person names the column, and never from
# the values -- see `_joined_reading` for the measurement that says why.
ROLE_JOINED = "joined_numbers"
ROLE_TEXT = "free_text"

# The lower bound of the long-tail detection line, and the max below is
# deliberate (plan P4-D5). LOWERING the publication floor must not widen
# WHICH columns become label-publishing: an all-different or nearly
# all-different column -- names, addresses, free comments -- has no
# eleven-row level and stays free text at EVERY floor, so the free-text
# role stays reachable and its promise stays floor-invariant. Raising
# the floor raises the line with it.
LONG_TAIL_LINE = 11

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
    ROLE_CLOCK,
    ROLE_AFFIXED,
    ROLE_LONG_TAIL,
    ROLE_JOINED,
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
ROLES_PUBLISHING_LABELS = (
    ROLE_CONSTANT,
    ROLE_BINARY,
    ROLE_CATEGORICAL,
    ROLE_LONG_TAIL,
)
# `affixed_number` is a ranges role with ONE named exception: its two
# affix keys carry floor-governed shared text off the table's cells, and
# no other key of any ranges role may ever carry a spelling. The
# exception is confined to those two keys by the forbidden-key rule, not
# by this tuple.
ROLES_PUBLISHING_RANGES = (
    ROLE_COUNT,
    ROLE_CONTINUOUS,
    ROLE_DATETIME,
    ROLE_CLOCK,
    ROLE_AFFIXED,
    # `joined_numbers` is a ranges role with ONE named exception of its
    # own, the same shape as the affixed role's two: `separator` carries
    # a character the table's cells wear. No other key of it may carry a
    # spelling, and the forbidden-key rule is what confines it.
    ROLE_JOINED,
)
ROLES_PUBLISHING_NOTHING = (
    ROLE_UNREPRESENTABLE,
    ROLE_IDENTIFIER,
    ROLE_TEXT,
)

# THE THREE AXES BESIDE THE ROLE (plan P2-D3, owner decision 1).
#
# The role name is a taxonomy verdict carrying a rule's history: it
# says which rule claimed the column and, through this module, why. The
# axes are the three questions a consumer actually asks -- what shape
# are the values, are there usable values at all, and is this column
# somebody's key -- and Phase 2's generator dispatches on THEM, never on
# the role. A role added to the tuple above then arrives with its
# answers already stated, instead of as an unrecognized name in a chain
# of comparisons somewhere else.
#
# Nothing about `role` moves for them. Every role keeps its name and its
# meaning, and the axes are published beside it, so a consumer written
# against the earlier document reads every fact it read before.
TYPE_UNKNOWN = "unknown"
TYPE_NUMERIC = "numeric"
TYPE_CODE = "code"
TYPE_TEXT = "text"
QUALITY_OK = "ok"
QUALITY_EMPTY = "empty"
QUALITY_UNREPRESENTABLE = "unrepresentable"
STRUCTURAL_DATA = "data"
STRUCTURAL_IDENTIFIER = "identifier"

# The three vocabularies as tuples, because the publication guard
# checks each axis against the whole of what it may say (plan P2-D2)
# and a check against a set gathered from the data it is checking would
# accept whatever it found. A test holds these to `ROLE_AXES`, so a
# role added with a new shape word cannot leave them behind.
STATISTICAL_TYPES = (
    TYPE_UNKNOWN,
    TYPE_NUMERIC,
    ROLE_CONSTANT,
    ROLE_BINARY,
    ROLE_DATETIME,
    ROLE_COUNT,
    ROLE_CONTINUOUS,
    ROLE_CATEGORICAL,
    TYPE_CODE,
    ROLE_CLOCK,
    ROLE_AFFIXED,
    ROLE_LONG_TAIL,
    ROLE_JOINED,
    TYPE_TEXT,
)
QUALITY_STATES = (QUALITY_OK, QUALITY_EMPTY, QUALITY_UNREPRESENTABLE)
STRUCTURAL_ROLES = (STRUCTURAL_DATA, STRUCTURAL_IDENTIFIER)

# What each role answers to the first two questions. The mapping is
# TOTAL over `ROLES` -- a completeness check in the suite compares the
# two -- because an axis a column sometimes lacks is an axis nobody can
# dispatch on.
#
# Four roles answer something other than their own name, and each is a
# case where the role name and the shape of the values are not the same
# fact: an `empty` column has no shape to report and no usable values;
# a `numeric_unrepresentable` column was written as numbers and holds
# none this format can carry; an `identifier` column holds codes; and
# `free_text` holds text. The other six name their own shape, and are
# written out one by one rather than derived from the role string,
# because a mapping a reader can check is worth more than one line of
# cleverness. `affixed_number` names its own shape and joins the ones
# that do.
ROLE_AXES: "dict[str, tuple[str, str]]" = {
    ROLE_EMPTY: (TYPE_UNKNOWN, QUALITY_EMPTY),
    ROLE_UNREPRESENTABLE: (TYPE_NUMERIC, QUALITY_UNREPRESENTABLE),
    ROLE_CONSTANT: (ROLE_CONSTANT, QUALITY_OK),
    ROLE_BINARY: (ROLE_BINARY, QUALITY_OK),
    ROLE_DATETIME: (ROLE_DATETIME, QUALITY_OK),
    ROLE_COUNT: (ROLE_COUNT, QUALITY_OK),
    ROLE_CONTINUOUS: (ROLE_CONTINUOUS, QUALITY_OK),
    ROLE_CATEGORICAL: (ROLE_CATEGORICAL, QUALITY_OK),
    ROLE_IDENTIFIER: (TYPE_CODE, QUALITY_OK),
    ROLE_CLOCK: (ROLE_CLOCK, QUALITY_OK),
    ROLE_AFFIXED: (ROLE_AFFIXED, QUALITY_OK),
    # A LONG-TAIL COLUMN NAMES ITS OWN SHAPE (contract 14.1 and C6-19).
    # It was mapped to `categorical` when the role landed, on the
    # ground that the two publish the same four keys -- but the axis
    # table is a BIJECTION, thirteen roles onto thirteen types, and a
    # role sharing another's type breaks the totality discipline that
    # is the axes' whole value here. The contract states the cost
    # plainly: for this role the shape axis buys nothing over the role
    # name, and it names itself anyway so that every role's type is one
    # row of one table a reader can check.
    ROLE_LONG_TAIL: (ROLE_LONG_TAIL, QUALITY_OK),
    # AND SO DOES A JOINED-NUMBER COLUMN, for the reason stated just
    # above (plan P4-D21). The table is a bijection, now fourteen roles
    # onto fourteen types, and this role's shape is not `continuous`
    # and not `count`: those name ONE number per cell, and a consumer
    # that read this column as either would take the whole cell for a
    # value and find `120/80` is not one.
    ROLE_JOINED: (ROLE_JOINED, QUALITY_OK),
    ROLE_TEXT: (TYPE_TEXT, QUALITY_OK),
}

# The label a suppressed value is replaced by, and the key under which
# blank cells are counted.
SUPPRESSED_LABEL = "(withheld)"
BLANK_SPELLING = parsing.MISSING_BLANK

# HOW A NUMBER WAS WRITTEN, and nothing about what it is (owner
# decision 10). Six forms, and no seventh may be added by an
# implementation: a consumer reads this enumeration as closed.
#
# WHY THE FACT EXISTS. Three columns -- `0`, `00`, `000`; `0.0`, `00.0`,
# `000.0`; and `0e0`, `00e0`, `000e0` -- were byte-for-byte identical in
# every earlier profile: three present values, three different
# spellings, all numeric, all zero, whole numbers throughout. A person
# reading the first sees a column of whole numbers and reading the
# second a column of decimals, so a twin built from those bytes alone
# could not keep the type its own reader would infer for all three. The
# form is now counted, so it can be kept.
#
# It carries no value, no magnitude and no spelling -- only how many
# cells used each form.
#
# The six names and the ladder that reads one off a cell now live in
# `parsing`, because the generator has to recount the forms of the twin
# it wrote and may not import this module. These are bindings to that
# one rule, not a second copy of it.
STYLE_PLAIN = parsing.STYLE_PLAIN
STYLE_LEADING_ZERO = parsing.STYLE_LEADING_ZERO
STYLE_LEADING_PLUS = parsing.STYLE_LEADING_PLUS
STYLE_DECIMAL = parsing.STYLE_DECIMAL
STYLE_EXPONENT_LOWER = parsing.STYLE_EXPONENT_LOWER
STYLE_EXPONENT_UPPER = parsing.STYLE_EXPONENT_UPPER

# The order the counts are written in. It is the enumeration's order and
# not the order the ladder in `numeric_style` tests, because this one is
# only for reading: the document sorts every mapping's keys anyway.
NUMERIC_STYLES = (
    STYLE_PLAIN,
    STYLE_LEADING_ZERO,
    STYLE_LEADING_PLUS,
    STYLE_DECIMAL,
    STYLE_EXPONENT_LOWER,
    STYLE_EXPONENT_UPPER,
)

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
    # THE FORM CENSUS IS ADMITTED HERE ON A CHECKED PROPERTY rather
    # than on a judgement (plan P4-D18). Every other key here carries a
    # COUNT, which is safe to read at a glance. A form is TEXT, which
    # is the kind of thing this list exists to keep out -- so it is
    # admitted only because every figure of a cell is replaced by `%`
    # and every letter by `@` before the key is built -- two
    # characters no cell that HAS a form may contain -- and because
    # `profile._is_shape_form` refuses any key holding anything but
    # those two and thirteen named marks, whatever built it. What is
    # published is where the marks fell; what is not is anything that
    # stood between them.
    "shape_forms",
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

# Both as tuples, for the publication guard: the decision and the
# reason are words of this module, and the guard checks them against
# the whole of what they may be rather than against their type.
SENTINEL_VERDICTS = (VERDICT_MISSING, VERDICT_KEPT)
SENTINEL_REASONS = (
    REASON_OUTLIER_AND_FREQUENT,
    REASON_NOT_AN_OUTLIER,
    REASON_TOO_RARE,
    REASON_TOO_FEW_OTHERS,
    REASON_KEPT_BY_USER,
)

# What a datetime column publishes under `resolution`, and which clock
# its endpoints and ladder are written on. `_datetime_details` and
# `_datetime_reading` write these same names; they are constants so
# that the guard's enumeration and the producer's words are one thing.
RESOLUTION_DATE = "date"
RESOLUTION_DATETIME = "datetime"
RESOLUTION_QUARTER = "quarter"
RESOLUTION_MONTH = "month"
RESOLUTIONS = (
    RESOLUTION_DATE,
    RESOLUTION_DATETIME,
    RESOLUTION_QUARTER,
    RESOLUTION_MONTH,
)
READ_AT_LOCAL = "local"
READ_AT_UTC = "utc"
DATETIMES_READ_AT = (READ_AT_LOCAL, READ_AT_UTC)

# The eleven points of the ladder by name, in the ladder's own order,
# and the keys of the two short summaries a free-text column publishes
# (its length and its word count). Every key of a published summary of
# that shape is one of these words.
LADDER_NAMES = tuple([name for name, _num, _den in LADDER])
LENGTH_KEYS = ("min", "max", "mean", "p50")
WORD_KEYS = ("min", "max", "mean")

# What a declared value is compared with, recorded inside every profile
# so that a reader never has to guess which rule removed a value.
DECLARATION_MATCHING = "exact_number_when_it_reads_as_one_else_spelling"

# What `profile_column` says when one value is named both ways. The
# command says it in its own words, because it can name the two options
# the person typed.
CONTRADICTORY_DECLARATION = (
    "the same value cannot be both kept as data and read as 'no value'"
)


# -- THE NOTE GRAMMAR: every sentence the profile publishes ------------
#
# WHY SENTENCES NEED A GRAMMAR AT ALL (plan P2-D2, review items
# P1-R8-F6 and P2-C1-F3). A profile carries two kinds of string: a
# VALUE the publication rules authorize -- a column's name, a label
# that cleared the small-cell floor, a date the ladder landed on -- and
# a SENTENCE synthtwin wrote about the column. Both are text, both stand
# at a key the document has always had, and a check that reads the key
# and the type cannot tell them apart. So a note that one day spelled a
# rare value into its own sentence would be published under a key every
# rule already permits, and no completeness check would notice, because
# no key appeared and no type changed.
#
# THE RULE THIS SECTION IMPLEMENTS: a sentence in the finished document
# is not free text. It is built here, by `note`, out of ONE form drawn
# from the closed table below plus arguments that are whole numbers,
# words of this package's own vocabulary, or other forms of this same
# table. `profile.check_publication` then rebuilds each sentence it
# meets from the form and the arguments the sentence carries and
# refuses it unless the rebuilt text is identical. A value of the real
# table cannot become an argument -- it is neither a whole number nor
# one of the words -- so a sentence carrying one cannot be built; and a
# sentence assembled by joining or formatting text is a plain string
# again (`Note` + anything is `str`), which carries no form and is
# refused at the guard.
#
# WHAT A FORM IS. A name in `NOTE_ARITY`, mapped to how many arguments
# it takes. `rendered` writes the text of each one out in full, so the
# whole vocabulary of the document's sentences can be read in one place
# rather than gathered from the branches that happened to build them.

# The publication notes: what a column held back, and why.
NOTE_UNREPRESENTABLE_WITHHELD = "no_values_unrepresentable"
NOTE_ONE_VALUE_BELOW_FLOOR = "one_value_below_the_floor"
NOTE_ONE_OF_TWO_BELOW_FLOOR = "one_of_two_labels_below_the_floor"
NOTE_LABELS_POOLED = "labels_pooled_below_the_floor"
NOTE_FREE_TEXT_WITHHELD = "free_text_publishes_no_values"
NOTE_IDENTIFIER_WITHHELD = "identifier_publishes_no_values"
NOTE_HISTOGRAM_WITHHELD = "histogram_publishes_no_shape"

# The detection evidence: why the column was given the role it has.
EVIDENCE_EMPTY = "evidence_every_value_absent"
EVIDENCE_UNREPRESENTABLE = "evidence_numbers_none_holdable"
EVIDENCE_ONE_VALUE = "evidence_one_value"
EVIDENCE_TWO_VALUES = "evidence_two_values"
EVIDENCE_DATES = "evidence_dates"
EVIDENCE_COUNTS = "evidence_counts_things"
EVIDENCE_NUMBERS = "evidence_written_as_numbers"
EVIDENCE_CATEGORIES = "evidence_set_of_categories"
EVIDENCE_LONG_TAIL = "evidence_long_tail_of_labels"
EVIDENCE_NO_READING_FITS = "evidence_no_reading_fits"
EVIDENCE_DECLARED_IDENTIFIER = "evidence_declared_identifier"

# Two fragments that appear inside a longer sentence rather than on
# their own. They are forms like any other, and they travel as
# arguments of the sentences that carry them, so the whole sentence is
# still rebuilt from enumerated parts.
SAID_WRITTEN_AS_NUMBERS = "said_written_as_numbers"
SAID_READ_AS_DATES = "said_read_as_dates"

# The remarks: what the person running the tool is told about a column.
REMARK_OUT_OF_RANGE = "remark_values_out_of_range"
# The affixed-number role's two sentences. The evidence says how the
# column was read; the remark is carried by EVERY column of the role,
# without condition, because no test of the values separates an opaque
# token family from a measurement -- so the choice is between telling
# every such column's owner and telling none.
EVIDENCE_CLOCK = "evidence_clock_times"
EVIDENCE_AFFIXED = "evidence_numbers_wearing_one_affix"
EVIDENCE_JOINED = "evidence_numbers_joined_in_one_cell"
REMARK_AFFIXED = "remark_affixed_numbers_may_be_codes"
REMARK_CONTRADICTORY = "remark_values_contradictory"
REMARK_RARE_SENTINELS = "remark_rare_sentinels_unnamed"
REMARK_UNREPRESENTABLE = "remark_too_few_holdable_numbers"
REMARK_CASE_ONLY_TWO = "remark_two_values_differ_in_case"
REMARK_TWO_ALSO_NUMBERS = "remark_two_values_also_read_otherwise"
REMARK_DATES_ALSO_NUMBERS = "remark_dates_also_read_as_numbers"
REMARK_MONTH_FIRST = "remark_slashed_dates_are_month_first"
REMARK_SLASHED_EVIDENCE = "remark_slashed_dates_read_against_your_declaration"
# The century a two-figure year is read into is a GUESS, and this is
# where the column says so (plan P4-D15, contract NF42).
REMARK_TWO_DIGIT_YEAR = "remark_two_figure_years_are_read_at_a_pivot"

# The two reading names the slashed remark's fifth argument takes. They
# are package words rather than format members on purpose (contract
# NF36): the remark speaks about a READING -- a way round to read a
# slashed date -- and one reading covers two format members, so naming
# the member would make the sentence say something narrower than it
# means and would render differently for a date column and a stamp
# column that were decided identically.
READING_DAY_FIRST = "day-first"
READING_MONTH_FIRST = "month-first"
NOTE_READING_WORDS = (READING_DAY_FIRST, READING_MONTH_FIRST)
REMARK_CASE_ONLY_MANY = "remark_values_differ_in_case"
REMARK_NEAR_CATEGORY_LINE = "remark_close_to_the_category_line"
REMARK_NO_READING_FITS = "remark_no_reading_fits"
REMARK_SOME_NOT_NUMBERS = "remark_some_values_are_not_numbers"
REMARK_NEAR_NUMERIC_LINE = "remark_close_to_the_numeric_line"
REMARK_ALL_DIFFERENT_NUMBERS = "remark_every_number_is_different"
# A number written with a leading zero is usually a code, and a column
# of them is described as quantities unless a person says otherwise
# (plan P4-D16, contract NF43).
REMARK_PADDED_NUMBERS = "remark_padded_numbers_may_be_codes"
# A comma inside a number is read as a thousands separator, which is a
# CHOICE this package makes and cannot check (plan P4-D17, contract
# NF44).
REMARK_GROUP_COMMAS = "remark_commas_read_as_thousands"
REMARK_SPREAD_OUT_OF_RANGE = "remark_spread_out_of_range"
REMARK_ALL_DIFFERENT_TEXT = "remark_every_value_is_different"

# The header verdict, which the reader settles and the profile
# publishes. The sentences live in this table with every other
# published sentence, for the reason the table exists: a verdict built
# somewhere else would be the one string in the document with no form
# behind it, and one exception is all a guard needs to stop meaning
# anything.
HEADER_NAMES_BY_OPTION = "header_names_because_you_said_so"
HEADER_DATA_BY_OPTION = "header_data_because_you_said_so"
HEADER_NAMES_BY_CONVENTION = "header_names_by_convention"
HEADER_NAMES_SHOWN_BY_COLUMN = "header_names_shown_by_a_column"

# EVERY form, with how many arguments it takes. This mapping is the
# enumeration: a name that is not a key here is not a form, and `note`
# and `rendered` both refuse one. Adding a sentence to this profile
# means adding a line here and a branch to `rendered`, which is the
# point -- a sentence nobody enumerated cannot be published.
NOTE_ARITY: "dict[str, int]" = {
    NOTE_UNREPRESENTABLE_WITHHELD: 0,
    NOTE_ONE_VALUE_BELOW_FLOOR: 1,
    NOTE_ONE_OF_TWO_BELOW_FLOOR: 2,
    NOTE_LABELS_POOLED: 3,
    NOTE_FREE_TEXT_WITHHELD: 0,
    NOTE_IDENTIFIER_WITHHELD: 0,
    NOTE_HISTOGRAM_WITHHELD: 0,
    EVIDENCE_EMPTY: 0,
    EVIDENCE_UNREPRESENTABLE: 3,
    EVIDENCE_ONE_VALUE: 1,
    EVIDENCE_TWO_VALUES: 0,
    EVIDENCE_DATES: 3,
    EVIDENCE_COUNTS: 1,
    EVIDENCE_NUMBERS: 2,
    EVIDENCE_CATEGORIES: 3,
    # The different values, the ceiling it passed, the rows, the line a
    # level had to cover, and how many levels covered it.
    EVIDENCE_LONG_TAIL: 5,
    EVIDENCE_NO_READING_FITS: 5,
    EVIDENCE_DECLARED_IDENTIFIER: 0,
    SAID_WRITTEN_AS_NUMBERS: 2,
    SAID_READ_AS_DATES: 2,
    REMARK_OUT_OF_RANGE: 1,
    # How many cells wore the pair, and the pair itself.
    EVIDENCE_CLOCK: 3,
    EVIDENCE_AFFIXED: 3,
    EVIDENCE_JOINED: 3,
    REMARK_AFFIXED: 3,
    REMARK_CONTRADICTORY: 1,
    REMARK_RARE_SENTINELS: 1,
    REMARK_UNREPRESENTABLE: 2,
    REMARK_CASE_ONLY_TWO: 0,
    REMARK_TWO_ALSO_NUMBERS: 0,
    REMARK_DATES_ALSO_NUMBERS: 0,
    REMARK_MONTH_FIRST: 0,
    REMARK_TWO_DIGIT_YEAR: 0,
    # Contract NF36 fixes the order: D, M, X, Y, then the reading used.
    REMARK_SLASHED_EVIDENCE: 5,
    REMARK_CASE_ONLY_MANY: 0,
    REMARK_NEAR_CATEGORY_LINE: 2,
    REMARK_NO_READING_FITS: 7,
    REMARK_SOME_NOT_NUMBERS: 1,
    REMARK_NEAR_NUMERIC_LINE: 3,
    REMARK_ALL_DIFFERENT_NUMBERS: 0,
    REMARK_PADDED_NUMBERS: 1,
    REMARK_GROUP_COMMAS: 2,
    REMARK_SPREAD_OUT_OF_RANGE: 0,
    REMARK_ALL_DIFFERENT_TEXT: 0,
    HEADER_NAMES_BY_OPTION: 0,
    HEADER_DATA_BY_OPTION: 0,
    HEADER_NAMES_BY_CONVENTION: 0,
    HEADER_NAMES_SHOWN_BY_COLUMN: 1,
}

# The same names as a sorted tuple, for a reader and for the tests that
# walk the whole vocabulary.
NOTE_FORMS = tuple(sorted(NOTE_ARITY))

# The only WORDS an argument may be. Every other argument is a whole
# number or another form, so this tuple is the whole of what a sentence
# can say that is not a count: the names of the date formats, each of
# which the profile already publishes under `format`.
#
# A value of the real table is not here and cannot be added by any
# route, because this tuple is written out rather than gathered: that
# is what stops a spelling from becoming an argument.
# ...and the two words a clock sentence names its form by. They are
# this package's own, chosen from a closed pair, so a sentence carrying
# one says which SHAPE the column's cells had and nothing about what
# any cell said.
NOTE_CLOCK_HOURS_MINUTES = "hours_and_minutes"
NOTE_CLOCK_HOURS_MINUTES_SECONDS = "hours_minutes_and_seconds"
NOTE_CLOCK_WORDS = (
    NOTE_CLOCK_HOURS_MINUTES,
    NOTE_CLOCK_HOURS_MINUTES_SECONDS,
)

NOTE_ARGUMENT_WORDS = (
    parsing.DATE_FORMATS + NOTE_CLOCK_WORDS + NOTE_READING_WORDS
)

# What `note` and `rendered` say when they are handed something the
# grammar does not have. Both are internal invariants -- no input a
# person can give reaches them -- so they read as checks rather than as
# advice, and the guard's own refusal is the one a person sees.
UNKNOWN_NOTE_FORM = "internal check: no sentence of this profile is"
UNAUTHORIZED_NOTE_ARGUMENT = (
    "internal check: a sentence of this profile may be built only from "
    "whole numbers, this package's own words, and other sentences of "
    "this profile"
)
WRONG_NOTE_ARGUMENTS = "internal check: wrong number of parts for"


class Note(str):
    """One sentence of the profile, carrying which sentence it is.

    A Note IS its text: it compares, sorts, joins and serializes as the
    string it holds, so every consumer written against a profile of
    plain sentences reads exactly what it read before. What it carries
    BESIDE the text is where the text came from -- the `form` it was
    built from and the `arguments` that filled that form.

    That pair is the whole control. `profile.check_publication` rebuilds
    the text from them and refuses the leaf unless the rebuilt text is
    identical, so a sentence can appear in a finished document only if
    this module can write it again from enumerated parts.

    Two properties of Python are load-bearing here, and both are relied
    on deliberately:

    * anything joined to or formatted from a Note is a plain `str`.
      A future edit that interpolates a value into a sentence therefore
      loses the form rather than carrying it along, and the guard sees
      a string with no origin;
    * an instance built any other way than through `note` keeps this
      class's own defaults -- an empty form and no arguments -- which is
      not a form, so it is refused too.

    Guarantees: the text is fixed at construction and never changes;
    `form` is one of `NOTE_FORMS` and `arguments` are enumerated
    whenever the instance came from `note`; no I/O of any kind.
    """

    form: str = ""
    arguments: "tuple[object, ...]" = ()


def argument_is_enumerated(argument: object) -> bool:
    """Whether one part of a sentence is a part the grammar allows.

    Guarantees:

    - Inputs: any object, including one this module did not make.
    - Determinism: the answer depends only on the argument.
    - Errors raised: none. A part the grammar does not allow is False,
      never an exception, so a caller can ask about anything.
    - Boundary: True for a whole number of zero or more, for a word of
      `NOTE_ARGUMENT_WORDS`, and for a nested (form, arguments) pair
      whose own parts are enumerated. A value of the real table is text
      that is not one of those words, so it is False, which is the
      property the publication guard rests on.

    A truth value is NOT a whole number here. `True` counts as `1` in
    Python, and a sentence that quietly rendered a flag as a count would
    read as a fact about the column.
    """
    if isinstance(argument, bool):
        return False
    if isinstance(argument, int):
        return argument >= 0
    if isinstance(argument, str):
        return argument in NOTE_ARGUMENT_WORDS
    if isinstance(argument, tuple):
        if len(argument) != 2:
            return False
        form = argument[0]
        parts = argument[1]
        if not isinstance(form, str) or form not in NOTE_ARITY:
            return False
        if not isinstance(parts, tuple):
            return False
        if len(parts) != NOTE_ARITY[form]:
            return False
        for part in parts:
            if not argument_is_enumerated(part):
                return False
        return True
    return False


def _whole(arguments: "tuple[object, ...]", place: int) -> int:
    """One argument as the whole number the form says it is."""
    argument = arguments[place]
    if isinstance(argument, bool):
        raise TypeError(UNAUTHORIZED_NOTE_ARGUMENT)
    if not isinstance(argument, int):
        raise TypeError(UNAUTHORIZED_NOTE_ARGUMENT)
    return argument


def _word(arguments: "tuple[object, ...]", place: int) -> str:
    """One argument as the vocabulary word the form says it is."""
    argument = arguments[place]
    if not isinstance(argument, str):
        raise TypeError(UNAUTHORIZED_NOTE_ARGUMENT)
    if argument not in NOTE_ARGUMENT_WORDS:
        raise ValueError(UNAUTHORIZED_NOTE_ARGUMENT)
    return argument


def _affix(arguments: "tuple[object, ...]", place: int) -> str:
    """One argument as an affix spelling, the fourth argument class.

    The first three classes -- a whole number, one of this package's own
    words, a nested form -- carry nothing off anybody's table. This one
    does, and it is admitted under plan amendment A-P4-7 because the
    remark's whole purpose is to let somebody holding a column of codes
    recognize THEIR column, which a sentence that could not name the
    pair would never do.

    What keeps it narrow is a binding rather than a type: the argument
    conforms only when it is character-for-character the `affix_prefix`
    or `affix_suffix` of the block the note names, POSITIONALLY --
    argument 1 is the prefix and argument 2 the suffix, never either.
    The pair is already published in that block, so the sentence
    discloses no spelling the document does not already hold, and a
    reader who may not see the pair may not see the remark either:
    one publication class governs both.

    This accessor checks the type and renders the value. The identity
    check is the publication guard's, because only the guard holds the
    block the note names; residual R-P4-15 records that the binding is
    written per form by hand rather than derived.
    """
    argument = arguments[place]
    if not isinstance(argument, str):
        raise TypeError(UNAUTHORIZED_NOTE_ARGUMENT)
    return f"'{argument}'" if argument else ""


def _clock_shape(arguments: "tuple[object, ...]", place: int) -> str:
    """The clause naming which clock form a column's cells wore."""
    word = _word(arguments, place)
    if word == NOTE_CLOCK_HOURS_MINUTES:
        return "hours and minutes, `09:30`"
    return "hours, minutes and seconds, `09:30:00`"


def _affix_shape(
    arguments: "tuple[object, ...]", prefix_place: int, suffix_place: int
) -> str:
    """The clause describing how a cell of an affixed column is written.

    Three shapes, because one of the two sides is usually empty and a
    sentence that said "written as nothing, a number, then 'mg'" would
    be describing a shape no cell has.
    """
    prefix = _affix(arguments, prefix_place)
    suffix = _affix(arguments, suffix_place)
    if prefix and suffix:
        return f"written as {prefix}, a number, then {suffix}"
    if prefix:
        return f"written as {prefix} followed by a number"
    return f"written as a number followed by {suffix}"


def _said(arguments: "tuple[object, ...]", place: int) -> str:
    """One argument as the sentence fragment the form says it is."""
    argument = arguments[place]
    if not isinstance(argument, tuple):
        raise TypeError(UNAUTHORIZED_NOTE_ARGUMENT)
    if len(argument) != 2:
        raise ValueError(UNAUTHORIZED_NOTE_ARGUMENT)
    form = argument[0]
    parts = argument[1]
    if not isinstance(form, str):
        raise TypeError(UNAUTHORIZED_NOTE_ARGUMENT)
    if not isinstance(parts, tuple):
        raise TypeError(UNAUTHORIZED_NOTE_ARGUMENT)
    return rendered(form, parts)


def rendered(form: str, arguments: "tuple[object, ...]") -> str:
    """The exact text of one form, written from its arguments alone.

    Guarantees:

    - Inputs: a form of `NOTE_ARITY` and exactly as many arguments as
      that table gives it, each one enumerated.
    - Determinism: the text depends only on the form and the arguments.
      The same pair always writes the same sentence, on every platform
      and in every run, which is what lets the publication guard rebuild
      a sentence and compare it.
    - Errors raised: ValueError for a form this grammar does not have,
      for the wrong number of arguments, and for a word that is not one
      of `NOTE_ARGUMENT_WORDS`; TypeError for an argument that is not
      of the kind the form takes at that place. Both are internal
      checks: `note` refuses the same arguments before rendering, and
      the publication guard refuses the sentence rather than letting a
      failure here reach a person.
    - Boundary: every branch below is literal text and its own
      arguments. Nothing here reads a column, a cell, a file or a
      setting, so no value of the real table can reach a sentence
      except by being passed in as an argument -- which
      `argument_is_enumerated` refuses.
    """
    if form not in NOTE_ARITY:
        raise ValueError(f"{UNKNOWN_NOTE_FORM} {form}")
    if len(arguments) != NOTE_ARITY[form]:
        raise ValueError(f"{WRONG_NOTE_ARGUMENTS} {form}")
    if form == NOTE_UNREPRESENTABLE_WITHHELD:
        return (
            "no value of this column is published: too few of them are "
            "numbers this file format can hold"
        )
    if form == NOTE_ONE_VALUE_BELOW_FLOOR:
        return (
            f"the single value in this column is shared by fewer rows "
            f"than the smallest group size ({_whole(arguments, 0)}), "
            f"so the value itself is not published"
        )
    if form == NOTE_ONE_OF_TWO_BELOW_FLOOR:
        return (
            f"{_whole(arguments, 0)} of the two labels in this "
            f"column are shared by fewer than "
            f"{_whole(arguments, 1)} rows, so that label is not "
            f"published"
        )
    if form == NOTE_LABELS_POOLED:
        return (
            f"{_whole(arguments, 0)} value(s) of this column are each "
            f"shared by fewer than {_whole(arguments, 1)} rows, so "
            f"they are counted together instead of being published "
            f"({_whole(arguments, 2)} rows in total)"
        )
    if form == NOTE_FREE_TEXT_WITHHELD:
        return (
            "this column is described as free text, so none of its values "
            "are published: only how long they are, how many words they "
            "hold, how often they repeat, and -- where enough of them "
            "were written the same way -- the shape of that writing, "
            "which carries no letter and no figure of any value"
        )
    if form == NOTE_HISTOGRAM_WITHHELD:
        return (
            "the shape of this column's numbers is not published: the "
            "values spread out far enough that at least one stretch "
            "between two edges holds fewer rows than your smallest "
            "group size, and a shape published in part would say less "
            "than nothing -- it names some stretches and leaves the "
            "reader to guess where the rest of the values sit"
        )
    if form == NOTE_IDENTIFIER_WITHHELD:
        return (
            "this column holds record numbers or codes, so no value of it "
            "is published anywhere in its description: only how many there "
            "are, how long they are, how often they repeat, and what "
            "synthtwin decided about them"
        )
    if form == EVIDENCE_EMPTY:
        return (
            "every value in this column is blank or one of the "
            "spellings that mean 'no value'"
        )
    if form == EVIDENCE_UNREPRESENTABLE:
        holdable = _whole(arguments, 2)
        if not holdable:
            said = "none of them is a number this file format can hold"
        else:
            said = (
                f"only {holdable} of them is a number this "
                f"file format can hold"
            )
        return (
            f"{_whole(arguments, 0)} of the {_whole(arguments, 1)} values "
            f"are written as numbers, and " + said
        )
    if form == EVIDENCE_ONE_VALUE:
        return (
            f"all {_whole(arguments, 0)} values that are present are the same"
        )
    if form == EVIDENCE_TWO_VALUES:
        return (
            "there are exactly two different values, ignoring upper "
            "and lower case"
        )
    if form == EVIDENCE_DATES:
        return (
            f"{_whole(arguments, 0)} of the {_whole(arguments, 1)} values "
            f"are dates written as "
            f"{parsing.format_example(_word(arguments, 2))}"
        )
    if form == EVIDENCE_COUNTS:
        return (
            f"all {_whole(arguments, 0)} numeric values are whole and none "
            f"is negative, so this column counts things"
        )
    if form == EVIDENCE_NUMBERS:
        return (
            f"{_whole(arguments, 0)} of the {_whole(arguments, 1)} values "
            f"are written as numbers"
        )
    if form == EVIDENCE_CATEGORIES:
        return (
            f"there are {_whole(arguments, 0)} different values, which is "
            f"within the {_whole(arguments, 1)} a set of categories may "
            f"have in a table of {_whole(arguments, 2)} rows, so this "
            f"column is a set of categories"
        )
    if form == EVIDENCE_LONG_TAIL:
        return (
            f"there are {_whole(arguments, 0)} different values, more "
            f"than the {_whole(arguments, 1)} a set of categories may "
            f"have in a table of {_whole(arguments, 2)} rows -- but "
            f"{_whole(arguments, 4)} level(s) of it are shared by at "
            f"least {_whole(arguments, 3)} rows each, so this column is "
            f"a long tail of labels rather than free text"
        )
    if form == EVIDENCE_NO_READING_FITS:
        return (
            f"{_said(arguments, 0)}, {_said(arguments, 1)}, and there are "
            f"{_whole(arguments, 2)} different values where a set of "
            f"categories may have at most {_whole(arguments, 3)} in a "
            f"table of {_whole(arguments, 4)} rows"
        )
    if form == EVIDENCE_DECLARED_IDENTIFIER:
        return (
            "you told synthtwin that this column holds record numbers "
            "rather than measurements"
        )
    if form == SAID_WRITTEN_AS_NUMBERS:
        written = _whole(arguments, 0)
        if not written:
            return (
                f"none of the {_whole(arguments, 1)} values is written as "
                f"a number"
            )
        return (
            f"{written} of the {_whole(arguments, 1)} values are written "
            f"as numbers"
        )
    if form == SAID_READ_AS_DATES:
        read = _whole(arguments, 0)
        if not read:
            return "none of them reads as a date in any form synthtwin knows"
        return (
            f"{read} read as dates written as "
            f"{parsing.format_example(_word(arguments, 1))}"
        )
    if form == EVIDENCE_CLOCK:
        return (
            f"{_whole(arguments, 0)} value(s) are clock times written "
            f"as {_clock_shape(arguments, 1)}, and "
            f"{_whole(arguments, 2)} value(s) are not"
        )
    if form == EVIDENCE_JOINED:
        # NUMBERS, NOT *WHOLE* NUMBERS, and the word was wrong on the
        # page a person reads until 2026-08-26. `splits_into_numbers`
        # admits a decimal part -- that is what lets an I:E ratio be
        # read at all, and the changelog offers `1:1.5` as a feature --
        # so a column of `1:2.0` and `1:2.5` published "2 whole numbers"
        # of cells whose second number is not whole. Measured on 400
        # such rows before the repair. Contract NF47 carries the same
        # correction.
        return (
            f"{_whole(arguments, 0)} value(s) are "
            f"{_whole(arguments, 1)} numbers written in one cell "
            f"and joined by {parsing.format_example(_affix(arguments, 2))}"
        )
    if form == EVIDENCE_AFFIXED:
        return (
            f"{_whole(arguments, 2)} value(s) are "
            f"{_affix_shape(arguments, 0, 1)}"
        )
    if form == REMARK_AFFIXED:
        # It names the COUNTED cells, never "every value": the role
        # tolerates stragglers up to the parse line, so a sentence
        # about every value would be false of them.
        return (
            f"{_whole(arguments, 2)} of this column's values are "
            f"{_affix_shape(arguments, 0, 1)}, and synthtwin described "
            f"those numbers as quantities: their average, their spread "
            f"and their ends are in this profile. If these are codes "
            f"rather than measurements, run the command again with "
            f"--identifier and no value of this column will be "
            f"published at all"
        )
    if form == REMARK_OUT_OF_RANGE:
        return (
            f"{_whole(arguments, 0)} value(s) are numbers too large or "
            f"too small for this file format to hold. They are counted "
            f"as numbers for deciding what this column is, and their "
            f"sign and whole-number status are counted too, but they "
            f"are left out of every statistic"
        )
    if form == REMARK_CONTRADICTORY:
        return (
            f"{_whole(arguments, 0)} value(s) are written in a form "
            f"whose meaning contradicts itself -- a plus or minus sign "
            f"inside brackets, where the brackets already mean negative. "
            f"synthtwin will not guess which was meant, so these values "
            f"are left out of every statistic. Write them with a sign "
            f"or with brackets, not both, and run the command again"
        )
    if form == REMARK_RARE_SENTINELS:
        return (
            f"{_whole(arguments, 0)} of the numbers synthtwin uses as "
            f"stand-ins for 'no value' appeared in this column too few "
            f"times to be named here; the decision about each of them is "
            f"recorded in the counts above"
        )
    if form == REMARK_UNREPRESENTABLE:
        return (
            f"this column is written as numbers, but only "
            f"{_whole(arguments, 0)} of its {_whole(arguments, 1)} numeric "
            f"values is a number this file format can hold -- the rest "
            f"are too large or too small, or in a form whose meaning "
            f"contradicts itself. Too few of them are left to describe "
            f"the column, and synthtwin will not invent values in their "
            f"place, so no statistic and no value of this column is "
            f"published. Rescale the column (for example, record "
            f"thousands instead of units) and run the command again"
        )
    if form == REMARK_CASE_ONLY_TWO:
        return (
            "this column has values that differ only in upper and "
            "lower case; they are counted, and published, as one"
        )
    if form == REMARK_TWO_ALSO_NUMBERS:
        return (
            "the two values in this column also read as numbers or "
            "dates; because there are only two of them, the profile "
            "records the two values and how often each appears, "
            "which describes the column exactly"
        )
    if form == REMARK_DATES_ALSO_NUMBERS:
        return (
            "the values in this column read both as dates and as "
            "plain numbers; they were read as dates"
        )
    if form == REMARK_MONTH_FIRST:
        # THE SENTENCE NAMES NO PUNCTUATION, and that is the change
        # P4-D15 made to it. The same ambiguity is carried by slashes,
        # by dots and by a two-figure year, and a sentence that said
        # "written with slashes" was read by a person holding a dotted
        # column as a statement about some other column.
        return (
            "where the day and the month are both written as numbers, "
            "they are read month first (03/04/2024 is the 4th of "
            "March); if this table writes the day first, the profile "
            "has the month and day the wrong way round"
        )
    if form == REMARK_TWO_DIGIT_YEAR:
        # THE CONSEQUENCE IS STATED AS A RANGE AND NOT AS A DISTANCE.
        # An earlier wording said such a table is read forward "by a
        # hundred years", which is true only for the century either
        # side of the pivot: `68` meaning 1868 is read as 2068 and is
        # two hundred years out, and `75` meaning 2075 is read as 1975
        # and is out in the other direction, which that wording did not
        # warn about at all.
        return (
            "this column writes its years with two figures, which do "
            "not say which century they are in; 00 to 68 are read as "
            "2000 to 2068 and 69 to 99 as 1969 to 1999, so any year "
            "this table means outside 1969 to 2068 is read as the "
            "wrong one"
        )
    if form == REMARK_CASE_ONLY_MANY:
        return (
            "some values in this column differ only in upper and "
            "lower case; they are counted, and published, as one"
        )
    if form == REMARK_SLASHED_EVIDENCE:
        # CONTRACT NF36, WHICH FIXES EVERY PART OF THIS SENTENCE. Two
        # clauses, the first always and the second on its own trigger;
        # the first has three renderings and exactly one applies,
        # selected by the arguments alone. The tie has a rendering of
        # its own because the tie is the case the declaration decides:
        # with only the other two, a producer on a tie must invent a
        # sentence or write a false one, since each of those claims one
        # reading parsed more than the other.
        day = _whole(arguments, 0)
        month = _whole(arguments, 1)
        day_only = _whole(arguments, 2)
        month_only = _whole(arguments, 3)
        used = _word(arguments, 4)
        if day > month:
            first = (
                f"read day first, which parses {day} of these values "
                f"against the month-first reading's {month}."
            )
        elif month > day:
            first = (
                f"read month first, though you asked for day first, "
                f"because it parses {month} against {day}."
            )
        else:
            first = (
                f"read day first because you asked for it: both "
                f"readings parse {day} of these values and the values "
                f"themselves do not settle which is right."
            )
        if used != READING_DAY_FIRST and used != READING_MONTH_FIRST:
            raise ValueError(UNAUTHORIZED_NOTE_ARGUMENT)
        if day_only > 0 and month_only > 0:
            # THE COMPOSITION IS EXACT: one space after the first
            # clause's closing stop, and no conjunction or joining word.
            return (
                f"{first} This column contradicts itself: {day_only} "
                f"values only a day-first reading accepts, and "
                f"{month_only} only a month-first one."
            )
        return first
    if form == REMARK_NEAR_CATEGORY_LINE:
        return (
            f"this column was close to the line between a set of "
            f"categories and free text: it has {_whole(arguments, 0)} "
            f"different values and the line is at {_whole(arguments, 1)}"
        )
    if form == REMARK_NO_READING_FITS:
        return (
            f"synthtwin could not settle what this column holds, so none of "
            f"its values is published. Here is why: "
            f"{_said(arguments, 0)} and {_said(arguments, 1)}; a column is "
            f"described as "
            f"numbers, or as dates, only when at least "
            f"{_whole(arguments, 2)} of them "
            f"read that way. It holds {_whole(arguments, 3)} different "
            f"values, where "
            f"a set of categories may hold at most {_whole(arguments, 4)}. "
            f"Describing it "
            f"from the part that does read would publish an average, a "
            f"smallest "
            f"and a largest value that the rest of the column contradicts, "
            f"so "
            f"synthtwin describes it as free text and publishes no value of "
            f"it "
            f"at all. If these are measurements written with a currency "
            f"sign, a "
            f"per-cent sign, a unit such as mg, or a clock time, write them "
            f"as "
            f"plain numbers -- one column for the number, and the unit in "
            f"the "
            f"column name -- and run the command again. "
            f"{_whole(arguments, 5)} of its values are numbers wearing "
            f"one shared piece of text, which is the reading that came "
            f"closest{_removed_said(arguments, 6)}"
        )
    if form == REMARK_SOME_NOT_NUMBERS:
        return (
            f"{_whole(arguments, 0)} value(s) in this column are not "
            f"numbers; they were left out of the statistics and are not "
            f"published"
        )
    if form == REMARK_NEAR_NUMERIC_LINE:
        return (
            f"this column was close to the line between numbers "
            f"and text: {_whole(arguments, 0)} of its "
            f"{_whole(arguments, 1)} values are "
            f"written as numbers, and the line is at {_whole(arguments, 2)}"
        )
    if form == REMARK_GROUP_COMMAS:
        # TWO SENTENCES, BECAUSE THERE ARE TWO SITUATIONS AND THEY ARE
        # not the same news. Argument 1 counts the cells that settled
        # NOTHING -- a comma with three figures after it and no point,
        # which reads either way. Argument 2 counts the cells that
        # settle it as a DECIMAL comma: a group that is not three
        # figures, a first group longer than three, or a point before
        # the comma. Where the second is not zero the column has
        # answered the question itself, and the sentence stops saying
        # "synthtwin cannot tell" and starts saying "your file has told
        # it, and the reading is wrong".
        #
        # It counts CELLS and speaks of them, never of "every value":
        # a column of fifty comma-bearing cells beside fifty plain ones
        # is not uniformly a thousand times out, and its average is not
        # out by that factor either.
        # NEITHER SENTENCE CLAIMS A STATISTIC THIS COLUMN MAY NOT
        # HAVE. An earlier wording said "this column's average, its
        # spread and its ends are wrong with them" -- which is false of
        # a `free_text` column, and a column that PROVES a decimal
        # comma is usually exactly that, because the cells that prove
        # it are not numbers this format reads and the column drops
        # below the parse line because of them. Both sentences now say
        # "any average, spread or ends this profile publishes", which
        # is true whether it publishes them or none.
        #
        # AND THE SETTLED SENTENCE DOES NOT SPEAK FOR THE FILE. Two
        # proof cells beside two hundred legitimate thousands-grouped
        # ones do not make the file European, and declaring that it is
        # would be the same false confidence in the other direction.
        # It says what it saw: this column CONTAINS values that cannot
        # be thousands-grouped.
        if arguments[1]:
            return (
                f"{_whole(arguments, 1)} of this column's values "
                f"cannot be read with the comma as a thousands "
                f"separator -- a thousands group is exactly three "
                f"figures and these are not -- so THIS COLUMN "
                f"CONTAINS VALUES WRITTEN WITH A DECIMAL COMMA, and "
                f"synthtwin does not read those as numbers at all. "
                f"Of the rest, {_whole(arguments, 0)} could be read "
                f"either way and were read with the comma as a "
                f"thousands separator, so `1,795` was read as one "
                f"thousand seven hundred and ninety-five; every one "
                f"of those that was meant the way the values above "
                f"are written has been read a thousand times too "
                f"large, and any average, spread or ends this profile "
                f"publishes for this column are wrong with them. "
                f"Write this column with a decimal point and run the "
                f"command again"
            )
        return (
            f"{_whole(arguments, 0)} of this column's values are "
            f"written with a comma inside the number that could be "
            f"read either way, and synthtwin read every one of them "
            f"with the comma as a thousands separator -- so `1,795` "
            f"was read as one thousand seven hundred and ninety-five. "
            f"MANY COUNTRIES WRITE THE DECIMAL POINT AS A COMMA, and "
            f"if this table is one of them then `1,795` means 1.795 "
            f"and each of those values has been read as a thousand "
            f"times its real size, and every statistic this profile "
            f"publishes about this column was computed from those "
            f"numbers. Nothing in this column settles which was meant. If your "
            f"file writes decimals with a comma, write this column "
            f"with a decimal point instead and run the command again"
        )
    if form == REMARK_PADDED_NUMBERS:
        # IT DECIDES NOTHING, and says so, on the exact pattern the
        # all-different remark set: the column is described as numbers
        # either way, which is what keeps its distribution. What it
        # adds is the one pointer a numeric code column had nowhere. A
        # column wearing an affix has carried this sentence since
        # P4-D4.1; a column of `00100` carried none, and those are the
        # same hazard written two ways.
        return (
            f"{_whole(arguments, 0)} of this column's values are "
            f"written with a leading zero, and synthtwin described "
            f"them as quantities: their average, their spread and "
            f"their ends are in this profile. A number written `00100` "
            f"is usually a code rather than a measurement -- nothing "
            f"is assumed from that, and the column is described as "
            f"numbers either way, which keeps its distribution. If "
            f"these are codes, run the command again with --identifier "
            f"NAME, where NAME is this column's name, and no value of "
            f"this column will be published at all"
        )
    if form == REMARK_ALL_DIFFERENT_NUMBERS:
        return (
            "every value in this column is different. That is not "
            "treated as evidence of anything: the column is described "
            "as numbers, which keeps its distribution. If it is really "
            "a record number, run the command again with --identifier "
            "NAME, where NAME is this column's name, and its values "
            "will be left out of the profile altogether"
        )
    if form == REMARK_SPREAD_OUT_OF_RANGE:
        return (
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
    if form == REMARK_ALL_DIFFERENT_TEXT:
        return (
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
    if form == HEADER_NAMES_BY_OPTION:
        return (
            "The first row was read as the column names because the command "
            "was run with --first-row names."
        )
    if form == HEADER_DATA_BY_OPTION:
        return (
            "The first row was read as the first record because the command "
            "was run with --first-row data, so the columns were named "
            "column_1, column_2, and so on and every record was kept."
        )
    if form == HEADER_NAMES_BY_CONVENTION:
        return (
            "The first row was read as the column names by convention, not "
            "by evidence: a CSV file is normally written with its column "
            "names first, and nothing in this file contradicted that -- no "
            "value in the first row belongs among the values of the column "
            "below it. synthtwin did not check that those values ARE names, "
            "because no such check exists. If that row is really the first "
            "record, run the command again with --first-row data: the "
            "columns are then named column_1, column_2, and so on and every "
            "record is kept."
        )
    if form == HEADER_NAMES_SHOWN_BY_COLUMN:
        return (
            f"column {_whole(arguments, 0)} holds a number in every row "
            f"below it, and its first-row value is not a number"
        )
    # A form listed in `NOTE_ARITY` with no branch above it is a form
    # nobody has written the words for, and the last branch's text is
    # not the right answer for it. It stops here rather than borrowing
    # somebody else's sentence.
    raise ValueError(f"{UNKNOWN_NOTE_FORM} {form}")


# The ONLY forms and positions where an affix spelling is an argument.
# Written as a table rather than as a test on the value, so that
# widening it is an edit somebody must make on purpose: a check that
# asked "is this a string?" would admit any value of any table.
# The contract fixes the order (NF35): argument 1 is the prefix,
# argument 2 the suffix, argument 3 `n_affixed`. The code had the count
# first, which is a different sentence shape from the one the contract
# specifies and would have made a guard written from the contract
# refuse every remark this producer writes.
_BOUND_AFFIX_PLACES: "dict[str, tuple[int, ...]]" = {
    EVIDENCE_AFFIXED: (0, 1),
    REMARK_AFFIXED: (0, 1),
    # THE JOINED-NUMBER SEPARATOR (plan P4-D21), admitted on the same
    # terms as the two affixes and for the same reason: it is a
    # spelling THE SAME BLOCK ALREADY PUBLISHES, under the `separator`
    # key, so the sentence discloses nothing the document does not
    # hold, and a sentence that could not name the character would not
    # let anybody recognize their own column. It is one position, and
    # naming it here rather than testing the value is what keeps
    # widening this an edit somebody makes on purpose.
    EVIDENCE_JOINED: (2,),
}


def takes_a_bound_affix(form: str, place: int) -> bool:
    """Whether this form takes an affix spelling at this position.

    Guarantees:

    - Inputs: a form name and a zero-based argument position.
    - Determinism: a lookup in a fixed table; nothing else is consulted.
    - Boundary: this is the ONE place that decides where the fourth
      argument class is admitted. Both the builder of a sentence and
      the guard that re-checks one ask it, so neither can drift from
      the other into admitting a spelling the other refuses.
    """
    if form not in _BOUND_AFFIX_PLACES:
        return False
    return place in _BOUND_AFFIX_PLACES[form]


def _is_bound_affix(form: str, place: int) -> bool:
    """True where this form takes an affix spelling at this position."""
    return takes_a_bound_affix(form, place)


def note(form: str, arguments: "tuple[object, ...]" = ()) -> Note:
    """Write one sentence of the profile, and say where it came from.

    Guarantees:

    - Inputs: a form of `NOTE_ARITY` and exactly as many arguments as
      that table gives it, each of them a whole number of zero or more,
      a word of `NOTE_ARGUMENT_WORDS`, or a nested (form, arguments)
      pair of this same grammar.
    - Determinism: the same form and arguments always write the same
      sentence.
    - Errors raised: ValueError for an unknown form, for the wrong
      number of arguments, and for an argument the grammar does not
      allow -- which is what a value of the real table is.
    - Boundary: this is the ONLY way a sentence of the finished profile
      is made. The returned Note carries the form and the arguments, so
      `profile.check_publication` can rebuild the text and refuse
      anything it cannot.

    A caller that wants to say something new adds a form to `NOTE_ARITY`
    and a branch to `rendered`. There is deliberately no way to pass
    text through: a sentence about a value would need that value as an
    argument, and no value of a table is one.
    """
    if form not in NOTE_ARITY:
        raise ValueError(f"{UNKNOWN_NOTE_FORM} {form}")
    if len(arguments) != NOTE_ARITY[form]:
        raise ValueError(f"{WRONG_NOTE_ARGUMENTS} {form}")
    for place, argument in enumerate(arguments):
        if _is_bound_affix(form, place):
            # The fourth argument class (plan amendment A-P4-7): an
            # affix spelling, admitted for exactly two forms and
            # exactly two positions in each, because those sentences
            # exist to let somebody recognize THEIR column and a
            # sentence that could not name the pair would never do it.
            # It is a spelling the same block already publishes, so it
            # discloses nothing the document does not hold; the guard
            # checks that identity, positionally.
            if not isinstance(argument, str):
                raise ValueError(UNAUTHORIZED_NOTE_ARGUMENT)
            continue
        if not argument_is_enumerated(argument):
            raise ValueError(UNAUTHORIZED_NOTE_ARGUMENT)
    written = Note(rendered(form, arguments))
    written.form = form
    written.arguments = arguments
    return written


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

    small_cell_floor: int = 1
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
    # FROM CONTRACT VERSION 5 THAT RULE HAS ONE STATED EXCEPTION, and it
    # is not the person's text (owner ruling 2026-08-17, plan amendment
    # A-P3-27 part 3, contract 5 section 6). The settings block also
    # names WHICH MEMBERS of synthtwin's own twenty-three published words a
    # declaration named -- ten spellings and three stand-in numbers,
    # written in the vocabulary's own spelling, identical in every
    # installation, and computed from the command line without reading a
    # cell. `built_in_values_named` below is the whole of it, and its
    # docstring carries the reason and the bound.
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
    # WHAT THE PERSON SAID ABOUT DATES WHOSE DAY AND MONTH ARE BOTH
    # NUMBERS -- written with slashes, with dots, or with a two-figure
    # year (plan P4-D4.6, widened by P4-D15) -- AND IT IS NOT AN ORDER
    # SWAP. A swap can reverse a column against its own
    # evidence: ninety-nine ambiguous slashed cells and one cell only
    # the month-first reading can parse would be read backwards, with
    # the column's ONLY evidence counted as unparsed. So where this is
    # set, BOTH slashed readings are counted and the one that parses
    # strictly more cells wins whatever the declaration said; the
    # declaration decides a count tie and nothing else.
    day_first: bool = False
    # THE LONG-TAIL DETECTION LINE, RECORDED RATHER THAN ASSUMED
    # (contract 4.x, plan P4-D5). It has exactly one permitted value,
    # on the `declaration_matching` precedent, and a loader refuses any
    # other -- because the line is a privacy boundary: a settings key
    # that could move it downward would let a settings combination, a
    # lowered floor included, widen which columns publish labels, which
    # is exactly what the `max` against the floor exists to prevent.
    # It is on the document's face so that a later phase can move it
    # only in the open, by a change to that contract.
    long_tail_minimum_level: int = LONG_TAIL_LINE


def axes_of(role: str, forced_identifier: bool) -> "tuple[str, str, str]":
    """The three axes a column carries beside its role (plan P2-D3).

    Returns (statistical_type, quality_state, structural_role): what
    shape the values have, whether there are usable values at all, and
    whether the column is somebody's key.

    THE THIRD ONE IS NOT DERIVED FROM THE ROLE, and that is the point of
    having it. A column is structurally an identifier exactly when the
    person who owns the table named it with `--identifier`, INCLUDING
    the one case where such a column does not carry the identifier role:
    a declared column whose cells are all blank or all spellings that
    mean "no value" is settled as an empty column before any other rule
    runs, so it arrives here with role `empty` while still being a
    column whose owner said it holds codes. A consumer that read the
    role alone would find no trace of the declaration on that column,
    and would treat it as an ordinary empty one.

    Guarantees:

    - Inputs: a role from `ROLES`, and whether the person declared this
      column. No value of the column is consulted, so the answer cannot
      vary with the data it describes.
    - Determinism: the answer depends only on those two arguments.
    - Errors raised: ValueError when the role is not one this module
      defines axes for, which is an internal invariant: `ROLE_AXES` is
      total over `ROLES` and the suite checks that it stays so.
    - Boundary: no I/O of any kind, and nothing here can publish a value
      -- all six results are words of this module's own vocabulary.
    """
    if role not in ROLE_AXES:
        raise ValueError(f"internal check: no axes are defined for {role}")
    statistical_type, quality_state = ROLE_AXES[role]
    if forced_identifier:
        return (statistical_type, quality_state, STRUCTURAL_IDENTIFIER)
    return (statistical_type, quality_state, STRUCTURAL_DATA)


@dataclasses.dataclass(frozen=True)
class ColumnProfile:
    """One column's description, ready to be written into the profile.

    Every field below the details block is present on EVERY role,
    because it is a field of this class rather than a key some branch
    remembered to add. A count that appears only on the roles someone
    remembered is a count that goes missing exactly when it matters
    (review items P1-R1-F9, P1-R3-F3). The three axes are here for that
    same reason: they are what a consumer dispatches on, so a role that
    carried them and a role that did not would be worse than no axes at
    all.
    """

    name: str
    position: int
    role: str
    # The three axes beside the role (plan P2-D3). `axes_of` above
    # derives them, and its docstring says why the third one cannot come
    # from the role.
    statistical_type: str
    quality_state: str
    structural_role: str
    # The three sentence-bearing fields carry `Note`s, not plain text
    # (plan P2-D2). A sentence of a profile is built by `note` from an
    # enumerated form, and these annotations put that rule where a
    # future edit meets it: assembling one of these out of text is a
    # type error before it is a publication failure.
    detection_evidence: Note
    n_present: int
    n_missing: int
    # Exact source spellings, published only for a role whose values may
    # appear at all, and only at or above the small-cell floor. The key
    # is the spelling character for character; the display boundary is
    # applied where a key is SHOWN and never before it is stored
    # (contract 5 C5-1). Its keys are the table's own text and nothing
    # else: no key here carries a first-party meaning (C5-N5).
    missing_by_source: dict[str, int]
    # The named classes a missing cell fell into. These are synthtwin's
    # own words, so this mapping is safe on every role and is always
    # written in full.
    missing_by_class: dict[str, int]
    # The two counts version 4 kept inside the spellings map, under the
    # two of synthtwin's own words that could collide with somebody's
    # data (contract 5 section 5). How many absent cells held nothing
    # but space -- zero unless at least the floor did -- and how many
    # wore a spelling, or a blankness, fewer than the floor shared.
    n_missing_blank: int
    n_missing_withheld: int
    details: dict[str, object]
    publication_notes: list[Note]
    remarks: list[Note]
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

def _totals(numbers: list[float]) -> "tuple[int, int, int, int, int]":
    """The exact sums of the values and of their squares, cubes and
    fourth powers.

    Returns ``(total, squares, cubes, fourths, base)``, where the values
    are ``a_1 ... a_n`` measured in units of ``2 ** base``:
    ``sum(x) == total * 2 ** base``,
    ``sum(x * x) == squares * 2 ** (2 * base)``,
    ``sum(x * x * x) == cubes * 2 ** (3 * base)`` and
    ``sum(x ** 4) == fourths * 2 ** (4 * base)``. All five are whole
    numbers and all four sums are EXACT -- that is the whole point of
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
    fourths: dict[int, int] = {}
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
            fourths[exponent] = fourths[exponent] + square * square
        else:
            ones[exponent] = significand
            squares[exponent] = square
            cubes[exponent] = square * significand
            fourths[exponent] = square * square
    total = 0
    total_squares = 0
    total_cubes = 0
    total_fourths = 0
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
        total_fourths = total_fourths + (
            fourths[exponent] << (shift + shift + shift + shift)
        )
    return (
        total,
        total_squares,
        total_cubes,
        total_fourths,
        smallest - SIGNIFICAND_BITS,
    )


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


def _exact_ratio(share: float) -> "tuple[int, int]":
    """One rate as the exact pair of whole numbers it really is.

    A rate recorded as `0.01` is not one hundredth: the nearest
    binary64 to one hundredth is a shade above it, and a line computed
    by multiplying that value in binary64 rounds the product back down,
    so a column holding exactly one value in a hundred cleared a line
    the contract says it misses. The contract asks for the EXACT
    product of the recorded rate and the count (its section 4.5.2), and
    a product is only exact if the rate is carried as the whole numbers
    it stands for.

    Every binary64 is a whole number times a power of two, which is
    what `frexp` hands back: the fraction it returns has at most
    fifty-three significant bits, so multiplying it by two to the
    fifty-third is exact and gives that whole number outright.

    Guarantees: accepts a rate of zero or more; returns a numerator and
    a denominator whose quotient IS the rate, with no rounding
    anywhere. Determinism: a function of the rate. Raises TypeError if
    handed anything that is not a float instance, and ValueError for a
    negative rate, which no setting of this tool carries. No I/O.
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


def _needed(share: float, total: int) -> int:
    """The smallest whole number of values that reaches ``share``.

    Thresholds are applied as counts rather than as compared shares, so
    that no rounding of a division can decide a column's role.

    AND THE PRODUCT IS EXACT, which the multiplication was not (review
    item P4-DATE-F1). A rate recorded as `0.01` is not one hundredth:
    the nearest binary64 to one hundredth sits a shade above it, so
    against a hundred values the exact product is a shade above one and
    the line is TWO. Multiplying in binary64 rounded that product back
    down to exactly one and the line came out at ONE, so a column
    holding a single value in a hundred cleared a line the contract
    says it misses. The rate is turned into the whole numbers it stands
    for and the ceiling is taken there, where no rounding is left to
    happen: the contract asks for the exact product of the recorded
    rate and the count (its section 4.5.2), and this is that product.

    Guarantees: accepts a rate and a count; returns the smallest whole
    number of values reaching the rate, never more than the count's own
    exact answer. Determinism: a function of the two. Raises TypeError
    if the rate is not a float instance. No I/O of any kind.
    """
    numerator, denominator = _exact_ratio(share)
    exact = numerator * total
    whole = exact // denominator
    if whole * denominator < exact:
        return whole + 1
    return whole


def _at_most(share: float, total: int) -> int:
    """The largest whole number of values that stays within ``share``.

    The ceiling counterpart of `_needed`, and a count for the same
    reason: `distinct <= 10% of the values` is decided by comparing two
    whole numbers, so no rounding of a division decides a role. Its
    product is exact for the same reason `_needed`'s is: a line built
    by rounding is a line that moves.

    Guarantees: accepts a rate and a count; returns the largest whole
    number of values within the rate. Determinism: a function of the
    two. Raises TypeError if the rate is not a float instance. No I/O.
    """
    numerator, denominator = _exact_ratio(share)
    exact = numerator * total
    whole = exact // denominator
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
        "kurtosis": None,
        "std_unrepresentable": False,
    }
    total, squares, cubes, fourths, base = _totals(numbers)
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
    if count < 4:
        return moments

    # n to the fourth times the fourth central moment, cleared of its
    # denominator, and the kurtosis is its ratio to the spread squared
    # (plan P4-D4.8, owner instruction 2026-08-26).
    #
    # THE k-TH MOMENT ASKS FOR k VALUES, which is why this waits for
    # four where the skewness waits for three. Over three points a
    # fourth moment cannot tell a heavy tail from a light one: it is
    # pinned inside a span narrower than the difference the fact is
    # published to report.
    #
    # WHAT IS PUBLISHED IS THE MOMENT RATIO AND NOT THE EXCESS, so the
    # normal curve reads 3 here rather than 0. That is the same choice
    # the skewness beside it makes -- both are the plain moment
    # measures -- and a reader who wants the excess subtracts three.
    #
    # NO OVERFLOW GUARD, and that is a measurement rather than an
    # oversight. The standard deviation carries `std_unrepresentable`
    # because a spread can be larger than this format holds. A moment
    # RATIO cannot: for any n values the kurtosis lies between 1 and
    # `n - 2 + 1 / (n - 1)`, so it is bounded by the row count and no
    # column can push it out of range. The exact arithmetic above never
    # rounds on the way, so nothing overflows in the middle either.
    tails = (
        count * count * count * fourths
        - 4 * count * count * total * cubes
        + 6 * count * total * total * squares
        - 3 * total * total * total * total
    )
    moments["kurtosis"] = published(
        _rounded_ratio(tails, spread * spread)
    )
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

_EXACTLY_ZERO: "tuple[int, tuple[str, ...], int]" = parsing.EXACTLY_ZERO


def exact_of_spelling(text: str) -> "tuple[int, tuple[str, ...], int] | None":
    """The exact number a spelling denotes, or None when it denotes none.

    The reader of record decides FIRST whether the text is a number this
    format can hold: nothing is exact about a spelling the rest of the
    tool refuses, and asking the question here a second way is how two
    parts of one program come to disagree about what a value is.

    IT IS PUBLIC, AND THE NAME IS THE WHOLE POINT (review items
    P1-R8-F2 and P3-V4-F1). This module decides which cells ARE a value
    by the number their digits denote, and every side that has to agree
    with this module about that question calls this rule rather than
    writing a second one: the validator re-describes a measured file
    with this producer, so any place it decides the same question with
    its own arithmetic can decide it differently, and one that decided
    it in binary64 erased eleven cells this module keeps. A rule two
    modules have to share is a rule with one name.

    Guarantees:

    - Inputs: the text of one cell or one declared value, exactly as it
      is spelled. Nothing else is consulted.
    - Determinism: the answer depends only on the text. Two texts give
      equal triples exactly when they denote the same number, and
      unequal triples exactly when they denote different numbers,
      however close the binary64 values they round to.
    - Errors raised: TypeError if handed anything that is not a string
      instance, through `parsing.classify_number`.
    - Boundary: returns None for every spelling that does not read as a
      number this format can hold, which is the reader of record's own
      answer and never a second reading of it. No I/O of any kind.
    """
    # ONE RULE WITH ONE NAME, AND IT LIVES WHERE EVERY SIDE CAN REACH
    # IT (review item P4-DATE3-F2). The scan itself moved to `parsing`,
    # which every module imports, because the generator may not import
    # this one and was left comparing two spellings after rounding them
    # both to binary64 -- a second opinion about what a number is,
    # which is exactly what this function exists to prevent. The name
    # stays here so that every caller that already asks this module
    # goes on asking it.
    return parsing.exact_of_spelling(text)


def exact_of_number(value: float) -> "tuple[int, tuple[str, ...], int]":
    """The same canonical triple, for a number already held as binary64.

    A finite binary64 value is a whole significand times a power of two,
    which `_parts` gives exactly, and a power of two is a whole number
    of tenths, hundredths and so on: multiplying by five as often as the
    power of two is negative turns it into a whole number of decimal
    places with nothing rounded. The digit count stays under about eight
    hundred for every finite value this format holds, which is what
    makes writing the whole number out affordable here.

    It is public for `exact_of_spelling`'s reason: a candidate this
    module carries as a number, compared with a cell this module carries
    as a spelling, is one comparison, and every side that has to make it
    makes it here.

    Guarantees:

    - Inputs: one finite binary64 value. Nothing else is consulted.
    - Determinism: the answer depends only on that value, and it denotes
      exactly that value -- no rounding happens anywhere in it.
    - Errors raised: none.
    - Boundary: the triple is comparable with `exact_of_spelling`'s, and
      the two are equal exactly when the spelling denotes this number.
      No I/O of any kind.
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
        exact = parsing.exact_of_accepted_number(text)
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
    # Cells whose writer MEANT a number and whose text still settles no
    # sign -- notation that conflicts with itself, and nothing else.
    # This is deliberately narrower than `n_sign_unknown`, which counts
    # every present cell the text leaves unsettled, ordinary text
    # included, because U2 is a margin over `n_present`. The role rule
    # below wants the narrow one: a straggler of ordinary text is a
    # cell the parse line already tolerates, and it says nothing about
    # whether this column counts things.
    n_sign_unsettled_numeric: int
    n_negative_unrepresentable: int
    raw_distinct: int
    folded_counts: dict[str, int]
    # For each folded identity, the EXACT spellings that folded onto it
    # and how many rows wrote each one. `folded_counts` is the total of
    # each of these mappings, and both are kept because they answer
    # different questions: how many rows share a label, and how those
    # rows wrote it (owner decisions 9 and 11).
    #
    # It is counted here, once, with everything else. A rule that needed
    # the spellings and went back to the cells for them would be a
    # second reading of a column this module reads once.
    spellings_by_folded: dict[str, dict[str, int]]
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
    sign_unsettled_numeric = 0
    whole = 0
    fraction = 0
    whole_unknown = 0
    negative_unrepresentable = 0
    all_digits = 0
    code_alphabet = 0
    folded_counts: dict[str, int] = {}
    spellings_by_folded: dict[str, dict[str, int]] = {}
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
        # EVERY present cell is counted here, ordinary text included.
        # The sign and whole-number families are two MARGINS over the
        # present cells, and the contract states them that way: U1 and
        # U2 both sum to `n_present`, and the three key meanings all
        # read "present cells whose notation settles ..." (contract v4
        # section 6.2). A cell of ordinary text settles neither
        # question, so it answers for `n_whole_unknown` and
        # `n_sign_unknown` -- which is exactly what the generation
        # method's construction table ties it to (generation method
        # G10.5 step 1, the "ordinary text" row), and exactly what
        # `_classify` already gives it: SIGN_UNKNOWN and WHOLE_UNKNOWN.
        #
        # This line used to read `if cell.kind != parsing.NOT_A_NUMBER`,
        # which left a text cell out of both families while `n_present`
        # counted it. The producer then wrote a description its own
        # loader refused, and the refusal told the reader their file had
        # been changed since it was written -- blaming a person who had
        # done nothing. Found while transcribing this rule for the
        # version 6 contract, reproduced end to end, and fixed here
        # rather than in the invariant, because the contract, the sealed
        # generation method and the shipped loader all three agree with
        # each other and against this line.
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
            if cell.kind != parsing.NOT_A_NUMBER:
                sign_unsettled_numeric = sign_unsettled_numeric + 1
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
            spellings_by_folded[cell.folded] = {}
        spellings = spellings_by_folded[cell.folded]
        if cell.text in spellings:
            spellings[cell.text] = spellings[cell.text] + 1
        else:
            spellings[cell.text] = 1
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
        n_sign_unsettled_numeric=sign_unsettled_numeric,
        n_negative_unrepresentable=negative_unrepresentable,
        raw_distinct=len(set(present)),
        folded_counts=folded_counts,
        spellings_by_folded=spellings_by_folded,
        all_digits=all_digits,
        code_alphabet=code_alphabet,
    )


# The characters a number this format holds can be written with. Used
# only to narrow the search for a cell's core: a substring the
# classifier accepts is made of these, so a span that contains none of
# them cannot hold one. Getting this wrong makes the search slower or
# makes it miss a core, and the second is why the set is generous --
# every character any accepted numeric form uses is in it, and the
# classifier, not this set, decides what parses.
_CORE_CHARACTERS = frozenset("0123456789+-.,()eE")


def _core_character(character: str) -> bool:
    """Whether a number this format holds could be written with it.

    Whitespace is admitted WHATEVER kind it is, because the classifier
    trims before it reads and therefore accepts a core wearing any of
    it. Listing three spellings of a space -- and missing the em space,
    the no-break space and the line separator -- made the core of
    `5<em space>mg` come out as `5` with the suffix ` mg`, so two cells
    of one column wore two different pairs over a difference the
    classifier cannot see.

    The whitespace test goes through `parsing.trimmed`, which is this
    package's own allowlisted answer to "what counts as space here",
    rather than through a method call on a value this module cannot
    trace. It also keeps ONE answer: the splitter and the classifier
    must agree about what a space is, and asking the same function is
    how that is guaranteed rather than hoped for.
    """
    if not isinstance(character, str):
        raise TypeError(UNAUTHORIZED_NOTE_ARGUMENT)
    if character in _CORE_CHARACTERS:
        return True
    return parsing.trimmed(character) == ""


def _core_spans(text: str) -> "list[tuple[int, int]]":
    """Maximal runs of characters a number could be written with."""
    spans: "list[tuple[int, int]]" = []
    start = None
    for index, character in enumerate(text):
        if _core_character(character):
            if start is None:
                start = index
        elif start is not None:
            spans += [(start, index)]
            start = None
    if start is not None:
        spans += [(start, len(text))]
    return spans


def affixed_split(text: str) -> "tuple[str, str, str] | None":
    """Split a cell into prefix, core and suffix, or None if it is not one.

    Guarantees:

    - Inputs: one cell's text, exactly as the file held it.
    - Determinism: the split is a function of the text alone. Where
      more than one substring parses as a number this format can hold,
      the core is the LONGEST, and of equal-length candidates the
      LEFTMOST -- a total order, so two producers reading one cell
      cannot disagree about where its number begins.
    - Returns None when no substring parses, and when the whole trimmed
      cell is the core: a bare number wears no affix and is not an
      affixed number. At least one side must carry text.
    - The classifier TRIMS, so whitespace between the number and the
      text around it belongs to the CORE and never to the pair. `5mg`,
      `5 mg` and `5  mg` therefore wear the ONE pair -- empty prefix,
      suffix `mg` -- and differ only in their cores. A reader will
      assume the opposite, which is why it is written down here and in
      the contract: a column mixing spaced and unspaced units is a
      one-pair column, not a mixed-affix column that declines.
    - The pair is the EXACT text on either side of the core, with no
      case folding and no inner trimming: `mg` and `MG` are two pairs,
      and so are `$` and `EUR`.
    """
    trimmed = parsing.trimmed(text)
    best_start = -1
    best_length = 0
    for span_start, span_stop in _core_spans(trimmed):
        for begin in range(span_start, span_stop):
            if span_stop - begin <= best_length:
                # Nothing from here on can be longer than what is held.
                break
            for end in range(span_stop, begin + best_length, -1):
                if parsing.classify_number(trimmed[begin:end]) == (
                    parsing.NUMBER
                ):
                    best_start, best_length = begin, end - begin
                    break
    if best_length <= 0:
        return None
    prefix = trimmed[:best_start]
    core = trimmed[best_start : best_start + best_length]
    suffix = trimmed[best_start + best_length :]
    if not prefix and not suffix:
        return None
    return prefix, core, suffix


def _numeric_looking_widths(cells: _Cells) -> "tuple[int, int]":
    """The shortest and longest NUMERIC-LOOKING cell, in characters.

    Producer obligation U-P: both are measured over the cells whose
    writer meant a number -- the ones `_numeric_looking` counts -- and
    never over the whole present population. This role tolerates a
    slack of cells that are not numeric notation at all, and such a
    straggler's length published as a bound would be read as magnitude
    by anybody who trusted the pair.

    Each is a count of characters of the cell's text AS THE FILE SPELLS
    IT, so a padded cell counts its zeros and a signed one counts its
    sign.

    Guarantees: accepts the tally; returns a pair with the smaller
    first, both at least 1. Where the role is reached with no
    numeric-looking cell at all -- which the detection line makes
    impossible, and which is answered here rather than left to raise --
    both come back as 1. Raises nothing. No I/O.
    """
    widths: "list[int]" = []
    for cell in cells.classified:
        if cell.kind == parsing.NOT_A_NUMBER:
            continue
        widths = widths + [len(cell.text)]
    if not widths:
        return (1, 1)
    shortest = widths[0]
    longest = widths[0]
    for width in widths:
        if width < shortest:
            shortest = width
        if width > longest:
            longest = width
    return (max(shortest, 1), max(longest, 1))


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
                exact=exact_of_spelling(spelling),
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


def declarations_named(spellings: "tuple[str, ...]") -> int:
    """How many DIFFERENT values one option named (contract 5 C5-18).

    A count of DECLARATIONS and not of keystrokes (review item
    P3-V9-F7; plan amendment A-P3-37). `--missing-value n/a
    --missing-value " N/A "` is two things typed and ONE declaration:
    the rule in `declaration_matching` folds them together, they take
    exactly the same cells of every column, and no description can tell
    them apart afterwards.

    WHY THE DIFFERENCE MATTERED. `n_declared` used to be how many words
    were typed. A consumer subtracting the two vocabulary lists from it
    to learn how many words of the PERSON'S own were named -- which is
    the whole reason those lists exist -- then invented a word nobody
    typed: two spellings of `n/a` gave `n_declared: 2` beside one
    vocabulary member, so the difference read as one word of the
    person's own, and the validator moved a fully rebuildable column's
    obligations off the checked census on the strength of it. The
    shortfall is now exact, which is what C5-18 promises about it.

    THE FOLDING IS THE PRODUCER'S OWN AND NOT A SECOND RULE. Two
    spellings are one declaration exactly when `_same_declaration` says
    so -- the exact number where both read as one, else the trimmed and
    case-folded spelling -- which is the rule that decided which cells
    the declaration took in the first place.

    Guarantees:

    - Inputs: the spellings the person typed for ONE of the two
      options. No cell, column or document is consulted.
    - Determinism: a fixed function of those spellings, and of their
      SET rather than their order: reordering a command line cannot
      move this number.
    - Errors raised: TypeError if handed anything that is not text,
      through `parsing.folded`.
    - Boundary: no I/O of any kind, and no spelling leaves this
      function -- only how many different ones there were.
    """
    distinct: list[_Declaration] = []
    for declaration in _declarations(spellings):
        known = False
        for already in distinct:
            if _same_declaration(declaration, already):
                known = True
        if not known:
            distinct = distinct + [declaration]
    return len(distinct)


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


def built_in_values_named(
    spellings: "tuple[str, ...]",
) -> "tuple[tuple[str, ...], tuple[float, ...], tuple[str, ...]]":
    """Which of synthtwin's OWN published words a declaration named.

    Contract 5 section 6, invariants C5-16, C5-17 and C5-K1 to C5-K5;
    plan amendment A-P3-27 part 3.

    THE WHOLE OF WHAT THIS MAY WRITE is a member of the twenty-three
    the contract publishes in its own appendix: the eighteen spellings
    `parsing.MISSING_TEXTS` and `parsing.MISSING_TEXTS_EXACT` read as
    "no value", the three stand-in numbers
    `parsing.NUMERIC_SENTINELS` judges, and the two placeholder days
    `parsing.CALENDAR_PLACEHOLDERS` judges. They are synthtwin's
    vocabulary, identical in every installation, and they contain no
    text of anybody's table. A declared value that is not one of them
    reaches NEITHER LIST, and the settings block keeps counting it and
    no more, exactly as version 4 did (C5-18).

    THAT IS A STATEMENT ABOUT THE SETTINGS BLOCK (review item
    P3-V9-F1). It is not a statement that the document withholds the
    word: a `--missing-value` naming somebody's own word puts that word
    into its column's `missing_by_source`, character for character,
    under the ordinary floor (contract 5 section 3.2 way 4). This
    function decides what the SETTINGS carry and decides nothing else,
    and every sentence built on it says which.

    AND WHAT THESE TWO LISTS HOLD IS THE MEMBER: through these lists
    never the spelling somebody typed (C5-17). A person who types
    `" N/A "` gets `n/a` in the document:
    their spacing and their capitals are not carried, because the rule
    that matches a declaration is over the folded form and over the
    number, so the member is the whole of what a consumer needs. Nothing
    a person typed reaches a document through these two lists.

    WHY THIS IS SAFE TO PUBLISH WHEN A SPELLING IS NOT, said here
    because a reader of this function will ask (C5-16, and it LOWERS
    the Phase 1 settings-block rule by exactly this much, on the owner's
    ruling of 2026-08-17). No cell of any table is consulted: the answer
    is a function of what was typed on the command line and of the two
    lists below. A word named but never held by any cell is recorded
    identically to a word every cell held, so the field is not evidence
    about the table -- which is the property the settings block has
    always been required to have.

    Guarantees:

    - Inputs: the spellings the person typed for ONE of the two options.
      Nothing else is consulted -- not a column, not a cell, not the
      other option's list.
    - Determinism: both tuples are sorted -- the texts by code point,
      the numbers by value -- and pairwise distinct, so two runs with
      the same options write the same bytes (C5-K2).
    - Errors raised: TypeError if handed anything that is not text,
      through `parsing.folded`.
    - Boundary: no I/O of any kind, and no value of any table can reach
      the result.
    """
    texts: dict[str, int] = {}
    numbers: dict[float, int] = {}
    days: dict[str, int] = {}
    for spelling in spellings:
        # THE THIRD LIST, and it is the placeholder days (plan
        # amendment A-P4-1 item 3). Its shape and its identity rules
        # are the numeric list's: a member is recorded when the
        # declaration names it, whether or not the table holds it, and
        # the person's own spelling never travels.
        for day in parsing.calendar_placeholders():
            if parsing.folded(spelling) == parsing.folded(day):
                days[day] = 1
        for member in parsing.built_in_missing_texts():
            # ASKED THROUGH THE ONE RULE, so the vocabulary's exact
            # member and its folded members are matched here exactly as
            # they are matched when a cell is read (plan P4-D6.2).
            if parsing.missing_text_matches(spelling, member):
                texts[member] = 1
        exact = exact_of_spelling(spelling)
        if exact is None:
            continue
        for candidate in parsing.NUMERIC_SENTINELS:
            if exact == exact_of_number(candidate):
                numbers[candidate] = 1
    return tuple(sorted(texts)), tuple(sorted(numbers)), tuple(sorted(days))


def is_published_vocabulary(spelling: str) -> bool:
    """Whether this spelling is one of synthtwin's own twenty-three words.

    The question every surface that talks about a declared word has to
    answer the same way: is this word OURS -- one of the ten spellings
    `parsing.MISSING_TEXTS` reads as "no value" or one of the three
    stand-in numbers `parsing.NUMERIC_SENTINELS` judges, all twenty-three
    printed in the contract's own appendix and identical in every
    installation -- or is it a word out of somebody's table?

    WHY IT IS ONE FUNCTION AND NOT THREE. Contract 5 section 3.3.1
    derives, from the description alone, which keys of a column's
    `missing_by_source` are spellings the person typed after
    `--missing-value`: every key that is not blank and is not a member
    of this vocabulary. The validator already asked that question to
    rebuild a reading rule; the summary now asks it to tell a person
    which of their own words the description carries; and the command
    line asks it before either file exists. Three answers that could
    drift apart would put three different sentences in front of one
    researcher about one word.

    Guarantees:

    - Inputs: one spelling, exactly as some cell wrote it or as
      somebody typed it. No cell, column or document is consulted.
    - Determinism: a fixed function of the spelling and of this
      package's own two lists.
    - Errors raised: TypeError if handed anything that is not text,
      through `parsing.folded`.
    - Boundary: no I/O of any kind.
    """
    for member in parsing.built_in_missing_texts():
        if parsing.missing_text_matches(spelling, member):
            return True
    exact = exact_of_spelling(spelling)
    if exact is None:
        return False
    for candidate in parsing.NUMERIC_SENTINELS:
        if exact == exact_of_number(candidate):
            return True
    return False


def _declared_spelling(
    text: str, declarations: "list[_Declaration]"
) -> bool:
    """True when a declaration that names no number matches this spelling."""
    folded = parsing.folded(text)
    for declaration in declarations:
        if declaration.exact is None and folded == declaration.folded:
            return True
    return False


def _rescues_a_vocabulary_cell(
    text: str, declarations: "list[_Declaration]"
) -> bool:
    """Whether a declaration reaches a cell THIS PACKAGE'S OWN LIST claims.

    THE RESCUE TEST, NAMED EXPLICITLY BY THE CONTRACT (C6-32) because
    leaving it to be inferred is how a completeness proof came to be
    carried with one of its ways unproved. A cell this package would
    read as absent is rescued only by a declaration that names the
    member claiming it, under THAT MEMBER'S OWN rule -- so a person who
    types `--keep-value nat` does not rescue cells spelled `NaT`, whose
    member is matched byte for byte.

    Without this, the declaration took effect on the cells while the
    settings block recorded no member as named: the person's own word
    was recorded as a word of their own, the count of members named
    stayed at zero, and the reading rule the description was written
    under could not be rebuilt from it -- which is the defect amendments
    A-P3-34 and A-P3-37 closed twice for the numeric list.

    Guarantees: accepts a cell's text and the declarations of one side;
    returns a truth value. Raises TypeError if handed anything that is
    not text. No I/O of any kind.
    """
    for member in parsing.MISSING_TEXTS_EXACT:
        if text != member:
            continue
        for declaration in declarations:
            if declaration.exact is None and declaration.text == member:
                return True
        return False
    return _declared_spelling(text, declarations)


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


def split_missing(
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
        # THE RESCUE ASKS THE MEMBER'S OWN RULE (contract C6-32). A
        # cell this package's own list claims is reached only by a
        # declaration that names the member claiming it, and for the
        # one exact-spelling member that means byte for byte.
        if _rescues_a_vocabulary_cell(value, kept):
            present += [value]
        elif _rescues_a_vocabulary_cell(value, declared_missing):
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
) -> "tuple[dict[str, int], dict[str, int], int, int]":
    """The two missing mappings and the two counts, under the floor.

    Returns, in this order: the spellings map, the class map, how many
    absent cells held nothing but space, and how many were pooled.

    `missing_by_class` uses only synthtwin's own five words, so it is
    safe on every role and is always written in full. A source spelling
    reaches `missing_by_source` only when at least `small_cell_floor`
    rows share that spelling; everything else is pooled, unnamed, into
    the count returned last.

    THE SPELLING IS STORED EXACTLY, character for character, and the
    display boundary is applied where a key is SHOWN (contract 5
    C5-1 to C5-4, plan amendment A-P3-27 part 1). Version 4 rewrote each
    spelling into its printable form before storing it, so a word
    holding an invisible character and a word holding the printable
    characters that stand for it published one key: two tables needing
    opposite readings produced byte-identical descriptions, and a file
    wearing one of them passed against the other's description. That
    rewriting is a rule about not scrambling somebody's terminal, and it
    belongs at the moment of printing -- which is what `variants` next
    door has always done, for the reason contract 4 section 7.4.2 gives.
    One consequence runs the OTHER way and is not a relaxation
    (C5-8): the floor is now applied to the exact spelling, so two
    spellings that escape alike are counted apart and pooled apart, and
    version 5 names strictly fewer groups there than version 4 did.

    THE MAP HOLDS ONE KEY SPACE (C5-11, C5-N5). Its keys are
    spellings some cell of the table held and nothing else. Blank cells
    and the pooled remainder -- which version 4 wrote into the same map
    under `(blank)` and `(withheld)` -- are the two counts returned
    beside it, so no key of this format can be both somebody's data and
    one of synthtwin's own words. That is what `variants_withheld`
    already does for the label roles. Both counts are floor-governed
    exactly as the two keys they replace were: a blank group smaller
    than the floor is pooled rather than named, so `n_missing_blank` is
    either zero or at least the floor (C5-N4).

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
    blank = 0
    for spelling, _name in missing:
        if not parsing.trimmed(spelling):
            blank = blank + 1
            continue
        if spelling in exact:
            exact[spelling] = exact[spelling] + 1
        else:
            exact[spelling] = 1
    withheld = 0
    for key in sorted(exact):
        if exact[key] >= settings.small_cell_floor:
            by_source[key] = exact[key]
        else:
            withheld = withheld + exact[key]
    named_blank = 0
    if blank >= settings.small_cell_floor:
        named_blank = blank
    else:
        withheld = withheld + blank
    return by_source, pooled, named_blank, withheld


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
        exact = exact_of_number(candidate)
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
        if _declared_number(exact_of_number(candidate), kept):
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
        frequent = occurrences >= _needed(
            settings.sentinel_minimum_share, n_present
        )
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


# -- calendar placeholders --------------------------------------------


def _placeholder_verdicts(
    present: "list[str]",
    format_name: str,
    settings: Settings,
) -> "dict[str, tuple[bool, str, int]]":
    """Decide, for each placeholder day present, whether it means "missing".

    THE NUMERIC RULE, TRANSPOSED TO DAY ORDINALS (plan amendment A-P4-1
    item 3). Every property of `_sentinel_verdicts` carries over and is
    carried over deliberately, because a second rule that merely
    resembles the first is a second rule:

    * the REFERENCE POPULATION excludes EVERY candidate, not only the
      one being judged, so a column holding both placeholders cannot
      make either look ordinary;
    * a candidate the person named with `--keep-value` is data, and
      says so, before any arithmetic runs;
    * fewer than four other values leaves the question unanswerable and
      the candidate is kept with that reason;
    * and the two recorded sentinel settings decide it -- an outlier by
      the interquartile rule and a share reaching the recorded minimum,
      applied as a COUNT.

    The ordinal space is whole days from the same civil epoch the rest
    of this package counts in, so no floating-point value is formed
    anywhere near a calendar and the answer is the same on every
    machine.

    Returns placeholder -> (is missing, reason code, occurrences).
    """
    kept = _declarations(settings.kept_values)
    verdicts: dict[str, tuple[bool, str, int]] = {}
    occurrences_of: dict[str, int] = {}
    days: dict[str, int] = {}
    others: list[float] = []
    for value in present:
        found = parsing.placeholder_day_of(value, format_name)
        if found is not None:
            if found in occurrences_of:
                occurrences_of[found] = occurrences_of[found] + 1
            else:
                occurrences_of[found] = 1
            continue
        pair = parsing.parse_datetime(value, format_name)
        if pair is None:
            continue
        others += [float(_day_ordinal(pair[0]))]
    for candidate in parsing.calendar_placeholders():
        if candidate not in occurrences_of:
            continue
        days[candidate] = _day_ordinal(candidate)
    for candidate in sorted(days):
        occurrences = occurrences_of[candidate]
        # THE PERSON NAMES A SPELLING OF THEIR TABLE, NOT A CANONICAL
        # DAY (review item P4-HOLE-F2). A month-first column writes the
        # far placeholder as `12/31/9999`, and that is what somebody
        # types after `--keep-value`; comparing their word against the
        # canonical `9999-12-31` matched nothing and the cells were
        # taken out over their instruction. So the declaration is asked
        # of the CELLS that denote this candidate, and of the canonical
        # spelling too, because a person may type either.
        if _declared_spelling(candidate, kept):
            verdicts[candidate] = (False, REASON_KEPT_BY_USER, occurrences)
            continue
        if _kept_by_spelling(present, format_name, candidate, kept):
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
        ordinal = float(days[candidate])
        is_outlier = (
            ordinal < lower - distance or ordinal > upper + distance
        )
        frequent = occurrences >= _needed(
            settings.sentinel_minimum_share, len(present)
        )
        if is_outlier and frequent:
            verdicts[candidate] = (
                True,
                REASON_OUTLIER_AND_FREQUENT,
                occurrences,
            )
        elif is_outlier:
            verdicts[candidate] = (False, REASON_TOO_RARE, occurrences)
        else:
            verdicts[candidate] = (
                False,
                REASON_NOT_AN_OUTLIER,
                occurrences,
            )
    return verdicts


def _kept_by_spelling(
    present: "list[str]",
    format_name: str,
    candidate: str,
    kept: "list[_Declaration]",
) -> bool:
    """Whether a declaration names a CELL that denotes this candidate."""
    for value in present:
        if parsing.placeholder_day_of(value, format_name) != candidate:
            continue
        if _declared_spelling(value, kept):
            return True
    return False


def _day_ordinal(canonical: str) -> int:
    """One canonical date's day, counted from the civil epoch."""
    return parsing.days_from_civil(
        int(canonical[0:4]), int(canonical[5:7]), int(canonical[8:10])
    )


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


def _published_day_verdicts(
    verdicts: "dict[str, tuple[bool, str, int]]", settings: Settings
) -> "tuple[list[dict[str, object]], int]":
    """The same publication rule, over the placeholder days.

    The candidate is written as its canonical ISO day and the entries
    are ordered as TEXT, which for these spellings is the same order as
    by day. Below the floor a candidate is counted and not named, for
    the reason the numeric half gives: naming it would publish a value
    the levels are withholding at the same moment.

    A DAY IS NOT A NUMBER AND IS NOT WRITTEN AS ONE. The numeric half
    writes `f"{candidate:g}"`; a day written that way would not be a
    day at all, and the two halves are two functions for exactly that
    reason rather than one with a branch in it.
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
                "candidate": candidate,
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


def _variants(
    spellings: dict[str, int], settings: Settings
) -> "tuple[dict[str, int], dict[str, int]]":
    """How one published label was actually written, under the floor.

    Returns (the spellings that may be named, the anonymous multiplicity
    map of the ones that may not).

    WHY THE PROFILE CARRIES THIS AT ALL (owner decisions 9 and 11). A
    published label is a FOLDED identity -- trimmed and case-folded --
    so a column holding `A`, `a`, `B`, `b` publishes two labels of two
    rows each, and a description built from that alone says nothing
    about the four different values the column holds. Anything built
    from it would repeat where the column never did. The implementer
    proposed accepting that and disclosing it; the owner directed the
    opposite, so the spellings are recorded and the count of different
    values can be kept.

    THE FLOOR GOVERNS A SPELLING EXACTLY AS IT GOVERNS A LABEL. A
    spelling shared by fewer than `small_cell_floor` rows is not named:
    it is counted, unnamed, into the second mapping, whose keys say how
    many rows a held-back spelling covered and whose entries say how
    many different spellings covered exactly that many. Without that
    second mapping a label of eleven rows written eleven different ways
    and one written two ways would be the same profile, and neither
    could be rebuilt.

    Guarantees:

    - Inputs: the exact spellings of ONE folded identity with how many
      rows wrote each, and the settings whose floor governs them.
    - Determinism: the answer depends only on those two, and the named
      spellings are built in sorted order.
    - Errors raised: none.
    - Boundary: a spelling reaches the first mapping only when at least
      `small_cell_floor` rows wrote it -- the same line a whole label
      has to clear -- so nothing crosses it that a label would not, and
      the second mapping names nothing at all.
    """
    named: dict[str, int] = {}
    withheld: list[int] = []
    for spelling in sorted(spellings):
        count = spellings[spelling]
        if count >= settings.small_cell_floor:
            named[spelling] = count
        else:
            withheld += [count]
    return (named, _multiplicity_map(withheld))


def _levels(
    counts: dict[str, int],
    spellings_by_folded: dict[str, dict[str, int]],
    settings: Settings,
) -> _Levels:
    """Published levels, plus everything that did not reach the profile.

    Levels are keyed on the value AFTER trimming and case folding --
    the same key the binary and categorical rules count distinct values
    with. Deciding the role on one key and counting the levels on
    another is what let a column the profile called binary publish
    THREE labels, and what let a lone differently-cased row become a
    level of its own (review item P1-R1-F10).

    Each PUBLISHED level also carries how it was written: `variants`
    names every spelling of it that cleared the floor, and
    `variants_withheld` counts the ones that did not, without naming
    them (owner decisions 9 and 11). `_variants` above states the rule
    and why the profile carries it. A level that did NOT clear the floor
    carries neither, because it has no entry to carry them in: a
    spelling of a label the profile refuses to name may not appear
    beside its count under any other key.

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
            named, withheld = _variants(spellings_by_folded[label], settings)
            entries += [
                {
                    "label": label,
                    "count": count,
                    "variants": named,
                    "variants_withheld": withheld,
                }
            ]
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


def _long_tail_line(settings: Settings) -> int:
    """How many rows a level must cover for the long-tail rule to fire.

    The publication floor or the recorded minimum, whichever is LARGER
    (plan P4-D5, contract 4.x). The max is the rule, not a safety
    margin, and the guarantee it buys is exact: membership at ANY floor
    is a subset of membership at eleven. Raising the floor can only
    remove a column -- publishing a floor-clearing spelling is
    constitutive of the role, so a level too small to be published must
    not be the level that made the column label-publishing. Lowering
    the floor widens which LEVELS of an admitted column are shown, and
    admits no column that was not one at eleven.
    """
    if settings.small_cell_floor > settings.long_tail_minimum_level:
        return settings.small_cell_floor
    return settings.long_tail_minimum_level


def _levels_covering(counts: "dict[str, int]", settings: Settings) -> int:
    """How many folded levels reach the long-tail detection line."""
    line = _long_tail_line(settings)
    found = 0
    for key in sorted(counts):
        if counts[key] >= line:
            found = found + 1
    return found


def _level_details(levels: _Levels, cells: _Cells) -> dict[str, object]:
    """The published block a label-publishing role carries.

    ...AND THE FORMS ITS CELLS WERE WRITTEN IN, ON ALL FOUR OF THEM
    (plan P4-D18, corrected). The census first stood on
    `long_tail_labels` alone, on the reasoning that the other three
    publish their levels so their twins hold them and have no stand-in
    to shape. That reasoning was WRONG, and running the tool on a
    patient table is what showed it: a diagnosis column of five common
    codes and twenty-six rare ones is under the categorical ceiling, so
    it takes `categorical` -- and the floor holds back all
    twenty-six, whose twin cells came out `group-1` through
    `group-24`. Every label role suppresses levels; whether it does is
    a fact about the FLOOR and not about the role. So the census
    stands wherever levels can be held back, which is here.
    """
    return {
        "levels": levels.published,
        "suppressed_levels": levels.suppressed_levels,
        "suppressed_rows": levels.suppressed_rows,
        "suppressed_level_counts": levels.suppressed_counts,
        "shape_forms": _shape_forms(cells),
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
        # ...and the forms its cells were written in, which is what
        # lets a made-up cell look like one of them (plan P4-D18).
        "shape_forms": _shape_forms(cells),
        # The shape of repetition, with no value attached to it (plan
        # P2-D4). A free-text column publishes no value, so without this
        # a column of a hundred different notes and one of fifty notes
        # written twice each are the same description, and anything
        # grouped by this column would behave differently on a twin than
        # on the table. `_n_distinct_by_occurrences` states its key form
        # and exactly what it does and does not disclose; it is the same
        # field, built by the same function, as the one a declared
        # record-number column has carried since review item P1-R8-F4.
        "n_distinct_by_occurrences": _n_distinct_by_occurrences(
            cells.present
        ),
    }


def numeric_style(text: str) -> str:
    """Which of the six forms one numeric cell was written in.

    THE RULE ITSELF IS `parsing.numeric_style`, and this is the name the
    describing side calls it by. It was moved there so that the
    generator, which may not import this module, recounts the twin's
    forms with the SAME ladder rather than a copy of it.

    THE LADDER IS FIRST-MATCH-WINS AND ITS ORDER IS PART OF THE
    CONTRACT, because a producer and a consumer that test the marks in
    different orders disagree about a cell carrying more than one:

    0. surrounding spaces come off; a value wrapped in a matching pair
       of accounting brackets is unwrapped and trimmed again; thousands
       separators are dropped. What is left is the CORE;
    1. `exponent_upper` -- the core holds an `E`;
    2. `exponent_lower` -- the core holds an `e`;
    3. `decimal` -- the core holds a `.`;
    4. `leading_plus` -- the core begins with `+`;
    5. `leading_zero` -- after any leading `-`, the core begins with `0`
       and is longer than that single `0`;
    6. `plain` -- everything else.

    WHY THE TYPE-BEARING FORMS ARE TESTED FIRST. A reader infers a
    decimal column from a decimal point or an exponent anywhere in it,
    so the mark that decides the inferred type is the one that must be
    counted when a cell carries two. `+0.5` is therefore counted as
    `decimal` and its leading plus is lost for that cell; the totals
    still close, and that is the trade this order makes deliberately.

    TWO SOURCE FORMS ARE NOT FORMS HERE, and the consequence is
    recorded rather than left to be discovered: accounting brackets and
    thousands separators are classified by the digits inside them. A
    comma would break a CSV row, and brackets are outside the spellings
    a twin may write, so neither could be reproduced and neither is
    counted as its own form.

    Guarantees:

    - Inputs: the text of one cell, exactly as the file spells it.
      Sensible only for a cell that reads as a number this format can
      hold; every other cell is counted elsewhere.
    - Determinism: the answer depends only on the text.
    - Errors raised: TypeError if handed anything that is not a string
      instance, through `parsing.trimmed`.
    - Boundary: the answer is one of six words of this module's own
      vocabulary, so no spelling and no magnitude of the cell can travel
      out through it. No I/O of any kind.
    """
    return parsing.numeric_style(text)


def _numeric_styles(cells: _Cells) -> dict[str, int]:
    """How many cells of this column used each form, under the floor.

    Counted over the cells that read as a number this format can hold,
    and over no others: a cell too large to hold, or one whose notation
    contradicts itself, is written by a rule of its own and has forms
    this enumeration cannot express, so counting it here would promise
    something no twin could keep.

    THE FLOOR GOVERNS A FORM AS IT GOVERNS A LABEL. A form used by fewer
    than `small_cell_floor` cells has no key of its own; its cells are
    counted into a `(withheld)` remainder, so a single oddly written
    cell cannot be singled out. What the mapping publishes either way is
    a count of cells per form -- no value, no magnitude, no spelling.

    Guarantees: accepts a tally of one column; returns a mapping from
    form names, plus possibly `(withheld)`, to counts that sum to how
    many cells read as numbers this format can hold. Determinism: the
    answer depends only on the tally, and the keys are built in the
    enumeration's order. Raises nothing. No I/O of any kind.
    """
    counts: dict[str, int] = {}
    for cell in cells.classified:
        if cell.kind != parsing.NUMBER:
            continue
        style = numeric_style(cell.text)
        if style in counts:
            counts[style] = counts[style] + 1
        else:
            counts[style] = 1
    published_counts: dict[str, int] = {}
    withheld = 0
    for style in NUMERIC_STYLES:
        if style not in counts:
            continue
        if counts[style] >= cells.settings.small_cell_floor:
            published_counts[style] = counts[style]
        else:
            withheld = withheld + counts[style]
    if withheld:
        published_counts[SUPPRESSED_LABEL] = withheld
    return published_counts


def fraction_width(text: str) -> int:
    """How many figures one `decimal`-styled cell writes after its point.

    THE RULE ITSELF IS `parsing.fraction_width`, and this is the name
    the describing side calls it by, for the reason `numeric_style` is
    reached the same way: the generator may not import this module and
    must recount a twin's widths with the SAME reader rather than a
    copy of it. Two readers of one width is how a census and the file
    it describes come to disagree about a cell neither of them wrote
    wrongly.
    """
    return parsing.fraction_width(text)


def _fraction_widths(cells: _Cells) -> dict[str, int]:
    """How many `decimal`-styled cells wrote each width, under the floor.

    TWO COLUMNS OF THE SAME FORM ARE NOT THE SAME COLUMN.
    Eleven cells reading `1.00` and eleven reading `2.000` are both
    `decimal` under the styles map, which says only that twenty-two
    cells carried a point -- so a twin writing every one of them to one
    place carried the published styles map exactly while writing a
    column no reader of the real table would recognize. This census is
    what the styles map cannot say: not that a point was written, but
    how many figures followed it.

    THE FLOOR GOVERNS A WIDTH AS IT GOVERNS A FORM. A width used by
    fewer than `small_cell_floor` cells has no key of its own and its
    cells are counted into a `(withheld)` remainder, so one oddly
    written cell cannot be singled out by its own width any more than
    by its own form.

    THE KEYS ARE THE WIDTHS AS DECIMAL FIGURES, canonically: no leading
    zero, no sign, no padding, so `2` and never `02`. A key grammar
    left to be inferred is a key two producers spell differently and a
    consumer reads as two widths.

    Guarantees: accepts a tally of one column; returns a mapping from
    canonical width keys, plus possibly `(withheld)`, to counts that sum
    to how many cells of this column were written in the `decimal`
    form. Determinism: the answer depends only on the tally, and the
    keys are built in ascending width order. Raises nothing. No I/O of
    any kind.
    """
    counts: dict[int, int] = {}
    for cell in cells.classified:
        if cell.kind != parsing.NUMBER:
            continue
        if numeric_style(cell.text) != parsing.STYLE_DECIMAL:
            continue
        width = fraction_width(cell.text)
        if width in counts:
            counts[width] = counts[width] + 1
        else:
            counts[width] = 1
    published_counts: dict[str, int] = {}
    withheld = 0
    for width in sorted(counts):
        if counts[width] >= cells.settings.small_cell_floor:
            published_counts[f"{width}"] = counts[width]
        else:
            withheld = withheld + counts[width]
    if withheld:
        published_counts[SUPPRESSED_LABEL] = withheld
    return published_counts


def pad_width(text: str) -> int:
    """How wide one zero-padded cell writes its figure field.

    THE RULE ITSELF IS `parsing.pad_width`, and this is the name the
    census reads it under, exactly as `fraction_width` is.
    """
    return parsing.pad_width(text)


def _shape_forms(cells: _Cells) -> dict[str, int]:
    """How many present cells wore each written form, under the floor.

    THE FACT THAT LETS A HELD-BACK VALUE HAVE A STAND-IN THAT LOOKS
    LIKE ONE. A column whose rare values the floor holds back publishes
    nothing about them, so its twin writes `group-14`: not the right
    length, not the right alphabet, and on a column of hyphenated codes
    it even splits into two parts and passes for one. A form says a
    letter, two figures, a point and a figure -- `A99.9` -- and says
    nothing whatever about WHICH letter or WHICH figures.

    THE FLOOR GOVERNS A FORM AS IT GOVERNS A LEVEL, and here it does
    more work than anywhere else: a form shared by fewer than
    `small_cell_floor` cells is pooled, so a column of prose, where
    every cell's form is its own, publishes nothing but the pool. The
    census therefore selects for STRUCTURE without anybody deciding
    which columns are structured.

    A cell with NO FORM AT ALL is counted NOWHERE -- not named and not
    pooled. `(withheld)` means one thing in this format, a group too
    small to name, and a cell this census does not describe is not a
    small group. The docstring said the opposite of the code for one
    landing; the code was right and this now says what it does.

    Guarantees: accepts a tally of one column; returns a mapping from
    forms, plus possibly `(withheld)`, to counts that sum to the cells
    that HAVE a form -- which is at most the column's present cells,
    and fewer wherever a cell was too long to have one. Determinism: the answer depends only on the
    tally, and the keys are built in sorted order. Raises nothing. No
    I/O of any kind.
    """
    counts: dict[str, int] = {}
    withheld = 0
    for value in cells.present:
        form = parsing.shape_form(value)
        if not form:
            # A CELL WITH NO FORM IS NOT COUNTED AT ALL, and it is not
            # pooled either. `(withheld)` means ONE thing everywhere in
            # this format -- a group too small to name -- and at a
            # floor of one there is no such group, which is a rule the
            # publication guard enforces. A cell too long to have a
            # form is not a small group; it is a cell this census has
            # nothing to say about. Pooling it there put a `(withheld)`
            # key into a floor-one document that the guard, rightly,
            # refused to write.
            continue
        if form in counts:
            counts[form] = counts[form] + 1
            continue
        counts[form] = 1
    # A FORM IS NAMED ON ITS COUNT ALONE, AND NEVER ON WHAT ELSE THE
    # COLUMN HOLDS. That is a rule this census had for a landing, lost,
    # and got back, so it is written down rather than left implied.
    #
    # The rule that was tried, twice, is "do not name a form spelled
    # the same as a present cell". It looks like a privacy rule and it
    # is the opposite of one. It makes suppression DATA-DEPENDENT, and
    # a reader can run the dependency backwards: the published levels
    # of a column wear a form and cover enough rows that SF1 REQUIRES
    # that key; the key is absent; the only rule that removes it is the
    # collision rule; therefore a cell is spelled exactly like the key.
    # A floor-suppressed value, recovered EXACTLY, from published facts
    # and no side knowledge.
    #
    # What it was meant to stop discloses nothing to begin with. The
    # key `@%%.%` is what ANY letter-figure-figure-point-figure column
    # publishes; a reader seeing it cannot tell whether some cell is
    # also spelled that way, and `A99` had two thousand six hundred
    # preimages when the placeholders were `9` and `A`. So the rule
    # trades a coincidence that tells nobody anything for a channel
    # that hands over a suppressed value.
    #
    # Round 2's verification refuted it. Round 3's read asked for it
    # again, on the formless-cell case, and it was BUILT AND REVERTED
    # -- measured: the same column with and without one odd cell gives
    # two documents differing only in whether the census is pooled.
    # A FORM WHOSE SUPPLY IS SMALL NAMES THE VALUES IT DESCRIBES, and
    # that is the deepest thing five adversarial reads found here.
    #
    # `%-` has exactly TEN cells that could have worn it, `0-` through
    # `9-`. A column holding all ten, nine of them often enough to
    # publish, names nine and holds one back -- and a reader with the
    # form and the nine knows the tenth exactly. Worse in free text: a
    # hundred values `0-0` through `9-9` all wear `%-%`, which has
    # exactly a hundred cells, so the census hands over the COMPLETE
    # value set of a role that promises no value at all.
    #
    # THE TEST IS OVER PUBLISHED FACTS ONLY, and that is what makes it
    # safe where the collision rule was not. `form_room` is a property
    # of the FORM and `n_distinct` and the floor are already on the
    # page, so a reader can work out for themselves which forms this
    # rule would refuse -- and an absence they can predict tells them
    # nothing. The rule the census refuses twice over, "do not name a
    # form spelled like a present cell", tested a HIDDEN fact, which
    # is why its absences spoke.
    #
    # `n_distinct` counts the whole column and is therefore at least
    # the values wearing any one form, so the test errs toward
    # refusing -- the safe direction.
    room_needed = cells.raw_distinct + cells.settings.small_cell_floor
    published_counts: dict[str, int] = {}
    for form in sorted(counts):
        if parsing.form_room(form) < room_needed:
            continue
        if counts[form] >= cells.settings.small_cell_floor:
            published_counts[form] = counts[form]
            continue
        withheld = withheld + counts[form]
    if withheld:
        published_counts[SUPPRESSED_LABEL] = withheld
    return published_counts


def _comma_remarks(cells: _Cells) -> "list[Note]":
    """The comma remark, or nothing, for any column that can carry it.

    ONE CALL SITE PER ROLE AND ONE RULE BEHIND THEM. The first
    revision fired this only from the numeric verdict, which left the
    two columns that need it most silent: a column wearing a currency
    sign, whose cores are read as quantities exactly as a bare numeric
    column's cells are; and a column whose European values reach a
    thousand, which DECLINES to free text precisely because `1000,000`
    is not a thousands-grouped number -- so the person was told
    "synthtwin could not settle what this column holds" with no
    mention of the reason sitting in every cell.
    """
    unsettled, settled = _group_comma_cells(cells)
    if not unsettled and not settled:
        return []
    return [note(REMARK_GROUP_COMMAS, (unsettled, settled))]


def _group_comma_cells(cells: _Cells) -> "tuple[int, int]":
    """The cells a comma left unsettled, and the cells that settled it.

    THE SECOND COUNT IS READ OVER EVERY PRESENT CELL and not only over
    the numbers, which is the whole reason it exists. `1000,000` is not
    a number this package reads -- a thousands group cannot be four
    figures -- so it is a straggler, and a column of European values
    that reaches a thousand carries its own proof in a cell the numeric
    census never sees. Counting the proof only among the numbers would
    have missed exactly the columns that settle the question.
    """
    unsettled = 0
    settled = 0
    for cell in cells.classified:
        reading = parsing.comma_reading(cell.text)
        if reading == parsing.COMMA_DECIMAL:
            settled = settled + 1
            continue
        if cell.kind != parsing.NUMBER:
            continue
        if reading == parsing.COMMA_EITHER:
            unsettled = unsettled + 1
    return unsettled, settled


def _padded_cells(cells: _Cells) -> int:
    """How many cells of this column were written with a leading zero.

    Counted off the CELLS rather than read back off the published
    styles map, because the map may have pooled the form below the
    floor -- and a column whose padding was too rare to name is still a
    column whose padding a person should be told about.
    """
    counted = 0
    for cell in cells.classified:
        if cell.kind != parsing.NUMBER:
            continue
        if numeric_style(cell.text) != parsing.STYLE_LEADING_ZERO:
            continue
        counted = counted + 1
    return counted


def _pad_widths(cells: _Cells) -> dict[str, int]:
    """How many `leading_zero`-styled cells wrote each field width.

    TWO CODE COLUMNS OF THE SAME FORM ARE NOT THE SAME COLUMN, which is
    the argument `_fraction_widths` makes about the point and this one
    makes about the padding. A styles map saying `leading_zero: 240`
    says a redundant zero was written two hundred and forty times. It
    does not say the field was five figures wide, so a twin carrying
    that map exactly wrote fields two, three and four figures wide and
    was not wrong by the map -- while a person reading a fixed-width
    code, slicing it, or joining on it held a twin their own code could
    not run against, and no report said a word.

    THE FLOOR GOVERNS A WIDTH AS IT GOVERNS A FORM, for the reason it
    does there: a width fewer than `small_cell_floor` cells share has
    no key of its own and its cells are counted into a `(withheld)`
    remainder, so one oddly written cell cannot be singled out by its
    width.

    THE KEYS ARE THE WIDTHS AS DECIMAL FIGURES, canonically -- no
    leading zero, no sign, no padding -- which is the one grammar the
    contract fixes for a width key, and it would be a poor joke for the
    census of padding to write a padded key.

    Guarantees: accepts a tally of one column; returns a mapping from
    canonical width keys, plus possibly `(withheld)`, to counts that sum
    to how many cells of this column were written in the `leading_zero`
    form. Determinism: the answer depends only on the tally, and the
    keys are built in ascending width order. Raises nothing. No I/O of
    any kind.
    """
    counts: dict[int, int] = {}
    for cell in cells.classified:
        if cell.kind != parsing.NUMBER:
            continue
        if numeric_style(cell.text) != parsing.STYLE_LEADING_ZERO:
            continue
        width = pad_width(cell.text)
        if width in counts:
            counts[width] = counts[width] + 1
        else:
            counts[width] = 1
    published_counts: dict[str, int] = {}
    withheld = 0
    for width in sorted(counts):
        if counts[width] >= cells.settings.small_cell_floor:
            published_counts[f"{width}"] = counts[width]
        else:
            withheld = withheld + counts[width]
    if withheld:
        published_counts[SUPPRESSED_LABEL] = withheld
    return published_counts


def _value_histogram(cells: _Cells, numbers: "list[float]") -> dict[str, int]:
    """How many of this column's numbers fall in each bin.

    THE BIN COUNTS ARE COUNTS AND FALL UNDER THE FLOOR, exactly as a
    level or a field width does: a bin holding fewer than
    `small_cell_floor` values has no key of its own and its values are
    counted into a `(withheld)` remainder. That is what makes a
    histogram cheaper in disclosure than a longer ladder -- a rung is
    an exact value of a real cell and is floor-free, while a bin says
    only how many cells lie between two edges the description already
    implies.

    Guarantees: accepts a tally and its numbers; returns a mapping from
    bin number to count, plus possibly `(withheld)`, summing to how
    many numbers the statistics used. Determinism: the answer depends
    only on the values and the published ends, and the keys are built
    in ascending bin order. Raises nothing. No I/O of any kind.
    """
    if not numbers:
        return {}
    lowest = min(numbers)
    highest = max(numbers)
    # A COLUMN WHOSE ENDS THIS FORMAT CANNOT HOLD PUBLISHES NO
    # HISTOGRAM. Bins between infinite edges have no width and no
    # meaning, and every value would land in one of them, so the honest
    # answer is silence rather than a census nobody can read. The
    # loader accepts an absent histogram, and the generator falls back
    # to the ladder exactly as it did before this fact existed.
    for value in numbers:
        if not math.isfinite(value):
            return {}
    if not math.isfinite(lowest) or not math.isfinite(highest):
        return {}
    # AND THE WIDTH MUST BE INSIDE THE FORMAT TOO, not only the ends. A
    # column running from about -1e308 to about 1e308 has finite ends
    # and a width this format cannot hold, so the bin rule can place
    # nothing and would answer "the first bin" for every value -- which
    # is not a quiet approximation but a false census. Silence is the
    # honest answer.
    if not math.isfinite(highest - lowest):
        return {}
    counts: dict[int, int] = {}
    for value in numbers:
        place = parsing.histogram_bin(value, lowest, highest)
        if place in counts:
            counts[place] = counts[place] + 1
        else:
            counts[place] = 1
    # THIS CENSUS IS ALL OR NOTHING, which is not how its siblings
    # behave and is the right rule for THIS fact.
    #
    # A field-width census with a pooled remainder still says something
    # a twin can hold: the named widths are counts of cells, and a cell
    # can be written at a named width whatever the pooled ones do. A
    # histogram is read by RANK -- bin numbers ascend with the values
    # they hold, and that is what lets a generator put its k-th
    # smallest number where the source's k-th smallest sits. A pooled
    # remainder does not say WHICH bins its values are in, so the ranks
    # the named bins cover are unknown and the map cannot be built at
    # all.
    #
    # Publishing it anyway would publish a fact the twin cannot hold.
    # Measured on the every-role fixture at a raised floor: 169 of 240
    # values pooled, seven bins named, and the twin missed all of them
    # -- a description whose own twin fails its quality report, which
    # is the one thing this product may not do. So a column that cannot
    # publish EVERY bin publishes none, the disclosure question stays
    # simple, and at the default floor of one nothing pools and every
    # column gets its shape.
    for place in sorted(counts):
        if counts[place] < cells.settings.small_cell_floor:
            return {}
    published_counts: dict[str, int] = {}
    for place in sorted(counts):
        published_counts[f"{place}"] = counts[place]
    return published_counts


def _distinct_numbers(cells: _Cells) -> int:
    """How many different NUMBERS this column's numeric cells hold.

    Guarantees: accepts a tally of one column; returns a count of at
    least zero, never more than the count of different spellings.
    Determinism: the answer depends only on the multiset of cells.
    Raises nothing. No I/O of any kind.
    """
    # READ OFF THE RECORD, never asked of the text again. Every cell
    # already carries the exact number it denotes -- `_classify`
    # computed it once, which is structural rule A's whole point -- so
    # calling `exact_of_spelling` here would classify all over again.
    # A test counts how often a numeric column is read that way, and
    # it is right to: the first draft of this asked twice per cell.
    seen: "dict[tuple[int, tuple[str, ...], int], int]" = {}
    for cell in cells.classified:
        if cell.kind != parsing.NUMBER:
            continue
        if cell.exact is None:
            continue
        seen[cell.exact] = 1
    return len(seen)


def _numeric_details(cells: _Cells, whole: bool) -> dict[str, object]:
    """The published description of a numeric column."""
    numbers = cells.numbers
    n_present = len(cells.present)
    details: dict[str, object] = {
        "percentiles": _quantiles(numbers),
        "value_histogram": _value_histogram(cells, numbers),
        # HOW MANY DIFFERENT NUMBERS, as distinct from how many
        # different SPELLINGS (plan P4-D4.9, closing residual R-P4-20).
        # `n_distinct` counts spellings and the contract defines it that
        # way on every role, so `1` and `01` are two of them and one
        # number. Nothing published bound the number count, and a twin
        # could meet the spelling count with the leading-zero family
        # while holding fewer numbers than the real column: measured on
        # a 200-row column of tightly clustered values, the twin held
        # all 166 published spellings and 163 numbers, with no
        # deviation raised anywhere. A reader grouping rows by value
        # met three groups that were not there.
        #
        # COUNTED BY THE EXACT NUMBER EACH CELL ALREADY CARRIES, which
        # is how this module decides which cells are the same value.
        # It is the exact number and not the rounded one, so two
        # spellings that round together but denote different numbers
        # count as two.
        "n_distinct_values": _distinct_numbers(cells),
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
        # How the numbers were WRITTEN, which is not a fact about what
        # they are (owner decision 10). Without it, a column of `0`, `00`
        # and `000` and a column of `0.0`, `00.0` and `000.0` are the
        # same profile, and a reader of either twin would infer a type
        # the real table does not have for one of them.
        "numeric_styles": _numeric_styles(cells),
        # ...and how many figures the ones written with a point wrote
        # after it, which the forms map cannot say (plan P4-D4.5,
        # amendments A-P4-5 and A-P4-6). It is a SIBLING of the forms
        # map and not a key inside it: version 4 requires every value of
        # that map to be an integer summing to the numeric count, so an
        # object among them is a document no loader can read.
        "fraction_widths": _fraction_widths(cells),
        # ...and how wide the ones written with a redundant zero wrote
        # their figure field, which the forms map cannot say either
        # (P4-D14). A SIBLING for the same reason: version 6 requires
        # every value of the forms map to be an integer summing to the
        # numeric count.
        "pad_widths": _pad_widths(cells),
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


# The two slashed readings of one grammar, month-first named first
# because that is the order the rule table tries them in. Each pair is
# the two ways ONE column can be read, which is what makes the
# declaration of P4-D4.6 a question about a pair rather than about a
# member.
# The month-first readings whose choice was a GUESS about a column
# that could have been read either way, and which therefore carry the
# standing warning. The textual pair is absent on purpose: a month name
# settles the order, so nothing was guessed.
_MONTH_FIRST_GUESSES = (
    "month-first-date",
    "month-first-datetime",
    "dotted-month-first-date",
    "two-digit-month-first-date",
)

# Both readings of the two-figure-year family, either of which leaves
# the century undecided by the cell.
_TWO_DIGIT_YEAR_MEMBERS = (
    "two-digit-month-first-date",
    "two-digit-day-first-date",
)

SLASHED_PAIRS = (
    ("month-first-date", "day-first-date"),
    ("month-first-datetime", "day-first-datetime"),
    # ...and the two families of P4-D15 that carry the same ambiguity in
    # different punctuation. A dotted date and a two-figure year say no
    # more about which field is the month than a slashed one does, so
    # they are read by this same machinery rather than by a rule of
    # their own: the evidence of a field above twelve first, then the
    # person's declaration, then the ratified default.
    ("dotted-month-first-date", "dotted-day-first-date"),
    ("two-digit-month-first-date", "two-digit-day-first-date"),
)


@dataclasses.dataclass(frozen=True)
class _SlashedEvidence:
    """What a column itself says about which way its slashes read.

    Four counts, and the two `only` ones are the whole reason the
    declaration is not a bare order swap: a column can hold a cell only
    the month-first reading parses AND a cell only the day-first
    reading parses, which is evidence in both directions and not a
    thing any single reading can be right about.
    """

    used: str
    reading: str
    month_parsed: int
    day_parsed: int
    month_only: int
    day_only: int


def _reads(present: "list[str]", format_name: str) -> "list[bool]":
    """Which of these cells one reading parses."""
    answers: list[bool] = []
    for value in present:
        answers = answers + [
            parsing.parse_datetime(value, format_name) is not None
        ]
    return answers


def _slashed_evidence(
    present: "list[str]", pair: "tuple[str, str]", day_first: bool
) -> _SlashedEvidence:
    """Which reading of one slashed pair this column's values choose.

    EVIDENCE FIRST, AND THE DECLARATION ONLY BREAKS A TIE (plan
    P4-D4.6). The reading that parses strictly more cells wins whatever
    the person said, because a swap that ignored the count would read a
    column backwards over its own single contrary cell and then count
    that cell -- the column's only evidence -- as unparsed.
    """
    month = _reads(present, pair[0])
    day = _reads(present, pair[1])
    month_parsed = 0
    day_parsed = 0
    month_only = 0
    day_only = 0
    for place in range(len(present)):
        if month[place]:
            month_parsed = month_parsed + 1
            if not day[place]:
                month_only = month_only + 1
        if day[place]:
            day_parsed = day_parsed + 1
            if not month[place]:
                day_only = day_only + 1
    used = pair[0]
    reading = READING_MONTH_FIRST
    if day_parsed > month_parsed:
        used = pair[1]
        reading = READING_DAY_FIRST
    elif day_parsed == month_parsed and day_first:
        used = pair[1]
        reading = READING_DAY_FIRST
    return _SlashedEvidence(
        used=used,
        reading=reading,
        month_parsed=month_parsed,
        day_parsed=day_parsed,
        month_only=month_only,
        day_only=day_only,
    )


def _remainder_reading(
    present: "list[str]", settings: Settings
) -> "str | None":
    """The format the NON-PLACEHOLDER cells read under, or None.

    THE ENTRY CONDITION OF THE PLACEHOLDER PASS, and the whole of what
    keeps it from moving a column between roles (plan amendment A-P4-1
    item 3). The candidates are taken out FIRST and the remainder is
    asked to clear the datetime rule's own line by itself: a column
    that is a column of dates without its placeholders is one this pass
    may judge, and a column that is not is one it must leave alone.

    The candidates are recognised under each format in turn, because
    which cells ARE candidates depends on the reading -- `12/31/9999`
    is a placeholder under one slashed member and unreadable under the
    other.

    Guarantees: accepts the present cells and the settings; returns a
    format member or None. Determinism: a function of the two, in the
    format table's own order. Raises nothing. No I/O of any kind.
    """
    for format_name in parsing.DATE_FORMATS:
        remainder: list[str] = []
        placeholders = 0
        for value in present:
            if parsing.placeholder_day_of(value, format_name) is not None:
                placeholders = placeholders + 1
                continue
            remainder += [value]
        if placeholders < 1:
            continue
        needed = _needed(settings.minimum_parse_rate, len(remainder))
        parsed = 0
        for value in remainder:
            if parsing.parse_datetime(value, format_name) is not None:
                parsed = parsed + 1
        if parsed >= needed and parsed:
            return format_name
    return None


def _matching_date_format(
    present: list[str], settings: Settings
) -> (
    "tuple[str, list[tuple[str, str]], list[str], int, "
    "_SlashedEvidence | None] | None"
):
    """The first date format that parses enough of the values.

    Returns (format name, parsed (canonical, offset) pairs, the source
    cells that parsed, count of cells that did not, and the slashed
    evidence where a declaration put a pair in play), or None.
    """
    needed = _needed(settings.minimum_parse_rate, len(present))
    for format_name in parsing.DATE_FORMATS:
        evidence: "_SlashedEvidence | None" = None
        reading = format_name
        if settings.day_first:
            for pair in SLASHED_PAIRS:
                if format_name == pair[0]:
                    evidence = _slashed_evidence(present, pair, True)
                    reading = evidence.used
        good: list[tuple[str, str]] = []
        sources: list[str] = []
        for value in present:
            pair_read = parsing.parse_datetime(value, reading)
            if pair_read is not None:
                good += [pair_read]
                sources += [value]
        if len(good) >= needed and good:
            return reading, good, sources, len(present) - len(good), evidence
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
        if reading == READ_AT_UTC:
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
    resolution = RESOLUTION_DATE
    if format_name == "iso-datetime" or format_name == FORMAT_ISO_MIXED:
        resolution = RESOLUTION_DATETIME
    if format_name == "month-first-datetime":
        resolution = RESOLUTION_DATETIME
    if format_name == "day-first-datetime":
        resolution = RESOLUTION_DATETIME
    if format_name == "year-quarter":
        resolution = RESOLUTION_QUARTER
    if format_name == "iso-month":
        resolution = RESOLUTION_MONTH
    # An offset is NAMED only where at least `small_cell_floor` rows
    # carry it. Publishing the endpoint's offset unconditionally beside a
    # floored `utc_offsets` map named the one rare zone the map had just
    # pooled into `(withheld)` -- a value published in one field of the
    # same block that another field promises to withhold, which is
    # exactly the contradiction review item P1-R1-F10 found.
    offsets = _offset_counts(pairs, settings)
    return {
        "format": format_name,
        "resolution_mix": _resolution_mix(format_name, sources),
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


# The joint ISO reading's own name, used where a rule has to tell it
# from the two members it joins.
FORMAT_ISO_MIXED = "iso-mixed"


def _resolution_mix(
    format_name: str, sources: "list[str]"
) -> "dict[str, int]":
    """How many parsed cells of this column wore each form (C6-25).

    ONE KEY ON A SINGLE-FORMAT COLUMN -- its own form, carrying every
    cell that parsed -- and exactly the two ISO members on a column the
    joint reading claimed. No other key set conforms, and the counts
    are exact with no floor: a two-member space beside the published
    parsed total makes a pooled remainder recoverable by subtraction,
    so a floor would withhold nothing, and what the fact carries is a
    count of FORMS rather than any value of the table.

    Guarantees: accepts a format member and the source cells that
    parsed under it; returns a mapping whose values sum to how many
    there were. Determinism: a function of the two, with the keys built
    in the format table's own order. Raises nothing. No I/O of any kind.
    """
    if format_name != FORMAT_ISO_MIXED:
        return {format_name: len(sources)}
    counted = {"iso-date": 0, "iso-datetime": 0}
    for value in sources:
        if parsing.parse_datetime(value, "iso-datetime") is not None:
            counted["iso-datetime"] = counted["iso-datetime"] + 1
            continue
        counted["iso-date"] = counted["iso-date"] + 1
    return counted


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
        return READ_AT_LOCAL
    return READ_AT_UTC


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
    """One role decision, with everything it wants to publish.

    The evidence, the notes and the remarks are `Note`s rather than
    plain strings, and the annotations say so: a sentence of the
    finished profile is built by `note` from an enumerated form, and a
    branch that assembled one out of text would be caught by the type
    check before the publication guard ever saw it (plan P2-D2).
    """

    role: str
    evidence: Note
    details: dict[str, object]
    notes: list[Note]
    remarks: list[Note]


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


@dataclasses.dataclass(frozen=True)
class _Clock:
    """One column's clock reading: the form, and the cells under it."""

    form: str
    # The text of every present cell the winning form accepted, in row
    # order. The cells it did not accept -- the other form's among them
    # -- are COUNTED and not listed: nothing of an unreadable cell is
    # published, and `n_unparsed` is the whole of what is said about
    # them.
    values: "list[str]"
    n_unparsed: int


def clock_reach(cells: _Cells) -> int:
    """How many present cells the BEST clock reading accepted.

    The count the closer of the two forms reached, whether or not it
    cleared the detection line -- so a column that declined can still
    say how far this reading got. Zero where no cell wore either form.

    A column that publishes nothing owes its owner the reason, and the
    reason is a set of counts (contract C6-5): the competing-readings
    remark already names how much of the column read as numbers, as
    dates and as one shared piece of text, and without this one it
    stayed silent about the reading that came closest on a column of
    clock times.

    Guarantees: accepts a tally of one column; returns a count of its
    present cells. No spelling of the column travels out through it.
    Determinism: a function of the cells alone. Raises nothing. No I/O
    of any kind.
    """
    best = 0
    for form in parsing.CLOCK_FORMS:
        found = 0
        for text in cells.present:
            if parsing.clock_form(text) == form:
                found = found + 1
        if found > best:
            best = found
    return best


# THE SEPARATORS A JOINED CELL MAY USE (plan P4-D21). Deliberately a
# short fixed list, and deliberately NOT the shape alphabet: a character
# that can join two numbers has to be one nobody writes INSIDE a number,
# so the point and the comma are absent -- `1.5` and `1,795` are single
# numbers this package already reads, and letting either join two would
# turn every decimal column into a pair.
JOINED_SEPARATORS = ("/", "-", ":", "|", ";", "_")

# THE SPACINGS A JOINED CELL MAY PUT AROUND ITS MARK (plan P4-D24). A
# pressure charted `120 / 80` is the same reading as `120/80` and was
# read as free text, which publishes nothing: the mark alone did not
# match and no rule looked further. The whole separator -- mark and
# spaces together -- is what a cell is split on and what the
# description publishes, so a twin writes back the spacing the table
# used. Only these three: a mark with no spaces, with one on each side,
# and with one after it, which is how a person writes a ratio.
JOINED_SPACINGS = ("", " ", "")
JOINED_TAILINGS = ("", " ", " ")


@dataclasses.dataclass(frozen=True)
class _Joined:
    """One column's reading as numbers joined in a cell.

    NOT *whole* numbers: a part may carry one decimal point, which is
    what lets a ventilator ratio be read. Every surface said "whole"
    until 2026-08-26, including the sentence a person reads.
    """

    separator: str
    n_parts: int
    # One list per position, in row order, holding the text of that
    # position for every cell that wears the reading.
    parts: "list[list[str]]"
    n_joined: int
    n_unparsed: int


def _reads_as_one_number(text: str) -> bool:
    """Whether one part of a joined cell is a plain number.

    Figures, and at most one point with figures on both sides of it.
    No sign, because a leading minus cannot be told from the mark a
    cell might be split on. Figures are tested against fixed ASCII
    rather than `str.isdigit`, for the reason `parsing._is_a_digit`
    gives: five supported Pythons carry five Unicode databases, and
    `str.isdigit` is true of characters this package must not read as
    figures.
    """
    if not text:
        return False
    points = 0
    for character in text:
        if character == ".":
            points = points + 1
            continue
        if not ("0" <= character <= "9"):
            return False
    if points > 1:
        return False
    if points == 1:
        if text[0] == "." or text[len(text) - 1] == ".":
            return False
    return True


def splits_into_numbers(text: str, separator: str) -> "list[str] | None":
    """The parts of one cell under one separator, or None.

    ``separator`` is the WHOLE separator, mark and any spaces around
    it, so `120 / 80` splits on `" / "` and its twin is written back
    the same way (plan P4-D24).

    A part may carry a decimal point, which an I:E ratio of `1:1.5`
    needs and which the first build of this role refused, sending the
    column to free text where it published nothing. **This function was
    called `splits_into_wholes` until 2026-08-26**, and the name was
    the origin of a false sentence on six surfaces: a reader who
    trusted it wrote "whole numbers" into the profile, the front page,
    the changelog and the contract, of a reading that accepts `1:1.5`.

    The type gate is the offline audit's: it accepts no method call on
    a value it cannot trace, and a cell arrives here from a list this
    function did not build.
    """
    if not isinstance(text, str):
        raise TypeError("a cell must be text")
    if not separator:
        return None
    parts: "list[str]" = []
    current = ""
    at = 0
    while at < len(text):
        matched = True
        for step in range(len(separator)):
            if at + step >= len(text) or text[at + step] != separator[step]:
                matched = False
                break
        if matched:
            parts = parts + [current]
            current = ""
            at = at + len(separator)
            continue
        current = current + text[at]
        at = at + 1
    parts = parts + [current]
    if len(parts) < 2:
        return None
    for part in parts:
        if not _reads_as_one_number(part):
            return None
    return parts


def _joined_reading(cells: _Cells) -> "_Joined | None":
    """The one joined-number reading this column wears, or None.

    Guarantees:

    - Determinism: separators are tried in a fixed order and every cell
      is read by `_splits_into_numbers`, a function of the cell alone.
    - The test is the contract's: at least the parse-line COUNT of
      present cells split into the SAME number of parts under ONE
      separator. A count, never a compared share, so no rounding of a
      division decides a role.
    - Boundary: reads the classified cells' text and nothing else.

    THIS IS NEVER CONSULTED UNLESS THE PERSON NAMED THE COLUMN, and the
    reason is a measurement rather than a caution (plan P4-D21). Asked
    of the columns this project already tests, a rule that read the
    VALUES would claim `visit_date` (`2023-02-12` is three whole
    numbers joined by `-`), `seen_at` (`09:30` is two joined by `:`),
    and -- past every rule order that could save the first two --
    `lab_code` (`1923-1`) and `ndc_code` (`00052-0052-52`), which are
    CODES. Claiming those would publish the smallest and largest of
    their parts, which are fragments of real codes, and would undo the
    round trip amendment A-P4-38 was built to guarantee. A blood
    pressure and a lab code are both figures joined by a mark, and
    nothing in either says which. So the caller asks only under the
    declaration, exactly as `taxonomy._decide`'s RULE 5 has said since
    review item P1-R6-F7 that such a thing must be.
    """
    present = cells.present
    n_present = len(present)
    if n_present == 0:
        return None
    needed = _needed(cells.settings.minimum_parse_rate, n_present)
    tried: "list[str]" = []
    for mark in JOINED_SEPARATORS:
        for spacing in range(len(JOINED_SPACINGS)):
            tried = tried + [
                JOINED_SPACINGS[spacing] + mark + JOINED_TAILINGS[spacing]
            ]
    for separator in tried:
        counted: "dict[int, int]" = {}
        for value in present:
            split = splits_into_numbers(value, separator)
            if split is not None:
                width = len(split)
                counted[width] = counted[width] + 1 if width in counted else 1
        for width in sorted(counted):
            if counted[width] < needed:
                continue
            columns: "list[list[str]]" = [[] for _each in range(width)]
            worn = 0
            for value in present:
                split = splits_into_numbers(value, separator)
                if split is None or len(split) != width:
                    continue
                worn = worn + 1
                for place in range(width):
                    columns[place] = columns[place] + [split[place]]
            return _Joined(
                separator=separator,
                n_parts=width,
                parts=columns,
                n_joined=worn,
                n_unparsed=n_present - worn,
            )
    return None


def _joined_details(
    joined: _Joined, settings: Settings
) -> "dict[str, object]":
    """The published block of a joined-number column.

    EACH POSITION GETS THE NUMERIC BLOCK EVERY QUANTITATIVE ROLE GETS,
    computed by the same function over a `_Cells` built from that
    position's text alone. Nothing here does arithmetic of its own: the
    exactness of the ladder, the mean and the spread is the exactness
    `_numeric_details` already carries, and a second implementation of
    it would be a second thing to keep true.

    `min_width` IS WHAT TELLS A PADDED COLUMN FROM A PLAIN ONE. A
    systolic reading of 95 is written `95` and one of 133 is written
    `133`, so widths differ because the NUMBERS differ; a padded column
    writes `007` and `080` at one width whatever the number. Publishing
    the smallest width each position was written at is enough for the
    twin to write both correctly, and it is a width rather than a
    spelling.
    """
    blocks: "list[dict[str, object]]" = []
    widths: "list[int]" = []
    for place in range(joined.n_parts):
        text = joined.parts[place]
        part_cells = _tally(_classify_all(text), len(text), settings)
        # WHETHER THIS POSITION IS WHOLE IS ASKED, not assumed. It was
        # assumed while a part could only be figures; a part may carry a
        # point now (plan P4-D24), and an I:E ratio's second number is
        # `1.5`.
        whole_here = True
        for spelling in text:
            if "." in spelling:
                whole_here = False
        blocks = blocks + [_numeric_details(part_cells, whole_here)]
        smallest = len(text[0])
        for value in text:
            if len(value) < smallest:
                smallest = len(value)
        widths = widths + [smallest]
    # HOW THE POSITIONS MOVE TOGETHER (plan P4-D23). Two numbers per
    # PAIR of positions, in the fixed order (1,2), (1,3), ... (2,3), ...
    # so a reader can find a pair without being told the order:
    #
    #   `part_agreements` -- how strongly the two rise and fall
    #     together, by rank. It is a fact about the PAIRING alone: each
    #     position's own numbers are already published exactly, so this
    #     repeats none of them and adds the one thing that was missing.
    #   `part_above` -- in how many rows the earlier position held the
    #     larger number. A blood pressure answers "all of them", and
    #     that is what stops a twin writing a diastolic above its
    #     systolic.
    #
    # Both are aggregates over every row and name no cell.
    numbers: "list[list[float]]" = []
    for place in range(joined.n_parts):
        counted_here: "list[float]" = []
        for spelling in joined.parts[place]:
            counted_here = counted_here + [float(spelling)]
        numbers = numbers + [counted_here]
    agreements: "list[float]" = []
    above: "list[int]" = []
    for first in range(joined.n_parts):
        for second in range(first + 1, joined.n_parts):
            agreements = agreements + [
                round(parsing.rank_agreement(numbers[first], numbers[second]), 4)
            ]
            counted = 0
            for seat in range(joined.n_joined):
                if numbers[first][seat] > numbers[second][seat]:
                    counted = counted + 1
            above = above + [counted]
    return {
        "separator": joined.separator,
        "n_parts": joined.n_parts,
        "n_joined": joined.n_joined,
        "n_unparsed": joined.n_unparsed,
        "parts": blocks,
        "part_min_widths": widths,
        "part_agreements": agreements,
        "part_above": above,
    }


def _joined_verdict(
    cells: _Cells,
    joined: _Joined,
    notes: "list[Note]",
    remarks: "list[Note]",
) -> _Verdict:
    """The verdict for a declared column of joined whole numbers."""
    return _Verdict(
        role=ROLE_JOINED,
        evidence=note(
            EVIDENCE_JOINED,
            (joined.n_joined, joined.n_parts, joined.separator),
        ),
        details=_joined_details(joined, cells.settings),
        notes=notes,
        remarks=remarks,
    )


def _clock_reading(cells: _Cells) -> "_Clock | None":
    """The one clock form this column wears, or None if it wears none.

    Guarantees:

    - Determinism: every cell is read by `parsing.clock_form`, which is
      a function of the cell alone, and the two forms are tried in a
      fixed order. Nothing here reads a clock or a random source.
    - The test is the contract's: at least the parse-line COUNT of
      present cells wear ONE form. It is a count and never a compared
      share, so no rounding of a division decides a role.
    - THE FINER FORM WINS where both clear the line, which can happen
      only at a lowered parse rate -- no cell wears both, since the two
      have different lengths, so both clearing needs twice the line to
      fit inside the column. `hh-mm-ss` is tried first, which is that
      rule.
    - NO FLOOR IS READ HERE, and that is a decision rather than an
      omission. Two rules of this phase consult `small_cell_floor` at
      detection because publishing a floor-clearing SPELLING is what
      makes them the role they are. This role publishes no spelling of
      the column's own text -- its clock values are the column's, but
      they are published as a range and a ladder, which is the ranges
      class -- so the only threshold it reads is the parse rate.
    - The winning form must have accepted at least ONE cell. At a parse
      rate of zero the line is zero and the contract's T5 is vacuous;
      this is what keeps a cell for the endpoints and the ladder to be
      values of.
    """
    present = cells.present
    if not present:
        return None
    needed = _needed(cells.settings.minimum_parse_rate, len(present))
    for form in (parsing.CLOCK_HH_MM_SS, parsing.CLOCK_HH_MM):
        good: "list[str]" = []
        for text in present:
            if parsing.clock_form(text) == form:
                # The CELL, not a tidied copy of it: what this role
                # publishes are values some row wore, and the reader
                # accepts nothing that needed tidying.
                good = good + [text]
        if len(good) >= needed and good:
            return _Clock(
                form=form,
                values=good,
                n_unparsed=len(present) - len(good),
            )
    return None


def _clock_verdict(
    cells: _Cells,
    clock: _Clock,
    notes: "list[Note]",
    remarks: "list[Note]",
) -> _Verdict:
    """The published block of a column of clock times (contract C6-10).

    FIVE KEYS AND NO SIXTH: which form the cells wore, the earliest and
    latest clock value, an eleven-rung ladder over the parsed values,
    and how many present cells no clock reading accepted.

    THE LADDER IS SELECTION, exactly as the date ladder is: eleven
    order statistics of cells the column really holds, with no
    interpolation anywhere in it. So every rung is a clock value some
    row wore, and `min` and `max` are the endpoints themselves.

    THE ORDER IS TEXT ORDER, and that is safe here rather than
    convenient: both forms are fixed-width and zero-padded, so
    comparing the written cells character by character puts them in
    the same order their ordinals do. The contract states the same
    equivalence and its own T3 is a text comparison for this reason.

    ONE LIMIT STATED AT THE FACT THAT CARRIES IT. The ladder reads the
    day as a LINE from `00:00` to the end of the day, as every ladder
    reads its axis, so a column whose values cluster across midnight is
    described as two clusters with an empty middle and a twin fills
    that middle. The clock face's circular reading is not modeled, in
    the same way a two-humped numeric column's valley is filled by the
    same ladder model today. The rungs stay exact cells either way.
    """
    ordered = sorted(clock.values)
    details: "dict[str, object]" = {
        "clock_form": clock.form,
        "earliest": ordered[0],
        "latest": ordered[len(ordered) - 1],
        "clock_percentiles": _date_ladder(ordered),
        "n_unparsed": clock.n_unparsed,
    }
    if _all_different(cells):
        remarks = remarks + [note(REMARK_ALL_DIFFERENT_NUMBERS)]
    return _Verdict(
        role=ROLE_CLOCK,
        evidence=note(
            EVIDENCE_CLOCK,
            (len(ordered), _clock_form_said(clock.form), clock.n_unparsed),
        ),
        details=details,
        notes=notes,
        remarks=remarks,
    )


def _clock_form_said(form: str) -> str:
    """One clock form as the word a sentence names it by.

    A word of this package's own, chosen from a closed pair, so a
    sentence carrying it carries nothing of anybody's table.
    """
    if form == parsing.CLOCK_HH_MM:
        return NOTE_CLOCK_HOURS_MINUTES
    return NOTE_CLOCK_HOURS_MINUTES_SECONDS


@dataclasses.dataclass(frozen=True)
class _Affixed:
    """One column's affixed reading: the pair, and the cores under it."""

    prefix: str
    suffix: str
    # The core text of every cell wearing the pair, in row order. The
    # cells NOT wearing it are the stragglers the parse line tolerates,
    # and they are counted rather than listed: nothing of a straggler
    # is published.
    cores: "list[str]"
    n_affixed: int


def affixed_reach(cells: _Cells) -> int:
    """How many present cells the BEST affix reading accounted for.

    The count the winning pair reached, whether or not it cleared the
    detection line -- so a column that declined can still say how far
    this reading got. Zero where no cell proposed a pair at all.

    A COLUMN THAT PUBLISHES NOTHING OWES ITS OWNER THE REASON, and the
    reason is a set of counts (contract C6-5). The competing-readings
    remark already names how much of the column read as numbers and how
    much as dates; without this one it stayed silent about the reading
    that came closest on a column of prices, which is the reading its
    owner would recognize.

    Guarantees: accepts a tally of one column; returns a count of its
    present cells. No spelling of the column travels out through it.
    Determinism: a function of the cells alone. Raises nothing. No I/O
    of any kind.
    """
    proposing: "dict[tuple[str, str], int]" = {}
    for text in cells.present:
        split = affixed_split(text)
        if split is None:
            continue
        prefix, _core, suffix = split
        key = (prefix, suffix)
        if key in proposing:
            proposing[key] = proposing[key] + 1
            continue
        proposing[key] = 1
    best = 0
    for key in sorted(proposing):
        if proposing[key] > best:
            best = proposing[key]
    return best


def _affixed_reading(
    cells: _Cells, forced_measurement: bool = False
) -> "_Affixed | None":
    """The one affix pair this column wears, or None if it wears none.

    Guarantees:

    - Determinism: every cell is split by `affixed_split`, which is a
      function of the cell alone, and the winning pair is chosen by
      count with ties broken by the pair's own text. Nothing here reads
      a clock or a random source, and no dictionary order reaches the
      result.
    - The test, and both halves are the contract's: at least the
      parse-line COUNT of present cells wear ONE pair, and that pair's
      cell count is at least `small_cell_floor`. Both are counts and
      neither is a compared share, so no rounding of a division decides
      a role.
    - The floor is read HERE, at detection, deliberately. The pair is
      PUBLISHED, so being able to publish a floor-clearing spelling is
      constitutive of the role: a column that could not publish one
      under the recorded settings takes the next rule instead of taking
      this one and then withholding the thing that makes it this role.
    - A column whose cells wear more than one pair past the line's
      slack returns None -- a recorded decline, not a partial reading.
      Publishing a distribution over the `$` cells of a column that
      also holds `EUR` cells would describe part of a column and drop
      the rest.
    """
    present = cells.present
    if not present:
        return None
    settings = cells.settings
    needed = _needed(settings.minimum_parse_rate, len(present))
    # PASS ONE: which pair. Only cells whose core is a number this
    # format can hold propose a pair, because the role exists to
    # describe a distribution and a pair proposed by cells holding no
    # number would describe none.
    proposing: "dict[tuple[str, str], int]" = {}
    for text in present:
        split = affixed_split(text)
        if split is None:
            continue
        prefix, core, suffix = split
        key = (prefix, suffix)
        if key in proposing:
            proposing[key] = proposing[key] + 1
        else:
            proposing[key] = 1
    if not proposing:
        return None
    # Walked over SORTED keys with a strict comparison, so the winner
    # is the pair the most cells proposed and never the one that
    # happened to be inserted first.
    pair = ("", "")
    best = 0
    for key in sorted(proposing):
        if proposing[key] > best:
            pair = key
            best = proposing[key]
    # THE DETECTION LINE is over the proposing cells: the contract's
    # test is that at least the parse-line count of present cells are
    # AFFIXED NUMBERS -- cells whose core reads as a number -- wearing
    # one pair.
    if best < needed:
        return None
    # TWO readings that both clear the line is an ambiguity, and this
    # role declines an ambiguous column rather than publishing half of
    # it. At the default line the slack is one cell in a hundred and
    # this cannot arise; at a lowered rate it can, and a column of
    # fifty `$` cells and fifty `EUR` cells would otherwise publish a
    # distribution over the dollars and quietly treat every euro as a
    # straggler -- describing part of a column and dropping the rest.
    clearing = 0
    for key in proposing:
        if proposing[key] >= needed:
            clearing = clearing + 1
    if clearing > 1:
        return None
    # PASS TWO: which cells WEAR it. This is a different population and
    # a larger one, and keeping them apart is the whole of C6-7. A
    # column of `5 mg`, `7 mg` and `many mg` wears the pair three
    # times: `n_affixed` is 3 and one core is not numeric at all. The
    # first pass alone would have said 2, and the three non-holdable
    # core classes would have been unreachable -- no producer could
    # ever have written `n_core_not_numeric` above zero.
    prefix, suffix = pair
    cores: "list[str]" = []
    for text in present:
        trimmed = parsing.trimmed(text)
        if not trimmed.startswith(prefix) or not trimmed.endswith(suffix):
            continue
        core = trimmed[len(prefix) : len(trimmed) - len(suffix)]
        if not core:
            # `mg` on its own wears no pair: it IS the suffix, with
            # nothing between the two sides for a number to be.
            continue
        cores = cores + [core]
    n_affixed = len(cores)
    # The floor is read HERE, at detection, deliberately: the pair is
    # PUBLISHED, so being able to publish a floor-clearing spelling is
    # constitutive of the role.
    if n_affixed < settings.small_cell_floor:
        return None
    if not forced_measurement and _wrapped_in_an_address(pair):
        return None
    return _Affixed(
        prefix=prefix, suffix=suffix, cores=cores, n_affixed=n_affixed
    )


# The characters an address may be spelled with, as literal constants
# rather than as method calls: the offline audit accepts membership
# tests on gated text and does not carry `isalpha` or `isalnum`.
_LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
_HOST_CHARACTERS = _LETTERS + "0123456789-."


def _wrapped_in_an_address(pair: "tuple[str, str]") -> bool:
    """Whether this pair is an electronic address around its number.

    RESIDUAL R-P4-39, and this is the THIRD attempt. Both earlier ones
    are written out, because what they got wrong is worth more than
    what this one gets right.

    THE DEFECT. A column of `user12345@example.org` was claimed by the
    affixed role: prefix `user`, suffix `@example.org`, numeric core.
    The block published a ladder, a mean and a spread over the cores --
    real numbers out of real addresses. Measured on 400 rows: the mean
    was 53,574.055, the average of the real identifiers.

    THE FIRST ATTEMPT was a deleted rule resurrected. It declined when
    the cores were all whole, all different, and the pair carried
    letters on the LEFT -- which reads `code1` as a token and `1mg` as
    a quantity, and review item P1-R6-F8 pins those two together
    because nothing in their values tells them apart. Seventeen tests
    refused it.

    THE SECOND ATTEMPT declined on `@` anywhere in the pair, over a
    claim that no unit of measurement uses that character. **The claim
    was false and was refuted the same day**: `100 ms @ ambient` and
    `$100@close` are ordinary quantities whose suffix carries `@`,
    which means "at" -- at a condition, at a price. Both would have
    lost their distribution.

    WHAT THIS ONE DOES DIFFERENTLY, and it is a different KIND of rule
    rather than a narrower version of the same one. The two failures
    above were both negative claims -- "no quantity looks like this" --
    and a negative claim over every column anybody might hold is a
    claim nobody can check. This rule makes a POSITIVE identification
    instead: the suffix is an electronic address, which has a shape of
    its own -- an `@`, then a host, then a dot, then a top label of
    letters. `@close` is not one. `ms @ ambient` is not one.
    `@example.org` is.

    It is still a rule about values, so it is still capable of being
    wrong about a column nobody has shown me. What it is not is a
    guess about which of two indistinguishable shapes a column meant.

    WHAT IT DOES NOT CLOSE. `ACC00012345` still reads as a quantity and
    cannot be told from `USD100` by any property of the values; that
    half of R-P4-39 stays open and its answer is a declaration, which
    is P1-R6-F8's own conclusion.

    Guarantees: accepts the winning affix pair; returns a truth value
    depending on that pair alone. Raises nothing. No I/O, no
    randomness, and no value of the column is published by anything
    here.
    """
    prefix, suffix = pair
    # THE TYPE GATE THE OFFLINE AUDIT ASKS FOR, in the exact form and
    # at the exact place it names: the top of the function, before any
    # method call. A call on a value the audit cannot trace is refused
    # whatever the method is called, because a caller-supplied object
    # may define one of any name. This is the second repair in this
    # landing to trip that rule, and the remedy is the one
    # `splits_into_numbers` already carries.
    if not isinstance(prefix, str):
        raise TypeError("an affix must be text")
    if not isinstance(suffix, str):
        raise TypeError("an affix must be text")
    return _is_an_address(prefix) or _is_an_address(suffix)


def _is_an_address(side: str) -> bool:
    """Whether one affix is an electronic address around a number.

    The shape, checked rather than guessed: an `@`, then a host of
    ordinary host characters, then a dot, then a top label of at least
    two letters. `@close` fails at the dot. `ms @ ambient` fails at the
    label. `@example.org` passes.

    WRITTEN IN A SMALLER VOCABULARY THAN CAME NATURALLY, and that is
    the offline audit's doing rather than a style choice. It accepts
    method calls on gated text only from an enumerated set -- the exact
    set the source tree already calls -- and `rfind`, `isalpha` and
    `isalnum` are not in it. Widening that set to suit one function
    would be changing the scanner to make the text pass, which the
    charter forbids in as many words. So the letter and host tests are
    membership checks against literal constants, which are operators
    rather than method calls, and the search runs on `find`.

    Guarantees: accepts text; returns a truth value depending on that
    text alone. Raises TypeError for anything else. No I/O, no
    randomness.
    """
    if not isinstance(side, str):
        raise TypeError("an affix must be text")
    at = side.find("@")
    if at < 0:
        return False
    host = side[at + 1 :]
    # The last dot of the host, found by walking rather than by
    # `rfind`, which the audit's enumeration does not carry.
    dot = -1
    place = 0
    for character in host:
        if character == ".":
            dot = place
        place = place + 1
    if dot <= 0:
        return False
    label = host[dot + 1 :]
    if len(label) < 2:
        return False
    for character in label:
        if character not in _LETTERS:
            return False
    body = host[:dot]
    if not body:
        return False
    for character in body:
        if character not in _HOST_CHARACTERS:
            return False
    return True


def _affixed_verdict(
    cells: _Cells,
    affixed: _Affixed,
    notes: "list[Note]",
    remarks: "list[Note]",
) -> _Verdict:
    """The `affixed_number` block: a distribution over the CORES.

    TWO POPULATIONS run through this function and they are never the
    same one. The column's CELLS answer for `n_present`, `n_rows` and
    everything the universal keys count. The CORES those cells hold
    answer for the quantitative block and for the four `n_core_*`
    counts. Conflating them was a defect twice in review, so every line
    below says which it is reading.

    The cores are classified by the SAME classifier every other role
    reads cells with, so a core too large to hold, or written in a form
    that conflicts with itself, is counted exactly as it would be on a
    plain numeric column -- and the statistics are computed over the
    cores that hold, never over the cells.
    """
    core_cells = _tally(
        _classify_all(affixed.cores), cells.n_rows, cells.settings
    )
    n_core_numeric = len(core_cells.numbers)
    # `whole_everywhere` over the CORES, on the same test the numeric
    # roles use over their cells.
    core_looking = _numeric_looking(core_cells)
    whole_everywhere = (
        core_cells.n_whole == core_looking and core_looking > 0
    )
    details = _numeric_details(core_cells, whole_everywhere)
    n_present = len(cells.present)
    # The two keys whose population the core substitution does NOT
    # reach. Version 4 defines them over PRESENT CELLS -- "how many
    # present cells the statistics were computed from", "the share of
    # present cells whose writer meant a number" -- so reading them
    # over the cores would leave a straggler in NEITHER count and make
    # both answer for a narrower population than their own published
    # meaning.
    details["n_left_out_of_statistics"] = n_present - n_core_numeric
    details["numeric_share"] = _share(core_looking, n_present)
    details["affix_prefix"] = affixed.prefix
    details["affix_suffix"] = affixed.suffix
    details["n_affixed"] = affixed.n_affixed
    details["n_core_numeric"] = n_core_numeric
    details["n_core_out_of_range"] = core_cells.n_out_of_range
    details["n_core_contradictory"] = core_cells.n_contradictory
    details["n_core_not_numeric"] = core_cells.n_not_numeric
    # Carried by EVERY column of this role, without condition: no test
    # of the values separates an opaque token family from a
    # measurement, so the choice is between telling every such column's
    # owner and telling none.
    pair = (affixed.prefix, affixed.suffix, affixed.n_affixed)
    # ...AND THE ALL-DIFFERENT REMARK IS THE NUMBERS ONE, NOT THE FREE
    # TEXT ONE. The observation reaches this role and must: a column of
    # `R1` to `R240` wearing one prefix is exactly the shape somebody
    # meant as record numbers, and the sentence that says so, with the
    # `--identifier` route beside it, is what makes them look. What may
    # NOT reach it is the free-text form's account of what was done
    # about it. That form says "Nothing from this column is published
    # either way -- no value of it, and no distribution", and then
    # tells the reader to write the values as plain numbers so that
    # "their distribution will be described" -- three clauses that are
    # false, in the plainest-language part of the document, of a block
    # publishing a full ladder and every moment. The plan's word
    # "verbatim" cannot mean a sentence that misdescribes the block it
    # stands in; the contract assigns this role the NUMBERS form, and
    # that is the one a column of `$1` to `$100` now carries.
    if _all_different(cells):
        remarks = remarks + [note(REMARK_ALL_DIFFERENT_NUMBERS)]
    return _Verdict(
        role=ROLE_AFFIXED,
        evidence=note(EVIDENCE_AFFIXED, pair),
        details=details,
        notes=notes,
        remarks=(
            remarks
            + [note(REMARK_AFFIXED, pair)]
            + _comma_remarks(core_cells)
        ),
    )


def _cores_judged(
    cells: _Cells,
    classified: "list[_Cell]",
    missing: "list[tuple[str, str]]",
    verdicts: "dict[float, tuple[bool, str, int]]",
) -> "tuple[list[_Cell], list[tuple[str, str]], dict[float, tuple[bool, str, int]]]":
    """Judge this column's stand-ins over its CORES, and remove them.

    The numeric pass asks its question of whole cells. On this role the
    numbers live inside the affix pair, so the question has to be asked
    of the cores -- and the answer removes the CELL, because a cell
    whose core means "no value" holds no value whatever it wears.

    Returns the surviving records, the absences with the removed cells
    added, and the verdicts to publish. The candidates are published
    exactly as they are on a numeric column: as the number, through the
    standing verdict machinery.
    """
    reading = _affixed_reading(cells)
    if reading is None:
        return classified, missing, verdicts
    # A DECLARATION MATCHES A WHOLE CELL, HERE AS EVERYWHERE, and the
    # core pass has to be told so in the only language it speaks. It
    # reads a column of CORES, and a rule that compared a declaration
    # against a core got both directions wrong at once: the spelling
    # the contract tells an owner to name -- `-999 mg`, the whole cell
    # -- matched no core and was ignored, so eleven cells the owner
    # declared to be data were published as holes on the same page that
    # said the owner had named them; and `-999`, which matches no cell
    # of that column at all and must therefore be inert on it, matched
    # every core and kept the stand-in in the statistics with no
    # verdict published anywhere (C6-117).
    #
    # So the declarations are TRANSLATED before the pass: a cell whose
    # whole trimmed text a `--keep-value` names hands its own core to
    # the pass as kept, and a declaration matching no cell hands over
    # nothing. What is compared is still a whole cell; what the pass
    # sees is the core of the cell that matched.
    settings = _cores_settings(cells, reading)
    cores = _tally(_classify_all(reading.cores), cells.n_rows, settings)
    if _numeric_looking(cores) < _needed(
        settings.minimum_parse_rate, len(cores.present)
    ):
        return classified, missing, verdicts
    judged = _sentinel_verdicts(cores, len(cores.present))
    withheld = sorted(
        candidate for candidate in judged if judged[candidate][0]
    )
    if not withheld:
        # NOTHING IS REMOVED, AND THE VERDICTS ARE STILL THE PASS'S
        # OWN. Returning the verdicts this pass never made threw away
        # every `kept_as_a_number` answer it did make -- so a column
        # whose owner protected its stand-in was described as though
        # nobody had asked, and the one line that would have told them
        # their instruction was honoured never appeared.
        return classified, missing, judged
    removed = [exact_of_number(candidate) for candidate in withheld]
    kept: "list[_Cell]" = []
    for cell in classified:
        split = _core_of(cell.text, reading.prefix, reading.suffix)
        core = _classify(split) if split is not None else None
        if core is not None and core.exact in removed:
            missing = missing + [(cell.text, parsing.MISSING_NUMERIC_SENTINEL)]
        else:
            kept = kept + [cell]
    return kept, missing, judged


def _cores_settings(cells: _Cells, reading: "_Affixed") -> Settings:
    """This column's settings with its declarations read over the cores.

    A `--keep-value` names a whole cell. The pass this feeds reads a
    column of cores, so the declaration is carried across the pair: a
    cell whose whole trimmed text the declaration names contributes its
    own CORE, and a declaration no cell matches contributes nothing and
    is inert, which is what a spelling that names no value of a column
    has always been.

    Guarantees: accepts one column's tally and its affix reading;
    returns a `Settings` differing from the column's own in
    `kept_values` alone. No value of the table travels anywhere but
    into that field, which the caller uses to compare against cores of
    the same column. Determinism: a function of the two inputs, with
    the cores gathered in the column's own order and de-duplicated by a
    sorted walk. Raises nothing. No I/O of any kind.
    """
    settings = cells.settings
    if not settings.kept_values:
        return settings
    declarations = _declarations(settings.kept_values)
    carried: "dict[str, int]" = {}
    for text in cells.present:
        trimmed = parsing.trimmed(text)
        if not _declared_spelling(trimmed, declarations):
            continue
        core = _core_of(text, reading.prefix, reading.suffix)
        if core is None:
            continue
        carried[core] = 1
    return dataclasses.replace(
        settings, kept_values=tuple(sorted(carried))
    )


def _core_of(text: str, prefix: str, suffix: str) -> "str | None":
    """The core of one cell under a known pair, or None if it wears none."""
    trimmed = parsing.trimmed(text)
    if not trimmed.startswith(prefix) or not trimmed.endswith(suffix):
        return None
    core = trimmed[len(prefix) : len(trimmed) - len(suffix)]
    return core if core else None


def _decide(
    cells: _Cells,
    forced_identifier: bool,
    removed: int = 0,
    after_removal: bool = False,
    after_days: bool = False,
    forced_code: bool = False,
    forced_measurement: bool = False,
) -> _Verdict:
    """Pick the one role, testing the rules in the documented order.

    Every rule here routes a column to a role decided by its VALUES.
    Exactly one role is not on that list: `identifier` comes from
    ``forced_identifier`` and from nowhere else, so a column no rule
    claims becomes free text rather than a guessed record number
    (review item P1-R6-F8).

    THE ORDER, and there is only one:

    0. the person's own declaration -- `identifier`;
    0b. the person's OTHER declaration -- `--code`, which decides no
       role by itself and instead SILENCES rules 2, 5, 6, 8 and 9, the
       five that read a cell as something other than a label. What is
       left is exactly the five label roles -- `constant`, `binary`,
       `categorical`, `long_tail_labels`, `free_text` -- which are
       exactly the five that carry a written-form census, so a declared
       code column always records the shapes its codes were written in
       (plan P4-D19). Rule 5's own comment below has asked for this
       since review item P1-R6-F7: it deleted a rule that guessed codes
       from width, said that only the owner of the table knows, and
       named `--identifier` as the way to declare one. `--identifier`
       publishes NOTHING, which is right for a record number and wrong
       for a vaccine code, whose distribution is the point. This is the
       declaration that comment was missing;
    1. no present value at all -- `empty`, settled by the caller;
    2. written as numbers, too few of them holdable -- the
       `numeric_unrepresentable` role;
    3. one distinct value -- `constant`;
    4. two distinct values -- `binary`;
    5. dates, under one documented format, at the parse rate;
    6. numbers, at the parse rate -- `count` or `continuous`;
    7. at most the ceiling of different values -- `categorical`;
    8. clock times, in one of two forms, at the parse rate --
       `time_of_day`;
    9. a number wearing one shared piece of text -- `affixed_number`;
    10. everything else -- `free_text`, which publishes nothing.

    RULES 8 AND 9 SIT WHERE THEY DO ON PURPOSE. Both are tested last
    before the fallback, so each claims only a column every earlier
    rule declined: no column an earlier rule can claim is diverted into
    one of them, and no earlier rule's reach depends on them. Between
    the two, the clock reading is first because it is the more specific
    claim -- clock text rarely splits as an affixed number, and where
    both could fire the time is what the column holds.

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
    notes: list[Note] = []
    remarks: list[Note] = []
    numeric_looking = _numeric_looking(cells)
    strict_needed = _needed(settings.minimum_parse_rate, n_present)
    folded_distinct = len(cells.folded_counts)
    ceiling = _categorical_ceiling(cells)

    # AFTER THE CORE PASS, ONLY THE RULES THE CONTRACT LETS RUN AGAIN.
    # The affix-based stand-in pass runs only once every rule THROUGH
    # `categorical` has declined the un-removed column, and then only
    # the rules after them run over what remains (C6-5). Re-running the
    # whole ladder is not the same thing and is not a smaller mistake:
    # a column of eleven `-999 mg` cells beside eighty-nine cycling
    # `1 mg` to `10 mg` declines to the affixed rule with eleven
    # different spellings, has its stand-ins removed, and then -- with
    # the ladder run again -- comes back as a set of ten CATEGORIES.
    # Its numbers are gone, the type a consumer routes on has changed
    # under it, and nothing on the page says why. The removed cells are
    # what made the earlier rules decline, so letting them decide again
    # lets a removal claim a column no rule would have given it.
    # AND AFTER THE PLACEHOLDER PASS, ONLY RULES 5 ONWARD (plan
    # amendment A-P4-1 item 3, review item P4-HOLE-F1). That pass's
    # gate is narrower than the core pass's: it runs where rules 0
    # through 4 declined, so those four are the ones that may not
    # decide again -- and the datetime rule, which is the whole reason
    # the pass ran, must still be asked. Two hundred and twenty-eight
    # dates over two days beside twelve placeholder cells is a column
    # of dates; re-asking rule 4 made it a two-valued column of labels
    # once the placeholders were gone, which is a column changing role
    # because cells LEFT it.
    if not after_removal:
        # RULE 0 -- the person who knows the table has the last word, and
        # since review item P1-R6-F8 it is also the ONLY word: this is the
        # one route to the identifier role, and every rule below can only
        # send a column somewhere else. A declared identifier beats every
        # rule, including the ones that publish. Eleven identical values
        # used to take the constant branch and publish the value while the
        # user had asked for exactly the opposite (review item P1-R1-F10).
        if forced_identifier and not after_days:
            return _identifier_verdict(cells, notes=notes, remarks=remarks)

        # RULE 0c -- the person's OTHER other declaration (plan P4-D21).
        # `--measurement` says a column holds quantities, including ones
        # written as two or more numbers in one cell. Where the
        # column really is written that way it takes the
        # `joined_numbers` role; where it is not, the declaration
        # decides nothing and every rule below runs untouched, because a
        # column of plain numbers is already read as numbers and needs
        # no help.
        #
        # IT IS ASKED ONLY UNDER THE DECLARATION, and `_joined_reading`
        # carries the measurement that says why: a rule reading the
        # values would claim this project's own date, clock, lab-code
        # and drug-code columns.
        if forced_measurement and not after_days:
            reading = _joined_reading(cells)
            if reading is not None:
                return _joined_verdict(cells, reading, notes, remarks)

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
        if (
            not after_days
            and not forced_code
            and numeric_looking >= strict_needed
            and (len(cells.numbers) < strict_needed)
        ):
            remarks = remarks + [
                note(
                    REMARK_UNREPRESENTABLE,
                    (len(cells.numbers), numeric_looking),
                )
            ]
            notes = notes + [note(NOTE_UNREPRESENTABLE_WITHHELD)]
            return _Verdict(
                role=ROLE_UNREPRESENTABLE,
                # "all N of the M values" was false whenever N < M, and the
                # review's own complaint was a detection_evidence sentence
                # that stated something the column did not show.
                evidence=note(
                    EVIDENCE_UNREPRESENTABLE,
                    (numeric_looking, n_present, len(cells.numbers)),
                ),
                details={
                    # THE TWO WIDTH FACTS, at last (residual R-P4-37).
                    # The contract has stated them on this role in four
                    # places since version 6 -- the added-keys table,
                    # invariant U5, producer obligation U-P and the
                    # forbidden-key matrix -- and the producer never
                    # wrote either, so a producer written to the
                    # contract emitted a block the shipped loader
                    # refused. The role-topology guard carried the
                    # disagreement as a NAMED exception; that exception
                    # is deleted with this.
                    #
                    # MEASURED OVER THE NUMERIC-LOOKING CELLS ONLY,
                    # which is what U-P requires and why they are not
                    # taken off `cells.present`: this role tolerates a
                    # slack of stragglers that are not numeric notation
                    # at all, and a straggler's length published as a
                    # bound would be read as magnitude.
                    "min_length": _numeric_looking_widths(cells)[0],
                    "max_length": _numeric_looking_widths(cells)[1],
                    "n_negative": cells.n_negative,
                    "n_positive": cells.n_positive,
                    "n_sign_unknown": cells.n_sign_unknown,
                    "n_whole": cells.n_whole,
                    "n_fraction": cells.n_fraction,
                    "n_whole_unknown": cells.n_whole_unknown,
                    # The same repetition fact free text and declared record
                    # numbers carry (plan P2-D4), for the same reason: this
                    # column publishes no value either, so its shape of
                    # repetition is otherwise unrecorded, and two columns
                    # with different ones would be one description.
                    "n_distinct_by_occurrences": _n_distinct_by_occurrences(
                        cells.present
                    ),
                },
                notes=notes,
                remarks=remarks,
            )

        # RULE 3 -- one value, repeated.
        if folded_distinct == 1 and not after_days:
            levels = _levels(
                cells.folded_counts, cells.spellings_by_folded, settings
            )
            if levels.suppressed_levels:
                notes = notes + [
                    note(
                        NOTE_ONE_VALUE_BELOW_FLOOR,
                        (settings.small_cell_floor,),
                    )
                ]
            return _Verdict(
                role=ROLE_CONSTANT,
                evidence=note(EVIDENCE_ONE_VALUE, (n_present,)),
                details=_level_details(levels, cells),
                notes=notes,
                remarks=remarks,
            )

        # RULE 4 -- two values. Decided on the SAME key the levels are
        # counted with, so the role and the published list can never
        # disagree about how many values there are.
        if folded_distinct == 2 and not after_days:
            levels = _levels(
                cells.folded_counts, cells.spellings_by_folded, settings
            )
            if levels.suppressed_levels:
                notes = notes + [
                    note(
                        NOTE_ONE_OF_TWO_BELOW_FLOOR,
                        (levels.suppressed_levels, settings.small_cell_floor),
                    )
                ]
            if cells.raw_distinct != 2:
                remarks = remarks + [note(REMARK_CASE_ONLY_TWO)]
            if numeric_looking >= strict_needed or _matching_date_format(
                present, settings
            ):
                remarks = remarks + [note(REMARK_TWO_ALSO_NUMBERS)]
            return _Verdict(
                role=ROLE_BINARY,
                evidence=note(EVIDENCE_TWO_VALUES),
                details=_level_details(levels, cells),
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
        matched = (
            None if forced_code else _matching_date_format(present, settings)
        )
        if matched is not None:
            format_name, pairs, sources, unparsed, evidence = matched
            details = _datetime_details(
                format_name, pairs, sources, unparsed, settings
            )
            if numeric_looking >= strict_needed:
                remarks = remarks + [note(REMARK_DATES_ALSO_NUMBERS)]
            # THE STAMP MEMBER CARRIES THE SAME QUESTION AS THE DATE
            # MEMBER, so it carries the same remark (plan amendment
            # A-P4-1 item 2, which says ambiguity handling is
            # untouched). `03/05/2024 14:05` is as ambiguous as
            # `03/05/2024` is, and a column of the first that said
            # nothing while a column of the second spoke would be
            # telling a reader the question had gone away.
            #
            # UNDER THE DECLARATION IT IS THE OTHER REMARK, AND EXACTLY
            # ONE OF THEM (plan P4-D4.6). The standing remark says the
            # profile may have the month and day the wrong way round,
            # which is a warning about a guess; a column read under the
            # declaration was not guessed at, so it gets the remark
            # that says what decided it and whether its own values
            # disagree with each other.
            if evidence is not None:
                remarks = remarks + [
                    note(
                        REMARK_SLASHED_EVIDENCE,
                        (
                            evidence.day_parsed,
                            evidence.month_parsed,
                            evidence.day_only,
                            evidence.month_only,
                            evidence.reading,
                        ),
                    )
                ]
            elif format_name in _MONTH_FIRST_GUESSES:
                remarks = remarks + [note(REMARK_MONTH_FIRST)]
            # THE CENTURY REMARK IS NOT AN ALTERNATIVE TO EITHER, so it
            # stands outside the chain above. A two-figure year is a
            # guess about the century whichever way the month and day
            # were settled -- by evidence, by a declaration, or by the
            # default -- so the column says so in every one of those
            # cases (plan P4-D15).
            if format_name in _TWO_DIGIT_YEAR_MEMBERS:
                remarks = remarks + [note(REMARK_TWO_DIGIT_YEAR)]
            return _Verdict(
                role=ROLE_DATETIME,
                evidence=note(
                    EVIDENCE_DATES, (len(pairs), n_present, format_name)
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
        if numeric_looking >= strict_needed and not forced_code:
            return _numeric_verdict(cells, notes, remarks)

        # RULE 7 -- a set of categories: at most the ceiling of different
        # values, counted after trimming and case folding. Tested after the
        # numeric rule, so a column of measurements is described as
        # measurements and a small set of labels that happen to be digits is
        # described as labels.
        if folded_distinct <= ceiling:
            levels = _levels(
                cells.folded_counts, cells.spellings_by_folded, settings
            )
            details = _level_details(levels, cells)
            details["level_ceiling"] = ceiling
            if levels.suppressed_levels:
                notes = notes + [_pooled_note(levels, settings)]
            if cells.raw_distinct != folded_distinct:
                remarks = remarks + [note(REMARK_CASE_ONLY_MANY)]
            if ceiling - folded_distinct <= settings.near_threshold_slack:
                remarks = remarks + [
                    note(REMARK_NEAR_CATEGORY_LINE, (folded_distinct, ceiling))
                ]
            return _Verdict(
                role=ROLE_CATEGORICAL,
                evidence=note(
                    EVIDENCE_CATEGORIES,
                    (folded_distinct, ceiling, cells.n_rows),
                ),
                details=details,
                notes=notes,
                remarks=remarks,
            )

    # RULE 8 -- a column of clock times: the `time_of_day` role.
    # `09:30`, `14:05:00`.
    #
    # Before the affixed rule and after every rule that already reads a
    # column well. Its place in front of the affix reading is the
    # contract's and has a reason: clock text rarely splits as an
    # affixed number, but where both could fire the time reading is the
    # more specific claim.
    clock = None if forced_code else _clock_reading(cells)
    if clock is not None:
        return _clock_verdict(cells, clock, notes, remarks)

    # RULE 9 -- one shared piece of text around a number: the
    # `affixed_number` role. `$1,200`, `45%`, `5 mg`, `170cm`.
    #
    # It is tested HERE, after every rule that already reads a column
    # well, and that placement is the whole of its safety: it can claim
    # only a column the earlier rules declined, so no column that reads
    # as a number, a date, a label or a category today is diverted into
    # it. A rule added earlier would have moved columns between roles,
    # which is the one thing this phase's no-regression rule forbids.
    affixed = (
        None
        if forced_code
        else _affixed_reading(cells, forced_measurement)
    )
    if affixed is not None:
        return _affixed_verdict(cells, affixed, notes, remarks)

    # RULE 9b -- a LONG TAIL of labels (plan P4-D5). Past the
    # ceiling, and at least one folded level covers the detection
    # line, which is the publication floor or eleven, whichever is
    # larger.
    #
    # WHY THE LINE HAS A LOWER BOUND OF ITS OWN, and it is the whole
    # of what keeps the free-text promise floor-invariant: lowering
    # the publication floor must not widen WHICH columns publish
    # labels. A column of names or free comments has no eleven-row
    # level at any floor, so it stays free text at every floor and
    # goes on publishing no value at all. Raising the floor raises
    # the line with it, because a level nobody may name is not a
    # level this rule can count.
    #
    # IT SITS LAST BUT ONE, AND THAT IS THE WHOLE OF ITS SAFETY. Every
    # rule above reads a column BETTER: a column of clock times with a
    # repeated time is a column of clock times, and a column of `5 mg`
    # readings with one repeated reading is a column of those. A long
    # tail is what a column is when nothing else fits AND it still
    # holds repeated labels worth publishing -- so it claims only what
    # would otherwise have been free text, which is the one thing this
    # phase's no-regression rule allows.
    # THE DECLARATION LIFTS THE LINE, AND ONLY THE DECLARATION (plan
    # P4-D22). The lower bound above is doing one job: keeping a column
    # of names, addresses or free comments out of the label roles, so
    # that lowering the publication floor never widens WHICH columns
    # publish. That job is a stand-in for a judgement nobody had made.
    # Where the person has said `--code`, they have made it, and the
    # stand-in has nothing left to stand in for.
    #
    # WHAT IT COSTS TO LEAVE IT IN PLACE, measured on a 400-row table.
    # A laboratory-code column of 228 different codes, none repeated
    # more than six times, clears neither door: it is past the
    # categorical ceiling and no level reaches eleven rows. So it fell
    # to free text and published NOTHING -- not one code, not one count
    # -- and its twin held not one real code. `--code` could not help
    # it, because `--code` silences the rules that read a cell as a
    # NUMBER and this column was never being read as one; it was
    # already at the bottom.
    #
    # WHAT IT BUYS. With the codes published at their counts, the twin
    # holds the same codes in the same proportions -- and then EVERY
    # rollup of that column reproduces exactly, including ones this
    # package knows nothing about. Measured on a diagnosis column: the
    # exact codes, the three-character prefixes, the chapter letters
    # and the code lengths all come back identical, and synthtwin has
    # no idea what a chapter is. Hierarchy is not modelled; it is a
    # consequence of holding the right values the right number of
    # times.
    covering = _levels_covering(cells.folded_counts, settings)
    if covering > 0 or forced_code:
        levels = _levels(
            cells.folded_counts, cells.spellings_by_folded, settings
        )
        details = _level_details(levels, cells)
        if levels.suppressed_levels:
            notes = notes + [_pooled_note(levels, settings)]
        if cells.raw_distinct != folded_distinct:
            remarks = remarks + [note(REMARK_CASE_ONLY_MANY)]
        return _Verdict(
            role=ROLE_LONG_TAIL,
            evidence=note(
                EVIDENCE_LONG_TAIL,
                (
                    folded_distinct,
                    ceiling,
                    cells.n_rows,
                    _long_tail_line(settings),
                    covering,
                ),
            ),
            details=details,
            notes=notes,
            remarks=remarks,
        )

    # RULE 10 -- everything else is free text, which publishes nothing.
    #
    # The rules between RULE 7 and this one all read a column BETTER
    # than free text does, and each was added by a ratified decision:
    # the clock, the affix pair and the long tail. Two rules used to
    # stand here as well, and both are gone. One read all-different single tokens as record
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
        _competing_readings(
            cells, ceiling, numbers_said, dates_said, removed
        )
    ]
    return _free_text_verdict(
        cells,
        notes=notes,
        remarks=remarks,
        evidence=note(
            EVIDENCE_NO_READING_FITS,
            (
                numbers_said,
                dates_said,
                folded_distinct,
                ceiling,
                cells.n_rows,
            ),
        ),
    )


def _read_as_numbers(
    numeric_looking: int, n_present: int
) -> "tuple[str, tuple[object, ...]]":
    """How much of a column is written as numbers, in words.

    "Written as" rather than "read as", and deliberately: this is the
    count the numeric line is compared against, and it includes the
    cells whose writer meant a number that no format can hold. Saying
    they "read as numbers" would claim more than the column shows.

    It returns the FORM and its arguments rather than the words, because
    this fragment is never published on its own: it goes inside two
    longer sentences, and a sentence built by formatting one string into
    another is a plain string with no origin, which the publication
    guard refuses (plan P2-D2). `taxonomy.rendered` writes the words.
    """
    return (SAID_WRITTEN_AS_NUMBERS, (numeric_looking, n_present))


def _read_as_dates(present: list[str]) -> "tuple[str, tuple[object, ...]]":
    """How much of a column read as dates, and under which format.

    Returns the form and its arguments, for the reason above: this
    fragment is carried inside a longer sentence.
    """
    best_name, best_count = _best_date_reading(present)
    return (SAID_READ_AS_DATES, (best_count, best_name))


def _removed_said(arguments: "tuple[object, ...]", place: int) -> str:
    """What stand-in judging took out of this column, or nothing at all.

    A clause rather than a sentence of its own, because it belongs to
    the count beside it: a column can be moved across a line by having
    its stand-ins removed, and a reader told only the count that
    remained would be told a number that no longer describes the file
    they are holding. Where nothing was removed the clause is empty --
    naming a removal of none says something happened.
    """
    removed = _whole(arguments, place)
    if removed == 0:
        return ""
    return (
        f", after {removed} of them were read as stand-ins for "
        f"'no value' and taken out -- which is what moved this column "
        f"across a line, so the counts above are of what was left"
    )


def _competing_readings(
    cells: _Cells,
    ceiling: int,
    numbers_said: "tuple[str, tuple[object, ...]]",
    dates_said: "tuple[str, tuple[object, ...]]",
    removed: int,
) -> Note:
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
    return note(
        REMARK_NO_READING_FITS,
        (
            numbers_said,
            dates_said,
            strict_needed,
            folded_distinct,
            ceiling,
            affixed_reach(cells),
            removed,
        ),
    )


def _free_text_verdict(
    cells: _Cells,
    notes: list[Note],
    remarks: list[Note],
    evidence: Note,
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
    # The note covers the WHOLE block, not the part this function used
    # to build. "Only how long they are and how many words they hold"
    # stopped being true the moment the block gained how often the
    # values repeat (plan P2-D4), and a note that promises less than its
    # block contains is how the next field slips past unnoticed --
    # exactly the correction the record-number note took at review item
    # P1-R8-F4.
    notes = notes + [note(NOTE_FREE_TEXT_WITHHELD)]
    if _all_different(cells):
        remarks = remarks + [note(REMARK_ALL_DIFFERENT_TEXT)]
    remarks = remarks + _comma_remarks(cells)
    return _Verdict(
        role=ROLE_TEXT,
        evidence=evidence,
        details=_text_details(cells),
        notes=notes,
        remarks=remarks,
    )


def _pooled_note(levels: _Levels, settings: Settings) -> Note:
    """The note that says how many levels were withheld and how many rows."""
    return note(
        NOTE_LABELS_POOLED,
        (
            levels.suppressed_levels,
            settings.small_cell_floor,
            levels.suppressed_rows,
        ),
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
    return _multiplicity_map([counts[value] for value in sorted(counts)])


def _multiplicity_map(sizes: list[int]) -> dict[str, int]:
    """How many of these groups have one member, two members, and so on.

    THE ONE SHAPE, BUILT IN ONE PLACE. TWO published mappings are this
    same fact about two different things -- how many different values
    cover exactly n rows (`n_distinct_by_occurrences`), and how many
    different spellings of one published label cover exactly n rows
    (`variants_withheld`) -- and they must not drift apart in key form,
    in padding or in order, because a consumer reads them with one
    routine. This said THREE and then named two; the miscount came from
    the contract's own section heading and was found while transcribing
    that section for the self-contained version 6. There is no third:
    this function has exactly two callers, and the only candidate --
    `suppressed_level_counts` -- is a sorted array of integers rather
    than a mapping. `_n_distinct_by_occurrences` above states what this class
    of fact does and does not disclose; that statement holds for every
    caller, because none of them passes anything but group sizes.

    THE KEY FORM: each key is a group size in base ten, left-padded with
    zeros to the width of the largest key in the SAME mapping, because
    the document sorts keys as text and `"10"` sorts before `"2"` when
    written bare. A consumer reads a key as a number; leading zeros do
    not change it.

    Guarantees: accepts the sizes of some collection of groups, each a
    whole number of one or more; returns a mapping whose entries sum to
    how many sizes were given and whose keys, read as numbers and
    weighted by their entries, sum to the total of those sizes. No sizes
    gives an empty mapping. Determinism: the answer depends only on the
    multiset of sizes -- their order cannot reach it -- and the keys are
    built in increasing numeric order. Raises nothing. No I/O of any
    kind.
    """
    tally: dict[int, int] = {}
    for size in sizes:
        if size in tally:
            tally[size] = tally[size] + 1
        else:
            tally[size] = 1
    if not tally:
        return {}
    width = len(f"{max(tally)}")
    shape: dict[str, int] = {}
    for size in sorted(tally):
        shape[_left_padded(size, width)] = tally[size]
    return shape


def _identifier_verdict(
    cells: _Cells,
    notes: list[Note],
    remarks: list[Note],
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
    notes = notes + [note(NOTE_IDENTIFIER_WITHHELD)]
    return _Verdict(
        role=ROLE_IDENTIFIER,
        evidence=note(EVIDENCE_DECLARED_IDENTIFIER),
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
    cells: _Cells, notes: list[Note], remarks: list[Note]
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
        remarks = remarks + [note(REMARK_SOME_NOT_NUMBERS, (unparsed,))]
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
            note(
                REMARK_NEAR_NUMERIC_LINE,
                (numeric_looking, n_present, strict_needed),
            )
        ]
    if cells.raw_distinct >= _needed(
        settings.identifier_uniqueness, n_present
    ):
        remarks = remarks + [note(REMARK_ALL_DIFFERENT_NUMBERS)]
    # ...AND A COLUMN WRITTEN WITH LEADING ZEROS SAYS SO TOO. The
    # all-different remark reaches a column whose every value differs,
    # which a column of codes is not: codes repeat, so that sentence
    # never fires on one. The affixed role has carried its own
    # `--identifier` pointer since P4-D4.1. Between the two, a column
    # of `00100` -- a procedure code, a vaccine code, a zip -- got no
    # pointer at all while being described as a quantity with an
    # average and a spread.
    padded = _padded_cells(cells)
    if padded:
        remarks = remarks + [note(REMARK_PADDED_NUMBERS, (padded,))]
    # ...AND A COMMA INSIDE A NUMBER IS A CHOICE, NOT A READING. This
    # is the one place the package can be wrong by a factor rather than
    # by a rounding, and it was silent about it: a column of European
    # lab values written `1,795` was published with an average a
    # thousand times too large, described as "whole numbers that count
    # things", and nothing anywhere said so.
    remarks = remarks + _comma_remarks(cells)
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
        whole_everywhere
        and cells.n_negative == 0
        and cells.n_sign_unsettled_numeric == 0
    )
    role = ROLE_COUNT if counts_things else ROLE_CONTINUOUS
    if role == ROLE_COUNT:
        evidence = note(EVIDENCE_COUNTS, (numeric_looking,))
    else:
        evidence = note(EVIDENCE_NUMBERS, (numeric_looking, n_present))
    details = _numeric_details(cells, whole_everywhere)
    # A spread larger than this file format can hold is a fact the
    # profile records in a field of its own, and it is also a fact the
    # person running the tool has to be told in words: without this
    # remark the only sign of it is a null where a number belongs
    # (review item P1-R6-F3).
    if details["std_unrepresentable"]:
        remarks = remarks + [note(REMARK_SPREAD_OUT_OF_RANGE)]
    # AND A SHAPE THIS COLUMN COULD NOT PUBLISH IS SAID IN WORDS. The
    # histogram is all or nothing, so a column whose values spread too
    # thinly for the floor publishes an EMPTY object -- and an empty
    # object beside a column full of numbers is exactly the silence
    # this file's other withheld-census notes exist to break. Without
    # it the only sign is an absence, and a reader cannot tell a shape
    # that was held back from a column that never had one.
    if numeric_looking > 0 and not details["value_histogram"]:
        notes = notes + [note(NOTE_HISTOGRAM_WITHHELD)]
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
    n_blank: int,
    n_withheld: int,
) -> (
    "tuple[dict[str, object], dict[str, int], list[dict[str, object]], "
    "int, int]"
):
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

    AND THE TWO COUNTS BESIDE THE MAP GO WITH IT (contract 5 C5-N6,
    C5-21). `n_missing_blank` and `n_missing_withheld` are the source
    accounting version 4 kept inside the map, so they follow the map's
    own rule: they are zero on exactly the columns whose class empties
    it. Leaving them behind would have said, of a free-text column that
    publishes no spelling, how many of its absent cells were blank and
    how many wore something the floor pooled -- which is the shape of
    the defect this function exists for, one field remembering the rule
    and the field added next to it forgetting.

    Guarantees: accepts whether the column may publish a value, the
    details block built for it, the missing-spelling map under the
    small-cell floor, the sentinel verdicts that cleared the floor, and
    the blank and pooled counts; returns the five of them unchanged for
    a column whose class permits values, and filtered for a column whose
    class does not. Raises nothing. No I/O of any kind.
    """
    if not publishes_nothing:
        return details, by_source, entries, n_blank, n_withheld
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
    return _counts_only(details), no_spellings, withheld, 0, 0


def profile_column(
    name: str,
    position: int,
    values: list[str],
    n_rows: int,
    settings: Settings,
    forced_identifier: bool = False,
    forced_code: bool = False,
    forced_measurement: bool = False,
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
    present, missing = split_missing(values, settings)
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
            removed = [exact_of_number(candidate) for candidate in withheld]
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
    # THE SAME JUDGEMENT, OVER THE PLACEHOLDER DAYS (plan amendment
    # A-P4-1 item 3). A column whose open-ended rows are filled with
    # `9999-12-31` publishes that day as its exact last value, drags
    # its whole ladder toward it, and seeds the twin with decades the
    # source never held -- the one audited shape where the ratified
    # plan published wrong numbers with no warning at all. It is the
    # calendar's `-999`, one space over.
    #
    # ITS ORDERING IS TIGHTER THAN THE AFFIX PASS'S, and the decision
    # says why: taking cells out changes every count, so a column no
    # rule has trouble with today might be claimed by a different one
    # afterwards. There are two conditions, and both must hold.
    #
    # The first is that rules 0 through 4 declined the UN-REMOVED
    # column, which is what the trial below asks. So a constant column
    # of one placeholder day keeps today's claim, and a two-valued
    # column whose one value is a placeholder stays binary.
    #
    # The second is that the NON-CANDIDATE REMAINDER itself clears the
    # datetime rule's line. Otherwise no cell is judged, no cell is
    # removed, and the column lands exactly where today's rules put
    # it -- so an existing datetime column can never fall out of the
    # role by this pass, and a column that was never a column of dates
    # cannot be turned into one by taking cells out of it.
    day_verdicts: dict[str, tuple[bool, str, int]] = {}
    removed_by_days = 0
    judged_over_days = False
    if present and not forced_identifier:
        trial = _decide(
            cells,
            forced_identifier,
            forced_code=forced_code,
            forced_measurement=forced_measurement,
        )
        if trial.role == ROLE_TEXT or trial.role == ROLE_DATETIME:
            reading = _remainder_reading(present, settings)
            if reading is not None:
                day_verdicts = _placeholder_verdicts(
                    present, reading, settings
                )
                withheld_days = sorted(
                    candidate
                    for candidate in day_verdicts
                    if day_verdicts[candidate][0]
                )
                if withheld_days:
                    kept_cells: list[_Cell] = []
                    for cell in classified:
                        found = parsing.placeholder_day_of(
                            cell.text, reading
                        )
                        if found is not None and found in withheld_days:
                            missing += [
                                (cell.text, parsing.MISSING_DATE_SENTINEL)
                            ]
                            removed_by_days = removed_by_days + 1
                        else:
                            kept_cells += [cell]
                    classified = kept_cells
                    cells = _tally(classified, n_rows, settings)
                    present = cells.present
                    judged_over_days = True

    # THE SAME JUDGEMENT, OVER THE CORES. A column of `-999 mg` beside
    # real amounts is the shape a trial file actually has, and the pass
    # above never sees it: the CELLS are not numeric-looking, so the
    # question is never asked, and `-999` is published as the column's
    # smallest dose with nothing complaining. That is the silent
    # statistical wrongness this project treats as its worst failure,
    # and the contract says plainly that stand-ins are judged over the
    # CORES once the earlier rules decline (C6-5).
    #
    # It runs only where an affixed reading is what the column reaches,
    # which is why the role is decided first and then decided again:
    # removing cells changes every count, so nothing may be built from
    # the first answer.
    removed_by_cores = 0
    judged_over_cores = False
    if present and not forced_identifier:
        trial = _decide(
            cells,
            forced_identifier,
            forced_code=forced_code,
            forced_measurement=forced_measurement,
        )
        if trial.role == ROLE_AFFIXED:
            before = len(present)
            classified, missing, verdicts = _cores_judged(
                cells, classified, missing, verdicts
            )
            cells = _tally(classified, n_rows, settings)
            present = cells.present
            # HOW MANY THE CORE PASS TOOK, carried to the verdict below.
            # Removal can move a column across the detection line -- a
            # pair whose count is eaten below the floor lands on a later
            # rule -- and the remark of the role it lands on has to say
            # so, or the reader is told a count of a column that no
            # longer exists (contract C6-5).
            removed_by_cores = before - len(present)
            judged_over_cores = True
    entries, unpublished = _published_verdicts(verdicts, settings)
    # THE DAY VERDICTS FOLLOW THE NUMBER VERDICTS, and the order is the
    # contract's own (invariant V4): every numeric candidate, ascending
    # by number, then every placeholder day, ascending as text. Two
    # kinds of candidate in one list need an order somebody can check,
    # and sorting the two together as text would put `1900-01-01`
    # between `-999` and `9999`.
    day_entries, day_unpublished = _published_day_verdicts(
        day_verdicts, settings
    )
    entries = entries + day_entries
    unpublished = unpublished + day_unpublished

    n_present = len(present)
    n_missing = n_rows - n_present
    remarks: list[Note] = []
    if cells.n_out_of_range:
        remarks = remarks + [
            note(REMARK_OUT_OF_RANGE, (cells.n_out_of_range,))
        ]
    if cells.n_contradictory:
        remarks = remarks + [
            note(REMARK_CONTRADICTORY, (cells.n_contradictory,))
        ]
    if unpublished:
        remarks = remarks + [note(REMARK_RARE_SENTINELS, (unpublished,))]

    if not present:
        verdict = _Verdict(
            role=ROLE_EMPTY,
            evidence=note(EVIDENCE_EMPTY),
            details={},
            notes=[],
            remarks=[],
        )
    else:
        # AFTER EITHER JUDGED PASS, rules 0 through 4 are not asked
        # again (review item P4-HOLE-F1). They already declined the
        # un-removed column, and asking them of the remainder is how a
        # column changes role because cells LEFT it: two hundred and
        # twenty-eight dates over two days beside twelve placeholder
        # cells is a column of dates, and re-asking made it a
        # two-valued column of labels once the placeholders were gone.
        # The plan's gate promises no such move, and this is what makes
        # the promise true rather than argued.
        verdict = _decide(
            cells,
            forced_identifier,
            removed_by_cores,
            after_removal=judged_over_cores,
            after_days=judged_over_days,
            forced_code=forced_code,
            forced_measurement=forced_measurement,
        )

    by_source, by_class, n_blank, n_withheld = _missing_maps(
        missing, settings
    )
    # ONE application of the publication class, over everything the
    # block can publish, after the role is known and before anything is
    # built. Doing it per field is what let one field be forgotten
    # (review item P1-R7-F2).
    (
        details,
        by_source,
        entries,
        n_blank,
        n_withheld,
    ) = _publication_class_applied(
        publishes_no_values(verdict.role, forced_identifier),
        verdict.details,
        by_source,
        entries,
        n_blank,
        n_withheld,
    )
    # ONE construction site. Every count below is a field of the class,
    # so it exists on every role by construction rather than by
    # somebody remembering to add it in ten places.
    statistical_type, quality_state, structural_role = axes_of(
        verdict.role, forced_identifier
    )
    return ColumnProfile(
        name=name,
        position=position,
        role=verdict.role,
        statistical_type=statistical_type,
        quality_state=quality_state,
        structural_role=structural_role,
        detection_evidence=verdict.evidence,
        n_present=n_present,
        n_missing=n_missing,
        missing_by_source=by_source,
        missing_by_class=by_class,
        n_missing_blank=n_blank,
        n_missing_withheld=n_withheld,
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

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

# THE NINETY PERCENTS THE LADDER ABOVE DOES NOT NAME (plan P4-D4.10,
# the owner's second numeric ask of 2026-08-26: "every p value 1 to
# 100"). Together with `LADDER` these are the whole hundred and one
# rungs: nought and a hundred are the two ends, `LADDER` names nine
# more between them, and this names the rest.
#
# THEY ARE ONE FACT AND NOT NINETY. Every rung `percentiles` names is
# an obligation with its own subcheck, and every executable subcheck
# owes a registered red case that makes THAT subcheck report missed;
# the entry table carries ninety-nine such cases for eleven rungs, and
# a hundred and one rungs would need about nine hundred. So the finer
# ladder is published under one key, disposed once, and its fidelity
# comes from the GENERATOR INTERPOLATING IT rather than from checking
# it rung by rung.
FINER_LADDER = tuple(
    (f"p{percent:02d}", percent, 100)
    for percent in range(1, 100)
    if percent not in (1, 5, 10, 25, 50, 75, 90, 95, 99)
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
# THE FIFTEENTH ROLE (residual R-P4-13, landing L8): numbers and
# labels sharing one cell space, each half described in its own
# terms and every present cell in exactly one of them.
ROLE_COMPOUND = "numbers_with_labels"
# THE FOURTEENTH ROLE (plan P4-D21). Two or more numbers written
# in one cell, joined by one repeated separator: `120/80`, `12-05-3`.
# Its full reading is reached ONLY where the person names the column --
# see `_joined_reading` for the measurement that says why -- and one
# shape, two plain whole numbers joined by a slash, is read from the
# values by rule 9c (plan P4-D40).
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
    ROLE_COMPOUND,
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
    ROLE_COMPOUND,
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
    # AND SO DOES A COLUMN OF NUMBERS BESIDE LABELS (residual R-P4-13,
    # landing L8). The table is a bijection, now FIFTEEN roles onto
    # fifteen types, and this role's shape is neither `continuous` nor
    # `long_tail_labels` though it holds a population of each: a
    # consumer routing on the type axis must not be told this column is
    # a quantity, because a quarter of its cells are not, nor that it
    # is a set of labels, because most of them are numbers. It names
    # itself for the same reason the two above do.
    ROLE_COMPOUND: (ROLE_COMPOUND, QUALITY_OK),
    ROLE_TEXT: (TYPE_TEXT, QUALITY_OK),
}

# The label a suppressed value is replaced by, and the key under which
# blank cells are counted.
SUPPRESSED_LABEL = "(withheld)"
BLANK_SPELLING = parsing.MISSING_BLANK

# THE STATE A CENSUS PUBLISHES WHERE IT CANNOT SPEAK WITHOUT NAMING
# SOMEBODY (the Codex review of landing 2b.2; owner twin definition,
# clause 3).
#
# `(withheld)` is not enough, and the difference is the whole of this
# key. That label says "these cells, and fewer of them than the floor" --
# a sentence that still NAMES the category wherever the census has only
# one category to name. Measured on the review's own column: 1,200
# measurements at a floor of eleven, all written `1000.5` upward,
# against the same column with one cell rewritten `+1600.5`. The two
# descriptions differed in exactly one place, `decimal_plus` moving from
# `{}` to `{"(withheld)": 1}`, and both loaded. Since `+` is that
# census's only possible key, a reader holding the other 1,199
# spellings can read off the remaining individual's.
#
# This key says nothing at all: not the count, and not whether the count
# is nought. That is what makes nought and a below-floor count the SAME
# published state, which is the property the rule asks for and the
# property `(withheld)` cannot have. Its count is always nought, because
# a number beside it would be the disclosure over again.
UNAVAILABLE_LABEL = "(unavailable)"

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
    # THE LAYOUT CENSUS IS ADMITTED ON THE SAME CHECKED PROPERTY THE
    # FORM CENSUS IS, and not on a judgement (landing 2b.18, plan
    # P4-D120). A layout is TEXT, which is what this list exists to
    # keep out, so it is admitted only because every figure and every
    # letter of a cell is replaced before the key is built -- by one of
    # six placeholders, `%` `!` `@` `&` `~` `^`, none of which a cell
    # that HAS a layout may contain -- and because
    # `profile._is_layout_form` refuses any key holding anything but
    # those six and fifteen named marks, whatever built it. What is
    # published is what KIND of character stood at each position and
    # where the marks between them fell; what is not published is which
    # character it was.
    #
    # WITHOUT THIS ENTRY the census is silently replaced by
    # `(withheld)` before the publication guard ever sees it, which is
    # what this list does to every key it does not name. That is the
    # right default and it is why the entry is written here with its
    # reason rather than added quietly.
    "layout_forms",
    # THE ONE ENTRY HERE THAT DOES CARRY TEXT OF THE TABLE, AND IT IS
    # HERE BY THE OWNER'S RULING OF 2026-09-17, item 1 (contract 7.12a).
    # A literal prefix every present cell of a declared record number
    # opens with -- `REC`, `P`, `ABC-` -- is a fragment of every value
    # in its column and of nobody's value in particular; the owner ruled
    # it published where the column clears the smallest group size, and
    # amended invariants I3 and F3 for this case only. It is admitted on
    # a checked property as the two censuses are: `profile` refuses any
    # prefix `parsing.is_a_literal_prefix` refuses and any key that is
    # neither `(column)` nor a layout, whatever built it.
    "layout_prefixes",
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
FINER_LADDER_NAMES = tuple([name for name, _num, _den in FINER_LADDER])
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

# What the PRODUCER says when a declared value's number depends on
# which grammar reads it, beside a `--decimal-comma` column. The
# command says it in its own words, because it can name the option the
# person typed; this is what any other caller of `build_document` gets.
#
# IT IS REFUSED AT THE PRODUCER AND NOT ONLY AT THE COMMAND LINE
# (review item P4-G3-R8-F2). `build_document` is a public entry point
# and accepted the pair, so the same wrong presence, role and numeric
# verdicts were one call away for anybody not going through the CLI.
AMBIGUOUS_DECLARED_VALUE = (
    "a declared value whose number depends on whether a column's "
    "numbers are written with a comma cannot be used together with a "
    "decimal-comma column"
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
EVIDENCE_COMPOUND = "evidence_numbers_with_labels"
# THE OTHER BRANCH OF THE SAME RULE, and it needs its own sentence
# because the one above states a fact that is not true of it (review
# round 1 of landing L8, item 5). Rule 7b admits a label half two ways:
# a value shared by the detection line's rows or more, OR a SMALL SET
# of different values however few rows each covers. A column of 295
# readings beside five `NOT DETECTED` is admitted by the second, and
# the first sentence told its reader that some value is shared by
# eleven rows or more. No value is. One rule, two grounds, two
# sentences.
EVIDENCE_COMPOUND_SMALL_SET = "evidence_numbers_with_a_few_labels"
EVIDENCE_NO_READING_FITS = "evidence_no_reading_fits"
EVIDENCE_DECLARED_IDENTIFIER = "evidence_declared_identifier"

# Four fragments that appear inside a longer sentence rather than on
# their own. They are forms like any other, and they travel as
# arguments of the sentences that carry them, so the whole sentence is
# still rebuilt from enumerated parts.
SAID_WRITTEN_AS_NUMBERS = "said_written_as_numbers"
SAID_READ_AS_DATES = "said_read_as_dates"
# THE THIRD FRAGMENT, and it is a privacy control rather than a phrase
# (stage 3 landing 3.5, plan P4-D334). It stands where a sentence would
# otherwise print a count NO KEY OF THE BLOCK PUBLISHES -- how far a
# reading the column was not described by got, how many cells wore a
# mark -- and the floor will not let it name. Its one argument is the
# census LINE, which is a setting of the run and not a count of
# anybody's rows, so the sentence says the SHAPE of the number and
# never the number.
SAID_FEWER_THAN_THE_LINE = "said_fewer_than_the_line"
# THE FOURTH FRAGMENT, and it is the other half of the same privacy
# control (stage 3 landing 3.5 repair pass, plan P4-D334.1). NF59 says
# "one or more, and below the line". This one says the opposite shape:
# the count REACHES the line, and what it leaves over against the
# population its binding names does NOT -- so the digits would publish
# that group by subtraction, and "fewer than 11" would be false of a
# count of 1,199. A remark standing there is withdrawn; the one
# sentence a block may not lose says this instead. It names no number
# at all, so there is nothing to subtract from anything, and its arity
# is nought for that reason: an argument here would be a count, and a
# count is what it exists not to say.
SAID_SOME_BUT_NOT_ALL = "said_some_but_not_all"

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
# THE COLUMN TWO RULES BOTH READ, and the question the tool puts to the
# person rather than guessing (amendment A-P4-58, owner ruling
# 2026-09-09; residual R-P4-157). It carries the count of cells whose
# spelling wears the shared text, so a reader can see how much of their
# column the answer decides.
REMARK_TWO_READINGS_FIT = "remark_two_readings_both_fit"
# THE SAME QUESTION, ON THE COLUMN NO RULE CLAIMED AT ALL (amendment
# A-P4-58; residual R-P4-157, landing L16). Where a letter is written
# FLUSH against the digits -- `13.5H` beside `1234F` -- the affix rule
# refuses the column undeclared, on purpose, because a rear letter is
# an abnormal flag on one table and a category of procedure code on
# the next. That refusal was SILENT: the column fell to free text and
# the competing-readings remark told the person to rewrite their data,
# naming neither declaration that already reads it. A chance of a
# wrong guess is the trigger, so the column is asked about rather than
# left in silence. It routes nothing.
REMARK_A_LETTER_NEEDS_A_DECLARATION = "remark_a_letter_against_the_digits"
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
# THE AFFIXED ROLE'S DECLINE, SAID OUT LOUD (plan P4-D30, residual
# R-P4-39, contract NF50). `_wrapped_in_an_address` refuses to read
# `user12345@example.org` as a number wearing affixes, and the refusal
# was SILENT: a column that had been publishing a mean, a spread and a
# ladder stopped doing so and no sentence anywhere said why or what the
# owner could do about it. Principle 5 says a column is either handled
# or declined with a plain-language explanation, and this decline had
# none.
REMARK_ADDRESS_NOT_A_QUANTITY = "remark_an_address_is_not_a_quantity"
# BRACKETS AROUND A NUMBER AND ITS TEXT TOGETHER, NAMED AND NOT READ
# (landing 2b.2, contract NF56). Accounting writes a negative amount
# `($1,234.56)`, and a note in brackets reads `(5 mg)`: the brackets
# stand outside the affix in both, and the values cannot say which. Such
# a wrapper is kept as written, so the twin writes the same spelling;
# what the remark says is that the numbers published for it are the ones
# inside the brackets, without a sign.
REMARK_BRACKETS_AROUND_THE_AFFIX = "remark_brackets_around_the_affix"
# A MINUS AFTER WHOLE FIGURES, NAMED AND NOT READ (the verification of
# landing 2b.2, contract NF57). A ledger of whole amounts writes `500-`
# for a debit, and a grade or a code writes `3-`: one cell cannot say
# which, so the minus is kept as the text after the number, in every
# cell alike whatever its size, and the remark says what the numbers
# published for that wrapper are. The same minus after figures with a
# point, `1,483.65-`, is read as a sign (`negative_form`).
REMARK_MINUS_AFTER_THE_FIGURES = "remark_a_minus_after_the_figures"
# A LABEL COLUMN PUBLISHING ONE OF THIS PACKAGE'S OWN STAND-IN NUMBERS
# AS A LEVEL (plan P4-D4.7, amendment A-P4-30 item 1, contract NF37).
# The stand-in judgement runs only above the numeric parse line, so a
# column of labels publishes `-999` as an ordinary level with an
# ordinary count and nothing anywhere said that the same number on a
# numeric column would have been read as a gap. Advisory: it routes
# nothing, and `--missing-value` is the person's own to make.
REMARK_LABEL_IS_A_STAND_IN = "remark_a_label_is_a_built_in_stand_in"
# A COLUMN OF WHOLE NUMBERS WHOSE EVERY VALUE LIES IN THE BAND A
# MOMENT IN TIME IS COUNTED INTO (residual R-P4-9, contract NF51).
# Such a column is read as a count and stays one -- no rule of this
# package reads a number as a time and no declaration makes one -- so
# the remark exists for the one thing that WAS missing: being told.
REMARK_EPOCH_BAND = "remark_whole_numbers_could_be_times"

# THE TWO BANDS, and there is no third. A moment in time is counted
# into a whole number in one of two units a person meets: seconds from
# the 1st of January 1970, or milliseconds from the same instant. The
# argument NAMES the band by its place in that pair, so the remark's
# rendering is a lookup rather than a spelling.
EPOCH_BAND_SECONDS = 1
EPOCH_BAND_MILLISECONDS = 2

# HOW WIDE EACH BAND IS, STATED AS TWO CALENDAR YEARS AND NOT AS TWO
# LARGE NUMBERS. The band runs from the first day of `EPOCH_BAND_FROM`
# up to, and not including, the first day of `EPOCH_BAND_UNTIL`; the
# whole numbers themselves are worked out from those days by
# `parsing.days_from_civil`, so nothing here is a constant somebody
# would have to check against a calendar.
#
# WHY THE BAND HAS A LOWER END AT ALL, and why it is this one. Zero is
# the 1st of January 1970, so a band that started there would cover
# every ordinary count a table holds -- ages, tallies, row counts -- and
# the remark would fire on almost every column of whole numbers, which
# is the noise a routing-nothing sentence can least afford. Starting
# at the year 2000 puts the band's floor at 946,684,800 in seconds:
# a count column reaching that is already unusual, and one whose
# EVERY value does is the shape this remark exists for.
EPOCH_BAND_FROM = 2000
EPOCH_BAND_UNTIL = 2051

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
# WHERE THE FIRST ROW CANNOT BE TOLD FROM A RECORD (the owner's ruling
# of 2026-09-17, item 8; plan P4-D232). The names are synthtwin's own,
# the row is kept as the record it may be, and the question is put in
# the questions file. No text of that row reaches this sentence, or any
# other: it is the row this verdict is about, so quoting it here would
# publish the very thing the verdict withholds.
HEADER_NAMES_NOT_TOLD = "header_names_could_not_be_told"

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
    EVIDENCE_COMPOUND: 4,
    EVIDENCE_COMPOUND_SMALL_SET: 4,
    EVIDENCE_NO_READING_FITS: 5,
    EVIDENCE_DECLARED_IDENTIFIER: 0,
    SAID_WRITTEN_AS_NUMBERS: 2,
    SAID_READ_AS_DATES: 2,
    # THE LINE, and nothing else (contract NF59). One argument, and it
    # is the census floor the run was given rather than any count of
    # the column, which is what makes this fragment sayable at all.
    SAID_FEWER_THAN_THE_LINE: 1,
    # NO ARGUMENT AT ALL (contract NF60). It stands where even the line
    # may not be said, because the count that would stand there reaches
    # the line and the reader would take the withheld remainder off the
    # population beside it. Nought arguments is the whole of the
    # control: a form with no argument can carry no count.
    SAID_SOME_BUT_NOT_ALL: 0,
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
    # BOTH COUNTS, BECAUSE THE READING WAS A CHOICE (contract NF25,
    # plan P4-D4.7, amendment A-P4-30 item 1). Argument 1 is what the
    # chosen date format parsed and argument 2 is the numeric-looking
    # count; the compact family is where the two readings compete most
    # often, and a sentence saying only which one won leaves its
    # reader no way to see how close the other came.
    REMARK_DATES_ALSO_NUMBERS: 2,
    REMARK_MONTH_FIRST: 0,
    REMARK_TWO_DIGIT_YEAR: 0,
    # Contract NF36 fixes the order: D, M, X, Y, then the reading used.
    REMARK_SLASHED_EVIDENCE: 5,
    REMARK_CASE_ONLY_MANY: 0,
    REMARK_NEAR_CATEGORY_LINE: 2,
    REMARK_TWO_READINGS_FIT: 1,
    # The count of cells wearing a wrapper that holds a letter, on a
    # column the affix rule refused undeclared. It is the same argument
    # NF54 carries and is counted the same way, so the two sentences a
    # person may meet about one hazard state one number.
    REMARK_A_LETTER_NEEDS_A_DECLARATION: 1,
    # NINE SINCE THE ADVISORY REMARKS LANDED (contract NF29). Seven
    # shipped: the two readings, the parse line, the different values,
    # the ceiling, the affix reading's reach and what stand-in judging
    # removed. Argument 8 is how far a CLOCK reading got -- the one
    # reading a declined column stayed silent about -- and argument 9
    # is the recoverable-distribution advice of amendment A-P4-1 item
    # 4. Each is 0 where its clause is not written.
    REMARK_NO_READING_FITS: 9,
    REMARK_SOME_NOT_NUMBERS: 1,
    REMARK_NEAR_NUMERIC_LINE: 3,
    REMARK_ALL_DIFFERENT_NUMBERS: 0,
    REMARK_PADDED_NUMBERS: 1,
    REMARK_GROUP_COMMAS: 2,
    REMARK_SPREAD_OUT_OF_RANGE: 0,
    REMARK_ALL_DIFFERENT_TEXT: 0,
    # IT CARRIES NO ARGUMENT ON PURPOSE. A count of the cells that wore
    # the address would be a count of a reading this column does NOT
    # publish -- the block that would have held `n_affixed` is the one
    # the decline refused to write -- and the affix pair itself is the
    # fourth argument class, admitted only where the same block
    # publishes the spelling. Neither is available here, so the
    # sentence says the shape in its own fixed words and names no
    # number of this column at all.
    REMARK_ADDRESS_NOT_A_QUANTITY: 0,
    # NO ARGUMENT, for the address remark's reason: the wrapper is
    # published in the block beside the remark and the reader finds it
    # there.
    REMARK_BRACKETS_AROUND_THE_AFFIX: 0,
    REMARK_MINUS_AFTER_THE_FIGURES: 0,
    # WHICH stand-in number, as its one-based place in this package's
    # own three-member list -- so 1, 2 or 3 and nothing else (contract
    # NF37). The NUMBER is written from that place through a fixed
    # table, so no spelling of the column reaches the sentence: the
    # level itself is published in the block beside the remark and the
    # reader finds it there.
    REMARK_LABEL_IS_A_STAND_IN: 1,
    # WHICH BAND, then the two ends read as calendar dates: the year,
    # the month and the day of the smallest value, then of the largest
    # (contract NF51). Seven whole numbers and no spelling of any kind
    # -- the two ends are the `min` and `max` this block already
    # publishes, said a second way.
    REMARK_EPOCH_BAND: 7,
    HEADER_NAMES_BY_OPTION: 0,
    HEADER_DATA_BY_OPTION: 0,
    HEADER_NAMES_BY_CONVENTION: 0,
    HEADER_NAMES_SHOWN_BY_COLUMN: 1,
    HEADER_NAMES_NOT_TOLD: 0,
}

# The same names as a sorted tuple, for a reader and for the tests that
# walk the whole vocabulary.
NOTE_FORMS = tuple(sorted(NOTE_ARITY))

# WHAT EVERY ARGUMENT OF EVERY SENTENCE IS BOUND TO (contract C6-143,
# stage 3 landing 3.5, plan P4-D333). `NOTE_ARITY` above says HOW MANY
# arguments a form takes; this table says what each one of them IS, and
# it is closed over every form and every position for the same reason
# that one is: a position nobody bound is a number a sentence may print
# that no rule governs.
#
# WHY IT EXISTS AT ALL. A count in a sentence and a count in a key are
# the same disclosure, and only the key was ever held to the floor.
# Measured over 56 descriptions at a floor of eleven (the design's own
# `guard_measure.txt`): 252 sentences and 145 of them carrying whole
# numbers, of which NINE printed a count no key of the block beside
# them published at all -- the floored positions this table names --
# and 38 more restated a count the key itself published below the line,
# which is P4-D332's territory and not this table's. THE SECOND NUMBER
# READ 29 UNTIL THE REPAIR PASS, which is what the same run records
# only after a rule-M prototype nobody built; 38 is what the run
# records for the shipped tool.
# `tests/test_p4d334_sentence_arguments.py::test_the_keys_a_sentence_restates_below_the_line_are_held_at_a_ceiling`
# re-measures the same class over the committed battery, so the number
# is one a reader can run rather than one they must take on trust. The
# rule
# this table makes checkable is one sentence long -- A SENTENCE MAY NOT
# CARRY A COUNT A KEY WITHHOLDS -- and it is P4-D221's padded-remark
# rule ("a count the map does not name is a count no sentence prints")
# made general instead of written once per remark.
#
# The eleven kinds, and what each one means for the guard
# (`profile._arguments_are_bound`):
#
# * `key` -- the argument must EQUAL the named key of the column block
#   the sentence belongs to, so the key's own floor rule governs the
#   sentence too and nothing more has to be asked here. The name is
#   dotted where the key lives in a sub-block (`labels.n_distinct_folded`).
# * `sum` and `difference` -- the argument must equal the sum, or the
#   difference, of published keys of that block. Same reasoning: every
#   part is already floored.
# * `document` -- a key of the description itself rather than of a
#   column, which is `n_rows` and nothing else today.
# * `main_wrapper` -- `n_affixed` less every named wrapper's count: the
#   cells wearing the wrapper the block publishes as its main one. The
#   first draft of this table bound it to `n_affixed` and the guard
#   caught the difference on a two-wrapper column, 380 against 400.
# * `setting` -- a threshold of the run: the smallest group size, a
#   ceiling, a detection line. It names no row of anybody's table.
# * `levels_at_the_line` -- how many levels reached the long-tail line,
#   which is the length of a list the block publishes.
# * `vocabulary` -- a place in one of this package's own closed lists
#   (which stand-in number, which time band), never a count.
# * `structural` -- a column number.
# * `value` -- a VALUE of the column restated in other words, which is
#   the date the epoch-band remark reads the ends as. Governed by the
#   stage-3 tail rule and never by a count rule; the tail landing moves
#   these to the tail's own boundaries.
# * `floored` -- THE THIRTEEN POSITIONS THAT ARE THE PUBLICATION. No
#   key of the block carries these counts, so the floor has to be asked
#   at the sentence: each is nought, or reaches `parsing.census_floor`
#   with no group left over against the POPULATION its binding names,
#   or carries `said_fewer_than_the_line` in the number's place, or --
#   where it reaches the line and the population leaves a group below
#   it -- `said_some_but_not_all`. FOUR OF THE THIRTEEN NAME A
#   POPULATION, and which four is a fact about what their complement
#   IS rather than a choice: at those four the cells the count does not
#   count are a SPELLING or AFFIX census group, which `census_nameable`
#   withholds in the same block, so the subtraction hands back a group
#   no key published. At the other nine the complement is the count of
#   cells a competing reading did not reach, which is the class of
#   number P4-D332 leaves published in a key of its own.
# * `word`, `nested` and `affix` -- the three argument classes that are
#   not whole numbers at all (contract C6-119 classes 2, 3 and 4).
#
BIND_KEY = "key"
BIND_SUM = "sum"
BIND_DIFFERENCE = "difference"
BIND_DOCUMENT = "document"
BIND_MAIN_WRAPPER = "main_wrapper"
BIND_SETTING = "setting"
BIND_LEVELS_AT_THE_LINE = "levels_at_the_line"
BIND_VOCABULARY = "vocabulary"
BIND_STRUCTURAL = "structural"
BIND_VALUE = "value"
BIND_FLOORED = "floored"
BIND_WORD = "word"
BIND_NESTED = "nested"
BIND_AFFIX = "affix"

BINDING_KINDS = (
    BIND_KEY,
    BIND_SUM,
    BIND_DIFFERENCE,
    BIND_DOCUMENT,
    BIND_MAIN_WRAPPER,
    BIND_SETTING,
    BIND_LEVELS_AT_THE_LINE,
    BIND_VOCABULARY,
    BIND_STRUCTURAL,
    BIND_VALUE,
    BIND_FLOORED,
    BIND_WORD,
    BIND_NESTED,
    BIND_AFFIX,
)

# The three counts every "written as numbers" clause adds up, written
# once because four forms restate the same sum and a sum spelled out
# four times is a sum that disagrees with itself.
_NUMERIC_LOOKING = ("n_numeric", "n_out_of_range", "n_contradictory")

# THE POPULATION A FLOORED COUNT IS COUNTED AGAINST, written once
# because four positions name it and a population spelled out four
# times is a population that disagrees with itself. It is the block's
# present cells, which every block publishes, so a reader holding the
# sentence and the block can always do the subtraction -- which is
# exactly why the four positions whose remainder no key publishes have
# to name it (contract C6-143, the complement clause).
_AGAINST_THE_PRESENT_CELLS = ("n_present",)

ARGUMENT_BINDINGS: "dict[tuple[str, int], tuple[object, ...]]" = {
    (NOTE_ONE_VALUE_BELOW_FLOOR, 0): (BIND_SETTING, "smallest group size"),
    (NOTE_ONE_OF_TWO_BELOW_FLOOR, 0): (BIND_KEY, "suppressed_levels"),
    (NOTE_ONE_OF_TWO_BELOW_FLOOR, 1): (BIND_SETTING, "smallest group size"),
    (NOTE_LABELS_POOLED, 0): (BIND_KEY, "suppressed_levels"),
    (NOTE_LABELS_POOLED, 1): (BIND_SETTING, "smallest group size"),
    (NOTE_LABELS_POOLED, 2): (BIND_KEY, "suppressed_rows"),
    (EVIDENCE_UNREPRESENTABLE, 0): (BIND_SUM, _NUMERIC_LOOKING),
    (EVIDENCE_UNREPRESENTABLE, 1): (BIND_KEY, "n_present"),
    (EVIDENCE_UNREPRESENTABLE, 2): (BIND_KEY, "n_numeric"),
    (EVIDENCE_ONE_VALUE, 0): (BIND_KEY, "n_present"),
    (EVIDENCE_DATES, 0): (BIND_DIFFERENCE, "n_present", "n_unparsed"),
    (EVIDENCE_DATES, 1): (BIND_KEY, "n_present"),
    (EVIDENCE_DATES, 2): (BIND_WORD,),
    (EVIDENCE_COUNTS, 0): (BIND_SUM, _NUMERIC_LOOKING),
    (EVIDENCE_NUMBERS, 0): (BIND_SUM, _NUMERIC_LOOKING),
    (EVIDENCE_NUMBERS, 1): (BIND_KEY, "n_present"),
    (EVIDENCE_CATEGORIES, 0): (BIND_KEY, "n_distinct_folded"),
    (EVIDENCE_CATEGORIES, 1): (BIND_SETTING, "category ceiling"),
    (EVIDENCE_CATEGORIES, 2): (BIND_DOCUMENT, "n_rows"),
    (EVIDENCE_LONG_TAIL, 0): (BIND_KEY, "n_distinct_folded"),
    (EVIDENCE_LONG_TAIL, 1): (BIND_SETTING, "category ceiling"),
    (EVIDENCE_LONG_TAIL, 2): (BIND_DOCUMENT, "n_rows"),
    (EVIDENCE_LONG_TAIL, 3): (BIND_SETTING, "long-tail line"),
    (EVIDENCE_LONG_TAIL, 4): (BIND_LEVELS_AT_THE_LINE,),
    (EVIDENCE_COMPOUND, 0): (BIND_KEY, "n_numeric_cells"),
    (EVIDENCE_COMPOUND, 1): (BIND_KEY, "n_label_cells"),
    (EVIDENCE_COMPOUND, 2): (BIND_SETTING, "compound line"),
    (EVIDENCE_COMPOUND, 3): (BIND_DOCUMENT, "n_rows"),
    (EVIDENCE_COMPOUND_SMALL_SET, 0): (BIND_KEY, "n_numeric_cells"),
    (EVIDENCE_COMPOUND_SMALL_SET, 1): (BIND_KEY, "n_label_cells"),
    (EVIDENCE_COMPOUND_SMALL_SET, 2): (BIND_KEY, "labels.n_distinct_folded"),
    (EVIDENCE_COMPOUND_SMALL_SET, 3): (BIND_DOCUMENT, "n_rows"),
    (EVIDENCE_NO_READING_FITS, 0): (BIND_NESTED,),
    (EVIDENCE_NO_READING_FITS, 1): (BIND_NESTED,),
    (EVIDENCE_NO_READING_FITS, 2): (BIND_KEY, "n_distinct_folded"),
    (EVIDENCE_NO_READING_FITS, 3): (BIND_SETTING, "category ceiling"),
    (EVIDENCE_NO_READING_FITS, 4): (BIND_DOCUMENT, "n_rows"),
    (SAID_WRITTEN_AS_NUMBERS, 0): (BIND_SUM, _NUMERIC_LOOKING),
    (SAID_WRITTEN_AS_NUMBERS, 1): (BIND_KEY, "n_present"),
    # THE DATE READING'S REACH, AND IT NAMES THE POPULATION (repair of
    # stage 3 landing 3.5). What this count does NOT count is the cells
    # no date format read, and on an unsettled column no key publishes
    # them: 390 ISO dates beside ten free-text cells printed 390 next
    # to a published `n_present` of 400, and ten is what the reader
    # took off it. This is the one floored position that stands inside
    # a sentence a block may not lose, so where the remainder falls
    # below the line the reach is written `said_some_but_not_all`
    # rather than withdrawn.
    (SAID_READ_AS_DATES, 0): (BIND_FLOORED, _AGAINST_THE_PRESENT_CELLS),
    (SAID_READ_AS_DATES, 1): (BIND_WORD,),
    (SAID_FEWER_THAN_THE_LINE, 0): (BIND_SETTING, "census line"),
    (REMARK_OUT_OF_RANGE, 0): (BIND_KEY, "n_out_of_range"),
    (EVIDENCE_CLOCK, 0): (BIND_DIFFERENCE, "n_present", "n_unparsed"),
    (EVIDENCE_CLOCK, 1): (BIND_WORD,),
    (EVIDENCE_CLOCK, 2): (BIND_KEY, "n_unparsed"),
    (EVIDENCE_AFFIXED, 0): (BIND_AFFIX,),
    (EVIDENCE_AFFIXED, 1): (BIND_AFFIX,),
    (EVIDENCE_AFFIXED, 2): (BIND_MAIN_WRAPPER,),
    (EVIDENCE_JOINED, 0): (BIND_KEY, "n_joined"),
    (EVIDENCE_JOINED, 1): (BIND_KEY, "n_parts"),
    (EVIDENCE_JOINED, 2): (BIND_AFFIX,),
    (REMARK_AFFIXED, 0): (BIND_AFFIX,),
    (REMARK_AFFIXED, 1): (BIND_AFFIX,),
    (REMARK_AFFIXED, 2): (BIND_MAIN_WRAPPER,),
    (REMARK_CONTRADICTORY, 0): (BIND_KEY, "n_contradictory"),
    (REMARK_RARE_SENTINELS, 0): (
        BIND_KEY,
        "n_sentinel_candidates_unpublished",
    ),
    (REMARK_UNREPRESENTABLE, 0): (BIND_KEY, "n_numeric"),
    (REMARK_UNREPRESENTABLE, 1): (BIND_SUM, _NUMERIC_LOOKING),
    (REMARK_DATES_ALSO_NUMBERS, 0): (
        BIND_DIFFERENCE,
        "n_present",
        "n_unparsed",
    ),
    (REMARK_DATES_ALSO_NUMBERS, 1): (BIND_SUM, _NUMERIC_LOOKING),
    # THE TWO READINGS' REACHES. They are floored, and they are among
    # the NINE that name no population (plan P4-D333): what a reader
    # takes off the present cells here is the count of cells one
    # reading did not parse, which is the class of number P4-D332
    # leaves published -- and publishes, in this block, as `n_unparsed`
    # beside them. Binding a population here would floor a count the
    # key next to it states outright, which is P4-D332's question and
    # not this table's. What they never carry is the FRAGMENT -- this
    # rendering compares them to choose which of its three sentences to
    # write, so a fragment standing in either would settle the sentence
    # by a number nobody may print, and a reach below the line
    # withdraws the remark instead.
    (REMARK_SLASHED_EVIDENCE, 0): (BIND_FLOORED,),
    (REMARK_SLASHED_EVIDENCE, 1): (BIND_FLOORED,),
    (REMARK_SLASHED_EVIDENCE, 2): (BIND_FLOORED,),
    (REMARK_SLASHED_EVIDENCE, 3): (BIND_FLOORED,),
    (REMARK_SLASHED_EVIDENCE, 4): (BIND_WORD,),
    (REMARK_NEAR_CATEGORY_LINE, 0): (BIND_KEY, "n_distinct_folded"),
    (REMARK_NEAR_CATEGORY_LINE, 1): (BIND_SETTING, "category ceiling"),
    (REMARK_TWO_READINGS_FIT, 0): (BIND_FLOORED,),
    (REMARK_A_LETTER_NEEDS_A_DECLARATION, 0): (BIND_FLOORED,),
    (REMARK_NO_READING_FITS, 0): (BIND_NESTED,),
    (REMARK_NO_READING_FITS, 1): (BIND_NESTED,),
    (REMARK_NO_READING_FITS, 2): (BIND_SETTING, "strict reading line"),
    (REMARK_NO_READING_FITS, 3): (BIND_KEY, "n_distinct_folded"),
    (REMARK_NO_READING_FITS, 4): (BIND_SETTING, "category ceiling"),
    # THE AFFIX READING'S REACH, AND IT NAMES THE POPULATION for the
    # same reason the date reach does: what it does not count is the
    # cells wearing no affix, which on a column described as free text
    # is a spelling group `census_nameable` withholds. Measured on a
    # sixty-row column at the default floor: 59 printed beside a
    # published `n_present` of 60. Arguments 7, 8 and 9 stay unbound --
    # a stand-in removal, a clock reach and a recoverable-distribution
    # count, each of which the block publishes a key for.
    (REMARK_NO_READING_FITS, 5): (BIND_FLOORED, _AGAINST_THE_PRESENT_CELLS),
    (REMARK_NO_READING_FITS, 6): (BIND_FLOORED,),
    (REMARK_NO_READING_FITS, 7): (BIND_FLOORED,),
    (REMARK_NO_READING_FITS, 8): (BIND_FLOORED,),
    (REMARK_SOME_NOT_NUMBERS, 0): (BIND_KEY, "n_not_numeric"),
    (REMARK_NEAR_NUMERIC_LINE, 0): (BIND_SUM, _NUMERIC_LOOKING),
    (REMARK_NEAR_NUMERIC_LINE, 1): (BIND_KEY, "n_present"),
    (REMARK_NEAR_NUMERIC_LINE, 2): (BIND_SETTING, "strict reading line"),
    (REMARK_PADDED_NUMBERS, 0): (BIND_KEY, "numeric_styles.leading_zero"),
    # THE COMMA REMARK'S TWO COUNTS, AND THIS IS THE REPOSITORY'S OWN
    # PRECEDENT. `parsing.census_nameable`'s docstring records the
    # shape that made the rule: 1,200 grouped prices at a floor of
    # eleven, one of them rewritten bare, published {",": 1199} beside
    # a row count of 1,200, and the one ungrouped cell was read off by
    # subtraction. The key census was corrected and the SENTENCE went
    # on printing 1199 beside a published `n_present` of 1,200 -- the
    # same subtraction, in prose. Both counts are cells bearing one
    # spelling of a number, so both complements are spelling-census
    # groups and both name the population.
    (REMARK_GROUP_COMMAS, 0): (BIND_FLOORED, _AGAINST_THE_PRESENT_CELLS),
    (REMARK_GROUP_COMMAS, 1): (BIND_FLOORED, _AGAINST_THE_PRESENT_CELLS),
    (REMARK_LABEL_IS_A_STAND_IN, 0): (BIND_VOCABULARY,),
    (REMARK_EPOCH_BAND, 0): (BIND_VOCABULARY,),
    (REMARK_EPOCH_BAND, 1): (BIND_VALUE,),
    (REMARK_EPOCH_BAND, 2): (BIND_VALUE,),
    (REMARK_EPOCH_BAND, 3): (BIND_VALUE,),
    (REMARK_EPOCH_BAND, 4): (BIND_VALUE,),
    (REMARK_EPOCH_BAND, 5): (BIND_VALUE,),
    (REMARK_EPOCH_BAND, 6): (BIND_VALUE,),
    (HEADER_NAMES_SHOWN_BY_COLUMN, 0): (BIND_STRUCTURAL,),
}

# THE TWO POSITIONS THE CONTRACT STATES AND THIS PRODUCER DOES NOT
# EMIT. `tests/test_p4d27_note_grammar_matches_the_code.py` carries
# both as named arity mismatches: contract 4.5.1 gives each of these
# remarks an argument counting the present cells that share a value
# with another row, and this producer raises them only where every
# value differs, so the argument would be nought at every call site.
# They are bound here all the same, because the contract's binding
# column has to be complete for the guard that compares the two to mean
# anything -- and the binding is the one the clause describes, a
# difference of two published keys.
ARGUMENT_BINDINGS_STATED_NOT_EMITTED: "dict[tuple[str, int], tuple[object, ...]]" = {
    (REMARK_ALL_DIFFERENT_NUMBERS, 0): (
        BIND_DIFFERENCE,
        "n_present",
        "n_distinct",
    ),
    (REMARK_ALL_DIFFERENT_TEXT, 0): (
        BIND_DIFFERENCE,
        "n_present",
        "n_distinct",
    ),
}

# Where a floored position carries the fragment rather than its own
# digits, the producer puts it there. Read by the producer's own pass
# and by the guard, so the two cannot disagree about which positions
# the fragment may stand at.
FLOORED_POSITIONS = tuple(
    sorted(
        place
        for place in ARGUMENT_BINDINGS
        if ARGUMENT_BINDINGS[place][0] == BIND_FLOORED
    )
)


def argument_binding(form: str, place: int) -> "tuple[object, ...]":
    """What one argument position of one form is bound to.

    Guarantees: accepts a form name and a zero-based position; returns
    the binding, or `()` where the table has none -- which is a defect
    the guard reports rather than a state a document may reach.
    Determinism: a lookup in a fixed table. No I/O of any kind.
    """
    if (form, place) in ARGUMENT_BINDINGS:
        return ARGUMENT_BINDINGS[(form, place)]
    return ()


def unbound_argument_positions() -> "list[tuple[str, int]]":
    """Every position of every form that this table does not bind.

    THE CLOSURE CHECK, written beside the table it closes. A form added
    to `NOTE_ARITY` with no binding for one of its arguments is a
    sentence that may print a number no rule governs, and the guard
    cannot invent one; the answer has to be a defect somebody sees.

    Guarantees: returns the missing positions in sorted order, and
    every position of `ARGUMENT_BINDINGS` that no form has. Determinism:
    a fixed function of the two tables. No I/O of any kind.
    """
    missing: "list[tuple[str, int]]" = []
    for form in sorted(NOTE_ARITY):
        for place in range(NOTE_ARITY[form]):
            if (form, place) not in ARGUMENT_BINDINGS:
                missing += [(form, place)]
    for bound in sorted(ARGUMENT_BINDINGS):
        if bound[0] not in NOTE_ARITY or bound[1] >= NOTE_ARITY[bound[0]]:
            missing += [bound]
    return missing

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


def _stand_in_spelling(place_in_list: int) -> str:
    """One built-in stand-in number, from its one-based place.

    Contract NF37's fixed table, DERIVED rather than typed: the list a
    cell is judged against is `parsing.NUMERIC_SENTINELS`, and a table
    written out beside it would be the same fact in two places -- the
    shape this project keeps finding drifted apart. Every member is a
    whole number, so the spelling is the number without a fraction.

    Guarantees: accepts 1, 2 or 3; returns this package's own spelling
    of that member. Raises ValueError for any other position, which is
    an internal check -- `note` refuses an argument no producer built.
    No value of any table can reach it. No I/O of any kind.
    """
    if place_in_list < 1 or place_in_list > len(parsing.NUMERIC_SENTINELS):
        raise ValueError(UNAUTHORIZED_NOTE_ARGUMENT)
    return f"{int(parsing.NUMERIC_SENTINELS[place_in_list - 1])}"


def _epoch_band_word(band: int) -> str:
    """The unit one of the two time bands counts in.

    Contract NF51's fixed table: 1 is seconds and 2 is milliseconds.
    Two bands and no third, so the word is a lookup and never a
    spelling of anybody's column.

    Guarantees: accepts 1 or 2; returns the word. Raises ValueError
    otherwise, which is an internal check. No I/O of any kind.
    """
    if band == EPOCH_BAND_SECONDS:
        return "seconds"
    if band == EPOCH_BAND_MILLISECONDS:
        return "milliseconds"
    raise ValueError(UNAUTHORIZED_NOTE_ARGUMENT)


def _written_day(arguments: "tuple[object, ...]", place: int) -> str:
    """Three whole numbers as one calendar day, `YYYY-MM-DD`.

    The year is written in four figures and the month and day in two,
    each padded with zeros on the left, which is the one spelling this
    package writes a day in anywhere. The three numbers are arguments
    of the form, so nothing is read from a column here.
    """
    return (
        f"{_whole(arguments, place):04d}-"
        f"{_whole(arguments, place + 1):02d}-"
        f"{_whole(arguments, place + 2):02d}"
    )


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

    Four shapes, because one of the two sides is usually empty and a
    sentence that said "written as nothing, a number, then 'mg'" would
    be describing a shape no cell has.

    AND THE FOURTH IS THE BARE WRAPPER, WHICH MAY BE THE COMMONEST ONE
    (plan P4-D36). It was three shapes until this landing, when the
    wrapper worn by no text at all became a member of the vocabulary --
    and on the shape this role was widened FOR it is usually the
    commonest, because most laboratory results carry no abnormal flag.
    A column of two hundred readings, a hundred of them bare, fifty
    ` H` and fifty ` L`, then rendered `written as a number followed by
    ''`, and the loader -- which holds the same shapes and cannot
    import this module -- refused its own producer's document. A
    documented command wrote a file the next command would not take,
    which is the defect amendment A-P3-11 exists to keep closed.
    """
    prefix = _affix(arguments, prefix_place)
    suffix = _affix(arguments, suffix_place)
    if prefix and suffix:
        return f"written as {prefix}, a number, then {suffix}"
    if prefix:
        return f"written as {prefix} followed by a number"
    if suffix:
        return f"written as a number followed by {suffix}"
    return "written as a number, with others wearing text beside it"


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


def _count_said(arguments: "tuple[object, ...]", place: int) -> str:
    """One argument as a count: its own digits, or the line fragment.

    THE THIRTEEN POSITIONS WHERE A SENTENCE CARRIES A COUNT NO KEY OF
    THE BLOCK PUBLISHES (contract C6-143, plan P4-D334). Everywhere
    else a sentence restates a published key and the key's own floor
    rule covers it; at these thirteen the sentence IS the publication,
    so the number stands on its own and the floor has to be asked
    here. Below the line the producer puts `said_fewer_than_the_line`
    in the argument's place, and this accessor renders whichever of
    the two is standing there.

    Guarantees: accepts a form's arguments and a position; returns the
    number's own digits, or the fragment's text. Raises TypeError for
    anything that is neither. Determinism: a fixed function of the
    two. No I/O of any kind.
    """
    if isinstance(arguments[place], tuple):
        return _said(arguments, place)
    return f"{_whole(arguments, place)}"


def _fewer_than_the_line(line: int, opening: bool) -> str:
    """NF59's words, written once, in the one case or the other.

    The fragment stands inside another sentence, and at NF29 argument 6
    it stands immediately after a full stop -- so a rendering with one
    case would give the document one sentence that begins in the middle
    of itself. Both cases are written HERE rather than one of them
    being made from the other by moving a letter, because the second is
    a rule about text and this is a rule about a sentence.
    """
    if opening:
        return f"Fewer than {line}"
    return f"fewer than {line}"


def _some_but_not_all(opening: bool) -> str:
    """NF60's words, written once, in the one case or the other.

    Both cases are written HERE for the reason `_fewer_than_the_line`
    gives: where the fragment opens a sentence, capitalising it is a
    rule about the SENTENCE, and making the second case out of the
    first by moving a letter would make it a rule about text.
    """
    if opening:
        return "Some but not all"
    return "some but not all"


def _count_said_opening(arguments: "tuple[object, ...]", place: int) -> str:
    """`_count_said` where the count OPENS a sentence, so it is capitalised.

    Only the fragments move: a number's digits have no case, which is
    why this reads as branches rather than as a rule about text.
    """
    argument = arguments[place]
    if not isinstance(argument, tuple):
        return f"{_whole(arguments, place)}"
    parts = argument[1]
    if not isinstance(parts, tuple):
        raise TypeError(UNAUTHORIZED_NOTE_ARGUMENT)
    if argument[0] == SAID_SOME_BUT_NOT_ALL:
        return _some_but_not_all(True)
    return _fewer_than_the_line(_whole(parts, 0), True)


def _count_is_named(arguments: "tuple[object, ...]", place: int) -> bool:
    """Whether a `_count_said` position carries something to say.

    The renderings at those positions branch on the count -- a clause
    is written where it is nonzero and left out where it is not -- and
    the fragment stands only where the count was one or more, so it is
    named for the same reason a nonzero number is.
    """
    if isinstance(arguments[place], tuple):
        return True
    return _whole(arguments, place) != 0


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
    if form == EVIDENCE_COMPOUND:
        return (
            f"{_whole(arguments, 0)} of this column's cells are ordinary "
            f"numbers and {_whole(arguments, 1)} are not, out of "
            f"{_whole(arguments, 3)} rows; the numbers are too few a "
            f"share to read the whole column as a quantity, and the "
            f"cells that are not numbers hold at least one value shared "
            f"by {_whole(arguments, 2)} rows or more -- so this column "
            f"is numbers and labels sharing one cell space, and each "
            f"half is described in its own terms"
        )
    if form == EVIDENCE_COMPOUND_SMALL_SET:
        return (
            f"{_whole(arguments, 0)} of this column's cells are ordinary "
            f"numbers and {_whole(arguments, 1)} are not, out of "
            f"{_whole(arguments, 3)} rows; the numbers are too few a "
            f"share to read the whole column as a quantity, and the "
            f"cells that are not numbers hold {_whole(arguments, 2)} "
            f"different value(s) between them, which is a set of "
            f"markers rather than free writing -- so this column is "
            f"numbers and labels sharing one cell space, and each half "
            f"is described in its own terms"
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
    if form == SAID_FEWER_THAN_THE_LINE:
        # THE WHOLE OF THIS FRAGMENT'S WORDS (contract NF59). It says
        # the count is one or more and below the line, which is all a
        # reader may be told about a group the floor will not name, and
        # the line itself is the setting the run was given.
        return _fewer_than_the_line(_whole(arguments, 0), False)
    if form == SAID_SOME_BUT_NOT_ALL:
        # THE WHOLE OF THIS FRAGMENT'S WORDS (contract NF60). It says
        # two things and no more: the group is not empty, and it is not
        # the whole column. Both are already asserted by the clause it
        # stands in -- a sentence that says these cells were read one
        # way and those were not -- so the fragment adds no count to
        # the document at all, which is why it may stand where even
        # NF59 may not.
        return _some_but_not_all(False)
    if form == SAID_READ_AS_DATES:
        if not _count_is_named(arguments, 0):
            return "none of them reads as a date in any form synthtwin knows"
        return (
            f"{_count_said(arguments, 0)} read as dates written as "
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
        # AND IT NAMES `--code` FIRST (residual R-P4-72, landing L19).
        # It named `--identifier` alone, which is the OPPOSITE
        # declaration: a person told "if these are codes, run with
        # --identifier" and doing as they were told published no value
        # of the column at all -- throwing away the distribution of
        # codes that is the whole reason the column was declared. NF43
        # shed this flaw at landing L16 and this sentence kept it,
        # because it is quoted inside a frozen reference vector and
        # moving it moves committed bytes. One answer per page now, and
        # each route says what it does.
        return (
            f"{_whole(arguments, 2)} of this column's values are "
            f"{_affix_shape(arguments, 0, 1)}, and synthtwin described "
            f"those numbers as quantities: their average, their spread "
            f"and their ends are in this profile. If these are codes "
            f"rather than measurements, run the command again with "
            f"--code NAME, where NAME is this column's name, and no "
            f"average will be published over them; each code a "
            f"smallest-group's worth of rows share is kept exactly as "
            f"written, with the number of rows that carried it. If "
            f"instead they are record numbers nothing should publish, "
            f"--identifier NAME leaves them out of the profile "
            f"altogether"
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
        # BOTH COUNTS ARE IN THE SENTENCE BECAUSE THE READING WAS A
        # CHOICE (contract NF25). Eight digits are a date and a number
        # at once, so the compact family is where the two readings
        # compete most often -- and a remark that says only which
        # reading won leaves its reader no way to see how close the
        # other one came. Stating both counts is what lets somebody
        # recognize a column that should have been read the other way.
        return (
            f"the values in this column read both as dates and as "
            f"plain numbers: {_whole(arguments, 0)} of them read as "
            f"dates and {_whole(arguments, 1)} of them are written as "
            f"numbers. They were read as dates"
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
        # THE TWO REACHES STAY WHOLE NUMBERS AND THE TWO CONTRADICTION
        # COUNTS DO NOT (plan P4-D334). Arguments 1 and 2 are compared
        # here to choose which of the three renderings applies, so a
        # fragment standing in either would decide the sentence by a
        # number nobody may print; where the floor will not let one of
        # them be named -- or lets a reader take the other off it --
        # the producer publishes no such remark at all. Arguments 3 and
        # 4 are printed and never compared, so the fragment stands
        # there.
        day = _whole(arguments, 0)
        month = _whole(arguments, 1)
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
        if _count_is_named(arguments, 2) and _count_is_named(arguments, 3):
            # THE COMPOSITION IS EXACT: one space after the first
            # clause's closing stop, and no conjunction or joining word.
            return (
                f"{first} This column contradicts itself: "
                f"{_count_said(arguments, 2)} "
                f"values only a day-first reading accepts, and "
                f"{_count_said(arguments, 3)} only a month-first one."
            )
        return first
    if form == REMARK_TWO_READINGS_FIT:
        # THREE READINGS, NOT TWO, AND BOTH DECLARATIONS (landing L16).
        # The sentence named a measurement and a label set and stopped
        # there, which left out the reading that costs a person most: a
        # CODING SYSTEM some of whose codes end in a letter. Measured on
        # a register of 280 five-digit codes beside fifteen `3074F` and
        # five `3075F`, the cautious reading publishes an average of
        # 54,239 over the bare codes -- true of nothing -- and the
        # sentence that reached the person offered only the declaration
        # that would publish MORE of them.
        return (
            f"{_count_said(arguments, 0)} of this column's values are a "
            f"number with a short word or letter beside it, and "
            f"synthtwin cannot tell from the values alone which of "
            f"three things that means. It may be a MEASUREMENT that "
            f"some cells carry a marker beside -- a laboratory result "
            f"flagged high or low; it may be numbers beside a small set "
            f"of LABELS whose spellings hold a figure, such as a stage; "
            f"or the whole column may be a CODING SYSTEM, some of whose "
            f"codes end in a letter. The three are described very "
            f"differently: as measurements, every one of these numbers "
            f"joins this column's average, spread and ends; as labels, "
            f"only the values wearing no marker are described that way; "
            f"as codes, no average is published at all, and the codes "
            f"themselves are published under the smallest-group size in "
            f"force -- at the default of 11, every code that 11 or more "
            f"rows carried, with the rows that carried it. synthtwin "
            f"has described the "
            f"unmarked values as numbers and the marked ones as labels, "
            f"and has not guessed further. If they are measurements, "
            f"run the command again with --measurement and this "
            f"column's name, and every one of its numbers will be "
            f"described; if they are codes, run it again with --code "
            f"and this column's name, and no average, smallest or "
            f"largest will be published over them"
        )
    if form == REMARK_A_LETTER_NEEDS_A_DECLARATION:
        return (
            f"{_count_said(arguments, 0)} of this column's values are a "
            f"number with a letter written against it, and synthtwin "
            f"does not read such a column as a quantity unless it is "
            f"told to: `13.5H` is a flagged laboratory result and "
            f"`1234F` is a category of procedure code, and the values "
            f"cannot say which. Nothing was assumed, so this column is "
            f"described without a distribution. If these are "
            f"measurements, run the command again with --measurement "
            f"and this column's name; if they are codes, run it again "
            f"with --code and this column's name, and no average, "
            f"smallest or largest will be published over them"
        )
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
            f"{_count_said_opening(arguments, 5)} of its values are numbers wearing "
            f"one shared piece of text, which is the reading that came "
            f"closest{_removed_said(arguments, 6)}"
            f"{_later_clauses(arguments, 7, 8)}"
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
        if _count_is_named(arguments, 1):
            return (
                f"{_count_said(arguments, 1)} of this column's values "
                f"cannot be read with the comma as a thousands "
                f"separator -- a thousands group is exactly three "
                f"figures and these are not -- so THIS COLUMN "
                f"CONTAINS VALUES WRITTEN WITH A DECIMAL COMMA, and "
                f"synthtwin does not read those as numbers at all. "
                f"Of the rest, {_count_said(arguments, 0)} could be read "
                f"either way and were read with the comma as a "
                f"thousands separator, so `1,795` was read as one "
                f"thousand seven hundred and ninety-five; every one "
                f"of those that was meant the way the values above "
                f"are written has been read a thousand times too "
                f"large, and any average, spread or ends this profile "
                f"publishes for this column are wrong with them. "
                f"Run the command again with --decimal-comma and "
                f"this column's name, and every one of them is read "
                f"as a decimal number. Rewriting the column with a "
                f"decimal point works too, and changes your file "
                f"where the declaration does not"
            )
        return (
            f"{_count_said(arguments, 0)} of this column's values are "
            f"written with a comma inside the number that could be "
            f"read either way, and synthtwin read every one of them "
            f"with the comma as a thousands separator -- so `1,795` "
            f"was read as one thousand seven hundred and ninety-five. "
            f"MANY COUNTRIES WRITE THE DECIMAL POINT AS A COMMA, and "
            f"if this table is one of them then `1,795` means 1.795 "
            f"and each of those values has been read as a thousand "
            f"times its real size, and every statistic this profile "
            f"publishes about this column was computed from those "
            f"numbers. Nothing in this column settles which was meant. "
            f"If your file writes decimals with a comma, run the "
            f"command again with --decimal-comma and this column's "
            f"name, and this column is read that way. Rewriting the "
            f"column with a decimal point works too, and changes your "
            f"file where the declaration does not"
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
            f"these are codes, run the command again with --code NAME, "
            f"where NAME is this column's name, and no average will be "
            f"published over them; each code a smallest-group's worth of "
            f"rows share is kept exactly as written, leading zeros and "
            f"all, with the number of rows that carried it. If instead "
            f"they are "
            f"record numbers nothing should publish, --identifier NAME "
            f"leaves them out of the profile altogether"
        )
    if form == REMARK_BRACKETS_AROUND_THE_AFFIX:
        return (
            "some values of this column are written inside brackets "
            "together with the text around the number -- `($12.50)` or "
            "`(5 mg)` -- and synthtwin reads the number inside as it is "
            "written, without a sign, because accounting writes a "
            "negative amount that way and a note in brackets looks the "
            "same. The twin writes those values the same way. If the "
            "brackets mean negative amounts, the average, the spread and "
            "the ends published for those values are of the amounts "
            "without their sign, and the column's count of negative "
            "numbers does not include them"
        )
    if form == REMARK_MINUS_AFTER_THE_FIGURES:
        return (
            "some values of this column are written with a minus after "
            "their figures and no decimal point -- `500-` -- and "
            "synthtwin keeps that minus as text written after the number "
            "rather than reading it as a sign, because a whole amount "
            "owed is written that way and so is a grade or a code. The "
            "twin writes those values the same way. If the minus means a "
            "negative amount, the average, the spread and the ends "
            "published for those values are of the amounts without their "
            "sign, and the column's count of negative numbers does not "
            "include them"
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
    if form == REMARK_ADDRESS_NOT_A_QUANTITY:
        # IT ROUTES NOTHING, and every clause of it is written to say
        # so. The decline is what moved this column; the sentence only
        # tells its owner that the decline happened, what shape caused
        # it, and which three declarations settle a question no rule of
        # this package may settle from the values (P1-R6-F8).
        #
        # THE THREE ROUTES EACH SAY A DIFFERENT THING, and the sentence
        # says which, because a list of three flags with no consequence
        # beside them is a list nobody can choose from. Each one was
        # measured on this exact column before being named here:
        # --identifier gives the `identifier` role and publishes no
        # value; --code gives `long_tail_labels` and publishes each
        # spelling with its count; --measurement restores the
        # `affixed_number` reading with its distribution over the
        # cores.
        return (
            "the values in this column are a number wrapped in an "
            "electronic address -- some text, then the number, then an "
            "at sign, a host and a dot label -- and synthtwin did NOT "
            "read them as a number wearing a shared piece of text. "
            "Reading them that way publishes an average, a spread and "
            "two ends over the numbers inside real addresses, which "
            "are whatever numbers those addresses were given and are "
            "not a quantity of anything. THIS SENTENCE DECIDES "
            "NOTHING, and no rule of synthtwin can decide it either: "
            "it is here so that you can recognize your own column and "
            "say what it holds. Three declarations say it, each a "
            "different thing. Run the command again with --identifier "
            "NAME to say these are record numbers, and no value of "
            "this column is published at all; with --code NAME to say "
            "they are a coding system, and each spelling a "
            "smallest-group's worth of rows share is published with "
            "how many rows carried it; or with --measurement NAME "
            "to say the number inside is a quantity after all, and the "
            "column is described as numbers wearing that address. NAME "
            "is this column's name"
        )
    if form == REMARK_LABEL_IS_A_STAND_IN:
        # THE NUMBER IS WRITTEN FROM THE ARGUMENT, NOT CARRIED IN IT
        # (contract NF37). Argument 1 is a POSITION in this package's
        # own three-member list, so the sentence names one of this
        # package's own numbers and never a spelling taken out of the
        # column. The level itself is published in the block beside
        # this remark, and a reader who wants to see it looks there.
        #
        # It is spelled from `parsing.NUMERIC_SENTINELS` rather than
        # typed, so the sentence and the list a cell is judged against
        # cannot drift apart -- the standing lesson of this project,
        # applied to a table small enough to look safe.
        number = _stand_in_spelling(_whole(arguments, 0))
        return (
            f"one of the values this column publishes is {number}, "
            f"which is one of the three numbers synthtwin treats as a "
            f"stand-in for 'no value' when a column's own numbers make "
            f"it one. This column holds labels rather than numbers, so "
            f"that value is published as a label and counted as a real "
            f"one. If it means 'no value' in your table, run the "
            f"command again with --missing-value {number} and it will "
            f"be counted as a gap instead."
        )
    if form == REMARK_EPOCH_BAND:
        # IT ROUTES NOTHING AND THERE IS NOTHING FOR IT TO ROUTE TO.
        # No rule of this package reads a number as a moment in time
        # and no declaration makes one, so unlike the address decline
        # beside it this sentence names no flag at all. What it does
        # is tell somebody that the column they are holding may be
        # times, which nothing in the document said before.
        #
        # AND IT SAYS PLAINLY THAT THE TWIN IS UNAFFECTED, because
        # that is the question a reader of a fidelity report asks
        # next. The numeric reading keeps every value's place and the
        # distance between any two of them, so converting the twin's
        # column to dates the way the source column would be converted
        # gives dates over the same span. What was missing is the
        # person being told, and this sentence is the whole of it.
        unit = _epoch_band_word(_whole(arguments, 0))
        first = _written_day(arguments, 1)
        last = _written_day(arguments, 4)
        return (
            f"every value in this column is a whole number, and every "
            f"one of them sits in the band a computer writes a moment "
            f"in time into when it counts {unit} from the 1st of "
            f"January 1970. Read that way this column runs from "
            f"{first} to {last}. synthtwin read them as plain numbers "
            f"and describes them as a count of things. THIS SENTENCE "
            f"DECIDES NOTHING and moves nothing: no rule of synthtwin "
            f"reads a number as a moment in time, and no declaration "
            f"makes one. It changes nothing about your twin either -- "
            f"reading the column as plain numbers keeps every value "
            f"where it was and every distance between two of them, so "
            f"turning the twin's column into dates the way you would "
            f"turn your own gives dates over the same span. What was "
            f"missing is being told, so that you can recognize your "
            f"own column and say in its name what it holds"
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
    if form == HEADER_NAMES_NOT_TOLD:
        return (
            "The first row could not be told from a record of the table, so "
            "synthtwin named the columns itself -- column_1, column_2, and "
            "so on -- and kept every row of the file, that first row "
            "included. No text of it appears anywhere in this description. "
            "The questions file beside this one asks which reading is "
            "right: run the command again with --first-row names if that "
            "row holds the column names, or leave it as it is if it is the "
            "first record."
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

    # THE SMALLEST GROUP, read from the one place its default is written
    # (`parsing.DEFAULT_SMALL_CELL_FLOOR`, 11 since plan P4-D316).
    small_cell_floor: int = parsing.DEFAULT_SMALL_CELL_FLOOR
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
    # EVERY SPELLING AN ABSENT CELL OF THE COLUMN HELD, published or not,
    # the empty spelling included. NEVER WRITTEN INTO A DESCRIPTION: it is
    # the producer's own working, handed to the workbook census so that a
    # cell whose spelling the twin cannot reproduce is counted in the
    # class the twin writes it as (plan P4-D174).
    absent_spellings: tuple[str, ...] = ()


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
    """The eleven-point percentile ladder of ``numbers``.

    A COLUMN WITH NO NUMBER AT ALL PUBLISHES A NULL AT EVERY RUNG
    (integration repair). `_quantile` accepts a non-empty list and says
    so, and a joined column every part of which is too large for this
    format to hold -- 300 pairs opening `10 ** 310` -- reached it with an
    empty one and `synthtwin profile` raised `IndexError`. A null rung
    carries no obligation (contract L3), which is the truth about such a
    column.
    """
    ordered = sorted(numbers)
    ladder: dict[str, float | None] = {}
    for label, num, den in LADDER:
        ladder[label] = None if not ordered else published(
            _quantile(ordered, num, den)
        )
    return ladder


def _finer_quantiles(numbers: list[float]) -> dict[str, "float | None"]:
    """The ninety rungs `_quantiles` does not name (plan P4-D4.10).

    Computed by exactly the rule beside it, at the other ninety
    percents, so the hundred and one rungs of the two together are one
    ladder measured one way, and not two of them that might disagree.

    WHY THIS EXISTS, in one measurement. An eleven-rung ladder says
    nothing about how many cells lie INSIDE a gap between two rungs, so
    a twin drawn from it puts too few values where the real column
    crowded them. Reconstructing one dental-code column from its rungs
    alone: from eleven rungs, 79 cells below 1000 against a true 97 --
    the defect residual R-P4-30 opened over -- and from a hundred and
    one rungs, 97 exactly.

    Guarantees: accepts the numbers the statistics used; returns ninety
    published values, each `None` exactly where the eleven-rung ladder
    beside it would be. Determinism: a function of the multiset.
    Raises nothing. No I/O of any kind.
    """
    ordered = sorted(numbers)
    ladder: dict[str, float | None] = {}
    for label, num, den in FINER_LADDER:
        # Null at every rung where the eleven beside it are null, which
        # a column with no representable number is (integration repair).
        ladder[label] = None if not ordered else published(
            _quantile(ordered, num, den)
        )
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




def moments_of(
    numbers: "list[float]",
) -> "tuple[float | None, float | None, float | None, float | None]":
    """The four moments of ``numbers``, exactly (plan P1-D11).

    THE ONE IMPLEMENTATION OF THESE FOUR STATISTICS, published so that
    nothing in this package writes a second (review items P4-G6-R5-F1
    and P4-G6-R5-F2). The generator's twin report used to recount them
    from the finished cells with a compensated sum in binary64, which
    agrees with this on ordinary columns and has no answer at either
    end of the range:

    - four zeroes beside one `5e-324` have a skew of 1.5 and a tail
      weight of 3.25, and every square of a deviation that small
      UNDERFLOWS to nothing, so the recount returned no spread, no
      shape and no tails at all;
    - one value at the bottom of the range beside a hundred and
      nineteen near the top has a finite mean and a finite spread, and
      `value - mean` on the first of them OVERFLOWS, so the recount
      returned the same three nothings.

    In both cases the report then said nothing whatever about three
    facts the description publishes, which is the defect four separate
    review rounds of this landing kept turning up in other places.
    `_moments` forms neither the square nor the difference: it works
    over whole numbers scaled by a shared power of two.

    Guarantees:

    - Inputs: a list of finite numbers, in any order. The result
      depends on the multiset and nothing else.
    - Returns: mean, sample standard deviation, skewness and tail
      weight, each the correctly rounded binary64 value of the exact
      statistic, or None where that statistic is undefined -- an empty
      list, a spread the format cannot hold, fewer values than the
      statistic needs, or a column whose values are all one number.
    - Errors raised: none. No I/O of any kind.
    """
    if not numbers:
        return (None, None, None, None)
    found = _moments(list(numbers))
    spread = found["std"]
    if found["std_unrepresentable"]:
        spread = None
    return (found["mean"], spread, found["skew"], found["kurtosis"])


def average_of(numbers: "list[float]") -> "float | None":
    """The mean of ``numbers``, exactly (plan P1-D11).

    THE COMPANION OF `spread_of`, AND FOR THE SAME REASON (review item
    P4-G6-R2-F2). `math.fsum` is exact until its final rounding and
    still raises `OverflowError` where the RUNNING TOTAL leaves the
    representable range, which sixty values near 1e308 do although
    their mean is an ordinary number. `_moments` never forms that
    total: it works over whole numbers scaled by a shared power of
    two, where there is no range to leave.

    Guarantees:

    - Inputs: a list of finite numbers, in any order. The result
      depends on the multiset and nothing else.
    - Returns: the correctly rounded binary64 mean, or None for an
      empty list. A mean is representable whenever the values are, so
      there is no unrepresentable case to report here.
    - Errors raised: none. No I/O of any kind.
    """
    if not numbers:
        return None
    return _moments(list(numbers))["mean"]


def spread_of(numbers: "list[float]") -> "float | None":
    """The sample standard deviation of ``numbers``, exactly (P1-D11).

    THE ONE IMPLEMENTATION OF THIS STATISTIC, published as a function
    so that nothing has to write a second one (review item
    P4-G6-R1-F5). The validator draws its moment windows around the
    spread of a reconstructed ladder, and it computed that spread with
    `sum((x - mean) ** 2)` in binary64 -- which agrees with this on
    ordinary columns and, on a column of values near 1e300, raises
    `OverflowError` out of `synthtwin validate` instead. The square of
    a large value has nowhere to go; `_moments` never forms one,
    working over whole numbers scaled by a shared power of two.

    Guarantees:

    - Inputs: a list of finite numbers, in any order. The result
      depends on the multiset and nothing else.
    - Returns: the correctly rounded binary64 sample deviation, or
      None where there is no such number -- fewer than two values, or
      an exact spread larger than binary64 can hold.
    - A column whose values are ALL ONE NUMBER returns 0.0 and not
      None, which is the one place this differs from the published
      `std` field. That field is null there because the profile writes
      null for "no shape to report", and the same test serves it for
      the undefined skewness; but the DEVIATION of a column of
      identical values is not undefined, it is zero, and a caller
      drawing a window around it needs the zero. Returning None here
      withheld every moment window on a flat ladder.
    - Errors raised: none. No I/O of any kind.
    """
    if len(numbers) < 2:
        return None
    moments = _moments(list(numbers))
    if moments["std_unrepresentable"]:
        return None
    spread = moments["std"]
    if spread is None:
        return 0.0
    return spread


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
    # THE SPELLING THE NUMBER RULES READ, which is `text` itself on
    # every undeclared column and the swapped spelling on one declared
    # `--decimal-comma` (plan P4-D26). The two are separate fields
    # because they answer different questions and a single field got
    # one of them wrong: `text` is what the FILE holds, and the label
    # roles publish it, so a declaration about numbers must never
    # rewrite a level, a code or a note; this is how the NUMBER is
    # written, and every census of numeric spelling reads it.
    #
    # Reading the censuses off `text` on a declared column made the
    # twin lose the fraction altogether. `1,5` carries no point, so its
    # style counted as `plain`, the whole column published `plain` and
    # `integer_valued: false` together, and the twin wrote `222` for a
    # column running from 2.89 to 300.23 -- the defect P4-D26 exists to
    # prevent, arriving through the census rather than through the
    # reading.
    numeric_text: str
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
    # THE CORE CARRIES EVERY NOTATION AS A LEADING MINUS, the brackets,
    # the minus sign and the trailing minus included (landing 2b.2).
    return parsing.number_core(text)[:1] == "-"


def _classify(text: str, decimal_comma: bool = False) -> _Cell:
    """Classify one present cell, once, into the record every rule reads.

    ``decimal_comma`` says this column was DECLARED as writing its
    numbers with a comma for the point (plan P4-D26). Only the NUMERIC
    reading is taken from the swapped text; `text`, `folded` and the
    two alphabet tests keep the cell exactly as the file wrote it,
    because a declaration about numbers must not rewrite a level, a
    code or a note. Undeclared columns pass `False` and nothing about
    them moves.

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
    # THE TEXT THE NUMBER RULES READ, which is the cell itself on every
    # undeclared column and the swapped spelling on a declared one.
    read = parsing.written_with_a_decimal_comma(text) if decimal_comma else text
    kind = parsing.classify_number(read)
    value: float | None = None
    exact: tuple[int, tuple[str, ...], int] | None = None
    sign = parsing.SIGN_UNKNOWN
    whole = parsing.WHOLE_UNKNOWN
    if kind == parsing.NUMBER:
        value = parsing.parse_number(read)
        exact = parsing.exact_of_accepted_number(read)
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
        if parsing.overflowed(read):
            whole = parsing.WHOLE_YES
        else:
            whole = parsing.WHOLE_NO
        if _written_negative(read):
            sign = parsing.SIGN_NEGATIVE
        else:
            sign = parsing.SIGN_POSITIVE
    trimmed = parsing.trimmed(text)
    return _Cell(
        text=text,
        numeric_text=read,
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
    # WHETHER THIS COLUMN WAS DECLARED `--decimal-comma`, carried on
    # the tally for the same reason `_Cell` carries `numeric_text`: the
    # rules below read this record and never the column, so a rule that
    # has to interpret a DECLARATION as a number -- the kept values of
    # the stand-in judgement, above all -- can only get the reading
    # right if the record hands it over (review item P4-G3-R6-F1).
    #
    # Without it `--decimal-comma amount --keep-value -999,0` read the
    # cells as the sentinel minus nine hundred and ninety-nine and the
    # KEPT declaration under the ordinary grammar, where it is no
    # number at all and matches nothing -- so the outlier pass carried
    # off forty cells the person had explicitly said to keep, and the
    # column's presence, statistics and role moved with them.
    #
    # A TALLY BUILT FROM CORES CARRIES IT TOO, and three of them did
    # not until plan P4-D108. The cores of an affixed column are
    # classified UNDER the declaration and were then counted into a
    # record built without it, so every rule that asks the record
    # which grammar this column writes answered for an undeclared
    # column while reading cells that had been read as declared ones.
    # Measured, 800 cells of `92.959,11 EUR` at floor eleven:
    # `group_separator: ""` and `thousands_marks: {}` about a column
    # where 800 of 800 cells carry a grouping point, a twin writing
    # `62391,86 EUR` with the mark on none of them, and exit 0 on both
    # files. The classification and the record are one decision and
    # are passed together at every site that builds one.
    decimal_comma: bool
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


def _classify_all(
    present: list[str], decimal_comma: bool = False
) -> list[_Cell]:
    """Classify every present cell exactly once, in row order."""
    return [_classify(value, decimal_comma) for value in present]


def _tally(
    classified: list[_Cell],
    n_rows: int,
    settings: Settings,
    decimal_comma: bool = False,
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
        decimal_comma=decimal_comma,
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
# The apostrophe, the right single quotation mark and the minus sign of
# the character tables joined this set with landing 2b.2: a core written
# `1'234.50` or `\u22126.09` is a number the reader holds, and a span
# that stopped at the mark split it in two.
_CORE_CHARACTERS = frozenset("0123456789+-.,()eE'\u2019\u2212")


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


def _reads_as_a_number(text: str, decimal_comma: bool) -> bool:
    """Whether this substring is a number IN THE COLUMN'S OWN GRAMMAR.

    ONE GRAMMAR PER COLUMN, which is the whole of the rule (landing
    2b.16, plan P4-D106; the audit's item NC-11). `_classify` reads a
    declared column's cell by swapping its points and commas and then
    asking the ordinary reader; this asks the same question of a
    SUBSTRING, so that the splitter and the classifier cannot disagree
    about what a number is on the same column.

    The two readings are not tried in turn, and that is deliberate. A
    declared column's grammar says the comma is its decimal point and
    the point is its mark between thousands, so `12,345,678` is not a
    number on such a column, and admitting it because the ORDINARY
    reader accepts it would give one column two graders. What the
    declaration answers is exactly this question, asked of the cells
    the earlier reader could not read at all.

    Guarantees: accepts a substring and whether the column was declared;
    returns whether it reads as a number this format holds.
    Determinism: a fixed function of the two. Raises nothing this
    module's reader does not raise. No I/O of any kind.
    """
    read = parsing.written_with_a_decimal_comma(text) if decimal_comma else text
    return parsing.classify_number(read) == parsing.NUMBER


def affixed_split(
    text: str, decimal_comma: bool = False
) -> "tuple[str, str, str] | None":
    """Split a cell into prefix, core and suffix, or None if it is not one.

    ``decimal_comma`` says this column was DECLARED as writing its
    numbers with a comma where the decimal point goes, and it reaches
    the search for the core (landing 2b.16, plan P4-D106). Without it
    the commonest European export there is -- a price or a percentage
    written `795,64 EUR` or `37,5 %` -- had no substring its reader
    could hold: `795,64` is not a number to the ordinary grader, so
    every cell proposed a pair of its own, no pair reached the line, and
    the column fell to free text with punctuation stand-ins in its
    twin. Measured on the base of this landing, 800 rows at floor
    eleven, seeds 1 and 7: role `free_text`, 0 numeric cells, twin
    cells `)!!!!! !!!!!`, and `synthtwin validate` exit 0 on both the
    twin and the real table, so nothing said a word about it.

    Guarantees:

    - Inputs: one cell's text, exactly as the file held it, and the
      column's own declaration.
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
                if _reads_as_a_number(trimmed[begin:end], decimal_comma):
                    best_start, best_length = begin, end - begin
                    break
    if best_length <= 0:
        return None
    prefix = trimmed[:best_start]
    core = trimmed[best_start : best_start + best_length]
    suffix = trimmed[best_start + best_length :]
    # THE SPACE BETWEEN THE NUMBER AND ITS UNIT BELONGS TO THE UNIT,
    # not to the core, and this was wrong until 2026-09-04. The walk
    # above takes the LONGEST span that reads as a number, and
    # `classify_number` trims its own argument -- so `14.2 g/dL` split
    # into a core of `14.2 ` and a suffix of `g/dL`. The core is then
    # rewritten as a NUMBER by the value stage, which has no space to
    # write, and the twin came back `12.7g/dL` where every real cell
    # read `14.2 g/dL`. A person splitting the twin on a space got one
    # field where their own table gives two.
    #
    # Moving the space into the wrapper is the whole repair: the core
    # still reads as the same number, and the wrapper is the text the
    # twin writes back character for character.
    #
    # WHICH CHARACTERS ARE SPACE IS ASKED OF `parsing.trimmed`, and the
    # first writing of this repair listed two of them instead (review
    # round 1 of this landing, item 7). `_core_character` above admits
    # WHATEVER kind of whitespace that function admits -- which is the
    # only way the splitter and the classifier can agree about where a
    # number begins -- so a repair that knew about the plain space and
    # the tab and nothing else left the others where they were:
    # `14.2<no-break space>g/dL` split into a core of `14.2<no-break
    # space>` and the value stage wrote the space away again, which is
    # the very defect this loop exists to close. One question, one
    # answer, asked of the one function that gives it.
    while core and parsing.trimmed(core[:1]) == "":
        prefix = prefix + core[:1]
        core = core[1:]
    while core and parsing.trimmed(core[-1:]) == "":
        suffix = core[-1:] + suffix
        core = core[:-1]
    if not core:
        return None
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

    Each is a count of characters of the cell's text AS THE NUMBER IS
    SPELLED, so a padded cell counts its zeros and a signed one counts
    its sign. On every column but a declared `--decimal-comma` one that
    is the file's own text, character for character.

    ON A DECLARED COLUMN IT IS THE SPELLING THE DESCRIPTION IS MADE
    FROM, and this clause used to say "as the file spells it" while
    measuring exactly that (review item P4-G3-R2-F2). The two differ:
    `1.234,5e-400` is twelve characters in the file and eleven once the
    grouping mark is dropped. ELEVEN is the number this pair owes,
    because the twin writes `1234,5e-400` -- the width a person meets
    is the twin's, and a bound measured on a spelling the twin never
    writes is a bound it cannot hold.

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
        widths += [len(cell.numeric_text)]
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


def _declarations(
    spellings: tuple[str, ...], decimal_comma: bool = False
) -> "list[_Declaration]":
    """Read each declared value once, into the record the rules compare.

    ``decimal_comma`` says this COLUMN was declared as writing its
    numbers with a comma. Only the NUMBER a declaration denotes is read
    that way; `text` and `folded` keep the spelling the person typed,
    because the spelling half of the matching rule compares a
    declaration with a cell as the file writes it.

    THE TWO HALVES USED TO BE READ UNDER DIFFERENT GRAMMARS (review
    item P4-G3-R5-F1). `--decimal-comma amount --missing-value 1,234`
    read the cells with the comma, making `1,234` one and
    two-hundred-and-thirty-four thousandths, and read the DECLARATION
    ordinarily, making it one thousand two hundred and thirty-four.
    The rule is `exact_number_when_it_reads_as_one_else_spelling`, so a
    declaration that reads as a number is matched BY NUMBER and never
    by spelling -- and those two numbers are not equal. Every cell the
    person had explicitly called "no value" was counted as a
    measurement instead, and the column's presence, ladder, moments and
    role all moved with them, in silence.

    Guarantees: accepts the spellings a person typed and whether this
    column was declared; returns one record per spelling, in the order
    given. Raises TypeError if handed anything that is not text. No I/O
    of any kind.
    """
    made: list[_Declaration] = []
    for spelling in spellings:
        read = spelling
        if decimal_comma:
            read = parsing.written_with_a_decimal_comma(spelling)
        made += [
            _Declaration(
                text=spelling,
                folded=parsing.folded(spelling),
                exact=exact_of_spelling(read),
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
            distinct += [declaration]
    return len(distinct)


def contradictory_declarations(
    kept_values: "tuple[str, ...]",
    declared_missing_values: "tuple[str, ...]",
    decimal_comma: bool = False,
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

    ``decimal_comma`` says the table has at least one column declared
    that way, and then the pair is tested under BOTH readings -- the
    ordinary one and the comma one -- because a clash under either is a
    clash (review item P4-G3-R6-F2). `--decimal-comma amount
    --keep-value 1,234 --missing-value 1,2340` names one number twice
    on that column and two different numbers everywhere else; tested
    under the ordinary grammar alone the pair looks innocent, the
    command is accepted, and the missing declaration then quietly
    defeats the keep declaration on the very column the person
    declared. A refusal is the only honest answer, because no order of
    precedence turns two opposite instructions into one.

    Guarantees: accepts the two lists of declared values and whether
    any column is declared; returns one plain sentence per clashing
    pair, in the order the kept values were given, and an empty list
    when nothing clashes. Raises TypeError if handed anything that is
    not text. No I/O of any kind.
    """
    kept = _declarations(kept_values)
    missing = _declarations(declared_missing_values)
    swapped_kept = _declarations(kept_values, decimal_comma)
    swapped_missing = _declarations(declared_missing_values, decimal_comma)
    named: list[str] = []
    for place in range(len(kept)):
        one = kept[place]
        for seat in range(len(missing)):
            other = missing[seat]
            clashes = _same_declaration(one, other)
            # WHICH READING FOUND THE CLASH DECIDES HOW IT IS NAMED
            # (review item P4-G3-R7-F5). A pair caught only under the
            # comma reading was described with the ORDINARY parse of
            # the kept value, so `1,2340` beside `1,234` -- two visibly
            # different spellings, one number on a declared column --
            # was refused with the words "the same spelling", and a
            # refusal whose reason is visibly untrue is a refusal a
            # person cannot act on.
            one_said = one
            if decimal_comma and not clashes:
                clashes = _same_declaration(
                    swapped_kept[place], swapped_missing[seat]
                )
                if clashes:
                    one_said = swapped_kept[place]
            if not clashes:
                continue
            if one_said.exact is None:
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

    A PLACEHOLDER DAY IS MATCHED BY WHAT THE TEXT DENOTES, not by the
    text alone (plan P4-D252). The two members are written in ISO and a
    person types the spelling their own table uses, so `01/01/1900` on
    a month-first column named the member `1900-01-01` and was recorded
    as a word of their own -- and nothing downstream could then rebuild
    the instruction for a column whose own verdict the publication floor
    withheld. Denotation is asked of the typed text under this package's
    own readings; no cell is consulted, and what is recorded is still
    the member.

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
        # ...AND A SPELLING THAT DENOTES ONE OF THEM (plan P4-D252, the
        # extra review of c5d09d5, item 5). The comparison above is of
        # TEXT, and the two members are written in ISO, so a person who
        # types the spelling their own table uses -- `01/01/1900` on a
        # month-first column -- named a member of this vocabulary and
        # was recorded as having named a word of their own. The
        # producer's column-local rule matched their spelling and kept
        # the cells; the SETTINGS recorded nothing, so nothing could
        # rebuild the instruction where the column's own verdict fell
        # below the publication floor, and the table checked against its
        # own description lost those cells and missed fourteen
        # obligations (five `01/01/1900` beside 395 month-first dates at
        # a floor of eleven). What is recorded is still the member and
        # never the spelling, and still no cell of any table is read:
        # the question asked is what the typed text denotes under this
        # package's own readings.
        for reading in parsing.DATE_FORMATS:
            found = parsing.placeholder_day_of(spelling, reading)
            if found is not None:
                days[found] = 1
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
    values: list[str],
    settings: Settings,
    decimal_comma: bool = False,
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
    kept = _declarations(settings.kept_values, decimal_comma)
    declared_missing = _declarations(
        settings.declared_missing_values, decimal_comma
    )
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
    classified: "list[_Cell]",
    settings: Settings,
    decimal_comma: bool = False,
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
    declared_missing = _declarations(
        settings.declared_missing_values, decimal_comma
    )
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


def _judged_totals(
    entries: "list[dict[str, object]]",
    judged: "dict[str, dict[str, int]]",
    by_source: "dict[str, int]",
) -> "list[tuple[int, int]]":
    """The totals a reader holds beside `missing_by_source`, all of them.

    THE THIRD READING OF THE SPELLING CENSUS (round 2 of the review,
    the disclosure pass, item 2). `_missing_maps` weighed the spelling
    census against `n_missing` and the class census against it too, and
    both were clear -- but a published VERDICT carries a total of its
    own. `n_occurrences` is every cell that denoted one stand-in
    number, however it was spelled, and `spellings` names exactly those
    of its spellings the floor let the column publish. The difference
    between them is the count of cells wearing the spellings the floor
    POOLED, which is a count the pool exists to hide.

    **Measured** at a floor of eleven on 400 rows of a declared
    measurement -- 368 ordinary values, twenty `-999`, one `-999.0` and
    eleven `NA`: `missing_by_source {"-999": 20}` beside a judged
    `-999` verdict of `n_occurrences` 21 published 21 less 20, which is
    one cell of a spelling the description never names. The eleven
    pooled `NA` cells raised the overall pool to twelve and left that
    subtraction exactly where it was, because it is a reading INSIDE
    one candidate and neither map's own total touches it.

    So each published judged verdict hands back one `(total, covered)`
    pair -- its occurrences, and how many of them this column's
    spelling census accounts for. A verdict that kept its candidate as
    a number took no cell out and offers no pair; a candidate below the
    floor is not published at all, so it has no total a reader can
    hold.

    THESE PAIRS ARE ASKED AT THE SETTINGS FLOOR AND NOT AT THE LINE OF
    TWO (the repair pass of this landing, round 2's disclosure finding
    3). The first writing handed them to `census_names_one_row` beside
    the caller's own pair, which asks its line of two -- so a remainder
    of ONE closed and a remainder of two to ten stayed open.
    **Measured** at a floor of eleven with twenty `-999` beside TWO
    `-999.0`: the description published `missing_by_source {"-999": 20,
    "NA": 11}` against an `n_occurrences` of 22, and 22 less 20 is two
    cells wearing a spelling the description never names, under a floor
    of eleven. The line of two is right for the two maps beside this
    one, whose pooled remainder the description publishes as
    `(withheld)` -- there the subtraction gives back a count the reader
    already holds. Nothing publishes this remainder, so it is asked at
    the floor like every other count synthtwin withholds, which is what
    the item asked for in the first place.

    Guarantees: accepts the published decisions, the record
    `_spelling_judged` gathered and the floored spelling map; returns
    one pair per published judged decision. Determinism: a function of
    the three; the keys are read in sorted order. Raises nothing. No
    I/O of any kind.
    """
    totals: "list[tuple[int, int]]" = []
    for entry in entries:
        if _text_at(entry, "verdict") != VERDICT_MISSING:
            continue
        candidate = _text_at(entry, "candidate")
        if candidate not in judged:
            continue
        occurrences = entry["n_occurrences"]
        if not isinstance(occurrences, int):
            continue
        covered = 0
        for spelling in sorted(judged[candidate]):
            if spelling in by_source:
                covered = covered + by_source[spelling]
        totals += [(occurrences, covered)]
    return totals


def _missing_maps(
    missing: list[tuple[str, str]],
    settings: Settings,
    entries: "list[dict[str, object]]",
    judged: "dict[str, dict[str, int]]",
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

    AND BLANK MEANS THE EMPTY SPELLING, NOTHING ELSE (plan P4-D74,
    contract C6-125). A cell holding one space, two spaces, a tab or a
    no-break space is not a cell that holds nothing: it holds a mark
    somebody's writer put there, which the reader of the real table
    meets. This function counted every such cell in `n_missing_blank`
    and lost its characters, so the twin wrote an empty cell where the
    table wrote a space and no published fact could tell the two files
    apart. Measured on a 500-row column of readings: 315 absent cells,
    177 of them holding a space, two spaces or a no-break space, all
    published as `n_missing_blank: 315` and all written empty -- while
    `pandas.to_numeric` runs on the twin and raises on the table, and a
    reader handed `na.strings=c("","NA")` finds levels on the table the
    twin does not have.

    A whitespace-only spelling is therefore an ordinary key from here
    on, stored character for character and held to the floor like every
    other spelling, and `n_missing_blank` counts the cells that held the
    EMPTY spelling alone. The class map is unchanged and still reads
    such a cell as `(blank)`, because the REASON it is absent is that
    nothing meaningful was written there; contract 5.4.4 is where the
    two questions are stated apart.

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

    AND A POOL OF ONE IS NOT A POOL (plan P4-D293, the merge-close of
    2026-09-18; `parsing.census_floor`'s own rule, "NEVER ONE, WHATEVER
    THE SETTINGS FLOOR"). Both maps pool what the floor cannot name, and
    until this entry neither asked whether the POOL named a row.
    **Measured** at a floor of eleven on 400 rows -- `north` x200,
    `south` x180, `NA` x19 and one `-999`: the description published
    `n_missing` 20, `missing_by_source {"NA": 19}`, `missing_by_class
    {"(text-code)": 19, "(withheld)": 1}` and `n_missing_withheld` 1,
    and two readings named that one row -- the count of one outright,
    and 20 less 19 by subtraction from the sibling total. Both documents
    loaded and every exit was nought.

    THE REPAIR RAISES THE POOL, IT DOES NOT MOVE A CELL INTO A NAMED
    GROUP. Both were built and both were measured. Counting the rare
    cell into the commonest spelling -- ruling 6's treatment of a
    spelling -- publishes `missing_by_source {"NA": 20}` over a table
    holding nineteen, and the REAL TABLE then misses its own
    description: `holes.by_source.NA` MISSED, 20 asked and 19 held,
    validate exit 3 on the table itself. A description that does not
    describe the table is not a repair, so the rule here is the floor's
    own: while `parsing.census_names_one_row` says either map names a
    row, the SMALLEST NAMED SPELLING joins the pool, in both maps at
    once, and the maps are counted again. The same 400 rows now publish
    `missing_by_source {}`, `missing_by_class {"(withheld)": 20}` and
    `n_missing_withheld` 20, which is exactly what the same table
    publishes at a floor of twenty, and both files validate at nought.

    THE TWO MAPS ARE RAISED TOGETHER because they cut the same cells two
    ways: a class holds every cell of each of its spellings, so pooling
    a spelling in one map and not the other would leave the class map
    naming the row the spelling map had just stopped naming.

    ITS NAMED LIMIT: where the pool already holds EVERY absent cell --
    one lone `NA` among 380 present -- there is no named group left to
    raise it with, and `missing_by_class` publishes `{"(withheld)": 1}`.
    The pool is then `n_missing` itself, a count the column publishes on
    its own terms beside it, so the map adds no reading to the one the
    description already carries. `census_names_one_row` reads no row
    there for the same reason: a census covering no cell of a total
    leaves the reader nothing to subtract.

    AND THE THIRD TOTAL IS A JUDGED CANDIDATE'S OWN (round 2 of the
    review, the disclosure pass, item 2). `_judged_totals` next door
    states what that total is and what it was measured to give away;
    the pool is raised against it by this same walk and by this same
    rule, which is why it arrives as another pair handed to
    `census_names_one_row` rather than as a second reading of the
    disclosure rule somewhere else.
    """
    held_back: "list[str]" = []
    if settings.small_cell_floor <= 1:
        # A FLOOR OF ONE IS THE PERSON SAYING NO GROUP IS TOO SMALL, and
        # the pool is empty there by construction: `profile.
        # _remainder_is_published` refuses a remainder above nought at
        # that floor outright. Raising the pool here would build the very
        # description that guard exists to stop, so the rule below binds
        # where pooling happens at all -- above one (plan P4-D293).
        return _missing_counted(missing, settings, held_back)
    for _round in range(len(missing) + 1):
        by_source, pooled, named_blank, withheld = _missing_counted(
            missing, settings, held_back
        )
        named_classes: dict[str, int] = {}
        covered_classes = 0
        for name in parsing.MISSING_CLASSES:
            if name == parsing.MISSING_WITHHELD:
                continue
            named_classes[name] = pooled[name]
            covered_classes = covered_classes + pooled[name]
        covered_spellings = named_blank
        for key in sorted(by_source):
            covered_spellings = covered_spellings + by_source[key]
        total = len(missing)
        names_a_row = parsing.census_names_one_row(
            named_classes, [(total, covered_classes)]
        ) != -1 or parsing.census_names_one_row(
            by_source, [(total, covered_spellings)]
        ) != -1 or parsing.census_names_one_row(
            {},
            _judged_totals(entries, judged, by_source),
            settings.small_cell_floor,
        ) != -1
        if not names_a_row:
            return by_source, pooled, named_blank, withheld
        smallest = _smallest_named_spelling(by_source, named_blank, settings)
        if smallest is None:
            return by_source, pooled, named_blank, withheld
        held_back += [smallest]
    return _missing_counted(missing, settings, held_back)


def _smallest_named_spelling(
    by_source: "dict[str, int]", named_blank: int, settings: Settings
) -> "str | None":
    """The named absent spelling the pool takes next, or None (P4-D293).

    The smallest of the spellings the floor let `_missing_maps` name,
    with the empty spelling standing for the blank cells counted beside
    the map; ties are settled by the sorted spelling, so the answer is a
    function of the counts alone and the pool grows the same way twice.
    The smallest is taken because it is the one whose loss costs the
    description least. None means no named spelling is left, which is
    the limit `_missing_maps` states.

    Guarantees: reads its three arguments; returns a spelling or None.
    Determinism: a fixed function of the arguments. Raises nothing. No
    I/O of any kind.
    """
    smallest: "str | None" = None
    count = 0
    if named_blank >= settings.small_cell_floor:
        smallest = ""
        count = named_blank
    for key in sorted(by_source):
        if smallest is None or by_source[key] < count:
            smallest = key
            count = by_source[key]
    return smallest


def _missing_counted(
    missing: "list[tuple[str, str]]",
    settings: Settings,
    held_back: "list[str]",
) -> "tuple[dict[str, int], dict[str, int], int, int]":
    """The two maps and the two counts, with the floor applied once.

    This is the arithmetic `_missing_maps` has always run, with one
    argument added by P4-D293: ``held_back`` names spellings the caller
    has already decided the pool takes, whatever the floor says of them.
    A cell wearing one of those spellings is pooled in BOTH maps -- its
    class is not named either -- which is what keeps the two maps
    cutting the same cells.

    Guarantees: accepts the absent cells, the settings and the
    held-back spellings; returns the spellings map, the class map, the
    named blank count and the pooled count. Determinism: a fixed
    function of the three. Raises nothing. No I/O of any kind.
    """
    by_class: dict[str, int] = {}
    for name in parsing.MISSING_CLASSES:
        by_class[name] = 0
    withheld_cells = 0
    for spelling, name in missing:
        if spelling in held_back:
            withheld_cells = withheld_cells + 1
            continue
        by_class[name] = by_class[name] + 1
    pooled: dict[str, int] = {}
    for name in parsing.MISSING_CLASSES:
        pooled[name] = 0
    pooled[parsing.MISSING_WITHHELD] = withheld_cells
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
        # THE EMPTY SPELLING AND NO OTHER (P4-D74). A cell of spaces
        # wears a spelling; the docstring above says what counting it
        # as blank cost.
        if spelling == "":
            blank = blank + 1
            continue
        if spelling in exact:
            exact[spelling] = exact[spelling] + 1
        else:
            exact[spelling] = 1
    withheld = 0
    for key in sorted(exact):
        if exact[key] >= settings.small_cell_floor and key not in held_back:
            by_source[key] = exact[key]
        else:
            withheld = withheld + exact[key]
    named_blank = 0
    if blank >= settings.small_cell_floor and "" not in held_back:
        named_blank = blank
    else:
        withheld = withheld + blank
    return by_source, pooled, named_blank, withheld


# -- numeric sentinels ------------------------------------------------


def _sentinel_verdicts(
    cells: _Cells, n_present: int, judged: "tuple[str, ...]" = ()
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

    ``judged`` is handed over by the validator alone (plan P4-D6.4,
    validation method V2.4-A8): the candidates the description it
    checks against published as `read_as_missing` in THIS column. Such a
    candidate is read as missing without the arithmetic being asked
    again, because the description already settled it for this column
    and the twin writes its cells as the source wrote them -- and a
    twin's own values need not fire the outlier rule a second time.
    Measured before this: 400 whole numbers whose fence stood a few units
    inside `-999`, twelve `-999` cells, eight seeds -- five twins read the
    twelve as values and missed obligations while the real table passed.
    A `--keep-value` still wins, as it does everywhere (C6-117).
    `synthtwin profile` never passes it.

    Returns candidate -> (is missing, reason code, occurrences).
    """
    settings = cells.settings
    kept = _declarations(settings.kept_values, cells.decimal_comma)
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
        if _judged_by_the_description(candidate, judged):
            verdicts[candidate] = (
                True,
                REASON_OUTLIER_AND_FREQUENT,
                occurrences,
            )
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


def _judged_by_the_description(
    candidate: float, judged: "tuple[str, ...]"
) -> bool:
    """Whether a checked description judged this stand-in number missing.

    Compared as the EXACT number both denote, which is the identity the
    candidate was counted by, so a description publishing `-999` names
    the candidate a file writes `-999.0`. A published name that is no
    number names nothing here. Raises nothing; no I/O.
    """
    exact = exact_of_number(candidate)
    for named in judged:
        if exact_of_spelling(named) == exact:
            return True
    return False


# -- calendar placeholders --------------------------------------------


def _placeholder_verdicts(
    present: "list[str]",
    format_name: str,
    settings: Settings,
    decimal_comma: bool = False,
    kept_days: "tuple[str, ...]" = (),
    judged_days: "tuple[str, ...]" = (),
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

    AND A DAY THIS COLUMN'S OWN DESCRIPTION RECORDS AS KEPT is kept
    (plan P4-D136). `kept_days` is handed over by the validator alone:
    the placeholder days a description it checks against published as
    `kept_by_you` in THIS column. A person who typed `01/01/1900` after
    `--keep-value` kept the cells spelled that way, and the settings
    block records only the vocabulary's own `1900-01-01` -- so without
    this the checked file's placeholder cells were judged as holes,
    and the table checked against its own description went from 500
    values to 470 and missed 14 obligations. It is asked of this column
    and no other, which is exactly how far the person's spelling reached.
    `synthtwin profile` never passes it.

    AND A DAY THIS COLUMN'S OWN DESCRIPTION JUDGED MISSING is missing
    (plan P4-D6.4), the other side of the same hand-over: `judged_days`
    are the placeholder days the checked description published as
    `read_as_missing` in this column. The twin writes those cells as the
    source wrote them, and a twin's generated dates need not fire the
    interquartile rule a second time, so the description's own verdict
    answers. A kept day still wins. `synthtwin profile` never passes it.

    Returns placeholder -> (is missing, reason code, occurrences).
    """
    kept = _declarations(settings.kept_values, decimal_comma)
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
        if _declared_spelling(candidate, kept) or candidate in kept_days:
            verdicts[candidate] = (False, REASON_KEPT_BY_USER, occurrences)
            continue
        if _kept_by_spelling(present, format_name, candidate, kept):
            verdicts[candidate] = (False, REASON_KEPT_BY_USER, occurrences)
            continue
        if candidate in judged_days:
            verdicts[candidate] = (
                True,
                REASON_OUTLIER_AND_FREQUENT,
                occurrences,
            )
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


def _spelling_judged(
    found: "dict[str, dict[str, int]]", candidate: str, spelling: str
) -> None:
    """Record that one candidate's pass took a cell spelled this way.

    THE PROVENANCE OF A HOLE SPELLING, GATHERED WHERE IT IS KNOWN
    (repair pass of landing 2b.6). A cell the person DECLARED is taken
    out before any pass judges anything, so a spelling reaching this
    record was put there by a judged pass and by nothing else. Both
    readers of the finished description -- the generator, which decides
    which spellings reach the whole table, and the validator, which
    reads the person's declarations back out of the columns -- had to
    guess this by counting, and no count can tell two keys writing one
    placeholder day apart: 500 rows with twenty judged
    `1900-01-01 00:00:00` beside thirty declared `1900-01-01T00:00:00`
    promoted the judged spelling to every column and made the REAL
    table miss thirteen obligations of its own description.

    The inner mapping is a mapping rather than a set for the reason
    `kept_spellings` gives (plan D6.2); its values are never read.

    Guarantees: accepts the record, the candidate as the description
    will publish it, and the cell's own spelling; adds one entry.
    Determinism: a function of the three. Raises nothing. No I/O.
    """
    if candidate not in found:
        found[candidate] = {}
    found[candidate][spelling] = 1


def _judged_spellings_published(
    entries: "list[dict[str, object]]",
    judged: "dict[str, dict[str, int]]",
    by_source: "dict[str, int]",
) -> "list[dict[str, object]]":
    """Each decision's own published hole spellings (contract V5).

    THE FLOOR DECIDES WHAT MAY BE NAMED HERE, and it has already
    decided: a spelling is written into a decision only where it is a
    key of `missing_by_source`, so this publishes no group the floor
    pooled and no spelling the document does not already carry. What is
    new is the LINK between the spelling and the pass that took it,
    which is a fact about the DESCRIBING RUN rather than about any row.

    A decision that kept its candidate as a number took no cell out and
    names nothing. A candidate below the floor is not published at all
    (V1), so its spellings have no entry to stand in.

    Guarantees: accepts the published decisions, the record
    `_spelling_judged` gathered and the floored spelling map; returns
    the decisions with their spellings filled, sorted and without
    repeats. Determinism: a function of the three. Raises nothing. No
    I/O of any kind.
    """
    filled: "list[dict[str, object]]" = []
    for entry in entries:
        candidate = _text_at(entry, "candidate")
        named: "list[str]" = []
        if _text_at(entry, "verdict") == VERDICT_MISSING and candidate in judged:
            for spelling in sorted(judged[candidate]):
                if spelling in by_source:
                    named += [spelling]
        carried: "dict[str, object]" = {}
        for key in sorted(entry):
            carried[key] = entry[key]
        carried["spellings"] = named
        filled += [carried]
    return filled


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
                # WHICH PUBLISHED SPELLINGS THIS DECISION TOOK OUT
                # (repair pass of landing 2b.6). Empty here and filled
                # by `profile_column` once the floor has decided which
                # spellings are named at all: this function does not
                # see the cells, and a spelling below the floor may not
                # be named anywhere.
                "spellings": [],
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
                # Filled by `profile_column`, for the reason the numeric
                # half gives.
                "spellings": [],
            }
        ]
    return entries, unpublished


# -- levels -----------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class _Levels:
    """The published level list and everything pooled out of it.

    The pool is two numbers and no sizes (owner ruling of 2026-09-17,
    item 2, option A; plan P4-D201): how many labels were held back and
    how many rows they covered together.
    """

    published: list[dict[str, object]]
    suppressed_levels: int
    suppressed_rows: int
    # THE SCALE OF THE POOLED NUMBERS (plan P4-D302, ledger K-2B-50),
    # under `n_cells` and `mean`. The pool itself is what this
    # aggregate is taken over, and `_pooled_numbers` states why that is
    # a group and not a row -- and why no spread stands beside it.
    pooled_numbers: dict[str, object]


def _absorb_lone_spellings(
    spellings: "dict[str, int]", settings: Settings
) -> "dict[str, int]":
    """One level's spellings, with every BELOW-FLOOR spelling counted into
    its commonest (plans P4-D240, P4-D275).

    THE OWNER'S RULING OF 2026-09-17, ITEM 6 (plan P4-D222, CONFIRMED),
    ASKED OF A LABEL'S SPELLINGS. For the six older number censuses a
    spelling below the line is counted into the commonest named one, so
    that no row is named; the label variants census was left out of that
    treatment and went on publishing a count of one outright. Measured on
    the tree this repairs: 490 `F`, 500 `M` and one `f` at a floor of
    eleven published, for the level `f`, `variants {"F": 490}` beside
    `variants_withheld {"1": 1}` -- by that census's own definition, ONE
    held-back spelling covering exactly ONE row -- and the twin then
    wrote a lone `f` cell in exactly one row. The same shape at a floor
    of five on 46 rows published the same pair.

    A SPELLING THE FLOOR HOLDS BACK IS THEREFORE COUNTED INTO THE
    LEVEL'S COMMONEST SPELLING, exactly as ruling 6 counts a rare mark
    into the commonest mark: the description is the description of the
    table with those cells written the way most of the level's cells
    were, `variants_withheld` carries nothing at all, and the twin writes
    the commonest spelling in those rows. Ties for the commonest go to
    the first spelling in sorted order, which is the tie rule
    `parsing.absorbed_census` already states.

    EVERY SPELLING BELOW THE LINE AND NOT THE ONE-ROW SPELLINGS ALONE
    (plan P4-D275, the repair of the extra review round of 2026-09-18).
    This rule was written for a count of ONE and stopped there, and the
    line it stopped short of is the one ruling 6 draws. **Measured** at a
    floor of eleven on 490 `F`, 500 `M` and TWO `f`: the pair was not
    absorbed at all, the level published `variants {"F": 490}` beside
    `variants_withheld {"2": 1}` -- one held-back spelling that exactly
    two rows wrote -- and the twin wrote two `f` cells. Two rows is a
    group below the line as surely as one row is, and the multiplicity
    map states its size outright. So the line is `small_cell_floor`, the
    same line `_variants` names a spelling at, and the second mapping is
    empty on every level of every raised-floor description.

    AT A FLOOR OF ONE NOTHING MOVES. A floor of one holds no spelling
    back, so every spelling is named and there is nothing to count in:
    a label written fifty different ways at that floor still publishes
    all fifty. Only a raised floor reaches this at all.

    Guarantees: accepts one folded identity's exact spellings with how
    many rows wrote each, and the settings whose floor governs them;
    returns a mapping over the same total, keyed by spellings of the
    same level, with no entry of one row where the floor is above one.
    Determinism: a fixed function of the two, walked in sorted order.
    Raises nothing. No I/O of any kind.
    """
    if settings.small_cell_floor <= 1:
        return dict(spellings)
    lone: "list[str]" = []
    rest: "dict[str, int]" = {}
    for spelling in sorted(spellings):
        if spellings[spelling] < settings.small_cell_floor:
            lone += [spelling]
        else:
            rest[spelling] = spellings[spelling]
    if not lone:
        return dict(spellings)
    commonest = ""
    for spelling in sorted(rest):
        if not commonest or rest[spelling] > rest[commonest]:
            commonest = spelling
    absorbed: "dict[str, int]" = {}
    for spelling in sorted(rest):
        absorbed[spelling] = rest[spelling]
    if not commonest:
        # NO SPELLING REACHES THE LINE, AND THE COMMONEST IS STILL ONE OF
        # THEM -- the tie rule `parsing.absorbed_census` states (plan
        # P4-D242). This took the first in sorted order whatever the
        # counts, which was the commonest only while every spelling here
        # was written once (P4-D240). Once P4-D275 brought in every
        # spelling below the line it was not: **measured** at a floor of
        # eleven, a level written as 2 `A` and 9 `a` published
        # `variants {"A": 11}` and the twin wrote the spelling two rows
        # wore in all eleven.
        for spelling in lone:
            if not commonest or spellings[spelling] > spellings[commonest]:
                commonest = spelling
        absorbed[commonest] = 0
    taken = 0
    for spelling in lone:
        taken = taken + spellings[spelling]
    absorbed[commonest] = absorbed[commonest] + taken
    return absorbed


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
      the second mapping names nothing at all. AT A RAISED FLOOR THE
      SECOND MAPPING IS EMPTY: every spelling below the line is counted
      into the level's commonest first (`_absorb_lone_spellings` above,
      plans P4-D240 and P4-D275), because a multiplicity map keyed `1`
      states a count of one outright and a map keyed `2` states a group
      of two. It carries entries only at a floor of one, where nothing
      is held back and the map is empty for that reason instead.
    """
    counted = _absorb_lone_spellings(spellings, settings)
    named: dict[str, int] = {}
    withheld: list[int] = []
    for spelling in sorted(counted):
        count = counted[spelling]
        if count >= settings.small_cell_floor:
            named[spelling] = count
        else:
            withheld += [count]
    return (named, _multiplicity_map(withheld))


def shape_form_cells(spellings: dict[str, int]) -> int:
    """How many cells of ONE level were written in a form (plan A-P4-47).

    THE FACT THAT LETS A LEVEL'S STAND-IN SPELLINGS KEEP ITS SHAPE.
    `shape_forms` beside it is a census of the whole COLUMN, and the
    twin covers that census out of whatever cells it writes;
    which of a level's held-back spellings wore the label's form is a
    fact the column census cannot carry, so the twin guessed and was
    wrong in both directions (residual R-P4-34). This is that fact,
    published for each level of its own.

    IT IS ONE NUMBER AND NOT A MAP, and that is a property rather than
    a simplification. A spelling belongs to a level when trimming and
    case folding it gives the label. A spelling that HAS a form holds
    only ASCII letters, ASCII figures and the marks -- no space, so
    trimming changes nothing -- and folding an ASCII letter leaves an
    ASCII letter in the same place, so `parsing.shape_form` answers the
    same string for the spelling and for its fold. Every form-bearing
    spelling of a level therefore wears exactly `shape_form(label)`,
    and a level's census can name at most that one form. A label with
    no form of its own has no form-bearing spelling at all, so this
    answers 0 for it.

    WHAT IT DOES NOT PUBLISH. No spelling, and no form key: the form
    this counts is `shape_form` of the level's own published label,
    which the reader already holds. The floor governs which VALUES are
    named and it still does; this names none.

    Guarantees:

    - Inputs: the exact spellings of ONE folded identity with how many
      rows wrote each -- the same mapping `_variants` above is handed.
    - Determinism: the answer depends only on that mapping, and the
      spellings are walked in sorted order.
    - Errors raised: none.
    - Boundary: the answer is between 0 and the level's own row count,
      and no character of any spelling reaches it.
    """
    shaped = 0
    for spelling in sorted(spellings):
        if parsing.shape_form(spelling):
            shaped = shaped + spellings[spelling]
    return shaped


def described_spellings(
    values: "list[str]", settings: Settings
) -> "list[str]":
    """Every cell as the level entries speak of it, in the order given.

    THE ONE STATEMENT OF THE RESPELLING, read by the producer and by the
    checker so the two cannot part (plan P4-D275.1, the repair of the
    merge of the extra round's fixes). P4-D275 counts every spelling below
    the floor into its level's commonest, so the description is the
    description of the table with those cells written the way most of the
    level's cells were -- and the level entry's `variants` and
    `shape_form_cells` say so. The column's `shape_forms` went on counting
    the cells as the source wrote them. **Measured** at a floor of eleven,
    on 181 four-figure codes beside a level of twenty `e11.9`, five
    `E11.9` and three `E11.9` written with trailing spaces: the level
    published `variants {"e11.9": 28}` and `shape_form_cells 28` beside a
    column census of `{"@%%.%": 206}`. Those are two tables. The twin
    writes the first, 209 cells in the form, so `synthtwin validate`
    MISSED the twin on the census while the table passed its own; and the
    three cells the census left out were the held-back group of three the
    absorption exists to hide.

    So a cell of a label whose rows reach the floor is respelled exactly
    as `_absorb_lone_spellings` counts it: a spelling it keeps stays, and
    a spelling it counts in is written as the spelling it was counted
    into. A cell of a label the floor holds back keeps its own spelling,
    which no key of the block names -- the rule `_published_distinct`
    states, so the number of different spellings in the answer is that
    count. A blank cell is handed back as it came. At a floor of one
    nothing is absorbed and the answer is the cells unchanged.

    THE CHECKER ASKS IT TOO. `synthtwin validate` recounts the census off
    the file's own cells, and a recount of the raw cells would find the
    table's twenty `e11.9` where its own description, made by this rule,
    says twenty-eight -- so the table would miss its own description.

    Guarantees: accepts cells and the settings whose floor governs them;
    returns one spelling per cell, in the same order, each folding onto
    that cell's own label. Determinism: a fixed function of the two,
    walked in sorted order. Raises nothing. No I/O of any kind.
    """
    groups: "dict[str, dict[str, int]]" = {}
    for value in values:
        label = parsing.folded(value)
        if label not in groups:
            groups[label] = {}
        spellings = groups[label]
        spellings[value] = (spellings[value] if value in spellings else 0) + 1
    written_as: "dict[str, dict[str, str]]" = {}
    for label in sorted(groups):
        spellings = groups[label]
        target: "dict[str, str]" = {}
        rows = 0
        for spelling in sorted(spellings):
            target[spelling] = spelling
            rows = rows + spellings[spelling]
        if label and rows >= settings.small_cell_floor:
            absorbed = _absorb_lone_spellings(spellings, settings)
            into = ""
            for spelling in sorted(absorbed):
                if absorbed[spelling] != spellings[spelling]:
                    into = spelling
            if into:
                for spelling in sorted(spellings):
                    if spelling not in absorbed:
                        target[spelling] = into
        written_as[label] = target
    return [written_as[parsing.folded(value)][value] for value in values]


def _published_distinct(cells: _Cells) -> int:
    """How many different spellings a label column's own block says it holds.

    THE COUNT DERIVED FROM THE PROTECTED SPELLINGS AND NOT FROM THE RAW
    ONES (plan P4-D276, the repair of the extra review round of
    2026-09-18). `n_distinct` counted the column's different cells
    exactly, and a published level's `variants` census counts the
    spellings the floor let it name -- so the difference between them
    counted the spellings the absorption took away, and while the
    absorption reached one-row spellings alone that difference WAS a
    count of one. **Measured** at a floor of eleven on 490 `F`, 500 `M`
    and one `f`: the block published `variants {"F": 491}` and
    `{"M": 500}`, no withheld spelling anywhere, and `n_distinct 3` --
    three spellings, two of them named, and the one left over is the row
    that wrote `f`.

    So the count is taken over the spellings the block SPEAKS OF: for
    every level the floor publishes, the spellings that survive
    `_absorb_lone_spellings`, and for every level the floor holds back,
    its own spellings, which no key of this block names and which no
    reader can subtract a published census from.

    Guarantees: accepts the column's tally; returns a count between the
    number of folded identities and `raw_distinct`. Determinism: a fixed
    function of the tally, walked in sorted order. Raises nothing. No I/O
    of any kind.
    """
    counted = 0
    for label in sorted(cells.folded_counts):
        spellings = cells.spellings_by_folded[label]
        if cells.folded_counts[label] >= cells.settings.small_cell_floor:
            spellings = _absorb_lone_spellings(spellings, cells.settings)
        for _spelling in sorted(spellings):
            counted = counted + 1
    return counted


def _column_distinct(
    cells: _Cells, role: str, details: "dict[str, object]"
) -> int:
    """The column's own `n_distinct`, counted the way its block speaks.

    ON THE FOUR LEVEL ROLES it is `_published_distinct` (plan P4-D276).
    ON A COMPOUND COLUMN IT IS THE TWO HALVES ADDED, and it was the raw
    count (the carried numbers pass of 2026-09-18, amending P4-D276).
    P4-D276 moved the LABEL HALF's own `n_distinct` to the spellings that
    half speaks of and left the column's count raw, so wherever the
    absorption took a spelling away the two disagreed -- and the loader
    holds them to `n_numeric_distinct + labels.n_distinct == n_distinct`
    (contract 7.14), so the producer wrote a description its own loader
    refused. **Measured** at a floor of eleven on forty exponents `2e0`
    to `80e0` beside `alpha` 6, `Alpha` 6, `beta` 5 and `Beta` 5: the
    label half published 3 (the level `alpha` absorbed into `Alpha`,
    and the held-back level's two spellings), the numeric half 40, and
    the column 44; `contract.load_profile` refused it. A raw 44 beside a
    published 40 and 3 is also the residual P4-D276 closed on the label
    roles -- the difference counts the spellings the absorption took
    away -- so the column's count is the halves' sum and not the raw one.

    Every other role keeps the raw count of different present cells.

    Guarantees: accepts the column's tally, its role and its published
    details; returns a whole number between the column's folded count
    and its raw count. Determinism: a fixed function of the three.
    Raises nothing. No I/O of any kind.
    """
    if role in _LEVEL_ROLES:
        return _published_distinct(cells)
    if role != ROLE_COMPOUND:
        return cells.raw_distinct
    if "n_numeric_distinct" not in details or "labels" not in details:
        return cells.raw_distinct
    numbers = details["n_numeric_distinct"]
    labels = details["labels"]
    if not isinstance(numbers, int) or not isinstance(labels, dict):
        return cells.raw_distinct
    if "n_distinct" not in labels:
        return cells.raw_distinct
    spoken = labels["n_distinct"]
    if not isinstance(spoken, int):
        return cells.raw_distinct
    return numbers + spoken


# WHAT A POOLED NUMERIC AGGREGATE PUBLISHES WHEN IT CANNOT SPEAK, and
# it is the state a pool of no numbers at all reaches (plan P4-D301).
# The two are deliberately the same two values, so that NO REFUSAL
# REASON IS DISTINGUISHABLE FROM ANOTHER: a refused pool of one value,
# a refused pool with no room to move and a pool holding no number at
# all publish the identical block, and nothing in this state says which
# rule was reached or how close the pool came to passing it.
#
# WHAT THIS STATE DOES NOT HIDE, said plainly because the comment here
# once claimed otherwise. The pooled numeric CELL COUNT is derivable
# from the block whether the pool speaks or not: `n_numeric` is
# published beside every published level and its count, so a reader
# subtracts the published numeric levels' cells from `n_numeric` and
# has it. Measured over the twelve shapes of this landing's table:
# `narrow_width` publishes nought here while a reader computes 48,
# `one_value_six_spellings` nought against 48, `two_levels` nought
# against 20, `wider_than_shown` nought against 24. That count is a
# fact section 6.3 already publishes elsewhere, and what this state
# withholds is the pool's SCALE, not its size.
_NO_POOLED_SCALE: "dict[str, object]" = {
    "n_cells": 0,
    "mean": None,
}

# HOW MANY ARRANGEMENTS OF THE HELD-BACK VALUES the published mean must
# leave before the block may speak at all (the owner's decision of
# 2026-09-21, plan P4-D302). It replaces the level rule, the flat rule
# and the looseness rule the published SPREAD needed, and it is the one
# question all three were asking badly: how many different populations
# fit everything this description says about the pool.
#
# WHY ONE RULE AND NOT THREE. A mean and a spread are two equations, and
# two equations over a pool packed as closely as its own grid allows
# leave ONE arrangement -- which is why the spread needed a looseness
# rule, a level rule and a rule against a pool of no spread. A mean
# alone is ONE equation. MEASURED, over twenty-five random pools of
# distinct whole numbers at each level count, the sizes given to the
# reader and the search over every value the column's own width allows:
#
#   levels | solved outright | down to four | median arrangements
#        1 |       25 of 25  |    25 of 25  | 1
#        2 |        none     |     none     | 224
#        3 |        none     |     none     | 47,502
#        4 |        none     |     none     | 4,219,740
#        5 |        none     |     none     | 457,634,000
#        6 |        none     |     none     | 76,176,700,000
#
# and the same family drawn AT THE TIGHTEST ARRANGEMENT ITS VALUES COULD
# TAKE -- the shape the spread named outright -- comes back at a median
# of 189, 45,757 and 6,318,400 for two, three and four levels. The
# looseness rule bought nothing once the spread was gone, and it is
# withdrawn with that measurement beside it.
#
# WHAT THE COUNT OF LEVELS DID NOT SEE, and this rule does. A pool of
# six one-figure numbers beside a published one-figure number passed
# every one of the three old rules and is NAMED: six different whole
# numbers of one figure is six of the ten there are, and the mean says
# which six to within sixteen answers. Measured over every pool of one-
# figure numbers, at every level count from one to seven, the smallest
# surviving count is ONE -- a pool standing against either end of the
# range its width allows is named whatever its level count. What
# protects the values is ROOM, and the room is what is counted.
#
# THE BOUND IS A THOUSAND. The level rule of six this replaces was
# accepted with a measured median of 118 arrangements and two pools of
# twenty-five down to four; this asks a thousand of EVERY pool rather
# than a median of the family, which is stricter than the rule it
# replaces at the place that rule was weakest.
_POOLED_SCALE_ROOM = 1000

# HOW FAR THE COUNT WALKS before it stops and answers "at least this
# many". The count never falls as a pool gains room up to the middle of
# its own range, so a pool with more room than this has at least as many
# arrangements as one standing exactly here, and counting further buys
# nothing but time. At this much room a pool of three levels already has
# more than five thousand arrangements, so the bound above is never
# decided by the stopping point except where the count is exact.
_POOLED_SCALE_COUNTED = 256


def _arrangements(
    levels: int, points: int, owed: int, bounded: bool
) -> int:
    """How many arrangements of the pool's values the published mean leaves.

    THE QUESTION. Take the numbers the pool holds: ``levels`` different
    ones, standing on the grid its own values stand on, inside the
    ``points`` places the column's width and its sign census allow. How
    many sets of that many different places add up to what the mean and
    the cell count say the pool adds up to? ``owed`` is that sum less
    the smallest such sum, counted in grid steps, so nought means the
    pool is packed against the bottom of its range.

    THE COUNT HAS A CLOSED ANSWER. Choosing ``levels`` different places
    out of ``points`` with a fixed sum is the same question as splitting
    ``owed`` into at most ``levels`` parts, none larger than
    ``points - levels``; the number of those is one coefficient of a
    Gaussian binomial, which the walk below builds a factor at a time.
    Checked against an exhaustive count of every subset over 980 cases
    at four range sizes and seven level counts: the same number every
    time.

    TWO SHORTCUTS, BOTH FACTS ABOUT THE COUNT AND NOT APPROXIMATIONS OF
    IT. The count is symmetric about the middle of its own range, so
    ``owed`` folds to the nearer end; and it never falls on the way up
    to that middle, so the walk stops at `_POOLED_SCALE_COUNTED` steps
    of room and the answer is then a floor rather than the total. A
    caller comparing against a bound is answered either way.

    ``bounded`` is False where the column publishes no number of its
    own, which is where no width bounds the values: the parts are then
    unbounded and neither the fold nor the out-of-range refusal applies.

    Guarantees: accepts the level count, the places, the room owed and
    whether a width bounds it; returns nought or more, and nought where
    no arrangement fits the range at all. Determinism: a fixed function
    of the four. Raises nothing. No I/O of any kind.
    """
    if levels < 1 or owed < 0:
        return 0
    widest = owed
    if bounded:
        if points < levels:
            return 0
        widest = points - levels
        reach = levels * widest
        if owed > reach:
            return 0
        if owed > reach - owed:
            owed = reach - owed
    if owed > _POOLED_SCALE_COUNTED:
        owed = _POOLED_SCALE_COUNTED
    row = [0] * (owed + 1)
    row[0] = 1
    for step in range(1, levels + 1):
        gap = widest + step
        if gap <= owed:
            for place in range(owed, gap - 1, -1):
                row[place] = row[place] - row[place - gap]
        for place in range(step, owed + 1):
            row[place] = row[place] + row[place - step]
    return row[owed]


def _closest_step(values: "list[float]") -> float:
    """The closest two DIFFERENT values of a pool stand, or nought.

    A reader solving for the pool's values is solving over a grid, and
    this is the coarsest grid the pool's own values sit on that this
    module can read off them. Taking the smallest gap rather than a
    finer one is the careful direction: a coarser grid makes the
    tightest arrangement wider, which makes `_pooled_numbers` refuse
    more often and never less.

    Guarantees: accepts any list; returns the smallest positive
    difference between two of its values, or nought where it holds
    fewer than two different ones. Determinism: a fixed function of the
    multiset. Raises nothing. No I/O of any kind.
    """
    ordered = sorted(set(values))
    closest = 0.0
    for place in range(1, len(ordered)):
        gap = ordered[place] - ordered[place - 1]
        if gap > 0.0 and (closest <= 0.0 or gap < closest):
            closest = gap
    return closest


def _whole_figures_of(value: float) -> int:
    """How many figures a number has before its decimal mark, sign aside.

    The count `generation._whole_figures` reads off the ladder, asked of
    a VALUE instead of a whole number of its last place: 0.5 and -0.5
    both have the one figure their plain spelling writes before the
    mark, and 1000000 has seven.

    Guarantees: accepts any finite number; returns 1 or more.
    Determinism: a fixed function of the value. Raises nothing for a
    finite number. No I/O of any kind.
    """
    size = value
    if size < 0.0:
        size = 0.0 - size
    return len(str(int(size)))


def population_mean_of(numbers: list[float]) -> float:
    """The arithmetic mean of ``numbers``, exactly rounded.

    PUBLIC because the generator measures its own pool against the
    published one with it (method G12.12), and a second copy of this
    arithmetic in that module would be a second answer to one question.

    IT USED TO RETURN A SPREAD BESIDE THE MEAN, and the owner's decision
    of 2026-09-21 withdrew the pooled spread from what is published, so
    nothing asks for one any more. What a pool publishes now is a count
    and a mean, and this is the mean.

    The arithmetic is the module's one rule -- every value written as a
    whole number of one shared power of two, summed exactly, and rounded
    to binary64 once at the end -- so the answer depends on the multiset
    and not on the order the rows arrived in.

    Guarantees: accepts at least one finite number; returns the
    correctly rounded binary64 value of its exact mean. Determinism: a
    fixed function of the multiset. Raises nothing for a non-empty
    list. No I/O of any kind.
    """
    count = len(numbers)
    total, _squares, _cubes, _fourths, base = _totals(numbers)
    top, bottom = _over_two(total, count, base)
    return _rounded_ratio(top, bottom)


# HOW WIDE METHOD G12.12'S WINDOW ON THE POOLED MEAN IS, counted in
# PLACES OF THE COLUMN'S OWN GRID. It is MEASURED rather than chosen.
# Method G8.3c step 4 makes the groups carry each other's arrears, so
# every group but the last is asked for whatever the cells still to be
# written must average for the pool to come out on the published mean,
# and the only error left over is the LAST group's own rounding onto a
# place the column writes at. Over 371 pools that publish a scale and
# whose twin publishes one back -- the shape ledger K-2B-50 names, its
# loose cousin, a decimal pool, an unanchored pool of readings, the ten
# shapes of the landing's own before-and-after table, and four draws of
# 150 randomised pools at four widths, two grids and both signs -- the
# furthest a conforming twin's own pooled mean stood from the published
# one was A THIRD OF ONE PLACE. The window is TWO places, six times the
# worst measured.
#
# WHY PLACES AND NOT A SHARE OF ANYTHING. A window that was a share of
# some magnitude on the page was a window drawn from a number that has
# nothing to do with the pool: measured on 100 `alpha`, twenty `990`
# and ten each of 940 to 949 at a floor of eleven, the column's own
# published `990` set a window of 198.0 around a pooled mean of 944.5,
# and the very defect ledger K-2B-50 names -- G8.3c's placement
# withdrawn, the twin's pool back at 990.0 -- passed inside it. What
# the placement can and cannot do is a fact about the GRID, so that is
# what the window is counted in, and the same defect now stands at
# forty-five and a half places of a window two places wide.
_POOLED_WINDOW_PLACES = 2


def _published_places(labels: "list[str]") -> int:
    """The FEWEST decimal places any published number of a column has.

    The coarsest grid the ladder of method G8.3a can reach, which is
    the coarsest any pooled placement can be rounded onto: the ladder's
    tiers are the counts of places the published numbers were written
    with, and a placement walks them finest first and whole numbers
    last. A column that publishes no number at all is read as whole
    numbers here, which is both the coarsest grid there is and the one
    an unanchored ladder ends on.

    A DECIMAL MARK THIS READS AS A GROUPING MARK ANSWERS NOUGHT, and
    that is the safe direction: a column whose own mark is a comma has
    `4,5` read here as a whole number, so the grid is taken to be
    coarser than it is and the window wider than it needs to be. A
    window read too NARROW would call a sound twin missed.

    Guarantees: accepts the published labels; returns nought or more.
    Determinism: a fixed function of the labels. Raises nothing. No I/O
    of any kind.
    """
    fewest = -1
    for label in labels:
        body = parsing.trimmed(label)
        if parsing.classify_number(body) != parsing.NUMBER:
            continue
        places = 0
        marks = 0
        for step in range(len(body)):
            if body[step] == ".":
                marks = marks + 1
                places = 0
            elif marks > 0:
                places = places + 1
        if marks != 1:
            places = 0
        if fewest < 0 or places < fewest:
            fewest = places
    if fewest < 0:
        return 0
    return fewest


def pooled_window(labels: "list[str]") -> float:
    """Half the window method G12.12 draws around the published pooled mean.

    PUBLIC because two modules draw it and neither may import the other:
    the generator's own report, which measures the twin it has just
    written, and the validator, which measures a file it was handed.
    One arithmetic, one answer.

    THE WINDOW USED TO BE DRAWN FROM THE POOL'S PUBLISHED SPREAD -- half
    of it either side of each aggregate -- and the owner's decision of
    2026-09-21 withdrew that spread. It was drawn next from the largest
    magnitude the column's description states, which was worse than
    nothing: on a column of 100 `alpha`, twenty `990` and ten each of
    940 to 949 the published `990` set a window of 198.0 around a pooled
    mean of 944.5, and the defect ledger K-2B-50 names passed inside it.

    IT IS DRAWN FROM THE GRID, because the grid is what decides how
    exactly a placement can meet a mean. Method G8.3c step 4 asks every
    group but the last for what the cells still to be written must
    average for the pool to come out on ``mu``, so the arrears of a
    group the census pushed elsewhere are carried by the groups after
    it and the only error left is the last group's rounding onto a
    place the column writes at. `_POOLED_WINDOW_PLACES` carries the
    measurement of how far that reaches.

    A COLUMN THAT PUBLISHES NO NUMBER is read as whole numbers, which
    is the coarsest grid there is and so the widest this window ever
    becomes. It is never nought, so no file meets a window of no width.

    Guarantees: accepts the published labels; returns a half-window
    above nought. Determinism: a fixed function of them. Raises
    nothing. No I/O of any kind.
    """
    places = _published_places(labels)
    unit = 1.0
    if places > 0:
        unit = 1.0 / float(10 ** places)
    return unit * float(_POOLED_WINDOW_PLACES)


def _pooled_numbers(
    counts: dict[str, int],
    spellings_by_folded: dict[str, dict[str, int]],
    settings: Settings,
) -> "dict[str, object]":
    """The scale of the numbers the floor held back (plan P4-D302).

    THE DEFECT THIS CLOSES (ledger K-2B-50). A column of 100 `alpha`,
    twenty `100` and ten each of 200 to 209 at a floor of eleven
    publishes one numeric level, `100`, and pools the ten others. The
    generator then has one number to place the made-up ones beside, so
    it writes 95 to 105 and the numeric population's mean falls from
    187.083333 to 100 -- while both files validate with nothing missed,
    because no published fact speaks of the pool's scale at all.

    WHAT IS PUBLISHED IS TWO NUMBERS ABOUT A GROUP and no third: how
    many cells of the held-back levels read as numbers, and their mean.
    No level is named, no count of any one level is given, and no cell
    is placed.

    THE SPREAD IS NOT PUBLISHED, by the owner's decision of 2026-09-21,
    and that decision is the whole shape of this function. A mean and a
    spread are TWO equations over the pool's values, and two equations
    over a pool packed as closely as its own grid allows leave one
    answer: the landing this repairs published a spread of
    2.8722813232690143 for the shape above, which is exactly the
    smallest a pool of ten distinct whole numbers can have, so its ten
    held-back values came back as 200 to 209 by arithmetic. A mean
    alone is ONE equation, and one equation over as many unknowns as the
    pool has different values is never solved that way.

    AND ONE PRODUCER OBLIGATION, measured, which the loader cannot
    re-ask (contract 6.3.3).

    THE PUBLISHED MEAN MUST LEAVE THE VALUES ROOM TO MOVE.
    `_arrangements` counts how many sets of different numbers the mean,
    the cell count, the pool's own grid and the column's width leave,
    and `_POOLED_SCALE_ROOM` is the bound. That ONE rule replaces the
    three the published spread needed -- a level count of six, a pool of
    no spread, and a pool at the tightest arrangement its values could
    take -- and each of those three is a case of it:

    * a pool holding ONE different number is named by its mean outright,
      whatever spellings it wears, and the count of its arrangements is
      one;
    * a pool at the tightest arrangement is not named by a mean at all,
      and the count says so -- 189 arrangements against a loose pool's
      224 at two levels, 45,757 against 47,502 at three;
    * and a pool of six one-figure numbers, which every one of the three
      old rules published, is named to within sixteen answers, because
      six different one-figure numbers are six of the ten there are.

    THE FOURTH OLD RULE GOES THE SAME WAY, AND IT IS A PROOF AND NOT A
    MEASUREMENT. The landing this replaces refused a pool WIDER than the
    widest number the column shows, because method G8.3a step 3 forbids
    the generator a made-up number wider than that and a scale it may
    not write states an obligation no file could meet. What the
    generator must now meet is the MEAN, and a mean outside that width
    is refused here already: every arrangement's values lie on the grid
    inside it, so their sum cannot reach `k` times a mean beyond it and
    `_arrangements` answers nought. What the width rule still refused
    was a pool holding ONE wide value beside small ones -- 1, 5 and
    2089 beside a three-figure column -- whose mean is 698.33 and well
    within what a twin may write. Measured over 200,000 random pools at
    four widths: not one has a mean the twin could not write and enough
    room to publish, while 2,915 were refused by the width rule with a
    mean the twin can write exactly. It bought nothing and cost those,
    so it is withdrawn.

    THE DISCLOSURE RULE IS ASKED AND NOT ASSERTED. `parsing.
    census_nameable` is asked with the pooled count as the one count it
    would print and the column's numeric cells as the population a
    reader can subtract it from, at the settings floor -- so the pool
    reaches `parsing.census_floor`, and so does what is left of the
    numeric cells once it is taken off. A pool of one numeric cell
    would BE that cell's value under the name `mean`, and the rule
    refuses it; so does a pool that leaves one published numeric cell
    behind, because that cell's own value is then recoverable.

    WHERE ANY RULE REFUSES, `_NO_POOLED_SCALE` stands, which is what a
    column with no held-back numbers publishes too.

    Guarantees: accepts the folded counts, the spellings of each folded
    value and the settings; returns a mapping of exactly `n_cells` and
    `mean`, whose mean is None exactly where the count is nought.
    Determinism: a fixed function of the three. Raises nothing. No I/O
    of any kind.
    """
    pooled: list[float] = []
    numeric = 0
    shown = 0
    negative = False
    for label in sorted(counts):
        spellings = spellings_by_folded[label]
        held = counts[label] < settings.small_cell_floor
        for spelling in sorted(spellings):
            if parsing.classify_number(spelling) != parsing.NUMBER:
                continue
            size = parsing.parse_number(spelling)
            if size is None or not math.isfinite(size):
                continue
            numeric = numeric + spellings[spelling]
            if size < 0.0:
                negative = True
            if not held:
                continue
            for _each in range(spellings[spelling]):
                pooled += [size]
        if held:
            continue
        # THE WIDEST NUMBER THIS COLUMN WILL SHOW, read off the spellings
        # `_levels` will NAME and no others: a spelling the variants
        # census holds back is counted into its level's commonest
        # (ruling 6) and never printed, so it is no evidence to a reader
        # and no rung to the generator.
        wrote, _withheld = _variants(
            _absorb_lone_spellings(spellings, settings), settings
        )
        for spelling in sorted(wrote):
            if parsing.classify_number(spelling) != parsing.NUMBER:
                continue
            size = parsing.parse_number(spelling)
            if size is None or not math.isfinite(size):
                continue
            figures = _whole_figures_of(size)
            if figures > shown:
                shown = figures
    if not pooled:
        return dict(_NO_POOLED_SCALE)
    if not parsing.census_nameable(
        [len(pooled)], [numeric], settings.small_cell_floor
    ):
        return dict(_NO_POOLED_SCALE)
    # THE ROOM THE PUBLISHED MEAN LEAVES THE VALUES, counted rather than
    # argued. The grid is the closest two of the pool's own values
    # stand, which is the coarsest grid this module can read off them
    # and so the fewest arrangements: a finer grid only ever gives a
    # reader more answers, so taking the coarse one refuses more often
    # and never less. The range is what the column's width and its sign
    # census allow, for the same reason -- a reader who knows no cell of
    # this column is negative does not search below nought.
    different = sorted(set(pooled))
    step = _closest_step(pooled)
    if len(different) < 2 or step <= 0.0:
        return dict(_NO_POOLED_SCALE)
    bounded = shown > 0
    low = 0.0
    points = 0
    if bounded:
        highest = float(10 ** shown) - step
        if negative:
            low = step - float(10 ** shown)
        points = int(round((highest - low) / step)) + 1
    elif negative:
        # NO WIDTH BOUNDS THE VALUES AND THE COLUMN HOLDS A NEGATIVE, so
        # the range runs away in both directions. The count is taken
        # over the stretch the walk could reach anyway, which is a
        # smaller question than the reader's and so a floor on its
        # answer.
        low = different[0] - float(_POOLED_SCALE_COUNTED) * step
    owed = len(different) * (len(different) - 1) // 2
    spent = 0
    for size in different:
        spent = spent + int(round((size - low) / step))
    room = _arrangements(len(different), points, spent - owed, bounded)
    if room < _POOLED_SCALE_ROOM:
        return dict(_NO_POOLED_SCALE)
    return {
        "n_cells": len(pooled),
        "mean": published(population_mean_of(pooled)),
    }


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

    **And `shape_form_cells`**, how many of the level's cells were
    written in the label's own form (plan amendment A-P4-47).
    `shape_form_cells` above states the rule and what it does and does
    not disclose; it is what lets the twin give a level's made-up
    spellings the shape the source's held-back spellings actually
    wore, which the column-wide `shape_forms` census cannot say.

    THE HELD-BACK LABELS ARE PUBLISHED AS A POOL, and only as a pool
    (owner ruling of 2026-09-17, item 2, option A; plan P4-D201): how
    many there were and how many rows they covered together. Their sizes
    one by one stood here as `suppressed_counts` since review item
    P1-R1-F9, so that a column split 1/9 and one split 5/5 serialised
    apart; the ruling gives that up, and a twin writes its invented
    labels at sizes a fixed rule reads off the pool.

    A POOL OF ONE ROW NEVER REACHES THIS FUNCTION (the owner's ruling of
    2026-09-17, item 5; plan P4-D231, loader invariant B4b). A pool of
    one level on one row IS a count of one, and `n_present` less the published counts reads it
    whether or not it is printed, so no key this function leaves out can
    hide it. Two remedies were tried and only the second is the owner's.
    The first writing of P4-D201 held the smallest PUBLISHED label back
    beside such a pool, and the repair pass of 2026-09-17 withdrew it,
    because the label it held back had cleared the floor and the twin
    then wrote none of it -- measured: 400 `north`, 15 `south` and one
    `west` at a floor of eleven gave `south` 0 twin rows against 15, and
    a lab column's `>1000` on 11 rows 0 against 11. The ruling of item 5
    takes the other way out: where the pool would be one level on one
    row, the cells of it are counted as missing before this function is
    reached (`_levels_read_by_subtraction`, the level pass of
    `profile_column`), so no label that clears the floor is ever held
    back, and no pool that arrives here is a count of one. What a pool
    of one level over MORE than one row still gives away is a limit plan
    P4-D231 measures and puts to the owner.

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
    for label in ordered:
        count = counts[label]
        if count >= settings.small_cell_floor:
            # COUNTED FIRST, SO BOTH KEYS SPEAK OF THE SAME SPELLINGS
            # (plan P4-D240): a one-row spelling is counted into the
            # level's commonest before either the variants census or the
            # form count is taken off it, or the form count would count a
            # cell the variants census has already respelled.
            written = _absorb_lone_spellings(
                spellings_by_folded[label], settings
            )
            named, withheld = _variants(written, settings)
            entries += [
                {
                    "label": label,
                    "count": count,
                    "variants": named,
                    "variants_withheld": withheld,
                    # ...AND HOW MANY OF ITS CELLS WORE ITS OWN WRITTEN
                    # FORM (plan amendment A-P4-47). Written on every
                    # published level of every label role, including
                    # the ones whose label has no form and whose answer
                    # is therefore 0: this format has no optional keys,
                    # and a key that appears only where the answer is
                    # interesting is a key whose ABSENCE speaks.
                    "shape_form_cells": shape_form_cells(written),
                }
            ]
        else:
            suppressed_levels = suppressed_levels + 1
            suppressed_rows = suppressed_rows + count
    return _Levels(
        published=entries,
        suppressed_levels=suppressed_levels,
        suppressed_rows=suppressed_rows,
        pooled_numbers=_pooled_numbers(counts, spellings_by_folded, settings),
    )


# THE LABEL ROLES WHOSE LEVELS ARE COUNTED OVER THE WHOLE COLUMN. The
# fifth, `numbers_with_labels`, counts its levels over its label half
# alone and is handled beside them.
_LEVEL_ROLES = (
    ROLE_BINARY,
    ROLE_CATEGORICAL,
    ROLE_CONSTANT,
    ROLE_LONG_TAIL,
)


# THE FOUR TOTALS A READER HOLDS BESIDE ANY COLUMN'S LEVELS, in the
# order the block prints them (contract 6.2, U-family): what each present
# cell READS AS. Every present cell answers exactly one of them, and the
# four come to `n_present`, so a reader subtracts the published levels of
# one class from its own total and is left with the rows that class holds
# back (plan P4-D261).
_READING_CLASSES = (
    parsing.NUMBER,
    parsing.NOT_A_NUMBER,
    parsing.NUMBER_OUT_OF_RANGE,
    parsing.NUMBER_CONTRADICTORY,
)

# The stand-in for a folded identity whose cells do not all read the same
# way. It belongs to no published total, so no reader can subtract it,
# and it is never counted out by the class pass. It holds a space, which
# no cell kind holds, so it can be mistaken for none of them.
_CLASS_MIXED = "two readings"


def _a_level_is_below_the_floor(cells: _Cells) -> bool:
    """Whether any folded value of this column covers fewer rows than the floor.

    The cheap gate in front of the level pass (plan P4-D231): no level
    below the floor means no pool at all, and at the default floor of
    one there can be no such level, so the pass costs nothing on the
    files that do not need it and the trial reading below is never run.

    Guarantees: accepts the tally; returns a bool. Determinism: a fixed
    function of the tally and its settings. Raises nothing. No I/O.
    """
    floor = cells.settings.small_cell_floor
    if floor <= 1:
        return False
    counts = cells.folded_counts
    for label in sorted(counts):
        if counts[label] < floor:
            return True
    return False


def _levels_read_by_subtraction(
    cells: _Cells, role: str
) -> "tuple[str, ...]":
    """The folded levels whose rows a reader could count by subtraction.

    THE OWNER'S RULING OF 2026-09-17, ITEM 5 (plan P4-D231). A label
    column publishes its levels at or above the floor and pools the
    rest, as a count of levels and a count of rows and no size of any
    one of them. Where the rows come to fewer than TWICE the levels a
    count of one is FORCED -- every held-back level covers at least one
    row -- and `n_present` less the published counts reads it whether or
    not a key prints it: 480 `F`, 519 `M` and one `U` at a floor of
    eleven published 999 of 1,000 present cells and told every reader
    that one row holds a third value, and three one-patient sites among
    2,000 rows published three levels over three rows, which can only be
    one and one and one (plan P4-D239). This answers which levels those
    are, and the caller counts every cell of them as MISSING, so the
    description is that of the table with those cells blank.

    THE QUESTION IS `parsing.pool_names_a_level`, which states the rule
    once and states the two wider readings that were measured and left
    to the owner. It is asked over the levels of the population the list
    is counted over: the whole column for the four roles that publish a
    level list, and the LABEL HALF alone for `numbers_with_labels`,
    whose own `n_present` is the cells of that half.

    NO LABEL THAT CLEARS THE FLOOR IS EVER HELD BACK TO HIDE ONE. The
    first writing of P4-D201 did exactly that and the twin then wrote
    none of a published label; this answers only levels the floor
    already refuses to name, so every label the floor publishes is
    published and written.

    Guarantees:

    - Inputs: the tally of the column's present cells, and the role the
      reading before this pass gave it.
    - Determinism: a fixed function of the two; the answer is in sorted
      order.
    - Errors raised: none.
    - Boundary: answers nothing at all for a role that publishes no
      level list, for a column whose every level clears the floor, and
      for any pool whose rows reach twice its levels and which is not
      one row per level below the published rows -- a long tail of
      hundreds of held-back levels covering more rows than the published
      labels do is untouched, and so is one level over five rows, which
      plan P4-D231 puts to the owner as the limit it is. No file is
      opened.
    """
    settings = cells.settings
    floor = settings.small_cell_floor
    counts = cells.folded_counts
    if role == ROLE_COMPOUND:
        compound = _compound_reading(cells)
        if compound is None:
            return ()
        halved: "dict[str, int]" = {}
        for cell in compound.labels:
            key = cell.folded
            halved[key] = (halved[key] if key in halved else 0) + 1
        counts = halved
    elif role not in _LEVEL_ROLES:
        return ()
    rare: "list[str]" = []
    pooled = 0
    published = 0
    smallest = 0
    for label in sorted(counts):
        if counts[label] < floor:
            rare += [label]
            pooled = pooled + counts[label]
            continue
        # BOTH HALVES OF THE RULING ARE ASKED, and each wants a
        # different figure off this one walk. The pool's own question is
        # asked against the rows the PUBLISHED levels cover (plan
        # P4-D290), which is the widened reading; the per-class question
        # below is asked beside the smallest count the column publishes
        # (plan P4-D261). One walk, so the two cannot part.
        published = published + counts[label]
        if not smallest or counts[label] < smallest:
            smallest = counts[label]
    if parsing.pool_names_a_level(len(rare), pooled, published):
        return tuple(rare)
    # BOTH SIBLING READINGS, AND THE ANSWER IS THEIR UNION (round 2 of
    # the review, the disclosure pass, item 3). The four reading classes
    # are one family of totals a reader subtracts the published levels
    # from; the FORM census is another, published beside the very level
    # entries whose `shape_form_cells` do the subtracting. A level the
    # first pass leaves alone can be named outright by the second, so
    # both are asked and every label either names is counted out.
    counted_out: "dict[str, int]" = {}
    for label in _levels_read_by_class(cells, role, rare, smallest):
        counted_out[label] = 1
    for label in _levels_read_by_form(cells, role, rare):
        counted_out[label] = 1
    return tuple(sorted(counted_out))


def _levels_read_by_class(
    cells: _Cells, role: str, rare: "list[str]", smallest: int
) -> "tuple[str, ...]":
    """The same ruling asked of each SIBLING TOTAL, not of the pool alone.

    THE OWNER'S RULING OF 2026-09-17, ITEM 5, OVER A SUBDIVISION OF THE
    POOL (Codex blocker 2 of the extra round, 2026-09-18; plan P4-D261).
    Every column publishes four totals saying what its present cells
    READ AS -- `n_numeric`, `n_not_numeric`, `n_out_of_range` and
    `n_contradictory` -- and a reader subtracts from each of them the
    published levels that read that way. The whole pool can be far too
    large to force a count of one while ONE of those four differences is
    a count of one on its own.

    MEASURED before this pass: `alpha` and `beta` a hundred rows each,
    `1` five rows, `2` six rows and `gamma` one row, at a floor of
    eleven. The block published `n_not_numeric` 201 with both named
    words at 100, so 201 less 200 is one: the withheld WORD level occurs
    once, although the pool itself was three levels over twelve rows and
    every printed count cleared the floor. The twin wrote one `group-1`,
    and both files passed every executable check.

    THE QUESTION IS `parsing.census_names_one_row`, asked of the class's
    own POOL and of the pair together, which is the rule the form and
    layout censuses already ask of their own sibling totals and the rule
    the LOADER asks here (invariant B4c). It is asked at that width and
    no wider, so the producer and the loader cannot part.

    THE CLASS NO PUBLISHED LEVEL COUNTS INTO IS READ TOO, and this
    paragraph said the opposite until the skeptic measured it on
    2026-09-18. The pair alone answers nothing where the census covers
    none of the total -- an absent census leaves a reader nothing to
    subtract -- and a class whose every level the floor held back is
    exactly that shape. MEASURED: `alpha` and `beta` a hundred rows each,
    `gamma` six, `delta` five, and ONE further cell at a floor of eleven.
    With that cell `77` the block published `n_numeric` 1 beside two
    published WORDS, so exactly one row of the column reads as a number
    and its value is withheld; with `1e999` the same of `n_out_of_range`
    and with `(+5)` of `n_contradictory`, which names the accounting
    notation ONE individual's cell was written in. All three passed
    every executable check and the twin wrote the row. So the class's
    held-back rows are handed in as a POOL as well: a pool of one is the
    one rule's first reading, and it does not need a census beside it.

    THE WIDER READING IS REFUSED BY MEASUREMENT AND NOT BY PREFERENCE.
    `parsing.pool_names_a_level`'s whole forced band -- a class whose
    rows come to fewer than twice its held-back levels -- is the natural
    generalisation, and it breaks the twin. The generator spends a
    pooled class over the group sizes G8.3 reads off the pool, which are
    not the source's: 25 out-of-range cells over eight source levels
    beside 9 words over four, at a floor of eleven, come back as six
    groups and six, and the TWIN's own description then falls in the
    band although the source's does not. Counting those cells out of the
    twin's description left it missing eight of its own obligations --
    `n_present`, `n_missing`, `n_not_numeric`, both distinct counts, both
    held-back counts and a published form -- on a file that passed
    before. The band belongs with the two readings plan P4-D231 already
    puts to the owner, and it waits on the generator spending a pooled
    class in sizes its own description cannot read a one out of.

    Guarantees:

    - Inputs: the tally, the role the reading before this pass gave it,
      the levels the floor holds back, and the smallest count the column
      publishes beside them (unused here, and taken so the two halves of
      the ruling have one signature).
    - Determinism: a fixed function of those; the answer is in sorted
      order.
    - Errors raised: none.
    - Boundary: answers nothing where the floor holds nothing back, and
      nothing for a class whose held-back rows are none, or more than
      one, or which no published level of the column counts into. A
      level whose cells do not all read the same way belongs to no class
      and is never counted out by this pass. No file is opened.
    """
    if not rare or smallest < 0:
        return ()
    population = cells.classified
    if role == ROLE_COMPOUND:
        compound = _compound_reading(cells)
        if compound is None:
            return ()
        population = compound.labels
    by_class: "dict[str, str]" = {}
    counts: "dict[str, int]" = {}
    totals: "dict[str, int]" = {}
    for cell in population:
        key = cell.folded
        counts[key] = (counts[key] if key in counts else 0) + 1
        totals[cell.kind] = (
            totals[cell.kind] if cell.kind in totals else 0
        ) + 1
        if key in by_class and by_class[key] != cell.kind:
            by_class[key] = _CLASS_MIXED
            continue
        by_class[key] = cell.kind
    held: "dict[str, list[str]]" = {}
    for label in rare:
        if label not in by_class:
            continue
        reading = by_class[label]
        held[reading] = (held[reading] if reading in held else []) + [label]
    counted_out: "list[str]" = []
    for reading in _READING_CLASSES:
        if reading not in held:
            continue
        total = totals[reading] if reading in totals else 0
        rows = 0
        for label in held[reading]:
            rows = rows + counts[label]
        covered = total - rows
        # THE CLASS'S OWN HELD-BACK ROWS ARE A POOL, and the one rule
        # refuses a pool of one exactly as it refuses a printed count of
        # one. Handing `rows` in as that pool is what reaches the class
        # NO PUBLISHED LEVEL COUNTS INTO, where `covered` is nought and
        # the pair alone says nothing (the skeptic's blocker of
        # 2026-09-18; plan P4-D261). Both readings are the one rule's,
        # asked in one call, so this is not a second copy of it.
        if parsing.census_names_one_row(
            {reading: rows}, [(total, covered)]
        ) != -1:
            counted_out += held[reading]
    return tuple(sorted(counted_out))


def _census_key_of(value: str, census: "dict[str, int]") -> str:
    """The key ONE cell was counted under in a form census, or the empty text.

    THE CASE RULE, READ BACK (round 2 of the review, the disclosure
    pass, item 3). `_lower_case_split` names a form under two keys
    where its lower-case cells reach the line and the rest do too, and
    under the lower-case key alone where the rest fall below it; below
    the line the form is named blind to case, and below the floor or
    the room rule it is not named at all. So a cell's key is not
    `parsing.shape_form` of it: a walk that assumed so would count a
    split form's cells under a key the census does not carry, and read
    a difference of one where there is none.

    The empty text means the census says nothing about this cell --
    it has no form, or its form was pooled.

    Guarantees: accepts one cell as the description speaks of it and
    the census the block publishes; returns a key of that census or the
    empty text. Determinism: a fixed function of the two. Raises
    nothing. No I/O of any kind.
    """
    form = parsing.shape_form(value)
    if not form:
        return ""
    lowered = parsing.lower_case_form(form)
    if lowered and lowered in census:
        if form not in census or parsing.is_lower_case_text(value):
            return lowered
    if form in census:
        return form
    return ""


def _levels_read_by_form(
    cells: _Cells, role: str, rare: "list[str]"
) -> "tuple[str, ...]":
    """The same ruling asked of the FORM census, which levels subtract from.

    THE OWNER'S RULING OF 2026-09-17, ITEM 5, OVER THE CENSUS PUBLISHED
    BESIDE THE LEVELS (round 2 of the review, the disclosure pass, item
    3). `_levels_read_by_class` next door weighs the published levels
    against the four totals saying what the column's cells READ AS. It
    is not the only family of totals a reader can subtract them from:
    every level entry carries `shape_form_cells`, how many of that
    level's cells were written in a form, and the block publishes a
    column-wide `shape_forms` census beside them. Those two are about
    THE SAME CELLS, so the census less the published levels' own
    contributions is the cells of the held-back levels wearing that
    form -- and where that difference is one, a held-back level is one
    row and its FORM is published.

    **Measured** at a floor of eleven and seed 4, on one column holding
    `ABC-100` a hundred times, `ABC-200` a hundred times, `ABC-300`
    once, `QQ-400` five times and `RR-500` six times. The block
    published both common levels at `shape_form_cells` 100 beside
    `shape_forms {"@@@-%%%": 201, "@@-%%%": 11}`, and 201 less 100 less
    100 is one: one held-back level covers one row and wears three
    letters, a hyphen and three figures. `n_missing` was nought, the
    twin wrote one `AAA-000`, and BOTH files validated at nought with
    47 held back and nothing missed -- every executable check passed
    over a description that named an individual's form. The second key
    is untouched by this pass and must be: its eleven cells belong to
    two held-back levels, no published level wears that form, so the
    census covers none of any total a reader holds and the pool is
    doing exactly what the ruling asks of it.

    THE QUESTION IS `parsing.census_names_one_row`, over the held-back
    rows of each named form as a POOL and over the pair `(census,
    published cells)` together -- the same call, at the same width, as
    the class pass beside it and as the loader's own check. The census
    is the one the block will publish, built by `_shape_forms` from the
    respelling `described_spellings` gives, so a form key this pass
    reads is a form key the description carries: a form the census
    pooled is not named, is not read here, and stays pooled.

    Guarantees:

    - Inputs: the tally, the role the reading before this pass gave it,
      and the levels the floor holds back.
    - Determinism: a fixed function of the three; the answer is in
      sorted order.
    - Errors raised: none.
    - Boundary: answers nothing where the floor holds nothing back, for
      a role that publishes no level list, for a cell with no form at
      all -- which this census counts nowhere -- and for any form whose
      held-back cells are none or more than one. No file is opened.
    """
    if not rare:
        return ()
    population = cells
    with_text_total = True
    if role == ROLE_COMPOUND:
        compound = _compound_reading(cells)
        if compound is None:
            return ()
        # THE LABEL HALF, TALLIED THE WAY THE BLOCK TALLIES IT, so this
        # pass reads the census `_level_details` will publish for that
        # half and not a second census of its own.
        population = _tally(
            _classify_all(
                [cell.text for cell in compound.labels], cells.decimal_comma
            ),
            len(compound.labels),
            cells.settings,
            cells.decimal_comma,
        )
        with_text_total = False
    elif role not in _LEVEL_ROLES:
        return ()
    spelled = described_spellings(population.present, population.settings)
    census = _shape_forms(population, False, with_text_total, spelled)
    held: "dict[str, list[str]]" = {}
    rows: "dict[str, int]" = {}
    covered: "dict[str, int]" = {}
    for value in spelled:
        form = _census_key_of(value, census)
        if not form:
            continue
        key = parsing.folded(value)
        if key not in rare:
            covered[form] = (covered[form] if form in covered else 0) + 1
            continue
        rows[form] = (rows[form] if form in rows else 0) + 1
        named = held[form] if form in held else []
        held[form] = named if key in named else named + [key]
    counted_out: "list[str]" = []
    for form in sorted(census):
        if form not in held:
            continue
        seen = covered[form] if form in covered else 0
        if parsing.census_names_one_row(
            {form: rows[form]}, [(census[form], seen)]
        ) != -1:
            counted_out += held[form]
    return tuple(sorted(counted_out))


@dataclasses.dataclass(frozen=True)
class _Compound:
    """The THREE populations of a `numbers_with_labels` column.

    `numbers` are the cells that read as an ordinary number, `unusable`
    the cells the number rules recognise as a numeral and this format
    cannot hold -- one too large, or one whose notation contradicts
    itself -- and `labels` everything else (residual R-P4-149, closed
    by the owner's ruling of 2026-09-04).

    THE THIRD POPULATION IS NOT A THIRD SUB-BLOCK. An unusable numeral
    is a NUMBER, so it belongs to the numeric half's population and is
    counted there the way a plain numeric column counts one: the half's
    `n_out_of_range` and `n_contradictory`. What the split does is stop
    calling it a word.
    """

    numbers: "list[_Cell]"
    unusable: "list[_Cell]"
    labels: "list[_Cell]"
    folded_counts: "dict[str, int]"


def _compound_reading(cells: "_Cells") -> "_Compound | None":
    """Numbers and labels in one cell space, or None -- rule 7b.

    Splits the present cells into the ones that read as ordinary
    numbers and the ones that are not numbers at all, and answers only
    where BOTH halves are what they need to be. The numbers must clear
    the detection line in CELLS and in different values, and hold more
    different values than a set of categories may. The words must be a
    VOCABULARY: more than nine tenths of the half's cells wearing a
    spelling that repeats, most of its identities repeating, and either
    a SMALL SET of them or one that clears the detection line -- either
    ground, not both. This paragraph said "at least one level that
    reaches it" until review round 8 of this landing (item 6), which
    is one of the two grounds and not the rule: a column of 295
    readings beside five `NOT DETECTED` is admitted by the other, and a
    maintainer following the sentence would have taken it away.

    A CELL THAT IS A NUMBER THE FORMAT CANNOT HOLD GOES WITH THE
    LABELS, and this paragraph said the opposite until review round 6
    of this landing (item 6). The first writing of the RULE refused the
    whole column on such a cell, on the ground that
    `numeric_unrepresentable` describes it properly -- and that role is
    decided by an earlier rule, so by the time this one runs it has
    already declined. Refusing here sent the column nowhere better: 280
    readings beside nineteen `POSITIVE` and ONE value too large for the
    format fell to the long tail, which describes none of the 280. So
    the rule changed and this sentence did not, which is a comment
    telling a maintainer the opposite of what the code beside it does.
    The comment below the signature has the whole reasoning; residual
    R-P4-149 carries the open question, which is whether such a cell
    should be described as a NUMBER rather than as a word.
    """
    # THE HALVES ARE "AN ORDINARY NUMBER" AND "EVERYTHING ELSE", and a
    # cell the format cannot hold goes with the everything else. An
    # earlier writing made such a cell REFUSE the whole rule, on the
    # ground that its column belongs to `numeric_unrepresentable` --
    # and that role is decided by an earlier rule, so by the time this
    # one runs it has already declined. Refusing here therefore did not
    # send the column anywhere better: 280 readings beside nineteen
    # `POSITIVE` and ONE value too large for the format fell through to
    # the long tail, which describes none of the 280. One stray cell
    # undid the whole role.
    numbers: "list[_Cell]" = []
    unusable: "list[_Cell]" = []
    labels: "list[_Cell]" = []
    for cell in cells.classified:
        if cell.kind == parsing.NUMBER:
            numbers += [cell]
        elif cell.kind in (
            parsing.NUMBER_OUT_OF_RANGE, parsing.NUMBER_CONTRADICTORY
        ):
            # A NUMERAL THIS FORMAT CANNOT HOLD IS STILL A NUMERAL
            # (residual R-P4-149, closed by the owner's ruling of
            # 2026-09-04). It used to join the labels, so a lab column
            # of 280 readings with one `9e999` published that cell as a
            # WORD beside `positive` and reported nought cells left out
            # of its statistics on a column that has one. Worse at a
            # raised floor: one such cell does not clear it, so the
            # spelling was suppressed and the cell came back as
            # `group-N` -- a fake word where the source had a number.
            unusable += [cell]
        else:
            labels += [cell]
    if not numbers or not labels:
        return None
    # AND THE NUMBERS MUST LOOK LIKE A QUANTITY RATHER THAN A CODE SET,
    # which is the question this rule forgot to ask about its own half.
    # `1`, `2`, `3` thirty times each beside five `unknown` is a coded
    # field: the digits are labels, and a mean of 2.0 over them is a
    # sentence about nothing. The suite holds that column and it is
    # right to -- the test is named "a small set of numeric codes is
    # still a set of categories".
    #
    # The line is the one already used on the other half: a numeric
    # population holding no more different values than a set of
    # categories may is a set of categories, whatever it is spelled
    # with. So this rule asks the text half to look like LABELS and the
    # numeric half to look like a QUANTITY, and declines when either
    # half is not what it needs to be.
    # The question is asked of the numeric half ON ITS OWN, over its own
    # cell count and not the column's rows. The ceiling is a share of
    # however many cells are being judged, so measuring a 3,000-cell
    # numeric half against a 6,000-row column's ceiling asks the wrong
    # question and called 400 different readings a code set.
    #
    # BY VALUE AND NOT BY SPELLING, which this counted wrongly at first
    # and which decides whether a coded field is read as a quantity.
    # Every cell already carries the exact number it denotes, and the
    # column's own distinctness is counted from those -- so a merge
    # that wrote `1` from one system and `1.0` from another holds SIX
    # different ECOG codes and not twelve. Counting the spellings made
    # the formatting decide the meaning: the same six codes crossed the
    # line into "quantity" and the twin would have published a mean of
    # a performance status.
    distinct_numbers: "dict[tuple[int, tuple[str, ...], int], int]" = {}
    for cell in numbers:
        if cell.exact is None:
            continue
        seen = 0
        if cell.exact in distinct_numbers:
            seen = distinct_numbers[cell.exact]
        distinct_numbers[cell.exact] = seen + 1
    settings = cells.settings
    # AND AN ABSOLUTE FLOOR BENEATH THE SHARE, because a share alone
    # says the same six codes are a QUANTITY in a fifty-row column and
    # a CODE SET in a hundred-row one -- the ceiling grows with the
    # column and the meaning does not. Six values are six values.
    #
    # The floor is the smallest group this project will publish at all.
    # A numeric population holding fewer different values than that is
    # a code set however many rows wear it: `0` to `5` is a performance
    # status, and a mean over it is a sentence about nothing. Above it,
    # the share decides as before.
    #
    # WHAT THIS CANNOT DO is tell a six-point CODE from a six-point
    # MEASUREMENT, and no count can -- the review that found this said
    # so. Where the two are indistinguishable this rule declines and
    # the column keeps the description it has today, which is the
    # honest answer; `--code` is how a person says which it is.
    # THE DETECTION LINE, AND IT IS THE FLOOR'S LINE AND NOT THE BARE
    # ELEVEN (review round 2 of this landing, item 1). This read
    # `settings.long_tail_minimum_level` -- the constant eleven -- so
    # raising the floor did not raise this bar, and the guarantee every
    # other rule of this taxonomy carries is that membership at ANY
    # floor is a subset of membership at eleven. Measured: at a floor
    # of twenty-five, eleven readings beside forty `POSITIVE` cells
    # took the role and published a mean, a spread and a percentile
    # rung over eleven cells -- to a person who had asked that nothing
    # about a group smaller than twenty-five be published.
    line = _long_tail_line(settings)
    # THE TWIN OF A COLUMN THAT SITS ON THIS LINE MAY NOT BE ONE, and
    # a margin is NOT the answer (review round 3 of this landing, item
    # 4, measured twice). The numeric machinery reaches about nine
    # tenths of a published count of different values on a hard column,
    # so a half holding exactly the line's worth writes fewer, and
    # re-describing the twin gives another role: over forty seeds, a
    # half on the line kept the role on 31 of 40 seeds at floors 1 and
    # 11 and on 13 of 40 at floor 25.
    #
    # A margin of a tenth was built and MEASURED and taken out again,
    # because it raises the bar the TWIN must clear as well: with it,
    # thirteen different numbers -- the first count that had been
    # stable at floor 1 -- kept the role on 27 of 40 seeds instead of
    # 40. Every margin does this, and each one costs real columns the
    # description they exist to get.
    #
    # So the line stands where the plan puts it and the limit is
    # NAMED instead: residual R-P4-151. The twin of such a column still
    # HOLDS its numbers -- what a re-description does not do is call it
    # the same kind of column, so `synthtwin validate` reports the
    # role's facts as withheld rather than held.
    if len(distinct_numbers) < line:
        return None
    # AND THE HALF ITSELF MUST CLEAR THE LINE, not only its count of
    # different values. The two are the same number on a column whose
    # readings never repeat and far apart on one whose readings do, and
    # the plan states this rule over the CELLS: a numeric half smaller
    # than the smallest publishable group is a group this description
    # may not describe.
    if len(numbers) < line:
        return None
    share = _at_most(settings.categorical_share, len(numbers))
    ceiling = min(settings.categorical_ceiling, share)
    if len(distinct_numbers) <= max(ceiling, settings.categorical_floor):
        return None
    folded_counts: "dict[str, int]" = {}
    for cell in labels:
        seen = 0
        if cell.folded in folded_counts:
            seen = folded_counts[cell.folded]
        folded_counts[cell.folded] = seen + 1
    # THE TEXT HALF IS JUDGED BY HOW MANY DIFFERENT WORDS IT HOLDS, NOT
    # BY HOW OFTEN THEY REPEAT, and the first writing of this rule had
    # it the other way about. It asked the words to clear the same
    # detection line the numbers clear -- one word shared by eleven
    # rows -- which reads plausibly and is backwards for the column
    # this role exists for. MEASURED on 300-row columns of readings
    # beside one marker: five markers and nine markers both declined
    # and their readings went on being described by nothing, while
    # eleven markers worked. A lab column is most often nearly all
    # numeric with a HANDFUL below the detection limit, so the rule
    # refused exactly the commonest shape.
    #
    # The words do not have to be publishable for the NUMBERS to
    # deserve describing. What matters is that the text half LOOKS LIKE
    # A COLUMN OF LABELS rather than prose -- and this project already
    # has two rules for that and no third is invented here. The text
    # half is label-shaped when EITHER:
    #
    #  - it holds no more different words than a set of categories may
    #    (the categorical ceiling), which is a handful of markers --
    #    one `NOT DETECTED`, or `POSITIVE` beside `NEGATIVE`; OR
    #  - at least one of its words is shared by enough rows to be
    #    published (the long-tail detection line), which is what a
    #    LARGE but repeating vocabulary looks like.
    #
    # THE SECOND DISJUNCT IS THE OWNER'S CORRECTION, and without it
    # this rule refused a real shape: a microbiology column naming
    # sixty organisms across three thousand cells has far more than the
    # ceiling's worth of different words and is not free text by any
    # reading -- every one of those names repeats scores of times. The
    # first writing of this rule had only the SECOND disjunct and
    # refused a handful of markers; the second had only the FIRST and
    # refused a large repeating vocabulary. Each was half of it.
    #
    # What falls outside both is prose: sixty notes in sixty cells, no
    # word repeated, nothing publishable. Those decline here and stay
    # free text exactly as today.
    #
    # AND A WORD THAT APPEARS ONCE IS A NOTE, NOT A LABEL. This is the
    # third correction to this rule and it came from the suite: a
    # policy test holds 98 numbers beside TWO all-different clinical
    # notes -- `seen clinic with nurse unchanged` -- and two is a small
    # set by any ceiling, so the rule above claimed the column and
    # would have published those two notes as levels. Publishing
    # somebody's free text verbatim is the thing the label roles exist
    # to avoid, and a note is not a marker however few there are. So
    # the text half must REPEAT somewhere: at least one of its words
    # covering more than one row. Five `NOT DETECTED` repeat; five
    # different notes do not.
    # AND THE WORDS THAT REPEAT MUST COVER MOST OF THE TEXT HALF, not
    # merely exist somewhere in it. Asking only that SOME word repeat
    # let one duplicated phrase carry arbitrary prose in with it: a
    # thousand rows holding 980 readings, TWO copies of `unable to
    # obtain` and eighteen different narrative results satisfied it,
    # and nineteen text values sit under a thousand-row column's
    # ceiling -- so the column read as compound and the label block
    # would have published those eighteen narratives verbatim. The
    # numeric mass was making the text half look like labels.
    #
    # MORE than half is the line, and the word above is "most":
    # `covered * 2 < len(labels)` refused fewer than half and admitted
    # EXACTLY half, which review round 1 of this landing showed is a
    # column of prose (item 4). Fifty numbers, `unable to obtain`
    # twice, and two different narratives -- the repeating identity
    # covers two of four text cells, the rule admitted it, and at a
    # floor of one both narratives would have been published verbatim
    # as levels.
    covered = 0
    singletons = 0
    for key in sorted(folded_counts):
        if folded_counts[key] > 1:
            covered = covered + folded_counts[key]
        else:
            singletons = singletons + 1
    # NINE TENTHS OF THE HALF'S CELLS, and "more than half" was not
    # enough (review round 2, item 4). Two hundred and ninety-six
    # readings, three `NOT DETECTED` and ONE narrative gives a half
    # whose repeating cells are three of four -- a clear majority --
    # and at a floor of one that narrative is published verbatim as a
    # level. Nine tenths refuses it and still admits the shape this
    # bar exists to protect: nineteen markers beside one MISSPELLED
    # marker is ninety-five hundredths, and a lab column is not to be
    # thrown to another role over one typing slip.
    # STRICTLY MORE than nine tenths, because the boundary itself
    # carries prose: two hundred readings beside ninety marker cells
    # and TEN different one-off notes is exactly nine tenths, and the
    # ten notes would each be published verbatim at a floor of one
    # (review round 3 of this landing, item 3). The typing-slip column
    # this bar protects is at ninety-five hundredths and is unaffected.
    if covered * 10 <= len(labels) * 9:
        return None
    # AND MOST OF THE HALF'S IDENTITIES MUST REPEAT, not merely most of
    # its cells. The cell test alone is carried by one big marker: a
    # thousand-row column holding a hundred `NOT DETECTED` and
    # ninety-nine different narratives has the marker covering more
    # than half the cells, one identity clearing the detection line,
    # and ninety-nine narratives that would each be published verbatim
    # at a floor of one. A vocabulary is a set of words that recur; a
    # set where most of the WORDS occur once is prose with a marker
    # mixed into it, and it stays free text.
    # AND MOST OF THE HALF'S IDENTITIES MUST REPEAT, which the cell
    # test above does not settle on a LARGE half: a thousand markers
    # beside ninety-nine different narratives is ninety-one hundredths
    # of the cells and still ninety-nine narratives. A MAJORITY of
    # singletons refuses; a tie does not, because the smallest half
    # with a stray -- one marker and one typo -- is a tie and is the
    # case the paragraph above admits on purpose.
    if singletons * 2 > len(folded_counts):
        return None
    # AND A TIE IS ADMITTED ONLY WHERE ITS REPEATING WORD IS ITSELF
    # PUBLISHABLE (review round 4 of this landing, item 4). The tie is
    # the smallest interesting half: one word that repeats and one that
    # occurs once. Whether admitting it publishes MORE of a person's
    # text than refusing it depends on what the column falls to, and
    # that turns on exactly this question:
    #
    # * 280 readings, nineteen `NOT DETECTED` and one stray -- the
    #   marker covers nineteen rows, clears the detection line, and
    #   REFUSING sends the column to `long_tail_labels`, which at a
    #   floor of one publishes 282 levels: the stray and all 280
    #   readings, each verbatim. Admitting publishes one.
    # * 289 readings, ten `NOT DETECTED` and one stray -- the marker
    #   covers ten rows, clears nothing, and refusing sends the column
    #   to `free_text`, which publishes no cell at all. Admitting
    #   publishes the stray for nothing.
    #
    # So the tie is admitted where a repeating word reaches the line
    # and refused where none does, which is the same question the rule
    # below asks for its OTHER branch and needs no new number.
    if (
        singletons * 2 == len(folded_counts)
        and _levels_covering(folded_counts, cells.settings) < 1
    ):
        return None
    a_small_set = len(folded_counts) <= _categorical_ceiling(cells)
    a_repeating_one = _levels_covering(folded_counts, cells.settings) >= 1
    if not a_small_set and not a_repeating_one:
        return None
    return _Compound(numbers, unusable, labels, folded_counts)


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


def _stand_in_level_remarks(levels: _Levels) -> "list[Note]":
    """One remark per built-in stand-in number published as a level.

    Contract NF37; plan P4-D4.7, withdrawn by amendment A-P4-30 item 1
    and built now under residual R-P4-24. The stand-in judgement runs
    only where a column's numbers reach the parse line, so a column of
    LABELS publishes `-999` as an ordinary level with an ordinary
    count, and nothing in the document told its owner that the same
    number one column over would have been read as a gap.

    IT ROUTES NOTHING. The role is already decided, the level is
    already published at its own count, and `--missing-value` is the
    person's to type or not. What the sentence adds is that they know
    the choice exists.

    THE MATCH IS BY NUMBER AND NOT BY SPELLING, which is the rule every
    other declaration in this module is matched under: `-999`,
    `-999.0` and `-999.00` are one number, and a column publishing any
    of them publishes the stand-in. Only levels that were PUBLISHED are
    looked at -- a level the floor held back is a level the remark may
    not describe, since the sentence says "one of the values this
    column publishes".

    Guarantees: accepts the published levels of one label column;
    returns a sentence for each built-in stand-in among them, in this
    package's own order, so a column publishing two of them is told
    about both. No spelling of the column reaches a sentence: each
    carries the candidate's PLACE in the built-in list and nothing
    else. Raises nothing. No I/O of any kind.
    """
    said: "list[Note]" = []
    labels = [
        entry["label"]
        for entry in levels.published
        if isinstance(entry["label"], str)
    ]
    exact = [exact_of_spelling(f"{label}") for label in labels]
    for place, candidate in enumerate(parsing.NUMERIC_SENTINELS, start=1):
        wanted = exact_of_number(candidate)
        for held in exact:
            if held is not None and held == wanted:
                said += [note(REMARK_LABEL_IS_A_STAND_IN, (place,))]
                break
    return said


def _level_details(
    levels: _Levels, cells: _Cells, with_text_total: bool = True
) -> dict[str, object]:
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
        # ...AND THE SCALE OF THE NUMBERS AMONG THEM (plan P4-D301,
        # ledger K-2B-50). Held back one by one, the pooled numeric
        # levels left the generator one published number to place its
        # made-up ones beside; three aggregates over the whole pool put
        # them back where the table had them. `_pooled_numbers` states
        # the rule and the disclosure question it asks.
        "suppressed_numbers": levels.pooled_numbers,
        # ...COUNTED OVER THE SPELLINGS THE LEVEL ENTRIES SPEAK OF (plan
        # P4-D275.1): a spelling the floor counted into its level's
        # commonest is counted there by this census too, or the column's
        # census and the level entries beside it describe two different
        # tables and no twin can meet both.
        "shape_forms": _shape_forms(
            cells,
            False,
            with_text_total,
            described_spellings(cells.present, cells.settings),
        ),
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
        "n_all_digits": _published_alphabets(cells)[1],
        "n_code_alphabet": _published_alphabets(cells)[0],
        # Both read from `_published_alphabets`, which is the one place
        # the disclosure rule is asked of them (plan P4-D277).
        # ...and the forms its cells were written in, which is what
        # lets a made-up cell look like one of them (plan P4-D18).
        "shape_forms": _shape_forms(cells, True),
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
    """How many cells of this column used each form, under the rule.

    Counted over the cells that read as a number this format can hold,
    and over no others: a cell too large to hold, or one whose notation
    contradicts itself, is written by a rule of its own and has forms
    this enumeration cannot express, so counting it here would promise
    something no twin could keep.

    THE DISCLOSURE RULE GOVERNS A FORM (plans P4-D221 and P4-D222; stage
    2 closed by the owner rulings of 2026-09-17), through
    `parsing.absorbed_census` with the six forms as a closed vocabulary.
    A form fewer cells than `parsing.census_floor` wrote -- two at a
    floor of one, the settings floor above it -- has no key of its own,
    and its cells are counted into the commonest named form, so no
    printed count and no count left by subtraction from the numeric
    count is one person, and the twin writes the column's own form:
    1,200 two-place prices with one padded, one exponent and one
    three-place cell publish `{"decimal": 1200}`. Where the map cannot
    speak it is one `(withheld)` pool, or the default form where a pool
    would say every form was written (`parsing.census_pools`). What the
    mapping publishes either way is a count of cells per form -- no
    value, no magnitude, no spelling.

    Guarantees: accepts a tally of one column; returns a mapping from
    form names, or `(withheld)` alone, to counts that sum to how many
    cells read as numbers this format can hold. Determinism: the answer
    depends only on the tally, and the keys are built in the
    enumeration's order. Raises nothing. No I/O of any kind.
    """
    counts = _form_tally(cells)
    total = 0
    for style in counts:
        total = total + counts[style]
    # THE DEFAULT FORM, where the six are too thinly shared to name one and
    # a pool would say every form was written (`parsing.census_pools`):
    # `plain` for a column whose every number is whole, `decimal` otherwise.
    default = parsing.STYLE_PLAIN
    for value in cells.numbers:
        if not math.isfinite(value) or int(value) != value:
            default = parsing.STYLE_DECIMAL
    census = parsing.absorbed_census(
        counts,
        total,
        cells.settings.small_cell_floor,
        len(NUMERIC_STYLES),
        default,
    )
    published_counts: dict[str, int] = {}
    for style in NUMERIC_STYLES:
        if style in census:
            published_counts[style] = census[style]
    if SUPPRESSED_LABEL in census:
        published_counts[SUPPRESSED_LABEL] = census[SUPPRESSED_LABEL]
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


def _fraction_widths(cells: _Cells, styles: "dict[str, int]") -> dict[str, int]:
    """How many `decimal`-styled cells wrote each width, under the rule.

    TWO COLUMNS OF THE SAME FORM ARE NOT THE SAME COLUMN.
    Eleven cells reading `1.00` and eleven reading `2.000` are both
    `decimal` under the styles map, which says only that twenty-two
    cells carried a point -- so a twin writing every one of them to one
    place carried the published styles map exactly while writing a
    column no reader of the real table would recognize. This census is
    what the styles map cannot say: not that a point was written, but
    how many figures followed it.

    THE DISCLOSURE RULE GOVERNS A WIDTH AS IT GOVERNS A FORM (plans
    P4-D221 and P4-D222; stage 2 closed by the owner rulings of
    2026-09-17), through `_absorbed_widths`: a width fewer cells than
    `parsing.census_floor` wrote is counted into the commonest width, so
    1,200 prices with one written to three places publish `{"2": 1200}`
    where they published `{"2": 1199, "3": 1}`. The census counts the
    `decimal` count the forms map publishes, so the cells of rarer forms
    that map counted as decimals are counted here at the commonest
    width; and a map that does not name `decimal` has no widths for it.

    THE KEYS ARE THE WIDTHS AS DECIMAL FIGURES, canonically: no leading
    zero, no sign, no padding, so `2` and never `02`. A key grammar
    left to be inferred is a key two producers spell differently and a
    consumer reads as two widths.

    Guarantees: accepts a tally of one column and its published forms
    map; returns a mapping from canonical width keys, or `(withheld)`
    alone, to counts that sum to the map's `decimal` count, or `{}`.
    Determinism: the answer depends only on the two, and the keys are
    built in ascending width order. Raises nothing. No I/O of any kind.
    """
    if parsing.STYLE_DECIMAL not in styles:
        return {}
    counts: dict[int, int] = {}
    for cell in cells.classified:
        if cell.kind != parsing.NUMBER:
            continue
        if numeric_style(cell.numeric_text) != parsing.STYLE_DECIMAL:
            continue
        _added_to(counts, fraction_width(cell.numeric_text), 1)
    census = parsing.absorbed_census(
        _width_keys(counts),
        styles[parsing.STYLE_DECIMAL],
        cells.settings.small_cell_floor,
        0,
    )
    # AN END THE WIDTHS CANNOT WRITE MAKES THE CENSUS ONE POOL (plan
    # P4-D222). The published minimum and maximum are exact, so their own
    # figures after the point are published already; where a rarer width
    # counted into the commonest is the one an end needs, a census naming
    # only narrower widths tells a twin to write every cell on a grid the
    # end is not on, and it wrote `2.1` for a published minimum of 2.11.
    # The pool says no width, as the census of a column whose widths were
    # all too rare to name does.
    widest = -1
    for key in census:
        if key != SUPPRESSED_LABEL:
            widest = max(widest, int(key))
    if widest >= 0 and cells.numbers:
        for end in (min(cells.numbers), max(cells.numbers)):
            if _end_figures(end) > widest:
                return {SUPPRESSED_LABEL: styles[parsing.STYLE_DECIMAL]}
    return _in_width_order(census)


def _end_figures(value: float) -> int:
    """How many figures after the point a value's shortest spelling writes.

    Nought for a whole value and for one whose shortest spelling carries an
    exponent, which no width census counts. Raises nothing. No I/O.
    """
    text = repr(value)
    if "e" in text or "E" in text or "." not in text:
        return 0
    figures = text[text.find(".") + 1 :]
    if figures == "0":
        return 0
    return len(figures)


def pad_width(text: str) -> int:
    """How wide one zero-padded cell writes its figure field.

    THE RULE ITSELF IS `parsing.pad_width`, and this is the name the
    census reads it under, exactly as `fraction_width` is.
    """
    return parsing.pad_width(text)


def layout_census(
    present: "list[str]", floor: int, raw_distinct: int
) -> dict[str, int]:
    """The census of LAYOUTS a column's present cells hold, under the floor.

    THE COUNT, AND ONLY THE COUNT. This is every rule of contract C6-130
    that is about one layout on its own -- the line, the small supply, the
    fill depth that is too rare, the pool -- and none of the rules of
    C6-131b that are about what a reader can work out from the census as
    a WHOLE. It is a function of its own, and public, because the
    validator recounts a file with it (validation method V3, plan
    P4-D124): a recount run through the whole-census rules would take
    decisions about the MEASURED file's cells that the description never
    took about the real ones, and a conforming twin whose made-up cells
    left exactly one cell off its named layouts would be told it had lost
    a layout it held at the published count.

    The rules, each one the disclosure rule and not a preference:

    - a layout is NAMED at the line, which is the floor or TWO, whichever
      is larger: no count of one is ever published (plan P4-D124);
    - a layout under whose key fewer cells could ever have been counted
      than the column's different values plus the floor is not named,
      because a layout with a small supply names the values it
      describes. The supply is `parsing.layout_supply` and not
      `parsing.layout_room`: on a key of figures alone the zero fill
      takes the leading noughts into a key of their own, so `%%%` is
      worn by nine hundred cells and not a thousand (Codex blocker 1 of
      the extra round, 2026-09-18; plan P4-D260);
    - a ZERO-FILLED layout of two or more fill noughts that either rule
      refuses is counted under the layout one nought SHALLOWER
      (`parsing.layout_shallower`), deepest first, so a fill depth too
      rare to name still counts where it is true -- a cell filled with
      three noughts was filled with at least two -- rather than falling
      out of the census (plan P4-D126);
    - any other layout under the line goes to the `(withheld)` pool where
      the floor is above one, and the pool is written only where it
      reaches two; at a floor of one there is no pool (C5-S13), and such a
      layout, like a small-supply one and like a cell with no layout at
      all, is counted nowhere.

    Guarantees: accepts the present cells, the floor and the column's
    different-spelling count; returns named layouts and possibly
    `(withheld)`, each at least two. Determinism: a function of the
    arguments alone; keys in sorted order. Raises TypeError for a cell
    that is not text. No I/O of any kind.
    """
    convention = parsing.layout_convention(present)
    counts: dict[str, int] = {}
    deepest = 0
    for value in present:
        layout = parsing.layout_form(value, convention)
        if not layout:
            # A CELL WITH NO LAYOUT IS COUNTED NOWHERE, and it is not
            # pooled either: `(withheld)` means a group too small to
            # name, and a cell this census does not describe is not a
            # small group.
            continue
        deepest = max(deepest, parsing.layout_fill(layout))
        if layout in counts:
            counts[layout] = counts[layout] + 1
            continue
        counts[layout] = 1
    line = parsing.census_floor(floor)
    room_needed = raw_distinct + floor
    depth = deepest
    while depth >= 2:
        for layout in sorted(counts):
            if parsing.layout_fill(layout) != depth:
                continue
            if (
                counts[layout] >= line
                and parsing.layout_supply(layout) >= room_needed
            ):
                continue
            shallower = parsing.layout_shallower(layout)
            counts[shallower] = (
                counts[shallower] if shallower in counts else 0
            ) + counts[layout]
            del counts[layout]
        depth = depth - 1
    pooled = 0
    census: dict[str, int] = {}
    for layout in sorted(counts):
        if parsing.layout_supply(layout) < room_needed:
            continue
        if counts[layout] >= line:
            census[layout] = counts[layout]
            continue
        if floor >= 2:
            pooled = pooled + counts[layout]
    if pooled >= 2:
        census[SUPPRESSED_LABEL] = pooled
    return census


def _layout_forms(cells: _Cells) -> dict[str, int]:
    """How many present cells wore each LAYOUT, under the floor (7.12).

    THE FACT THAT LETS A RECORD NUMBER KEEP ITS SHAPE. A declared
    identifier publishes no value, so before this census its twin had
    only two lengths and two alphabet counts to work from -- and it
    wrote `A----------------------------------J` for a UUID, `A------J`
    for `NYC-2033`, and `10000020` for `02254257`. Measured on eight
    hundred rows at two source seeds: the column's own pattern matched
    800 real cells and 0 twin cells, and both files passed their own
    description at exit 0, so nothing named it.

    A layout says what KIND of character stood at each position -- a
    figure, a letter of one case, a hexadecimal character -- and never
    which one. `~~~~~~~~-~~~~-~~~~-~~~~-~~~~~~~~~~~~` says a UUID and
    says nothing whatever about WHICH UUID. The rules about one layout
    at a time are `layout_census`'s.

    AND NO COMPLEMENT OF ONE, which is the rule this function adds over
    the whole census (contract C6-131b, plan P4-D124). A reader holds
    three totals beside the census -- `n_present`, `n_code_alphabet` and,
    in a plain column, `n_all_digits` -- and subtracting from each the
    named layouts it covers counts the cells that wear no named layout.
    Where any of those differences is exactly ONE the census says that
    one row of the table is unlike every other, which the disclosure rule
    forbids as it forbids a count of one. MEASURED before this rule, on
    799 record numbers beside one `REC 123456`: the census published
    `{"@@@%%%%%%%": 799}` against 800 present cells. So, until no
    difference is one:

    - where the difference against `n_present` is one and the pool is
      written, the pool is not written, which makes it one plus the pool;
    - otherwise the smallest named layout that no shallower named layout
      stands behind -- the earliest in sorted order on a tie -- is no
      longer named, and joins the pool where the floor is above one. Only
      such a layout can be taken back, because a deeper fill counted
      under a shallower one would otherwise move into it and leave the
      difference where it was; for the two alphabet totals it is the
      smallest such layout those totals cover.

    The question is asked while anything is published, a census writing
    only its pool included (plan P4-D151), and of the shared rule
    `parsing.census_names_one_row`, which the loader asks too (plan
    P4-D150). Each step raises the difference by at least two or ends the
    rule, so it ends. What it costs is stated, not hidden: a column in which
    exactly one cell wears no named layout, and whose only named layout
    is the one taken back, publishes no layout at all.

    Guarantees: accepts a tally of one column; returns a mapping from
    layouts, plus possibly `(withheld)`, to counts summing to at most
    the column's present cells. Determinism: the answer depends only on
    the tally, and the keys are built in sorted order. Raises nothing.
    No I/O of any kind.
    """
    floor = cells.settings.small_cell_floor
    census = layout_census(cells.present, floor, cells.raw_distinct)
    pooled = 0
    if SUPPRESSED_LABEL in census:
        pooled = census[SUPPRESSED_LABEL]
    named: dict[str, int] = {}
    for layout in sorted(census):
        if layout != SUPPRESSED_LABEL:
            named[layout] = census[layout]
    written_pool = pooled >= 2
    plain = parsing.layout_convention(cells.present) == parsing.LAYOUT_PLAIN
    code_alphabet, all_digits = _published_alphabets(cells)
    totals = [
        (code_alphabet, _LAYOUT_CODE_MARKS),
        (all_digits if plain else 0, _LAYOUT_FIGURE_MARKS),
    ]
    # THE LOOP RUNS WHILE ANYTHING IS PUBLISHED, THE POOL ALONE INCLUDED
    # (plan P4-D151). It ran while a layout was NAMED, so a census that
    # named none and wrote only its pool was never asked the question:
    # 800 record numbers beside one cell of another layout, at a floor of
    # eleven, published `{"(withheld)": 800}` beside 801 present cells,
    # which names the one cell outside the pool -- and the loader then
    # refused the producer's own document. The question is asked of the
    # shared rule, `parsing.census_names_one_row`, which the loader asks
    # too.
    while named or written_pool:
        taken = ""
        readings: list[tuple[int, int]] = []
        for total, marks in totals:
            readings += [(total, _layout_cells_within(named, marks))]
        whole = _layout_cells_within(named, "")
        if written_pool:
            whole = whole + pooled
        readings += [(len(cells.present), whole)]
        failed = parsing.census_names_one_row({}, readings)
        if failed < 0:
            break
        if failed < len(totals):
            taken = _layout_to_take_back(named, totals[failed][1])
        else:
            if written_pool:
                written_pool = False
                continue
            taken = _layout_to_take_back(named, "")
        if floor >= 2:
            pooled = pooled + named[taken]
        del named[taken]
    published: dict[str, int] = {}
    for layout in sorted(named):
        published[layout] = named[layout]
    if written_pool and pooled >= 2:
        published[SUPPRESSED_LABEL] = pooled
    return published


def _layout_prefixes(
    cells: _Cells, layouts: "dict[str, int]"
) -> "dict[str, str]":
    """The literal text a declared column's cells open with (7.12a).

    OWNER RULING OF 2026-09-17, ITEM 1. A layout says what KIND of
    character stood at each position, so `REC1234567` published
    `@@@%%%%%%%` and its twin wrote `FPQ7317879`: measured at 800 rows
    (landing 2b.15), `^REC\\d{7}$` matched 800 real cells and 0 twin
    cells, and `^P\\d{5}$` 800 and 30, both files at exit 0. The owner
    ruled that a constant prefix is published where the column clears
    the smallest group size, amending invariants I3 and F3 for this case
    only.

    TWO SCOPES, AND THE FIRST WINS:

    - `(column)`, where `parsing.literal_prefix` finds one over every
      present cell. Nothing else is then written.
    - otherwise one entry per NAMED layout whose own cells share one.
      A column of `REC` and seven figures beside `E` and six publishes
      `{"@%%%%%%": "E", "@@@%%%%%%%": "REC"}`. This per-layout extension
      is the landing's reading of the ruling and is flagged to the owner.

    EVERY ENTRY ASKS THE DISCLOSURE RULE (`parsing.prefix_nameable`):
    the cells opening with the prefix reach the line, and the present
    cells that do not are nought or reach it too, so no entry says that
    one row of the table is written otherwise.

    AND EVERY ENTRY ASKS THE ROOM RULE TOO (`parsing.prefix_leaves_room`;
    plan P4-D270, contract invariant LP3). A layout is named only where
    it could have come from `n_distinct + floor` different cells, and a
    prefix fixes characters of it: `@@@%%%` beside `REC` leaves a
    THOUSAND cells, not 17,576,000, so 1,000 declared record numbers
    published a shape with exactly one solution and the twin wrote all
    1,000 of them. Where the prefix would take the room below the line
    the prefix is not written, and the census stands: the coarser fact
    is published and the sharper one is not.

    Guarantees: accepts a tally and its published layout census; returns
    a mapping from `(column)` or a named layout to a literal prefix.
    Determinism: a function of the arguments; keys in sorted order.
    Raises nothing. No I/O of any kind.
    """
    floor = cells.settings.small_cell_floor
    convention = parsing.layout_convention(cells.present)
    present = len(cells.present)
    # ONLY BESIDE A CENSUS THAT NAMES A LAYOUT (invariant LP1). The twin
    # writes a prefix as part of a named layout's template; with none
    # named, every cell falls to the band walk, whose own shapes the
    # prefix cannot be laid over without spellings colliding -- measured
    # on 120 `S` and five figures whose census C6-131b emptied, the twin
    # held 43 cells not opening with `S` and missed at exit 3.
    named = [layout for layout in sorted(layouts) if layout != SUPPRESSED_LABEL]
    if not named:
        return {}
    whole = parsing.literal_prefix(cells.present, convention)
    if (
        whole
        and parsing.prefix_nameable(present, present, floor)
        and _prefix_keeps_the_room(cells, named, whole, convention)
    ):
        return {parsing.PREFIX_OF_THE_COLUMN: whole}
    found: "dict[str, str]" = {}
    for layout in sorted(layouts):
        if layout == SUPPRESSED_LABEL:
            continue
        wearing = [
            value
            for value in cells.present
            if parsing.layout_form(value, convention) == layout
        ]
        prefix = parsing.literal_prefix(wearing, convention)
        if not prefix:
            continue
        carrying = 0
        for value in cells.present:
            if value[: len(prefix)] == prefix:
                carrying = carrying + 1
        if parsing.prefix_nameable(
            carrying, present, floor
        ) and _prefix_keeps_the_room(cells, [layout], prefix, convention):
            found[layout] = prefix
    return found


def _prefix_keeps_the_room(
    cells: _Cells, layouts: "list[str]", prefix: str, convention: str
) -> bool:
    """Whether a prefix leaves every layout it governs room to spell the column.

    `parsing.prefix_leaves_room` states the rule and this only asks it of
    each layout the entry would stand over -- every named layout for the
    whole column's prefix, the one layout for a layout's own.
    """
    distinct = cells.raw_distinct
    floor = cells.settings.small_cell_floor
    for layout in sorted(layouts):
        if not parsing.prefix_leaves_room(
            layout, prefix, convention, distinct, floor
        ):
            return False
    return True


# The characters a layout key may hold for every cell wearing it to lie
# inside one of the two alphabets `n_code_alphabet` and `n_all_digits`
# count: the code alphabet is letters, figures, the hyphen and the
# underscore, and a cell of figures alone wears only `%` and `!`.
_LAYOUT_CODE_MARKS = "%@&~^!-_"
_LAYOUT_FIGURE_MARKS = "%!"


def _layout_within(layout: str, marks: str) -> bool:
    """Whether every character of a key is one of ``marks``; "" is any."""
    if not marks:
        return True
    for character in layout:
        if character not in marks:
            return False
    return True


def _layout_cells_within(named: "dict[str, int]", marks: str) -> int:
    """How many cells the named layouts made only of ``marks`` count."""
    counted = 0
    for layout in sorted(named):
        if _layout_within(layout, marks):
            counted = counted + named[layout]
    return counted


def _layout_to_take_back(named: "dict[str, int]", marks: str) -> str:
    """The smallest named layout of ``marks`` with no shallower one named.

    The earliest in sorted order on a tie. There always is one where any
    layout of ``marks`` is named, because the shallowest named layout of
    a fill has nothing named behind it and is made of the same marks.
    """
    best = ""
    for layout in sorted(named):
        if not _layout_within(layout, marks):
            continue
        behind = parsing.layout_shallower(layout)
        covered = False
        while behind:
            if behind in named:
                covered = True
                break
            behind = parsing.layout_shallower(behind)
        if covered:
            continue
        if not best or named[layout] < named[best]:
            best = layout
    return best


def _published_reading_split(
    cells: _Cells, role: str
) -> "tuple[int, int, int, int]":
    """What a declared record number's cells READ AS, under the rule.

    THE FOUR-WAY PARTITION OF `n_present` (contract X2): how many cells
    read as a number, how many as a numeral out of range, how many as a
    numeral contradicting itself, and how many as text. Every block
    carries it, and on a DECLARED RECORD NUMBER -- the one role whose
    whole promise is that no fact about any one record is published --
    it named one (plan P4-D277). **Measured** at a floor of eleven, on
    999 identifiers `REC` and seven figures beside one `42`: the block
    published `n_numeric 1`, `n_all_digits 1` and `n_not_numeric 999`,
    and the layout census was withheld beside them because it would have
    said the same thing.

    A PART BELOW THE LINE IS COUNTED INTO THE LARGEST PART, ties to the
    first of the four, which is ruling 6 of 2026-09-17 again. The four
    then sum to `n_present` exactly as X2 requires, every published part
    is nought or names a group, and so is every complement, because a
    complement here is a sum of the other three.

    IT IS ASKED OF THIS ROLE ALONE, and the limit is stated rather than
    left to be discovered. The three numeric partitions are what the
    numeric roles are described BY -- a column of measurements publishes
    its `n_not_numeric` beside a form census checked against it -- so
    moving them there is a change to what those roles mean and not a
    disclosure repair. Free text publishes the same four beside the same
    promise to name no value, and the same reading of one cell is open
    there; it is measured and left for the owner rather than half-built
    here.

    Guarantees: accepts the tally and the role the reading gave it;
    returns the four counts in the contract's own order, summing to the
    present cells. Determinism: a fixed function of the two. Raises
    nothing. No I/O of any kind.
    """
    parts = [
        len(cells.numbers),
        cells.n_out_of_range,
        cells.n_contradictory,
        cells.n_not_numeric,
    ]
    if role != ROLE_IDENTIFIER:
        return (parts[0], parts[1], parts[2], parts[3])
    # THE RULE IS STATED ONCE, in `parsing.absorbed_parts`, because the
    # generator owes the partition as this publishes it and reads the
    # same function to know which measured partitions it stands for
    # (plan P4-D298).
    kept = parsing.absorbed_parts(parts, cells.settings.small_cell_floor)
    return (kept[0], kept[1], kept[2], kept[3])


def _published_alphabets(cells: _Cells) -> "tuple[int, int]":
    """`n_code_alphabet` and `n_all_digits` as a block may publish them.

    THE DISCLOSURE RULE ASKED OF THE TWO ALPHABET COUNTS (plan P4-D277,
    `parsing.absorbed_total`). Only the two roles that publish no value of
    the table carry these -- a declared record number and free text --
    and each is a census of two groups written as one number: the cells
    inside the alphabet, and the cells outside it, which a reader takes
    by subtracting from `n_present`. **Measured** at a floor of eleven, on
    999 record numbers of `REC` and seven figures beside one `X Y`:
    `n_code_alphabet 999` beside `n_present 1000` named the one
    identifier written outside the alphabet, while the layout census that
    would have named it was withheld for exactly that reason.

    The pair is read here and nowhere else, so the counts the block
    PRINTS and the counts its own censuses are checked against can never
    part: `_layout_forms` and `_form_disclosure` ask this too.

    Guarantees: accepts the tally; returns the code-alphabet count and
    the figures-alone count, each the measured count, nought, or every
    present cell. Determinism: a fixed function of the tally. Raises
    nothing. No I/O of any kind.
    """
    present = len(cells.present)
    floor = cells.settings.small_cell_floor
    return (
        parsing.absorbed_total(cells.code_alphabet, present, floor),
        parsing.absorbed_total(cells.all_digits, present, floor),
    )


def _shape_forms(
    cells: _Cells,
    with_code_total: bool = False,
    with_text_total: bool = True,
    spelled: "list[str] | None" = None,
) -> dict[str, int]:
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

    ``spelled``, WHERE IT IS GIVEN, IS WHAT THE CENSUS COUNTS INSTEAD OF
    THE RAW CELLS: the present cells as the block's level entries speak
    of them (`described_spellings`, plan P4-D275.1), one per present
    cell and in row order. The room rule and the case rule then ask the
    number of different spellings in it, which is the column's published
    `n_distinct` on the four label roles (plan P4-D276) and the number
    C6-31c and C6-31d are stated over.

    Guarantees: accepts a tally of one column and, optionally, its
    present cells respelled; returns a mapping from forms, plus possibly
    `(withheld)`, to counts that sum to the cells that HAVE a form --
    which is at most the column's present cells, and fewer wherever a
    cell was too long to have one. Determinism: the answer depends only
    on the tally and the respelling, and the keys are built in sorted
    order. Raises nothing. No I/O of any kind.
    """
    values = cells.present if spelled is None else spelled
    distinct = cells.raw_distinct if spelled is None else len(set(values))
    counts: dict[str, int] = {}
    # HOW MANY CELLS OF EACH FORM WROTE EVERY LETTER LOWER CASE (plan
    # P4-D121, audit LTM-6). Counted beside the form rather than folded
    # into it, because a case-split FORM would shatter a mixed column
    # into keys the floor then pools: the decision below is taken per
    # form, once the whole count is known.
    lower: dict[str, int] = {}
    for value in values:
        form = parsing.shape_form(value)
        if form and parsing.is_lower_case_text(value):
            lower[form] = (lower[form] if form in lower else 0) + 1
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
    room_needed = distinct + cells.settings.small_cell_floor
    census = _form_census(counts, lower, cells, room_needed, distinct)
    # NO COUNT OF ONE AND NO COMPLEMENT OF ONE, OVER THE WHOLE CENSUS
    # (plan P4-D160), asked of the shared rule the loader asks.
    return _form_disclosure(census, cells, with_code_total, with_text_total)


def _form_disclosure(
    census: "dict[str, int]",
    cells: _Cells,
    with_code_total: bool,
    with_text_total: bool = True,
) -> "dict[str, int]":
    """The form census with no reading of it naming one row (P4-D160).

    THE DISCLOSURE RULE OF P4-D150, ASKED OF THE FORM CENSUS WHATEVER ITS
    KEYS. A reader holds the pool and up to four totals beside the
    census: `n_present`, which every form the census counts lies inside;
    `n_not_numeric`, which every form no number can wear lies inside
    (plan P4-D175); and, on a free-text column, `n_code_alphabet` and
    `n_code_alphabet` less `n_all_digits`, which every form made of
    figures, letters, the hyphen and the underscore lies inside, because
    a form carries two kinds and a cell of figures alone has none. MEASURED
    before this rule, at a floor of twenty: 799 `ABC-00001` beside one
    `WXYZ-123456` published `{"@@@-%%%%%": 799, "(withheld)": 1}`, a pool
    of one; and 799 of them beside one sentence too long to have a form
    published `{"@@@-%%%%%": 799}` beside 800 present cells, a complement
    of one. So, until no reading names a row:

    - a pool of one takes in the smallest family of named keys, the
      earliest in sorted order on a tie, or where none is named is not
      written;
    - a difference of one against `n_present` gives the pool up where it
      is written, which makes it one plus the pool;
    - otherwise the smallest family of named keys that total covers is no
      longer named. MEASURED before the two totals P4-D175 added: 400
      five-figure numbers, 399 codes and one `hello` at a floor of eleven
      published `{"&&&-%%%": 399}` beside `n_not_numeric` 400.

    A FAMILY is a form's own key and its lower-case key, taken back
    together, because a lower-case key named alone counts the form's
    other cells too, and a form's own key named alone its lower-case
    cells. Each step removes a key or
    the pool, so the rule ends. What it costs is stated: a column in which
    exactly one cell wears no named form publishes no form it cannot name
    without naming that cell.

    Guarantees: returns a census whose keys are a subset of the one given,
    with the pool possibly larger or gone. Raises nothing. No I/O.
    """
    named: dict[str, int] = {}
    pooled = 0
    for key in sorted(census):
        if key == SUPPRESSED_LABEL:
            pooled = census[key]
            continue
        named[key] = census[key]
    # THE READINGS, IN THE ORDER THE LOADER ASKS THEM. The first is the
    # only one the pool is counted in; the others count the named keys
    # of one kind, because the pool names no form and so no kind. The
    # last two were added by plan P4-D175: 400 figures, 399 codes and one
    # `hello` published `{"&&&-%%%": 399}` beside `n_code_alphabet` 800,
    # `n_all_digits` 400 and `n_not_numeric` 400, and 800 - 400 - 399 and
    # 400 - 399 are both one. A form carries two kinds, so no cell of
    # figures alone has one, and a code form counts cells inside
    # `n_code_alphabet` less `n_all_digits`.
    kinds = [_FORM_ANY]
    totals = [len(cells.present)]
    if with_code_total:
        code_alphabet, all_digits = _published_alphabets(cells)
        kinds += [_FORM_CODE, _FORM_CODE]
        totals += [code_alphabet, code_alphabet - all_digits]
    # THE LABEL HALF OF A COMPOUND COLUMN PUBLISHES NO `n_not_numeric` of
    # its own, and every cell of it is text, so its `n_present` is the
    # reading this one would be.
    if with_text_total:
        kinds += [_FORM_TEXT]
        totals += [cells.n_not_numeric]
    while named or pooled:
        readings: list[tuple[int, int]] = []
        place = 0
        for total in totals:
            covered = _form_cells_within(named, kinds[place])
            if place == 0:
                covered = covered + pooled
            readings += [(total, covered)]
            place = place + 1
        pool = {SUPPRESSED_LABEL: pooled} if pooled else {}
        failed = parsing.census_names_one_row(pool, readings)
        if failed == -1:
            break
        if failed == -2:
            if not named:
                pooled = 0
                continue
            family = _form_family_to_take_back(named, _FORM_ANY)
            for key in family:
                pooled = pooled + named[key]
                del named[key]
            continue
        if failed == 0 and pooled:
            pooled = 0
            continue
        for key in _form_family_to_take_back(named, kinds[failed]):
            del named[key]
    published: dict[str, int] = {}
    for key in sorted(named):
        published[key] = named[key]
    if pooled:
        published[SUPPRESSED_LABEL] = pooled
    return published


# The three kinds of form key a reading of the census counts: every key;
# a key made only of figures, letters, the hyphen and the underscore, so
# inside `n_code_alphabet`; and a key no number can wear, so inside
# `n_not_numeric` (`parsing.form_never_a_number`, plan P4-D175).
_FORM_ANY = ""
_FORM_CODE = "code"
_FORM_TEXT = "text"


def _form_of_kind(key: str, kind: str) -> bool:
    """Whether a form key is of one of the three kinds a reading counts."""
    if kind == _FORM_CODE:
        return _layout_within(key, _FORM_CODE_MARKS)
    if kind == _FORM_TEXT:
        return parsing.form_never_a_number(key)
    return True


# The characters a form key may hold for every cell wearing it to lie
# inside the code alphabet `n_code_alphabet` counts: figures, letters of
# either case, the hyphen and the underscore.
_FORM_CODE_MARKS = "%@&-_"


def _form_cells_within(named: "dict[str, int]", kind: str) -> int:
    """How many cells the named forms of one kind count."""
    counted = 0
    for key in sorted(named):
        if _form_of_kind(key, kind):
            counted = counted + named[key]
    return counted


def _form_family_to_take_back(
    named: "dict[str, int]", kind: str
) -> "list[str]":
    """The smallest family of named keys of one kind, as a list.

    A family is a form blind to case and its lower-case key; its size is
    the cells both count; the earliest blind form in sorted order wins a
    tie. There is always one where any key of the kind is named, because
    a lower-case key is of the same kind as its form: `&` and `@` are
    the same mark to both `_FORM_CODE_MARKS` and a number's exponent.
    """
    sizes: dict[str, int] = {}
    for key in sorted(named):
        if not _form_of_kind(key, kind):
            continue
        blind = _blind_form(key)
        sizes[blind] = (sizes[blind] if blind in sizes else 0) + named[key]
    best = ""
    for blind in sorted(sizes):
        if not best or sizes[blind] < sizes[best]:
            best = blind
    family: list[str] = []
    for key in sorted(named):
        if _blind_form(key) == best:
            family += [key]
    return family


def _blind_form(key: str) -> str:
    """A form key with every lower-case mark written as a letter mark."""
    built = ""
    for character in key:
        built = built + (
            parsing.SHAPE_LETTER if character == parsing.SHAPE_LOWER
            else character
        )
    return built


def _form_census(
    counts: "dict[str, int]",
    lower: "dict[str, int]",
    cells: _Cells,
    room_needed: int,
    distinct: int,
) -> "dict[str, int]":
    """The form census from its per-form counts, each form split by case.

    The body `_shape_forms` always ran, taken out so the disclosure rule
    of the whole census (plan P4-D160) reads as its own step.
    ``distinct`` is the number of different spellings the census counted
    over, which the case rule below compares with the folded count.
    """
    floor = cells.settings.small_cell_floor
    withheld = 0
    published_counts: dict[str, int] = {}
    for form in sorted(counts):
        if parsing.form_room(form) < room_needed:
            continue
        lowered = lower[form] if form in lower else 0
        # NO LOWER-CASE KEY ON A COLUMN WHOSE VALUES FOLD ONTO EACH
        # OTHER, and the test is over two PUBLISHED counts, so an
        # absence it causes is one a reader predicts, and so tells
        # them nothing. Such a column's twin writes values that differ from one
        # another only in case or edge spacing -- the partners of G9.3
        # and the made-up variants of G8.2 -- and a case flip of a
        # lower-case value is not lower case, so it settles the form's own
        # key and never the lower-case one. Measured on 240 cells, 200
        # `a-b` and twenty `x00` beside twenty `X00`: named apart, the
        # twin's partners came out `A-a` and missed three keys by
        # thirty-three cells, where the case-blind census it had before
        # is met (plan P4-D121).
        if distinct != len(cells.folded_counts):
            lowered = 0
        split = _lower_case_split(
            form, counts[form], lowered, floor, room_needed
        )
        if split:
            for key in sorted(split):
                if key == SUPPRESSED_LABEL:
                    withheld = withheld + split[key]
                    continue
                published_counts[key] = split[key]
            continue
        # NEVER A NAMED COUNT OF ONE, WHATEVER THE FLOOR (plan P4-D181).
        # A free-text column publishes no value, and at the default floor
        # of one a census naming `{"@@-%%%%%%": 1}` beside 799 other codes
        # singled out the one row written that way. Under the line the
        # form is pooled where the floor pools, and counted nowhere at a
        # floor of one, where a pool is not written (invariant S13).
        if counts[form] >= parsing.census_floor(floor):
            published_counts[form] = counts[form]
            continue
        if floor < 2:
            continue
        withheld = withheld + counts[form]
    if withheld:
        published_counts[SUPPRESSED_LABEL] = withheld
    return published_counts


def _lower_case_split(
    form: str, count: int, lowered: int, floor: int, room_needed: int
) -> "dict[str, int]":
    """How one form's cells are named when its lower-case cells are apart.

    THE CASE CONVENTION, CARRIED UNDER THE DISCLOSURE RULE (plan
    P4-D121, audit LTM-6). A form's letter mark said "a letter" and the
    twin wrote a capital, so a column of lower-case codes came back in
    capitals on every row -- measured on 800 cells `e9z-1i1`: a
    case-sensitive pattern matched 800 real cells and 0 twin cells,
    and both files passed. The fact that was missing is how many cells
    of a form wrote every letter lower case, and it is published here
    by naming a SECOND KEY of that form, `&` in every letter place.

    WHAT IS NAMED, and each branch is the disclosure rule and not a
    preference. ``lowered`` is how many of the form's ``count`` cells
    wrote every letter lower case and ``rest`` the others; the line is
    the floor or TWO, whichever is larger, because no count of one is
    ever published and no pair of keys may leave a count of one to be
    worked out from them.

    - ``lowered`` under the line, or the lower-case key's own supply
      below what the small-supply rule asks of any key: the form is
      named as it always was, blind to case. This answers {} and the
      caller writes the form exactly as before, byte for byte.
    - ``lowered`` at or over the line and nothing else: the lower-case
      key alone.
    - both at or over the line: both keys, the form's own key then
      counting the cells that were NOT all lower case.
    - ``rest`` of one or more under the line (plan P4-D160): the
      lower-case key ALONE, counting every cell of the form. It said the
      lower-case cells and pooled the rest, and a rest of one was a pool
      of one -- 799 `abc-00001` beside one `ABC-00799` published
      `{"&&&-%%%%%": 799, "(withheld)": 1}`, which names the one row --
      while naming the form blind to case instead turned the twin's 799
      lower-case codes into capitals. A lower-case key named without its
      partner counts the whole form, validation's recount counts the few
      cells written otherwise under it while they stay under the line,
      and the twin writes the convention the form was written in.

    A reader of a case-blind key therefore is shown nothing about case:
    it is written where the lower-case cells were too few to name, and
    where they were none.

    Guarantees: returns {} or a mapping of the keys to name. Raises
    nothing. No I/O.
    """
    line = parsing.census_floor(floor)
    lower_key = parsing.lower_case_form(form)
    if not lower_key or lowered < line:
        return {}
    if parsing.form_room(lower_key) < room_needed:
        return {}
    rest = count - lowered
    if rest >= line:
        return {lower_key: lowered, form: rest}
    return {lower_key: count}


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
        reading = parsing.comma_reading(cell.numeric_text)
        if reading == parsing.COMMA_DECIMAL:
            settled = settled + 1
            continue
        if cell.kind != parsing.NUMBER:
            continue
        if reading == parsing.COMMA_EITHER:
            unsettled = unsettled + 1
    return unsettled, settled


# The longest figure string the spelling census below reads as one
# number: fifteen figures is the widest whole number binary64 holds
# exactly, so every spelling it names is a number this format carries.
_SPELLING_FIGURES = 15


def _number_spellings(cells: _Cells) -> dict[str, int]:
    """Every spelling of a column that wrote one number more than one way.

    THE FACT A CODE COLUMN OF MIXED PADDING LOST (plan P4-D123; the
    audit's missed item, numbers and codes). A column of coded answers
    written `7`, `07`, `007` and `0` -- how an export that zero-fills
    some cells and not others writes a code -- was described as a count,
    and a count publishes how many cells wore each field width and how
    many were padded, but never WHICH number wore which. Its twin came
    back `7`, `007`, `0`, `00`, `07` and `05`: seven spellings for four,
    three of them spellings the real column never had, and both files
    passed. Nothing published could say otherwise.

    WHAT IS PUBLISHED, and only here. A census of the column's spellings
    with how many cells wrote each, under four conditions, every one of
    them the disclosure rule or the reading this census is for:

    - every cell read as a number is written in figures alone, at most
      fifteen of them, so every key is a whole number this format holds;
    - at least two of those spellings are ONE NUMBER, which is what the
      census is for -- a column writing each number one way is already
      described by its field widths, and publishes `{}` here;
    - EVERY spelling is written by at least the smallest group size and
      at least two cells. The census is all or nothing, as the value
      histogram is: a spelling too rare to name is never pooled, because
      beside the named ones a pool's count would be the complement of a
      number anybody can add up, and a count of one is never published;
    - and the spellings are no more than a set of categories may hold in
      a table this size, so a long column of counts is never turned into
      a list of every value it holds.

    A column with no such census publishes `{}`, and that absence says
    only that one of the four did not hold -- no count of anybody.

    Guarantees: a function of the tally alone; keys in sorted order.
    Raises nothing. No I/O of any kind.
    """
    written: dict[str, int] = {}
    numbers = 0
    for cell in cells.classified:
        if cell.kind != parsing.NUMBER:
            continue
        numbers = numbers + 1
        text = cell.text
        if len(text) > _SPELLING_FIGURES or not parsing.is_digit_text(text):
            return {}
        written[text] = (written[text] if text in written else 0) + 1
    if numbers < 1:
        return {}
    line = parsing.census_floor(cells.settings.small_cell_floor)
    seen: dict[str, int] = {}
    twice = False
    for spelling in sorted(written):
        if written[spelling] < line:
            return {}
        bare = _figures_unfilled(spelling)
        if bare in seen:
            twice = True
        seen[bare] = 1
    if not twice or len(written) > _categorical_ceiling(cells):
        return {}
    return {spelling: written[spelling] for spelling in sorted(written)}


def _figures_unfilled(spelling: str) -> str:
    """A figure string with its leading noughts taken off, `0` at least."""
    start = 0
    while start < len(spelling) - 1 and spelling[start] == "0":
        start = start + 1
    return spelling[start:]


def _padded_cells(cells: _Cells) -> int:
    """How many cells of this column were written with a leading zero.

    Counted off the CELLS. The remark that carried this count used it
    because the map may have pooled the form below the floor; since plan
    P4-D221 that remark speaks only where the map names the form, and
    with the map's own count, so this answers only whether any cell is
    padded.
    """
    counted = 0
    for cell in cells.classified:
        if cell.kind != parsing.NUMBER:
            continue
        if numeric_style(cell.numeric_text) != parsing.STYLE_LEADING_ZERO:
            continue
        counted = counted + 1
    return counted


def _form_tally(cells: _Cells) -> "dict[str, int]":
    """How many cells of this column wrote each form, before any rule.

    Counted over the cells that read as a number this format can hold.
    The forms map is this tally held to the disclosure rule; the width
    censuses read it beside the map to learn how many cells of which
    form the map counted into its commonest one (plan P4-D222).
    """
    counts: dict[str, int] = {}
    for cell in cells.classified:
        if cell.kind != parsing.NUMBER:
            continue
        style = numeric_style(cell.numeric_text)
        if style in counts:
            counts[style] = counts[style] + 1
        else:
            counts[style] = 1
    return counts


def _counted_into(
    styles: "dict[str, int]", tally: "dict[str, int]"
) -> "tuple[str, int]":
    """The form a forms map counted rarer forms into, and how many cells.

    `parsing.absorbed_census` adds the cells of every form below the line
    to the commonest named form (plan P4-D222), so that form is the one
    whose published count exceeds its own cells. Guarantees: returns
    `("", 0)` where no form took anything in. Raises nothing. No I/O.
    """
    for style in NUMERIC_STYLES:
        cells = tally[style] if style in tally else 0
        if style in styles and styles[style] > cells:
            return style, styles[style] - cells
    return "", 0


def _added_to(counts: "dict[int, int]", width: int, cells: int) -> None:
    """Add ``cells`` at ``width`` to a tally, in place."""
    if width in counts:
        counts[width] = counts[width] + cells
    else:
        counts[width] = cells


def _width_keys(counts: "dict[int, int]") -> "dict[str, int]":
    """A tally by width, keyed by the canonical width text, noughts left out."""
    tally: dict[str, int] = {}
    for width in sorted(counts):
        if counts[width] > 0:
            tally[f"{width}"] = counts[width]
    return tally


def _in_width_order(census: "dict[str, int]") -> dict[str, int]:
    """A published width census, widths ascending and any pool last."""
    widths: list[int] = []
    for key in census:
        if key != SUPPRESSED_LABEL:
            widths += [int(key)]
    published_counts: dict[str, int] = {}
    for width in sorted(widths):
        published_counts[f"{width}"] = census[f"{width}"]
    if SUPPRESSED_LABEL in census:
        published_counts[SUPPRESSED_LABEL] = census[SUPPRESSED_LABEL]
    return published_counts


def _absorbed_widths(counts: "dict[int, int]", floor: int) -> dict[str, int]:
    """A width tally held to the disclosure rule (plans P4-D221, P4-D222).

    `parsing.absorbed_census` over the tally's own total, the widths an
    open vocabulary: a width fewer cells than `parsing.census_floor` wrote
    is counted into the commonest width at the line, and where no width
    reaches it the census is one pool. Keys are canonical widths,
    ascending, or `(withheld)` alone. Raises nothing. No I/O of any kind.
    """
    tally = _width_keys(counts)
    total = 0
    for key in tally:
        total = total + tally[key]
    return _in_width_order(parsing.absorbed_census(tally, total, floor, 0))


def _width_censuses(
    cells: _Cells, styles: "dict[str, int]"
) -> "tuple[dict[str, int], dict[str, int]]":
    """`pad_widths` and `field_widths`, built together under the disclosure rule.

    TWO CODE COLUMNS OF THE SAME FORM ARE NOT THE SAME COLUMN (P4-D14,
    P4-D30). A forms map saying `leading_zero: 240` does not say the
    field was five figures wide, and a cell written `199` -- no pad, no
    point -- has its width in neither of the other censuses. `pad_widths`
    counts the padded cells by the width of their figure field, and
    `field_widths` counts EVERY whole-written cell (`plain`,
    `leading_plus`, `leading_zero`) by that same width, so the two
    overlap deliberately: the difference at a width is how many cells
    were written there with no pad. A PLUS DOES NOT HIDE A PAD (plan
    P4-D145): `+00123` is counted as padded, where the plus route below
    allows it. THE KEYS ARE THE WIDTHS AS DECIMAL FIGURES, canonically.

    WHAT THE TWO COUNT IS THE COLUMN THE FORMS MAP DESCRIBES (plan
    P4-D222; stage 2 closed by the owner rulings of 2026-09-17). The map
    counts a form fewer cells than `parsing.census_floor` wrote into its
    commonest form, so these censuses count only the cells of forms the
    map names, and count the cells it took in as cells of that form at
    its commonest width -- padded at the commonest pad width where the
    form is `leading_zero`, unpadded at the commonest unpadded width
    otherwise. A map that names nothing has no widths published at all
    (contract P8). Then no count either census prints, and no difference
    a reader takes between them, is below the line
    (`parsing.width_census_breaches` finds nothing):

    1. THE PLUS ROUTE (plan P4-D148). The census's total less the
       `leading_zero` count is the plus-signed padded cells, and the
       `leading_plus` count less that is the plus-signed unpadded ones.
       Where either is too few to name, the plus-signed padded cells are
       not counted as padded -- the state a column with none reaches.
    2. A PAD WIDTH BELOW THE LINE is counted, in both censuses, into the
       commonest pad width; where no pad width reaches the line the
       padded census is one pool of its whole total.
    3. THE UNPADDED CELLS AT A WIDTH, where fewer than the line, are
       counted into the width most unpadded cells wrote. Measured before
       P4-D148: 800 padded five-figure codes beside one `12345` published
       `field_widths {"5": 801}` beside `pad_widths {"5": 800}`.
    4. A FIELD WIDTH STILL BELOW THE LINE -- padded cells only, beside a
       pooled padded census -- is counted into the commonest field width
       by the census's own rule, and a census no width of which reaches
       the line is one pool.

    Guarantees: accepts a tally of one column and its published forms
    map; returns the two published censuses, between which
    `parsing.width_census_breaches` finds nothing. Determinism: a
    function of the two. Raises nothing. No I/O of any kind.
    """
    floor = cells.settings.small_cell_floor
    line = parsing.census_floor(floor)
    if SUPPRESSED_LABEL in styles:
        return {}, {}
    form, taken = _counted_into(styles, _form_tally(cells))
    pads: dict[int, int] = {}
    plus_pads: dict[int, int] = {}
    unpadded: dict[int, int] = {}
    for cell in cells.classified:
        if cell.kind != parsing.NUMBER:
            continue
        style = numeric_style(cell.numeric_text)
        if style not in POINT_FREE_STYLES or style not in styles:
            continue
        width = pad_width(cell.numeric_text)
        if style == parsing.STYLE_LEADING_ZERO:
            _added_to(pads, width, 1)
        elif parsing.is_padded(cell.numeric_text):
            _added_to(plus_pads, width, 1)
        else:
            _added_to(unpadded, width, 1)
    # 1. THE PLUS ROUTE.
    plus_cells = 0
    for width in plus_pads:
        plus_cells = plus_cells + plus_pads[width]
    counted_plus = (
        plus_cells > 0
        and parsing.STYLE_LEADING_PLUS in styles
        and parsing.census_nameable(
            [plus_cells], [styles[parsing.STYLE_LEADING_PLUS]], floor
        )
    )
    for width in sorted(plus_pads):
        if counted_plus:
            _added_to(pads, width, plus_pads[width])
        else:
            _added_to(unpadded, width, plus_pads[width])
    # 2 AND 3. EACH PART COUNTED INTO ITS COMMONEST WIDTH AT THE LINE.
    pooled_fields = False
    padded_named = _into_commonest_named(pads, line)
    if padded_named >= 0 and form == parsing.STYLE_LEADING_ZERO:
        _added_to(pads, padded_named, taken)
    elif taken > 0 and form == parsing.STYLE_LEADING_ZERO:
        pooled_fields = True
    unpadded_named = _into_commonest_named(unpadded, line)
    if unpadded_named >= 0 and form in POINT_FREE_STYLES and (
        form != parsing.STYLE_LEADING_ZERO
    ):
        _added_to(unpadded, unpadded_named, taken)
    elif form in POINT_FREE_STYLES and form != parsing.STYLE_LEADING_ZERO:
        pooled_fields = pooled_fields or taken > 0
    unpadded_total = 0
    for width in unpadded:
        unpadded_total = unpadded_total + unpadded[width]
    if unpadded_named < 0 and unpadded_total > 0:
        # NO UNPADDED WIDTH REACHES THE LINE, so no whole-number width
        # names them: beside a named padded census every field width
        # would carry a difference too few cells wrote.
        pooled_fields = True
    fields: dict[int, int] = {}
    for width in sorted(pads):
        _added_to(fields, width, pads[width])
    for width in sorted(unpadded):
        _added_to(fields, width, unpadded[width])
    if padded_named < 0:
        # 4. THE PADDED CENSUS IS ONE POOL: a field width only padded
        # cells wrote, fewer than the line, is counted into the commonest
        # field width of two figures or more that reaches the line, where
        # a padded cell can stand; where none does, the census is a pool.
        target = -1
        for width in sorted(fields):
            if width >= 2 and fields[width] >= line and (
                target < 0 or fields[width] > fields[target]
            ):
                target = width
        for width in sorted(fields):
            if width == target or fields[width] >= line or fields[width] < 1:
                continue
            if target < 0:
                pooled_fields = True
                continue
            _added_to(fields, target, fields[width])
            fields[width] = 0
    padded_census = _absorbed_widths(pads, floor)
    if padded_named < 0:
        padded_total = plus_cells if counted_plus else 0
        if parsing.STYLE_LEADING_ZERO in styles:
            padded_total = padded_total + styles[parsing.STYLE_LEADING_ZERO]
        padded_census = {}
        if padded_total > 0:
            padded_census = {SUPPRESSED_LABEL: padded_total}
    if pooled_fields:
        total = 0
        for style in POINT_FREE_STYLES:
            if style in styles:
                total = total + styles[style]
        if total < 1:
            return padded_census, {}
        return padded_census, {SUPPRESSED_LABEL: total}
    return padded_census, _absorbed_widths(fields, floor)


def _into_commonest_named(counts: "dict[int, int]", line: int) -> int:
    """Count every width below the line into the commonest one at it (P4-D222).

    In place. The widest count at the line or above takes in every count
    below it, the narrowest width on a tie; where no width reaches the line
    nothing moves and the answer is -1, otherwise that width.
    """
    target = -1
    for width in sorted(counts):
        if counts[width] >= line and (target < 0 or counts[width] > counts[target]):
            target = width
    if target < 0:
        return -1
    for width in sorted(counts):
        if width != target and 0 < counts[width] < line:
            _added_to(counts, target, counts[width])
            counts[width] = 0
    return target


POINT_FREE_STYLES = (
    parsing.STYLE_PLAIN,
    parsing.STYLE_LEADING_PLUS,
    parsing.STYLE_LEADING_ZERO,
)


def _bin_census(numbers: "list[float]") -> "dict[int, int] | None":
    """How many of a column's numbers fall in each of the bins.

    THE ONE PLACE THE BINS ARE COUNTED, and it is one place because two
    published facts are read off the same count: the census of how many
    values each bin holds, and the list of bins holding NONE. Counting
    twice is how the two would come to disagree about a column, and a
    description whose two shape facts contradict each other is worse
    than either of them alone.

    Returns None -- not an empty count -- where the column has no scale
    to divide at all: no numbers, an end this format cannot hold, or
    two finite ends whose WIDTH it cannot hold. The two callers answer
    that case in their own words, because "there is no scale" and "the
    scale has no empty bin" are different sentences and a reader has to
    be able to tell them apart.

    Guarantees: accepts the numbers the statistics used; returns a
    mapping from bin number to a count of one or more, holding a key
    only for the bins that hold something, or None. Determinism: the
    answer depends only on the values. Raises nothing. No I/O of any
    kind.
    """
    if not numbers:
        return None
    lowest = min(numbers)
    highest = max(numbers)
    for value in numbers:
        if not math.isfinite(value):
            return None
    if not math.isfinite(lowest) or not math.isfinite(highest):
        return None
    if not math.isfinite(highest - lowest):
        return None
    counts: dict[int, int] = {}
    for value in numbers:
        place = parsing.histogram_bin(value, lowest, highest)
        if place in counts:
            counts[place] = counts[place] + 1
        else:
            counts[place] = 1
    return counts


def _empty_edges(numbers: "list[float]") -> "list[list[float]]":
    """The REAL boundaries of each stretch this column leaves empty.

    RESIDUAL R-P4-138, CLOSED BY THE OWNER'S RULING OF 2026-09-04.
    `empty_bins` divides the column's reach into thirty-two and names
    the bins that hold nothing, and the bins a column leaves empty are
    strictly INSIDE the stretch it really leaves empty -- so a twin
    repaired to the edge of the nearest occupied bin still lands inside
    the source's own gap. Measured on a 300-row column whose real gap
    runs 26.9 to 74.0: five cells of three hundred sat in that gap at
    every seed, each about one unit past the cluster edge.

    THIS FACT IS THE TWO REAL VALUES, one per side: the largest value
    below the gap and the smallest above it. The twin then has the
    edge itself to keep out of rather than a bin edge inside it.

    WHAT IT COSTS A READER TO KNOW, priced against the owner's ruling
    of 2026-09-03 on the small-cell floor. Each edge IS a value of a
    real cell -- the same kind of fact a percentile rung is, and a
    ladder publishes eleven of them on every numeric column. It says
    that some row holds 26.9 and some row holds 74.0, and nothing about
    which rows, how many, or what those rows hold anywhere else. The
    ruling that covers a rung covers this.

    Guarantees: accepts the numbers the statistics used; returns one
    ascending `[below, above]` pair per maximal run of empty bins, in
    ascending order, and the empty list where the column has no scale
    or leaves no bin empty. Determinism: a fixed function of the
    values. Raises nothing. No I/O of any kind.
    """
    bins = _empty_bins(numbers)
    if not bins:
        return []
    ordered = sorted(numbers)
    edges: "list[list[float]]" = []
    for run in _bin_runs(bins):
        # The values on each side of this run of empty bins. A run
        # never reaches an end -- the smallest value is in the first
        # bin and the largest in the last -- so both sides exist.
        below = None
        above = None
        for value in ordered:
            place = parsing.histogram_bin(value, ordered[0], ordered[-1])
            if place < run[0]:
                below = value
            if place > run[1] and above is None:
                above = value
        if below is None or above is None:
            continue
        if above <= below:
            continue
        edges += [[below, above]]
    return edges


def _bin_runs(bins: "list[int]") -> "list[tuple[int, int]]":
    """The maximal runs of consecutive bin numbers, ascending."""
    runs: "list[tuple[int, int]]" = []
    start = -1
    last = -2
    for place in bins:
        if place != last + 1:
            if start >= 0:
                runs += [(start, last)]
            start = place
        last = place
    if start >= 0:
        runs += [(start, last)]
    return runs


def _empty_bins(numbers: "list[float]") -> "list[int]":
    """Which of the bins hold NONE of this column's numbers (P4-D32).

    THE FACT THAT NAMES NOBODY, and that is the whole of why it is
    published where the census beside it is not. A bin holding one
    value says a person is there and where they are; a bin holding
    fewer than the smallest group size says a small group is there;
    a bin holding NOTHING says nobody is there, and there is no
    smaller group than nobody. The owner ruled on exactly that question
    on 2026-08-31 and ruled that an empty bin may be published while
    the bins holding one to one-below-the-floor stay hidden.

    IT DOES NOT REOPEN THE ALL-OR-NOTHING RULE ON THE CENSUS, and the
    reasoning that rule rests on comes through untouched. That rule
    holds because a census with a pooled remainder cannot be read by
    RANK: the pooled values are in bins nobody named, so the ranks the
    named bins cover are unknown and a generator cannot build the map
    it needs. This fact is not read by rank at all. It says where no
    value is, which is the same sentence whatever the floor is and
    whatever the other bins hold, and a generator reads it as a set of
    stretches to keep out of rather than as a place to put a value.

    WHAT IT COSTS A READER TO KNOW. The bins are fixed by the two ends
    the ladder already publishes, so naming an empty one adds no edge a
    reader could not already compute. What it adds is the sentence "no
    cell of the real column lies between these two edges" -- a
    statement about the absence of rows, not about any row.

    THE FIRST BIN AND THE LAST ARE NEVER AMONG THEM. The scale runs
    from the column's smallest value to its largest, so the smallest
    lies in the first bin and the largest in the last, and a column
    with a scale at all has both of them occupied.

    Guarantees: accepts the numbers the statistics used; returns the
    bin numbers holding none of them, ascending, and the empty list
    where the column has no scale. Determinism: the answer depends only
    on the values. Raises nothing. No I/O of any kind.
    """
    counts = _bin_census(numbers)
    if counts is None:
        return []
    # AND A COLUMN WHOSE VALUES ARE ALL ONE NUMBER NAMES NOTHING. Its
    # two ends are the same number, so there is no width to divide and
    # `parsing.histogram_bin` puts every value in the first bin by its
    # own total rule -- which makes the other thirty-one look empty
    # while there is no division for them to be empty IN. Saying so
    # would be saying something about a scale that does not exist, and
    # the loader refuses exactly that: `_has_width` there asks the same
    # question and this is the producer's side of it. A constant
    # position inside a joined column is the shape that found it.
    if max(numbers) <= min(numbers):
        return []
    return [
        place
        for place in range(parsing.HISTOGRAM_BINS)
        if place not in counts
    ]


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
    # A COLUMN WHOSE ENDS THIS FORMAT CANNOT HOLD PUBLISHES NO
    # HISTOGRAM. Bins between infinite edges have no width and no
    # meaning, and every value would land in one of them, so the honest
    # answer is silence rather than a census nobody can read. The
    # loader accepts an absent histogram, and the generator falls back
    # to the ladder exactly as it did before this fact existed. The
    # width has to be inside the format too, not only the ends: a
    # column running from about -1e308 to about 1e308 has finite ends
    # and a width this format cannot hold. `_bin_census` settles all
    # three refusals in one place and answers None for them, so this
    # rule and the empty-bin rule beside it cannot come to differ about
    # which columns have a scale.
    counts = _bin_census(numbers)
    if counts is None:
        return {}
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
    # simple, and at a floor of one nothing pools and every column gets
    # its shape. At the default of 11 (plan P4-D316) a column with any
    # bin under eleven rows publishes none.
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


def _mode_of(cells: _Cells) -> "tuple[float | None, int]":
    """The number this column held most often, and how many cells held it.

    THE VALUE IS AN IDENTITY QUESTION AND THE ANSWER IS THE EXACT ONE.
    Cells are grouped by the canonical triple each already carries --
    the same key `_distinct_numbers` counts with, and the same one the
    declared-value and sentinel rules compare by -- so two spellings of
    one number are one value here, and two numbers that round to one
    binary64 are two. Grouping by the rounded `value` would make one
    mode out of two different numbers.

    THE TIE RULE IS THE SMALLEST, and it is written down rather than
    left to whatever a mapping iterates in. Where several numbers share
    the largest count the smallest of them is the mode: it is
    deterministic, it names no value the ladder does not already
    publish one of, and it gives an independent implementer one answer
    (plan P4-D4.11).

    Guarantees: accepts a tally of one column; returns the mode's own
    published value and its count, or `(None, 0)` where the column
    holds no number at all. The floor is NOT applied here -- this
    answers what the column held, and `_numeric_details` decides what
    may be published. Determinism: the answer depends only on the
    multiset of cells. Raises nothing. No I/O of any kind.
    """
    counts: "dict[tuple[int, tuple[str, ...], int], int]" = {}
    values: "dict[tuple[int, tuple[str, ...], int], float]" = {}
    for cell in cells.classified:
        if cell.kind != parsing.NUMBER:
            continue
        if cell.exact is None or cell.value is None:
            continue
        if cell.exact in counts:
            counts[cell.exact] = counts[cell.exact] + 1
        else:
            counts[cell.exact] = 1
        values[cell.exact] = cell.value
    if not counts:
        return None, 0
    most = 0
    for key in counts:
        if counts[key] > most:
            most = counts[key]
    smallest: "float | None" = None
    for key in counts:
        if counts[key] != most:
            continue
        found = values[key]
        if smallest is None or found < smallest:
            smallest = found
    return smallest, most


def _mode_published(cells: _Cells, floor: int) -> dict[str, object]:
    """The mode pair a column may publish, or the withheld pair.

    Three bounds, and each is a rule rather than a preference. A mode
    held by fewer cells than the SMALL-CELL FLOOR is a small group and
    the floor exists for exactly that. A mode held by ONE cell is not a
    mode at all: every value ties, and the tie rule would publish the
    column's smallest number under a name that says it dominates.

    AND THE COMPLEMENT IS A GROUP TOO (stage 3 landing 3.5, plan
    P4-D335). The count was floored on ONE side, and a heap publishes
    the other: measured at a floor of eleven, 395 zeros among 400
    numbers published `mode_count: 395` beside `n_used_in_statistics:
    400`, and the five cells that are not the heap are a group the
    floor would never let a key name. It is `parsing.census_nameable`
    asked of the count against the cells the statistics used -- the
    same rule the spelling censuses ask -- so the pair is published
    where the count is a group and what is left of the numbers is
    nothing or a group, and withheld whole otherwise.

    WITHHELD WHOLE, AND NOT THE COUNT ALONE, for the reason the floor
    already withheld it whole: a value published without its count says
    "this was the commonest number", which is the same fact in fewer
    words.

    Guarantees: accepts a tally and a floor of zero or more; returns
    either both keys with a number and a count, or both keys withheld.
    Determinism: a function of the two. Raises nothing. No I/O.
    """
    value, count = _mode_of(cells)
    if value is None or count < 2 or count < floor:
        return {"mode": None, "mode_count": 0}
    if not parsing.census_nameable([count], [len(cells.numbers)], floor):
        return {"mode": None, "mode_count": 0}
    return {"mode": value, "mode_count": count}


# THE THREE FORMS A GROUPED NUMBER CAN WEAR, and the only three the
# generator will write a separator into. A padded figure field is a code,
# and an exponent form's mantissa is not where a reader groups thousands.
_GROUPABLE_STYLES = ("plain", "leading_plus", "decimal")


def _whole_figures(text: str) -> int:
    """How many figures stand before the point, separators not counted.

    Guarantees: accepts one written number; returns the count of its
    whole figures with any sign and any group separator removed.
    Determinism: a fixed function of the text. Raises TypeError if
    handed anything that is not a string instance. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError("a whole-figure count was asked of something else")
    # An accounting negative's brackets are not figures (stage 2 audit):
    # counted as two, `(123.45)` stood as a bare four-figure cell and
    # withheld the mark from a whole column of grouped charges. Nor is
    # any sign, nor any mark of `parsing.GROUP_MARKS` (landing 2b.2),
    # which is what `parsing.number_core` takes off.
    body = parsing.number_core(text)
    if body[:1] == "+" or body[:1] == "-":
        body = body[1:]
    figures = 0
    for letter in body:
        if letter == ".":
            break
        figures += 1
    return figures


def grouping_proven(cells: "list[str]", floor: int, mark: str = ",") -> bool:
    """Whether written cells prove the grouping ``mark``, by `_group_separator`'s rule.

    The same proof, bareness and majority `_group_separator` asks of a
    described column, asked of cells written with a point for decimals:
    the generator's own numbers before any decimal-comma exchange, so it
    can tell when a twin's cells no longer prove the mark it writes.
    ``mark`` is the one they are grouped with, a comma for a published
    comma or point and the published mark itself otherwise.

    Guarantees: accepts cells, the smallest group size and one mark of
    `parsing.GROUP_MARKS`; returns a bool. Determinism: a function of the
    three. No I/O of any kind.
    """
    proven = 0
    bare = 0
    for cell in cells:
        if not isinstance(cell, str):
            raise TypeError("a grouping recount was handed something else")
        if parsing.classify_number(cell) != parsing.NUMBER:
            continue
        if numeric_style(cell) not in _GROUPABLE_STYLES:
            continue
        if _whole_figures(cell) < 4:
            continue
        if parsing.thousands_mark(cell) == mark:
            proven += 1
        else:
            bare += 1
    return proven >= 1 and proven >= floor and proven > bare


def _marks_exchanged(text: str) -> str:
    """The cell with its points and commas exchanged, `42.037,34` to `42,037.34`.

    Guarantees: accepts one cell; returns text of the same length.
    Raises TypeError if handed anything that is not a string instance.
    No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError("a mark exchange was asked of something else")
    out = ""
    for letter in text:
        if letter == ".":
            out = out + ","
        elif letter == ",":
            out = out + "."
        else:
            out = out + letter
    return out


def _grouping_evidence(cell: _Cell, decimal: bool) -> "tuple[bool, bool, str]":
    """What one numeric cell proves about the mark between thousands.

    THE ONE EVIDENCE RULE, asked by `_group_separator` and
    `_thousands_marks` alike (plan P4-D141, the final Codex review's
    grouping item 7). The two used to ask it separately, and they
    disagreed on a declared decimal comma: the majority key read
    `1097.001,01` in the column's own grammar and proved a point, while
    the census asked the strict groups of the undeclared reader and
    proved nothing. Measured: 780 such cells beside 20 of `197 001,01`
    published `group_separator: "."` beside `thousands_marks: {" ": 20}`,
    a description the loader refuses under TM1 -- so the table could not
    be twinned at all.

    The answer is three things:

    1. WHETHER THE CELL REFUSES A MARK TO THE WHOLE COLUMN: a form the
       writer never groups -- padded, or an exponent -- holding a mark,
       or holding a comma at all (rule 2 of `_group_separator`).
    2. WHETHER IT COULD HAVE BEEN GROUPED: a groupable form with four or
       more whole figures.
    3. THE MARK IT PROVES, or "" for a bare cell, read in the column's
       own grammar: a declared decimal comma has its points and commas
       exchanged first, and there the proof is the one
       `parsing.comma_reading` gives, which drops every point whatever
       groups it leaves. The mark is returned AS WRITTEN AFTER THAT
       EXCHANGE, so a proven point comes back as a comma and each caller
       publishes it as the point that column writes.

    Guarantees: accepts one classified numeric cell and whether its
    column declared a decimal comma; returns (refuses, eligible, mark),
    the mark "" wherever the cell is not eligible. Determinism: a fixed
    function of the two. Raises nothing. No I/O of any kind.
    """
    written = cell.text
    if decimal:
        written = _marks_exchanged(cell.text)
    style = numeric_style(cell.numeric_text)
    mark = parsing.thousands_mark(written)
    if decimal and mark == "" and "," in written:
        # A DECLARED COLUMN IS READ IN ITS OWN GRAMMAR, which drops
        # every point whatever groups it leaves, so its proof is the
        # one `comma_reading` gives and not the strict groups the
        # undeclared reader needs: `1097.001,01` has always proven a
        # point, and a stricter proof would have withdrawn the mark
        # from columns the stage 2 rule published it on.
        reading = parsing.comma_reading(written)
        if reading == parsing.COMMA_GROUPED or reading == parsing.COMMA_EITHER:
            mark = ","
    if style not in _GROUPABLE_STYLES:
        return (bool(mark) or "," in written, False, "")
    if _whole_figures(written) < 4:
        return (False, False, "")
    return (False, True, mark)


def _group_separator(cells: _Cells) -> str:
    """The mark this column writes between thousands, or no mark.

    THE SPELLING THE DESCRIPTION USED TO THROW AWAY. A charge written
    `$2,198.92` came back from the twin as `$2198.92`, so code developed
    on the twin silently discarded every charge over a thousand when it
    met the real table -- a mean of 412 against a true 918, with no
    error raised.

    WHAT COUNTS AS PROOF. A cell of four or more whole figures, in a form
    the writer groups, proves a mark of `parsing.GROUP_MARKS` where its
    whole part reads as thousands groups around that one mark
    (`parsing.thousands_mark`) -- and that includes a lone group such as
    `12,345`, which could be a decimal comma in some other table but is
    read as thousands by this one: the statistics already rest on that
    reading, so refusing it here left the commonest grouped column, whole
    counts below a million, written bare (stage 2 audit, 400 of 400
    cells). A four-figure cell in such a form carrying no valid grouping
    is BARE.

    EVERY MARK, NOT ONLY THE COMMA (landing 2b.2). A space, an
    apostrophe, the right single quotation mark, a no-break space and a
    narrow no-break space prove their own mark by the same rule, and a
    column whose charges were written `2 198.92` publishes a space.

    PUBLISHED ONLY WHERE THE TWIN CAN REPRODUCE THE COLUMN'S CONVENTION:

    1. **THE MAJORITY OF THE COLUMN.** The commonest proven mark -- the
       first in `parsing.GROUP_MARKS` on a tie -- must reach the smallest
       group size and outnumber every other four-figure groupable cell,
       bare or grouped with another mark. One grouped cell among two
       hundred bare ones publishes nothing (part one's review measured a
       twin grouping all two hundred), and five bare stragglers among
       395 grouped cells no longer strip the mark from the whole column
       (stage 2 audit: the twin wrote 0 of 400 grouped). The twin writes
       every groupable cell with the mark, so a column mixing the two is
       written as its majority.
    2. **A FORM THE TWIN WILL NOT GROUP.** A padded or exponent cell
       holding a valid grouping (`01,234,000`, `1,234,000e1`) withholds
       the mark, because the writer never groups those forms.
    3. **A DECLARED DECIMAL COMMA** swaps the roles of the comma and the
       point: the cell is read with its points and commas exchanged, and
       where the comma is proven the mark published is `.`, the one
       `42.037,34` writes. The other marks are not exchanged, so
       `1 234,56` publishes a space. Under that declaration a lone group
       reads as thousands for the same reason as above.

    Guarantees: accepts the column's tally; returns a mark of
    `parsing.PUBLISHED_GROUP_MARKS`, "." only under a declared decimal
    comma and "," never there. Determinism: a fixed function of the
    tally, cells taken in their given order. Raises nothing. No I/O of
    any kind.
    """
    decimal = cells.decimal_comma
    proven: "dict[str, int]" = {}
    for mark in parsing.GROUP_MARKS:
        proven[mark] = 0
    others = 0
    for cell in cells.classified:
        if cell.kind != parsing.NUMBER:
            continue
        refuses, eligible, mark = _grouping_evidence(cell, decimal)
        if refuses:
            return ""
        if not eligible:
            continue
        if not mark:
            others += 1
            continue
        proven[mark] = proven[mark] + 1
        others += 1
    best = ""
    for mark in parsing.GROUP_MARKS:
        if proven[mark] > 0 and (best == "" or proven[mark] > proven[best]):
            best = mark
    if best == "":
        return ""
    held = proven[best]
    # AND THE LINE IS THE CENSUS FLOOR, NOT THE SETTINGS FLOOR (rule W
    # of the stage-3 count inventory, plan P4-D335). The mark is a WORD
    # MOVED BY A COUNT: it stands exactly where enough cells wore it, so
    # a reader who knows how every other cell was written reads the last
    # one's spelling off the word. At a settings floor of one that count
    # was one, and `parsing.census_floor` is the one statement of "never
    # one, whatever the floor" that `negative_form`, `wide_runs` and the
    # spelling censuses beside it already read. At the default floor of
    # eleven nothing here moves.
    if held < parsing.census_floor(cells.settings.small_cell_floor):
        return ""
    if held <= others - held:
        return ""
    if decimal and best == ",":
        return "."
    return best


def _negative_form(cells: _Cells) -> str:
    """How this column writes its negative numbers, by the majority rule.

    ACCOUNTING BRACKETS WERE READ AND THEN FORGOTTEN (landing 2b.2). A
    column of charges written `(1,234.56)` for a credit was described
    with its negatives counted and its brackets dropped, so the twin
    wrote `-1,234.56`: code parsing the real table's brackets met none on
    the twin, and the real table failed its own description's spelling
    check. The same held for the minus sign of the character tables and
    for the trailing minus accounting systems write, which this reader
    did not read as negative at all until the same landing.

    Each cell reading as a negative number this format holds is counted
    under the notation it wrote (`parsing.negative_notation`). A notation
    other than the hyphen-minus in front is published where its cells
    reach the smallest group size and outnumber every other negative
    cell together; the commonest such notation is the candidate, the
    first in `parsing.NEGATIVE_FORMS` on a tie. Otherwise the column
    publishes `minus`. The twin writes every negative in the published
    notation, so a column mixing two is written as its majority, as a
    grouped column is.

    Guarantees: accepts the column's tally; returns one name of
    `parsing.NEGATIVE_FORMS`. Determinism: a fixed function of the
    tally. Raises nothing. No I/O of any kind.
    """
    counts: "dict[str, int]" = {}
    for form in parsing.NEGATIVE_FORMS:
        counts[form] = 0
    negatives = 0
    for cell in cells.classified:
        if cell.kind != parsing.NUMBER or cell.sign != parsing.SIGN_NEGATIVE:
            continue
        form = parsing.negative_notation(cell.numeric_text)
        counts[form] = counts[form] + 1
        negatives += 1
    best = parsing.NEGATIVE_MINUS
    for form in parsing.NEGATIVE_FORMS:
        if form == parsing.NEGATIVE_MINUS:
            continue
        if counts[form] > 0 and (
            best == parsing.NEGATIVE_MINUS or counts[form] > counts[best]
        ):
            best = form
    if best == parsing.NEGATIVE_MINUS:
        return best
    held = counts[best]
    # THE CENSUS FLOOR, for `_group_separator`'s reason (rule W, plan
    # P4-D335): the notation is a word one group of cells moves, and a
    # word one CELL can move tells the reader who knows every other cell
    # what that cell wrote. Invariant NS1 reads the same line.
    if (
        held < parsing.census_floor(cells.settings.small_cell_floor)
        or held <= negatives - held
    ):
        return parsing.NEGATIVE_MINUS
    return best


def _census_floor(settings: Settings) -> int:
    """The smallest count the spelling censuses of landing 2b.7 publish.

    NEVER ONE, WHATEVER THE SETTINGS FLOOR (owner twin definition,
    clause 3, as the Codex review of landing 2b.2 applied it; plan
    P4-D65.1). A published count of one names an individual outright:
    the reader who knows how every other cell was written can tell how
    that cell was. `small_cell_floor` may be lowered to one, so a census
    governed by it alone publishes exactly that count, and the review
    measured the disclosure at a floor of eleven as well -- the pooled
    remainder carried it there.

    Two is the smallest count that names a group rather than a person,
    so these censuses read the larger of two and the settings floor.
    Where the owner raises the floor for stage 3 this rises with it and
    nothing here has to move.

    Guarantees: accepts the settings; returns a whole number of two or
    more. Determinism: a fixed function of the floor. Raises nothing. No
    I/O of any kind.
    """
    return census_floor_of(settings.small_cell_floor)


def census_floor_of(floor: int) -> int:
    """`_census_floor`'s rule, read from a floor rather than settings.

    The publication guard checks a FINISHED document, where the floor is
    a number it read out of the settings block and no `Settings` object
    survives. It has to answer the same question this module answers
    when it writes the census, and a second copy of "two, or the floor
    where that is larger" is a second thing to keep in step -- which is
    the drift the guard exists to catch, landing in the guard itself.

    ONE STATEMENT OF IT, which `parsing.census_floor` holds and the
    loader and the checker read too (plan P4-D140).

    Guarantees: accepts a floor; returns two or the floor, whichever is
    larger. Determinism: a fixed function of the floor. Raises nothing.
    No I/O of any kind.
    """
    return parsing.census_floor(floor)


def _mixture_census(
    counts: "dict[str, int]",
    order: "tuple[str, ...]",
    settings: Settings,
    populations: "list[int]",
    silent: "dict[str, int]",
) -> "dict[str, int]":
    """One census of a column's MIXED conventions, floored per convention.

    THE MAJORITY RULE THREW THE MINORITY AWAY, AND EVERY CHECK PASSED
    (the Codex review of landing 2b.2, closed 2026-09-15; plan
    P4-D65.2). A column of 600 charges wrote 480 with a minus in front
    and 120 in accounting brackets; the description published the
    majority notation alone, the twin wrote 600 minuses and no bracket,
    and neither the twin's report nor the real table's named a thing.
    The same held for marks: 200 cells grouped with a space beside 100
    grouped with a narrow no-break space came back as 300 ordinary
    spaces, so code that strips an ordinary space succeeded on the twin
    and failed on the real table -- which is goal 1 of the owner's
    two mandatory goals, broken silently.

    So a mixture is REPRODUCED as a count per convention rather than
    collapsed to its majority (owner ruling 2026-09-15: the twin writes
    anything as the original source, without changes).

    WHAT IT PUBLISHES, and the floor is read per convention:

    * a convention used by at least `_census_floor` cells is named with
      its count;
    * A CONVENTION BELOW THE LINE IS COUNTED INTO THE COMMONEST NAMED
      ONE, which is ruling 6 of 2026-09-17 and `parsing.absorbed_census`'
      own rule, written here for the same reason (plan P4-D274, the
      repair of the extra review round of 2026-09-18). It used to be
      pooled, and where the pool then fell below the line the WHOLE
      census went silent -- which left the majority field standing alone
      and told a reader what the census had held back. **Measured** at a
      floor of eleven, on 388 positive decimals, eleven negatives in
      accounting brackets and one `-12.25`: the description published
      `n_negative 12`, `negative_form brackets` and
      `negative_notations {"(unavailable)": 0}`, and the majority field
      needs at least eleven bracketed cells while twelve would have been
      named -- so the three facts together prove eleven brackets and one
      other notation. Counted in, the census says `{"brackets": 12}`,
      nothing is derivable, and describing the table again says the same
      thing, so the table passes its own description;
    * where NO convention reaches the line there is no commonest named
      one to take them in, and what is left is pooled under `(withheld)`
      -- these censuses have FOUR and SEVEN possible keys, so a pool here
      names no convention, which is exactly the property `decimal_plus`
      lacks and the reason that key may not pool at all;
    * but a pool that is itself below the floor would name the cells it
      holds as surely as publishing them would, so a census that cannot
      pool safely publishes `(unavailable)` and no number whatever.

    THE COMPLEMENT CLAUSE IS ASKED, NOT ASSUMED (plan P4-D140, the final
    Codex review's grouping BLOCKER). Among the printed counts it holds by
    construction: every one of them is at least the floor. It did NOT
    hold against the cells a reader can subtract the printed total from,
    and the first version said it did: 1,200 grouped prices at a floor of
    eleven, one of them rewritten bare, published `{",": 1199}` beside a
    row count of 1,200. So ``populations`` names every such total and
    `parsing.census_nameable`, the one statement of the disclosure rule,
    decides whether the census may speak at all.

    AND WHAT A CENSUS THAT CANNOT SPEAK PUBLISHES IS ``silent``, the
    caller's decision: it must be the state the same census reaches where
    NO cell wears a convention, whenever the population is not empty,
    because a reader who can tell those two apart can tell nought from a
    count below the floor.

    Guarantees: accepts the counts per convention, the enumeration
    fixing the key order, the settings, the totals a reader can subtract
    from and the silent state; returns `{}` where no cell wears a
    convention and the silent state is empty, a mapping of named
    conventions with possibly a `(withheld)` remainder, or a copy of the
    silent state. Determinism: the answer depends only on those five,
    and the keys are built in the enumeration's order. Raises nothing.
    No I/O of any kind.
    """
    total = 0
    for name in order:
        if name in counts:
            total = total + counts[name]
    if total < 1:
        return dict(silent)
    floor = _census_floor(settings)
    published: "dict[str, int]" = {}
    pooled = 0
    commonest = ""
    for name in order:
        if name not in counts:
            continue
        if counts[name] >= floor:
            published[name] = counts[name]
            if not commonest or counts[name] > published[commonest]:
                commonest = name
            continue
        pooled = pooled + counts[name]
    # A CONVENTION BELOW THE LINE IS COUNTED INTO THE COMMONEST NAMED
    # ONE (plan P4-D274, ruling 6 of 2026-09-17). Ties go to the first
    # in the enumeration's order, which is the order this loop walks,
    # and the name that takes the rest in is always the largest printed
    # count, so nothing else can grow past it.
    if commonest and pooled >= 1:
        published[commonest] = published[commonest] + pooled
        pooled = 0
    if pooled < 1:
        return _spoken_or_silent(published, populations, settings, silent)
    # A POOL IS A THING HELD BACK, AND AT A FLOOR OF ONE NOTHING IS
    # (invariant C5-S13). This census reads `_census_floor`, which is
    # two even where the person asked for one, so it has a range below
    # its own floor exactly where the document says there is none: two
    # cells, one in brackets and one wearing the minus sign, would pool
    # a remainder of two into a description whose floor is one, and the
    # loader's S13 walk refuses that document -- rightly, because
    # `(withheld)` is the format's one word for a group the floor holds
    # back. So at a floor of one this census does not pool at all: it
    # publishes the unavailable state, which holds back no COUNT and
    # takes no key S13 reads.
    if pooled < floor or settings.small_cell_floor < 2:
        return dict(silent)
    published[SUPPRESSED_LABEL] = pooled
    return _spoken_or_silent(published, populations, settings, silent)


def _spoken_or_silent(
    published: "dict[str, int]",
    populations: "list[int]",
    settings: Settings,
    silent: "dict[str, int]",
) -> "dict[str, int]":
    """A census as it would print, or its silent state where the rule says so.

    The complement half of the disclosure rule, asked once for every
    census `_mixture_census` builds: `parsing.census_nameable` over the
    counts it would print and the totals a reader can subtract them
    from (plan P4-D140).

    Guarantees: accepts the census as it would print, the populations,
    the settings and the silent state; returns the first or a copy of
    the last. Determinism: a fixed function of the four. Raises
    nothing. No I/O of any kind.
    """
    printed: "list[int]" = []
    for name in sorted(published):
        printed += [published[name]]
    if parsing.census_nameable(
        printed, populations, settings.small_cell_floor
    ):
        return published
    return dict(silent)


def _negative_notations(cells: _Cells) -> "dict[str, int]":
    """How many negative cells wore each notation, floored per notation.

    `negative_form` publishes the column's MAJORITY notation and the
    generator writes every negative that way, so a column mixing two
    came back written wholly as one. This census is what says the
    column mixed them, and the generator spends it cell by cell.

    COUNTED OVER THE SAME CELLS `negative_form` IS COUNTED OVER: every
    cell reading as a negative number this format holds, under the
    notation `parsing.negative_notation` reads from it. The two keys
    therefore never disagree about the population, and the majority key
    stays exactly what it was -- this census is a sibling, not a
    replacement, and a reader with no use for the mixture reads
    `negative_form` as before.

    ITS COMPLEMENT IS NOUGHT BY CONSTRUCTION, and it is still asked
    (plan P4-D140): every negative cell wears exactly one notation, so
    the population a reader subtracts from is the negatives themselves.
    Its silent state is `(unavailable)`, as it always was: the census is
    empty only where the column has no negative number, and
    `n_negative` already says that in public.

    Guarantees: accepts the column's tally; returns `_mixture_census`'s
    answer over `parsing.NEGATIVE_FORMS`. Determinism: a fixed function
    of the tally. Raises nothing. No I/O of any kind.
    """
    counts: "dict[str, int]" = {}
    negatives = 0
    for cell in cells.classified:
        if cell.kind != parsing.NUMBER or cell.sign != parsing.SIGN_NEGATIVE:
            continue
        negatives += 1
        form = parsing.negative_notation(cell.numeric_text)
        if form in counts:
            counts[form] = counts[form] + 1
        else:
            counts[form] = 1
    if negatives < 1:
        return {}
    return _mixture_census(
        counts,
        parsing.NEGATIVE_FORMS,
        cells.settings,
        [negatives],
        {UNAVAILABLE_LABEL: 0},
    )


def _thousands_marks(cells: _Cells) -> "dict[str, int]":
    """How many grouped cells wore each mark, floored per mark.

    THE SIBLING OF `_negative_notations`, ASKED OF THE OTHER MIXTURE.
    `group_separator` publishes one mark and the twin groups every
    groupable cell with it, so 200 cells grouped with a space beside 100
    grouped with a narrow no-break space were written as 300 ordinary
    spaces. This census carries the mixture and the generator spends it.

    COUNTED OVER THE CELLS THAT PROVE A MARK, by `_grouping_evidence`,
    which is `_group_separator`'s own evidence rule and not a second one
    (plan P4-D141): a cell in a groupable form whose whole part reads as
    groups of three around one mark, read in the column's own grammar. A
    BARE groupable cell proves no mark and is named nowhere here -- but
    it is COUNTED, because a reader can take it back out (below).

    READ IN THE COLUMN'S OWN GRAMMAR. A declared decimal comma has the
    cell's points and commas exchanged before the mark is read, exactly
    as `_group_separator` does it, so the two keys agree on every cell;
    a proven comma is published as the point that column writes.

    THE DISCLOSURE RULE, WITH BOTH COMPLEMENTS (plan P4-D140, the final
    Codex review's second BLOCKER). The census prints no count and no
    remainder below `census_floor`, and nothing is left over, against
    the cells that COULD have been grouped or against every number of
    the column, that is neither nought nor at least that floor. The
    first version counted the bare cells nowhere, so 1,200 grouped
    prices at a floor of eleven with ONE rewritten bare published
    `{",": 1199}` beside a row count of 1,200. Where the rule refuses,
    the census is `{}` -- the state a column in which no cell proves a
    mark reaches -- so nought and a count below the floor stay one
    published state, and the generator writes every groupable cell with
    the published majority mark, which is what it did before this census
    existed.

    Guarantees: accepts the column's tally; returns `{}` or a mapping of
    named marks, each at least `census_floor`, with possibly a
    `(withheld)` remainder of at least that, whose total leaves nought
    or at least that floor against the groupable cells and against the
    numeric cells. Determinism: a fixed function of the tally. Raises
    nothing. No I/O of any kind.
    """
    decimal = cells.decimal_comma
    counts: "dict[str, int]" = {}
    groupable = 0
    numeric = 0
    for cell in cells.classified:
        if cell.kind != parsing.NUMBER:
            continue
        numeric += 1
        refuses, eligible, mark = _grouping_evidence(cell, decimal)
        if refuses:
            # A CELL THAT REFUSES THE MARK TO THE COLUMN REFUSES THE
            # CENSUS TOO (plan P4-D141). `_group_separator` publishes no
            # mark for such a column, and a census naming one beside it
            # had the twin group cells a description publishing no mark
            # says were never grouped: 400 grouped charges beside three
            # `01,234,000` published `{",": 202}` beside `""`, and the
            # twin's own description then published a comma.
            return {}
        if not eligible:
            continue
        groupable += 1
        if not mark:
            continue
        if decimal and mark == ",":
            mark = "."
        if mark in counts:
            counts[mark] = counts[mark] + 1
        else:
            counts[mark] = 1
    return _mixture_census(
        counts,
        parsing.PUBLISHED_GROUP_MARKS,
        cells.settings,
        [groupable, numeric],
        {},
    )


def _signable_decimals(decimals: int, negatives: int) -> int:
    """How many decimals a reader can work out could have carried a plus.

    THE SECOND POPULATION OF THE PLUS CENSUS (round 2 of the review,
    the disclosure pass, item 5). Both numbers are published: the
    decimals by the forms map and `n_negative` by the block. A negative
    cell is written with a minus and never with a plus, so their
    difference is what is left for the census to be about. It is a
    LOWER bound, because `n_negative` counts the negative whole numbers
    too, and `_decimal_plus` reads it only where it does not fall below
    the signed count -- below there the two do not describe one another
    and the difference is no reading of anything.

    Guarantees: accepts the two counts; returns their difference, never
    below nought. Determinism: a fixed function of the two. Raises
    nothing. No I/O of any kind.
    """
    if negatives >= decimals:
        return 0
    return decimals - negatives


def _decimal_plus(cells: _Cells, styles: "dict[str, int]") -> "dict[str, int]":
    """How many cells written with a point carried a leading plus.

    THE PLUS A DECIMAL LOST (landing 2b.2). The form ladder tests the
    point before the plus, so `+12.5` is a `decimal` cell and its plus
    was published nowhere: the twin wrote none, and a column of signed
    changes came back with every rise unsigned. A whole number keeps its
    plus through the `leading_plus` form, counted cell by cell; this is
    the same count for the cells the ladder files under `decimal`, so a
    column with a plus on three cells in ten keeps three in ten on both
    kinds of number.

    A CENSUS WITH ONE CATEGORY, AND THAT IS WHY IT CANNOT POOL (the
    Codex review of landing 2b.2, closed 2026-09-15; plan P4-D65.1).
    `+` is the only key this census can ever carry, so a `(withheld)`
    remainder beside it names the category it is holding back and
    differs from `{}` for exactly one reason: somebody signed a cell.
    The review measured it -- 1,200 cells at a floor of eleven, one of
    them rewritten with a plus, two descriptions differing in that key
    alone and both loading -- and a reader holding the other 1,199
    spellings can read off the remaining individual's. So the pool is gone
    from this key and `(unavailable)` stands in its place, which is the
    same published state a count of nought reaches.

    THE THREE STATES, and each is a statement a reader can act on:

    1. `{}` -- this column wrote NO cell with a point at all, so the
       census has no population. `numeric_styles` already says that
       publicly, so the empty census adds nothing a reader did not
       have.
    2. `{"+": n}` -- exactly n of them carried a plus, published only
       where n names a group AND the cells that did not also name one:
       n reaches `_census_floor`, and the remainder is either nought
       (every one of them signed, which is a fact about the column
       rather than about anybody in it) or reaches that floor too. The
       second half is the complement clause, and without it a column of
       1,199 signed cells and one unsigned one published the unsigned
       cell as plainly as the first version published the signed one.
    3. `{"(unavailable)": 0}` -- anything else. Nought is in here
       BESIDE the below-floor counts, deliberately and at a cost named
       in the plan: a column with a point and no plus at all used to
       publish `{}`, and now says nothing, because a state only a
       zero-plus column reaches is a state that tells a reader every
       other column had one.

    NEVER ONE, WHATEVER THE SETTINGS FLOOR, which is `_census_floor`'s
    own rule and the reason this key stopped reading `small_cell_floor`
    directly.

    Guarantees: accepts the column's tally; returns `{}`, `{"+": n}` with
    n at least `_census_floor` and a complement of nought or at least
    that, or `{"(unavailable)": 0}`. Determinism: a fixed function of the
    tally. Raises nothing. No I/O of any kind.
    """
    counted = 0
    decimals = 0
    for cell in cells.classified:
        if cell.kind != parsing.NUMBER:
            continue
        if numeric_style(cell.numeric_text) != parsing.STYLE_DECIMAL:
            continue
        decimals += 1
        if parsing.number_core(cell.numeric_text)[:1] == "+":
            counted += 1
    # OVER THE `decimal` COUNT THE FORMS MAP PUBLISHES (plan P4-D222). The
    # map counts a form below the line into its commonest form, so the
    # column it describes has that many decimals -- the cells it took in
    # among them, carrying no plus -- or, where the map names other forms
    # and not this one, none: its few decimals were counted as another
    # form, and a census saying they exist names them.
    # And where the map is one pool it says no form's count, so this census
    # says nothing either: `{}` there would say no cell carried a point,
    # which the pool holds back.
    if SUPPRESSED_LABEL in styles:
        return {UNAVAILABLE_LABEL: 0}
    decimals = 0
    if parsing.STYLE_DECIMAL in styles:
        decimals = styles[parsing.STYLE_DECIMAL]
    else:
        counted = 0
    if decimals < 1:
        return {}
    floor = cells.settings.small_cell_floor
    # THE SECOND POPULATION, WHICH IS DERIVED AND NOT PRINTED (round 2
    # of the review, the disclosure pass, item 5). A reader does not
    # only hold the decimals: `n_negative` is published beside them, and
    # a negative cell is written with a minus and never with a plus, so
    # the decimals LESS the negatives are the cells that could have
    # carried one. `census_nameable` was asked of the first population
    # and not of the second. **Measured** at a floor of eleven on a
    # declared measurement of 500 cells -- 400 written `+100.5` upward,
    # 99 written `-100.5` downward and ONE written `250.5` -- which
    # published `n_numeric` 500, `n_negative` 99 and `decimal_plus
    # {"+": 400}`, so 500 less 99 less 400 is one unsigned non-negative
    # cell. The description loaded and the source file validated with
    # nothing missed.
    #
    # `n_negative` counts the whole column and a negative WHOLE number
    # is in it too, so the difference is a LOWER bound on the cells that
    # could carry a plus. Erring low errs toward withholding, which is
    # the direction that publishes less.
    signable = _signable_decimals(decimals, cells.n_negative)
    # ...AND RULING 6 TAKES THE RARE SPELLING FIRST (the owner's ruling
    # of 2026-09-17, item 6). The unsigned cells among those are a
    # spelling of the same value; below the line they are counted into
    # the commonest spelling the column wrote, which is the plus, and
    # the description is that of the column with them written that way
    # -- so the census says 401 and the difference is nought. Withholding
    # the whole census instead would have cost 400 cells their plus in
    # the twin to hide one, and ruling 6 exists to refuse that trade.
    unsigned = signable - counted
    line = parsing.census_floor(floor)
    # ...AND ONLY WHERE THE FIRST POPULATION IS ALREADY SATISFIED. The
    # complement over the DECIMALS is settled by withholding the census
    # and has been since P4-D140 -- 1,199 signed prices beside one whole
    # number at a floor of one publish `{"(unavailable)": 0}`, and that
    # is a decision of its own, not this one. Ruling 6 is asked here
    # about the cells the second population leaves over, and about
    # nothing else, so this reads a description the old rule already
    # allowed and never rewrites one it refused.
    if (
        parsing.census_nameable([counted], [decimals], floor)
        and counted >= line
        and 0 < unsigned < line
    ):
        counted = signable
        unsigned = 0
    # THE DISCLOSURE RULE, stated once in `parsing.census_nameable` and
    # read here over BOTH populations a reader subtracts this count from
    # (plan P4-D140).
    # THE SECOND POPULATION IS READ ONLY WHERE THE SUBTRACTION IS
    # CONSISTENT. `n_negative` counts the negative WHOLE numbers too, so
    # on a column holding both kinds the difference falls BELOW the
    # signed count and tells a reader nothing except that their
    # arithmetic does not apply -- measured on 900 changes written half
    # `+12` and half `+3.25`, where it comes out well under the plus
    # count at every seed. Reading it there would refuse a description
    # every such column produces.
    populations = [decimals]
    if signable >= counted:
        populations += [signable]
    if parsing.census_nameable([counted], populations, floor):
        return {"+": counted}
    return {UNAVAILABLE_LABEL: 0}

def _figures_past_the_pad(digits: str) -> str:
    """The run a padded cell writes, once its pad is read off.

    THE PAD IS READ BEFORE THE CANONICAL QUESTION IS ASKED (landing
    2b.16 part 2, plan P4-D107), and this is the whole of that reading.
    `_wide_runs` beside it asks whether a wide run is the text its own
    value writes; a padded cell's figures are not that text until its
    padding is off, which is why the padded form was left out of the
    question until this landing and why 800 respelled padded keys went
    unseen.

    NO CENSUS DECIDES THE SPLIT, and that is the reason this can be a
    function of the text alone. Past `parsing.WIDE_RUN_FLOOR` every
    value is a whole number, and the figures a whole number writes never
    begin with a zero -- so every leading zero of the run is pad, and
    what remains is the run. The published width census is not consulted
    and does not need to be: a column pooling its width under
    `(withheld)`, or publishing none, splits exactly where a column
    naming `19` splits.

    A RUN OF ZEROS KEEPS ONE, so the answer is never the empty text. No
    such cell reaches the canonical question -- zero is far below the
    wide floor -- and a rule whose answer is a run of figures should
    return one whatever it is handed.

    Guarantees: accepts a run of base-ten figures with its sign already
    taken off; returns the same run with its leading zeros removed, and
    a single `0` where it was all zeros. Determinism: a fixed function
    of the text. Raises nothing. No I/O of any kind -- the answer is a
    SHORTER PIECE of the text handed in, so no figure this column did
    not already write travels out through it.
    """
    kept = digits
    while kept[:1] == "0" and len(kept) > 1:
        kept = kept[1:]
    return kept


def _wide_runs(cells: _Cells, styles: "dict[str, int]") -> str:
    """Whether this column's wide runs of figures are their own values' text.

    THE CANONICAL QUESTION NOTHING ASKED (landing 2b.13, plan P4-D90,
    closing the residual plan P4-D66.2 named). That decision admitted
    the figures of a whole number past what binary64 keeps as a spelling
    of its own value, because a real export of seventeen-figure
    accession numbers writes runs no shortest-round-trip rule produces
    and was being told its own file failed its own description. The
    admission is right and it took the canonical question with it: a run
    of figures is a spelling of the number it reads back as, so
    `styles.spelled` cannot ask it, and the ceiling beside it reads the
    published count of the form, which on every column of identifiers is
    the row count and licenses every cell. Measured before this key
    existed: 800 canonical seventeen-figure runs, respelled cell by cell
    into the value-preserving neighbours binary64 cannot tell from them,
    790 of 800 moved, validated at exit 0 with nothing missed.

    So the fact is published about the COLUMN and the ceiling is read
    against it. `none` where no cell of the column is such a run;
    `canonical` where fewer of them than the census floor are anything
    but the text their own values write; `respelled` where at least
    that many are not.

    WHAT IT DISCLOSES IS A PROPERTY OF THE WRITER, AND ONLY A GROUP
    MOVES IT (plan P4-D140). The three words name no count, no row and
    no figure. The first version said that was enough and carried no
    floor between its last two words, and the final Codex review
    measured why it was not: 800 canonical keys at a floor of eleven
    published `canonical`, the same column with cell 432 respelled into
    its binary64 neighbour published `respelled`, both loaded, and a
    reader who knew the other 799 cells read the last one's spelling
    off the word. So the word moves at `parsing.census_floor` respelled
    runs and not at one, and the checker's `canonical` ceiling is that
    same floor: a file with fewer respelled runs meets it, which is
    what keeps the real table meeting its own description.

    ASKED OF THE TWO POINT-FREE FORMS, and of the CORE of each cell
    (landing 2b.13's repair pass, plan P4-D91). The first version asked
    it of the `plain` form alone, and of the raw text, on the stated
    ground that "a padded or plus-signed wide run wears a spelling whose
    own census already answers for it". MEASURED, that ground was false
    for one of the two and the raw text was wrong for both: a column of
    800 plus-signed wide keys, every one respelled, published `none` and
    was checked by nothing -- the styles map counts FORMS, and a
    respelled neighbour wears the same form and the same width as the
    run it replaced, so no census beside this one can see it. So
    `leading_plus` is asked too.

    AND `leading_zero` IS ASKED TOO, ONCE THE PAD IS READ OFF (landing
    2b.16 part 2, plan P4-D107). Until this landing the padded form was
    left out, on the ground that a padded cell's figures are not its
    value's figures BY CONSTRUCTION -- `0090071992547409931` carries the
    padding the width census governs -- so the canonical question could
    not be asked without first deciding which zeros are the pad. That
    ground held for the reading and not for the exclusion, and the
    measurement is what says so: 800 zero-padded nineteen-wide keys at
    floor eleven, every cell respelled into the value-preserving
    neighbour a double cannot tell apart -- 786 of 800 moved at seed 1,
    780 at seed 7 -- published `none`, and the twin, the real table and
    the canonical description handed the respelled file all exited 0
    with nothing named. The word was false about the whole file and the
    ceiling had nothing to govern.

    THE PAD NEEDS NO CENSUS TO DECIDE IT, which is the sentence the old
    bound was missing. A canonical run NEVER begins with a zero: past
    `WIDE_RUN_FLOOR` every value is a whole number and the figures it
    writes are its own, so a leading zero can only be pad. The split is
    therefore a fact of the TEXT and not of the published width, and
    `_figures_past_the_pad` takes it -- the pad is read first, and the
    canonical question is asked of the figures that remain. A column
    whose published width is `(withheld)`, or that publishes no width at
    all, is read exactly the same way, which is what keeps this word
    from waiting on a census it never needed.

    THE SAME READING REPAIRS THE FORM THIS RULE ALREADY ADMITTED, which
    is the other half of the argument that the pad belongs to the
    reading. `+0019094652364241860` is `leading_plus`, not
    `leading_zero`, so it was counted here before this landing and its
    PADDED figures were compared with its value's: measured, a column of
    800 plus-signed padded keys, every one written canonically, was
    counted 800 of 800 NOT canonical, and the column published
    `respelled` about a file that respells nothing. One reading answers
    for all three point-free forms, and none of them is a special case.

    AND OF THE CORE, because the form beside it is read off the core:
    brackets, the minus sign of the character tables, a surrounding
    space and a thousands mark are all taken off by `number_core`
    before a cell's form is decided, and this asked the raw text. A
    single cell of eight hundred given a leading space and respelled
    made a REAL table fail its own description at exit 3, while a
    column of 800 grouped or space-padded wide runs published `none`
    and hid the respelling of every one of them. `parsing.is_a_wide_run`
    carries both measurements.

    AND HELD TO THE SMALLEST GROUP SIZE, as its sibling `negative_form`
    is by invariant NS1. A word that carries no count still names the
    FORM of the cells it is about, and where fewer cells than the floor
    are such runs the styles map has pooled that form into `(withheld)`
    precisely so that no reader can tell what form they wore: measured,
    one wide key beside 799 charge amounts at a floor of eleven
    published `numeric_styles {(withheld): 1, decimal: 799}` and
    `wide_runs: canonical` beside it, which tells a reader exactly what
    the pool was hiding. Below the floor the word is `none`, and the
    contract sentence for `none` says so.

    AND ONLY OVER THE FORMS THE FORMS MAP NAMES (plan P4-D222; stage 2
    closed by the owner rulings of 2026-09-17). A form fewer cells than
    `parsing.census_floor` wrote is counted into the commonest named form,
    so its cells are cells of that form in the column the description
    describes; a wide run among them would name what the map counted
    away, and beside a map naming no point-free form invariant WR1
    refuses the word. Where the map is one pool every cell is asked.

    Guarantees: accepts the column's tally and its published forms map;
    returns one word of `parsing.WIDE_RUNS`. Determinism: a fixed
    function of the two. Raises nothing. No I/O of any kind.
    """
    counted = 0
    odd = 0
    for cell in cells.classified:
        if cell.kind != parsing.NUMBER:
            continue
        text = cell.numeric_text
        style = numeric_style(text)
        if style not in POINT_FREE_STYLES:
            continue
        if SUPPRESSED_LABEL not in styles and style not in styles:
            continue
        # THE NUMBER THE RECORD ALREADY HOLDS, read once by `_classify`
        # from this same text. Reading it again here asked the parser
        # 180 more times on an 80-cell column (invariant of structural
        # rule A, `tests/test_r6_taxonomy_contract.py`).
        value = cell.value
        if value is None:
            continue
        core = parsing.number_core(text)
        if not parsing.is_a_wide_run(core, value):
            continue
        counted = counted + 1
        digits = core
        if digits[:1] == "-" or digits[:1] == "+":
            digits = digits[1:]
        if _figures_past_the_pad(digits) != parsing.wide_run_figures(value):
            odd = odd + 1
    # THE CENSUS FLOOR ON BOTH OF THIS WORD'S LINES (rule W, plan
    # P4-D335). The line BETWEEN the last two words already stood here,
    # through `census_nameable` below; the line between `none` and the
    # other two read the settings floor, so one wide run among 799
    # charge amounts at a floor of one published `canonical` and named
    # the form of exactly one cell. Both lines are the same line now.
    floor = parsing.census_floor(cells.settings.small_cell_floor)
    if counted < 1 or counted < floor:
        return parsing.WIDE_NONE
    # NO ONE CELL MOVES THE WORD (plan P4-D140, the final Codex review's
    # first BLOCKER). The line between the two words used to stand
    # between nought respelled runs and one, and a word that one cell
    # can move tells the reader who knows every other cell what that
    # cell wrote. It stands at the census floor now: `respelled` where
    # at least that many runs are respelled -- a group, by the rule
    # `parsing.census_nameable` states -- and `canonical` below it,
    # which is the ceiling the checker holds a file to in the same
    # words.
    if parsing.census_nameable([odd], [], floor):
        return parsing.WIDE_RESPELLED
    return parsing.WIDE_CANONICAL


def _numeric_details(cells: _Cells, whole: bool) -> dict[str, object]:
    """The published description of a numeric column."""
    numbers = cells.numbers
    n_present = len(cells.present)
    # THE FORMS MAP AND THE TWO WIDTH CENSUSES A READER SUBTRACTS FROM
    # IT, built together so the disclosure rule can be asked of all three
    # at once (plan P4-D148).
    styles_map = _numeric_styles(cells)
    widths_pair = _width_censuses(cells, styles_map)
    details: dict[str, object] = {
        "percentiles": _quantiles(numbers),
        # THE OTHER NINETY RUNGS (plan P4-D4.10). One key, one
        # disposition, and the fidelity comes from the generator
        # interpolating them rather than from checking each.
        "percentiles_between": _finer_quantiles(numbers),
        "value_histogram": _value_histogram(cells, numbers),
        # ...AND WHICH OF THOSE BINS HOLD NOTHING AT ALL (plan P4-D32,
        # the owner's ruling of 2026-08-31). The census above is all or
        # nothing and vanishes at any floor above one; this fact
        # survives it, because a bin holding nobody is a bin no floor
        # protects. It is what stops a twin writing cells into a
        # stretch the real column left empty -- a two-peak column
        # publishes a middle rung no cell of it holds, and the value
        # stage honoured that rung until this fact told it not to.
        "empty_bins": _empty_bins(numbers),
        # ...AND THE REAL EDGES OF EACH OF THOSE STRETCHES (residual
        # R-P4-138, closed by the owner's ruling of 2026-09-04). The
        # bins a column leaves empty sit strictly INSIDE the stretch it
        # really leaves empty, so a twin repaired to a bin edge still
        # lands in the source's own gap. These two values are the gap
        # itself.
        "empty_edges": _empty_edges(numbers),
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
        # THE NUMBER THIS COLUMN HELD MOST OFTEN, and how many cells
        # held it (plan P4-D4.11, the owner's fifth numeric ask of
        # 2026-08-26: "the mode, for columns where one value
        # dominates").
        #
        # THE FLOOR GOVERNS THE COUNT AND NOT THE VALUE. An exact value
        # is not a new disclosure class on this role -- the ladder
        # already publishes eleven of them -- so what the floor is
        # asked about is the new fact, "this number was held by N
        # cells". Below the floor the PAIR is withheld whole rather
        # than the count alone, because a value published without its
        # count would say "this was the commonest number" and that is
        # the same fact in fewer words.
        #
        # A COLUMN WHOSE VALUES ARE ALL DIFFERENT HAS NO MODE WORTH THE
        # NAME, and publishing the smallest of three hundred ties would
        # be an arbitrary real value dressed as a statistic. Measured:
        # a 300-row continuous column's most frequent value was held by
        # one cell, and a laboratory column's by four. Two is the least
        # a mode can mean, and the floor is the other bound.
        **_mode_published(cells, cells.settings.small_cell_floor),
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
        "numeric_styles": styles_map,
        # ...and how many figures the ones written with a point wrote
        # after it, which the forms map cannot say (plan P4-D4.5,
        # amendments A-P4-5 and A-P4-6). It is a SIBLING of the forms
        # map and not a key inside it: version 4 requires every value of
        # that map to be an integer summing to the numeric count, so an
        # object among them is a document no loader can read.
        # THE MARK BETWEEN THOUSANDS, beside the other spelling
        # facts rather than inside the styles map, which is a
        # partition that must close on the numeric count
        # (amendment A-P4-5 set that precedent for the fraction
        # widths and this follows it).
        "group_separator": _group_separator(cells),
        # ...and how its negatives and its signed decimals were written
        # (landing 2b.2): the notation a negative wore, and how many
        # cells written with a point carried a plus. Siblings for the
        # reason the mark is one.
        "negative_form": _negative_form(cells),
        # ...and whether its WIDE runs of figures are their own values'
        # text (landing 2b.13, plan P4-D90). A sibling of the two above
        # for the reason they are siblings of the mark: it is a fact
        # about how the column was written, and the one the canonical
        # ceiling of a point-free cell past 2**53 is read against.
        "wide_runs": _wide_runs(cells, styles_map),
        # ...and the MIXTURE each of those two majority keys collapses
        # (landing 2b.7, plan P4-D65.2). A column writing 480 negatives
        # with a minus and 120 in brackets, or 200 cells grouped with a
        # space and 100 with a narrow no-break space, published one
        # convention and its twin wrote one convention, with every check
        # passing. These two censuses carry the mixture, floored per
        # convention, and the generator spends them cell by cell.
        "negative_notations": _negative_notations(cells),
        "thousands_marks": _thousands_marks(cells),
        "decimal_plus": _decimal_plus(cells, styles_map),
        "fraction_widths": _fraction_widths(cells, styles_map),
        # ...and how wide the ones written with a redundant zero wrote
        # their figure field, which the forms map cannot say either
        # (P4-D14). A SIBLING for the same reason: version 6 requires
        # every value of the forms map to be an integer summing to the
        # numeric count.
        "pad_widths": widths_pair[0],
        # ...and how wide EVERY whole-written cell wrote its figure
        # field, which neither of the other two censuses can say
        # (P4-D30, closing R-P4-30 and R-P4-35). The padded census
        # covers the cells wearing a redundant zero and the fraction
        # census the figures after a point; a cell written `199` is in
        # neither, so its width was published nowhere and a twin wrote
        # it at whatever width its drawn value needed. A SIBLING for
        # the reason both the others are.
        "field_widths": widths_pair[1],
    }
    moments = _moments(numbers)
    for key in sorted(moments):
        details[key] = moments[key]
    return details


def _offset_counts(
    pairs: list[tuple[str, str]], settings: Settings
) -> dict[str, int]:
    """How often each UTC offset appeared, held to the disclosure rule.

    The earlier revision reduced every offset in a column to the single
    word `mixed`, so a profile could not say that most rows were written
    in one zone and a handful in another (review item P1-R1-F9).

    AND NO COUNT IT PRINTS NAMES A ROW (plans P4-D220 and P4-D222). It
    named an offset where its count reached the settings floor, so at the
    then default floor of one a single row written at `+01:00` beside 399 at
    `Z` was published by name, and at a floor of eleven the pool beside
    `Z` was that one row. `parsing.absorbed_census` decides it now, over
    the values that read as a date, with the offsets as an open
    vocabulary: an offset fewer rows than `parsing.census_floor` carried
    is counted into the commonest named offset, and `_datetime_details`
    reads those rows as written at that offset.
    """
    counts: dict[str, int] = {}
    for _canonical, offset in pairs:
        key = offset if offset else "(none)"
        if key in counts:
            counts[key] = counts[key] + 1
        else:
            counts[key] = 1
    return parsing.absorbed_census(
        counts, len(pairs), settings.small_cell_floor, 0
    )


def _offsets_published(
    format_name: str,
    pairs: list[tuple[str, str]],
    sources: list[str],
    settings: Settings,
) -> "tuple[dict[str, int], list[tuple[str, str]]]":
    """The offset census and the pairs it describes, over the right population.

    THE POPULATION AN OFFSET CENSUS IS ABOUT (round 2 of the review,
    the disclosure pass, item 4). A whole DATE carries no offset and
    can carry none: on a joint ISO column its cells land under
    `(none)` because of what they are, not because of how anybody wrote
    them. `resolution_mix` publishes how many such cells there are, and
    its counts are exact -- so `(none)` less that number is the count of
    TIMESTAMPS written with no offset, and a floor applied to the whole
    column says nothing about it.

    **Measured** at a floor of eleven: 100 ISO dates, 299 timestamps at
    noon written with a trailing `Z`, and ONE noon timestamp written
    with no offset at all. `utc_offsets` published `{"(none)": 101,
    "Z": 299}` beside `resolution_mix {"iso-date": 100,
    "iso-datetime": 300}`, and 101 less 100 is one person's cell told
    from the 299 beside it. The description loaded and the source file
    validated with nothing missed.

    So ruling 6 is applied WHERE THE CONVENTION LIVES: the absorption
    that counts a rare offset into the commonest one is decided over
    the timestamps alone, those cells are read at the offset it gives
    them, and the census published afterwards counts every cell as the
    description now speaks of it -- the dates under `(none)`, each
    timestamp under the offset it was read at. The rare cell is then
    told apart by nothing, because nothing publishes it: the one
    unzoned timestamp above is read at `Z`, the map is `{"(none)": 100,
    "Z": 300}`, and `(none)` less the date-only cells is nought.

    A column that is not the joint reading, and a joint column with no
    date-only cell or no timestamp, has one population and this is the
    census it always was.

    Guarantees: accepts the format member, the parsed (canonical,
    offset) pairs, the source cells that parsed -- one per pair, in the
    same order -- and the settings; returns the published census and
    the pairs as that census speaks of them, in the order given.
    Determinism: a function of the four; every mapping is walked in
    sorted order. Raises nothing. No I/O of any kind.
    """
    dated = _date_only_places(format_name, pairs, sources)
    if not dated or len(dated) == len(pairs):
        offsets = _offset_counts(pairs, settings)
        return offsets, _offsets_as_published(pairs, offsets)
    stamped: "list[tuple[str, str]]" = []
    place = 0
    for canonical, offset in pairs:
        if place not in dated:
            stamped += [(canonical, offset)]
        place = place + 1
    named = _offset_counts(stamped, settings)
    if parsing.MISSING_WITHHELD in named:
        # NO OFFSET OF THE TIMESTAMPS REACHES THE LINE, so the census
        # names none of them and the column is read on the shared clock.
        # The pool then covers every parsed cell of the column: a map
        # that named `(none)` for the dates beside a pool would say the
        # rest wore something else, which is the reading the pool exists
        # to refuse.
        return {parsing.MISSING_WITHHELD: len(pairs)}, pairs
    written = _offsets_as_published(stamped, named)
    kept: "list[tuple[str, str]]" = []
    counts: "dict[str, int]" = {}
    taken = 0
    place = 0
    for canonical, offset in pairs:
        worn = offset
        if place not in dated:
            worn = written[taken][1]
            taken = taken + 1
        key = worn if worn else "(none)"
        counts[key] = (counts[key] if key in counts else 0) + 1
        kept += [(canonical, worn)]
        place = place + 1
    return counts, kept


def _date_only_places(
    format_name: str, pairs: list[tuple[str, str]], sources: list[str]
) -> "dict[int, int]":
    """Which places of a joint column hold a whole DATE and no clock.

    Empty for every reading but the joint one, and for a joint column
    whose cells all wrote a clock. The test is `_resolution_mix`'s own:
    a cell that parses as `iso-datetime` is a timestamp, and everything
    else the joint reading claimed is a date.

    Guarantees: accepts the format member, the parsed pairs and the
    source cells beside them; returns the places, as a mapping used as a
    set. Determinism: a function of the three. Raises nothing. No I/O.
    """
    places: "dict[int, int]" = {}
    if format_name != FORMAT_ISO_MIXED:
        return places
    if len(sources) != len(pairs):
        return places
    place = 0
    for value in sources:
        if parsing.parse_datetime(value, ISO_FORMS[1]) is None:
            places[place] = 1
        place = place + 1
    return places


def _offsets_as_published(
    pairs: list[tuple[str, str]], offsets: "dict[str, int]"
) -> list[tuple[str, str]]:
    """Each value's offset as the published census counts it (plan P4-D222).

    `parsing.absorbed_census` counts an offset below the line into the
    commonest named offset, so the description is that of the column with
    those rows written at it: the value keeps its own clock text and
    wears the commonest offset, and the clock the column is read on, its
    two ends and their offsets follow from that. Otherwise one `Z` among
    399 values at `+00:00` published the shared clock -- a column that
    wore two offsets -- beside a census naming one, which tells the rare
    offset from nought. A pooled census leaves every value as written.

    Guarantees: accepts the parsed pairs and the published census;
    returns pairs in the same order. Determinism: a function of the two.
    Raises nothing. No I/O of any kind.
    """
    commonest, _room = parsing.absorbed_room(offsets, 1)
    if not commonest:
        return pairs
    worn = "" if commonest == "(none)" else commonest
    kept: list[tuple[str, str]] = []
    for canonical, offset in pairs:
        key = offset if offset else "(none)"
        if key in offsets:
            kept += [(canonical, offset)]
        else:
            kept += [(canonical, worn)]
    return kept


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
    "dotted-two-digit-month-first-date",
)

# Both readings of the two-figure-year family, either of which leaves
# the century undecided by the cell.
_TWO_DIGIT_YEAR_MEMBERS = (
    "two-digit-month-first-date",
    "two-digit-day-first-date",
    # The dotted half of the same family (residual R-P4-4, landing
    # L18). It leaves the century undecided by the cell for exactly
    # the same reason, so it carries exactly the same sentence.
    "dotted-two-digit-month-first-date",
    "dotted-two-digit-day-first-date",
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
    ("dotted-two-digit-month-first-date",
     "dotted-two-digit-day-first-date"),
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
    """Which of these cells one reading parses.

    IT GREW ITS LIST THE COPYING WAY, and this module's own rule says
    not to: `answers = answers + [item]` copies everything accumulated
    so far, so the work grew as the SQUARE of the column's length --
    the very defect review item P1-R6-F10 fixed for the numeric path
    and wrote into this module's opening paragraph.

    IT WAS INVISIBLE UNTIL LANDING L18, and that is the part worth
    keeping. This function ran only under `--day-first`, which no
    growth test declares, so a quadratic walk sat in the tree
    unmeasured. Landing L18 made the column's own evidence decide
    whether or not anybody declared anything, which put this walk on
    every column that reaches the date pass -- and the growth guard
    that has watched the numeric path since P1-R6-F10 turned red at
    once, measuring 14.4 times the work for four times the values
    where proportional growth is about 4.
    """
    answers: list[bool] = []
    for value in present:
        answers += [parsing.parse_datetime(value, format_name) is not None]
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

    AND A SLASHED PAIR IS READ HERE THE WAY THE CLASSIFIER READS IT
    (plan P4-D251, the extra review of c5d09d5, item 2): the column's
    own evidence first and the declaration as the tie-break, exactly
    `_matching_date_format`'s own two lines. This walked the format
    table alone, so the member standing first won by ORDER while the
    description that followed was written in the other one. Measured on
    the reviewer's shape: `01/01/1900` twenty times beside `12/01/1900`,
    `12/02/1900` and `12/03/1900` at 125, 125 and 130, declared day
    first at a floor of eleven. Judging read the three reference days
    MONTH first, as December 1 to 3, so the twenty January dates sat
    eleven months adrift, were judged outliers and were removed; the
    description was then written day first over what was left and
    published 380 present, 20 missing and an earliest of `1900-01-12`.
    Judged in the declared reading the four days span January 1 to
    March 12 and all 400 values stand, which is what the column holds.

    Guarantees: accepts the present cells and the settings; returns a
    format member or None. Determinism: a function of the two, in the
    format table's own order. Raises nothing. No I/O of any kind.
    """
    for format_name in parsing.DATE_FORMATS:
        reading = format_name
        for pair in SLASHED_PAIRS:
            if format_name != pair[0]:
                continue
            weighed = _slashed_evidence(present, pair, settings.day_first)
            if settings.day_first or weighed.day_parsed > weighed.month_parsed:
                reading = weighed.used
        remainder: list[str] = []
        placeholders = 0
        for value in present:
            if parsing.placeholder_day_of(value, reading) is not None:
                placeholders = placeholders + 1
                continue
            remainder += [value]
        if placeholders < 1:
            continue
        needed = _needed(settings.minimum_parse_rate, len(remainder))
        parsed = 0
        for value in remainder:
            if parsing.parse_datetime(value, reading) is not None:
                parsed = parsed + 1
        if parsed >= needed and parsed:
            return reading
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
    # A DOTTED TRIPLE NAMING A ZERO FIELD IS A VERSION SAYING SO
    # (review round 1 of landing L18, item 2). It is worked out once
    # for the column rather than per format, because it is a fact about
    # the column and not about a reading.
    contradicted = False
    for value in present:
        if parsing.names_a_zero_field(value):
            contradicted = True
            break
    for format_name in parsing.DATE_FORMATS:
        # THE GUARD IS THE NEW FAMILY'S ALONE, and that bound is
        # deliberate. This landing gave the two-figure dotted spelling
        # its first reader, so a column of `01.00.24` firmware moved
        # from a set of categories to dates and back is a regression
        # this landing owes. The FOUR-figure dotted family has admitted
        # `01.00.2024` since P4-D15 and the slashed pair since before
        # that; widening the guard to them would move columns that have
        # read one way for weeks, which is a change to make on its own
        # evidence rather than inside a repair. Carried as a residual.
        if contradicted and format_name in (
            "dotted-two-digit-month-first-date",
            "dotted-two-digit-day-first-date",
        ):
            continue
        evidence: "_SlashedEvidence | None" = None
        reading = format_name
        # THE COLUMN'S OWN EVIDENCE IS READ WHETHER OR NOT ANYBODY
        # DECLARED ANYTHING (review round 1 of landing L18, item 1).
        # `_slashed_evidence` has said since it was written that the
        # reading parsing strictly more cells wins "whatever the person
        # said", and this caller asked it only under `--day-first` --
        # so undeclared, the member standing first in the format table
        # won by ORDER and the column's own values were never counted.
        #
        # Measured on all four shipped pairs and the one this landing
        # adds: 299 cells both readings accept beside ONE that only a
        # day-first reading accepts came out month-first with that cell
        # reported unparsed, on every family. The column had settled the
        # question and the tool overruled it with a default.
        #
        # UNDECLARED, IT REACHES EXACTLY THE CASE THE ORDER GETS WRONG,
        # and no other. Where month-first parses at least as many, the
        # format table's own order already picks month-first and there
        # is nothing to correct. Where DAY-first parses strictly more,
        # the order picks the worse reading and this overrides it.
        #
        # THAT BOUND IS THE SENTENCE'S AS WELL AS THE READING'S, which
        # is why it is drawn here rather than around the whole
        # comparison. Contract NF36 gives the evidence remark three
        # renderings and only ONE of them is true of a column nobody
        # declared: "read day first, which parses N of these values
        # against the month-first reading's M". The other two say
        # "though you asked for day first" and "because you asked for
        # it", and a first writing of this repair put those words on
        # columns whose owner had asked for nothing. A sentence that
        # makes up a declaration is worse than the reading it stands
        # beside.
        for pair in SLASHED_PAIRS:
            if format_name != pair[0]:
                continue
            weighed = _slashed_evidence(present, pair, settings.day_first)
            if settings.day_first or weighed.day_parsed > weighed.month_parsed:
                evidence = weighed
                reading = weighed.used
        good: list[tuple[str, str]] = []
        sources: list[str] = []
        for value in present:
            pair_read = parsing.parse_datetime(value, reading)
            if pair_read is not None:
                good += [pair_read]
                sources += [value]
        if len(good) >= needed and good:
            # THE FORMS AS PUBLISHED, BEFORE ANY FACT IS TAKEN FROM
            # THEM (plan P4-D250): a cell whose FORM the census counts
            # into the commonest form is read in that form by
            # everything below -- the evidence sentence, the remarks
            # and every field of the description alike -- so no
            # published fact tells it apart.
            reading, good, sources = _forms_as_published(
                reading, good, sources, settings
            )
            return reading, good, sources, len(present) - len(good), evidence
    return None


def _forms_as_published(
    format_name: str,
    pairs: "list[tuple[str, str]]",
    sources: "list[str]",
    settings: Settings,
) -> "tuple[str, list[tuple[str, str]], list[str]]":
    """The joint ISO reading's two forms, held to the disclosure rule (P4-D250).

    THE CENSUS OF FORMS NAMED ONE ROW (the extra review of c5d09d5, item
    1). `resolution_mix` published its two counts exactly, on the reading
    that a two-member space beside the published parsed total makes a
    pooled remainder recoverable by subtraction -- true, and beside the
    point, because the count itself is the disclosure. Measured on the
    reviewer's own shape: 118 consecutive ISO dates, one
    `2024-07-01T00:00:00` and one unreadable word at a floor of eleven
    published `resolution_mix={"iso-date": 118, "iso-datetime": 1}` and
    `datetime_separators={"(withheld)": 1}`, and the second census
    pooled a count of one, which pools nothing. A form held by one row
    describes how THAT row was written, exactly as a spelling held by
    one row does.

    So the forms ask `parsing.absorbed_census` with the line
    `parsing.census_floor`, as every other census of how a column was
    written does (owner ruling 6 of 2026-09-17, plans P4-D222 and
    P4-D242): a form below the line is counted into the commonest form,
    and the column is then published WHOLLY in that form -- its cells
    rewritten in it, its reading named as it, its resolution, precision
    and mark census following from the rewritten cells. Jointly, because
    the dependent counts are what subtraction reaches: publishing the
    mix alone would leave the mark census owing the absorbed cells'
    marks, and publishing the mark census alone would leave the mix
    naming them.

    A date rewritten as a moment stands at the midnight it already named,
    under the mark most of the column's moments wrote; a moment rewritten
    as a date loses its time of day, which is ruling 6's own cost and is
    the same cost a rare spelling meets everywhere else. Where BOTH forms
    reach the line nothing moves, so a column holding both in numbers the
    rule can name is described exactly as before.

    Guarantees: accepts the chosen reading, its parsed (canonical,
    offset) pairs, the source cells that parsed and the settings;
    returns a reading, pairs and cells of the same length, unchanged
    for every reading but the joint one. Determinism: a function of the
    four. Raises nothing. No I/O of any kind.
    """
    if format_name != FORMAT_ISO_MIXED or not sources:
        return format_name, pairs, sources
    counts = _resolution_mix(FORMAT_ISO_MIXED, sources)
    published = parsing.absorbed_census(
        counts, len(sources), settings.small_cell_floor, len(ISO_FORMS)
    )
    kept = ""
    named = 0
    for name in sorted(published):
        if name == parsing.MISSING_WITHHELD:
            continue
        named = named + 1
        kept = name
    if named == len(ISO_FORMS):
        return format_name, pairs, sources
    if not kept:
        # A POOL NAMES NO FORM, and a description naming no reading
        # describes no column at all, so the commonest form the cells
        # wrote stands -- exactly as `absorbed_census` itself writes it
        # where a closed vocabulary refuses the pool (plan P4-D242).
        for name in sorted(counts):
            if not kept or counts[name] > counts[kept]:
                kept = name
    mark = parsing.SEPARATOR_MARKS[_commonest_mark(sources)]
    written: "list[str]" = []
    rewritten: "list[tuple[str, str]]" = []
    for value in sources:
        text = _written_in_form(value, kept, mark)
        again = parsing.parse_datetime(text, kept)
        if again is None:
            return format_name, pairs, sources
        written += [text]
        rewritten += [again]
    return kept, rewritten, written


def _commonest_mark(sources: "list[str]") -> str:
    """The mark between day and clock most of these moments wrote (P4-D250).

    Ties to the first in sorted order, as `parsing.absorbed_census`
    breaks them, so a cell rewritten as a moment wears the mark that
    census names. `parsing.SEPARATOR_UPPER_T` stands where no cell wrote
    a clock, which is the vocabulary's own default name.

    Guarantees: accepts the source cells; returns a member of
    `parsing.DATETIME_SEPARATORS`. Determinism: a function of the cells.
    Raises nothing. No I/O of any kind.
    """
    counts: "dict[str, int]" = {}
    for value in sources:
        name = parsing.datetime_separator(value, FORMAT_ISO_MIXED)
        if name is None:
            continue
        if name in counts:
            counts[name] = counts[name] + 1
        else:
            counts[name] = 1
    commonest = ""
    for name in sorted(counts):
        if not commonest or counts[name] > counts[commonest]:
            commonest = name
    if not commonest:
        return parsing.SEPARATOR_UPPER_T
    return commonest


def _written_in_form(value: str, form: str, mark: str) -> str:
    """One cell of a joint ISO column, written in the form published (P4-D250).

    A cell already in that form is handed back UNCHANGED, character for
    character, so nothing about the cells the census names moves. The
    other form's cells are rewritten: an ISO moment keeps its first ten
    characters, its day, and an ISO date gains the mark and the midnight
    it already named.

    Guarantees: accepts one source cell, the form the column publishes
    and the mark its moments wear; returns a cell that reads under that
    form wherever the original read under either ISO member.
    Determinism: a function of the three. Raises nothing. No I/O.
    """
    if parsing.parse_datetime(value, form) is not None:
        return value
    body = parsing.trimmed(value)
    if form == ISO_FORMS[0]:
        return body[0:10]
    return body[0:10] + mark + "00:00:00"


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
    # THE OFFSETS AS PUBLISHED, FIRST (plan P4-D222): a value whose offset
    # the census counts into the commonest one is read at that offset by
    # everything below, so no published fact tells it apart.
    offsets, pairs = _offsets_published(
        format_name, pairs, sources, settings
    )
    reading = _datetime_reading(pairs)
    # AND A CENSUS HELD BACK WHOLE SAYS NOT EVEN WHETHER THE COLUMN WORE ONE
    # OFFSET (plan P4-D222). The local clock is published where every value
    # shares an offset, so beside a pool it told a column of eight values
    # at `+01:00` from the same column with one of them at `Z`; the shared
    # clock stands beside every pool of a reading that takes an offset.
    if (
        parsing.MISSING_WITHHELD in offsets
        and format_name not in parsing.SLASHED_STAMPS
    ):
        reading = READ_AT_UTC
    placed = ordered_moments(pairs, reading)
    canonical_order = placed[0]
    earliest = placed[1]
    latest = placed[2]
    earliest_offset = placed[3]
    latest_offset = placed[4]
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
    if format_name == "slashed-iso-datetime":
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
        "datetime_separators": _separator_counts(sources, format_name, settings),
        # HOW THE CELLS WERE WRITTEN, beside what they were read as
        # (landing 2b.6). Four censuses of FORMS, each floored exactly as
        # the marks beside them are, so that the twin can be written in
        # the source's own spelling instead of in ISO.
        "date_field_widths": _width_counts(sources, format_name, settings),
        "month_name_styles": _name_style_counts(sources, format_name, settings),
        "quarter_marker_case": _marker_counts(sources, format_name, settings),
        "zulu_case": _zulu_counts(sources, format_name, offsets, settings),
        "all_at_midnight": _all_at_midnight(
            format_name, resolution, reading, sources, offsets, settings
        ),
        "n_at_midnight": _midnight_count(
            format_name, resolution, reading, sources, offsets, settings
        ),
    }


def _floored_census(
    counts: "dict[str, int]", population: int, settings: Settings
) -> "dict[str, int]":
    """One census of written forms, held to the disclosure rule (P4-D131).

    `parsing.disclosed_census` exactly, written once for the four
    censuses landing 2b.6 added and asked of each with the total the
    document already publishes for the cells it counts over.

    WHAT IT REPLACES AND WHY (review of 158c811, item 1). This census
    used to take `_offset_counts`' rule: a name published where its count
    reached the smallest group size, the rest pooled under `(withheld)`.
    At the then default size of one that published a count of one outright,
    and at any size it pooled into a key that named the one form left:
    400 moments at noon, one of them written with a lower-case `z`,
    published `{"lower": 1, "upper": 399}` by default and
    `{"upper": 399, "(withheld)": 1}` at a floor of eleven, and both
    descriptions loaded. A form held by one row describes how THAT row
    was written.

    Guarantees: accepts a tally, the published total it counts over and
    the run's settings; returns the published census. Determinism: a
    function of the three. Raises nothing. No I/O of any kind.
    """
    return parsing.disclosed_census(
        counts, population, settings.small_cell_floor
    )


def width_tally(sources: "list[str]", format_name: str) -> "dict[str, int]":
    """How many cells wrote each width word, before any floor (2b.6, P4-D132).

    Counted over the cells that could SHOW one -- a field below ten --
    and NOT folded; `parsing.folded_width_tally` folds it. The validator
    asks this of a file's own cells, so the producer and the checker
    count one way.
    """
    counts: "dict[str, int]" = {}
    for value in sources:
        name = parsing.date_field_style(value, format_name)
        if name is None:
            continue
        if name in counts:
            counts[name] = counts[name] + 1
        else:
            counts[name] = 1
    return counts


def name_style_tally(sources: "list[str]", format_name: str) -> "dict[str, int]":
    """How many cells wrote each month-name style, before any floor (2b.6).

    NOT folded; `parsing.folded_name_tally` folds a name of May into the
    length its column's other cells wrote. A spelling outside the three
    cases is counted under no key.
    """
    counts: "dict[str, int]" = {}
    for value in sources:
        name = parsing.month_name_style(value, format_name)
        if name is None:
            continue
        if name in counts:
            counts[name] = counts[name] + 1
        else:
            counts[name] = 1
    return counts


def _width_counts(
    sources: "list[str]", format_name: str, settings: Settings
) -> "dict[str, int]":
    """How many parsed cells wrote each width convention (2b.6, P4-D139).

    Counted over the cells that could SHOW one -- a field below ten --
    so a column of dates every one of which falls after the ninth of a
    month above September publishes an empty census, honestly: nothing
    in it says how it would have written a single figure.

    A CELL THAT COULD SHOW NO WIDTH IS COUNTED INTO THE COMMONEST WIDTH,
    and the census is then held against every parsed cell (plan P4-D278,
    the repair of the extra review round of 2026-09-18). The remainder
    used to be counted against the cells that COULD show a width, which
    no field of the block publishes -- and a reader holds the parsed
    total, `n_present` less `n_unparsed`, so they subtract from that one
    instead. **Measured** at a floor of eleven, on 399 dates written
    `1/1/2000` through `1/9/2044` beside one `12/25/2020`: the census
    published `{"unpadded": 399}` against 400 parsed cells, and the one
    left over is the record whose month and day are both two figures.

    THE ABSORPTION COSTS NOTHING, which is why it is taken instead of
    the silence plan P4-D139 measured. A date both of whose fields are
    ten or more is written IDENTICALLY under either convention, so
    counting it under the column's commonest one is a true statement
    about that cell and the twin writes it the same way either way.
    P4-D139 withheld the whole census instead, and a single `12/25/2019`
    among 244 dates written `m/d/yyyy` then left 212 of the twin's 245
    cells written `04/14/2020`; counted in, the census says
    `{"m/d": 245}` and the twin writes the column's own convention.
    Ties for the commonest go to the first in sorted order, which is
    `parsing.absorbed_census`' own tie rule. One-field counts are folded
    into the joint words first (`parsing.folded_width_tally`).
    """
    counts = absorbed_width_tally(
        parsing.folded_width_tally(width_tally(sources, format_name)),
        len(sources),
    )
    shown = 0
    for name in counts:
        shown = shown + counts[name]
    return _floored_census(counts, shown, settings)


def absorbed_width_tally(
    tally: "dict[str, int]", parsed: int
) -> "dict[str, int]":
    """A width tally with the cells showing no width counted into the commonest.

    THE ONE STATEMENT OF THE ABSORPTION `_width_counts` above sets out
    (plan P4-D278), read by the producer and by the checker so the two
    cannot part. A date both of whose fields are ten or more is written
    identically under either convention, so counting it under the
    column's commonest one is true of it. Ties go to the first name in
    sorted order. A tally naming nothing is handed back unchanged: there
    is no commonest convention to count them into.

    Guarantees: accepts a folded width tally and how many cells parsed;
    returns a tally over the same names, summing to the parsed cells
    wherever it names one. Determinism: a fixed function of the two,
    walked in sorted order. Raises nothing. No I/O of any kind.
    """
    shown = 0
    commonest = ""
    for name in sorted(tally):
        shown = shown + tally[name]
        if not commonest or tally[name] > tally[commonest]:
            commonest = name
    absorbed: "dict[str, int]" = {}
    for name in sorted(tally):
        absorbed[name] = tally[name]
    if commonest and parsed > shown:
        absorbed[commonest] = absorbed[commonest] + (parsed - shown)
    return absorbed


def _name_style_counts(
    sources: "list[str]", format_name: str, settings: Settings
) -> "dict[str, int]":
    """How many parsed cells wrote each joint month-name style (2b.6).

    A cell whose month is MAY shows no length and is folded into the
    style of the same case, mark and comma its column's other cells
    wrote (`parsing.folded_name_tally`, plan P4-D139); it keeps its
    `either` word only where no other cell wrote those three.
    """
    counts = parsing.folded_name_tally(name_style_tally(sources, format_name))
    return _floored_census(counts, len(sources), settings)


def _marker_counts(
    sources: "list[str]", format_name: str, settings: Settings
) -> "dict[str, int]":
    """How many quarter cells wrote `Q` and how many wrote `q` (2b.6)."""
    counts: "dict[str, int]" = {}
    for value in sources:
        name = parsing.quarter_marker_case(value, format_name)
        if name is None:
            continue
        if name in counts:
            counts[name] = counts[name] + 1
        else:
            counts[name] = 1
    return _floored_census(counts, len(sources), settings)


def _zulu_counts(
    sources: "list[str]",
    format_name: str,
    offsets: "dict[str, int]",
    settings: Settings,
) -> "dict[str, int]":
    """How many zulu-marked cells wrote `Z` and how many wrote `z` (2b.6).

    EMPTY WHERE THE OFFSET MAP DOES NOT NAME `Z`. The case census counts
    a subset of the cells carrying one offset, so publishing it beside a
    pooled offset would hand back the count the pool exists to withhold
    -- the contradiction review item P1-R1-F10 found for the endpoint
    offsets, met again here.
    """
    if "Z" not in offsets:
        return {}
    counts: "dict[str, int]" = {}
    worn = 0
    for value in sources:
        name = parsing.zulu_case(value, format_name)
        if name is None:
            continue
        worn = worn + 1
        if name in counts:
            counts[name] = counts[name] + 1
        else:
            counts[name] = 1
    # THE VALUES THE OFFSET CENSUS COUNTED INTO `Z` (plan P4-D222) are
    # read as written at it, in the case most `Z` cells wrote, so what the
    # named cases leave of the published `Z` count is what they leave of
    # the column that description describes.
    commonest = ""
    for name in sorted(counts):
        if not commonest or counts[name] > counts[commonest]:
            commonest = name
    if commonest and offsets["Z"] > worn:
        counts[commonest] = counts[commonest] + offsets["Z"] - worn
    return _floored_census(counts, offsets["Z"], settings)


def _separator_counts(
    sources: "list[str]", format_name: str, settings: Settings
) -> "dict[str, int]":
    """How many parsed cells wore each mark between day and clock (P4-D39).

    A cell that writes no clock is not counted, so the map is empty on a
    column of dates, months or quarters, and on an `iso-mixed` column it
    covers only the cells that wrote one.

    A POOL HERE IS NEVER A COUNT OF ONE, and that rests on the reading
    rather than on a rule of this census (`_forms_as_published`, plan
    P4-D250). The population it counts over is the cells that wrote a
    clock, which on a joint column is `resolution_mix`'s own moment
    count; a joint column whose moments fall below the line is read as a
    column of DATES instead, so the population reaching this is nought
    or at least the line. **Measured** before that: 395 ISO dates beside
    one `2020-05-03T00:00:00` published `{"(withheld)": 1}`, a pool whose
    whole size is that one record.

    HELD TO THE DISCLOSURE RULE (plan P4-D220). It took `_offset_counts`'
    old rule -- a name published where its count reached the settings
    floor, the rest pooled -- so 400 moments with one `t` published
    `{"lower_t": 1, "upper_t": 399}` at the default floor and
    `{"upper_t": 399, "(withheld)": 1}` at eleven. `parsing.absorbed_census`
    decides it now (plan P4-D222), over the cells that write a clock, with
    the marks as the closed vocabulary they are: a mark below the line is
    counted into the commonest, and where none reaches it the census pools
    the whole of it, or names `upper_t` where a pool would say every mark
    was written.

    Guarantees: accepts the cells that parsed, their format member and
    the run's settings; returns a mapping of `parsing.DATETIME_SEPARATORS`
    members, or `(withheld)` alone, to counts. Determinism: a function of
    the three. Raises nothing. No I/O of any kind.
    """
    counts: dict[str, int] = {}
    clocks = 0
    for value in sources:
        name = parsing.datetime_separator(value, format_name)
        if name is None:
            continue
        clocks = clocks + 1
        if name in counts:
            counts[name] = counts[name] + 1
        else:
            counts[name] = 1
    return parsing.absorbed_census(
        counts,
        clocks,
        settings.small_cell_floor,
        parsing.separator_names(format_name),
        parsing.SEPARATOR_UPPER_T,
    )


def _all_at_midnight(
    format_name: str,
    resolution: str,
    reading: str,
    sources: "list[str]",
    offsets: "dict[str, int]",
    settings: Settings,
) -> bool:
    """Whether every parsed cell of a column of moments stands at midnight.

    The warehouse spelling of a date with no time is the date plus
    `00:00:00`, and without this fact the twin invents a time of day
    for every row (plan P4-D39). Exactly where `_midnight_count` counts
    every parsed cell, so the statement and the count cannot disagree:
    asked of the LOCAL cell text, on either clock, and only where the
    parsed cells reach the smallest group size.

    Guarantees: accepts the column's format member, resolution, clock,
    parsed cells, published offset map and settings; returns a bool.
    Determinism: a function of the six. Raises nothing. No I/O of any kind.
    """
    counted = _midnight_count(
        format_name, resolution, reading, sources, offsets, settings
    )
    return counted is not None and counted == len(sources)


def _midnight_count(
    format_name: str,
    resolution: str,
    reading: str,
    sources: "list[str]",
    offsets: "dict[str, int]",
    settings: Settings,
) -> "int | None":
    """How many parsed cells of a column of moments stand at midnight.

    A column only PARTLY at midnight -- a date stored as the date plus
    `00:00:00` beside rows that kept a time of day, or 999 values at midnight and
    one stray `14:30` -- published nothing about it, so its twin invented
    a time for nearly every row: 361 real values at midnight of 400 came back as
    2 (landing 2b.3). A count is published instead, floored on BOTH
    sides: at least the smallest group size stood at midnight and at
    least that many did not, or every parsed cell did and the parsed
    cells reach it.

    THE FLOOR ON EITHER SIDE IS NEVER BELOW TWO, AND WHAT IS NOT
    PUBLISHED IS `None` RATHER THAN NOUGHT (landing 2b.6, the owner's
    twin definition clause 3). Measured on the reviewer's own shape: 400
    moments a day apart at noon, described twice, the second time with
    zero-based row 31 moved to midnight. Both documents loaded, and the
    ONLY difference between them anywhere was `n_at_midnight: 0 -> 1`, so
    a reader holding the other 399 values learned that row's time of day.
    A count of one names one person, and so does a count leaving exactly
    one off midnight, which is why `parsing.MIDNIGHT_DISCLOSURE_FLOOR`
    bounds both sides.

    Nought had been this field's own word for "nothing is published", and
    that is what made the singleton visible: suppressing a count of one
    into a nought a reader can tell from a real nought suppresses
    nothing. So the two are ONE state now -- the count is absent, written
    `null` -- and a genuine nought is not published either. The cost is
    named rather than hidden: a column no value of which stood at
    midnight publishes no count, so its twin is held to none (the
    move-off rule of landing 2b.3's repair pass is withdrawn with the
    nought that bought it) and the quality report lists the field instead
    of checking it.

    Asked of each cell's LOCAL text, as `parsing.clock_at_midnight`
    answers it: a whole date of an `iso-mixed` column counts, and a
    fraction of zeros does. ON THE SHARED CLOCK TOO (landing 2b.3): a
    CET export writes `T00:00:00+01:00` in winter and `+02:00` in
    summer, every cell a local midnight, and the column is published on
    the shared clock only because it wore two offsets. Every published
    instant is then a local midnight under an offset the map names, which
    is what lets a twin write it back. Where the map pools an offset
    under `(withheld)` that is not so -- a pooled offset is written with
    none -- and the count is `0`.

    Guarantees: accepts the column's format member, resolution, clock,
    parsed cells, published offset map and settings; returns a count.
    Determinism: a function of the six. Raises nothing. No I/O of any kind.
    """
    if resolution != RESOLUTION_DATETIME or len(sources) == 0:
        return None
    if reading != READ_AT_LOCAL and parsing.MISSING_WITHHELD in offsets:
        return None
    counted = 0
    for value in sources:
        if parsing.clock_at_midnight(value, format_name):
            counted = counted + 1
    floor = parsing.census_floor(settings.small_cell_floor)
    if not _joint_midnight_nameable(format_name, sources, floor):
        return None
    if counted == len(sources):
        return counted if counted >= floor else None
    if counted >= floor and len(sources) - counted >= floor:
        return counted
    return None


def _joint_midnight_nameable(
    format_name: str, sources: "list[str]", floor: int
) -> bool:
    """Whether the TIMESTAMP half of a joint column may carry the count.

    THE TOTAL A READER SUBTRACTS FROM `n_at_midnight` (round 2 of the
    review, the disclosure pass, item 4). A joint ISO column publishes
    `resolution_mix`, whose counts are EXACT by construction, and a
    whole date of such a column stands at midnight by definition -- so
    `n_at_midnight` less the date-only cells is the count of TIMESTAMPS
    at midnight, and the floor on either side of the whole column says
    nothing about either side of that residual.

    **Measured** at a floor of eleven: 100 ISO dates, 299 timestamps at
    noon and ONE timestamp at midnight published `resolution_mix
    {"iso-date": 100, "iso-datetime": 300}` beside `n_at_midnight` 101.
    Both sides of 101 against 400 clear eleven, and 101 less 100 is one
    person's time of day. The description loaded and the source file
    validated with nothing missed.

    So the residual is held to the same floor on both sides, and where
    it is not the count is not published at all -- the field's one
    silence, written `null`, which is what `_midnight_count` above does
    for every other reason it cannot speak.

    A column that is not the joint reading has no such residual: every
    cell of it carries a clock, or none does, and the answer is True.

    Guarantees: accepts the column's format member, its parsed cells
    and the census floor; returns a bool. Determinism: a fixed function
    of the three. Raises nothing. No I/O of any kind.
    """
    if format_name != FORMAT_ISO_MIXED:
        return True
    stamped = 0
    at_midnight = 0
    for value in sources:
        if parsing.parse_datetime(value, ISO_FORMS[1]) is None:
            continue
        stamped = stamped + 1
        if parsing.clock_at_midnight(value, format_name):
            at_midnight = at_midnight + 1
    if at_midnight == stamped or at_midnight == 0:
        return True
    return at_midnight >= floor and stamped - at_midnight >= floor


# The joint ISO reading's own name, used where a rule has to tell it
# from the two members it joins.
FORMAT_ISO_MIXED = "iso-mixed"

# ...and the two members themselves, in the format table's own order,
# read as the closed vocabulary the form census is held to (P4-D250).
# The loader states the same pair as `contract.ISO_MEMBERS`, which is
# where a document's key set is checked against it.
ISO_FORMS = ("iso-date", "iso-datetime")


def _resolution_mix(
    format_name: str, sources: "list[str]"
) -> "dict[str, int]":
    """How many parsed cells of this column wore each form (C6-25).

    ONE KEY ON A SINGLE-FORMAT COLUMN -- its own form, carrying every
    cell that parsed -- and exactly the two ISO members on a column the
    joint reading claimed. No other key set conforms, and the counts
    it publishes are exact.

    THE FLOOR IS ASKED BEFORE THIS FUNCTION IS REACHED, not here (plan
    P4-D250). The text that stood in this docstring said a floor would
    withhold nothing, because a two-member space beside the published
    parsed total makes a pooled remainder recoverable by subtraction.
    The arithmetic was right and the conclusion was wrong: the answer
    is not to pool the rare form but to ABSORB it, so
    `_forms_as_published` counts a form below `parsing.census_floor`
    into the commonest form and publishes the column wholly in that
    form. By the time this counts anything, either both forms reach the
    line or only one form is left, and the exact counts name no row.

    THE COUNTS ARE EXACT AND NO FLOOR GOVERNS THEM, and that is safe
    only because NEITHER MEMBER CAN BE BELOW THE LINE HERE
    (`_forms_as_published`, plan P4-D250). A two-member space beside
    the published parsed total makes a pooled remainder recoverable by
    subtraction, so a floor applied at this point would withhold
    nothing -- which is why a column of 395 ISO dates and ONE moment
    published `{"iso-date": 395, "iso-datetime": 1}` and named that one
    record. The reading is settled before this is asked: a joint column
    whose one form is below the line is read under the OTHER form, and
    what this counts is therefore two groups each at the line or above.

    Guarantees: accepts a format member and the source cells that parsed
    under it; returns a mapping whose values sum to how many there were.
    Determinism: a function of the two, with the keys built in the format
    table's own order. Raises nothing. No I/O of any kind.
    """
    if format_name != FORMAT_ISO_MIXED:
        return {format_name: len(sources)}
    counted = {ISO_FORMS[0]: 0, ISO_FORMS[1]: 0}
    for value in sources:
        if parsing.parse_datetime(value, ISO_FORMS[1]) is not None:
            counted[ISO_FORMS[1]] = counted[ISO_FORMS[1]] + 1
            continue
        counted[ISO_FORMS[0]] = counted[ISO_FORMS[0]] + 1
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


def ordered_moments(
    pairs: "list[tuple[str, str]]", reading: str
) -> "tuple[list[str], str, str, str, str]":
    """These parsed moments in the order a description publishes them.

    THE ONE STATEMENT OF THE ORDER AND OF ITS TIE RULE (plan P4-D255).
    The cells are ordered by the INSTANT each names -- not by its local
    text, which sorted two offsets the wrong way round (review item
    P1-R1-F9) -- then by the text published for it, then by the offset
    it wears. So where several cells share an end's instant, the offset
    published for that end is the LARGEST of theirs at the latest and
    the SMALLEST at the earliest, and that is a rule the generator has
    to meet rather than guess at: `generation._endpoint_offset_notes`
    recounts the twin through this same function, and
    `generation._endpoint_tie_offsets` holds every tied rank to it.

    Guarantees: accepts the parsed (canonical, offset) pairs -- at least
    one -- and the clock they are published on; returns the canonical
    texts in order, the first and last of them, and the offsets those
    two wear. Determinism: a function of the two. Raises nothing. No I/O
    of any kind.
    """
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
        return (
            canonical_order,
            ordered[0][1],
            ordered[len(ordered) - 1][1],
            ordered[0][2],
            ordered[len(ordered) - 1][2],
        )
    canonical_order = sorted(unkeyed)
    return (
        canonical_order,
        canonical_order[0],
        canonical_order[len(canonical_order) - 1],
        "",
        "",
    )


def _named_offset(offset: str, published_offsets: dict[str, int]) -> str:
    """One endpoint's UTC offset, named only if the floor let it be named.

    Beside a census held back whole the endpoint is held back too, `(none)`
    included (plan P4-D222): a pool of offsets says no value's offset, and
    `(none)` beside it told a naive end from a zoned one.
    """
    if parsing.MISSING_WITHHELD in published_offsets:
        return parsing.MISSING_WITHHELD
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
            parts += [current]
            current = ""
            at = at + len(separator)
            continue
        current = current + text[at]
        at = at + 1
    parts += [current]
    if len(parts) < 2:
        return None
    for part in parts:
        if not _reads_as_one_number(part):
            return None
    return parts


def _reads_as_a_plain_whole(text: str) -> bool:
    """Whether one part of a cell is figures alone, with no leading zero.

    The part shape rule 9c reads from the values (plan P4-D40): no
    point, no sign, and no padding. A padded part (`007`) is how a code
    is written far more often than a measurement, and a part with a
    point is a ratio the declaration reads and this rule leaves alone.
    Figures are tested against fixed ASCII for the reason
    `_reads_as_one_number` gives.
    """
    if not text:
        return False
    for character in text:
        if not ("0" <= character <= "9"):
            return False
    if len(text) > 1 and text[0] == "0":
        return False
    # AND THE FIGURES MUST BE A NUMBER THIS FORMAT CAN HOLD. Spelling is
    # not representability: `10**310` is figures alone with no padding,
    # and every statistic over it is taken on a value binary64 cannot
    # carry. Admitted on its spelling, a column of such pairs described
    # a position whose statistics used none of its cells while
    # `n_joined` counted them all, and the loader then refused the
    # description under invariant Q2 -- so `synthtwin profile` wrote a
    # file `synthtwin generate` would not read. A part that is not
    # representable leaves the cell unparsed, and the parse line of
    # `_joined_reading` decides the column as it does for every other
    # cell it cannot read.
    if not math.isfinite(float(text)):
        return False
    return True


def _split_for_reading(
    value: str, separator: str, plain_pair: bool
) -> "list[str] | None":
    """The parts of one cell under one separator for one reading, or None.

    Under the declaration every split `splits_into_numbers` accepts is
    read. Under rule 9c only a PAIR of plain whole numbers is, and any
    other cell is left unparsed.
    """
    split = splits_into_numbers(value, separator)
    if split is None or not plain_pair:
        return split
    if len(split) != 2:
        return None
    for part in split:
        if not _reads_as_a_plain_whole(part):
            return None
    return split


def _joined_reading(
    cells: _Cells, plain_pair: bool = False
) -> "_Joined | None":
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

    ONE SHAPE IS READ WITHOUT IT, and ``plain_pair`` asks for it (plan
    P4-D40, 2026-09-15, which narrows P4-D21). A column every other rule
    declined, whose cells are TWO plain whole numbers joined by a slash
    -- `128/79`, `120 / 80` -- is read here from its values. It wears
    none of the shapes the measurement above found: a date or a clock
    is claimed by an earlier rule, and the codes it names are joined by
    a hyphen and padded. Such a column was free text, which publishes
    nothing, so its twin held stand-in text where a blood pressure was;
    the question the questions file puts is still put, with `code` and
    `identifier` offered beside the reading taken.
    """
    present = cells.present
    n_present = len(present)
    if n_present == 0:
        return None
    needed = _needed(cells.settings.minimum_parse_rate, n_present)
    tried: "list[str]" = []
    for mark in JOINED_SEPARATORS:
        if plain_pair and mark != "/":
            continue
        for spacing in range(len(JOINED_SPACINGS)):
            tried += [
                JOINED_SPACINGS[spacing] + mark + JOINED_TAILINGS[spacing]
            ]
    for separator in tried:
        counted: "dict[int, int]" = {}
        for value in present:
            split = _split_for_reading(value, separator, plain_pair)
            if split is not None:
                width = len(split)
                counted[width] = counted[width] + 1 if width in counted else 1
        for width in sorted(counted):
            if counted[width] < needed:
                continue
            columns: "list[list[str]]" = [[] for _each in range(width)]
            worn = 0
            for value in present:
                split = _split_for_reading(value, separator, plain_pair)
                if split is None or len(split) != width:
                    continue
                worn = worn + 1
                for place in range(width):
                    columns[place] += [split[place]]
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
        blocks += [_numeric_details(part_cells, whole_here)]
        smallest = len(text[0])
        for value in text:
            if len(value) < smallest:
                smallest = len(value)
        widths += [smallest]
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
            counted_here += [float(spelling)]
        numbers += [counted_here]
    agreements: "list[float]" = []
    above: "list[int]" = []
    for first in range(joined.n_parts):
        for second in range(first + 1, joined.n_parts):
            agreements += [
                round(
                    parsing.rank_agreement(numbers[first], numbers[second]),
                    parsing.RANK_AGREEMENT_PLACES,
                )
            ]
            counted = 0
            for seat in range(joined.n_joined):
                if numbers[first][seat] > numbers[second][seat]:
                    counted = counted + 1
            above += [counted]
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
    """The verdict for a column of numbers joined in one cell.

    Reached by the declaration (rule 0c) or, for a pair of plain whole
    numbers joined by a slash, from the values (rule 9c).
    """
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
                good += [text]
        if len(good) >= needed and good:
            return _Clock(
                form=form,
                values=good,
                n_unparsed=len(present) - len(good),
            )
    return None


def _compound_details(
    cells: _Cells, compound: "_Compound"
) -> "dict[str, object]":
    """Both halves of a compound column, each described in its own terms.

    THE TWO SUB-BLOCKS, and they are the whole point of the role. The
    counts alone would say only that the column has two populations and
    nothing about either -- which is the omission review item P1-R6-F7
    deleted a rule for, wearing a different hat. What answers that item
    is describing both.

    EACH HALF IS DESCRIBED BY THE MACHINERY THAT ALREADY DESCRIBES ITS
    KIND OF COLUMN, over a view of its own cells, on the precedent the
    affixed role set with its cores (G6A.2): the numeric half goes
    through the same tally and the same `_numeric_details` a column of
    numbers goes through, and the label half through the same `_levels`
    and `_level_details` a column of labels goes through. Nothing here
    computes a statistic of its own, so the two halves cannot come to
    disagree with the roles they are borrowed from.

    THE COUNTS STAY, and they are what a reader checks the halves
    against: `n_numeric_cells` and `n_label_cells` sum to `n_present`,
    so every present cell is in exactly one of the two descriptions.
    """
    # THE HALF'S OWN CELL COUNT IS THE ROW COUNT ITS BLOCK ECHOES, not
    # the table's. A joined position settled this first: that block
    # describes only the cells that split, so it echoes `n_joined`, and
    # comparing it against the table's count made the tool write files
    # it then refused to read. A compound half is the same shape of
    # thing -- it describes the numeric cells and no others -- and it
    # echoed the table's count until review round 1 of this landing
    # named the difference (item 7). Section 6.16 says this block
    # carries what a joined position carries; now it does.
    # READ THE WAY THE COLUMN WAS READ, declaration included. Both
    # halves are re-classified here, and the first writing dropped the
    # decimal-comma flag on the way -- so a DECLARED column of `1,5`
    # cells was split into a numeric half by the rule that reads the
    # comma and then re-read WITHOUT it, leaving a numeric half of no
    # numbers at all and an IndexError out of the percentile walk
    # (review round 4 of this landing, item 1). The tool crashed on a
    # real table, which is the worst outcome any of these rounds found.
    # THE HALF'S POPULATION IS ITS NUMBERS AND ITS UNUSABLE NUMERALS
    # (residual R-P4-149). Read together, so the block this half
    # publishes is a genuine numeric block: its four class counts are
    # the real ones, `n_left_out_of_statistics` says how many cells
    # the statistics could not use, and its count of different
    # spellings covers every cell the half holds. Read apart, the
    # column's own count of different cells was one more than the two
    # halves added, and the loader refused the description.
    half = compound.numbers + compound.unusable
    numeric_cells = _tally(
        _classify_all(
            [cell.text for cell in half], cells.decimal_comma
        ),
        len(half),
        cells.settings,
        cells.decimal_comma,
    )
    looking = _numeric_looking(numeric_cells)
    whole_everywhere = (
        numeric_cells.n_whole == looking and looking > 0
    )
    label_cells = _tally(
        _classify_all(
            [cell.text for cell in compound.labels], cells.decimal_comma
        ),
        len(compound.labels),
        cells.settings,
        cells.decimal_comma,
    )
    levels = _levels(
        label_cells.folded_counts,
        label_cells.spellings_by_folded,
        cells.settings,
    )
    unusable_out = 0
    unusable_contradictory = 0
    for cell in compound.unusable:
        if cell.kind == parsing.NUMBER_OUT_OF_RANGE:
            unusable_out = unusable_out + 1
        else:
            unusable_contradictory = unusable_contradictory + 1
    details: "dict[str, object]" = {
        "n_numeric_cells": len(compound.numbers),
        # THE THIRD POPULATION (residual R-P4-149). Cells the number
        # rules recognise as a numeral that this format cannot hold:
        # one too large or small, and one whose notation contradicts
        # itself. They are counted with the NUMERIC half -- an unusable
        # numeral is a number -- and the two counts below are the same
        # two a plain numeric column publishes, so the twin writes them
        # back through the machinery that writes them there.
        "n_numeric_out_of_range": unusable_out,
        "n_numeric_contradictory": unusable_contradictory,
        "n_label_cells": len(compound.labels),
        # THE NUMERIC HALF'S OWN COUNTS OF DIFFERENT WRITTEN CELLS, and
        # they are here because a SPELLING is not a VALUE (review round
        # 1 of this landing, item 1). The generator's layout spends
        # these two as its budget of different spellings, and the only
        # counts the block carried were the column's -- which count the
        # markers too -- and the half's count of different NUMBERS,
        # which counts `07` and `7` once between them.
        #
        # MEASURED on 300 cells holding sixty values each written twice,
        # plainly and with a leading zero, beside twenty markers: the
        # column publishes 113 different cells and the twin held 56 or
        # 57 at every one of five seeds, so `compound.n_distinct` --
        # which this landing registered EXACT-OBSERVABLE -- missed on
        # every file. The first measurement of this fact used a column
        # whose values were each written one way, where a count of
        # numbers and a count of spellings are the same number.
        "n_numeric_distinct": numeric_cells.raw_distinct,
        "n_numeric_distinct_folded": len(numeric_cells.folded_counts),
        "numbers": _numeric_details(numeric_cells, whole_everywhere),
        "labels": _level_details(levels, label_cells, False),
    }
    # THE LABEL HALF'S OWN COUNT OF DIFFERENT VALUES, which invariant
    # B2 is stated over: published levels and held-back levels together
    # are all of them. The column's own `n_distinct_folded` counts the
    # numbers too, so it cannot answer for this half, and a reader
    # checking B2 against it would be checking the wrong sum.
    labels_block = details["labels"]
    if isinstance(labels_block, dict):
        labels_block["n_distinct_folded"] = len(label_cells.folded_counts)
        # AND ITS RAW COUNT BESIDE THE FOLDED ONE (review round 3 of
        # this landing, item 5). The half's view carried the COLUMN's
        # count of different cells -- two hundred and ninety-six on a
        # half of five -- because the half published none, and a view
        # that carries a number from another population is a number
        # waiting to be read. With this the column's own count is the
        # two halves' counts added, rather than a range between them.
        labels_block["n_distinct"] = _published_distinct(label_cells)
        # AND HOW MANY CELLS THE HALF HOLDS, which the form census is
        # stated over: a census of forms is a census of the cells that
        # wore them, and the column's own `n_present` counts the
        # numbers too.
        labels_block["n_present"] = len(compound.labels)
    return details


def _compound_verdict(
    cells: _Cells,
    compound: "_Compound",
    notes: "list[Note]",
    remarks: "list[Note]",
) -> _Verdict:
    """The published block of a column of numbers beside labels.

    TWO POPULATIONS AND TWO COUNTS THAT SUM TO `n_present`, which is
    the whole answer to review item P1-R6-F7. That item deleted a rule
    which published a distribution over SOME of a column's cells and
    dropped the rest, because outcome principle 5 forbids describing a
    column in part and saying nothing about the remainder. This role
    publishes every present cell in exactly one of two populations and
    says how many are in each, so nothing is dropped and a reader can
    check the arithmetic.

    THE COUNTS ARE THE FIRST THING BUILT because they are the thing
    that makes the rest admissible. The numeric sub-block and the
    label sub-block are added by the landing's later steps; a block
    holding only the split is incomplete and is marked so in the
    register rather than shipped as finished.
    """
    # WHICH GROUND ADMITTED THE LABEL HALF, and the sentence says the
    # one that did. Rule 7b takes a half whose words are a small set OR
    # whose words include one the detection line clears; the first
    # writing of this had one sentence claiming the second ground on
    # every column, so a column of five markers was published with a
    # false statement about its own detection (review round 1, item 5).
    # The repeating ground is the stronger evidence and is stated where
    # it holds.
    if _levels_covering(compound.folded_counts, cells.settings) >= 1:
        evidence = note(
            EVIDENCE_COMPOUND,
            (
                len(compound.numbers),
                len(compound.labels),
                _long_tail_line(cells.settings),
                cells.n_rows,
            ),
        )
    else:
        evidence = note(
            EVIDENCE_COMPOUND_SMALL_SET,
            (
                len(compound.numbers),
                len(compound.labels),
                len(compound.folded_counts),
                cells.n_rows,
            ),
        )
    return _Verdict(
        role=ROLE_COMPOUND,
        evidence=evidence,
        details=_compound_details(cells, compound),
        notes=notes,
        remarks=remarks,
    )


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
        remarks += [note(REMARK_ALL_DIFFERENT_NUMBERS)]
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
    """One column's affixed reading: the pairs, and the cores under them.

    THE COMMONEST PAIR AND ITS VARIANTS (plan P4-D36). A column wears
    ONE pair on most tables and a SMALL SET of them on some that
    matter: a laboratory column whose values carry an abnormal flag --
    `13.5`, `4.2 H`, `9.8 L` -- wears three, and a column recorded in
    two units wears two. Before this, no single pair reached the parse
    line on such a column and the whole thing fell to free text, which
    publishes no ladder, no mean and no distribution at all.

    `prefix` and `suffix` are the COMMONEST pair, unchanged, so a
    column wearing one pair is described exactly as it was. `variants`
    holds the others with their counts.
    """

    prefix: str
    suffix: str
    variants: "list[tuple[str, str, int]]"
    # The core text of every cell wearing the pair, in row order. The
    # cells NOT wearing it are the stragglers the parse line tolerates,
    # and they are counted rather than listed: nothing of a straggler
    # is published.
    cores: "list[str]"
    # WHICH WRAPPER EACH OF THOSE CORES WORE, in the same order (plan
    # P4-D37). The cores were a flat list until that ruling, so nothing
    # downstream could tell a kilogram from a pound: one ladder was
    # read over all of them and published as the column's own. Every
    # wrapper carries its own numbers now, and this is what lets them
    # be read apart.
    wrappers: "list[tuple[str, str]]"
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
        split = affixed_split(text, cells.decimal_comma)
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

    This is `_affixed_before_the_address_test` with the address decline
    applied, and the two are kept apart for one reason: so that "did
    this column decline BECAUSE it was an address?" is answered from
    the SAME computation rather than from a second copy of the pair
    walk. A fact worked out twice in this project drifts, and the
    remedy this repository has settled on is to work it out once
    (`_declined_as_an_address` is the other caller).

    Guarantees: as `_affixed_before_the_address_test`, and one more --
    a pair that is an electronic address around its number is refused
    unless the person declared the column a measurement. That refusal
    is not silent: `_decide` asks `_declined_as_an_address` and the
    column carries `REMARK_ADDRESS_NOT_A_QUANTITY` (contract NF50).
    """
    reading = _affixed_before_the_address_test(cells, forced_measurement)
    if reading is None:
        return None
    if not forced_measurement and _wrapped_in_an_address(
        (reading.prefix, reading.suffix)
    ):
        return None
    return reading


def _declined_as_an_address(cells: _Cells) -> bool:
    """Whether the affix reading was refused for being an address.

    TRUE only where every other test of the role PASSED and the winning
    pair is an electronic address. A column that wears no pair, wears
    two, or wears one too few cells wore did not decline for this
    reason and gets no sentence about addresses.

    It asks the same function `_affixed_reading` asks, so the two can
    never disagree about which pair won; what it does not do is repeat
    the walk. The declaration is deliberately NOT a parameter: where
    `--measurement` is given there is no decline to speak about,
    because `_affixed_reading` returns the reading and `_decide` never
    reaches this question.

    Guarantees: accepts a tally; returns a truth value depending on
    that tally alone. No I/O, no randomness, and no value of the
    column is published by anything here or by the sentence it leads
    to -- the remark it raises carries no argument at all.
    """
    reading = _affixed_before_the_address_test(cells)
    if reading is None:
        return False
    return _wrapped_in_an_address((reading.prefix, reading.suffix))


def _pairs_of(reading: "_Affixed") -> "list[tuple[str, str]]":
    """Every wrapper this reading would publish: the commonest and its set."""
    pairs = [(reading.prefix, reading.suffix)]
    for prefix, suffix, _count in reading.variants:
        pairs += [(prefix, suffix)]
    return pairs


# THE MARKS THAT ARE NOT PART OF A WORD, enumerated rather than
# derived (review round 1 of landing L16, item 1). The question this
# governs is whether a wrapper is a WORD against a number -- a unit, a
# laboratory flag, a code's category letter -- and the first writing
# asked whether any character was an ASCII letter. That REMOVED a
# warning the tree already gave: 280 readings beside twenty `10.50 α`
# carried the question before this landing and carried nothing after
# it, because a Greek letter is a letter and `_LETTERS` is ASCII.
#
# WHY A CLOSED SET OF SYMBOLS RATHER THAN `str.isalpha`. The five
# supported Pythons carry five Unicode databases, so an alphabetic
# test can answer differently on two of them, and which sentences a
# profile carries is a published fact of the document (plan D12). The
# refusal set is closed and platform-stable, and it errs the way the
# owner's ruling errs: a symbol nobody listed is read as a word and
# raises a question, which costs one question, where a missing letter
# costs a person the warning entirely.
_SYMBOL_MARKS = "<>=~+-*/\\|^%$#@&()[]{}.,:;'\"!?_"


def _is_a_word_mark(mark: str) -> bool:
    """Whether one character belongs to a word rather than to a symbol.

    Guarantees: accepts one character; returns whether it is part of a
    word. Determinism: a function of that character against a closed
    set. Raises nothing. No I/O of any kind.
    """
    if parsing.trimmed(mark) == "":
        return False
    if mark in _DIGITS:
        return False
    if mark in _SYMBOL_MARKS:
        return False
    return True


def _carries_a_word(prefix: str, suffix: str) -> bool:
    """Whether one wrapper holds a word mark on either side."""
    for mark in prefix + suffix:
        if _is_a_word_mark(mark):
            return True
    return False


def _wears_a_word(reading: "_Affixed") -> bool:
    """Whether any wrapper this reading publishes holds a letter.

    THE FILTER THAT KEEPS A QUESTION FROM BEING NOISE (landing L16).
    The ambiguity this asks about is a WORD against a number -- a
    laboratory flag, a stage, a code's category letter. A mark that is
    no letter is not that ambiguity and never was: `<0.5` is a
    detection limit, `$98` is money, `45%` is a proportion, and none of
    them is a coding system. Measured before this filter existed: a
    column of 280 readings beside twenty `<0.5` cells raised the
    question and pointed at `--measurement`, which would then have
    published a distribution over the detection limit itself.

    Guarantees: accepts an affix reading; returns whether any wrapper
    it would publish carries a letter. Determinism: a function of that
    reading. Raises nothing. No I/O of any kind.
    """
    for prefix, suffix in _pairs_of(reading):
        if _carries_a_word(prefix, suffix):
            return True
    return False


def _wearing_a_word(reading: "_Affixed") -> int:
    """How many cells hold a NUMBER with a word written beside it.

    THE ARGUMENT BOTH QUESTION SENTENCES CARRY, and it is a count of
    CELLS rather than of anything else. It read `len(compound.labels)`
    until this landing, which is the whole text half: on 280 readings
    beside seventeen `<0.5` and three `NOT DETECTED` the sentence said
    twenty where seventeen wear text. The contract has always defined
    the argument as the present cells holding a number with text beside
    it, so this makes the producer match the contract rather than the
    other way about.

    **AND IT COUNTS BOTH HALVES OF THAT DEFINITION** (review round 1 of
    landing L16, item 3). The first writing counted every cell whose
    wrapper was not the bare one, which is neither half:

    * ten `10.50 H` beside ten `<0.50` came out TWENTY, and `<` is a
      comparison rather than a word -- the sentence names a word or a
      letter and only ten cells hold one;
    * seventeen `10.50 H` beside three `many H` came out TWENTY, and
      `many` is not a number -- the sentence names a NUMBER with a word
      beside it and only seventeen cells hold one.

    So a cell is counted when its wrapper carries a word AND its core
    reads as a number, which is exactly the population both sentences
    describe.

    Guarantees: accepts an affix reading; returns a count. Determinism:
    a function of that reading. Raises nothing. No I/O of any kind.
    """
    total = 0
    place = 0
    for prefix, suffix in reading.wrappers:
        if place >= len(reading.cores):
            break
        core = reading.cores[place]
        place = place + 1
        if not _carries_a_word(prefix, suffix):
            continue
        if parsing.classify_number(core) != parsing.NUMBER:
            continue
        total = total + 1
    return total


def _annotated_reading(cells: _Cells) -> "_Affixed | None":
    """The affix reading a DECLARATION would admit, where one would.

    RESIDUAL R-P4-157, AND THE PLACE IT IS ANSWERED FROM. A column of
    numbers beside figure-ending labels satisfies rule 7b and rule 9
    both, and which one claimed it depended on the values drawn.
    Amendment A-P4-58 rules that such a column is ASKED about rather
    than guessed at, and asks it BEFORE both numeric-bearing routes --
    so the question cannot be answered from inside either rule, and
    this is the one computation both of them consult.

    IT ASKS THE AFFIX WALK AS IF THE COLUMN WERE DECLARED. The letter
    guard `_stands_apart` is the only test that reads the declaration,
    and it is precisely the test that hides this column: a rear letter
    flush against the digits is refused undeclared, so asking the walk
    undeclared answers "no reading fits" and the tie is never seen.
    Asking it as if declared sees the reading the person could have,
    which is what the question is about.

    TWO REFUSALS ARE KEPT rather than inherited. An electronic address
    is not this question -- it has its own sentence, contract NF50 --
    and a wrapper carrying no letter is not this question either
    (`_wears_a_word`).

    IT ROUTES NOTHING AND IT IS NOT A READING. No rule takes a column
    because of this function: rule 7b still decides by
    `_compound_reading` and rule 9 still decides by `_affixed_reading`
    with the person's own declaration. What this answers is whether a
    SENTENCE is owed.

    Guarantees: accepts a tally; returns the reading a declaration
    would admit, or None. Determinism: a function of that tally.
    Raises nothing. No I/O of any kind, and no value of the column
    leaves it -- its callers publish only a count.
    """
    reading = _affixed_before_the_address_test(cells, forced_measurement=True)
    if reading is None:
        return None
    if _wrapped_in_an_address((reading.prefix, reading.suffix)):
        return None
    if not _wears_a_word(reading):
        return None
    return reading


def _affixed_before_the_address_test(
    cells: _Cells, forced_measurement: bool = False
) -> "_Affixed | None":
    """The one affix pair this column wears, address or not.

    Every rule of the role except the address decline. Two callers ask
    it and each applies that last rule for itself, which is what keeps
    the reading and the reason for refusing it one computation.

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
        split = affixed_split(text, cells.decimal_comma)
        if split is None:
            # THE BARE PAIR IS A MEMBER OF THE VOCABULARY (plan
            # P4-D36), proposed by a cell that reads as a number
            # wearing nothing at all. A laboratory column of `13.5`,
            # `4.2 H` and `9.8 L` wears three wrappers and one of them
            # is empty; without it the two flagged thirds could never
            # reach the line between them and the column was described
            # as free text.
            #
            # IT CANNOT SWALLOW A PLAIN NUMERIC COLUMN, because rule 6
            # is asked first: a column most of whose cells are bare
            # numbers is a column of numbers and never reaches here.
            if _reads_as_a_number(
                parsing.trimmed(text), cells.decimal_comma
            ):
                key = ("", "")
                proposing[key] = (
                    proposing[key] + 1 if key in proposing else 1
                )
            continue
        prefix, core, suffix = split
        key = (prefix, suffix)
        if key in proposing:
            proposing[key] = proposing[key] + 1
        else:
            proposing[key] = 1
    if not proposing:
        return None
    # WHICH PAIRS ARE PUBLISHABLE (plan P4-D36). A pair worn by fewer
    # cells than the smallest group size cannot be published, so its
    # cells are STRAGGLERS -- the population the parse line already
    # tolerates and the straggler construction already writes. That is
    # what keeps this rule from needing a held-back pool of its own.
    #
    # Walked over SORTED keys throughout, so nothing here depends on
    # the order a dictionary happened to fill.
    speaking: "list[tuple[str, str]]" = []
    for key in sorted(proposing):
        if proposing[key] >= settings.small_cell_floor:
            speaking += [key]
    if not speaking:
        return None
    # EVERY WRAPPER OF A SET STANDS APART FROM THE NUMBER (plan
    # P4-D36), and this guard is what keeps a set of CODE SCHEMES and
    # a set of markers from being read as a quantity.
    #
    # A LETTER WRITTEN FLUSH AGAINST A NUMBER IS NOT A UNIT. A unit or
    # an annotation is either separated from the number -- `13.5 H`,
    # `70 kg` -- or is a mark that is no letter at all -- `$98`, `45%`.
    # Two shapes were read as quantities without this and neither is
    # one: a diagnosis column of `E10.0`, `I11.2`, `J44.9` published a
    # LADDER over its code numbers, and a column of a hundred ages
    # beside twenty `refused3` markers put the marker's own digit into
    # the ladder with them.
    #
    # ASKING IT OF EVERY WRAPPER RATHER THAN OF ONE is what the second
    # of those settled: the bare wrapper stands apart by itself, so a
    # column of numbers beside ANY flush marker would have been
    # admitted on the numbers' own account.
    #
    # THE PRICE, and it is small: a column of `$98` beside `EUR99` --
    # a currency written flush -- is not read as a quantity. It was
    # free text before this landing and stays that way, so nothing is
    # lost that anybody had.
    #
    # ASKED OF A SET ONLY. A column wearing ONE wrapper is read exactly
    # as it was, so `D0140` is still whatever it was before.
    if len(speaking) > 1:
        # SOME CELL OF THIS COLUMN IS A PLAIN NUMBER, which is what
        # lets a flag be written flush against the digits (review round
        # 1, item 6). See `_stands_apart`: the front of the number is
        # where a code scheme puts its letter, and the back is where an
        # abnormal flag puts one -- but only a column that holds
        # unwrapped numbers is a column of numbers with annotations.
        # A LETTER FLUSH BEHIND THE DIGITS IS AMBIGUOUS AND THE PERSON
        # SETTLES IT (review round 3, item 2). Round 1 relaxed this
        # where the vocabulary held the bare wrapper, on the ground
        # that a column holding unwrapped numbers is a column of
        # numbers with annotations; round 2 then found a register of
        # procedure codes wearing exactly that shape, and round 3 found
        # that the width test written to separate them does neither
        # job. Measured, both ways:
        #
        #   100 bare two-digit readings beside 50 ending `H` and 50
        #   ending `L` -- an ordinary laboratory column -- was REFUSED,
        #   because its cores are all two digits;
        #
        #   50 bare four-digit codes beside 50 five-digit ones and 100
        #   ending `F` -- a register whose leading zeros a spreadsheet
        #   ate -- was ADMITTED, because its bare cores are of two
        #   widths.
        #
        # Nothing in the text tells a flagged measurement from a code
        # register: both are figures with a letter behind them. So the
        # question goes to whoever holds the table, which is this
        # project's own answer where a guess is not confident, and
        # `--measurement` is the flag that carries it. Undeclared, such
        # a column is what it was before this landing.
        for key in speaking:
            if not _stands_apart(key[0], key[1], forced_measurement):
                return None
        # AND EVERY WRAPPER OF A SET IS ONE WORD (plan P4-D36). A unit
        # or an annotation is a word -- `H`, `kg`, `months`, `EUR`,
        # `$` -- and a sentence is not. A column of `free comment
        # number 03 written out` beside its upper-case variants
        # proposes two wrappers of four words each; both clear the
        # floor, and the column published a LADDER over what is a
        # sequence number inside prose.
        #
        # ASKED OF A SET ONLY, so a column wearing ONE wrapper is read
        # exactly as it was: `note 3 of the batch` was this role
        # before this landing and still is.
        for key in speaking:
            if not _one_word(key[0]) or not _one_word(key[1]):
                return None
    # A SET OF WRAPPERS MAY NOT DIFFER BY ITS DIGITS (plan P4-D36),
    # and this guard was written against a false reading the set rule
    # created. A column of feet and inches, `4'5"`, `5'11"` proposes one pair per
    # inches value -- prefix nothing, suffix `'5"` -- and a dozen of
    # them clear the floor and the ceiling together. The column then
    # published a ladder over the FEET of some cells and the inches of
    # others: a description saying something false, where before it
    # said nothing at all.
    #
    # A WRAPPER IS SHARED TEXT. Where a column wears ONE, it may carry
    # digits -- `mL/min/1.73m2` is a real unit and this rule read it
    # before -- so the guard is asked only of a SET, where a digit is
    # the mark of a split that cut through a number.
    if len(speaking) > 1:
        for key in speaking:
            for side in key:
                for mark in side:
                    if mark in "0123456789":
                        return None
    # THE SET IS A VOCABULARY AND NOT PROSE, on the categorical rule's
    # own ceiling. A column proposing dozens of different pairs is a
    # column of text that happens to hold digits, and describing it as
    # a quantity in many wrappers would be describing something else.
    if len(speaking) > _categorical_ceiling(cells):
        return None
    # THE DETECTION LINE is over the cells wearing a PUBLISHABLE pair,
    # together. The contract's test is that at least the parse-line
    # count of present cells are affixed numbers; before plan P4-D36 it
    # asked that of ONE pair, so a laboratory column of `13.5`,
    # `4.2 H` and `9.8 L` -- where no pair carries a third of the
    # column -- reached no rule at all and was described as free text.
    covered = 0
    for key in speaking:
        covered = covered + proposing[key]
    if covered < needed:
        return None
    # THE COMMONEST PAIR IS THE ONE THE BLOCK NAMES, ties broken by the
    # pair's own text so two implementations pick the same one.
    pair = speaking[0]
    best = 0
    for key in speaking:
        if proposing[key] > best:
            pair = key
            best = proposing[key]
    if len(speaking) > 1:
        # AND EVERY WRAPPER'S CELLS ARE WRITTEN THE WAY THE COMMONEST
        # WRAPPER'S ARE (plan P4-D36). A unit or a flag does not change
        # how a value is SPELLED: a column of `13.5`, `4.2 H` and
        # `9.8 L` writes one figure after the point whichever wrapper a
        # cell wears. A NOUN in front of an index does: a column of 240
        # readings written to one figure beside sixty `note 3` cells
        # proposes two wrappers that both stand apart and are both one
        # word, and reading it as a quantity puts the notes' own
        # sequence numbers into the ladder with the readings.
        #
        # THE TEST IS AN OVERLAP AND NOT AN IDENTITY, because a real
        # flagged column may carry a whole value beside its fractional
        # ones: each wrapper's cells must share at least one fraction
        # width with the commonest wrapper's.
        if not _written_alike(present, speaking, pair, cells):
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
    wrappers: "list[tuple[str, str]]" = []
    counts: "dict[tuple[str, str], int]" = {}
    for text in present:
        trimmed = parsing.trimmed(text)
        chosen = _pair_worn(trimmed, speaking, cells.decimal_comma)
        if chosen is None:
            continue
        core = trimmed[
            len(chosen[0]) : len(trimmed) - len(chosen[1])
        ]
        if not core:
            # `mg` on its own wears no pair: it IS the suffix, with
            # nothing between the two sides for a number to be.
            continue
        cores += [core]
        # ...AND WHICH WRAPPER IT WORE (plan P4-D37), kept beside it so
        # the blocks below can be read one wrapper at a time.
        wrappers += [chosen]
        counts[chosen] = counts[chosen] + 1 if chosen in counts else 1
    # A WRAPPER IS FILTERED ON WHAT WEARS IT, NOT ON WHAT PROPOSED IT
    # (found while building plan P4-D37). `speaking` holds the wrappers
    # that cleared the floor at PROPOSAL -- pass one, over the cells
    # that read as a number wearing them -- and the count published is
    # the count that WEARS them, which is a different population and
    # can be far smaller. A column of `$1` to `$99` beside eleven cells
    # spelled `1` and one spelled `7`, with `1` DECLARED a hole,
    # proposes the bare wrapper twelve times and is worn by it ONCE:
    # the eleven holes are not present cells. The bare wrapper was
    # published with the count 1, which is a group of one named in a
    # description under a floor of eleven.
    #
    # So the floor is applied again here, where the published count
    # exists, and a wrapper that fails it is not published at all: its
    # cells become STRAGGLERS, which is the population this role
    # already has and already writes.
    kept: "dict[tuple[str, str], int]" = {}
    for key in counts:
        if key == pair or counts[key] >= settings.small_cell_floor:
            kept[key] = counts[key]
    if len(kept) != len(counts):
        held: "list[str]" = []
        wearing: "list[tuple[str, str]]" = []
        for place in range(len(cores)):
            if wrappers[place] in kept:
                held += [cores[place]]
                wearing += [wrappers[place]]
        cores = held
        wrappers = wearing
        counts = kept
    n_affixed = len(cores)
    # THE COMMONEST WRAPPER IS CHOSEN FROM WHAT WEARS IT, and it was
    # chosen from what PROPOSED it (review round 5, item 1). The
    # proposal pass counts cells that read as a NUMBER wearing a
    # wrapper; the wear pass counts every cell that wears it, cores
    # that are no number included, and the two orders can differ. AF17
    # then refused what this function had just written: a hundred
    # distinct ` kg` numerals beside ninety-eight ` aa` numerals and
    # two `many aa` cells proposes ` kg` as commonest and WEARS both a
    # hundred times, so the loader's tie rule wants ` aa` -- and
    # `synthtwin profile` wrote a file `synthtwin generate` refused,
    # which is the defect amendment A-P3-11 exists to keep closed.
    #
    # THE TIE RULE IS THE LOADER'S, character for character: most cells
    # first, and where two wrappers wear the same number of cells the
    # pair that sorts first.
    for key in sorted(counts):
        if counts[key] > counts[pair] or (
            counts[key] == counts[pair] and key < pair
        ):
            pair = key
    prefix, suffix = pair
    variants: "list[tuple[str, str, int]]" = []
    for key in sorted(counts):
        if key == pair:
            continue
        variants += [(key[0], key[1], counts[key])]
    # The floor is read HERE, at detection, deliberately: the pair is
    # PUBLISHED, so being able to publish a floor-clearing spelling is
    # constitutive of the role.
    if n_affixed < settings.small_cell_floor:
        return None
    if pair not in counts:
        return None
    return _Affixed(
        prefix=prefix,
        suffix=suffix,
        variants=variants,
        cores=cores,
        wrappers=wrappers,
        n_affixed=n_affixed,
    )


def _written_alike(
    present: "list[str]",
    speaking: "list[tuple[str, str]]",
    pair: "tuple[str, str]",
    cells: "_Cells",
) -> bool:
    """Whether every wrapper's cores are written like the commonest one's.

    A unit or a flag qualifies a value and does not respell it, so the
    cells wearing one carry cores written the way the rest are -- with
    a point where the rest have one. A noun in front of an index is a
    different thing wearing the same shape, and its cores are whole
    numbers whatever the rest of the column does.

    THE TEST IS AN OVERLAP AND NOT AN IDENTITY, because a real flagged
    column may carry a whole value beside its fractional ones: what
    each wrapper's cores must do is share a written form with the
    commonest wrapper's, not match its whole census.

    Guarantees: accepts the present cells, the publishable wrappers,
    the commonest one and the tally; returns whether every wrapper's
    cores are written with a point where the commonest wrapper's are,
    or without one where they are without. A
    wrapper whose cells carry no readable number at all is passed over
    rather than refused -- the class counts describe those cells and
    this question is about the ones that hold a value. Determinism: a
    function of those inputs. Raises nothing. No I/O of any kind.
    """
    widths: "dict[tuple[str, str], dict[bool, int]]" = {}
    for text in present:
        chosen = _pair_worn(
            parsing.trimmed(text), speaking, cells.decimal_comma
        )
        if chosen is None:
            continue
        trimmed = parsing.trimmed(text)
        core = trimmed[
            len(chosen[0]) : len(trimmed) - len(chosen[1])
        ]
        if not core:
            continue
        seen = _classify_all([core], cells.decimal_comma)
        for one in seen:
            if one.kind != parsing.NUMBER:
                continue
            # THE WRITTEN FORM AND NOT THE VALUE'S WHOLENESS. A cell
            # spelled `23.0` holds a whole number and is written with
            # a point, and it is the WRITING that a unit leaves alone:
            # asking the value instead let a column of readings
            # spelled to one figure share a form with a column of
            # bare indexes, because some of those readings landed on
            # a whole number.
            mark = "," if cells.decimal_comma else "."
            pointed = False
            for letter in core:
                if letter == mark:
                    pointed = True
            found = widths[chosen] if chosen in widths else {}
            found[pointed] = 1
            widths[chosen] = found
    if pair not in widths:
        return False
    common = widths[pair]
    for key in widths:
        shared = False
        for width in widths[key]:
            if width in common:
                shared = True
        if not shared:
            return False
    return True


def _one_word(side: str) -> bool:
    """Whether one side of a wrapper is a single word.

    The space that SEPARATES a unit from its number is part of the
    wrapper -- `13.5 H` wears ` H` -- so that one space is taken off
    before the question is asked. What is left must hold no space at
    all: `kg`, `months`, `EUR` and `$` do, and `written out` does not.

    WHICH CHARACTERS ARE SPACE IS ASKED OF `parsing.trimmed`, and this
    knew about the plain space and the tab alone until review round 8
    (item 4). `affixed_split` moves EVERY kind of whitespace into the
    wrapper -- that repair was itself review round 1's item 7 -- so a
    wrapper could arrive here holding a no-break space, and a no-break
    space is not in a two-character list. Measured: 120 cells reading
    `Clinical Stage 001` to `120` and 120 reading `Followup Stage 121`
    to `240`, with a no-break space between the words, were admitted
    as a quantity and published a distribution over sequence numbers
    inside two-word text; the same cells written with an ordinary
    space were free text. One question, one answer, asked of the one
    function that gives it -- the same repair, in the second of the two
    places that needed it.

    Guarantees: accepts one side of a wrapper; returns whether it is a
    single word. Determinism: a function of that input. Raises
    nothing. No I/O of any kind.
    """
    rest = side
    while rest and parsing.trimmed(rest[:1]) == "":
        rest = rest[1:]
    while rest and parsing.trimmed(rest[len(rest) - 1 :]) == "":
        rest = rest[: len(rest) - 1]
    for mark in rest:
        if parsing.trimmed(mark) == "":
            return False
    return True


def _stands_apart(prefix: str, suffix: str, declared: bool) -> bool:
    """Whether a wrapper is a unit or an annotation rather than a scheme.

    THE CHARACTER TOUCHING THE NUMBER is what says which, and the two
    sides are not the same risk.

    IN FRONT, a letter flush against the digits is USUALLY a code
    scheme -- `E10.0`, `I11.2`, `J44.9`, `D0140` -- where the letter
    says which register the number belongs to. Reading the rest as a
    quantity publishes a ladder over code numbers and writes codes
    nobody issued, so undeclared it is refused.

    **AND THE DECLARATION REACHES THIS SIDE TOO** (review round 6, item
    2). It did not, and the cost was a person answering the question
    and getting nothing for it: a hundred readings of `7.000` to
    `7.099` beside a hundred written `pH7.000` to `pH7.099` -- a real
    unit, written in front, flush -- stayed free text WITH
    `--measurement` given. A declaration the tool then ignores is worse
    than no declaration, because the person has done the one thing
    asked of them.

    BEHIND, a letter flush against the digits is AMBIGUOUS and the
    person settles it. `13.5H` is an abnormal flag on a laboratory
    result; `1234F` is a category of procedure code. Nothing in the
    text tells them apart, and two rules written to try were both
    measured wrong: refusing the shape outright sent every laboratory
    column whose flags are written flush to free text (round 1, item
    6), and admitting it where the cores are not all one width refused
    an ordinary two-digit laboratory column while admitting a register
    whose bare codes had lost their leading zeros (round 3, item 2).
    So `--measurement` carries the answer, which is this project's own
    way with a question it cannot settle for somebody.

    A letter that STANDS APART -- `13.5 H`, `70 kg` -- is a unit or an
    annotation and needs no declaration: a code register does not put a
    space before its category letter. A mark that is no letter at all
    (`$98`, `45%`) stands apart too, and the bare wrapper -- nothing on
    either side -- always does, because a cell wearing it IS a plain
    number.

    Guarantees: accepts the two sides of a wrapper and whether the
    person declared this column a measurement; returns whether the
    wrapper stands apart from the number it wraps. Determinism: a
    function of those inputs. Raises nothing. No I/O of any kind.
    """
    if not prefix and not suffix:
        return True
    if prefix:
        for mark in prefix[len(prefix) - 1 :]:
            if mark in _LETTERS and not declared:
                return False
    if suffix:
        for mark in suffix[:1]:
            if mark in _LETTERS and not declared:
                return False
    return True
def _wears(text: str, prefix: str, suffix: str) -> bool:
    """Whether one cell wears one wrapper with something between.

    THE CELL IS TRIMMED HERE rather than handed in already trimmed,
    which is what `_core_of` below does and what the offline audit
    asks for: a method call is accepted on a value the audit watched
    being made, and `parsing.trimmed` is such a maker while a
    parameter is not.

    Guarantees: accepts a cell and the two sides; returns whether the
    cell starts with the one, ends with the other, and has at least
    one character between them. Determinism: a function of those
    inputs. Raises nothing. No I/O of any kind.
    """
    trimmed = parsing.trimmed(text)
    if not trimmed.startswith(prefix):
        return False
    if not trimmed.endswith(suffix):
        return False
    return len(trimmed) > len(prefix) + len(suffix)


def _pair_worn(
    trimmed: str, speaking: "list[tuple[str, str]]", decimal: bool = False
) -> "tuple[str, str] | None":
    """Which of the publishable pairs this cell wears, or none.

    THE LONGEST WRAPPER WINS, and the tie is broken by the pair's own
    text. A cell of `13.5 H` wears both `('', ' H')` and `('', '')`,
    and reading it as the second would put ` H` inside the CORE, where
    no number rule can read it -- so the column would publish a core
    class count of "not a number" for a cell that plainly holds one.
    Taking the longest wrapper is what makes the split of a cell into
    a wrapper and a core the same split a person would make.

    THE BARE PAIR IS ASKED IN THE COLUMN'S OWN GRAMMAR (plan P4-D143,
    the final Codex review's item 4). ``decimal`` says the column was
    declared `--decimal-comma`, and there a bare `100,25` IS a number:
    asked under the ordinary grammar it was not, so 800 prices of which
    600 wore ` EUR` published `n_affixed: 600` -- a description the
    loader refuses, since at least 792 must wear the pair -- and with 400
    wrapped the column fell to free text.

    Guarantees: accepts a trimmed cell, the publishable pairs and
    whether the column declared a decimal comma; returns the pair it
    wears or None. Determinism: a function of those inputs, with a fixed
    order. Raises `TypeError` where the cell is not text, which is the
    offline audit's own gate. No I/O of any kind.
    """
    # THE CELL READS AS TEXT BEFORE A METHOD TOUCHES IT, in the exact
    # gate the offline audit names: this function's caller hands it a
    # value and a method call on an untraced value is refused.
    if not isinstance(trimmed, str):
        raise TypeError("a cell is text")
    found: "tuple[str, str] | None" = None
    reach = -1
    for key in sorted(speaking):
        # THE TWO SIDES GO THROUGH A FUNCTION THAT DECLARES THEM AS
        # TEXT. The offline audit accepts a parameter annotated `str`
        # and does not accept a tuple's member, which is how
        # `_core_of` below already writes the same comparison.
        front = key[0]
        back = key[1]
        if not _wears(trimmed, front, back):
            continue
        # THE BARE WRAPPER IS WORN BY A NUMBER AND BY NOTHING ELSE,
        # which is the rule it was PROPOSED under. It is a prefix and a
        # suffix of every cell there is, so without this a cell of
        # `9.9 CRITICAL` would wear it -- with the whole cell as its
        # core -- and the straggler population would vanish from every
        # column that publishes the bare wrapper.
        if not front and not back:
            read = trimmed
            if decimal:
                read = parsing.written_with_a_decimal_comma(trimmed)
            if parsing.classify_number(read) != parsing.NUMBER:
                continue
        width = len(front) + len(back)
        if width > reach:
            found = key
            reach = width
    return found


# The characters an address may be spelled with, as literal constants
# rather than as method calls: the offline audit accepts membership
# tests on gated text and does not carry `isalpha` or `isalnum`.
_LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
# The ten figures, written out for the same reason the letters are: the
# code-family test asks whether a core is written in figures alone, and
# a membership check against a literal is an operator rather than a
# method call on a value the offline audit cannot trace.
_DIGITS = "0123456789"
_HOST_CHARACTERS = _LETTERS + _DIGITS + "-."


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


def _variant_blocks(
    affixed: _Affixed, cells: _Cells
) -> "list[dict[str, object]]":
    """Every wrapper beside the commonest, with its own numbers (P4-D37).

    FOUR CLASS COUNTS PER WRAPPER, and they are not decoration. The
    block beside them is loaded the way any block of a subset is, and a
    loader cannot check a block without knowing how many of the cores
    under it read as numbers, how many are numerals this format cannot
    hold, how many contradict themselves and how many are not numbers
    at all. The column's own four are the sums; each wrapper's four
    close on its own count, exactly as AF4 closes the column's on
    `n_affixed`.

    Guarantees: accepts the column's affixed reading and the cells it
    was read from; returns one entry per wrapper beside the commonest,
    in the order those wrappers were published. Determinism: a function
    of those inputs. Raises nothing this module does not raise for any
    tally. No I/O of any kind.
    """
    blocks: "list[dict[str, object]]" = []
    for prefix, suffix, count in affixed.variants:
        tally = _wrapper_tally(affixed, (prefix, suffix), cells)
        looking = _numeric_looking(tally)
        blocks += [
            {
                "prefix": prefix,
                "suffix": suffix,
                "count": count,
                "n_core_numeric": len(tally.numbers),
                "n_core_out_of_range": tally.n_out_of_range,
                "n_core_contradictory": tally.n_contradictory,
                "n_core_not_numeric": tally.n_not_numeric,
                # ...AND HOW MANY DIFFERENT CORES THIS WRAPPER HOLDS.
                # The generator lays each wrapper's cores out from its
                # own block now, and a layout is divided by a count of
                # different things: handed the COLUMN's count, a
                # wrapper worn by fifty cells was asked for the
                # spellings of two hundred.
                "n_core_distinct": tally.raw_distinct,
                "n_core_distinct_folded": len(tally.folded_counts),
                "numbers": _numeric_details(
                    tally, tally.n_whole == looking and looking > 0
                ),
            }
        ]
    return blocks


def _wrapper_details(
    affixed: _Affixed,
    wrapper: "tuple[str, str]",
    cells: _Cells,
) -> "dict[str, object]":
    """The quantitative block of ONE wrapper, over its own cores.

    PLAN P4-D37, AND THE MEASUREMENTS THAT RULED IT IN. One block over
    every core of a column wearing a SET is a statistic of no quantity
    where the wrappers are units -- a hundred weights written `60.0 kg`
    to `69.9 kg` beside a hundred written `132.3 lb` to `153.8 lb`
    published mean 104.722, an average of nothing, with the column's
    ends running from 60 to 153.8 -- and a wrong one where a wrapper
    marks a different population: 240 readings written to one figure
    beside sixty markers reading `note 0.0` to `note 59.0` published
    mean 17.511, where the readings alone average 14.514.

    THE BLOCK ANSWERS FOR ITS OWN WRAPPER AND SAYS SO IN ITS OWN ROW
    COUNT. `_numeric_details` reads every population key off the tally
    it is handed, so a tally built over one wrapper's cores, with that
    wrapper's count as its row count, yields a block whose
    `n_used_in_statistics`, `n_left_out_of_statistics`, `numeric_share`
    and echoed `n_rows` are all that wrapper's. That is the arrangement
    a JOINED column's positions already have, word for word: a block
    describing a subset of a column's cells answers for that subset.

    Guarantees: accepts the column's affixed reading, one wrapper of
    it, and the cells it was read from; returns that wrapper's block.
    Determinism: a function of those inputs; the cores are taken in row
    order. Raises nothing this module does not raise for any tally. No
    I/O of any kind.
    """
    tally = _wrapper_tally(affixed, wrapper, cells)
    looking = _numeric_looking(tally)
    return _numeric_details(
        tally, tally.n_whole == looking and looking > 0
    )


def _wrapper_tally(
    affixed: _Affixed,
    wrapper: "tuple[str, str]",
    cells: _Cells,
) -> _Cells:
    """The cores ONE wrapper's cells hold, classified (plan P4-D37).

    ONE TALLY, TWO READERS. The block above is read off it and so are
    the four class counts beside that block, because a wrapper's cores
    are classified once and a second pass over the same cells is a
    second answer waiting to differ from the first.

    THE RECORD CARRIES THE DECLARATION ITS CELLS WERE CLASSIFIED
    UNDER (plan P4-D108). It did not, and the cores were classified as
    a declared column's while the record said they were not, so the
    mark between thousands was read in the wrong grammar for every
    wrapper of every declared column.

    Guarantees: accepts the column's affixed reading, one wrapper of
    it, and the cells it was read from; returns the tally of that
    wrapper's cores, in row order, with that wrapper's own count as its
    row count. Determinism: a function of those inputs. Raises nothing
    this module does not raise for any tally. No I/O of any kind.
    """
    worn: "list[str]" = []
    for place in range(len(affixed.cores)):
        if affixed.wrappers[place] == wrapper:
            worn += [affixed.cores[place]]
    return _tally(
        _classify_all(worn, cells.decimal_comma),
        len(worn),
        cells.settings,
        cells.decimal_comma,
    )


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

    AND UNDER THE SAME DECLARATION, WHICH THE RECORD NOW CARRIES (plan
    P4-D108). The cores were classified with the declaration and
    tallied without it, so `_group_separator` and `_thousands_marks`
    -- which read the grammar off the record and never off the column
    -- asked the undeclared question of a declared column's cores: a
    European price column grouping its thousands with a point
    published no mark at all, and its twin wrote every cell ungrouped
    at exit 0 on both files.
    """
    core_cells = _tally(
        _classify_all(affixed.cores, cells.decimal_comma),
        cells.n_rows,
        cells.settings,
        cells.decimal_comma,
    )
    n_core_numeric = len(core_cells.numbers)
    # `whole_everywhere` over the CORES, on the same test the numeric
    # roles use over their cells.
    core_looking = _numeric_looking(core_cells)
    # THE COLUMN'S OWN QUANTITATIVE BLOCK IS THE COMMONEST WRAPPER'S
    # (plan P4-D37). It was read over ALL the cores, and on a column
    # wearing a SET that is a statistic of no quantity: a hundred
    # weights in kilograms beside a hundred in pounds published mean
    # 104.722, an average of nothing, presented as the column's own.
    # Every published wrapper carries its own numbers now, this block
    # is the commonest wrapper's, and each of the others is beside its
    # own entry.
    #
    # A COLUMN WEARING ONE WRAPPER IS UNTOUCHED, which is the point of
    # writing it this way round: its commonest wrapper is its only one,
    # its cores are all of them, and `_cores_wearing` returns the same
    # list `affixed.cores` already held.
    n_present = len(cells.present)
    if not affixed.variants:
        # ONE WRAPPER, AND EVERY LINE OF THIS BRANCH IS WHAT SHIPPED.
        # Its commonest wrapper is its only one and its cores are all
        # of them, so there is nothing to read apart and nothing here
        # moves.
        whole_everywhere = (
            core_cells.n_whole == core_looking and core_looking > 0
        )
        details = _numeric_details(core_cells, whole_everywhere)
        # The two keys whose population the core substitution does NOT
        # reach. Version 4 defines them over PRESENT CELLS -- "how many
        # present cells the statistics were computed from", "the share
        # of present cells whose writer meant a number" -- so reading
        # them over the cores would leave a straggler in NEITHER count
        # and make both answer for a narrower population than their own
        # published meaning.
        details["n_left_out_of_statistics"] = n_present - n_core_numeric
        details["numeric_share"] = _share(core_looking, n_present)
        common_distinct = core_cells
    else:
        # A SET, SO THIS BLOCK IS THE COMMONEST WRAPPER'S AND ITS
        # POPULATION KEYS ARE THAT WRAPPER'S TOO (plan P4-D37). Reading
        # them over the whole column instead would leave the block
        # saying its statistics were computed from two hundred cells
        # and its ladder covering a hundred.
        #
        # This is the arrangement a JOINED column's positions already
        # have, in the same words: a block describing a SUBSET of the
        # column's cells answers for that subset, and echoes its count
        # rather than the table's row count.
        common = _wrapper_tally(
            affixed, (affixed.prefix, affixed.suffix), cells
        )
        common_looking = _numeric_looking(common)
        details = _numeric_details(
            common, common.n_whole == common_looking and common_looking > 0
        )
        common_distinct = common
    details["affix_prefix"] = affixed.prefix
    details["affix_suffix"] = affixed.suffix
    # THE OTHER WRAPPERS THIS COLUMN WEARS (plan P4-D36). A laboratory
    # column of `13.5`, `4.2 H` and `9.8 L` wears three, and until this
    # key existed no single one of them reached the detection line, so
    # the whole column was described as free text -- no ladder, no
    # mean, no distribution at all. Each entry names a wrapper and how
    # many cells wear it; the commonest one is the pair above and is
    # not repeated here. Every wrapper published clears the smallest
    # group size, and a wrapper worn by fewer cells than that is not
    # published: its cells are STRAGGLERS, which is the population
    # this role already has and already writes.
    # ...AND EACH OF THEM CARRIES ITS OWN NUMBERS (plan P4-D37). One
    # ladder over every core was a statistic of no quantity where the
    # wrappers were units -- a hundred weights in kilograms beside a
    # hundred in pounds published mean 104.722 -- and it was a wrong
    # one where they were markers: 240 readings beside sixty `note N.0`
    # cells published mean 17.511 where the readings alone average
    # 14.514. Every wrapper is published only where its count clears the
    # smallest group size, so every block below is read over at least
    # that many cores and is governed by the floor like any other.
    details["affix_variants"] = _variant_blocks(affixed, cells)
    details["n_affixed"] = affixed.n_affixed
    # HOW MANY DIFFERENT CORES, as distinct from how many different
    # CELLS (plan P4-D36). On a column wearing ONE wrapper the two are
    # the same number, which is why this key was not needed until a
    # column could wear several: with three wrappers, a hundred
    # different cores make up to three hundred different cells, and the
    # generator laid its cores out from the CELL count. Measured on a
    # laboratory column of 200 cells, 141 different cells and about a
    # hundred different cores: the core stage was asked for 141
    # different cores, spent the leading-zero family reaching for them
    # and wrote `0011.9 H` where every real cell read `11.9 H`.
    # ...AND THEY ARE THE COMMONEST WRAPPER'S, LIKE THE BLOCK THEY
    # BELONG TO (plan P4-D37). A count of different cores is the budget
    # of core spellings ONE layout is laid out from, and each wrapper
    # has its own layout now, so the column's pair belongs to the
    # column's block -- which is the commonest wrapper's. Every other
    # wrapper's pair is beside its own block. On a column wearing ONE
    # wrapper the commonest is the only one and these are what they
    # always were.
    #
    # The two counts CANNOT be left column-wide beside a per-wrapper
    # block: a count of different things does not subtract, so a
    # commonest wrapper's budget could not be recovered from the
    # column's total and the wrappers' -- and a layout handed a total
    # asks a wrapper worn by fifty cells for the spellings of two
    # hundred.
    details["n_core_distinct"] = common_distinct.raw_distinct
    details["n_core_distinct_folded"] = len(common_distinct.folded_counts)
    details["n_core_numeric"] = n_core_numeric
    details["n_core_out_of_range"] = core_cells.n_out_of_range
    details["n_core_contradictory"] = core_cells.n_contradictory
    details["n_core_not_numeric"] = core_cells.n_not_numeric
    # Carried by EVERY column of this role, without condition: no test
    # of the values separates an opaque token family from a
    # measurement, so the choice is between telling every such column's
    # owner and telling none.
    # THE COUNT NAMED BESIDE A SPELLING IS THE COUNT THAT WEARS IT
    # (review round 8, item 3). It was `n_affixed` -- every counted
    # cell -- and the sentence names ONE wrapper, so a column of a
    # hundred kilograms beside a hundred pounds published "200 of this
    # column's values are written as a number followed by ` kg`" when
    # a hundred are. The role's evidence line made the same false
    # claim and the loader required it, so the description, its
    # summary and its warning all said it together.
    #
    # On a column wearing ONE wrapper the two counts are the same
    # number, so nothing about such a column moves.
    worn_elsewhere = 0
    for _prefix, _suffix, count in affixed.variants:
        worn_elsewhere = worn_elsewhere + count
    pair = (
        affixed.prefix,
        affixed.suffix,
        affixed.n_affixed - worn_elsewhere,
    )
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
        remarks += [note(REMARK_ALL_DIFFERENT_NUMBERS)]
    # ...AND A WRAPPER THAT BRACKETS ITS WHOLE CELL IS NAMED (landing
    # 2b.2, contract NF56). It is a wrapper like any other -- its prefix
    # opens a bracket and its suffix closes one -- so nothing about the
    # reading moves; the sentence is what tells the owner that a sign
    # the brackets may carry is not in the numbers.
    worn: "list[tuple[str, str]]" = [(affixed.prefix, affixed.suffix)]
    for prefix, suffix, _count in affixed.variants:
        worn += [(prefix, suffix)]
    for prefix, suffix in worn:
        if prefix[:1] == "(" and suffix[len(suffix) - 1 : len(suffix)] == ")":
            remarks += [note(REMARK_BRACKETS_AROUND_THE_AFFIX)]
            break
    # ...AND SO IS A WRAPPER WRITING A MINUS AFTER ITS FIGURES (the
    # verification of landing 2b.2, contract NF57): a minus after figures
    # with no point is not read as a sign, so it reaches this role as a
    # suffix, and the sentence says the sign is not in the numbers.
    for _prefix, suffix in worn:
        if suffix[len(suffix) - 1 : len(suffix)] == "-":
            remarks += [note(REMARK_MINUS_AFTER_THE_FIGURES)]
            break
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
    judged_spellings: "dict[str, dict[str, int]]",
    forced_measurement: bool = False,
    judged: "tuple[str, ...]" = (),
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

    ITS TALLY CARRIES THE DECLARATION TOO (plan P4-D108), for the
    reason the record's own field states: a tally built from cells
    classified under a declaration and recorded as undeclared is one
    fact answered two ways.

    IT TAKES THE DECLARATION BECAUSE ITS CALLER DECIDED THE ROLE WITH
    ONE, and asking the reading a different question than the caller
    asked was a defect. `--measurement` carries an address-shaped
    column past the address decline, so it holds the affixed role --
    and this function re-derived the reading WITHOUT the declaration,
    got the decline, and returned every cell unjudged. Measured on 200
    cells of `user<core>@example.org`, 189 cores between 50 and 70
    beside eleven spelled `-999`: no verdict published, `-999` kept as
    the column's smallest reading, and the mean 1.785 where the same
    column wearing an ordinary pair reads 60.03 and publishes
    `read_as_missing` / `outlier_and_frequent`. That is the silent
    statistical wrongness C6-5's core pass exists to prevent, reached
    through the one declaration that says the numbers are real.
    """
    reading = _affixed_reading(cells, forced_measurement)
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
    cores = _tally(
        _classify_all(reading.cores, cells.decimal_comma),
        cells.n_rows,
        settings,
        cells.decimal_comma,
    )
    if _numeric_looking(cores) < _needed(
        settings.minimum_parse_rate, len(cores.present)
    ):
        return classified, missing, verdicts
    decided = _sentinel_verdicts(cores, len(cores.present), judged)
    withheld = sorted(
        candidate for candidate in decided if decided[candidate][0]
    )
    if not withheld:
        # NOTHING IS REMOVED, AND THE VERDICTS ARE STILL THE PASS'S
        # OWN. Returning the verdicts this pass never made threw away
        # every `kept_as_a_number` answer it did make -- so a column
        # whose owner protected its stand-in was described as though
        # nobody had asked, and the one line that would have told them
        # their instruction was honoured never appeared.
        return classified, missing, decided
    removed = [exact_of_number(candidate) for candidate in withheld]
    kept: "list[_Cell]" = []
    for cell in classified:
        split = _core_of(cell.text, reading.prefix, reading.suffix)
        core = _classify(split) if split is not None else None
        if core is not None and core.exact in removed:
            missing += [(cell.text, parsing.MISSING_NUMERIC_SENTINEL)]
            # THE WHOLE CELL IS THE SPELLING, not the core: what a
            # `missing_by_source` key carries is what the cell held,
            # character for character, and that is what a later reader
            # compares against (repair pass of landing 2b.6).
            place = 0
            for step in range(len(removed)):
                if removed[step] == core.exact:
                    place = step
            _spelling_judged(
                judged_spellings, f"{withheld[place]:g}", cell.text
            )
        else:
            kept += [cell]
    return kept, missing, decided


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
    after_levels: bool = False,
    forced_code: bool = False,
    forced_measurement: bool = False,
    probing: bool = False,
    described_as_pair: bool = False,
) -> _Verdict:
    """Pick the one role, testing the rules in the documented order.

    ``probing`` says this run is the recoverable-distribution advice
    asking what a smaller version of this column would be described as
    (contract NF29 argument 9). It suppresses the advice itself and
    nothing else, so the question is asked exactly once and this
    function cannot call itself without end. Every other caller leaves
    it false and gets the ordinary reading.

    ``after_levels`` says the LEVEL PASS took cells out of this column:
    every cell of a label level the floor would not let the column name,
    counted as missing because the pool they left could be read by
    subtraction (the owner's ruling of 2026-09-17, item 5; plan
    P4-D231). It silences rules 2, 5, 6, 8, 9 and 9c -- and rule 0c,
    which reads a declared measurement as joined numbers -- exactly as
    `--code` does, so the column stays a column of LABELS and which
    label rule claims it follows the levels that remain. That narrowing
    is the one the other two removal passes state in their own words: a
    column may not change what KIND of thing it holds because cells left
    it, and the cells this pass removed are the ones that were keeping
    the parse-rate rules out. A column of 480 `F`, 519 `M` and one `U`
    at a floor of eleven is therefore a `binary` column of `F` and `M`
    with one cell counted absent, and its twin describes back to the
    same role.

    ``described_as_pair`` says the DESCRIPTION a file is being checked
    against read this column as a slashed pair of plain whole numbers
    from its values (rule 9c, plan P4-D40). Only the validator sets it,
    and it moves rule 9c's reading to just before rule 9b and changes
    nothing else; see the comment at that point for why. Every other
    caller leaves it false.

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
    7b. NUMBERS BESIDE WORDS in one cell space -- `numbers_with_labels`
       (residual R-P4-13, plan P4-D33). It was missing from this list
       while the rule shipped, so a maintainer reading the one place
       that states the order was told of fourteen rules where there
       are fifteen (review round 8 of landing L8, item 6);
    8. clock times, in one of two forms, at the parse rate --
       `time_of_day`;
    9. a number wearing one shared piece of text -- `affixed_number`;
    9b. a long tail of labels -- `long_tail_labels`;
    9c. TWO PLAIN WHOLE NUMBERS JOINED BY A SLASH in every cell but the
       parse line's remainder -- `joined_numbers` read from the values
       (plan P4-D40). Last before the fallback, so it claims only a
       column that would otherwise publish nothing;
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
    # THE FIVE RULES THAT READ A CELL AS SOMETHING OTHER THAN A LABEL,
    # silenced by the `--code` declaration (rule 0b) and by the level
    # pass (plan P4-D231), which each leave a column of labels behind
    # them. One name for both, so the two can never silence different
    # rules.
    labels_only = forced_code or after_levels

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
        if forced_measurement and not after_days and not after_levels:
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
            and not labels_only
            and numeric_looking >= strict_needed
            and (len(cells.numbers) < strict_needed)
        ):
            remarks += [
                note(
                    REMARK_UNREPRESENTABLE,
                    (len(cells.numbers), numeric_looking),
                )
            ]
            notes += [note(NOTE_UNREPRESENTABLE_WITHHELD)]
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
                notes += [
                    note(
                        NOTE_ONE_VALUE_BELOW_FLOOR,
                        (settings.small_cell_floor,),
                    )
                ]
            # A CONSTANT COLUMN OF `-999` IS THE LOUDEST CASE OF ALL
            # (contract NF37): every row of it is the number this
            # package would have called a gap, and the description says
            # only that the column holds one value.
            remarks = remarks + _stand_in_level_remarks(levels)
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
                notes += [
                    note(
                        NOTE_ONE_OF_TWO_BELOW_FLOOR,
                        (levels.suppressed_levels, settings.small_cell_floor),
                    )
                ]
            if cells.raw_distinct != 2:
                remarks += [note(REMARK_CASE_ONLY_TWO)]
            if numeric_looking >= strict_needed or _matching_date_format(
                present, settings
            ):
                remarks += [note(REMARK_TWO_ALSO_NUMBERS)]
            remarks = remarks + _stand_in_level_remarks(levels)
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
            None if labels_only else _matching_date_format(present, settings)
        )
        if matched is not None:
            format_name, pairs, sources, unparsed, evidence = matched
            details = _datetime_details(
                format_name, pairs, sources, unparsed, settings
            )
            if numeric_looking >= strict_needed:
                # BOTH COUNTS, AND THEY ARE ALREADY COMPUTED HERE
                # (contract NF25, plan P4-D4.7). `pairs` is what the
                # chosen format parsed and `numeric_looking` is the
                # count the numeric line was compared against three
                # lines up, so the sentence states the two readings'
                # own numbers rather than a third measurement of them.
                remarks += [
                    note(
                        REMARK_DATES_ALSO_NUMBERS,
                        (len(pairs), numeric_looking),
                    )
                ]
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
                remarks += [
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
                remarks += [note(REMARK_MONTH_FIRST)]
            # THE CENTURY REMARK IS NOT AN ALTERNATIVE TO EITHER, so it
            # stands outside the chain above. A two-figure year is a
            # guess about the century whichever way the month and day
            # were settled -- by evidence, by a declaration, or by the
            # default -- so the column says so in every one of those
            # cases (plan P4-D15).
            if format_name in _TWO_DIGIT_YEAR_MEMBERS:
                remarks += [note(REMARK_TWO_DIGIT_YEAR)]
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
        if numeric_looking >= strict_needed and not labels_only:
            return _numeric_verdict(cells, notes, remarks)

        # RULE 7 -- a set of categories: at most the ceiling of different
        # values, counted after trimming and case folding. Tested after the
        # numeric rule, so a column of measurements is described as
        # measurements and a small set of labels that happen to be digits is
        # described as labels.
        #
        # IT STANDS ASIDE FOR A COLUMN WITH A REAL NUMERIC HALF, which is
        # the one exception it makes and the owner's decision of
        # 2026-09-03. A result column recorded coarsely -- readings at one
        # decimal beside a handful of markers -- can hold few enough
        # different values to pass the ceiling above, and this rule would
        # then claim it and describe every reading as a LABEL. That is the
        # defect rule 7b exists to repair, arriving one rule earlier: the
        # numbers are published as a list of words with counts and nothing
        # records that they are a distribution.
        #
        # Measured: 3,000 readings at four decimals beside 60 organism
        # names take rule 7b, and the SAME readings at one decimal are
        # claimed here instead -- the same column, described two ways,
        # decided by how finely the laboratory recorded it.
        #
        # THE TEST IS RULE 7b'S OWN and not a second one written here, so
        # the two rules cannot come to disagree about what a compound
        # column is. Where it answers, this rule declines and the column
        # falls to 7b below; a column with no numeric half, or whose text
        # half is prose, is untouched and lands here exactly as it did.
        if folded_distinct <= ceiling and (
            forced_code or _compound_reading(cells) is None
        ):
            levels = _levels(
                cells.folded_counts, cells.spellings_by_folded, settings
            )
            details = _level_details(levels, cells)
            details["level_ceiling"] = ceiling
            if levels.suppressed_levels:
                notes += [_pooled_note(levels, settings)]
            if cells.raw_distinct != folded_distinct:
                remarks += [note(REMARK_CASE_ONLY_MANY)]
            if ceiling - folded_distinct <= settings.near_threshold_slack:
                remarks += [
                    note(REMARK_NEAR_CATEGORY_LINE, (folded_distinct, ceiling))
                ]
            remarks = remarks + _stand_in_level_remarks(levels)
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

    # RULE 7b -- numbers and labels in ONE cell space: the
    # `numbers_with_labels` role. `7.2` beside `POSITIVE`, `0.9` beside
    # `NOT DETECTED` -- the long-format panel export (residual
    # R-P4-13, landing L8).
    #
    # WHY THE COLUMN NEEDS A ROLE OF ITS OWN, measured before it was
    # built. Such a column declines to `long_tail_labels` today, and
    # that decline is wrong in BOTH directions. On a 300-row column of
    # 222 readings beside two markers: at the then default floor of one
    # every reading clears the line and is published as its own LEVEL,
    # 177 of them, so the description carries the readings themselves;
    # at a floor of eleven the levels fall to two and the twin holds NO
    # numeric cell at all. The protective setting destroys the numeric
    # population and the permissive one carries it verbatim. Neither
    # DESCRIBES it.
    #
    # WHERE IT SITS, and it is the one placement that is not free.
    # After categorical, before the clock rule -- so ABOVE the long
    # tail and free text, and it therefore MOVES columns those two hold
    # today. That is an exception to this phase's no-regression rule
    # and is named as one rather than discovered: the columns it moves
    # are exactly the ones whose numeric mass nothing describes, and
    # the transition is exercised both ways in the battery.
    #
    # WHAT IT ASKS, and each half must earn its own publication:
    #
    #  - the numeric cells fall SHORT of the numeric line, or rule 6
    #    took the column already and this rule never sees it;
    #  - the numeric cells number at least the detection line, the
    #    publication floor or eleven whichever is larger -- the same
    #    line the long tail uses, so lowering the floor cannot widen
    #    which columns take this role;
    #  - and the cells that are NOT numbers hold at least one level
    #    that clears that same line. This is the half the close plan
    #    left open: "every other present cell folds to a label level"
    #    is true of any column, so it cannot be what tells a lab
    #    column from numbers beside free comments. Asking the text
    #    half to be label-publishing IN ITS OWN RIGHT is what does,
    #    and it is the rule the long tail already applies to a whole
    #    column, applied here to a part of one.
    #
    # A column failing any of the three declines to the rules below
    # exactly as it does today.
    # A COLUMN BOTH RULES CAN READ IS AN AMBIGUOUS COLUMN, AND AN
    # AMBIGUOUS COLUMN IS ASKED ABOUT RATHER THAN GUESSED AT
    # (amendment A-P4-58, owner ruling 2026-09-09; residual R-P4-157).
    #
    # A column of readings beside `H` and `L` flags satisfies this rule
    # and the affix rule both, and WHICH IT REACHED DEPENDED ON THE
    # VALUES DRAWN -- `affixed_number` on thirty of forty draws and
    # `numbers_with_labels` on ten. Three rules were written over the
    # TEXT to separate the two readings and all three were measured
    # wrong; the last turned `Stage 1` and `Stage 2` labels into a
    # quantity. The text does not carry the answer.
    #
    # SO THE DRAW NO LONGER DECIDES IT. Where both readings are
    # available the CAUTIOUS one is taken -- this rule, which describes
    # the unmarked values as numbers and the marked ones as labels --
    # and the column carries a remark saying what was not settled and
    # which flag settles it. The two errors are not the same size: read
    # as labels, a measurement column publishes fewer numbers than it
    # holds and every number it publishes is true; read as
    # measurements, a label column publishes a mean of stage numbers,
    # which is a quantity that does not exist.
    #
    # AND `--measurement` IS THE ANSWER, not a bypass: the person who
    # holds the table says it is a quantity, and rule 9 then reads it.
    # THE ARBITRATION ASKS ONE COMPUTATION, AND IT IS NOT THE ONE THAT
    # DECIDES THE ROLE (landing L16, closing round 8's first item).
    #
    # The question used to be put to `_affixed_reading` with the
    # person's own declaration, which cannot see the tie it was meant
    # to find: undeclared, the letter guard refuses a rear letter
    # flush against the digits, so `both_fit` came out false and a
    # register of 280 five-digit procedure codes beside fifteen
    # `3074F` and five `3075F` took this role in silence, publishing an
    # average of 54,239 over the bare codes and carrying no sentence at
    # all. `_annotated_reading` asks the walk AS IF DECLARED, which is
    # what makes the tie visible, and refuses an address or a wrapper
    # holding no letter so the question stays a real one.
    #
    # WHAT READS WHAT, because the three must not blur. Rule 7b decides
    # by `_compound_reading`. Rule 9 decides by `_affixed_reading` with
    # the person's own declaration, untouched, so no undeclared column
    # moves role and the no-regression rule is not disturbed. Only the
    # SENTENCE is decided here.
    compound = None if forced_code else _compound_reading(cells)
    if compound is not None and not forced_code:
        if forced_measurement:
            # The person has answered. Fall through to rule 9, on the
            # same test as before this landing: whether the declaration
            # gives them an affixed reading at all.
            if _affixed_reading(cells, True) is not None:
                compound = None
        else:
            annotated = _annotated_reading(cells)
            if annotated is not None:
                remarks += [
                    note(
                        REMARK_TWO_READINGS_FIT,
                        (_wearing_a_word(annotated),),
                    )
                ]
    if compound is not None:
        return _compound_verdict(cells, compound, notes, remarks)

    # RULE 8 -- a column of clock times: the `time_of_day` role.
    # `09:30`, `14:05:00`.
    #
    # Before the affixed rule and after every rule that already reads a
    # column well. Its place in front of the affix reading is the
    # contract's and has a reason: clock text rarely splits as an
    # affixed number, but where both could fire the time reading is the
    # more specific claim.
    clock = None if labels_only else _clock_reading(cells)
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
        if labels_only
        else _affixed_reading(cells, forced_measurement)
    )
    if affixed is not None:
        return _affixed_verdict(cells, affixed, notes, remarks)

    # ...AND WHERE THE RULE DECLINED BECAUSE THE PAIR IS AN ADDRESS,
    # THE COLUMN SAYS SO (contract NF50, residual R-P4-39). The decline
    # itself is right and is not touched here: publishing a mean over
    # the numbers inside `user12345@example.org` is publishing the
    # average of real identifiers, which was measured at 53,574.055 on
    # 400 rows. What was missing is the second half of principle 5 --
    # a column is either handled or DECLINED WITH A PLAIN-LANGUAGE
    # EXPLANATION -- and this decline had none: the column stopped
    # being described as numbers and every surface was silent about it.
    #
    # IT ROUTES NOTHING. The remark is added to the list the rules
    # below carry into whatever role they give this column, so no role,
    # no published fact and no cell moves because of it. The three
    # declarations it names are the only things that move any of those,
    # and each of them is made by whoever holds the table.
    #
    # `forced_code` is asked because rule 9 was never run under it: a
    # declared code column is already being described as labels, and a
    # sentence proposing three declarations to somebody who has just
    # made one of them is noise.
    if not forced_code and _declined_as_an_address(cells):
        remarks += [note(REMARK_ADDRESS_NOT_A_QUANTITY)]

    # ...AND WHERE IT DECLINED BECAUSE A LETTER IS WRITTEN FLUSH
    # AGAINST THE DIGITS, THE COLUMN SAYS THAT TOO (landing L16,
    # residual R-P4-157, amendment A-P4-58). This is the address
    # remark's sibling and it is owed for the same reason: the decline
    # is right and it was silent. `13.5H` is a flagged laboratory
    # result and `1234F` is a category of procedure code; the guard at
    # `_stands_apart` refuses the shape undeclared BECAUSE the values
    # cannot tell them apart, and a person meeting that refusal was
    # told by the competing-readings remark to rewrite their data --
    # while two declarations that read the column correctly already
    # shipped and neither was named.
    #
    # IT ROUTES NOTHING, exactly as the address remark routes nothing:
    # no role, no published fact and no cell moves. `--measurement` is
    # excluded because under it rule 9 read the column and there is no
    # decline to speak about; `forced_code` is excluded for the reason
    # the address remark gives -- proposing declarations to somebody
    # who has just made one is noise.
    #
    # AND IT CANNOT COLLIDE WITH THE ADDRESS REMARK: an address is
    # refused inside `_annotated_reading`, so a column carrying that
    # sentence never carries this one.
    if not forced_code and not forced_measurement:
        letter_bound = _annotated_reading(cells)
        if letter_bound is not None:
            remarks += [
                note(
                    REMARK_A_LETTER_NEEDS_A_DECLARATION,
                    (_wearing_a_word(letter_bound),),
                )
            ]

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
    # ...UNLESS THE DESCRIPTION BEING CHECKED ALREADY READ THIS COLUMN AS
    # A SLASHED PAIR (plan P4-D40; validation method V2.2-A2). Rule 9c
    # stands after rule 9b, so whether a column of slashed pairs is read
    # as two numbers or as a long tail turns on whether one whole reading
    # repeats in the long-tail line's count of rows -- and that is a
    # property of the SAMPLE, not of the column. Measured on a blood
    # pressure of 5,000 rows: the real column's commonest reading
    # repeated 9 times, a faithful twin's, whose two positions are paired
    # at random, 12 and 14 times, so the twin re-read as a long tail and
    # `synthtwin validate` called the role MISSED on 22 round trips of 80
    # between 1,200 and 5,000 rows, where the declared column passed on
    # the same cells. Checking a file is asking whether it matches the
    # description, so the file is read the way the description was read,
    # exactly as a declaration is carried over. It can still fail: a
    # file whose cells are not such pairs is not read as them, and falls
    # to the rules below.
    if described_as_pair and not forced_code:
        described_pair = _joined_reading(cells, plain_pair=True)
        if described_pair is not None:
            return _joined_verdict(cells, described_pair, notes, remarks)

    covering = _levels_covering(cells.folded_counts, settings)
    if covering > 0 or forced_code:
        levels = _levels(
            cells.folded_counts, cells.spellings_by_folded, settings
        )
        details = _level_details(levels, cells)
        if levels.suppressed_levels:
            notes += [_pooled_note(levels, settings)]
        if cells.raw_distinct != folded_distinct:
            remarks += [note(REMARK_CASE_ONLY_MANY)]
        remarks = remarks + _stand_in_level_remarks(levels)
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

    # RULE 9c -- TWO PLAIN WHOLE NUMBERS JOINED BY A SLASH, read from
    # the values (plan P4-D40, 2026-09-15, narrowing P4-D21). A blood
    # pressure written `128/79` beside 1,999 others was free text at
    # 300 rows and at 2,000: this rule was asked only under
    # `--measurement`, so without the declaration its twin held stand-in
    # text and neither position's ladder was ever described or checked.
    #
    # IT CLAIMS ONLY WHAT WOULD OTHERWISE PUBLISH NOTHING. It sits after
    # every rule that publishes a value, so no column those rules read
    # today moves; and it reads one shape, which none of the columns
    # P4-D21 measured wears: a date and a clock are claimed by rules 5
    # and 8, the laboratory code `1923-1` and the drug code
    # `00052-0052-52` are joined by a hyphen, and a padded part such as
    # `007` or a part with a point is left to the declaration. A code
    # written as two slashed figures is still a code this rule cannot
    # tell from a measurement, which is why the questions file goes on
    # asking about the column with `code` and `identifier` offered.
    if not labels_only:
        paired = _joined_reading(cells, plain_pair=True)
        if paired is not None:
            return _joined_verdict(cells, paired, notes, remarks)

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
    remarks += [
        _competing_readings(
            cells,
            ceiling,
            numbers_said,
            dates_said,
            removed,
            # THE FOURTH READING, WHICH THIS COLUMN USED TO BE SILENT
            # ABOUT (contract NF29 argument 8). The remark named the
            # numeric reading, the date reading and the affix reading;
            # a column of clock times in a shape this version does not
            # describe was told that nothing fitted and never told
            # which reading came closest.
            clock_reach(cells),
            # ...AND THE ONE DECLARATION THAT WOULD CHANGE THE ANSWER
            # (contract NF29 argument 9, amendment A-P4-1 item 4). The
            # DECLARATIONS ARE PASSED IN because the advice is false
            # under `--code`: that declaration silences every rule that
            # reads a cell as a number, so no `--missing-value` can
            # give this column a distribution, and a sentence promising
            # one would send its reader to a command that cannot help.
            _recoverable_reach(
                cells, forced_code, forced_measurement, probing
            ),
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
    if not _count_is_named(arguments, place):
        return ""
    return (
        f", after {_count_said(arguments, place)} of them were read as "
        f"stand-ins for "
        f"'no value' and taken out -- which is what moved this column "
        f"across a line, so the counts above are of what was left"
    )


def _later_clauses(
    arguments: "tuple[object, ...]", clock_place: int, advice_place: int
) -> str:
    """NF29's last two clauses, composed exactly as the contract says.

    Argument 8 is how far a CLOCK reading got. The competing-readings
    remark named the numeric reading, the date reading and the affix
    reading, and stayed silent about the fourth -- so a column of clock
    times in a shape this version does not describe was told that no
    reading fitted it and never told which reading came closest.

    Argument 9 is the recoverable-distribution advice (amendment A-P4-1
    item 4). Where a declined column's repeated non-numeric spellings
    are what held it below the parse line, one `--missing-value`
    brings its distribution back, and the remark said nothing about it.
    IT IS ADVISORY AND ROUTES NOTHING: the count is the rows those
    spellings cover and the declaration is the person's own to make.
    Its trigger is a PRODUCER obligation and is stated where the
    producer computes it (`_recoverable_reach`), not here.

    THE COMPOSITION IS THE CONTRACT'S AND IT IS WRITTEN ONCE. 4.5.1
    says a clause is written if and only if its own argument is
    nonzero, in argument order, each ending in a full stop and
    separated from the next by ONE space, with a full stop and one
    space after what came before. Two functions each prefixing their
    own ". " wrote `describe.. 9 more` the first time this was built,
    which is why the join lives in one place: a guard rebuilding the
    sentence has one candidate string to compare, not a family of
    them.
    """
    written: "list[str]" = []
    if _count_is_named(arguments, clock_place):
        written += [
            f"{_count_said(arguments, clock_place)} of these values read "
            f"as a clock time, in a shape "
            f"synthtwin does not describe."
        ]
    if _count_is_named(arguments, advice_place):
        # THE COUNT IS NAMED ONCE AND POINTED AT AFTERWARDS. The
        # second mention used to repeat the number, which reads as
        # "if those fewer than 11 mean" once the fragment stands
        # there; "those values" says the same thing and says it of
        # either.
        written += [
            f"{_count_said(arguments, advice_place)} more are written "
            f"one of a few ways that repeat "
            f"often enough to name. If those values mean 'no "
            f"value', run the command again with --missing-value and "
            f"this column's distribution will be described."
        ]
    if not written:
        return ""
    # BUILT BY ADDITION AND NOT BY `join`. The offline audit refuses a
    # data method handed a value it cannot resolve under its own eyes,
    # because the receiver's protocol then runs on that value -- and a
    # list built here is not one of the shapes it can trace. Adding
    # strings has no such reach, and the separator is still stated once.
    tail = ""
    for clause in written:
        if tail:
            tail = tail + " " + clause
        else:
            tail = clause
    return ". " + tail


def _competing_readings(
    cells: _Cells,
    ceiling: int,
    numbers_said: "tuple[str, tuple[object, ...]]",
    dates_said: "tuple[str, tuple[object, ...]]",
    removed: int,
    clock_said: int,
    recoverable: int,
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
            clock_said,
            recoverable,
        ),
    )


# THE ROLES THE RECOVERABLE-DISTRIBUTION ADVICE MAY PROMISE. The advice
# tells its reader that one `--missing-value` will get "this column's
# distribution described", so the roles that make that sentence TRUE
# are the ones that publish an average, a spread and a ladder over
# numbers. Written out rather than derived from a wider predicate on
# purpose: `numeric_unrepresentable` publishes no statistic at all,
# `constant` and `binary` publish labels and counts, and residual
# R-P4-16 was opened because the plan's arithmetic promised a
# distribution on exactly those three.
# THE ROLES THAT PUBLISH A DISTRIBUTION, which is what the
# recoverable-distribution advice promises a re-run would produce. The
# compound role belongs here (residual R-P4-13, landing L8): its
# numeric half carries the same quantitative block a column of numbers
# does, so a declaration that turns a column into one HAS given its
# reader the distribution the sentence offered.
_ROLES_WITH_A_DISTRIBUTION = (
    ROLE_COUNT,
    ROLE_CONTINUOUS,
    ROLE_AFFIXED,
    ROLE_COMPOUND,
)


def _recoverable_reach(
    cells: _Cells,
    forced_code: bool,
    forced_measurement: bool,
    probing: bool,
) -> int:
    """Rows one `--missing-value` would recover a distribution from.

    Contract NF29 argument 9; amendment A-P4-1 item 4, under the
    TIGHTENED trigger residual R-P4-16 asked for and the owner
    accepted. Zero means no advice is written, and the remark then says
    nothing about a declaration.

    THE TRIGGER IS A RE-RUN AND NOT AN ARITHMETIC, and that is the
    whole of what R-P4-16 settles. The plan's original trigger was
    "removing the floor-clearing non-numeric folded spellings lifts the
    survivors past the parse line", which is whole-number arithmetic
    over counts this remark already carries -- and it does not deliver
    the clause's own promise. Survivors can clear the line on cells
    that merely LOOK numeric without one of them being a number this
    format can hold, in which case the column takes
    `numeric_unrepresentable` and publishes no statistic; or they can
    collapse to one or two different values, which `constant` and
    `binary` claim ahead of every numeric rule. In both cases the
    advice promised a distribution the re-run would not describe.

    So the producer RE-READS the column over the survivors and writes
    the sentence only where that reading lands on a role that publishes
    a distribution. **A loader cannot check this** -- it holds a
    description and not the cells -- which is why R-P4-16 records it as
    a producer obligation and not as a wire invariant, and why this
    function is where the rule lives.

    THE DECLARATIONS ARE ASKED, because they decide whether the advice
    is true at all. Under `--code` every rule that reads a cell as a
    number is silenced, so no `--missing-value` can give this column a
    distribution and the advice must stay quiet.

    ``probing`` is the re-run asking this same question one level down.
    It answers zero, which is what bounds the recursion at one step:
    the advice is decided by the FIRST reading of the survivors, and a
    survivor column that would itself have carried advice is a column
    the reader will meet after making the declaration this sentence
    proposes.

    Guarantees: accepts the tally of one column that fell to free text,
    the two declarations that were in force, and whether this is the
    probe; returns a count of that column's present cells, or zero.
    Determinism: a function of those arguments alone. Raises nothing.
    No I/O of any kind, and no spelling of the column travels out
    through it -- the answer is a count.

    ONE LIMIT, STATED WHERE IT LIVES. The re-run is this module's role
    reading. The stand-in and placeholder judgements sit ABOVE it in
    `profile_column` and are not repeated here, so a column whose
    survivors those passes would collapse to two values could still be
    given hopeful advice. It is recorded with R-P4-16 rather than
    argued away: closing it means re-running those passes too, and the
    two shapes R-P4-16 names are both closed by this reading.
    """
    if probing or forced_code:
        return 0
    settings = cells.settings
    offending = _floor_clearing_non_numeric(cells)
    if not offending:
        return 0
    survivors = [
        cell for cell in cells.classified if cell.folded not in offending
    ]
    covered = len(cells.classified) - len(survivors)
    if not survivors or covered == 0:
        return 0
    reading = _decide(
        _tally(survivors, cells.n_rows, settings, cells.decimal_comma),
        False,
        forced_measurement=forced_measurement,
        probing=True,
    )
    if reading.role in _ROLES_WITH_A_DISTRIBUTION:
        return covered
    return 0


def _floor_clearing_non_numeric(cells: _Cells) -> "tuple[str, ...]":
    """Folded spellings that repeat often enough to name and hold no number.

    "Often enough to name" is the publication floor and not a rule of
    this remark's own: a spelling the floor would hold back is a
    spelling the advice may not describe, so the two lines are the same
    line. "Holds no number" is asked of the CELLS rather than of the
    folded key, because the key is a trimmed and case-folded string and
    asking it a second time would be a second reading of a cell this
    module reads once.

    TWO THINGS ARE NARROWER THAN THE FLOOR, and both are here so the
    contract's own sentence is TRUE of the column it is written on.
    NF29's clause 9 says the covered cells "are written one of a few
    ways that repeat often enough to name", and neither half of that
    survives the floor alone:

    * **A spelling has to REPEAT**, which at a floor of one it need
      not (amendment A-P4-37 lowered the default floor to 1, four
      amendments after A-P4-1 wrote this trigger against it; plan
      P4-D316 returned it to 11). Without
      this, a column of a hundred numbers beside a hundred ALL
      DIFFERENT words would have every word counted as a "way that
      repeats", and the sentence would call a hundred one-off
      spellings a few repeated ones.
    * **There have to be A FEW WAYS**, which is the categorical
      ceiling -- this document's own line for "a small set of values in
      this column", computed and not invented. Without it a column
      whose gaps wear fifty different spellings is told they are "a
      few".

    Both narrow the advice rather than widening it, so no column gains
    a sentence by them; some columns that would have been told
    something loosely true are told nothing, which is the direction an
    advisory remark should err in.

    Guarantees: accepts the tally of one column; returns the folded
    identities in sorted order, which is the order every walk over them
    is taken in, and returns none at all where there are more of them
    than the ceiling admits. Raises nothing. No I/O of any kind.
    """
    # A MAPPING RATHER THAN A SET, and the offline audit is why: a set
    # is filled by a METHOD CALL on a value that audit cannot trace to
    # an allowlisted API, and no method call on an untraced value is
    # accepted. Subscript assignment is what `_tally` above builds its
    # own folded map with, for the same reason.
    numeric_somewhere: "dict[str, bool]" = {}
    for cell in cells.classified:
        if cell.kind != parsing.NOT_A_NUMBER:
            numeric_somewhere[cell.folded] = True
    floor = cells.settings.small_cell_floor
    if floor < 2:
        floor = 2
    found = tuple(
        folded
        for folded in sorted(cells.folded_counts)
        if cells.folded_counts[folded] >= floor
        and folded not in numeric_somewhere
    )
    if len(found) > _categorical_ceiling(cells):
        return ()
    return found


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
    notes += [note(NOTE_FREE_TEXT_WITHHELD)]
    if _all_different(cells):
        remarks += [note(REMARK_ALL_DIFFERENT_TEXT)]
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
    the same class of fact the sizes of a label column's withheld levels
    were, published for the same reason until the owner's ruling of
    2026-09-17 pooled those sizes into one total (plan P4-D201) -- and
    the reason was checked here rather than assumed:

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
      about an unnamed group, which is precisely what the withheld
      level sizes published until that ruling, and it is why the
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
    this function has exactly two callers, and the only candidate -- the
    withheld level sizes -- was a sorted array of integers rather than a
    mapping, and is published as one pooled total since the owner's
    ruling of 2026-09-17 (plan P4-D201). `_n_distinct_by_occurrences` above states what this class
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
    notes += [note(NOTE_IDENTIFIER_WITHHELD)]
    layouts = _layout_forms(cells)
    return _Verdict(
        role=ROLE_IDENTIFIER,
        evidence=note(EVIDENCE_DECLARED_IDENTIFIER),
        details={
            "min_length": min(lengths),
            "max_length": max(lengths),
            "all_whole_numbers": (
                cells.n_whole == n_present and cells.n_whole > 0
            ),
            "n_all_digits": _published_alphabets(cells)[1],
            "n_code_alphabet": _published_alphabets(cells)[0],
            # WHAT A RECORD NUMBER LOOKS LIKE, with no value attached
            # to it (7.12, plan P4-D120). The five facts above say how
            # long the values are and which alphabet they came from,
            # and between them they said nothing about their SHAPE --
            # which is why a column of UUIDs published every fact it
            # had and its twin matched none of its own rows.
            "layout_forms": layouts,
            # THE ONE LITERAL RUN THE BLOCK CARRIES, BY RULING (owner
            # ruling of 2026-09-17, item 1; contract 7.12a). Where every
            # present cell opens with the same text -- `REC`, `P`, `ABC-`
            # -- or every cell of one named layout does, that text is
            # published, so a pattern written against the twin selects
            # the rows it selects on the table. See `_layout_prefixes`.
            "layout_prefixes": _layout_prefixes(cells, layouts),
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


# How many of each unit a day holds. The seconds figure is the one
# `parsing` already counts a day in; the milliseconds figure is that
# one a thousand times over, computed here rather than typed.
_SECONDS_IN_A_DAY = 24 * 60 * 60
_EPOCH_BAND_UNITS_IN_A_DAY = {
    EPOCH_BAND_SECONDS: _SECONDS_IN_A_DAY,
    EPOCH_BAND_MILLISECONDS: _SECONDS_IN_A_DAY * 1000,
}


def _epoch_band_reading(cells: _Cells) -> "tuple[object, ...] | None":
    """This column read as moments in time, or None if it cannot be.

    Residual R-P4-9, contract NF51. Returns the arguments NF51 takes --
    which band, then the year, month and day of the smallest value and
    of the largest, read in that band -- or None where the column is
    not in either band.

    THE WALK IS OVER EVERY VALUE, AND WHAT THAT DOES AND DOES NOT BUY
    IS MEASURED RATHER THAN CLAIMED. A band is one interval, so on the
    role this is asked of -- where every value is a whole number by the
    role's own rule -- asking `min` and `max` answers the same question
    as asking every value. Rewriting the walk that way was run as a
    mutation and turned nothing red, which is the honest result: it is
    an equivalent rewrite and not an escaped defect. The walk stays
    because it makes this function right on ITS OWN terms rather than
    on its caller's -- a band ever written as two intervals, or a
    caller that ever asks this of a role admitting a value whose text
    does not settle it as whole, breaks the equivalence and not the
    walk. What the walk DOES rule out, on any role, is a column holding
    a number this format cannot hold: `len(numbers) != numeric_looking`
    above refuses it, because a cell too large to hold has no place in
    a band at all.

    WHY THE BAND STARTS IN THE YEAR 2000 rather than at zero is written
    where `EPOCH_BAND_FROM` is set: zero is the 1st of January 1970, so
    a band beginning there covers every ordinary count.

    Guarantees: accepts the tally of one column; returns NF51's
    arguments or None. Determinism: a function of the tallied numbers
    alone, and the bands are worked out from two calendar years by
    `parsing.days_from_civil`. Raises nothing. No I/O of any kind.
    """
    numbers = cells.numbers
    if not numbers or len(numbers) != _numeric_looking(cells):
        return None
    first_day = parsing.days_from_civil(EPOCH_BAND_FROM, 1, 1)
    last_day = parsing.days_from_civil(EPOCH_BAND_UNTIL, 1, 1)
    for band in (EPOCH_BAND_SECONDS, EPOCH_BAND_MILLISECONDS):
        each_day = _EPOCH_BAND_UNITS_IN_A_DAY[band]
        low = first_day * each_day
        high = last_day * each_day
        inside = True
        for value in numbers:
            # WHOLENESS BY ARITHMETIC, NOT BY `is_integer`, which is a
            # method call the offline audit refuses on a value it
            # cannot trace. The remainder is also the safer test at the
            # ends of the format: anything that is not a finite whole
            # number leaves a remainder that is not zero, so the same
            # line refuses it.
            if value % 1 != 0:
                inside = False
                break
            if value < low or value >= high:
                inside = False
                break
        if inside:
            smallest = parsing.civil_from_days(int(min(numbers)) // each_day)
            largest = parsing.civil_from_days(int(max(numbers)) // each_day)
            return (band,) + smallest + largest
    return None


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
        remarks += [note(REMARK_SOME_NOT_NUMBERS, (unparsed,))]
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
        remarks += [
            note(
                REMARK_NEAR_NUMERIC_LINE,
                (numeric_looking, n_present, strict_needed),
            )
        ]
    if cells.raw_distinct >= _needed(
        settings.identifier_uniqueness, n_present
    ):
        remarks += [note(REMARK_ALL_DIFFERENT_NUMBERS)]
    # ...AND A COLUMN WRITTEN WITH LEADING ZEROS SAYS SO TOO. The
    # all-different remark reaches a column whose every value differs,
    # which a column of codes is not: codes repeat, so that sentence
    # never fires on one. The affixed role has carried its own
    # `--identifier` pointer since P4-D4.1. Between the two, a column
    # of `00100` -- a procedure code, a vaccine code, a zip -- got no
    # pointer at all while being described as a quantity with an
    # average and a spread.
    #
    # AND ITS COUNT IS THE ONE THE FORMS MAP NAMES, or there is no remark
    # (plan P4-D221; stage 2 closed by the owner rulings of 2026-09-17).
    # It was counted off the cells so that padding too rare to name was
    # still told, and that told it: 1,200 prices with one padded cell
    # carried "1 of this column's values are written with a leading zero"
    # at every floor, beside a forms map that pooled the cell. A count the
    # map does not name is a count no sentence prints.
    padded = _padded_cells(cells)
    styles = _numeric_styles(cells)
    if padded and parsing.STYLE_LEADING_ZERO in styles:
        remarks += [
            note(REMARK_PADDED_NUMBERS, (styles[parsing.STYLE_LEADING_ZERO],))
        ]
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
        # ...AND A COLUMN OF WHOLE NUMBERS THAT ARE ALL MOMENTS IN TIME
        # SAYS SO (residual R-P4-9, contract NF51). It is asked only of
        # this role because the band is a band of whole non-negative
        # numbers, which is what this role means. The remark ROUTES
        # NOTHING and there is nothing for it to route to: no rule here
        # reads a number as a time and no declaration makes one, so the
        # column stays a count either way and every published fact of
        # it is the same fact. What changes is that its owner is told.
        band = _epoch_band_reading(cells)
        if band is not None:
            remarks += [note(REMARK_EPOCH_BAND, band)]
    else:
        evidence = note(EVIDENCE_NUMBERS, (numeric_looking, n_present))
    details = _numeric_details(cells, whole_everywhere)
    if role == ROLE_COUNT:
        # EVERY SPELLING, WHERE ONE NUMBER WAS WRITTEN MORE THAN ONE WAY
        # (plan P4-D123, the audit's missed item on mixed padding). The
        # count role alone: a column holding a negative is not a column
        # of codes written `007` beside `7`.
        details["number_spellings"] = _number_spellings(cells)
    # A spread larger than this file format can hold is a fact the
    # profile records in a field of its own, and it is also a fact the
    # person running the tool has to be told in words: without this
    # remark the only sign of it is a null where a number belongs
    # (review item P1-R6-F3).
    if details["std_unrepresentable"]:
        remarks += [note(REMARK_SPREAD_OUT_OF_RANGE)]
    # AND A SHAPE THIS COLUMN COULD NOT PUBLISH IS SAID IN WORDS. The
    # histogram is all or nothing, so a column whose values spread too
    # thinly for the floor publishes an EMPTY object -- and an empty
    # object beside a column full of numbers is exactly the silence
    # this file's other withheld-census notes exist to break. Without
    # it the only sign is an absence, and a reader cannot tell a shape
    # that was held back from a column that never had one.
    if numeric_looking > 0 and not details["value_histogram"]:
        notes += [note(NOTE_HISTOGRAM_WITHHELD)]
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
        counted = _counts_only(entries[place])
        # THE SPELLINGS GO WITH THE CANDIDATE (repair pass of landing
        # 2b.6). A column that publishes no value of the table
        # publishes no spelling of one, here as in `missing_by_source`
        # -- and this key is a LIST, so what stands for "withheld" in
        # it is emptiness rather than the word `_counts_only` writes
        # into every other key that could carry a value.
        counted["spellings"] = []
        withheld += [counted]
    # ...AND THE SPELLINGS OF ABSENCE ARE NOT VALUES OF THE TABLE, so
    # the ones drawn from synthtwin's OWN vocabulary stay (plan P4-D85).
    # The map was emptied whole, which threw away the one thing here
    # that was never anybody's data: `NA`, `N/A` and `NULL` are words
    # this package ships, identical in every installation, and C6-31
    # says in terms that the published vocabulary "contains no text
    # from any table". Emptying them cost the twin its holes and cost
    # the description its own readability -- a 500-row free-text column
    # with 174 `NA`/`N/A` cells published `n_missing: 275` and named no
    # spelling, so the table it was written from was re-described as
    # holding 399 present cells against the published 225 and MISSED
    # both presence counts: the real table failing its own description,
    # loudly, on the plainest run there is.
    #
    # WHAT DOES NOT COME BACK IS A PERSON'S OWN WORD, and the reason is
    # that a LOADER CANNOT CHECK IT. A declaration is recorded as a
    # count and never as text (C5-17), so a document naming
    # `Not documented` here could not be told from one naming a value of
    # the column, and the rule this format can enforce is the one it
    # states: a key of a nothing-publishing column names a member of the
    # published vocabulary. A declared spelling of the person's own
    # words stays in the pooled remainder, which is the narrowing this
    # decision takes deliberately rather than a gap it missed.
    # THE CELLS THE CLASS WITHHOLDS ARE NOT ADDED TO THE POOLED
    # REMAINDER, and that is a rule rather than an oversight. The
    # remainder is what the FLOOR held back, and a description written
    # at a floor of one holds nothing back because there is no group
    # below one (C5-S13, enforced by the publication guard and by the
    # loader). A spelling this class withholds is withheld for another
    # reason entirely, at every floor, so counting it there would make a
    # floor-one description claim a floor-one description cannot make
    # and would be refused by synthtwin's own guard before it was
    # written. Those cells stay exactly where they were before this
    # decision: counted in `n_missing`, and accounted for by nothing.
    # C6-126 states the consequence at its true size -- on such a column
    # the three accounted numbers do not exceed `n_missing` rather than
    # coming to it.
    vocabulary: dict[str, int] = {}
    for spelling in sorted(by_source):
        if parsing.names_a_published_word(spelling):
            vocabulary[spelling] = by_source[spelling]
    return _counts_only(details), vocabulary, withheld, n_blank, n_withheld


def profile_column(
    name: str,
    position: int,
    values: list[str],
    n_rows: int,
    settings: Settings,
    forced_identifier: bool = False,
    forced_code: bool = False,
    forced_measurement: bool = False,
    forced_decimal_comma: bool = False,
    described_as_pair: bool = False,
    kept_placeholder_days: "tuple[str, ...]" = (),
    judged_candidates: "tuple[str, ...]" = (),
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
    - ``described_as_pair`` is not a declaration and no person sets it:
      the validator sets it on a column its description read as a
      slashed pair of whole numbers from the values, so the checked
      file is read the way the description was (plan P4-D40,
      validation method V2.2-A2). `_decide` states what it moves.
    - ``kept_placeholder_days`` is not a declaration either, and no person
      sets it: the validator hands over the placeholder days the checked
      description published as `kept_by_you` in this column, so the file
      keeps them exactly as the description did (plan P4-D136).
    - ``judged_candidates`` is the other side of the same hand-over, and
      no person sets it either: the candidates -- stand-in numbers and
      placeholder days alike -- the checked description published as
      `read_as_missing` in this column. Each is read as missing here
      without its outlier and share rules being asked again (plan
      P4-D6.4, validation method V2.4-A8), because the twin writes those
      cells as the source wrote them and its own values need not fire
      the rules a second time. `synthtwin profile` never passes it.
    - Errors raised: TypeError if a value is not text (an internal
      invariant: both readers produce text), and ValueError when the
      settings name one value BOTH as data and as "no value" -- there
      is no reading of that pair that is not a guess, so it is refused
      before anything is described (review item P1-R6-F9). No refusal
      comes from the VALUES of a column: one that matches no rule is
      described as free text rather than rejected.
    - Boundary: no file is opened, and no value of a suppressed kind
      (identifier, free text, a number no format can hold, or a label
      below the small-cell floor) appears in the returned description,
      and no pool of one level on one row is left for a reader to read a
      count of one off -- the cells of such a level are counted as
      missing, spelled as nothing, by the level pass (the owner's ruling
      of 2026-09-17, item 5; plan P4-D231).
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
        settings.kept_values,
        settings.declared_missing_values,
        forced_decimal_comma,
    )
    if clashes:
        raise ValueError(f"{CONTRADICTORY_DECLARATION}: {clashes[0]}")
    present, missing = split_missing(
        values, settings, forced_decimal_comma
    )
    # THE one classification of this column's cells. Everything below
    # reads these records; not one line of it reads the column again.
    classified = _classify_all(present, forced_decimal_comma)
    # The second half of what the person declared, and the half that has
    # to wait for the classification: a declared NUMBER is compared with
    # the number a cell holds, not with the way the file spells it
    # (review item P1-R6-F9). It runs before the cells are counted, so
    # no rule and no statistic ever sees a value the person called "no
    # value".
    classified, declared = _declared_numbers_removed(
        classified, settings, forced_decimal_comma
    )
    missing = missing + declared
    # WHICH JUDGED PASS TOOK WHICH SPELLING (repair pass of landing
    # 2b.6, contract V5). Gathered at each of the three places a pass
    # removes a cell, because that is the only place it is known: after
    # the removal the classes are counted and the spellings are
    # counted, and neither says which pass a spelling came from.
    # Everything above this line is a DECLARATION -- `split_missing`
    # and `_declared_numbers_removed` -- so nothing the person named
    # can reach this record.
    judged_spellings: "dict[str, dict[str, int]]" = {}
    cells = _tally(classified, n_rows, settings, forced_decimal_comma)
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
        verdicts = _sentinel_verdicts(
            cells, len(present), judged_candidates
        )
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
                    # WHICH candidate took it, written the way the
                    # verdict will publish it, so the two cannot drift.
                    place = 0
                    for step in range(len(removed)):
                        if removed[step] == cell.exact:
                            place = step
                    _spelling_judged(
                        judged_spellings,
                        f"{withheld[place]:g}",
                        cell.text,
                    )
                else:
                    kept += [cell]
            classified = kept
            # Every population is counted again from the surviving
            # RECORDS; none is patched, and no cell is classified twice.
            # Reading the column a second time here was the last place
            # where two readings of one cell could have differed
            # (review item P1-R6-F10).
            cells = _tally(
                classified, n_rows, settings, forced_decimal_comma
            )
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
            described_as_pair=described_as_pair,
        )
        if trial.role == ROLE_TEXT or trial.role == ROLE_DATETIME:
            reading = _remainder_reading(present, settings)
            if reading is not None:
                day_verdicts = _placeholder_verdicts(
                    present,
                    reading,
                    settings,
                    forced_decimal_comma,
                    kept_placeholder_days,
                    judged_candidates,
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
                            # The candidate is the canonical day, which
                            # is exactly what the verdict publishes.
                            _spelling_judged(
                                judged_spellings, found, cell.text
                            )
                            removed_by_days = removed_by_days + 1
                        else:
                            kept_cells += [cell]
                    classified = kept_cells
                    cells = _tally(
                classified, n_rows, settings, forced_decimal_comma
            )
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
            described_as_pair=described_as_pair,
        )
        if trial.role == ROLE_AFFIXED:
            before = len(present)
            classified, missing, verdicts = _cores_judged(
                cells,
                classified,
                missing,
                verdicts,
                judged_spellings,
                forced_measurement,
                judged_candidates,
            )
            cells = _tally(
                classified, n_rows, settings, forced_decimal_comma
            )
            present = cells.present
            # HOW MANY THE CORE PASS TOOK, carried to the verdict below.
            # Removal can move a column across the detection line -- a
            # pair whose count is eaten below the floor lands on a later
            # rule -- and the remark of the role it lands on has to say
            # so, or the reader is told a count of a column that no
            # longer exists (contract C6-5).
            removed_by_cores = before - len(present)
            judged_over_cores = True

    # THE LEVEL PASS: a label column's lone row that a reader could read
    # by subtraction is counted as missing (the owner's ruling of
    # 2026-09-17, item 5; plan P4-D231). The three passes above take out
    # cells that stand for "no value"; this one takes out cells whose
    # VALUE the floor will not let the column name, and it takes them
    # out for the reason the floor exists. A pool of one level on one
    # row IS a count of one, whether or not a key prints it (B3), so a
    # column of 480 `F`, 519 `M` and one `U` at a floor of eleven told
    # every reader that one row holds a third value -- and its twin
    # wrote an invented label in exactly one row, which is that person's
    # row. The cells are counted as missing, spelled as nothing, so the
    # description is that of the table with those cells blank: no count
    # is left to be worked out, and the twin writes a blank there.
    #
    # ITS ORDERING IS THE OTHER PASSES' (C6-5, A-P4-1 item 3). The role
    # is decided first and then decided again, because taking cells out
    # changes every count; the trial reading below is what says whether
    # this column publishes a level list at all, and `_decide` is then
    # asked again with `after_levels`, which holds the second reading to
    # the label rules.
    #
    # THE GATE IS CHEAP. No level below the floor means no pool at all,
    # and at a floor of one there is no such level, so no run at that
    # floor is charged for a second reading.
    judged_over_levels = False
    if (
        present
        and not forced_identifier
        and _a_level_is_below_the_floor(cells)
    ):
        trial = _decide(
            cells,
            forced_identifier,
            removed_by_cores,
            after_removal=judged_over_cores,
            after_days=judged_over_days,
            forced_code=forced_code,
            forced_measurement=forced_measurement,
            described_as_pair=described_as_pair,
        )
        counted_out = _levels_read_by_subtraction(cells, trial.role)
        if counted_out:
            # AND WHETHER THE LABEL RULES ALONE MAY DECIDE AGAIN. On a
            # column of LABELS they must: the cells this pass removed
            # are the ones that were keeping the parse-rate rules out,
            # and re-asking those rules would let a removal claim a
            # column no rule would have given it (C6-5). On a column of
            # numbers BESIDE labels they must not: what the pass removes
            # there is the whole of a label half the floor would not
            # name, and the numbers left were numbers all along --
            # measured, 98 readings beside two `trace` cells became FREE
            # TEXT and published no number at all, where the honest
            # answer is a column of 98 numbers with two holes.
            labels_alone = trial.role in _LEVEL_ROLES
            level_kept: list[_Cell] = []
            for cell in classified:
                if cell.folded in counted_out:
                    # THE SPELLING IS NOT CARRIED OVER, and that is the
                    # whole point. A cell counted absent under its own
                    # spelling would put that spelling in
                    # `missing_by_source` or in the pool beside it, and
                    # a reader who can tell such a cell from an ordinary
                    # blank has been told the count this pass exists to
                    # withhold.
                    missing += [("", parsing.MISSING_BLANK)]
                else:
                    level_kept += [cell]
            classified = level_kept
            cells = _tally(
                classified, n_rows, settings, forced_decimal_comma
            )
            present = cells.present
            judged_over_levels = labels_alone
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
            after_levels=judged_over_levels,
            forced_code=forced_code,
            forced_measurement=forced_measurement,
            described_as_pair=described_as_pair,
        )

    by_source, by_class, n_blank, n_withheld = _missing_maps(
        missing, settings, entries, judged_spellings
    )
    # AND EACH DECISION'S OWN SPELLINGS, filled once the floor has said
    # which spellings may be named at all (contract V5).
    entries = _judged_spellings_published(
        entries, judged_spellings, by_source
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
    # THE FOUR COUNTS OF WHAT THE CELLS READ AS, AS THE BLOCK PUBLISHES
    # THEM (plan P4-D277). Read once, because they are one partition.
    numeric, out_of_range, contradictory, not_numeric = (
        _published_reading_split(cells, verdict.role)
    )
    # THE TWO REMARKS THAT RESTATE A KEY READ THE KEY AS PUBLISHED
    # (plan P4-D333). They were built from the TALLY, before the role
    # was known, and the role decides whether the four-way reading
    # split is published at all: on a declared identifier P4-D277
    # absorbs it, so a column of 25 record numbers holding one `5e999`
    # published `n_out_of_range: 0` and a remark saying one value was
    # out of range -- a count of one that no key of the block carried,
    # which is exactly what the binding guard refuses. The remark now
    # says what the key says, and where the key says nought there is
    # no remark: the reading it is about is one this role does not
    # publish.
    remarks: list[Note] = []
    if out_of_range:
        remarks += [note(REMARK_OUT_OF_RANGE, (out_of_range,))]
    if contradictory:
        remarks += [note(REMARK_CONTRADICTORY, (contradictory,))]
    if unpublished:
        remarks += [note(REMARK_RARE_SENTINELS, (unpublished,))]
    # THE FLOOR, ASKED OF THE SENTENCES (plan P4-D334). Every count a
    # sentence restates is a published key and the key answered for it
    # already; the thirteen that no key carries are asked here, in the
    # one place a column's sentences are finished, so a remark added
    # anywhere upstream is covered without its author remembering.
    said, said_remarks = sentences_at_the_line(
        verdict.evidence, remarks + verdict.remarks, n_present, settings
    )
    return ColumnProfile(
        name=name,
        position=position,
        role=verdict.role,
        statistical_type=statistical_type,
        quality_state=quality_state,
        structural_role=structural_role,
        detection_evidence=said,
        n_present=n_present,
        n_missing=n_missing,
        missing_by_source=by_source,
        missing_by_class=by_class,
        n_missing_blank=n_blank,
        n_missing_withheld=n_withheld,
        details=details,
        publication_notes=verdict.notes,
        remarks=said_remarks,
        n_numeric=numeric,
        n_out_of_range=out_of_range,
        n_contradictory=contradictory,
        n_not_numeric=not_numeric,
        n_distinct=_column_distinct(cells, verdict.role, details),
        n_distinct_folded=len(cells.folded_counts),
        sentinel_verdicts=entries,
        n_sentinel_candidates_unpublished=unpublished,
        absent_spellings=_spellings_of(missing),
    )


# THE TWO FLOORED POSITIONS THE RENDERING COMPARES WITH EACH OTHER.
# NF36 chooses which of its three sentences to write by asking whether
# the day-first reach is above, below or equal to the month-first one,
# so a fragment standing in either would settle the sentence by a
# number nobody may print -- and the reader could take one reach off
# the present cells to recover the contradiction count the same
# sentence's own floor withholds. Where the floor will not let both be
# named, this remark is not written at all.
_COMPARED_FLOORED_POSITIONS = (
    (REMARK_SLASHED_EVIDENCE, 0),
    (REMARK_SLASHED_EVIDENCE, 1),
)

# What `_floored_stands` answers.
_STANDS_AS_WRITTEN = "as written"
_STANDS_AS_THE_FRAGMENT = "the fragment"
_STANDS_NOWHERE = "no sentence"


def _floored_stands(
    form: str, place: int, value: int, line: int, n_present: int
) -> str:
    """Whether one floored argument may be printed, and as what.

    THE FLOOR, ASKED OF THE THIRTEEN POSITIONS NO KEY COVERS (plan
    P4-D334). Everywhere else a sentence restates a key and the key's
    own rule governs it; here the sentence IS the publication.

    Three answers, and the reasons are the census's own:

    * AS WRITTEN, for nought -- which names nobody -- and for a count
      that reaches the line with nothing left below it.
    * THE FRAGMENT, for one or more below the line: the reader is told
      the shape of the number and never the number.
    * NO SENTENCE, where the fragment cannot say it. That is three
      cases. A LINE OF TWO, where "fewer than 2" beside a clause
      asserting such cells exist is a count of one said in words --
      which is what `parsing.census_floor` exists to refuse, at every
      floor a person may ask for. A position the RENDERING COMPARES,
      which would decide the sentence by the number it withholds. And
      a count that reaches the line but leaves a group below it
      against a population its BINDING names, where printing the count
      would publish the remainder by subtraction. FOUR OF THE THIRTEEN
      NAME ONE (contract C6-143): the comma remark's two counts, the
      affix reading's reach and the date reading's reach, whose
      complements are spelling or affix census groups the block's own
      keys withhold.

    What "no sentence" means next is `_arguments_at_the_line`'s to
    decide, and it is not the same in the two cases: a remark is
    withdrawn, and the one sentence a block may not lose is written
    with `said_fewer_than_the_line` where the count is below the line
    and `said_some_but_not_all` where it reaches it. The second is
    there because the first would be FALSE of a count of 1,199.

    Guarantees: accepts a form, a zero-based position, the count, the
    census line and the block's present cells; returns one of the
    three answers above. Determinism: a fixed function of the five.
    Raises nothing. No I/O of any kind.
    """
    if value < 0:
        return _STANDS_AS_WRITTEN
    if 0 < value < line:
        if line <= parsing.MIDNIGHT_DISCLOSURE_FLOOR:
            return _STANDS_NOWHERE
        if (form, place) in _COMPARED_FLOORED_POSITIONS:
            return _STANDS_NOWHERE
        return _STANDS_AS_THE_FRAGMENT
    binding = argument_binding(form, place)
    if len(binding) < 2 or not isinstance(binding[1], tuple):
        return _STANDS_AS_WRITTEN
    for population in binding[1]:
        if population != "n_present":
            continue
        rest = n_present - value
        if 0 < rest < line:
            return _STANDS_NOWHERE
    return _STANDS_AS_WRITTEN


def _sentence_at_the_line(
    sentence: Note, line: int, n_present: int, may_drop: bool
) -> "Note | None":
    """One sentence with every floored count the floor will not let it print.

    Walks the form's own arguments and the arguments of every fragment
    nested in them, because a count carried by a fragment is a count
    the sentence prints. ``may_drop`` is false for the one sentence a
    column must carry -- its detection evidence -- so a fragment
    stands there at every line: `said_fewer_than_the_line` where the
    count is below the line, and `said_some_but_not_all` where it
    reaches the line but leaves a group below it against the
    population its binding names. THE SECOND IS NOT A REWORDING OF THE
    FIRST. "fewer than 11" is false of 1,199, and writing the digits
    instead is what `profile._floored_argument_is_bound` refuses -- so
    before the repair pass an ordinary table with 390 dates beside ten
    words became an internal fault the moment a binding named a
    population.

    AND AT A LINE OF TWO THAT IS NOT LESS THAN THE DIGIT, which is
    stated rather than claimed away. The fragment stands only where
    the count is one or more, so "fewer than 2" is one said in other
    words -- exactly what the digit it replaces said, and the reason
    every sentence that CAN be withdrawn is withdrawn there instead.
    Above a line of two it says strictly less. Measured at
    `--smallest-group 1`: 399 free-text cells beside one date write
    "fewer than 2 read as dates" in their evidence, while the remark
    that repeats the same count is withdrawn. A block must say how it
    was read, so its evidence keeps what the digit said and never
    more.

    Guarantees: accepts a sentence, the census line, the block's
    present cells and whether the sentence may be withdrawn; returns
    the sentence, a rebuilt one, or None where it may not be published.
    Determinism: a fixed function of the four. No I/O of any kind.
    """
    rebuilt = _arguments_at_the_line(
        sentence.form, sentence.arguments, line, n_present, may_drop
    )
    if rebuilt is None:
        return None
    if rebuilt == sentence.arguments:
        return sentence
    return note(sentence.form, rebuilt)


def _arguments_at_the_line(
    form: str,
    arguments: "tuple[object, ...]",
    line: int,
    n_present: int,
    may_drop: bool,
) -> "tuple[object, ...] | None":
    """`_sentence_at_the_line` for one form's arguments, nested ones included."""
    written: "list[object]" = []
    for place in range(len(arguments)):
        argument = arguments[place]
        if isinstance(argument, tuple) and len(argument) == 2:
            inner = argument[1]
            if isinstance(argument[0], str) and isinstance(inner, tuple):
                deeper = _arguments_at_the_line(
                    argument[0], inner, line, n_present, may_drop
                )
                if deeper is None:
                    return None
                written += [(argument[0], deeper)]
                continue
        if isinstance(argument, bool) or not isinstance(argument, int):
            written += [argument]
            continue
        if argument_binding(form, place)[:1] != (BIND_FLOORED,):
            written += [argument]
            continue
        stands = _floored_stands(form, place, argument, line, n_present)
        if stands == _STANDS_NOWHERE and may_drop:
            return None
        if stands == _STANDS_AS_WRITTEN:
            written += [argument]
            continue
        if stands == _STANDS_NOWHERE and argument >= line:
            # THE ONE SENTENCE A BLOCK MAY NOT LOSE, AT A COUNT THAT
            # REACHES THE LINE. This is the complement case: the count
            # is large and the group it leaves over against its
            # population is not. The digits stood here until the
            # repair pass, which made the producer write exactly what
            # `profile._floored_argument_is_bound` refuses -- so the
            # first binding to name a population turned an ordinary
            # table into an internal fault instead of a description.
            # NF59 cannot stand here either: "fewer than 11" is false
            # of 1,199. NF60 is what is left that is true, and it
            # names no number at all.
            written += [(SAID_SOME_BUT_NOT_ALL, ())]
            continue
        written += [(SAID_FEWER_THAN_THE_LINE, (line,))]
    return tuple(written)


def sentences_at_the_line(
    evidence: Note,
    remarks: "list[Note]",
    n_present: int,
    settings: Settings,
) -> "tuple[Note, list[Note]]":
    """Every sentence of one column, with no count below the census line.

    THE PRODUCER'S HALF of the binding guard (plan P4-D334). The guard
    in `profile.check_publication` refuses a document whose sentence
    carries a count a key withholds; this is what keeps the producer's
    own documents clear of one, in the single place every column's
    sentences are finished, so no call site can forget it.

    A remark that cannot be written is WITHDRAWN rather than reworded:
    its whole subject is a count the floor will not name, and a
    sentence that said so in other words would be the same disclosure
    with a longer sentence in front of it. The detection evidence is
    never withdrawn -- a column block must say how it was read -- so
    its floored counts take a fragment.

    THAT RULE COSTS A WARNING, and the cost is stated rather than
    claimed away. The comma remark of 1,199 grouped prices beside one
    bare cell is withdrawn here: it was a load-bearing warning about
    1,199 cells that may be a thousand times their real size, and what
    withdraws it is the single ungrouped cell a reader would otherwise
    take off the published `n_present`. Keeping the warning and
    printing no count is what `said_some_but_not_all` does for the
    sentence that cannot be withdrawn; extending it to remarks is an
    owner-sized question about what a description is FOR, and is on
    the board rather than taken here.

    Guarantees: accepts a column's detection evidence, its remarks, its
    present cells and the settings; returns the evidence and the
    remarks that may be published, in their given order. Determinism: a
    fixed function of the four. Raises nothing. No I/O of any kind.
    """
    line = parsing.census_floor(settings.small_cell_floor)
    kept: "list[Note]" = []
    for remark in remarks:
        written = _sentence_at_the_line(remark, line, n_present, True)
        if written is not None:
            kept += [written]
    said = _sentence_at_the_line(evidence, line, n_present, False)
    return (evidence if said is None else said), kept


def _spellings_of(missing: "list[tuple[str, str]]") -> "tuple[str, ...]":
    """Each spelling an absent cell held, once, in sorted order."""
    seen: "dict[str, bool]" = {}
    for spelling, _kind in missing:
        seen[spelling] = True
    return tuple(sorted(seen))

### 6.7 `count` and `continuous` — the numeric roles

Both roles carry exactly the same key set — the fifteen keys below,
added to the universal set of section 5.1. They differ only in the
verdict that produced them.

**When a column takes one of these roles.** Rule 7 of the order in
section 5.2 claims a column when at least the parse-line count of its
present cells are NUMERIC-LOOKING — the cells `n_numeric`,
`n_out_of_range` and `n_contradictory` count between them — and at
least that same count are values this file format can hold, which is
`n_numeric`. The two tests share ONE line on purpose, and it is the
line section 6.2 states for `numeric_unrepresentable`: deciding the
numeric roles on the holdable count alone let three unrepresentable
cells stop the question being asked, and deciding them on the
numeric-looking count alone let a ladder be built from a single
holdable cell in a hundred. The population that decides a role and the
population its statistics are computed from are one population.
Falling short of the line decides nothing but this rule — the column
goes on to `categorical` and may still be a set of categories.

**Which of the two: the column COUNTS THINGS, and takes role `count`,
when all three of these hold. It is `continuous` otherwise.**

1. Every numeric-looking cell's notation settles that its value is a
   WHOLE NUMBER, and there is at least one numeric-looking cell.
2. No present cell's notation settles a negative sign: `n_negative`
   is `0`.
3. No cell whose writer MEANT a number leaves its sign unsettled.

**The reasons, because each condition was bought.** A column of counts
must be whole and non-negative in every cell whose writer meant a
number, INCLUDING the ones no format can hold: `(1e999)` is visibly
negative and `1e-999` is visibly a fraction strictly between zero and
one, and both were published as whole non-negative counts before
review item P1-R5-F2. Condition 3 is the same principle applied to a
cell that settles nothing: a cell whose sign the text does not settle
is enough to rule the role out, because missing evidence is not
evidence of nothing.

**Condition 3 refuses no document condition 1 admits, under the
notation this format reads today**, and is stated anyway. The only
numeric-looking cell whose sign the text leaves unsettled is one whose
notation conflicts with itself — a sign inside accounting parentheses
— and such a cell settles the whole-number question no more than the
sign question, so it already fails condition 1. The two are different
questions, and a notation that settled wholeness without settling sign
would separate them; a reader checking this rule against an
implementation should know which of the three is doing the work.

**A straggler of ordinary text does not rule `count` out, and
condition 3 is narrow for exactly that reason.** The parse line
tolerates a slack of present cells that are not numeric notation at
all. Such a cell settles neither the sign question nor the whole-number
question, and it says nothing about whether this column counts things,
so it is not what condition 3 asks about: condition 3 ranges over the
cells whose writer meant a number and nothing else. This is
deliberately NARROWER than the published sign margin of section 6.2,
which runs over the whole present population because U2 must close on
`n_present`. The two are different questions and a producer that
answers one with the other either refuses a legitimate `count` column
or writes a description its own loader refuses.

**The choice is a PRODUCER rule.** Like the rule order itself
(section 5.2), it decides what a producer writes. A loader holds one
document and never the table it describes, so it cannot re-run the
three conditions; what a loader enforces about the pair is A4 — the
triple (`role`, `statistical_type`, `quality_state`) is one row of the
axes table — together with the Q family below. Q8 is what keeps a
consumer off the role name.

**Added keys:**

| key | JSON type | range | meaning | disposition |
|---|---|---|---|---|
| `percentiles` | ladder object | section 5.6 | the eleven-rung ladder over the PARSED values | `min` and `max` EXACT-OBSERVABLE; the nine interior rungs APPROXIMATED |
| `mean` | number or `null` | — | the arithmetic mean of the parsed values | APPROXIMATED |
| `std` | number or `null` | ≥ 0 when a number | the sample standard deviation, divided by n−1 | APPROXIMATED |
| `skew` | number or `null` | — | the moment-based skewness | APPROXIMATED |
| `std_unrepresentable` | boolean | — | true when the exact spread is larger than binary64 can hold | EXACT-OBSERVABLE |
| `n_zero` | integer ≥ 0 | — | parsed values equal to zero | EXACT-OBSERVABLE |
| `n_negative` | integer ≥ 0 | — | present cells whose notation settles a negative sign, including ones no statistic could use | EXACT-OBSERVABLE |
| `n_negative_unrepresentable` | integer ≥ 0 | — | out-of-range cells whose notation settles a negative sign | EXACT-OBSERVABLE |
| `n_used_in_statistics` | integer ≥ 0 | — | how many present cells the statistics were computed from | EXACT-OBSERVABLE |
| `n_left_out_of_statistics` | integer ≥ 0 | — | how many present cells were not | EXACT-OBSERVABLE |
| `numeric_share` | number | 0.0 ≤ x ≤ 1.0 | the share of present cells whose writer meant a number | EXACT-OBSERVABLE |
| `integer_valued` | boolean | — | true when every numeric-looking cell is a whole number | EXACT-OBSERVABLE, routed by the published FACT and not by role |
| `n_rows` | integer ≥ 0 | `== n_rows` at the top level | the table's row count, echoed | LOADER-ONLY |
| `numeric_styles` | object | section 7.5 | how many cells were written in each spelling style, under the floor | EXACT-OBSERVABLE against the recount identity of section 7.5.7 |
| `fraction_widths` | object | C6-28 to C6-30 below | how many `decimal`-styled cells were written at each fraction width, under the floor | EXACT-OBSERVABLE, under the producer obligation FW-P |

Fifteen keys. Every one is present in every block of these two roles —
this format has no optional keys — and every key not listed here or in
section 5.1 is FORBIDDEN on them (section 6.11).

**Where the approximations and the recounts are fixed.** The nine
interior rungs are APPROXIMATED inside a rung-by-rung two-sided
envelope, fixed by `docs/spec/generation-method-v1.md` G5.6 and
restated there as G12.2. A generator that collapses the nine interior
rungs onto the endpoints must FAIL that envelope, and so must one that
ignores, permutes or swaps rungs. `mean`, `std` and `skew` are
APPROXIMATED under a fixed formula and a two-sided bound, both fixed
by that document's G12.3. `numeric_styles` is EXACT-OBSERVABLE against
the recount identity of section 7.5.7: every published count is met or
exceeded, the three forms the remainder cannot reach are exact, and
the remainder is spelled by its own cells' values. `n_distinct` and
`n_distinct_folded` are universal keys whose disposition on this role
group is set in section 9.

**The ladder.** `percentiles` is the ladder — the fixed eleven rungs
of section 2.3 — read over the PARSED values. Section 5.6 states L1,
L2 and L3, including what a `null` rung means and what a generator
writes in its place, and this section adds nothing to them.

#### `numeric_styles` on these roles

`numeric_styles` is REQUIRED on `count`, `continuous` and
`affixed_number`, and FORBIDDEN on every other role including
`numeric_unrepresentable`. **The reason.** Those are the roles whose
twin cells are written as parsed numbers from the ladder in owner
decision 8's spelling family — on `affixed_number`, inside its affix
pair — so they are the roles where the reader's inferred type is at
stake and where a style map is something the generator can discharge.
A `numeric_unrepresentable` column's twin cells are invented digit
strings at one canonical width (residual R-P2-1), so a style map there
would describe a form the twin is already unable to reproduce.

**The fact is about FORM, not values.** It carries no value, no
magnitude and no spelling — only how many cells used each form. It
exists because three source families — `0`, `00`, `000`; `0.0`,
`00.0`, `000.0`; and `0e0`, `00e0`, `000e0` — otherwise produce
byte-for-byte identical column blocks, and an ordinary reader infers a
whole-number column from the first and a decimal column from the other
two.

**The styles are exactly these six, and no seventh may be added by an
implementation:**

| style | what it names |
|---|---|
| `plain` | the canonical spelling: digits, an optional leading minus, no decimal point, no exponent, no redundant leading zero |
| `leading_zero` | the digits before any decimal point begin with a redundant `0` |
| `leading_plus` | the cell begins with `+` |
| `decimal` | the cell carries a decimal point |
| `exponent_lower` | the cell carries a lower-case `e` exponent |
| `exponent_upper` | the cell carries an upper-case `E` exponent |

The wire shape, the first-match-wins classification ladder that assigns
each counted cell exactly one style, invariants P1 through P4 and the
twin's recount obligation are stated in section 7.5. What this section
fixes is that the key stands on these roles and on no others.

#### `fraction_widths`

**C6-27 (where it lives, and why not where it looks like it belongs).**
A `count`, `continuous` or `affixed_number` block carries
`fraction_widths` as a key of the BLOCK, a sibling of `numeric_styles`
and NOT a key inside it. Inside is where it reads as belonging, and
inside is impossible: invariant P1 requires every value of
`numeric_styles` to be an integer and requires those values to sum to
the numeric count, so an object placed among them breaks both. There is
exactly one location and it is the sibling one (plan amendment
A-P4-5). It is forbidden on every other role.

**C6-28 (what it holds).** A mapping from a fraction width — the count
of digits after the point — to the number of `decimal`-styled cells
written at that width, together with the pooled key `(withheld)` for
widths fewer than `small_cell_floor` cells share.

**C6-29 (the key grammar, so one width has one spelling).** A width key
is the decimal spelling of a non-negative integer: no sign, no leading
zero unless the width is itself zero, no space, no other character —
`0`, `1`, `2`, `10`. `02`, `+2` and `-1` are not width keys and a
loader refuses a document carrying one. The pooled key is exactly
`(withheld)` and is the only non-numeric key permitted. Section 3
fixes the order these keys are written in, which is code point order
and not numeric order.

**C6-30 (invariants).** The census this key holds is a census of the
DECIMAL-styled cells, so its invariants are stated by cases over what
`numeric_styles` publishes about that style. The cases are exhaustive
over the shapes `numeric_styles` can take, and every one of them binds
something.

**P5 (the sum, by cases).** Let *F* be the sum of ALL values of
`fraction_widths`, its own `(withheld)` value included.

- **P5.a — `numeric_styles` publishes a `decimal` key.** *F* equals
  that key's value exactly. This is the ordinary case and the strict
  equality the style invariants lead a reader to expect. That value is
  at or above the floor by P2, so the census is non-empty here.
- **P5.b — `numeric_styles` publishes no `decimal` key and no
  `(withheld)` key.** The column has no decimal-styled cell, so
  `fraction_widths` is the empty object and *F* is zero.
- **P5.c — `numeric_styles` publishes no `decimal` key but does
  publish `(withheld)`.** The decimal count, if there is one, was
  pooled, and no published number holds it. `fraction_widths` is
  EITHER the empty object — the column has no decimal cell at all and
  the pool holds other styles — OR it carries the pooled decimal cells
  under its own `(withheld)`. Write *W* for
  `numeric_styles["(withheld)"]`. FOUR conditions bind, and a document
  breaking any of them does not conform:

  1. *F* is at least 1 WHEREVER THE CENSUS IS NON-EMPTY. This
     condition alone is branch-scoped, and the scope is the whole of
     its content: it does not refuse the empty census, which P5.c's
     own first sentence admits (plan amendment A-P4-6);
  2. *F* is strictly BELOW `small_cell_floor`, because a style is
     pooled only when its own count falls below the floor;
  3. *F* is at most *W*, because the pooled decimal cells are a subset
     of the pool;
  4. **F ≥ W − 5 × (small_cell_floor − 1)** (plan amendment A-P4-8).
     There are exactly six numeric styles, so at most five share the
     pool with decimal, and each of those holds at most
     `small_cell_floor − 1` cells. Where the right-hand side is zero or
     negative this condition is vacuous.

  **What binds the EMPTY census is condition 4 read at *F* = 0**, and
  it is written out because a reader who has just been told condition 1
  does not reach that branch will otherwise read the branch as free.
  At *F* = 0 condition 4 says W ≤ 5 × (`small_cell_floor` − 1), which
  is exactly the arithmetic A-P4-8 appeals to when it permits the empty
  census where the right-hand side is zero or negative. At a floor of
  11, `numeric_styles: {"(withheld)": 51}` with `fraction_widths: {}`
  says five pooled styles hold fifty-one cells between them, so one of
  them holds eleven and would have been published by name; condition 4
  requires *F* ≥ 1 there and refuses it.

  **A corollary a reader should not have to derive.** In case P5.c
  `fraction_widths` is either the empty object or exactly
  `{"(withheld)": F}` with 1 ≤ *F* < `small_cell_floor`. No NAMED width
  key may appear, because every named width's count is at or above the
  floor by P6 while *F* is below it.

**Why conditions 3 and 4 exist, stated rather than quietly fixed.**
An earlier revision said of case P5.c that the sum "binds nothing." It
would have admitted `fraction_widths: {"(withheld)": 1000}` on a
hundred-cell column — a fraction census larger than the table, with no
rule to refuse it. What A-P4-5 correctly established is that an
invariant cannot be stated over a key that may not exist; what it
wrongly concluded is that nothing else can be stated. The bounds above
are stated over keys that DO exist in case P5.c, so they cost that
reasoning nothing. Condition 4 came from a later round, which found a
document satisfying conditions 1 through 3 and describing no table:
`n_numeric: 60` with `numeric_styles: {"(withheld)": 60}` and
`fraction_widths: {"(withheld)": 1}` at a floor of 11 makes the other
five styles hold fifty-nine cells between them, so one of them holds
twelve, and a style holding twelve at a floor of eleven is published by
name rather than pooled.

**P6.** Every named width's count is at or above `small_cell_floor`.
**P7.** A width key is present only if its count is nonzero;
equivalently, *F* is zero if and only if `fraction_widths` is the
empty object. This closes the route residual R-P3-12 records.

**FW-P (a producer obligation, stated because a loader cannot check
it).** Every `fraction_widths` count is the count of source cells
written at that fraction width. The cases of P5 bound the total; none
of them can check the shape of the census, so the shape is a producer
obligation.

**At a floor of one.** Where `small_cell_floor` is 1, what invariant
S13 requires to be empty or zero is the `(withheld)` ENTRY of
`fraction_widths` — the ENTRY, not the field, and section 4 states
that list entire. At a floor of one every named width reaches the
floor, so widths are NAMED rather than pooled, and the field is
nonempty precisely because nothing is held back.

#### The Q family

**Invariant Q1 (the echo).** The per-column `n_rows` equals the
document's `n_rows`. It appears ONLY inside `count`, `continuous` and
`affixed_number` blocks, and is FORBIDDEN on every other role. It is
LOADER-ONLY: the document-level `n_rows` is the one that carries the
row-count obligation, and conflating the two is the error plan
revision 2 made.

**Invariant Q2 (statistics population).**
`n_used_in_statistics == n_numeric` and
`n_left_out_of_statistics == n_present - n_numeric`.

**Invariant Q3 (the numeric roles always have numbers).**
`n_numeric >= 1`. A column reaches these roles only when the count of
values binary64 can hold clears `minimum_parse_rate` of the present
cells, so the ladder is never built from nothing.

**Invariant Q4 (`std` nulls).** `std` is `null` exactly when
`n_used_in_statistics < 2` or `std_unrepresentable` is true. Those two
are different facts and the contract keeps them apart: a null with the
flag false means undefined; a null with the flag true means a spread
larger than this format can hold. A reader never has to guess which.

**Invariant Q5 (`skew` nulls).** `skew` is `null` when
`n_used_in_statistics < 3`, and when every parsed value is identical.
It is a number otherwise.

**Invariant Q6 (`std` of one value).** When every parsed value is
identical and `n_used_in_statistics >= 2`, `std` is `0.0` and
`std_unrepresentable` is false.

**Invariant Q7 (`mean` nulls).** `mean` is `null` only when the exact
mean is not a finite binary64 value. It is a number in every producible
profile this contract knows of; a loader accepts `null` and a generator
treats it as an approximated field with no target, saying so in the
report.

**Invariant Q8 (`integer_valued` is a FACT, not a role).** The twin's
integer rule is routed by this published boolean and never by whether
the role name is `count`. A `continuous` column may publish
`integer_valued: true` — a column of whole numbers containing a
negative one is exactly that — and its twin cells are whole numbers.

**Invariant Q9 (`numeric_share`).** `numeric_share` is
`(n_numeric + n_out_of_range + n_contradictory) / n_present`, computed
as a share of the present cells, and is `0.0` when `n_present` is 0 —
which cannot occur on these roles by Q3.

**Invariant Q10 (`n_negative_unrepresentable` bound).**
`n_negative_unrepresentable <= n_out_of_range` and
`n_negative_unrepresentable <= n_negative`.

**Invariant Q11 (`n_zero` bound).** `n_zero <= n_numeric`.

**Where else this family is enforced.** On `affixed_number` every
invariant of this section is read over the CORES, with
`n_core_numeric` in place of `n_numeric` (AF7), and nowhere else. The
four universal cell-census counts answer for the cells on that role as
on every other.
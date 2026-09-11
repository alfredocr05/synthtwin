### 6.7 `count` and `continuous` — the numeric roles

Both roles carry exactly the same key set. They differ only in the
verdict that produced them, and that verdict is written out below
rather than left to be inferred from the role names.

**When a column reaches either role.** At least the parse-line count
of its present cells are NUMERIC-LOOKING — the cells `n_numeric`,
`n_out_of_range` and `n_contradictory` count between them — and at
least that same count are numbers this file format can hold, which is
`n_numeric` alone. The two tests share ONE line, and the line is
`minimum_parse_rate` applied as a count and never as a compared share.
They share it on purpose: deciding the numeric roles on the holdable
count alone let three unrepresentable cells stop the question being
asked, and deciding them on the numeric-looking count alone let a
ladder be built from a single holdable cell in a hundred — one row's
exact value published as eleven statistics. The population that
decides the role and the population the statistics are computed from
are one population. A column that clears the first test and fails the
second takes `numeric_unrepresentable`, which is tested earlier in the
rule order of section 5.2.

#### The rule that chooses between the two

A column COUNTS THINGS, and takes `count`, exactly when all three of
these hold:

1. every numeric-looking cell is a whole number — which is the same
   fact the block publishes as `integer_valued`;
2. no present cell's notation settles a negative sign — `n_negative`
   is `0`;
3. no cell whose writer MEANT a number leaves its sign unsettled.

Otherwise the column takes `continuous`.

**Why tests 1 and 2 reach cells no statistic could use.** `(1e999)`
is visibly negative and `1e-999` is visibly a fraction strictly
between zero and one, and neither is a value this format can hold.
Both were published as whole, non-negative counts until review item
P1-R5-F2, because the tests read only the cells the statistics used. A
column of counts must be whole and non-negative in every cell whose
writer meant a number, including the ones no format can hold.

**Why test 3 exists, and why it is narrower than it looks.** Missing
evidence is not evidence of nothing: a cell whose sign or whose
whole-number status the text does not settle is enough to rule the
role out. Notation that conflicts with itself — a sign inside
accounting parentheses, `(-5)` saying negative twice and `(+5)` saying
both — settles neither question, so tests 1 and 3 both reach it. But
ordinary text settles no sign either, and this role tolerates a slack
of ordinary-text stragglers below the parse line. A straggler of
ordinary text does not rule the role out, because the parse line
already tolerates it and it says nothing about whether this column
counts things. Test 3 therefore ranges over the numeric-looking cells
alone. This is deliberately narrower than the sign family published on
`numeric_unrepresentable`, where `n_sign_unknown` is a margin over
`n_present` and counts every present cell the text leaves unsettled,
ordinary text included. Test 2 needs no such narrowing: ordinary text
can never settle a negative sign, so `n_negative` over the present
cells and `n_negative` over the numeric-looking cells are the same
count.

**The rule is a PRODUCER rule.** The count test 3 reads is not a key
of this format — no block publishes it — so a loader holding one
document cannot re-run the rule, exactly as it cannot re-run the rule
order of section 5.2. What a loader enforces about the role is
invariant A4: the triple (`role`, `statistical_type`, `quality_state`)
is one row of the axes table, or the document is refused. Two
published consequences do follow from the rule and are named here
because a reader will look for them: a conforming `count` block always
carries `integer_valued: true` and `n_negative: 0`. Neither converse
holds — Q8 — and no clause of this contract makes either a loader
refusal.

#### Added keys

| key | JSON type | range | meaning | disposition |
|---|---|---|---|---|
| `percentiles` | ladder of numbers or nulls | the eleven rungs of section 5.6 | the ladder over the PARSED values | `min` and `max` EXACT-OBSERVABLE; the nine interior rungs APPROXIMATED |
| `mean` | number or `null` | — | the arithmetic mean of the parsed values | APPROXIMATED, fixed formula and two-sided bound |
| `std` | number or `null` | ≥ 0 when a number | the sample standard deviation, divided by n−1 | APPROXIMATED, fixed formula and two-sided bound |
| `skew` | number or `null` | — | the moment-based skewness | APPROXIMATED, fixed formula and two-sided bound |
| `std_unrepresentable` | boolean | — | true when the exact spread is larger than binary64 can hold | EXACT-OBSERVABLE |
| `n_zero` | integer ≥ 0 | ≤ `n_numeric` | parsed values equal to zero | EXACT-OBSERVABLE |
| `n_negative` | integer ≥ 0 | — | present cells whose notation settles a negative sign, including ones no statistic could use | EXACT-OBSERVABLE |
| `n_negative_unrepresentable` | integer ≥ 0 | ≤ `n_out_of_range`, ≤ `n_negative` | out-of-range cells whose notation settles a negative sign | EXACT-OBSERVABLE |
| `n_used_in_statistics` | integer ≥ 0 | `== n_numeric` | how many present cells the statistics were computed from | EXACT-OBSERVABLE |
| `n_left_out_of_statistics` | integer ≥ 0 | `== n_present - n_numeric` | how many present cells were not | EXACT-OBSERVABLE |
| `numeric_share` | number | 0.0 ≤ x ≤ 1.0 | the share of present cells whose writer meant a number | EXACT-OBSERVABLE |
| `integer_valued` | boolean | — | true when every numeric-looking cell is a whole number | EXACT-OBSERVABLE, routed by the published FACT and not by role |
| `n_rows` | integer ≥ 0 | `== n_rows` at the top level | the table's row count, echoed | LOADER-ONLY |
| `numeric_styles` | object | style name or `(withheld)` → integer ≥ 1 | how many of the `n_numeric` cells were written in each spelling style, under the floor | EXACT-OBSERVABLE against the recount identity of the numeric-styles section |
| `fraction_widths` | object | width key or `(withheld)` → integer ≥ 1 | how many `decimal`-styled cells were written at each fraction width, under the floor | EXACT-OBSERVABLE, with the census SHAPE a producer obligation (FW-P) |

Fifteen keys, and the forbidden-key matrix of section 6.11 carries the
same fifteen in each of the two columns.

**The ladder is the one of section 5.6** — the eleven rungs `min`,
`p01`, `p05`, `p10`, `p25`, `p50`, `p75`, `p90`, `p95`, `p99`, `max`,
non-decreasing (L1), with `min` the smallest parsed value and `max`
the largest (L2), and a rung permitted to be `null` under L3. The two
endpoints are the rungs a generator pins by fixed rule and they are
EXACT-OBSERVABLE; the nine interior rungs are APPROXIMATED inside a
rung-by-rung two-sided envelope. A mutant that collapses the nine
interior rungs onto the endpoints must FAIL the rung envelope. So must
a mutant that ignores, permutes or swaps rungs.

#### `numeric_styles` on these roles

`numeric_styles` is REQUIRED on `count`, `continuous` and
`affixed_number`, and is FORBIDDEN on every other role including
`numeric_unrepresentable`. These are the three roles whose twin cells
are written as parsed numbers from the ladder — on `affixed_number`,
as a parsed number inside the affix pair — so the reader's inferred
type is what is at stake and a style map is something the generator
can discharge. A `numeric_unrepresentable` column's twin cells are
invented digit strings inside a published length range, so a style map
there would describe a form the twin is already unable to reproduce.

The six styles, the first-match-wins classification ladder that
assigns each counted cell exactly one of them, the wire shape, and
invariants P1 through P4 are stated once, in the numeric-styles
section, and are not restated here. What this section needs from them,
and states because the fraction-width invariants below rest on it, is
the floor's two directions together: a style whose own count reaches
`small_cell_floor` is published BY NAME and is never pooled, and a
style whose count falls below the floor has no key of its own and its
cells are pooled into `(withheld)`. P2 bounds the named values from
below — every value under a style name is at least
`small_cell_floor` — and that is the converse rather than the
direction the bounds below need. The direction they need is what
`(withheld)` MEANS: a group too small to name, counted rather than
named. Nothing at or above the floor is in the pool, because the pool
is precisely the remainder the floor held back.

#### `fraction_widths`

**C6-27 (where it lives, and why not where it looks like it belongs).**
A `count`, `continuous` or `affixed_number` block carries
`fraction_widths` as a key of the BLOCK, a sibling of `numeric_styles`
and NOT a key inside it. Inside is where it reads as belonging, and
inside is impossible: P1 requires every value of `numeric_styles` to
be an integer and requires them to sum to the numeric count, so an
object placed among them breaks both. The ratified plan placed it
inside; the plan governs, so the plan was amended rather than this
document deviating from it — **plan amendment A-P4-5**, which fixes
the sibling placement and states this reason. There is exactly one
location for this key, and it is the sibling one.

**C6-28 (what it holds).** A mapping from a fraction width — the count
of digits after the point — to the number of `decimal`-styled cells
written at that width, together with the pooled key `(withheld)` for
widths fewer than `small_cell_floor` cells share.

**C6-29 (the key grammar, so one width has one spelling).** A width
key is the decimal spelling of a non-negative integer: no sign, no
leading zero unless the width is itself zero, no space, no other
character — `0`, `1`, `2`, `10`. `02`, `+2` and `-1` are not width
keys and a loader refuses a document carrying one. The pooled key is
exactly `(withheld)` and is the only non-numeric key permitted.

**C6-30 (invariants).** The census this key holds is a census of the
DECIMAL-styled cells, so its invariants are stated by cases over what
`numeric_styles` publishes about that style. The cases are exhaustive
over the shapes `numeric_styles` can take, and every one of them binds
something (plan amendments A-P4-5, A-P4-6 and A-P4-8).

**P5 (the sum, by cases).** Let *F* be the sum of ALL values of
`fraction_widths`, its own `(withheld)` value included, and let *W* be
the value of `numeric_styles["(withheld)"]` where that key is present.
An empty census has *F* = 0, and every condition below that is stated
over *F* is read at that value.

- **P5.a — `numeric_styles` publishes a `decimal` key.** *F* equals
  that key's value exactly. This is the ordinary case and the strict
  equality the style invariants would lead a reader to expect. By P2
  that value is at least `small_cell_floor`, so `fraction_widths` is
  non-empty here.
- **P5.b — `numeric_styles` publishes no `decimal` key and no
  `(withheld)` key.** The column has no decimal-styled cell, so
  `fraction_widths` is the empty object and *F* is zero.
- **P5.c — `numeric_styles` publishes no `decimal` key but does
  publish `(withheld)`.** The decimal count, if there is one, was
  pooled, and no published number holds it. `fraction_widths` is
  EITHER the empty object — the column has no decimal cell and the
  pool holds other styles — OR it carries the pooled decimal cells
  under its own `(withheld)`. FOUR conditions bind, and a document
  breaking any of them does not conform:

  1. *F* is at least 1 wherever the census is NON-EMPTY (plan
     amendment A-P4-6). This is the one condition confined to that
     branch, because an empty census is what a column with no decimal
     cell at all writes;
  2. *F* is strictly BELOW `small_cell_floor`, because a style is
     pooled only when its own count falls below the floor;
  3. *F* is at most *W*, because the pooled decimal cells are a subset
     of the pool;
  4. ***F* ≥ *W* − 5 × (`small_cell_floor` − 1)** (plan amendment
     A-P4-8). There are exactly six numeric styles, so at most five
     share the pool with decimal, and each of those holds at most
     `small_cell_floor` − 1 cells. Where the right-hand side is zero
     or negative this condition is vacuous. Without it, `n_numeric:
     60` with `numeric_styles: {"(withheld)": 60}` and
     `fraction_widths: {"(withheld)": 1}` at a floor of 11 satisfies
     conditions 1 through 3 and still describes no table: the other
     five styles would have to hold fifty-nine cells between them, so
     one of them holds twelve, and a style holding twelve at a floor
     of eleven is published by name rather than pooled.

**Condition 4 is also what admits or refuses an EMPTY census, and no
separate rule is needed for it.** *F* is the sum of all values of the
census, so an empty census has *F* = 0 and condition 4 reads *W* ≤ 5 ×
(`small_cell_floor` − 1): the whole of the pool is then made of the
five styles other than decimal, each holding at most
`small_cell_floor` − 1 cells. That is exactly where amendment A-P4-8's
own closing sentence puts it — the census may be empty where that
condition's right-hand side is zero or negative. Read at *F* = 0 it
refuses a document carrying `n_numeric: 51`, `numeric_styles:
{"(withheld)": 51}` and `fraction_widths: {}` at a floor of 11, which
conditions 2 and 3 admit and which describes no table: fifty-one cells
cannot be shared by five styles holding at most ten each.

**P6.** Every named width's count is at or above `small_cell_floor`.
**P7.** A width key is present only if its count is nonzero. This
closes the route residual R-P3-12 records.

**A consequence of P6 with P5.c, stated because a reader will look for
it and it is not an extra rule.** Where `numeric_styles` publishes no
`decimal` key, `fraction_widths` is either the empty object or exactly
`{"(withheld)": F}` with 1 ≤ *F* ≤ `small_cell_floor` − 1. No NAMED
width key can appear there: every named width's count is at least the
floor by P6, and the whole census totals less than the floor by
condition 2, so no width can reach it.

**Why this key has needed three amendments.** Revision 3 said of case
P5.c that the sum "binds nothing," and that was wrong in a way worth
naming rather than quietly fixing: it would have admitted
`fraction_widths: {"(withheld)": 1000}` on a hundred-cell column, a
fraction census larger than the table, with no rule to refuse it.
A-P4-5 correctly established that an invariant cannot be stated over a
key that may not exist; what it wrongly concluded is that nothing else
can be stated. The bounds above are stated over keys that DO exist in
case P5.c, so they cost that reasoning nothing. The lesson the plan
draws is worth carrying: a count drawn from a partition inherits every
constraint the partition has, and stating those constraints one at a
time as a reviewer finds them is slower than deriving them from the
partition once.

**What P5 through P7 do not reach.** They bound the census against
numbers the same document publishes; none of them can check that a
published width count is the count of source cells written at that
width. That measurement is a producer obligation, FW-P, and a loader
holding one document and never the table cannot recompute it. Two
documents can satisfy every condition above and disagree about what
the source held.

**The floor of one.** `fraction_widths` is on invariant S13's list at
the ENTRY and not at the field: where `small_cell_floor` is 1 its
`(withheld)` entry is absent or zero, while the named widths stay,
because at a floor of one every named width reaches the floor and
nothing is held back. S13 states the whole list, in the settings
section, and it is not restated here.

#### The invariants

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
values binary64 can hold clears the parse line of the present cells,
so the ladder is never built from nothing.

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
report. Where every parsed value is identical the exact mean is that
value and this format holds it, so a `null` there is refused.

**How a loader decides "every parsed value is identical", which Q5, Q6
and Q7 all turn on.** It reads `percentiles.min == percentiles.max`.
By L2 those two rungs are the smallest and the largest parsed value,
so they are equal exactly when the parsed values are all one value.
Where either endpoint is `null` under L3 the question cannot be asked
and the values are NOT treated as identical: the identical-value
clause of Q5, the whole of Q6, and Q7's identical-value clause do not
bite, while Q5's remaining clause applies as it does on any column
whose endpoints differ — with `n_used_in_statistics >= 3`, `skew` is a
number. The test is stated because it is the only route to those three
invariants from a parsed document, and two implementations that
reached it differently would refuse different documents.

**Invariant Q8 (`integer_valued` is a FACT, not a role).** The twin's
integer rule is routed by this published boolean and never by whether
the role name is `count`. A `continuous` column may publish
`integer_valued: true` — a column of whole numbers containing a
negative one is exactly that — and its twin cells are whole numbers.

**Invariant Q9 (`numeric_share`).**
`numeric_share` is `(n_numeric + n_out_of_range + n_contradictory) /
n_present`, computed as a share of the present cells, and is `0.0`
when `n_present` is 0 — which cannot occur on these roles by Q3.

**Invariant Q10 (`n_negative_unrepresentable` bound).**
`n_negative_unrepresentable <= n_out_of_range` and
`n_negative_unrepresentable <= n_negative`.

**Invariant Q11 (`n_zero` bound).** `n_zero <= n_numeric`.

**Every quantitative invariant of this section is read on
`affixed_number` over the CORES**, with `n_core_numeric` standing
wherever `n_numeric` appears. That substitution is AF7's, stated once
in the `affixed_number` section; the quantitative rules themselves are
the ones above and are not written twice.
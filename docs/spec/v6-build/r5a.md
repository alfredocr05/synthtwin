### 6.12 `affixed_number`

A column of numbers each wearing one shared piece of text — `$1,200`,
`45%`, `5 mg`, `170cm`. The number inside is described as a
distribution; the text around it is published as two exact spellings
and written back onto the twin's cells. It is rule 10 of the order in
section 5.2, so it claims only a column every earlier rule declined.

**Two populations run through this section and they are never the same
one:** the column's CELLS, and the CORES those cells hold. Every key
below says which of the two it answers for, and every invariant says
which of the two it is read over.

#### When a column takes this role

**C6-4 (what it is).** A cell is an AFFIXED NUMBER when its trimmed
text is `prefix + core + suffix`, where the core is a substring the
one number classifier of this format reads as a number this format can
hold — the same classifier every other role reads cells with, with the
acceptance of group separators, a leading plus and accounting
parentheses it has on every role — and at least one of prefix and
suffix is non-empty.

**Where more than one substring parses, the core is the LONGEST, and
of equal-length candidates the LEFTMOST.** That is a total order over
the candidates, so the split is a function of the cell and of nothing
else, and two producers reading one cell cannot disagree about where
its number begins. In `$1,200.00` the longest parsing substring is
`1,200.00`, so the prefix is `$` and the suffix empty; in `-12-34` two
candidates tie at three characters, `-12` and `-34`, and the leftmost
wins, so the prefix is empty and the suffix is `-34`.

**The classifier trims, so whitespace between the number and the text
around it belongs to the CORE and never to the pair.** The longest
parsing substring of `5 mg` is `5 `, not `5`, because the classifier
reads `5 ` as the number 5. So `5mg`, `5 mg` and `5  mg` all wear the
one pair — empty prefix, suffix `mg` — and differ only in their cores,
and the same holds on the prefix side, where `$1,200` and `$ 1,200`
both wear `$` and an empty suffix. This is a consequence of the two
rules above and it is written down because a reader will assume the
opposite: a column mixing spaced and unspaced units is a ONE-PAIR
column that takes this role, not a mixed-affix column that declines.

**C6-5 (the pair's identity).** The pair is the EXACT text of the
trimmed cell on either side of the core — no case folding, no inner
trimming. `mg` and `MG` are two pairs and not one, and so are `$` and
`EUR`.

**The test.** A column takes this role when no earlier rule has
claimed it and both of these hold:

1. at least the parse-line count of its present cells are affixed
   numbers wearing ONE affix pair — the count `minimum_parse_rate`
   fixes (section 4.4), applied as a COUNT and never as a compared
   share, so no rounding of a division decides a role; and
2. that pair's cell count is at least `small_cell_floor`.

**The floor is read at DETECTION time, deliberately:** the pair is
published, so publishing a floor-clearing spelling is constitutive of
the role, and a column that cannot publish one under the recorded
settings takes the next rule instead.

**A column whose cells wear more than one pair past the line's slack
does not take this role.** A column mixing `$` cells with `EUR` cells,
or `mg` with `MG`, declines to the later rules: a recorded decline,
not a partial publication, because publishing a distribution over some
cells while dropping the others is what the outcome principle forbids.
Its competing-readings remark says how far the affix reading got
(section 4.5, the form `remark_no_reading_fits`, argument 6).

**Stragglers are permitted up to the parse line.** A hundred-cell
column with ninety-nine affixed values and one plain number conforms.
No rule of this format, and no sentence a producer writes about such a
column, may say that EVERY value of it wears the pair; the remark
below names the count that actually did.

**Once the pair is fixed, wearing it is a question about the cell.** A
present cell WEARS the pair when its trimmed text begins with
`affix_prefix`, ends with `affix_suffix`, and is at least as long as
the two together; its CORE is the text between them, whatever that
text is. `n_affixed` counts the cells that wear the pair and the four
core-class counts classify their cores, so a milligram column holding
`5 mg`, `7 mg` and `many mg` has `n_affixed` 3 and `n_core_not_numeric`
1 — the third cell wears the pair and holds no number.

A cell's own split and the column's fixed pair are two different
questions. The line above is over cells that are affixed NUMBERS
wearing the pair; `n_core_numeric` counts cells wearing the pair whose
core is holdable, which can be the larger population. So the line is
not `n_core_numeric` restated, and a loader — holding one document and
never the table — can recount neither.

**AF-P (*producer*).** At least the parse-line count of the present
cells were affixed numbers wearing the published pair; the pair is the
one those cells wore; the core of each of them is that cell's
longest-then-leftmost parsing substring; and the four core-class
counts are the classifier's own verdicts over the cores of the cells
that wore the pair.

#### Stand-in numbers are judged over the CORES

The numeric stand-in pass runs where every role reads it: over whole
cells, before any role rule. The affix-based eligibility runs at a
stated later point: **only after rules 1 through 8 of section 5.2's
order — through `categorical` — have all declined the un-removed
column.** Where they decline, candidates are matched over the CORES by
the standing outlier-and-share rule, reusing
`sentinel_outlier_iqr_multiple` and `sentinel_minimum_share`; no
settings key of its own exists for this pass. The judged cells are
counted absent, the column is re-tallied exactly as a plain numeric
column is, and only THEN do rules 9 through 12 run over what remains.
A marker core inside an affixed column — `-999 mg` — is therefore read
as a hole and never averaged in.

**Removal can move a column across a line, and the landing is loud.** A
pair whose count is eaten below the floor, or below the parse line,
declines to the later rules by the same post-removal fall-through a
plain numeric column can take; the competing-readings remark of the
column it lands on states how many cells stand-in judging removed
whenever removal moved the column across a line (section 4.5, the form
`remark_no_reading_fits`, argument 7), and the sentinel verdicts stay
published under the landing role's publication class.

**This ordering is looser than the calendar-placeholder pass's (C6-34)
and that is not an oversight.** Removal here reaches only a column
every earlier rule has already declined, so no column an earlier rule
claims can be re-roled by it: a two-valued column whose cells share an
affix pair stays `binary`, and this pass never sees it.

**A declaration matches whole cells, here as everywhere.** A value
named with `--missing-value` or `--keep-value` is matched under
`declaration_matching` (section 4.4) against the whole trimmed cell,
never against a core, and nothing about declarations changes on this
role: a person protecting `-999 mg` names that spelling and not `-999`.
C6-117 binds this pass with the rest — a value named with `--keep-value`
is data, and no judged pass may read it as a hole.

#### C6-6. Added keys: twenty-two

Seven of this role's own, and the fifteen a `count` or `continuous`
block carries, the quantitative ones computed over the CORES.

| key | JSON type | range | meaning | disposition |
|---|---|---|---|---|
| `affix_prefix` | string | possibly empty | the exact text a counted CELL wears before its core | EXACT-OBSERVABLE |
| `affix_suffix` | string | possibly empty | the exact text a counted CELL wears after its core | EXACT-OBSERVABLE |
| `n_affixed` | integer ≥ 0 | `small_cell_floor` .. `n_present` | CELLS wearing the pair | EXACT-OBSERVABLE |
| `n_core_numeric` | integer ≥ 1 | ≤ `n_affixed` | CORES reading as a number this format can hold | EXACT-OBSERVABLE |
| `n_core_out_of_range` | integer ≥ 0 | ≤ `n_affixed` | CORES that are well-formed numbers too large or too small for binary64 | EXACT-OBSERVABLE |
| `n_core_contradictory` | integer ≥ 0 | ≤ `n_affixed` | CORES written in numeric notation whose meaning conflicts with itself | EXACT-OBSERVABLE |
| `n_core_not_numeric` | integer ≥ 0 | ≤ `n_affixed` | CORES that are not numeric notation at all | EXACT-OBSERVABLE |
| `percentiles` | ladder of numbers | section 5.6 | the eleven-rung ladder over the parsed CORES | ends EXACT-OBSERVABLE, nine interior rungs APPROXIMATED, as on `count` |
| `mean` | number or `null` | — | arithmetic mean of the parsed CORES | APPROXIMATED, as on `count` |
| `std` | number or `null` | ≥ 0 when a number | sample standard deviation of the parsed CORES, divided by n−1 | APPROXIMATED, as on `count` |
| `skew` | number or `null` | — | moment-based skewness of the parsed CORES | APPROXIMATED, as on `count` |
| `std_unrepresentable` | boolean | — | true when the CORES' exact spread exceeds binary64 | EXACT-OBSERVABLE |
| `n_zero` | integer ≥ 0 | — | parsed CORES equal to zero | EXACT-OBSERVABLE |
| `n_negative` | integer ≥ 0 | — | CORES whose notation settles a negative sign, including ones no statistic could use | EXACT-OBSERVABLE |
| `n_negative_unrepresentable` | integer ≥ 0 | — | out-of-range CORES whose notation settles a negative sign | EXACT-OBSERVABLE |
| `n_used_in_statistics` | integer ≥ 0 | — | present CELLS that contributed a core to the statistics | EXACT-OBSERVABLE |
| `n_left_out_of_statistics` | integer ≥ 0 | — | present CELLS that did not, cells wearing no pair included | EXACT-OBSERVABLE |
| `numeric_share` | number | 0.0 ≤ x ≤ 1.0 | share of present CELLS whose writer meant a number, read over the cores | EXACT-OBSERVABLE |
| `integer_valued` | boolean | — | true when every numeric-looking CORE is whole | EXACT-OBSERVABLE, routed by the FACT and not by role |
| `n_rows` | integer ≥ 0 | `== n_rows` at the top level | the table's row count, echoed | LOADER-ONLY |
| `numeric_styles` | object | section 7.5 | CORES per spelling style, under the floor | EXACT-OBSERVABLE, recount identity of section 7.5.7 |
| `fraction_widths` | object | C6-27 to C6-30 | `decimal`-styled CORES per fraction width, under the floor | EXACT-OBSERVABLE |

**The block is forty-four keys**: the twenty-two universal keys of
section 5.1 and the twenty-two above — a `count` block's fifteen
additions plus this role's own seven. The matrix of section 6.11 marks
exactly those twenty-two cells in its `afx` column. There is no
unparsed count on this role: cells wearing no pair are
`n_present - n_affixed`, and a key restating a subtraction is a key
two implementations can disagree about.

#### C6-7. The two populations, kept apart

The four universal counts `n_numeric`, `n_out_of_range`,
`n_contradictory` and `n_not_numeric` keep the meaning section 5.1
gives them and answer for the CELLS. On a column of `u:1`, `u:2`, … no
complete cell reads as a number, so `n_numeric` is zero and
`n_not_numeric` is the present count. That is the truth about the cells
and this document does not bend it. The quantitative block above
describes the CORES, and four keys of its own name that population —
`n_core_numeric`, `n_core_out_of_range`, `n_core_contradictory`,
`n_core_not_numeric` — each classified by the one number classifier
over the core substring alone.

**The core census has four counts because the classifier's verdict on
any text is exactly one of four**: a number this format can hold, a
well-formed number too large or too small to hold, numeric notation
that conflicts with itself, and no number at all. That is why AF4
below is exhaustive and why a fifth core count would describe nothing.

X2 closes over the cells here as on every role; AF4 is the core
census's own closure, and it closes on `n_affixed` rather than
`n_present`, because a present cell that wore no pair has no core to
classify.

#### C6-8. The invariants

**AF1.** `affix_prefix` and `affix_suffix` are not both empty.

**AF2.** `small_cell_floor <= n_affixed <= n_present`.

**AF3.** `n_affixed` is at least the parse-line count of `n_present` —
the count `minimum_parse_rate` fixes, applied as a count and never as a
compared share — so a block whose pair never cleared the detection line
cannot conform.

**AF4.** `n_core_numeric + n_core_out_of_range + n_core_contradictory +
n_core_not_numeric == n_affixed`.

**AF5.** `n_core_numeric >= 1`. The ladder is never built from nothing.

**AF6.** `integer_valued` is a fact about the CORES and is what a
consumer routes on, never the role name. A column of whole cores
publishes `integer_valued: true` and its twin cores are whole numbers.

**AF7.** Every quantitative key above obeys the invariant section 6.7
states for it on `count` and `continuous`, read over the CORES.
Wherever such an invariant names a cell-census count it is read here
over the matching core-class count — `n_core_numeric` for `n_numeric`,
`n_core_out_of_range` for `n_out_of_range`, `n_core_contradictory` for
`n_contradictory` — and over no other count. `n_present` and `n_rows`
are read unchanged: they answer for the column's cells on every role.
The six readings that produces are written out, so nothing is left to
inference:

| invariant | as read on this role |
|---|---|
| invariant Q2 (statistics population) | `n_used_in_statistics == n_core_numeric`, `n_left_out_of_statistics == n_present - n_core_numeric` |
| invariant Q3 (numbers exist) | `n_core_numeric >= 1`, which is AF5 |
| invariant Q9 (`numeric_share`) | `(n_core_numeric + n_core_out_of_range + n_core_contradictory) / n_present` |
| invariant Q10 (`n_negative_unrepresentable`) | `<= n_core_out_of_range` and `<= n_negative` |
| invariant Q11 (`n_zero`) | `n_zero <= n_core_numeric` |
| invariant P1 (the style population) | the values of `numeric_styles` sum to `n_core_numeric` |

**The substitution reaches all three numeric-looking counts and not
`n_numeric` alone, because Q9 and Q10 name the other two and Q10
refuses a conforming column otherwise.** A hundred-cell milligram
column of ninety `5 mg`-shaped cells and ten `-1e999 mg` cells
publishes `n_out_of_range: 0` — no complete cell of it reads as a
number, well-formed or otherwise — beside `n_core_out_of_range: 10`
and `n_negative_unrepresentable: 10`. Read over the cell census, Q10's
`n_negative_unrepresentable <= n_out_of_range` is `10 <= 0` and the
document is refused; and Q9 computes `(90 + 0 + 0) / 100`, publishing
`numeric_share: 0.90` for a column every one of whose present cells
carries a numeric-looking core. Q4 through Q8 name no census count and
are read exactly as section 6.7 states them; L1, L2 and L3 bind
`percentiles` here as on `count`.

**The echo, invariant Q1, read on this role.** The per-column `n_rows` equals the
document's `n_rows`. It appears only inside `count`, `continuous` and
`affixed_number` blocks, is FORBIDDEN on every other role, and is
LOADER-ONLY: the document-level `n_rows` carries the row-count
obligation.

**`numeric_styles` is REQUIRED here**, on section 7.5's terms, its
census being a census of the CORES. It reaches this role for the reason
it reached the two numeric ones: an `affixed_number` twin cell is
written as a parsed number from the ladder placed inside its affix
pair, so the reader's inferred type is at stake and a style map is
something the generator can discharge. `fraction_widths` sits beside it
as a sibling key of the block under C6-27 through C6-30 — never inside
`numeric_styles`, which P1 forbids — its cases P5.a to P5.c, P6 and P7
read over the same core population, P2 and P4 bind as section 7.5
states them, and P3 holds because AF5 gives it `n_core_numeric >= 1`.

#### C6-9. Publication class

`affixed_number` is a RANGES-class role. The ranges class's "no
spelling appears" sentence gains ONE named exception, confined by the
matrix of section 6.11 to exactly two keys: `affix_prefix` and
`affix_suffix` carry shared affix text, governed by the floor through
C6-4's detection rule, so a published pair is always a floor-cleared
fact. **No other key of any ranges-class role may carry a spelling**;
the labels class is untouched, and the nothing class's "no value, no
spelling, no fragment of one" sentence is untouched. It is an exception
and not a fourth class: a fourth class would need a meaning everywhere
the three are enforced, where an exception is confined by one matrix.

The ladder's two ends are exact values of real cores, published
floor-free under the endpoint policy every ranges-class role carries.
Both the pair and the core distribution are disclosure no earlier rule
of section 5.2's order would have produced for this column, and the
disclosure section prices them.

The class governs the column's VALUES. It does not reach
`missing_by_class`, whose keys are this format's own words, and it does
not silence `missing_by_source`: this is not a nothing-publishing role,
so an undeclared `affixed_number` column names its absent spellings
under the floor exactly as `datetime` does. A column declared with
`--identifier` cannot reach this role at all — the declaration is
decided at rule 2 — so the structural override never meets it.

**Forbidden keys.** Every key not listed above is FORBIDDEN here and a
loader refuses it, naming the key and the column. The four a reader
will ask about: `levels` and its three companions, which belong to the
labels class and to no ranges-class role; `level_ceiling`, which is
`categorical`'s alone; `n_unparsed`, `clock_form` and every other
datetime or clock key; and the whole-number, sign and length keys of
`numeric_unrepresentable` — `n_whole`, `n_fraction`, `n_whole_unknown`,
`n_positive`, `n_sign_unknown`, `min_length`, `max_length`.
`n_negative` is the one name shared with that role: one key with one
meaning, asked of two populations — the present cells there, the cores
here.

#### The remark this role carries

**Every `affixed_number` column carries the affixed-column remark,
WITHOUT CONDITION** — the form `remark_affixed_numbers_may_be_codes`
of section 4.5, arity 3. Argument 1 is the block's `affix_prefix`,
argument 2 its `affix_suffix`, argument 3 its `n_affixed`. The two
affix arguments are bound POSITIONALLY and character-for-character to
the block named by the note's own `column` field, so a pair cannot be
rendered swapped; argument 3 equals that block's own `n_affixed`.
Section 4.5 fixes the rendering, and it names the count of cells that
ACTUALLY wore the pair rather than claiming every value did: the role
admits stragglers up to the parse line, so the universal claim was
false on a conforming column, and a remark whose whole job is to let
somebody recognize their own column must not misdescribe it.

**It is unconditional because no test of the values can separate an
opaque token family from a measurement.** A prefixed code column
(`A-101`, `A-102`, …) that published nothing before now reads as
quantities with a published distribution over its numeric parts, and
repeating decimal-cored tokens defeat every conditional remark anyone
drafts — which is how three identifier inferences were defeated before
withdrawal. The choice is between telling every such column's owner and
telling none, and the remark names `--identifier` as the route if these
are codes rather than measurements. What the misroute cannot do is take
a column away from a rule that handles it already: `V1`, `V2`, `V3`
visit labels stay `categorical`, because `categorical` runs first.

The code-shaped all-different remark reaches this role on its own
trigger, in the wording section 4.5 fixes and no other; and the block
carries the universal `detection_evidence` sentence and any other
remark whose trigger it meets, each built from the closed grammar of
section 4.5 under the publication guard.

#### What the twin writes

A twin cell is `affix_prefix + core + affix_suffix`: cores from the
existing numeric machinery over the published core facts, affixes byte
for byte. Cells that wore no pair are reproduced by class through the
straggler constructions, including the plain-number construction the
generation method defines for this role — a spelling that reads back as
a number, reads as no date form, and collides with no published hole
spelling of its column (C6-118). Describing the twin again re-detects
the role, the same pair and the same core distribution.
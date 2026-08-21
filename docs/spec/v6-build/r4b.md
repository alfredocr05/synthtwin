### 6.8 `identifier`

The one role no rule reads out of a column's values, and one of the
three that publish no value of the table anywhere in their block.

**C6-80 (the route, and it is the only one).** A column takes `role:
identifier` exactly when the person who owns the table named that
column with `--identifier` on the profiling run and the column has at
least one present cell. It is rule 2 of the order in section 5.2,
tested immediately after the empty rule, so a DECLARED column with no
present cells takes `role: empty` with `structural_role: identifier`
instead (invariant E1): the empty rule settles first and the
declaration wins immediately after. Which columns were declared is on
the document's own face — `settings.forced_identifiers` (section 4.4)
carries the declared names, sorted. No count, no shape and no measure
of the values sends a column here.

**C6-81 (the uniqueness thresholds decide NO role).** The settings
`identifier_uniqueness` and `identifier_minimum_rows` (section 4.4)
govern one thing: whether the run SAYS that a column's values never
repeat, and points at `--identifier` for a person who knows what the
column holds. A producer emits that remark when both of these hold —

- `n_present >= identifier_minimum_rows`, and
- `n_distinct` is at least the smallest whole number reaching
  `identifier_uniqueness` × `n_present`: the whole part of the exact
  product, plus one where that whole part falls below the product,
  applied as a COUNT and never as a compared share, so that no
  rounding of a division decides what is said

— and says nothing about repetition at all below
`identifier_minimum_rows`, because in a short column almost every
measurement is all-different. The remark rides whatever role the
column ACTUALLY reached: one form on the roles described as numbers —
`count`, `continuous` and `affixed_number` — and one on `free_text`.
It never rides this role, which no column reaches by uniqueness.
Section 4.5 fixes the two wordings and which role carries which; this
clause fixes when they fire. Both point two ways on purpose — naming
`--identifier` alone told the owner of a column of prices,
percentages or clock times to mark a MEASUREMENT as a record number,
which withholds its values permanently and silently.

**Why the route is a declaration and not a test.** Three value-based
identifier inferences arrived here across three revisions and every
one was withdrawn, each defeated by a column of measurements that also
never repeated (review item P1-R6-F8). The trade was never worth
taking: when the guess was right it published no more than free text
publishes, and when it was wrong it destroyed a distribution the twin
exists to reproduce.

**Added keys** — six, beyond the universal keys of section 5.1:

| key | JSON type | range | meaning |
|---|---|---|---|
| `min_length` | integer ≥ 1 | ≤ `max_length` | the shortest present value's length in characters |
| `max_length` | integer ≥ 1 | ≥ `min_length` | the longest present value's length in characters |
| `all_whole_numbers` | boolean | — | true when every present cell is a whole number and there is at least one |
| `n_all_digits` | integer ≥ 0 | ≤ `n_present` | present cells that are ASCII digits and nothing else, after trimming |
| `n_code_alphabet` | integer ≥ 0 | ≤ `n_present` | present cells drawn from the code alphabet, after trimming |
| `n_distinct_by_occurrences` | multiplicity map | section 5.3 | how many different RAW present values covered one row, two rows, … |

None of the six is this role's alone except `all_whole_numbers`. A
`numeric_unrepresentable` block carries `min_length` and `max_length`
over a DIFFERENT population, under the rule stated at that role;
`n_all_digits` and `n_code_alphabet` stand on this role and on
`free_text` and nowhere else; `n_distinct_by_occurrences` stands on
those two and on `numeric_unrepresentable`. Section 6.11's matrix is
where a reader checks that.

**How lengths and the two shape counts are measured**, stated once
here and read by `free_text` as well. A length is counted on the RAW
present value, untrimmed, in characters. `n_all_digits` and
`n_code_alphabet` are decided on each present cell's TRIMMED text.
**The code alphabet is ASCII letters, ASCII digits, the hyphen and the
underscore, and nothing else.** A cell holding any other character — a
currency sign, a decimal point, a percent sign, a colon, or any
character outside ASCII — is not in it, and neither is the empty
string.

**Invariant I1.** `role == "identifier"` implies `structural_role ==
"identifier"` (A2) and `n_present >= 1`.

**Invariant I2.** M1 and M2 bind `n_distinct_by_occurrences`: its
values sum to `n_distinct`, and its keys read as numbers and weighted
by its values sum to `n_present`.

**Invariant I3 (this block publishes nothing of the table).**
`missing_by_source` is empty, `n_missing_blank` and
`n_missing_withheld` are both `0`, and every `sentinel_verdicts` entry
has `candidate == "(withheld)"` (N3, V2). It is a property of the
whole BLOCK: no value of the column, no spelling of one and no
fragment of one stands anywhere in it. What is published is the role,
the counts, the shortest and longest length, whether every value is a
whole number, how many cells are all digits or all code alphabet, and
the shape of repetition — lengths and counts, never values.

**Invariant I4.** `min_length >= 1`. A present cell of length zero is
a blank, and a blank is absent.

**The infeasible corner, and what it costs.** Where a declared
identifier's published length range cannot supply as many distinct
values as the column has rows, **length wins and invented identifiers
may repeat** (owner decision 6). The cost is stated, not softened: the
twin's identifier column then holds duplicate values where the real
column had none, so a join or a de-duplication developed against the
twin can fan out or collapse differently than on the real table. The
report names the column, the number of duplicates and that
consequence, every run. What the decision buys is that the twin's
identifiers keep the exact width the real ones had, so
width-dependent validation and fixed-width parsing developed on the
twin still hold.

**In that corner, THREE distinctness facts become REPORT-ONLY, not
one** (plan P2-D6, item P2-R4-F4): raw `n_distinct`,
`n_distinct_folded`, AND `n_distinct_by_occurrences`. Worked on the
real 200-row single-character case: a twin holding length 1 can offer
at most 95 distinct characters and 69 distinct folded identities
against 200 and 122 published, and 200 values drawn from at most 95
cannot all be singletons — so the multiplicity map is necessarily
violated too. That last one deserves naming, because the multiplicity
map exists precisely so that a generator never invents a repetition
pattern, and in this corner it must. What the column then preserves is
`n_present`, `n_missing`, the length range, `all_whole_numbers`,
`n_all_digits` and `n_code_alphabet` — and nothing about distinctness
or repetition. The report names all three lost facts with the achieved
value beside the published one. **Outside that corner every one of
them is EXACT-OBSERVABLE.**

**Scope of the corner, stated precisely.** Owner decision 6 governs
ONLY the case where the published facts are jointly infeasible. The
general all-different obligation — that a column publishing
`n_distinct == n_present` generates all-different values, on every
role — is not touched by that decision and still binds wherever it is
feasible, which is the ordinary case and includes every undeclared key
column arriving as free text or as a numeric role.

### 6.9 `free_text`

A column no rule claimed. It is rule 12 of the order in section 5.2 —
the fallback, tested after every other rule — and none of its values
is published.

**C6-82 (fewer columns reach here, and the surfaces say so).** Three
rules of this version claim columns that reached `free_text` before
them: `time_of_day`, `affixed_number` and `long_tail_labels`, all
three tested after the categorical rule and before this fallback. A
column of clock times, a column of numbers wearing one affix pair, and
a column past the categorical ceiling holding at least one level big
enough to name each now take a role that publishes something about its
values. **A column that still reaches `free_text` publishes nothing,
so its twin is invention.** That the set is smaller is a REPORTING
obligation on the surfaces and not a fidelity claim: nothing about
what this role publishes is relaxed by it.

**What a column reaching here has been ruled out of.** Every reading
was ruled OUT and none was established — including the column that is
only PART numbers, where a mean over the part that reads would leave
the rest out of the distribution while the profile looked complete.
The run's remarks name each reading that was tried and how far it got,
so a person can see the arithmetic and not only the verdict.

**Added keys** — five, beyond the universal keys of section 5.1:

| key | JSON type | shape | meaning |
|---|---|---|---|
| `length` | object | exactly `min`, `max`, `mean`, `p50` | statistics of the present values' lengths in characters |
| `words` | object | exactly `min`, `max`, `mean` | statistics of the present values' word counts |
| `n_all_digits` | integer ≥ 0 | ≤ `n_present` | present cells that are ASCII digits and nothing else, after trimming |
| `n_code_alphabet` | integer ≥ 0 | ≤ `n_present` | present cells drawn from the code alphabet, after trimming |
| `n_distinct_by_occurrences` | multiplicity map | section 5.3 | how many different RAW present values covered one row, two rows, … |

`length.min` and `length.max` are integers ≥ 1; `length.mean` is a
number or `null`; `length.p50` is a number or `null`. `words.min` and
`words.max` are integers ≥ 0; `words.mean` is a number or `null`. A
null in any of the three means the exact statistic is not a finite
binary64 value, which no producible profile is known to reach. **A
word is a run of characters separated by whitespace**, counted on the
present value; lengths and the two shape counts are measured exactly
as section 6.8 states, and the code alphabet is the one defined there.

**Invariant F1.** `length.min <= length.p50 <= length.max` when `p50`
is a number, and `length.min <= length.mean <= length.max` when `mean`
is a number. Likewise `words.min <= words.mean <= words.max`.

**Invariant F2.** M1 and M2 bind `n_distinct_by_occurrences`, exactly
as I2 states them.

**Invariant F3 (this block publishes nothing of the table).**
`missing_by_source` is empty, `n_missing_blank` and
`n_missing_withheld` are both `0`, and every `sentinel_verdicts` entry
has `candidate == "(withheld)"` (N3, V2). As at I3 this binds the
whole BLOCK, not any one field: no value, no spelling of one and no
fragment of one stands anywhere in it.

**Invariant F4.** `length.min >= 1` and `words.min >= 0`. A present
cell has at least one character; a cell of punctuation alone may hold
no words.

**The binding generation rule.** The generator INVENTS language:
neutral synthetic words honoring the published length and word
statistics, the digit and code-alphabet counts, and the multiplicity
map including fold collisions. **It never samples, quotes, templates
from, or paraphrases source text.** Any future change that carries
source language into the profile or the twin is a charter change
requiring an owner decision and a privacy review.

What else the multiplicity map carries — its key form and
serialization (section 5.3), its floor-free publication class and its
disposition — is stated once at section 7.2 and is not restated here.
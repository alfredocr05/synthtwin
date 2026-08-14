# Generation method v1 — the exact transform from (profile, seed) to twin bytes

**Status:** revision 1, written before any Phase 2 code exists, under the
owner sequencing override recorded in `docs/plans/phase-2-generator.md`
(revision 5). **Not ratified.** This is artifact 3 of that plan's four,
and it carries out decisions the plan makes; it introduces no mechanism
the plan left open, except the one the plan explicitly delegated here —
the invention domain and its capacity rule, with a named refusal
(P2-R5-F4), which section G9 fixes.

**Who this is for.** Two readers, and the document fails if either is
left guessing. The first is the implementer of `synthtwin generate`. The
second is an INDEPENDENT implementer, working from this text alone, in
another language, who must produce the same twin bytes from the same
profile and the same seed. Every place where two conforming programs
could differ is therefore closed here by a stated rule, including the
ones that look too small to matter: the order of a loop, the direction
of a rounding, which end of a list a tie goes to.

**What it does not cover.** The profile's wire shape, key by key, is
`docs/spec/profile-contract-v4.md`; this document names published fields
and assumes that contract's meanings. The command line, the output file
names, the write transaction, the refusal catalogue's wording and the
generation report's own bytes are P2-D10's business. Fidelity
measurement and the quality report are `synthtwin validate`'s, and the
rules it measures against are `docs/spec/validation-method-v1.md`.

**This amends the sentence that called fidelity measurement later work**
(Phase 3 plan P3-D7 stage 2, amendment A-P3-8, 2026-08-14). The
validator ships, so a reader of this document — including the
independent implementer it is written for — is now told where the
measuring rules live rather than which phase would eventually write
them. Nothing this document obliges a generator to do moves: the
validator measures a written file against the PROFILE, and it is a
consumer of this method's output rather than a rule upon it.

**Vocabulary.** "Word" always means one full-width unsigned 64-bit draw
from the single stream of section G3. "Cell" means one value in one row
of one column of the written twin. "Published" means present in the
profile document; a fact that is not published is not available to any
rule here, and a rule that would need one is a defect in this document.

---

## G1. The boundary this method upholds

The transform below reads the profile document and the seed. It reads
nothing else. It has no access to the real table, no access to the file
the profile was made from, and no access to anything the profile does
not carry. That is not an aspiration of the implementation: it is a
property of this method, and it can be checked against this text —
**every input to every rule below is either a published profile field, a
word from the single stream, or a constant fixed in this document.**

Two consequences worth stating, because they are the ones an
implementer is tempted to breach:

- **No rule may read a twin cell it has already written back out of the
  written file** to decide the next one. Every decision is made from the
  in-memory construction described here, so the method never depends on
  the file system or on a reader.
- **No rule may consult the profiler's code.** Where this document has
  to agree with the profiler — the fold, the number parser, the date
  parser, the ladder positions — it states the rule in full and names
  the shipped function that must agree with it, so the agreement is
  testable in both directions rather than assumed.

## G2. The output bytes

The twin is one CSV file. The exact byte-level rules, because "CSV" is
not one format:

| property | value |
|---|---|
| encoding | UTF-8, no byte-order mark |
| line ending | LF (`\n`), on every line, including the last |
| field separator | comma (U+002C) |
| quote character | `"` (U+0022) |
| doubling | an embedded `"` is written twice inside a quoted field |
| escape character | none |
| quoting | minimal: a field is quoted when and only when it contains a comma, a quote character, a carriage return or a line feed — **plus the two canonical exceptions below** |
| header row | written when `source.header_source` is `file`; not written when it is `generated` |
| column order | the `columns` list order of the profile, which the contract fixes as the schema order (P2-D6, STRUCTURAL) |
| row count | exactly the document-level `n_rows` data rows, not counting the header row when one is written |

**Canonical quoting exception 1 — a leading U+FEFF in a column name.**
A first column name beginning U+FEFF is always quoted (P2-D10). Written
unquoted it would begin the file with the byte-order-mark sequence,
which the reader then consumes, silently renaming the column.

**Canonical quoting exception 2 — a row that would otherwise be
empty.** When the table has exactly one column and that row's single
cell is absent, the cell is written as `""` — two quote characters —
rather than as nothing. Written as nothing, the line is empty, and the
shipped reader refuses a one-column file with an empty line (it cannot
tell a record whose only value is missing from a blank line left in the
file) while the second reader would drop it. The `""` spelling is the
one the reader's own refusal message teaches, it reads back as an empty
cell, and an empty cell is what an absent value is. This exception
cannot arise with two or more columns, because a row of absent cells is
then written as one or more commas, which is not an empty line.

**Every other cell is written as its exact text.** No trimming, no
padding, no normalization, no locale, no alteration of a published
label — including a label a spreadsheet would treat as a formula
(P2-D10 and R-P2-6: counted and warned, never altered).

## G3. The single stream: one generator, one draw shape, integer primitives

### G3.1 The generator

Exactly one random generator exists in a run:

```
generator = numpy.random.default_rng(seed)
```

`seed` is a Python integer in `0 .. 2**64 - 1`, parsed from the command
line under the grammar P2-D8 fixes (one or more ASCII decimal digits and
nothing else; leading zeros accepted; no sign, no underscores, no
whitespace, no non-ASCII digits). `default_rng` is the only name this
method uses from numpy (scanner policy E7). There is no `spawn`, no
second generator, no module-level generator, and no other source of
randomness anywhere in the run — not a hash seed, not a clock, not a set
iteration order.

### G3.2 The one draw shape

Every random quantity in this method comes from **full-width unsigned
64-bit words**, drawn in exactly this form and no other:

```
generator.integers(0, 18446744073709551615, size=count, dtype="uint64",
                   endpoint=True)
```

- `low` is the literal `0`; `high` is the literal `18446744073709551615`
  (that is `2**64 - 1`); `endpoint` is the literal `True`. So the drawn
  range is the whole of `0 .. 2**64 - 1`, inclusive at both ends.
- `size` is a first-party Python integer computed by the rules of this
  document. It is never derived from anything the caller supplies.
- `dtype` is the **string** `"uint64"`, never `numpy.uint64`: E7 permits
  no numpy attribute but `default_rng`, so the type is named by text.
- Each element is converted to a first-party Python integer by `int(...)`
  before any other use. That conversion is the point where the library
  scalar's origin ends (E8); nothing else is ever done to an element, an
  array or a scalar.

**Why this shape and no other.** The plan measured (numpy 1.24.0 and
2.5.1, seed 12345) that power-of-two, non-power-of-two and full-width
uint64 draws agree exactly today, so nothing diverges now; fixing one
shape narrows what the twin's bytes can ever depend on to a single
library operation. The claim that this makes the vectors independent of
numpy is NOT made here and was withdrawn in the plan (P2-R3-F2):
`integers` is itself the retained random operation. What first-party
post-processing removes is the additional surfaces, nothing more.

### G3.3 Calls, blocks and the word sequence

The **word sequence** of a run is the concatenation, in order, of every
word the run draws. Section G4 fixes that order exactly.

The implementation makes **one `integers` call per stage** (the stages
are named in G4) with `size` equal to that stage's exact word count, and
makes no call at all for a stage whose count is zero. That is stated as
a rule rather than left free, so no implementation detail can move a
byte.

It is nevertheless a property of this draw shape that the word sequence
does not depend on how the calls are cut: drawing `n` words in one call,
in `n` calls of one, or as `n` scalar draws yields the same words, because
the full-width range needs no rejection and no buffering. Verified on
numpy 2.5.1; the conformance battery re-checks it on every supported
numpy version, so a library change that broke it would turn a test red
rather than move a twin.

For orientation only — no reference vector depends on it — the first
four words for `--seed 0` are:

```
11749869230777074271
4976686463289251617
755828109848996024
304881062738325533
```

### G3.4 The three derived primitives, in first-party integer code

Nothing below ever forms a binary64 uniform. Every use of a word is
exact integer arithmetic on Python integers, so no rounding mode, no
extended precision and no platform difference can reach it.

**(a) The unit value.** `unit(w)` is the exact rational `w / 2**64`,
in `[0, 1)`. It is never materialized as a float: it always appears as
the pair (numerator `w`, denominator `2**64`) inside a larger exact
integer expression. Section G5.4 and G7.3 are the only users.

**(b) A bounded range.** For an integer `m >= 1`:

```
bounded(w, m) = (w * m) >> 64
```

which is the integer part of `unit(w) * m`, a value in `0 .. m - 1`.

This is the multiply-high rule, and it is chosen over a rejection loop
for one reason that matters more than its bias: **it consumes exactly
one word for every call, so the word count of a run is a fixed function
of the published facts and can be stated in advance.** A rejection loop
would make the count depend on the words themselves, and every draw
budget in this document would become unstatable.

Its cost is stated rather than hidden: the outcomes are not exactly
uniform. Of the `2**64` words, each outcome receives either
`floor(2**64 / m)` or `ceil(2**64 / m)` of them, so the largest
deviation from `1/m` is below `m / 2**64`. For every `m` this method
uses — `m` is at most a table's row count — that is below `2**-32` for
tables under four thousand million rows, which is far below any
distributional effect the twin is measured for. It is not a
cryptographic construction and is not offered as one.

**(c) An arrangement.** `permutation(n)` consumes exactly `max(n - 1, 0)`
words and produces an arrangement `a` of `0 .. n - 1`:

```
a = [0, 1, ..., n - 1]
for i = n - 1 down to 1:
    w = the next word
    j = bounded(w, i + 1)
    swap a[i] and a[j]
```

The loop runs downward, the drawn index is inclusive of `i` itself, and
the swap happens even when `j == i`. All three are stated because all
three change the bytes.

## G4. Order and count of draws

### G4.1 Column order

Columns are generated in the profile's `columns` **list order**. The
contract fixes that this is the schema order, the twin's output column
order, and the order in which the single stream is consumed (P2-D6,
P2-R5-F6). No column is generated before an earlier one, no column is
generated lazily, and no column's words are drawn out of turn. Nothing
is drawn before the first column: the first word of the run is the first
word the first column's first stage asks for.

### G4.2 Stages within a column

Every column is generated in exactly two stages, in this order:

1. **Content.** Build `content`, a list of exactly `n_present` cell
   texts, by the role's own rule (G5–G10). The order of `content` is
   fixed by that rule; it is not the output order.
2. **Placement.** Extend `content` with `n_missing` copies of the empty
   text, giving a list of exactly `n_rows` entries, then draw
   `a = permutation(n_rows)` and write

   ```
   written[t] = content[a[t]]      for t = 0 .. n_rows - 1
   ```

The absent cells are therefore placed by the same arrangement that
places everything else, which is what makes their positions
seeded-random (P2-D9) without a second mechanism and without a second
draw budget.

### G4.3 The draw budget, as a function of published content

| role | content words | placement words |
|---|---|---|
| `empty` | 0 | `max(n_rows - 1, 0)` |
| `constant`, `binary`, `categorical` | 0 | `max(n_rows - 1, 0)` |
| `count`, `continuous` | `S - pinned - zeroed` (G5.3) | `max(n_rows - 1, 0)` |
| `datetime` | `max(P - 2, 0)` where `P = n_present - n_unparsed` (G7) | `max(n_rows - 1, 0)` |
| `identifier` | 0 | `max(n_rows - 1, 0)` |
| `free_text` | 0 | `max(n_rows - 1, 0)` |
| `numeric_unrepresentable` | 0 | `max(n_rows - 1, 0)` |

Where, for the numeric roles, `S` is the number of value strata
(G5.2), `pinned` is the number of strata pinned to an endpoint (2 when
`S >= 2`, 1 when `S == 1`, 0 when `S == 0`), and `zeroed` is 1 when a
zero stratum exists and is not itself one of the pinned strata, else 0.

**Everything else is placed by fixed rule and costs no word** (P2-D8):
the endpoints of a numeric or datetime column, the zeros, the class
stand-ins, every invented identifier, every invented text, every label
and every label variant. Where this document says a value is pinned,
that means no word is drawn for it — never that a word is drawn and
discarded.

**The consequence D12 already carries** is restated here so nobody is
surprised by it: a schema change, or any change to this method that
alters a column's word count, shifts every later column at the same
seed. Regeneration after a method change is a changelogged event.

## G5. Numeric columns (`count`, `continuous`)

### G5.1 What the profile supplies, and what each fact obliges

Published: the 11-rung `percentiles` ladder; `n_zero`; `n_negative`;
`n_negative_unrepresentable`; `integer_valued`; `n_used_in_statistics`;
`n_left_out_of_statistics`; `numeric_share`; `mean`, `std`, `skew`,
`std_unrepresentable`; the universal class counts `n_numeric`,
`n_out_of_range`, `n_contradictory`, `n_not_numeric`; `n_distinct` and
`n_distinct_folded`; and (owner decision 10) `numeric_styles` with its
withheld remainder.

Fixed quantities used throughout:

```
K = n_numeric                     cells that parse as ordinary numbers
O = n_out_of_range                cells that are numbers out of range
C = n_contradictory               cells with self-contradicting notation
N = n_not_numeric                 cells that are ordinary text
K + O + C + N = n_present         (contract invariant)

G = n_negative - n_negative_unrepresentable    negatives among the K
Z = n_zero                                     zeros among the K
P = K - G - Z                                  positives among the K
```

`P < 0` is a jointly infeasible document and is a generation refusal
(G12). The ladder rungs are named `L[0] .. L[10]` for
`min, p01, p05, p10, p25, p50, p75, p90, p95, p99, max`, with
probabilities in hundredths

```
PCT = (0, 1, 5, 10, 25, 50, 75, 90, 95, 99, 100)
```

held as integers, never as decimal fractions, for the same reason the
profiler holds them that way: `0.99` has no exact binary spelling and
the nearest one moves a rung onto the wrong pair of neighbours in a
large column. The contract requires the ladder to be non-decreasing, so
a descending pair is a loader refusal and not something this method
repairs.

**A null rung is NOT a refusal, and this is the rule for one**
(P2-C1-F8). Revision 1 of this document said the contract required every
rung to be a finite number and that a null rung was a loader refusal.
The contract says the opposite in its rule L3 — a rung may be null, it
carries no obligation of its own, and a loader accepts it rather than
refusing a document over a case it cannot rule out — and the shipped
loader accepts one. A method that expects a refusal that never comes
leaves the generator to decide the rule for itself, which is what
happened. The rule is fixed here:

- **The filled ladder.** Before anything in G5.2 or G5.3 reads a rung,
  every null rung takes the value of the NEAREST rung BELOW it that
  holds a number; where no rung below it holds one, it takes the FIRST
  rung of the ladder that holds a number. The filled ladder is what
  every later rule reads, and it is still non-decreasing, because each
  filled rung repeats a number already standing at or before its own
  place.
- **A ladder that holds no number anywhere** has no filled form. The
  column's values are then placed on the sign counts alone (G5.5), no
  ladder-derived bound is measured for it, and the empty ladder is named
  in the report on every run (G12.3).
- **A filled rung owes nothing.** `min` and `max` are EXACT-OBSERVABLE
  only where they hold a number; where either was null the report names
  it as a published fact the description did not carry, rather than as
  an endpoint the twin missed.

No producible profile is known to reach any of this — every interpolated
rung lies between two finite neighbours — but "not known to be
reachable" is not a rule, and the loader accepts the document, so the
method states what happens rather than leaving two implementations to
answer differently.

### G5.2 Strata: how many different values, and how the cells divide

The K numeric cells are divided into **strata**. One stratum holds one
value; a stratum of size `g` puts that one value in `g` cells. Strata
exist because raw distinctness is a published fact and a numeric column
may hold far fewer different values than cells.

Let `F_num` be the folded-spelling budget this column's numbers may use
(G6.5 computes it; where the column has no other class of cell it is
just `n_distinct_folded`). Then

```
M = min(K, F_num)          the number of different VALUES
```

`M` is the largest value count the distinctness facts allow, and largest
is deliberate: every value the ladder is allowed to distinguish is a
value the twin keeps.

The strata are laid out in one fixed order — **negatives ascending, then
the zero stratum, then positives ascending** — because that is the
sorted order of the column's own values, and the ladder is a statement
about sorted order.

```
M_zero = 1 if Z > 0 else 0
M_rest = min(M - M_zero, G + P)           (refuse if M - M_zero < 0)
```

**A stratum with no cell in it is not a value** (P2-C1-F5). Only the
negatives and the positives are divided into strata, so at most `G + P`
of them can hold a cell, and `M_rest` is capped at that. Without the cap
a column of nothing but zeros whose published spelling count is large --
which owner decision 8's leading-zero family makes ordinary, since one
value has as many spellings as a description asks for -- built one
empty stratum per spelling. Each of those still took an end of the
ladder in G5.3 and still had its sign repaired in G5.5, so the run named
an endpoint deviation about a value the twin never wrote. A published
count of different SPELLINGS is not a count of different VALUES: G6.5 is
where the spellings come from.

If `G > 0` and `P > 0`:

```
M_neg  = the integer nearest to M_rest * G / (G + P), ties upward,
         computed exactly in integers as
         M_neg = (2 * M_rest * G + (G + P)) // (2 * (G + P))
then clamp M_neg into [1, M_rest - 1]
M_pos  = M_rest - M_neg
```

If `G == 0`, `M_neg = 0` and `M_pos = M_rest`. If `P == 0`, `M_pos = 0`
and `M_neg = M_rest`. A clamp that cannot be satisfied (`M_rest < 2`
with both `G > 0` and `P > 0`) means fewer different values are
permitted than the sign facts require; the sign facts win (P2-D6
feasibility rule 4), `M` is raised to the smallest value that satisfies
them, and the report names the raised distinct count beside the
published one.

Within the negatives, the `G` cells are divided into `M_neg` strata by
the even split

```
size of stratum i = floor((i + 1) * G / M_neg) - floor(i * G / M_neg)
```

for `i = 0 .. M_neg - 1`, and the positives likewise over `P` and
`M_pos`. The zero stratum, when it exists, has size `Z`.

**The carrier step: the cells a published point-free count needs**
(P2-C4-F3). Three of the six styles of G6.1 — `plain`, `leading_zero`
and `leading_plus` — can be worn only by a cell whose value has a
point-free spelling (G6.2), so how many such cells a column HAS is
settled here, by the split, before any style is chosen. Let

```
W      = plain + leading_zero + leading_plus in the published
         `numeric_styles` map, with the `(withheld)` remainder added
         to `plain` (G6.4), capped at K
W_plus = the published `leading_plus` count, capped at Z + P
```

A stratum **can carry** a point-free value exactly when it is the zero
stratum, whose value is exactly `0`; or a pinned end whose published
rung has a point-free spelling; or any other stratum, because the
values step of G6.4 may take it to a whole number.

Write `Room(reachable)` for the most cells the strata that can carry
could ever cover inside a set of sign bands: a band with no stratum
that can carry offers nothing, because cells never cross a sign band,
and a band that has one offers every cell it holds except the one each
of its other strata must keep. `Room` is taken over every band for `W`,
and over the zero and positive bands alone for `W_plus`.

**The band step, taken first.** How the different values divide between
the negative and the positive side is no more published than how many
cells each holds. A band left with ONE stratum, where that stratum is a
pinned end whose rung carries a point, can carry no point-free cell at
all, and every cell of that band is stuck on it. So where `Room` falls
below its demand, ONE stratum moves into such a band from the other
divided band — `W_plus` considered before `W`, and the negative side
before the positive — provided the other band keeps at least one and
the move raises `Room`. Each band gains at most one stratum. `S`,
`M_zero`, the sign counts and the draw budget of G4.3 are all
unchanged: both bands keep a stratum, so the zero stratum keeps its
place in the order, and G4.3 counts strata rather than cells. A 58-cell
column publishing forty-one `leading_zero` cells, ten negative cells
and a `min` of `-45.5` had `M_neg = 1`: without this step its ten
negative cells were stuck on `-45.5` and TWO NAMED counts came out
short.

**The cell step, taken second.** Where the strata that can carry cover
fewer than `W` cells, cells move into them until they do, or until no
more can move:

- `W_plus` is settled first, and only over the zero and positive bands,
  because there is no leading-plus spelling of a negative value;
- cells move only WITHIN a sign band, so `G`, `Z` and `P` are exactly
  what they were;
- no stratum is emptied, so `S` is exactly what it was;
- the fewest cells the demand needs are moved: taken from the strata of
  that band that cannot carry, in ascending `s`, each down to size 1,
  and shared out over the strata of that band that can carry by the
  same even split above.

**The reach step, taken third** (P2-C5-F3). "Can carry" above is a
PLAN, not a certainty: every stratum that is neither a pinned end nor
the zero stratum is counted because the values step of G6.4 MAY take it
to a whole number. On a ladder that crowds several different values
inside one unit that plan does not come true — four values between
`0.125` and `1` leave their strata one whole number between them — and
the cell step then moves nothing, because by its own count nothing
needed moving. A genuine 82-cell producer column published 34
point-free cells and the twin wrote 20 on three seeds and 30 on two.

So the question is put to the LADDER and the answer is taken to a fixed
point:

- a stratum **really carries** exactly when its own share of the
  published ladder — the closed interval from `Ladder(c[s]/K)` to
  `Ladder((c[s]+g[s])/K)`, read by G5.6's own rule — holds a whole
  number that is inside its sign band, inside the published `min` and
  `max`, has a point-free spelling (G6.2), and is not one another
  stratum holds. Strata are offered their candidates in ascending `s`,
  each from the middle of its own share outward, which is where a drawn
  value sits on average and therefore which number `_whole_inside`
  takes;
- a stratum whose share does not move at all — the ladder is flat
  across it — is CERTAIN to hold that one value, so it claims it before
  the walk begins. Deciding in stratum order instead gave the number to
  an earlier stratum whose share merely touched the flat rung, and at
  run time the flat one took it anyway and the earlier one came back
  with nothing;
- the two sign fallbacks of G5.5 are treated as spoken for wherever a
  stratum's share crosses its own band's sign, because which side a
  drawn value falls on is a function of the seed and the split may not
  be;
- where the strata that really carry cover fewer than `W` cells, the
  cell step above runs again on this answer;
- and where a band's strata ALL sit on fractions, so that no cell can
  move anywhere useful, ONE stratum's window moves instead: the band's
  last stratum that may take a value at all is given the narrowest
  window of the ladder that reaches a free whole number, widened to the
  cells the demand still needs with its start moving first, and the
  band's other strata divide what is left by the same even split, each
  keeping one cell. `G`, `Z`, `P`, `S` and the draw budget are
  untouched;
- the two steps repeat until both demands are met or a round changes
  nothing, which is bounded by the strata themselves.

A column publishing `integer_valued: true` skips this step: G5.4 makes
every value whole, so every stratum carries already.

**Why the split gives way and the count does not.** A numeric block
publishes no multiplicity map — nothing in it says how many cells hold
each different value — so the even split is this method's own default,
not a published fact. `numeric_styles` IS published, and
EXACT-OBSERVABLE (contract 7.5.7, 9.4). Plan P2-D6's feasibility rule 4
fixes the order: published counts take precedence over ladder
conformance where the conflict is otherwise resolvable. The cost is
paid in the open rather than absorbed, because `g_max` in G5.6 is read
off the strata this step produces, so the rung envelope widens by
exactly what the step spent and by nothing else. Revision 1 had no such
step and left a producer's own style map unreachable: a 51-cell column
holding eleven `1.5`, twenty `100` and twenty `200.5` publishes twenty
`plain` cells, its own values prove the map, and an even three-way
split gave the one stratum that could hold a whole number seventeen
cells and named the other three as missed.

Number the strata `s = 0 .. S - 1` in the fixed order above, where
`S = M_neg + M_zero + M_pos`. Let `c[s]` be the number of cells in all
strata before `s` (so `c[0] = 0`) and `g[s]` the size of stratum `s`.
Then `c[S - 1] + g[S - 1] = K`.

### G5.3 The value of each stratum: pinned ends, stratified inverse transform, no word for a zero

For each stratum `s`, in ascending `s`:

- **`s == 0`**: the value is `L[0]` — the published `min`, used exactly
  as published. No word.
- **`s == S - 1` and `S >= 2`**: the value is `L[10]` — the published
  `max`, exactly. No word.
- **the zero stratum** (when it exists and is neither of the above): the
  value is exactly `0`. No word.
- **any other stratum**: one word `w` is drawn, and the value is

  ```
  N_s = c[s] * 2**64 + g[s] * w              (exact integer)
  D   = K * 2**64                            (exact integer)
  ```

  which places the stratum's uniform inside the stratum's own share of
  the distribution: `N_s / D` lies in `[c[s]/K, (c[s]+g[s])/K)`.

  Find the ladder segment `j` — the unique `j` in `0 .. 9` with

  ```
  PCT[j] * D  <=  100 * N_s  <  PCT[j+1] * D
  ```

  scanning `j` upward from 0 and stopping at the first that holds. Where
  two adjacent rungs share a probability this cannot happen (the
  probabilities are strictly increasing), so the segment is unique. Then

  ```
  A = 100 * N_s - PCT[j] * D                 (exact, 0 <= A < B)
  B = (PCT[j+1] - PCT[j]) * D                (exact)
  T = (A << 53) // B                         (exact, 0 <= T <= 2**53 - 1)
  t = ldexp(T, -53)                          (exact: a power-of-two scale)
  ```

  and the value is the **convex form**, in exactly this operation order,
  with exactly these four IEEE-754 binary64 operations and no others:

  ```
  u  = 1 - t                  (one IEEE subtraction)
  x1 = u * L[j]               (one IEEE multiplication)
  x2 = t * L[j+1]             (one IEEE multiplication)
  v  = x1 + x2                (one IEEE addition)
  ```

  followed by the **clamp**, in this order:

  ```
  if v < L[j]:    v = L[j]
  if v > L[j+1]:  v = L[j+1]
  ```

**Why the convex form and not `L[j] + t * (L[j+1] - L[j])`.** The
difference form overflows to an infinity when the two rungs sit at
opposite ends of the representable range, and it loses the interpolation
entirely between neighbouring subnormal values — the two failures review
item P1-R2-F4 found in the profiler's own arithmetic. The convex form
cannot overflow on either multiplication, because each product is
bounded by its own rung.

**Why the clamp is not decoration.** `1 - t` rounds, so `u + t` can
exceed 1 by one unit in the last place, and two rungs of the same large
magnitude can then sum to an infinity. More importantly the published
`min` and `max` are EXACT-OBSERVABLE: an interior value one unit in the
last place above `max` would change the twin's own recomputed maximum
and break a fact the profile publishes. The clamp bounds every value
inside its own segment, so every value is inside `[min, max]`, exactly.

`t < 1` always (`A < B` gives `T <= 2**53 - 1`), so `t = 1` is never
reached and the top of a segment is only ever produced by the clamp or
by the `max` pin.

### G5.4 The integer rule

When `integer_valued` is published **true**, every value of the K
numeric cells is a whole number. The rule is applied to each stratum
value after G5.3 and before G5.5, and it is applied by the FACT and not
by the role (P2-D6): a `continuous` column publishing
`integer_valued: true` gets it, and a `count` column publishing false
does not.

```
b = int(v)                  exact truncation toward zero
r = v - float(b)            exact; |r| < 1, sign follows v
if r >  0.5:  n = b + 1
elif r == 0.5: n = b + 1                  ties go toward +infinity
elif r < -0.5: n = b - 1
elif r == -0.5: n = b                     ties go toward +infinity
else:          n = b
```

**Rounding direction, stated once:** to nearest, and **ties toward
positive infinity**. Not banker's rounding, and not toward zero: two
implementations that disagree here disagree on bytes, and half-even
would make a twin's rounding depend on the parity of a neighbour.

Both subtractions are exact. For `|v| >= 2**52` the value is already
integral and `r` is zero; below that, `b` is exactly representable and
`v - float(b)` needs no more than 53 bits, so no rounding occurs.

`min` and `max` are themselves whole numbers whenever `integer_valued`
is true (every value was whole, so the extremes are), and rounding a
value inside `[min, max]` to a nearest integer cannot leave that
interval. The pinned strata are not rounded — they already carry the
published rungs — which is what keeps the endpoints exact.

### G5.5 Placing `n_zero` and `n_negative` exactly

The strata of G5.2 give the exact counts by construction: `G` cells sit
in negative strata, `Z` cells in the zero stratum, `P` in positive
strata. Two repairs make that construction true of the VALUES as well,
because the ladder and the sign counts are separate published facts and
nothing forces them to agree:

```
negative_fallback = the larger of L[0] and -1
positive_fallback = the smaller of L[10] and 1
```

Applied to every stratum after the integer rule, including the pinned
ones:

- a stratum in the negative band whose value is `>= 0` takes
  `negative_fallback`;
- a stratum in the positive band whose value is `<= 0` takes
  `positive_fallback`;
- the zero stratum's value is exactly `0` and needs no repair, because
  it was never drawn.

Both fallbacks are inside `[min, max]` whenever they are reachable: a
column with `G > 0` has a negative value, so `min < 0`, so
`max(min, -1) < 0`; symmetrically for the positive side. Both are whole
numbers when `integer_valued` is true, because a whole `min < 0` is at
most `-1`.

**The precedence is stated, not implied:** where the ladder and the sign
counts disagree, **the counts win** (P2-D6 feasibility rule 4). The
repair moves at most one value per conflicting stratum onto a fallback,
the deviation is measured against the published rungs, and the report
names it. Where a repair changes a PINNED stratum — which can happen
only for a profile whose `min`/`max` contradict its own sign counts —
the endpoint stops being EXACT-OBSERVABLE for that column and the report
names the achieved endpoint beside the published one.

### G5.6 The two-sided rung envelope

This is the acceptance bound the disposition battery applies to a
numeric column, and it is stated here because the method is what makes
it true.

Let `Ladder(p)` be the published ladder read as a piecewise-linear
function of a probability `p` in `[0, 1]`, using the same segment rule
and the same convex form as G5.3. Let `g_max` be the largest stratum
size of G5.2 and

```
d = (g_max + 2) / K
```

Then, for each of the nine INTERIOR rungs `i = 1 .. 9`, the rung `T[i]`
recomputed from the twin's own written numeric cells (by the profiler's
own type-7 quantile, over the parsed values) must satisfy

```
Ladder(max(0, PCT[i]/100 - d))  <=  T[i]  <=  Ladder(min(1, PCT[i]/100 + d))
```

and the two extreme rungs must be met EXACTLY:

```
T[0] == L[0]        and        T[10] == L[10]
```

**Why that window.** The cell that lands at recomputed rank `k` comes
from the stratum covering rank `k`, whose share of the distribution is
at most `g_max / K` wide, and a recomputed rung interpolates two
adjacent order statistics, which adds one more rank. So `d` is the
widest ladder displacement the construction can produce, and the bound
is a statement about the method rather than a tolerance somebody
measured and rounded up.

**What it must reject.** A mutant that ignores the nine interior rungs
and interpolates only between `min` and `max` produces
`T[i] ≈ min + (PCT[i]/100) * (max - min)`, which leaves this window on
any column whose ladder is materially non-linear. The battery is
therefore required to include at least one fixture whose interior ladder
is far from a straight line and whose `K` is large enough that `d` is
small — a fixture where the collapse mutant misses the window by more
than one rung — and to assert this bound on it. Rung mutants that
permute or swap the interior rungs are rejected by the same window.

**The same window holds rank by rank, not only at the nine rungs.** The
argument above never uses the fact that `i` is one of the eleven ladder
positions: it bounds the value at ANY recomputed rank. Writing `p_k =
k / (K - 1)` for the share the profiler's own quantile rule attaches to
sorted position `k`, every value `V[k]` of the twin's own sorted numeric
cells satisfies

```
Ladder(max(0, p_k - d))  <=  V[k]  <=  Ladder(min(1, p_k + d))
```

with the same `d`. On a column publishing `integer_valued: true` both
ends widen by the one half unit the whole-number rule of G5.4 can add,
and by nothing else. G12.3 derives the moment bounds from this rank
form, so the moments and the rungs rest on one statement about the
construction rather than on two.

Moments (`mean`, `std`, `skew`) are APPROXIMATED, and **G12.3 fixes a
formula and a finite two-sided bound for each of them**, derived from
the rank form above. Revision 1 of this document left that bound to a
test battery; review item P2-C1-F4 ruled that delegating a normative
bound to a battery leaves an approximated fact with no bound at all,
since a battery is not a document an independent implementer can
conform to.

## G6. Numeric spelling

### G6.1 The permitted family

Owner decisions 7, 8 and 10 fix the family. A numeric cell is written in
exactly one of six **styles**, and in no other form:

| style | what it writes | changes the type a reader infers? |
|---|---|---|
| `plain` | the canonical spelling (G6.2) | no |
| `leading_zero` | canonical, with one or more `0` characters inserted immediately after the sign | no |
| `leading_plus` | canonical, with a `+` written before a non-negative canonical spelling | no |
| `decimal` | the value in fixed-point notation with at least one digit after the point | yes — a whole-number column reads as a decimal one |
| `exponent_lower` | the value in exponent notation with a lower-case `e` | yes |
| `exponent_upper` | the value in exponent notation with an upper-case `E` | yes |

**Never a thousands separator** — the comma breaks the CSV row itself —
and **never accounting parentheses**, which are reserved for the
contradictory-notation stand-in of G10.3 and would otherwise change a
cell's class.

**Which decision governs which question** (P2-C1-F8). Decision 8 fixed
the family the twin may INVENT from — the leading-zero forms, which have
no ceiling and change no inferred type — for the spellings a published
distinctness count needs beyond the ones the style map already accounts
for (G6.5). Decision 10 then made the FORM of every cell a published
fact, and a published form is written because it is published: a
`decimal` cell carries a point because the real column's cell did, which
is the fidelity decision 10 was taken to protect. The profile contract
states the same division in its section 7.5.7, and the two documents are
checked against each other by a test.

**An alternate spelling is used only where the published counts require
it.** A column whose `numeric_styles` says every cell is `plain` is
written entirely in canonical spellings and is byte-plain, and is read
by an ordinary reader as exactly the kind of column the real one was.

### G6.2 The canonical spelling

For a finite binary64 `v`:

- **When the column publishes `integer_valued: true`** (so `v` is
  whole): the base-ten digits of the exact integer `int(v)`, with a
  leading `-` when negative, no decimal point and no exponent. `0` is
  written `0`, never `-0`.
- **Otherwise**: the shortest decimal digit string `D` and decimal
  exponent that read back as exactly `v` (shortest first, then nearest,
  ties to even significand), formatted by this rule, where `decpt` is
  the position of the decimal point relative to `D` — that is,
  `v = 0.D × 10**decpt`:
  - `-4 < decpt <= 16`: fixed-point notation, with `.0` appended when no
    fractional digit would otherwise be written;
  - otherwise: exponent notation `d[.ddd]e±XX`, lower-case `e`, sign
    always written, exponent at least two digits.

  This is exactly what Python's `repr` of a float produces, which is
  what the implementation uses; the rule is stated in full so an
  independent implementer in another language does not have to
  reverse-engineer it. Examples that pin the boundaries: `1e+16`,
  `1000000000000000.0`, `0.0001`, `1e-05`, `5.0`, `-2.5`.

**The POINT-FREE spelling of a value, and why it is not always the
canonical one** (P2-C2-F2). Three of the six styles — `plain`,
`leading_zero` and `leading_plus` — write a text carrying neither a
decimal point nor an exponent, because that is what the contract's
first-match ladder (contract 7.5.4) counts them by. On a column
publishing `integer_valued: false` the canonical spelling of the whole
value `100` is `100.0`, which that ladder counts as `decimal`, so a
generator writing canonical spellings can place none of those three
styles on such a column at all. That is not what the profile says
happened: a real column holding `1.5` beside `100` publishes eleven
`decimal` cells and forty `plain` ones, and the forty were written
`100`, `101` and so on.

So the point-free spelling of a value `v` is defined for its own sake:
let `D` and `decpt` be the shortest round-trip digits and decimal point
of G6.2. Where `decpt >= len(D)` — that is, `v` is a whole number — the
point-free spelling is the sign, `D`, and `decpt - len(D)` trailing
zeros, and it reads back through `parsing.parse_number` as exactly `v`.
Zero is written `0`, never `-0`. **There is no width ceiling** (owner
decision 10, 2026-08-13): an earlier revision stopped at
`-4 < decpt <= 16`, which is the fixed-point window of the CANONICAL
spelling, and that window governs the numbers inside a profile document
rather than the spelling of a cell in the twin. A plain cell owes that
it reads back as the same number and that it classifies as plain, and
the digits of a whole value do both however many there are; while the
ceiling stood, a column whose source wrote `100000000000000000000` in
figures was published `plain` and written back with a point. Where `v`
is not whole, no point-free spelling of it exists; the canonical spelling stands in its
place and G6.4 does not offer the three styles to such a cell unless
every other quota is already spent.

Every canonical spelling reads back through the shipped
`parsing.parse_number` as exactly the same binary64 and classifies as
`NUMBER` through `parsing.classify_number`. That is a property a test
asserts over the reference vectors, not an assumption.

### G6.3 The five alternate spellings

Let `sign` be the leading `-` of the canonical spelling (possibly
empty), and `body` the rest.

- **`leading_zero`, order k (k >= 1)**: `sign` + `k` copies of `0` +
  the POINT-FREE spelling's body. `00`, `000`, `0005` are this style.
  The supply is unbounded — one value has as many leading-zero spellings
  as a profile can ask for — which is why decision 8 chose this family
  and why capacity never binds a numeric column's raw distinctness.
- **`leading_plus`**: `+` + `body`, permitted only when `sign` is empty.
  There is no leading-plus spelling of a negative value; G6.4 says what
  happens when the counts ask for one anyway.
- **`decimal`**: the shortest round-trip digits written in fixed-point
  notation whatever `decpt` is, with `.0` appended when there would
  otherwise be no fractional digit. `5` becomes `5.0`; `1e+16` becomes
  `10000000000000000.0`.
- **`exponent_lower`**: the shortest round-trip digits written as
  `d[.ddd]e±XX` whatever `decpt` is, lower-case `e`, sign always
  written, exponent at least two digits. `5` becomes `5e+00`.
- **`exponent_upper`**: the same with `E`. `5E+00`.

The exponent pair is the ONLY place a numeric spelling carries case, so
it is the only construction that can make a numeric column's folded
count fall below its raw count (G6.5).

**The leading-zero family is available INSIDE every style but `plain`**
(P2-C2-F3). Owner decision 8 chose that family because it has no
ceiling and changes no type a reader infers, and decision 10 then made
the form of each cell a published fact. Revision 1 reached for the
family only where the assigned style was literally `leading_zero`,
which left a column reproducing a `decimal` or an exponent form with
one spelling of a value and no way to make a second: a profile
publishing thirty-six `decimal` cells, three raw identities and three
folded identities held one identity in the twin and named the loss.
Zeros written straight after the sign leave the contract's ladder
exactly where it was for the other four styles — a point keeps a cell
`decimal`, an `e` or an `E` keeps it in its exponent case, a leading
plus keeps it `leading_plus` — and the value each reads back as is
unchanged. So each of the five carries an **order k >= 0**, where order
zero is the style's own base spelling and each step writes one more
zero after the sign: `0.0`, `00.0`, `000.0`; `+5`, `+05`, `+005`;
`1e+05`, `01e+05`, `001e+05`. `plain` is the one style with no family,
because a zero in front of a plain spelling is what makes it
`leading_zero`, and a column whose whole map is `plain` therefore
reaches its published distinctness only as far as its different values
carry it (G12.8).

### G6.4 Which cell gets which style

`numeric_styles` publishes a count per style, plus a withheld remainder
(a style used by fewer rows than the small-cell floor is pooled, exactly
as a rare label is). **A pooled cell is written by its own value**: in
the `plain` style where the value has a point-free spelling, because
that is the style that changes nothing a reader infers, and in the
value's own canonical text (contract 3.2.1) where it has none. The
report names how many cells the remainder covered and how many of them
had no point-free spelling.

**This amends the rule that wrote every pooled cell plainly** (Phase 3
plan P3-D8.1, 2026-08-12, closing the registry's open P2-C5-F3). A
published `min` or `max` carrying a decimal point has no point-free
spelling, and both ends are EXACT-OBSERVABLE, so a column whose
remainder covered such a cell owed a form no conforming generator could
write. Nothing published moves: the amendment gives the anonymous
remainder — which names no form at all, that being what pooling MEANS —
a spelling its own cells can carry.

**The recount is therefore the identity contract 7.5.7 states**, whose
clauses are these, with `r(s)` the recount, `p(s)` the published count,
`R` the remainder and `NW` the written numeric cells with no point-free
spelling: `leading_zero`, `leading_plus` and `exponent_upper` exact;
`plain`, `decimal` and `exponent_lower` never below their published
counts; the spill `D = max(0, NW - p(decimal) - p(exponent_lower) -
p(exponent_upper))`; `r(decimal) + r(exponent_lower) = p(decimal) +
p(exponent_lower) + D`; `r(plain) = p(plain) + R - D`; and, in each of
`decimal` and `exponent_lower`, at most `p` of its cells carry a text
that is not the canonical text of their own value, so a pooled cell can
never be re-spelled into a form the description never named. `NW` is
read off the VALUES and never off the spellings — the count of written
numeric cells whose value has no point-free spelling — because counting
the cells WRITTEN with a point would let a twin inflate its own `D` and
balance the arithmetic against itself. No cell text falls outside the
six styles, so there is no "outside the published styles" bucket for the
remainder to be counted in.

Styles are assigned over the K numeric cells in the fixed **stratum
order** of G5.2 (which is the sorted order of the values), by
**largest-remaining-quota**:

```
remaining[style] = the published count of that style,
                   plus the withheld remainder added to `plain`
pool         = the withheld remainder still standing inside
               remaining[plain], capped at it
carriers[i]  = how many cells from i onward can wear a point-free
               style; plus_carriers[i], how many of those are not
               negative
for each cell, in stratum order, and within a stratum in ascending
cell index:
    consider only the styles this cell's value can wear (below) whose
        remaining count is above zero -- and, where the point-free
        claims still standing outnumber carriers[i + 1], `plain` is
        offered to a cell that can wear no point-free style too,
        while the pool is still standing, spending one pooled cell
        and writing it in the value's own canonical text.  Among
        the styles offered, consider only those whose
        choice leaves
            remaining[leading_plus]        <=  plus_carriers[i + 1]
        after the choice is taken.  Write
            owed = remaining[plain] + remaining[leading_zero]
                     + remaining[leading_plus], after the choice
            named = owed  minus the pool still standing after the
                     choice
        and take the FIRST of these four that offers a style:
        1. the largest remaining count among the styles whose choice
           leaves  owed <= carriers[i + 1];
        2. the largest remaining count among the styles whose choice
           leaves  named <= carriers[i + 1];
        3. the largest remaining count among the POINT-FREE styles
           this cell can wear, and G12 names the miss;
        4. the largest remaining count this cell can wear at all,
           and G12 names the miss;
    ties are broken by the enumeration order
        plain, leading_zero, leading_plus, decimal,
        exponent_lower, exponent_upper;
    decrement its remaining count, and where the style taken is
        `plain` and the pool is still standing, decrement the pool
        first.
```

**Why the second answer exists** (P2-C4-F3). The pool is the count of
cells whose form the description WITHHELD: it says how many there were
and never which of the six they were, so a pooled cell is written
plainly wherever its value has a point-free spelling, because plain
changes nothing a reader infers, and in the value's own canonical text
where it has none (P3-D8.1). Where the point-free cells cannot carry
every quota, something has to give, and it is the anonymous claim that
gives — never a count the description names. A column publishing
twenty-five `leading_zero` cells and a pooled remainder of ten, on a
ladder whose two ends carry points, has thirty-three point-free cells
for thirty-five claims: it writes all twenty-five named `leading_zero`
cells, eight pooled cells plainly, and the remaining two in their own
values' canonical text — every cell has a spelling and no named count
moves. Answer 1 alone spent the shortfall on both claims at once and
missed the named count by one.

**Why the third answer exists.** Reaching it means the point-free
counts cannot all be placed however the rest of the column goes. Every
cell that can wear a point-free style must then wear one, because a
carrier spent on a form any cell could have worn makes the shortfall one
cell worse than the column's own values force — and the shortfall is a
published count. So answer 3 offers only the point-free styles, and
answer 4 is reached only by a cell that can wear none of them. **This is
what makes the miss the values' own size and not the placement's**: on
every description this method's battery reaches, the cells written
point-free are exactly the cells whose value HAS a point-free spelling.

**What "this cell's value can wear" means, in full** (P2-C1-F8,
P2-C2-F2). Revision 1 gave one example — a leading plus on a negative
value — and called it the only one. It is not. A cell's style is not a
label the generator keeps beside the cell: it is what the contract's own
first-match ladder (contract 7.5.4) makes of the text the twin finally
writes, because that ladder is what the recount from the CSV runs. So a
style can be given to a cell only where the finished text would classify
back as that style:

- **`leading_plus`** needs a value that is not negative.
- **`plain`, `leading_zero` and `leading_plus`** need a value with a
  POINT-FREE spelling (G6.2) — a WHOLE value, at any width (owner
  decision 10; the fixed-point window this clause used to name governs
  the canonical spelling and not this one). `12.5` has none; inserting
  zeros or a plus in front of it leaves the point exactly where it was,
  so `012.5` classifies as `decimal`, not as `leading_zero`. `1e+16` and
  `1e+20` DO have one — their digits — which is what keeps a column of
  wide whole numbers reading as whole numbers.
- **`decimal`, `exponent_lower` and `exponent_upper`** can spell any
  finite value.

**The look-ahead is part of the rule, not an optimisation** (P2-C2-F2).
Largest-remaining alone spends a cell that could have worn a point-free
style on a form any cell could have worn, and the quota then arrives at
the end of the column with nothing left to carry it. The two conditions
above are exactly what stops that, and together with the values step
below they make **every producer-feasible style map come out exactly**.

**The VALUES step, taken before the styles** (P2-C2-F2). The map and
the values are one question: a `plain` quota needs cells whose values
are whole, and on a column publishing `integer_valued: false` the
ladder hands back values that mostly are not. So, before styles are
assigned, take `W` and `W_plus` from G5.2's carrier step — they are the
same two numbers the split was made to serve. The walk is taken twice,
in the order the carrier step uses and for the same reason: first over
the strata that are not negative until the cells they cover reach
`W_plus`, because a plus needs a value that is not negative as well as
one with no point, and then over every stratum until the cells they
cover reach `W`. Without the first pass a walk could cover `W` entirely
out of the negative band and leave a published `leading_plus` count
with nowhere to go. Each pass counts the cells whose stratum value
already has a point-free spelling and, while that count is below its
demand, walks the strata in ascending order and gives the FEWEST of
them whole values that the shortfall needs, taking each stratum's value
to the nearest whole number by the rule of G5.4. Two strata are never taken: the two pinned
ends, which hold the published ends of the ladder. Three further rules
bound which whole number a stratum may take, and none of the three may
be traded for a style: it never crosses zero, so `n_zero` and
`n_negative` are untouched; it is never a whole number another stratum
already holds, so the count of different values does not fall; and it
is never outside the published `min` and `max`. **That third rule is
not decoration** (P2-C4-F3): G5.4 rounds a tie toward positive
infinity, so a stratum whose value interpolated to `88.5` rounds to
`89`, and on a column whose published `max` IS `88.5` that puts a value
above an EXACT-OBSERVABLE end of the ladder. The step below takes `88`
instead. Where a stratum can take no whole number under all three, it
takes none, and the point-free demand is short by that stratum's cells.

**Where the nearest whole number is another stratum's already**
(P2-C4-F3), the stratum does not give up the published form: the walk
steps one unit at a time, `+1`, `-1`, `+2`, `-2`, and takes the first
whole number that meets all three rules above and lies within HALF A
UNIT of the stratum's own share of the ladder — the closed interval
from `Ladder(c[s]/K)` to `Ladder((c[s]+g[s])/K)`, read by G5.6's own
piecewise-linear rule, widened by `0.5` at each end. The walk is
bounded at `S + 1` steps, because at most `S` values are already held.
Revision 1 skipped such a stratum, which lost a published count on the
commonest shape there is: a column whose most frequent value IS its
published `min` gives the ladder a flat lower half, so the interior
stratum rounds onto the pinned end's own number. A value inside the
stratum's own share costs G5.6's window nothing at all, because that
window already bounds a rank by the width of the stratum covering it;
half a unit outside it is exactly what the NEAREST candidate can
already cost, and G12.2 widens for that half unit and no more. Revision
2 held the stepped candidates to the share ITSELF, which bought that
window nothing and lost a form: a 39-cell producer column whose ladder
is flat at `18` gives the flat stratum that number, and the stratum
just below it — whose share stops AT `18`, and whose own `17` sits a
fraction below the share — was left with no candidate at all on the
seeds where its value rounded up.

**A candidate outside the stratum's own share is refused where a LATER
stratum's share holds it** (P2-C5-F3). Two neighbouring strata can
reach one whole number, the earlier from outside its share and the
later from inside its own, and which of them got it then turned on a
drawn value rather than on anything the description publishes: a
54-cell producer column publishing 26 point-free cells wrote 26 on some
seeds and 20 on others. The refusal costs the earlier stratum nothing
it was owed — every whole number of its own share, and every one within
the half unit that no later stratum's share holds, is still open to it
— and it leaves the later stratum the only number it has.

**A quota that cannot be placed is a MISS, and naming it is not a
licence to leave it unplaced.** Where a quota's own cells exist, an
implementation that fails to put them there is defective, not
approximate. G5.2's carrier step and the two answers above are what
make the cells exist: the split gives way before a published count
does, and the anonymous pool gives way before a named count does.
**The remainder leaves no shape a producer writes** (Phase 3 plan
P3-D8.1): what a producer could once cost THROUGH THE POOL is placed
exactly now, because a remainder names no form and is spelled by its own
cells' values. **One producer-reachable shape survives, and it is not
the pool's** (review item P3-C2-F1): a column whose values are whole but
lie outside the fixed-point window of G6.2 is published `plain` by a
source that wrote it in figures, while the twin writes it with a
decimal point, so the plain count is missed and the spelling is named
beside it. That is the
window's own cost, it predates this repair, and the Phase 3 plan carries
it as a defect for the owner rather than as a disposition this method
grants. This method grants
`numeric_styles` no lesser outcome anywhere, and the shapes listed
below are reached only by a hand-written description whose own facts
contradict each other — the same class of document G12's refusals
settle, listed here because the walk answers them rather than stopping:

- a `leading_plus` quota larger than the column's own count of
  non-negative cells. No producer emits one — a cell it read as
  `leading_plus` was not negative — so this shape needs a hand-edited
  description whose own facts disagree.
- a NAMED point-free demand larger than `K` minus the cells the
  published ends force to carry a point. At least one cell must read
  back as `min` and one as `max`, both EXACT-OBSERVABLE, so an end that
  has no point-free spelling costs one cell of the demand. **No producer
  reaches this shape**: the named counts alone can never exceed that
  ceiling, because the source's own end cells were not written
  point-free either, so it takes a hand-written description whose facts
  disagree with each other. The twin writes the largest number of
  point-free cells the published ends leave, which is the most any
  conforming generator can write, and names the miss.

  **The producer-reachable half of this shape is CLOSED** (Phase 3 plan
  P3-D8.1, closing the registry's open P2-C5-F3). A producer reached it
  only through the anonymous pool, where it was the conflict between
  `min`/`max` exactness and the withdrawn rule that every pooled cell is
  written `plain`. A pooled cell names no form, so it is now spelled by
  its own value and there is nothing left to miss: measured over the
  producer battery of 240 descriptions at eight seeds, the eight columns
  that filed such a line file none.
The third shape revision 2 listed here — a stratum whose own share
holds no whole number free for it — **is no longer one of them**
(P2-C5-F3). Where a band's strata all sit on fractions the strata
themselves move: G5.2's reach step gives one of them a window of the
ladder that reaches a free whole number. The 82-cell producer column
that shape was written for reproduces its published `34` and `48`
exactly, on every seed.

Largest-remaining rather than a block per style, and the reason is
fidelity: a block assignment would put every exponent-styled cell at one
end of the distribution, so a reader of the twin would find style
correlated with magnitude where the real column had no such pattern.

**Except where one form per stratum is what the spelling count leaves
room for** (P2-C5-F3). Two styles inside one stratum write one value
two ways, so they cost a spelling, and a column with as many strata as
it has published spellings — which is the ordinary case, since `M` is
`min(K, F_num)` — has no room for that at all. The cell walk above then
meets `numeric_styles` by missing `n_distinct` and `n_distinct_folded`,
which is one published count bought with another. So where the walk's
own answer would spend more spellings than the column has, the styles
are packed over whole STRATA instead, by the same complete rule G9.5
states: every style quota is met exactly whenever any assignment of
whole strata meets them all, and each stratum keeps one form. It is
reached for only there, and where no such assignment exists the walk's
answer stands.

### G6.5 Reaching `n_distinct` and `n_distinct_folded`

Raw `n_distinct` counts different SPELLINGS over all present cells;
`n_distinct_folded` counts different folded identities, where folding is
trimming then Unicode `casefold`, as the shipped `parsing.folded` does.
A numeric column's present cells come from four classes, and different
classes never share a spelling (G10 constructs them so).

**Budget allocation across classes**, in this fixed order:

```
classes, in order:  numbers (K cells), out_of_range (O),
                    contradictory (C), not_numeric (N)
```

1. Every non-empty class receives one spelling. If `n_distinct` is
   smaller than the number of non-empty classes, the published facts
   cannot hold together: raw distinctness becomes REPORT-ONLY for the
   column, the twin uses one spelling per class, and the report names
   both counts.
2. The remainder of `n_distinct` is offered to the classes in the order
   above, each taking as much as it can use (never more than its own
   cell count), until the remainder is spent. The same allocation is
   made for `n_distinct_folded`. Call the numbers class's two shares
   `R_num` and `F_num`.

**Inside the numbers class**, with `M = min(K, F_num)` different values
already fixed by G5.2:

- The `M` stratum values each contribute their own spelling.
- `F_num - M` further FOLDED spellings are needed. Each is supplied by
  raising the leading-zero ORDER of a cell whose base spelling repeats
  an identity already written — inside whatever style G6.4 gave that
  cell, since every style but `plain` carries the family (G6.3). A
  stratum of size `g` can carry `g - 1` alternate spellings, and the
  total capacity `K - M` is always at least `F_num - M`, because
  `F_num <= K`.

  **How many zeros are spent is decided over the WHOLE column first**,
  not cell by cell. Count the identities the column's base spellings
  already hold; the shortfall against `F_num` is how many cells raise
  their order, and no more. A cell cannot tell from where it stands
  whether the identities still to come will cover the count on their
  own, and spending a zero that was not needed carries the count PAST
  the published one — a miss in the other direction, and just as
  visible to somebody grouping rows by the column. Cells are visited in
  the order of G6.4, and each that raises its order takes the lowest
  order whose folded identity is new.
- `R_num - F_num` further RAW spellings are needed, and each must fold
  onto a spelling already used. The only construction that does this in
  a numeric column is the exponent case pair: a value written
  `exponent_lower` and the same value written `exponent_upper` are two
  raw spellings of one folded identity. Each such pair therefore
  consumes one `exponent_lower` cell and one `exponent_upper` cell out
  of the quotas of G6.4.
- Where the published style counts do not supply enough exponent cells
  to make `R_num - F_num` pairs, the twin's folded count comes out equal
  to its raw count for those spellings; raw and folded distinctness then
  fall inside the two-sided envelope rather than being exact, and the
  report names the profile's counts beside the twin's (P2-D6).

**Precedence, stated:** the published style counts are met first, and
distinctness is met within them. That is the order P2-D6 already
implies — `n_distinct` is EXACT-OBSERVABLE "using the spellings owner
decision 7 permits, falling back to the two-sided envelope only where
even those cannot supply the count" — and it is stated here so two
implementations cannot resolve the conflict in opposite directions.

## G7. Datetime columns

### G7.1 The ordinal space

All datetime arithmetic in this method is **exact integer arithmetic in
ordinal space**. No float is formed anywhere in G7. The ordinal unit is
fixed by the published `resolution`:

| `resolution` | canonical form | ordinal unit | ordinal of a value |
|---|---|---|---|
| `date` | `YYYY-MM-DD` | one day | days from 1970-01-01, proleptic Gregorian |
| `datetime` | `YYYY-MM-DD HH:MM:SS` | one second | `86400 * days + 3600*HH + 60*MM + SS` |
| `quarter` | `YYYY-Qn` | one quarter | `4 * (year - 1970) + (n - 1)` |

The day count is the proleptic Gregorian civil-to-days function the
shipped `parsing._days_from_civil` computes, and its inverse is
`parsing._civil_from_days`; this method requires exactly those two, and
the leap rule they use (a year divisible by four is a leap year, except
a century not divisible by four hundred).

**Two cells do not travel through this space**: the endpoint cells of
G7.3, which are built from the published endpoint's own fields by
G7.5. The whole-second row above has one place for `HH:MM:59` and the
next for `HH:MM+1:00`, and none for the `SS` of `60` the profile
contract's canonical form admits — so an endpoint carrying one is
written from its fields, and the space below is left to the interior
ranks it is exact for.

### G7.2 What is generated, and what is a stand-in

```
P = n_present - n_unparsed     cells that parsed as dates
n_unparsed                      cells that did not
```

The `n_unparsed` cells are class-preserving neutral stand-ins (G10.4);
they are explicitly OUTSIDE the parsed-value representation obligation
(P2-D6) and are counted, not reproduced.

The `P` parsed cells are generated from the published
`date_percentiles` ladder, `earliest`, `latest`, `earliest_utc_offset`,
`latest_utc_offset`, `utc_offsets` and `datetimes_read_at`.

### G7.3 Values: the same stratified inverse transform, in integers

The ladder `date_percentiles` is a SELECTION ladder — the profiler
picks the value at the rung rather than interpolating, because there is
no half-way point between two dates a calendar would recognize. The
generator interpolates in ORDINAL space, which a calendar does
recognize, and rounds down.

Convert the eleven rungs to ordinals `Lo[0] .. Lo[10]`. The cells are
ranks `r = 0 .. P - 1` (one cell per rank; datetime columns are not
stratified by value, because no datetime multiplicity map is
published). Then:

- `r == 0`: the cell's instant is `earliest`, used exactly as published.
  No word. "Exactly as published" means the endpoint's OWN fields, not
  its ordinal: these two cells are built by G7.5's endpoint rule and do
  not pass through the space of G7.1 at all.
- `r == P - 1` and `P >= 2`: the instant is `latest`, exactly, by the
  same rule. No word.
- otherwise: one word `w`, and

  ```
  N_r = r * 2**64 + w
  D   = P * 2**64
  find j with PCT[j] * D <= 100 * N_r < PCT[j+1] * D
  A   = 100 * N_r - PCT[j] * D
  B   = (PCT[j+1] - PCT[j]) * D
  ordinal = Lo[j] + (A * (Lo[j+1] - Lo[j])) // B
  ```

  The floor division is the stated rounding direction: **toward the
  earlier instant**, always, including for ordinals before the epoch
  (Python's `//` floors toward negative infinity, and that is the
  intended behaviour — a rule that truncated toward zero would round in
  opposite directions on either side of 1970).

  `ordinal` is inside `[Lo[j], Lo[j+1]]` by construction, so it is
  inside `[Lo[0], Lo[10]]`, which is `[earliest, latest]` because the
  profile contract's D11 makes the ladder's two ends those two instants.
  So no interior cell can fall outside the published range and the
  endpoints stay exact. The step from one to the other was an unstated
  assumption until D11: with the pair untied, a hand-made ladder end
  below `earliest` put interior cells before the published earliest
  instant, and describing the twin again gave back an `earliest` the
  report had said nothing about.

`n_distinct` and `n_distinct_folded` on a datetime column are
APPROXIMATED under **the envelope of G12.5**, which is the one the
profile contract's matrix names for them (contract 9.6) and the one this
document derives from the rank windows of G12.4. An earlier revision
sent them to G5.6's numeric rung envelope with `g_max = 1`, which is a
bound on where a VALUE sits and not on how many different values a
column holds; two rules for one question is one too many, and G5.6 is
not the one either document's matrix points at. No repair is made for
these two counts (P2-D6, datetime cardinality); the recount of G12 names
them where the published count was missed.

### G7.4 Offsets: only where recorded

`utc_offsets` maps an offset text to a count, under the small-cell
floor, with a `(withheld)` key pooling everything below it and a
`(none)` key counting offsetless cells.

Allocation, over the `P` parsed cells in ascending rank:

1. Rank `0` takes `earliest_utc_offset` and rank `P - 1` takes
   `latest_utc_offset`, when each names a real offset — that is, when it
   is neither `(none)` nor `(withheld)`. Those two consume one from that
   offset's count. `earliest_utc_offset` and `latest_utc_offset` are
   EXACT-OBSERVABLE and this is what makes them so.
2. The remaining counts are spent over the remaining ranks in ascending
   rank order, taking the offset keys in the profile's own sorted key
   order, `(none)` and `(withheld)` last.
3. A cell allocated `(none)` is written with **no offset**.
4. A cell allocated `(withheld)` is written with **no offset** as well,
   and this is a loss, named as one: the profile does not say which
   offsets those cells carried, so the twin has no published way to
   spell them apart. See G11 instance 3.

**The clock conversion, which is not optional.** `datetimes_read_at`
says which clock `earliest`, `latest` and the ladder are written on:

- `local` — one offset wrote the whole column, so the published text IS
  the local wall clock. The cell text is the canonical form of the
  ordinal, and the offset is appended as published.
- `utc` — two or more offsets appeared, so the published text is the
  INSTANT. A cell that carries an offset must be written on that
  offset's own wall clock, or the twin would re-profile to a different
  instant. So:

  ```
  local_ordinal = ordinal + offset_in_seconds     (resolution `datetime`)
  local_ordinal = ordinal                          (resolution `date`,
                                                    `quarter`: no clock
                                                    to shift)
  ```

  where `offset_in_seconds` is `+/- (3600 * HH + 60 * MM)` read from the
  offset text, and `Z` is zero. The cell text is the canonical form of
  `local_ordinal` followed by the offset.

`datetimes_read_at` is EXACT-OBSERVABLE (P2-R4-F3) and is met by this
construction whenever the published offset map holds two or more keys,
because the twin then writes two or more offset kinds. Where the map's
only key is `(withheld)` and the published reading is `utc`, the twin
writes one kind, re-profiles as `local`, and the report names it. That
corner is bounded: it needs two or more distinct offsets each used by
fewer rows than the small-cell floor.

### G7.5 Writing the cell at the PUBLISHED precision (owner decision 5)

D12 fixed ISO 8601 with an explicit offset; owner decision 5 amended it
for twin CSV cells, because the producer legitimately publishes
offsetless dates and quarters and no output could satisfy both D12 and
the published facts. **A twin datetime cell is written in the ISO form
matching the precision the profile records, and an offset is written
only where the profile records a real one.** Exactly:

| `resolution` | `time_precision` | cell text |
|---|---|---|
| `quarter` | `quarter` | `YYYY-Qn` |
| `date` | `date` | `YYYY-MM-DD` |
| `datetime` | `minute` | `YYYY-MM-DDTHH:MM` |
| `datetime` | `second` | `YYYY-MM-DDTHH:MM:SS` |
| `datetime` | `subsecond` | `YYYY-MM-DDTHH:MM:SS.` + `subsecond_digits` digits |

then the offset suffix, when one was allocated: `Z`, or `+HH:MM`, or
`-HH:MM`, exactly as the offset key spells it.

**The table is COMPLETE, and that is now true of the contract as well**
(P2-C1-F6). Revision 1 of the profile contract permitted a sixth pair —
`resolution: datetime` with `time_precision: date` — for which no cell
text exists: written `YYYY-MM-DD` the column re-profiles with
`resolution: date`, and written with seconds it re-profiles with
`time_precision: second`, and both fields are EXACT-OBSERVABLE. The
producer cannot make that pair, because a value carrying no time of day
does not read as a date AND time at all, so the contract's invariant D6
now refuses it and its loader enforces that. Every pair a description
can carry has a row above.

**An offset is written only where `resolution` is `datetime`** (contract
invariant D9). A whole date and a quarter have no time of day for an
offset to move, and a cell written `2024-03-15+02:00` reads back as no
date at all.

**THE TWO ENDPOINT CELLS ARE BUILT FROM THE PUBLISHED ENDPOINT'S OWN
FIELDS, NOT FROM ITS ORDINAL** (review item P2-C2-F5). G7.3 pins ranks
`0` and `P - 1` to `earliest` and `latest` "used exactly as published",
and this paragraph is what makes that sentence literal. The ordinal
space of G7.1 round-trips every instant a whole-second count can hold,
and there is one a real reader can still hand a description that it
cannot: the last second of a leap minute, `SS` of `60`, which the
profile contract's canonical form admits at 6.6.2 because the shipped
reader accepts one. Read `earliest` (or `latest`) as its four fields —
the date, `HH`, `MM` and `SS` — and build the cell as:

1. `resolution` `date` or `quarter`: the published text itself, which is
   already the cell text the table above asks for.
2. `resolution` `datetime`: take the published date with `HH:MM` and
   `SS` of `00`, move THAT to the clock G7.4 allocates for this cell —
   unchanged where `datetimes_read_at` is `local`, shifted by
   `offset_in_seconds` where it is `utc` — and then write the published
   `SS` back into the seconds field unchanged. Every offset is a whole
   number of minutes (contract 6.6.2 bounds the minute field), so the
   move never touches the seconds field and a `60` survives it.

The result is then cut to the recorded `time_precision` by the table
above, and the offset suffix follows as usual. The cut can drop no
published detail: `minute` is the only precision with no seconds field,
and the contract's D10 admits it only where both endpoints' `SS` is
`00`. For every instant whose `SS` is `00` through `59` this produces
exactly the same bytes the ordinal route produces, which is why it moved
no case of G14.3's first nine when it was written; for `SS` of `60` it
produces the endpoint the description published, and G14.3's
`leap_second_endpoint` case freezes those bytes beside a committed
mutant that puts the ordinal route back.

**Both endpoints are therefore EXACT-OBSERVABLE, with no leap-second
exception**, which is what the ratified plan requires in its own words —
`earliest`, `latest` EXACT-OBSERVABLE in the representation owner
decision 5 fixes (`docs/plans/phase-2-generator.md` revision 5, P2-D6,
the datetime paragraph) — and what the profile contract's 9.6 now
states in the same words. An earlier
revision of this section instead declared the endpoint REPORT-ONLY
because the ordinal space has no room for the value. That was a true
statement about the ordinal space used to lower a bar the owner set;
the bar is restored and the ordinal space is no longer the endpoints'
route.

**The rule above has no case that declines** (review items P2-C3-F2 and
P2-C4-F1). Step 2 writes the published `SS` back on BOTH clocks, at
every instant the canonical form can spell. An earlier revision of this
paragraph named two descriptions on which the endpoint would instead be
met as far as it could be, recounted and named — a `time_precision` of
`minute` whose endpoint carries seconds, and an `SS` of `60` while
`datetimes_read_at` is `utc` — and an implementation followed it,
sending the second of those back through the ordinal space. The revision
that withdrew those two named a third in the paragraph below: a
shared-clock endpoint whose own offset moves its cell off the end of the
calendar. Each was an exception written beside a sentence that says
there is none, and the previous paragraph's own words apply to all
three: a true statement about what a cell can show, used to lower a bar
the owner set. All three pairs are now refused by the profile contract's
**D10**, on the same terms as its D6 refusal of the
`date`-beside-`datetime` pair, and its **D11** ties
`date_percentiles.min` and `.max` to the same two texts. No pair of the
three reaches a generator, so this method needs no rule for them, and it
states none.

**The endpoints are still checked on the written cell, not assumed from
the rule.** After the cells for ranks `0` and `P - 1` are built, each is
read back with the shipped date reader, put on the clock
`datetimes_read_at` names, and compared with the published `earliest`
and `latest`. Silence there was the defect: a fact the loader accepted
was quietly changed on output. The check is not a formality now that D10
and D11 stand, and it is not vacuous either: it fails on any
implementation that stops writing the ends from their own fields, which
is the regression this whole section exists to prevent, and a conforming
repository owes a case that puts that regression in and watches the
check catch it. What it is NOT is a route by which a
description gets a lesser end. Every description this contract's loader
accepts has an end this rule writes exactly; a disagreement here is a
defect in the implementation, and the run says so in as many words
rather than passing it off as an outcome the description asked for.

- **The separator is `T`**, on every `datetime` cell. The shipped parser
  accepts `T`, `t` and a space; `T` is the ISO form and one choice has
  to be made for the bytes to be fixed.
- **The fractional digits are zeros.** The profile publishes how MANY
  subsecond digits the finest cell carried and nothing about their
  values — the parser reads and discards the fraction — so any other
  digits would be an invented fact, and drawing them would cost words
  for a quantity no published fact constrains.
- **Every parsed cell is written at the same precision**, which is the
  finest the column recorded. That is what makes `time_precision`
  EXACT-OBSERVABLE: it is the finest precision any value writes, so at
  least one value must write it, and writing them all at that precision
  is the rule that needs no further fact.
- `format` is REPORT-ONLY and is NOT reproduced (P2-R4-F3, R-P2-7): a
  month-first source column yields ISO twin dates and re-profiles as
  `iso-date`. Code that parses dates with an explicit source format
  needs that argument changed, and the report says so.

## G8. Label columns (`constant`, `binary`, `categorical`)

A label column consumes no content words. Everything is fixed by
published counts, which is why a fully determined label column produces
seed-invariant bytes.

### G8.1 Published levels and their variants

For each entry of `levels`, in the profile's own list order (the
producer sorts by descending count then by label), the entry's `count`
cells are filled as follows:

1. **`variants`** (owner decisions 9 and 11) maps an exact spelling to
   its count. Each key contributes exactly its count of cells, written
   byte-for-byte as the key spells it. Keys are taken in the profile's
   sorted key order.
2. **`variants_withheld`** maps an occurrence count to how many distinct
   spellings occurred that often. For each key in ascending numeric
   order, and for each of its distinct spellings, one invented variant
   spelling is produced (G8.2) and used exactly that many times.
3. If the entry publishes neither key, or both are empty, all `count`
   cells are written with the normalized label itself.

The contract's invariant — each variant's count is at most its parent's,
and the variant counts plus the withheld pool sum exactly to the
parent's count — means no remainder can exist. A document that breaks it
is a loader refusal, not something this method repairs.

**Why the variants are written rather than the normalized identity
alone:** the producer folds case and trims spacing before publishing a
label, so a column holding `A`, `a`, `B`, `b` publishes two labels of
two rows each. A twin built from the normalized identities alone would
write `a, a, b, b` and repeat where the real column never did, breaking
the all-different obligation for every label role. Owner decision 9
directed that the variants be published so the twin can keep the values
distinct; this section is where that is spent.

### G8.2 Invented variant spellings

An invented variant must fold to its parent label, differ from every
spelling already used in the column, and be produced by a rule that has
an unbounded supply. In this order:

1. **Case flips.** Let the parent's alphabetic positions be
   `q[0] .. q[L-1]`, left to right. For `k = 1, 2, 3, ...` write `k` in
   binary and flip the case of position `q[i]` for every set bit `i`,
   with bit 0 the LEFTMOST alphabetic position. Skip any candidate equal
   to a spelling already used in this column, raw or after folding
   against a DIFFERENT parent. This supplies `2**L - 1` spellings.
2. **Trailing spaces.** When the case flips are exhausted (a parent with
   no letters exhausts them immediately), append `m = 1, 2, 3, ...`
   space characters to the parent's spelling. Folding trims, so every
   one of these folds to the parent; the reader preserves them
   (`skipinitialspace=False`, and minimal quoting does not quote for a
   trailing space); and the supply has no end.

A spelling that is only spaces cannot arise, because a published label
is not empty — an empty cell is an absent value, not a label.

### G8.3 Withheld levels

`suppressed_levels` says how many levels were withheld and
`suppressed_level_counts` gives their sizes as an anonymous multiset,
in ascending order. For each size in that list, in order, one invented
neutral label is produced and used exactly that many times.

The invented labels are `group-1`, `group-2`, `group-3`, … in order.
Each candidate is skipped and the number advanced when it collides,
raw or folded, with any spelling already used in the column. They are
neutral by construction: they carry no fragment of any real value, they
are not one of the spellings that mean "no value", they do not read as a
number or a date, they contain no comma or quote so they need no
quoting, and they do not begin with a character that a spreadsheet reads
as a formula.

### G8.4 The order of `content`

Published levels first, in profile order, each level's variants in the
order of G8.1; then the withheld levels in the order of G8.3. The
placement arrangement of G4.2 is what makes the rows random; the content
order is fixed so that two implementations build the same list.

## G9. Invention: alphabets, the enumeration, fold collisions, capacity

This section fixes what P2-R5-F4 carried to this gate: the invention
domain and its capacity rule, with a named refusal.

### G9.1 The three alphabets

Each alphabet is an ordered tuple of characters. The ORDER is part of
the specification, because it decides which spellings are produced
first.

| name | characters | size |
|---|---|---|
| `DIGITS` | `0`–`9` in ASCII order | 10 |
| `CODE` | `-`, `0`–`9`, `A`–`Z`, `_`, `a`–`z` — ASCII code-point order | 64 |
| `WIDE` | every printable ASCII character, U+0020 through U+007E, in code-point order | 95 |

`CODE` is exactly the alphabet the shipped `parsing.is_code_text`
accepts, which is what makes `n_code_alphabet` reproducible. `DIGITS` is
a subset of `CODE`, which is why an all-digit value counts toward
`n_code_alphabet` as well, and the constructions below rely on that.

**Positional constraints, which apply to every spelling the ENUMERATION
of G9.2 produces:**

- the first and last character is never a space, so no enumerated value
  can be changed by trimming or read as blank;
- the first character is never `=`, `+`, `-` or `@`, so no invented
  value creates a spreadsheet formula hazard the report would have to
  count — **with one carve-out, bounded by the packing** (owner
  decision 9): a two-character value of the code alphabet that is not
  figures alone and reads back as a whole number has no other spelling,
  and a description publishing those counts proves the real column held
  one, so the twin reproduces the character rather than refusing to
  build. It is reached only where no assignment of whole groups meets
  every published count without it, and the report counts it and names
  its column (published labels are a different matter: they are written
  unchanged, counted and warned);
- a comma or a quote character inside an invented value is permitted;
  the writer quotes the field and the reader reads it back unchanged,
  and a test asserts that round trip.

When a positional constraint rejects a character, the enumeration puts
the first character of the same alphabet that meets that constraint in
its place, in the alphabet's own order.

**The ONE construction outside the first constraint, and why it is
outside it** (P2-C2-F6). A fold-collision partner built by G9.3 may
carry a space at one or both ends. The first constraint exists so that
an enumerated value cannot be *changed* by trimming; a partner's whole
purpose is to come down onto a value already written once the ends are
trimmed, which is the same sentence with the sign turned over. The
constraint's other half is kept in full: a partner is built from a
parent that is not empty and holds no space at either end, so no partner
can be read as blank, and the character a spreadsheet would act on is
still never at the front. Every OTHER value of every column obeys the
constraint as written.

### G9.2 The enumeration, and why there is no search

The spellings of one alphabet `A` and one length `L` are enumerated as
plain base-`|A|` counting with `A[0]` as the zero digit and the leftmost
character most significant: index `k` in `0 .. |A|**L - 1` maps to the
string whose character at position `i` from the RIGHT is
`A[(k // |A|**i) mod |A|]`.

The **domain** of a column is enumerated by ascending length from
`min_length` to `max_length`, and within a length by ascending `k`.

The spellings a column needs are the first ones of that enumeration,
with the two extreme lengths pinned:

- the FIRST invented spelling of a column has length `min_length`;
- the SECOND has length `max_length` (when `max_length > min_length`);
- the rest follow the enumeration in order, skipping any spelling
  already used in this column.

The pins are what make `min_length` and `max_length` EXACT-OBSERVABLE.
They cost no word, exactly like the numeric endpoints.

**The index-to-spelling map is a mixed-radix decomposition and holds no
search of any kind.** The `n`-th spelling is computed in a fixed number
of steps from `n`, so two implementations cannot diverge by searching in
different orders.

**The WALK over that map does step past spellings, and its bound is
stated here** (P2-C1-F2). Revision 1 said no rejection loop existed
anywhere in the invention path. That was not true of the implementation
and cannot be true of any implementation of this document. **Five rules
reject a candidate after it is computed**, and every one of them is
listed here because an implementer who plans for fewer plans a walk that
is too short:

1. the spelling is one this column has already written, or one this
   column already folds onto;
2. the spelling reads back as some other numeric class than the one its
   group has to answer for (G10.2);
3. the spelling means "no value" (G10.3's list);
4. the spelling reads as a date under `parsing.DATE_FORMATS`;
5. only while a fold collision is being asked for (G9.3 step 1), the
   spelling holds no character with a case.

What is required, and is sufficient, is that the walk is BOUNDED:

- the walk over one family visits the indices `0, 1, 2, …` of that
  family in order and **stops at the family's own size** (G9.4), which
  is a number computed before the walk begins;
- a family that is spent returns "no more" rather than beginning again,
  so the walk cannot return to a spelling it has already written;
- the fold-collision ask of G9.3 is an ASK: a pass that insists on a
  letter-bearing candidate and finds none puts the walk back exactly
  where that pass began and takes it again without the ask, so the ask
  can never spend a family the ordinary rule could still have used. The
  pass gives up after **4,096** rule-5 rejections, and that number is
  NORMATIVE rather than an implementation's own choice: two programs
  giving up at different points would part company on the first family
  holding a letter-bearing spelling between their two ceilings, and the
  twin's bytes would stop being a function of the profile and the seed.
  Giving up MUST mean handing back "no more" so the rewind happens —
  carrying on inside the same pass would spend the very indices the
  rewind exists to protect (P2-C2-F8);
- the caller's response to "no more" is fixed by role in G9.4: a
  refusal for `free_text` and `numeric_unrepresentable`, and repetition
  under owner decision 6 for a declared identifier.

**The bound, stated truly** (P2-C2-F8). Revision 4 added a tighter
sentence: that the walk visits at most one more index than the number of
pieces of text the column has already written. **That sentence was
false, and a false normative bound is worse than a missing one, because
an implementer trusts it** — an implementation refusing at `used + 1`
rejects a family from which the walk does return a value. It is retired.
What is true:

- **Termination.** Let `room` be the family's capacity (G9.4) and `s`
  the index the family's cursor stands at when a value is asked for. The
  ordinary pass visits `s, s + 1, …` and stops at `room`; the cursor
  never moves backwards except for the one rewind the ask performs. So
  each index is visited at most once by the ordinary rule, at most
  `room` ordinary visits exist over a whole column, and a column asking
  `v` values of one family costs at most `room + A·v` index visits,
  where `A` is the ask ceiling. Every term is finite and computed before
  the walk begins.
- **Per value.** Producing one value visits at most `room − s` indices
  in the ordinary pass, plus at most `A` in the ask pass that may
  precede it, and **no bound smaller than that can be stated in terms of
  what the column has already written.** Rules 2 to 5 do not consult the
  column's history at all, so each can reject a run of consecutive
  indices with nothing yet written. Three witnesses in this document's
  own enumeration, each reachable with an empty history:

  | family | index | rejected because |
  |---|---:|---|
  | `out_of_range`, `CODE`, length 5, 1 word | 0 | `0e999` reads as an ordinary number, not an out-of-range one (rule 2) |
  | text, `WIDE`, length 1 | 11, 17 | `.` and `?` mean "no value" (rule 3) |
  | `number`, `DIGITS`, length 8 | 10101 – 10131 | `00010101` … `00010131` read as compact dates (rule 4) — thirty-one consecutive rejections |

  The first of those three settles the question on its own: one index is
  rejected and the second produces the first value of the column, so a
  walk that stopped after `0 + 1` indices would refuse a family that
  holds one.

### G9.3 Fold collisions when folded is below raw

When a column publishes `n_distinct_folded < n_distinct`, exactly
`n_distinct - n_distinct_folded` invented spellings must fold onto a
spelling already used. This obligation is binding and non-trivial: a
real 200-row single-character identifier profile publishes 200 raw and
122 folded, so 78 values must fold onto a partner.

**The fold this section has to reproduce is the SHIPPED fold, and the
shipped fold trims before it turns the case over** (P2-C2-F6). Revision
4 built partners by case flip alone, which is half of that operation, so
two whole classes of feasible collision could not be built at all: a
one-character parent holding a single letter offers exactly one case
variant, and a parent written in figures alone offers none. A column of
`a`, ` a`, `a ` and ` a `, which a producer describes as four raw
spellings, one folded identity and the length range 1 to 3, was written
as four folded identities and the miss was named. Naming it was honest
and wrong: owner decision 6 authorizes a lost distinctness count only
where width and capacity are jointly infeasible, and this column's own
source proves the pattern fits inside its own published length range. A
partner is therefore **a case flip, edge spacing, or both**.

The construction, in this order:

1. **Plan the budget first.** Let `X = n_distinct - n_distinct_folded`
   be the number of collision partners needed, and let `Y =
   n_distinct_folded` be the number of different folded identities. The
   first `X` folded identities are PREFERRED from the enumeration
   restricted to spellings holding at least one ASCII letter (in the
   `CODE` and `WIDE` alphabets this restriction removes only the
   all-digit and all-punctuation spellings; in `DIGITS` there are no
   letters at all). The preference exists because a case flip is the
   partner that leaves the length exactly where it was; it is a
   preference and not a condition, because step 2's second construction
   needs no letter. A pass that insists on a letter and finds none is
   put back where it began (G9.2), and the ordinary rule then takes the
   same spellings it would have taken anyway.
2. **Produce the partners.** The partners of one parent are one family,
   enumerated in this fixed order so that two implementations build the
   same ones:

   - the **edge spacing** is taken by ascending TOTAL number of spaces,
     starting at whatever total the parent needs to reach this partner's
     shortest permitted length and starting at none where the parent is
     already long enough; within one total the LEADING share ascends, so
     the spaces go to the end first, then are moved leftward one at a
     time. A total of `t` therefore supplies `t + 1` placements;
   - within one placement, the **case flips** of G8.2 are taken in
     ascending binary-counter order — for `k = 0, 1, 2, ...` flip the
     case of the alphabetic positions named by the set bits of `k`, bit
     0 the leftmost — with `k = 0` the parent's own case. A parent with
     `L` such positions supplies `2**L` of them;
   - the parent itself, which is no spacing and `k = 0`, is not one of
     its own partners and is stepped over.

   Case flips of the unspaced parent are therefore the first `2**L - 1`
   partners, in exactly the order revision 4 gave them, so a column whose
   collisions case alone could carry writes what it wrote before.

   **WHICH MEMBER OF THAT ORDER A SLOT TAKES** (review item P2-C4-F4).
   The three rules above say what the family IS; this says which member
   of it a slot gets, and the twin's bytes are fixed only by the two
   together. A slot takes the **first** member of its parent's family —
   read in the order above, from that family's own start — that meets
   both of the following and is turned down for no other cause:

   - the column has not already written that exact spelling, raw text
     against raw text;
   - its length is one the slot's own window admits (step 3).

   **Every slot walks the family from that family's start.** The one
   place the start moves is the first rule above: a slot whose shortest
   permitted length is longer than the parent begins at the total that
   reaches it, since no smaller total can produce a member that slot
   could hold at all. A member some other slot's window turned down is
   NOT spent — a later slot with a wider window may still take it — and
   **the number of partners a parent has already supplied decides which
   parent comes next (step 4), never which member of a family is
   taken.** A slot that began at the second member of the family, or at
   the member whose position matches its own ordinal among the partners,
   would step over a member the column has not written and no window has
   turned down; this rule forbids that.

   Worked on the four-spelling column above, written in figures so that
   the case flips supply nothing at all. The parent is `1` and the
   published length range is 1 to 3, so the family is `1 `, ` 1`, `1  `,
   ` 1 `, `  1` — each backtick pair holds one digit and one or two
   single spaces. The slot pinned to the longest published length starts
   at the two spaces that length needs and takes `1  `. The next slot's
   window is the whole published range, so its walk starts where every
   walk starts, steps over the parent, and takes `1 ` — the member the
   pinned slot walked past. The slot after it takes ` 1`. The three
   partners of that column are therefore `1  `, `1 ` and ` 1`, in that
   order, and `tests/reference/generation-branch-vectors.json` freezes
   them.

   Revision 5 fixed the order and left this choice to be worked out from
   it. Two implementations worked it out differently on exactly that
   column: one wrote the three partners above, the other wrote `1  `,
   ` 1` and ` 1 ` and left `1 ` unwritten. Both columns satisfy every
   published fact of that description, which is what made the difference
   easy to walk past and is precisely why it is settled here — the
   frozen vectors exist to fix the bytes, and an order two careful
   readers can complete two ways fixes none. This paragraph adds a
   requirement to G9.3 and takes none away.
3. **The length a partner may take is the length its own slot may
   take.** Spacing lengthens a value, and both published length ends are
   EXACT-OBSERVABLE, so each slot carries a window:

   - the slot holding the SHORTEST published length, and the slot
     holding the LONGEST, may take only that one length;
   - every other slot may take any length in the published range;
   - a role publishing no longest length at all —
     `numeric_unrepresentable`, whose width is not published (R-P2-1) —
     puts no end on the spacing.

   Step 1 fills the first `Y` slots with the folded identities and the
   `X` slots after them with partners, so the first slot is never a
   partner — nothing has been written for it to fold onto — and the
   SECOND is a partner exactly when `Y == 1`, which is to say when the
   whole column comes down to one identity. **In that case the second
   slot may be a partner**: spacing lengthens, so a partner CAN carry
   the longest published length while folding onto the shortest, which
   is exactly what the four-spelling column above asks for. Revision 4
   barred both of the first two slots on the reasoning that a partner
   copies its parent's length, and that reasoning is retired with the
   construction that made it true. Nothing else the second slot carries
   is put at risk by this, because `Y == 1` means every present cell has
   the same trimmed, case-folded text and therefore the same word count:
   the published word range is a single number there.
4. Partners are assigned to identities in ascending identity order, one
   each, then a second each, and so on, so that the collisions are
   spread rather than piled on one identity. A partner is only ever
   taken from a parent of its own FAMILY — its band, and on free text
   its numeric class as well — because neither construction moves the
   trimmed characters, so a partner reads back in its parent's alphabet
   counts and its parent's numeric class, and taking one from another
   family would meet the folded count by missing a different published
   one.
5. **The layout is CHECKED against what the families actually supplied,
   and repaired where a collision could not be built. THIS RAISES: a
   published `n_distinct_folded` that revision 5 missed on descriptions
   whose own values meet it is now met** (plan amendment A-P3-12).
   Steps 1 to 4 settle which slots carry the collisions before any
   spelling exists, and what a family can SUPPLY is a fact about
   spellings: its identities' own case positions, and whatever edge
   spacing their lengths leave inside the taking slot's window. Spacing
   only lengthens, so an identity pinned to the LONGEST published
   length supplies no spaced partner at all, and a family whose flips
   are spent supplies no further one. A layout can therefore ask one
   family for more collisions than it holds while another family of the
   same column has room to spare. Measured over 1,200 descriptions a
   real producer wrote, every one of whose own values is an exact
   assignment of every count it publishes: 44 of them, 3.7 per cent,
   lost the published folded count that way, and the feasibility check
   of G12 never fired on one of them, because that check counts a whole
   alphabet and knows nothing about families, slots or windows.

   So the column is laid out AGAIN. The layouts are offered in the
   fixed order below, and the FIRST one that supplies every collision
   it owes is the answer:

   1. **the layout of steps 1 to 4, unchanged and offered first.** A
      description that layout answers is answered by it, so this step
      can reach no column the earlier rule already met, and no twin
      that met every published count changes by one byte;
   2. **the same layout with every family that fell short asked for no
      more collisions than that layout showed it supplies**, the
      surplus passing to the next family G9.6's choice rule admits.
      Where the repeat falls short again the ceiling is lowered again,
      at most once per group;
   3. **layouts 1 and 2 with the slots carrying the two published
      length ENDS taking a collision before any other slot their family
      admits.** The pinned slot is the one place in a family where
      being an identity costs the family its whole spacing supply and
      being a partner costs it nothing: pinned to the longest published
      length an identity can be lengthened by nothing, while a PARTNER
      pinned there is built by spacing its own family's shorter
      identity out to that length;
   4. **all of the above over each further packing of G9.6**, in that
      section's own order, and then over the packings that section's
      search reaches by holding ONE group to ONE family. A description
      can have several exact packings; one that gives every group a
      family of its own leaves no slot a same-family sibling, so no
      collision can be built at all, where another packing of the very
      same counts puts two groups together.

   **A repair may not give up a count the first layout held.** The one
   count a different layout of the same packing can lose is the one
   this walk names for itself: a layout that ran out of spellings and
   had to write one twice gives up the raw distinctness count and the
   repetition pattern with it (owner decision 6). So a layout is
   accepted only when it repeats no more than the first layout did.
   Trading raw distinctness for the folded count is the trade this
   section refuses, and this refuses it by construction rather than by
   measurement.

   **The walk ends in a stated number of steps.** At most two hundred
   and fifty-six candidate packings are examined on one column, counted
   across both of G9.6's tiers; the per-family ceiling is lowered at
   most once per group; and every layout is a fixed function of the
   description, so two implementations that follow this order write the
   same bytes. Where every offered layout falls short the column KEEPS
   THE FIRST, and the folded count it missed is recounted from the
   finished cells and named as a deviation — which is what happened to
   every one of them before this step existed.

   **This step moves no other published fact, and the reason is
   structural rather than measured.** Every layout it offers assigns
   the same group sizes to the same class-and-alphabet families as some
   exact packing of G9.6, so all four class counts and both alphabet
   counts are met by construction; the collision choice is a
   permutation of the groups, and the occurrence multiset pairs a size
   with a made-up value and never with a position, so it is
   permutation-invariant; both published length ends travel with their
   carriers. What the step CAN move is which spelling a slot writes,
   and so how many cells open with a character a spreadsheet reads as a
   formula. Measured over the same 1,200 descriptions: 42 of the 44
   repaired columns write the same number of such cells as before and
   two write nine and twelve where they wrote none. Writing fewer of
   them conforms, here as in G9.6.

**Why edge spacing costs no other published fact.** `n_all_digits` and
`n_code_alphabet` are read from the TRIMMED value, so a space at either
end moves neither. Word counts are read as whitespace-separated words,
so a space at either end adds none. The numeric class a cell reads back
as is read after trimming, so a whole number stays a whole number. The
length is read from the raw cell, which is why step 3's window exists
and is the ONLY fact spacing can move. The twin writer quotes a field
for a comma, a quote character or a line ending and for nothing else,
and the reader reads with `skipinitialspace=False`, so the spacing
reaches the file and comes back unchanged.

**The bound on the walk over one parent's family.** Two different orders
of one parent's family build two different spellings — a different
spacing gives a different string, and a different flip set gives a
different string. A candidate is refused only when the column has
already written that exact spelling, so at most one order per piece of
text the column has recorded can be refused and the walk ends by the
time it has tried one more than that. This is a true bound of the shape
G9.2 says the ENUMERATION's walk does not have, and it is true here for
the reason it is false there: this family has no class check, no
"no value" check and no date check on it, because a partner inherits all
three answers from a parent that already passed them.

### G9.4 The capacity rule

Capacity is decided **before any cell of the run is generated**, in the
generation-feasibility stage, so a shortfall never produces a partial
file.

**Capacity is a property of a FAMILY, not of an alphabet** (P2-C1-F2).
Revision 1 defined it as

```
capacity = sum over L in [min_length, max_length] of |A|**L
```

and that number is not the domain any construction of this document
generates. Three rules narrow it, and all three were already in this
document when that formula was written: G9.1 fixes the first and last
character positionally, G9.5 step 4 fixes what the leftmost character
may be so that the value falls in its own alphabet band, and G10.2
requires every cell to read back as its own numeric class. The `WIDE`
alphabet at length one has 95 members; the ordinary-text construction at
length one in the wide band produces **25** different values, because
the space is refused at both ends, the four characters a spreadsheet
reads as the start of a formula are refused at the front, and two of the
remainder are spellings that mean "no value". A planner quoting 95 there
promises a column it cannot write.

**The definition.** A **family** is one (class, band, length, word
count) combination. Its capacity is the number of indices its
mixed-radix map (G9.2) has:

```
capacity(class, band, L, w) = the number of indices of that family's map
```

computed with a **saturating rule** — every power stops accumulating
once it passes `2**62`, which is far above any row count a table can
hold, so every comparison this decision makes is exact and the
arithmetic costs a few dozen multiplications whatever `max_length` says.

The capacity is an **upper bound on what the walk produces**, never a
lower one: the positional rules of G9.1 can put two indices onto one
spelling, and the three rejection rules of G9.2 remove candidates. That
direction is the safe one — a run can only ever write fewer values than
the capacity claims, never more — and the number a refusal quotes is the
number the WALK produced, counted by the same walk that would have
written the cells, so the message states a fact rather than a bound.

**Where the demand is settled.** The class of every group, its band and
its length are settled in the feasibility stage (G9.5 steps 1 to 5)
before any capacity question is asked, so every group belongs to exactly
one family and each family's demand is the number of groups in it. A
family whose walk runs out before its demand is met is what triggers the
outcome table below.

Where fold collisions are required, the same rule is applied to the
sub-domain a partner can be built FROM, and that sub-domain has two
halves because G9.3 has two constructions (P2-C2-F6): the spellings
holding a character with a case, which a case flip varies, and the
spellings shorter than the longest published length, which edge spacing
lengthens. Counting only the first is what refuses a column whose
collisions the second can build, so both are counted and their counts
add — two different parents never build the same partner. Only where
BOTH halves are empty are the collisions genuinely unbuildable: that is
a column whose one permitted length holds no character with a case,
which is the corner owner decision 6 governs on a declared identifier
and the `generation-domain-too-small` refusal on the other two roles.

**When capacity cannot be met**, the outcome depends on the role, and
each outcome is fixed here:

| role | outcome |
|---|---|
| `identifier` (declared) | **No refusal.** Owner decision 6 governs: LENGTH WINS and invented identifiers repeat. The fewest necessary values repeat, and the report names the column, the number of duplicates and the join consequence. Raw `n_distinct`, `n_distinct_folded` and `n_distinct_by_occurrences` all become REPORT-ONLY for that column, each achieved value named beside its published one (P2-R4-F4). |
| `constant`, `binary`, `categorical` | **Cannot arise.** The withheld-level and variant alphabets of G8 have no end. |
| `count`, `continuous` | **Cannot arise.** The leading-zero family has no ceiling (owner decision 8): order `k` is computed directly for whatever `k` the published counts ask for, and no implementation may impose a ceiling of its own (P2-C1-F5). |
| `datetime` | **No refusal.** Cardinality is APPROXIMATED under the envelope. |
| `free_text`, `numeric_unrepresentable` | **REFUSAL — `generation-domain-too-small`.** |

**This table settles CAPACITY, and capacity alone.** Two of the four
refusals G12 lists are raised for a different reason — published facts
that contradict one another outright rather than a domain that ran out —
and one of those reaches a declared identifier, whose row above says
only that a domain too small for its multiplicity map does not stop the
run. G12 carries the closed list of all four.

**The named refusal, and why it is these two roles.** Both publish
`n_distinct_by_occurrences` under multiplicity parity (owner decision
2): an exact repetition pattern, group size by group size. The map
exists precisely so that a generator never invents a repetition pattern.
Where the domain cannot supply the distinct spellings that map requires,
the only ways forward are to invent a different repetition pattern —
which the map forbids — or to write a value longer than `max_length`,
which contradicts a published length fact. No owner decision authorizes
either for these two roles, so generation refuses. The refusal:

- is a refusal of GENERATION and says so — **the profile is valid**;
- names the column, the length and the alphabet band of the family that
  ran out, what that family's values have to read back as, the number of
  different values the profile requires of it and the number the walk
  produced;
- names the two facts that cannot both hold, in the person's words;
- gives remediation that does not assume the person still holds the
  table.

It is raised in the feasibility stage, before any output file is
created, so a refused run leaves the folder exactly as it found it.

### G9.5 Free text

Free text is INVENTED language. The generator never samples, quotes,
templates from, or paraphrases source text, and no source text is
available to it in any case (G1). Any future change carrying source
language into the profile or the twin is a charter change requiring an
owner decision and a privacy review (P2-D9).

The construction, and its precedence order — each later constraint is
met only within the freedom the earlier ones leave, and the report names
any that could not be met:

1. **The repetition pattern.** `n_distinct_by_occurrences` fixes the
   groups: for each key (a row count, read as a number in base ten;
   leading zeros are padding and do not change it) in ascending order,
   and for each of that key's distinct values, one spelling is invented
   and used exactly that many times. The groups' sizes sum to
   `n_present` and their number sums to `n_distinct`, by the contract's
   own invariant. **Every published count below is a count of CELLS and
   every group covers a whole number of cells**, so meeting a count
   means choosing which GROUPS answer for it — see "the packing rule"
   after step 4.
2. **The lengths, and WHICH group carries each published end.** Step 5
   assigns a length and a word count to every group. **It is not settled
   before steps 3 and 4 and it may not be** (P2-C4-F2). Revision 5 said
   the lengths came first and depended on nothing the other steps
   decide, which is false in the direction that costs published counts:
   a length decides which class-and-alphabet pairs a group can stand in
   at all, so a shape fixed in advance can make a count unreachable that
   another shape reaches. Steps 2, 3 and 4 are therefore ONE allocation
   — see "the packing rule" after step 4.
3. **Numeric class.** The `n_numeric`, `n_out_of_range`,
   `n_contradictory` and `n_not_numeric` counts are met by the
   class-preserving constructions of G10, exactly as for a numeric
   column. A free-text column publishes these counts too, and they are
   EXACT-OBSERVABLE by construction on every role. A group may answer
   for a class only where some band can write that class at that group's
   length.
4. **The alphabets.** `n_all_digits` cells are written from `DIGITS`;
   a further `n_code_alphabet - n_all_digits` cells from `CODE`, each
   carrying at least one non-digit character at its leftmost position so
   it does not count as all-digits; the remaining cells from `WIDE`,
   each carrying at least one character outside `CODE` at its leftmost
   permitted position so it does not count as code-alphabet.

   **The bands a group may take depend on the class it took in step 3**,
   and that dependency is part of the rule rather than something an
   implementation may leave to chance (P2-C1-F1). A cell whose notation
   conflicts with itself is written inside accounting parentheses, which
   the code alphabet does not hold, so such a group can answer for
   neither alphabet count. A cell of ordinary text cannot be written in
   figures alone, because figures alone read as a number. Packing the
   two alphabet counts without those rules lets a count the description
   publishes be missed while a construction that could have met it goes
   unused.

   **A cell counted in the code alphabet holds ONE word**, because the
   words of step 6 are separated by a space and a space is not one of
   that alphabet's characters. **And so does a cell of any of the three
   numeric classes**, for a plainer reason that was left unsaid and cost
   an exact fact (P2-C4-F2): every numeric construction of step 3 writes
   one unbroken run of characters — a number, a number too large to
   hold, a notation inside accounting parentheses — and none of them has
   a space anywhere in it. The rule is therefore stated over FAMILIES
   and not over one band: a family that cannot hold a group's word count
   is not a family that group may be given.

   Every group but the two that carry the published word extremes may
   therefore have its word count brought down to one wherever the family
   it is given needs that: `n_code_alphabet` and the class counts are
   EXACT-OBSERVABLE and `words.mean` is APPROXIMATED, so the exact fact
   wins and the change is measured and named. The two groups carrying
   the ends keep their published word counts, and take only families
   that can hold them — and WHICH two groups those are is decided by the
   packing below, not before it. Reading this rule as being about the
   code alphabet alone let a word-extreme carrier be given a numeric
   class, write one word, and miss `words.max` with nothing said, which
   is why G12 now recounts all four ends from the finished cells.

   **TWO CHARACTERS ARE ENOUGH FOR A NUMBER IN THE CODE BAND**
   (P2-C4-F2). A number written in that band needs a character the
   figures do not hold, and a leading minus sign is one: `-3` reads back
   as a number, holds a character outside `DIGITS`, and is two
   characters long. Requiring three — which an exponent form needs —
   loses published counts a real table reaches, because a source of one
   one-character number, five two-letter words and six copies of `-3`
   publishes twelve code-alphabet cells of which six read as numbers,
   and its own values are an exact assignment. So this family begins at
   length two. At length one it is genuinely empty: one character that
   reads as a number is a figure, and a figure is all-digits.

**The packing rule, stated once for steps 2, 3 and 4** (P2-C1-F1,
P2-C2-F1, P2-C4-F2). Steps 3 and 4 are **ONE packing, not two**, and
step 2's choice of which groups carry the published ends is **part of
that same packing, not an input to it**. Every group
answers for one class count and one alphabet count at the same time,
and which PAIRS it may stand in depends on its own length, so deciding
the classes in one walk and the alphabets in a second throws away joint
assignments that exist. Round 2 built a five-row column with three
singleton numeric groups and one doubled text group whose joint
class-and-alphabet assignment is exact and which two separate walks
missed by one code-alphabet cell.

The packing is therefore stated over a GRID of cells carrying MARGINS.
A margin is one published family of counts that divides the cells
between them: here the rows are the four class quotas of step 3 and the
columns are the three alphabet quotas of step 4, and each group takes
exactly one cell of that grid out of the set its length permits. Given
the groups, every margin and each group's permitted cells, an
implementation MUST produce an assignment in which **every quota of
every margin is met exactly, whenever such an assignment exists**. A
largest-group-first greedy rule does not satisfy this and is not
conforming: on groups of 2, 2 and 3 with a digits quota of 4 it
writes 5.

**THE SHAPE IS PART OF THE ANSWER, NOT PART OF THE QUESTION**
(P2-C4-F2). "The set its length permits" is not a set the description
publishes: the description publishes only that SOME group's values are
`length.min` characters long, that SOME group's are `length.max`, and
the same for the two word extremes. Which group that is, and what
length every other group takes, is the implementation's own choice, so
an implementation that makes it before the packing has narrowed the
packing with a fact the profile never carried. Revision 5 did exactly
that — first group takes the shortest, second takes the longest — and a
producer profile loses a published count to it. Take a source of twelve
cells: one of
them holds two words in three characters; five hold one character that
the code alphabet has; six hold two characters it does not. The
description publishes `n_code_alphabet = 5`, and the source's own
twelve cells are an exact assignment of it. But pinning the longest
length and the largest word count onto the group of five bars that
group from the code alphabet, and no other group covers five cells, so
every seed wrote one code-alphabet cell against the five published.

So the completeness sentence above is read over the shape as well:
**every quota of every margin is met exactly whenever SOME shape the
description leaves open admits such an assignment**. The shapes are
offered in this fixed order, and the FIRST whose grid packs every quota
exactly is the one taken:

- the pairs of groups that may carry the two ends, in ascending order of
  the pair — the group taking the shortest length first, then the group
  taking the longest — so the description's own first two groups are
  tried first and a description the earlier rule already answered is
  answered identically, byte for byte;
- under each pair, first the reading that holds every other group to the
  length step 5's walk gave it, and then the reading that holds only the
  two end-carrying groups to their lengths and lets every other group be
  written at any published length. The first reading is preferred
  because it keeps the approximated average where the walk put it; the
  second is reached only where no pair's first reading packs every
  count, because `length.mean` and `length.p50` are APPROXIMATED and the
  counts are EXACT, and an exact fact outranks an approximated one. A
  group lengthened under the second reading takes the shortest permitted
  length at or above the walk's, so the average moves as little as the
  exact counts require, and where the middle length then lands outside
  the bound of G12.6 the report names it like any other approximated
  fact that could not be held.

**Two groups of the same size are the same question**, and that is what
keeps this bounded. No published count tells two groups covering the
same number of cells apart: the grid ranks a group by its size and by
nothing else, and step 5's walk gives the groups carrying no end the
same lengths in the same amounts whichever of two equal-sized groups
took an end. So a pair whose two SIZES an earlier pair already offered
can only fail the same way and is skipped, and the number of pairs
actually walked is the square of the number of different group sizes
rather than of the number of groups. A shape whose group sizes and
permitted cells repeat a shape already tried is skipped for the same
reason, since whether a grid packs depends on nothing else.

Where NO pair and no reading packs every count — which a description a
real table produced does not reach, because that table's own values are
one such shape — the description's own first two groups carry the ends
and the fallback below applies.

**A grid may carry more than two margins, and where the description
publishes more than two families over the same cells it MUST**
(P2-C3-F1). Two margins is this step's shape, not the rule's: an
unrepresentable column publishes three families over one set of cells
(G10.5), and the completeness sentence above governs all of them
together. An implementation that picks two of the published families,
derives the rest by a choice of its own, and packs that instead has
answered a question the description never asked — which is what lost
six exact counts on a genuine six-row column, in G10.5's own words.

The order is fixed so that two implementations pack the same way. Each
margin ranks its own counts in ascending order of their published
values, ties by the order the contract states them in; a cell then
carries one rank per margin and the cells are filled in ascending order
of those ranks read margin by margin, ties by the cell's own number,
which over two margins is exactly row-major order over ranked rows and
ranked columns. Within a cell the different group SIZES are offered in
ascending order and each size offers as many copies as the cell can
still hold, falling back to fewer; a fill that leaves a later cell
unable to finish is undone and the next is tried; and groups are handed
to their cells in group order, so the first cell takes the earliest
groups. A cell is the last of one of its counts exactly when nothing
after it can answer for that count, and then it takes what that count
still owes rather than choosing. A grid one cell wide is the
single-axis rule, which is how the same statement governs the alphabet
packing of a declared identifier (G9.6), and a grid of three margins is
how it governs the unrepresentable column of G10.5.

**The smallest quota is answered for first**, and the largest last:
inside every margin the counts are taken in ascending order of their
own published values, ties by the contract's own order, so the count
that absorbs whatever is left over is filled at the end. That is a
statement about the ORDER and not about the answer — the completeness
above is unchanged either way — and it is written down because it is
what keeps a genuine description answered at once. Filling the largest
count first spends the small group sizes on it and leaves the small
counts to be made out of the large sizes, which is the shape a packing
walk can spend an unbounded amount of time undoing.

**ONE thing bounds the walk, and it is not a bound on the SHAPE of a
description, on its size, or on the work the walk spends** (P2-C2-F1,
P2-C3-F1). Revision 1 carried two structural ceilings — one refusing
any profile publishing more than a stated number of different group
sizes, the other stopping after a stated number of steps in a walk with
no pruning — and round 2 showed a description the PRODUCER emits
reaching the first, losing three published counts an exact packing
reaches. The repair replaced them with a ceiling on WORK, permitted on
the assertion that no producer description could reach it, and round 3
disproved that assertion: a 2,710-row unrepresentable column with 38
groups, class counts 592, 879 and 1,239 and sign counts 1,578, 540 and
592 needs more work than the ceiling allowed. **All three ceilings are
withdrawn, and no implementation may carry one.** What is left is the
pruning, which costs no exactness at all:

Before the walk descends past one group size it asks, in one
whole-number test, whether the sizes it has not yet decided can still
reach a total the cell accepts; and on entering a cell it asks whether
every count still owed, on every margin, can be made at all from what
is unplaced. Both are necessary conditions, so a branch either of them
cuts held no answer. A state the walk has already found no answer for —
which cell is being filled, which sizes are unplaced, what every count
of every margin still owes — is never entered twice, and the number of
different states is finite and fixed by the description before the walk
begins, so **the walk ends on every input the loader accepts and no
count is traded to make it end**.

**What that costs, stated rather than hidden.** The packing question is
the classic partition one and has no known quick answer, so a
contract-valid document nobody produced could take a long time. That
cost is accepted for the same reason plan P2-D2 accepts a document too
large for the machine failing on the memory-exhaustion path rather than
being refused by a cap: a bound that keeps the run short by writing a
number the description did not publish is the worse of the two, and it
is the exact shape of failure the section-9 head of the contract names
— "the published facts cannot all hold" must mean no assignment
satisfies them, PROVED, not that the search was stopped. What keeps
genuine descriptions quick is that their own values are an answer and
that the walk is handed only the relationships the description
publishes, so it is never asked to settle a cross-tabulation the real
column never fixed.

**The packing is COMPLETE, and that is the whole of what steps 3 and 4
owe.** Every count of both margins is met exactly whenever any
assignment of whole groups meets them all, on every description, and
the walk finds such an assignment whenever one exists. A description
for which none exists is one whose own published facts cannot all hold
at once — no profile a real table produced is one, because that table's
own values are such an assignment — and it is the section-9 shape of
the contract's head, proved rather than assumed. G12 states what a run
does there and what its report says; nothing in this section grants an
implementation a lesser outcome on a description an assignment exists
for.

5. **The lengths.** `length.min` and `length.max` are EXACT-OBSERVABLE
   and are pinned: one group takes `length.min` and one takes
   `length.max` — **the two the packing rule above settled on, not the
   description's first two** (P2-C4-F2). The remaining groups start at
   `base`, the published
   `length.p50` rounded to a whole number by the rule of G5.4 and
   clamped into `[min, max]`. Let `n = n_present`, and let `S` be the
   nearest whole number to the exact product `length.mean * n`, ties
   upward, computed on the exact rational value of the published
   binary64 rather than in floating point. The residual

   ```
   R = S - (sum over groups of occurrences * assigned length)
   ```

   is spent one character at a time: while `R > 0`, add one to the
   length of the group with the largest occurrence count that is below
   `max` (ties by group order), subtracting its occurrence count from
   `R`; while `R < 0`, subtract one from the group with the largest
   occurrence count that is above `min`, adding its occurrence count to
   `R`. Stop when `R` reaches zero, changes sign, or no group can move.
   `length.mean` and `length.p50` are APPROXIMATED; this is the fixed
   rule their bound is measured against.
6. **The words.** `words.min` and `words.max` are EXACT-OBSERVABLE and
   pinned onto the same two groups the lengths pinned — whichever two
   the packing rule settled on; `words.mean` is APPROXIMATED
   and is approached by the same residual walk. A group of length `L`
   can hold at most `(L + 1) // 2` words (each word at least one
   character, each separator one space). **A description whose
   `words.max` is more than `length.max` carries, or whose `words.min`
   is more than `length.min` carries, publishes facts that cannot all
   hold**, and G12 refuses generation for it before any cell is built
   rather than writing a twin and naming the miss (review item
   P2-C5-F4). Lengths and word counts are paired by ascending order —
   the longest cells take the most words.

   What is left for the ceiling above to bite is a group carrying
   NEITHER published extreme, whose count is the walk's own step toward
   the APPROXIMATED `words.mean` rather than a number the description
   publishes: that count comes down to what its own length carries, and
   the change is measured and named like any other. The two carrying
   groups are never brought down this way — their lengths are the two
   published ends, and a description in which those ends cannot hold
   their own published word counts never reaches this step.
7. **The text itself.** A group of length `L` and word count `w` is
   written as `w` words separated by single spaces, whose lengths differ
   by at most one and sum to `L - (w - 1)`, longer words first. Each
   word is the next spelling of the group's alphabet enumeration
   (G9.2) at that word's length, so the whole cell is distinct from
   every other group's cell.

### G9.6 Identifiers

`min_length`, `max_length`, `all_whole_numbers`, `n_all_digits` and
`n_code_alphabet` are EXACT-OBSERVABLE in every case, since owner
decision 6 keeps the length, and so are the four class counts
`n_numeric`, `n_out_of_range`, `n_contradictory` and `n_not_numeric`,
which P2-D6 makes exact by class-preserving construction on every role.
The construction is G9.5 steps 1, 3, 4, 5 and 7, with that section's
packing rule applying here IN FULL — both margins and the shape search
— and four changes:

- **the four class counts are packed WITH the two alphabet counts, in
  one allocation, and which two groups carry the published length ends
  is part of that same packing** (P2-C5-F2). Revision 2 said the bands
  came from the two published alphabet counts and from nothing else,
  and that the shape search of G9.5 could not reach here because no
  group's length was an input to it. Both halves were false in the
  direction that costs published counts. A group written from an
  alphabet reads back as whatever the contract's classifier makes of
  it, so packing the alphabets alone READS a published class count off
  a construction instead of meeting it: a declared column of `N_7`,
  `no!!`, `x-y`, `913` and `-3` publishes 23 cells that read as numbers
  and 26 that do not, its own five values are an exact assignment, and
  the twin wrote 12 and 37. And once the classes are packed a group's
  LENGTH is an input, because one character cannot be a number and
  stand outside the figures at the same time — so pinning an end onto a
  group chosen in advance can make a count unreachable that another
  pinning meets. A column of `-48562`, `14618`, `3`, `37e999`, `^slX`
  and `tA` publishes an exact assignment in its own values, and pinning
  the shortest published length onto its two-row group, whose value is
  six characters long and reads as a number outside the figures, puts
  that group where no exact assignment has it. The candidate shapes are
  offered in the fixed order of G9.5's own shape rule, so the
  description's own first two groups are tried first and a column the
  earlier rule already answered is answered the same way, byte for
  byte. **This search can be asked for MORE than its first answer**
  (G9.3 step 5, plan amendment A-P3-12), because a description can have
  several exact packings and the first can be one no fold collision can
  be built inside. The further answers are this same walk continued in
  this same order, and then this same walk again with ONE group held to
  ONE family — which is a narrowing of the permissions handed to the
  packer, never a change to the packer's own fill order, so the first
  answer stays the first answer and the rule four roles share is
  untouched;
- **each of the four class families is class-preserving by
  construction, and the walk CHECKS it.** A cell that reads as an
  ordinary number, one holding a well-formed number too large or too
  small to hold, and one whose notation conflicts with itself inside
  accounting parentheses are the constructions of G9.5 step 3 and
  G10.3; a cell of ordinary text is the band's own alphabet walk of
  G9.2, led by a character that holds the value inside its band. A
  candidate the contract's own classifier does not read back as its
  family's class is stepped over, so the class a cell is counted in is
  the class it was packed for. Revision 1 said that when
  `all_whole_numbers` is true every group is written from `DIGITS` and
  `n_all_digits` then equals `n_present`, "as the contract's own
  invariant requires". **The contract has no such invariant and the
  statement is false** (P2-C1-F1): a column of `+1` and `+2` publishes
  `all_whole_numbers: true` with `n_all_digits = 0` AND
  `n_code_alphabet = 0`, because `+` is in neither alphabet, and the
  shipped producer writes exactly that. The false implication is
  withdrawn;
- **which slots carry the fold collisions is settled after the packing,
  not before it** (P2-C5-F2). A partner carries its parent's family
  (G9.3), so a slot that owes a collision and whose class-and-alphabet
  family no earlier slot has can carry none at all. The collision slots
  are therefore chosen rather than taken: each in turn is the LAST group
  whose family can carry a collision — one whose spellings hold a
  character with a case, or any family at all where the published length
  range leaves room for edge spacing — and which still has another
  member among the groups not yet chosen, then the last group whose
  family merely has another member, and otherwise the last remaining
  group, which is the ascending occurrence order this rule replaces.
  Groups keep their relative order otherwise, so a column whose groups
  all share one family is laid out exactly as it was. Nothing published
  moves: the occurrence multiset pairs a size with a made-up value and
  never with a position, and every group keeps its own class, alphabet
  and size wherever it sits. The ask of G9.3 step 1 stays an ASK here as
  everywhere: a family whose spellings hold no character with a case —
  a notation inside accounting parentheses never does — gives the pass
  up after the ceiling G9.2 fixes, the walk is put back where that pass
  began, and the ordinary rule takes the value it would have taken
  anyway. **AND THE CHOICE IS CHECKED ONCE THE SPELLINGS EXIST** (G9.3
  step 5, plan amendment A-P3-12): whether a family can SUPPLY the
  collisions this choice asks it for depends on spellings that do not
  exist while the choice is being made, so a layout that could not
  build one is laid out again — the short family asked for no more than
  it was shown to supply, a slot carrying a published length end
  offered a collision before any other slot of its family, and where
  neither helps, the further exact packings of this section, including
  the ones its own search reaches by holding one group to one family.
  The choice above is offered FIRST and unchanged, so a description it
  answers is answered by it, byte for byte;
- **when `all_whole_numbers` is true, every band writes whole numbers.**
  In the figures band the first character is a non-zero digit, so the
  spelling's length is its digit count. In the code band the value is
  written `<digits>e0`, which reads back as a whole number and holds a
  character the figures do not. Outside the code alphabet it is written
  `<digits>.`, which reads back as a whole number and holds a character
  the code alphabet does not. **Where the published length range leaves
  a value that must stand outside the figures no whole-number spelling
  at ANY length — one character cannot be both a whole number and
  outside the figures — the facts cannot all hold and G12 refuses
  generation before any cell is built** (review item P2-C5-F4);
- no word statistics exist, so G9.5 step 6 does not apply and no space
  is ever written into an identifier.

**What the length ends and the bands cost, and how both were settled**
(review items P2-C5-F4 and P2-C5-F2; closed by Phase 3 plan P3-D8.1,
owner decision 1, 2026-08-12). A whole number standing outside the
figures needs two characters in the wide band and three in the code
band, so once `all_whole_numbers` is true a band's permitted LENGTHS
are part of the question. The first bullet above settles length and
band together, which closed the shape a length end pinned onto a group
whose band has no whole-number spelling at that one length used to
leave — a source of `1.`, `2e0` and `3` is its own proof that an answer
exists, and the packing finds it.

The other shape was a published longest length of two characters
carrying a value that must stand in the code alphabet. Its only
two-character whole numbers begin with a sign, which G9.1 keeps a
made-up value from beginning with, and the implementation wrote one
anyway — meeting the count by breaking the bar, and leaving the
report's formula paragraph telling the reader that an invented cell was
a value the description published.

**The owner settled it as a bounded carve-out, not a refusal** (owner
decision 9, 2026-08-13). A description carrying those counts PROVES the
real column held sign-leading values, since no other spelling of that
width exists, so the twin inherits a hazard the table already had
rather than manufacturing one — which is the distinction G9.1's bar was
written to draw. Refusing instead would deny a person a twin over a
character their own file used. The family is written where it is
needed, and the report's formula paragraph names those columns, says
the cells were invented, and says why.

**"Where it is needed" is decided by the packing and by nothing else.**
The class-and-alphabet search above runs first with the two-character
code family CLOSED, and reaches for it only when no assignment of whole
groups meets every published count without it — so a column with room
for three characters writes `1e0` and no sign at all.
`all_whole_numbers` stays EXACT-OBSERVABLE in every case this method
builds, and an invented record number opens with such a character only
where the published counts leave no other way to spell a value of that
width for its own group.

**The COUNT of such cells is not minimal, and this document said
otherwise until now** (Phase 3 plan P3-C7-F1 and its amendment A-P3-8
clause 4, 2026-08-14). A fold-collision PARTNER carries its parent's
spelling, and `_partner_of` searches only the family the packing
already gave the slot, so it cannot move a collision to a family where
it would cost nothing: the plan's measured column — `-3` twelve times,
`-34023` twice, `8e999` three times and `8E999` twice — writes fourteen
such cells where an allocation putting the collision on the
out-of-range pair would write two. Every published count is met either
way, so what is missing is a MINIMISATION rather than an obligation;
the plan records the three passes that designed it, measured it and did
not take it, and the generation report says the same thing to the
person holding the twin. An independent implementer is bound by the
counts, not by this shortfall: writing fewer such cells while meeting
every published count conforms.

In the infeasible corner of owner decision 6 the identifier repeats:
the groups are filled from the domain in order and, when it is
exhausted, the enumeration restarts, so the fewest necessary values
repeat. Three distinctness facts are then REPORT-ONLY, not one — raw
`n_distinct`, `n_distinct_folded` AND `n_distinct_by_occurrences` — and
the report names all three achieved values beside the published ones,
with the join and de-duplication consequence in the person's own words.

## G10. Absent cells, straggler stand-ins, unrepresentable values

### G10.1 Absent cells

Exactly `n_missing` cells per column, each written as the EMPTY text —
no space, no marker, no spelling of any kind — and placed by the
arrangement of G4.2. `missing_by_class` and `missing_by_source` are
REPORT-ONLY: the real table's absent-value spellings and classes are
named in the report and are not reproduced (R-P2-2). An empty cell
re-profiles as `(blank)`, which is what makes `n_present` and
`n_missing` EXACT-OBSERVABLE.

The one-column canonical quoting exception of G2 applies here.

### G10.2 The class partition

Every present cell of every role belongs to exactly one of four classes,
and the four counts are published on every role:

```
n_numeric + n_out_of_range + n_contradictory + n_not_numeric = n_present
```

They are EXACT-OBSERVABLE **by class-preserving construction**: each
class has its own construction below, each construction's output
classifies back into its own class through the shipped
`parsing.classify_number`, and a test asserts exactly that over every
constructed spelling.

### G10.3 The three straggler constructions

Distinctness inside a class is supplied by advancing `k` from 1; the
budget allocation of G6.5 says how many different spellings each class
may use, and a class that has spent its budget repeats its last
spelling.

- **Out of range (`n_out_of_range`).** A well-formed number too large or
  too small for binary64. Too large, spelling `k`: `1e999`, `2e999`,
  `3e999`, … (`ke999`, with `k` written in base ten). Too small,
  spelling `k`: `1e-999`, `2e-999`, …. A negative one carries a leading
  `-`. The published `n_negative_unrepresentable` says how many of these
  are negative; on the numeric roles the too-large/too-small split is
  not published for this class and every out-of-range cell is written
  too LARGE, which the report names.
- **Contradictory (`n_contradictory`).** A sign inside accounting
  parentheses, which is numeric notation whose meaning conflicts with
  itself: `(-1)`, `(-2)`, `(-3)`, … for spelling `k`. These carry
  neither sign nor whole-number status — the shipped parser answers
  "unknown" for both, and never guesses — so they can answer only for
  `n_sign_unknown` and `n_whole_unknown` wherever those are published.
  They are not the only class that can: a cell of ordinary text is left
  unsettled by the same parser in the same way, so the two together are
  what those counts are made of, and G10.5 step 1 states that tie for
  the one role that publishes them.
- **Ordinary text (`n_not_numeric`).** `text-1`, `text-2`, `text-3`, …
  for spelling `k`. Each is checked against the spellings that mean "no
  value" (`""`, `-`, `--`, `.`, `?`, `n/a`, `na`, `nan`, `none`,
  `null`, compared after trimming and case folding) and against every
  spelling already used in the column, and `k` is advanced on a
  collision. It parses as no number and as no date, so it stays in its
  own class.

**The interaction with the numeric-sentinel rule, stated rather than
left to chance.** The profiler reads `-9999`, `-999` and `9999` as
"no value" when they are also distribution outliers and cover at least
`sentinel_minimum_share` of the column. A twin cell that lands on one of
those numbers can therefore be read as missing when the twin is
re-profiled, exactly as the real column's own cells were. The method
does not steer values away from those three numbers — doing so would
distort a distribution to protect a re-profiling artifact — and the
report names `sentinel_verdicts` as REPORT-ONLY. This is a residual, not
a defect, and it is named as one in G13.

### G10.4 Unparsed datetime stand-ins

`n_unparsed` is EXACT-OBSERVABLE as counted neutral stand-ins,
explicitly outside the parsed-value obligation. The spellings are
`text-1`, `text-2`, … from the same construction as G10.3, checked
additionally against every date format the shipped `parsing.DATE_FORMATS`
names so that a stand-in cannot accidentally parse as a date and change
`n_unparsed`.

### G10.5 The `numeric_unrepresentable` role

The column publishes `n_whole`, `n_fraction`, `n_whole_unknown`,
`n_positive`, `n_negative`, `n_sign_unknown`, `n_out_of_range` and
`n_distinct_by_occurrences`, and publishes **no width and no magnitude
fact** (P2-D4, verified against the producer: two columns of overflowing
values, one about 400 characters wide and one about 4,000, publish
identically). Width fidelity is withdrawn; one canonical invented width
is used and disclosed (R-P2-1).

**The canonical width is 400 significant digits.** A 400-digit whole
number is far outside binary64's range, so it classifies as out of range
and as whole; a fraction written as `0.` followed by 399 zeros and one
non-zero digit is far below the smallest subnormal, so it classifies as
out of range and as a fraction. The width is invented, it is the same
for every such column, and the report says so in those words.

Construction, in this fixed order, so the counts land exactly:

1. **The cells a twin may write, and which published count each
   answers for.** A wide cell is written in one of six shapes: the
   contradictory construction of G10.3; a whole number too large for
   the format; a fraction too small for it; a whole number the format
   holds; a fraction the format holds; and ordinary text. The shipped
   parser's own answers tie those six to the published counts, and this
   tie is the whole of the relationship between them:

   | shape | counted by | whole-number status | sign |
   |---|---|---|---|
   | contradictory | `n_contradictory` | `n_whole_unknown` | `n_sign_unknown` |
   | too large | `n_out_of_range` | `n_whole` | `n_negative` or `n_positive` |
   | too small | `n_out_of_range` | `n_fraction` | `n_negative` or `n_positive` |
   | whole, in range | `n_numeric` | `n_whole` | `n_negative` or `n_positive` |
   | fraction, in range | `n_numeric` | `n_fraction` | `n_negative` or `n_positive` |
   | ordinary text | `n_not_numeric` | `n_whole_unknown` | `n_sign_unknown` |

   **A group whose cells carry no sign can answer only for
   `n_sign_unknown`, and only for `n_whole_unknown`**: notation that
   conflicts with itself and ordinary text are the shapes whose sign
   and whole-number status the shipped parser refuses to guess, and
   that rule is carried into the packing as a permission rather than
   left to chance.
2. **The three published families are THREE MARGINS over those cells,
   and no cross-tabulation of them is assumed** (P2-C3-F1). The
   description publishes how the cells divide by notation class (`X2`:
   `n_numeric`, `n_not_numeric`, `n_out_of_range`, `n_contradictory`),
   how they divide by whole-number status (`U1`: `n_whole`,
   `n_fraction`, `n_whole_unknown`) and how they divide by sign (`U2`:
   `n_negative`, `n_positive`, `n_sign_unknown`). It publishes NOTHING
   about how those three divisions cross. In particular **how
   `n_out_of_range` divides between whole numbers and fractions is not
   a published fact**, and an implementation that fixes it by a rule of
   its own — spending `n_whole` on the too-large cells first, say — has
   invented a description and may then find no packing where the real
   column had one.

   Revision 2 did exactly that and lost six exact counts on a genuine
   six-row column: four groups of 2, 2, 1 and 1 publishing
   `n_numeric = 2`, `n_out_of_range = 1`, `n_contradictory = 3`,
   `n_whole = 2`, `n_fraction = 1`, `n_whole_unknown = 3`,
   `n_negative = 3`, `n_positive = 0` and `n_sign_unknown = 3`. Sending
   the one out-of-range cell to `n_whole` asks for cell quotas no
   packing of those groups meets; sending it to `n_fraction` — equally
   consistent with every published count — is met exactly. The real
   table proves only that SOME cross-tabulation of the published counts
   exists, never which one, so the packing is stated over the three
   margins themselves and the walk chooses among every cross-tabulation
   they permit.
3. **The three margins are ONE packing, not three** (P2-C2-F1,
   P2-C3-F1). Which shape a group takes settles which sign counts and
   which whole-number counts it can answer for, so deciding them one
   after another throws away joint assignments that exist: round 2
   built a five-row column with groups of 1, 1, 1 and 2 whose joint
   class-and-sign assignment is exact and which two separate walks
   missed, writing two negative cells and none positive against one of
   each. All three are therefore packed together by the grid rule of
   G9.5, over the cells and permissions of step 1, with the notation
   counts, the whole-number counts and the sign counts as its three
   margins. Spending the negative count greedily and stopping at the
   first group too large to fit is not conforming — on three negative
   rows in one group beside two positive groups of two it writes two
   negatives (P2-C1-F1).
4. In-range cells are written as `1`, `-1`, `0.5`, `-0.5` and their
   distinct variants from the leading-zero family, since no ladder and
   no statistic is published for this role.
5. The repetition pattern is `n_distinct_by_occurrences`, exactly as in
   G9.5 step 1; the capacity rule and its refusal (G9.4) apply, with the
   digit alphabet over the canonical width.
6. **Every one of `n_whole`, `n_fraction`, `n_whole_unknown`,
   `n_positive`, `n_negative` and `n_sign_unknown` is recounted from the
   finished cells** and named in the report where it was missed, under
   its own field name, with the achieved value beside the published one.
   The recount asks the shipped parser the same three questions the
   profiler asks of a real cell — what the notation classifies as, what
   sign it settles, and whether it is a whole number — and, like the
   profiler, it leaves a cell that reads as ordinary text out of the
   sign and whole tallies altogether. Where the three margins have no
   joint answer at all — which no description a real table produced can
   reach, because that table's own values are such an answer — G9.5's
   fallback rule applies: each published family is packed after the one
   before it, and this recount is what turns whatever it missed into a
   NAMED deviation the report renders. The four notation counts are
   recounted the same way on every role (G10.2). A miss on this path is
   never silent, and a miss the search could have avoided is a defect
   rather than a deviation.

## G11. The all-different obligation

**The rule, once:** whenever a column publishes
`n_distinct == n_present`, its present values are ALL DIFFERENT in the
twin, on every role, in that column's own notion of equality — because
an undeclared key column arrives as free text or as a numeric role, not
as an identifier (P1-D4 item 8; P2-R5-F3).

The obligation can bind only on facts the profile actually publishes,
and stating it that way is what stops a fourth instance arriving
undetected. Where the raw distinctness of a column was produced by
something the disclosure rules WITHHELD, the twin cannot reproduce it
without making up unpublished facts; raw distinctness is REPORT-ONLY
there, and the report names the achieved count beside the published one.

How each role meets it:

| role | notion of equality | mechanism |
|---|---|---|
| `count`, `continuous` | the raw spelling | G6.5: `M = K` different values, and the leading-zero family for any spelling budget above that |
| `datetime` | the raw spelling | G7.3 with `P` ranks, plus the published offsets of G7.4 |
| `constant`, `binary`, `categorical` | the raw spelling | G8.1: the published variants |
| `identifier`, `free_text`, `numeric_unrepresentable` | the raw spelling | G9.2: one enumeration element per group |

**The three known instances where it cannot hold**, each of which is
tested:

1. **Declared identifiers** whose published length range cannot supply
   as many distinct values as the column has rows. Owner decision 6:
   length wins, values repeat, and three distinctness facts become
   REPORT-ONLY (G9.6).
2. **Label columns whose values differ only before the fold**, beneath
   the small-cell floor. Owner decisions 9 and 11 publish the variants,
   so the obligation now HOLDS wherever the variants are visible and
   falls back only beneath the floor, where `variants_withheld` says how
   many spellings to invent but not what they were; the invented
   variants of G8.2 are distinct, so the obligation is met in form, and
   the report names that the spellings themselves are invented.
3. **Datetime columns whose offsets are withheld.** A 30-row column of
   ten rare offsets over 15 dates publishes
   `n_present = n_distinct = 30` while `utc_offsets` collapses to
   `{"(withheld)": 30}`: the obligation fires, but the profile never
   says which offsets made those 30 spellings distinct, so the twin
   holds only 15 instants and no published way to spell them apart
   (G7.4). Raw distinctness is REPORT-ONLY for that column. Where the
   same column's offsets ARE published, the obligation holds and the
   twin uses them.

A fourth instance is a change to this document, not an exception granted
during implementation.

## G12. Feasibility, refusals, and named deviations

The generation-feasibility stage runs after the loader and before any
generation, and every outcome is fixed (P2-D6):

1. **Domains are widened first** — G9.1's alphabets include upper and
   lower case and the full printable ASCII range, and G9.3's partner
   family adds edge spacing to the case flips, so a fold collision can
   be placed on a value with no case at all.
2. **Identifier length versus distinctness**: owner decision 6 (G9.4,
   G9.6).
3. **Numeric raw distinctness**: owner decisions 7, 8 and 10 (G6.5).
4. **Published counts take precedence over ladder conformance** where a
   numeric conflict is otherwise resolvable (G5.5); the residual
   deviation is measured and named.
5. **Refusal is reserved for documents no rule above can satisfy.** This
   method has exactly four, each of them a refusal of GENERATION rather
   than a claim that the description is invalid, and each says the
   profile is VALID, names the two facts that cannot both hold, and
   gives remediation that does not assume the person still holds the
   table:
   - `generation-domain-too-small` (G9.4) — a free-text or
     unrepresentable column whose published multiplicity map needs more
     different values than its published length range can spell;
   - `generation-counts-contradict` — a numeric column whose
     `n_zero` and `n_negative` together exceed `n_numeric` (`P < 0` in
     G5.1), which no ordering of values can satisfy;
   - `generation-words-exceed-length` (G9.5 step 6, review item
     P2-C5-F4) — a free-text column whose `words.max` is more than its
     `length.max` can hold, or whose `words.min` is more than its
     `length.min` can hold, given that a value of `L` characters holds
     at most `(L + 1) // 2` words;
   - `generation-whole-numbers-need-room` (G9.6, review item P2-C5-F4)
     — a declared identifier published as whole numbers whose length
     range leaves a value that must stand outside the figures no
     whole-number spelling at any length: one character that reads as a
     whole number IS a figure, so a longest length of one character
     with `n_all_digits` below `n_present`, and a shortest length of one
     character with `n_all_digits` of zero, are both descriptions no
     table can hold;
   A FIFTH REFUSAL WAS ADDED HERE ON 2026-08-12 AND WITHDRAWN ON
   2026-08-13, both by amendment, and the round trip is recorded rather
   than erased. `generation-whole-numbers-need-code-room` stopped a
   declared identifier published as whole numbers whose values must
   stand in the code alphabet with no room for a third character. The
   owner withdrew it under decision 9: a description carrying those
   counts proves the real column held sign-leading values, so refusing
   denied a person a twin over a character their own file used. G9.1's
   bar carries the bounded carve-out instead, and the report counts and
   names the cells.

   The last two were written as twins with the exact fact named as
   missed until review item P2-C5-F4; the ratified plan reserves the
   report line for facts a rule CAN meet, and a person who receives a
   twin where the plan says the run stops has no signal that anything
   was wrong. A fifth refusal is a change to this document, not an
   exception granted during implementation.

Every deviation this document permits is **measured against the
published fact and named in the report, every run**, with the achieved
value beside the published one. The complete list, so that a reviewer
can check the report against it: a raised distinct count (G5.2); an
endpoint moved by a sign repair (G5.5); a `leading_plus` quota larger
than the column's own count of non-negative cells, and a point-free
demand larger than `K` minus the cells the published ends force to
carry a point — the only two shapes G6.4 leaves, both narrower than
the entry this replaces, which named any unplaceable point-free quota
before G5.2's carrier step existed (G6.4, P2-C4-F3); a folded count
that could not fall below its raw count
(G6.5); a
datetime reading that fell from `utc` to `local` because every offset
was withheld (G7.4); the invented spellings behind withheld label
variants (G8.2) and withheld levels (G8.3); identifier duplicates and
the three distinctness facts they cost (G9.6); a word count brought down
to what its own length carries on a group carrying NEITHER published
word extreme, the two carrying groups being settled by a refusal instead
(G9.5 step 6, P2-C5-F4); the invented canonical width of an unrepresentable column
(G10.5); and the out-of-range cells all written too large (G10.3).

**What this list does not hold, and why the absence is the point.** No
end of a column of dates appears in it. The contract's D10 and D11
settle every description on which one could not be written, so a
generator has an exact answer for the two ends of every column it is
handed; a run that finds otherwise has found a defect in itself, prints
it in the same shape as the entries above, and is not conforming while
it does. A list is the place a lowered obligation hides — four repairs
put one here or in a paragraph like it (contract 13.16) — so a fact
leaving this list is a fact whose bar went back up, and one arriving
needs the ratified plan to name it first.

**And, on every column, every published count the packing rule of G9.5
could not meet.** These are not predicted by a rule; they are RECOUNTED
from the finished cells, which is what lets them catch a shortfall no
rule of this document foresaw (P2-C1-F1). Each is named under the
contract's own field name, never under a name the implementation
invented for it:

- the four class counts `n_numeric`, `n_out_of_range`,
  `n_contradictory` and `n_not_numeric`, on every role (G10.2);
- `n_all_digits` and `n_code_alphabet` on the two roles that publish
  them, and `all_whole_numbers` on a declared identifier (G9.5, G9.6);
- `length.min`, `length.max`, `words.min` and `words.max` on a column of
  free text (G9.5 steps 5 and 6). **These four were pinned and never
  recounted, and one of them was lost in silence** (P2-C4-F2): a group
  pinned to the published largest word count and then given a class
  that writes one unbroken run of characters wrote one word, no rule
  predicted it, and no line of the report said so. A construction that
  believes a fact is exactly the construction that stops measuring it,
  so all four are measured from the finished cells like every count
  above them;
- `n_whole`, `n_fraction`, `n_whole_unknown`, `n_positive`,
  `n_negative` and `n_sign_unknown` on an unrepresentable column
  (G10.5);
- `n_distinct` and `n_distinct_folded` on every column.

### G12.1 What an APPROXIMATED fact owes

The profile contract gives every published field exactly one
disposition, and APPROXIMATED means: reproduced under a stated rule
inside a two-sided finite-sample bound, MEASURED from the written CSV,
checked against BOTH ends of that bound, and named in the generation
report with the achieved value beside the published one
(`docs/spec/profile-contract-v4.md` section 2.2). This subsection and
the six after it fix that rule and both ends for every field the
contract's matrix marks APPROXIMATED. The complete list, by role:

| role | field | where its bound is fixed |
|---|---|---|
| `count`, `continuous` | the nine interior rungs of `percentiles` | G5.6, restated as G12.2 |
| `count`, `continuous` | `mean`, `std`, `skew` | G12.3 |
| `datetime` | the nine interior rungs of `date_percentiles` | G12.4 |
| `datetime` | `n_distinct`, `n_distinct_folded` | G12.5 |
| `free_text` | `length.mean`, `length.p50`, `words.mean` | G12.6 |
| `constant`, `binary`, `categorical` | `n_distinct` in its fallback | G12.7 |
| `count`, `continuous` | `n_distinct`, `n_distinct_folded` in their fallback | G12.8 |

Nothing else is approximated. Every other published field is
EXACT-OBSERVABLE, EXACT-CONTROL, REPORT-ONLY, LOADER-ONLY or
STRUCTURAL, and a field measured under two dispositions would be a
field with two answers.

Four rules hold for all of them.

1. **Measured, never predicted.** The achieved value is recomputed from
   the FINISHED cells — the same characters the twin file carries —
   using the profiler's own formula for that field, so that the two
   numbers the report prints side by side are the same statistic
   computed the same way. A value the generator held in memory on the
   way to the file is not the measurement.
2. **Both ends are checked, and both are finite.** A bound with one end
   is not a bound: a twin can leave a one-sided window in the direction
   nobody looked. Where a derivation below would leave an end at
   infinity, the subsection names the finite value that replaces it and
   why that value is a true bound.
3. **Every one is named in the report, every run**, with the published
   value, the achieved value, both ends of the bound and whether the
   achieved value landed between them — whatever the answer is. A fact
   whose bound was checked but not printed is a fact the reader has to
   take on trust, and this document treats an unshown check as a check
   that was not made.
4. **A measurement outside its bound is ALSO a named deviation.** The
   bound is a statement this method makes about its own construction,
   so a twin that leaves it did not hold what the description asks for,
   and it belongs in the deviation list of G12 beside every other fact
   the twin could not meet.

**A bound here is a statement about the CONSTRUCTION**, derived from the
rule that builds the cells, never a tolerance measured on an output and
rounded up. That is what makes each one able to FAIL: a generator that
ignored the published ladder, collapsed the interior rungs, wrote
values at the wrong precision, or made up its own lengths leaves these
windows on an ordinary column. A bound no wrong twin can leave is not a
check.

### G12.2 The bound on the nine interior numeric rungs

G5.6 states it, and it is not restated here. Its two forms are used
below: the rung form, over the nine published interior rungs, and the
rank form, over every sorted position of the twin's own numeric cells.
Both use the same displacement `d = (g_max + 2) / K`, where `K` is the
number of cells the twin writes that read back as a number and `g_max`
is the largest stratum of G5.2.

**The half unit, and the two rules that can spend it.** On a column
publishing `integer_valued: true` both ends widen by one half unit, and
by nothing else, because G5.4 rounds each value to a whole number
exactly once. On a column publishing `integer_valued: false` whose
`numeric_styles` map holds a count for `plain`, `leading_zero` or
`leading_plus`, the values step of G6.4 may take a stratum to the
nearest whole number so that the published form can be written at all
(P2-C2-F2), which is the same half unit and no more; both ends widen by
it there too. A column publishing none of those three counts keeps the
tighter window, so the widening is granted to exactly the columns whose
own map can spend it and to no others.

**And the step that spends nothing.** Where that whole number is
another stratum's already, G6.4 takes one inside the stratum's own
share of the ladder instead (P2-C4-F3). That move is not an extra
allowance and no term is added for it: `d` already carries the whole
width of the stratum covering a rank, which is the argument G5.6 makes
in full, so a value anywhere inside that share is inside the window
before the half unit is added. The half unit above remains the only
widening this document grants.

### G12.3 The bounds on `mean`, `std` and `skew`

Let `V` be the twin's own numeric cells, sorted, read back through
`parsing.parse_number`; `K = len(V)`; `p_k = k / (K - 1)`; and, with
`Ladder` and `d` as in G5.6 and `h` the half unit of G12.2,

```
A[k] = Ladder(max(0, p_k - d)) - h        (the lowest value rank k can hold)
B[k] = Ladder(min(1, p_k + d)) + h        (the highest)
R[k] = Ladder(p_k)                        (the ladder's own value there)
e[k] = max(R[k] - A[k], B[k] - R[k])
E    = sqrt( (1 / K) * sum over k of e[k] * e[k] )
```

`A[k] <= V[k] <= B[k]` is G5.6's rank form, and `A[k] <= R[k] <= B[k]`
because `Ladder` never decreases; so `|V[k] - R[k]| <= e[k]` for every
rank, and `E` is the largest root-mean-square displacement the
construction can produce.

The three formulas are the profiler's own (`taxonomy._moments`): the
arithmetic mean; the SAMPLE standard deviation, divided by `K - 1`; and
the moment skewness, the average cubed deviation over the cube of the
POPULATION standard deviation. `std` is undefined for `K < 2` and
`skew` for `K < 3` or a column whose values are all identical, matching
the contract's Q4 and Q5; where the published field is null the twin
owes nothing and the fact is not measured.

**`mean`.** The mean rises with every value, so its two ends are the
mean of the two windows:

```
(1/K) * sum A[k]   <=   mean(V)   <=   (1/K) * sum B[k]
```

**`std`.** The sample standard deviation is
`||V - mean(V)|| / sqrt(K - 1)` for the ordinary Euclidean length,
which is a seminorm of `V`, so it moves by at most the length of the
displacement:

```
| std(V) - std(R) |  <=  ||V - R|| / sqrt(K - 1)  <=  E * sqrt(K / (K - 1))
```

giving `max(0, std(R) - E*sqrt(K/(K-1)))  <=  std(V)  <=  std(R) +
E*sqrt(K/(K-1))`, where `std(R)` is the same statistic of the ladder's
own values `R`.

**`skew`.** The skewness is a ratio, so each part is bounded and the
two are divided. With `meanA = (1/K) sum A[k]` and
`meanB = (1/K) sum B[k]`, every deviation `V[k] - mean(V)` lies between
`A[k] - meanB` and `B[k] - meanA`; cubing keeps that order, so the
average cubed deviation lies between `(1/K) sum (A[k] - meanB)^3` and
`(1/K) sum (B[k] - meanA)^3`. The population standard deviation obeys
the same seminorm argument as `std`, so it lies between
`max(0, s(R) - E)` and `s(R) + E`, and the denominator lies between the
cubes of those two. The skewness lies in the quotient of the two
intervals, taken with the sign rule division needs: a negative
numerator end is divided by the SMALLEST denominator and a positive one
by the largest, and the reverse for the upper end.

**The one column with no bound at all.** A description whose ladder is
null at EVERY rung publishes no shape for the values to take: G5.3 puts
them on the sign counts alone, and there is no `Ladder` for any of the
three bounds above to be drawn from. Such a column's moments are not
measured and not bounded, and the empty ladder is named in the report as
a deviation on every run — which tells a reader more than a bound would,
because it says the column's values follow no published shape at all. A
rung that is null while OTHER rungs hold numbers is a different case:
contract rule L3 admits one, G5.1 fixes exactly which number fills it,
and the filled ladder bounds it like any other.

**And the finite fallback.** Where `s(R) <= E` the denominator's lower
end is zero and that quotient has no finite upper end. It is replaced
by the range every sample of `K` values lies in whatever its values
are:

```
-(K - 2) / sqrt(K - 1)   <=   skew   <=   +(K - 2) / sqrt(K - 1)
```

The published bound is the INTERSECTION of the quotient with that
range, so it is finite on both sides for every column, and it narrows
to the quotient exactly when the ladder's own spread exceeds the
displacement — which is the ordinary case for a column whose ladder
describes it at all. A column whose published ladder is so coarse that
`E` reaches its own spread is told so by a wide bound rather than by a
bound that cannot be printed.

### G12.4 The bound on the nine interior datetime rungs

Let `P = n_present - n_unparsed` be the number of twin cells that read
back as a date, and `Ladder_d` the published `date_percentiles` read in
the ordinal space of G7.1 by the same whole-number interpolation G7.3
builds cells with. Rank `k` of G7.3 draws its share inside
`[k / P, (k + 1) / P)` and no word can take it outside that band, and
ranks `0` and `P - 1` are pinned to the published `earliest` and
`latest`, which the profile contract's D11 also makes the ladder's own
two ends. So for the twin's own ordinals `O`, sorted:

```
O[0] == earliest,   O[P-1] == latest,   and for every rank between them
Ladder_d(k / P) - u   <=   O[k]   <=   Ladder_d((k + 1) / P)
```

where `u` is what reading a written cell back can lose: one unit for
the downward rounding of the whole-number interpolation itself, plus
59 seconds where `resolution == "datetime"` and
`time_precision == "minute"`, because such a cell carries no seconds.
A date, a quarter, a second and a subsecond cell each carry their own
unit exactly and lose nothing further.

The achieved rung at percent `c` is the profiler's own selection rule
(`taxonomy._ordinal_rung`): the ordinal at sorted position
`k = floor((P - 1) * c / 100)`, SELECTED and not interpolated, because
there is no half-way point between two dates a calendar recognises. Its
two ends are that rank's own two ends above.

### G12.5 The envelope on datetime `n_distinct` and `n_distinct_folded`

**The lower end.** Two ranks whose windows of G12.4 do not overlap
cannot hold the same instant. Let `F` be the largest number of ranks
whose windows are pairwise separate — taken in one walk, since the
windows arrive in non-decreasing order of both ends: keep the first
rank, then keep each later rank whose lower end is strictly above the
last kept rank's upper end. Every cell that did not read as a date is a
counted stand-in spelled differently from every other cell of the
column (G10.4). So

```
F + n_unparsed   <=   n_distinct(twin)
```

**The upper end.** Every cell that reads as a date carries an instant
between the published `earliest` and `latest`, written at the published
precision, spelled with one of the offsets `utc_offsets` names by name
(G7.4). With `W` the number of instants that range holds at that
precision and `M` the number of named offsets — or 1 where none is
named — and `n_present` cells in the column at all:

```
n_distinct(twin)   <=   min(n_present, W * M + n_unparsed)
```

Folding a date cell changes no two of them onto one, so both ends bound
`n_distinct_folded` as well. The lower end is brought down to the upper
where a description's own facts put them the wrong way round.

**This envelope need not contain the published count, and often does
not.** A column of 240 rows over 84 different dates publishes
`n_distinct = 84`, while the method above writes a value per rank and
holds far more; the envelope says what the CONSTRUCTION guarantees, and
the published count is printed beside it. Where the two disagree, the
recount of G12 names `n_distinct` as a deviation, so the reader is told
both that the published count was missed and how many different values
the twin does hold. Making the twin's cardinality exact is not in this
phase's method; saying so plainly, every run, is.

### G12.6 The bounds on `length.mean`, `length.p50` and `words.mean`

Let `G[0], G[1], ...` be the group sizes of G9.5 step 1, `g_max` the
largest of them, and `N = n_present`. Write `lo` and `hi` for the two
groups the packing rule of G9.5 settled the published ends onto — **the
run's own pair, not group 0 and group 1** (P2-C4-F2), which for a
description the first pair already answers are the same two. G9.5
step 5 pins `G[lo]` to the smallest published value and `G[hi]` to the
largest, leaves every other group free between the two, and walks the
free groups toward the whole target `T = round(a * N)` for the
published average `a`, one character at a time, largest group first,
stopping as soon as the residual changes sign. So it overshoots by less
than the largest group it moved, and the total the column can reach at
all lies between

```
Floor = G[lo]*smallest + G[hi]*largest + (N - G[lo] - G[hi]) * smallest
Ceil  = G[lo]*smallest + G[hi]*largest + (N - G[lo] - G[hi]) * largest
```

Write `clamp(x)` for `x` brought inside `[Floor, Ceil]`.

**`length.mean`.** Nothing clamps a length after the walk, so the twin's
total written length `S` satisfies
`clamp(T - g_max) <= S <= clamp(T + g_max)`, with `Floor` and `Ceil`
formed from `length.min` and `length.max`, and the achieved average is
`S / N`.

**`words.mean`.** The same walk, and then the clamp of G9.5 step 6: a
value of `L` characters holds at most `(L + 1) // 2` words, since every
word needs a character and every gap between two words needs one too.
With `c[i] = max(1, (L[i] + 1) // 2)` over the twin's OWN written
cells, `w_lo = max(words.min, 1)`, `w_hi = max(words.max, 1)`,
`Floor` and `Ceil` formed from those two, and
`Allow = sum over cells of max(0, w_hi - c[i])`:

```
max( sum max(1, min(w_lo, c[i])),  clamp(T - g_max) - Allow )
    <=   S_words   <=
min( sum max(1, min(w_hi, c[i])),  clamp(T + g_max) )
```

The clamp can only REMOVE words, never add them, which is why it widens
the lower end by exactly `Allow` and leaves the upper end alone. Where
the two ends cross — a description whose own facts cannot both hold —
the lower end is brought down to the upper.

**`length.p50`.** Every free group starts at
`start = clamp(round(length.p50), length.min, length.max)` and the walk
moves it in ONE direction only. Its total movement is at most
`M = |T - Built| + g_max`, where
`Built = G[lo]*length.min + G[hi]*length.max + (N - G[lo] - G[hi]) * start`
is the total before the walk; and a group that moved `t` characters
spent `t` of that movement for every row it covers, so at most
`M / floor(N / 2)` characters of movement can reach the middle of the
column. With `W = ceil(M / max(1, floor(N / 2)))`:

```
start - (W where T < Built, else 0)  <=  p50(twin)  <=  start + (W where T > Built, else 0)
```

with two exceptions for the two end-carrying groups, each of which
holds the middle itself when it covers half the column: where
`2*G[lo] >= N` the lower end is `length.min`, and where `2*G[hi] >= N`
the upper end is `length.max`. Both ends are then brought inside
`[length.min, length.max]`, which every written length obeys because
those two facts are EXACT-OBSERVABLE. The achieved value is the
profiler's own `p50` — the interpolated quantile of `taxonomy._quantile`
— over the twin's own written lengths.

**These three bounds are the WALK's reach and are widened by nothing
else** (P2-C4-F2). Where no pair of end-carriers packs every published
count at the walk's own lengths, G9.5's packing rule reaches its wider
reading and lengthens a free group so that an exact count can be met —
an exact count outranks an approximated average, and that precedence is
stated there. A lengthened group can put the achieved middle length, or
the achieved average, outside the ends computed above. **The bound is
not widened to swallow that.** The measurement is made against these
ends every run, the miss is reported as an approximated fact the twin
did not hold, and G12.1's rule that a measurement outside its own bound
is also named among the facts the twin could not meet applies unchanged.
A bound that stretched to cover whatever the construction did would
report a pass that means nothing.

### G12.7 The envelope on label `n_distinct`

G8 writes exactly one spelling for each published variant, one for each
variant the floor held back, one for each level whose variants do not
cover its own count, and one for each level held back whole. Call that
number `S`: it is fixed by the description alone, before any cell is
written. Then

```
min(S, n_distinct)   <=   n_distinct(twin)   <=   max(S, n_distinct)
```

Where `S == n_distinct` the two ends coincide, the bound is a single
number and the fact is exact — which is the ordinary case, and what the
contract means by EXACT-OBSERVABLE "where the published variants and
the withheld-variant map supply enough spellings" (contract 9.5). The
envelope is the fallback the same line names. G8.2's supply has no end
— case flips first, then trailing spaces — so a conforming generator
that reaches this fallback at all has been handed a description whose
own counts disagree, and the report prints both numbers.

### G12.8 The fallback on numeric `n_distinct` and `n_distinct_folded`

For `count` and `continuous` both counts are EXACT-OBSERVABLE using the
spellings owner decisions 7, 8 and 10 permit (G6.5), and the contract
sends them to the two-sided envelope only where even those cannot
supply the count. That corner is real: the whole-number rule of G5.4
can round two neighbouring strata onto one value, and where the
published map writes those cells `plain` — the one style with no
leading-zero family (G6.3) — no spelling rule brings the second
identity back.

**Both ends are measured and printed on every run** (P2-C2-F4).
Revision 1 wrote the lower end as "the count the finished cells hold",
which is the achieved value itself: an envelope no twin can leave, and
a fact whose range the report never printed at all. It is replaced by
the column's own SUPPLY — how many different spellings the finished
cells are capable of carrying, which is a statement about the
construction and not a second reading of the output:

```
supply = for each (value, style) group of the numbers class:
             1                      where the style is `plain`
             the group's cell count otherwise, since every other style
                                    carries the leading-zero family
       + for each other class:
             min(its cell count, its share of the budget in G6.5)

min(supply, n_distinct)  <=  n_distinct(twin)  <=  max(supply, n_distinct)
```

and the same over the folded identities for `n_distinct_folded`. Where
`supply` reaches the published count the two ends meet on it, the bound
is a single number and the fact is exact — the ordinary case, and what
the contract's EXACT-OBSERVABLE means here. Where it does not, the
printed range says how far the count could fall, and the report names
the published count beside the achieved one under the recount of G12 as
well. The bound is able to fail: a twin that wrote one spelling where
its own cells could have carried two lands outside it.

## G13. Residuals this method carries

- **R-P2-1** — unrepresentable values have no published width; one
  canonical width (400 digits) is invented and disclosed.
- **R-P2-2** — absent-value spellings and classes are not reproduced.
- **R-P2-7** — the twin keeps a datetime column's precision and offset
  state but not the source's lexical date family; a month-first table
  yields ISO twin dates, and `format` is REPORT-ONLY for that reason.
- **R-P2-9** — twin numeric cells may carry several spellings of one
  value from the leading-zero family, so a twin column can look less
  tidy than a table whose numbers were written one way. The inferred
  column type is preserved, which the decimal-point form of decision 7
  would not have done.
- **R-P2-13 (new here)** — a generated numeric value can land on one of
  the three numbers the profiler treats as stand-ins for "no value"
  (`-9999`, `-999`, `9999`) and be read as missing when the twin is
  re-profiled, exactly as the real column's own cells were. The method
  does not steer values away from them, because distorting a
  distribution to protect a re-profiling artifact is the worse trade.
  `sentinel_verdicts` is REPORT-ONLY and the report names the column.
- **R-P2-14 (new here, review item P2-C3-F1)** — the packing of G9.5
  runs to its own end and nothing stops it early, so a contract-valid
  document nobody produced could take a long time to generate. This is
  a cost in TIME and never in exactness: no published count is traded
  to make the walk stop, which is what the withdrawn work ceiling did
  on a description the producer emits. It is the same trade plan P2-D2
  made when it refused a size cap on the description, and it is
  recorded here rather than paid for silently.

## G14. The frozen reference vectors

### G14.1 What the oracle is, and what it may not import

The vectors are computed by a tool under `tools/reference/`, importing
nothing from `src/` — the same rule the Phase 1 numeric vectors follow,
for the same reason: a value recomputed beside the code it checks can
drift with it.

**The oracle computes twin values as a pure function of GIVEN uint64
words.** The words are inputs of the vector file, written out in the
file itself, not drawn by the oracle. The oracle therefore contains no
generator, no seed handling and no library random operation of any kind.

**The oracle may not import numpy**, and the reason is mechanical rather
than stylistic: the data-provenance guard runs every fixture generator
under an audit hook that refuses `ctypes` — and numpy imports `ctypes`,
so a generator that imported numpy would be stopped by the guard before
it wrote a byte. This is stated here because it is the constraint that
shapes the whole vector design: the transform from words to bytes is
what the vectors freeze, and the word stream itself is bound separately
by a golden twin hash computed in CI against the locked numpy.

Exact quantities are computed in integer or rational arithmetic
(`fractions.Fraction` and Python integers), and each published binary64
is proved correctly rounded by midpoint comparison against its two
neighbours, ties to the even significand — the proof shape the Phase 1
vector tool already uses, including its two hand-checked boundaries (the
point where binary64 rounds to an infinity, and the sign of a zero). The
tool walks the exact serialized tree it writes, tuples included
(P1-R8-F3's blind spot), and carries a full-generator mutant that must
fail.

### G14.2 The vector file shape

**Two committed JSON files, and ONE oracle** (review item P2-C3-F3).
`tests/reference/generation-reference-vectors.json` carries the nine
cases G14.3 names first and
`tests/reference/generation-branch-vectors.json` carries the six it
names after them (five, until owner decision 11 added the
pooled-spelling case). Both are written by
`tools/reference/make_generation_reference_vectors.py` — the second
through the entry point `tools/reference/make_generation_branch_vectors.py`,
which runs that oracle and asks it for the second case set — so there is
one transform, one proof layer and one set of rules behind both files.
Each is registered in `tools/provenance/fixture-manifest.json` with its
`seed` (`0`, accepted and ignored — these vectors are a fixed transform,
not a random sample), its `sha256`, and a justification, and each is
rebuilt and byte-compared in CI.

**Why two files rather than one.** Each file must stay under the
manifest's 100000-byte fixture limit, and the two case sets together
carry about 123000 bytes. Splitting them is the one thing that must NOT
be done by dropping a case or shortening a proof: the limit is a rule
about a committed file, and the case list of G14.3 is a rule about
coverage. A third file follows the same rule the moment the second
approaches the limit. Two copies of the oracle would not, and are
forbidden here: a proof layer that exists twice can be repaired once.

Serialization: `json.dumps(document, indent=2, sort_keys=True,
allow_nan=False)` plus a terminal newline — the same canonical form the
Phase 1 vectors use, so a reviewer reads one shape and not two.

```
{
  "what":          one sentence naming this as the generation oracle
  "generated_by":  "tools/reference/make_generation_reference_vectors.py"
  "case_set":      which of the two case sets this file carries, and where
                   the other one lives, so neither file can be read as the
                   whole of the oracle
  "never_imports": ["synthtwin", "numpy", "pandas"]
  "method":        "docs/spec/generation-method-v1.md"
  "method_revision": 1
  "word_source":   a sentence saying the words below are INPUTS, that the
                   oracle draws nothing, and that the word stream itself
                   is bound by the golden twin hash and not by this file
  "definitions":   one entry per named transform of this document, each
                   stating the rule and the section that fixes it:
                     bounded, permutation, stratum_layout, ladder_segment,
                     convex_interpolation, integer_rule, class_repair,
                     canonical_spelling, style_allocation,
                     ordinal_transform, precision_form, endpoint_fields,
                     offset_form, grid_packing, partner_family,
                     notation_reading
  "cases": {
     "<case name>": {
        "why":            what this case exists to pin
        "column":         the published facts the case supplies, key by
                          key, in the profile's own wire shape
        "words":          the uint64 words the case is given, as decimal
                          strings, in consumption order
        "word_budget":    {"content": n, "placement": m} — the counts
                          this document's G4.3 predicts, so a mismatch is
                          a failure rather than a silent re-alignment
        "content":        the content list before placement, as exact
                          cell text
        "cells":          the written column, as exact cell text, in row
                          order after placement
        "csv_bytes":      the exact bytes of the column's own field of
                          each row, as a JSON string with the LF endings
                          written out
        "float64":        for every interior numeric value: the exact
                          rational it stands for, its correctly rounded
                          binary64, and the proof shape used
     }
  }
}
```

Every number in the file is either inside a `float64` wrapper carrying
its exact value, or a whole number at a path the tool's own list of
whole-number fields names. A number reaching the document with no exact
value recorded beside it stops the run, so "every published float is
proved" cannot quietly stop being true when a field is added.

### G14.3 The required cases

The four the plan names (P2-D7), five more this method's own mechanisms
need, five more for the branches those nine leave unexercised (four at
review item P2-C4-C3 and one at owner decision 11, review
item P2-C3-F3), and one more for the published end the ordinal space
cannot hold (review item P2-C4-C3), and the pooled remainder written by
its own value beside a whole number wider than the fixed-point window
(owner decision 11). **All fifteen are required.** The
first nine are the first committed file and the last five the second
(G14.2):

| case | pins |
|---|---|
| `date_only` | G7.5's date form; endpoints exact; ordinal floor rounding |
| `quarter` | G7.5's quarter form; the quarter ordinal |
| `offset_bearing` | G7.4's allocation, the `utc` clock conversion, and `earliest_utc_offset`/`latest_utc_offset` |
| `mixed_parsed_unparsed` | G10.4's stand-ins beside parsed cells, and `n_unparsed` |
| `numeric_integer` | G5.3 with `integer_valued: true`, the tie-toward-`+inf` rounding, and both endpoint pins |
| `numeric_decimal_styles` | G6.2's canonical boundaries (`1e+16`, `1e-05`, `.0`), G6.4's largest-remaining allocation, and a fold-collision pair |
| `label_variants` | G8.1's variant allocation, G8.2's case flips and trailing spaces, G8.3's withheld levels |
| `identifier_fold_collisions` | G9.3 with `n_distinct_folded < n_distinct`, and G9.2's length pins |
| `identifier_whole_numbers` | G9.6 with `all_whole_numbers: true` reaching all three bands, and the whole-group alphabet packing |
| `unrepresentable_joint` | G10.5's three margins packed together, on the six-row column of its step 2 whose out-of-range cell no two of them place |
| `free_text_joint` | G9.5 steps 3 and 4 as ONE packing, on a column two separate walks cannot both land |
| `identifier_edge_spacing` | G9.3's partner family where case flips supply nothing at all, so every partner is edge spacing |
| `numeric_point_free_styles` | G6.1's literal `decimal`, `leading_zero` and `leading_plus` placements, G6.4's tie order, and G5.3's clamp |
| `leap_second_endpoint` | G7.5's endpoint-fields route on a `local`-clock end whose seconds field is `60`, which the ordinal space of G7.1 has no place for |

Each case is small enough to read by hand — at most a few dozen cells —
because a vector nobody can check by hand is a vector nobody checks.

**Every case must also FAIL when the branch it exists for is removed or
reverted**, and that mutant is committed beside it. A case a withdrawn
rule would still write is a case that tests nothing, which is exactly
how the ninth case's branch carried a withdrawn rule for two rounds.

**The mutants are ONE TABLE, and its keys are the case set** (review
item P2-C4-C2). Four of the thirteen carried a mutant of their own and
nine did not, which is the same gap in a quieter form: a case whose own
rule can be reverted with every committed byte unchanged proves nothing,
whether it is named in this list or not. So the mutants are committed as
a single table whose keys are asserted equal to the whole case set — a
case added without one turns that assertion red — and each entry must
either change its own case's cells or stop the oracle from building it.
Each entry also builds its case UNMUTATED first, so a mutant that would
have refused for some unrelated reason cannot pass by refusing.

**Why the ninth case exists** (2026-08-11; review item P2-C2-F7). The
oracle carried revision 1's withdrawn rule — that `all_whole_numbers`
true means every group is written from the figures — and no frozen case
reached it, so byte equality never tested it. A branch no vector reaches
is a branch that can bless a withdrawn rule the day somebody freezes a
case on it. `identifier_whole_numbers` reaches it: twelve cells over
eight groups, `n_all_digits` 4 and `n_code_alphabet` 8, so four cells
fall in the figures, four in the code alphabet and four outside it, and
each band writes the whole-number spelling this section fixes for it.
Two doubled groups answer for each of the two non-figures counts, so the
case also pins that both alphabet counts are counts of CELLS answered
for by whole GROUPS.

**Why the four after them exist** (2026-08-12; review item P2-C3-F3).
The nine above are sound where they run, and between them they reach no
`numeric_unrepresentable` column at all, no joint class-and-alphabet
grid on free text, no fold collision that a case change cannot build,
and no cell wearing the literal `decimal`, `leading_zero` or
`leading_plus` style. So the defect G10.5 step 2 records — a generator
choosing a cross-tabulation the description never published, and losing
six exact counts on a genuine six-row column — left every committed byte
unchanged, and so would a repair that took the edge spacing back out of
G9.3. Each of the four reaches exactly one of those branches:

- **`unrepresentable_joint`** is that six-row column, published fact for
  published fact. Its three margins have one joint answer, the walk
  finds it, and the recount of G10.5 step 6 reads all twelve counts back
  off the finished cells. Withdrawing the too-small shape — which is
  what spending `n_whole` on the too-large cells amounts to — leaves the
  column with no packing at all, and that is the committed mutant.
- **`free_text_joint`** is four cells over three groups whose class
  counts and alphabet counts have a joint answer that neither margin
  settles alone: deciding the classes first hands the two singletons to
  the numeric class and leaves one doubled group owing one code-alphabet
  cell and one wide cell, which no whole group can answer for.
- **`identifier_edge_spacing`** is written in figures alone, so its one
  identity holds no character with a case and the case-flip half of
  G9.3's family is empty from the start. All three partners come from
  the edge spacing, and the case-flip-only construction revision 4
  carried cannot build the column at all.
- **`numeric_point_free_styles`** publishes the three styles the floor
  makes expensive — eleven cells each — and pins that a cell named
  `decimal` carries a point, a cell named `leading_plus` a `+` and a
  cell named `leading_zero` a redundant `0`, each recounted by the
  contract's own first-match ladder. Its ladder is flat, which also pins
  that G5.3's clamp is not decoration: the four IEEE-754 operations of
  the convex form can land one unit in the last place away from a value
  both rungs agree on, and the clamp is what brings it back.

**Why the fifteenth exists** (2026-08-13; owner decision 11). The
independent oracle still implemented the pooled-plain rule the Phase 3
repair retired, and no committed case reached the branch, so both files
stayed byte-identical while the check they exist to be proved nothing
there. `numeric_pooled_spelling` reaches it, and reaches owner decision
10's point-free spelling at any width in the same twelve cells: its
published smallest value carries a decimal point, so the cell that must
read back as it can wear no point-free form and the held-back cell is
the one that lands there; its published largest is ten to the twentieth,
whole, and written in figures. **What the case freezes is the CELLS**,
and the pooled rule's own difference is in the recount rather than in
them -- the retired rule wrote the same canonical text for that cell and
differed only in what it then owed -- so the recount identity of 7.5.7
is guarded by the style batteries and the report's golden bytes, and
this case guards the width.

**Why the fourteenth exists** (2026-08-12; review item P2-C4-C3). The
obligation G7.5's endpoint route carries had been lowered twice and
argued over in three rounds, and not one committed case held a seconds
field of `60` — so an implementation that sent the two ends back through
the ordinal space of G7.1 landed on the minute after such an end and
left every frozen byte where it was. `leap_second_endpoint` is twelve
cells on the `local` clock at `time_precision` `second`, published from
`23:00:00` to `23:59:60` on one evening, offsets `(none)` throughout. Its
first and last cells are the two ends written from their own fields, its
ten interior ranks are the ordinal transform this section already
freezes, and its committed mutant is the ordinal route put back: that
mutant writes the following midnight in place of the published end and
must fail. The pair this route cannot show on the SHARED clock is
refused by the profile contract's D10 before generation, so it is a
loader case and not a vector case — a description no loader accepts has
no twin bytes to freeze.

**`numeric_decimal_styles` was regenerated against this revision by the
oracle's own owner** (2026-08-11; review items P2-C2-F2 and P2-C2-F3).
The cells committed before the two repairs above froze the behaviour
both items rejected: they held nought `plain` cells against a published
three and three `decimal` cells against a published nought, and
twenty-one folded identities against a published twenty-three. Derived
again from this revision alone, the same case comes out with `plain` 3,
`exponent_lower` 11 and `exponent_upper` 11 — its published map exactly
— and twenty-three folded identities, its published count exactly, at
the cost of one raw spelling (23 against a published 24), which the
exact map forces because the column holds only one value a point-free
spelling can be written for and all three `plain` cells must therefore
share it. G6.5's stated precedence — the published style counts are met
first and distinctness is met within them — is what decides that trade,
and G12.8's envelope prints the range the raw count fell in.

The vectors are the independent artifact of P2-D7 and are written by a
tool that imports nothing from `src/`. Reconciling that tool to this
revision, regenerating the file and reviewing the affected proof and
bytes belonged to that tool's owner, exactly as review item P2-C2-F7
directed for the identifier branch it found stale; an implementer
editing the independent artifact to agree with implementation work would
weaken the provenance the artifact exists for. The reconciliation was
carried out from this document, the committed bytes were rebuilt and
re-registered, and `tests/test_generation_reference.py` now holds the
implementation to the regenerated case with no exception of any kind.

### G14.4 What the vectors do NOT freeze

- **The word stream.** The vectors take words as inputs. The stream from
  a seed is bound by the golden twin and report hashes on every CI cell,
  with the numpy floor proved by the `minimums` job.
- **The report's bytes.** Golden-tested separately (P2-D10).
- **Anything about a real table.** No value in the file comes from any
  real or synthetic table; every published fact in every case is written
  by hand in this document's own neutral vocabulary.

---

## Conformance checklist

An implementation conforms to this document when all of the following
hold, and each has a test:

1. One generator, created once from the seed, threaded explicitly; no
   module-level randomness; no second random source (G3.1).
2. Every random quantity comes from the one draw form of G3.2, with
   `dtype` given as the string `"uint64"` and each element converted by
   `int(...)` before use.
3. The word count per column matches G4.3 exactly, and the reference
   vectors' `word_budget` is asserted against it.
4. Columns are consumed in `columns` list order; the first word of the
   run belongs to the first column (G4.1).
5. Numeric endpoints are exact; the nine interior rungs sit inside the
   two-sided window of G5.6; the rung-ignoring, rung-permuting,
   rung-swapping and endpoints-only mutants each fail it.
6. `n_zero`, `n_negative`, `integer_valued`, the four class counts and
   the published style counts are each recounted from the WRITTEN CSV
   and match exactly, outside the named deviations of G12.
7. Datetime cells carry the published precision and offset state, and a
   profile → twin → profile round trip returns the same `resolution`,
   `time_precision`, `subsecond_digits`, `utc_offsets` and
   `datetimes_read_at` (G7).
8. Label counts, variants and withheld level sizes are recounted from
   the written CSV and match exactly (G8).
9. The capacity rule is decided before any file is created, and the
   named refusal leaves every byte on disk unchanged (G9.4).
10. Twin bytes are identical for identical inputs; a different seed
    changes interior values for a profile that has a random degree of
    freedom; and twin bytes are seed-INVARIANT for a fully determined
    profile — one whose published counts pin every cell (G4.2 makes this
    true: an arrangement of identical entries is identical).
11. EVERY committed vector file rebuilds byte-for-byte in CI; the oracle
    imports neither `synthtwin`, nor numpy, nor pandas (G14); every case
    G14.3 names is present; and each one FAILS when the branch it exists
    for is removed or reverted, because a case a withdrawn rule would
    still write tests nothing (G14.3).
12. The packing of G9.5 meets every quota of EVERY margin exactly
    whenever an assignment of whole groups exists; its margins are the
    families the description publishes and no others, so no
    cross-tabulation of them is chosen by the implementation (G10.5);
    and **nothing counts the walk's work and stops it** — a description
    a producer can emit reached the ceiling that once did (P2-C3-F1),
    so the only end of the walk is the finite state space of G9.5.

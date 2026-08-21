### 7.5 `numeric_styles`

A census of the FORM a numeric column's cells were written in: no
value, no magnitude, no spelling, only counts of form. Without it the
three source families `0`/`00`/`000`, `0.0`/`00.0`/`000.0` and
`0e0`/`00e0`/`000e0` give **byte-for-byte identical** column blocks,
though the first reads as whole-number and the others as decimal
(decision 10). REQUIRED on `count`, `continuous` and `affixed_number`;
FORBIDDEN on every other role **including `numeric_unrepresentable`**,
whose invented digit strings at one canonical width (R-P2-1) no style
map describes.

#### 7.5.1 The six styles

Exactly six; an implementation may add no seventh.

| style | what it names |
|---|---|
| `plain` | the canonical spelling: digits, an optional leading minus, no point, no exponent, no redundant zero |
| `leading_zero` | the digits before any point start with a redundant `0` |
| `leading_plus` | the cell begins with `+` |
| `decimal` | the cell carries a decimal point |
| `exponent_lower` | the cell carries a lower-case `e` exponent |
| `exponent_upper` | the cell carries an upper-case `E` exponent |

#### 7.5.2 C6-83 — the classification ladder

Every counted cell takes **exactly one** style, by a first-match-wins
ladder over its text. The ORDER is normative: it makes producer and
generator agree.

1. Strip surrounding whitespace; unwrap a matching pair of accounting
   parentheses and strip again; remove thousands-separator commas. The
   result is the **core**, so `(05)` is `leading_zero` and `1,234` is
   `plain`.
2. `exponent_upper` — the core contains the character `E`.
3. `exponent_lower` — the core contains the character `e`.
4. `decimal` — the core contains the character `.`.
5. `leading_plus` — the core begins with `+`.
6. `leading_zero` — after any leading `-`, the core begins with `0` and
   is longer than that single `0`.
7. `plain` — everything else.

**Type-bearing forms come first** because a reader infers a decimal
column from a point or exponent anywhere, so where a cell carries two
marks the style fixing the inferred type is counted: `+0.5` is
`decimal`, its plus lost while the totals close.

**This ladder is what a twin cell's style IS.** The same rule reads the
real column and the twin's finished cells, so a style is what the
ladder makes of the text the twin wrote, never a label kept beside the
cell — a recount from the CSV sees nothing else. Hence `plain`,
`leading_zero` and `leading_plus` can only be a WHOLE value's style: a
non-whole value's canonical spelling already carries a point or an
exponent.

#### 7.5.3 The wire shape

An object mapping a style name to a count, plus a `(withheld)`
remainder when the floor pooled anything. Keys are the six style names
or `(withheld)`, values integers ≥ 1; a style used by no cell has no
key, and one used by fewer rows than the floor pools into `(withheld)`
instead, so a single oddly-written cell cannot be singled out.

#### 7.5.4 Invariants

**P1 (the population).** The values sum to `n_numeric` — the present
cells that read as a number binary64 can hold — and to `n_core_numeric`
on `affixed_number` (AF7). Out-of-range and contradictory cells are NOT
counted: plan P2-D9's class-preserving construction writes them in
forms the six styles cannot express, so counting them would oblige a
form no generator writes.

**P2 (the floor, both ways).** Every value under a style NAME is at
least `small_cell_floor`. `(withheld)` appears only when the pooled
remainder is at least 1, and its own value may be anything from 1 up.

**P3 (never empty here).** Never `{}`: the numeric count is at least 1
on these roles (Q3) and every counted cell lands in a key.

**P4 (independent of `integer_valued`).** `integer_valued: true` does
not forbid `decimal` or an exponent style — `5.0` is whole, written
with a point. A loader checks neither against the other.

#### 7.5.5 Disposition, and the recount identity

EXACT-OBSERVABLE. **The twin writes each named style in its published
count**, and **may write only the six of 7.5.1, never a seventh** —
never a thousands separator, which breaks the CSV row, never accounting
parentheses, excluded by decision 8 and kept for the
contradictory-notation stand-in. Both are classified by digit form and
written on no column: a cell standing for `(05)` is written as a signed
leading-zero form, not brackets (R-P2-9: a twin numeric column can be
punctuated differently from its source).

**Why all six**, when decision 8's invention family is three: decision
8 fixes what the twin INVENTS where a count needs more spellings than
the map holds, decision 10 what it REPRODUCES — a `decimal` cell
carries a point because the real one did. The exponent pair alone
carries case, the only way a folded count falls below a raw one.

**C6-84 (a pooled cell is written by its own value):** plainly where
the value has a point-free spelling, `plain` changing nothing a reader
infers; in its own canonical text (3.2.1) where it has none. The rule
writing EVERY pooled cell plainly is withdrawn — a published end
carrying a point has no point-free spelling, so it and `min`/`max`
exactness could not both be met — and no published count moves. Two
withdrawn wordings a test can ban: pooled cells as those in no
published style (every cell text falls in one of the six, so no
outside-the-styles bucket exists), and the remainder added to `plain`.

**C6-85 (the recount identity).** Write `r(s)` for the cells a recount
finds in `s`, `p(s)` for its published count, `R` for the `(withheld)`
remainder, `NW` for the written numeric cells whose VALUES have no
point-free spelling. Each clause is computable from the cells
and map:

- `r(s) = p(s)` for `leading_zero`, `leading_plus` and `exponent_upper`
  — the remainder never reaches these three: the first two are decision
  8's invention family, and canonical text never carries `E`;
- `r(s) >= p(s)` for `plain`, `decimal` and `exponent_lower` — **a
  published form is never substituted away**;
- the spill `D = max(0, NW - p(decimal) - p(exponent_lower) -
  p(exponent_upper))` is exactly the pooled cells with no point-free
  spelling, the published point-carrying counts being spent on them
  first;
- `r(decimal) + r(exponent_lower) = p(decimal) + p(exponent_lower) + D`;
- `r(plain) = p(plain) + R - D`, the remainder's other cells;
- **no cell is spelled non-canonically without a published count
  entitling it**: in `decimal` and `exponent_lower` the cells whose
  text is NOT their own value's canonical text are at most its
  published count, so every pooled cell carries its own canonical text
  and no pool is re-spelled into a form never named.

`NW` is read off the VALUES, never the spellings: counting cells
WRITTEN with a point would make the identity circular, a twin spelling
a whole `1000` as `1000.0` inflating its own `D`. Where nothing pooled,
`D` is zero and every style matches its count exactly; **an alternate
spelling is used ONLY where the counts require it**, so an
all-canonical whole-number column publishes `{"plain": n}` and stays
byte-plain. The report names the remainder, the cells it covered and
how many lacked a point-free spelling.

### 7.6 `fraction_widths`

**C6-27 (where it lives).** A `count`, `continuous` or `affixed_number`
block carries `fraction_widths` as a key of the BLOCK, a sibling of
`numeric_styles` and NOT a key inside it, and forbidden on every other
role. Inside is impossible: P1 makes every value of
`numeric_styles` an integer summing to the numeric count; an object is
neither. The plan said inside; it was amended rather than this
document deviating (**A-P4-5**).

**C6-28 (what it holds).** A mapping from a fraction width — digits
after the point — to the number of `decimal`-styled cells at that
width, with the pooled key `(withheld)` for widths fewer than
`small_cell_floor` cells share; read over the cores on `affixed_number`
(AF7).

**C6-29 (key grammar: one width, one spelling).** A width key is the
decimal spelling of a non-negative integer: no sign, no leading zero
unless the width is itself zero, no space, no other character — `0`,
`1`, `2`, `10`. `02`, `+2` and `-1` are not width keys and a loader
refuses one; `(withheld)` is the only non-numeric key permitted.

**C6-30 (invariants, by cases).** The census counts DECIMAL-styled
cells, so its invariants are cases over what `numeric_styles` says
about that style; the cases are exhaustive over that key's shapes and
each binds something. **P5 (the sum).** Let *F* be the sum of ALL
values, `(withheld)` included; an empty census has *F* = 0, read at
that value by every condition below.

- **P5.a — a `decimal` key is published.** *F* equals that key's value
  exactly.
- **P5.b — no `decimal` key and no `(withheld)` key.** No decimal cell
  exists: `fraction_widths` is `{}`, *F* zero.
- **P5.c — no `decimal` key but a `(withheld)` key.** Any decimal count
  was pooled and no published number holds it, so `fraction_widths` is
  EITHER `{}` (no decimal cell, the pool holding other styles) OR the
  pooled decimal cells under its own `(withheld)`. Write *W* for
  `numeric_styles["(withheld)"]`. FOUR conditions bind, any breach
  refusing the document:

  1. *F* is at least 1 wherever the census is NON-EMPTY (A-P4-6) — the
     one condition confined to that branch, an empty census being what
     a column with no decimal cell writes;
  2. *F* is strictly BELOW `small_cell_floor`, a style being pooled
     only when its count falls below the floor;
  3. *F* is at most *W*, the pooled decimal cells being a subset of the
     pool;
  4. ***F* ≥ *W* − 5 × (`small_cell_floor` − 1)** (A-P4-8): six styles
     exist, so at most five share the pool with decimal, each holding
     at most `small_cell_floor` − 1 cells. Vacuous where the right-hand
     side is zero or negative. It refuses *W* = 60 beside
     `{"(withheld)": 1}` at a floor of 11, which 1 to 3 admit — *F* ≥
     10 is required, one of the other five otherwise holding twelve.

**Condition 4 also decides an EMPTY census; no fifth is needed.** At
*F* = 0 it reads *W* ≤ 5 × (`small_cell_floor` − 1), the pool being the
five styles other than decimal: it refuses
`{"(withheld)": 51}` beside `{}` at a floor of 11, which 2 and 3 admit,
fifty-one being unshareable by five styles holding ten each.

**P6.** Every NAMED width's count is at or above `small_cell_floor`.
**P7.** A width key is present only if its count is nonzero, so a
present `(withheld)` value is at least 1; this closes the route R-P3-12
records.

**Disposition: EXACT-OBSERVABLE**, against a C6-85-shaped recount:
cells recounted at a named width number at least the published count
and at most it plus the pooled `(withheld)` value — exact where nothing
pooled, windowed where something did. **P5 to P7 do not reach
producer obligation FW-P**: they bound the census against published
numbers, and none checks that a width count IS the count of source
cells at that width — a loader holds no table and cannot recompute it.
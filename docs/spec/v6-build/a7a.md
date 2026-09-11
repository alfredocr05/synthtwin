### 5.3 The multiplicity map — one shape, published in two places

A **multiplicity map** is an object whose keys are row counts written in
base ten and whose values are how many different things covered exactly
that many rows.

**C6-90 (the form of a multiplicity map).** Every map of this shape,
wherever it is published, obeys all four rules below.

- **Key form.** Each key is the row count in base ten, left-padded with
  zeros to the width of the LARGEST key in the SAME mapping. Padding is
  what makes the canonical sorted-key order a numeric order: written
  bare, `"10"` sorts before `"2"`. A consumer reads a key as a base-ten
  number; leading zeros do not change it. Every key in one map has the
  same width.
- **Key range.** Every key reads as an integer ≥ 1.
- **Value range.** Every value is an integer ≥ 1. A count that covered
  nothing has no key.
- **Empty map.** `{}` is valid and means the thing being counted has no
  members.

**Invariant M1 (entry sum).** The values sum to the number of different
things the map describes.

**Invariant M2 (weighted sum).** The keys, read as numbers and weighted
by their values, sum to the number of rows the map covers.

M1 and M2 are stated abstractly here and bound at each use, so a loader
always has named quantities to check them against.

| published map | what it counts | where its bounds are stated |
|---|---|---|
| `n_distinct_by_occurrences` | different RAW present values of one column | invariants U3 (`numeric_unrepresentable`), I2 (`identifier`) and F2 (`free_text`); its shape, class and disposition at section 7.2 |
| `variants_withheld` | different spellings of one published label that stayed below the floor | section 7.4: W4 closes its weighted sum inside the level entry, W5 holds every key between 1 and `small_cell_floor - 1` |

`suppressed_level_counts` (section 6.3) is the same CLASS of fact —
sizes of unnamed groups — but it is NOT this shape: it is a sorted
array, not a map, and that shape does not move.

### 7.2 Multiplicity parity for `free_text` and `numeric_unrepresentable`

**C6-91 (parity).** `n_distinct_by_occurrences` stands on `free_text`
and on `numeric_unrepresentable` **with the identifier field's exact
shape and serialization** — the multiplicity map of section 5.3, no
variation of any kind. One key form, one canonical serialization, on
every role that carries the key.

**What the map counts here.** Its values are how many different RAW
present values covered exactly that many rows, and it is `{}` when the
column has no present value. **Distinctness is over RAW present
values**, the same question `n_distinct` answers, so the two always
agree — which is what M1 states on this key. Two spellings that fold to
one identity are two different raw values and are counted as two; this
map does not bind `n_distinct_folded`, which is a separate count under
its own obligations. The concrete pairs are stated once per role, at U3
(`numeric_unrepresentable`), I2 (`identifier`) and F2 (`free_text`):
the values sum to `n_distinct`, and the keys weighted by the values sum
to `n_present`.

**The KEY's reach and this RULE's reach are different, and neither
implies the other.** The key `n_distinct_by_occurrences` appears on
three roles — `numeric_unrepresentable`, `identifier` and `free_text` —
and on no other role, which the forbidden-key matrix of section 6.11
fixes cell by cell. The rule stated here is the narrower one: it is
what puts the identifier field's exact shape on the other two roles.
Reading the key's three-role reach off this rule's two-role title, or
the rule off the matrix, misstates one of them.

**Publication class: counts about unnamed groups, with no small-cell
floor.** The map is a function of the group SIZES alone: rename every
value, or shuffle every row, and it does not move. No spelling, no
order, no row position and no link to any other column reaches it. It
is the same class of fact as `suppressed_level_counts`, which publishes
the sizes of the withheld levels for the same reason. What it does
disclose, stated rather than waved away, is the sizes themselves: a map
containing `"1": 1` says some one row holds a value no other row holds.
That is a count about an unnamed group, and it is why the profile is
described as real-derived material rather than as anonymous.

**Why the key is needed at all.** Without it, two columns with
different repetition patterns serialize to identical bytes — six rows
holding one value four times and two values once each, versus six rows
holding three values twice each, both recording `n_present` 6 and
`n_distinct` 3 — so a generator reading the profile alone would have to
pick one pattern for both, and any grouped analysis on the twin would
diverge from the real table.

**The floor-free class was checked here rather than assumed.** At the
extremes the map adds nothing already published: one present value
gives `{"1": 1}`; every value different gives `{"1": n_distinct}`;
every value the same gives one entry keyed on `n_present`. Each of
those is forced by `n_present` and `n_distinct`, which every profile of
this contract publishes. Between the extremes it adds exactly one
thing: the size of each repetition group, with nothing saying which
group. Knowing that some value covers four of six rows does not say
which value, and no value of the column appears anywhere in its block.

**Disposition.** EXACT-OBSERVABLE on `free_text` and on
`numeric_unrepresentable`. On `identifier` it is EXACT-OBSERVABLE
outside owner decision 6's infeasible corner and REPORT-ONLY inside it
(section 6.8), where it is one of the three distinctness facts that
corner costs.

### 7.3 The relationship manifest

**C6-92.** The `relationships` manifest is specified in section 4.6:
one top-level object, eight required keys and no ninth, every value
exactly `null`, enforced by invariant S12. Disposition: LOADER-ONLY,
one disposition covering the whole subtree, because nothing under it is
an output obligation.

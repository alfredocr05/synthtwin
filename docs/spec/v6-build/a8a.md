## 8. Every invariant, in one checkable list — part one

This section restates the rules above as one list a loader or a test can
walk. Each row is true or false with no interpretation left; the
identifiers are the ones the sections above use.

**The third column.** `yes` — true or false of ONE PARSED DOCUMENT; a
loader decides it holding nothing else. `producer` — checked
producer-side, because a loader holds no table. `reading` — the row
fixes what a field MEANS and leaves a loader nothing to refuse.
`contract` — true or false of a table printed in this contract, not of
a document, so no document can violate it.

### 8.1 The document, its containers, the version

| id | statement | loader? |
|---|---|---|
| C6-44 | `profile_version` is the integer 6; every other integer is refused, and the version is read BEFORE the canonical round trip, so an older description draws advice about itself rather than a complaint about canonical form | yes |
| S1 | `len(columns) == n_columns` | yes |
| S2 | for every index `i` from zero, `columns[i].position == i + 1`; positions are exactly `1..n_columns`, each once, increasing along the list | yes |
| S3 | the order of `columns` IS the schema order of the table, the left-to-right order of the twin's columns and of a written header row, and the order the single RNG stream is consumed | reading — else two producers could route values and RNG bytes differently while every set-shaped rule passed |
| S4 | column names are non-empty after trimming and pairwise distinct as text; two names differing only in case or in surrounding space are distinct and both kept as written | yes |
| S5 | `source.used_fallback_encoding` is true exactly when `source.encoding == "latin-1"` | yes |
| S6 | `source.header_by_convention` true implies `source.header_source == "file"`; generated names are not a convention about somebody's first record | yes |
| S7 | `values_recorded` is `false` in both declaration records — neither carries the text the person typed; `true` is refused, naming an older profile that recorded spellings under this key | yes |
| S8 | every name in `settings.forced_identifiers` is some column's `name`; a name matching no column means the profile and the schema disagree | yes |
| S9 | `settings.categorical_floor <= settings.categorical_ceiling` | yes |
| S10 | every `publication_notes[i].column` is some column's `name` | yes |
| S11 | `publication_notes` is grouped by column in schema order, and within one column in producer emission order; the grouping is decidable, the within-column order canonical bytes a loader does not re-derive | yes |
| S12 | `relationships` has exactly the eight reserved keys, no ninth, every value exactly `null` | yes |
| S13 | at `small_cell_floor` 1 every field carrying what the floor held back is empty or zero, over 4.4's closed list; on `missing_by_class`, `utc_offsets`, `numeric_styles` and `fraction_widths` the `(withheld)` ENTRY goes, never the map. Checked before any column block is read | yes |
| S14 | each declaration record has exactly five keys | yes |
| C6-20 | `settings` has exactly its seventeen keys; sixteen or eighteen is a document this contract does not describe | yes |
| C6-53 | a column block's key set is exactly the twenty-two universal keys plus the marked cells of its role's column in the forbidden-key matrix; every other key is FORBIDDEN, and refused by name | yes |

**Four membership rules of this part carry no identifier**, so no list
can cite them: the nine top-level keys (4.1), the five `source` keys
(4.3), a level entry's four (6.3.1), a `publication_notes` entry's two
(4.5). Each is normative where stated, and a loader enforces it.

### 8.2 The cell census — X

| id | statement | loader? |
|---|---|---|
| X1 | `n_present + n_missing == n_rows`, the DOCUMENT's `n_rows`, never the per-column echo, a different quantity | yes |
| X2 | `n_numeric + n_not_numeric + n_out_of_range + n_contradictory == n_present`. The four classify the complete present CELL on all thirteen roles; on `affixed_number` they stand BESIDE its four core counts, never in place of them | yes |
| X3 | `n_distinct_folded <= n_distinct <= n_present` | yes |
| X4 | `n_distinct == 0` ⇔ `n_present == 0` ⇔ `n_distinct_folded == 0` | yes |
| X5 | `1 <= position <= n_columns` | yes |

### 8.3 Absent cells — N

| id | statement | loader? |
|---|---|---|
| N1 | `missing_by_class` carries exactly SIX keys — `(blank)`, `(date-sentinel)`, `(declared-missing)`, `(numeric-sentinel)`, `(text-code)`, `(withheld)` — always all six, on every column block of every role, and their six values sum to `n_missing` | yes |
| N2 | each `missing_by_class` value other than `(withheld)` is 0 or at least `small_cell_floor`: a class counting between 1 and the floor is pooled into `(withheld)` and reads 0 here. `(withheld)` is exempt — the remainder the named counts were pooled out of, and one remainder pools several classes | yes |
| N3 | on a column that is not a nothing-publishing column, `sum(missing_by_source.values()) + n_missing_blank + n_missing_withheld == n_missing`; on a nothing-publishing column `missing_by_source == {}` and both counts are 0, whatever `n_missing` is | yes |
| N4 | every value of `missing_by_source` is at least `small_cell_floor`, with no exemption, and `n_missing_blank` is 0 or at least the floor. `n_missing_withheld` is bounded in neither direction, for N2's reason | yes |
| N5 | no key of `missing_by_source` carries a first-party meaning — not the six class words nor any other name this format uses (`n_missing_withheld`, `n_sentinel_candidates_unpublished` among them), because a cell can say those too: such a key means cells of the table held that text. `levels[].variants` is the other map the TABLE keys | reading |
| N6 | `n_missing_blank` and `n_missing_withheld` are 0 on exactly the nothing-publishing columns; that class is a function of `role` and `structural_role`, which every block publishes | yes |
| N7 | a `missing_by_source` key is the source spelling character for character | producer |

### 8.4 The declaration records — K

| id | statement | loader? |
|---|---|---|
| K1 | every element of `built_in_texts` is in the published vocabulary's spelling list, of `built_in_numbers` in its stand-in list, of `built_in_dates` in its calendar-placeholder list; anything else is a value from somebody's table, refused and named | yes |
| K2 | all three arrays are sorted ascending and pairwise distinct — texts and dates by code point, numbers numerically. Order is part of the canonical bytes | yes |
| K3 | in each record, `len(built_in_texts) + len(built_in_numbers) + len(built_in_dates) <= n_declared`. `<=` and not `==`: no declaration lands in two lists, so the shortfall is exactly the number of values named that were not synthtwin's own words, never their text | yes |
| K4 | no member appears in both `kept_values` and `declared_missing_values`, across ALL THREE lists | yes |
| K5 | the six lists — three in each record — are a function of the command line alone; a declared value matching no cell of any column is recorded exactly as one matching every cell | producer |

### 8.5 The axes — A

| id | statement | loader? |
|---|---|---|
| A1 | `structural_role == "identifier"` if and only if `name` appears in `settings.forced_identifiers` | yes |
| A2 | `statistical_type == "code"` implies `structural_role == "identifier"`: there is no route to the `identifier` role but the declaration | yes |
| A3 | `structural_role == "identifier"` implies `statistical_type` is `code` or `unknown`, and `role` is `identifier` or `empty` | yes |
| A4 | the triple (`role`, `statistical_type`, `quality_state`) is exactly one row of 5.2's thirteen-row table; refused rather than repaired, naming the column and its three values | yes |
| A5 | that table is total over the thirteen roles: every role of the vocabulary has a row, and no role has two | contract |

### 8.6 The label roles — B, and the six that restrict them

The eight B rows are stated over a block carrying `levels`, not over a
list of roles, so each binds `constant`, `binary`, `categorical` and
`long_tail_labels` identically.

| id | statement | loader? |
|---|---|---|
| B1 | every `label` is a folded identity: it equals its own trimmed, case-folded form, so a published label may never have appeared byte for byte in the table; what the table held is in `variants` | yes |
| B2 | `len(levels) + suppressed_levels == n_distinct_folded` | yes |
| B3 | `sum(entry.count for entry in levels) + suppressed_rows == n_present` | yes |
| B4 | `len(suppressed_level_counts) == suppressed_levels`, `sum(...) == suppressed_rows`, and the array is sorted ascending — non-decreasing: two held-back labels may cover the same size | yes |
| B5 | every `entry.count` is at least the floor; every element of `suppressed_level_counts` is at least 1 and below the floor | yes |
| B6 | `levels` is ordered by descending `count`, then ascending `label`; with B7 a total order, so one set of levels has exactly one conforming sequence | yes |
| B7 | no two entries share a `label` | yes |
| B8 | `levels == []` is valid — every label fell below the floor — and then `n_distinct_folded == suppressed_levels`, `n_present == suppressed_rows` | yes |
| C1 | `constant`: `n_distinct_folded == 1` | yes |
| C2 | `constant`: `len(levels) + suppressed_levels == 1`, which is C1 and B2 together | yes |
| Y1 | `binary`: `n_distinct_folded == 2` | yes |
| Y2 | `binary`: `len(levels) + suppressed_levels == 2`, which is Y1 and B2 together | yes |
| G1 | `categorical`: `n_distinct_folded <= level_ceiling` | yes |
| G2 | `level_ceiling` imposes no output obligation on the twin: the generator reproduces counts, not the rule that produced them | reading |

### 8.7 Multiplicity maps — M

These bind `n_distinct_by_occurrences` and `variants_withheld`.

| id | statement | loader? |
|---|---|---|
| M1 | values sum to the number of different things described | yes |
| M2 | keys read as numbers, weighted by values, sum to the rows covered | yes |
| M3 | every key is a base-ten integer ≥ 1, and all keys in one map have the same character width, that of the largest key | yes |
| M4 | every value is an integer ≥ 1 | yes |

### 8.8 Label spellings — W

| id | statement | loader? |
|---|---|---|
| W1 | `variants` and `variants_withheld` appear on published level entries only | yes |
| W2 | trimming and case-folding a variant key yields the entry's `label` | yes |
| W3 | every `variants` value is at most the entry's `count` | yes |
| W4 | `sum(variants.values()) + sum(key × value over variants_withheld) == count` | yes |
| W5 | every `variants` value is at least the floor; every `variants_withheld` key is in `1 .. floor - 1` | yes |
| W6 | variant keys are distinct | yes |
| W7 | `variants` and `variants_withheld` are not both empty on one entry | yes |

**The list continues** in the next section: the remaining roles, the
ladder and stand-in rules, and the producer obligations.

## 14. Appendix: every enumeration in one place

**What this section is, and what it is not.** It is a READING AID: one
place to check a spelling and a count without walking the document.
Every list here is defined normatively somewhere else, and that section
is named beside it. **Where this appendix and a defining section
differ, the defining section governs and this appendix is defective** —
not the other way round, and never "whichever reads better". Every
count is stated beside its list so that the two can be checked against
each other by reading.

**The one named exception, so that no list is defined nowhere.** The
published vocabulary of 14.4 is DEFINED here and not elsewhere. It is
the list the declaration rules of 4.4 and the absent-cell rules of
section 5 bind to by name, and it has one home so that the eight
members this version adds cannot be added in one place and missed in
another. Every other list in this section is a copy, and the sentence
above governs it.

### 14.1 Roles, axes and classes

**`role` — 13.** Defined in 5.2, specified role by role in section 6.
In the order the rules of 5.2 test them: `empty`, `identifier`,
`numeric_unrepresentable`, `constant`, `binary`, `datetime`, `count`,
`continuous`, `categorical`, `time_of_day`, `affixed_number`,
`long_tail_labels`, `free_text`. Thirteen roles in twelve rules,
because `count` and `continuous` are decided by one rule that then
chooses between the two.

**`statistical_type` — 13.** Defined in 5.2: `unknown`, `numeric`,
`constant`, `binary`, `datetime`, `count`, `continuous`,
`categorical`, `code`, `text`, `time_of_day`, `affixed_number`,
`long_tail_labels`.

**The axis derivation rows — 13.** Defined in 5.2, which is the
authority; the set of rows, not this order, is normative.

| `role` | `statistical_type` | `quality_state` |
|---|---|---|
| `empty` | `unknown` | `empty` |
| `numeric_unrepresentable` | `numeric` | `unrepresentable` |
| `constant` | `constant` | `ok` |
| `binary` | `binary` | `ok` |
| `datetime` | `datetime` | `ok` |
| `count` | `count` | `ok` |
| `continuous` | `continuous` | `ok` |
| `categorical` | `categorical` | `ok` |
| `identifier` | `code` | `ok` |
| `free_text` | `text` | `ok` |
| `time_of_day` | `time_of_day` | `ok` |
| `affixed_number` | `affixed_number` | `ok` |
| `long_tail_labels` | `long_tail_labels` | `ok` |

Four roles answer something other than their own name — `empty`,
`numeric_unrepresentable`, `identifier` and `free_text` — and the other
nine name their own shape.

**`quality_state` — 3:** `ok`, `empty`, `unrepresentable`.
**`structural_role` — 2:** `data`, `identifier`.

**Publication buckets — 4** (6.10). Every role is in exactly one.

| bucket | roles | count |
|---|---|---|
| labels | `constant`, `binary`, `categorical`, `long_tail_labels` | 4 |
| ranges | `count`, `continuous`, `datetime`, `time_of_day`, `affixed_number` | 5 |
| nothing | `numeric_unrepresentable`, `identifier`, `free_text` | 3 |
| no value-publishing class | `empty` | 1 |

Separately and binarily, a **nothing-publishing column** is a column of
one of the three nothing-class roles, or any column whose
`structural_role` is `identifier` whatever its role. The role `empty`
does not BY ITSELF make a column one: an undeclared all-absent column
is not a nothing-publishing column, and a declared one is, by that
override.

**Disposition classes — 6** (2.2): `EXACT-OBSERVABLE`,
`EXACT-CONTROL`, `APPROXIMATED`, `REPORT-ONLY`, `LOADER-ONLY`,
`STRUCTURAL`.

**Forbidden-key matrix — 55 rows over 13 role columns**, 107 marked
cells, defined in 6.11. Not reproduced here; a matrix is not a list.

### 14.2 Document and block key sets

**Top-level keys — 9** (4.1): `columns`, `created_with`, `n_columns`,
`n_rows`, `profile_version`, `publication_notes`, `relationships`,
`settings`, `source`.
**`profile_version` — 1 permitted value:** the integer `6`.

**`source` keys — 5** (4.3): `encoding`, `header_by_convention`,
`header_evidence`, `header_source`, `used_fallback_encoding`.
**`source.encoding` — 2:** `utf-8-sig`, `latin-1`.
**`source.header_source` — 2:** `file`, `generated`.

**`relationships` keys — 8** (4.6), every value exactly `null`:
`deterministic`, `grain`, `hierarchy`, `keys`,
`missing_data_process`, `statistical`, `temporal`,
`validation_targets`.

**`publication_notes` entry keys — 2** (4.5): `column`, `note`.

**Universal column keys — 22** (5.1): `detection_evidence`,
`missing_by_class`, `missing_by_source`, `n_contradictory`,
`n_distinct`, `n_distinct_folded`, `n_missing`, `n_missing_blank`,
`n_missing_withheld`, `n_not_numeric`, `n_numeric`, `n_out_of_range`,
`n_present`, `n_sentinel_candidates_unpublished`, `name`, `position`,
`quality_state`, `remarks`, `role`, `sentinel_verdicts`,
`statistical_type`, `structural_role`.

**Level entry keys — 4** (6.3.1): `count`, `label`, `variants`,
`variants_withheld`.

**`sentinel_verdicts` entry keys — 4** (5.5): `candidate`,
`n_occurrences`, `reason`, `verdict`.
**`verdict` — 2:** `read_as_missing`, `kept_as_a_number`.
**`reason` — 5:** `outlier_and_frequent`, `not_an_outlier`,
`too_rare`, `too_few_other_values`, `kept_by_you`.

**The ladder — 11 rungs**, in this order (2.3): `min`, `p01`, `p05`,
`p10`, `p25`, `p50`, `p75`, `p90`, `p95`, `p99`, `max`.

### 14.3 Settings and declarations

**`settings` keys — 17** (4.4), in the ascending code-point order every
object of a canonical document takes: `categorical_ceiling`,
`categorical_floor`, `categorical_share`, `day_first`,
`declaration_matching`, `declaration_publication`,
`declared_missing_values`, `forced_identifiers`,
`identifier_minimum_rows`, `identifier_uniqueness`, `kept_values`,
`long_tail_minimum_level`, `minimum_parse_rate`,
`near_threshold_slack`, `sentinel_minimum_share`,
`sentinel_outlier_iqr_multiple`, `small_cell_floor`.

**`settings.declaration_matching` — 1 permitted value:**
`exact_number_when_it_reads_as_one_else_spelling`.
**`settings.declaration_publication` — 1 permitted value:**
`settings_counts_only_columns_unchanged`.
**`settings.long_tail_minimum_level` — 1 permitted value:** `11`.

**Declaration-record keys — 5** (4.4), in `kept_values` and in
`declared_missing_values` alike: `built_in_dates`, `built_in_numbers`,
`built_in_texts`, `n_declared`, `values_recorded`.

### 14.4 The published vocabulary — 23 members

**This list is DEFINED here** (the named exception at the head of this
section), and 4.4 and section 5's absent-cell rules bind to it.
Extending any part is a change to this contract and advances
`profile_version`.

**Eighteen text spellings read as "no value".** Seventeen are compared
after trimming and a Unicode case fold; one is compared by raw byte
equality with the cell, with no trimming and no case folding.

| # | member | matched |
|---|---|---|
| 1 | `` (the empty spelling) | folded |
| 2 | `-` | folded |
| 3 | `--` | folded |
| 4 | `.` | folded |
| 5 | `?` | folded |
| 6 | `n/a` | folded |
| 7 | `na` | folded |
| 8 | `nan` | folded |
| 9 | `none` | folded |
| 10 | `null` | folded |
| 11 | `#DIV/0!` | folded |
| 12 | `#N/A` | folded |
| 13 | `#NAME?` | folded |
| 14 | `#NULL!` | folded |
| 15 | `#NUM!` | folded |
| 16 | `#REF!` | folded |
| 17 | `#VALUE!` | folded |
| 18 | `NaT` | EXACT bytes |

**Three stand-in numbers**, compared as numbers, written in a document
in these canonical forms: `-9999.0`, `-999.0`, `9999.0`.

**Two calendar placeholders**, written as their canonical ISO day
spellings: `1900-01-01`, `9999-12-31`.

A stand-in or a placeholder is read as "no value" only where the
column's own rule judges it to be one, and every candidate's fate is
published in `sentinel_verdicts` either way. Being on this list is not
a verdict.

### 14.5 Absent cells

**Absence classes — 6**, the keys of `missing_by_class`, always all six
on every column block of every role (5.4): `(blank)`,
`(date-sentinel)`, `(declared-missing)`, `(numeric-sentinel)`,
`(text-code)`, `(withheld)`.

**`missing_by_source` keys** are absent-value SPELLINGS of the table
and nothing else. There is no reserved key in that map: the pooled
count and the blank count live in `n_missing_withheld` and
`n_missing_blank`.

### 14.6 Datetime and clock

**`format` — 11** (6.6.2), each with the `resolution` it requires:

| `format` | `resolution` |
|---|---|
| `iso-date` | `date` |
| `month-first-date` | `date` |
| `day-first-date` | `date` |
| `compact-date` | `date` |
| `slashed-iso-date` | `date` |
| `iso-month` | `month` |
| `year-quarter` | `quarter` |
| `iso-datetime` | `datetime` |
| `iso-mixed` | `datetime` |
| `month-first-datetime` | `datetime` |
| `day-first-datetime` | `datetime` |

**`resolution` — 4:** `date`, `datetime`, `quarter`, `month`.
**`time_precision` — 6:** `subsecond`, `second`, `minute`, `date`,
`quarter`, `month`.
**`datetimes_read_at` — 2:** `local`, `utc`.
**`clock_form` — 2:** `hh-mm`, `hh-mm-ss`.
**`resolution_mix` keys** are `format` members: on a single-format
column exactly the column's own member; on an `iso-mixed` column
exactly `iso-date` and `iso-datetime`. No other key set conforms.

### 14.7 Numeric spelling

**Numeric styles — 6**, plus the pooled key (7.5): `plain`,
`leading_zero`, `leading_plus`, `decimal`, `exponent_lower`,
`exponent_upper`; and `(withheld)`.

**`fraction_widths` keys** are the decimal spelling of a non-negative
integer — no sign, no leading zero unless the width is itself zero, no
space, no other character (`0`, `1`, `2`, `10`) — plus the pooled key
`(withheld)`, which is the only non-numeric key permitted.

### 14.8 The note grammar — 41 forms

Defined in 4.5.1, which is the authority on every rendering and every
argument. 62 argument positions: 53 whole numbers, 3 package words, 4
nested forms, 2 bound affix strings.

| # | form | arity |
|---|---|---|
| NG1 | `no_values_unrepresentable` | 0 |
| NG2 | `one_value_below_the_floor` | 1 |
| NG3 | `one_of_two_labels_below_the_floor` | 2 |
| NG4 | `labels_pooled_below_the_floor` | 3 |
| NG5 | `free_text_publishes_no_values` | 0 |
| NG6 | `identifier_publishes_no_values` | 0 |
| NG7 | `evidence_every_value_absent` | 0 |
| NG8 | `evidence_numbers_none_holdable` | 3 |
| NG9 | `evidence_one_value` | 1 |
| NG10 | `evidence_two_values` | 0 |
| NG11 | `evidence_dates` | 3 |
| NG12 | `evidence_counts_things` | 1 |
| NG13 | `evidence_written_as_numbers` | 2 |
| NG14 | `evidence_set_of_categories` | 3 |
| NG15 | `evidence_no_reading_fits` | 5 |
| NG16 | `evidence_declared_identifier` | 0 |
| NG17 | `said_written_as_numbers` | 2 |
| NG18 | `said_read_as_dates` | 2 |
| NG19 | `remark_values_out_of_range` | 1 |
| NG20 | `remark_values_contradictory` | 1 |
| NG21 | `remark_rare_sentinels_unnamed` | 1 |
| NG22 | `remark_too_few_holdable_numbers` | 2 |
| NG23 | `remark_two_values_differ_in_case` | 0 |
| NG24 | `remark_two_values_also_read_otherwise` | 0 |
| NG25 | `remark_dates_also_read_as_numbers` | 2 |
| NG26 | `remark_slashed_dates_are_month_first` | 0 |
| NG27 | `remark_values_differ_in_case` | 0 |
| NG28 | `remark_close_to_the_category_line` | 2 |
| NG29 | `remark_no_reading_fits` | 9 |
| NG30 | `remark_some_values_are_not_numbers` | 1 |
| NG31 | `remark_close_to_the_numeric_line` | 3 |
| NG32 | `remark_every_number_is_different` | 1 |
| NG33 | `remark_spread_out_of_range` | 0 |
| NG34 | `remark_every_value_is_different` | 1 |
| NG35 | `remark_affixed_numbers_may_be_codes` | 3 |
| NG36 | `remark_slashed_dates_read_against_your_declaration` | 5 |
| NG37 | `remark_a_label_is_a_built_in_stand_in` | 1 |
| NG38 | `header_names_because_you_said_so` | 0 |
| NG39 | `header_data_because_you_said_so` | 0 |
| NG40 | `header_names_by_convention` | 0 |
| NG41 | `header_names_shown_by_a_column` | 1 |

**The package-word vocabulary — 13**, the whole of the second argument
class (4.5.1): the eleven `format` members of 14.6, plus `day-first`
and `month-first`, the two reading names the slashed-date remark needs.
No other string is a word of this class, and membership alone does not
admit a word: a `format` member stands only at `evidence_dates`
argument 3 or `said_read_as_dates` argument 2, and `day-first` or
`month-first` only at
`remark_slashed_dates_read_against_your_declaration` argument 5.

The four sentence paths, and no other leaf of the document is a
sentence: `source.header_evidence`, `publication_notes[].note`,
`columns[].detection_evidence`, `columns[].remarks[]`. No rule binds a
form to one of those four paths.

### 14.9 The reserved tokens

**Where `(withheld)` appears — 6 places.**

| place | meaning |
|---|---|
| `missing_by_class` | the pooled count of absent-value CLASSES whose own counts fell below the floor |
| `sentinel_verdicts[].candidate` | the column is a nothing-publishing column, so no value of the table appears anywhere in its block |
| `utc_offsets` | the pooled count of cells whose OFFSETS fell below the floor |
| `earliest_utc_offset`, `latest_utc_offset` | that endpoint's offset is one the map is withholding |
| `numeric_styles` | the pooled count of cells whose spelling STYLE was used by too few rows to name |
| `fraction_widths` | the pooled count of `decimal`-styled cells whose fraction WIDTH was used by too few rows to name |

One token, one meaning: a group too small to name, counted rather than
named. It is never a value, and it is never a key a generator has to
invert. Every list it appears in draws its other keys from a fixed
first-party vocabulary — class words, offset texts, style names, width
digits — so there is no field of this format in which a value of
somebody's table and one of synthtwin's own words can land in the same
slot. A field added later that breaks that property breaks this
sentence.

**Where `(none)` appears — 2 places:** as a key of `utc_offsets`, and
as the value of `earliest_utc_offset` or `latest_utc_offset`. It means
the cell carried no offset at all.

**`(blank)`** is a key of `missing_by_class` and of nothing else.
`resolution_mix` carries no reserved key: it is floor-free and never
withholds.
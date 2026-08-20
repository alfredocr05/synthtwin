# Profile contract, version 6 — the normative specification

**Status:** revision 0, 2026-08-20 — written before any version 6 code
exists, under the ratified plan `docs/plans/phase-4-columns.md`, which
governs on every conflict. **Not ratified.** It is reviewed
adversarially before the implementation it anchors is written, under
the standing process: plans and specifications before the artifacts
they anchor. It joins the disposition seal at its own landing, making
the governing set seven documents.

**Authority.** The Phase 4 plan is the authority for every decision
here; this document is the normative statement of what a version 6
description may contain. Where the two disagree the plan governs and
this document is defective. The eight owner decisions of P4-D0 were
all taken on 2026-08-19, and amendments A-P4-1 through A-P4-4 are part
of the ratified text this document transcribes.

**What this document is for.** A version 6 description is a file some
person may hold, hand to a colleague, or keep for a year. This
document says exactly what may be in it, so a producer knows what to
write, a loader knows what to refuse, and a reader knows what a
sentence of it means without asking anybody.

**What this document is not.** It does not say how the twin is built —
that is `docs/spec/generation-method-v1.md` — nor how a written file is
checked against a description, which is
`docs/spec/validation-method-v1.md`. Each of those is amended at its
own stage against this one.

## 1. What changed from version 5, and why

**Read this section first. It is the whole story in plain words, and
nothing below it is a surprise if this section is understood.**

Version 5 could describe a column only if one of ten readings claimed
it. A column of prices, of clock times, of month-only dates, of one
ISO column mixing dates with date-times, or of category labels too
numerous for the categorical ceiling, matched none of them and became
free text — a role that publishes no value of the table at all. The
twin of such a column is invented from its shape statistics and
nothing else, which is meaningless filler where a researcher expected
data. Phase 4 exists to shrink that set, and version 6 is the wire
change that lets it.

Six changes, and each one is a column a person could not describe
before:

1. **Three new column kinds.** `affixed_number` reads a number wearing
   a symbol or a unit — a price, a percentage, a dose — and publishes
   a real distribution over the numbers with the affix recorded beside
   it. `time_of_day` reads a clock column. `long_tail_labels` gives a
   column past the categorical ceiling the same floor-governed level
   machinery a categorical column has, instead of nothing at all.
   Every one of them is tested AFTER the readings version 5 already
   had, so no column any earlier rule claims today changes what it is
   (plan P4-D3).
2. **Five new calendar readings.** A slashed year-leading date, a
   month-only form, a joint reading for the ISO family, and two
   slashed date-and-time forms. Each is an explicit member of the
   closed format vocabulary; none of them guesses.
3. **Two length facts** on the role for numbers no format can hold,
   settling a question Phase 2 left open for the owner, so the twin of
   such a column stops writing four-hundred-figure stand-ins for
   four-figure sources.
4. **A fixed-fraction spelling fact**, so a column written to two
   decimal places is described as being written that way, and its twin
   writes it that way too.
5. **Eight more words that mean "no value"**, and two dates that do:
   the spreadsheet error literals a machine writes when a formula
   fails, the absent-time literal one common tool writes, and the two
   calendar placeholders an administrative extract uses for "not
   known" and "still open".
6. **The twin reproduces the hole spellings the description already
   records.** Version 5 recorded which word a person called "missing";
   it stayed on the page. Now it is written into the twin, so code
   that names its own missing markers behaves on the twin as it will
   on the real table.

**What version 6 does not touch.** The relationship manifest is still
eight reserved slots, every one `null`, and a loader still refuses a
document that fills any of them: cross-column structure is Phase 5's
and no part of it arrives here. The categorical ceiling, the numeric
parse line, the small-cell floor and the identifier rule are all
unchanged. Identifier is still reached only by declaration. Nothing is
routed by the width of its text, and no column publishes a
distribution over part of itself.

## 2. Scope, authority, and how version 5 is carried

### 2.1 What this document governs

**2.1.1** It governs exactly one artifact: the description file
`<stem>-profile.json` written by `synthtwin profile` and read by
`synthtwin generate` and `synthtwin validate`. It does not govern the
plain-language summary beside it, the twin, the twin's report, or the
quality report.

**2.1.2** The ratified plan governs on conflict. Where this document
and `docs/plans/phase-4-columns.md` disagree, the plan is right and
this document is defective.

### 2.2 Version 5 is carried by reference, and this is the rule

**2.2.1** Every rule of `docs/spec/profile-contract-v5.md` — and,
through it, every rule of `docs/spec/profile-contract-v4.md` that
version 5 does not supersede — is a rule of version 6 at its own
wording and its own identifier, EXCEPT where a clause of this document
supersedes it by name. The inheritance is not exhaustive-listed here;
it is total, and the exceptions are the clauses below.

**2.2.2** A clause that supersedes names the rule it replaces. Where
the superseded rule is one of version 5's, the superseding clause
keeps that rule's letter and takes a `C6-` prefix — `C6-N3` supersedes
`C5-N3`, `C6-S13` supersedes `C5-S13`. Where the clause is new and
supersedes nothing, it is numbered plainly: `C6-1`, `C6-2`, and so on.

**2.2.3** The older documents are NEVER edited to change what version
6 requires. A change is written here, as a numbered clause naming what
it supersedes. Editing version 5 or version 4 instead is a defect,
because a person holding a version 5 description must be able to read
the rules that governed it, unchanged, for as long as they hold it.

**2.2.4** Precedence is by the document's own version integer. This
document governs a description whose `profile_version` is 6; version 5
governs one whose integer is 5; no description is governed by both.

### 2.3 Terms this document adds

Version 5's vocabulary is carried entire. Four terms are added:

| term | meaning |
|---|---|
| *the affix pair* | the exact prefix text and suffix text that every counted cell of an `affixed_number` column wears around its number |
| *the core* | the substring of an affixed cell that the number classifier reads as a number, chosen longest-then-leftmost |
| *a calendar placeholder* | one of the two built-in dates a description may judge as meaning "no value", by the same rule that judges the three stand-in numbers |
| *the exact-spelling member* | the one member of the published vocabulary matched by raw byte equality rather than after trimming and case folding |

## 3. The three new column kinds

Each is a role of the taxonomy, entering the closed role vocabulary in
the rule order the plan fixes, and each carries its full axis triple.

### 3.1 The rule order, and the invariant that makes it safe

**C6-1.** The role vocabulary gains exactly three members —
`affixed_number`, `time_of_day`, `long_tail_labels` — and the rule
order becomes: `empty`; declared `identifier`;
`numeric_unrepresentable`; `constant`; `binary`; `datetime`; `count`
or `continuous`; `categorical`; `time_of_day`; `affixed_number`;
`long_tail_labels`; `free_text`. The three new rules are tested after
`categorical`, so a column any earlier rule claims under version 5 is
claimed by the same rule under version 6.

**C6-2.** The empty rule settles before the declaration, unchanged: an
all-absent declared column carries role `empty` with
`structural_role` `identifier`, exactly as version 4's axis rules
already have it.

### 3.2 `affixed_number`

**C6-3 (what it is).** A column at least the parse-line count of whose
present cells are affixed numbers wearing ONE affix pair, where the
pair's cell count is at least `small_cell_floor`, and which no earlier
rule claimed. A cell is an affixed number when its trimmed text is
`prefix + core + suffix` with the core read as a holdable number by
the one shipped number classifier — unchanged, with its existing
acceptance of group separators, a leading plus and accounting
parentheses — and at least one of prefix and suffix non-empty. Where
more than one substring parses, the core is the LONGEST, and of
equal-length candidates the LEFTMOST: a total order, so the split is a
function of the cell and of nothing else.

**C6-4 (the pair's identity).** The pair is the EXACT text of the
trimmed cell on either side of the core — no case folding, no inner
trimming. A column whose cells wear more than one pair past the parse
line's slack does not take this role.

**C6-5 (added keys).** A block of this role carries, beside every
universal key: `affix_prefix` and `affix_suffix` (each a string,
possibly empty, and not both empty); `n_affixed` (integer ≥ 0, how
many present cells wore the pair); and the complete quantitative key
set of a `count`/`continuous` block computed over the CORES —
`percentiles`, `mean`, `std`, `skew`, `std_unrepresentable`, `n_zero`,
`n_negative`, `n_negative_unrepresentable`, `n_used_in_statistics`,
`n_left_out_of_statistics`, `numeric_share`, `integer_valued`,
`n_rows`, `numeric_styles`.

**C6-6 (invariants).** AF1: `affix_prefix` and `affix_suffix` are not
both the empty string. AF2: `n_affixed ≤ n_present`, and
`n_affixed ≥ small_cell_floor`. AF3: `integer_valued` is a fact about
the cores and is what a consumer routes on, never the role name. AF4:
every quantitative key of C6-5 obeys the invariant version 4 gives it
on `count`/`continuous`, read over the cores.

**C6-7 (publication class).** `affixed_number` is a RANGES-class role.
The ranges class's "no spelling appears" sentence gains ONE named
exception, confined by the forbidden-key matrix to exactly two keys:
`affix_prefix` and `affix_suffix` carry shared affix text, governed by
the floor through C6-3's detection rule. No other key of any
ranges-class role may carry a spelling, and neither the labels class
nor the nothing class is touched.

### 3.3 `time_of_day`

**C6-8 (what it is).** A column at least the parse-line count of whose
present cells match ONE of exactly two clock forms — `HH:MM` or
`HH:MM:SS`, two-digit fields, hours 00–23, minutes 00–59, seconds
00–59 — and which no earlier rule claimed. Cells of the other form,
and every other unreadable cell inside the line's slack, are counted
in `n_unparsed`. There is no joint clock reading: a column neither
form alone carries declines to the later rules. Fractional seconds, a
leap second, and single-digit hours do not parse.

**C6-9 (added keys).** `clock_form` (one of `hh-mm`, `hh-mm-ss`);
`earliest` and `latest` (each a clock value written in the column's
own form); `clock_percentiles` (an eleven-rung ladder of clock values
in the ladder's fixed rung order); `n_unparsed` (integer ≥ 0).

**C6-10 (invariants).** T1: every published clock value is written in
the form `clock_form` names. T2: the ladder's first rung equals
`earliest` and its last rung equals `latest`. T3: the ladder is
non-decreasing in seconds-of-day. T4: `n_unparsed < n_present`. T2 and
T3 are stated because the generation rule rests on them, and are the
analogue of the datetime rules that pin its ladder.

**C6-11 (the model, stated where the fact carries it).** The ladder
reads the day as a LINE from `00:00` to `23:59:59`, as every ladder
reads its axis. A column whose values cluster across midnight is
therefore described as two edge clusters with an empty middle, and a
twin's interior interpolation fills that middle. The rungs are exact
values of real cells either way; the clock face's circular reading is
not modeled, exactly as a two-humped numeric column's valley is not.

**C6-12 (publication class).** Ranges. No exception of its own.

### 3.4 `long_tail_labels`

**C6-13 (what it is).** A column past the categorical ceiling, no
earlier rule having claimed it, at least one of whose folded levels
covers `max(small_cell_floor, long_tail_minimum_level)` rows. A column
past the ceiling with no such level stays `free_text` and publishes
what it publishes today.

**C6-14 (added keys).** Exactly the four shared label keys, under the
shared label invariants B1 through B8 verbatim: `levels` (each entry
with `label`, `count`, `variants`, `variants_withheld`),
`suppressed_levels`, `suppressed_rows`, `suppressed_level_counts`.

**C6-15 (the forbidden key, named so no ambiguity survives).**
`level_ceiling` is FORBIDDEN on this role. It is the categorical
role's own key, its invariant is that folded distinctness is at or
under the ceiling, and that is exactly what a long-tail column
violates by definition. The format has no optional keys, so the key is
absent rather than sometimes-present; the ceiling the column passed is
recorded in its `detection_evidence` sentence.

**C6-16 (publication class).** Labels. Its published spellings are
whole values of the table under the same floor as every label.

### 3.5 The axes, and the settings the new rules read

**C6-17 (axes).** The role-to-`statistical_type` table gains three
rows, each new role naming itself. Every new role carries
`quality_state` `ok` and `structural_role` `data`; a declaration still
forces `structural_role` `identifier`, winning immediately after the
empty rule settles. The table stays total over the role vocabulary and
a loader refuses any triple that is not a row of it.

**C6-18 (settings).** The settings block holds EXACTLY seventeen keys:
version 5's fifteen, plus `day_first` (a yes/no, default no, recording
that slashed dates were read day-first-preferring) and
`long_tail_minimum_level`. The ONLY permitted value of
`long_tail_minimum_level` in version 6 is the integer 11, on the
`declaration_matching` only-value precedent; a loader refuses any
other. The key exists so the detection line of C6-13 is recorded on
the document's own face, and so that a later phase can move it only in
the open, by a contract change. No settings key is added for the affix
rule, the clock rule or the calendar-placeholder pass: they reuse
`minimum_parse_rate`, `small_cell_floor`,
`sentinel_outlier_iqr_multiple` and `sentinel_minimum_share`.

## 4. New facts on the readings version 5 already had

### 4.1 The calendar vocabulary

**C6-19 (five new format members).** The closed `format` vocabulary
grows from six members to ELEVEN. The five added, with their exact
wire spellings and their resolution bindings:

| member | reads | `resolution` |
|---|---|---|
| `slashed-iso-date` | `YYYY/MM/DD`, fields padded | `date` |
| `iso-month` | `YYYY-MM` | `month` |
| `iso-mixed` | the joint ISO family reading of C6-21 | `datetime` |
| `month-first-datetime` | a slashed month-first date, one space, a clock in a form of C6-8 | `datetime` |
| `day-first-datetime` | a slashed day-first date, one space, a clock in a form of C6-8 | `datetime` |

**C6-20 (the unpadded widening).** Exactly four families accept one-
or two-digit month and day fields: `month-first-date`,
`day-first-date`, `month-first-datetime` and `day-first-datetime`.
Their grammar is a one- or two-digit month and day, a four-digit year,
and the slash delimiter. `slashed-iso-date` stays fully padded and
`compact-date` stays exactly eight digits, so no family overlaps
another.

**C6-21 (the joint ISO reading).** The single-format pass runs first
and its verdict stands wherever it clears. Only where NO single format
clears the parse line does the joint test run: where `iso-date` and
`iso-datetime` cells TOGETHER reach the line, the column is one
datetime column at the family's finest resolution, with `format`
`iso-mixed`.

**C6-22 (the month resolution).** The `resolution` vocabulary gains
`month`, with canonical form `YYYY-MM`, which sorts as text. The
sibling `time_precision` vocabulary gains `month` with it; the two
move together, as the quarter precedent has them.

**C6-23 (`resolution_mix`).** Every datetime block carries
`resolution_mix`, a mapping from format-member strings to integer
counts. Its permitted key sets are closed: on a single-format column,
exactly one key — the column's own `format` member — carrying the full
parsed count; on an `iso-mixed` column, exactly the two members
`iso-date` and `iso-datetime`. No other key set conforms. The counts
are exact and no floor governs them: with a two-member space beside
the published parsed total, a pooled remainder is recoverable by
subtraction, so a floor would withhold nothing, and the fact is what
it is — a form-shape count carrying no value of the table. Its
disposition is REPORT-ONLY (§9).

### 4.2 Lengths on `numeric_unrepresentable`

**C6-24.** A block of this role carries `min_length` and `max_length`,
each an integer ≥ 1, over its NUMERIC-LOOKING cells only — not over
the whole present population, because the role tolerates a slack of
non-numeric stragglers whose lengths are facts about text rather than
about the numbers this role exists for. Invariant U5:
`min_length ≤ max_length`. This settles residual R-P2-1, open for the
owner since Phase 2.

### 4.3 The fixed-fraction spelling fact

**C6-25.** The `numeric_styles` block of a `count`, `continuous` or
`affixed_number` column carries `fraction_widths`, a mapping from a
fraction width — the count of digits after the point, written as
decimal text — to the number of `decimal`-styled cells written at that
width, together with the pooled key `(withheld)` for widths fewer than
`small_cell_floor` cells share. Invariant P5: the values of
`fraction_widths` sum to the `decimal` count of `numeric_styles`. P6:
every named width's count is at or above the floor, and the
`(withheld)` value is 0 or at least 1. This closes the route residual
R-P3-12 records.

## 5. Absent cells: the vocabulary, the classes, the placeholders

### 5.1 The published vocabulary

**C6-26 (supersedes C5-15).** The published vocabulary is a closed
list of THREE parts, and its size is stated here because every surface
that counts it must count the same number:

- **Eighteen text spellings** read as "no value". The ten version 5
  fixed, matched after trimming and a Unicode case fold; SEVEN
  spreadsheet error literals — `#DIV/0!`, `#N/A`, `#NAME?`, `#NULL!`,
  `#NUM!`, `#REF!`, `#VALUE!` — matched the same folded way; and ONE
  exact-spelling member, `NaT`, matched by raw byte equality with the
  cell, with no trimming and no case folding.
- **Three stand-in numbers**, unchanged: −9999, −999, 9999.
- **Two calendar placeholders**: `1900-01-01` and `9999-12-31`.

Twenty-three members in all. Extending any of the three parts is a
change to this contract and advances `profile_version`.

**C6-27 (why one member is matched differently, stated because a
difference in a matching rule is the kind of thing a reader must not
have to infer).** Every folded member's folded form collides with no
human word. `NaT`'s does: folded, it is a person's name, so admitting
it under the folded rule would silently read name cells as absent. It
therefore joins as the vocabulary's one exact-spelling member, and
that one operation — raw byte equality — is applied identically
wherever the vocabulary is consulted: missing recognition, declaration
recording, the published-vocabulary tests, and the validator's
reconstruction. The criterion that keeps `unknown` and `missing` out —
a human word carries meaning somewhere — stands unweakened for every
folded member.

### 5.2 The absence classes

**C6-N3 (supersedes C5-12 and version 4's N1 and N2).**
`missing_by_class` carries SIX keys, always all six, on every column
block of every role: `(blank)`, `(date-sentinel)`,
`(declared-missing)`, `(numeric-sentinel)`, `(text-code)`,
`(withheld)`. Their six values sum to `n_missing`. Each value other
than `(withheld)` is 0 or at least `small_cell_floor`.

### 5.3 The calendar placeholders, judged

**C6-28 (identity).** A cell matches a placeholder when its own
WRITTEN fields, under the column's own format, denote that calendar
day. No shared-clock normalization and no offset arithmetic enters the
question: a placeholder is a writing convention, and the writer typed
that day.

**C6-29 (the pass, and when it does not run).** Placeholders are
judged by the standing outlier-and-share rule transposed to day
ordinals over the written days, reusing
`sentinel_outlier_iqr_multiple` and `sentinel_minimum_share`. The pass
runs only after the first five rules have declined the un-removed
column, and it ENTERS only when the non-candidate remainder itself
clears the datetime rule's parse line. Otherwise no cell is judged, no
cell is removed, and the column lands exactly where the rules without
this pass put it — so a constant or binary column keeps its claim, and
an existing datetime column can never fall out of its role by this
pass.

**C6-30 (verdicts).** A judged placeholder publishes through the
standing verdict machinery: a `sentinel_verdicts` entry whose
`candidate` is the placeholder's canonical ISO day spelling, reusing
the standing `verdict` and `reason` enumerations and the standing
withholding on nothing-publishing columns. **C6-V4 (supersedes V4):**
where a block carries both numeric and calendar candidates, entries
are ordered by their candidate text.

### 5.4 The declaration records

**C6-31 (supersedes C5-16's two-list shape).** Each of
`settings.kept_values` and `settings.declared_missing_values` carries
a THIRD list, `built_in_dates`, of the same shape and identity rules
as `built_in_numbers`: an array, always present and possibly empty,
every element a member of C6-26's placeholder part, sorted, pairwise
distinct, LOADER-ONLY. **C6-K5 (supersedes C5-K4's count identity):**
in each record, the three list lengths sum to at most `n_declared`.

## 6. The twin reproduces the recorded hole spellings

**C6-9R — the clause that supersedes C5-9.** Version 5 stated that the
twin writes every absent cell as an empty field and that no
absent-value spelling is reproduced in any twin. That is no longer
true of the file the tree produces, and this clause replaces it. A
version 6 twin writes, per column, in one rule:

1. each `missing_by_source` spelling at exactly its published count,
   EXCEPT a spelling that reads as one of the three stand-in numbers,
   which stays blank;
2. every other absent cell — the blank count, the withheld remainder,
   and any stand-in-sourced cell — empty;
3. all of them placed by the same single permutation that places
   everything else, with spellings assigned to absent slots in a fixed
   sorted order before the permutation.

**C6-32 (why stand-in-sourced cells stay blank).** A reproduced TEXT
spelling is read back as absence by a fixed rule of the description
alone. A stand-in NUMBER is that rule's named exclusion: its absence
reading runs through the producer's outlier-and-share judgement over
the measured file's own values, which a twin's generated distribution
is not guaranteed to re-fire. Reproducing those cells would make the
green battery contingent on a re-judgement; leaving them blank keeps
every reproduced cell's reading deterministic. Nothing is lost that
the description records: the twin's report names, per column, the
stand-in cells and below-floor spellings that were not reproduced.

**C6-33 (the collision rule, with no runtime escape).** No PRESENT
cell of a twin may wear a spelling the description publishes as a hole
source for its column. The generation method's amendment carries the
written proof that no construction is ever forced onto one; a shape
outside that proof is a defect of the method, found at review, and
never a deviation printed at run time.

## 7. What version 6 does NOT close

**This section is normative and may not be softened.**

**C6-34.** Version 5's two permanently-open reading-rule routes are
unchanged and unclosable by any version of this format: a word of the
person's own that fewer than `small_cell_floor` cells of every column
share, which the floor pools unnamed; and a word of the person's own
on a column whose publication class permits no value of the table.
Version 6 reproduces what is recorded; it does not record more of
these.

**C6-35.** A column no reading claims is still `free_text`, still
publishes no value of the table, and its twin is still invention. The
set is smaller than version 5's and the surfaces now say so loudly,
which is a reporting obligation and not a fidelity one.

**C6-36.** The `relationships` manifest is still eight `null` slots
and a loader still refuses a document that fills any of them. No
cross-column fact enters this version.

## 8. Every new and changed key, in one table

| key | where | JSON type | meaning | disposition |
|---|---|---|---|---|
| `affix_prefix` | `affixed_number` block | string | the shared prefix text | EXACT-OBSERVABLE |
| `affix_suffix` | `affixed_number` block | string | the shared suffix text | EXACT-OBSERVABLE |
| `n_affixed` | `affixed_number` block | integer | present cells wearing the pair | EXACT-OBSERVABLE |
| the quantitative set of C6-5 | `affixed_number` block | as on `count` | computed over the cores | as on `count` |
| `clock_form` | `time_of_day` block | string | `hh-mm` or `hh-mm-ss` | EXACT-CONTROL |
| `earliest`, `latest` | `time_of_day` block | string | the two end clock values | EXACT-OBSERVABLE |
| `clock_percentiles` | `time_of_day` block | array of 11 strings | the ordinal ladder | ends EXACT-OBSERVABLE, interior APPROXIMATED |
| `n_unparsed` | `time_of_day` block | integer | cells that did not read as clocks | EXACT-OBSERVABLE |
| the four label keys of C6-14 | `long_tail_labels` block | as on `categorical` | published levels and the held-back tail | EXACT-OBSERVABLE |
| `min_length`, `max_length` | `numeric_unrepresentable` block | integer | over numeric-looking cells | EXACT-OBSERVABLE |
| `fraction_widths` | `numeric_styles` | object | width → cell count, floored | EXACT-OBSERVABLE |
| `resolution_mix` | every `datetime` block | object | form → parsed cell count | REPORT-ONLY |
| `(date-sentinel)` | `missing_by_class` | integer | cells read absent as a placeholder | REPORT-ONLY |
| `built_in_dates` | both declaration records | array of strings | which placeholders a declaration named | LOADER-ONLY |
| `day_first` | `settings` | boolean | slashed dates read day-first-preferring | LOADER-ONLY |
| `long_tail_minimum_level` | `settings` | integer, only 11 | the long-tail detection line | LOADER-ONLY |

**Nothing is removed.** Every key of version 5 is a key of version 6.

**What a version 5 consumer must do.** Refuse. A version 6 document
carries keys and vocabulary members version 5's rules do not admit,
and a strict version 5 loader correctly refuses it. There is no
partial reading and none is offered.

## 9. Every new and changed invariant, in one checkable list

| id | supersedes | statement |
|---|---|---|
| AF1 | — | `affix_prefix` and `affix_suffix` are not both empty |
| AF2 | — | `small_cell_floor ≤ n_affixed ≤ n_present` |
| AF3 | — | `integer_valued` is the routing fact, computed over cores |
| AF4 | — | every quantitative key obeys its `count` invariant over cores |
| T1 | — | every published clock value is written in `clock_form` |
| T2 | — | `clock_percentiles` first rung is `earliest`, last is `latest` |
| T3 | — | `clock_percentiles` is non-decreasing in seconds of day |
| T4 | — | `n_unparsed < n_present` |
| U5 | — | `min_length ≤ max_length` on `numeric_unrepresentable` |
| P5 | — | `fraction_widths` values sum to the `decimal` style count |
| P6 | — | every named fraction width is at or above the floor |
| RM1 | — | `resolution_mix` keys are exactly the set C6-23 permits |
| RM2 | — | `resolution_mix` values sum to `n_present − n_unparsed` |
| C6-N3 | C5-12, N1, N2 | six absence classes, always all six, summing to `n_missing`, each non-withheld value 0 or ≥ floor |
| C6-V4 | V4 | mixed candidates are ordered by candidate text |
| C6-K5 | C5-K4 | the three declaration lists sum to at most `n_declared` |
| C6-S13 | C5-S13 | at a floor of one nothing is held back: the floor-one list gains `fraction_widths`, `resolution_mix` excepted as floor-free |
| G1L | — | `long_tail_labels` carries no `level_ceiling` |
| A5 | — | the axes table is total over the twelve roles |

## 10. The version rule and the refusal

### 10.1 The rule

**C6-37.** `profile_version` is the integer 6. The producer writes 6;
the loader reads exactly 6 and refuses every other integer. The
version is read before the canonical round trip, exactly where version
5 reads it, so a person is given direction-correct advice rather than
a complaint about canonical form.

**C6-38 (fail-closed, no upgrade).** The loader does not upgrade a
version 5 document, does not partially accept one, and does not offer
to. Converting one would mean making up facts the older rules never held.

### 10.2 The refusal, and the analysis its advice rests on

**C6-39.** The older-version refusal keeps the shape version 5 fixed
for it and names EVERY option of `synthtwin profile` that changes what
a description publishes. That set gains `--day-first`, which changes
how slashed dates are read and therefore what the description says, so
it joins the sentence and its priced list. A test derives that set
from the shipped parser, so an option added later and not named here
turns the suite red.

**C6-40 (the pre-release analysis, re-examined as version 5 required
and answered by fact).** Version 5 declared its "describe the table
again" advice safe only while no release existed, and required the
wording to be re-examined rather than inherited once one did. It has
been re-examined, and the fact settles it: **no release exists.**
Phase 3 was closed by owner act on 2026-08-19 without its release —
there is no tag and nothing is published — so every holder of a
description is still someone who holds the table it was made from, and
the advice remains safe on exactly the ground version 5 stated. This
clause is the record that the question was asked, not skipped. It is
also a standing obligation: the first release makes this analysis
false, and whichever version is current then owes a new one.

## 11. The disposition matrix, delta only

Version 5's section 11 and version 4's section 9 are carried entire.
These rows change or are added; every other row is unchanged.

| fact | version 5 | version 6 | why |
|---|---|---|---|
| `missing_by_source` | REPORT-ONLY | **EXACT-OBSERVABLE**, per-spelling recount, stand-in-spelled keys excepted | the twin now writes those spellings (C6-9R) |
| `n_missing_blank`, `n_missing_withheld` | REPORT-ONLY | REPORT-ONLY, bound by a stated SUM identity | the twin's recounted blank absent cells equal blank + withheld + stand-in-sourced; a per-field equality would be false by construction |
| `missing_by_class` | REPORT-ONLY | REPORT-ONLY, unchanged | its classes are not recoverable from bytes |
| every key of §8 not named above | — | as §8 states | new facts, one class each |

The completeness assertion holds: every key a producer emits has
exactly one disposition in these documents read together, and no
exception may be acquired during implementation.

## 12. The disclosure delta, in one place

What version 6 publishes that version 5 withheld, each row priced.

1. **Long-tail levels.** Floor-cleared label spellings from columns
   that publish no value today. Bounded by the floor exactly as every
   label is; the detection line never drops below eleven rows, so a
   lowered floor cannot make a new column label-publishing.
2. **The affix pair.** Two shared cell fragments per affected column,
   floor-governed by C6-3's detection rule, under the named
   ranges-class exception.
3. **The affixed-core quantitative block, as one grouped row.** Mean,
   standard deviation, skewness, the sign and zero counts, the
   whole-number fact, the styles block with its fraction widths, and
   the affixed-cell count — each under the treatment the same fact has
   on a plain numeric column, all of it new for columns that were free
   text.
4. **Core endpoints and ladder rungs of affixed columns**, and
   **clock endpoints and rungs of time-of-day columns** — exact values
   of real cells, published floor-free under the ratified ranges-class
   endpoint policy, newly reaching columns that were free text.
5. **Month and joint-ISO endpoints**, likewise, for columns those
   readings newly claim.
6. **The two unrepresentable lengths.** For decimal numerals length
   bounds magnitude, so `max_length` states the largest withheld
   numeral's order of magnitude: one cell's worth of floor-free fact.
7. **The fraction widths**, floor-governed with a pooled remainder.
8. **The exact resolution-mix counts**, floor-free with the
   subtraction argument of C6-23 stating why a floor would withhold
   nothing.
9. **The twin as a carrier of published hole spellings.** A person's
   own marker word, already published in the description under the
   floor, is now written into the twin as well.

Each row is named in `SECURITY.md` and in the profiler's own summary,
where a person meets it.

## 13. Decisions this contract took

**13.1** The three new roles are tested after `categorical` rather
than at the position their specificity might suggest, so that no
column any earlier rule claims changes what it is. Fidelity for
unclaimed columns is worth less than stability for claimed ones.

**13.2** `affixed_number` is a ranges-class role with a named
two-key exception rather than a fourth publication class. A fourth
class would have to be given a meaning everywhere the three are
enforced; an exception is confined by the forbidden-key matrix.

**13.3** `resolution_mix` is REPORT-ONLY. Reproducing a form mix would
need a per-form construction with its own packing, feasibility rule
and window family, for one reading — cost out of proportion to a fact
the reader still receives. The twin writes the finest recorded form
and the report says the mix was recorded and not kept, on the
precedent of the `format` fact itself.

**13.4** `long_tail_minimum_level` has one permitted value rather than
a range. The line it records is a privacy boundary; a settings key
that could move it downward would let a settings combination widen
which columns publish labels, which is exactly what C6-13's `max`
exists to prevent.

**13.5** `NaT` joins as an exact-spelling member rather than being
excluded. Excluding it left a common absent-time literal reading as
data; admitting it under the folded rule would read a person's name as
absent. The third option — one stated exception to the matching rule —
costs a reader one more sentence and loses nothing.

**13.6** Stand-in-sourced absent cells are not reproduced. Their
absence reading is not deterministic from the description alone, and a
reproduction whose correctness depends on a re-judgement is worse than
a blank cell with a sentence naming what was not carried.

## 14. Enumerations added and changed

**Roles (12):** `empty`, `numeric_unrepresentable`, `constant`,
`binary`, `datetime`, `count`, `continuous`, `categorical`,
`identifier`, `affixed_number`, `time_of_day`, `long_tail_labels`,
`free_text` — tested in the order C6-1 fixes.

**`statistical_type` (12):** version 5's, plus `affixed_number`,
`time_of_day`, `long_tail_labels`.

**`format` (11):** `iso-date`, `iso-datetime`, `compact-date`,
`month-first-date`, `day-first-date`, `year-quarter`,
`slashed-iso-date`, `iso-month`, `iso-mixed`, `month-first-datetime`,
`day-first-datetime`.

**`resolution` (4):** `date`, `datetime`, `quarter`, `month`.

**`time_precision` (6):** `subsecond`, `second`, `minute`, `date`,
`quarter`, `month`.

**`clock_form` (2):** `hh-mm`, `hh-mm-ss`.

**Absence classes (6):** `(blank)`, `(date-sentinel)`,
`(declared-missing)`, `(numeric-sentinel)`, `(text-code)`,
`(withheld)`.

**The published vocabulary (23):** eighteen text spellings — the ten
of version 5 and the seven spreadsheet error literals, all folded, and
`NaT`, exact; three stand-in numbers; two calendar placeholders.

## Review record

- **Specification reviews (this document):** pending; recorded here
  round by round as
  `docs/plans/reviews/phase-4-contract-v6-review-round-N.md`.

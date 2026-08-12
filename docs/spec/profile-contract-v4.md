# Profile contract, version 4 — the normative specification

**Status:** the second of the four Phase 2 artifacts named in
`docs/plans/phase-2-generator.md` (revision 5), sequencing section. It
carries out the decisions that plan ratified and introduces no mechanism
the plan left open. Where the plan fixed a fact but not its exact wire
shape, this document fixes the shape and says so, in section 13, so a
reviewer can see every place a shape was chosen here rather than
inherited.

**What this document is for.** A strict loader and a generator must both
be writable from this text alone, without reading the producer's source
and without guessing. Every key that may appear in a version 4 profile is
named here with its type, its permitted values, what a null means, which
keys may not appear beside it, and which invariants bind it. Every rule a
loader enforces is stated in a form that can be checked mechanically.

**What this document is not.** It does not say how the twin's values are
computed. The transform from (profile, seed) to twin bytes is
`docs/spec/generation-method-v1.md`, the third artifact, together with
its frozen neutral reference vectors. This contract says what the
generator is given and what it owes; the method specification says how it
discharges that debt.

**Relationship to version 3.** Version 3 is the shipped producer's
format. Version 4 is version 3 plus five additions and no removals; every
version 3 key keeps its name, its type and its meaning. Section 12 lists
the change set and says what a version 3 consumer must do.

---

## 1. Scope, authority, and reading order

1.1 This contract governs one artifact: the machine-readable profile
document, written by `synthtwin profile` as `<stem>-profile.json` and
read by `synthtwin generate`. It does not govern the human-readable
profile summary `<stem>-profile.txt`, the twin CSV, or the generation
report.

1.2 The profile document is the ONLY input the generator receives about
the real table. The generator never opens the real table, and no rule in
this contract may be satisfied by consulting anything but the profile and
the seed (plan P2-D1).

1.3 Where this contract and the Phase 2 plan disagree on a fact the plan
decided, the plan governs and this document is defective. Where the plan
names a fact without fixing its shape, this document governs.

1.4 **Exactly two parser bounds exist**: nesting depth and numeric token
length, section 10.3. Revision 5 of the plan removed the container-entry
limit (its item P2-R5-F7) and ruled that two remain. Three passages of
the plan's prose still carried the earlier count of four, which was true
of plan revisions 3 and 4; all three were corrected under code review
item P2-C1-F8, so the plan and this contract now say two in every place
and a reader has no count to reconcile. This is not a contract decision;
it is the plan's own revision-5 ruling applied consistently.

---

## 2. Terms, and how to read this document

### 2.1 Normative words

| word | meaning |
|---|---|
| MUST / MUST NOT | a conforming producer always does this; a conforming loader refuses a document that does not |
| REQUIRED | the key is present in every block of that kind, on every run |
| FORBIDDEN | the key is absent from every block of that kind; a loader refuses a document carrying it |
| OPTIONAL | not used in this contract — there are no optional keys in version 4 |

There are no optional keys on purpose. A key that appears only sometimes
is a key a consumer comes to guess about, and the guess is what fails
silently. Every key listed for a role is present on every column of that
role, including when its content is empty.

### 2.2 The six disposition classes

The disposition class of a field says what the twin owes it. The classes
are the plan's (P2-D6); they are reproduced here because the loader and
the generator are both written against them.

| class | what it means | how it is evidenced |
|---|---|---|
| **EXACT-OBSERVABLE** | the twin reproduces the published value exactly | recounted from the written twin CSV, independently of the generator's own bookkeeping |
| **EXACT-CONTROL** | a metadata or dispatch decision a CSV cannot evidence | typed-object or schema-order assertions, plus a misrouting mutant that must fail |
| **APPROXIMATED** | reproduced under a stated rule inside a two-sided finite-sample bound | measured, checked against both sides of the bound, and named in the generation report with the achieved value beside the published one |
| **REPORT-ONLY** | not reproduced in the twin at all; stated in the generation report | asserted present in the report |
| **LOADER-ONLY** | validated on input; never an output obligation | asserted to impose no output obligation |
| **STRUCTURAL** | a container whose own key carries no VALUE obligation, but which carries membership and order obligations | membership and order asserted; swapped, duplicate, omitted and extra member mutations must each fail |

A field has exactly one disposition. A container's disposition does not
cover its leaves: every leaf under a STRUCTURAL container is disposed
individually (section 9).

### 2.3 The vocabulary of the counts

| term | definition |
|---|---|
| **present** | a cell that survived the absent-value rules and the declarations; `n_present` counts them |
| **absent** | a cell counted as holding no value, for any of the five recorded reasons; `n_missing` counts them |
| **raw identity** | a present cell's text exactly as the file spells it. `n_distinct` counts raw identities |
| **folded identity** | a present cell's text after trimming and a Unicode `casefold()`. `n_distinct_folded` counts folded identities, and every published label is a folded identity |
| **the floor** | `settings.small_cell_floor`, the smallest number of rows a published group may cover. Its value is in the document; it is never below 11 |
| **withheld** | held back by the floor and pooled into a counted remainder, never named |
| **the ladder** | the fixed eleven rungs `min`, `p01`, `p05`, `p10`, `p25`, `p50`, `p75`, `p90`, `p95`, `p99`, `max`, in that order |

**Equality per path** (plan P2-D6). `n_distinct` counts RAW present
spellings. `n_distinct_folded` counts FOLDED identities. Numeric
statistics describe PARSED values. Level facts use the FOLDED identity.
Datetime facts use the parsed instant at the recorded resolution. A
conforming implementation never swaps one notion of equality for
another, in either direction.

---

## 3. Encoding and canonical serialization

3.1 The document is a single JSON value: an object. The file is UTF-8
text with LF line endings, no byte-order mark, and exactly one terminal
newline.

3.2 **The canonical text of a document is defined by construction**: it
is what `json.dumps` produces with `sort_keys=True`, `indent=2`,
`separators=(",", ": ")`, `ensure_ascii=False` and `allow_nan=False`,
followed by one newline character. That fixes, normatively:

- every object's keys appear in ascending order of their code points;
- nesting is indented by two spaces per level;
- the separator between members is `,` followed by the newline the indent
  mode inserts; the separator between a key and its value is `: `;
- non-ASCII characters are written as themselves, not as `\u` escapes;
- `NaN`, `Infinity` and `-Infinity` are not writable, so they cannot
  appear in a canonical document;
- numbers are written by the grammar of 3.2.1, which has two cases and
  turns on the KIND of number, not on whether the number happens to be
  whole.

**3.2.1 The canonical number grammar** (review item P2-C1-F8). Earlier
revisions gave one sentence here — shortest form, and a whole number
without a point or an exponent — and that sentence is not a grammar an
independent loader can apply. Read one way it says a whole-VALUED number
is written `2`, and a loader following it refuses a shipped profile
whose `mean` reads `2.0`, which the serializer of section 3.2 writes and
this contract's own T1 (section 10.5) depends on. The old wording is
described rather than repeated, so that a test can ban it outright. The
grammar is therefore stated exactly, in the two cases the serializer
has:

- **A number of INTEGER kind** — the kind every field this contract
  types "integer" carries — is written as the base-ten digits of its
  value, with a leading `-` when negative, and nothing else: no
  fractional part, no exponent, no leading zero, no leading `+`.
- **A number of FLOAT kind** — the kind a field typed "number" may
  carry, and the only kind `mean`, `std`, `skew`, a `percentiles` rung
  and the `length`/`words` statistics take when their value is not
  whole — is written as the shortest decimal digit string that reads
  back as exactly the same binary64 value (shortest first, then
  nearest, ties to the even significand), laid out by the position
  `decpt` of the decimal point relative to those digits: fixed-point
  notation when `-4 < decpt <= 16`, with `.0` appended where no
  fractional digit would otherwise be written; and otherwise
  `d[.ddd]e±XX` with a lower-case `e`, the exponent sign always
  written, and at least two exponent digits.

So `2.0` is the canonical text of the float two — `2` is the canonical
text of the INTEGER two, and they are different documents — and
`1e+16`, `1000000000000000.0`, `0.0001`, `1e-05` and `-2.5` are all
canonical. A number spelling that is not the shortest round trip of its
own value, such as `1.0e2`, is not canonical and section 10.4 catches
it. A spelling JSON has no grammar for at all, such as `+5` or `05`,
stops the parse at step 4 of section 10.1 (R5) and never reaches the
round trip.

**The float case is the same grammar the twin's own numeric cells use**
(`docs/spec/generation-method-v1.md` G6.2), deliberately and not by
coincidence: one rule for "the shortest text that reads back as this
binary64" is one rule an implementer has to get right, and the two
documents are checked against each other by a test.

3.3 A document is CANONICAL when its bytes equal the canonical text of
the value it parses to. Section 10.4 makes this the loader's first
semantic check and says what it catches.

3.4 The maximum nesting depth of a conforming version 4 document is
**six**: document → `columns` → a column block → `levels` → a level entry
→ `variants`. Depth is a function of the contract's shape, not of the
data, so no table can raise it.

---

## 4. The document: top-level structure

### 4.1 Every top-level key

Exactly these nine keys are present. No other top-level key may appear;
a loader refuses one that does, naming it.

| key | JSON type | meaning | disposition |
|---|---|---|---|
| `columns` | array of objects | one block per column of the table, in schema order | **STRUCTURAL** |
| `created_with` | string | the synthtwin version that wrote this document, or `0+unknown` when the installed version could not be read | LOADER-ONLY |
| `n_columns` | integer ≥ 1 | how many columns the table has | EXACT-OBSERVABLE |
| `n_rows` | integer ≥ 0 | how many data rows the table has, not counting a header row | EXACT-OBSERVABLE |
| `profile_version` | integer | the contract version. In this contract, exactly `4` | LOADER-ONLY |
| `publication_notes` | array of objects | per-column plain-language notes about what was held back and why | LOADER-ONLY |
| `relationships` | object | the reserved cross-column manifest; eight keys, every one `null` | LOADER-ONLY |
| `settings` | object | the rules that produced this profile | LOADER-ONLY |
| `source` | object | how the table was read | **STRUCTURAL** |

`settings`, `publication_notes` and `relationships` each carry ONE
disposition covering their whole subtree, because nothing under them is
an output obligation. Their membership rules are still stated below,
because a strict loader enforces them.

### 4.2 STRUCTURAL rules for `columns`

These four rules are the whole of what `columns` means as a container.
They are normative, and each has a mutation that must fail (plan P2-D6,
item P2-R5-F6).

**S1 — length.** `len(columns) == n_columns`.

**S2 — position.** For every index `i` counting from zero,
`columns[i].position == i + 1`. Positions therefore form exactly the set
`1..n_columns`, each once, in increasing order along the list.

**S3 — list order is the schema.** The order of `columns` IS:

- the schema order of the table;
- the order in which the twin's columns are written to the CSV, left to
  right, and the order of the header row when one is written;
- the order in which the single RNG stream is consumed — the column at
  index 0 takes its draws first, and every later column's draws follow
  the ones before it.

Without S3, two conforming implementations could serialize the blocks in
different order and route names, type paths, values and RNG bytes
differently while every set-shaped invariant still passed.

**S4 — names.** Column names are non-empty after trimming and are
pairwise distinct as text. Two names that differ only in case, or only in
surrounding spaces, are distinct names and both are kept exactly as
written. A loader refuses an empty name and refuses a repeated one.

### 4.3 STRUCTURAL rules for `source`

`source` is an object with exactly these five keys and no others.

| key | JSON type | permitted values | meaning | disposition |
|---|---|---|---|---|
| `encoding` | string | `utf-8-sig`, `latin-1` | the encoding that read the table | REPORT-ONLY |
| `used_fallback_encoding` | boolean | — | true when the fallback rather than the primary encoding read the file | REPORT-ONLY |
| `header_source` | string | `file`, `generated` | `file`: the column names came from the table's first row. `generated`: no names were in the file and synthtwin named the columns `column_1`, `column_2`, … | EXACT-CONTROL |
| `header_by_convention` | boolean | — | true when the first row was taken as names because nothing in the file said otherwise, rather than because the file showed it | REPORT-ONLY, with a required sentence |
| `header_evidence` | string | any non-empty text | the header verdict in one plain sentence | REPORT-ONLY, with a required sentence |

**Membership rule.** All five keys are REQUIRED. No other key may appear
under `source`.

**Invariant S5.** `used_fallback_encoding` is true exactly when
`encoding` is `latin-1`.

**Invariant S6.** `header_by_convention` may be true only when
`header_source` is `file`. Generated names are not a convention about
somebody's first record; they are names synthtwin made.

**The required sentence.** When `header_by_convention` is true, the
generation report MUST say, in plain words, that the twin's column names
may in fact be a first data row of the real table rather than names — not
merely that a header was written. Phase 1's R1 residual is exactly this
uncertainty, and a report that says only "a header was written" hides a
warning the profile is carrying (plan P2-D6).

### 4.4 `settings`

An object with exactly these fifteen keys. Its whole subtree is
LOADER-ONLY: nothing in it is an output obligation, and the generator
reads it only to interpret floor-governed facts elsewhere in the
document.

| key | JSON type | range / permitted values |
|---|---|---|
| `small_cell_floor` | integer | ≥ 11 |
| `identifier_uniqueness` | number | 0.0 ≤ x ≤ 1.0 |
| `identifier_minimum_rows` | integer | ≥ 0 |
| `minimum_parse_rate` | number | 0.0 ≤ x ≤ 1.0 |
| `categorical_share` | number | 0.0 ≤ x ≤ 1.0 |
| `categorical_ceiling` | integer | ≥ 1 |
| `categorical_floor` | integer | ≥ 1 |
| `sentinel_outlier_iqr_multiple` | number | ≥ 0.0 |
| `sentinel_minimum_share` | number | 0.0 ≤ x ≤ 1.0 |
| `kept_values` | object | exactly `{"n_declared": integer ≥ 0, "values_recorded": false}` |
| `declared_missing_values` | object | the same two keys, the same rules |
| `declaration_matching` | string | exactly `exact_number_when_it_reads_as_one_else_spelling` |
| `declaration_publication` | string | exactly `settings_counts_only_columns_unchanged` |
| `near_threshold_slack` | integer | ≥ 0 |
| `forced_identifiers` | array of strings | the names the person passed to `--identifier`, sorted ascending, pairwise distinct |

**Invariant S7.** `values_recorded` is `false` in both declaration
records. It is a discriminator, not a switch: a profile written before
this rule carried an array of spellings under the same key, and a
consumer must be able to tell the two apart without guessing. A loader
refuses `true`, because a document claiming to record declared spellings
is not a version 4 document.

**Invariant S8.** Every name in `forced_identifiers` is the `name` of
some column block. A name that matches no column is a refusal: it means
the profile and the schema disagree about which columns were declared.

**Invariant S9.** `categorical_floor <= categorical_ceiling`.

### 4.5 `publication_notes`

An array, possibly empty, of objects each having exactly two keys:

| key | JSON type | meaning |
|---|---|---|
| `column` | string | the `name` of the column the note is about |
| `note` | string | one plain-language sentence about what was held back and why |

**Invariant S10.** Every `column` value is the `name` of some column
block.

**Invariant S11.** The notes appear grouped by column in schema order,
and within one column in the order the producer emitted them. Order is
part of the canonical bytes; a loader does not need to re-derive it, but
a producer may not shuffle it between runs.

**The publication guard.** Every string in the finished document —
`publication_notes` included, because `build_document` lifts these notes
to the top level after each column block is finished — is either a value
the disposition matrix authorizes for publication or a note built by an
enumerated first-party constructor from a fixed grammar of literal
fragments plus already-authorized values (plan P2-D2, item P2-R5-F5).
This is a producer obligation; it is recorded here because it is a
property of the document the contract describes, and because a future
note that interpolates a source spelling must fail at construction rather
than at pattern matching.

**How the shipped producer meets it** (item P2-C1-F3). Every sentence
this producer can publish — the publication notes, each column's
`detection_evidence`, each of its `remarks`, and `source.header_evidence`
— is built by `taxonomy.note` from one form of the closed table
`taxonomy.NOTE_ARITY`, filled only with whole numbers, words of this
package's own enumerated vocabulary, and other forms of that same table.
The sentence carries the form and the arguments it was built from.
`profile.check_publication` then walks the finished document, top-level
notes included, and accepts a sentence only when `taxonomy.rendered`
writes the identical text again from that form and those arguments;
every other leaf must satisfy the rule its own path carries, and a path,
a key or a leaf kind with no rule stops the run before serialization.
Four mutations are required to fail and are held in
`tests/test_p2c1f3_publication_guard.py`: a source spelling formatted
into an existing note path with an unchanged type, a concatenation
assembling the same text from fragments, a nested container smuggling
one, and a note lifted to the top level. A loader implements none of
this: it reads the strings the document carries, under the rules stated
above.

### 4.6 `relationships` — the reserved manifest (version 4 addition)

An object with exactly these eight keys, in this set, each with the JSON
value `null` and nothing else.

| key | value |
|---|---|
| `deterministic` | `null` |
| `grain` | `null` |
| `hierarchy` | `null` |
| `keys` | `null` |
| `missing_data_process` | `null` |
| `statistical` | `null` |
| `temporal` | `null` |
| `validation_targets` | `null` |

**Invariant S12.** All eight keys are present. No ninth key may appear.
Every value is exactly `null`. A loader refuses any non-null content,
naming the key, and its message says that this version of synthtwin does
not carry cross-column structure and that the person needs a newer
synthtwin to read a profile that does.

**Why the block exists empty.** Phase 2 preserves no cross-column
structure, and a block reserved in the shape it will eventually take is
what lets a later phase fill one slot without moving any other key. The
generator carries exactly one dispatch seam that verifies this block is
empty and then generates columns independently (plan P2-D5). Filling any
slot advances `profile_version`; version 4 is defined as the version in
which all eight are null.

---

## 5. The column block

A column block is an object. Its key set is the union of the universal
keys (section 5.1) and the keys its role adds (section 6). No other key
may appear; a loader refuses an unknown key, naming it and the column.

### 5.1 Universal keys — present on every column, every role

| key | JSON type | range / permitted values | meaning |
|---|---|---|---|
| `name` | string | non-empty after trimming | the column's name |
| `position` | integer | `1 .. n_columns` | the column's one-based place in the schema |
| `role` | string | one of the ten role names, section 6 | the type path the taxonomy chose |
| `statistical_type` | string | `unknown`, `numeric`, `constant`, `binary`, `datetime`, `count`, `continuous`, `categorical`, `code`, `text` | the shape of the column's values (version 4 addition) |
| `quality_state` | string | `ok`, `empty`, `unrepresentable` | whether the column has usable values at all (version 4 addition) |
| `structural_role` | string | `data`, `identifier` | whether the column was declared to hold record numbers or codes (version 4 addition) |
| `n_present` | integer ≥ 0 | ≤ `n_rows` | how many cells hold a value |
| `n_missing` | integer ≥ 0 | ≤ `n_rows` | how many cells hold no value |
| `missing_by_class` | object | exactly five keys, section 5.4 | absent cells by the reason each was counted absent |
| `missing_by_source` | object | section 5.4 | absent cells by the exact spelling that made them absent, under the floor |
| `n_distinct` | integer ≥ 0 | ≤ `n_present` | how many different RAW present spellings the column holds |
| `n_distinct_folded` | integer ≥ 0 | ≤ `n_distinct` | how many different FOLDED identities it holds |
| `n_numeric` | integer ≥ 0 | — | present cells that read as a number this file format can hold |
| `n_not_numeric` | integer ≥ 0 | — | present cells that are not numeric notation at all |
| `n_out_of_range` | integer ≥ 0 | — | present cells that are well-formed numbers too large or too small for binary64 |
| `n_contradictory` | integer ≥ 0 | — | present cells written in numeric notation whose meaning conflicts with itself — a sign inside accounting parentheses |
| `n_sentinel_candidates_unpublished` | integer ≥ 0 | — | how many stand-in numbers were judged but occurred in too few rows to be named |
| `sentinel_verdicts` | array of objects | section 5.5 | what was decided about each named stand-in number, and why |
| `detection_evidence` | string | non-empty | one plain sentence saying why this role was chosen |
| `remarks` | array of strings | possibly empty | plain-language notes about this column |

### 5.2 The three axes (version 4 addition), and the rule that derives them

`role` stays exactly as version 3 shipped it. The three axes are added
beside it, and **the generator dispatches on the axes, never on `role`**
(plan P2-D3). The axes are derived by the fixed rule in this table, which
is total over the ten roles and admits no other combination.

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

**`structural_role` is `identifier` exactly when the column was named
with `--identifier`, and `data` otherwise.** This includes a declared
column that ends with role `empty`, which is the one case where a
declared column does not carry role `identifier`: the empty-column rule
settles a column with no present values before any other rule runs, so a
declared column of entirely absent cells arrives at role `empty` while
still being a column whose owner said it holds codes.

**Invariant A1.** `structural_role == "identifier"` if and only if `name`
appears in `settings.forced_identifiers`.

**Invariant A2.** `statistical_type == "code"` implies
`structural_role == "identifier"`. There is no route to the `identifier`
role but the declaration, so a `code` column is always a declared one.

**Invariant A3.** `structural_role == "identifier"` implies
`statistical_type` is `code` or `unknown`, and `role` is `identifier` or
`empty`.

**Invariant A4.** The pair (`role`, `statistical_type`, `quality_state`)
is exactly one row of the table above. A loader refuses any other
combination, naming the column and the three values, because a
combination outside the table is a document whose axes and role disagree,
and the generator dispatches on the axes.

**Why the axes and not the role.** The role name is a taxonomy verdict
carrying a rule's history; the axes are the three questions the generator
actually asks — what shape are the values, are there usable values at
all, and is this column somebody's key. Dispatching on the axes means a
future role added to the taxonomy arrives with its answers already
stated, rather than as an unrecognized name in a chain of comparisons.

### 5.3 The multiplicity map — one shape, used in three places

A **multiplicity map** is an object whose keys are row counts written in
base ten and whose values are how many different things covered exactly
that many rows.

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

The three uses, with M1 and M2 made concrete, are
`n_distinct_by_occurrences` (section 7.2), `variants_withheld` (section
7.4), and — in the same class of fact though not the same shape —
`suppressed_level_counts` (section 6.3), which is a sorted array rather
than a map because it is a version 3 field and its shape does not move.

### 5.4 The two absent-cell maps

**`missing_by_class`** has exactly these five keys, always all five, each
an integer ≥ 0:

| key | meaning |
|---|---|
| `(blank)` | the cell was empty or held only spaces |
| `(declared-missing)` | the person named this value with `--missing-value` |
| `(numeric-sentinel)` | a stand-in number the column-level rule judged to mean "no value" |
| `(text-code)` | one of the spellings that mean "no value" |
| `(withheld)` | the pooled remainder of the classes above whose own counts fell below the floor |

**Invariant N1.** The five values sum to `n_missing`.

**Invariant N2.** A class other than `(withheld)` is either 0 or at least
the floor. A class whose real count fell between 1 and the floor is
pooled into `(withheld)` and reads 0 here.

**`missing_by_source`** is an object mapping an exact absent-value
spelling to how many rows held it, plus a `(withheld)` remainder. Its
keys are:

- an absent-value spelling that at least `small_cell_floor` rows shared,
  after passing through the display boundary that escapes line, control
  and bidirectional formatting characters; or
- `(blank)`, standing for every cell that was empty or held only spaces;
  or
- `(withheld)`, the pooled count of every spelling below the floor.

**Invariant N3.** Either `missing_by_source` is empty, or its values sum
to `n_missing`. It is empty, whatever `n_missing` is, exactly on a column
whose publication class permits no value of the table to appear anywhere
in its block — that is, when `structural_role == "identifier"` or `role`
is one of `numeric_unrepresentable`, `identifier`, `free_text`.

**Invariant N4.** Every key other than `(blank)` and `(withheld)` maps to
a value at least the floor.

Both maps are REPORT-ONLY. The twin writes every absent cell as an empty
CSV field; absent-value spellings and their classes are not reproduced
(residual R-P2-2), and the report names the real table's published
spellings so the person can see what was not carried over.

### 5.5 A sentinel verdict entry

`sentinel_verdicts` is an array, possibly empty, of objects each having
exactly these four keys:

| key | JSON type | permitted values |
|---|---|---|
| `candidate` | string | the stand-in number as text, or exactly `(withheld)` |
| `verdict` | string | `read_as_missing`, `kept_as_a_number` |
| `reason` | string | `outlier_and_frequent`, `not_an_outlier`, `too_rare`, `too_few_other_values`, `kept_by_you` |
| `n_occurrences` | integer ≥ 1 | how many rows held the candidate |

**Invariant V1.** Every entry has `n_occurrences` at least the floor.
Candidates below the floor are not listed at all; they are counted,
unnamed, in `n_sentinel_candidates_unpublished`.

**Invariant V2.** `candidate` is `(withheld)` on exactly the columns
where `missing_by_source` is empty for the reason in N3 — a column whose
class permits no value of the table anywhere in its block. Naming the
candidate there would publish a value out of a column that publishes
none.

**Invariant V3.** `verdict` is `read_as_missing` only when `reason` is
`outlier_and_frequent`. The other four reasons all keep the candidate as
an ordinary number of the column.

**Invariant V4.** Where `candidate` is a number rather than `(withheld)`,
entries appear in ascending order of that number. Where it is
`(withheld)`, entries appear ordered by `n_occurrences`, then `verdict`,
then `reason` — so that on a withholding column no position can say which
of two withheld candidates is the smaller.

The whole block is REPORT-ONLY. The twin does not reproduce stand-in
spellings; the report says what was decided.

### 5.6 The ladder

Two fields carry a ladder: `percentiles` on the numeric roles and
`date_percentiles` on `datetime`. Both are objects with exactly the
eleven keys `min`, `p01`, `p05`, `p10`, `p25`, `p50`, `p75`, `p90`,
`p95`, `p99`, `max`, no more and no fewer.

**Invariant L1 (non-decreasing).** Read in ladder order — `min`, `p01`,
`p05`, `p10`, `p25`, `p50`, `p75`, `p90`, `p95`, `p99`, `max` — the
values never decrease. For `percentiles` the comparison is numeric; for
`date_percentiles` it is plain text comparison, which is why the
canonical datetime forms are chosen to sort as text (section 6.6).

**Invariant L2 (endpoints).** `min` is the smallest value and `max` the
largest. They are the two rungs the generator pins by fixed rule, and
they are EXACT-OBSERVABLE while the nine interior rungs are APPROXIMATED.

**Invariant L3 (null rungs).** A `percentiles` rung may be `null`, and
means the exact rung is not a finite binary64 value. No producible
profile is known to reach this — every interpolated rung lies between two
finite neighbours and is therefore finite — but a loader accepts `null`
rather than refusing a document over a case it cannot rule out, and a
generator treats a null rung as carrying no obligation at that rung and
says so in the report. **The value a generator uses in its place is
fixed by `docs/spec/generation-method-v1.md` G5.1**, so a null rung is
one rule and not two: the loader accepts it here, the method says what
is written for it there, and neither document leaves it to an
implementation. `date_percentiles` rungs are never null.

---

## 6. The roles, one section each

There are **ten** roles. The plan and the Phase 2 task description both
speak of "the nine roles" while listing ten; the producer's own role
tuple has ten entries and this contract is written against it. The ten
are: `empty`, `numeric_unrepresentable`, `constant`, `binary`,
`datetime`, `count`, `continuous`, `categorical`, `identifier`,
`free_text`.

Each section below gives the keys the role ADDS to the universal set of
section 5.1. **Every key not listed for a role — universal or
role-specific — is FORBIDDEN on that role.** Section 6.11 gives the
forbidden-key matrix in one place, because "forbidden" is the half of a
contract that a loader can only enforce if it is written down.

### 6.1 `empty`

A column with no present cells at all: every cell was blank, or one of
the spellings that mean "no value", or removed by a declaration.

**Added keys:** none. An `empty` block is exactly the universal key set.

| fact | value |
|---|---|
| `n_present` | `0` |
| `n_missing` | `n_rows` |
| `n_distinct` | `0` |
| `n_distinct_folded` | `0` |
| `n_numeric`, `n_not_numeric`, `n_out_of_range`, `n_contradictory` | `0` |
| `sentinel_verdicts` | `[]` |
| `n_sentinel_candidates_unpublished` | `0` |

**Invariant E1.** `role == "empty"` if and only if `n_present == 0`.

**Invariant E2.** An `empty` column carries NO per-column `n_rows` echo.
The echo lives only inside numeric blocks (section 6.7).

Both distinctness counts are EXACT-OBSERVABLE and trivially met: the twin
writes an all-absent column, which recounts to zero raw and zero folded
identities.

### 6.2 `numeric_unrepresentable`

A column whose writer meant numbers, where too few of those numbers are
values binary64 can hold for any statistic to be honest. No value of the
column is published.

**Added keys:**

| key | JSON type | range | meaning |
|---|---|---|---|
| `n_whole` | integer ≥ 0 | — | present cells whose notation settles that the value is a whole number |
| `n_fraction` | integer ≥ 0 | — | present cells whose notation settles that the value is not whole |
| `n_whole_unknown` | integer ≥ 0 | — | present cells whose notation settles neither |
| `n_positive` | integer ≥ 0 | — | present cells whose notation settles a positive sign |
| `n_negative` | integer ≥ 0 | — | present cells whose notation settles a negative sign |
| `n_sign_unknown` | integer ≥ 0 | — | present cells whose notation settles neither |
| `n_distinct_by_occurrences` | multiplicity map | section 5.3 | how many different RAW present spellings covered one row, two rows, and so on (version 4 addition) |

**Invariant U1.** `n_whole + n_fraction + n_whole_unknown == n_present`.

**Invariant U2.** `n_positive + n_negative + n_sign_unknown == n_present`.

**Invariant U3.** M1 for `n_distinct_by_occurrences`: its values sum to
`n_distinct`. M2: its keys weighted by its values sum to `n_present`.

**Invariant U4.** `missing_by_source` is empty and every
`sentinel_verdicts` entry has `candidate == "(withheld)"` (N3, V2).

**What this role does NOT publish, stated because the omission is
load-bearing.** There is no width fact and no magnitude fact anywhere in
this block. Two columns of overflowing values, one about 400 characters
wide and one about 4,000, publish identically. Width fidelity is
therefore withdrawn: the twin invents digit strings that are themselves
outside binary64 range, reproduces the whole/fraction and sign counts and
the multiplicity map, and does so at ONE canonical invented width, which
the report discloses (residual R-P2-1, still flagged for the owner).

**And no CROSS-TABULATION of the three count families is published
either** (review item P2-C3-F1). This block carries three separate
divisions of the same present cells — by notation class (X2), by
whole-number status (U1) and by sign (U2) — and says nothing about how
any two of them cross. How `n_out_of_range` divides between `n_whole`
and `n_fraction` is the case that matters in practice, and it is not
recorded here or anywhere else in the document. A generator that fixes
such a division by a rule of its own has added a fact to the
description: the real table proves that SOME cross-tabulation of these
counts exists, never which one, so a division the description does not
carry can be infeasible where the real column's own values were not.
The three families are therefore three margins of one packing, and the
method states that rule (`docs/spec/generation-method-v1.md` G10.5).
Every one of the counts themselves stays EXACT-OBSERVABLE in section 9,
unchanged and with no exception.

### 6.3 The label roles: shared shape

`constant`, `binary` and `categorical` all publish LEVELS. Their shared
keys are specified once here; sections 6.4 to 6.6 state only what each
adds or restricts.

| key | JSON type | meaning |
|---|---|---|
| `levels` | array of level entries | the published labels and their counts, section 6.3.1 |
| `suppressed_levels` | integer ≥ 0 | how many labels the floor held back |
| `suppressed_rows` | integer ≥ 0 | how many rows those held-back labels covered in total |
| `suppressed_level_counts` | array of integers | the sizes of the held-back labels, sorted ascending |

#### 6.3.1 A level entry

An object with exactly these four keys. Two of them are version 4
additions.

| key | JSON type | meaning |
|---|---|---|
| `label` | string | the published label, as a FOLDED identity: trimmed and case-folded |
| `count` | integer ≥ 1 | how many present rows carry this folded identity |
| `variants` | object | exact spelling → count, for every spelling of this label that cleared the floor (version 4 addition) |
| `variants_withheld` | multiplicity map | how many different spellings of this label covered one row, two rows, … below the floor (version 4 addition) |

Section 7.4 specifies `variants` and `variants_withheld` in full.

#### 6.3.2 Label invariants

**Invariant B1 (published identity is normalized).** Every `label` is a
folded identity — trimmed and case-folded — so a published label may
never have appeared byte-for-byte in the table. The contract calls it a
normalized identity everywhere. What the table actually held is in
`variants`.

**Invariant B2 (level completeness).**
`len(levels) + suppressed_levels == n_distinct_folded`.

**Invariant B3 (row completeness).**
`sum(entry.count for entry in levels) + suppressed_rows == n_present`.

**Invariant B4 (the suppressed multiset).**
`len(suppressed_level_counts) == suppressed_levels` and
`sum(suppressed_level_counts) == suppressed_rows`, and the array is
sorted ascending.

**Invariant B5 (the floor, both ways).** Every `entry.count` is at least
the floor. Every element of `suppressed_level_counts` is at least 1 and
below the floor.

**Invariant B6 (label order).** `levels` is ordered by descending
`count`, and among equal counts by ascending `label`. Order is part of
the canonical bytes and a producer may not shuffle it between runs.

**Invariant B7 (labels are distinct).** No two entries share a `label`.

**Invariant B8 (levels may be empty).** `levels == []` is valid: it is a
column every one of whose labels fell below the floor. `n_distinct_folded`
then equals `suppressed_levels` and `n_present` equals `suppressed_rows`.

`levels`, `suppressed_levels`, `suppressed_level_counts` and
`suppressed_rows` are EXACT-OBSERVABLE: the twin writes each published
label at exactly its count and invents that many neutral labels at
exactly the held-back sizes.

### 6.4 `constant`

Every present cell is the same folded identity.

**Added keys:** the four shared label keys of section 6.3 and nothing
else. `level_ceiling` is FORBIDDEN on this role.

**Invariant C1.** `n_distinct_folded == 1`.

**Invariant C2.** `len(levels) + suppressed_levels == 1`. Either the one
label cleared the floor — one entry, `suppressed_levels == 0` — or it did
not, in which case `levels == []`, `suppressed_levels == 1`, and the
value itself is not published.

### 6.5 `binary`

Exactly two folded identities.

**Added keys:** the four shared label keys of section 6.3 and nothing
else. `level_ceiling` is FORBIDDEN on this role.

**Invariant Y1.** `n_distinct_folded == 2`.

**Invariant Y2.** `len(levels) + suppressed_levels == 2`.

Note that `n_distinct` may exceed 2 on a binary column: `A`, `a`, `B`,
`b` is two folded identities and four raw spellings. Version 4 publishes
those spellings (section 7.4), which is what lets the twin keep the raw
count.

### 6.6 `categorical` and `datetime`

Two roles with nothing in common but their place in this ordering. Each
has its own key set and its own subsection.

#### 6.6.1 `categorical`

At most a ceiling of different folded identities, each shared by rows.

**Added keys:** the four shared label keys of section 6.3, plus:

| key | JSON type | range | meaning | disposition |
|---|---|---|---|---|
| `level_ceiling` | integer ≥ 1 | — | the most different values a set of categories could have had in a table of this many rows | LOADER-ONLY |

**Invariant G1.** `n_distinct_folded <= level_ceiling`.

**Invariant G2.** `level_ceiling` is LOADER-ONLY. It records the line the
column passed and imposes no obligation on the twin: it must not be read
as a cap the generator has to respect, because the generator reproduces
counts, not the rule that produced them.

#### 6.6.2 `datetime`

**Added keys:**

| key | JSON type | permitted values | meaning |
|---|---|---|---|
| `format` | string | `iso-date`, `iso-datetime`, `compact-date`, `month-first-date`, `day-first-date`, `year-quarter` | the parser family that read the REAL file |
| `resolution` | string | `date`, `datetime`, `quarter` | which canonical form the published datetimes are written in |
| `time_precision` | string | `subsecond`, `second`, `minute`, `date`, `quarter` | the FINEST precision any cell of the real column writes |
| `subsecond_digits` | integer ≥ 0 | — | the most fractional-second digits any cell writes |
| `datetimes_read_at` | string | `local`, `utc` | which clock `earliest`, `latest` and `date_percentiles` are written on |
| `earliest` | string | a canonical form, below | the earliest instant, in the canonical form for this resolution |
| `latest` | string | a canonical form, below | the latest instant |
| `earliest_utc_offset` | string | an offset, `(none)`, or `(withheld)` | the UTC offset the earliest cell carried |
| `latest_utc_offset` | string | an offset, `(none)`, or `(withheld)` | the UTC offset the latest cell carried |
| `date_percentiles` | ladder of strings | section 5.6 | the eleven-rung ladder over the ordered instants |
| `n_unparsed` | integer ≥ 0 | — | present cells that did not read as a date under the chosen format |
| `utc_offsets` | object | offset → count | how often each UTC offset appeared, under the floor |

**The canonical forms**, fixed by `resolution`:

| `resolution` | canonical text | example |
|---|---|---|
| `date` | `YYYY-MM-DD` | `2024-03-15` |
| `datetime` | `YYYY-MM-DD HH:MM:SS` | `2024-03-15 14:05:00` |
| `quarter` | `YYYY-Qn` | `2024-Q1` |

All three sort correctly as plain text, which is why L1 compares
`date_percentiles` as text.

**The RANGES are part of the canonical form, not only the shape**
(review item P2-C1-F6). A loader checks both, and a document failing
either is refused:

| field | permitted values |
|---|---|
| `YYYY` | `0001` and above; a year the proleptic Gregorian calendar has |
| `MM` | `01` to `12` |
| `DD` | `01` to the last day that month has, leap years by the Gregorian rule (a year divisible by four, except a century not divisible by four hundred) |
| `HH` | `00` to `23` |
| `MM` (minutes) | `00` to `59` |
| `SS` | `00` to `60` — sixty is deliberate: a leap second is a reading a real table can hold and the shipped date reader accepts one, and a twin cell carries it back unchanged (section 9.6). D10 refuses it on the one clock no cell can show it on, rather than reporting it as a loss |
| `n` (quarter) | `1` to `4` |

Earlier revisions checked the shape alone and said so, on the reasoning
that the contract fixed the form and said nothing about the calendar.
That reasoning had a cost the revision did not see: a generator does
whole-day and whole-second arithmetic on these fields, so an accepted
`2024-99-99` is not refused and is not preserved either — it is
normalized into a real date somewhere else entirely, and the exact
endpoint text a published fact promises is silently lost. The producer
writes no such value: the shipped date reader refuses a thirty-first of
February before it reaches a description.

**The offset forms.** An offset key or endpoint value is one of: `Z`; a
signed offset exactly as the source wrote it, such as `+02:00` or
`-05:00`; `(none)` for a cell that carried no offset at all; or
`(withheld)` for the pooled remainder. **A signed offset carries its own
range**, for the same reason and enforced the same way: the hour field
runs from `00` to `14`, the minute field from `00` to `59`, and an hour
field of `14` requires a minute field of `00`. No zone stands further
from the shared clock than that, and these are the bounds the shipped
date reader already applies to a real cell.

**Invariant D1 (resolution follows format).** `resolution` is `datetime`
when `format` is `iso-datetime`, `quarter` when `format` is
`year-quarter`, and `date` for the other four formats.

**Invariant D2 (offset totals).** The values of `utc_offsets` sum to
`n_present - n_unparsed`. Only cells that parsed have an offset.

**Invariant D3 (the floor on offsets).** Every key of `utc_offsets` other
than `(withheld)` maps to a count at least the floor. `(withheld)`
appears only when the pooled remainder is non-zero.

**Invariant D4 (endpoint offsets never out-name the map).** An endpoint
offset field holds `(none)` when that endpoint's cell carried no offset;
otherwise it holds that offset when the offset is a key of `utc_offsets`,
and `(withheld)` when it is not. An endpoint field may never name an
offset the map is withholding — a value published in one field of a block
that another field of the same block promises to withhold is a
contradiction the contract forbids.

**Invariant D5 (which clock).** `datetimes_read_at` is `local` when the
whole column shares one UTC offset, and `utc` when two or more offsets
appear. Local text is what the table holds and is the more faithful thing
to publish, so it is kept whenever every value shares one offset — which
is every real column but a few. The moment two offsets appear, local text
no longer orders the values and the profile publishes the instants
instead.

**D5 is a published fact, not one a consumer may re-derive from
`utc_offsets`.** Where every offset in a column fell below the floor, the
map collapses to a single `(withheld)` entry whether one offset wrote the
column or ten did, so the map alone cannot settle the question. That is
exactly why the field exists and is published separately: a consumer
never has to combine fields, and never has to guess, to know which clock
it is holding. A loader therefore checks D5 only in the direction the
document can support — `utc_offsets` holding two or more non-`(withheld)`
keys requires `datetimes_read_at == "utc"` — and accepts either value
where the map is fully withheld.

**Invariant D6 (precision is at least as fine as resolution).**
`time_precision` is `quarter` only when `resolution` is `quarter`; it is
`date` only when `resolution` is `date`; `minute`, `second`
and `subsecond` occur only when `resolution` is `datetime`.

**Why `date` beside `datetime` is refused, and not merely unusual**
(review item P2-C1-F6). An earlier revision permitted that pair. No twin
cell can hold it: written `2024-03-15` the column re-profiles with
`resolution: date`, so the published form is lost, and written
`2024-03-15T00:00:00` it re-profiles with `time_precision: second`, so
the published detail is lost. Both fields are EXACT-OBSERVABLE, so a
description carrying that pair is one no generator can satisfy. The
producer cannot make it either — a value with no time of day does not
read as a date AND time at all, so a column read that way never has a
whole date as its finest detail — which is why refusing it costs nothing
a real table can express.

**Invariant D9 (an offset needs a time of day to move).** Every key of
`utc_offsets`, and both endpoint offset fields, are `(none)` or
`(withheld)` unless `resolution` is `datetime`. A whole date and a
quarter carry no clock, the shipped reader reads neither with an offset,
and a twin cell written `2024-03-15+02:00` reads back as no date at all.

**Invariant D7 (subsecond digits).** `subsecond_digits > 0` implies
`time_precision == "subsecond"`, and `time_precision == "subsecond"`
implies `subsecond_digits > 0`.

**Invariant D8 (the ladder covers the parsed cells).**
`date_percentiles` is a ladder over the cells that parsed. When
`n_present == n_unparsed` the column has no parsed cell and cannot reach
the datetime role at all, so both endpoints are always real values.

**Invariant D10 (an endpoint the column's own recorded shape can show).**
Where `resolution` is `datetime`, the seconds field of `earliest` and of
`latest`:

- is `00` when `time_precision` is `minute`, because a cell written
  `YYYY-MM-DDTHH:MM` has no seconds field to carry anything else; and
- is not `60` when `datetimes_read_at` is `utc`, because that field
  names the instant on the SHARED clock, and reading any wall-clock cell
  back onto the shared clock moves a sixtieth second to the following
  minute whatever cell carried it.

And, where `resolution` is `datetime` and `datetimes_read_at` is `utc`,
each endpoint's own minute moved onto the clock its endpoint offset
names — `earliest` by `earliest_utc_offset`, `latest` by
`latest_utc_offset` — is still inside the years `0001` to `9999` that
6.6.2's canonical form can spell. A column on the shared clock writes
every cell on the wall clock its offset names, so an endpoint within one
offset's distance of the calendar's first or last minute asks for a cell
no reader reads back as a date at all. BOTH directions are refused: an
early endpoint behind the shared clock, and a late endpoint ahead of it.

**Why this is refused rather than reported** (review items P2-C3-F2 and
P2-C4-F1). Both endpoints are EXACT-OBSERVABLE with no exception, so a
pair of published facts that no cell can show at once is settled where
it is decided, exactly as the `date`-beside-`datetime` pair of D6 is.
The producer writes none of the three: `time_precision` is the FINEST
precision any cell writes, so a column whose end carries seconds wrote a
seconds field somewhere; a column put on the shared clock has its
endpoints normalized onto that clock before they are published, which is
where a sixtieth second would have been resolved; and a real column
whose values sit within a day of either end of the calendar has no
offsets to mix. So this refuses nothing a real table can express, and it
costs the leap second nothing: on the `local` clock — which is every
column but the few that mix offsets — `SS` of `60` is accepted and
written back unchanged, as section 9.6 requires.

The third pair is here because the loader already holds all three fields
it needs — the endpoint, its offset and the clock — so the pair is
decidable in the description. It was the fourth time this one obligation
had been lowered instead (13.16), and the two fields settle it.

**Invariant D11 (the ladder ends ARE the two endpoints).**
`date_percentiles.min == earliest` and `date_percentiles.max == latest`.
Both pairs describe the same two instants, both are EXACT-OBSERVABLE,
and the producer builds all four from one ordering of the same values.
Leaving the pair untied let a hand-made document publish a ladder end
below `earliest`; a generator pins its first cell to `earliest` and
interpolates the rest inside the ladder, so the twin then held instants
EARLIER than the endpoint it published, and describing that twin again
gave back a different `earliest` with nothing said about it. Tying the
two is what makes D10 cover the ladder ends as well, since they are the
same two texts.

**A consequence, stated rather than left to be discovered.** The
canonical `datetime` form carries seconds and no fractional part, so
`earliest`, `latest` and every rung of `date_percentiles` are at second
resolution EVEN WHEN `time_precision` is `subsecond` and
`subsecond_digits` is 3. The finer precision is a fact about the column's
notation, published in its own two fields, not a property of the eleven
published instants. A generator that must write subsecond cells reads
`time_precision` and `subsecond_digits`, never the ladder.

**Twin datetime cells** follow owner decision 5: a twin datetime cell is
written in the ISO form matching the precision the profile records — a
date-only column writes `2024-03-15`, a quarter column writes `2024-Q1`,
and an offset is written only where the profile records a real one. The
amendment is scoped to twin CSV cells; the profile's own canonical
serialization is unchanged.

**`format` is REPORT-ONLY.** It names the REAL file's parser family. The
twin is written in ISO syntax at the recorded precision, not in the
source's lexical family, so a month-first column's twin reprofiles as
`iso-date` and this field cannot be reproduced. That narrowed loss is
residual R-P2-7: code that parses dates with an explicit source format
argument needs that argument changed when it moves from the twin to the
real table.

### 6.7 `count` and `continuous` — the numeric roles

Both roles carry exactly the same key set. They differ only in the
verdict that produced them: `count` when every numeric-looking cell is
whole and none is negative, `continuous` otherwise.

**Added keys:**

| key | JSON type | range | meaning |
|---|---|---|---|
| `percentiles` | ladder of numbers | section 5.6 | the eleven-rung ladder over the PARSED values |
| `mean` | number or `null` | — | the arithmetic mean of the parsed values |
| `std` | number or `null` | ≥ 0 when a number | the sample standard deviation, divided by n−1 |
| `skew` | number or `null` | — | the moment-based skewness |
| `std_unrepresentable` | boolean | — | true when the exact spread is larger than binary64 can hold |
| `n_zero` | integer ≥ 0 | — | parsed values equal to zero |
| `n_negative` | integer ≥ 0 | — | present cells whose notation settles a negative sign, including ones no statistic could use |
| `n_negative_unrepresentable` | integer ≥ 0 | — | out-of-range cells whose notation settles a negative sign |
| `n_used_in_statistics` | integer ≥ 0 | — | how many present cells the statistics were computed from |
| `n_left_out_of_statistics` | integer ≥ 0 | — | how many present cells were not |
| `numeric_share` | number | 0.0 ≤ x ≤ 1.0 | the share of present cells whose writer meant a number |
| `integer_valued` | boolean | — | true when every numeric-looking cell is a whole number |
| `n_rows` | integer ≥ 0 | `== n_rows` at the top level | the table's row count, echoed |
| `numeric_styles` | object | section 7.5 | how many cells were written in each spelling style, under the floor (version 4 addition) |

**Invariant Q1 (the echo).** The per-column `n_rows` equals the
document's `n_rows`. It appears ONLY inside numeric blocks — `count` and
`continuous` — and is FORBIDDEN on every other role. It is LOADER-ONLY:
the document-level `n_rows` is the one that carries the row-count
obligation, and conflating the two is the error plan revision 2 made.

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
`n_used_in_statistics < 3`, and when every parsed value is identical. It
is a number otherwise.

**Invariant Q6 (`std` of one value).** When every parsed value is
identical and `n_used_in_statistics >= 2`, `std` is `0.0` and
`std_unrepresentable` is false.

**Invariant Q7 (`mean` nulls).** `mean` is `null` only when the exact
mean is not a finite binary64 value. It is a number in every producible
profile this contract knows of; a loader accepts `null` and a generator
treats it as an approximated field with no target, saying so in the
report.

**Invariant Q8 (`integer_valued` is a FACT, not a role).** The twin's
integer rule is routed by this published boolean and never by whether the
role name is `count`. A `continuous` column may publish
`integer_valued: true` — a column of whole numbers containing a negative
one is exactly that — and its twin cells are whole numbers.

**Invariant Q9 (`numeric_share`).**
`numeric_share` is `(n_numeric + n_out_of_range + n_contradictory) /
n_present`, computed as a share of the present cells, and is `0.0` when
`n_present` is 0 — which cannot occur on these roles by Q3.

**Invariant Q10 (`n_negative_unrepresentable` bound).**
`n_negative_unrepresentable <= n_out_of_range` and
`n_negative_unrepresentable <= n_negative`.

**Invariant Q11 (`n_zero` bound).** `n_zero <= n_numeric`.

### 6.8 `identifier`

The one role no rule can produce from values. A column carries it exactly
when the person who owns the table named it with `--identifier`, and no
value of it is published anywhere in its block.

**Added keys:**

| key | JSON type | range | meaning |
|---|---|---|---|
| `min_length` | integer ≥ 0 | ≤ `max_length` | the shortest present value's length in characters |
| `max_length` | integer ≥ 0 | ≥ `min_length` | the longest present value's length |
| `all_whole_numbers` | boolean | — | true when every present cell is a whole number and there is at least one |
| `n_all_digits` | integer ≥ 0 | ≤ `n_present` | present cells that are ASCII digits and nothing else, after trimming |
| `n_code_alphabet` | integer ≥ 0 | ≤ `n_present` | present cells drawn from the code alphabet, after trimming |
| `n_distinct_by_occurrences` | multiplicity map | section 5.3 | how many different RAW present values covered one row, two rows, … |

**Invariant I1.** `role == "identifier"` implies
`structural_role == "identifier"` (A2) and `n_present >= 1` (a declared
column with no present cells takes role `empty`, invariant E1).

**Invariant I2.** M1 and M2 for `n_distinct_by_occurrences`: its values
sum to `n_distinct`; its keys weighted by its values sum to `n_present`.

**Invariant I3.** `missing_by_source` is empty and every
`sentinel_verdicts` entry has `candidate == "(withheld)"` (N3, V2).

**Invariant I4.** `min_length >= 1`. A present cell of length zero is a
blank, and a blank is absent.

**The infeasible corner, and what it costs.** Where a declared
identifier's published length range cannot supply as many distinct values
as the column has rows, **length wins and invented identifiers may
repeat** (owner decision 6). The cost is stated, not softened: the twin's
identifier column then contains duplicate values where the real column
had none, so a join or a de-duplication developed against the twin can
fan out or collapse differently than on the real table. The report names
the column, the number of duplicates and that consequence, every run.
What the decision buys is that the twin's identifiers keep the exact
width the real ones had, so width-dependent validation and fixed-width
parsing developed on the twin still hold.

**In that corner, THREE distinctness facts become REPORT-ONLY, not one**
(plan P2-D6, item P2-R4-F4): raw `n_distinct`, `n_distinct_folded`, AND
`n_distinct_by_occurrences`. Worked on the real 200-row single-character
case: a twin holding length 1 can offer at most 95 distinct characters
and 69 distinct folded identities against 200 and 122 published, and 200
values drawn from at most 95 cannot all be singletons — so the
multiplicity map is necessarily violated too. That last one deserves
naming, because the multiplicity map exists precisely so a generator never
makes up a repetition pattern, and in this corner it must. What the
identifier column then preserves is `n_present`, `n_missing`, the length
range, `all_whole_numbers`, `n_all_digits` and `n_code_alphabet` — and
nothing about distinctness or repetition. The report names all three lost
facts with the achieved value beside the published one. **Outside that
corner every one of them is EXACT-OBSERVABLE.**

**Scope of the corner, stated precisely.** Owner decision 6 governs ONLY
the case where the published facts are jointly infeasible. The general
all-different obligation — that a column publishing
`n_distinct == n_present` generates all-different values, on every role —
is unchanged and still binding wherever it is feasible, which is the
ordinary case and includes every undeclared key column arriving as free
text or as a numeric role.

### 6.9 `free_text`

A column no rule claimed. None of its values is published.

**Added keys:**

| key | JSON type | shape | meaning |
|---|---|---|---|
| `length` | object | exactly `min`, `max`, `mean`, `p50` | statistics of the present values' lengths in characters |
| `words` | object | exactly `min`, `max`, `mean` | statistics of the present values' word counts |
| `n_all_digits` | integer ≥ 0 | ≤ `n_present` | present cells that are ASCII digits and nothing else, after trimming |
| `n_code_alphabet` | integer ≥ 0 | ≤ `n_present` | present cells drawn from the code alphabet, after trimming |
| `n_distinct_by_occurrences` | multiplicity map | section 5.3 | how many different RAW present values covered one row, two rows, … (version 4 addition) |

`length.min` and `length.max` are integers ≥ 0; `length.mean` is a number
or `null`; `length.p50` is a number or `null`. `words.min` and
`words.max` are integers ≥ 0; `words.mean` is a number or `null`. A null
in any of the three means the exact statistic is not a finite binary64
value, which no producible profile is known to reach.

**Invariant F1.** `length.min <= length.p50 <= length.max` when `p50` is
a number, and `length.min <= length.mean <= length.max` when `mean` is a
number. Likewise `words.min <= words.mean <= words.max`.

**Invariant F2.** M1 and M2 for `n_distinct_by_occurrences`.

**Invariant F3.** `missing_by_source` is empty and every
`sentinel_verdicts` entry has `candidate == "(withheld)"` (N3, V2).

**Invariant F4.** `length.min >= 1` and `words.min >= 0`. A present cell
has at least one character; a cell of punctuation alone may hold no
words.

**The binding generation rule.** The generator INVENTS language: neutral
synthetic words honoring the published length and word statistics, the
digit and code-alphabet counts, and the multiplicity map including fold
collisions. **It never samples, quotes, templates from, or paraphrases
source text.** Any future change that carries source language into the
profile or the twin is a charter change requiring an owner decision and a
privacy review.

### 6.10 The publication class, in one sentence

Three roles publish no value of the table anywhere in their block —
`numeric_unrepresentable`, `identifier`, `free_text` — and so does any
column whose `structural_role` is `identifier`, whatever its role. On
those columns, and only those, `missing_by_source` is empty and every
sentinel candidate reads `(withheld)`. This is a property of the whole
BLOCK, not of any one field: it is what stops the next field somebody
adds from being the one that leaks.

### 6.11 The forbidden-key matrix

A key is FORBIDDEN on every role whose column below is blank. The
universal keys of section 5.1 are omitted: they are required everywhere.

| key | empty | unrep. | constant | binary | categorical | datetime | count | continuous | identifier | free_text |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| `levels` | | | ● | ● | ● | | | | | |
| `suppressed_levels` | | | ● | ● | ● | | | | | |
| `suppressed_rows` | | | ● | ● | ● | | | | | |
| `suppressed_level_counts` | | | ● | ● | ● | | | | | |
| `level_ceiling` | | | | | ● | | | | | |
| `format` | | | | | | ● | | | | |
| `resolution` | | | | | | ● | | | | |
| `time_precision` | | | | | | ● | | | | |
| `subsecond_digits` | | | | | | ● | | | | |
| `datetimes_read_at` | | | | | | ● | | | | |
| `earliest` | | | | | | ● | | | | |
| `latest` | | | | | | ● | | | | |
| `earliest_utc_offset` | | | | | | ● | | | | |
| `latest_utc_offset` | | | | | | ● | | | | |
| `date_percentiles` | | | | | | ● | | | | |
| `n_unparsed` | | | | | | ● | | | | |
| `utc_offsets` | | | | | | ● | | | | |
| `percentiles` | | | | | | | ● | ● | | |
| `mean` | | | | | | | ● | ● | | |
| `std` | | | | | | | ● | ● | | |
| `skew` | | | | | | | ● | ● | | |
| `std_unrepresentable` | | | | | | | ● | ● | | |
| `n_zero` | | | | | | | ● | ● | | |
| `n_negative` | | ● | | | | | ● | ● | | |
| `n_negative_unrepresentable` | | | | | | | ● | ● | | |
| `n_used_in_statistics` | | | | | | | ● | ● | | |
| `n_left_out_of_statistics` | | | | | | | ● | ● | | |
| `numeric_share` | | | | | | | ● | ● | | |
| `integer_valued` | | | | | | | ● | ● | | |
| `n_rows` (echo) | | | | | | | ● | ● | | |
| `numeric_styles` | | | | | | | ● | ● | | |
| `n_whole` | | ● | | | | | | | | |
| `n_fraction` | | ● | | | | | | | | |
| `n_whole_unknown` | | ● | | | | | | | | |
| `n_positive` | | ● | | | | | | | | |
| `n_sign_unknown` | | ● | | | | | | | | |
| `min_length` | | | | | | | | | ● | |
| `max_length` | | | | | | | | | ● | |
| `all_whole_numbers` | | | | | | | | | ● | |
| `length` | | | | | | | | | | ● |
| `words` | | | | | | | | | | ● |
| `n_all_digits` | | | | | | | | | ● | ● |
| `n_code_alphabet` | | | | | | | | | ● | ● |
| `n_distinct_by_occurrences` | | ● | | | | | | | ● | ● |

Note the two names that mean different things in different blocks and are
NOT the same key: `n_negative` on the numeric roles counts present cells
whose notation settles a negative sign, and on
`numeric_unrepresentable` counts the same thing over a column no
statistic could use. They are one key with one meaning; the row shows
both columns filled. The per-column `n_rows` echo, by contrast, is a
different quantity from the document-level `n_rows` and appears in only
one place.

---

## 7. The five version 4 additions, in full

Nothing was removed from version 3 and nothing changed shape. These five
are the whole of the difference.

### 7.1 The three axes beside the role (owner decision 1, plan P2-D3)

Specified in section 5.2: `statistical_type`, `quality_state` and
`structural_role`, on every column block, with the derivation table and
invariants A1 to A4. Disposition: EXACT-CONTROL, all three.

**Exact shape:** three string-valued keys in the column block, each from
a closed enumeration, each REQUIRED on every role.

**What makes them additive rather than a rewrite:** `role` keeps its name
and its ten values, so a version 3 reader that dispatches on `role` reads
a version 4 column block correctly for every fact version 3 carried. The
axes are what the version 4 GENERATOR dispatches on.

### 7.2 Multiplicity parity for `free_text` and `numeric_unrepresentable` (owner decision 2, plan P2-D4)

Version 3 carries `n_distinct_by_occurrences` on the `identifier` role
alone. Version 4 adds it to `free_text` and `numeric_unrepresentable`,
**with the identifier field's exact shape and serialization** — the
multiplicity map of section 5.3, no variation of any kind.

**Exact shape:** an object; keys are row counts in base ten, left-padded
with zeros to the width of the largest key in the same mapping; values
are how many different RAW present values covered exactly that many rows.
`{}` when the column has no present value.

**Distinctness is over RAW present values**, the same question
`n_distinct` answers, so the two always agree (M1).

**Publication class:** counts about unnamed groups, with **no small-cell
floor**. The map is a function of the group SIZES alone: rename every
value, or shuffle every row, and it does not move. No spelling, no order,
no row position and no link to any other column reaches it. It is the
same class of fact as `suppressed_level_counts`, which publishes the
sizes of the withheld levels for the same reason. What it does disclose,
stated rather than waved away, is the sizes themselves: a map containing
`"1": 1` says some one row holds a value no other row holds. That is a
count about an unnamed group, and it is why the profile is described as
real-derived material rather than as anonymous.

**Why it is needed.** Without it, two columns with different repetition
patterns serialize to identical bytes — six rows holding one value four
times and two values once each, versus six rows holding three values
twice each — so a generator reading the profile alone would have to pick
one pattern for both, and any grouped analysis on the twin would diverge
from the real table.

**Disposition:** EXACT-OBSERVABLE on `free_text` and
`numeric_unrepresentable`. On `identifier` it is EXACT-OBSERVABLE outside
owner decision 6's infeasible corner and REPORT-ONLY inside it
(section 6.8).

### 7.3 The relationship manifest (owner decision 3, plan P2-D5)

Specified in section 4.6: one top-level object, eight required keys,
every value exactly `null`, invariant S12. Disposition: LOADER-ONLY.

### 7.4 Label spelling variants (owner decisions 9 and 11)

#### 7.4.1 What this fixes

The producer folds case and trims spacing before publishing a label. A
column holding `A`, `a`, `B`, `b` therefore publishes two labels of two
rows each, and a twin built from that record alone would write `a, a, b,
b` — repeating where the real column never did, and breaking the
inherited all-different obligation for every label role, not only for
identifiers. The implementer recommended accepting the repeats and
disclosing them; **the owner directed the opposite** — the profile
records the variants so the twin can keep the values distinct.

#### 7.4.2 The wire shape

Every PUBLISHED level entry (section 6.3.1) carries both of these keys.
They are REQUIRED on every entry of `levels` on the three label roles and
FORBIDDEN everywhere else — on every non-label role, and on the
suppressed levels, which have no entry to carry them.

**`variants`** — an object mapping an EXACT source spelling to how many
present rows held it.

- Keys are the spelling exactly as the file wrote it, byte for byte,
  before trimming and before the fold. They are NOT passed through the
  display boundary: a variant is a generation input the twin writes into
  a CSV cell and must read back identically, unlike `missing_by_source`,
  whose keys are REPORT-ONLY and are escaped for display. The display
  boundary applies where a variant is interpolated into the generation
  report or into command output, never to the stored key.
- Values are integers ≥ the floor.
- `{}` is valid: it is a published label every one of whose spellings
  fell below the floor.

**`variants_withheld`** — a multiplicity map (section 5.3): how many
different spellings of this label covered one row, two rows, and so on,
for the spellings the floor held back.

- Keys are row counts in base ten, left-padded to the width of the
  largest key in the same mapping, each reading as an integer between 1
  and `small_cell_floor - 1` inclusive.
- Values are integers ≥ 1.
- `{}` is valid: it is a published label with no held-back spelling.

Worked example, floor 11, a categorical column:

```
{
  "count": 40,
  "label": "north",
  "variants": {
    "North": 22,
    "north": 15
  },
  "variants_withheld": {
    "1": 3
  }
}
```

Twenty-two rows wrote `North`, fifteen wrote `north`, and three further
spellings — which the profile does not name — were written by one row
each. 22 + 15 + 3 × 1 = 40, the parent's count.

#### 7.4.3 Invariants

**Invariant W1 (parent binding).** Every variant is bound to one
already-visible parent label: the keys are forbidden on a withheld
parent, which has no entry, and on every non-label role.

**Invariant W2 (each variant folds to its parent).** Trimming a variant
key and case-folding it yields exactly the entry's `label`. A key that
folds to anything else is a refusal: it would be a spelling of some other
label filed under this one.

**Invariant W3 (no variant exceeds its parent).** Every value of
`variants` is at most the entry's `count`.

**Invariant W4 (the counts close exactly).**
`sum(variants.values()) + sum(key × value for variants_withheld)`
`== count`. Nothing about a published label's rows is unaccounted for.

**Invariant W5 (the floor governs a variant like any published label).**
Every value of `variants` is at least `small_cell_floor`. Every key of
`variants_withheld`, read as a number, is between 1 and
`small_cell_floor - 1`.

**Invariant W6 (variant keys are distinct).** They are object keys, so
this is a property of the JSON, but it is stated because two spellings
that differ only by a character the canonical form does not distinguish
would be one key and must not be produced as two.

**Invariant W7 (at least one spelling exists).** `variants` and
`variants_withheld` are never BOTH empty on the same entry, because a
published label covers at least `small_cell_floor` rows and every row was
written some way.

#### 7.4.4 Why the withheld map is needed

Without it, a parent of eleven rows cannot be told apart from eleven
one-off spellings versus two spellings occurring ten and one times, and
the twin would not know how many spellings to invent. It is the same
class of fact as the identifier repetition multiset: counts about unnamed
groups.

#### 7.4.5 The disclosure delta, stated accurately

The producer folds with a Unicode `casefold()` after trimming, not merely
capitalization. Recording variants therefore publishes every exact
spelling that differs BEFORE that fold — which includes pairs a reader
may not expect, such as `ß` and `SS` normalizing together. The owner
confirmed this broader reading. The delta is bounded to the spelling
forms of labels the profile ALREADY publishes, and no variant crosses the
boundary that a whole label would not, because each variant is governed
by the same floor as any published label. The fact is named in
`SECURITY.md`, in the profiler summary, and in the generation report, and
the disclosure battery scans the COMPLETE profile and profiler summary as
well as the twin and report, because the new fact appears first in the
profile (residual R-P2-11).

**A correction that travels with this addition.** Contract text saying
that case and edge spacing are not preserved is wrong from version 4 on,
and the report must not say it. Case and edge spacing ARE preserved
wherever the variants are visible, and fall back to normalized spelling
only beneath the floor.

#### 7.4.6 Disposition

`variants` and `variants_withheld` are both EXACT-OBSERVABLE: the twin
writes each named spelling at exactly its count, and invents exactly that
many neutral spellings of the parent at exactly the held-back sizes, and
both are recounted from the written CSV.

Their consequence for raw distinctness on the label roles is in section
9: `n_distinct_folded` is EXACT-OBSERVABLE, and raw `n_distinct` is
EXACT-OBSERVABLE where the published variants and the withheld-variant
map supply enough spellings — which is the ordinary case — and
APPROXIMATED under the two-sided envelope only where they do not, with
the report naming the profile's count beside the twin's.

### 7.5 `numeric_styles` (owner decision 10)

#### 7.5.1 What this fixes

Round 5 of the plan review demonstrated that three source families — `0`,
`00`, `000`; `0.0`, `00.0`, `000.0`; and `0e0`, `00e0`, `000e0` — produce
**byte-for-byte identical** column blocks in version 3: role `count`,
three present, three raw and folded identities, all numeric, all zero,
`integer_valued: true`. An ordinary reader infers a whole-number column
from the first family and a decimal column from the other two, so no
profile-only generator could preserve the reader's type for all three,
and owner decision 8's leading-zero family silently chose the whole-number
shape for all of them. The owner directed that the missing fact be
published rather than the fidelity abandoned.

**The fact is about FORM, not values.** It carries no value, no magnitude
and no spelling — only how many cells used each form.

#### 7.5.2 Where it appears

`numeric_styles` is REQUIRED on `count` and `continuous`, and FORBIDDEN
on every other role including `numeric_unrepresentable`. Section 13 gives
the reason and records this as a contract decision: those two roles are
the ones whose twin cells are written as parsed numbers from the ladder
in owner decision 8's spelling family, so they are the roles where the
reader's inferred type is at stake and where a style map is something the
generator can discharge. A `numeric_unrepresentable` column's twin cells
are invented digit strings at one canonical width (residual R-P2-1), so a
style map there would describe a form the twin is already unable to
reproduce.

#### 7.5.3 The enumerated styles

Exactly six styles, and no seventh may be added by an implementation:

| style | what it names |
|---|---|
| `plain` | the canonical spelling: digits, an optional leading minus, no decimal point, no exponent, no redundant leading zero |
| `leading_zero` | the digits before any decimal point begin with a redundant `0` |
| `leading_plus` | the cell begins with `+` |
| `decimal` | the cell carries a decimal point |
| `exponent_lower` | the cell carries a lower-case `e` exponent |
| `exponent_upper` | the cell carries an upper-case `E` exponent |

#### 7.5.4 The classification rule

Every cell counted here is assigned **exactly one** style. The rule is a
first-match-wins ladder over the cell's text, and the ORDER is normative
because it is what makes producer and generator agree:

1. Remove surrounding whitespace. If the result is wrapped in a matching
   pair of accounting parentheses, take what is inside and remove
   surrounding whitespace again. Remove any thousands-separator commas.
   Call the result the **core**.
2. `exponent_upper` — the core contains the character `E`.
3. `exponent_lower` — the core contains the character `e`.
4. `decimal` — the core contains the character `.`.
5. `leading_plus` — the core begins with `+`.
6. `leading_zero` — after any leading `-`, the core begins with `0` and
   is longer than that single `0`.
7. `plain` — everything else.

Worked: `0` → `plain`. `00` and `-007` → `leading_zero`. `+5` →
`leading_plus`. `0.0` and `+0.5` → `decimal`. `1e5` → `exponent_lower`.
`1E5` → `exponent_upper`. `(5)` → `plain`. `(05)` → `leading_zero`.
`1,234` → `plain`.

**Why type-bearing forms are tested first.** A reader infers a decimal
column from the presence of a decimal point or an exponent anywhere in
the column, so the styles that decide the inferred type are the ones that
must be counted when a cell carries more than one mark. `+0.5` is counted
as `decimal`; the leading plus is lost for that cell and the totals still
close, which is the trade the priority order makes deliberately.

**This ladder is what a twin cell's style IS** (review item P2-C1-F8).
The same rule runs in both directions: it reads the real column to write
this map, and it reads the twin's finished cells to check the map was
met. A twin cell's style is therefore what this ladder makes of the text
the twin actually wrote, never a label the generator kept beside the
cell — a recount from the CSV can see nothing else. The consequence is
load-bearing and is stated here rather than left for a generator to
discover: on a column publishing `integer_valued: false`, the canonical
spelling of a value that is not whole already carries a point or an
exponent (`12.5`, `1e+16`), so `plain`, `leading_zero` and
`leading_plus` can only ever be the style of a WHOLE value. Writing a
non-whole value and calling it `plain` does not make the count come
back.

**Two source forms are not styles, and the consequence is recorded.**
Accounting parentheses and thousands separators are classified by their
digit form and are never written by the twin: the comma breaks the CSV
row itself, and parentheses are excluded by owner decision 8. A twin cell
standing for `(05)` is therefore written as a signed leading-zero form,
not as brackets. This is inside residual R-P2-9, which already records
that a twin numeric column can look less tidy, or differently punctuated,
than a table whose numbers were written one way.

#### 7.5.5 The wire shape

An object mapping a style name to a count, plus a `(withheld)` remainder
when the floor pooled anything.

```
"numeric_styles": {
  "(withheld)": 4,
  "decimal": 71,
  "plain": 25
}
```

- Keys are style names from the six above, or `(withheld)`.
- Values are integers ≥ 1.
- A style used by no cell has no key.
- A style used by fewer rows than the floor has no key of its own; its
  cells are pooled into `(withheld)`, so a single oddly-written cell
  cannot be singled out.

#### 7.5.6 Invariants

**Invariant P1 (the population).** The values sum to `n_numeric` — the
present cells that read as a number binary64 can hold. Out-of-range and
contradictory cells are NOT counted here: they are written by the
class-preserving construction of plan P2-D9, which has forms of its own,
and counting them here would oblige the generator to write a form the six
styles cannot express.

**Invariant P2 (the floor, both ways).** Every value under a style name
is at least `small_cell_floor`. `(withheld)` appears only when the pooled
remainder is at least 1, and its own value may be anything from 1
upwards.

**Invariant P3 (never empty on these roles).** `numeric_styles` is never
`{}`, because `n_numeric >= 1` on `count` and `continuous` (Q3) and every
counted cell lands in some key.

**Invariant P4 (agreement with `integer_valued`).**
`integer_valued: true` does not forbid a `decimal` or exponent style: a
cell written `5.0` is a whole number written with a point. The two facts
are independent and a loader checks neither against the other.

#### 7.5.7 Disposition and what the twin owes

EXACT-OBSERVABLE. **The twin writes each named style in its published
count**, which restores both the inferred type and much of the
raw-distinctness capacity. **The styles it may write are the six of
section 7.5.3 and no seventh**: a cell named `decimal` is written with a
decimal point, a cell named `exponent_upper` with an upper-case `E`, and
so on for each of the six. Never a thousands separator — the comma
breaks the CSV row itself — and never accounting parentheses, which are
kept for the contradictory-notation stand-in.

**Why all six, and how that sits with owner decision 8** (review item
P2-C1-F8). An earlier revision of this section said the permitted family
was decision 8's — the canonical spelling, leading-zero forms and the
leading-plus form, with exponent forms admitted only to supply fold
collisions — which omits `decimal` entirely while this same section
requires `decimal` cells to be written in their published count. The two
sentences cannot both be obeyed, and an independent generator would emit
plain cells where the shipped one emits decimal ones. The two decisions
govern different questions and the plan now says so (P2-D0, decisions 8
and 10):

- **Decision 8 fixes what the twin may INVENT** — the spellings it
  reaches for where a published count needs more spellings of one value
  than the style map accounts for. That family is the leading-zero one,
  chosen because it has no ceiling and changes no inferred type.
- **Decision 10 fixes what the twin REPRODUCES** — the form of each
  cell, now that the form is a published fact. A `decimal` cell is
  written with a point because the real column's cell had one, which is
  the whole reason decision 10 exists: a column of `0.0`, `00.0`,
  `000.0` is read as a decimal column, and a twin that wrote it plain
  would silently change the reader's inferred type, which is the defect
  decision 10 was taken to close.

The exponent pair keeps its second job as well: it is the only numeric
spelling that carries case, so it is the only construction that can put
a numeric column's folded count below its raw one
(`docs/spec/generation-method-v1.md` G6.5).

**A cell pooled into `(withheld)` is written by its own value**
(`docs/spec/generation-method-v1.md` G6.4): plainly where the value has
a point-free spelling, because `plain` changes nothing a reader infers,
and in the value's own canonical text (3.2.1) where it has none.

**This amends the rule that wrote EVERY pooled cell plainly** (Phase 3
plan P3-D8.1, closing the open defect the disposition registry held
under P2-C5-F3, 2026-08-12). That rule and this section's own
`min`/`max` exactness cannot both be met: a published end carrying a
decimal point has no point-free spelling at all, so a column whose
remainder covered such a cell owed a form no conforming generator could
write, and the twin was required to miss a total it could have met. The
obligation is not lowered by the amendment — no published count moves,
and the two earlier wordings are withdrawn rather than weakened. The
first, which counted the pooled cells as the written cells belonging to
none of the published styles, is unmeetable because every numeric cell
text falls in one of the six styles by the total rule of 7.5.4. The
second, which added the whole remainder to `plain`, is unmeetable on the
shape above. Both are described rather than repeated so that a test can
ban them.

**The EXACT-OBSERVABLE obligation is therefore an identity over the
recount**, every clause of it computable from the written cells and the
published map alone. Writing `r(s)` for the cells the recount finds in
style `s`, `p(s)` for the count the map publishes for it, `R` for the
`(withheld)` remainder, and `NW` for the written numeric cells whose
values have no point-free spelling:

- `r(leading_zero) = p(leading_zero)`, `r(leading_plus) =
  p(leading_plus)` and `r(exponent_upper) = p(exponent_upper)` — the
  remainder never reaches these three: the first two are the invention
  family of owner decision 8, and canonical text never carries an
  upper-case exponent;
- `r(plain) >= p(plain)`, `r(decimal) >= p(decimal)` and
  `r(exponent_lower) >= p(exponent_lower)` — **a published form is
  never substituted away**, whatever the remainder does above it;
- the spill `D = max(0, NW - p(decimal) - p(exponent_lower) -
  p(exponent_upper))` is exactly the pooled cells with no point-free
  spelling, because the published point-carrying counts are spent on
  such cells first;
- `r(decimal) + r(exponent_lower) = p(decimal) + p(exponent_lower) + D`,
  the two canonical forms carrying the spill between them, which of the
  two being each value's own canonical text;
- `r(plain) = p(plain) + R - D`, the remainder's other cells;
- **and no cell is spelled non-canonically without a published count
  entitling it**: in each of `decimal` and `exponent_lower`, the cells
  whose text is NOT the canonical text (3.2.1) of their own value are
  at most that style's published count. The published counts are the
  only licence for a non-canonical point-carrying spelling, so every
  pooled cell carries exactly its value's canonical text and a pool
  cannot be re-spelled into a form the description never named.

`NW` is read off the VALUES, never off the spellings: it is the count of
written numeric cells whose value has no point-free spelling at all.
Counting the cells that were WRITTEN with a point would make the
identity circular — a twin spelling a whole value `1000.0` instead of
`1000` would inflate its own `D` and balance the arithmetic against
itself — and `NW` is fixed by the numbers the cells read back as, which
no choice of spelling can move.

An ordinary column publishes no remainder, `D` is zero, and the identity
is the plain reading: every style matches its published count exactly.
The report names the remainder, how many cells it covered, and how many
of them had no point-free spelling of their own.

**An alternate spelling is used ONLY where the published counts require
it**, so an ordinary all-canonical whole-number column publishes
`{"plain": n}` and its twin stays byte-plain and is read as a
whole-number column exactly as the real one is.

---

## 8. Every invariant, in one checkable list

This section restates the invariants above as one list a loader or a test
can walk. Each is stated so that it is either true or false of a parsed
document, with no interpretation left. The identifiers are the ones used
above.

**Document and structure**

| id | statement |
|---|---|
| S1 | `len(columns) == n_columns` |
| S2 | for all `i`, `columns[i].position == i + 1` |
| S3 | list order is schema order, output column order, and RNG consumption order |
| S4 | column names are non-empty after trimming and pairwise distinct as text |
| S5 | `source.used_fallback_encoding` is true exactly when `source.encoding == "latin-1"` |
| S6 | `source.header_by_convention` implies `source.header_source == "file"` |
| S7 | `settings.kept_values.values_recorded` and `settings.declared_missing_values.values_recorded` are both `false` |
| S8 | every name in `settings.forced_identifiers` is some column's `name` |
| S9 | `settings.categorical_floor <= settings.categorical_ceiling` |
| S10 | every `publication_notes[i].column` is some column's `name` |
| S11 | `publication_notes` is grouped by column in schema order |
| S12 | `relationships` has exactly the eight named keys, each `null` |

**Axes**

| id | statement |
|---|---|
| A1 | `structural_role == "identifier"` ⇔ `name` ∈ `settings.forced_identifiers` |
| A2 | `statistical_type == "code"` ⇒ `structural_role == "identifier"` |
| A3 | `structural_role == "identifier"` ⇒ `statistical_type` ∈ {`code`, `unknown`} and `role` ∈ {`identifier`, `empty`} |
| A4 | (`role`, `statistical_type`, `quality_state`) is one row of the section 5.2 table |

**Universal counts**

| id | statement |
|---|---|
| X1 | `n_present + n_missing == n_rows` |
| X2 | `n_numeric + n_not_numeric + n_out_of_range + n_contradictory == n_present` |
| X3 | `n_distinct_folded <= n_distinct <= n_present` |
| X4 | `n_distinct == 0` ⇔ `n_present == 0` ⇔ `n_distinct_folded == 0` |
| X5 | `1 <= position <= n_columns` |
| N1 | the five values of `missing_by_class` sum to `n_missing` |
| N2 | each `missing_by_class` value other than `(withheld)` is 0 or ≥ the floor |
| N3 | `missing_by_source` is empty, or its values sum to `n_missing`; it is empty exactly on the nothing-publishing columns of section 6.10 |
| N4 | each `missing_by_source` key other than `(blank)` and `(withheld)` maps to a value ≥ the floor |
| V1 | every `sentinel_verdicts` entry has `n_occurrences >= floor` |
| V2 | `candidate == "(withheld)"` exactly on the nothing-publishing columns of section 6.10 |
| V3 | `verdict == "read_as_missing"` ⇒ `reason == "outlier_and_frequent"` |
| V4 | entry order is by candidate number when named, by (`n_occurrences`, `verdict`, `reason`) when withheld |

**Multiplicity maps** (`n_distinct_by_occurrences`, `variants_withheld`)

| id | statement |
|---|---|
| M1 | values sum to the number of different things described |
| M2 | keys read as numbers, weighted by values, sum to the rows covered |
| M3 | every key is a base-ten integer ≥ 1, and all keys in one map have the same character width, that of the largest key |
| M4 | every value is an integer ≥ 1 |

**The ladder fields**

| id | statement |
|---|---|
| L1 | rungs are non-decreasing in ladder order: numerically for `percentiles`, as text for `date_percentiles` |
| L2 | `min` is the smallest and `max` the largest value |
| L3 | a `percentiles` rung may be `null`; a `date_percentiles` rung may not |
| L4 | both objects have exactly the eleven ladder keys |

**Roles**

| id | statement |
|---|---|
| E1 | `role == "empty"` ⇔ `n_present == 0` |
| E2 | an `empty` block carries no per-column `n_rows` |
| U1 | `n_whole + n_fraction + n_whole_unknown == n_present` |
| U2 | `n_positive + n_negative + n_sign_unknown == n_present` |
| U3 | M1 and M2 for `n_distinct_by_occurrences` |
| U4 | `missing_by_source` empty, candidates withheld |
| B1 | every `label` is a folded identity |
| B2 | `len(levels) + suppressed_levels == n_distinct_folded` |
| B3 | `sum(level counts) + suppressed_rows == n_present` |
| B4 | `len(suppressed_level_counts) == suppressed_levels`, `sum(...) == suppressed_rows`, sorted ascending |
| B5 | every `count` ≥ floor; every suppressed count in `1 .. floor - 1` |
| B6 | `levels` ordered by descending `count`, then ascending `label` |
| B7 | labels are pairwise distinct |
| B8 | `levels == []` is valid |
| C1 | `constant`: `n_distinct_folded == 1` |
| C2 | `constant`: `len(levels) + suppressed_levels == 1` |
| Y1 | `binary`: `n_distinct_folded == 2` |
| Y2 | `binary`: `len(levels) + suppressed_levels == 2` |
| G1 | `categorical`: `n_distinct_folded <= level_ceiling` |
| G2 | `level_ceiling` imposes no output obligation |
| D1 | `resolution` follows `format` by the fixed map |
| D2 | `sum(utc_offsets.values()) == n_present - n_unparsed` |
| D3 | every `utc_offsets` key but `(withheld)` maps to a count ≥ floor |
| D4 | an endpoint offset field never names an offset `utc_offsets` withholds |
| D5 | `datetimes_read_at == "local"` exactly when one offset wrote the whole column; a loader checks the one direction the document supports — two or more non-`(withheld)` keys in `utc_offsets` require `utc` |
| D6 | `time_precision` is compatible with `resolution` |
| D7 | `subsecond_digits > 0` ⇔ `time_precision == "subsecond"` |
| D8 | `n_unparsed < n_present` |
| D9 | a real offset is named only where `resolution == "datetime"` |
| D10 | where `resolution == "datetime"`, the seconds field of `earliest` and `latest` is `00` when `time_precision == "minute"`, and is not `60` when `datetimes_read_at == "utc"`; and where `datetimes_read_at == "utc"`, each endpoint moved onto the clock its own endpoint offset names stays inside the years `0001` to `9999` — the three pairs no cell can show, every one refused rather than reported |
| D11 | `date_percentiles.min == earliest` and `date_percentiles.max == latest` |
| Q1 | the per-column `n_rows` equals the document's, appears only on `count`/`continuous`, and is LOADER-ONLY |
| Q2 | `n_used_in_statistics == n_numeric`; `n_left_out_of_statistics == n_present - n_numeric` |
| Q3 | `n_numeric >= 1` |
| Q4 | `std is null` ⇔ (`n_used_in_statistics < 2` or `std_unrepresentable`) |
| Q5 | `skew is null` when `n_used_in_statistics < 3` or every parsed value is identical |
| Q6 | all values identical and `n_used_in_statistics >= 2` ⇒ `std == 0.0`, `std_unrepresentable == false` |
| Q7 | `mean is null` only when the exact mean is not a finite binary64 value |
| Q8 | the integer rule is routed by `integer_valued`, never by the role name |
| Q9 | `numeric_share == (n_numeric + n_out_of_range + n_contradictory) / n_present` |
| Q10 | `n_negative_unrepresentable <= min(n_out_of_range, n_negative)` |
| Q11 | `n_zero <= n_numeric` |
| I1 | `role == "identifier"` ⇒ `structural_role == "identifier"` and `n_present >= 1` |
| I2 | M1 and M2 for `n_distinct_by_occurrences` |
| I3 | `missing_by_source` empty, candidates withheld |
| I4 | `1 <= min_length <= max_length` |
| F1 | `length` and `words` statistics lie inside their own min and max |
| F2 | M1 and M2 for `n_distinct_by_occurrences` |
| F3 | `missing_by_source` empty, candidates withheld |
| F4 | `length.min >= 1`; `words.min >= 0` |

**Version 4 additions**

| id | statement |
|---|---|
| W1 | `variants`/`variants_withheld` appear on published level entries only |
| W2 | trimming and case-folding a variant key yields the entry's `label` |
| W3 | every `variants` value ≤ the entry's `count` |
| W4 | `sum(variants) + sum(key × value over variants_withheld) == count` |
| W5 | every `variants` value ≥ floor; every `variants_withheld` key in `1 .. floor - 1` |
| W6 | variant keys are distinct |
| W7 | `variants` and `variants_withheld` are not both empty on one entry |
| P1 | `sum(numeric_styles.values()) == n_numeric` |
| P2 | every style value ≥ floor; `(withheld)` value ≥ 1 when present |
| P3 | `numeric_styles != {}` on `count` and `continuous` |
| P4 | `numeric_styles` and `integer_valued` are independent facts |

---

## 9. The disposition matrix

Taken from plan section P2-D6. A completeness assertion enumerates every
key the producer emits for every role, plus every top-level key, and
FAILS when any key has no disposition here. It must pass against this
matrix as written; it may not acquire exceptions during implementation.

**What an EXACT-OBSERVABLE obligation covers, and what becomes of a
document whose own facts cannot all hold** (review items P2-C1-F8,
P2-C5-F4). Every disposition below is an obligation over descriptions
whose published facts CAN all hold at once, which is every description
the producer writes. This contract's invariants do not tie every pair of
fields together, and deliberately so — a loader that had to decide
whether a whole SET of counts was jointly satisfiable would be doing the
generator's work at the wrong end of the run — so a strict loader
accepts a small number of hand-made documents that no twin can satisfy.
A one-character declared identifier published as whole numbers with
`n_all_digits` below `n_present` is one: no single character is both a
whole number and outside the figures.

**Such a document is REFUSED, and a twin is never written from it.**
Plan P2-D6's feasibility rule 5 settles this and revision 4 of this
contract contradicted it (review item P2-C5-F4): the
generation-feasibility stage runs after the loader and before any cell
is built, and where the published facts are PROVED to have no joint
answer it refuses GENERATION rather than the description — the message
says the profile is valid, names the two facts that cannot both hold,
and gives remediation that does not assume the person still holds the
table. The method's G12 carries the closed list of those refusals, the
one-character whole-number identifier above among them. Saying instead
that the generator meets what it can, recounts the fact and names it in
the report turned a description the ratified plan settles into a twin
somebody receives with no signal that anything was wrong, and the plan
reserves the report line for facts a rule CAN meet.

**This is not a licence anywhere else.** Where an exact answer exists,
producing it is the obligation, and an implementation that misses a
reachable count is defective rather than approximate — that is owner
decision 4 and it is what `docs/spec/generation-method-v1.md` G9.5's
packing rule requires. "The published facts cannot all hold" means no
assignment satisfies them, proved, not "the first rule I tried did not
find one".

### 9.1 Top level

| key | disposition | note |
|---|---|---|
| `columns` | STRUCTURAL | membership and order: S1, S2, S3 |
| `source` | STRUCTURAL | membership: the five keys of section 4.3 |
| `profile_version` | LOADER-ONLY | |
| `settings` | LOADER-ONLY | whole subtree |
| `created_with` | LOADER-ONLY | |
| `publication_notes` | LOADER-ONLY | whole subtree |
| `relationships` | LOADER-ONLY | whole subtree |
| `n_rows` (document) | EXACT-OBSERVABLE | the twin has this many data rows |
| `n_columns` | EXACT-OBSERVABLE | the twin has this many columns |
| `source.encoding` | REPORT-ONLY | the twin is always UTF-8 with LF (residual R-P2-5) |
| `source.used_fallback_encoding` | REPORT-ONLY | |
| `source.header_source` | EXACT-CONTROL | decides whether a header row is written at all |
| `source.header_by_convention` | REPORT-ONLY, required sentence | section 4.3 |
| `source.header_evidence` | REPORT-ONLY, required sentence | section 4.3 |

### 9.2 Universal per-column fields

| field | disposition |
|---|---|
| `n_present`, `n_missing` | EXACT-OBSERVABLE |
| `name` | EXACT-OBSERVABLE when a header is written, else EXACT-CONTROL |
| `position`, `role`, `statistical_type`, `quality_state`, `structural_role` | EXACT-CONTROL |
| `missing_by_class`, `missing_by_source` | REPORT-ONLY — every absent cell is written empty |
| `n_numeric`, `n_not_numeric`, `n_out_of_range`, `n_contradictory` | EXACT-OBSERVABLE by class-preserving construction |
| `n_sentinel_candidates_unpublished`, `sentinel_verdicts`, `detection_evidence`, `remarks` | REPORT-ONLY |

`n_distinct` and `n_distinct_folded` are universal keys whose disposition
is set per role group, in 9.3 to 9.7.

### 9.3 `empty`

| field | disposition |
|---|---|
| `n_distinct`, `n_distinct_folded` | EXACT-OBSERVABLE — both `0`, trivially met by an all-absent column |

`empty` is neither a label, an invention nor a distribution role, and it
carries no per-column `n_rows`. Its dispositions are stated separately
for exactly that reason.

### 9.4 The numeric roles: `count`, `continuous`

| field | disposition |
|---|---|
| `percentiles.min`, `percentiles.max` | EXACT-OBSERVABLE |
| `percentiles` interior rungs (`p01` … `p99`) | APPROXIMATED, inside a rung-by-rung two-sided envelope — fixed by `docs/spec/generation-method-v1.md` G5.6, restated as G12.2 |
| `n_zero`, `n_negative`, `std_unrepresentable`, `n_negative_unrepresentable`, `n_used_in_statistics`, `n_left_out_of_statistics`, `numeric_share` | EXACT-OBSERVABLE |
| `integer_valued` | EXACT-OBSERVABLE, routed by the published FACT and not by role |
| `mean`, `std`, `skew` | APPROXIMATED, fixed formula and two-sided bound — both fixed by `docs/spec/generation-method-v1.md` G12.3 |
| `n_distinct`, `n_distinct_folded` | EXACT-OBSERVABLE using the spellings owner decisions 7, 8 and 10 permit — the ordinary case; APPROXIMATED under the two-sided envelope only where even those cannot supply the count, with the report naming the profile's count beside the twin's. The envelope is fixed by `docs/spec/generation-method-v1.md` G12.8, and BOTH of its ends are measured and printed on every run, because a fallback whose range is never shown is a fallback a reader cannot check (review item P2-C2-F4) |
| `numeric_styles` | EXACT-OBSERVABLE against the recount identity of section 7.5.7: every published count is met or exceeded, the three forms the remainder cannot reach are exact, and the remainder is spelled by its own cells' values |
| `n_rows` (echo) | LOADER-ONLY |

A mutant that collapses the nine interior rungs onto the endpoints must
FAIL the rung envelope. So must a mutant that ignores, permutes or swaps
rungs.

### 9.5 The label roles: `constant`, `binary`, `categorical`

| field | disposition |
|---|---|
| `levels` (normalized `label` and `count`) | EXACT-OBSERVABLE |
| `variants`, `variants_withheld` | EXACT-OBSERVABLE |
| `suppressed_levels`, `suppressed_level_counts`, `suppressed_rows` | EXACT-OBSERVABLE |
| `n_distinct_folded` | EXACT-OBSERVABLE |
| `n_distinct` | EXACT-OBSERVABLE where the published variants and the withheld-variant map supply enough spellings — the ordinary case; APPROXIMATED under the two-sided envelope only where they do not, with the report naming the profile's count beside the twin's. The envelope is fixed by `docs/spec/generation-method-v1.md` G12.7 |
| `level_ceiling` | LOADER-ONLY |

### 9.6 `datetime`

| field | disposition |
|---|---|
| `earliest`, `latest` | EXACT-OBSERVABLE in the representation owner decision 5 fixes, which is the ratified plan's own wording. No corner, no exception: the last second of a leap minute is written back unchanged (below, and `docs/spec/generation-method-v1.md` G7.5) |
| `date_percentiles.min`, `date_percentiles.max` | EXACT-OBSERVABLE, in the same representation and on the same terms. No corner, no exception: they are the same two instants, and D11 makes that a rule the loader enforces rather than a sentence a document may contradict |
| `date_percentiles` interior rungs | APPROXIMATED — the window is fixed by `docs/spec/generation-method-v1.md` G12.4 |
| `resolution`, `time_precision`, `subsecond_digits`, `utc_offsets`, `earliest_utc_offset`, `latest_utc_offset` | EXACT-OBSERVABLE, outside the withheld-offset corner below |
| `datetimes_read_at` | EXACT-OBSERVABLE outside the withheld-offset corner — derived from the offset diversity present in the cells, so it is recomputable from the written twin and must be checked that way. A dispatch assertion cannot detect a twin that reprofiles from `utc` to `local` because one invented rare offset changed the diversity while the pooled offset map and the endpoints still matched |
| `format` | REPORT-ONLY — it names the real file's parser family, and owner decision 5 chooses ISO twin syntax at the recorded precision, not the source's lexical family (residual R-P2-7) |
| `n_unparsed` | EXACT-OBSERVABLE as counted neutral stand-ins, explicitly OUTSIDE the parsed-value representation obligation |
| `n_distinct`, `n_distinct_folded` | APPROXIMATED — the envelope is fixed by `docs/spec/generation-method-v1.md` G12.5, and it is stated there that it need not contain the published count |

Datetime cardinality has its own explicit bound so that one
implementation cannot bound datetime distinctness while another ignores
it.

**The one corner this matrix names, rather than leaving it to the
method alone** (review item P2-C1-F8). The method specification already
names it and requires it to be measured and named in the report on
every run; a matrix that claimed those fields were exact in every case
would be a matrix an implementer trusts and a report the same
implementer then cannot make honest.

1. **Withheld offsets.** Where every offset of a column fell below the
   floor, `utc_offsets` collapses to a single `(withheld)` entry and the
   endpoint offset fields read `(withheld)` too. The profile never says
   which offsets those cells carried, so the twin writes them with no
   offset at all: `utc_offsets` recounts as `(none)`, the endpoint
   fields recount as `(none)`, and `datetimes_read_at` can fall from
   `utc` to `local` because the twin holds one offset kind where the
   real column held several. All four are then REPORT-ONLY for that
   column, with the achieved value named beside the published one
   (`docs/spec/generation-method-v1.md` G7.4, G12). It touches those
   four fields and no others: `earliest` and `latest` are the instants
   themselves, which a cell carrying no offset still gives back exactly.

**THE LAST SECOND OF A LEAP MINUTE IS NOT A CORNER, AND MAY NOT BE MADE
ONE** (review item P2-C2-F5). `SS` of `60` is a reading the canonical
form above admits because a real reader accepts one, and the ratified
plan makes both endpoints exact in owner decision 5's representation
with no exception at all (`docs/plans/phase-2-generator.md` revision 5,
P2-D6, the datetime paragraph). A twin cell carries it: the two
endpoint cells are written from the published endpoint's OWN fields
rather than through the whole-second ordinal arithmetic the interior
ranks use, so `2024-11-02 04:55:60` is written `2024-11-02T04:55:60`
and reads back character for character (`docs/spec/generation-method-v1.md`
G7.5). An earlier revision of this section made that endpoint
REPORT-ONLY on the reasoning that the ordinal space has no room for the
value. The reasoning was true of the ordinal space and false of the
obligation: no owner decision authorized moving the endpoint out of the
exact class, an exact representation exists, and lowering a ratified
bar to fit an implementation is not available to this document. The
disposition is restored, and section 9's head governs what remains.

**And what a previous repair left standing beside it is refused, not
reported** (review items P2-C3-F2 and P2-C4-F1). That repair restored
the disposition above and then wrote a second paragraph here saying that
a hand-made description publishing an endpoint no cell of its own
recorded shape can show — seconds on a column whose `time_precision` is
`minute`, or `SS` of `60` published while `datetimes_read_at` is `utc` —
would have that endpoint met as far as it could be, recounted and named.
The method said the same and the generator did it. The repair AFTER that
one refused those two pairs and left a third standing in the method: an
endpoint on the shared clock whose own offset carries its cell off the
end of the calendar. Each is an exception, whatever it is called: this
table says the two ends are exact with no exception, and a document the
loader ACCEPTS whose end the twin then changes makes the sentence false
for every consumer who reads it. No pair of the three is now loadable.
**D10 refuses all three**, exactly as D6 refuses the
`date`-beside-`datetime` pair and for the same reason: published facts
that no cell can show at once, decidable from the fields themselves, are
settled in the description rather than paid for in the twin. The
producer writes none of them, so this refuses nothing a real table can
express, and D11 ties `date_percentiles.min` and `.max` to the same two
texts so the ladder ends cannot carry what the endpoints may not.

The head of section 9 still governs the documents whose facts cannot all
hold in ways two fields do not settle — a whole set of counts with no
joint answer is the generator's question, not the loader's. It is not a
route by which an end this contract calls exact becomes a line in the
report.

Outside that one corner, every field in this table means exactly what
its disposition says.

### 9.7 The invention roles

**`free_text`**

| field | disposition |
|---|---|
| `length`, `words` | STRUCTURAL — the container's own key carries no VALUE obligation; its membership is the four and three keys below, and every one of them is disposed in its own right |
| `length.min`, `length.max`, `n_all_digits`, `n_code_alphabet`, `n_distinct_by_occurrences` | EXACT-OBSERVABLE |
| `words.min`, `words.max` | EXACT-OBSERVABLE, with no corner and no exception. A cell of `L` characters holds at most `(L + 1) // 2` space-separated words, so a document publishing a word extreme its own published length cannot carry — more words than `length.max` holds, or a floor under every value that the `length.min` value cannot reach — is a document whose facts cannot all hold, and generation is refused before any cell is built (`docs/spec/generation-method-v1.md` G12, `generation-words-exceed-length`). A real column cannot produce that pair. Revision 4 clamped the word count and named the miss instead, which is review item P2-C5-F4 |
| `length.mean`, `length.p50`, `words.mean` | APPROXIMATED, two-sided bounds — the bounds are fixed by `docs/spec/generation-method-v1.md` G12.6 |
| `n_distinct`, `n_distinct_folded` | EXACT-OBSERVABLE |

**`identifier`**

| field | disposition |
|---|---|
| `min_length`, `max_length`, `n_all_digits`, `n_code_alphabet` | EXACT-OBSERVABLE in every case, since owner decision 6 keeps the length |
| `all_whole_numbers` | EXACT-OBSERVABLE in every case, since owner decision 6 keeps the length. A published length range in which a value that must stand outside the figures can be no whole number at all — one character cannot be both — is a document whose own facts cannot all hold, and generation is refused before any cell is built (`docs/spec/generation-method-v1.md` G12, `generation-whole-numbers-need-room`). No producer-written profile carries that pair |
| `n_distinct`, `n_distinct_folded`, `n_distinct_by_occurrences` | EXACT-OBSERVABLE outside owner decision 6's infeasible corner; all THREE REPORT-ONLY inside it, with the report naming the achieved value beside the published one |

**What the whole-number row cost, and how both shapes were settled**
(review item P2-C5-F4; closed by Phase 3 plan P3-D8.1, owner decision 1,
2026-08-12). Two shapes a real table produces used to cost
`all_whole_numbers`, and neither does now.

The first was a length end that G9.6 pinned onto a group whose band has
no whole-number spelling at that one length, where the source's own
values show another pairing that holds every published count. It closed
when the length ends and the bands were settled in ONE packing rather
than pinned first, as G9.5 already does for free text: the packing walks
every carrier pair and finds the pairing the source's values prove
exists.

The second was a published length range whose longest value is two
characters, where some value has to stand in the code alphabet — the
only two-character whole numbers outside the figures begin with a sign,
and G9.1 keeps a made-up value from beginning with one, because that is
the character common spreadsheet software reads as the start of a
formula. The implementation met the count by writing the sign anyway,
which is a ratified rule traded for a published count, and left the
report's formula paragraph telling the reader that an invented cell was
a value the description had published. **The owner settled it as a
refusal, not as a lesser outcome**: the two-character code family is
withdrawn, and a description it leaves with no spelling meets
`generation-whole-numbers-need-code-room` — the fifth refusal of method
G12, landed there as an amendment.

`all_whole_numbers` is therefore EXACT-OBSERVABLE in every case a twin
is written at all, which is what the ratified plan holds it to, and this
contract grants no lesser outcome for it.

**`numeric_unrepresentable`**

| field | disposition |
|---|---|
| `n_whole`, `n_fraction`, `n_whole_unknown`, `n_positive`, `n_negative`, `n_sign_unknown`, `n_distinct_by_occurrences` | EXACT-OBSERVABLE |
| `n_distinct`, `n_distinct_folded` | EXACT-OBSERVABLE |
| width | not published at all (residual R-P2-1) |

**The fold-collision obligation.** On the invention roles both
distinctness counts are EXACT-OBSERVABLE, which obliges the invention
alphabet to REPRODUCE FOLD COLLISIONS when the profile shows folded below
raw. That obligation is binding and non-trivial: a real 200-row
single-character identifier profile publishes 200 raw and **122** folded,
so 78 values must fold onto a partner.

**The obligation is the WHOLE fold, both halves of it** (P2-C2-F6). A
folded identity is this document's own definition at section 2: the
cell's text after TRIMMING and a Unicode `casefold()`. Two spellings
therefore collide when they differ in case, in edge spacing, or in both,
and a construction reaching for only one of the two answers fewer
collisions than the profile can legitimately publish. A column of `a`,
` a`, `a ` and ` a ` publishes four raw spellings, one folded identity
and the length range 1 to 3, and every one of those facts is
EXACT-OBSERVABLE at once — the source column is the proof that they hold
together. Losing the folded count there is not owner decision 6's
infeasible corner and may not be named as one; the constructions that
meet it are `docs/spec/generation-method-v1.md` G9.3, and the alphabet
counts survive them because both of those are read after trimming as
well (sections 9.6 and 9.7 above).

### 9.8 The all-different obligation, and the three places it cannot bind

Whenever a column publishes `n_distinct == n_present`, its present values
are all different, on every role, in that column's own notion of
equality — because an undeclared key column arrives as free text or as a
numeric role, not as an identifier. **The obligation can bind only on
facts the profile actually publishes.** Where the raw distinctness of a
column was produced by something the disclosure rules WITHHELD, the twin
cannot reproduce it without making facts up, so raw distinctness is
REPORT-ONLY there and the report names the achieved count beside the
published one. Three instances are known and each is tested:

1. **Declared identifiers** whose published length range cannot supply as
   many distinct values as the column has rows (owner decision 6,
   section 6.8).
2. **Label columns** whose values differ only before the fold — resolved
   by owner decisions 9 and 11, which publish the variants, so the
   obligation now HOLDS for labels wherever the variants are visible and
   falls back only beneath the floor (section 7.4).
3. **Datetime columns whose offsets are withheld.** A 30-row column of
   ten rare offsets over 15 dates publishes
   `n_present == n_distinct == 30` while `utc_offsets` collapses to
   `{"(withheld)": 30}`: the obligation fires, but the profile never says
   which offsets made those 30 spellings distinct, so the twin holds only
   15 instants and no published way to spell them apart. Where the same
   column's offsets ARE published, the obligation holds and the twin uses
   them.

Stating the obligation as one rule with named instances is what stops a
fourth instance arriving undetected.

---

## 10. The loader

The strict loader is the first implemented Phase 2 artifact and the ONLY
way generation receives a profile. It is fail-closed: a document it
cannot prove conforming is refused, never repaired, never partially
accepted.

### 10.1 The order of operations

The order is normative, because it decides which message a person sees
when a document is wrong in more than one way, and the most useful
message is the one nearest the cause.

| step | what happens | refusals it can raise |
|---|---|---|
| 1 | resolve and open the profile path | R1, R2, R3 |
| 2 | read the bytes and decode as UTF-8 | R4, R19 |
| 3 | the bounded structural pre-scan over the TEXT, using only string operations, before any parse | R8, R9 |
| 4 | parse with a plain JSON parse — no callback slot of any kind is involved | R5 |
| 5 | read `profile_version` and check it is exactly the integer 4 | R11, R12 |
| 6 | canonical round-trip: re-serialize under section 3.2 and require byte equality with the file's text | R6, R7, R10 |
| 7 | schema and invariant validation, top level then columns in list order | R13 … R18 |
| 8 | build and return typed objects | — |

**Why the version check precedes the round-trip.** Direction-correct
version advice is more use to a person than a complaint about canonical
form, and an older or newer document is very likely to be canonical under
its own rules and to fail this one's for reasons that would only confuse.
The consequence is stated rather than hidden: at step 5 the loader is
reading a value the round-trip has not yet proved unique, so a document
with a duplicated `profile_version` key is described by its last value —
and is then refused a moment later at step 6 anyway.

**Why the pre-scan precedes the parse.** Both bounds exist to protect the
parser itself; checking them afterwards would be checking them after the
cost has already been paid.

### 10.2 What the loader does NOT do

- **No feasibility check.** The loader performs no generation
  feasibility check whatsoever. That is a separate stage, run after
  loading and before generation, so that a contract-valid document never
  becomes unloadable and a refusal to GENERATE is never mistaken for a
  claim that the profile is invalid.
- **No repair.** It does not normalize, reorder, coerce, default, or
  fill. A document that is not canonical is refused, not rewritten.
- **No table.** It accepts a filesystem path to the profile and nothing
  else. It constructs no table path, no table handle, no table object and
  no raw cell collection, at any layer (plan P2-D1).

### 10.3 The two parser bounds

**Exactly two bounds exist in this phase.** Neither is reachable by any
producible profile, because neither scales with the table.

| bound | value | why |
|---|---|---|
| maximum nesting depth | **32** | the document is six deep (section 3.4), and depth is a function of the contract's shape, not of the data |
| maximum length of a single JSON NUMERIC TOKEN | **64 characters** | an arbitrarily long numeric literal costs quadratic parse time, while the producer's longest published number is far shorter |

**The pre-scan.** Both are checked by a bounded first-party structural
pre-scan over the document text using only string operations, before
parsing. The scan is string-literal aware:

- a `"` outside a string opens one and a `"` inside one closes it, except
  where it is preceded by an odd number of backslashes;
- inside a string, nothing counts: no brace, no bracket, no digit;
- outside a string, `{` and `[` increase the depth and `}` and `]`
  decrease it; the deepest depth reached is compared with 32;
- outside a string, a NUMERIC TOKEN is a maximal run beginning at `-` or
  a digit and continuing over the characters `0`–`9`, `.`, `e`, `E`, `+`
  and `-`. Its length in characters is compared with 64.

**Near-limit-valid and one-over-limit tests are required for each of the
two bounds.**

**No other limit exists anywhere in this phase.** No document-byte cap,
no container-entry cap, no producer-side cap, and no string-length cap
beyond the reader's own shipped field limit. A profile too large for the
machine fails on the catalogued memory-exhaustion path exactly as
Phase 1's reader does, so the two phases promise the same thing. A
container-entry limit was considered and REMOVED: every column
contributes one entry to `columns`, so a ten-million-entry ceiling is a
ten-million-COLUMN ceiling, which Phase 1 never promised to stop at. A
producer-to-loader boundary test asserts that a genuine wide-table
profile loads.

### 10.4 The canonical round-trip

The loader parses the text with a plain JSON parse, re-serializes the
resulting value under section 3.2's canonical rules, and requires the
result to equal the file's text byte for byte.

**What this single check catches**, each verified before being written
here:

| defect | why the round-trip catches it |
|---|---|
| a duplicated key | the parse keeps one value; re-serializing writes the key once, so the text is shorter than the file |
| keys in any order but ascending | re-serialization sorts, so a reordered document does not come back the same |
| a number spelling that is not the shortest round trip of its own value — `1.0e2`, `2.50`, `1E5` | re-serialization writes the shortest form of the parsed value, `100.0`, `2.5`, `100000.0`, which differs |
| any indentation, spacing or separator but the canonical one | re-serialization fixes the layout |
| `NaN`, `Infinity`, `-Infinity`, which a plain parse accepts | re-serialization refuses to write them at all (R7) |
| an escaped lone surrogate, such as `"\ud800"` | re-serialization cannot encode it as UTF-8 (R6) |
| a missing or extra terminal newline | the canonical text has exactly one |

**What it does NOT catch, stated because an earlier revision said it
did** (review item P2-C1-F8):

- **A trailing `.0` on a whole-valued number passes this check.** `2.0`
  parses to a float and re-serializes as `2.0` under 3.2.1, byte for
  byte. Where the field is typed integer, T1 refuses it at step 7
  (R15); where the field is typed number, it is a correct canonical
  document and there is nothing to refuse.
- **`+5` and `05` never reach this check.** JSON has no grammar for a
  leading `+` or a redundant leading zero, so the plain parse of step 4
  stops on them and the person sees R5 with the position the parse
  stopped at.

Both are worth stating because a table row claiming the round trip
catches them is a row an implementer builds a test around, and the test
would then pass for the wrong reason.

**No callback slot is involved.** The check is a re-serialization and a
byte comparison; it does not install a parse hook of any kind, and the
offline policy's callback rules are not engaged by it.

### 10.5 Type rules the loader enforces

JSON's type system is looser than this contract's, so four rules are
stated explicitly.

**T1 — integers are integers.** A field typed "integer" must be a JSON
integer: no fractional part, no exponent. `2.0` is refused where `2` is
required. This is a real distinction, because `2.0` survives the
canonical round-trip unchanged.

**T2 — booleans are not integers.** In several host languages a boolean
is a subtype of integer. A field typed "integer" refuses `true` and
`false`; a field typed "boolean" refuses `0` and `1`.

**T3 — numbers may be integers.** A field typed "number" accepts both a
JSON integer and a JSON float, and reads the same value from either.
`mean: 2` and `mean: 2.0` are both canonical — they are the two kinds
of 3.2.1, and this contract does not say which kind a producer holds a
whole-valued statistic in, so a loader that refused one would refuse a
conforming document. The shipped producer holds these statistics as
floats and therefore writes `2.0`.

**T4 — null is a value, not an absence.** A field whose type permits
`null` still has its key present. A key that is absent is a missing
required key (R14), never a null.

### 10.6 Version handling, with direction-correct advice

`profile_version` MUST be exactly the integer `4`. Two refusals, and the
difference between them is the whole point.

**R11 — an OLDER profile** (`profile_version < 4`). The advice is to make
the profile again by re-running `synthtwin profile` on the table. That
advice is safe to give, because the person who holds an old profile of
their own table is normally the person who holds the table.

**R12 — a NEWER profile** (`profile_version > 4`). The advice is to
UPDATE synthtwin, and never to re-run a profiler. A newer profile means
this generator is behind, and telling somebody to re-run a profiler on a
machine that may not hold the table — or that may hold a different
table — is advice that cannot be followed and may be acted on anyway.
The message says which version this synthtwin reads and which version the
document claims.

Neither message quotes anything from the document except the two version
numbers.

### 10.7 The refusal catalogue

Every refusal on this path has its own plain-language message, an
exact-shape test and a reachability test. Every message says what
happened and what to do next, in words a person who does not program can
act on. **No message on this path quotes `n_rows`**, because allocation
can fail before any field is validated and a message that names a row
count it never read is a message that lies.

| id | trigger | the message says |
|---|---|---|
| R1 | the profile path names nothing | the exact path, that nothing is there, and to check the name |
| R2 | the profile path cannot be read | the exact path and that permission or the drive is the likely reason |
| R3 | the profile path is a folder | the exact path, that it is a folder, and to name the `-profile.json` file inside it |
| R4 | the bytes are not valid UTF-8 | that the file is not text synthtwin can read, and that a profile is always written by `synthtwin profile` |
| R5 | the text is not JSON | the position at which the parse stopped, and that the file may have been edited or truncated |
| R6 | an escaped lone surrogate | that the file holds a character that cannot be written as text, and that the profile should be made again |
| R7 | a non-finite number the parser accepted | that the file holds a number that is not a number, and that the profile should be made again |
| R8 | nesting deeper than 32 | the limit, that no profile synthtwin writes is anywhere near it, and that the file is not one synthtwin wrote |
| R9 | a numeric token longer than 64 characters | the limit and the same conclusion |
| R10 | not canonical, including a duplicated key | that the file is not in the exact form synthtwin writes, that an editor or a merge may have changed it, and to make the profile again |
| R11 | `profile_version < 4` | both versions, and to re-run `synthtwin profile` |
| R12 | `profile_version > 4` | both versions, and to update synthtwin — never to re-run a profiler |
| R13 | an unknown key | the key, its place in the document, and that this synthtwin does not know it |
| R14 | a missing required key | the key, its place, and which role or block requires it |
| R15 | a wrong type | the key, what was found, and what was required |
| R16 | a value outside its range or enumeration | the key, the value, and the permitted range or list |
| R17 | a violated invariant | the invariant's own words, the two quantities that disagree, and where each lives |
| R18 | `relationships` carries non-null content | the key, that this synthtwin does not carry cross-column structure, and that a newer synthtwin is needed |
| R19 | memory exhausted while loading | that the machine ran out of memory for a file of this size, and what to try — a machine with more memory, or a profile of fewer columns |

R13 to R17 each name the KEY and the RULE. A refusal that says only that
something was invalid is a bug report against synthtwin, not an error
message.

### 10.8 What the loader returns

Typed objects: one document object holding the top-level facts, the
source block, the settings block, the empty relationship manifest, and a
list of column objects in list order. The list order of the returned
column objects IS the order of `columns` (S3), and every consumer walks
it in that order: schema order, output column order, RNG consumption
order.

---

## 11. The carried condition: invention domain capacity

Plan review round 5 raised, and the plan CARRIED rather than settled, one
condition that touches this contract's obligations without being one of
its rules (its item P2-R5-F4, "finite invention domain").

**The condition.** Several fields of this contract oblige the generator
to produce a stated number of distinct invented values — raw
`n_distinct` and `n_distinct_folded` on the invention roles (section
9.7), the fold-collision obligation, the invented spellings that
`variants_withheld` calls for (section 7.4), and the invented labels that
`suppressed_level_counts` calls for. Every one of those obligations is
finite only if the alphabet the generator invents from is large enough.
The alphabet is finite, so for every one of them there exists a profile
whose published counts exceed the domain's capacity.

**Where it is owned.** The plan carried this to the
**method-specification gate**, bounded: `docs/spec/generation-method-v1.md`
fixes the invention domain and its capacity rule, with a **named
refusal** where capacity cannot be met. It is not this contract's to
settle, and this contract does not settle it.

**What this contract does say about it, so the carry is not a hole.**

1. The condition changes no rule here. A profile that exceeds the
   invention capacity is a VALID version 4 profile and the loader accepts
   it. The capacity question belongs to the generation-feasibility stage,
   which runs after loading (section 10.2).
2. Where the method specification's capacity rule cannot be met, the
   outcome is a refusal of GENERATION, never a claim that the profile is
   invalid: the message says the profile is valid, names the two facts
   that cannot both hold, and gives remediation that does not assume the
   person still holds the table.
3. The one capacity conflict the PLAN already settled is outside the
   carry: a declared identifier whose length range cannot supply enough
   distinct values is governed by owner decision 6 — length wins, values
   repeat, three distinctness facts become REPORT-ONLY, the report names
   all three (section 6.8).
4. The domain is widened before any of this is asked: identifier and text
   alphabets include upper and lower case — which is also what lets fold
   collisions be placed — and the full printable ASCII range.

A reviewer checking this contract for completeness should read this
section as the record of a known gap with a named owner, not as a rule.

---

## 12. What changed from version 3

Version 4 is version 3 plus five additions. **Nothing was removed and
nothing changed shape.** Every version 3 key keeps its name, its type,
its meaning, its permitted values and its position in the document.

| # | addition | where | governed by |
|---|---|---|---|
| 1 | `statistical_type`, `quality_state`, `structural_role` | every column block | owner decision 1, plan P2-D3 |
| 2 | `n_distinct_by_occurrences` | `free_text` and `numeric_unrepresentable` blocks (version 3 had it on `identifier` only) | owner decision 2, plan P2-D4 |
| 3 | `relationships` | the top level | owner decision 3, plan P2-D5 |
| 4 | `variants`, `variants_withheld` | every published level entry on the three label roles | owner decisions 9 and 11 |
| 5 | `numeric_styles` | `count` and `continuous` blocks | owner decision 10 |

**What a version 3 consumer must do.** Version 4 is not backward
compatible for a STRICT consumer, and deliberately so: a strict version 3
loader refuses a version 4 document because five keys it does not know
have appeared, and that refusal is correct. The additions are what make
the profile a sufficient input for the generator, which version 3 was not
for label columns, for repetition on free text, or for the reader's
inferred numeric type.

**What the version number therefore means.** `profile_version` advances
whenever a key appears, disappears, or changes meaning. It advanced from
3 to 4 for the five additions above. It advances again the first time any
slot of `relationships` is filled.

**The disclosure delta of version 4**, stated in one place because it is
the part a person must be able to weigh:

- addition 1 publishes no new fact about the data: the axes are derived
  from `role`, which version 3 already published;
- addition 2 publishes group SIZES about unnamed groups on two more
  roles, under no floor, exactly as version 3 already did on `identifier`
  (section 7.2);
- addition 3 publishes nothing at all: eight nulls;
- addition 4 publishes the exact spellings of labels the profile already
  published, each governed by the same floor as a whole label
  (section 7.4.5). This is the only addition that carries new source
  text, and it is named in `SECURITY.md`, in the profiler summary and in
  the generation report (residual R-P2-11);
- addition 5 publishes counts of spelling FORMS, floor-governed, carrying
  no value, no magnitude and no spelling (section 7.5).

All three Phase 2 artifacts — profile, twin and report — carry
real-derived published facts, and all three are handled under the
institution's rules for real-derived material. synthtwin claims no formal
privacy guarantee.

---

## 13. Decisions this contract took, and why

The plan fixed every mechanism; in the places below it named a fact
without fixing its exact shape, and this contract fixed the shape. Each
is listed so a reviewer can accept or reject it here, at the cheapest
place, rather than discover it in code.

**13.1 `numeric_styles` appears on `count` and `continuous` only.** Owner
decision 10 says "each numeric column". Three roles could be read as
numeric. The contract restricts the key to the two whose twin cells are
written as parsed numbers from the ladder in decision 8's spelling
family, because those are the roles where the reader's inferred type is
at stake and where the generator can discharge the obligation. A
`numeric_unrepresentable` twin writes invented digit strings at one
canonical invented width (residual R-P2-1), so a style map there would
describe a form the twin already cannot reproduce. If a reviewer prefers
the wider reading, the change is additive: the key would become required
on `numeric_unrepresentable` too, and P1's population would have to be
restated for a role with no representable numbers.

**13.2 The style classification ladder, and its priority order**
(section 7.5.4). Decision 10 enumerated six style NAMES; a total,
order-fixed rule assigning exactly one to every counted cell is what
makes producer and generator agree. Type-bearing forms are tested first
because they are the forms that decide what an ordinary reader infers,
which is the fidelity decision 10 exists to protect.

**13.3 Accounting parentheses and thousands separators are classified by
their digit form, not given styles of their own.** The enumeration is
closed at six, and both forms are excluded from twin output by decision 8
— a comma breaks the CSV row itself. The consequence is recorded inside
residual R-P2-9.

**13.4 `numeric_styles` counts the `n_numeric` cells only** (invariant
P1). Out-of-range and contradictory cells are written by the
class-preserving construction of plan P2-D9, whose forms — an overflowing
digit string, a sign inside brackets — are not expressible in the six
styles, so counting them here would make the map impossible to discharge.

**13.5 `variants` keys are stored EXACTLY, not display-escaped**
(section 7.4.2). `missing_by_source` escapes its keys through the display
boundary, and the difference is deliberate: `missing_by_source` is
REPORT-ONLY and never written into a cell, while `variants` is
EXACT-OBSERVABLE and must read back byte for byte from the twin CSV. The
display boundary applies where a variant reaches a report or command
output.

**13.6 `variants` and `variants_withheld` are REQUIRED on every published
level entry**, even when empty, rather than appearing only where a label
has more than one spelling. This contract has no optional keys: a key
that appears only sometimes is a key a consumer comes to guess about.

**13.7 `variants_withheld` uses the multiplicity-map key form**
(section 5.3) — base-ten keys left-padded to a common width. Owner
decision 11 calls it "the same class of fact as the identifier repetition
multiset", and using the same wire shape means one reader, one writer and
one set of invariants for both.

**13.8 The axis derivation table** (section 5.2). Plan P2-D3 fixed the
three enumerations and said the rule is "derived by a fixed rule the
contract states". The table is that rule. It is a bijection between the
ten roles and the ten `statistical_type` values, with `quality_state`
carrying the two degenerate states and `structural_role` carrying the
declaration.

**13.9 Invariant A4 is a loader refusal.** An axis triple outside the
table is refused rather than repaired, because the generator dispatches
on the axes and a document whose axes and role disagree would route a
column somewhere its own `role` says it does not belong.

**13.10 Ten roles, not nine.** The plan and the Phase 2 task text both
say "the nine roles" while listing ten. The producer's role tuple has ten
entries, and this contract is written against the producer.

**13.11 Two parser bounds, not four.** Section 1.4.

**13.12 The loader checks the version before the canonical round-trip**
(section 10.1), with the consequence of that ordering stated in the same
place rather than left to be discovered.

**13.13 `null` is accepted on `mean`, on every `percentiles` rung, and on
`length.mean`, `length.p50` and `words.mean`** (L3, Q7, section 6.9).
Each is null only where the exact statistic is not a finite binary64
value. No producible profile is known to reach any of them, and the
contract accepts null rather than refusing a document over a case it
cannot rule out; a generator treats a null as an approximated field with
no target and says so in the report.

**13.14 The last second of a leap minute is carried, not excused**
(section 9.6, review item P2-C2-F5). This entry records a bar that was
lowered and put back, because a reader who sees only the current text
cannot tell the difference between a decision and a drift. Closing the
temporal round-trip item of code review round 1, a repair widened the
`SS` field to `60` in the canonical form — correctly, since the shipped
reader accepts one and the producer can therefore publish one — and
then, rather than write that instant back, made the endpoint
REPORT-ONLY in section 9.6 and in the method's G7.5. That traded a
ratified exact fact for a sentence in the report. No owner decision
authorized it, and an exact representation was available the whole
time: the endpoint cells are written from the published endpoint's own
fields, so the seconds field survives. Both documents now say what the
plan says, and a test asserts this wording so the bar cannot be lowered
again in silence.

**13.15 The same bar, lowered a second time in a second place, and the
refusal that ends it** (D10, D11, section 9.6, review item P2-C3-F2).
The repair recorded in 13.14 restored the disposition where the last
reviewer had looked — the matrix row, the method's G7.5 construction —
and then wrote the exception back in the paragraph after it: a
description publishing an endpoint no cell of its own recorded shape can
show would have that endpoint met as far as it could be, recounted, and
named in the report. The method carried the same paragraph and the
generator implemented it, declining to write the published seconds field
whenever `datetimes_read_at` was `utc`. The strict loader accepted such a
description, so the matrix said "no corner, no exception" about
documents this contract itself let through with the end changed. A
sentence restored in one place and weakened in another is the same
lowering, and it is harder to see.

What was put back: the exception paragraph is gone from this contract
and from the method; the generator writes both ends from the published
end's own fields on both clocks, with no case that declines; and the two
pairs that made the exception arguable are now refused by D10, with D11
tying the ladder ends to the endpoints so the same refusal covers all
four texts. D11 also closed a hole nothing had named: with the pair
untied, a hand-made ladder end below `earliest` gave a twin holding
instants earlier than its own published endpoint, and no report said so.
The ends are exact on every description the loader accepts, which is
what the ratified plan asked for and what a consumer reading the matrix
may rely on.

**13.16 The same bar, a third and fourth time, and the registry that
ends the pattern** (D10, section 9.6, review item P2-C4-F1). The repair
recorded in 13.15 refused the two pairs it named and left a third
standing in the method: an endpoint on the shared clock whose own offset
carries its cell outside the years `0001` to `9999`, which the method
called the calendar's own end and had the run name in the report. Its
new wording guard listed that passage as a decided one, so the guard
was green about the very sentence it existed to catch. Counting from the
first, the same obligation had now been lowered four times, each time by
a repair closing the review item that named the previous one.

What was put back: D10 refuses the calendar pair in both directions, so
no description a loader accepts can reach a lesser endpoint; the method
and the generator carry no calendar case; and the guard requires ZERO
endpoint-loss passages rather than listing one.

What is new, and matters more than the sentence: a repository-wide
registry now holds every published fact against the disposition the
ratified plan gives it, and a test reads THIS document, the method and
the plan and fails when any of the three states a weaker outcome for a
fact than the registry does, omits a fact the registry names, or names a
fact it does not. A weaker sentence written anywhere in the three is a
red test rather than a reviewer's find. The registry may authorize a
lesser outcome only where the plan's own words name it, so lowering a
bar means amending the ratified plan in the open — which is the process
this repository already required and the thing four repairs did not do.

---

## 14. Appendix: every enumeration in one place

| enumeration | values |
|---|---|
| `role` | `empty`, `numeric_unrepresentable`, `constant`, `binary`, `datetime`, `count`, `continuous`, `categorical`, `identifier`, `free_text` |
| `statistical_type` | `unknown`, `numeric`, `constant`, `binary`, `datetime`, `count`, `continuous`, `categorical`, `code`, `text` |
| `quality_state` | `ok`, `empty`, `unrepresentable` |
| `structural_role` | `data`, `identifier` |
| `source.encoding` | `utf-8-sig`, `latin-1` |
| `source.header_source` | `file`, `generated` |
| `missing_by_class` keys | `(blank)`, `(declared-missing)`, `(numeric-sentinel)`, `(text-code)`, `(withheld)` |
| `sentinel_verdicts[].verdict` | `read_as_missing`, `kept_as_a_number` |
| `sentinel_verdicts[].reason` | `outlier_and_frequent`, `not_an_outlier`, `too_rare`, `too_few_other_values`, `kept_by_you` |
| `format` | `iso-date`, `iso-datetime`, `compact-date`, `month-first-date`, `day-first-date`, `year-quarter` |
| `resolution` | `date`, `datetime`, `quarter` |
| `time_precision` | `subsecond`, `second`, `minute`, `date`, `quarter` |
| `datetimes_read_at` | `local`, `utc` |
| `numeric_styles` keys | `plain`, `leading_zero`, `leading_plus`, `decimal`, `exponent_lower`, `exponent_upper`, `(withheld)` |
| ladder keys | `min`, `p01`, `p05`, `p10`, `p25`, `p50`, `p75`, `p90`, `p95`, `p99`, `max` |
| `relationships` keys | `deterministic`, `grain`, `hierarchy`, `keys`, `missing_data_process`, `statistical`, `temporal`, `validation_targets` |
| `settings.declaration_matching` | `exact_number_when_it_reads_as_one_else_spelling` |
| `settings.declaration_publication` | `settings_counts_only_columns_unchanged` |
| the pooled-remainder key, everywhere it appears | `(withheld)` |
| the blank-spelling key in `missing_by_source` | `(blank)` |
| the no-offset key in `utc_offsets` and the endpoint offset fields | `(none)` |

**Where `(withheld)` appears, and what it means in each place**

| place | meaning |
|---|---|
| `missing_by_class` | the pooled count of absent-value CLASSES whose own counts fell below the floor |
| `missing_by_source` | the pooled count of absent-value SPELLINGS below the floor |
| `sentinel_verdicts[].candidate` | the block's publication class permits no value of the table anywhere in it |
| `utc_offsets` | the pooled count of cells whose OFFSETS fell below the floor |
| `earliest_utc_offset`, `latest_utc_offset` | that endpoint's offset is one the map is withholding |
| `numeric_styles` | the pooled count of cells whose spelling STYLE was used by too few rows to name |

One token, one meaning: a group too small to name, counted rather than
named. It is never a value, and it is never a key a generator has to
invert.




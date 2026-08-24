# Profile contract, version 6 — the normative specification

**Status: SHIPPED**, as of the Phase 4 wire flip. `synthtwin profile`
writes version 6, the loader reads version 6, and an older description
is refused with the message section 10.2 fixes word for word. Every
rule below describes the file the tree produces today.

**The status paragraph this replaces, and why replacing it is the
point** (the same move version 5 made when it shipped). Until the flip
this document read: "revision 6, 2026-08-21 — the first COMPLETE
statement of this format. **Not ratified.** It is reviewed
adversarially before the implementation it anchors is written, under
the standing process: plans and specifications before the artifacts
they anchor. It joins the disposition seal at its own landing." Both
of the first two sentences became false on the commit that landed the
flip, and a document that goes on describing itself as unbuilt while
the tree ships it is the one surface a reader has no way to correct
from.

**This document is self-contained.** It carries nothing by reference
from version 4 or version 5, replaces nothing by name, and holds no
table of replacements. Every rule, key, enumeration, invariant,
disposition and loader obligation that governs a version 6 description
is written HERE, at its own wording, once. Section 1 states that rule
and what it cost.

**Authority.** The Phase 4 plan `docs/plans/phase-4-columns.md` is the
authority for every decision here; this document is the normative
statement of what a version 6 description may contain. Where the two
disagree the plan governs and this document is defective. The plan's
amendments A-P4-1 through A-P4-12 are part of the ratified text this
document transcribes.

**Versions 4 and 5 keep their sealed text** and keep governing the
descriptions written under them. Nothing here edits what they require.

---

<!-- s1: scope, authority, completeness; terms -->

## 1. Scope, authority, and completeness

**1.1 What this document is.** It is the normative statement of what a
version 6 description may contain. A strict loader and a producer must
both be writable from this text ALONE, without reading the producer's
source and without guessing. Every key that may appear in a version 6
description is named here with its type, its permitted values, what a
null means, which keys may not appear beside it, and which invariants
bind it. Every rule a loader enforces is stated in a form that can be
checked mechanically. A version 6 description is a file some person
may hold, hand to a colleague, or keep for a year; this document says
exactly what may be in it, so a producer knows what to write, a loader
knows what to refuse, and a reader knows what a sentence of it means
without asking anybody.

**1.2 What this document is not.** It does not say how the twin's
values are computed. The transform from (description, seed) to twin
bytes is `docs/spec/generation-method-v1.md`, together with its frozen
neutral reference vectors. It does not say what `synthtwin validate`
checks; that is `docs/spec/validation-method-v1.md`. Neither of those
documents is amended here — each is amended at its own stage, against
this text. This contract says what the generator is given and what it
owes; the method specification says how it discharges that debt.

**1.3 What it governs.** Exactly one artifact: the machine-readable
description file, written by `synthtwin profile` as
`<stem>-profile.json` and read by `synthtwin generate` and
`synthtwin validate`. It does not govern the plain-language summary
written beside it, the twin CSV, the generation report, or the quality
report.

**1.4 The description is the only input the generator receives about
the real table.** The generator never opens the real table, and no
rule in this contract may be satisfied by consulting anything but the
description and the seed (plan P2-D1).

**1.5 The ratified plan governs on conflict.** The Phase 4 plan,
`docs/plans/phase-4-columns.md`, is the authority for every decision
here. Where this contract and that plan disagree on a fact the plan
decided, the plan governs and this document is defective. Where the
plan names a fact without fixing its shape, this document fixes the
shape and says so, in the decisions section, so a reviewer can see
every place a shape was chosen here rather than inherited.

**C6-121 (1.6) — this document states every rule in force, itself.**
There is no carrying by reference. No rule of
`docs/spec/profile-contract-v5.md`, and no rule of
`docs/spec/profile-contract-v4.md`, binds a version 6 description by
being a rule of those documents. Every role, key, enumeration,
invariant, disposition and loader rule that governs a version 6
description is written HERE, at its own wording, once. It follows that
this document contains no supersession table, no "carried unchanged"
register, and no clause of the form "as version 4 has it" or "version
5's rule stands" — and that nothing in it supersedes anything, because
nothing in it is inherited. A sentence that made a version 6
obligation depend on the text of another version's document would be
defective whatever it said.

<!-- framing-ok: this paragraph describes the delta design this
document replaced, so it necessarily names the mechanism the rest of
the document forbids. It states no rule of this contract. -->
**Why, stated because a reader meeting a document this size will ask
what it bought** (owner decision 2026-08-20, plan amendment A-P4-11).
Version 6 was first written as a DELTA over a base that requires total
restatement, and six adversarial review rounds failed to converge on
it. Each rule a delta supersedes is in fact stated in two to four
places — a defining section, version 4's universal-key table, version
4's appendix, and a shipped constant — so every round found another
site superseded in one place and left live in another. At the worst,
version 4's universal-key table pinned `role` at ten names and the
absence map at five keys while version 6 introduces thirteen roles and
six absence classes, so three of its own roles and one of its own
absence classes were unwritable in the very document that introduces
them. None of that was a review failure: a reviewer reads what the
contract says, and a site the contract never mentions is invisible to
them, which is why a seventh round of the same kind would not have
converged either. Under-restatement cannot occur in a document that
carries nothing forward; an implementer working from the text alone —
which is what the whole specification discipline exists for — reads
one document instead of three and reaches a rule without resolving a
chain of supersessions; and the question that consumed six rounds —
"is this replacement total?" — stops being a question anybody can get
wrong.

**The price, stated rather than discovered.** A self-contained
document can disagree with version 4 by transcription error in a way a
delta could not. Every rule stated here is checked against the
artifact that fixes it, and the batteries that pin exact lists — the
disposition registry and the claim inventory — gain the version 6
enumerations, so a list that drifts turns the suite red rather than
waiting for a reader to notice.

**1.7 A description is governed by exactly one version's documents.**
Precedence is by the description's own version integer: this document
governs a description whose `profile_version` is 6,
`docs/spec/profile-contract-v5.md` governs one whose integer is 5, and
`docs/spec/profile-contract-v4.md` governs one whose integer is 4. No
description is ever governed by two. What a producer writes for that
key, and what a loader does with any other integer, is the version
rule and the refusal in the loader section.

**1.8 The older documents keep their sealed text.** Versions 4 and 5
stay in the tree and keep governing the descriptions written under
them. Neither is ever edited to change what it requires — a person
holding a version 5 description must be able to read the rules that
governed it, unchanged, for as long as they hold it. A change to what
version 6 requires is written here and nowhere else. Editorial repair
of an older document — a typo, a broken reference — is not a change to
what it requires and is outside this rule; every one of them still
moves a digest in `tests/disposition_seal.py` and is therefore
visible.

**1.9 Exactly two parser bounds exist**: nesting depth and numeric
token length, fixed in the loader section. Revision 5 of the Phase 2
plan removed the container-entry limit (its item P2-R5-F7) and ruled
that two remain; this document says two in every place it says
anything, so a reader has no count to reconcile. This is not a
contract decision — it is that plan's own revision-5 ruling applied
consistently.

---

## 2. Terms, and how to read this document

### 2.1 Normative words

| word | meaning |
|---|---|
| MUST / MUST NOT | a conforming producer always does this; a conforming loader refuses a document that does not |
| REQUIRED | the key is present in every block of that kind, on every run |
| FORBIDDEN | the key is absent from every block of that kind; a loader refuses a document carrying it |
| OPTIONAL | not used in this contract — there are no optional keys in version 6 |

There are no optional keys on purpose. A key that appears only
sometimes is a key a consumer comes to guess about, and the guess is
what fails silently. Every key listed for a role is present on every
column of that role, including when its content is empty. The rule is
total over the format: where a fact does not apply to a role, the key
is FORBIDDEN on that role rather than sometimes-present, and no key
anywhere in a version 6 description is present on some runs and absent
on others.

### 2.2 The six disposition classes

The disposition class of a field says what the twin owes it. The
classes are the Phase 2 plan's (P2-D6); they are stated here in full
because the loader and the generator are both written against them.

| class | what it means | how it is evidenced |
|---|---|---|
| **EXACT-OBSERVABLE** | the twin reproduces the published value exactly | recounted from the written twin CSV, independently of the generator's own bookkeeping |
| **EXACT-CONTROL** | a metadata or dispatch decision a CSV cannot evidence | typed-object or schema-order assertions, plus a misrouting mutant that must fail |
| **APPROXIMATED** | reproduced under a stated rule inside a two-sided finite-sample bound | measured, checked against both sides of the bound, and named in the generation report with the achieved value beside the published one |
| **REPORT-ONLY** | not reproduced in the twin at all; stated in the generation report | asserted present in the report |
| **LOADER-ONLY** | validated on input; never an output obligation | asserted to impose no output obligation |
| **STRUCTURAL** | a container whose own key carries no VALUE obligation, but which carries membership and order obligations | membership and order asserted; swapped, duplicate, omitted and extra member mutations must each fail |

A field has exactly one disposition. A container's disposition does
not cover its leaves: every leaf under a STRUCTURAL container is
disposed individually, in the disposition matrix.

### 2.3 The vocabulary of the counts

| term | definition |
|---|---|
| **present** | a cell that survived the absent-value rules and the declarations; `n_present` counts them |
| **absent** | a cell counted as holding no value. Every absent cell is counted in one of the six absence classes C6-N3 fixes — five of them naming a reason a cell was read as holding no value, the sixth being the remainder the floor pools — and `n_missing` counts them |
| **raw identity** | a present cell's text exactly as the file spells it. `n_distinct` counts raw identities |
| **folded identity** | a present cell's text after trimming and a Unicode `casefold()`. `n_distinct_folded` counts folded identities, and every published label is a folded identity |
| **the floor** | `settings.small_cell_floor`, the smallest number of rows a published group may cover. Its value is in the document and the document is the only place it is fixed: it is at least 1, and 11 is what `synthtwin profile` writes when nobody asks for another. The settings section states the range, and what a floor below the default gives up |
| **withheld** | held back by the floor and pooled into a counted remainder, never named |
| **the ladder** | the fixed eleven rungs `min`, `p01`, `p05`, `p10`, `p25`, `p50`, `p75`, `p90`, `p95`, `p99`, `max`, in that order |

**Equality per path** (plan P2-D6). `n_distinct` counts RAW present
spellings. `n_distinct_folded` counts FOLDED identities. Numeric
statistics describe PARSED values. Level facts use the FOLDED
identity. Datetime facts use the parsed instant at the recorded
resolution. A conforming implementation never swaps one notion of
equality for another, in either direction.

### 2.4 The closed terms

Section 2.3 fixes the terms the counts are written in. These eight are
the rest of the terms of art this section defines — fifteen in all,
each defined once. A term of art a later section fixes is defined
there and is not restated here, under the same rule that governs every
other statement in this document: it is written once, at its own site.
Where a term names a rule, the table gives the term's meaning and the
named clause gives the rule.

| term | meaning | the clause that fixes its rule |
|---|---|---|
| **the reading rule** | how each cell's raw text became either a value or no value: the blanks, synthtwin's own built-in words, the stand-in numbers, the calendar placeholders, the words named with `--missing-value`, and the words rescued with `--keep-value` | C6-N3, and the absent-cell section entire |
| **the display boundary** | the rewriting that turns a character which instructs a display — a control code, a bidirectional override, a zero-width mark — into a printable form that shows itself, so that printing text cannot scramble somebody's terminal | the spelling-storage rules of the absent-cell maps and of `variants` |
| **the published vocabulary** | the closed list of TWENTY-THREE members C6-31 fixes: eighteen text spellings synthtwin reads as "no value", three stand-in numbers it judges, and two calendar placeholders it judges. It is synthtwin's own, it is the same in every installation, and it contains no text from any table | C6-31 |
| **the exact-spelling member** | the one member of the published vocabulary matched by raw byte equality with the cell, rather than after trimming and case folding | C6-31, C6-32 |
| **a calendar placeholder** | one of the two built-in dates a description may judge as meaning "no value", by the same rule that judges the three stand-in numbers | C6-31, C6-33 through C6-35 |
| **a nothing-publishing column** | a column whose publication class permits no value of the table anywhere in its block: `role` in `numeric_unrepresentable`, `identifier` or `free_text`, or `structural_role` `identifier` whatever the role. The term is BINARY — a column either is one or is not — and the role `empty` does not by itself make a column one | C6-50, C6-51, C6-52 |
| **the affix pair** | the exact prefix text and suffix text that every counted cell of an `affixed_number` column wears around its number | C6-4, C6-5 |
| **the core** | the substring of an affixed cell that the number classifier reads as a number, chosen longest-then-leftmost | C6-4 |

**Why the nothing-publishing term is binary, stated because a reader
who has met the publication classes will expect three of them.** The
publication classes sort the twelve value-publishing roles into
labels, ranges and nothing, and `empty` is in none of the three
because it has no value to publish. That is NOT the same as being
nothing-publishing. An `empty` column nobody declared publishes its
absent-cell source accounting under the floor, exactly as every other
column that is not nothing-publishing does; reading the term as a
three-way partition would force `missing_by_source` empty and both
absence counts to zero on such a column, delete a fact the description
holds today, and make the twin write blank fields where the recorded
spelling belongs. A DECLARED all-absent column is the other case and
it is meant to differ: it carries `role` `empty` with
`structural_role` `identifier`, so the structural override makes it
nothing-publishing, its source map is empty and both absence counts
are zero — and the difference between the two columns is exactly the
difference the person made by typing `--identifier`. The
publication-class section carries the argument in full; the term is
binary here so that no rule quantified over it can pick up the third
class by accident.

---

<!-- s3: encoding and canonical serialization -->

## 3. Encoding and canonical serialization

3.1 The document is a single JSON value: an object. The file is UTF-8
text with LF line endings, no byte-order mark, and exactly one terminal
newline.

**Line endings are the producer's to control, not its platform's.** A
producer that writes the canonical text through a stream whose platform
translates `\n` on the way out emits CR LF, and its file is not
canonical however correct the text it handed over was. The translation
is switched off explicitly rather than assumed absent, so that one
document written on any platform is one sequence of bytes.

3.2 **The canonical text of a document is defined by construction**: it
is what `json.dumps` produces with `sort_keys=True`, `indent=2`,
`separators=(",", ": ")`, `ensure_ascii=False` and `allow_nan=False`,
followed by one newline character. That fixes, normatively:

- every object's keys appear in ascending order of their code points;
- nesting is indented by two spaces per level;
- the separator between members is `,` followed by the newline the indent
  mode inserts; the separator between a key and its value is `: `;
- an EMPTY object is written `{}` and an empty array `[]`, with no
  newline and no indent between the two brackets; a non-empty container
  puts each member on its own line at one further level of indent and
  its closing bracket on a line of its own at the parent's indent. Both
  empty forms are reachable in a conforming document, so neither is a
  case an implementer may leave untested: `publication_notes` is an
  array possibly empty (section 4.5), `levels == []` is valid
  (invariant B8), a multiplicity map may be `{}` (section 5.3), and
  `fraction_widths` is the empty object in case P5.b;
- inside a string, exactly three groups of characters are escaped and
  no others: `\` is written `\\`; `"` is written `\"`; and every
  character U+0000 through U+001F is written with the short escape JSON
  gives it — `\b` (U+0008), `\t` (U+0009), `\n` (U+000A), `\f`
  (U+000C), `\r` (U+000D) — and otherwise as `\u00XX` with LOWER-CASE
  hexadecimal digits. Nothing else is escaped: `/` is written as
  itself, U+007F is written as itself, and non-ASCII characters are
  written as themselves, which the next bullet states as its own rule;
- non-ASCII characters are written as themselves, not as `\u` escapes;
- `NaN`, `Infinity` and `-Infinity` are not writable, so they cannot
  appear in a canonical document;
- numbers are written by the grammar of 3.2.1, which has two cases and
  turns on the KIND of number, not on whether the number happens to be
  whole.

**The key order is over CODE POINTS, and never over what a key
denotes.** Two of this contract's mappings key themselves on the figures
of a whole number, and THEY DO NOT READ THE SAME WAY, so neither may be
inferred from the other:

- `fraction_widths` writes its width keys BARE — no sign, no leading
  zero unless the width is itself zero, no space, no other character
  (C6-29) — so its code point order is not a numeric order. Under the
  code point order `(withheld)` precedes every digit, `1` precedes
  `10`, and `10` precedes `2`; so a `fraction_widths` object carrying
  the widths `0`, `1`, `2` and `10` and a pooled remainder is written
  in the order `(withheld)`, `0`, `1`, `10`, `2`, and any other order
  is a document section 10.4 refuses.
- a multiplicity map — `n_distinct_by_occurrences` and
  `variants_withheld` — pads its row-count keys with leading zeros to a
  uniform width, and section 5.3, which states that key form, gives
  THIS RULE as the reason for it: padded, the canonical sorted-key
  order and the numeric order coincide, where written bare `10` would
  sort before `2`. Section 5.3 fixes the form; this clause only records
  why the form is shaped that way, and a producer that writes an
  unpadded multiplicity key writes a document section 10.4 refuses.

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

**The T1 this clause depends on, stated here because a bare identifier
states no rule.** A field typed "integer" must be a JSON integer, with
no fractional part and no exponent, so `2.0` is refused where `2` is
required; the distinction is real precisely because `2.0` survives the
canonical round trip unchanged. That is the loader's type rule of
section 10.5, and NOT the `time_of_day` invariant that carries the same
letter.

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

**The comparison is over BYTES, and a reader that translates line
endings has not made it.** A file written with carriage returns arrives
as text with none through any reader that decodes with universal
newlines, so a comparison of decoded TEXT alone accepts a file whose
bytes are not the ones a producer writes. A loader that decodes that way
MUST therefore also compare the UTF-8 byte length of the canonical text
with the file's size, and refuse the document when the two differ, under
the same refusal the text comparison raises. The two conditions together
are sufficient: equal text plus equal byte length leaves only one
possible byte sequence, because UTF-8 is a one-to-one encoding of any
text that is not a lone surrogate — and a lone surrogate is refused
separately, before this comparison is reached — and line-ending
translation is the only step that can change the text without changing
the file.

3.4 The maximum nesting depth of a conforming version 6 document is
**six**: document → `columns` → a column block → `levels` → a level
entry → `variants`. Depth is a function of the contract's shape, not of
the data, so no table can raise it.

**The bound as a closed fact about this format**, stated in full because
the three roles `affixed_number`, `time_of_day` and `long_tail_labels`
and every key they carry were checked against it rather than assumed to
leave it alone:

- Exactly two containers stand at the SIXTH level: `variants` and
  `variants_withheld`, both keys of a `levels` entry.
- Exactly two containers stand at the FIFTH: a `levels` entry and a
  `sentinel_verdicts` entry.
- Every other container of this format stands at four or less.

`long_tail_labels` reaches the sixth level and no further: it carries
the same `levels` list of entries carrying the same `variants` and
`variants_withheld` objects that `categorical` carries, under the same
label invariants, and adds no container of its own.

The keys of the other two roles, and every remaining key of this
contract that is not reached through `columns` → `levels` → an entry,
stand at four or less. On `affixed_number` these are `affix_prefix`,
`affix_suffix`, `n_affixed`, the four core-class counts
`n_core_numeric`, `n_core_out_of_range`, `n_core_contradictory` and
`n_core_not_numeric`, and the quantitative set computed over the cores,
whose only container members are the objects `percentiles` and
`numeric_styles`. On `time_of_day` they are `clock_form`, `earliest`,
`latest`, `clock_percentiles` and `n_unparsed`. Elsewhere they are
`fraction_widths` — a key of the block, a sibling of `numeric_styles` —
`resolution_mix`, `min_length`, `max_length`, the `(date-sentinel)` key
of `missing_by_class`, `built_in_dates` as the third list of each
declaration record, whose members are strings, and the `settings` keys
`day_first` and `long_tail_minimum_level`.

---

<!-- s4: the document: top level and settings -->

## 4. The document: top-level structure

### 4.1 Every top-level key

Exactly these nine keys are present. No other top-level key may
appear; a loader refuses one that does, naming it.

| key | JSON type | meaning | disposition |
|---|---|---|---|
| `columns` | array of objects | one block per column of the table, in schema order | **STRUCTURAL** |
| `created_with` | string | the synthtwin version that wrote this document, or `0+unknown` when the installed version could not be read | LOADER-ONLY |
| `n_columns` | integer ≥ 1 | how many columns the table has | EXACT-OBSERVABLE |
| `n_rows` | integer ≥ 0 | how many data rows the table has, not counting a header row | EXACT-OBSERVABLE |
| `profile_version` | integer | the contract version. In this contract, exactly `6` | LOADER-ONLY |
| `publication_notes` | array of objects | per-column plain-language notes about what was held back and why | LOADER-ONLY |
| `relationships` | object | the reserved cross-column manifest; eight keys, every one `null` | LOADER-ONLY |
| `settings` | object | the rules that produced this profile | LOADER-ONLY |
| `source` | object | how the table was read | **STRUCTURAL** |

`settings`, `publication_notes` and `relationships` each carry ONE
disposition covering their whole subtree, because nothing under them
is an output obligation. Their membership rules are still stated
below, because a strict loader enforces them.

**The version key.** `profile_version` is the integer `6`. A producer
writes `6`; a loader reads exactly `6` and refuses every other
integer. It does not upgrade a document written under an older
contract, does not partially accept one, and does not offer to:
converting one would mean making up facts the older rules never held.
The version is read BEFORE the canonical round trip of section 3.3, so
a person handing over an older description is given direction-correct
advice about their own file rather than a complaint about canonical
form. Section 10 carries the loader's order of operations and the
exact words of the refusal.

### 4.2 STRUCTURAL rules for `columns`

These four rules are the whole of what `columns` means as a container.
They are normative, and each has a mutation that must fail (plan
P2-D6, item P2-R5-F6).

**S1 — length.** `len(columns) == n_columns`.

**S2 — position.** For every index `i` counting from zero,
`columns[i].position == i + 1`. Positions therefore form exactly the
set `1..n_columns`, each once, in increasing order along the list.

**S3 — list order is the schema.** The order of `columns` IS:

- the schema order of the table;
- the order in which the twin's columns are written to the CSV, left
  to right, and the order of the header row when one is written;
- the order in which the single RNG stream is consumed — the column at
  index 0 takes its draws first, and every later column's draws follow
  the ones before it.

Without S3, two conforming implementations could serialize the blocks
in different order and route names, type paths, values and RNG bytes
differently while every set-shaped invariant still passed.

**S4 — names.** Column names are non-empty after trimming and are
pairwise distinct as text. Two names that differ only in case, or only
in surrounding spaces, are distinct names and both are kept exactly as
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

**Membership rule.** All five keys are REQUIRED. No other key may
appear under `source`.

**Invariant S5.** `used_fallback_encoding` is true exactly when
`encoding` is `latin-1`.

**Invariant S6.** `header_by_convention` may be true only when
`header_source` is `file`. Generated names are not a convention about
somebody's first record; they are names synthtwin made.

**The required sentence.** When `header_by_convention` is true, the
generation report MUST say, in plain words, that the twin's column
names may in fact be a first data row of the real table rather than
names — not merely that a header was written. Phase 1's R1 residual is
exactly this uncertainty, and a report that says only "a header was
written" hides a warning the profile is carrying (plan P2-D6).

### 4.4 `settings`

An object with exactly these seventeen keys. Its whole subtree is
LOADER-ONLY: nothing in it is an output obligation, and the generator
reads it only to interpret floor-governed facts elsewhere in the
document.

The keys are written here in the ascending code-point order section
3.2 gives every object of a canonical document, so that a reader
auditing the count has a list to audit rather than an arithmetic
claim.

| key | JSON type | range / permitted values | meaning |
|---|---|---|---|
| `categorical_ceiling` | integer | ≥ 1 | the absolute cap on how many different FOLDED values a column may hold and still be described as categories |
| `categorical_floor` | integer | ≥ 1 | the effective cap is never below this, so that a tiny table still has a categorical path |
| `categorical_share` | number | 0.0 ≤ x ≤ 1.0 | the share of the table's ROWS that caps it as well: the effective cap is `min(categorical_ceiling, categorical_share of n_rows)`, never below `categorical_floor` |
| `day_first` | boolean | — | true when the person declared, with `--day-first`, that slashed dates in this table are day-first; false otherwise. Default false. It records that the DECLARATION was made, and not which reading any column took — see below |
| `declaration_matching` | string | exactly `exact_number_when_it_reads_as_one_else_spelling` | the one rule that says which cells a declared value matches: a declared value that reads as a number this format can hold matches every cell holding that EXACT NUMBER, whatever either is spelled like, so `-999` covers a file that writes `-999.00`; any other declared value matches by spelling, after trimming and case folding |
| `declaration_publication` | string | exactly `settings_counts_only_columns_unchanged` | what this block publishes about a declaration and what it does not: counts and synthtwin's own words here, and the columns unchanged |
| `declared_missing_values` | object | exactly the five keys below | the declaration record for `--missing-value` |
| `forced_identifiers` | array of strings | — | the names the person passed to `--identifier`, sorted ascending, pairwise distinct |
| `identifier_minimum_rows` | integer | ≥ 0 | below this many rows nothing is said about a column being all-different, because in a short column almost every measurement is. It decides no role |
| `identifier_uniqueness` | number | 0.0 ≤ x ≤ 1.0 | how different a column's values have to be before synthtwin SAYS SO. It decides no role: nothing decides the identifier role but the person who owns the table |
| `kept_values` | object | exactly the five keys below | the declaration record for `--keep-value` |
| `long_tail_minimum_level` | integer | exactly `11` | the long-tail detection line, recorded on the document's own face |
| `minimum_parse_rate` | number | 0.0 ≤ x ≤ 1.0 | THE line for the numeric roles and for the datetime role, and the only one: at least this share of the present values must read as numbers this format can hold before the column is described as numbers, and at least this share must parse under one date format before it is described as dates. Applied as a COUNT, never as a compared share, so no rounding of a division decides a role |
| `near_threshold_slack` | integer | ≥ 0 | a column is reported as borderline when this many values, or fewer, separate it from a different reading. Counting values rather than comparing shares keeps the report meaningful at the ends of the scale |
| `sentinel_minimum_share` | number | 0.0 ≤ x ≤ 1.0 | the share of present cells a stand-in candidate must reach to count as frequent |
| `sentinel_outlier_iqr_multiple` | number | ≥ 0.0 | how many interquartile ranges beyond the quartiles of the column's other numbers a stand-in candidate must lie to count as an outlier |
| `small_cell_floor` | integer | ≥ 1 | the disclosure floor: the smallest number of rows a group may cover and still be NAMED anywhere in this description |

**C6-20 (membership).** All seventeen keys are REQUIRED. No other key
may appear under `settings`; a loader refuses one that does, naming
it. A block of sixteen keys or of eighteen — one of the seventeen
skipped, or a key of somebody's own added — is a document this
contract does not describe. **No settings key exists for the affix
rule, the clock rule or the calendar-placeholder pass**: those rules
read `minimum_parse_rate`, `small_cell_floor`,
`sentinel_outlier_iqr_multiple` and `sentinel_minimum_share`, which
are already here, and a constant of their own would be a threshold
this block does not record.

**`day_first`, and what it does and does not say.** The key is true
exactly when the person declared `--day-first`, and false otherwise;
the default is false. It records that the DECLARATION was made. It
does not record which reading any column took, because the reading is
evidence-first: where the option is given and a column's slashed cells
are in play, BOTH slashed readings are counted, the reading that
parses strictly more cells wins whatever the declaration said, and the
declaration decides only a count tie. Which reading a column took is
that column's own `format`, and the remark that column carries says
how the winner was chosen and, where the column holds cells only each
reading can parse, that it carries evidence in both directions. The
reason the setting is written down at all is the reason every other
one is: a reader of a description never has to guess which version of
the rules produced it, and a person is never silently overruled,
never silently obeyed against evidence, and never silently obeyed into
free text.

**`long_tail_minimum_level`, and why it has one permitted value rather
than a range.** The key records the detection line of the
`long_tail_labels` rule: a column past the categorical ceiling that no
earlier rule has claimed becomes a long-tail column when at least one
of its folded levels covers `max(small_cell_floor,
long_tail_minimum_level)` rows. Its only permitted value in this
contract is the integer `11`, on the `declaration_matching`
only-value precedent, and a loader refuses any other. The line it
records is a privacy boundary: a settings key that could move it
downward would let a settings combination — a lowered floor included —
widen which columns publish labels, which is exactly what that `max`
exists to prevent. The key exists so that the line is on the
document's own face, and so that a later phase can move it only in the
open, by a change to this contract.

#### The two declaration records

**Invariant S14 (membership).** `kept_values` and
`declared_missing_values` each have exactly these FIVE keys. No other
key may appear under either; a loader refuses one that does, naming it
and the record.

| key | JSON type | contents | disposition |
|---|---|---|---|
| `built_in_dates` | array of strings | which members of the published vocabulary's calendar-placeholder list this declaration named; sorted ascending; pairwise distinct; possibly empty | LOADER-ONLY |
| `built_in_numbers` | array of numbers | which members of its stand-in list this declaration named; sorted ascending; pairwise distinct; possibly empty | LOADER-ONLY |
| `built_in_texts` | array of strings | which members of its spelling list this declaration named; sorted ascending; pairwise distinct; possibly empty | LOADER-ONLY |
| `n_declared` | integer ≥ 0 | how many DIFFERENT values were named this way, different at `declaration_matching`'s own identity — the exact number where the value reads as one, and otherwise the trimmed, case-folded spelling | LOADER-ONLY |
| `values_recorded` | boolean | exactly `false` | LOADER-ONLY |

**Two spellings of one value being one declaration is not a convention
chosen here** — it is the rule that decided which cells the
declaration took, so a count that separated them would be counting
something no column of the description can reflect. A person who types
a value twice is recorded identically to one who typed it once.

**What enters a list.** A declared value enters `built_in_texts` when
it matches a member of the spelling list by that list's own matching
operation — trimmed and case-folded for the seventeen folded members,
raw byte equality for the one exact-spelling member — and what is
written is that MEMBER. It enters `built_in_numbers` when it reads as
a number and that number is one of the three stand-ins, and what is
written is that member's canonical form. It enters `built_in_dates`
when it is one of the two calendar placeholders, and what is written
is that placeholder's canonical day spelling. A declared value that is
none of these enters no list, and `n_declared` counts it exactly as it
counts every other different value named. **No character a person
typed reaches the document through these three lists.**

**Invariant K1 (membership).** Every element of `built_in_texts` is a
member of the published vocabulary's spelling list; every element of
`built_in_numbers` is a member of its stand-in list; every element of
`built_in_dates` is a member of its calendar-placeholder list (section
14.1). A loader refuses any other value, naming it, because a value
outside those lists is a value from somebody's table.

**Invariant K2 (form).** All three arrays are sorted ascending and
pairwise distinct — `built_in_texts` and `built_in_dates` by code
point, `built_in_numbers` numerically. For the canonical ISO day
spellings the two placeholders take, ascending by code point is also
ascending by date. Order is part of the canonical bytes and a producer
may not shuffle it between runs.

**Invariant K3 (the count bounds the lists).** In each record,
`len(built_in_texts) + len(built_in_numbers) + len(built_in_dates)`
is at most `n_declared`. It is `<=` and not `==`, and the inequality is
the only thing a LOADER can check: every vocabulary member in a list
is named by exactly one declaration — two spellings that fold to one
member are one declaration, and no declaration can be in two of the
three lists, since nothing the spelling list holds reads as a number,
nothing it holds is a calendar day, and no stand-in number is a
calendar day spelling — so the count separates exactly into the
members this document names and the values of the person's own, and a
shortfall is exactly the second of those. A consumer reading a
shortfall knows only that some values named were not synthtwin's own
words. The settings block does not record what those values were --
and that is a sentence about the settings block, which is not the
document. A producer that wrote a smaller
`n_declared` than its own lists is refused here.

**Invariant K4 (the two records do not overlap).** No member appears
in both `kept_values` and `declared_missing_values`, across ALL THREE
lists: not in the two text lists, not in the two number lists, and not
in the two date lists. A value named both ways is refused before the
table is opened, so a document carrying one is a document its own
settings contradict.

**Invariant K5 (a producer obligation, stated because a loader cannot
check it).** The six lists — three in each record — are a function of
the command line alone. They are computed from what the person typed
and from section 14.1, and from nothing else: no cell of the table is
consulted, and **a declared value that matched no cell of any column
is recorded exactly as one that matched every cell**, so the lists are
not evidence that any cell wore the word. They carry no count of
cells, no column, no row and no text of the table. Two runs with the
same options over two different tables write the same six lists. A
loader holds no command line and cannot verify this; it is verified on
the producer's side, by a test that profiles two tables — one holding
the named word and one not — with the same options, and requires the
six lists to be identical.

**Invariant S7 (`values_recorded`).** `values_recorded` is `false` in
both declaration records, and a loader refuses `true`. Its meaning is
fixed here so that it cannot be read as contradicting the three lists
beside it:

> `values_recorded: false` says that this record does not carry the
> text the person typed. The three lists beside it are not that text:
> each holds members of the closed vocabulary printed in section 14.1
> of this contract, which is synthtwin's own and identical in every
> installation, written in the vocabulary's spelling and never in the
> person's.

It is a discriminator, not a switch: a profile written before this
rule carried an array of spellings under the same key, and a consumer
must be able to tell the two apart without guessing. A loader refuses
`true`, because a document claiming to record declared spellings is
not a version 6 document.

**The settings block carries the policy — how many values were named
each way, the rules that matched them, and which of synthtwin's own
published words were among them. The settings block never carries a
spelling of the person's own. AND THAT IS A SENTENCE ABOUT THE
SETTINGS BLOCK, WHICH IS NOT THE DOCUMENT.** The reason the block is bounded is sound
and is not withdrawn: a declaration is compared against every cell of
every column, including the columns whose values never appear in a
description at all, so a spelling written into the settings would
publish a value out of all of them at once. But a declared spelling
does reach the document by another route: a value named with
`--missing-value` stands in a column's `missing_by_source`, character
for character, wherever that column publishes values at all and the
count of cells wearing it reaches `small_cell_floor`; and a value
named with `--keep-value` is ordinary data of its column from that
point on. Where a declared spelling does and does not travel is fixed
by this contract's absent-cell rules and by the publication class of
the column, not by this section. A consumer, an auditor or a
user-facing page that reads this paragraph as a document-wide silence
is reading it wrong. Every readable surface that states the settings
rule must state the column route beside it; that obligation is the
plan's (amendment A-P3-31), not this contract's, and the claim
inventory holds the surfaces to it.

**What a reader can infer FROM THE SETTINGS BLOCK, said rather than
waved away.** A person usually types a word because it is in their
table, so these lists make a guess available: not "one value was
rescued" but "the value rescued was `n/a`". The word guessed at is one
of the members synthtwin publishes in this contract; it can never be a
name, a code, a diagnosis or a free-text answer, because a value
outside the vocabulary never enters these lists (K1). A reader holding
the whole description can put a vocabulary member beside a column's
own `missing_by_class` and `n_missing_withheld` and, where a column's
accounting leaves one explanation, conclude that a below-floor group
of cells wore that word. The bound on that is exact: the SIZE of that
group is a number the description publishes anyway, and the word is
one of a closed list this contract prints. Priced, and on the owner's
authority, ruled 2026-08-17 with this delta stated to them, and taken
because the alternative leaves a researcher who rescues one of
synthtwin's own words without a usable check on the table the
description was written from.

#### The remaining settings invariants

**Invariant S8.** Every name in `forced_identifiers` is the `name` of
some column block. A name that matches no column is a refusal: it
means the profile and the schema disagree about which columns were
declared.

**Invariant S9.** `categorical_floor <= categorical_ceiling`.

#### The floor, its minimum, and what a floor of one means

**The smallest permitted `small_cell_floor` is ONE** (owner ruling
2026-08-14; plan amendment A-P3-11). **THIS IS LOWER THAN THE DEFAULT
AND THE REASON IS STATED.** The floor `synthtwin profile` writes when
nobody asks for another is 11. It was once also the smallest a loader
would accept, and under that rule `synthtwin profile --smallest-group
2` accepted the number, wrote the description, and told the person to
hand that file to `synthtwin generate` — which then refused it and
advised them to make the description again and use it exactly as
written, which is what they had done. A documented option produced a
file the product would not read.

**What is given up, stated at its size.** The floor is the whole of
what keeps a published group too large to point at one person. At 11
no group named anywhere in a description covers fewer than eleven
rows; at `f` no group covers fewer than `f`, and at 1 every group is
named exactly, including a group of one row. Where one row of the real
table is one person, a description written at a low floor publishes
the existence of that person's value together with how many people
share it. That is not a route to a disclosure; it is the disclosure.
The producer publishes the same facts it always did, and the floor
decides which of them are named — so the loss is exactly the pooling
that `(withheld)`, `suppressed_levels`, `suppressed_level_counts`,
`variants_withheld` and the pooled remainders of this contract exist
to perform. On whose authority: the owner's, ruled on 2026-08-14 with
the consequence stated to them and accepted.

**No other rule of this contract is relaxed by it.** Every
floor-governed invariant is written as "at least the floor" and "below
the floor", so each one still binds at the value the document carries:
the absence-class and absence-source rules (N2, N4), the label rules
(B5, W5), the offset rule (D3), the numeric-style rule (P2), the
fraction-width rule (P6) and the stand-in rule (V1) hold at `f`
exactly as they held at 11. The long-tail detection line does not move
at all, because it reads `max(small_cell_floor,
long_tail_minimum_level)`. At `f = 1` the "below the floor" half is
the empty range, so nothing may be held back at all. A hand-edited
description is refused for every reason it was refused before; the
only refusal withdrawn is the one against the floor's own value.

**Invariant S13 (a floor of one holds nothing back).** Where
`small_cell_floor` is 1, the range of group sizes below the floor is
empty, so every field that carries what the floor held back is empty
or zero. Every one of these is empty or zero, and this list is the
whole of it:

`suppressed_levels`; `suppressed_rows`; `suppressed_level_counts`;
every `variants_withheld` block; `n_sentinel_candidates_unpublished`;
`n_missing_withheld`; and the `(withheld)` ENTRIES of
`missing_by_class`, `utc_offsets`, `numeric_styles` and
`fraction_widths`.

A document that fills one of them is refused. The rule is checked with
the top-level rules, before any column block is read, because the
floor is a top-level setting and what the rule states is a fact about
the whole description.

**On four of those positions the added thing is the ENTRY, not the
field, and the difference matters.** At a floor of 1 a decimal column
of two cells written at width 2 publishes `fraction_widths: {"2": 2}`,
which is correct and must not be refused: at a floor of one every
named width reaches the floor, so widths are NAMED rather than pooled,
and the field is nonempty precisely because nothing is held back. What
must be zero or absent there is the `(withheld)` entry alone, for the
rule's own reason — at a floor of one there is nothing to pool. The
same reading applies to `missing_by_class`, `utc_offsets` and
`numeric_styles`: the map stays, the pooled remainder goes.

**What does NOT join the list, named so no reader adds it.**
`missing_by_source` is not on it: its keys are spellings of the table
and nothing else, so it carries no pooled `(withheld)` entry at any
floor, and the count of the cells whose spelling fewer than the floor
shared is `n_missing_withheld`, which IS on the list. `n_missing_blank`
is not on it and must not be added: at a floor of one every blank
group reaches the floor, so blanks are named rather than pooled, which
is what the rule requires. And `resolution_mix` is not on it because
it is floor-free — it never withholds at any floor, so a rule about
what a floor of one holds back has nothing to say about it.

**THE LIST IS EXHAUSTIVE, AND THAT MATTERS TO A WALK** (plan amendment
A-P3-32, review item P3-V9-F2). Every position above is a FIELD of
this format or a key drawn from a vocabulary this format publishes. No
key of `missing_by_source` and no key of `levels[].variants` is on the
list or can be put on it, because the TABLE decides those keys: a
column publishing `missing_by_source: {"n_missing_withheld": 2}` says
that two cells held exactly those eighteen characters, and a level
publishing `variants: {"(withheld)": 12}` says that twelve rows wrote
their label that way. A loader that finds this rule's positions by
searching the document for names must therefore stop reading a key as
a name inside those two maps, and a producer's own publication guard
must do the same — both did not, and each refused a description this
format requires.

**Why S13 is a rule of its own, and not left to the invariants it
overlaps.** For three fields a floor of one is caught by an existing
rule: B5 reads `suppressed_level_counts` against the range below the
floor, the multiplicity rules read `variants_withheld`'s keys against
it, and B4 ties `suppressed_levels` and `suppressed_rows` to the
sizes. For the others it is not. N2, D3, P2 and P6 each say a
PUBLISHED count is at least the floor, and each exempts the pooled
`(withheld)` remainder — because the remainder is what the published
counts were pooled OUT of, and at every floor above one no bound on it
exists, since one remainder pools several groups at once. Two further
positions are reached by no rule at all rather than by an exemption:
N4 binds every value of `missing_by_source` at the floor with no
exemption and `n_missing_blank` at zero-or-the-floor, and leaves
`n_missing_withheld` — the remainder that accounting was pooled out of
— bounded in neither direction; and V1 says the same of a stand-in
number's occurrences and puts the ones below the floor into
`n_sentinel_candidates_unpublished`, which no other rule of this
contract bounds at any floor. Four exemptions and two unbounded counts
are what "below the floor" reaches at a floor of one, and no other
rule of this contract reaches them. This one does (plan amendment
A-P3-16).

**Zero and below are still refused.** One is the smallest workable
value, not a preference: "below the floor" at zero would name counts
of nothing at all, and no count is. The refusal for a floor of zero is
R16.

**What the artifacts owe when the floor is under the default.** This
contract governs the profile document, which carries the floor as a
number under `settings` and needs no further wording. Of the five
files a full run leaves behind, the readable ones — the plain-language
summary, the twin's report and the quality report — each state on
their own face that the description was made under a lowered floor and
what that can mean for a person, and the screen a `profile` run prints
says it before either of its files exists. That obligation is the
plan's (amendment A-P3-11), not this contract's, and is recorded here
because a reader of this section will ask where the disclosure went.

---

<!-- s45: publication notes, the note grammar, relationships -->

### 4.5 `publication_notes`

An array, possibly empty, of objects each having exactly two keys:

| key | JSON type | meaning |
|---|---|---|
| `column` | string | the `name` of the column the note is about |
| `note` | string | one plain-language sentence about what was held back and why |

No third key may appear; a loader refuses one, naming it.

**Invariant S10.** Every `column` value is the `name` of some column
block.

**Invariant S11.** The notes appear grouped by column in schema order,
and within one column in the order the producer emitted them. Order is
part of the canonical bytes; a loader does not need to re-derive it, but
a producer may not shuffle it between runs.

**The publication guard.** Every string in the finished document —
`publication_notes` included, because the producer lifts these notes
to the top level after each column block is finished — is either a value
the disposition matrix authorizes for publication or a note built by an
enumerated first-party constructor from the fixed grammar of section
4.5.1: literal fragments plus already-authorized values (plan P2-D2,
item P2-R5-F5). This is a producer obligation; it is recorded here
because it is a property of the document the contract describes, and
because a note that interpolates a source spelling must fail at
construction rather than at pattern matching.

**How the shipped producer meets it** (item P2-C1-F3). Every sentence
this producer can publish is built by its note constructor from one form
of the closed table of section 4.5.1, filled only with arguments of the
four classes that section closes. The sentence carries the form and the
arguments it was built from. The producer's publication check then walks
the finished document, top-level notes included, and accepts a sentence
only when re-rendering that form with those arguments writes the
identical text again; every other leaf must satisfy the rule its own
path carries, and a path, a key or a leaf kind with no rule stops the run
before serialization. Four mutations are required to fail and are held in
`tests/test_p2c1f3_publication_guard.py`: a source spelling formatted
into an existing note path with an unchanged type, a concatenation
assembling the same text from fragments, a nested container smuggling
one, and a note lifted to the top level. A loader implements none of
that machinery: it reads the strings the document carries, under the
rules stated here.

---

#### 4.5.1 The note grammar

**C6-120 (the closed form table).** Every sentence of this document
is built from one FORM: a wire identifier, a fixed number of arguments,
and one rendering. A sentence described in prose is a sentence two
producers spell two ways and no guard can rebuild, so each form's
rendering is written out below and is the whole of what that form may
say.

**The four sentence paths this grammar governs.** A form fills exactly
these leaves, and no other leaf of the document is a sentence:

- `source.header_evidence`
- `publication_notes[].note`
- `columns[].detection_evidence`
- `columns[].remarks[]`

**What the guard does NOT check, stated because a reader will assume
otherwise.** No rule binds a form to one of those four paths. The
groupings A–E below are the shipped producer's convention and a reading
aid; they are not normative. The check is about where text CAME FROM,
and that is the whole of what it claims: a form standing at an
unexpected path would be odd and would be caught by the tests that read
what a profile says, but it could not publish anything, because no form
of this grammar can carry a value of the table except under the one
binding C6-119's fourth class fixes.

**C6-119 (the argument classes, closed at FOUR).** A form argument is
one of exactly four things, and a fifth class is a change to this
contract:

1. **A whole number.** A non-boolean integer of zero or more. A truth
   value is NOT a whole number here: `true` counts as `1` in some
   languages, and a sentence that quietly rendered a flag as a count
   would read as a fact about the column. `true` and `false` are
   refused.
2. **One of this package's own words.** The membership is closed at
   THIRTEEN and is written out rather than gathered, because a tuple
   written out is what stops a spelling of somebody's table from
   becoming an argument:

   `iso-date`, `iso-datetime`, `compact-date`, `month-first-date`,
   `day-first-date`, `year-quarter`, `slashed-iso-date`, `iso-month`,
   `iso-mixed`, `month-first-datetime`, `day-first-datetime` — the
   eleven `format` members — and `day-first`, `month-first`, the two
   reading names the slashed-date remark needs. No other string is a
   word of this class.

   **Membership is not enough; the position is bound too** (NG18).
   A `format` member stands only where a form's argument table below
   names a format name — `evidence_dates` argument 3 and
   `said_read_as_dates` argument 2, and nowhere else. `day-first` and
   `month-first` stand only at
   `remark_slashed_dates_read_against_your_declaration` argument 5.
   Without that restriction a producer could build `evidence_dates`
   with the word `day-first` and render "are dates written as
   day-first" — a false sentence with a true form, which every other
   check below accepts.
3. **A nested form.** A (form, arguments) pair whose form is in this
   table, whose argument count equals that form's arity, and whose own
   arguments are each of these four classes. Nesting is what lets a
   long sentence carry a fragment without a producer formatting one
   string into another — a string assembled that way is a plain string
   with no origin, which the guard refuses.
4. **A bound affix string.** Admitted under a binding, never as a free
   string, and only at the two positions the affixed-column remark
   fixes. **The binding is POSITIONAL.** Argument 1 conforms only when
   it is character-for-character the `affix_prefix`, and argument 2
   only when it is character-for-character the `affix_suffix`, of the
   column block NAMED BY THE NOTE'S OWN SIBLING `column` FIELD.

   Position is part of the binding, and a membership test is not
   enough: a rule reading "must equal the `affix_prefix` or the
   `affix_suffix`" is satisfied with the pair SWAPPED, so a block
   publishing prefix `$` and suffix `kg` would admit the arguments
   `("kg", "$")` and render a sentence telling its reader the cells
   read `kg`, a number, then `$`.

   The resolution runs through `column` and not through any enclosing
   block, because a publication note does not sit in a column block at
   all: notes live in the top-level `publication_notes` array as
   objects of exactly two keys, and the producer lifts them out of the
   blocks that raised them. A guard told to compare against "the column
   block the sentence sits in" has no block to compare against and can
   only reject every affix note, guess a lookup, or accept any string.
   `column` is a field the note already carries and the loader already
   checks against the schema's column list.

   **What this class costs, stated without softening.** The grammar's
   original property was that no value of anybody's table could reach a
   sentence of this document at all. That property is gone and no
   wording brings it back. What replaces it is narrower and still worth
   stating: no value reaches a sentence that the SAME DOCUMENT does not
   already publish in the same column's block, under the one exception
   cut for the affix pair and confined by the forbidden-key matrix.
   The remark discloses nothing the block beside it does not, and a
   reader who may not see the affix pair may not see the remark either,
   because one publication class governs both. The guard therefore
   checks the identity and not merely that the argument is a string:
   widening it to arbitrary strings would be exactly the hole that lets
   a source-derived value into a sentence and be rebuilt successfully.

**The census.** The table holds 41 forms and 62 argument positions. Of
those, 53 are whole numbers, 3 are package words, 4 are nested forms,
and 2 are bound affix strings. No position is a string of any other
kind.

**Notation.** «*k*» marks where argument *k* is written into the
rendering. Renderings are given character for character, including the
double hyphen `--` where the text carries one. Where a rendering writes
an argument through a fixed table rather than as its own digits, the
table is given with the form.

---

##### A. The withheld-value notes (six forms)

**NF1. `no_values_unrepresentable`** — arity 0.

> no value of this column is published: too few of them are numbers
> this file format can hold

**NF2. `one_value_below_the_floor`** — arity 1. Argument 1: the floor.

> the single value in this column is shared by fewer rows than the
> smallest group size («1»), so the value itself is not published

**NF3. `one_of_two_labels_below_the_floor`** — arity 2. Argument 1: how
many levels were suppressed. Argument 2: the floor.

> «1» of the two labels in this column are shared by fewer than «2»
> rows, so that label is not published

**NF4. `labels_pooled_below_the_floor`** — arity 3. Argument 1: how many
levels were suppressed. Argument 2: the floor. Argument 3: how many
rows those levels cover.

> «1» value(s) of this column are each shared by fewer than «2» rows,
> so they are counted together instead of being published («3» rows in
> total)

**NF5. `free_text_publishes_no_values`** — arity 0.

> this column is described as free text, so none of its values are
> published: only how long they are, how many words they hold, and how
> often they repeat

**NF6. `identifier_publishes_no_values`** — arity 0.

> this column holds record numbers or codes, so no value of it is
> published anywhere in its description: only how many there are, how
> long they are, how often they repeat, and what synthtwin decided
> about them

---

##### B. The detection-evidence forms (ten forms)

**NF7. `evidence_every_value_absent`** — arity 0.

> every value in this column is blank or one of the spellings that
> mean 'no value'

**NF8. `evidence_numbers_none_holdable`** — arity 3. Argument 1:
numeric-looking cells. Argument 2: present cells. Argument 3: holdable
numbers. Two renderings, selected by argument 3 alone:

> where «3» is nonzero: «1» of the «2» values are written as numbers,
> and only «3» of them is a number this file format can hold
>
> where «3» is zero: «1» of the «2» values are written as numbers, and
> none of them is a number this file format can hold

**NF9. `evidence_one_value`** — arity 1. Argument 1: present cells.

> all «1» values that are present are the same

**NF10. `evidence_two_values`** — arity 0.

> there are exactly two different values, ignoring upper and lower case

**NF11. `evidence_dates`** — arity 3. Argument 1: cells the format
parsed. Argument 2: present cells. Argument 3: a package word — the
format name.

> «1» of the «2» values are dates written as EXAMPLE

EXAMPLE is not the argument's own spelling. It is this package's fixed
example spelling of the format argument 3 names, and the table of
examples is closed:

| format name | EXAMPLE |
|---|---|
| `iso-date` | `2024-03-17` |
| `iso-datetime` | `2024-03-17 14:05:00` |
| `compact-date` | `20240317` |
| `month-first-date` | `03/17/2024 (month first)` |
| `day-first-date` | `17/03/2024 (day first)` |
| `year-quarter` | `2024-Q1` |

A format name with no row of its own is written out as itself, so
`slashed-iso-date`, `iso-month`, `iso-mixed`, `month-first-datetime`
and `day-first-datetime` render as their own wire spellings. The
rendering is therefore fixed for all eleven members and two
implementations cannot diverge, but the five that fall through the
table read badly ("are dates written as slashed-iso-date"), and an
example for each of them should be fixed and added to this table.

**NF12. `evidence_counts_things`** — arity 1. Argument 1: numeric-looking
cells.

> all «1» numeric values are whole and none is negative, so this column
> counts things

**NF13. `evidence_written_as_numbers`** — arity 2. Argument 1:
numeric-looking cells. Argument 2: present cells.

> «1» of the «2» values are written as numbers

**NF14. `evidence_set_of_categories`** — arity 3. Argument 1: different
values, counted after trimming and case folding. Argument 2: the
categorical ceiling. Argument 3: rows.

> there are «1» different values, which is within the «2» a set of
> categories may have in a table of «3» rows, so this column is a set
> of categories

**NF15. `evidence_no_reading_fits`** — arity 5. Arguments 1 and 2: nested
forms. Argument 3: different values, counted after trimming and case
folding. Argument 4: the categorical ceiling. Argument 5: rows.

> «1-rendered», «2-rendered», and there are «3» different values where
> a set of categories may have at most «4» in a table of «5» rows

**NF16. `evidence_declared_identifier`** — arity 0.

> you told synthtwin that this column holds record numbers rather than
> measurements

---

##### C. The two fragment forms

These are forms like any other. The shipped producer builds them only
as nested arguments of the sentences that carry them, never on their
own, so that the whole sentence carrying them is rebuilt from
enumerated parts. That is convention, on the same footing as the
groupings above: no rule binds a form to a path, and a fragment
standing alone at a sentence path would be odd rather than refused.

**NF17. `said_written_as_numbers`** — arity 2. Argument 1: cells written
as numbers. Argument 2: present cells. Two renderings, selected by
argument 1 alone:

> where «1» is nonzero: «1» of the «2» values are written as numbers
>
> where «1» is zero: none of the «2» values is written as a number

**"Written as" rather than "read as", and deliberately:** this is the
count the numeric line is compared against, and it includes the cells
whose writer meant a number that no format can hold. Saying they "read
as numbers" would claim more than the column shows.

**NF18. `said_read_as_dates`** — arity 2. Argument 1: cells that read as
dates. Argument 2: a package word — the format name. Two renderings,
selected by argument 1 alone:

> where «1» is nonzero: «1» read as dates written as EXAMPLE
>
> where «1» is zero: none of them reads as a date in any form synthtwin
> knows

EXAMPLE is written through B5's table, by the same rule. In the zero
rendering argument 2 is not written; arity 2 does not imply both
positions are load-bearing, and a zero-count instance renders
identically whatever word sits at position 2.

---

##### D. The remarks (nineteen forms)

**NF19. `remark_values_out_of_range`** — arity 1. Argument 1:
out-of-range cells.

> «1» value(s) are numbers too large or too small for this file format
> to hold. They are counted as numbers for deciding what this column
> is, and their sign and whole-number status are counted too, but they
> are left out of every statistic

**NF20. `remark_values_contradictory`** — arity 1. Argument 1:
contradictory cells.

> «1» value(s) are written in a form whose meaning contradicts itself
> -- a plus or minus sign inside brackets, where the brackets already
> mean negative. synthtwin will not guess which was meant, so these
> values are left out of every statistic. Write them with a sign or
> with brackets, not both, and run the command again

**NF21. `remark_rare_sentinels_unnamed`** — arity 1. Argument 1:
candidates too rare to name.

> «1» of the numbers synthtwin uses as stand-ins for 'no value'
> appeared in this column too few times to be named here; the decision
> about each of them is recorded in the counts above

**NF22. `remark_too_few_holdable_numbers`** — arity 2. Argument 1:
holdable numbers. Argument 2: numeric-looking cells.

> this column is written as numbers, but only «1» of its «2» numeric
> values is a number this file format can hold -- the rest are too
> large or too small, or in a form whose meaning contradicts itself.
> Too few of them are left to describe the column, and synthtwin will
> not invent values in their place, so no statistic and no value of
> this column is published. Rescale the column (for example, record
> thousands instead of units) and run the command again

**NF23. `remark_two_values_differ_in_case`** — arity 0.

> this column has values that differ only in upper and lower case; they
> are counted, and published, as one

**NF24. `remark_two_values_also_read_otherwise`** — arity 0.

> the two values in this column also read as numbers or dates; because
> there are only two of them, the profile records the two values and
> how often each appears, which describes the column exactly

**NF25. `remark_dates_also_read_as_numbers`** — arity 2. Argument 1:
cells the chosen date format parsed. Argument 2: numeric-looking cells.
Carried when a date format matched the column AND the numeric-looking
count also reaches the parse line — the column read both ways, and
dates won.

> the values in this column read both as dates and as plain numbers:
> «1» of them read as dates and «2» of them are written as numbers.
> They were read as dates

**Both counts are in the sentence because the reading was a choice.**
The compact-date family is the shape where the two readings compete
most often — eight digits are a date and a number at once — and a
remark that says only which reading won leaves its reader no way to see
how close the other one came. Stating both counts is what lets somebody
recognize a column that should have been read the other way.

**NF26. `remark_slashed_dates_are_month_first`** — arity 0. Carried when
the chosen `format` is a month-first slashed reading.

> dates written with slashes are read month first (03/04/2024 is the
> 4th of March); if this table writes the day first, the profile has
> the month and day the wrong way round

This form is not false under a `day_first` declaration. It is carried
only where the month-first reading was the reading chosen, and a
month-first reading is chosen only where it parsed at least as many
cells as the day-first one, so the sentence is true wherever it appears.

**NF27. `remark_values_differ_in_case`** — arity 0.

> some values in this column differ only in upper and lower case; they
> are counted, and published, as one

**NF28. `remark_close_to_the_category_line`** — arity 2. Argument 1:
different values, counted after trimming and case folding. Argument 2:
the categorical ceiling.

> this column was close to the line between a set of categories and
> free text: it has «1» different values and the line is at «2»

**NF29. `remark_no_reading_fits` — the competing-readings remark** —
arity 9.

| # | class | meaning |
|---|---|---|
| 1 | nested form | how far the numeric reading got |
| 2 | nested form | how far the date reading got |
| 3 | whole number | the parse line, as a count |
| 4 | whole number | different values, counted after trimming and case folding |
| 5 | whole number | the categorical ceiling |
| 6 | whole number | present cells the affix reading accepted; 0 where no affix clause is written |
| 7 | whole number | cells stand-in judging removed where removal moved this column across a line; 0 where no such clause is written |
| 8 | whole number | present cells a clock reading accepted under the form that came closest; 0 where no clock clause is written |
| 9 | whole number | present cells covered by this column's floor-clearing non-numeric folded spellings; 0 where no advice is written |

The base sentence, always written:

> synthtwin could not settle what this column holds, so none of its
> values is published. Here is why: «1-rendered» and «2-rendered»; a
> column is described as numbers, or as dates, only when at least «3»
> of them read that way. It holds «4» different values, where a set of
> categories may hold at most «5». Describing it from the part that
> does read would publish an average, a smallest and a largest value
> that the rest of the column contradicts, so synthtwin describes it as
> free text and publishes no value of it at all. If these are
> measurements written with a currency sign, a per-cent sign, a unit
> such as mg, or a clock time, write them as plain numbers -- one
> column for the number, and the unit in the column name -- and run the
> command again

Then FOUR conditional clauses, each written if and only if its own
argument is nonzero, in argument order:

| written when | clause |
|---|---|
| «6» ≠ 0 | Read as a prefix, a number and a suffix, «6» of these values wear one shared pair, and a reading needs «3». |
| «7» ≠ 0 | «7» value(s) were read as stand-ins for 'no value' and taken out before this decision, which is what moved this column across a line. |
| «8» ≠ 0 | «8» of these values read as a clock time, in a shape synthtwin does not describe. |
| «9» ≠ 0 | «9» more are written one of a few ways that repeat often enough to name. If those «9» mean 'no value', run the command again with --missing-value and this column's distribution will be described. |

**The composition is exact.** Where no clause is written the sentence is
the base sentence alone, ending as it does, with no terminal full stop.
Where any clause is written, a full stop and ONE space follow the base
sentence, then the clauses that apply in argument order, each written
exactly as the table above gives it and ending in a full stop,
separated from the next by ONE space, and no other punctuation,
conjunction or joining word is added. A guard rebuilding the sentence
therefore has one candidate string to compare, not a family of
equivalent spellings.

**Why a column that publishes nothing owes this much.** The reason a
column was declined is a set of counts rather than a verdict: how much
of the column each reading accounted for, and how much each reading
needed. Without it the person is told only that synthtwin declined,
which is a report they cannot act on. The four clauses exist because
four things can now go wrong quietly: a shared affix pair that fell
short of the line; a shared affix pair, or a numeric reading, eaten
below a line by stand-in removal; a clock shape this version does not
describe; and a set of repeated non-numeric spellings that one
declaration would turn into gaps. A column that fell to a later rule
for any of those reasons must say so in its own evidence. The fourth
clause is advisory and routes nothing: it is written exactly when the
arithmetic makes it TRUE rather than hopeful, and where the arithmetic
does not hold no advice fires and nothing implies one declaration would
suffice.

**NF30. `remark_some_values_are_not_numbers`** — arity 1. Argument 1:
unparsed cells.

> «1» value(s) in this column are not numbers; they were left out of
> the statistics and are not published

**NF31. `remark_close_to_the_numeric_line`** — arity 3. Argument 1:
numeric-looking cells. Argument 2: present cells. Argument 3: the parse
line, as a count.

> this column was close to the line between numbers and text: «1» of
> its «2» values are written as numbers, and the line is at «3»

**NF32. `remark_every_number_is_different` — the code-shaped numeric
remark** — arity 1. Argument 1: how many of this column's present cells
carry a value some other row also carries; 0 where every value is
different. Two renderings, selected by argument 1 alone:

> where «1» is zero: every value in this column is different. That is
> not treated as evidence of anything: the column is described as
> numbers, which keeps its distribution. If it is really a record
> number, run the command again with --identifier NAME, where NAME is
> this column's name, and its values will be left out of the profile
> altogether
>
> where «1» is nonzero: the values in this column are shaped like
> codes, and «1» of them are shared with another row. That is not
> treated as evidence of anything: the column is described as numbers,
> which keeps its distribution. If it is really a record number, run
> the command again with --identifier NAME, where NAME is this
> column's name, and its values will be left out of the profile
> altogether

**Why there are two renderings.** The trigger for this remark is code
SHAPE — values that are all whole, or nearly never repeat, or are
fixed-width digit strings with leading zeros — and a code column whose
values repeat is code-shaped too. A single rendering opening "every
value in this column is different" would be false on exactly the
repeating code columns the shape test reaches, and a remark whose whole
job is to let somebody recognize their own column must not misdescribe
it.

**NF33. `remark_spread_out_of_range`** — arity 0.

> the values in this column are so far apart that their spread is a
> number too large for this file format to hold, so no standard
> deviation is published for it: the profile records that the spread is
> out of range rather than a number that would be wrong. Every other
> statistic of this column is published as usual. If you need the
> spread, record the column in larger units -- thousands or millions
> instead of units, with the unit in the column name -- and run the
> command again

**NF34. `remark_every_value_is_different` — the code-shaped text
remark** — arity 1. Argument 1: as NF32. Two renderings, selected by
argument 1 alone. Where «1» is zero:

> every value in this column is different, and none of the forms
> synthtwin can read fits them. synthtwin did NOT assume they are
> record numbers: it cannot tell from the values alone whether these
> are record numbers or measurements written in a form it does not read
> yet, and a wrong guess would throw away the whole distribution.
> Nothing from this column is published either way -- no value of it,
> and no distribution. If these ARE record numbers, run the command
> again with --identifier NAME, where NAME is this column's name, and
> the profile will say so. If they are measurements written with a
> currency sign, a per-cent sign, a unit such as mg, or a clock time,
> write them as plain numbers -- one column for the number, and the
> unit in the column name -- and their distribution will be described.
> Do not use --identifier on a measurement: it withholds the column
> entirely

Where «1» is nonzero, the identical text with its first sentence
replaced by: *"the values in this column are shaped like codes, «1» of
them are shared with another row, and none of the forms synthtwin can
read fits them."*

This form is carried on every role its trigger reaches, the
affixed-number role included, at the wording above and no other — the
same tell-the-person-both-ways posture the affixed-column remark also
takes.

**NF35. `remark_affixed_numbers_may_be_codes`** — arity 3. Argument 1: a
bound affix string — the block's `affix_prefix`. Argument 2: a bound
affix string — the block's `affix_suffix`. Argument 3: `n_affixed`, how
many present cells actually wore the pair.

> «3» of this column's values are written as «1», a number, then «2»,
> and synthtwin described those numbers as quantities: their average,
> their spread and their ends are in this profile. If these are codes
> rather than measurements, run the command again with --identifier
> NAME and no value of this column will be published at all.

**Carried by EVERY affixed-number column, without condition.** No test
of the values can separate an opaque token family from a measurement —
repeating decimal-cored tokens defeat every conditional remark anyone
drafts, which is how three identifier inferences were defeated before
withdrawal — so the choice is between telling every such column's owner
and telling none.

**The count is in the sentence because the sentence was false without
it.** A rendering opening "EVERY value in this column is written as
«1»…" claims more than the role requires: the role admits stragglers up
to the parse line, so a hundred-cell column with ninety-nine affixed
values and one plain number conforms and the remark was false of the
hundredth.

**NF36. `remark_slashed_dates_read_against_your_declaration`** — arity 5.

| # | class | meaning |
|---|---|---|
| 1 | whole number | *D*, cells the day-first reading parsed |
| 2 | whole number | *M*, cells the month-first reading parsed |
| 3 | whole number | *X*, cells only the day-first reading parsed |
| 4 | whole number | *Y*, cells only the month-first reading parsed |
| 5 | package word | the reading USED: `day-first` or `month-first` |

Carried whenever `day_first` was given and a slashed reading was in
play, exactly once per such column.

The rendering is TWO clauses, the first always and the second on its own
trigger. The first clause has three renderings and exactly one applies,
selected by the arguments alone:

| when | first clause |
|---|---|
| «1» > «2» (argument 5 is `day-first`) | read day first, which parses «1» of these values against the month-first reading's «2». |
| «2» > «1» (argument 5 is `month-first`) | read month first, though you asked for day first, because it parses «2» against «1». |
| «1» = «2» (argument 5 is `day-first`) | read day first because you asked for it: both readings parse «1» of these values and the values themselves do not settle which is right. |

The third rendering is the TIE, and it has a rendering of its own
because the tie is the case the declaration decides: with only the
other two, a producer on a tie has to invent a sentence or write a false
one, since each of them claims one reading parsed more than the other.

The second clause appears if and only if BOTH «3» and «4» are nonzero,
at any counts, tie or no tie, and renders:

> This column contradicts itself: «3» values only a day-first reading
> accepts, and «4» only a month-first one.

**Why two independent clauses.** How the winner was chosen and whether
the column contradicts itself are different questions that combine
freely. A column can hold one cell only the day-first reading parses AND
one cell only the month-first reading parses — evidence in both
directions at equal counts — so a column that is evidence-decided AND
internally inconsistent is reported as both, never presented as settled.
The person is never silently overruled, never silently obeyed against
evidence, and never silently obeyed into free text.

**The composition is exact.** Where the second clause appears it follows
the first with ONE space between the first clause's closing full stop
and the second clause's opening capital, and no other punctuation,
conjunction or joining word is added. Where it does not appear, the
sentence is the first clause alone.

**NF37. `remark_a_label_is_a_built_in_stand_in`** — arity 1. Argument 1:
which built-in stand-in number, given as its one-based position in this
package's three-member list — so 1, 2 or 3 and nothing else. The
rendering writes it through this fixed table:

| «1» | NUMBER |
|---|---|
| 1 | `-9999` |
| 2 | `-999` |
| 3 | `9999` |

> one of the values this column publishes is NUMBER, which is one of
> the three numbers synthtwin treats as a stand-in for 'no value' when
> a column's own numbers make it one. This column holds labels rather
> than numbers, so that value is published as a label and counted as a
> real one. If it means 'no value' in your table, run the command again
> with --missing-value NUMBER and it will be counted as a gap instead.

Both occurrences of NUMBER are written from argument 1 through the same
table. The value itself is not an argument and no spelling of the table
enters the sentence: the label is published in the column's own block
beside the remark, and the reader finds it there.

**Why it exists.** A label column holding `-999` publishes it as an
ordinary level with an ordinary count, and nothing else in the document
tells its owner that synthtwin would have read that number as a gap on a
numeric column. It is advisory and routes nothing.

---

##### E. The header-verdict forms (four forms)

**NF38. `header_names_because_you_said_so`** — arity 0.

> The first row was read as the column names because the command was
> run with --first-row names.

**NF39. `header_data_because_you_said_so`** — arity 0.

> The first row was read as the first record because the command was
> run with --first-row data, so the columns were named column_1,
> column_2, and so on and every record was kept.

**NF40. `header_names_by_convention`** — arity 0.

> The first row was read as the column names by convention, not by
> evidence: a CSV file is normally written with its column names first,
> and nothing in this file contradicted that -- no value in the first
> row belongs among the values of the column below it. synthtwin did
> not check that those values ARE names, because no such check exists.
> If that row is really the first record, run the command again with
> --first-row data: the columns are then named column_1, column_2, and
> so on and every record is kept.

**NF41. `header_names_shown_by_a_column`** — arity 1. Argument 1: the
column's one-based position.

> column «1» holds a number in every row below it, and its first-row
> value is not a number

**Why the header verdict is a form at all.** A verdict built anywhere
else would be the one string in the document with no form behind it, and
one exception is all a guard needs to stop meaning anything.

---

#### 4.5.2 Argument-consistency checks

An argument that can disagree with another argument, or with the block
the note names, is a way to write a false sentence with a true form. The
checks below are part of the grammar: a form whose arguments fail any
check that applies to it is refused, by a producer and by a loader
alike, except where a row is marked *producer*.

**The parse-line count, defined here because three checks depend on
it.** For a population of *t* cells, the parse-line count is the
smallest whole number that reaches `settings.minimum_parse_rate` × *t*:
compute the exact product, take its whole part, and add one if the whole
part is below the exact product. It is applied as a COUNT, never as a
compared share, so that no rounding of a division can decide a column's
role.

**Floor-clearing, defined here for the same reason.** A folded spelling
of a column is *floor-clearing* when at least `settings.small_cell_floor`
of that column's present cells share it.

**For `remark_slashed_dates_read_against_your_declaration`**, over the
column the note's own `column` field names, writing *n* for that
column's `n_present`:

| id | statement |
|---|---|
| NG1 | *D*, *M*, *X* and *Y* are whole numbers of zero or more |
| NG2 | the both-readings identity: *D* − *X* = *M* − *Y* |
| NG3 | *X* ≤ *D*; given NG2 this gives *Y* ≤ *M* |
| NG4 | *D* + *Y* ≤ *n*, equivalently *M* + *X* ≤ *n* |
| NG5 | argument 5 is `day-first` where *D* ≥ *M*, and `month-first` where *M* > *D* |

**Why NG2 is not optional.** The cells BOTH readings parse are
countable two ways — the day-first total less the day-first-only cells,
and the month-first total less the month-first-only cells — and the two
must agree. Without it, *D*=90, *M*=80, *X*=10, *Y*=20 passes every
other check and gives 80 and 60 for the same quantity: a census no table
can produce, rendered into a sentence a guard would rebuild and accept.

**Why NG4 bounds the union and not each count.** Bounding *D* ≤ *n*
and *M* ≤ *n* separately bounds nothing about the four blocks together:
at *n*=100, *D*=80, *M*=80, *X*=30, *Y*=30 both bounds hold, NG2 and
NG3 hold, and the four blocks need 110 cells. The union bound is the
one that refuses it, and *D* ≤ *n* and *M* ≤ *n* follow from it.

**These five are complete.** Given values passing them, set the
both-readings block to *D* − *X* and the neither block to *n* − *D* −
*Y*; both are non-negative and the four blocks realize (*D*, *M*, *X*,
*Y*) exactly.

**For `remark_no_reading_fits`**, over the column the note names,
writing *N* for the numeric-looking count carried inside argument 1:

| id | statement |
|---|---|
| NG6 | argument 1 is a `said_written_as_numbers` fragment whose own argument 1 equals the named column's `n_numeric` + `n_out_of_range` + `n_contradictory`, and whose own argument 2 equals its `n_present` |
| NG10 | the base sentence's own precondition, on the `free_text` columns this remark is carried by: *N* is below the parse-line count of `n_present` |

**And on its recoverable-distribution clause**, writing *C* for
argument 9:

| id | statement |
|---|---|
| NG7 | where *C* ≠ 0: *N* + *C* ≤ `n_present`, equivalently *C* ≤ `n_not_numeric` |
| NG8 | where *C* ≠ 0: *C* ≥ `settings.small_cell_floor` |
| NG9 | where *C* ≠ 0: *N* is at least the parse-line count of (`n_present` − *C*) |
| NG9-P | *producer*: where that arithmetic holds, the clause IS written. A loader holding a document with no clause holds no *C* and cannot test the converse |

**The count is the numeric-looking one, not `n_numeric` alone**, and the
two differ whenever a column holds an out-of-range or contradictory
spelling. It is the count the numeric line is compared against, it is
the count the fragment at argument 1 already carries, and it is the
count the rendered words call *written as* numbers. Declaring the
covered spellings missing makes their cells ABSENT, so the surviving
present population is `n_present` − *C* while *N* is unchanged, and the
column is re-tested against the same one line applied to the smaller
population. That is why the trigger is arithmetic over counts the remark
already carries plus the floor, and why it needs no settings key of its
own.

**NG10 is scoped to `free_text` and must not be applied wider.**
A `numeric_unrepresentable` column is reached only where the
numeric-looking count is at or above the parse line, so applying
NG10 there would refuse every legitimate such document.

**For `remark_affixed_numbers_may_be_codes`**, over the column the note
names:

| id | statement |
|---|---|
| NG11 | argument 3 equals the named column block's `n_affixed` |
| NG12 | argument 1 is character-for-character the block's `affix_prefix` and argument 2 character-for-character its `affix_suffix`, at those positions and not merely as members of the pair |

**For `remark_a_label_is_a_built_in_stand_in`:**

| id | statement |
|---|---|
| NG13 | argument 1 is 1, 2 or 3 |
| NG13-P | *producer*: the column publishes a level whose spelling is the stand-in argument 1 names |

**For every form:**

| id | statement |
|---|---|
| NG14 | the form is one of the 41 in section 4.5.1 |
| NG15 | the argument count equals that form's arity |
| NG16 | every argument is of one of C6-119's four classes |
| NG17 | re-rendering the form with those arguments writes the leaf's text character for character |
| NG18 | every package word stands at a position C6-119's second class admits it at: a `format` member only at `evidence_dates` argument 3 or `said_read_as_dates` argument 2, and `day-first` or `month-first` only at `remark_slashed_dates_read_against_your_declaration` argument 5 |

NG17 is the one check that is not a pattern, and it is what the rest
rests on: a sentence with a value of the table formatted into it fails
NG14 — formatting a note produces a plain string, which carries no
form — and could not pass NG17 either, because no enumerated argument
spells a value of a table. NG18 is what NG17 cannot do: a word of
the wrong kind at a word position renders and re-renders cleanly, so
only the position rule refuses it.

### 4.6 `relationships` — the reserved manifest

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

**Why the block exists empty.** This version preserves no cross-column
structure, and a block reserved in the shape it will eventually take is
what lets a later phase fill one slot without moving any other key. The
generator carries exactly one dispatch seam that verifies this block is
empty and then generates columns independently (plan P2-D5). Filling any
slot advances `profile_version`; version 6 is defined as a version in
which all eight are null. No cross-column fact enters this version: not
a correlation, not a formula between two columns, not a shared pattern
of empty cells, not the order of two event dates.

---

<!-- s5: the column block: universal keys and the axes -->

## 5. The column block

A column block is an object. Its key set is the union of the universal
keys (section 5.1) and the keys its role adds (section 6). No other key
may appear; a loader refuses an unknown key, naming it and the column.

### 5.1 Universal keys — present on every column, every role

There are **twenty-two** universal keys. Every one is present in every
column block of every role, on every run, including when its content is
zero or empty. This format has no optional keys, on purpose: a key that
appears only sometimes is a key a consumer comes to guess about, and the
guess is what fails silently.

| key | JSON type | range / permitted values | meaning | disposition |
|---|---|---|---|---|
| `name` | string | non-empty after trimming | the column's name | EXACT-OBSERVABLE when a header is written, else EXACT-CONTROL |
| `position` | integer | `1 .. n_columns` | the column's one-based place in the schema | EXACT-CONTROL |
| `role` | string | one of the thirteen role names fixed by the table in section 5.2 | the type path the taxonomy chose | EXACT-CONTROL |
| `statistical_type` | string | one of the thirteen statistical types fixed by the table in section 5.2 | the shape of the column's values | EXACT-CONTROL |
| `quality_state` | string | `ok`, `empty`, `unrepresentable` | whether the column has usable values at all | EXACT-CONTROL |
| `structural_role` | string | `data`, `identifier` | whether the column was declared to hold record numbers or codes | EXACT-CONTROL |
| `n_present` | integer ≥ 0 | ≤ `n_rows` | how many cells hold a value | EXACT-OBSERVABLE |
| `n_missing` | integer ≥ 0 | ≤ `n_rows` | how many cells hold no value | EXACT-OBSERVABLE |
| `missing_by_class` | object | exactly six keys, section 5.4 | absent cells by the reason each was counted absent | REPORT-ONLY |
| `missing_by_source` | object | section 5.4 | absent cells by the exact spelling that made them absent, under the floor | EXACT-OBSERVABLE — recounted per spelling from the written twin, except a key a judged pass put there (a spelling reading as a stand-in number, or as a calendar placeholder), which the twin writes empty |
| `n_missing_blank` | integer ≥ 0 | — | how many absent cells of this column held nothing, or nothing but space — written when at least `small_cell_floor` cells did, and `0` otherwise, those cells being counted in `n_missing_withheld` instead | REPORT-ONLY, bound by the sum identity the twin's reproduction rule states: the twin's recounted blank absent cells equal `n_missing_blank` plus `n_missing_withheld` plus the stand-in-sourced cells, because a per-field equality would be false by construction |
| `n_missing_withheld` | integer ≥ 0 | — | how many absent cells of this column wore a spelling — or a blankness — that fewer than `small_cell_floor` cells of the column shared, pooled together and unnamed | REPORT-ONLY, bound by the same sum identity |
| `n_distinct` | integer ≥ 0 | ≤ `n_present` | how many different RAW present spellings the column holds | set per role group, section 9 |
| `n_distinct_folded` | integer ≥ 0 | ≤ `n_distinct` | how many different FOLDED identities it holds | set per role group, section 9 |
| `n_numeric` | integer ≥ 0 | — | present cells that read as a number this file format can hold | EXACT-OBSERVABLE by class-preserving construction |
| `n_not_numeric` | integer ≥ 0 | — | present cells that are not numeric notation at all | EXACT-OBSERVABLE by class-preserving construction |
| `n_out_of_range` | integer ≥ 0 | — | present cells that are well-formed numbers too large or too small for binary64 | EXACT-OBSERVABLE by class-preserving construction |
| `n_contradictory` | integer ≥ 0 | — | present cells written in numeric notation whose meaning conflicts with itself — a sign inside accounting parentheses | EXACT-OBSERVABLE by class-preserving construction |
| `n_sentinel_candidates_unpublished` | integer ≥ 0 | — | how many stand-in candidates were judged but occurred in too few rows to be named | REPORT-ONLY |
| `sentinel_verdicts` | array of objects | section 5.5 | what was decided about each named stand-in candidate — a stand-in number or a calendar placeholder — and why | REPORT-ONLY |
| `detection_evidence` | string | non-empty | one plain sentence saying why this role was chosen | REPORT-ONLY |
| `remarks` | array of strings | possibly empty | plain-language notes about this column | REPORT-ONLY |

**Three closed lists are named here rather than repeated here.** The
role vocabulary and the statistical-type vocabulary are written out in
the table of section 5.2; the six absence classes are written out in
section 5.4. A closed list stated in two places is a list two
implementations can read differently, and the reading that loses is
always the one a document was written against. The two short axis
vocabularies above are written at their own rows because a rule of
section 5.2 binds each of them and neither can drift: invariant A4
admits no `quality_state` but the three the table's third column
carries, and invariant A1 with the declaration rule fixes
`structural_role` at exactly `data` and `identifier`. Section 5.2 names
the thirteen roles a second time, as the order its rules are tested in;
invariant A5 requires the table to be total over the vocabulary, so a
name in one list and not the other is a defect that invariant names.

**The four numeric census counts answer for CELLS.** `n_numeric`,
`n_not_numeric`, `n_out_of_range` and `n_contradictory` classify the
complete present cell, on every role. On `affixed_number` that is not
the population its quantitative facts describe: those describe the
cores, which are counted by four keys of that role's own, beginning
with `n_core_numeric`. The `affixed_number` section states the split,
and every quantitative invariant this format states over `n_numeric` is
read on that role over `n_core_numeric`, and nowhere else.

**`detection_evidence` and `remarks` are built sentences, not free
text.** Both are subject to the publication guard of section 4.5: each
is built by a first-party constructor from one form of the closed note
grammar, filled only with whole numbers, words of this package's own
enumerated vocabulary, other forms of that grammar, and the bound affix
strings that grammar admits. This is a producer obligation. It is
recorded here because it is a property of the document this contract
describes, and because a note that interpolates a source spelling must
fail at construction rather than at pattern matching. A loader does not
re-derive it; it reads the strings the document carries, under the
types and bounds this table states.

### 5.2 The three axes, and the rule that derives them

Three axes stand beside `role` in every column block:
`statistical_type`, `quality_state` and `structural_role`. **The
generator dispatches on the axes, never on `role`** (plan P2-D3). The
first two are derived by the fixed rule in the table below, which is
total over the thirteen roles and admits no other combination. The
third is derived by the declaration rule stated after it.

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

**Thirteen rows, thirteen statistical types, one row each.** The table
is a bijection: no two roles answer the same `statistical_type`, and
every one of the thirteen types is reached by exactly one role. The
row order above is presentational; what is normative is the set of
rows, and invariant A4 is what a loader enforces against it.

**Four roles answer something other than their own name, and each is a
case where the role name and the shape of the values are not the same
fact.** An `empty` column has no shape to report and no usable values;
a `numeric_unrepresentable` column was written as numbers and holds
none this format can carry; an `identifier` column holds codes; and
`free_text` holds text. The other nine name their own shape. The table
is written out row by row rather than derived from the role string,
because a mapping a reader can check is worth more than one line of
cleverness.

**C6-19.** `time_of_day`, `affixed_number` and `long_tail_labels` each
name themselves. That is a stated cost rather than an oversight: for
these three the shape axis buys nothing over the role name, and the
axes' value here is the totality discipline, not extra information.
Each carries `quality_state` `ok`, and each carries `structural_role`
`data` — no declared column can reach any of the three, because the
declaration is decided at rule 2 of the order below and these three
rules are tested at 9, 10 and 11.

**`structural_role` is `identifier` exactly when the column was named
with `--identifier`, and `data` otherwise.** This includes a declared
column that ends with role `empty`, which is the one case where a
declared column does not carry role `identifier`.

**C6-3.** The empty rule settles a column with no present values before
any other rule runs, including before the declaration. So a declared
column of entirely absent cells arrives at role `empty` while still
being a column whose owner said it holds codes: `role` `empty`,
`statistical_type` `unknown`, `quality_state` `empty`,
`structural_role` `identifier`.

**Invariant A1.** `structural_role == "identifier"` if and only if
`name` appears in `settings.forced_identifiers`.

**Invariant A2.** `statistical_type == "code"` implies
`structural_role == "identifier"`. There is no route to the
`identifier` role but the declaration, so a `code` column is always a
declared one.

**Invariant A3.** `structural_role == "identifier"` implies
`statistical_type` is `code` or `unknown`, and `role` is `identifier`
or `empty`.

**A2 and A3 stay narrow across all thirteen roles, and here is why they
are still total.** Both quantify over the types `code` and `unknown`
and the roles `identifier` and `empty`, and the three roles this
version adds widen neither set: the declaration is decided at rule 2 of
the order below, ahead of every rule that can reach a new role, so a
declared column reaches only `empty` (settled at rule 1) or
`identifier` (rule 2). No role added after rule 2 is reachable by a
declared column, and no role but `identifier` answers `code`.

**Invariant A4.** The triple (`role`, `statistical_type`,
`quality_state`) is exactly one row of the table above. A loader
refuses any other combination — refuses it rather than repairing it —
naming the column and the three values, because a combination outside
the table is a document whose axes and role disagree, and the generator
dispatches on the axes.

**Invariant A5.** The table above is total over the thirteen roles:
every role of the vocabulary has a row, and no role has two. An axis a
column sometimes lacks is an axis nobody can dispatch on.

**Why the axes and not the role.** The role name is a taxonomy verdict
carrying a rule's history; the axes are the three questions the
generator actually asks — what shape are the values, are there usable
values at all, and is this column somebody's key. Dispatching on the
axes means a role added to the taxonomy arrives with its answers
already stated, rather than as an unrecognized name in a chain of
comparisons.

#### The rule order: which role claims a column

**C6-1.** The role vocabulary has thirteen members. Which one a column
takes is decided by testing these rules in order, first match wins:

1. `empty`;
2. declared `identifier`;
3. `numeric_unrepresentable`;
4. `constant`;
5. `binary`;
6. `datetime`;
7. `count` or `continuous`;
8. `categorical`;
9. `time_of_day`;
10. `affixed_number`;
11. `long_tail_labels`;
12. `free_text`.

Thirteen roles in twelve rules: `count` and `continuous` are decided by
one rule, which then chooses between the two.

**Why rules 9 through 11 sit after `categorical`.** They are tested
last before the fallback, so they claim only columns every earlier rule
declined; no column an earlier rule can claim is diverted into one of
them, and no earlier rule's reach depends on them. Their internal order
is `time_of_day` before `affixed_number` — clock text rarely splits as
an affixed number, but the time reading is the more specific claim —
and `affixed_number` before `long_tail_labels`, because a distribution
beats labels where both could fire, with `long_tail_labels` last before
the fallback.

**The order is a PRODUCER rule.** It decides what a producer writes. A
loader holds one document and never the table it describes, so it
cannot re-run the order and cannot check that the winning rule was the
first that matched. What a loader enforces about the role is A4: the
triple is one row of the table, or the document is refused.

---

<!-- a7a_53: the multiplicity map -->

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

---

<!-- s5b: the vocabulary, the absent cells, verdicts, the ladder -->

### 5.4 The absent cells: the vocabulary, two maps and two counts

Every column block says how many of its cells held no value, and then
says it again three more ways: by the REASON the cell was counted
absent, by the SPELLING the cell wore, and by two counts standing
beside the spelling map for the cells no spelling could name. The four
answer different questions and none replaces another.

#### 5.4.1 The published vocabulary

**C6-31 (the closed list).** The published vocabulary is the set of
values synthtwin itself reads as "no value" or judges as a stand-in,
without anybody naming them. It is a closed list of THREE parts, and
its size is stated here because every surface that counts it must
count the same number:

- **EIGHTEEN text spellings** read as "no value". Seventeen are
  matched after trimming and a Unicode case fold: the ten plain
  spellings — the empty spelling, `-`, `--`, `.`, `?`, `n/a`, `na`,
  `nan`, `none`, `null` — and the seven spreadsheet error literals
  `#DIV/0!`, `#N/A`, `#NAME?`, `#NULL!`, `#NUM!`, `#REF!`, `#VALUE!`.
  The eighteenth, `NaT`, is matched by raw byte equality with the
  cell, with no trimming and no case folding.
- **THREE stand-in numbers**: −9999, −999, 9999, written on the wire
  as `-9999.0`, `-999.0` and `9999.0`.
- **TWO calendar placeholders**: `1900-01-01` and `9999-12-31`.

**Twenty-three members in all.** Extending any of the three parts is a
change to this contract and advances `profile_version`.

**This list is synthtwin's own.** It is the same in every
installation, it contains no text from any table, and a document
naming one of its members in a declaration record therefore discloses
something about a command line rather than about a column.

**C6-32 (why one member is matched differently).** A difference in a
matching rule is the kind of thing a reader must not have to infer, so
it is stated rather than left to the code. Every folded member's
folded form collides with no human word. `NaT`'s does: folded, it is a
person's name, so admitting it under the folded rule would silently
read name cells as absent.

It therefore joins as the vocabulary's one exact-spelling member, and
that one operation — raw byte equality — is applied identically
wherever the vocabulary is consulted: recognizing a cell as absent;
recording which members a declaration named; **the test of whether a
declaration names a vocabulary member and so rescues a cell that this
list would otherwise make absent**; the published-vocabulary tests;
and the validator's reconstruction. The rescue test is named
explicitly because leaving it to be inferred is how the kept-side
completeness proof (8.4) came to be carried with one of its six ways
unproved.

The criterion that keeps `unknown` and `missing` OUT of this list — a
human word carries meaning somewhere — stands unweakened for every
folded member.

#### 5.4.2 `missing_by_class` — by reason

An object with exactly these SIX keys, always all six, on every column
block of every role, each an integer at least 0:

| key | meaning |
|---|---|
| `(blank)` | the cell was empty or held only spaces |
| `(date-sentinel)` | a calendar placeholder the column-level pass of 6.6.4 judged to mean "no value" |
| `(declared-missing)` | the person named this value with `--missing-value` |
| `(numeric-sentinel)` | a stand-in number the column-level rule judged to mean "no value" |
| `(text-code)` | one of the spellings of the published vocabulary (14.9) |
| `(withheld)` | the pooled remainder of the classes above whose own counts fell below the floor |

**Invariant N1.** The six values sum to `n_missing`.

**Invariant N2.** A class other than `(withheld)` is either 0 or at
least `small_cell_floor`. A class whose real count fell between 1 and
the floor is pooled into `(withheld)` and reads 0 here. `(withheld)` is
exempt from the floor in both directions: it is the remainder the named
counts were pooled out of, and one remainder may pool several classes.

**These keys are a closed first-party enumeration** into which no text
of anybody's table can land, so they carry no collision to close. That
is what separates this map from the next one.

#### 5.4.3 `missing_by_source` — by spelling

An object mapping an exact absent-value spelling to how many rows of
this column held it. Every key is a spelling that at least
`small_cell_floor` rows shared, written character for character as the
file held it, having passed through the display boundary that turns a
line, control or bidirectional formatting character into a printable
form that shows itself (2.4).

**It carries no `(blank)` key and no `(withheld)` key.** Those two are
`n_missing_blank` and `n_missing_withheld`, fields of their own beside
it, and 5.4.4 says why the split matters.

**Invariant N3 (the source accounting closes).** On a column that is
not a nothing-publishing column (6.10):

```
sum(missing_by_source.values()) + n_missing_blank + n_missing_withheld
    == n_missing
```

On a nothing-publishing column, `missing_by_source` is `{}`,
`n_missing_blank` is 0 and `n_missing_withheld` is 0, whatever
`n_missing` is. Naming a spelling there would publish a value out of a
column that publishes none.

**Invariant N4.** Every value of `missing_by_source` is at least
`small_cell_floor`, with no exemption, and `n_missing_blank` is 0 or at
least the floor. `n_missing_withheld` is bounded in neither direction,
for N2's reason.

**Invariant N5 (the keys are the TABLE's).** No key of
`missing_by_source` carries a first-party meaning — not the six class
words of 5.4.2, and not any other name this format uses,
`n_missing_withheld` and `n_sentinel_candidates_unpublished` among
them. A cell can hold those words too, and a column publishing
`missing_by_source: {"n_missing_withheld": 2}` says that two cells of
the table held exactly those eighteen characters. `levels[].variants`
is the other map the table keys, and a rule that finds this format's
fields by searching a document for names must stop reading a key as a
name inside both.

**Invariant N6.** `n_missing_blank` and `n_missing_withheld` are 0 on
exactly the nothing-publishing columns. That class is a function of
`role` and `structural_role`, both of which every block publishes, so a
consumer can decide it from the document alone.

**Invariant N7 (producer).** A `missing_by_source` key is the source
spelling character for character. A loader holds one document and never
the table it describes, so it cannot check that the spelling published
is the spelling a cell wore.

#### 5.4.4 Why the blank count and the blank CLASS are two numbers

`n_missing_blank` is not the same number as
`missing_by_class["(blank)"]`, and neither replaces the other. The
class count is pooled when the CLASS falls below the floor; the field
is pooled when the SPELLING — here, blankness — falls below it. A
column can therefore publish a class count of zero and a blank count of
forty, or the reverse, and both readings are correct about different
questions. Both are published, in two fields, because a field that
carried both could not be read.

**The dispositions of all four are section 9's**, and they are not the
same: this version reproduces recorded hole spellings in the twin,
which is what makes one of these maps checkable against written bytes
and leaves the others as report facts.

### 5.5 A sentinel verdict entry

`sentinel_verdicts` is an array, possibly empty, of objects each having
exactly these four keys:

| key | JSON type | permitted values |
|---|---|---|
| `candidate` | string | the stand-in number as text; the canonical ISO day spelling of a calendar placeholder (6.6.4); or exactly `(withheld)` |
| `verdict` | string | `read_as_missing`, `kept_as_a_number` |
| `reason` | string | `outlier_and_frequent`, `not_an_outlier`, `too_rare`, `too_few_other_values`, `kept_by_you` |
| `n_occurrences` | integer ≥ 1 | how many rows held the candidate |

**Invariant V1.** Every entry has `n_occurrences` at least
`small_cell_floor`. Candidates below the floor are not listed at all;
they are counted, unnamed, in `n_sentinel_candidates_unpublished`. That
count is the one field of this format that records a thing held back in
its NAME rather than under the `(withheld)` word, and at a floor of one
it is zero under S13, because no candidate can be below one.

**Invariant V2.** `candidate` is `(withheld)` on exactly the columns
where `missing_by_source` is `{}` for N3's reason — a column whose
publication class permits no value of the table anywhere in its block.

**Invariant V3.** `verdict` is `read_as_missing` only when `reason` is
`outlier_and_frequent`. The other four reasons all keep the candidate
as an ordinary value of the column.

**Invariant V4 (the order, total over all three kinds of candidate).**
Entries appear in this order, and the rule is exhaustive over the
candidates this version permits:

1. candidates that are NUMBERS, ascending by the number;
2. candidates that are CALENDAR DAY SPELLINGS, ascending by the
   candidate text — which, for the canonical ISO day spelling, is also
   ascending by date. These follow every numeric entry;
3. candidates that read `(withheld)`, ordered by `n_occurrences`, then
   `verdict`, then `reason`, so that no position can say which of two
   withheld candidates is the smaller.

The three groups appear in that order wherever a block carries more
than one of them. A block never in fact mixes group 3 with groups 1 or
2, because withholding is a property of the whole block and not of a
single entry; the group order settles the mixed case that CAN arise —
numeric together with calendar — and states the rest so a reader need
not infer it. A rule that ordered only the mixed case would leave a
calendar-only block ordered by nothing at all, and the same declared
inputs would canonicalize to different bytes.

### 5.6 The ladder

Two fields carry a ladder: `percentiles` on the numeric roles and
`date_percentiles` on `datetime`. Both are objects with exactly the
eleven keys `min`, `p01`, `p05`, `p10`, `p25`, `p50`, `p75`, `p90`,
`p95`, `p99`, `max`, no more and no fewer.

**Invariant L1 (non-decreasing).** Read in ladder order — `min`, `p01`,
`p05`, `p10`, `p25`, `p50`, `p75`, `p90`, `p95`, `p99`, `max` — the
values never decrease. For `percentiles` the comparison is numeric; for
`date_percentiles` it is plain text comparison, which is why the
canonical datetime forms are chosen to sort as text (6.6.2).

**Invariant L2 (endpoints).** `min` is the smallest value and `max` the
largest. They are the two rungs the generator pins by fixed rule, and
they are EXACT-OBSERVABLE while the nine interior rungs are
APPROXIMATED (section 9).

**Invariant L3 (null rungs).** A `percentiles` rung may be `null`, and
means the exact rung is not a finite binary64 value. No producible
profile is known to reach this — every interpolated rung lies between
two finite neighbours and is therefore finite — but a loader accepts
`null` rather than refusing a document over a case it cannot rule out,
and a generator treats a null rung as carrying no obligation at that
rung and says so in the report. **The value a generator uses in its
place is fixed by `docs/spec/generation-method-v1.md` G5.1**, so a null
rung is one rule and not two: the loader accepts it here, the method
says what is written for it there, and neither document leaves it to an
implementation. `date_percentiles` rungs are never null.

---

<!-- r1: the roles; empty; numeric_unrepresentable -->

## 6. The roles, one section each

There are **thirteen** roles. In the order section 5.2's rules test
them, they are `empty`, `identifier`, `numeric_unrepresentable`,
`constant`, `binary`, `datetime`, `count`, `continuous`,
`categorical`, `time_of_day`, `affixed_number`, `long_tail_labels`,
`free_text` — thirteen roles in twelve rules, because `count` and
`continuous` are decided by one rule that then chooses between the
two. This is the same thirteen the axis table of section 5.2 carries,
and invariant A5 requires the two to name the same roles.

**This section does not fix the ORDER the rules are tested in.** That
order is section 5.2's, stated there once. Where a role's own test is
not settled by its name, the part below states that test; what every
part states is what a block of the role CONTAINS. The parts appear in
a reading order, not the rule order: `identifier` is tested second and
specified late, because it is the one role no rule reads out of a
column's values.

**The three rules tested last claim only what every earlier rule
declined.** `time_of_day`, `affixed_number` and `long_tail_labels` sit
after the categorical rule, so no column an earlier rule can claim is
diverted into one of them, and no earlier rule's reach depends on
them. That is what makes the role vocabulary safe to grow: holding the
reading of a column's cells fixed, a column the constant, binary,
datetime, numeric or categorical rules read is read by the same rule
with those three beside it. The order and their internal ordering are
section 5.2's.

Each part below gives the keys the role ADDS to the universal set of
section 5.1. **Every key not listed for a role — universal or
role-specific — is FORBIDDEN on that role**, and a loader refuses an
unknown key, naming the key and the column. That sentence is written
down because "forbidden" is the half of a contract a loader can only
enforce if it is written down, and it is the whole of the
forbidden-key discipline: the per-role listings below ARE the matrix,
and there is no second table of it to fall out of step with them. A
fact that does not apply to a role is a key ABSENT from that role,
never a key sometimes present, because this format has no optional
keys.

Some parts below cover more than one role, where roles share a shape:
the label roles are specified once and each then states only what it
adds or restricts, and `count` and `continuous` are specified
together. Every role's own key set is still readable at its own name.

### 6.1 `empty`

A column with no present cells at all: every cell of it was blank, or
one of the spellings that mean "no value", or removed by a
declaration. Which reason each cell was counted absent for is what
`missing_by_class` records.

**Added keys:** none. An `empty` block is exactly the twenty-two
universal keys of section 5.1, with the values below fixed by the
role itself.

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

**Invariant E2.** An `empty` column carries NO per-column `n_rows`
echo. That echo appears only in the blocks invariant Q1 names, and
this role is not one of them.

The two distinctness rows are X4 read through E1; the four census
rows are X2 over a population of zero. Both distinctness counts are
EXACT-OBSERVABLE and trivially met: the twin writes an all-absent
column, which recounts to zero raw and zero folded identities.

**Why the two stand-in rows read as they do**, stated because a reader
will test them against a column holding nothing but a stand-in number.
Such a column is not `empty`. A candidate is judged against the other
numbers of its column — the numbers that are not a candidate of any
kind — and a column that could be emptied this way has none of them,
so its candidates are kept as ordinary numbers under the reason
`too_few_other_values` (section 5.5). Those cells stay present and the
column takes a role with values. A column that reached `empty`
therefore has no candidate to name and none to count.

**The absent cells, and what this block says about them.** This role
adds no rule here. It applies N3, N4 and the publication-class rules,
each stated at its own site, and the result is worth writing out
because `empty` is the one role where the accounting runs over every
row of the table.

`missing_by_class` carries its six keys and its counts on every
`empty` column, declared or not. The publication class does not reach
it: its keys are this format's own words and name no spelling of any
table.

On an UNDECLARED `empty` column — `structural_role` `data` —
`missing_by_source` names every absent spelling at or above
`small_cell_floor` with the count of rows that wore it, `n_missing_blank`
holds the blank cells when at least the floor of them were blank and
`0` otherwise, and `n_missing_withheld` holds what the floor pooled.
N3's sum closes, and here it closes over the whole column:

```
sum(missing_by_source.values()) + n_missing_blank + n_missing_withheld
    == n_missing == n_rows
```

Forty cells alternating a blank and one built-in absent word, at a
floor of eleven, publish `missing_by_source: {"NA": 20}`,
`n_missing_blank: 20` and `n_missing_withheld: 0`. Forty cells wearing
eight different absent spellings at five cells each, at the same
floor, publish an empty map, `n_missing_blank: 0` and
`n_missing_withheld: 40`: no spelling reached the floor and neither
did blankness, so the whole count is pooled.

On a DECLARED `empty` column — `structural_role` `identifier`, which
the empty rule leaves standing — the structural override makes the
block a nothing-publishing column whatever its role, so
`missing_by_source` is `{}` and `n_missing_blank` and
`n_missing_withheld` are both `0`, whatever `n_missing` is.

**`empty` is in no value-publishing class, and that is not the same as
being nothing-publishing.** The role publishes no value because it
holds none; it is not by that fact a nothing-publishing column, and
the difference between the two columns above is exactly the difference
the person made by typing `--identifier`. The argument is the
publication-class section's, at C6-51 and C6-52, and is not
restated here.

The consequence for the twin follows from the source map alone: on the
undeclared column the recorded spellings are written back into the
twin's absent cells under the twin's reproduction rule (C6-115); on the
declared column there is nothing recorded and the twin writes empty
fields.

### 6.2 `numeric_unrepresentable`

A column whose writer meant numbers, where too few of those numbers
are values binary64 can hold for any statistic to be honest. No value
of the column is published.

**When a column takes this role.** At least the parse-line count of
its present cells are NUMERIC-LOOKING — the cells `n_numeric`,
`n_out_of_range` and `n_contradictory` count between them — and fewer
than that same count are numbers this file format can hold. The two
tests share ONE line on purpose: deciding the numeric roles on the
holdable count alone let three unrepresentable cells stop the question
being asked, and deciding them on the numeric-looking count alone let
a ladder be built from a single holdable cell in a hundred. The
population that decides a role and the population its statistics are
computed from are one population.

**Added keys:**

| key | JSON type | range | meaning |
|---|---|---|---|
| `n_whole` | integer ≥ 0 | — | present cells whose notation settles that the value is a whole number |
| `n_fraction` | integer ≥ 0 | — | present cells whose notation settles that the value is not whole |
| `n_whole_unknown` | integer ≥ 0 | — | present cells whose notation settles neither |
| `n_positive` | integer ≥ 0 | — | present cells whose notation settles a positive sign; a cell denoting zero is counted here |
| `n_negative` | integer ≥ 0 | — | present cells whose notation settles a negative sign |
| `n_sign_unknown` | integer ≥ 0 | — | present cells whose notation settles neither |
| `n_distinct_by_occurrences` | multiplicity map | section 5.3 | how many different RAW present spellings covered one row, two rows, and so on |
| `min_length` | integer ≥ 1 | ≤ `max_length` | the shortest numeric-looking cell's length in characters |
| `max_length` | integer ≥ 1 | ≥ `min_length` | the longest numeric-looking cell's length in characters |

**Invariant U1.** `n_whole + n_fraction + n_whole_unknown ==
n_present`.

**Invariant U2.** `n_positive + n_negative + n_sign_unknown ==
n_present`.

**Both sums are over the whole present population, and this role
reaches cells that are not numbers at all.** The detection line above
is a count, so a column may carry a slack of present cells that are
not numeric notation and still take this role. Such a cell settles
neither question, so it is counted in `n_whole_unknown` and in
`n_sign_unknown`; notation that conflicts with itself settles neither
question either and lands in the same two cells. That tie is what
closes both sums on `n_present`, and it is the tie the generation
method's own construction table states
(`docs/spec/generation-method-v1.md` G10.5 step 1).

**Invariant U3.** M1 for `n_distinct_by_occurrences`: its values sum
to `n_distinct`. M2: its keys weighted by its values sum to
`n_present`.

**Invariant U4.** This role is a nothing-publishing column, so
`missing_by_source` is `{}`, `n_missing_blank` and `n_missing_withheld`
are `0`, and every `sentinel_verdicts` entry has
`candidate == "(withheld)"` (N3, V2).

**Invariant U5.** `min_length <= max_length`.

**U-P (a producer obligation, stated because a loader cannot check
it).** `min_length` and `max_length` are measured over the
NUMERIC-LOOKING cells only — not over the whole present population,
because the role tolerates a slack of non-numeric stragglers whose
lengths are facts about text rather than about the numbers this role
exists for, and a straggler's length published as a bound would be
read as magnitude. Each is a count of characters of the cell's text as
the file spells it. A loader holds one document and never the table,
so it cannot recompute either; U5 bounds them against each other and
reaches no further.

**What this role publishes about width, and what it does not.** The
two lengths are the whole of it. No count of cells at any length
between them is published, no other magnitude fact is, and no value,
spelling or fragment of one is. What the two lengths cost is stated
rather than left to be discovered: for decimal numerals length bounds
magnitude, so `max_length` states the largest withheld numeral's order
of magnitude — one cell's worth of floor-free fact, priced in the
disclosure section. What they buy is that a twin of a four-figure
source stops being written at an invented four-hundred-figure width:
the twin invents digit strings that are themselves outside binary64
range, reproduces the whole/fraction and sign counts and the
multiplicity map, and writes them inside the published range with both
ends carried. Every count in this block is EXACT-OBSERVABLE, and so
are the two lengths (section 9).

**And no CROSS-TABULATION of the three count families is published**
(review item P2-C3-F1). This block carries three separate divisions of
the same present cells — by notation class (X2), by whole-number
status (U1) and by sign (U2) — and says nothing about how any two of
them cross. How `n_out_of_range` divides between `n_whole` and
`n_fraction` is the case that matters in practice, and it is not
recorded here or anywhere else in the document. A generator that fixes
such a division by a rule of its own has added a fact to the
description: the real table proves that SOME cross-tabulation of these
counts exists, never which one, so a division the description does not
carry can be infeasible where the real column's own values were not.
The three families are therefore three margins of one packing, and the
method states that rule (`docs/spec/generation-method-v1.md` G10.5).

---

<!-- r2: the label roles; constant; binary -->

### 6.3 The label roles: shared shape

`constant`, `binary`, `categorical` and `long_tail_labels` all publish
LEVELS. Their shared keys are specified once here; sections 6.4 and
6.5, section 6.6.1, and the section for `long_tail_labels` state only
what each adds or restricts. The four are the labels publication
class, and the forbidden-key matrix admits `levels` on no other role.

| key | JSON type | meaning |
|---|---|---|
| `levels` | array of level entries | the published labels and their counts, section 6.3.1 |
| `suppressed_levels` | integer ≥ 0 | how many labels the floor held back |
| `suppressed_rows` | integer ≥ 0 | how many rows those held-back labels covered in total |
| `suppressed_level_counts` | array of integers | the sizes of the held-back labels, sorted ascending |

The floor named throughout this section is `small_cell_floor`, the
setting of section 4.4. Every rule below that reads it is written as
"at least the floor" or "below the floor", so each binds at whatever
value the document carries; at a floor of one the second half is the
empty range, so a description written at that floor holds nothing back
at all. Invariant S13 states that as a rule and lists every field it
reaches — this section's `suppressed_levels`, `suppressed_rows`,
`suppressed_level_counts` and `variants_withheld` among them.

#### 6.3.1 A level entry

An object with exactly these four keys. A loader refuses an entry that
carries any other key, or that is missing one of these, naming the key
and the column.

| key | JSON type | meaning |
|---|---|---|
| `label` | string | the published label, as a FOLDED identity: trimmed and case-folded |
| `count` | integer ≥ 1 | how many present rows carry this folded identity |
| `variants` | object | exact spelling → count, for every spelling of this label that cleared the floor |
| `variants_withheld` | multiplicity map | how many different spellings of this label covered one row, two rows, … below the floor |

Section 7.4 specifies `variants` and `variants_withheld` in full: what
their keys hold, what a value means, where the two keys may and may not
appear, and invariants W1 to W7. Section 5.3 fixes the form of a
multiplicity map.

#### 6.3.2 Label invariants

**These eight invariants are stated over a block that carries
`levels`, not over a list of roles.** None of them names a role, so
each binds every one of the four label roles identically, and none of
them needs restating or widening for any of the four.

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
sorted ascending — non-decreasing, because two held-back labels may
cover the same number of rows and the array is a multiset of sizes, not
a set.

**Invariant B5 (the floor, both ways).** Every `entry.count` is at least
the floor. Every element of `suppressed_level_counts` is at least 1 and
below the floor.

**Invariant B6 (label order).** `levels` is ordered by descending
`count`, and among equal counts by ascending `label`. Order is part of
the canonical bytes and a producer may not shuffle it between runs.
B7 makes the labels distinct, so descending `count` then ascending
`label` is a total order and one set of levels has exactly one
conforming sequence.

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
else. `level_ceiling` is FORBIDDEN on this role: it is `categorical`'s
own key, and this format has no optional keys, so it is absent rather
than sometimes-present.

**Invariant C1.** `n_distinct_folded == 1`.

**Invariant C2.** `len(levels) + suppressed_levels == 1`. Either the one
label cleared the floor — one entry, `suppressed_levels == 0` — or it did
not, in which case `levels == []`, `suppressed_levels == 1`, and the
value itself is not published. C2 is what C1 and B2 come to together.

### 6.5 `binary`

Exactly two folded identities.

**Added keys:** the four shared label keys of section 6.3 and nothing
else. `level_ceiling` is FORBIDDEN on this role, for the reason section
6.4 gives.

**Invariant Y1.** `n_distinct_folded == 2`.

**Invariant Y2.** `len(levels) + suppressed_levels == 2`. As with C2,
this is Y1 and B2 together: either both labels cleared the floor, or one
did and one did not, or neither did and `levels == []`.

Note that `n_distinct` may exceed 2 on a binary column: `A`, `a`, `B`,
`b` is two folded identities and four raw spellings. This contract
publishes those spellings (section 7.4), which is what lets the twin
keep the raw count.

---

<!-- r3: categorical and datetime -->

### 6.6 `categorical` and `datetime`

Two roles with nothing in common but their place in this ordering. Each
has its own key set and its own subsection.

#### 6.6.1 `categorical`

At most a ceiling of different folded identities, each shared by rows.
It is rule 8 of the order in section 5.2, so it claims only a column
every earlier rule declined.

**Added keys:** the four shared label keys of section 6.3, plus:

| key | JSON type | range | meaning | disposition |
|---|---|---|---|---|
| `level_ceiling` | integer ≥ 1 | — | the most different values a set of categories could have had in a table of this many rows | LOADER-ONLY |

**The ceiling arithmetic, so the number has a derivation and not only
a name.** The ceiling is the smaller of `categorical_ceiling` and the
largest whole number of rows lying within `categorical_share` of
`n_rows`, and it is never below `categorical_floor` — the three
settings keys of section 4.4, read against the document's own
`n_rows`. It is a share of the table's ROWS and not of the values the
column happens to hold, and the two differ on a sparse column: a
100-row table whose coded field is filled in 30 times with 6 labels has
a ceiling of 10 here and is a set of categories, where a share of the
PRESENT values would have put its ceiling at 3 and sent an ordinary
shape to free text with nothing published at all. Which labels may then
be SHOWN is a separate question, settled by `small_cell_floor` and not
by this number. The comparison is between whole numbers, so no rounding
of a division decides a role.

That arithmetic is the producer's rule for fixing the number, and no
invariant ties the published value to it. G1 and G2 are what a loader
enforces about `level_ceiling`.

**Invariant G1.** `n_distinct_folded <= level_ceiling`.

**Invariant G2.** `level_ceiling` is LOADER-ONLY. It records the line
the column passed and imposes no obligation on the twin: it must not be
read as a cap the generator has to respect, because the generator
reproduces counts, not the rule that produced them.

**The key belongs to this role and to no other.** It is FORBIDDEN on
`constant`, on `binary`, on `long_tail_labels`, and on every other
role, under the rule that every key not listed for a role is FORBIDDEN
on that role (FKM). `long_tail_labels` is named here because it is the
role a reader will ask about: its columns lie PAST the ceiling, so G1
is exactly the invariant such a column violates by definition, and
this format has no optional keys — the key is absent there rather than
sometimes-present, and the ceiling that column passed is recorded in
its `detection_evidence` sentence instead.

A column above the ceiling is therefore not necessarily free text. It
is offered to the later rules of section 5.2's order, and the
`long_tail_labels` role may claim it on the terms that role's own
section states.

#### 6.6.2 `datetime`

A column at least the parse-line count of whose present cells read
under ONE member of the format vocabulary below, no earlier rule having
claimed it — rule 6 of the order in section 5.2, with the line
`minimum_parse_rate` fixes (section 4.4) applied as a COUNT and never
as a compared share. Where no single member clears the line, the joint
ISO reading below may still claim the column.

**Added keys: thirteen.**

| key | JSON type | permitted values | meaning |
|---|---|---|---|
| `format` | string | one of the ELEVEN members of the table below | the parser family that read the REAL file |
| `resolution` | string | `date`, `datetime`, `quarter`, `month` | which canonical form the published datetimes are written in |
| `time_precision` | string | `subsecond`, `second`, `minute`, `date`, `quarter`, `month` | the FINEST precision any cell of the real column writes |
| `subsecond_digits` | integer ≥ 0 | — | the most fractional-second digits any cell writes |
| `datetimes_read_at` | string | `local`, `utc` | which clock `earliest`, `latest` and `date_percentiles` are written on |
| `earliest` | string | a canonical form, below | the earliest instant, in the canonical form for this resolution |
| `latest` | string | a canonical form, below | the latest instant |
| `earliest_utc_offset` | string | an offset, `(none)`, or `(withheld)` | the UTC offset the earliest cell carried |
| `latest_utc_offset` | string | an offset, `(none)`, or `(withheld)` | the UTC offset the latest cell carried |
| `date_percentiles` | ladder of strings | section 5.6 | the eleven-rung ladder over the ordered instants |
| `n_unparsed` | integer ≥ 0 | — | present cells that did not read as a date under the chosen format |
| `utc_offsets` | object | offset → count | how often each UTC offset appeared, under the floor |
| `resolution_mix` | object | format member → count | how many parsed cells wore each form |

**Three closed vocabularies stand in that table** — `format` with
ELEVEN members, `resolution` with FOUR, `time_precision` with SIX — and
each is written again below inside a table that BINDS it: the eleven
formats are the rows of the next table, where D1 fixes each one's
resolution; the four resolutions are the rows of the canonical-forms
table, which fixes what each one's instants are written as, and of D6's
table; and the six precisions are named in D6's table, which admits no
pair outside it. A closed list copied with nothing binding the copies
is a list two implementations can read differently; each copy here is
the subject of a rule, so a member missing from one of them is a defect
that rule catches. Section 14 indexes all three.

##### The format vocabulary, its readings and its resolutions

Eleven members, each with the shape it reads and the `resolution` it
requires:

| `format` | reads | `resolution` |
|---|---|---|
| `iso-date` | `YYYY-MM-DD`: a four-digit year, two-digit month and day, hyphen-delimited, exactly ten characters | `date` |
| `month-first-date` | a slashed month-first date: a one- or two-digit month, a one- or two-digit day, a four-digit year, slash-delimited | `date` |
| `day-first-date` | a slashed day-first date: a one- or two-digit day, a one- or two-digit month, a four-digit year, slash-delimited | `date` |
| `compact-date` | `YYYYMMDD`: exactly eight digits and nothing else | `date` |
| `slashed-iso-date` | `YYYY/MM/DD`, fields padded | `date` |
| `iso-month` | `YYYY-MM` | `month` |
| `year-quarter` | `YYYY-Qn`: a four-digit year, a hyphen, the letter Q in either case, and a quarter digit `1` to `4` | `quarter` |
| `iso-datetime` | an `iso-date`, one separator — the letter T in either case, or a space — then a clock `HH:MM` or `HH:MM:SS`, an optional fractional part, and an optional UTC offset | `datetime` |
| `iso-mixed` | the joint ISO family reading below | `datetime` |
| `month-first-datetime` | a slashed month-first date, one space, then a clock in one of the two forms the `time_of_day` role fixes | `datetime` |
| `day-first-datetime` | a slashed day-first date, one space, then a clock in one of the two forms the `time_of_day` role fixes | `datetime` |

**Invariant D1 (resolution follows format).** A document's `format` and
`resolution` are one row of the table above. The binding is exact and
total: every member of the format vocabulary appears exactly once, a
document whose pair is not a row does not conform, and a loader refuses
it naming both the format and the resolution it found. Totality is the
point of writing all eleven rows out. A partial binding — one that
named the resolutions of some members and left the rest unbound — would
let a document pair `format: iso-date` with `resolution: datetime` and
be refused by no rule at all, so a whole-date source could be routed as
a datetime column with nothing in the document saying so.

**An `iso-datetime` cell's fractional part is read and discarded**, the
profile recording whole seconds; how many digits the source wrote is
`subsecond_digits`, and that a column wrote any is `time_precision`.
The two fields are where that notation is recorded, and the published
instants are not.

**C6-22 (the unpadded widening).** Exactly four families accept one- or
two-digit month and day fields: `month-first-date`, `day-first-date`,
`month-first-datetime` and `day-first-datetime`. Their grammar is a
one- or two-digit month and day, a four-digit year, and the slash
delimiter. `slashed-iso-date` stays fully padded and `compact-date`
stays exactly eight digits, so no family overlaps another, and no fixed
character-count rule stands over the four widened families.

**The day-first reading rule.** `--day-first` tells the profiler that
slashed dates in this table are day-first, and the settings key
`day_first` (section 4.4) records that the declaration was made.
Its mechanics are NOT a bare order swap, because a swap can silently
reverse a column against its own evidence: with ninety-nine ambiguous
slashed cells and one cell only the month-first reading can parse, a
swapped table lets the day-first reading clear the line first and reads
the whole column backwards, counting the one contrary cell — the
column's only evidence — as unparsed. The rule is therefore
evidence-first: where the option is given and a column's slashed cells
are in play, BOTH slashed readings are counted, and the reading that
parses strictly more cells wins whatever the declaration said; the
declaration decides only a count tie. Which reading a column took is
that column's own `format` and is recorded nowhere else. Absent the
declaration the ordinary reading stands: the vocabulary is tried in its
own fixed order, month-first before day-first, and the first member
that clears the line wins.

**DF-P (producer).** Both slashed readings were counted, the reading
used is the one that parsed strictly more cells, and the declaration
decided only a count tie.

**DF-R (producer).** Where the option was given and a column's slashed
reading was in play, that column carries the slashed-date remark form
of section 4.5 — exactly once — built from the four counts that pass
yields and the reading used. The remark is written over the EVIDENCE
and not over the winner, because a count tie is not always full
ambiguity: a column can hold one cell only the day-first reading parses
AND one cell only the month-first reading parses, evidence in both
directions at equal counts. Section 4.5 fixes the form, its arguments
and its two clauses.

Both are producer obligations because a loader holds one document and
never the table it describes, so it cannot recount either reading.

**C6-23 (the joint ISO reading).** The single-format pass runs first
and its verdict stands wherever it clears: a column of ninety-nine ISO
dates and one datetime cell is an `iso-date` column with one unparsed
cell, and stays one. Only where NO single format clears the parse line
does the joint test run: where `iso-date` and `iso-datetime` cells
TOGETHER reach the line, the column is one datetime column at the
family's finest resolution, with `format` `iso-mixed`. Only the ISO
family mixes. Slashed and compact forms do not, because their mixes are
ambiguous with one another, and a month-with-day mix — `2024-03` beside
`2024-03-17` — is not read at all: it is a recorded decline (residual
R-P4-6), not an oversight.

**C6-25 (`resolution_mix`).** Every datetime block carries
`resolution_mix`, a mapping from format-member strings to integer
counts. Its permitted key sets are closed: on a single-format column,
exactly one key — the column's own `format` member — carrying the full
parsed count; on an `iso-mixed` column, exactly the two members
`iso-date` and `iso-datetime`. No other key set conforms. The counts
are exact and no floor governs them: with a two-member space beside the
published parsed total, a pooled remainder is recoverable by
subtraction, so a floor would withhold nothing, and the fact is what it
is — a form-shape count carrying no value of the table.

**Invariant RM1.** `resolution_mix` keys are exactly the set C6-25
permits for the column's own `format`.

**Invariant RM2.** `resolution_mix` values sum to
`n_present - n_unparsed`. On an `iso-mixed` column the chosen format IS
the joint reading, so `n_unparsed` there counts the cells that read
under neither ISO member.

**RM-P (producer).** The counts are the counts the source's own cells
wore. RM1 and RM2 check the key set and the total, and a 40/60 split
and a 50/50 split of the same hundred cells satisfy both, so a loader
cannot tell a true mix from a false one — the split itself is a
producer obligation.

**`resolution_mix` is REPORT-ONLY.** The twin writes every parsed cell
at the column's finest recorded precision, exactly as the datetime rule
writes every column: a date-form cell cannot spell a
datetime-resolution interior value, and a construction that split the
generated ordinals into two per-form lanes would need its own packing,
feasibility rule and window family for one reading — cost out of
proportion to a fact the reader still receives. The mix is recorded and
not reproduced, on the precedent of the `format` fact itself, and the
twin's report names it as such per column, every run (residual
R-P4-12).

##### The canonical forms, the ranges and the offsets

**The canonical forms**, fixed by `resolution`:

| `resolution` | canonical text | example |
|---|---|---|
| `date` | `YYYY-MM-DD` | `2024-03-15` |
| `datetime` | `YYYY-MM-DD HH:MM:SS` | `2024-03-15 14:05:00` |
| `quarter` | `YYYY-Qn` | `2024-Q1` |
| `month` | `YYYY-MM` | `2024-03` |

All four sort correctly as plain text, which is why L1 compares
`date_percentiles` as text.

**The RANGES are part of the canonical form, not only the shape.** A
loader checks both, and a document failing either is refused:

| field | permitted values |
|---|---|
| `YYYY` | `0001` and above; a year the proleptic Gregorian calendar has |
| `MM` | `01` to `12` |
| `DD` | `01` to the last day that month has, leap years by the Gregorian rule (a year divisible by four, except a century not divisible by four hundred) |
| `HH` | `00` to `23` |
| `MM` (minutes) | `00` to `59` |
| `SS` | `00` to `60` — sixty is deliberate: a leap second is a reading a real table can hold and the shipped date reader accepts one, and a twin cell carries it back unchanged (section 9). D10 refuses it on the one clock no cell can show it on, rather than reporting it as a loss |
| `n` (quarter) | `1` to `4` |

**Checking the shape alone would not be enough.** A rule that fixed the
form and said nothing about the calendar would carry a cost: a
generator does whole-day and whole-second arithmetic on these fields,
so an accepted `2024-99-99` is not refused and is not preserved either
— it is normalized into a real date somewhere else entirely, and the
exact endpoint text a published fact promises is silently lost. The
producer writes no such value: the shipped date reader refuses a
thirty-first of February before it reaches a description.

**The offset forms.** An offset key or endpoint value is one of: `Z`; a
signed offset exactly as the source wrote it, such as `+02:00` or
`-05:00`; `(none)` for a cell that carried no offset at all; or
`(withheld)` for the pooled remainder. **A signed offset carries its
own range**, for the same reason and enforced the same way: the hour
field runs from `00` to `14`, the minute field from `00` to `59`, and
an hour field of `14` requires a minute field of `00`. No zone stands
further from the shared clock than that, and these are the bounds the
shipped date reader already applies to a real cell.

##### The datetime invariants

D1 is stated above, beside the format table whose rows are its own.

**Invariant D2 (offset totals).** The values of `utc_offsets` sum to
`n_present - n_unparsed`. Only cells that parsed have an offset.

**Invariant D3 (the floor on offsets).** Every key of `utc_offsets`
other than `(withheld)` maps to a count at least the floor.
`(withheld)` appears only when the pooled remainder is non-zero.

**Invariant D4 (endpoint offsets never out-name the map).** An endpoint
offset field holds `(none)` when that endpoint's cell carried no
offset; otherwise it holds that offset when the offset is a key of
`utc_offsets`, and `(withheld)` when it is not. An endpoint field may
never name an offset the map is withholding — a value published in one
field of a block that another field of the same block promises to
withhold is a contradiction the contract forbids.

**Invariant D5 (which clock).** `datetimes_read_at` is `local` when the
whole column shares one UTC offset, and `utc` when two or more offsets
appear. Local text is what the table holds and is the more faithful
thing to publish, so it is kept whenever every value shares one offset
— which is every real column but a few. The moment two offsets appear,
local text no longer orders the values and the profile publishes the
instants instead.

**D5 is a published fact, not one a consumer may re-derive from
`utc_offsets`.** Where every offset in a column fell below the floor,
the map collapses to a single `(withheld)` entry whether one offset
wrote the column or ten did, so the map alone cannot settle the
question. That is exactly why the field exists and is published
separately: a consumer never has to combine fields, and never has to
guess, to know which clock it is holding. A loader therefore checks D5
only in the direction the document can support — `utc_offsets` holding
two or more non-`(withheld)` keys requires `datetimes_read_at ==
"utc"` — and accepts either value where the map is fully withheld.

**Invariant D6 (precision is at least as fine as resolution).** The
pair (`resolution`, `time_precision`) is one row of this table:

| `resolution` | permitted `time_precision` |
|---|---|
| `date` | `date` |
| `datetime` | `minute`, `second`, `subsecond` |
| `quarter` | `quarter` |
| `month` | `month` |

Four resolutions, six precisions, and every precision named in exactly
one row, so all twenty-four pairs are decided and none is left to a
reader's judgement. `quarter` and `month` each stand alone with the
resolution of their own name: the resolution vocabulary and its sibling
precision vocabulary carry `month` for the reason the quarter precedent
already had, that a column written `YYYY-MM` has a whole month as its
finest written detail exactly as a column written `YYYY-Qn` has a
quarter.

**Why `date` beside `datetime` is refused, and not merely unusual.** No
twin cell can hold that pair: written `2024-03-15` the column
re-profiles with `resolution: date`, so the published form is lost, and
written `2024-03-15T00:00:00` it re-profiles with `time_precision:
second`, so the published detail is lost. Both fields are
EXACT-OBSERVABLE, so a description carrying that pair is one no
generator can satisfy. The producer cannot make it either — a value
with no time of day does not read as a date AND time at all, so a
column read that way never has a whole date as its finest detail —
which is why refusing it costs nothing a real table can express.

**Invariant D9 (an offset needs a time of day to move).** Every key of
`utc_offsets`, and both endpoint offset fields, are `(none)` or
`(withheld)` unless `resolution` is `datetime` AND `format` is one of
the three ISO members. A whole date, a month and a quarter carry no
clock; `month-first-datetime` and `day-first-datetime` carry a clock
in the `time_of_day` role's two forms and NO offset, because that is
the whole of what their own reader takes; the date reader reads none
of them with an offset, and a twin cell written `2024-03-15+02:00`
reads back as no
date at all. Under D1 this reaches every member of the format
vocabulary but TWO: only `iso-datetime` and `iso-mixed` may carry an
offset at all. The paragraph named four until 2026-08-22, which
contradicted its own opening sentence in the same breath (review item
P4-DATE5-F4): the two slashed stamp members reach `datetime`
resolution, so a reader that took the four-member list would accept
`03/17/2024 14:05+02:00` as a cell of a conforming column, and the
named parser refuses that cell because its clock grammar stops after
the minutes or the seconds.

**And their clock is `local`, always** (invariant D5). A reading that
takes no offset gives every cell it accepts the same one, so a column
read under either slashed stamp member never carried two, and
`datetimes_read_at` of `utc` on such a column is an EXACT-OBSERVABLE
fact no file can meet. D5's allowance for either value where the
offset map is fully withheld is an allowance for readings that CAN
carry an offset, and these two cannot.

**Invariant D7 (subsecond digits).** `subsecond_digits > 0` implies
`time_precision == "subsecond"`, and `time_precision == "subsecond"`
implies `subsecond_digits > 0`.

**Invariant D8 (the ladder covers the parsed cells).**
`date_percentiles` is a ladder over the cells that parsed, and the
checkable form of it is `n_unparsed < n_present`. When `n_present ==
n_unparsed` the column has no parsed cell and cannot reach the datetime
role at all, so both endpoints are always real values.

**Invariant D10 (an endpoint the column's own recorded shape can
show).** Where `resolution` is `datetime`, the seconds field of
`earliest` and of `latest`:

- is `00` when `time_precision` is `minute`, because a cell written
  `YYYY-MM-DDTHH:MM` has no seconds field to carry anything else; and
- is not `60` when `datetimes_read_at` is `utc`, because that field
  names the instant on the SHARED clock, and reading any wall-clock
  cell back onto the shared clock moves a sixtieth second to the
  following minute whatever cell carried it.

And, where `resolution` is `datetime` and `datetimes_read_at` is `utc`,
each endpoint's own minute moved onto the clock its endpoint offset
names — `earliest` by `earliest_utc_offset`, `latest` by
`latest_utc_offset` — is still inside the years `0001` to `9999` that
the canonical forms above can spell. A column on the shared clock
writes every cell on the wall clock its offset names, so an endpoint
within one offset's distance of the calendar's first or last minute
asks for a cell no reader reads back as a date at all. BOTH directions
are refused: an early endpoint behind the shared clock, and a late
endpoint ahead of it.

**Why this is refused rather than reported.** Both endpoints are
EXACT-OBSERVABLE with no exception, so a pair of published facts that
no cell can show at once is settled where it is decided, exactly as the
`date`-beside-`datetime` pair of D6 is. The producer writes none of the
three: `time_precision` is the FINEST precision any cell writes, so a
column whose end carries seconds wrote a seconds field somewhere; a
column put on the shared clock has its endpoints normalized onto that
clock before they are published, which is where a sixtieth second would
have been resolved; and a real column whose values sit within a day of
either end of the calendar has no offsets to mix. So this refuses
nothing a real table can express, and it costs the leap second nothing:
on the `local` clock — which is every column but the few that mix
offsets — `SS` of `60` is accepted and written back unchanged, as
section 9 requires. The third pair is decided here because the loader
already holds all three fields it needs — the endpoint, its offset and
the clock — so it is decidable in the description rather than lowered
to an obligation somewhere else. It was the fourth time this one
obligation had been lowered instead, and section 13 records the four.

**Invariant D11 (the ladder ends ARE the two endpoints).**
`date_percentiles.min == earliest` and `date_percentiles.max ==
latest`. Both pairs describe the same two instants, both are
EXACT-OBSERVABLE, and the producer builds all four from one ordering of
the same values. Leaving the pair untied let a hand-made document
publish a ladder end below `earliest`; a generator pins its first cell
to `earliest` and interpolates the rest inside the ladder, so the twin
then held instants EARLIER than the endpoint it published, and
describing that twin again gave back a different `earliest` with
nothing said about it. Tying the two is what makes D10 cover the ladder
ends as well, since they are the same two texts.

**A consequence, stated rather than left to be discovered.** The
canonical `datetime` form carries seconds and no fractional part, so
`earliest`, `latest` and every rung of `date_percentiles` are at second
resolution EVEN WHEN `time_precision` is `subsecond` and
`subsecond_digits` is 3. The finer precision is a fact about the
column's notation, published in its own two fields, not a property of
the eleven published instants. A generator that must write subsecond
cells reads `time_precision` and `subsecond_digits`, never the ladder.

**Twin datetime cells** follow owner decision 5: a twin datetime cell
is written in the ISO form matching the precision the profile records —
a date-only column writes `2024-03-15`, a month column writes
`2024-03`, a quarter column writes `2024-Q1`, and an offset is written
only where the profile records a real one. A column whose `format` is
`iso-mixed` writes every parsed cell at the finest recorded form, its
mix recorded and not reproduced. The rule is scoped to twin CSV cells
and does not touch the profile's own canonical serialization.

**`format` is REPORT-ONLY.** It names the REAL file's parser family.
The twin is written in ISO syntax at the recorded precision, not in the
source's lexical family, so a month-first column's twin reprofiles as
`iso-date` and this field cannot be reproduced. That narrowed loss is
residual R-P2-7: code that parses dates with an explicit source format
argument needs that argument changed when it moves from the twin to the
real table. The widened readings above widen what is read, not what is
remembered.

##### The calendar placeholders, judged

Two members of the published vocabulary are calendar days — `1900-01-01`
and `9999-12-31` (C6-31) — and a column of dates may be using one of
them to mean "no value" in the way the three stand-in numbers are used.
They are judged, never assumed.

**C6-33 (identity).** A cell matches a placeholder when its own WRITTEN
fields, under the column's own format, denote that calendar day. No
shared-clock normalization and no offset arithmetic enters the
question: a placeholder is a writing convention, and the writer typed
that day.

**C6-34 (the pass, and when it does not run).** Placeholders are judged
by the standing outlier-and-share rule transposed to day ordinals over
the written days, reusing `sentinel_outlier_iqr_multiple` and
`sentinel_minimum_share`; no settings key of its own exists for it. The
pass runs only after the first five rules of section 5.2's order have
declined the un-removed column, and it ENTERS only when the
non-candidate remainder itself clears the datetime rule's parse line.
Otherwise no cell is judged, no cell is removed, and the column lands
exactly where the rules without this pass put it — so a constant or
binary column keeps its claim, and an existing datetime column can
never fall out of its role by this pass. This ordering is tighter than
the affixed rule's, because a removal here could otherwise demote an
existing datetime column. Where the pass DOES enter, the judged cells
are counted absent and the column is described from the remainder.

**C6-35 (verdicts).** A judged placeholder publishes through the
standing verdict machinery of section 5.5: a `sentinel_verdicts` entry
whose `candidate` is the placeholder's canonical ISO day spelling — the
reason that key's permitted values admit a calendar day spelling beside
the stand-in number and `(withheld)` — reusing the standing `verdict`
and `reason` enumerations and the standing withholding on
nothing-publishing columns.

**CP-P (producer).** A published placeholder verdict is the verdict the
outlier-and-share rule reached over the source's own written days. A
loader holds no source and cannot recompute it.

A value the person named with `--keep-value` is data, and this pass may
not read it as a hole — C6-117 states that rule over the numeric pass,
the calendar pass and the built-in vocabulary alike.

Cells this pass reads as absent are counted under the
`(date-sentinel)` key of `missing_by_class` (section 5.4), which is
nonzero only on a column the pass entered. A `missing_by_source`
spelling this pass put there stays blank in the twin, under the named
exception the hole-spelling reproduction rule states (C6-115, with its
reason at C6-116).

**The order of `sentinel_verdicts` entries is invariant V4**, stated
in full at 5.5. It is total over all three kinds of candidate this
format permits — numbers, calendar day spellings and `(withheld)` —
and the calendar kind is the one this role's placeholder pass
produces. It is stated once, there, because one ordering rule governs
every block that carries verdicts, and a rule written twice is a rule
that comes to differ.

---

<!-- r4a: count and continuous -->

### 6.7 `count` and `continuous` — the numeric roles

Both roles carry exactly the same key set — the fifteen keys below,
added to the universal set of section 5.1. They differ only in the
verdict that produced them.

**When a column takes one of these roles.** Rule 7 of the order in
section 5.2 claims a column when at least the parse-line count of its
present cells are NUMERIC-LOOKING — the cells `n_numeric`,
`n_out_of_range` and `n_contradictory` count between them — and at
least that same count are values this file format can hold, which is
`n_numeric`. The two tests share ONE line on purpose, and it is the
line section 6.2 states for `numeric_unrepresentable`: deciding the
numeric roles on the holdable count alone let three unrepresentable
cells stop the question being asked, and deciding them on the
numeric-looking count alone let a ladder be built from a single
holdable cell in a hundred. The population that decides a role and the
population its statistics are computed from are one population.
Falling short of the line decides nothing but this rule — the column
goes on to `categorical` and may still be a set of categories.

**Which of the two: the column COUNTS THINGS, and takes role `count`,
when all three of these hold. It is `continuous` otherwise.**

1. Every numeric-looking cell's notation settles that its value is a
   WHOLE NUMBER, and there is at least one numeric-looking cell.
2. No present cell's notation settles a negative sign: `n_negative`
   is `0`.
3. No cell whose writer MEANT a number leaves its sign unsettled.

**The reasons, because each condition was bought.** A column of counts
must be whole and non-negative in every cell whose writer meant a
number, INCLUDING the ones no format can hold: `(1e999)` is visibly
negative and `1e-999` is visibly a fraction strictly between zero and
one, and both were published as whole non-negative counts before
review item P1-R5-F2. Condition 3 is the same principle applied to a
cell that settles nothing: a cell whose sign the text does not settle
is enough to rule the role out, because missing evidence is not
evidence of nothing.

**Condition 3 refuses no document condition 1 admits, under the
notation this format reads today**, and is stated anyway. The only
numeric-looking cell whose sign the text leaves unsettled is one whose
notation conflicts with itself — a sign inside accounting parentheses
— and such a cell settles the whole-number question no more than the
sign question, so it already fails condition 1. The two are different
questions, and a notation that settled wholeness without settling sign
would separate them; a reader checking this rule against an
implementation should know which of the three is doing the work.

**A straggler of ordinary text does not rule `count` out, and
condition 3 is narrow for exactly that reason.** The parse line
tolerates a slack of present cells that are not numeric notation at
all. Such a cell settles neither the sign question nor the whole-number
question, and it says nothing about whether this column counts things,
so it is not what condition 3 asks about: condition 3 ranges over the
cells whose writer meant a number and nothing else. This is
deliberately NARROWER than the published sign margin of section 6.2,
which runs over the whole present population because U2 must close on
`n_present`. The two are different questions and a producer that
answers one with the other either refuses a legitimate `count` column
or writes a description its own loader refuses.

**The choice is a PRODUCER rule.** Like the rule order itself
(section 5.2), it decides what a producer writes. A loader holds one
document and never the table it describes, so it cannot re-run the
three conditions; what a loader enforces about the pair is A4 — the
triple (`role`, `statistical_type`, `quality_state`) is one row of the
axes table — together with the Q family below. Q8 is what keeps a
consumer off the role name.

**Added keys:**

| key | JSON type | range | meaning | disposition |
|---|---|---|---|---|
| `percentiles` | ladder object | section 5.6 | the eleven-rung ladder over the PARSED values | `min` and `max` EXACT-OBSERVABLE; the nine interior rungs APPROXIMATED |
| `mean` | number or `null` | — | the arithmetic mean of the parsed values | APPROXIMATED |
| `std` | number or `null` | ≥ 0 when a number | the sample standard deviation, divided by n−1 | APPROXIMATED |
| `skew` | number or `null` | — | the moment-based skewness | APPROXIMATED |
| `std_unrepresentable` | boolean | — | true when the exact spread is larger than binary64 can hold | EXACT-OBSERVABLE |
| `n_zero` | integer ≥ 0 | — | parsed values equal to zero | EXACT-OBSERVABLE |
| `n_negative` | integer ≥ 0 | — | present cells whose notation settles a negative sign, including ones no statistic could use | EXACT-OBSERVABLE |
| `n_negative_unrepresentable` | integer ≥ 0 | — | out-of-range cells whose notation settles a negative sign | EXACT-OBSERVABLE |
| `n_used_in_statistics` | integer ≥ 0 | — | how many present cells the statistics were computed from | EXACT-OBSERVABLE |
| `n_left_out_of_statistics` | integer ≥ 0 | — | how many present cells were not | EXACT-OBSERVABLE |
| `numeric_share` | number | 0.0 ≤ x ≤ 1.0 | the share of present cells whose writer meant a number | EXACT-OBSERVABLE |
| `integer_valued` | boolean | — | true when every numeric-looking cell is a whole number | EXACT-OBSERVABLE, routed by the published FACT and not by role |
| `n_rows` | integer ≥ 0 | `== n_rows` at the top level | the table's row count, echoed | LOADER-ONLY |
| `numeric_styles` | object | section 7.5 | how many cells were written in each spelling style, under the floor | EXACT-OBSERVABLE against the recount identity of section 7.5.7 |
| `fraction_widths` | object | C6-28 to C6-30 below | how many `decimal`-styled cells were written at each fraction width, under the floor | EXACT-OBSERVABLE, under the producer obligation FW-P |

Fifteen keys. Every one is present in every block of these two roles —
this format has no optional keys — and every key not listed here or in
section 5.1 is FORBIDDEN on them (section 6.11).

**Where the approximations and the recounts are fixed.** The nine
interior rungs are APPROXIMATED inside a rung-by-rung two-sided
envelope, fixed by `docs/spec/generation-method-v1.md` G5.6 and
restated there as G12.2. A generator that collapses the nine interior
rungs onto the endpoints must FAIL that envelope, and so must one that
ignores, permutes or swaps rungs. `mean`, `std` and `skew` are
APPROXIMATED under a fixed formula and a two-sided bound, both fixed
by that document's G12.3. `numeric_styles` is EXACT-OBSERVABLE against
the recount identity of section 7.5.7: every published count is met or
exceeded, the three forms the remainder cannot reach are exact, and
the remainder is spelled by its own cells' values. `n_distinct` and
`n_distinct_folded` are universal keys whose disposition on this role
group is set in section 9.

**The ladder.** `percentiles` is the ladder — the fixed eleven rungs
of section 2.3 — read over the PARSED values. Section 5.6 states L1,
L2 and L3, including what a `null` rung means and what a generator
writes in its place, and this section adds nothing to them.

#### `numeric_styles` on these roles

`numeric_styles` is REQUIRED on `count`, `continuous` and
`affixed_number`, and FORBIDDEN on every other role including
`numeric_unrepresentable`. **The reason.** Those are the roles whose
twin cells are written as parsed numbers from the ladder in owner
decision 8's spelling family — on `affixed_number`, inside its affix
pair — so they are the roles where the reader's inferred type is at
stake and where a style map is something the generator can discharge.
A `numeric_unrepresentable` column's twin cells are invented digit
strings at one canonical width (residual R-P2-1), so a style map there
would describe a form the twin is already unable to reproduce.

**The fact is about FORM, not values.** It carries no value, no
magnitude and no spelling — only how many cells used each form. It
exists because three source families — `0`, `00`, `000`; `0.0`,
`00.0`, `000.0`; and `0e0`, `00e0`, `000e0` — otherwise produce
byte-for-byte identical column blocks, and an ordinary reader infers a
whole-number column from the first and a decimal column from the other
two.

**The styles are exactly these six, and no seventh may be added by an
implementation:**

| style | what it names |
|---|---|
| `plain` | the canonical spelling: digits, an optional leading minus, no decimal point, no exponent, no redundant leading zero |
| `leading_zero` | the digits before any decimal point begin with a redundant `0` |
| `leading_plus` | the cell begins with `+` |
| `decimal` | the cell carries a decimal point |
| `exponent_lower` | the cell carries a lower-case `e` exponent |
| `exponent_upper` | the cell carries an upper-case `E` exponent |

The wire shape, the first-match-wins classification ladder that assigns
each counted cell exactly one style, invariants P1 through P4 and the
twin's recount obligation are stated in section 7.5. What this section
fixes is that the key stands on these roles and on no others.

#### `fraction_widths`

This role carries `fraction_widths`, a sibling of `numeric_styles` on
the block rather than a key inside it. **Section 7.6 states it in
full** — what it holds, its key grammar, and invariants P5, P6 and P7 —
because it stands on three roles and a rule stated at one of them
would be a rule the other two carry by inference.

What belongs here is only its reach: `fraction_widths` is REQUIRED on
`count`, `continuous` and `affixed_number`, and FORBIDDEN on every
other role, exactly as `numeric_styles` is and for the same reason
(7.5).

#### The Q family

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
values binary64 can hold clears `minimum_parse_rate` of the present
cells, so the ladder is never built from nothing.

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
report.

**Invariant Q8 (`integer_valued` is a FACT, not a role).** The twin's
integer rule is routed by this published boolean and never by whether
the role name is `count`. A `continuous` column may publish
`integer_valued: true` — a column of whole numbers containing a
negative one is exactly that — and its twin cells are whole numbers.

**Invariant Q9 (`numeric_share`).** `numeric_share` is
`(n_numeric + n_out_of_range + n_contradictory) / n_present`, computed
as a share of the present cells, and is `0.0` when `n_present` is 0 —
which cannot occur on these roles by Q3.

**Invariant Q10 (`n_negative_unrepresentable` bound).**
`n_negative_unrepresentable <= n_out_of_range` and
`n_negative_unrepresentable <= n_negative`.

**Invariant Q11 (`n_zero` bound).** `n_zero <= n_numeric`.

**Where else this family is enforced.** On `affixed_number` every
invariant of this section is read over the CORES, with
`n_core_numeric` in place of `n_numeric` (AF7), and nowhere else. The
four universal cell-census counts answer for the cells on that role as
on every other.

---

<!-- r4b: identifier and free_text -->

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

---

<!-- r6: the publication class and the forbidden-key matrix -->

### 6.10 The publication class

Two things are settled here and they are not the same thing. The
first says which columns publish no value of the table anywhere in
their block; it is BINARY, and it is the term the rest of this format
is written in. The second sorts the role vocabulary into the three
classes that decide, for a column that DOES publish values, which
kind it publishes. A reader who meets the second first will expect
the first to be one of its three cases. It is not, and this section
is ordered so that the two cannot be run together.

#### The nothing-publishing column

**C6-49.** Three roles publish no value of the table anywhere in
their block — `numeric_unrepresentable`, `identifier` and `free_text`
— and so does any column whose `structural_role` is `identifier`,
whatever its role. On those columns, and only those,
`missing_by_source` is empty, `n_missing_blank` and
`n_missing_withheld` are both zero, and every sentinel candidate
reads `(withheld)`. **This is a property of the whole BLOCK, not of
any one field: it is what stops the next field somebody adds from
being the one that leaks.**

**The term is BINARY.** A column either is a nothing-publishing
column or it is not. There is no third state and no partial one, and
the role `empty` does not by itself make a column one (C6-51).
Wherever this document says *a nothing-publishing column* it means
this term and no other — in N3's source accounting, in N6's two
absence counts, in V2's withheld sentinel candidate, in the per-role
restatements U4, I3 and F3, and at every other site the term appears.

**The class is decidable from the document alone.** It is a function
of `role` and `structural_role`, and every block publishes both, so a
consumer can always tell "this column publishes no source accounting"
from "this column had nothing to account for".

**Why the rule is written over the block and not over a list of
dangerous fields.** The per-field form was tried and it failed in
service. `missing_by_source` and the published levels had each been
closed by name; `sentinel_verdicts` was added later, carrying a
candidate's spelling under `candidate`, and was on nobody's list — so
an `identifier` column published `-999` while its own summary
promised that no value of it would appear anywhere. The block rule is
what a producer implements as a whitelist: a key of such a block
carries its own contents only where this format has said in writing
that the key holds a count, a length, a word count, or a yes-or-no
about the column as a whole.

**What such a column still publishes**, so that the rule is not read
as silence: its universal counts, and whichever keys section 6.11
marks for its role — lengths and word statistics, digit and
code-alphabet counts, the whole-number test, the multiplicity map,
and on `numeric_unrepresentable` the whole-number and sign counts.
Section 6.11 is the authority on which of those each of the three
roles carries.

Its `detection_evidence` and its `remarks` are still written, because
a sentence of this document is not free text: it is built from one
form of the closed note grammar, filled with whole numbers, words of
this package's own enumerated vocabulary, and other forms of that
grammar. The grammar admits exactly one source-derived argument class
— the bound affix strings of an `affixed_number` column's remark, at
the two positions that remark fixes — and `affixed_number` is a
ranges-class role, so no form a nothing-publishing column can raise
takes an argument that any value of the table could fill.

#### The three value-publishing classes

**C6-50.** A role publishes through one channel, and the channel —
not the branch that happened to build the block — decides what may
appear in the output. Every one of the thirteen roles sits in exactly
one row of the table below:

| class | roles | what the class means |
|---|---|---|
| labels | `constant`, `binary`, `categorical`, `long_tail_labels` | the values themselves appear, folded, with counts, and only when at least `small_cell_floor` rows share them |
| ranges | `count`, `continuous`, `datetime`, `time_of_day`, `affixed_number` | no spelling appears; order statistics computed from the values do. ONE named exception, C6-9's, confined by section 6.11 to `affix_prefix` and `affix_suffix` |
| nothing | `numeric_unrepresentable`, `identifier`, `free_text` | no value, no spelling, no fragment of one, anywhere — not in levels, not in `missing_by_source`, not in the evidence, not in a remark, not in a publication note, not in a sentinel verdict |
| **no value-publishing class** | `empty` | it has no value to publish, and it is NOT thereby a nothing-publishing column (C6-51) |

The three value-publishing classes carry exactly twelve of the
thirteen roles, each in exactly one row. Membership is a property of
the whole block, on the same reasoning C6-49 gives: a class stated
per field is a class the next field escapes.

**The affix exception is an exception and not a fourth class.** A
fourth class would have to be given a meaning everywhere the three
are enforced; an exception is confined by one matrix, which is where
section 6.11 confines it. The labels class is untouched by it, and
the nothing class's "no value, no spelling, no fragment of one"
sentence is untouched by it.

#### `empty`, and the fourth bucket

**C6-51.** `empty` is in NO value-publishing class, because it has no
value to publish. **Being in no value-publishing class is not the
same as being a nothing-publishing column, and an `empty` column
nobody declared is not one.** Its `missing_by_source` carries the
absent SPELLINGS its cells wore, under the floor, with their counts,
and its two absence counts are written exactly as N3 and N6 have them
for any other column that is not nothing-publishing.

**The exactly-one invariant is therefore over FOUR buckets** — the
three value-publishing classes, plus `empty` — and this is how the
shipped battery has stated it since Phase 1
(`test_every_role_belongs_to_exactly_one_publication_class`,
`tests/test_column_analysis.py:573-583`, which tests membership of
the three tuples AND `role == ROLE_EMPTY` and asserts exactly one of
the four is true). Plan amendment A-P4-10 governs and states it in
that shape. The invariant is a property of the table above rather
than of a document: a loader reads a role and finds its bucket, and
no parsed document can violate it.

**What follows for an `empty` column's source accounting, worked.**
Profile forty cells alternating a blank and `NA`, undeclared, at
`small_cell_floor: 11`. The column takes role `empty` and publishes
`missing_by_source: {"NA": 20}`, `n_missing_blank: 20`,
`n_missing_withheld: 0`, and N3 closes: 20 + 20 + 0 == 40. Profile
eleven cells that all hold one built-in absent word at the same floor
and the column publishes that word with the count 11, which the twin
then writes in all eleven rows under C6-115.

**Why this is stated at length rather than assumed.** Reading the
class table as a three-way partition of all thirteen roles puts
`empty` in the nothing class, and the reasoning that gets there is
sound-sounding: a column with no values discloses none. The
conclusion breaks a shipped fact. `ROLES_PUBLISHING_LABELS`,
`ROLES_PUBLISHING_RANGES` and `ROLES_PUBLISHING_NOTHING`
(`src/synthtwin/taxonomy.py:258-264`) name three roles each and
`empty` is deliberately in none of them; `src/synthtwin/contract.py`
ships the nothing tuple alone, listing exactly
`numeric_unrepresentable`, `identifier` and `free_text`. Taken the
other way the forty-cell column above would publish an empty map and
two zero counts, N3's sum would fail for it, the published spelling
would vanish with no rule saying it had, and the twin would write
twenty blank fields where the description records `NA` — the
reproduction obligation failing silently, produced by one wrong table
row.

#### The structural override, and where the exactly-one question is settled

**C6-52.** A column whose `structural_role` is `identifier` is a
nothing-publishing column whatever its `role`, and this rule wins
wherever it and the class table of C6-50 could differ. It is written
as an override rather than as a row of that table because a row would
put such a column in two rows at once.

It is also where the exactly-one question actually bites. A DECLARED
all-absent column carries `role: empty` with `structural_role:
identifier`, because the empty rule settles before the declaration
(C6-3); the override makes it nothing-publishing, so its
`missing_by_source` is empty and both absence counts are zero. The
UNDECLARED all-absent column beside it is not nothing-publishing and
publishes its source accounting under the floor. Those two columns
differ, they are meant to, and the difference between them is exactly
the difference the person made by typing `--identifier`.

**The override is written generally, and under the rule order only
two roles can reach it.** The declaration is decided at rule 2, so a
declared column reaches `empty` (rule 1) or `identifier` (rule 2) and
no other role — which is what invariant A3 states. The general
wording is deliberate: it is what stops a role added later from
arriving outside the override, and it costs nothing while A3 holds.

### 6.11 The forbidden-key matrix

**C6-53. Every key not listed for a role — universal or
role-specific — is FORBIDDEN on that role**, and a loader refuses an
unknown key naming both the key and the column. "Forbidden" is the
half of a contract a loader can only enforce if it is written down,
so it is written down here, once, in one place, for all thirteen
roles.

The listing for a role is the twenty-two universal keys of section
5.1, which are required on every role and are omitted from the matrix
for that reason, together with the cells marked below. **A marked
cell is REQUIRED as well as permitted**: this format has no optional
keys, so a key of a role is present in every block of that role, on
every run, including where its content is zero or empty. A blank cell
is FORBIDDEN in the sense section 2.1 fixes: the key is absent from
every block of that role, and a loader refuses a document carrying
it.

The thirteen columns, abbreviated for width: `emp` `empty`, `unr`
`numeric_unrepresentable`, `con` `constant`, `bin` `binary`, `cat`
`categorical`, `ltl` `long_tail_labels`, `dtm` `datetime`, `tod`
`time_of_day`, `cnt` `count`, `ctn` `continuous`, `afx`
`affixed_number`, `idn` `identifier`, `txt` `free_text`.

| key | emp | unr | con | bin | cat | ltl | dtm | tod | cnt | ctn | afx | idn | txt |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| `levels` | | | ● | ● | ● | ● | | | | | | | |
| `suppressed_levels` | | | ● | ● | ● | ● | | | | | | | |
| `suppressed_rows` | | | ● | ● | ● | ● | | | | | | | |
| `suppressed_level_counts` | | | ● | ● | ● | ● | | | | | | | |
| `level_ceiling` | | | | | ● | | | | | | | | |
| `format` | | | | | | | ● | | | | | | |
| `resolution` | | | | | | | ● | | | | | | |
| `resolution_mix` | | | | | | | ● | | | | | | |
| `time_precision` | | | | | | | ● | | | | | | |
| `subsecond_digits` | | | | | | | ● | | | | | | |
| `datetimes_read_at` | | | | | | | ● | | | | | | |
| `earliest` | | | | | | | ● | ● | | | | | |
| `latest` | | | | | | | ● | ● | | | | | |
| `earliest_utc_offset` | | | | | | | ● | | | | | | |
| `latest_utc_offset` | | | | | | | ● | | | | | | |
| `date_percentiles` | | | | | | | ● | | | | | | |
| `utc_offsets` | | | | | | | ● | | | | | | |
| `n_unparsed` | | | | | | | ● | ● | | | | | |
| `clock_form` | | | | | | | | ● | | | | | |
| `clock_percentiles` | | | | | | | | ● | | | | | |
| `percentiles` | | | | | | | | | ● | ● | ● | | |
| `mean` | | | | | | | | | ● | ● | ● | | |
| `std` | | | | | | | | | ● | ● | ● | | |
| `skew` | | | | | | | | | ● | ● | ● | | |
| `std_unrepresentable` | | | | | | | | | ● | ● | ● | | |
| `n_zero` | | | | | | | | | ● | ● | ● | | |
| `n_negative` | | ● | | | | | | | ● | ● | ● | | |
| `n_negative_unrepresentable` | | | | | | | | | ● | ● | ● | | |
| `n_used_in_statistics` | | | | | | | | | ● | ● | ● | | |
| `n_left_out_of_statistics` | | | | | | | | | ● | ● | ● | | |
| `numeric_share` | | | | | | | | | ● | ● | ● | | |
| `integer_valued` | | | | | | | | | ● | ● | ● | | |
| `n_rows` (echo) | | | | | | | | | ● | ● | ● | | |
| `numeric_styles` | | | | | | | | | ● | ● | ● | | |
| `fraction_widths` | | | | | | | | | ● | ● | ● | | |
| `affix_prefix` | | | | | | | | | | | ● | | |
| `affix_suffix` | | | | | | | | | | | ● | | |
| `n_affixed` | | | | | | | | | | | ● | | |
| `n_core_numeric` | | | | | | | | | | | ● | | |
| `n_core_out_of_range` | | | | | | | | | | | ● | | |
| `n_core_contradictory` | | | | | | | | | | | ● | | |
| `n_core_not_numeric` | | | | | | | | | | | ● | | |
| `n_whole` | | ● | | | | | | | | | | | |
| `n_fraction` | | ● | | | | | | | | | | | |
| `n_whole_unknown` | | ● | | | | | | | | | | | |
| `n_positive` | | ● | | | | | | | | | | | |
| `n_sign_unknown` | | ● | | | | | | | | | | | |
| `min_length` | | ● | | | | | | | | | | ● | |
| `max_length` | | ● | | | | | | | | | | ● | |
| `all_whole_numbers` | | | | | | | | | | | | ● | |
| `length` | | | | | | | | | | | | | ● |
| `words` | | | | | | | | | | | | | ● |
| `n_all_digits` | | | | | | | | | | | | ● | ● |
| `n_code_alphabet` | | | | | | | | | | | | ● | ● |
| `n_distinct_by_occurrences` | | ● | | | | | | | | | | ● | ● |

**Fifty-five rows, one hundred and seven marked cells**, distributed
`empty` 0, `numeric_unrepresentable` 9, `constant` 4, `binary` 4,
`categorical` 5, `long_tail_labels` 4, `datetime` 13, `time_of_day`
5, `count` 15, `continuous` 15, `affixed_number` 22, `identifier` 6,
`free_text` 5. The counts are stated so that a reader can check a
column of the matrix against the role's own section without counting
twice.

**The `empty` column is blank, and that is the whole of it.** An
`empty` block is exactly the twenty-two universal keys. It carries no
per-column `n_rows` echo (E2), and it is not blank because it
publishes nothing — C6-51 — but because it has no role-specific fact
to publish.

**Names that stand in more than one column, each named so a reader
does not read a coincidence into the matrix.**

- `n_negative` is ONE key with ONE meaning — cells whose notation
  settles a negative sign — asked on each role of the population that
  role's facts describe: the present cells on
  `numeric_unrepresentable`, over a column no statistic could use,
  and on `count` and `continuous`; the cores on `affixed_number`
  (AF7). The row shows four columns filled and no ambiguity follows.
- `earliest`, `latest` and `n_unparsed` stand on `datetime` and on
  `time_of_day`. They ask the same question of two different domains:
  on `datetime` the endpoints are canonical instants at the recorded
  `resolution`; on `time_of_day` they are clock values written in
  `clock_form` (T1), and `n_unparsed` counts cells that no clock
  reading accepted rather than cells that no date format read.
- `min_length` and `max_length` stand on `numeric_unrepresentable`
  and on `identifier`, and here the POPULATIONS DIFFER. On
  `identifier` they are measured over the present cells (I4:
  `min_length >= 1`). On `numeric_unrepresentable` they are measured
  over the numeric-looking cells only, because that role tolerates a
  slack of non-numeric stragglers whose lengths are facts about text
  rather than about the numbers the role exists for. That population
  is a producer obligation, U-P, because a loader holding one
  document cannot check what a length was measured over; U5 bounds
  the pair, `min_length <= max_length`. A consumer that reads one as
  the other reads a different measurement.
- The per-column `n_rows` echo is a DIFFERENT QUANTITY from the
  document-level `n_rows`, and Q1 confines it to `count`,
  `continuous` and `affixed_number` and makes it LOADER-ONLY. The
  document-level key is the one that carries the row-count
  obligation.
- The quantitative set on `affixed_number` — `percentiles` through
  `numeric_styles`, and `fraction_widths` beside it — describes the
  CORES, not the cells. The four universal cell-census counts answer
  for the cells on that role as on every other, and the cores have
  four counts of their own beginning with `n_core_numeric` (C6-7).
  Every quantitative invariant this format states over `n_numeric` is
  read on that role over `n_core_numeric`, and nowhere else (AF7).

**Three confinements this matrix is where a reader finds enforced.**
`numeric_styles` and `fraction_widths` stand on exactly `count`,
`continuous` and `affixed_number`, and are forbidden everywhere else
including `numeric_unrepresentable`. `level_ceiling` stands on
`categorical` alone: it is that role's own key, its invariant is that
folded distinctness is at or under the ceiling, and that is exactly
what a `long_tail_labels` column violates by definition, so the key
is absent there rather than sometimes-present (G1L), and the ceiling
such a column passed is recorded in its `detection_evidence`
sentence. And **no key of any ranges-class role but `affix_prefix`
and `affix_suffix` may carry a spelling** — the whole of C6-9's
exception, held to two cells of one column of this matrix.

**The matrix is total.** A conforming column block's key set is
exactly the twenty-two universal keys plus the marked cells of its
role's column, and nothing else may appear.

---

<!-- r5a: affixed_number -->

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

---

<!-- r5b: time_of_day -->

### 6.13 `time_of_day`

A column of clock times written with no date beside them: an hour, a
minute, and on some columns a second. It is rule 9 of the order in
section 5.2, tested after the categorical rule, so it claims only a
column every earlier rule declined — in particular only one the
datetime rule did not read, that rule running at 6 and reading a clock
only as the tail of a date.

#### When a column takes this role

**C6-10.** At least the parse-line count of the column's present cells
match ONE of the exactly two clock forms below, and no earlier rule
claimed the column. The line is the count `minimum_parse_rate` fixes
(section 4.4), applied as a COUNT and never as a compared share, so
that no rounding of a division decides a role; the arithmetic of the
count itself is section 4.5.2's.

| `clock_form` | the text a cell wears | fields and ranges | the form's ordinal unit | spellings |
|---|---|---|---|---|
| `hh-mm` | `HH:MM` | hours `00`–`23`, minutes `00`–`59` | minutes of day, `0` to `1439`: 60 × `HH` + `MM` | 1,440 |
| `hh-mm-ss` | `HH:MM:SS` | hours `00`–`23`, minutes `00`–`59`, seconds `00`–`59` | seconds of day, `0` to `86399`: 3600 × `HH` + 60 × `MM` + `SS` | 86,400 |

Every field is exactly two digits, and no cell matches both forms. The
fixed width is what gives each ordinal exactly one spelling, and what
makes plain text comparison of two cells agree with their clock order.
Both are load-bearing: the first is why every value an interpolation
can reach has a canonical spelling in the column's own form and no
generated cell is ever truncated or widened to fit, the second is why
the ladder can be checked as written text. These are also the two
forms the `month-first-datetime` and `day-first-datetime` members of
the format vocabulary read as the tail of a slashed date; they are
enumerated here and nowhere else.

**One form must clear the line; cells of the other are counted, not
fatal.** This is the datetime rule's arithmetic transposed, where one
date format must clear the line. Cells of the other clock form, and
every other present cell no clock reading accepted, are counted in
`n_unparsed` inside the slack the line leaves. An in-slack minority
form is the line's ordinary arithmetic and not a decline.

**Where BOTH forms clear the line, the finer wins: the column takes
`hh-mm-ss`.** A cell matches at most one form, so both clear only
where twice the parse-line count is at most `n_present`, which a
lowered `minimum_parse_rate` permits and a high one does not. The
tie-break is fixed here so that two producers reading one table under
one setting cannot disagree about the column's form, its endpoints,
its ladder or its unparsed count. Under it the `HH:MM` cells are the
ones counted in `n_unparsed`.

#### Four readings this role refuses, each a rule and not an omission

1. **A fractional part on the seconds field does not parse.** This
   role publishes no key that could record one — `subsecond_digits` is
   `datetime`'s and is not imported — so a reading that accepted such
   a cell would silently drop the fraction and thereby approximate
   every cell of the column.
2. **A seconds field of `60` does not parse.** The ordinal spaces
   above have no faithful point for a leap second. `datetime` accepts
   an `SS` field of `60` on its local-clock endpoints, on the strength
   of an endpoint construction that publishes an instant's own FIELDS
   rather than an ordinal; this role publishes ordinals and does not
   import that machinery, so it refuses the reading rather than carry
   a value it would have to move to the following minute.
3. **A single-digit hour does not parse.** Both forms are fixed-width,
   which is what merits the two properties above; a variable width
   would give one ordinal two spellings.
4. **Two clock forms in one column are not read as one clock.** There
   is no JOINT reading: one form carries the column and the other
   form's cells are counted in `n_unparsed`, and where neither carries
   it the column declines to the later rules. `datetime` has a joint
   reading across ISO resolutions because that mix is the dominant
   export shape; clock-precision mixes are not, so this version takes
   the narrow reading and names the joint one as the candidate for a
   later widening, on the resolution-mix precedent.

Each refusal sends the column to the later rules, where — if nothing
later claims it — it is declined with the competing-readings remark,
whose clock argument names how many cells a clock reading accepted
under the form that came closest (section 4.5, `remark_no_reading_fits`).
All four are named residual R-P4-5.

#### Added keys: five

| key | JSON type | permitted values | meaning | disposition |
|---|---|---|---|---|
| `clock_form` | string | `hh-mm`, `hh-mm-ss` | which form the column's cells wore, and the form every published clock value of the block is written in | EXACT-CONTROL |
| `earliest` | string | a clock value in `clock_form` | the earliest clock value the column holds | EXACT-OBSERVABLE |
| `latest` | string | a clock value in `clock_form` | the latest clock value the column holds | EXACT-OBSERVABLE |
| `clock_percentiles` | ladder of strings | section 5.6, rungs in `clock_form` | the eleven-rung ladder over the ordered clock values of the cells that parsed | `min` and `max` EXACT-OBSERVABLE; the nine interior rungs APPROXIMATED, inside the window the generation method's approximated-fields table fixes for this role |
| `n_unparsed` | integer ≥ 0 | — | present cells no clock reading of C6-10 accepted, the other form's cells among them | EXACT-OBSERVABLE as counted neutral stand-ins, explicitly OUTSIDE the clock representation obligation |

**C6-11.** Those five are the whole of what this role adds to the
twenty-two universal keys of section 5.1. A container's disposition
does not cover its leaves (section 2.2), which is why the ladder's
ends and its interior are disposed separately.

`clock_percentiles` is a ladder in the shape section 5.6 fixes: an
object with exactly the eleven keys `min`, `p01`, `p05`, `p10`, `p25`,
`p50`, `p75`, `p90`, `p95`, `p99`, `max`, no more and no fewer. The
rungs are NAMED rather than positional, as `percentiles` and
`date_percentiles` are, because the generator pins `min` and `max` by
name and a positional array would make the two ends a counting
convention. The ladder is SELECTION — eleven order statistics of cells
the column really holds, with no interpolation in it.

#### The ordinal, the endpoints and the ladder

A clock value's ORDER is its ordinal in the unit its own form sets:
minutes of day for `hh-mm`, seconds of day for `hh-mm-ss`. That is the
datetime role's resolution-sets-the-unit rule transposed to the clock,
and it is what keeps every value an interpolation can reach inside the
column's one published form. Endpoints and rungs are written as TEXT
in that form, never as ordinals; because both forms are fixed-width
and zero-padded the two orders agree, so T3 is checkable without
arithmetic on the fields.

**A consequence of T1, stated rather than left to be discovered.** No
rung is ever `null`. `percentiles` admits a null rung because an
interpolated numeric rung can fall outside binary64; every rung here
is a value some cell held and every such value has a spelling in its
form, exactly as on `date_percentiles`.

#### Invariants

**T1 (one form, everywhere in the block).** Every published clock
value — `earliest`, `latest` and all eleven rungs — is written in the
form `clock_form` names, every field in two digits and in the ranges
that form's row gives.

**T2 (the ladder ends ARE the endpoints).** `clock_percentiles.min ==
earliest` and `clock_percentiles.max == latest`. Both pairs describe
the same two values, all four built from one ordering of the same
cells, and both ends are EXACT-OBSERVABLE. It is stated because the
generation rule rests on it: a generator pins its first and last ranks
to the endpoints and interpolates inside the ladder, so an untied pair
would let a document publish a ladder end below `earliest`, produce a
twin holding values earlier than the endpoint it published, and
re-describe with a different `earliest` and nothing said about it.
This is the analogue of D11, which pins the datetime ladder.

**T3 (non-decreasing).** Read in ladder order — `min`, `p01`, `p05`,
`p10`, `p25`, `p50`, `p75`, `p90`, `p95`, `p99`, `max` — the values
never decrease in seconds of day. Minutes of day and seconds of day
put the same values in the same order, and both agree with plain text
comparison of the written rungs, so an `hh-mm` ladder is checked by
this one rule and not by a second. Stated for T2's reason: the
generation rule rests on it. It is the reading L1 takes on this field.

**T4 (at least one cell parsed).** `n_unparsed < n_present`. This is
NOT implied by T5: `minimum_parse_rate` may be `0.0`, at which the
parse-line count is zero and T5 is vacuous, and T4 is then the only
rule keeping a cell for the endpoints and the ladder to be values of.
A column with no parsed cell cannot reach this role at all, so both
endpoints are always real values.

**T5 (the detection line, checkable afterwards).** `n_present -
n_unparsed` is at least the parse-line count of `n_present` — the
count `minimum_parse_rate` fixes, applied as a count — so a block
whose one form never cleared the detection line cannot conform.

**T-P (a producer obligation, stated because a loader cannot check
it).** Every published clock value is a value some cell of the source
column held. A loader holds one document and never the table.

**TU-P (the same, for the count).** `n_unparsed` is the count of
present cells no clock reading of C6-10 accepted, and **a loader
cannot recompute it.** Its own type bounds it below at zero; T4 and T5
bound it above — T5 the tighter of the two wherever the parse-line
count is at least one — and neither reaches the measurement: two
documents can satisfy every checkable rule of this section and
disagree about how much of the source read as a clock. The
measurement is the producer's obligation, checked by the
producer-side tests, and it is written down here so that no consumer
reads T4 and T5 as more than the bounds they are.

#### The model the ladder rests on, stated where the fact carries it

**C6-13.** The ladder reads the day as a LINE from `00:00` to
`23:59:59`, as every ladder reads its axis. A column whose values
cluster across midnight is therefore described as two edge clusters
with an empty middle, and a twin's interior interpolation fills that
middle. The rungs are exact values of real cells either way. The clock
face's circular reading is not modeled — exactly as a two-humped
numeric column's valley is not — and this is a bound of the ladder
model rather than a defect of this role.

#### Publication class, and the floor-free endpoints

**C6-14.** `time_of_day` is a RANGES-class role (section 6.10): no
spelling of the column appears in the block, and order statistics
computed from its values do. It carries no exception of its own — the
one named exception to the ranges class is `affixed_number`'s two
affix keys, and section 6.11 confines it there.

**The endpoints and the eleven rungs are exact values of real cells,
published FLOOR-FREE, and that is a disclosure rather than a
formality.** No `small_cell_floor` governs an endpoint or a rung: a
clock value one single cell held is published if it is the smallest,
the largest, or the cell an order statistic lands on. That is the
ratified ranges-class endpoint policy, the same one `datetime`,
`count` and `continuous` endpoints already have, and it newly reaches
columns that were free text and published no value at all. The
disclosure inventory prices it, and prices `clock_form` and
`n_unparsed` beside it: those two carry a shape and a count of the
table, but no value of it.

This role is not a nothing-publishing column, so its absent-cell
accounting is published under the floor exactly as N3 and N6 have it
for every column that is not.

#### The keys forbidden on this role

Every key not listed above is FORBIDDEN, universal or role-specific,
and a loader refuses one, naming the key and the column. The
forbidden-key matrix of section 6.11 carries the same listing for this
role and for the other twelve; three groups are named here because a
reader will expect them and their absence is a decision.

- **The other ten datetime keys.** `format`, `resolution`,
  `resolution_mix`, `time_precision`, `subsecond_digits`,
  `datetimes_read_at`, `earliest_utc_offset`, `latest_utc_offset`,
  `date_percentiles` and `utc_offsets` are `datetime`'s. `clock_form`
  answers the form question here, and a clock with no date carries no
  zone: an offset moves an instant, and this role publishes none.
- **Every quantitative key.** `percentiles`, `mean`, `std`, `skew`,
  `numeric_styles`, `fraction_widths`, `integer_valued` and the rest
  belong to `count`, `continuous` and `affixed_number`, as does the
  per-column `n_rows` echo, which Q1 confines to those three.
- **Every label key.** `levels`, `suppressed_levels`,
  `suppressed_rows` and `suppressed_level_counts` belong to the four
  labels-class roles, and `level_ceiling` to `categorical` alone. This
  role is in neither place.

`earliest`, `latest` and `n_unparsed` are the three names this role
shares with `datetime`. They ask the same question of a different
domain: here the endpoints are clock values in `clock_form` rather
than canonical instants at a recorded resolution, and `n_unparsed`
counts cells no CLOCK reading accepted rather than cells no date
format read.

#### The remarks it carries, and the one it does not

This role raises no note form of its own. The clock clause of the
competing-readings remark belongs to a column this rule DECLINED and
no later rule claimed; it is written on that column's block, never on
a `time_of_day` one. Like every column, a `time_of_day` block carries
a `detection_evidence` sentence built from the closed note grammar of
section 4.5, and carries any remark whose trigger its values reach.

#### What the twin owes

Rank 0 and the last rank are pinned to `earliest` and `latest`; the
interior ranks are interpolated by floor division between them in the
ordinal unit the published form itself sets, so every value written
has a canonical spelling in that one form. Every present cell is
written in `clock_form`, and the `n_unparsed` cells are written as
counted neutral stand-ins and counted on the surfaces that say what
was invented. The interpolation is always satisfiable: the two ends
are real values of a closed finite space and every interior value
floor-divides between them in that same unit.

Where the column publishes `n_distinct == n_present` the all-different
obligation binds on this role, and it binds through that same ordinal
mechanism — distinct ordinals, distinct spellings. This is not one of
the places the obligation cannot bind; what it has instead is a
capacity, because the ordinal space is finite, and that is the one
place a description of this role can be infeasible. The unparsed
stand-ins come from an unbounded text family and supply distinctness
of their own, so the shape no twin can hold is a description whose
distinct demand NET of them — `n_distinct - n_unparsed` — exceeds the
form's 1,440 or 86,400 spellings.

**Such a document is a VALID description and a loader accepts it.**
The conflict is decided at the generation-feasibility stage, which
runs after the loader and before any cell is built, and it is refused
there by name: it is the one refusal this role adds to the generation
method's closed list of generation refusals, which stood at four. The
message says the profile is valid, names the two published facts that
cannot both hold, and gives remediation that does not assume the
person still holds the table. Only that shape is refused. A
description whose own source met every published count, unparsed cells
included, is never refused by this rule.

---

<!-- r5c: long_tail_labels -->

### 6.14 `long_tail_labels`

A column holding more different values than a set of categories may
hold, some of which are nevertheless shared by enough rows to be
named. It is rule 11 of the order in section 5.2 — tested after every
other rule but the free-text fallback — so it claims only a column
every earlier rule declined.

**The detection rule, in full.** A column takes this role when all
three of the following hold.

1. **It is past the categorical ceiling.** Its `n_distinct_folded` —
   how many different folded identities it holds, counted after
   trimming and case folding — EXCEEDS the ceiling for a table of this
   many rows: the smaller of `categorical_ceiling` and the largest
   whole number of rows lying within `categorical_share` of `n_rows`,
   never below `categorical_floor`. That is the arithmetic section
   6.6.1 states, read against the settings of section 4.4 and the
   document's own `n_rows`.
2. **No earlier rule of section 5.2's order claimed it.** This
   includes the two rules tested immediately before it, on the terms
   their own sections state: a column whose cells read as clock text
   takes `time_of_day`, and a column whose cells read as numbers
   inside one affix pair takes `affixed_number`, even where a level of
   it would clear the line in 3.
3. **At least one of its folded levels covers
   `max(small_cell_floor, long_tail_minimum_level)` rows.** Both
   settings are keys of section 4.4, so the line is on the document's
   own face and no reader has to work out which of the two produced
   it.

**A column past the ceiling with no such level is not this role, and
there is no partial form of it.** It falls through to rule 12, takes
`free_text`, and its block is exactly what the section for `free_text`
specifies: no value of the column appears anywhere in it. That is what
keeps the free-text promise literally true rather than approximately
true. An all-different or nearly all-different column — names, street
addresses, typed comments — has no level covering eleven rows at any
floor, so it stays free text at EVERY floor, and the promise is
floor-invariant.

**Why the detection line is a `max`, and never falls below eleven.**
`long_tail_minimum_level` has exactly one permitted value in this
contract, the integer `11` (section 4.4), and a loader refuses any
other. At the default floor of `11` the two terms coincide. Raising
the floor raises the detection line with it, because publishing a
floor-clearing spelling is CONSTITUTIVE of this role: a level too
small to be published must not be the level that made a column
label-publishing, so a column that cannot publish one under the
recorded settings takes the next rule instead. In a table of fewer
than eleven rows no level can meet the line at all, and the role is
unreachable there. LOWERING the floor does not lower the line:
`small_cell_floor` may be set as low as `1`, and at a floor of `1`
every level a label column holds is published, but no column becomes a
long-tail column that was not one at eleven. **A settings combination
must not be able to widen which columns publish labels at all**, and
that is the whole of what the `max` buys. Which levels of an admitted
column are then SHOWN is the floor's question and moves with it;
whether the column is admitted is this line's question and does not.

**Added keys:** the four shared label keys of section 6.3 and nothing
else — `levels`, whose entries carry exactly `label`, `count`,
`variants` and `variants_withheld` under section 6.3.1;
`suppressed_levels`; `suppressed_rows`; and `suppressed_level_counts`.
Their JSON types and meanings are section 6.3's, identically, and
`variants` and `variants_withheld` are specified in full in section
7.4: the spellings of a published label that cleared the floor are
named in its `variants`, and those that did not are counted, unnamed,
in its `variants_withheld` — exactly as on any other label role.

**`level_ceiling` is FORBIDDEN on this role.** It is `categorical`'s
own key. Its invariant, G1, is that folded distinctness is at or under
the ceiling — and that is precisely what a long-tail column violates
by definition, since condition 1 of the detection rule puts it past
the ceiling. This format has no optional keys, so the key is ABSENT
from every block of this role rather than sometimes-present, and a
loader refuses a `long_tail_labels` block that carries it. The ceiling
the column passed is recorded instead in that column's
`detection_evidence` sentence, which is a built sentence of the closed
note grammar of section 4.5.1 like every other sentence of this
document.

**Which shared label invariants reach this role: all eight of them.**
B1 through B8 are stated in section 6.3.2 over a block that carries
`levels`, not over a list of roles, so each binds a `long_tail_labels`
block identically and none needs widening or restating here: B1
(published identity is normalized), B2 (level completeness), B3 (row
completeness), B4 (the suppressed multiset), B5 (the floor, both
ways), B6 (label order), B7 (labels are distinct) and B8 (levels may
be empty).

**What B8 comes to on this role, which is not what it comes to on the
others.** B8 admits `levels == []` for a block carrying levels. On
this role that case is unreachable: the detection line is at or above
`small_cell_floor`, so a level meeting it clears the floor and cannot
be one of the below-floor levels B5 bounds — it is published — and LT1
requires that there be one. **`levels` is never empty on a
`long_tail_labels` column.** This is a consequence of LT1 and B5
together and not a rule of its own, which is why it is stated rather
than numbered.

**Invariant LT1.** At least one entry of `levels` has a `count` of at
least `max(small_cell_floor, long_tail_minimum_level)`. This is the
detection rule's third condition made checkable against a parsed
document: both settings are in the document, and the level that met
the line is one the floor could not hold back.

**Invariant LT2.** `n_distinct_folded` exceeds the categorical ceiling
the settings imply — the same number the arithmetic of section 6.6.1
computes from `categorical_ceiling`, `categorical_share`,
`categorical_floor` and `n_rows`. A loader recomputes it and refuses a
block that does not clear it.

**The two roles are checked differently, and here is why.** On
`categorical` the ceiling is a published integer and G2 makes it
LOADER-ONLY, with no invariant tying the published value to the
arithmetic. Here the key is absent, so the settings and `n_rows` are
the only ceiling the document carries, and LT2 reads them directly.
Nothing is lost by the absence: the number was never a fact about the
column's values.

**Invariant G1L.** A `long_tail_labels` block carries no
`level_ceiling`. Stated as its own invariant, and not left to the
general rule that every key not listed for a role is forbidden on it
(section 6.11), because this is the one key a reader will expect on a
role defined by its relation to the ceiling.

**Publication class: LABELS.** Its published spellings are whole
values of the table, folded, with their counts, and only where at
least `small_cell_floor` rows share them — the same bound every label
of this format carries, with no exception of its own. Section 6.10 is
the authority on the class.

**A `long_tail_labels` column is never a nothing-publishing column.**
Its `structural_role` is always `data`: the declaration is decided at
rule 2 of section 5.2's order and this rule is tested at 11, so no
declared column can reach this role. So the rules of section 6.10 that
empty `missing_by_source`, zero the two absence counts and withhold
every sentinel candidate do not reach it, and its absent cells are
accounted for under the ordinary rules of sections 5.4 and 5.5. The
column it would otherwise have been — a free-text column — is a
nothing-publishing column, so that crossing is a disclosure of its
own, and it is priced as one in this document's disclosure inventory
rather than left to be discovered.

**Disposition, and what the twin owes.** `levels`,
`suppressed_levels`, `suppressed_rows` and `suppressed_level_counts`
are EXACT-OBSERVABLE, as section 6.3.2 states for every label role:
the twin writes each published label at exactly its count and invents
that many neutral labels at exactly the held-back sizes. The published
spellings go in byte for byte, under section 7.4's own
EXACT-OBSERVABLE rule for `variants` and `variants_withheld`, fold
collisions included. There is no generation rule of this role's own,
and a label column's twin invents neutral labels rather than language.
The twin of a long-tail column therefore carries its real repeated
labels and a counted invented tail, where the free-text twin of the
same column would carry neither.

**The disclosure this role adds, priced exactly.** Two facts, and the
second is narrower than its key looks.

- **The floor-cleared label spellings**, from columns that would
  otherwise publish no value of the table at all. Bounded by the floor
  exactly as every label of this format is: nothing covering fewer
  than `small_cell_floor` rows is named. What is new is WHICH columns
  publish labels — a genuine prose column with eleven identical cells
  names that repeated sentence as a level. Two widenings of that
  sentence's own price are stated rather than left to be discovered:
  the eleven rows are ROWS and not people — the grain is undescribed,
  so eleven repeated cells may be one person's repeated records, the
  caveat this project states for every floor-guarded fact and which
  now guards sentences too; and the profiler's summary names every
  column whose labels will be visible BEFORE anything is written,
  long-tail columns included.
- **The sizes of the BELOW-FLOOR folded identities**, through
  `suppressed_level_counts`. A free-text column already publishes a
  repetition map over its raw present values, so anonymous group sizes
  are not themselves new. That map groups RAW spellings; this multiset
  groups FOLDED identities. **The additional fact is therefore exactly
  which unnamed spellings share a trim-and-case identity — counts
  only, never a spelling** — a fact about below-floor cells the
  repetition map does not carry. It is stated at this width because a
  reader who prices only the first bullet would be approving something
  this role does not do.

**Document size, stated rather than found later.**
`suppressed_level_counts` holds one integer per below-floor level, and
on this role there may be many of them: their number is bounded by
nothing but `n_rows`. No cap is imposed, because a cap would contract
a domain this format has promised, and B4's equalities would then be
unwritable.

---

<!-- a7a_72: multiplicity parity and the relationship manifest -->

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

---

<!-- a7b1: label spelling variants -->

### 7.4 Label spelling variants (owner decisions 9 and 11)

This machinery is shared by the four label-publishing roles —
`constant`, `binary`, `categorical` and `long_tail_labels` — and is
stated once, here, for all four.

#### 7.4.1 What a variant is, and what publishing it fixes

**C6-93 (definition).** A **variant** of a published label is one exact
source spelling that present rows of the column wrote that label with:
the characters the file held, before any trimming and before any fold.
A published `label` is a folded identity (B1); a variant is one of the
raw forms standing behind it.

The producer trims edge spacing and applies a Unicode case fold before
publishing a label. A column holding `A`, `a`, `B`, `b` therefore
publishes two labels of two rows each, and a twin built from that
record alone would write `a, a, b, b` — repeating where the real column
never did, and breaking the all-different obligation for every label
role, not only for identifiers. The implementer recommended accepting
the repeats and disclosing them; **the owner directed the opposite** —
the description records the variants so the twin can keep the values
distinct.

#### 7.4.2 The wire shape

**C6-94 (where the two keys stand).** Both keys are REQUIRED on every
entry of `levels` (6.3.1) on the four label roles, and FORBIDDEN
everywhere else: on every non-label role, and on a suppressed level,
which has no entry to hold them (W1). Both are written even when
empty, because this format has no optional keys and a key that appears
only sometimes is a key a consumer comes to guess about.

**`variants`** — an object mapping an EXACT source spelling to how many
present rows wrote the label that way.

- Keys are the spelling exactly as the file wrote it, character for
  character, before trimming and before the fold.
- Values are integers at least `small_cell_floor` (W5).
- `{}` is valid: it is a published label every one of whose spellings
  fell below the floor. The label still stands, because its own `count`
  cleared the floor, and `variants_withheld` then covers all its rows.
- The keys are the TABLE's own text and carry no first-party meaning:
  N5 states that for the two maps the table keys, `missing_by_source`
  and `levels[].variants`.

**`variants_withheld`** — a multiplicity map in the form 5.3 fixes
(C6-90): how many different spellings of this label covered one row,
two rows, and so on, for the spellings the floor held back. It names
none of them. Its keys are bounded here to 1 through
`small_cell_floor - 1` (W5), and `{}` is valid — a published label with
no held-back spelling. At a floor of one that range is empty, so every
map of this key is `{}`; `variants_withheld` is one of the fields S13
names, and S13 is checked before any column block is read.

Worked example — floor 11, one entry of a `categorical` column:

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
spellings — which the description does not name — were written by one
row each. 22 + 15 + 3 × 1 = 40, the entry's own `count`.

#### 7.4.3 Stored exactly, escaped only where it is shown

**C6-95 (the storage rule).** A variant key is stored character for
character as the table wrote it. The display boundary applies at the
moment of SHOWING and never to what is stored: every surface that puts
such a key in front of a person — the plain-language summary, the
generation report, the quality report, any command output — escapes it
there and never stores the result. A surface that interpolates a
stored key without the boundary is a defect in the implementation, not
in this contract. `missing_by_source` keys are stored the same way and
for the same reason (5.4).

**The reason.** A variant is a generation input, not a fact for a
person to read: the twin writes it into a CSV cell and a re-reader
must read it back byte for byte, and a key something has to read back
is a key that must survive being written down. Escaping it at rest
would file the count under a spelling no row ever wrote, and the
twin's cells would differ from the table's in exactly the characters
this key exists to preserve.

**W-P (a producer obligation, stated because a loader cannot check
it).** A variant key is the source spelling character for character. A
loader holds no table and can check only that a key folds to its
parent (W2), so this is verified on the producer's side, by a test
that profiles two tables differing only in a spelling the display
boundary would merge and requires the two descriptions to differ.

#### 7.4.4 Why the withheld map is needed

Without it, a parent of eleven rows cannot be told apart from eleven
one-off spellings versus two spellings occurring ten times and once,
and the twin would not know how many spellings to invent. It is the
same class of fact as the identifier repetition multiset: counts about
unnamed groups.

#### 7.4.5 The disclosure delta, stated accurately

The fold is a Unicode case fold applied after trimming, not merely a
capitalization change. Recording variants therefore publishes every
exact spelling that differs BEFORE that fold — which includes pairs a
reader may not expect, such as `ß` and `SS` folding together. The owner
confirmed this broader reading.

The delta is bounded to the spelling forms of labels the description
ALREADY publishes, and no variant crosses a line that a whole label
would not, because each variant is governed by the same floor as any
published label. The fact is named in `SECURITY.md`, in the profiler
summary and in the generation report, and the disclosure battery scans
the COMPLETE profile and profiler summary as well as the twin and the
report, because the fact appears first in the profile (residual
R-P2-11).

**A correction that travels with these keys.** Any text saying that
case and edge spacing are not preserved is false of this format, and
no surface may print it. Case and edge spacing ARE preserved wherever
the variants are visible, and fall back to the normalized spelling
only beneath the floor.

#### 7.4.6 Publication class and disposition

**C6-96 (publication class).** A named variant is a floor-governed
publication of the labels class: a spelling of a label the description
already names, held to the same line as the label itself.
`variants_withheld` is the other class — counts about unnamed groups,
which no floor suppresses, the same class as `suppressed_level_counts`
and the repetition multiset. What it discloses, stated rather than
waved away, is the group SIZES: a map containing `"1": 3` says three
spellings of this label were each written by exactly one row, without
saying what any of them was.

**Disposition.** `variants` and `variants_withheld` are both
EXACT-OBSERVABLE: the twin writes each named spelling at exactly its
count and invents exactly that many neutral spellings of the parent at
exactly the held-back sizes, and both are recounted from the written
CSV. What these two keys do to raw `n_distinct` on the label roles is
that key's own row in the disposition matrix (section 9), not a rule
of this section.

#### 7.4.7 The invariants — W

Seven, and all seven are decidable from one parsed document.

**C6-114 (what the seven quantify over).** W1 through W7 are stated
over a PUBLISHED LEVEL ENTRY — one member of a block's `levels`
(section 6.3.1) — and over the two spelling maps that entry holds.
None of them names a publishing role. Only W1 reaches outside the
entry, and only to its complement: the two keys are forbidden on every
block that publishes no `levels`. So every block that publishes
`levels` binds all seven identically, and not one of them is restated,
widened or excepted for any role — `long_tail_labels` included, which
publishes `levels` under the shared label shape of section 6.3 and
therefore takes the seven exactly as they stand. The floor they read is
`small_cell_floor`, the setting of section 4.4, so each binds at
whatever value the document records.

Seven, and all seven are decidable from one parsed document.

**Invariant W1 (parent binding).** Every variant is bound to one
already-visible parent label: the two keys are forbidden on a withheld
parent, which has no entry to carry them, and on every non-label role.

**Invariant W2 (each variant folds to its parent).** Trimming a
variant key and case-folding it yields exactly the entry's `label`. A
key that folds to anything else is a refusal: it would be a spelling
of some other label filed under this one.

**Invariant W3 (no variant exceeds its parent).** Every value of
`variants` is at most the entry's `count`.

**Invariant W4 (the counts close exactly).**
`sum(variants.values()) + sum(key × value over variants_withheld)
== count`. Nothing about a published label's rows is unaccounted for.
This is M2 bound to the entry.

**Invariant W5 (the floor governs a variant like any published
label).** Every value of `variants` is at least `small_cell_floor`.
Every key of `variants_withheld`, read as a number, is between 1 and
`small_cell_floor - 1`.

**Invariant W6 (variant keys are distinct).** They are object keys, so
this is a property of the JSON, but it is stated because two spellings
that differ only by a character the canonical form does not
distinguish would be one key and must not be produced as two.

**Invariant W7 (at least one spelling exists).** `variants` and
`variants_withheld` are never BOTH empty on one entry, because a
published label covers at least `small_cell_floor` rows and every row
was written some way.

[ASSEMBLY: 6.3.1 points here for W1–W7 and this is their home; the
checkable list of §8.8 restates them, which is that list's stated
purpose. Add `W-P` to that list's producer rows.]

---

<!-- a7c: numeric styles and fraction widths -->

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

---

<!-- a7d: the twin reproduces the recorded hole spellings -->

### 7.7 The twin reproduces the recorded hole spellings

Every version of this format before this one wrote every absent cell
of a twin as an empty field, and reproduced no absent-value spelling
anywhere. That is no longer true of the file this version's generator
produces, and this part states what replaces it. It is one rule, in
one place, because a twin's absent cells are written by one
construction whatever role the column took.

**C6-115 (the write rule).** A version 6 twin writes, per column:

1. each `missing_by_source` spelling at exactly its published count —
   EXCEPT a spelling a JUDGED PASS put there, which stays blank;
2. every other absent cell empty: the blank count, the withheld
   remainder, and every judged-pass-sourced cell;
3. all of them placed by the same single permutation that places
   everything else, with spellings assigned to absent slots in a fixed
   sorted order before the permutation runs.

A judged pass is either of the two this version has: the stand-in
number pass, and the calendar placeholder pass of 6.6.4.

**C6-116 (why judged-pass cells stay blank).** A reproduced TEXT
spelling is read back as absence by a fixed rule of the description
alone — it is a member of the published vocabulary (5.4.1), or a value
the person named with `--missing-value`, and either way the reading
does not depend on the twin's own values. A stand-in NUMBER is that
rule's named exclusion, and a CALENDAR PLACEHOLDER is excluded for
exactly the same reason: the absence reading of both runs through the
producer's outlier-and-share judgement over the measured file's own
values, which a twin's generated distribution is not guaranteed to
re-fire.

Reproducing those cells would make the twin's own measurement
contingent on a re-judgement; leaving them blank keeps every
reproduced cell's reading deterministic. **Nothing the description
records is lost by it**: the twin's report names, per column, the
stand-in cells, the placeholder cells and the below-floor spellings
that were not reproduced.

**C6-117 (declaration wins, on every pass).** Where a person named a
value with `--keep-value`, that value is data and no judged pass may
read it as a hole — the numeric pass, the calendar pass and the
published vocabulary alike. A cell rescued that way is a PRESENT cell:
its spelling reaches `missing_by_source` for no column, and the twin
writes it wherever its column's publication rules put a value.

**C6-118 (the collision rule, with no runtime escape).** No PRESENT
cell of a twin may wear a spelling the description publishes as a hole
source for its column. If it could, a twin would hold a cell that
reads as absent to the rule of C6-116 while standing where a value
belongs, and the file would describe itself two ways.

The generation method carries the written proof that no construction
is ever forced onto such a spelling. **A shape outside that proof is a
defect of the method, found at review** — it is never a deviation
printed at run time. That distinction is the whole of this clause: a
rule a generator may break and then report is not a rule, and this one
holds by construction or the method is wrong.

**The SUM identity this creates.** Because the construction writes
several pools of absent cells as empty fields, no per-field equality
holds between the twin's blank cells and any single published count.
What holds is a sum: the twin's recounted blank absent cells equal
`n_missing_blank` plus `n_missing_withheld` plus the judged-pass-
sourced count, over BOTH judged passes. An identity naming only the
stand-in pass would be false by construction on any column carrying
judged calendar placeholders, and a validator checking it would report
a failure against a correct twin — which is worse than no check,
because it teaches its reader to stop believing the report.

---

<!-- a8a: every invariant, part one -->

## 8. Every invariant, in one checkable list — part one

This section states every invariant of this format as one list a loader
or a test can walk. Each row is true or false with no interpretation
left, and the identifiers are the ones the rest of the document uses.

**Most rows restate a rule stated beside the thing it constrains**, and
a reader who has met the rule already will meet it again here. Four
families are stated ONLY here, because their subject is spread across
several sections and a normative home in any one of them would be a
home the others reached by inference: the cell census (`X`), the
multiplicity-map bounds (`M`), the style and fraction census (`P`), and
the note-grammar checks (`NG`). For those, this list is the rule and
not an echo of one.

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

---

<!-- a8b1: every invariant: the value-bearing families -->

### The numeric, unrepresentable, datetime and verdict families

The third column is part one's, with its four values — `yes`,
`producer`, `reading`, `contract` — and is not redefined here. Where a
rule is half a predicate over a parsed document and half a fact about
the source no loader can recompute, the row states the half a loader
decides and names the other half beside it.

Every row of the Q family is read on `affixed_number` over the CORES,
under AF7's substitution, which names the counts it moves and writes
each reading out; `n_present` and `n_rows` are NOT substituted there,
as those keys' own published meanings have them.

#### The Q family — `count`, `continuous`, and the cores of `affixed_number`

| id | statement | loader? |
|---|---|---|
| Q1 | the per-column `n_rows` equals the document's `n_rows`; the key appears ONLY on `count`, `continuous` and `affixed_number`, and is forbidden on every other role | yes |
| Q2 | `n_used_in_statistics == n_numeric`, and `n_left_out_of_statistics == n_present - n_numeric` | yes |
| Q3 | `n_numeric >= 1` | yes |
| Q4 | `std` is `null` exactly when `n_used_in_statistics < 2` or `std_unrepresentable` is true; the two are different facts, so a reader never guesses which a `null` is | yes |
| Q5 | `skew` is `null` when `n_used_in_statistics < 3`, and when every parsed value is identical; it is a number otherwise | yes |
| Q6 | where every parsed value is identical and `n_used_in_statistics >= 2`, `std` is `0.0` and `std_unrepresentable` is false | yes |
| Q7 | where every parsed value is identical the exact mean is that value and this format holds it, so a `null` there is refused; `mean` is `null` only when the exact mean is not a finite binary64 value, and that general clause refuses no document, a loader holding no values to recompute a mean from | yes, in the identical-value direction |
| Q8 | the twin's integer rule is routed by the published `integer_valued`, never by whether the role name is `count`; a `continuous` column may publish `integer_valued: true` and its twin cells are whole numbers | reading — it binds the consumer, and no document is refused for it |
| Q9 | `numeric_share == (n_numeric + n_out_of_range + n_contradictory) / n_present`, a share of the present cells, and `0.0` where `n_present` is 0 — which Q3 forbids on these roles | yes |
| Q10 | `n_negative_unrepresentable <= n_out_of_range` and `n_negative_unrepresentable <= n_negative` | yes |
| Q11 | `n_zero <= n_numeric` | yes |

**Q5, Q6 and Q7 all turn on "every parsed value is identical".** The
numeric roles fix that test where they state those three rules —
`percentiles.min == percentiles.max`, with a `null` endpoint under L3
reading NOT identical, so a `null` `skew` at `n_used_in_statistics >=
3` is refused there as on any column whose endpoints differ. It is the
only route to these three rows from a parsed document, and a reader who
supplied a different test would refuse different files.

#### The U family — `numeric_unrepresentable`

| id | statement | loader? |
|---|---|---|
| U1 | `n_whole + n_fraction + n_whole_unknown == n_present` | yes |
| U2 | `n_positive + n_negative + n_sign_unknown == n_present` | yes |
| U3 | M1 and M2 hold of `n_distinct_by_occurrences`: its values sum to `n_distinct`, and its keys weighted by its values sum to `n_present` | yes |
| U4 | the role is a nothing-publishing column, so `missing_by_source` is `{}`, `n_missing_blank` and `n_missing_withheld` are `0`, and every `sentinel_verdicts` entry has `candidate == "(withheld)"` (N3, V2) | yes |
| U5 | `min_length <= max_length` | yes |
| U-P | `min_length` and `max_length` are measured over the NUMERIC-LOOKING cells only, each a count of characters of the cell's text as the file spells it; U5 bounds the two against each other and reaches no further | producer |

**U1 and U2 are margins over the WHOLE present population, ordinary
text included.** The detection line is a count, so this role tolerates
present cells that are not numeric notation at all. Such a cell settles
neither question and is counted in `n_whole_unknown` and in
`n_sign_unknown`, as is notation that conflicts with itself, and that
tie is what closes both sums on `n_present` rather than on any narrower
count. The role's own section states the tie and the construction table
it answers to.

#### The D family — `datetime`

| id | statement | loader? |
|---|---|---|
| D1 | the pair (`format`, `resolution`) is one row of the format table, and the binding is exact and TOTAL over all ELEVEN members: `iso-date`, `month-first-date`, `day-first-date`, `compact-date` and `slashed-iso-date` take `date`; `iso-month` takes `month`; `year-quarter` takes `quarter`; `iso-datetime`, `iso-mixed`, `month-first-datetime` and `day-first-datetime` take `datetime` | yes |
| D2 | `sum(utc_offsets.values()) == n_present - n_unparsed` — only cells that parsed have an offset | yes |
| D3 | every key of `utc_offsets` other than `(withheld)` maps to a count at least the floor, and `(withheld)` appears only when the pooled remainder is non-zero | yes |
| D4 | an endpoint offset field naming a real offset names a key of `utc_offsets`: a value published in one field of a block that another field of the same block promises to withhold is a contradiction this format forbids | yes, in that direction — that `(none)` marks an endpoint cell wearing no offset, and `(withheld)` an offset the map is holding back, is *producer* |
| D5 | `datetimes_read_at` is `local` when the whole column shares one UTC offset, `utc` when two or more appear | yes, in the direction a document supports — two or more non-`(withheld)` keys in `utc_offsets` require `utc`; where the map is fully withheld either value is accepted, because it reads the same whether one offset wrote the column or ten — EXCEPT under a format whose reader takes no offset at all (`month-first-datetime`, `day-first-datetime`), where `local` is the only value any column could have held (review item P4-DATE5-F1) |
| D6 | the pair (`resolution`, `time_precision`) is one row of this map, TOTAL over the FOUR resolutions and the SIX precisions, so all twenty-four pairs are decided: `date` permits `date`; `datetime` permits `minute`, `second` and `subsecond`; `quarter` permits `quarter`; `month` permits `month` — with ONE format-family narrowing inside the datetime row: `month-first-datetime` and `day-first-datetime` read a clock in the `time_of_day` role's two forms, which carry no fraction, so those two members permit `minute` and `second` and not `subsecond` | yes |
| D7 | `subsecond_digits > 0` implies `time_precision == "subsecond"`, and `time_precision == "subsecond"` implies `subsecond_digits > 0` | yes |
| D8 | `n_unparsed < n_present` — the checkable form of "the ladder covers the parsed cells", so both endpoints are always real values | yes |
| D9 | every key of `utc_offsets`, and both endpoint offset fields, are `(none)` or `(withheld)` unless `resolution` is `datetime` AND `format` is an ISO member; under D1 that reaches every format member but TWO — only `iso-datetime` and `iso-mixed` may carry an offset at all, because the two slashed stamp members take a clock in the `time_of_day` role's two forms and no offset (review item P4-DATE5-F4) | yes |
| D10 | where `resolution` is `datetime`, the seconds field of `earliest` and of `latest` is `00` when `time_precision` is `minute`, and is not `60` when `datetimes_read_at` is `utc`; and where `resolution` is `datetime` and `datetimes_read_at` is `utc`, each endpoint moved onto the clock its own endpoint offset names stays inside the years `0001` to `9999` | yes — the loader holds all three fields it needs: the endpoint, its offset, the clock |
| D11 | `date_percentiles.min == earliest` and `date_percentiles.max == latest` | yes |

#### The V family — `sentinel_verdicts`, wherever a block carries one

| id | statement | loader? |
|---|---|---|
| V1 | every entry has `n_occurrences` at least the floor. A candidate below it is not listed at all: it is counted, unnamed, in `n_sentinel_candidates_unpublished`, the one field of this format that records a thing held back in its NAME rather than under the `(withheld)` word, and S13 puts that count at zero at a floor of one | yes |
| V2 | `candidate` is `(withheld)` on exactly the columns where `missing_by_source` is empty for N3's reason — a column whose publication class permits no value of the table anywhere in its block. Naming a candidate there would publish a value out of a column that publishes none, and on every other column no candidate reads `(withheld)` | yes |
| V3 | `verdict` is `read_as_missing` only when `reason` is `outlier_and_frequent`; the other four reasons all keep the candidate as an ordinary number of the column | yes |
| V4 | entries appear in three groups, in this order, and the rule is TOTAL over the candidates this format permits: (1) NUMBERS, ascending by the number; (2) CALENDAR DAY SPELLINGS, ascending by the candidate text; (3) `(withheld)`, ordered by `n_occurrences`, then `verdict`, then `reason`, so no position can say which of two withheld candidates is the smaller. The datetime section states the rule entire, with the reason it is written total rather than for the mixed case alone | yes |

---

<!-- a8b2: every invariant: the new roles and the producer obligations -->

## 8. Every invariant, in one checkable list — part two-B

Every row below is decidable by a loader holding ONE PARSED DOCUMENT,
except the two marked *reading*, which fix a MEANING and leave nothing
to refuse. Producer rows stand once, in the last table; N7 and K5 are
part one's (8.3, 8.4).

### 8.x The style census and the fraction widths — P

| id | statement |
|---|---|
| P1 | the values of `numeric_styles` sum to `n_numeric`, and to `n_core_numeric` on `affixed_number` (AF7); out-of-range and contradictory cells are NOT counted, being written in forms no style expresses |
| P2 | every value under a style NAME is at least `small_cell_floor`; `(withheld)` is exempt, present only when the pooled remainder is at least 1, and may be anything from 1 up |
| P3 | `numeric_styles` is never `{}` on the three roles carrying it |
| P4 | *reading*: `integer_valued` and the census are independent — `5.0` is whole, written with a point; a loader checks neither against the other |
| P5 | *F*, the sum of ALL `fraction_widths` values including `(withheld)`, obeys the case below that `numeric_styles` selects; an empty census has *F* = 0 throughout |
| P6 | every NAMED width's count is at or above `small_cell_floor` |
| P7 | a width key is present only if its count is nonzero, so a present `(withheld)` value is at least 1 and *F* is zero exactly where the census is empty |

- **P5.a — a `decimal` key is published.** *F* equals its value.
- **P5.b — no `decimal` and no `(withheld)` key.** No decimal cell
  exists: the census is `{}` and *F* is zero.
- **P5.c — no `decimal` key but a `(withheld)` key.** The decimal
  count, if any, was pooled, so the census is `{}` or exactly
  `{"(withheld)": F}` — no NAMED width key, P6 putting one at the
  floor and condition 2 putting *F* below it. Writing *W* for
  `numeric_styles["(withheld)"]`, **FOUR conditions bind**, any
  breach refusing the document:

  1. *F* is at least 1 **wherever the census is non-empty**, an empty
     census being what a column with no decimal cell writes;
  2. *F* is strictly BELOW `small_cell_floor`, a style being pooled
     only when its own count falls below it;
  3. *F* is at most *W*, the pooled decimal cells being a subset of
     the pool;
  4. *F* ≥ *W* − 5 × (`small_cell_floor` − 1): six styles exist, so at
     most five share the pool with decimal, each holding at most
     `small_cell_floor` − 1 cells. Vacuous where that is ≤ 0.

**Condition 4 decides the EMPTY census too, so no fifth is needed**:
at *F* = 0 it reads *W* ≤ 5 × (`small_cell_floor` − 1).

### 8.x The affixed-number role — AF

| id | statement |
|---|---|
| AF1 | `affix_prefix` and `affix_suffix` are not both the empty string |
| AF2 | `small_cell_floor <= n_affixed <= n_present` |
| AF3 | `n_affixed` is at least the parse-line count of `n_present`, applied as a COUNT, never a compared share |
| AF4 | `n_core_numeric + n_core_out_of_range + n_core_contradictory + n_core_not_numeric == n_affixed`, beside X2, not in place of it |
| AF5 | `n_core_numeric >= 1`, Q3 read over the cores |
| AF6 | *reading*: `integer_valued` is a fact about the CORES and is what a consumer routes on, never the role name |
| AF7 | every quantitative key obeys the invariant stated for it on `count` and `continuous`, read over the CORES under that role's substitution, `n_present` and `n_rows` untouched |
| AF-R | every `affixed_number` column bears the affixed-column remark, without condition, at arity 3, under NG11 and NG12 |

### 8.x The clock role — T

| id | statement |
|---|---|
| T1 | every published clock value — `earliest`, `latest`, the eleven rungs — is written in the form `clock_form` names, two digits a field, in its ranges |
| T2 | `clock_percentiles.min == earliest` and `.max == latest`; untied, a twin pinned to the ladder can hold values earlier than its published endpoint |
| T3 | read in ladder order the rungs never decrease in seconds of day, which for these fixed-width forms agrees with text comparison |
| T4 | `n_unparsed < n_present`. NOT implied by T5: at `minimum_parse_rate` `0.0` the parse line is zero and T5 vacuous, T4 alone keeping a cell for the endpoints |
| T5 | `n_present - n_unparsed` is at least the parse-line count of `n_present`, applied as a count |

### 8.x The long-tail label role — LT

| id | statement |
|---|---|
| LT1 | at least one entry of `levels` has a `count` of at least `max(small_cell_floor, long_tail_minimum_level)` |
| LT2 | `n_distinct_folded` exceeds the ceiling the settings imply, recomputed from `categorical_ceiling`, `categorical_share`, `categorical_floor` and `n_rows` |
| G1L | a `long_tail_labels` block has no `level_ceiling` |

### 8.x The resolution mix — RM

| id | statement |
|---|---|
| RM1 | `resolution_mix` keys are exactly what the column's `format` permits: on a single-format column that member, on `iso-mixed` exactly `iso-date` and `iso-datetime` |
| RM2 | values sum to `n_present - n_unparsed`; on `iso-mixed`, the joint reading being the chosen format, `n_unparsed` counts cells reading under neither member |

### 8.x The note grammar — NG

Read over the column each note's `column` names. NG1–NG5 bind the
slashed-date remark, *n* being that column's `n_present` and *D*, *M*,
*X*, *Y* its arguments 1 to 4: cells day-first parsed, cells
month-first parsed, cells only day-first parsed, cells only
month-first parsed.

| id | statement |
|---|---|
| NG1 | *D*, *M*, *X* and *Y* are whole numbers of zero or more |
| NG2 | the both-readings identity: *D* − *X* = *M* − *Y* |
| NG3 | *X* ≤ *D*; given NG2 this gives *Y* ≤ *M* |
| NG4 | *D* + *Y* ≤ *n*, equivalently *M* + *X* ≤ *n*: the UNION is bounded, never each count on its own |
| NG5 | argument 5 is `day-first` where *D* ≥ *M*, `month-first` where *M* > *D* |
| NG6 | on `remark_no_reading_fits`: argument 1 is a `said_written_as_numbers` fragment whose own arguments 1 and 2 are the column's `n_numeric` + `n_out_of_range` + `n_contradictory` and its `n_present` |
| NG7 | on its recoverable-distribution clause, *C* being argument 9 and *N* that fragment's own argument 1: where *C* ≠ 0, *N* + *C* ≤ `n_present`, i.e. *C* ≤ `n_not_numeric` |
| NG8 | where *C* ≠ 0: *C* ≥ `settings.small_cell_floor` |
| NG9 | where *C* ≠ 0: *N* is at least the parse-line count of (`n_present` − *C*) |
| NG10 | on a `free_text` column bearing this remark, *N* is below the parse-line count of `n_present`; **scoped to `free_text`, never wider** |
| NG11 | on `remark_affixed_numbers_may_be_codes`: argument 3 equals the named block's `n_affixed` |
| NG12 | argument 1 is character-for-character that block's `affix_prefix` and argument 2 its `affix_suffix`, AT THOSE POSITIONS, not merely as members of the pair |
| NG13 | on `remark_a_label_is_a_built_in_stand_in`: argument 1 is 1, 2 or 3 |
| NG14 | for every form: one of the 41 the note grammar enumerates |
| NG15 | the argument count equals that form's arity |
| NG16 | every argument is of one of the four argument classes |
| NG17 | re-rendering the form with those arguments writes the leaf's text character for character |
| NG18 | each package word stands only at a position its class admits: a `format` member only at `evidence_dates` argument 3 or `said_read_as_dates` argument 2, `day-first` and `month-first` only at the slashed-date remark's argument 5 |

### 8.x Every producer obligation, in one table

Each row is true of a PRODUCER, never of a document: a loader holds one
document, never the table it describes.

| id | statement | why no loader can decide it |
|---|---|---|
| AF-P | at least the parse-line count of present cells wore the published pair; the pair is the one they wore; each core is that cell's longest-then-leftmost parsing substring; the four core-class counts are the classifier's verdicts over those cores | two documents satisfy AF1–AF7 and disagree about the source; the split rule is a total order, so ONE table gives ONE answer |
| T-P | every published clock value, endpoints and rungs, is a value some cell of the source column held | T1 checks spelling and T2 and T3 order, never provenance |
| TU-P | `n_unparsed` on `time_of_day` is the count of present cells no clock reading accepted | its type bounds it below and T4 and T5 above; neither reaches the measurement |
| U-P | `min_length` and `max_length` on `numeric_unrepresentable` are measured over the NUMERIC-LOOKING cells only, each a character count of the cell's text | a straggler's length is a fact about text and as a bound would read as magnitude; U5 reaches no further |
| DF-P | both slashed readings were counted, the reading used parsed strictly more cells, and the declaration decided only a tie | the winning `format` is recorded, the losing count is not |
| DF-R | where the option was given and a slashed reading was in play, the column bears that remark exactly once, over the EVIDENCE, not the winner | whether a reading was in play is a fact about the table |
| CP-P | a published calendar-placeholder verdict is the one the outlier-and-share rule reached over the source's written days | the rule ran over a table a loader never holds |
| RM-P | the `resolution_mix` counts are the counts the source's own cells wore | a 40/60 and a 50/50 split of a hundred cells both satisfy RM1 and RM2 |
| FW-P | every `fraction_widths` count is the count of source cells written at that fraction width | P5 bounds the total and P6 and P7 the entries; none checks the census's SHAPE |
| NG9-P | where the recoverable-distribution arithmetic holds, that clause IS written | a document with no clause holds no *C*, so the converse is untestable |
| NG13-P | the column publishes a level whose spelling is the stand-in argument 1 names | the argument names a stand-in by number and the level is published folded |

One producer obligation has no identifier: the four sentence leaves
are each built by a first-party constructor from one grammar form, so
a note interpolating a source spelling fails at CONSTRUCTION.

---

<!-- a9: the disposition matrix -->

## 9. The disposition matrix

Taken from plan section P2-D6. Every published fact carries exactly
ONE of the six dispositions section 2.2 fixes, and this section says
which, fact by fact, and what each promises about the twin. A
completeness assertion enumerates every key the producer emits for
every one of the thirteen roles, plus every top-level key, and FAILS
when any key has no disposition here. It must pass against this matrix
as written; it may not acquire exceptions during implementation.

**Every disposition below is an obligation over descriptions whose
published facts CAN all hold at once**, which is every description the
producer writes (review items P2-C1-F8, P2-C5-F4). This contract's
invariants do not tie every pair of fields together, and deliberately
so — a loader that had to decide whether a whole SET of counts was
jointly satisfiable would be doing the generator's work at the wrong
end of the run — so a strict loader accepts a small number of
hand-made documents no twin can satisfy. A one-character declared
identifier published as whole numbers with `n_all_digits` below
`n_present` is one: no single character is both a whole number and
outside the figures.

**Such a document is REFUSED, and a twin is never written from it**
(plan P2-D6, feasibility rule 5). The generation-feasibility stage
runs after the loader and before any cell is built, and where the
published facts are PROVED to have no joint answer it refuses
GENERATION rather than the description: the message says the profile
is valid, names the two facts that cannot both hold, and gives
remediation that does not assume the person still holds the table.
`docs/spec/generation-method-v1.md` G12 carries the closed list of
those refusals. Meeting what can be met, recounting the fact and
naming it in the report would turn a description the ratified plan
settles into a twin somebody receives with no signal that anything was
wrong, and the plan reserves the report line for facts a rule CAN
meet.

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
| `columns` | STRUCTURAL | the four container rules: S1, S2, S3, S4 |
| `source` | STRUCTURAL | membership: its five keys, section 4.3 |
| `n_rows` (document) | EXACT-OBSERVABLE | the twin has this many data rows |
| `n_columns` | EXACT-OBSERVABLE | the twin has this many columns |
| `profile_version` | LOADER-ONLY | the integer 6 |
| `settings` | LOADER-ONLY | whole subtree: all seventeen keys, `day_first` and `long_tail_minimum_level` among them, and both declaration records with all five of their keys — `built_in_dates` included |
| `created_with` | LOADER-ONLY | |
| `publication_notes` | LOADER-ONLY | whole subtree |
| `relationships` | LOADER-ONLY | whole subtree; eight `null` slots |
| `source.encoding` | REPORT-ONLY | the twin is always UTF-8 with LF (residual R-P2-5) |
| `source.used_fallback_encoding` | REPORT-ONLY | |
| `source.header_source` | EXACT-CONTROL | decides whether a header row is written at all |
| `source.header_by_convention` | REPORT-ONLY, required sentence | section 4.3 |
| `source.header_evidence` | REPORT-ONLY, required sentence | section 4.3 |

`built_in_dates` is named in the `settings` row rather than left to be
inferred: it is a function of the command line alone, it carries no
cell, no column and no count of the table, and it is LOADER-ONLY on
exactly the terms `built_in_numbers` and `built_in_texts` are.

### 9.2 Universal per-column fields

These cover all twenty-two universal keys.

| field | disposition |
|---|---|
| `n_present`, `n_missing` | EXACT-OBSERVABLE |
| `name` | EXACT-OBSERVABLE when a header is written, else EXACT-CONTROL |
| `position`, `role`, `statistical_type`, `quality_state`, `structural_role` | EXACT-CONTROL |
| `missing_by_source` | EXACT-OBSERVABLE, recounted per spelling from the written twin — EXCEPT a key a JUDGED PASS put there, which the twin writes empty and which is REPORT-ONLY for that key, the achieved zero named beside the published count |
| `missing_by_class` | REPORT-ONLY, all six classes — the classes are not recoverable from bytes |
| `n_missing_blank`, `n_missing_withheld` | REPORT-ONLY, bound by the sum identity: the twin's recounted blank absent cells equal `n_missing_blank` plus `n_missing_withheld` plus the judged-pass-sourced cells. A per-field equality would be false by construction, because the twin writes all three pools blank |
| `n_numeric`, `n_not_numeric`, `n_out_of_range`, `n_contradictory` | EXACT-OBSERVABLE by class-preserving construction, over the CELLS on every role |
| `n_sentinel_candidates_unpublished`, `sentinel_verdicts`, `detection_evidence`, `remarks` | REPORT-ONLY |

**The judged-pass exception is stated at the reproduction rule's own
width, and a narrower reading is a defect.** The rule the twin obeys
excepts a spelling a judged pass put there — one reading as a stand-in
NUMBER, *or* as a CALENDAR PLACEHOLDER — and both stay blank for one
reason: the absence reading of both runs through the producer's
outlier-and-share judgement over the measured file's own values, which
a twin's generated distribution is not guaranteed to re-fire.
Reproducing either would make the green battery contingent on a
re-judgement. A row excepting only the stand-in numbers would oblige a
producer to reproduce a published placeholder spelling, which the
reproduction rule forbids, and the sum identity above names the
judged-pass-sourced cells for the same reason: both pools are written
blank, so an identity naming only one of them is false by the same
construction it rests on.

`sentinel_verdicts` is REPORT-ONLY for calendar-placeholder entries
exactly as for stand-in numbers: a placeholder entry publishes the
placeholder's canonical ISO day spelling as its `candidate`, with its
occurrence count, verdict and reason, and the twin holds none of those
cells.

`n_distinct` and `n_distinct_folded` are universal keys whose
disposition is set per role group, in 9.3 to 9.7.

### 9.3 `empty`

| field | disposition |
|---|---|
| `n_distinct`, `n_distinct_folded` | EXACT-OBSERVABLE — both `0`, trivially met by an all-absent column |

`empty` is neither a label, an invention nor a distribution role, and
it carries no per-column `n_rows`. Its dispositions are stated
separately for exactly that reason. An `empty` column nobody declared
still publishes its `missing_by_source` accounting under the floor,
and the row above does not touch it: 9.2 governs it, and the twin
reproduces the recorded spellings there as on any other column.

### 9.4 The numeric roles: `count`, `continuous`, `affixed_number`

**`count` and `continuous`**

| field | disposition |
|---|---|
| `percentiles.min`, `percentiles.max` | EXACT-OBSERVABLE |
| `percentiles` interior rungs (`p01` … `p99`) | APPROXIMATED, inside a rung-by-rung two-sided envelope — `docs/spec/generation-method-v1.md` G5.6, restated as G12.2 |
| `n_zero`, `n_negative`, `std_unrepresentable`, `n_negative_unrepresentable`, `n_used_in_statistics`, `n_left_out_of_statistics`, `numeric_share` | EXACT-OBSERVABLE |
| `integer_valued` | EXACT-OBSERVABLE, routed by the published FACT and not by role |
| `mean`, `std`, `skew` | APPROXIMATED, fixed formula and two-sided bound — G12.3 |
| `n_distinct`, `n_distinct_folded` | EXACT-OBSERVABLE using the spellings owner decisions 7, 8 and 10 permit — the ordinary case; APPROXIMATED under the two-sided envelope only where even those cannot supply the count, with the report naming the profile's count beside the twin's. The envelope is G12.8, and BOTH of its ends are measured and printed on every run, because a fallback whose range is never shown is a fallback a reader cannot check (review item P2-C2-F4) |
| `numeric_styles` | EXACT-OBSERVABLE against the recount identity of section 7.5.7: every published count is met or exceeded, the three forms the remainder cannot reach are exact, and the remainder is spelled by its own cells' values |
| `fraction_widths` | EXACT-OBSERVABLE against a recount identity of the same shape: recounted cells at a named width number at least the published count and at most that count plus the pooled `(withheld)` value — exact where nothing pooled, windowed where something did. Widths are met by value adjustment inside the value-construction stage, so a pinned cell counts toward a width only when its value already fits it |
| `n_rows` (echo) | LOADER-ONLY |

A mutant that collapses the nine interior rungs onto the endpoints
must FAIL the rung envelope. So must a mutant that ignores, permutes
or swaps rungs.

**`affixed_number`.** The four universal census counts of 9.2 answer
for the CELLS on this role as on every other. The keys below describe
the CORES, and every quantitative disposition above is read here over
the cores and over `n_core_numeric` in place of `n_numeric`.

| field | disposition |
|---|---|
| `affix_prefix`, `affix_suffix` | EXACT-OBSERVABLE — written byte-for-byte around every counted cell's core, and recounted from the written twin |
| `n_affixed` | EXACT-OBSERVABLE — the twin writes exactly this many cells wearing the pair; the remaining present cells are reproduced by class through the straggler constructions |
| `n_core_numeric`, `n_core_out_of_range`, `n_core_contradictory`, `n_core_not_numeric` | EXACT-OBSERVABLE by class-preserving construction over the cores |
| `percentiles.min`, `percentiles.max` | EXACT-OBSERVABLE — exact values of real cores |
| `percentiles` interior rungs | APPROXIMATED, the G12.2 envelope read over the cores |
| `mean`, `std`, `skew` | APPROXIMATED, the G12.3 bounds read over the cores |
| `n_zero`, `n_negative`, `std_unrepresentable`, `n_negative_unrepresentable`, `n_used_in_statistics`, `n_left_out_of_statistics`, `numeric_share` | EXACT-OBSERVABLE over the cores |
| `integer_valued` | EXACT-OBSERVABLE, computed over the cores and routed on as the published FACT, never inferred from the role name (AF6) |
| `numeric_styles`, `fraction_widths` | EXACT-OBSERVABLE against the same two recount identities, read over the cores |
| `n_distinct`, `n_distinct_folded` | as on `count` and `continuous` above, the numeric mechanism supplying the spellings over the cores while the affix pair is constant across every counted cell |
| `n_rows` (echo) | LOADER-ONLY |

### 9.5 The label roles: `constant`, `binary`, `categorical`, `long_tail_labels`

| field | disposition |
|---|---|
| `levels` (normalized `label` and `count`) | EXACT-OBSERVABLE |
| `variants`, `variants_withheld` | EXACT-OBSERVABLE |
| `suppressed_levels`, `suppressed_level_counts`, `suppressed_rows` | EXACT-OBSERVABLE |
| `n_distinct_folded` | EXACT-OBSERVABLE |
| `n_distinct` | EXACT-OBSERVABLE where the published variants and the withheld-variant map supply enough spellings — the ordinary case; APPROXIMATED under the two-sided envelope only where they do not, with the report naming the profile's count beside the twin's. The envelope is G12.7 |
| `level_ceiling` (`categorical` only) | LOADER-ONLY |

The first five rows bind `long_tail_labels` exactly as they bind the
other three label roles: it publishes the four shared label keys under
the shared label invariants, its twin is written by the label
construction — published variants byte-for-byte at their counts,
invented neutral labels at the exact suppressed sizes, fold collisions
reproduced — and it carries no `level_ceiling`, so the sixth row
reaches it with nothing to dispose.

### 9.6 The calendar and clock roles: `datetime`, `time_of_day`

**`datetime`**

| field | disposition |
|---|---|
| `earliest`, `latest` | EXACT-OBSERVABLE in the representation owner decision 5 fixes. No corner, no exception: the last second of a leap minute is written back unchanged |
| `date_percentiles.min`, `date_percentiles.max` | EXACT-OBSERVABLE, in the same representation and on the same terms. No corner, no exception: they are the same two instants, and D11 makes that a rule the loader enforces rather than a sentence a document may contradict |
| `date_percentiles` interior rungs | APPROXIMATED — the window is G12.4 |
| `resolution`, `time_precision`, `subsecond_digits`, `utc_offsets`, `earliest_utc_offset`, `latest_utc_offset` | EXACT-OBSERVABLE, outside the withheld-offset corner below |
| `datetimes_read_at` | EXACT-OBSERVABLE outside that corner — derived from the offset diversity present in the cells, so it is recomputable from the written twin and must be checked that way. A dispatch assertion cannot detect a twin that reprofiles from `utc` to `local` because one invented rare offset changed the diversity while the pooled offset map and the endpoints still matched |
| `format` | REPORT-ONLY — it names the real file's parser family across all eleven members, and owner decision 5 chooses ISO twin syntax at the recorded precision, not the source's lexical family (residual R-P2-7) |
| `resolution_mix` | REPORT-ONLY — the twin writes every parsed cell at the column's finest recorded precision, exactly as the datetime rule writes every column, and the report names the recorded mix as not reproduced, per column, every run (residual R-P4-12) |
| `n_unparsed` | EXACT-OBSERVABLE as counted neutral stand-ins, explicitly OUTSIDE the parsed-value representation obligation |
| `n_distinct`, `n_distinct_folded` | APPROXIMATED — the envelope is G12.5, and it is stated there that it need not contain the published count |

Datetime cardinality has its own explicit bound so that one
implementation cannot bound datetime distinctness while another
ignores it.

**The one corner this matrix names, rather than leaving it to the
method alone** (review item P2-C1-F8). The method specification
already names it and requires it to be measured and named in the
report on every run; a matrix that claimed those fields were exact in
every case would be a matrix an implementer trusts and a report the
same implementer then cannot make honest.

**Withheld offsets.** Where every offset of a column fell below the
floor, `utc_offsets` collapses to a single `(withheld)` entry and the
endpoint offset fields read `(withheld)` too. The profile never says
which offsets those cells carried, so the twin writes them with no
offset at all: `utc_offsets` recounts as `(none)`, the endpoint fields
recount as `(none)`, and `datetimes_read_at` can fall from `utc` to
`local` because the twin holds one offset kind where the real column
held several. All four are then REPORT-ONLY for that column, with the
achieved value named beside the published one (G7.4, G12). It touches
those four fields and no others: `earliest` and `latest` are the
instants themselves, which a cell carrying no offset still gives back
exactly.

**THE LAST SECOND OF A LEAP MINUTE IS NOT A CORNER, AND MAY NOT BE
MADE ONE** (review item P2-C2-F5). `SS` of `60` is a reading the
canonical form admits because a real reader accepts one, and both
endpoints are exact in owner decision 5's representation with no
exception at all. A twin cell carries it: the two endpoint cells are
written from the published endpoint's OWN fields rather than through
the whole-second ordinal arithmetic the interior ranks use, so
`2024-11-02 04:55:60` is written `2024-11-02T04:55:60` and reads back
character for character (G7.5). An exact representation exists, and
lowering a ratified bar to fit an implementation is not available to
this document.

**And three pairs beside it are refused, not reported** (review items
P2-C3-F2, P2-C4-F1). An endpoint no cell of the column's own recorded
shape can show — seconds on a column whose `time_precision` is
`minute`; `SS` of `60` published while `datetimes_read_at` is `utc`;
an endpoint on the shared clock whose own offset carries its cell off
the end of the calendar — is each an exception, whatever it is called:
this table says the two ends are exact with no exception, and a
document the loader ACCEPTS whose end the twin then changes makes the
sentence false for every consumer who reads it. **D10 refuses all
three**, exactly as D6 refuses the `date`-beside-`datetime` pair and
for the same reason: published facts that no cell can show at once,
decidable from the fields themselves, are settled in the description
rather than paid for in the twin. The producer writes none of them, so
this refuses nothing a real table can express, and D11 ties
`date_percentiles.min` and `.max` to the same two texts so the ladder
ends cannot carry what the endpoints may not.

The head of section 9 still governs the documents whose facts cannot
all hold in ways two fields do not settle — a whole set of counts with
no joint answer is the generator's question, not the loader's. It is
not a route by which an end this contract calls exact becomes a line
in the report. Outside the withheld-offset corner, every field in this
table means exactly what its disposition says.

**`time_of_day`**

| field | disposition |
|---|---|
| `clock_form` | EXACT-OBSERVABLE — every twin cell of the column is written in the form this key names, so the form is recounted from the written twin. It is the clock role's analogue of `resolution`, which fixes the canonical text of a datetime cell and is exact for the same reason |
| `earliest`, `latest` | EXACT-OBSERVABLE — exact values of real cells, written back character for character in `clock_form` |
| `clock_percentiles` first and last rungs | EXACT-OBSERVABLE — they ARE the two endpoints, which T2 makes a rule the loader enforces rather than a sentence a document may contradict |
| `clock_percentiles` interior rungs | APPROXIMATED — the ends are pinned and the interior ranks are floor-division interpolations between them, in the ordinal unit the published form itself sets: minutes of day for `hh-mm`, seconds of day for `hh-mm-ss`. The two-sided window is fixed in the generation method's time-of-day clause and cited there, never restated here |
| `n_unparsed` | EXACT-OBSERVABLE as counted neutral stand-ins, explicitly OUTSIDE the clock-value representation obligation |
| `n_distinct`, `n_distinct_folded` | APPROXIMATED — the twin writes a value per rank between pinned ends, exactly as the calendar ladder does, so how many different values it holds is a consequence of the construction rather than a target, and the two-sided envelope that bounds both counts is fixed in the same time-of-day clause and cited there, never restated here. The ALL-DIFFERENT obligation of 9.8 is the one case the construction meets outright: it binds through the ordinal mechanism, whose capacity is stated — the space holds 1,440 or 86,400 distinct spellings by form, and the unparsed cells are stand-ins from an unbounded text family that supply distinctness of their own. A description whose distinct demand NET of its unparsed cells — `n_distinct` less `n_unparsed` — exceeds the form's capacity is the one infeasible shape, and it is REFUSED at the feasibility stage under the head of this section, never approximated. A description whose own source met every count, unparsed cells included, is never refused by this rule |

The ladder reads the day as a LINE from `00:00` to `23:59:59`, as
every ladder reads its axis, so a column whose values cluster across
midnight is described as two edge clusters with an empty middle and a
twin's interior interpolation fills that middle. The rungs are exact
values of real cells either way; the clock face's circular reading is
not modeled, exactly as a two-humped numeric column's valley is not.

### 9.7 The invention roles

**`free_text`**

| field | disposition |
|---|---|
| `length`, `words` | STRUCTURAL — the container's own key carries no VALUE obligation; its membership is the four and three keys below, and every one of them is disposed in its own right |
| `length.min`, `length.max`, `n_all_digits`, `n_code_alphabet`, `n_distinct_by_occurrences` | EXACT-OBSERVABLE |
| `words.min`, `words.max` | EXACT-OBSERVABLE, with no corner and no exception. A cell of `L` characters holds at most `(L + 1) // 2` space-separated words, so a document publishing a word extreme its own published length cannot carry — more words than `length.max` holds, or a floor under every value that the `length.min` value cannot reach — is a document whose facts cannot all hold, and generation is refused before any cell is built (G12, `generation-words-exceed-length`). A real column cannot produce that pair |
| `length.mean`, `length.p50`, `words.mean` | APPROXIMATED, two-sided bounds — fixed by G12.6 |
| `n_distinct`, `n_distinct_folded` | EXACT-OBSERVABLE |

**`identifier`**

| field | disposition |
|---|---|
| `min_length`, `max_length`, `n_all_digits`, `n_code_alphabet` | EXACT-OBSERVABLE in every case, since owner decision 6 keeps the length |
| `all_whole_numbers` | EXACT-OBSERVABLE in every case, since owner decision 6 keeps the length. A published length range in which a value that must stand outside the figures can be no whole number at all — one character cannot be both — is a document whose own facts cannot all hold, and generation is refused before any cell is built (G12, `generation-whole-numbers-need-room`). No producer-written profile carries that pair |
| `n_distinct`, `n_distinct_folded`, `n_distinct_by_occurrences` | EXACT-OBSERVABLE outside owner decision 6's infeasible corner; all THREE REPORT-ONLY inside it, with the report naming the achieved value beside the published one |

Two shapes a real table produces used to cost `all_whole_numbers`, and
neither does now (Phase 3 plan P3-D8.1, owner decision 1). A length
end pinned onto a group whose band has no whole-number spelling at
that one length, where the source's own values show another pairing
that holds every published count, closed when the length ends and the
bands were settled in ONE packing rather than pinned first, as G9.5
already does for free text: the packing walks every carrier pair and
finds the pairing the source's values prove exists. A published length
range whose longest value is two characters, where some value has to
stand in the code alphabet, is a **bounded carve-out to G9.1** (owner
decision 9): the only two-character whole numbers outside the figures
begin with a sign, and G9.1 keeps a made-up value from beginning with
one, because that is the character common spreadsheet software reads
as the start of a formula. The twin writes the sign, and the report
counts those cells and names their column. A description carrying
those counts proves the real column held such values, since no other
spelling of that width exists, so the twin inherits a hazard the table
already had. Where the sign is needed is decided by the packing, which
reaches for it only when no assignment of whole groups meets every
published count without it. `all_whole_numbers` is therefore
EXACT-OBSERVABLE in every case a twin is written at all, and this
contract grants no lesser outcome for it.

**`numeric_unrepresentable`**

| field | disposition |
|---|---|
| `n_whole`, `n_fraction`, `n_whole_unknown`, `n_positive`, `n_negative`, `n_sign_unknown`, `n_distinct_by_occurrences` | EXACT-OBSERVABLE |
| `min_length`, `max_length` | EXACT-OBSERVABLE — the twin's numerals are written inside the published range with both ends carried, which is what retires the invented four-hundred-figure width and its always-printed deviation, and what closes residual R-P2-1 |
| `n_distinct`, `n_distinct_folded` | EXACT-OBSERVABLE |

**The fold-collision obligation.** On the invention roles both
distinctness counts are EXACT-OBSERVABLE, which obliges the invention
alphabet to REPRODUCE FOLD COLLISIONS when the profile shows folded
below raw. That obligation is binding and non-trivial: a real 200-row
single-character identifier profile publishes 200 raw and **122**
folded, so 78 values must fold onto a partner.

**The obligation is the WHOLE fold, both halves of it** (P2-C2-F6). A
folded identity is this document's own definition at section 2: the
cell's text after TRIMMING and a Unicode `casefold()`. Two spellings
therefore collide when they differ in case, in edge spacing, or in
both, and a construction reaching for only one of the two answers
fewer collisions than the profile can legitimately publish. A column
of `a`, ` a`, `a ` and ` a ` publishes four raw spellings, one folded
identity and the length range 1 to 3, and every one of those facts is
EXACT-OBSERVABLE at once — the source column is the proof that they
hold together. Losing the folded count there is not owner decision 6's
infeasible corner and may not be named as one; the constructions that
meet it are G9.3, and the alphabet counts survive them because both of
those are read after trimming as well. Where the published lengths pin
every cell's length, a fold partner may shorten its digit body to make
room for edge spacing inside the pinned length, so any source whose
own cells matched the published pattern remains expressible.

### 9.8 The all-different obligation, and the three places it cannot bind

Whenever a column publishes `n_distinct == n_present`, its present
values are all different, on every role, in that column's own notion
of equality — because an undeclared key column arrives as free text or
as a numeric role, not as an identifier. **The obligation can bind
only on facts the profile actually publishes.** Where the raw
distinctness of a column was produced by something the disclosure
rules WITHHELD, the twin cannot reproduce it without making facts up,
so raw distinctness is REPORT-ONLY there and the report names the
achieved count beside the published one. Three instances are known and
each is tested:

1. **Declared identifiers** whose published length range cannot supply
   as many distinct values as the column has rows (owner decision 6,
   section 6.8).
2. **Label columns** whose values differ only before the fold —
   resolved by owner decisions 9 and 11, which publish the variants,
   so the obligation now HOLDS for labels wherever the variants are
   visible and falls back only beneath the floor (section 7.4).
3. **Datetime columns whose offsets are withheld.** A 30-row column of
   ten rare offsets over 15 dates publishes
   `n_present == n_distinct == 30` while `utc_offsets` collapses to
   `{"(withheld)": 30}`: the obligation fires, but the profile never
   says which offsets made those 30 spellings distinct, so the twin
   holds only 15 instants and no published way to spell them apart.
   Where the same column's offsets ARE published, the obligation holds
   and the twin uses them.

Stating the obligation as one rule with named instances is what stops
a fourth instance arriving undetected.

**On `long_tail_labels`, `affixed_number` and `time_of_day` the
obligation BINDS**, through the mechanism each role's own facts
already use, and none of them is a fourth instance: `long_tail_labels`
through the label mechanism, where the published variants and the
withheld-variant map supply the spellings exactly as on every other
label role; `affixed_number` through the numeric mechanism over its
cores, the affix pair being constant across every counted cell; and
`time_of_day` through the ordinal mechanism, whose capacity is finite
and stated, so the one shape that cannot be met is refused at the
feasibility stage rather than reported as a loss.

---

<!-- a10a: the loader -->

## 10. The loader, part one: what it does

**C6-100.** The strict loader is the ONLY way generation receives a
description. It is fail-closed: a document it cannot prove conforming is
refused, never repaired, never partially accepted.

The integer this loader reads, the two version refusals with their
exact wording, and the refusal catalogue `R1`–`R19` are the NEXT
SECTION's [assembly: the loader, part two].

### 10.1 The order of operations

**C6-101.** The order is normative, because it decides which message a
person sees when a document is wrong in more than one way, and the most
useful message is the one nearest the cause.

| step | what happens | refusals it can raise |
|---|---|---|
| 1 | resolve and open the description path | R1, R2, R3 |
| 2 | read the bytes and decode as UTF-8 | R4, R19 |
| 3 | the bounded structural pre-scan over the TEXT, using only string operations, before any parse | R8, R9 |
| 4 | parse with a plain JSON parse — no callback slot of any kind is involved | R5 |
| 5 | read `profile_version` and check it is exactly the integer the next section fixes | R11, R12, R14, R15 |
| 6 | the canonical round trip: re-serialize under section 3.2 and require the result to be the file | R6, R7, R10 |
| 7 | schema and invariant validation: the top level first, then the columns in list order | R13 … R18 |
| 8 | build and return the typed objects | — |

Step 5 reaches R14 and R15 as well as the two version refusals: a
document that is not a block of named entries, that carries no
`profile_version`, or whose `profile_version` is not a whole number is
refused THERE, because until the loader holds that integer it cannot say
whose rules to apply.

**C6-102 (why the version is read BEFORE the round trip).**
Direction-correct version advice is more use to a person than a
complaint about canonical form, and an older or newer document is very
likely to be canonical under its OWN rules and to fail this one's for
reasons that would only confuse. The consequence is stated rather than
hidden: at step 5 the loader is reading a value the round trip has not
yet proved unique, so a document with a duplicated `profile_version` key
is described by its last value — and is then refused a moment later at
step 6 anyway.

**C6-103 (why the pre-scan precedes the parse).** Both bounds exist to
protect the parser itself; checking them afterwards would be checking
them after the cost has already been paid.

**C6-104 (the order within step 7).** The top level is checked first and
the columns afterwards, in list order, so that a person reading a
refusal meets the outermost thing that is wrong. Two placements are
fixed because either is reasonable:

- The three rules that need BOTH halves run at the END of step 7,
  because until the columns are read there is nothing to check them
  against: S8, every name declared as holding record numbers is a column
  of this table; S10, every note is about a column of this table; S11,
  the notes are grouped by column in column order.
- S13 runs WITH the top level, although the floor it reads lives in
  `settings`: what it reports is a fact about the whole description —
  it was made at a floor of one and it holds something back — and that
  is outermost, nearer the cause than the column arithmetic such a
  spliced-in field breaks on the way past.

### 10.2 What the loader does NOT do

**C6-105 (no feasibility check).** The loader performs no generation
feasibility check whatsoever. That is a separate stage, run after
loading and before generation, so that a contract-valid document never
becomes unloadable and a refusal to GENERATE is never mistaken for a
claim that the description is invalid.

**C6-106 (no repair).** It does not normalize, reorder, coerce, default
or fill. A document that is not canonical is refused, not rewritten.

**C6-107 (no table).** It accepts a filesystem path to the description
and nothing else. It constructs no table path, no table handle, no table
object and no raw cell collection, at any layer (plan P2-D1).

It does not upgrade a document written under an earlier version, does
not partially accept one, and does not offer to; that rule and its
reason are stated with the version rule in the next section.

### 10.3 The two parser bounds

**C6-108.** EXACTLY TWO BOUNDS EXIST. Neither is reachable by any
producible description, because neither scales with the table.

| bound | value | why |
|---|---|---|
| maximum nesting depth | **32** | a conforming document is six deep (section 3.4), and depth is a function of this format's shape, not of the data |
| maximum length of a single JSON NUMERIC TOKEN | **64 characters** | an arbitrarily long numeric literal costs quadratic parse time, while the producer's longest published number is far shorter |

**The pre-scan.** Both are checked by a bounded first-party structural
pre-scan over the document text using only string operations, before
parsing. It is string-literal aware, because a brace inside a quoted
value is a character of that value and not a level of nesting:

- a `"` outside a string opens one and a `"` inside one closes it,
  except where it is preceded by an odd number of backslashes;
- inside a string, nothing counts: no brace, no bracket, no digit;
- outside a string, `{` and `[` increase the depth and `}` and `]`
  decrease it; the deepest depth reached is compared with 32;
- outside a string, a NUMERIC TOKEN is a maximal run beginning at `-` or
  a digit and continuing over the characters `0`–`9`, `.`, `e`, `E`, `+`
  and `-`. Its length in characters is compared with 64.

**Near-limit-valid and one-over-limit tests are required for each
bound.**

**C6-109 (no other limit exists anywhere).** No document-byte cap, no
container-entry cap, no producer-side cap, and no string-length cap
beyond the reader's own shipped field limit. A description too large for
the machine fails on the catalogued memory-exhaustion path (R19) exactly
as the profiler's own reader does, so the two halves of the product
promise the same thing. A container-entry limit was considered and
REMOVED: every column contributes one entry to `columns`, so a
ten-million-entry ceiling is a ten-million-COLUMN ceiling, which the
profiler never promised to stop at. A producer-to-loader boundary test
asserts that a genuine wide-table description loads.

### 10.4 The canonical round trip

**C6-110.** The loader re-serializes the value step 4 parsed, under
section 3.2's canonical rules, and requires the result to be the file:
the canonical text must equal the file's text, AND its UTF-8 byte length
must equal the file's size in bytes. The second comparison is not
redundant: section 3.3 states why a loader decoding with universal
newlines has not compared bytes without it.

**What this single check catches — EIGHT defects**, each verified
before being written here:

| defect | why the round trip catches it |
|---|---|
| a duplicated key | the parse keeps one value; re-serializing writes the key once, so the text is shorter than the file |
| keys in any order but ascending | re-serialization sorts, so a reordered document does not come back the same |
| a number spelling that is not the shortest round trip of its own value — `1.0e2`, `2.50`, `1E5` | re-serialization writes the shortest form of the parsed value, `100.0`, `2.5`, `100000.0`, which differs |
| any indentation, spacing or separator but the canonical one | re-serialization fixes the layout |
| `NaN`, `Infinity`, `-Infinity`, which a plain parse accepts | re-serialization refuses to write them at all (R7) |
| an escaped lone surrogate, such as `"\ud800"` | re-serialization cannot encode it as UTF-8 (R6) |
| a missing or extra terminal newline | the canonical text has exactly one |
| CR LF line endings | the byte length differs, even where a translating reader made the text itself agree |

**C6-111 — what it does NOT catch, stated because an earlier revision
said it did** (review item P2-C1-F8):

- **A trailing `.0` on a whole-valued number passes this check.** `2.0`
  parses to a float and re-serializes as `2.0` under 3.2.1, byte for
  byte. Where the field is typed integer, T1 refuses it at step 7 (R15);
  where the field is typed number, it is a correct canonical document
  and there is nothing to refuse.
- **`+5` and `05` never reach this check.** JSON has no grammar for a
  leading `+` or a redundant leading zero, so the plain parse of step 4
  stops on them and the person sees R5 with the position the parse
  stopped at.

Both are stated because a row claiming the round trip catches them is a
row an implementer builds a test around, and the test would then pass
for the wrong reason.

**C6-112 (no callback slot is involved).** The check is a
re-serialization and a comparison; it installs no parse hook of any
kind, and the offline policy's callback rules are not engaged by it.
Neither does step 4: the parse is handed the text and nothing else — no
object hook, no pairs hook, no parse hook — because the offline policy
forbids handing a callable to a library API (offline-guarantee plan
D6.2, not P4-D6.2), and because the duplicated keys a pairs hook is
usually reached for are caught by this check instead.

### 10.5 The type rules the loader enforces

JSON's type system is looser than this format's, so four rules are
stated explicitly. **These four are the LOADER's `T` rules; the `T1` to
`T5` of the `time_of_day` role are a different family wearing the same
letter** [assembly: the time-of-day invariant table].

**TY1 — integers are integers.** A field typed "integer" must be a JSON
integer: no fractional part, no exponent. `2.0` is refused where `2` is
required. This is a real distinction, because `2.0` survives the
canonical round trip unchanged.

**TY2 — booleans are not integers.** In several host languages a boolean
is a subtype of integer. A field typed "integer" refuses `true` and
`false`; a field typed "boolean" refuses `0` and `1`.

**TY3 — numbers may be integers.** A field typed "number" accepts both a
JSON integer and a JSON float, and reads the same value from either.
`mean: 2` and `mean: 2.0` are both canonical — they are the two kinds of
3.2.1, and this format does not say which kind a producer holds a
whole-valued statistic in, so a loader that refused one would refuse a
conforming document. The shipped producer holds these statistics as
floats and therefore writes `2.0`.

**TY4 — null is a value, not an absence.** A field whose type permits
`null` still has its key present. A key that is absent is a missing
required key (R14), never a null.

### 10.6 What the loader returns

**C6-113.** Typed objects: one document object holding the top-level
facts, the source block, the settings block, the empty relationship
manifest, the publication notes, and a list of column objects in list
order. The list order of the returned column objects IS the order of
`columns` (S3), and every consumer walks it in that order: schema order,
output column order, RNG consumption order.

---

<!-- a10b: the version rule, the refusals, the message -->

<!-- continues section 10 -->

### 10.6 The version rule, and what it binds

**C6-44.** `profile_version` is the integer `6`. The producer writes
`6`; the loader reads exactly `6` and refuses every other integer. The
version is read before the canonical round trip, so a person holding an
older or newer description is told which they hold rather than handed a
complaint about canonical form they cannot act on.

**How C6-44 binds the catalogue.** The two version rows below, R11 and R12,
read against the integer THIS loader reads — `6` — never against one
left standing from an earlier contract. Below `6` trips R11; above `6`
trips R12; `6` alone passes to the remaining checks. This is written out
because leaving it implicit has already gone wrong, and it goes wrong
two ways: a catalogue whose rows still read against `4` gives the
integer `4` no row to trip at all, so the one message this document
fixes word for word has nothing to fire it, and `5` — an older document
— trips the NEWER row and is told to update synthtwin when it should be
told to describe the table again. The shipped loader already compares
against its own version constant rather than a literal
(`src/synthtwin/contract.py`), which is this binding in code.

**C6-45 (fail-closed, no upgrade).** The loader does not upgrade an
older document, does not partially accept one, and does not offer to. An
older description carries facts computed under rules that changed;
converting it would mean making up facts the older rules never held,
which is the whole reason this version exists.

### 10.7 The two version rows, and why their advice differs

**R11 — an OLDER description** (`profile_version < 6`). The advice is to
make the description again by running `synthtwin profile` on the table,
under the options of the first run. Its exact words are C6-46.

**R12 — a NEWER description** (`profile_version > 6`). The advice is to
UPDATE synthtwin, and never to re-run a profiler. A newer description
means this synthtwin is behind, and telling somebody to re-run a
profiler on a machine that may not hold the table — or that may hold a
different table — is advice that cannot be followed and may be acted on
anyway. The message says which version this synthtwin reads and which
version the document claims.

### 10.8 The refusal catalogue

**C6-83.** Every refusal on this path has its own plain-language
message, an exact-shape test and a reachability test. Every message says
what happened and what to do next, in words a person who does not
program can act on. **No message on this path quotes `n_rows`**, because
allocation can fail before any field is validated and a message that
names a row count it never read is a message that lies. Neither version
message quotes anything from the document except the two version
numbers.

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
| R11 | `profile_version < 6` | both versions, and to re-run `synthtwin profile` |
| R12 | `profile_version > 6` | both versions, and to update synthtwin — never to re-run a profiler |
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

**Nineteen rows, and they are the LOADER's.** A description whose
published facts no twin can hold — a `time_of_day` column whose distinct
demand net of its unparsed cells exceeds its form's space of 1,440 or
86,400 spellings — is a valid description this catalogue accepts; it is
refused later, by name, at the generation-feasibility stage, which is
not a loader refusal and takes no row here.

### 10.9 The older-version message, word for word

**C6-46.** R11's message is EXACT TEXT, not a shape a message must have.
Text that only describes the shape replaces an exact message with an
approximate one, and the failure is concrete: two loaders both claiming
to keep "the shape", naming different option sets in different words,
and a person following the shorter one omits a publication-changing
option and writes a description that exposes what the old run held back.
The message is therefore written out, and it is the message — with only
the two version numbers filled in from the document and the loader, so a
version 5 document reads "version 5":

> This description was written by an older version of synthtwin: it
> says it is version 4, and this synthtwin reads version 6. A version
> 6 description records things an older description does not — which
> of synthtwin's own words for "no value" you named on the command
> line, and how slashed dates were read — so this file cannot be read
> back exactly. Please make the description again by running
> 'synthtwin profile' on your table, giving it every option you gave
> the first time: --keep-value, --missing-value, --identifier,
> --smallest-group, --first-row and --day-first. Every one of them
> changes what the description PUBLISHES about your table, so any
> option you leave out can put something into the new description that
> the old one held back: without the --smallest-group you gave, a
> value that fewer rows share can be named; without the --identifier
> you gave, a column of record numbers is described like any other
> column; without the --missing-value you gave, a stand-in is read as
> a real reading, and the stand-in itself can be published as the
> column's smallest value; without the --keep-value you gave, a word
> you had counted as an ordinary value becomes a gap, which can change
> what kind of column synthtwin sees and publish both that word and
> the column's own numbers; without the --first-row you gave, the
> first line of your file is read as the column names and published as
> them; and without the --day-first you gave, slashed dates can be
> read the other way round, which changes the dates the description
> publishes and can leave the column described as text instead. If you
> do not hold the table yourself, ask whoever made this description to
> run it again for you. Read the summary page synthtwin writes beside
> the new description before either file goes anywhere, and use the
> description exactly as synthtwin writes it.

**Why it names six options and prices each.** The message names EVERY
option of `synthtwin profile` that changes what the description
publishes about the table, and says of each what leaving it out can put
into the new description. A person who ran with no options loses nothing
by re-running; one who ran with them and forgets one gets a description
that reads their table differently and can publish more of it. Advice
that sends somebody to re-run must say so where they read it: re-running
under different options is not merely "different" — it can disclose.

**What the message does NOT do.** It does not tell the person which
options THEIR description was made with, although their own settings
block records every one: C6-83 forbids quoting the document beyond the
two versions, and the version is read before that block is validated, so
there is nothing this message may soundly read out. What is owed and
paid is that they are told which options matter.

**A standing obligation, and its test.** A test derives the set of
options named in this message from the shipped argument parser, so an
option added later and not named here turns the suite red. The
obligation is on the option set, not on the prose: an option joins the
sentence in the commit that adds it, and joins the priced list too
unless somebody can show it changes only how the table is READ — which
is what nobody could show for the three that were once excused on
exactly that ground.

**C6-47 (the holder assumption, re-examined and answered narrowly).**
The "describe the table again" advice was declared safe only while no
release existed; this clause records that the question was asked. The
release fact holds: no release, no tag, nothing published. It supports
only that the population which can MAKE a version 6 description is
bounded by the people a maintainer handed the tool to; it does NOT
support the narrower claim that such a maintainer ran from a source
checkout, because a wheel built from the tree reaches a colleague who
never sees the source. That bound was never load-bearing anyway: a
description travels, and its holder may be a colleague who never ran the
tool, so this clause does NOT claim that every holder holds the table.
The message is addressed to a reader who can act on it and says so —
describe the table again with the same options if you hold it, ask
whoever made the description if you do not — so the second reader is
never assumed away. The obligation recurs: the first release widens that
population to the whole public and owes whichever version is current
then a new analysis, which this re-examination does not discharge.

---

<!-- a14: capacity, the disclosure inventory, the decisions -->

## 11. The carried condition: invention domain capacity

Phase 2's plan review round 5 raised, and the plan CARRIED rather than
settled, one condition that touches this contract's obligations without
being one of its rules (its item P2-R5-F4, "finite invention domain").

**The condition.** Several fields of this contract oblige the generator
to produce a stated number of distinct invented values — raw
`n_distinct` and `n_distinct_folded` on the invention roles (section
9.7), the fold-collision obligation, the invented spellings that
`variants_withheld` calls for (section 7.4), and the invented labels
that `suppressed_level_counts` calls for. Every one is finite only if
the alphabet the generator invents from is large enough. The alphabet
is finite, so for each there exists a description whose published
counts exceed the domain's capacity.

**Where it is owned.** The plan carried this to the
**method-specification gate**, bounded:
`docs/spec/generation-method-v1.md` fixes the invention domain and its
capacity rule with a **named refusal** where capacity cannot be met.
Its section G9 is where that is written and G9.4 is the capacity rule.
It is not this contract's to settle, and this contract does not settle
it.

**What this contract does say, so the carry is not a hole.**

1. The condition changes no rule here. A description that exceeds the
   invention capacity is a VALID version 6 description and the loader
   accepts it. The capacity question belongs to the
   generation-feasibility stage, which runs after loading (10.2).
2. Where the capacity rule cannot be met the outcome is a refusal of
   GENERATION, never a claim that the description is invalid: the
   message says the description is valid, names the two facts that
   cannot both hold, and gives remediation that does not assume the
   person still holds the table.
3. **Two capacity conflicts sit outside the carry, because a ratified
   plan has already settled each.** A declared `identifier` whose
   length range cannot supply enough distinct values is governed by
   Phase 2 owner decision 6 — length wins, values repeat, three
   distinctness facts become REPORT-ONLY and the report names all three
   (6.8). A `time_of_day` description whose distinct demand NET of its
   unparsed cells — `n_distinct` minus `n_unparsed` — exceeds its clock
   form's finite space of 1,440 or 86,400 spellings is a NAMED REFUSAL
   of generation (Phase 4 plan P4-D4.2 and P4-D8.5). A description
   whose own source met every count, unparsed cells included, is never
   refused by that rule.
4. Two of the three roles this version adds raise no capacity question
   of their own. `long_tail_labels` invents through the label
   machinery, whose withheld-level and variant alphabets have no end;
   `affixed_number` invents through the numeric machinery over its
   cores, whose leading-zero family has no ceiling. Each inherits the
   posture of the machinery it borrows.
5. The domain is widened before any of this is asked: identifier and
   text alphabets include upper and lower case — which is also what
   lets fold collisions be placed — and the full printable ASCII range.

A reviewer checking this contract for completeness should read this
section as the record of a known gap with a named owner, not as a rule.

---

## 12. The disclosure inventory

### 12.1 What this section is

This is the one place that says what a version 6 description publishes
about the real table and what each item costs, so a person can weigh a
description without reading the rest of this document.

**C6-54 (completeness).** Every fact a version 6 description publishes
about the table has a row in this section, and every other key of this
format publishes no fact about the table. Completeness is asserted over
the WHOLE document — every top-level key, every settings key, every
column block of every one of the thirteen roles, and every sentence
form of section 4.5 — and not over the facts one version added. A key
or a sentence argument added to this format that reaches no row here,
and that is not shown to publish nothing of the table, is a defect in
this document, and the battery the plan requires turns red on it.

### 12.2 The standing inventory: what any description publishes

| where | what of the table it publishes | floor treatment |
|---|---|---|
| `n_rows`, `n_columns` | the exact shape of the table | floor-free |
| `profile_version`, `created_with` | the format version and the version of synthtwin that wrote the file | carries no cell, no column and no count of the table |
| `source.encoding`, `used_fallback_encoding` | how the file was read | carries no cell |
| `source.header_source`, `header_by_convention`, `header_evidence` | whether the first row was names, in one sentence of the closed grammar | carries no cell of the body |
| `columns[].name`, `columns[].position` | the column's own name exactly as written — the file's own text wherever `header_source` is `file` — and its one-based place in the schema | floor-free |
| the universal counts (5.1) | `n_present`, `n_missing`, `n_distinct`, `n_distinct_folded`, `n_numeric`, `n_not_numeric`, `n_out_of_range`, `n_contradictory`, `n_sentinel_candidates_unpublished`, `n_missing_blank`, `n_missing_withheld` — counts, never a value | floor-free EXCEPT the two absence counts: `n_missing_blank` is `0` or at least the floor, and the blank cells below it are counted in `n_missing_withheld`, which is itself a pooled residue |
| `missing_by_class` | six counts of absent cells by reason | each non-`(withheld)` value 0 or at least the floor |
| `missing_by_source` | the EXACT absent-value SPELLINGS the cells wore, with counts | floor-governed; empty on a nothing-publishing column |
| `sentinel_verdicts` | the candidate as text — a stand-in number, or a calendar placeholder's ISO day — with occurrence count, verdict and reason | `(withheld)` on a nothing-publishing column |
| labels-class blocks (`constant`, `binary`, `categorical`, `long_tail_labels`) | folded label spellings with row counts; each label's exact spellings under `variants`; how many levels were held back and how many rows they cover (`suppressed_levels`, `suppressed_rows`) and the ascending sizes of those levels (`suppressed_level_counts`) | every named spelling floor-governed; the three held-back facts publish SIZES and COUNTS of unnamed groups, floor-free |
| `level_ceiling`, on `categorical` | the effective category cap the run applied, computed from `categorical_ceiling`, `categorical_share`, `categorical_floor` and `n_rows` | publishes nothing the settings block and `n_rows` do not already publish |
| ranges-class blocks (`count`, `continuous`, `datetime`, `time_of_day`, `affixed_number`) | endpoints and the eleven ladder rungs, which are exact values of real cells; moments and shape statistics; sign and zero counts; the style census, the fraction-width census and the offset map; `resolution_mix`; the affix pair | endpoints and rungs FLOOR-FREE under the ranges-class endpoint policy; the three maps floor-governed with a `(withheld)` pool; the affix pair floor-governed by its own detection rule |
| nothing-class blocks (`numeric_unrepresentable`, `identifier`, `free_text`) | lengths, word statistics, digit and code-alphabet counts, the whole-number test, the repetition multiset, and on `numeric_unrepresentable` the whole-number and sign counts | no value, no spelling, no fragment of one; the multiplicity map publishes SIZES of unnamed groups under no floor |
| `empty` columns nobody declared | the absent SPELLINGS their cells wore and the two absence counts, exactly as any column that is not nothing-publishing | floor-governed |
| `settings` | the rules the run applied, the floor's own value, how many values each declaration named, and which of THIS package's published words were among them | carries no cell, no column and no count of the table; a person's own spelling never enters |
| `source.header_evidence`, `publication_notes[].note`, `detection_evidence`, `remarks` | sentences of the 41 closed forms: 62 argument positions, of which 53 are whole numbers, 3 package words, 4 nested forms and 2 bound affix strings | the whole numbers are counts the block beside them already publishes, EXCEPT the positions priced at rows 16 and 18 |
| `relationships` | nothing: eight nulls | — |

### 12.3 The rows, each priced

Rows marked NEW did not appear in a description written under version
5; the marking is history, and each row stands on its own terms without
it. A privacy approval given for an earlier description does not cover
a marked row.

1. **Long-tail levels. NEW.** Floor-cleared label spellings from
   columns that published no value before. Bounded by the floor exactly
   as every label is; the detection line never drops below eleven rows,
   so a lowered floor cannot make a new column label-publishing.
2. **The affix pair. NEW.** Two shared cell fragments per affected
   column, floor-governed by C6-4's detection rule, under the named
   ranges-class exception.
3. **The affixed-core quantitative block, as one grouped row, every
   fact named. NEW.** `percentiles`, `mean`, `std`, `skew`,
   `std_unrepresentable`, `n_zero`, `n_negative`,
   `n_negative_unrepresentable`, `n_used_in_statistics`,
   `n_left_out_of_statistics`, `numeric_share`, `integer_valued`,
   `n_rows`, `numeric_styles` with its sibling `fraction_widths`,
   `n_affixed`, and the four core-class counts `n_core_numeric`,
   `n_core_out_of_range`, `n_core_contradictory`, `n_core_not_numeric`
   — each under the treatment the same fact has on a plain numeric
   column, all of it reaching columns that were free text. With row 2
   this prices all twenty-two keys the role adds; rows 4 and 7 restate
   two of them at their own floor treatment and add nothing to the set.
4. **Core endpoints and ladder rungs of affixed columns, and clock
   endpoints and rungs of time-of-day columns. NEW.** Exact values of
   real cells, published floor-free under the ratified ranges-class
   endpoint policy, newly reaching columns that were free text.
5. **Every ROLE-ADDED fact a datetime block publishes**, on every
   column the five calendar members `slashed-iso-date`, `iso-month`,
   `iso-mixed`, `month-first-datetime` and `day-first-datetime`, or the
   unpadded reading of the slashed month and day fields, newly claim.
   **NEW for such a column.** The universal keys it newly fills are
   priced at row 15, not here. The role-added set is thirteen keys, of
   which a `free_text` block carries none, so every one is new for such
   a column:
   - **VALUES of real cells, floor-free under the ranges-class endpoint
     policy:** `earliest` and `latest`; `date_percentiles`, whose `min`
     and `max` ARE those two texts by D11 and whose nine interior rungs
     are interpolated; and `earliest_utc_offset` and
     `latest_utc_offset`, each the offset text that endpoint's own cell
     carried.
   - **One VALUE map that is floor-GOVERNED:** the KEYS of
     `utc_offsets`, each an offset spelling as the source wrote it,
     under D3's floor with a `(withheld)` pool.
   - D9 flattens both endpoint offset fields and every `utc_offsets`
     key to `(none)` or `(withheld)` unless `resolution` is `datetime`,
     so of those five members only `iso-mixed`,
     `month-first-datetime` and `day-first-datetime` may carry an
     offset at all (14.6 binds each member to its resolution).
   - **SHAPE facts, carrying no cell but fixing how every cell of the
     column was written, floor-free:** `format`, the parser family that
     read the REAL file, REPORT-ONLY because the twin is written in ISO
     syntax; `resolution`, the canonical form the published datetimes
     are written in; `time_precision`, the finest precision any cell
     writes; `subsecond_digits`, the most fractional-second digits any
     cell writes; `datetimes_read_at`, which clock the endpoints and
     the ladder are on and therefore, by D5, whether the column mixed
     offsets; and the KEYS of `resolution_mix`, whose counts row 8
     prices.
   - **COUNTS of the table, floor-free:** `n_unparsed`, the present
     cells that did not read as a date under the chosen format — the
     datetime sibling of the count row 13 prices; and the VALUES of
     `utc_offsets`, how many rows carried each named offset.
   - **A column newly claimed here need not have been free text.**
     `datetime` is tested before `count`/`continuous` and before
     `categorical`, so a column either of those claimed can be taken by
     the widened rule — a column of `YYYY-MM` values under the
     categorical ceiling is the clean case — and such a block gains the
     same thirteen while it STOPS publishing that column's label
     spellings. A `constant` or `binary` column is not reachable: both
     are tested before `datetime` and an earlier rule's claim survives.
6. **The two unrepresentable lengths. NEW.** For decimal numerals
   length bounds magnitude, so `max_length` states the largest withheld
   numeral's order of magnitude: one cell's worth of floor-free fact.
7. **The fraction widths. NEW.** Floor-governed with a pooled
   remainder: every named width's count is at or above the floor by P6,
   and the total is bound in every case by P5 — exactly by the
   `decimal` style's own count where that key is published, and, where
   it was pooled instead, above and below by the four conditions of
   case P5.c.
8. **The exact resolution-mix counts. NEW.** Floor-free, with C6-25's
   subtraction argument stating why a floor would withhold nothing.
9. **The twin as a carrier of published hole spellings. NEW.** A
   person's own marker word, already published in the description under
   the floor, is also written into the twin.
10. **The `built_in_dates` lists. NEW.** In both declaration records:
    which of the two calendar placeholders a declaration named,
    computed from the command line alone, carrying no cell, no column
    and no count of the table — the treatment the two other declaration
    lists have.
11. **The sizes of BELOW-FLOOR FOLDED identities on a long-tail
    column**, via `suppressed_level_counts`. **NEW, and narrower than
    the key looks; stated at the plan's own width (P4-D5).** Row 1
    covers spellings at or above the floor and is easy to read as the
    whole of the long-tail disclosure; it is not. A free-text column
    already publishes a repetition map, so sizes of unnamed groups are
    not themselves new — but that map groups RAW spellings and this
    multiset groups FOLDED identities. The additional fact is which
    unnamed spellings share a trim-and-case identity: counts only,
    never a spelling. Owner decision 1 is priced with it. A privacy
    reviewer approving on the belief that nothing below the floor
    changed would be approving something this document does not do.
12. **The eight new text members of the published vocabulary. NEW, in
    BOTH the ways they reach a document, and the second is much the
    larger.**
    - **By declaration:** `built_in_texts` may record any of the seven
      spreadsheet error literals or the exact-spelling `NaT`. Like the
      other lists this is a function of the command line alone and
      carries no cell.
    - **AUTOMATICALLY, with no declaration at all.** These eight
      spellings are read as absent BY DEFAULT. A column of ninety
      numbers and ten cells holding one error literal published no
      number of the table before; here the ten read as absent, the
      ninety clear the parse line, and the column becomes numeric. What
      appears is not one fact but four: the error SPELLING and its
      COUNT in `missing_by_source` where the floor admits them, the
      column's whole numeric distribution — mean, spread, endpoints,
      ladder rungs — and the role transition itself. None of it
      required anybody to type anything.
    - This is the largest single widening in this table and a direct
      consequence of owner decision 7. It is priced here rather than
      left to be discovered, because a reviewer reading this row as
      "one more thing a declaration can record" would be reading the
      smaller half.
13. **The time-of-day form facts. NEW.** `clock_form` says which of the
    two written clock forms the column's cells wore, and `n_unparsed`
    counts the cells no clock reading accepted. Neither carries a
    value; both carry a shape and a count of the table.
14. **The calendar-placeholder verdicts and their counts. NEW.** A
    judged placeholder publishes a `sentinel_verdicts` entry whose
    `candidate` is the placeholder's own canonical ISO day spelling,
    with its occurrence count, verdict and reason — the treatment the
    three stand-in numbers already have, now reaching dates. On a
    nothing-publishing column it withholds exactly as the numeric
    candidates do.
15. **The BLOCK-CLASS source accounting, reaching columns that
    published none. NEW.** `free_text` is a NOTHING-class role;
    `datetime`, `time_of_day` and `affixed_number` are RANGES-class and
    `long_tail_labels` is LABELS-class. On the nothing class
    `missing_by_source` is empty, both absence counts are zero, and
    every sentinel candidate reads `(withheld)`; on the other classes
    none of that holds. So every column crossing out of free text into
    one of those FOUR roles — by the five calendar members named at row
    5, the unpadded reading, the clock rule, the affix rule or the
    long-tail rule — newly publishes four kinds of fact about its
    ABSENT cells:
    - the EXACT absent-value SPELLINGS its cells wore, every key of
      `missing_by_source` being text of the table with no first-party
      meaning, floor-governed;
    - each spelling's ROW COUNT, at or above `small_cell_floor`;
    - `n_missing_blank` and `n_missing_withheld`, two counts that read
      zero on every nothing-publishing column — the first floor-
      governed, the second the pooled residue that carries the blank
      cells below the floor;
    - the NAME of each sentinel candidate — the stand-in number as
      text, or a calendar placeholder's ISO day spelling — where such a
      column published only `(withheld)`.
    And `missing_by_source` is EXACT-OBSERVABLE, so under C6-115 the
    twin WRITES those spellings at their published counts — **with
    C6-115's own named exception**: a spelling a JUDGED PASS put there,
    one reading as a stand-in number or as a calendar placeholder,
    stays blank in the twin (C6-116), and section 9's row carries the
    same exception in its own words. This is the class of fact row 12's
    second bullet prices for the error-literal mechanism; it is priced
    here for the five mechanisms row 12 does not reach. Row 1 prices a
    long-tail column's floor-cleared LEVEL spellings and not this,
    which is why `long_tail_labels` is named here as well.
16. **The slashed-reading parse counts, carried in a sentence. NEW.**
    Where the `day_first` option was given and a slashed reading was in
    play, the column carries the
    `remark_slashed_dates_read_against_your_declaration` form, whose
    arity is five: cells the day-first reading parsed (*D*), cells the
    month-first reading parsed (*M*), cells only day-first parsed
    (*X*), cells only month-first parsed (*Y*), and the reading used.
    Four of the five are COUNTS OF THE TABLE. The total for the reading
    USED is already a block fact — `n_present` less `n_unparsed`. The
    other THREE are carried by no key of any block; two are independent
    and the third follows from the both-readings identity *D* − *X* =
    *M* − *Y*. The sentence is where they are published. Each is
    bounded by the named column's `n_present`, and no value of the
    table enters. **Open, and stated rather than assumed:** nothing in
    section 4.5 says whether a column read both ways that then DECLINES
    to `datetime` still carries the form. If it can, these counts reach
    a column with no `n_unparsed` key at all and all four are carried
    by no key.
17. **The `(date-sentinel)` absence-class count. NEW.**
    `missing_by_class` carries six keys, always all six, on every block
    of every role. `(date-sentinel)` counts the cells a calendar
    placeholder pass read as absent: a count of the table,
    floor-governed like every other non-`(withheld)` class,
    REPORT-ONLY. It is nonzero only where the placeholder pass entered,
    which C6-34 confines to a column whose non-candidate remainder
    clears the datetime rule's parse line. Row 14 prices the
    placeholder VERDICTS; this row prices the CLASS COUNT beside them,
    which is a different key.
18. **The declined column's evidence counts, carried in a sentence.
    NEW in four positions.** `remark_no_reading_fits` has arity 9 and
    is carried by a `free_text` column, which publishes no value of the
    table — yet four of its arguments are counts of that table, written
    into the sentence when nonzero, and carried by no key of a
    `free_text` block:
    - argument 6, present cells the affix reading accepted;
    - argument 7, cells stand-in judging removed where the removal
      moved the column across a line — the same population
      `missing_by_class`'s `(numeric-sentinel)` entry counts, but that
      entry is floor-governed and this argument is written exactly, so
      a below-floor group's SIZE can be named here where the map pooled
      it. It is a size of an unnamed group, never a spelling, which is
      the treatment `n_distinct_by_occurrences` and
      `suppressed_level_counts` already have;
    - argument 8, present cells a clock reading accepted under the form
      that came closest;
    - argument 9, present cells covered by the column's floor-clearing
      non-numeric folded spellings — **floor-governed**, because the
      argument-consistency check section 4.5.2 states for that argument
      holds it at or above `small_cell_floor` whenever it is written.
    Arguments 6, 7 and 8 are bound by no floor rule this contract
    states. The other two sentence forms this version adds publish
    nothing new: the affixed remark's three arguments are the block's
    own `affix_prefix`, `affix_suffix` and `n_affixed`, tied to them
    character for character; and the built-in-stand-in remark writes a
    position in a three-member first-party list, never a spelling, for
    a label the block publishes beside it.

### 12.4 The files, and the handling rule

Every file a full run leaves behind — the description, the
plain-language summary beside it, the twin, the twin's report and the
quality report — carries real-derived published facts, and each is
handled under the institution's rules for real-derived material.
synthtwin claims no formal privacy guarantee. Two of the five are
counted because a narrower reading once left them out, and each is
named with the reason it belongs: the quality report `synthtwin
validate` writes states measurements taken from the file it checked;
and the summary is a file of its own because that is how a person meets
these facts — it is printed on the screen, written beside the
description, and repeats in words the labels and endpoints section 6
publishes. Nothing this contract publishes moves with that reading; the
handling rule reaches further, and that direction is the only one it
may move in.

### 12.5 What the assertion means

Each row above is named in `SECURITY.md` and in the profiler's own
summary, where a person meets it. Every fact this document introduces
is either in a row above or publishes nothing of the table. Two rows
exist because a reader took an earlier, narrower statement as the whole
of a mechanism — row 11 beside row 1, and row 12's second bullet beside
its first — and a completeness claim that stops short of the facts it
must cover is the failure this section is written to prevent.

---

## 13. Decisions this contract took, and why

The plan fixed every mechanism; in the places below it named a fact
without fixing its exact shape, and this contract fixed the shape. Each
is listed so a reviewer can accept or reject it here, at the cheapest
place, rather than discover it in code.

**13.1 `numeric_styles` appears on `count`, `continuous` and
`affixed_number` only.** Owner decision 10 says "each numeric column";
several roles could be read as numeric. The key is restricted to the
three whose twin cells are written as parsed numbers from the ladder in
decision 8's spelling family, because those are the roles where the
reader's inferred type is at stake and where the generator can
discharge the obligation. A `numeric_unrepresentable` twin writes
invented digit strings at one canonical invented width, so a style map
there would describe a form the twin cannot reproduce. A reviewer
preferring the wider reading is asking for an additive change: the key
would become required on `numeric_unrepresentable` too, and P1's
population would have to be restated for a role with no representable
numbers.

**13.2 The style classification ladder, and its priority order**
(7.5.4). Decision 10 enumerated six style NAMES; a total, order-fixed
rule assigning exactly one to every counted cell is what makes producer
and generator agree. Type-bearing forms are tested first because they
are the forms that decide what an ordinary reader infers, which is the
fidelity decision 10 exists to protect.

**13.3 Accounting parentheses and thousands separators are classified
by their digit form, not given styles of their own.** The enumeration
is closed at six and both forms are excluded from twin output by
decision 8 — a comma breaks the CSV row itself.

**13.4 `numeric_styles` counts the `n_numeric` cells only** (P1), read
over `n_core_numeric` on `affixed_number`. Out-of-range and
contradictory cells are written by the class-preserving construction of
plan P2-D9, whose forms — an overflowing digit string, a sign inside
brackets — are not expressible in the six styles, so counting them here
would make the map impossible to discharge.

**13.5 `variants` keys and `missing_by_source` keys are both stored
EXACTLY, not display-escaped** (7.4.2, 5.4). Both maps are
EXACT-OBSERVABLE and both have their keys written back into twin cells,
and a key something has to read back is a key that must survive being
written down. The display boundary applies at the moment of SHOWING and
never to what is stored: every surface that puts such a key in front of
a person — the plain-language summary, the generation report, the
quality report, any command output — escapes it there and never stores
the result, and a surface that interpolates a stored key without the
boundary is a defect in the implementation, not in this contract.

**13.6 `variants` and `variants_withheld` are REQUIRED on every
published level entry**, even when empty, rather than appearing only
where a label has more than one spelling. This contract has no optional
keys: a key that appears only sometimes is a key a consumer comes to
guess about.

**13.7 `variants_withheld` uses the multiplicity-map key form** (5.3) —
base-ten keys left-padded to a common width. Owner decision 11 calls it
"the same class of fact as the identifier repetition multiset", and
using the same wire shape means one reader, one writer and one set of
invariants for both.

**13.8 The axis derivation table** (5.2). Plan P2-D3 fixed the three
enumerations and said the rule is "derived by a fixed rule the contract
states". The table is that rule. **It is a bijection between the
THIRTEEN roles and the THIRTEEN `statistical_type` values** — no two
roles answer the same type and every type is reached by exactly one
role — with `quality_state` carrying the two degenerate states and
`structural_role` carrying the declaration.

**13.9 Invariant A4 is a loader refusal.** An axis triple outside the
table is refused rather than repaired, because the generator dispatches
on the axes and a document whose axes and role disagree would route a
column somewhere its own `role` says it does not belong.

**13.10 Thirteen roles.** Earlier plan and task text said "the nine
roles" while listing ten, and the count is now thirteen. The reason it
is thirteen is not that a shipped tuple has thirteen entries — no
version 6 producer exists yet, and the shipped tuple still has ten. It
is that the ratified Phase 4 plan's delta adds exactly three roles —
`time_of_day`, `affixed_number`, `long_tail_labels` — to the ten this
format already had, and this contract is written before the code so
that the code is written against it. Where a count here and a count in
the tree disagree, the plan governs and the code is repaired.

**13.11 Two parser bounds, not four** (1.4).

**13.12 The loader checks the version before the canonical round-trip**
(10.1), with the consequence of that ordering stated in the same place
rather than left to be discovered.

**13.13 `null` is accepted on `mean`, on every `percentiles` rung, and
on `length.mean`, `length.p50` and `words.mean`** (L3, Q7, 6.9). Each
is null only where the exact statistic is not a finite binary64 value.
No producible description is known to reach any of them; the contract
accepts null rather than refusing a document over a case it cannot rule
out, and a generator treats a null as an approximated field with no
target and says so in the report.

**13.14 The last second of a leap minute is carried, not excused**
(9.6, review item P2-C2-F5). This entry records a bar that was lowered
and put back, because a reader who sees only the current text cannot
tell a decision from a drift. A repair widened the `SS` field to `60`
in the canonical form — correctly, since the shipped reader accepts one
and the producer can publish one — and then, rather than write that
instant back, made the endpoint REPORT-ONLY, trading a ratified exact
fact for a sentence in the report. No owner decision authorized it, and
an exact representation was available the whole time: the endpoint
cells are written from the published endpoint's own fields, so the
seconds field survives. A test asserts this wording so the bar cannot
be lowered again in silence.

**13.15 The same bar, lowered a second time in a second place, and the
refusal that ends it** (D10, D11, 9.6, item P2-C3-F2). The repair in
13.14 restored the disposition where the last reviewer had looked and
then wrote the exception back in the paragraph after it: a description
publishing an endpoint no cell of its own recorded shape can show would
have that endpoint met as far as it could be, recounted, and named in
the report. The strict loader accepted such a description, so the
matrix said "no corner, no exception" about documents this contract let
through with the end changed. **A sentence restored in one place and
weakened in another is the same lowering, and it is harder to see.**
What was put back: the exception paragraph is gone; both ends are
written from the published end's own fields on both clocks with no case
that declines; the two pairs that made the exception arguable are
refused by D10, with D11 tying the ladder ends to the endpoints so one
refusal covers all four texts. D11 also closed a hole nothing had named
— with the pair untied, a hand-made ladder end below `earliest` gave a
twin holding instants earlier than its own published endpoint, and no
report said so. The ends are exact on every description the loader
accepts, which is what a consumer reading the matrix may rely on.

**13.16 The same bar a third and fourth time, and the registry that
ends the pattern** (D10, 9.6, item P2-C4-F1). The repair in 13.15
refused the two pairs it named and left a third standing in the method:
an endpoint on the shared clock whose own offset carries its cell
outside the years `0001` to `9999`, which the method called the
calendar's own end and had the run name in the report. Its wording
guard listed that passage as a decided one, so the guard was green
about the very sentence it existed to catch. D10 now refuses the
calendar pair in both directions and the guard requires ZERO
endpoint-loss passages rather than listing one. What matters more than
the sentence: a repository-wide registry holds every published fact
against the disposition the ratified plan gives it, and a test reads
THIS document, the method and the plan and fails when any of the three
states a weaker outcome for a fact than the registry does, omits a fact
the registry names, or names a fact it does not. **The registry may
authorize a lesser outcome only where the plan's own words name it**,
so lowering a bar means amending the ratified plan in the open — which
is the process this repository already required and the thing four
repairs did not do.

**13.17 `missing_by_source` keeps its name.** Its key space and its
storage rule both changed, and a rename would have made every passage
of every other document ambiguous about which field it meant. The
version number is what tells the two apart, which is what a version
number is for.

**13.18 The pooled absent-cell remainder is an integer, not a
multiplicity map.** The shape `variants_withheld` uses would publish
group sizes the floor held back and would buy a consumer nothing.

**13.19 The blank count is floor-governed.** A blank count exempt from
the floor would be a wider publication, on every column, that nobody
asked for.

**13.20 The vocabulary lists in a declaration record are three arrays,
not one mixed array.** A single array holding strings, numbers and day
spellings has to be type-tested at every read, and the three are
matched by three different rules — folded spelling, exact number,
placeholder day — which is the same reason `declaration_matching` has
the value it has.

**13.21 The vocabulary member is written, never the person's
spelling.** Writing what they typed would put their spacing and their
capitals in the document for no gain: matching is over the folded form,
the number and the placeholder day, so the member carries everything a
consumer needs.

**13.22 The lists are written whether or not the word occurs.**
Recording only the words that actually matched a cell would make the
field evidence about the table, which is exactly what the settings
block exists not to be, and would be wrong for the consumer, which
needs the RULE the run applied and not its outcome.

**13.23 The published vocabulary is normative.** The cost is that the
built-in lists cannot be extended without a contract change; the
alternative is that two installations disagree about whether a key is
synthtwin's word or the person's.

**13.24 `values_recorded` keeps its name and its value.** Renaming it
would cost the discriminator its job against the much older format that
carried an array of spellings under the same key. Its meaning is fixed
in words instead, because a boolean beside three lists is a place a
reader can draw the wrong conclusion.

**13.25 Two producer obligations are stated as invariants although a
loader cannot check them** (N7, that a `missing_by_source` key is the
source spelling character for character; and K5, that the declaration
lists are a function of the command line alone). Leaving them out would
leave the properties the whole mechanism rests on unwritten; marking
them is what tells an implementer to prove them on the producer's side
instead of looking for a loader rule that cannot exist.

**13.26 The routes a description's absent-cell rules leave open are in
the normative text** — stated where the absent-cell rules themselves
are stated (5.4 and section 7), not in a residual list. A limit a
reader has to find somewhere else is a limit a reader does not find.

**13.27 The three new roles are tested after `categorical`** rather
than at the position their specificity might suggest, so that no column
any earlier rule claims changes what it is. Fidelity for unclaimed
columns is worth less than stability for claimed ones.

**13.28 `affixed_number` is a ranges-class role with a named two-key
exception rather than a fourth publication class.** A fourth class
would have to be given a meaning everywhere the three are enforced; an
exception is confined by the forbidden-key matrix.

**13.29 `resolution_mix` is REPORT-ONLY.** Reproducing a form mix would
need a per-form construction with its own packing, feasibility rule and
window family, for one reading — cost out of proportion to a fact the
reader still receives. The twin writes the finest recorded form and the
report says the mix was recorded and not kept, on the precedent of the
`format` fact itself.

**13.30 `long_tail_minimum_level` has one permitted value rather than a
range.** The line it records is a privacy boundary; a settings key that
could move it downward would let a settings combination widen which
columns publish labels, which is exactly what the `max` in the detection rule of 6.14 exists
to prevent.

**13.31 `NaT` joins as an exact-spelling member rather than being
excluded.** Excluding it left a common absent-time literal reading as
data; admitting it under the folded rule would read a person's name as
absent. The third option — one stated exception to the matching rule —
costs a reader one more sentence and loses nothing.

**13.32 Stand-in-sourced absent cells are not reproduced.** Their
absence reading is not deterministic from the description alone, and a
reproduction whose correctness depends on a re-judgement is worse than
a blank cell with a sentence naming what was not carried.

**13.33 `fraction_widths` is a sibling of `numeric_styles`, not a key
inside it.** Inside is where it reads as belonging and inside is
impossible: P1 requires every value of `numeric_styles` to be an
integer and requires them to sum to the numeric count, so an object
placed among them breaks both. The ratified plan said inside; the plan
governs, so the plan was amended rather than this document deviating
from it.

**13.34 This contract states every rule in force, itself** (1.6). An
earlier version of this format carried its predecessor by reference,
and that predecessor carried one before it. Six adversarial review
rounds failed to converge on that design: each rule stood in two to
four places, and every round found a site amended in one place and left
live in another. The cost of stating everything once is a longer
document; the buy is that no rule has two homes and no reader has to
work out which home is current. Owner decision 2026-08-20, plan
amendment A-P4-11. What did not change with it: an older document is
never edited to change what it requires, and a description is governed
by exactly one version's documents.

**13.35 Inherited invariants keep their exact identifiers.** `D1` binds
eleven formats rather than six and is still `D1`. This is not a style
preference: the sealed generation method, the validation method and the
test suite cite these by name, and a document that renames them
silently breaks every citation pointing at it. New checkable rules join
the family that owns their subject; everything else takes a plain
numbered identifier.

**13.36 The appendix is a reading aid and the defining section
governs.** An earlier version of this format printed six enumerations a
second time in its appendix, and nobody noticed it was a second site —
which is how an enumeration came to be amended in one place and left
standing in the other. Section 14 is written out in full because a
reader needs one page to check a spelling against, and it is
subordinate by rule so that it can never be the site a change misses.
The published vocabulary is the one list section 14 DEFINES rather than
repeats, and section 14 says so at the list itself, because a list with
two homes is precisely what this entry refuses.

**13.37 Where this contract and the shipped code disagree, the code is
repaired** (1.5). This document is written before the code that
implements it, so a difference between a list here and a constant in
the tree is the ordinary state of the work and not evidence about the
rule. The authority order is the ratified plan, then this contract,
then the code. The one thing a reader may NOT do is take whichever
version is convenient: a transcription of invariant U1 found the
shipped profiler leaving ordinary-text cells out of the whole-number
and sign families while `n_present` counted them, so the producer wrote
descriptions its own loader refused, with a message blaming the reader
for tampering. The contract was right, the code was wrong, and the code
was repaired.

---

---

<!-- a14app: appendix: every enumeration in one place -->

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
